#!/usr/bin/env npx tsx
/**
 * post-tool-use-failure.ts -- PostToolUseFailure hook
 *
 * Fired when a tool execution fails.
 * Extracts tool name and the error message.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const toolName = input.tool?.name || input.tool_name || null;
  const error =
    input.error ||
    input.tool?.error ||
    input.message ||
    input.reason ||
    "Unknown error";
  const errorStr = typeof error === "string" ? error : JSON.stringify(error);

  const summary = `PostToolUseFailure: ${toolName || "unknown"} -- ${truncate(errorStr, 400)}`;

  await sendEvent("PostToolUseFailure", {
    session_id: getSessionId(input),
    tool_name: toolName,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
