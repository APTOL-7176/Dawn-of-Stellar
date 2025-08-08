#!/usr/bin/env python3
"""
터미널 전용 게임 실행기
게임패드를 완전히 비활성화하고 키보드만 사용
"""

import os
import sys

def main():
    """터미널 모드로 게임 실행"""
    print("🖥️  터미널 전용 모드로 게임을 실행합니다...")
    print("📌 게임패드가 비활성화됩니다 (터미널 방해 방지)")
    print("🎮 키보드 입력만 사용됩니다")
    print("-" * 50)
    
    # 환경 변수 설정으로 게임패드 완전 비활성화
    os.environ['DISABLE_GAMEPAD'] = '1'
    os.environ['TERMINAL_MODE'] = '1'
    os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '0'
    
    # SDL이 게임패드를 감지하지 않도록 설정
    os.environ['SDL_GAMECONTROLLER_ALLOW_BACKGROUND_EVENTS'] = '0'
    os.environ['SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '0'
    
    # 추가 안전 조치: pygame 게임패드 관련 기능 비활성화
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    os.environ['SDL_VIDEODRIVER'] = 'dummy'  # 비디오 없는 더미 드라이버
    
    print("✅ 환경 변수 설정 완료:")
    print(f"   - DISABLE_GAMEPAD: {os.environ.get('DISABLE_GAMEPAD')}")
    print(f"   - TERMINAL_MODE: {os.environ.get('TERMINAL_MODE')}")
    print(f"   - SDL 게임패드 이벤트: 비활성화")
    print("-" * 50)
    
    # 게임 실행
    try:
        # main.py를 직접 임포트해서 실행
        sys.path.insert(0, os.path.dirname(__file__))
        import main
        main.main()
    except KeyboardInterrupt:
        print("\n🛑 게임이 중단되었습니다.")
    except Exception as e:
        print(f"❌ 게임 실행 중 오류: {e}")

if __name__ == "__main__":
    main()
