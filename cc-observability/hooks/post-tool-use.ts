#!/usr/bin/env npx tsx
/**
 * post-tool-use.ts -- PostToolUse hook
 *
 * Fired after a tool executes successfully.
 * Extracts tool name and a truncated result summary.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const toolName = input.tool?.name || input.tool_name || null;
  const toolResult = input.tool?.output || input.tool_result || input.result || input.output || "";

  // Build result summary
  const resultStr = typeof toolResult === "string"
    ? toolResult
    : JSON.stringify(toolResult);
  const summary = `PostToolUse: ${toolName || "unknown"} -> ${truncate(resultStr, 450)}`;

  await sendEvent("PostToolUse", {
    session_id: getSessionId(input),
    tool_name: toolName,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
