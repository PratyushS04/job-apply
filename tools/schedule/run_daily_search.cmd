@echo off
rem Runs the daily job search and appends its output to logs\discovery\daily_search.log.
rem Used by the "JobApply Daily Search" task (install_daily_search.ps1). You can also run it by hand:
rem   tools\schedule\run_daily_search.cmd candidate
setlocal
cd /d "%~dp0..\.."
set "CANDIDATE=%~1"
if "%CANDIDATE%"=="" set "CANDIDATE=candidate"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
if not exist "logs\discovery" mkdir "logs\discovery"
".venv\Scripts\python.exe" tools\daily_search.py --candidate "%CANDIDATE%" >> "logs\discovery\daily_search.log" 2>&1
exit /b %ERRORLEVEL%
