export type SessionStatus = 'waiting' | 'active' | 'completed'

export interface GameOption {
  uuid: string
  text: string
}

export interface GameQuestion {
  uuid: string
  text: string
  is_multiple_answers: boolean
  options: Array<GameOption>
}

export interface SyncStateEvent {
  event: 'sync_state'
  end_time_ts: number
  questions: Array<GameQuestion>
}

export interface ErrorEvent {
  event: 'error'
  message: string
}

export interface SessionClosedEvent {
  event: 'session_closed'
}

export type IncomingWsMessage =
  | SyncStateEvent
  | ErrorEvent
  | SessionClosedEvent
  | { event: string; [key: string]: any }

export interface SubmitAnswerPayload {
  event: 'submit_answer'
  question_uuid: string
  option_uuids: Array<string>
}
