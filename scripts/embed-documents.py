#!/usr/bin/env python3
"""
embed-documents.py - Embed documents into Qdrant collections for RAG

This script reads documents from specified directories and embeds them into
the appropriate Qdrant collections using Ollama embeddings.

Usage:
    python embed-documents.py --collection capability-maps --source ./docs/capabilities/
    python embed-documents.py --collection reference-architectures --source ./docs/patterns/
    python embed-documents.py --all --source-dir ./docs/knowledge/

Environment Variables:
    QDRANT_URL: Qdrant server URL (default: http://qdrant:6333)
    OLLAMA_URL: Ollama server URL (default: http://ollama:11434)
    EMBEDDING_MODEL: Model for embeddings (default: nomic-embed-text)

Directory Structure Expected for --all:
    ./docs/knowledge/
    ├── capability-maps/
    ├── reference-architectures/
    ├── guardrails-principles/
    ├── existing-landscape/
    └── compliance-requirements/
"""

import argparse
import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Generator
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


# Supported file extensions
SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}


def get_embedding(
    text: str,
    ollama_url: str = "http://ollama:11434",
    model: str = "nomic-embed-text",
) -> Optional[List[float]]:
    """Get embedding vector from Ollama."""

    if not REQUESTS_AVAILABLE:
        print("Error: requests library is required.")
        return None

    try:
        response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> Generator[str, None, None]:
    """Split text into overlapping chunks."""

    if len(text) <= chunk_size:
        yield text
        return

    start = 0
    while start < len(text):
        end = start + chunk_size

        # Try to break at a sentence or paragraph boundary
        if end < len(text):
            # Look for paragraph break
            para_break = text.rfind("\n\n", start, end)
            if para_break > start + chunk_size // 2:
                end = para_break + 2
            else:
                # Look for sentence break
                sentence_break = text.rfind(". ", start, end)
                if sentence_break > start + chunk_size // 2:
                    end = sentence_break + 2

        yield text[start:end].strip()
        start = end - overlap


def read_document(file_path: Path) -> Optional[Dict]:
    """Read a document and extract content and metadata."""

    if not file_path.exists():
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract metadata from filename and path
        metadata = {
            "filename": file_path.name,
            "filepath": str(file_path),
            "extension": file_path.suffix,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        }

        # Try to extract YAML frontmatter for markdown files
        if file_path.suffix == ".md" and content.startswith("---"):
            try:
                import yaml
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if isinstance(frontmatter, dict):
                        metadata.update(frontmatter)
                    content = parts[2].strip()
            except Exception:
                pass

        return {
            "content": content,
            "metadata": metadata,
        }

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def generate_point_id(text: str, metadata: Dict) -> str:
    """Generate a deterministic point ID from content."""
    hash_input = f"{text}{json.dumps(metadata, sort_keys=True)}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def embed_documents(
    collection_name: str,
    source_dir: Path,
    qdrant_url: str = "http://qdrant:6333",
    ollama_url: str = "http://ollama:11434",
    embedding_model: str = "nomic-embed-text",
    chunk_size: int = 500,
    batch_size: int = 10,
) -> Dict[str, int]:
    """Embed documents from a directory into a Qdrant collection."""

    if not QDRANT_AVAILABLE:
        print("Error: qdrant-client is required.")
        return {"error": "qdrant-client not available"}

    if not REQUESTS_AVAILABLE:
        print("Error: requests library is required.")
        return {"error": "requests not available"}

    client = QdrantClient(url=qdrant_url)

    # Verify collection exists
    try:
        client.get_collection(collection_name)
    except Exception:
        print(f"Error: Collection '{collection_name}' does not exist.")
        print("Run setup-qdrant-collections.py first.")
        return {"error": "collection not found"}

    stats = {
        "files_processed": 0,
        "chunks_created": 0,
        "points_added": 0,
        "errors": 0,
    }

    # Find all supported files
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(source_dir.glob(f"**/*{ext}"))

    print(f"Found {len(files)} files to process")

    points_batch = []

    for file_path in files:
        print(f"\nProcessing: {file_path.name}")

        doc = read_document(file_path)
        if not doc:
            stats["errors"] += 1
            continue

        stats["files_processed"] += 1

        # Chunk the content
        chunks = list(chunk_text(doc["content"], chunk_size=chunk_size))
        print(f"  Created {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            # Get embedding
            embedding = get_embedding(chunk, ollama_url, embedding_model)
            if not embedding:
                stats["errors"] += 1
                continue

            # Create point
            chunk_metadata = doc["metadata"].copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)

            point = PointStruct(
                id=generate_point_id(chunk, chunk_metadata),
                vector=embedding,
                payload={
                    "text": chunk,
                    "metadata": chunk_metadata,
                }
            )

            points_batch.append(point)
            stats["chunks_created"] += 1

            # Upsert in batches
            if len(points_batch) >= batch_size:
                try:
                    client.upsert(collection_name, points_batch)
                    stats["points_added"] += len(points_batch)
                    print(f"  Uploaded {len(points_batch)} points")
                except Exception as e:
                    print(f"  Error uploading batch: {e}")
                    stats["errors"] += 1
                points_batch = []

    # Upload remaining points
    if points_batch:
        try:
            client.upsert(collection_name, points_batch)
            stats["points_added"] += len(points_batch)
            print(f"  Uploaded {len(points_batch)} points")
        except Exception as e:
            print(f"  Error uploading final batch: {e}")
            stats["errors"] += 1

    return stats


def embed_all_collections(
    source_dir: Path,
    qdrant_url: str = "http://qdrant:6333",
    ollama_url: str = "http://ollama:11434",
    embedding_model: str = "nomic-embed-text",
) -> Dict[str, Dict]:
    """Embed documents for all collections from a structured directory."""

    results = {}

    # Expected subdirectories matching collection names
    collections = [
        "capability-maps",
        "reference-architectures",
        "guardrails-principles",
        "existing-landscape",
        "compliance-requirements",
    ]

    for collection in collections:
        collection_dir = source_dir / collection

        if not collection_dir.exists():
            print(f"\nSkipping {collection}: directory not found at {collection_dir}")
            results[collection] = {"skipped": True}
            continue

        print(f"\n{'=' * 60}")
        print(f"Processing collection: {collection}")
        print(f"Source: {collection_dir}")
        print("=" * 60)

        stats = embed_documents(
            collection_name=collection,
            source_dir=collection_dir,
            qdrant_url=qdrant_url,
            ollama_url=ollama_url,
            embedding_model=embedding_model,
        )

        results[collection] = stats

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Embed documents into Qdrant collections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--collection",
        help="Target collection name (use with --source)"
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Source directory containing documents"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all collections from structured directory"
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("./docs/knowledge"),
        help="Base directory for --all mode (default: ./docs/knowledge)"
    )
    parser.add_argument(
        "--qdrant-url",
        default=os.environ.get("QDRANT_URL", "http://qdrant:6333"),
        help="Qdrant server URL"
    )
    parser.add_argument(
        "--ollama-url",
        default=os.environ.get("OLLAMA_URL", "http://ollama:11434"),
        help="Ollama server URL"
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("EMBEDDING_MODEL", "nomic-embed-text"),
        help="Embedding model name"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Text chunk size (default: 500)"
    )

    args = parser.parse_args()

    if not args.all and not (args.collection and args.source):
        parser.error("Either --all or both --collection and --source are required")

    print("=" * 60)
    print("Document Embedding for Qdrant")
    print("=" * 60)
    print(f"Qdrant URL: {args.qdrant_url}")
    print(f"Ollama URL: {args.ollama_url}")
    print(f"Model: {args.model}")

    if args.all:
        results = embed_all_collections(
            source_dir=args.source_dir,
            qdrant_url=args.qdrant_url,
            ollama_url=args.ollama_url,
            embedding_model=args.model,
        )
    else:
        if not args.source.exists():
            print(f"Error: Source directory not found: {args.source}")
            return 1

        results = {
            args.collection: embed_documents(
                collection_name=args.collection,
                source_dir=args.source,
                qdrant_url=args.qdrant_url,
                ollama_url=args.ollama_url,
                embedding_model=args.model,
                chunk_size=args.chunk_size,
            )
        }

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    for collection, stats in results.items():
        print(f"\n{collection}:")
        if isinstance(stats, dict):
            for key, value in stats.items():
                print(f"  {key}: {value}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
