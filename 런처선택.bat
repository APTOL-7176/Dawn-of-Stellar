@echo off
chcp 65001 > nul
title 🌟 Dawn of Stellar - 런처 선택기 v4.0.0

echo.
echo ════════════════════════════════════════════════════════════════
echo               🌟 Dawn of Stellar - 런처 선택기 🌟
echo                      별들의 새벽 - 로그라이크 RPG
echo ════════════════════════════════════════════════════════════════
echo.
echo 📋 런처를 선택하세요:
echo.
echo    [1] ⚡ 고속 런처 (빠른 실행, 간단 메뉴)
echo        💡 즉시 반응, 최소 기능, 빠른 게임 시작
echo.
echo    [2] 🌟 통합 런처 (모든 기능, 상세 메뉴)  
echo        💡 모든 AI 기능, 상세 설정, 완전한 제어
echo.
echo    [3] 🎮 게임 직접 실행 (런처 없이 바로 게임)
echo.
echo    [4] 🤖 AI 로바트와 대화하기 (NEW!)
echo.
echo    [0] ❌ 종료
echo.
echo ────────────────────────────────────────────────────────────────

set /p choice="선택하세요 (1-4, 0): "

if "%choice%"=="1" goto fast_launcher
if "%choice%"=="2" goto full_launcher  
if "%choice%"=="3" goto direct_game
if "%choice%"=="4" goto ai_chat
if "%choice%"=="0" goto exit

echo ⚠️ 잘못된 선택입니다.
pause
goto start

:fast_launcher
echo.
echo ⚡ 고속 런처를 실행합니다...
D:/로그라이크_2/.venv/Scripts/python.exe performance_launcher.py
goto end

:full_launcher
echo.
echo 🌟 통합 런처를 실행합니다...
D:/로그라이크_2/.venv/Scripts/python.exe python_launcher.py
goto end

:direct_game
echo.
echo 🎮 게임을 직접 실행합니다...
D:/로그라이크_2/.venv/Scripts/python.exe main.py
goto end

:ai_chat
echo.
echo 🤖 AI 로바트와 대화를 시작합니다...
D:/로그라이크_2/.venv/Scripts/python.exe ai_robat_chat.py
goto end

:exit
echo.
echo 👋 Dawn of Stellar을 다음에 또 만나요!
timeout /t 2 /nobreak > nul
exit

:end
echo.
echo 📋 다른 런처를 사용하시겠습니까? (Y/N)
set /p restart="선택: "
if /i "%restart%"=="Y" goto start
if /i "%restart%"=="y" goto start

echo.
echo 👋 게임을 즐겨주셔서 감사합니다!
pause
