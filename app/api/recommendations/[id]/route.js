/**
 * Rota GET /api/recommendations/:id
 * Portada de backend/controllers/chat_controller.py (get_recommendations).
 */

import { getRecommendations } from '@/lib/movie'
import { cacheGet, cacheSet } from '@/lib/ratelimit'
import { CACHE_TIMEOUT_SECONDS } from '@/lib/constants'
import { ChatCineError, errorPayload } from '@/lib/errors'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET(request, { params }) {
  const { id } = await params
  const movieId = Number(id)

  if (!Number.isInteger(movieId) || movieId <= 0) {
    return Response.json(
      { type: 'text', content: 'ID de filme inválido.' },
      { status: 400 }
    )
  }

  // Cache de 1 hora (equivalente a @cache.cached(timeout=3600))
  const cacheKey = `recs:${movieId}`
  const cached = cacheGet(cacheKey)
  if (cached) {
    return Response.json(cached, { status: 200 })
  }

  try {
    const recommendations = await getRecommendations(movieId)
    const payload = { type: 'recommendations', content: recommendations }
    cacheSet(cacheKey, payload, CACHE_TIMEOUT_SECONDS)
    return Response.json(payload, { status: 200 })
  } catch (error) {
    if (error instanceof ChatCineError) {
      return Response.json(errorPayload(error), { status: error.status })
    }
    return Response.json(
      { type: 'text', content: 'Ocorreu um erro ao buscar recomendações.' },
      { status: 500 }
    )
  }
}
