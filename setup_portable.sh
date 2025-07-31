#!/bin/bash

echo "==============================================="
echo "Dawn Of Stellar - 포터블 파이썬 설정"
echo "==============================================="
echo ""

# 스크립트 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/python"
GAME_DIR="$SCRIPT_DIR"

# 포터블 파이썬 존재 확인
if [ ! -f "$PYTHON_DIR/bin/python3" ]; then
    echo "[오류] 포터블 파이썬이 설치되지 않았습니다."
    echo "python 폴더에 포터블 파이썬을 압축 해제해주세요."
    echo ""
    echo "Linux 포터블 파이썬 설치:"
    echo "1. https://www.python.org/downloads/source/ 에서 Python 소스 다운로드"
    echo "2. 또는 pyenv를 사용하여 로컬 Python 설치"
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

echo "[1/3] 포터블 파이썬 환경 설정 중..."
export PATH="$PYTHON_DIR/bin:$PATH"
export PYTHONPATH="$GAME_DIR"

echo "[2/3] 필요한 라이브러리 설치 중..."
"$PYTHON_DIR/bin/python3" -m pip install --upgrade pip
"$PYTHON_DIR/bin/python3" -m pip install -r requirements.txt

echo "[3/3] 게임 실행 준비 완료!"
echo ""
echo "==============================================="
echo "설정이 완료되었습니다!"
echo "'start_game_portable.sh'를 실행하여 게임을 시작하세요."
echo "==============================================="
read -p "계속하려면 Enter를 누르세요..."
