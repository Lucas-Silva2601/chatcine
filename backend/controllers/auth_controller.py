"""
Controller para operações de autenticação API REST.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from repositories.user_repository import UserRepository
from core.exceptions import ValidationError, AuthenticationError

auth_bp = Blueprint('auth', __name__)
user_repo = UserRepository()


@auth_bp.route('/login', methods=['POST'])
def login():
    """Rota de login - retorna JWT token."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user = user_repo.get_by_email(email)
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        # Cria tokens JWT
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'profile_pic_url': user.profile_pic_url
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """Rota de registro - cria novo usuário e retorna JWT token."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400
        
        # Verifica se email já existe
        if user_repo.get_by_email(email):
            return jsonify({'error': 'Este email já está registrado'}), 409
        
        # Cria novo usuário
        user = user_repo.create_user(email=email, password=password)
        
        # Cria tokens JWT
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Conta criada com sucesso',
            'token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'profile_pic_url': user.profile_pic_url
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renova o access token usando refresh token."""
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Retorna informações do usuário autenticado."""
    try:
        current_user_id = get_jwt_identity()
        user = user_repo.get_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'profile_pic_url': user.profile_pic_url,
                'plan_status': user.plan_status
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout (no lado do cliente, remove o token)."""
    return jsonify({'message': 'Logout realizado com sucesso'}), 200
