"""
Controller para operações de chat.
"""
from flask import Blueprint, render_template, request, jsonify, session

from ..services.chat_service import ChatService
from ..services.movie_service import MovieService
from ..dto.chat_dto import ChatRequestDTO
from ..dto.movie_dto import RecommendationsDTO
from ..core.exceptions import ChatCineException, ValidationError, NotFoundError
from ..extensions import limiter, cache


class ChatController:
    """Controller para gerenciar rotas de chat."""
    
    def __init__(self):
        """Inicializa o controller."""
        self.chat_service = ChatService()
        self.movie_service = MovieService()
        self.blueprint = Blueprint('main', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Registra as rotas do controller."""
        self.blueprint.route("/", methods=["GET"])(self.index)
        self.blueprint.route("/chat", methods=["POST"])(self.chat)
        self.blueprint.route("/movie/<int:movie_id>", methods=["GET"])(self.get_movie_by_id)
        self.blueprint.route("/recommendations/<int:movie_id>", methods=["GET"])(self.get_recommendations)
    
    def index(self):
        """Rota para a página principal do chat."""
        return render_template('index.html')
    
    @limiter.limit("10 per minute")
    def chat(self):
        """Processa mensagem do chat."""
        try:
            request_dto = ChatRequestDTO(
                message=request.form.get("message", "").strip(),
                file=request.files.get("file")
            )
            
            # Usa session_id da sessão Flask (cookie) para usuários anônimos
            session_id = session.get('chat_session_id')
            response = self.chat_service.process_message(
                session_id=session_id,
                request=request_dto
            )
            
            # Salva session_id na sessão Flask se foi criado
            if response.get('_session_id'):
                session['chat_session_id'] = response['_session_id']
                del response['_session_id']
            
            return jsonify(response)
        
        except ValidationError as e:
            return jsonify({"type": "error", "content": e.message}), e.status_code
        except ChatCineException as e:
            return jsonify({"type": "text", "content": e.message}), e.status_code
        except Exception as e:
            return jsonify({
                "type": "text",
                "content": "Desculpe, ocorreu um erro inesperado."
            }), 500
    
    @cache.cached(timeout=3600)
    def get_movie_by_id(self, movie_id: int):
        """Busca filme por ID."""
        try:
            movie = self.movie_service.get_movie_by_id(movie_id)
            if movie:
                return jsonify({"type": "movie", "content": movie.to_dict()})
            raise NotFoundError("Não consegui encontrar detalhes sobre este filme.")
        except ChatCineException as e:
            return jsonify({"type": "text", "content": e.message}), e.status_code
        except Exception as e:
            return jsonify({
                "type": "text",
                "content": "Ocorreu um erro ao buscar informações do filme."
            }), 500
    
    @cache.cached(timeout=3600)
    def get_recommendations(self, movie_id: int):
        """Busca recomendações de filme."""
        try:
            recommendations = self.movie_service.get_recommendations(movie_id)
            return jsonify({
                "type": "recommendations",
                "content": recommendations.to_list()
            })
        except ChatCineException as e:
            return jsonify({"type": "text", "content": e.message}), e.status_code
        except Exception as e:
            return jsonify({
                "type": "text",
                "content": "Ocorreu um erro ao buscar recomendações."
            }), 500


# Cria instância do controller
chat_controller = ChatController()
main_bp = chat_controller.blueprint

