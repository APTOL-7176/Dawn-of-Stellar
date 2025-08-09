"""
개선된 캐릭터 생성 시스템
"""

import os
import json
import datetime
from typing import List, Dict, Optional, Tuple
import random
from .character import Character
from .auto_party_builder import AutoPartyBuilder
from .input_utils import KeyboardInput


class PartyHistoryManager:
    """파티 히스토리 관리 시스템"""
    
    def __init__(self, history_file="party_history.json"):
        self.history_file = history_file
        self.max_history = 50  # 최대 50개 파티 보관
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """히스토리 파일 로드"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"히스토리 로드 실패: {e}")
        return []
    
    def _save_history(self):
        """히스토리 파일 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"히스토리 저장 실패: {e}")
    
    def add_party(self, party_members: List[Character], exploration_data: Dict = None):
        """파티를 히스토리에 추가"""
        try:
            party_data = {
                "id": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
                "created_at": datetime.datetime.now().isoformat(),
                "members": [],
                "exploration": exploration_data or {},
                "total_level": 0,
                "total_power": 0,
                "composition": ""
            }
            
            # 파티원 정보 저장
            total_level = 0
            total_power = 0
            class_names = []
            
            for member in party_members:
                member_data = {
                    "name": member.name,
                    "class": getattr(member, 'character_class', '알 수 없음'),
                    "level": getattr(member, 'level', 1),
                    "hp": getattr(member, 'current_hp', 0),
                    "max_hp": getattr(member, 'max_hp', 0),
                    "power": self._calculate_member_power(member)
                }
                
                party_data["members"].append(member_data)
                total_level += member_data["level"]
                total_power += member_data["power"]
                class_names.append(member_data["class"])
            
            party_data["total_level"] = total_level
            party_data["total_power"] = total_power
            party_data["composition"] = " + ".join(class_names)
            
            # 히스토리에 추가 (최신이 앞으로)
            self.history.insert(0, party_data)
            
            # 최대 개수 제한
            if len(self.history) > self.max_history:
                self.history = self.history[:self.max_history]
            
            self._save_history()
            
        except Exception as e:
            print(f"파티 히스토리 추가 실패: {e}")
    
    def _calculate_member_power(self, member) -> int:
        """멤버 전투력 계산"""
        try:
            # display.py의 calculate_combat_power 사용
            from .display import calculate_combat_power
            return calculate_combat_power(member)
        except:
            # 폴백: 간단한 계산
            return (getattr(member, 'physical_attack', 0) + 
                   getattr(member, 'magic_attack', 0) + 
                   getattr(member, 'physical_defense', 0) + 
                   getattr(member, 'magic_defense', 0))
    
    def get_history(self) -> List[Dict]:
        """전체 히스토리 반환"""
        return self.history.copy()
    
    def delete_party(self, party_id: str) -> bool:
        """특정 파티 삭제"""
        try:
            original_length = len(self.history)
            self.history = [p for p in self.history if p.get("id") != party_id]
            
            if len(self.history) < original_length:
                self._save_history()
                return True
        except Exception as e:
            print(f"파티 삭제 실패: {e}")
        
        return False
    
    def clear_history(self):
        """모든 히스토리 삭제"""
        self.history.clear()
        self._save_history()
    
    def get_party_by_id(self, party_id: str) -> Optional[Dict]:
        """ID로 특정 파티 조회"""
        for party in self.history:
            if party.get("id") == party_id:
                return party.copy()
        return None

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

try:
    from .character_presets import CharacterPresets
    PRESETS_AVAILABLE = True
except ImportError:
    PRESETS_AVAILABLE = False

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
BRIGHT_RED = '\033[91m\033[1m'
BRIGHT_GREEN = '\033[92m\033[1m'
BRIGHT_YELLOW = '\033[93m\033[1m'
BRIGHT_BLUE = '\033[94m\033[1m'
BRIGHT_MAGENTA = '\033[95m\033[1m'
BRIGHT_CYAN = '\033[96m\033[1m'
BRIGHT_WHITE = '\033[97m\033[1m'

class EasyCharacterCreator:
    """쉬운 캐릭터 생성 시스템"""
    
    def __init__(self):
        self.keyboard = KeyboardInput()
        self.auto_builder = AutoPartyBuilder()
        self.last_generated_party = None  # 특성 상세 보기용
        
        # 프리셋 매니저 초기화
        if PRESETS_AVAILABLE:
            self.preset_manager = CharacterPresets()
        else:
            self.preset_manager = None
        
        if PASSIVE_SYSTEM_AVAILABLE:
            self.passive_manager = get_passive_system()
        else:
            self.passive_manager = None
        
        # 파티 히스토리 관리자 초기화
        self.party_history = PartyHistoryManager()
        
        # 추천 직업 조합 (사용자가 쉽게 선택할 수 있도록)
        self.recommended_combos = {
            "균형잡힌 파티": {
                "classes": ["전사", "아크메이지", "성기사", "바드"],
                "icon": "⚖️",
                "description": "탱커, 딜러, 힐러, 서포터의 완벽한 조합",
                "stats": "공격력: ⭐⭐⭐ | 방어력: ⭐⭐⭐⭐ | 마법력: ⭐⭐⭐ | 속도: ⭐⭐⭐",
                "strengths": ["안정적인 전투", "모든 상황 대응", "초보자 친화적"],
                "difficulty": "쉬움"
            },
            "물리 특화 파티": {
                "classes": ["검성", "궁수", "사무라이", "몽크"],
                "icon": "⚔️",
                "description": "압도적인 물리 데미지와 크리티컬 특화",
                "stats": "공격력: ⭐⭐⭐⭐⭐ | 방어력: ⭐⭐⭐ | 마법력: ⭐⭐ | 속도: ⭐⭐⭐⭐",
                "strengths": ["높은 물리 피해", "크리티컬 연계", "빠른 전투 종료"],
                "difficulty": "보통"
            },
            "마법 특화 파티": {
                "classes": ["아크메이지", "네크로맨서", "정령술사", "드루이드"],
                "icon": "🔮",
                "description": "강력한 마법 공격과 다양한 상태효과",
                "stats": "공격력: ⭐⭐⭐ | 방어력: ⭐⭐ | 마법력: ⭐⭐⭐⭐⭐ | 속도: ⭐⭐⭐",
                "strengths": ["광역 마법", "상태이상 특화", "MP 관리 중요"],
                "difficulty": "보통"
            },
            "생존 특화 파티": {
                "classes": ["성기사", "신관", "드루이드", "기사"],
                "icon": "🛡️",
                "description": "최고의 방어력과 회복 능력",
                "stats": "공격력: ⭐⭐ | 방어력: ⭐⭐⭐⭐⭐ | 마법력: ⭐⭐⭐⭐ | 속도: ⭐⭐",
                "strengths": ["극강 생존력", "지속적 회복", "장기전 특화"],
                "difficulty": "쉬움"
            },
            "속도 특화 파티": {
                "classes": ["암살자", "해적", "도적", "바드"],
                "icon": "💨",
                "description": "빠른 행동과 크리티컬 위주의 전투",
                "stats": "공격력: ⭐⭐⭐⭐ | 방어력: ⭐⭐ | 마법력: ⭐⭐⭐ | 속도: ⭐⭐⭐⭐⭐",
                "strengths": ["초고속 행동", "연속 공격", "크리티컬 폭격"],
                "difficulty": "어려움"
            },
            "독특한 조합": {
                "classes": ["무당", "용기사", "기계공학자", "철학자"],
                "icon": "🌟",
                "description": "특별한 스킬과 유니크한 플레이 스타일",
                "stats": "공격력: ⭐⭐⭐ | 방어력: ⭐⭐⭐ | 마법력: ⭐⭐⭐⭐ | 속도: ⭐⭐⭐",
                "strengths": ["독특한 메커니즘", "예측 불가능", "창의적 전술"],
                "difficulty": "매우 어려움"
            }
        }
    
    def show_character_creation_menu(self) -> List[Character]:
        """캐릭터 생성 메뉴 표시 - 커서 방식"""
        if CURSOR_MENU_AVAILABLE:
            try:
                while True:
                    options = [
                        "🚀 자동 파티 생성 (추천)",
                        "🎯 질문 기반 맞춤 파티",
                        "📋 추천 조합 선택",
                        "🛠️ 커스텀 파티 생성",
                        "👤 단일 캐릭터 생성",
                        "💾 단일 캐릭터만 저장",
                        "💾 프리셋 관리",
                        "📚 파티 히스토리 관리",
                        "❓ 도움말",
                        "❌ 나가기"
                    ]
                    
                    descriptions = [
                        "밸런스 잡힌 4인 파티를 자동으로 생성합니다",
                        "질문에 답하여 당신만의 맞춤형 파티를 생성합니다",
                        "미리 준비된 조합 중에서 선택합니다",
                        "직접 캐릭터들을 만들어 파티를 구성합니다",
                        "캐릭터 한 명만 생성합니다",
                        "단일 캐릭터만 생성하고 저장합니다 (게임 시작 안 함)",
                        "저장된 캐릭터와 파티를 불러오거나 관리합니다",
                        "저장된 파티의 역사를 확인하고 관리합니다",
                        "캐릭터 생성에 대한 도움말을 봅니다",
                        "메인 메뉴로 돌아갑니다"
                    ]
                    
                    menu = CursorMenu("🎭 캐릭터 생성", options, descriptions, cancellable=True)
                    result = menu.run()
                    
                    if result is None or result == 9:  # 나가기
                        return None
                    elif result == 0:  # 자동 파티 생성
                        party = self._auto_party_creation()
                        return party
                    elif result == 1:  # 질문 기반 맞춤 파티
                        party = self._question_based_party_creation()
                        return party
                    elif result == 2:  # 추천 조합 선택
                        party = self._recommended_combo_creation()
                        return party
                    elif result == 3:  # 커스텀 파티 생성
                        party = self._custom_party_creation()
                        return party
                    elif result == 4:  # 단일 캐릭터 생성
                        party = self._single_character_creation()
                        return party
                    elif result == 5:  # 단일 캐릭터만 저장
                        result = self._single_character_save_only()
                        if result == "SAVE_ONLY":
                            continue  # 메뉴로 돌아가기
                        elif result:
                            return result
                    elif result == 6:  # 프리셋 관리
                        party = self._preset_management()
                        if party:  # 프리셋에서 파티를 불러온 경우
                            return party
                    elif result == 7:  # 파티 히스토리 관리
                        self._party_history_management()
                    elif result == 8:  # 도움말
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
                    self.last_generated_party = party
                    return self._offer_party_options(party, "자동 생성 파티")
                return None
                
            except Exception:
                # 폴백: 기존 방식
                return self._auto_party_creation_fallback()
        else:
            # 폴백: 기존 방식
            return self._auto_party_creation_fallback()
    
    def _recommended_combo_creation(self) -> List[Character]:
        """추천 조합 선택 - 커서 메뉴 방식"""
        try:
            # 메뉴 옵션 구성 - 완전히 새로운 디자인
            options = []
            descriptions = []
            combo_details = []
            
            for i, (combo_name, combo_data) in enumerate(self.recommended_combos.items()):
                # 아이콘과 함께 옵션 생성
                option_text = f"{combo_data['icon']} {combo_name}"
                if combo_name == "균형잡힌 파티":
                    option_text += f" {YELLOW}(추천){RESET}"
                
                options.append(option_text)
                
                # 상세 설명 생성
                classes_str = " + ".join(combo_data['classes'])
                difficulty_color = {
                    "쉬움": GREEN,
                    "보통": YELLOW, 
                    "어려움": RED,
                    "매우 어려움": BRIGHT_RED
                }.get(combo_data['difficulty'], WHITE)
                
                desc = f"""{combo_data['description']}
{CYAN}구성:{RESET} {classes_str}
{combo_data['stats']}
{GREEN}장점:{RESET} {' | '.join(combo_data['strengths'])}
{difficulty_color}난이도: {combo_data['difficulty']}{RESET}"""
                
                descriptions.append(desc)
                combo_details.append(combo_data['classes'])
            
            # 랜덤 조합 추가
            options.append("🎲 랜덤 추천 조합")
            descriptions.append(f"""모든 추천 조합 중 하나를 랜덤하게 선택합니다
{CYAN}재미있는 도전을 원한다면 선택하세요!{RESET}""")
            combo_details.append(None)  # 랜덤은 나중에 처리
            
            # 추가 정보 텍스트 - 완전히 새로운 디자인
            extra_content = f"""{CYAN}═══════════════════════════════════════════════════════════{RESET}
{BRIGHT_CYAN}🌟 D A W N   O F   S T E L L A R - 파티 조합 가이드 🌟{RESET}
{CYAN}═══════════════════════════════════════════════════════════{RESET}

{BRIGHT_WHITE}💡 각 조합의 특징:{RESET}

{GREEN}⚖️ 균형잡힌 파티{RESET} - 모든 상황에 대응할 수 있는 만능 구성
   {WHITE}• 처음 플레이하는 분들께 강력 추천!{RESET}
   {WHITE}• 안정적인 전투와 학습에 최적화{RESET}

{RED}⚔️ 물리 특화 파티{RESET} - 압도적인 화력으로 적을 제압
   {WHITE}• 높은 데미지와 크리티컬 특화{RESET}
   {WHITE}• 빠른 전투 종료를 원한다면 선택{RESET}

{BLUE}🔮 마법 특화 파티{RESET} - 다양한 마법과 상태효과 활용
   {WHITE}• 광역 공격과 상태이상 특화{RESET}
   {WHITE}• 전략적 사고를 좋아한다면 추천{RESET}

{CYAN}🛡️ 생존 특화 파티{RESET} - 극강의 방어력과 회복력
   {WHITE}• 절대 죽지 않는 철벽 방어{RESET}
   {WHITE}• 안전하게 플레이하고 싶다면 선택{RESET}

{YELLOW}💨 속도 특화 파티{RESET} - 번개같은 속도와 연속 공격
   {WHITE}• 스릴 넘치는 고속 전투{RESET}
   {WHITE}• 숙련된 플레이어에게 추천{RESET}

{MAGENTA}🌟 독특한 조합{RESET} - 특별한 스킬과 창의적 전술
   {WHITE}• 예측 불가능한 유니크 플레이{RESET}
   {WHITE}• 도전적인 플레이를 원한다면 선택{RESET}

{CYAN}═══════════════════════════════════════════════════════════{RESET}"""

            if CURSOR_MENU_AVAILABLE:
                try:
                    from .cursor_menu_system import CursorMenu
                    
                    menu = CursorMenu(
                        title=f"{BRIGHT_CYAN}🎯 추천 파티 조합 선택{RESET}",
                        options=options,
                        descriptions=descriptions,
                        extra_content=extra_content,
                        audio_manager=getattr(self, 'audio_manager', None),
                        keyboard=self.keyboard
                    )
                    
                    choice = menu.run()
                    
                    if choice == -1 or choice is None:  # 취소
                        return self.show_character_creation_menu()
                    
                    # 선택된 조합 처리
                    if choice == len(options) - 1:  # 랜덤 선택
                        random_combo_name = random.choice(list(self.recommended_combos.keys()))
                        selected_combo = self.recommended_combos[random_combo_name]['classes']
                        combo_name = f"랜덤 추천 ({random_combo_name})"
                        print(f"\n{BRIGHT_YELLOW}🎲 랜덤 선택 결과: {random_combo_name}!{RESET}")
                    else:
                        combo_name = list(self.recommended_combos.keys())[choice]
                        selected_combo = combo_details[choice]
                        combo_data = self.recommended_combos[combo_name]
                        print(f"\n{BRIGHT_GREEN}✨ {combo_data['icon']} {combo_name} 선택!{RESET}")
                        print(f"{WHITE}{combo_data['description']}{RESET}")
                    
                    print(f"\n{YELLOW}파티 생성 중...{RESET}")
                    print(f"{CYAN}선택된 조합: {combo_name} ({' + '.join(selected_combo)}){RESET}")
                    
                except ImportError:
                    # 폴백: 기본 메뉴 방식
                    return self._recommended_combo_creation_fallback()
                    
            else:
                return self._recommended_combo_creation_fallback()
            
            # 특성 선택 방식 묻기 (커서 메뉴)
            trait_options = ["🤖 자동 선택 (빠름)", "✋ 수동 선택 (상세)", "🔙 뒤로가기"]
            trait_descriptions = [
                "특성을 자동으로 선택하여 빠르게 게임을 시작합니다",
                "커서를 사용하여 특성을 직접 선택합니다",
                "이전 메뉴로 돌아갑니다"
            ]
            
            if CURSOR_MENU_AVAILABLE:
                try:
                    trait_menu = CursorMenu(
                        title="🎭 특성 선택 방식", 
                        options=trait_options, 
                        descriptions=trait_descriptions, 
                        audio_manager=getattr(self, 'audio_manager', None),
                        keyboard=self.keyboard,
                        cancellable=True
                    )
                    trait_choice_idx = trait_menu.run()
                    if trait_choice_idx is None or trait_choice_idx == 2:  # 취소 또는 뒤로가기
                        return None
                    manual_traits = (trait_choice_idx == 1)  # 0: 자동, 1: 수동
                except Exception:
                    # 폴백: 기본 입력 방식
                    manual_traits = self._ask_trait_selection_method_fallback()
            else:
                manual_traits = self._ask_trait_selection_method_fallback()
            
            # 파티 생성
            party = self._create_party_from_classes(selected_combo, manual_traits)
            
            if party:
                print(f"\n{GREEN}✅ {combo_name} 파티 생성 완료!{RESET}")
                return party
            else:
                print(f"{RED}❌ 파티 생성에 실패했습니다.{RESET}")
                return self._recommended_combo_creation()
                
        except Exception as e:
            print(f"{RED}❌ 메뉴 오류: {e}{RESET}")
            return self._recommended_combo_creation_fallback()
    
    def _recommended_combo_creation_fallback(self) -> List[Character]:
        """추천 조합 선택 - 기본 메뉴 방식 (폴백)"""
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
            manual_traits = self._ask_trait_selection_method_fallback()
            
            # 파티 생성
            party = self._create_party_from_classes(selected_combo, manual_traits)
            
            if party:
                print(f"\n{GREEN}✅ 추천 조합 파티 생성 완료!{RESET}")
                return party
            else:
                print(f"{RED}❌ 파티 생성에 실패했습니다.{RESET}")
                return self._recommended_combo_creation()
                
        except ValueError:
            print(f"{RED}올바른 숫자를 입력해주세요.{RESET}")
            return self._recommended_combo_creation()
        except Exception as e:
            print(f"{RED}오류 발생: {e}{RESET}")
            return self._recommended_combo_creation()
    
    def _ask_trait_selection_method_fallback(self) -> bool:
        """특성 선택 방식 묻기 - 기본 방식"""
        print(f"\n{CYAN}🎭 특성 선택 방식{RESET}")
        print("1. 🤖 자동 선택 (빠름)")
        print("2. ✋ 수동 선택 (상세)")
        
        try:
            choice = int(self.keyboard.get_key())
            return choice == 2  # 2번이면 수동 선택
        except ValueError:
            print(f"{RED}잘못된 입력입니다. 자동 선택으로 진행합니다.{RESET}")
            return False
    
    def _ensure_full_party(self, selected_characters: List[Character], source_party: List[Character] = None) -> List[Character]:
        """4명 파티를 보장하는 헬퍼 함수 - 부족하면 AI가 자동으로 채움"""
        if len(selected_characters) >= 4:
            return selected_characters[:4]  # 4명 초과시 앞의 4명만 반환
        
        # 4명 미만이면 AI가 나머지를 채움
        needed_count = 4 - len(selected_characters)
        
        if source_party:
            # 소스 파티에서 선택되지 않은 캐릭터들 중에서 선택
            remaining_characters = [char for char in source_party if char not in selected_characters]
            if len(remaining_characters) >= needed_count:
                auto_selected = remaining_characters[:needed_count]
                selected_characters.extend(auto_selected)
                
                print(f"\n{CYAN}🤖 AI가 나머지 파티원을 자동으로 선택했습니다!{RESET}")
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                for char in auto_selected:
                    print(f"👤 {CYAN}AI 선택{RESET}: {char.name} ({char.character_class})")
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                return selected_characters
        
        # 소스 파티가 없거나 부족하면 새로운 캐릭터 자동 생성
        if hasattr(self, 'auto_builder'):
            print(f"\n{CYAN}🤖 AI가 나머지 {needed_count}명의 파티원을 자동으로 생성합니다!{RESET}")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            # 기존 직업들을 피해서 다양한 직업으로 생성
            existing_classes = [char.character_class for char in selected_characters]
            available_classes = [cls for cls in self.auto_builder.ALL_CLASSES if cls not in existing_classes]
            
            for i in range(needed_count):
                if available_classes:
                    # 사용 가능한 직업 중에서 선택
                    chosen_class = available_classes.pop(0)
                else:
                    # 모든 직업이 사용되었으면 기본 직업들 중에서 선택
                    chosen_class = ["전사", "아크메이지", "궁수", "성기사"][i % 4]
                
                new_character = self.auto_builder._create_character(chosen_class, i)
                if new_character:
                    selected_characters.append(new_character)
                    print(f"👤 {CYAN}AI 생성{RESET}: {new_character.name} ({new_character.character_class})")
            
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"{YELLOW}💡 이제 완전한 4인 파티가 구성되었습니다!{RESET}")
            input("Enter를 눌러 계속...")
        
        return selected_characters
    
    def _create_party_from_classes(self, selected_combo: List[str], manual_traits: bool) -> List[Character]:
        """직업 리스트로부터 파티 생성 - 항상 4명 파티 보장"""
        if manual_traits:
            print(f"{GREEN}✅ 수동 특성 선택 모드{RESET}")
        else:
            print(f"{GREEN}✅ 자동 특성 선택 모드{RESET}")
        
        # 선택된 직업이 4개 미만이면 자동으로 채움
        if len(selected_combo) < 4:
            print(f"{YELLOW}🤖 선택된 직업이 {len(selected_combo)}개입니다. AI가 나머지 {4-len(selected_combo)}개 직업을 자동으로 선택합니다...{RESET}")
            
            # 기본 균형잡힌 직업들
            default_classes = ["전사", "아크메이지", "궁수", "성기사", "네크로맨서", "도적", "바드", "몽크"]
            
            # 이미 선택된 직업과 중복되지 않는 직업들 찾기
            available_classes = [cls for cls in default_classes if cls not in selected_combo]
            
            # 부족한 만큼 추가
            needed = 4 - len(selected_combo)
            additional_classes = available_classes[:needed]
            
            # 여전히 부족하다면 모든 직업에서 선택
            if len(additional_classes) < needed:
                all_classes = self.auto_builder.ALL_CLASSES if hasattr(self.auto_builder, 'ALL_CLASSES') else default_classes
                remaining_classes = [cls for cls in all_classes if cls not in selected_combo and cls not in additional_classes]
                additional_classes.extend(remaining_classes[:needed - len(additional_classes)])
            
            selected_combo = selected_combo + additional_classes[:needed]
            print(f"{CYAN}AI가 추가한 직업: {', '.join(additional_classes[:needed])}{RESET}")
        
        while True:  # 🔄 재생성 루프
            try:
                if manual_traits:
                    # 수동 특성 선택을 위해 특성 없이 파티 생성
                    party = self.auto_builder.create_balanced_party(selected_combo[:4], auto_select_traits=False)
                else:
                    # 자동 특성 선택 포함해서 파티 생성
                    party = self.auto_builder.create_balanced_party(selected_combo[:4], auto_select_traits=True)
            except Exception as e:
                print(f"{RED}파티 생성 중 오류 발생: {e}{RESET}")
                return None
            
            # 4명 파티 보장
            if party and len(party) < 4:
                print(f"{YELLOW}🤖 생성된 파티가 {len(party)}명입니다. AI가 나머지를 자동으로 채웁니다...{RESET}")
                party = self._ensure_full_party(party, [])
            
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
                elif confirm_result == "SAVE_ONLY":
                    # 특별한 "저장만" 신호를 상위로 전달
                    return "SAVE_ONLY"
                elif confirm_result is False:
                    # 🔄 재생성: 루프를 계속하여 새 파티 생성
                    print(f"{YELLOW}🔄 같은 설정으로 파티를 다시 생성합니다...{RESET}")
                    continue
                else:  # confirm_result is None (취소)
                    return None
            else:
                return None
    
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
                
                # 🔄 파티 생성 루프
                while True:
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
                            continue  # 루프 계속
                        else:
                            return None
                    
                    # 수동 특성 선택이면 각 캐릭터마다 특성 선택
                    if manual_traits and party:
                        print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
                        trait_all_success = True
                        for i, character in enumerate(party, 1):
                            print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                            trait_success = self._manual_trait_selection_cursor(character)
                            if not trait_success:  # 특성 선택이 취소된 경우
                                print(f"{RED}특성 선택이 취소되어 파티 생성을 중단합니다.{RESET}")
                                trait_all_success = False
                                break
                        
                        if not trait_all_success:
                            return None
                    
                    if party:
                        confirm_result = self._confirm_party_cursor(party)
                        if confirm_result is True:
                            return party
                        elif confirm_result is False:
                            # 🔄 재생성: 루프를 계속하여 새 파티 생성
                            print(f"{YELLOW}🔄 같은 설정으로 파티를 다시 생성합니다...{RESET}")
                            continue
                        else:  # confirm_result is None (취소)
                            return None
                    else:
                        continue  # 파티 생성 실패 시 재시도
                    
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
                # 🔄 재생성: 같은 설정으로 파티만 다시 생성
                print(f"{YELLOW}🔄 같은 설정으로 파티를 다시 생성합니다...{RESET}")
                # 특성 설정은 유지하고 파티만 재생성
                try:
                    if manual_traits:
                        party = self.auto_builder.create_balanced_party(selected_classes, auto_select_traits=False)
                        if party:
                            print(f"\n{CYAN}=== 특성 선택 단계 ==={RESET}")
                            for i, character in enumerate(party, 1):
                                print(f"\n{YELLOW}━━━ {i}/4: {character.name} ({character.character_class}) ━━━{RESET}")
                                trait_success = self._manual_trait_selection(character)
                                if not trait_success:
                                    print(f"{RED}특성 선택이 취소되어 파티 생성을 중단합니다.{RESET}")
                                    return None
                    else:
                        party = self.auto_builder.create_balanced_party(selected_classes, auto_select_traits=True)
                    
                    if party:
                        self._show_created_party(party)
                        if self._confirm_party():
                            return party
                except Exception as e:
                    print(f"{RED}재생성 중 오류 발생: {e}{RESET}")
                    return None
                
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
                        continue_options = ["✅ 예, 다음 파티원 추가", "❌ 아니오, 현재 파티로 완료", "🔙 뒤로가기"]
                        continue_descriptions = [
                            "다음 파티원을 계속 생성합니다",
                            f"현재 {len(party)}명의 파티로 게임을 시작합니다",
                            "이전 단계로 돌아갑니다"
                        ]
                        
                        continue_menu = CursorMenu(
                            f"🎭 파티 구성 ({len(party)}/{max_party_size})", 
                            continue_options, 
                            continue_descriptions, 
                            cancellable=True
                        )
                        continue_result = continue_menu.run()
                        
                        if continue_result is None or continue_result == 2:  # 뒤로가기
                            return None
                        elif continue_result == 1:  # 아니오
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
                            "classes": ["전사", "성기사", "기사", "암흑기사", "검투사", "광전사", "용기사"],
                            "color": bright_red,
                            "description": "높은 체력과 방어력으로 파티를 보호합니다"
                        },
                        "⚔️ 물리 딜러": {
                            "classes": ["검성", "사무라이", "암살자", "몽크", "궁수", "도적", "해적"],
                            "color": bright_yellow,
                            "description": "물리 공격으로 적을 제압하는 전투 전문가"
                        },
                        "🔮 마법사": {
                            "classes": ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사", "기계공학자"],
                            "color": bright_blue,
                            "description": "강력한 마법으로 적을 소멸시킵니다"
                        },
                        "✨ 서포터": {
                            "classes": ["바드", "드루이드", "신관", "무당"],
                            "color": bright_cyan,
                            "description": "파티원을 치유하고 강화하는 지원 역할"
                        },
                        "🎯 특수 클래스": {
                            "classes": ["철학자", "마검사"],
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
        """클래스별 간단한 설명 (새로운 스킬 시스템 기반)"""
        descriptions = {
            # 탱커
            "전사": "방어력 기반 적응형 전투의 균형잡힌 탱커",
            "성기사": "빛의 힘과 치유 능력을 가진 신성한 수호자",
            "기사": "기사도 정신으로 파티를 보호하는 명예로운 전사",
            "암흑기사": "어둠의 흡수와 디버프로 적을 압도하는 타락한 기사",
            
            # 물리 딜러
            "검성": "검기와 도심으로 완벽한 검술을 구사하는 검의 대가",
            "사무라이": "빛의 정신력과 거합으로 일격필살을 노리는 무사",
            "암살자": "은신과 즉사술로 적을 조용히 제거하는 그림자 암살자",
            "몽크": "내공과 정신 수련으로 자신을 강화하는 수행자",
            "검투사": "연속 공격과 관중 버프로 화려하게 싸우는 투기사",
            "광전사": "분노 상태로 폭발적 화력을 발휘하는 광기의 전사",
            
            # 원거리 딜러
            "궁수": "조준 포인트와 지원사격으로 팀을 지원하는 전술적 명사수",
            "도적": "맹독과 침묵으로 적을 서서히 말려죽이는 독의 지배자",
            "해적": "물과 번개를 조합한 자유분방한 바다의 전사",
            "기계공학자": "번개 에너지와 기계술로 전투하는 과학자",
            
            # 마법사
            "아크메이지": "화염을 중심으로 모든 원소를 다루는 대마법사",
            "네크로맨서": "어둠과 언데드를 조종하는 죽음의 마법사",
            "정령술사": "대지, 물, 화염 정령과 소통하는 자연의 친구",
            "시간술사": "시간과 공간을 조작하는 신비한 시공간 마법사",
            "연금술사": "독과 폭발로 물질을 변환하는 실험적 학자",
            "차원술사": "공간 조작과 차원 이동을 다루는 차원의 지배자",
            
            # 서포터
            "바드": "빛과 어둠의 음악으로 파티를 지원하는 예술가",
            "드루이드": "대지와 번개로 자연을 치유하는 현명한 현자",
            "신관": "빛의 치유와 언데드 퇴치를 담당하는 성직자",
            "무당": "빛과 어둠, 대지의 영력을 다루는 영적 샤먼",
            
            # 특수/하이브리드
            "용기사": "화염 드래곤의 힘을 계승한 전설적 존재",
            "철학자": "논리와 지혜로 현실을 조작하는 사상가",
            "마검사": "마법과 검술을 완벽히 융합한 마검의 달인"
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
    
    def _should_select_traits(self) -> Optional[bool]:
        """특성을 수동으로 선택할지 묻기 (None: 뒤로가기)"""
        trait_options = ["🤖 자동 선택 - 빠르게 게임 시작 (추천)", "✋ 수동 선택 - 커서로 특성 직접 선택", "🔙 뒤로가기"]
        trait_descriptions = [
            "특성을 자동으로 선택하여 빠르게 게임을 시작합니다",
            "커서를 사용하여 특성을 직접 선택합니다. 특성은 게임 중 자동으로 발동되는 패시브 능력입니다",
            "이전 단계로 돌아갑니다"
        ]
        
        if CURSOR_MENU_AVAILABLE:
            try:
                trait_menu = CursorMenu("🎭 특성 선택 방식을 정하세요", trait_options, trait_descriptions, cancellable=True)
                trait_choice = trait_menu.run()
                if trait_choice is None or trait_choice == 2:  # 뒤로가기
                    return None
                elif trait_choice == 1:  # 수동 선택
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
        """자동 특성 선택 - 2개 선택"""
        # 개발 모드 확인
        try:
            from config import game_config
            is_dev_mode = hasattr(game_config, 'DEVELOPMENT_MODE') and game_config.DEVELOPMENT_MODE
        except:
            is_dev_mode = False
        
        # 해당 직업의 모든 특성 가져오기
        available_traits = self.auto_builder._get_available_traits(character.character_class)
        
        if not available_traits:
            print(f"{YELLOW}선택 가능한 특성이 없습니다.{RESET}")
            return
        
        # 개발 모드이거나 특성이 해금되어 있으면 2개 선택
        if is_dev_mode or len(available_traits) >= 2:
            # 2개 랜덤 선택 (중복 없이)
            selected_trait_names = random.sample(available_traits, min(2, len(available_traits)))
            character.traits = selected_trait_names
            
            print(f"{GREEN}자동 선택된 특성 (2개): {', '.join(selected_trait_names)}{RESET}")
        else:
            # 1개만 선택
            selected_trait_name = random.choice(available_traits)
            character.traits = [selected_trait_name]
            print(f"{GREEN}자동 선택된 특성: {selected_trait_name}{RESET}")
        
        # 레거시 호환성을 위해 selected_traits도 설정
        if hasattr(character, 'selected_traits'):
            character.selected_traits = getattr(character, 'traits', [])
    
    def _create_single_character(self, class_name: str, index: int) -> Character:
        """단일 캐릭터 생성 (이름 설정 포함)"""
        # 기본 캐릭터 생성
        character = self.auto_builder._create_character(class_name, index)
        
        # 이름 설정
        custom_name = self._set_character_name(character, class_name)
        if custom_name:
            character.name = custom_name
            
        return character
    
    def _set_character_name(self, character: Character, class_name: str) -> Optional[str]:
        """캐릭터 이름 설정"""
        if not CURSOR_MENU_AVAILABLE:
            # 폴백: 기본 이름 사용
            return None
            
        try:
            current_name = getattr(character, 'name', f"{class_name} 전사")
            
            options = [
                f"📝 직접 입력 (현재: {current_name})",
                "🎲 랜덤 이름 생성",
                "🇰🇷 한글 이름 선택",
                f"✅ 기본 이름 사용 ({current_name})"
            ]
            
            descriptions = [
                "원하는 이름을 직접 입력합니다",
                "성별과 직업에 맞는 랜덤 이름을 생성합니다",
                "미리 준비된 한글 이름 중에서 선택합니다", 
                "자동 생성된 기본 이름을 사용합니다"
            ]
            
            menu = CursorMenu(f"👤 {class_name} 캐릭터 이름 설정", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None or result == 3:  # 취소 또는 기본 이름
                return None
            elif result == 0:  # 직접 입력
                return self._input_custom_name(current_name)
            elif result == 1:  # 랜덤 이름
                return self._generate_random_name(character, class_name)
            elif result == 2:  # 한글 이름 선택
                return self._select_korean_name(class_name)
                
        except Exception as e:
            print(f"{RED}이름 설정 중 오류: {e}{RESET}")
            return None
        
        return None
    
    def _select_korean_name(self, class_name: str) -> Optional[str]:
        """한글 이름 선택"""
        korean_names = {
            "남성": ["민준", "서준", "도윤", "예준", "시우", "주원", "하준", "지호", "건우", "우진",
                   "승현", "준서", "연우", "진우", "현우", "지안", "선우", "서진", "민성", "태현"],
            "여성": ["서연", "하은", "민서", "지우", "서현", "수빈", "지유", "채원", "지민", "다은",
                   "예은", "소율", "시은", "수아", "윤서", "채은", "예원", "지아", "하린", "가은"]
        }
        
        # 직업별 특별한 이름들 추가
        special_names = {
            "전사": ["강철", "용맹", "철산", "무쇠", "검은별"],
            "마법사": ["별빛", "달빛", "마나", "현자", "지혜"],
            "궁수": ["바람", "화살", "독수리", "매의눈", "바람개비"],
            "도적": ["그림자", "암영", "밤바람", "검은발톱", "달그림자"],
            "성기사": ["빛나", "성광", "은혜", "축복", "거룩"],
            "암흑기사": ["어둠", "그림자", "밤", "어스름", "칠흑"],
            "바드": ["선율", "화음", "노래", "악기", "멜로디"]
        }
        
        # 이름 목록 구성
        options = []
        descriptions = []
        
        # 일반 남성 이름
        for name in korean_names["남성"][:10]:
            options.append(f"👨 {name}")
            descriptions.append("남성 이름")
        
        # 일반 여성 이름  
        for name in korean_names["여성"][:10]:
            options.append(f"👩 {name}")
            descriptions.append("여성 이름")
        
        # 직업별 특별 이름
        if class_name in special_names:
            for name in special_names[class_name]:
                options.append(f"⚔️ {name}")
                descriptions.append(f"{class_name} 특화 이름")
        
        options.append("❌ 취소")
        descriptions.append("이름 선택을 취소합니다")
        
        menu = CursorMenu("🇰🇷 한글 이름 선택", options, descriptions, cancellable=True)
        result = menu.run()
        
        if result is None or result == len(options) - 1:  # 취소
            return None
        
        # 선택된 이름에서 이모지 제거
        selected_name = options[result].split(" ", 1)[1]
        return selected_name
    
    def _input_custom_name(self, current_name: str) -> Optional[str]:
        """사용자 직접 이름 입력 - 한글 지원 개선"""
        import sys
        import os
        
        print(f"\n{CYAN}👤 캐릭터 이름 입력{RESET}")
        print(f"현재 이름: {current_name}")
        print(f"새 이름을 입력하세요 (Enter: 기본 이름 유지):")
        
        try:
            # Windows 콘솔 인코딩 설정
            if os.name == 'nt':
                try:
                    # UTF-8 코드페이지 설정
                    import subprocess
                    subprocess.run(['chcp', '65001'], capture_output=True, shell=True)
                except:
                    pass
            
            # sys.stdin의 인코딩 확인 및 설정
            old_encoding = getattr(sys.stdin, 'encoding', 'utf-8')
            
            # 안전한 입력 받기
            print(f"{YELLOW}> {RESET}", end="", flush=True)
            
            try:
                new_name = input().strip()
            except UnicodeDecodeError:
                # 인코딩 오류 시 재시도
                print(f"\n{YELLOW}한글 입력에 문제가 있습니다. 다시 시도해주세요.{RESET}")
                print(f"{YELLOW}> {RESET}", end="", flush=True)
                new_name = input().strip()
            
            if not new_name:
                return None  # 기본 이름 유지
            
            # 이름 길이 확인 (한글은 2바이트로 계산)
            name_length = len(new_name.encode('utf-8'))
            if name_length > 40:  # 한글 기준 약 13자 정도
                print(f"{RED}❌ 이름이 너무 깁니다 (한글 기준 약 13자 이내){RESET}")
                input("Enter를 눌러 계속...")
                return None
            
            # 기본적인 유효성 검사만 수행
            if len(new_name.strip()) == 0:
                print(f"{RED}❌ 빈 이름은 사용할 수 없습니다{RESET}")
                input("Enter를 눌러 계속...")
                return None
            
            # 특수문자 제한 (일부만)
            forbidden_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
            if any(char in new_name for char in forbidden_chars):
                print(f"{RED}❌ 사용할 수 없는 특수문자가 포함되어 있습니다{RESET}")
                print(f"{YELLOW}💡 파일명에 사용할 수 없는 문자: < > : \" | ? * \\ /{RESET}")
                input("Enter를 눌러 계속...")
                return None
            
            return new_name
            
        except (KeyboardInterrupt, EOFError):
            return None
        except Exception as e:
            print(f"{RED}❌ 이름 입력 중 오류: {e}{RESET}")
            print(f"{YELLOW}💡 영어 이름을 시도해보세요{RESET}")
            input("Enter를 눌러 계속...")
            return None
    
    def _is_valid_name_character(self, char: str) -> bool:
        """이름에 사용 가능한 문자인지 확인"""
        # 한글 완성형 (가-힣)
        if '가' <= char <= '힣':
            return True
        # 영어 대소문자
        if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            return True
        # 숫자
        if '0' <= char <= '9':
            return True
        # 공백
        if char == ' ':
            return True
        # 일부 특수문자 허용
        if char in '-_':
            return True
        return False
        # 숫자
        if '0' <= char <= '9':
            return True
        # 공백
        if char == ' ':
            return True
        return False
    
    def _generate_random_name(self, character: Character, class_name: str) -> str:
        """랜덤 이름 생성"""
        try:
            # AI 게임 모드에서 이름 풀 가져오기
            from .ai_game_mode import CharacterTraits
            
            # 성별 결정 (랜덤 또는 기존 캐릭터 성별)
            import random
            gender = getattr(character, 'gender', random.choice(['male', 'female']))
            
            if gender == 'female':
                name_pool = CharacterTraits.FEMALE_NAMES
            else:
                name_pool = CharacterTraits.MALE_NAMES
            
            # 랜덤 이름 선택 (접미사 없이 깔끔하게)
            base_name = random.choice(name_pool)
            return base_name
                
        except Exception:
            # 폴백: 간단한 랜덤 이름
            import random
            simple_names = [
                "아리아", "루나", "제이든", "카이", "노바", "제라", "리온", "미라",
                "오리온", "셀라", "다크스", "루비", "제이크", "에바", "렉스", "티아"
            ]
            return random.choice(simple_names)
    
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
        """생성된 파티 표시 - 간략한 버전"""
        # 파티 정보 저장 (특성 상세 보기용)
        self.last_generated_party = party
        
        print(f"\n{BRIGHT_YELLOW}🎉 질문 기반 맞춤 파티 완성!{RESET}")
        print(f"{BRIGHT_CYAN}{'='*60}{RESET}")
        
        for i, member in enumerate(party, 1):
            # 직업 색상
            job_color = self._get_job_color(member.character_class)
            
            # 특성 정보 간략하게
            traits_info = ""
            if hasattr(member, 'traits') and member.traits:
                # 특성이 2개 이상이면 첫 번째만 표시
                primary_trait = member.traits[0]
                trait_desc = self._get_trait_description(primary_trait, member.character_class)
                traits_info = f"\n   ✨ {primary_trait}\n      {trait_desc}"
                
                # 2개째 특성이 있으면 추가 표시
                if len(member.traits) > 1:
                    secondary_trait = member.traits[1]
                    secondary_desc = self._get_trait_description(secondary_trait, member.character_class)
                    traits_info += f"\n   ✨ {secondary_trait}\n      {secondary_desc}"
            
            print(f"{i}. {job_color}{member.name} ({member.character_class}){RESET}{traits_info}")
            
        print(f"{BRIGHT_CYAN}{'='*60}{RESET}")
        
        # 파티 전체 밸런스 정보 (간략)
        roles = self._analyze_party_balance(party)
        if roles:
            print(f"{CYAN}파티 구성:{RESET} {' | '.join(roles)}")
        
        print()  # 여백 추가
    
    def _get_job_color(self, job_name: str) -> str:
        """직업별 색상 반환"""
        color_map = {
            '전사': GREEN, '궁수': YELLOW, '성기사': WHITE, '암흑기사': MAGENTA,
            '바드': CYAN, '검성': BLUE, '검투사': RED, '광전사': RED,
            '아크메이지': BLUE, '도적': GREEN, '몽크': YELLOW, '네크로맨서': MAGENTA,
            '용기사': RED, '정령술사': CYAN, '암살자': MAGENTA, '기계공학자': WHITE,
            '무당': YELLOW, '해적': BLUE, '사무라이': RED, '드루이드': GREEN,
            '철학자': WHITE, '시간술사': MAGENTA, '연금술사': YELLOW, '기사': CYAN,
            '신관': WHITE, '마검사': BLUE, '차원술사': MAGENTA
        }
        return color_map.get(job_name, WHITE)
    
    def _get_trait_description(self, trait_name: str, job_name: str) -> str:
        """특성 설명 반환"""
        descriptions = self._get_trait_descriptions()
        return descriptions.get(trait_name, "특수 효과")
    
    def _analyze_party_balance(self, party: List[Character]) -> List[str]:
        """파티 구성 분석"""
        roles = []
        for member in party:
            if member.character_class in ['전사', '성기사', '기사', '검투사', '용기사', '광전사']:
                roles.append(f"🛡️ {member.character_class}")
            elif member.character_class in ['궁수', '도적', '암살자', '검성', '해적', '사무라이', '마검사']:
                roles.append(f"⚔️ {member.character_class}")
            elif member.character_class in ['아크메이지', '네크로맨서', '정령술사', '시간술사', '연금술사', '차원술사']:
                roles.append(f"🔮 {member.character_class}")
            elif member.character_class in ['바드', '신관', '드루이드', '무당', '철학자']:
                roles.append(f"💫 {member.character_class}")
            else:
                roles.append(f"🌟 {member.character_class}")
        return roles
        
        # 특성 설명 딕셔너리 (모든 클래스 5개씩)
        trait_descriptions = {
            # 전사 특성 (적응형 시스템 연계)
            "적응형 무술": "전투 중 자세 변경 시 다음 공격 위력 30% 증가",
            "전장의 지배자": "적응형 자세에서 얻는 보너스 효과 50% 증가",
            "불굴의 의지": "방어형 자세에서 체력 회복량 2배, 다른 자세에서도 턴당 체력 3% 회복",
            "전투 본능": "공격형/광전사 자세에서 크리티컬 확률 20% 증가",
            "균형감각": "균형 자세에서 모든 능력치 15% 증가, 수호자 자세에서 아군 보호 효과",
            
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
            
            # 도적 특성 (리메이크)
            "독술 지배": "모든 공격에 독 효과 부여, 독 피해량 50% 증가",
            "침묵 술": "공격 시 30% 확률로 적의 스킬 봉인 2턴",
            "독 촉진": "독에 걸린 적 공격 시 남은 독 피해의 25%를 즉시 피해",
            "맹독 면역": "모든 독과 상태이상에 완전 면역, 독 공격 받을 때 반사",
            "독왕의 권능": "적이 독으로 죽을 때 주변 적들에게 독 전파",
            
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
            
            # 광전사 특성 (2025년 8월 6일 완전 개편 + 너프)
            "혈투의 광기": "HP 15% 이하에서 공격력 100% 증가, 모든 공격이 HP 공격으로 변환",
            "불굴의 의지": "HP 15% 이하에서 1턴간 무적 상태, 모든 상태이상 면역",
            "광전사의 분노": "받는 피해의 50%를 다음 공격에 추가 피해로 반영",
            "최후의 일격": "HP 10% 이하일 때 다음 공격이 치명타 + 200% 추가 피해",
            "생존 본능": "HP 15% 이하에서 회피율 +50%, 크리티컬 확률 +30%",
            
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
            
            # 차원술사 특성 (2025년 8월 6일 탱커 역할로 완전 전환)
            "차원 도약": "공격받을 때 30% 확률로 완전 회피, 회피 시 반격 데미지",
            "공간 왜곡": "모든 공격에 20% 회피율, 회피 시 적에게 반사 피해",
            "차원의 방패": "아군이 받는 피해를 15% 확률로 대신 받기 (30% 감소)",
            "시공간 조작": "적의 강력한 공격을 50% 확률로 무효화",
            "차원술사의 직감": "위험한 적의 행동을 미리 감지하여 파티에게 경고"
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
                    trait_desc = getattr(trait, 'description', trait_descriptions.get(trait_name, "특수 효과"))
                    traits_info.append((trait_name, trait_desc))
            elif hasattr(character, 'active_traits') and character.active_traits:
                # active_traits 사용 (최대 2개)
                for trait in character.active_traits[:2]:  # 최대 2개만
                    trait_name = trait.name
                    trait_desc = getattr(trait, 'description', trait_descriptions.get(trait_name, "특수 효과"))
                    traits_info.append((trait_name, trait_desc))
            elif hasattr(character, 'traits') and character.traits:
                # 기본 traits 사용 (최대 2개)
                for trait in character.traits[:2]:  # 최대 2개만
                    trait_name = trait.name if hasattr(trait, 'name') else str(trait)
                    trait_desc = getattr(trait, 'description', trait_descriptions.get(trait_name, "특수 효과")) if hasattr(trait, 'description') else "특수 효과"
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
                        "✅ 확인하고 게임 시작",
                        "💾 파티만 저장하고 종료",
                        "✏️ 캐릭터 이름 변경",
                        "📋 파티 정보 다시 보기",
                        "📝 특성 상세 설명 보기",
                        "🔄 파티 다시 생성",
                        "🔙 뒤로가기",
                        "❓ 도움말"
                    ]
                    descriptions = [
                        "현재 파티로 게임을 시작합니다",
                        "파티를 저장하고 메인 메뉴로 돌아갑니다 (게임 시작 안 함)",
                        "파티원들의 이름을 개별적으로 변경합니다",
                        "선택한 파티의 전체 정보를 다시 확인합니다",
                        "각 캐릭터의 특성에 대한 상세한 설명을 봅니다",
                        "새로운 파티를 다시 생성합니다",
                        "이전 단계로 돌아갑니다",
                        "파티 생성에 대한 도움말을 봅니다"
                    ]
                    
                    # CursorMenu 생성
                    self._clear_screen_safely()
                    
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
                    
                    if choice is None or choice == 6:  # 취소 또는 뒤로가기
                        return None
                    elif choice == 0:  # 확인하고 게임 시작
                        return True
                    elif choice == 1:  # 파티만 저장하고 종료
                        return self._save_party_only(party)
                    elif choice == 2:  # 캐릭터 이름 변경
                        self._change_party_names(party)
                    elif choice == 3:  # 파티 정보 다시 보기
                        self._clear_screen_safely()
                        self._show_created_party(party)
                        input(f"\n{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
                    elif choice == 4:  # 특성 상세 설명 보기
                        self._clear_screen_safely()
                        self._show_trait_details()
                        input(f"\n{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
                    elif choice == 5:  # 파티 다시 생성
                        return False
                    elif choice == 7:  # 도움말
                        self._clear_screen_safely()
                        self._show_help()
                        input(f"\n{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
                        
            except Exception:
                # 폴백: 기존 방식
                return self._confirm_party()
        else:
            # 폴백: 기존 방식
            return self._confirm_party()

    def _change_party_names(self, party: List[Character]):
        """파티원들의 이름 변경"""
        if not CURSOR_MENU_AVAILABLE:
            print(f"{RED}커서 메뉴 시스템이 필요합니다.{RESET}")
            return
        
        try:
            while True:
                # 캐릭터 선택 메뉴
                options = []
                descriptions = []
                
                for i, character in enumerate(party):
                    current_name = getattr(character, 'name', f"캐릭터 {i+1}")
                    char_class = getattr(character, 'character_class', '알 수 없음')
                    options.append(f"👤 {current_name} ({char_class})")
                    descriptions.append(f"{char_class} 캐릭터의 이름을 변경합니다")
                
                options.extend([
                    "🎲 모든 캐릭터 랜덤 이름",
                    "✅ 완료"
                ])
                descriptions.extend([
                    "모든 파티원의 이름을 랜덤으로 변경합니다",
                    "이름 변경을 완료하고 돌아갑니다"
                ])
                
                import os
                self._clear_screen_safely()
                
                # 현재 파티 이름 표시
                print(f"\n{CYAN}👤 파티원 이름 변경{RESET}")
                print(f"{'='*50}")
                for i, character in enumerate(party, 1):
                    current_name = getattr(character, 'name', f"캐릭터 {i}")
                    char_class = getattr(character, 'character_class', '알 수 없음')
                    print(f"{i}. {YELLOW}{current_name}{RESET} ({char_class})")
                print(f"{'='*50}\n")
                
                menu = CursorMenu("👤 이름을 변경할 캐릭터 선택", options, descriptions, cancellable=True)
                result = menu.run()
                
                if result is None or result == len(party) + 1:  # 취소 또는 완료
                    break
                elif result == len(party):  # 모든 캐릭터 랜덤 이름
                    self._randomize_all_names(party)
                    print(f"{GREEN}✅ 모든 캐릭터의 이름을 랜덤으로 변경했습니다!{RESET}")
                    input("Enter를 눌러 계속...")
                elif 0 <= result < len(party):  # 개별 캐릭터 선택
                    character = party[result]
                    char_class = getattr(character, 'character_class', '알 수 없음')
                    new_name = self._set_character_name(character, char_class)
                    if new_name:
                        character.name = new_name
                        print(f"{GREEN}✅ {char_class} 캐릭터의 이름을 '{new_name}'으로 변경했습니다!{RESET}")
                        input("Enter를 눌러 계속...")
                        
        except Exception as e:
            print(f"{RED}이름 변경 중 오류: {e}{RESET}")
            
    def _randomize_all_names(self, party: List[Character]):
        """모든 캐릭터의 이름을 랜덤으로 변경"""
        for character in party:
            char_class = getattr(character, 'character_class', '알 수 없음')
            new_name = self._generate_random_name(character, char_class)
            character.name = new_name

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
                    trait_desc = getattr(trait, 'description', trait_descriptions.get(trait_name, "특수 효과"))
                    traits_info.append((trait_name, trait_desc))
            elif hasattr(character, 'active_traits') and character.active_traits:
                for trait in character.active_traits[:2]:  # 최대 2개만
                    trait_name = trait.name
                    trait_desc = getattr(trait, 'description', trait_descriptions.get(trait_name, "특수 효과"))
                    traits_info.append((trait_name, trait_desc))
            elif hasattr(character, 'traits') and character.traits:
                for trait in character.traits[:2]:  # 최대 2개만
                    trait_name = trait.name if hasattr(trait, 'name') else str(trait)
                    trait_desc = getattr(trait, 'description', trait_descriptions.get(trait_name, "특수 효과")) if hasattr(trait, 'description') else "특수 효과"
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
            # 전사 특성 (적응형 시스템 연계)
            "적응형 무술": "전투 중 자세 변경 시 다음 공격 위력 30% 증가 (트리거)",
            "전장의 지배자": "적응형 자세에서 얻는 보너스 효과 50% 증가 (패시브)",
            "불굴의 의지": "방어형 자세에서 체력 회복량 2배, 다른 자세에서도 턴당 체력 3% 회복 (패시브)",
            "전투 본능": "공격형/광전사 자세에서 크리티컬 확률 20% 증가 (패시브)",
            "균형감각": "균형 자세에서 모든 능력치 15% 증가, 수호자 자세에서 아군 보호 효과 (패시브)",
            
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
            
            # 도적 특성 (리메이크)
            "독술 지배": "모든 공격에 독 효과 부여, 독 피해량 50% 증가 (패시브)",
            "침묵 술": "공격 시 30% 확률로 적의 스킬 봉인 2턴 (트리거)",
            "독 촉진": "독에 걸린 적 공격 시 남은 독 피해의 25%를 즉시 피해 (트리거)",
            "맹독 면역": "모든 독과 상태이상에 완전 면역, 독 공격 받을 때 반사 (패시브)",
            "독왕의 권능": "적이 독으로 죽을 때 주변 적들에게 독 전파 (트리거)",
            
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
            "연막술": "공격 시 20% 확률로 회피율 50% 증가 (3턴) (트리거)",
            
            # 기계공학자 특성
            "자동 포탑": "전투 시작 시 50% 확률로 포탑 자동 설치 (물리공격력 비례 피해) (트리거)",
            "기계 정비": "전투 후 5턴간 장비 효과 10% 증가 (중첩 가능) (트리거)",
            "폭탄 제작": "소모품 폭탄 무한 사용 (패시브)",
            "강화 장비": "모든 장비 효과 20% 증가 (패시브)",
            "오버클럭": "HP 50% 이하일 때 모든 능력치 30% 증가 (패시브)",
            
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
    
    def _question_based_party_creation(self) -> List[Character]:
        """질문 기반 맞춤 파티 생성"""
        try:
            party = self.auto_builder.create_question_based_party()
            if party is None:  # 사용자가 취소한 경우
                return None
            
            self.last_generated_party = party
            
            # 파티 확인 및 재생성 옵션
            return self._offer_party_options(party, "질문 기반 맞춤 파티")
            
        except Exception as e:
            print(f"{RED}질문 기반 파티 생성 중 오류 발생: {e}{RESET}")
            print(f"{YELLOW}자동 파티 생성으로 전환합니다...{RESET}")
            return self._auto_party_creation()
    
    def _offer_party_options(self, party: List[Character], party_type: str) -> List[Character]:
        """파티 확인 및 옵션 제공"""
        if not CURSOR_MENU_AVAILABLE:
            return party
        
        while True:
            options = [
                "✅ 이 파티로 시작",
                "🔄 파티 재생성",
                "👀 특성 상세 보기",
                "🔧 직업별 기믹 보기",
                "❌ 취소"
            ]
            
            descriptions = [
                "현재 파티로 게임을 시작합니다",
                "새로운 파티를 다시 생성합니다",
                "각 캐릭터의 특성을 자세히 봅니다",
                "각 직업의 고유 기믹을 확인합니다",
                "캐릭터 생성을 취소합니다"
            ]
            
            menu = CursorMenu(f"🎉 {party_type} 완성!", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None or result == 4:  # 취소
                return None
            elif result == 0:  # 이 파티로 시작
                return party
            elif result == 1:  # 파티 재생성
                if party_type == "질문 기반 맞춤 파티":
                    new_party = self._question_based_party_creation()
                else:
                    new_party = self._auto_party_creation()
                if new_party:
                    party = new_party
                    self.last_generated_party = party
            elif result == 2:  # 특성 상세 보기
                self._show_party_traits_detail(party)
            elif result == 3:  # 직업별 기믹 보기
                self._show_party_mechanics_detail(party)
    
    def _show_party_traits_detail(self, party: List[Character]):
        """파티 특성 상세 보기"""
        if not party:
            return
        
        print(f"\n{CYAN}🔍 파티 특성 상세 정보{RESET}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for i, character in enumerate(party, 1):
            print(f"\n{WHITE}{i}. {character.name} ({character.character_class}){RESET}")
            
            # 활성 특성 표시 (실제 description 사용)
            if hasattr(character, 'active_traits') and character.active_traits:
                for trait in character.active_traits:
                    trait_desc = getattr(trait, 'description', "설명 없음")
                    print(f"   ✨ {GREEN}{trait.name}{RESET}")
                    print(f"      {BLUE}{trait_desc}{RESET}")
            elif hasattr(character, 'selected_traits') and character.selected_traits:
                for trait in character.selected_traits:
                    trait_desc = getattr(trait, 'description', "설명 없음")
                    print(f"   ✨ {GREEN}{trait.name}{RESET}")
                    print(f"      {BLUE}{trait_desc}{RESET}")
            else:
                print(f"   {YELLOW}선택된 특성이 없습니다{RESET}")
        
        print(f"\n{CYAN}아무 키나 누르면 돌아갑니다...{RESET}")
        self.keyboard.get_key()
    
    def _show_party_mechanics_detail(self, party: List[Character]):
        """파티 기믹 상세 보기"""
        if not party:
            return
        
        print(f"\n{CYAN}⚙️ 직업별 고유 기믹 정보{RESET}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for i, character in enumerate(party, 1):
            print(f"\n{WHITE}{i}. {character.name} - {character.character_class}{RESET}")
            self.auto_builder.display_class_mechanics(character.character_class)
        
        print(f"\n{CYAN}아무 키나 누르면 돌아갑니다...{RESET}")
        self.keyboard.get_key()
    
    def _preset_management(self) -> Optional[List[Character]]:
        """프리셋 관리 메뉴"""
        if not PRESETS_AVAILABLE or not self.preset_manager:
            print(f"{RED}프리셋 시스템을 사용할 수 없습니다.{RESET}")
            return None
        
        if CURSOR_MENU_AVAILABLE:
            try:
                while True:
                    options = [
                        "📂 저장된 파티 불러오기",
                        "👤 저장된 파티 불러오기 (개별선택)", 
                        "💾 현재 파티 저장하기",
                        "📋 프리셋 목록 보기",
                        "❌ 돌아가기"
                    ]
                    
                    descriptions = [
                        "저장된 파티 프리셋을 불러와서 게임을 시작합니다",
                        "저장된 파티에서 개별 캐릭터를 선택하여 게임을 시작합니다", 
                        "현재 생성된 파티를 프리셋으로 저장합니다",
                        "모든 저장된 프리셋을 확인합니다",
                        "캐릭터 생성 메뉴로 돌아갑니다"
                    ]
                    
                    menu = CursorMenu("💾 프리셋 관리", options, descriptions, cancellable=True)
                    result = menu.run()
                    
                    if result is None or result == 4:  # 돌아가기
                        return None
                    elif result == 0:  # 파티 불러오기
                        party = self._load_party_preset()
                        if party:
                            return party
                    elif result == 1:  # 캐릭터 불러오기  
                        party = self._load_character_preset()
                        if party:
                            return party  # 4명 파티 리스트를 바로 반환
                    elif result == 2:  # 파티 저장하기
                        self._save_party_preset()
                    elif result == 3:  # 프리셋 목록 보기
                        self._show_preset_list()
            except Exception:
                print(f"{RED}프리셋 관리 중 오류가 발생했습니다.{RESET}")
                return None
        else:
            print(f"{RED}커서 메뉴 시스템이 필요합니다.{RESET}")
            return None
    
    def _load_party_preset(self) -> Optional[List[Character]]:
        """파티 프리셋 불러오기"""
        party_presets = self.preset_manager.list_party_presets()
        
        if not party_presets:
            print(f"{YELLOW}저장된 파티 프리셋이 없습니다.{RESET}")
            input("Enter를 눌러 계속...")
            return None
        
        try:
            options = []
            descriptions = []
            
            for preset in party_presets:
                options.append(f"🎭 {preset['name']} ({preset['composition']})")
                desc = f"{preset['description']}"
                if preset['created_at']:
                    desc += f" (생성: {preset['created_at'][:10]})"
                descriptions.append(desc)
            
            options.append("❌ 취소")
            descriptions.append("파티 불러오기를 취소합니다")
            
            menu = CursorMenu("📂 저장된 파티 선택", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None or result == len(party_presets):  # 취소
                return None
            
            # 선택된 파티 로드
            selected_preset = party_presets[result]
            party = self.preset_manager.load_party_preset(selected_preset['name'])
            
            if party:
                print(f"{GREEN}✅ 파티 '{selected_preset['name']}' 불러오기 완료!{RESET}")
                self._show_created_party(party)
                
                # 확인 메뉴
                confirm_options = ["✅ 이 파티로 시작", "❌ 다른 파티 선택"]
                confirm_descriptions = ["불러온 파티로 게임을 시작합니다", "다른 파티를 선택합니다"]
                confirm_menu = CursorMenu("파티 확인", confirm_options, confirm_descriptions)
                confirm_result = confirm_menu.run()
                
                if confirm_result == 0:
                    return party
                else:
                    return self._load_party_preset()  # 다시 선택
            else:
                print(f"{RED}❌ 파티 불러오기 실패{RESET}")
                input("Enter를 눌러 계속...")
                return None
                
        except Exception as e:
            print(f"{RED}파티 불러오기 중 오류: {e}{RESET}")
            return None
    
    def _load_character_preset(self) -> Optional[List[Character]]:
        """개별 캐릭터 프리셋 불러오기 - 저장된 게임 파일에서 선택"""
        try:
            print(f"\n{CYAN}👤 개별 캐릭터 선택 모드{RESET}")
            print(f"{YELLOW}저장된 게임 파일에서 캐릭터를 개별 선택합니다...{RESET}")
            
            # AutoPartyBuilder의 저장된 캐릭터 선택 기능 사용
            from .auto_party_builder import get_auto_party_builder
            auto_builder = get_auto_party_builder()
            
            party = auto_builder.build_party_from_saved_characters()
            
            if party:
                print(f"{GREEN}✅ 저장된 캐릭터로 파티 구성 완료!{RESET}")
                return party
            else:
                print(f"\n{YELLOW}저장된 캐릭터 선택이 취소되었거나 실패했습니다.{RESET}")
                
                # 대안 제시
                print(f"{CYAN}💡 대안 옵션:{RESET}")
                print(f"1. 📂 저장된 파티 프리셋 사용")
                print(f"2. ❌ 메뉴로 돌아가기")
                
                while True:
                    choice = input(f"{GREEN}선택하세요 (1/2): {RESET}").strip()
                    if choice == "1":
                        return self._load_party_preset_fallback()
                    elif choice == "2":
                        return None
                    else:
                        print(f"{RED}1 또는 2를 입력하세요.{RESET}")
                
        except Exception as e:
            print(f"{RED}저장된 캐릭터 로드 중 오류: {e}{RESET}")
            print(f"상세 오류: {str(e)}")
            print(f"{CYAN}💡 대신 파티 프리셋에서 선택해보세요.{RESET}")
            
            # 폴백: 기존 파티 프리셋 방식
            return self._load_party_preset_fallback()
    
    def _load_party_preset_fallback(self) -> Optional[List[Character]]:
        """파티 프리셋에서 불러오기 (폴백)"""
        party_presets = self.preset_manager.list_party_presets()
        
        if not party_presets:
            print(f"{YELLOW}저장된 파티 프리셋이 없습니다.{RESET}")
            print(f"{CYAN}💡 팁: 먼저 파티를 생성하고 저장한 후 불러올 수 있습니다.{RESET}")
            input("Enter를 눌러 계속...")
            return None
        
        # 파티 프리셋 선택 메뉴
        try:
            options = []
            descriptions = []
            
            for preset in party_presets:
                # 파티 이름과 구성 표시
                party_name = preset.get('name', 'Unknown Party')
                composition = preset.get('composition', 'Unknown')
                created_at = preset.get('created_at', '')
                
                options.append(f"🎭 {party_name} ({composition})")
                desc = f"파티 구성: {composition}"
                if created_at:
                    desc += f" (생성: {created_at[:10]})"
                descriptions.append(desc)
            
            options.append("❌ 취소")
            descriptions.append("파티 불러오기를 취소합니다")
            
            menu = CursorMenu("📂 저장된 파티 선택", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None or result == len(party_presets):  # 취소
                return None
            
            # 선택된 파티 로드
            selected_preset = party_presets[result]
            party = self.preset_manager.load_party_preset(selected_preset['name'])
            
            if party:
                print(f"{GREEN}✅ 파티 '{selected_preset['name']}'을(를) 성공적으로 불러왔습니다!{RESET}")
                return party
            else:
                print(f"{RED}❌ 파티를 불러오는 데 실패했습니다.{RESET}")
                return None
        except Exception as e:
            print(f"{RED}파티 프리셋 로드 중 오류: {e}{RESET}")
            return None

    def _save_party_preset(self):
        """파티 프리셋 저장"""
        if not self.last_generated_party:
            print(f"{YELLOW}저장할 파티가 없습니다. 먼저 파티를 생성해주세요.{RESET}")
            input("Enter를 눌러 계속...")
            return
        
        try:
            print(f"\n{CYAN}💾 파티 프리셋 저장{RESET}")
            print(f"프리셋 이름을 입력하세요:")
            print(f"{YELLOW}> {RESET}", end="")
            
            preset_name = ""
            while True:
                key = self.keyboard.get_key()
                if key == '\r' or key == '\n':  # Enter
                    if preset_name.strip():
                        break
                elif key == '\x08':  # Backspace
                    if preset_name:
                        preset_name = preset_name[:-1]
                        print(f"\r{YELLOW}> {preset_name}{RESET} ", end="")
                elif len(key) == 1 and key.isprintable():
                    preset_name += key
                    print(key, end="", flush=True)
            
            print(f"\n설명을 입력하세요 (선택사항):")
            print(f"{YELLOW}> {RESET}", end="")
            
            description = ""
            while True:
                key = self.keyboard.get_key()
                if key == '\r' or key == '\n':  # Enter
                    break
                elif key == '\x08':  # Backspace
                    if description:
                        description = description[:-1]
                        print(f"\r{YELLOW}> {description}{RESET} ", end="")
                elif len(key) == 1 and key.isprintable():
                    description += key
                    print(key, end="", flush=True)
            
            # 저장 실행
            if self.preset_manager.save_party_preset(self.last_generated_party, preset_name.strip(), description.strip()):
                print(f"\n{GREEN}✅ 파티 프리셋 '{preset_name}' 저장 완료!{RESET}")
            else:
                print(f"\n{RED}❌ 파티 프리셋 저장 실패{RESET}")
            
            input("Enter를 눌러 계속...")
            
        except Exception as e:
            print(f"\n{RED}저장 중 오류: {e}{RESET}")
            input("Enter를 눌러 계속...")
    
    def _show_preset_list(self):
        """프리셋 목록 보기"""
        try:
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{WHITE}📋 저장된 프리셋 목록{RESET}")
            print(f"{CYAN}{'='*60}{RESET}")
            
            # 파티 프리셋 목록
            if self.preset_manager:
                party_presets = self.preset_manager.list_party_presets()
                print(f"\n{YELLOW}🎭 파티 프리셋 ({len(party_presets)}개):{RESET}")
                
                if party_presets:
                    for i, preset in enumerate(party_presets, 1):
                        print(f"{WHITE}{i:2d}.{RESET} {preset['name']}")
                        print(f"     구성: {preset['composition']}")
                        if preset.get('description'):
                            print(f"     설명: {preset['description']}")
                        if preset.get('created_at'):
                            print(f"     생성일: {preset['created_at'][:10]}")
                        print()
                else:
                    print(f"     {CYAN}저장된 파티 프리셋이 없습니다.{RESET}")
                    print(f"     {YELLOW}💡 파티를 생성한 후 '현재 파티 저장하기'를 사용해보세요.{RESET}")
            else:
                print(f"{RED}프리셋 관리자를 사용할 수 없습니다.{RESET}")
            
            # 저장된 게임 파일에서 캐릭터 정보도 표시
            print(f"\n{YELLOW}💾 저장된 게임 파일 분석:{RESET}")
            try:
                import json
                import os
                from glob import glob
                
                # 저장 파일들 찾기
                save_files = glob("saves/*.json") + glob("*.json")
                save_files = [f for f in save_files if f.startswith(("save_", "saves/save_"))]
                
                if save_files:
                    total_characters = 0
                    for save_file in save_files:
                        try:
                            with open(save_file, 'r', encoding='utf-8') as f:
                                save_data = json.load(f)
                            
                            if 'party' in save_data:
                                char_count = len(save_data['party'])
                                total_characters += char_count
                                print(f"     📁 {save_file}: {char_count}명 캐릭터")
                        except Exception:
                            continue
                    
                    print(f"\n     {GREEN}총 {total_characters}명의 캐릭터를 개별 선택에서 사용 가능{RESET}")
                else:
                    print(f"     {CYAN}저장된 게임 파일이 없습니다.{RESET}")
                    print(f"     {YELLOW}💡 게임을 진행하고 저장한 후 사용할 수 있습니다.{RESET}")
                    
            except Exception as e:
                print(f"     {RED}게임 파일 분석 실패: {e}{RESET}")
            
            print(f"\n{CYAN}아무 키나 누르면 돌아갑니다...{RESET}")
            self.keyboard.get_key()
            
        except Exception as e:
            print(f"{RED}목록 표시 중 오류: {e}{RESET}")
            print(f"상세 오류: {str(e)}")
            input("Enter를 눌러 계속...")

    def _save_party_only(self, party: List[Character]) -> Optional[bool]:
        """파티만 저장하고 게임 시작하지 않기"""
        try:
            self._clear_screen_safely()
            
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{CYAN}💾 파티 저장 모드{RESET}")
            print(f"{CYAN}{'='*60}{RESET}")
            
            # 파티 정보 표시
            self._show_created_party(party)
            
            print(f"\n{GREEN}✅ 파티가 성공적으로 저장되었습니다!{RESET}")
            print(f"{YELLOW}이 파티는 언제든지 '개별 캐릭터 불러오기'에서 사용할 수 있습니다.{RESET}")
            print(f"\n{CYAN}메인 메뉴로 돌아갑니다...{RESET}")
            
            input(f"\n{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
            
            # 특별한 반환값으로 "저장만 하고 종료" 신호
            return "SAVE_ONLY"
            
        except Exception as e:
            print(f"{RED}저장 중 오류 발생: {e}{RESET}")
            input(f"\n{YELLOW}계속하려면 Enter를 누르세요...{RESET}")
            return None

    def _clear_screen_safely(self):
        """안전한 화면 지우기 (화면 겹침 문제 완전 해결)"""
        try:
            import os
            import time
            import sys
            
            # 출력 버퍼 강제 플러시
            sys.stdout.flush()
            sys.stderr.flush()
            
            # 화면 지우기 전 짧은 대기
            time.sleep(0.05)
            
            # 강력한 화면 지우기
            if os.name == 'nt':  # Windows
                try:
                    # ANSI 시퀀스로 스크롤백까지 클리어
                    print("\x1b[2J\x1b[3J\x1b[H", end='', flush=True)
                    time.sleep(0.05)
                except:
                    # 폴백: CMD cls
                    os.system('cls')
                    time.sleep(0.05)
            else:  # Unix/Linux/Mac
                print("\x1b[2J\x1b[3J\x1b[H", end='', flush=True)
                time.sleep(0.05)
                
            # 잔여 메시지 완전 제거를 위한 추가 빈 줄
            print('\n' * 5, end='', flush=True)
            print("\x1b[H", end='', flush=True)  # 커서 홈으로
            
            # 최종 출력 버퍼 플러시
            sys.stdout.flush()
            
        except Exception:
            # 화면 지우기 실패 시 대량 빈 줄로 기존 내용 완전 밀어내기
            try:
                print('\n' * 150, flush=True)  # 매우 많은 줄로 기존 내용 덮기
                print("\x1b[H", end='', flush=True)  # 커서 홈으로
            except:
                print('\n' * 150)  # 최소한의 폴백

    def _safe_print_after_clear(self, message):
        """화면 지우기 후 안전한 메시지 출력"""
        try:
            import time
            import sys
            
            # 화면 지우기
            self._clear_screen_safely()
            
            # 메시지 출력 전 추가 대기
            time.sleep(0.05)
            
            # 메시지 출력
            print(message)
            
            # 출력 완료 후 버퍼 플러시
            sys.stdout.flush()
            
        except Exception:
            # 폴백: 단순 출력
            print(message)

    def _single_character_save_only(self) -> Optional[str]:
        """단일 캐릭터만 생성해서 저장 (게임 시작 안 함)"""
        try:
            import time
            
            self._clear_screen_safely()
            
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{CYAN}💾 단일 캐릭터 저장 모드{RESET}")
            print(f"{CYAN}{'='*60}{RESET}")
            print(f"{YELLOW}캐릭터 한 명만 생성하고 저장합니다. 게임은 시작하지 않습니다.{RESET}")
            print()
            
            # 직업 선택
            character_class = self._select_character_class()
            if not character_class:
                return None
            
            # 캐릭터 생성
            character = self._create_single_character(character_class, 1)
            if not character:
                return None
            
            # 특성 선택 방식 묻기
            trait_options = ["🤖 자동 선택 (빠름)", "✋ 수동 선택 (상세)", "🚫 특성 없이 저장", "🔙 뒤로가기"]
            trait_descriptions = [
                "특성을 자동으로 선택합니다",
                "직접 특성을 선택합니다",
                "특성 없이 캐릭터만 저장합니다",
                "이전 메뉴로 돌아갑니다"
            ]
            
            if CURSOR_MENU_AVAILABLE:
                try:
                    trait_menu = CursorMenu(
                        title="🎭 특성 선택 방식", 
                        options=trait_options, 
                        descriptions=trait_descriptions, 
                        cancellable=True
                    )
                    trait_choice = trait_menu.run()
                    if trait_choice is None or trait_choice == 3:  # 취소 또는 뒤로가기
                        return None
                    
                    if trait_choice == 0:  # 자동 선택
                        self._auto_select_traits(character)
                        print(f"{GREEN}✅ 특성이 자동으로 선택되었습니다{RESET}")
                    elif trait_choice == 1:  # 수동 선택
                        character.select_traits("manual")
                    elif trait_choice == 2:  # 특성 없이
                        print(f"{YELLOW}💡 특성 없이 캐릭터를 저장합니다{RESET}")
                        
                except Exception:
                    # 폴백: 자동 특성 선택
                    self._auto_select_traits(character)
            else:
                # 폴백: 자동 특성 선택
                self._auto_select_traits(character)
            
            # 캐릭터 정보 표시
            self._clear_screen_safely()
            print(f"\n{GREEN}✅ 캐릭터 생성 완료!{RESET}")
            self._show_created_party([character])
            
            # 저장 확인
            save_options = ["💾 저장하고 메뉴로", "🔄 다시 생성", "❌ 취소"]
            save_descriptions = [
                "이 캐릭터를 저장하고 메인 메뉴로 돌아갑니다",
                "새로운 캐릭터를 다시 생성합니다",
                "저장하지 않고 메뉴로 돌아갑니다"
            ]
            
            if CURSOR_MENU_AVAILABLE:
                try:
                    save_menu = CursorMenu(
                        title="💾 캐릭터 저장", 
                        options=save_options, 
                        descriptions=save_descriptions, 
                        cancellable=True
                    )
                    save_choice = save_menu.run()
                    
                    if save_choice == 0:  # 저장하고 메뉴로
                        # 프리셋 매니저를 통해 저장 (파티가 아닌 개별 캐릭터로)
                        if PRESETS_AVAILABLE and self.preset_manager:
                            try:
                                # 임시 파티로 만들어서 저장 후 개별 캐릭터로 사용 가능하게
                                temp_party = [character]
                                preset_name = f"{character.name}_{character.character_class}_{int(time.time())}"
                                self.preset_manager.save_party_preset(temp_party, preset_name)
                                print(f"\n{GREEN}💾 캐릭터가 성공적으로 저장되었습니다!{RESET}")
                                print(f"{CYAN}저장명: {preset_name}{RESET}")
                                print(f"{YELLOW}💡 '개별 캐릭터 불러오기'에서 사용할 수 있습니다.{RESET}")
                            except Exception as e:
                                print(f"{RED}저장 중 오류 발생: {e}{RESET}")
                        else:
                            print(f"{YELLOW}💾 캐릭터 정보가 표시되었습니다 (저장 시스템 없음){RESET}")
                        
                        input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
                        return "SAVE_ONLY"
                        
                    elif save_choice == 1:  # 다시 생성
                        return self._single_character_save_only()
                    else:  # 취소
                        return None
                        
                except Exception:
                    # 폴백: 자동 저장
                    print(f"{GREEN}💾 캐릭터가 저장되었습니다{RESET}")
                    input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
                    return "SAVE_ONLY"
            else:
                # 폴백: 자동 저장
                print(f"{GREEN}💾 캐릭터가 저장되었습니다{RESET}")
                input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
                return "SAVE_ONLY"
                
        except Exception as e:
            print(f"{RED}단일 캐릭터 저장 중 오류 발생: {e}{RESET}")
            input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
            return None

    def _party_history_management(self):
        """파티 히스토리 관리 메뉴"""
        if not CURSOR_MENU_AVAILABLE:
            print(f"{RED}커서 메뉴 시스템이 필요합니다.{RESET}")
            input("Enter를 눌러 계속...")
            return
        
        try:
            while True:
                self._clear_screen_safely()
                
                # 히스토리 통계 표시
                history = self.party_history.get_history()
                total_parties = len(history)
                
                print(f"\n{CYAN}📚 파티 히스토리 관리{RESET}")
                print(f"{'='*50}")
                print(f"💾 총 저장된 파티: {YELLOW}{total_parties}개{RESET}")
                
                if total_parties > 0:
                    # 최근 파티 정보
                    latest_party = max(history.values(), key=lambda x: x['created_at'])
                    latest_date = latest_party['created_at']
                    print(f"📅 최근 저장: {YELLOW}{latest_date}{RESET}")
                    
                    # 가장 강한 파티 찾기
                    strongest_party = max(history.values(), key=lambda x: x.get('total_power', 0))
                    strongest_power = strongest_party.get('total_power', 0)
                    strongest_name = strongest_party.get('party_name', '이름 없음')
                    print(f"💪 최강 파티: {YELLOW}{strongest_name}{RESET} (전투력: {strongest_power:,})")
                    
                print(f"{'='*50}\n")
                
                options = [
                    "📋 파티 히스토리 보기",
                    "🔍 파티 상세 분석",
                    "📊 파티 비교 분석", 
                    "🗑️ 파티 삭제",
                    "🧹 전체 히스토리 삭제",
                    "💾 현재 파티 추가 (테스트)",
                    "❌ 돌아가기"
                ]
                
                descriptions = [
                    "저장된 모든 파티의 목록을 확인합니다",
                    "특정 파티의 상세한 분석을 봅니다",
                    "여러 파티를 비교 분석합니다",
                    "선택한 파티를 삭제합니다",
                    "모든 파티 히스토리를 삭제합니다",
                    "테스트용으로 현재 파티를 히스토리에 추가합니다",
                    "캐릭터 생성 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("📚 파티 히스토리 관리", options, descriptions, cancellable=True)
                choice = menu.run()
                
                if choice is None or choice == 6:  # 취소 또는 돌아가기
                    break
                elif choice == 0:  # 파티 히스토리 보기
                    self._show_party_history()
                elif choice == 1:  # 파티 상세 분석
                    self._analyze_party_from_history()
                elif choice == 2:  # 파티 비교 분석
                    self._compare_parties_from_history()
                elif choice == 3:  # 파티 삭제
                    self._delete_party_from_history()
                elif choice == 4:  # 전체 히스토리 삭제
                    self._clear_all_history()
                elif choice == 5:  # 현재 파티 추가 (테스트)
                    self._add_test_party_to_history()
                    
        except Exception as e:
            print(f"{RED}파티 히스토리 관리 중 오류 발생: {e}{RESET}")
            input("Enter를 눌러 계속...")

    def _show_party_history(self):
        """파티 히스토리 목록 표시"""
        history = self.party_history.get_history()
        
        if not history:
            print(f"\n{YELLOW}📭 저장된 파티 히스토리가 없습니다.{RESET}")
            input("Enter를 눌러 계속...")
            return
        
        self._clear_screen_safely()
        print(f"\n{CYAN}📋 파티 히스토리 목록{RESET}")
        print(f"{'='*70}")
        
        # 날짜순으로 정렬
        sorted_parties = sorted(history.items(), key=lambda x: x[1]['created_at'], reverse=True)
        
        for i, (party_id, party_data) in enumerate(sorted_parties, 1):
            party_name = party_data.get('party_name', '이름 없음')
            created_at = party_data.get('created_at', '날짜 불명')
            total_power = party_data.get('total_power', 0)
            exploration_data = party_data.get('exploration_data', {})
            floor_reached = exploration_data.get('max_floor', 0)
            
            print(f"{i:2d}. {YELLOW}{party_name}{RESET}")
            print(f"    📅 생성일: {created_at}")
            print(f"    💪 전투력: {total_power:,}")
            print(f"    🏰 최고층: {floor_reached}층")
            
            # 파티 구성 간단 표시
            members = party_data.get('members', [])
            if members:
                member_classes = [m.get('character_class', '알 수 없음') for m in members]
                print(f"    👥 구성: {', '.join(member_classes)}")
            print()
        
        print(f"{'='*70}")
        input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")

    def _analyze_party_from_history(self):
        """히스토리에서 파티 선택하여 상세 분석"""
        history = self.party_history.get_history()
        
        if not history:
            print(f"\n{YELLOW}📭 분석할 파티 히스토리가 없습니다.{RESET}")
            input("Enter를 눌러 계속...")
            return
        
        # 파티 선택 메뉴
        options = []
        descriptions = []
        party_list = []
        
        sorted_parties = sorted(history.items(), key=lambda x: x[1]['created_at'], reverse=True)
        
        for party_id, party_data in sorted_parties:
            party_name = party_data.get('party_name', '이름 없음')
            total_power = party_data.get('total_power', 0)
            created_at = party_data.get('created_at', '날짜 불명')
            
            options.append(f"📊 {party_name} (전투력: {total_power:,})")
            descriptions.append(f"생성일: {created_at}")
            party_list.append((party_id, party_data))
        
        self._clear_screen_safely()
        menu = CursorMenu("🔍 분석할 파티 선택", options, descriptions, cancellable=True)
        choice = menu.run()
        
        if choice is None or choice >= len(party_list):
            return
        
        party_id, party_data = party_list[choice]
        
        # display.py의 로바트 분석 시스템 사용
        try:
            from game.display import get_display
            display = get_display()
            
            # 파티 데이터를 Character 객체로 복원
            characters = []
            for member_data in party_data.get('members', []):
                # 간단한 Character 객체 생성 (분석용)
                char = type('Character', (), {})()
                for key, value in member_data.items():
                    setattr(char, key, value)
                characters.append(char)
            
            if characters:
                self._clear_screen_safely()
                print(f"\n{CYAN}🤖 로바트의 파티 분석 시스템{RESET}")
                print(f"📊 분석 대상: {YELLOW}{party_data.get('party_name', '이름 없음')}{RESET}")
                print(f"{'='*60}")
                
                # 로바트의 완전체 분석 실행
                display.show_detailed_party_analysis(characters)
                
                print(f"\n{CYAN}📈 히스토리 추가 정보{RESET}")
                print(f"{'='*40}")
                exploration_data = party_data.get('exploration_data', {})
                print(f"📅 생성일: {party_data.get('created_at', '날짜 불명')}")
                print(f"🏰 최고 도달층: {exploration_data.get('max_floor', 0)}층")
                print(f"⚔️ 총 전투 수: {exploration_data.get('total_battles', 0)}회")
                print(f"🏆 승리 수: {exploration_data.get('victories', 0)}회")
                
                if exploration_data.get('total_battles', 0) > 0:
                    win_rate = (exploration_data.get('victories', 0) / exploration_data.get('total_battles', 1)) * 100
                    print(f"📊 승률: {win_rate:.1f}%")
                
            else:
                print(f"{RED}❌ 파티 데이터를 불러올 수 없습니다.{RESET}")
                
        except Exception as e:
            print(f"{RED}❌ 분석 중 오류 발생: {e}{RESET}")
        
        input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")

    def _compare_parties_from_history(self):
        """여러 파티 비교 분석"""
        history = self.party_history.get_history()
        
        if len(history) < 2:
            print(f"\n{YELLOW}📭 비교할 파티가 부족합니다. (최소 2개 필요){RESET}")
            input("Enter를 눌러 계속...")
            return
        
        print(f"\n{CYAN}📊 파티 비교 분석 시스템{RESET}")
        print(f"{'='*50}")
        
        # 전투력 랭킹
        sorted_by_power = sorted(history.items(), key=lambda x: x[1].get('total_power', 0), reverse=True)
        print(f"\n💪 {YELLOW}전투력 랭킹{RESET}")
        for i, (party_id, party_data) in enumerate(sorted_by_power[:5], 1):
            party_name = party_data.get('party_name', '이름 없음')
            total_power = party_data.get('total_power', 0)
            print(f"{i}. {party_name}: {total_power:,}")
        
        # 탐험 성과 랭킹
        sorted_by_floor = sorted(history.items(), 
                                key=lambda x: x[1].get('exploration_data', {}).get('max_floor', 0), 
                                reverse=True)
        print(f"\n🏰 {YELLOW}탐험 성과 랭킹{RESET}")
        for i, (party_id, party_data) in enumerate(sorted_by_floor[:5], 1):
            party_name = party_data.get('party_name', '이름 없음')
            max_floor = party_data.get('exploration_data', {}).get('max_floor', 0)
            print(f"{i}. {party_name}: {max_floor}층")
        
        # 승률 랭킹
        parties_with_battles = [(pid, pdata) for pid, pdata in history.items() 
                               if pdata.get('exploration_data', {}).get('total_battles', 0) > 0]
        
        if parties_with_battles:
            sorted_by_winrate = sorted(parties_with_battles, 
                                      key=lambda x: x[1].get('exploration_data', {}).get('victories', 0) / 
                                                   max(x[1].get('exploration_data', {}).get('total_battles', 1), 1), 
                                      reverse=True)
            print(f"\n🏆 {YELLOW}승률 랭킹{RESET}")
            for i, (party_id, party_data) in enumerate(sorted_by_winrate[:5], 1):
                party_name = party_data.get('party_name', '이름 없음')
                exploration_data = party_data.get('exploration_data', {})
                victories = exploration_data.get('victories', 0)
                total_battles = exploration_data.get('total_battles', 1)
                win_rate = (victories / total_battles) * 100 if total_battles > 0 else 0
                print(f"{i}. {party_name}: {win_rate:.1f}% ({victories}/{total_battles})")
        
        # 직업 조합 분석
        print(f"\n👥 {YELLOW}인기 직업 조합 TOP 3{RESET}")
        class_combinations = {}
        for party_data in history.values():
            members = party_data.get('members', [])
            if len(members) >= 4:
                classes = sorted([m.get('character_class', '알 수 없음') for m in members])
                combo_key = ', '.join(classes)
                class_combinations[combo_key] = class_combinations.get(combo_key, 0) + 1
        
        if class_combinations:
            sorted_combos = sorted(class_combinations.items(), key=lambda x: x[1], reverse=True)
            for i, (combo, count) in enumerate(sorted_combos[:3], 1):
                print(f"{i}. {combo} ({count}회 사용)")
        
        input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")

    def _delete_party_from_history(self):
        """히스토리에서 파티 삭제"""
        history = self.party_history.get_history()
        
        if not history:
            print(f"\n{YELLOW}📭 삭제할 파티 히스토리가 없습니다.{RESET}")
            input("Enter를 눌러 계속...")
            return
        
        # 파티 선택 메뉴
        options = []
        descriptions = []
        party_list = []
        
        sorted_parties = sorted(history.items(), key=lambda x: x[1]['created_at'], reverse=True)
        
        for party_id, party_data in sorted_parties:
            party_name = party_data.get('party_name', '이름 없음')
            total_power = party_data.get('total_power', 0)
            created_at = party_data.get('created_at', '날짜 불명')
            
            options.append(f"🗑️ {party_name}")
            descriptions.append(f"전투력: {total_power:,}, 생성일: {created_at}")
            party_list.append((party_id, party_data))
        
        self._clear_screen_safely()
        menu = CursorMenu("🗑️ 삭제할 파티 선택", options, descriptions, cancellable=True)
        choice = menu.run()
        
        if choice is None or choice >= len(party_list):
            return
        
        party_id, party_data = party_list[choice]
        party_name = party_data.get('party_name', '이름 없음')
        
        # 삭제 확인
        if CURSOR_MENU_AVAILABLE:
            confirm_options = ["❌ 예, 삭제합니다", "✅ 아니오, 취소"]
            confirm_descriptions = [f"'{party_name}' 파티를 영구 삭제합니다", "삭제를 취소하고 돌아갑니다"]
            
            confirm_menu = CursorMenu(f"⚠️ '{party_name}' 파티를 정말 삭제하시겠습니까?", 
                                    confirm_options, confirm_descriptions, cancellable=True)
            confirm_choice = confirm_menu.run()
            
            if confirm_choice == 0:  # 삭제 확인
                self.party_history.delete_party(party_id)
                print(f"\n{GREEN}✅ '{party_name}' 파티가 삭제되었습니다.{RESET}")
            else:
                print(f"\n{YELLOW}❌ 삭제가 취소되었습니다.{RESET}")
        else:
            print(f"\n{YELLOW}❌ 커서 메뉴가 필요합니다.{RESET}")
        
        input("Enter를 눌러 계속...")

    def _clear_all_history(self):
        """전체 히스토리 삭제"""
        history = self.party_history.get_history()
        
        if not history:
            print(f"\n{YELLOW}📭 삭제할 히스토리가 없습니다.{RESET}")
            input("Enter를 눌러 계속...")
            return
        
        total_count = len(history)
        
        # 삭제 확인
        if CURSOR_MENU_AVAILABLE:
            confirm_options = ["❌ 예, 모두 삭제", "✅ 아니오, 취소"]
            confirm_descriptions = [
                f"모든 파티 히스토리 ({total_count}개)를 영구 삭제합니다", 
                "삭제를 취소하고 돌아갑니다"
            ]
            
            self._clear_screen_safely()
            print(f"\n{RED}⚠️ 경고: 전체 히스토리 삭제{RESET}")
            print(f"📊 총 {total_count}개의 파티 히스토리가 영구 삭제됩니다.")
            print(f"{RED}이 작업은 되돌릴 수 없습니다!{RESET}\n")
            
            confirm_menu = CursorMenu(f"⚠️ 정말로 모든 파티 히스토리를 삭제하시겠습니까?", 
                                    confirm_options, confirm_descriptions, cancellable=True)
            confirm_choice = confirm_menu.run()
            
            if confirm_choice == 0:  # 삭제 확인
                self.party_history.clear_history()
                print(f"\n{GREEN}✅ 모든 파티 히스토리가 삭제되었습니다.{RESET}")
            else:
                print(f"\n{YELLOW}❌ 삭제가 취소되었습니다.{RESET}")
        else:
            print(f"\n{YELLOW}❌ 커서 메뉴가 필요합니다.{RESET}")
        
        input("Enter를 눌러 계속...")

    def _add_test_party_to_history(self):
        """테스트용 파티를 히스토리에 추가"""
        try:
            # 샘플 파티 생성
            test_party = self._auto_party_creation()
            
            if test_party and len(test_party) >= 4:
                # 파티 이름 입력
                party_name = input(f"\n{CYAN}파티 이름을 입력하세요 (기본: 테스트 파티): {RESET}").strip()
                if not party_name:
                    party_name = f"테스트 파티 #{len(self.party_history.get_history()) + 1}"
                
                # 히스토리에 추가
                self.party_history.add_party(test_party, party_name)
                
                print(f"\n{GREEN}✅ '{party_name}' 파티가 히스토리에 추가되었습니다!{RESET}")
                
                # 파티 정보 간단 표시
                print(f"\n{CYAN}추가된 파티 정보:{RESET}")
                for i, character in enumerate(test_party, 1):
                    char_name = getattr(character, 'name', f'캐릭터{i}')
                    char_class = getattr(character, 'character_class', '알 수 없음')
                    print(f"{i}. {char_name} ({char_class})")
                
            else:
                print(f"\n{RED}❌ 테스트 파티 생성에 실패했습니다.{RESET}")
                
        except Exception as e:
            print(f"\n{RED}❌ 테스트 파티 추가 중 오류: {e}{RESET}")
        
        input("Enter를 눌러 계속...")


# 전역 인스턴스
easy_creator = EasyCharacterCreator()

def get_easy_character_creator():
    """쉬운 캐릭터 생성기 반환"""
    return easy_creator
