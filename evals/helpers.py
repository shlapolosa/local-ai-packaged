"""Shared utilities for the eval suite.

DB access goes through `docker compose exec` so we have zero Python-side
database deps; SP token mint reads copilots/.env locally and posts to Entra.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DOCKER_COMPOSE_PROJECT = os.environ.get("DOCKER_COMPOSE_PROJECT", "localai")
DB_CONTAINER = os.environ.get("DB_CONTAINER", "db")
APIM_SP_ENV_PATH = os.environ.get(
    "APIM_SP_ENV_PATH", "/Users/socrateshlapolosa/Development/copilots/.env"
)
APIM_BASE = "https://aigw-apim-dev-w4x7ibwk4e2is.azure-api.net"
SP_AUDIENCE = "api://fe225ae2-c6eb-4e4e-b4c2-79b45b2dce69/.default"


# ────────────────────────────────────────────────────────────────────────────
# Postgres via docker exec
# ────────────────────────────────────────────────────────────────────────────
def db_query(sql: str, *, tuples: bool = False) -> list[list[str]] | str:
    """Run a SQL string against the local Supabase Postgres container.

    Returns lines (default) or a list of tab-split rows when `tuples=True`.
    """
    cmd = [
        "docker", "compose", "-p", DOCKER_COMPOSE_PROJECT,
        "exec", "-T", DB_CONTAINER,
        "psql", "-U", "postgres", "-d", "postgres", "-tAc", sql,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
    if not tuples:
        return out
    return [line.split("|") for line in out.splitlines() if line]


def db_jsonb_value(sql: str) -> Any:
    """Run a query expected to return a single JSONB column value; parse JSON."""
    raw = db_query(sql)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


# ────────────────────────────────────────────────────────────────────────────
# Entra SP token (cached per session)
# ────────────────────────────────────────────────────────────────────────────
_TOKEN_CACHE: dict[str, Any] = {}


def _read_env(name: str) -> str:
    with open(APIM_SP_ENV_PATH) as f:
        for line in f:
            if line.startswith(f"{name}="):
                return line[len(name) + 1 :].rstrip("\n")
    raise KeyError(f"{name} missing from {APIM_SP_ENV_PATH}")


def get_sp_token() -> str:
    """Mint (and cache for ~50 min) a Bearer token for the SP, audience fe225ae2-…"""
    now = time.time()
    if _TOKEN_CACHE.get("expiry", 0) > now + 60:
        return _TOKEN_CACHE["token"]

    tenant = _read_env("SUBSCRIPTION_TENANT_ID")
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": _read_env("SP_CLIENT_ID"),
        "client_secret": _read_env("SP_CLIENT_SECRET"),
        "scope": SP_AUDIENCE,
    }).encode()
    req = urllib.request.Request(
        f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
        data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode())

    _TOKEN_CACHE["token"] = payload["access_token"]
    _TOKEN_CACHE["expiry"] = now + payload.get("expires_in", 3500)
    return _TOKEN_CACHE["token"]


# ────────────────────────────────────────────────────────────────────────────
# MCP catalog probe (single shot, cached per pytest session)
# ────────────────────────────────────────────────────────────────────────────
def _mcp_call(url: str, payload: dict, token: str) -> str:
    """POST to an MCP server with retry-with-backoff on 429/5xx/timeout."""
    backoffs = (3, 7, 15)  # 4 attempts total → ~25s worst-case before final raise
    last_exc: Exception | None = None
    for attempt in range(len(backoffs) + 1):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(), method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": f"Bearer {token}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode()
        except urllib.error.HTTPError as e:
            last_exc = e
            if e.code in (429, 502, 503, 504) and attempt < len(backoffs):
                time.sleep(backoffs[attempt]); continue
            raise
        except urllib.error.URLError as e:
            last_exc = e
            if attempt < len(backoffs):
                time.sleep(backoffs[attempt]); continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("unreachable")


def _sse_last_json(body: str) -> dict | None:
    matches = re.findall(r"^data:\s*(.+)$", body, flags=re.MULTILINE)
    if not matches:
        return None
    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError:
        return None


_CATALOG_CACHE: dict[str, Any] = {}


def get_catalog(refresh: bool = False) -> dict[str, dict[str, Any]]:
    """Return `{component_name: full_catalog_entry}` from a live catalog.list.

    Cached per process. Pass `refresh=True` to invalidate.
    """
    if not refresh and "by_name" in _CATALOG_CACHE:
        return _CATALOG_CACHE["by_name"]

    token = get_sp_token()
    url = APIM_BASE + "/mcp/catalog/mcp"
    _mcp_call(url, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "evals", "version": "1.0"}},
    }, token)
    _mcp_call(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, token)
    body = _mcp_call(url, {
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "catalog.list", "arguments": {"provisionable_only": True}},
    }, token)
    rpc = _sse_last_json(body) or {}
    entries: dict[str, dict[str, Any]] = {}
    for item in (rpc.get("result", {}) or {}).get("content", []) or []:
        text = item.get("text") or ""
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "name" in obj:
            entries[obj["name"]] = obj
    _CATALOG_CACHE["by_name"] = entries
    return entries


# ────────────────────────────────────────────────────────────────────────────
# OAM YAML inspection
# ────────────────────────────────────────────────────────────────────────────
@dataclass
class ComponentTuple:
    name: str
    type: str


def parse_oam(yaml_text: str) -> dict:
    """Strict-parse OAM YAML. Raises yaml.YAMLError on invalid input."""
    return yaml.safe_load(yaml_text)


def components(oam: dict) -> list[ComponentTuple]:
    out: list[ComponentTuple] = []
    for c in ((oam or {}).get("spec", {}) or {}).get("components", []) or []:
        out.append(ComponentTuple(name=c.get("name") or "", type=c.get("type") or ""))
    return out


def types(oam: dict) -> set[str]:
    return {c.type for c in components(oam) if c.type}


# ────────────────────────────────────────────────────────────────────────────
# Architecture inspection (to compute coverage ratio)
# ────────────────────────────────────────────────────────────────────────────
def count_architecture_elements(slug: str) -> int:
    """Best-effort count of *distinct* architectural elements across
    application_arch + data_arch + infrastructure_arch.

    Heuristic: walks the JSONB, counts items in any array whose siblings
    include a `name` field. Conservative — designed to give a lower bound
    on capability count for the coverage ratio assertion.
    """
    total = 0
    for type_name in ("application_arch", "data_arch", "infrastructure_arch"):
        doc = db_jsonb_value(
            f"SELECT content FROM architecture.artifacts "
            f"WHERE project_id=(SELECT id FROM architecture.projects WHERE slug='{slug}') "
            f"AND type='{type_name}' ORDER BY version DESC LIMIT 1"
        )
        total += _walk_named_items(doc)
    return max(total, 1)


def _walk_named_items(node: Any) -> int:
    n = 0
    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and "name" in item:
                n += 1
            else:
                n += _walk_named_items(item)
    elif isinstance(node, dict):
        for v in node.values():
            n += _walk_named_items(v)
    return n


# ────────────────────────────────────────────────────────────────────────────
# Dry-run-result decode
# ────────────────────────────────────────────────────────────────────────────
def dry_run_ok(dry_run_field: Any) -> bool | None:
    """The agent persists dry_run as the raw MCP response: {content:[{text:"<json>"}]}.

    Returns the inner `ok` flag, or None when shape is unrecognised.
    """
    if not isinstance(dry_run_field, dict):
        return None
    content = dry_run_field.get("content") or []
    if not content:
        return None
    text = content[0].get("text") if isinstance(content[0], dict) else None
    if not text:
        return None
    try:
        return json.loads(text).get("ok")
    except json.JSONDecodeError:
        return None


# ────────────────────────────────────────────────────────────────────────────
# Naming-convention check
# ────────────────────────────────────────────────────────────────────────────
def name_follows_convention(name: str, slug: str) -> bool:
    return name.startswith(f"{slug}-") or name.startswith("shared-")
