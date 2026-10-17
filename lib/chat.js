/**
 * Serviço de lógica de negócio para chat.
 * Portado de backend/services/chat_service.py.
 */

import { generateResponse, cleanJsonResponse } from './ai'
import { searchMovie } from './movie'
import { chatSessions, chatMessages } from './db'
import { validateAiResponse } from './validate'
import {
  CHAT_HISTORY_LIMIT,
  MESSAGE_ROLE_USER,
  MESSAGE_ROLE_ASSISTANT,
  ALLOWED_FILE_TYPES,
} from './constants'
import { ValidationError, ExternalAPIError } from './errors'

/**
 * Processa uma mensagem do usuário e retorna a resposta da IA.
 *
 * @param {object} params
 * @param {string} [params.sessionId] Sessão existente (opcional)
 * @param {string} [params.message] Mensagem de texto
 * @param {{ buffer: Buffer, mimetype: string, name?: string }} [params.file] Arquivo opcional
 * @param {string|number} [params.userId] Usuário autenticado (opcional)
 * @returns {Promise<object>} Resposta da IA (type/content, possivelmente _session_id)
 */
export async function processMessage({ sessionId, message, file, userId } = {}) {
  const hasContent = Boolean((message && message.trim()) || file)
  if (!hasContent) {
    throw new ValidationError('Mensagem ou arquivo vazio.')
  }

  // Obtém ou cria sessão
  let session
  if (sessionId) {
    session = chatSessions.findById(sessionId)
    if (!session) {
      session = chatSessions.getOrCreate({ userId })
    }
  } else {
    session = chatSessions.getOrCreate({ userId })
  }

  const newSessionId = !sessionId && session ? session.id : null

  // Processa arquivo, se fornecido
  let userMessage = message || ''
  let imageFile = null

  if (file) {
    const mimetype = file.mimetype || ''
    if (!ALLOWED_FILE_TYPES.includes(mimetype)) {
      throw new ValidationError('Tipo de arquivo não suportado.')
    }
    imageFile = file
  }

  // Salva mensagem do usuário
  chatMessages.create({
    sessionId: session.id,
    role: MESSAGE_ROLE_USER,
    content: userMessage,
  })

  // Histórico para dar contexto à IA
  const history = getSessionHistory(session.id)

  // Gera resposta da IA
  const aiResponseText = await generateResponse(userMessage, {
    hasImage: Boolean(imageFile),
    history,
  })

  // Limpa e valida JSON
  const jsonStr = cleanJsonResponse(aiResponseText)
  if (!jsonStr) {
    throw new ExternalAPIError('Problema ao formatar resposta da IA.')
  }

  let parsed
  try {
    parsed = validateAiResponse(JSON.parse(jsonStr))
  } catch (error) {
    if (error instanceof ValidationError) throw error
    throw new ValidationError(`Erro ao validar resposta da IA: ${error.message}`)
  }

  // Salva resposta da IA
  chatMessages.create({
    sessionId: session.id,
    role: MESSAGE_ROLE_ASSISTANT,
    content: JSON.stringify(parsed),
  })

  // Se identificou filme, busca detalhes reais na TMDB
  if (parsed.type === 'movie' && parsed.content) {
    const movieTitle = parsed.content.title
    if (movieTitle) {
      const movieDetails = await searchMovie(movieTitle)
      if (movieDetails) {
        const result = { type: 'movie', content: movieDetails }
        chatMessages.create({
          sessionId: session.id,
          role: MESSAGE_ROLE_ASSISTANT,
          content: JSON.stringify(result),
        })
        return result
      }
      const errorResponse = {
        type: 'text',
        content: `Pensei que fosse '${movieTitle}', mas não encontrei detalhes.`,
      }
      chatMessages.create({
        sessionId: session.id,
        role: MESSAGE_ROLE_ASSISTANT,
        content: JSON.stringify(errorResponse),
      })
      return errorResponse
    }
  }

  const result = { ...parsed }
  if (newSessionId) result._session_id = newSessionId
  return result
}

/**
 * Histórico de chat formatado para o prompt da IA.
 * @param {string|number} sessionId
 * @returns {Array<{role: string, content: any}>}
 */
export function getSessionHistory(sessionId) {
  const messages = chatMessages.getSessionHistory(sessionId, CHAT_HISTORY_LIMIT)
  return messages.map((msg) => ({
    role: msg.role,
    content:
      msg.role === MESSAGE_ROLE_ASSISTANT ? safeParse(msg.content) : msg.content,
  }))
}

function safeParse(content) {
  try {
    return JSON.parse(content)
  } catch {
    return content
  }
}
