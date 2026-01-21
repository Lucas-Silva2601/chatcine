import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ChatPage from './pages/ChatPage'
import './styles/App.css'

function App() {
  // Login desabilitado temporariamente para testes
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ChatPage />} />
      </Routes>
    </Router>
  )
}

export default App

