@echo off
chcp 65001 > nul
echo ====================================================
echo  ATUALIZAR API DA IQ OPTION
echo ====================================================
echo.

echo Desinstalando versão antiga...
pip uninstall -y iqoptionapi
echo.

echo Instalando versão correta do GitHub...
pip install git+https://github.com/Lu-Yi-Hsun/iqoptionapi.git
echo.

echo Atualizando outras dependências...
pip install --upgrade pandas python-dotenv
echo.

echo ====================================================
echo  ATUALIZAÇÃO CONCLUÍDA!
echo ====================================================
echo.
echo Versão instalada:
pip show iqoptionapi | findstr "Name Version"
echo.
echo IMPORTANTE: A versão correta vem do GitHub,
echo não do PyPI oficial (que está desatualizado)
echo.
pause

