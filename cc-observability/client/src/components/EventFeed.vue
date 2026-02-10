<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue';
import { useEventStore } from '../stores/events';
import { relativeTime } from '../composables/useRelativeTime';

const props = withDefaults(
  defineProps<{
    compact?: boolean;
    maxItems?: number;
    storyId?: string;
    projectId?: string;
  }>(),
  {
    compact: false,
    maxItems: 50,
  }
);

const store = useEventStore();
const feedContainer = ref<HTMLElement | null>(null);

const filteredEvents = computed(() => {
  let events = store.recentEvents;
  if (props.storyId) {
    events = events.filter((e) => e.story_id === props.storyId);
  }
  if (props.projectId) {
    events = events.filter((e) => e.project_id === props.projectId);
  }
  return events.slice(0, props.maxItems);
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

// Auto-scroll when new events arrive
watch(
  () => filteredEvents.value.length,
  async () => {
    if (feedContainer.value) {
      await nextTick();
      feedContainer.value.scrollTop = 0;
    }
  }
);
</script>

<template>
  <div ref="feedContainer" class="space-y-2" :class="{ 'max-h-96 overflow-y-auto': !compact }">
    <div
      v-if="filteredEvents.length === 0"
      class="text-center py-8 text-gray-500 text-sm"
    >
      No events yet. Waiting for activity...
    </div>

    <div
      v-for="event in filteredEvents"
      :key="event.id"
      class="flex flex-col gap-1 p-2 rounded-md bg-gray-800/60 border border-gray-700/40 text-sm"
      :class="{ 'p-1.5': compact }"
    >
      <div class="flex items-center justify-between gap-2">
        <span :class="eventBadgeClass(event.hook_event_type)" class="truncate">
          {{ shortEventType(event.hook_event_type) }}
        </span>
        <span class="text-xs text-gray-500 whitespace-nowrap">
          {{ relativeTime(event.timestamp) }}
        </span>
      </div>

      <div v-if="!compact" class="flex items-center gap-2 text-xs text-gray-400">
        <span v-if="event.tool_name" class="text-gray-300">{{ event.tool_name }}</span>
        <span v-if="event.project_id" class="truncate">{{ event.project_id }}</span>
      </div>

      <div v-if="compact" class="text-xs text-gray-500 truncate">
        <span v-if="event.tool_name">{{ event.tool_name }}</span>
        <span v-else-if="event.summary">{{ event.summary }}</span>
        <span v-else>{{ event.project_id }}</span>
      </div>
    </div>
  </div>
</template>
