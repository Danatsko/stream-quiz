import api from '@/services/api'
import type { GetMeSessionResponse, GetMeSessionsResponse } from '@/types/history'

export const historyAPI = {
  async getMeSessions(page: number, size: number): Promise<GetMeSessionsResponse> {
    const response = await api.get<GetMeSessionsResponse>('users/me/sessions', {
      params: {
        page: page,
        size: size,
      },
    })

    return response.data
  },

  async getMeSession(uuid: string): Promise<GetMeSessionResponse> {
    const response = await api.get<GetMeSessionResponse>(`users/me/sessions/${uuid}`)

    return response.data
  },
}
