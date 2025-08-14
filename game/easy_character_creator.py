from typing import List, Optional
from game.character import Character
from game.items import Item
from game.unified_name_pools import unified_name_pools
from game.enhanced_items import enhanced_items
from game.enhanced_party_presets import EnhancedPartyPresets
from game.auto_party_builder import AutoPartyBuilder
from game.party_history_manager import PartyHistoryManager
from game.cursor_menu_system import CursorMenu
from game.color_text import *

# 커서 메뉴 시스템 사용 가능 여부 확인
try:
    from game.cursor_menu_system import CursorMenu
    CURSOR_MENU_AVAILABLE = True
except ImportError:
    CURSOR_MENU_AVAILABLE = False

class EasyCharacterCreator:
    def __init__(self):
        """Easy Character Creator 초기화"""
        self.auto_builder = AutoPartyBuilder()
        self.party_history = PartyHistoryManager()
        self.enhanced_party_presets = EnhancedPartyPresets()
        self.last_generated_party = None
    
    def create_default_player_party(self) -> List[Character]:
        """플레이어용 기본 파티 생성 (수동 특성 선택)"""
        print(f"\n{YELLOW}🎮 플레이어 파티를 생성하는 중...{RESET}")
        
        try:
            # 밸런스 잡힌 파티 생성 (특성 수동 선택)
            party = self.auto_builder.create_balanced_party(auto_select_traits=False)
            
            if party:
                print(f"\n{GREEN}✅ 파티 생성 완료!{RESET}")
                print(f"{CYAN}파티 구성:{RESET}")
                for i, character in enumerate(party, 1):
                    print(f"  {i}. {character.name} ({character.character_class}) - Lv.{character.level}")
                
                # 파티를 히스토리에 저장
                self.party_history.add_party(party, {"auto_generated": True, "player_default": True})
                self.last_generated_party = party
                
                # 파티 프리셋 저장 옵션 제공
                self._offer_party_preset_save(party)
                
                return party
            else:
                print(f"{RED}❌ 파티 생성에 실패했습니다.{RESET}")
                return None
                
        except Exception as e:
            print(f"{RED}❌ 파티 생성 중 오류 발생: {e}{RESET}")
            
            # 폴백: 기본 파티 직접 생성
            try:
                print(f"{YELLOW}🔄 기본 파티로 대체합니다...{RESET}")
                from game.character import Character
                
                # 기본 4인 파티 생성 (전사, 아크메이지, 성기사, 바드)
                default_party = []
                default_classes = ["전사", "아크메이지", "성기사", "바드"]
                
                for i, class_name in enumerate(default_classes):
                    character = Character(f"플레이어{i+1}", class_name)
                    character.level = 1
                    character.current_hp = character.max_hp
                    character.current_mp = character.max_mp
                    default_party.append(character)
                
                print(f"{GREEN}✅ 기본 파티 생성 완료!{RESET}")
                return default_party
                
            except Exception as fallback_error:
                print(f"{RED}❌ 기본 파티 생성도 실패했습니다: {fallback_error}{RESET}")
                return None


    def _offer_party_preset_save(self, party: List[Character]) -> bool:
        """파티 프리셋 저장 제안"""
        if not party or len(party) == 0:
            return False
        
        try:
            if CURSOR_MENU_AVAILABLE:
                save_options = [
                    "💾 예, 프리셋으로 저장",
                    "🎮 아니오, 바로 게임 시작",
                    "📋 파티 정보만 확인"
                ]
                save_descriptions = [
                    "이 파티를 프리셋으로 저장하여 나중에 다시 사용할 수 있습니다",
                    "저장하지 않고 바로 게임을 시작합니다",
                    "파티 구성과 능력치를 자세히 확인합니다"
                ]
                
                save_menu = CursorMenu(
                    "💾 파티 프리셋 저장",
                    save_options, 
                    save_descriptions, 
                    cancellable=True,
                    extra_content=self._get_party_summary(party)
                )
                
                save_choice = save_menu.run()
                
                if save_choice == 0:  # 저장
                    return self._save_party_preset_interactive(party)
                elif save_choice == 2:  # 파티 정보 확인
                    self._show_detailed_party_info(party)
                    return self._offer_party_preset_save(party)  # 다시 저장 옵션 제공
                
                return False  # 저장하지 않음
            else:
                # 폴백: 텍스트 기반
                print(f"\n{CYAN}💾 이 파티를 프리셋으로 저장하시겠습니까?{RESET}")
                print(f"{GREEN}Y{RESET}: 저장, {RED}N{RESET}: 저장하지 않음")
                
                choice = input("선택: ").strip().lower()
                if choice in ['y', 'yes', '예', 'ㅇ']:
                    return self._save_party_preset_interactive(party)
                
                return False
                
        except Exception as e:
            print(f"⚠️ 프리셋 저장 제안 중 오류: {e}")
            return False
    
    def _save_party_preset_interactive(self, party: List[Character]) -> bool:
        """대화형 파티 프리셋 저장"""
        try:
            # 파티 이름 입력
            print(f"\n{CYAN}📝 파티 프리셋 저장{RESET}")
            party_name = input(f"{YELLOW}파티 이름을 입력하세요: {RESET}").strip()
            
            if not party_name:
                # 기본 이름 생성
                composition = "_".join([char.character_class for char in party[:2]])
                party_name = f"파티_{composition}"
            
            # 설명 입력 (선택사항)
            description = input(f"{YELLOW}파티 설명 (선택사항): {RESET}").strip()
            
            # 프리셋 저장
            print(f"\n{YELLOW}저장 중...{RESET}")
            filename = self.enhanced_party_presets.save_party_preset(party, party_name, description)
            
            if filename:
                print(f"\n{GREEN}✅ 파티 프리셋이 저장되었습니다!{RESET}")
                print(f"{CYAN}파일명: {filename}{RESET}")
                print(f"{CYAN}저장 위치: presets/parties/{RESET}")
                
                # AI 게임모드 호환 버전도 저장됨을 알림
                print(f"\n{BLUE}ℹ️ AI 게임모드 호환 버전도 함께 저장되었습니다.{RESET}")
                print(f"{BLUE}   이 프리셋은 AI 게임모드에서도 사용할 수 있습니다.{RESET}")
                
                # 저장된 캐릭터 목록 표시
                print(f"\n{CYAN}저장된 캐릭터들:{RESET}")
                for i, char in enumerate(party, 1):
                    char_name = getattr(char, 'name', f'캐릭터{i}')
                    char_class = getattr(char, 'character_class', '알 수 없음')
                    char_level = getattr(char, 'level', 1)
                    print(f"  {i}. {char_name} ({char_class}) - Lv.{char_level}")
                
                input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
                return True
            else:
                print(f"\n{RED}❌ 프리셋 저장에 실패했습니다.{RESET}")
                input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
                return False
                
        except Exception as e:
            print(f"\n{RED}❌ 프리셋 저장 중 오류: {e}{RESET}")
            input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
            return False
    
    def _get_party_summary(self, party: List[Character]) -> str:
        """파티 요약 정보 생성"""
        if not party:
            return "파티 정보 없음"
        
        try:
            summary_lines = []
            summary_lines.append(f"👥 파티 구성 ({len(party)}명):")
            
            total_hp = 0
            total_mp = 0
            total_level = 0
            
            for i, char in enumerate(party, 1):
                char_name = getattr(char, 'name', f'캐릭터{i}')
                char_class = getattr(char, 'character_class', '알 수 없음')
                char_level = getattr(char, 'level', 1)
                char_hp = getattr(char, 'max_hp', 0)
                char_mp = getattr(char, 'max_mp', 0)
                
                summary_lines.append(f"  {i}. {char_name} ({char_class}) Lv.{char_level}")
                
                total_hp += char_hp
                total_mp += char_mp
                total_level += char_level
            
            avg_level = total_level / len(party) if party else 0
            
            summary_lines.append("")
            summary_lines.append(f"📊 파티 통계:")
            summary_lines.append(f"  평균 레벨: {avg_level:.1f}")
            summary_lines.append(f"  총 HP: {total_hp:,}")
            summary_lines.append(f"  총 MP: {total_mp:,}")
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            return f"파티 요약 생성 실패: {e}"
    
    def _show_detailed_party_info(self, party: List[Character]):
        """상세한 파티 정보 표시"""
        if not party:
            print(f"\n{RED}❌ 표시할 파티 정보가 없습니다.{RESET}")
            return
        
        try:
            # 화면 정리 (안전하게)
            try:
                from game.clear_screen_utils import clear_screen
                clear_screen()
            except ImportError:
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{WHITE}{BOLD}📋 상세 파티 정보{RESET}")
            print(f"{CYAN}{'='*60}{RESET}")
            
            for i, char in enumerate(party, 1):
                char_name = getattr(char, 'name', f'캐릭터{i}')
                char_class = getattr(char, 'character_class', '알 수 없음')
                char_level = getattr(char, 'level', 1)
                
                print(f"\n{GREEN}{BOLD}{i}. {char_name} ({char_class}) - Lv.{char_level}{RESET}")
                print(f"{CYAN}{'─'*40}{RESET}")
                
                # 기본 스탯
                hp = getattr(char, 'max_hp', 0)
                mp = getattr(char, 'max_mp', 0)
                phys_att = getattr(char, 'physical_attack', 0)
                mag_att = getattr(char, 'magic_attack', 0)
                phys_def = getattr(char, 'physical_defense', 0)
                mag_def = getattr(char, 'magic_defense', 0)
                speed = getattr(char, 'speed', 0)
                
                print(f"  💚 HP: {hp:,} | 💙 MP: {mp:,}")
                print(f"  ⚔️ 물리공격: {phys_att} | 🔮 마법공격: {mag_att}")
                print(f"  🛡️ 물리방어: {phys_def} | 🌟 마법방어: {mag_def}")
                print(f"  💨 속도: {speed}")
                
                # 특성 정보
                if hasattr(char, 'passive_traits') and char.passive_traits:
                    print(f"  ✨ 특성: {', '.join([trait.name for trait in char.passive_traits])}")
                elif hasattr(char, 'selected_traits') and char.selected_traits:
                    print(f"  ✨ 특성: {len(char.selected_traits)}개 선택됨")
                else:
                    print(f"  ✨ 특성: 없음")
                
                # 장비 정보
                if hasattr(char, 'equipment') and char.equipment:
                    equipped_items = [item.name for item in char.equipment.values() if item]
                    if equipped_items:
                        print(f"  🎒 장비: {', '.join(equipped_items)}")
                    else:
                        print(f"  🎒 장비: 없음")
                else:
                    print(f"  🎒 장비: 없음")
            
            # 파티 전체 통계
            total_hp = sum(getattr(char, 'max_hp', 0) for char in party)
            total_mp = sum(getattr(char, 'max_mp', 0) for char in party)
            avg_level = sum(getattr(char, 'level', 1) for char in party) / len(party)
            
            print(f"\n{YELLOW}{BOLD}📊 파티 전체 통계{RESET}")
            print(f"{CYAN}{'─'*40}{RESET}")
            print(f"  👥 파티원 수: {len(party)}명")
            print(f"  📈 평균 레벨: {avg_level:.1f}")
            print(f"  💚 총 HP: {total_hp:,}")
            print(f"  💙 총 MP: {total_mp:,}")
            
            # 직업 구성 분석
            class_count = {}
            for char in party:
                char_class = getattr(char, 'character_class', '알 수 없음')
                class_count[char_class] = class_count.get(char_class, 0) + 1
            
            print(f"  🎭 직업 구성: {', '.join([f'{cls}({cnt})' for cls, cnt in class_count.items()])}")
            
            input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
            
        except Exception as e:
            print(f"\n{RED}❌ 파티 정보 표시 중 오류: {e}{RESET}")
            input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
    
    def create_character_with_details(self, character_class: str, name: str = None, gender: str = None, level: int = 1) -> Character:
        """상세 정보를 포함한 캐릭터 생성"""
        try:
            # 이름이 제공되지 않으면 통합 이름 풀에서 생성
            if not name:
                if gender:
                    name = unified_name_pools.get_random_name_by_gender(gender)
                else:
                    name, _ = unified_name_pools.get_random_name()
            
            # 성별이 제공되지 않으면 이름으로부터 감지
            if not gender:
                gender = unified_name_pools.detect_gender_from_name(name)
            
            # 캐릭터 생성 (level 매개변수 사용)
            character = self.auto_builder._create_character(character_class, level)
            character.name = name
            
            # 성별 정보 저장
            if hasattr(character, '__dict__'):
                character.gender = gender
            
            # 확장된 시작 아이템 지급
            self._give_enhanced_starting_items(character)
            
            return character
            
        except Exception as e:
            print(f"⚠️ 캐릭터 생성 실패: {e}")
            # 폴백: 기본 캐릭터 생성
            character = Character(name or "모험가", character_class)
            return character

    def _give_enhanced_starting_items(self, character: Character):
        """확장된 시작 아이템 지급"""
        try:
            starting_items = enhanced_items.generate_starting_items(
                character.character_class, character.level
            )
            
            # 인벤토리가 없으면 생성
            if not hasattr(character, 'inventory'):
                character.inventory = []
            
            # 장비 아이템 추가
            for equipment in starting_items["equipment"]:
                item = enhanced_items.create_item_for_inventory(equipment)
                if hasattr(character.inventory, 'add_item_by_name'):
                    # Inventory 객체인 경우 - 이름으로 추가
                    character.inventory.add_item_by_name(item['name'])
                elif hasattr(character.inventory, 'add_item'):
                    # Inventory 객체인 경우 - 직접 추가 (fallback)
                    from game.items import Item, ItemType, ItemRarity
                    inventory_item = Item(item['name'], ItemType.WEAPON, ItemRarity.COMMON, 
                                        item.get('description', '장비 아이템'))
                    character.inventory.add_item(inventory_item)
                else:
                    # 리스트인 경우 (호환성)
                    character.inventory.append(item)
            
            # 소비 아이템 추가
            for consumable in starting_items["consumables"]:
                item = enhanced_items.create_item_for_inventory(consumable)
                if hasattr(character.inventory, 'add_item_by_name'):
                    # Inventory 객체인 경우 - 이름으로 추가
                    character.inventory.add_item_by_name(item['name'])
                elif hasattr(character.inventory, 'add_item'):
                    # Inventory 객체인 경우 - 직접 추가 (fallback)
                    from game.items import Item, ItemType, ItemRarity
                    inventory_item = Item(item['name'], ItemType.CONSUMABLE, ItemRarity.COMMON, 
                                        item.get('description', '소비 아이템'))
                    character.inventory.add_item(inventory_item)
                else:
                    # 리스트인 경우 (호환성)
                    character.inventory.append(item)
                
        except Exception as e:
            print(f"⚠️ 시작 아이템 지급 실패: {e}")

    def create_balanced_party(self, auto_select_traits: bool = False) -> List[Character]:
        """균형잡힌 파티 생성"""
        try:
            print(f"\n{YELLOW}⚖️ 균형잡힌 파티를 생성하는 중...{RESET}")
            party = self.auto_builder.create_balanced_party(auto_select_traits=auto_select_traits)
            
            if party:
                print(f"{GREEN}✅ 균형잡힌 파티 생성 완료!{RESET}")
                self.last_generated_party = party
                return party
            else:
                print(f"{RED}❌ 파티 생성에 실패했습니다.{RESET}")
                return None
                
        except Exception as e:
            print(f"{RED}❌ 균형잡힌 파티 생성 중 오류: {e}{RESET}")
            return None
    
    def create_random_party(self, party_size: int = 4) -> List[Character]:
        """랜덤 파티 생성"""
        try:
            print(f"\n{YELLOW}🎲 랜덤 파티를 생성하는 중...{RESET}")
            
            # AutoPartyBuilder에 create_random_party 메서드가 있는지 확인
            if hasattr(self.auto_builder, 'create_random_party'):
                party = self.auto_builder.create_random_party(party_size=party_size)
            else:
                # 폴백: 랜덤 직업 선택으로 균형잡힌 파티 생성
                import random
                from game.character import Character
                
                available_classes = [
                    "전사", "아크메이지", "성기사", "바드", "도적", "기사", 
                    "신관", "드루이드", "무당", "기계공학자", "정령술사"
                ]
                
                party = []
                selected_classes = random.sample(available_classes, min(party_size, len(available_classes)))
                
                for i, char_class in enumerate(selected_classes):
                    character = self.create_character_with_details(char_class)
                    if character:
                        party.append(character)
                        print(f"  ✅ {character.name} ({character.character_class}) 생성 완료")
            
            if party:
                print(f"{GREEN}✅ 랜덤 파티 생성 완료! ({len(party)}명){RESET}")
                self.last_generated_party = party
                return party
            else:
                print(f"{RED}❌ 파티 생성에 실패했습니다.{RESET}")
                return None
                
        except Exception as e:
            print(f"{RED}❌ 랜덤 파티 생성 중 오류: {e}{RESET}")
            return None

    def create_party_from_history(self, party_data):
        """파티 히스토리에서 파티 재생성"""
        try:
            print(f"{CYAN}🔍 히스토리 데이터 검증 중...{RESET}")
            
            # 데이터 구조 확인
            if not party_data:
                print(f"{RED}❌ party_data가 None 또는 빈 값입니다.{RESET}")
                return None
            
            print(f"{CYAN}📋 party_data 타입: {type(party_data)}{RESET}")
            
            # party_data가 리스트인 경우 딕셔너리로 변환 시도
            if isinstance(party_data, list):
                print(f"{YELLOW}⚠️ party_data가 list입니다. dict로 변환 시도...{RESET}")
                if len(party_data) >= 4:  # 최소 4명의 파티원이 있어야 함
                    # 리스트를 딕셔너리로 변환
                    converted_data = {"members": party_data}
                    party_data = converted_data
                    print(f"{GREEN}✅ party_data를 dict로 변환했습니다.{RESET}")
                else:
                    print(f"{RED}❌ party_data 리스트에 충분한 데이터가 없습니다: {len(party_data)}개{RESET}")
                    return None
            
            print(f"{CYAN}📋 party_data 키: {list(party_data.keys()) if isinstance(party_data, dict) else 'dict가 아님'}{RESET}")
            
            # party_data가 딕셔너리가 아닌 경우 오류
            if not isinstance(party_data, dict):
                print(f"{RED}❌ party_data가 딕셔너리가 아닙니다: {type(party_data)}{RESET}")
                return None
            
            # members 데이터 확인
            if 'members' not in party_data:
                print(f"{RED}❌ members 키가 없습니다.{RESET}")
                return None
            
            members_data = party_data['members']
            if not isinstance(members_data, list):
                print(f"{RED}❌ members가 리스트가 아닙니다: {type(members_data)}{RESET}")
                return None
            
            if not members_data:
                print(f"{RED}❌ members가 비어있습니다.{RESET}")
                return None
            
            print(f"{GREEN}✅ 데이터 구조 검증 완료{RESET}")
            print(f"{CYAN}📋 파티원 수: {len(members_data)}명{RESET}")
            
            # 파티 재생성
            party = []
            for i, member_data in enumerate(members_data):
                print(f"{CYAN}🔄 {i+1}번째 멤버 생성 중...{RESET}")
                
                if not isinstance(member_data, dict):
                    print(f"{RED}❌ 멤버 데이터가 딕셔너리가 아닙니다: {type(member_data)}{RESET}")
                    continue
                
                # 필수 데이터 확인
                name = member_data.get('name', 'Unknown')
                char_class = member_data.get('class', '전사')
                level = member_data.get('level', 1)
                
                print(f"{CYAN}   📝 이름: {name}, 직업: {char_class}, 레벨: {level}{RESET}")
                
                # 캐릭터 생성
                character = self.create_character_with_details(char_class, name=name, level=level)
                if character:
                    # 스탯 복원
                    if 'hp' in member_data:
                        character.current_hp = member_data['hp']
                    if 'max_hp' in member_data:
                        character.max_hp = member_data['max_hp']
                    if 'mp' in member_data:
                        character.current_mp = member_data['mp']
                    if 'max_mp' in member_data:
                        character.max_mp = member_data['max_mp']
                    if 'experience' in member_data:
                        character.experience = member_data['experience']
                    if 'brave_points' in member_data:
                        character.brave_points = member_data['brave_points']
                        
                    # 전투 스탯 복원
                    for stat in ['physical_attack', 'physical_defense', 'magic_attack', 'magic_defense', 'speed']:
                        if stat in member_data:
                            setattr(character, stat, member_data[stat])
                    
                    party.append(character)
                    print(f"{GREEN}   ✅ {character.name} ({character.character_class}) 복원 완료{RESET}")
                else:
                    print(f"{RED}   ❌ 캐릭터 생성 실패{RESET}")
            
            if party:
                print(f"{GREEN}✅ 파티 복원 완료! ({len(party)}명){RESET}")
                self.last_generated_party = party
                return party
            else:
                print(f"{RED}❌ 파티원이 한 명도 생성되지 않았습니다.{RESET}")
                return None
            
        except Exception as e:
            print(f"{RED}❌ 히스토리에서 파티 생성 실패: {e}{RESET}")
            import traceback
            print(f"{RED}상세 오류: {traceback.format_exc()}{RESET}")
            return None
            if not isinstance(composition, dict):
                print(f"{RED}❌ composition이 딕셔너리가 아닙니다: {type(composition)}{RESET}")
                return None
                
            if 'party' not in composition:
                print(f"{RED}❌ composition에 'party' 키가 없습니다.{RESET}")
                print(f"{CYAN}📋 사용 가능한 키: {list(composition.keys())}{RESET}")
                return None
            
            party_data = composition['party']
            
            if not party_data:
                print(f"{RED}❌ party_data가 빈 값입니다.{RESET}")
                return None
                
            if not isinstance(party_data, list):
                print(f"{RED}❌ party_data가 리스트가 아닙니다: {type(party_data)}{RESET}")
                return None
            
            print(f"{GREEN}✅ 파티 데이터 검증 완료 - {len(party_data)}명의 캐릭터 데이터 발견{RESET}")
            
            party = []
            
            for i, char_data in enumerate(party_data):
                try:
                    print(f"{CYAN}🔄 캐릭터 {i+1} 복원 중...{RESET}")
                    
                    if not isinstance(char_data, dict):
                        print(f"{RED}❌ 캐릭터 데이터가 딕셔너리가 아닙니다: {type(char_data)}{RESET}")
                        continue
                    
                    # 캐릭터 재생성
                    character = Character(
                        name=char_data.get('name', f'복원된캐릭터{i+1}'),
                        character_class=char_data.get('character_class', '전사')
                    )
                    
                    # 기본 속성 복원
                    character.level = char_data.get('level', 1)
                    character.current_hp = char_data.get('current_hp', character.max_hp)
                    character.current_mp = char_data.get('current_mp', character.max_mp)
                    
                    # 장비 복원 (기본값 설정)
                    if 'equipment' in char_data:
                        # 장비 복원 로직 (향후 구현)
                        pass
                    
                    party.append(character)
                    print(f"{GREEN}✅ {character.name} ({character.character_class}) 복원 완료{RESET}")
                    
                except Exception as char_error:
                    print(f"{RED}❌ 캐릭터 {i+1} 복원 실패: {char_error}{RESET}")
                    continue
            
            if party:
                print(f"{GREEN}✅ 히스토리에서 {len(party)}명의 파티를 복원했습니다.{RESET}")
                return party
            else:
                print(f"{RED}❌ 복원 가능한 캐릭터가 없습니다.{RESET}")
                return None
            
        except Exception as e:
            print(f"{RED}❌ 파티 히스토리 복원 중 오류: {e}{RESET}")
            import traceback
            traceback.print_exc()
            return None

# 전역 인스턴스
easy_creator = EasyCharacterCreator()

def get_easy_character_creator():
    """쉬운 캐릭터 생성기 반환"""
    return easy_creator
