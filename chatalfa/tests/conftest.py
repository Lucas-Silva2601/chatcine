"""
Configuração compartilhada para testes pytest.
"""
import pytest
from chatcine import create_app
from chatcine.extensions import db
from chatcine.models import User, ChatSession, ChatMessage


@pytest.fixture
def app():
    """Cria uma instância da aplicação para testes."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    return app


@pytest.fixture
def client(app):
    """Cria um cliente de teste."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Cria um runner de comandos CLI."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Cria um usuário de teste."""
    with app.app_context():
        user = User(email='test@example.com', password='testpass123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Cria um cliente autenticado."""
    from flask_login import login_user
    
    with client:
        with client.session_transaction() as sess:
            # Simula login
            login_user(test_user)
        yield client

