import type { Database } from "bun:sqlite";
import type { BroadcastFn, EventPayload } from "../types";
import type { SQLiteSpanExporter } from "../otel/sqlite-exporter";
import { SpanKind, SpanStatusCode } from "@opentelemetry/api";

// Will be set by index.ts after OTEL init
let spanExporter: SQLiteSpanExporter | null = null;

export function setSpanExporter(exporter: SQLiteSpanExporter): void {
  spanExporter = exporter;
}

/**
 * POST /api/events
 *
 * Ingests a single event.  Auto-creates project, contributor, and session
 * rows when they do not yet exist, then inserts the event and broadcasts
 * it to all connected WebSocket clients.
 *
 * Also creates/completes OTEL spans:
 * - PreToolUse → opens a new span
 * - PostToolUse / PostToolUseFailure → completes the matching span
 * - Standalone events → creates an instant span (start = end)
 */
export async function handlePostEvent(
  req: Request,
  db: Database,
  broadcast: BroadcastFn,
): Promise<Response> {
  let body: EventPayload;
  try {
    body = (await req.json()) as EventPayload;
  } catch {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  // Validate required fields
  if (!body.project_id || !body.contributor_id || !body.session_id || !body.hook_event_type) {
    return jsonResponse(
      { error: "Missing required fields: project_id, contributor_id, session_id, hook_event_type" },
      400,
    );
  }

  const now = new Date().toISOString();

  // ── Auto-create project ────────────────────────────────────────────────
  db.prepare(
    `INSERT INTO projects (project_id, display_name, first_seen_at, last_active_at)
     VALUES (?, ?, ?, ?)
     ON CONFLICT(project_id) DO UPDATE SET last_active_at = excluded.last_active_at`,
  ).run(body.project_id, body.project_id, now, now);

  // ── Auto-create contributor ────────────────────────────────────────────
  db.prepare(
    `INSERT INTO contributors (contributor_id, display_name, first_seen_at, last_active_at)
     VALUES (?, ?, ?, ?)
     ON CONFLICT(contributor_id) DO UPDATE SET last_active_at = excluded.last_active_at`,
  ).run(body.contributor_id, body.contributor_id, now, now);

  // ── Auto-create session ────────────────────────────────────────────────
  db.prepare(
    `INSERT INTO sessions (session_id, project_id, contributor_id, story_id, model_name, started_at)
     VALUES (?, ?, ?, ?, ?, ?)
     ON CONFLICT(session_id) DO NOTHING`,
  ).run(
    body.session_id,
    body.project_id,
    body.contributor_id,
    body.story_id ?? null,
    body.model_name ?? "",
    now,
  );

  // ── Insert event ───────────────────────────────────────────────────────
  const payloadStr = typeof body.payload === "string" ? body.payload : JSON.stringify(body.payload ?? {});
  const inputTokens = body.input_tokens ?? 0;
  const outputTokens = body.output_tokens ?? 0;

  const result = db.prepare(
    `INSERT INTO events
       (project_id, contributor_id, session_id, story_id,
        hook_event_type, payload, chat, summary, tool_name, model_name,
        timestamp, input_tokens, output_tokens)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  ).run(
    body.project_id,
    body.contributor_id,
    body.session_id,
    body.story_id ?? null,
    body.hook_event_type,
    payloadStr,
    body.chat ?? null,
    body.summary ?? null,
    body.tool_name ?? null,
    body.model_name ?? null,
    now,
    inputTokens,
    outputTokens,
  );

  const eventId = Number(result.lastInsertRowid);

  // ── Update session token totals ────────────────────────────────────────
  if (inputTokens > 0 || outputTokens > 0) {
    db.prepare(
      `UPDATE sessions
       SET total_input_tokens  = total_input_tokens  + ?,
           total_output_tokens = total_output_tokens + ?
       WHERE session_id = ?`,
    ).run(inputTokens, outputTokens, body.session_id);
  }

  // ── Update story token totals (if linked) ──────────────────────────────
  if (body.story_id && (inputTokens > 0 || outputTokens > 0)) {
    db.prepare(
      `UPDATE stories
       SET total_input_tokens  = total_input_tokens  + ?,
           total_output_tokens = total_output_tokens + ?
       WHERE story_id = ?`,
    ).run(inputTokens, outputTokens, body.story_id);
  }

  // ── Create/complete OTEL span ──────────────────────────────────────────
  if (spanExporter) {
    try {
      createOrCompleteSpan(body, payloadStr, now, inputTokens, outputTokens);
    } catch (err) {
      console.error("[otel] span creation error:", err);
    }
  }

  // ── Broadcast to WebSocket clients ─────────────────────────────────────
  broadcast({
    type: "event",
    data: {
      id: eventId,
      project_id: body.project_id,
      contributor_id: body.contributor_id,
      session_id: body.session_id,
      story_id: body.story_id ?? null,
      hook_event_type: body.hook_event_type,
      tool_name: body.tool_name ?? null,
      model_name: body.model_name ?? null,
      timestamp: now,
      input_tokens: inputTokens,
      output_tokens: outputTokens,
    },
  });

  return jsonResponse({ id: eventId }, 201);
}

/**
 * Create or complete an OTEL span based on the event type.
 */
function createOrCompleteSpan(
  body: EventPayload,
  payloadStr: string,
  timestamp: string,
  inputTokens: number,
  outputTokens: number,
): void {
  if (!spanExporter) return;

  let payload: Record<string, unknown> = {};
  try {
    payload = JSON.parse(payloadStr);
  } catch {}

  const nowNano = isoToNano(timestamp);
  // Use session_id as trace_id (padded/hashed to 32 hex chars)
  const traceId = sessionToTraceId(body.session_id);
  const toolUseId = payload.tool_use_id as string | undefined;

  if (body.hook_event_type === "PreToolUse" && toolUseId) {
    // Open a new span
    const spanId = toolUseIdToSpanId(toolUseId);
    const toolName = (payload.tool_name as string) || body.tool_name || "unknown";
    const toolInput = payload.tool_input
      ? JSON.stringify(payload.tool_input)
      : null;

    const attrs: Record<string, unknown> = {
      "tool.name": toolName,
      "hook.event_type": body.hook_event_type,
    };
    if (body.model_name) attrs["gen_ai.request.model"] = body.model_name;

    spanExporter.insertOpenSpan({
      traceId,
      spanId,
      parentSpanId: null,
      name: toolName,
      kind: SpanKind.INTERNAL,
      startTimeUnixNano: nowNano,
      serviceName: body.project_id,
      serviceInstanceId: body.contributor_id,
      toolName,
      modelName: body.model_name || null,
      inputTokens,
      outputTokens,
      storyId: body.story_id || null,
      attributes: JSON.stringify(attrs),
      resourceAttributes: JSON.stringify({
        "service.name": body.project_id,
        "service.instance.id": body.contributor_id,
      }),
      inputPayload: toolInput,
    });
  } else if (
    (body.hook_event_type === "PostToolUse" || body.hook_event_type === "PostToolUseFailure") &&
    toolUseId
  ) {
    // Complete an existing span
    const spanId = toolUseIdToSpanId(toolUseId);
    const isError = body.hook_event_type === "PostToolUseFailure";
    const toolResponse = payload.tool_response
      ? JSON.stringify(payload.tool_response)
      : null;

    const attrs: Record<string, unknown> = {
      "hook.event_type": body.hook_event_type,
    };
    if (body.model_name) attrs["gen_ai.request.model"] = body.model_name;

    spanExporter.completeSpan({
      spanId,
      endTimeUnixNano: nowNano,
      statusCode: isError ? SpanStatusCode.ERROR : SpanStatusCode.OK,
      statusMessage: isError ? (payload.error as string) || "Tool use failed" : null,
      outputPayload: toolResponse,
      outputTokens,
      inputTokens,
      attributes: JSON.stringify(attrs),
      events: null,
    });
  } else {
    // Standalone event → instant span (start = end, duration = 0)
    const spanId = generateSpanId();
    const name = body.hook_event_type;

    const attrs: Record<string, unknown> = {
      "hook.event_type": body.hook_event_type,
    };
    if (body.tool_name) attrs["tool.name"] = body.tool_name;
    if (body.model_name) attrs["gen_ai.request.model"] = body.model_name;

    spanExporter.insertOpenSpan({
      traceId,
      spanId,
      parentSpanId: null,
      name,
      kind: SpanKind.INTERNAL,
      startTimeUnixNano: nowNano,
      serviceName: body.project_id,
      serviceInstanceId: body.contributor_id,
      toolName: body.tool_name || null,
      modelName: body.model_name || null,
      inputTokens,
      outputTokens,
      storyId: body.story_id || null,
      attributes: JSON.stringify(attrs),
      resourceAttributes: JSON.stringify({
        "service.name": body.project_id,
        "service.instance.id": body.contributor_id,
      }),
      inputPayload: payloadStr !== "{}" ? payloadStr : null,
    });

    // Immediately close it
    spanExporter.completeSpan({
      spanId,
      endTimeUnixNano: nowNano,
      startTimeUnixNano: nowNano,
      statusCode: SpanStatusCode.OK,
      statusMessage: null,
      outputPayload: null,
      outputTokens: 0,
      inputTokens: 0,
      attributes: null,
      events: null,
    });
  }
}

/**
 * GET /api/events
 *
 * Query events with optional filters:
 *   project_id, contributor_id, session_id, story_id,
 *   type (hook_event_type), since (ISO timestamp), limit (default 100)
 */
export function handleGetEvents(
  req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const url = new URL(req.url);
  const projectId = url.searchParams.get("project_id");
  const contributorId = url.searchParams.get("contributor_id");
  const sessionId = url.searchParams.get("session_id");
  const storyId = url.searchParams.get("story_id");
  const eventType = url.searchParams.get("type");
  const since = url.searchParams.get("since");
  const limit = Math.min(Math.max(parseInt(url.searchParams.get("limit") || "100", 10), 1), 1000);

  const conditions: string[] = [];
  const params: unknown[] = [];

  if (projectId) {
    conditions.push("project_id = ?");
    params.push(projectId);
  }
  if (contributorId) {
    conditions.push("contributor_id = ?");
    params.push(contributorId);
  }
  if (sessionId) {
    conditions.push("session_id = ?");
    params.push(sessionId);
  }
  if (storyId) {
    conditions.push("story_id = ?");
    params.push(storyId);
  }
  if (eventType) {
    conditions.push("hook_event_type = ?");
    params.push(eventType);
  }
  if (since) {
    conditions.push("timestamp >= ?");
    params.push(since);
  }

  const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
  params.push(limit);

  const rows = db
    .prepare(`SELECT * FROM events ${where} ORDER BY timestamp DESC LIMIT ?`)
    .all(...params);

  return jsonResponse(rows);
}

// ── Helpers ────────────────────────────────────────────────────────────────

function jsonResponse(data: unknown, status: number = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/**
 * Convert session_id (UUID) to a 32-char hex trace_id.
 * Strips dashes from UUID. If not a UUID, pads/truncates to 32 chars.
 */
function sessionToTraceId(sessionId: string): string {
  const hex = sessionId.replace(/-/g, "");
  if (hex.length >= 32) return hex.substring(0, 32);
  return hex.padEnd(32, "0");
}

/**
 * Convert tool_use_id to a 16-char hex span_id.
 * Uses last 16 hex chars of the tool_use_id.
 */
function toolUseIdToSpanId(toolUseId: string): string {
  const hex = toolUseId.replace(/[^0-9a-fA-F]/g, "");
  if (hex.length >= 16) return hex.substring(hex.length - 16, hex.length);
  return hex.padStart(16, "0");
}

/**
 * Generate a random 16-char hex span_id for standalone events.
 */
function generateSpanId(): string {
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Convert ISO timestamp to nanosecond string.
 */
function isoToNano(iso: string): string {
  const ms = new Date(iso).getTime();
  return String(BigInt(ms) * 1_000_000n);
}
