<script setup lang="ts">
defineProps<{
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
}>();
</script>

<template>
  <div class="card flex flex-col gap-1">
    <span class="text-xs font-medium text-gray-400 uppercase tracking-wider">{{ title }}</span>
    <div class="flex items-baseline gap-2">
      <span class="text-2xl font-bold text-white">{{ value }}</span>
      <span
        v-if="trend && trend !== 'neutral'"
        class="text-xs font-medium flex items-center gap-0.5"
        :class="trend === 'up' ? 'text-emerald-400' : 'text-red-400'"
      >
        <svg v-if="trend === 'up'" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
        </svg>
        <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </span>
    </div>
    <span v-if="subtitle" class="text-xs text-gray-500">{{ subtitle }}</span>
  </div>
</template>
