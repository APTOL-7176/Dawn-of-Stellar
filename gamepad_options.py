#!/usr/bin/env python3
"""
게임패드 비활성화 옵션들

터미널에서 게임패드 사용 시 다른 프로그램이 실행되는 문제를 해결하는 방법들:
"""

# 방법 1: 환경 변수로 게임패드 완전 비활성화
print("=" * 60)
print("🎮 게임패드 비활성화 방법들")
print("=" * 60)

print("\n📋 방법 1: 환경 변수 설정")
print("다음 명령어로 게임패드를 완전히 비활성화:")
print("PowerShell: $env:DISABLE_GAMEPAD='1'; .\.venv\Scripts\python.exe main.py")
print("CMD: set DISABLE_GAMEPAD=1 && .\.venv\Scripts\python.exe main.py")

print("\n📋 방법 2: 게임 내 설정")
print("게임 실행 후 메뉴에서 '게임패드 비활성화' 옵션 선택")

print("\n📋 방법 3: 임시 스크립트")
print("gamepad_off.bat 파일 생성:")
print("@echo off")
print("set DISABLE_GAMEPAD=1")
print(".\.venv\Scripts\python.exe main.py")
print("pause")

print("\n🔧 현재 개선 사항:")
print("- SDL 비디오 드라이버 비활성화")
print("- 불필요한 이벤트 필터링")
print("- 터미널 전용 모드 최적화")
print("- 예외 처리 강화")

if __name__ == "__main__":
    import os
    
    print(f"\n🔍 현재 환경 변수:")
    print(f"DISABLE_GAMEPAD: {os.getenv('DISABLE_GAMEPAD')}")
    print(f"MOBILE_MODE: {os.getenv('MOBILE_MODE')}")
    print(f"WEB_MODE: {os.getenv('WEB_MODE')}")
    
    choice = input("\n게임패드를 비활성화하고 게임을 실행하시겠습니까? (y/n): ").lower()
    if choice == 'y':
        print("🚫 게임패드 비활성화 모드로 게임 실행...")
        os.environ['DISABLE_GAMEPAD'] = '1'
        
        import subprocess
        import sys
        
        result = subprocess.run([
            sys.executable, "main.py"
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(f"게임 종료됨 (코드: {result.returncode})")
    else:
        print("게임 실행을 취소했습니다.")
