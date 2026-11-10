import { useEffect, useState, type FormEvent } from 'react'
import { ArrowRight } from 'lucide-react'
import { api } from '../api'
import { useStudent } from '../student'
import { Brand } from '../components/Shell'
import type { Student } from '../types'

export default function Profiles() {
  const { setStudent } = useStudent()
  const [students, setStudents] = useState<Student[] | null>(null)
  const [name, setName] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    api.students().then(setStudents).catch(() => { setStudents([]); setErr('Não consegui falar com o servidor. Ele está rodando?') })
  }, [])

  const create = async (e: FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    try { setStudent(await api.createStudent(name.trim())) } catch (x) { setErr((x as Error).message) }
  }

  return (
    <div className="profiles">
      <Brand />
      <h1 className="page-title">Quem vai estudar agora?</h1>
      <div className="profile-list">
        {students?.map(s => (
          <button key={s.id} className="ficha profile" onClick={() => setStudent(s)}>
            <span className="profile-name">{s.name}</span>
            <span className="profile-go">Abrir fichário <ArrowRight size={16} aria-hidden /></span>
          </button>
        ))}
      </div>
      <form className="profile-new" onSubmit={create}>
        <label className="label" htmlFor="new-name">Novo perfil</label>
        <div className="row">
          <input id="new-name" className="input" placeholder="Seu nome" value={name} onChange={e => setName(e.target.value)} />
          <button className="btn btn-primary" disabled={!name.trim()}>Criar</button>
        </div>
        {err && <p className="error-text" role="alert">{err}</p>}
      </form>
    </div>
  )
}
