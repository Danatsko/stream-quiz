import { defineStore } from 'pinia'
import { ref } from 'vue'
import { WebSocketService } from '@/services/websocket'
import useNotificationsStore from '@/stores/notifications'
import type {
  CreateRoomPayload,
  CreateSessionPayload,
  DetailedSession,
  IncomingHostWsMessage,
  SummaryRoom,
  SummarySession,
  UpdateRoomPayload,
  UpdateSessionPayload,
} from '@/types/rooms'
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
  const sessionStatusFilter = ref<string>('all')
  const roomSearchQuery = ref<string>('')
  const sessionSearchQuery = ref<string>('')
  const hostWs = ref<WebSocketService | null>(null)
  const hostEndTimeTs = ref<number | null>(null)
  const isLoading = ref<boolean>(false)

  const clearRooms = (): void => {
    rooms.value = []
    totalRooms.value = null
    roomsPage.value = null
    roomsTotalPages.value = null
  }

  const clearRoom = (): void => {
    room.value = null
  }

  const clearSessions = (): void => {
    sessions.value = []
    totalSessions.value = null
    sessionsPage.value = null
    sessionsTotalPages.value = null
  }

  const clearSession = (): void => {
    session.value = null
  }

  const setSessionStatusFilter = async (roomUuid: string, filter: string): Promise<void> => {
    if (sessionStatusFilter.value === filter) {
      return
    }

    sessionStatusFilter.value = filter

    clearSessions()
    await getSessions(roomUuid)
  }

  const setRoomSearchQuery = async (query: string): Promise<void> => {
    if (roomSearchQuery.value === query) {
      return
    }

    roomSearchQuery.value = query

    clearRooms()
    await getRooms()
  }

  const setSessionSearchQuery = async (roomUuid: string, query: string): Promise<void> => {
    if (sessionSearchQuery.value === query) {
      return
    }

    sessionSearchQuery.value = query

    clearSessions()
    await getSessions(roomUuid)
  }

  const createRoom = async (payload: CreateRoomPayload): Promise<string> => {
    isLoading.value = true

    try {
      const response = await roomsAPI.createRoom(payload)

      return response.uuid
    } catch (createRoomError) {
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

    try {
      const nextPage = roomsPage.value === null ? 1 : roomsPage.value + 1
      const response = await roomsAPI.getRooms(nextPage, roomsSize, roomSearchQuery.value)
      rooms.value.push(...response.rooms)
      totalRooms.value = response.total_rooms
      roomsPage.value = response.page
      roomsTotalPages.value = response.total_pages
    } catch (getRoomsError) {
      throw getRoomsError
    } finally {
      isLoading.value = false
    }
  }

  const getRoom = async (uuid: string): Promise<void> => {
    isLoading.value = true

    try {
      room.value = await roomsAPI.getRoom(uuid)
    } catch (getRoomError) {
      throw getRoomError
    } finally {
      isLoading.value = false
    }
  }

  const updateRoom = async (uuid: string, payload: UpdateRoomPayload): Promise<void> => {
    isLoading.value = true

    try {
      await roomsAPI.updateRoom(uuid, payload)
    } catch (updateRoomError) {
      throw updateRoomError
    } finally {
      isLoading.value = false
    }
  }

  const deleteRoom = async (uuid: string): Promise<void> => {
    isLoading.value = true

    try {
      await roomsAPI.deleteRoom(uuid)

      rooms.value = rooms.value.filter((r) => r.uuid !== uuid)

      if (room.value?.uuid === uuid) {
        room.value = null
      }
    } catch (deleteRoomError) {
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

    try {
      const response = await roomsAPI.createSession(roomUuid, payload)

      return response.uuid
    } catch (createSessionError) {
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

    try {
      const nextPage = sessionsPage.value === null ? 1 : sessionsPage.value + 1
      const response = await roomsAPI.getSessions(
        roomUuid,
        nextPage,
        sessionsSize,
        sessionStatusFilter.value,
        sessionSearchQuery.value,
      )
      sessions.value.push(...response.sessions)
      totalSessions.value = response.total_sessions
      sessionsPage.value = response.page
      sessionsTotalPages.value = response.total_pages
    } catch (getSessionsError) {
      throw getSessionsError
    } finally {
      isLoading.value = false
    }
  }

  const getSession = async (roomUuid: string, uuid: string): Promise<void> => {
    isLoading.value = true

    try {
      session.value = await roomsAPI.getSession(roomUuid, uuid)
    } catch (getSessionError) {
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

    try {
      await roomsAPI.updateSession(roomUuid, uuid, payload)
    } catch (updateSessionError) {
      throw updateSessionError
    } finally {
      isLoading.value = false
    }
  }

  const deleteSession = async (roomUuid: string, uuid: string): Promise<void> => {
    isLoading.value = true

    try {
      await roomsAPI.deleteSession(roomUuid, uuid)

      sessions.value = sessions.value.filter((s) => s.uuid !== uuid)

      if (session.value?.uuid === uuid) {
        session.value = null
      }
    } catch (deleteSessionError) {
      throw deleteSessionError
    } finally {
      isLoading.value = false
    }
  }

  const startSession = async (roomUuid: string, uuid: string): Promise<void> => {
    isLoading.value = true

    try {
      await roomsAPI.startSession(roomUuid, uuid)
    } catch (startSessionError) {
      throw startSessionError
    } finally {
      isLoading.value = false
    }
  }

  const stopSession = async (roomUuid: string, uuid: string): Promise<void> => {
    isLoading.value = true

    try {
      await roomsAPI.stopSession(roomUuid, uuid)
    } catch (stopSessionError) {
      throw stopSessionError
    } finally {
      isLoading.value = false
    }
  }

  const connectHostSession = (sessionUuid: string): void => {
    if (hostWs.value) {
      hostWs.value.disconnect()
    }

    hostWs.value = new WebSocketService(sessionUuid, 'host')
    hostWs.value.onOpen = (): void => {}

    hostWs.value.onMessage = (message: IncomingHostWsMessage) => {
      if (!session.value) {
        return
      }

      if (message.event === 'sync_state') {
        session.value.questions = message.questions
        session.value.total_questions = message.total_questions
        session.value.total_score = message.total_score
        session.value.members = message.members
        session.value.total_members = message.total_members
        hostEndTimeTs.value = message.end_time_ts
        session.value = { ...session.value }
      } else if (message.event === 'user_answered') {
        const { user_uuid, username, question_uuid, answer_data } = message
        let member = session.value.members.find((m) => m.user_uuid === user_uuid)

        if (!member) {
          member = {
            user_uuid,
            username: username || 'Unknown',
            answers: [],
            total_answers: 0,
            score: 0,
          }
          session.value.members.push(member)
          session.value.total_members = session.value.members.length
        }

        const question = session.value.questions.find((q) => q.uuid === question_uuid)
        let questionScore = 0

        if (question) {
          const correctOptions = question.options.filter((o) => o.is_correct).map((o) => o.uuid)
          const wrongOptions = question.options.filter((o) => !o.is_correct).map((o) => o.uuid)

          const safeAnswerData = Array.isArray(answer_data) ? answer_data : []
          const selectedCorrect = safeAnswerData.filter((id: string) =>
            correctOptions.includes(id),
          ).length
          const selectedWrong = safeAnswerData.filter((id: string) =>
            wrongOptions.includes(id),
          ).length

          const correctRatio =
            correctOptions.length > 0 ? selectedCorrect / correctOptions.length : 0
          const wrongRatio = wrongOptions.length > 0 ? selectedWrong / wrongOptions.length : 0
          questionScore = Math.max(0, correctRatio - wrongRatio)
        }

        const existingAnswer = member.answers.find((a) => a.question_uuid === question_uuid)

        if (existingAnswer) {
          const previouslyEmpty = existingAnswer.selected_option_uuids.length === 0

          member.score -= existingAnswer.score
          existingAnswer.selected_option_uuids = Array.isArray(answer_data) ? [...answer_data] : []
          existingAnswer.score = questionScore
          member.score += questionScore

          if (previouslyEmpty && answer_data && answer_data.length > 0) {
            member.total_answers += 1
          } else if (!previouslyEmpty && (!answer_data || answer_data.length === 0)) {
            member.total_answers -= 1
          }
        } else {
          member.answers.push({
            question_uuid,
            selected_option_uuids: Array.isArray(answer_data) ? [...answer_data] : [],
            score: questionScore,
          })
          member.score += questionScore
          member.total_answers += 1
        }

        member.score = Math.round(member.score * 100) / 100

        session.value = JSON.parse(JSON.stringify(session.value))
      } else if (message.event === 'session_closed') {
        useNotificationsStore().addNotification('Session has been completed', 'info')
        session.value.status = 'completed'
        disconnectHostSession()

        if (session.value.room_uuid) {
          getSession(session.value.room_uuid, session.value.uuid)
        }
      }
    }

    hostWs.value.onDisconnect = (event) => {
      if (event.code === 1008) {
        useNotificationsStore().addNotification(
          event.reason || 'Session is not active or you are not a host',
          'error',
        )
      }
    }
    hostWs.value.onError = (msg): void => {
      useNotificationsStore().addNotification(msg, 'error')
    }

    hostWs.value.connect()
  }

  const disconnectHostSession = (): void => {
    if (hostWs.value) {
      hostWs.value.disconnect()
      hostWs.value = null
    }

    hostEndTimeTs.value = null
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
    sessionStatusFilter,
    roomSearchQuery,
    sessionSearchQuery,
    hostEndTimeTs,
    isLoading,
    clearRooms,
    clearRoom,
    clearSessions,
    clearSession,
    setSessionStatusFilter,
    setRoomSearchQuery,
    setSessionSearchQuery,
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
    stopSession,
    connectHostSession,
    disconnectHostSession,
  }
})

export default useRoomsStore
