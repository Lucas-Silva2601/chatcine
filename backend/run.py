"""
Ponto de entrada da aplicação Flask.
"""
import os
from app import create_app
from utils.logging_config import setup_logging

# Cria a aplicação
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Configura logging
setup_logging(app)

if __name__ == "__main__":
    # Em desenvolvimento, roda com debug
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5001))
    
    app.run(debug=debug, host='0.0.0.0', port=port)
