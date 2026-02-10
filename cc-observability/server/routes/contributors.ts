import type { Database } from "bun:sqlite";
import type { BroadcastFn } from "../types";

/**
 * GET /api/contributors
 *
 * Returns all contributors with stats.  Optional query param `project_id`
 * filters to contributors who have sessions in that project.
 */
export function handleGetContributors(
  req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const url = new URL(req.url);
  const projectId = url.searchParams.get("project_id");

  let rows;
  if (projectId) {
    rows = db
      .prepare(
        `SELECT
           c.contributor_id,
           c.display_name,
           c.first_seen_at,
           c.last_active_at,
           (SELECT COUNT(*) FROM sessions
            WHERE contributor_id = c.contributor_id AND project_id = ?) AS session_count,
           (SELECT COUNT(*) FROM stories
            WHERE contributor_id = c.contributor_id AND project_id = ?) AS story_count,
           (SELECT COALESCE(SUM(total_input_tokens), 0) FROM sessions
            WHERE contributor_id = c.contributor_id AND project_id = ?) AS total_input_tokens,
           (SELECT COALESCE(SUM(total_output_tokens), 0) FROM sessions
            WHERE contributor_id = c.contributor_id AND project_id = ?) AS total_output_tokens
         FROM contributors c
         WHERE c.contributor_id IN (
           SELECT DISTINCT contributor_id FROM sessions WHERE project_id = ?
         )
         ORDER BY c.last_active_at DESC`,
      )
      .all(projectId, projectId, projectId, projectId, projectId);
  } else {
    rows = db
      .prepare(
        `SELECT
           c.contributor_id,
           c.display_name,
           c.first_seen_at,
           c.last_active_at,
           (SELECT COUNT(*) FROM sessions
            WHERE contributor_id = c.contributor_id) AS session_count,
           (SELECT COUNT(*) FROM stories
            WHERE contributor_id = c.contributor_id) AS story_count,
           (SELECT COALESCE(SUM(total_input_tokens), 0) FROM sessions
            WHERE contributor_id = c.contributor_id) AS total_input_tokens,
           (SELECT COALESCE(SUM(total_output_tokens), 0) FROM sessions
            WHERE contributor_id = c.contributor_id) AS total_output_tokens
         FROM contributors c
         ORDER BY c.last_active_at DESC`,
      )
      .all();
  }

  return jsonResponse(rows);
}

/**
 * GET /api/contributors/:id
 *
 * Returns contributor detail with their sessions and stories.
 */
export function handleGetContributorById(
  _req: Request,
  db: Database,
  _broadcast: BroadcastFn,
  contributorId: string,
): Response {
  const contributor = db
    .prepare(
      `SELECT
         c.contributor_id,
         c.display_name,
         c.first_seen_at,
         c.last_active_at,
         (SELECT COUNT(*) FROM sessions WHERE contributor_id = c.contributor_id) AS session_count,
         (SELECT COUNT(*) FROM stories WHERE contributor_id = c.contributor_id) AS story_count,
         (SELECT COALESCE(SUM(total_input_tokens), 0) FROM sessions
          WHERE contributor_id = c.contributor_id) AS total_input_tokens,
         (SELECT COALESCE(SUM(total_output_tokens), 0) FROM sessions
          WHERE contributor_id = c.contributor_id) AS total_output_tokens
       FROM contributors c
       WHERE c.contributor_id = ?`,
    )
    .get(contributorId);

  if (!contributor) {
    return jsonResponse({ error: "Contributor not found" }, 404);
  }

  const sessions = db
    .prepare(
      `SELECT session_id, project_id, story_id, model_name,
              started_at, ended_at, end_reason,
              total_input_tokens, total_output_tokens
       FROM sessions
       WHERE contributor_id = ?
       ORDER BY started_at DESC
       LIMIT 50`,
    )
    .all(contributorId);

  const stories = db
    .prepare(
      `SELECT story_id, project_id, title, status,
              started_at, completed_at,
              estimated_minutes, actual_minutes,
              lines_added, lines_removed,
              review_cycles, bugs_found,
              total_input_tokens, total_output_tokens
       FROM stories
       WHERE contributor_id = ?
       ORDER BY started_at DESC
       LIMIT 50`,
    )
    .all(contributorId);

  return jsonResponse({ ...contributor, sessions, stories });
}

// ── Helpers ────────────────────────────────────────────────────────────────

function jsonResponse(data: unknown, status: number = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
