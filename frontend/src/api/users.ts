import api from '@/services/api'
import type { GetMeResponse, UpdateMePayload } from '../types/users'

export const usersAPI = {
  async getMe(): Promise<GetMeResponse> {
    const response = await api.get<GetMeResponse>('/users/me')

    return response.data
  },

  async updateMe(payload: UpdateMePayload): Promise<void> {
    await api.patch('/users/me', payload)
  },

  async deleteMe(): Promise<void> {
    await api.delete('/users/me')
  },
}
