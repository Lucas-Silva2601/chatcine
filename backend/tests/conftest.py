"""
Configuração compartilhada para testes pytest.
"""
import pytest
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from extensions import db
from models import User, ChatSession, ChatMessage


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
        db.session.refresh(user)  # Atualiza o objeto para evitar DetachedInstanceError
        yield user


@pytest.fixture
def authenticated_client(client, test_user):
    """Cria um cliente autenticado."""
    from flask_login import login_user
    
    with client:
        with client.session_transaction() as sess:
            # Simula login
            login_user(test_user)
        yield client

