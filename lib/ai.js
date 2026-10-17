/**
 * Serviço para integração com a API de IA (Ollama Cloud).
 * Usa o endpoint compatível com OpenAI em https://ollama.com/v1.
 * A autenticação é feita via `Authorization: Bearer $OLLAMA_API_KEY`.
 */

import { SYSTEM_PROMPT, OLLAMA_BASE_URL, OLLAMA_MODEL } from './constants'
import { ExternalAPIError } from './errors'

const OLLAMA_URL = `${OLLAMA_BASE_URL}/v1/chat/completions`

export function isAiConfigured() {
  return Boolean(process.env.OLLAMA_API_KEY)
}

/**
 * Gera uma resposta da IA (string JSON) para a mensagem informada.
 *
 * @param {string} userMessage Mensagem do usuário
 * @param {{ hasImage?: boolean, history?: Array<{role: string, content: any}> }} options
 * @returns {Promise<string>} Resposta da IA como string
 */
export async function generateResponse(userMessage, { hasImage = false, history = [] } = {}) {
  const apiKey = process.env.OLLAMA_API_KEY
  if (!apiKey) {
    throw new ExternalAPIError('OLLAMA_API_KEY não configurada.')
  }

  const messages = [{ role: 'system', content: SYSTEM_PROMPT }]

  // Histórico de conversa (últimas 6 mensagens), como no original
  for (const message of history.slice(-6)) {
    if (message.role === 'user') {
      messages.push({ role: 'user', content: message.content })
    } else if (message.role === 'assistant') {
      let content = message.content ?? ''
      if (typeof content === 'object') content = JSON.stringify(content)
      messages.push({ role: 'assistant', content: String(content) })
    }
  }

  // Mensagem atual
  if (hasImage) {
    messages.push({
      role: 'user',
      content: `${userMessage}\n\n[O usuário enviou uma imagem. Descreva o que você vê ou identifique o filme baseado na descrição fornecida.]`,
    })
  } else {
    messages.push({ role: 'user', content: userMessage })
  }

  let response
  try {
    response = await fetch(OLLAMA_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: OLLAMA_MODEL,
        messages,
        temperature: 0.7,
        max_tokens: 2048,
      }),
    })
  } catch (error) {
    throw new ExternalAPIError(`Erro na API do Ollama: ${error.message}`)
  }

  if (!response.ok) {
    const detail = await response.text().catch(() => '')
    throw new ExternalAPIError(`Erro na API do Ollama: HTTP ${response.status} ${detail}`)
  }

  const data = await response.json()
  const content = data?.choices?.[0]?.message?.content
  if (!content) {
    throw new ExternalAPIError('Resposta vazia da API do Ollama.')
  }
  return content.trim()
}

/**
 * Limpa e extrai um objeto JSON de uma string (portado de clean_json_response).
 *
 * @param {string} text String que pode conter JSON (ex: cercado por ```json)
 * @returns {string|null} String JSON válida ou null
 */
export function cleanJsonResponse(text) {
  if (typeof text !== 'string') return null

  // Remove blocos de código markdown
  if (text.includes('```json')) {
    text = text.split('```json')[1].trim()
  }
  if (text.includes('```')) {
    text = text.split('```')[0].trim()
  }

  const start = text.indexOf('{')
  if (start === -1) return null

  let open = 0
  let end = -1
  for (let i = start; i < text.length; i++) {
    if (text[i] === '{') open++
    else if (text[i] === '}') {
      open--
      if (open === 0) {
        end = i
        break
      }
    }
  }

  if (end === -1) return null

  const candidate = text.slice(start, end + 1)
  try {
    JSON.parse(candidate) // valida
    return candidate
  } catch {
    return null
  }
}
