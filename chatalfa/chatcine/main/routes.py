"""
Rotas principais da aplicação.
Gerencia o chat, busca de filmes e recomendações.
"""
import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from ..models import ChatSession, ChatMessage
from ..extensions import db, limiter, cache
from ..schemas import validate_ai_response
from .. import services

# Cria um Blueprint chamado 'main'
main_bp = Blueprint('main', __name__)


def get_or_create_chat_session(user_id: int) -> ChatSession:
    """Obtém ou cria uma sessão de chat para o usuário."""
    session = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).first()
    
    if not session:
        session = ChatSession(user_id=user_id)
        db.session.add(session)
        db.session.commit()
    
    return session


def get_chat_history(session_id: int, limit: int = 6) -> list:
    """Obtém o histórico de mensagens da sessão."""
    messages = ChatMessage.query.filter_by(session_id=session_id)\
        .order_by(ChatMessage.created_at.desc())\
        .limit(limit)\
        .all()
    
    # Inverte para ordem cronológica
    messages.reverse()
    
    history = []
    for msg in messages:
        history.append({
            "role": msg.role,
            "content": json.loads(msg.content) if msg.role == "assistant" else msg.content
        })
    
    return history


def save_message(session_id: int, role: str, content: str) -> None:
    """Salva uma mensagem no banco de dados."""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content
    )
    db.session.add(message)
    db.session.commit()


@main_bp.route("/")
@login_required
def index():
    """Rota para a página principal do chat."""
    return render_template('index.html', user=current_user)


@main_bp.route("/chat", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def chat():
    """Rota que recebe as mensagens do usuário e retorna a resposta da IA."""
    user_message = request.form.get("message", "").strip()
    file = request.files.get("file")
    
    if not user_message and not file:
        return jsonify({"type": "error", "content": "Mensagem ou arquivo vazio."}), 400
    
    try:
        # Obtém ou cria sessão de chat
        chat_session = get_or_create_chat_session(current_user.id)
        
        # Processa arquivo de áudio se fornecido
        image_file = None
        if file and file.mimetype.startswith('audio/'):
            audio_text = services.process_audio(file)
            if audio_text:
                user_message = f"Áudio transcrito: '{audio_text}'.\n\n{user_message}" if user_message else f"Áudio transcrito: '{audio_text}'."
            else:
                return jsonify({
                    "type": "text",
                    "content": "Não consegui entender o áudio. Verifique se seu microfone está funcionando ou se as credenciais da API de áudio estão corretas."
                })
        elif file and (file.mimetype.startswith('image/') or file.mimetype.startswith('video/')):
            image_file = file
        
        # Salva mensagem do usuário
        save_message(chat_session.id, "user", user_message)
        
        # Obtém histórico
        chat_history = get_chat_history(chat_session.id)
        
        # Gera resposta da IA
        ia_response_text = services.generate_gemini_response(user_message, image_file, chat_history)
        
        # Limpa e valida JSON
        json_str = services.clean_json_response(ia_response_text)
        if not json_str:
            return jsonify({
                "type": "text",
                "content": "Desculpe, tive um problema para formatar a resposta da IA."
            })
        
        try:
            parsed_json = json.loads(json_str)
            # Valida usando schema Marshmallow
            parsed_json = validate_ai_response(parsed_json)
        except Exception as e:
            return jsonify({
                "type": "text",
                "content": f"Erro ao validar resposta da IA: {str(e)}"
            })
        
        # Salva resposta da IA
        save_message(chat_session.id, "assistant", json.dumps(parsed_json))
        
        # Se identificou um filme, busca detalhes no TMDB
        if parsed_json.get("type") == "movie" and parsed_json.get("content"):
            movie_title_from_ai = parsed_json["content"].get("title")
            if movie_title_from_ai:
                movie_details = services.get_movie_info(movie_title_from_ai)
                if movie_details:
                    # Atualiza a mensagem salva com os detalhes completos
                    parsed_json["content"] = movie_details
                    save_message(chat_session.id, "assistant", json.dumps(parsed_json))
                    return jsonify({"type": "movie", "content": movie_details})
                else:
                    error_msg = f"Pensei que fosse '{movie_title_from_ai}', mas não encontrei detalhes sobre ele."
                    save_message(chat_session.id, "assistant", json.dumps({"type": "text", "content": error_msg}))
                    return jsonify({"type": "text", "content": error_msg})
        
        return jsonify(parsed_json)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "type": "text",
            "content": "Desculpe, ocorreu um erro ao salvar sua mensagem."
        }), 500
    except Exception as e:
        return jsonify({
            "type": "text",
            "content": "Desculpe, ocorreu um erro inesperado ao processar sua solicitação."
        }), 500


@main_bp.route("/movie/<int:movie_id>")
@login_required
@cache.cached(timeout=3600)  # Cache por 1 hora
def get_movie_by_id(movie_id: int):
    """Rota para buscar detalhes de um filme específico pelo seu ID do TMDB."""
    try:
        movie_details = services.get_movie_info_by_id(movie_id)
        if movie_details:
            return jsonify({"type": "movie", "content": movie_details})
        else:
            return jsonify({
                "type": "text",
                "content": "Não consegui encontrar detalhes sobre este filme."
            }), 404
    except Exception as e:
        return jsonify({
            "type": "text",
            "content": "Ocorreu um erro ao buscar informações do filme."
        }), 500


@main_bp.route("/recommendations/<int:movie_id>")
@login_required
@cache.cached(timeout=3600)  # Cache por 1 hora
def get_recommendations(movie_id: int):
    """Rota para buscar recomendações baseadas em um filme (pelo ID do TMDB)."""
    try:
        recommendations = services.get_movie_recommendations(movie_id)
        if recommendations:
            return jsonify({"type": "recommendations", "content": recommendations})
        else:
            return jsonify({
                "type": "text",
                "content": "Não consegui encontrar recomendações para este filme."
            }), 404
    except Exception as e:
        return jsonify({
            "type": "text",
            "content": "Ocorreu um erro ao buscar recomendações."
        }), 500
