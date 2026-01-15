"""
Testes unitários para modelos.
"""
import pytest
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import User, ChatSession, ChatMessage
from extensions import db


class TestUser:
    """Testes para o modelo User."""
    
    def test_create_user(self, app):
        """Testa criação de usuário."""
        with app.app_context():
            user = User(email='test@example.com', password='password123')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.email == 'test@example.com'
            assert user.password_hash is not None
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')
    
    def test_user_default_avatar(self, app):
        """Testa geração de avatar padrão."""
        with app.app_context():
            user = User(email='test@example.com', password='password123')
            assert user.profile_pic_url is not None
            assert 'ui-avatars.com' in user.profile_pic_url
    
    def test_user_set_password(self, app):
        """Testa definição de senha."""
        with app.app_context():
            user = User(email='test@example.com', password='password123')
            user.set_password('newpassword456')
            assert user.check_password('newpassword456')
            assert not user.check_password('password123')
    
    def test_user_get_id(self, app):
        """Testa método get_id."""
        with app.app_context():
            user = User(email='test@example.com', password='password123')
            db.session.add(user)
            db.session.commit()
            
            assert user.get_id() == str(user.id)


class TestChatSession:
    """Testes para o modelo ChatSession."""
    
    def test_create_chat_session(self, app, test_user):
        """Testa criação de sessão de chat."""
        with app.app_context():
            session = ChatSession(user_id=test_user.id)
            db.session.add(session)
            db.session.commit()
            
            assert session.id is not None
            assert session.user_id == test_user.id
            assert session.user == test_user


class TestChatMessage:
    """Testes para o modelo ChatMessage."""
    
    def test_create_chat_message(self, app, test_user):
        """Testa criação de mensagem de chat."""
        with app.app_context():
            session = ChatSession(user_id=test_user.id)
            db.session.add(session)
            db.session.commit()
            
            message = ChatMessage(
                session_id=session.id,
                role='user',
                content='Test message'
            )
            db.session.add(message)
            db.session.commit()
            
            assert message.id is not None
            assert message.session_id == session.id
            assert message.role == 'user'
            assert message.content == 'Test message'
            assert message.session == session

