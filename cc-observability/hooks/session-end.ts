#!/usr/bin/env npx tsx
/**
 * session-end.ts -- SessionEnd hook
 *
 * Fired when a Claude Code session ends.
 * Extracts end reason, duration, and final token tallies.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const endReason =
    input.end_reason ||
    input.reason ||
    input.stop_reason ||
    "unknown";

  const duration = input.duration || input.duration_ms || null;
  const inputTokens = input.usage?.input_tokens ?? input.total_input_tokens ?? null;
  const outputTokens = input.usage?.output_tokens ?? input.total_output_tokens ?? null;
  const modelName = input.model || input.model_name || null;

  let summary = `SessionEnd: ${endReason}`;
  if (duration) {
    const seconds = typeof duration === "number" && duration > 1000
      ? `${(duration / 1000).toFixed(1)}s`
      : `${duration}`;
    summary += `, duration=${seconds}`;
  }
  if (inputTokens || outputTokens) {
    summary += `, tokens=${inputTokens ?? 0}in/${outputTokens ?? 0}out`;
  }

  await sendEvent("SessionEnd", {
    session_id: getSessionId(input),
    model_name: modelName,
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
