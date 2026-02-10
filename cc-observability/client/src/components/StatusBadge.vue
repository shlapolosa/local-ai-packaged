<script setup lang="ts">
import type { StoryStatus } from '../types';

defineProps<{
  status: StoryStatus | string;
}>();

function badgeClass(status: string): string {
  switch (status) {
    case 'in_progress':
      return 'badge-blue';
    case 'completed':
      return 'badge-green';
    case 'abandoned':
      return 'badge-red';
    case 'pending':
      return 'badge-yellow';
    default:
      return 'badge-blue';
  }
}

function label(status: string): string {
  return status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
</script>

<template>
  <span :class="badgeClass(status)">{{ label(status) }}</span>
</template>
