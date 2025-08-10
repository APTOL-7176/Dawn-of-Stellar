@echo off
chcp 65001 >nul
title Dawn of Stellar - 런처 선택

:menu
cls
echo.
echo     ╔══════════════════════════════════════════════════════════════╗
echo              🌟 Dawn of Stellar - 런처 선택 v4.0.1 🌟
echo                        별들의 새벽 - 로그라이크 RPG
echo     ╚══════════════════════════════════════════════════════════════╝
echo.
echo 📋 런처를 선택하세요:
echo ══════════════════════════════════════
echo   [1] 🚀 고속 런처 (권장)
echo       💭 빠른 반응속도, 최소 메모리 사용
echo.
echo   [2] 🎮 통합 런처 (고급)  
echo       💭 모든 기능 포함, 상세한 메뉴
echo.
echo   [3] 🤖 AI 로바트와 대화
echo       💭 실제 언어모델과 대화 가능
echo.
echo   [4] 🔑 API 키 설정
echo       💭 OpenAI, Claude 등 API 키 설정
echo.
echo   [0] ❌ 종료
echo.
echo ──────────────────────────────────────────────────────────────
set /p choice="🎯 선택 (1-4, 0): "

if "%choice%"=="1" goto fast_launcher
if "%choice%"=="2" goto full_launcher  
if "%choice%"=="3" goto ai_chat
if "%choice%"=="4" goto api_setup
if "%choice%"=="0" goto exit

echo ❌ 잘못된 선택입니다.
timeout /t 2 >nul
goto menu

:fast_launcher
echo.
echo 🚀 고속 런처를 시작합니다...
D:\로그라이크_2\.venv\Scripts\python.exe performance_launcher.py
goto menu

:full_launcher
echo.
echo 🎮 통합 런처를 시작합니다...
D:\로그라이크_2\.venv\Scripts\python.exe python_launcher.py
goto menu

:ai_chat
echo.
echo 🤖 AI 로바트와 대화를 시작합니다...
echo 💡 API 키가 설정되어 있지 않으면 대체 응답을 사용합니다.
D:\로그라이크_2\.venv\Scripts\python.exe ai_language_model_integration.py chat
pause
goto menu

:api_setup
echo.
echo 🔑 API 키 설정을 시작합니다...
echo 💡 OpenAI, Claude, Gemini 등의 API 키를 설정할 수 있습니다.
D:\로그라이크_2\.venv\Scripts\python.exe ai_language_model_integration.py setup
pause
goto menu

:exit
echo.
echo 👋 Dawn of Stellar 런처를 종료합니다.
echo 💝 게임을 즐겨주셔서 감사합니다!
timeout /t 2 >nul
exit
