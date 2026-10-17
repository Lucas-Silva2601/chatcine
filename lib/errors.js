/**
 * Erros customizados da aplicação (portado de backend/core/exceptions.py).
 *
 * Mantém a mesma semântica de status code usada no backend Flask para que o
 * contrato de respostas HTTP com o frontend não mude.
 */

export class ChatCineError extends Error {
  constructor(message, status = 500, type = 'text') {
    super(message)
    this.name = 'ChatCineError'
    this.status = status
    this.type = type
  }
}

export class ValidationError extends ChatCineError {
  constructor(message = 'Dados inválidos fornecidos.', type = 'error') {
    super(message, 400, type)
    this.name = 'ValidationError'
  }
}

export class NotFoundError extends ChatCineError {
  constructor(message = 'Recurso não encontrado.') {
    super(message, 404, 'text')
    this.name = 'NotFoundError'
  }
}

export class AuthenticationError extends ChatCineError {
  constructor(message = 'Credenciais inválidas.') {
    super(message, 401, 'text')
    this.name = 'AuthenticationError'
  }
}

export class AuthorizationError extends ChatCineError {
  constructor(message = 'Acesso não autorizado.') {
    super(message, 403, 'text')
    this.name = 'AuthorizationError'
  }
}

export class ExternalAPIError extends ChatCineError {
  constructor(message = 'Erro ao comunicar com serviço externo.', type = 'text') {
    super(message, 502, type)
    this.name = 'ExternalAPIError'
  }
}

export class DatabaseError extends ChatCineError {
  constructor(message = 'Erro ao acessar banco de dados.') {
    super(message, 500, 'text')
    this.name = 'DatabaseError'
  }
}

/** Converte um erro em payload JSON padronizado para respostas de chat. */
export function errorPayload(error) {
  if (error instanceof ValidationError) {
    return { type: error.type, content: error.message }
  }
  if (error instanceof ChatCineError) {
    return { type: 'text', content: error.message }
  }
  return { type: 'text', content: 'Desculpe, ocorreu um erro inesperado.' }
}
