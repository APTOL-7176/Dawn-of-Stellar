@echo off
:: Dawn of Stellar 게임 설치 배치파일
:: UTF-8 인코딩으로 한글 지원
chcp 65001 > nul

title Dawn of Stellar - 게임 설치

:: 컬러 설정
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                    🌟 Dawn of Stellar 게임 설치 🌟                          ║
echo ║                                                                              ║
echo ║                        별들의 새벽 - 로그라이크 RPG                          ║
echo ║                                                                              ║
echo ║                            자동 설치 시스템                                 ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️ 일부 기능은 관리자 권한이 필요할 수 있습니다.
    echo    필요시 우클릭 → "관리자 권한으로 실행"을 해주세요.
    echo.
)

:: 설치 확인
echo 📋 설치할 구성 요소:
echo.
echo    1. 🔗 Git 설치 확인/설치
echo    2. 🐍 Python 3.10+ 설치 확인/설치  
echo    3. 📁 Dawn of Stellar 게임 다운로드
echo    4. 📦 가상환경 설정
echo    5. 📚 Python 패키지 설치
echo    6. 🎵 오디오 시스템 설정
echo    7. 🚀 게임 실행 준비
echo.

set /p install_confirm="🤔 위 구성 요소들을 설치하시겠습니까? (Y/N): "
if /i not "%install_confirm%"=="Y" (
    echo.
    echo 😢 설치가 취소되었습니다.
    echo    나중에 다시 실행해주세요!
    pause
    exit /b 0
)

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                     🚀 설치 시작!                          ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Step 1: Git 설치 확인
echo 🔍 [1/7] Git 설치 상태 확인 중...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git이 설치되지 않았습니다.
    echo.
    echo 📥 Git 설치 페이지를 열겠습니다...
    echo    https://git-scm.com/download/win
    echo.
    set /p git_install="Git을 수동으로 설치한 후 Y를 입력하세요 (Y/N): "
    if /i not "%git_install%"=="Y" (
        echo 😢 Git 설치가 필요합니다. 설치를 중단합니다.
        pause
        exit /b 1
    )
    
    :: Git 재확인
    git --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Git이 여전히 설치되지 않았습니다.
        echo    설치 후 명령 프롬프트를 다시 열어주세요.
        pause
        exit /b 1
    )
)
echo ✅ Git 설치 확인됨
echo.

:: Step 2: Python 설치 확인
echo 🔍 [2/7] Python 설치 상태 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo.
    echo 📥 Python 3.10 이상 설치가 필요합니다.
    echo    https://www.python.org/downloads/
    echo.
    set /p python_install="Python을 수동으로 설치한 후 Y를 입력하세요 (Y/N): "
    if /i not "%python_install%"=="Y" (
        echo 😢 Python 설치가 필요합니다. 설치를 중단합니다.
        pause
        exit /b 1
    )
    
    :: Python 재확인
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python이 여전히 설치되지 않았습니다.
        echo    설치 후 명령 프롬프트를 다시 열어주세요.
        pause
        exit /b 1
    )
)

:: Python 버전 확인
for /f "tokens=2" %%i in ('python --version') do set python_version=%%i
echo ✅ Python %python_version% 설치 확인됨
echo.

:: Step 3: 게임 소스코드 다운로드
echo 📁 [3/7] Dawn of Stellar 게임 다운로드 중...

:: 이미 폴더가 있는지 확인
if exist "Dawn-of-Stellar" (
    echo ⚠️ Dawn-of-Stellar 폴더가 이미 존재합니다.
    set /p overwrite="기존 폴더를 덮어쓰시겠습니까? (Y/N): "
    if /i "%overwrite%"=="Y" (
        echo 🗑️ 기존 폴더 삭제 중...
        rmdir /s /q "Dawn-of-Stellar"
    ) else (
        echo 📁 기존 폴더를 유지합니다.
        cd "Dawn-of-Stellar"
        goto :skip_clone
    )
)

echo 📥 Git에서 게임 소스코드 다운로드 중...
git clone https://github.com/APTOL-7176/Dawn-of-Stellar.git
if errorlevel 1 (
    echo ❌ 게임 다운로드에 실패했습니다.
    echo    인터넷 연결을 확인해주세요.
    pause
    exit /b 1
)

cd "Dawn-of-Stellar"
:skip_clone

echo ✅ 게임 소스코드 다운로드 완료
echo.

:: Step 4: 가상환경 설정
echo 🏗️ [4/7] Python 가상환경 설정 중...

if exist ".venv" (
    echo ⚠️ 가상환경이 이미 존재합니다. 재사용합니다.
) else (
    echo 📦 새 가상환경 생성 중...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
)

echo ✅ 가상환경 설정 완료
echo.

:: Step 5: 패키지 설치
echo 📚 [5/7] Python 패키지 설치 중...

echo 🔄 가상환경 활성화...
call .venv\Scripts\activate.bat

echo 📦 pip 업그레이드...
python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo 📋 필수 패키지 설치 중...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ⚠️ 일부 패키지 설치에 실패했을 수 있습니다.
        echo    게임은 기본 기능으로 실행됩니다.
    )
) else (
    echo 📦 기본 패키지 설치 중...
    pip install pygame colorama requests flask pillow
)

echo ✅ 패키지 설치 완료
echo.

:: Step 6: 오디오 시스템 확인
echo 🎵 [6/7] 오디오 시스템 확인 중...

echo 🔊 pygame 오디오 모듈 테스트...
python -c "import pygame; pygame.mixer.init(); print('✅ 오디오 시스템 정상')" 2>nul
if errorlevel 1 (
    echo ⚠️ 오디오 시스템에 문제가 있을 수 있습니다.
    echo    게임은 소리 없이 실행됩니다.
) else (
    echo ✅ 오디오 시스템 정상
)
echo.

:: Step 7: 게임 실행 테스트
echo 🚀 [7/7] 게임 실행 준비 확인...

if exist "main.py" (
    echo ✅ 게임 메인 파일 확인됨
) else (
    echo ❌ 게임 메인 파일을 찾을 수 없습니다.
    echo    다운로드에 문제가 있을 수 있습니다.
)

if exist "python_launcher.py" (
    echo ✅ Python 런처 확인됨
) else (
    echo ⚠️ Python 런처가 없습니다. 게임은 직접 실행해야 합니다.
)

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                   🎉 설치 완료! 🎉                         ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo 🎮 게임 실행 방법:
echo.
echo    1. 🚀 간편 실행 (권장):
echo       ► "파이썬런처실행.bat" 더블클릭
echo.
echo    2. 🔧 수동 실행:
echo       ► cd Dawn-of-Stellar
echo       ► .venv\Scripts\activate.bat
echo       ► python main.py
echo.
echo    3. 🎵 런처 사용:
echo       ► .venv\Scripts\python.exe python_launcher.py
echo.

echo 📋 설치된 구성 요소:
echo    ✅ Dawn of Stellar 게임
echo    ✅ Python 가상환경
echo    ✅ 필수 Python 패키지
echo    ✅ 오디오 시스템 (pygame)
echo    ✅ 게임 런처
echo.

set /p run_now="🎮 지금 바로 게임을 실행하시겠습니까? (Y/N): "
if /i "%run_now%"=="Y" (
    echo.
    echo 🚀 게임 실행 중...
    
    if exist "파이썬런처실행.bat" (
        echo 📱 Python 런처로 실행...
        call "파이썬런처실행.bat"
    ) else if exist "python_launcher.py" (
        echo 🔧 직접 런처 실행...
        .venv\Scripts\python.exe python_launcher.py
    ) else (
        echo 🎯 게임 직접 실행...
        .venv\Scripts\python.exe main.py
    )
) else (
    echo.
    echo 🎊 설치가 완료되었습니다!
    echo    원할 때 언제든지 게임을 즐기세요!
)

echo.
echo 🌟 Dawn of Stellar에 오신 것을 환영합니다! 🌟
echo.
pause
exit /b 0
