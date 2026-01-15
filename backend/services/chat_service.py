"""
Serviço de lógica de negócio para chat.
"""
import json
from typing import List, Dict, Any, Optional

from repositories.chat_repository import ChatSessionRepository, ChatMessageRepository
from dto.chat_dto import ChatRequestDTO, ChatHistoryDTO, ChatMessageDTO
from dto.movie_dto import MovieDTO
from services.ai_service import AIService
from services.movie_service import MovieService
from services.speech_service import SpeechService
from schemas import validate_ai_response
from core.constants import CHAT_HISTORY_LIMIT, MESSAGE_ROLE_USER, MESSAGE_ROLE_ASSISTANT
from core.exceptions import ValidationError, ExternalAPIError


class ChatService:
    """Serviço para gerenciar conversas de chat."""
    
    def __init__(self):
        """Inicializa o serviço de chat."""
        self.session_repo = ChatSessionRepository()
        self.message_repo = ChatMessageRepository()
        self.ai_service = AIService()
        self.movie_service = MovieService()
        try:
            self.speech_service = SpeechService()
        except ExternalAPIError:
            self.speech_service = None
    
    def process_message(
        self,
        session_id: int = None,
        request: ChatRequestDTO = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário e retorna resposta da IA.
        
        Args:
            session_id: ID da sessão (se já existe)
            request: DTO com dados da requisição
            user_id: ID do usuário (se autenticado, opcional)
            
        Returns:
            Resposta da IA como dicionário (pode incluir '_session_id' se nova sessão foi criada)
        """
        if not request or not request.has_content():
            raise ValidationError("Mensagem ou arquivo vazio.")
        
        # Obtém ou cria sessão
        if session_id:
            session = self.session_repo.get_by_id(session_id)
            if not session:
                # Se session_id não existe, cria nova
                session = self.session_repo.get_or_create_for_user(user_id=user_id)
        else:
            session = self.session_repo.get_or_create_for_user(user_id=user_id)
        
        # Retorna session_id se foi criado novo
        new_session_id = None
        if not session_id and session:
            new_session_id = session.id
        
        # Processa arquivo se fornecido
        user_message = request.message or ""
        image_file = None
        
        if request.file:
            if request.file.mimetype.startswith('audio/'):
                if not self.speech_service or not self.speech_service.is_configured():
                    raise ExternalAPIError("Serviço de transcrição de áudio não está configurado.")
                audio_text = self.speech_service.transcribe_audio(request.file)
                if audio_text:
                    user_message = f"Áudio transcrito: '{audio_text}'.\n\n{user_message}" if user_message else f"Áudio transcrito: '{audio_text}'."
                else:
                    raise ExternalAPIError("Não consegui entender o áudio.")
            elif request.file.mimetype.startswith(('image/', 'video/')):
                image_file = request.file
        
        # Salva mensagem do usuário
        self.message_repo.create_message(session.id, MESSAGE_ROLE_USER, user_message)
        
        # Obtém histórico
        history = self._get_chat_history(session.id)
        
        # Gera resposta da IA
        ai_response_text = self.ai_service.generate_response(
            user_message,
            image_file,
            history
        )
        
        # Limpa e valida JSON
        json_str = self.ai_service.clean_json_response(ai_response_text)
        if not json_str:
            raise ExternalAPIError("Problema ao formatar resposta da IA.")
        
        try:
            parsed_json = json.loads(json_str)
            parsed_json = validate_ai_response(parsed_json)
        except Exception as e:
            raise ValidationError(f"Erro ao validar resposta da IA: {str(e)}")
        
        # Salva resposta da IA
        self.message_repo.create_message(
            session.id,
            MESSAGE_ROLE_ASSISTANT,
            json.dumps(parsed_json)
        )
        
        # Se identificou filme, busca detalhes
        if parsed_json.get("type") == "movie" and parsed_json.get("content"):
            movie_title = parsed_json["content"].get("title")
            if movie_title:
                movie_details = self.movie_service.search_movie(movie_title)
                if movie_details:
                    parsed_json["content"] = movie_details.to_dict()
                    # Atualiza mensagem salva
                    self.message_repo.create_message(
                        session.id,
                        MESSAGE_ROLE_ASSISTANT,
                        json.dumps(parsed_json)
                    )
                    return parsed_json
                else:
                    error_msg = f"Pensei que fosse '{movie_title}', mas não encontrei detalhes."
                    error_response = {"type": "text", "content": error_msg}
                    self.message_repo.create_message(
                        session.id,
                        MESSAGE_ROLE_ASSISTANT,
                        json.dumps(error_response)
                    )
                    return error_response
        
        result = parsed_json.copy()
        if new_session_id:
            result['_session_id'] = new_session_id
        
        return result
    
    def _get_chat_history(self, session_id: int) -> List[Dict[str, Any]]:
        """Obtém histórico de chat formatado."""
        messages = self.message_repo.get_session_history(session_id, CHAT_HISTORY_LIMIT)
        history_dto = ChatHistoryDTO.from_messages(messages)
        return history_dto.to_list()

