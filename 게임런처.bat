@echo off
chcp 65001 > nul
color 0A
title Dawn of Stellar - CMD Terminal Launcher v4.1

REM Force CMD terminal (not PowerShell)
if "%1" neq "cmd" (
    cmd /c "%~f0" cmd %*
    exit /b
)

:MAIN_MENU
cls
echo.
echo     ===============================================================
echo                Dawn of Stellar - CMD Terminal Launcher v4.1          
echo                        Korean AI-Powered Roguelike RPG                    
echo                  AI Chat with 27 Unique Job Personalities!               
echo                           Full Color Support in CMD!
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
echo       [3] Single Player Game (main.py)
echo           - Start the main roguelike adventure
echo.
echo     Multiplayer Options:
echo     ========================================
echo       [4] Host Multiplayer Game
echo           - Create server and host for friends
echo.
echo       [5] Join Multiplayer Game
echo           - Connect to existing game server
echo.
echo       [6] AI Co-op Adventure
echo           - Play with intelligent AI robats as teammates
echo.
echo     Korean AI Chat (EXAONE):
echo     ========================================
echo       [7] Robat Chat (EXAONE-Korean)
echo           - Chat with 27 job-specific AI personalities
echo.
echo       [8] Personality System View
echo           - Browse 27 job-specific robat personalities
echo.
echo     Ollama Management:
echo     ========================================
echo       [9] Korean AI Model Setup/Check
echo       [1] Fast Launcher (performance_launcher.py)
echo           - Quick response, optimized performance
echo.
echo           - Install/verify exaone3.5:7.8b (LG AI official)
echo.
echo       [A] Ollama Server Management
echo           - Start/stop server, check status
echo.
echo       [B] Korean Model Guide
echo           - Compare and recommendations for Korean models
echo.
echo     Other Options:
echo     ========================================
echo       [0] Exit
echo.
set /p choice="    Select option (0-9, A, B): "

if "%choice%"=="1" goto FAST_LAUNCHER
if "%choice%"=="2" goto FULL_LAUNCHER  
if "%choice%"=="3" goto SINGLE_PLAYER
if "%choice%"=="4" goto HOST_MULTIPLAYER
if "%choice%"=="5" goto JOIN_MULTIPLAYER
if "%choice%"=="6" goto AI_COOP
if "%choice%"=="7" goto AI_CHAT
if "%choice%"=="8" goto PERSONALITY_SYSTEM
if "%choice%"=="9" goto EXAONE_SETUP
if /i "%choice%"=="A" goto OLLAMA_MANAGEMENT
if /i "%choice%"=="B" goto KOREAN_MODEL_GUIDE
if "%choice%"=="0" goto EXIT

echo     [ERROR] Invalid selection.
timeout /t 2 > nul
goto MAIN_MENU

:SINGLE_PLAYER
cls
echo     Starting Single Player Adventure!
echo     Full color support in CMD terminal!
echo.
echo     Loading Dawn of Stellar main game...
D:\로그라이크_2\.venv\Scripts\python.exe main.py
pause
goto MAIN_MENU

:HOST_MULTIPLAYER
cls
echo     🌐 Advanced Multiplayer Host Server!
echo     ===================================
echo.
echo     Choose hosting mode:
echo.
echo       [1] Standard Network Game
echo           - Traditional multiplayer hosting
echo.
echo       [2] AI-Enhanced Multiplayer
echo           - Mix human and AI players seamlessly
echo.
echo       [3] Robat Playground Server
echo           - Specialized server for AI robat testing
echo.
echo       [0] Back to Main Menu
echo.
set /p host_mode="    Select hosting mode (0-3): "

if "%host_mode%"=="1" goto STANDARD_HOST
if "%host_mode%"=="2" goto AI_ENHANCED_HOST
if "%host_mode%"=="3" goto ROBAT_SERVER
if "%host_mode%"=="0" goto MAIN_MENU

echo     [ERROR] Invalid selection.
timeout /t 2 > nul
goto HOST_MULTIPLAYER

:STANDARD_HOST
cls
echo     🌐 Starting Standard Multiplayer Server...
echo     =========================================
echo.
echo     Setting up server for friends to join...
echo     [INFO] Server will be hosted on your local network
echo     [INFO] Friends can connect using your IP address
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.multiplayer_server import start_server
start_server()
"
pause
goto HOST_MULTIPLAYER

:AI_ENHANCED_HOST
cls
echo     🤖 AI-Enhanced Multiplayer Server!
echo     ==================================
echo.
echo     🌟 Enhanced Features:
echo       • Mix human and AI players
echo       • AI fills empty slots automatically
echo       • Dynamic difficulty adjustment
echo       • Intelligent matchmaking
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.integrated_multiplayer import start_ai_enhanced_server
start_ai_enhanced_server()
"
pause
goto HOST_MULTIPLAYER

:ROBAT_SERVER
cls
echo     🎮 Robat Playground Server!
echo     ===========================
echo.
echo     🤖 Robat Server Features:
echo       • Test AI robat interactions
echo       • Observe AI vs AI gameplay
echo       • Train and evaluate AI models
echo       • Research and development mode
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.robat_multiplayer import start_robat_playground_server
start_robat_playground_server()
"
pause
goto HOST_MULTIPLAYER

:JOIN_MULTIPLAYER
cls
echo     🔗 Join Advanced Multiplayer Game!
echo     ==================================
echo.
echo     Choose connection mode:
echo.
echo       [1] Connect to Standard Server
echo           - Join traditional multiplayer game
echo.
echo       [2] Smart Auto-Connect
echo           - Automatically find best available server
echo.
echo       [3] AI Spectator Mode
echo           - Watch AI vs AI battles with analysis
echo.
echo       [0] Back to Main Menu
echo.
set /p join_mode="    Select connection mode (0-3): "

if "%join_mode%"=="1" goto MANUAL_CONNECT
if "%join_mode%"=="2" goto AUTO_CONNECT  
if "%join_mode%"=="3" goto AI_SPECTATOR
if "%join_mode%"=="0" goto MAIN_MENU

echo     [ERROR] Invalid selection.
timeout /t 2 > nul
goto JOIN_MULTIPLAYER

:MANUAL_CONNECT
cls
echo     🔗 Manual Server Connection
echo     ==========================
echo.
set /p server_ip="    Enter server IP address (or press Enter for localhost): "
if "%server_ip%"=="" set server_ip=localhost
echo.
echo     Connecting to server: %server_ip%
echo     Starting multiplayer client...
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.multiplayer_client import connect_to_server
connect_to_server('%server_ip%')
"
pause
goto JOIN_MULTIPLAYER

:AUTO_CONNECT
cls
echo     🤖 Smart Auto-Connect!
echo     ======================
echo.
echo     🔍 Scanning for available servers...
echo     [INFO] Checking local network and internet
echo     [INFO] Analyzing server quality and latency
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.multiplayer_network import smart_auto_connect
smart_auto_connect()
"
pause
goto JOIN_MULTIPLAYER

:AI_SPECTATOR
cls
echo     👁️ AI Spectator Mode!
echo     =====================
echo.
echo     🧠 Spectator Features:
echo       • Watch AI vs AI battles
echo       • Real-time strategy analysis
echo       • Learning algorithm visualization
echo       • Performance metrics display
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.ultimate_multiplayer_ai import start_ai_spectator_mode
start_ai_spectator_mode()
"
pause
goto JOIN_MULTIPLAYER

:AI_COOP
cls
echo     🤖 Ultimate AI Co-op Adventure!
echo     ===============================
echo.
echo     Choose your AI partnership mode:
echo.
echo       [1] Human + Robat Hybrid Mode
echo           - Best of both worlds: Human creativity + AI efficiency
echo.
echo       [2] Ultimate Multiplayer AI
echo           - Advanced ML-powered AI teammates  
echo.
echo       [3] Robat Multiplayer Session
echo           - Play with specialized job-based AI robats
echo.
echo       [4] AI Learning Partnership
echo           - AI learns from your playstyle and adapts
echo.
echo       [0] Back to Main Menu
echo.
set /p ai_mode="    Select AI Co-op mode (0-4): "

if "%ai_mode%"=="1" goto HYBRID_MODE
if "%ai_mode%"=="2" goto ULTIMATE_AI
if "%ai_mode%"=="3" goto ROBAT_MULTIPLAYER
if "%ai_mode%"=="4" goto AI_LEARNING
if "%ai_mode%"=="0" goto MAIN_MENU

echo     [ERROR] Invalid selection.
timeout /t 2 > nul
goto AI_COOP

:HYBRID_MODE
cls
echo     👥 Human + Robat Hybrid Mode!
echo     ============================
echo.
echo     🌟 Features:
echo       • Human creativity + AI efficiency
echo       • Natural communication with robats
echo       • Adaptive AI that learns your style
echo       • 5 different cooperation modes
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.human_ai_hybrid_multiplayer import start_hybrid_session
start_hybrid_session()
"
pause
goto AI_COOP

:ULTIMATE_AI
cls
echo     🚀 Ultimate Multiplayer AI!
echo     ===========================
echo.
echo     🧠 Advanced Features:
echo       • Machine learning based gameplay
echo       • Real-time strategy adaptation
echo       • Human-level decision making
echo       • Advanced teamwork algorithms
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.ultimate_multiplayer_ai import start_ultimate_ai_session
start_ultimate_ai_session()
"
pause
goto AI_COOP

:ROBAT_MULTIPLAYER
cls
echo     🎮 Robat Multiplayer Session!
echo     =============================
echo.
echo     🤖 Robat Features:
echo       • 27 job-specialized AI personalities
echo       • Real-time AI communication
echo       • Leadership system (host/leader roles)
echo       • Cooperative and competitive modes
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.robat_multiplayer import start_robat_session
start_robat_session()
"
pause
goto AI_COOP

:AI_LEARNING
cls
echo     📚 AI Learning Partnership!
echo     ===========================
echo.
echo     🎯 Learning Features:
echo       • AI observes and learns from you
echo       • Adapts to your playstyle preferences
echo       • Provides personalized suggestions
echo       • Grows smarter over time
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import sys
sys.path.append('.')
from game.ultimate_ai_learning_system import start_learning_session
start_learning_session()
"
pause
goto AI_COOP

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
echo     EXAONE-Korean support! 27 unique job personalities!
echo.
echo     Checking Ollama server status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel%==0 (
    echo     [OK] Ollama server connected - EXAONE model available!
    echo.
    echo     Korean EXAONE Chat:
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

:EXAONE_SETUP
cls
echo     Korean AI Model Installation and Verification
echo     =============================================
echo     Installing Korean AI model for best chat experience!
echo.
echo     Checking installed models...
ollama list | findstr "exaone"
if %errorlevel%==0 (
    echo     [OK] EXAONE Korean model is already installed!
    echo.
    echo     Do you want to test the model? (y/n)
    set /p test_choice="    "
    if /i "%test_choice%"=="y" (
        echo     Testing EXAONE model...
        ollama run exaone3.5:7.8b "안녕하세요! 저는 Dawn of Stellar의 로바트입니다!"
    )
) else (
    echo     [ERROR] EXAONE Korean model is not installed.
    echo.
    echo     Model Information:
    echo       Name: EXAONE 3.5 (7.8B parameters)  
    echo       Full Name: exaone3.5:7.8b
    echo       Size: About 4.7GB
    echo       Features: Korean-English bilingual, LG AI Research
    echo       Developer: LG AI Research (Official)
    echo.
    echo     Install now? This may take a while. (y/n)
    set /p install_choice="    "
    if /i "%install_choice%"=="y" (
        echo     Starting EXAONE Korean model download...
        echo     This may take 10-20 minutes depending on network speed.
        ollama pull exaone3.5:7.8b
        echo.
        echo     [OK] Installation complete! Starting test...
        ollama run exaone3.5:7.8b "설치가 완료되었습니다!"
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
echo     EXAONE robats are waiting for you!
echo     Korean AI adventure continues in full color!
echo     
echo     CMD terminal launcher v4.1 - optimized for color support
echo.
timeout /t 3 > nul
exit
