#!/usr/bin/env npx tsx
/**
 * notification.ts -- Notification hook
 *
 * Fired when Claude Code sends a notification (e.g. task complete, waiting for input).
 * Extracts the notification message.
 */

import { readStdin, sendEvent, getSessionId, truncate } from "./lib.ts";

async function main(): Promise<void> {
  const input = await readStdin();

  const message =
    input.message ||
    input.notification ||
    input.text ||
    input.title ||
    "";
  const messageStr = typeof message === "string"
    ? message
    : JSON.stringify(message);

  const summary = `Notification: ${truncate(messageStr, 450)}`;

  await sendEvent("Notification", {
    session_id: getSessionId(input),
    summary: truncate(summary, 500),
    payload: input,
  });
}

main().catch(() => {}).finally(() => process.exit(0));
