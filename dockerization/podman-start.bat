@echo off
pushd "%~dp0.."

REM ============================================
REM Podman Start Script for IneX̂ō
REM ============================================

REM Get local IP address for network access
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP_ADDR=%%a
    goto :ip_found
)
:ip_found
REM Trim leading spaces
for /f "tokens=* delims= " %%a in ("%IP_ADDR%") do set IP_ADDR=%%a

echo.
echo ========================================
echo  Starting IneX̂ō with Podman
echo ========================================
echo.

REM Check if Podman is installed
where podman >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Podman is not installed or not in PATH!
    echo.
    echo Please install Podman Desktop from: https://podman-desktop.io/
    echo.
    pause
    exit /b 1
)

echo [OK] Podman is installed
echo.

REM Check if podman-compose is installed
where podman-compose >nul 2>&1
if errorlevel 1 (
    echo [ERROR] podman-compose is not installed!
    echo.
    echo Please install it using: pip install podman-compose
    echo.
    pause
    exit /b 1
)

echo [OK] podman-compose is installed
echo.

REM Check if containers are already running
podman ps | findstr "inexo" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Container is already running!
    echo.
    echo Access the app at: http://localhost:8501
    echo.
    echo To restart, run podman-stop.bat first.
    echo.
    pause
    exit /b 0
)

echo Starting containers...
echo.

echo Starting Auto-Backup Job...
start "ShijoBackup" "localrun\inexo_start_backup_job.bat"

REM Start the containers
podman-compose -f dockerization\docker-compose.yml up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers!
    echo.
    echo Try running: podman-compose up --build
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESS! Application is running
echo ========================================
echo.
echo Local Access:   http://localhost:8501
echo Network Access: http://%IP_ADDR%:8501
echo.
echo ---------------------------------------------------
echo To access from mobile/other devices:
echo Use: http://%IP_ADDR%:8501
echo (Make sure devices are on the same Wi-Fi network)
echo ---------------------------------------------------
echo.
echo To view logs, run: podman-compose logs -f
echo To stop the app, run: podman-stop.bat
echo.
pause
