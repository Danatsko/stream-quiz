import { defineStore } from 'pinia'
import { ref } from 'vue'
import { WebSocketService } from '@/services/websocket'
import type { GameQuestion, IncomingWsMessage, SubmitAnswerPayload } from '@/types/take'

export const useTakeStore = defineStore('take', () => {
  const wsService = ref<WebSocketService | null>(null)
  const isConnected = ref<boolean>(false)
  const isReconnecting = ref<boolean>(false)
  const questions = ref<GameQuestion[]>([])
  const endTimeTs = ref<number | null>(null)
  const error = ref<string | null>(null)

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
        error.value = event.reason || 'Session is not active'
      }
    }
    wsService.value.onError = (message: string): void => {
      error.value = message
    }

    wsService.value.connect()
  }

  const handleIncomingMessage = (message: IncomingWsMessage): void => {
    switch (message.event) {
      case 'sync_state':
        questions.value = message.questions
        endTimeTs.value = message.end_time_ts

        break
      case 'error':
        error.value = message.message

        break
      case 'session_closed':
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
      option_uuids: optionUuids,
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
    questions.value = []
    endTimeTs.value = null
  }

  return {
    isConnected,
    isReconnecting,
    questions,
    endTimeTs,
    error,
    connectToSession,
    submitAnswer,
    disconnectFromSession,
  }
})

export default useTakeStore
