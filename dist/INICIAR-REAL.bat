@echo off
echo ===================================
echo   Trader Bot - Modo REAL
echo ===================================
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
pause
echo.
python bot/main.py --mode real --sinais data/sinais.txt
echo.
pause
