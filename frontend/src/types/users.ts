export interface User {
  uuid: string
  username: string
  email: string
}

export interface GetMeResponse extends User {}

export interface UpdateMePayload {
  username?: string
}
