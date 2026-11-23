@echo off
chcp 65001 >nul
cd /d "%~dp0automacao_amazon"
set PY=py
where py >nul 2>nul || set PY=python
echo ==== Instalando Selenium e openpyxl ====
%PY% -m pip install -r requirements.txt
echo.
%PY% -c "import selenium, openpyxl; print('OK - Selenium', selenium.__version__, '- openpyxl', openpyxl.__version__)"
echo.
pause
