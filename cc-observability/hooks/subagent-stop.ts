#!/usr/bin/env npx tsx
/**
 * subagent-stop.ts -- SubagentStop hook
 *
 * Fired when a sub-agent completes.
 * Extracts agent id and completion status.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const agentId =
    input.agent_id ||
    input.id ||
    input.subagent?.id ||
    null;
  const status =
    input.status ||
    input.completion_status ||
    input.subagent?.status ||
    "completed";
  const inputTokens = input.usage?.input_tokens ?? input.input_tokens ?? null;
  const outputTokens = input.usage?.output_tokens ?? input.output_tokens ?? null;

  const summary = `SubagentStop: ${agentId ? `id=${agentId}, ` : ""}status=${status}`;

  await sendEvent("SubagentStop", {
    session_id: getSessionId(input),
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
