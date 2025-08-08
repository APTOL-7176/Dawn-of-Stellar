#!/usr/bin/env python3
"""
입력 유틸리티 - 키보드 입력을 바로 받기 위한 모듈
"""

import sys
import os

class KeyboardInput:
    """키보드 입력을 바로 받는 클래스"""
    
    def __init__(self, sound_manager=None):
        # subprocess 환경에서는 강제로 input() 모드 사용
        self.use_subprocess_mode = os.getenv('SUBPROCESS_MODE') == '1'
        
        if self.use_subprocess_mode:
            # subprocess 환경에서는 getch 대신 input() 사용
            self.getch_func = self._fallback_input
        else:
            self.getch_func = self._get_getch_function()
            
        # 키 반복 입력을 위한 상태 추적
        self.key_press_time = {}
        self.key_last_repeat = {}
        self.initial_delay = 0.5      # 처음 입력 후 0.5초 대기
        self.repeat_delay = 0.1       # 이후 0.1초마다 반복 (1초에 10번)
            
        # 오디오 매니저 자동 설정
        if not sound_manager:
            try:
                from .audio_system import get_audio_manager
                self.sound_manager = get_audio_manager()
            except ImportError:
                self.sound_manager = None
        else:
            self.sound_manager = sound_manager
    
    def _get_getch_function(self):
        """OS에 맞는 getch 함수 반환"""
        try:
            # Windows
            if os.name == 'nt':
                import msvcrt
                return msvcrt.getch
            # Unix/Linux/Mac
            else:
                import tty, termios
                def _unix_getch():
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    return ch
                return _unix_getch
        except ImportError:
            # 백업: 일반 input() 사용
            return self._fallback_input
    
    def _fallback_input(self):
        """백업 입력 함수 - subprocess 환경에서 사용"""
        try:
            prompt = "" if self.use_subprocess_mode else "명령: "
            user_input = input(prompt)
            # 빈 줄은 Enter로 간주
            if user_input == "" or user_input == "\n":
                return '\n'
            user_input = user_input.lower().strip()
            return user_input[:1] if user_input else ''
        except (EOFError, KeyboardInterrupt):
            return 'q'  # 종료 신호
    
    def get_key(self) -> str:
        """키 입력 받기"""
        try:
            # subprocess 모드에서는 항상 input() 사용
            if self.use_subprocess_mode:
                return self.getch_func()
                
            if os.name == 'nt':
                # Windows: bytes를 string으로 변환
                key = self.getch_func()
                if isinstance(key, bytes):
                    key = key.decode('utf-8', errors='ignore')
                    
                # 키 입력 효과음 비활성화 (중복 방지 - cursor_menu_system에서 처리)
                # if self.sound_manager:
                #     self.sound_manager.play_sfx("menu_select")
                    
                return key.lower()
            else:
                # Unix 계열
                key = self.getch_func().lower()
                
                # 키 입력 효과음 비활성화 (중복 방지 - cursor_menu_system에서 처리)
                # if self.sound_manager:
                #     self.sound_manager.play_sfx("menu_select")
                    
                return key
        except:
            # 에러 발생시 백업으로 input() 사용
            prompt = "" if self.use_subprocess_mode else "명령: "
            result = input(prompt).lower().strip()[:1]
            
            # 키 입력 효과음 비활성화 (중복 방지 - cursor_menu_system에서 처리)
            # if self.sound_manager:
            #     self.sound_manager.play_sfx("menu_select")
                
            return result
    
    def clear_input_buffer(self):
        """입력 버퍼 클리어 - 선입력 방지"""
        try:
            if os.name == 'nt':
                # Windows
                import msvcrt
                while msvcrt.kbhit():
                    msvcrt.getch()
            else:
                # Unix 계열
                import sys, select
                while select.select([sys.stdin], [], [], 0.0)[0]:
                    sys.stdin.read(1)
        except:
            pass  # 실패해도 무시
    
    def wait_for_key(self, message: str = "아무 키나 누르세요...") -> str:
        """메시지와 함께 키 대기"""
        print(message, end='', flush=True)
        
        # 먼저 입력 버퍼 클리어
        self.clear_input_buffer()
        
        # AI 자동 모드 체크
        import sys
        if hasattr(sys.modules.get('__main__'), 'ai_auto_mode') and sys.modules.get('__main__').ai_auto_mode:
            print(" 🤖 자동 진행")
            import time
            time.sleep(0.2)  # 0.2초 대기
            return 'enter'  # 기본 키 반환
        else:
            key = self.get_key()
            print()  # 줄바꿈
            return key
    
    def get_string_input(self, prompt: str = "") -> str:
        """문자열 입력 받기 (숫자 입력용)"""
        try:
            if prompt:
                print(prompt, end='', flush=True)
            
            # AI 자동 모드 체크
            import sys
            if hasattr(sys.modules.get('__main__'), 'ai_auto_mode') and sys.modules.get('__main__').ai_auto_mode:
                print("🤖 자동 입력: 기본값")
                return ""
            
            # 실제 문자열 입력 받기
            result = input().strip()
            return result
            
        except (EOFError, KeyboardInterrupt):
            return ""

def get_single_key_input(prompt: str = "") -> str:
    """단일 키 입력 받기 (편의 함수)"""
    keyboard = KeyboardInput()
    if prompt:
        print(prompt, end='', flush=True)
    key = keyboard.get_key()
    print()  # 줄바꿈
    return key

def wait_for_any_key(message: str = "아무 키나 누르세요...") -> str:
    """아무 키나 눌러서 계속하기"""
    import sys
    if hasattr(sys.modules.get('__main__'), 'ai_auto_mode') and sys.modules.get('__main__').ai_auto_mode:
        print(f"{message} 🤖 자동 진행")
        import time
        time.sleep(0.2)  # 0.2초 대기
        return 'enter'  # 기본 키 반환
    else:
        keyboard = KeyboardInput()
        return keyboard.wait_for_key(message)


class InputManager:
    """입력 관리자 클래스 - KeyboardInput의 래퍼"""
    
    def __init__(self):
        self.keyboard = KeyboardInput()
    
    def get_key(self) -> str:
        """키 입력 받기 - KeyboardInput과 동일"""
        return self.keyboard.get_key()
    
    def wait_for_key(self, message: str = "아무 키나 누르세요...") -> str:
        """메시지와 함께 키 대기"""
        return self.keyboard.wait_for_key(message)


class GamepadInput:
    """게임패드 입력 처리 클래스 (데스크탑용) - 지연 초기화 + 진동 기능"""
    
    def __init__(self):
        self.pygame_available = False
        self.joystick = None
        self.last_button_state = {}
        self.button_cooldown = {}
        
        # 키보드 스타일 반복 입력 설정
        self.initial_delay = 0.5      # 처음 입력 후 0.5초 대기
        self.repeat_delay = 0.1       # 이후 0.1초마다 반복 (1초에 10번)
        self.button_press_time = {}   # 버튼이 처음 눌린 시간
        self.button_last_repeat = {}  # 마지막 반복 입력 시간
        
        # 진동 설정
        self.vibration_enabled = True
        self.vibration_strength = 0.8  # 기본 진동 강도 (0.0~1.0)
        
        self.initialized = False  # 지연 초기화 플래그
    
    def _lazy_init_gamepad(self):
        """게임패드 지연 초기화 - 실제 사용 시에만 초기화"""
        if self.initialized:
            return
            
        self.initialized = True
        try:
            # pygame 출력 숨기기
            import os
            os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
            
            import pygame
            
            # SDL 환경 변수 설정 - 터미널 환경 최적화
            os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '1'
            os.environ['SDL_VIDEODRIVER'] = 'dummy'  # 비디오 드라이버 비활성화
            os.environ['SDL_AUDIODRIVER'] = 'dummy'  # 오디오 드라이버 비활성화
            
            pygame.init()
            pygame.joystick.init()
            
            # 이벤트 큐 비우기 (다른 프로그램 간섭 방지)
            pygame.event.clear()
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.pygame_available = True
            else:
                self.pygame_available = False
                self.joystick = None
        except ImportError:
            self.pygame_available = False
            self.joystick = None
        except Exception:
            self.pygame_available = False
            self.joystick = None
    
    def is_available(self) -> bool:
        """게임패드 사용 가능 여부"""
        if not self.initialized:
            self._lazy_init_gamepad()
        return self.pygame_available and self.joystick is not None
    
    def set_vibration_enabled(self, enabled: bool):
        """진동 활성화/비활성화"""
        self.vibration_enabled = enabled
    
    def set_vibration_strength(self, strength: float):
        """진동 강도 설정 (0.0~1.0)"""
        self.vibration_strength = max(0.0, min(1.0, strength))
    
    def vibrate(self, duration: float = 0.1, intensity: float = None):
        """게임패드 진동 (다중 대안 방식)
        
        Args:
            duration: 진동 지속 시간 (초)
            intensity: 진동 강도 (None이면 기본 설정 사용)
        """
        if not self.vibration_enabled or not self.is_available():
            return
        
        try:
            import pygame
            import threading
            import time
            
            if intensity is None:
                intensity = self.vibration_strength
            
            # 진동 강도 제한
            intensity = max(0.0, min(1.0, intensity))
            
            def vibrate_thread():
                success = False
                
                try:
                    # 방법 1: Windows XInput 직접 호출 (가장 안정적) - 우선순위 변경
                    try:
                        import ctypes
                        import ctypes.wintypes
                        
                        # Windows xinput 진동 시도
                        if hasattr(ctypes, 'windll'):
                            xinput = ctypes.windll.xinput1_4
                            # 좌우 모터에 동일한 강도 적용
                            left_motor = int(intensity * 65535)  # 저주파 모터
                            right_motor = int(intensity * 65535) # 고주파 모터
                            
                            # XINPUT_VIBRATION 구조체 생성
                            class XINPUT_VIBRATION(ctypes.Structure):
                                _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                                           ("wRightMotorSpeed", ctypes.c_ushort)]
                            
                            vibration = XINPUT_VIBRATION(left_motor, right_motor)
                            result = xinput.XInputSetState(0, ctypes.byref(vibration))
                            
                            if result == 0:  # ERROR_SUCCESS
                                success = True
                                time.sleep(duration)
                                # 진동 정지
                                stop_vibration = XINPUT_VIBRATION(0, 0)
                                xinput.XInputSetState(0, ctypes.byref(stop_vibration))
                    except Exception as e:
                        print(f"🔧 XInput 진동 실패: {e}")
                    
                    # 방법 2: pygame rumble (백업)
                    if not success and hasattr(self.joystick, 'rumble'):
                        try:
                            duration_ms = int(duration * 1000)
                            result = self.joystick.rumble(intensity, intensity, duration_ms)
                            if result:
                                success = True
                                time.sleep(duration)
                        except Exception as e:
                            print(f"🔧 pygame rumble 실패: {e}")
                    
                    # 방법 3: 펄스 진동 (폴백)
                    if not success:
                        try:
                            pulse_count = max(3, int(duration / 0.06))  # 60ms 단위로 분할
                            pulse_duration = duration / pulse_count
                            
                            for i in range(pulse_count):
                                if hasattr(self.joystick, 'rumble'):
                                    self.joystick.rumble(intensity, intensity, 60)  # 60ms씩
                                time.sleep(pulse_duration)
                            success = True
                        except Exception as e:
                            print(f"🔧 펄스 진동 실패: {e}")
                    
                    # 방법 4: 최후 수단 - 시스템 알림음
                    if not success:
                        try:
                            import winsound
                            frequency = int(400 + (intensity * 400))  # 400~800Hz
                            duration_ms = int(duration * 1000)
                            winsound.Beep(frequency, duration_ms)
                            success = True
                        except Exception as e:
                            print(f"🔧 시스템 알림음 실패: {e}")
                    
                    # 진동 정지 처리
                    if hasattr(self.joystick, 'stop_rumble'):
                        try:
                            self.joystick.stop_rumble()
                        except:
                            pass
                        
                except Exception as e:
                    print(f"🔧 진동 시스템 전체 실패: {e}")
                
                return success
            
            # 백그라운드에서 진동 실행
            thread = threading.Thread(target=vibrate_thread, daemon=True)
            thread.start()
            
        except Exception:
            # 진동 기능 실패는 조용히 처리
            pass
    
    def vibrate_light(self):
        """가벼운 진동 (메뉴 선택, 아이템 획득 등)"""
        self.vibrate(duration=0.08, intensity=0.4)  # 더 길고 강하게
    
    def vibrate_medium(self):
        """중간 진동 (공격 성공, 레벨업 등)"""
        self.vibrate(duration=0.2, intensity=0.7)   # 더 길고 강하게
    
    def vibrate_heavy(self):
        """강한 진동 (피격, 크리티컬 등)"""
        self.vibrate(duration=0.3, intensity=1.0)   # 더 길게
    
    def vibrate_pattern_encounter(self):
        """인카운터 진동 패턴 (강화된 패턴)"""
        if not self.vibration_enabled:
            return
        
        import threading
        import time
        
        def pattern():
            try:
                # 더 강력한 인카운터 패턴
                for i in range(3):
                    self.vibrate(duration=0.15, intensity=0.8)
                    time.sleep(0.2)
                # 마지막에 긴 진동
                time.sleep(0.1)
                self.vibrate(duration=0.25, intensity=1.0)
            except Exception:
                pass
        
        thread = threading.Thread(target=pattern, daemon=True)
        thread.start()
    
    def vibrate_pattern_victory(self):
        """승리 진동 패턴 (강화된 패턴)"""
        if not self.vibration_enabled:
            return
        
        import threading
        import time
        
        def pattern():
            try:
                # 더 화려한 승리 패턴
                # 첫 번째: 긴 강한 진동
                self.vibrate(duration=0.4, intensity=1.0)
                time.sleep(0.5)
                # 두 번째: 중간 진동 3번
                for i in range(3):
                    self.vibrate(duration=0.12, intensity=0.6)
                    time.sleep(0.15)
                # 마지막: 피날레 진동
                time.sleep(0.2)
                self.vibrate(duration=0.5, intensity=1.0)
            except Exception:
                pass
        
        thread = threading.Thread(target=pattern, daemon=True)
        thread.start()
    
    def test_vibration_methods(self):
        """진동 방법들 테스트 (디버그용)"""
        if not self.is_available():
            print("❌ 게임패드가 연결되지 않음")
            return
        
        import time
        print("🔧 진동 방법 테스트 시작...")
        
        # 방법 1: 기본 rumble
        try:
            if hasattr(self.joystick, 'rumble'):
                result = self.joystick.rumble(1.0, 1.0, 500)
                print(f"방법 1 (기본 rumble): {'성공' if result else '실패'}")
                time.sleep(0.6)
        except Exception as e:
            print(f"방법 1 실패: {e}")
        
        # 방법 2: 여러 번 짧은 진동
        try:
            for i in range(5):
                if hasattr(self.joystick, 'rumble'):
                    self.joystick.rumble(0.8, 0.8, 100)
                time.sleep(0.15)
            print("방법 2 (펄스 진동): 완료")
        except Exception as e:
            print(f"방법 2 실패: {e}")
        
        # 방법 3: Windows XInput 직접 호출
        try:
            import ctypes
            if hasattr(ctypes, 'windll'):
                xinput = ctypes.windll.xinput1_4
                vibration = ctypes.c_uint32(32767)  # 50% 강도
                xinput.XInputSetState(0, ctypes.byref(vibration))
                time.sleep(0.3)
                xinput.XInputSetState(0, ctypes.byref(ctypes.c_uint32(0)))
                print("방법 3 (XInput 직접): 성공")
        except Exception as e:
            print(f"방법 3 실패: {e}")
        
        print("🔧 진동 테스트 완료!")
    
    def get_input(self) -> str:
        """게임패드 입력을 키보드 입력으로 변환"""
        if not self.is_available():
            return ''
        
        try:
            import pygame
            import time
            
            # 이벤트 처리 (다른 프로그램 간섭 방지)
            pygame.event.pump()
            
            # 불필요한 이벤트 제거 (키보드, 마우스 등)
            for event in pygame.event.get():
                if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, 
                                pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                    # 게임과 관련없는 이벤트는 무시
                    pass
            
            current_time = time.time()
            
            # D-패드 (방향키) - 새로운 함수 사용
            hat = self.joystick.get_hat(0) if self.joystick.get_numhats() > 0 else (0, 0)
            dpad_input = self._get_dpad_input(hat, current_time)
            if dpad_input:
                return dpad_input
            
            # 아날로그 스틱 (축 입력)
            if self.joystick.get_numaxes() >= 2:
                x_axis = self.joystick.get_axis(0)
                y_axis = self.joystick.get_axis(1)
                threshold = 0.5
                
                if y_axis < -threshold and self._check_cooldown('stick_up', current_time):
                    return 'w'
                elif y_axis > threshold and self._check_cooldown('stick_down', current_time):
                    return 's'
                elif x_axis < -threshold and self._check_cooldown('stick_left', current_time):
                    return 'a'
                elif x_axis > threshold and self._check_cooldown('stick_right', current_time):
                    return 'd'
            
            # 버튼 입력
            for i in range(self.joystick.get_numbuttons()):
                if self.joystick.get_button(i) and self._check_cooldown(f'button_{i}', current_time):
                    return self._map_button_to_key(i)
            
            return ''
        except Exception as e:
            return ''
    
    def _check_cooldown(self, input_id: str, current_time: float) -> bool:
        """키보드 스타일 반복 입력 체크"""
        # 현재 버튼이 눌려있는지 확인
        button_pressed = False
        
        if input_id.startswith('button_'):
            button_num = int(input_id.split('_')[1])
            button_pressed = self.joystick.get_button(button_num)
        elif input_id in ['up', 'down', 'left', 'right']:
            hat = self.joystick.get_hat(0) if self.joystick.get_numhats() > 0 else (0, 0)
            if input_id == 'up':
                button_pressed = hat[1] == 1
            elif input_id == 'down':
                button_pressed = hat[1] == -1
            elif input_id == 'left':
                button_pressed = hat[0] == -1
            elif input_id == 'right':
                button_pressed = hat[0] == 1
        elif input_id.startswith('stick_'):
            if self.joystick.get_numaxes() >= 2:
                x_axis = self.joystick.get_axis(0)
                y_axis = self.joystick.get_axis(1)
                threshold = 0.5
                
                if input_id == 'stick_up':
                    button_pressed = y_axis < -threshold
                elif input_id == 'stick_down':
                    button_pressed = y_axis > threshold
                elif input_id == 'stick_left':
                    button_pressed = x_axis < -threshold
                elif input_id == 'stick_right':
                    button_pressed = x_axis > threshold
        
        # 버튼이 눌려있지 않으면 상태 초기화
        if not button_pressed:
            if input_id in self.button_press_time:
                del self.button_press_time[input_id]
            if input_id in self.button_last_repeat:
                del self.button_last_repeat[input_id]
            return False
        
        # 처음 눌린 경우
        if input_id not in self.button_press_time:
            self.button_press_time[input_id] = current_time
            self.button_last_repeat[input_id] = current_time
            return True  # 즉시 입력
        
        # 눌린 지 경과한 시간
        time_since_press = current_time - self.button_press_time[input_id]
        time_since_last_repeat = current_time - self.button_last_repeat[input_id]
        
        # 초기 지연 시간이 지났고, 반복 간격도 지났으면 반복 입력
        if time_since_press >= self.initial_delay and time_since_last_repeat >= self.repeat_delay:
            self.button_last_repeat[input_id] = current_time
            return True
        
        return False
    
    def _map_button_to_key(self, button_id: int) -> str:
        """버튼을 키보드 키로 매핑 - 단순화된 매핑"""
        # Xbox 컨트롤러 기준 매핑
        button_map = {
            # 메인 버튼 (A/B/X/Y)
            0: '\n',       # A 버튼 - 확인 (Enter)
            1: 'q',        # B 버튼 - 취소 (Q)
            2: '\x1b',     # X 버튼 - ESC (메뉴/뒤로가기)
            3: 'i',        # Y 버튼 - 인벤토리 (I)
            
            # 어깨 버튼 (LB/RB) - 나중에 조합키용으로 사용 예정
            4: '',         # LB - 사용 안함 (조합키용 예약)
            5: '',         # RB - 사용 안함 (조합키용 예약)
            
            # 뒤쪽 버튼 (View/Menu)
            6: '',         # View - 사용 안함
            7: 'b',        # Menu/Start - 저장 (B)
            
            # 스틱 버튼은 사용 안함
            8: '',         # 왼쪽 스틱 버튼 - 사용 안함
            9: '',         # 오른쪽 스틱 버튼 - 사용 안함
        }
        return button_map.get(button_id, '')
    
    def _get_dpad_input(self, hat, current_time) -> str:
        """D-Pad 입력 처리 - 단순한 버튼 매핑"""
        # 십자키를 버튼으로 사용 (이동은 아날로그 스틱으로)
        if hat[1] == 1 and self._check_cooldown('up', current_time):  # 위
            return 'm'  # AI 모드
        elif hat[1] == -1 and self._check_cooldown('down', current_time):  # 아래
            return 'f'  # 필드 (중요한 기능!)
        elif hat[0] == -1 and self._check_cooldown('left', current_time):  # 왼쪽
            return 'h'  # 도움말
        elif hat[0] == 1 and self._check_cooldown('right', current_time):  # 오른쪽
            return 'p'  # 파티 정보
        
        return ''


class UnifiedInputManager:
    """키보드와 게임패드를 통합한 입력 관리자"""
    
    def __init__(self, enable_gamepad=True):
        self.keyboard = KeyboardInput()
        self.enable_gamepad = enable_gamepad
        
        # 환경 변수로 게임패드 강제 비활성화 옵션
        disable_gamepad = os.getenv('DISABLE_GAMEPAD') == '1'
        mobile_mode = os.getenv('MOBILE_MODE') == '1'
        web_mode = os.getenv('WEB_MODE') == '1'
        subprocess_mode = os.getenv('SUBPROCESS_MODE') == '1'
        
        # 터미널 환경 감지 - 터미널에서는 게임패드 비활성화
        terminal_mode = self._is_running_in_terminal()
        
        # 게임패드 비활성화 조건들
        if disable_gamepad or mobile_mode or web_mode or subprocess_mode or terminal_mode:
            self.gamepad = None
            self.gamepad_enabled = False
            print("🎮 터미널 환경: 게임패드 비활성화됨")
        else:
            try:
                # 콘솔 독점 모드로 게임패드 초기화
                os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '0'  # 백그라운드 이벤트 차단
                self.gamepad = GamepadInput()
                self.gamepad_enabled = True and enable_gamepad
                if self.gamepad_enabled and self.gamepad.is_available():
                    print("🎮 게임패드 연결됨 - 게임 전용 모드")
                else:
                    print("🎮 게임패드 없음 - 키보드 모드")
            except Exception as e:
                self.gamepad = None
                self.gamepad_enabled = False
                print(f"🎮 게임패드 초기화 실패: {e}")
                
        # 진동 매니저는 나중에 초기화
        self.vibration_manager = None
        
    def _is_running_in_terminal(self) -> bool:
        """터미널에서 실행 중인지 감지"""
        try:
            # 환경 변수로 터미널 감지
            terminal_vars = [
                'TERM', 'WT_SESSION', 'SHELL', 'PROMPT',
                'VSCODE_INJECTION', 'TERMINAL_EMULATOR'
            ]
            
            for var in terminal_vars:
                if os.getenv(var):
                    return True
            
            # stdout이 터미널인지 확인
            if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
                return True
            
            # 프로세스 이름 간단 체크
            try:
                import sys
                if 'python.exe' in sys.executable and sys.stdin.isatty():
                    return True
            except:
                pass
                
            return False
        except:
            # 감지 실패시 안전하게 터미널 모드로 간주
            return True
    
    def get_input(self) -> str:
        """키보드 또는 게임패드 입력 받기 - 논블로킹 모드"""
        import time
        
        # 게임패드 입력 우선 체크 (활성화된 경우에만)
        if self.enable_gamepad and self.gamepad and self.gamepad.is_available():
            gamepad_input = self.gamepad.get_input()
            if gamepad_input:
                return gamepad_input
        
        # 키보드 논블로킹 입력 체크 (Windows만 지원)
        if os.name == 'nt':
            try:
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if isinstance(key, bytes):
                        key = key.decode('utf-8', errors='ignore')
                    return key.lower()
            except:
                pass
        
        return ''  # 입력 없음
    
    def wait_for_input_with_repeat(self, message: str = "입력 대기 중...", timeout: float = None) -> str:
        """키 반복을 지원하는 입력 대기"""
        import time
        
        if message:
            print(message)
        
        start_time = time.time()
        
        while True:
            # 타임아웃 체크
            if timeout and (time.time() - start_time) > timeout:
                return ''
            
            # 입력 체크
            key = self.get_input()
            if key:
                return key
            
            # 짧은 딜레이 (CPU 사용량 감소)
            time.sleep(0.05)  # 50ms 딜레이
    
    def get_key(self) -> str:
        """키 입력 받기 - KeyboardInput과 호환"""
        return self.get_input()
    
    # ===== 진동 기능 래퍼 메서드들 =====
    def set_vibration_enabled(self, enabled: bool):
        """진동 활성화/비활성화"""
        if self.gamepad:
            self.gamepad.set_vibration_enabled(enabled)
    
    def set_vibration_strength(self, strength: float):
        """진동 강도 설정 (0.0~1.0)"""
        if self.gamepad:
            self.gamepad.set_vibration_strength(strength)
    
    def vibrate_light(self):
        """가벼운 진동 (메뉴 선택, 아이템 획득 등)"""
        if self.gamepad:
            self.gamepad.vibrate_light()
    
    def vibrate_medium(self):
        """중간 진동 (공격 성공, 레벨업 등)"""
        if self.gamepad:
            self.gamepad.vibrate_medium()
    
    def vibrate_heavy(self):
        """강한 진동 (피격, 크리티컬 등)"""
        if self.gamepad:
            self.gamepad.vibrate_heavy()
    
    def vibrate_encounter(self):
        """인카운터 진동 패턴"""
        if self.gamepad:
            self.gamepad.vibrate_pattern_encounter()
    
    def vibrate_victory(self):
        """승리 진동 패턴"""
        if self.gamepad:
            self.gamepad.vibrate_pattern_victory()
    
    def test_vibration_methods(self):
        """진동 방법들 테스트 (디버그용)"""
        if self.gamepad:
            self.gamepad.test_vibration_methods()
        else:
            print("❌ 게임패드가 활성화되지 않음")
    
    def wait_for_key(self, message: str = "아무 키나 누르세요...") -> str:
        """메시지와 함께 키 대기 - KeyboardInput과 호환"""
        return self.keyboard.wait_for_key(message)
    
    def clear_input_buffer(self):
        """입력 버퍼 클리어 - KeyboardInput과 호환"""
        return self.keyboard.clear_input_buffer()
    
    def get_string_input(self, prompt: str = "") -> str:
        """문자열 입력 받기 - KeyboardInput과 호환"""
        return self.keyboard.get_string_input(prompt)
    
    def wait_for_input(self, message: str = "입력을 기다리는 중...") -> str:
        """메시지와 함께 입력 대기"""
        if message:
            print(message)
        
        while True:
            # 게임패드 입력 체크 (논블로킹, 활성화된 경우에만)
            if self.enable_gamepad and self.gamepad and self.gamepad.is_available():
                gamepad_input = self.gamepad.get_input()
                if gamepad_input:
                    return gamepad_input
            
            # 키보드 입력 체크 (짧은 타임아웃)
            try:
                import select
                import sys
                
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    return self.keyboard.get_key()
            except:
                # 폴백: 키보드만 사용
                return self.keyboard.get_key()
            
            # 짧은 딜레이 (CPU 사용량 감소)
            import time
            time.sleep(0.05)


class VibrationManager:
    """진동 관리 클래스"""
    
    def __init__(self):
        self.enabled = True
    
    def vibrate_light(self):
        """가벼운 진동"""
        pass
    
    def vibrate_medium(self):
        """중간 진동"""
        pass
    
    def vibrate_heavy(self):
        """강한 진동"""
        pass
