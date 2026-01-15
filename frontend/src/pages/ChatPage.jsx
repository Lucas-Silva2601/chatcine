import { useState, useRef, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import { chatService } from '../services/chatService'
import ChatMessage from '../components/ChatMessage'
import MovieCard from '../components/MovieCard'
import '../styles/ChatPage.css'

function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState(null)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)
  
  const { user, logout } = useAuthStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() && !file) return

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await chatService.sendMessage(input, file)
      
      const aiMessage = {
        role: 'assistant',
        ...response,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, aiMessage])
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        type: 'text',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleLogout = () => {
    logout()
  }

  return (
    <div className="chat-page">
      <header className="chat-header">
        <div className="header-content">
          <h1>🎬 ChatCine</h1>
          <div className="user-info">
            <span>{user?.email}</span>
            <button onClick={handleLogout} className="btn-logout">
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="chat-main">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Bem-vindo ao ChatCine! 🍿</h2>
              <p>Converse sobre filmes, peça recomendações ou envie imagens!</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index}>
              {message.type === 'movie' ? (
                <MovieCard movie={message.content} />
              ) : (
                <ChatMessage message={message} />
              )}
            </div>
          ))}

          {loading && (
            <div className="loading-message">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="chat-footer">
        <form onSubmit={handleSubmit} className="chat-form">
          <div className="input-container">
            {file && (
              <div className="file-preview">
                <span>{file.name}</span>
                <button 
                  type="button" 
                  onClick={() => {
                    setFile(null)
                    if (fileInputRef.current) {
                      fileInputRef.current.value = ''
                    }
                  }}
                  className="btn-remove-file"
                >
                  ✕
                </button>
              </div>
            )}

            <div className="input-row">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*,audio/*"
                style={{ display: 'none' }}
              />
              
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="btn-attach"
                title="Anexar arquivo"
              >
                📎
              </button>

              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Digite sua mensagem..."
                disabled={loading}
                className="chat-input"
              />

              <button
                type="submit"
                disabled={loading || (!input.trim() && !file)}
                className="btn-send"
              >
                {loading ? '⏳' : '🚀'}
              </button>
            </div>
          </div>
        </form>
      </footer>
    </div>
  )
}

export default ChatPage

