#!/usr/bin/env python3
"""
Convert sahatna-knowledge-seed.json to individual markdown files
with YAML frontmatter for the Knowledge Agent upload system.
"""

import json
import os
import yaml

# Source file and output directory
SEED_FILE = "/Users/socrateshlapolosa/Development/local-ai-packaged/shared/knowledge/sahatna-knowledge-seed.json"
OUTPUT_DIR = "/Users/socrateshlapolosa/Development/local-ai-packaged/shared/knowledge/agent-docs/business-analyst"

def convert_to_markdown():
    # Load the seed file
    with open(SEED_FILE, 'r') as f:
        documents = json.load(f)

    print(f"Found {len(documents)} documents to convert")

    for doc in documents:
        doc_id = doc.get('id')
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})

        # Build frontmatter
        frontmatter = {
            'doc_id': doc_id,
        }

        # Add scope if present
        if 'scope' in metadata:
            frontmatter['scope'] = metadata['scope']

        # Add other relevant metadata
        if 'documentType' in metadata:
            frontmatter['documentType'] = metadata['documentType']
        if 'project' in metadata:
            frontmatter['project'] = metadata['project']
        if 'service' in metadata:
            frontmatter['service'] = metadata['service']
        if 'integration' in metadata:
            frontmatter['integration'] = metadata['integration']

        # Generate filename from doc_id
        filename = f"{doc_id}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Create markdown content with YAML frontmatter
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)

        markdown_content = f"""---
{yaml_str.rstrip()}
---

{content}
"""

        # Write the file
        with open(filepath, 'w') as f:
            f.write(markdown_content)

        print(f"Created: {filename}")

    print(f"\nCompleted! {len(documents)} files created in {OUTPUT_DIR}")

if __name__ == '__main__':
    convert_to_markdown()
