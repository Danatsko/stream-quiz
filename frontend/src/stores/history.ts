import { defineStore } from 'pinia'
import { ref } from 'vue'
import { AxiosError } from 'axios'
import type { DetailedSession, SummarySession } from '@/types/history.ts'
import { historyAPI } from '@/api/history.ts'

export const useHistoryStore = defineStore('history', () => {
  const sessions = ref<Array<SummarySession>>([])
  const session = ref<DetailedSession | null>(null)
  const totalSessions = ref<number | null>(null)
  const page = ref<number | null>(null)
  const size = 10
  const totalPages = ref<number | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const resetError = (): void => {
    error.value = null
  }

  const clearSessions = (): void => {
    sessions.value = []
    totalSessions.value = null
    page.value = null
    totalPages.value = null
    resetError()
  }

  const clearSession = (): void => {
    session.value = null
    resetError()
  }

  const getSessions = async (): Promise<void> => {
    if (page.value !== null && totalPages.value !== null && page.value >= totalPages.value) {
      return
    }

    isLoading.value = true
    resetError()

    try {
      const nextPage = page.value === null ? 1 : page.value + 1
      const response = await historyAPI.getMeSessions(nextPage, size)
      sessions.value.push(...response.sessions)
      totalSessions.value = response.total_sessions
      page.value = response.page
      totalPages.value = response.total_pages
    } catch (getMeSessionsError) {
      if (getMeSessionsError instanceof AxiosError) {
        error.value = getMeSessionsError.response?.data?.detail || 'Error during get me sessions'
      }

      throw getMeSessionsError
    } finally {
      isLoading.value = false
    }
  }

  const getSession = async (uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      session.value = await historyAPI.getMeSession(uuid)
    } catch (getMeSessionError) {
      if (getMeSessionError instanceof AxiosError) {
        error.value = getMeSessionError.response?.data?.detail || 'Error during get me session'
      }

      throw getMeSessionError
    } finally {
      isLoading.value = false
    }
  }

  return {
    sessions,
    session,
    totalSessions,
    page,
    size,
    totalPages,
    isLoading,
    error,
    clearSessions,
    clearSession,
    getSessions,
    getSession,
  }
})

export default useHistoryStore
