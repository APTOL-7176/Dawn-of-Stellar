@echo off
echo ===============================================
echo Dawn Of Stellar - 포터블 파이썬 설정
echo ===============================================
echo.

REM 포터블 파이썬 디렉토리 설정
set PYTHON_DIR=%~dp0python
set GAME_DIR=%~dp0

REM 포터블 파이썬 존재 확인
if not exist "%PYTHON_DIR%\python.exe" (
    echo [오류] 포터블 파이썬이 설치되지 않았습니다.
    echo python 폴더에 포터블 파이썬을 압축 해제해주세요.
    echo.
    echo 포터블 파이썬 다운로드: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

echo [1/3] 포터블 파이썬 환경 설정 중...
set PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%
set PYTHONPATH=%GAME_DIR%

echo [2/3] 필요한 라이브러리 설치 중...
"%PYTHON_DIR%\python.exe" -m pip install --upgrade pip
"%PYTHON_DIR%\python.exe" -m pip install -r requirements.txt

echo [3/3] 게임 실행 준비 완료!
echo.
echo ===============================================
echo 설정이 완료되었습니다!
echo '게임시작_포터블.bat'를 실행하여 게임을 시작하세요.
echo ===============================================
pause
