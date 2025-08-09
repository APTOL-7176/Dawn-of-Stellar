#!/usr/bin/env python3
"""
색상 및 텍스트 장식 시스템
"""

from enum import Enum
import os
import sys


# Windows에서 ANSI 색상 지원 활성화 - PowerShell 호환성 개선
if os.name == 'nt':
    try:
        import ctypes
        from ctypes import wintypes
        
        # GetStdHandle과 SetConsoleMode 정의
        STD_OUTPUT_HANDLE = -11
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        
        # 현재 콘솔 모드 가져오기
        mode = wintypes.DWORD()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        
        # Virtual Terminal Processing 활성화
        new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(handle, new_mode)
        
        # PowerShell 환경 감지 및 강제 색상 활성화
        if 'PSModulePath' in os.environ:
            os.environ['FORCE_COLOR'] = '1'
            
    except Exception as e:
        # 폴백: 기본 설정 사용
        pass
    
    # Windows Terminal, ConEmu, PowerShell 감지
    if any(env in os.environ for env in ['WT_SESSION', 'ConEmuANSI', 'PSModulePath']):
        os.environ['FORCE_COLOR'] = '1'


class Color(Enum):
    """색상 코드"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # 기본 색상
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 밝은 색상
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 배경색
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class ColorText:
    """색상 텍스트 관리 클래스"""
    
    @staticmethod
    def is_color_supported() -> bool:
        """색상 지원 여부 확인 - PowerShell 호환성 개선"""
        # 강제 색상 모드가 설정된 경우
        if os.environ.get('FORCE_COLOR') == '1':
            return True
            
        # PowerShell 환경 감지
        if 'PSModulePath' in os.environ:
            return True
            
        # Windows Terminal, ConEmu, ANSICON 등
        if any(env in os.environ for env in ['WT_SESSION', 'ConEmuANSI', 'ANSICON']):
            return True
            
        # Unix/Linux 시스템
        if os.name != 'nt':
            return True
            
        # Windows 시스템에서도 기본적으로 색상 지원 시도
        return True
    
    @staticmethod
    def colorize(text: str, color: Color, bold: bool = False) -> str:
        """텍스트에 색상 적용"""
        if not ColorText.is_color_supported():
            return text
        
        prefix = color.value
        if bold:
            prefix = Color.BOLD.value + prefix
        
        return f"{prefix}{text}{Color.RESET.value}"
    
    @staticmethod
    def rarity_color(rarity: str) -> Color:
        """희귀도별 색상 반환"""
        rarity_colors = {
            "일반": Color.WHITE,
            "고급": Color.GREEN,
            "희귀": Color.BLUE,
            "영웅": Color.MAGENTA,
            "전설": Color.YELLOW
        }
        return rarity_colors.get(rarity, Color.WHITE)
    
    @staticmethod
    def hp_color(current_hp: int, max_hp: int) -> Color:
        """HP 비율에 따른 색상"""
        ratio = current_hp / max_hp if max_hp > 0 else 0
        if ratio > 0.7:
            return Color.GREEN
        elif ratio > 0.3:
            return Color.YELLOW
        else:
            return Color.RED
    
    @staticmethod
    def damage_color(damage: int) -> Color:
        """피해량에 따른 색상"""
        if damage > 100:
            return Color.BRIGHT_RED
        elif damage > 50:
            return Color.RED
        else:
            return Color.YELLOW
    
    @staticmethod
    def heal_color() -> Color:
        """치유 색상"""
        return Color.BRIGHT_GREEN
    
    @staticmethod
    def exp_color() -> Color:
        """경험치 색상"""
        return Color.CYAN
    
    @staticmethod
    def gold_color() -> Color:
        """골드 색상"""
        return Color.YELLOW


# 편의 함수들
def colored(text: str, color: Color, bold: bool = False) -> str:
    """색상 적용 편의 함수"""
    return ColorText.colorize(text, color, bold)

def red(text: str, bold: bool = False) -> str:
    return colored(text, Color.RED, bold)

def green(text: str, bold: bool = False) -> str:
    return colored(text, Color.GREEN, bold)

def blue(text: str, bold: bool = False) -> str:
    return colored(text, Color.BLUE, bold)

def yellow(text: str, bold: bool = False) -> str:
    return colored(text, Color.YELLOW, bold)

def magenta(text: str, bold: bool = False) -> str:
    return colored(text, Color.MAGENTA, bold)

def cyan(text: str, bold: bool = False) -> str:
    return colored(text, Color.CYAN, bold)

def bright_white(text: str, bold: bool = False) -> str:
    return colored(text, Color.BRIGHT_WHITE, bold)

def bright_red(text: str, bold: bool = False) -> str:
    return colored(text, Color.BRIGHT_RED, bold)

def bright_green(text: str, bold: bool = False) -> str:
    return colored(text, Color.BRIGHT_GREEN, bold)

def bright_yellow(text: str, bold: bool = False) -> str:
    return colored(text, Color.BRIGHT_YELLOW, bold)

def bright_cyan(text: str, bold: bool = False) -> str:
    return colored(text, Color.BRIGHT_CYAN, bold)

def bright_blue(text: str, bold: bool = False) -> str:
    return colored(text, Color.BRIGHT_BLUE, bold)

def dim(text: str) -> str:
    """어두운 (dim) 텍스트"""
    if not ColorText.is_color_supported():
        return text
    return f"{Color.DIM.value}{text}{Color.RESET.value}"

def bright_magenta(text: str, bold: bool = False) -> str:
    return colored(text, Color.BRIGHT_MAGENTA, bold)

def white(text: str, bold: bool = False) -> str:
    return colored(text, Color.WHITE, bold)

def bright_black(text: str, bold: bool = False) -> str:
    return colored(text, Color.BRIGHT_BLACK, bold)

def rarity_colored(text: str, rarity: str) -> str:
    """희귀도별 색상 적용"""
    color = ColorText.rarity_color(rarity)
    return colored(text, color, True)

def hp_colored(text: str, current_hp: int, max_hp: int) -> str:
    """HP 비율별 색상 적용"""
    color = ColorText.hp_color(current_hp, max_hp)
    return colored(text, color)

def damage_colored(text: str, damage: int) -> str:
    """피해량별 색상 적용"""
    color = ColorText.damage_color(damage)
    return colored(text, color, True)

def get_display_length(text: str) -> int:
    """ANSI 색상 코드를 제외한 실제 표시 길이 계산"""
    import re
    # ANSI 색상 코드 제거
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    clean_text = ansi_escape.sub('', text)
    return len(clean_text)

# 직접 접근 가능한 색상 상수들
BLACK = Color.BLACK.value
RED = Color.RED.value
GREEN = Color.GREEN.value
YELLOW = Color.YELLOW.value
BLUE = Color.BLUE.value
MAGENTA = Color.MAGENTA.value
CYAN = Color.CYAN.value
WHITE = Color.WHITE.value
BRIGHT_BLACK = Color.BRIGHT_BLACK.value
BRIGHT_RED = Color.BRIGHT_RED.value
BRIGHT_GREEN = Color.BRIGHT_GREEN.value
BRIGHT_YELLOW = Color.BRIGHT_YELLOW.value
BRIGHT_BLUE = Color.BRIGHT_BLUE.value
BRIGHT_MAGENTA = Color.BRIGHT_MAGENTA.value
BRIGHT_CYAN = Color.BRIGHT_CYAN.value
BRIGHT_WHITE = Color.BRIGHT_WHITE.value
RESET = Color.RESET.value
BOLD = Color.BOLD.value
DIM = Color.DIM.value
UNDERLINE = Color.UNDERLINE.value

# 배경색 상수들
BG_BLACK = Color.BG_BLACK.value
BG_RED = Color.BG_RED.value
BG_GREEN = Color.BG_GREEN.value
BG_YELLOW = Color.BG_YELLOW.value
BG_BLUE = Color.BG_BLUE.value
BG_MAGENTA = Color.BG_MAGENTA.value
BG_CYAN = Color.BG_CYAN.value
BG_WHITE = Color.BG_WHITE.value
