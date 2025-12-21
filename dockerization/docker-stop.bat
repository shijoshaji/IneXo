@echo off
pushd "%~dp0.."

REM ============================================
REM Docker Stop Script for IneX̂ō
REM ============================================

echo.
echo ========================================
echo  Stopping IneX̂ō (Docker)
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker is not running!
    echo.
    echo If containers were running, they may have already stopped.
    echo.
    pause
    exit /b 0
)

REM Check if containers are running
docker ps | findstr "inexo" >nul 2>&1
if errorlevel 1 (
    echo [INFO] No running containers found.
    echo.
    echo The application is already stopped.
    echo.
    pause
    exit /b 0
)

echo Stopping containers...
echo.

REM Stop the containers
docker-compose -f dockerization\docker-compose.yml down

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to stop containers!
    echo.
    echo You may need to manually stop them using Docker Desktop.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESS! Application stopped
echo ========================================
echo.
echo To start again, run: docker-start.bat
echo.
pause
