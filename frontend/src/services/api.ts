// Minimal typed API client. Set VITE_API_URL to call the backend directly
// (CORS-enabled); leave it empty to use the Vite dev-server proxy (/api).
const API_BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

export interface HealthStatus {
  status: string
  timestamp: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`)
  }
  return (await response.json()) as T
}

export const api = {
  health: () => request<HealthStatus>('/api/v1/health/'),
}
