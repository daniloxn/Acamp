import { useEffect, useRef, useState } from 'react'
import { FileText, Video } from 'lucide-react'
import { api } from '../api'
import type { Guide as G } from '../types'

export default function Guide({ topicId, resume, onPosition }: { topicId: number; resume: string; onPosition: (p: string) => void }) {
  const [guides, setGuides] = useState<G[] | null>(null)
  const [active, setActive] = useState('')
  const timer = useRef<number>(undefined)

  useEffect(() => { api.guide(topicId).then(setGuides) }, [topicId])

  // retoma a seção onde parou
  useEffect(() => {
    if (guides && resume) document.getElementById(resume)?.scrollIntoView({ block: 'start' })
  }, [guides, resume])

  // acompanha a seção visível e salva a posição
  useEffect(() => {
    if (!guides) return
    const io = new IntersectionObserver(entries => {
      const top = entries.filter(e => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0]
      if (!top) return
      setActive(top.target.id)
      clearTimeout(timer.current)
      timer.current = window.setTimeout(() => onPosition(top.target.id), 1200)
    }, { rootMargin: '0px 0px -65% 0px' })
    document.querySelectorAll('.guide-section').forEach(el => io.observe(el))
    return () => { io.disconnect(); clearTimeout(timer.current) }
  }, [guides, onPosition])

  if (!guides) return <div className="empty muted">Carregando o guia…</div>

  return (
    <div className="guide">
      <nav className="guide-toc" aria-label="Seções do guia">
        {guides.map(g => (
          <div key={g.source_id}>
            <span className="label">{g.source_title}</span>
            {g.sections.map((s, i) => {
              const id = `s${g.source_id}-${i}`
              return <a key={id} href={`#${id}`} aria-current={active === id ? 'true' : undefined}>{s.title}</a>
            })}
          </div>
        ))}
      </nav>

      <div className="guide-body">
        {guides.map(g => (
          <article key={g.source_id} className="guide-source">
            <header className="ficha guide-overview">
              <div className="ficha-head">
                <span className="label">{g.source_kind === 'youtube' ? <Video size={13} aria-hidden /> : <FileText size={13} aria-hidden />} {g.source_title}</span>
                <span className="label">Visão geral</span>
              </div>
              <p>{g.overview}</p>
            </header>
            {g.sections.map((s, i) => (
              <section key={i} id={`s${g.source_id}-${i}`} className="guide-section">
                <h2>{s.title}</h2>
                <p>{s.summary}</p>
                <ul className="key-points">
                  {s.key_points.map((k, j) => <li key={j}>{k}</li>)}
                </ul>
              </section>
            ))}
          </article>
        ))}
      </div>
    </div>
  )
}
