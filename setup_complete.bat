@echo off
chcp 65001 >nul
echo ===============================================
echo    ⭐ Dawn Of Stellar 자동 설치 프로그램 ⭐
echo           별빛의 여명 v2.0.0
echo ===============================================
echo.

:: 관리자 권한 확인
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo 🔒 관리자 권한이 필요합니다. 관리자로 다시 실행해주세요.
    echo    우클릭 → "관리자 권한으로 실행"
    pause
    exit /B 1
)

echo 🎮 Dawn Of Stellar 완전 자동 설치를 시작합니다...
echo.

:: 설치 디렉토리 설정
set INSTALL_DIR=%USERPROFILE%\Dawn-of-Stellar
echo 📁 설치 경로: %INSTALL_DIR%
echo.

:: 1. Git 설치 확인 및 자동 설치
echo ===============================================
echo 📥 1단계: Git 설치 확인 및 설치
echo ===============================================

git --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ❌ Git이 설치되지 않았습니다. 자동으로 설치합니다...
    
    :: Git 다운로드 URL
    set GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe
    set GIT_INSTALLER=%TEMP%\git-installer.exe
    
    echo 📥 Git 설치파일을 다운로드하는 중...
    powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%GIT_INSTALLER%' }"
    
    if exist "%GIT_INSTALLER%" (
        echo 🔧 Git을 설치하는 중... (조용한 설치)
        "%GIT_INSTALLER%" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
        echo ✅ Git 설치 완료!
        
        :: PATH 새로고침
        call refreshenv.cmd >nul 2>&1
        set PATH=%PATH%;C:\Program Files\Git\cmd
        
        del "%GIT_INSTALLER%" >nul 2>&1
    ) else (
        echo ❌ Git 다운로드 실패. 수동으로 설치해주세요.
        echo 🌐 https://git-scm.com/download/win
        pause
        exit /B 1
    )
) else (
    echo ✅ Git이 이미 설치되어 있습니다.
)
echo.

:: 2. Python 설치 확인 및 자동 설치
echo ===============================================
echo 🐍 2단계: Python 설치 확인 및 설치
echo ===============================================

python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ❌ Python이 설치되지 않았습니다. 자동으로 설치합니다...
    
    :: Python 다운로드 URL (Python 3.11.7)
    set PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe
    set PYTHON_INSTALLER=%TEMP%\python-installer.exe
    
    echo 📥 Python 설치파일을 다운로드하는 중...
    powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' }"
    
    if exist "%PYTHON_INSTALLER%" (
        echo 🔧 Python을 설치하는 중... (자동 설정)
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0 Include_tcltk=0
        echo ✅ Python 설치 완료!
        
        :: PATH 새로고침
        call refreshenv.cmd >nul 2>&1
        
        del "%PYTHON_INSTALLER%" >nul 2>&1
    ) else (
        echo ❌ Python 다운로드 실패. 수동으로 설치해주세요.
        echo 🌐 https://www.python.org/downloads/
        pause
        exit /B 1
    )
) else (
    echo ✅ Python이 이미 설치되어 있습니다.
    python --version
)
echo.

:: 3. pip 업그레이드
echo ===============================================
echo 📦 3단계: pip 업그레이드
echo ===============================================
echo 🔄 pip을 최신 버전으로 업그레이드하는 중...
python -m pip install --upgrade pip --quiet
echo ✅ pip 업그레이드 완료!
echo.

:: 4. 게임 소스코드 다운로드
echo ===============================================
echo 📥 4단계: 게임 소스코드 다운로드
echo ===============================================

if exist "%INSTALL_DIR%" (
    echo 📁 기존 설치 디렉토리를 제거하는 중...
    rmdir /s /q "%INSTALL_DIR%"
)

echo 📥 GitHub에서 게임 소스코드를 다운로드하는 중...
git clone https://github.com/APTOL-7176/Dawn-of-Stellar.git "%INSTALL_DIR%"

if %errorlevel% NEQ 0 (
    echo ❌ 게임 소스코드 다운로드 실패.
    echo 🌐 인터넷 연결을 확인하고 다시 시도해주세요.
    pause
    exit /B 1
)

echo ✅ 게임 소스코드 다운로드 완료!
echo.

:: 5. 의존성 설치
echo ===============================================
echo 📚 5단계: 필수 라이브러리 설치
echo ===============================================
cd /d "%INSTALL_DIR%"

echo 📦 필수 라이브러리를 설치하는 중...
echo    - pygame (사운드 시스템)
echo    - numpy (수학 연산)
echo    - colorama (컬러 터미널)
echo    - keyboard (키보드 입력)

python -m pip install -r requirements.txt --quiet

if %errorlevel% NEQ 0 (
    echo ❌ 라이브러리 설치 실패. 수동으로 설치를 시도합니다...
    python -m pip install pygame numpy colorama keyboard
    if %errorlevel% NEQ 0 (
        echo ❌ 라이브러리 설치에 실패했습니다.
        echo 💡 관리자 권한으로 다시 실행하거나 수동 설치를 시도해주세요.
        pause
        exit /B 1
    )
)

echo ✅ 모든 라이브러리 설치 완료!
echo.

:: 6. 바탕화면 바로가기 생성
echo ===============================================
echo 🖥️ 6단계: 바탕화면 바로가기 생성
echo ===============================================

set SHORTCUT_PATH=%USERPROFILE%\Desktop\Dawn of Stellar.lnk
set GAME_PATH=%INSTALL_DIR%\main.py

echo 🔗 바탕화면 바로가기를 생성하는 중...

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'python'; $s.Arguments = '%GAME_PATH%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.IconLocation = 'C:\Windows\System32\shell32.dll,14'; $s.Description = 'Dawn Of Stellar - 별빛의 여명 v2.0.0'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo ✅ 바탕화면 바로가기 생성 완료!
) else (
    echo ⚠️ 바탕화면 바로가기 생성에 실패했지만 게임은 정상적으로 실행 가능합니다.
)
echo.

:: 7. 게임 실행 배치파일 생성
echo ===============================================
echo 🚀 7단계: 게임 실행 파일 생성
echo ===============================================

set RUN_SCRIPT=%INSTALL_DIR%\게임시작.bat

echo @echo off > "%RUN_SCRIPT%"
echo chcp 65001 ^>nul >> "%RUN_SCRIPT%"
echo cd /d "%INSTALL_DIR%" >> "%RUN_SCRIPT%"
echo cls >> "%RUN_SCRIPT%"
echo echo ⭐ Dawn Of Stellar - 별빛의 여명 v2.0.0 ⭐ >> "%RUN_SCRIPT%"
echo echo 게임을 시작합니다... >> "%RUN_SCRIPT%"
echo echo. >> "%RUN_SCRIPT%"
echo python main.py >> "%RUN_SCRIPT%"
echo pause >> "%RUN_SCRIPT%"

echo ✅ 게임 실행 파일 생성 완료! (%RUN_SCRIPT%)
echo.

:: 8. Windows Terminal 설정 (선택사항)
echo ===============================================
echo 🖥️ 8단계: Windows Terminal 최적화 (선택사항)
echo ===============================================

where wt >nul 2>&1
if %errorlevel% EQU 0 (
    echo ✅ Windows Terminal이 설치되어 있습니다.
    echo 💡 Windows Terminal에서 게임을 실행하면 더 좋은 화면을 볼 수 있습니다!
    echo    시작 메뉴에서 "Windows Terminal"을 검색하여 실행하세요.
) else (
    echo ⚠️ Windows Terminal이 설치되지 않았습니다.
    echo 💡 Microsoft Store에서 "Windows Terminal"을 설치하면
    echo    더 나은 게임 화면을 경험할 수 있습니다!
)
echo.

:: 설치 완료
echo ===============================================
echo 🎉 설치 완료! 🎉
echo ===============================================
echo.
echo ✅ Dawn Of Stellar v2.0.0이 성공적으로 설치되었습니다!
echo.
echo 📁 설치 경로: %INSTALL_DIR%
echo 🖥️ 바탕화면 바로가기: Dawn of Stellar
echo 🚀 게임 실행 방법:
echo    1) 바탕화면 바로가기 더블클릭
echo    2) %RUN_SCRIPT% 실행
echo    3) 설치 폴더에서 "python main.py" 명령 실행
echo.
echo 🎮 게임 특징:
echo    - 27개 고유 직업군
echo    - Brave 전투 시스템
echo    - 메타 진행 시스템
echo    - 완전한 오디오 지원
echo    - 무한층 던전 탐험
echo.
echo 💡 팁: Windows Terminal에서 실행하면 더 좋은 화면을 볼 수 있습니다!
echo.

:: 즉시 게임 실행 옵션
echo 🚀 지금 바로 게임을 시작하시겠습니까? (Y/N)
set /p START_NOW="   입력: "

if /i "%START_NOW%"=="Y" (
    echo.
    echo 🎮 게임을 시작합니다...
    cd /d "%INSTALL_DIR%"
    python main.py
) else (
    echo.
    echo 🎮 나중에 바탕화면 바로가기를 통해 게임을 즐겨주세요!
)

echo.
echo 📚 문제가 있다면 GitHub Issues에 문의해주세요:
echo    https://github.com/APTOL-7176/Dawn-of-Stellar/issues
echo.
echo 🌟 게임이 마음에 드시면 GitHub에서 Star를 눌러주세요!
echo    https://github.com/APTOL-7176/Dawn-of-Stellar
echo.
pause
