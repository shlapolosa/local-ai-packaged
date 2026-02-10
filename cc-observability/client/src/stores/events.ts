import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Event } from '../types';

const MAX_EVENTS = 100;

export const useEventStore = defineStore('events', () => {
  const recentEvents = ref<Event[]>([]);
  const connectionStatus = ref<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const ws = ref<WebSocket | null>(null);
  const reconnectTimer = ref<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = ref(0);
  const maxReconnectAttempts = 10;
  const baseReconnectDelay = 1000;

  const latestEvents = computed(() => recentEvents.value.slice(0, 10));
  const isConnected = computed(() => connectionStatus.value === 'connected');

  function addEvent(event: Event) {
    recentEvents.value.unshift(event);
    if (recentEvents.value.length > MAX_EVENTS) {
      recentEvents.value = recentEvents.value.slice(0, MAX_EVENTS);
    }
  }

  function connect() {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      return;
    }

    connectionStatus.value = 'connecting';

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const socket = new WebSocket(`${protocol}//${host}/ws`);

    socket.onopen = () => {
      connectionStatus.value = 'connected';
      reconnectAttempts.value = 0;
    };

    socket.onmessage = (messageEvent: MessageEvent) => {
      try {
        const data = JSON.parse(messageEvent.data);
        if (data && data.id && data.hook_event_type) {
          addEvent(data as Event);
        }
      } catch {
        // Ignore non-JSON messages
      }
    };

    socket.onclose = () => {
      connectionStatus.value = 'disconnected';
      ws.value = null;
      scheduleReconnect();
    };

    socket.onerror = () => {
      connectionStatus.value = 'disconnected';
      socket.close();
    };

    ws.value = socket;
  }

  function disconnect() {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value);
      reconnectTimer.value = null;
    }
    reconnectAttempts.value = maxReconnectAttempts;
    if (ws.value) {
      ws.value.close();
      ws.value = null;
    }
    connectionStatus.value = 'disconnected';
  }

  function scheduleReconnect() {
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      return;
    }
    const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts.value);
    reconnectAttempts.value++;
    reconnectTimer.value = setTimeout(() => {
      connect();
    }, Math.min(delay, 30000));
  }

  function clearEvents() {
    recentEvents.value = [];
  }

  return {
    recentEvents,
    connectionStatus,
    latestEvents,
    isConnected,
    addEvent,
    connect,
    disconnect,
    clearEvents,
  };
});
