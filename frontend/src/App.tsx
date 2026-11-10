import { Navigate, Route, Routes } from 'react-router-dom'
import { StudentProvider, useStudent } from './student'
import Shell from './components/Shell'
import Profiles from './pages/Profiles'
import Home from './pages/Home'
import AddContent from './pages/AddContent'
import TopicPage from './pages/Topic'

function Routed() {
  const { student } = useStudent()
  if (!student) return <Profiles />
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route index element={<Home />} />
        <Route path="adicionar" element={<AddContent />} />
        <Route path="assunto/:topicId/:tab?" element={<TopicPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <StudentProvider>
      <Routed />
    </StudentProvider>
  )
}
