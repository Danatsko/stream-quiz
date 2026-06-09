import { defineStore } from 'pinia'
import { ref } from 'vue'
import { WebSocketService } from '@/services/websocket'
import type { GameQuestion, IncomingWsMessage, SubmitAnswerPayload } from '@/types/take'
import useNotificationsStore from '@/stores/notifications'

export const useTakeStore = defineStore('take', () => {
  const wsService = ref<WebSocketService | null>(null)
  const isConnected = ref<boolean>(false)
  const isReconnecting = ref<boolean>(false)
  const questions = ref<GameQuestion[]>([])
  const totalQuestions = ref<number | null>(null)
  const answeredQuestions = ref<number | null>(null)
  const endTimeTs = ref<number | null>(null)
  const error = ref<string | null>(null)

  const clearState = (): void => {
    questions.value = []
    totalQuestions.value = null
    answeredQuestions.value = null
    endTimeTs.value = null
    error.value = null
  }

  const connectToSession = (sessionUuid: string): void => {
    if (wsService.value) {
      wsService.value.disconnect()
    }

    wsService.value = new WebSocketService(sessionUuid)
    wsService.value.onOpen = (): void => {
      isConnected.value = true
      isReconnecting.value = false
      error.value = null
    }
    wsService.value.onReconnectAttempt = (): void => {
      isReconnecting.value = true
      isConnected.value = false
    }
    wsService.value.onMessage = (message: IncomingWsMessage): void => {
      handleIncomingMessage(message)
    }
    wsService.value.onDisconnect = (event: CloseEvent): void => {
      isConnected.value = false

      if (event.code === 1008) {
        const msg = event.reason || 'Session is not active'
        error.value = msg

        useNotificationsStore().addNotification(msg, 'error')
      }
    }
    wsService.value.onError = (message: string): void => {
      error.value = message
      useNotificationsStore().addNotification(message, 'error')
    }

    wsService.value.connect()
  }

  const handleIncomingMessage = (message: IncomingWsMessage): void => {
    switch (message.event) {
      case 'sync_state':
        questions.value = message.questions
        endTimeTs.value = message.end_time_ts
        totalQuestions.value = message.total_questions
        answeredQuestions.value = message.answered_questions

        break
      case 'error':
        error.value = message.message

        useNotificationsStore().addNotification(message.message, 'error')

        break
      case 'session_closed':
        error.value = 'Session has been closed'

        useNotificationsStore().addNotification('Session has been closed', 'info')
        disconnectFromSession()

        break
      default:
        break
    }
  }

  const submitAnswer = (questionUuid: string, optionUuids: string[]): void => {
    if (!wsService.value) {
      return
    }

    const payload: SubmitAnswerPayload = {
      event: 'submit_answer',
      question_uuid: questionUuid,
      selected_option_uuids: optionUuids,
    }

    wsService.value.send(payload)
  }

  const disconnectFromSession = (): void => {
    if (wsService.value) {
      wsService.value.disconnect()

      wsService.value = null
    }
    isConnected.value = false
    isReconnecting.value = false
  }

  return {
    isConnected,
    isReconnecting,
    questions,
    totalQuestions,
    answeredQuestions,
    endTimeTs,
    error,
    clearState,
    connectToSession,
    submitAnswer,
    disconnectFromSession,
  }
})

export default useTakeStore
