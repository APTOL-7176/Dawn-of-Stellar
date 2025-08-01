#!/usr/bin/env python3
"""
UI 시스템 개선 - 깔끔한 인터페이스, Windows 호환
"""

import math
import os
from typing import Tuple, List, Dict, Optional
from enum import Enum

# Windows용 curses 대안
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    # Windows에서 curses가 없을 경우 더미 모듈
    class DummyCurses:
        def initscr(self): return None
        def endwin(self): pass
        def cbreak(self): pass
        def noecho(self): pass
        def curs_set(self, visibility): pass
        def newwin(self, *args): return DummyWindow()
        
    class DummyWindow:
        def addstr(self, *args): pass
        def refresh(self): pass
        def clear(self): pass
        def move(self, *args): pass
        def getmaxyx(self): return (24, 80)
        
    curses = DummyCurses()
    CURSES_AVAILABLE = False

class UIColor(Enum):
    """UI 색상"""
    WHITE = 1
    RED = 2
    GREEN = 3
    BLUE = 4
    YELLOW = 5
    MAGENTA = 6
    CYAN = 7
    BLACK = 8

class UIManager:
    """UI 관리자"""
    
    def __init__(self):
        self.stdscr = None
        self.colors_initialized = False
        self.screen_height = 0
        self.screen_width = 0
        
        # UI 영역 정의
        self.map_area = None
        self.status_area = None
        self.message_area = None
        self.menu_area = None
        
        # 시야 관련
        self.vision_radius = 8
        self.fov_map = {}
        
    def initialize(self, stdscr=None):
        """UI 초기화"""
        if not CURSES_AVAILABLE:
            self.screen_height = 24
            self.screen_width = 80
            return
            
        self.stdscr = stdscr
        if stdscr:
            self.screen_height, self.screen_width = stdscr.getmaxyx()
            
            # 커서 숨기기
            curses.curs_set(0)
            
            # 색상 초기화
            if curses.has_colors():
                curses.start_color()
                curses.use_default_colors()
                
                curses.init_pair(UIColor.WHITE.value, curses.COLOR_WHITE, -1)
                curses.init_pair(UIColor.RED.value, curses.COLOR_RED, -1)
                curses.init_pair(UIColor.GREEN.value, curses.COLOR_GREEN, -1)
            curses.init_pair(UIColor.BLUE.value, curses.COLOR_BLUE, -1)
            curses.init_pair(UIColor.YELLOW.value, curses.COLOR_YELLOW, -1)
            curses.init_pair(UIColor.MAGENTA.value, curses.COLOR_MAGENTA, -1)
            curses.init_pair(UIColor.CYAN.value, curses.COLOR_CYAN, -1)
            curses.init_pair(UIColor.BLACK.value, curses.COLOR_BLACK, -1)
            
            self.colors_initialized = True
        
        # UI 영역 계산
        self._calculate_ui_areas()
    
    def _calculate_ui_areas(self):
        """UI 영역 계산"""
        # 맵 영역 (좌측 상단, 정사각형에 가깝게)
        map_width = min(self.screen_width * 2 // 3, self.screen_height - 4)
        map_height = self.screen_height - 4
        
        self.map_area = {
            "x": 1, "y": 1,
            "width": map_width, "height": map_height
        }
        
        # 상태 영역 (우측 상단)
        self.status_area = {
            "x": map_width + 2, "y": 1,
            "width": self.screen_width - map_width - 3, "height": map_height // 2
        }
        
        # 메시지 영역 (우측 하단)
        self.message_area = {
            "x": map_width + 2, "y": map_height // 2 + 2,
            "width": self.screen_width - map_width - 3, "height": map_height // 2 - 1
        }
        
        # 메뉴 영역 (하단)
        self.menu_area = {
            "x": 1, "y": self.screen_height - 2,
            "width": self.screen_width - 2, "height": 1
        }
    
    def clear_screen(self):
        """화면 지우기"""
        if CURSES_AVAILABLE and self.stdscr:
            self.stdscr.clear()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def refresh_screen(self):
        """화면 새로고침"""
        if CURSES_AVAILABLE and self.stdscr:
            self.stdscr.refresh()
    
    def draw_border(self, area: Dict, title: str = ""):
        """테두리 그리기"""
        if not CURSES_AVAILABLE or not self.stdscr:
            return
        
        x, y = area["x"], area["y"]
        width, height = area["width"], area["height"]
        
        try:
            # 상하단
            for i in range(width):
                self.stdscr.addch(y, x + i, "─")
                self.stdscr.addch(y + height - 1, x + i, "─")
            
            # 좌우단
            for i in range(height):
                self.stdscr.addch(y + i, x, "│")
                self.stdscr.addch(y + i, x + width - 1, "│")
            
            # 모서리
            self.stdscr.addch(y, x, "┌")
            self.stdscr.addch(y, x + width - 1, "┐")
            self.stdscr.addch(y + height - 1, x, "└")
            self.stdscr.addch(y + height - 1, x + width - 1, "┘")
            
            # 제목
            if title:
                title_x = x + (width - len(title)) // 2
                self.stdscr.addstr(y, title_x, f"[ {title} ]")
        except:
            pass
    
    def draw_text(self, x: int, y: int, text: str, color: UIColor = UIColor.WHITE):
        """텍스트 그리기"""
        if not CURSES_AVAILABLE or not self.stdscr:
            return
        
        try:
            if self.colors_initialized:
                self.stdscr.addstr(y, x, text, curses.color_pair(color.value))
            else:
                self.stdscr.addstr(y, x, text)
        except:
            pass  # 화면 밖으로 나간 경우 무시
    
    def draw_centered_text(self, y: int, text: str, color: UIColor = UIColor.WHITE):
        """중앙 정렬 텍스트"""
        x = (self.screen_width - len(text)) // 2
        self.draw_text(x, y, text, color)
    
    def calculate_circular_fov(self, center_x: int, center_y: int, radius: int = 8) -> Dict[Tuple[int, int], bool]:
        """원형 시야 계산 (스페이스바로 빈 공간 표시)"""
        fov = {}
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # 원형 공식: x² + y² <= r²
                distance_squared = dx * dx + dy * dy
                if distance_squared <= radius * radius:
                    x, y = center_x + dx, center_y + dy
                    fov[(x, y)] = True
        
        return fov
    
    def draw_game_map(self, game_map: List[List[str]], player_x: int, player_y: int,
                     entities: Dict[Tuple[int, int], str] = None):
        """게임 맵 그리기"""
        if not self.stdscr or not self.map_area:
            return
        
        area = self.map_area
        
        # 테두리 그리기
        self.draw_border(area, "던전")
        
        # 시야 계산 (원형으로 변경)
        fov = self.calculate_circular_fov(player_x, player_y)
        
        # 맵 중앙을 플레이어 위치로 설정
        map_center_x = area["width"] // 2
        map_center_y = area["height"] // 2
        
        # 맵 그리기
        for dy in range(area["height"] - 2):
            for dx in range(area["width"] - 2):
                map_x = player_x + (dx - map_center_x)
                map_y = player_y + (dy - map_center_y)
                
                screen_x = area["x"] + 1 + dx
                screen_y = area["y"] + 1 + dy
                
                # 맵 범위 체크
                if (0 <= map_x < len(game_map[0]) and 
                    0 <= map_y < len(game_map)):
                    
                    # 시야 내인지 확인
                    if (map_x, map_y) in fov:
                        # 엔티티가 있는지 확인
                        if entities and (map_x, map_y) in entities:
                            char = entities[(map_x, map_y)]
                            color = UIColor.YELLOW
                        else:
                            char = game_map[map_y][map_x]
                            color = self._get_tile_color(char)
                        
                        self.draw_text(screen_x, screen_y, char, color)
                    else:
                        # 시야 밖은 스페이스(공백)로 표시
                        self.draw_text(screen_x, screen_y, " ", UIColor.BLACK)
                else:
                    # 맵 밖도 스페이스로 표시
                    self.draw_text(screen_x, screen_y, " ", UIColor.BLACK)
        
        # 플레이어 그리기 (항상 중앙에)
        player_screen_x = area["x"] + 1 + map_center_x
        player_screen_y = area["y"] + 1 + map_center_y
        self.draw_text(player_screen_x, player_screen_y, "@", UIColor.GREEN)
    
    def _get_tile_color(self, tile: str) -> UIColor:
        """타일별 색상 결정"""
        tile_colors = {
            "#": UIColor.WHITE,    # 벽
            ".": UIColor.WHITE,    # 바닥
            "+": UIColor.YELLOW,   # 문
            ">": UIColor.CYAN,     # 계단 (내려가기)
            "<": UIColor.CYAN,     # 계단 (올라가기)
            "!": UIColor.RED,      # 함정
            "$": UIColor.YELLOW,   # 골드
            "?": UIColor.BLUE,     # 아이템
        }
        return tile_colors.get(tile, UIColor.WHITE)
    
    def draw_status_panel(self, character_data: Dict):
        """상태 패널 그리기"""
        if not self.stdscr or not self.status_area:
            return
        
        area = self.status_area
        self.draw_border(area, "상태")
        
        # 캐릭터 정보
        y_offset = 2
        
        name = character_data.get("name", "모험가")
        job = character_data.get("job", "전사")
        level = character_data.get("level", 1)
        
        self.draw_text(area["x"] + 2, area["y"] + y_offset, f"{name} ({job})", UIColor.CYAN)
        y_offset += 1
        self.draw_text(area["x"] + 2, area["y"] + y_offset, f"레벨: {level}", UIColor.WHITE)
        y_offset += 2
        
        # HP/MP 바
        hp = character_data.get("current_hp", 100)
        max_hp = character_data.get("max_hp", 100)
        mp = character_data.get("current_mp", 50)
        max_mp = character_data.get("max_mp", 50)
        
        self._draw_progress_bar(area["x"] + 2, area["y"] + y_offset, 
                               "HP", hp, max_hp, UIColor.RED, area["width"] - 4)
        y_offset += 2
        
        self._draw_progress_bar(area["x"] + 2, area["y"] + y_offset,
                               "MP", mp, max_mp, UIColor.BLUE, area["width"] - 4)
        y_offset += 2
        
        # BRV
        brv = character_data.get("current_brv", 1000)
        max_brv = character_data.get("max_brv", 5000)
        self._draw_progress_bar(area["x"] + 2, area["y"] + y_offset,
                               "BRV", brv, max_brv, UIColor.YELLOW, area["width"] - 4)
        y_offset += 2
        
        # 기본 스탯
        stats = ["attack", "defense", "magic_power", "speed"]
        for stat in stats:
            if y_offset < area["height"] - 2:
                value = character_data.get(stat, 0)
                stat_name = {"attack": "공격", "defense": "방어", 
                           "magic_power": "마력", "speed": "속도"}.get(stat, stat)
                self.draw_text(area["x"] + 2, area["y"] + y_offset, 
                             f"{stat_name}: {value}", UIColor.WHITE)
                y_offset += 1
    
    def _draw_progress_bar(self, x: int, y: int, label: str, current: int, maximum: int,
                          color: UIColor, width: int):
        """진행률 바 그리기"""
        if maximum <= 0:
            return
        
        bar_width = width - len(label) - 15  # 라벨과 숫자 공간 제외
        if bar_width <= 0:
            return
        
        filled = int((current / maximum) * bar_width)
        
        # 라벨
        self.draw_text(x, y, f"{label}:", UIColor.WHITE)
        
        # 바
        bar_x = x + len(label) + 2
        self.draw_text(bar_x, y, "[", UIColor.WHITE)
        
        for i in range(bar_width):
            if i < filled:
                self.draw_text(bar_x + 1 + i, y, "█", color)
            else:
                self.draw_text(bar_x + 1 + i, y, "░", UIColor.WHITE)
        
        self.draw_text(bar_x + bar_width + 1, y, "]", UIColor.WHITE)
        
        # 숫자
        numbers = f"{current}/{maximum}"
        self.draw_text(bar_x + bar_width + 3, y, numbers, UIColor.WHITE)
    
    def draw_message_panel(self, messages: List[str]):
        """메시지 패널 그리기"""
        if not self.stdscr or not self.message_area:
            return
        
        area = self.message_area
        self.draw_border(area, "메시지")
        
        # 최근 메시지들만 표시
        max_messages = area["height"] - 2
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        for i, message in enumerate(recent_messages):
            if len(message) > area["width"] - 4:
                message = message[:area["width"] - 7] + "..."
            
            self.draw_text(area["x"] + 2, area["y"] + 1 + i, message, UIColor.WHITE)
    
    def draw_menu(self, menu_items: List[str], selected_index: int = 0):
        """메뉴 그리기"""
        if not self.stdscr or not self.menu_area:
            return
        
        area = self.menu_area
        
        # 메뉴 아이템들을 한 줄에 표시
        x_offset = area["x"]
        
        for i, item in enumerate(menu_items):
            if i == selected_index:
                # 선택된 아이템은 하이라이트
                self.draw_text(x_offset, area["y"], f"[{item}]", UIColor.YELLOW)
                x_offset += len(item) + 4
            else:
                self.draw_text(x_offset, area["y"], f" {item} ", UIColor.WHITE)
                x_offset += len(item) + 3
    
    def show_title_screen(self):
        """타이틀 화면 - 깔끔한 텍스트 로고"""
        self.clear_screen()
        
        # 깔끔한 텍스트 로고
        title_lines = [
            "",
            "Dawn Of Stellar",
            "별빛의 여명",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "28명의 개성있는 캐릭터들과 함께하는",
            "전술 ATB 로그라이크 RPG",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "",
            "1. ⚔️  새 게임 시작",
            "2. 📁  게임 불러오기", 
            "3. 📚  튜토리얼",
            "4. ⚙️  설정",
            "5. 🚪  게임 종료",
            "",
            "",
            "방향키로 선택, Enter로 확인"
        ]
        
        start_y = (self.screen_height - len(title_lines)) // 2
        
        for i, line in enumerate(title_lines):
            if line in ["Dawn Of Stellar", "별빛의 여명"]:  # 제목
                self.draw_centered_text(start_y + i, line, UIColor.CYAN)
            elif "━" in line:  # 구분선
                self.draw_centered_text(start_y + i, line, UIColor.WHITE)
            elif line.startswith(("1.", "2.", "3.", "4.", "5.")):  # 메뉴 항목
                self.draw_centered_text(start_y + i, line, UIColor.YELLOW)
            elif "28명의 개성있는" in line or "전술 ATB" in line:  # 설명
                self.draw_centered_text(start_y + i, line, UIColor.GREEN)
            else:
                self.draw_centered_text(start_y + i, line, UIColor.WHITE)
        
        self.refresh_screen()
    
    def show_inventory(self, items: List[Dict], selected_index: int = 0):
        """인벤토리 화면"""
        self.clear_screen()
        
        # 제목
        self.draw_centered_text(2, "인벤토리", UIColor.CYAN)
        self.draw_centered_text(3, "=" * 20, UIColor.WHITE)
        
        if not items:
            self.draw_centered_text(10, "아이템이 없습니다.", UIColor.WHITE)
        else:
            start_y = 5
            for i, item in enumerate(items):
                color = UIColor.YELLOW if i == selected_index else UIColor.WHITE
                item_text = f"{item.get('name', '알 수 없는 아이템')} ({item.get('quantity', 1)}개)"
                
                self.draw_text(5, start_y + i, item_text, color)
                
                if i == selected_index:
                    # 선택된 아이템 설명
                    desc = item.get('description', '설명 없음')
                    self.draw_text(40, start_y + i, desc, UIColor.CYAN)
        
        # 도움말
        self.draw_centered_text(self.screen_height - 3, "방향키: 선택, Enter: 사용, ESC: 닫기", UIColor.WHITE)
        
        self.refresh_screen()
    
    def show_game_over(self, final_stats: Dict):
        """게임 오버 화면"""
        self.clear_screen()
        
        lines = [
            "게임 오버",
            "=========",
            "",
            f"레벨: {final_stats.get('level', 1)}",
            f"도달 층수: {final_stats.get('floor', 1)}",
            f"처치한 적: {final_stats.get('kills', 0)}",
            f"플레이 시간: {final_stats.get('playtime', '0:00')}",
            "",
            "아무 키나 누르세요..."
        ]
        
        start_y = (self.screen_height - len(lines)) // 2
        
        for i, line in enumerate(lines):
            if i == 0:  # 제목
                self.draw_centered_text(start_y + i, line, UIColor.RED)
            elif "=" in line:  # 구분선
                self.draw_centered_text(start_y + i, line, UIColor.WHITE)
            else:
                self.draw_centered_text(start_y + i, line, UIColor.WHITE)
        
        self.refresh_screen()

# 전역 UI 매니저
ui_manager = UIManager()

def get_ui_manager() -> UIManager:
    """UI 매니저 반환"""
    return ui_manager
