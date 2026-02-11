import api from '@/services/api'
import type { User } from '@/types/user'

export const usersAPI = {
  async getMe(): Promise<User> {
    const response = await api.get<User>('/users/me')

    return response.data
  },
}
