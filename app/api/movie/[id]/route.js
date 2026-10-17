/**
 * Rota GET /api/movie/:id
 * Portada de backend/controllers/chat_controller.py (get_movie_by_id).
 */

import { getMovieById } from '@/lib/movie'
import { cacheGet, cacheSet } from '@/lib/ratelimit'
import { CACHE_TIMEOUT_SECONDS } from '@/lib/constants'
import { ChatCineError, NotFoundError, errorPayload } from '@/lib/errors'

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
  const cacheKey = `movie:${movieId}`
  const cached = cacheGet(cacheKey)
  if (cached) {
    return Response.json(cached, { status: 200 })
  }

  try {
    const movie = await getMovieById(movieId)
    if (!movie) {
      throw new NotFoundError('Não consegui encontrar detalhes sobre este filme.')
    }

    const payload = { type: 'movie', content: movie }
    cacheSet(cacheKey, payload, CACHE_TIMEOUT_SECONDS)
    return Response.json(payload, { status: 200 })
  } catch (error) {
    if (error instanceof ChatCineError) {
      return Response.json(errorPayload(error), { status: error.status })
    }
    return Response.json(
      { type: 'text', content: 'Ocorreu um erro ao buscar informações do filme.' },
      { status: 500 }
    )
  }
}
