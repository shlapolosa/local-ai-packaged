"""Eval corpus: known-good project slugs + per-slug expectations.

These slugs already exist in `architecture.projects`. Each entry encodes the
soft expectations we want regression to hold — *minimums*, not exact values,
so that the agent has room to improve coverage without breaking the suite.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SlugSpec:
    slug: str
    # Minimum capabilities the OAM agent should map on intent=oam.
    expected_mapped_min: int
    # At least these catalog types must appear in the final YAML.
    must_include_types: frozenset[str] = field(default_factory=frozenset)
    # Notes for humans reading test failures.
    notes: str = ""


# Reference happy-path slug; oldest known-good baseline.
AP_CLEAN_FINAL = SlugSpec(
    slug="ap-clean-final",
    expected_mapped_min=18,
    must_include_types=frozenset({"webservice", "postgresql"}),
    notes="Reference baseline (created 2026-05-27)",
)

# Today's monolith run; tests 3-layer completeness post-fix.
# expected_mapped_min lowered from 20 → 14 to accommodate gpt-5.4 frontier's
# turn-to-turn variance (observed range 14–25 on this slug). The
# must_include_types floor (webservice + postgresql) still catches the real
# "silently dropped data layer" regression even when the total count varies.
AP_INVOICE_TODAY = SlugSpec(
    slug="build-an-accounts-payable-invoice-processing-112818",
    expected_mapped_min=14,
    must_include_types=frozenset({"webservice", "postgresql"}),
    notes="Catches the 'silently dropped data layer' regression (2026-05-28)",
)

LOYALTY = SlugSpec(
    slug="build-a-customer-loyalty-rewards-platform",
    expected_mapped_min=10,
    must_include_types=frozenset({"webservice", "postgresql"}),
    notes="Different domain — sanity check for prompt over-fit",
)


CORPUS_FULL: list[SlugSpec] = [AP_CLEAN_FINAL, AP_INVOICE_TODAY, LOYALTY]


def selected_corpus() -> list[SlugSpec]:
    """Honour the EVAL_SLUGS env var (comma-separated) for ad-hoc runs."""
    override = os.environ.get("EVAL_SLUGS", "").strip()
    if not override:
        return CORPUS_FULL
    wanted = {s.strip() for s in override.split(",") if s.strip()}
    return [s for s in CORPUS_FULL if s.slug in wanted] or [
        SlugSpec(slug=s, expected_mapped_min=1) for s in wanted
    ]


# Lightest reference for tests that only need one slug (smoke tests).
PRIMARY_SLUG = AP_CLEAN_FINAL
