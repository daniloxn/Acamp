import { useCallback, useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { api } from '../api'
import { useStudent } from '../student'
import type { Flashcard, ReviewResult, SubTopic } from '../types'
import { SubtopicChips } from './Filters'

const ORDER: Record<string, number> = { errei: 0, null: 1, dificil: 2, acertei: 3 }
const RESULTS: { r: ReviewResult; label: string; key: string; when: string }[] = [
  { r: 'errei', label: 'Errei', key: '1', when: 'volta em 10 min' },
  { r: 'dificil', label: 'Difícil', key: '2', when: 'volta amanhã' },
  { r: 'acertei', label: 'Acertei', key: '3', when: 'volta em 3 dias' },
]

function dueLabel(iso: string) {
  const d = new Date(iso), diff = d.getTime() - Date.now()
  if (diff <= 0) return 'hoje'
  if (diff < 36e5) return 'em ' + Math.max(1, Math.round(diff / 6e4)) + ' min'
  return 'em ' + d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}

export default function Flashcards({ topicId, resume, onPosition }: { topicId: number; resume: string; onPosition: (p: string) => void }) {
  const { student } = useStudent()
  const [subtopics, setSubtopics] = useState<SubTopic[]>([])
  const [selected, setSelected] = useState<number[]>([])
  const [deck, setDeck] = useState<Flashcard[] | null>(null)
  const [i, setI] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [tally, setTally] = useState<Record<ReviewResult, number>>({ errei: 0, dificil: 0, acertei: 0 })

  useEffect(() => { api.subtopics(topicId).then(setSubtopics) }, [topicId])

  useEffect(() => {
    if (!student) return
    api.flashcards(topicId, student.id, selected).then(cards => {
      const sorted = [...cards].sort((a, b) => ORDER[String(a.last_result)] - ORDER[String(b.last_result)])
      setDeck(sorted)
      const at = resume ? sorted.findIndex(c => String(c.id) === resume) : -1
      setI(at > 0 ? at : 0)
      setFlipped(false)
      setTally({ errei: 0, dificil: 0, acertei: 0 })
    })
  }, [topicId, student, selected, resume])

  const card = deck?.[i]
  const subName = useMemo(() => Object.fromEntries(subtopics.map(s => [s.id, s.name])), [subtopics])

  useEffect(() => { if (card) onPosition(String(card.id)) }, [card, onPosition])

  const rate = useCallback((r: ReviewResult) => {
    if (!card || !student) return
    api.review(card.id, student.id, r).catch(() => {})
    setTally(t => ({ ...t, [r]: t[r] + 1 }))
    setFlipped(false)
    setI(n => n + 1)
  }, [card, student])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).closest('input, textarea')) return
      if (e.key === ' ') { e.preventDefault(); setFlipped(f => !f) }
      const hit = RESULTS.find(x => x.key === e.key)
      if (hit && flipped) rate(hit.r)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [flipped, rate])

  if (!deck) return <div className="empty muted">Separando as fichas…</div>

  return (
    <div className="cards">
      <SubtopicChips subtopics={subtopics} selected={selected} onChange={setSelected} />

      {deck.length === 0 ? (
        <div className="empty panel"><h3>Nenhuma ficha nesses tópicos</h3><p>Escolha outros tópicos acima.</p></div>
      ) : !card ? (
        <div className="ficha done-card">
          <div className="ficha-head"><span className="label">Fim do maço</span><span className="label num">{deck.length} fichas</span></div>
          <h2 className="continue-title">Maço revisado</h2>
          <p className="muted num">Acertei {tally.acertei} · Difícil {tally.dificil} · Errei {tally.errei}</p>
          <button className="btn btn-primary" onClick={() => { setI(0); setTally({ errei: 0, dificil: 0, acertei: 0 }) }}>
            <RotateCcw size={16} aria-hidden /> Revisar de novo
          </button>
        </div>
      ) : (
        <>
          <div className="deck-meta">
            <span className="label num">Ficha {i + 1} de {deck.length}</span>
            <span className="label">{subName[card.subtopic_id]}</span>
          </div>
          <div className="deck">
            {deck.length - i > 2 && <div className="ficha stack s2" aria-hidden />}
            {deck.length - i > 1 && <div className="ficha stack s1" aria-hidden />}
            <button className={`flip ${flipped ? 'is-flipped' : ''}`} onClick={() => setFlipped(f => !f)}
              aria-label={flipped ? 'Mostrar o termo' : 'Mostrar o significado'} key={card.id}>
              <div className="ficha face front">
                <div className="ficha-head"><span className="label">Termo</span>
                  {card.last_result && <span className={`stamp stamp-${card.last_result}`}>{RESULTS.find(r => r.r === card.last_result)!.label}</span>}
                </div>
                <p className="term">{card.term}</p>
                <span className="hint">Toque para virar</span>
              </div>
              <div className="ficha face back">
                <div className="ficha-head"><span className="label">{card.term}</span><span className="label">Significado</span></div>
                <p className="meaning">{card.meaning}</p>
                {card.next_due && <span className="stamp stamp-due">Revisar {dueLabel(card.next_due)}</span>}
              </div>
            </button>
          </div>
          <div className="rate" aria-hidden={!flipped}>
            {RESULTS.map(x => (
              <button key={x.r} className={`btn rate-${x.r}`} disabled={!flipped} onClick={() => rate(x.r)}>
                {x.label}<small>{x.when}</small>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
