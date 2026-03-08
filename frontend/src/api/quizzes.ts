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
    quizUuid: string,
    payload: CreateQuizQuestionPayload,
  ): Promise<CreateQuizQuestionResponse> {
    const response = await api.post<CreateQuizQuestionResponse>(
      `/quizzes/${quizUuid}/questions`,
      payload,
    )

    return response.data
  },

  async updateQuizQuestion(
    quizUuid: string,
    uuid: string,
    payload: UpdateQuizQuestionPayload,
  ): Promise<void> {
    await api.patch(`/quizzes/${quizUuid}/questions/${uuid}`, payload)
  },

  async deleteQuizQuestion(quizUuid: string, uuid: string): Promise<void> {
    await api.delete(`/quizzes/${quizUuid}/questions/${uuid}`)
  },

  async createQuizQuestionOption(
    quizUuid: string,
    quizQuestionUuid: string,
    payload: CreateQuizQuestionOptionPayload,
  ): Promise<CreateQuizQuestionOptionResponse> {
    const response = await api.post<CreateQuizQuestionOptionResponse>(
      `/quizzes/${quizUuid}/questions/${quizQuestionUuid}/options`,
      payload,
    )

    return response.data
  },

  async updateQuizQuestionOption(
    quizUuid: string,
    quizQuestionUuid: string,
    uuid: string,
    payload: UpdateQuizQuestionOptionPayload,
  ): Promise<void> {
    await api.patch(`/quizzes/${quizUuid}/questions/${quizQuestionUuid}/options/${uuid}`, payload)
  },

  async deleteQuizQuestionOption(
    quizUuid: string,
    quizQuestionUuid: string,
    uuid: string,
  ): Promise<void> {
    await api.delete(`/quizzes/${quizUuid}/questions/${quizQuestionUuid}/options/${uuid}`)
  },
}
