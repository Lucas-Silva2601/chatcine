"""
Configuração de logging para a aplicação.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(app) -> None:
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    # Cria diretório de logs se não existir
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Remove handlers padrão
    app.logger.handlers.clear()
    
    # Handler para arquivo
    file_handler = RotatingFileHandler(
        log_dir / 'chatcine.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Adiciona handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # Define nível de logging
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.info('ChatCine logging configurado')

