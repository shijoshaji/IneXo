@echo off
pushd "%~dp0.."

title IneX̂ō
echo Starting Auto-Backup Job...
start "ShijoBackup" /D "%~dp0" "inexo_start_backup_job.bat"

echo Starting IneX̂ō...
call venv\Scripts\activate
streamlit run app.py

@REM For multiple devices
@REM echo ---------------------------------------------------
@REM echo To access from mobile/other devices:
@REM echo URL: http://192.168.0.102:8501
@REM echo (Make sure devices are on the same Wi-Fi)
@REM echo ---------------------------------------------------
@REM streamlit run app.py --server.address=0.0.0.0
pause
