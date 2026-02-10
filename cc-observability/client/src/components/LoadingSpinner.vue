<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: 'sm' | 'md' | 'lg';
    text?: string;
  }>(),
  {
    size: 'md',
    text: 'Loading...',
  }
);
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 gap-3">
    <svg
      class="animate-spin text-brand-400"
      :class="{
        'w-5 h-5': size === 'sm',
        'w-8 h-8': size === 'md',
        'w-12 h-12': size === 'lg',
      }"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
    <span v-if="text" class="text-sm text-gray-400">{{ text }}</span>
  </div>
</template>
