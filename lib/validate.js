/**
 * Validação da resposta da IA.
 * Portado de backend/schemas.py (Marshmallow) — validação manual equivalente.
 */

import { ValidationError } from './errors'

/**
 * Valida a estrutura de uma resposta da IA.
 *
 * Regras (idênticas ao schema Marshmallow original):
 *  - `type` é obrigatório e deve ser 'movie' | 'recommendations' | 'text'
 *  - `content` é obrigatório e seu formato depende do `type`
 *
 * @param {object} data Objeto retornado pela IA
 * @returns {object} O mesmo objeto, se válido
 * @throws {ValidationError}
 */
export function validateAiResponse(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    throw new ValidationError('Resposta da IA em formato inválido.')
  }

  const { type, content } = data

  if (typeof type !== 'string' || !['movie', 'recommendations', 'text'].includes(type)) {
    throw new ValidationError('Tipo de resposta da IA inválido.')
  }

  if (content === undefined || content === null) {
    throw new ValidationError('Conteúdo da resposta da IA ausente.')
  }

  if (type === 'movie') {
    if (typeof content !== 'object' || Array.isArray(content)) {
      throw new ValidationError('Content deve ser um objeto para tipo "movie".')
    }
    if (typeof content.title !== 'string' || content.title.length < 1 || content.title.length > 200) {
      throw new ValidationError('Título do filme inválido.')
    }
    if (typeof content.year !== 'string' || content.year.length !== 4) {
      throw new ValidationError('Ano do filme inválido.')
    }
  } else if (type === 'recommendations') {
    if (!Array.isArray(content)) {
      throw new ValidationError('Content deve ser uma lista para tipo "recommendations".')
    }
    for (const item of content) {
      if (!item || typeof item.title !== 'string' || typeof item.year !== 'string') {
        throw new ValidationError('Item de recomendação inválido.')
      }
    }
  } else if (type === 'text') {
    if (typeof content !== 'string') {
      throw new ValidationError('Content deve ser uma string para tipo "text".')
    }
  }

  return data
}
