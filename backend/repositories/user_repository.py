"""
Repository para operações com usuários.
"""
from typing import Optional
from models import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository para gerenciar usuários."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
        return self.first(email=email.lower().strip())
    
    def email_exists(self, email: str) -> bool:
        """Verifica se um email já está cadastrado."""
        return self.get_by_email(email) is not None
    
    def create_user(self, email: str, password: str = None, **kwargs) -> User:
        """Cria um novo usuário."""
        return self.create(
            email=email.lower().strip(),
            password=password,
            **kwargs
        )

