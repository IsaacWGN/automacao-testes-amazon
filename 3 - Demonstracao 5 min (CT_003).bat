@echo off
chcp 65001 >nul
cd /d "%~dp0automacao_amazon"
set PY=py
where py >nul 2>nul || set PY=python
echo ==== DEMONSTRACAO (5 min): CT_003 - Ordenar por preco ====
echo.
%PY% executar_testes.py CT_003
echo.
pause
