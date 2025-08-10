"""
버퍼링 기반 디스플레이 시스템
화면 깜빡임을 최소화하고 부드러운 출력을 제공
"""

import os
import sys
from typing import List, Optional
from .color_text import Color  # color_text.Color로 통일


# 안전한 색상 상수 정의
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'DIM': '\033[2m', 
    'UNDERLINE': '\033[4m',
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'BRIGHT_BLACK': '\033[90m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_YELLOW': '\033[93m',
    'BRIGHT_BLUE': '\033[94m',
    'BRIGHT_MAGENTA': '\033[95m',
    'BRIGHT_CYAN': '\033[96m',
    'BRIGHT_WHITE': '\033[97m',
    'BG_BLACK': '\033[40m',
    'BG_RED': '\033[41m',
    'BG_GREEN': '\033[42m',
    'BG_YELLOW': '\033[43m',
    'BG_BLUE': '\033[44m',
    'BG_MAGENTA': '\033[45m',
    'BG_CYAN': '\033[46m',
    'BG_WHITE': '\033[47m'
}

def get_color(color_name):
    """안전한 색상 코드 반환"""
    return COLORS.get(color_name, '')

class BufferedDisplay:
    """버퍼링 기반 화면 출력 시스템"""
    
    def __init__(self, width: int = 80, height: int = 25):
        self.width = width
        self.height = height
        self.buffer = []
        self.previous_buffer = []
        self.cursor_visible = True
        
        # 터미널 설정
        self._setup_terminal()
    
    def _setup_terminal(self):
        """터미널 초기 설정"""
        if os.name == 'nt':  # Windows
            os.system('chcp 65001 > nul')  # UTF-8 인코딩
        
        # 커서 숨기기
        self.hide_cursor()
        
        # 초기 화면 클리어
        self.clear_screen_immediate()
    
    def hide_cursor(self):
        """커서 숨기기"""
        if not self.cursor_visible:
            return
        print('\033[?25l', end='', flush=True)
        self.cursor_visible = False
    
    def show_cursor(self):
        """커서 보이기"""
        if self.cursor_visible:
            return
        print('\033[?25h', end='', flush=True)
        self.cursor_visible = True
    
    def clear_screen_immediate(self):
        """즉시 화면 클리어 (초기화용)"""
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    
    def move_cursor(self, row: int, col: int):
        """커서를 특정 위치로 이동"""
        print(f'\033[{row};{col}H', end='', flush=True)
    
    def clear_buffer(self):
        """버퍼 초기화 및 화면 완전 클리어"""
        self.buffer = []
        self.previous_buffer = []  # 이전 버퍼도 초기화하여 강제 전체 업데이트
        # 실제 화면도 클리어
        self.clear_screen_immediate()
    
    def soft_clear_buffer(self):
        """소프트 버퍼 초기화 (화면은 유지)"""
        self.buffer = []
    
    def add_line(self, text: str):
        """버퍼에 라인 추가"""
        # ANSI 색상 코드가 포함된 텍스트의 실제 길이 계산
        visible_length = self._get_visible_length(text)
        
        # 너무 긴 라인은 자르기
        if visible_length > self.width:
            text = self._truncate_text(text, self.width)
        
        self.buffer.append(text)
    
    def add_lines(self, lines: List[str]):
        """여러 라인을 버퍼에 추가"""
        for line in lines:
            self.add_line(line)
    
    def _get_visible_length(self, text: str) -> int:
        """ANSI 색상 코드를 제외한 실제 텍스트 길이 계산"""
        import re
        # ANSI 이스케이프 시퀀스 제거
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', text)
        return len(clean_text)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """텍스트를 지정된 길이로 자르기 (ANSI 코드 고려)"""
        import re
        
        # ANSI 코드와 일반 텍스트를 분리
        ansi_escape = re.compile(r'(\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]))')
        parts = ansi_escape.split(text)
        
        result = ""
        visible_count = 0
        
        for part in parts:
            if ansi_escape.match(part):
                # ANSI 코드는 그대로 추가
                result += part
            else:
                # 일반 텍스트는 길이 체크하며 추가
                remaining = max_length - visible_count
                if remaining <= 0:
                    break
                
                if len(part) <= remaining:
                    result += part
                    visible_count += len(part)
                else:
                    result += part[:remaining]
                    visible_count += remaining
                    break
        
        return result
    
    def render_optimized(self):
        """최적화된 렌더링 (변경된 부분만 업데이트)"""
        if not self.buffer:
            return
        
        # 버퍼 크기 제한
        display_buffer = self.buffer[:self.height]
        
        # 이전 버퍼와 비교하여 변경된 라인만 업데이트
        if len(self.previous_buffer) == len(display_buffer):
            changes_detected = False
            for i, (current, previous) in enumerate(zip(display_buffer, self.previous_buffer)):
                if current != previous:
                    # 변경된 라인만 업데이트
                    self.move_cursor(i + 1, 1)
                    print(f'\033[K{current}', end='', flush=True)  # 라인 클리어 후 출력
                    changes_detected = True
            
            if not changes_detected:
                return  # 변경사항이 없으면 출력하지 않음
            
            # 화면 번쩍임 방지를 위한 딜레이 완전 제거 (즉시 렌더링)
            # time.sleep(0.01)  # 딜레이 제거로 최대한 부드럽게
        else:
            # 전체 화면 업데이트
            self.move_cursor(1, 1)
            for i, line in enumerate(display_buffer):
                self.move_cursor(i + 1, 1)
                print(f'\033[K{line}', end='', flush=True)
            
            # 남은 라인들 클리어
            for i in range(len(display_buffer), self.height):
                self.move_cursor(i + 1, 1)
                print('\033[K', end='', flush=True)
            
            # 전체 화면 업데이트 후 딜레이 제거 (즉시 완료)
            # time.sleep(0.02)  # 딜레이 제거로 최대한 부드럽게
        
        # 현재 버퍼를 이전 버퍼로 저장
        self.previous_buffer = display_buffer.copy()
    
    def render_immediate(self):
        """즉시 전체 화면 렌더링"""
        if not self.buffer:
            return
        
        # 커서를 맨 위로 이동
        self.move_cursor(1, 1)
        
        # 버퍼 내용 출력
        display_buffer = self.buffer[:self.height]
        
        for i, line in enumerate(display_buffer):
            self.move_cursor(i + 1, 1)
            print(f'\033[K{line}', end='', flush=True)  # 라인 클리어 후 출력
        
        # 남은 라인들 클리어
        for i in range(len(display_buffer), self.height):
            self.move_cursor(i + 1, 1)
            print('\033[K', end='', flush=True)
        
        # 현재 버퍼를 이전 버퍼로 저장
        self.previous_buffer = display_buffer.copy()
    
    def add_separator(self, char: str = "─", length: int = None, color: str = None):
        """구분선 추가"""
        if length is None:
            length = self.width
        
        if color:
            line = f"{color}{char * length}{get_color('RESET')}"
        else:
            line = char * length
        
        self.add_line(line)
    
    def add_header(self, text: str, color: str = Color.BRIGHT_CYAN):
        """헤더 추가"""
        self.add_separator("=", color=color)
        centered_text = text.center(self.width)
        self.add_line(f"{color}{centered_text}{get_color('RESET')}")
        self.add_separator("=", color=color)
    
    def add_empty_line(self):
        """빈 라인 추가"""
        self.add_line("")
    
    def add_centered_text(self, text: str, color: str = None):
        """중앙 정렬 텍스트 추가"""
        visible_length = self._get_visible_length(text)
        padding = (self.width - visible_length) // 2
        centered = " " * padding + text
        
        if color:
            centered = f"{color}{centered}{get_color('RESET')}"
        
        self.add_line(centered)
    
    def cleanup(self):
        """정리 작업"""
        self.show_cursor()
        print(get_color('RESET'), end='', flush=True)
    
    def __del__(self):
        """소멸자"""
        self.cleanup()


# 전역 버퍼링 디스플레이 인스턴스
_buffered_display = None

def get_buffered_display() -> BufferedDisplay:
    """전역 버퍼링 디스플레이 인스턴스 반환"""
    global _buffered_display
    if _buffered_display is None:
        _buffered_display = BufferedDisplay(width=80, height=40)  # 높이를 40으로 증가
    return _buffered_display

def cleanup_display():
    """디스플레이 정리"""
    global _buffered_display
    if _buffered_display:
        _buffered_display.cleanup()
        _buffered_display = None
