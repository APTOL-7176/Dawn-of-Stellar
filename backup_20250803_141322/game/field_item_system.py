"""
필드에서 아이템 사용 시스템
"""

from typing import List, Optional
from .character import Character, PartyManager
from .items import ItemDatabase, ItemType
from .input_utils import KeyboardInput

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

class FieldItemSystem:
    """필드 아이템 사용 시스템"""
    
    def __init__(self):
        self.keyboard = KeyboardInput()
        self.item_db = ItemDatabase()
    
    def show_field_item_menu(self, party: PartyManager) -> bool:
        """필드 아이템 메뉴 표시 - 커서 방식"""
        print(f"\n{CYAN}💼 필드 아이템 메뉴{RESET}")
        print("="*60)
        
        # 파티원 선택
        alive_members = party.get_alive_members()
        if not alive_members:
            print(f"{RED}사용 가능한 파티원이 없습니다.{RESET}")
            return False
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            # 파티원 목록을 커서 메뉴로 생성
            options = []
            descriptions = []
            
            for member in alive_members:
                hp_bar = self._get_hp_bar(member)
                mp_bar = self._get_mp_bar(member)
                options.append(f"👤 {member.name}")
                descriptions.append(f"{hp_bar} | {mp_bar}")
            
            options.append("❌ 취소")
            descriptions.append("아이템 사용을 취소합니다")
            
            menu = create_simple_menu("🎒 아이템 사용 - 대상 선택", options, descriptions)
            result = menu.run()
            
            if result == -1 or result >= len(alive_members):  # 취소
                return False
            else:
                selected_member = alive_members[result]
                return self._show_member_items(selected_member, party)
                
        except ImportError:
            # 폴백: 기존 텍스트 메뉴
            print("아이템을 사용할 파티원을 선택하세요:")
            for i, member in enumerate(alive_members, 1):
                hp_bar = self._get_hp_bar(member)
                mp_bar = self._get_mp_bar(member)
                print(f"{i}. {member.name} | {hp_bar} | {mp_bar}")
            print(f"{len(alive_members)+1}. 취소")
            
            try:
                choice = int(self.keyboard.get_key()) - 1
                if choice == len(alive_members):
                    return False
                elif 0 <= choice < len(alive_members):
                    selected_member = alive_members[choice]
                    return self._show_member_items(selected_member, party)
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
                    return False
            except ValueError:
                print(f"{RED}숫자를 입력하세요.{RESET}")
                return False
        except ValueError:
            print(f"{RED}숫자를 입력하세요.{RESET}")
            return False
    
    def _show_member_items(self, user: Character, party: PartyManager) -> bool:
        """선택된 파티원의 아이템 목록 표시 - 커서 방식"""
        print(f"\n{WHITE}{user.name}의 필드 아이템:{RESET}")
        print("-" * 50)
        
        # 필드에서 사용 가능한 아이템 필터링
        field_items = []
        for item_name, quantity in user.inventory.get_items_list():
            item = self.item_db.get_item(item_name)
            if item and item.item_type == ItemType.CONSUMABLE and getattr(item, 'field_usable', False):
                field_items.append((item, quantity))
        
        if not field_items:
            print(f"{YELLOW}필드에서 사용할 수 있는 아이템이 없습니다.{RESET}")
            print(f"{CYAN}💡 야영 텐트, 치료 포션, 귀환 두루마리 등을 구입해보세요!{RESET}")
            return False
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            # 아이템 목록을 커서 메뉴로 생성
            options = []
            descriptions = []
            
            for item, quantity in field_items:
                effect_desc = item.get_effect_description() if hasattr(item, 'get_effect_description') else item.description
                usable_info = self._get_usability_info(item)
                options.append(f"💊 {item.name} ({quantity}개) {usable_info}")
                descriptions.append(effect_desc)
            
            options.append("❌ 취소")
            descriptions.append("아이템 사용을 취소합니다")
            
            menu = create_simple_menu(f"{user.name}의 아이템", options, descriptions)
            result = menu.run()
            
            if result == -1 or result >= len(field_items):  # 취소
                return False
            else:
                selected_item, quantity = field_items[result]
                return self._use_field_item(user, selected_item, party)
                
        except ImportError:
            # 폴백: 기존 텍스트 메뉴
            print("사용할 아이템을 선택하세요:")
            for i, (item, quantity) in enumerate(field_items, 1):
                effect_desc = item.get_effect_description() if hasattr(item, 'get_effect_description') else item.description
                usable_info = self._get_usability_info(item)
                print(f"{i}. {item.name} ({quantity}개) {usable_info}")
                print(f"   📝 {effect_desc}")
                print()
            print(f"{len(field_items)+1}. 취소")
            
            try:
                choice = int(self.keyboard.get_key()) - 1
                if choice == len(field_items):
                    return False
                elif 0 <= choice < len(field_items):
                    selected_item, quantity = field_items[choice]
                    return self._use_field_item(user, selected_item, party)
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
                    return False
            except ValueError:
                print(f"{RED}숫자를 입력하세요.{RESET}")
                return False
    
    def _use_field_item(self, user: Character, item, party: PartyManager) -> bool:
        """필드 아이템 사용"""
        # 대상 선택이 필요한 아이템들
        if any(effect in item.effects for effect in ["heal", "mana_restore", "cure"]):
            target = self._select_target(party, "치료할 대상을 선택하세요:")
            if not target:
                return False
        elif "revive" in item.effects:
            target = self._select_dead_target(party)
            if not target:
                return False
        else:
            target = user  # 자기 자신 또는 특별한 대상 불필요
        
        # 아이템 사용
        print(f"\n{GREEN}✨ {user.name}이(가) {item.name}을(를) 사용합니다!{RESET}")
        
        success = item.use_item(target)
        
        if success:
            # 아이템 소모
            user.inventory.remove_item(item.name, 1)
            
            # 특별한 필드 효과들 처리
            if "teleport_town" in item.effects:
                print(f"{MAGENTA}🌟 마을로 순간이동합니다!{RESET}")
                # 실제 게임에서는 월드 시스템과 연동하여 마을로 이동
                return True
            elif "escape_floor" in item.effects:
                print(f"{YELLOW}💨 현재 층에서 탈출합니다!{RESET}")
                # 실제 게임에서는 다음 층으로 이동
                return True
            elif "detect_treasure" in item.effects:
                print(f"{CYAN}🔍 숨겨진 보물의 위치가 밝혀졌습니다!{RESET}")
                # 실제 게임에서는 맵에 보물 위치 표시
                return True
            elif "unlock" in item.effects:
                print(f"{GREEN}🔓 자물쇠 해제 도구가 준비되었습니다!{RESET}")
                # 실제 게임에서는 다음 잠긴 문/상자에 보너스 적용
                return True
            
            return True
        else:
            print(f"{RED}아이템을 사용할 수 없습니다.{RESET}")
            return False
    
    def _select_target(self, party: PartyManager, prompt: str) -> Optional[Character]:
        """대상 선택"""
        alive_members = party.get_alive_members()
        if not alive_members:
            return None
        
        print(f"\n{prompt}")
        for i, member in enumerate(alive_members, 1):
            hp_status = f"HP: {member.current_hp}/{member.max_hp}"
            mp_status = f"MP: {member.current_mp}/{member.max_mp}"
            status = ""
            if member.current_hp < member.max_hp * 0.5:
                status += " [부상]"
            if member.current_mp < member.max_mp * 0.3:
                status += " [MP부족]"
            print(f"{i}. {member.name} ({hp_status}, {mp_status}){status}")
        print(f"{len(alive_members)+1}. 취소")
        
        try:
            choice = int(self.keyboard.get_key()) - 1
            if choice == len(alive_members):
                return None
            elif 0 <= choice < len(alive_members):
                return alive_members[choice]
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return None
        except ValueError:
            print(f"{RED}숫자를 입력하세요.{RESET}")
            return None
    
    def _select_dead_target(self, party: PartyManager) -> Optional[Character]:
        """죽은 파티원 선택"""
        dead_members = [member for member in party.members if not member.is_alive]
        if not dead_members:
            print(f"{YELLOW}부활시킬 수 있는 파티원이 없습니다.{RESET}")
            return None
        
        print("\n부활시킬 대상을 선택하세요:")
        for i, member in enumerate(dead_members, 1):
            print(f"{i}. {member.name} [사망]")
        print(f"{len(dead_members)+1}. 취소")
        
        try:
            choice = int(self.keyboard.get_key()) - 1
            if choice == len(dead_members):
                return None
            elif 0 <= choice < len(dead_members):
                return dead_members[choice]
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return None
        except ValueError:
            print(f"{RED}숫자를 입력하세요.{RESET}")
            return None
    
    def _get_usability_info(self, item) -> str:
        """아이템 사용 가능 정보"""
        if not getattr(item, 'combat_usable', True):
            return f"{CYAN}[필드전용]{RESET}"
        elif getattr(item, 'field_usable', False):
            return f"{GREEN}[필드+전투]{RESET}"
        else:
            return f"{YELLOW}[전투전용]{RESET}"
    
    def _get_hp_bar(self, character: Character) -> str:
        """HP 바 생성"""
        if character.max_hp <= 0:
            return "HP: ???"
        
        ratio = character.current_hp / character.max_hp
        bar_length = 10
        filled = int(ratio * bar_length)
        
        if ratio > 0.7:
            color = GREEN
        elif ratio > 0.3:
            color = YELLOW
        else:
            color = RED
            
        bar = color + "█" * filled + RESET + "░" * (bar_length - filled)
        return f"HP {character.current_hp:3}/{character.max_hp:3} [{bar}]"
    
    def _get_mp_bar(self, character: Character) -> str:
        """MP 바 생성"""
        if character.max_mp <= 0:
            return "MP: ???"
        
        ratio = character.current_mp / character.max_mp
        bar_length = 8
        filled = int(ratio * bar_length)
        
        if ratio > 0.5:
            color = BLUE
        elif ratio > 0.2:
            color = YELLOW
        else:
            color = RED
            
        bar = color + "█" * filled + RESET + "░" * (bar_length - filled)
        return f"MP {character.current_mp:2}/{character.max_mp:2} [{bar}]"


# 전역 인스턴스
field_item_system = FieldItemSystem()

def get_field_item_system():
    """필드 아이템 시스템 인스턴스 반환"""
    return field_item_system
