#!/usr/bin/env python3
"""
입력 유틸리티 - 키보드 입력을 바로 받기 위한 모듈
"""

import sys
import os

class KeyboardInput:
    """키보드 입력을 바로 받는 클래스"""
    
    def __init__(self, sound_manager=None):
        self.getch_func = self._get_getch_function()
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
            def _fallback_input():
                return input().lower().strip()[:1]
            return _fallback_input
    
    def get_key(self) -> str:
        """키 입력 받기"""
        try:
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
            result = input("명령: ").lower().strip()[:1]
            
            # 키 입력 효과음 비활성화 (중복 방지 - cursor_menu_system에서 처리)
            # if self.sound_manager:
            #     self.sound_manager.play_sfx("menu_select")
                
            return result
    
    def wait_for_key(self, message: str = "아무 키나 누르세요...") -> str:
        """메시지와 함께 키 대기"""
        print(message, end='', flush=True)
        
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
