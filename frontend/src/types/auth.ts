export interface RegistrationPayload {
  username: string
  email: string
  password: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface VerifyPayload {
  token: string
}

export interface ResendVerificationPayload {
  email: string
}
