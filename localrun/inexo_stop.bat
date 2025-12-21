@echo off
pushd "%~dp0.."

taskkill /FI "WINDOWTITLE eq ShijoFinTracker" /T /F
