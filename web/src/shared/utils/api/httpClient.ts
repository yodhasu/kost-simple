import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { config } from '../../../config'
import { auth } from '../../../lib/firebase'

const httpClient: AxiosInstance = axios.create({
  baseURL: config.api.baseUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add Firebase ID token
httpClient.interceptors.request.use(
  async (requestConfig: InternalAxiosRequestConfig) => {
    const user = auth.currentUser
    if (user && requestConfig.headers) {
      const token = await user.getIdToken()
      requestConfig.headers.Authorization = `Bearer ${token}`
    }
    return requestConfig
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

/**
 * Setup interceptors that depend on the User Store.
 * Call this from main.ts after store initialization.
 */
export function setupAxiosInterceptors(_userStore: any) {
  // No-op: region scoping is handled per-feature to avoid global/local conflicts.
}

// Response interceptor
httpClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      const path = window.location.pathname
      if (path === '/login' || path === '/unauthorized') {
        return Promise.reject(error)
      }
      // If user already logged out, go to login instead of unauthorized
      if (!auth.currentUser) {
        window.location.href = '/login'
        return Promise.reject(error)
      }
      // Token expired or invalid. Show guardrail page (user can go to login).
      const redirect = encodeURIComponent(`${window.location.pathname}${window.location.search}`)
      window.location.href = `/unauthorized?redirect=${redirect}`
    } else if (error.response?.status === 403) {
      window.location.href = '/forbidden'
    }
    return Promise.reject(error)
  }
)

export default httpClient

