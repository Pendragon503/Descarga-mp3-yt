@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Instalador Python + FFmpeg + yt-dlp y ejecutor del script

echo ==========================================================
echo  Instalador de dependencias y lanzador de descargar_audio.py
echo ==========================================================
echo.

:: 0) Comprobar privilegios de administrador; si no, reintentar elevado
>nul 2>&1 net session
if %errorlevel% NEQ 0 (
  echo Reintentando como Administrador...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

:: Variables
set "WORKDIR=%~dp0"
set "PY_OK=0"
set "FF_OK=0"
set "PYEXE=python"
set "TEMP_DIR=%TEMP%\yt_setup"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

echo [1/6] Comprobando Python...
where python >nul 2>&1 && set "PY_OK=1"
if %PY_OK%==0 (
  where py >nul 2>&1 && (set "PYEXE=py" & set "PY_OK=1")
)

if %PY_OK%==0 (
  echo Python no encontrado. Intentando instalar con winget...
  where winget >nul 2>&1
  if %errorlevel%==0 (
    winget install -e --id Python.Python.3 --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel%==0 (
      set "PY_OK=1"
    )
  ) else (
    echo winget no disponible. Intentando instalador oficial...
    set "PY_URL=https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    set "PY_EXE=%TEMP_DIR%\python-installer.exe"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_EXE%'"
    if exist "%PY_EXE%" (
      "%PY_EXE%" /quiet InstallAllUsers=1 PrependPath=1 Include_tcltk=1
      if %errorlevel%==0 set "PY_OK=1"
    )
  )
)

:: Revalidar Python y fijar ejecutable preferido
if %PY_OK%==1 (
  where python >nul 2>&1 && set "PYEXE=python"
  if not "%PYEXE%"=="python" (
    where py >nul 2>&1 && set "PYEXE=py"
  )
) else (
  echo Error: no se pudo instalar Python. Cancelo.
  goto :end_fail
)

echo [2/6] Version de Python:
%PYEXE% --version

echo.
echo [3/6] Instalando/actualizando pip y yt-dlp...
%PYEXE% -m pip install --upgrade pip
if %errorlevel% NEQ 0 echo Aviso: no se pudo actualizar pip y se continuara.
%PYEXE% -m pip install --upgrade yt-dlp
if %errorlevel% NEQ 0 (
  echo Error: no se pudo instalar yt-dlp.
  goto :end_fail
)

echo.
echo [4/6] Comprobando FFmpeg en PATH...
where ffmpeg >nul 2>&1 && set "FF_OK=1"

if %FF_OK%==0 (
  echo FFmpeg no encontrado. Descargando y configurando...
  set "FF_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
  set "FF_ZIP=%TEMP_DIR%\ffmpeg.zip"
  set "FF_DIR=C:\ffmpeg"
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%FF_URL%' -OutFile '%FF_ZIP%'"
  if not exist "%FF_ZIP%" (
    echo Error: no se pudo descargar FFmpeg.
    goto :end_fail
  )
  if not exist "%FF_DIR%" mkdir "%FF_DIR%"
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%FF_ZIP%' -DestinationPath '%FF_DIR%' -Force"
  :: Detectar la carpeta extraida (ffmpeg-*-essentials_build)
  set "FF_BIN="
  for /d %%D in ("%FF_DIR%\ffmpeg-*") do (
    if exist "%%~fD\bin\ffmpeg.exe" set "FF_BIN=%%~fD\bin"
  )
  if "%FF_BIN%"=="" (
    :: Intento alterno: buscar bin en subniveles
    for /r "%FF_DIR%" %%F in (ffmpeg.exe) do (
      set "FF_BIN=%%~dpF"
      goto :foundbin
    )
    :foundbin
  )
  if "%FF_BIN%"=="" (
    echo Error: no se encontro la carpeta bin de FFmpeg tras descomprimir.
    goto :end_fail
  )
  echo Agregando FFmpeg a PATH del sistema: %FF_BIN%
  for /f "tokens=2* delims= " %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path ^| find /i "Path"') do set "SYS_PATH=%%b"
  echo %SYS_PATH% | find /i "%FF_BIN%" >nul || setx /M PATH "%SYS_PATH%;%FF_BIN%" >nul
  set "PATH=%PATH%;%FF_BIN%"
)

echo.
echo [5/6] Verificando FFmpeg:
ffmpeg -version | find /i "ffmpeg" >nul
if %errorlevel% NEQ 0 (
  echo Error: FFmpeg no responde en PATH.
  goto :end_fail
)

echo.
echo [6/6] Verificando yt-dlp:
yt-dlp --version
if %errorlevel% NEQ 0 (
  echo Error: yt-dlp no responde.
  goto :end_fail
)

echo.
echo Dependencias OK.
echo.

:: Ejecutar el script si existe junto al .bat
set "SCRIPT=%WORKDIR%descargar_audio.py"
if exist "%SCRIPT%" (
  echo Ejecutando: %SCRIPT%
  "%PYEXE%" "%SCRIPT%"
) else (
  echo No se encontro "%SCRIPT%".
  echo Coloca descargar_audio.py en la misma carpeta que este .bat y vuelve a ejecutar.
  echo Presiona una tecla para salir...
  pause >nul
  goto :eof
)

goto :eof

:end_fail
echo.
echo Hubo un problema durante la instalacion o verificacion.
echo Revisa los mensajes anteriores. Presiona una tecla para salir...
pause >nul
exit /b 1
