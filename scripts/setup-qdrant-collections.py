#!/usr/bin/env python3
"""
setup-qdrant-collections.py - Initialize Qdrant collections for architecture knowledge base

This script creates the required Qdrant collections for the AI architecture pipeline:
- capability-maps: Organization capability models
- reference-architectures: Standard patterns, templates
- guardrails-principles: Org constraints, policies
- existing-landscape: Current APIs, schemas, components
- compliance-requirements: HIPAA, GDPR, SOC2 docs

Usage:
    python setup-qdrant-collections.py
    python setup-qdrant-collections.py --qdrant-url http://localhost:6333
    python setup-qdrant-collections.py --recreate  # Drops and recreates collections

Environment Variables:
    QDRANT_URL: Qdrant server URL (default: http://qdrant:6333)
    EMBEDDING_SIZE: Embedding vector size (default: 768 for nomic-embed-text)
"""

import argparse
import os
import sys
from typing import Dict, List, Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        FieldCondition,
        Range,
        MatchValue,
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Warning: qdrant-client not installed. Install with: pip install qdrant-client", file=sys.stderr)


# Collection definitions for architecture knowledge base
COLLECTIONS = {
    "capability-maps": {
        "description": "Organization capability models (L1-L4 hierarchies)",
        "metadata_fields": ["industry", "domain", "level", "source"],
    },
    "reference-architectures": {
        "description": "Standard architecture patterns and templates",
        "metadata_fields": ["pattern_type", "domain", "technology", "source"],
    },
    "guardrails-principles": {
        "description": "Organizational constraints, policies, and architecture principles",
        "metadata_fields": ["category", "priority", "source", "mandatory"],
    },
    "existing-landscape": {
        "description": "Current APIs, schemas, components in the enterprise",
        "metadata_fields": ["component_type", "domain", "status", "version"],
    },
    "compliance-requirements": {
        "description": "Regulatory and compliance documentation (HIPAA, GDPR, SOC2, etc.)",
        "metadata_fields": ["regulation", "domain", "requirement_type", "criticality"],
    },
}


def create_collection(
    client: "QdrantClient",
    collection_name: str,
    vector_size: int = 768,
    distance: str = "Cosine",
    recreate: bool = False,
) -> bool:
    """Create a Qdrant collection with the specified parameters."""

    # Check if collection exists
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)

    if exists:
        if recreate:
            print(f"  Dropping existing collection: {collection_name}")
            client.delete_collection(collection_name)
        else:
            print(f"  Collection already exists: {collection_name} (skipping)")
            return False

    # Create the collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE if distance == "Cosine" else Distance.EUCLID,
        ),
    )

    print(f"  Created collection: {collection_name} (vector_size={vector_size})")
    return True


def setup_all_collections(
    qdrant_url: str,
    vector_size: int = 768,
    recreate: bool = False,
) -> Dict[str, bool]:
    """Set up all required Qdrant collections."""

    if not QDRANT_AVAILABLE:
        print("Error: qdrant-client is required. Install with: pip install qdrant-client")
        return {}

    print(f"Connecting to Qdrant at: {qdrant_url}")
    client = QdrantClient(url=qdrant_url)

    # Test connection
    try:
        client.get_collections()
        print("  Connected successfully")
    except Exception as e:
        print(f"Error: Failed to connect to Qdrant: {e}")
        return {}

    results = {}

    print("\nCreating collections:")
    for collection_name, config in COLLECTIONS.items():
        print(f"\n{collection_name}:")
        print(f"  Description: {config['description']}")

        created = create_collection(
            client=client,
            collection_name=collection_name,
            vector_size=vector_size,
            recreate=recreate,
        )

        results[collection_name] = created

    return results


def list_collections(qdrant_url: str) -> List[str]:
    """List all existing Qdrant collections."""

    if not QDRANT_AVAILABLE:
        print("Error: qdrant-client is required.")
        return []

    client = QdrantClient(url=qdrant_url)
    collections = client.get_collections().collections

    return [c.name for c in collections]


def get_collection_info(qdrant_url: str, collection_name: str) -> Optional[Dict]:
    """Get information about a specific collection."""

    if not QDRANT_AVAILABLE:
        return None

    client = QdrantClient(url=qdrant_url)

    try:
        info = client.get_collection(collection_name)
        return {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
            "vector_size": info.config.params.vectors.size,
        }
    except Exception as e:
        print(f"Error getting collection info: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Set up Qdrant collections for architecture knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--qdrant-url",
        default=os.environ.get("QDRANT_URL", "http://qdrant:6333"),
        help="Qdrant server URL (default: http://qdrant:6333 or QDRANT_URL env var)"
    )
    parser.add_argument(
        "--vector-size",
        type=int,
        default=int(os.environ.get("EMBEDDING_SIZE", "768")),
        help="Embedding vector size (default: 768 for nomic-embed-text)"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Drop and recreate existing collections"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing collections and exit"
    )

    args = parser.parse_args()

    if args.list:
        print(f"Connecting to Qdrant at: {args.qdrant_url}")
        collections = list_collections(args.qdrant_url)

        if collections:
            print("\nExisting collections:")
            for name in collections:
                info = get_collection_info(args.qdrant_url, name)
                if info:
                    print(f"  - {name}: {info['points_count']} points, vector_size={info['vector_size']}")
                else:
                    print(f"  - {name}")
        else:
            print("\nNo collections found.")

        return 0

    print("=" * 60)
    print("Qdrant Knowledge Base Setup")
    print("=" * 60)

    results = setup_all_collections(
        qdrant_url=args.qdrant_url,
        vector_size=args.vector_size,
        recreate=args.recreate,
    )

    if not results:
        print("\nSetup failed!")
        return 1

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    created = sum(1 for v in results.values() if v)
    skipped = len(results) - created

    print(f"  Created: {created}")
    print(f"  Skipped: {skipped}")
    print(f"  Total:   {len(results)}")

    if created > 0:
        print("\nNext steps:")
        print("  1. Run embed-documents.py to add documents to collections")
        print("  2. Configure n8n workflows to use Qdrant for RAG")

    return 0


if __name__ == "__main__":
    sys.exit(main())
