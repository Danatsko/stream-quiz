export interface RoomBase {
  title: string
  description: string
}

export interface SessionQuestionOptionBase {
  uuid: string
  text: string
  is_correct: boolean
}

export interface SessionQuestionBase {
  uuid: string
  text: string
  is_multiple_answers: boolean
  options: Array<SessionQuestionOptionBase>
}

export interface SessionMemberAnswerBase {
  question_uuid: string
  selected_option_uuids: Array<string>
  score: number
}

export interface SessionMemberBase {
  user_uuid: string | null
  username: string
  answers: Array<SessionMemberAnswerBase>
  total_answers: number
  score: number
}

export interface SessionBase {
  title: string
  description: string
  time_seconds: number
}

export interface CreateRoomPayload extends RoomBase {}

export interface CreateRoomResponse {
  uuid: string
}

export interface SummaryRoom extends RoomBase {
  creator_uuid: string
  uuid: string
  created_at: string
  updated_at: string
}

export interface GetRoomsResponse {
  rooms: Array<SummaryRoom>
  total_rooms: number
  page: number
  size: number
  total_pages: number
}

export interface GetRoomResponse extends SummaryRoom {}

export interface UpdateRoomPayload {
  title?: string
  description?: string
}

export interface CreateSessionPayload extends SessionBase {
  quiz_uuid: string
}

export interface CreateSessionResponse {
  uuid: string
}

export interface SummarySession extends SessionBase {
  uuid: string
  room_uuid: string
  quiz_uuid: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface GetSessionsResponse {
  sessions: Array<SummarySession>
  total_sessions: number
  page: number
  size: number
  total_pages: number
}

export interface DetailedSession extends SummarySession {
  members: Array<SessionMemberBase>
  total_members: number
  questions: Array<SessionQuestionBase>
  total_questions: number
  total_score: number
}

export interface GetSessionResponse extends DetailedSession {}

export interface UpdateSessionPayload {
  quiz_uuid?: string
  title?: string
  description?: string
  time_seconds?: number
}

export interface HostWsSyncStateEvent {
  event: 'sync_state'
  end_time_ts: number | null
  questions: Array<SessionQuestionBase>
  total_questions: number
  total_score: number
  members: Array<SessionMemberBase>
  total_members: number
}

export interface HostWsUserAnsweredEvent {
  event: 'user_answered'
  user_uuid: string
  username: string
  question_uuid: string
  answer_data: Array<string>
}

export interface HostWsSessionClosedEvent {
  event: 'session_closed'
  message?: string
}

export interface HostWsErrorEvent {
  event: 'error'
  message: string
}

export type IncomingHostWsMessage =
  | HostWsSyncStateEvent
  | HostWsUserAnsweredEvent
  | HostWsSessionClosedEvent
  | HostWsErrorEvent
  | { event: string; [key: string]: any }
