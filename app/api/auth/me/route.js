/**
 * Rota GET /api/auth/me
 * Portada de backend/controllers/auth_controller.py (get_current_user).
 */

import { users } from '@/lib/db'
import { getUserIdFromRequest } from '@/lib/jwt'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET(request) {
  try {
    const userId = getUserIdFromRequest(request)
    if (!userId) {
      return Response.json({ error: 'Não autenticado' }, { status: 401 })
    }

    const user = users.findById(userId)
    if (!user) {
      return Response.json({ error: 'Usuário não encontrado' }, { status: 404 })
    }

    return Response.json({
      user: {
        id: user.id,
        email: user.email,
        profile_pic_url: user.profile_pic_url,
        plan_status: user.plan_status,
      },
    })
  } catch (error) {
    return Response.json({ error: String(error.message || error) }, { status: 500 })
  }
}
