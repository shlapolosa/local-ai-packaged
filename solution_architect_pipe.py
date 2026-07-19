"""
title: Solution Architect (OAM)
author: socrates (modelled on architecture_pipeline_pipe.py)
version: 1.0.0

Open WebUI Function that talks to the n8n "Solution Architect - OAM" workflow.

Accepts three intents (parsed from the chat message):
    oam <slug>         — generate the OAM YAML only
    provision <slug>   — generate AND submit for provisioning via app.submit
    both <slug>        — same as provision (validate + submit)
    help               — usage card

The webhook is synchronous: each call returns the full OAM YAML + dry-run
report inline; the document is also persisted in Postgres
`architecture.artifacts` as `type=oam_application`.

INSTALL: Open WebUI -> Workspace -> Functions -> "+" -> paste -> Save -> enable.
"""

from typing import Optional, Callable, Awaitable
from pydantic import BaseModel, Field
import os
import re
import json
import time
import requests


def _extract_event_info(ee):
    if not ee or not getattr(ee, "__closure__", None):
        return None, None
    for cell in ee.__closure__:
        if isinstance(info := cell.cell_contents, dict):
            return info.get("chat_id"), info.get("message_id")
    return None, None


class Pipe:
    class Valves(BaseModel):
        webhook_url: str = Field(
            default="http://n8n:5678/webhook/solution-architect-oam",
            description="n8n webhook that runs the solution-architect agent.",
        )
        n8n_bearer_token: str = Field(default="", description="Optional Bearer token for n8n.")
        timeout_seconds: int = Field(default=900, description="Max wait for the synchronous webhook (s).")
        task_model: str = Field(
            default="llama3.2:3b",
            description="Small/fast model for Open WebUI labelling tasks (title/tags/follow-up).",
        )
        task_chat_url: str = Field(
            default="http://host.docker.internal:11434/api/chat",
            description="Chat endpoint for the labelling model. Local native Ollama by default.",
        )

    def __init__(self):
        self.type = "pipe"
        self.id = "solution_architect"
        self.name = "Solution Architect (OAM)"
        self.valves = self.Valves()

    # ---- helpers -------------------------------------------------------------
    async def _emit(self, ee, message, done=False, level="info"):
        if ee:
            await ee({"type": "status", "data": {
                "status": "complete" if done else "in_progress",
                "level": level, "description": message, "done": done}})

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.valves.n8n_bearer_token:
            h["Authorization"] = f"Bearer {self.valves.n8n_bearer_token}"
        return h

    def _cloud_key(self):
        return os.environ.get("OPENAI_API_KEY") or os.environ.get("OLLAMA_API_KEY") or ""

    def _label(self, prompt: str) -> str:
        want_json = "json" in prompt.lower()
        body = {"model": self.valves.task_model, "stream": False,
                "messages": [{"role": "user", "content": prompt}], "options": {"temperature": 0.2}}
        if want_json:
            body["format"] = "json"
        try:
            r = requests.post(self.valves.task_chat_url, json=body, timeout=60,
                              headers={"Content-Type": "application/json",
                                       "Authorization": f"Bearer {self._cloud_key()}"})
            if r.status_code == 200:
                return (r.json().get("message", {}) or {}).get("content", "") or ""
        except requests.RequestException:
            pass
        return ""

    def _help_text(self) -> str:
        return (
            "## 🧰 Solution Architect — Help\n\n"
            "👋 I take a project's architecture artifacts (produced by the Architecture Pipeline) "
            "and turn them into an executable **OAM Application** using only components published "
            "by the live capability catalog. Optionally I submit it for provisioning.\n\n"
            "### 🚀 Commands\n"
            "- `oam <slug>` — compose + `oam.dry_run` only. No submit, no propose.\n"
            "- `provision <slug>` — compose, dry-run, then `app.submit` if it passes.\n"
            "- `provision_wait <slug>` — same but `app.submit_wait` if a CD is missing "
            "(commits the OAM and polls vela dry-run for up to 72 h before deploying).\n"
            "- `propose <slug>` — compose, dry-run; for any unmappable capability, "
            "file a `factory.propose` PR (one per gap).\n"
            "- `both <slug>` — alias for `provision`.\n"
            "- `help` — show this card.\n\n"
            "### 📦 Output\n"
            "1. 🧾 KubeVela OAM Application (`apiVersion: core.oam.dev/v1beta1`).\n"
            "2. ✅ `catalog.validate` dry-run report.\n"
            "3. 🚚 If provisioning: `app.submit` tracking info.\n\n"
            "### 💾 Where it lands\n"
            "Postgres `architecture.artifacts` as `type=oam_application` (auto-versioned). "
            "Retrieve via `architecture-artifact-v2?projectSlug=&type=oam_application`.\n"
        )

    _CMD = re.compile(
        r"^\s*(oam|provision_wait|provision|propose|both)\s+([A-Za-z0-9][A-Za-z0-9_\-]*)\s*$",
        re.IGNORECASE,
    )

    def _parse(self, msg: str):
        m = self._CMD.match(msg or "")
        if not m:
            return None, None
        intent = m.group(1).lower()
        slug = m.group(2).strip()
        # `both` is a legacy alias for `provision`. `propose` and
        # `provision_wait` pass through verbatim (handled by the agent).
        if intent == "both":
            intent = "provision"
        return intent, slug

    def _render_response(self, j: dict) -> str:
        lines = []
        slug = j.get("projectSlug") or "?"
        version = j.get("version")
        intent = j.get("intent")
        lines.append(f"## ✅ OAM generated — **{slug}** (v{version}, intent: `{intent}`)\n")
        yaml_str = (j.get("oam") or {}).get("yaml", "")
        lines.append("```yaml")
        lines.append(yaml_str)
        lines.append("```")
        dry = j.get("dry_run")
        if dry:
            text = ""
            if isinstance(dry, dict):
                content = dry.get("content")
                if isinstance(content, list) and content and isinstance(content[0], dict):
                    text = content[0].get("text", "")
                else:
                    text = json.dumps(dry, indent=2)
            else:
                text = str(dry)
            preview = text if len(text) <= 1500 else (text[:1500] + "\n…")
            lines.append("\n<details><summary>🔬 Dry-run report (vela)</summary>\n\n```\n" + preview + "\n```\n</details>")
        sub = j.get("submit")
        if sub:
            lines.append("\n<details><summary>🚚 Provision submission (`app.submit`)</summary>\n\n```json\n" + json.dumps(sub, indent=2)[:1500] + "\n```\n</details>")
        subw = j.get("submit_wait")
        if subw:
            lines.append("\n<details><summary>⏳ Submit-wait queued (`app.submit_wait`)</summary>\n\n```json\n" + json.dumps(subw, indent=2)[:1500] + "\n```\n</details>")
        prov = j.get("provision")  # legacy field name
        if prov and not sub:
            lines.append("\n<details><summary>🚚 Provision submission</summary>\n\n```json\n" + json.dumps(prov, indent=2)[:1500] + "\n```\n</details>")
        prs = j.get("proposed_prs") or []
        if prs:
            lines.append("\n### 📝 Proposed PRs")
            for pr in prs:
                # Unwrap MCP {content:[{text:"<json>"}]} shape if present
                pr_obj = pr
                if isinstance(pr, dict) and isinstance(pr.get("content"), list) and pr["content"]:
                    inner = pr["content"][0].get("text", "")
                    try:
                        pr_obj = json.loads(inner)
                    except Exception:
                        pr_obj = {"raw": inner}
                url = pr_obj.get("pr_url") or pr_obj.get("html_url") or pr_obj.get("url")
                title = pr_obj.get("title") or pr_obj.get("branch") or "(no title)"
                if url:
                    lines.append(f"- [{title}]({url})")
                else:
                    lines.append(f"- {title}\n  ```json\n{json.dumps(pr_obj, indent=2)[:600]}\n  ```")
        cov = j.get("capability_coverage") or []
        if cov:
            lines.append(f"\n_Mapped {len(cov)} capability(ies)._")
        turns = (j.get("agent") or {}).get("turns_used")
        if turns is not None:
            lines.append(f"_Agent used {turns} turn(s)._")
        return "\n".join(lines)

    # ---- main ---------------------------------------------------------------
    async def pipe(self, body: dict, __user__: Optional[dict] = None,
                   __event_emitter__: Callable[[dict], Awaitable[None]] = None,
                   __event_call__: Callable[[dict], Awaitable[dict]] = None) -> str:
        messages = body.get("messages", [])
        if not messages:
            return ""
        user_message = messages[-1].get("content", "")

        # 1) Open WebUI background tasks → small model (labelling), do NOT run the workflow.
        task = (body.get("metadata") or {}).get("task")
        if task or user_message.lstrip().startswith("### Task:"):
            return self._label(user_message)

        # 2) Help intercept.
        msg_norm = user_message.strip().lower().rstrip("?").strip()
        if msg_norm in {"help", "/help", "hints", "hint", "usage", "commands", "info",
                        "what can you do", "what can it do"} or msg_norm.startswith(("help ", "/help")):
            await self._emit(__event_emitter__, "Help", done=True)
            return self._help_text()

        # 3) Parse <intent> <slug>
        intent, slug = self._parse(user_message)
        if not intent or not slug:
            return ("❓ I couldn't parse a command. Try:\n"
                    "- `oam <project-slug>`\n"
                    "- `provision <project-slug>`\n"
                    "- `both <project-slug>`\n"
                    "- `help`")

        await self._emit(__event_emitter__, f"Running solution architect agent on `{slug}` (intent: `{intent}`)…")
        payload = {"projectSlug": slug, "intent": intent}
        try:
            resp = requests.post(self.valves.webhook_url, json=payload,
                                 headers=self._headers(), timeout=self.valves.timeout_seconds)
        except requests.RequestException as e:
            await self._emit(__event_emitter__, f"Error reaching n8n: {e}", True, "error")
            return f"⚠️ Failed to reach n8n: {e}"

        if resp.status_code >= 400:
            await self._emit(__event_emitter__, f"Webhook error {resp.status_code}", True, "error")
            return f"⚠️ Webhook error {resp.status_code}: ```\n{resp.text[:800]}\n```"

        try:
            j = resp.json()
        except ValueError:
            await self._emit(__event_emitter__, "Bad response body", True, "error")
            return f"⚠️ Bad response from n8n: ```\n{resp.text[:800]}\n```"

        if not j.get("ok"):
            # WIP path — agent could not produce an OAM that passes catalog.validate.
            # Strict policy: no fabrication, no DB write. Render a clean banner.
            if j.get("status") == "wip":
                await self._emit(__event_emitter__, "WIP — escalation needed", True, "warning")
                picks = j.get("agent_picked_types") or []
                picks_md = ", ".join(f"`{t}`" for t in picks) if picks else "_(none)_"
                diag = (j.get("validate_diagnostics") or "").strip()
                model = j.get("model") or {}
                mode = model.get("mode", "apim")
                turns = (j.get("agent") or {}).get("turns_used")
                note = j.get("note") or ""

                parts = [
                    f"## 🚧 WIP — `{j.get('projectSlug')}` (intent: `{j.get('intent')}`)\n",
                    "**The agent could not produce an OAM that passes `catalog.validate`.** "
                    "No OAM was persisted (strict catalog-or-fail policy).\n",
                    f"- **Reason:** {j.get('reason')}",
                    f"- **Agent picked types:** {picks_md}",
                    f"- **Turns used:** {turns}",
                    f"- **Model:** `{model.get('deployment')}` (mode: `{mode}`)\n",
                ]

                mapped = j.get("mapped_capabilities") or []
                if mapped:
                    parts.append("### ✓ Mapped capabilities")
                    for c in mapped:
                        if isinstance(c, dict):
                            parts.append(
                                f"- {c.get('capability','')} → "
                                f"`{c.get('component_name','')}` (`{c.get('type','')}`)"
                            )
                        else:
                            parts.append(f"- {c}")
                    parts.append("")

                unmappable = j.get("unmappable_capabilities") or []
                if unmappable:
                    parts.append("### ✗ Unmappable capabilities")
                    for c in unmappable:
                        if not isinstance(c, dict):
                            parts.append(f"- {c}")
                            continue
                        tried = c.get("tried_components") or []
                        tried_md = (
                            ", ".join(f"`{t}`" for t in tried) if tried else "_(none)_"
                        )
                        parts.append(
                            f"- **{c.get('capability','')}** — tried: {tried_md}\n"
                            f"  - _why:_ {c.get('why','')}"
                        )
                    parts.append("")

                drafts = j.get("factory_propose_drafts") or []
                if drafts:
                    parts.append("### 📝 Factory PR drafts (not filed)")
                    parts.append(
                        "_Re-run with `intent=propose` to actually open these PRs._"
                    )
                    for d in drafts:
                        if not isinstance(d, dict):
                            continue
                        title = d.get("title") or "(no title)"
                        repo = d.get("repo") or ""
                        files = list((d.get("files") or {}).keys())
                        parts.append(f"- **{title}** → `{repo}`")
                        for f in files:
                            parts.append(f"  - `{f}`")
                    parts.append("")

                if diag:
                    diag_preview = diag if len(diag) <= 1500 else (diag[:1500] + "\n…")
                    parts.append(
                        "<details><summary>🔬 catalog.validate diagnostics</summary>\n\n"
                        "```\n" + diag_preview + "\n```\n</details>"
                    )

                if note:
                    parts.append(f"\n> {note}")

                return "\n".join(parts)
            await self._emit(__event_emitter__, "Agent reported failure", True, "error")
            return f"⚠️ Agent failed: ```json\n{json.dumps(j, indent=2)[:1500]}\n```"

        await self._emit(__event_emitter__,
                         f"Done — version {j.get('version')}, {(j.get('agent') or {}).get('turns_used')} agent turn(s).",
                         True)
        return self._render_response(j)
