"""
Script para iniciar o servidor Flask com output visível.
"""
import os
import sys
from pathlib import Path

# Tenta usar o Python do venv local primeiro
venv_python = Path(__file__).parent / 'venv' / 'Scripts' / 'python.exe'
if venv_python.exists():
    # Se o venv existe, verifica se estamos usando ele
    if not str(venv_python.parent.parent) in sys.executable:
        print(f"⚠️  Usando Python: {sys.executable}")
        print(f"💡 Para usar o venv local, execute: .\\venv\\Scripts\\python.exe start_server.py")
        print()

# Adiciona o diretório chatalfa ao PYTHONPATH
chatalfa_path = Path(__file__).parent / 'chatalfa'
if str(chatalfa_path) not in sys.path:
    sys.path.insert(0, str(chatalfa_path))

print("🚀 Iniciando servidor ChatCine...")
print(f"📁 Diretório: {Path(__file__).parent}")
print(f"🐍 Python: {sys.executable}")

try:
    from chatcine import create_app
    from chatcine.utils.logging_config import setup_logging
    
    print("✅ Módulos importados com sucesso")
    
    # Cria a aplicação
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    print("✅ Aplicação criada")
    
    # Configura logging
    setup_logging(app)
    print("✅ Logging configurado")
    
    # Configurações
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5001))
    
    print(f"🌐 Iniciando servidor em http://0.0.0.0:{port}")
    print(f"🔧 Debug: {debug}")
    print("=" * 50)
    
    # Inicia servidor
    app.run(debug=debug, host='0.0.0.0', port=port, use_reloader=False)
    
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

