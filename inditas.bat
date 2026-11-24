@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtualis kornyezet letrehozasa...
    py -3 -m venv .venv
    if errorlevel 1 goto :hiba
)

".venv\Scripts\python.exe" -c "import pandas, numpy, matplotlib, sklearn" >nul 2>&1
if errorlevel 1 (
    echo Fuggosegek telepitese...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :hiba
)

".venv\Scripts\python.exe" main.py
if errorlevel 1 goto :hiba
exit /b 0

:hiba
echo.
echo Hiba tortent. Ellenorizd a fenti hibauzenetet.
echo Python 3.11 vagy ujabb szukseges, Tcl/Tk osszetevovel.
echo Az elso telepiteshez internetkapcsolat is kell.
pause
exit /b 1