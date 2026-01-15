"""
Configurações da aplicação Flask.
Separa as configurações por ambiente (desenvolvimento, produção, teste).
"""
import os
from pathlib import Path


class Config:
    """Configuração base compartilhada por todos os ambientes."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32).hex())
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(32).hex())
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 dias
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security
    WTF_CSRF_ENABLED = False  # Desabilitado para API REST
    WTF_CSRF_TIME_LIMIT = None
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    # APIs
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Inicializa configurações específicas da aplicação."""
        pass


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    DEBUG = True
    
    # Supabase ou SQLite local
    database_url = os.getenv('DATABASE_URL', '')
    
    # Se usar Supabase, corrige o prefixo postgres:// para postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or f"sqlite:///{Path(__file__).parent / 'instance' / 'chatcine_dev.db'}"
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Configuração para produção."""
    DEBUG = False
    
    # Supabase em produção
    database_url = os.getenv('DATABASE_URL', '')
    
    # Se usar Supabase, corrige o prefixo postgres:// para postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Logging em produção
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/chatcine.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('ChatCine startup')


class TestingConfig(Config):
    """Configuração para testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


# Dicionário para facilitar a seleção de configuração
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

