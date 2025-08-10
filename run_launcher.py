#!/usr/bin/env python3
"""
Dawn of Stellar - 터미널 직접 실행 스크립트
현재 터미널에서 바로 게임 런처 실행
"""

import os
import sys

def main():
    """현재 터미널에서 런처 실행"""
    print("🎮 Dawn of Stellar - 터미널 런처")
    print("=" * 50)
    
    # 현재 디렉터리 확인
    if not os.path.exists("python_launcher.py"):
        print("❌ python_launcher.py 파일을 찾을 수 없습니다.")
        print(f"현재 위치: {os.getcwd()}")
        print("올바른 게임 폴더에서 실행해주세요.")
        return
    
    # Python 런처 실행
    try:
        import python_launcher
        print("✅ 런처를 시작합니다...")
        python_launcher.main()
    except ImportError as e:
        print(f"❌ 런처 모듈 로드 실패: {e}")
    except Exception as e:
        print(f"❌ 런처 실행 오류: {e}")

if __name__ == "__main__":
    main()
