#!/usr/bin/env npx tsx
/**
 * send-event.ts -- Central event dispatcher
 *
 * Reads JSON from stdin, accepts --event-type <type> as a CLI argument,
 * and POSTs a structured event to the cc-observability server.
 *
 * Usage:
 *   echo '{"tool":{"name":"Read"}}' | npx tsx send-event.ts --event-type PreToolUse
 *
 * Always exits 0 regardless of errors.
 */

import { createHash } from "crypto";
import { execSync } from "child_process";
import { readFileSync, existsSync } from "fs";
import { userInfo, hostname } from "os";

async function main(): Promise<void> {
  // ── Parse CLI args ───────────────────────────────────────────────────────
  const args = process.argv.slice(2);
  let eventType = "Unknown";
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--event-type" && args[i + 1]) {
      eventType = args[i + 1];
      break;
    }
  }

  // ── Read stdin ───────────────────────────────────────────────────────────
  const input = await readStdinRaw();

  // ── Environment ──────────────────────────────────────────────────────────
  const observabilityUrl = process.env.CC_OBSERVABILITY_URL?.replace(/\/+$/, "");
  if (!observabilityUrl) {
    process.exit(0);
  }

  const projectId = getProjectId();
  const contributorId = getContributorId();
  const storyId = getActiveStoryId();
  const sessionId =
    input.session_id ||
    input.sessionId ||
    input.session?.id ||
    input.session?.session_id ||
    `session-${Date.now()}`;

  // ── Extract fields ───────────────────────────────────────────────────────
  const toolName =
    input.tool_name ||
    input.tool?.name ||
    input.tool ||
    null;
  const modelName = input.model || input.model_name || null;
  const inputTokens = input.usage?.input_tokens ?? input.input_tokens ?? 0;
  const outputTokens = input.usage?.output_tokens ?? input.output_tokens ?? 0;

  // ── Build summary ────────────────────────────────────────────────────────
  let summary: string | null = null;
  if (toolName && typeof toolName === "string") {
    summary = `${eventType}: ${toolName}`;
  } else if (input.stop_reason) {
    summary = `Stop: ${input.stop_reason}`;
  } else if (input.message && typeof input.message === "string") {
    summary = input.message.substring(0, 200);
  } else {
    summary = eventType;
  }

  // ── POST to server ───────────────────────────────────────────────────────
  const body = {
    project_id: projectId,
    contributor_id: contributorId,
    session_id: sessionId,
    story_id: storyId,
    hook_event_type: eventType,
    payload: input,
    tool_name: typeof toolName === "string" ? toolName : null,
    model_name: modelName,
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    summary,
    timestamp: new Date().toISOString(),
  };

  try {
    await fetch(`${observabilityUrl}/api/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(5000),
    });
  } catch {
    // Silently swallow
  }
}

// ─── Helpers (self-contained, no imports from lib.ts) ────────────────────────

async function readStdinRaw(): Promise<Record<string, any>> {
  return new Promise((resolve) => {
    const chunks: Buffer[] = [];
    process.stdin.on("data", (chunk: Buffer) => chunks.push(chunk));
    process.stdin.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf-8").trim();
      if (!raw) { resolve({}); return; }
      try { resolve(JSON.parse(raw)); } catch { resolve({ _raw: raw }); }
    });
    process.stdin.on("error", () => resolve({}));
    setTimeout(() => resolve({}), 2000);
  });
}

function getProjectId(): string {
  if (process.env.CC_PROJECT_ID) return process.env.CC_PROJECT_ID;
  try {
    const url = execSync("git remote get-url origin", {
      encoding: "utf-8", timeout: 5000, stdio: ["pipe", "pipe", "pipe"],
    }).trim();
    const m = url.match(/\/([^/]+?)(?:\.git)?$/) || url.match(/:([^/]+?)(?:\.git)?$/);
    return m ? m[1] : url;
  } catch {
    return process.cwd().split("/").pop() || "unknown";
  }
}

function getContributorId(): string {
  if (process.env.CC_CONTRIBUTOR_ID) return process.env.CC_CONTRIBUTOR_ID;
  try {
    const hash = createHash("sha256")
      .update(userInfo().username + hostname())
      .digest("hex");
    return hash.substring(0, 12);
  } catch { return "anonymous"; }
}

function getActiveStoryId(): string | null {
  try {
    const path = "/tmp/.cc_active_story";
    if (existsSync(path)) {
      return readFileSync(path, "utf-8").trim() || null;
    }
  } catch {}
  return null;
}

// ─── Entry ───────────────────────────────────────────────────────────────────

main().catch(() => {}).finally(() => process.exit(0));
