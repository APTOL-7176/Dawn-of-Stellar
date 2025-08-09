@echo off
echo ====================================
echo    Dawn of Stellar - PowerShell 실행
echo ====================================
echo.
echo 최적의 화면 표시를 위해 PowerShell에서 게임을 실행합니다...
echo.
powershell.exe -ExecutionPolicy Bypass -Command "& { cd '%~dp0'; .\.venv\Scripts\python.exe main.py }"
pause
