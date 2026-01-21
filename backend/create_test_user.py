"""
Script para criar usuário de teste.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    # Verifica se usuário de teste já existe
    test_user = User.query.filter_by(email='teste@chatcine.com').first()
    
    if test_user:
        print("✅ Usuário de teste já existe!")
        print(f"   Email: {test_user.email}")
        print(f"   ID: {test_user.id}")
    else:
        # Cria usuário de teste
        test_user = User(
            email='teste@chatcine.com',
            password='teste123',
            plan_status='free'
        )
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Usuário de teste criado com sucesso!")
        print(f"   Email: teste@chatcine.com")
        print(f"   Senha: teste123")
        print(f"   ID: {test_user.id}")

