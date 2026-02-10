#!/usr/bin/env npx tsx
/**
 * subagent-start.ts -- SubagentStart hook
 *
 * Fired when Claude Code spawns a sub-agent (e.g. a Task agent).
 * Extracts agent type and agent id.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const agentType =
    input.agent_type ||
    input.type ||
    input.subagent?.type ||
    "unknown";
  const agentId =
    input.agent_id ||
    input.id ||
    input.subagent?.id ||
    null;
  const modelName =
    input.model ||
    input.model_name ||
    input.subagent?.model ||
    null;

  const summary = `SubagentStart: type=${agentType}${agentId ? `, id=${agentId}` : ""}`;

  await sendEvent("SubagentStart", {
    session_id: getSessionId(input),
    model_name: modelName,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
