import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  CreateQuizPayload,
  DetailedQuiz,
  FullUpdateQuizPayload,
  SummaryQuiz,
  UpdateQuizPayload,
} from '@/types/quizzes'
import { AxiosError } from 'axios'
import { quizzesAPI } from '@/api/quizzes'

export const useQuizzesStore = defineStore('quizzes', () => {
  const quizzes = ref<Array<SummaryQuiz>>([])
  const quiz = ref<DetailedQuiz | null>(null)
  const totalQuizzes = ref<number | null>(null)
  const page = ref<number | null>(null)
  const size = 10
  const totalPages = ref<number | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const resetError = (): void => {
    error.value = null
  }

  const clearQuizzes = (): void => {
    quizzes.value = []
    totalQuizzes.value = null
    page.value = null
    totalPages.value = null
    resetError()
  }

  const clearQuiz = (): void => {
    quiz.value = null
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
    if (page.value !== null && totalPages.value !== null && page.value >= totalPages.value) {
      return
    }

    isLoading.value = true
    resetError()

    try {
      const nextPage = page.value === null ? 1 : page.value + 1
      const response = await quizzesAPI.getQuizzes(nextPage, size)
      quizzes.value.push(...response.quizzes)
      totalQuizzes.value = response.total_quizzes
      page.value = response.page
      totalPages.value = response.total_pages
    } catch (getQuizzesError) {
      if (getQuizzesError instanceof AxiosError) {
        error.value = getQuizzesError.response?.data?.detail || 'Error during get quizzes'
      }

      throw getQuizzesError
    } finally {
      isLoading.value = false
    }
  }

  const getQuiz = async (uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      quiz.value = await quizzesAPI.getQuiz(uuid)
    } catch (getQuizError) {
      if (getQuizError instanceof AxiosError) {
        error.value = getQuizError.response?.data?.detail || 'Error during get quiz'
      }

      throw getQuizError
    } finally {
      isLoading.value = false
    }
  }

  const updateQuiz = async (uuid: string, payload: UpdateQuizPayload): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await quizzesAPI.updateQuiz(uuid, payload)
    } catch (updateQuizError) {
      if (updateQuizError instanceof AxiosError) {
        error.value = updateQuizError.response?.data?.detail || 'Error during update quiz'
      }

      throw updateQuizError
    } finally {
      isLoading.value = false
    }
  }

  const fullUpdateQuiz = async (uuid: string, payload: FullUpdateQuizPayload): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await quizzesAPI.fullUpdateQuiz(uuid, payload)
    } catch (fullUpdateQuizError) {
      if (fullUpdateQuizError instanceof AxiosError) {
        error.value = fullUpdateQuizError.response?.data?.detail || 'Error during full update quiz'
      }

      throw fullUpdateQuizError
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

      if (quiz.value?.uuid === uuid) {
        quiz.value = null
      }
    } catch (deleteQuizError) {
      if (deleteQuizError instanceof AxiosError) {
        error.value = deleteQuizError.response?.data?.detail || 'Error during delete quiz'
      }

      throw deleteQuizError
    } finally {
      isLoading.value = false
    }
  }

  return {
    quizzes,
    quiz,
    totalQuizzes,
    page,
    size,
    totalPages,
    isLoading,
    error,
    clearQuizzes,
    clearQuiz,
    createQuiz,
    getQuizzes,
    getQuiz,
    updateQuiz,
    fullUpdateQuiz,
    deleteQuiz,
  }
})

export default useQuizzesStore
