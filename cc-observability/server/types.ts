// ─── Entity Types ────────────────────────────────────────────────────────────

export interface Project {
  project_id: string;
  display_name: string;
  git_remote_url: string;
  first_seen_at: string;
  last_active_at: string;
}

export interface Contributor {
  contributor_id: string;
  display_name: string;
  first_seen_at: string;
  last_active_at: string;
}

export type StoryStatus = "in_progress" | "completed" | "abandoned";

export interface Story {
  story_id: string;
  project_id: string;
  contributor_id: string;
  title: string;
  description: string;
  status: StoryStatus;
  started_at: string;
  completed_at: string | null;
  estimated_minutes: number | null;
  actual_minutes: number | null;
  lines_added: number;
  lines_removed: number;
  review_cycles: number;
  bugs_found: number;
  total_input_tokens: number;
  total_output_tokens: number;
}

export interface Session {
  session_id: string;
  project_id: string;
  contributor_id: string;
  story_id: string | null;
  model_name: string;
  started_at: string;
  ended_at: string | null;
  end_reason: string | null;
  total_input_tokens: number;
  total_output_tokens: number;
}

export interface Event {
  id: number;
  project_id: string;
  contributor_id: string;
  session_id: string;
  story_id: string | null;
  hook_event_type: string;
  payload: string;
  chat: string | null;
  summary: string | null;
  tool_name: string | null;
  model_name: string | null;
  timestamp: string;
  input_tokens: number;
  output_tokens: number;
}

export interface ReviewCycle {
  id: number;
  story_id: string;
  submitted_at: string;
  returned_at: string | null;
  feedback: string | null;
  status: string;
}

export interface ModelPricing {
  model_name: string;
  input_cost_per_1k: number;
  output_cost_per_1k: number;
}

// ─── API Payload Types ───────────────────────────────────────────────────────

export interface EventPayload {
  project_id: string;
  contributor_id: string;
  session_id: string;
  story_id?: string | null;
  hook_event_type: string;
  payload: unknown;
  chat?: string | null;
  summary?: string | null;
  tool_name?: string | null;
  model_name?: string | null;
  input_tokens?: number;
  output_tokens?: number;
}

export interface CreateStoryPayload {
  story_id?: string;
  project_id: string;
  contributor_id: string;
  title: string;
  description?: string;
  estimated_minutes?: number;
}

export interface UpdateStoryPayload {
  title?: string;
  description?: string;
  status?: StoryStatus;
  completed_at?: string;
  estimated_minutes?: number;
  actual_minutes?: number;
  lines_added?: number;
  lines_removed?: number;
  review_cycles?: number;
  bugs_found?: number;
  total_input_tokens?: number;
  total_output_tokens?: number;
}

export interface ReviewCyclePayload {
  story_id?: string;
  feedback?: string;
  submitted_at?: string;
  returned_at?: string;
}

export interface BugFoundPayload {
  story_id: string;
  description?: string;
}

export interface StoryUpdateWebhookPayload {
  story_id: string;
  [key: string]: unknown;
}

// ─── Dashboard Types ─────────────────────────────────────────────────────────

export interface DashboardKPIs {
  total_projects: number;
  total_contributors: number;
  total_stories: number;
  stories_completed: number;
  avg_time_per_story: number | null;
  avg_lines_per_story: number | null;
  avg_review_cycles: number | null;
  avg_bugs_per_story: number | null;
  total_input_tokens: number;
  total_output_tokens: number;
  estimated_total_cost: number;
}

export interface TrendData {
  period: string;
  stories_completed: number;
  avg_time: number | null;
  total_tokens: number;
  estimated_cost: number;
}

export interface LeaderboardEntry {
  contributor_id: string;
  display_name: string;
  stories_completed: number;
  avg_quality: number;
  efficiency: number;
}

export interface CostData {
  dimension: string;
  dimension_value: string;
  total_input_tokens: number;
  total_output_tokens: number;
  estimated_cost: number;
}

// ─── OTEL Span Type ─────────────────────────────────────────────────────────

export interface OtelSpan {
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  trace_state: string | null;
  name: string;
  kind: number;
  start_time_unix_nano: string;
  end_time_unix_nano: string | null;
  duration_ms: number | null;
  status_code: number;
  status_message: string | null;
  service_name: string;
  service_instance_id: string;
  tool_name: string | null;
  model_name: string | null;
  input_tokens: number;
  output_tokens: number;
  story_id: string | null;
  attributes: string | null;
  events: string | null;
  links: string | null;
  resource_attributes: string | null;
  input_payload: string | null;
  output_payload: string | null;
}

export interface TraceSummary {
  trace_id: string;
  service_name: string;
  span_count: number;
  first_span: string;
  last_span: string | null;
  duration_ms: number | null;
  error_count: number;
}

// ─── Route Handler Signature ─────────────────────────────────────────────────

export type BroadcastFn = (data: unknown) => void;
