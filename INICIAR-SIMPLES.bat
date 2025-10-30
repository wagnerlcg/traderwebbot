@echo off
chcp 65001 > nul
echo 🚀 INICIANDO TRADER BOT - INTERFACE WEB COMPLETA
echo ================================================

echo.
echo 1. Verificando ambiente virtual...
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ Ambiente virtual não encontrado!
    echo Execute: python -m venv .venv
    pause
    exit /b 1
)

echo ✅ Ambiente virtual encontrado
call .venv\Scripts\activate.bat

echo.
echo 2. Verificando dependências...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependências...
    pip install flask flask-socketio pymysql flask-session cryptography python-dotenv
) else (
    echo ✅ Dependências OK
)

echo.
echo 3. Iniciando servidor web...
echo ================================================
echo 🌐 Acesse: http://localhost:5000
echo 👤 Login: usuario@exemplo.com
echo 🔑 Senha: 123456
echo ================================================
echo.
echo 💡 Todas as funcionalidades estão na interface web:
echo    - Controle do Bot
echo    - Upload de Sinais
echo    - Configurações Avançadas
echo    - Logs em Tempo Real
echo    - Ferramentas do Sistema
echo    - Relatórios e Análises
echo ================================================
echo.

python web_interface.py

echo.
echo Servidor encerrado. Pressione qualquer tecla para sair...
pause >nul
