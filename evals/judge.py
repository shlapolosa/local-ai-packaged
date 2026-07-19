"""LLM-as-judge helpers.

Grades an OAM Application against the architecture artifacts that produced
it using gpt-5.4 via direct Foundry (same auth as the agent in mode=direct).
Single call per slug, cached for the pytest session.

The rubric is structured-JSON so individual facet scores can drive
fine-grained assertions in the test file.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from helpers import _read_env, db_jsonb_value


FOUNDRY_BASE = os.environ.get("FOUNDRY_BASE", "https://aifoundry-socrates.openai.azure.com")
JUDGE_DEPLOYMENT = os.environ.get("JUDGE_DEPLOYMENT", "gpt-5.4")
JUDGE_API_VERSION = os.environ.get("JUDGE_API_VERSION", "2024-10-21")
JUDGE_TIMEOUT_S = int(os.environ.get("JUDGE_TIMEOUT_S", "240"))


_FOUNDRY_KEY_CACHE: dict[str, str] = {}


def _foundry_key() -> str:
    if "key" not in _FOUNDRY_KEY_CACHE:
        _FOUNDRY_KEY_CACHE["key"] = _read_env("FOUNDRY_API_KEY")
    return _FOUNDRY_KEY_CACHE["key"]


JUDGE_SYSTEM = """You are an evaluator grading a KubeVela OAM Application against the
architecture artifacts that produced it. You are STRICT but FAIR. You only
penalise verifiable failures; you do not invent novel requirements.

Score each facet 0-10. Then return ONE JSON object — no prose, no fences.

Facets:
- completeness:    Did the OAM faithfully cover the application, data, and
                   infrastructure layers from the architecture artifacts?
                   10 = every distinct architectural element is represented
                   as an OAM component or merged into a clearly-named shared
                   primitive. 0 = whole layers missing without justification.
- catalog_fidelity: Every `type:` MUST be a name the platform catalog publishes
                    (the catalog list is given to you below). Inventions = 0.
                    Component re-use of the same generic type is OK.
- naming:           initiative components follow `{slug}-{role}`; shared
                    infrastructure uses `shared-{type}`. 0 = off-convention.
- layer_coverage:   Application + data + infrastructure layers are each touched
                    by at least one component. 0 = a layer is entirely absent.
- structural:       OAM YAML is well-formed and conforms to KubeVela schema
                    (apiVersion, kind: Application, metadata, spec.components[]).
- overall:          Synthesis. Not a mechanical average.

Also produce:
- top_issues: array of 0-3 short strings naming the most important problems
              (empty if everything is fine).
- one_line_summary: a sentence the engineer can paste into a PR.

Schema (return EXACTLY this shape):
{
  "completeness": <int 0-10>,
  "catalog_fidelity": <int 0-10>,
  "naming": <int 0-10>,
  "layer_coverage": <int 0-10>,
  "structural": <int 0-10>,
  "overall": <int 0-10>,
  "top_issues": [<string>, ...],
  "one_line_summary": <string>
}
"""


def _arch_for(slug: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for type_name in ("application_arch", "data_arch", "infrastructure_arch", "solution_arch_md"):
        out[type_name] = db_jsonb_value(
            "SELECT content FROM architecture.artifacts "
            f"WHERE project_id=(SELECT id FROM architecture.projects WHERE slug='{slug}') "
            f"AND type='{type_name}' ORDER BY version DESC LIMIT 1"
        )
    return out


def grade_oam(slug: str, oam_yaml: str, catalog_names: list[str]) -> dict[str, Any]:
    """Call the judge once; return the parsed rubric or {error: ...}."""
    arch = _arch_for(slug)
    user_payload = json.dumps({
        "project_slug": slug,
        "catalog_components_published": sorted(catalog_names),
        "architecture_artifacts": arch,
        "oam_yaml": oam_yaml,
    })
    url = f"{FOUNDRY_BASE}/openai/deployments/{JUDGE_DEPLOYMENT}/chat/completions?api-version={JUDGE_API_VERSION}"
    body = json.dumps({
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user",   "content": user_payload},
        ],
        "temperature": 1,
        "max_completion_tokens": 1024,
        "response_format": {"type": "json_object"},
    }).encode()
    # Retry-with-backoff on transient 429/5xx/network errors.
    backoffs = (5, 15, 30)  # 4 attempts → ~50 s worst-case before final raise
    t0 = time.time()
    last_exc: Exception | None = None
    j: dict[str, Any] | None = None
    for attempt in range(len(backoffs) + 1):
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/json", "api-key": _foundry_key()},
        )
        try:
            with urllib.request.urlopen(req, timeout=JUDGE_TIMEOUT_S) as r:
                j = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            last_exc = e
            if e.code in (429, 502, 503, 504) and attempt < len(backoffs):
                time.sleep(backoffs[attempt]); continue
            return {"error": f"judge HTTP {e.code}: {e.read().decode()[:200]}",
                    "elapsed_s": time.time() - t0}
        except urllib.error.URLError as e:
            last_exc = e
            if attempt < len(backoffs):
                time.sleep(backoffs[attempt]); continue
            return {"error": f"judge URLError after retries: {e}", "elapsed_s": time.time() - t0}
    if j is None:
        return {"error": f"judge unreachable: {last_exc}", "elapsed_s": time.time() - t0}
    elapsed = time.time() - t0
    text = (((j.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
    try:
        rubric = json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"judge returned non-JSON ({e}). head: {text[:300]}", "elapsed_s": elapsed}
    rubric["_elapsed_s"] = elapsed
    return rubric
