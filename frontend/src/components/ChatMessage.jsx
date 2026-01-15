import '../styles/ChatMessage.css'

function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'ai-message'}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-text">
          {message.content}
        </div>
        <div className="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage

