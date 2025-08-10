@echo off
chcp 65001 > nul
color 0A
title Dawn of Stellar - Ollama EEVE Launcher v3.0

:MAIN_MENU
cls
echo.
echo     ===============================================================
echo                Dawn of Stellar - Ollama EEVE Launcher v3.0           
echo                        Korean AI-Powered Roguelike RPG                    
echo                  AI Chat with 27 Unique Job Personalities!               
echo     ===============================================================

REM Ollama status check
echo     Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel%==0 (
    echo     [OK] Ollama server is running (localhost:11434)
) else (
    echo     [ERROR] Ollama server not running (need 'ollama serve')
)
echo.

echo     Game Launcher Options:
echo     ========================================
echo       [1] Fast Launcher (performance_launcher.py)
echo           - Quick response, optimized performance
echo.
echo       [2] Full Launcher (python_launcher.py)  
echo           - All features, detailed options
echo.
echo     Korean AI Chat (EEVE):
echo     ========================================
echo       [3] Robat Chat (EEVE-Korean)
echo           - Chat with 27 job-specific AI personalities
echo.
echo       [4] Personality System View
echo           - Browse 27 job-specific robat personalities
echo.
echo     Ollama Management:
echo     ========================================
echo       [5] EEVE Model Setup/Check
echo           - Install/verify yanolja/EEVE-Korean-Instruct-10.8B-v1.0
echo.
echo       [6] Ollama Server Management
echo           - Start/stop server, check status
echo.
echo       [7] Korean Model Guide
echo           - Compare and recommendations for Korean models
echo.
echo     Other Options:
echo     ========================================
echo       [0] Exit
echo.
set /p choice="    Select option (0-7): "

if "%choice%"=="1" goto FAST_LAUNCHER
if "%choice%"=="2" goto FULL_LAUNCHER  
if "%choice%"=="3" goto AI_CHAT
if "%choice%"=="4" goto PERSONALITY_SYSTEM
if "%choice%"=="5" goto EEVE_SETUP
if "%choice%"=="6" goto OLLAMA_MANAGEMENT
if "%choice%"=="7" goto KOREAN_MODEL_GUIDE
if "%choice%"=="0" goto EXIT

echo     [ERROR] Invalid selection.
timeout /t 2 > nul
goto MAIN_MENU

:FAST_LAUNCHER
cls
echo     Starting Fast Launcher...
echo     Quick response and optimized performance!
echo.
D:\로그라이크_2\.venv\Scripts\python.exe performance_launcher.py
pause
goto MAIN_MENU

:FULL_LAUNCHER
cls
echo     Starting Full Launcher...
echo     All features and detailed options!
echo.
D:\로그라이크_2\.venv\Scripts\python.exe python_launcher.py
pause
goto MAIN_MENU

:AI_CHAT
cls
echo     Starting Korean AI Chat with Robat!
echo     EEVE-Korean support! 27 unique job personalities!
echo.
echo     Checking Ollama server status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel%==0 (
    echo     [OK] Ollama server connected - EEVE model available!
    echo.
    echo     Korean EEVE Chat:
    D:\로그라이크_2\.venv\Scripts\python.exe simple_robat_chat.py
) else (
    echo     [ERROR] Ollama server not running! Running in fallback mode...
    echo     [TIP] Start server with 'ollama serve' for better chat experience!
    echo.
    echo     Simple Chat (Fallback Mode):
    D:\로그라이크_2\.venv\Scripts\python.exe simple_robat_chat.py
)
pause
goto MAIN_MENU

:PERSONALITY_SYSTEM
cls
echo     27 Job-Specific Robat Personality System!
echo     =========================================
echo.
D:\로그라이크_2\.venv\Scripts\python.exe game\robat_personality_system.py
pause
goto MAIN_MENU

:EEVE_SETUP
cls
echo     EEVE-Korean Model Installation and Verification
echo     ===============================================
echo     Installing the best Korean AI model!
echo.
echo     Checking installed models...
ollama list | findstr "yanolja"
if %errorlevel%==0 (
    echo     [OK] EEVE-Korean model is already installed!
    echo.
    echo     Do you want to test the model? (y/n)
    set /p test_choice="    "
    if /i "%test_choice%"=="y" (
        echo     Testing EEVE model...
        ollama run yanolja/EEVE-Korean-Instruct-10.8B-v1.0 "Hello! I am Dawn of Stellar robat!"
    )
) else (
    echo     [ERROR] EEVE-Korean model is not installed.
    echo.
    echo     Model Information:
    echo       Name: EEVE-Korean Instruct 10.8B v1.0  
    echo       Full Name: yanolja/EEVE-Korean-Instruct-10.8B-v1.0
    echo       Size: About 6.2GB
    echo       Features: Korean-specialized, natural conversation
    echo       Developer: Yanolja AI Team
    echo.
    echo     Install now? This may take a while. (y/n)
    set /p install_choice="    "
    if /i "%install_choice%"=="y" (
        echo     Starting EEVE-Korean model download...
        echo     This may take 10-30 minutes depending on network speed.
        ollama pull yanolja/EEVE-Korean-Instruct-10.8B-v1.0
        echo.
        echo     [OK] Installation complete! Starting test...
        ollama run yanolja/EEVE-Korean-Instruct-10.8B-v1.0 "Installation completed successfully!"
    ) else (
        echo     [CANCEL] Installation cancelled.
    )
)
pause
goto MAIN_MENU

:OLLAMA_MANAGEMENT
cls
echo     Ollama Server Management
echo     ========================
echo.
echo     Current Ollama Status:
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel%==0 (
    echo     [OK] Ollama server running (port 11434)
    echo.
    echo     Installed Models List:
    ollama list
    echo.
    echo     Management Options:
    echo       [1] Restart Server
    echo       [2] Stop Server  
    echo       [3] Refresh Model List
    echo       [4] Clean Unused Models
    echo       [0] Go Back
    echo.
    set /p mgmt_choice="    Selection: "
    if "%mgmt_choice%"=="1" (
        echo     Restarting Ollama server...
        taskkill /f /im ollama.exe >nul 2>&1
        timeout /t 2 >nul
        start /b ollama serve
        echo     [OK] Server restarted!
    ) else if "%mgmt_choice%"=="2" (
        echo     Stopping Ollama server...
        taskkill /f /im ollama.exe >nul 2>&1
        echo     [OK] Server stopped!
    ) else if "%mgmt_choice%"=="3" (
        echo     Refreshing model list:
        ollama list
    ) else if "%mgmt_choice%"=="4" (
        echo     Manual cleanup required for unused models:
        echo       Use: ollama rm ^<model_name^>
        ollama list
    )
) else (
    echo     [ERROR] Ollama server is not running.
    echo.
    echo     Start the server? (y/n)
    set /p start_choice="    "
    if /i "%start_choice%"=="y" (
        echo     Starting Ollama server...
        start /b ollama serve
        echo     [OK] Server started! Please wait a moment...
        timeout /t 5 >nul
    )
)
pause
goto MAIN_MENU

:KOREAN_MODEL_GUIDE
cls
echo     Korean Model Guide
echo     ==================
echo.
D:\로그라이크_2\.venv\Scripts\python.exe korean_ollama_guide.py
pause
goto MAIN_MENU

:EXIT
cls
echo.
echo     Thank you for using Dawn of Stellar!
echo     EEVE robats are waiting for you!
echo     Korean AI adventure continues!
echo.
timeout /t 3 > nul
exit
