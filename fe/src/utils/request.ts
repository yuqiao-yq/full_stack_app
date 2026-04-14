import axios, { type AxiosError, type AxiosRequestConfig } from 'axios'
import { clearToken, getToken } from './auth'
import { buildLoginRedirectPath } from './navigation'

const service = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

service.interceptors.request.use((config) => {
  const token = getToken()

  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

service.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ message?: string }>) => {
    if (error.response?.status === 401) {
      clearToken()
      window.location.replace(buildLoginRedirectPath())
    }

    const message =
      error.response?.data?.message ?? error.message ?? 'Request failed'

    return Promise.reject(new Error(message))
  },
)

const http = {
  get<T>(url: string, config?: AxiosRequestConfig) {
    return service.get<T>(url, config).then((response) => response.data)
  },
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return service.post<T>(url, data, config).then((response) => response.data)
  },
  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return service.put<T>(url, data, config).then((response) => response.data)
  },
  delete<T>(url: string, config?: AxiosRequestConfig) {
    return service.delete<T>(url, config).then((response) => response.data)
  },
}

export { service }
export default http
