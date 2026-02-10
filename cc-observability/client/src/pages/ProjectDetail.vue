<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { Project, Contributor, Story } from '../types';
import { fetchProject, fetchContributors, fetchStories } from '../composables/useApi';
import { relativeTime, formatDuration, formatNumber } from '../composables/useRelativeTime';
import KpiCard from '../components/KpiCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const props = defineProps<{ id: string }>();
const router = useRouter();

const project = ref<Project | null>(null);
const contributors = ref<Contributor[]>([]);
const stories = ref<Story[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const avgTimePerStory = computed(() => {
  const completed = stories.value.filter((s) => s.status === 'completed' && s.actual_minutes);
  if (completed.length === 0) return null;
  const total = completed.reduce((sum, s) => sum + (s.actual_minutes || 0), 0);
  return total / completed.length;
});

const avgLinesPerStory = computed(() => {
  if (stories.value.length === 0) return null;
  const total = stories.value.reduce((sum, s) => sum + s.lines_added + s.lines_removed, 0);
  return Math.round(total / stories.value.length);
});

const totalContributors = computed(() => contributors.value.length);
const totalStories = computed(() => stories.value.length);

async function loadData() {
  loading.value = true;
  error.value = null;
  try {
    const [proj, contribs, storyList] = await Promise.all([
      fetchProject(props.id),
      fetchContributors(props.id),
      fetchStories({ project_id: props.id }),
    ]);
    project.value = proj;
    contributors.value = contribs;
    stories.value = storyList;
  } catch (err: any) {
    error.value = err.message || 'Failed to load project';
  } finally {
    loading.value = false;
  }
}

function goToContributor(id: string) {
  router.push({ name: 'contributor-detail', params: { id } });
}

function goToStory(id: string) {
  router.push({ name: 'story-detail', params: { id } });
}

onMounted(loadData);
</script>

<template>
  <div class="space-y-6">
    <!-- Back link -->
    <router-link to="/" class="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back to Projects
    </router-link>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="card text-center py-12">
      <p class="text-red-400 mb-4">{{ error }}</p>
      <button @click="loadData" class="btn-primary">Retry</button>
    </div>

    <template v-else-if="project">
      <!-- Project header -->
      <div>
        <h1 class="text-2xl font-bold text-white">{{ project.display_name || project.project_id }}</h1>
        <p v-if="project.git_remote_url" class="text-sm text-gray-400 mt-1">{{ project.git_remote_url }}</p>
        <p class="text-xs text-gray-500 mt-1">
          First seen {{ relativeTime(project.first_seen_at) }} -- Last active {{ relativeTime(project.last_active_at) }}
        </p>
      </div>

      <!-- KPI row -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KpiCard title="Contributors" :value="totalContributors" />
        <KpiCard title="Stories" :value="totalStories" />
        <KpiCard
          title="Avg Time/Story"
          :value="avgTimePerStory != null ? formatDuration(avgTimePerStory) : '--'"
        />
        <KpiCard
          title="Avg Lines/Story"
          :value="avgLinesPerStory != null ? formatNumber(avgLinesPerStory) : '--'"
        />
      </div>

      <!-- Contributors grid -->
      <div>
        <h2 class="text-lg font-semibold text-white mb-3">Contributors</h2>
        <div v-if="contributors.length === 0" class="card text-center py-8 text-gray-500 text-sm">
          No contributors yet.
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            v-for="contributor in contributors"
            :key="contributor.contributor_id"
            class="card-hover"
            @click="goToContributor(contributor.contributor_id)"
          >
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-brand-600/30 flex items-center justify-center text-brand-400 font-bold text-sm flex-shrink-0">
                {{ (contributor.display_name || contributor.contributor_id).charAt(0).toUpperCase() }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-sm font-medium text-white truncate">
                  {{ contributor.display_name || contributor.contributor_id }}
                </div>
                <div class="text-xs text-gray-500">
                  Last active {{ relativeTime(contributor.last_active_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stories table -->
      <div>
        <h2 class="text-lg font-semibold text-white mb-3">Stories</h2>
        <div v-if="stories.length === 0" class="card text-center py-8 text-gray-500 text-sm">
          No stories yet.
        </div>
        <div v-else class="card overflow-x-auto p-0">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-700 text-gray-400 text-xs uppercase tracking-wider">
                <th class="text-left px-4 py-3 font-medium">Title</th>
                <th class="text-left px-4 py-3 font-medium">Status</th>
                <th class="text-left px-4 py-3 font-medium">Contributor</th>
                <th class="text-right px-4 py-3 font-medium">Duration</th>
                <th class="text-right px-4 py-3 font-medium">Lines</th>
                <th class="text-right px-4 py-3 font-medium">Reviews</th>
                <th class="text-right px-4 py-3 font-medium">Bugs</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="story in stories"
                :key="story.story_id"
                class="table-row cursor-pointer"
                @click="goToStory(story.story_id)"
              >
                <td class="px-4 py-3 text-white font-medium max-w-xs truncate">
                  {{ story.title }}
                </td>
                <td class="px-4 py-3">
                  <StatusBadge :status="story.status" />
                </td>
                <td class="px-4 py-3 text-gray-400">
                  {{ story.contributor_id }}
                </td>
                <td class="px-4 py-3 text-right text-gray-300">
                  {{ formatDuration(story.actual_minutes) }}
                </td>
                <td class="px-4 py-3 text-right">
                  <span class="text-emerald-400">+{{ story.lines_added }}</span>
                  <span class="text-gray-600 mx-0.5">/</span>
                  <span class="text-red-400">-{{ story.lines_removed }}</span>
                </td>
                <td class="px-4 py-3 text-right text-gray-300">
                  {{ story.review_cycles }}
                </td>
                <td class="px-4 py-3 text-right text-gray-300">
                  {{ story.bugs_found }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
