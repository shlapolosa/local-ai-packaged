#!/usr/bin/env npx tsx
/**
 * permission-request.ts -- PermissionRequest hook
 *
 * Fired when Claude Code requests permission to execute a tool or action.
 * Extracts the permission type and the tool requesting permission.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const permissionType =
    input.permission_type ||
    input.type ||
    input.permission?.type ||
    "unknown";
  const toolName =
    input.tool_name ||
    input.tool?.name ||
    input.permission?.tool_name ||
    null;
  const description =
    input.description ||
    input.permission?.description ||
    input.message ||
    "";

  let summary = `PermissionRequest: ${permissionType}`;
  if (toolName) {
    summary += ` for ${toolName}`;
  }
  if (description) {
    summary += ` -- ${truncate(typeof description === "string" ? description : JSON.stringify(description), 300)}`;
  }

  await sendEvent("PermissionRequest", {
    session_id: getSessionId(input),
    tool_name: toolName,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
