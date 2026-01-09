"""
Factory da aplicação Flask.
Cria e configura a aplicação seguindo o padrão Application Factory.
"""
import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa extensões
from .extensions import (
    login_manager, db, migrate, oauth, limiter, talisman, cache
)
import chatcine.extensions as ext
from .config import config


def create_app(config_name: str = None) -> Flask:
    """
    Cria e configura a aplicação Flask.
    
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
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # OAuth
    oauth.init_app(app)
    
    # Security
    # Configura CSP para permitir imagens do TMDB
    csp_policy = {
        'default-src': "'self'",
        'img-src': ["'self'", 'https://image.tmdb.org', 'https://via.placeholder.com', 'data:'],
        'script-src': ["'self'", "'unsafe-inline'"],  # Permite scripts inline para templates
        'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
        'font-src': ["'self'", 'https://fonts.gstatic.com'],
        'connect-src': ["'self'", 'https://api.themoviedb.org', 'https://api.groq.com'],
        'object-src': "'none'"
    }
    
    talisman.init_app(
        app,
        force_https=False,  # Desabilitado em desenvolvimento
        strict_transport_security=False,  # Desabilitado em desenvolvimento
        content_security_policy=csp_policy
    )
    
    # Rate Limiting
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter.init_app(app)
    
    # Cache
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    
    # User loader
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id: str):
        """Carrega usuário do banco de dados."""
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None
    
    # Configura Google OAuth
    if app.config.get('GOOGLE_CLIENT_ID') and app.config.get('GOOGLE_CLIENT_SECRET'):
        ext.google_oauth = oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )


def _setup_google_credentials() -> None:
    """Configura as credenciais do Google Cloud."""
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if credentials_json:
        # Se as credenciais estão em variável de ambiente, escreve em arquivo
        filepath = Path(__file__).parent.parent / 'google-credentials.json'
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
    from .controllers.auth_controller import auth_bp
    from .controllers.chat_controller import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp, url_prefix='/')


def _register_error_handlers(app: Flask) -> None:
    """Registra handlers de erro."""
    from flask import render_template, jsonify, request, redirect, url_for, flash
    from .core.exceptions import ChatCineException
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {'error': 'Rate limit exceeded', 'message': str(error.description)}, 429
    
    @app.errorhandler(ChatCineException)
    def handle_chatcine_exception(error: ChatCineException):
        """Handler para exceções customizadas."""
        if request.is_json or request.path.startswith('/api'):
            return jsonify({'error': error.message}), error.status_code
        flash(error.message, 'error')
        return redirect(request.referrer or url_for('main.index')), error.status_code
