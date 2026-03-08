import api from '@/services/api'
import type {
  CreateQuizPayload,
  CreateQuizQuestionOptionPayload,
  CreateQuizQuestionOptionResponse,
  CreateQuizQuestionPayload,
  CreateQuizQuestionResponse,
  CreateQuizResponse,
  GetQuizResponse,
  GetQuizzesResponse,
  UpdateQuizPayload,
  UpdateQuizQuestionOptionPayload,
  UpdateQuizQuestionPayload,
} from '@/types/quizzes'

export const quizzesAPI = {
  async createQuiz(payload: CreateQuizPayload): Promise<CreateQuizResponse> {
    const response = await api.post<CreateQuizResponse>('/quizzes', payload)

    return response.data
  },

  async getQuizzes(page: number, size: number): Promise<GetQuizzesResponse> {
    const response = await api.get<GetQuizzesResponse>('/quizzes', {
      params: {
        page: page,
        size: size,
      },
    })

    return response.data
  },

  async getQuiz(uuid: string): Promise<GetQuizResponse> {
    const response = await api.get<GetQuizResponse>(`/quizzes/${uuid}`)

    return response.data
  },

  async updateQuiz(uuid: string, payload: UpdateQuizPayload): Promise<void> {
    await api.patch(`/quizzes/${uuid}`, payload)
  },

  async deleteQuiz(uuid: string): Promise<void> {
    await api.delete(`/quizzes/${uuid}`)
  },

  async createQuizQuestion(
    quiz_uuid: string,
    payload: CreateQuizQuestionPayload,
  ): Promise<CreateQuizQuestionResponse> {
    const response = await api.post<CreateQuizQuestionResponse>(
      `/quizzes/${quiz_uuid}/questions`,
      payload,
    )

    return response.data
  },

  async updateQuizQuestion(
    quiz_uuid: string,
    uuid: string,
    payload: UpdateQuizQuestionPayload,
  ): Promise<void> {
    await api.patch(`/quizzes/${quiz_uuid}/questions/${uuid}`, payload)
  },

  async deleteQuizQuestion(quiz_uuid: string, uuid: string): Promise<void> {
    await api.delete(`/quizzes/${quiz_uuid}/questions/${uuid}`)
  },

  async createQuizQuestionOption(
    quiz_uuid: string,
    quiz_question_uuid: string,
    payload: CreateQuizQuestionOptionPayload,
  ): Promise<CreateQuizQuestionOptionResponse> {
    const response = await api.post<CreateQuizQuestionOptionResponse>(
      `/quizzes/${quiz_uuid}/questions/${quiz_question_uuid}/options`,
      payload,
    )

    return response.data
  },

  async updateQuizQuestionOption(
    quiz_uuid: string,
    quiz_question_uuid: string,
    uuid: string,
    payload: UpdateQuizQuestionOptionPayload,
  ): Promise<void> {
    await api.patch(
      `/quizzes/${quiz_uuid}/questions/${quiz_question_uuid}/options/${uuid}`,
      payload,
    )
  },

  async deleteQuizQuestionOption(
    quiz_uuid: string,
    quiz_question_uuid: string,
    uuid: string,
  ): Promise<void> {
    await api.delete(`/quizzes/${quiz_uuid}/questions/${quiz_question_uuid}/options/${uuid}`)
  },
}
