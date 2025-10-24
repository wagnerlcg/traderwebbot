@echo off
title Trader Bot - Modo REAL (Direto)
color 0C

echo.
echo ========================================
echo   TRADER BOT - MODO REAL (DIRETO)
echo ========================================
echo.
echo ⚠️  ATENCAO: MODO REAL ATIVADO! ⚠️
echo.
echo ✅ Modo: REAL (Dinheiro real)
echo ✅ Execução: Direta (sem interface web)
echo ✅ Mensagens: "[!] ATIVO FECHADO"
echo.
echo ATENCAO: Voce esta iniciando o bot em modo REAL!
echo Suas operacoes serao executadas com dinheiro real.
echo.
echo O bot solicitara:
echo  1. Stop Loss (1-50%%)
echo  2. Credenciais IQ Option
echo.
echo Suas credenciais NAO serao armazenadas.
echo.
echo ========================================
echo.
echo TEM CERTEZA QUE DESEJA CONTINUAR?
echo Digite 'SIM' para confirmar ou qualquer tecla para cancelar:
set /p confirmacao=

if /i not "%confirmacao%"=="SIM" (
    echo.
    echo Operacao cancelada pelo usuario.
    pause
    exit /b 0
)

echo.
echo Confirmado! Iniciando modo REAL...

REM Verificar se o executável existe
if not exist "TraderBot-Direto.exe" (
    echo ERRO: TraderBot-Direto.exe nao encontrado!
    echo Certifique-se de que o arquivo esta na mesma pasta.
    pause
    exit /b 1
)

echo.
echo Iniciando Trader Bot em modo REAL (direto)...
echo.
echo Pressione CTRL+C para parar o bot
echo.

REM Executar o bot diretamente (sem interface web)
TraderBot-Direto.exe --mode real --sinais data/sinais.txt

echo.
echo Bot parado.
pause
