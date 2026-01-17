#!/bin/bash
# setup-architecture-pipeline.sh - Initialize the architecture pipeline environment
#
# This script:
# 1. Creates necessary directories in the shared volume
# 2. Copies conversion scripts to shared/scripts for n8n access
# 3. Sets up knowledge base directories
# 4. Initializes Qdrant collections (optional)
#
# Usage:
#   ./scripts/setup-architecture-pipeline.sh
#   ./scripts/setup-architecture-pipeline.sh --init-qdrant

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Architecture Pipeline Setup"
echo "=========================================="
echo "Project Root: $PROJECT_ROOT"
echo ""

# Create shared volume directories
echo "Creating shared volume directories..."
mkdir -p "$PROJECT_ROOT/shared/scripts"
mkdir -p "$PROJECT_ROOT/shared/artifacts"
mkdir -p "$PROJECT_ROOT/shared/knowledge/capability-maps"
mkdir -p "$PROJECT_ROOT/shared/knowledge/reference-architectures"
mkdir -p "$PROJECT_ROOT/shared/knowledge/guardrails-principles"
mkdir -p "$PROJECT_ROOT/shared/knowledge/existing-landscape"
mkdir -p "$PROJECT_ROOT/shared/knowledge/compliance-requirements"
mkdir -p "$PROJECT_ROOT/projects"

echo "  Created: shared/scripts"
echo "  Created: shared/artifacts"
echo "  Created: shared/knowledge/* (5 collections)"
echo "  Created: projects"
echo ""

# Copy conversion scripts to shared volume
echo "Copying conversion scripts to shared volume..."

# Main conversion scripts
if [ -d "$PROJECT_ROOT/opencode/scripts" ]; then
    cp "$PROJECT_ROOT/opencode/scripts/json-to-archimate.py" "$PROJECT_ROOT/shared/scripts/" 2>/dev/null || echo "  Warning: json-to-archimate.py not found"
    cp "$PROJECT_ROOT/opencode/scripts/json-to-openapi.py" "$PROJECT_ROOT/shared/scripts/" 2>/dev/null || echo "  Warning: json-to-openapi.py not found"
    cp "$PROJECT_ROOT/opencode/scripts/json-to-sql.py" "$PROJECT_ROOT/shared/scripts/" 2>/dev/null || echo "  Warning: json-to-sql.py not found"
    cp "$PROJECT_ROOT/opencode/scripts/json-to-markdown.py" "$PROJECT_ROOT/shared/scripts/" 2>/dev/null || echo "  Warning: json-to-markdown.py not found"
    cp "$PROJECT_ROOT/opencode/scripts/json-to-adoit.py" "$PROJECT_ROOT/shared/scripts/" 2>/dev/null || echo "  Warning: json-to-adoit.py not found"
    echo "  Copied conversion scripts from opencode/scripts"
fi

# Copy ADOIT generator module if available
if [ -d "$PROJECT_ROOT/opencode/.opencode/skills/adoit-archimate/scripts" ]; then
    cp "$PROJECT_ROOT/opencode/.opencode/skills/adoit-archimate/scripts/adoit_excel_generator.py" "$PROJECT_ROOT/shared/scripts/" 2>/dev/null || echo "  Warning: adoit_excel_generator.py not found"
    cp "$PROJECT_ROOT/opencode/.opencode/skills/adoit-archimate/scripts/validate_import.py" "$PROJECT_ROOT/shared/scripts/" 2>/dev/null || echo "  Warning: validate_import.py not found"
    echo "  Copied ADOIT scripts from skills/adoit-archimate"
fi

# List scripts in shared volume
echo ""
echo "Scripts available in shared/scripts:"
ls -la "$PROJECT_ROOT/shared/scripts/" 2>/dev/null || echo "  No scripts found"
echo ""

# Copy n8n workflows to backup location (if not already there)
if [ -d "$PROJECT_ROOT/n8n/backup/workflows/architecture" ]; then
    echo "Architecture workflows found in n8n/backup/workflows/architecture"
    ls "$PROJECT_ROOT/n8n/backup/workflows/architecture/"
    echo ""
fi

# Check if --init-qdrant flag is provided
if [ "$1" == "--init-qdrant" ]; then
    echo "Initializing Qdrant collections..."

    # Check if Python is available
    if command -v python3 &> /dev/null; then
        python3 "$PROJECT_ROOT/scripts/setup-qdrant-collections.py" --qdrant-url "${QDRANT_URL:-http://localhost:6333}"
    else
        echo "  Warning: Python not found. Run setup-qdrant-collections.py manually."
    fi
fi

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Start the Docker stack: python start_services.py --profile <your-profile>"
echo "2. Import the workflows in n8n UI from n8n/backup/workflows/architecture/"
echo "3. Configure Ollama credentials in n8n"
echo "4. Test the pipeline:"
echo "   curl -X POST http://localhost:5678/webhook/architecture-pipeline \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"requirements\": \"Build a pet store inventory system...\"}'"
echo ""
echo "Optional:"
echo "- Initialize Qdrant: ./scripts/setup-architecture-pipeline.sh --init-qdrant"
echo "- Embed documents: python scripts/embed-documents.py --all --source-dir ./shared/knowledge"
