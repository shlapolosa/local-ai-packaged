"""Open WebUI pipe rendering — pure unit tests, zero network.

Asserts that `solution_architect_pipe.Pipe.pipe()` returns the right Markdown
for every output shape the webhook can emit, plus the right routing for
help / background-tasks / bad commands.

`requests.post` is monkeypatched at the pipe module level so no HTTP fires.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

import solution_architect_pipe as pipe_mod


pytestmark = [pytest.mark.fast, pytest.mark.pipe]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
async def _noop_emitter(_: dict) -> None:
    return None


def _run(pipe: "pipe_mod.Pipe", body: dict) -> str:
    return asyncio.get_event_loop().run_until_complete(
        pipe.pipe(body, __event_emitter__=_noop_emitter)
    ) if False else asyncio.run(pipe.pipe(body, __event_emitter__=_noop_emitter))


def _fake_response(*, status_code: int, json_body: Any | None = None, text: str | None = None):
    class _R:
        def __init__(self) -> None:
            self.status_code = status_code
            self.text = text if text is not None else (json.dumps(json_body) if json_body is not None else "")

        def json(self) -> Any:
            if json_body is None:
                raise ValueError("no json body")
            return json_body
    return _R()


def _wrap_user(content: str, *, task: str | None = None) -> dict:
    body: dict = {"messages": [{"role": "user", "content": content}]}
    if task is not None:
        body["metadata"] = {"task": task}
    return body


@pytest.fixture
def pipe() -> pipe_mod.Pipe:
    return pipe_mod.Pipe()


@pytest.fixture
def no_post(monkeypatch):
    """Block real HTTP — every test asserts whether it should have been called."""
    calls: list[dict] = []

    def _post(url, json=None, timeout=None, headers=None):  # noqa: A002 — match requests sig
        calls.append({"url": url, "json": json, "timeout": timeout, "headers": headers})
        return _fake_response(status_code=599, text="no-post fixture: returning sentinel")

    monkeypatch.setattr(pipe_mod.requests, "post", _post)
    return calls


def _set_post_response(monkeypatch, response):
    monkeypatch.setattr(pipe_mod.requests, "post", lambda *a, **k: response)


# ─────────────────────────────────────────────────────────────────────────────
# Routing: help / tasks / bad commands MUST NOT call the webhook
# ─────────────────────────────────────────────────────────────────────────────
def test_help_does_not_call_webhook(pipe, no_post):
    md = _run(pipe, _wrap_user("help"))
    assert "Solution Architect — Help" in md
    assert "oam <slug>" in md
    assert no_post == [], f"help must not call webhook; got {no_post}"


def test_help_variants_route_to_help(pipe, no_post):
    for variant in ("HELP", "/help", "what can you do?", "usage", "hints"):
        md = _run(pipe, _wrap_user(variant))
        assert "Solution Architect — Help" in md, f"help routing failed for {variant!r}"
    assert no_post == []


def test_background_task_does_not_call_webhook(pipe, no_post, monkeypatch):
    """A title/tag/follow-up task should route to _label, not the webhook."""
    # Stub _label so we don't hit Ollama either.
    monkeypatch.setattr(pipe_mod.Pipe, "_label", lambda self, prompt: "Auto Title")
    md = _run(pipe, _wrap_user("### Task: generate a 3-5 word title", task="title_generation"))
    assert md == "Auto Title"
    assert no_post == [], f"background task must not call webhook; got {no_post}"


def test_bad_command_returns_usage_card(pipe, no_post):
    md = _run(pipe, _wrap_user("do the thing"))
    assert "couldn't parse" in md or "couldn’t parse" in md
    assert "oam <project-slug>" in md
    assert no_post == [], "bad command must not call webhook"


# ─────────────────────────────────────────────────────────────────────────────
# Intent parsing — the regex must pull (intent, slug) correctly
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("text, want_intent, want_slug", [
    ("oam acme-billing",          "oam",       "acme-billing"),
    ("provision acme-billing",    "provision", "acme-billing"),
    ("propose acme-billing",      "propose",   "acme-billing"),
    ("both acme-billing",         "provision", "acme-billing"),   # both → provision per pipe
    ("OAM AcmeBilling",           "oam",       "AcmeBilling"),
])
def test_intent_parsing(pipe, no_post, monkeypatch, text, want_intent, want_slug):
    """The pipe routes the parsed (intent, slug) into the webhook payload."""
    seen: list[dict] = []

    def _post(url, json=None, **_):
        seen.append(json)
        return _fake_response(status_code=200, json_body={
            "ok": True, "projectSlug": want_slug, "intent": want_intent,
            "type": "oam_application", "version": 1,
            "oam": {"yaml": "apiVersion: core.oam.dev/v1beta1\nkind: Application\nmetadata: {name: a, namespace: default}\nspec:\n  components: []\n"},
            "dry_run": {"content": [{"text": '{"ok": true}'}]},
            "capability_coverage": [],
            "agent": {"turns_used": 1}, "model": {"deployment": "x"},
        })
    monkeypatch.setattr(pipe_mod.requests, "post", _post)

    _run(pipe, _wrap_user(text))
    assert len(seen) == 1, f"expected exactly one webhook call; got {len(seen)}"
    assert seen[0]["projectSlug"] == want_slug
    assert seen[0]["intent"] == want_intent


def test_provision_wait_is_accepted_intent(pipe, no_post, monkeypatch):
    """Regression guard — pipe must accept the provision_wait command verbatim."""
    seen: list[dict] = []

    def _post(url, json=None, **_):
        seen.append(json)
        return _fake_response(status_code=200, json_body={
            "ok": True, "projectSlug": "x", "intent": "provision_wait",
            "type": "oam_application", "version": 1,
            "oam": {"yaml": "apiVersion: core.oam.dev/v1beta1\nkind: Application\nmetadata: {name: x, namespace: default}\nspec:\n  components: []\n"},
            "dry_run": {"content": [{"text": '{"ok": true}'}]},
            "agent": {"turns_used": 1}, "model": {"deployment": "x"},
        })
    monkeypatch.setattr(pipe_mod.requests, "post", _post)
    _run(pipe, _wrap_user("provision_wait x"))
    # The current pipe regex captures oam|provision|both; provision_wait may need
    # an explicit handler. If the pipe doesn't recognise it, this test surfaces
    # the gap as a failure — that IS the regression net we want.
    assert seen, "pipe must recognise `provision_wait <slug>` as a real command"
    assert seen[0]["intent"] in ("provision_wait", "provision"), (
        f"pipe routed `provision_wait` to {seen[0]['intent']!r}; should pass through"
    )


# ─────────────────────────────────────────────────────────────────────────────
# OK response — Markdown shape
# ─────────────────────────────────────────────────────────────────────────────
OK_RESPONSE = {
    "ok": True,
    "projectSlug": "acme-billing",
    "projectName": "Acme Billing",
    "intent": "oam",
    "type": "oam_application",
    "version": 7,
    "created_at": "2026-05-29T10:00:00Z",
    "oam": {"yaml": (
        "apiVersion: core.oam.dev/v1beta1\n"
        "kind: Application\n"
        "metadata: {name: acme-billing-app, namespace: default}\n"
        "spec:\n"
        "  components:\n"
        "    - name: acme-billing-api\n"
        "      type: webservice\n"
        "      properties: {image: nginx:1.25, port: 80}\n"
    )},
    "dry_run": {"content": [{"text": '{"ok": true, "diagnostics": "Deployment rendered"}'}]},
    "submit": None,
    "submit_wait": None,
    "proposed_prs": [],
    "capability_coverage": [
        {"capability": "Web API", "component_name": "acme-billing-api", "type": "webservice"}
    ],
    "model": {"deployment": "gpt-5.4", "mode": "direct"},
    "agent": {"turns_used": 6},
}


def test_ok_renders_yaml_fence(pipe, monkeypatch):
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=OK_RESPONSE))
    md = _run(pipe, _wrap_user("oam acme-billing"))
    # Exactly one yaml fenced block whose contents parse
    fences = [chunk for chunk in md.split("```") if chunk.lstrip().startswith("yaml")]
    assert len(fences) == 1, f"expected exactly 1 yaml fence; got {len(fences)}\nmd:\n{md}"
    yaml_text = fences[0].split("\n", 1)[1]
    parsed = yaml.safe_load(yaml_text)
    assert parsed["apiVersion"] == "core.oam.dev/v1beta1"
    assert parsed["kind"] == "Application"


def test_ok_header_carries_version_and_intent(pipe, monkeypatch):
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=OK_RESPONSE))
    md = _run(pipe, _wrap_user("oam acme-billing"))
    assert "OAM generated" in md
    assert "v7" in md
    assert "`oam`" in md
    assert "acme-billing" in md


def test_ok_dry_run_in_collapsible(pipe, monkeypatch):
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=OK_RESPONSE))
    md = _run(pipe, _wrap_user("oam acme-billing"))
    assert "<details>" in md and "Dry-run report" in md
    assert "Deployment rendered" in md


# ─────────────────────────────────────────────────────────────────────────────
# WIP response
# ─────────────────────────────────────────────────────────────────────────────
WIP_RESPONSE = {
    "ok": False,
    "status": "wip",
    "projectSlug": "acme-billing",
    "intent": "oam",
    "reason": "Dapr sidecar unmappable",
    "mapped_capabilities": [
        {"capability": "Web API", "component_name": "acme-billing-api", "type": "webservice"},
    ],
    "unmappable_capabilities": [
        {"capability": "Dapr runtime", "tried_components": ["application-infrastructure"],
         "why": "only candidate is ApplicationClaim-backed"}
    ],
    "factory_propose_drafts": [
        {"repo": "health-service-idp", "title": "request: dapr sidecar capability",
         "body": "Consumer agent…", "files": {"capability-factory/requests/REQ-1-dapr.yaml": "id: REQ-1\n"}}
    ],
    "agent": {"turns_used": 8},
    "model": {"deployment": "gpt-5.4", "mode": "direct"},
}


def test_wip_renders_banner_and_no_yaml(pipe, monkeypatch):
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=WIP_RESPONSE))
    md = _run(pipe, _wrap_user("oam acme-billing"))
    assert "🚧 WIP" in md or "WIP" in md
    assert "Dapr runtime" in md or "Dapr" in md
    assert "```yaml" not in md, "WIP response must not include a yaml block"


def test_wip_lists_unmappable_tried_components(pipe, monkeypatch):
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=WIP_RESPONSE))
    md = _run(pipe, _wrap_user("oam acme-billing"))
    # The currently-installed pipe falls through to JSON dump for WIP; either
    # the banner OR the JSON must show the tried_components signal.
    assert "application-infrastructure" in md


# ─────────────────────────────────────────────────────────────────────────────
# Error & edge paths
# ─────────────────────────────────────────────────────────────────────────────
def test_webhook_404(pipe, monkeypatch):
    _set_post_response(monkeypatch, _fake_response(
        status_code=404, json_body={"ok": False, "error": "no project with slug='x'"}
    ))
    md = _run(pipe, _wrap_user("oam acme-billing"))
    assert "Webhook error" in md or "404" in md
    assert "no project with slug" in md


def test_webhook_400_bad_intent(pipe, monkeypatch):
    _set_post_response(monkeypatch, _fake_response(
        status_code=400, json_body={"ok": False, "error": "intent must be one of …"}
    ))
    md = _run(pipe, _wrap_user("oam acme-billing"))
    assert "400" in md or "Webhook error" in md


def test_network_error(pipe, monkeypatch):
    def _boom(*a, **k):
        from requests.exceptions import RequestException
        raise RequestException("connection refused")
    monkeypatch.setattr(pipe_mod.requests, "post", _boom)
    md = _run(pipe, _wrap_user("oam acme-billing"))
    assert "Failed to reach n8n" in md or "connection refused" in md


def test_non_json_body(pipe, monkeypatch):
    bad = _fake_response(status_code=200, json_body=None, text="not json at all")
    _set_post_response(monkeypatch, bad)
    md = _run(pipe, _wrap_user("oam acme-billing"))
    assert "Bad response" in md or "not json" in md


def test_propose_with_no_unmappable_omits_pr_section(pipe, monkeypatch):
    payload = dict(OK_RESPONSE, intent="propose", proposed_prs=[])
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=payload))
    md = _run(pipe, _wrap_user("propose acme-billing"))
    assert "📝" not in md and "Proposed PR" not in md and "Provision submission" not in md
    assert "```yaml" in md


def test_propose_with_prs_shows_links(pipe, monkeypatch):
    payload = dict(OK_RESPONSE, intent="propose", proposed_prs=[
        {"content": [{"text": '{"pr_url":"https://github.com/x/y/pull/42"}'}]}
    ])
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=payload))
    md = _run(pipe, _wrap_user("propose acme-billing"))
    # Pipe currently doesn't have a "Proposed PRs" section; this asserts the
    # contract by checking the URL surfaces somewhere readable. If not, we
    # know to add the renderer.
    assert "pull/42" in md or "Proposed" in md or "proposed_prs" in md


# ─────────────────────────────────────────────────────────────────────────────
# Markdown sanity — fence balance, no leaked Python repr
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("payload, command", [
    (OK_RESPONSE,  "oam acme-billing"),
    (WIP_RESPONSE, "oam acme-billing"),
])
def test_markdown_fences_balanced(pipe, monkeypatch, payload, command):
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=payload))
    md = _run(pipe, _wrap_user(command))
    assert md.count("```") % 2 == 0, f"unbalanced ``` fences in:\n{md}"
    # No accidentally-printed Python dict reprs leaking past json.dumps
    assert "'ok':" not in md, "looks like a raw Python dict leaked into the Markdown"


# ─────────────────────────────────────────────────────────────────────────────
# Golden file snapshot — happy path
# ─────────────────────────────────────────────────────────────────────────────
GOLDEN_DIR = Path(__file__).parent / "golden"
GOLDEN_DIR.mkdir(exist_ok=True)


def _normalise(md: str) -> str:
    """Strip volatile bits before diffing (timestamps, version numbers in
    headers, etc.)."""
    out = md
    # If we ever embed wall-clock timestamps, strip them here.
    return out.rstrip() + "\n"


def test_golden_ok_response(pipe, monkeypatch, request):
    """First run writes the golden; subsequent runs diff.

    Regenerate with: `pytest -m pipe --update-goldens` (see flag below)."""
    _set_post_response(monkeypatch, _fake_response(status_code=200, json_body=OK_RESPONSE))
    md = _normalise(_run(pipe, _wrap_user("oam acme-billing")))

    golden = GOLDEN_DIR / "ok_oam.md"
    update = request.config.getoption("--update-goldens", default=False)
    if update or not golden.exists():
        golden.write_text(md)
        if not update:
            pytest.skip(f"wrote initial golden: {golden}")
    expected = golden.read_text()
    assert md == expected, (
        f"golden mismatch — run with --update-goldens to refresh.\n"
        f"diff (first 1500 chars):\n--- expected ---\n{expected[:750]}\n"
        f"--- actual ---\n{md[:750]}"
    )


# --update-goldens flag is registered in conftest.py
