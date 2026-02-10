import { trace } from "@opentelemetry/api";
import {
  BasicTracerProvider,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace-base";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import type { Database } from "bun:sqlite";
import { SQLiteSpanExporter } from "./sqlite-exporter";

let sqliteExporter: SQLiteSpanExporter | null = null;

/**
 * Initialize the OpenTelemetry TracerProvider.
 *
 * - Always adds SQLiteSpanExporter to write spans to the local DB.
 * - Optionally adds OTLPTraceExporter if OTEL_EXPORTER_OTLP_ENDPOINT is set
 *   (for forwarding to Jaeger, Grafana Tempo, etc.).
 *
 * Returns the SQLiteSpanExporter for direct span manipulation
 * (open/complete pattern used by event ingestion).
 */
export function initOtel(db: Database): SQLiteSpanExporter {
  const resource = resourceFromAttributes({
    [ATTR_SERVICE_NAME]: "cc-observability",
  });

  // Primary exporter: SQLite
  sqliteExporter = new SQLiteSpanExporter(db);
  const spanProcessors = [new SimpleSpanProcessor(sqliteExporter)];

  // Optional: OTLP exporter for Jaeger / Tempo
  const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
  if (otlpEndpoint) {
    const otlpExporter = new OTLPTraceExporter({ url: `${otlpEndpoint}/v1/traces` });
    spanProcessors.push(new SimpleSpanProcessor(otlpExporter));
    console.log(`[otel] OTLP exporter enabled → ${otlpEndpoint}`);
  }

  const provider = new BasicTracerProvider({ resource, spanProcessors });
  trace.setGlobalTracerProvider(provider);
  console.log("[otel] TracerProvider initialized with SQLite exporter");

  return sqliteExporter;
}

/**
 * Get a tracer instance for creating spans via the OTEL SDK.
 */
export function getTracer(name: string = "cc-observability") {
  return trace.getTracer(name);
}

export function getSQLiteExporter(): SQLiteSpanExporter | null {
  return sqliteExporter;
}
