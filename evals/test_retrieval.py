"""Tests for the artifact-get webhook + DB round-trip.

Pure read-side; fast lane, no LLM, no Foundry.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

import pytest

from corpus import AP_CLEAN_FINAL
from helpers import db_query

pytestmark = [pytest.mark.fast, pytest.mark.network]


def _get(url: str, *, timeout: int = 30) -> tuple[int, dict | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            raw = r.read().decode()
            try:
                return r.status, json.loads(raw), raw
            except json.JSONDecodeError:
                return r.status, None, raw
    except urllib.error.HTTPError as e:
        return e.code, None, e.read().decode()


def test_known_slug_known_type_returns_artifact(artifact_get_webhook):
    """artifact-get with a slug that has a `brd` artifact returns the row."""
    url = artifact_get_webhook + "?" + urllib.parse.urlencode(
        {"projectSlug": AP_CLEAN_FINAL.slug, "type": "brd"}
    )
    status, body, raw = _get(url)
    assert status == 200, f"unexpected status {status}, body head: {raw[:200]}"
    assert body and body.get("ok") is True
    art = body.get("artifact") or {}
    assert art.get("type") == "brd"
    assert isinstance(art.get("version"), int) and art["version"] >= 1
    assert "content" in art


def test_returns_highest_version_when_multiple(artifact_get_webhook):
    """When multiple versions exist for (slug, type), the latest one wins."""
    # Inspect the DB to find the highest version we expect
    expected_version_str = db_query(
        "SELECT MAX(version)::text FROM architecture.artifacts "
        f"WHERE project_id=(SELECT id FROM architecture.projects WHERE slug='{AP_CLEAN_FINAL.slug}') "
        "AND type='brd'"
    ).strip()
    if not expected_version_str:
        pytest.skip(f"no BRD artifact for {AP_CLEAN_FINAL.slug}")
    expected_version = int(expected_version_str)
    url = artifact_get_webhook + "?" + urllib.parse.urlencode(
        {"projectSlug": AP_CLEAN_FINAL.slug, "type": "brd"}
    )
    status, body, _ = _get(url)
    assert status == 200
    assert (body["artifact"] or {}).get("version") == expected_version


def test_unknown_slug_returns_not_found_shape(artifact_get_webhook):
    """The retrieval webhook should not 500 on a bad slug. 200/404 with ok:false ok."""
    url = artifact_get_webhook + "?" + urllib.parse.urlencode(
        {"projectSlug": "does-not-exist-xyzzy-9999", "type": "brd"}
    )
    status, body, raw = _get(url)
    assert status in (200, 404), f"unexpected status {status}: {raw[:200]}"
    if body is not None:
        assert body.get("ok") is False
