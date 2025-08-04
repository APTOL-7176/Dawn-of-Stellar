#!/usr/bin/env python3
"""
안정적인 화면 출력 시스템
ANSI 색상 코드로 인한 화면 깨짐 방지
"""

import os
import re
import time
from typing import List, Optional
from .combat_visual import Color

class StableDisplay:
    """안정적인 화면 출력 클래스"""
    
    def __init__(self, width: int = 80, height: int = 25):
        self.width = width
        self.height = height
        self.buffer = []
        self.last_output = ""
        
    def strip_ansi(self, text: str) -> str:
        """ANSI 색상 코드 제거"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def get_visible_length(self, text: str) -> int:
        """실제 보이는 텍스트 길이 반환"""
        return len(self.strip_ansi(text))
    
    def safe_print(self, text: str, width: Optional[int] = None):
        """안전한 출력 - 길이 제한"""
        if width is None:
            width = self.width
            
        # ANSI 코드를 고려한 안전한 출력
        visible_len = self.get_visible_length(text)
        
        if visible_len > width:
            # 텍스트가 너무 길면 자르기 (공백 유지)
            stripped = self.strip_ansi(text)
            truncated = stripped[:width-3] + " ..."
            print(truncated)
        else:
            print(text)
    
    def clear_screen(self):
        """화면 지우기"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def create_box(self, content: List[str], title: str = "", border_char: str = "=") -> List[str]:
        """박스 형태로 내용 감싸기"""
        if not content:
            return []
        
        # 내용의 최대 너비 계산
        max_width = max(self.get_visible_length(line) for line in content)
        box_width = min(max_width + 4, self.width)
        
        lines = []
        
        # 상단 경계
        if title:
            title_line = f" {title} "
            title_padding = (box_width - len(title_line)) // 2
            lines.append(border_char * title_padding + title_line + border_char * (box_width - title_padding - len(title_line)))
        else:
            lines.append(border_char * box_width)
        
        # 내용
        for line in content:
            visible_len = self.get_visible_length(line)
            padding = box_width - visible_len - 3
            if padding > 0:
                lines.append(f"| {line}{' ' * padding}|")
            else:
                # 너무 긴 줄은 자르기 (공백 유지)
                stripped = self.strip_ansi(line)
                truncated = stripped[:box_width-6] + " ..."
                lines.append(f"| {truncated} |")
        
        # 하단 경계
        lines.append(border_char * box_width)
        
        return lines
    
    def show_simple_map(self, map_lines: List[str], player_info: str = ""):
        """간단하고 안정적인 맵 표시"""
        self.clear_screen()
        
        # 헤더
        header = f"{Color.BRIGHT_CYAN}=== DAWN OF STELLAR ==={Color.RESET}"
        self.safe_print(header, self.width)
        self.safe_print("", self.width)
        
        # 맵 표시 (안전한 길이로)
        map_width = min(60, self.width - 4)
        for line in map_lines[:20]:  # 최대 20줄
            # ANSI 코드가 있는 경우 처리
            visible_len = self.get_visible_length(line)
            if visible_len > map_width:
                # 너무 긴 줄 자르기
                stripped = self.strip_ansi(line)
                line = stripped[:map_width]
            
            self.safe_print(f"  {line}", self.width)
        
        # 플레이어 정보
        if player_info:
            self.safe_print("", self.width)
            self.safe_print(f"{Color.YELLOW}파티 상태:{Color.RESET}", self.width)
            for info_line in player_info.split('\n'):
                if info_line.strip():
                    self.safe_print(f"  {info_line}", self.width)
    
    def show_combat_simple(self, party: List, enemies: List, current_char=None):
        """간단하고 안정적한 전투 화면 - ATB/MP 강화 버전"""
        self.clear_screen()
        
        # 헤더
        self.safe_print(f"{Color.BRIGHT_RED}{'='*70}{Color.RESET}")
        self.safe_print(f"{Color.BRIGHT_YELLOW}  ⚔️  전투 진행 중 - ATB 시스템  ⚔️{Color.RESET}")
        self.safe_print(f"{Color.BRIGHT_RED}{'='*70}{Color.RESET}")
        self.safe_print("")
        
        # 파티 상태 (ATB/MP 추가)
        self.safe_print(f"{Color.BRIGHT_BLUE}👥 아군 파티:{Color.RESET}")
        self.safe_print("-" * 65)
        for char in party:
            if char.is_alive:
                name_color = Color.BRIGHT_GREEN if char == current_char else Color.WHITE
                status = "⚡" if char == current_char else "  "
                
                # HP 상태
                hp_ratio = char.current_hp / char.max_hp if char.max_hp > 0 else 0
                if hp_ratio > 0.7:
                    hp_color = Color.GREEN
                elif hp_ratio > 0.3:
                    hp_color = Color.YELLOW
                else:
                    hp_color = Color.RED
                
                # MP 상태
                mp_ratio = char.current_mp / char.max_mp if char.max_mp > 0 else 0
                if mp_ratio > 0.5:
                    mp_color = Color.BRIGHT_BLUE
                elif mp_ratio > 0.2:
                    mp_color = Color.BLUE
                else:
                    mp_color = Color.BRIGHT_BLACK
                
                # ATB 상태
                atb_gauge = getattr(char, 'atb_gauge', 0)
                if atb_gauge >= 1000:
                    atb_display = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
                    atb_bar = f"{Color.BRIGHT_CYAN}{'█'*10}{Color.RESET}"
                else:
                    atb_percent = int(atb_gauge / 10)  # 1000 스케일을 100%로 변환
                    atb_display = f"{Color.CYAN}{atb_percent:3}%{Color.RESET}"
                    filled = int(atb_gauge / 100)  # 1000 스케일에 맞게 조정
                    atb_bar = f"{Color.CYAN}{'█'*filled}{Color.BRIGHT_BLACK}{'░'*(10-filled)}{Color.RESET}"
                
                # 레벨 표시 추가
                level_display = f"Lv.{getattr(char, 'level', 1):2}"
                
                # 첫 번째 줄: 기본 정보 (레벨 추가)
                info1 = f"{status} {name_color}{char.name:10}{Color.RESET} {Color.BRIGHT_WHITE}{level_display}{Color.RESET} "
                info1 += f"HP:{hp_color}{char.current_hp:3}/{char.max_hp:3}{Color.RESET} "
                info1 += f"MP:{mp_color}{char.current_mp:3}/{char.max_mp:3}{Color.RESET} "
                info1 += f"BRV:{Color.YELLOW}{char.brave_points:4}{Color.RESET}"
                
                # 두 번째 줄: ATB와 상태 (ATB % 오른쪽으로)
                info2 = f"     ATB: [{atb_bar}]   {atb_display}"
                
                # 상태 이상 표시
                if hasattr(char, 'is_broken') and char.is_broken:
                    info2 += f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                elif hasattr(char, 'status_manager') and char.status_manager.effects:
                    info2 += f" {Color.YELLOW}[BUFF]{Color.RESET}"
                
                # 상처 정보
                if hasattr(char, 'wounds') and char.wounds > 0:
                    info2 += f" {Color.RED}🩸 WOUND:{char.wounds}{Color.RESET}"
                
                self.safe_print(f"  {info1}")
                self.safe_print(f"  {info2}")
                self.safe_print("")
        
        self.safe_print("")
        
        # 적 상태 (ATB 추가)
        self.safe_print(f"{Color.BRIGHT_RED}👹 적군:{Color.RESET}")
        self.safe_print("-" * 65)
        for enemy in enemies:
            if enemy.is_alive:
                name_color = Color.BRIGHT_RED if enemy == current_char else Color.WHITE
                status = "⚡" if enemy == current_char else "  "
                
                # HP 상태
                hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
                if hp_ratio > 0.7:
                    hp_color = Color.GREEN
                elif hp_ratio > 0.3:
                    hp_color = Color.YELLOW
                else:
                    hp_color = Color.RED
                
                # ATB 상태
                atb_gauge = getattr(enemy, 'atb_gauge', 0)
                if atb_gauge >= 1000:
                    atb_display = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
                    atb_bar = f"{Color.BRIGHT_CYAN}{'█'*10}{Color.RESET}"
                else:
                    atb_percent = int(atb_gauge / 10)  # 1000 스케일을 100%로 변환
                    atb_display = f"{Color.CYAN}{atb_percent:3}%{Color.RESET}"
                    filled = int(atb_gauge / 100)  # 1000 스케일에 맞게 조정
                    atb_bar = f"{Color.CYAN}{'█'*filled}{Color.BRIGHT_BLACK}{'░'*(10-filled)}{Color.RESET}"
                
                # 첫 번째 줄: 기본 정보
                info1 = f"{status} {name_color}{enemy.name:12}{Color.RESET} "
                info1 += f"HP:{hp_color}{enemy.current_hp:3}/{enemy.max_hp:3}{Color.RESET} "
                info1 += f"BRV:{Color.YELLOW}{enemy.brave_points:4}{Color.RESET}"
                
                # 두 번째 줄: ATB (ATB % 오른쪽으로)
                info2 = f"     ATB: [{atb_bar}]   {atb_display}"
                
                if hasattr(enemy, 'is_broken') and enemy.is_broken:
                    info2 += f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                
                self.safe_print(f"  {info1}")
                self.safe_print(f"  {info2}")
                self.safe_print("")
        
        self.safe_print(f"{Color.BRIGHT_RED}{'='*70}{Color.RESET}")
    
    def show_message(self, message: str, message_type: str = "info"):
        """간단한 메시지 표시"""
        if message_type == "error":
            color = Color.BRIGHT_RED
            prefix = "❌"
        elif message_type == "success":
            color = Color.BRIGHT_GREEN
            prefix = "✅"
        elif message_type == "warning":
            color = Color.BRIGHT_YELLOW
            prefix = "⚠️"
        else:
            color = Color.WHITE
            prefix = "ℹ️"
        
        formatted_msg = f"{color}{prefix} {message}{Color.RESET}"
        self.safe_print(formatted_msg)
    
    def show_menu(self, title: str, options: List[str], selected: int = -1):
        """안전한 메뉴 표시"""
        self.safe_print(f"\n{Color.BRIGHT_CYAN}{title}{Color.RESET}")
        self.safe_print("-" * len(title))
        
        for i, option in enumerate(options):
            if i == selected:
                self.safe_print(f"{Color.BRIGHT_YELLOW}► {option}{Color.RESET}")
            else:
                self.safe_print(f"  {option}")
    
    def pause_for_input(self, prompt: str = "계속하려면 아무 키나 누르세요..."):
        """입력 대기"""
        self.safe_print(f"\n{Color.DIM}{prompt}{Color.RESET}")
        
        # AI 자동 모드 체크 (전역에서 확인)
        import sys
        if hasattr(sys.modules.get('__main__'), 'ai_auto_mode') and sys.modules.get('__main__').ai_auto_mode:
            self.safe_print(f"{Color.GREEN}🤖 AI 자동 모드: 자동으로 계속 진행합니다.{Color.RESET}")
            import time
            time.sleep(0.3)  # 0.3초 대기
        else:
            input()

# 전역 인스턴스
stable_display = StableDisplay()

def get_stable_display():
    """안정적인 디스플레이 인스턴스 반환"""
    return stable_display
