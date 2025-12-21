@echo off
pushd "%~dp0.."

REM ============================================
REM Docker Start Script for IneX̂ō
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
echo  Starting IneX̂ō with Docker
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    echo Look for the Docker whale icon in your system tray.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if containers are already running
docker ps | findstr "inexo" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Container is already running!
    echo.
    echo Access the app at: http://localhost:8501
    echo.
    echo To restart, run docker-stop.bat first.
    echo.
    pause
    exit /b 0
)

echo Starting containers...
echo.

REM Build and start containers
echo Starting Auto-Backup Job...
start "ShijoBackup" "localrun\inexo_start_backup_job.bat"

REM Start the containers
docker-compose -f dockerization\docker-compose.yml up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers!
    echo.
    echo Try running: docker-compose up --build
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
echo To view logs, run: docker-compose logs -f
echo To stop the app, run: docker-stop.bat
echo.
pause
