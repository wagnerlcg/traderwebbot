@echo off
echo 🚀 INICIANDO TRADER BOT - VERSÃO SIMPLES
echo =========================================

echo.
echo 1. Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo.
echo 2. Instalando dependências básicas...
pip install flask flask-socketio pymysql flask-session cryptography python-dotenv --quiet

echo.
echo 3. Iniciando servidor web...
echo =========================================
echo 🌐 Acesse: http://localhost:5000
echo 👤 Login: usuario@exemplo.com
echo 🔑 Senha: 123456
echo =========================================
echo.

python web_interface_simples.py

pause
