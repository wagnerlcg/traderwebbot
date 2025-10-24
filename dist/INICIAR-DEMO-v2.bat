@echo off
title Trader Bot v2 - Modo DEMO
color 0A

echo.
echo ========================================
echo   TRADER BOT v2 - MODO DEMO
echo ========================================
echo.
echo ✅ Versao: v2 (Mensagens Simplificadas)
echo ✅ Modo: DEMO (Sem dinheiro real)
echo ✅ Autenticacao: MySQL obrigatoria
echo.
echo O bot solicitara:
echo  1. Stop Loss (1-50%%)
echo  2. Credenciais IQ Option
echo.
echo Suas credenciais NAO serao armazenadas.
echo.
echo PREREQUISITOS:
echo - MariaDB/MySQL rodando
echo - Banco 'trader_bot' criado
echo - Usuario cadastrado na tabela 'usuarios'
echo.
echo Usuario padrao: wagnerlcg@gmail.com
echo.
echo ========================================
echo.

REM Verificar se o executável existe
if not exist "TraderBot-Autenticado-v2.exe" (
    echo ERRO: TraderBot-Autenticado-v2.exe nao encontrado!
    echo Certifique-se de que o arquivo esta na mesma pasta.
    pause
    exit /b 1
)

echo Iniciando Trader Bot v2 em modo DEMO...
echo.
echo Acesse: http://localhost:3000
echo Login: wagnerlcg@gmail.com
echo.
echo Pressione CTRL+C para parar o servidor
echo.

REM Executar o bot
TraderBot-Autenticado-v2.exe

echo.
echo Servidor parado.
pause
