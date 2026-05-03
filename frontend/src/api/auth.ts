import api from '@/services/api'
import type {
  LoginPayload,
  RegistrationPayload,
  ResendVerificationPayload,
  VerifyPayload,
} from '@/types/auth'

export const authAPI = {
  async registration(payload: RegistrationPayload): Promise<void> {
    await api.post('/auth/registration', payload)
  },

  async login(payload: LoginPayload): Promise<void> {
    await api.post('/auth/login', payload)
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  async verify(payload: VerifyPayload): Promise<void> {
    await api.post('/auth/verify', payload)
  },

  async resendVerification(payload: ResendVerificationPayload): Promise<void> {
    await api.post('/auth/resend-verification', payload)
  },
}
