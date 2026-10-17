/**
 * Rota POST /api/auth/login
 * Portada de backend/controllers/auth_controller.py (login).
 */

import { users } from '@/lib/db'
import { verifyPassword } from '@/lib/password'
import { createAccessToken, createRefreshToken } from '@/lib/jwt'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function POST(request) {
  try {
    const data = await request.json().catch(() => null)
    if (!data) {
      return Response.json({ error: 'No data provided' }, { status: 400 })
    }

    const email = String(data.email || '').trim().toLowerCase()
    const password = String(data.password || '')

    if (!email || !password) {
      return Response.json({ error: 'Email e senha são obrigatórios' }, { status: 400 })
    }

    const user = users.findByEmail(email)
    if (!user || !user.password_hash || !verifyPassword(password, user.password_hash)) {
      return Response.json({ error: 'Email ou senha inválidos' }, { status: 401 })
    }

    return Response.json({
      message: 'Login realizado com sucesso',
      token: createAccessToken(user.id),
      refresh_token: createRefreshToken(user.id),
      user: {
        id: user.id,
        email: user.email,
        profile_pic_url: user.profile_pic_url,
      },
    })
  } catch (error) {
    return Response.json({ error: String(error.message || error) }, { status: 500 })
  }
}
