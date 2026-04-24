import http from '../../shared/api/client'

export interface AuthUser {
  id: number
  username: string
  name: string
  createdAt: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  displayName: string
  password: string
  confirmPassword: string
}

export interface LoginResponse {
  token: string
  user: AuthUser
}

export interface CurrentUserResponse {
  user: AuthUser
}

export function login(payload: LoginPayload) {
  return http.post<LoginResponse>('/auth/login', payload)
}

export function register(payload: RegisterPayload) {
  return http.post<LoginResponse>('/auth/register', payload)
}

export function getCurrentUser() {
  return http.get<CurrentUserResponse>('/auth/me')
}
