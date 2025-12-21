@echo off
pushd "%~dp0.."

echo Starting Auto-Backup Job...
powershell -ExecutionPolicy Bypass -File "localrun\inexo_auto_backup_db.ps1"
pause
