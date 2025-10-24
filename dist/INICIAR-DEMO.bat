@echo off
echo ===================================
echo   Trader Bot - Modo DEMO
echo ===================================
echo.
echo O bot solicitara:
echo  1. Stop Loss (1-50%%)
echo  2. Credenciais IQ Option
echo.
echo Suas credenciais NAO serao armazenadas.
echo.
echo.
python C:\Users\conta\apps-python\web-trader-bot-sinais\bot\main.py --mode demo --sinais data/sinais.txt
echo.
pause
