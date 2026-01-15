"""
Script para migrar dados do SQLite para Supabase.
Execute este script se você já tem dados no SQLite e quer migrar para Supabase.
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from models import User, ChatSession, ChatMessage
from dotenv import load_dotenv

load_dotenv()


def migrate_data():
    """Migra dados do SQLite para Supabase."""
    
    # Conexão SQLite (origem)
    sqlite_path = Path(__file__).parent / 'instance' / 'chatcine_dev.db'
    if not sqlite_path.exists():
        print("❌ Banco SQLite não encontrado!")
        print(f"   Procurado em: {sqlite_path}")
        return
    
    sqlite_url = f'sqlite:///{sqlite_path}'
    sqlite_engine = create_engine(sqlite_url)
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SqliteSession()
    
    # Conexão Supabase (destino)
    supabase_url = os.getenv('DATABASE_URL')
    if not supabase_url:
        print("❌ DATABASE_URL não configurada!")
        print("   Configure a variável de ambiente DATABASE_URL com a URL do Supabase")
        return
    
    # Corrige prefixo postgres:// para postgresql://
    if supabase_url.startswith('postgres://'):
        supabase_url = supabase_url.replace('postgres://', 'postgresql://', 1)
    
    supabase_engine = create_engine(supabase_url)
    SupabaseSession = sessionmaker(bind=supabase_engine)
    supabase_session = SupabaseSession()
    
    print("🚀 Iniciando migração...")
    print(f"   Origem: SQLite ({sqlite_path})")
    print(f"   Destino: Supabase")
    print()
    
    try:
        # Migrar usuários
        users = sqlite_session.query(User).all()
        print(f"📊 Migrando {len(users)} usuários...")
        
        user_map = {}  # Mapeia IDs antigos para novos
        for old_user in users:
            # Verifica se usuário já existe
            existing = supabase_session.query(User).filter_by(email=old_user.email).first()
            if existing:
                print(f"   ⚠️  Usuário {old_user.email} já existe, pulando...")
                user_map[old_user.id] = existing.id
                continue
            
            new_user = User(
                email=old_user.email,
                password=None,  # Senha já está hasheada
                profile_pic_url=old_user.profile_pic_url,
                plan_status=old_user.plan_status
            )
            new_user.password_hash = old_user.password_hash
            supabase_session.add(new_user)
            supabase_session.flush()
            
            user_map[old_user.id] = new_user.id
            print(f"   ✅ {old_user.email}")
        
        supabase_session.commit()
        print(f"✅ {len(users)} usuários migrados!\n")
        
        # Migrar sessões de chat
        sessions = sqlite_session.query(ChatSession).all()
        print(f"📊 Migrando {len(sessions)} sessões de chat...")
        
        session_map = {}
        for old_session in sessions:
            if old_session.user_id and old_session.user_id not in user_map:
                print(f"   ⚠️  Sessão {old_session.id} tem user_id inválido, pulando...")
                continue
            
            new_session = ChatSession(
                user_id=user_map.get(old_session.user_id) if old_session.user_id else None,
                session_key=old_session.session_key
            )
            supabase_session.add(new_session)
            supabase_session.flush()
            
            session_map[old_session.id] = new_session.id
        
        supabase_session.commit()
        print(f"✅ {len(sessions)} sessões migradas!\n")
        
        # Migrar mensagens
        messages = sqlite_session.query(ChatMessage).all()
        print(f"📊 Migrando {len(messages)} mensagens...")
        
        migrated = 0
        for old_message in messages:
            if old_message.session_id not in session_map:
                continue
            
            new_message = ChatMessage(
                session_id=session_map[old_message.session_id],
                role=old_message.role,
                content=old_message.content
            )
            supabase_session.add(new_message)
            migrated += 1
            
            if migrated % 100 == 0:
                print(f"   {migrated}/{len(messages)}...")
        
        supabase_session.commit()
        print(f"✅ {migrated} mensagens migradas!\n")
        
        print("🎉 Migração concluída com sucesso!")
        print()
        print("📊 Resumo:")
        print(f"   Usuários: {len(users)}")
        print(f"   Sessões: {len(sessions)}")
        print(f"   Mensagens: {migrated}")
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        supabase_session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        sqlite_session.close()
        supabase_session.close()


if __name__ == '__main__':
    print("=" * 60)
    print("  MIGRAÇÃO SQLite → Supabase")
    print("=" * 60)
    print()
    print("⚠️  ATENÇÃO:")
    print("   - Certifique-se de ter executado o schema SQL no Supabase")
    print("   - Configure DATABASE_URL no .env com a URL do Supabase")
    print("   - Esta migração NÃO deleta dados do SQLite")
    print()
    
    resposta = input("Deseja continuar? (s/n): ")
    if resposta.lower() != 's':
        print("Migração cancelada.")
        sys.exit(0)
    
    print()
    migrate_data()

