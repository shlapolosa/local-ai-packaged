"""Monolith Architecture Pipeline tests.

Slow: a single run takes ~20–35 min on Ollama Cloud qwen3-coder:480b.
Marked `slow` + `regression`. Each test fires the monolith once with a fixed
projectName for a predictable slug, then polls until all expected artifacts
land or the timeout fires.

Guarded by EVAL_RUN_MONOLITH=1 so an accidental `pytest -m regression` on a
laptop doesn't quietly burn token budget; explicit opt-in.
"""
from __future__ import annotations

import os
import time

import pytest

from helpers import db_jsonb_value, db_query

pytestmark = [pytest.mark.slow, pytest.mark.regression, pytest.mark.network]


EXPECTED_TYPES = {
    "brd", "business_arch", "application_arch", "data_arch", "infrastructure_arch",
    "archimate_xml_business_application",
    "archimate_xml_business_application_data",
    "archimate_xml_business_application_data_infra",
    "risk_assessment_md", "solution_arch_md",
    "openapi_yaml", "asyncapi_yaml", "avro_schemas_json",
    "cloudevents_md", "sql_schema_sql",
    "test_strategy_md", "test_scenarios_md",
}
REQUIRED_FOR_DOWNSTREAM = {
    "infrastructure_arch", "application_arch", "data_arch", "solution_arch_md"
}

CANONICAL_AP_PROMPT = (
    "Build an accounts-payable invoice processing service: ingest invoices "
    "through multiple channels (email, API, file upload, EDI), extract key "
    "fields using OCR/AI (vendor, invoice number, amount, date, line items, "
    "tax), match invoices to purchase orders and goods receipts using three-way "
    "matching with two-way fallback, auto-approve clean matches within tolerance, "
    "route mismatches to an AI Exception Handling Agent that investigates "
    "discrepancies and recommends actions, and surface exceptions in an AP "
    "Clerk Approval Queue."
)


def _skip_unless_opted_in() -> None:
    if not os.environ.get("EVAL_RUN_MONOLITH"):
        pytest.skip("set EVAL_RUN_MONOLITH=1 to run the monolith (20–35 min, costs tokens)")


@pytest.fixture(scope="module")
def monolith_run(fire_monolith, poll_artifacts) -> dict:
    """Fire one monolith run; poll until all 4 required-for-downstream types
    land (or shorter timeout — they're the early stages).

    Returns {slug, ack_body, poll_result_set, elapsed_s}.
    """
    _skip_unless_opted_in()
    project_name = f"eval-ap-{int(time.time())}"
    ack = fire_monolith(CANONICAL_AP_PROMPT, project_name=project_name)
    assert ack.status in (200, 202), f"monolith ack status {ack.status}: {ack.raw[:300]}"
    slug = (ack.body or {}).get("projectSlug") or (
        ((ack.body or {}).get("request") or {}).get("projectSlug")
    )
    assert slug, f"no projectSlug in ack body: {ack.body!r}"
    t0 = time.time()
    seen = poll_artifacts(slug, REQUIRED_FOR_DOWNSTREAM)
    return {
        "slug": slug,
        "ack_body": ack.body,
        "seen_types": seen,
        "elapsed_s": time.time() - t0,
        "project_name": project_name,
    }


def test_smoke_returns_slug(monolith_run):
    assert monolith_run["slug"]
    assert monolith_run["ack_body"], "ack body must be JSON"


def test_required_downstream_artifacts_land(monolith_run):
    """The 4 artifacts the OAM agent consumes must show up."""
    missing = REQUIRED_FOR_DOWNSTREAM - set(monolith_run["seen_types"])
    assert not missing, (
        f"required-for-OAM-handoff artifacts missing after "
        f"{monolith_run['elapsed_s']:.0f}s: {missing}"
    )


@pytest.mark.xfail(
    strict=False,
    reason="qwen3-coder intermittently stores one of the JSON arch stages as `{}`. "
           "Tracked as a monolith reliability issue; the eval records each occurrence "
           "but does not break the build on a known-flaky surface.",
)
def test_no_empty_json_stages(monolith_run):
    """Regression guard: application_arch / data_arch / infrastructure_arch
    should not be stored as `{}`. Observed intermittently on 2026-05-28 +
    2026-05-29 (this test caught both). Marked xfail strict=False so a green
    run doesn't break the build but the failure is still surfaced when it
    happens — the count over time is the signal.
    """
    slug = monolith_run["slug"]
    empties = []
    for type_name in ("application_arch", "data_arch", "infrastructure_arch"):
        raw = db_query(
            f"SELECT content::text FROM architecture.artifacts "
            f"WHERE project_id=(SELECT id FROM architecture.projects WHERE slug='{slug}') "
            f"AND type='{type_name}' ORDER BY version DESC LIMIT 1"
        ).strip()
        if raw == "{}":
            empties.append(type_name)
    assert not empties, (
        f"JSON-stage regression — these were stored as empty `{{}}` for slug={slug}: {empties}"
    )


def test_brd_has_structured_content(monolith_run):
    """qwen3-coder's BRD shape is non-deterministic across runs — sometimes a
    flat `components: [...]` list at the top level, sometimes a nested object
    with keys like `approval`, `matching`, `ingestion`. The test asserts the
    document is structurally rich (a JSON object with several non-trivial
    top-level keys) rather than pinning to one specific schema.
    """
    slug = monolith_run["slug"]
    brd = db_jsonb_value(
        f"SELECT content FROM architecture.artifacts "
        f"WHERE project_id=(SELECT id FROM architecture.projects WHERE slug='{slug}') "
        f"AND type='brd' ORDER BY version DESC LIMIT 1"
    )
    assert isinstance(brd, dict), f"BRD not JSON object: {type(brd).__name__}"
    assert len(brd) >= 4, f"BRD object too thin ({len(brd)} top-level keys): {list(brd)}"

    # At least one top-level field must carry real content — a non-empty list
    # of structured items OR a non-empty nested object.
    def _has_content(v) -> bool:
        if isinstance(v, list):
            return len(v) >= 1 and any(isinstance(x, (dict, str)) for x in v)
        if isinstance(v, dict):
            return len(v) >= 1
        return False
    rich_keys = [k for k, v in brd.items() if _has_content(v)]
    assert len(rich_keys) >= 2, (
        f"BRD has fewer than 2 keys with non-trivial content. "
        f"Keys: {list(brd)}. Rich keys: {rich_keys}"
    )


# ────────────────────────────────────────────────────────────────────────────
# Downstream hand-off — monolith → OAM agent on the freshly-minted slug
# ────────────────────────────────────────────────────────────────────────────
def test_oam_agent_can_consume_monolith_output(monolith_run, call_oam):
    """Smoke: the slug the monolith just produced is consumable by the OAM
    agent (passes the consumer's input-validation phase + at least starts the
    agent loop). Not asserting OK — just that the structural prerequisites
    are met so the agent runs to completion.
    """
    slug = monolith_run["slug"]
    res = call_oam(slug, "oam")
    assert res.status == 200, f"oam handoff failed with {res.status}: {res.raw[:300]}"
    assert isinstance(res.body, dict)
    # The agent must NOT reject for missing prereq artifacts.
    if not res.body.get("ok"):
        reason = (res.body.get("reason") or "").lower()
        assert "missing prerequisite artifacts" not in reason, (
            f"OAM agent thinks the monolith's output is incomplete for {slug}: "
            f"{res.body.get('reason')!r}"
        )
