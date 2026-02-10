#!/usr/bin/env npx tsx
/**
 * session-start.ts -- SessionStart hook
 *
 * Fired when a new Claude Code session begins.
 * Extracts model name and session metadata.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const modelName =
    input.model ||
    input.model_name ||
    input.config?.model ||
    null;

  const cwd = input.cwd || input.working_directory || process.cwd();

  const summary = modelName
    ? `SessionStart: model=${modelName}, cwd=${cwd}`
    : `SessionStart: cwd=${cwd}`;

  await sendEvent("SessionStart", {
    session_id: getSessionId(input),
    model_name: modelName,
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
