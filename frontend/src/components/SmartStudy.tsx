import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, Check, RotateCcw, X } from 'lucide-react'
import { api } from '../api'
import { useStudent } from '../student'
import type { AnswerResult, Difficulty, Question, SubTopic } from '../types'
import { SubtopicChips } from './Filters'

const LEVELS: { d: Difficulty; label: string }[] = [
  { d: 'facil', label: 'Fácil' }, { d: 'medio', label: 'Médio' }, { d: 'dificil', label: 'Difícil' },
]
const LEVEL_LABEL = Object.fromEntries(LEVELS.map(l => [l.d, l.label])) as Record<Difficulty, string>
const LETTERS = ['A', 'B', 'C', 'D']

export default function SmartStudy({ topicId, onPosition, onAnswered }: {
  topicId: number; onPosition: (p: string) => void; onAnswered: () => void
}) {
  const { student } = useStudent()
  const [subtopics, setSubtopics] = useState<SubTopic[]>([])
  const [levels, setLevels] = useState<Difficulty[]>([])
  const [subs, setSubs] = useState<number[]>([])
  const [skipCorrect, setSkipCorrect] = useState(true)
  const [limit, setLimit] = useState(10)
  const [qs, setQs] = useState<Question[] | null>(null)
  const [i, setI] = useState(0)
  const [chosen, setChosen] = useState<number | null>(null)
  const [result, setResult] = useState<AnswerResult | null>(null)
  const [score, setScore] = useState(0)
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.subtopics(topicId).then(setSubtopics) }, [topicId])
  const subName = useMemo(() => Object.fromEntries(subtopics.map(s => [s.id, s.name])), [subtopics])

  const start = async () => {
    if (!student) return
    setLoading(true)
    const list = await api.questions(topicId, student.id, { difficulty: levels, subtopics: subs, skipCorrect, limit })
    setQs(list); setI(0); setChosen(null); setResult(null); setScore(0); setLoading(false)
  }

  const q = qs?.[i]
  useEffect(() => { if (q) onPosition(`question:${q.id}`) }, [q, onPosition])

  const answer = async (idx: number) => {
    if (!q || !student || result) return
    setChosen(idx)
    const r = await api.answer(q.id, student.id, idx)
    setResult(r)
    if (r.correct) setScore(s => s + 1)
    onAnswered()
  }

  const next = () => { setI(n => n + 1); setChosen(null); setResult(null) }
  const toggleLevel = (d: Difficulty) => setLevels(l => (l.includes(d) ? l.filter(x => x !== d) : [...l, d]))

  // ---------- configuração ----------
  if (!qs) {
    return (
      <div className="smart-setup">
        <fieldset className="step">
          <legend className="label">Nível</legend>
          <div className="chips">
            <button type="button" className="chip" aria-pressed={levels.length === 0} onClick={() => setLevels([])}>Todos os níveis</button>
            {LEVELS.map(l => (
              <button type="button" key={l.d} className={`chip lvl-${l.d}`} aria-pressed={levels.includes(l.d)} onClick={() => toggleLevel(l.d)}>{l.label}</button>
            ))}
          </div>
        </fieldset>
        <fieldset className="step">
          <legend className="label">Tópicos</legend>
          <SubtopicChips subtopics={subtopics} selected={subs} onChange={setSubs} />
        </fieldset>
        <fieldset className="step setup-row">
          <label className="check">
            <input type="checkbox" checked={skipCorrect} onChange={e => setSkipCorrect(e.target.checked)} />
            Esconder questões que já acertei
          </label>
          <label className="count-select">
            Questões por rodada
            <select className="input" value={limit} onChange={e => setLimit(Number(e.target.value))}>
              {[5, 10, 15, 20].map(n => <option key={n}>{n}</option>)}
            </select>
          </label>
        </fieldset>
        <button className="btn btn-primary" onClick={start} disabled={loading}>
          {loading ? 'Montando a rodada…' : 'Começar rodada'} <ArrowRight size={18} aria-hidden />
        </button>
      </div>
    )
  }

  // ---------- sem resultado / fim ----------
  if (qs.length === 0 || !q) {
    return (
      <div className="ficha done-card">
        <div className="ficha-head"><span className="label">{qs.length ? 'Fim da rodada' : 'Nada encontrado'}</span></div>
        {qs.length ? (
          <>
            <h2 className="continue-title num">{score} de {qs.length} certas</h2>
            <p className="muted">{score === qs.length ? 'Rodada perfeita.' : 'As que você errou voltam na próxima rodada.'}</p>
          </>
        ) : (
          <>
            <h2 className="continue-title">Nenhuma questão com esses filtros</h2>
            <p className="muted">{skipCorrect ? 'Talvez você já tenha acertado todas. Desmarque "esconder as que já acertei" ou mude os filtros.' : 'Mude o nível ou os tópicos.'}</p>
          </>
        )}
        <div className="row">
          <button className="btn btn-primary" onClick={start}><RotateCcw size={16} aria-hidden /> Nova rodada</button>
          <button className="btn" onClick={() => setQs(null)}>Mudar filtros</button>
        </div>
      </div>
    )
  }

  // ---------- questão ----------
  return (
    <div className="quiz">
      <div className="quiz-top">
        <button className="btn btn-ghost btn-sm" onClick={() => setQs(null)}>Filtros</button>
        <div className="progress-dots" aria-label={`Questão ${i + 1} de ${qs.length}`}>
          {qs.map((_, n) => <span key={n} className={n < i ? 'past' : n === i ? 'now' : ''} />)}
        </div>
        <span className="label num">{i + 1}/{qs.length}</span>
      </div>

      <article className="ficha question">
        <div className="ficha-head">
          <span className="label">{subName[q.subtopic_id]}</span>
          <span className={`level lvl-${q.difficulty}`}>{LEVEL_LABEL[q.difficulty]}</span>
        </div>
        <h2 className="q-text">{q.question}</h2>
        <ol className="options">
          {q.options.map((o, n) => {
            const state = !result ? '' : n === result.correct_index ? 'is-right' : n === chosen ? 'is-wrong' : 'is-dim'
            return (
              <li key={n}>
                <button className={`option ${state}`} onClick={() => answer(n)} disabled={!!result}>
                  <span className="letter">{state === 'is-right' ? <Check size={15} /> : state === 'is-wrong' ? <X size={15} /> : LETTERS[n]}</span>
                  <span>{o}</span>
                </button>
              </li>
            )
          })}
        </ol>
        {result && (
          <div className={`feedback ${result.correct ? 'ok' : 'bad'}`} role="status">
            <strong>{result.correct ? 'Certa.' : `Não foi dessa vez. A correta é a ${LETTERS[result.correct_index]}.`}</strong>
            <p>{result.explanation}</p>
          </div>
        )}
      </article>

      {result && (
        <div className="quiz-next">
          <button className="btn btn-primary" onClick={next} autoFocus>
            {i + 1 < qs.length ? 'Próxima questão' : 'Ver resultado'} <ArrowRight size={18} aria-hidden />
          </button>
        </div>
      )}
    </div>
  )
}
