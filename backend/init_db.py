"""
Script para inicializar o banco de dados.
Cria as tabelas e pode popular com dados iniciais.
"""
from app import create_app
from extensions import db
from models import User, ChatSession, ChatMessage

app = create_app()

with app.app_context():
    # Remove todas as tabelas e recria (para desenvolvimento)
    db.drop_all()
    # Cria todas as tabelas
    db.create_all()
    print("✅ Banco de dados inicializado com sucesso!")
    print("📊 Tabelas criadas: users, chat_sessions, chat_messages")
    print("ℹ️  Agora o chat funciona sem necessidade de login!")
