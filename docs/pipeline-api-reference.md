# Architecture Pipeline API Reference

## Endpoint

```
POST /webhook/architecture-pipeline-ack
```

## Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `requirements` | string | **Yes** | - | The business requirements text to process |
| `text` | string | No | - | Alias for `requirements` (either works) |
| `projectName` | string | No | `"architecture-project"` | Human-readable project name |
| `startAt` | string | No | `""` (empty) | Stage to start from (for resuming/skipping) |

### `startAt` Parameter Values

Use `startAt` to resume from a specific stage (skipping earlier stages):

| Value | Starts From | Skips |
|-------|-------------|-------|
| `""` (empty) | Beginning | Nothing - runs all stages |
| `"business_analyst"` | BRD Generation | Nothing |
| `"application_architect"` | Application Architecture | BRD, Business Arch |
| `"data_architect"` | Data Architecture | BRD, Business, App Arch |
| `"infrastructure_architect"` | Infrastructure Architecture | BRD, Business, App, Data Arch |

## Example Requests

### Full Pipeline (Recommended)

```bash
curl -X POST https://n8n.your-domain.org/webhook/architecture-pipeline-ack \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Build a task management API with CRUD operations and JWT authentication.",
    "projectName": "Task Management API"
  }'
```

### Resume from Application Architecture

```bash
curl -X POST https://n8n.your-domain.org/webhook/architecture-pipeline-ack \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Build a task management API with CRUD operations and JWT authentication.",
    "projectName": "Task Management API",
    "startAt": "application_architect"
  }'
```

## Response

```json
{
  "status": "accepted",
  "jobId": "job_20260120-130959_06e630e8",
  "projectSlug": "task-management-api",
  "pipeline": {
    "executionId": "1236563"
  },
  "artifactQuery": {
    "byJobIdInfra": "/webhook/architecture-artifact-v2?jobId=...&type=infrastructure_arch",
    "byJobIdCombinedXml": "/webhook/architecture-artifact-v2?jobId=...&type=archimate_xml_business_application_data_infra"
  }
}
```

## Pipeline Stages

```
1. Intent Classification
2. BRD Generation (Business Requirements Document)
3. Business Architecture + ArchiMate XML
4. Application Architecture + Combined XML
5. Data Architecture + Combined XML
6. Infrastructure Architecture + Full XML
7. Risk Assessment
8. Solution Architecture
9. QA Package (Test Strategy + Scenarios)
10. PRD Generation (Product Requirements Document)
11. [Auto-trigger] Software Delivery Pipeline
```

## Changelog

### 2026-01-20: Routing Logic Fix (v2)

**Issue:** Pipeline stopped after Business Architecture regardless of `startAt` value.

**Root Cause:** The stage routing nodes (After Business/App/Data Stage) were checking `startAt` to decide whether to continue. This was incorrect - `startAt` is only for determining where to START, not where to STOP. Once started, the pipeline should always run to completion.

**Fix Applied:** Updated all three routing conditions to always continue:
```javascript
true  // Always continue to next stage
```

**Behavior:**
- `startAt` determines which stage to begin from (skips earlier stages)
- Once started, pipeline runs through ALL subsequent stages to completion
- No early stopping - full pipeline execution from start point

**Affected Nodes:**
- After Business Stage → Always continues to Application Architecture
- After App Stage → Always continues to Data Architecture
- After Data Stage → Always continues to Infrastructure Architecture
