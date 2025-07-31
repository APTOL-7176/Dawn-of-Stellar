#!/bin/bash

echo "==============================================="
echo "Dawn Of Stellar - 별빛의 여명 (포터블 버전)"
echo "==============================================="
echo ""

# 스크립트 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/python"
GAME_DIR="$SCRIPT_DIR"

# 포터블 파이썬 존재 확인
if [ ! -f "$PYTHON_DIR/bin/python3" ]; then
    echo "[오류] 포터블 파이썬이 설정되지 않았습니다."
    echo "먼저 'setup_portable.sh'를 실행해주세요."
    echo ""
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

# 환경 설정
export PATH="$PYTHON_DIR/bin:$PATH"
export PYTHONPATH="$GAME_DIR"

echo "게임을 시작합니다..."
echo ""

# 게임 실행
"$PYTHON_DIR/bin/python3" main.py

# 게임 종료 후 대기
echo ""
echo "게임이 종료되었습니다."
read -p "계속하려면 Enter를 누르세요..."
