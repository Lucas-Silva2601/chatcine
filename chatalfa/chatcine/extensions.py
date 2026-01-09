"""
Inicialização de extensões Flask.
Centraliza todas as extensões para evitar importações circulares.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache

# Inicializa as extensões
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()
cache = Cache()

# Variável global para o objeto Google OAuth
google_oauth = None

