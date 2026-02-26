export interface QuizQuestionOption {
  text: string
}

export interface QuizQuestion {
  text: string
  is_multiple_answers: boolean
}

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

export interface DetailedQuizQuestionOption extends QuizQuestionOption {
  uuid: string
  is_correct: boolean | null
}

export interface DetailedQuizQuestion extends QuizQuestion {
  uuid: string
  options: Array<DetailedQuizQuestionOption>
}

export interface DetailedQuiz extends Quiz {
  uuid: string
  creator_uuid: string | null
  questions: Array<DetailedQuizQuestion>
  total_questions: number
}

export interface GetQuizResponse extends DetailedQuiz {}

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
