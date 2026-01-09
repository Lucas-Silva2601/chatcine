"""
Ponto de entrada da aplicação Flask.
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório chatalfa ao PYTHONPATH
chatalfa_path = Path(__file__).parent / 'chatalfa'
if str(chatalfa_path) not in sys.path:
    sys.path.insert(0, str(chatalfa_path))

from chatcine import create_app
from chatcine.utils.logging_config import setup_logging

# Cria a aplicação
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Configura logging
setup_logging(app)

if __name__ == "__main__":
    # Em desenvolvimento, roda com debug
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5001))
    
    app.run(debug=debug, host='0.0.0.0', port=port)
