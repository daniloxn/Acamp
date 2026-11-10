import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, Layers, Target } from 'lucide-react'
import { useStudent } from '../student'
import type { Mode } from '../types'

export const MODE_TAB: Record<Mode, string> = { guia: 'guia', flashcards: 'flashcards', estudo_inteligente: 'estudo' }
export const MODE_LABEL: Record<Mode, string> = { guia: 'Guia de estudo', flashcards: 'Flashcards', estudo_inteligente: 'Estudo inteligente' }
const MODE_ICON = { guia: BookOpen, flashcards: Layers, estudo_inteligente: Target }

function when(iso: string) {
  const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z')
  const days = Math.floor((Date.now() - d.getTime()) / 86400000)
  if (days <= 0) return 'hoje'
  if (days === 1) return 'ontem'
  return `há ${days} dias`
}

export default function Home() {
  const { student, subjects, loaded } = useStudent()
  const topics = subjects.flatMap(s => s.topics.map(t => ({ ...t, subject: s.name })))
  const last = topics
    .filter(t => t.stats?.updated_at)
    .sort((a, b) => (b.stats!.updated_at! > a.stats!.updated_at! ? 1 : -1))[0]

  return (
    <div className="home-main">
      <h1 className="page-title">Olá, {student?.name}.</h1>

      {!loaded ? (
        <p className="muted">Abrindo o fichário…</p>
      ) : last ? (
        <section className="ficha continue" aria-labelledby="cont-title">
          <div className="ficha-head">
            <span className="label">{last.subject}</span>
            <span className="label">{when(last.stats!.updated_at!)}</span>
          </div>
          <h2 id="cont-title" className="continue-title">{last.name}</h2>
          <p className="muted continue-meta">
            {(() => { const m = last.stats!.last_mode!; const I = MODE_ICON[m]; return <><I size={16} aria-hidden /> Você parou em {MODE_LABEL[m]}</> })()}
            <span className="dot" aria-hidden>·</span>
            <span className="num">{last.stats!.questions_correct} de {last.stats!.questions_total} questões certas</span>
          </p>
          <Link className="btn btn-primary" to={`/assunto/${last.id}/${MODE_TAB[last.stats!.last_mode!]}?retomar=1`}>
            Continuar de onde parei <ArrowRight size={18} aria-hidden />
          </Link>
        </section>
      ) : topics.length ? (
        <p className="muted">Escolha um assunto ao lado para começar a estudar.</p>
      ) : (
        <section className="ficha continue">
          <div className="ficha-head"><span className="label">Fichário vazio</span></div>
          <h2 className="continue-title">Comece pela primeira aula</h2>
          <p className="muted">Cole um link do YouTube ou envie um PDF. O Acamp transcreve, organiza e monta guia, flashcards e questões.</p>
          <Link className="btn btn-primary" to="/adicionar">Adicionar conteúdo <ArrowRight size={18} aria-hidden /></Link>
        </section>
      )}
    </div>
  )
}
