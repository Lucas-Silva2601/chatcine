"""
Script de setup inicial do ChatCine.
Cria arquivos .env necessários se não existirem.
"""
import os
from pathlib import Path

def create_env_file(path, content):
    """Cria arquivo .env se não existir."""
    env_path = Path(path)
    if env_path.exists():
        print(f"✅ {path} já existe")
        return False
    
    env_path.write_text(content, encoding='utf-8')
    print(f"✅ {path} criado com sucesso!")
    return True

def main():
    print("=" * 60)
    print("  SETUP INICIAL - ChatCine")
    print("=" * 60)
    print()
    
    # Conteúdo do backend/.env
    backend_env = """# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
PORT=5001

# Database - SQLite Local (para desenvolvimento)
# Deixe vazio para usar SQLite local
DATABASE_URL=

# Para usar Supabase, configure:
# DATABASE_URL=postgresql://postgres:[SUA-SENHA]@db.xxxxx.supabase.co:5432/postgres

# External APIs (CONFIGURE SUAS CHAVES AQUI!)
GROQ_API_KEY=
TMDB_API_KEY=

# Rate Limiting
RATELIMIT_ENABLED=true

# Logging
LOG_LEVEL=INFO
"""
    
    # Conteúdo do frontend/.env
    frontend_env = """# API Backend
VITE_API_URL=http://localhost:5001/api

# Supabase (Opcional - apenas se usar recursos diretos do Supabase)
# VITE_SUPABASE_URL=https://xxxxx.supabase.co
# VITE_SUPABASE_ANON_KEY=sua-chave-publica
"""
    
    # Criar arquivos
    print("📝 Criando arquivos de configuração...")
    print()
    
    backend_created = create_env_file('backend/.env', backend_env)
    frontend_created = create_env_file('frontend/.env', frontend_env)
    
    print()
    print("=" * 60)
    
    if backend_created or frontend_created:
        print("🎉 Setup concluído!")
        print()
        print("⚠️  IMPORTANTE:")
        print("   1. Configure suas API keys em backend/.env:")
        print("      - GROQ_API_KEY (https://console.groq.com/)")
        print("      - TMDB_API_KEY (https://www.themoviedb.org/)")
        print()
        print("   2. Para usar Supabase:")
        print("      - Veja o guia: SUPABASE_SETUP.md")
        print("      - Configure DATABASE_URL em backend/.env")
        print()
        print("   3. Execute: npm run dev")
    else:
        print("ℹ️  Arquivos .env já existem. Nenhuma alteração feita.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()

