"""Shared pytest fixtures."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from helpers import db_query

# Make `solution_architect_pipe` importable from this sibling-of-repo-root layout.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def pytest_addoption(parser):
    parser.addoption(
        "--update-goldens", action="store_true", default=False,
        help="overwrite golden files in evals/golden/ instead of asserting equality",
    )

N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "http://localhost:5678")
OAM_WEBHOOK = N8N_BASE_URL + os.environ.get("OAM_WEBHOOK", "/webhook/solution-architect-oam")
MONOLITH_WEBHOOK = N8N_BASE_URL + os.environ.get("MONOLITH_WEBHOOK", "/webhook/architecture-pipeline")
ARTIFACT_GET_WEBHOOK = N8N_BASE_URL + os.environ.get(
    "ARTIFACT_GET_WEBHOOK", "/webhook/architecture-artifact-v2"
)

OAM_AGENT_TIMEOUT = int(os.environ.get("OAM_AGENT_TIMEOUT", "360"))
MONOLITH_POLL_TIMEOUT = int(os.environ.get("MONOLITH_POLL_TIMEOUT", "2700"))
MONOLITH_POLL_INTERVAL = int(os.environ.get("MONOLITH_POLL_INTERVAL", "30"))


@dataclass
class WebhookCall:
    status: int
    body: dict | None
    raw: str
    elapsed_s: float


def _post_json(url: str, payload: dict, timeout: int) -> WebhookCall:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json"},
    )

    def _try_parse(raw: str) -> dict | None:
        if not raw.strip():
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            return WebhookCall(status=r.status, body=_try_parse(raw), raw=raw, elapsed_s=time.time() - t0)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        # n8n's Respond-to-Webhook node sends a JSON body alongside the 4xx
        # status; parse it the same way as a success.
        return WebhookCall(status=e.code, body=_try_parse(raw), raw=raw, elapsed_s=time.time() - t0)


@pytest.fixture(scope="session")
def n8n_base_url() -> str:
    return N8N_BASE_URL


@pytest.fixture(scope="session")
def oam_webhook() -> str:
    return OAM_WEBHOOK


@pytest.fixture(scope="session")
def monolith_webhook() -> str:
    return MONOLITH_WEBHOOK


@pytest.fixture(scope="session")
def artifact_get_webhook() -> str:
    return ARTIFACT_GET_WEBHOOK


@pytest.fixture
def call_oam():
    """Hit /webhook/solution-architect-oam with {projectSlug, intent}, return parsed."""
    def _call(slug: str, intent: str = "oam") -> WebhookCall:
        return _post_json(OAM_WEBHOOK, {"projectSlug": slug, "intent": intent}, OAM_AGENT_TIMEOUT)
    return _call


# ────────────────────────────────────────────────────────────────────────────
# Session-scoped OAM agent results — shared across test_oam_agent.py,
# test_oam_agent_qual_judge.py, and any consumer-protocol test that needs
# the intent=oam call. Saves ~3 min per shared slug.
# ────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def oam_results() -> dict:
    """Returns {slug: WebhookCall}. Calls intent=oam once per corpus slug."""
    from corpus import selected_corpus
    out: dict = {}
    for spec in selected_corpus():
        out[spec.slug] = _post_json(
            OAM_WEBHOOK, {"projectSlug": spec.slug, "intent": "oam"}, OAM_AGENT_TIMEOUT
        )
    return out


@pytest.fixture(scope="session")
def fire_monolith():
    """POST the monolith webhook; returns the ack body + slug derived.

    Session-scoped so that module-scoped consumers in test_monolith.py can
    depend on it without ScopeMismatch.
    """
    def _fire(prompt: str, project_name: str | None = None) -> WebhookCall:
        body: dict[str, Any] = {"requirements": prompt}
        if project_name:
            body["projectName"] = project_name
        return _post_json(MONOLITH_WEBHOOK, body, timeout=180)
    return _fire


@pytest.fixture(scope="session")
def poll_artifacts():
    """Poll architecture.artifacts until all `required_types` show up or timeout."""
    def _poll(slug: str, required_types: set[str], *, timeout_s: int = MONOLITH_POLL_TIMEOUT,
              interval_s: int = MONOLITH_POLL_INTERVAL) -> set[str]:
        deadline = time.time() + timeout_s
        seen: set[str] = set()
        while time.time() < deadline:
            rows = db_query(
                "SELECT DISTINCT type FROM architecture.artifacts "
                f"WHERE project_id=(SELECT id FROM architecture.projects WHERE slug='{slug}')"
            )
            seen = {ln for ln in rows.splitlines() if ln}
            if required_types.issubset(seen):
                return seen
            time.sleep(interval_s)
        return seen
    return _poll
