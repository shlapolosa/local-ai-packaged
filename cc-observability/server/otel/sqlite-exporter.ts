import type { SpanExporter, ReadableSpan } from "@opentelemetry/sdk-trace-base";
import { ExportResultCode, type ExportResult } from "@opentelemetry/core";
import type { Database } from "bun:sqlite";

/**
 * Custom OTEL SpanExporter that writes completed spans to SQLite.
 *
 * Called by the TracerProvider's SpanProcessor when `span.end()` is invoked.
 * Handles both INSERT (new spans) and UPDATE (completing open spans).
 */
export class SQLiteSpanExporter implements SpanExporter {
  private db: Database;
  private insertStmt: ReturnType<Database["prepare"]>;
  private updateStmt: ReturnType<Database["prepare"]>;

  constructor(db: Database) {
    this.db = db;

    this.insertStmt = db.prepare(`
      INSERT OR REPLACE INTO spans (
        trace_id, span_id, parent_span_id, trace_state,
        name, kind,
        start_time_unix_nano, end_time_unix_nano, duration_ms,
        status_code, status_message,
        service_name, service_instance_id,
        tool_name, model_name, input_tokens, output_tokens, story_id,
        attributes, events, links, resource_attributes,
        input_payload, output_payload
      ) VALUES (
        ?, ?, ?, ?,
        ?, ?,
        ?, ?, ?,
        ?, ?,
        ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?
      )
    `);

    this.updateStmt = db.prepare(`
      UPDATE spans SET
        end_time_unix_nano = ?,
        duration_ms = ?,
        status_code = ?,
        status_message = ?,
        output_payload = ?,
        output_tokens = CASE WHEN ? > 0 THEN ? ELSE output_tokens END,
        input_tokens = CASE WHEN ? > 0 THEN ? ELSE input_tokens END,
        attributes = ?,
        events = ?
      WHERE span_id = ?
    `);
  }

  export(
    spans: ReadableSpan[],
    resultCallback: (result: ExportResult) => void,
  ): void {
    try {
      const tx = this.db.transaction(() => {
        for (const span of spans) {
          this.writeSpan(span);
        }
      });
      tx();
      resultCallback({ code: ExportResultCode.SUCCESS });
    } catch (err) {
      console.error("[SQLiteSpanExporter] export error:", err);
      resultCallback({ code: ExportResultCode.FAILED });
    }
  }

  async shutdown(): Promise<void> {
    // DB lifecycle managed by main server
  }

  async forceFlush(): Promise<void> {
    // No buffering — writes are synchronous
  }

  private writeSpan(span: ReadableSpan): void {
    const ctx = span.spanContext();
    const attrs = span.attributes;

    const traceId = ctx.traceId;
    const spanId = ctx.spanId;
    const parentSpanId = span.parentSpanId || null;
    const traceState = ctx.traceState?.serialize() || null;

    const startNano = hrTimeToNano(span.startTime);
    const endNano = hrTimeToNano(span.endTime);
    const durationMs =
      (Number(BigInt(endNano) - BigInt(startNano))) / 1_000_000;

    const serviceName =
      (span.resource.attributes["service.name"] as string) || "unknown";
    const serviceInstanceId =
      (span.resource.attributes["service.instance.id"] as string) || "unknown";

    const toolName = (attrs["tool.name"] as string) || null;
    const modelName = (attrs["gen_ai.request.model"] as string) || null;
    const inputTokens = (attrs["gen_ai.usage.input_tokens"] as number) || 0;
    const outputTokens = (attrs["gen_ai.usage.output_tokens"] as number) || 0;
    const storyId = (attrs["story.id"] as string) || null;
    const inputPayload = (attrs["tool.input"] as string) || null;
    const outputPayload = (attrs["tool.output"] as string) || null;

    // Serialize full attributes (excluding large payloads already stored)
    const filteredAttrs: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(attrs)) {
      if (k !== "tool.input" && k !== "tool.output") {
        filteredAttrs[k] = v;
      }
    }

    const eventsJson = span.events.length > 0
      ? JSON.stringify(
          span.events.map((e) => ({
            name: e.name,
            time: hrTimeToNano(e.time),
            attributes: e.attributes || {},
          })),
        )
      : null;

    const linksJson = span.links.length > 0
      ? JSON.stringify(
          span.links.map((l) => ({
            traceId: l.context.traceId,
            spanId: l.context.spanId,
            attributes: l.attributes || {},
          })),
        )
      : null;

    const resourceAttrs = JSON.stringify(span.resource.attributes);

    this.insertStmt.run(
      traceId,
      spanId,
      parentSpanId,
      traceState,
      span.name,
      span.kind,
      startNano,
      endNano,
      durationMs,
      span.status.code,
      span.status.message || null,
      serviceName,
      serviceInstanceId,
      toolName,
      modelName,
      inputTokens,
      outputTokens,
      storyId,
      JSON.stringify(filteredAttrs),
      eventsJson,
      linksJson,
      resourceAttrs,
      inputPayload,
      outputPayload,
    );
  }

  /**
   * Directly insert/update an open span from event data (bypasses OTEL SDK).
   * Used for PreToolUse events where the span hasn't ended yet.
   */
  insertOpenSpan(params: {
    traceId: string;
    spanId: string;
    parentSpanId: string | null;
    name: string;
    kind: number;
    startTimeUnixNano: string;
    serviceName: string;
    serviceInstanceId: string;
    toolName: string | null;
    modelName: string | null;
    inputTokens: number;
    outputTokens: number;
    storyId: string | null;
    attributes: string;
    resourceAttributes: string;
    inputPayload: string | null;
  }): void {
    this.insertStmt.run(
      params.traceId,
      params.spanId,
      params.parentSpanId,
      null, // trace_state
      params.name,
      params.kind,
      params.startTimeUnixNano,
      null, // end_time (open span)
      null, // duration (open span)
      0,    // status_code UNSET
      null, // status_message
      params.serviceName,
      params.serviceInstanceId,
      params.toolName,
      params.modelName,
      params.inputTokens,
      params.outputTokens,
      params.storyId,
      params.attributes,
      null, // events
      null, // links
      params.resourceAttributes,
      params.inputPayload,
      null, // output_payload (not yet)
    );
  }

  /**
   * Complete an open span (set end time, duration, status, output).
   */
  completeSpan(params: {
    spanId: string;
    endTimeUnixNano: string;
    startTimeUnixNano?: string;
    statusCode: number;
    statusMessage: string | null;
    outputPayload: string | null;
    outputTokens: number;
    inputTokens: number;
    attributes: string | null;
    events: string | null;
  }): void {
    // Look up start time if not provided
    let durationMs: number | null = null;
    if (params.startTimeUnixNano) {
      durationMs =
        Number(BigInt(params.endTimeUnixNano) - BigInt(params.startTimeUnixNano)) / 1_000_000;
    } else {
      const row = this.db
        .prepare("SELECT start_time_unix_nano FROM spans WHERE span_id = ?")
        .get(params.spanId) as { start_time_unix_nano: string } | null;
      if (row) {
        durationMs =
          Number(BigInt(params.endTimeUnixNano) - BigInt(row.start_time_unix_nano)) / 1_000_000;
      }
    }

    this.updateStmt.run(
      params.endTimeUnixNano,
      durationMs,
      params.statusCode,
      params.statusMessage,
      params.outputPayload,
      params.outputTokens,
      params.outputTokens,
      params.inputTokens,
      params.inputTokens,
      params.attributes,
      params.events,
      params.spanId,
    );
  }
}

/**
 * Convert OTEL HrTime [seconds, nanoseconds] to nanosecond string.
 */
function hrTimeToNano(hrTime: [number, number]): string {
  const [sec, nano] = hrTime;
  return String(BigInt(sec) * 1_000_000_000n + BigInt(nano));
}
