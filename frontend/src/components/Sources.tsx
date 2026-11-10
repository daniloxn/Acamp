import { useEffect, useState } from 'react'
import { AlertTriangle, Check, FileText, Loader2, RotateCcw, Trash2, Video } from 'lucide-react'
import { api } from '../api'
import type { Source } from '../types'

const VIDEO_STEPS = [
  { s: 'downloading', label: 'Baixando áudio' },
  { s: 'transcribing', label: 'Transcrevendo' },
  { s: 'generating', label: 'Gerando material' },
]
const DOC_STEPS = [
  { s: 'extracting', label: 'Lendo documento' },
  { s: 'generating', label: 'Gerando material' },
]

function Steps({ src }: { src: Source }) {
  const steps = src.kind === 'youtube' ? VIDEO_STEPS : DOC_STEPS
  const at = steps.findIndex(x => x.s === src.status)
  return (
    <ol className="steps">
      {steps.map((x, n) => {
        const state = src.status === 'done' || n < at ? 'done' : n === at ? 'now' : 'todo'
        return (
          <li key={x.s} className={state}>
            {state === 'done' ? <Check size={14} aria-hidden /> : state === 'now' ? <Loader2 size={14} className="spin" aria-hidden /> : <span className="pip" aria-hidden />}
            {x.label}
          </li>
        )
      })}
    </ol>
  )
}

const SEEN_KEY = 'acamp.seen'
function readSeen(): Record<string, string> {
  try { return JSON.parse(localStorage.getItem(SEEN_KEY) || '{}') } catch { return {} }
}

export default function Sources({ sources, onChange }: { sources: Source[]; onChange: () => void }) {
  // status visto da última vez: o que mudou desde então ganha marca até a próxima visita
  const [before] = useState(readSeen)
  useEffect(() => {
    const seen = readSeen()
    for (const s of sources) seen[s.id] = s.status
    try { localStorage.setItem(SEEN_KEY, JSON.stringify(seen)) } catch { /* sem armazenamento */ }
  }, [sources])
  const [busy, setBusy] = useState<number | null>(null)
  const [err, setErr] = useState('')

  const act = async (id: number, fn: () => Promise<unknown>) => {
    setBusy(id); setErr('')
    try { await fn(); onChange() } catch (e) { setErr((e as Error).message) } finally { setBusy(null) }
  }

  if (!sources.length) return <div className="empty panel"><h3>Nenhuma fonte ainda</h3><p>Use “Adicionar fonte” para enviar um vídeo ou documento.</p></div>

  return (
    <ul className="sources">
      {err && <li className="error-text" role="alert">{err}</li>}
      {sources.map(src => {
        const working = src.status !== 'done' && src.status !== 'error'
        const fresh = !working && before[src.id] !== undefined && before[src.id] !== src.status
        return (
          <li key={src.id} className={`ficha source ${working ? 'is-working' : ''} ${src.status === 'error' ? 'is-error' : ''} ${fresh ? 'is-fresh' : ''}`}>
            <div className="ficha-head">
              <span className="label">{src.kind === 'youtube' ? <Video size={13} aria-hidden /> : <FileText size={13} aria-hidden />} {src.kind.toUpperCase()}{fresh && <span className="fresh-tag">{src.status === 'done' ? 'Pronto agora' : 'Falhou'}</span>}</span>
              <span className="label num">{new Date(src.created_at.endsWith('Z') || src.created_at.includes('+') ? src.created_at : src.created_at + 'Z').toLocaleDateString('pt-BR')}</span>
            </div>
            <div className="source-body">
              <div className="source-text">
                <strong className="source-title">{src.title || (src.kind === 'youtube' ? src.ref : 'Documento')}</strong>
                {src.status === 'queued' && <span className="muted small">Na fila. Uma fonte é processada por vez.</span>}
                {working && src.status !== 'queued' && <Steps src={src} />}
                {src.status === 'done' && <span className="muted small num">Pronto · {src.chars.toLocaleString('pt-BR')} caracteres de texto</span>}
                {src.status === 'error' && (
                  <span className="error-text small"><AlertTriangle size={14} aria-hidden /> Falhou: {src.error?.slice(0, 220)}</span>
                )}
              </div>
              <div className="source-actions">
                {src.status === 'error' && (
                  <button className="btn btn-sm" disabled={busy === src.id} onClick={() => act(src.id, () => api.retry(src.id))}>
                    <RotateCcw size={14} aria-hidden /> Tentar de novo
                  </button>
                )}
                {!working || src.status === 'queued' ? (
                  <button className="btn btn-ghost btn-sm" disabled={busy === src.id} title="Apagar fonte e o material gerado"
                    onClick={() => { if (confirm('Apagar esta fonte e todo o material gerado dela?')) act(src.id, () => api.removeSource(src.id)) }}>
                    <Trash2 size={14} aria-hidden /> Apagar
                  </button>
                ) : null}
              </div>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
