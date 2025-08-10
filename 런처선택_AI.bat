@echo off
chcp 65001 > nul
color 0A
title Dawn of Stellar - EXAONE Launcher v4.0 (Korean)

:MAIN_MENU
cls
echo.
echo     ===============================================================
echo                Dawn of Stellar - EXAONE Launcher v4.0 (Korean)           
echo                        Korean AI-Powered Roguelike RPG                    
echo                  AI Chat with 27 Unique Job Personalities!               
echo     ===============================================================

REM Ollama status check
echo     Ollama 상태 확인 중...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel%==0 (
    echo     [OK] Ollama 서버 실행 중 (localhost:11434)
) else (
    echo     [ERROR] Ollama 서버 미실행 (ollama serve 필요)
)
echo.

echo     런처 선택:
echo     ========================================
echo       [1] 고속 런처 (performance_launcher.py)
echo           - 빠른 응답, 최적화된 성능
echo.
echo       [2] 완전 런처 (python_launcher.py)  
echo           - 모든 기능, 상세한 옵션
echo.
echo     한글 AI 채팅 (EXAONE):
echo     ========================================
echo       [3] 로바트 채팅 (EXAONE-Korean!)
echo           - 27개 직업별 고유 성격 한국어 AI 대화
echo.
echo       [4] 성격 시스템 보기
echo           - 27개 직업별 로바트 성격 정보
echo.
echo     Ollama 관리:
echo     ========================================
echo       [5] EXAONE 모델 설치/확인
echo           - LG AI Research exaone3.5:7.8b
echo.
echo       [6] Ollama 서버 관리
echo           - 서버 시작/중지, 상태 확인
echo.
echo       [7] 한글 모델 가이드
echo           - 한국어 특화 모델 비교 및 추천
echo.
echo     기타:
echo     ========================================
echo       [0] 종료
echo.
set /p choice="    선택 (0-7): "

if "%choice%"=="1" goto FAST_LAUNCHER
if "%choice%"=="2" goto FULL_LAUNCHER  
if "%choice%"=="3" goto AI_CHAT
if "%choice%"=="4" goto PERSONALITY_SYSTEM
if "%choice%"=="5" goto EXAONE_SETUP
if "%choice%"=="6" goto OLLAMA_MANAGEMENT
if "%choice%"=="7" goto KOREAN_MODEL_GUIDE
if "%choice%"=="0" goto EXIT

echo     [ERROR] 잘못된 선택입니다.
timeout /t 2 > nul
goto MAIN_MENU

:FAST_LAUNCHER
cls
echo     고속 런처 실행 중...
echo     빠른 응답과 최적화된 성능!
echo.
D:\로그라이크_2\.venv\Scripts\python.exe performance_launcher.py
pause
goto MAIN_MENU

:FULL_LAUNCHER
cls
echo     완전 런처 실행 중...
echo     모든 기능과 상세한 옵션!
echo.
D:\로그라이크_2\.venv\Scripts\python.exe python_launcher.py
pause
goto MAIN_MENU

:AI_CHAT
cls
echo     로바트와 한국어 채팅 시작!
echo     EXAONE-Korean 지원! 27개 직업별 고유 성격!
echo.
echo     Ollama 서버 상태 확인 중...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel%==0 (
    echo     [OK] Ollama 서버 연결됨 - EXAONE 모델 사용 가능!
    echo.
    echo     한국어 EEVE 채팅:
    D:\로그라이크_2\.venv\Scripts\python.exe simple_robat_chat.py
) else (
    echo     [ERROR] Ollama 서버 미실행! 폴백 모드로 실행...
    echo     [TIP] 더 나은 대화를 위해 'ollama serve' 명령으로 서버를 시작하세요!
    echo.
    echo     간단 채팅 (폴백 모드):
    D:\로그라이크_2\.venv\Scripts\python.exe simple_robat_chat.py
)
pause
goto MAIN_MENU

:PERSONALITY_SYSTEM
cls
echo     27개 직업별 로바트 성격 시스템!
echo     ==============================
echo.
D:\로그라이크_2\.venv\Scripts\python.exe game\robat_personality_system.py
pause
goto MAIN_MENU

:EEVE_SETUP
cls
echo     � EEVE-Korean 모델 설치 및 확인
echo     ═════════════════════════════════════════
echo     🇰🇷 최고의 한국어 AI 모델을 설치합니다!
echo.
echo     � 설치된 모델 확인 중...
ollama list | findstr "yanolja"
if %errorlevel%==0 (
    echo     ✅ EEVE-Korean 모델이 이미 설치되어 있습니다!
    echo.
    echo     🧪 모델 테스트를 원하시나요? ^(y/n^)
    set /p test_choice="    "
    if /i "%test_choice%"=="y" (
        echo     🤖 EEVE 모델 테스트 중...
        ollama run yanolja/EEVE-Korean-Instruct-10.8B-v1.0 "안녕하세요! 저는 Dawn of Stellar의 로바트입니다!"
    )
) else (
    echo     ❌ EEVE-Korean 모델이 설치되지 않았습니다.
    echo.
    echo     📦 모델 정보:
    echo       • 이름: EEVE-Korean Instruct 10.8B v1.0  
    echo       • 실제명: yanolja/EEVE-Korean-Instruct-10.8B-v1.0
    echo       • 크기: 약 6.2GB
    echo       • 특징: 한국어 전용, 자연스러운 대화
    echo       • 개발: 야놀자 (Yanolja) AI팀
    echo.
    echo     💾 지금 설치하시겠습니까? 시간이 오래 걸릴 수 있습니다. ^(y/n^)
    set /p install_choice="    "
    if /i "%install_choice%"=="y" (
        echo     📥 EEVE-Korean 모델 다운로드 시작...
        echo     ⏳ 네트워크 상태에 따라 10-30분 소요될 수 있습니다.
        ollama pull yanolja/EEVE-Korean-Instruct-10.8B-v1.0
        echo.
        echo     ✅ 설치 완료! 테스트를 진행합니다...
        ollama run yanolja/EEVE-Korean-Instruct-10.8B-v1.0 "안녕하세요! 설치가 완료되었습니다!"
    ) else (
        echo     ❌ 설치를 취소했습니다.
    )
)
pause
goto MAIN_MENU

:OLLAMA_MANAGEMENT
cls
echo     🔧 Ollama 서버 관리
echo     ═════════════════════════════════════════
echo.
echo     📊 현재 Ollama 상태:
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel%==0 (
    echo     ✅ Ollama 서버 실행 중 ^(포트 11434^)
    echo.
    echo     📋 설치된 모델 목록:
    ollama list
    echo.
    echo     🛠️ 관리 옵션:
    echo       [1] 🔄 서버 재시작
    echo       [2] ⏹️ 서버 중지  
    echo       [3] 📋 모델 목록 새로고침
    echo       [4] 🗑️ 사용하지 않는 모델 정리
    echo       [0] 🔙 돌아가기
    echo.
    set /p mgmt_choice="    선택: "
    if "%mgmt_choice%"=="1" (
        echo     🔄 Ollama 서버 재시작 중...
        taskkill /f /im ollama.exe >nul 2>&1
        timeout /t 2 >nul
        start /b ollama serve
        echo     ✅ 서버가 재시작되었습니다!
    ) else if "%mgmt_choice%"=="2" (
        echo     ⏹️ Ollama 서버 중지 중...
        taskkill /f /im ollama.exe >nul 2>&1
        echo     ✅ 서버가 중지되었습니다!
    ) else if "%mgmt_choice%"=="3" (
        echo     📋 모델 목록 새로고침:
        ollama list
    ) else if "%mgmt_choice%"=="4" (
        echo     🗑️ 사용하지 않는 모델 정리는 수동으로 진행하세요:
        echo       • ollama rm ^<모델명^>
        ollama list
    )
) else (
    echo     ❌ Ollama 서버가 실행되지 않았습니다.
    echo.
    echo     🚀 서버를 시작하시겠습니까? ^(y/n^)
    set /p start_choice="    "
    if /i "%start_choice%"=="y" (
        echo     🚀 Ollama 서버 시작 중...
        start /b ollama serve
        echo     ✅ 서버가 시작되었습니다! 잠시 기다려주세요...
        timeout /t 5 >nul
    )
)
pause
goto MAIN_MENU

:KOREAN_MODEL_GUIDE
cls
echo     🇰🇷 한글 모델 가이드
echo     ═════════════════════════════════════════
echo.
D:\로그라이크_2\.venv\Scripts\python.exe korean_ollama_guide.py
pause
goto MAIN_MENU

:EXIT
cls
echo.
echo     🌟 Dawn of Stellar을 이용해 주셔서 감사합니다!
echo     🇰🇷 EEVE 로바트들이 기다리고 있어요!
echo     🤖 한국어 AI와 함께하는 모험이 계속됩니다!
echo.
timeout /t 3 > nul
exit
