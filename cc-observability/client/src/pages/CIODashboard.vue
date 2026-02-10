<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { DashboardKPIs, LeaderboardEntry, CostData, TrendData } from '../types';
import {
  fetchDashboardKPIs,
  fetchLeaderboard,
  fetchCosts,
  fetchTrends,
} from '../composables/useApi';
import { formatDuration, formatNumber, formatCost } from '../composables/useRelativeTime';
import KpiCard from '../components/KpiCard.vue';
import SparkLine from '../components/SparkLine.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const router = useRouter();

const kpis = ref<DashboardKPIs | null>(null);
const leaderboard = ref<LeaderboardEntry[]>([]);
const costs = ref<CostData[]>([]);
const trends = ref<TrendData[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

function trendValues(key: keyof TrendData): number[] {
  return trends.value.map((t) => {
    const val = t[key];
    return typeof val === 'number' ? val : 0;
  });
}

function reviewReturnRate(): string {
  if (!kpis.value || !kpis.value.avg_review_cycles) return '--';
  // Review return rate approximation: cycles > 1 indicates returns
  const rate = Math.max(0, (kpis.value.avg_review_cycles - 1) / kpis.value.avg_review_cycles) * 100;
  return `${rate.toFixed(0)}%`;
}

async function loadData() {
  loading.value = true;
  error.value = null;
  try {
    const [kpiData, leaderboardData, costData, trendData] = await Promise.all([
      fetchDashboardKPIs(),
      fetchLeaderboard(),
      fetchCosts('project'),
      fetchTrends('weekly'),
    ]);
    kpis.value = kpiData;
    leaderboard.value = leaderboardData;
    costs.value = costData;
    trends.value = trendData;
  } catch (err: any) {
    error.value = err.message || 'Failed to load dashboard';
  } finally {
    loading.value = false;
  }
}

function goToContributor(id: string) {
  router.push({ name: 'contributor-detail', params: { id } });
}

onMounted(loadData);
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div>
      <h1 class="text-2xl font-bold text-white">Executive Dashboard</h1>
      <p class="text-sm text-gray-400 mt-1">AI-assisted development metrics and insights</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="card text-center py-12">
      <p class="text-red-400 mb-4">{{ error }}</p>
      <button @click="loadData" class="btn-primary">Retry</button>
    </div>

    <template v-else>
      <!-- KPI Cards row -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard
          title="Avg Time/Story"
          :value="kpis?.avg_time_per_story != null ? formatDuration(kpis.avg_time_per_story) : '--'"
        />
        <KpiCard
          title="Avg Lines/Story"
          :value="kpis?.avg_lines_per_story != null ? formatNumber(kpis.avg_lines_per_story) : '--'"
        />
        <KpiCard
          title="Review Return Rate"
          :value="reviewReturnRate()"
        />
        <KpiCard
          title="Bugs/Story"
          :value="kpis?.avg_bugs_per_story != null ? kpis.avg_bugs_per_story.toFixed(1) : '--'"
        />
        <KpiCard
          title="Total Token Spend"
          :value="formatNumber((kpis?.total_input_tokens ?? 0) + (kpis?.total_output_tokens ?? 0))"
          :subtitle="formatCost(kpis?.estimated_total_cost)"
        />
        <KpiCard
          title="Stories Completed"
          :value="kpis?.stories_completed ?? 0"
          :subtitle="`of ${kpis?.total_stories ?? 0} total`"
        />
      </div>

      <!-- Trends sparklines -->
      <div v-if="trends.length > 1" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="card">
          <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Stories Completed (Weekly)</div>
          <SparkLine :data="trendValues('stories_completed')" color="#34d399" :width="280" :height="48" />
        </div>
        <div class="card">
          <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Total Tokens (Weekly)</div>
          <SparkLine :data="trendValues('total_tokens')" color="#818cf8" :width="280" :height="48" />
        </div>
        <div class="card">
          <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Estimated Cost (Weekly)</div>
          <SparkLine :data="trendValues('estimated_cost')" color="#f59e0b" :width="280" :height="48" />
        </div>
      </div>

      <!-- Two column layout: Leaderboard and Costs -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Contributor Leaderboard -->
        <div>
          <h2 class="text-lg font-semibold text-white mb-3">Contributor Leaderboard</h2>
          <div v-if="leaderboard.length === 0" class="card text-center py-8 text-gray-500 text-sm">
            No contributor data available yet.
          </div>
          <div v-else class="card overflow-x-auto p-0">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-700 text-gray-400 text-xs uppercase tracking-wider">
                  <th class="text-left px-4 py-3 font-medium w-10">#</th>
                  <th class="text-left px-4 py-3 font-medium">Contributor</th>
                  <th class="text-right px-4 py-3 font-medium">Stories</th>
                  <th class="text-right px-4 py-3 font-medium">Avg Reviews</th>
                  <th class="text-right px-4 py-3 font-medium">Efficiency</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(entry, idx) in leaderboard"
                  :key="entry.contributor_id"
                  class="table-row cursor-pointer"
                  @click="goToContributor(entry.contributor_id)"
                >
                  <td class="px-4 py-3">
                    <span
                      class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                      :class="{
                        'bg-yellow-500/20 text-yellow-400': idx === 0,
                        'bg-gray-400/20 text-gray-300': idx === 1,
                        'bg-orange-600/20 text-orange-400': idx === 2,
                        'bg-gray-700/30 text-gray-500': idx > 2,
                      }"
                    >
                      {{ idx + 1 }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-white font-medium">
                    {{ entry.display_name || entry.contributor_id }}
                  </td>
                  <td class="px-4 py-3 text-right text-gray-300">
                    {{ entry.stories_completed }}
                  </td>
                  <td class="px-4 py-3 text-right text-gray-300">
                    {{ entry.avg_quality.toFixed(1) }}
                  </td>
                  <td class="px-4 py-3 text-right">
                    <span
                      class="inline-flex items-center gap-1 font-medium"
                      :class="{
                        'text-emerald-400': entry.efficiency >= 70,
                        'text-yellow-400': entry.efficiency >= 40 && entry.efficiency < 70,
                        'text-red-400': entry.efficiency < 40,
                      }"
                    >
                      {{ entry.efficiency.toFixed(0) }}
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          v-if="entry.efficiency >= 70"
                          stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M5 15l7-7 7 7"
                        />
                        <path
                          v-else-if="entry.efficiency < 40"
                          stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M19 9l-7 7-7-7"
                        />
                        <path
                          v-else
                          stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M5 12h14"
                        />
                      </svg>
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Cost Breakdown -->
        <div>
          <h2 class="text-lg font-semibold text-white mb-3">Cost Breakdown by Project</h2>
          <div v-if="costs.length === 0" class="card text-center py-8 text-gray-500 text-sm">
            No cost data available yet.
          </div>
          <div v-else class="card overflow-x-auto p-0">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-700 text-gray-400 text-xs uppercase tracking-wider">
                  <th class="text-left px-4 py-3 font-medium">Project</th>
                  <th class="text-right px-4 py-3 font-medium">Input Tokens</th>
                  <th class="text-right px-4 py-3 font-medium">Output Tokens</th>
                  <th class="text-right px-4 py-3 font-medium">Est. Cost</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="cost in costs"
                  :key="cost.dimension_value"
                  class="table-row"
                >
                  <td class="px-4 py-3 text-white font-medium">
                    {{ cost.dimension_value }}
                  </td>
                  <td class="px-4 py-3 text-right text-gray-300">
                    {{ formatNumber(cost.total_input_tokens) }}
                  </td>
                  <td class="px-4 py-3 text-right text-gray-300">
                    {{ formatNumber(cost.total_output_tokens) }}
                  </td>
                  <td class="px-4 py-3 text-right text-emerald-400 font-medium">
                    {{ formatCost(cost.estimated_cost) }}
                  </td>
                </tr>

                <!-- Total row -->
                <tr class="border-t-2 border-gray-600 bg-gray-700/20">
                  <td class="px-4 py-3 text-white font-bold">Total</td>
                  <td class="px-4 py-3 text-right text-white font-bold">
                    {{ formatNumber(costs.reduce((s, c) => s + c.total_input_tokens, 0)) }}
                  </td>
                  <td class="px-4 py-3 text-right text-white font-bold">
                    {{ formatNumber(costs.reduce((s, c) => s + c.total_output_tokens, 0)) }}
                  </td>
                  <td class="px-4 py-3 text-right text-emerald-400 font-bold">
                    {{ formatCost(costs.reduce((s, c) => s + c.estimated_cost, 0)) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
