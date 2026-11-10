import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { BookOpen, ChevronLeft, FolderOpen, Layers, Plus, Target } from 'lucide-react'
import { api } from '../api'
import { useStudent } from '../student'
import type { Mode, Source, TopicDetail, TopicStats } from '../types'
import Guide from '../components/Guide'
import Flashcards from '../components/Flashcards'
import SmartStudy from '../components/SmartStudy'
import Sources from '../components/Sources'

const TABS = [
  { slug: 'guia', label: 'Guia de estudo', icon: BookOpen, mode: 'guia' as Mode },
  { slug: 'flashcards', label: 'Flashcards', icon: Layers, mode: 'flashcards' as Mode },
  { slug: 'estudo', label: 'Estudo inteligente', icon: Target, mode: 'estudo_inteligente' as Mode },
  { slug: 'fontes', label: 'Fontes', icon: FolderOpen, mode: null },
]

export default function TopicPage() {
  const { topicId, tab } = useParams()
  const tid = Number(topicId)
  const nav = useNavigate()
  const [params] = useSearchParams()
  const { student, reloadSubjects } = useStudent()
  const [topic, setTopic] = useState<TopicDetail | null>(null)
  const [sources, setSources] = useState<Source[]>([])
  const [stats, setStats] = useState<TopicStats | null>(null)
  const [err, setErr] = useState('')

  const resume = params.get('retomar') ? stats?.last_position ?? '' : ''
  const ready = sources.some(s => s.status === 'done')
  const pending = sources.some(s => s.status !== 'done' && s.status !== 'error')
  const current = TABS.find(t => t.slug === tab) ?? (ready ? TABS[0] : TABS[3])

  const loadSources = useCallback(() => api.sources(tid).then(setSources), [tid])

  useEffect(() => {
    setTopic(null); setErr('')
    api.topic(tid).then(setTopic).catch(e => setErr(e.message))
    loadSources()
    if (student) api.progress(student.id, tid).then(setStats)
  }, [tid, student, loadSources])

  // polling enquanto houver fonte sendo processada
  useEffect(() => {
    if (!pending) return
    const h = setInterval(() => {
      api.sources(tid).then(next => {
        if (next.some((s, i) => s.status === 'done' && sources[i]?.status !== 'done')) reloadSubjects()
        setSources(next)
      })
    }, 3000)
    return () => clearInterval(h)
  }, [pending, tid, sources, reloadSubjects])

  const savePos = useCallback((mode: Mode, pos = '') => {
    if (student) api.savePosition(student.id, tid, mode, pos).catch(() => {})
  }, [student, tid])

  useEffect(() => { if (current.mode && ready) savePos(current.mode) }, [current.mode, ready, savePos])

  if (err) return <div className="empty"><h3>Assunto não encontrado</h3><p>{err}</p><Link to="/" className="btn">Voltar ao início</Link></div>
  if (!topic) return <div className="empty muted">Abrindo a gaveta…</div>

  return (
    <>
      <div className="page-head">
        <div>
          <Link to="/" className="crumb"><ChevronLeft size={16} aria-hidden /> {topic.subject.name}</Link>
          <h1 className="page-title">{topic.name}</h1>
        </div>
        <Link className="btn btn-sm" to={`/adicionar?assunto=${tid}`}><Plus size={16} aria-hidden /> Adicionar fonte</Link>
      </div>

      <div className="tabs" role="tablist">
        {TABS.map(t => (
          <button key={t.slug} role="tab" className="tab" aria-selected={current.slug === t.slug}
            onClick={() => nav(`/assunto/${tid}/${t.slug}`)}>
            <t.icon size={16} aria-hidden /> {t.label}
            {t.slug === 'fontes' && <span className="count num">{sources.length}</span>}
          </button>
        ))}
      </div>

      {current.slug === 'fontes' ? (
        <Sources sources={sources} onChange={() => { loadSources(); reloadSubjects() }} />
      ) : !ready ? (
        <div className="empty panel">
          <h3>{pending ? 'Catalogando o conteúdo…' : 'Este assunto ainda não tem material'}</h3>
          <p>{pending ? 'Assim que a primeira fonte terminar, o guia, os flashcards e as questões aparecem aqui.' : 'Adicione um vídeo ou documento para começar.'}</p>
          <button className="btn" onClick={() => nav(`/assunto/${tid}/fontes`)}>Ver fontes</button>
        </div>
      ) : current.slug === 'guia' ? (
        <Guide topicId={tid} resume={resume} onPosition={p => savePos('guia', p)} />
      ) : current.slug === 'flashcards' ? (
        <Flashcards topicId={tid} resume={resume} onPosition={p => savePos('flashcards', p)} />
      ) : (
        <SmartStudy topicId={tid} onPosition={p => savePos('estudo_inteligente', p)} onAnswered={() => reloadSubjects()} />
      )}
    </>
  )
}
