import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import VerifyPage from './pages/VerifyPage.jsx'
import LoginPage from './pages/LoginPage.jsx'

function App() {
  return (
    <div>
      <h1>Google Drive Reference</h1>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify" element={<VerifyPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </div>
  )
}

export default App