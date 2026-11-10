import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { LogOut, Plus, SquareLibrary } from 'lucide-react'
import { useStudent } from '../student'

export function Brand() {
  return (
    <span className="brand-name">
      <SquareLibrary size={20} strokeWidth={2} aria-hidden /> Acamp
    </span>
  )
}

export function Rail() {
  const { student, setStudent, subjects } = useStudent()
  const nav = useNavigate()
  return (
    <aside className="rail" aria-label="Matérias">
      <div className="brand">
        <NavLink to="/" style={{ textDecoration: 'none' }}><Brand /></NavLink>
        <button className="btn btn-ghost btn-sm" onClick={() => setStudent(null)} title="Trocar de perfil">
          {student?.name} <LogOut size={15} aria-hidden />
        </button>
      </div>

      <button className="btn btn-primary" onClick={() => nav('/adicionar')}>
        <Plus size={18} aria-hidden /> Adicionar conteúdo
      </button>

      {subjects.length === 0 ? (
        <p className="muted" style={{ fontSize: '.9rem', margin: 0 }}>
          Nenhuma matéria ainda. Adicione um vídeo ou PDF e crie a primeira gaveta.
        </p>
      ) : (
        subjects.map(sub => (
          <section key={sub.id} className="drawer">
            <div className="drawer-head">
              <span className="label">{sub.name}</span>
              <span className="label num">{sub.topics.length}</span>
            </div>
            {sub.topics.map(t => {
              const s = t.stats
              const pct = s && s.questions_total ? (s.questions_correct / s.questions_total) * 100 : 0
              return (
                <NavLink key={t.id} to={`/assunto/${t.id}`} className="topic-link">
                  <span>{t.name}</span>
                  <span className="label num" title="Questões acertadas">
                    {s ? `${s.questions_correct}/${s.questions_total}` : ''}
                  </span>
                  <span className="bar meter" aria-hidden><span style={{ width: `${pct}%` }} /></span>
                </NavLink>
              )
            })}
          </section>
        ))
      )}
    </aside>
  )
}

export default function Shell() {
  const { pathname } = useLocation()
  const { student, setStudent } = useStudent()
  return (
    <div className={`shell ${pathname === '/' ? 'home' : ''}`}>
      <header className="topbar">
        <NavLink to="/" style={{ textDecoration: 'none' }}><Brand /></NavLink>
        <div className="row">
          {pathname !== '/adicionar' && (
            <NavLink to="/adicionar" className="btn btn-sm btn-primary" aria-label="Adicionar conteúdo"><Plus size={16} aria-hidden /></NavLink>
          )}
          <button className="btn btn-ghost btn-sm" onClick={() => setStudent(null)} title="Trocar de perfil">
            {student?.name} <LogOut size={15} aria-hidden />
          </button>
        </div>
      </header>
      <Rail />
      <main className="main">
        <div className="main-inner"><Outlet /></div>
      </main>
    </div>
  )
}
