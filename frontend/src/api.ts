import type {
  AnswerResult, Difficulty, Flashcard, Guide, Mode, Question, ReviewResult, Source, Student,
  Subject, SubTopic, Topic, TopicDetail, TopicStats,
} from './types'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, init)
  if (!r.ok) {
    let msg = `Erro ${r.status}`
    try { msg = (await r.json()).detail ?? msg } catch { /* sem corpo */ }
    throw new Error(msg)
  }
  return r.json()
}

const json = (method: string, body: unknown): RequestInit => ({
  method, headers: { 'content-type': 'application/json' }, body: JSON.stringify(body),
})

const ids = (list?: number[]) => (list && list.length ? list.join(',') : '')

export const api = {
  students: () => req<Student[]>('/students'),
  createStudent: (name: string) => req<Student>('/students', json('POST', { name })),

  subjects: (sid: number) => req<Subject[]>(`/students/${sid}/subjects`),
  createSubject: (sid: number, name: string) => req<Subject>(`/students/${sid}/subjects`, json('POST', { name })),
  createTopic: (subjectId: number, name: string) => req<Topic>(`/subjects/${subjectId}/topics`, json('POST', { name })),
  topic: (tid: number) => req<TopicDetail>(`/topics/${tid}`),

  sources: (tid: number) => req<Source[]>(`/topics/${tid}/sources`),
  addLink: (tid: number, url: string) => req<Source>(`/topics/${tid}/sources`, json('POST', { url })),
  addFile: (tid: number, file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return req<Source>(`/topics/${tid}/sources`, { method: 'POST', body: fd })
  },
  retry: (id: number) => req<Source>(`/sources/${id}/retry`, { method: 'POST' }),
  removeSource: (id: number) => req<{ ok: true }>(`/sources/${id}`, { method: 'DELETE' }),

  guide: (tid: number) => req<Guide[]>(`/topics/${tid}/guide`),
  subtopics: (tid: number) => req<SubTopic[]>(`/topics/${tid}/subtopics`),
  flashcards: (tid: number, sid: number, subtopics?: number[]) =>
    req<Flashcard[]>(`/topics/${tid}/flashcards?student_id=${sid}&subtopics=${ids(subtopics)}`),
  review: (fid: number, sid: number, result: ReviewResult) =>
    req(`/flashcards/${fid}/review`, json('POST', { student_id: sid, result })),

  questions: (tid: number, sid: number, o: { difficulty: Difficulty[]; subtopics: number[]; skipCorrect: boolean; limit: number }) =>
    req<Question[]>(`/topics/${tid}/questions?student_id=${sid}&difficulty=${o.difficulty.join(',')}` +
      `&subtopics=${ids(o.subtopics)}&skip_correct=${o.skipCorrect}&limit=${o.limit}`),
  answer: (qid: number, sid: number, chosen: number) =>
    req<AnswerResult>(`/questions/${qid}/answer`, json('POST', { student_id: sid, chosen_index: chosen })),

  progress: (sid: number, tid: number) => req<TopicStats>(`/students/${sid}/topics/${tid}/progress`),
  savePosition: (sid: number, tid: number, mode: Mode, position = '') =>
    req(`/students/${sid}/topics/${tid}/progress`, json('PUT', { mode, position })),
}
