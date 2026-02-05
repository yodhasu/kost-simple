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
export function setupAxiosInterceptors(userStore: any) {
  httpClient.interceptors.request.use((config) => {
    if (userStore.regionId) {
      config.params = { 
        ...config.params, 
        region_id: userStore.regionId 
      }
    }
    return config
  })
}

// Response interceptor
httpClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default httpClient

