"""
DTOs para operações de chat.
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class ChatMessageDTO:
    """DTO para mensagem de chat."""
    role: str
    content: str | Dict[str, Any]
    
    @classmethod
    def from_model(cls, message) -> 'ChatMessageDTO':
        """Cria DTO a partir do modelo."""
        import json
        content = json.loads(message.content) if message.role == 'assistant' else message.content
        return cls(role=message.role, content=content)
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            'role': self.role,
            'content': self.content
        }


@dataclass
class ChatHistoryDTO:
    """DTO para histórico de chat."""
    messages: List[ChatMessageDTO]
    
    @classmethod
    def from_messages(cls, messages) -> 'ChatHistoryDTO':
        """Cria DTO a partir de lista de mensagens."""
        return cls(messages=[ChatMessageDTO.from_model(msg) for msg in messages])
    
    def to_list(self) -> List[dict]:
        """Converte para lista de dicionários."""
        return [msg.to_dict() for msg in self.messages]


@dataclass
class ChatRequestDTO:
    """DTO para requisição de chat."""
    message: Optional[str] = None
    file: Optional[Any] = None
    
    def has_content(self) -> bool:
        """Verifica se há conteúdo na requisição."""
        return bool(self.message or self.file)

