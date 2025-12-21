@echo off
pushd "%~dp0.."

REM ============================================
REM Podman Stop Script for IneX̂ō
REM ============================================

echo.
echo ========================================
echo  Stopping IneX̂ō (Podman)
echo ========================================
echo.

REM Check if Podman is installed
where podman >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Podman is not installed or not in PATH!
    echo.
    echo Cannot stop containers without Podman.
    echo.
    pause
    exit /b 1
)

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

REM Check if containers are running
podman ps | findstr "inexo" >nul 2>&1
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
podman-compose -f dockerization\docker-compose.yml down

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to stop containers!
    echo.
    echo You may need to manually stop them using: podman stop inexo
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESS! Application stopped
echo ========================================
echo.
echo To start again, run: podman-start.bat
echo.
pause
