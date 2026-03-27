import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  CreateRoomPayload,
  CreateSessionPayload,
  DetailedSession,
  SummaryRoom,
  SummarySession,
  UpdateRoomPayload,
  UpdateSessionPayload,
} from '@/types/rooms'
import { AxiosError } from 'axios'
import { roomsAPI } from '@/api/rooms'

export const useRoomsStore = defineStore('rooms', () => {
  const rooms = ref<Array<SummaryRoom>>([])
  const room = ref<SummaryRoom | null>(null)
  const totalRooms = ref<number | null>(null)
  const roomsPage = ref<number | null>(null)
  const roomsSize = 10
  const roomsTotalPages = ref<number | null>(null)
  const sessions = ref<Array<SummarySession>>([])
  const session = ref<DetailedSession | null>(null)
  const totalSessions = ref<number | null>(null)
  const sessionsPage = ref<number | null>(null)
  const sessionsSize = 10
  const sessionsTotalPages = ref<number | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const resetError = (): void => {
    error.value = null
  }

  const clearRooms = (): void => {
    rooms.value = []
    totalRooms.value = null
    roomsPage.value = null
    roomsTotalPages.value = null
    resetError()
  }

  const clearRoom = (): void => {
    room.value = null
    resetError()
  }

  const clearSessions = (): void => {
    sessions.value = []
    totalSessions.value = null
    sessionsPage.value = null
    sessionsTotalPages.value = null
    resetError()
  }

  const clearSession = (): void => {
    session.value = null
    resetError()
  }

  const createRoom = async (payload: CreateRoomPayload): Promise<string> => {
    isLoading.value = true
    resetError()

    try {
      const response = await roomsAPI.createRoom(payload)

      return response.uuid
    } catch (createRoomError) {
      if (createRoomError instanceof AxiosError) {
        error.value = createRoomError.response?.data?.detail || 'Error during create room'
      }

      throw createRoomError
    } finally {
      isLoading.value = false
    }
  }

  const getRooms = async (): Promise<void> => {
    if (
      roomsPage.value !== null &&
      roomsTotalPages.value !== null &&
      roomsPage.value >= roomsTotalPages.value
    ) {
      return
    }

    isLoading.value = true
    resetError()

    try {
      const nextPage = roomsPage.value === null ? 1 : roomsPage.value + 1
      const response = await roomsAPI.getRooms(nextPage, roomsSize)
      rooms.value.push(...response.rooms)
      totalRooms.value = response.total_rooms
      roomsPage.value = response.page
      roomsTotalPages.value = response.total_pages
    } catch (getRoomsError) {
      if (getRoomsError instanceof AxiosError) {
        error.value = getRoomsError.response?.data?.detail || 'Error during get rooms'
      }

      throw getRoomsError
    } finally {
      isLoading.value = false
    }
  }

  const getRoom = async (uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      room.value = await roomsAPI.getRoom(uuid)
    } catch (getRoomError) {
      if (getRoomError instanceof AxiosError) {
        error.value = getRoomError.response?.data?.detail || 'Error during get room'
      }

      throw getRoomError
    } finally {
      isLoading.value = false
    }
  }

  const updateRoom = async (uuid: string, payload: UpdateRoomPayload): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await roomsAPI.updateRoom(uuid, payload)
    } catch (updateRoomError) {
      if (updateRoomError instanceof AxiosError) {
        error.value = updateRoomError.response?.data?.detail || 'Error during update room'
      }

      throw updateRoomError
    } finally {
      isLoading.value = false
    }
  }

  const deleteRoom = async (uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await roomsAPI.deleteRoom(uuid)

      rooms.value = rooms.value.filter((r) => r.uuid !== uuid)

      if (room.value?.uuid === uuid) {
        room.value = null
      }
    } catch (deleteRoomError) {
      if (deleteRoomError instanceof AxiosError) {
        error.value = deleteRoomError.response?.data?.detail || 'Error during delete room'
      }

      throw deleteRoomError
    } finally {
      isLoading.value = false
    }
  }

  const createSession = async (
    roomUuid: string,
    payload: CreateSessionPayload,
  ): Promise<string> => {
    isLoading.value = true
    resetError()

    try {
      const response = await roomsAPI.createSession(roomUuid, payload)

      return response.uuid
    } catch (createSessionError) {
      if (createSessionError instanceof AxiosError) {
        error.value = createSessionError.response?.data?.detail || 'Error during create session'
      }

      throw createSessionError
    } finally {
      isLoading.value = false
    }
  }

  const getSessions = async (roomUuid: string): Promise<void> => {
    if (
      sessionsPage.value !== null &&
      sessionsTotalPages.value !== null &&
      sessionsPage.value >= sessionsTotalPages.value
    ) {
      return
    }

    isLoading.value = true
    resetError()

    try {
      const nextPage = sessionsPage.value === null ? 1 : sessionsPage.value + 1
      const response = await roomsAPI.getSessions(roomUuid, nextPage, sessionsSize)
      sessions.value.push(...response.sessions)
      totalSessions.value = response.total_sessions
      sessionsPage.value = response.page
      sessionsTotalPages.value = response.total_pages
    } catch (getSessionsError) {
      if (getSessionsError instanceof AxiosError) {
        error.value = getSessionsError.response?.data?.detail || 'Error during get sessions'
      }

      throw getSessionsError
    } finally {
      isLoading.value = false
    }
  }

  const getSession = async (roomUuid: string, uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      session.value = await roomsAPI.getSession(roomUuid, uuid)
    } catch (getSessionError) {
      if (getSessionError instanceof AxiosError) {
        error.value = getSessionError.response?.data?.detail || 'Error during get session'
      }

      throw getSessionError
    } finally {
      isLoading.value = false
    }
  }

  const updateSession = async (
    roomUuid: string,
    uuid: string,
    payload: UpdateSessionPayload,
  ): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await roomsAPI.updateSession(roomUuid, uuid, payload)
    } catch (updateSessionError) {
      if (updateSessionError instanceof AxiosError) {
        error.value = updateSessionError.response?.data?.detail || 'Error during update session'
      }

      throw updateSessionError
    } finally {
      isLoading.value = false
    }
  }

  const deleteSession = async (roomUuid: string, uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await roomsAPI.deleteSession(roomUuid, uuid)

      sessions.value = sessions.value.filter((s) => s.uuid !== uuid)

      if (session.value?.uuid === uuid) {
        session.value = null
      }
    } catch (deleteSessionError) {
      if (deleteSessionError instanceof AxiosError) {
        error.value = deleteSessionError.response?.data?.detail || 'Error during delete session'
      }

      throw deleteSessionError
    } finally {
      isLoading.value = false
    }
  }

  const startSession = async (roomUuid: string, uuid: string): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await roomsAPI.startSession(roomUuid, uuid)
    } catch (startSessionError) {
      if (startSessionError instanceof AxiosError) {
        error.value = startSessionError.response?.data?.detail || 'Error during start session'
      }

      throw startSessionError
    } finally {
      isLoading.value = false
    }
  }

  return {
    rooms,
    room,
    totalRooms,
    roomsPage,
    roomsSize,
    roomsTotalPages,
    sessions,
    session,
    totalSessions,
    sessionsPage,
    sessionsSize,
    sessionsTotalPages,
    isLoading,
    error,
    clearRooms,
    clearRoom,
    clearSessions,
    clearSession,
    createRoom,
    getRooms,
    getRoom,
    updateRoom,
    deleteRoom,
    createSession,
    getSessions,
    getSession,
    updateSession,
    deleteSession,
    startSession,
  }
})

export default useRoomsStore
