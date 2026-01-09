"""
Arquivo de compatibilidade - Mantém interface antiga funcionando.
Este arquivo será removido após migração completa.
"""
# Importa os novos services
from .services.ai_service import AIService
from .services.movie_service import MovieService
from .services.speech_service import SpeechService

# Cria instâncias globais para compatibilidade
_ai_service = None
_movie_service = None
_speech_service = None


def _get_ai_service():
    """Obtém instância do serviço de IA."""
    global _ai_service
    if _ai_service is None:
        try:
            _ai_service = AIService()
        except Exception:
            pass
    return _ai_service


def _get_movie_service():
    """Obtém instância do serviço de filmes."""
    global _movie_service
    if _movie_service is None:
        try:
            _movie_service = MovieService()
        except Exception:
            pass
    return _movie_service


def _get_speech_service():
    """Obtém instância do serviço de transcrição."""
    global _speech_service
    if _speech_service is None:
        try:
            _speech_service = SpeechService()
        except Exception:
            pass
    return _speech_service


# Funções de compatibilidade
def generate_gemini_response(user_message: str, image_file=None, chat_history=None) -> str:
    """Compatibilidade com código antigo."""
    service = _get_ai_service()
    if not service or not service.is_configured():
        import json
        return json.dumps({"type": "text", "content": "A API do Gemini não está configurada."})
    return service.generate_response(user_message, image_file, chat_history)


def clean_json_response(text: str):
    """Compatibilidade com código antigo."""
    service = _get_ai_service()
    if not service:
        return None
    return service.clean_json_response(text)


def get_movie_info(movie_name: str):
    """Compatibilidade com código antigo."""
    service = _get_movie_service()
    if not service or not service.is_configured():
        return None
    movie = service.search_movie(movie_name)
    return movie.to_dict() if movie else None


def get_movie_info_by_id(movie_id: int, media_type: str = "movie"):
    """Compatibilidade com código antigo."""
    service = _get_movie_service()
    if not service or not service.is_configured():
        return None
    movie = service.get_movie_by_id(movie_id, media_type)
    return movie.to_dict() if movie else None


def get_movie_recommendations(movie_id: int, media_type: str = "movie"):
    """Compatibilidade com código antigo."""
    service = _get_movie_service()
    if not service or not service.is_configured():
        return []
    recommendations = service.get_recommendations(movie_id, media_type)
    return recommendations.to_list()


def process_audio(file):
    """Compatibilidade com código antigo."""
    service = _get_speech_service()
    if not service or not service.is_configured():
        return None
    try:
        return service.transcribe_audio(file)
    except Exception:
        return None
