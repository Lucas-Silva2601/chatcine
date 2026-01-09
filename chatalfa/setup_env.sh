#!/bin/bash

echo "===================================="
echo "Configurando Ambiente ChatCine"
echo "===================================="
echo ""

# Cria ambiente virtual
echo "[1/4] Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar ambiente virtual"
    exit 1
fi

# Ativa ambiente virtual
echo "[2/4] Ativando ambiente virtual..."
source venv/bin/activate

# Instala dependências
echo "[3/4] Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências"
    exit 1
fi

# Cria arquivo .env se não existir
echo "[4/4] Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    echo "Criando arquivo .env a partir do .env.example..."
    cp .env.example .env
    echo ""
    echo "ATENÇÃO: Edite o arquivo .env e configure suas chaves de API!"
else
    echo "Arquivo .env já existe."
fi

echo ""
echo "===================================="
echo "Configuração concluída!"
echo "===================================="
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env com suas chaves de API"
echo "2. Execute: python init_db.py"
echo "3. Execute: python run.py"
echo ""

