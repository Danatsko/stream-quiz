import api from '@/services/api'
import type { GetMeResponse } from '@/types/user'

export const usersAPI = {
  async getMe(): Promise<GetMeResponse> {
    const response = await api.get<GetMeResponse>('/users/me')

    return response.data
  },
}
