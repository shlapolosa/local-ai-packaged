#!/usr/bin/env npx tsx
/**
 * user-prompt-submit.ts -- UserPromptSubmit hook
 *
 * Fired when the user submits a prompt.
 * Extracts the first 200 characters of the prompt text as a summary.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const promptText =
    input.prompt ||
    input.message ||
    input.content ||
    input.text ||
    "";
  const promptStr = typeof promptText === "string"
    ? promptText
    : JSON.stringify(promptText);

  const summary = `UserPromptSubmit: ${truncate(promptStr, 200)}`;

  await sendEvent("UserPromptSubmit", {
    session_id: getSessionId(input),
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
