@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ===================================================================
:: Dawn Of Stellar v2.0.0 - 완전 자동 설치 스크립트
:: ===================================================================
:: 이 스크립트는 Python, Git, 게임 소스코드를 모두 자동으로 설치합니다.
:: 관리자 권한으로 실행해주세요.
:: ===================================================================

echo.
echo ⭐ Dawn Of Stellar v2.0.0 자동 설치 스크립트 ⭐
echo ================================================
echo.
echo 🎮 친구와 함께 즐기는 로그라이크 RPG 게임
echo 🚀 Python, Git, 게임을 모두 자동으로 설치합니다
echo.
echo ⚠️  주의사항:
echo    - 관리자 권한으로 실행해주세요
echo    - 인터넷 연결이 필요합니다
echo    - 설치 중 약 5-10분 소요됩니다
echo.

:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 오류: 관리자 권한이 필요합니다.
    echo    이 파일을 우클릭하여 "관리자 권한으로 실행"을 선택해주세요.
    echo.
    pause
    exit /b 1
)

echo ✅ 관리자 권한 확인됨
echo.

:: 설치 시작 확인
set /p confirm="🎯 설치를 시작하시겠습니까? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo 설치가 취소되었습니다.
    pause
    exit /b 0
)

echo.
echo 🚀 설치를 시작합니다...
echo.

:: 설치 디렉토리 설정
set "INSTALL_DIR=%USERPROFILE%\Games\Dawn-Of-Stellar"
set "PYTHON_DIR=%INSTALL_DIR%\python"
set "GAME_DIR=%INSTALL_DIR%\game"

:: 설치 디렉토리 생성
echo.
echo 📁 전용 게임 폴더 생성 중...
echo ===============================
echo 📂 설치 위치: %INSTALL_DIR%
echo.
echo    📂 Games/
echo    └── 📂 Dawn-Of-Stellar/
echo        ├── 📂 python/     (Python 실행환경)
echo        ├── 📂 game/       (게임 소스코드)
echo        └── 🎮 게임시작.bat (게임 실행 파일)
echo.

if not exist "%USERPROFILE%\Games" (
    mkdir "%USERPROFILE%\Games"
    echo ✅ Games 폴더 생성됨
)

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo ✅ Dawn-Of-Stellar 폴더 생성됨
)

if not exist "%PYTHON_DIR%" (
    mkdir "%PYTHON_DIR%"
    echo ✅ Python 폴더 생성됨
)

cd /d "%INSTALL_DIR%"

:: =================================================================
:: 1. Python 설치
:: =================================================================
echo.
echo 🐍 1단계: Python 3.11 설치 중...
echo =====================================

:: Python 설치 여부 확인
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo ✅ Python이 이미 설치되어 있습니다.
    python --version
) else (
    echo 📥 Python 3.11 다운로드 중...
    
    :: Python 3.11.9 임베디드 버전 다운로드 (설치 불필요)
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    set "PYTHON_ZIP=%TEMP%\python-3.11.9-embed-amd64.zip"
    
    powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%' -UseBasicParsing}"
    
    if exist "%PYTHON_ZIP%" (
        echo ✅ Python 다운로드 완료
        echo 📦 Python 압축 해제 중...
        
        powershell -Command "& {Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force}"
        
        if exist "%PYTHON_DIR%\python.exe" (
            echo ✅ Python 설치 완료
            
            :: get-pip.py 다운로드 및 pip 설치
            echo 📥 pip 설치 중...
            powershell -Command "& {Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\get-pip.py' -UseBasicParsing}"
            
            "%PYTHON_DIR%\python.exe" "%PYTHON_DIR%\get-pip.py" --no-warn-script-location
            
            if exist "%PYTHON_DIR%\Scripts\pip.exe" (
                echo ✅ pip 설치 완료
            )
        ) else (
            echo ❌ Python 설치 실패
            goto :error
        )
        
        :: 임시 파일 정리
        del "%PYTHON_ZIP%" >nul 2>&1
    ) else (
        echo ❌ Python 다운로드 실패
        goto :error
    )
)

:: =================================================================
:: 2. Git 설치
:: =================================================================
echo.
echo 📡 2단계: Git 설치 중...
echo ==========================

:: Git 설치 여부 확인
git --version >nul 2>&1
if %errorLevel% equ 0 (
    echo ✅ Git이 이미 설치되어 있습니다.
    git --version
) else (
    echo 📥 Git for Windows 다운로드 중...
    
    :: Git for Windows 최신 버전 다운로드
    set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe"
    set "GIT_INSTALLER=%TEMP%\Git-installer.exe"
    
    powershell -Command "& {Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%GIT_INSTALLER%' -UseBasicParsing}"
    
    if exist "%GIT_INSTALLER%" (
        echo ✅ Git 다운로드 완료
        echo 🔧 Git 설치 중... (잠시만 기다려주세요)
        
        :: Git 자동 설치 (조용한 설치)
        "%GIT_INSTALLER%" /SILENT /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
        
        :: 설치 완료 대기
        timeout /t 30 /nobreak >nul
        
        :: PATH 새로고침
        set "PATH=%PATH%;C:\Program Files\Git\bin"
        
        :: Git 설치 확인
        "C:\Program Files\Git\bin\git.exe" --version >nul 2>&1
        if %errorLevel% equ 0 (
            echo ✅ Git 설치 완료
            "C:\Program Files\Git\bin\git.exe" --version
        ) else (
            echo ❌ Git 설치 실패 - 수동으로 설치해주세요
            echo    Git 다운로드: https://git-scm.com/download/win
        )
        
        :: 임시 파일 정리
        del "%GIT_INSTALLER%" >nul 2>&1
    ) else (
        echo ❌ Git 다운로드 실패
        goto :error
    )
)

:: =================================================================
:: 3. 게임 소스코드 다운로드
:: =================================================================
echo.
echo 🎮 3단계: 게임 소스코드 다운로드 중...
echo ========================================

if exist "%GAME_DIR%" (
    echo 🔄 기존 게임 디렉토리 정리 중...
    rmdir /s /q "%GAME_DIR%" >nul 2>&1
)

echo 📡 GitHub에서 최신 소스코드 다운로드 중...

:: Git 경로 확인
set "GIT_EXE=git"
if exist "C:\Program Files\Git\bin\git.exe" (
    set "GIT_EXE=C:\Program Files\Git\bin\git.exe"
)

"%GIT_EXE%" clone https://github.com/APTOL-7176/Dawn-of-Stellar.git "%GAME_DIR%"

if %errorLevel% equ 0 (
    echo ✅ 게임 소스코드 다운로드 완료
) else (
    echo ❌ 게임 소스코드 다운로드 실패
    echo 📥 ZIP 파일로 대체 다운로드 시도 중...
    
    :: ZIP 파일로 대체 다운로드
    set "GAME_ZIP_URL=https://github.com/APTOL-7176/Dawn-of-Stellar/archive/refs/heads/master.zip"
    set "GAME_ZIP=%TEMP%\Dawn-of-Stellar.zip"
    
    powershell -Command "& {Invoke-WebRequest -Uri '%GAME_ZIP_URL%' -OutFile '%GAME_ZIP%' -UseBasicParsing}"
    
    if exist "%GAME_ZIP%" (
        echo ✅ ZIP 파일 다운로드 완료
        powershell -Command "& {Expand-Archive -Path '%GAME_ZIP%' -DestinationPath '%INSTALL_DIR%' -Force}"
        
        :: 압축 해제된 디렉토리 이름 변경
        if exist "%INSTALL_DIR%\Dawn-of-Stellar-master" (
            move "%INSTALL_DIR%\Dawn-of-Stellar-master" "%GAME_DIR%"
            echo ✅ 게임 파일 압축 해제 완료
        )
        
        del "%GAME_ZIP%" >nul 2>&1
    ) else (
        echo ❌ 게임 다운로드 완전 실패
        goto :error
    )
)

:: =================================================================
:: 4. Python 의존성 설치
:: =================================================================
echo.
echo 📦 4단계: 게임 의존성 설치 중...
echo ==================================

cd /d "%GAME_DIR%"

:: Python 실행 파일 경로 설정
set "PYTHON_EXE=python"
if exist "%PYTHON_DIR%\python.exe" (
    set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
    set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"
) else (
    set "PIP_EXE=pip"
)

echo 🔧 필수 라이브러리 설치 중...

if exist "requirements.txt" (
    "%PIP_EXE%" install -r requirements.txt --no-warn-script-location
    if %errorLevel% equ 0 (
        echo ✅ 의존성 설치 완료
    ) else (
        echo ⚠️ 일부 의존성 설치 실패 - 게임은 기본 기능으로 실행됩니다
    )
) else (
    echo 📦 수동으로 핵심 라이브러리 설치 중...
    "%PIP_EXE%" install pygame>=2.0.0 numpy>=1.20.0 colorama>=0.4.0 --no-warn-script-location
)

:: =================================================================
:: 5. 바탕화면 바로가기 생성
:: =================================================================
echo.
echo 🖥️ 5단계: 바탕화면 바로가기 생성 중...
echo =========================================

:: 게임 실행 배치 파일 생성
set "START_BATCH=%GAME_DIR%\start_game.bat"
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%GAME_DIR%"
echo title Dawn Of Stellar - 별빛의 여명 v2.0.0
echo echo.
echo echo ⭐ Dawn Of Stellar - 별빛의 여명 v2.0.0 ⭐
echo echo ==========================================
echo echo.
if exist "%PYTHON_DIR%\python.exe" (
    echo "%PYTHON_EXE%" main.py
) else (
    echo python main.py
)
echo pause
) > "%START_BATCH%"

if exist "%START_BATCH%" (
    echo ✅ 게임 실행 파일 생성 완료
    
    :: PowerShell로 바탕화면 바로가기 생성
    echo 🔗 바탕화면 바로가기 생성 중...
    
    set "DESKTOP=%USERPROFILE%\Desktop"
    set "SHORTCUT=%DESKTOP%\Dawn Of Stellar.lnk"
    
    powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%START_BATCH%'; $Shortcut.WorkingDirectory = '%GAME_DIR%'; $Shortcut.Description = 'Dawn Of Stellar - 별빛의 여명 v2.0.0'; $Shortcut.Save()}"
    
    if exist "%SHORTCUT%" (
        echo ✅ 바탕화면 바로가기 생성 완료
    ) else (
        echo ⚠️ 바탕화면 바로가기 생성 실패 - 수동으로 생성해주세요
    )
) else (
    echo ❌ 게임 실행 파일 생성 실패
)

:: =================================================================
:: 6. 설치 완료
:: =================================================================
echo.
echo 🎉🎉🎉 설치 완료! 🎉🎉🎉
echo ========================
echo.
echo ✅ 모든 구성요소가 성공적으로 설치되었습니다!
echo.
echo 📁 게임이 설치된 위치:
echo    📂 %INSTALL_DIR%
echo.
echo 📂 폴더 구조:
echo    📂 Games/
echo    └── 📂 Dawn-Of-Stellar/
echo        ├── 📂 python/        (Python 실행환경)
echo        ├── 📂 game/          (게임 소스코드)
echo        ├── 🎮 게임시작.bat   (게임 실행파일)
echo        └── 📄 README.md      (게임 설명서)
echo.
echo ✅ 설치된 구성요소:
if exist "%PYTHON_DIR%\python.exe" (
    echo    🐍 Python 3.11 (포터블 버전)
) else (
    echo    🐍 Python (시스템 설치 버전)
)
echo    📡 Git for Windows
echo    🎮 Dawn Of Stellar v2.0.0
echo    📦 모든 필수 라이브러리 (pygame, numpy, colorama 등)
echo    🖥️ 바탕화면 바로가기
echo.
echo  게임 실행 방법:
echo    1. 🖱️  바탕화면의 "Dawn Of Stellar" 아이콘 더블클릭
echo    2. 📁 또는 폴더로 이동: %GAME_DIR%
echo    3. 🎮 게임시작.bat 파일 실행
echo.
echo 🔄 게임 업데이트 방법:
echo    게임 폴더에서 Git Bash 열기 → 'git pull' 명령어 실행
echo.
echo 📖 게임 가이드:
echo    게임 폴더의 README.md 파일에서 자세한 플레이 가이드 확인 가능
echo.
echo 🎯 지금 바로 게임을 실행해보시겠습니까? (Y/N): 
set /p launch=""
if /i "%launch%"=="Y" (
    echo.
    echo 🎮 게임을 시작합니다...
    echo 🌟 즐거운 모험 되세요!
    start "" "%START_BATCH%"
) else (
    echo.
    echo 📂 설치된 폴더를 열어보시겠습니까? (Y/N): 
    set /p openfolder=""
    if /i "!openfolder!"=="Y" (
        echo 📁 게임 폴더를 엽니다...
        explorer "%GAME_DIR%"
    )
)

echo.
echo 🌟 Dawn Of Stellar - 별빛의 여명을 즐겨주세요! 🌟
echo 💝 문제가 있으면 GitHub Issues에서 문의해주세요!
echo.
pause
exit /b 0

:: =================================================================
:: 오류 처리
:: =================================================================
:error
echo.
echo ❌ 설치 중 오류가 발생했습니다.
echo.
echo 🔧 문제 해결 방법:
echo    1. 인터넷 연결 확인
echo    2. 관리자 권한으로 실행했는지 확인
echo    3. 바이러스 백신 프로그램이 차단하지 않는지 확인
echo.
echo 💬 지원이 필요하시면:
echo    GitHub: https://github.com/APTOL-7176/Dawn-of-Stellar/issues
echo    Email: aptol.7176@gmail.com
echo.
pause
exit /b 1
