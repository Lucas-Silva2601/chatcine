"""
Exceções customizadas da aplicação.
"""
from typing import Optional


class ChatCineException(Exception):
    """Exceção base da aplicação."""
    message: str = "Ocorreu um erro na aplicação."
    status_code: int = 500
    
    def __init__(self, message: Optional[str] = None, status_code: Optional[int] = None):
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class ValidationError(ChatCineException):
    """Erro de validação de dados."""
    message = "Dados inválidos fornecidos."
    status_code = 400


class NotFoundError(ChatCineException):
    """Recurso não encontrado."""
    message = "Recurso não encontrado."
    status_code = 404


class AuthenticationError(ChatCineException):
    """Erro de autenticação."""
    message = "Credenciais inválidas."
    status_code = 401


class AuthorizationError(ChatCineException):
    """Erro de autorização."""
    message = "Acesso não autorizado."
    status_code = 403


class ExternalAPIError(ChatCineException):
    """Erro ao comunicar com API externa."""
    message = "Erro ao comunicar com serviço externo."
    status_code = 502


class DatabaseError(ChatCineException):
    """Erro de banco de dados."""
    message = "Erro ao acessar banco de dados."
    status_code = 500

