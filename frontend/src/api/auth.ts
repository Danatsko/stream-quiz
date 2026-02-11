import api from '@/services/api'
import type { RegistrationPayload } from '@/types/auth'

export const authAPI = {
  async registration(payload: RegistrationPayload): Promise<void> {
    await api.post('/auth/registration', payload)
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },
}
