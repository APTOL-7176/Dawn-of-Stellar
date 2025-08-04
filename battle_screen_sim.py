#!/usr/bin/env python3
"""
전투창 시뮬레이션 - 개선된 게이지 시스템
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

# Color 클래스 정의
class Color:
    RESET = '\033[0m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_WHITE = '\033[97m'
    BRIGHT_CYAN = '\033[96m'
    WHITE = '\033[37m'
    BRIGHT_GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED = '\033[91m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    BRIGHT_MAGENTA = '\033[95m'
    GREEN = '\033[32m'
    BRIGHT_BLACK = '\033[90m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'

# 모의 Character 클래스
class MockCharacter:
    def __init__(self, name, level, character_class, current_hp, max_hp, current_mp, max_mp, brave_points, atb_gauge, is_casting=False):
        self.name = name
        self.level = level
        self.character_class = character_class
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.current_mp = current_mp
        self.max_mp = max_mp
        self.brave_points = brave_points
        self.atb_gauge = atb_gauge
        self.is_alive = current_hp > 0
        self.is_casting = is_casting
        self.speed = 100
        
# 모의 BraveCombatSystem
class MockBraveCombatSystem:
    ATB_MAX = 10000
    ATB_READY_THRESHOLD = 10000
    ATB_DISPLAY_SCALE = 100
    
    def create_beautiful_hp_gauge(self, current: int, maximum: int, length: int = 18) -> str:
        if maximum <= 0:
            return " " * length
        ratio = current / maximum
        filled_blocks = int(ratio * length)
        if ratio >= 0.6:
            color = Color.BRIGHT_GREEN
        elif ratio >= 0.3:
            color = Color.YELLOW
        else:
            color = Color.BRIGHT_RED
        gauge = f"{color}{'█' * filled_blocks}{Color.RESET}"
        gauge += " " * (length - filled_blocks)
        return gauge
        
    def create_beautiful_mp_gauge(self, current: int, maximum: int, length: int = 18) -> str:
        if maximum <= 0:
            return " " * length
        ratio = current / maximum
        filled_blocks = int(ratio * length)
        color = Color.BRIGHT_CYAN
        gauge = f"{color}{'█' * filled_blocks}{Color.RESET}"
        gauge += " " * (length - filled_blocks)
        return gauge
        
    def create_beautiful_atb_gauge(self, current: int, maximum: int, length: int = 18, is_casting: bool = False) -> str:
        if maximum <= 0:
            return " " * length
        ratio = current / maximum
        filled_blocks = int(ratio * length)
        if is_casting:
            color = Color.BRIGHT_MAGENTA
        else:
            color = Color.BRIGHT_CYAN
        gauge = f"{color}{'█' * filled_blocks}{Color.RESET}"
        gauge += " " * (length - filled_blocks)
        return gauge

def simulate_battle_screen():
    """전투 화면 시뮬레이션"""
    combat = MockBraveCombatSystem()
    
    # 모의 파티 데이터
    party = [
        MockCharacter("코딘", 15, "궁수", 750, 850, 280, 320, 1250, 8500),
        MockCharacter("루나", 14, "아크메이지", 420, 520, 180, 250, 850, 6200, True),  # 캐스팅 중
        MockCharacter("벤자민", 16, "전사", 980, 1200, 50, 80, 2100, 9800),
        MockCharacter("세라", 13, "성기사", 680, 780, 220, 280, 600, 3400)
    ]
    
    # 모의 적군 데이터  
    enemies = [
        MockCharacter("고블린 족장", 12, "Enemy", 350, 500, 80, 120, 800, 7300),
        MockCharacter("오크 전사", 14, "Enemy", 120, 800, 40, 60, 1200, 4100),  # 저체력
        MockCharacter("다크 메이지", 15, "Enemy", 280, 400, 150, 200, 950, 10000)  # READY 상태
    ]
    
    print(f"{Color.BRIGHT_CYAN}🌟 Dawn Of Stellar - 전투 화면 시뮬레이션 🌟{Color.RESET}")
    print("=" * 80)
    
    # 아군 파티 표시
    print(f"\n{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}🛡️  아군 파티 상태{Color.RESET}")
    print(f"{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
    
    for i, member in enumerate(party, 1):
        if member.is_alive:
            # 현재 턴 캐릭터 강조 (첫 번째 캐릭터)
            if i == 1:
                status_icon = "▶ "
                name_color = Color.BRIGHT_YELLOW
            else:
                status_icon = "  "
                name_color = Color.BRIGHT_WHITE
            
            # 클래스 아이콘
            class_icon = {
                '전사': '⚔️', '아크메이지': '🔮', '궁수': '🏹', '도적': '🗡️',
                '성기사': '🛡️', '암흑기사': '💀', '몽크': '👊', '바드': '🎵',
            }.get(member.character_class, '🎭')
            
            # 게이지 생성 (길이 20으로 증가)
            hp_bar = combat.create_beautiful_hp_gauge(member.current_hp, member.max_hp, 20)
            mp_bar = combat.create_beautiful_mp_gauge(member.current_mp, member.max_mp, 20)
            
            # ATB 게이지 생성
            atb_percent = int(member.atb_gauge // combat.ATB_DISPLAY_SCALE)
            if member.is_casting:
                atb_display = f"{Color.BRIGHT_MAGENTA}🔮 75%{Color.RESET}"
                atb_bar = combat.create_beautiful_atb_gauge(75, 100, 20, True)
            elif member.atb_gauge >= combat.ATB_READY_THRESHOLD:
                atb_display = f"{Color.BRIGHT_YELLOW}READY{Color.RESET}"
                atb_bar = combat.create_beautiful_atb_gauge(100, 100, 20, False)
            else:
                atb_display = f"{Color.BRIGHT_CYAN}{atb_percent}%{Color.RESET}"
                atb_bar = combat.create_beautiful_atb_gauge(atb_percent, 100, 20, False)
            
            # BRV 색상 결정
            if member.brave_points <= 299:
                brv_color = Color.BRIGHT_RED
            elif member.brave_points >= 5000:
                brv_color = Color.BRIGHT_MAGENTA
            else:
                brv_color = Color.BRIGHT_YELLOW
            
            # 상태이상 아이콘
            status_icons = ""
            if member.is_casting:
                status_icons += " 🔮"
            
            # 캐스팅 상태 표시
            casting_status = ""
            if member.is_casting:
                casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: 파이어볼]{Color.RESET}"
            
            print(f"  {status_icon}{class_icon} Lv.{member.level} {name_color}{member.name}{Color.RESET}{status_icons}")
            print(f"  💚 HP: {Color.BRIGHT_GREEN}{member.current_hp}{Color.RESET} / {Color.WHITE}{member.max_hp}{Color.RESET} {Color.WHITE}[{hp_bar}]{Color.RESET}")
            print(f"  💙 MP: {Color.BRIGHT_CYAN}{member.current_mp}{Color.RESET} / {Color.WHITE}{member.max_mp}{Color.RESET} {Color.WHITE}[{mp_bar}]{Color.RESET} | {brv_color}⚡ BRV: {member.brave_points}{Color.RESET}")
            print(f"  ⌛ TIME: {Color.WHITE}[{atb_bar}]{Color.RESET} {atb_display} | SPD: {Color.WHITE}{member.speed}{Color.RESET}{casting_status}")
    
    # 적군 상태 표시
    print(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}⚔️  적군 상태{Color.RESET}")
    print(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
    
    for enemy in enemies:
        if enemy.is_alive:
            # HP 비율에 따른 색상
            hp_ratio = enemy.current_hp / enemy.max_hp
            if hp_ratio > 0.6:
                hp_color = Color.BRIGHT_GREEN
            elif hp_ratio > 0.3:
                hp_color = Color.YELLOW
            else:
                hp_color = Color.BRIGHT_RED
            
            # 게이지 생성
            hp_bar = combat.create_beautiful_hp_gauge(enemy.current_hp, enemy.max_hp, 20)
            
            # ATB 게이지
            atb_percent = int(enemy.atb_gauge // combat.ATB_DISPLAY_SCALE)
            if enemy.atb_gauge >= combat.ATB_READY_THRESHOLD:
                atb_display = f"{Color.BRIGHT_YELLOW}READY{Color.RESET}"
                atb_bar = combat.create_beautiful_atb_gauge(100, 100, 20, False)
                atb_icon = "⚡"
            else:
                atb_display = f"{Color.BRIGHT_CYAN}{atb_percent}%{Color.RESET}"
                atb_bar = combat.create_beautiful_atb_gauge(atb_percent, 100, 20, False)
                atb_icon = "⏳"
            
            print(f"  💀 {Color.BRIGHT_RED}{enemy.name}{Color.RESET}")
            print(f"  💚 HP: {hp_color}{enemy.current_hp}{Color.RESET} / {Color.WHITE}{enemy.max_hp}{Color.RESET} {Color.WHITE}[{hp_bar}]{Color.RESET}")
            print(f"  {atb_icon} TIME: {Color.WHITE}[{atb_bar}]{Color.RESET} {atb_display}")
    
    print(f"{Color.BRIGHT_GREEN}✨ 개선된 게이지 시스템이 적용되었습니다!{Color.RESET}")
    print("=" * 80)
    print(f"{Color.BRIGHT_CYAN}특징:{Color.RESET}")
    print(f"  • HP/MP/ATB 게이지 길이: 10칸 → 20칸으로 확장")
    print(f"  • 구형 ▰▱ 블록 → 깔끔한 █ 블록으로 교체")
    print(f"  • BRV 게이지 제거 (수치만 표시)")
    print(f"  • 캐스팅 상태 시각화 개선")
    print(f"  • 색상별 상태 구분 강화")

if __name__ == "__main__":
    simulate_battle_screen()
