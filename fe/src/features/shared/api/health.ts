import http from './client'

export interface HealthResponse {
  message: string
}

export function getHealth() {
  return http.get<HealthResponse>('/health')
}
