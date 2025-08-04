#!/usr/bin/env python3
"""
자동 파티 구성 시스템 - 밸런스 잡힌 파티 자동 생성
"""

import random
from typing import List, Dict, Any, Optional
from .character import Character, CharacterClassManager
from .input_utils import KeyboardInput
from config import game_config

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

class AutoPartyBuilder:
    """자동 파티 구성 시스템"""
    
    def __init__(self):
        self.keyboard = KeyboardInput()
        self._used_names = set()
    
    # 전체 직업 정의 (모든 직업 포함)
    ALL_CLASSES = [
        "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크",
        "바드", "네크로맨서", "용기사", "검성", "정령술사", "암살자", "기계공학자",
        "무당", "해적", "사무라이", "드루이드", "철학자", "시간술사", "연금술사",
        "검투사", "기사", "신관", "마검사", "차원술사", "광전사"
    ]
    
    # 역할별 분류
    ROLE_CLASSES = {
        "탱커": ["전사", "성기사", "기사", "검투사", "용기사", "광전사"],
        "딜러": ["궁수", "도적", "암살자", "검성", "해적", "사무라이", "마검사"],
        "마법사": ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사"],
        "서포터": ["바드", "신관", "드루이드", "무당", "철학자"],
        "하이브리드": ["암흑기사", "몽크", "기계공학자"]
    }
    
    # 시너지 조합
    SYNERGY_COMBINATIONS = {
        "성기사 + 신관": {"bonus": "신성 시너지", "effect": "언데드에게 추가 피해"},
        "암흑기사 + 네크로맨서": {"bonus": "어둠 시너지", "effect": "생명력 흡수 증가"},
        "궁수 + 사무라이": {"bonus": "원거리 + 근거리", "effect": "속도 보너스"},
        "바드 + 아크메이지": {"bonus": "마법 증폭", "effect": "마법 피해 증가"},
        "드루이드 + 정령술사": {"bonus": "자연 조화", "effect": "MP 회복 증가"},
        "기계공학자 + 연금술사": {"bonus": "과학 조합", "effect": "아이템 효과 증가"}
    }

    def create_balanced_party(self, user_selected: List[str] = None, party_size: int = 4, auto_select_traits: bool = True) -> List[Character]:
        """밸런스 잡힌 파티 생성"""
        if user_selected is None:
            user_selected = []
        
        # 사용자 선택 저장
        self.last_user_selection = user_selected.copy()
        
        # 이름 중복 방지를 위해 사용된 이름 초기화
        self._used_names = set()
        
        # 사용자 선택 캐릭터 검증
        validated_selected = []
        for class_name in user_selected:
            if class_name in self.ALL_CLASSES:
                validated_selected.append(class_name)
            else:
                print(f"{YELLOW}경고: '{class_name}'는 유효하지 않은 직업입니다.{RESET}")
        
        print(f"\n{CYAN}=== 자동 파티 구성 시작 ==={RESET}")
        if validated_selected:
            print(f"{GREEN}사용자 선택: {', '.join(validated_selected)}{RESET}")
        
        # 파티 구성
        party_classes = self._select_party_classes(validated_selected, party_size)
        party_members = []
        
        for i, class_name in enumerate(party_classes):
            character = self._create_character(class_name, i + 1)
            # 특성 자동 선택 (옵션)
            if auto_select_traits:
                self._auto_select_passives(character)
            party_members.append(character)
        
        # 파티 분석 및 시너지 확인
        self._analyze_party(party_members)
        
        # Easy Character Creator에서 확인을 처리하므로 여기서는 생략
        # self._offer_regeneration_option(party_members)
        
        return party_members
    
    def regenerate_party(self, party_size: int = 4) -> List[Character]:
        """파티 재생성 (마지막 사용자 선택 유지)"""
        print(f"\n{CYAN}🔄 파티 재생성 중...{RESET}")
        return self.create_balanced_party(self.last_user_selection, party_size)
    
    def _offer_regeneration_option(self, current_party: List[Character]):
        """파티 재생성 옵션 제공"""
        print(f"\n{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{WHITE}파티가 마음에 드시나요?{RESET}")
        print(f"{GREEN}✅ Enter: 이 파티로 진행{RESET}")
        print(f"{CYAN}🔄 R: 파티 재생성{RESET}")
        print(f"{RED}❌ Q: 종료{RESET}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        while True:
            try:
                choice = self.keyboard.get_key().lower()
                
                if choice == '' or choice == 'enter' or choice == '\r':
                    print(f"{GREEN}✅ 파티 확정!{RESET}")
                    break
                elif choice == 'r':
                    regenerated_party = self.regenerate_party()
                    return regenerated_party
                elif choice == 'q':
                    print(f"{RED}❌ 파티 생성 취소{RESET}")
                    return None
                else:
                    print(f"{RED}잘못된 입력입니다. Enter, R, 또는 Q를 입력해주세요.{RESET}")
            except KeyboardInterrupt:
                print(f"\n{RED}❌ 파티 생성 취소{RESET}")
                return None
    
    def _select_party_classes(self, user_selected: List[str], party_size: int) -> List[str]:
        """파티 직업 선택 (밸런스 고려)"""
        remaining_slots = party_size - len(user_selected)
        available_classes = [c for c in self.ALL_CLASSES if c not in user_selected]
        
        if remaining_slots <= 0:
            return user_selected[:party_size]
        
        # 현재 파티 역할 분석
        current_roles = self._analyze_roles(user_selected)
        needed_roles = self._determine_needed_roles(current_roles, remaining_slots)
        
        selected_classes = user_selected.copy()
        
        # 필요한 역할에 따라 캐릭터 선택
        for role in needed_roles:
            if remaining_slots <= 0:
                break
                
            role_candidates = [c for c in self.ROLE_CLASSES.get(role, []) if c in available_classes]
            
            if role_candidates:
                # 시너지를 고려한 선택
                best_candidate = self._select_best_candidate(role_candidates, selected_classes)
                selected_classes.append(best_candidate)
                available_classes.remove(best_candidate)
                remaining_slots -= 1
        
        # 남은 슬롯은 랜덤 선택
        while remaining_slots > 0 and available_classes:
            random_choice = random.choice(available_classes)
            selected_classes.append(random_choice)
            available_classes.remove(random_choice)
            remaining_slots -= 1
        
        return selected_classes
    
    def _analyze_roles(self, classes: List[str]) -> Dict[str, int]:
        """현재 파티의 역할 분석"""
        role_count = {"탱커": 0, "딜러": 0, "마법사": 0, "서포터": 0, "하이브리드": 0}
        
        for class_name in classes:
            for role, role_classes in self.ROLE_CLASSES.items():
                if class_name in role_classes:
                    role_count[role] += 1
                    break
        
        return role_count
    
    def _determine_needed_roles(self, current_roles: Dict[str, int], remaining_slots: int) -> List[str]:
        """필요한 역할 결정 (서포터 비중 높임)"""
        needed_roles = []
        
        # 서포터 우선 구성: 서포터를 우선적으로 배치
        if current_roles["서포터"] == 0:
            needed_roles.append("서포터")
        
        # 탱커 추가
        if current_roles["탱커"] == 0:
            needed_roles.append("탱커")
        
        # 딜러 추가 (최소 1명)
        if current_roles["딜러"] == 0:
            needed_roles.append("딜러")
        
        # 마법사 추가 (서포터가 없을 때만)
        if current_roles["마법사"] == 0 and current_roles["서포터"] == 0 and len(needed_roles) < remaining_slots:
            needed_roles.append("마법사")
        
        # 남은 슬롯을 서포터나 딜러로 채우기 (서포터 우선)
        while len(needed_roles) < remaining_slots:
            if current_roles["서포터"] + needed_roles.count("서포터") < 2:
                needed_roles.append("서포터")
            else:
                needed_roles.append("딜러")
        
        return needed_roles[:remaining_slots]
    
    def _select_best_candidate(self, candidates: List[str], current_party: List[str]) -> str:
        """시너지를 고려한 최적 후보 선택"""
        synergy_scores = {}
        
        for candidate in candidates:
            score = 0
            
            # 시너지 확인
            for party_member in current_party:
                synergy_key1 = f"{party_member} + {candidate}"
                synergy_key2 = f"{candidate} + {party_member}"
                
                if synergy_key1 in self.SYNERGY_COMBINATIONS or synergy_key2 in self.SYNERGY_COMBINATIONS:
                    score += 10
            
            # 다양성 보너스 (같은 직업이 없으면 보너스)
            if candidate not in current_party:
                score += 5
            
            synergy_scores[candidate] = score
        
        # 가장 높은 점수의 후보 선택 (동점이면 랜덤)
        max_score = max(synergy_scores.values())
        best_candidates = [c for c, s in synergy_scores.items() if s == max_score]
        
        return random.choice(best_candidates)
    
    def _create_character(self, class_name: str, index: int) -> Character:
        """캐릭터 생성"""
        # 대폭 확장된 캐릭터 이름 풀 (300개 이상)
        character_names = [
            # 남성 이름 (150개)
            "아리우스", "발렌타인", "가브리엘", "라파엘", "카이저", "레오나르드", "세바스찬", "알렉산더",
            "막시무스", "아드리안", "루카스", "니콜라스", "도미닉", "빈센트", "에밀리오", "마르코",
            "클라우디우스", "오거스트", "바실리우스", "이그니스", "펠릭스", "라이언", "에릭",
            "마틴", "엘리아스", "다미안", "율리안", "카를로스", "디에고", "파블로", "프란시스",
            "로드리고", "안토니오", "페드로", "미구엘", "호세", "루이스", "페르난도", "애드워드",
            "라몬", "호르헤", "카를로스", "마누엘", "프랑크", "올리버", "해리", "잭", "윌리엄",
            "제임스", "찰스", "로버트", "마이클", "데이비드", "리처드", "조셉", "토머스", "크리스토퍼",
            "매트", "앤소니", "마크", "도널드", "스티븐", "폴", "앤드류", "조슈아", "케네스", "케빈",
            "브라이언", "조지", "에드워드", "로널드", "티모시", "제이슨", "제프리", "라이언", "제이콥",
            "게리", "니콜라스", "에릭", "조나단", "스티븐", "래리", "저스틴", "스콧", "브랜든", "벤자민",
            "사무엘", "그레고리", "알렉산더", "패트릭", "잭", "데니스", "제리", "타일러", "애런",
            "호세", "헨리", "더글러스", "네이선", "피터", "잭슨", "노아", "이단", "루카스", "메이슨",
            "로건", "제이콥", "윌리엄", "엘리야", "웨인", "칼렙", "라이언", "니콜라스", "조던",
            "로버트", "그레이슨", "헌터", "에이든", "카메론", "코너", "산티아고", "칼렙", "네이선",
            "이사이야", "찰리", "이반", "오웬", "루크", "딜런", "잭슨", "가빈", "데이비드", "콜튼",
            "앤드류", "맥스", "라이언", "브레이든", "토머스", "카터", "다니엘", "마이클", "아담",
            "엘라이", "벤자민", "핀", "코딘", "트리스탄", "로넌", "블레이크", "브로디", "데클란",
            "숀", "리암", "루카", "제임슨", "카일", "브랜든", "알렉스", "자이든", "자비에르",
            "도미닉", "데미트리","에이스", "니키타", "블라디미르", "알렉세이", "이반", "안톤", "올렉",
            "세르겐", "빅터", "로만", "파벨", "녹티스", "아르템", "콘스탄틴", "발렌틴", "드미트리","티더","클라우드","프롬프토","그림니르","시스","랜슬롯",
            
            # 여성 이름 (150개)
            "아리아", "셀레스트","유나", "이사벨라", "발레리아", "세라피나", "아드리아나", "밀리아", "비비안", "클라라","비라","유엘",
            "에밀리아", "루시아", "소피아", "올리비아", "나탈리아", "카밀라", "레오니", "미리암",
            "로사", "에스텔라", "바이올렛", "샬롯", "베아트리체", "카타리나", "레베카", "엘레나",
            "마리아", "안나", "루나", "시에라", "니나", "에바", "릴리안", "로렌", "그레이스",
            "에밀리", "한나", "엠마", "매디슨", "애슐리", "사라", "브리트니", "사만다", "제시카",
            "아만다", "스테파니", "니콜", "멜리사", "데보라", "레이첼", "캐서린", "엘리자베스", "해더",
            "티파니", "에이미", "줄리", "조이스", "빅토리아", "켈리", "크리스티나", "조안", "이블린",
            "린다", "바바라", "엘렌", "캐럴", "산드라", "도나", "루스", "샤론", "미셸", "로라",
            "에밀리", "칼라", "레베카", "스테파니", "캐롤라인", "엘리", "제나", "브룩", "케이트",
            "사바나", "제시카", "테일러", "킴벌리", "데이지", "하이디", "가브리엘라", "니키",
            "로린", "셸리", "레슬리", "에리카", "카일린", "애나", "코트니", "루비", "에바",
            "메간", "알렉시스", "소피아", "클로에", "이사벨", "에이바", "밀라", "아리아나",
            "라일라", "미아", "에마", "아드리아나", "알리", "라일리", "캐밀라", "클레어", "빅토리아",
            "엘리아나", "나오미", "엘레나", "네이탈리", "헤일리", "브루클린", "로렌", "앨리슨",
            "가브리엘라", "세라", "자스민", "마야", "사만다", "페넬로페", "오드리", "발레리아",
            "바이올렛", "스카를릿", "애나스타샤", "베로니카", "테레사", "앤젤라", "카르멘", "몰리",
            "셸리", "레이첼", "니콜", "웬디", "리사", "킴벌리", "도나", "아니타", "리비",
            "알리시아", "알렉산드라", "키아라", "조아나", "마리사", "카렌", "스테이시", "다이애나",
            "로즈", "이솔데", "기네비어", "모르가나", "세라피나", "아르테미스", "아테나", "헤라",
            "아프로디테", "헤스티아", "데메테르", "펠레", "프레이야", "이두나", "브룬힐데", "발키리",
            "키르케", "카산드라", "안드로메다", "페넬로페", "헬렌", "클레오파트라", "이시스", "네페르티티",
            "세라핌", "우리엘", "가브리엘라", "미카엘라", "라파엘라", "아리엘", "젤다", "세레나",
            "팬도라", "포에베", "셀레네", "헤카테", "님프", "오로라", "루나", "스텔라", "노바",
            "베가", "안드로메다", "카시오페아", "라이라", "알타이르", "벨라트릭스", "리겔", "시리우스",
            "프로키온", "아크투루스", "스피카", "알데바란", "카펠라", "폴룩스", "레굴루스", "안타레스"
        ]
        
        # 중복되지 않는 이름 선택
        available_names = [name for name in character_names if name not in self._used_names]
        if not available_names:
            # 모든 이름이 사용되었으면 초기화
            self._used_names.clear()
            available_names = character_names
        
        name = random.choice(available_names)
        self._used_names.add(name)
        
        # 직업별 기본 스탯 (레벨 10 기준)
        base_stats = self._get_class_base_stats(class_name)
        
        character = Character(
            name=name,
            character_class=class_name,
            max_hp=base_stats["hp"],
            physical_attack=base_stats["physical_attack"],
            magic_attack=base_stats["magic_attack"],
            physical_defense=base_stats["physical_defense"],
            magic_defense=base_stats["magic_defense"],
            speed=base_stats["speed"]
        )
        
        # 레벨 1로 설정
        character.level = 1
        
        return character
    
    def _get_class_base_stats(self, class_name: str) -> Dict[str, int]:
        """직업별 기본 스탯 (고정값으로 변경)"""
        # 직업별 고정 스탯 정의 (레벨 10 기준)
        fixed_stats = {
            "전사": {"hp": 216, "physical_attack": 75, "magic_attack": 43, "physical_defense": 63, "magic_defense": 48, "speed": 56},
            "아크메이지": {"hp": 121, "physical_attack": 43, "magic_attack": 78, "physical_defense": 33, "magic_defense": 67, "speed": 58},
            "궁수": {"hp": 164, "physical_attack": 74, "magic_attack": 33, "physical_defense": 44, "magic_defense": 43, "speed": 68},
            "도적": {"hp": 150, "physical_attack": 64, "magic_attack": 38, "physical_defense": 43, "magic_defense": 49, "speed": 93},
            "성기사": {"hp": 197, "physical_attack": 67, "magic_attack": 38, "physical_defense": 76, "magic_defense": 62, "speed": 43},
            "암흑기사": {"hp": 189, "physical_attack": 71, "magic_attack": 54, "physical_defense": 58, "magic_defense": 51, "speed": 52},
            "몽크": {"hp": 172, "physical_attack": 82, "magic_attack": 51, "physical_defense": 59, "magic_defense": 64, "speed": 76},
            "바드": {"hp": 107, "physical_attack": 43, "magic_attack": 66, "physical_defense": 38, "magic_defense": 58, "speed": 69},
            "네크로맨서": {"hp": 134, "physical_attack": 44, "magic_attack": 84, "physical_defense": 39, "magic_defense": 74, "speed": 48},
            "용기사": {"hp": 181, "physical_attack": 78, "magic_attack": 62, "physical_defense": 67, "magic_defense": 58, "speed": 61},
            "검성": {"hp": 164, "physical_attack": 83, "magic_attack": 31, "physical_defense": 51, "magic_defense": 47, "speed": 71},
            "정령술사": {"hp": 107, "physical_attack": 49, "magic_attack": 85, "physical_defense": 42, "magic_defense": 69, "speed": 59},
            "암살자": {"hp": 134, "physical_attack": 81, "magic_attack": 28, "physical_defense": 34, "magic_defense": 39, "speed": 87},
            "기계공학자": {"hp": 156, "physical_attack": 63, "magic_attack": 59, "physical_defense": 54, "magic_defense": 48, "speed": 53},
            "무당": {"hp": 121, "physical_attack": 48, "magic_attack": 86, "physical_defense": 44, "magic_defense": 77, "speed": 64},
            "해적": {"hp": 164, "physical_attack": 74, "magic_attack": 34, "physical_defense": 52, "magic_defense": 41, "speed": 77},
            "사무라이": {"hp": 167, "physical_attack": 74, "magic_attack": 45, "physical_defense": 58, "magic_defense": 53, "speed": 67},
            "드루이드": {"hp": 175, "physical_attack": 53, "magic_attack": 81, "physical_defense": 48, "magic_defense": 69, "speed": 59},
            "철학자": {"hp": 107, "physical_attack": 38, "magic_attack": 76, "physical_defense": 54, "magic_defense": 86, "speed": 49},
            "시간술사": {"hp": 121, "physical_attack": 54, "magic_attack": 77, "physical_defense": 49, "magic_defense": 64, "speed": 57},
            "연금술사": {"hp": 135, "physical_attack": 59, "magic_attack": 72, "physical_defense": 44, "magic_defense": 58, "speed": 54},
            "검투사": {"hp": 172, "physical_attack": 79, "magic_attack": 41, "physical_defense": 56, "magic_defense": 48, "speed": 64},
            "기사": {"hp": 216, "physical_attack": 79, "magic_attack": 46, "physical_defense": 72, "magic_defense": 54, "speed": 48},
            "신관": {"hp": 143, "physical_attack": 42, "magic_attack": 79, "physical_defense": 57, "magic_defense": 89, "speed": 52},
            "마검사": {"hp": 164, "physical_attack": 67, "magic_attack": 70, "physical_defense": 54, "magic_defense": 61, "speed": 58},
            "차원술사": {"hp": 84, "physical_attack": 33, "magic_attack": 88, "physical_defense": 28, "magic_defense": 72, "speed": 47},
            "광전사": {"hp": 327, "physical_attack": 64, "magic_attack": 13, "physical_defense": 22, "magic_defense": 21, "speed": 74}
        }
        
        return fixed_stats.get(class_name, {
            "hp": 150, "physical_attack": 50, "magic_attack": 50, 
            "physical_defense": 50, "magic_defense": 50, "speed": 50
        })
    
    def _auto_select_passives(self, character: Character):
        """자동 패시브 선택 (2개 강제)"""
        if not character.available_traits:
            print(f"  {character.name}: 사용 가능한 특성이 없습니다.")
            return
        
        print(f"  {character.name}: 개발 모드 = {game_config.are_all_passives_unlocked()}")
        print(f"  {character.name}: 사용 가능한 특성 수 = {len(character.available_traits)}")
        
        # 개발 모드가 아닌 경우 해금된 패시브만 선택 가능
        if not game_config.are_all_passives_unlocked():
            unlocked_traits = character._get_unlocked_traits()
            available_indices = []
            for i, trait in enumerate(character.available_traits):
                if trait.name in unlocked_traits:
                    available_indices.append(i)
            
            # 해금된 패시브가 없으면 패시브 없이 진행
            if not available_indices:
                character.select_passive_traits([])
                return
            
            # 해금된 패시브 중에서 2개 선택 (가능한 만큼)
            num_to_select = min(2, len(available_indices))
            if num_to_select > 0:
                selected_indices = random.sample(available_indices, num_to_select)
                character.select_passive_traits(selected_indices)
            else:
                character.select_passive_traits([])
        else:
            # 개발 모드에서는 직업 특성을 고려한 패시브 선택 로직
            trait_priorities = self._get_trait_priorities(character.character_class)
            
            # 우선순위에 따라 정렬
            sorted_traits = []
            for i, trait in enumerate(character.available_traits):
                priority = trait_priorities.get(trait.name, 0)
                sorted_traits.append((i, trait, priority))  # 인덱스도 함께 저장
            
            sorted_traits.sort(key=lambda x: x[2], reverse=True)  # priority로 정렬
            
            # 항상 2개 선택 (사용 가능한 특성이 있다면)
            selected_indices = []
            
            if len(sorted_traits) >= 2:
                # 상위 2개 특성 선택
                selected_indices = [sorted_traits[0][0], sorted_traits[1][0]]
            elif len(sorted_traits) == 1:
                # 1개만 있으면 1개만 선택
                selected_indices = [sorted_traits[0][0]]
            
            # 패시브 적용
            character.select_passive_traits(selected_indices)
    
    def _get_trait_priorities(self, class_name: str) -> Dict[str, int]:
        """직업별 특성 우선순위 (새로운 스킬 시스템에 맞춤 - 27개 직업)"""
        priorities = {
            "전사": {"불굴의 의지": 10, "균형감각": 9, "전투 본능": 8, "방어 전문가": 7, "위협적 존재": 6},
            "아크메이지": {"마법 지식": 10, "마력 조절": 9, "집중력": 8, "원소 친화": 7, "마력 폭주": 6},
            "궁수": {"정밀함": 10, "집중력": 9, "연속 사격": 8, "원거리 전문가": 7, "사냥꾼의 직감": 6},
            "도적": {"은신술": 10, "독 저항": 9, "치명타 전문가": 8, "민첩성": 7, "그림자 조작": 6},
            "성기사": {"신성 가호": 10, "치유술": 9, "정의감": 8, "빛의 가호": 7, "수호의 맹세": 6},
            "암흑기사": {"흡혈술": 10, "어둠 친화": 9, "생명력 조작": 8, "타락한 힘": 7, "불사의 의지": 6},
            "몽크": {"내공술": 10, "연타 전문가": 9, "정신 수련": 8, "기 조절": 7, "참선의 깨달음": 6},
            "바드": {"음악 재능": 10, "파티 지원": 9, "매혹술": 8, "정신 조작": 7, "카리스마": 6},
            "네크로맨서": {"죽음 친화": 10, "영혼 조작": 9, "언데드 지배": 8, "생명 흡수": 7, "공포 유발": 6},
            "용기사": {"용의 혈통": 10, "화염 친화": 9, "드래곤 브레스": 8, "비늘 갑옷": 7, "고대의 지혜": 6},
            "검성": {"검기 조작": 10, "완벽한 검술": 9, "일섬 달인": 8, "검의 도": 7, "무사도": 6},
            "정령술사": {"원소 조작": 10, "정령 소통": 9, "원소 융합": 8, "자연 친화": 7, "마나 효율": 6},
            "시간술사": {"시간 조작": 10, "미래 예측": 9, "시공간 인식": 8, "시간 역행": 7, "인과 조작": 6},
            "연금술사": {"화학 지식": 10, "폭발 제어": 9, "물질 변환": 8, "연성술": 7, "실험 정신": 6},
            "차원술사": {"공간 조작": 10, "차원 이동": 9, "공간 인식": 8, "차원 균열": 7, "무한 지식": 6},
            "암살자": {"완벽한 은신": 10, "즉사술": 9, "독 전문가": 8, "그림자 조작": 7, "치명타 특화": 6},
            "기계공학자": {"기계 조작": 10, "에너지 제어": 9, "로봇 공학": 8, "과학 지식": 7, "창의성": 6},
            "무당": {"영혼 시야": 10, "정신 지배": 9, "귀신 소통": 8, "주술 지식": 7, "영적 보호": 6},
            "해적": {"이도류 달인": 10, "보물 감각": 9, "항해술": 8, "약탈 전문가": 7, "운명의 바람": 6},
            "사무라이": {"무사도 정신": 10, "거합 달인": 9, "명예 수호": 8, "검의 길": 7, "집중력": 6},
            "드루이드": {"자연 소통": 10, "동물 변신": 9, "자연 마법": 8, "생태 지식": 7, "식물 성장": 6},
            "철학자": {"논리적 사고": 10, "진리 추구": 9, "지식 축적": 8, "설득술": 7, "학자의 직감": 6},
            "검투사": {"관중 의식": 10, "투기 기술": 9, "생존술": 8, "화려한 전투": 7, "명성": 6},
            "기사": {"기사도 정신": 10, "창술 달인": 9, "명예 수호": 8, "돌격술": 7, "귀족의 품격": 6},
            "신관": {"신성 가호": 10, "치유 전문가": 9, "신앙심": 8, "축복술": 7, "정화": 6},
            "마검사": {"마검 조화": 10, "원소 검술": 9, "마법 검기": 8, "이중 수련": 7, "균형 감각": 6},
            "광전사": {"광폭화": 10, "분노 제어": 9, "야생 본능": 8, "무모한 용기": 7, "전투 흥분": 6}
        }
        
        return priorities.get(class_name, {})
    
    def _analyze_party(self, party: List[Character]):
        """파티 분석 및 시너지 표시"""
        print(f"\n{GREEN}=== 생성된 파티 ==={RESET}")
        
        # 파티 구성 표시
        for i, character in enumerate(party, 1):
            role = self._get_character_role(character.character_class)
            passives = [trait.name for trait in character.active_traits]
            
            print(f"{WHITE}{i}. {character.name}{RESET}")
            print(f"   직업: {CYAN}{character.character_class}{RESET} ({role})")
            print(f"   레벨: {character.level}")
            print(f"   스탯: HP {character.max_hp}, 물공 {character.physical_attack}, 마공 {character.magic_attack}")
            print(f"   패시브: {YELLOW}{', '.join(passives)}{RESET}")
            print()
        
        # 역할 분석
        roles = self._analyze_roles([c.character_class for c in party])
        print(f"{BLUE}파티 역할 구성:{RESET}")
        for role, count in roles.items():
            if count > 0:
                print(f"  {role}: {count}명")
        
        # 시너지 확인
        synergies = self._check_synergies(party)
        if synergies:
            print(f"\n{MAGENTA}파티 시너지:{RESET}")
            for synergy in synergies:
                print(f"  ✨ {synergy}")
        
        print(f"\n{GREEN}파티 구성 완료! 🎉{RESET}")
    
    def _get_character_role(self, class_name: str) -> str:
        """캐릭터의 역할 반환"""
        for role, classes in self.ROLE_CLASSES.items():
            if class_name in classes:
                return role
        return "기타"
    
    def _check_synergies(self, party: List[Character]) -> List[str]:
        """파티 시너지 확인"""
        synergies = []
        party_classes = [c.character_class for c in party]
        
        for combination, info in self.SYNERGY_COMBINATIONS.items():
            classes = combination.split(" + ")
            if all(cls in party_classes for cls in classes):
                synergies.append(f"{combination}: {info['effect']}")
        
        return synergies
    
    def get_balanced_party_from_list(self, unlocked_names: List[str]) -> List[str]:
        """해금된 캐릭터 목록에서 균형잡힌 파티 구성 (이름만 반환)"""
        if len(unlocked_names) < 4:
            return unlocked_names
        
        # 역할별로 분류
        available_by_role = {role: [] for role in self.ROLE_CLASSES.keys()}
        
        for name in unlocked_names:
            for role, classes in self.ROLE_CLASSES.items():
                if name in classes:
                    available_by_role[role].append(name)
                    break
        
        # 균형잡힌 파티 구성 (각 역할에서 1명씩)
        selected = []
        
        # 탱커 1명
        if available_by_role["탱커"]:
            selected.append(random.choice(available_by_role["탱커"]))
        
        # 딜러 1명
        if available_by_role["딜러"]:
            selected.append(random.choice(available_by_role["딜러"]))
        
        # 마법사 1명
        if available_by_role["마법사"]:
            selected.append(random.choice(available_by_role["마법사"]))
        
        # 서포터 또는 하이브리드 1명
        support_pool = available_by_role["서포터"] + available_by_role["하이브리드"]
        if support_pool:
            selected.append(random.choice(support_pool))
        
        # 4명이 안 되면 나머지 해금된 캐릭터로 채우기
        remaining = [name for name in unlocked_names if name not in selected]
        while len(selected) < 4 and remaining:
            selected.append(remaining.pop(0))
        
        return selected[:4]

# 전역 자동 파티 빌더 인스턴스
auto_party_builder = AutoPartyBuilder()

def get_auto_party_builder() -> AutoPartyBuilder:
    """자동 파티 빌더 반환"""
    return auto_party_builder
