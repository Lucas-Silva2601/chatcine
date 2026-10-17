/**
 * Rota POST /api/auth/register
 * Portada de backend/controllers/auth_controller.py (register).
 */

import { users } from '@/lib/db'
import { hashPassword } from '@/lib/password'
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

    if (password.length < 6) {
      return Response.json(
        { error: 'A senha deve ter pelo menos 6 caracteres' },
        { status: 400 }
      )
    }

    if (users.findByEmail(email)) {
      return Response.json({ error: 'Este email já está registrado' }, { status: 409 })
    }

    const user = users.create({ email, passwordHash: hashPassword(password) })

    return Response.json(
      {
        message: 'Conta criada com sucesso',
        token: createAccessToken(user.id),
        refresh_token: createRefreshToken(user.id),
        user: {
          id: user.id,
          email: user.email,
          profile_pic_url: user.profile_pic_url,
        },
      },
      { status: 201 }
    )
  } catch (error) {
    return Response.json({ error: String(error.message || error) }, { status: 500 })
  }
}
