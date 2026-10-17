import './globals.css'

// Estilos globais da aplicação (mantidos da versão anterior)
import '@/styles/index.css'
import '@/styles/ChatPage.css'
import '@/styles/ChatMessage.css'
import '@/styles/MovieCard.css'
import '@/styles/LoginPage.css'

export const metadata = {
  title: 'ChatCine - Chat sobre Filmes com IA',
  description:
    'Chat interativo sobre filmes com inteligência artificial: recomendações, busca na TMDB e análise de imagens.',
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
