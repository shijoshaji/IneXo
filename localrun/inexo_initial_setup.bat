@echo off
pushd "%~dp0.."

echo ===================================================
echo   Initial Setup for IneX̂ō
echo ===================================================
echo.
echo 1. Removing broken virtual environment...
if exist venv (
    rmdir /s /q venv
)

echo 2. Creating new virtual environment...
python -m venv venv

echo 3. Activating and installing requirements...
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo ===================================================
echo   Setup Complete! You can now run the app.
echo ===================================================
pause
