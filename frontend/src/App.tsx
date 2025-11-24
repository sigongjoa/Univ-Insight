import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import ResearchPage from './pages/ResearchPage'
import ReportPage from './pages/ReportPage'
import ProfilePage from './pages/ProfilePage'
import PlanBPage from './pages/PlanBPage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/research" element={<ResearchPage />} />
        <Route path="/research/:paperId/plan-b" element={<PlanBPage />} />
        <Route path="/reports" element={<ReportPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
