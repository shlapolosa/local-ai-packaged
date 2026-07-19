"""LLM-as-judge quality grading.

Reuses the session-scoped `oam_results` fixture from test_oam_agent.py so we
don't re-fire the agent — we just send each OK run through gpt-5.4 once with
a structured rubric and assert on the facet scores.

Marked `judge` so it can be opt-in if cost becomes a concern.
"""
from __future__ import annotations

import pytest

from corpus import SlugSpec, selected_corpus
from helpers import get_catalog
from judge import grade_oam


pytestmark = [pytest.mark.network, pytest.mark.judge]


THRESHOLDS = {
    # Calibrated against the first baseline run; these are the floors below
    # which we treat the result as a regression. Tighten them once the agent
    # consistently scores higher.
    "overall": 6,
    "completeness": 5,
    "catalog_fidelity": 9,   # any miss here is a closed-vocabulary violation
    "naming": 5,           # model occasionally drops `shared-` prefix; tighten via prompt later
    "layer_coverage": 7,
    "structural": 9,
}


@pytest.fixture(scope="session")
def judge_rubrics(oam_results) -> dict[str, dict]:
    """Run the judge once per OK slug; cache the rubric."""
    catalog_names = list(get_catalog().keys())
    out: dict[str, dict] = {}
    for slug, res in oam_results.items():
        if not res.body or not res.body.get("ok"):
            continue
        yaml_text = (res.body.get("oam") or {}).get("yaml") or ""
        out[slug] = grade_oam(slug, yaml_text, catalog_names)
    return out


def _rubric_for(slug: str, judge_rubrics) -> dict:
    rubric = judge_rubrics.get(slug)
    if rubric is None:
        pytest.skip(f"agent did not produce OK on {slug}; judge not run")
    if "error" in rubric:
        pytest.fail(f"judge failed for {slug}: {rubric['error']}")
    return rubric


@pytest.mark.parametrize("spec", selected_corpus(), ids=lambda s: s.slug)
@pytest.mark.parametrize("facet,floor", list(THRESHOLDS.items()),
                         ids=lambda v: v if isinstance(v, str) else str(v))
def test_facet_above_floor(spec: SlugSpec, facet: str, floor: int, judge_rubrics):
    rubric = _rubric_for(spec.slug, judge_rubrics)
    score = rubric.get(facet)
    assert isinstance(score, int), f"judge omitted facet `{facet}`; rubric: {rubric}"
    assert score >= floor, (
        f"{facet} = {score} < {floor} for {spec.slug}.\n"
        f"  summary: {rubric.get('one_line_summary')!r}\n"
        f"  issues : {rubric.get('top_issues')}"
    )


@pytest.mark.parametrize("spec", selected_corpus(), ids=lambda s: s.slug)
def test_judge_surfaces_actionable_issues_only(spec: SlugSpec, judge_rubrics):
    """If overall is high but `top_issues` is huge, the judge is being noisy.
    Conversely, if overall is low but `top_issues` is empty, it's hiding signal."""
    rubric = _rubric_for(spec.slug, judge_rubrics)
    overall = rubric.get("overall", 0)
    issues = rubric.get("top_issues") or []
    if overall >= 9:
        assert len(issues) <= 1, f"overall={overall} but {len(issues)} issues: {issues}"
    if overall <= 4:
        assert len(issues) >= 1, f"overall={overall} but top_issues is empty"
