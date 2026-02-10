import type { Database } from "bun:sqlite";
import type { BroadcastFn } from "../types";

/**
 * GET /api/v1/spans
 *
 * Query OTEL spans with optional filters:
 *   trace_id, service_name, name (span name), limit (default 200)
 */
export function handleGetSpans(
  req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const url = new URL(req.url);
  const traceId = url.searchParams.get("trace_id");
  const serviceName = url.searchParams.get("service_name");
  const name = url.searchParams.get("name");
  const limit = Math.min(
    Math.max(parseInt(url.searchParams.get("limit") || "200", 10), 1),
    1000,
  );

  const conditions: string[] = [];
  const params: unknown[] = [];

  if (traceId) {
    conditions.push("trace_id = ?");
    params.push(traceId);
  }
  if (serviceName) {
    conditions.push("service_name = ?");
    params.push(serviceName);
  }
  if (name) {
    conditions.push("name = ?");
    params.push(name);
  }

  const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
  params.push(limit);

  const rows = db
    .prepare(
      `SELECT * FROM spans ${where} ORDER BY start_time_unix_nano ASC LIMIT ?`,
    )
    .all(...params);

  return jsonResponse(rows);
}

/**
 * GET /api/v1/traces
 *
 * List unique traces with summary metadata.
 * Optional filters: service_name, limit (default 50)
 */
export function handleGetTraces(
  req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const url = new URL(req.url);
  const serviceName = url.searchParams.get("service_name");
  const limit = Math.min(
    Math.max(parseInt(url.searchParams.get("limit") || "50", 10), 1),
    200,
  );

  const conditions: string[] = [];
  const params: unknown[] = [];

  if (serviceName) {
    conditions.push("service_name = ?");
    params.push(serviceName);
  }

  const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
  params.push(limit);

  const rows = db
    .prepare(
      `SELECT
         trace_id,
         service_name,
         COUNT(*) as span_count,
         MIN(start_time_unix_nano) as first_span,
         MAX(end_time_unix_nano) as last_span,
         CASE
           WHEN MAX(end_time_unix_nano) IS NOT NULL AND MIN(start_time_unix_nano) IS NOT NULL
           THEN (CAST(MAX(end_time_unix_nano) AS REAL) - CAST(MIN(start_time_unix_nano) AS REAL)) / 1000000
           ELSE NULL
         END as duration_ms,
         SUM(CASE WHEN status_code = 2 THEN 1 ELSE 0 END) as error_count
       FROM spans
       ${where}
       GROUP BY trace_id
       ORDER BY MIN(start_time_unix_nano) DESC
       LIMIT ?`,
    )
    .all(...params);

  return jsonResponse(rows);
}

/**
 * GET /api/v1/traces/:trace_id
 *
 * All spans for a specific trace, ordered by start_time.
 */
export function handleGetTraceById(
  _req: Request,
  db: Database,
  _broadcast: BroadcastFn,
  traceId: string,
): Response {
  const rows = db
    .prepare(
      `SELECT * FROM spans WHERE trace_id = ? ORDER BY start_time_unix_nano ASC`,
    )
    .all(traceId);

  if (rows.length === 0) {
    return jsonResponse({ error: "Trace not found" }, 404);
  }

  return jsonResponse(rows);
}

// ── Helpers ────────────────────────────────────────────────────────────────

function jsonResponse(data: unknown, status: number = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
