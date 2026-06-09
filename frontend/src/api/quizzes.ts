import api from '@/services/api'
import type {
  CreateQuizPayload,
  CreateQuizResponse,
  FullUpdateQuizPayload,
  GetQuizResponse,
  GetQuizzesResponse,
  UpdateQuizPayload,
} from '@/types/quizzes'

export const quizzesAPI = {
  async createQuiz(payload: CreateQuizPayload): Promise<CreateQuizResponse> {
    const response = await api.post<CreateQuizResponse>('/quizzes', payload)

    return response.data
  },

  async getQuizzes(
    page: number,
    size: number,
    ownership: string = 'all',
    q: string = '',
  ): Promise<GetQuizzesResponse> {
    const response = await api.get<GetQuizzesResponse>('/quizzes', {
      params: {
        page: page,
        size: size,
        ownership: ownership,
        q: q || undefined,
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

  async fullUpdateQuiz(uuid: string, payload: FullUpdateQuizPayload): Promise<void> {
    await api.put(`/quizzes/${uuid}`, payload)
  },

  async deleteQuiz(uuid: string): Promise<void> {
    await api.delete(`/quizzes/${uuid}`)
  },
}
