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

// Request interceptor - Add Firebase ID token and Region ID
httpClient.interceptors.request.use(
  async (requestConfig: InternalAxiosRequestConfig) => {
    const user = auth.currentUser
    if (user && requestConfig.headers) {
      const token = await user.getIdToken()
      requestConfig.headers.Authorization = `Bearer ${token}`
    }

    // Add region_id to params if available
    // We import the store dynamically to avoid initialization issues
    try {
      const { useUserStore } = await import('../../stores/userStore')
      const userStore = useUserStore()
      if (userStore.regionId) {
        requestConfig.params = { 
          ...requestConfig.params, 
          region_id: userStore.regionId 
        }
      }
    } catch (e) {
      // Store might not be ready or authorized yet, ignore
    }

    return requestConfig
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

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

