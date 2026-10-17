/**
 * Rota POST /api/chat
 * Portada de backend/controllers/chat_controller.py (chat()).
 *
 * Processa um FormData com `message` e opcionalmente `file`.
 */

import { processMessage } from '@/lib/chat'
import { rateLimit, getClientIp } from '@/lib/ratelimit'
import { RATE_LIMIT_PER_MINUTE } from '@/lib/constants'
import { ValidationError, ChatCineError, errorPayload } from '@/lib/errors'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function POST(request) {
  // Rate limiting "10 per minute" (igual ao @limiter.limit do Flask)
  const ip = getClientIp(request)
  const { allowed, retryAfter } = rateLimit(`chat:${ip}`, RATE_LIMIT_PER_MINUTE)
  if (!allowed) {
    return Response.json(
      { error: 'Rate limit exceeded', message: `Tente novamente em ${retryAfter}s.` },
      { status: 429 }
    )
  }

  try {
    const formData = await request.formData()

    const message = (formData.get('message') || '').toString().trim()
    const file = formData.get('file')

    let filePayload = null
    if (file && typeof file === 'object' && 'arrayBuffer' in file && file.size > 0) {
      const buffer = Buffer.from(await file.arrayBuffer())
      filePayload = {
        buffer,
        mimetype: file.type || 'application/octet-stream',
        name: file.name,
      }
    }

    // O backend original usava um user_id fixo (1) pois o JWT está desabilitado
    // temporariamente para testes. Mantemos o mesmo comportamento.
    const userId = 1

    const response = await processMessage({
      message,
      file: filePayload,
      userId,
    })

    return Response.json(response, { status: 200 })
  } catch (error) {
    if (error instanceof ValidationError) {
      return Response.json(errorPayload(error), { status: error.status })
    }
    if (error instanceof ChatCineError) {
      return Response.json(errorPayload(error), { status: error.status })
    }
    return Response.json(
      { type: 'text', content: 'Desculpe, ocorreu um erro inesperado.' },
      { status: 500 }
    )
  }
}
