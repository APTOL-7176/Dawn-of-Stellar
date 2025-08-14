@echo off
chcp 65001 # main.py
echo Dawn of Stellar
echo.
title Dawn of Stellar
set LAUNCHER_POWERSHELL=0
set TERMINAL_MODE=1

echo.
echo =========================================================
echo                     Dawn of Stellar
echo =========================================================
echo.


if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Python
)


echo 🚀 Dawn of Stellar
echo.

python main.py


if %ERRORLEVEL% neq 0 (
    echo.
    echo %ERRORLEVEL%
    echo.
    pause
)


echo.


if exist "*.pyc" del /q "*.pyc"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
pause
