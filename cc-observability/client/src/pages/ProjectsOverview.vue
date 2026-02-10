<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { Project, DashboardKPIs } from '../types';
import { fetchProjects, fetchDashboardKPIs } from '../composables/useApi';
import { relativeTime } from '../composables/useRelativeTime';
import KpiCard from '../components/KpiCard.vue';
import SparkLine from '../components/SparkLine.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const router = useRouter();

const projects = ref<Project[]>([]);
const kpis = ref<DashboardKPIs | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

async function loadData() {
  loading.value = true;
  error.value = null;
  try {
    const [projectData, kpiData] = await Promise.all([
      fetchProjects(),
      fetchDashboardKPIs(),
    ]);
    projects.value = projectData;
    kpis.value = kpiData;
  } catch (err: any) {
    error.value = err.message || 'Failed to load data';
  } finally {
    loading.value = false;
  }
}

function navigateToProject(projectId: string) {
  router.push({ name: 'project-detail', params: { id: projectId } });
}

onMounted(loadData);
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div>
      <h1 class="text-2xl font-bold text-white">Projects</h1>
      <p class="text-sm text-gray-400 mt-1">Overview of all tracked Claude Code projects</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="card text-center py-12">
      <p class="text-red-400 mb-4">{{ error }}</p>
      <button @click="loadData" class="btn-primary">Retry</button>
    </div>

    <template v-else>
      <!-- Global KPI bar -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <KpiCard
          title="Total Projects"
          :value="kpis?.total_projects ?? 0"
          subtitle="Active repositories"
        />
        <KpiCard
          title="Total Contributors"
          :value="kpis?.total_contributors ?? 0"
          subtitle="Developers using Claude"
        />
        <KpiCard
          title="Total Stories"
          :value="kpis?.total_stories ?? 0"
          :subtitle="`${kpis?.stories_completed ?? 0} completed`"
        />
      </div>

      <!-- Empty state -->
      <div v-if="projects.length === 0" class="card text-center py-16">
        <svg class="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <h3 class="text-lg font-medium text-gray-300 mb-2">No projects yet</h3>
        <p class="text-sm text-gray-500">Projects will appear here once Claude Code hooks start sending data.</p>
      </div>

      <!-- Project cards grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="project in projects"
          :key="project.project_id"
          class="card-hover group"
          @click="navigateToProject(project.project_id)"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="min-w-0 flex-1">
              <h3 class="text-base font-semibold text-white truncate group-hover:text-brand-400 transition-colors">
                {{ project.display_name || project.project_id }}
              </h3>
              <p v-if="project.git_remote_url" class="text-xs text-gray-500 truncate mt-0.5">
                {{ project.git_remote_url }}
              </p>
            </div>
            <svg class="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>

          <div class="grid grid-cols-3 gap-3 text-center mb-3">
            <div>
              <div class="text-lg font-bold text-white">{{ project.contributor_count ?? '--' }}</div>
              <div class="text-xs text-gray-500">Contributors</div>
            </div>
            <div>
              <div class="text-lg font-bold text-white">{{ project.story_count ?? '--' }}</div>
              <div class="text-xs text-gray-500">Stories</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mt-1">{{ relativeTime(project.last_active_at) }}</div>
              <div class="text-xs text-gray-500">Last active</div>
            </div>
          </div>

          <div class="flex items-center justify-between border-t border-gray-700/50 pt-3">
            <span class="text-xs text-gray-500">7-day activity</span>
            <SparkLine
              :data="project.recent_activity || []"
              color="#818cf8"
              :width="100"
              :height="24"
            />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
