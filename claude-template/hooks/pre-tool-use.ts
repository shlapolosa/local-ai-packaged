#!/usr/bin/env npx tsx
/**
 * pre-tool-use.ts -- PreToolUse hook
 *
 * Fired before Claude Code executes a tool.
 * Extracts tool name and a brief summary of the tool input.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const toolName = input.tool?.name || input.tool_name || null;
  const toolInput = input.tool?.input || input.tool_input || input.input || {};

  // Build a brief summary of what is about to be executed
  let summary = `PreToolUse: ${toolName || "unknown"}`;
  if (typeof toolInput === "object" && toolInput !== null) {
    const keys = Object.keys(toolInput);
    if (keys.length > 0) {
      const preview = keys.slice(0, 3).join(", ");
      summary += ` (${preview})`;
    }
  }

  await sendEvent("PreToolUse", {
    session_id: getSessionId(input),
    tool_name: toolName,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
