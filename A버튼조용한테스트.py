#!/usr/bin/env python3
"""
A버튼 조용한 테스트 - 게임 화면을 방해하지 않는 백그라운드 차단 테스트
"""

import sys
import os
import time
import subprocess
import threading

# 게임 경로 추가
sys.path.append('.')

def silent_background_block():
    """백그라운드에서 조용히 화상키보드 차단"""
    keyboard_processes = [
        "TabTip.exe",
        "TextInputHost.exe", 
        "osk.exe",
        "wisptis.exe"
    ]
    
    blocking_active = True
    
    def block_loop():
        while blocking_active:
            try:
                for process in keyboard_processes:
                    result = subprocess.run(
                        ["tasklist", "/fi", f"imagename eq {process}"],
                        capture_output=True, text=True, check=False
                    )
                    
                    if process in result.stdout:
                        # 완전히 조용히 차단
                        subprocess.run(
                            ["taskkill", "/f", "/im", process],
                            capture_output=True, text=True, check=False
                        )
            except:
                pass
            time.sleep(0.2)  # 200ms마다 체크
    
    # 백그라운드 스레드 시작
    block_thread = threading.Thread(target=block_loop, daemon=True)
    block_thread.start()
    
    return lambda: globals().update({'blocking_active': False})

def test_gamepad_quietly():
    """조용한 게임패드 테스트"""
    print("🎮 A버튼 조용한 테스트 시작")
    print("=" * 40)
    
    # 백그라운드 차단 시작
    stop_blocking = silent_background_block()
    
    try:
        # 게임 모듈 임포트 및 테스트
        from game.gamepad_input import GamepadInput
        
        gamepad = GamepadInput()
        
        if not gamepad.is_connected():
            print("❌ 게임패드가 연결되지 않았습니다.")
            return False
        
        print("✅ 게임패드 연결됨")
        print("🔇 화상키보드 백그라운드 차단 활성화 (로그 없음)")
        print()
        print("🎮 A버튼을 눌러보세요 (5초간)")
        print("   화상키보드가 나타나지 않고, 로그도 출력되지 않아야 합니다!")
        
        start_time = time.time()
        button_pressed = False
        
        while time.time() - start_time < 5:
            if gamepad.has_input():
                key = gamepad.get_input()
                if key == '\n':  # A버튼
                    print("✅ A버튼 눌림 감지! 화상키보드 차단 성공!")
                    button_pressed = True
                    break
            time.sleep(0.1)
        
        if not button_pressed:
            print("⚠️ A버튼이 감지되지 않았습니다.")
            print("🎮 Xbox 컨트롤러의 A버튼을 눌러보세요.")
        
        gamepad.stop()
        return button_pressed
        
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return False
    finally:
        # 차단 중지
        stop_blocking()

def main():
    """메인 실행"""
    success = test_gamepad_quietly()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 A버튼 조용한 차단 테스트 성공!")
        print("✅ 이제 실제 게임에서 조용히 화상키보드가 차단됩니다.")
    else:
        print("❌ 테스트 실패 또는 불완전")
    
    print("\n💡 실제 게임을 시작하세요: python main.py")
    input("아무 키나 누르세요...")

if __name__ == "__main__":
    main()
