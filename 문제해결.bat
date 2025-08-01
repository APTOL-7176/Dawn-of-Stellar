@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ================================================================================
echo 🔧 Dawn Of Stellar - 문제 해결 도구
echo ================================================================================
echo.

echo 이 도구는 게임 실행 시 발생할 수 있는 문제를 진단하고 해결합니다.
echo.

REM Python 설치 확인
echo 📋 1. Python 설치 상태 확인...
python --version >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python %%i 설치됨
) else (
    echo ❌ Python이 설치되지 않음 또는 PATH에 등록되지 않음
    echo    해결방법: "파이썬_설치.bat" 실행
)

REM 가상환경 확인
echo.
echo 📋 2. 가상환경 상태 확인...
if exist ".venv" (
    echo ✅ 가상환경 폴더 존재
    if exist ".venv\Scripts\python.exe" (
        echo ✅ 가상환경 Python 실행파일 존재
    ) else (
        echo ❌ 가상환경이 손상됨
        echo    해결방법: "파이썬_설치.bat" 다시 실행
    )
) else (
    echo ❌ 가상환경 폴더 없음
    echo    해결방법: "파이썬_설치.bat" 실행
)

REM 게임 파일 확인
echo.
echo 📋 3. 게임 파일 확인...
if exist "main.py" (
    echo ✅ main.py 존재
) else (
    echo ❌ main.py 파일 없음
    echo    해결방법: 게임 파일이 올바른 폴더에 있는지 확인
)

if exist "game" (
    echo ✅ game 폴더 존재
) else (
    echo ❌ game 폴더 없음
    echo    해결방법: 게임 파일이 올바른 폴더에 있는지 확인
)

REM 의존성 패키지 확인
echo.
echo 📋 4. 의존성 패키지 확인...
if exist ".venv" (
    call ".venv\Scripts\activate.bat" >nul 2>&1
    
    python -c "import pygame" >nul 2>&1
    if %errorlevel% == 0 (
        echo ✅ pygame 설치됨
    ) else (
        echo ❌ pygame 설치되지 않음
        echo    해결방법: pip install pygame
    )
    
    python -c "import numpy" >nul 2>&1
    if %errorlevel% == 0 (
        echo ✅ numpy 설치됨
    ) else (
        echo ❌ numpy 설치되지 않음
        echo    해결방법: pip install numpy
    )
    
    python -c "import colorama" >nul 2>&1
    if %errorlevel% == 0 (
        echo ✅ colorama 설치됨
    ) else (
        echo ⚠️  colorama 설치되지 않음 (선택사항)
    )
    
    python -c "import keyboard" >nul 2>&1
    if %errorlevel% == 0 (
        echo ✅ keyboard 설치됨
    ) else (
        echo ⚠️  keyboard 설치되지 않음 (선택사항)
    )
)

REM 사운드 시스템 확인
echo.
echo 📋 5. 사운드 시스템 확인...
if exist "sounds" (
    echo ✅ sounds 폴더 존재
    if exist "sounds\bgm" (
        echo ✅ BGM 폴더 존재
    ) else (
        echo ⚠️  BGM 폴더 없음 (사운드 없어도 게임 실행 가능)
    )
    if exist "sounds\sfx" (
        echo ✅ SFX 폴더 존재
    ) else (
        echo ⚠️  SFX 폴더 없음 (사운드 없어도 게임 실행 가능)
    )
) else (
    echo ⚠️  sounds 폴더 없음 (사운드 없어도 게임 실행 가능)
)

REM 권한 확인
echo.
echo 📋 6. 시스템 권한 확인...
echo test > test_write.tmp 2>nul
if exist "test_write.tmp" (
    del test_write.tmp
    echo ✅ 쓰기 권한 있음
) else (
    echo ❌ 쓰기 권한 없음
    echo    해결방법: 관리자 권한으로 실행하거나 다른 폴더에서 실행
)

REM 메모리 및 시스템 리소스 확인
echo.
echo 📋 7. 시스템 리소스 확인...
for /f "tokens=2 delims=:" %%i in ('wmic OS get TotalVisibleMemorySize /value') do set /a TOTAL_MEM=%%i/1024
for /f "tokens=2 delims=:" %%i in ('wmic OS get FreePhysicalMemory /value') do set /a FREE_MEM=%%i/1024
if defined TOTAL_MEM (
    echo ✅ 총 메모리: !TOTAL_MEM! MB
    if !FREE_MEM! GTR 1000 (
        echo ✅ 여유 메모리: !FREE_MEM! MB (충분함)
    ) else (
        echo ⚠️  여유 메모리: !FREE_MEM! MB (부족할 수 있음)
    )
) else (
    echo ⚠️  메모리 정보를 확인할 수 없음
)

echo.
echo ================================================================================
echo 🔧 자동 복구 옵션
echo ================================================================================
echo.
echo 1. 🔄 가상환경 다시 생성
echo 2. 📦 패키지 다시 설치
echo 3. 🧹 캐시 파일 정리
echo 4. 🎮 강제 게임 실행 시도
echo 5. 📁 사운드 폴더 생성
echo 6. 🚪 종료
echo.

set /p fix_choice="복구 옵션을 선택하세요 (1-6): "

if "!fix_choice!" == "1" goto RECREATE_VENV
if "!fix_choice!" == "2" goto REINSTALL_PACKAGES
if "!fix_choice!" == "3" goto CLEAN_CACHE
if "!fix_choice!" == "4" goto FORCE_RUN
if "!fix_choice!" == "5" goto CREATE_SOUNDS
if "!fix_choice!" == "6" goto END
goto INVALID_FIX

:RECREATE_VENV
echo.
echo 🔄 가상환경을 다시 생성합니다...
if exist ".venv" rmdir /s /q ".venv"
python -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    python -m pip install pygame numpy colorama keyboard
)
echo ✅ 가상환경 재생성 완료
goto END

:REINSTALL_PACKAGES
echo.
echo 📦 패키지를 다시 설치합니다...
call ".venv\Scripts\activate.bat"
python -m pip uninstall -y pygame numpy colorama keyboard
python -m pip install pygame numpy colorama keyboard
echo ✅ 패키지 재설치 완료
goto END

:CLEAN_CACHE
echo.
echo 🧹 캐시 파일을 정리합니다...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "game\__pycache__" rmdir /s /q "game\__pycache__"
echo ✅ 캐시 정리 완료
goto END

:FORCE_RUN
echo.
echo 🎮 게임 강제 실행을 시도합니다...
call ".venv\Scripts\activate.bat"
python main.py
goto END

:CREATE_SOUNDS
echo.
echo 📁 사운드 폴더를 생성합니다...
if not exist "sounds" mkdir sounds
if not exist "sounds\bgm" mkdir sounds\bgm
if not exist "sounds\sfx" mkdir sounds\sfx
echo ✅ 사운드 폴더 생성 완료
goto END

:INVALID_FIX
echo ❌ 잘못된 선택입니다.
goto END

:END
echo.
echo ================================================================================
echo 🔧 문제 해결 도구 종료
echo ================================================================================
echo.
echo 💡 추가 도움이 필요하면:
echo    - SOUND_FIX_GUIDE.md 파일 참조
echo    - README.md 파일 확인
echo    - GitHub Issues에 문제 보고
echo.
pause
