# local-ai-packaged within the CAFÉ & CAM Framework — and Coexistence with the Microsoft Ecosystem

*Analysis date: 2026-05-26. Sources: `CAFE_Framework_v0.2.docx`, `roadmap.html`, plus this repo's `README.md`, `docs/`, `graphify-out/GRAPH_REPORT.md`, and `.understand-anything/knowledge-graph.json`.*

---

## 1. Framework recap (so the mapping is grounded)

**CAFÉ** (Cognitive Architecture Framework for the Enterprise) extends classical BDAT for a world where agents behave probabilistically. It defines **seven domains** plus two cross-cutting planes:

| # | Domain | Owns |
|---|--------|------|
| 0 | **Foundation** | Metamodel, ontology of architectural elements, mandatory invariants, principles, the Architecture Board |
| 1 | **Business** | Capability map, value streams, processes, policies, KPIs (now with determinism tiers) |
| 2 | **Semantic** | The enterprise **ontology** — concepts, relationships, constraints, schema bindings (CAFÉ's headline addition to BDAT) |
| 3 | **Knowledge** | Knowledge bases, grounding sources, **retrieval contracts** |
| 4 | **Cognitive** | Agents, tools, prompts, **evaluation harness**, autonomy levels, safety bounds |
| 5 | **Application** | Deterministic + hybrid apps only (probabilistic systems move up to Cognitive) |
| 6 | **Technology** | Runtime, hosting, networking, **agent Identity** |

Cross-cutting planes: **Trust & Governance** (Agent 365, Entra Agent ID, Purview, Power Platform CoE, DLP, Responsible AI, evaluation harness) and **Stakeholder Concerns** (ISO 42010).

**Determinism spectrum:** Deterministic (Power Apps/Automate → traditional ALM) → Hybrid (Copilot Studio → mixed testing) → Probabilistic (Foundry / multi-agent → continuous evaluation, golden datasets, regression gates).

**Mandatory invariants** (the load-bearing ones for this analysis): every Action traces to an Identity; every Agent has exactly **one Identity** (Entra Agent ID or equivalent); every Agent grounds on Knowledge bases **via a Retrieval contract**; every Concept binds to a Data entity via a Schema binding; every Agent is measured by ≥1 Evaluation; **no model lock-in** (substitutability verified by evaluation).

**CAM** (CAFÉ Architecture Method) — the ADM analogue — runs **Phase 0 Concerns → 1 Business → 2 Semantic → 3 Knowledge → 4 Cognitive → 5 Application → 6 Technology → 7 Governance/Operate**, with a hard prerequisite chain (you cannot build an agent in P4 without P3 knowledge, which needs P2 ontology, etc.). The single most-cited failure mode is "skipping the ontology" and jumping straight to Phase 4.

**Operationalisation artifacts (interlocked):** **M1** archetype typology · **M2** decision tree (routing) · **M3** guardrails (invariants) · **M4** component capability map (closed set) · **M5** reference architectures (compose only M4 components, respect all M3 guardrails).

**Roadmap (`roadmap.html`, ADHDS/HSO, three parallel streams):**
- **Stream 1 — Delivery:** collect use cases → create solutions (architecture per case) → allocate to teams → prioritise → **implement Phase 1+2 (managed context → AI-augmented delivery)** → consolidate with Accenture → future rollout.
- **Stream 2 — Reference Architecture** (branches from Stream 1 step 2): preliminary architecture → Microsoft vendor baseline → consolidate/adapt to ADHDS → **automate architecture (agent-driven composition)**.
- **Stream 3 — Capability Procurement** (branches from Stream 2 step 8): identify capabilities → licenses/allocation → Microsoft training.

---

## 2. CAFÉ/CAM → local-ai-packaged component mapping

| CAFÉ/CAM element | local-ai-packaged component | Fit | Notes / gaps |
|---|---|---|---|
| **Foundation** — metamodel, ArchiMate/C4 model production, principles | OpenCode/Claude tooling generating **ArchiMate Exchange (.xml) + C4**; ADOIT/Archi tooling; `industry-config.json` capability/compliance/data/component knowledge | **Strong** | Produces the *modelling* substrate. Does not by itself enforce the CAFÉ metamodel/invariants — needs a conformance check step. |
| **Business** (P1) — capability map, AI-candidate flagging, determinism tiers | n8n **Business Analysis Pipeline** + BRD validation/router workflows; CTO/BA/Compliance/Business-Architect agents (TOGAF ADM cycle); industry capability models | **Strong** | Generates capability maps & PRDs. Does **not** auto-tag determinism tier per process — add explicitly. |
| **Semantic** (P2) — **ontology**, concepts, relationships, schema bindings | **Neo4j** knowledge graph (GraphRAG/LightRAG/Graphiti); healthcare (IFHAS/Sahatna) domain KBs; Data-Architect agent | **Partial→Strong** | Neo4j is the ideal home for a *real* CAFÉ ontology (relationships + constraints), but the repo today holds knowledge graphs/taxonomies, not a governed ontology with enforced rules. **This is the chief gap** — and the one CAFÉ warns is most damaging. |
| **Knowledge** (P3) — knowledge bases, grounding sources, **retrieval contracts** | **Qdrant** + **Supabase pgvector** RAG stores; **SearXNG** (web grounding); Open WebUI Knowledge Pipe; Local RAG agent workflow | **Strong (infra) / Weak (contract)** | Excellent grounding infrastructure. There is no formal *retrieval contract* abstraction — agents query stores directly. Add contracts to satisfy the invariant. |
| **Cognitive** (P4) — agents, tools, prompts, **evaluation**, autonomy, safety | **OpenCode multi-agent system** (ADM + Development cycles, specialist coders), **n8n** orchestration, **Flowise**, **Ollama** models, **Langfuse** (eval/observability), **Taskmaster** | **Very strong** | This is the heart of the stack. Langfuse covers the evaluation-harness invariant. Autonomy is largely L2–L3 (orchestrated, tool-using). Safety bounds/escalation playbooks are implicit, not formalised. |
| **Application** (P5) — deterministic/hybrid apps | n8n **deterministic workflows** (webhooks, routers, Azure DevOps mirroring), Software Delivery Pipeline → GitHub/GitOps/ArgoCD | **Strong** | n8n flows are textbook CAFÉ "Application" (deterministic tools invoked by Cognitive agents). |
| **Technology** (P6) — runtime, hosting, **Identity** | Docker Compose `localai` stack; **Caddy** reverse proxy/TLS; Ollama runtime; **Supabase Auth** (GoTrue/JWT) | **Strong (runtime) / Weak (agent identity)** | Solid sovereign runtime. Identity is *human/service* auth via Supabase JWT — there is **no per-agent first-class identity** (the Entra Agent ID equivalent). Violates the "one Identity per Agent" invariant as-is. |
| **Trust & Governance plane** | **Langfuse** (traces/evals), **Backstage** IDP (service catalog), Caddy boundary, Azure DevOps artifact mirroring | **Partial** | Observability + a catalog exist. Missing: DLP/content classification (Purview analogue), a unified agent control plane (Agent 365 analogue), Responsible-AI policy enforcement. |
| **Stakeholder Concerns plane (P0, ISO 42010)** | n8n intake/intent-routing workflows; PRD/BRD pipelines | **Partial** | Captures use cases; no formal stakeholder/concern register tying every artifact to a named concern. |
| **CAM operationalisation M1–M5** | TOGAF Multi-Agent EA Pipeline; intent classification/routing (≈M2); industry component types (≈M4); generated reference architectures/OAM specs (≈M5) | **Emergent** | The pipeline *shape* mirrors M1–M5 but the **interlock** (closed component set, guardrail invariants) is not enforced — drift is possible. |

**Overlaps with Microsoft:** RAG/vector (Qdrant/pgvector ↔ Azure AI Search), orchestration (n8n ↔ Power Automate), agent build (OpenCode/Flowise ↔ Copilot Studio/Foundry), catalog/governance (Backstage/Langfuse ↔ Agent 365/Purview), auth (Supabase ↔ Entra).

**Net gaps the local stack does NOT cover vs CAFÉ:** (a) a *governed* ontology with enforced rules (Semantic); (b) first-class per-agent identity (Technology invariant); (c) formal retrieval contracts (Knowledge invariant); (d) DLP/data-classification + a unified agent control plane (Governance); (e) explicit determinism-tier tagging and safety/escalation playbooks; (f) enforced M1–M5 interlock.

---

## 3. Where it sits on the roadmap

local-ai-packaged is overwhelmingly a **Stream 2 accelerator** and a **Stream 1 enabler**:

- **Stream 2 step 11 — "Automate architecture (agent-driven composition)":** this is a near-exact description of the OpenCode TOGAF ADM multi-agent pipeline that turns a use case into ArchiMate/C4 + PRD + reference architecture. The repo is arguably the *proof-of-concept implementation* of that milestone.
- **Stream 2 steps 8 & 10 — preliminary/ADHDS-adapted reference architecture:** the industry-config + capability-model knowledge bases and ArchiMate output directly produce these.
- **Stream 1 step 02 — "create solutions (architecture per case)" and step 05 — "implement Phase 1+2":** the BA→Architecture→Solution→Software-Delivery pipeline chain automates exactly this hand-off, all the way to GitOps.
- It does **not** advance Stream 3 (procurement/licensing/Microsoft training) — that is organisational/commercial.

In short: it is the **sovereign, low-cost engine that de-risks and pre-builds the agent-driven reference-architecture milestone** before (or alongside) the Microsoft vendor baseline arrives.

---

## 4. Coexistence with the Microsoft ecosystem

### Verdict
**Yes — they can and should coexist, as two tiers under one governance and one catalog.** *Why in one sentence:* local-ai-packaged is the **sovereign / offline / low-cost build-and-experiment tier** (and an automation engine for the architecture pipeline itself), while Azure AI Foundry / Copilot Studio / Power Platform is the **governed production tier** — and CAFÉ's own "no model lock-in + substitutability" principle makes running both not just tolerable but *desirable*.

### Concrete integration points
- **n8n ↔ Power Automate / Azure DevOps:** already real — every architecture pipeline mirrors artifacts to **Azure DevOps repos** in parallel with GitHub (`docs/azure-devops-setup.md`). Extend with: n8n webhooks → Power Automate flows (and back), and n8n → Azure DevOps **work items/wiki** so generated PRDs/architectures become tracked backlog. This makes n8n the *deterministic-Application* glue spanning both estates.
- **Inference tiers (Ollama ↔ Foundry/Copilot Studio):** Ollama = the **sovereign/offline/air-gapped + zero-marginal-cost** inference tier for sensitive data, bulk batch generation, and dev iteration; Foundry/Copilot Studio = the **governed, frontier-model production tier**. CAFÉ's substitutability invariant means an agent spec should run against either — use the **Langfuse evaluation harness as the shared gate** that proves a Foundry agent and an Ollama agent meet the same golden-dataset bar before promotion.
- **Vector / RAG (Qdrant + pgvector ↔ Azure AI Search):** keep Qdrant/pgvector for local, sovereign, and dev RAG; promote production grounding indexes to **Azure AI Search** where Entra-scoped security trimming and Purview classification are required. Same documents, two indexes — bound by a **retrieval contract** that records which store, which filter, which classification (closes the CAFÉ Knowledge invariant on both sides).
- **Observability (Langfuse across both):** point **both** local agents and Foundry/Copilot Studio agents at Langfuse (OpenTelemetry) for a single trace/eval surface. This is the one component that should *not* be duplicated — unify it.
- **Backstage as the IDP catalog over both:** register local services *and* Foundry/Copilot Studio agents, n8n flows, and Power Automate flows as catalog entities. Backstage becomes the cross-cloud **Agent 365 analogue** for discovery (note: it catalogs, it does not enforce — Agent 365/Purview still own enforcement on the Microsoft side).
- **Identity (Entra ID ↔ Supabase Auth):** make **Entra ID the authority**. Federate Supabase Auth (OIDC) to Entra so local-stack human access uses corporate identity. For *agents*, issue **Entra Agent IDs** to anything that touches production data; treat Supabase-JWT-only agents as confined to the local/dev tier and never granted production scopes.

### Division of responsibility (what runs where, and why)

| Concern | Run local (local-ai-packaged) | Run cloud (Microsoft) | Why |
|---|---|---|---|
| Sensitive / un-clearable data inference | ✅ Ollama | — | Data sovereignty, no egress |
| Architecture-pipeline automation (PRD→ArchiMate→ref arch) | ✅ n8n + OpenCode | (mirror artifacts to ADO) | Cost, speed, iteration |
| Dev/experiment RAG & agents | ✅ Qdrant/pgvector/Flowise | — | Zero marginal cost, fast loop |
| Production business agents | — | ✅ Copilot Studio / Foundry | Governance, SLA, Entra/Purview |
| Production grounding with security trimming | — | ✅ Azure AI Search | Entra-scoped, classified |
| Deterministic enterprise workflow | n8n (dev/glue) | ✅ Power Automate (prod) | ALM + CoE governance |
| Identity authority | federate to Entra | ✅ Entra (incl. Agent ID) | Single principal model (CAFÉ invariant) |
| Evaluation & observability | Langfuse (shared) | feed into Langfuse | One eval gate across tiers |
| Data classification / DLP | — | ✅ Purview / DLP | No local equivalent |

### Trust boundaries & data-flow
- **Caddy is the local trust boundary.** In `public` mode only 80/443 are exposed; treat the local stack as a network enclave. Cloud↔local traffic should be one-way push of *artifacts/telemetry* (n8n → ADO, agents → Langfuse), not inbound cloud calls into the enclave.
- **Classification gate before promotion:** data may flow local→cloud only after Purview classification; sensitive-classified data stays in the Ollama/Qdrant enclave. Never let a Supabase-JWT-only agent obtain a production Entra token.

### Risks / anti-patterns
- **Anti-pattern: skipping the ontology** (CAFÉ's #1 failure). The repo has knowledge graphs but not a governed Neo4j ontology with rules — fix before scaling agents.
- **Anti-pattern: agents without identity.** Supabase JWT ≠ Entra Agent ID. Don't promote a local agent to production without a first-class identity.
- **Anti-pattern: two divergent observability/eval stacks.** Unify on Langfuse, or you cannot prove substitutability.
- **Anti-pattern: shadow governance.** A local stack that bypasses Purview/DLP/Power Platform CoE is exactly the ungoverned proliferation CAFÉ exists to prevent. Keep local strictly non-production for regulated data.
- **Risk: model-tier drift.** Without a shared golden dataset, local and cloud agents silently diverge.

### Recommended coexistence topology
```
                 ┌──────────────────────── Backstage IDP (catalog over BOTH) ────────────────────────┐
                 │                                                                                    │
   ┌─────────────┴─────────────┐   artifacts (n8n→ADO)   ┌──────────────────────────────────────────┐ │
   │  LOCAL ENCLAVE (Caddy)    │  ───────────────────►   │  MICROSOFT GOVERNED TIER                 │ │
   │  • OpenCode multi-agent   │                          │  • Copilot Studio (hybrid agents)        │ │
   │  • n8n (dev + glue)       │   webhooks ◄────────►   │  • Azure AI Foundry (pro-code agents)    │ │
   │  • Ollama (sovereign LLM) │                          │  • Power Automate (prod deterministic)   │ │
   │  • Qdrant / pgvector RAG  │   promote indexes ───►   │  • Azure AI Search (prod grounding)      │ │
   │  • Neo4j  → ONTOLOGY      │                          │  • SharePoint / Azure DevOps             │ │
   │  • Supabase Auth (fed.)   │   ◄── Entra OIDC fed. ── │  • Entra ID + Entra Agent ID (authority) │ │
   └──────────────┬────────────┘                          │  • Purview / DLP / Agent 365 (enforce)   │ │
                  │   OpenTelemetry traces + evals         └──────────────────┬───────────────────────┘ │
                  └────────────────────►  Langfuse (single shared eval/observability surface)  ◄────────┘
```

---

## 5. Opinionated recommendation

**Keep the local stack — but reframe it.** Its highest-value role is **not** as a parallel production agent platform; it is (1) the **agent-driven architecture-composition engine** that fulfils roadmap Stream 2 step 11 *today*, and (2) the **sovereign experimentation + offline-inference tier** for the Microsoft platform. Do three things to make it CAFÉ-conformant and a clean Microsoft citizen:

1. **Promote Neo4j from knowledge graph to a governed ontology** (concepts + relationships + constraints) — this closes the framework's most damaging gap and is the prerequisite for everything downstream.
2. **Unify identity and evaluation:** federate Supabase Auth to **Entra ID**, give any production-bound agent an **Entra Agent ID**, and make **Langfuse the single golden-dataset eval gate** that proves model substitutability across the local↔cloud tiers.
3. **Treat local as non-production for regulated data:** classify via Purview before any local→cloud promotion, catalog both estates in Backstage, and route deterministic production work to Power Automate under the Power Platform CoE.

Done this way, local-ai-packaged isn't a competitor to the Microsoft estate — it's the **fast, sovereign R&D + architecture-automation lab that feeds it**, and CAFÉ's own anti-lock-in stance turns that duality into an asset.
