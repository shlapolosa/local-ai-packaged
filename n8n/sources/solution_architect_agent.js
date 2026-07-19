// ─────────────────────────────────────────────────────────────────────────────
// Solution Architect — consumer agent for the producer/consumer catalog model.
//
// Implements the 6-phase consumer protocol (compose → verify → diagnose →
// revise → submit → monitor) over the live Catalog + Factory MCPs at APIM.
//
// Intents (gated tool surface):
//   oam            — compose + catalog.validate only. Never submits / proposes.
//   provision      — compose + dry_run. If pass: app.submit. Else: WIP.
//   provision_wait — compose + dry_run. If pass: app.submit. Else missing-CD
//                    case: app.submit_wait (commit + 72h polling).
//   propose        — compose + dry_run. For each unmappable, try Option A
//                    (catalog.search alt). If still unmappable: factory.propose.
//   both           — alias for provision (legacy).
//
// Reads SP creds + APIM config from /home/node/.n8n/.apim-sp.json.
// Single JWT (audience api://fe225ae2-…/.default) authorises catalog + factory
// + Foundry AOAI in one round-trip.
// ─────────────────────────────────────────────────────────────────────────────

const fs = require('fs');
const ctx = $input.all()[0].json;
const sp = JSON.parse(fs.readFileSync('/home/node/.n8n/.apim-sp.json', 'utf8'));

const APIM         = sp.apim_base;
const MCP_CATALOG  = APIM + sp.mcp_path;
const MCP_FACTORY  = APIM + (sp.factory_mcp_path || '/mcp/factory/mcp');
const DEPLOYMENT   = sp.deployment_default;
const MODE         = sp.mode || 'apim';
const FACTORY_REPO = sp.default_factory_repo || 'health-service-idp';

const AOAI_URL = (MODE === 'direct' && sp.foundry_direct_base)
  ? (sp.foundry_direct_base + sp.aoai_chat_path_template.replace('{deployment}', DEPLOYMENT))
  : (APIM + sp.aoai_chat_path_template.replace('{deployment}', DEPLOYMENT));
const AOAI_AUTH_HDR = (MODE === 'direct' && sp.foundry_api_key)
  ? { 'api-key': sp.foundry_api_key }
  : null;

const TICK = String.fromCharCode(96);
const FENCE = TICK + TICK + TICK;

// ─── HTTP helper (n8n sandbox lacks global fetch; this.helpers.httpRequest used) ───
async function _sleep(ms) { await new Promise(r => setTimeout(r, ms)); }
const _BACKOFF_MS = [5000, 15000, 30000, 60000, 60000];
async function http(method, url, headers, body) {
  const opts = {
    method, url,
    headers: headers || {},
    returnFullResponse: true,
    json: false,
    encoding: 'utf8',
    // Hard per-request cap so a single unresponsive upstream (AOAI / MCP) can't
    // hang the agent indefinitely. With 6 retry attempts this still gives
    // ~12 min worst case per call slot.
    timeout: 120000,
  };
  if (body !== undefined) opts.body = body;
  let attempt = 0;
  const maxAttempts = _BACKOFF_MS.length + 1;
  while (true) {
    attempt++;
    try {
      const resp = await this.helpers.httpRequest(opts);
      const sc = resp.statusCode || resp.status;
      if ((sc === 429 || sc === 503) && attempt < maxAttempts) {
        const ra = (resp.headers && (resp.headers['retry-after'] || resp.headers['Retry-After'])) || null;
        const wait = ra ? Math.min(parseInt(ra, 10) * 1000, 60000) : _BACKOFF_MS[attempt - 1];
        await _sleep(wait); continue;
      }
      return resp;
    } catch (e) {
      const status = e.statusCode || e.status || (e.response && e.response.status);
      const code = (e && e.code) || '';
      const msg  = String((e && e.message) || e);
      // Transient = either a known retryable HTTP status, OR a connection-level
      // failure with no status at all (socket hang up, reset, timeout, DNS blip).
      const NET_RE = /socket hang up|ECONNRESET|ETIMEDOUT|EPIPE|EAI_AGAIN|ENOTFOUND|read ECONNRESET|aborted/i;
      const isTransientStatus  = (status === 429 || status === 503 || status === 502 || status === 504);
      const isTransientNetwork = (!status) && (NET_RE.test(msg) || NET_RE.test(code));
      if ((isTransientStatus || isTransientNetwork) && attempt < maxAttempts) {
        const ra = (e.response && e.response.headers && (e.response.headers['retry-after'] || e.response.headers['Retry-After'])) || null;
        const wait = ra ? Math.min(parseInt(ra, 10) * 1000, 60000) : _BACKOFF_MS[attempt - 1];
        await _sleep(wait); continue;
      }
      const ebody = (e.response && e.response.body) || msg;
      const err = new Error('HTTP ' + (status || '?') + ' ' + method + ' ' + url + ': ' + String(ebody).slice(0, 400));
      err.httpStatus = status || null;
      err.httpUrl = url;
      throw err;
    }
  }
}

function formEncode(obj) {
  return Object.entries(obj).map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v)).join('&');
}

async function getToken() {
  const body = formEncode({
    grant_type: 'client_credentials',
    client_id: sp.client_id,
    client_secret: sp.client_secret,
    scope: sp.audience,
  });
  const resp = await http.call(this, 'POST',
    'https://login.microsoftonline.com/' + sp.tenant_id + '/oauth2/v2.0/token',
    { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  );
  if (resp.statusCode >= 400) throw new Error('token mint ' + resp.statusCode + ': ' + String(resp.body).slice(0, 300));
  return JSON.parse(resp.body).access_token;
}

// ─── Per-MCP JSON-RPC / SSE client ───
function makeMcpClient(serverUrl, bearerH) {
  let rpcId = 0;
  let initialized = false;
  async function call(method, params) {
    const id = ++rpcId;
    const payload = { jsonrpc: '2.0', method };
    if (!method.startsWith('notifications/')) payload.id = id;
    if (params) payload.params = params;
    const resp = await http.call(this, 'POST', serverUrl,
      { ...bearerH, 'Accept': 'application/json, text/event-stream' },
      JSON.stringify(payload),
    );
    if (method.startsWith('notifications/')) return null;
    if (resp.statusCode >= 400) throw new Error(`${serverUrl} ${method} ${resp.statusCode}: ${String(resp.body).slice(0,300)}`);
    const text = String(resp.body);
    const lines = text.split('\n').map(l => l.trim()).filter(l => l.startsWith('data:'));
    if (!lines.length) throw new Error(`${serverUrl} ${method}: no SSE data line. body=${text.slice(0,200)}`);
    return JSON.parse(lines[lines.length - 1].slice(5).trim());
  }
  async function ensureInit() {
    if (initialized) return;
    await call.call(this, 'initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'n8n-sol-arch', version: '2.0' } });
    await call.call(this, 'notifications/initialized');
    initialized = true;
  }
  return { call, ensureInit };
}

// ─── Top-level guarded body — never throw, always return structured WIP/OK ───
let __agentResult = null;
try {

const tok = await getToken.call(this);
const H = { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok };

const catalogMcp = makeMcpClient(MCP_CATALOG, H);
const factoryMcp = makeMcpClient(MCP_FACTORY, H);
await catalogMcp.ensureInit.call(this);
// Lazy-init factory only if the intent allows propose (avoid unnecessary RTT).

// ─── Intent-gated tool surface ───
const intent = ctx.intent; // already normalised by Validate Input
const allowSubmit     = (intent === 'provision' || intent === 'both' || intent === 'provision_wait');
const allowSubmitWait = (intent === 'provision_wait');
const allowPropose    = (intent === 'propose');

const baseTools = [
  { name: 'catalog.list',     desc: 'List published OAM capabilities (live ComponentDefinitions). Call this first.',
    params: { type: 'object', properties: { provisionable_only: { type: 'boolean' } } } },
  { name: 'catalog.describe', desc: 'Describe a component incl. its parameter schema (`parameters[]` with name/type/required/default), `applicable_traits[]`, `description_completeness`. The `parameters[]` list is AUTHORITATIVE — use ONLY those names; never invent fields.',
    params: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] } },
  { name: 'catalog.search',   desc: 'Rank KB technologies for a structured CapabilityRequest (category + qualityAttributes [+ weights]).',
    params: { type: 'object', properties: { category: { type: 'string' }, qualityAttributes: { type: 'object' }, weights: { type: 'object' } }, required: ['category', 'qualityAttributes'] } },
  { name: 'catalog.scaffold', desc: 'Return a minimal valid OAM Application snippet for a component.',
    params: { type: 'object', properties: { component: { type: 'string' }, app_name: { type: 'string' }, namespace: { type: 'string' } }, required: ['component'] } },
  { name: 'catalog.validate',      desc: 'vela dry-run over an OAM Application. Returns {ok, diagnostics}. PREFERRED validate tool per the consumer protocol.',
    params: { type: 'object', properties: { oam_yaml: { type: 'string' } }, required: ['oam_yaml'] } },
  // ── New cluster-wide discovery tools (live as of 2026-05-30) ──
  { name: 'catalog.traits', desc: 'List all TraitDefinitions cluster-wide.',
    params: { type: 'object', properties: {} } },
  { name: 'catalog.describe_trait', desc: 'Trait parameter schema (live vela show). Call BEFORE attaching any trait.',
    params: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] } },
  { name: 'catalog.traits_for', desc: 'List the traits applicable to a given component type. Authoritative gate: if a trait is NOT in this result for component X, you may NOT attach it to X.',
    params: { type: 'object', properties: { component_type: { type: 'string' } }, required: ['component_type'] } },
  { name: 'catalog.policies', desc: 'List all PolicyDefinitions cluster-wide.',
    params: { type: 'object', properties: {} } },
  { name: 'catalog.describe_policy', desc: 'Policy parameter schema (parsed from CUE). Call BEFORE referencing any policy.',
    params: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] } },
  { name: 'catalog.workflow_steps', desc: 'List all WorkflowStepDefinitions.',
    params: { type: 'object', properties: {} } },
  { name: 'catalog.describe_workflow_step', desc: 'Workflow step parameter schema. Call BEFORE referencing any workflow step.',
    params: { type: 'object', properties: { name: { type: 'string' } }, required: ['name'] } },
  { name: 'catalog.connectivity_recipes', desc: 'Pre-approved trait/policy wiring for composite components (e.g. compute-service + datastore). If a recipe matches, emit its `emit:` files alongside the components. Never invent a connectivity pattern.',
    params: { type: 'object', properties: { a: { type: 'string' }, b: { type: 'string' } } } },
];

const submitTools = !allowSubmit ? [] : [
  { name: 'app.submit', desc: 'OAM-first provisioning: re-validate + commit OAM to gitops + trigger oam-apply workflow. SYNC. Requires the OAM to already pass catalog.validate.',
    params: { type: 'object', properties: { oam_yaml: { type: 'string' } }, required: ['oam_yaml'] } },
];

const submitWaitTools = !allowSubmitWait ? [] : [
  { name: 'app.submit_wait', desc: 'Commit OAM + trigger oam-apply-wait workflow that polls vela dry-run every 60s until prereqs land (up to 72h), then deploys. USE THIS when some referenced ComponentDefinitions are missing and you have already filed (or will file) a factory.propose request.',
    params: { type: 'object', properties: { oam_yaml: { type: 'string' } }, required: ['oam_yaml'] } },
];

const proposeTools = !allowPropose ? [] : [
  { name: 'factory.propose', desc: 'Open a PR to file a CapabilityRequest. files MUST map paths under "capability-factory/requests/REQ-NNN-<slug>.yaml" to YAML bodies. Never push implementation files (crossplane/, kb/, docs/adr/). Repo defaults to ' + JSON.stringify(FACTORY_REPO) + '.',
    params: { type: 'object', properties: {
      repo: { type: 'string' },
      title: { type: 'string' },
      body: { type: 'string' },
      files: { type: 'object' },
      base: { type: 'string' },
      branch_prefix: { type: 'string' },
    }, required: ['title', 'body', 'files'] } },
  { name: 'factory.list_open_prs', desc: 'List currently-open consumer/factory PRs in repo (for awareness — avoid duplicating an in-flight request).',
    params: { type: 'object', properties: { repo: { type: 'string' }, head_prefix: { type: 'string' } } } },
];

const toolDefs = [...baseTools, ...submitTools, ...submitWaitTools, ...proposeTools];
const aoaiTools = toolDefs.map(t => ({ type: 'function', function: { name: t.name, description: t.desc, parameters: t.params } }));
const allowedNames = new Set(toolDefs.map(t => t.name));

// ─── System prompt ───
const archContext = {
  infrastructure_arch: ctx.artifacts.infrastructure_arch,
  application_arch:    ctx.artifacts.application_arch,
  data_arch:           ctx.artifacts.data_arch,
  solution_arch_md:    ctx.artifacts.solution_arch_md,
};

const systemPrompt = [
  'You are the Solution Architect consumer agent. Your job: compose ONE KubeVela OAM Application from the project architecture below using only components from the live capability catalog, verify it with catalog.validate, then (per intent) submit or propose.',
  '',
  'Current request:',
  '  projectSlug: ' + ctx.projectSlug,
  '  intent: ' + intent,
  '  tools available this run: ' + [...allowedNames].sort().join(', '),
  '',
  '═══ Non-negotiable rules ═══',
  'R0. EVIDENCE. Do not emit a final answer until you have called catalog.validate on a complete assembled OAM YAML and observed the response. Never predict outcomes; always observe them. You may call catalog.validate up to 3 times — if it still fails after the third try, follow the consumer protocol (Option A/B/C) rather than re-trying further.',
  'R1. SUBMIT GUARD. Never call app.submit / app.submit_wait without a successful catalog.validate on the exact YAML you intend to submit.',
  'R2. CLOSED VOCABULARY. The `type:` under spec.components[*] is exactly what catalog.list returns. Don\'t invent. Don\'t alias to generic strings.',
  'R3. AVOID ApplicationClaim/* components. Known cluster RBAC gap; they fail catalog.validate.',
  'R4. NAMING and NAMESPACE. metadata.name MUST be "' + ctx.projectSlug + '-app". metadata.namespace MUST be "default" (the catalog cluster currently has namespace-scoped RBAC that breaks catalog.validate for any non-default namespace; revisit once that is widened). Initiative-scoped components: `' + ctx.projectSlug + '-{role}`. Shared infra: `shared-{type}`. Component names disambiguate projects; namespace is shared by design.',
  'R5. SOURCE-OF-TRUTH HIERARCHY (replaces "be exhaustive across all four artifacts"):',
  '   The OAM must model THE COMPONENTS THIS APPLICATION ACTUALLY USES, derived in this order:',
  '     1. solution_arch_md — primary source. The "## Components:" + "## Data Flow:" / "## Component Mappings:" sections describe what the app consumes.',
  '     2. application_arch — secondary; itemises the same components in structured form. Use it to disambiguate names/technologies named in solution_arch_md.',
  '     3. data_arch — describes specifically-named stores the app uses (e.g. "Invoice DB"). Only include those that solution_arch_md or application_arch references.',
  '     4. infrastructure_arch — PLATFORM CONTEXT, NOT A CHECKLIST. It enumerates what the cluster CAN provide (MongoDB, Event Hubs, APIM, AGIC, IdPs, etc.). Include an infrastructure_arch component in the OAM ONLY IF solution_arch_md or application_arch directly references it as something this app uses. Treat platform-only items (e.g. APIM, AGIC, generic IdP, generic MongoDB/Cosmos/Event Hubs) as platform-managed unless the application explicitly consumes them.',
  '   Rule of thumb: if a component appears in your final OAM but no other component\'s `properties` references its `component_name` (via `database:`, `cache:`, `messaging:`, `identityProvider:`, env vars, etc.), it is almost certainly an orphan — either wire it in or remove it.',
  '',
  '   Concretely for the live MFG-TC catalog: APIM, AGIC, and external IdPs that solution_arch_md describes as platform-level concerns (auth handled by APIM, ingress handled by AGIC) are NOT separate OAM components — they\'re ambient platform services. Only emit an `auth0-idp` / `identity-service` component when the application code explicitly integrates with one beyond what APIM provides.',
  '',
  '═══ Working principles (not enumerations — guides) ═══',
  '• Generic primitives are reusable. Many capabilities legitimately share the same `type:` while differing by `component_name`. That\'s the point of generic components.',
  '• Translate before you search. Architecture artifacts name things in domain or vendor terms ("Invoice Database", "AKS", "Event Hubs"). Search on the functional category ("relational database", "kubernetes runtime", "event streaming"), not the literal name.',
  '• Vendor names are aliases. AKS/Event Hubs/Cosmos DB/APIM/etc. → find the closest catalog primitive. Don\'t mark UNMAPPABLE just because vendor branding is missing.',
  '',
  '═══ AUTHORING RULES (mandatory checks before catalog.validate / app.submit) ═══',
  'A1. For EACH component you place, BEFORE writing its `properties:`, call catalog.describe(<component_type>) and treat the returned `parameters[]` list as AUTHORITATIVE. Use only those parameter names, with the documented types/required/default. Do NOT invent parameter names. If a parameter is marked `required:true`, you MUST set it (or apply A5/A6 below).',
  'A2. For EACH trait you intend to attach to a component, call catalog.traits_for(<component_type>) FIRST. If the trait is not in the returned list, you may NOT attach it to that component — find another way to express the requirement. After confirming applicability, call catalog.describe_trait(<trait_name>) and treat its parameters as authoritative just like A1.',
  'A3. For EACH policy you reference in `spec.policies`, call catalog.describe_policy(<policy_name>) and follow its parameter schema. For EACH workflow step in `spec.workflow.steps`, call catalog.describe_workflow_step(<step_name>) and respect its schema.',
  'A4. For COMPOSITE component splits (e.g. a webservice that needs a postgres datastore, or a webservice that needs a redis cache) — call catalog.connectivity_recipes(<a>, <b>) using broad categories ("compute-service", "datastore", "cache", "messaging" …). If a recipe matches, emit each file from the recipe\'s `emit:` block alongside the components, in the order the recipe specifies. NEVER invent a connectivity pattern.',
  'A5. IMAGES — schema-driven (DO NOT hard-code enums; trust catalog.describe at runtime).',
  '   The webservice schema makes `image` auto-derived by default. The canonical path is `language:` + optional `framework:`. CRITICAL: the live enum values for both `language` and `framework` come from the CURRENT `catalog.describe(webservice).parameters` response — they have changed multiple times this week (e.g. {python,java,nodejs,rasa} → narrowed to {python,java}; framework "auto" → narrowed to {fastapi,springboot}). YOU MUST honour whatever enum is live RIGHT NOW, not a remembered enum. Procedure, per component:',
  '     (a) Read `catalog.describe(webservice)` BEFORE composing properties; locate the `language` and `framework` parameter entries; the `type` field carries the current enum (e.g. `"python" or "java"`).',
  '     (b) Map the architecture\'s technology hint (e.g. "Python/FastAPI", "Java/Spring Boot", "Node.js/Express") to the closest LIVE enum value. If the exact match is in the live enum, use it. If the architecture\'s technology is OUTSIDE the live enum (e.g. architecture says "Node.js/Express" but live enum is only `{python, java}`), DO NOT silently substitute. Emit a clarifying_questions entry: {"component":"<name>","field":"language","question":"Architecture specifies <X> but the live catalog enum is <enum>; defaulting to <closest> unless told otherwise."} and either (i) proceed with the closest live-enum value AND record the substitution in `placeholder_images` style notice, or (ii) emit wip and wait. Prefer (ii) for `intent=provision`; (i) is acceptable for `intent=oam`.',
  '     (c) Set `framework:` only when the architecture is specific AND the framework value is in the live `framework` enum. Otherwise omit `framework:` — it defaults harmlessly.',
  '     (d) ONLY when the architecture explicitly names a fully-qualified container image AND that image points at this cluster\'s registered ACR registry, set `image:` to that exact string.',
  '     (e) When the architecture names neither a usable language nor an image, emit a clarifying_questions entry of the form {"component":"<name>","field":"image","question":"No language in live enum matched, and no image was provided. What should this component run?"} and emit a wip shape.',
  '   NEVER set `image:` to any stock-vendor string (nginx, httpd, busybox, alpine, ubuntu, debian, redis:*, postgres:*, node:*, python:*, eclipse-temurin:*, golang:*, etc.). Schema regex requires a cluster-registered registry; catalog.validate rejects all stock images.',
  'A6. SCHEMA enums. If a `parameters[]` entry shows an enum type (e.g. registry = "dockerhub" or "acr" or "custom"), the value MUST be one of those strings. Don\'t paraphrase.',
  '',
  '═══ Working principles continued ═══',
  '• Thin schemas mean defaults work. catalog.scaffold + minimal overrides is the play.',
  '',
  '═══ Consumer protocol — apply per missing ComponentDefinition ═══',
  'When catalog.validate keeps reporting ok:false after at most 3 retries because a referenced ComponentDefinition is not found (or its CD is forbidden in the cluster), follow this priority — the design intent is: validate, submit-if-valid, else propose and queue:',
  '  A. REUSE/REPURPOSE: catalog.search with the QA you actually need; relax soft attributes. If a near-fit (score ≤ 2.0) is in catalog.list and not ApplicationClaim-backed, revise the OAM and re-run catalog.validate.',
  (allowPropose
    ? '  B. REQUEST NEW: if no acceptable substitute, call factory.propose. files MUST be under `capability-factory/requests/REQ-<id>-<slug>.yaml`. Never push implementation files. One PR per missing capability. Body must list what you considered and rejected.'
    : '  B. REQUEST NEW: not authorised for intent=' + intent + '. Surface what you would propose in `factory_propose_drafts` so the user can re-run with intent=propose.'),
  (allowSubmitWait
    ? '  C. QUEUE: call app.submit_wait — commits the OAM and polls vela dry-run for up to 72h, deploys when prereqs land.'
    : '  C. QUEUE: not authorised for intent=' + intent + '. Surface intent_hint="provision_wait" in WIP so the user can re-run with it.'),
  '',
  '═══ Per-intent submission step ═══',
  intent === 'oam'            ? '  intent=oam → do nothing further once dry_run is ok. Return the validated YAML.' :
  intent === 'provision'      ? '  intent=provision → if dry_run ok, call app.submit. If dry_run failed and protocol A/B/C cannot fully recover, emit WIP.' :
  intent === 'both'           ? '  intent=both (alias of provision) → if dry_run ok, call app.submit.' :
  intent === 'provision_wait' ? '  intent=provision_wait → if dry_run ok, app.submit; else if missing CDs, app.submit_wait (commit anyway; will deploy when prereqs land).' :
  intent === 'propose'        ? '  intent=propose → if dry_run ok, simply return YAML. If dry_run fails due to missing CDs and Option A finds no fit, call factory.propose for each gap. Do not submit OAM.' :
  '  unknown intent (defensive): treat as oam.',
  '',
  '═══ Output format ═══',
  'OK (dry_run passed, no unanswered clarifying questions) — exactly:',
  '  ' + FENCE + 'yaml',
  '  <validated OAM YAML>',
  '  ' + FENCE,
  '  ' + FENCE + 'json',
  '  {"dry_run": <catalog.validate result>, "submit": <app.submit result|null>, "submit_wait": <app.submit_wait result|null>, "proposed_prs": [<factory.propose results>] or [], "capability_coverage": [{"capability": "...", "component_name": "...", "type": "..."}, ...], "placeholder_images": [], "clarifying_questions": []}',
  '  ' + FENCE,
  '',
  'WIP — any of these conditions hold: capabilities unmappable; image source missing (A5(c)); OR `clarifying_questions` has any items. JSON only, no YAML:',
  '  ' + FENCE + 'json',
  '  {"status": "wip", "reason": "...", "mapped_capabilities": [{"capability","component_name","type"} ...], "unmappable_capabilities": [{"capability","tried_components":[...],"why"} ...], "factory_propose_drafts": [{"repo":"' + FACTORY_REPO + '","title":"...","body":"...","files":{"capability-factory/requests/REQ-<id>-<slug>.yaml":"<YAML>"}} ...], "clarifying_questions": [{"component":"<name>","field":"<param>","question":"..."} ...]}',
  '  ' + FENCE,
  '',
  'INVARIANT: `placeholder_images` in an OK response MUST be empty. If you would have populated it, you violated A5 — emit WIP with `clarifying_questions` instead.',
].join('\n');

const userMsg = 'projectSlug: ' + ctx.projectSlug + '\nintent: ' + intent + '\n\nArchitecture artifacts:\n' + JSON.stringify(archContext);

let messages = [
  { role: 'system', content: systemPrompt },
  { role: 'user',   content: userMsg },
];

// ─── Agent loop ───
const transcript = [];
const MAX_TURNS = 18;
let finalText = null;
let validateResult = null;
let submitResult = null;
let submitWaitResult = null;
let proposedPrs = [];

const self = this;
for (let turn = 1; turn <= MAX_TURNS; turn++) {
  const aoaiBody = { messages, tools: aoaiTools, tool_choice: 'auto', temperature: 1, max_completion_tokens: 16384 };
  const aoaiHeaders = AOAI_AUTH_HDR ? { 'Content-Type': 'application/json', ...AOAI_AUTH_HDR } : H;
  const aoaiResp = await http.call(self, 'POST', AOAI_URL, aoaiHeaders, JSON.stringify(aoaiBody));
  if (aoaiResp.statusCode >= 400) throw new Error('AOAI turn ' + turn + ' failed ' + aoaiResp.statusCode + ': ' + String(aoaiResp.body).slice(0, 500));
  const resp = JSON.parse(aoaiResp.body);
  const msg = resp.choices && resp.choices[0] && resp.choices[0].message;
  if (!msg) throw new Error('AOAI turn ' + turn + ': no message in response');

  transcript.push({ turn, role: 'assistant',
    tool_calls: (msg.tool_calls || []).map(tc => ({ id: tc.id, name: tc.function.name, args: tc.function.arguments })),
    content_preview: (msg.content || '').slice(0, 200) });
  messages.push(msg);

  const toolCalls = msg.tool_calls || [];
  if (!toolCalls.length) { finalText = msg.content || ''; break; }

  // Dispatch each tool_call to the correct MCP (catalog vs factory); refuse non-allowed tools.
  const toolResults = await Promise.all(toolCalls.map(async (tc) => {
    let args = {};
    try { args = JSON.parse(tc.function.arguments || '{}'); } catch (e) {}
    let result;
    const name = tc.function.name;

    // Hard-deny tools the intent does not authorise (defence in depth — already excluded from toolDefs)
    if (!allowedNames.has(name)) {
      result = { error: `tool "${name}" is not authorised for intent "${intent}"` };
    } else {
      try {
        let rpc;
        if (name.startsWith('factory.')) {
          // Auto-fill repo default
          if (name === 'factory.propose' && !args.repo) args.repo = FACTORY_REPO;
          if (name === 'factory.list_open_prs' && !args.repo) args.repo = FACTORY_REPO;
          await factoryMcp.ensureInit.call(self);
          rpc = await factoryMcp.call.call(self, 'tools/call', { name, arguments: args });
        } else {
          rpc = await catalogMcp.call.call(self, 'tools/call', { name, arguments: args });
        }
        result = rpc.result;
      } catch (e) {
        result = { error: String(e).slice(0, 300) };
      }
    }

    // Capture key results so the outer wrapper can return them faithfully
    if (name === 'catalog.validate' || name === 'oam.dry_run') validateResult = result;
    if (name === 'app.submit')       submitResult     = result;
    if (name === 'app.submit_wait')  submitWaitResult = result;
    if (name === 'factory.propose')  proposedPrs.push(result);

    return { tool_call_id: tc.id, role: 'tool', name, content: typeof result === 'string' ? result : JSON.stringify(result) };
  }));
  for (const tr of toolResults) {
    messages.push(tr);
    transcript.push({ turn, role: 'tool', name: tr.name, content_preview: (tr.content || '').slice(0, 300) });
  }
}

if (finalText === null) throw new Error('agent did not finish within ' + MAX_TURNS + ' turns');

// ─── Extract YAML + trailing JSON ───
function extractFenced(text, lang) {
  const fence = TICK + TICK + TICK;
  const escFence = fence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(escFence + '\\s*' + lang + '\\s*\\n([\\s\\S]*?)\\n' + escFence, 'i');
  const m = text.match(re);
  return m ? m[1].trim() : null;
}
const oamYaml = extractFenced(finalText, 'yaml') || extractFenced(finalText, 'yml') || '';
let trailingJson = null;
let trailingJsonRaw = null;
try {
  trailingJsonRaw = extractFenced(finalText, 'json');
  trailingJson = trailingJsonRaw ? JSON.parse(trailingJsonRaw) : null;
} catch (e) { /* may be truncated — handled below */ }

// Tolerant WIP detection: if trailing JSON failed to parse but obviously contains a wip status,
// salvage what we can rather than emitting a generic "no yaml block" error.
let agentWipSignal = (trailingJson && trailingJson.status === 'wip') ? trailingJson : null;
if (!agentWipSignal && !oamYaml && trailingJsonRaw && /"status"\s*:\s*"wip"/.test(trailingJsonRaw)) {
  agentWipSignal = { status: 'wip',
    reason: 'agent emitted a WIP signal but the JSON block was truncated/malformed',
    truncated_raw_head: trailingJsonRaw.slice(0, 1200),
  };
}

function parseValidateOk(vr) {
  if (!vr) return { ok: null, reason: 'no catalog.validate / catalog.validate result was captured' };
  try {
    const inner = (vr.content && vr.content[0] && vr.content[0].text) || '';
    const parsed = inner ? JSON.parse(inner) : null;
    if (parsed && typeof parsed.ok === 'boolean') return { ok: parsed.ok, reason: parsed.diagnostics || parsed.error || null };
    return { ok: null, reason: 'unrecognised dry_run result shape' };
  } catch (e) { return { ok: null, reason: 'dry_run result not JSON: ' + String(e).slice(0,120) }; }
}
function pickedTypes(yamlStr) {
  if (!yamlStr) return [];
  const re = /^\s+type:\s*(\S+)/gm; const out = []; let m;
  while ((m = re.exec(yamlStr)) !== null) out.push(m[1]);
  return Array.from(new Set(out));
}

// A5 defense-in-depth: refuse OK if the YAML contains stock-vendor image
// strings as `image:` values. The model is told not to do this; this catches
// regressions in the model's adherence.
const STOCK_IMAGE_RE = /^(?:nginx|httpd|apache|busybox|alpine|ubuntu|debian|centos|fedora|redis|postgres|postgresql|mongo|mongodb|node|python|golang|go|java|openjdk|eclipse-temurin|amazoncorretto|ruby|php|rust|haskell|scala|elixir|maven|gradle)(?::|$)/i;
function stockImageOffenders(yamlStr) {
  if (!yamlStr) return [];
  const offenders = [];
  const re = /^\s*image:\s*(["']?)([^\s"']+)\1\s*$/gm;
  let m;
  while ((m = re.exec(yamlStr)) !== null) {
    const img = m[2];
    if (STOCK_IMAGE_RE.test(img)) offenders.push(img);
  }
  return Array.from(new Set(offenders));
}

const vCheck = parseValidateOk(validateResult);

// ─── Resolve final result ───
if (agentWipSignal) {
  __agentResult = {
    __status: 'wip', ok: false, status: 'wip',
    reason: agentWipSignal.reason || 'agent reported unmappable capabilities',
    unmappable_capabilities: agentWipSignal.unmappable_capabilities || [],
    mapped_capabilities: agentWipSignal.mapped_capabilities || [],
    factory_propose_drafts: agentWipSignal.factory_propose_drafts || [],
    clarifying_questions: agentWipSignal.clarifying_questions || [],
    agent: { turns_used: transcript.filter(t => t.role === 'assistant').length, transcript_brief: transcript },
    model: { deployment: DEPLOYMENT, mode: sp.mode || 'apim' },
  };
} else if (!oamYaml) {
  __agentResult = {
    __status: 'wip', ok: false, status: 'wip',
    reason: 'agent finished without a fenced yaml block',
    agent_final_text_preview: (finalText || '').slice(0, 800),
    agent: { turns_used: transcript.filter(t => t.role === 'assistant').length, transcript_brief: transcript },
    model: { deployment: DEPLOYMENT, mode: sp.mode || 'apim' },
  };
} else if (vCheck.ok !== true) {
  const neverCalledDryRun = !validateResult;
  __agentResult = {
    __status: 'wip', ok: false, status: 'wip',
    reason: neverCalledDryRun
      ? 'R0 violation: agent emitted final YAML without ever calling catalog.validate / catalog.validate. No evidence to claim ok or wip.'
      : 'catalog.validate did not pass — refusing to persist OAM that fails dry-run',
    validate_diagnostics: (vCheck.reason || '').toString().slice(0, 4000),
    agent_picked_types: pickedTypes(oamYaml),
    agent: { turns_used: transcript.filter(t => t.role === 'assistant').length, transcript_brief: transcript },
    model: { deployment: DEPLOYMENT, mode: sp.mode || 'apim' },
  };
} else {
  // ── A5 defense-in-depth: stock-vendor image strings as `image:` values
  //    are forbidden. If the model slipped one in (despite the prompt
  //    saying not to), force WIP instead of persisting it.
  const stock = stockImageOffenders(oamYaml);
  if (stock.length > 0) {
    __agentResult = {
      __status: 'wip', ok: false, status: 'wip',
      reason: 'A5 violation: stock-vendor image strings detected in OAM — refusing to persist OAM that uses stock placeholders (' + stock.join(', ') + '). Use language:/framework: for platform auto-scaffold or surface a clarifying_question.',
      stock_image_offenders: stock,
      agent_picked_types: pickedTypes(oamYaml),
      clarifying_questions: (trailingJson && trailingJson.clarifying_questions) || [],
      agent: { turns_used: transcript.filter(t => t.role === 'assistant').length, transcript_brief: transcript },
      model: { deployment: DEPLOYMENT, mode: sp.mode || 'apim' },
    };
  } else {
    __agentResult = {
      __status: 'ok',
      oam: { yaml: oamYaml },
      dry_run: validateResult,
      submit: submitResult || (trailingJson && trailingJson.submit) || null,
      submit_wait: submitWaitResult || (trailingJson && trailingJson.submit_wait) || null,
      proposed_prs: (proposedPrs && proposedPrs.length) ? proposedPrs : ((trailingJson && trailingJson.proposed_prs) || []),
      capability_coverage: (trailingJson && trailingJson.capability_coverage) || null,
      placeholder_images: (trailingJson && trailingJson.placeholder_images) || [],
      clarifying_questions: (trailingJson && trailingJson.clarifying_questions) || [],
      agent: { turns_used: transcript.filter(t => t.role === 'assistant').length, transcript_brief: transcript },
      model: { deployment: DEPLOYMENT, mode: sp.mode || 'apim' },
    };
  }
}

} catch (e) {
  const status = e && e.httpStatus;
  const isRateLimit = status === 429 || status === 503;
  __agentResult = {
    __status: 'wip', ok: false,
    status: isRateLimit ? 'wip' : 'error',
    reason: isRateLimit
      ? ('AOAI/MCP transient failure (' + status + '). Try again in a minute.')
      : ('agent threw: ' + String((e && e.message) || e).slice(0, 600)),
    error: { message: String((e && e.message) || e).slice(0, 800), httpStatus: status || null, httpUrl: (e && e.httpUrl) || null },
    model: { deployment: sp.deployment_default, mode: sp.mode || 'apim' },
  };
}

return [{ json: { ...ctx, ...__agentResult } }];
