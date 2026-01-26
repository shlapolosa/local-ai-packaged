#!/usr/bin/env python3
"""
Seed Qdrant collection with knowledge documents for the Business Analysis Pipeline.
This script creates the collection and uploads documents with embeddings.
"""

import json
import requests
import sys
import hashlib
from pathlib import Path

# Configuration
QDRANT_URL = "http://qdrant:6333"  # Internal Docker network
OLLAMA_URL = "https://ollama.socrates-hlapolosa.org/api/embeddings"
COLLECTION_NAME = "agent-knowledge-business-analyst"
EMBEDDING_MODEL = "nomic-embed-text"
VECTOR_SIZE = 768  # nomic-embed-text dimension

def get_embedding(text: str) -> list:
    """Generate embedding using Ollama."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=60
    )
    response.raise_for_status()
    return response.json()["embedding"]

def create_collection():
    """Create Qdrant collection if it doesn't exist."""
    # Check if collection exists
    response = requests.get(f"{QDRANT_URL}/collections/{COLLECTION_NAME}")
    if response.status_code == 200:
        print(f"Collection '{COLLECTION_NAME}' already exists")
        return True

    # Create collection
    response = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION_NAME}",
        json={
            "vectors": {
                "size": VECTOR_SIZE,
                "distance": "Cosine"
            }
        }
    )
    if response.status_code in (200, 201):
        print(f"Created collection '{COLLECTION_NAME}'")
        return True
    else:
        print(f"Failed to create collection: {response.text}")
        return False

def generate_point_id(doc_id: str) -> int:
    """Generate a consistent numeric ID from string ID."""
    # Use hash to generate consistent numeric ID
    hash_bytes = hashlib.md5(doc_id.encode()).digest()
    return int.from_bytes(hash_bytes[:8], byteorder='big') % (2**63)

def upsert_documents(documents: list):
    """Upload documents to Qdrant with embeddings."""
    points = []

    for i, doc in enumerate(documents):
        doc_id = doc.get("id", f"doc-{i}")
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})

        print(f"Processing: {doc_id}...")

        # Generate embedding
        try:
            embedding = get_embedding(content)
        except Exception as e:
            print(f"  Error generating embedding: {e}")
            continue

        # Create point
        point = {
            "id": generate_point_id(doc_id),
            "vector": embedding,
            "payload": {
                "doc_id": doc_id,
                "content": content,
                "metadata": metadata
            }
        }
        points.append(point)
        print(f"  Embedding generated ({len(embedding)} dims)")

    if not points:
        print("No points to upsert")
        return False

    # Batch upsert
    response = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points",
        json={"points": points}
    )

    if response.status_code in (200, 201):
        print(f"\nSuccessfully upserted {len(points)} documents")
        return True
    else:
        print(f"Failed to upsert: {response.text}")
        return False

def main():
    # Load knowledge documents
    knowledge_file = Path(__file__).parent / "sahatna-knowledge-seed.json"

    if not knowledge_file.exists():
        print(f"Knowledge file not found: {knowledge_file}")
        sys.exit(1)

    with open(knowledge_file, "r") as f:
        documents = json.load(f)

    print(f"Loaded {len(documents)} documents from {knowledge_file.name}")
    print(f"Qdrant URL: {QDRANT_URL}")
    print(f"Collection: {COLLECTION_NAME}")
    print()

    # Create collection
    if not create_collection():
        sys.exit(1)

    # Upsert documents
    if not upsert_documents(documents):
        sys.exit(1)

    print("\nSeeding complete!")

if __name__ == "__main__":
    main()
