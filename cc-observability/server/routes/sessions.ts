import type { Database } from "bun:sqlite";
import type { BroadcastFn } from "../types";

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/**
 * GET /api/sessions?project_id=&contributor_id=&story_id=
 */
export function handleGetSessions(
  req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const url = new URL(req.url);
  const projectId = url.searchParams.get("project_id");
  const contributorId = url.searchParams.get("contributor_id");
  const storyId = url.searchParams.get("story_id");

  let sql = `SELECT s.*,
    (SELECT COUNT(*) FROM events e WHERE e.session_id = s.session_id) as event_count
    FROM sessions s WHERE 1=1`;
  const params: string[] = [];

  if (projectId) {
    sql += " AND s.project_id = ?";
    params.push(projectId);
  }
  if (contributorId) {
    sql += " AND s.contributor_id = ?";
    params.push(contributorId);
  }
  if (storyId) {
    sql += " AND s.story_id = ?";
    params.push(storyId);
  }

  sql += " ORDER BY s.started_at DESC";

  const sessions = db.prepare(sql).all(...params);
  return jsonResponse(sessions);
}
