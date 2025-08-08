#!/usr/bin/env python3
"""
향상된 전투 비주얼 시스템
컬러와 ASCII 아트를 활용한 전투 화면
"""

import random
import time
from typing import List, Dict, Any
from enum import Enum

class Color:
    """ANSI 컬러 코드"""
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
    
    # 배경 색상
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    
    # 스타일
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # 리셋
    RESET = '\033[0m'
    END = '\033[0m'

class EffectType(Enum):
    PHYSICAL_ATTACK = "physical"
    MAGIC_ATTACK = "magic"
    HP_ATTACK = "hp_attack"
    HEAL = "heal"
    CRITICAL = "critical"
    DEFEND = "defend"
    SKILL = "skill"
    BRAVE_GAIN = "brave"
    BREAK = "break"
    DEATH = "death"

class CombatVisualizer:
    """전투 시각 효과 시스템"""
    
    def __init__(self):
        self.character_sprites = {
            # 플레이어 캐릭터들
            '검사': '🗡️',
            '대마법사': '🔮',
            '성기사': '🛡️',
            '암살자': '🗡️',
            '궁수': '🏹',
            '전사': '⚔️',
            '마법사': '✨',
            '도적': '🗡️'
        }
        
        self.enemy_sprites = {
            '고블린': '👹',
            '오크': '👿',
            '스켈레톤': '💀',
            '드래곤': '🐲',
            '슬라임': '🟢',
            '좀비': '🧟',
            '마법사': '🧙',
            '기사': '🤺'
        }
        
        self.effect_colors = {
            EffectType.PHYSICAL_ATTACK: Color.BRIGHT_RED,
            EffectType.MAGIC_ATTACK: Color.BRIGHT_BLUE,
            EffectType.HEAL: Color.BRIGHT_GREEN,
            EffectType.CRITICAL: Color.BRIGHT_YELLOW,
            EffectType.DEFEND: Color.CYAN,
            EffectType.SKILL: Color.BRIGHT_MAGENTA,
            EffectType.BRAVE_GAIN: Color.YELLOW,
            EffectType.BREAK: Color.BRIGHT_RED,
            EffectType.DEATH: Color.BRIGHT_BLACK
        }
    
    def get_character_sprite(self, character):
        """캐릭터 스프라이트 반환"""
        # character가 유효한 객체인지 확인
        if not hasattr(character, 'name'):
            return '❓'  # name 속성이 없으면 기본 스프라이트 반환
            
        class_name = getattr(character, 'character_class', '전사')
        name = character.name.lower()
        
        # 적인지 확인
        if hasattr(character, 'is_enemy') or '고블린' in name or '오크' in name or '스켈레톤' in name or '드래곤' in name:
            for enemy_type in self.enemy_sprites:
                if enemy_type in name:
                    return self.enemy_sprites[enemy_type]
            return '👹'  # 기본 적 스프라이트
        
        # 플레이어 캐릭터
        return self.character_sprites.get(class_name, '⚔️')
    
    def get_hp_bar(self, current_hp: int, max_hp: int, width: int = 20) -> str:
        """HP 바 생성"""
        if max_hp <= 0:
            ratio = 0
        else:
            ratio = current_hp / max_hp
        
        filled = int(ratio * width)
        empty = width - filled
        
        # HP 비율에 따른 색상
        if ratio > 0.7:
            color = Color.BRIGHT_GREEN
        elif ratio > 0.3:
            color = Color.BRIGHT_YELLOW
        else:
            color = Color.BRIGHT_RED
        
        bar = color + '█' * filled + Color.BRIGHT_BLACK + '░' * empty + Color.RESET
        return f"[{bar}] {current_hp}/{max_hp}"
    
    def get_atb_bar(self, atb_gauge: float, width: int = 10) -> str:
        """ATB 게이지 바 생성"""
        ratio = min(atb_gauge / 100, 1.0)
        filled = int(ratio * width)
        empty = width - filled
        
        if ratio >= 1.0:
            color = Color.BRIGHT_CYAN + Color.BLINK
        elif ratio > 0.7:
            color = Color.CYAN
        else:
            color = Color.BLUE
        
        bar = color + '▰' * filled + Color.BRIGHT_BLACK + '▱' * empty + Color.RESET
        return f"ATB[{bar}]"
    
    def get_atb_visual_bar(self, atb_gauge: float, width: int = 15) -> str:
        """ATB 시각적 바 생성 (더 상세한 버전)"""
        ratio = min(atb_gauge / 100, 1.0)
        filled = int(ratio * width)
        empty = width - filled
        
        if ratio >= 1.0:
            color = Color.BRIGHT_CYAN
            char = '█'
        elif ratio >= 0.75:
            color = Color.CYAN
            char = '▓'
        elif ratio >= 0.5:
            color = Color.BLUE
            char = '▒'
        else:
            color = Color.BRIGHT_BLACK
            char = '░'
        
        bar = color + char * filled + Color.BRIGHT_BLACK + '░' * empty + Color.RESET
        return f"[{bar}]"
    
    def get_mp_bar(self, current_mp: int, max_mp: int, width: int = 8) -> str:
        """MP 바 생성"""
        if max_mp <= 0:
            ratio = 0
        else:
            ratio = current_mp / max_mp
        
        filled = int(ratio * width)
        empty = width - filled
        
        # MP 비율에 따른 색상
        if ratio > 0.5:
            color = Color.BRIGHT_BLUE
        elif ratio > 0.2:
            color = Color.BLUE
        else:
            color = Color.BRIGHT_BLACK
        
        bar = color + '▪' * filled + Color.BRIGHT_BLACK + '▫' * empty + Color.RESET
        return f"[{bar}]"
    
    def show_battle_field(self, party: List, enemies: List, current_char=None):
        """전투 필드 표시 - 세로 정렬된 ATB와 MP 포함 개선 버전"""
        # 화면 크기 제한
        max_width = 90
        
        print("\n" + "=" * max_width)
        print(f"  ⚔️  전투 진행 중 - ATB 시스템  ⚔️")
        print("=" * max_width)
        
        # 파티 표시 (세로 정렬된 ATB)
        print(f"\n👥 아군 파티:")
        print("-" * 65)
        for char in party:
            if not char.is_alive:
                continue
                
            name_color = Color.BRIGHT_GREEN if char == current_char else Color.WHITE
            
            # 상태 아이콘
            status = ""
            if hasattr(char, 'is_broken') and char.is_broken:
                status = f"{Color.BRIGHT_RED}[BREAK]{Color.RESET}"
            elif hasattr(char, 'status_manager') and char.status_manager.effects:
                status = f"{Color.YELLOW}[BUFF]{Color.RESET}"
            
            # HP 상태
            hp_ratio = char.current_hp / char.max_hp if char.max_hp > 0 else 0
            hp_color = Color.BRIGHT_GREEN if hp_ratio > 0.7 else Color.BRIGHT_YELLOW if hp_ratio > 0.3 else Color.BRIGHT_RED
            
            # MP 상태 
            mp_ratio = char.current_mp / char.max_mp if char.max_mp > 0 else 0
            mp_color = Color.BRIGHT_BLUE if mp_ratio > 0.5 else Color.BLUE if mp_ratio > 0.2 else Color.BRIGHT_BLACK
            
            # ATB 게이지
            atb_gauge = getattr(char, 'atb_gauge', 0)
            if atb_gauge >= 1000:
                atb_bar = f"[{Color.BRIGHT_CYAN}██████████{Color.RESET}]"
                atb_status = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
            else:
                atb_percent = int(atb_gauge / 10)  # 1000 스케일을 100%로 변환
                filled = "█" * (atb_percent // 10)
                empty = "░" * (10 - atb_percent // 10)
                if atb_gauge >= 750:  # 75% = 750/1000
                    atb_bar = f"[{Color.CYAN}{filled}{Color.RESET}{empty}]"
                    atb_status = f"{Color.CYAN}{atb_percent:3}%{Color.RESET}"
                else:
                    atb_bar = f"[{Color.BLUE}{filled}{Color.RESET}{empty}]"
                    atb_status = f"{Color.BLUE}{atb_percent:3}%{Color.RESET}"
            
            # 현재 캐릭터 표시
            current_marker = f" ⚡ " if char == current_char else "   "
            
            # 레벨 표시 추가
            level_display = f"Lv.{getattr(char, 'level', 1):2}"
            
            # 첫 번째 줄: 이름, 레벨, HP/MP/BRV
            name_line = f"{current_marker}{name_color}{char.name[:12]:12}{Color.RESET} {Color.BRIGHT_WHITE}{level_display}{Color.RESET}"
            stats_line = f"HP:{hp_color}{char.current_hp:3}/{char.max_hp:3}{Color.RESET} MP:{mp_color}{char.current_mp:3}/{char.max_mp:3}{Color.RESET} BRV:{Color.YELLOW}{char.brave_points:4}{Color.RESET}"
            
            # 두 번째 줄: ATB 게이지 (퍼센트/READY를 오른쪽으로)
            atb_line = f"       ATB: {atb_bar}   {atb_status}"
            
            print(f"{name_line} {stats_line}")
            print(atb_line)
            print()  # 공백 줄로 구분
        
        # 적 표시 (세로 정렬된 ATB)
        print(f"\n👹 적군:")
        print("-" * 65)
        for enemy in enemies:
            if not enemy.is_alive:
                continue
                
            name_color = Color.BRIGHT_RED if enemy == current_char else Color.WHITE
            
            # 상태
            status = ""
            if hasattr(enemy, 'is_broken') and enemy.is_broken:
                status = f"{Color.BRIGHT_RED}[BREAK]{Color.RESET}"
            
            # HP 상태
            hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
            hp_color = Color.BRIGHT_GREEN if hp_ratio > 0.7 else Color.BRIGHT_YELLOW if hp_ratio > 0.3 else Color.BRIGHT_RED
            
            # ATB 게이지
            atb_gauge = getattr(enemy, 'atb_gauge', 0)
            if atb_gauge >= 1000:
                atb_bar = f"[{Color.BRIGHT_CYAN}██████████{Color.RESET}]"
                atb_status = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
            else:
                atb_percent = int(atb_gauge / 10)  # 1000 스케일을 100%로 변환
                filled = "█" * (atb_percent // 10)
                empty = "░" * (10 - atb_percent // 10)
                if atb_gauge >= 750:  # 75% = 750/1000
                    atb_bar = f"[{Color.CYAN}{filled}{Color.RESET}{empty}]"
                    atb_status = f"{Color.CYAN}{atb_percent:3}%{Color.RESET}"
                else:
                    atb_bar = f"[{Color.BLUE}{filled}{Color.RESET}{empty}]"
                    atb_status = f"{Color.BLUE}{atb_percent:3}%{Color.RESET}"
            
            # 현재 적 표시
            current_marker = f" ⚡ " if enemy == current_char else "   "
            
            # 레벨 표시 추가
            level_display = f"Lv.{getattr(enemy, 'level', 1):2}"
            
            # 첫 번째 줄: 이름, 레벨과 HP/BRV
            name_line = f"{current_marker}{name_color}{enemy.name[:15]:15}{Color.RESET} {Color.BRIGHT_WHITE}{level_display}{Color.RESET}"
            stats_line = f"HP:{hp_color}{enemy.current_hp:3}/{enemy.max_hp:3}{Color.RESET} BRV:{Color.YELLOW}{enemy.brave_points:4}{Color.RESET}"
            
            # 두 번째 줄: ATB 게이지 (퍼센트/READY를 오른쪽으로)
            atb_line = f"       ATB: {atb_bar}   {atb_status}"
            
            print(f"{name_line} {stats_line}")
            print(atb_line)
            print()  # 공백 줄로 구분
        
        print("=" * max_width)
    
    def show_attack_effect(self, attacker, target, damage: int, effect_type: EffectType, skill_name: str = None):
        """공격 이펙트 표시 - 안정적인 버전"""
        # attacker와 target이 유효한 객체인지 확인
        if not hasattr(attacker, 'name') or not hasattr(target, 'name'):
            return  # name 속성이 없으면 출력하지 않음
            
        color = self.effect_colors.get(effect_type, Color.WHITE)
        attacker_sprite = self.get_character_sprite(attacker)
        target_sprite = self.get_character_sprite(target)
        
        # 이펙트 간소화
        if effect_type == EffectType.PHYSICAL_ATTACK:
            effect_icon = "⚔️"
            action_text = f"{skill_name}" if skill_name else "공격"
        elif effect_type == EffectType.MAGIC_ATTACK:
            effect_icon = "✨"
            action_text = f"{skill_name}" if skill_name else "마법"
        elif effect_type == EffectType.CRITICAL:
            effect_icon = "💥"
            action_text = "크리티컬"
        elif effect_type == EffectType.HEAL:
            effect_icon = "💚"
            action_text = "치료"
        elif effect_type == EffectType.DEFEND:
            effect_icon = "🛡️"
            action_text = "방어"
        else:
            effect_icon = "✨"
            action_text = skill_name or "행동"
        
        # 간단한 이펙트 출력 (로그 제거)
        # print(f"\n{color}{Color.BOLD}")
        # action_line = f"{attacker_sprite} {attacker.name} {effect_icon} {action_text} → {target_sprite} {target.name}"
        # print(f"  {action_line}")
        
        # 데미지/효과 표시 (로그 제거)
        # if damage > 0:
        #     damage_color = Color.BRIGHT_RED if effect_type == EffectType.CRITICAL else Color.RED
        #     print(f"  {damage_color}💢 {damage} 데미지!{Color.RESET}")
        # elif effect_type == EffectType.HEAL and damage < 0:
        #     print(f"  {Color.BRIGHT_GREEN}💚 {-damage} 회복!{Color.RESET}")
        
        # print(f"{Color.RESET}")
        
        # 짧은 대기 시간
        time.sleep(0.5)
    
    def show_skill_effect(self, caster, skill_name: str, effect_type: EffectType):
        """스킬 이펙트 표시 - 간소화 버전"""
        # caster가 유효한 객체인지 확인
        if not hasattr(caster, 'name'):
            return  # name 속성이 없으면 출력하지 않음
            
        color = self.effect_colors.get(effect_type, Color.BRIGHT_MAGENTA)
        caster_sprite = self.get_character_sprite(caster)
        
        # 스킬별 아이콘
        skill_icons = {
            '월광베기': '🌙⚔️',
            '별빛폭발': '⭐💥',
            '신성한보호': '🛡️✨',
            '독날': '🗡️☠️',
            '치유의빛': '💚✨',
            '그림자은신': '👤💨'
        }
        
        icon = skill_icons.get(skill_name, '✨')
        
        print(f"\n{color}{Color.BOLD}")
        print(f"  {caster_sprite} {caster.name} - {icon} {skill_name}")
        print(f"{Color.RESET}")
        
        # 짧은 대기
        time.sleep(0.3)
    
    def show_brave_change(self, character, old_brave: int, new_brave: int):
        """Brave 포인트 변화 표시 - 간소화"""
        # character가 유효한 객체인지 확인
        if not hasattr(character, 'name'):
            return  # name 속성이 없으면 출력하지 않음
            
        change = new_brave - old_brave
        sprite = self.get_character_sprite(character)
        
        if change > 0:
            color = Color.BRIGHT_YELLOW
            symbol = ""  # "+" 기호 제거
            effect = "💰"
            print(f"  {color}{sprite} {character.name} {effect} Brave: {change} → {new_brave}{Color.RESET}")
        elif change < 0:
            color = Color.BRIGHT_RED
            symbol = ""
            effect = "💸"
            # HP 공격의 경우 특별 처리 (전체 소모)
            if old_brave > new_brave and old_brave > 1000:
                print(f"  {color}{sprite} {character.name} {effect} Brave: {old_brave} → 0{Color.RESET}")
            else:
                # 음수 값을 절댓값으로 표시
                abs_change = abs(change)
                print(f"  {color}{sprite} {character.name} {effect} Brave: {abs_change} → {new_brave}{Color.RESET}")
        # change가 0이면 출력하지 않음
    
    def show_status_change(self, character, status_name: str, is_positive: bool = True):
        """상태 변화 표시 - 간소화"""
        # character가 유효한 객체인지 확인
        if not hasattr(character, 'name'):
            return  # name 속성이 없으면 출력하지 않음
            
        sprite = self.get_character_sprite(character)
        color = Color.BRIGHT_GREEN if is_positive else Color.BRIGHT_RED
        effect = "✨" if is_positive else "💀"
        
        print(f"  {color}{sprite} {character.name} {effect} {status_name}{Color.RESET}")
    
    def show_miss_effect(self, attacker, target):
        """회피 효과 표시 - 중복 메시지 방지를 위해 비주얼 효과만"""
        # brave_combat.py에서 이미 회피 메시지를 출력하므로 여기서는 생략
        # 필요시 추가 비주얼 효과만 처리
        time.sleep(0.3)
    
    def clear_screen(self):
        """화면 지우기"""
        import os
        # 파이프/모바일 모드에서는 하드 클리어 금지 (깜빡임/검은 화면 방지)
        if os.getenv('SUBPROCESS_MODE') == '1':
            print("\n")
            return
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_death_effect(self, character):
        """사망 효과 표시"""
        if not hasattr(character, 'name'):
            return
            
        sprite = self.get_character_sprite(character)
        print(f"  {Color.BRIGHT_BLACK}💀 {sprite} {character.name}이(가) 쓰러졌습니다!{Color.RESET}")
        time.sleep(0.5)

# 전역 인스턴스
combat_visualizer = CombatVisualizer()

def get_combat_visualizer():
    """전투 비주얼라이저 인스턴스 반환"""
    return combat_visualizer
