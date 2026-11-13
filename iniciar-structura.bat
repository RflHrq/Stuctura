@echo off
setlocal
cd /d "%~dp0"
title Structura

echo.
echo   Structura - subindo o sistema
echo.

docker info >nul 2>&1
if errorlevel 1 (
  echo   O Docker nao esta respondendo.
  echo   Abra o Docker Desktop, espere ele terminar de iniciar
  echo   e clique neste arquivo de novo.
  echo.
  pause
  exit /b 1
)

docker compose up -d --build
if errorlevel 1 (
  echo.
  echo   A subida falhou. A mensagem acima diz o motivo.
  echo.
  pause
  exit /b 1
)

echo.
echo   Esperando o sistema responder...
set /a tentativas=0

rem A espera usa ping, e nao timeout: timeout falha sem console,
rem e ai as tentativas se esgotam em segundos sem esperar nada.
:espera
curl -s -o nul -m 3 http://127.0.0.1:8010/topicos
if not errorlevel 1 goto pronto
set /a tentativas+=1
if %tentativas% geq 40 goto demorou
ping -n 3 127.0.0.1 >nul
goto espera

:pronto
echo.
echo   No ar:  http://127.0.0.1:8010
echo.
echo   Pode fechar esta janela: o sistema continua ligado, e volta
echo   sozinho quando o Docker iniciar. Para desligar, use o
echo   parar-structura.bat.
echo.
echo   Os registros das sessoes ficam na pasta coleta\portal.
echo.
start "" http://127.0.0.1:8010
ping -n 9 127.0.0.1 >nul
exit /b 0

:demorou
echo.
echo   O sistema nao respondeu em 80 segundos. O que ele diz:
echo.
docker compose logs --tail 30 portal
echo.
pause
exit /b 1
