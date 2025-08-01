@echo off
chcp 65001 > nul
title Dawn of Stellar - 일반 모드
echo.
echo ========================================
echo    Dawn of Stellar - 로그라이크 게임
echo ========================================
echo.
echo 일반 모드로 게임을 시작합니다...
echo - 기본 4개 직업만 해금 (전사, 아크메이지, 궁수, 도적)
echo - 별조각과 메타 진행 시스템 활성화
echo - 내구도 시스템 포함한 모든 게임 기능
echo.

REM Python 가상환경 확인 및 활성화
if exist ".venv\Scripts\activate.bat" (
    echo Python 가상환경을 활성화합니다...
    call .venv\Scripts\activate.bat
) else (
    echo 가상환경이 없습니다. 전역 Python을 사용합니다.
)

REM config.py 파일을 건드리지 않고 환경변수로 일반모드 설정
set ROGUELIKE_DEV_MODE=false
echo ✅ 일반 모드로 설정되었습니다.

REM Python 실행
echo.
echo 게임을 시작합니다...
echo.
python main.py

REM 오류 처리
if %ERRORLEVEL% neq 0 (
    echo.
    echo 게임 실행 중 오류가 발생했습니다!
    echo Python이 설치되어 있는지 확인해주세요.
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 게임이 종료되었습니다.
pause
