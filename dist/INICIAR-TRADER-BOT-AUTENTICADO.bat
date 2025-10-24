@echo off
title Trader Bot - Sistema Autenticado
color 0A

echo.
echo ========================================
echo    TRADER BOT - SISTEMA AUTENTICADO
echo ========================================
echo.
echo Iniciando Trader Bot com autenticacao MySQL...
echo.
echo PREREQUISITOS:
echo - MariaDB/MySQL rodando
echo - Banco 'trader_bot' criado
echo - Tabela 'usuarios' configurada
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

echo Iniciando servidor...
echo.
echo Acesse: http://localhost:3000
echo.
echo Pressione CTRL+C para parar o servidor
echo.

REM Executar o bot
TraderBot-Autenticado-v2.exe

echo.
echo Servidor parado.
pause
