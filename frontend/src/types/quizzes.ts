export interface Quiz {
  title: string
  description: string
  is_public: boolean
}

export interface SummaryQuiz extends Quiz {
  uuid: string
  creator_uuid: string | null
  total_questions: number
}

export interface GetQuizzesResponse {
  quizzes: Array<SummaryQuiz>
  total_quizzes: number
  page: number
  size: number
  total_pages: number
}

export interface CreateQuizPayload {
  title: string
  description: string
}

export interface CreateQuizResponse {
  uuid: string
}
