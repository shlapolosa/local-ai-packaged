import type { Database } from "bun:sqlite";
import type { BroadcastFn, CreateStoryPayload, UpdateStoryPayload, ReviewCyclePayload } from "../types";

/**
 * GET /api/stories
 *
 * Query stories with optional filters: project_id, contributor_id, status
 */
export function handleGetStories(
  req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const url = new URL(req.url);
  const projectId = url.searchParams.get("project_id");
  const contributorId = url.searchParams.get("contributor_id");
  const status = url.searchParams.get("status");

  const conditions: string[] = [];
  const params: unknown[] = [];

  if (projectId) {
    conditions.push("s.project_id = ?");
    params.push(projectId);
  }
  if (contributorId) {
    conditions.push("s.contributor_id = ?");
    params.push(contributorId);
  }
  if (status) {
    conditions.push("s.status = ?");
    params.push(status);
  }

  const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";

  const rows = db
    .prepare(
      `SELECT
         s.*,
         p.display_name AS project_name,
         c.display_name AS contributor_name,
         (SELECT COUNT(*) FROM review_cycles WHERE story_id = s.story_id)
           AS review_cycle_count,
         (SELECT COUNT(*) FROM events WHERE story_id = s.story_id)
           AS event_count
       FROM stories s
       LEFT JOIN projects p ON p.project_id = s.project_id
       LEFT JOIN contributors c ON c.contributor_id = s.contributor_id
       ${where}
       ORDER BY s.started_at DESC`,
    )
    .all(...params);

  return jsonResponse(rows);
}

/**
 * POST /api/stories
 *
 * Create a new story.
 */
export async function handlePostStory(
  req: Request,
  db: Database,
  broadcast: BroadcastFn,
): Promise<Response> {
  let body: CreateStoryPayload;
  try {
    body = (await req.json()) as CreateStoryPayload;
  } catch {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  if (!body.project_id || !body.contributor_id || !body.title) {
    return jsonResponse(
      { error: "Missing required fields: project_id, contributor_id, title" },
      400,
    );
  }

  const storyId = body.story_id || crypto.randomUUID();
  const now = new Date().toISOString();

  // Verify project exists
  const project = db.prepare("SELECT project_id FROM projects WHERE project_id = ?").get(body.project_id);
  if (!project) {
    return jsonResponse({ error: "Project not found" }, 404);
  }

  // Verify contributor exists
  const contributor = db
    .prepare("SELECT contributor_id FROM contributors WHERE contributor_id = ?")
    .get(body.contributor_id);
  if (!contributor) {
    return jsonResponse({ error: "Contributor not found" }, 404);
  }

  db.prepare(
    `INSERT INTO stories (story_id, project_id, contributor_id, title, description,
                          estimated_minutes, started_at)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
  ).run(
    storyId,
    body.project_id,
    body.contributor_id,
    body.title,
    body.description ?? "",
    body.estimated_minutes ?? null,
    now,
  );

  const story = db.prepare("SELECT * FROM stories WHERE story_id = ?").get(storyId);

  broadcast({ type: "story_created", data: story });

  return jsonResponse(story, 201);
}

/**
 * GET /api/stories/:id
 *
 * Returns story detail with event timeline and review cycles.
 */
export function handleGetStoryById(
  _req: Request,
  db: Database,
  _broadcast: BroadcastFn,
  storyId: string,
): Response {
  const story = db
    .prepare(
      `SELECT
         s.*,
         p.display_name AS project_name,
         c.display_name AS contributor_name
       FROM stories s
       LEFT JOIN projects p ON p.project_id = s.project_id
       LEFT JOIN contributors c ON c.contributor_id = s.contributor_id
       WHERE s.story_id = ?`,
    )
    .get(storyId);

  if (!story) {
    return jsonResponse({ error: "Story not found" }, 404);
  }

  const events = db
    .prepare(
      `SELECT id, session_id, hook_event_type, tool_name, model_name,
              summary, timestamp, input_tokens, output_tokens
       FROM events
       WHERE story_id = ?
       ORDER BY timestamp ASC`,
    )
    .all(storyId);

  const reviewCycles = db
    .prepare(
      `SELECT id, submitted_at, returned_at, feedback, status
       FROM review_cycles
       WHERE story_id = ?
       ORDER BY submitted_at ASC`,
    )
    .all(storyId);

  return jsonResponse({ ...story, events, review_cycles: reviewCycles });
}

/**
 * PATCH /api/stories/:id
 *
 * Update story fields.
 */
export async function handlePatchStory(
  req: Request,
  db: Database,
  broadcast: BroadcastFn,
  storyId: string,
): Promise<Response> {
  let body: UpdateStoryPayload;
  try {
    body = (await req.json()) as UpdateStoryPayload;
  } catch {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  // Verify story exists
  const existing = db.prepare("SELECT story_id FROM stories WHERE story_id = ?").get(storyId);
  if (!existing) {
    return jsonResponse({ error: "Story not found" }, 404);
  }

  // Build dynamic UPDATE from provided fields
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
      values.push((body as Record<string, unknown>)[field]);
    }
  }

  // Auto-set completed_at when status transitions to completed
  if (body.status === "completed" && !body.completed_at) {
    setClauses.push("completed_at = ?");
    values.push(new Date().toISOString());
  }

  if (setClauses.length === 0) {
    return jsonResponse({ error: "No valid fields to update" }, 400);
  }

  values.push(storyId);
  db.prepare(`UPDATE stories SET ${setClauses.join(", ")} WHERE story_id = ?`).run(...values);

  const updated = db.prepare("SELECT * FROM stories WHERE story_id = ?").get(storyId);

  broadcast({ type: "story_updated", data: updated });

  return jsonResponse(updated);
}

/**
 * POST /api/stories/:id/review-cycles
 *
 * Add a review cycle to a story.
 */
export async function handlePostReviewCycle(
  req: Request,
  db: Database,
  broadcast: BroadcastFn,
  storyId: string,
): Promise<Response> {
  let body: ReviewCyclePayload;
  try {
    body = (await req.json()) as ReviewCyclePayload;
  } catch {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  // Verify story exists
  const existing = db.prepare("SELECT story_id FROM stories WHERE story_id = ?").get(storyId);
  if (!existing) {
    return jsonResponse({ error: "Story not found" }, 404);
  }

  const now = new Date().toISOString();

  db.prepare(
    `INSERT INTO review_cycles (story_id, submitted_at, returned_at, feedback, status)
     VALUES (?, ?, ?, ?, ?)`,
  ).run(
    storyId,
    body.submitted_at ?? now,
    body.returned_at ?? null,
    body.feedback ?? null,
    body.returned_at ? "returned" : "pending",
  );

  // Increment review_cycles on the story
  db.prepare(
    "UPDATE stories SET review_cycles = review_cycles + 1 WHERE story_id = ?",
  ).run(storyId);

  const cycle = db
    .prepare("SELECT * FROM review_cycles WHERE story_id = ? ORDER BY id DESC LIMIT 1")
    .get(storyId);

  broadcast({ type: "review_cycle_added", data: { story_id: storyId, cycle } });

  return jsonResponse(cycle, 201);
}

// ── Helpers ────────────────────────────────────────────────────────────────

function jsonResponse(data: unknown, status: number = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
