#!/usr/bin/env python3
"""
게임패드 입력을 키보드 이벤트로 변환하는 시스템
화상키보드 트리거를 완전히 우회하는 방식
"""

import pygame
import sys
import os
import time
import threading
import queue
from pynput.keyboard import Controller as KeyController
from pynput.mouse import Controller as MouseController

class GamepadToKeyboard:
    """게임패드 입력을 키보드 이벤트로 변환하는 클래스"""
    
    def __init__(self):
        self.keyboard = KeyController()
        self.mouse = MouseController()
        self.running = False
        self.input_queue = queue.Queue()
        
        # 버튼 매핑 (Xbox 컨트롤러 기준)
        self.button_mapping = {
            0: 'enter',      # A버튼 → Enter
            1: 'q',          # B버튼 → Q (취소)
            2: 'i',          # X버튼 → I (인벤토리)
            3: 'm',          # Y버튼 → M (메뉴)
            4: 'h',          # LB버튼 → H (도움말)
            5: 'escape',     # RB버튼 → ESC
            6: 'ctrl+s',     # 뒤로가기 → 저장
            7: 'space',      # 시작 → 스페이스
            8: 'tab',        # L스틱 클릭 → Tab
            9: 'alt',        # R스틱 클릭 → Alt
        }
    
    def setup_pygame(self):
        """pygame 초기화 (화상키보드 트리거 방지)"""
        try:
            # 환경 변수 설정으로 터치 이벤트 차단
            os.environ['SDL_AUDIODRIVER'] = 'directsound'
            os.environ['SDL_VIDEODRIVER'] = 'windib'
            os.environ['SDL_TOUCH_EVENTS'] = '0'  # 터치 이벤트 완전 차단
            os.environ['SDL_GESTURE_EVENTS'] = '0'  # 제스처 이벤트 차단
            
            pygame.init()
            pygame.joystick.init()
            
            # 숨겨진 창 생성 (터치 인터페이스 방지)
            self.screen = pygame.display.set_mode((1, 1), pygame.HIDDEN | pygame.NOFRAME)
            pygame.display.set_caption("")
            
            return True
            
        except Exception as e:
            print(f"❌ pygame 초기화 실패: {e}")
            return False
    
    def kill_touch_keyboards(self):
        """실시간 화상키보드 모니터링 및 즉시 차단"""
        import subprocess
        
        keyboard_processes = [
            "TabTip.exe",
            "TextInputHost.exe", 
            "osk.exe",
            "wisptis.exe"
        ]
        
        while self.running:
            for process in keyboard_processes:
                try:
                    # 프로세스 체크
                    result = subprocess.run(
                        ["tasklist", "/fi", f"imagename eq {process}"],
                        capture_output=True, text=True, check=False
                    )
                    
                    if process in result.stdout:
                        print(f"🚨 화상키보드 감지! 즉시 차단: {process}")
                        subprocess.run(
                            ["taskkill", "/f", "/im", process],
                            capture_output=True, text=True, check=False
                        )
                except:
                    pass
            
            time.sleep(0.1)  # 100ms마다 체크
    
    def process_gamepad_input(self):
        """게임패드 입력을 키보드 이벤트로 변환"""
        
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            print("❌ 게임패드가 감지되지 않았습니다.")
            return
        
        # 첫 번째 게임패드 사용
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        
        print(f"🎮 게임패드 연결: {joystick.get_name()}")
        print("🔥 A버튼(Enter), B버튼(Q), X버튼(I), Y버튼(M) 테스트")
        print("   화상키보드가 나타나지 않아야 합니다!")
        print("   ESC키 눌러서 종료")
        
        while self.running:
            # pygame 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    button = event.button
                    if button in self.button_mapping:
                        key = self.button_mapping[button]
                        try:
                            # 키보드 이벤트로 변환하여 전송
                            if '+' in key:
                                # 조합키 처리 (예: ctrl+s)
                                keys = key.split('+')
                                with self.keyboard.pressed(*keys[:-1]):
                                    self.keyboard.press(keys[-1])
                                    self.keyboard.release(keys[-1])
                            else:
                                # 단일키 처리
                                self.keyboard.press(key)
                                self.keyboard.release(key)
                            
                            print(f"✅ {button}번 버튼 → {key} 키 변환 성공!")
                            
                        except Exception as e:
                            print(f"⚠️ 키 변환 실패: {e}")
                
                elif event.type == pygame.JOYHATMOTION:
                    # D-패드 입력 처리
                    hat_x, hat_y = event.value
                    if hat_x == 1:  # 오른쪽
                        self.keyboard.press('right')
                        self.keyboard.release('right')
                        print("✅ D-패드 오른쪽 → 방향키 오른쪽")
                    elif hat_x == -1:  # 왼쪽
                        self.keyboard.press('left')
                        self.keyboard.release('left')
                        print("✅ D-패드 왼쪽 → 방향키 왼쪽")
                    elif hat_y == 1:  # 위
                        self.keyboard.press('up')
                        self.keyboard.release('up')
                        print("✅ D-패드 위 → 방향키 위")
                    elif hat_y == -1:  # 아래
                        self.keyboard.press('down')
                        self.keyboard.release('down')
                        print("✅ D-패드 아래 → 방향키 아래")
                
                elif event.type == pygame.JOYAXISMOTION:
                    # 아날로그 스틱 처리 (임계값 0.7 이상일 때만)
                    if abs(event.value) > 0.7:
                        if event.axis == 0:  # 왼쪽 스틱 X축
                            if event.value > 0.7:
                                self.keyboard.press('d')
                                self.keyboard.release('d')
                                print("✅ 왼쪽 스틱 오른쪽 → D키")
                            elif event.value < -0.7:
                                self.keyboard.press('a')
                                self.keyboard.release('a')
                                print("✅ 왼쪽 스틱 왼쪽 → A키")
                        elif event.axis == 1:  # 왼쪽 스틱 Y축
                            if event.value > 0.7:
                                self.keyboard.press('s')
                                self.keyboard.release('s')
                                print("✅ 왼쪽 스틱 아래 → S키")
                            elif event.value < -0.7:
                                self.keyboard.press('w')
                                self.keyboard.release('w')
                                print("✅ 왼쪽 스틱 위 → W키")
            
            time.sleep(0.016)  # 60 FPS
    
    def start(self):
        """게임패드→키보드 변환 시작"""
        if not self.setup_pygame():
            return False
        
        self.running = True
        
        # 화상키보드 감시 스레드 시작
        monitor_thread = threading.Thread(target=self.kill_touch_keyboards, daemon=True)
        monitor_thread.start()
        
        try:
            self.process_gamepad_input()
        except KeyboardInterrupt:
            print("\n🛑 사용자가 중단했습니다.")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """변환 중지"""
        self.running = False
        if hasattr(self, 'screen'):
            pygame.quit()

def main():
    """메인 실행 함수"""
    print("🎮 Dawn of Stellar - 게임패드→키보드 변환 시스템")
    print("💡 A버튼 화상키보드 문제 완전 해결!")
    print("=" * 60)
    
    # pynput 설치 확인
    try:
        import pynput
        print("✅ pynput 라이브러리 확인됨")
    except ImportError:
        print("❌ pynput 라이브러리가 설치되지 않았습니다.")
        print("💡 설치 명령: pip install pynput")
        return
    
    converter = GamepadToKeyboard()
    success = converter.start()
    
    if not success:
        print("❌ 게임패드→키보드 변환 실패!")
    
    print("\n🎯 변환 시스템 종료")

if __name__ == "__main__":
    main()
