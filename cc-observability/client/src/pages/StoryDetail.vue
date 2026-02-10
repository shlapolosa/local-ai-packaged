<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { Story, Event, ReviewCycle } from '../types';
import { fetchStory, fetchEvents } from '../composables/useApi';
import { relativeTime, formatDuration, formatNumber, formatCost } from '../composables/useRelativeTime';
import KpiCard from '../components/KpiCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const props = defineProps<{ id: string }>();
const router = useRouter();

const story = ref<Story | null>(null);
const events = ref<Event[]>([]);
const reviewCycles = ref<ReviewCycle[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

// Rough cost estimation: using claude-sonnet-4-5 pricing as default
const INPUT_COST_PER_1K = 0.003;
const OUTPUT_COST_PER_1K = 0.015;

const estimatedCost = computed(() => {
  if (!story.value) return 0;
  return (
    (story.value.total_input_tokens / 1000) * INPUT_COST_PER_1K +
    (story.value.total_output_tokens / 1000) * OUTPUT_COST_PER_1K
  );
});

const totalLines = computed(() => {
  if (!story.value) return 0;
  return story.value.lines_added + story.value.lines_removed;
});

const totalTokens = computed(() => {
  if (!story.value) return 0;
  return story.value.total_input_tokens + story.value.total_output_tokens;
});

const storyDuration = computed(() => {
  if (!story.value?.started_at) return null;
  const start = new Date(story.value.started_at).getTime();
  const end = story.value.completed_at
    ? new Date(story.value.completed_at).getTime()
    : Date.now();
  return (end - start) / 60000;
});

function eventBadgeClass(hookType: string): string {
  const map: Record<string, string> = {
    'PreToolUse': 'badge-cyan',
    'PostToolUse': 'badge-blue',
    'Notification': 'badge-yellow',
    'Stop': 'badge-red',
    'SubagentStop': 'badge-orange',
    'PreCompact': 'badge-purple',
    'PostCompact': 'badge-purple',
  };
  return map[hookType] || 'badge-blue';
}

function shortEventType(hookType: string): string {
  return hookType.replace(/([A-Z])/g, ' $1').trim();
}

function reviewStatusBadge(status: string): string {
  switch (status) {
    case 'approved': return 'badge-green';
    case 'rejected': return 'badge-red';
    case 'pending': return 'badge-yellow';
    default: return 'badge-blue';
  }
}

async function loadData() {
  loading.value = true;
  error.value = null;
  try {
    const [storyData, eventData] = await Promise.all([
      fetchStory(props.id),
      fetchEvents({ story_id: props.id, limit: 200 }),
    ]);
    story.value = storyData;
    events.value = eventData;
    reviewCycles.value = (storyData as any).review_cycles || [];
  } catch (err: any) {
    error.value = err.message || 'Failed to load story';
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <div class="space-y-6">
    <!-- Back link -->
    <button
      @click="router.back()"
      class="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back
    </button>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="card text-center py-12">
      <p class="text-red-400 mb-4">{{ error }}</p>
      <button @click="loadData" class="btn-primary">Retry</button>
    </div>

    <template v-else-if="story">
      <!-- Story header -->
      <div class="flex items-start gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-1">
            <h1 class="text-2xl font-bold text-white">{{ story.title }}</h1>
            <StatusBadge :status="story.status" />
          </div>
          <p v-if="story.description" class="text-sm text-gray-400 mt-1">{{ story.description }}</p>
          <div class="flex items-center gap-4 text-xs text-gray-500 mt-2">
            <span>Project: {{ story.project_id }}</span>
            <span>Contributor: {{ story.contributor_id }}</span>
            <span>Started {{ relativeTime(story.started_at) }}</span>
            <span v-if="story.completed_at">Completed {{ relativeTime(story.completed_at) }}</span>
          </div>
        </div>
      </div>

      <!-- KPI row -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard
          title="Duration"
          :value="formatDuration(storyDuration)"
        />
        <KpiCard
          title="Lines Changed"
          :value="formatNumber(totalLines)"
          :subtitle="`+${story.lines_added} / -${story.lines_removed}`"
        />
        <KpiCard
          title="Review Cycles"
          :value="reviewCycles.length"
        />
        <KpiCard
          title="Bugs Found"
          :value="story.bugs_found"
        />
        <KpiCard
          title="Total Tokens"
          :value="formatNumber(totalTokens)"
          :subtitle="`In: ${formatNumber(story.total_input_tokens)} / Out: ${formatNumber(story.total_output_tokens)}`"
        />
        <KpiCard
          title="Est. Cost"
          :value="formatCost(estimatedCost)"
        />
      </div>

      <!-- Review Cycles timeline -->
      <div v-if="reviewCycles.length > 0">
        <h2 class="text-lg font-semibold text-white mb-3">Review Cycles</h2>
        <div class="card space-y-3">
          <div
            v-for="(review, idx) in reviewCycles"
            :key="review.id"
            class="flex items-start gap-3"
          >
            <!-- Timeline connector -->
            <div class="flex flex-col items-center flex-shrink-0">
              <div
                class="w-3 h-3 rounded-full border-2"
                :class="{
                  'border-emerald-400 bg-emerald-400/20': review.status === 'approved',
                  'border-red-400 bg-red-400/20': review.status === 'rejected',
                  'border-yellow-400 bg-yellow-400/20': review.status === 'pending',
                  'border-gray-500 bg-gray-500/20': !['approved','rejected','pending'].includes(review.status),
                }"
              ></div>
              <div
                v-if="idx < reviewCycles.length - 1"
                class="w-px h-8 bg-gray-700"
              ></div>
            </div>

            <div class="flex-1 min-w-0 pb-2">
              <div class="flex items-center gap-2">
                <span :class="reviewStatusBadge(review.status)">{{ review.status }}</span>
                <span class="text-xs text-gray-500">Submitted {{ relativeTime(review.submitted_at) }}</span>
                <span v-if="review.returned_at" class="text-xs text-gray-500">
                  -- Returned {{ relativeTime(review.returned_at) }}
                </span>
              </div>
              <p v-if="review.feedback" class="text-sm text-gray-400 mt-1">{{ review.feedback }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Event timeline -->
      <div>
        <h2 class="text-lg font-semibold text-white mb-3">
          Event Timeline
          <span class="text-sm font-normal text-gray-500">({{ events.length }} events)</span>
        </h2>
        <div v-if="events.length === 0" class="card text-center py-8 text-gray-500 text-sm">
          No events recorded for this story.
        </div>
        <div v-else class="card space-y-0 p-0 divide-y divide-gray-700/40">
          <div
            v-for="event in events"
            :key="event.id"
            class="flex items-start gap-3 px-4 py-3 hover:bg-gray-700/20 transition-colors"
          >
            <div class="flex-shrink-0 mt-0.5">
              <span :class="eventBadgeClass(event.hook_event_type)" class="text-[10px]">
                {{ shortEventType(event.hook_event_type) }}
              </span>
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span v-if="event.tool_name" class="text-sm text-white font-medium">
                  {{ event.tool_name }}
                </span>
                <span v-if="event.model_name" class="text-xs text-gray-500">
                  {{ event.model_name }}
                </span>
              </div>
              <p v-if="event.summary" class="text-xs text-gray-400 mt-0.5 truncate">
                {{ event.summary }}
              </p>
              <div v-if="event.input_tokens || event.output_tokens" class="text-xs text-gray-600 mt-0.5">
                {{ formatNumber(event.input_tokens) }} in / {{ formatNumber(event.output_tokens) }} out
              </div>
            </div>

            <span class="text-xs text-gray-500 whitespace-nowrap flex-shrink-0">
              {{ relativeTime(event.timestamp) }}
            </span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
