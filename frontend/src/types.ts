export type Student = { id: number; name: string }

export type TopicStats = {
  questions_total: number
  questions_answered: number
  questions_correct: number
  wrong_question_ids: number[]
  last_mode: Mode | null
  last_position: string | null
  updated_at: string | null
  sources: number
  flashcards: number
}

export type Topic = { id: number; subject_id: number; name: string; stats?: TopicStats }
export type Subject = { id: number; student_id: number; name: string; topics: Topic[] }
export type TopicDetail = Topic & { subject: { id: number; name: string } }

export type SourceStatus =
  | 'queued' | 'downloading' | 'extracting' | 'transcribing' | 'generating' | 'done' | 'error'

export type Source = {
  id: number
  topic_id: number
  kind: 'youtube' | 'pdf' | 'docx' | 'txt'
  ref: string
  title: string
  status: SourceStatus
  error: string | null
  chars: number
  created_at: string
  updated_at: string
}

export type GuideSection = { title: string; summary: string; key_points: string[] }
export type Guide = {
  source_id: number
  source_title: string
  source_kind: Source['kind']
  overview: string
  sections: GuideSection[]
}

export type SubTopic = { id: number; name: string }
export type Flashcard = {
  id: number
  subtopic_id: number
  term: string
  meaning: string
  last_result: ReviewResult | null
  next_due: string | null
}
export type ReviewResult = 'errei' | 'dificil' | 'acertei'

export type Difficulty = 'facil' | 'medio' | 'dificil'
export type Question = {
  id: number
  subtopic_id: number
  difficulty: Difficulty
  question: string
  options: string[]
}
export type AnswerResult = { correct: boolean; correct_index: number; explanation: string }

export type Mode = 'guia' | 'flashcards' | 'estudo_inteligente'
