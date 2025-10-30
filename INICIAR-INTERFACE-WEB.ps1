# Script para iniciar a Interface Web do Trader Bot
# INICIAR-INTERFACE-WEB.ps1

Write-Host "🚀 INICIANDO TRADER BOT - INTERFACE WEB" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Verificar se o ambiente virtual existe
if (-not (Test-Path ".venv\Scripts\activate.bat")) {
    Write-Host "❌ Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "Execute: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "1. Ativando ambiente virtual..." -ForegroundColor Cyan
& .venv\Scripts\activate.bat

Write-Host ""
Write-Host "2. Verificando dependências..." -ForegroundColor Cyan

# Verificar se Flask está instalado
try {
    python -c "import flask; print('✅ Flask OK')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
        pip install flask flask-socketio pymysql flask-session cryptography python-dotenv
    }
} catch {
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
    pip install flask flask-socketio pymysql flask-session cryptography python-dotenv
}

Write-Host ""
Write-Host "3. Iniciando servidor web..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Green
Write-Host "🌐 Acesse: http://localhost:5000" -ForegroundColor White
Write-Host "👤 Login: usuario@exemplo.com" -ForegroundColor White
Write-Host "🔑 Senha: 123456" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Iniciar a interface web
python web_interface.py
