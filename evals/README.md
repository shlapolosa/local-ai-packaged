# Architecture Pipeline + OAM Agent Evals

Pytest suite that exercises both ends of the architecture-to-deployment chain:

| Flow | Webhook | Suite | Typical wall time |
|---|---|---|---|
| Monolith Architecture Pipeline | `POST /webhook/architecture-pipeline` (async; poll artifact-get) | `test_monolith.py` | 20–35 min per slug |
| OAM Solution Architect agent | `POST /webhook/solution-architect-oam` (sync) | `test_oam_agent.py` | 1–4 min per slug × intent |
| Consumer-protocol intent gating | same OAM webhook with varied `intent` | `test_consumer_protocol.py` | 1–4 min per case |
| Artifact retrieval | `GET /webhook/architecture-artifact-v2` | `test_retrieval.py` | < 1 s per case |

## Run

```bash
cd evals
pip install -r requirements.txt

# Fast lane: retrieval + non-LLM contract checks (< 1 min total)
pytest -m fast

# Default lane: OAM agent + consumer-protocol intents (~10–15 min, no deploys)
pytest -m "not slow and not deploys"

# Nightly regression (includes monolith — 20–35 min × slugs)
pytest -m regression

# Anything that triggers a real GitOps commit / ArgoCD deploy is gated:
pytest -m deploys     # only if you want to fire app.submit live
```

## What each suite catches

### `test_oam_agent.py` — contract + quality

These are derived from real failure modes we hit while building the agent:

1. **No fabricated WIP** — `status=ok` requires a real `oam.dry_run` response with `ok:true` in the captured tool history.
2. **YAML structural conformance** — parses, has `apiVersion: core.oam.dev/v1beta1`, `kind: Application`, `metadata.{name,namespace}`, `spec.components[]`.
3. **Closed-vocabulary check** — every `type:` in the YAML appears in a live `catalog.list({provisionable_only:true})`.
4. **No `ApplicationClaim/*`-backed types** — known RBAC gap; agent must skip them.
5. **Naming convention** — components match `{projectSlug}-{role}` or `shared-{type}` (R4).
6. **Completeness** — `mapped_capabilities` ≥ 70 % of distinct architectural elements across `application_arch + data_arch + infrastructure_arch`. Catches the "silently dropped data layer" failure.
7. **Multi-layer coverage** — final OAM touches at least app + data layers when the architecture has both.
8. **WIP-no-write** — when `status=wip`, no new `oam_application` row appears in `architecture.artifacts`.
9. **Turns + wall time SLOs** — `turns_used ≤ 14`, `dt ≤ 240 s` (gpt-5.4). Regression detection.

### `test_consumer_protocol.py` — intent gating

For each intent the agent's tool surface and side effects must match the protocol:

- `intent=oam` → `submit==null`, `submit_wait==null`, `proposed_prs==[]`.
- `intent=propose` on a clean slug → `proposed_prs==[]` (nothing to propose).
- `intent=propose` on a slug with synthetic unmappable → `proposed_prs` has ≥1 PR draft body with a `capability-factory/requests/REQ-` file path.
- `intent=provision_wait` on pass → calls `app.submit` (not submit_wait); on missing-CD → `app.submit_wait`.
- `intent=provision` / `both` → calls `app.submit` only when dry-run passes.

The deploy-firing tests are marked `deploys`; skipped by default.

### `test_retrieval.py` — artifact-get

- 200 + `{ok:true, artifact:{type, version, content,…}}` for a known slug+type.
- 404 / `{ok:false}` on unknown slug.
- Returns highest-version artifact when multiple versions exist.

### `test_monolith.py` — slow, marked `slow regression`

- Smoke fire returns `{ack with projectSlug}`.
- After polling, all 17 expected artifact types land within the budget.
- **Regression guard: `application_arch`, `data_arch`, `infrastructure_arch` content must NOT equal `{}`** — this is the qwen3-coder JSON-stage failure we observed on 2026-05-28.
- BRD has a non-empty `components` array.
- ArchiMate XML artifacts parse as XML.

## Cost notes

| Suite | Tokens (rough) | Wall-time per case | Notes |
|---|---|---|---|
| `test_retrieval.py` | 0 | < 1 s | No LLM |
| `test_oam_agent.py` (gpt-5.4) | ~10–25 k | ~180–225 s | Real Foundry call per slug × intent |
| `test_consumer_protocol.py` (gpt-5.4) | ~10–25 k | ~180–225 s | Same |
| `test_monolith.py` (qwen3-coder 480B) | ~80–150 k | ~1500 s | Ollama Cloud cost; ~25 min |

A single `pytest -m "not slow and not deploys"` run touches the OAM agent ~8 times. Budget ~30 min wall time and a few hundred kilotokens of gpt-5.4 per nightly.

## Knobs (env vars honoured by `conftest.py`)

```
N8N_BASE_URL              http://localhost:5678   default
OAM_WEBHOOK               /webhook/solution-architect-oam
MONOLITH_WEBHOOK          /webhook/architecture-pipeline
ARTIFACT_GET_WEBHOOK      /webhook/architecture-artifact-v2
APIM_SP_ENV_PATH          /Users/socrateshlapolosa/Development/copilots/.env
DOCKER_COMPOSE_PROJECT    localai
DB_CONTAINER              db
N8N_CONTAINER             n8n

MONOLITH_POLL_TIMEOUT     2700   (seconds; 45 min default)
OAM_AGENT_TIMEOUT         360    (seconds; 6 min default)

EVAL_SLUGS                comma-separated override for the corpus list
```
