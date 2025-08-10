@echo off
:: Dawn of Stellar - 터미널 기반 런처 (현재 터미널에서 실행)
:: UTF-8 encoding for Korean support
chcp 65001 > nul

title Dawn of Stellar - Terminal Launcher

echo.
echo ================================================================
echo.
echo                Dawn of Stellar - Python Launcher
echo.
echo                     터미널 기반 실행 모드
echo.
echo ================================================================
echo.

:: Check current directory
if not exist "python_launcher.py" (
    echo [ERROR] python_launcher.py file not found.
    echo    Current location: %cd%
    echo    Please run from the correct game folder.
    pause
    exit /b 1
)

:: Python environment check and execution
echo [INFO] Checking Python environment...

:: 🎨 Windows Terminal 색상 강제 활성화
set FORCE_COLOR=1
set WT_SESSION=1
echo [COLOR] Enabling Windows Terminal color support...

:: Check virtual environment and execute
if exist ".venv\Scripts\python.exe" (
    echo [SUCCESS] Virtual environment found! (.venv\Scripts\python.exe^)
    echo [START] Starting Python launcher...
    echo.
    echo ====================================================
    echo              Launcher Running
    echo.
    echo   - Navigation: W/S keys or arrow keys
    echo   - Select: Enter key
    echo   - Direct select: Number/Letter keys  
    echo   - Exit: ESC key or Q
    echo.
    echo ====================================================
    echo.
    
    ".venv\Scripts\python.exe" python_launcher.py
    
) else if exist "venv\Scripts\python.exe" (
    echo [SUCCESS] Virtual environment found! (venv\Scripts\python.exe^)
    echo [START] Starting Python launcher...
    echo.
    "venv\Scripts\python.exe" python_launcher.py
    
) else (
    echo [WARNING] Virtual environment not found. Using system Python.
    
    :: Check system Python
    python --version > nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH.
        echo.
        echo [SOLUTION]
        echo    1. Install Python 3.10 or higher
        echo    2. Create virtual environment: python -m venv .venv
        echo    3. Activate virtual environment: .venv\Scripts\activate.bat
        echo    4. Install dependencies: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    
    echo [START] Starting Python launcher...
    echo.
    python python_launcher.py
)

:: Post-execution handling
set exit_code=%errorlevel%

echo.
echo ================================================================

if %exit_code% equ 0 (
    echo [SUCCESS] Python launcher exited normally.
) else (
    echo [ERROR] Error occurred during Python launcher execution. (Exit code: %exit_code%^)
    echo.
    echo [TROUBLESHOOTING]
    echo    - Check dependencies: pip install -r requirements.txt
    echo    - Check file permissions
    echo    - Reset virtual environment
)

echo.
echo [COMPLETE] Hope this helped with game development!
echo.

:: Prevent auto-close (for debugging)
echo.
echo [COMPLETE] Dawn of Stellar launcher finished.
echo.

if "%1"=="/auto" (
    echo [AUTO] Auto mode - closing automatically
    timeout /t 1 > nul
) else (
    echo [MANUAL] Press any key to close...
    pause > nul
)

exit /b %exit_code%
