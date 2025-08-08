@echo off
:: Dawn of Stellar - Python Launcher Batch File
:: UTF-8 encoding for Korean support
chcp 65001 > nul

title Dawn of Stellar - Python Launcher

:: Color settings
color 0B

echo.
echo ================================================================
echo.
echo                Dawn of Stellar - Python Launcher
echo.
echo                     Development Tools Integration
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
if "%1"=="/auto" (
    echo [AUTO] Auto mode - closing in 3 seconds
    timeout /t 3 > nul
) else (
    echo [WAIT] Press any key to close window...
    pause > nul
)

exit /b %exit_code%
