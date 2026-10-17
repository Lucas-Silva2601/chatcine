/**
 * Serviço para integração com a API TMDB.
 * Portado de backend/services/movie_service.py — usa `fetch` nativo.
 */

import { TMDB_BASE_URL, TMDB_IMAGE_BASE_URL } from './constants'
import { ExternalAPIError } from './errors'

export function isMovieConfigured() {
  return Boolean(process.env.TMDB_API_KEY)
}

function buildPosterUrl(posterPath) {
  return posterPath ? `${TMDB_IMAGE_BASE_URL}${posterPath}` : null
}

async function tmdbGet(pathname, params) {
  const apiKey = process.env.TMDB_API_KEY
  const url = new URL(`${TMDB_BASE_URL}${pathname}`)
  url.searchParams.set('api_key', apiKey)
  url.searchParams.set('language', 'pt-BR')
  for (const [key, value] of Object.entries(params || {})) {
    url.searchParams.set(key, value)
  }

  let response
  try {
    response = await fetch(url.toString(), { next: { revalidate: 3600 } })
  } catch (error) {
    throw new ExternalAPIError(`Erro ao buscar no TMDB: ${error.message}`)
  }

  if (!response.ok) {
    throw new ExternalAPIError(`Erro ao buscar no TMDB: HTTP ${response.status}`)
  }
  return response.json()
}

/** Monta o objeto Movie no mesmo formato do MovieDTO.to_dict(). */
function buildMovie(item, mediaType) {
  const title = mediaType === 'movie' ? item.title : item.name || 'Desconhecido'
  const releaseDate = mediaType === 'movie' ? item.release_date : item.first_air_date || ''
  const year = releaseDate ? releaseDate.slice(0, 4) : 'N/A'

  return {
    id: item.id,
    title,
    year,
    poster_url: buildPosterUrl(item.poster_path),
    genres:
      (item.genres || []).map((g) => g.name).join(', ') || 'Não disponível',
    rating: `${(item.vote_average || 0).toFixed(1)}/10`,
    overview: item.overview || 'Sinopse não disponível.',
    imdb_id: item.external_ids?.imdb_id || null,
    media_type: mediaType,
  }
}

/**
 * Busca detalhes de um filme pelo ID.
 * @returns {Promise<object|null>} Movie ou null se não encontrado
 */
export async function getMovieById(movieId, mediaType = 'movie') {
  if (!isMovieConfigured()) {
    throw new ExternalAPIError('TMDB_API_KEY não configurada.')
  }

  const item = await tmdbGet(`/${mediaType}/${movieId}`, {
    append_to_response: 'external_ids',
  })
  return buildMovie(item, mediaType)
}

/**
 * Busca um filme pelo nome e retorna os detalhes do primeiro resultado.
 * @returns {Promise<object|null>} Movie ou null se não encontrado
 */
export async function searchMovie(movieName) {
  if (!isMovieConfigured()) {
    throw new ExternalAPIError('TMDB_API_KEY não configurada.')
  }

  const data = await tmdbGet('/search/multi', { query: movieName })
  const results = data.results || []
  if (results.length === 0) return null

  const first = results[0]
  const mediaType = first.media_type
  if (mediaType !== 'movie' && mediaType !== 'tv') return null

  return getMovieById(first.id, mediaType)
}

/**
 * Busca recomendações baseadas em um filme.
 * @returns {Promise<object[]>} Lista de recomendações
 */
export async function getRecommendations(movieId, mediaType = 'movie') {
  if (!isMovieConfigured()) {
    throw new ExternalAPIError('TMDB_API_KEY não configurada.')
  }

  const data = await tmdbGet(`/${mediaType}/${movieId}/recommendations`, { page: 1 })

  return (data.results || []).slice(0, 5).map((rec) => {
    const recMediaType = rec.media_type || mediaType
    return {
      id: rec.id,
      title: recMediaType === 'movie' ? rec.title : rec.name || 'Desconhecido',
      year: (rec.release_date || rec.first_air_date || '').slice(0, 4),
      poster_url: buildPosterUrl(rec.poster_path),
    }
  })
}
