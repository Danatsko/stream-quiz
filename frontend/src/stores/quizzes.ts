import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  CreateQuizPayload,
  CreateQuizQuestionOptionPayload,
  CreateQuizQuestionPayload,
  DetailedQuiz,
  GetQuizResponse,
  SummaryQuiz,
  UpdateQuizPayload,
  UpdateQuizQuestionOptionPayload,
  UpdateQuizQuestionPayload,
} from '@/types/quizzes'
import { AxiosError } from 'axios'
import { quizzesAPI } from '@/api/quizzes'

export const useQuizzesStore = defineStore('quizzes', () => {
  const quizzes = ref<Array<SummaryQuiz>>([])
  const quiz = ref<DetailedQuiz | null>(null)
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

  const createQuizQuestion = async (
    quiz_uuid: string,
    payload: CreateQuizQuestionPayload,
  ): Promise<string> => {
    isLoading.value = true
    resetError()

    try {
      const response = await quizzesAPI.createQuizQuestion(quiz_uuid, payload)

      return response.uuid
    } catch (createQuizQuestionError) {
      if (createQuizQuestionError instanceof AxiosError) {
        error.value =
          createQuizQuestionError.response?.data?.detail || 'Error during create quiz question'
      }

      throw createQuizQuestionError
    } finally {
      isLoading.value = false
    }
  }

  const updateQuizQuestion = async (
    quiz_uuid: string,
    uuid: string,
    payload: UpdateQuizQuestionPayload,
  ): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await quizzesAPI.updateQuizQuestion(quiz_uuid, uuid, payload)
    } catch (updateQuizQuestionError) {
      if (updateQuizQuestionError instanceof AxiosError) {
        error.value =
          updateQuizQuestionError.response?.data?.detail || 'Error during update quiz question'
      }

      throw updateQuizQuestionError
    } finally {
      isLoading.value = false
    }
  }

  const deleteQuizQuestion = async (quiz_uuid: string, uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await quizzesAPI.deleteQuizQuestion(quiz_uuid, uuid)
    } catch (deleteQuizQuestionError) {
      if (deleteQuizQuestionError instanceof AxiosError) {
        error.value =
          deleteQuizQuestionError.response?.data?.detail || 'Error during delete quiz question'
      }

      throw deleteQuizQuestionError
    } finally {
      isLoading.value = false
    }
  }

  const createQuizQuestionOption = async (
    quiz_uuid: string,
    quiz_question_uuid: string,
    payload: CreateQuizQuestionOptionPayload,
  ): Promise<string> => {
    isLoading.value = true
    resetError()

    try {
      const response = await quizzesAPI.createQuizQuestionOption(
        quiz_uuid,
        quiz_question_uuid,
        payload,
      )

      return response.uuid
    } catch (createQuizQuestionOptionError) {
      if (createQuizQuestionOptionError instanceof AxiosError) {
        error.value =
          createQuizQuestionOptionError.response?.data?.detail ||
          'Error during create quiz question option'
      }

      throw createQuizQuestionOptionError
    } finally {
      isLoading.value = false
    }
  }

  const updateQuizQuestionOption = async (
    quiz_uuid: string,
    quiz_question_uuid: string,
    uuid: string,
    payload: UpdateQuizQuestionOptionPayload,
  ): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await quizzesAPI.updateQuizQuestionOption(quiz_uuid, quiz_question_uuid, uuid, payload)
    } catch (updateQuizQuestionOptionError) {
      if (updateQuizQuestionOptionError instanceof AxiosError) {
        error.value =
          updateQuizQuestionOptionError.response?.data?.detail ||
          'Error during update quiz question option'
      }

      throw updateQuizQuestionOptionError
    } finally {
      isLoading.value = false
    }
  }

  const deleteQuizQuestionOption = async (
    quiz_uuid: string,
    quiz_question_uuid: string,
    uuid: string,
  ): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await quizzesAPI.deleteQuizQuestionOption(quiz_uuid, quiz_question_uuid, uuid)
    } catch (deleteQuizQuestionOptionError) {
      if (deleteQuizQuestionOptionError instanceof AxiosError) {
        error.value =
          deleteQuizQuestionOptionError.response?.data?.detail ||
          'Error during delete quiz question option'
      }

      throw deleteQuizQuestionOptionError
    } finally {
      isLoading.value = false
    }
  }

  return {
    quizzes,
    quiz,
    total_quizzes,
    page,
    size,
    total_pages,
    isLoading,
    error,
    clearQuizzes,
    clearQuiz,
    createQuiz,
    getQuizzes,
    getQuiz,
    updateQuiz,
    deleteQuiz,
    createQuizQuestion,
    updateQuizQuestion,
    deleteQuizQuestion,
    createQuizQuestionOption,
    updateQuizQuestionOption,
    deleteQuizQuestionOption,
  }
})

export default useQuizzesStore
