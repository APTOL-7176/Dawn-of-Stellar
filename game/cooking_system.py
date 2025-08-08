"""
개선된 요리 시스템 - 최대 HP 증가, 상처 시스템, BRV 시스템 연동, 영구 진행 상황 포함
"""

import random
import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# SFX 시스템 import
try:
    from game.audio_system import get_audio_manager, SFXType
    audio_manager = get_audio_manager()
except ImportError:
    print("오디오 시스템을 찾을 수 없습니다. 소리 없이 진행합니다.")
    audio_manager = None

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

class IngredientType(Enum):
    """식재료 타입"""
    MEAT = "고기류"
    SEAFOOD = "해산물"
    VEGETABLE = "채소류"
    FRUIT = "과일류"
    GRAIN = "곡물류"
    HERB = "약초류"
    SPICE = "향신료"
    LIQUID = "액체류"
    SPECIAL = "특수재료"

@dataclass
class Ingredient:
    """식재료 클래스"""
    name: str
    type: IngredientType
    rarity: int  # 1-5 (1이 가장 흔함)
    description: str
    icon: str = "🥕"
    value: float = 1.0  # 재료 가치 (같은 타입 내에서 대체 가능)
    weight: float = 0.1  # 무게 (kg)

@dataclass
class Recipe:
    """요리 레시피 클래스 - 돈스타브 스타일 제약 조건 포함"""
    name: str
    ingredients: Dict[str, float]  # 재료 타입: 필요 가치
    effects: Dict[str, int]  # 효과명: 효과값
    duration_steps: int  # 효과 지속 걸음 수
    description: str
    icon: str = "🍳"
    special_effects: List[str] = field(default_factory=list)  # 특수 효과들
    priority: int = 1  # 우선도 (높을수록 우선 제작)
    difficulty: int = 1  # 제작 난이도 (실패 확률에 영향)
    weight: float = 0.3  # 완성된 요리의 무게 (kg)
    forbidden_ingredients: List[str] = field(default_factory=list)  # 금지 재료 타입들
    required_specific: Dict[str, float] = field(default_factory=dict)  # 특정 재료 필수 (재료명: 수량)
    max_ingredients: Dict[str, float] = field(default_factory=dict)  # 재료 최대 제한 (타입: 최대값)
    cooking_method: str = "일반"  # 요리 방법 (굽기, 끓이기, 튀기기 등)

@dataclass
class CookingBuff:
    """요리 버프 클래스"""
    recipe_name: str
    effects: Dict[str, int]
    remaining_steps: int
    special_effects: List[str]
    icon: str

# 적별 특정 식재료 드롭 테이블 (확장)
ENEMY_SPECIFIC_DROPS = {
    # 기본 몬스터
    "고블린": ["작은 고기", "잡초", "야생 버섯"],
    "오크": ["멧돼지 고기", "야생 당근", "거친 가죽"],
    "스켈레톤": ["철광석", "고대 보리", "뼈 가루"],
    "좀비": ["독버섯", "썩은 고기", "저주받은 약초"],
    "거미": ["거대 거미 다리", "독버섯", "거미줄"],
    "늑대": ["늑대 고기", "용기 풀", "야생의 향신료"],
    "곰": ["곰 고기", "회복 허브", "곰 가죽"],
    
    # 중급 몬스터  
    "트롤": ["트롤 고기", "고대 이끼", "재생 약초"],
    "오우거": ["거대 고기", "야만 향신료", "거인의 뼈"],
    "와이번": ["와이번 날개", "하늘의 정수", "바람의 깃털"],
    "슬라임": ["젤라틴", "끈적한 액체", "슬라임 코어"],
    "미믹": ["모조 금속", "속임수 약초", "변화의 정수"],
    "가고일": ["석화 가루", "고대 석재", "대지의 정수"],
    "뱀파이어": ["붉은 와인", "박쥐 날개", "암흑의 정수"],
    "리치": ["언데드 향신료", "생명력 정수", "마법 뼈"],
    
    # 고급 몬스터
    "드래곤": ["드래곤 고기", "용의 피", "별가루", "용의 비늘"],
    "미노타우르스": ["미노타우르스 고기", "고대 룬", "미궁의 허브"],
    "그리폰": ["그리폰 날개", "정령의 눈물", "하늘의 깃털"],
    "정령": ["정령의 눈물", "마나 허브", "원소 결정"],
    "악마": ["악마의 뿔", "어둠의 정수", "지옥의 향신료"],
    "피닉스": ["불멸의 깃털", "부활의 재", "화염 정수"],
    "크라켄": ["크라켄 촉수", "심해의 진주", "바다의 정수"],
    "키메라": ["키메라 고기", "합성 향신료", "변이 정수"],
    
    # 전설급 몬스터
    "바하무트": ["신룡의 고기", "창조의 정수", "별의 조각"],
    "레비아탄": ["거대 바다뱀 고기", "심연의 정수", "대해의 진주"],
    "이프리트": ["화염왕의 정수", "용암 결정", "불의 왕관"],
    "시바": ["얼음여왕의 정수", "빙설 결정", "얼음의 왕관"],
    "타이탄": ["대지왕의 정수", "암석 결정", "땅의 왕관"],
    "알렉산더": ["기계신의 정수", "성스러운 기어", "빛의 결정"],
    
    # 특수 몬스터
    "엔젤": ["천사의 깃털", "성수", "신성 허브"],
    "데빌": ["악마의 혈액", "저주의 향신료", "지옥불 정수"],
    "유니콘": ["순수한 뿔", "치유의 물", "정화 약초"],
    "다크 유니콘": ["타락한 뿔", "어둠의 물", "저주 약초"],
    "펜릴": ["거대 늑대 고기", "달빛 갈기", "야성의 정수"],
    "요르문간드": ["세계뱀 고기", "독의 정수", "거대 비늘"],
    
    # 환상종
    "세이렌": ["매혹의 목소리", "바다 거품", "환상 진주"],
    "하피": ["폭풍 깃털", "선풍 정수", "날개 고기"],
    "메두사": ["석화의 뱀발", "고르곤 눈물", "저주의 머리카락"],
    "스핑크스": ["수수께끼 정수", "지혜의 가루", "모래 시계"],
}

# 지역별 특산 식재료 확장

# 지역별 특산 식재료 확장
GATHERING_LOCATIONS = {
    "숲속 채집지": {
        "common": ["잡초", "야생 당근", "들딸기", "풀잎", "솔방울", "나뭇잎", "야생 버섯"],
        "uncommon": ["회복 허브", "마나 허브", "독버섯", "야생의 향신료", "숲의 정수"],
        "rare": ["용기 풀", "치유 베리", "고대 이끼", "엘프의 잎"],
        "icon": "🌲",
        "description": "울창한 숲에서 약초와 과일을 채집할 수 있습니다."
    },
    "강가 채집지": {
        "common": ["물", "물고기", "민물새우", "강바닥 이끼", "물풀", "연꽃잎"],
        "uncommon": ["달빛 이슬", "강물 허브", "물의 정수", "강 조개"],
        "rare": ["정령의 눈물", "수정", "진주 조개", "물의 왕관"],
        "icon": "🏞️",
        "description": "맑은 강물 근처에서 특별한 재료를 찾을 수 있습니다."
    },
    "동굴 채집지": {
        "common": ["철광석", "소금", "버섯", "박쥐 털", "동굴 이끼", "석탄"],
        "uncommon": ["크리스탈", "고대 보리", "석화 가루", "지하수"],
        "rare": ["별가루", "고대 룬", "다이아몬드", "용암 결정"],
        "icon": "🕳️",
        "description": "어두운 동굴에서 광물과 특수 재료를 채집합니다."
    },
    "고원 채집지": {
        "common": ["산나물", "바람꽃", "찬바람 허브", "고산 열매", "빙하수"],
        "uncommon": ["황금 포도", "하늘 꿀", "구름 솜", "서리 잎"],
        "rare": ["시간 과일", "요정의 가루", "하늘의 정수", "별빛 이슬"],
        "icon": "🏔️",
        "description": "높은 고원에서 희귀한 식재료를 찾을 수 있습니다."
    },
    "화산 채집지": {
        "common": ["화산석", "유황", "용암 이끼", "화염 허브", "마그마 열매"],
        "uncommon": ["화염 결정", "용암 정수", "불꽃 씨앗", "화산 소금"],
        "rare": ["불의 왕관", "피닉스 재", "화염왕의 정수", "용의 비늘"],
        "icon": "🌋",
        "description": "활화산 근처에서 화염 속성 재료를 채집합니다."
    },
    "빙하 채집지": {
        "common": ["얼음 조각", "눈꽃", "서리 열매", "빙하 물", "겨울 나뭇잎"],
        "uncommon": ["빙설 결정", "서리 정수", "얼음 진주", "극지 허브"],
        "rare": ["얼음의 왕관", "빙하 여왕의 눈물", "영원한 얼음", "시바의 축복"],
        "icon": "🧊",
        "description": "영원한 빙하에서 얼음 속성 재료를 채집합니다."
    },
    "사막 채집지": {
        "common": ["선인장", "사막 열매", "모래", "오아시스 물", "건조 약초"],
        "uncommon": ["사막 장미", "미라지 정수", "모래 시계", "황금 모래"],
        "rare": ["사막의 진주", "신기루 정수", "파라오의 보물", "태양의 조각"],
        "icon": "🏜️",
        "description": "뜨거운 사막에서 희귀한 보물을 찾을 수 있습니다."
    },
    "심해 채집지": {
        "common": ["해조류", "조개껍질", "바닷물", "산호 조각", "심해 물고기"],
        "uncommon": ["진주", "바다의 정수", "크라켄 먹물", "인어의 비늘"],
        "rare": ["바다의 왕관", "심연의 정수", "대해의 진주", "포세이돈의 삼지창"],
        "icon": "🌊",
        "description": "깊은 바다에서 신비한 해양 재료를 채집합니다."
    },
    "천공 채집지": {
        "common": ["구름", "하늘 바람", "별먼지", "천사의 깃털", "빛의 조각"],
        "uncommon": ["하늘의 정수", "구름 정수", "바람의 깃털", "성스러운 이슬"],
        "rare": ["별의 조각", "천사의 눈물", "신의 축복", "창조의 정수"],
        "icon": "☁️",
        "description": "하늘 높은 곳에서 신성한 재료를 찾을 수 있습니다."
    },
    "지하 세계": {
        "common": ["지옥불", "마그마", "악마의 뿔", "저주받은 뼈", "어둠의 가루"],
        "uncommon": ["지옥의 향신료", "악마의 혈액", "저주의 정수", "어둠의 결정"],
        "rare": ["지옥의 왕관", "사탄의 눈물", "어둠의 정수", "파멸의 씨앗"],
        "icon": "🔥",
        "description": "지하 깊은 곳에서 어둠의 힘이 담긴 재료를 얻습니다."
    }
}

class CookingSystem:
    """개선된 요리 시스템 메인 클래스"""
    
    def __init__(self):
        self.ingredients_inventory = {}  # 보유 식재료
        self.cooked_food_inventory = {}  # 완성된 요리 인벤토리
        self.active_buffs = []  # 활성 요리 버프들
        self.active_food_effect = None  # 현재 활성 요리 효과 (중복 방지용)
        self.discovered_recipes = set()  # 발견한 레시피들
        self.cooking_experience = 0  # 요리 경험치
        self.cooking_level = 1  # 요리 레벨
        self.party_manager = None  # 파티 매니저 참조
        
        self._init_ingredients()
        self._init_recipes()
        self._load_permanent_recipes()  # 영구 레시피 로드
    
    def show_cooking_menu(self):
        """요리 메뉴 표시 - 메인 인터페이스"""
        try:
            from game.cursor_menu_system import create_simple_menu
            
            options = [
                "🥘 요리하기",
                "🍽️ 요리 섭취",
                "📦 식재료 확인",
                "🍳 완성된 요리 확인",
                "✨ 활성 버프 확인",
                "🌍 채집지 정보",
                "⚔️ 전투 드롭 정보",
                "📖 레시피 컬렉션"
            ]
            
            descriptions = [
                "보유한 재료로 요리를 만듭니다",
                "완성된 요리를 먹어서 버프를 받습니다",
                "현재 보유한 식재료를 확인합니다", 
                "완성된 요리 목록을 확인합니다",
                "현재 활성화된 요리 버프를 확인합니다",
                "채집 가능한 장소들을 확인합니다",
                "적 처치 시 식재료 드롭 정보를 확인합니다",
                "발견한 레시피들을 확인합니다"
            ]
            
            while True:
                # 상태 정보 표시
                print(f"\n📊 요리 시스템 상태:")
                print(f"  요리 레벨: {self.cooking_level}")
                print(f"  식재료: {len(self.ingredients_inventory)}종류")
                print(f"  완성 요리: {len(self.cooked_food_inventory)}종류")
                print(f"  활성 버프: {len(self.active_buffs)}개")
                print(f"  무게: {self.get_total_inventory_weight():.1f}/{self.get_max_inventory_weight():.1f}kg")
                print(self.get_food_status())
                
                menu = create_simple_menu("🍳 요리 시스템", options, descriptions)
                result = menu.run()
                
                if result is None:  # 취소
                    break
                elif result == 0:  # 요리하기
                    self._show_cooking_recipes()
                elif result == 1:  # 요리 섭취
                    self._show_food_consumption()
                elif result == 2:  # 식재료 확인
                    self.show_ingredients_inventory()
                    input("아무 키나 눌러 계속...")
                elif result == 3:  # 완성된 요리 확인
                    self.show_cooked_food_inventory()
                    input("아무 키나 눌러 계속...")
                elif result == 4:  # 활성 버프 확인
                    self.show_active_buffs()
                    input("아무 키나 눌러 계속...")
                elif result == 5:  # 채집지 정보
                    self.show_gathering_locations()
                    input("아무 키나 눌러 계속...")
                elif result == 6:  # 전투 드롭 정보
                    self.show_combat_drop_info()
                    input("아무 키나 눌러 계속...")
                elif result == 7:  # 레시피 컬렉션
                    show_recipe_collection()
                    
        except ImportError:
            # 폴백: 기존 텍스트 메뉴
            self._show_cooking_menu_fallback()
    
    def _show_cooking_menu_fallback(self):
        """요리 메뉴 폴백 (기존 방식)"""
        while True:
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{WHITE}{BOLD}🍳 요리 시스템{RESET}")
            print(f"{CYAN}{'='*60}{RESET}")
            
            # 상태 정보 표시
            print(f"요리 레벨: {self.cooking_level}")
            print(f"식재료: {len(self.ingredients_inventory)}종류")
            print(f"완성 요리: {len(self.cooked_food_inventory)}종류")
            print(f"활성 버프: {len(self.active_buffs)}개")
            print(f"무게: {self.get_total_inventory_weight():.1f}/{self.get_max_inventory_weight():.1f}kg")
            print(self.get_food_status())
            
            print(f"\n{YELLOW}1. 🥘 요리하기{RESET}")
            print(f"{YELLOW}2. 🍽️ 요리 섭취{RESET}")
            print(f"{YELLOW}3. 📦 식재료 확인{RESET}")
            print(f"{YELLOW}4. 🍳 완성된 요리 확인{RESET}")
            print(f"{YELLOW}5. ✨ 활성 버프 확인{RESET}")
            print(f"{YELLOW}6. 🌍 채집지 정보{RESET}")
            print(f"{YELLOW}7. 📖 레시피 컬렉션{RESET}")
            print(f"{YELLOW}0. 돌아가기{RESET}")
            
            try:
                choice = input(f"\n{WHITE}선택: {RESET}").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._show_cooking_recipes()
                elif choice == '2':
                    self._show_food_consumption()
                elif choice == '3':
                    self.show_ingredients_inventory()
                    input("아무 키나 눌러 계속...")
                elif choice == '4':
                    self.show_cooked_food_inventory()
                    input("아무 키나 눌러 계속...")
                elif choice == '5':
                    self.show_active_buffs()
                    input("아무 키나 눌러 계속...")
                elif choice == '6':  
                    self.show_gathering_locations()
                    input("아무 키나 눌러 계속...")
                elif choice == '7':
                    show_recipe_collection()
                else:
                    print("올바른 선택지를 입력하세요.")
                    
            except (ValueError, KeyboardInterrupt):
                break

    def _show_cooking_recipes(self):
        """요리 제작 메뉴"""
        print(f"\n{CYAN}{'='*80}{RESET}")
        print(f"{WHITE}{BOLD}🥘 요리 제작{RESET}")
        print(f"{CYAN}{'='*80}{RESET}")
        
        # 발견한 레시피 중 제작 가능한 것들 표시
        quick_recipes = self.get_quick_cooking_menu()
        if quick_recipes:
            print(f"\n{GREEN}⚡ 빠른 요리 (발견한 레시피):{RESET}")
            for i, recipe_name in enumerate(quick_recipes[:10], 1):
                recipe = self.all_recipes[recipe_name]
                print(f"  [{i}] {recipe.icon} {recipe_name} - {recipe.description}")
            
            try:
                choice = input(f"\n빠른 요리 선택 (1-{len(quick_recipes[:10])}) 또는 0(돌아가기): ").strip()
                if choice == '0':
                    return
                elif choice.isdigit() and 1 <= int(choice) <= len(quick_recipes[:10]):
                    selected_recipe = quick_recipes[int(choice) - 1]
                    success, message = self.quick_cook_dish(selected_recipe)
                    print(f"\n{GREEN if success else RED}{message}{RESET}")
                    input("아무 키나 눌러 계속...")
                    return
            except (ValueError, IndexError):
                print("올바른 선택지를 입력하세요.")
        
        # 실험적 요리 (모든 레시피 시도 가능)
        print(f"\n{YELLOW}🧪 실험적 요리 (모든 레시피 시도 가능):{RESET}")
        print("재료가 있으면 모든 레시피를 시도할 수 있습니다.")
        
        available_recipes = []
        for recipe_name, recipe in self.all_recipes.items():
            if recipe_name == "곤죽":  # 실패작은 제외
                continue
            can_cook, _ = self.can_cook_with_substitutes(recipe_name)
            if can_cook:
                available_recipes.append(recipe_name)
        
        if available_recipes:
            print(f"\n{CYAN}제작 가능한 레시피:{RESET}")
            for i, recipe_name in enumerate(available_recipes[:20], 1):  # 최대 20개
                recipe = self.all_recipes[recipe_name]
                new_mark = " 🆕" if recipe_name not in self.discovered_recipes else ""
                print(f"  [{i}] {recipe.icon} {recipe_name}{new_mark}")
            
            try:
                choice = input(f"\n실험 요리 선택 (1-{len(available_recipes[:20])}) 또는 0(돌아가기): ").strip()
                if choice == '0':
                    return
                elif choice.isdigit() and 1 <= int(choice) <= len(available_recipes[:20]):
                    selected_recipe = available_recipes[int(choice) - 1]
                    success, message = self.cook_dish(selected_recipe)
                    print(f"\n{GREEN if success else RED}{message}{RESET}")
                    if success and selected_recipe not in self.discovered_recipes:
                        print(f"{MAGENTA}🎉 새로운 레시피를 발견했습니다: {selected_recipe}!{RESET}")
                    input("아무 키나 눌러 계속...")
            except (ValueError, IndexError):
                print("올바른 선택지를 입력하세요.")
        else:
            print(f"{RED}현재 제작 가능한 요리가 없습니다.{RESET}")
            input("아무 키나 눌러 계속...")

    def _show_food_consumption(self):
        """요리 섭취 메뉴"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🍽️ 요리 섭취{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        # 현재 상태 표시
        print(self.get_food_status())
        
        if not self.cooked_food_inventory:
            print(f"\n{RED}섭취할 수 있는 요리가 없습니다.{RESET}")
            input("아무 키나 눌러 계속...")
            return
        
        # 이미 배부른 상태면 섭취 불가
        if self.active_food_effect is not None:
            print(f"\n{RED}이미 배부른 상태입니다. 다른 요리를 먹을 수 없습니다.{RESET}")
            input("아무 키나 눌러 계속...")
            return
        
        print(f"\n{GREEN}섭취 가능한 요리:{RESET}")
        foods = list(self.cooked_food_inventory.items())
        for i, (food_name, amount) in enumerate(foods, 1):
            recipe = self.all_recipes.get(food_name)
            if recipe:
                print(f"  [{i}] {recipe.icon} {food_name} x{amount}")
                print(f"      {recipe.description}")
        
        try:
            choice = input(f"\n섭취할 요리 선택 (1-{len(foods)}) 또는 0(돌아가기): ").strip()
            if choice == '0':
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(foods):
                selected_food = foods[int(choice) - 1][0]
                success, message = self.consume_food(selected_food)
                print(f"\n{GREEN if success else RED}{message}{RESET}")
                
                if success:
                    # 효과 상세 표시
                    recipe = self.all_recipes[selected_food] 
                    print(f"\n{CYAN}적용된 효과:{RESET}")
                    for effect, value in recipe.effects.items():
                        print(f"  • {effect}: +{value}")
                    if recipe.special_effects:
                        print(f"  • 특수효과: {', '.join(recipe.special_effects)}")
                    print(f"  • 지속시간: {recipe.duration_steps}걸음")
                
                input("아무 키나 눌러 계속...")
        except (ValueError, IndexError):
            print("올바른 선택지를 입력하세요.")
            input("아무 키나 눌러 계속...")

    def set_party_manager(self, party_manager):
        """파티 매니저 설정"""
        self.party_manager = party_manager
    
    def _load_permanent_recipes(self):
        """영구 진행 상황에서 발견한 레시피 로드"""
        try:
            if os.path.exists("permanent_progress.json"):
                with open("permanent_progress.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # discovered_recipes가 있으면 로드
                if "discovered_recipes" in data:
                    self.discovered_recipes = set(data["discovered_recipes"])
                    print(f"영구 레시피 {len(self.discovered_recipes)}개 로드됨")
        except Exception as e:
            print(f"영구 레시피 로드 실패: {e}")
    
    def _save_permanent_recipes(self):
        """영구 진행 상황에 발견한 레시피 저장"""
        try:
            # 기존 파일 로드
            data = {}
            if os.path.exists("permanent_progress.json"):
                with open("permanent_progress.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            # 발견한 레시피 추가
            data["discovered_recipes"] = list(self.discovered_recipes)
            
            # 파일 저장
            with open("permanent_progress.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"영구 레시피 저장 실패: {e}")
    
    def get_max_inventory_weight(self) -> float:
        """파티의 총 무게한계 반환"""
        if self.party_manager:
            max_weight = 0.0
            for member in self.party_manager.members:
                if hasattr(member, 'inventory'):
                    max_weight += member.inventory.max_weight
            return max_weight if max_weight > 0 else 60.0
        return 60.0  # 기본값
    
    def _init_ingredients(self):
        """식재료 데이터 초기화 (무게 포함)"""
        self.all_ingredients = {
            # 고기류 - 대폭 확장
            "작은 고기": Ingredient("작은 고기", IngredientType.MEAT, 1, "작은 동물의 고기", "🥩", 0.5, 0.2),
            "토끼 고기": Ingredient("토끼 고기", IngredientType.MEAT, 1, "부드러운 토끼 고기", "🐰", 0.8, 0.5),
            "닭고기": Ingredient("닭고기", IngredientType.MEAT, 1, "담백한 닭고기", "🐔", 1.0, 0.8),
            "오리 고기": Ingredient("오리 고기", IngredientType.MEAT, 1, "기름진 오리 고기", "🦆", 1.2, 0.9),
            "멧돼지 고기": Ingredient("멧돼지 고기", IngredientType.MEAT, 2, "질긴 야생 멧돼지 고기", "🐗", 1.5, 1.2),
            "사슴 고기": Ingredient("사슴 고기", IngredientType.MEAT, 2, "고급스러운 사슴 고기", "🦌", 1.8, 1.1),
            "늑대 고기": Ingredient("늑대 고기", IngredientType.MEAT, 3, "야성적인 맛의 늑대 고기", "🐺", 2.0, 1.5),
            "곰 고기": Ingredient("곰 고기", IngredientType.MEAT, 3, "거대한 곰의 고기", "🐻", 3.0, 2.5),
            "양고기": Ingredient("양고기", IngredientType.MEAT, 2, "부드러운 양고기", "🐑", 1.7, 1.3),
            "소고기": Ingredient("소고기", IngredientType.MEAT, 2, "고급 소고기", "🐄", 2.2, 1.8),
            "거대 거미 다리": Ingredient("거대 거미 다리", IngredientType.MEAT, 3, "거대한 거미의 다리", "🕷️", 4.0, 1.8),
            "미노타우르스 고기": Ingredient("미노타우르스 고기", IngredientType.MEAT, 4, "전설적인 미노타우르스의 고기", "🐂", 5.0, 3.0),
            "드래곤 고기": Ingredient("드래곤 고기", IngredientType.MEAT, 5, "전설적인 드래곤의 고기", "🐉", 8.0, 4.0),
            "그리폰 날개": Ingredient("그리폰 날개", IngredientType.MEAT, 5, "하늘을 나는 그리폰의 날개", "🦅", 6.0, 1.5),
            "썩은 고기": Ingredient("썩은 고기", IngredientType.MEAT, 1, "썩어가는 고기", "🤢", 0.3, 0.3),
            "악마의 고기": Ingredient("악마의 고기", IngredientType.MEAT, 4, "지옥에서 온 악마의 고기", "😈", 4.5, 2.2),
            "천사의 고기": Ingredient("천사의 고기", IngredientType.MEAT, 5, "천상의 존재의 고기", "👼", 7.0, 0.8),
            
            # 해산물 - 새로 추가
            "물고기": Ingredient("물고기", IngredientType.SEAFOOD, 1, "신선한 강물고기", "🐟", 0.6, 0.4),
            "민물새우": Ingredient("민물새우", IngredientType.SEAFOOD, 2, "작지만 맛있는 새우", "🦐", 0.8, 0.2),
            "연어": Ingredient("연어", IngredientType.SEAFOOD, 2, "고급 연어", "🐠", 2.5, 1.2),
            "참치": Ingredient("참치", IngredientType.SEAFOOD, 3, "고급 참치", "🐟", 4.0, 2.0),
            "바닷가재": Ingredient("바닷가재", IngredientType.SEAFOOD, 3, "신선한 바닷가재", "🦞", 3.5, 1.5),
            "게": Ingredient("게", IngredientType.SEAFOOD, 2, "신선한 게", "🦀", 2.0, 0.8),
            "굴": Ingredient("굴", IngredientType.SEAFOOD, 2, "바다의 우유 굴", "🦪", 1.5, 0.3),
            "전복": Ingredient("전복", IngredientType.SEAFOOD, 3, "고급 전복", "🐚", 3.0, 0.5),
            "바다뱀 고기": Ingredient("바다뱀 고기", IngredientType.SEAFOOD, 4, "신비한 바다뱀", "🐍", 5.0, 2.5),
            "크라켄 촉수": Ingredient("크라켄 촉수", IngredientType.SEAFOOD, 5, "전설의 바다 괴물", "🐙", 8.0, 3.0),
            
            # 채소류 - 대폭 확장
            "잡초": Ingredient("잡초", IngredientType.VEGETABLE, 1, "그냥 잡초", "🌱", 0.3, 0.1),
            "야생 당근": Ingredient("야생 당근", IngredientType.VEGETABLE, 1, "숲에서 자란 당근", "🥕", 0.8, 0.2),
            "양파": Ingredient("양파", IngredientType.VEGETABLE, 1, "매운 양파", "🧅", 0.7, 0.3),
            "감자": Ingredient("감자", IngredientType.VEGETABLE, 1, "평범한 감자", "🥔", 1.0, 0.4),
            "고구마": Ingredient("고구마", IngredientType.VEGETABLE, 1, "달콤한 고구마", "🍠", 1.2, 0.5),
            "양배추": Ingredient("양배추", IngredientType.VEGETABLE, 1, "신선한 양배추", "🥬", 1.1, 0.6),
            "시금치": Ingredient("시금치", IngredientType.VEGETABLE, 1, "철분 가득한 시금치", "🥬", 0.8, 0.3),
            "브로콜리": Ingredient("브로콜리", IngredientType.VEGETABLE, 1, "영양가 높은 브로콜리", "🥦", 1.0, 0.4),
            "콜리플라워": Ingredient("콜리플라워", IngredientType.VEGETABLE, 1, "하얀 콜리플라워", "🥬", 1.1, 0.5),
            "오이": Ingredient("오이", IngredientType.VEGETABLE, 1, "아삭한 오이", "🥒", 0.6, 0.2),
            "토마토": Ingredient("토마토", IngredientType.VEGETABLE, 1, "빨간 토마토", "🍅", 0.9, 0.3),
            "가지": Ingredient("가지", IngredientType.VEGETABLE, 1, "보라색 가지", "🍆", 1.0, 0.4),
            "호박": Ingredient("호박", IngredientType.VEGETABLE, 2, "큰 호박", "🎃", 2.5, 1.2),
            "마법 양파": Ingredient("마법 양파", IngredientType.VEGETABLE, 3, "마법력이 깃든 양파", "🧅", 2.0, 0.5),
            "빛나는 토마토": Ingredient("빛나는 토마토", IngredientType.VEGETABLE, 3, "빛을 발하는 토마토", "🍅", 2.5, 0.6),
            "독버섯": Ingredient("독버섯", IngredientType.VEGETABLE, 2, "독성이 있지만 요리하면 약효가", "🍄", 1.5, 0.2),
            "고대 감자": Ingredient("고대 감자", IngredientType.VEGETABLE, 3, "고대부터 자란 신비한 감자", "🥔", 2.0, 0.6),
            "마나 버섯": Ingredient("마나 버섯", IngredientType.VEGETABLE, 4, "마법력을 증진시키는 버섯", "🟦", 3.0, 0.3),
            "세계수 뿌리": Ingredient("세계수 뿌리", IngredientType.VEGETABLE, 5, "세계수의 뿌리", "🌳", 5.0, 2.0),
            "산나물": Ingredient("산나물", IngredientType.VEGETABLE, 2, "고원에서 자란 나물", "🥬", 1.2, 0.3),
            "버섯": Ingredient("버섯", IngredientType.VEGETABLE, 1, "동굴에서 자란 버섯", "🍄", 0.9, 0.2),
            "생명의 뿌리": Ingredient("생명의 뿌리", IngredientType.VEGETABLE, 5, "생명력을 크게 증진시키는 뿌리", "💚", 6.0, 1.0),
            
            # 과일류 - 확장
            "들딸기": Ingredient("들딸기", IngredientType.FRUIT, 1, "작은 들딸기", "🫐", 0.5, 0.1),
            "빨간 사과": Ingredient("빨간 사과", IngredientType.FRUIT, 1, "달콤한 빨간 사과", "🍎", 1.0, 0.3),
            "청사과": Ingredient("청사과", IngredientType.FRUIT, 1, "신맛의 청사과", "🍏", 1.0, 0.3),
            "바나나": Ingredient("바나나", IngredientType.FRUIT, 1, "달콤한 바나나", "🍌", 0.8, 0.2),
            "오렌지": Ingredient("오렌지", IngredientType.FRUIT, 1, "비타민 가득한 오렌지", "🍊", 0.9, 0.25),
            "레몬": Ingredient("레몬", IngredientType.FRUIT, 1, "새콤한 레몬", "🍋", 0.7, 0.2),
            "포도": Ingredient("포도", IngredientType.FRUIT, 1, "달콤한 포도", "🍇", 1.2, 0.4),
            "딸기": Ingredient("딸기", IngredientType.FRUIT, 1, "빨간 딸기", "🍓", 0.6, 0.15),
            "복숭아": Ingredient("복숭아", IngredientType.FRUIT, 1, "부드러운 복숭아", "🍑", 1.1, 0.3),
            "체리": Ingredient("체리", IngredientType.FRUIT, 1, "작은 체리", "🍒", 0.5, 0.1),
            "치유 베리": Ingredient("치유 베리", IngredientType.FRUIT, 3, "상처를 치유하는 신비한 베리", "🫐", 2.5, 0.2),
            "황금 포도": Ingredient("황금 포도", IngredientType.FRUIT, 4, "황금빛으로 빛나는 포도", "🍇", 3.0, 0.3),
            "시간 과일": Ingredient("시간 과일", IngredientType.FRUIT, 5, "시간을 조작하는 전설의 과일", "⏰", 5.0, 0.4),
            "바람꽃": Ingredient("바람꽃", IngredientType.FRUIT, 2, "고원의 바람을 머금은 꽃", "💐", 1.3, 0.1),
            "생명의 과실": Ingredient("생명의 과실", IngredientType.FRUIT, 5, "영원한 생명을 주는 과실", "💎", 8.0, 0.5),
            
            # 곡물류 - 확장
            "밀": Ingredient("밀", IngredientType.GRAIN, 1, "기본적인 곡물", "🌾", 1.0, 0.5),
            "쌀": Ingredient("쌀", IngredientType.GRAIN, 1, "흰 쌀", "🍚", 1.2, 0.6),
            "보리": Ingredient("보리", IngredientType.GRAIN, 1, "고소한 보리", "🌾", 1.1, 0.55),
            "옥수수": Ingredient("옥수수", IngredientType.GRAIN, 1, "달콤한 옥수수", "🌽", 1.3, 0.7),
            "귀리": Ingredient("귀리", IngredientType.GRAIN, 1, "영양가 높은 귀리", "🌾", 1.0, 0.5),
            "호밀": Ingredient("호밀", IngredientType.GRAIN, 1, "특별한 호밀", "🌾", 1.1, 0.6),
            "현미": Ingredient("현미", IngredientType.GRAIN, 2, "건강한 현미", "🍚", 1.4, 0.8),
            "고대 보리": Ingredient("고대 보리", IngredientType.GRAIN, 2, "고대의 힘이 담긴 보리", "🌾", 2.0, 0.8),
            "마법 쌀": Ingredient("마법 쌀", IngredientType.GRAIN, 3, "마법이 깃든 신비한 쌀", "✨", 3.0, 0.5),
            "황금 밀": Ingredient("황금 밀", IngredientType.GRAIN, 4, "황금빛으로 빛나는 밀", "✨", 4.0, 0.6),
            "별빛 밀": Ingredient("별빛 밀", IngredientType.GRAIN, 5, "별의 힘이 깃든 밀", "⭐", 6.0, 0.3),
            
            # 약초류 - 확장
            "풀잎": Ingredient("풀잎", IngredientType.HERB, 1, "그냥 풀잎", "🍃", 0.3, 0.05),
            "회복 허브": Ingredient("회복 허브", IngredientType.HERB, 2, "체력을 회복시키는 허브", "🌿", 1.5, 0.2),
            "마나 허브": Ingredient("마나 허브", IngredientType.HERB, 2, "마나를 회복시키는 허브", "🍃", 1.5, 0.2),
            "용기 풀": Ingredient("용기 풀", IngredientType.HERB, 3, "용기를 북돋우는 신비한 풀", "💚", 2.0, 0.1),
            "찬바람 허브": Ingredient("찬바람 허브", IngredientType.HERB, 2, "고원의 찬 바람을 담은 허브", "❄️", 1.8, 0.15),
            "강물 허브": Ingredient("강물 허브", IngredientType.HERB, 2, "강가에서 자란 특별한 허브", "💧", 1.6, 0.18),
            "민트": Ingredient("민트", IngredientType.HERB, 1, "상쾌한 민트", "🌿", 0.5, 0.1),
            "바질": Ingredient("바질", IngredientType.HERB, 1, "향긋한 바질", "🌿", 0.6, 0.1),
            "로즈마리": Ingredient("로즈마리", IngredientType.HERB, 1, "기억을 돕는 로즈마리", "🌿", 0.7, 0.1),
            "타임": Ingredient("타임", IngredientType.HERB, 1, "시간의 허브 타임", "🌿", 0.5, 0.1),
            "세이지": Ingredient("세이지", IngredientType.HERB, 2, "지혜의 허브 세이지", "🌿", 1.2, 0.15),
            "고대 약초": Ingredient("고대 약초", IngredientType.HERB, 3, "고대부터 전해내려오는 약초", "🌿", 2.5, 0.2),
            "신성한 잎": Ingredient("신성한 잎", IngredientType.HERB, 4, "신의 축복이 깃든 잎", "✨", 3.5, 0.1),
            "마법 약초": Ingredient("마법 약초", IngredientType.HERB, 4, "마법력이 응축된 약초", "🔮", 4.0, 0.15),
            "생명 약초": Ingredient("생명 약초", IngredientType.HERB, 5, "생명의 기운이 넘치는 약초", "💚", 5.0, 0.1),
            
            # 향신료 - 확장
            "소금": Ingredient("소금", IngredientType.SPICE, 1, "기본적인 조미료", "🧂", 0.5, 0.1),
            "후추": Ingredient("후추", IngredientType.SPICE, 1, "매운 후추", "⚫", 0.8, 0.05),
            "마늘": Ingredient("마늘", IngredientType.SPICE, 1, "강한 냄새의 마늘", "🧄", 1.0, 0.1),
            "생강": Ingredient("생강", IngredientType.SPICE, 1, "알싸한 생강", "🫚", 0.9, 0.1),
            "계피": Ingredient("계피", IngredientType.SPICE, 2, "달콤한 계피", "🟤", 1.2, 0.05),
            "정향": Ingredient("정향", IngredientType.SPICE, 2, "향긋한 정향", "🟤", 1.1, 0.03),
            "육두구": Ingredient("육두구", IngredientType.SPICE, 2, "특별한 향신료", "🟤", 1.3, 0.04),
            "카레 가루": Ingredient("카레 가루", IngredientType.SPICE, 2, "매운 카레 가루", "🟡", 1.5, 0.1),
            "파프리카": Ingredient("파프리카", IngredientType.SPICE, 1, "붉은 파프리카 가루", "🌶️", 0.8, 0.05),
            "고추 가루": Ingredient("고추 가루", IngredientType.SPICE, 1, "매운 고추 가루", "🌶️", 0.9, 0.06),
            "화산 소금": Ingredient("화산 소금", IngredientType.SPICE, 3, "화산에서 나온 특별한 소금", "🌋", 2.0, 0.2),
            "별빛 소금": Ingredient("별빛 소금", IngredientType.SPICE, 4, "별의 힘이 깃든 소금", "⭐", 3.0, 0.1),
            
            # 특수 재료들 추가
            "달걀": Ingredient("달걀", IngredientType.SPECIAL, 1, "신선한 달걀", "🥚", 1.0, 0.15),
            "벌꿀": Ingredient("벌꿀", IngredientType.SPECIAL, 2, "달콤한 벌꿀", "🍯", 1.5, 0.3),
            "우유": Ingredient("우유", IngredientType.LIQUID, 1, "신선한 우유", "🥛", 1.2, 0.4),
            "물": Ingredient("물", IngredientType.LIQUID, 1, "깨끗한 물", "💧", 0.8, 1.0),
            "와인": Ingredient("와인", IngredientType.LIQUID, 3, "고급 와인", "🍷", 2.0, 0.5),
            "맥주": Ingredient("맥주", IngredientType.LIQUID, 2, "시원한 맥주", "🍺", 1.8, 0.6),
            
            # 마법 재료들
            "마법 가루": Ingredient("마법 가루", IngredientType.SPECIAL, 3, "신비한 마법 가루", "✨", 2.5, 0.05),
            "용의 비늘": Ingredient("용의 비늘", IngredientType.SPECIAL, 5, "용의 강력한 비늘", "🐉", 5.0, 0.2),
            "정령의 눈물": Ingredient("정령의 눈물", IngredientType.LIQUID, 4, "정령이 흘린 눈물", "💧", 3.5, 0.1),
            "태양의 조각": Ingredient("태양의 조각", IngredientType.SPECIAL, 5, "태양의 힘이 응축된 조각", "☀️", 4.0, 0.1),
            "불꽃 향신료": Ingredient("불꽃 향신료", IngredientType.SPICE, 4, "뜨거운 맛의 향신료", "🔥", 3.0, 0.05),
            "별가루": Ingredient("별가루", IngredientType.SPICE, 5, "별에서 떨어진 신비한 가루", "⭐", 5.0, 0.02),
            
            # 액체류
            "물": Ingredient("물", IngredientType.LIQUID, 1, "깨끗한 물", "💧", 0.5, 1.0),
            "우유": Ingredient("우유", IngredientType.LIQUID, 1, "신선한 우유", "🥛", 1.0, 1.2),
            "꿀": Ingredient("꿀", IngredientType.LIQUID, 2, "달콤한 꿀", "🍯", 1.5, 0.5),
            "달빛 이슬": Ingredient("달빛 이슬", IngredientType.LIQUID, 3, "달빛에 맺힌 이슬", "🌙", 2.5, 0.3),
            "정령의 눈물": Ingredient("정령의 눈물", IngredientType.LIQUID, 4, "정령이 흘린 눈물", "💎", 4.0, 0.2),
            "용의 피": Ingredient("용의 피", IngredientType.LIQUID, 5, "드래곤의 붉은 피", "🩸", 5.0, 0.5),
            "하늘 꿀": Ingredient("하늘 꿀", IngredientType.LIQUID, 3, "고원에서만 나는 특별한 꿀", "🌤️", 2.8, 0.4),
            
            # 특수재료
            "철광석": Ingredient("철광석", IngredientType.SPECIAL, 2, "단단한 철광석", "⛏️", 1.0, 2.0),
            "크리스탈": Ingredient("크리스탈", IngredientType.SPECIAL, 3, "마력이 깃든 크리스탈", "💎", 2.0, 0.3),
            "요정의 가루": Ingredient("요정의 가루", IngredientType.SPECIAL, 5, "요정들이 남긴 마법 가루", "✨", 4.0, 0.1),
            "고대 룬": Ingredient("고대 룬", IngredientType.SPECIAL, 5, "고대 마법이 새겨진 룬", "🔮", 5.0, 0.5),
            "악마의 뿔": Ingredient("악마의 뿔", IngredientType.SPECIAL, 4, "악마의 검은 뿔", "😈", 3.5, 0.8),
            "어둠의 정수": Ingredient("어둠의 정수", IngredientType.SPECIAL, 4, "어둠의 힘이 응축된 정수", "🌑", 3.0, 0.3),
            "수정": Ingredient("수정", IngredientType.SPECIAL, 2, "맑고 투명한 수정", "💎", 1.8, 0.4),
            
            # 새로 추가된 식재료들
            # 해산물
            "해산물": Ingredient("해산물", IngredientType.MEAT, 2, "신선한 바다의 선물", "🦐", 1.8, 0.8),
            "바다 게": Ingredient("바다 게", IngredientType.MEAT, 3, "달콤한 바다 게", "🦀", 2.2, 1.2),
            "바다 물고기": Ingredient("바다 물고기", IngredientType.MEAT, 2, "은빛 바다 물고기", "🐟", 1.6, 0.9),
            "신비한 조개": Ingredient("신비한 조개", IngredientType.MEAT, 4, "마법의 힘이 깃든 조개", "🐚", 3.0, 0.6),
            
            # 견과류 (새로운 타입)
            "견과류": Ingredient("견과류", IngredientType.FRUIT, 2, "영양가 높은 견과", "🥜", 1.3, 0.3),
            "도토리": Ingredient("도토리", IngredientType.FRUIT, 1, "숲의 도토리", "🌰", 0.8, 0.2),
            "호두": Ingredient("호두", IngredientType.FRUIT, 2, "고소한 호두", "🌰", 1.5, 0.25),
            "황금 견과": Ingredient("황금 견과", IngredientType.FRUIT, 4, "황금빛 견과", "🥇", 3.5, 0.15),
            
            # 독성 식물
            "독성식물": Ingredient("독성식물", IngredientType.HERB, 3, "위험하지만 강력한 독성 식물", "☠️", 2.5, 0.1),
            "독버섯": Ingredient("독버섯", IngredientType.HERB, 2, "치명적인 독버섯", "🍄", 1.8, 0.2),
            "가시덤불": Ingredient("가시덤불", IngredientType.HERB, 3, "날카로운 가시가 돋은 덤불", "🌵", 2.0, 0.15),
            
            # 마법 재료
            "마법재료": Ingredient("마법재료", IngredientType.SPECIAL, 3, "마법 실험용 재료", "🔬", 2.8, 0.3),
            "마법 돌": Ingredient("마법 돌", IngredientType.SPECIAL, 3, "마법이 깃든 신비한 돌", "🪨", 2.5, 0.8),
            "마법 나뭇잎": Ingredient("마법 나뭇잎", IngredientType.HERB, 3, "마법의 힘이 담긴 나뭇잎", "🍀", 2.2, 0.05),
            "신비한 꽃": Ingredient("신비한 꽃", IngredientType.HERB, 4, "신비로운 힘의 꽃", "🌸", 3.2, 0.08),
            
            # 알코올
            "알코올": Ingredient("알코올", IngredientType.LIQUID, 2, "발효된 알코올", "🍺", 1.5, 0.8),
            "엘프 와인": Ingredient("엘프 와인", IngredientType.LIQUID, 4, "엘프들이 만든 고급 와인", "🍷", 3.8, 0.7),
            "드워프 맥주": Ingredient("드워프 맥주", IngredientType.LIQUID, 3, "드워프들의 진한 맥주", "🍺", 2.5, 1.0),
            
            # 희귀 채소
            "황금 당근": Ingredient("황금 당근", IngredientType.VEGETABLE, 3, "황금빛으로 빛나는 당근", "🥕", 2.8, 0.3),
            "마법 양파": Ingredient("마법 양파", IngredientType.VEGETABLE, 3, "마법의 힘이 깃든 양파", "🧅", 2.5, 0.25),
            "고대 무": Ingredient("고대 무", IngredientType.VEGETABLE, 4, "고대부터 자란 거대한 무", "🥢", 3.5, 0.8),
            "별빛 셀러리": Ingredient("별빛 셀러리", IngredientType.VEGETABLE, 4, "별빛을 받아 자란 셀러리", "⭐", 3.0, 0.2),
            
            # 희귀 곡물
            "천상의 밀": Ingredient("천상의 밀", IngredientType.GRAIN, 4, "하늘에서 내린 신성한 밀", "☁️", 3.5, 0.4),
            "용의 보리": Ingredient("용의 보리", IngredientType.GRAIN, 5, "용의 숨결을 받은 보리", "🐲", 4.5, 0.35),
            "흑마법 귀리": Ingredient("흑마법 귀리", IngredientType.GRAIN, 4, "어둠의 힘이 깃든 귀리", "🌑", 3.8, 0.3),
            
            # 희귀 과일
            "용의 열매": Ingredient("용의 열매", IngredientType.FRUIT, 5, "전설의 용이 지키던 열매", "🐉", 5.0, 0.5),
            "시간의 열매": Ingredient("시간의 열매", IngredientType.FRUIT, 5, "시간을 조작하는 신비한 열매", "⏰", 4.8, 0.3),
            "생명의 열매": Ingredient("생명의 열매", IngredientType.FRUIT, 4, "생명력을 회복하는 열매", "💚", 4.0, 0.4),
            "지혜의 열매": Ingredient("지혜의 열매", IngredientType.FRUIT, 4, "지혜를 증진하는 열매", "🧠", 3.8, 0.35),
        }
    
    def _init_recipes(self):
        """레시피 데이터 초기화 (BRV, 상처, 최대 HP 시스템 연동)"""
        self.all_recipes = {
            # 기본 요리들 - 돈스타브 스타일 제약 조건 추가
            "구운 고기": Recipe(
                name="구운 고기",
                ingredients={"고기류": 1.0, "향신료": 0.5},
                effects={"hp_recovery": 38, "attack": 8},
                duration_steps=250,
                description="간단히 구운 고기. 체력 회복과 공격력 증가.",
                icon="🍖",
                priority=1,
                difficulty=1,
                weight=0.4,
                forbidden_ingredients=["채소류"],  # 채소가 들어가면 안됨 (고기 전용)
                max_ingredients={"고기류": 2.0},  # 고기는 최대 2.0까지만
                cooking_method="굽기"
            ),
            
            "야채 수프": Recipe(
                name="야채 수프",
                ingredients={"채소류": 2.0, "액체류": 1.0},
                effects={"mp_recovery": 13, "defense": 5},
                duration_steps=200,
                description="영양 가득한 야채 수프. MP 회복과 방어력 증가.",
                icon="🍲",
                priority=1,
                difficulty=1,
                weight=0.6,
                forbidden_ingredients=["고기류", "해산물"],  # 채식 수프 - 동물성 식품 금지
                required_specific=["액체류"],  # 액체는 반드시 필요
                max_ingredients={"채소류": 4.0},  # 채소 최대 4.0까지
                cooking_method="끓이기"
            ),
            
            "과일 샐러드": Recipe(
                name="과일 샐러드",
                ingredients={"과일류": 2.0},
                effects={"hp_recovery": 50, "speed": 8},
                duration_steps=180,
                description="신선한 과일로 만든 샐러드. 체력 회복과 속도 증가.",
                icon="🥗",
                priority=1,
                difficulty=1,
                weight=0.3,
                forbidden_ingredients=["고기류", "해산물", "곡물류"],  # 순수 과일 샐러드
                max_ingredients={"과일류": 3.0},  # 과일 최대 3.0까지
                cooking_method="자르기"
            ),
            
            # 최대 HP 증가 요리들 (대폭 증가량)
            "생명력 강화 스튜": Recipe(
                name="생명력 강화 스튜",
                ingredients={"고기류": 3.0, "약초류": 2.0, "액체류": 1.5, "특수재료": 1.0},
                effects={"max_hp_increase": 150, "hp_recovery": 100, "constitution": 25},  # HP 80->100 (+25%)
                duration_steps=500,
                description="생명력을 대폭 강화하는 신비한 스튜. 최대 HP 대폭 증가!",
                icon="❤️",
                priority=8,
                difficulty=4,
                weight=1.2,
                special_effects=["max_hp_boost", "constitution_boost"]
            ),
            
            "용사의 만찬": Recipe(
                name="용사의 만찬",
                ingredients={"고기류": 8.0, "곡물류": 3.0, "과일류": 2.0, "특수재료": 3.0},
                effects={"max_hp_increase": 300, "max_mp_increase": 100, "all_stats": 40},
                duration_steps=800,
                description="용사만이 먹을 수 있는 전설의 만찬. 모든 능력치 대폭 상승!",
                icon="🍽️",
                priority=10,
                difficulty=5,
                weight=2.5,
                special_effects=["legendary_feast", "hero_blessing"]
            ),
            
            # 상처 시스템 연동 요리들
            "상처 치유 물약": Recipe(
                name="상처 치유 물약",
                ingredients={"약초류": 3.0, "과일류": 2.0, "액체류": 2.0},
                effects={"wound_healing": 50, "hp_recovery": 75},  # HP 60->75 (+25%)
                duration_steps=300,
                description="깊은 상처를 치유하는 특별한 물약. 상처 50% 치유!",
                icon="🧪",
                priority=7,
                difficulty=3,
                weight=0.5,
                special_effects=["wound_healing", "deep_recovery"]
            ),
            
            "재생의 엘릭서": Recipe(
                name="재생의 엘릭서",
                ingredients={"약초류": 5.0, "특수재료": 3.0, "액체류": 4.0},
                effects={"wound_healing": 100, "hp_regen_per_step": 2},
                duration_steps=1000,
                description="모든 상처를 완전히 치유하고 지속 회복하는 엘릭서. 걸음당 2HP 회복.",
                icon="💊",
                priority=9,
                difficulty=5,
                weight=0.8,
                special_effects=["complete_wound_healing", "regeneration", "hp_regen_per_step"]
            ),
            
            # BRV 시스템 연동 요리들
            "용기의 수프": Recipe(
                name="용기의 수프",
                ingredients={"고기류": 2.0, "약초류": 2.0, "향신료": 1.5},
                effects={"brv_gain_bonus": 30, "attack": 20, "courage": 15},
                duration_steps=400,
                description="용기를 북돋우는 수프. BRV 획득량 30% 증가!",
                icon="🍜",
                priority=6,
                difficulty=3,
                weight=0.7,
                special_effects=["brv_boost", "courage_boost"]
            ),
            
            "전사의 영양식": Recipe(
                name="전사의 영양식",
                ingredients={"고기류": 4.0, "곡물류": 2.0, "향신료": 2.0},
                effects={"brv_damage_bonus": 25, "critical_rate": 20, "attack": 30},
                duration_steps=350,
                description="전사의 BRV 공격력을 강화하는 영양식. BRV 데미지 25% 증가!",
                icon="⚔️",
                priority=7,
                difficulty=4,
                weight=1.0,
                special_effects=["brv_power", "warrior_strength"]
            ),
            
            "지혜의 차": Recipe(
                name="지혜의 차",
                ingredients={"약초류": 3.0, "액체류": 2.0, "특수재료": 1.0},
                effects={"brv_defense_bonus": 20, "mp_recovery": 20, "wisdom": 25},  # MP 40->20 (-50%)
                duration_steps=300,
                description="정신력을 강화하는 차. BRV 방어력 20% 증가!",
                icon="🍵",
                priority=5,
                difficulty=2,
                weight=0.4,
                special_effects=["brv_shield", "mental_clarity"]
            ),
            
            # 고급 요리들
            "드래곤 바베큐": Recipe(
                name="드래곤 바베큐",
                ingredients={"고기류": 8.0, "향신료": 5.0, "특수재료": 2.0},
                effects={"all_stats": 50, "fire_resistance": 80, "attack": 60, "max_hp_increase": 200},
                duration_steps=800,
                description="전설적인 드래곤 고기로 만든 바베큐. 모든 능력치 대폭 상승.",
                icon="🐲",
                priority=10,
                difficulty=5,
                weight=2.0,
                special_effects=["fire_immunity", "intimidation", "dragon_power"]
            ),
            
            "시간 조작 스튜": Recipe(
                name="시간 조작 스튜",
                ingredients={"과일류": 5.0, "채소류": 3.0, "특수재료": 6.0, "액체류": 2.5},
                effects={"speed": 80, "evasion": 50, "brv_gain_bonus": 50},
                duration_steps=500,
                description="시간을 조작하는 신비한 스튜. 엄청난 속도와 회피율 획득.",
                icon="⏰",
                priority=9,
                difficulty=5,
                weight=1.5,
                special_effects=["double_turn", "time_slow", "temporal_boost"]
            ),
            
            # 실패작
            "곤죽": Recipe(
                name="곤죽",
                ingredients={},
                effects={"hp_recovery": -20, "all_stats": -10},
                duration_steps=50,
                description="요리에 실패해서 만들어진 끔찍한 곤죽.",
                icon="🤢",
                priority=0,
                difficulty=0,
                weight=0.5,
                special_effects=["nausea"]
            ),
            
            # 추가된 새로운 요리들
            "원기회복 수프": Recipe(
                name="원기회복 수프",
                ingredients={"채소류": 2.0, "약초류": 2.0, "액체류": 3.0},
                effects={"hp_regen_per_step": 1, "brv_gain_bonus": 10},
                duration_steps=400,
                description="체력과 용기를 지속적으로 회복해주는 특제 수프. 걸음당 1HP 회복.",
                icon="🍲",
                priority=5,
                difficulty=3,
                weight=1.2,
                special_effects=["regeneration", "hp_regen_per_step"]
            ),
            
            "바다의 보물찜": Recipe(
                name="바다의 보물찜",
                ingredients={"해산물": 4.0, "채소류": 2.0, "향신료": 2.0},
                effects={"defense": 40, "water_resistance": 60, "mp_regen_per_step": 2},
                duration_steps=600,
                description="바다의 신선한 해산물로 만든 찜. 방어력과 수중 활동에 특화.",
                icon="🦐",
                priority=6,
                difficulty=3,
                weight=1.5,
                special_effects=["aquatic_blessing", "mp_regen_per_step"]
            ),
            
            "숲의 과실 샐러드": Recipe(
                name="숲의 과실 샐러드",
                ingredients={"과일류": 3.0, "채소류": 2.0, "견과류": 1.5},
                effects={"speed": 30, "luck": 25, "natural_recovery": 15},
                duration_steps=450,
                description="자연의 기운이 담긴 신선한 과실 샐러드. 민첩성과 운을 증가.",
                icon="🥗",
                priority=4,
                difficulty=2,
                weight=0.8,
                special_effects=["nature_blessing", "luck_boost"]
            ),
            
            "암흑의 독 스튜": Recipe(
                name="암흑의 독 스튜",
                ingredients={"독성식물": 3.0, "고기류": 2.0, "특수재료": 2.0},
                effects={"poison_resistance": 90, "dark_damage": 50, "stealth": 40},
                duration_steps=500,
                description="독을 다루는 자들의 비밀 요리. 독 저항력과 암흑 공격력 상승.",
                icon="☠️",
                priority=7,
                difficulty=4,
                weight=1.0,
                special_effects=["poison_immunity", "shadow_strike"]
            ),
            
            "천상의 꿀케이크": Recipe(
                name="천상의 꿀케이크",
                ingredients={"곡물류": 3.0, "꿀": 4.0, "과일류": 2.0},
                effects={"max_hp_increase": 150, "divine_protection": 30, "charisma": 50},
                duration_steps=800,
                description="천상의 꿀로 만든 신성한 케이크. 최대 체력과 신성한 가호를 부여.",
                icon="🍰",
                priority=8,
                difficulty=4,
                weight=1.2,
                special_effects=["divine_blessing", "hp_boost"]
            ),
            
            "전투광의 고기구이": Recipe(
                name="전투광의 고기구이",
                ingredients={"고기류": 5.0, "향신료": 3.0, "알코올": 2.0},
                effects={"attack": 50, "berserker_rage": 40, "pain_resistance": 30},
                duration_steps=450,
                description="전투에 미친 자들이 즐기는 자극적인 고기구이. 광폭한 공격력을 부여.",
                icon="🥩",
                priority=6,
                difficulty=3,
                weight=1.8,
                special_effects=["berserker_mode", "pain_immunity"]
            ),
            
            "마법사의 비밀 스프": Recipe(
                name="마법사의 비밀 스프",
                ingredients={"약초류": 4.0, "마법재료": 3.0, "액체류": 2.0},
                effects={"magic_power": 60, "mp_max_increase": 100, "spell_resistance": 40},
                duration_steps=600,
                description="고대 마법사들의 비밀 레시피. 마법력과 최대 MP를 크게 증가.",
                icon="🔮",
                priority=7,
                difficulty=4,
                weight=0.9,
                special_effects=["arcane_mastery", "mp_boost"]
            ),
            
            "길잡이의 건조육": Recipe(
                name="길잡이의 건조육",
                ingredients={"고기류": 3.0, "소금": 2.0, "향신료": 1.0},
                effects={"stamina": 40, "exploration_bonus": 30, "terrain_adaptation": 25},
                duration_steps=1000,
                description="오랜 여행을 위해 만든 건조육. 스태미나와 탐험 능력을 향상.",
                icon="🥓",
                priority=5,
                difficulty=2,
                weight=0.6,
                special_effects=["explorer_endurance", "long_journey"]
            ),
            
            "신령의 과실주": Recipe(
                name="신령의 과실주",
                ingredients={"과일류": 6.0, "알코올": 3.0, "특수재료": 2.0},
                effects={"spirit_power": 50, "divine_sight": 40, "wisdom": 35},
                duration_steps=700,
                description="신령들이 즐긴다는 전설의 과실주. 영적 능력과 지혜를 크게 향상.",
                icon="🍷",
                priority=8,
                difficulty=5,
                weight=0.7,
                special_effects=["spiritual_awakening", "divine_insight"]
            ),
            
            # 전설급 요리들 - 까다로운 제약 조건
            "불멸의 엘릭서": Recipe(
                name="불멸의 엘릭서",
                ingredients={"특수재료": 8.0, "약초류": 5.0, "액체류": 3.0, "과일류": 2.0},
                effects={"hp_recovery": 625, "max_hp_increase": 300, "all_stats": 30, "immunity": 80},
                duration_steps=250,
                description="신화적 재료로 만한 불멸의 물약. 죽음을 거부하는 힘을 부여한다.",
                icon="🧪",
                priority=12,
                difficulty=6,
                weight=1.0,
                special_effects=["immortality", "status_immunity", "perfect_health"],
                forbidden_ingredients=["고기류", "해산물", "곡물류"],  # 순수한 자연재료만
                required_specific=["특수재료", "약초류", "액체류"],  # 필수 재료들
                max_ingredients={"특수재료": 10.0, "약초류": 6.0},  # 과용 금지
                cooking_method="연금술"
            ),
            
            "천사의 디저트": Recipe(
                name="천사의 디저트",
                ingredients={"특수재료": 4.0, "약초류": 2.0, "액체류": 2.0},
                effects={"mp_recovery": 150, "magic_power": 50, "divine_protection": 80},
                duration_steps=600,
                description="천상의 재료로 만든 신성한 디저트. 신의 축복이 깃들어 있다.",
                icon="👼",
                priority=11,
                difficulty=5,
                weight=0.8,
                special_effects=["divine_blessing", "purification", "holy_aura"],
                forbidden_ingredients=["고기류", "해산물", "향신료"],  # 신성함 유지
                required_specific=["특수재료"],  # 특수재료 필수
                max_ingredients={"특수재료": 5.0},  # 특수재료 제한
                cooking_method="신성한_의식"
            ),
            
            "심연의 수프": Recipe(
                name="심연의 수프",
                ingredients={"해산물": 5.0, "액체류": 3.0, "특수재료": 2.0},  # 재료 종류 기반으로 변경
                effects={"mp_recovery": 100, "magic_power": 40, "water_mastery": 70},  # mana_recovery -> mp_recovery, 200->100 (-50%)
                duration_steps=500,
                description="깊은 바다의 신비가 담긴 검은 수프. 바다의 힘을 부여한다.",
                icon="🌊",
                priority=10,
                difficulty=5,
                weight=1.5,
                special_effects=["aquatic_breathing", "tidal_force", "oceanic_power"]
            ),
            
            "별빛 푸딩": Recipe(
                name="별빛 푸딩",
                ingredients={"특수재료": 4.0, "액체류": 2.0, "과일류": 2.0},  # 재료 종류 기반으로 변경
                effects={"mp_recovery": 125, "magic_power": 35, "night_vision": True},  # mana_recovery -> mp_recovery, 250->125 (-50%)
                duration_steps=400,
                description="별의 힘으로 만든 신비한 푸딩. 밤하늘의 마법이 깃들어 있다.",
                icon="⭐",
                priority=9,
                difficulty=4,
                weight=0.7,
                special_effects=["stellar_power", "cosmic_insight", "astral_projection"]
            ),
            
            "지옥의 라면": Recipe(
                name="지옥의 라면",
                ingredients={"향신료": 4.0, "곡물류": 2.0, "고기류": 2.0, "특수재료": 1.0},  # 재료 종류 기반으로 변경
                effects={"attack": 40, "fire_resistance": 60, "berserker_mode": True},
                duration_steps=300,
                description="지옥에서 온 극한의 매운맛. 악마도 울고 갈 정도의 매운맛이다.",
                icon="🔥",
                priority=8,
                difficulty=4,
                weight=1.2,
                special_effects=["hellfire", "berserker_rage", "pain_immunity"]
            ),
            
            "바람의 파스타": Recipe(
                name="바람의 파스타",
                ingredients={"곡물류": 3.0, "약초류": 2.0, "특수재료": 2.0},  # 재료 종류 기반으로 변경
                effects={"speed": 60, "evasion": 40, "wind_mastery": 50},
                duration_steps=350,
                description="하늘의 바람을 면발에 담은 신기한 파스타. 몸이 가벼워진다.",
                icon="💨",
                priority=7,
                difficulty=4,
                weight=0.9,
                special_effects=["flight", "wind_walk", "air_mastery"]
            ),
            
            "시공간 오믈렛": Recipe(
                name="시공간 오믈렛",
                ingredients={"특수재료": 5.0, "과일류": 2.0, "액체류": 1.0, "향신료": 1.0},  # 재료 종류 기반으로 변경
                effects={"all_stats": 25, "time_control": True, "exp_bonus": 100},
                duration_steps=600,
                description="시공간을 초월한 신비한 오믈렛. 시간의 흐름을 조작할 수 있다.",
                icon="🥚",
                priority=11,
                difficulty=6,
                weight=1.1,
                special_effects=["time_manipulation", "dimensional_shift", "chronos_blessing"]
            ),
            
            "용암 치즈 버거": Recipe(
                name="용암 치즈 버거",
                ingredients={"고기류": 4.0, "곡물류": 2.0, "채소류": 2.0, "향신료": 3.0},  # 재료 종류 기반으로 변경
                effects={"attack": 35, "defense": 25, "fire_resistance": 50, "hp_recovery": 188},  # HP 150->188 (+25%)
                duration_steps=400,
                description="뜨거운 용암이 흘러내리는 거대한 버거. 한 입 베어물면 입 안이 불타오른다.",
                icon="🍔",
                priority=8,
                difficulty=4,
                weight=1.8,
                special_effects=["molten_core", "lava_burst", "volcanic_power"]
            ),
            
            "정령의 샐러드": Recipe(
                name="정령의 샐러드",
                ingredients={"채소류": 4.0, "약초류": 3.0, "과일류": 2.0, "특수재료": 1.0},  # 재료 종류 기반으로 변경
                effects={"hp_regeneration": 30, "nature_affinity": 80, "poison_immunity": True},
                duration_steps=500,
                description="숲의 정령들이 축복한 신선한 샐러드. 자연의 생명력이 넘친다.",
                icon="🥗",
                priority=9,
                difficulty=4,
                weight=0.8,
                special_effects=["nature_blessing", "forest_protection", "elemental_harmony"]
            ),
            
            "바다왕 해물찜": Recipe(
                name="바다왕 해물찜",
                ingredients={"해산물": 6.0, "향신료": 3.0, "특수재료": 2.0},  # 재료 종류 기반으로 변경
                effects={"defense": 40, "mp_recovery": 100, "water_control": 70},  # mana_recovery -> mp_recovery, 200->100 (-50%)
                duration_steps=450,
                description="바다의 왕이 인정한 최고급 해물찜. 대양의 힘이 몸 안에 흐른다.",
                icon="🦑",
                priority=10,
                difficulty=5,
                weight=2.2,
                special_effects=["ocean_dominion", "tidal_mastery", "sea_king_blessing"]
            ),
            
            # 기본 요리 대폭 확장 - 쉬운 레시피들
            "달걀 후라이": Recipe(
                name="달걀 후라이",
                ingredients={"달걀": 1.0, "향신료": 0.3},
                effects={"hp_recovery": 25, "stamina": 5},  # HP 20->25 (+25%)
                duration_steps=120,
                description="간단하고 맛있는 달걀 후라이. 기본적인 체력 회복.",
                icon="🍳",
                priority=1,
                difficulty=1,
                weight=0.2
            ),
            
            "밥": Recipe(
                name="밥",
                ingredients={"곡물류": 1.0},
                effects={"hp_recovery": 19, "fullness": 30},  # HP 15->19 (+25%)
                duration_steps=100,
                description="기본적인 밥. 배고픔을 달래준다.",
                icon="🍚",
                priority=1,
                difficulty=1,
                weight=0.3
            ),
            
            "빵": Recipe(
                name="빵",
                ingredients={"곡물류": 1.5, "향신료": 0.2},
                effects={"hp_recovery": 31, "fullness": 40},
                duration_steps=150,
                description="갓 구운 빵. 포만감과 약간의 체력 회복.",
                icon="🍞",
                priority=1,
                difficulty=1,
                weight=0.4,
                forbidden_ingredients=["고기류", "해산물", "과일류"],  # 기본 빵 - 단순함 유지
                required_specific=["곡물류"],  # 곡물은 반드시 필요
                max_ingredients={"곡물류": 2.0, "향신료": 0.5},  # 재료량 제한
                cooking_method="굽기"
            ),
            
            "생선구이": Recipe(
                name="생선구이",
                ingredients={"해산물": 1.0, "향신료": 0.5},
                effects={"hp_recovery": 44, "intelligence": 5},
                duration_steps=180,
                description="신선한 생선을 구운 요리. 두뇌 활동에 도움.",
                icon="🐟",
                priority=2,
                difficulty=1,
                weight=0.5,
                forbidden_ingredients=["고기류", "액체류"],  # 순수 생선구이 - 고기나 액체 금지
                required_specific=["해산물"],  # 해산물은 반드시 필요
                max_ingredients={"해산물": 2.0},  # 해산물 최대 2.0까지
                cooking_method="굽기"
            ),
            
            "야채볶음": Recipe(
                name="야채볶음",
                ingredients={"채소류": 2.0, "향신료": 0.8},
                effects={"hp_recovery": 38, "defense": 3},
                duration_steps=160,
                description="각종 야채를 볶은 건강한 요리. 약간의 방어력 상승.",
                icon="🥬",
                priority=2,
                difficulty=1,
                weight=0.6,
                forbidden_ingredients=["고기류", "해산물", "과일류"],  # 순수 야채볶음
                required_specific=["채소류"],  # 채소는 반드시 필요
                max_ingredients={"채소류": 3.0, "향신료": 1.0},  # 재료량 제한
                cooking_method="볶기"
            ),
            
            "과일 스무디": Recipe(
                name="과일 스무디",
                ingredients={"과일류": 2.5},
                effects={"mp_recovery": 15, "speed": 5},
                duration_steps=140,
                description="신선한 과일로 만든 스무디. MP 회복과 민첩성 증가.",
                icon="🥤",
                priority=2,
                difficulty=1,
                weight=0.7,
                forbidden_ingredients=["고기류", "해산물", "향신료", "곡물류"],  # 순수 과일만
                required_specific=["과일류"],  # 과일은 반드시 필요
                max_ingredients={"과일류": 4.0},  # 과일 최대 4.0까지
                cooking_method="갈기"
            ),
            
            "오믈렛": Recipe(
                name="오믈렛",
                ingredients={"달걀": 2.0, "채소류": 1.0, "향신료": 0.5},
                effects={"hp_recovery": 50, "constitution": 8},  # HP 40->50 (+25%)
                duration_steps=200,
                description="야채가 들어간 폭신한 오믈렛. 체질 강화.",
                icon="🍳",
                priority=2,
                difficulty=2,
                weight=0.7
            ),
            
            "샌드위치": Recipe(
                name="샌드위치",
                ingredients={"곡물류": 2.0, "고기류": 1.0, "채소류": 1.0},
                effects={"hp_recovery": 63, "fullness": 60},  # HP 50->63 (+25%)
                duration_steps=220,
                description="든든한 샌드위치. 높은 포만감과 체력 회복.",
                icon="🥪",
                priority=3,
                difficulty=2,
                weight=0.8
            ),
            
            "치킨 스테이크": Recipe(
                name="치킨 스테이크",
                ingredients={"고기류": 2.5, "향신료": 1.0},
                effects={"hp_recovery": 75, "attack": 12},  # HP 60->75 (+25%)
                duration_steps=250,
                description="두툼한 치킨 스테이크. 공격력과 체력 회복.",
                icon="🍗",
                priority=3,
                difficulty=2,
                weight=1.0
            ),
            
            "해물전": Recipe(
                name="해물전",
                ingredients={"해산물": 2.0, "곡물류": 1.0, "향신료": 0.8},
                effects={"hp_recovery": 56, "mp_recovery": 10},  # HP 45->56 (+25%), MP 20->10 (-50%)
                duration_steps=190,
                description="바삭한 해물전. HP와 MP를 동시에 회복.",
                icon="🥞",
                priority=3,
                difficulty=2,
                weight=0.9
            ),
            
            "볶음밥": Recipe(
                name="볶음밥",
                ingredients={"곡물류": 2.0, "고기류": 1.0, "달걀": 1.0, "향신료": 0.5},
                effects={"hp_recovery": 69, "stamina": 20},  # HP 55->69 (+25%)
                duration_steps=210,
                description="고소한 볶음밥. 스태미나와 체력 회복.",
                icon="🍛",
                priority=3,
                difficulty=2,
                weight=1.1
            ),
            
            "미역국": Recipe(
                name="미역국",
                ingredients={"해산물": 1.5, "채소류": 1.0},
                effects={"hp_recovery": 44, "wound_healing": 10},  # HP 35->44 (+25%)
                duration_steps=170,
                description="영양가 높은 미역국. 상처 치유에 도움.",
                icon="🍜",
                priority=2,
                difficulty=1,
                weight=0.7
            ),
            
            "김치찌개": Recipe(
                name="김치찌개",
                ingredients={"채소류": 3.0, "고기류": 1.5, "향신료": 1.5},
                effects={"hp_recovery": 88, "fire_resistance": 15},  # HP 70->88 (+25%)
                duration_steps=280,
                description="매콤한 김치찌개. 화염 저항력 증가.",
                icon="🌶️",
                priority=4,
                difficulty=2,
                weight=1.3
            ),
            
            "파스타": Recipe(
                name="파스타",
                ingredients={"곡물류": 2.5, "채소류": 1.5, "향신료": 1.0},
                effects={"hp_recovery": 81, "mp_recovery": 13},  # HP 65->81 (+25%), MP 25->13 (-50%)
                duration_steps=240,
                description="이국적인 파스타. HP와 MP를 균형있게 회복.",
                icon="🍝",
                priority=3,
                difficulty=2,
                weight=1.0
            ),
            
            "카레": Recipe(
                name="카레",
                ingredients={"고기류": 2.0, "채소류": 2.0, "향신료": 2.5},
                effects={"hp_recovery": 100, "warmth": 30},  # HP 80->100 (+25%)
                duration_steps=300,
                description="따뜻한 카레. 추위를 막아주고 체력을 크게 회복.",
                icon="🍛",
                priority=4,
                difficulty=3,
                weight=1.4
            ),
            
            "라면": Recipe(
                name="라면",
                ingredients={"곡물류": 1.5, "향신료": 1.0, "달걀": 0.5},
                effects={"hp_recovery": 50, "warmth": 20},  # HP 40->50 (+25%)
                duration_steps=150,
                description="간편한 라면. 빠른 체력 회복과 몸을 따뜻하게.",
                icon="🍜",
                priority=2,
                difficulty=1,
                weight=0.6
            ),
            
            "피자": Recipe(
                name="피자",
                ingredients={"곡물류": 3.0, "고기류": 2.0, "채소류": 2.0, "향신료": 1.5},
                effects={"hp_recovery": 113, "morale": 25},  # HP 90->113 (+25%)
                duration_steps=350,
                description="맛있는 피자. 사기를 크게 올려주고 체력을 회복.",
                icon="🍕",
                priority=4,
                difficulty=3,
                weight=1.8
            ),
            
            "만두": Recipe(
                name="만두",
                ingredients={"곡물류": 2.0, "고기류": 1.5, "채소류": 1.0},
                effects={"hp_recovery": 69, "fullness": 50},  # HP 55->69 (+25%)
                duration_steps=220,
                description="속이 꽉 찬 만두. 높은 포만감과 체력 회복.",
                icon="🥟",
                priority=3,
                difficulty=2,
                weight=1.0
            ),
            
            "팬케이크": Recipe(
                name="팬케이크",
                ingredients={"곡물류": 2.0, "달걀": 1.0, "과일류": 1.0},
                effects={"hp_recovery": 56, "happiness": 20},
                duration_steps=180,
                description="달콤한 팬케이크. 기분을 좋게 하고 체력을 회복.",
                icon="🥞",
                priority=2,
                difficulty=2,
                weight=0.8,
                forbidden_ingredients=["고기류", "해산물", "향신료"],  # 달콤한 요리 - 짠맛 금지
                required_specific=["곡물류", "과일류"],  # 기본 재료 필수
                max_ingredients={"과일류": 2.0},  # 과일 적당히
                cooking_method="굽기"
            ),
            
            "된장찌개": Recipe(
                name="된장찌개",
                ingredients={"채소류": 2.5, "곡물류": 0.5, "향신료": 1.0},
                effects={"hp_recovery": 69, "warmth": 15},
                duration_steps=220,
                description="한국의 전통 찌개. 따뜻함과 포만감을 제공.",
                icon="🍲",
                priority=3,
                difficulty=2,
                weight=1.2,
                forbidden_ingredients=["과일류", "특수재료"],  # 전통 찌개 - 과일이나 이상한 재료 금지
                required_specific=["채소류", "향신료"],  # 채소와 양념 필수
                max_ingredients={"향신료": 2.0},  # 양념 과하면 안됨
                cooking_method="끓이기"
            )
        }
    
    def get_total_inventory_weight(self) -> float:
        """현재 인벤토리 총 무게 계산"""
        total_weight = 0.0
        
        # 식재료 무게
        for ingredient_name, amount in self.ingredients_inventory.items():
            if ingredient_name in self.all_ingredients:
                total_weight += self.all_ingredients[ingredient_name].weight * amount
        
        # 완성된 요리 무게
        for food_name, amount in self.cooked_food_inventory.items():
            if food_name in self.all_recipes:
                total_weight += self.all_recipes[food_name].weight * amount
        
        return total_weight
    
    def add_ingredient(self, ingredient_name: str, amount: int = 1) -> bool:
        """식재료 추가 (무게 체크 포함)"""
        if ingredient_name not in self.all_ingredients:
            return False
        
        ingredient = self.all_ingredients[ingredient_name]
        added_weight = ingredient.weight * amount
        
        # 무게 제한 체크
        max_weight = self.get_max_inventory_weight()
        if self.get_total_inventory_weight() + added_weight > max_weight:
            print(f"{RED}⚠️ 인벤토리가 너무 무거워서 {ingredient_name}을(를) 더 들 수 없습니다!{RESET}")
            print(f"현재 무게: {self.get_total_inventory_weight():.1f}kg / {max_weight:.1f}kg")
            return False
        
        if ingredient_name in self.ingredients_inventory:
            self.ingredients_inventory[ingredient_name] += amount
        else:
            self.ingredients_inventory[ingredient_name] = amount
        
        return True
    
    def can_gather_from_location(self, location_name: str) -> bool:
        """특정 채집지에서 채집할 수 있는지 확인"""
        return location_name in GATHERING_LOCATIONS
    
    def gather_ingredients_from_location(self, location_name: str) -> List[str]:
        """특정 채집지에서 식재료 채집"""
        if location_name not in GATHERING_LOCATIONS:
            return []
        
        location = GATHERING_LOCATIONS[location_name]
        gathered = []
        
        # 6-10개의 재료를 채집 시도 (대폭 증가)
        attempts = random.randint(6, 10)
        
        for _ in range(attempts):
            # 95% 확률로 무언가는 발견 (성공률 대폭 증가)
            if random.random() < 0.05:  # 5% 확률로만 실패
                continue
                
            rarity_roll = random.random()
            ingredient = None
            amount = 1  # 기본 획득량
            
            if rarity_roll < 0.6:  # 60% 확률로 일반 재료
                if location["common"]:
                    ingredient = random.choice(location["common"])
                    amount = random.randint(2, 4)  # 일반 재료는 2-4개씩
            elif rarity_roll < 0.85:  # 25% 확률로 언커먼 재료
                if location["uncommon"]:
                    ingredient = random.choice(location["uncommon"])
                    amount = random.randint(1, 3)  # 언커먼 재료는 1-3개씩
            else:  # 15% 확률로 레어 재료
                if location["rare"]:
                    ingredient = random.choice(location["rare"])
                    amount = random.randint(1, 2)  # 레어 재료는 1-2개씩
            
            if ingredient and self.add_ingredient(ingredient, amount):
                gathered.extend([ingredient] * amount)
        
        return gathered
    
    def show_gathering_results(self, gathered_ingredients: List[str], location_name: str):
        """채집 결과 표시"""
        if not gathered_ingredients:
            print(f"\n{YELLOW}😔 {location_name}에서 아무것도 찾지 못했습니다.{RESET}")
            return
        
        # 아이템별로 개수 집계
        gather_counts = {}
        for ingredient in gathered_ingredients:
            gather_counts[ingredient] = gather_counts.get(ingredient, 0) + 1
        
        print(f"\n{GREEN}🌿 {location_name} 채집 결과:{RESET}")
        total_gathered = len(gathered_ingredients)
        print(f"  총 {total_gathered}개의 식재료를 발견했습니다!")
        
        for ingredient, count in gather_counts.items():
            if ingredient in self.all_ingredients:
                rarity = self.all_ingredients[ingredient].rarity
                rarity_color = {1: WHITE, 2: GREEN, 3: BLUE, 4: MAGENTA, 5: YELLOW}.get(rarity, WHITE)
                print(f"  {rarity_color}🥕 {ingredient} x{count}{RESET}")
            else:
                print(f"  🥕 {ingredient} x{count}")
        
        if audio_manager:
            audio_manager.play_sfx(SFXType.ITEM_PICKUP)
    
    def enhanced_gather_from_location(self, location_name: str) -> bool:
        """향상된 채집 기능 (결과 표시 포함)"""
        if not self.can_gather_from_location(location_name):
            print(f"{RED}❌ '{location_name}'는 유효한 채집지가 아닙니다.{RESET}")
            return False
        
        gathered = self.gather_ingredients_from_location(location_name)
        self.show_gathering_results(gathered, location_name)
        
        return len(gathered) > 0
    
    def get_quick_cooking_menu(self) -> List[str]:
        """한 번 만든 요리들의 빠른 제작 목록"""
        available_quick_recipes = []
        
        for recipe_name in self.discovered_recipes:
            # 재료 확인 없이 제작 가능한지만 체크
            can_cook, _ = self.can_cook_with_substitutes(recipe_name)
            if can_cook:
                available_quick_recipes.append(recipe_name)
        
        return sorted(available_quick_recipes)
    
    def quick_cook_dish(self, recipe_name: str) -> Tuple[bool, str]:
        """빠른 요리 제작 (발견한 레시피만, 재료 표시 없음)"""
        if recipe_name not in self.discovered_recipes:
            return False, "아직 발견하지 못한 레시피입니다!"
        
        # 기존 cook_dish 로직 사용하되 메시지만 변경
        result, message = self.cook_dish(recipe_name)
        
        if result and "성공적으로" in message:
            return True, f"⚡ {recipe_name}을(를) 빠르게 만들었습니다!"
        
        return result, message
    
    def show_cooking_interface(self, show_ingredients: bool = False) -> str:
        """요리 인터페이스 표시 (도전 모드용)"""
        interface = []
        interface.append("🍳 야외 요리 시스템")
        interface.append("=" * 50)
        
        if show_ingredients:
            # 개발자 모드에서만 재료 표시
            interface.append("📦 보유 재료:")
            if not self.ingredients_inventory:
                interface.append("  재료가 없습니다.")
            else:
                for ingredient, amount in sorted(self.ingredients_inventory.items()):
                    interface.append(f"  • {ingredient}: {amount}개")
        else:
            # 도전 모드: 재료 개수만 표시
            total_ingredients = sum(self.ingredients_inventory.values())
            interface.append(f"📦 보유 재료: 총 {total_ingredients}개 (내용물 확인 불가)")
        
        interface.append("")
        interface.append("🍽️ 완성된 요리:")
        if not self.cooked_food_inventory:
            interface.append("  완성된 요리가 없습니다.")
        else:
            for food, amount in sorted(self.cooked_food_inventory.items()):
                interface.append(f"  • {food}: {amount}개")
        
        # 빠른 요리 메뉴
        quick_recipes = self.get_quick_cooking_menu()
        if quick_recipes:
            interface.append("")
            interface.append("⚡ 빠른 요리 (발견한 레시피):")
            for i, recipe_name in enumerate(quick_recipes[:10], 1):  # 최대 10개만
                recipe = self.all_recipes[recipe_name]
                interface.append(f"  [{i}] {recipe.icon} {recipe_name}")
        
        return "\n".join(interface)
    
    def get_enemy_specific_ingredient_drop(self, enemy_name: str, enemy_level: int) -> Optional[str]:
        """적 종류별 특정 식재료 드롭"""
        enemy_key = None
        for key in ENEMY_SPECIFIC_DROPS.keys():
            if key in enemy_name or enemy_name in key:
                enemy_key = key
                break
        
        if not enemy_key:
            return None
        
        # 85% 확률로 특정 드롭 (대폭 증가)
        if random.random() < 0.85:
            possible_drops = ENEMY_SPECIFIC_DROPS[enemy_key]
            return random.choice(possible_drops)
        
        return None
    
    def get_random_ingredient_drop(self, enemy_level: int = 1) -> Optional[str]:
        """일반 랜덤 식재료 드롭"""
        # 기본 80% 드롭률에서 시작, 레벨당 추가 5%
        drop_chance = 0.8 + (enemy_level * 0.05)
        drop_chance = min(drop_chance, 0.98)  # 최대 98%까지
        
        if random.random() > drop_chance:
            return None
        
        rarity_weights = {
            1: 50, 2: 30, 3: 15, 4: 4, 5: 1
        }
        
        # 고레벨 적일수록 희귀 재료 드롭률 증가
        if enemy_level >= 5:
            rarity_weights[3] += 15  # 증가량 증가
            rarity_weights[4] += 8
        if enemy_level >= 10:
            rarity_weights[4] += 15  # 증가량 증가
            rarity_weights[5] += 10
        
        available_ingredients = []
        for name, ingredient in self.all_ingredients.items():
            weight = rarity_weights.get(ingredient.rarity, 1)
            available_ingredients.extend([name] * weight)
        
        return random.choice(available_ingredients) if available_ingredients else None
    
    def process_enemy_defeat_drops(self, enemy_name: str, enemy_level: int = 1) -> List[str]:
        """적 처치 시 식재료 드롭 처리 (여러 개 가능)"""
        dropped_ingredients = []
        
        # 1-3개의 드롭 시도 (레벨에 따라 증가)
        max_drops = min(3 + (enemy_level // 5), 5)  # 최대 5개까지
        drop_attempts = random.randint(1, max_drops)
        
        for _ in range(drop_attempts):
            # 특정 드롭 시도 (85% 확률)
            specific_drop = self.get_enemy_specific_ingredient_drop(enemy_name, enemy_level)
            if specific_drop:
                # 특정 드롭은 1-2개씩 (높은 레벨일수록 많이)
                amount = 1 if enemy_level < 10 else random.randint(1, 2)
                if self.add_ingredient(specific_drop, amount):
                    dropped_ingredients.extend([specific_drop] * amount)
                continue
            
            # 일반 랜덤 드롭 시도 (80%+ 확률)
            random_drop = self.get_random_ingredient_drop(enemy_level)
            if random_drop:
                # 일반 드롭도 1-2개씩
                amount = 1 if enemy_level < 5 else random.randint(1, 2)
                if self.add_ingredient(random_drop, amount):
                    dropped_ingredients.extend([random_drop] * amount)
        
        return dropped_ingredients
    
    def show_ingredient_drops(self, dropped_ingredients: List[str], enemy_name: str = "적"):
        """드롭된 식재료 표시"""
        if not dropped_ingredients:
            return
        
        # 아이템별로 개수 집계
        drop_counts = {}
        for ingredient in dropped_ingredients:
            drop_counts[ingredient] = drop_counts.get(ingredient, 0) + 1
        
        print(f"\n{GREEN}💰 {enemy_name} 처치 보상:{RESET}")
        for ingredient, count in drop_counts.items():
            print(f"  🥕 {ingredient} x{count}")
        
        if audio_manager:
            audio_manager.play_sfx(SFXType.ITEM_PICKUP)
    
    def get_total_drop_rate_info(self, enemy_level: int = 1) -> str:
        """현재 드롭률 정보 표시"""
        specific_rate = 85
        random_rate = min(80 + (enemy_level * 5), 98)
        max_drops = min(3 + (enemy_level // 5), 5)
        
        return (f"드롭률 정보:\n"
                f"  특정 드롭: {specific_rate}%\n"
                f"  일반 드롭: {random_rate}%\n"
                f"  최대 동시 드롭: {max_drops}개")
    
    def can_cook_with_substitutes(self, recipe_name: str) -> Tuple[bool, Dict[str, List[Tuple[str, float]]]]:
        """레시피를 재료 대체로 요리할 수 있는지 확인"""
        if recipe_name not in self.all_recipes:
            return False, {}
        
        recipe = self.all_recipes[recipe_name]
        substitution_plan = {}
        
        for ingredient_type, needed_value in recipe.ingredients.items():
            available_ingredients = []
            for name, ingredient in self.all_ingredients.items():
                if ingredient.type.value == ingredient_type and name in self.ingredients_inventory:
                    available_count = self.ingredients_inventory[name]
                    available_ingredients.append((name, ingredient.value, available_count))
            
            if not available_ingredients:
                return False, {}
            
            available_ingredients.sort(key=lambda x: x[1], reverse=True)
            current_value = 0.0
            selected_ingredients = []
            
            for name, value, count in available_ingredients:
                if current_value >= needed_value:
                    break
                
                remaining_needed = needed_value - current_value
                use_count = min(count, int(remaining_needed / value) + (1 if remaining_needed % value > 0 else 0))
                
                if use_count > 0:
                    selected_ingredients.append((name, min(remaining_needed / value, use_count)))
                    current_value += value * min(remaining_needed / value, use_count)
            
            if current_value < needed_value:
                return False, {}
            
            substitution_plan[ingredient_type] = selected_ingredients
        
        return True, substitution_plan
    
    def validate_recipe_constraints(self, recipe: Recipe, substitution_plan: Dict) -> Tuple[bool, str]:
        """레시피 제약 조건 검증 (돈스타브 스타일)"""
        # 금지된 재료 확인
        if hasattr(recipe, 'forbidden_ingredients') and recipe.forbidden_ingredients:
            for ingredient_type, selected_ingredients in substitution_plan.items():
                if ingredient_type in recipe.forbidden_ingredients:
                    return False, f"이 요리에는 {ingredient_type}를 사용할 수 없습니다!"
        
        # 필수 재료 확인
        if hasattr(recipe, 'required_specific') and recipe.required_specific:
            for required_type in recipe.required_specific:
                if required_type not in substitution_plan:
                    return False, f"이 요리에는 {required_type}가 반드시 필요합니다!"
        
        # 최대 재료량 확인
        if hasattr(recipe, 'max_ingredients') and recipe.max_ingredients:
            for ingredient_type, selected_ingredients in substitution_plan.items():
                if ingredient_type in recipe.max_ingredients:
                    total_amount = sum(amount for _, amount in selected_ingredients)
                    max_allowed = recipe.max_ingredients[ingredient_type]
                    if total_amount > max_allowed:
                        return False, f"{ingredient_type}는 최대 {max_allowed}까지만 사용할 수 있습니다! (현재: {total_amount})"
        
        return True, "제약 조건을 모두 만족합니다."
    
    def cook_dish(self, recipe_name: str) -> Tuple[bool, str]:
        """요리 제작"""
        can_cook, substitution_plan = self.can_cook_with_substitutes(recipe_name)
        if not can_cook:
            return False, "재료가 부족합니다."
        
        recipe = self.all_recipes[recipe_name]
        
        # 돈스타브 스타일 제약 조건 검증
        constraint_valid, constraint_message = self.validate_recipe_constraints(recipe, substitution_plan)
        if not constraint_valid:
            return False, constraint_message
        
        # 완성된 요리 무게 체크
        if self.get_total_inventory_weight() + recipe.weight > 60.0:
            return False, f"완성된 요리가 너무 무거워서 인벤토리에 넣을 수 없습니다! (무게: {recipe.weight}kg)"
        
        # 요리 시작 사운드
        if audio_manager:
            audio_manager.play_sfx(SFXType.MENU_SELECT)  # 요리 시작음
        
        # 재료 소모
        for ingredient_type, selected_ingredients in substitution_plan.items():
            for ingredient_name, use_amount in selected_ingredients:
                use_count = int(use_amount) + (1 if use_amount % 1 > 0 else 0)
                self.ingredients_inventory[ingredient_name] -= use_count
                if self.ingredients_inventory[ingredient_name] <= 0:
                    del self.ingredients_inventory[ingredient_name]
        
        # 성공 확률 계산
        base_success_rate = 0.85
        level_bonus = min(self.cooking_level * 0.05, 0.4)
        difficulty_penalty = recipe.difficulty * 0.08
        success_rate = max(0.2, base_success_rate + level_bonus - difficulty_penalty)
        
        if random.random() > success_rate:
            # 실패 - 곤죽 생성
            if audio_manager:
                audio_manager.play_sfx(SFXType.MENU_CANCEL)  # 요리 실패음
            
            if "곤죽" in self.cooked_food_inventory:
                self.cooked_food_inventory["곤죽"] += 1
            else:
                self.cooked_food_inventory["곤죽"] = 1
            self._gain_cooking_exp(5)
            return True, f"요리에 실패했습니다! 곤죽이 만들어졌습니다... (성공률: {success_rate*100:.1f}%)"
        
        # 성공 - 완성된 요리를 인벤토리에 추가
        if audio_manager:
            audio_manager.play_sfx(SFXType.ITEM_GET)  # 요리 성공음
        
        if recipe_name in self.cooked_food_inventory:
            self.cooked_food_inventory[recipe_name] += 1
        else:
            self.cooked_food_inventory[recipe_name] = 1
        
        # 새로운 레시피 발견 시 영구 저장
        is_new_recipe = recipe_name not in self.discovered_recipes
        self.discovered_recipes.add(recipe_name)
        
        if is_new_recipe:
            self._save_permanent_recipes()  # 영구 저장
        
        self._gain_cooking_exp(recipe.duration_steps // 8)
        return True, f"{recipe_name}을(를) 성공적으로 만들었습니다!"
    
    def consume_food(self, food_name: str) -> Tuple[bool, str]:
        """요리 섭취 (버프 적용) - 중복 섭취 방지"""
        if food_name not in self.cooked_food_inventory or self.cooked_food_inventory[food_name] <= 0:
            return False, "해당 요리가 없습니다."
        
        # 이미 다른 요리 효과가 활성 중인지 확인
        if self.active_food_effect is not None:
            return False, f"너무 배부릅니다! '{self.active_food_effect}' 효과가 끝나야 다른 요리를 먹을 수 있습니다."
        
        recipe = self.all_recipes[food_name]
        
        # 요리 소모
        self.cooked_food_inventory[food_name] -= 1
        if self.cooked_food_inventory[food_name] <= 0:
            del self.cooked_food_inventory[food_name]
        
        # 현재 활성 요리 설정
        self.active_food_effect = food_name
        
        # 버프 적용
        self._apply_cooking_buff(recipe)
        
        return True, f"{food_name}을(를) 먹었습니다! 파티 전체에게 효과가 적용되었습니다."
    
    def _apply_cooking_buff(self, recipe: Recipe):
        """요리 버프 적용"""
        # 기존 같은 음식 버프 제거
        self.active_buffs = [buff for buff in self.active_buffs if buff.recipe_name != recipe.name]
        
        # 새 버프 추가
        new_buff = CookingBuff(
            recipe_name=recipe.name,
            effects=recipe.effects.copy(),
            remaining_steps=recipe.duration_steps,
            special_effects=recipe.special_effects.copy(),
            icon=recipe.icon
        )
        
        self.active_buffs.append(new_buff)
    
    def update_buffs_on_step(self):
        """걸음마다 버프 업데이트"""
        expired_buffs = []
        
        for buff in self.active_buffs:
            buff.remaining_steps -= 1
            
            if buff.remaining_steps <= 0:
                expired_buffs.append(buff)
        
        for expired_buff in expired_buffs:
            self.active_buffs.remove(expired_buff)
            print(f"{YELLOW}⏰ {expired_buff.recipe_name}의 효과가 만료되었습니다.{RESET}")
            
            # 현재 활성 요리 효과가 만료된 경우 초기화
            if self.active_food_effect == expired_buff.recipe_name:
                self.active_food_effect = None
                print(f"{GREEN}✅ 다시 요리를 먹을 수 있습니다!{RESET}")
    
    def get_total_effects(self) -> Dict[str, int]:
        """현재 활성화된 모든 요리 효과 합계"""
        total_effects = {}
        
        for buff in self.active_buffs:
            for effect_name, effect_value in buff.effects.items():
                if effect_name in total_effects:
                    total_effects[effect_name] += effect_value
                else:
                    total_effects[effect_name] = effect_value
        
        return total_effects
    
    def get_special_effects(self) -> List[str]:
        """현재 활성화된 모든 특수 효과 목록"""
        all_special_effects = []
        for buff in self.active_buffs:
            all_special_effects.extend(buff.special_effects)
        return list(set(all_special_effects))  # 중복 제거
    
    def _gain_cooking_exp(self, amount: int):
        """요리 경험치 획득"""
        self.cooking_experience += amount
        
        exp_needed = self.cooking_level * 100
        while self.cooking_experience >= exp_needed:
            self.cooking_experience -= exp_needed
            self.cooking_level += 1
            print(f"{GREEN}🎉 요리 레벨이 {self.cooking_level}로 올랐습니다!{RESET}")
            exp_needed = self.cooking_level * 100
    
    def get_food_status(self) -> str:
        """현재 요리 섭취 상태 반환"""
        if self.active_food_effect is None:
            return f"{GREEN}🍽️ 요리를 먹을 수 있습니다!{RESET}"
        else:
            # 현재 활성 효과의 남은 시간 찾기
            remaining_steps = 0
            for buff in self.active_buffs:
                if buff.recipe_name == self.active_food_effect:
                    remaining_steps = buff.remaining_steps
                    break
            
            return f"{RED}🤰 너무 배부릅니다! '{self.active_food_effect}' 효과가 {remaining_steps}걸음 후 끝납니다.{RESET}"
    
    def show_ingredients_inventory(self):
        """식재료 인벤토리 표시 (무게 포함)"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🥕 식재료 인벤토리{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        total_weight = self.get_total_inventory_weight()
        max_weight = self.get_max_inventory_weight()
        weight_ratio = total_weight / max_weight if max_weight > 0 else 0
        
        if weight_ratio >= 0.8:
            weight_color = RED
        elif weight_ratio >= 0.6:
            weight_color = YELLOW
        else:
            weight_color = GREEN
            
        print(f"{YELLOW}총 무게: {weight_color}{total_weight:.1f}kg / {max_weight:.1f}kg{RESET}")
        
        if not self.ingredients_inventory:
            print(f"{YELLOW}보유한 식재료가 없습니다.{RESET}")
            return
        
        for ingredient_name, amount in self.ingredients_inventory.items():
            if ingredient_name in self.all_ingredients:
                ingredient = self.all_ingredients[ingredient_name]
                rarity_color = [WHITE, GREEN, BLUE, MAGENTA, YELLOW][min(ingredient.rarity-1, 4)]
                total_weight = ingredient.weight * amount
                print(f"  {ingredient.icon} {rarity_color}{ingredient.name}{RESET} x{amount}")
                print(f"    {WHITE}{ingredient.description}{RESET}")
                print(f"    가치: {ingredient.value:.1f}, 무게: {ingredient.weight:.1f}kg개당 (총 {total_weight:.1f}kg)")
    
    def show_cooked_food_inventory(self):
        """완성된 요리 인벤토리 표시"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🍽️ 완성된 요리{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        # 현재 요리 섭취 상태 표시
        print(self.get_food_status())
        print()
        
        if not self.cooked_food_inventory:
            print(f"{YELLOW}완성된 요리가 없습니다.{RESET}")
            return
        
        for food_name, amount in self.cooked_food_inventory.items():
            if food_name in self.all_recipes:
                recipe = self.all_recipes[food_name]
                total_weight = recipe.weight * amount
                print(f"  {recipe.icon} {GREEN}{food_name}{RESET} x{amount}")
                print(f"    {WHITE}{recipe.description}{RESET}")
                print(f"    무게: {recipe.weight:.1f}kg개당 (총 {total_weight:.1f}kg)")
    
    def show_active_buffs(self):
        """활성 요리 버프 표시 (남은 걸음 수 포함)"""
        print(f"\n{CYAN}{'='*50}{RESET}")
        print(f"{WHITE}{BOLD}🍳 활성 요리 효과{RESET}")
        print(f"{CYAN}{'='*50}{RESET}")
        
        if not self.active_buffs:
            print(f"{YELLOW}활성화된 요리 효과가 없습니다.{RESET}")
            return
        
        for buff in self.active_buffs:
            remaining_color = GREEN if buff.remaining_steps > 100 else YELLOW if buff.remaining_steps > 50 else RED
            print(f"\n{GREEN}{buff.icon} {buff.recipe_name}{RESET}")
            print(f"  {remaining_color}⏰ 남은 시간: {buff.remaining_steps}걸음{RESET}")
            
            for effect, value in buff.effects.items():
                if effect.startswith("max_") and effect.endswith("_increase"):
                    print(f"  {MAGENTA}{effect}: +{value} (영구적){RESET}")
                else:
                    print(f"  {YELLOW}{effect}: +{value}{RESET}")
            
            if buff.special_effects:
                print(f"  {CYAN}특수효과: {', '.join(buff.special_effects)}{RESET}")
    
    def show_gathering_locations(self):
        """채집 가능한 장소들 표시"""
        print(f"\n{CYAN}{'='*70}{RESET}")
        print(f"{WHITE}{BOLD}🌍 채집 가능한 장소들{RESET}")
        print(f"{CYAN}{'='*70}{RESET}")
        
        print(f"\n{GREEN}✨ 개선된 채집 시스템:{RESET}")
        print(f"  • 채집 시도: 6-10회 (기존 3-5회)")
        print(f"  • 성공률: 95% (기존 85%)")
        print(f"  • 획득량: 일반 2-4개, 언커먼 1-3개, 레어 1-2개")
        
        for i, (location_name, location_data) in enumerate(GATHERING_LOCATIONS.items(), 1):
            print(f"\n{YELLOW}[{i}] {location_data['icon']} {location_name}{RESET}")
            print(f"    {WHITE}{location_data['description']}{RESET}")
            print(f"    {GREEN}일반(60%): {', '.join(location_data['common'][:3])}...{RESET}")
            print(f"    {BLUE}희귀(25%): {', '.join(location_data['uncommon'][:2])}...{RESET}")
            print(f"    {MAGENTA}전설(15%): {', '.join(location_data['rare'])}...{RESET}")
    
    def show_combat_drop_info(self):
        """전투 시 식재료 드롭 정보 표시"""
        print(f"\n{CYAN}{'='*70}{RESET}")
        print(f"{WHITE}{BOLD}⚔️ 전투 식재료 드롭 시스템{RESET}")
        print(f"{CYAN}{'='*70}{RESET}")
        
        print(f"\n{GREEN}✨ 개선된 드롭 시스템:{RESET}")
        print(f"  • 특정 몬스터 드롭: 85% (기존 60%)")
        print(f"  • 일반 랜덤 드롭: 80%+ (레벨당 +5%)")
        print(f"  • 동시 드롭 수: 1-5개 (레벨에 따라 증가)")
        print(f"  • 고레벨 적일수록 희귀 재료 확률 증가")
        
        print(f"\n{YELLOW}📊 레벨별 드롭률:{RESET}")
        for level in [1, 5, 10, 15, 20]:
            random_rate = min(80 + (level * 5), 98)
            max_drops = min(3 + (level // 5), 5)
            print(f"  Lv.{level:2d}: 일반 드롭 {random_rate:2d}%, 최대 동시 {max_drops}개")
        
        print(f"\n{BLUE}🎯 특정 몬스터 드롭 예시:{RESET}")
        sample_enemies = list(ENEMY_SPECIFIC_DROPS.keys())[:8]
        for enemy in sample_enemies:
            drops = ENEMY_SPECIFIC_DROPS[enemy][:3]  # 처음 3개만 표시
            print(f"  {WHITE}{enemy}:{RESET} {', '.join(drops)}...")
        
        if len(ENEMY_SPECIFIC_DROPS) > 8:
            remaining = len(ENEMY_SPECIFIC_DROPS) - 8
            print(f"  {WHITE}... 그 외 {remaining}종의 몬스터별 고유 드롭{RESET}")
        
        print(f"\n{MAGENTA}💡 팁:{RESET}")
        print(f"  • 높은 레벨의 적일수록 더 많은 식재료 드롭")
        print(f"  • 특정 몬스터는 해당 몬스터만의 특별한 식재료 드롭")
        print(f"  • 전설급 몬스터는 최고급 식재료 확정 드롭")

# 전역 인스턴스
cooking_system = CookingSystem()

def get_cooking_system():
    """요리 시스템 인스턴스 반환"""
    return cooking_system

def show_recipe_collection():
    """해금된 레시피 컬렉션 확인 - 커서 방식"""
    try:
        from .cursor_menu_system import create_simple_menu, MenuItem
        
        print("\n" + "="*80)
        print("🍳 레시피 컬렉션 - 발견한 레시피들")
        print("="*80)
        
        if not cooking_system.discovered_recipes:
            print("\n아직 발견한 레시피가 없습니다.")
            print("요리를 시도해보세요!")
            from .input_utils import KeyboardInput
            KeyboardInput().wait_for_key("아무 키나 눌러 계속...")
            return
        
        # 발견한 레시피들을 정리
        options = []
        descriptions = []
        
        for recipe_name in sorted(cooking_system.discovered_recipes):
            if recipe_name in cooking_system.recipes:
                recipe = cooking_system.recipes[recipe_name]
                
                # 재료 정보
                ingredients = ", ".join([f"{ingredient}({count}개)" 
                                       for ingredient, count in recipe.ingredients.items()])
                
                # 효과 정보
                effects = []
                for effect in recipe.buffs:
                    effects.append(f"{effect.stat_name} +{effect.value}")
                effects_str = ", ".join(effects) if effects else "효과 없음"
                
                # 등급 아이콘
                grade_icon = {
                    "기본": "⭐",
                    "고급": "⭐⭐", 
                    "희귀": "⭐⭐⭐",
                    "전설": "⭐⭐⭐⭐"
                }.get(recipe.grade, "⭐")
                
                option_text = f"{grade_icon} {recipe_name}"
                desc = f"재료: {ingredients} | 효과: {effects_str} | 지속: {recipe.duration_steps}턴"
                
                options.append(option_text)
                descriptions.append(desc)
        
        menu = create_simple_menu("레시피 컬렉션", options, descriptions)
        menu.run()
        
    except ImportError:
        # 폴백: 기존 텍스트 방식
        _show_recipe_collection_fallback()

def _show_recipe_collection_fallback():
    """레시피 컬렉션 폴백 (기존 방식)"""
    print("\n" + "="*60)
    print("🍳 레시피 컬렉션 - 발견한 레시피들")
    print("="*60)
    
    if not cooking_system.discovered_recipes:
        print("\n아직 발견한 레시피가 없습니다.")
        print("요리를 시도해보세요!")
        input("\n아무 키나 눌러 계속...")
        return
    
    for i, recipe_name in enumerate(sorted(cooking_system.discovered_recipes), 1):
        if recipe_name in cooking_system.recipes:
            recipe = cooking_system.recipes[recipe_name]
            
            # 재료 정보
            ingredients = ", ".join([f"{ingredient}({count}개)" 
                                   for ingredient, count in recipe.ingredients.items()])
            
            # 효과 정보  
            effects = []
            for effect in recipe.buffs:
                effects.append(f"{effect.stat_name} +{effect.value}")
            effects_str = ", ".join(effects) if effects else "효과 없음"
            
            # 등급 아이콘
            grade_icon = {
                "기본": "⭐",
                "고급": "⭐⭐", 
                "희귀": "⭐⭐⭐",
                "전설": "⭐⭐⭐⭐"
            }.get(recipe.grade, "⭐")
            
            print(f"\n{i:2}. {grade_icon} {recipe_name}")
            print(f"     재료: {ingredients}")
            print(f"     효과: {effects_str}")
            print(f"     지속: {recipe.duration_steps}턴")
    
    print(f"\n총 {len(cooking_system.discovered_recipes)}개의 레시피를 발견했습니다!")
    input("\n아무 키나 눌러 계속...")
