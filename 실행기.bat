@echo off
chcp 65001 > nul
title Dawn of Stellar - 실행기

:: 터미널 모드 설정 (PowerShell 감지 비활성화)
set LAUNCHER_POWERSHELL=0
set TERMINAL_MODE=1

echo.
echo =========================================================
echo          🌟 Dawn of Stellar - 게임 실행기
echo =========================================================
echo.

:: 가상환경 확인 및 활성화
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️ 가상환경을 찾을 수 없습니다. 기본 Python을 사용합니다.
)

:: Python 런처 실행
echo 🚀 Dawn of Stellar 런처 시작...
echo.

python python_launcher.py

:: 오류 처리
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ 게임 실행 중 오류가 발생했습니다.
    echo    오류 코드: %ERRORLEVEL%
    echo.
    pause
)

:: 게임 종료 후 정리
echo.
echo 🎮 게임이 종료되었습니다.
echo 🧹 임시 파일 정리 중...

:: 임시 파일 정리 (선택적)
if exist "*.pyc" del /q "*.pyc"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo ✅ 정리 완료!
echo.
pause
