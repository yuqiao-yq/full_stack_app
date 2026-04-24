import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  getCurrentUser,
  login as loginApi,
  register as registerApi,
  type AuthUser,
  type LoginPayload,
  type LoginResponse,
  type RegisterPayload,
} from '../api/auth'
import { clearToken, getToken, setToken } from '../lib/tokenStorage'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getToken())
  const user = ref<AuthUser | null>(null)
  const isAuthenticated = computed(() => Boolean(token.value))

  function applyAuthSession(data: LoginResponse) {
    token.value = data.token
    user.value = data.user
    setToken(data.token)
    return data.user
  }

  async function login(payload: LoginPayload) {
    const data = await loginApi(payload)
    return applyAuthSession(data)
  }

  async function register(payload: RegisterPayload) {
    const data = await registerApi(payload)
    return applyAuthSession(data)
  }

  async function fetchMe() {
    if (!token.value) {
      return null
    }

    const data = await getCurrentUser()
    user.value = data.user
    return data.user
  }

  function logout() {
    token.value = ''
    user.value = null
    clearToken()
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    fetchMe,
    logout,
  }
})
