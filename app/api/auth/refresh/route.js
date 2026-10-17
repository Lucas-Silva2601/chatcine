/**
 * Rota POST /api/auth/refresh
 * Portada de backend/controllers/auth_controller.py (refresh).
 */

import { verifyToken, createAccessToken } from '@/lib/jwt'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function POST(request) {
  try {
    const auth = request.headers.get('authorization')
    if (!auth || !auth.startsWith('Bearer ')) {
      return Response.json({ error: 'Token de refresh ausente' }, { status: 401 })
    }

    const payload = verifyToken(auth.slice(7).trim())
    if (!payload || payload.type !== 'refresh') {
      return Response.json({ error: 'Token de refresh inválido' }, { status: 401 })
    }

    return Response.json({ token: createAccessToken(payload.sub) })
  } catch (error) {
    return Response.json({ error: String(error.message || error) }, { status: 500 })
  }
}
