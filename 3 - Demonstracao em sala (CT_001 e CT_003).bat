@echo off
chcp 65001 >nul
cd /d "%~dp0automacao_amazon"
set PY=py
where py >nul 2>nul || set PY=python
echo ==== DEMONSTRACAO: CT_001 e CT_003 ====
echo.
%PY% executar_testes.py CT_001 CT_003
echo.
pause
