# End-to-End Solution Development - n8n Agent Workflows

Complete n8n workflow automation for transforming high-level system briefs into production-ready OAM (Open Application Model) definitions through expert agent consultations.

## Overview

This platform transforms the Claude Code agent architecture into n8n workflows, enabling:
- **Interactive requirements gathering** via Business Analyst chat interface
- **Automated expert consultations** following the agent pipeline sequence
- **Shared context management** across all expert agents
- **Audit trail generation** for compliance and traceability
- **PRD and OAM generation** ready for GitOps deployment

## Architecture

```
User → Business Analyst (Chat) → PRD Generator Orchestrator
                                         ↓
                                   Component Catalog
                                         ↓
                                  Expert Pipeline:
                                         ↓
                 ┌────────────────────────┴────────────────────────┐
                 │                                                  │
         Compliance & Risk ──→ Business Architect ──→ Experience Designer
                 │                      │                          │
                 └──────────────────────┴─────────────┬────────────┘
                                                      ↓
                                              Technology CTO
                                                      ↓
                                          Application Architect
                                                      ↓
                                          Solution Architect (PRD-to-OAM)
                                                      ↓
                                          Infrastructure Reviewer
                                                      ↓
                                            Final PRD + OAM Definitions
```

## Technology Stack

- **n8n** - Workflow orchestration
- **Ollama + OpenWebUI** - Local LLM (Qwen 2.5 models)
- **PostgreSQL** - State management and audit trail
- **GitHub** - OAM definition storage (optional)
- **Git** - Version control for generated artifacts

## Quick Start

### 1. Database Setup

Run the database schema:

```bash
# If using existing migration platform database
docker exec -i db psql -U postgres -d postgres < n8n-workflows/database/e2e-schema.sql

# Or if using dedicated database
psql -h localhost -U postgres -d your_database < n8n-workflows/database/e2e-schema.sql
```

### 2. Import n8n Workflows

Import workflows in order:

**Entry Point:**
0. `0-business-analyst-e2e.json` - Requirements gathering chat interface

**Core Orchestration:**
1. `1-prd-generator-orchestrator.json` - Main workflow coordinating all experts

**Expert Workflows:**
2. `2-expert-compliance-risk.json` - Compliance & Risk Assessor
3. `3-expert-business-architect.json` - Business Architect (ArchiMate)
4. `4-expert-experience-designer.json` - Experience Design Optimizer
5. `5-expert-technology-cto.json` - Technology CTO
6. `6-expert-application-architect.json` - Application Architect
7. `7-expert-solution-architect.json` - Solution Architect (PRD-to-OAM)
8. `8-expert-infrastructure-reviewer.json` - Infrastructure Reviewer

**Import via n8n UI:**
- Go to n8n (http://localhost:8001)
- Click "Workflows" → "Import from File"
- Select each JSON file and import
- Activate all workflows

### 3. Configure PostgreSQL Credentials

1. Go to n8n → Credentials
2. Add new "PostgreSQL" credential:
   - **Name:** `PostgreSQL Main` (must match exactly)
   - **Host:** `db` (or your PostgreSQL host)
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Password:** `password` (from your .env)
   - **Port:** `5432`

### 4. Open Business Analyst Chat Interface

```bash
# Option 1: Open directly
open n8n-workflows/chat-interfaces/business-analyst-chat.html

# Option 2: Serve with local server
cd n8n-workflows/chat-interfaces
python3 -m http.server 8080
# Then open: http://localhost:8080/business-analyst-chat.html
```

## Usage

### Interactive Requirements Gathering

1. **Open chat interface** (see Quick Start step 4)

2. **Describe your project:**
   ```
   "I want to build a mobile app for tracking daily habits
   with social features and AI-powered insights"
   ```

3. **Answer clarifying questions:**
   - Project name
   - Project type (mobile/web/backend/fullstack)
   - Target platforms (iOS, Android, Web)
   - Core features (at least 3-5)
   - Technical/business constraints
   - Non-functional requirements

4. **Confirm requirements:**
   - Assistant summarizes all information
   - Confirm to trigger PRD generation

5. **Monitor progress:**
   - Watch n8n execution logs
   - Query database for status
   - Review expert consultations

### Expert Consultation Sequence

Once requirements are confirmed, the PRD Generator automatically orchestrates:

#### Stage 1: Component Discovery
- Query available OAM ComponentDefinitions
- Build platform capability catalog
- Update shared context

#### Stage 2: Compliance & Risk Assessment
- Identify applicable regulations (GDPR, HIPAA, PCI-DSS, etc.)
- Perform threat modeling (STRIDE)
- Define security controls
- Create risk register
- Update context with compliance requirements

#### Stage 3: Business Architecture
- Design business capability maps
- Create process flows and value streams
- Map to industry standards (BIAN, ACORD, HL7 FHIR)
- Generate ArchiMate models
- Update context with business constraints

#### Stage 4: Experience Design
- Create service blueprints
- Map customer journeys
- Identify friction points
- Define personas and user stories
- Assess accessibility (WCAG 2.1 AA)
- Update context with UX requirements

#### Stage 5: Technology Strategy (CTO)
- Evaluate technology stack options
- Validate against available OAM components
- Make strategic decisions (build vs buy)
- Assess vendor lock-in risks
- Update context with technology decisions

#### Stage 6: Application Architecture
- Design cloud-native microservices
- Define event-driven architecture
- Create data mesh patterns
- Specify API contracts
- Generate Mermaid diagrams
- Update context with architectural patterns

#### Stage 7: Solution Architecture (PRD-to-OAM)
- Generate **two** OAM definitions:
  1. **Standard OAM** - Portable across any OAM runtime
  2. **Platform-specific OAM** - Leverages all available components
- Map functional requirements to components
- Define deployment topology
- Create logical dependency chain

#### Stage 8: Infrastructure Review
- Cost optimization analysis
- Resource right-sizing
- Auto-scaling configuration
- Security validation
- Observability setup
- Iterative refinement until approved

### Monitoring Progress

**Check project status:**

```sql
SELECT * FROM v_project_dashboard ORDER BY created_at DESC;
```

**View expert consultations:**

```sql
SELECT
  ec.expert_name,
  ec.status,
  ec.duration_seconds,
  ec.completed_at
FROM expert_consultations ec
WHERE ec.project_id = 'YOUR_PROJECT_ID'
ORDER BY ec.started_at ASC;
```

**View shared context evolution:**

```sql
SELECT
  version,
  updated_by,
  created_at,
  context_data->'expert_recommendations' as recommendations
FROM shared_context
WHERE project_id = 'YOUR_PROJECT_ID'
ORDER BY version ASC;
```

**View generated PRD:**

```sql
SELECT
  markdown_content
FROM prd_documents
WHERE project_id = 'YOUR_PROJECT_ID'
ORDER BY version DESC
LIMIT 1;
```

**View OAM definitions:**

```sql
SELECT
  definition_type,
  yaml_content,
  review_status
FROM oam_definitions
WHERE project_id = 'YOUR_PROJECT_ID'
ORDER BY created_at DESC;
```

## Database Schema

### Core Tables

- **`e2e_projects`** - Project tracking and status
- **`functional_requirements`** - Requirements from Business Analyst
- **`shared_context`** - Cumulative knowledge across experts (JSONB)
- **`expert_consultations`** - Audit trail of expert work
- **`expert_communications`** - Bidirectional queries between experts
- **`chat_sessions`** - Business Analyst conversation state
- **`oam_definitions`** - Generated OAM YAML files
- **`prd_documents`** - Generated PRD markdown files
- **`oam_component_catalog`** - Available platform components

### Views

- **`v_project_dashboard`** - Real-time project status
- **`v_expert_performance`** - Expert metrics and SLAs
- **`v_requirements_coverage`** - Requirement traceability

## Workflow Details

### Business Analyst Workflow

**Webhook:** `/webhook/chat/business-analyst`

**Responsibilities:**
- Interactive chat interface
- Extract functional requirements from natural language
- Identify non-functional requirements
- Clarify ambiguities
- Validate completeness
- Create project record
- Trigger PRD Generator

**Session State:**
```javascript
{
  step: 0,
  systemBrief: null,
  projectName: null,
  projectType: null,  // mobile/web/backend/fullstack/ml/iot
  platforms: [],      // ['ios', 'android', 'web']
  coreFeatures: [],
  constraints: [],
  nfrs: [],          // Non-functional requirements
  githubRepo: null,
  targetBranch: 'main',
  requirementsComplete: false
}
```

### PRD Generator Orchestrator

**Webhook:** `/webhook/prd-generator`

**Responsibilities:**
- Load project and requirements
- Initialize shared context
- Call experts in sequence
- Merge context updates
- Generate final PRD
- Save PRD and OAM definitions
- Update project status

**Input:**
```json
{
  "projectId": "uuid",
  "projectName": "string",
  "triggeredBy": "business-analyst"
}
```

**Output:**
```json
{
  "success": true,
  "projectId": "uuid",
  "projectName": "string",
  "prdGenerated": true,
  "oamGenerated": true,
  "status": "completed"
}
```

### Expert Workflow Pattern

All expert workflows follow this pattern:

1. **Receive** project ID and shared context
2. **Log** consultation start
3. **Analyze** with LLM using expert-specific prompt
4. **Update** shared context with findings
5. **Save** updated context (new version)
6. **Complete** consultation with audit trail
7. **Return** updated context to orchestrator

**Webhook Pattern:** `/webhook/expert/{expert-name}`

**Input:**
```json
{
  "projectId": "uuid",
  "sharedContext": {},
  "contextVersion": 1
}
```

**Output:**
```json
{
  "success": true,
  "expertName": "string",
  "projectId": "uuid",
  "updatedContext": {},
  "contextVersion": 2,
  "analysis": {},
  "recommendations": []
}
```

## Shared Context Structure

```json
{
  "project_overview": {
    "name": "...",
    "brief": "...",
    "type": "mobile/web/backend",
    "platforms": ["ios", "android"]
  },
  "functional_requirements": [...],
  "non_functional_requirements": [...],
  "constraints": [...],
  "compliance_requirements": [
    "GDPR compliance for EU users",
    "PCI-DSS for payment processing"
  ],
  "business_constraints": [
    "Launch within 6 months",
    "Budget: $500K"
  ],
  "ux_requirements": [
    "Mobile-first design",
    "WCAG 2.1 AA compliance"
  ],
  "technology_decisions": [
    "Use Knative for auto-scaling",
    "PostgreSQL for relational data"
  ],
  "architectural_patterns": [
    "Event-driven architecture",
    "CQRS for read-heavy operations"
  ],
  "infrastructure_constraints": [
    "Max 10 pods per service",
    "Cost target: $200/month"
  ],
  "identified_risks": [
    {
      "description": "API rate limiting",
      "severity": "medium",
      "mitigation": "Implement caching layer"
    }
  ],
  "key_assumptions": [
    "Users have stable internet connection",
    "Peak load: 10K concurrent users"
  ],
  "expert_recommendations": {
    "compliance_risk_assessor": "...",
    "business_architect": "...",
    ...
  },
  "decision_rationale": {
    "database_choice": "PostgreSQL chosen for ACID compliance",
    ...
  },
  "platform_capabilities": {
    "available_components": [...],
    "foundational": [...],
    "compositional": [...],
    "infrastructural": [...]
  }
}
```

## Extending the Platform

### Adding New Experts

1. Create new workflow JSON following expert pattern
2. Add expert name to `expert_consultations.expert_name` constraint
3. Define LLM prompt with expert knowledge
4. Specify context updates and outputs
5. Add to PRD Generator orchestrator sequence

### Customizing LLM Prompts

Edit the "LLM - Analysis" node in each expert workflow:

```json
{
  "system": "You are a [EXPERT ROLE] with expertise in...",
  "temperature": 0.2,  // Lower = more consistent
  "model": "qwen2.5:7b-instruct-q4_K_M"  // or upgrade to 32b
}
```

### Adding New Project Types

Update Business Analyst workflow session state:

```javascript
projectType: 'mobile' | 'web' | 'backend' | 'fullstack' | 'ml' | 'iot' | 'YOUR_TYPE'
```

Update database constraint:

```sql
ALTER TABLE e2e_projects DROP CONSTRAINT IF EXISTS e2e_projects_project_type_check;
ALTER TABLE e2e_projects ADD CONSTRAINT e2e_projects_project_type_check
  CHECK (project_type IN ('mobile', 'web', 'backend', 'fullstack', 'ml', 'iot', 'YOUR_TYPE'));
```

## Integration with Existing Migration Platform

This E2E platform is designed to integrate with the existing white-label migration platform:

### Shared Database

Both platforms use the same PostgreSQL instance, with separate table namespaces:
- **Migration Platform:** `migrations`, `approval_gates`
- **E2E Platform:** `e2e_projects`, `functional_requirements`, `shared_context`, etc.

### Intent Routing

Update the intent router in the migration platform to detect E2E intent:

```javascript
// In 0-configuration-assistant-intent-router.json
{
  "intent": "e2e_solution",
  "confidence": 0.9,
  "route": "/webhook/chat/business-analyst"  // Routes to E2E platform
}
```

### Naming Conventions

To avoid conflicts with migration platform workflows:
- Prefix E2E workflows with numbers: `0-`, `1-`, `2-`, etc.
- Use descriptive names: `business-analyst-e2e`, `prd-generator-orchestrator`
- Expert webhooks: `/webhook/expert/{name}` vs migration: `/webhook/agent/{name}`

## Troubleshooting

### Chat Interface Not Connecting

**Symptoms:** "Error connecting to Business Analyst workflow"

**Solutions:**
1. Verify n8n is running: `docker ps | grep n8n`
2. Check workflow is active in n8n UI
3. Verify PostgreSQL credentials configured
4. Update `N8N_URL` in chat HTML if n8n is not on localhost:8001
5. Serve HTML via HTTP, not file:// protocol

### LLM Errors

**Symptoms:** 500 errors or timeout

**Solutions:**
1. Verify Ollama running: `curl http://ollama:11434/api/tags`
2. Verify OpenWebUI: `curl http://open-webui:8080/api/health`
3. Check model pulled: `docker exec ollama ollama list`
4. Pull model if missing: `docker exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M`
5. Increase timeout in HTTP Request nodes

### Database Connection Errors

**Solutions:**
1. Test connection: `docker exec -it db psql -U postgres -d postgres -c "SELECT 1"`
2. Verify schema created: `docker exec -it db psql -U postgres -d postgres -c "\dt e2e_*"`
3. Check credentials match in n8n
4. Ensure database has capacity

### Expert Workflow Not Updating Context

**Symptoms:** Context version doesn't increment

**Solutions:**
1. Check expert workflow execution logs
2. Verify shared context table has records
3. Ensure JSON parsing succeeds in "Update Shared Context" node
4. Check for PostgreSQL errors in logs

### PRD Generator Not Triggering

**Symptoms:** Requirements complete but no PRD generated

**Solutions:**
1. Check Business Analyst workflow triggered PRD Generator
2. Verify webhook URL correct: `http://n8n:5678/webhook/prd-generator`
3. Check PRD Generator workflow is active
4. Review n8n execution logs for errors

## Model Upgrades

For better quality, upgrade to larger models:

### Upgrade to Qwen 2.5 Coder 32B

```bash
# Pull model
docker exec ollama ollama pull qwen2.5-coder:32b

# Update workflows: Replace in all HTTP Request nodes
# "model": "qwen2.5-coder:32b"
```

### Adjust Temperature

- **Lower (0.1-0.3):** More deterministic, consistent outputs (compliance, technical specs)
- **Higher (0.6-0.9):** More creative (UX design, brainstorming)

## Production Considerations

### Performance

- **Parallel Expert Consultations:** Modify orchestrator to call non-dependent experts in parallel (Business Architect + Experience Designer)
- **Caching:** Cache LLM responses for repeated queries
- **Database Indexing:** Already optimized with indexes on project_id, created_at

### Security

- **Authentication:** Add API key validation to webhooks
- **RBAC:** Implement role-based access to projects
- **Encryption:** Encrypt sensitive data in shared context (PII, credentials)
- **Audit:** All consultations logged with timestamps

### Scalability

- **Connection Pooling:** Configure PostgreSQL connection pooling
- **Queue Management:** Use n8n execution queue for high concurrency
- **Model Scaling:** Deploy multiple Ollama instances with load balancing

## Related Documentation

- **/.claude/agents/README.md** - Original Claude Code agent architecture
- **/Users/socrateshlapolosa/Development/local-ai-packaged/n8n-workflows-start-here/README.md** - Migration platform documentation
- **CLAUDE.md** - Development methodology
- **REALTIME_SYSTEM.md** - Real-time system design

## Support

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

**Generated by:** E2E Solution Development Platform
**Platform Version:** Health Service IDP v1.1
**OAM Specification:** core.oam.dev/v1beta1
**Last Updated:** 2025-01-27
