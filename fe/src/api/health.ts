import http from '../utils/request'

export interface HealthResponse {
  message: string
}

export function getHealth() {
  return http.get<HealthResponse>('/health')
}
