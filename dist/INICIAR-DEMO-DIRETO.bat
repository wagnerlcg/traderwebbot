@echo off
title Trader Bot - Modo DEMO (Direto)
color 0A

echo.
echo ========================================
echo   TRADER BOT - MODO DEMO (DIRETO)
echo ========================================
echo.
echo ✅ Modo: DEMO (Sem dinheiro real)
echo ✅ Execução: Direta (sem interface web)
echo ✅ Mensagens: "[!] ATIVO FECHADO"
echo.
echo O bot solicitara:
echo  1. Stop Loss (1-50%%)
echo  2. Credenciais IQ Option
echo.
echo Suas credenciais NAO serao armazenadas.
echo.
echo ========================================
echo.

REM Verificar se o executável existe
if not exist "TraderBot-Direto.exe" (
    echo ERRO: TraderBot-Direto.exe nao encontrado!
    echo Certifique-se de que o arquivo esta na mesma pasta.
    pause
    exit /b 1
)

echo Iniciando Trader Bot em modo DEMO (direto)...
echo.
echo Pressione CTRL+C para parar o bot
echo.

REM Executar o bot diretamente (sem interface web)
TraderBot-Direto.exe --mode demo --sinais data/sinais.txt

echo.
echo Bot parado.
pause
