# DevOps Engineer & GitHub Docs Integration

## Overview

The **DevOps Engineer** agent runs in parallel with the PRD Generator pipeline to create the actual application container infrastructure while experts analyze requirements. All expert analysis documents are written to a `docs/analysis` folder in the GitHub repository.

## Architecture

```
Business Analyst (Requirements Complete)
           ↓
    ┌──────┴──────┐
    │             │
DevOps Engineer  PRD Generator Orchestrator
    │             │
    │             ├─→ Compliance & Risk
    │             ├─→ Business Architect
    │             ├─→ Experience Designer
Create App       ├─→ Technology CTO
Container        ├─→ Application Architect
    │             ├─→ Solution Architect
    │             └─→ Infrastructure Reviewer
    ↓                  ↓
GitHub Repo      Each expert writes
docs/analysis    to GitHub docs/analysis
    ↓                  ↓
    └──────┬──────────┘
           ↓
All analysis documents
in GitHub repository
```

## DevOps Engineer Workflow

### Responsibilities

1. **Create Application Container** - Via slack-api-server
2. **Monitor Argo Workflow** - Wait for infrastructure completion
3. **Initialize GitHub Docs** - Create `docs/analysis` folder
4. **Provide Infrastructure Context** - Return GitHub repo details

### Execution Flow

```
1. Receive project from Business Analyst
   ↓
2. Extract app-container name from project name
   ↓
3. Call slack-api-server to create infrastructure
   POST /slack/command
   Body: text=/create-app app-container=<name> github-org=<org> github-repo=<repo>
   ↓
4. Parse response for Argo Workflow name
   ↓
5. Poll Argo Workflow status (10s intervals)
   kubectl get workflow <name> -n argo -o jsonpath='{.status.phase}'
   ↓
6. Wait until status = "Succeeded"
   ↓
7. Create docs/analysis folder in GitHub
   PUT /repos/:owner/:repo/contents/docs/analysis/.gitkeep
   ↓
8. Write DevOps analysis report
   ↓
9. Return infrastructure_ready = true + GitHub URLs
```

### Slack API Integration

**Endpoint:** `http://istio-ingressgateway.istio-system/slack/command`

**Payload:**
```
POST /slack/command
Content-Type: application/x-www-form-urlencoded

text=/create-app app-container=habittracker github-org=myorg github-repo=habittracker
user_name=n8n-devops
channel_name=automation
```

**Response:**
```json
{
  "text": "Workflow: microservice-standard-contract-habittracker created successfully"
}
```

### Argo Workflow Monitoring

The DevOps Engineer monitors the Argo Workflow until completion:

```bash
# Check workflow status
kubectl get workflow microservice-standard-contract-habittracker -n argo -o jsonpath='{.status.phase}'

# Possible statuses:
# - Pending
# - Running
# - Succeeded
# - Failed
# - Error
```

**Polling Strategy:**
- Interval: 10 seconds
- Max retries: 60 (10 minutes total)
- Fail on: "Failed" or "Error" status

### GitHub Docs Initialization

Creates the `docs/analysis` folder structure:

```
github-repo/
└── docs/
    └── analysis/
        ├── .gitkeep                           # Folder placeholder
        ├── devops-infrastructure-setup.md     # DevOps report
        ├── compliance-risk-analysis.md        # Expert reports...
        ├── business-architecture.md
        ├── ux-analysis.md
        ├── cto-technology-decisions.md
        ├── application-architecture.md
        ├── solution-architecture-oam.md
        ├── infrastructure-review.md
        └── final-prd.md                       # Final PRD
```

## GitHub Docs Writer Helper

**Workflow:** `9-github-docs-writer.json`
**Webhook:** `/webhook/github/write-docs`

### Purpose

Centralized helper workflow for all experts to write their analysis documents to GitHub.

### Usage

```javascript
// From any expert workflow
const response = await fetch('http://n8n:5678/webhook/github/write-docs', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    projectId: 'uuid',
    expertName: 'compliance-risk-assessor',
    markdownContent: '# Compliance & Risk Analysis\n\n...',
    fileName: 'compliance-risk-analysis.md' // Optional
  })
});
```

### Features

- **Automatic file naming** - Defaults to `{expertName}-analysis-{timestamp}.md`
- **Update support** - Checks if file exists and updates (requires SHA)
- **Base64 encoding** - Handles content encoding for GitHub API
- **Error resilient** - Returns success even if file already exists

### GitHub API Operations

1. **Check file exists:**
   ```
   GET /repos/:owner/:repo/contents/docs/analysis/:filename
   ```

2. **Create or update file:**
   ```
   PUT /repos/:owner/:repo/contents/docs/analysis/:filename
   Body: {
     message: "docs: add :filename",
     content: "<base64-encoded-markdown>",
     sha: "<sha-if-updating>",
     branch: "main"
   }
   ```

## Parallel Execution Pattern

### Business Analyst Triggers

When requirements gathering is complete, the Business Analyst triggers **both** workflows in parallel:

```javascript
// In Business Analyst workflow, after "Insert Requirements" node

// Trigger 1: DevOps Engineer (async)
fetch('http://n8n:5678/webhook/devops-engineer', {
  method: 'POST',
  body: JSON.stringify({
    projectId: projectId,
    projectName: projectName,
    sessionState: sessionState,
    triggeredBy: 'business-analyst'
  })
});

// Trigger 2: PRD Generator (async)
fetch('http://n8n:5678/webhook/prd-generator', {
  method: 'POST',
  body: JSON.stringify({
    projectId: projectId,
    projectName: projectName,
    triggeredBy: 'business-analyst'
  })
});
```

### Why Parallel?

| Workflow | Duration | Task |
|----------|----------|------|
| DevOps Engineer | 5-10 min | Create app container, setup GitHub |
| PRD Generator | 15-20 min | 7 expert consultations |

**Total Serial:** 20-30 minutes
**Total Parallel:** 15-20 minutes (DevOps completes first)

### Synchronization Points

- **No blocking** - Both workflows run independently
- **Shared resource** - GitHub repository (created by DevOps first)
- **Eventual consistency** - All docs written to same folder

## Expert Analysis Workflow Pattern

All expert workflows must write their final analysis to GitHub:

### Updated Expert Workflow Structure

```
1. Webhook Trigger
2. Extract Inputs
3. Log Consultation Start
4. LLM Analysis
5. Update Shared Context (in-memory)
6. Save Updated Context (database)
7. ✨ Write to GitHub Docs (NEW) ✨
8. Complete Consultation
9. Respond to Orchestrator
```

### Implementation in Each Expert

Add this node after "Save Updated Context":

```json
{
  "name": "Write Analysis to GitHub",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 3,
  "position": [X, Y],
  "parameters": {
    "method": "POST",
    "url": "http://n8n:5678/webhook/github/write-docs",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "projectId",
          "value": "={{ $json.projectId }}"
        },
        {
          "name": "expertName",
          "value": "compliance-risk-assessor"
        },
        {
          "name": "markdownContent",
          "value": "={{ $node['Update Shared Context'].json.markdownReport }}"
        },
        {
          "name": "fileName",
          "value": "compliance-risk-analysis.md"
        }
      ]
    }
  }
}
```

## Database Schema Updates

### New Tables

**`github_docs_files`** - Tracks all documents written to GitHub
```sql
CREATE TABLE github_docs_files (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES e2e_projects(id),
    expert_name TEXT,
    file_name TEXT,
    file_path TEXT,
    file_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Updated Columns

**`e2e_projects`:**
- `infrastructure_ready BOOLEAN` - DevOps completion flag
- `github_docs_url TEXT` - URL to docs/analysis folder

### Expert Names

Updated constraint to include:
- `business-analyst`
- **`devops-engineer`** ⭐ NEW
- `compliance-risk-assessor`
- `business-architect`
- `experience-designer`
- `technology-cto`
- `application-architect`
- `solution-architect`
- `infrastructure-reviewer`

## Monitoring

### Check Infrastructure Status

```sql
SELECT
  project_name,
  infrastructure_ready,
  github_docs_url,
  status
FROM e2e_projects
WHERE id = 'YOUR_PROJECT_ID';
```

### View All Docs Written

```sql
SELECT
  expert_name,
  file_name,
  file_url,
  created_at
FROM github_docs_files
WHERE project_id = 'YOUR_PROJECT_ID'
ORDER BY created_at ASC;
```

### Check DevOps Progress

```sql
SELECT
  expert_name,
  status,
  duration_seconds,
  output_artifacts->>'infrastructure_ready' as infra_ready
FROM expert_consultations
WHERE project_id = 'YOUR_PROJECT_ID'
  AND expert_name = 'devops-engineer';
```

### Monitor Argo Workflow

```bash
# Watch workflow progress
kubectl get workflow -n argo -w

# Check specific workflow
kubectl get workflow microservice-standard-contract-<name> -n argo -o yaml

# View workflow logs
kubectl logs -n argo -l workflows.argoproj.io/workflow=microservice-standard-contract-<name>
```

## Error Handling

### DevOps Engineer Failures

**Scenario:** Slack API call fails

```javascript
{
  "success": false,
  "error": "App container creation failed",
  "projectId": "uuid"
}
```

**Action:**
- Mark expert_consultations status = 'failed'
- Do NOT block PRD Generator (runs independently)
- Manual intervention required for infrastructure

**Recovery:**
```bash
# Manually trigger DevOps again
curl -X POST http://localhost:8001/webhook/devops-engineer \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "uuid",
    "projectName": "HabitTracker",
    "sessionState": {...}
  }'
```

### Argo Workflow Timeout

**Scenario:** Workflow takes > 10 minutes

**Action:**
- Check workflow status manually
- Extend polling timeout in DevOps workflow
- Or mark as failed and investigate

### GitHub API Failures

**Scenario:** Cannot create docs folder

**Action:**
- Expert analysis still saved to database
- GitHub write is non-blocking
- Can retry GitHub write later via helper

**Recovery:**
```bash
# Manually write docs
curl -X POST http://localhost:8001/webhook/github/write-docs \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "uuid",
    "expertName": "compliance-risk-assessor",
    "markdownContent": "...",
    "fileName": "compliance-risk-analysis.md"
  }'
```

## Testing

### Test DevOps Engineer Alone

```bash
curl -X POST http://localhost:8001/webhook/devops-engineer \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "test-uuid",
    "projectName": "TestApp",
    "sessionState": {
      "githubRepo": "https://github.com/myorg/testapp",
      "targetBranch": "main",
      "projectType": "web"
    },
    "triggeredBy": "manual"
  }'
```

### Test GitHub Docs Writer

```bash
curl -X POST http://localhost:8001/webhook/github/write-docs \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "test-uuid",
    "expertName": "test-expert",
    "markdownContent": "# Test Analysis\n\nThis is a test.",
    "fileName": "test-analysis.md"
  }'
```

### Verify GitHub Folder

```bash
# Check folder exists
curl https://api.github.com/repos/myorg/testapp/contents/docs/analysis \
  -H "Authorization: token $GITHUB_TOKEN"

# Check specific file
curl https://api.github.com/repos/myorg/testapp/contents/docs/analysis/test-analysis.md \
  -H "Authorization: token $GITHUB_TOKEN"
```

## Environment Variables

### Required

- `GITHUB_TOKEN` - GitHub personal access token with `repo` scope
- `ISTIO_GATEWAY_URL` (optional) - Defaults to `http://istio-ingressgateway.istio-system`

### Setting in n8n

```bash
# In n8n Docker container
docker exec -it n8n sh
export GITHUB_TOKEN="ghp_your_token_here"

# Or in docker-compose.yml
environment:
  - GITHUB_TOKEN=${GITHUB_TOKEN}
  - ISTIO_GATEWAY_URL=http://istio-ingressgateway.istio-system
```

## Best Practices

### 1. Idempotent Operations

- DevOps Engineer checks if infrastructure exists before creating
- GitHub Docs Writer updates files if they exist (using SHA)

### 2. Async Communication

- DevOps and PRD run in parallel (no blocking)
- Expert analysis written to GitHub asynchronously

### 3. Graceful Degradation

- If GitHub write fails, analysis still in database
- Can retry GitHub operations later

### 4. Audit Trail

- All operations logged in `expert_consultations`
- GitHub commits provide version history
- Database + GitHub = dual backup

### 5. Resource Naming

- App container name: lowercase, hyphenated project name
- GitHub file names: `{expert-name}-analysis.md`
- Consistent naming across infrastructure and docs

## Integration with Existing Migration Platform

### Shared Infrastructure

- **Slack API Server** - Used by both platforms
- **Argo Workflows** - Manages infrastructure creation
- **GitHub** - Source of truth for configuration

### Separate Concerns

- **E2E Platform** - Creates new projects from scratch
- **Migration Platform** - Migrates existing React Native apps
- **Both** - Write to GitHub, use Argo, share Slack API

---

## Summary

The DevOps Engineer integration provides:

✅ **Parallel execution** - Infrastructure created while experts analyze
✅ **GitHub-centric** - All analysis in repository
✅ **Production-ready** - Real infrastructure via Argo Workflows
✅ **Auditable** - Database + GitHub dual tracking
✅ **Resilient** - Independent workflows, graceful degradation

All expert analysis documents end up in one place: **`docs/analysis`** in the GitHub repository.

---

**Next Steps:**
1. Run database schema updates
2. Import DevOps Engineer workflow
3. Import GitHub Docs Writer helper
4. Test end-to-end with parallel execution
5. Verify docs written to GitHub

---

*Generated: 2025-01-27*
*E2E Agent Pipeline with DevOps Integration*
