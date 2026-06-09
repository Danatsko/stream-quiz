import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AppNotification } from '@/types/notifications'

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<AppNotification[]>([])
  const MAX_NOTIFICATIONS = 5
  const NOTIFICATION_TIMEOUT_MS = 5000

  const addNotification = (message: string, type: AppNotification['type'] = 'error'): void => {
    const id = crypto.randomUUID()

    notifications.value.push({ id, message, type })

    if (notifications.value.length > MAX_NOTIFICATIONS) {
      notifications.value.shift()
    }

    setTimeout(() => {
      removeNotification(id)
    }, NOTIFICATION_TIMEOUT_MS)
  }

  const removeNotification = (id: string): void => {
    notifications.value = notifications.value.filter((n) => n.id !== id)
  }

  return {
    notifications,
    addNotification,
    removeNotification,
  }
})

export default useNotificationsStore
