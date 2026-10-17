/**
 * Rate limiting e cache em memória.
 * Portes leves de Flask-Limiter ("10 per minute") e Flask-Caching (1 hora).
 */

// ---------------------------------------------------------------------------
// Rate limiter (janela deslizante simples por IP + rota)
// ---------------------------------------------------------------------------
const buckets = new Map()
const WINDOW_MS = 60_000

/**
 * Limita requisições por janela de 1 minuto.
 * @param {string} key Identificador único (ex: `${rota}:${ip}`)
 * @param {number} max Máximo de requisições na janela
 * @returns {{ allowed: boolean, remaining: number, retryAfter: number }}
 */
export function rateLimit(key, max = 10) {
  const now = Date.now()
  const entry = buckets.get(key) || []

  // Remove timestamps fora da janela
  const recent = entry.filter((ts) => now - ts < WINDOW_MS)

  if (recent.length >= max) {
    const oldest = recent[0]
    const retryAfter = Math.ceil((WINDOW_MS - (now - oldest)) / 1000)
    buckets.set(key, recent)
    return { allowed: false, remaining: 0, retryAfter }
  }

  recent.push(now)
  buckets.set(key, recent)
  return { allowed: true, remaining: max - recent.length, retryAfter: 0 }
}

/** Obtém o IP do cliente a partir do request (ou proxy headers). */
export function getClientIp(request) {
  const forwarded = request.headers.get('x-forwarded-for')
  if (forwarded) return forwarded.split(',')[0].trim()
  return request.headers.get('x-real-ip') || '127.0.0.1'
}

// ---------------------------------------------------------------------------
// Cache em memória com TTL (port de Flask-Caching SimpleCache)
// ---------------------------------------------------------------------------
const cacheStore = new Map()

/**
 * Lê um valor do cache.
 * @param {string} key
 * @returns {*} valor ou undefined
 */
export function cacheGet(key) {
  const entry = cacheStore.get(key)
  if (!entry) return undefined
  if (Date.now() > entry.expires) {
    cacheStore.delete(key)
    return undefined
  }
  return entry.value
}

/**
 * Grava um valor no cache com TTL em segundos.
 * @param {string} key
 * @param {*} value
 * @param {number} ttlSeconds
 */
export function cacheSet(key, value, ttlSeconds = 3600) {
  cacheStore.set(key, { value, expires: Date.now() + ttlSeconds * 1000 })
}
