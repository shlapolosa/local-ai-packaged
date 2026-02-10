import { onMounted, onUnmounted } from 'vue';
import { useEventStore } from '../stores/events';

export function useWebSocket() {
  const store = useEventStore();

  onMounted(() => {
    store.connect();
  });

  onUnmounted(() => {
    // Don't disconnect on unmount since the store is shared.
    // Only disconnect if no components need it.
    // The store handles reconnection internally.
  });

  return {
    recentEvents: store.recentEvents,
    latestEvents: store.latestEvents,
    connectionStatus: store.connectionStatus,
    isConnected: store.isConnected,
    connect: store.connect,
    disconnect: store.disconnect,
  };
}
