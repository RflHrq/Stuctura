@echo off
setlocal
cd /d "%~dp0"
title Structura

echo.
echo   Structura - desligando o sistema
echo.

docker info >nul 2>&1
if errorlevel 1 (
  echo   O Docker nao esta respondendo: nao ha o que desligar.
  echo.
  pause
  exit /b 0
)

docker compose down
echo.
echo   Desligado. Os registros continuam na pasta coleta\portal.
echo.
ping -n 6 127.0.0.1 >nul
exit /b 0
