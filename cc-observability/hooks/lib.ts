/**
 * cc-observability hooks -- shared utilities
 *
 * This module provides common functions used by every hook script.
 * It relies exclusively on Node.js built-in APIs (no npm dependencies).
 */

import { createHash } from "crypto";
import { execSync } from "child_process";
import { readFileSync, existsSync, writeFileSync, unlinkSync } from "fs";
import { userInfo, hostname } from "os";

// ─── Constants ───────────────────────────────────────────────────────────────

const STORY_FILE = "/tmp/.cc_active_story";

// ─── stdin ───────────────────────────────────────────────────────────────────

/**
 * Reads all data from stdin and parses it as JSON.
 * Returns an empty object if stdin is empty or contains invalid JSON.
 */
export async function readStdin(): Promise<Record<string, any>> {
  return new Promise((resolve) => {
    const chunks: Buffer[] = [];
    process.stdin.on("data", (chunk: Buffer) => chunks.push(chunk));
    process.stdin.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf-8").trim();
      if (!raw) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch {
        resolve({ _raw: raw });
      }
    });
    process.stdin.on("error", () => resolve({}));

    // If stdin is already ended (e.g. piped empty), force resolution after a short timeout
    setTimeout(() => resolve({}), 2000);
  });
}

// ─── Environment helpers ─────────────────────────────────────────────────────

/**
 * Returns the observability server URL from the CC_OBSERVABILITY_URL env var.
 * Returns null if the variable is not set (hooks should silently skip).
 */
export function getObservabilityUrl(): string | null {
  return process.env.CC_OBSERVABILITY_URL?.replace(/\/+$/, "") || null;
}

/**
 * Returns the project ID.
 *
 * Priority:
 *   1. CC_PROJECT_ID env var
 *   2. Derived from `git remote get-url origin`
 *   3. Basename of the current working directory
 */
export function getProjectId(): string {
  if (process.env.CC_PROJECT_ID) {
    return process.env.CC_PROJECT_ID;
  }

  try {
    const remoteUrl = execSync("git remote get-url origin", {
      encoding: "utf-8",
      timeout: 5000,
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();

    // Extract repo name from URL patterns like:
    //   git@github.com:user/repo.git
    //   https://github.com/user/repo.git
    const match = remoteUrl.match(/\/([^/]+?)(?:\.git)?$/) || remoteUrl.match(/:([^/]+?)(?:\.git)?$/);
    if (match) {
      return match[1];
    }
    return remoteUrl;
  } catch {
    // Fallback to cwd basename
    const cwd = process.cwd();
    return cwd.split("/").pop() || "unknown-project";
  }
}

/**
 * Returns the contributor ID.
 *
 * Priority:
 *   1. CC_CONTRIBUTOR_ID env var
 *   2. sha256(username + hostname) truncated to 12 hex characters
 */
export function getContributorId(): string {
  if (process.env.CC_CONTRIBUTOR_ID) {
    return process.env.CC_CONTRIBUTOR_ID;
  }

  try {
    const user = userInfo().username;
    const host = hostname();
    const hash = createHash("sha256")
      .update(user + host)
      .digest("hex");
    return hash.substring(0, 12);
  } catch {
    return "anonymous";
  }
}

/**
 * Returns the active story ID from the temp file, or null if no story is active.
 */
export function getActiveStoryId(): string | null {
  try {
    if (existsSync(STORY_FILE)) {
      const content = readFileSync(STORY_FILE, "utf-8").trim();
      return content || null;
    }
  } catch {
    // Ignore read errors
  }
  return null;
}

/**
 * Writes an active story ID to the temp file.
 */
export function setActiveStoryId(storyId: string): void {
  writeFileSync(STORY_FILE, storyId, "utf-8");
}

/**
 * Removes the active story temp file.
 */
export function clearActiveStoryId(): void {
  try {
    if (existsSync(STORY_FILE)) {
      unlinkSync(STORY_FILE);
    }
  } catch {
    // Ignore
  }
}

/**
 * Extracts the session_id from hook input JSON.
 * Claude Code hooks pass session info in various ways; try common paths.
 */
export function getSessionId(input: Record<string, any>): string {
  return (
    input.session_id ||
    input.sessionId ||
    input.session?.id ||
    input.session?.session_id ||
    `session-${Date.now()}`
  );
}

/**
 * Truncates a string to a maximum length, appending "..." if truncated.
 */
export function truncate(str: string, maxLen: number): string {
  if (!str) return "";
  if (str.length <= maxLen) return str;
  return str.substring(0, maxLen) + "...";
}

// ─── Event sender ────────────────────────────────────────────────────────────

export interface EventData {
  session_id?: string;
  story_id?: string | null;
  tool_name?: string | null;
  model_name?: string | null;
  input_tokens?: number | null;
  output_tokens?: number | null;
  summary?: string | null;
  payload?: unknown;
}

/**
 * Sends an event to the cc-observability server.
 *
 * Silently does nothing if CC_OBSERVABILITY_URL is not set or if the POST fails.
 * Always resolves (never throws).
 */
export async function sendEvent(
  eventType: string,
  data: EventData,
): Promise<void> {
  const url = getObservabilityUrl();
  if (!url) return;

  const body = {
    project_id: getProjectId(),
    contributor_id: getContributorId(),
    session_id: data.session_id || `session-${Date.now()}`,
    story_id: data.story_id ?? getActiveStoryId() ?? null,
    hook_event_type: eventType,
    payload: data.payload ?? {},
    summary: data.summary ?? null,
    tool_name: data.tool_name ?? null,
    model_name: data.model_name ?? null,
    input_tokens: data.input_tokens ?? 0,
    output_tokens: data.output_tokens ?? 0,
    timestamp: new Date().toISOString(),
  };

  try {
    await fetch(`${url}/api/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(5000),
    });
  } catch {
    // Silently swallow network errors -- hooks must never block the developer
  }
}
