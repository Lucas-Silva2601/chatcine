/**
 * Tokens JWT (HS256) usando apenas node:crypto.
 * Portado de backend/controllers/auth_controller.py (Flask-JWT-Extended).
 *
 * Formato compatível com o esperado pelo frontend: o access token é
 * verificado nas rotas protegidas e o payload expõe `sub` (id do usuário).
 */

import crypto from 'node:crypto'

const DEFAULT_ACCESS_TTL = 3600 // 1 hora
const DEFAULT_REFRESH_TTL = 2592000 // 30 dias

function secret() {
  return process.env.JWT_SECRET_KEY || process.env.SECRET_KEY || 'dev-secret-key-change-in-production'
}

function b64url(input) {
  return Buffer.from(input).toString('base64url')
}

function sign(payload, ttlSeconds) {
  const header = b64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const now = Math.floor(Date.now() / 1000)
  const body = b64url(
    JSON.stringify({ ...payload, iat: now, exp: now + ttlSeconds })
  )
  const signature = crypto
    .createHmac('sha256', secret())
    .update(`${header}.${body}`)
    .digest('base64url')
  return `${header}.${body}.${signature}`
}

/**
 * Cria um access token a partir do id do usuário.
 * @param {string|number} userId
 * @returns {string}
 */
export function createAccessToken(userId) {
  return sign({ sub: String(userId), type: 'access' }, DEFAULT_ACCESS_TTL)
}

/**
 * Cria um refresh token a partir do id do usuário.
 * @param {string|number} userId
 * @returns {string}
 */
export function createRefreshToken(userId) {
  return sign({ sub: String(userId), type: 'refresh' }, DEFAULT_REFRESH_TTL)
}

/**
 * Verifica e decodifica um token.
 * @param {string} token
 * @returns {{ sub: string, type: string, exp: number }|null} Payload ou null se inválido
 */
export function verifyToken(token) {
  if (!token || typeof token !== 'string') return null

  const parts = token.split('.')
  if (parts.length !== 3) return null

  const [header, body, signature] = parts
  const expected = crypto
    .createHmac('sha256', secret())
    .update(`${header}.${body}`)
    .digest('base64url')

  // Comparação em tempo constante
  const sigBuf = Buffer.from(signature)
  const expBuf = Buffer.from(expected)
  if (sigBuf.length !== expBuf.length) return null
  if (!crypto.timingSafeEqual(sigBuf, expBuf)) return null

  try {
    const payload = JSON.parse(Buffer.from(body, 'base64url').toString('utf8'))
    if (typeof payload.exp === 'number' && payload.exp < Math.floor(Date.now() / 1000)) {
      return null // expirado
    }
    return payload
  } catch {
    return null
  }
}

/**
 * Extrai o id do usuário de um header Authorization Bearer.
 * @param {Request|Headers|{get?:Function}|string|null} reqOrHeader
 * @returns {string|null} id do usuário ou null se não autenticado
 */
export function getUserIdFromRequest(reqOrHeader) {
  let auth = null
  if (!reqOrHeader) return null

  if (typeof reqOrHeader === 'string') {
    auth = reqOrHeader
  } else if (typeof reqOrHeader.headers?.get === 'function') {
    auth = reqOrHeader.headers.get('authorization')
  } else if (typeof reqOrHeader.get === 'function') {
    auth = reqOrHeader.get('authorization')
  }

  if (!auth || !auth.startsWith('Bearer ')) return null

  const payload = verifyToken(auth.slice(7).trim())
  return payload?.sub ?? null
}
