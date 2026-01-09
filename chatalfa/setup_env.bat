@echo off
echo ====================================
echo Configurando Ambiente ChatCine
echo ====================================
echo.

REM Cria ambiente virtual
echo [1/4] Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual
    pause
    exit /b 1
)

REM Ativa ambiente virtual
echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instala dependências
echo [3/4] Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependências
    pause
    exit /b 1
)

REM Cria arquivo .env se não existir
echo [4/4] Configurando variáveis de ambiente...
if not exist .env (
    echo Criando arquivo .env a partir do .env.example...
    copy .env.example .env
    echo.
    echo ATENCAO: Edite o arquivo .env e configure suas chaves de API!
) else (
    echo Arquivo .env ja existe.
)

echo.
echo ====================================
echo Configuracao concluida!
echo ====================================
echo.
echo Proximos passos:
echo 1. Edite o arquivo .env com suas chaves de API
echo 2. Execute: python init_db.py
echo 3. Execute: python run.py
echo.
pause

