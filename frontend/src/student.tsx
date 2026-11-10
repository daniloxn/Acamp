import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { api } from './api'
import type { Student, Subject } from './types'

const KEY = 'acamp.student'

type Ctx = {
  student: Student | null
  setStudent: (s: Student | null) => void
  subjects: Subject[]
  loaded: boolean
  reloadSubjects: () => Promise<void>
}

const StudentCtx = createContext<Ctx>(null!)

function readStored(): Student | null {
  try { return JSON.parse(localStorage.getItem(KEY) || 'null') } catch { return null }
}

export function StudentProvider({ children }: { children: ReactNode }) {
  const [student, setStudentState] = useState<Student | null>(readStored)
  const [subjects, setSubjects] = useState<Subject[] | null>(null)

  const setStudent = (s: Student | null) => {
    setSubjects(null)
    setStudentState(s)
    try { s ? localStorage.setItem(KEY, JSON.stringify(s)) : localStorage.removeItem(KEY) } catch { /* sem storage */ }
  }

  const reloadSubjects = useCallback(async () => {
    if (!student) return setSubjects([])
    setSubjects(await api.subjects(student.id))
  }, [student])

  useEffect(() => { reloadSubjects().catch(() => setSubjects([])) }, [reloadSubjects])

  const value = { student, setStudent, subjects: subjects ?? [], loaded: subjects !== null, reloadSubjects }
  return <StudentCtx.Provider value={value}>{children}</StudentCtx.Provider>
}

export const useStudent = () => useContext(StudentCtx)
