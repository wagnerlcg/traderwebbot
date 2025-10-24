@echo off
title Gravação de Vídeo - Trader Bot
color 0A

echo.
echo ========================================
echo    GRAVACAO DE VIDEO - TRADER BOT
echo ========================================
echo.
echo Este script vai preparar o ambiente para
echo gravacao do video de demonstracao.
echo.
echo ========================================
echo.

REM Criar pasta de vídeos se não existir
if not exist "Videos_TraderBot" mkdir Videos_TraderBot
if not exist "Videos_TraderBot\Raw" mkdir Videos_TraderBot\Raw
if not exist "Videos_TraderBot\Edited" mkdir Videos_TraderBot\Edited
if not exist "Videos_TraderBot\Social" mkdir Videos_TraderBot\Social

echo 📁 Pastas criadas:
echo    - Videos_TraderBot\Raw
echo    - Videos_TraderBot\Edited  
echo    - Videos_TraderBot\Social
echo.

echo 🎥 FERRAMENTAS DE GRAVACAO RECOMENDADAS:
echo.
echo 1. OBS Studio (Gratuito) - RECOMENDADO
echo    Download: https://obsproject.com/
echo.
echo 2. Bandicam (Pago)
echo    Download: https://www.bandicam.com/
echo.
echo 3. Camtasia (Pago)
echo    Download: https://www.techsmith.com/camtasia.html
echo.

echo 📋 INSTRUCOES:
echo.
echo 1. Instale uma ferramenta de gravacao
echo 2. Configure para salvar em: Videos_TraderBot\Raw\
echo 3. Execute: python demo_impacto.py
echo 4. Grave a tela durante a execucao
echo 5. Narre os pontos principais
echo.

echo 🎯 ROTEIRO SUGERIDO:
echo.
echo - 0-15s: Introducao
echo - 15-120s: Demonstracao
echo - 120-150s: Resultados
echo - 150-180s: Call to action
echo.

echo 📊 CONFIGURACOES RECOMENDADAS:
echo.
echo - Resolucao: 1920x1080 (Full HD)
echo - Taxa de quadros: 30 FPS
echo - Qualidade: Alta
echo - Formato: MP4
echo.

echo ========================================
echo.

set /p choice="Deseja executar o script de demonstracao agora? (s/n): "
if /i "%choice%"=="s" (
    echo.
    echo Executando demonstracao...
    echo Pressione CTRL+C para parar
    echo.
    python demo_impacto.py
) else (
    echo.
    echo Para executar depois, use: python demo_impacto.py
)

echo.
echo ========================================
echo.
echo 📁 VIDEOS SERAO SALVOS EM:
echo    %CD%\Videos_TraderBot\Raw\
echo.
echo 📖 Para mais informacoes, leia:
echo    Videos_TraderBot\COMO_GRAVAR_VIDEO.md
echo.
echo ========================================
echo.
pause
