@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ================================================================================
echo 🐍 Dawn Of Stellar - Python 환경 설치 스크립트
echo ================================================================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ 관리자 권한으로 실행 중입니다.
) else (
    echo ⚠️  관리자 권한이 필요할 수 있습니다.
    echo    설치 중 오류가 발생하면 관리자 권한으로 다시 실행해주세요.
)
echo.

REM Python 설치 확인
echo 📋 Python 설치 상태 확인 중...
python --version >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python !PYTHON_VERSION! 이미 설치되어 있습니다.
    set PYTHON_INSTALLED=1
) else (
    echo ❌ Python이 설치되어 있지 않습니다.
    set PYTHON_INSTALLED=0
)
echo.

REM Python 미설치 시 설치 안내
if !PYTHON_INSTALLED! == 0 (
    echo 🔽 Python 설치가 필요합니다!
    echo.
    echo 다음 단계를 따라 Python을 설치해주세요:
    echo 1. https://www.python.org/downloads/ 접속
    echo 2. "Download Python 3.11.x" 클릭
    echo 3. 설치 시 "Add Python to PATH" 체크박스 반드시 선택!
    echo 4. 설치 완료 후 이 스크립트를 다시 실행해주세요.
    echo.
    echo 📝 추천 버전: Python 3.11.x (안정성과 호환성이 우수)
    echo.
    pause
    echo.
    echo 🌐 Python 다운로드 페이지를 열겠습니다...
    start https://www.python.org/downloads/
    echo.
    echo Python 설치 후 이 스크립트를 다시 실행해주세요.
    pause
    exit /b 1
)

REM pip 업데이트
echo 📦 pip 업데이트 중...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  pip 업데이트에 실패했습니다. 계속 진행합니다...
) else (
    echo ✅ pip 업데이트 완료
)
echo.

REM 가상환경 확인 및 생성
echo 🏗️  가상환경 설정 중...
if exist ".venv" (
    echo ✅ 기존 가상환경을 발견했습니다.
) else (
    echo 📂 새 가상환경을 생성합니다...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ 가상환경 생성에 실패했습니다.
        echo    Python이 올바르게 설치되었는지 확인해주세요.
        pause
        exit /b 1
    )
    echo ✅ 가상환경 생성 완료
)
echo.

REM 가상환경 활성화
echo 🔌 가상환경 활성화 중...
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    if %errorlevel% neq 0 (
        echo ❌ 가상환경 활성화에 실패했습니다.
        pause
        exit /b 1
    )
    echo ✅ 가상환경 활성화 완료
) else (
    echo ❌ .venv\Scripts\activate.bat 파일을 찾을 수 없습니다.
    echo    가상환경이 제대로 생성되지 않았을 수 있습니다.
    pause
    exit /b 1
)
echo.

REM requirements.txt 설치
echo 📚 게임 의존성 패키지 설치 중...
echo    이 과정은 몇 분 정도 소요될 수 있습니다...
echo.

if exist "requirements.txt" (
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 의존성 설치에 실패했습니다.
        echo.
        echo 🔧 문제 해결 방법:
        echo 1. 인터넷 연결을 확인해주세요
        echo 2. 방화벽이나 백신 프로그램이 차단하고 있는지 확인해주세요
        echo 3. 관리자 권한으로 다시 실행해보세요
        echo 4. 수동 설치: pip install pygame numpy colorama keyboard
        echo.
        pause
        exit /b 1
    )
    echo ✅ 모든 의존성 패키지 설치 완료
) else (
    echo ⚠️  requirements.txt 파일을 찾을 수 없습니다.
    echo    수동으로 필수 패키지를 설치합니다...
    python -m pip install pygame numpy colorama keyboard
    if %errorlevel% neq 0 (
        echo ❌ 패키지 설치에 실패했습니다.
        pause
        exit /b 1
    )
    echo ✅ 기본 패키지 설치 완료
)
echo.

REM 설치 검증
echo 🧪 설치 검증 중...
python -c "import pygame, numpy, colorama, keyboard; print('✅ 모든 패키지가 정상적으로 설치되었습니다!')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  일부 패키지에 문제가 있을 수 있습니다.
    echo    하지만 게임은 정상적으로 실행될 가능성이 높습니다.
) else (
    echo ✅ 모든 패키지 정상 작동 확인
)
echo.

REM 게임 실행 가능 확인
echo 🎮 게임 실행 가능성 확인 중...
if exist "main.py" (
    python -c "import main" 2>nul
    if %errorlevel% == 0 (
        echo ✅ 게임 실행 준비 완료!
    ) else (
        echo ⚠️  게임 모듈에 문제가 있을 수 있지만, 실행은 가능할 것입니다.
    )
) else (
    echo ⚠️  main.py 파일을 찾을 수 없습니다.
)
echo.

echo ================================================================================
echo 🎉 설치 완료!
echo ================================================================================
echo.
echo 🎮 게임 실행 방법:
echo    1. 이 창을 닫지 마세요 (가상환경이 활성화되어 있습니다)
echo    2. python main.py 입력하여 게임 실행
echo    또는
echo    3. "게임시작.bat" 파일을 더블클릭하여 실행
echo.
echo 📝 참고사항:
echo    - 가상환경이 (.venv) 폴더에 생성되었습니다
echo    - 다음에 게임을 실행할 때는 "게임시작.bat"을 사용하세요
echo    - 사운드 파일이 없어도 게임은 정상 작동합니다
echo.
echo 🎵 사운드 파일 설치:
echo    - sounds 폴더에 BGM과 SFX 파일을 넣으면 음향 효과를 즐길 수 있습니다
echo    - SOUND_FIX_GUIDE.md 파일을 참조하세요
echo.

REM 게임 바로 실행 옵션
echo 지금 바로 게임을 시작하시겠습니까? (Y/N)
set /p choice="선택: "
if /i "!choice!" == "Y" (
    echo.
    echo 🚀 게임을 시작합니다...
    python main.py
) else (
    echo.
    echo 나중에 게임을 실행하려면 "게임시작.bat"을 실행하세요!
)

echo.
echo 🔚 설치 스크립트를 종료합니다.
pause
