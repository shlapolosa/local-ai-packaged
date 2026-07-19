# Solution Architect → OAM

A second n8n workflow that consumes the Architecture Pipeline's per-slug artifacts and produces an executable **KubeVela OAM Application**, optionally submitted for provisioning via the live Capability Catalog MCP.

## Webhook contract

| | |
|---|---|
| **Path** | `POST /webhook/solution-architect-oam` |
| **Body** | `{ "projectSlug": "<slug>", "intent": "oam" \| "provision" \| "both" }` |
| **Auth** | None (internal). Bearer token honoured if the n8n pipe configures it. |
| **Timing** | Synchronous. ~30–60s per call (one agent loop, ≤12 turns). |
| **Response** | `200` JSON with the full OAM YAML inline (see below). |

### Intents

| Intent | What happens |
|---|---|
| `oam` | Generate the OAM Application + run `catalog.validate` (vela dry-run). No submission. |
| `provision` | Same as `oam`, then call `app.submit` → validate → commit to GitOps → trigger oam-apply. |
| `both` | Alias of `provision`. |

### Response shape

```json
{
  "ok": true,
  "projectSlug": "ap-clean-final",
  "projectName": "Ap Clean Final",
  "intent": "oam",
  "type": "oam_application",
  "version": 1,
  "created_at": "2026-05-28T08:49:28.912731+00:00",
  "oam": { "yaml": "apiVersion: core.oam.dev/v1beta1\nkind: Application\n..." },
  "dry_run": { "content": [{ "type": "text", "text": "{ \"ok\": true, \"diagnostics\": \"...\" }" }] },
  "provision": null,
  "model": { "deployment": "gpt-5.4-mini" },
  "agent": { "turns_used": 6 }
}
```

Same row is persisted in Postgres `architecture.artifacts` as `type=oam_application`. Retrieve later via the existing artifact-get webhook:

```
GET /webhook/architecture-artifact-v2?projectSlug=<slug>&type=oam_application
```

## Architecture

```
Open WebUI            n8n workflow                                   APIM (sp-ai-usecase-poc)
─────────────         ───────────────────────                         ──────────────────────
 user types     ─POST→ /webhook/solution-architect-oam
 "oam <slug>"          │
                       ├─ Validate input
                       ├─ PG: resolve project_id
                       ├─ PG: fetch infrastructure_arch,
                       │       application_arch, data_arch,
                       │       solution_arch_md
                       │
                       └─ Code: Solution Architect Agent ─POST→ login.microsoftonline.com
                          │                                        (client_credentials → Bearer)
                          │
                          ├─ MCP handshake ────────────────────POST→ /mcp/catalog/mcp
                          │   (initialize + notifications/initialized)
                          │
                          └─ AOAI agent loop ──────────────────POST→ /openai/deployments/
                             max 12 turns                              gpt-5.4-mini/chat/completions
                                                                       ?api-version=2024-10-21
                             tool_calls → MCP tools/call ────────POST→ /mcp/catalog/mcp
                                catalog.list / .describe / .search /
                                .semantic_search / .scaffold / .validate
                                app.submit  (only on provision/both)
                       │
                       ├─ Prep insert (base64 packs payload)
                       ├─ PG: INSERT architecture.artifacts (type=oam_application, version=N+1)
                       └─ Respond JSON  ──────────────────────────────→  OAM YAML rendered inline
```

## Setup

These are one-time steps. Most boxes are already ticked on this machine.

1. **n8n container env** (already in `docker-compose.override.private.yml`):

   ```yaml
   services:
     n8n:
       environment:
         - NODE_FUNCTION_ALLOW_BUILTIN=fs,crypto,buffer
         - NODE_FUNCTION_ALLOW_EXTERNAL=*
   ```

   Required so the agent Code node can `require('fs')` to read SP creds.

2. **SP credentials file** on n8n's persistent volume:

   ```
   /home/node/.n8n/.apim-sp.json
   ```

   Holds `{tenant_id, client_id, client_secret, audience, apim_base, mcp_path, aoai_chat_path_template, deployment_default}`. Created from `/Users/socrateshlapolosa/Development/copilots/.env` via `docker exec` (see commit history). Re-create with:

   ```bash
   # values read from copilots/.env, never printed
   N8N_CT=n8n
   CID=$(awk -F= '/^SP_CLIENT_ID=/{sub(/^SP_CLIENT_ID=/,"");print}' /Users/socrateshlapolosa/Development/copilots/.env)
   CSEC=$(awk -F= '/^SP_CLIENT_SECRET=/{sub(/^SP_CLIENT_SECRET=/,"");print}' /Users/socrateshlapolosa/Development/copilots/.env)
   TID=$(awk -F= '/^SUBSCRIPTION_TENANT_ID=/{sub(/^SUBSCRIPTION_TENANT_ID=/,"");print}' /Users/socrateshlapolosa/Development/copilots/.env)
   python3 -c "import json,sys; print(json.dumps({
     'tenant_id': sys.argv[3], 'client_id': sys.argv[1], 'client_secret': sys.argv[2],
     'audience': 'api://fe225ae2-c6eb-4e4e-b4c2-79b45b2dce69/.default',
     'apim_base': 'https://aigw-apim-dev-w4x7ibwk4e2is.azure-api.net',
     'mcp_path': '/mcp/catalog/mcp',
     'aoai_chat_path_template': '/openai/deployments/{deployment}/chat/completions?api-version=2024-10-21',
     'deployment_default': 'gpt-5.4-mini',
     'deployment_frontier': 'gpt-5.4'
   }, indent=2))" "$CID" "$CSEC" "$TID" \
     | docker exec -i "$N8N_CT" sh -c 'cat > /home/node/.n8n/.apim-sp.json && chmod 600 /home/node/.n8n/.apim-sp.json'
   ```

   The SP `sp-ai-usecase-poc` lives in the **subscription** tenant `df03bef9-…` (`SUBSCRIPTION_TENANT_ID`), not `WORK_TENANT_ID`. Tenant mismatch → `AADSTS700016`.

3. **Workflow file**: `n8n/backup/workflows/Solution_Architect_OAM.json` (id `SolArchOAM01wf01`).
   The agent JS source lives at `n8n/sources/solution_architect_agent.js` for readability; splice into the workflow JSON with:
   ```bash
   python3 -c "
   import json
   wf='n8n/backup/workflows/Solution_Architect_OAM.json'
   js='n8n/sources/solution_architect_agent.js'
   w=json.load(open(wf))
   for n in w['nodes']:
     if n.get('id')=='n-agent': n['parameters']['jsCode']=open(js).read()
   json.dump(w, open(wf,'w'), indent=2)"
   ```
   then re-import:
   ```bash
   cat n8n/backup/workflows/Solution_Architect_OAM.json | docker exec -i n8n sh -c 'cat > /tmp/w.json && n8n import:workflow --input=/tmp/w.json; rm -f /tmp/w.json'
   docker exec n8n n8n update:workflow --id=SolArchOAM01wf01 --active=true
   docker restart n8n
   ```

4. **Open WebUI pipe**: `solution_architect_pipe.py`.
   Open WebUI → Workspace → Functions → "+" → paste the file → Save → enable.

## Usage examples

### Via curl

```bash
# generate OAM only
curl -sS -X POST http://localhost:5678/webhook/solution-architect-oam \
  -H 'Content-Type: application/json' \
  -d '{"projectSlug":"ap-clean-final","intent":"oam"}' | jq '.oam.yaml' -r

# generate AND submit to GitOps
curl -sS -X POST http://localhost:5678/webhook/solution-architect-oam \
  -H 'Content-Type: application/json' \
  -d '{"projectSlug":"ap-clean-final","intent":"both"}' | jq

# fetch the latest persisted OAM
curl -sS 'http://localhost:5678/webhook/architecture-artifact-v2?projectSlug=ap-clean-final&type=oam_application' | jq
```

### Via Open WebUI chat

```
oam ap-clean-final
provision ap-clean-final
both ap-clean-final
help
```

## Catalog MCP tool surface (auto-used by the agent)

| Tool | Required args | Optional | What it does |
|---|---|---|---|
| `catalog.list` | — | `provisionable_only` | live `ComponentDefinitions` from the cluster |
| `catalog.describe` | `name` | — | parameter schema for that component |
| `catalog.search` | `category`, `qualityAttributes` | `weights` | deterministic ranked KB technologies |
| `catalog.semantic_search` | `intent` | `top`, `category` | NL intent → embedding → AI Search match + live `is_provisionable` check |
| `catalog.scaffold` | `component` | `app_name`, `namespace` | minimal valid OAM snippet for a component |
| `catalog.validate` | `oam_yaml` | — | `vela dry-run` |
| `app.submit` | `oam_yaml` | — | validate → commit OAM to gitops → trigger oam-apply (only path to provision) |

The agent's system prompt requires it to always call `catalog.validate` before finalising and to call `app.submit` only when the user intent is `provision` or `both`.

## Troubleshooting

### Agent fails fast (< 1s, empty response body)

Almost always the agent Code node threw — n8n's webhook returns an empty 200 when the responding node is never reached. Check:

```sql
SELECT id, status FROM execution_entity WHERE "workflowId"='SolArchOAM01wf01' ORDER BY id DESC LIMIT 1;
```

For the actual error message, decode the latest `execution_data.data` (it's stored as a deref-table of strings — see the troubleshooting snippet at the end of `architecture-pipeline-ops`).

### `AADSTS700016: Application … was not found in the directory 'socratespersonal'`

The SP lives in the **subscription** tenant (`SUBSCRIPTION_TENANT_ID`, `df03bef9-…`), not `WORK_TENANT_ID` (`b911f4d4-…`, the M365 tenant). Verify `/home/node/.n8n/.apim-sp.json` has the subscription tenant id.

### AOAI returns HTTP 500 "Internal Server Error" via APIM

APIM's openai API `serviceUrl` may have drifted again. The expected value is `https://aifoundry-socrates.cognitiveservices.azure.com/openai` (trailing `/openai` is required because APIM strips the matched API path segment), and APIM's system-assigned MI needs the `Cognitive Services OpenAI User` role on the Foundry resource. Direct-Foundry (`api-key` header) is a sanity check for whether the model itself is healthy.

### Webhook 404

The retrieval workflow `Architecture Artifact Get v2` (id `7IUOzaD9TUwXP2Qw`) can flip inactive on restart in some setups. Activate:
```bash
docker exec n8n n8n update:workflow --id=7IUOzaD9TUwXP2Qw --active=true
docker restart n8n
```

### Agent loops past 12 turns

Edit `MAX_TURNS` in `n8n/sources/solution_architect_agent.js`, re-splice, re-import, restart.

## Files

| Path | Role |
|---|---|
| `n8n/backup/workflows/Solution_Architect_OAM.json` | The n8n workflow (importable, id `SolArchOAM01wf01`). |
| `n8n/sources/solution_architect_agent.js` | Readable JS source of the agent Code node. Splice into the workflow JSON via the snippet above. |
| `solution_architect_pipe.py` | Open WebUI Function. |
| `docs/SOLUTION-ARCHITECT-OAM.md` | This file. |
| `/home/node/.n8n/.apim-sp.json` *(inside the n8n container, persistent volume)* | SP creds + APIM config the agent reads at runtime. |
