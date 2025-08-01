@echo off
chcp 65001 >nul 2>&1

REM 가상환경 활성화 (안전한 방법)
if exist ".venv\Scripts\activate.bat" (
    echo 🔄 가상환경 활성화 중...
    call ".venv\Scripts\activate.bat"
) else (
    echo ⚠️ 가상환경을 찾을 수 없습니다. 파이썬_설치.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

setlocal enabledelayedexpansion

echo ================================================================================
echo 🎮 Dawn Of Stellar - 게임 시작
echo ================================================================================
echo.

REM 가상환경 확인
if not exist ".venv" (
    echo ❌ 가상환경을 찾을 수 없습니다.
    echo.
    echo 먼저 "파이썬_설치.bat"을 실행하여 환경을 설정해주세요.
    echo.
    pause
    exit /b 1
)

REM 가상환경 활성화
echo 🔌 가상환경 활성화 중...
call ".venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo ❌ 가상환경 활성화에 실패했습니다.
    echo.
    echo "파이썬_설치.bat"을 다시 실행해주세요.
    pause
    exit /b 1
)

REM 게임 파일 확인
if not exist "main.py" (
    echo ❌ main.py 파일을 찾을 수 없습니다.
    echo.
    echo 게임 파일이 올바른 위치에 있는지 확인해주세요.
    pause
    exit /b 1
)

echo ✅ 환경 설정 완료
echo.
echo 🚀 Dawn Of Stellar을 시작합니다...
echo.
echo ================================================================================

REM 게임 실행
python main.py

REM 게임 종료 후 메시지
echo.
echo ================================================================================
echo 🎮 게임이 종료되었습니다.
echo.
echo 다시 플레이하려면 이 파일을 다시 실행하세요!
echo ================================================================================
echo.
pause
