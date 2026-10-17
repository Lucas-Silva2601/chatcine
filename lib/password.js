/**
 * Hash e verificação de senha com scrypt (node:crypto nativo).
 * Substitui werkzeug.security.generate_password_hash / check_password_hash.
 */

import crypto from 'node:crypto'

const SCRYPT_KEYLEN = 64
const SCRYPT_PARAMS = { N: 16384, r: 8, p: 1 }

/**
 * Gera um hash no formato `scrypt:<N>:<r>:<p>:<salt>:<hash>` (hex).
 * @param {string} password Senha em texto puro
 * @returns {string}
 */
export function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex')
  const { N, r, p } = SCRYPT_PARAMS
  const hash = crypto
    .scryptSync(password, salt, SCRYPT_KEYLEN, { N, r, p })
    .toString('hex')
  return `scrypt:${N}:${r}:${p}:${salt}:${hash}`
}

/**
 * Verifica uma senha contra um hash gerado por {@link hashPassword}.
 * @param {string} password Senha em texto puro
 * @param {string} stored Hash armazenado
 * @returns {boolean}
 */
export function verifyPassword(password, stored) {
  if (!stored || typeof stored !== 'string') return false

  const parts = stored.split(':')
  if (parts.length !== 6 || parts[0] !== 'scrypt') return false

  const [, N, r, p, salt, hash] = parts
  const expected = Buffer.from(hash, 'hex')
  const actual = crypto.scryptSync(password, salt, expected.length, {
    N: Number(N),
    r: Number(r),
    p: Number(p),
  })
  return crypto.timingSafeEqual(expected, actual)
}
