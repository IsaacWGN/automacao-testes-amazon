@echo off
chcp 65001 >nul
cd /d "%~dp0automacao_amazon"
set PY=py
where py >nul 2>nul || set PY=python
echo ==== ENSAIO: executando os 7 casos automatizados ====
echo A planilha deve estar FECHADA no Excel.
echo.
%PY% executar_testes.py
echo.
echo Depois do ensaio, rode '4 - Restaurar planilha.bat' antes da aula.
pause
