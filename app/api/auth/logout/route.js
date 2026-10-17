/**
 * Rota POST /api/auth/logout
 * Portada de backend/controllers/auth_controller.py (logout).
 * No backend original o logout era apenas uma confirmação (token removido no cliente).
 */

import { getUserIdFromRequest } from '@/lib/jwt'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function POST(request) {
  try {
    // No Flask original esta rota exigia @jwt_required(). Mantemos a checagem
    // para bater com o mesmo contrato, mas o token é invalidado no cliente.
    const userId = getUserIdFromRequest(request)
    if (!userId) {
      return Response.json({ error: 'Não autenticado' }, { status: 401 })
    }

    return Response.json({ message: 'Logout realizado com sucesso' })
  } catch (error) {
    return Response.json({ error: String(error.message || error) }, { status: 500 })
  }
}
