import api from '@/services/api'
import type {
  CreateQuizPayload,
  CreateQuizResponse,
  GetQuizResponse,
  GetQuizzesResponse,
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

  async deleteQuiz(uuid: string): Promise<void> {
    await api.delete(`/quizzes/${uuid}`)
  },
}
