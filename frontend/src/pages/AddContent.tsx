import { useMemo, useRef, useState, type FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { FileUp, Link2, Plus, Video } from 'lucide-react'
import { api } from '../api'
import { useStudent } from '../student'

const NEW = -1

export default function AddContent() {
  const { student, subjects, loaded, reloadSubjects } = useStudent()
  const nav = useNavigate()
  const [params] = useSearchParams()
  const preTopic = Number(params.get('assunto')) || null
  const preSubject = subjects.find(s => s.topics.some(t => t.id === preTopic))

  const [subjectId, setSubjectId] = useState<number | null>(null)
  const [subjectName, setSubjectName] = useState('')
  const [topicId, setTopicId] = useState<number | null>(preTopic)
  const [topicName, setTopicName] = useState('')
  const [kind, setKind] = useState<'link' | 'file'>('link')
  const [url, setUrl] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const effSubject = subjectId ?? preSubject?.id ?? (loaded && subjects.length === 0 ? NEW : null)
  const subject = useMemo(() => subjects.find(s => s.id === effSubject), [subjects, effSubject])
  const topics = subject?.topics ?? []

  const ready =
    (effSubject === NEW ? subjectName.trim() : effSubject) &&
    (topicId === NEW || effSubject === NEW || topics.length === 0 ? topicName.trim() : topicId) &&
    (kind === 'link' ? url.trim() : file)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    if (!student || !ready) return
    setBusy(true); setErr('')
    try {
      let sid = effSubject!
      if (sid === NEW) sid = (await api.createSubject(student.id, subjectName.trim())).id
      let tid = topicId
      if (!tid || tid === NEW || effSubject === NEW) tid = (await api.createTopic(sid, topicName.trim())).id
      if (kind === 'link') await api.addLink(tid, url.trim())
      else await api.addFile(tid, file!)
      await reloadSubjects()
      nav(`/assunto/${tid}/fontes`)
    } catch (x) {
      setErr((x as Error).message)
    } finally {
      setBusy(false)
    }
  }

  const askTopicName = effSubject === NEW || topicId === NEW || (subject && topics.length === 0)

  return (
    <form className="add" onSubmit={submit}>
      <h1 className="page-title">Adicionar conteúdo</h1>
      <p className="muted lead">Cada aula vai para uma gaveta: escolha a matéria e o assunto, depois o vídeo ou o arquivo.</p>

      <fieldset className="step">
        <legend className="label">Matéria</legend>
        <div className="chips">
          {subjects.map(s => (
            <button type="button" key={s.id} className="chip" aria-pressed={effSubject === s.id}
              onClick={() => { setSubjectId(s.id); setTopicId(null) }}>{s.name}</button>
          ))}
          <button type="button" className="chip" aria-pressed={effSubject === NEW} onClick={() => { setSubjectId(NEW); setTopicId(NEW) }}>
            <Plus size={14} aria-hidden /> Nova matéria
          </button>
        </div>
        {effSubject === NEW && (
          <input className="input" autoFocus placeholder="Ex.: Cálculo I" value={subjectName} onChange={e => setSubjectName(e.target.value)} aria-label="Nome da nova matéria" />
        )}
      </fieldset>

      {effSubject !== null && (
        <fieldset className="step">
          <legend className="label">Assunto</legend>
          {effSubject !== NEW && topics.length > 0 && (
            <div className="chips">
              {topics.map(t => (
                <button type="button" key={t.id} className="chip" aria-pressed={topicId === t.id} onClick={() => setTopicId(t.id)}>{t.name}</button>
              ))}
              <button type="button" className="chip" aria-pressed={topicId === NEW} onClick={() => setTopicId(NEW)}>
                <Plus size={14} aria-hidden /> Novo assunto
              </button>
            </div>
          )}
          {askTopicName && (
            <input className="input" placeholder="Ex.: Limites e continuidade" value={topicName} onChange={e => setTopicName(e.target.value)} aria-label="Nome do novo assunto" />
          )}
        </fieldset>
      )}

      <fieldset className="step">
        <legend className="label">Fonte</legend>
        <div className="seg" role="tablist">
          <button type="button" role="tab" aria-selected={kind === 'link'} onClick={() => setKind('link')}><Video size={16} aria-hidden /> Vídeo do YouTube</button>
          <button type="button" role="tab" aria-selected={kind === 'file'} onClick={() => setKind('file')}><FileUp size={16} aria-hidden /> PDF, DOCX ou TXT</button>
        </div>
        {kind === 'link' ? (
          <div className="with-icon">
            <Link2 size={16} aria-hidden />
            <input className="input" inputMode="url" placeholder="https://www.youtube.com/watch?v=…" value={url} onChange={e => setUrl(e.target.value)} aria-label="Link do vídeo" />
          </div>
        ) : (
          <button type="button" className="drop" onClick={() => fileRef.current?.click()}
            onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); setFile(e.dataTransfer.files[0] ?? null) }}>
            <FileUp size={22} aria-hidden />
            {file ? <strong>{file.name}</strong> : <span>Arraste o arquivo aqui ou toque para escolher</span>}
            <input ref={fileRef} type="file" hidden accept=".pdf,.docx,.txt,.md" onChange={e => setFile(e.target.files?.[0] ?? null)} />
          </button>
        )}
      </fieldset>

      {err && <p className="error-text" role="alert">{err}</p>}
      <div className="add-actions">
        <button className="btn btn-primary" disabled={!ready || busy}>{busy ? 'Enviando…' : 'Enviar para catalogar'}</button>
        <span className="muted small">Vídeos levam de 1 a 5 minutos. Você pode estudar outra coisa enquanto isso.</span>
      </div>
    </form>
  )
}
