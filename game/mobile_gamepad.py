#!/usr/bin/env python3
"""
Dawn of Stellar - 게임패드 지원 시스템
터치스크린 및 가상 게임패드 지원
"""

try:
    from kivy.app import App
    from kivy.uix.widget import Widget
    from kivy.uix.button import Button
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.boxlayout import BoxLayout
    from kivy.graphics import Color, Ellipse, Rectangle
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.vector import Vector
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

import threading
from enum import Enum
from typing import Callable, Dict, Optional

class GamepadButton(Enum):
    """게임패드 버튼"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    A = "a"  # 확인
    B = "b"  # 취소
    X = "x"  # 메뉴
    Y = "y"  # 특수
    START = "start"
    SELECT = "select"

class VirtualJoystick(Widget):
    """가상 조이스틱"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stick_size = 50
        self.background_size = 100
        self.stick_pos = [0, 0]
        self.center_pos = [0, 0]
        self.is_pressed = False
        
        # 그래픽 요소들
        self.background = None
        self.stick = None
        
        # 콜백
        self.on_move_callback = None
        
        # 초기화
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        Clock.schedule_once(self.init_graphics, 0)
    
    def init_graphics(self, dt):
        """그래픽 초기화"""
        with self.canvas:
            # 배경 원
            Color(0.3, 0.3, 0.3, 0.8)
            self.background = Ellipse(size=(self.background_size, self.background_size))
            
            # 조이스틱
            Color(0.7, 0.7, 0.7, 0.9)
            self.stick = Ellipse(size=(self.stick_size, self.stick_size))
        
        self.update_graphics()
    
    def update_graphics(self, *args):
        """그래픽 업데이트"""
        if self.background and self.stick:
            # 중심 위치 계산
            self.center_pos = [
                self.x + self.width / 2,
                self.y + self.height / 2
            ]
            
            # 배경 위치
            bg_x = self.center_pos[0] - self.background_size / 2
            bg_y = self.center_pos[1] - self.background_size / 2
            self.background.pos = (bg_x, bg_y)
            
            # 조이스틱 위치
            stick_x = self.center_pos[0] + self.stick_pos[0] - self.stick_size / 2
            stick_y = self.center_pos[1] + self.stick_pos[1] - self.stick_size / 2
            self.stick.pos = (stick_x, stick_y)
    
    def on_touch_down(self, touch):
        """터치 시작"""
        if self.collide_point(*touch.pos):
            self.is_pressed = True
            self.update_stick_position(touch.pos)
            return True
        return False
    
    def on_touch_move(self, touch):
        """터치 이동"""
        if self.is_pressed:
            self.update_stick_position(touch.pos)
            return True
        return False
    
    def on_touch_up(self, touch):
        """터치 종료"""
        if self.is_pressed:
            self.is_pressed = False
            self.stick_pos = [0, 0]
            self.update_graphics()
            
            if self.on_move_callback:
                self.on_move_callback(0, 0)
            return True
        return False
    
    def update_stick_position(self, touch_pos):
        """조이스틱 위치 업데이트"""
        # 터치 위치에서 중심까지의 벡터
        dx = touch_pos[0] - self.center_pos[0]
        dy = touch_pos[1] - self.center_pos[1]
        
        # 거리 제한
        max_distance = self.background_size / 2 - self.stick_size / 2
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > max_distance:
            dx = dx / distance * max_distance
            dy = dy / distance * max_distance
        
        self.stick_pos = [dx, dy]
        self.update_graphics()
        
        # 정규화된 값 (-1 ~ 1)
        normalized_x = dx / max_distance if max_distance > 0 else 0
        normalized_y = dy / max_distance if max_distance > 0 else 0
        
        if self.on_move_callback:
            self.on_move_callback(normalized_x, normalized_y)

class VirtualGamepadLayout(FloatLayout):
    """가상 게임패드 레이아웃"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_callbacks: Dict[GamepadButton, Callable] = {}
        self.joystick_callback: Optional[Callable] = None
        
        self.setup_gamepad()
    
    def setup_gamepad(self):
        """게임패드 설정"""
        # 왼쪽 조이스틱
        self.joystick = VirtualJoystick(
            size_hint=(None, None),
            size=(120, 120),
            pos_hint={'x': 0.05, 'y': 0.15}
        )
        self.joystick.on_move_callback = self.on_joystick_move
        self.add_widget(self.joystick)
        
        # 오른쪽 버튼들 (다이아몬드 배치)
        button_size = (60, 60)
        
        # A 버튼 (하단)
        self.btn_a = Button(
            text='A',
            size_hint=(None, None),
            size=button_size,
            pos_hint={'right': 0.95, 'y': 0.15},
            background_color=(0.2, 0.8, 0.2, 0.9)
        )
        self.btn_a.bind(on_press=lambda x: self.on_button_press(GamepadButton.A))
        self.add_widget(self.btn_a)
        
        # B 버튼 (우측)
        self.btn_b = Button(
            text='B',
            size_hint=(None, None),
            size=button_size,
            pos_hint={'right': 1.05, 'y': 0.25},
            background_color=(0.8, 0.2, 0.2, 0.9)
        )
        self.btn_b.bind(on_press=lambda x: self.on_button_press(GamepadButton.B))
        self.add_widget(self.btn_b)
        
        # X 버튼 (좌측)
        self.btn_x = Button(
            text='X',
            size_hint=(None, None),
            size=button_size,
            pos_hint={'right': 0.85, 'y': 0.25},
            background_color=(0.2, 0.2, 0.8, 0.9)
        )
        self.btn_x.bind(on_press=lambda x: self.on_button_press(GamepadButton.X))
        self.add_widget(self.btn_x)
        
        # Y 버튼 (상단)
        self.btn_y = Button(
            text='Y',
            size_hint=(None, None),
            size=button_size,
            pos_hint={'right': 0.95, 'y': 0.35},
            background_color=(0.8, 0.8, 0.2, 0.9)
        )
        self.btn_y.bind(on_press=lambda x: self.on_button_press(GamepadButton.Y))
        self.add_widget(self.btn_y)
        
        # 십자키 (왼쪽 상단)
        dpad_size = (40, 40)
        
        # 위
        self.btn_up = Button(
            text='↑',
            size_hint=(None, None),
            size=dpad_size,
            pos_hint={'x': 0.1, 'y': 0.7},
            background_color=(0.5, 0.5, 0.5, 0.8)
        )
        self.btn_up.bind(on_press=lambda x: self.on_button_press(GamepadButton.UP))
        self.add_widget(self.btn_up)
        
        # 아래
        self.btn_down = Button(
            text='↓',
            size_hint=(None, None),
            size=dpad_size,
            pos_hint={'x': 0.1, 'y': 0.6},
            background_color=(0.5, 0.5, 0.5, 0.8)
        )
        self.btn_down.bind(on_press=lambda x: self.on_button_press(GamepadButton.DOWN))
        self.add_widget(self.btn_down)
        
        # 왼쪽
        self.btn_left = Button(
            text='←',
            size_hint=(None, None),
            size=dpad_size,
            pos_hint={'x': 0.05, 'y': 0.65},
            background_color=(0.5, 0.5, 0.5, 0.8)
        )
        self.btn_left.bind(on_press=lambda x: self.on_button_press(GamepadButton.LEFT))
        self.add_widget(self.btn_left)
        
        # 오른쪽
        self.btn_right = Button(
            text='→',
            size_hint=(None, None),
            size=dpad_size,
            pos_hint={'x': 0.15, 'y': 0.65},
            background_color=(0.5, 0.5, 0.5, 0.8)
        )
        self.btn_right.bind(on_press=lambda x: self.on_button_press(GamepadButton.RIGHT))
        self.add_widget(self.btn_right)
        
        # START/SELECT 버튼
        small_btn_size = (50, 30)
        
        self.btn_start = Button(
            text='START',
            size_hint=(None, None),
            size=small_btn_size,
            pos_hint={'right': 0.7, 'y': 0.85},
            background_color=(0.3, 0.3, 0.3, 0.8)
        )
        self.btn_start.bind(on_press=lambda x: self.on_button_press(GamepadButton.START))
        self.add_widget(self.btn_start)
        
        self.btn_select = Button(
            text='SELECT',
            size_hint=(None, None),
            size=small_btn_size,
            pos_hint={'x': 0.3, 'y': 0.85},
            background_color=(0.3, 0.3, 0.3, 0.8)
        )
        self.btn_select.bind(on_press=lambda x: self.on_button_press(GamepadButton.SELECT))
        self.add_widget(self.btn_select)
    
    def on_joystick_move(self, x, y):
        """조이스틱 이동 처리"""
        if self.joystick_callback:
            self.joystick_callback(x, y)
    
    def on_button_press(self, button: GamepadButton):
        """버튼 눌림 처리"""
        if button in self.button_callbacks:
            self.button_callbacks[button]()
    
    def set_button_callback(self, button: GamepadButton, callback: Callable):
        """버튼 콜백 설정"""
        self.button_callbacks[button] = callback
    
    def set_joystick_callback(self, callback: Callable):
        """조이스틱 콜백 설정"""
        self.joystick_callback = callback

class MobileGamepadManager:
    """모바일 게임패드 매니저"""
    
    def __init__(self):
        self.gamepad_layout = None
        self.input_queue = []
        self.input_lock = threading.Lock()
        
        # 입력 매핑
        self.key_mapping = {
            GamepadButton.UP: 'w',
            GamepadButton.DOWN: 's', 
            GamepadButton.LEFT: 'a',
            GamepadButton.RIGHT: 'd',
            GamepadButton.A: '\r',  # Enter
            GamepadButton.B: '\x1b',  # Escape
            GamepadButton.X: 'm',   # Menu
            GamepadButton.Y: 'i',   # Inventory
            GamepadButton.START: 'p',  # Pause
            GamepadButton.SELECT: 'h'  # Help
        }
    
    def create_gamepad(self) -> Optional[VirtualGamepadLayout]:
        """게임패드 생성"""
        if not KIVY_AVAILABLE:
            return None
        
        self.gamepad_layout = VirtualGamepadLayout()
        
        # 버튼 콜백 설정
        for button in GamepadButton:
            self.gamepad_layout.set_button_callback(
                button, 
                lambda b=button: self.handle_button_input(b)
            )
        
        # 조이스틱 콜백 설정
        self.gamepad_layout.set_joystick_callback(self.handle_joystick_input)
        
        return self.gamepad_layout
    
    def handle_button_input(self, button: GamepadButton):
        """버튼 입력 처리"""
        with self.input_lock:
            if button in self.key_mapping:
                key = self.key_mapping[button]
                self.input_queue.append(key)
                print(f"🎮 버튼 입력: {button.value} → {repr(key)}")
    
    def handle_joystick_input(self, x: float, y: float):
        """조이스틱 입력 처리"""
        # 임계값 설정
        threshold = 0.5
        
        with self.input_lock:
            if abs(x) > threshold:
                if x > 0:
                    self.input_queue.append('d')  # 오른쪽
                else:
                    self.input_queue.append('a')  # 왼쪽
            
            if abs(y) > threshold:
                if y > 0:
                    self.input_queue.append('w')  # 위
                else:
                    self.input_queue.append('s')  # 아래
    
    def get_input(self) -> Optional[str]:
        """입력 큐에서 입력 가져오기"""
        with self.input_lock:
            if self.input_queue:
                return self.input_queue.pop(0)
        return None
    
    def has_input(self) -> bool:
        """입력이 있는지 확인"""
        with self.input_lock:
            return len(self.input_queue) > 0

# 전역 게임패드 매니저
_gamepad_manager = None

def get_gamepad_manager() -> MobileGamepadManager:
    """게임패드 매니저 인스턴스 반환"""
    global _gamepad_manager
    if _gamepad_manager is None:
        _gamepad_manager = MobileGamepadManager()
    return _gamepad_manager

if __name__ == "__main__":
    # 테스트 앱
    class GamepadTestApp(App):
        def build(self):
            manager = get_gamepad_manager()
            return manager.create_gamepad()
    
    if KIVY_AVAILABLE:
        GamepadTestApp().run()
    else:
        print("❌ Kivy가 설치되지 않아 게임패드 테스트를 실행할 수 없습니다.")
