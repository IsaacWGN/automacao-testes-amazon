@echo off
chcp 65001 >nul
cd /d "%~dp0"
copy /Y "03 - Acompanhamento Bugs - Amazon - RESERVA.xlsx" "03 - Acompanhamento Bugs - Amazon.xlsx"
echo Planilha restaurada a partir da RESERVA.
pause
