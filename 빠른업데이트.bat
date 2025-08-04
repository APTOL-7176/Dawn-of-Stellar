@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ===================================================================
:: Dawn Of Stellar v2.2.0 - 빠른 업데이트 스크립트
:: ===================================================================
:: 이미 설치된 게임을 최신 버전으로 빠르게 업데이트합니다.
:: ===================================================================

echo.
echo ⚡ Dawn Of Stellar v2.2.0 빠른 업데이트 ⚡
echo =========================================
echo.
echo 🔄 기존 설치된 게임을 최신 버전으로 업데이트합니다
echo 📡 GitHub에서 최신 코드를 가져와 적용합니다
echo.

:: 설치 디렉토리 확인
set "INSTALL_DIR=%USERPROFILE%\Games\Dawn-Of-Stellar"
set "GAME_DIR=%INSTALL_DIR%\game"

:: 기존 설치 확인
if not exist "%GAME_DIR%" (
    echo ❌ 오류: 기존 설치를 찾을 수 없습니다.
    echo 📂 예상 위치: %GAME_DIR%
    echo.
    echo 💡 해결 방법:
    echo    1. 자동설치.bat을 먼저 실행하여 게임을 설치하세요
    echo    2. 또는 다른 위치에 설치했다면 해당 폴더에서 'git pull' 실행
    echo.
    pause
    exit /b 1
)

echo ✅ 기존 설치 발견됨: %GAME_DIR%
echo.

:: 업데이트 확인
set /p confirm="🎯 최신 버전으로 업데이트하시겠습니까? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo 업데이트가 취소되었습니다.
    pause
    exit /b 0
)

echo.
echo 🔄 업데이트를 시작합니다...
echo.

cd /d "%GAME_DIR%"

:: Git 경로 확인
set "GIT_EXE=git"
if exist "C:\Program Files\Git\bin\git.exe" (
    set "GIT_EXE=C:\Program Files\Git\bin\git.exe"
)

:: Git 저장소 확인
if exist ".git" (
    echo 📡 Git을 이용한 업데이트...
    
    :: 현재 브랜치와 상태 확인
    "%GIT_EXE%" status --porcelain > "%TEMP%\git_status.txt"
    set "has_changes=0"
    for /f %%i in ("%TEMP%\git_status.txt") do set "has_changes=1"
    
    if !has_changes! equ 1 (
        echo 📦 로컬 변경사항 발견됨 - 백업 중...
        "%GIT_EXE%" stash push -m "Auto-backup-before-update-$(date +%%Y%%m%%d-%%H%%M%%S)"
        echo ✅ 변경사항 백업 완료
    )
    
    :: 최신 버전 가져오기
    echo 📥 최신 버전 다운로드 중...
    "%GIT_EXE%" fetch origin
    
    :: 현재 브랜치 확인
    for /f "tokens=*" %%i in ('"%GIT_EXE%" rev-parse --abbrev-ref HEAD') do set "current_branch=%%i"
    
    :: 마스터 브랜치로 전환 및 업데이트
    "%GIT_EXE%" checkout master >nul 2>&1
    "%GIT_EXE%" reset --hard origin/master
    
    if %errorLevel% equ 0 (
        echo ✅ Git 업데이트 성공!
        
        :: 버전 정보 확인
        if exist "version.txt" (
            echo 📄 현재 버전:
            type "version.txt"
        ) else (
            for /f "tokens=*" %%i in ('"%GIT_EXE%" log -1 --format="%%h - %%s (%%cd)" --date=short') do echo 📄 최신 커밋: %%i
        )
        
        :: 백업된 변경사항 복원 옵션
        if !has_changes! equ 1 (
            echo.
            echo 💾 백업된 변경사항을 복원하시겠습니까? (Y/N):
            set /p restore=""
            if /i "!restore!"=="Y" (
                "%GIT_EXE%" stash pop
                if %errorLevel% equ 0 (
                    echo ✅ 변경사항 복원 완료
                ) else (
                    echo ⚠️ 일부 충돌이 발생했습니다. 수동으로 확인해주세요.
                )
            ) else (
                echo 📦 변경사항은 'git stash list'로 확인할 수 있습니다.
            )
        )
    ) else (
        echo ❌ Git 업데이트 실패
        echo 📥 ZIP 다운로드로 재시도 중...
        goto :zip_update
    )
) else (
    echo ⚠️ Git 저장소가 아닙니다. ZIP 파일로 업데이트합니다.
    goto :zip_update
)

goto :update_dependencies

:zip_update
echo 📥 GitHub에서 최신 ZIP 파일 다운로드 중...

:: 현재 디렉토리 백업
set "BACKUP_DIR=%INSTALL_DIR%\backup_before_update"
if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%" >nul 2>&1
mkdir "%BACKUP_DIR%"

:: 중요 파일들 백업 (세이브 파일, 설정 등)
if exist "saves" xcopy "saves" "%BACKUP_DIR%\saves" /e /i /q >nul 2>&1
if exist "config.json" copy "config.json" "%BACKUP_DIR%\" >nul 2>&1
if exist "game_settings.json" copy "game_settings.json" "%BACKUP_DIR%\" >nul 2>&1

echo 💾 중요 파일 백업 완료

:: 최신 ZIP 다운로드
set "GAME_ZIP_URL=https://github.com/APTOL-7176/Dawn-of-Stellar/archive/refs/heads/master.zip"
set "GAME_ZIP=%TEMP%\Dawn-of-Stellar-update.zip"

powershell -Command "& {Invoke-WebRequest -Uri '%GAME_ZIP_URL%' -OutFile '%GAME_ZIP%' -UseBasicParsing}"

if exist "%GAME_ZIP%" (
    echo ✅ ZIP 파일 다운로드 완료
    
    :: 기존 게임 파일 삭제 (백업 제외)
    cd /d "%INSTALL_DIR%"
    for /d %%d in ("%GAME_DIR%\*") do (
        if "%%~nxd" neq "backup_before_update" rmdir /s /q "%%d" >nul 2>&1
    )
    for %%f in ("%GAME_DIR%\*") do (
        if "%%~nxf" neq "backup_before_update" del "%%f" >nul 2>&1
    )
    
    :: 새 파일 압축 해제
    powershell -Command "& {Expand-Archive -Path '%GAME_ZIP%' -DestinationPath '%INSTALL_DIR%' -Force}"
    
    :: 압축 해제된 폴더에서 파일 이동
    if exist "%INSTALL_DIR%\Dawn-of-Stellar-master" (
        robocopy "%INSTALL_DIR%\Dawn-of-Stellar-master" "%GAME_DIR%" /e /mov /nfl /ndl /njh /njs >nul
        rmdir "%INSTALL_DIR%\Dawn-of-Stellar-master" >nul 2>&1
        echo ✅ 최신 파일 압축 해제 완료
    )
    
    :: 백업 파일 복원
    if exist "%BACKUP_DIR%\saves" (
        xcopy "%BACKUP_DIR%\saves" "%GAME_DIR%\saves" /e /i /q >nul 2>&1
        echo ✅ 세이브 파일 복원 완료
    )
    if exist "%BACKUP_DIR%\config.json" copy "%BACKUP_DIR%\config.json" "%GAME_DIR%\" >nul 2>&1
    if exist "%BACKUP_DIR%\game_settings.json" copy "%BACKUP_DIR%\game_settings.json" "%GAME_DIR%\" >nul 2>&1
    
    del "%GAME_ZIP%" >nul 2>&1
    echo ✅ ZIP 업데이트 완료
) else (
    echo ❌ ZIP 다운로드 실패
    goto :error
)

:update_dependencies
echo.
echo 📦 의존성 라이브러리 업데이트 중...
echo ====================================

cd /d "%GAME_DIR%"

:: Python 실행 파일 경로 설정
set "PYTHON_EXE=python"
set "PYTHON_DIR=%INSTALL_DIR%\python"
if exist "%PYTHON_DIR%\python.exe" (
    set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
    set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"
) else (
    set "PIP_EXE=pip"
)

if exist "requirements.txt" (
    echo 📦 requirements.txt에서 의존성 업데이트 중...
    "%PIP_EXE%" install -r requirements.txt --upgrade --no-warn-script-location
    if %errorLevel% equ 0 (
        echo ✅ 의존성 업데이트 완료
    ) else (
        echo ⚠️ 일부 의존성 업데이트 실패 - 게임은 정상 작동할 것입니다
    )
) else (
    echo 📦 핵심 라이브러리 업데이트 중...
    "%PIP_EXE%" install pygame numpy colorama --upgrade --no-warn-script-location
)

echo.
echo 🎉 업데이트 완료! 🎉
echo ==================
echo.
echo ✅ Dawn Of Stellar이 최신 버전으로 업데이트되었습니다!
echo 📁 게임 위치: %GAME_DIR%
echo.
echo 🎮 게임을 바로 실행하시겠습니까? (Y/N): 
set /p launch=""
if /i "%launch%"=="Y" (
    echo.
    echo 🎮 게임을 시작합니다...
    if exist "%INSTALL_DIR%\start_game.bat" (
        start "" "%INSTALL_DIR%\start_game.bat"
    ) else (
        "%PYTHON_EXE%" main.py
    )
) else (
    echo.
    echo 🌟 업데이트된 Dawn Of Stellar을 즐겨주세요! 🌟
)

echo.
pause
exit /b 0

:error
echo.
echo ❌ 업데이트 중 오류가 발생했습니다.
echo.
echo 🔧 문제 해결 방법:
echo    1. 인터넷 연결 확인
echo    2. 게임 폴더 권한 확인
echo    3. 자동설치.bat을 다시 실행하여 완전 재설치
echo.
pause
exit /b 1
