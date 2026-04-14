import axios, { type AxiosError, type AxiosRequestConfig } from 'axios'

const service = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

service.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ message?: string }>) => {
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

export default http
