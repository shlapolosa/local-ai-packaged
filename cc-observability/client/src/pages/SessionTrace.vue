<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { Session, OtelSpan } from '../types';
import { fetchSessions, fetchSpans } from '../composables/useApi';
import { relativeTime, formatNumber } from '../composables/useRelativeTime';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const route = useRoute();
const router = useRouter();

const sessions = ref<Session[]>([]);
const spans = ref<OtelSpan[]>([]);
const selectedSessionId = ref<string | null>(null);
const loading = ref(true);
const spansLoading = ref(false);
const error = ref<string | null>(null);
const expandedSpans = ref<Set<string>>(new Set());
const filterType = ref<string>('all');
const sessionSearch = ref('');

// ── Selected session object ────────────────────────────────────
const selectedSession = computed(() =>
  sessions.value.find(s => s.session_id === selectedSessionId.value) || null
);

// ── Session filtering ──────────────────────────────────────────
const filteredSessions = computed(() => {
  if (!sessionSearch.value.trim()) return sessions.value;
  const q = sessionSearch.value.toLowerCase();
  return sessions.value.filter(s =>
    s.session_id.toLowerCase().includes(q) ||
    s.project_id.toLowerCase().includes(q) ||
    s.contributor_id.toLowerCase().includes(q) ||
    (s.model_name || '').toLowerCase().includes(q) ||
    formatSessionTime(s.started_at).toLowerCase().includes(q)
  );
});

// ── Convert session_id to OTEL trace_id (same logic as server) ──
function sessionToTraceId(sessionId: string): string {
  const hex = sessionId.replace(/-/g, '');
  if (hex.length >= 32) return hex.substring(0, 32);
  return hex.padEnd(32, '0');
}

// ── Filter spans by type ──────────────────────────────────────
const filteredSpans = computed(() => {
  if (filterType.value === 'all') return spans.value;
  if (filterType.value === 'tools') return spans.value.filter(s => s.tool_name != null);
  if (filterType.value === 'lifecycle') return spans.value.filter(s => s.tool_name == null);
  return spans.value;
});

// ── Helpers ────────────────────────────────────────────────────

function toggleSpan(spanId: string) {
  if (expandedSpans.value.has(spanId)) {
    expandedSpans.value.delete(spanId);
  } else {
    expandedSpans.value.add(spanId);
  }
  expandedSpans.value = new Set(expandedSpans.value);
}

function selectSession(sessionId: string) {
  selectedSessionId.value = sessionId;
  router.replace({ query: { session: sessionId } });
}

function formatSessionTime(dateStr: string | null): string {
  if (!dateStr) return '--';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
    ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function formatMs(ms: number | null): string {
  if (ms == null) return '--';
  if (ms < 1000) return `${Math.round(ms)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

function nanoToTime(nano: string | null): string {
  if (!nano) return '--';
  const ms = Number(BigInt(nano) / 1_000_000n);
  const d = new Date(ms);
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}

function spanStatus(statusCode: number): 'success' | 'failure' | 'pending' {
  if (statusCode === 1) return 'success';  // OK
  if (statusCode === 2) return 'failure';  // ERROR
  return 'pending'; // UNSET
}

function toolColor(toolName: string): string {
  const colors: Record<string, string> = {
    Bash: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    Read: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    Write: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    Edit: 'bg-green-500/20 text-green-400 border-green-500/30',
    Grep: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    Glob: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
    Task: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
    WebFetch: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    WebSearch: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
  };
  return colors[toolName] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
}

function statusIcon(status: string): string {
  if (status === 'success') return '\u2713';
  if (status === 'failure') return '\u2717';
  return '\u22EF';
}

function statusColor(status: string): string {
  if (status === 'success') return 'text-emerald-400';
  if (status === 'failure') return 'text-red-400';
  return 'text-yellow-400';
}

function eventIcon(span: OtelSpan): string {
  if (span.tool_name) return '\uD83D\uDD27';
  const icons: Record<string, string> = {
    UserPromptSubmit: '\uD83D\uDCAC',
    Stop: '\u23F9',
    Notification: '\uD83D\uDD14',
    SubagentStart: '\uD83D\uDE80',
    SubagentStop: '\uD83C\uDFC1',
    PreCompact: '\uD83D\uDCE6',
    SessionStart: '\u25B6',
    SessionEnd: '\u23F8',
  };
  return icons[span.name] || '\uD83D\uDCCC';
}

function spanSummary(span: OtelSpan): string {
  if (span.input_payload) {
    try {
      const input = JSON.parse(span.input_payload);
      return input.description || input.command?.substring(0, 80) || input.file_path || '';
    } catch {}
  }
  return span.status_message || span.name;
}

function truncate(str: string, max: number): string {
  if (!str) return '';
  return str.length > max ? str.substring(0, max) + '\u2026' : str;
}

function formatJson(obj: any): string {
  if (obj == null) return '';
  if (typeof obj === 'string') {
    try { obj = JSON.parse(obj); } catch { return obj; }
  }
  return JSON.stringify(obj, null, 2);
}

async function loadSessions() {
  loading.value = true;
  error.value = null;
  try {
    sessions.value = await fetchSessions();
  } catch (err: any) {
    error.value = err.message || 'Failed to load sessions';
  } finally {
    loading.value = false;
  }
}

async function loadSpans(sessionId: string) {
  spansLoading.value = true;
  try {
    const traceId = sessionToTraceId(sessionId);
    spans.value = await fetchSpans({ trace_id: traceId, limit: 500 });
  } catch (err: any) {
    error.value = err.message;
  } finally {
    spansLoading.value = false;
  }
}

watch(selectedSessionId, (id) => {
  if (id) {
    expandedSpans.value = new Set();
    loadSpans(id);
  }
});

onMounted(async () => {
  await loadSessions();
  const querySession = route.query.session as string;
  if (querySession && sessions.value.some(s => s.session_id === querySession)) {
    selectedSessionId.value = querySession;
  } else if (sessions.value.length > 0) {
    selectedSessionId.value = sessions.value[0].session_id;
  }
});
</script>

<template>
  <div class="flex gap-4 h-[calc(100vh-4rem)]">
    <!-- ── Left panel: Session list ──────────────────────────── -->
    <div class="w-72 flex-shrink-0 flex flex-col bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden">
      <div class="p-3 border-b border-gray-700/50">
        <h2 class="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-2">Sessions</h2>
        <!-- Search -->
        <input
          v-model="sessionSearch"
          type="text"
          placeholder="Filter sessions…"
          class="w-full px-2.5 py-1.5 bg-gray-900 border border-gray-700 rounded text-xs text-gray-300 placeholder-gray-600 focus:outline-none focus:border-brand-500/50"
        />
      </div>

      <LoadingSpinner v-if="loading" />

      <div v-else class="flex-1 overflow-y-auto">
        <div v-if="filteredSessions.length === 0" class="p-3 text-xs text-gray-600 text-center">
          No sessions found.
        </div>
        <button
          v-for="session in filteredSessions"
          :key="session.session_id"
          @click="selectSession(session.session_id)"
          class="w-full px-3 py-2.5 text-left border-b border-gray-700/30 transition-colors"
          :class="selectedSessionId === session.session_id
            ? 'bg-brand-600/15 border-l-2 border-l-brand-500'
            : 'hover:bg-gray-800/50 border-l-2 border-l-transparent'"
        >
          <!-- Timestamp (prominent) -->
          <div class="text-xs font-medium" :class="selectedSessionId === session.session_id ? 'text-brand-300' : 'text-gray-300'">
            {{ formatSessionTime(session.started_at) }}
          </div>
          <!-- Session ID -->
          <div class="font-mono text-[10px] mt-0.5" :class="selectedSessionId === session.session_id ? 'text-brand-400/70' : 'text-gray-600'">
            {{ session.session_id.substring(0, 16) }}…
          </div>
          <!-- Meta row -->
          <div class="flex items-center gap-2 mt-1">
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-700/50 text-gray-400 truncate max-w-[7rem]">
              {{ session.project_id }}
            </span>
            <span v-if="session.contributor_id" class="text-[10px] text-gray-600 truncate">
              {{ session.contributor_id.substring(0, 10) }}
            </span>
          </div>
          <!-- Event count + model -->
          <div class="flex items-center gap-2 mt-1">
            <span v-if="session.event_count != null" class="text-[10px] text-gray-500">
              {{ session.event_count }} events
            </span>
            <span v-if="session.model_name" class="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400/70 truncate">
              {{ session.model_name }}
            </span>
          </div>
          <!-- Status -->
          <div class="flex items-center gap-1.5 mt-1">
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="session.ended_at ? 'bg-gray-500' : 'bg-emerald-400 animate-pulse'"
            ></span>
            <span class="text-[10px]" :class="session.ended_at ? 'text-gray-600' : 'text-emerald-500/70'">
              {{ session.ended_at ? 'Ended' : 'Active' }}
            </span>
            <span class="text-[10px] text-gray-600 ml-auto">
              {{ relativeTime(session.started_at) }}
            </span>
          </div>
        </button>
      </div>
    </div>

    <!-- ── Right panel: Spans ────────────────────────────────── -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Header with session info -->
      <div v-if="selectedSession" class="flex items-center justify-between mb-3">
        <div>
          <h1 class="text-lg font-bold text-white flex items-center gap-2">
            Session Trace
            <span
              class="w-2 h-2 rounded-full"
              :class="selectedSession.ended_at ? 'bg-gray-500' : 'bg-emerald-400 animate-pulse'"
            ></span>
          </h1>
          <p class="text-xs text-gray-500 font-mono mt-0.5">
            {{ selectedSession.session_id }}
            <span class="text-gray-600 mx-1">·</span>
            {{ formatSessionTime(selectedSession.started_at) }}
            <span class="text-gray-600 mx-1">·</span>
            {{ selectedSession.project_id }}
          </p>
        </div>
      </div>
      <div v-else class="mb-3">
        <h1 class="text-lg font-bold text-white">Session Traces</h1>
        <p class="text-xs text-gray-500 mt-0.5">Select a session to view its traces</p>
      </div>

      <!-- Filter bar -->
      <div v-if="selectedSessionId" class="flex items-center gap-2 text-sm mb-3 flex-shrink-0">
        <span class="text-gray-500 text-xs">Filter:</span>
        <button
          v-for="f in ['all', 'tools', 'lifecycle']"
          :key="f"
          @click="filterType = f"
          class="px-2.5 py-1 rounded text-xs transition-colors"
          :class="filterType === f
            ? 'bg-gray-700 text-white'
            : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'"
        >
          {{ f === 'all' ? `All (${spans.length})` : f === 'tools' ? 'Tool Calls' : 'Lifecycle' }}
        </button>
        <button
          @click="loadSpans(selectedSessionId!)"
          class="ml-auto px-2.5 py-1 rounded text-xs text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors"
          :disabled="spansLoading"
        >
          {{ spansLoading ? 'Loading…' : '↻ Refresh' }}
        </button>
      </div>

      <!-- Spans list -->
      <div class="flex-1 overflow-y-auto space-y-1">
        <LoadingSpinner v-if="spansLoading && spans.length === 0" />

        <div v-else-if="!selectedSessionId" class="card text-center py-12 text-gray-500 text-sm">
          Select a session from the left panel to view traces.
        </div>

        <div v-else-if="filteredSpans.length === 0" class="card text-center py-8 text-gray-500 text-sm">
          No spans found for this session.
        </div>

        <div
          v-for="span in filteredSpans"
          :key="span.span_id"
          class="rounded-lg border transition-all"
          :class="expandedSpans.has(span.span_id)
            ? 'bg-gray-800 border-gray-600'
            : 'bg-gray-800/50 border-gray-700/50 hover:border-gray-600'"
        >
          <!-- Span header -->
          <button
            @click="toggleSpan(span.span_id)"
            class="w-full px-4 py-2.5 flex items-center gap-3 text-left"
          >
            <svg
              class="w-3.5 h-3.5 text-gray-500 transition-transform flex-shrink-0"
              :class="{ 'rotate-90': expandedSpans.has(span.span_id) }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>

            <span class="text-xs flex-shrink-0" :class="statusColor(spanStatus(span.status_code))">
              {{ statusIcon(spanStatus(span.status_code)) }}
            </span>

            <span class="text-xs flex-shrink-0">{{ eventIcon(span) }}</span>

            <span
              v-if="span.tool_name"
              class="px-2 py-0.5 rounded text-xs font-mono border flex-shrink-0"
              :class="toolColor(span.tool_name)"
            >
              {{ span.tool_name }}
            </span>
            <span
              v-else
              class="px-2 py-0.5 rounded text-xs font-mono bg-gray-700/50 text-gray-400 border border-gray-600/50 flex-shrink-0"
            >
              {{ span.name }}
            </span>

            <span class="text-sm text-gray-300 truncate flex-1 min-w-0">
              {{ truncate(spanSummary(span), 100) }}
            </span>

            <span v-if="span.duration_ms != null" class="text-xs text-gray-500 tabular-nums flex-shrink-0">
              {{ formatMs(span.duration_ms) }}
            </span>

            <span class="text-[10px] text-gray-600 tabular-nums flex-shrink-0 hidden sm:inline">
              {{ nanoToTime(span.start_time_unix_nano) }}
            </span>
          </button>

          <!-- Expanded detail -->
          <div v-if="expandedSpans.has(span.span_id)" class="px-4 pb-4 border-t border-gray-700/50">
            <div class="flex flex-wrap gap-4 py-3 text-xs text-gray-500">
              <div v-if="span.tool_name">
                <span class="text-gray-600">Tool:</span>
                <span class="text-gray-400 ml-1">{{ span.tool_name }}</span>
              </div>
              <div>
                <span class="text-gray-600">Span:</span>
                <span class="text-gray-400 ml-1">{{ span.name }}</span>
              </div>
              <div>
                <span class="text-gray-600">Status:</span>
                <span class="text-gray-400 ml-1">{{ span.status_code === 1 ? 'OK' : span.status_code === 2 ? 'ERROR' : 'UNSET' }}</span>
              </div>
              <div v-if="span.duration_ms != null">
                <span class="text-gray-600">Duration:</span>
                <span class="text-gray-400 ml-1">{{ formatMs(span.duration_ms) }}</span>
              </div>
              <div>
                <span class="text-gray-600">Span ID:</span>
                <span class="text-gray-400 ml-1 font-mono">{{ span.span_id }}</span>
              </div>
              <div v-if="span.parent_span_id">
                <span class="text-gray-600">Parent:</span>
                <span class="text-gray-400 ml-1 font-mono">{{ span.parent_span_id }}</span>
              </div>
            </div>

            <div v-if="span.input_payload" class="mb-3">
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                Input
              </div>
              <pre class="bg-gray-900 rounded-md p-3 text-xs text-gray-300 overflow-x-auto max-h-80 overflow-y-auto font-mono leading-relaxed whitespace-pre-wrap break-words">{{ formatJson(span.input_payload) }}</pre>
            </div>

            <div v-if="span.output_payload">
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 17l-5-5m0 0l5-5m-5 5h12" />
                </svg>
                Output
              </div>
              <pre class="bg-gray-900 rounded-md p-3 text-xs text-gray-300 overflow-x-auto max-h-80 overflow-y-auto font-mono leading-relaxed whitespace-pre-wrap break-words">{{ formatJson(span.output_payload) }}</pre>
            </div>

            <div v-if="!span.input_payload && !span.output_payload && span.attributes">
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Attributes</div>
              <pre class="bg-gray-900 rounded-md p-3 text-xs text-gray-300 overflow-x-auto max-h-80 overflow-y-auto font-mono leading-relaxed whitespace-pre-wrap break-words">{{ formatJson(span.attributes) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
