import type { ServerWebSocket } from "bun";
import { config } from "./config";
import { initDatabase } from "./db";
import { initOtel } from "./otel/setup";
import { handlePostEvent, handleGetEvents, setSpanExporter } from "./routes/events";
import { handleGetProjects, handleGetProjectById } from "./routes/projects";
import { handleGetContributors, handleGetContributorById } from "./routes/contributors";
import { handleGetSessions } from "./routes/sessions";
import {
  handleGetStories,
  handlePostStory,
  handleGetStoryById,
  handlePatchStory,
  handlePostReviewCycle,
} from "./routes/stories";
import {
  handleGetKPIs,
  handleGetTrends,
  handleGetLeaderboard,
  handleGetCost,
} from "./routes/dashboard";
import {
  handleWebhookReviewCycle,
  handleWebhookBugFound,
  handleWebhookStoryUpdate,
} from "./routes/webhooks";
import { handleGetSpans, handleGetTraces, handleGetTraceById } from "./routes/spans";

// ── Database ─────────────────────────────────────────────────────────────────

const db = initDatabase();

// ── OTEL ─────────────────────────────────────────────────────────────────────

const sqliteExporter = initOtel(db);
setSpanExporter(sqliteExporter);

// ── WebSocket state ──────────────────────────────────────────────────────────

const wsClients = new Set<ServerWebSocket<unknown>>();

function broadcast(data: unknown): void {
  const message = JSON.stringify(data);
  for (const ws of wsClients) {
    try {
      ws.send(message);
    } catch {
      wsClients.delete(ws);
    }
  }
}

// ── CORS helpers ─────────────────────────────────────────────────────────────

function corsHeaders(): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": config.corsOrigins,
    "Access-Control-Allow-Methods": "GET, POST, PATCH, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
  };
}

function addCors(response: Response): Response {
  const headers = new Headers(response.headers);
  for (const [k, v] of Object.entries(corsHeaders())) {
    headers.set(k, v);
  }
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

function jsonResponse(data: unknown, status: number = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

// ── Static file serving ──────────────────────────────────────────────────────

const CLIENT_DIR = "/app/client";

async function serveStatic(pathname: string): Promise<Response | null> {
  // Strip leading slash and resolve file path
  const filePath = `${CLIENT_DIR}${pathname}`;
  const file = Bun.file(filePath);
  if (await file.exists()) {
    return new Response(file);
  }
  return null;
}

async function serveIndex(): Promise<Response> {
  const indexFile = Bun.file(`${CLIENT_DIR}/index.html`);
  if (await indexFile.exists()) {
    return new Response(indexFile, {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  }
  return jsonResponse({ error: "Dashboard not found" }, 404);
}

// ── Route dispatch ───────────────────────────────────────────────────────────

/**
 * Strip `/api/v1` prefix to normalize versioned routes.
 * Both `/api/events` and `/api/v1/events` resolve to the same handler.
 */
function normalizeApiPath(pathname: string): string {
  if (pathname.startsWith("/api/v1/")) {
    return "/api/" + pathname.slice("/api/v1/".length);
  }
  return pathname;
}

async function handleRequest(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const rawPathname = url.pathname;
  const pathname = normalizeApiPath(rawPathname);
  const method = req.method;

  // ── CORS preflight ───────────────────────────────────────────────────
  if (method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }

  // ── Health ───────────────────────────────────────────────────────────
  if (pathname === "/health" && method === "GET") {
    return jsonResponse({ status: "ok", timestamp: new Date().toISOString() });
  }

  // ── API routes ───────────────────────────────────────────────────────

  // Events
  if (pathname === "/api/events") {
    if (method === "POST") return handlePostEvent(req, db, broadcast);
    if (method === "GET") return handleGetEvents(req, db, broadcast);
    return jsonResponse({ error: "Method not allowed" }, 405);
  }

  // Spans (OTEL)
  if (pathname === "/api/spans" && method === "GET") {
    return handleGetSpans(req, db, broadcast);
  }

  // Traces (OTEL)
  if (pathname === "/api/traces" && method === "GET") {
    return handleGetTraces(req, db, broadcast);
  }
  const traceMatch = pathname.match(/^\/api\/traces\/([^/]+)$/);
  if (traceMatch && method === "GET") {
    return handleGetTraceById(req, db, broadcast, decodeURIComponent(traceMatch[1]));
  }

  // Projects
  if (pathname === "/api/projects" && method === "GET") {
    return handleGetProjects(req, db, broadcast);
  }
  const projectMatch = pathname.match(/^\/api\/projects\/([^/]+)$/);
  if (projectMatch && method === "GET") {
    return handleGetProjectById(req, db, broadcast, decodeURIComponent(projectMatch[1]));
  }

  // Contributors
  if (pathname === "/api/contributors" && method === "GET") {
    return handleGetContributors(req, db, broadcast);
  }
  const contributorMatch = pathname.match(/^\/api\/contributors\/([^/]+)$/);
  if (contributorMatch && method === "GET") {
    return handleGetContributorById(req, db, broadcast, decodeURIComponent(contributorMatch[1]));
  }

  // Sessions
  if (pathname === "/api/sessions" && method === "GET") {
    return handleGetSessions(req, db, broadcast);
  }

  // Stories
  if (pathname === "/api/stories") {
    if (method === "GET") return handleGetStories(req, db, broadcast);
    if (method === "POST") return handlePostStory(req, db, broadcast);
    return jsonResponse({ error: "Method not allowed" }, 405);
  }
  // Story review cycles (must be checked before generic story/:id)
  const reviewCycleMatch = pathname.match(/^\/api\/stories\/([^/]+)\/review-cycles$/);
  if (reviewCycleMatch && method === "POST") {
    return handlePostReviewCycle(req, db, broadcast, decodeURIComponent(reviewCycleMatch[1]));
  }
  const storyMatch = pathname.match(/^\/api\/stories\/([^/]+)$/);
  if (storyMatch) {
    const storyId = decodeURIComponent(storyMatch[1]);
    if (method === "GET") return handleGetStoryById(req, db, broadcast, storyId);
    if (method === "PATCH") return handlePatchStory(req, db, broadcast, storyId);
    return jsonResponse({ error: "Method not allowed" }, 405);
  }

  // Dashboard
  if (pathname === "/api/dashboard/kpis" && method === "GET") {
    return handleGetKPIs(req, db, broadcast);
  }
  if (pathname === "/api/dashboard/trends" && method === "GET") {
    return handleGetTrends(req, db, broadcast);
  }
  if (pathname === "/api/dashboard/leaderboard" && method === "GET") {
    return handleGetLeaderboard(req, db, broadcast);
  }
  if (pathname === "/api/dashboard/cost" && method === "GET") {
    return handleGetCost(req, db, broadcast);
  }

  // Webhooks
  if (pathname === "/api/webhooks/review-cycle" && method === "POST") {
    return handleWebhookReviewCycle(req, db, broadcast);
  }
  if (pathname === "/api/webhooks/bug-found" && method === "POST") {
    return handleWebhookBugFound(req, db, broadcast);
  }
  if (pathname === "/api/webhooks/story-update" && method === "POST") {
    return handleWebhookStoryUpdate(req, db, broadcast);
  }

  // ── Static files / SPA fallback ─────────────────────────────────────
  if (!rawPathname.startsWith("/api/") && rawPathname !== "/ws") {
    // Try to serve static asset
    const staticResponse = await serveStatic(rawPathname);
    if (staticResponse) return staticResponse;

    // SPA fallback: serve index.html for any unmatched non-API path
    return serveIndex();
  }

  return jsonResponse({ error: "Not found" }, 404);
}

// ── Server ───────────────────────────────────────────────────────────────────

const server = Bun.serve({
  port: config.port,

  async fetch(req, server) {
    const url = new URL(req.url);

    // ── WebSocket upgrade ────────────────────────────────────────────
    if (url.pathname === "/ws") {
      const upgraded = server.upgrade(req);
      if (upgraded) return undefined as unknown as Response;
      return jsonResponse({ error: "WebSocket upgrade failed" }, 400);
    }

    // ── HTTP request ─────────────────────────────────────────────────
    try {
      const response = await handleRequest(req);
      return addCors(response);
    } catch (err) {
      console.error("Unhandled error:", err);
      return addCors(
        jsonResponse({ error: "Internal server error" }, 500),
      );
    }
  },

  websocket: {
    open(ws: ServerWebSocket<unknown>) {
      wsClients.add(ws);
      console.log(`[ws] client connected (${wsClients.size} total)`);
    },

    message(_ws: ServerWebSocket<unknown>, _message: string | Buffer) {
      // Clients don't send meaningful messages; server is push-only.
    },

    close(ws: ServerWebSocket<unknown>) {
      wsClients.delete(ws);
      console.log(`[ws] client disconnected (${wsClients.size} total)`);
    },
  },
});

console.log(`cc-observability server listening on http://localhost:${server.port}`);
console.log(`  Database: ${config.dbPath}`);
console.log(`  CORS origins: ${config.corsOrigins}`);
console.log(`  WebSocket: ws://localhost:${server.port}/ws`);
console.log(`  API versioning: /api/v1/* enabled`);
