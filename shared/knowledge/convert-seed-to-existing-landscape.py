#!/usr/bin/env python3
"""
Convert sahatna-knowledge-seed.json to:
1. Individual markdown files with YAML frontmatter (for manual review)
2. A consolidated JSON file for the Knowledge Loader n8n workflow

Each document becomes a markdown file with component metadata for
sequence diagram enrichment, plus a JSON file for Qdrant seeding.
"""

import json
import re
import yaml
from pathlib import Path

# Source file and output directory
SCRIPT_DIR = Path(__file__).parent
SEED_FILE = SCRIPT_DIR / "sahatna-knowledge-seed.json"
OUTPUT_DIR = SCRIPT_DIR / "existing-landscape"
JSON_OUTPUT = OUTPUT_DIR / "existing_landscape.json"


def extract_port_from_content(content: str) -> int | None:
    """Extract service port from content."""
    match = re.search(r'\*\*Port\*\*:\s*(\d+)', content)
    if match:
        return int(match.group(1))
    return None


def extract_health_endpoint(content: str) -> str | None:
    """Extract health endpoint from content."""
    match = re.search(r'\*\*Health Endpoint\*\*:\s*([^\n]+)', content)
    if match:
        return match.group(1).strip()
    return None


def extract_database_schema(content: str) -> str | None:
    """Extract database schema name from content."""
    match = re.search(r'Database Schema:\s*(\w+)', content)
    if match:
        return match.group(1).strip()
    return None


def determine_component_type(doc: dict) -> str:
    """Determine the component type based on document metadata."""
    doc_type = doc.get("metadata", {}).get("documentType", "")

    type_map = {
        "external-integration": "external",
        "service-architecture": "api",
        "technology-stack": "infrastructure",
        "architecture-pattern": "pattern",
        "operations": "operations",
        "project-overview": "overview",
        "architectural-principles": "principles",
        "system-requirements": "requirements",
        "glossary": "reference",
    }

    return type_map.get(doc_type, "reference")


def is_internal_component(doc: dict) -> bool:
    """Determine if component is internal or external."""
    doc_type = doc.get("metadata", {}).get("documentType", "")
    return doc_type != "external-integration"


def convert_to_markdown():
    """Convert seed documents to markdown files and JSON for Knowledge Loader."""

    # Load the seed file
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    print(f"Found {len(documents)} documents to convert")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    created_count = 0
    json_documents = []  # For Knowledge Loader workflow

    for doc in documents:
        doc_id = doc.get('id')
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        scope = metadata.get('scope', {})

        # Determine component properties
        component_type = determine_component_type(doc)
        is_internal = is_internal_component(doc)

        # Build frontmatter with component metadata for Qdrant
        frontmatter = {
            'doc_id': doc_id,
            'component_name': metadata.get('service') or metadata.get('integration') or doc_id,
            'component_type': component_type,
            'is_internal': is_internal,
            'document_type': metadata.get('documentType', ''),
            'project': metadata.get('project', ''),
        }

        # Add service-specific fields
        if metadata.get('service'):
            frontmatter['service'] = metadata['service']
        if metadata.get('integration'):
            frontmatter['integration'] = metadata['integration']

        # Extract technical details from content
        port = extract_port_from_content(content)
        if port:
            frontmatter['port'] = port

        health_endpoint = extract_health_endpoint(content)
        if health_endpoint:
            frontmatter['health_endpoint'] = health_endpoint

        database_schema = extract_database_schema(content)
        if database_schema:
            frontmatter['database_schema'] = database_schema

        # Add scope information (capabilities, integrations)
        if scope.get('internalSystems'):
            frontmatter['internal_systems'] = scope['internalSystems']
        if scope.get('internalCapabilities'):
            frontmatter['capabilities'] = scope['internalCapabilities']
        if scope.get('supportedIntegrations'):
            frontmatter['integrations'] = scope['supportedIntegrations']

        # Generate filename from doc_id
        filename = f"{doc_id}.md"
        filepath = OUTPUT_DIR / filename

        # Create markdown content with YAML frontmatter
        yaml_str = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )

        markdown_content = f"""---
{yaml_str.rstrip()}
---

{content}
"""

        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"  Created: {filename} ({component_type})")
        created_count += 1

        # Build JSON document for Knowledge Loader workflow
        json_doc = {
            "text": content,
            "metadata": {
                "doc_id": doc_id,
                "component_name": frontmatter.get('component_name'),
                "component_type": component_type,
                "is_internal": is_internal,
                "document_type": frontmatter.get('document_type'),
                "project": frontmatter.get('project'),
                "source": f"existing-landscape/{filename}",
            }
        }
        # Add optional metadata
        if frontmatter.get('service'):
            json_doc['metadata']['service'] = frontmatter['service']
        if frontmatter.get('integration'):
            json_doc['metadata']['integration'] = frontmatter['integration']
        if frontmatter.get('port'):
            json_doc['metadata']['port'] = frontmatter['port']
        if frontmatter.get('health_endpoint'):
            json_doc['metadata']['health_endpoint'] = frontmatter['health_endpoint']
        if frontmatter.get('database_schema'):
            json_doc['metadata']['database_schema'] = frontmatter['database_schema']
        if frontmatter.get('capabilities'):
            json_doc['metadata']['capabilities'] = frontmatter['capabilities']
        if frontmatter.get('integrations'):
            json_doc['metadata']['integrations'] = frontmatter['integrations']

        json_documents.append(json_doc)

    # Write consolidated JSON for Knowledge Loader workflow
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(json_documents, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted!")
    print(f"  - {created_count} markdown files created in {OUTPUT_DIR}")
    print(f"  - JSON file created: {JSON_OUTPUT}")
    print("\nTo seed Qdrant, run one of:")
    print("  1. curl -X POST http://localhost:5678/webhook/knowledge-loader -H 'Content-Type: application/json' -d '{\"collection\": \"existing-landscape\"}'")
    print("  2. Or manually trigger 'Knowledge Loader - Generic' in n8n UI with collection='existing-landscape'")


if __name__ == '__main__':
    convert_to_markdown()
