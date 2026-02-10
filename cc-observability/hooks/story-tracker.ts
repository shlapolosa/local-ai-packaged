#!/usr/bin/env npx tsx
/**
 * story-tracker.ts -- Dev Story lifecycle tracker
 *
 * Hooks into UserPromptSubmit to detect /dev-story commands.
 *
 * Commands:
 *   /dev-story start <title>   -- Creates a new story, writes ID to /tmp/.cc_active_story
 *   /dev-story end             -- Completes the active story, captures git diff stats
 *   /dev-story abandon         -- Abandons the active story
 *
 * If the prompt does not contain a /dev-story command, the hook exits silently.
 */

import { createHash, randomUUID } from "crypto";
import { execSync } from "child_process";
import { readFileSync, existsSync, writeFileSync, unlinkSync } from "fs";
import { userInfo, hostname } from "os";

const STORY_FILE = "/tmp/.cc_active_story";

async function main(): Promise<void> {
  const input = await readStdinRaw();

  // Extract prompt text
  const promptText =
    input.prompt ||
    input.message ||
    input.content ||
    input.text ||
    "";
  const prompt = typeof promptText === "string" ? promptText : String(promptText);

  // Check for /dev-story command
  const match = prompt.match(/\/dev-story\s+(start|end|abandon)(?:\s+(.*))?/i);
  if (!match) {
    // Not a dev-story command -- exit silently
    process.exit(0);
  }

  const command = match[1].toLowerCase();
  const titleArg = (match[2] || "").trim();

  const observabilityUrl = getObservabilityUrlRaw();
  if (!observabilityUrl) {
    process.exit(0);
  }

  const projectId = getProjectIdRaw();
  const contributorId = getContributorIdRaw();

  switch (command) {
    case "start":
      await handleStart(observabilityUrl, projectId, contributorId, titleArg);
      break;
    case "end":
      await handleEnd(observabilityUrl, "completed");
      break;
    case "abandon":
      await handleEnd(observabilityUrl, "abandoned");
      break;
  }
}

// ─── Command handlers ────────────────────────────────────────────────────────

async function handleStart(
  baseUrl: string,
  projectId: string,
  contributorId: string,
  title: string,
): Promise<void> {
  const storyId = randomUUID();
  const storyTitle = title || `Story started at ${new Date().toISOString()}`;

  const body = {
    story_id: storyId,
    project_id: projectId,
    contributor_id: contributorId,
    title: storyTitle,
    description: "",
  };

  try {
    const response = await fetch(`${baseUrl}/api/stories`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(5000),
    });

    if (response.ok || response.status === 201) {
      // Write story ID to temp file so other hooks can attach events to it
      writeFileSync(STORY_FILE, storyId, "utf-8");
      // Also send an event marking the story start
      await sendEventRaw(baseUrl, "StoryStart", projectId, contributorId, {
        story_id: storyId,
        title: storyTitle,
        summary: `Story started: ${storyTitle}`,
      });
    }
  } catch {
    // Silently swallow
  }
}

async function handleEnd(
  baseUrl: string,
  status: "completed" | "abandoned",
): Promise<void> {
  // Read active story ID
  let storyId: string | null = null;
  try {
    if (existsSync(STORY_FILE)) {
      storyId = readFileSync(STORY_FILE, "utf-8").trim() || null;
    }
  } catch {}

  if (!storyId) {
    // No active story -- nothing to do
    return;
  }

  // Capture git diff stats for lines added/removed
  let linesAdded = 0;
  let linesRemoved = 0;
  try {
    const diffStat = execSync("git diff --stat", {
      encoding: "utf-8",
      timeout: 5000,
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();

    // Parse the summary line: " 5 files changed, 120 insertions(+), 30 deletions(-)"
    const insertMatch = diffStat.match(/(\d+)\s+insertion/);
    const deleteMatch = diffStat.match(/(\d+)\s+deletion/);
    if (insertMatch) linesAdded = parseInt(insertMatch[1], 10);
    if (deleteMatch) linesRemoved = parseInt(deleteMatch[1], 10);
  } catch {
    // git diff may fail in non-git directories, or if there are no changes
  }

  // Also try staged changes
  try {
    const stagedStat = execSync("git diff --cached --stat", {
      encoding: "utf-8",
      timeout: 5000,
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();

    const insertMatch = stagedStat.match(/(\d+)\s+insertion/);
    const deleteMatch = stagedStat.match(/(\d+)\s+deletion/);
    if (insertMatch) linesAdded += parseInt(insertMatch[1], 10);
    if (deleteMatch) linesRemoved += parseInt(deleteMatch[1], 10);
  } catch {
    // Ignore
  }

  const updateBody: Record<string, unknown> = {
    status,
    completed_at: new Date().toISOString(),
    lines_added: linesAdded,
    lines_removed: linesRemoved,
  };

  try {
    await fetch(`${baseUrl}/api/stories/${storyId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updateBody),
      signal: AbortSignal.timeout(5000),
    });
  } catch {
    // Silently swallow
  }

  // Send an event marking the story end
  const projectId = getProjectIdRaw();
  const contributorId = getContributorIdRaw();
  await sendEventRaw(baseUrl, "StoryEnd", projectId, contributorId, {
    story_id: storyId,
    status,
    lines_added: linesAdded,
    lines_removed: linesRemoved,
    summary: `Story ${status}: +${linesAdded}/-${linesRemoved} lines`,
  });

  // Remove the temp file
  try {
    unlinkSync(STORY_FILE);
  } catch {}
}

// ─── Self-contained helpers (no lib.ts import to avoid circular issues) ──────

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

function getObservabilityUrlRaw(): string | null {
  return process.env.CC_OBSERVABILITY_URL?.replace(/\/+$/, "") || null;
}

function getProjectIdRaw(): string {
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

function getContributorIdRaw(): string {
  if (process.env.CC_CONTRIBUTOR_ID) return process.env.CC_CONTRIBUTOR_ID;
  try {
    const hash = createHash("sha256")
      .update(userInfo().username + hostname())
      .digest("hex");
    return hash.substring(0, 12);
  } catch { return "anonymous"; }
}

async function sendEventRaw(
  baseUrl: string,
  eventType: string,
  projectId: string,
  contributorId: string,
  data: Record<string, unknown>,
): Promise<void> {
  const body = {
    project_id: projectId,
    contributor_id: contributorId,
    session_id: `session-${Date.now()}`,
    story_id: data.story_id || null,
    hook_event_type: eventType,
    payload: data,
    summary: (data.summary as string) || eventType,
    tool_name: null,
    model_name: null,
    input_tokens: 0,
    output_tokens: 0,
    timestamp: new Date().toISOString(),
  };

  try {
    await fetch(`${baseUrl}/api/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(5000),
    });
  } catch {}
}

// ─── Entry ───────────────────────────────────────────────────────────────────

main().catch(() => {}).finally(() => process.exit(0));
