export interface QuizQuestionOptionBase {
  text: string
}

export interface QuizQuestionBase {
  text: string
  is_multiple_answers: boolean
}

export interface QuizBase {
  title: string
  description: string
}

export interface SummaryQuiz extends QuizBase {
  uuid: string
  creator_uuid: string | null
  is_public: boolean
  total_questions: number
  created_at: string
  updated_at: string
}

export interface GetQuizzesResponse {
  quizzes: Array<SummaryQuiz>
  total_quizzes: number
  page: number
  size: number
  total_pages: number
}

export interface DetailedQuizQuestionOption extends QuizQuestionOptionBase {
  uuid: string
  is_correct: boolean | null
}

export interface DetailedQuizQuestion extends QuizQuestionBase {
  uuid: string
  options: Array<DetailedQuizQuestionOption>
}

export interface DetailedQuiz extends SummaryQuiz {
  questions: Array<DetailedQuizQuestion>
}

export interface GetQuizResponse extends DetailedQuiz {}

export interface CreateQuizPayload extends QuizBase {}

export interface CreateQuizResponse {
  uuid: string
}

export interface UpdateQuizPayload {
  title?: string
  description?: string
  is_public?: boolean
}

export interface FullUpdateQuizQuestionOption extends QuizQuestionOptionBase {
  uuid?: string | null
  is_correct: boolean
}

export interface FullUpdateQuizQuestion extends QuizQuestionBase {
  uuid?: string | null
  options: Array<FullUpdateQuizQuestionOption>
}

export interface FullUpdateQuizPayload extends QuizBase {
  is_public: boolean
  questions: Array<FullUpdateQuizQuestion>
}
