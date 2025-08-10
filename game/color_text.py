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
        # 폴백: 색상 비활성화
        os.environ['NO_COLOR'] = '1'
    
    # Windows Terminal, ConEmu, PowerShell 감지
    if any(env in os.environ for env in ['WT_SESSION', 'ConEmuANSI', 'PSModulePath']):
        os.environ['FORCE_COLOR'] = '1'

# 파워셸 환경에서 색상 문제 해결을 위한 전역 플래그
POWERSHELL_DETECTED = 'PSModulePath' in os.environ
# Windows Terminal에서는 PowerShell도 색상 지원 (WT_SESSION 체크)
WINDOWS_TERMINAL = 'WT_SESSION' in os.environ
COLOR_DISABLED = os.environ.get('NO_COLOR') == '1' or (POWERSHELL_DETECTED and not WINDOWS_TERMINAL)


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


# COLORS 딕셔너리 - Color enum을 안전하게 사용하기 위한 매핑
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'DIM': '\033[2m',
    'UNDERLINE': '\033[4m',
    
    # 기본 색상
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    
    # 밝은 색상
    'BRIGHT_BLACK': '\033[90m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_YELLOW': '\033[93m',
    'BRIGHT_BLUE': '\033[94m',
    'BRIGHT_MAGENTA': '\033[95m',
    'BRIGHT_CYAN': '\033[96m',
    'BRIGHT_WHITE': '\033[97m',
    
    # 배경색
    'BG_BLACK': '\033[40m',
    'BG_RED': '\033[41m',
    'BG_GREEN': '\033[42m',
    'BG_YELLOW': '\033[43m',
    'BG_BLUE': '\033[44m',
    'BG_MAGENTA': '\033[45m',
    'BG_CYAN': '\033[46m',
    'BG_WHITE': '\033[47m'
}


def get_color(color_name: str) -> str:
    """Color enum을 안전하게 가져오는 함수"""
    try:
        if color_name in COLORS:
            return COLORS[color_name]
        else:
            # 알 수 없는 색상명인 경우 빈 문자열 반환
            return ''
    except Exception:
        # 모든 예외 상황에서 빈 문자열 반환
        return ''


class ColorText:
    """색상 텍스트 관리 클래스"""
    
    @staticmethod
    def is_color_supported() -> bool:
        """색상 지원 여부 확인 - Windows Terminal + PowerShell 호환성"""
        # 색상이 명시적으로 비활성화된 경우
        if COLOR_DISABLED:
            return False
            
        # 강제 색상 모드가 설정된 경우
        if os.environ.get('FORCE_COLOR') == '1':
            return True
            
        # Windows Terminal (PowerShell 포함)
        if WINDOWS_TERMINAL:
            return True
            
        # ConEmu, ANSICON 등
        if any(env in os.environ for env in ['ConEmuANSI', 'ANSICON']):
            return True
            
        # Unix/Linux 시스템
        if os.name != 'nt':
            return True
            
        # 기본적으로 색상 비활성화 (안전)
        return False
    
    @staticmethod
    def colorize(text: str, color: Color, bold: bool = False) -> str:
        """텍스트에 색상 적용"""
        if not ColorText.is_color_supported():
            return text
        
        prefix = color.value
        if bold:
            prefix = get_color('BOLD') + prefix
        
        return f"{prefix}{text}{get_color('RESET')}"
    
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
    """색상 적용 편의 함수 - PowerShell 호환성"""
    # PowerShell이나 색상이 지원되지 않는 환경에서는 텍스트만 반환
    if not ColorText.is_color_supported():
        return str(text)
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
    return f"{get_color('DIM')}{text}{get_color('RESET')}"

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
BLACK = get_color('BLACK')
RED = get_color('RED')
GREEN = get_color('GREEN')
YELLOW = get_color('YELLOW')
BLUE = get_color('BLUE')
MAGENTA = get_color('MAGENTA')
CYAN = get_color('CYAN')
WHITE = get_color('WHITE')
BRIGHT_BLACK = get_color('BRIGHT_BLACK')
BRIGHT_RED = get_color('BRIGHT_RED')
BRIGHT_GREEN = get_color('BRIGHT_GREEN')
BRIGHT_YELLOW = get_color('BRIGHT_YELLOW')
BRIGHT_BLUE = get_color('BRIGHT_BLUE')
BRIGHT_MAGENTA = get_color('BRIGHT_MAGENTA')
BRIGHT_CYAN = get_color('BRIGHT_CYAN')
BRIGHT_WHITE = get_color('BRIGHT_WHITE')
RESET = get_color('RESET')
BOLD = get_color('BOLD')
DIM = get_color('DIM')
UNDERLINE = get_color('UNDERLINE')

# 배경색 상수들
BG_BLACK = get_color('BG_BLACK')
BG_RED = get_color('BG_RED')
BG_GREEN = get_color('BG_GREEN')
BG_YELLOW = get_color('BG_YELLOW')
BG_BLUE = get_color('BG_BLUE')
BG_MAGENTA = get_color('BG_MAGENTA')
BG_CYAN = get_color('BG_CYAN')
BG_WHITE = get_color('BG_WHITE')
