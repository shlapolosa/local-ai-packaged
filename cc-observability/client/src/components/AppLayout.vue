<script setup lang="ts">
import { useWebSocket } from '../composables/useWebSocket';

const { connectionStatus } = useWebSocket();
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-900">
    <!-- Top Navbar -->
    <header class="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between z-20 sticky top-0">
      <div class="flex items-center gap-6">
        <router-link to="/" class="flex items-center gap-2 text-white hover:text-brand-400 transition-colors">
          <svg class="w-6 h-6 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span class="text-lg font-semibold tracking-tight">CC Observability</span>
        </router-link>

        <nav class="hidden md:flex items-center gap-1">
          <router-link
            to="/"
            class="px-3 py-1.5 text-sm rounded-md transition-colors"
            :class="$route.path === '/' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700/50'"
          >
            Projects
          </router-link>
          <router-link
            to="/traces"
            class="px-3 py-1.5 text-sm rounded-md transition-colors"
            :class="$route.path === '/traces' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700/50'"
          >
            Traces
          </router-link>
          <router-link
            to="/dashboard"
            class="px-3 py-1.5 text-sm rounded-md transition-colors"
            :class="$route.path === '/dashboard' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700/50'"
          >
            Dashboard
          </router-link>
        </nav>
      </div>

      <div class="flex items-center gap-3">
        <!-- Connection indicator -->
        <div class="flex items-center gap-1.5 text-xs">
          <span
            class="w-2 h-2 rounded-full"
            :class="{
              'bg-emerald-400': connectionStatus === 'connected',
              'bg-yellow-400 animate-pulse': connectionStatus === 'connecting',
              'bg-red-400': connectionStatus === 'disconnected',
            }"
          ></span>
          <span class="text-gray-400 hidden sm:inline">
            {{ connectionStatus === 'connected' ? 'Live' : connectionStatus === 'connecting' ? 'Connecting...' : 'Offline' }}
          </span>
        </div>

      </div>
    </header>

    <!-- Main content area -->
    <main class="flex-1 overflow-y-auto p-4 lg:p-6">
      <router-view />
    </main>
  </div>
</template>
