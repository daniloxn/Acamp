import type { SubTopic } from '../types'

export function SubtopicChips({ subtopics, selected, onChange }: {
  subtopics: SubTopic[]; selected: number[]; onChange: (ids: number[]) => void
}) {
  const toggle = (id: number) => onChange(selected.includes(id) ? selected.filter(x => x !== id) : [...selected, id])
  return (
    <div className="chips" role="group" aria-label="Tópicos">
      <button type="button" className="chip" aria-pressed={selected.length === 0} onClick={() => onChange([])}>Todos os tópicos</button>
      {subtopics.map(s => (
        <button type="button" key={s.id} className="chip" aria-pressed={selected.includes(s.id)} onClick={() => toggle(s.id)}>{s.name}</button>
      ))}
    </div>
  )
}
