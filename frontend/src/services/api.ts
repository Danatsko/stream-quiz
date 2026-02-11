import axios from 'axios'
import router from '@/router'

const API_URL = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    if (!originalRequest) {
      return Promise.reject(error)
    }

    if (originalRequest.url?.includes('/auth/refresh')) {
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        await api.post('/auth/refresh')

        return api(originalRequest)
      } catch (refreshError) {
        const { useAuthStore } = await import('@/stores/auth')
        const authStore = useAuthStore()

        await authStore.logout(false)
        await router.push({ name: 'Home' })

        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export default api
