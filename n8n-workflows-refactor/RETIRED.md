# RETIRED — absorbed into health-service-idp (2026-06-11)

This n8n architecture pipeline (7-stage document flow: BA→BRD, 4 architecture
views, solution-reuse assessment, risk, test strategy, PM→PRD, SD→taskmaster)
was never deployed in-cluster and is **superseded by the platform-native path**
in `shlapolosa/health-service-idp`:

| This pipeline | Replaced by |
|---|---|
| webhook intake + classify + slugify | slack-api-server → `app.submit` + architect-v1 |
| Qdrant landscape search (reuse) | catalog MCP `kb.*` / `examples.*` |
| Ollama generation | Foundry architect-v1 |
| Postgres project/job/artifact state | intake ledger + claims/ArgoCD + `lifecycle.state` |
| SSH+git artifact commits | mscv / FactoryBot GitHub App |

The durable residue — the LLM system prompts, output schemas, and per-stage
validation criteria — was ported verbatim (N8N-ABSORB #174, commit `5f4c1cf`) to:

`health-service-idp/factory/production-lines/traditional-cloud/adapters/compose/prompts/analysis/`

They will be wired as architect-v1's opt-in "deep analysis" mode
(dev-agent-factory plan, W5). The JSON exports in this directory are kept
read-only for provenance.
