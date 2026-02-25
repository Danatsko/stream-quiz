import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { CreateQuizPayload, SummaryQuiz } from '@/types/quizzes'
import { AxiosError } from 'axios'
import { quizzesAPI } from '@/api/quizzes'

export const useQuizzesStore = defineStore('quizzes', () => {
  const quizzes = ref<Array<SummaryQuiz>>([])
  const total_quizzes = ref<number | null>(null)
  const page = ref<number | null>(null)
  const size = 10
  const total_pages = ref<number | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const resetError = (): void => {
    error.value = null
  }

  const clearQuizzes = (): void => {
    quizzes.value = []
    total_quizzes.value = null
    page.value = null
    total_pages.value = null
    resetError()
  }

  const createQuiz = async (payload: CreateQuizPayload): Promise<string> => {
    isLoading.value = true
    resetError()

    try {
      const response = await quizzesAPI.createQuiz(payload)

      return response.uuid
    } catch (createQuizError) {
      if (createQuizError instanceof AxiosError) {
        error.value = createQuizError.response?.data?.detail || 'Error during create quiz'
      }

      throw createQuizError
    } finally {
      isLoading.value = false
    }
  }

  const getQuizzes = async (): Promise<void> => {
    if (page.value !== null && total_pages.value !== null && page.value >= total_pages.value) {
      return
    }

    isLoading.value = true
    resetError()

    try {
      const nextPage = page.value === null ? 1 : page.value + 1
      const response = await quizzesAPI.getQuizzes(nextPage, size)
      quizzes.value.push(...response.quizzes)
      total_quizzes.value = response.total_quizzes
      page.value = response.page
      total_pages.value = response.total_pages
    } catch (getQuizzesError) {
      if (getQuizzesError instanceof AxiosError) {
        error.value = getQuizzesError.response?.data?.detail || 'Error during get quizzes'
      }

      throw getQuizzesError
    } finally {
      isLoading.value = false
    }
  }

  const deleteQuiz = async (uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await quizzesAPI.deleteQuiz(uuid)

      quizzes.value = quizzes.value.filter((q) => q.uuid !== uuid)
    } catch (deleteQuizError) {
      if (deleteQuizError instanceof AxiosError) {
        error.value = deleteQuizError.response?.data?.detail || 'Error during create quiz'
      }

      throw deleteQuizError
    } finally {
      isLoading.value = false
    }
  }

  return {
    quizzes,
    total_quizzes,
    page,
    size,
    total_pages,
    isLoading,
    error,
    clearQuizzes,
    createQuiz,
    getQuizzes,
    deleteQuiz,
  }
})

export default useQuizzesStore
