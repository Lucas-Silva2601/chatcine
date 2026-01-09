"""
Script para inicializar o banco de dados.
Cria as tabelas e pode popular com dados iniciais.
"""
from chatcine import create_app
from chatcine.extensions import db
from chatcine.models import User, ChatSession, ChatMessage

app = create_app()

with app.app_context():
    # Cria todas as tabelas
    db.create_all()
    print("✅ Banco de dados inicializado com sucesso!")
    print("📊 Tabelas criadas: users, chat_sessions, chat_messages")

