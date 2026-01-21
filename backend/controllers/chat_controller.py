"""
Controller para operações de chat API REST.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.chat_service import ChatService
from services.movie_service import MovieService
from dto.chat_dto import ChatRequestDTO
from core.exceptions import ChatCineException, ValidationError, NotFoundError
from extensions import limiter, cache

chat_bp = Blueprint('chat', __name__)
chat_service = ChatService()
movie_service = MovieService()


@chat_bp.route('/chat', methods=['POST'])
# @jwt_required()  # Desabilitado temporariamente para testes
@limiter.limit("10 per minute")
def chat():
    """Processa mensagem do chat."""
    try:
        # current_user_id = get_jwt_identity()  # Desabilitado para testes
        current_user_id = 1  # ID fixo para testes
        
        # Processa form-data (para suportar arquivos)
        message = request.form.get("message", "").strip()
        file = request.files.get("file")
        
        request_dto = ChatRequestDTO(
            message=message,
            file=file
        )
        
        response = chat_service.process_message(
            request=request_dto,
            user_id=current_user_id
        )
        
        return jsonify(response), 200
    
    except ValidationError as e:
        return jsonify({"type": "error", "content": e.message}), e.status_code
    except ChatCineException as e:
        return jsonify({"type": "text", "content": e.message}), e.status_code
    except Exception as e:
        return jsonify({
            "type": "text",
            "content": "Desculpe, ocorreu um erro inesperado."
        }), 500


@chat_bp.route('/movie/<int:movie_id>', methods=['GET'])
# @jwt_required()  # Desabilitado temporariamente para testes
@cache.cached(timeout=3600)
def get_movie_by_id(movie_id: int):
    """Busca filme por ID."""
    try:
        movie = movie_service.get_movie_by_id(movie_id)
        if movie:
            return jsonify({"type": "movie", "content": movie.to_dict()}), 200
        raise NotFoundError("Não consegui encontrar detalhes sobre este filme.")
    except ChatCineException as e:
        return jsonify({"type": "text", "content": e.message}), e.status_code
    except Exception as e:
        return jsonify({
            "type": "text",
            "content": "Ocorreu um erro ao buscar informações do filme."
        }), 500


@chat_bp.route('/recommendations/<int:movie_id>', methods=['GET'])
# @jwt_required()  # Desabilitado temporariamente para testes
@cache.cached(timeout=3600)
def get_recommendations(movie_id: int):
    """Busca recomendações de filme."""
    try:
        recommendations = movie_service.get_recommendations(movie_id)
        return jsonify({
            "type": "recommendations",
            "content": recommendations.to_list()
        }), 200
    except ChatCineException as e:
        return jsonify({"type": "text", "content": e.message}), e.status_code
    except Exception as e:
        return jsonify({
            "type": "text",
            "content": "Ocorreu um erro ao buscar recomendações."
        }), 500
