"""Intent-gating tests for the consumer protocol.

Each `intent` value has a strict tool-surface contract:
    oam            — no submit, no propose, no queue
    propose        — no submit/queue; factory.propose fires only on unmappable
    provision      — app.submit only when dry_run passes
    provision_wait — app.submit on pass, app.submit_wait on missing-CD
    both           — alias of provision

Real-deploy intents are gated behind the `deploys` marker.
"""
from __future__ import annotations

import pytest

from corpus import PRIMARY_SLUG

pytestmark = [pytest.mark.network]


# ────────────────────────────────────────────────────────────────────────────
# intent=oam — never submits, never proposes
# Reuses the session-scoped `oam_results` fixture (defined in conftest.py)
# so we don't re-fire the agent ~3 min for what's already cached.
# ────────────────────────────────────────────────────────────────────────────
def test_intent_oam_never_submits(oam_results):
    res = oam_results.get(PRIMARY_SLUG.slug)
    if res is None or res.body is None:
        pytest.skip(f"no oam_results entry for {PRIMARY_SLUG.slug}")
    assert res.status == 200
    assert isinstance(res.body, dict)
    assert res.body.get("submit") in (None, {}), f"oam must not submit; got {res.body.get('submit')}"
    assert res.body.get("submit_wait") in (None, {}), \
        f"oam must not submit_wait; got {res.body.get('submit_wait')}"
    if res.body.get("ok"):
        assert (res.body.get("proposed_prs") or []) == [], \
            "oam must not propose; proposed_prs must be empty"


# ────────────────────────────────────────────────────────────────────────────
# intent=propose — proposes only on unmappable
# ────────────────────────────────────────────────────────────────────────────
def test_intent_propose_on_clean_slug_no_prs(call_oam):
    """When the architecture maps cleanly, no factory.propose fires."""
    res = call_oam(PRIMARY_SLUG.slug, "propose")
    assert res.status == 200
    if not res.body.get("ok"):
        pytest.skip("primary slug WIPped — covered elsewhere")
    assert (res.body.get("proposed_prs") or []) == [], (
        f"propose on a clean slug must not file PRs; got {res.body.get('proposed_prs')}"
    )
    # And must NOT submit
    assert res.body.get("submit") in (None, {})
    assert res.body.get("submit_wait") in (None, {})


# ────────────────────────────────────────────────────────────────────────────
# Real-deploy intents — kept off by default
# ────────────────────────────────────────────────────────────────────────────
@pytest.mark.deploys
def test_intent_provision_submits_on_pass(call_oam):
    res = call_oam(PRIMARY_SLUG.slug, "provision")
    assert res.status == 200
    if not res.body.get("ok"):
        pytest.fail(f"provision on primary slug failed dry-run: {res.body!r}")
    submit = res.body.get("submit")
    assert submit, f"provision must call app.submit on dry-run pass; got submit={submit!r}"


@pytest.mark.deploys
def test_intent_provision_wait_passes_through_to_submit_when_dryrun_ok(call_oam):
    """When dry-run passes, provision_wait should call app.submit (not submit_wait)."""
    res = call_oam(PRIMARY_SLUG.slug, "provision_wait")
    assert res.status == 200
    if not res.body.get("ok"):
        pytest.fail(f"provision_wait failed dry-run on primary slug: {res.body!r}")
    assert res.body.get("submit"), "submit must be set when dry-run passes"
    assert res.body.get("submit_wait") in (None, {}), \
        "submit_wait must be null when dry-run already passes"


@pytest.mark.deploys
def test_intent_both_aliases_provision(call_oam):
    """intent=both shouldn't behave differently from provision at the contract level.

    Marked `deploys` because if dry-run passes, the agent calls app.submit,
    which fires an oam-apply workflow and creates real ArgoCD resources.
    """
    res = call_oam(PRIMARY_SLUG.slug, "both")
    assert res.status == 200
    assert isinstance(res.body, dict)
    assert res.body.get("intent") in ("both", "provision")  # accept either echo


# ────────────────────────────────────────────────────────────────────────────
# Input validation
# ────────────────────────────────────────────────────────────────────────────
def test_bad_intent_returns_400(call_oam):
    res = call_oam(PRIMARY_SLUG.slug, "make_me_a_sandwich")
    assert res.status == 400
    assert res.body and res.body.get("ok") is False
    assert "intent" in (res.body.get("error") or "").lower()


def test_missing_slug_returns_400(call_oam):
    from conftest import OAM_AGENT_TIMEOUT, OAM_WEBHOOK, _post_json  # type: ignore
    res = _post_json(OAM_WEBHOOK, {"intent": "oam"}, OAM_AGENT_TIMEOUT)
    assert res.status == 400
    assert res.body and res.body.get("ok") is False
    assert "projectslug" in (res.body.get("error") or "").lower()


def test_unknown_slug_returns_404(call_oam):
    res = call_oam("nonexistent-slug-xyzzy", "oam")
    assert res.status == 404
    assert res.body and res.body.get("ok") is False
