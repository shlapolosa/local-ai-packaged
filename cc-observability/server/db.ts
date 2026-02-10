import { Database } from "bun:sqlite";
import { config } from "./config";

/**
 * Open (or create) the SQLite database, enable WAL mode, and ensure all
 * tables exist.  Returns the ready-to-use Database handle.
 */
export function initDatabase(path: string = config.dbPath): Database {
  const db = new Database(path, { create: true });

  // ── Pragmas ──────────────────────────────────────────────────────────────
  db.exec("PRAGMA journal_mode = WAL");
  db.exec("PRAGMA busy_timeout = 5000");
  db.exec("PRAGMA synchronous = NORMAL");
  db.exec("PRAGMA foreign_keys = ON");

  // ── Schema ───────────────────────────────────────────────────────────────
  db.exec(`
    CREATE TABLE IF NOT EXISTS projects (
      project_id      TEXT PRIMARY KEY,
      display_name    TEXT NOT NULL,
      git_remote_url  TEXT NOT NULL DEFAULT '',
      first_seen_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
      last_active_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
    );

    CREATE TABLE IF NOT EXISTS contributors (
      contributor_id  TEXT PRIMARY KEY,
      display_name    TEXT NOT NULL,
      first_seen_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
      last_active_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
    );

    CREATE TABLE IF NOT EXISTS stories (
      story_id            TEXT PRIMARY KEY,
      project_id          TEXT NOT NULL REFERENCES projects(project_id),
      contributor_id      TEXT NOT NULL REFERENCES contributors(contributor_id),
      title               TEXT NOT NULL,
      description         TEXT NOT NULL DEFAULT '',
      status              TEXT NOT NULL DEFAULT 'in_progress'
                            CHECK(status IN ('in_progress','completed','abandoned')),
      started_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
      completed_at        TEXT,
      estimated_minutes   INTEGER,
      actual_minutes      INTEGER,
      lines_added         INTEGER NOT NULL DEFAULT 0,
      lines_removed       INTEGER NOT NULL DEFAULT 0,
      review_cycles       INTEGER NOT NULL DEFAULT 0,
      bugs_found          INTEGER NOT NULL DEFAULT 0,
      total_input_tokens  INTEGER NOT NULL DEFAULT 0,
      total_output_tokens INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS sessions (
      session_id          TEXT PRIMARY KEY,
      project_id          TEXT NOT NULL REFERENCES projects(project_id),
      contributor_id      TEXT NOT NULL REFERENCES contributors(contributor_id),
      story_id            TEXT REFERENCES stories(story_id),
      model_name          TEXT NOT NULL DEFAULT '',
      started_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
      ended_at            TEXT,
      end_reason          TEXT,
      total_input_tokens  INTEGER NOT NULL DEFAULT 0,
      total_output_tokens INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS events (
      id                INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id        TEXT NOT NULL REFERENCES projects(project_id),
      contributor_id    TEXT NOT NULL REFERENCES contributors(contributor_id),
      session_id        TEXT NOT NULL REFERENCES sessions(session_id),
      story_id          TEXT REFERENCES stories(story_id),
      hook_event_type   TEXT NOT NULL,
      payload           TEXT NOT NULL DEFAULT '{}',
      chat              TEXT,
      summary           TEXT,
      tool_name         TEXT,
      model_name        TEXT,
      timestamp         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
      input_tokens      INTEGER NOT NULL DEFAULT 0,
      output_tokens     INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS review_cycles (
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      story_id      TEXT NOT NULL REFERENCES stories(story_id),
      submitted_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
      returned_at   TEXT,
      feedback      TEXT,
      status        TEXT NOT NULL DEFAULT 'pending'
    );

    CREATE TABLE IF NOT EXISTS model_pricing (
      model_name          TEXT PRIMARY KEY,
      input_cost_per_1k   REAL NOT NULL,
      output_cost_per_1k  REAL NOT NULL
    );

    -- OTEL Spans table
    CREATE TABLE IF NOT EXISTS spans (
      trace_id              TEXT NOT NULL,
      span_id               TEXT NOT NULL PRIMARY KEY,
      parent_span_id        TEXT,
      trace_state           TEXT,

      name                  TEXT NOT NULL,
      kind                  INTEGER DEFAULT 0,

      start_time_unix_nano  TEXT NOT NULL,
      end_time_unix_nano    TEXT,
      duration_ms           REAL,

      status_code           INTEGER DEFAULT 0,
      status_message        TEXT,

      service_name          TEXT NOT NULL,
      service_instance_id   TEXT NOT NULL,

      tool_name             TEXT,
      model_name            TEXT,
      input_tokens          INTEGER DEFAULT 0,
      output_tokens         INTEGER DEFAULT 0,
      story_id              TEXT,

      attributes            TEXT,
      events                TEXT,
      links                 TEXT,
      resource_attributes   TEXT,

      input_payload         TEXT,
      output_payload        TEXT
    );

    -- Indexes for common query patterns
    CREATE INDEX IF NOT EXISTS idx_events_project      ON events(project_id);
    CREATE INDEX IF NOT EXISTS idx_events_contributor   ON events(contributor_id);
    CREATE INDEX IF NOT EXISTS idx_events_session       ON events(session_id);
    CREATE INDEX IF NOT EXISTS idx_events_story         ON events(story_id);
    CREATE INDEX IF NOT EXISTS idx_events_timestamp     ON events(timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_events_type          ON events(hook_event_type);
    CREATE INDEX IF NOT EXISTS idx_stories_project      ON stories(project_id);
    CREATE INDEX IF NOT EXISTS idx_stories_contributor  ON stories(contributor_id);
    CREATE INDEX IF NOT EXISTS idx_stories_status       ON stories(status);
    CREATE INDEX IF NOT EXISTS idx_sessions_project     ON sessions(project_id);
    CREATE INDEX IF NOT EXISTS idx_sessions_contributor ON sessions(contributor_id);
    CREATE INDEX IF NOT EXISTS idx_review_cycles_story  ON review_cycles(story_id);

    -- Spans indexes
    CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id);
    CREATE INDEX IF NOT EXISTS idx_spans_service  ON spans(service_name);
    CREATE INDEX IF NOT EXISTS idx_spans_start    ON spans(start_time_unix_nano);
    CREATE INDEX IF NOT EXISTS idx_spans_name     ON spans(name);
    CREATE INDEX IF NOT EXISTS idx_spans_parent   ON spans(parent_span_id);
  `);

  // ── Seed model pricing ───────────────────────────────────────────────────
  const upsertPricing = db.prepare(`
    INSERT INTO model_pricing (model_name, input_cost_per_1k, output_cost_per_1k)
    VALUES (?, ?, ?)
    ON CONFLICT(model_name) DO UPDATE SET
      input_cost_per_1k  = excluded.input_cost_per_1k,
      output_cost_per_1k = excluded.output_cost_per_1k
  `);

  const seedData: Array<[string, number, number]> = [
    ["claude-sonnet-4-5-20250929", 0.003, 0.015],
    ["claude-opus-4-6", 0.015, 0.075],
    ["claude-haiku-4-5-20251001", 0.0008, 0.004],
  ];

  const seedTransaction = db.transaction(() => {
    for (const [model, inputCost, outputCost] of seedData) {
      upsertPricing.run(model, inputCost, outputCost);
    }
  });
  seedTransaction();

  return db;
}
