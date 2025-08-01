"""
개선된 캐릭터 생성 시스템
"""

from typing import List, Dict, Optional, Tuple
import random
from .character import Character
from .auto_party_builder import AutoPartyBuilder
from .input_utils import KeyboardInput

try:
    from .passive_selection import get_passive_system
    PASSIVE_SYSTEM_AVAILABLE = True
except ImportError:
    PASSIVE_SYSTEM_AVAILABLE = False

try:
    from .cursor_menu_system import CursorMenu
    CURSOR_MENU_AVAILABLE = True
except ImportError:
    CURSOR_MENU_AVAILABLE = False

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

class EasyCharacterCreator:
    """쉬운 캐릭터 생성 시스템"""
    
    def __init__(self):
        self.keyboard = KeyboardInput()
        self.auto_builder = AutoPartyBuilder()
        self.last_generated_party = None  # 특성 상세 보기용
        if PASSIVE_SYSTEM_AVAILABLE:
            self.passive_manager = get_passive_system()
        else:
            self.passive_manager = None
        
        # 추천 직업 조합 (사용자가 쉽게 선택할 수 있도록)
        self.recommended_combos = {
            "균형잡힌 파티": ["전사", "아크메이지", "성기사", "바드"],
            "물리 특화 파티": ["검성", "궁수", "사무라이", "몽크"],
            "마법 특화 파티": ["아크메이지", "네크로맨서", "정령술사", "드루이드"],
            "생존 특화 파티": ["성기사", "신관", "드루이드", "기사"],
            "속도 특화 파티": ["암살자", "해적", "도적", "바드"],
            "독특한 조합": ["무당", "용기사", "기계공학자", "철학자"]
        }
    
    def show_character_creation_menu(self) -> List[Character]:
        """캐릭터 생성 메뉴 표시 - 커서 방식"""
        if CURSOR_MENU_AVAILABLE:
            try:
                while True:
                    options = [
                        "🚀 자동 파티 생성 (추천)",
                        "🎯 추천 조합 선택",
                        "🛠️ 커스텀 파티 생성",
                        "👤 단일 캐릭터 생성",
                        "❓ 도움말",
                        "❌ 나가기"
                    ]
                    
                    descriptions = [
                        "밸런스 잡힌 4인 파티를 자동으로 생성합니다",
                        "미리 준비된 조합 중에서 선택합니다",
                        "직접 캐릭터들을 만들어 파티를 구성합니다",
                        "캐릭터 한 명만 생성합니다",
                        "캐릭터 생성에 대한 도움말을 봅니다",
                        "메인 메뉴로 돌아갑니다"
                    ]
                    
                    menu = CursorMenu("🎭 캐릭터 생성", options, descriptions, cancellable=True)
                    result = menu.run()
                    
                    if result is None or result == 5:  # 나가기
                        return None
                    elif result == 0:  # 자동 파티 생성
                        party = self._auto_party_creation()
                        return party
                    elif result == 1:  # 추천 조합 선택
                        party = self._recommended_combo_creation()
                        return party
                    elif result == 2:  # 커스텀 파티 생성
                        party = self._custom_party_creation()
                        return party
                    elif result == 3:  # 단일 캐릭터 생성
                        party = self._single_character_creation()
                        return party
                    elif result == 4:  # 도움말
                        self._show_help()
                        
            except Exception:
                # 폴백: 기존 텍스트 메뉴
                return self._show_character_creation_menu_fallback()
        else:
            # 폴백: 기존 텍스트 메뉴
            return self._show_character_creation_menu_fallback()
    
    def _show_character_creation_menu_fallback(self) -> List[Character]:
        """캐릭터 생성 메뉴 폴백 (기존 방식)"""
        while True:
            self._show_main_menu()
            choice = self.keyboard.get_key().lower()
            
            if choice == '1':
                return self._auto_party_creation()
            elif choice == '2':
                return self._recommended_combo_creation()
            elif choice == '3':
                return self._custom_party_creation()
            elif choice == '4':
                return self._single_character_creation()
            elif choice == '5':
                self._show_help()
            elif choice == 'q':
                return None
            else:
                print(f"{RED}잘못된 선택입니다. 다시 시도해주세요.{RESET}")
    
    def _show_main_menu(self):
        """메인 메뉴 표시"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🎭 Dawn Of Stellar - 캐릭터 생성{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        print(f"{GREEN}1.{RESET} 🎲 완전 자동 파티 (빠름)")
        print(f"{GREEN}2.{RESET} 📋 추천 조합 선택 (쉬움)")
        print(f"{GREEN}3.{RESET} 🛠️ 커스텀 파티 (상세)")
        print(f"{GREEN}4.{RESET} 👤 개별 캐릭터 생성 (전문)")
        print(f"{GREEN}5.{RESET} ❓ 도움말")
        print(f"{RED}Q.{RESET} 🚪 나가기")
        print(f"{CYAN}{'='*60}{RESET}")
        print(f"{YELLOW}선택하세요: {RESET}", end="")
    
    def _auto_party_creation(self) -> List[Character]:
        """완전 자동 파티 생성"""
        if CURSOR_MENU_AVAILABLE:
            try:
                # 특성 선택 방식 묻기
                trait_options = ["자동 선택 (빠름)", "수동 선택 (상세)"]
                trait_descriptions = [
                    "AI가 직업에 맞는 특성을 자동으로 선택합니다",
                    "각 캐릭터마다 직접 특성을 선택합니다"
                ]
                
                trait_menu = CursorMenu("🎲 자동 파티 생성\n특성 선택 방식을 선택하세요", trait_options, trait_descriptions, cancellable=True)
                trait_result = trait_menu.run()
                
                if trait_result is None:  # 취소
                    return None
                    
                manual_traits = (trait_result == 1)
                
                print(f"\n{YELLOW}생성 중...{RESET}")
                
                try:
                    if manual_traits:
                        # 수동 특성 선택을 위해 특성 없이 파티 생성
                        party = self.auto_builder.create_balanced_party(auto_select_traits=False)
                    else:
                        # 자동 특성 선택 포함해서 파티 생성
                        party = self.auto_builder.create_balanced_party(auto_select_traits=True)
                except Exception as e:
                    print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
                    
                    # 재시도 확인 메뉴
                    retry_options = ["다시 시도", "메뉴로 돌아가기"]
                    retry_descriptions = ["파티 생성을 다시 시도합니다", "캐릭터 생성 메뉴로 돌아갑니다"]
                    retry_menu = CursorMenu("오류 발생", retry_options, retry_descriptions)
                    retry_result = retry_menu.run()
                    
                    if retry_result == 0:
                        return self._auto_party_creation()
                    else:
                        return None
                
                # 수동 특성 선택이면 각 캐릭터마다 특성 선택
                if manual_traits and party:
                    print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
                    for i, character in enumerate(party, 1):
                        # 이미 특성이 선택되어 있는지 확인
                        has_traits = (hasattr(character, 'selected_traits') and character.selected_traits) or \
                                   (hasattr(character, 'traits') and character.traits) or \
                                   (hasattr(character, 'active_traits') and character.active_traits)
                        
                        if has_traits:
                            print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                            print(f"{GREEN}✅ 이미 특성이 자동으로 선택되었습니다.{RESET}")
                            continue
                        
                        print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                        trait_success = self._manual_trait_selection_cursor(character)
                        if not trait_success:  # 특성 선택이 취소된 경우
                            print(f"{RED}특성 선택이 취소되어 파티 생성을 중단합니다.{RESET}")
                            return None
                
                if party:
                    confirm_result = self._confirm_party_cursor(party)
                    if confirm_result is True:
                        return party
                    elif confirm_result is False:
                        return self._auto_party_creation()  # 재생성
                    else:  # confirm_result is None (취소)
                        return None
                return None
                
            except Exception:
                # 폴백: 기존 방식
                return self._auto_party_creation_fallback()
        else:
            # 폴백: 기존 방식
            return self._auto_party_creation_fallback()
    
    def _recommended_combo_creation(self) -> List[Character]:
        """추천 조합 선택"""
        print(f"\n{CYAN}📋 추천 파티 조합{RESET}")
        print("검증된 조합 중에서 선택하세요:")
        print()
        
        combos = list(self.recommended_combos.items())
        for i, (name, classes) in enumerate(combos, 1):
            classes_str = " + ".join(classes)
            print(f"{GREEN}{i}.{RESET} {name}")
            print(f"   {BLUE}{classes_str}{RESET}")
            print()
        
        print(f"{len(combos)+1}. 🎲 랜덤 추천 조합")
        print("0. 돌아가기")
        
        try:
            choice_str = self.keyboard.get_key()
            choice = int(choice_str)
            if choice == 0:
                return self.show_character_creation_menu()
            elif choice == len(combos)+1:
                # 랜덤 추천
                selected_combo = random.choice(list(self.recommended_combos.values()))
            elif 1 <= choice <= len(combos):
                selected_combo = combos[choice-1][1]
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return self._recommended_combo_creation()
            
            print(f"\n{YELLOW}선택된 조합으로 파티 생성 중...{RESET}")
            print(f"{CYAN}선택된 조합: {' + '.join(selected_combo)}{RESET}")
            
            # 특성 선택 방식 묻기 (커서 메뉴)
            trait_options = ["🤖 자동 선택 (빠름)", "✋ 수동 선택 (상세)"]
            trait_descriptions = [
                "특성을 자동으로 선택하여 빠르게 게임을 시작합니다",
                "커서를 사용하여 특성을 직접 선택합니다"
            ]
            
            if CURSOR_MENU_AVAILABLE:
                try:
                    trait_menu = CursorMenu("🎭 특성 선택 방식", trait_options, trait_descriptions, cancellable=True)
                    trait_choice_idx = trait_menu.run()
                    if trait_choice_idx is None:
                        return None
                    manual_traits = (trait_choice_idx == 1)  # 0: 자동, 1: 수동
                except Exception:
                    # 폴백: 커서 메뉴 방식
                    trait_options = ["🤖 자동 선택 (빠름)", "✋ 수동 선택 (상세)"]
                    trait_descriptions = [
                        "AI가 캐릭터에 적합한 특성을 자동으로 선택합니다",
                        "플레이어가 직접 각 캐릭터의 특성을 선택합니다"
                    ]
                    trait_menu = CursorMenu("🎭 특성 선택 방식", trait_options, trait_descriptions, cancellable=True)
                    trait_choice_idx = trait_menu.run()
                    if trait_choice_idx is None:
                        return None
                    manual_traits = (trait_choice_idx == 1)
            else:
                # 폴백: 커서 메뉴 방식
                trait_options = ["🤖 자동 선택 (빠름)", "✋ 수동 선택 (상세)"]
                trait_descriptions = [
                    "AI가 캐릭터에 적합한 특성을 자동으로 선택합니다",
                    "플레이어가 직접 각 캐릭터의 특성을 선택합니다"
                ]
                trait_menu = CursorMenu("🎭 특성 선택 방식", trait_options, trait_descriptions, cancellable=True)
                trait_choice_idx = trait_menu.run()
                if trait_choice_idx is None:
                    return None
                manual_traits = (trait_choice_idx == 1)
                
            if manual_traits:
                print(f"{GREEN}✅ 수동 특성 선택 모드{RESET}")
            else:
                print(f"{GREEN}✅ 자동 특성 선택 모드{RESET}")
            
            try:
                if manual_traits:
                    # 수동 특성 선택을 위해 특성 없이 파티 생성
                    party = self.auto_builder.create_balanced_party(selected_combo, auto_select_traits=False)
                else:
                    # 자동 특성 선택 포함해서 파티 생성
                    party = self.auto_builder.create_balanced_party(selected_combo, auto_select_traits=True)
            except Exception as e:
                print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
                if self._show_yes_no_menu("🔄 오류 발생", "다시 시도하시겠습니까?", "다시 시도", "메뉴로 돌아가기"):
                    return self._recommended_combo_creation()
                else:
                    return self.show_character_creation_menu()
            
            # 수동 특성 선택이면 각 캐릭터마다 특성 선택
            if manual_traits and party:
                print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
                for i, character in enumerate(party, 1):
                    print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                    trait_success = self._manual_trait_selection(character)
                    if not trait_success:  # 특성 선택이 취소된 경우
                        print(f"{RED}특성 선택이 취소되어 파티 생성을 중단합니다.{RESET}")
                        return None
            
            if party:
                confirm_result = self._confirm_party_cursor(party)
                if confirm_result is True:
                    return party
                elif confirm_result is False:
                    return self._recommended_combo_creation()  # 재생성
                else:  # confirm_result is None (취소)
                    return None
            return None
            
        except ValueError:
            print(f"{RED}숫자를 입력해주세요.{RESET}")
            return self._recommended_combo_creation()
    
    def _custom_party_creation(self) -> List[Character]:
        """커스텀 파티 생성 - 커서 방식"""
        if CURSOR_MENU_AVAILABLE:
            try:
                from .color_text import bright_red, bright_blue, bright_green, bright_yellow, bright_magenta, bright_cyan
                
                selected_classes = []
                max_party_size = 4
                
                # 역할군별 캐릭터 분류
                role_categories = {
                    "🛡️ 탱커": {
                        "classes": ["전사", "성기사", "기사", "암흑기사", "검투사", "광전사", "용기사"],
                        "color": bright_red,
                        "description": "높은 체력과 방어력으로 파티를 보호합니다"
                    },
                    "⚔️ 물리 딜러": {
                        "classes": ["검성", "사무라이", "암살자", "몽크", "마검사", "궁수", "도적", "해적", "기계공학자"],
                        "color": bright_yellow,
                        "description": "물리 공격으로 적을 제압하는 전투 전문가"
                    },
                    "🔮 마법사": {
                        "classes": ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사"],
                        "color": bright_blue,
                        "description": "강력한 마법으로 적을 소멸시킵니다"
                    },
                    "✨ 서포터": {
                        "classes": ["바드", "드루이드", "신관", "무당", "철학자"],
                        "color": bright_cyan,
                        "description": "파티원을 치유하고 강화하는 지원 역할"
                    }
                }
                
                while len(selected_classes) < max_party_size:
                    remaining = max_party_size - len(selected_classes)
                    
                    # 현재 선택된 클래스들 표시
                    if selected_classes:
                        print(f"\n{GREEN}✅ 현재 선택된 파티:{RESET}")
                        for i, class_name in enumerate(selected_classes, 1):
                            print(f"  {i}. {CYAN}{class_name}{RESET}")
                        print()
                    
                    # 메뉴 옵션 생성
                    options = []
                    descriptions = []
                    
                    for category_name, category_data in role_categories.items():
                        color_func = category_data["color"]
                        available_count = len([c for c in category_data["classes"] if c not in selected_classes])
                        if available_count > 0:
                            options.append(color_func(f"{category_name} ({available_count}개)"))
                            descriptions.append(f"{category_data['description']} - {available_count}개 선택 가능")
                    
                    # 특별 옵션들
                    if len(selected_classes) > 0:
                        options.extend([
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                            f"🎯 자동 완성 (남은 {remaining}자리)",
                            "🗑️ 마지막 선택 취소"
                        ])
                        descriptions.extend([
                            "",
                            f"남은 {remaining}자리를 자동으로 균형있게 채웁니다",
                            f"마지막으로 선택한 {selected_classes[-1]}을(를) 제거합니다"
                        ])
                    
                    title = f"🛠️ 커스텀 파티 생성 ({len(selected_classes)}/{max_party_size})"
                    menu = CursorMenu(title, options, descriptions, cancellable=True)
                    result = menu.run()
                    
                    if result is None:  # 취소
                        return None
                    elif result >= len(role_categories):  # 특별 옵션들
                        special_index = result - len(role_categories)
                        if special_index == 1:  # 자동 완성
                            remaining_party = self.auto_builder.create_balanced_party(selected_classes, max_party_size)
                            if remaining_party:
                                confirm_result = self._confirm_party_cursor(remaining_party)
                                if confirm_result is True:
                                    return remaining_party
                                elif confirm_result is None:  # 취소
                                    return None
                                # confirm_result is False이면 continue (재생성)
                            continue
                        elif special_index == 2:  # 마지막 선택 취소
                            if selected_classes:
                                removed = selected_classes.pop()
                                print(f"{YELLOW}✅ {removed} 제거됨{RESET}")
                            continue
                    else:
                        # 역할군 선택됨 - 해당 역할군의 클래스들 표시
                        category_names = list(role_categories.keys())
                        selected_category = category_names[result]
                        category_data = role_categories[selected_category]
                        available_classes = [c for c in category_data["classes"] if c not in selected_classes]
                        
                        if not available_classes:
                            print(f"{RED}❌ 해당 역할군의 모든 클래스가 이미 선택되었습니다.{RESET}")
                            continue
                        
                        # 역할군 내 클래스 선택
                        class_options = []
                        class_descriptions = []
                        color_func = category_data["color"]
                        
                        for class_name in available_classes:
                            class_options.append(color_func(f"🎭 {class_name}"))
                            class_descriptions.append(self._get_class_description(class_name))
                        
                        class_menu = CursorMenu(
                            f"{selected_category} 선택 ({remaining}자리 남음)", 
                            class_options, 
                            class_descriptions, 
                            cancellable=True
                        )
                        
                        class_result = class_menu.run()
                        
                        if class_result is not None:
                            selected_class = available_classes[class_result]
                            selected_classes.append(selected_class)
                            print(f"{GREEN}✅ {selected_class} 추가됨{RESET}")
                
                # 모든 자리가 채워짐 - 파티 생성
                print(f"\n{YELLOW}선택된 파티로 캐릭터 생성 중...{RESET}")
                print(f"{CYAN}최종 선택: {' + '.join(selected_classes)}{RESET}")
                
                # 특성 선택 방식 묻기 (커서 메뉴)
                trait_options = ["🤖 자동 선택 (빠름)", "✋ 수동 선택 (상세)"]
                trait_descriptions = [
                    "AI가 직업에 맞는 특성을 자동으로 선택합니다",
                    "각 캐릭터마다 특성을 직접 선택합니다"
                ]
                trait_menu = CursorMenu("🎭 특성 선택 방식", trait_options, trait_descriptions, cancellable=True)
                trait_result = trait_menu.run()
                
                if trait_result is None:  # 취소
                    return None
                    
                manual_traits = (trait_result == 1)
                
                try:
                    if manual_traits:
                        # 수동 특성 선택을 위해 특성 없이 파티 생성
                        party = self.auto_builder.create_balanced_party(selected_classes, auto_select_traits=False)
                    else:
                        # 자동 특성 선택 포함해서 파티 생성
                        party = self.auto_builder.create_balanced_party(selected_classes, auto_select_traits=True)
                except Exception as e:
                    print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
                    if self._show_yes_no_menu("🔄 오류 발생", "다시 시도하시겠습니까?", "다시 시도", "취소"):
                        return self._custom_party_creation()
                    else:
                        return None
                
                # 수동 특성 선택이면 각 캐릭터마다 특성 선택
                if manual_traits and party:
                    print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
                    for i, character in enumerate(party, 1):
                        print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                        trait_success = self._manual_trait_selection_cursor(character)
                        if not trait_success:  # 특성 선택이 취소된 경우
                            print(f"{RED}특성 선택이 취소되어 파티 생성을 중단합니다.{RESET}")
                            return None
                
                if party:
                    confirm_result = self._confirm_party_cursor(party)
                    if confirm_result is True:
                        return party
                    elif confirm_result is False:
                        return self._custom_party_creation()  # 재생성
                    else:  # confirm_result is None (취소)
                        return None
                else:
                    return self._custom_party_creation()
                    
            except Exception:
                # 폴백: 기존 방식
                return self._custom_party_creation_fallback()
        else:
            # 폴백: 기존 방식
            return self._custom_party_creation_fallback()
    
    def _show_yes_no_menu(self, title: str, question: str, yes_text: str = "예", no_text: str = "아니오") -> bool:
        """Y/N 선택을 위한 커서 메뉴"""
        if CURSOR_MENU_AVAILABLE:
            try:
                options = [f"✅ {yes_text}", f"❌ {no_text}"]
                descriptions = [question, ""]
                
                menu = CursorMenu(title, options, descriptions, cancellable=False)
                result = menu.run()
                
                return result == 0  # 0이면 Yes, 1이면 No
            except Exception:
                # 폴백: 기존 텍스트 방식
                print(f"\n{question} (Y/N)")
                choice = self.keyboard.get_key().lower()
                return choice == 'y'
        else:
            # 폴백: 기존 텍스트 방식
            print(f"\n{question} (Y/N)")
            choice = self.keyboard.get_key().lower()
            return choice == 'y'
    
    def _custom_party_creation_fallback(self) -> List[Character]:
        """커스텀 파티 생성 - 폴백 방식"""
        print(f"\n{CYAN}🛠️ 커스텀 파티 생성{RESET}")
        print("원하는 직업을 선택해서 파티를 구성하세요.")
        
        selected_classes = []
        max_party_size = 4
        
        while len(selected_classes) < max_party_size:
            remaining = max_party_size - len(selected_classes)
            print(f"\n{YELLOW}파티원 {len(selected_classes)+1}/{max_party_size} 선택 (남은 자리: {remaining}){RESET}")
            
            if selected_classes:
                print(f"현재 선택: {' + '.join(selected_classes)}")
            
            # 사용 가능한 직업을 번호로 표시
            available_classes = self.auto_builder.ALL_CLASSES
            self._show_numbered_classes(available_classes)
            
            print(f"\n{WHITE}선택하세요:{RESET}")
            print(f"숫자 입력 후 {GREEN}Enter{RESET}: 직업 선택 (1-{len(available_classes)})")
            print("A: 자동 완성")
            print("B: 이전으로")
            print("L: 목록 다시 보기")
            print(f"\n{YELLOW}> {RESET}", end="")
            
            # 키 입력 처리 로직 (기존 방식)
            choice_input = ""
            while True:
                key = self.keyboard.get_key().lower()
                
                if key == '\r' or key == '\n':
                    if choice_input:
                        choice = choice_input
                        print()
                        break
                    else:
                        continue
                elif key.isdigit():
                    choice_input += key
                    print(key, end='', flush=True)
                elif key in ['a', 'b', 'l']:
                    if choice_input:
                        print('\b' * len(choice_input) + ' ' * len(choice_input) + '\b' * len(choice_input), end='', flush=True)
                        choice_input = ""
                    choice = key
                    print(key)
                    break
                elif key == '\b' or key == '\x7f':
                    if choice_input:
                        choice_input = choice_input[:-1]
                        print('\b \b', end='', flush=True)
            
            # 선택 처리 로직 (기존 코드와 동일)
            if choice == 'a':
                remaining_party = self.auto_builder.create_balanced_party(selected_classes, max_party_size)
                if remaining_party:
                    self._show_created_party(remaining_party)
                    if self._confirm_party():
                        return remaining_party
                continue
            elif choice == 'b':
                if selected_classes:
                    removed = selected_classes.pop()
                    print(f"{removed} 제거됨")
                else:
                    return self.show_character_creation_menu()
                continue
            elif choice == 'l':
                continue
            
            try:
                class_index = int(choice) - 1
                if 0 <= class_index < len(available_classes):
                    selected_class = available_classes[class_index]
                    if selected_class not in selected_classes:
                        selected_classes.append(selected_class)
                        print(f"{GREEN}✅ {selected_class} 추가됨{RESET}")
                    else:
                        print(f"{YELLOW}⚠️ {selected_class}는 이미 선택되었습니다.{RESET}")
                else:
                    print(f"{RED}❌ 잘못된 번호입니다. 1-{len(available_classes)} 사이의 숫자를 입력하세요.{RESET}")
            except ValueError:
                print(f"{RED}❌ 숫자나 명령어(A/B/L)를 입력하세요.{RESET}")
        
        # 파티 생성 완료 처리 (기존 로직)
        print(f"\n{YELLOW}선택된 파티로 캐릭터 생성 중...{RESET}")
        print(f"{CYAN}최종 선택: {' + '.join(selected_classes)}{RESET}")
        
        # 특성 선택 방식 묻기 (커서 메뉴)
        trait_options = ["🤖 자동 선택 (빠름)", "✋ 수동 선택 (상세)"]
        trait_descriptions = [
            "특성을 자동으로 선택하여 빠르게 게임을 시작합니다",
            "커서를 사용하여 특성을 직접 선택합니다"
        ]
        
        try:
            if CURSOR_MENU_AVAILABLE:
                trait_menu = CursorMenu("🎭 특성 선택 방식", trait_options, trait_descriptions, cancellable=True)
                trait_choice_idx = trait_menu.run()
                if trait_choice_idx is None:
                    return None
                manual_traits = (trait_choice_idx == 1)  # 0: 자동, 1: 수동
            else:
                # 폴백: 키보드 방식
                print(f"\n{YELLOW}특성 선택 방식:{RESET}")
                print("1. 자동 선택 (빠름)")
                print("2. 수동 선택 (상세)")
                
                trait_choice = self.keyboard.get_key()
                manual_traits = (trait_choice == '2')
        except Exception as e:
            # 폴백: 키보드 방식
            print(f"\n{YELLOW}특성 선택 방식:{RESET}")
            print("1. 자동 선택 (빠름)")
            print("2. 수동 선택 (상세)")
            
            trait_choice = self.keyboard.get_key()
            manual_traits = (trait_choice == '2')
        
        try:
            if manual_traits:
                # 수동 특성 선택을 위해 특성 없이 파티 생성
                party = self.auto_builder.create_balanced_party(selected_classes, auto_select_traits=False)
            else:
                # 자동 특성 선택 포함해서 파티 생성
                party = self.auto_builder.create_balanced_party(selected_classes, auto_select_traits=True)
        except Exception as e:
            print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
            if self._show_yes_no_menu("🔄 오류 발생", "다시 시도하시겠습니까?", "다시 시도", "취소"):
                return self._custom_party_creation_fallback()
            else:
                return None
        
        if manual_traits and party:
            print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
            for i, character in enumerate(party, 1):
                print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                trait_success = self._manual_trait_selection(character)
                if not trait_success:  # 특성 선택이 취소된 경우
                    print(f"{RED}특성 선택이 취소되어 파티 생성을 중단합니다.{RESET}")
                    return None
        
        if party:
            self._show_created_party(party)
            if self._confirm_party():
                return party
            else:
                return self._custom_party_creation_fallback()
        return None
    
    def _single_character_creation(self) -> List[Character]:
        """개별 캐릭터 생성 (특성 선택 포함)"""
        print(f"\n{CYAN}👤 개별 캐릭터 생성{RESET}")
        print("각 캐릭터마다 직업과 특성을 직접 선택합니다.")
        
        # 특성 선택 방식을 파티 생성 시작 시 한 번만 묻기
        manual_traits = self._should_select_traits()
        if manual_traits:
            print(f"{GREEN}✅ 수동 특성 선택 모드{RESET}")
        else:
            print(f"{GREEN}✅ 자동 특성 선택 모드{RESET}")
        
        party = []
        max_party_size = 4
        
        for i in range(max_party_size):
            print(f"\n{YELLOW}━━━ 파티원 {i+1}/{max_party_size} ━━━{RESET}")
            
            # 직업 선택
            character_class = self._select_character_class()
            if not character_class:
                if i == 0:
                    return self.show_character_creation_menu()
                break
            
            # 캐릭터 생성
            try:
                character = self._create_single_character(character_class, i+1)
                
                # 특성 선택 (파티 시작 시 결정된 방식 사용)
                if manual_traits:
                    # 수동 특성 선택
                    print(f"\n{CYAN}🎯 {character.name}의 특성을 선택하세요{RESET}")
                    character.select_traits("manual")
                else:
                    # 자동 특성 선택
                    self._auto_select_traits(character)
                
                party.append(character)
            except Exception as e:
                print(f"{RED}캐릭터 생성 중 오류 발생: {e}{RESET}")
                if not self._show_yes_no_menu("⚠️ 오류 발생", "이 캐릭터를 건너뛰고 계속하시겠습니까?", "건너뛰기", "메뉴로 돌아가기"):
                    return self.show_character_creation_menu()
                continue
            print(f"{GREEN}✅ {character.name} ({character_class}) 생성 완료{RESET}")
            
            # 계속할지 묻기 - 커서 방식
            if i < max_party_size - 1:
                if CURSOR_MENU_AVAILABLE:
                    try:
                        continue_options = ["✅ 예, 다음 파티원 추가", "❌ 아니오, 현재 파티로 완료"]
                        continue_descriptions = [
                            "다음 파티원을 계속 생성합니다",
                            f"현재 {len(party)}명의 파티로 게임을 시작합니다"
                        ]
                        
                        continue_menu = CursorMenu(
                            f"🎭 파티 구성 ({len(party)}/{max_party_size})", 
                            continue_options, 
                            continue_descriptions, 
                            cancellable=False
                        )
                        continue_result = continue_menu.run()
                        
                        if continue_result == 1:  # 아니오
                            break
                    except Exception:
                        # 폴백: 기존 방식
                        print(f"\n다음 파티원을 추가하시겠습니까? (Y/n)")
                        continue_choice = self.keyboard.get_key().lower()
                        if continue_choice == 'n':
                            break
                else:
                    # 폴백: 기존 방식
                    print(f"\n다음 파티원을 추가하시겠습니까? (Y/n)")
                    continue_choice = self.keyboard.get_key().lower()
                    if continue_choice == 'n':
                        break
        
        if party:
            self._show_created_party(party)
            if self._confirm_party():
                return party
            else:
                return self._single_character_creation()
        return None
    
    def _select_character_class(self) -> Optional[str]:
        """직업 선택 - 역할군별 분류"""
        if CURSOR_MENU_AVAILABLE:
            try:
                from .color_text import bright_red, bright_blue, bright_green, bright_yellow, bright_magenta, bright_cyan
                
                while True:
                    # 역할군별 캐릭터 분류
                    role_categories = {
                        "🛡️ 탱커": {
                            "classes": ["전사", "성기사", "기사", "암흑기사"],
                            "color": bright_red,
                            "description": "높은 체력과 방어력으로 파티를 보호합니다"
                        },
                        "⚔️ 물리 딜러": {
                            "classes": ["검성", "사무라이", "암살자", "몽크", "검투사", "광전사", "궁수", "도적", "해적", "기계공학자"],
                            "color": bright_yellow,
                            "description": "물리 공격으로 적을 제압하는 전투 전문가"
                        },
                        "🔮 마법사": {
                            "classes": ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사"],
                            "color": bright_blue,
                            "description": "강력한 마법으로 적을 소멸시킵니다"
                        },
                        "✨ 서포터": {
                            "classes": ["바드", "드루이드", "신관", "무당"],
                            "color": bright_cyan,
                            "description": "파티원을 치유하고 강화하는 지원 역할"
                        },
                        "🎯 특수 클래스": {
                            "classes": ["용기사", "철학자", "마검사"],
                            "color": bright_magenta,
                            "description": "독특한 능력을 가진 특별한 클래스들"
                        }
                    }
                    
                    # 메뉴 옵션 생성
                    options = []
                    descriptions = []
                    
                    for category_name, category_data in role_categories.items():
                        color_func = category_data["color"]
                        options.append(color_func(category_name))
                        descriptions.append(category_data["description"])
                    
                    # 빠른 선택 옵션들
                    options.extend([
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        "🎯 균형잡힌 파티 (추천)",
                        "🎲 랜덤 선택"
                    ])
                    descriptions.extend([
                        "",
                        "전사, 아크메이지, 궁수, 바드의 밸런스 좋은 조합",
                        "무작위로 직업을 선택합니다"
                    ])
                    
                    menu = CursorMenu("🎭 직업 선택 - 역할군별", options, descriptions, cancellable=True)
                    result = menu.run()
                    
                    if result is None:  # 취소
                        return None
                    elif result == len(role_categories):  # 구분선
                        continue
                    elif result == len(role_categories) + 1:  # 균형잡힌 파티
                        return "balanced_party"
                    elif result == len(role_categories) + 2:  # 랜덤 선택
                        import random
                        all_classes = []
                        for category_data in role_categories.values():
                            all_classes.extend(category_data["classes"])
                        return random.choice(all_classes)
                    else:
                        # 역할군 선택됨 - 해당 역할군의 클래스들 표시
                        category_names = list(role_categories.keys())
                        selected_category = category_names[result]
                        selected_classes = role_categories[selected_category]["classes"]
                        color_func = role_categories[selected_category]["color"]
                        
                        # 역할군 내 클래스 선택
                        class_options = []
                        class_descriptions = []
                        
                        for class_name in selected_classes:
                            class_options.append(color_func(f"🎭 {class_name}"))
                            # 클래스별 간단한 설명 추가
                            class_desc = self._get_class_description(class_name)
                            class_descriptions.append(class_desc)
                        
                        class_menu = CursorMenu(
                            f"{selected_category} 선택", 
                            class_options, 
                            class_descriptions, 
                            cancellable=True
                        )
                        
                        class_result = class_menu.run()
                        
                        if class_result is not None:
                            return selected_classes[class_result]
                        # class_result가 None이면 상위 메뉴로 돌아감
                        
            except Exception:
                # 폴백: 기존 방식
                return self._select_character_class_fallback()
        else:
            # 폴백: 기존 방식
            return self._select_character_class_fallback()
    
    def _get_class_description(self, class_name: str) -> str:
        """클래스별 간단한 설명"""
        descriptions = {
            # 탱커
            "전사": "균형잡힌 전투 능력의 기본 탱커",
            "성기사": "치유 능력이 있는 신성한 수호자",
            "기사": "높은 방어력과 기동성을 가진 기사단",
            "암흑기사": "어둠의 힘으로 적을 압도하는 탱커",
            
            # 물리 딜러
            "검성": "검술의 달인, 강력한 검기 공격",
            "사무라이": "일격필살의 검술과 무사도 정신",
            "암살자": "은밀함과 치명타로 적을 제거",
            "몽크": "맨손 격투와 내공을 다루는 수행자",
            "검투사": "투기장의 전사, 연속 공격 특화",
            "광전사": "분노로 전투력이 증가하는 전사",
            
            # 원거리 딜러
            "궁수": "정확한 활 사격의 원거리 전문가",
            "도적": "빠른 몸놀림과 기습 공격",
            "해적": "총기와 함께 바다를 누비는 자유인",
            "기계공학자": "발명품과 기계 장치로 전투",
            
            # 마법사
            "아크메이지": "모든 원소 마법의 대마법사",
            "네크로맨서": "죽음과 언데드를 다루는 마법사",
            "정령술사": "자연 정령과 소통하는 마법사",
            "시간술사": "시간을 조작하는 신비한 마법사",
            "연금술사": "물질 변환과 독을 다루는 학자",
            "차원술사": "공간과 차원을 조작하는 마법사",
            
            # 서포터
            "바드": "음악으로 파티를 버프하는 예술가",
            "드루이드": "자연의 힘으로 치유하는 현자",
            "신관": "신성한 치유와 축복의 성직자",
            "무당": "영혼과 저주를 다루는 샤먼",
            
            # 특수
            "용기사": "용의 힘을 다루는 전설적 존재",
            "철학자": "지혜와 논리로 전투하는 사상가",
            "마검사": "마법과 검술을 융합한 전사"
        }
        return descriptions.get(class_name, "특별한 능력을 가진 클래스")
    
    def _select_character_class_fallback(self) -> Optional[str]:
        """직업 선택 - 폴백 방식"""
        available_classes = self.auto_builder.ALL_CLASSES
        
        while True:
            print(f"\n{WHITE}직업을 선택하세요:{RESET}")
            self._show_numbered_classes(available_classes)
            print(f"\n숫자 입력 후 {GREEN}Enter{RESET}: 직업 선택 (1-{len(available_classes)})")
            print("B: 돌아가기")
            print(f"\n{YELLOW}> {RESET}", end="")
            
            # 두 자리 숫자 입력 지원
            choice_input = ""
            while True:
                key = self.keyboard.get_key().lower()
                
                if key == '\r' or key == '\n':  # Enter 키
                    if choice_input:
                        choice = choice_input
                        print()  # 줄바꿈
                        break
                    else:
                        continue
                elif key.isdigit():
                    choice_input += key
                    print(key, end='', flush=True)
                    # Enter를 기다림 (자동 선택 제거)
                elif key == 'b':
                    if choice_input:
                        print('\b' * len(choice_input) + ' ' * len(choice_input) + '\b' * len(choice_input), end='', flush=True)
                        choice_input = ""
                    choice = key
                    print(key)
                    break
                elif key == '\b' or key == '\x7f':  # 백스페이스
                    if choice_input:
                        choice_input = choice_input[:-1]
                        print('\b \b', end='', flush=True)
            
            if choice == 'b':
                return None
            
            try:
                class_index = int(choice) - 1
                if 0 <= class_index < len(available_classes):
                    return available_classes[class_index]
                else:
                    print(f"{RED}❌ 잘못된 번호입니다. 1-{len(available_classes)} 사이의 숫자를 입력하세요.{RESET}")
            except ValueError:
                print(f"{RED}❌ 숫자나 'B'를 입력하세요.{RESET}")
    
    def _should_select_traits(self) -> bool:
        """특성을 수동으로 선택할지 묻기"""
        trait_options = ["🤖 자동 선택 - 빠르게 게임 시작 (추천)", "✋ 수동 선택 - 커서로 특성 직접 선택"]
        trait_descriptions = [
            "특성을 자동으로 선택하여 빠르게 게임을 시작합니다",
            "커서를 사용하여 특성을 직접 선택합니다. 특성은 게임 중 자동으로 발동되는 패시브 능력입니다"
        ]
        
        if CURSOR_MENU_AVAILABLE:
            try:
                trait_menu = CursorMenu("🎭 특성 선택 방식을 정하세요", trait_options, trait_descriptions, cancellable=False)
                trait_choice = trait_menu.run()
                if trait_choice == 1:  # 수동 선택
                    print(f"{CYAN}✅ 수동 선택이 선택되었습니다.{RESET}")
                    return True
                else:  # 자동 선택
                    print(f"{GREEN}✅ 자동 선택이 선택되었습니다.{RESET}")
                    return False
            except Exception:
                # 폴백: 키보드 방식
                print(f"\n{YELLOW}🎭 특성 선택 방식을 정하세요:{RESET}")
                print(f"{GREEN}1.{RESET} {WHITE}자동 선택{RESET} - 빠르게 게임 시작 (추천)")
                print(f"{CYAN}2.{RESET} {WHITE}수동 선택{RESET} - 커서로 특성 직접 선택")
                print()
                print(f"{YELLOW}💡 특성은 게임 중 자동으로 발동되는 패시브 능력입니다{RESET}")
                
                choice = self.keyboard.get_key()
                if choice == '2':
                    print(f"{CYAN}✅ 수동 선택이 선택되었습니다.{RESET}")
                    return True
                else:
                    print(f"{GREEN}✅ 자동 선택이 선택되었습니다.{RESET}")
                    return False
        else:
            # 폴백: 키보드 방식
            print(f"\n{YELLOW}🎭 특성 선택 방식을 정하세요:{RESET}")
            print(f"{GREEN}1.{RESET} {WHITE}자동 선택{RESET} - 빠르게 게임 시작 (추천)")
            print(f"{CYAN}2.{RESET} {WHITE}수동 선택{RESET} - 커서로 특성 직접 선택")
            print()
            print(f"{YELLOW}💡 특성은 게임 중 자동으로 발동되는 패시브 능력입니다{RESET}")
            
            choice = self.keyboard.get_key()
            if choice == '2':
                print(f"{CYAN}✅ 수동 선택이 선택되었습니다.{RESET}")
                return True
            else:
                print(f"{GREEN}✅ 자동 선택이 선택되었습니다.{RESET}")
                return False
    
    def _manual_trait_selection(self, character: Character):
        """수동 특성 선택 - 커서 방식"""
        print(f"\n{WHITE}{BOLD}{'='*50}{RESET}")
        print(f"{WHITE}{BOLD}🎯 {character.name} ({character.character_class})의 특성 선택{RESET}")
        print(f"{WHITE}{BOLD}{'='*50}{RESET}")
        
        if not character.available_traits:
            print(f"{YELLOW}❌ 사용 가능한 특성이 없습니다.{RESET}")
            return
        
        if CURSOR_MENU_AVAILABLE:
            return self._manual_trait_selection_cursor(character)
        else:
            return self._manual_trait_selection_fallback(character)
    
    def _manual_trait_selection_cursor(self, character: Character) -> bool:
        """커서 기반 특성 선택"""
        try:
            selected_indices = []
            max_traits = 2
            
            while len(selected_indices) < max_traits:
                remaining = max_traits - len(selected_indices)
                
                # 메뉴 옵션 생성
                options = []
                descriptions = []
                
                for i, trait in enumerate(character.available_traits):
                    # 특성 효과에 따른 아이콘
                    trait_icon = "⚔️"
                    if "공격" in trait.description or "데미지" in trait.description:
                        trait_icon = "⚔️"
                    elif "방어" in trait.description or "HP" in trait.description:
                        trait_icon = "🛡️"
                    elif "속도" in trait.description or "회피" in trait.description:
                        trait_icon = "💨"
                    elif "마법" in trait.description or "MP" in trait.description:
                        trait_icon = "🔮"
                    elif "회복" in trait.description or "치유" in trait.description:
                        trait_icon = "💚"
                    elif "크리티컬" in trait.description or "치명타" in trait.description:
                        trait_icon = "💥"
                    
                    # 선택 상태 표시
                    status = " ✅" if i in selected_indices else ""
                    option_text = f"{trait_icon} {trait.name}{status}"
                    
                    options.append(option_text)
                    descriptions.append(trait.description)
                
                # 특별 옵션들
                if selected_indices:
                    options.extend([
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        "✅ 선택 완료",
                        "🔄 선택 초기화"
                    ])
                    descriptions.extend([
                        "",
                        f"현재 선택된 {len(selected_indices)}개 특성으로 완료합니다",
                        "모든 선택을 취소하고 처음부터 다시 선택합니다"
                    ])
                
                title = f"🎯 특성 선택 ({len(selected_indices)}/{max_traits}) - {character.name}"
                if selected_indices:
                    selected_names = [character.available_traits[i].name for i in selected_indices]
                    title += f"\n선택됨: {', '.join(selected_names)}"
                
                menu = CursorMenu(title, options, descriptions, cancellable=True)
                result = menu.run()
                
                if result is None:  # 취소
                    return False
                elif result < len(character.available_traits):  # 특성 선택/해제
                    trait_index = result
                    if trait_index in selected_indices:
                        # 선택 해제
                        selected_indices.remove(trait_index)
                        trait_name = character.available_traits[trait_index].name
                        print(f"{YELLOW}❌ {trait_name} 선택 해제됨{RESET}")
                    else:
                        # 선택 추가
                        selected_indices.append(trait_index)
                        trait_name = character.available_traits[trait_index].name
                        print(f"{GREEN}✅ {trait_name} 선택됨!{RESET}")
                        
                        # 최대 개수 도달하면 자동 완료
                        if len(selected_indices) >= max_traits:
                            break
                            
                elif result == len(character.available_traits) + 1:  # 선택 완료
                    if selected_indices:
                        break
                    else:
                        print(f"{YELLOW}⚠️ 최소 1개의 특성을 선택해주세요.{RESET}")
                        continue
                        
                elif result == len(character.available_traits) + 2:  # 선택 초기화
                    selected_indices = []
                    print(f"{YELLOW}🔄 선택이 초기화되었습니다.{RESET}")
                    continue
            
            # 특성 적용
            if selected_indices:
                character.select_passive_traits(selected_indices)
                selected_traits = [character.available_traits[i].name for i in selected_indices]
                print(f"\n{GREEN}{'='*50}{RESET}")
                print(f"{GREEN}🎉 특성 선택 완료!{RESET}")
                print(f"{WHITE}선택된 특성: {BOLD}{', '.join(selected_traits)}{RESET}")
                print(f"{GREEN}{'='*50}{RESET}")
                return True
            else:
                print(f"\n{YELLOW}🔄 특성 없이 진행합니다.{RESET}")
                return True
                
        except Exception as e:
            print(f"{RED}커서 메뉴 오류: {e}{RESET}")
            return self._manual_trait_selection_fallback(character)
    
    def _manual_trait_selection_fallback(self, character: Character) -> bool:
        """키보드 기반 특성 선택 (폴백)"""
        print(f"{GREEN}📋 사용 가능한 특성:{RESET}")
        print()
        
        for i, trait in enumerate(character.available_traits, 1):
            # 특성 효과에 따른 색상과 아이콘
            trait_icon = "⚔️"
            trait_color = WHITE
            
            if "공격" in trait.description or "데미지" in trait.description:
                trait_icon = "⚔️"
                trait_color = RED
            elif "방어" in trait.description or "HP" in trait.description:
                trait_icon = "🛡️"
                trait_color = BLUE
            elif "속도" in trait.description or "회피" in trait.description:
                trait_icon = "💨"
                trait_color = CYAN
            elif "마법" in trait.description or "MP" in trait.description:
                trait_icon = "🔮"
                trait_color = MAGENTA
            elif "회복" in trait.description or "치유" in trait.description:
                trait_icon = "💚"
                trait_color = GREEN
            elif "크리티컬" in trait.description or "치명타" in trait.description:
                trait_icon = "💥"
                trait_color = YELLOW
            
            print(f"{GREEN}{i:2}.{RESET} {trait_icon} {trait_color}{BOLD}{trait.name}{RESET}")
            print(f"     {WHITE}{trait.description}{RESET}")
            print()
        
        print(f"{CYAN}{'='*50}{RESET}")
        print(f"{YELLOW}💡 최대 2개까지 선택할 수 있습니다.{RESET}")
        print(f"{WHITE}   숫자를 눌러 특성을 선택하세요.{RESET}")
        print(f"{CYAN}{'='*50}{RESET}")
        
        selected_indices = []
        while len(selected_indices) < 2:
            remaining = 2 - len(selected_indices)
            
            print(f"\n{YELLOW}🎯 특성 {len(selected_indices)+1}/2 선택{RESET} {WHITE}(남은 선택: {remaining}){RESET}")
            
            if selected_indices:
                selected_names = [character.available_traits[i].name for i in selected_indices]
                print(f"{GREEN}현재 선택: {BOLD}{', '.join(selected_names)}{RESET}")
            
            print(f"\n{WHITE}선택하세요:{RESET}")
            print(f"{GREEN}1-{len(character.available_traits)}{RESET}: 특성 선택")
            print(f"{BLUE}S{RESET}: 선택 완료")
            print(f"{RED}C{RESET}: 선택 취소")
            print(f"{YELLOW}V{RESET}: 특성 목록 다시 보기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == 's':
                if selected_indices:
                    break  # 선택 완료
                else:
                    print(f"{YELLOW}⚠️ 최소 1개의 특성을 선택해주세요.{RESET}")
                    continue
            elif choice == 'c':
                selected_indices = []
                print(f"{YELLOW}🔄 선택이 취소되었습니다.{RESET}")
                continue
            elif choice == 'v':
                # 특성 목록 다시 표시
                print(f"\n{GREEN}📋 사용 가능한 특성:{RESET}")
                print()
                for i, trait in enumerate(character.available_traits, 1):
                    trait_icon = "⚔️"
                    trait_color = WHITE
                    
                    if "공격" in trait.description or "데미지" in trait.description:
                        trait_icon = "⚔️"
                        trait_color = RED
                    elif "방어" in trait.description or "HP" in trait.description:
                        trait_icon = "🛡️"
                        trait_color = BLUE
                    elif "속도" in trait.description or "회피" in trait.description:
                        trait_icon = "💨"
                        trait_color = CYAN
                    elif "마법" in trait.description or "MP" in trait.description:
                        trait_icon = "🔮"
                        trait_color = MAGENTA
                    elif "회복" in trait.description or "치유" in trait.description:
                        trait_icon = "💚"
                        trait_color = GREEN
                    elif "크리티컬" in trait.description or "치명타" in trait.description:
                        trait_icon = "💥"
                        trait_color = YELLOW
                    
                    status = ""
                    if i-1 in selected_indices:
                        status = f" {GREEN}✅{RESET}"
                    
                    print(f"{GREEN}{i:2}.{RESET} {trait_icon} {trait_color}{BOLD}{trait.name}{RESET}{status}")
                    print(f"     {WHITE}{trait.description}{RESET}")
                    print()
                continue
            
            try:
                trait_index = int(choice) - 1
                if 0 <= trait_index < len(character.available_traits):
                    if trait_index not in selected_indices:
                        selected_indices.append(trait_index)
                        trait = character.available_traits[trait_index]
                        print(f"{GREEN}✅ {BOLD}{trait.name}{RESET} {GREEN}선택됨!{RESET}")
                    else:
                        # 이미 선택된 특성을 다시 누르면 해제
                        selected_indices.remove(trait_index)
                        trait = character.available_traits[trait_index]
                        print(f"{YELLOW}❌ {BOLD}{trait.name}{RESET} {YELLOW}선택 해제됨{RESET}")
                else:
                    print(f"{RED}❌ 잘못된 번호: {choice}{RESET}")
            except ValueError:
                print(f"{RED}❌ 숫자나 명령어(S/C/V)를 입력하세요.{RESET}")
        
        character.select_passive_traits(selected_indices)
        
        # 선택 완료 메시지
        if selected_indices:
            selected_traits = [character.available_traits[i].name for i in selected_indices]
            print(f"\n{GREEN}{'='*50}{RESET}")
            print(f"{GREEN}🎉 특성 선택 완료!{RESET}")
            print(f"{WHITE}선택된 특성: {BOLD}{', '.join(selected_traits)}{RESET}")
            print(f"{GREEN}{'='*50}{RESET}")
        else:
            print(f"\n{YELLOW}🔄 특성 없이 진행합니다.{RESET}")
        
        return True
    
    def _auto_select_traits(self, character: Character):
        """자동 특성 선택"""
        self.auto_builder._auto_select_passives(character)
        
        if character.selected_traits:
            trait_names = [trait.name for trait in character.selected_traits]
            print(f"{GREEN}자동 선택된 특성: {', '.join(trait_names)}{RESET}")
        else:
            print(f"{YELLOW}선택된 특성이 없습니다.{RESET}")
    
    def _create_single_character(self, class_name: str, index: int) -> Character:
        """단일 캐릭터 생성"""
        return self.auto_builder._create_character(class_name, index)
    
    def _show_available_classes(self, classes: List[str]):
        """사용 가능한 직업 목록 표시"""
        print(f"\n{CYAN}사용 가능한 직업:{RESET}")
        
        # 역할별로 분류해서 표시
        role_classes = self.auto_builder.ROLE_CLASSES
        
        for role, role_class_list in role_classes.items():
            available_in_role = [c for c in role_class_list if c in classes]
            if available_in_role:
                print(f"\n{YELLOW}{role}:{RESET}")
                for i, class_name in enumerate(available_in_role):
                    if i % 4 == 0 and i > 0:
                        print()
                    print(f"{class_name:<12}", end=" ")
                print()
    
    def _show_numbered_classes(self, classes: List[str]):
        """번호와 함께 직업 목록 표시"""
        print(f"\n{CYAN}사용 가능한 직업:{RESET}")
        
        # 역할별로 분류해서 번호와 함께 표시
        role_classes = self.auto_builder.ROLE_CLASSES
        current_number = 1
        
        for role, role_class_list in role_classes.items():
            available_in_role = [c for c in role_class_list if c in classes]
            if available_in_role:
                print(f"\n{YELLOW}{role}:{RESET}")
                for class_name in available_in_role:
                    class_index = classes.index(class_name) + 1
                    print(f"{GREEN}{class_index:2}.{RESET} {class_name}")
                print()
    
    def _find_matching_class(self, input_text: str, available_classes: List[str]) -> Optional[str]:
        """입력 텍스트와 일치하는 직업 찾기"""
        input_text = input_text.strip()
        
        # 정확한 일치
        for class_name in available_classes:
            if class_name == input_text:
                return class_name
        
        # 부분 일치
        for class_name in available_classes:
            if input_text in class_name or class_name in input_text:
                return class_name
        
        return None
    
    def _show_created_party(self, party: List[Character]):
        """생성된 파티 표시"""
        # 파티 정보 저장 (특성 상세 보기용)
        self.last_generated_party = party
        
        # 특성 설명 딕셔너리 (모든 클래스 5개씩)
        trait_descriptions = {
            # 전사 특성
            "불굴의 의지": "HP가 25% 이하일 때 공격력 50% 증가",
            "전투 광기": "적을 처치할 때마다 다음 공격의 피해량 20% 증가",
            "방어 숙련": "방어 시 받는 피해 30% 추가 감소",
            "위협적 존재": "전투 시작 시 적들의 공격력 10% 감소",
            "피의 갈증": "HP가 50% 이상일 때 공격속도 25% 증가",
            
            # 아크메이지 특성
            "마나 순환": "스킬 사용 시 30% 확률로 MP 소모량 절반",
            "원소 지배": "속성 마법 사용 시 해당 속성 저항 20% 증가",
            "마법 연구자": "전투 후 획득 경험치 15% 증가",
            "마법 폭주": "크리티컬 마법 시 주변 적들에게 연쇄 피해",
            "마력 집중": "MP가 75% 이상일 때 마법 피해 40% 증가",
            
            # 궁수 특성
            "정밀 사격": "크리티컬 확률 25% 증가",
            "원거리 숙련": "첫 공격 시 항상 크리티컬",
            "민첩한 몸놀림": "회피 확률 20% 증가",
            "사냥꾼의 직감": "적의 약점을 간파해 방어력 무시 확률 15%",
            "바람의 가호": "이동 시 다음 공격의 명중률과 피해량 15% 증가",
            
            # 도적 특성
            "그림자 은신": "전투 시작 시 3턴간 은신 상태",
            "치명적 급소": "크리티컬 시 추가 출혈 효과 부여",
            "빠른 손놀림": "아이템 사용 시 턴 소모하지 않음",
            "도적의 직감": "함정과 보물 발견 확률 50% 증가",
            "독 숙련": "모든 공격에 10% 확률로 독 효과 추가",
            
            # 성기사 특성
            "신성한 가호": "언데드와 악마에게 받는 피해 50% 감소",
            "치유의 빛": "공격 시 30% 확률로 파티원 전체 소량 회복",
            "정의의 분노": "아군이 쓰러질 때 공격력과 마법력 30% 증가",
            "축복받은 무기": "모든 공격에 성속성 추가 피해",
            "수호의 맹세": "파티원 보호 시 받는 피해 50% 감소",
            
            # 암흑기사 특성
            "생명 흡수": "가한 피해의 15%만큼 HP 회복",
            "어둠의 계약": "HP가 낮을수록 공격력 증가 (최대 100%)",
            "공포 오라": "적들이 간헐적으로 행동 불가",
            "불사의 의지": "치명상 시 1회 한정 완전 회복",
            "어둠 조작": "턴 종료 시 20% 확률로 적에게 암속성 피해",
            
            # 몽크 특성
            "내공 순환": "MP가 가득 찰 때마다 모든 능력치 일시 증가",
            "연타 숙련": "연속 공격 시마다 피해량 누적 증가",
            "정신 수양": "상태이상 저항 50% 증가",
            "기절 공격": "일정 확률로 적을 기절시켜 1턴 행동 불가",
            "참선의 깨달음": "전투 중 매 5턴마다 MP 완전 회복",
            
            # 광전사 특성
            "광기 상태": "HP가 낮을수록 공격력과 속도 증가",
            "무모한 돌진": "방어 무시하고 최대 피해 공격",
            "고통 무시": "상태이상 무효",
            "전투 광증": "적 처치 시 즉시 재행동",
            "불사의 의지": "치명상 시 3턴간 불사 상태",
            
            # 바드 특성
            "전투 노래": "파티원들의 공격력 15% 증가",
            "치유의 선율": "턴 종료 시 파티 전체 소량 회복",
            "용기의 찬송": "파티원들의 크리티컬 확률 10% 증가",
            "마법 해제": "적의 버프를 무효화하는 확률 25%",
            "영감의 리듬": "스킬 사용 시 아군의 MP 회복",
            
            # 네크로맨서 특성
            "어둠의 계약": "적 처치 시 MP 회복량 2배",
            "생명력 흡수": "적에게 피해를 줄 때 HP와 MP 동시 회복",
            "저주술": "공격 시 25% 확률로 적에게 저주 부여",
            "죽음의 오라": "주변 적들의 회복 효과 50% 감소",
            "영혼 흡수": "적 처치 시 최대 MP 일시 증가",
            
            # 용기사 특성
            "용의 숨결": "모든 공격에 화염 속성 추가",
            "비늘 방어": "받는 물리 피해 15% 감소",
            "용의 분노": "HP가 낮을수록 공격속도 증가",
            "날개 돌격": "크리티컬 시 추가 행동 기회",
            "용족의 긍지": "디버프 저항 40% 증가",
            
            # 검성 특성
            "검술 달인": "무기 공격력 30% 증가",
            "연속 베기": "공격 성공 시 30% 확률로 즉시 재공격",
            "검기 충격": "공격 시 25% 확률로 2배 피해",
            "완벽한 방어": "방어 시 100% 피해 무효화",
            "검의 의지": "무기 파괴 무효",
            
            # 정령술사 특성
            "정령 친화": "모든 속성 마법 위력 25% 증가",
            "자연의 축복": "턴 시작 시 MP 자동 회복",
            "원소 조화": "서로 다른 속성 연계 시 추가 피해",
            "원소 폭발": "마법 크리티컬 시 광역 피해",
            
            # 암살자 특성
            "그림자 이동": "첫 턴에 반드시 선공",
            "치명타 특화": "크리티컬 확률 40% 증가",
            "독날 무기": "모든 공격에 독 효과",
            "은신 공격": "은신 상태에서 공격 시 피해 200% 증가",
            "연막탄": "전투 도중 은신 상태 진입 가능",
            
            # 기계공학자 특성
            "자동 포탑": "전투 시작 시 포탑 설치",
            "기계 정비": "전투 후 5턴간 장비 효과 10% 증가",
            "폭탄 제작": "소모품 폭탄 무한 사용",
            "강화 장비": "모든 장비 효과 20% 증가",
            "오버클럭": "일시적으로 모든 능력치 50% 증가",
            
            # 무당 특성
            "시야 확장": "필드 시야 범위 +1",
            "정령 가호": "상태이상 저항 40% 증가",
            "악령 퇴치": "언데드에게 추가 피해 50%",
            "무당의 직감": "크리티컬 받을 확률 30% 감소",
            "영적 보호": "즉사 공격 무효",
            
            # 해적 특성
            "보물 사냥꾼": "골드 획득량 30% 증가",
            "이도류 전투": "공격 시 30% 확률로 2회 공격",
            "바다의 분노": "연속 공격 시 피해량 누적 증가",
            "럭키 스트라이크": "크리티컬 시 20% 확률로 골드 추가 획득",
            "해적의 경험": "전투 후 경험치 15% 추가 획득",
            
            # 사무라이 특성
            "일격필살": "HP 25% 이하일 때 크리티컬 확률 50% 증가",
            "카타나 숙련": "검류 무기 공격력 40% 증가",
            "참선": "전투 외 MP 회복 속도 2배",
            "무사도": "HP 10% 이하일 때 모든 공격 크리티컬",
            "명예의 맹세": "디버프 무효, 모든 능력치 15% 증가",
            
            # 드루이드 특성
            "자연의 가호": "턴 시작 시 HP/MP 소량 회복",
            "자연 치유": "야외에서 지속적인 HP 회복",
            "식물 조종": "적의 이동 제한 스킬",
            "동물 변신": "늑대형태: 공속+30%, 곰형태: 방어+30%, 독수리형태: 회피+25%",
            "계절의 힘": "전투마다 랜덤 속성 강화",
            
            # 철학자 특성
            "현자의 지혜": "모든 스킬 MP 소모량 20% 감소",
            "논리적 사고": "적의 패턴 분석으로 회피율 증가",
            "깨달음": "경험치 획득량 25% 증가",
            "사색의 힘": "MP가 가득 찰 때마다 지혜 스택 증가",
            "철학적 논증": "적을 혼란에 빠뜨리는 스킬",
            
            # 시간술사 특성
            "시간 정지": "적의 행동을 1턴 지연",
            "과거 회귀": "한 번 받은 피해 되돌리기",
            "시간 인식": "적의 다음 행동 타입 미리 파악",
            "순간 가속": "크리티컬 시 20% 확률로 즉시 재행동",
            "인과 조작": "공격 실패 시 재계산 가능",
            
            # 연금술사 특성
            "포션 제조": "회복 아이템 효과 2배",
            "원소 변환": "적의 속성 저항 무시",
            "폭발물 전문": "폭발 계열 스킬 위력 50% 증가",
            "실험 정신": "디버프 지속시간 25% 증가",
            "마법 물질": "모든 공격에 랜덤 속성 추가",
            
            # 검투사 특성
            "관중의 환호": "적을 많이 처치할수록 능력치 증가",
            "검투 기술": "반격 확률 30% 증가",
            "투기장 경험": "1대1 전투 시 모든 능력치 25% 증가",
            "생존 본능": "HP 30% 이하에서 회피율 50% 증가",
            "전사의 혼": "파티원이 전멸해도 5턴간 홀로 전투 지속",
            
            # 기사 특성
            "명예의 수호": "아군 보호 시 받는 피해 30% 감소",
            "창술 숙련": "창류 무기 공격력 35% 증가",
            "기사도 정신": "디버프 지속시간 50% 감소",
            "용맹한 돌격": "첫 공격이 크리티컬일 시 추가 피해",
            "영광의 맹세": "파티원 수만큼 능력치 증가",
            
            # 신관 특성
            "신의 가호": "치명타 무효화 확률 20%",
            "성스러운 빛": "언데드에게 2배 피해",
            "치유 특화": "모든 회복 효과 50% 증가",
            "축복의 기도": "파티 전체 버프 효과",
            "신탁": "랜덤하게 강력한 기적 발생",
            
            # 마검사 특성
            "마검 일체": "물리와 마법 공격력 동시 적용",
            "마력 충전": "공격할 때마다 MP 회복",
            "검기 폭발": "검 공격에 마법 피해 추가",
            "이중 속성": "두 가지 속성 동시 공격",
            "마검 오의": "궁극기 사용 시 모든 적에게 피해",
            
            # 차원술사 특성
            "차원 보관": "무제한 아이템 보관",
            "공간 이동": "위치 변경으로 공격 회피",
            "차원 절단": "공간을 가르는 강력한 공격",
            "평행우주": "전투 상황을 리셋할 수 있는 능력",
            "차원의 문": "아군을 안전한 곳으로 이동"
        }
        
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🎉 생성된 파티{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
        
        for i, character in enumerate(party, 1):
            # 직업별 색상
            class_colors = {
                "전사": RED, "성기사": YELLOW, "기사": YELLOW, "검투사": RED, "용기사": MAGENTA,
                "궁수": GREEN, "도적": CYAN, "검성": RED, "해적": BLUE, "사무라이": MAGENTA, "암살자": CYAN,
                "아크메이지": BLUE, "네크로맨서": MAGENTA, "정령술사": CYAN, "시간술사": YELLOW,
                "바드": GREEN, "신관": WHITE, "드루이드": GREEN, "무당": MAGENTA,
                "암흑기사": RED, "몽크": YELLOW, "기계공학자": CYAN, "철학자": BLUE, "연금술사": MAGENTA
            }
            
            class_color = class_colors.get(character.character_class, WHITE)
            
            # 특성 정보 수집 - 선택된 특성만 2개 표시
            traits_info = []
            if hasattr(character, 'selected_traits') and character.selected_traits:
                # selected_traits 사용 (최대 2개)
                for trait in character.selected_traits[:2]:  # 최대 2개만
                    trait_name = trait.name
                    trait_desc = trait_descriptions.get(trait_name, "특수 효과")
                    traits_info.append((trait_name, trait_desc))
            elif hasattr(character, 'active_traits') and character.active_traits:
                # active_traits 사용 (최대 2개)
                for trait in character.active_traits[:2]:  # 최대 2개만
                    trait_name = trait.name
                    trait_desc = trait_descriptions.get(trait_name, "특수 효과")
                    traits_info.append((trait_name, trait_desc))
            elif hasattr(character, 'traits') and character.traits:
                # 기본 traits 사용 (최대 2개)
                for trait in character.traits[:2]:  # 최대 2개만
                    trait_name = trait.name if hasattr(trait, 'name') else str(trait)
                    trait_desc = trait_descriptions.get(trait_name, "특수 효과")
                    traits_info.append((trait_name, trait_desc))
            
            print(f"{GREEN}{i}.{RESET} {WHITE}{character.name}{RESET} ({class_color}{character.character_class}{RESET})")
            if traits_info:
                print(f"   {CYAN}특성: {', '.join([trait[0] for trait in traits_info])}{RESET}")
                for trait_name, trait_desc in traits_info:
                    print(f"   {YELLOW}└─ {trait_name}: {WHITE}{trait_desc}{RESET}")
            print(f"   HP: {RED}{character.max_hp}{RESET} | 물공: {YELLOW}{character.physical_attack}{RESET} | 마공: {BLUE}{character.magic_attack}{RESET}")
            print(f"   물방: {GREEN}{character.physical_defense}{RESET} | 마방: {CYAN}{character.magic_defense}{RESET} | 속도: {MAGENTA}{character.speed}{RESET}")
            print()
    
    def _confirm_party_cursor(self, party: List[Character]) -> Optional[bool]:
        """파티 확인 - 커서 방식 (True: 확인, False: 재생성, None: 취소)"""
        if CURSOR_MENU_AVAILABLE:
            try:
                while True:
                    # 커서 메뉴 옵션
                    options = [
                        "✅ 확인하고 시작",
                        "📋 파티 정보 다시 보기", 
                        "📝 특성 상세 설명 보기",
                        "🔄 파티 다시 생성",
                        "❓ 도움말"
                    ]
                    descriptions = [
                        "현재 파티로 게임을 시작합니다",
                        "선택한 파티의 전체 정보를 다시 확인합니다",
                        "각 캐릭터의 특성에 대한 상세한 설명을 봅니다",
                        "새로운 파티를 다시 생성합니다",
                        "파티 생성에 대한 도움말을 봅니다"
                    ]
                    
                    # CursorMenu 생성
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                    # 파티 정보 표시
                    self._show_created_party(party)
                    
                    print(f"\n{YELLOW}{'='*60}{RESET}")
                    print(f"{YELLOW}이 파티로 게임을 시작하시겠습니까?{RESET}")
                    print(f"{YELLOW}{'='*60}{RESET}")
                    print(f"{CYAN}파티 정보를 확인한 후 아무 키나 누르세요...{RESET}")
                    
                    # 사용자 입력 대기
                    input()
                    
                    menu = CursorMenu("🎯 파티 확인", options, descriptions, cancellable=True)
                    choice = menu.run()
                    
                    if choice is None or choice == -1:  # 취소
                        return None
                    elif choice == 0:  # 확인하고 시작
                        return True
                    elif choice == 1:  # 파티 정보 다시 보기
                        os.system('cls' if os.name == 'nt' else 'clear')
                        self._show_created_party(party)
                        input(f"\n{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
                    elif choice == 2:  # 특성 상세 설명 보기
                        os.system('cls' if os.name == 'nt' else 'clear')
                        self._show_trait_details()
                        input(f"\n{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
                    elif choice == 3:  # 파티 다시 생성
                        return False
                    elif choice == 4:  # 도움말
                        os.system('cls' if os.name == 'nt' else 'clear')
                        self._show_help()
                        input(f"\n{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
                        
            except Exception:
                # 폴백: 기존 방식
                return self._confirm_party()
        else:
            # 폴백: 기존 방식
            return self._confirm_party()

    def _confirm_party(self) -> bool:
        """파티 확인 - 특성 설명 메뉴 추가"""
        while True:
            # 파티 정보 다시 표시
            if hasattr(self, 'last_generated_party') and self.last_generated_party:
                self._show_created_party(self.last_generated_party)
            
            print(f"\n{YELLOW}{'='*60}{RESET}")
            print(f"{YELLOW}이 파티로 게임을 시작하시겠습니까?{RESET}")
            
            # 커서 메뉴 사용
            options = [
                "✅ 확인하고 시작",
                "📋 파티 정보 다시 보기",
                "📝 특성 상세 설명 보기", 
                "🔄 파티 다시 생성",
                "❓ 도움말"
            ]
            descriptions = [
                "현재 파티로 게임을 시작합니다",
                "선택한 파티의 전체 정보를 다시 확인합니다",
                "각 캐릭터의 특성에 대한 상세한 설명을 봅니다",
                "새로운 파티를 다시 생성합니다",
                "파티 생성에 대한 도움말을 봅니다"
            ]
            
            menu = CursorMenu("🎯 파티 확인", options, descriptions, cancellable=False)
            choice = menu.run()
            
            if choice == 0:  # 확인하고 시작
                return True
            elif choice == 1:  # 파티 정보 다시 보기
                continue  # 루프 시작으로 돌아가서 파티 정보 다시 표시
            elif choice == 2:  # 특성 상세 설명 보기
                self._show_trait_details()
            elif choice == 3:  # 파티 다시 생성
                return False
            elif choice == 4:  # 도움말
                self._show_help()
            else:
                print(f"{RED}잘못된 입력입니다. Y/T/N/H 중 하나를 선택해주세요.{RESET}")
    
    def _show_trait_details(self):
        """특성 상세 설명 표시"""
        if not hasattr(self, 'last_generated_party') or not self.last_generated_party:
            print(f"{RED}생성된 파티가 없습니다.{RESET}")
            return
            
        print(f"\n{CYAN}{'='*80}{RESET}")
        print(f"{WHITE}{BOLD}🌟 파티 특성 상세 설명{RESET}")
        print(f"{CYAN}{'='*80}{RESET}")
        
        # 특성 설명 딕셔너리 (여기서 가져옴)
        trait_descriptions = self._get_trait_descriptions()
        
        for i, character in enumerate(self.last_generated_party, 1):
            print(f"\n{GREEN}{i}. {character.name} ({character.character_class}){RESET}")
            print(f"{CYAN}{'─'*60}{RESET}")
            
            # 특성 정보 수집 - 선택된 특성만 2개 표시
            traits_info = []
            if hasattr(character, 'selected_traits') and character.selected_traits:
                for trait in character.selected_traits[:2]:  # 최대 2개만
                    trait_name = trait.name
                    trait_desc = trait_descriptions.get(trait_name, "특수 효과")
                    traits_info.append((trait_name, trait_desc))
            elif hasattr(character, 'active_traits') and character.active_traits:
                for trait in character.active_traits[:2]:  # 최대 2개만
                    trait_name = trait.name
                    trait_desc = trait_descriptions.get(trait_name, "특수 효과")
                    traits_info.append((trait_name, trait_desc))
            elif hasattr(character, 'traits') and character.traits:
                for trait in character.traits[:2]:  # 최대 2개만
                    trait_name = trait.name if hasattr(trait, 'name') else str(trait)
                    trait_desc = trait_descriptions.get(trait_name, "특수 효과")
                    traits_info.append((trait_name, trait_desc))
            
            if traits_info:
                for j, (trait_name, trait_desc) in enumerate(traits_info, 1):
                    effect_type = "액티브" if any(word in trait_desc for word in ["활성화", "사용", "스킬"]) else "패시브"
                    print(f"   {YELLOW}{j}. {trait_name}{RESET} [{MAGENTA}{effect_type}{RESET}]")
                    print(f"      {WHITE}{trait_desc}{RESET}")
                    print()
            else:
                print(f"   {RED}특성 정보가 없습니다.{RESET}")
                
        print(f"{CYAN}{'='*80}{RESET}")
        input(f"{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
    
    def _show_help(self):
        """도움말 표시"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🎮 Easy Character Creator 도움말{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        print(f"\n{GREEN}기본 조작:{RESET}")
        print(f"  {YELLOW}Y{RESET}: 현재 파티로 게임 시작")
        print(f"  {YELLOW}T{RESET}: 특성 상세 설명 보기")
        print(f"  {YELLOW}N{RESET}: 새로운 파티 다시 생성")
        print(f"  {YELLOW}H{RESET}: 이 도움말 표시")
        
        print(f"\n{GREEN}특성 시스템:{RESET}")
        print(f"  • {CYAN}패시브 특성{RESET}: 전투 중 자동으로 적용")
        print(f"  • {MAGENTA}액티브 특성{RESET}: 수동으로 활성화 가능")
        print(f"  • 각 캐릭터마다 클래스별 고유 특성 보유")
        
        print(f"\n{GREEN}전투 시스템:{RESET}")
        print(f"  • ATB 게이지가 가득 찰 때 행동 가능")
        print(f"  • HP 공격과 BRV 공격으로 구분")
        print(f"  • 상처 시스템으로 최대 HP 제한")
        
        print(f"{CYAN}{'='*60}{RESET}")
        input(f"{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
        
    def _get_trait_descriptions(self):
        """특성 설명 딕셔너리 반환 - 실제 존재하는 특성들"""
        return {
            # 전사 특성
            "불굴의 의지": "HP가 25% 이하일 때 공격력 50% 증가 (패시브)",
            "전투 광기": "적을 처치할 때마다 다음 공격의 피해량 20% 증가 (트리거)",
            "방어 숙련": "방어 시 받는 피해 30% 추가 감소 (패시브)",
            "위협적 존재": "전투 시작 시 적들의 공격력 10% 감소 (패시브)",
            "피의 갈증": "HP가 50% 이상일 때 공격속도 25% 증가 (패시브)",
            
            # 아크메이지 특성  
            "마나 순환": "스킬 사용 시 30% 확률로 MP 소모량 절반 (패시브)",
            "원소 지배": "속성 마법 사용 시 해당 속성 저항 20% 증가 (패시브)",
            "마법 연구자": "전투 후 획득 경험치 15% 증가 (패시브)",
            "마법 폭주": "크리티컬 마법 시 주변 적들에게 연쇄 피해 (트리거)",
            "마력 집중": "MP가 75% 이상일 때 마법 피해 40% 증가 (패시브)",
            
            # 궁수 특성
            "정밀 사격": "크리티컬 확률 25% 증가 (패시브)",
            "원거리 숙련": "첫 공격 시 항상 크리티컬 (트리거)", 
            "민첩한 몸놀림": "회피 확률 20% 증가 (패시브)",
            "사냥꾼의 직감": "적의 약점을 간파해 방어력 무시 확률 15% (패시브)",
            "바람의 가호": "이동 시 다음 공격의 명중률과 피해량 15% 증가 (패시브)",
            
            # 도적 특성
            "그림자 은신": "전투 시작 시 3턴간 은신 상태 (액티브)",
            "치명적 급소": "크리티컬 시 추가 출혈 효과 부여 (트리거)",
            "빠른 손놀림": "아이템 사용 시 턴 소모하지 않음 (패시브)",
            "도적의 직감": "함정과 보물 발견 확률 50% 증가 (패시브)",
            "독 숙련": "모든 공격에 10% 확률로 독 효과 추가 (패시브)",
            
            # 성기사 특성
            "신성한 가호": "언데드와 악마에게 받는 피해 50% 감소 (패시브)",
            "치유의 빛": "공격 시 30% 확률로 파티원 전체 소량 회복 (트리거)",
            "정의의 분노": "아군이 쓰러질 때 공격력과 마법력 30% 증가 (트리거)",
            "축복받은 무기": "모든 공격에 성속성 추가 피해 (패시브)",
            "수호의 맹세": "파티원 보호 시 받는 피해 50% 감소 (패시브)",
            
            # 암흑기사 특성
            "생명 흡수": "가한 피해의 15%만큼 HP 회복 (패시브)",
            "어둠의 계약": "HP가 낮을수록 공격력 증가 (최대 100%) (패시브)",
            "공포 오라": "적들이 간헐적으로 행동 불가 (패시브)",
            "불사의 의지": "치명상 시 1회 한정 완전 회복 (트리거)",
            "어둠 조작": "턴 종료 시 20% 확률로 적에게 암속성 피해 (패시브)",
            
            # 몽크 특성
            "내공 순환": "MP가 가득 찰 때마다 모든 능력치 일시 증가 (트리거)",
            "연타 숙련": "연속 공격 시마다 피해량 누적 증가 (패시브)",
            "정신 수양": "상태이상 저항 50% 증가 (패시브)",
            "기절 공격": "일정 확률로 적을 기절시켜 1턴 행동 불가 (트리거)",
            "참선의 깨달음": "전투 중 매 5턴마다 MP 완전 회복 (패시브)",
            
            # 바드 특성
            "전투 노래": "파티원들의 공격력 15% 증가 (패시브)",
            "치유의 선율": "턴 종료 시 파티 전체 소량 회복 (패시브)",
            "용기의 찬송": "파티원들의 크리티컬 확률 10% 증가 (패시브)",
            "마법 해제": "적의 버프를 무효화하는 확률 25% (트리거)",
            "영감의 리듬": "스킬 사용 시 아군의 MP 회복 (트리거)",
            
            # 네크로맨서 특성
            "어둠의 계약": "적 처치 시 MP 회복량 2배 (트리거)",
            "생명력 흡수": "적에게 피해를 줄 때 HP와 MP 동시 회복 (패시브)",
            "저주술": "공격 시 25% 확률로 적에게 저주 부여 (트리거)",
            "죽음의 오라": "주변 적들의 회복 효과 50% 감소 (패시브)",
            "영혼 흡수": "적 처치 시 최대 MP 일시 증가 (트리거)",
            
            # 용기사 특성
            "용의 숨결": "모든 공격에 화염 속성 추가 (패시브)",
            "비늘 방어": "받는 물리 피해 15% 감소 (패시브)",
            "용의 분노": "HP가 낮을수록 공격속도 증가 (패시브)",
            "날개 돌격": "크리티컬 시 추가 행동 기회 (트리거)",
            "용족의 긍지": "디버프 저항 40% 증가 (패시브)",
            
            # 검성 특성
            "검술 달인": "무기 공격력 30% 증가 (패시브)",
            "연속 베기": "공격 성공 시 30% 확률로 즉시 재공격 (트리거)",
            "검기 충격": "공격 시 25% 확률로 2배 피해 (트리거)",
            "완벽한 방어": "방어 시 100% 피해 무효화 (트리거)",
            "검의 의지": "무기 파괴 무효 (패시브)",
            
            # 정령술사 특성
            "정령 친화": "모든 속성 마법 위력 25% 증가 (패시브)",
            "자연의 축복": "턴 시작 시 MP 자동 회복 (패시브)",
            "원소 조화": "서로 다른 속성 연계 시 추가 피해 (트리거)",
            "마나 순환": "마법 사용 시 50% 확률로 MP 소모량 절반 (패시브)",
            "원소 폭발": "마법 크리티컬 시 광역 피해 (트리거)",
            
            # 암살자 특성
            "그림자 이동": "첫 턴에 반드시 선공 (패시브)",
            "치명타 특화": "크리티컬 확률 40% 증가 (패시브)",
            "독날 무기": "모든 공격에 독 효과 (패시브)",
            "은신 공격": "은신 상태에서 공격 시 피해 200% 증가 (트리거)",
            "연막탄": "전투 도중 은신 상태 진입 가능 (액티브)",
            
            # 기계공학자 특성
            "자동 포탑": "전투 시작 시 포탑 설치 (물리공격력 비례 피해) (액티브)",
            "기계 정비": "전투 후 5턴간 장비 효과 10% 증가 (중첩 가능) (트리거)",
            "폭탄 제작": "소모품 폭탄 무한 사용 (패시브)",
            "강화 장비": "모든 장비 효과 20% 증가 (패시브)",
            "오버클럭": "일시적으로 모든 능력치 50% 증가 (액티브)",
            
            # 무당 특성
            "시야 확장": "필드 시야 범위 +1 (패시브)",
            "정령 가호": "상태이상 저항 40% 증가 (패시브)",
            "악령 퇴치": "언데드에게 추가 피해 50% (패시브)",
            "무당의 직감": "크리티컬 받을 확률 30% 감소 (패시브)",
            "영적 보호": "즉사 공격 무효 (패시브)",
            
            # 해적 특성
            "보물 사냥꾼": "골드 획득량 30% 증가 (패시브)",
            "이도류 전투": "공격 시 30% 확률로 2회 공격 (트리거)",
            "바다의 분노": "연속 공격 시 피해량 누적 증가 (패시브)",
            "럭키 스트라이크": "크리티컬 시 20% 확률로 골드 추가 획득 (트리거)",
            "해적의 경험": "전투 후 경험치 15% 추가 획득 (패시브)",
            
            # 사무라이 특성
            "일격필살": "HP 25% 이하일 때 크리티컬 확률 50% 증가 (패시브)",
            "카타나 숙련": "검류 무기 공격력 40% 증가 (패시브)",
            "참선": "전투 외 MP 회복 속도 2배 (패시브)",
            "무사도": "HP 10% 이하일 때 모든 공격 크리티컬 (트리거)",
            "명예의 맹세": "디버프 무효, 모든 능력치 15% 증가 (패시브)",
            
            # 드루이드 특성
            "자연의 가호": "턴 시작 시 HP/MP 소량 회복 (패시브)",
            "자연 치유": "야외에서 지속적인 HP 회복 (패시브)",
            "식물 조종": "적의 이동 제한 및 마법공격력 비례 피해 (액티브)",
            "동물 변신": "늑대형태: 공속+30%, 곰형태: 방어+30%, 독수리형태: 회피+25% (액티브)",
            "계절의 힘": "전투마다 랜덤 속성 강화 (패시브)",
            
            # 철학자 특성
            "현자의 지혜": "모든 스킬 MP 소모량 20% 감소 (패시브)",
            "논리적 사고": "적의 패턴 분석으로 회피율 증가 (패시브)",
            "깨달음": "경험치 획득량 25% 증가 (패시브)",
            "사색의 힘": "MP가 가득 찰 때마다 지혜 스택 증가 (트리거)",
            "철학적 논증": "적을 혼란에 빠뜨리는 스킬 (액티브)",
            
            # 시간술사 특성
            "시간 정지": "적의 행동을 1턴 지연 (액티브)",
            "과거 회귀": "한 번 받은 피해 되돌리기 (트리거)",
            "시간 인식": "적의 다음 행동 타입 미리 파악 (패시브)",
            "순간 가속": "크리티컬 시 20% 확률로 즉시 재행동 (트리거)",
            "인과 조작": "공격 실패 시 재계산 가능 (트리거)",
            
            # 연금술사 특성
            "포션 제조": "회복 아이템 효과 2배 (패시브)",
            "원소 변환": "적의 속성 저항 무시 (패시브)",
            "폭발물 전문": "폭발 계열 스킬 위력 50% 증가 (패시브)",
            "실험 정신": "디버프 지속시간 25% 증가 (패시브)",
            "마법 물질": "모든 공격에 랜덤 속성 추가 (패시브)",
            
            # 검투사 특성
            "관중의 환호": "적을 많이 처치할수록 능력치 증가 (트리거)",
            "검투 기술": "반격 확률 30% 증가 (패시브)",
            "투기장 경험": "1대1 전투 시 모든 능력치 25% 증가 (트리거)",
            "생존 본능": "HP 30% 이하에서 회피율 50% 증가 (패시브)",
            "전사의 혼": "파티원이 전멸해도 5턴간 홀로 전투 지속 (트리거)",
            
            # 기사 특성
            "명예의 수호": "아군 보호 시 받는 피해 30% 감소 (패시브)",
            "창술 숙련": "창류 무기 공격력 35% 증가 (패시브)",
            "기사도 정신": "디버프 지속시간 50% 감소 (패시브)",
            "용맹한 돌격": "첫 공격이 크리티컬일 시 추가 피해 (트리거)",
            "영광의 맹세": "파티원 수만큼 능력치 증가 (패시브)",
            
            # 마검사 특성
            "마검 일체": "물리와 마법 공격력 동시 적용 (패시브)",
            "마력 충전": "공격할 때마다 MP 회복 (패시브)",
            "검기 폭발": "검 공격에 마법 피해 추가 (패시브)",
            "이중 속성": "두 가지 속성 동시 공격 (패시브)",
            "마검 오의": "궁극기 사용 시 모든 적에게 피해 (트리거)",
            
            # 신관 특성
            "신의 가호": "치명타 무효화 확률 20% (패시브)",
            "성스러운 빛": "언데드에게 2배 피해 (패시브)",
            "치유 특화": "모든 회복 효과 50% 증가 (패시브)",
            "축복의 기도": "파티 전체 버프 효과 (액티브)",
            "신탁": "랜덤하게 강력한 기적 발생 (트리거)",
            
            # 차원술사 특성
            "차원 보관": "무제한 아이템 보관 (패시브)",
            "공간 이동": "위치 변경으로 공격 회피 (트리거)",
            "차원 균열": "마법공격력 비례 차원 피해 (보스 50% 감소) (액티브)",
            "평행우주": "공격 실패 시 재시도 가능 (트리거)",
            "공간 왜곡": "적의 정확도 30% 감소 (패시브)"
        }
    
    def _auto_party_creation_fallback(self) -> List[Character]:
        """자동 파티 생성 폴백 (기존 방식)"""
        print(f"\n{CYAN}🎲 완전 자동 파티 생성{RESET}")
        print("밸런스 잡힌 4명의 파티를 자동으로 생성합니다.")
        
        # 특성 선택 방식 묻기
        print(f"\n{YELLOW}특성 선택 방식:{RESET}")
        print("1. 자동 선택 (빠름)")
        print("2. 수동 선택 (상세)")
        
        trait_choice = self.keyboard.get_key()
        manual_traits = (trait_choice == '2')
        
        if manual_traits:
            print(f"{GREEN}✅ 수동 특성 선택 모드{RESET}")
        else:
            print(f"{GREEN}✅ 자동 특성 선택 모드{RESET}")
        
        print(f"{YELLOW}생성 중...{RESET}")
        
        try:
            if manual_traits:
                # 수동 특성 선택을 위해 특성 없이 파티 생성
                party = self.auto_builder.create_balanced_party(auto_select_traits=False)
            else:
                # 자동 특성 선택 포함해서 파티 생성
                party = self.auto_builder.create_balanced_party(auto_select_traits=True)
        except Exception as e:
            print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
            print(f"{YELLOW}다시 시도하시겠습니까? (Y/N){RESET}")
            retry_choice = self.keyboard.get_key().lower()
            if retry_choice == 'y':
                return self._auto_party_creation_fallback()
            else:
                return None
        
        # 수동 특성 선택이면 각 캐릭터마다 특성 선택
        if manual_traits and party:
            print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
            for i, character in enumerate(party, 1):
                print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                result = self._manual_trait_selection(character)
                if result is None:  # 취소된 경우
                    print(f"{YELLOW}특성 선택이 취소되었습니다.{RESET}")
                    return None
        
        if party:
            self._show_created_party(party)
            # last_generated_party 저장
            self.last_generated_party = party
            if self._confirm_party():
                return party
            else:
                return self._auto_party_creation_fallback()  # 재생성
        return None
    
    def _get_party_info_string(self, party: List[Character]) -> str:
        """파티 정보를 문자열로 생성"""
        from game.color_text import GREEN, WHITE, RESET, BOLD, RED, YELLOW, BLUE, CYAN, MAGENTA
        
        lines = []
        lines.append(f"{GREEN}{'='*60}{RESET}")
        lines.append(f"{WHITE}{BOLD}🎉 생성된 파티{RESET}")
        lines.append(f"{GREEN}{'='*60}{RESET}")
        
        for i, character in enumerate(party, 1):
            # 직업별 색상
            class_colors = {
                "전사": RED, "성기사": YELLOW, "기사": YELLOW, "검투사": RED, "용기사": MAGENTA,
                "궁수": GREEN, "도적": CYAN, "검성": RED, "해적": BLUE, "사무라이": MAGENTA, "암살자": CYAN,
                "아크메이지": BLUE, "네크로맨서": MAGENTA, "정령술사": CYAN, "시간술사": YELLOW,
                "바드": GREEN, "신관": WHITE, "드루이드": GREEN, "무당": MAGENTA,
                "암흑기사": RED, "몽크": YELLOW, "기계공학자": CYAN, "철학자": BLUE, "연금술사": MAGENTA
            }
            
            class_color = class_colors.get(character.character_class, WHITE)
            
            traits_str = ""
            if hasattr(character, 'selected_traits') and character.selected_traits:
                trait_names = [trait.name for trait in character.selected_traits]
                traits_str = f"\n   {CYAN}특성: {', '.join(trait_names)}{RESET}"
            elif hasattr(character, 'active_traits') and character.active_traits:
                # 표준: active_traits 속성 사용
                trait_names = [trait.name for trait in character.active_traits]
                traits_str = f"\n   {CYAN}특성: {', '.join(trait_names)}{RESET}"
            elif hasattr(character, 'traits') and character.traits:
                # 대체: traits 속성 사용
                trait_names = [trait.name for trait in character.traits]
                traits_str = f"\n   {CYAN}특성: {', '.join(trait_names)}{RESET}"
            
            lines.append(f"{GREEN}{i}.{RESET} {WHITE}{character.name}{RESET} ({class_color}{character.character_class}{RESET}){traits_str}")
            lines.append(f"   HP: {RED}{character.max_hp}{RESET} | 물공: {YELLOW}{character.physical_attack}{RESET} | 마공: {BLUE}{character.magic_attack}{RESET}")
            lines.append(f"   물방: {GREEN}{character.physical_defense}{RESET} | 마방: {CYAN}{character.magic_defense}{RESET} | 속도: {MAGENTA}{character.speed}{RESET}")
            
            if i < len(party):  # 마지막이 아닌 경우 빈 줄 추가
                lines.append("")
        
        return "\n".join(lines)


# 전역 인스턴스
easy_creator = EasyCharacterCreator()

def get_easy_character_creator():
    """쉬운 캐릭터 생성기 반환"""
    return easy_creator
