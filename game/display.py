"""
게임 디스플레이 시스템
ASCII 기반 그래픽 표시
"""

from typing import List
import os
import platform
from .character import Character, PartyManager
from .world import GameWorld
from .color_text import *


class GameDisplay:
    """게임 화면 표시 클래스"""
    
    def __init__(self):
        self.screen_width = 120  # 화면 너비 증가
        self.screen_height = 35  # 화면 높이 증가
        
    def clear_screen(self):
        """화면 지우기"""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
            
    def show_title(self):
        """타이틀 화면 표시 (글꼴 호환성 개선)"""
        self.clear_screen()
        
        # 터미널 설정 안내
        print("=" * 70)
        print("   DAWN OF STELLAR - 별빛의 여명")
        print("=" * 70)
        print()
        print("  최적의 게임 환경을 위한 터미널 설정 안내:")
        print("  • Windows: 설정 > 글꼴에서 'Consolas' 또는 'Courier New' 선택")
        print("  • PowerShell: 속성 > 글꼴 > 'Consolas' 권장")
        print("  • CMD: 속성 > 글꼴 > 'Consolas' 또는 래스터 글꼴")
        print("  • 터미널 크기: 최소 120x30 권장")
        print()
        
        title_art = """
══════════════════════════════════════════════════════════════════════════
                                                                          
                          DAWN OF STELLAR                                
                             별빛의 여명                                    
                                                                       
                        전술 로그라이크 게임                                                                                  
                                                                          
══════════════════════════════════════════════════════════════════════════
        """
        print(title_art)
        print("\n" + "="*60)
        print("게임을 시작합니다...")
        input("Enter 키를 눌러 계속...")
        
    def show_game_screen(self, party_manager: PartyManager, world: GameWorld):
        """메인 게임 화면 표시 - 간소화된 버전"""
        self.clear_screen()
        
        # 안전한 너비 설정
        safe_width = min(80, self.screen_width)
        
        # 상단 정보 표시
        title = f"던전 {world.current_level}층 - Dawn Of Stellar"
        title_padding = (safe_width - len(title)) // 2
        print(f"{' ' * title_padding}{bright_cyan(title)}")
        print()
        
        # 던전 맵 표시 (색상 적용)
        map_display = world.get_colored_map_display(min(30, safe_width - 4), 15)  # 색상 맵 사용
        for line in map_display:
            # 줄 길이 제한 (색상 코드 때문에 실제 길이와 표시 길이가 다를 수 있음)
            print(f"  {line}")
            
        print()
        
        # 파티 상태 정보 - 간소화 (중복 제거)
        alive_count = len(party_manager.get_alive_members())
        total_count = len(party_manager.members)
        
        party_info = f"파티: {alive_count}/{total_count}명 생존 | 층: {world.current_level} | 골드: {party_manager.party_gold}G"
        
        # 파티 전체 무게 정보 추가 (개별 인벤토리 합계)
        total_weight = 0.0
        max_weight = 0.0
        for member in party_manager.members:
            if hasattr(member, 'inventory'):
                total_weight += member.inventory.get_total_weight()
                max_weight += member.inventory.max_weight
        
        weight_ratio = total_weight / max_weight if max_weight > 0 else 0
        if weight_ratio >= 0.9:
            weight_color = red
            weight_emoji = "🧳"
        elif weight_ratio >= 0.7:
            weight_color = yellow
            weight_emoji = "🎒"
        else:
            weight_color = green
            weight_emoji = "🎒"
        
        weight_info = f" | {weight_emoji}무게: {weight_color(f'{total_weight:.1f}/{max_weight:.1f}kg')}"
        
        print(f"  {party_info}{weight_info}")
        print("+" + "-" * (safe_width - 2) + "+")
        
        # 파티원 상태 (깔끔하게 정리)
        for i, member in enumerate(party_manager.members[:4]):  # 최대 4명만 표시
            if member.is_alive:
                # HP/MP 비율 계산
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                
                # HP 색상과 이모지 계산
                if hp_ratio >= 0.8:
                    hp_color = bright_green
                    hp_emoji = "💚"
                elif hp_ratio >= 0.6:
                    hp_color = green
                    hp_emoji = "💛"
                elif hp_ratio >= 0.4:
                    hp_color = yellow
                    hp_emoji = "🧡"
                elif hp_ratio >= 0.2:
                    hp_color = bright_red
                    hp_emoji = "❤️"
                else:
                    hp_color = red
                    hp_emoji = "💔"
                
                # MP 색상과 이모지 계산
                if mp_ratio >= 0.8:
                    mp_color = bright_cyan
                    mp_emoji = "💙"
                elif mp_ratio >= 0.6:
                    mp_color = cyan
                    mp_emoji = "💙"
                elif mp_ratio >= 0.4:
                    mp_color = blue
                    mp_emoji = "💙"
                elif mp_ratio >= 0.2:
                    mp_color = magenta
                    mp_emoji = "💜"
                else:
                    mp_color = red
                    mp_emoji = "❤️"
                
                # 이름과 직업 표시 (직업별 이모지 추가)
                class_emoji = {
                    # 기본 직업
                    "전사": "⚔️", "마법사": "🔮", "도둑": "🗡️", "성직자": "✨",
                    "궁수": "🏹", "사무라이": "🗾", "드루이드": "🌿", "정령술사": "💫",
                    "네크로맨서": "💀", "팔라딘": "🛡️", "어쌔신": "🥷", "바드": "🎵",
                    
                    # 확장 직업
                    "성기사": "🛡️", "암흑기사": "🖤", "몽크": "👊", "용기사": "🐉",
                    "검성": "⚡", "암살자": "🗡️", "기계공학자": "🔧", "무당": "🔯",
                    "해적": "☠️", "철학자": "📚", "시간술사": "⏰", "연금술사": "⚗️",
                    "검투사": "🏟️", "기사": "🐎", "신관": "⛪", "마검사": "🌟",
                    "차원술사": "🌀", "시인": "📜", "학자": "🎓", "상인": "💰",
                    "광전사": "😤", "무희": "💃", "점성술사": "🔮", "영매": "👻",
                    "흑기사": "⚫", "현자": "🧙"
                }.get(member.character_class, "👤")
                
                name_class = f"{class_emoji} {member.name[:8]:8} ({member.character_class[:6]:6})"
                
                # 상처 시스템 정보
                wounds_info = ""
                if hasattr(member, 'wounds') and member.wounds > 0:
                    wound_ratio = member.wounds / member.max_hp if member.max_hp > 0 else 0
                    if wound_ratio >= 0.5:
                        wounds_info = f" {red('🩸 중상:' + str(member.wounds))}"
                    elif wound_ratio >= 0.3:
                        wounds_info = f" {yellow('🩹 경상:' + str(member.wounds))}"
                    else:
                        wounds_info = f" {bright_red('상처:' + str(member.wounds))}"
                
                # 최종 상태 라인
                hp_text = f"{hp_emoji}HP:{hp_color(f'{member.current_hp:3}/{member.max_hp:3}')}"
                mp_text = f"{mp_emoji}MP:{mp_color(f'{member.current_mp:2}/{member.max_mp:2}')}"
                status_line = f"  {name_class} {hp_text} {mp_text}{wounds_info}"
                print(f"  {status_line}")
            else:
                # 사망한 파티원
                class_emoji = {
                    # 기본 직업
                    "전사": "⚔️", "마법사": "🔮", "도둑": "🗡️", "성직자": "✨",
                    "궁수": "🏹", "사무라이": "🗾", "드루이드": "🌿", "정령술사": "💫",
                    "네크로맨서": "💀", "팔라딘": "🛡️", "어쌔신": "🥷", "바드": "🎵",
                    
                    # 확장 직업
                    "성기사": "🛡️", "암흑기사": "🖤", "몽크": "👊", "용기사": "🐉",
                    "검성": "⚡", "암살자": "🗡️", "기계공학자": "🔧", "무당": "🔯",
                    "해적": "☠️", "철학자": "📚", "시간술사": "⏰", "연금술사": "⚗️",
                    "검투사": "🏟️", "기사": "🐎", "신관": "⛪", "마검사": "🌟",
                    "차원술사": "🌀", "시인": "📜", "학자": "🎓", "상인": "💰",
                    "광전사": "😤", "무희": "💃", "점성술사": "🔮", "영매": "👻",
                    "흑기사": "⚫", "현자": "🧙"
                }.get(member.character_class, "👤")
                
                name_class = f"{class_emoji} {member.name[:8]:8} ({member.character_class[:6]:6})"
                status_line = f"  {name_class} {red('💀 사망')}"
                print(f"  {status_line}")
        
        print("+" + "-" * (safe_width - 2) + "+")
        
    def show_party_status(self, party_manager: PartyManager):
        """상세 파티 상태 표시"""
        print("\n" + bright_cyan("="*90, True))
        print(bright_cyan("=== 🎭 파티 상태 ===", True))
        print(bright_cyan("="*90, True))
        
        for i, member in enumerate(party_manager.members, 1):
            # 직업별 이모지
            class_emoji = {
                # 기본 직업
                "전사": "⚔️", "마법사": "🔮", "도둑": "🗡️", "성직자": "✨",
                "궁수": "🏹", "사무라이": "🗾", "드루이드": "🌿", "정령술사": "💫",
                "네크로맨서": "💀", "팔라딘": "🛡️", "어쌔신": "🥷", "바드": "🎵",
                
                # 확장 직업
                "성기사": "🛡️", "암흑기사": "🖤", "몽크": "👊", "용기사": "🐉",
                "검성": "⚡", "암살자": "🗡️", "기계공학자": "🔧", "무당": "🔯",
                "해적": "☠️", "철학자": "📚", "시간술사": "⏰", "연금술사": "⚗️",
                "검투사": "🏟️", "기사": "🐎", "신관": "⛪", "마검사": "🌟",
                "차원술사": "🌀", "시인": "📜", "학자": "🎓", "상인": "💰",
                "광전사": "😤", "무희": "💃", "점성술사": "🔮", "영매": "👻",
                "흑기사": "⚫", "현자": "🧙"
            }.get(member.character_class, "👤")
            
            # 생존 상태에 따른 표시
            if member.is_alive:
                print(f"\n[{bright_yellow(str(i))}] {class_emoji} {bright_white(member.name)} - {green(member.character_class)}")
                
                # HP/MP 비율과 색상
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                
                # HP 상태
                if hp_ratio >= 0.8:
                    hp_display = f"💚 HP {bright_green(f'{member.current_hp}/{member.max_hp}')}"
                elif hp_ratio >= 0.6:
                    hp_display = f"💛 HP {yellow(f'{member.current_hp}/{member.max_hp}')}"
                elif hp_ratio >= 0.4:
                    hp_display = f"🧡 HP {yellow(f'{member.current_hp}/{member.max_hp}')}"
                elif hp_ratio >= 0.2:
                    hp_display = f"❤️ HP {bright_red(f'{member.current_hp}/{member.max_hp}')}"
                else:
                    hp_display = f"💔 HP {red(f'{member.current_hp}/{member.max_hp}')}"
                
                # MP 색상과 이모지 계산
                if mp_ratio >= 0.8:
                    mp_display = f"💙 MP {bright_cyan(f'{member.current_mp}/{member.max_mp}')}"
                elif mp_ratio >= 0.6:
                    mp_display = f"💙 MP {cyan(f'{member.current_mp}/{member.max_mp}')}"
                elif mp_ratio >= 0.4:
                    mp_display = f"💙 MP {blue(f'{member.current_mp}/{member.max_mp}')}"
                elif mp_ratio >= 0.2:
                    mp_display = f"💜 MP {magenta(f'{member.current_mp}/{member.max_mp}')}"
                else:
                    mp_display = f"❤️ MP {red(f'{member.current_mp}/{member.max_mp}')}"
                
                print(f"    HP: {hp_display} | MP: {mp_display}")
            else:
                print(f"\n[{bright_yellow(str(i))}] {class_emoji} {red(member.name)} - {red(member.character_class)} {red('💀 사망')}")
            
            # 상세 정보 (색상 적용)
            atk_color = bright_green if member.physical_attack >= 50 else green if member.physical_attack >= 30 else white
            def_color = bright_blue if member.physical_defense >= 50 else blue if member.physical_defense >= 30 else white
            mag_atk_color = bright_magenta if member.magic_attack >= 50 else magenta if member.magic_attack >= 30 else white
            mag_def_color = bright_cyan if member.magic_defense >= 50 else cyan if member.magic_defense >= 30 else white
            
            print(f"    ⚔️ 물리: ATK {atk_color(str(member.physical_attack))} / DEF {def_color(str(member.physical_defense))} | "
                  f"🔮 마법: ATK {mag_atk_color(str(member.magic_attack))} / DEF {mag_def_color(str(member.magic_defense))} | "
                  f"✨ 경험치: {bright_yellow(str(member.experience))}")
            
            # 통합 인벤토리 정보 (첫 번째 멤버에게만 표시)
            if i == 1 and hasattr(party_manager, 'shared_inventory'):
                current_weight = party_manager.get_current_carry_weight()
                max_weight = party_manager.get_total_carry_capacity()
                weight_ratio = current_weight / max_weight if max_weight > 0 else 0
                
                if weight_ratio >= 0.9:
                    weight_display = f"🧳 {red(f'{current_weight:.1f}/{max_weight:.1f}kg')} {red('과부하!')}"
                elif weight_ratio >= 0.7:
                    weight_display = f"🎒 {yellow(f'{current_weight:.1f}/{max_weight:.1f}kg')} {yellow('무거움')}"
                else:
                    weight_display = f"🎒 {green(f'{current_weight:.1f}/{max_weight:.1f}kg')} {green('양호')}"
                
                item_count = len(party_manager.shared_inventory.items) if hasattr(party_manager.shared_inventory, 'items') else 0
                print(f"    💼 파티 인벤토리: {weight_display} | 📦 아이템: {bright_cyan(str(item_count))}개")
                  
            # 특성 정보
            if hasattr(member, 'active_traits') and member.active_traits:
                print(f"    🌟 특성:")
                for trait in member.active_traits[:3]:  # 최대 3개까지 표시
                    if hasattr(trait, 'name') and hasattr(trait, 'description'):
                        # 특성 이름을 청록색으로, 설명을 흰색으로 표시
                        print(f"      • {bright_cyan(trait.name)}: {white(trait.description)}")
                    elif hasattr(trait, 'name'):
                        print(f"      • {bright_cyan(trait.name)}")
                    else:
                        print(f"      • {white(str(trait))}")
                
                # 3개 초과시 추가 특성 개수 표시
                if len(member.active_traits) > 3:
                    remaining = len(member.active_traits) - 3
                    print(f"      {bright_black(f'... 외 {remaining}개 특성 보유')}")
                
            # HP 상태 세부사항
            if member.is_alive:
                hp_percentage = (member.current_hp / member.limited_max_hp * 100) if member.limited_max_hp > 0 else 0
                wound_percentage = (member.wounds / member.max_hp * 100) if member.max_hp > 0 else 0
                
                if hp_percentage >= 80:
                    hp_status = bright_green(f"{hp_percentage:.1f}%")
                elif hp_percentage >= 60:
                    hp_status = yellow(f"{hp_percentage:.1f}%")
                elif hp_percentage >= 40:
                    hp_status = yellow(f"{hp_percentage:.1f}%")
                else:
                    hp_status = bright_red(f"{hp_percentage:.1f}%")
                
                print(f"    💗 HP 상태: {hp_status}", end="")
                
                if member.wounds > 0:
                    if wound_percentage >= 50:
                        wound_status = red(f" | 🩸 중상: {wound_percentage:.1f}%")
                    elif wound_percentage >= 30:
                        wound_status = yellow(f" | 🩹 경상: {wound_percentage:.1f}%")
                    else:
                        wound_status = bright_red(f" | 상처: {wound_percentage:.1f}%")
                    
                    print(wound_status)
                    print(f"      상처로 인한 최대 HP 감소: {red(str(member.wounds))} ({member.max_hp} → {bright_red(str(member.limited_max_hp))})")
                else:
                    print(f" | 🌟 {bright_green('상처 없음')}")
                
        print("\n" + bright_cyan("="*90, True))
        input(bright_white("Enter 키를 눌러 계속...", True))
        
    def show_minimap(self, world: GameWorld, size: int = 5):
        """미니맵 표시"""
        player_x, player_y = world.player_pos
        
        print(f"\n미니맵 (주변 {size}x{size} 영역):")
        print("┌" + "─" * (size * 2 + 1) + "┐")
        
        for dy in range(-size//2, size//2 + 1):
            line = "│ "
            for dx in range(-size//2, size//2 + 1):
                x, y = player_x + dx, player_y + dy
                
                if dx == 0 and dy == 0:
                    line += "@"  # 플레이어
                elif world.is_valid_pos(x, y):
                    line += world.get_tile_char(x, y)
                else:
                    line += " "
                    
                line += " "
            line += "│"
            print(line)
            
        print("└" + "─" * (size * 2 + 1) + "┘")
        
    def show_ascii_art(self, art_type: str):
        """ASCII 아트 표시"""
        arts = {
            "sword": [
                "    /|",
                "   / |",
                "  /__|__",
                " |    |",
                " |    |",
                " |____|"
            ],
            "shield": [
                "  ╭─────╮",
                " ╱       ╲",
                "│   ┌─┐   │",
                "│   │ │   │",
                " ╲ ╱   ╲ ╱",
                "  ╰─────╯"
            ],
            "potion": [
                "   ╭─╮",
                "   │ │",
                "  ╭─┴─╮",
                " ╱     ╲",
                "│ ☆ ☆ ☆ │",
                " ╲     ╱",
                "  ╰───╯"
            ]
        }
        
        if art_type in arts:
            for line in arts[art_type]:
                print(line)
                
    def show_damage_effect(self, damage: int, is_critical: bool = False):
        """데미지 이펙트 표시"""
        if is_critical:
            print(f"    ★ CRITICAL! {damage} ★")
        else:
            print(f"    -{damage}")
            
    def show_heal_effect(self, heal_amount: int):
        """회복 이펙트 표시"""
        print(f"    +{heal_amount} HP ♥")
        
    def draw_progress_bar(self, current: int, maximum: int, length: int = 20, 
                         filled_char: str = "█", empty_char: str = "░") -> str:
        """진행률 바 그리기"""
        if maximum == 0:
            return f"[{empty_char * length}]"
            
        filled_length = int((current / maximum) * length)
        bar = filled_char * filled_length + empty_char * (length - filled_length)
        return f"[{bar}]"
        
    def show_level_up_effect(self, character: Character, old_level: int):
        """레벨업 이펙트"""
        print("\n" + "="*50)
        print(f"    ★ LEVEL UP! ★")
        print(f"    {character.name}: Lv.{old_level} → Lv.{character.level}")
        print("="*50)
        
    def show_status_effects(self, character: Character):
        """상태 이상 효과 표시"""
        effects = []
        
        # 상처 상태
        if character.wounds > 0:
            wound_ratio = character.wounds / character.max_hp
            if wound_ratio > 0.5:
                effects.append("중상")
            elif wound_ratio > 0.25:
                effects.append("경상")
                
        # ATB 상태
        if character.atb_gauge >= 100:
            effects.append("행동가능")
        elif character.atb_gauge >= 75:
            effects.append("준비중")
            
        if effects:
            effect_str = " | ".join(effects)
            print(f"    상태: {effect_str}")
            
    def format_number(self, number: int) -> str:
        """숫자 포맷팅 (3자리마다 콤마)"""
        return f"{number:,}"
        
    def show_inventory_grid(self, items: List, grid_width: int = 8):
        """인벤토리 그리드 표시"""
        print("+" + "---+" * grid_width)
        
        for row in range((len(items) + grid_width - 1) // grid_width):
            line = "|"
            for col in range(grid_width):
                idx = row * grid_width + col
                if idx < len(items):
                    item_char = items[idx].get_display_char() if hasattr(items[idx], 'get_display_char') else "?"
                    line += f" {item_char} |"
                else:
                    line += "   |"
            print(line)
            
            if row < (len(items) + grid_width - 1) // grid_width - 1:
                print("+" + "---+" * grid_width)
                
        print("+" + "---+" * grid_width)

    def show_main_menu(self):
        """메인 메뉴 표시"""
        self.clear_screen()
        
        # 게임 로고 및 메뉴
        print("\n" + "="*60)
        print("             🌟 DAWN OF STELLAR 🌟")
        print("                별빛의 여명")
        print("="*60)
        
        print("\n" + bright_cyan("🎮 로그라이크 던전 탐험 게임", True))
        print(f"   {yellow('⚔️')} 전술적 ATB 전투 시스템")
        print(f"   {green('👥')} 4인 파티 관리")
        print(f"   {blue('🏰')} 무한 던전 탐험")
        
        print("\n" + bright_white("게임이 곧 시작됩니다...", True))
