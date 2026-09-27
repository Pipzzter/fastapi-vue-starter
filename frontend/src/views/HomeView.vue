<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, type HealthStatus } from '@/services/api'

const health = ref<HealthStatus | null>(null)
const error = ref<string | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    health.value = await api.health()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unknown error'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="home">
    <h1>FastAPI + Vue Starter</h1>
    <p>The frontend is wired to the backend API. Live health check:</p>

    <div v-if="loading" class="status">Checking backend…</div>
    <div v-else-if="error" class="status status--error">Backend unreachable: {{ error }}</div>
    <div v-else class="status status--ok">
      <strong>{{ health?.status }}</strong>
      <span>{{ health?.timestamp }}</span>
    </div>
  </section>
</template>

<style scoped>
.home {
  max-width: 40rem;
  margin: 4rem auto;
  padding: 0 1rem;
  font-family: system-ui, sans-serif;
}
.status {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background: #f4f4f5;
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
.status--ok {
  background: #ecfdf5;
  color: #065f46;
}
.status--error {
  background: #fef2f2;
  color: #991b1b;
}
</style>
