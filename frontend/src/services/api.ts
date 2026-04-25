import axios from 'axios'
import router from '@/router'
import useNotificationsStore from '@/stores/notifications'

const API_URL: string = window.APP_CONFIG.API_URL

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

    let errorMessage = 'An unknown error occurred'
    const detail = error.response?.data?.detail

    if (detail) {
      if (Array.isArray(detail)) {
        const isUuidError = detail.some((err: any) => err.type === 'uuid_parsing')

        if (isUuidError) {
          errorMessage = 'Invalid identifier passed'
        } else {
          errorMessage = detail.map((err: any) => err.msg).join(', ')
        }
      } else if (typeof detail === 'string') {
        errorMessage = detail
      }
    }

    const notificationsStore = useNotificationsStore()

    notificationsStore.addNotification(errorMessage, 'error')

    return Promise.reject(error)
  },
)

export default api
