<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { Contributor, Story, Session } from '../types';
import { fetchContributor, fetchStories, fetchSessions } from '../composables/useApi';
import { relativeTime, formatDuration, formatNumber } from '../composables/useRelativeTime';
import KpiCard from '../components/KpiCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const props = defineProps<{ id: string }>();
const router = useRouter();

const contributor = ref<Contributor | null>(null);
const stories = ref<Story[]>([]);
const sessions = ref<Session[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const storiesCompleted = computed(() =>
  stories.value.filter((s) => s.status === 'completed').length
);

const avgTime = computed(() => {
  const completed = stories.value.filter((s) => s.status === 'completed' && s.actual_minutes);
  if (completed.length === 0) return null;
  return completed.reduce((sum, s) => sum + (s.actual_minutes || 0), 0) / completed.length;
});

const totalTokens = computed(() =>
  sessions.value.reduce((sum, s) => sum + s.total_input_tokens + s.total_output_tokens, 0)
);

async function loadData() {
  loading.value = true;
  error.value = null;
  try {
    const [contrib, storyList, sessionList] = await Promise.all([
      fetchContributor(props.id),
      fetchStories({ contributor_id: props.id }),
      fetchSessions({ contributor_id: props.id }),
    ]);
    contributor.value = contrib;
    stories.value = storyList;
    sessions.value = sessionList;
  } catch (err: any) {
    error.value = err.message || 'Failed to load contributor';
  } finally {
    loading.value = false;
  }
}

function sessionDuration(session: Session): string {
  if (!session.started_at) return '--';
  const start = new Date(session.started_at).getTime();
  const end = session.ended_at ? new Date(session.ended_at).getTime() : Date.now();
  const minutes = (end - start) / 60000;
  return formatDuration(minutes);
}

function goToStory(id: string) {
  router.push({ name: 'story-detail', params: { id } });
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

    <template v-else-if="contributor">
      <!-- Contributor header -->
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 rounded-full bg-brand-600/30 flex items-center justify-center text-brand-400 font-bold text-xl flex-shrink-0">
          {{ (contributor.display_name || contributor.contributor_id).charAt(0).toUpperCase() }}
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white">
            {{ contributor.display_name || contributor.contributor_id }}
          </h1>
          <p class="text-sm text-gray-400 mt-0.5">
            ID: {{ contributor.contributor_id }}
          </p>
          <p class="text-xs text-gray-500">
            First seen {{ relativeTime(contributor.first_seen_at) }} -- Last active {{ relativeTime(contributor.last_active_at) }}
          </p>
        </div>
      </div>

      <!-- KPI row -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <KpiCard
          title="Stories Completed"
          :value="storiesCompleted"
          :subtitle="`${stories.length} total`"
        />
        <KpiCard
          title="Avg Time/Story"
          :value="avgTime != null ? formatDuration(avgTime) : '--'"
        />
        <KpiCard
          title="Total Tokens"
          :value="formatNumber(totalTokens)"
          subtitle="Input + Output"
        />
      </div>

      <!-- Sessions table -->
      <div>
        <h2 class="text-lg font-semibold text-white mb-3">Session History</h2>
        <div v-if="sessions.length === 0" class="card text-center py-8 text-gray-500 text-sm">
          No sessions recorded.
        </div>
        <div v-else class="card overflow-x-auto p-0">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-700 text-gray-400 text-xs uppercase tracking-wider">
                <th class="text-left px-4 py-3 font-medium">Session ID</th>
                <th class="text-left px-4 py-3 font-medium">Model</th>
                <th class="text-left px-4 py-3 font-medium">Started</th>
                <th class="text-right px-4 py-3 font-medium">Duration</th>
                <th class="text-right px-4 py-3 font-medium">Tokens</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="session in sessions"
                :key="session.session_id"
                class="table-row cursor-pointer"
                @click="router.push({ name: 'traces', query: { session: session.session_id } })"
              >
                <td class="px-4 py-3 text-brand-400 font-mono text-xs hover:underline">
                  {{ session.session_id.substring(0, 12) }}...
                </td>
                <td class="px-4 py-3">
                  <span class="badge-purple">{{ session.model_name || 'unknown' }}</span>
                </td>
                <td class="px-4 py-3 text-gray-400">
                  {{ relativeTime(session.started_at) }}
                </td>
                <td class="px-4 py-3 text-right text-gray-300">
                  {{ sessionDuration(session) }}
                </td>
                <td class="px-4 py-3 text-right text-gray-300">
                  {{ formatNumber(session.total_input_tokens + session.total_output_tokens) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Story history -->
      <div>
        <h2 class="text-lg font-semibold text-white mb-3">Story History</h2>
        <div v-if="stories.length === 0" class="card text-center py-8 text-gray-500 text-sm">
          No stories associated with this contributor.
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="story in stories"
            :key="story.story_id"
            class="card-hover flex items-center justify-between"
            @click="goToStory(story.story_id)"
          >
            <div class="min-w-0 flex-1">
              <div class="text-sm font-medium text-white truncate">{{ story.title }}</div>
              <div class="text-xs text-gray-500 mt-0.5">
                Started {{ relativeTime(story.started_at) }}
                <span v-if="story.actual_minutes"> -- {{ formatDuration(story.actual_minutes) }}</span>
              </div>
            </div>
            <div class="flex items-center gap-3 ml-4 flex-shrink-0">
              <StatusBadge :status="story.status" />
              <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
