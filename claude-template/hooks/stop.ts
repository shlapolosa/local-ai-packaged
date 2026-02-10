#!/usr/bin/env npx tsx
/**
 * stop.ts -- Stop hook
 *
 * Fired when Claude Code stops generating a response.
 * Extracts stop reason, token usage, and a summary of the last message.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const stopReason = input.stop_reason || input.reason || "unknown";
  const inputTokens = input.usage?.input_tokens ?? input.input_tokens ?? null;
  const outputTokens = input.usage?.output_tokens ?? input.output_tokens ?? null;
  const modelName = input.model || input.model_name || null;

  // Try to get last message content for summary
  let lastMessage = "";
  if (input.messages && Array.isArray(input.messages) && input.messages.length > 0) {
    const last = input.messages[input.messages.length - 1];
    if (typeof last.content === "string") {
      lastMessage = last.content;
    } else if (typeof last.text === "string") {
      lastMessage = last.text;
    }
  } else if (input.content && typeof input.content === "string") {
    lastMessage = input.content;
  }

  const summary = lastMessage
    ? `Stop (${stopReason}): ${truncate(lastMessage, 400)}`
    : `Stop: ${stopReason}`;

  await sendEvent("Stop", {
    session_id: getSessionId(input),
    model_name: modelName,
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
