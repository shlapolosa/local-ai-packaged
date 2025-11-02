# Migration Platform - n8n Workflows

Complete n8n workflow automation for white-label migration from React Native to native platforms (iOS, Android, Web).

## Overview

This platform uses:
- **n8n** - Workflow orchestration
- **Ollama + OpenWebUI** - Local LLM for code generation
- **PostgreSQL** - State management
- **GitHub** - PR-based approval gates
- **Git** - Version control and governance

## Architecture

```
User → Configuration Assistant (chat) → Master Orchestrator
                                             ↓
                                        Agent Workflows
                                             ↓
                                        Git/GitHub (PRs)
                                             ↓
                                        GitHub Webhooks → n8n
```

## 🆕 Quick Start with Chat Interface

**NEW!** Don't know the API format? Use the interactive Configuration Assistant:

```bash
# 1. Import the Configuration Assistant workflow
# 2. Open the chat interface
open n8n-workflows/chat-interface.html

# 3. Chat with the assistant - it will guide you step by step!
# 4. Migration starts automatically when you're ready
```

**See full guide:** [CONFIGURATION-ASSISTANT-GUIDE.md](CONFIGURATION-ASSISTANT-GUIDE.md)

---

## Setup Instructions

### 1. Database Setup

Run the database schema:

```bash
# Connect to your PostgreSQL
docker exec -i db psql -U postgres -d postgres < database-schema.sql
```

### 2. Import n8n Workflows

Import all workflows into n8n (order matters):

**Interactive Setup (Recommended):**
0. **0-configuration-assistant.json** ⭐ - Interactive chat to configure migration

**Core Workflows:**
1. **1-github-webhook-handler.json** - Handles GitHub webhook events
2. **2-master-orchestrator.json** - Main workflow coordinating all stages

**Agent Workflows:**
3. **3-repo-analyzer-agent.json** - Analyzes React Native codebase
4. **4-contract-generator-agent.json** - Generates TypeScript contracts
5. **5-code-transformer-ios.json** - Generates SwiftUI code
6. **6-code-transformer-android.json** - Generates Jetpack Compose code
7. **7-code-transformer-web.json** - Generates React web code
8. **8-validator-agent.json** - Validates generated code
9. **9-visual-diff-agent.json** - Compares RN vs native screenshots
10. **10-test-generator-agent.json** - Generates unit tests
11. **11-documentation-generator-agent.json** - Generates component docs

**Import via n8n UI:**
- Go to n8n (http://localhost:8001)
- Click "Workflows" → "Import from File"
- Select each JSON file and import

### 3. Configure PostgreSQL Credentials in n8n

1. Go to n8n → Credentials
2. Add new "PostgreSQL" credential:
   - **Name:** `PostgreSQL Main` (must match exactly)
   - **Host:** `db`
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Password:** `password` (from your .env)
   - **Port:** `5432`

### 4. Verify GitHub Webhook

Your GitHub webhook should already be configured:
- **URL:** `https://0dbf302010aa.ngrok-free.app/webhook/github/events`
- **Secret:** `f5ef9c2a7a657ca80a5ea26175038564adce5fd95b2dad0e04683126a058da15`
- **Events:** Pull requests, Pull request reviews, Check runs

### 5. Environment Variables

Verify these are in your `.env`:

```bash
GITHUB_TOKEN=${PERSONAL_ACCESS_TOKEN}
GITHUB_OWNER=shlapolosa
GITHUB_REPO=coding-assistant
GITHUB_WEBHOOK_SECRET=f5ef9c2a7a657ca80a5ea26175038564adce5fd95b2dad0e04683126a058da15
GIT_USER_EMAIL=socrates.hlapolosa@gmail.com
GIT_USER_NAME="Migration Bot"
```

## Usage

### Option 1: Interactive Chat (Recommended for First Time)

**Use the Configuration Assistant:**

```bash
# Open the chat interface
open n8n-workflows/chat-interface.html

# Or serve it with:
cd n8n-workflows
python3 -m http.server 8080
# Then open: http://localhost:8080/chat-interface.html
```

**The assistant will guide you through:**
1. React Native repository URL
2. Monorepo URL for migration
3. Target platforms (iOS, Android, Web)
4. Migration stages to complete
5. GitHub reviewers
6. Final confirmation

**Then it automatically starts the migration!**

See full guide: [CONFIGURATION-ASSISTANT-GUIDE.md](CONFIGURATION-ASSISTANT-GUIDE.md)

---

### Option 2: Direct API Call (For Automation/Scripts)

Send POST request to Master Orchestrator:

```bash
curl -X POST http://localhost:8001/webhook/start-migration \
  -H "Content-Type: application/json" \
  -d '{
    "repoRN": "https://github.com/yourorg/rn-app",
    "repoNative": null,
    "monorepoUrl": "https://github.com/shlapolosa/coding-assistant",
    "strategy": {
      "startStage": 1,
      "endStage": 3
    },
    "platforms": ["ios", "android", "web"],
    "reviewers": ["shlapolosa"],
    "targetBranch": "main"
  }'
```

---

### Migration Flow

1. **Master Orchestrator** receives request
2. Clones monorepo, scaffolds structure
3. Calls **Repo Analyzer Agent** → analyzes RN codebase
4. Creates branch `migration/stage-1-analysis`
5. Commits analysis files
6. **Creates PR #1** on GitHub
7. **Workflow PAUSES** waiting for PR merge
8. You review PR on GitHub, approve & merge
9. GitHub webhook → **Workflow RESUMES**
10. Calls **Contract Generator Agent**
11. Creates branch `migration/stage-2-contracts`
12. **Creates PR #2**
13. **Workflow PAUSES** again
14. ... and so on for each stage

### Monitoring

**Check migration status:**

```sql
SELECT
  m.id,
  m.status,
  m.current_stage,
  m.created_at,
  COUNT(ag.id) as total_prs,
  COUNT(CASE WHEN ag.status = 'merged' THEN 1 END) as merged_prs
FROM migrations m
LEFT JOIN approval_gates ag ON m.id = ag.migration_id
GROUP BY m.id
ORDER BY m.created_at DESC;
```

**View pending PRs:**

```sql
SELECT
  ag.gate_name,
  ag.pr_number,
  ag.pr_url,
  ag.status,
  ag.created_at
FROM approval_gates ag
WHERE ag.status = 'pending'
ORDER BY ag.created_at DESC;
```

## Workflow Details

### 0. Configuration Assistant (NEW!)
- **Interactive chat interface** for user-friendly setup
- Asks questions one at a time
- Validates responses (URL format, valid stages, etc.)
- Extracts information from natural language
- Shows progress visually
- Confirms configuration before starting
- **Automatically triggers Master Orchestrator** when ready
- Can be used via: Web chat, OpenWebUI function, or API

### 1. GitHub Webhook Handler
- Receives all GitHub events
- Verifies HMAC signature
- Routes PR merge events to Master Orchestrator
- Updates approval_gates table

### 2. Master Orchestrator
- Main state machine
- Coordinates all stages
- Creates PRs, waits for approvals
- Calls specialized agents
- Handles Stage 0 (scaffold) → Stage 1 (analysis) → Stage 2 (contracts) → Stage 3 (code gen)

### 3. Repo Analyzer Agent
- Clones React Native repo
- Finds all components (*.tsx, *.ts, *.jsx, *.js)
- Analyzes each component with Ollama
- Extracts: complexity, risk, dependencies, native modules
- Generates component inventory, risk matrix, dependency graph
- Returns structured JSON

### 4. Contract Generator Agent
- Gets component inventory from DB
- For each component:
  - Calls Ollama to generate TypeScript interface
  - Validates syntax
  - Writes to `packages/shared-components/contracts/`
- Extracts design tokens
- Returns contracts + tokens

### 5. Code Transformer Agents (iOS/Android/Web)
- Gets contracts from DB
- For each contract:
  - Calls Ollama with platform-specific prompt
  - Generates SwiftUI / Jetpack Compose / React code
  - Writes to `packages/native-components/{platform}/`
- Returns generated code

### 6. Validator Agent
- Finds generated code files
- Runs platform-specific validators:
  - Swift: `swiftc -typecheck`
  - Kotlin: `kotlinc -no-stdlib`
  - TypeScript: `tsc --noEmit`
- Returns validation results

### 7. Visual Diff Agent
- (Placeholder - requires Playwright setup)
- Takes screenshots of RN components
- Takes screenshots of native components
- Compares with pixelmatch
- Returns similarity scores

### 8. Test Generator Agent
- Finds generated components
- Calls Ollama to generate unit tests
- Returns test code

### 9. Documentation Generator Agent
- Gets components from DB
- Calls Ollama to generate markdown docs
- Writes to `docs/components/`
- Returns documentation

## Troubleshooting

### 502 Errors on GitHub Webhook
- Normal if workflows not imported yet
- Import workflows, activate them in n8n
- Test by merging a dummy PR

### Workflow Not Resuming After PR Merge
- Check GitHub webhook is configured correctly
- Verify webhook secret matches
- Check n8n execution logs
- Ensure approval_gates table has correct pr_number

### LLM Errors (OpenWebUI)
- Verify Ollama is running: `curl http://ollama:11434/api/tags`
- Verify OpenWebUI: `curl http://open-webui:8080/api/health`
- Check model is pulled: `docker exec ollama ollama list`
- If missing: `docker exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M`

### PostgreSQL Connection Errors
- Verify credentials in n8n match .env
- Test connection: `docker exec -it db psql -U postgres -d postgres -c "SELECT 1"`
- Check tables exist: `docker exec -it db psql -U postgres -d postgres -c "\dt"`

### Git Operations Failing
- Ensure git is available in n8n container
- Check /tmp/migrations directory exists
- Verify GitHub token has repo permissions

## Extending

### Adding New Agent
1. Create new workflow JSON
2. Add webhook trigger: `/webhook/agent-your-agent`
3. Implement agent logic
4. Call from Master Orchestrator at appropriate stage

### Adding New Stage
1. Edit Master Orchestrator
2. Add new stage after existing stage
3. Call appropriate agents
4. Create PR for approval
5. Add webhook wait node

### Customizing Prompts
- Edit the `jsonBody` in HTTP Request nodes
- Modify system/user prompts
- Adjust temperature for more/less creative output

## Configuration Reference

### Models Used
- **Repo Analyzer:** `qwen2.5:7b-instruct-q4_K_M` (fast, lightweight)
- **Contract Generator:** `qwen2.5:7b-instruct-q4_K_M`
- **Code Transformers:** `qwen2.5:7b-instruct-q4_K_M`
- **Test Generator:** `qwen2.5:7b-instruct-q4_K_M`
- **Docs Generator:** `qwen2.5:7b-instruct-q4_K_M`

### Upgrade to Larger Models
For better quality, use `qwen2.5-coder:32b`:

1. Pull model: `docker exec ollama ollama pull qwen2.5-coder:32b`
2. Edit workflows, replace model name in HTTP Request nodes
3. Save and reactivate workflows

## Next Steps

1. Import all workflows ✓
2. Configure PostgreSQL credentials ✓
3. Run database schema ✓
4. Test with sample migration
5. Review first PR on GitHub
6. Merge and watch workflow resume
7. Iterate and refine prompts

## Support

- **n8n Docs:** https://docs.n8n.io/
- **Ollama Docs:** https://ollama.ai/
- **OpenWebUI Docs:** https://docs.openwebui.com/
- **GitHub Webhook Docs:** https://docs.github.com/webhooks

---

🤖 Generated by Migration Platform
