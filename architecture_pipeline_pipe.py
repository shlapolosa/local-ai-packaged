"""
title: Architecture Pipeline (n8n)
author: adapted from Cole Medin's n8n_pipe
version: 1.3.0

Open WebUI pipe for the self-contained "Architecture Pipeline - AI Agent" n8n workflow.
Handles three request kinds:
  1. Open WebUI background TASKS (title / tags / follow-up / query generation) -> answered by a
     small fast model (so conversation labelling works), WITHOUT firing the pipeline.
  2. "help" / "?" / "what can you do" -> usage text.
  3. A real use-case / requirements brief -> fires POST /webhook/architecture-pipeline (async),
     polls the artifact-get webhook, and streams progress. Each run gets a UNIQUE, meaningful slug.

INSTALL: Open WebUI -> Workspace -> Functions -> "+" -> paste -> Save -> enable.
"""

from typing import Optional, Callable, Awaitable
from pydantic import BaseModel, Field
import time
import json
import re
import os
import base64
import requests

STAGES = [
    ("Business Requirements", "brd"),
    ("Business Architecture", "business_arch"),
    ("Application Architecture", "application_arch"),
    ("Data Architecture", "data_arch"),
    ("Infrastructure Architecture", "infrastructure_arch"),
    ("Risk Assessment", "risk_assessment_md"),
    ("Solution Package", "solution_arch_md"),
    ("Test Strategy", "test_strategy_md"),
]


def extract_event_info(event_emitter):
    if not event_emitter or not getattr(event_emitter, "__closure__", None):
        return None, None
    for cell in event_emitter.__closure__:
        if isinstance(info := cell.cell_contents, dict):
            return info.get("chat_id"), info.get("message_id")
    return None, None


class Pipe:
    class Valves(BaseModel):
        webhook_url: str = Field(
            default="http://n8n:5678/webhook/architecture-pipeline",
            description="n8n webhook that starts the architecture pipeline (async).",
        )
        n8n_base_url: str = Field(
            default="http://n8n:5678", description="Base URL of n8n for polling artifacts."
        )
        artifact_path: str = Field(
            default="/webhook/architecture-artifact-v2",
            description="Artifact-get webhook path (returns {ok, artifact}).",
        )
        input_field: str = Field(default="requirements", description="Payload field for the use case.")
        default_project_name: str = Field(
            default="", description="Optional fixed project name prefix; blank = derive from the text."
        )
        n8n_bearer_token: str = Field(default="", description="Optional Bearer token for n8n.")
        poll_for_artifacts: bool = Field(default=True, description="Poll + stream artifact progress.")
        max_wait_seconds: int = Field(default=1200, description="Max poll time (s).")
        poll_interval: float = Field(default=10.0, description="Seconds between polls.")
        task_model: str = Field(
            default="llama3.2:3b",
            description="Small/fast model for Open WebUI labelling tasks (title/tags/follow-up).",
        )
        task_chat_url: str = Field(
            default="http://host.docker.internal:11434/api/chat",
            description="Chat endpoint for the labelling model. Local native Ollama by default so "
            "labelling never contends with the cloud pipeline generation.",
        )

    def __init__(self):
        self.type = "pipe"
        self.id = "architecture_pipeline"
        self.name = "Architecture Pipeline"
        self.valves = self.Valves()

    # ---- helpers -------------------------------------------------------------
    async def emit(self, ee, message, done=False, level="info"):
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
        """Answer an Open WebUI task prompt with a small fast model (for title/tags/follow-up)."""
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
            "## 🏛️ Architecture Pipeline — Help\n\n"
            "👋 I turn a **use case** into a complete, governed architecture — generated stage by "
            "stage and saved to the Postgres `architecture` schema.\n\n"
            "### 🚀 How to use\n"
            "Type your use case (a paragraph is plenty), or 📎 attach a requirements document. "
            "I run the pipeline and stream progress here.\n\n"
            "### 💡 Example\n"
            "> *Build an accounts-payable invoice processing service: ingest invoices, match them to "
            "purchase orders, auto-approve clean matches, and route exceptions to an AI agent.*\n\n"
            "### 📦 What you get\n"
            "1. 📋 Business Requirements (BRD)\n"
            "2. 🧩 Business → Application → Data → Infrastructure architecture (+ 🗺️ ArchiMate XML)\n"
            "3. ⚠️ Risk assessment\n"
            "4. 🛠️ Solution package, 📝 PRD, and ✅ QA / test strategy\n\n"
            "### ⏱️ Good to know\n"
            "Runs **asynchronously** (a few minutes on cloud ☁️) — artifacts appear as each stage "
            "completes. Type `help` anytime to see this again.\n"
        )

    def _extract_file(self, messages) -> Optional[str]:
        for msg in messages:
            for f in msg.get("files", []) or []:
                data = f.get("data")
                if not data:
                    continue
                if isinstance(data, str) and data.startswith("data:") and "," in data:
                    try:
                        return base64.b64decode(data.split(",", 1)[1]).decode("utf-8")
                    except Exception:
                        return data
                if isinstance(data, str):
                    return data
        return None

    def _get_artifact(self, project_slug, art_type):
        try:
            url = self.valves.n8n_base_url.rstrip("/") + self.valves.artifact_path
            r = requests.get(url, params={"projectSlug": project_slug, "type": art_type},
                             headers=self._headers(), timeout=30)
            if r.status_code == 200 and r.text.strip():
                return r.json()
        except (requests.RequestException, ValueError):
            pass
        return None

    # ---- main ---------------------------------------------------------------
    async def pipe(self, body: dict, __user__: Optional[dict] = None,
                   __event_emitter__: Callable[[dict], Awaitable[None]] = None,
                   __event_call__: Callable[[dict], Awaitable[dict]] = None) -> str:
        messages = body.get("messages", [])
        if not messages:
            return ""
        user_message = messages[-1].get("content", "")
        chat_id, _ = extract_event_info(__event_emitter__)

        # 1) Open WebUI background tasks -> small model (labelling), do NOT run the pipeline.
        task = (body.get("metadata") or {}).get("task")
        if task or user_message.lstrip().startswith("### Task:"):
            return self._label(user_message)

        # 2) Help intercept.
        msg_norm = user_message.strip().lower().rstrip("?").strip()
        if msg_norm in {"help", "/help", "hints", "hint", "usage", "commands", "info",
                        "what can you do", "what can it do", "what do you do"} or \
                msg_norm.startswith(("help ", "/help")):
            await self.emit(__event_emitter__, "Help", done=True)
            return self._help_text()

        # 3) Real use case -> fire the pipeline with a UNIQUE, meaningful project name.
        requirements = self._extract_file(messages) or user_message
        await self.emit(__event_emitter__, "Starting architecture pipeline…")
        base = (self.valves.default_project_name.strip()
                or " ".join(re.sub(r"[^A-Za-z0-9 ]+", " ", requirements).split()[:6]) or "architecture")
        payload = {self.valves.input_field: requirements, "sessionId": chat_id or "owui",
                   "projectName": f"{base} {time.strftime('%H%M%S')}"}
        try:
            resp = requests.post(self.valves.webhook_url, json=payload, headers=self._headers(), timeout=120)
        except requests.RequestException as e:
            await self.emit(__event_emitter__, f"Error: {e}", True, "error")
            return f"Failed to reach n8n: {e}"
        if resp.status_code not in (200, 202):
            await self.emit(__event_emitter__, "Webhook error", True, "error")
            return f"Webhook error {resp.status_code}: {resp.text[:400]}"

        ack = resp.json() if resp.text.strip() else {}
        project_slug = (ack.get("request", {}) or {}).get("projectSlug") or ack.get("projectSlug", "")
        project_name = (ack.get("request", {}) or {}).get("projectName") or project_slug
        if not project_slug:
            return f"```json\n{json.dumps(ack, indent=2)}\n```"
        await self.emit(__event_emitter__, f"Pipeline running for '{project_name}' ({project_slug})…")

        if not self.valves.poll_for_artifacts:
            return (f"**Architecture pipeline started** for **{project_name}** (`{project_slug}`).\n\n"
                    f"Runs async; retrieve via `{self.valves.n8n_base_url}{self.valves.artifact_path}"
                    f"?projectSlug={project_slug}&type=brd`.")

        deadline = time.time() + self.valves.max_wait_seconds
        found = {}
        while time.time() < deadline:
            for label, art_type in STAGES:
                if art_type in found:
                    continue
                got = self._get_artifact(project_slug, art_type)
                if got and got.get("ok") and got.get("artifact"):
                    found[art_type] = got["artifact"]
                    await self.emit(__event_emitter__, f"✓ {label}")
            if len(found) >= len(STAGES):
                break
            await self.emit(__event_emitter__, f"Generating… {len(found)}/{len(STAGES)} stages ready")
            time.sleep(self.valves.poll_interval)

        done = len(found) >= len(STAGES)
        await self.emit(__event_emitter__, "Complete" if done else "Partial (still generating)", True)
        lines = [f"## Architecture Pipeline — {project_name} (`{project_slug}`)\n",
                 f"**{len(found)}/{len(STAGES)} stages ready.**"
                 + ("" if done else " Remaining stages are still running.") + "\n"]
        for label, art_type in STAGES:
            lines.append(f"- {'✅' if art_type in found else '⏳'} {label}")
        brd = found.get("brd", {})
        content = brd.get("content") if isinstance(brd, dict) else None
        if isinstance(content, dict) and content.get("executiveSummary"):
            lines.append(f"\n**Executive summary:** {content['executiveSummary']}")
        lines.append(f"\n_Artifacts in Postgres `architecture` schema; fetch any type via "
                     f"`{self.valves.artifact_path}?projectSlug={project_slug}&type=<type>`._")
        return "\n".join(lines)
