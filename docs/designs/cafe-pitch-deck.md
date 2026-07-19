# CAFE — Governed AI Adoption, Turnkey
### 1–2 page pitch deck · structured on the Minto Pyramid Principle (SCQA)

---

## Elevator pitch

> We solve **the gap between AI ambition and governed delivery** — where adoption stalls in pilots, slideware, and ungoverned shadow AI — by **turning a use case into a running, governed architecture across both AI and traditional workloads, on sovereign or cloud infrastructure.** Unlike **AI platforms that hand you a toolbox, systems integrators that hand you a slide deck, and governance tools that only say "no" after the fact**, we **generate governance as the system composes itself and provision it into live infrastructure — we create *and* implement, with no lock-in** — which brings **a governed, production-ready system in days, not quarters.** So — **how does your organisation get from an AI use case to a governed, running system today, and how long does that take?**

| Slot | Fill (refine each independently) |
|---|---|
| **Problem** | AI ambition stalls before governed delivery — pilots, slideware, ungoverned shadow AI |
| **What it does** | Turns a use case into a running, governed architecture — AI + traditional, sovereign or cloud |
| **Competitors** | AI platforms — IBM watsonx, Microsoft Azure AI Foundry, Amazon Bedrock, Google Vertex AI (a toolbox); systems integrators — Accenture, Deloitte (a slide deck); governance point-tools — Credo AI, Holistic AI, Modulos (an after-the-fact gate) |
| **What's unique** | Governance-as-generator + create *and* implement (application manifest → running infrastructure), no lock-in |
| **Primary benefit** | Governed, production-ready system in days, not quarters |
| **Open question** | "How do you get from an AI use case to a governed, running system today — and how long does it take?" |

*The data behind "it's breaking them" (88% adopted / 21% trust governance / 79% struggling / 54% "tearing the company apart") is in the Supporting Data section below — use it to open the Complication.*

---

## The offering

**What it is:** an AI-adoption operating system built on a proven method — **CAFE** (Composable AI Framework for Enterprise: 7 governed domains) and its companion adoption method (**CAM**) — sitting on three working systems: a **sovereign stack** (n8n + Ollama, self-hosted), an **enterprise stack** (Microsoft Azure AI Foundry / Copilot Studio / Power Platform + data-loss prevention), and an **implementation runtime** (KubeVela / ArgoCD / Azure Kubernetes Service) that turns the generated architecture into live infrastructure.

**Two ways to buy** (same demo sells both):
- **Product Offer** — the platform. You run it; it generates and implements governed architectures on demand.
- **Framework Offer** — adoption + consultancy / intellectual-property licensing. We help you adopt CAFE, or license the method.

**Why it wins (three things no competitor combines):**
1. **Governance-as-generator, not governance-as-veto** — governance is the *output* of composition, visible live, not an audit that says "no" later.
2. **No lock-in** — the same use case renders sovereign *or* cloud; substitutable by design.
3. **Creates *and* implements** — use case → governed architecture → *running platform*. Not a deck. For AI *and* traditional work.

---

## The storyline (SCQA — Minto Pyramid Principle)

> *Pyramid Principle: lead with the answer, support it with the structure. SCQA (Situation, Complication, Question, Answer) frames the problem before the answer; the executive-summary compression SCR is Situation → Challenge (Complication) → Solution (Resolution).*

**S — Situation** *(what everyone agrees on)*
AI adoption is now mandatory. 88% of enterprises have deployed AI in at least one major business area; boards and chief executives are demanding scale.

**C — Complication** *(the problem / urgency)*
Adoption is failing at the point of governance and delivery:
- Only **21%** of organisations are fully confident in their AI governance model.
- **79%** report struggling with adoption — a double-digit jump year over year.
- **54%** of senior executives say adopting AI is "tearing the company apart."
- The available answers force a bad trade-off: **buy a platform** (IBM watsonx, Azure AI Foundry, Amazon Bedrock — vendor lock-in, your data leaves your boundary) **or hire a systems integrator** (Accenture, Deloitte — slow, bespoke per use case, ends in a slide deck). Governance tooling (Credo AI, Holistic AI, Modulos) is sold as an after-the-fact **gate**. **Nobody connects** *use case → governed architecture → running system.*

**Q — Question** *(what the audience now asks)*
How do we adopt AI **fast and governed** — without lock-in, across both AI and traditional workloads — and end up with a **running system**, not another slide deck?

**A — Answer** *(the main idea — top of the pyramid)*
**CAFE.** A turnkey, governed platform that **generates the governed architecture and implements it** — sovereign or enterprise, AI or traditional. Governance is produced as the system is composed (visible on a live scorecard), the architecture is provisioned into running infrastructure, and your team is left to add only the business logic. We prove it by taking a use case to a **running, governed platform in the room.**

---

## The demo (the proof) — operational use case: **Accounts-Payable invoice exception handling**

**Why this use case (the sweet spot):** every enterprise pays invoices, so the audience believes it instantly. It splits cleanly into a **deterministic traditional backbone** (the perfect showcase for application-manifest auto-provisioning) and a **genuinely agentic** layer (judgment + tool use + drafting — not a classification model). It also resolves the anomaly-detection trap: **detection/matching is deterministic; the *resolution* is agentic.**

**The two halves — and how each is automated:**
- **Traditional (deterministic → the application manifest provisions it live):** invoice intake service → document text extraction (optical character recognition) → Postgres store → **3-way match** (purchase order ↔ goods-receipt ↔ invoice) → enterprise-resource-planning integration → message queue → approval-queue screen. The application manifest (an **Open Application Model** file) describes it; the implementation runtime applies it. *The deterministic-automation showcase.*
- **AI (agentic):** on a match failure or ambiguity (the exception), an agent investigates purchase-order history + contract terms + vendor correspondence, **decides** (approve-within-tolerance / request-correction / route-to-human-with-recommendation), **drafts the vendor email**, and logs its rationale. Composed via **Microsoft Azure AI Foundry / Copilot Studio** (enterprise tier) or **Claude Code / local agents** (sovereign tier).
- **Governance (live scorecard):** vendor personally-identifiable-information protection (data-loss prevention), per-agent identity, an evaluation gate on decision quality, an audit trail, and CAFE-domain coverage.
- **Presentation:** an accounts-payable clerk sees an exception queue with the agent's recommendation + rationale + one-click approve.

**Beats:**
1. **Drop in the use case** — "automate accounts-payable invoice processing."
2. **Watch it compose** — CAFE generates the architecture (ontology → business & product requirement documents → architecture models in ArchiMate / C4 notation → application manifest); the **governance scorecard fills in live** (identity, data-loss prevention, evaluation coverage, CAFE 7-domain maturity). *Governance, felt — not claimed.*
3. **Same use case, two tiers, side by side** — sovereign (local) ↔ enterprise (your Azure). *Lock-in fear, answered visually.*
4. **It implements itself** — the application manifest → the implementation runtime provisions the **deterministic backbone live** (intake / text-extraction / store / match / enterprise-resource-planning / approval queue); the **agent layer** wires in via Azure AI Foundry / Copilot Studio (enterprise) or Claude Code / local agents (sovereign). *Two automation modes, one governed system.*
5. **AI *and* traditional, in one run** — a clean invoice **auto-matches** (traditional); a mismatched one **triggers the agent** → investigate → recommend → draft vendor email (AI); the clerk **approves in the user interface** (presentation). *Not just an AI toy.*
6. **Close:** "your team owns the business rules and edge policy." Present the **Product Offer** and **Framework Offer**.

**Architectural punchline:** the application manifest automates the *traditional* architecture deterministically; the *AI* components are composed via Azure AI Foundry / Copilot Studio or Claude Code / local agents — the same CAFE method governs both halves.

*Demo safety:* present the highest reliably-ready tier; a control-room fallback drops to a pre-built walkthrough if a live step stumbles.

*Alternative use cases (same shape — deterministic detect, agentic decide): order/fulfillment exception management; information-technology incident triage.*

---

## Supporting data

| Metric | Figure | So what |
|---|---|---|
| Enterprises with AI in ≥1 major function | **88%** | The market has already bought in — the fight is adoption quality, not interest |
| Orgs fully confident in AI governance | **21%** | The governance gap is the wound; governance-as-generator is the bandage |
| Orgs struggling with adoption | **79%** (↑ double digits year over year) | The pain is growing, not shrinking — urgency is real |
| Senior executives saying AI is "tearing the company apart" | **54%** | This is a boardroom-level problem with budget behind it |
| Lock-in / sovereignty | rising driver | Open-weight + self-host momentum validates the dual-tier, no-lock-in stance |

**Sources:** [WRITER — Enterprise AI adoption 2026 (79%, 54%)](https://writer.com/blog/enterprise-ai-adoption-2026/) · [Adoptify AI — governance-led adoption (88%, 21%)](https://www.adoptify.ai/blogs/a-governance-led-ai-adoption-framework-for-enterprises/) · [Kai Waehner — Agentic AI Landscape 2026 (lock-in, trust)](https://www.kai-waehner.de/blog/2026/04/06/enterprise-agentic-ai-landscape-2026-trust-flexibility-and-vendor-lock-in/) · Methodology: [Minto Pyramid & SCQA — ModelThinkers](https://modelthinkers.com/mental-model/minto-pyramid-scqa)

---
*Roadmap and scope: see `cafe-productization.md` (this folder). Framework fit & Microsoft coexistence: see `../CAFE-CAM-local-ai-fit.md`.*
