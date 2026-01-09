"""
Repository para operações com chat.
"""
from typing import List, Optional
from ..models import ChatSession, ChatMessage
from .base import BaseRepository


class ChatSessionRepository(BaseRepository[ChatSession]):
    """Repository para gerenciar sessões de chat."""
    
    def __init__(self):
        super().__init__(ChatSession)
    
    def get_or_create_for_user(self, user_id: int = None, session_key: str = None) -> ChatSession:
        """
        Obtém ou cria uma sessão de chat.
        
        Args:
            user_id: ID do usuário (se autenticado)
            session_key: Chave da sessão (se anônimo)
        """
        if user_id:
            session = self.session.query(ChatSession)\
                .filter_by(user_id=user_id)\
                .order_by(ChatSession.created_at.desc())\
                .first()
            
            if not session:
                session = self.create(user_id=user_id)
        elif session_key:
            session = self.session.query(ChatSession)\
                .filter_by(session_key=session_key)\
                .first()
            
            if not session:
                session = self.create(session_key=session_key)
        else:
            # Cria nova sessão anônima
            import uuid
            new_session_key = str(uuid.uuid4())
            session = self.create(session_key=new_session_key)
        
        return session
    
    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Busca sessão por ID."""
        return self.session.query(ChatSession).filter_by(id=session_id).first()
    
    def get_user_sessions(self, user_id: int, limit: int = 10) -> List[ChatSession]:
        """Busca sessões de um usuário."""
        return self.session.query(ChatSession)\
            .filter_by(user_id=user_id)\
            .order_by(ChatSession.created_at.desc())\
            .limit(limit)\
            .all()


class ChatMessageRepository(BaseRepository[ChatMessage]):
    """Repository para gerenciar mensagens de chat."""
    
    def __init__(self):
        super().__init__(ChatMessage)
    
    def get_session_history(self, session_id: int, limit: int = 6) -> List[ChatMessage]:
        """Obtém histórico de mensagens de uma sessão."""
        messages = self.session.query(ChatMessage)\
            .filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()
        
        # Inverte para ordem cronológica
        messages.reverse()
        return messages
    
    def create_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        """Cria uma nova mensagem."""
        return self.create(
            session_id=session_id,
            role=role,
            content=content
        )

