import type { GetSessionResponse } from '@/types/rooms.ts'

export interface SessionQuestionOptionBase {
  uuid: string
  text: string
}

export interface SessionQuestionBase {
  uuid: string
  text: string
  is_multiple_answers: boolean
  options: Array<SessionQuestionOptionBase>
}

export interface SessionMemberAnswerSelectedOptionBase {
  uuid: string
  is_correct: boolean
}

export interface SessionMemberAnswerBase {
  question_uuid: string
  selected_options: Array<SessionMemberAnswerSelectedOptionBase>
  score: number
}

export interface SessionBase {
  title: string
  description: string
  time_seconds: number
}

export interface SummarySession extends SessionBase {
  uuid: string
  quiz_uuid: string | null
  status: string
}

export interface GetMeSessionsResponse {
  sessions: Array<SummarySession>
  total_sessions: number
  page: number
  size: number
  total_pages: number
}

export interface DetailedSession extends SummarySession {
  questions: Array<SessionQuestionBase>
  total_questions: number
  total_score: number
  answers: Array<SessionMemberAnswerBase>
  total_answers: number
  score: number
}

export interface GetMeSessionResponse extends DetailedSession {}
