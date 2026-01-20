# Overview
Architecture Pipeline Pattern (APP) v1 is a deterministic, schema-validated, stateful architecture generation workflow implemented in n8n. It converts free-text project requests and updates into consistent architecture artifacts (starting with Business Analyst outputs and Business Architecture), persists them in Supabase Postgres under a dedicated `architecture` schema, and renders downstream formats (initially deterministic ArchiMate XML). The workflow solves the current problems of inconsistent LLM outputs, malformed/partial JSON leading to incorrect ArchiMate files, hardcoded/biased retrieval prompts causing irrelevant capabilities (e.g., medication formulary for a wearable telemetry app), and lack of state/context when starting mid-pipeline.

The product is for enterprise architects, business analysts, and solution teams who want repeatable architecture artifacts from natural language, with a workflow that can be extended to additional architect roles (application/data/infrastructure) without re-architecting the pipeline. The value is reliability: deterministic generation, strict validation with repair loops, auditability via persisted versions/hashes, and a standard stage contract enabling safe expansion.

# Core Features

## 1) Standardized Request Contract + Webhook Entry
- What it does
  - Defines a stable webhook input shape for all requests and updates.
- Why it's important
  - Eliminates ad-hoc payloads and makes routing + persistence + stage execution predictable.
- How it works at a high level
  - Webhook accepts JSON:
    - `text` (required): problem statement or update instruction
    - `projectName` (optional): human-readable name
    - `startAt` (optional): stage name; if omitted starts from beginning

## 2) Deterministic Intent Classification and Stage Routing
- What it does
  - Determines whether the request is a new project or an update and selects the stage to start at.
- Why it's important
  - Ensures consistent routing and supports "run from requested stage downwards".
- How it works at a high level
  - Uses Llama via direct Ollama HTTP call with structured output schema to produce:
    - `intent` (create/update/etc.)
    - `startAt` (if not provided)
    - `proposedProjectName` (if missing)
    - `confidence`
  - A deterministic code-based slugifier generates `projectSlug`.
  - Project is auto-created in Supabase if it does not exist.
  - Stage router executes from `startAt` down the dependency chain.

## 3) Stateful Context Resolver (Start Mid-Pipeline Safely)
- What it does
  - When starting at a non-initial stage, loads prerequisite artifacts from the database instead of relying on inline context passing.
- Why it's important
  - Prevents "corrupted" runs where a stage executes without required upstream context.
- How it works at a high level
  - Each stage declares prerequisites (e.g., Business Architect requires latest BRD).
  - Resolver queries latest artifact versions from Supabase.
  - If prerequisite missing, automatically runs prerequisite stage(s) first.

## 4) Knowledge Binding via `shared/` Configuration (Dynamic Retrieval)
- What it does
  - Selects which Qdrant collections to query for a given architect role based on `shared/knowledge/knowledge-config.json`.
- Why it's important
  - Removes hardcoded retrieval prompts/collections and makes the workflow extensible to new architect roles.
  - Allows knowledge artifacts to change over time without rewiring the workflow.
- How it works at a high level
  - Workflow reads `/data/shared/knowledge/knowledge-config.json` each run.
  - It maps the stage "consumer role" to a set of Qdrant collections.
  - Retrieval queries only those collections; results are sorted deterministically.
  - Knowledge config version and collections used are recorded in artifact metadata.

## 5) Capability Relevance Gate (Prevents Irrelevant Capabilities)
- What it does
  - Filters retrieved capabilities to only those relevant to the current project, preventing domain bleed (e.g., medication formulary for wearables telemetry).
- Why it's important
  - Reduces hallucination and cross-domain contamination, improving accuracy downstream.
- How it works at a high level
  - Step 1: Qdrant returns candidate capability snippets (larger topK, e.g. 40).
  - Step 2: Llama "Capability Selector" (structured output) returns `selectedCapabilities[]` with `relevanceScore` and reasons.
  - Step 3: Workflow filters by score threshold and passes only selected capabilities into the Business Architect stage.

## 6) Llama-only Generation via Direct Ollama HTTP (No Agent Nodes)
- What it does
  - Replaces n8n "agent" nodes with explicit HTTP calls to Ollama to reduce overhead and variability.
- Why it's important
  - Agent nodes can add hidden prompt overhead and output artifacts; direct calls improve repeatability.
- How it works at a high level
  - Use `POST https://ollama.socrates-hlapolosa.org/api/chat`
  - Model: `llama3.1:8b-instruct-q4_K_M` only
  - Deterministic settings stored at workflow level:
    - `temperature: 0`
    - `seed: fixed integer (e.g., 42)`
  - All model outputs use `format` with JSON Schema for structure enforcement.

## 7) Schema Validation + Repair Loop (No Malformed JSON Downstream)
- What it does
  - Validates every LLM artifact against JSON Schema and semantic rules; repairs or fails hard before conversion.
- Why it's important
  - Prevents malformed JSON from producing incorrect ArchiMate files.
  - Ensures the "key is validity" rather than enforcing fixed element counts.
- How it works at a high level
  - Parse JSON output.
  - Validate via Ajv (JSON Schema).
  - Apply semantic validators (relationship references exist; no duplicate ids; allowed enums).
  - If invalid:
    - Call Llama again with the invalid output + validation errors
    - Enforce schema again via `format`
    - Retry max N times (e.g., 2) then fail with diagnostics.

## 8) Deterministic ArchiMate XML Rendering
- What it does
  - Converts validated architecture JSON into ArchiMate XML in a deterministic way (same inputs -> same outputs).
- Why it's important
  - Eliminates run-to-run drift caused by timestamps/random IDs.
- How it works at a high level
  - Generate stable IDs from hashes of stable fields (projectSlug + artifactType + element.id).
  - Sort elements and relationships deterministically before rendering.
  - Store XML as an artifact and return it in webhook response.

## 9) Artifact Persistence and Versioning in Supabase (Audit + Reproducibility)
- What it does
  - Stores all artifacts (BRD, capability selection, business architecture, ArchiMate XML) with versions and hashes.
- Why it's important
  - Enables update routing, rollback, audit, and deterministic rebuilds.
- How it works at a high level
  - DB schema `architecture` includes `projects` and `artifacts`.
  - Each artifact write increments version per project+type.
  - Store `content_hash`, model settings, and knowledge config version in metadata.

# User Experience

## User Personas
- Business Analyst (BA)
  - Wants consistent BRDs and stakeholder/requirements extraction from text.
- Business Architect
  - Wants capability-aligned business architecture with traceable rationale and valid ArchiMate export.
- Enterprise/Solution Architect (future)
  - Wants to add application/data/infra architecture stages without redoing the pipeline.
- Delivery Team / Developers
  - Want machine-readable outputs (JSON/ArchiMate) to build from, and confidence that results are repeatable.

## Key User Flows

### Flow A: Create New Project (Default)
1) User POSTs:
   - `{ "text": "...", "projectName": "Optional" }`
2) Workflow:
   - classifies intent -> creates project -> runs BA -> retrieves+selects capabilities -> runs Business Architect -> validates -> renders XML -> persists all artifacts
3) Response:
   - `projectSlug`, current artifact versions/ids, BRD JSON, business arch JSON, ArchiMate XML, validation status

### Flow B: Update Existing Project Starting Midstream
1) User POSTs:
   - `{ "text": "Update business architecture to include ...", "projectName": "...", "startAt": "business_architect" }`
2) Workflow:
   - resolves project -> loads latest BRD from DB -> computes change summary/diff -> re-selects capabilities -> regenerates business architecture from scratch -> validates -> renders XML -> persists new versions
3) Response:
   - includes which prerequisites were loaded, what changed, new artifact versions/hashes

### Flow C: Update Without `startAt`
1) User omits `startAt`, workflow either:
   - starts from BA (default), or
   - classifier sets `startAt` if explicit in text (optional enhancement)
2) Runs from start and regenerates downstream.

## UI/UX Considerations
- This is an API-first workflow; "UX" is response structure and observability.
- Response must always include:
  - `validation` results and explicit failure reasons if invalid
  - artifact references (ids, version numbers, hashes)
  - knowledge version used (for reproducibility)
- Fail fast on invalid JSON or schema violations; don't silently return "completed" with broken outputs.
- Provide stable, predictable response shape so clients (Open WebUI, Flowise, scripts) can integrate.

<PRD>
# Technical Architecture

## System Components

### 1) n8n Workflow: `iKBlJTWf5HPkKAVX` (Refactor In Place)
Major changes:
- Replace agent nodes with HTTP Request nodes to Ollama.
- Add intent classifier + router + project persistence.
- Replace hardcoded Qdrant prompt with dynamic retrieval based on project text/BRD and `shared/knowledge/knowledge-config.json`.
- Add schema validation + repair loops.
- Replace ArchiMate XML generation with deterministic logic.

### 2) Ollama (External HTTPS Endpoint)
- Endpoint: `https://ollama.socrates-hlapolosa.org/api/chat`
- Model: `llama3.1:8b-instruct-q4_K_M`
- Workflow-level options:
  - `temperature: 0`
  - `seed: 42` (fixed; stored in workflow config node)
  - consistent other sampling params (either omit or keep fixed)

Structured outputs:
- Use Ollama `format` field to enforce JSON schemas for classifier and artifact generation.

### 3) Qdrant (Knowledge Retrieval)
- Use collections defined in `shared/knowledge/knowledge-config.json`.
- For business-architect stage, default collections:
  - `capability-maps`
  - `existing-landscape`
- Retrieval behavior:
  - `topK` increase from 6 to ~40 (configurable workflow-level)
  - deterministic sorting of results before Llama selection

### 4) Supabase Postgres (State Store)
- Use Postgres node with:
  - host `db`
  - port `5432`
  - database `postgres`
  - user `postgres`
  - password from `.env` (`POSTGRES_PASSWORD`)
- Create and use schema: `architecture`

### 5) Shared Knowledge and Scripts (`shared/`)
Mount already exists: `./shared` -> `/data/shared` in n8n container.

Files leveraged:
- `/data/shared/knowledge/knowledge-config.json` (collection mapping + version)
- Knowledge folders:
  - `/data/shared/knowledge/capability-maps/...`
  - `/data/shared/knowledge/existing-landscape/...` etc.

Design requirement:
- Workflow reads config each run so changes to knowledge are automatically reflected.
- Workflow records config version and collections used in artifact metadata.

## Data Models (Supabase Postgres)

### Schema: `architecture`

#### Table: `projects`
- `id uuid primary key default gen_random_uuid()`
- `slug text unique not null`
- `name text`
- `created_at timestamptz default now()`
- `updated_at timestamptz default now()`

#### Table: `artifacts`
- `id uuid primary key default gen_random_uuid()`
- `project_id uuid not null references architecture.projects(id)`
- `type text not null` (enum-like via convention)
- `version int not null`
- `content jsonb not null`
- `content_hash text not null`
- `meta jsonb not null default '{}'::jsonb`
- `created_at timestamptz default now()`

Artifact `type` values for MVP:
- `request_brief` (structured interpretation of request text)
- `brd`
- `capability_candidates` (optional, for audit)
- `capability_selection`
- `business_arch`
- `archimate_xml` (store in `content` as `{ xml: "<...>" }`)

Indexes:
- `(project_id, type, version desc)`
- unique constraint suggestion: `(project_id, type, version)`.

## APIs and Integrations

### Webhook API (n8n)
- Endpoint: existing workflow webhook path (`/webhook/architecture-pipeline`)
- Input:
  - `{ "text": string, "projectName"?: string, "startAt"?: string }`
- Output (standardized):
  - `projectSlug`
  - `intent`, `startAtEffective`
  - artifact references: ids, versions, hashes
  - `brd`, `businessArchitecture` (JSON objects or JSON strings; choose one standard)
  - `archimateXml` string
  - `validation`: per artifact
  - `knowledge`: config version + collections used

### Ollama Integration
HTTP Request payload pattern (per call):
- `model`: `llama3.1:8b-instruct-q4_K_M`
- `messages`: system + user (keep prompts minimal, explicit)
- `options`: `{ temperature: 0, seed: 42 }`
- `format`: JSON Schema (varies by step)

### Qdrant Integration
- Query prompt must be derived from:
  - request.text
  - and/or BRD executive summary if available
- Must not hardcode "patient appointment booking".
- topK configurable.

## Infrastructure Requirements
- n8n container must have access to:
  - Supabase Postgres host `db`
  - Qdrant host `qdrant`
  - shared volume at `/data/shared`
  - external Ollama endpoint (HTTPS)
- Ensure n8n has network egress to `ollama.socrates-hlapolosa.org`.
- Ensure Postgres has pgcrypto extension if using `gen_random_uuid()` (or use UUID generation in n8n and store explicitly).

# Development Roadmap

## Phase 1 (MVP): Deterministic BA + Business Architect Pipeline
Scope: make the workflow usable and reliable end-to-end for two roles.

1) Webhook input standardization
- Update webhook handler to accept `{text, projectName?, startAt?}` only.
- Backward compatibility optional (if needed, map old `requirements` to `text`).

2) Workflow-level configuration node
- Define constants:
  - model, temperature, seed, maxRetries, qdrantTopK, relevanceThreshold
- Keep in one Set node at the top so later stages reuse it.

3) Intent classifier (Llama structured output)
- Implement HTTP->Ollama classifier with schema enforcing:
  - intent enum, startAt enum, proposedProjectName, confidence
- Deterministic code-based slugify from chosen name.

4) Project upsert/load in Supabase Postgres
- Upsert `architecture.projects` by slug (auto-create).
- Load latest artifacts per type for context.

5) Request brief artifact + diff
- Generate `request_brief` (structured) from request.text (Llama schema).
- Persist as artifact.
- If previous exists, compute JSON diff and store `change_summary` in meta (or as separate artifact type).

6) Business Analyst stage (BRD)
- Generate BRD via HTTP->Ollama with JSON Schema enforcement.
- Validate with Ajv + semantic checks (e.g. minimum stakeholder count if desired).
- Repair loop on failure.
- Persist `brd` artifact.

7) Knowledge binding + capability retrieval for Business Architect
- Read `knowledge-config.json` from shared folder.
- Determine collections for `business-architect`.
- Query Qdrant candidates (topK ~40 per collection).
- Persist `capability_candidates` optionally.

8) Capability selector gate (Llama structured output)
- Select only relevant capabilities for the project.
- Persist `capability_selection`.

9) Business Architect stage (business architecture JSON)
- Generate from scratch using:
  - latest BRD
  - capability_selection
  - request_brief + change summary
- Enforce schema (no fixed element count).
- Validate + semantic checks + repair loop.
- Persist `business_arch`.

10) Deterministic ArchiMate XML renderer
- Replace current random-id generator with deterministic hashing + sorting.
- Persist `archimate_xml` artifact.

11) Response payload standardization
- Return projectSlug + latest artifacts + validation status + deterministic xml.

## Phase 2: Pattern Hardening + Observability
Scope: make it robust for scale and easier debugging.

1) Strict error handling and failure modes
- If repair loop fails: workflow returns `status: failed` with detailed validation errors.
- Ensure no XML rendering runs when JSON invalid.

2) Knowledge provenance and repeatability
- Record:
  - knowledge-config version
  - collections queried
  - candidate counts, selected counts
  - retrieval scores distribution

3) Deterministic retrieval ordering
- Explicitly sort Qdrant results by `score desc`, then `id/path`.

4) Artifact hash-based deduplication (optional)
- If generated artifact hash equals latest stored hash, do not create new version (or create version but mark unchanged).

## Phase 3: Extendable Role Framework (Application/Data/Infra Ready)
Scope: enable adding new architect roles with minimal workflow rewiring.

1) Stage registry abstraction (in-workflow)
- Define a stage registry object:
  - stage name
  - prerequisites
  - consumer role string for knowledge binding
  - schema references
  - renderer(s)
- Implement generic "execute stage" pattern in nodes.

2) Add first additional role skeletons (no full generation yet)
- Stub nodes for application architect and data architect that:
  - resolve prerequisites
  - retrieve mapped knowledge collections
  - placeholder generation disabled
This validates extensibility without expanding scope too far.

3) Renderer framework
- Add additional renderers as optional outputs:
  - Markdown summary (using existing shared scripts as reference)
  - OpenAPI draft (later)
  - presentation outline JSON (later)

# Logical Dependency Chain

## Foundation (must build first)
1) Webhook contract standardization
2) Workflow-level deterministic config node (model/seed/temperature/retries)
3) Supabase schema + tables (`architecture.projects`, `architecture.artifacts`)
4) Project resolver (slugify + upsert + load)
5) Request brief generation + persistence (enables diff + context)

## MVP Usable/Visible Output (fastest to "working")
6) Business Analyst BRD generation + validation + persistence
7) Business Architect capability retrieval (dynamic via knowledge-config) + selector gate
8) Business Architecture generation + validation + persistence
9) Deterministic ArchiMate XML rendering + response

This delivers a visible output: a downloadable/importable `.archimate` XML and structured JSON artifacts.

## Build-upon Improvements (atomic enhancements)
10) Diff-based change summary and explicit "what changed" injected into prompts
11) Improved semantic validators (capability subset, relationship constraints)
12) Enhanced knowledge provenance in artifact metadata

# Risks and Mitigations

## Technical challenges
- Risk: Ajv not available in n8n Code node runtime
  - Mitigation: verify availability; if unavailable, use JSON schema validation via a lightweight custom validator or install allowed modules (prefer Ajv if present).
- Risk: Ollama structured output `format` behavior differs by version
  - Mitigation: keep validation/repair loop regardless; treat `format` as best-effort but not sole guard.
- Risk: External Ollama endpoint variability/latency
  - Mitigation: retries with backoff for HTTP; timeouts; log failed calls; optionally allow internal `ollama:11434` fallback later.
- Risk: Qdrant corpus mismatch (capability map doesn't contain consumer app/wearables capabilities)
  - Mitigation: selection gate prevents wrong picks, but may yield sparse results; expand/curate capability documents over time in `shared/knowledge/capability-maps/`.

## MVP definition risk
- Risk: Over-building framework before producing value
  - Mitigation: MVP includes only BA + Business Architect + ArchiMate XML output, but uses the general stage pattern so additional roles are additive.

## Resource constraints
- Risk: Workflow complexity increases debugging cost
  - Mitigation: persist intermediate artifacts (`request_brief`, `capability_candidates`, `capability_selection`) for audit; strict structured response with validation outputs.

# Appendix

## Research Findings / Observations from Current System
- Current workflow retrieval prompt is hardcoded to appointment booking, causing irrelevant capability context.
- Current outputs can be well-formed JSON but structurally inaccurate (missing elements), leading to incomplete ArchiMate XML.
- Current ArchiMate XML generator uses timestamp/random-based IDs, guaranteeing non-determinism even with identical JSON inputs.
- `shared/knowledge/knowledge-config.json` already provides the correct abstraction for role-based collection selection.
- `shared/scripts/json-to-archimate.py` provides type/relationship mapping reference but uses UUIDs; determinism must be implemented in-workflow.

## Technical Specifications (Schemas to define)
Minimum JSON schemas required (MVP):
1) Intent classifier schema:
- `intent` enum, `startAt` enum, `proposedProjectName`, `confidence`
2) Request brief schema:
- stable decomposition of request into structured fields
3) BRD schema:
- executive summary, stakeholders, goals, scope, NFRs, etc.
4) Capability selector schema:
- `selected[]` with `capabilityId/path/name`, `relevanceScore`, `reason`
5) Business architecture schema:
- `name`, `layer`, `elements[]`, `relationships[]`
- enforce types/enums and referential integrity via semantic validator

## Deterministic ID Specification (ArchiMate XML)
- `elementXmlId = sha256(projectSlug + ":" + artifactType + ":" + element.id).slice(0, 12)`
- `relationshipXmlId = sha256(type + ":" + source + "->" + target).slice(0, 12)`
- sort elements by `id`; relationships by `(type, source, target)`

## Knowledge Binding Specification
- Read `/data/shared/knowledge/knowledge-config.json`
- For a stage, compute `collections = agent_collection_mapping[consumerRole]`
- Query Qdrant per collection
- Record:
  - `knowledgeConfig.version`
  - collections used
  - candidate counts and selected counts
</PRD>
