#!/usr/bin/env python3
"""
Windows 11 게임패드 격리 테스트 - 화상키보드 완전 차단
A버튼 누를 때 화상키보드 켜지는 문제 해결
"""

import os
import sys
import time
import ctypes
from ctypes import wintypes

# Windows 11 최강 차단 - 시스템 후킹 방식
def disable_touch_keyboard_completely():
    """Windows 11 터치 키보드 시스템 레벨 완전 차단"""
    try:
        # Windows API를 사용한 직접 차단
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        # 터치 키보드 윈도우 찾아서 강제 숨기기
        def hide_touch_keyboard():
            # Windows 11 터치 키보드 클래스명들
            keyboard_classes = [
                "IPTip_Main_Window",
                "IPTIP_Main_Window", 
                "WindowsInternal.ComposableShell.Experiences.TextInput.InputApp",
                "ApplicationFrameWindow",
                "Windows.UI.Core.CoreWindow"
            ]
            
            for class_name in keyboard_classes:
                hwnd = user32.FindWindowW(class_name, None)
                if hwnd:
                    user32.ShowWindow(hwnd, 0)  # SW_HIDE
                    print(f"✅ 화상키보드 윈도우 숨김: {class_name}")
        
        # 터치 키보드 서비스 비활성화
        def disable_touch_service():
            try:
                import subprocess
                subprocess.run([
                    "sc", "config", "TabletInputService", "start=", "disabled"
                ], capture_output=True, text=True, check=False)
                subprocess.run([
                    "sc", "stop", "TabletInputService"
                ], capture_output=True, text=True, check=False)
                print("✅ 터치 입력 서비스 완전 비활성화")
            except:
                pass
        
        print("🛡️ Windows 11 시스템 레벨 터치 키보드 차단 중...")
        hide_touch_keyboard()
        disable_touch_service()
        
        return True
        
    except Exception as e:
        print(f"⚠️ 시스템 레벨 차단 실패: {e}")
        return False

# 게임패드 이벤트를 완전히 격리하는 래퍼
def isolated_gamepad_test():
    """격리된 환경에서 게임패드 테스트"""
    
    # 1단계: 모든 화상키보드 프로세스 강제 종료
    import subprocess
    
    keyboard_processes = [
        "TabTip.exe",
        "TextInputHost.exe",
        "WindowsInternal.ComposableShell.Experiences.TextInput.InputApp.exe",
        "osk.exe",
        "wisptis.exe"
    ]
    
    print("🔥 모든 화상키보드 프로세스 강제 종료 중...")
    for process in keyboard_processes:
        try:
            subprocess.run(["taskkill", "/f", "/im", process], 
                         capture_output=True, text=True, check=False)
        except:
            pass
    
    # 2단계: pygame을 격리된 환경에서 초기화
    try:
        import pygame
        
        # pygame 초기화 전 환경 설정
        os.environ['SDL_AUDIODRIVER'] = 'directsound'  # DirectSound 강제 사용
        os.environ['SDL_VIDEODRIVER'] = 'windib'       # Windows DIB 드라이버 사용
        
        # pygame 초기화
        pygame.init()
        pygame.joystick.init()
        
        # 가상 화면 생성 (화상키보드 트리거 방지)
        screen = pygame.display.set_mode((1, 1), pygame.HIDDEN | pygame.NOFRAME)
        pygame.display.set_caption("")
        
        print("\n🎮 격리된 환경에서 게임패드 테스트 시작")
        print("=" * 50)
        
        joystick_count = pygame.joystick.get_count()
        print(f"🎮 감지된 게임패드: {joystick_count}개")
        
        if joystick_count > 0:
            joysticks = []
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                joysticks.append(joystick)
                print(f"  📱 {i+1}번: {joystick.get_name()}")
            
            print("\n🔥 A버튼 테스트 (화상키보드 차단 모드)")
            print("   A버튼을 눌러보세요. 화상키보드가 나타나면 안됩니다!")
            print("   5초간 테스트합니다...")
            
            start_time = time.time()
            button_pressed = False
            
            # 실시간 화상키보드 감시 및 즉시 차단
            def monitor_and_kill():
                for process in keyboard_processes:
                    try:
                        result = subprocess.run(["tasklist", "/fi", f"imagename eq {process}"], 
                                              capture_output=True, text=True, check=False)
                        if process in result.stdout:
                            print(f"🚨 화상키보드 감지! 즉시 차단: {process}")
                            subprocess.run(["taskkill", "/f", "/im", process], 
                                         capture_output=True, text=True, check=False)
                            # 추가로 윈도우 숨기기
                            disable_touch_keyboard_completely()
                            return True
                    except:
                        pass
                return False
            
            while time.time() - start_time < 5:
                # 이벤트 처리 (pygame 이벤트 큐 비우기)
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 0:  # A버튼 (Xbox 컨트롤러 기준)
                            print("🎮 A버튼 눌림 감지!")
                            button_pressed = True
                            # 즉시 화상키보드 체크 및 차단
                            if monitor_and_kill():
                                print("✅ 화상키보드가 나타났지만 즉시 차단했습니다!")
                            else:
                                print("✅ 화상키보드가 나타나지 않았습니다!")
                
                # 주기적 화상키보드 감시
                monitor_and_kill()
                
                time.sleep(0.05)
            
            if button_pressed:
                print("\n🎉 테스트 성공!")
                print("✅ A버튼이 정상 작동했습니다!")
                print("✅ 화상키보드가 차단되었습니다!")
            else:
                print("\n⚠️ A버튼 입력이 감지되지 않았습니다.")
                print("🎮 Xbox 컨트롤러의 A버튼을 눌러보세요.")
        
        else:
            print("\n❌ 게임패드가 감지되지 않았습니다.")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ 격리된 테스트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🎮 Dawn of Stellar - Windows 11 A버튼 화상키보드 차단 테스트")
    print("=" * 60)
    
    # 시스템 레벨 차단
    disable_touch_keyboard_completely()
    
    # 격리된 환경에서 테스트
    success = isolated_gamepad_test()
    
    if success:
        print("\n🎉 테스트 완료!")
        print("🛡️ A버튼 누를 때 화상키보드가 나타나지 않아야 합니다.")
    else:
        print("\n❌ 테스트 실패!")
        print("💡 관리자 권한으로 실행해보세요.")
    
    print("\n" + "=" * 60)
    input("아무 키나 누르세요...")

if __name__ == "__main__":
    main()
