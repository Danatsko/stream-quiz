import type {
  CreateRoomPayload,
  CreateRoomResponse,
  CreateSessionPayload,
  CreateSessionResponse,
  GetRoomResponse,
  GetRoomsResponse,
  GetSessionResponse,
  GetSessionsResponse,
  UpdateRoomPayload,
  UpdateSessionPayload,
} from '@/types/rooms'
import api from '@/services/api'

export const roomsAPI = {
  async createRoom(payload: CreateRoomPayload): Promise<CreateRoomResponse> {
    const response = await api.post<CreateRoomResponse>('/rooms', payload)

    return response.data
  },

  async getRooms(page: number, size: number): Promise<GetRoomsResponse> {
    const response = await api.get<GetRoomsResponse>('/rooms', {
      params: {
        page: page,
        size: size,
      },
    })

    return response.data
  },

  async getRoom(uuid: string): Promise<GetRoomResponse> {
    const response = await api.get<GetRoomResponse>(`/rooms/${uuid}`)

    return response.data
  },

  async updateRoom(uuid: string, payload: UpdateRoomPayload): Promise<void> {
    await api.patch(`/rooms/${uuid}`, payload)
  },

  async deleteRoom(uuid: string): Promise<void> {
    await api.delete(`/rooms/${uuid}`)
  },

  async createSession(
    roomUuid: string,
    payload: CreateSessionPayload,
  ): Promise<CreateSessionResponse> {
    const response = await api.post<CreateSessionResponse>(`/rooms/${roomUuid}/sessions`, payload)

    return response.data
  },

  async getSessions(
    roomUuid: string,
    page: number,
    size: number,
    status: string = 'all',
  ): Promise<GetSessionsResponse> {
    const response = await api.get<GetSessionsResponse>(`/rooms/${roomUuid}/sessions`, {
      params: {
        page: page,
        size: size,
        status: status,
      },
    })

    return response.data
  },

  async getSession(roomUuid: string, uuid: string): Promise<GetSessionResponse> {
    const response = await api.get<GetSessionResponse>(`/rooms/${roomUuid}/sessions/${uuid}`)

    return response.data
  },

  async updateSession(
    roomUuid: string,
    uuid: string,
    payload: UpdateSessionPayload,
  ): Promise<void> {
    await api.patch(`/rooms/${roomUuid}/sessions/${uuid}`, payload)
  },

  async deleteSession(roomUuid: string, uuid: string): Promise<void> {
    await api.delete(`/rooms/${roomUuid}/sessions/${uuid}`)
  },

  async startSession(roomUuid: string, uuid: string): Promise<void> {
    await api.post(`/rooms/${roomUuid}/sessions/${uuid}/start`)
  },

  async stopSession(roomUuid: string, uuid: string): Promise<void> {
    await api.post(`/rooms/${roomUuid}/sessions/${uuid}/stop`)
  },
}
