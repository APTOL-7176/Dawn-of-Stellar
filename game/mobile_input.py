#!/usr/bin/env python3
"""
모바일 입력 시스템 - 터치, 제스처, 가상 컨트롤러 지원
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Optional, Dict, List
import time
import math

class InputType(Enum):
    """입력 타입"""
    KEYBOARD = "keyboard"
    TOUCH = "touch"
    GAMEPAD = "gamepad"
    GESTURE = "gesture"

class TouchEvent:
    """터치 이벤트 데이터"""
    def __init__(self, x: float, y: float, touch_type: str = "down"):
        self.x = x
        self.y = y
        self.touch_type = touch_type  # down, move, up
        self.timestamp = time.time()

class GestureType(Enum):
    """제스처 타입"""
    TAP = "tap"
    LONG_TAP = "long_tap"
    DOUBLE_TAP = "double_tap"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    PINCH_IN = "pinch_in"
    PINCH_OUT = "pinch_out"

class VirtualButton:
    """가상 버튼"""
    def __init__(self, x: float, y: float, width: float, height: float, 
                 command: str, label: str = ""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.command = command
        self.label = label
        self.is_pressed = False
        self.last_press_time = 0
    
    def contains_point(self, x: float, y: float) -> bool:
        """점이 버튼 영역 내에 있는지 확인"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def press(self):
        """버튼 누르기"""
        self.is_pressed = True
        self.last_press_time = time.time()
    
    def release(self):
        """버튼 떼기"""
        self.is_pressed = False

class TouchZone:
    """터치 영역 정의"""
    def __init__(self, name: str, x: float, y: float, width: float, height: float):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def contains_point(self, x: float, y: float) -> bool:
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)

class GestureRecognizer:
    """제스처 인식기"""
    
    def __init__(self):
        self.swipe_threshold = 50  # 최소 스와이프 거리
        self.tap_timeout = 0.3     # 탭 타임아웃
        self.long_tap_timeout = 1.0  # 롱탭 타임아웃
        self.double_tap_timeout = 0.5  # 더블탭 타임아웃
        
        self.touch_start_pos = None
        self.touch_start_time = None
        self.last_tap_time = 0
        self.last_tap_pos = None
    
    def process_touch_down(self, x: float, y: float) -> Optional[GestureType]:
        """터치 시작 처리"""
        self.touch_start_pos = (x, y)
        self.touch_start_time = time.time()
        
        # 더블탭 체크
        if (self.last_tap_pos and 
            time.time() - self.last_tap_time < self.double_tap_timeout and
            self._distance(self.last_tap_pos, (x, y)) < 30):
            return GestureType.DOUBLE_TAP
        
        return None
    
    def process_touch_up(self, x: float, y: float) -> Optional[GestureType]:
        """터치 종료 처리"""
        if not self.touch_start_pos or not self.touch_start_time:
            return None
        
        duration = time.time() - self.touch_start_time
        distance = self._distance(self.touch_start_pos, (x, y))
        
        # 롱탭 체크
        if duration > self.long_tap_timeout and distance < 20:
            return GestureType.LONG_TAP
        
        # 스와이프 체크
        if distance > self.swipe_threshold:
            dx = x - self.touch_start_pos[0]
            dy = y - self.touch_start_pos[1]
            
            if abs(dx) > abs(dy):
                return GestureType.SWIPE_RIGHT if dx > 0 else GestureType.SWIPE_LEFT
            else:
                return GestureType.SWIPE_UP if dy > 0 else GestureType.SWIPE_DOWN
        
        # 일반 탭
        if duration < self.tap_timeout and distance < 20:
            self.last_tap_time = time.time()
            self.last_tap_pos = (x, y)
            return GestureType.TAP
        
        return None
    
    def _distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """두 점 사이의 거리 계산"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

class MobileInputManager:
    """모바일 입력 관리자"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gesture_recognizer = GestureRecognizer()
        self.virtual_buttons: List[VirtualButton] = []
        self.touch_zones: Dict[str, TouchZone] = {}
        self.setup_default_layout()
        
        # 현재 입력 상태
        self.current_command = None
        self.active_touches: Dict[int, TouchEvent] = {}
        
    def setup_default_layout(self):
        """기본 모바일 레이아웃 설정"""
        button_size = 80
        margin = 20
        
        # 방향키 (왼쪽 하단)
        dpad_x = margin
        dpad_y = self.screen_height - button_size * 3 - margin * 2
        
        self.virtual_buttons.extend([
            VirtualButton(dpad_x + button_size, dpad_y, button_size, button_size, "w", "↑"),
            VirtualButton(dpad_x, dpad_y + button_size, button_size, button_size, "a", "←"),
            VirtualButton(dpad_x + button_size * 2, dpad_y + button_size, button_size, button_size, "d", "→"),
            VirtualButton(dpad_x + button_size, dpad_y + button_size * 2, button_size, button_size, "s", "↓"),
        ])
        
        # 액션 버튼 (오른쪽 하단)
        action_x = self.screen_width - button_size * 2 - margin * 2
        action_y = self.screen_height - button_size * 2 - margin
        
        self.virtual_buttons.extend([
            VirtualButton(action_x, action_y, button_size, button_size, "enter", "확인"),
            VirtualButton(action_x + button_size + margin, action_y, button_size, button_size, "q", "취소"),
            VirtualButton(action_x, action_y + button_size + margin, button_size, button_size, "i", "인벤"),
            VirtualButton(action_x + button_size + margin, action_y + button_size + margin, button_size, button_size, "p", "파티"),
        ])
        
        # 터치 영역 설정
        self.touch_zones = {
            'movement': TouchZone('movement', 0, self.screen_height - 200, 250, 200),
            'action': TouchZone('action', self.screen_width - 250, self.screen_height - 200, 250, 200),
            'game_area': TouchZone('game_area', 250, 50, self.screen_width - 500, self.screen_height - 250),
            'menu_bar': TouchZone('menu_bar', 0, 0, self.screen_width, 50)
        }
    
    def process_touch_event(self, touch_id: int, x: float, y: float, touch_type: str) -> Optional[str]:
        """터치 이벤트 처리"""
        touch_event = TouchEvent(x, y, touch_type)
        
        if touch_type == "down":
            self.active_touches[touch_id] = touch_event
            return self._handle_touch_down(x, y)
        elif touch_type == "up":
            if touch_id in self.active_touches:
                del self.active_touches[touch_id]
            return self._handle_touch_up(x, y)
        elif touch_type == "move":
            if touch_id in self.active_touches:
                self.active_touches[touch_id] = touch_event
            return self._handle_touch_move(x, y)
        
        return None
    
    def _handle_touch_down(self, x: float, y: float) -> Optional[str]:
        """터치 다운 처리"""
        # 가상 버튼 체크
        for button in self.virtual_buttons:
            if button.contains_point(x, y):
                button.press()
                return button.command
        
        # 제스처 시작
        self.gesture_recognizer.process_touch_down(x, y)
        return None
    
    def _handle_touch_up(self, x: float, y: float) -> Optional[str]:
        """터치 업 처리"""
        # 가상 버튼 릴리즈
        for button in self.virtual_buttons:
            if button.is_pressed:
                button.release()
        
        # 제스처 인식
        gesture = self.gesture_recognizer.process_touch_up(x, y)
        return self._gesture_to_command(gesture)
    
    def _handle_touch_move(self, x: float, y: float) -> Optional[str]:
        """터치 이동 처리"""
        # 드래그 기반 이동 (추후 구현)
        return None
    
    def _gesture_to_command(self, gesture: Optional[GestureType]) -> Optional[str]:
        """제스처를 게임 명령으로 변환"""
        if not gesture:
            return None
        
        gesture_commands = {
            GestureType.TAP: "enter",
            GestureType.DOUBLE_TAP: "f",  # 필드 활동
            GestureType.LONG_TAP: "p",    # 파티 상태
            GestureType.SWIPE_UP: "w",
            GestureType.SWIPE_DOWN: "s",
            GestureType.SWIPE_LEFT: "a",
            GestureType.SWIPE_RIGHT: "d",
        }
        
        return gesture_commands.get(gesture)
    
    def get_virtual_buttons_for_rendering(self) -> List[VirtualButton]:
        """렌더링용 가상 버튼 리스트 반환"""
        return self.virtual_buttons
    
    def get_touch_zones_for_rendering(self) -> Dict[str, TouchZone]:
        """렌더링용 터치 영역 반환"""
        return self.touch_zones
    
    def enable_haptic_feedback(self, enabled: bool = True):
        """햅틱 피드백 활성화/비활성화"""
        # 실제 구현은 플랫폼별로 다름
        pass
    
    def set_screen_size(self, width: int, height: int):
        """화면 크기 변경 시 레이아웃 재조정"""
        self.screen_width = width
        self.screen_height = height
        self.virtual_buttons.clear()
        self.setup_default_layout()

# 모바일 입력 관리자 싱글톤
_mobile_input_manager = None

def get_mobile_input_manager() -> MobileInputManager:
    """모바일 입력 관리자 반환"""
    global _mobile_input_manager
    if _mobile_input_manager is None:
        _mobile_input_manager = MobileInputManager()
    return _mobile_input_manager

def convert_touch_to_keyboard_input(x: float, y: float, touch_type: str = "down") -> Optional[str]:
    """터치 입력을 키보드 입력으로 변환 (기존 시스템과 호환)"""
    manager = get_mobile_input_manager()
    return manager.process_touch_event(0, x, y, touch_type)

# 기존 KeyboardInput 클래스와 호환성을 위한 래퍼
class MobileCompatibleInput:
    """모바일 호환 입력 클래스"""
    
    def __init__(self):
        self.mobile_manager = get_mobile_input_manager()
        self.last_command = None
        self.waiting_for_input = False
    
    def get_key(self) -> str:
        """키 입력 받기 (모바일 터치 포함)"""
        # 모바일에서는 터치 이벤트를 대기
        # 실제 구현은 UI 프레임워크와 연동 필요
        self.waiting_for_input = True
        
        # 임시: 'enter' 반환 (실제로는 터치 이벤트 대기)
        return 'enter'
    
    def wait_for_key(self, message: str = "터치하세요...") -> str:
        """터치 대기"""
        print(f"📱 {message}")
        return self.get_key()
    
    def clear_input_buffer(self):
        """입력 버퍼 클리어"""
        pass

if __name__ == "__main__":
    # 테스트 코드
    manager = MobileInputManager(800, 600)
    
    # 터치 시뮬레이션
    print("=== 모바일 입력 시스템 테스트 ===")
    
    # 방향키 터치 테스트
    cmd = manager.process_touch_event(0, 100, 500, "down")  # 위쪽 버튼
    print(f"위쪽 버튼 터치: {cmd}")
    
    # 스와이프 제스처 테스트
    manager.gesture_recognizer.process_touch_down(400, 300)
    gesture = manager.gesture_recognizer.process_touch_up(400, 200)  # 위로 스와이프
    cmd = manager._gesture_to_command(gesture)
    print(f"위로 스와이프: {cmd}")
    
    print("가상 버튼 목록:")
    for i, button in enumerate(manager.virtual_buttons):
        print(f"  {i+1}. {button.label} ({button.command}) - 위치: ({button.x}, {button.y})")
