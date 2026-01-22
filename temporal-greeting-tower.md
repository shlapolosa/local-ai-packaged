# End-to-End Software Delivery Pipeline Analysis & Improvements

## Current Workflow Architecture

### Flow Overview
```
Knowledge Loader (periodic/on-demand - per role context)
         ↓ (loaded into Qdrant, referenced by agents)

Architecture Pipeline Ack (entry point)
         ↓
Architecture Pipeline - AI Agent with Ollama (main processing)
         ↓
Architecture Artifact Get v2 (status/artifact checking)
         ↓
Software Delivery Pipeline (GitHub + Taskmaster) [MANUAL TRIGGER - GAP]
         ↓
OpenCode (development) [FUTURE]
```

### Knowledge Loading (Separate from Main Flow)
- **Periodic/On-demand** - NOT triggered every pipeline run
- **Per-role context** - Business Analyst, Enterprise Architect, Solution Architect, etc.
- **Externalized** - Users can load context via webhook or manual trigger
- **Stored in Qdrant** - Referenced by AI agents during Architecture Pipeline

---

## Workflow Analysis

### 1. Knowledge Loader - All Collections (`hW4tlUp7CC0BItkN`)
**Status:** Inactive
**Purpose:** Load context into Qdrant vector store for AI agents

**Flow:**
- Manual Trigger → Read Config → Parse Collections → Loop Collections → Call Knowledge Loader → Aggregate Results → Build Summary

**Issue:** Workflow is inactive and only has manual trigger

---

### 2. Architecture Pipeline Ack (`RlBWh7XL9ZXgOJ7e`)
**Status:** Active
**Purpose:** Entry point that acknowledges request and triggers main pipeline

**Flow:**
- Webhook → Prepare Job → Trigger Pipeline (HTTP) → Respond Ack

**Works correctly** - Immediately returns acknowledgment while triggering async pipeline

---

### 3. Architecture Pipeline - AI Agent with Ollama (`iKBlJTWf5HPkKAVX`)
**Status:** Active (100 nodes)
**Purpose:** Main architecture generation pipeline

**Flow:**
1. Webhook Trigger → Initialize Parameters → **Respond Ack** (immediate)
2. Run Config → Classify Intent (Ollama) → Apply Classification + Slugify
3. Ensure DB Schema → Pass Context → Upsert Project → Load Latest BRD
4. BRD Generation/Validation → Store BRD Artifact
5. Qdrant Search (Capabilities) → Select Relevant Capabilities
6. **Business Architecture** → Validate → Store → ArchiMate XML
7. **Application Architecture** → Validate → Store → Combined XML
8. **Data Architecture** → Validate → Store → Combined XML
9. **Infrastructure Architecture** → Validate → Store → Full XML
10. **Risk Assessment** → Validate → Store
11. **Solution Package** → Validate → Store
12. **QA Package** → Validate → Store
13. **PRD (RPG Template)** → Validate → Store

**GAP:** Pipeline ends after storing PRD - does NOT trigger Software Delivery Pipeline

---

### 4. Architecture Artifact Get v2 (`7IUOzaD9TUwXP2Qw`)
**Status:** Active
**Purpose:** Check status and retrieve artifacts during/after pipeline

**Flow:**
- Webhook → Mode Router → Fetch Artifact OR List Artifacts → Format Response

**Works correctly**

---

### 5. Software Delivery Pipeline (`RxOksieHq60Si7A5`)
**Status:** Active
**Purpose:** Publish artifacts to GitHub and run TaskMaster

**Flow:**
1. Webhook → Parse Input → Resolve Project (jobId) → Fetch Artifacts (jobId)
2. Collect Artifacts (validates: prd_md, brd, archimate_xml_business_application_data_infra)
3. Render BRD.md → Build Git SSH Script → SSH: Checkout + Write + Commit
4. Build Taskmaster SSH Script → SSH: Taskmaster Init/Parse/Expand/Stories
5. Respond

**Issues Found:**
- Currently commits `.taskmaster` folder (should be excluded)
- Manual trigger only (should be auto-triggered by Architecture Pipeline)

---

## Identified Gaps & Improvements

### Critical Issues

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 1 | `.taskmaster` committed to git | Noise in repo, large commits | Remove from git add |
| 2 | No auto-trigger from Architecture Pipeline | Manual intervention required | Add HTTP trigger at end of Architecture Pipeline |
| 3 | Knowledge Loader inactive | Context not loaded for agents | Activate and add webhook trigger |

### Recommended Improvements

| # | Improvement | Benefit |
|---|-------------|---------|
| 4 | Add completion callback/webhook to Architecture Pipeline | Notify external systems when done |
| 5 | Add error handling path in Software Delivery | Graceful failure reporting |
| 6 | Add option for manual vs auto trigger on Software Delivery | Flexibility for different use cases |

---

## Implementation Plan

### Phase 1: Fix .taskmaster Exclusion (Required)

**File:** Software Delivery Pipeline - "Build Taskmaster SSH Script" node

**Change:** Remove `.taskmaster` from git add command

```diff
- git add '{projectSlug}-docs/backlog/tasks.json' '{projectSlug}-docs/backlog/stories.json' '{projectSlug}-docs/.taskmaster' || true
+ git add '{projectSlug}-docs/backlog/tasks.json' '{projectSlug}-docs/backlog/stories.json' || true
```

### Phase 2: Auto-Trigger Software Delivery (Recommended)

**File:** Architecture Pipeline - Add node after "Store PRD Artifact"

**New Node:** HTTP Request to trigger Software Delivery webhook

```javascript
// After Store PRD Artifact, add:
POST /webhook/software-delivery
Body: { "jobId": "{{ $json.jobId }}" }
```

**Alternative:** Add switch node allowing user to choose:
- `autoTriggerDelivery: true/false` in initial request

### Phase 3: Knowledge Loader (Already Externalized - Verify)

**Current State:**
- Knowledge Loader - Generic (`BlN67oV6QwF2hzgb`) has webhook trigger
- Knowledge Loader - All Collections (`hW4tlUp7CC0BItkN`) loops through collections

**Verify:**
1. Confirm webhook endpoint is accessible: `POST /webhook/knowledge-loader`
2. Confirm config file defines per-role collections (BA, EA, SA, etc.)
3. Confirm periodic loading schedule if needed (cron trigger)

**No changes needed** if already externalized - just verify it works

---

## Files to Modify

1. **Software Delivery Pipeline** (`RxOksieHq60Si7A5`)
   - Node: "Build Taskmaster SSH Script"
   - Change: Remove `.taskmaster` from git add

2. **Architecture Pipeline** (`iKBlJTWf5HPkKAVX`) [Optional]
   - Add: HTTP Request node after "Store PRD Artifact"
   - Purpose: Auto-trigger Software Delivery Pipeline

3. **Knowledge Loader - All Collections** (`hW4tlUp7CC0BItkN`) [Optional]
   - Change: Activate workflow
   - Add: Webhook trigger

---

## What Gets Committed to Git

### Commit 1: Build Git SSH Script (Artifacts)
**Branch:** `{projectSlug}`
**Files:**
```
software-delivery/
├── org-architecture/
│   └── full.archimate              # Combined ArchiMate XML (all layers)
│
└── {projectSlug}-docs/
    ├── docs/
    │   ├── BRD.md                  # Business Requirements Document
    │   ├── PRD.md                  # Product Requirements Document
    │   ├── risk-assessment.md      # (if generated)
    │   ├── solution-architecture.md # (if generated)
    │   ├── test-strategy.md        # (if generated)
    │   └── test-scenarios.md       # (if generated)
    │
    ├── architecture/
    │   ├── business.archimate      # (if exists) Business layer only
    │   ├── application.archimate   # (if exists) App layer only
    │   ├── data.archimate          # (if exists) Data layer only
    │   ├── technology.archimate    # Full XML copy
    │   └── full.archimate          # Combined all layers
    │
    ├── api/
    │   ├── openapi.yaml            # (if generated) REST API spec
    │   ├── asyncapi.yaml           # (if generated) Event API spec
    │   ├── cloudevents.md          # (if generated) Event schemas
    │   └── avro-schemas.json       # (if generated) Avro schemas
    │
    └── db/
        └── schema.sql              # (if generated) Database schema
```

### Commit 2: Build Taskmaster SSH Script (Backlog)
**Branch:** `{projectSlug}`
**Files (CURRENT - includes .taskmaster):**
```
{projectSlug}-docs/
├── backlog/
│   ├── tasks.json                  # TaskMaster tasks
│   └── stories.json                # Stories with story points
│
└── .taskmaster/                    # CURRENTLY COMMITTED - SHOULD EXCLUDE
    ├── tasks/
    │   └── tasks.json
    ├── reports/
    │   └── task-complexity-report.json
    └── config.json
```

**Files (AFTER FIX - excludes .taskmaster):**
```
{projectSlug}-docs/
└── backlog/
    ├── tasks.json                  # TaskMaster tasks
    └── stories.json                # Stories with story points
```

---

## Verification Steps

After implementation:

1. **Test .taskmaster exclusion:**
   ```bash
   # After running Software Delivery Pipeline
   cd /opt/workspace/software-delivery
   git log --name-only -1
   # Should NOT show .taskmaster files
   ```

2. **Test auto-trigger (if implemented):**
   ```bash
   curl -X POST https://n8n.socrates-hlapolosa.org/webhook/architecture-pipeline-ack \
     -H "Content-Type: application/json" \
     -d '{"requirements": "test project"}'
   # Should trigger both Architecture and Software Delivery pipelines
   ```

3. **Verify outputs:**
   ```bash
   ls /local-ai-packaged/projects/software-delivery/{projectSlug}-docs/backlog/
   # Should contain: tasks.json, stories.json (NOT .taskmaster/)
   ```

---

## Summary

The current implementation is functional but has these gaps:

| Priority | Issue | Action |
|----------|-------|--------|
| **P1** | `.taskmaster` folder committed to git | Remove from git add in Taskmaster script |
| **P2** | Manual trigger between Architecture → Software Delivery | Add auto-trigger with manual option |
| **P3** | Knowledge Loader verification | Verify externalized loading works (likely already OK) |

### Recommended Implementation Order:
1. **Phase 1** (Required): Fix `.taskmaster` exclusion - simple change
2. **Phase 2** (Recommended): Add auto-trigger with option for manual override
3. **Phase 3** (Verify only): Confirm Knowledge Loader is accessible externally

### What OpenCode Will Receive:
After Software Delivery Pipeline completes, the git branch `{projectSlug}` will contain:
- **docs/** - BRD.md, PRD.md, and other documentation
- **architecture/** - ArchiMate XML files for all layers
- **api/** - OpenAPI, AsyncAPI, CloudEvents specs (if generated)
- **db/** - SQL schema (if generated)
- **backlog/** - tasks.json and stories.json for development planning

OpenCode can then clone the branch and start implementation using the tasks/stories as guidance.
