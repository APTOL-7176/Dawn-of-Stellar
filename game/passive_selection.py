#!/usr/bin/env python3
"""
패시브 특성 선택 시스템
"""

from typing import List, Dict, Any
from .character import Character, CharacterClassManager

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'

class PassiveSelectionSystem:
    """패시브 특성 선택 시스템"""
    
    def __init__(self):
        self.selected_passives = {}  # 캐릭터별 선택된 패시브 저장
    
    def select_passives_for_party(self, party: List[Character]) -> bool:
        """파티 전체의 패시브 선택"""
        print(f"\n{BOLD}{CYAN}=== 패시브 특성 선택 ==={RESET}")
        print(f"{YELLOW}각 캐릭터마다 2개의 특성을 선택할 수 있습니다.{RESET}\n")
        
        for character in party:
            if not self._select_character_passives(character):
                return False
        
        print(f"\n{GREEN}모든 캐릭터의 패시브 선택이 완료되었습니다!{RESET}\n")
        return True
    
    def _select_character_passives(self, character: Character) -> bool:
        """개별 캐릭터의 패시브 선택"""
        while True:
            character.display_available_traits()
            
            try:
                print(f"{WHITE}선택할 특성 번호를 입력하세요 (1-5, 최대 2개, 쉼표로 구분):")
                print(f"예: 1,3 또는 2,5{RESET}")
                user_input = input(f"{CYAN}>>> {RESET}").strip()
                
                if not user_input:
                    print(f"{RED}번호를 입력해주세요.{RESET}")
                    continue
                
                # 입력 파싱
                try:
                    indices = [int(x.strip()) - 1 for x in user_input.split(',')]
                except ValueError:
                    print(f"{RED}올바른 번호를 입력해주세요.{RESET}")
                    continue
                
                # 패시브 선택 시도
                if character.select_passive_traits(indices):
                    self.selected_passives[character.name] = character.active_traits
                    print(f"\n{GREEN}✓ {character.name}의 패시브 선택 완료{RESET}")
                    
                    # 선택된 특성들을 자세히 표시하는 확인창
                    self._show_selection_confirmation(character)
                    
                    # 커서 메뉴로 확인 옵션 제공
                    if self._confirm_selection_with_cursor(character):
                        print(f"\n{GREEN}🎉 {character.name}의 특성 선택이 확정되었습니다!{RESET}")
                        input(f"{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
                        return True
                    else:
                        # 선택 초기화하고 다시
                        character.active_traits = []
                        print(f"\n{YELLOW}선택을 초기화합니다. 다시 선택해주세요.{RESET}")
                        continue
                        
            except KeyboardInterrupt:
                print(f"\n{RED}선택이 취소되었습니다.{RESET}")
                return False
            except Exception as e:
                print(f"{RED}오류가 발생했습니다: {e}{RESET}")
                continue
    
    def _show_selection_confirmation(self, character: Character):
        """선택된 특성들을 확인창으로 표시"""
        print(f"\n{BOLD}{GREEN}{'='*60}{RESET}")
        print(f"{BOLD}{WHITE}🎯 {character.name}의 선택된 특성{RESET}")
        print(f"{BOLD}{GREEN}{'='*60}{RESET}")
        
        for i, trait in enumerate(character.active_traits, 1):
            # 특성 타입에 따른 아이콘
            if trait.effect_type == "passive":
                icon = "🛡️"
            elif trait.effect_type == "trigger":
                icon = "⚡"
            elif trait.effect_type == "active":
                icon = "🔥"
            else:
                icon = "✨"
            
            print(f"{CYAN}{i}. {icon} {BOLD}{trait.name}{RESET}")
            print(f"   {WHITE}└─ {trait.description}{RESET}")
            
            # 효과 분석
            effect_hints = []
            effect_str = str(trait.effect_value)
            
            if "damage" in effect_str.lower():
                effect_hints.append("⚔️ 공격력 관련")
            if "defense" in effect_str.lower():
                effect_hints.append("🛡️ 방어력 관련")
            if "crit" in effect_str.lower():
                effect_hints.append("💥 크리티컬 관련")
            if "heal" in effect_str.lower():
                effect_hints.append("💚 회복 관련")
            if "speed" in effect_str.lower():
                effect_hints.append("💨 속도 관련")
            
            if effect_hints:
                print(f"   {MAGENTA}   ({' | '.join(effect_hints)}){RESET}")
            print()
        
        print(f"{YELLOW}총 {len(character.active_traits)}개의 특성이 선택되었습니다.{RESET}")
    
    def _confirm_selection_with_cursor(self, character: Character) -> bool:
        """커서 메뉴로 선택 확인"""
        try:
            # CursorMenu import 시도
            from .cursor_menu_system import CursorMenu
            
            print(f"\n{CYAN}{'='*50}{RESET}")
            print(f"{YELLOW}이 선택으로 확정하시겠습니까?{RESET}")
            print(f"{CYAN}{'='*50}{RESET}")
            
            options = [
                "✅ 확정하기",
                "🔄 다시 선택하기",
                "📋 선택 내용 다시 보기"
            ]
            descriptions = [
                f"{character.name}의 특성 선택을 확정합니다",
                "선택을 초기화하고 다시 선택합니다",
                "선택된 특성들을 다시 확인합니다"
            ]
            
            menu = CursorMenu("🎯 특성 선택 확인", options, descriptions, clear_screen=False)
            
            while True:
                choice = menu.run()
                
                if choice == 0:  # 확정하기
                    return True
                elif choice == 1:  # 다시 선택하기
                    return False
                elif choice == 2:  # 선택 내용 다시 보기
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self._show_selection_confirmation(character)
                    print(f"\n{CYAN}{'='*50}{RESET}")
                    print(f"{YELLOW}이 선택으로 확정하시겠습니까?{RESET}")
                    print(f"{CYAN}{'='*50}{RESET}")
                    continue
                else:  # 취소 또는 기타
                    return False
                    
        except ImportError:
            # CursorMenu를 사용할 수 없는 경우 기존 방식 사용
            print(f"\n{CYAN}{'='*50}{RESET}")
            print(f"{YELLOW}이 선택으로 확정하시겠습니까?{RESET}")
            print(f"{WHITE}Y: 확정 | N: 다시 선택{RESET}")
            print(f"{CYAN}{'='*50}{RESET}")
            confirm = input(f"{CYAN}>>> {RESET}").strip().lower()
            return confirm in ['y', 'yes', '예', 'ㅇ']
    
    def display_party_passives(self, party: List[Character]):
        """파티 전체의 선택된 패시브 표시"""
        print(f"\n{BOLD}{CYAN}=== 파티 패시브 현황 ==={RESET}")
        
        for character in party:
            print(f"\n{WHITE}{character.name} ({character.character_class}):{RESET}")
            
            if character.active_traits:
                for i, trait in enumerate(character.active_traits, 1):
                    print(f"  {GREEN}{i}. {trait.name}{RESET}")
                    print(f"     {trait.description}")
            else:
                print(f"  {RED}선택된 패시브가 없습니다{RESET}")
        
        print()
    
    def get_passive_effects_summary(self, character: Character) -> Dict[str, Any]:
        """캐릭터의 패시브 효과 요약"""
        summary = {
            "passive_names": [trait.name for trait in character.active_traits],
            "combat_effects": {},
            "stat_bonuses": {}
        }
        
        for trait in character.active_traits:
            effect_value = trait.effect_value
            
            # 전투 효과 분석
            if "damage_multiplier" in str(effect_value):
                summary["combat_effects"]["damage_boost"] = True
            if "defense_bonus" in str(effect_value):
                summary["combat_effects"]["defense_boost"] = True
            if "crit_chance_bonus" in str(effect_value):
                summary["combat_effects"]["crit_boost"] = True
            if "dodge_bonus" in str(effect_value):
                summary["combat_effects"]["evasion_boost"] = True
            if "heal_on_attack" in str(effect_value):
                summary["combat_effects"]["healing"] = True
            if "life_steal" in str(effect_value):
                summary["combat_effects"]["life_steal"] = True
        
        return summary
    
    def save_passive_selections(self, filename: str = "passive_selections.json"):
        """패시브 선택 사항 저장"""
        import json
        
        save_data = {}
        for char_name, traits in self.selected_passives.items():
            save_data[char_name] = [
                {
                    "name": trait.name,
                    "description": trait.description,
                    "effect_type": trait.effect_type,
                    "effect_value": trait.effect_value
                }
                for trait in traits
            ]
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            print(f"{GREEN}패시브 선택 사항이 저장되었습니다: {filename}{RESET}")
        except Exception as e:
            print(f"{RED}저장 실패: {e}{RESET}")
    
    def load_passive_selections(self, party: List[Character], filename: str = "passive_selections.json"):
        """저장된 패시브 선택 사항 로드"""
        import json
        from .character import CharacterTrait
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            for character in party:
                if character.name in save_data:
                    character.active_traits = []
                    for trait_data in save_data[character.name]:
                        trait = CharacterTrait(
                            trait_data["name"],
                            trait_data["description"],
                            trait_data["effect_type"],
                            trait_data["effect_value"]
                        )
                        character.active_traits.append(trait)
                    
                    self.selected_passives[character.name] = character.active_traits
            
            print(f"{GREEN}패시브 선택 사항이 로드되었습니다: {filename}{RESET}")
            return True
            
        except FileNotFoundError:
            print(f"{YELLOW}저장된 패시브 선택 파일이 없습니다.{RESET}")
            return False
        except Exception as e:
            print(f"{RED}로드 실패: {e}{RESET}")
            return False

# 전역 패시브 선택 시스템 인스턴스
passive_system = PassiveSelectionSystem()

def get_passive_system() -> PassiveSelectionSystem:
    """패시브 선택 시스템 반환"""
    return passive_system

def show_passive_selection_ui(*args, **kwargs):
    """패시브 선택 UI 표시 (호환성 함수)"""
    return passive_system.select_passives_for_party(*args, **kwargs)
