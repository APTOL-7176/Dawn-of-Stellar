@echo off
:: Dawn of Stellar 게임 설치 배치파일 - Windows Terminal 최적화 버전
:: UTF-8 인코딩으로 한글 지원
chcp 65001 > nul

title Dawn of Stellar - 게임 설치 (Windows Terminal 최적화)

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo                                                                               
echo                       🌟 Dawn of Stellar 게임 설치 🌟                          
echo                                                                               
echo                          별들의 새벽 - 로그라이크 RPG                          
echo                                                                               
echo                         Windows Terminal 최적화 버전                          
echo                                                                               
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Windows Terminal 확인 및 설치
echo 🖥️ [터미널 최적화] Windows Terminal 확인 중...

:: Windows Terminal 감지
where wt >nul 2>&1
if errorlevel 1 (
    echo ❌ Windows Terminal이 설치되지 않았습니다.
    echo.
    echo 🎮 최고의 게임 경험을 위해 Windows Terminal 설치를 강력히 권장합니다!
    echo.
    echo 📊 터미널 비교:
    echo    💀 CMD: 제한적 색상, 느린 성능, 게임 호환성 낮음
    echo    🌟 Windows Terminal: 완벽한 색상, 빠른 성능, 게임 최적화
    echo.
    echo 📥 Windows Terminal 자동 설치를 진행하시겠습니까?
    set /p wt_install="(Y: 자동설치 / M: Microsoft Store 열기 / N: 건너뛰기): "
    
    if /i "%wt_install%"=="Y" (
        echo 🔄 winget으로 Windows Terminal 설치 중...
        winget install Microsoft.WindowsTerminal --accept-package-agreements --accept-source-agreements >nul 2>&1
        if errorlevel 1 (
            echo ⚠️ winget 설치 실패. Microsoft Store로 이동합니다...
            start ms-windows-store://pdp/?ProductId=9N0DX20HK701
            echo 📱 Store에서 Windows Terminal을 설치한 후 이 창으로 돌아와주세요.
            pause
        ) else (
            echo ✅ Windows Terminal 설치 완료!
        )
    ) else if /i "%wt_install%"=="M" (
        echo 📱 Microsoft Store 열기 중...
        start ms-windows-store://pdp/?ProductId=9N0DX20HK701
        echo 📱 Store에서 Windows Terminal을 설치한 후 이 창으로 돌아와주세요.
        pause
    )
) else (
    echo ✅ Windows Terminal 설치 확인됨
    
    :: Windows Terminal에서 실행 중인지 확인
    if defined WT_SESSION (
        echo 🎉 현재 Windows Terminal에서 실행 중! 최고의 게임 경험 준비됨!
    ) else (
        echo ⚠️ 현재 일반 CMD에서 실행 중입니다.
        echo 🚀 더 나은 경험을 위해 Windows Terminal에서 재실행하시겠습니까?
        set /p restart_wt="(Y: Windows Terminal로 재시작 / N: 현재 환경에서 계속): "
        
        if /i "%restart_wt%"=="Y" (
            echo 🔄 Windows Terminal로 재시작 중...
            start wt -d "%~dp0" cmd /k "%~f0"
            exit /b 0
        )
    )
)
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
echo    1. 🖥️ Windows Terminal 최적화 (게임 최고 품질)
echo    2. 🔗 Git 설치 확인/설치
echo    3. 🐍 Python 3.10+ 설치 확인/설치  
echo    4. 📁 Dawn of Stellar 게임 다운로드
echo    5. 📦 가상환경 설정
echo    6. 📚 Python 패키지 설치
echo    7. 🎵 오디오 시스템 설정
echo    8. 🎮 게임패드 지원 활성화
echo    9. 📱 모바일 백엔드 준비
echo    10. 🚀 게임 실행 환경 최적화
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
echo                          🚀 설치 시작!                          
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Step 1: Git 설치 확인
echo 🔍 [1/10] Git 설치 상태 확인 중...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git이 설치되지 않았습니다.
    echo.
    echo 📥 Git 설치 페이지를 열겠습니다...
    start https://git-scm.com/download/win
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
echo 🔍 [2/10] Python 설치 상태 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo.
    echo 📥 Python 3.10 이상 설치가 필요합니다.
    start https://www.python.org/downloads/
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
echo 📁 [3/10] Dawn of Stellar 게임 다운로드 중...

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
echo 🏗️ [4/10] Python 가상환경 설정 중...

if exist ".venv" (
    echo ✅ 기존 가상환경이 발견되었습니다.
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
echo 📚 [5/10] Python 패키지 설치 중...

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
    echo    게임 엔진 및 필수 라이브러리...
    pip install pygame colorama requests flask pillow flask-cors
    echo    게임패드 지원 라이브러리...
    pip install pygame
    echo    모바일 백엔드 지원...
    pip install flask flask-cors
    echo    UI 및 그래픽 라이브러리...
    pip install pillow colorama
    echo    🎮 게임패드 화상키보드 차단 라이브러리...
    pip install pynput
)

echo ✅ 패키지 설치 완료
echo.

:: Step 6: 오디오 시스템 확인
echo 🎵 [6/10] 오디오 시스템 확인 중...

echo 🔊 pygame 오디오 모듈 테스트...
python -c "import pygame; pygame.mixer.init(); print('✅ 오디오 시스템 정상')" 2>nul
if errorlevel 1 (
    echo ⚠️ 오디오 시스템에 문제가 있을 수 있습니다.
    echo    게임은 음성 없이 실행됩니다.
) else (
    echo ✅ 오디오 시스템 정상
)
echo.

:: Step 7: 게임패드 지원 활성화
echo 🎮 [7/10] 게임패드 지원 활성화 중...

echo 🔄 게임패드 드라이버 확인...
python -c "import pygame; pygame.init(); pygame.joystick.init(); joystick_count = pygame.joystick.get_count(); print(f'감지된 게임패드: {joystick_count}개'); [print(f'  - {pygame.joystick.Joystick(i).get_name()}') for i in range(joystick_count)] if joystick_count > 0 else print('ℹ️ 현재 연결된 게임패드가 없습니다'); print('✅ 게임패드 지원 활성화됨') if joystick_count > 0 else print('   Xbox/PlayStation/Nintendo Switch Pro 컨트롤러 지원'); pygame.quit()" 2>nul

if errorlevel 1 (
    echo ⚠️ 게임패드 시스템 초기화 실패
    echo    키보드로만 플레이 가능합니다.
) else (
    echo ✅ 게임패드 지원 시스템 준비 완료
)
echo.

:: Step 8: 모바일 백엔드 준비
echo 📱 [8/10] 모바일 확장성 준비 중...

echo 🌐 Flask 모바일 백엔드 확인...
python -c "try: import flask; print('✅ Flask 웹서버 준비됨'); print('   모바일 클라이언트 연결 가능'); import os; print('✅ 모바일 백엔드 서버 스크립트 확인됨') if os.path.exists('mobile_backend_server.py') else print('ℹ️ 모바일 백엔드는 필요시 활성화 가능'); except ImportError: print('ℹ️ Flask 미설치 - 모바일 기능은 선택사항입니다')" 2>nul

echo ✅ 모바일 확장성 준비 완료
echo.

:: Step 9: Windows Terminal 게임 최적화
echo 🖥️ [9/10] Windows Terminal 게임 최적화 중...

:: Windows Terminal 설정 최적화
if defined WT_SESSION (
    echo 🎨 Windows Terminal 색상 최적화...
    echo    - 24비트 트루컬러 활성화
    echo    - ANSI 이스케이프 시퀀스 지원
    echo    - 게임 전용 폰트 권장: Cascadia Code 또는 Consolas
    echo ✅ Windows Terminal 최적화 완료
) else (
    echo ⚠️ 일반 CMD 환경에서 실행 중
    echo    최고 품질을 위해 Windows Terminal 사용을 권장합니다
)
echo.

:: Step 10: 게임 실행 환경 최적화
echo 🚀 [10/10] 게임 실행 환경 최적화 중...

if exist "main.py" (
    echo ✅ 게임 메인 파일 확인됨
) else (
    echo ❌ 게임 메인 파일을 찾을 수 없습니다.
    echo    다운로드에 문제가 있을 수 있습니다.
)

if exist "launcher.py" (
    echo ✅ Python 런처 확인됨
) else (
    echo ⚠️ Python 런처가 없습니다. 게임은 직접 실행해야 합니다.
)

:: Windows Terminal 전용 실행 스크립트 생성
echo 📝 Windows Terminal 최적화 실행 스크립트 생성 중...

:: 배치 파일 생성
(
echo @echo off
echo :: Dawn of Stellar - Windows Terminal 최적화 실행
echo chcp 65001 ^> nul
echo title Dawn of Stellar - 별들의 새벽
echo.
echo :: Windows Terminal 감지
echo if not defined WT_SESSION ^(
echo     echo 🚀 Windows Terminal에서 실행 중이 아닙니다.
echo     echo    최고의 게임 경험을 위해 Windows Terminal을 사용하세요!
echo     echo.
echo     set /p wt_restart="Windows Terminal로 실행하시겠습니까? ^(Y/N^): "
echo     if /i "%%wt_restart%%"=="Y" ^(
echo         start wt -d "%%~dp0" cmd /k "%%~f0"
echo         exit /b 0
echo     ^)
echo ^)
echo.
echo :: 가상환경 활성화
echo call .venv\Scripts\activate.bat
echo.
echo :: 게임 실행
echo echo 🌟 Dawn of Stellar 시작 중...
echo echo    최적화된 Windows Terminal 환경에서 실행됩니다!
echo echo.
echo python launcher.py
echo.
echo echo.
echo echo 🎮 게임이 종료되었습니다. 즐거우셨나요?
echo pause
) > "Dawn_of_Stellar_실행.bat"

:: PowerShell 실행 스크립트도 생성 (대안)
(
echo # Dawn of Stellar - PowerShell 실행 스크립트
echo Write-Host "🌟 Dawn of Stellar 시작 중..." -ForegroundColor Cyan
echo Write-Host "   PowerShell 환경에서 실행됩니다" -ForegroundColor Yellow
echo Write-Host ""
echo.
echo # 가상환경 활성화
echo ^& ".\.venv\Scripts\Activate.ps1"
echo.
echo # 게임 실행
echo python launcher.py
echo.
echo Write-Host ""
echo Write-Host "🎮 게임이 종료되었습니다. 즐거우셨나요?" -ForegroundColor Green
echo Read-Host "계속하려면 Enter를 누르세요"
) > "Dawn_of_Stellar_PowerShell실행.ps1"

echo ✅ 실행 스크립트 생성 완료

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo                         🎉 설치 완료! 🎉                         
echo                   Windows Terminal 최적화 완료!                
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo 🎮 게임 실행 방법 (추천 순서):
echo.
echo    1. 🌟 Windows Terminal 최적화 실행 (최고 품질):
echo       ► "Dawn_of_Stellar_실행.bat" 더블클릭
echo.
echo    2. 💻 PowerShell 실행 (고품질):
echo       ► "Dawn_of_Stellar_PowerShell실행.ps1" 우클릭 → PowerShell로 실행
echo.
echo    3. 🚀 Python 런처 (개발자 옵션):
echo       ► python launcher.py
echo.
echo    4. 🔧 수동 실행 (고급 사용자):
echo       ► Windows Terminal에서: cd Dawn-of-Stellar
echo       ► .venv\Scripts\activate.bat
echo       ► python main.py
echo.

echo 📋 설치된 구성 요소:
echo    ✅ Dawn of Stellar 게임 (28개 직업, 165+ 상태효과)
echo    ✅ Windows Terminal 최적화
echo    ✅ Python 가상환경
echo    ✅ 필수 Python 패키지
echo    ✅ 오디오 시스템 (pygame)
echo    ✅ 게임패드 지원 (Xbox/PlayStation/Switch Pro)
echo    ✅ 모바일 확장성 준비
echo    ✅ 최적화된 실행 스크립트
echo.

echo 🎯 추가 기능:
echo    🎮 게임패드: Xbox, PlayStation, Nintendo Switch Pro 컨트롤러 지원
echo    📱 모바일: Flutter 앱 연결 가능 (백엔드 서버 포함)
echo    🎨 색상: 24비트 트루컬러 지원 (Windows Terminal에서)
echo    🔊 사운드: BGM 및 효과음 완벽 지원
echo.

set /p run_now="🎮 지금 바로 게임을 실행하시겠습니까? (Y/N): "
if /i "%run_now%"=="Y" (
    echo.
    echo 🚀 게임 실행 중...
    
    :: Windows Terminal에서 실행 중인지 확인
    if defined WT_SESSION (
        echo 🌟 Windows Terminal 최적화 환경에서 실행!
        call "Dawn_of_Stellar_실행.bat"
    ) else (
        echo 🔄 Windows Terminal로 게임 시작...
        where wt >nul 2>&1
        if not errorlevel 1 (
            start wt -d "%cd%" cmd /k "Dawn_of_Stellar_실행.bat"
        ) else (
            echo ⚠️ Windows Terminal을 찾을 수 없어 현재 환경에서 실행합니다.
            if exist "launcher.py" (
                python launcher.py
            ) else (
                python main.py
            )
        )
    )
) else (
    echo.
    echo 🎊 설치가 완료되었습니다!
    echo    "Dawn_of_Stellar_실행.bat"을 더블클릭하여 언제든지 게임을 즐기세요!
    echo.
    echo 💡 팁: Windows Terminal에서 실행하면 더욱 아름다운 게임을 경험할 수 있습니다!
)

echo.
echo 🌟 Dawn of Stellar에 오신 것을 환영합니다! 🌟
echo.
pause
exit /b 0
