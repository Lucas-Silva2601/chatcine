"""
Script para inicializar o banco de dados.
Cria as tabelas e pode popular com dados iniciais.
"""
import sys
from pathlib import Path

# Adiciona o diretório chatalfa ao PYTHONPATH
chatalfa_path = Path(__file__).parent / 'chatalfa'
if str(chatalfa_path) not in sys.path:
    sys.path.insert(0, str(chatalfa_path))

from chatcine import create_app
from chatcine.extensions import db
from chatcine.models import User, ChatSession, ChatMessage

app = create_app()

with app.app_context():
    # Remove todas as tabelas e recria (para desenvolvimento)
    db.drop_all()
    # Cria todas as tabelas
    db.create_all()
    print("✅ Banco de dados inicializado com sucesso!")
    print("📊 Tabelas criadas: users, chat_sessions, chat_messages")
    print("ℹ️  Agora o chat funciona sem necessidade de login!")
