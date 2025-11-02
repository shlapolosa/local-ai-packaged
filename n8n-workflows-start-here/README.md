# n8n Workflow Automation Platform

**Complete n8n workflow automation for:**
- 📋 **PRD Generation** - Expert-driven requirements & architecture
- 🏗️ **End-to-End Solution Development** - Full-stack project generation
- 🔄 **White-Label Migration** - React Native to native platforms

---

## 📚 Documentation Index

### Getting Started
- **[Quick Start](docs/QUICK-START.md)** - 5-minute setup guide
- **[Configuration](docs/CONFIGURATION.md)** - Environment setup & credentials
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System architecture & design

### Core Features
- **[Intent Routing](docs/INTENT-ROUTING.md)** - LLM-powered workflow routing
- **[PRD Generation](docs/PRD-GENERATION.md)** - Expert consultation pipeline
- **[White-Label Migration](docs/WHITE-LABEL-MIGRATION.md)** - React Native migration

### Technical Reference
- **[Database Schema](docs/DATABASE-SCHEMA.md)** - Tables, views, and queries
- **[Testing & Validation](docs/TESTING.md)** - Test suite and quality assurance
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues & solutions
- **[API Reference](docs/API-REFERENCE.md)** - Webhook endpoints & models

---

## Overview

This platform provides a comprehensive n8n-based workflow automation system that intelligently routes user intents to specialized workflows:

### Technology Stack
- **n8n** - Workflow orchestration
- **Ollama + OpenWebUI** - Local LLM (Qwen 2.5 models)
- **PostgreSQL** - State management and audit trail
- **GitHub** - Version control and PR-based approvals
- **Git** - Repository management

### Key Features

#### 📋 PRD Generation & E2E Solutions
- Interactive requirements gathering via Business Analyst chat
- Automated expert consultations (7 specialized agents)
- Shared context management across experts
- Audit trail generation for compliance
- PRD and OAM generation for GitOps deployment
- **Expert Pipeline:** Compliance → Business → UX → CTO → App → Solution → Infrastructure

#### 🔄 White-Label Migration
- Migrate React Native apps to native platforms
- Mono-repo structure with platform-specific code
- Stage-based workflow with PR approvals
- Code generation for iOS (SwiftUI), Android (Jetpack Compose), Web (React)
- **Stages:** Scaffold → Analysis → Contracts → Code Generation

#### 🎯 Intent-Aware Routing
- LLM-powered intent classification
- Automatic workflow selection
- Confidence-based clarification
- Session state management

---

## Quick Start

### Prerequisites
- n8n running: `http://localhost:8001`
- PostgreSQL: Docker container `db`
- Ollama + OpenWebUI running
- Model: `qwen2.5:7b-instruct-q4_K_M`

### 5-Minute Setup

#### 1. Database Setup
```bash
# Import E2E schema
docker exec -i db psql -U postgres -d postgres < database/e2e-schema.sql

# Import migration schema (if using white-label)
docker exec -i db psql -U postgres -d postgres < database-schema.sql

# Verify tables
docker exec -it db psql -U postgres -d postgres -c "\dt"
```

#### 2. Import Workflows to n8n

**Open n8n**: http://localhost:8001

**Import in order:**

**Core Intent Router:**
1. `0-configuration-assistant-intent-router.json` ⭐ Main entry point

**PRD Generation (11 workflows):**
2. `workflows/0-business-analyst-e2e.json`
3. `workflows/1-prd-generator-orchestrator.json`
4. `workflows/2-expert-compliance-risk.json`
5. `workflows/3-expert-business-architect.json`
6. `workflows/4-expert-experience-designer.json`
7. `workflows/5-expert-technology-cto.json`
8. `workflows/6-expert-application-architect.json`
9. `workflows/7-expert-solution-architect.json`
10. `workflows/8-expert-infrastructure-reviewer.json`
11. `workflows/1b-devops-engineer.json`
12. `workflows/9-github-docs-writer.json`

**White-Label Migration (11 workflows):**
13. `0-configuration-assistant.json`
14. `1-github-webhook-handler.json`
15. `2-master-orchestrator.json`
16-24. Additional agent workflows (see [White-Label Migration](docs/WHITE-LABEL-MIGRATION.md))

#### 3. Configure PostgreSQL Credentials

1. n8n → Credentials → Add Credential
2. Search "PostgreSQL"
3. Configure:
   - **Name:** `PostgreSQL Main` (exact match)
   - **Host:** `db`
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Password:** `password`
   - **Port:** `5432`
4. Save

#### 4. Open Chat Interface

```bash
# Serve chat interface
cd /Users/socrateshlapolosa/Development/local-ai-packaged/n8n-workflows-start-here
python3 -m http.server 8080
```

Then open: http://localhost:8080/chat-interface.html

---

## Workflow Counts

**Total Workflows:** 24

**By Category:**
- Intent Router: 1
- PRD Generation: 11
- White-Label Migration: 11
- GitHub Integration: 1

**Entry Points:**
- Main: `0-configuration-assistant-intent-router.json`
- Business Analyst: `workflows/0-business-analyst-e2e.json`
- Migration Config: `0-configuration-assistant.json`

---

## Supported Intents

### 1. 📋 PRD Generation (`prd_generation`)
**Keywords:** PRD, requirements, architecture, design, specification, documentation, OAM, infrastructure

**Routes to:** Business Analyst → PRD Generator → 7 Experts → DevOps

**Example triggers:**
```
"I need a PRD for my mobile app"
"Help me create architecture documentation"
"Generate requirements for a new project"
```

### 2. 🏗️ End-to-End Solution (`e2e_solution`)
**Keywords:** build, create, develop, new app, solution, project, from scratch

**Routes to:** Business Analyst → PRD Generator → 7 Experts → DevOps

**Example triggers:**
```
"Build a new mobile app"
"Create a complete solution from scratch"
"Develop a healthcare platform"
```

### 3. 🔄 White-Label Migration (`whitelabel_migration`)
**Keywords:** migrate, migration, react native, iOS, Android, white-label, platform, mono-repo

**Routes to:** Migration Config → Master Orchestrator → 6 Agents

**Example triggers:**
```
"Migrate my React Native app"
"Convert my RN app to iOS and Android"
"White-label migration for my mobile app"
```

### 4. ❓ Help/Unknown
**Routes to:** Clarification response with available services

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    User Message                               │
│                       ↓                                       │
│           Intent Router (LLM Classification)                  │
│                       ↓                                       │
│   ┌──────────────────┴────────────────┬──────────────────┐  │
│   ▼                  ▼                 ▼                   │  │
│ PRD/E2E         White-Label       Unknown/Help             │  │
│ Generation       Migration        Clarification            │  │
└──────────────────────────────────────────────────────────────┘
```

For detailed architecture diagrams, see **[Architecture Overview](docs/ARCHITECTURE.md)**.

---

## Project Structure

```
/Users/socrateshlapolosa/Development/local-ai-packaged/n8n-workflows-start-here/
│
├── README.md                                    # This file
├── docs/                                        # Documentation
│   ├── QUICK-START.md                          # 5-minute setup
│   ├── ARCHITECTURE.md                         # System architecture
│   ├── INTENT-ROUTING.md                       # Intent detection
│   ├── PRD-GENERATION.md                       # PRD workflow details
│   ├── WHITE-LABEL-MIGRATION.md                # Migration details
│   ├── DATABASE-SCHEMA.md                      # Database reference
│   ├── CONFIGURATION.md                        # Setup guide
│   ├── TESTING.md                              # Test suite
│   ├── TROUBLESHOOTING.md                      # Common issues
│   └── API-REFERENCE.md                        # Webhook endpoints
│
├── workflows/                                   # PRD Generation workflows
│   ├── 0-business-analyst-e2e.json
│   ├── 1-prd-generator-orchestrator.json
│   ├── 1b-devops-engineer.json
│   ├── 2-expert-compliance-risk.json
│   ├── 3-expert-business-architect.json
│   ├── 4-expert-experience-designer.json
│   ├── 5-expert-technology-cto.json
│   ├── 6-expert-application-architect.json
│   ├── 7-expert-solution-architect.json
│   ├── 8-expert-infrastructure-reviewer.json
│   └── 9-github-docs-writer.json
│
├── database/                                    # Database schemas
│   ├── e2e-schema.sql                          # PRD generation schema
│   └── database-schema.sql                     # Migration schema
│
├── tests/                                       # Test suite
│   ├── test_workflow_validation.py             # Structure tests
│   └── pytest.ini                              # Test configuration
│
├── chat-interface.html                          # Web chat UI
│
└── [White-Label Migration Workflows]           # Root-level workflows
    ├── 0-configuration-assistant.json
    ├── 0-configuration-assistant-intent-router.json
    ├── 1-github-webhook-handler.json
    ├── 2-master-orchestrator.json
    └── [Additional agent workflows...]
```

---

## Development Workflow

1. **User sends message** → Chat interface or webhook
2. **Intent Router analyzes** → LLM classifies intent
3. **Route to workflow:**
   - PRD/E2E → Business Analyst
   - White-Label → Migration Config
   - Unknown → Clarification
4. **Workflow executes** → Agents process request
5. **Results delivered** → PRD, OAM, or migrated code

---

## Monitoring & Observability

### n8n Execution Logs
View real-time execution in n8n UI:
- http://localhost:8001/workflows
- Click "Executions" tab
- Filter by workflow name

### Database Queries
Monitor projects and progress:
```bash
# View active projects
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT * FROM v_project_dashboard ORDER BY created_at DESC;"

# Check expert consultations
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT expert_name, status, duration_seconds
   FROM expert_consultations
   WHERE project_id = 'YOUR_PROJECT_ID';"
```

For complete monitoring queries, see **[Database Schema](docs/DATABASE-SCHEMA.md)**.

---

## Testing

### Run Test Suite
```bash
cd tests
pytest test_workflow_validation.py -v
```

**Test Coverage:**
- Structural validation (8 tests)
- Data flow validation (2 tests)
- Security validation (2 tests)

**All 12 tests passing ✅**

For detailed testing documentation, see **[Testing & Validation](docs/TESTING.md)**.

---

## Troubleshooting

### Common Issues

**Chat Interface Not Connecting:**
```bash
# Check n8n is running
docker ps | grep n8n

# Verify workflow is active
# Visit: http://localhost:8001/workflows
```

**Database Connection Failed:**
```bash
# Test PostgreSQL connection
docker exec -it db psql -U postgres -d postgres -c "SELECT 1"

# Verify credentials in n8n match exactly
```

**LLM Errors:**
```bash
# Check Ollama is running
curl http://ollama:11434/api/tags

# Pull model if missing
docker exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M
```

For complete troubleshooting guide, see **[Troubleshooting](docs/TROUBLESHOOTING.md)**.

---

## Contributing

Contributions welcome! Please:
1. Follow existing workflow patterns
2. Add tests for new workflows
3. Update documentation
4. Test end-to-end before submitting PR

---

## Support & Resources

### n8n Resources
- n8n Docs: https://docs.n8n.io/
- n8n Community: https://community.n8n.io/

### LLM Resources
- Ollama Docs: https://ollama.ai/
- OpenWebUI Docs: https://docs.openwebui.com/
- Qwen Models: https://github.com/QwenLM/Qwen

### Database
- PostgreSQL Docs: https://www.postgresql.org/docs/

---

**Platform Version:** n8n Workflow Automation v1.0
**OAM Specification:** core.oam.dev/v1beta1
**Last Updated:** 2025-01-27
