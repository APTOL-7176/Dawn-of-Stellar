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
        """캐릭터 생성 메뉴 표시"""
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
            party = self.auto_builder.create_balanced_party()
        except Exception as e:
            print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
            print(f"{YELLOW}다시 시도하시겠습니까? (Y/N){RESET}")
            retry_choice = self.keyboard.get_key().lower()
            if retry_choice == 'y':
                return self._auto_party_creation()
            else:
                return self.show_character_creation_menu()
        
        # 수동 특성 선택이면 각 캐릭터마다 특성 선택
        if manual_traits and party:
            print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
            for i, character in enumerate(party, 1):
                print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                self._manual_trait_selection(character)
        
        if party:
            self._show_created_party(party)
            if self._confirm_party():
                return party
            else:
                return self._auto_party_creation()  # 재생성
        return None
    
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
            
            try:
                party = self.auto_builder.create_balanced_party(selected_combo)
            except Exception as e:
                print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
                print(f"{YELLOW}다시 시도하시겠습니까? (Y/N){RESET}")
                retry_choice = self.keyboard.get_key().lower()
                if retry_choice == 'y':
                    return self._recommended_combo_creation()
                else:
                    return self.show_character_creation_menu()
            
            # 수동 특성 선택이면 각 캐릭터마다 특성 선택
            if manual_traits and party:
                print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
                for i, character in enumerate(party, 1):
                    print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                    self._manual_trait_selection(character)
            
            if party:
                self._show_created_party(party)
                if self._confirm_party():
                    return party
                else:
                    return self._recommended_combo_creation()
            return None
            
        except ValueError:
            print(f"{RED}숫자를 입력해주세요.{RESET}")
            return self._recommended_combo_creation()
    
    def _custom_party_creation(self) -> List[Character]:
        """커스텀 파티 생성"""
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
                elif key in ['a', 'b', 'l']:
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
            
            
            if choice == 'a':
                # 나머지 자리를 자동으로 채움
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
                continue  # 목록을 다시 표시
            
            # 숫자 입력 처리
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
        
        # 선택 완료 후 파티 생성
        print(f"\n{YELLOW}선택된 파티로 캐릭터 생성 중...{RESET}")
        print(f"{CYAN}최종 선택: {' + '.join(selected_classes)}{RESET}")
        
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
        
        try:
            party = self.auto_builder.create_balanced_party(selected_classes)
        except Exception as e:
            print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
            print(f"{YELLOW}다시 시도하시겠습니까? (Y/N){RESET}")
            retry_choice = self.keyboard.get_key().lower()
            if retry_choice == 'y':
                return self._custom_party_creation()
            else:
                return self.show_character_creation_menu()
        
        # 수동 특성 선택이면 각 캐릭터마다 특성 선택
        if manual_traits and party:
            print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
            for i, character in enumerate(party, 1):
                print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                self._manual_trait_selection(character)
        
        if party:
            self._show_created_party(party)
            if self._confirm_party():
                return party
            else:
                return self._custom_party_creation()
        return None
    
    def _single_character_creation(self) -> List[Character]:
        """개별 캐릭터 생성 (특성 선택 포함)"""
        print(f"\n{CYAN}👤 개별 캐릭터 생성{RESET}")
        print("각 캐릭터마다 직업과 특성을 직접 선택합니다.")
        
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
                
                # 특성 선택
                if self._should_select_traits():
                    self._manual_trait_selection(character)
                else:
                    self._auto_select_traits(character)
                
                party.append(character)
            except Exception as e:
                print(f"{RED}캐릭터 생성 중 오류 발생: {e}{RESET}")
                print(f"{YELLOW}이 캐릭터를 건너뛰고 계속하시겠습니까? (Y/N){RESET}")
                retry_choice = self.keyboard.get_key().lower()
                if retry_choice != 'y':
                    return self.show_character_creation_menu()
                continue
            print(f"{GREEN}✅ {character.name} ({character_class}) 생성 완료{RESET}")
            
            # 계속할지 묻기
            if i < max_party_size - 1:
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
        """직업 선택"""
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
        print(f"\n{YELLOW}특성 선택 방식:{RESET}")
        print("1. 자동 선택 (추천)")
        print("2. 수동 선택 (상세)")
        
        choice = self.keyboard.get_key()
        return choice == '2'
    
    def _manual_trait_selection(self, character: Character):
        """수동 특성 선택"""
        print(f"\n{WHITE}{BOLD}{'='*50}{RESET}")
        print(f"{WHITE}{BOLD}🎯 {character.name} ({character.character_class})의 특성 선택{RESET}")
        print(f"{WHITE}{BOLD}{'='*50}{RESET}")
        
        if not character.available_traits:
            print(f"{YELLOW}❌ 사용 가능한 특성이 없습니다.{RESET}")
            return
        
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
                "암흑기사": RED, "몽크": YELLOW, "기계공학자": CYAN
            }
            
            class_color = class_colors.get(character.character_class, WHITE)
            
            traits_str = ""
            if hasattr(character, 'selected_traits') and character.selected_traits:
                trait_names = [trait.name for trait in character.selected_traits]
                traits_str = f"\n   {CYAN}특성: {', '.join(trait_names)}{RESET}"
            
            print(f"{GREEN}{i}.{RESET} {WHITE}{character.name}{RESET} ({class_color}{character.character_class}{RESET}){traits_str}")
            print(f"   HP: {RED}{character.max_hp}{RESET} | 물공: {YELLOW}{character.physical_attack}{RESET} | 마공: {BLUE}{character.magic_attack}{RESET}")
            print(f"   물방: {GREEN}{character.physical_defense}{RESET} | 마방: {CYAN}{character.magic_defense}{RESET} | 속도: {MAGENTA}{character.speed}{RESET}")
            print()
    
    def _confirm_party(self) -> bool:
        """파티 확인"""
        print(f"{YELLOW}이 파티로 게임을 시작하시겠습니까?{RESET}")
        print(f"{GREEN}Y{RESET}: 확인  {RED}N{RESET}: 다시 생성")
        
        choice = self.keyboard.get_key().lower()
        return choice == 'y' or choice == ''
    
    def _show_help(self):
        """도움말 표시"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}📖 캐릭터 생성 도움말{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        print(f"{GREEN}1. 완전 자동 파티:{RESET}")
        print("   - 가장 빠른 방법")
        print("   - 밸런스 잡힌 4명 자동 생성")
        print("   - 초보자 추천")
        print()
        print(f"{GREEN}2. 추천 조합:{RESET}")
        print("   - 검증된 파티 조합")
        print("   - 특정 전략에 특화")
        print("   - 중급자 추천")
        print()
        print(f"{GREEN}3. 커스텀 파티:{RESET}")
        print("   - 원하는 직업 선택")
        print("   - 부족한 역할 자동 보완")
        print("   - 고급자 추천")
        print()
        print(f"{GREEN}4. 개별 생성:{RESET}")
        print("   - 각 캐릭터 직접 설정")
        print("   - 특성까지 수동 선택")
        print("   - 전문가용")
        print(f"{CYAN}{'='*60}{RESET}")
        self.keyboard.wait_for_key("아무 키나 눌러 계속...")


# 전역 인스턴스
easy_creator = EasyCharacterCreator()

def get_easy_character_creator():
    """쉬운 캐릭터 생성기 반환"""
    return easy_creator
