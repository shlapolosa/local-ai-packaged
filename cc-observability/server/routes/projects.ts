import type { Database } from "bun:sqlite";
import type { BroadcastFn } from "../types";

/**
 * GET /api/projects
 *
 * Returns all projects with aggregated stats:
 * contributor_count, story_count, session_count, last_active_at
 */
export function handleGetProjects(
  _req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const rows = db
    .prepare(
      `SELECT
         p.project_id,
         p.display_name,
         p.git_remote_url,
         p.first_seen_at,
         p.last_active_at,
         (SELECT COUNT(DISTINCT contributor_id) FROM sessions WHERE project_id = p.project_id)
           AS contributor_count,
         (SELECT COUNT(*) FROM stories WHERE project_id = p.project_id)
           AS story_count,
         (SELECT COUNT(*) FROM sessions WHERE project_id = p.project_id)
           AS session_count
       FROM projects p
       ORDER BY p.last_active_at DESC`,
    )
    .all();

  return jsonResponse(rows);
}

/**
 * GET /api/projects/:id
 *
 * Returns project detail including contributor list and recent activity.
 */
export function handleGetProjectById(
  _req: Request,
  db: Database,
  _broadcast: BroadcastFn,
  projectId: string,
): Response {
  const project = db
    .prepare(
      `SELECT
         p.project_id,
         p.display_name,
         p.git_remote_url,
         p.first_seen_at,
         p.last_active_at,
         (SELECT COUNT(DISTINCT contributor_id) FROM sessions WHERE project_id = p.project_id)
           AS contributor_count,
         (SELECT COUNT(*) FROM stories WHERE project_id = p.project_id)
           AS story_count,
         (SELECT COUNT(*) FROM sessions WHERE project_id = p.project_id)
           AS session_count
       FROM projects p
       WHERE p.project_id = ?`,
    )
    .get(projectId);

  if (!project) {
    return jsonResponse({ error: "Project not found" }, 404);
  }

  const contributors = db
    .prepare(
      `SELECT DISTINCT
         c.contributor_id,
         c.display_name,
         c.last_active_at,
         (SELECT COUNT(*) FROM stories
          WHERE project_id = ? AND contributor_id = c.contributor_id) AS story_count,
         (SELECT COUNT(*) FROM sessions
          WHERE project_id = ? AND contributor_id = c.contributor_id) AS session_count
       FROM contributors c
       INNER JOIN sessions s ON s.contributor_id = c.contributor_id
       WHERE s.project_id = ?
       ORDER BY c.last_active_at DESC`,
    )
    .all(projectId, projectId, projectId);

  const recentEvents = db
    .prepare(
      `SELECT id, contributor_id, session_id, hook_event_type,
              tool_name, model_name, timestamp, input_tokens, output_tokens
       FROM events
       WHERE project_id = ?
       ORDER BY timestamp DESC
       LIMIT 50`,
    )
    .all(projectId);

  return jsonResponse({ ...project, contributors, recent_events: recentEvents });
}

// ── Helpers ────────────────────────────────────────────────────────────────

function jsonResponse(data: unknown, status: number = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
