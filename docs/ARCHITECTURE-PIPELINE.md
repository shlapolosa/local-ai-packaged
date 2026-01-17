# n8n Architecture Pipeline

This document describes the AI-powered architecture generation pipeline using n8n and Ollama.

## Overview

The Architecture Pipeline automates TOGAF-based enterprise architecture generation using:
- **n8n**: Workflow orchestration
- **Ollama**: Local LLM inference (qwen2.5:7b-instruct)
- **Qdrant**: Vector database for RAG knowledge base
- **Python scripts**: JSON to ArchiMate/OpenAPI/SQL conversion

## Quick Start

### 1. Run Setup

```bash
./scripts/setup-architecture-pipeline.sh
```

This creates:
- `shared/scripts/` - Conversion scripts accessible to n8n
- `shared/artifacts/` - Generated output directory
- `shared/knowledge/` - Knowledge base document directories
- `projects/` - Taskmaster project workspace

### 2. Start the Stack

```bash
python start_services.py --profile gpu-nvidia  # or cpu, gpu-amd
```

### 3. Import Workflows

In n8n UI (http://localhost:5678):
1. Go to Workflows
2. Import from `n8n/backup/workflows/architecture/`
3. Activate the workflows

### 4. Test the Pipeline

```bash
curl -X POST http://localhost:5678/webhook/architecture-pipeline \
  -H 'Content-Type: application/json' \
  -d '{
    "requirements": "Build a healthcare appointment booking system. Patients should be able to self-schedule appointments online, view provider availability, and receive automated reminders. Must integrate with Epic EHR via FHIR R4 APIs. Budget: $250,000. Timeline: 8 months.",
    "projectName": "healthcare-appointment-system"
  }'
```

## Workflows

### Architecture Pipeline (`architecture-pipeline.json`)

Main orchestrating workflow that:
1. Receives requirements via webhook
2. Generates BRD (Business Requirements Document)
3. Generates Business Architecture (ArchiMate JSON)
4. Generates Application Architecture (ArchiMate JSON)
5. Converts outputs to final formats (XML, Markdown)
6. Saves artifacts to shared volume

**Webhook**: `POST /webhook/architecture-pipeline`

**Input**:
```json
{
  "requirements": "Your project requirements...",
  "projectName": "optional-project-name"
}
```

**Output**:
```json
{
  "status": "completed",
  "sessionId": "20260117-123456",
  "artifactsPath": "/data/shared/artifacts/20260117-123456",
  "artifacts": ["brd.json", "brd.md", "business-architecture.json", ...]
}
```

### Solution Design Workflow (`solution-design-workflow.json`)

Generates API and database designs:
1. Receives application architecture
2. Generates OpenAPI 3.1 specification
3. Generates PostgreSQL DDL schema
4. Converts to YAML and SQL files

**Webhook**: `POST /webhook/solution-design`

**Input**:
```json
{
  "appArchitecture": "...",
  "brd": "...",
  "sessionId": "optional-session-id"
}
```

## Generated Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| `brd.json` | JSON | Business Requirements Document (structured) |
| `brd.md` | Markdown | Business Requirements Document (readable) |
| `business-architecture.json` | JSON | ArchiMate Business Layer elements |
| `business-architecture.archimate` | XML | Archi-compatible ArchiMate file |
| `application-architecture.json` | JSON | ArchiMate Application Layer elements |
| `application-architecture.archimate` | XML | Archi-compatible ArchiMate file |
| `openapi-spec.json` | JSON | API specification (intermediate) |
| `openapi.yaml` | YAML | OpenAPI 3.1 specification |
| `sql-schema.json` | JSON | Database schema (intermediate) |
| `schema.sql` | SQL | PostgreSQL DDL |

## Conversion Scripts

Located in `shared/scripts/`:

| Script | Input | Output |
|--------|-------|--------|
| `json-to-archimate.py` | ArchiMate JSON | ArchiMate XML (.archimate) |
| `json-to-markdown.py` | BRD JSON | Markdown (.md) |
| `json-to-openapi.py` | API JSON | OpenAPI YAML |
| `json-to-sql.py` | Schema JSON | PostgreSQL DDL |
| `json-to-adoit.py` | ArchiMate JSON | ADOIT Excel import |

## Knowledge Base (RAG)

### Collections

| Collection | Purpose |
|------------|---------|
| `capability-maps` | Organization capability models |
| `reference-architectures` | Standard patterns, templates |
| `guardrails-principles` | Org constraints, policies |
| `existing-landscape` | Current APIs, schemas, components |
| `compliance-requirements` | HIPAA, GDPR, SOC2 docs |

### Setup Knowledge Base

```bash
# Initialize collections
python scripts/setup-qdrant-collections.py

# Embed documents
python scripts/embed-documents.py --all --source-dir ./shared/knowledge
```

### Add Documents

Place documents in the appropriate subdirectory:
- `shared/knowledge/capability-maps/` - Capability model markdown files
- `shared/knowledge/reference-architectures/` - Architecture pattern docs
- `shared/knowledge/guardrails-principles/` - Policy documents
- etc.

Supported formats: `.md`, `.txt`, `.json`, `.yaml`

## Taskmaster Integration

The `taskmaster` container provides AI-powered task breakdown:

```bash
# Access taskmaster container
docker exec -it taskmaster bash

# Initialize project
cd /app/projects/my-project
taskmaster init --model qwen2.5:7b-instruct

# Parse PRD
taskmaster parse-prd --input /data/shared/artifacts/session-id/prd.md

# Expand tasks
taskmaster expand-all

# Export tasks
cat .taskmaster/tasks.json
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Webhook (requirements input)                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Phase 2: BRD Generation                                     │
│     └─→ Ollama (qwen2.5:7b-instruct)                         │
│         └─→ JSON → Markdown                                  │
│                                                              │
│  Phase 3: Architecture                                       │
│     ├─→ Business Architecture → ArchiMate JSON → XML         │
│     └─→ Application Architecture → ArchiMate JSON → XML      │
│                                                              │
│  Phase 3.5: Solution Design                                  │
│     ├─→ OpenAPI JSON → YAML                                  │
│     └─→ SQL Schema JSON → DDL                                │
│                                                              │
│  Artifacts saved to /data/shared/artifacts/{session}/        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Ollama Connection Issues

Ensure n8n can reach Ollama:
```bash
docker exec -it n8n curl http://ollama:11434/api/tags
```

### Script Execution Errors

Check scripts are in the shared volume:
```bash
ls -la shared/scripts/
```

Re-run setup if missing:
```bash
./scripts/setup-architecture-pipeline.sh
```

### JSON Parsing Errors

The LLM sometimes produces invalid JSON. Check:
1. Model temperature is low (0.3 recommended)
2. Prompt explicitly requests "OUTPUT ONLY JSON"
3. Parse errors in n8n execution log

### Workflow Import Issues

If workflows don't appear:
1. Check n8n container logs: `docker logs n8n`
2. Manually import via n8n UI
3. Verify JSON file syntax

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_URL` | `http://qdrant:6333` | Qdrant server URL |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama server URL |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Model for embeddings |
| `TASKMASTER_MODEL` | `qwen2.5:7b-instruct-q4_K_M` | Model for Taskmaster |

### n8n Credentials

Required credentials in n8n:
1. **OpenAI API** (for Ollama): Base URL = `http://ollama:11434/v1`
2. **Postgres** (optional): For chat memory

## Future Enhancements

- [ ] PR approval gates with webhook callbacks
- [ ] Azure DevOps integration for story export
- [ ] Security/Compliance architect sub-workflows
- [ ] Multi-model support (Claude, GPT-4)
- [ ] Incremental architecture updates
