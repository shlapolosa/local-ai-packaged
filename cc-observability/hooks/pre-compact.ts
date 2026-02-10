#!/usr/bin/env npx tsx
/**
 * pre-compact.ts -- PreCompact hook
 *
 * Fired before Claude Code compacts the conversation context.
 * Extracts context size information.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const contextSize =
    input.context_size ||
    input.token_count ||
    input.total_tokens ||
    null;
  const maxTokens =
    input.max_tokens ||
    input.context_window ||
    null;
  const messageCount =
    input.message_count ||
    input.messages?.length ||
    null;

  let summary = "PreCompact";
  const parts: string[] = [];
  if (contextSize) parts.push(`tokens=${contextSize}`);
  if (maxTokens) parts.push(`max=${maxTokens}`);
  if (messageCount) parts.push(`messages=${messageCount}`);
  if (parts.length > 0) {
    summary += `: ${parts.join(", ")}`;
  }

  await sendEvent("PreCompact", {
    session_id: getSessionId(input),
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
