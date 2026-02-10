import type {
  Project,
  Contributor,
  Story,
  Event,
  Session,
  ReviewCycle,
  DashboardKPIs,
  TrendData,
  LeaderboardEntry,
  CostData,
  OtelSpan,
  TraceSummary,
} from '../types';

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text().catch(() => 'Unknown error');
    throw new ApiError(body, response.status);
  }

  return response.json() as Promise<T>;
}

// ---- Projects ----

export function fetchProjects(): Promise<Project[]> {
  return apiFetch<Project[]>('/projects');
}

export function fetchProject(id: string): Promise<Project> {
  return apiFetch<Project>(`/projects/${encodeURIComponent(id)}`);
}

// ---- Contributors ----

export function fetchContributors(projectId?: string): Promise<Contributor[]> {
  const query = projectId ? `?project_id=${encodeURIComponent(projectId)}` : '';
  return apiFetch<Contributor[]>(`/contributors${query}`);
}

export function fetchContributor(id: string): Promise<Contributor> {
  return apiFetch<Contributor>(`/contributors/${encodeURIComponent(id)}`);
}

// ---- Stories ----

export interface StoryQueryParams {
  project_id?: string;
  contributor_id?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export function fetchStories(params?: StoryQueryParams): Promise<Story[]> {
  const searchParams = new URLSearchParams();
  if (params?.project_id) searchParams.set('project_id', params.project_id);
  if (params?.contributor_id) searchParams.set('contributor_id', params.contributor_id);
  if (params?.status) searchParams.set('status', params.status);
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiFetch<Story[]>(`/stories${query}`);
}

export function fetchStory(id: string): Promise<Story> {
  return apiFetch<Story>(`/stories/${encodeURIComponent(id)}`);
}

// ---- Events ----

export interface EventQueryParams {
  project_id?: string;
  contributor_id?: string;
  session_id?: string;
  story_id?: string;
  hook_event_type?: string;
  limit?: number;
  offset?: number;
}

export function fetchEvents(params?: EventQueryParams): Promise<Event[]> {
  const searchParams = new URLSearchParams();
  if (params?.project_id) searchParams.set('project_id', params.project_id);
  if (params?.contributor_id) searchParams.set('contributor_id', params.contributor_id);
  if (params?.session_id) searchParams.set('session_id', params.session_id);
  if (params?.story_id) searchParams.set('story_id', params.story_id);
  if (params?.hook_event_type) searchParams.set('hook_event_type', params.hook_event_type);
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiFetch<Event[]>(`/events${query}`);
}

// ---- Sessions ----

export function fetchSessions(params?: {
  project_id?: string;
  contributor_id?: string;
  story_id?: string;
}): Promise<Session[]> {
  const searchParams = new URLSearchParams();
  if (params?.project_id) searchParams.set('project_id', params.project_id);
  if (params?.contributor_id) searchParams.set('contributor_id', params.contributor_id);
  if (params?.story_id) searchParams.set('story_id', params.story_id);
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiFetch<Session[]>(`/sessions${query}`);
}

// ---- Review Cycles ----

export function fetchReviewCycles(storyId: string): Promise<ReviewCycle[]> {
  return apiFetch<ReviewCycle[]>(`/stories/${encodeURIComponent(storyId)}/reviews`);
}

// ---- Dashboard ----

export function fetchDashboardKPIs(): Promise<DashboardKPIs> {
  return apiFetch<DashboardKPIs>('/dashboard/kpis');
}

export function fetchTrends(period?: string): Promise<TrendData[]> {
  const query = period ? `?period=${encodeURIComponent(period)}` : '';
  return apiFetch<TrendData[]>(`/dashboard/trends${query}`);
}

export function fetchLeaderboard(): Promise<LeaderboardEntry[]> {
  return apiFetch<LeaderboardEntry[]>('/dashboard/leaderboard');
}

export function fetchCosts(dimension?: string): Promise<CostData[]> {
  const query = dimension ? `?by=${encodeURIComponent(dimension)}` : '';
  return apiFetch<CostData[]>(`/dashboard/cost${query}`);
}

// ---- OTEL Spans ----

export function fetchSpans(params: {
  trace_id?: string;
  service_name?: string;
  name?: string;
  limit?: number;
}): Promise<OtelSpan[]> {
  const searchParams = new URLSearchParams();
  if (params.trace_id) searchParams.set('trace_id', params.trace_id);
  if (params.service_name) searchParams.set('service_name', params.service_name);
  if (params.name) searchParams.set('name', params.name);
  if (params.limit) searchParams.set('limit', String(params.limit));
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiFetch<OtelSpan[]>(`/v1/spans${query}`);
}

export function fetchTraces(params?: {
  service_name?: string;
  limit?: number;
}): Promise<TraceSummary[]> {
  const searchParams = new URLSearchParams();
  if (params?.service_name) searchParams.set('service_name', params.service_name);
  if (params?.limit) searchParams.set('limit', String(params.limit));
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiFetch<TraceSummary[]>(`/v1/traces${query}`);
}

export function fetchTraceSpans(traceId: string): Promise<OtelSpan[]> {
  return apiFetch<OtelSpan[]>(`/v1/traces/${encodeURIComponent(traceId)}`);
}
