<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    data: number[];
    color?: string;
    width?: number;
    height?: number;
    strokeWidth?: number;
    fill?: boolean;
  }>(),
  {
    color: '#818cf8',
    width: 120,
    height: 32,
    strokeWidth: 1.5,
    fill: true,
  }
);

const points = computed(() => {
  if (!props.data || props.data.length === 0) return '';

  const values = props.data;
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;
  const padding = 2;
  const usableWidth = props.width - padding * 2;
  const usableHeight = props.height - padding * 2;
  const step = usableWidth / Math.max(values.length - 1, 1);

  return values
    .map((v, i) => {
      const x = padding + i * step;
      const y = padding + usableHeight - ((v - min) / range) * usableHeight;
      return `${x},${y}`;
    })
    .join(' ');
});

const fillPoints = computed(() => {
  if (!props.data || props.data.length === 0 || !points.value) return '';

  const padding = 2;
  const usableWidth = props.width - padding * 2;
  const step = usableWidth / Math.max(props.data.length - 1, 1);
  const lastX = padding + (props.data.length - 1) * step;
  const firstX = padding;

  return `${firstX},${props.height} ${points.value} ${lastX},${props.height}`;
});

const hasData = computed(() => props.data && props.data.length > 1);
</script>

<template>
  <svg
    v-if="hasData"
    :width="width"
    :height="height"
    :viewBox="`0 0 ${width} ${height}`"
    class="inline-block"
  >
    <polygon
      v-if="fill"
      :points="fillPoints"
      :fill="color"
      fill-opacity="0.1"
    />
    <polyline
      :points="points"
      fill="none"
      :stroke="color"
      :stroke-width="strokeWidth"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
  <span v-else class="text-xs text-gray-600">--</span>
</template>
