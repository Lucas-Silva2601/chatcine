"""
Factory da aplicação Flask API REST.
Cria e configura a aplicação seguindo o padrão Application Factory.
"""
import os
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa extensões
from extensions import (
    db, migrate, limiter, cache, jwt
)
from config import config


def create_app(config_name: str = None) -> Flask:
    """
    Cria e configura a aplicação Flask API.
    
    Args:
        config_name: Nome da configuração ('development', 'production', 'testing')
                    Se None, usa FLASK_ENV ou 'default'
    
    Returns:
        Instância configurada da aplicação Flask
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Seleciona a configuração
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Cria diretório instance se não existir
    instance_path = Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)
    
    # Configura CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Inicializa extensões
    _init_extensions(app)
    
    # Configura Google Cloud credentials
    _setup_google_credentials()
    
    # Registra blueprints
    _register_blueprints(app)
    
    # Configura error handlers
    _register_error_handlers(app)
    
    return app


def _init_extensions(app: Flask) -> None:
    """Inicializa todas as extensões Flask."""
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # JWT
    jwt.init_app(app)
    
    # Rate Limiting
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter.init_app(app)
    
    # Cache
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})


def _setup_google_credentials() -> None:
    """Configura as credenciais do Google Cloud."""
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if credentials_json:
        # Se as credenciais estão em variável de ambiente, escreve em arquivo
        filepath = Path(__file__).parent / 'google-credentials.json'
        with open(filepath, 'w') as f:
            f.write(credentials_json)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(filepath)
    elif credentials_path and os.path.exists(credentials_path):
        # Se o caminho já está configurado e o arquivo existe
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    elif os.path.exists('google-credentials.json'):
        # Fallback para arquivo na raiz
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-credentials.json'


def _register_blueprints(app: Flask) -> None:
    """Registra todos os blueprints da aplicação."""
    from controllers.auth_controller import auth_bp
    from controllers.chat_controller import chat_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api')


def _register_error_handlers(app: Flask) -> None:
    """Registra handlers de erro."""
    from flask import jsonify
    from core.exceptions import ChatCineException
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({'error': 'Rate limit exceeded', 'message': str(error.description)}), 429
    
    @app.errorhandler(ChatCineException)
    def handle_chatcine_exception(error: ChatCineException):
        """Handler para exceções customizadas."""
        return jsonify({'error': error.message}), error.status_code
