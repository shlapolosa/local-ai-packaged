import type { Database } from "bun:sqlite";
import type { BroadcastFn } from "../types";

/**
 * GET /api/dashboard/kpis
 *
 * Aggregated KPIs across all projects.
 */
export function handleGetKPIs(
  _req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const totalProjects = (
    db.prepare("SELECT COUNT(*) AS cnt FROM projects").get() as { cnt: number }
  ).cnt;

  const totalContributors = (
    db.prepare("SELECT COUNT(*) AS cnt FROM contributors").get() as { cnt: number }
  ).cnt;

  const storyStats = db
    .prepare(
      `SELECT
         COUNT(*)                                                        AS total_stories,
         SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)         AS stories_completed,
         AVG(CASE WHEN status = 'completed' THEN actual_minutes END)    AS avg_time_per_story,
         AVG(lines_added + lines_removed)                               AS avg_lines_per_story,
         AVG(review_cycles)                                             AS avg_review_cycles,
         AVG(bugs_found)                                                AS avg_bugs_per_story,
         COALESCE(SUM(total_input_tokens), 0)                           AS total_input_tokens,
         COALESCE(SUM(total_output_tokens), 0)                          AS total_output_tokens
       FROM stories`,
    )
    .get() as Record<string, number | null>;

  // Calculate estimated cost from events joined with model_pricing
  const costRow = db
    .prepare(
      `SELECT COALESCE(SUM(
         (e.input_tokens  / 1000.0) * COALESCE(mp.input_cost_per_1k, 0) +
         (e.output_tokens / 1000.0) * COALESCE(mp.output_cost_per_1k, 0)
       ), 0) AS estimated_total_cost
       FROM events e
       LEFT JOIN model_pricing mp ON mp.model_name = e.model_name`,
    )
    .get() as { estimated_total_cost: number };

  return jsonResponse({
    total_projects: totalProjects,
    total_contributors: totalContributors,
    total_stories: storyStats.total_stories ?? 0,
    stories_completed: storyStats.stories_completed ?? 0,
    avg_time_per_story: round(storyStats.avg_time_per_story),
    avg_lines_per_story: round(storyStats.avg_lines_per_story),
    avg_review_cycles: round(storyStats.avg_review_cycles),
    avg_bugs_per_story: round(storyStats.avg_bugs_per_story),
    total_input_tokens: storyStats.total_input_tokens ?? 0,
    total_output_tokens: storyStats.total_output_tokens ?? 0,
    estimated_total_cost: round(costRow.estimated_total_cost),
  });
}

/**
 * GET /api/dashboard/trends?period=daily|weekly|monthly
 *
 * Time-series of: stories_completed, avg_time, total_tokens, estimated_cost
 */
export function handleGetTrends(
  req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const url = new URL(req.url);
  const period = url.searchParams.get("period") || "daily";

  let dateFmt: string;
  switch (period) {
    case "weekly":
      dateFmt = "%Y-W%W";
      break;
    case "monthly":
      dateFmt = "%Y-%m";
      break;
    default:
      dateFmt = "%Y-%m-%d";
  }

  // Story-based trends (only completed stories contribute time data)
  const storyTrends = db
    .prepare(
      `SELECT
         strftime('${dateFmt}', started_at) AS period,
         SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)        AS stories_completed,
         AVG(CASE WHEN status = 'completed' THEN actual_minutes END)   AS avg_time,
         COALESCE(SUM(total_input_tokens + total_output_tokens), 0)    AS total_tokens
       FROM stories
       GROUP BY strftime('${dateFmt}', started_at)
       ORDER BY period ASC`,
    )
    .all() as Array<{
    period: string;
    stories_completed: number;
    avg_time: number | null;
    total_tokens: number;
  }>;

  // Cost trends from events
  const costTrends = db
    .prepare(
      `SELECT
         strftime('${dateFmt}', e.timestamp) AS period,
         COALESCE(SUM(
           (e.input_tokens  / 1000.0) * COALESCE(mp.input_cost_per_1k, 0) +
           (e.output_tokens / 1000.0) * COALESCE(mp.output_cost_per_1k, 0)
         ), 0) AS estimated_cost
       FROM events e
       LEFT JOIN model_pricing mp ON mp.model_name = e.model_name
       GROUP BY strftime('${dateFmt}', e.timestamp)
       ORDER BY period ASC`,
    )
    .all() as Array<{ period: string; estimated_cost: number }>;

  // Merge the two result sets by period
  const costMap = new Map(costTrends.map((c) => [c.period, c.estimated_cost]));

  const merged = storyTrends.map((row) => ({
    period: row.period,
    stories_completed: row.stories_completed,
    avg_time: round(row.avg_time),
    total_tokens: row.total_tokens,
    estimated_cost: round(costMap.get(row.period) ?? 0),
  }));

  // Also include periods that only have events but no stories
  const storyPeriods = new Set(storyTrends.map((s) => s.period));
  for (const ct of costTrends) {
    if (!storyPeriods.has(ct.period)) {
      merged.push({
        period: ct.period,
        stories_completed: 0,
        avg_time: null,
        total_tokens: 0,
        estimated_cost: round(ct.estimated_cost),
      });
    }
  }

  merged.sort((a, b) => a.period.localeCompare(b.period));

  return jsonResponse(merged);
}

/**
 * GET /api/dashboard/leaderboard
 *
 * Contributors ranked by stories completed, quality, and efficiency.
 */
export function handleGetLeaderboard(
  _req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const rows = db
    .prepare(
      `SELECT
         c.contributor_id,
         c.display_name,
         COUNT(CASE WHEN s.status = 'completed' THEN 1 END) AS stories_completed,
         -- Quality: inverse of avg review cycles (fewer = better), normalized 0..1
         CASE
           WHEN AVG(s.review_cycles) IS NULL THEN 0
           WHEN AVG(s.review_cycles) = 0 THEN 1.0
           ELSE 1.0 / (1.0 + AVG(s.review_cycles))
         END AS avg_quality,
         -- Efficiency: stories completed per total hours of actual_minutes
         CASE
           WHEN SUM(s.actual_minutes) IS NULL OR SUM(s.actual_minutes) = 0 THEN 0
           ELSE CAST(COUNT(CASE WHEN s.status = 'completed' THEN 1 END) AS REAL) /
                (SUM(CASE WHEN s.status = 'completed' THEN s.actual_minutes ELSE 0 END) / 60.0)
         END AS efficiency
       FROM contributors c
       LEFT JOIN stories s ON s.contributor_id = c.contributor_id
       GROUP BY c.contributor_id
       HAVING stories_completed > 0
       ORDER BY stories_completed DESC, avg_quality DESC, efficiency DESC`,
    )
    .all();

  const rounded = (rows as Array<Record<string, unknown>>).map((r) => ({
    ...r,
    avg_quality: round(r.avg_quality as number | null),
    efficiency: round(r.efficiency as number | null),
  }));

  return jsonResponse(rounded);
}

/**
 * GET /api/dashboard/cost?by=project|contributor|model
 *
 * Token cost breakdown by the selected dimension.
 */
export function handleGetCost(
  req: Request,
  db: Database,
  _broadcast: BroadcastFn,
): Response {
  const url = new URL(req.url);
  const by = url.searchParams.get("by") || "model";

  let groupCol: string;
  let dimensionLabel: string;
  switch (by) {
    case "project":
      groupCol = "e.project_id";
      dimensionLabel = "project";
      break;
    case "contributor":
      groupCol = "e.contributor_id";
      dimensionLabel = "contributor";
      break;
    default:
      groupCol = "e.model_name";
      dimensionLabel = "model";
  }

  const rows = db
    .prepare(
      `SELECT
         ${groupCol}                                              AS dimension_value,
         COALESCE(SUM(e.input_tokens), 0)                        AS total_input_tokens,
         COALESCE(SUM(e.output_tokens), 0)                       AS total_output_tokens,
         COALESCE(SUM(
           (e.input_tokens  / 1000.0) * COALESCE(mp.input_cost_per_1k, 0) +
           (e.output_tokens / 1000.0) * COALESCE(mp.output_cost_per_1k, 0)
         ), 0) AS estimated_cost
       FROM events e
       LEFT JOIN model_pricing mp ON mp.model_name = e.model_name
       GROUP BY ${groupCol}
       ORDER BY estimated_cost DESC`,
    )
    .all();

  const result = (rows as Array<Record<string, unknown>>).map((r) => ({
    dimension: dimensionLabel,
    dimension_value: r.dimension_value ?? "unknown",
    total_input_tokens: r.total_input_tokens,
    total_output_tokens: r.total_output_tokens,
    estimated_cost: round(r.estimated_cost as number | null),
  }));

  return jsonResponse(result);
}

// ── Helpers ────────────────────────────────────────────────────────────────

function round(value: number | null | undefined, decimals: number = 2): number | null {
  if (value === null || value === undefined) return null;
  const factor = Math.pow(10, decimals);
  return Math.round(value * factor) / factor;
}

function jsonResponse(data: unknown, status: number = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
