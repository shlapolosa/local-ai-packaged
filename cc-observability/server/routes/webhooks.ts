import type { Database } from "bun:sqlite";
import type { BroadcastFn, ReviewCyclePayload, BugFoundPayload, StoryUpdateWebhookPayload } from "../types";

/**
 * POST /api/webhooks/review-cycle
 *
 * Creates a review_cycle record and increments review_cycles on the story.
 * Designed for n8n/Azure DevOps webhook integrations.
 */
export async function handleWebhookReviewCycle(
  req: Request,
  db: Database,
  broadcast: BroadcastFn,
): Promise<Response> {
  let body: ReviewCyclePayload & { story_id?: string };
  try {
    body = (await req.json()) as ReviewCyclePayload & { story_id?: string };
  } catch {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  if (!body.story_id) {
    return jsonResponse({ error: "Missing required field: story_id" }, 400);
  }

  // Verify story exists
  const story = db.prepare("SELECT story_id FROM stories WHERE story_id = ?").get(body.story_id);
  if (!story) {
    return jsonResponse({ error: "Story not found" }, 404);
  }

  const now = new Date().toISOString();

  db.prepare(
    `INSERT INTO review_cycles (story_id, submitted_at, returned_at, feedback, status)
     VALUES (?, ?, ?, ?, ?)`,
  ).run(
    body.story_id,
    body.submitted_at ?? now,
    body.returned_at ?? null,
    body.feedback ?? null,
    body.returned_at ? "returned" : "pending",
  );

  // Increment review_cycles counter on the story
  db.prepare(
    "UPDATE stories SET review_cycles = review_cycles + 1 WHERE story_id = ?",
  ).run(body.story_id);

  const cycle = db
    .prepare("SELECT * FROM review_cycles WHERE story_id = ? ORDER BY id DESC LIMIT 1")
    .get(body.story_id);

  broadcast({ type: "webhook_review_cycle", data: { story_id: body.story_id, cycle } });

  return jsonResponse({ ok: true, cycle }, 201);
}

/**
 * POST /api/webhooks/bug-found
 *
 * Increments bugs_found on a story.
 */
export async function handleWebhookBugFound(
  req: Request,
  db: Database,
  broadcast: BroadcastFn,
): Promise<Response> {
  let body: BugFoundPayload;
  try {
    body = (await req.json()) as BugFoundPayload;
  } catch {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  if (!body.story_id) {
    return jsonResponse({ error: "Missing required field: story_id" }, 400);
  }

  // Verify story exists
  const story = db
    .prepare("SELECT story_id, bugs_found FROM stories WHERE story_id = ?")
    .get(body.story_id) as { story_id: string; bugs_found: number } | null;
  if (!story) {
    return jsonResponse({ error: "Story not found" }, 404);
  }

  db.prepare(
    "UPDATE stories SET bugs_found = bugs_found + 1 WHERE story_id = ?",
  ).run(body.story_id);

  const newCount = story.bugs_found + 1;

  broadcast({
    type: "webhook_bug_found",
    data: {
      story_id: body.story_id,
      description: body.description ?? null,
      bugs_found: newCount,
    },
  });

  return jsonResponse({ ok: true, bugs_found: newCount });
}

/**
 * POST /api/webhooks/story-update
 *
 * Updates arbitrary story fields.  The body must include story_id and any
 * combination of updatable story fields.
 */
export async function handleWebhookStoryUpdate(
  req: Request,
  db: Database,
  broadcast: BroadcastFn,
): Promise<Response> {
  let body: StoryUpdateWebhookPayload;
  try {
    body = (await req.json()) as StoryUpdateWebhookPayload;
  } catch {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  if (!body.story_id) {
    return jsonResponse({ error: "Missing required field: story_id" }, 400);
  }

  // Verify story exists
  const existing = db.prepare("SELECT story_id FROM stories WHERE story_id = ?").get(body.story_id);
  if (!existing) {
    return jsonResponse({ error: "Story not found" }, 404);
  }

  const allowedFields = [
    "title",
    "description",
    "status",
    "completed_at",
    "estimated_minutes",
    "actual_minutes",
    "lines_added",
    "lines_removed",
    "review_cycles",
    "bugs_found",
    "total_input_tokens",
    "total_output_tokens",
  ];

  const setClauses: string[] = [];
  const values: unknown[] = [];

  for (const field of allowedFields) {
    if (field in body) {
      setClauses.push(`${field} = ?`);
      values.push(body[field]);
    }
  }

  // Auto-set completed_at when status transitions to completed
  if (body.status === "completed" && !body.completed_at) {
    if (!setClauses.some((c) => c.startsWith("completed_at"))) {
      setClauses.push("completed_at = ?");
      values.push(new Date().toISOString());
    }
  }

  if (setClauses.length === 0) {
    return jsonResponse({ error: "No valid fields to update" }, 400);
  }

  values.push(body.story_id);
  db.prepare(`UPDATE stories SET ${setClauses.join(", ")} WHERE story_id = ?`).run(...values);

  const updated = db.prepare("SELECT * FROM stories WHERE story_id = ?").get(body.story_id);

  broadcast({ type: "webhook_story_update", data: updated });

  return jsonResponse({ ok: true, story: updated });
}

// ── Helpers ────────────────────────────────────────────────────────────────

function jsonResponse(data: unknown, status: number = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
