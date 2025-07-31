@echo off
title Dawn Of Stellar - 포터블 실행
echo ===============================================
echo Dawn Of Stellar - 별빛의 여명 (포터블 버전)
echo ===============================================
echo.

REM 포터블 파이썬 디렉토리 설정
set PYTHON_DIR=%~dp0python
set GAME_DIR=%~dp0

REM 포터블 파이썬 존재 확인
if not exist "%PYTHON_DIR%\python.exe" (
    echo [오류] 포터블 파이썬이 설정되지 않았습니다.
    echo 먼저 'setup_portable.bat'를 실행해주세요.
    echo.
    pause
    exit /b 1
)

REM 환경 설정
set PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%
set PYTHONPATH=%GAME_DIR%

echo 게임을 시작합니다...
echo.

REM 게임 실행
"%PYTHON_DIR%\python.exe" main.py

REM 게임 종료 후 대기
echo.
echo 게임이 종료되었습니다.
pause
