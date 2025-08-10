#!/usr/bin/env python3
"""
Dawn of Stellar - 게임패드 입력 시스템
Xbox/PlayStation/Nintendo Switch Pro 컨트롤러 지원
+ Windows 11 화상키보드 완전 차단 기능
"""

import pygame
import time
import threading
import subprocess
from typing import Dict, Optional, Tuple, List, Callable
from enum import Enum

# 화상키보드 차단을 위한 pynput 임포트
try:
    from pynput.keyboard import Controller as KeyController
    PYNPUT_AVAILABLE = True
except ImportError:
    print("⚠️ pynput 라이브러리가 설치되지 않았습니다. 화상키보드 차단 기능이 제한됩니다.")
    PYNPUT_AVAILABLE = False

class GamepadButtons(Enum):
    """게임패드 버튼 매핑"""
    # 페이스 버튼 (ABXY / 크로스/서클/스퀘어/트라이앵글)
    A = 0           # 확인/선택
    B = 1           # 취소/뒤로
    X = 2           # 인벤토리/메뉴
    Y = 3           # 필드 활동
    
    # 숄더 버튼
    LB = 4          # 파티 상태
    RB = 5          # 도움말
    LT = 6          # 저장
    RT = 7          # 자동전투
    
    # 시스템 버튼
    SELECT = 8      # 로그 확인
    START = 9       # 설정 메뉴
    
    # 스틱 클릭
    L_STICK = 10    # 텔레포트
    R_STICK = 11    # 예비
    
    # D-Pad (십자키)
    DPAD_UP = 12
    DPAD_DOWN = 13
    DPAD_LEFT = 14
    DPAD_RIGHT = 15

class GamepadAxes(Enum):
    """게임패드 축 매핑"""
    # 왼쪽 스틱 (이동)
    LEFT_X = 0      # 좌우 이동
    LEFT_Y = 1      # 상하 이동
    
    # 오른쪽 스틱 (메뉴 탐색)
    RIGHT_X = 2     # 메뉴 좌우
    RIGHT_Y = 3     # 메뉴 상하
    
    # 트리거 (아날로그)
    LEFT_TRIGGER = 4
    RIGHT_TRIGGER = 5

class GamepadMapping:
    """Dawn of Stellar 게임패드 키 매핑"""
    
    def __init__(self):
        # 버튼 → 키보드 매핑
        self.button_mappings = {
            # 페이스 버튼
            GamepadButtons.A: '\n',        # Enter (확인/상호작용)
            GamepadButtons.B: 'q',         # 취소/종료
            GamepadButtons.X: 'i',         # 인벤토리
            GamepadButtons.Y: 'f',         # 필드 활동
            
            # 숄더 버튼
            GamepadButtons.LB: 'p',        # 파티 상태
            GamepadButtons.RB: 'h',        # 도움말
            GamepadButtons.LT: 'b',        # 저장
            GamepadButtons.RT: 't',        # 자동전투 토글
            
            # 시스템 버튼
            GamepadButtons.SELECT: 'l',    # 로그 확인
            GamepadButtons.START: 'm',     # 설정 메뉴
            
            # 스틱 클릭
            GamepadButtons.L_STICK: 'z',   # 긴급 텔레포트
            GamepadButtons.R_STICK: 'r',   # 예비 (AI 요청/핫 리로드)
        }
        
        # D-Pad → 키보드 매핑 (메뉴 탐색/숫자키)
        self.dpad_mappings = {
            GamepadButtons.DPAD_UP: 'w',       # 위 (또는 메뉴에서 1)
            GamepadButtons.DPAD_DOWN: 's',     # 아래 (또는 메뉴에서 2)
            GamepadButtons.DPAD_LEFT: 'a',     # 왼쪽 (또는 메뉴에서 3)
            GamepadButtons.DPAD_RIGHT: 'd',    # 오른쪽 (또는 메뉴에서 4)
        }
        
        # 스틱 데드존
        self.deadzone = 0.3
        
        # 이동 키 반복 설정
        self.movement_repeat_delay = 0.15  # 150ms
        self.last_movement_time = 0
        
        # 메뉴 모드 (메뉴에서는 D-Pad가 숫자키로 동작)
        self.menu_mode = False

class GamepadInput:
    """게임패드 입력 처리 클래스"""
    
    def __init__(self, sound_manager=None):
        # pygame 초기화 (게임패드 전용 환경 설정)
        import os
        
        # 🔧 Windows 게임패드 문제 방지 환경 변수 설정
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # 비디오 비활성화
        os.environ['SDL_AUDIODRIVER'] = 'dummy'  # 오디오 비활성화  
        os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '1'  # 백그라운드 이벤트 허용
        os.environ['SDL_GAMECONTROLLERCONFIG'] = ''  # 기본 컨트롤러 설정 사용
        os.environ['SDL_HINT_JOYSTICK_HIDAPI'] = '1'  # HID API 사용
        os.environ['SDL_HINT_JOYSTICK_HIDAPI_PS4'] = '1'  # PS4 컨트롤러 지원
        os.environ['SDL_HINT_JOYSTICK_HIDAPI_PS5'] = '1'  # PS5 컨트롤러 지원
        os.environ['SDL_HINT_JOYSTICK_HIDAPI_SWITCH'] = '1'  # Switch Pro 컨트롤러 지원
        os.environ['SDL_HINT_JOYSTICK_HIDAPI_XBOX'] = '1'  # Xbox 컨트롤러 지원
        
        # 🚫 Windows 화상키보드 및 다른 앱 활성화 방지
        os.environ['SDL_HINT_TOUCH_MOUSE_EVENTS'] = '0'  # 터치 이벤트 비활성화
        os.environ['SDL_HINT_MOUSE_TOUCH_EVENTS'] = '0'  # 마우스 터치 이벤트 비활성화
        os.environ['SDL_HINT_WINDOWS_DISABLE_THREAD_NAMING'] = '1'  # 스레드 이름 비활성화
        os.environ['SDL_HINT_WINDOWS_INTRESOURCE_ICON'] = '0'  # 아이콘 리소스 비활성화
        os.environ['SDL_HINT_WINDOWS_INTRESOURCE_ICON_SMALL'] = '0'  # 작은 아이콘 비활성화
        
        # 🎮 화상키보드 차단 관련 환경 변수 추가
        os.environ['SDL_TOUCH_EVENTS'] = '0'  # 터치 이벤트 완전 차단
        os.environ['SDL_GESTURE_EVENTS'] = '0'  # 제스처 이벤트 차단
        
        pygame.init()
        pygame.joystick.init()
        
        # 비디오 시스템 초기화 (더미 모드로)
        try:
            pygame.display.set_mode((1, 1))  # 최소 크기 더미 디스플레이
        except:
            pass  # 비디오 초기화 실패해도 조이스틱은 작동 가능
        
        self.joysticks = []
        self.active_joystick = None
        self.mapping = GamepadMapping()
        self.sound_manager = sound_manager
        
        # 입력 큐 (스레드 안전)
        self.input_queue = []
        self.queue_lock = threading.Lock()
        
        # 연속 입력 방지
        self.last_input_time = {}
        self.input_cooldown = 0.1  # 100ms
        
        # 🛡️ 화상키보드 차단 시스템 초기화
        self.keyboard_controller = None
        self.touch_keyboard_monitor_running = False
        self.touch_keyboard_monitor_thread = None
        
        if PYNPUT_AVAILABLE:
            try:
                self.keyboard_controller = KeyController()
                self._start_touch_keyboard_monitor()
                # 초기화 시에만 한 번만 출력
                print("✅ 화상키보드 차단 시스템 활성화 (조용한 모드)")
            except Exception as e:
                print(f"⚠️ 화상키보드 차단 시스템 초기화 실패: {e}")
        
        # 게임패드 감지
        self.detect_gamepads()
        
        # 입력 스레드 시작
        self.running = True
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
        
        print(f"🎮 게임패드 시스템 초기화 완료: {len(self.joysticks)}개 감지됨")
    
    def _start_touch_keyboard_monitor(self):
        """화상키보드 실시간 모니터링 시작"""
        if not PYNPUT_AVAILABLE:
            return
            
        self.touch_keyboard_monitor_running = True
        self.touch_keyboard_monitor_thread = threading.Thread(
            target=self._monitor_touch_keyboard, 
            daemon=True
        )
        self.touch_keyboard_monitor_thread.start()
        
    def _monitor_touch_keyboard(self):
        """화상키보드 실시간 감시 및 즉시 차단 (조용한 모드)"""
        keyboard_processes = [
            "TabTip.exe",
            "TextInputHost.exe", 
            "osk.exe",
            "wisptis.exe"
        ]
        
        # 디버그 모드 (개발자용 - 기본적으로 비활성화)
        debug_mode = False
        
        while self.touch_keyboard_monitor_running:
            try:
                for process in keyboard_processes:
                    # 프로세스 체크
                    result = subprocess.run(
                        ["tasklist", "/fi", f"imagename eq {process}"],
                        capture_output=True, text=True, check=False
                    )
                    
                    if process in result.stdout:
                        # 조용히 차단 (로그 출력 없음)
                        if debug_mode:  # 디버그 모드에서만 출력
                            print(f"🚨 화상키보드 감지! 즉시 차단: {process}")
                        
                        subprocess.run(
                            ["taskkill", "/f", "/im", process],
                            capture_output=True, text=True, check=False
                        )
            except Exception as e:
                # 완전히 조용히 넘어감 (로그 없음)
                pass
            
            time.sleep(0.15)  # 150ms마다 체크 (부하 감소)
    
    def _convert_gamepad_to_keyboard(self, gamepad_key: str) -> str:
        """게임패드 입력을 키보드 이벤트로 변환하여 화상키보드 우회"""
        if not self.keyboard_controller or not PYNPUT_AVAILABLE:
            return gamepad_key
            
        try:
            # 게임패드 키를 키보드 이벤트로 변환
            if gamepad_key == '\n':  # Enter (A버튼)
                self.keyboard_controller.press('\n')
                self.keyboard_controller.release('\n')
                return gamepad_key
            elif gamepad_key == 'q':  # Q (B버튼)
                self.keyboard_controller.press('q')
                self.keyboard_controller.release('q')
                return gamepad_key
            elif gamepad_key == '\x1b':  # ESC (X버튼)
                self.keyboard_controller.press('\x1b')
                self.keyboard_controller.release('\x1b')
                return gamepad_key
            elif gamepad_key in ['w', 'a', 's', 'd']:  # 이동키
                self.keyboard_controller.press(gamepad_key)
                self.keyboard_controller.release(gamepad_key)
                return gamepad_key
            else:
                # 기타 키들도 동일하게 처리
                self.keyboard_controller.press(gamepad_key)
                self.keyboard_controller.release(gamepad_key)
                return gamepad_key
                
        except Exception as e:
            # 변환 실패 시 원래 키 반환
            return gamepad_key
    
    def detect_gamepads(self) -> List[Dict]:
        """연결된 게임패드 감지"""
        self.joysticks.clear()
        gamepad_list = []
        
        joystick_count = pygame.joystick.get_count()
        
        for i in range(joystick_count):
            try:
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                
                gamepad_info = {
                    'index': i,
                    'name': joystick.get_name(),
                    'axes': joystick.get_numaxes(),
                    'buttons': joystick.get_numbuttons(),
                    'hats': joystick.get_numhats(),
                    'instance_id': joystick.get_instance_id(),
                    'joystick': joystick
                }
                
                self.joysticks.append(joystick)
                gamepad_list.append(gamepad_info)
                
                # 첫 번째 게임패드를 활성 게임패드로 설정
                if i == 0:
                    self.active_joystick = joystick
                    print(f"🎮 활성 게임패드: {joystick.get_name()}")
                    
            except Exception as e:
                print(f"⚠️ 게임패드 {i} 초기화 실패: {e}")
                
        return gamepad_list
    
    def _input_loop(self):
        """게임패드 입력 감지 스레드"""
        clock = pygame.time.Clock()
        
        while self.running:
            try:
                pygame.event.pump()  # 이벤트 업데이트
                
                if self.active_joystick:
                    self._process_gamepad_input()
                
                clock.tick(60)  # 60 FPS
                
            except Exception as e:
                print(f"⚠️ 게임패드 입력 루프 오류: {e}")
                time.sleep(0.1)
    
    def _process_gamepad_input(self):
        """게임패드 입력 처리"""
        current_time = time.time()
        
        # 버튼 입력 처리
        for button_enum in GamepadButtons:
            button_id = button_enum.value
            
            # 버튼 범위 확인
            if button_id >= self.active_joystick.get_numbuttons():
                continue
                
            # D-Pad는 HAT으로 처리
            if button_enum in [GamepadButtons.DPAD_UP, GamepadButtons.DPAD_DOWN, 
                              GamepadButtons.DPAD_LEFT, GamepadButtons.DPAD_RIGHT]:
                continue
                
            try:
                if self.active_joystick.get_button(button_id):
                    # 연속 입력 방지
                    last_time = self.last_input_time.get(button_enum, 0)
                    if current_time - last_time < self.input_cooldown:
                        continue
                        
                    # 버튼 매핑된 키 가져오기
                    mapped_key = self.mapping.button_mappings.get(button_enum)
                    if mapped_key:
                        self._add_input(mapped_key)
                        self.last_input_time[button_enum] = current_time
                        
                        # 사운드 효과
                        if self.sound_manager:
                            self.sound_manager.play_sfx("menu_select")
                            
            except Exception as e:
                print(f"⚠️ 버튼 {button_id} 처리 오류: {e}")
        
        # D-Pad (HAT) 처리
        if self.active_joystick.get_numhats() > 0:
            try:
                hat_value = self.active_joystick.get_hat(0)
                self._process_dpad(hat_value, current_time)
            except Exception as e:
                print(f"⚠️ D-Pad 처리 오류: {e}")
        
        # 왼쪽 스틱 (이동) 처리
        try:
            left_x = self.active_joystick.get_axis(GamepadAxes.LEFT_X.value)
            left_y = self.active_joystick.get_axis(GamepadAxes.LEFT_Y.value)
            self._process_movement_stick(left_x, left_y, current_time)
        except Exception as e:
            print(f"⚠️ 왼쪽 스틱 처리 오류: {e}")
    
    def _process_dpad(self, hat_value: Tuple[int, int], current_time: float):
        """D-Pad 입력 처리"""
        x, y = hat_value
        
        # D-Pad 방향 감지
        dpad_pressed = None
        if y == 1:      # 위
            dpad_pressed = GamepadButtons.DPAD_UP
        elif y == -1:   # 아래
            dpad_pressed = GamepadButtons.DPAD_DOWN
        elif x == -1:   # 왼쪽
            dpad_pressed = GamepadButtons.DPAD_LEFT
        elif x == 1:    # 오른쪽
            dpad_pressed = GamepadButtons.DPAD_RIGHT
            
        if dpad_pressed:
            # 연속 입력 방지
            last_time = self.last_input_time.get(dpad_pressed, 0)
            if current_time - last_time < self.input_cooldown:
                return
                
            # 메뉴 모드에 따라 다른 매핑 사용
            if self.mapping.menu_mode:
                # 메뉴에서는 D-Pad가 숫자키로 동작
                number_mapping = {
                    GamepadButtons.DPAD_UP: '1',
                    GamepadButtons.DPAD_DOWN: '2', 
                    GamepadButtons.DPAD_LEFT: '3',
                    GamepadButtons.DPAD_RIGHT: '4'
                }
                mapped_key = number_mapping.get(dpad_pressed)
            else:
                # 일반 모드에서는 이동키로 동작
                mapped_key = self.mapping.dpad_mappings.get(dpad_pressed)
                
            if mapped_key:
                self._add_input(mapped_key)
                self.last_input_time[dpad_pressed] = current_time
                
                # 사운드 효과
                if self.sound_manager:
                    if self.mapping.menu_mode:
                        self.sound_manager.play_sfx("menu_select")
                    else:
                        self.sound_manager.play_sfx("menu_move")
    
    def _process_movement_stick(self, left_x: float, left_y: float, current_time: float):
        """왼쪽 스틱 이동 처리"""
        # 데드존 적용
        if abs(left_x) < self.mapping.deadzone and abs(left_y) < self.mapping.deadzone:
            return
            
        # 이동 반복 딜레이 체크
        if current_time - self.mapping.last_movement_time < self.mapping.movement_repeat_delay:
            return
            
        # 8방향 이동 계산
        movement_key = None
        
        if abs(left_x) > abs(left_y):  # 좌우 이동이 더 강함
            if left_x > self.mapping.deadzone:
                movement_key = 'd'  # 오른쪽
            elif left_x < -self.mapping.deadzone:
                movement_key = 'a'  # 왼쪽
        else:  # 상하 이동이 더 강함
            if left_y > self.mapping.deadzone:
                movement_key = 's'  # 아래
            elif left_y < -self.mapping.deadzone:
                movement_key = 'w'  # 위
                
        # 대각선 이동 지원
        if abs(left_x) > self.mapping.deadzone and abs(left_y) > self.mapping.deadzone:
            if left_x < 0 and left_y < 0:  # 왼쪽 위
                movement_key = 'q'
            elif left_x > 0 and left_y < 0:  # 오른쪽 위
                movement_key = 'e'
            # 다른 대각선은 기본 상하좌우로 처리
                
        if movement_key:
            self._add_input(movement_key)
            self.mapping.last_movement_time = current_time
            
            # 이동 사운드
            if self.sound_manager:
                self.sound_manager.play_sfx("step")
    
    def _add_input(self, key: str):
        """입력을 큐에 추가 (스레드 안전) + 화상키보드 차단"""
        # 🛡️ 화상키보드 차단을 위한 키보드 이벤트 변환
        converted_key = self._convert_gamepad_to_keyboard(key)
        
        with self.queue_lock:
            self.input_queue.append(converted_key)
    
    def get_input(self) -> Optional[str]:
        """큐에서 입력 가져오기"""
        with self.queue_lock:
            if self.input_queue:
                return self.input_queue.pop(0)
        return None
    
    def has_input(self) -> bool:
        """입력이 있는지 확인"""
        with self.queue_lock:
            return len(self.input_queue) > 0
    
    def clear_input_queue(self):
        """입력 큐 클리어"""
        with self.queue_lock:
            self.input_queue.clear()
    
    def set_menu_mode(self, enabled: bool):
        """메뉴 모드 설정 (D-Pad 매핑 변경)"""
        self.mapping.menu_mode = enabled
        
    def is_connected(self) -> bool:
        """게임패드 연결 상태 확인"""
        return self.active_joystick is not None
    
    def get_gamepad_info(self) -> Dict:
        """활성 게임패드 정보"""
        if self.active_joystick:
            return {
                'name': self.active_joystick.get_name(),
                'axes': self.active_joystick.get_numaxes(),
                'buttons': self.active_joystick.get_numbuttons(),
                'hats': self.active_joystick.get_numhats()
            }
        return {}
    
    def stop(self):
        """게임패드 시스템 정지"""
        self.running = False
        
        # 🛡️ 화상키보드 모니터링 중지
        if self.touch_keyboard_monitor_running:
            self.touch_keyboard_monitor_running = False
            if self.touch_keyboard_monitor_thread and self.touch_keyboard_monitor_thread.is_alive():
                self.touch_keyboard_monitor_thread.join(timeout=1.0)
                
        if self.input_thread.is_alive():
            self.input_thread.join(timeout=1.0)
        pygame.joystick.quit()
        
    def __del__(self):
        """소멸자"""
        self.stop()

class HybridInputManager:
    """키보드 + 게임패드 통합 입력 관리자"""
    
    def __init__(self, keyboard_input, sound_manager=None):
        self.keyboard_input = keyboard_input
        self.gamepad_input = None
        self.sound_manager = sound_manager
        
        # 게임패드 초기화 시도
        try:
            self.gamepad_input = GamepadInput(sound_manager)
            if self.gamepad_input.is_connected():
                print(f"🎮 하이브리드 입력 모드: 키보드 + {self.gamepad_input.get_gamepad_info()['name']}")
            else:
                print("⌨️ 키보드 전용 모드: 게임패드가 연결되지 않았습니다")
        except Exception as e:
            print(f"⚠️ 게임패드 초기화 실패: {e}")
            self.gamepad_input = None
    
    def get_key(self) -> str:
        """키보드 또는 게임패드에서 입력 받기"""
        # 게임패드 입력 우선 확인
        if self.gamepad_input and self.gamepad_input.has_input():
            return self.gamepad_input.get_input()
            
        # 키보드 입력 (넌블로킹)
        try:
            # 키보드 입력이 있는지 확인
            if hasattr(self.keyboard_input, 'has_input') and self.keyboard_input.has_input():
                return self.keyboard_input.get_key()
            elif hasattr(self.keyboard_input, 'get_key_non_blocking'):
                return self.keyboard_input.get_key_non_blocking()
        except:
            pass
            
        return None
    
    def wait_for_key(self, message: str = "아무 키나 누르세요...") -> str:
        """키보드 또는 게임패드 입력 대기"""
        print(message, end='', flush=True)
        
        while True:
            # 게임패드 입력 확인
            if self.gamepad_input and self.gamepad_input.has_input():
                key = self.gamepad_input.get_input()
                print()  # 줄바꿈
                return key
            
            # 키보드 입력 확인 (넌블로킹)
            try:
                key = self.get_key()
                if key:
                    print()  # 줄바꿈
                    return key
            except:
                pass
                
            time.sleep(0.016)  # 60 FPS
    
    def set_menu_mode(self, enabled: bool):
        """메뉴 모드 설정"""
        if self.gamepad_input:
            self.gamepad_input.set_menu_mode(enabled)
    
    def clear_input_buffer(self):
        """모든 입력 버퍼 클리어"""
        if self.keyboard_input and hasattr(self.keyboard_input, 'clear_input_buffer'):
            self.keyboard_input.clear_input_buffer()
        if self.gamepad_input:
            self.gamepad_input.clear_input_queue()
    
    def is_gamepad_connected(self) -> bool:
        """게임패드 연결 상태"""
        return self.gamepad_input and self.gamepad_input.is_connected()
    
    def get_input_info(self) -> str:
        """현재 입력 방법 정보"""
        if self.is_gamepad_connected():
            gamepad_info = self.gamepad_input.get_gamepad_info()
            return f"🎮 {gamepad_info['name']} + ⌨️ 키보드"
        else:
            return "⌨️ 키보드 전용"

# 게임패드 버튼 매핑 가이드
GAMEPAD_GUIDE = """
🎮 Dawn of Stellar 게임패드 조작법

📍 이동:
   왼쪽 스틱     → 캐릭터 이동 (8방향)
   D-Pad         → 캐릭터 이동 (4방향) 또는 메뉴 선택

🎯 액션:
   A 버튼        → 확인/상호작용 (Enter)
   B 버튼        → 취소/종료 (Q)
   X 버튼        → 인벤토리 (I)
   Y 버튼        → 필드 활동 (F)

📋 메뉴:
   LB (L1)       → 파티 상태 (P)
   RB (R1)       → 도움말 (H)
   LT (L2)       → 게임 저장 (B)
   RT (R2)       → 자동전투 토글 (T)

⚙️ 시스템:
   Select/Share  → 로그 확인 (L)
   Start/Menu    → 설정 메뉴 (M)
   L스틱 클릭    → 긴급 텔레포트 (Z)
   R스틱 클릭    → AI 요청/핫 리로드 (R)

💡 팁: 게임패드와 키보드를 동시에 사용할 수 있습니다!
"""

def enable_gamepad_for_game():
    """게임에서 게임패드 사용을 위한 환경 재설정"""
    import os
    
    # 🎮 런처에서 설정된 게임패드 비활성화 환경변수들을 제거
    gamepad_disable_vars = [
        'DISABLE_GAMEPAD',
        'SDL_GAMECONTROLLER_IGNORE_DEVICES', 
        'SDL_JOYSTICK_DEVICE'
    ]
    
    for var in gamepad_disable_vars:
        if var in os.environ:
            del os.environ[var]
    
    # ✅ 게임용 게임패드 활성화 설정
    os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '1'  # 백그라운드 이벤트 허용
    os.environ['SDL_HINT_JOYSTICK_HIDAPI'] = '1'  # HID API 사용
    os.environ['SDL_HINT_JOYSTICK_HIDAPI_PS4'] = '1'  # PS4 컨트롤러 지원
    os.environ['SDL_HINT_JOYSTICK_HIDAPI_PS5'] = '1'  # PS5 컨트롤러 지원
    os.environ['SDL_HINT_JOYSTICK_HIDAPI_SWITCH'] = '1'  # Switch Pro 컨트롤러 지원
    os.environ['SDL_HINT_JOYSTICK_HIDAPI_XBOX'] = '1'  # Xbox 컨트롤러 지원
    
    # 🛡️ 하지만 여전히 화상키보드와 다른 앱 간섭은 방지
    os.environ['SDL_HINT_TOUCH_MOUSE_EVENTS'] = '0'  # 터치 이벤트 비활성화
    os.environ['SDL_HINT_MOUSE_TOUCH_EVENTS'] = '0'  # 마우스 터치 이벤트 비활성화
    os.environ['SDL_HINT_WINDOWS_DISABLE_THREAD_NAMING'] = '1'  # 스레드 이름 비활성화
    
    print("🎮 게임패드가 게임용으로 활성화되었습니다!")
