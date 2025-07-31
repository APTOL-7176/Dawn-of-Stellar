"""
요리 시스템 - 식재료 수집 및 요리 제작
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

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
    weight: float = 0.5  # 무게 (kg)

@dataclass
class Recipe:
    """요리 레시피 클래스"""
    name: str
    ingredients: Dict[str, float]  # 재료 타입: 필요 가치 (예: "고기류": 2.0)
    effects: Dict[str, int]  # 효과명: 효과값
    duration_steps: int  # 효과 지속 걸음 수
    description: str
    icon: str = "🍳"
    special_effects: List[str] = None  # 특수 효과들
    priority: int = 1  # 우선도 (높을수록 우선 제작)
    difficulty: int = 1  # 제작 난이도 (실패 확률에 영향)
    weight: float = 1  # 완성된 요리의 무게 (kg)

@dataclass
class CookingBuff:
    """요리 버프 클래스"""
    recipe_name: str
    effects: Dict[str, int]
    remaining_steps: int
    special_effects: List[str]
    icon: str

class CookingSystem:
    """요리 시스템 메인 클래스"""
    
    def __init__(self):
        self.ingredients_inventory = {}  # 보유 식재료
        self.active_buffs = []  # 활성 요리 버프들
        self.discovered_recipes = set()  # 발견한 레시피들
        self.cooking_experience = 0  # 요리 경험치
        self.cooking_level = 1  # 요리 레벨
        
        self._init_ingredients()
        self._init_recipes()
    
    def _init_ingredients(self):
        """식재료 데이터 초기화"""
        self.all_ingredients = {
            # 고기류 - 작은 것부터 큰 것까지
            "작은 고기": Ingredient("작은 고기", IngredientType.MEAT, 1, "작은 동물의 고기", "🥩", 0.5),
            "토끼 고기": Ingredient("토끼 고기", IngredientType.MEAT, 1, "부드러운 토끼 고기", "🐰", 0.8),
            "닭고기": Ingredient("닭고기", IngredientType.MEAT, 1, "담백한 닭고기", "🐔", 1.0),
            "멧돼지 고기": Ingredient("멧돼지 고기", IngredientType.MEAT, 2, "질긴 야생 멧돼지 고기", "🐗", 1.5),
            "늑대 고기": Ingredient("늑대 고기", IngredientType.MEAT, 3, "야성적인 맛의 늑대 고기", "🐺", 2.0),
            "곰 고기": Ingredient("곰 고기", IngredientType.MEAT, 3, "거대한 곰의 고기", "🐻", 3.0),
            "거대 거미 다리": Ingredient("거대 거미 다리", IngredientType.MEAT, 3, "거대한 거미의 다리", "🕷️", 4.0),
            "미노타우르스 고기": Ingredient("미노타우르스 고기", IngredientType.MEAT, 4, "전설적인 미노타우르스의 고기", "🐂", 5.0),
            "드래곤 고기": Ingredient("드래곤 고기", IngredientType.MEAT, 5, "전설적인 드래곤의 고기", "🐉", 8.0),
            "바다뱀 고기": Ingredient("바다뱀 고기", IngredientType.MEAT, 4, "바다 깊은 곳의 뱀 고기", "�", 3.5),
            "그리폰 날개": Ingredient("그리폰 날개", IngredientType.MEAT, 5, "하늘을 나는 그리폰의 날개", "🦅", 6.0),
            
            # 채소류
            "잡초": Ingredient("잡초", IngredientType.VEGETABLE, 1, "그냥 잡초", "🌱", 0.3),
            "야생 당근": Ingredient("야생 당근", IngredientType.VEGETABLE, 1, "숲에서 자란 당근", "🥕", 0.8),
            "양파": Ingredient("양파", IngredientType.VEGETABLE, 1, "매운 양파", "🧅", 0.7),
            "감자": Ingredient("감자", IngredientType.VEGETABLE, 1, "평범한 감자", "🥔", 1.0),
            "양배추": Ingredient("양배추", IngredientType.VEGETABLE, 1, "신선한 양배추", "🥬", 1.2),
            "독버섯": Ingredient("독버섯", IngredientType.VEGETABLE, 2, "독성이 있지만 요리하면 약효가", "🍄", 1.5),
            "고대 감자": Ingredient("고대 감자", IngredientType.VEGETABLE, 3, "고대부터 자란 신비한 감자", "🥔", 2.0),
            "얼음 양배추": Ingredient("얼음 양배추", IngredientType.VEGETABLE, 3, "차가운 기운이 도는 양배추", "🧊", 2.5),
            "마나 버섯": Ingredient("마나 버섯", IngredientType.VEGETABLE, 4, "마법력을 증진시키는 버섯", "🟦", 3.0),
            "황금 옥수수": Ingredient("황금 옥수수", IngredientType.VEGETABLE, 4, "황금빛으로 빛나는 옥수수", "🌽", 3.5),
            "세계수 뿌리": Ingredient("세계수 뿌리", IngredientType.VEGETABLE, 5, "세계수의 뿌리", "🌳", 5.0),
            
            # 과일류
            "들딸기": Ingredient("들딸기", IngredientType.FRUIT, 1, "작은 들딸기", "🫐", 0.5),
            "빨간 사과": Ingredient("빨간 사과", IngredientType.FRUIT, 1, "달콤한 빨간 사과", "🍎", 1.0),
            "바나나": Ingredient("바나나", IngredientType.FRUIT, 1, "달콤한 바나나", "🍌", 0.8),
            "오렌지": Ingredient("오렌지", IngredientType.FRUIT, 1, "상큼한 오렌지", "🍊", 1.2),
            "수박": Ingredient("수박", IngredientType.FRUIT, 2, "시원한 수박", "🍉", 2.0),
            "치유 베리": Ingredient("치유 베리", IngredientType.FRUIT, 3, "상처를 치유하는 신비한 베리", "🫐", 2.5),
            "황금 포도": Ingredient("황금 포도", IngredientType.FRUIT, 4, "황금빛으로 빛나는 포도", "🍇", 3.0),
            "불사조 열매": Ingredient("불사조 열매", IngredientType.FRUIT, 5, "불사조가 지키던 열매", "🔥", 4.0),
            "시간 과일": Ingredient("시간 과일", IngredientType.FRUIT, 5, "시간을 조작하는 전설의 과일", "⏰", 5.0),
            "생명의 과실": Ingredient("생명의 과실", IngredientType.FRUIT, 5, "생명력이 넘치는 과실", "💚", 6.0),
            
            # 곡물류
            "잡곡": Ingredient("잡곡", IngredientType.GRAIN, 1, "잡다한 곡물", "🌾", 0.5),
            "밀": Ingredient("밀", IngredientType.GRAIN, 1, "기본적인 곡물", "🌾", 1.0),
            "보리": Ingredient("보리", IngredientType.GRAIN, 1, "고소한 보리", "🌾", 0.8),
            "쌀": Ingredient("쌀", IngredientType.GRAIN, 1, "흰 쌀", "🍚", 1.2),
            "현미": Ingredient("현미", IngredientType.GRAIN, 2, "영양가 높은 현미", "🌾", 1.5),
            "고대 보리": Ingredient("고대 보리", IngredientType.GRAIN, 2, "고대의 힘이 담긴 보리", "🌾", 2.0),
            "마법 쌀": Ingredient("마법 쌀", IngredientType.GRAIN, 3, "마법이 깃든 신비한 쌀", "✨", 3.0),
            "신성한 밀": Ingredient("신성한 밀", IngredientType.GRAIN, 4, "신들이 축복한 밀", "⭐", 4.0),
            "영원의 곡물": Ingredient("영원의 곡물", IngredientType.GRAIN, 5, "영원불멸의 곡물", "♾️", 5.0),
            
            # 약초류
            "풀잎": Ingredient("풀잎", IngredientType.HERB, 1, "그냥 풀잎", "🍃", 0.3),
            "민들레": Ingredient("민들레", IngredientType.HERB, 1, "흔한 민들레", "🌼", 0.5),
            "회복 허브": Ingredient("회복 허브", IngredientType.HERB, 2, "체력을 회복시키는 허브", "🌿", 1.5),
            "마나 허브": Ingredient("마나 허브", IngredientType.HERB, 2, "마나를 회복시키는 허브", "🍃", 1.5),
            "용기 풀": Ingredient("용기 풀", IngredientType.HERB, 3, "용기를 북돋우는 신비한 풀", "💚", 2.0),
            "신속 잎": Ingredient("신속 잎", IngredientType.HERB, 3, "몸을 빠르게 만드는 잎", "🍃", 2.0),
            "지혜의 이끼": Ingredient("지혜의 이끼", IngredientType.HERB, 4, "지혜를 주는 고대 이끼", "🧠", 3.0),
            "만병통치 약초": Ingredient("만병통치 약초", IngredientType.HERB, 5, "모든 병을 치료하는 전설의 약초", "🌟", 5.0),
            
            # 향신료
            "소금": Ingredient("소금", IngredientType.SPICE, 1, "기본적인 조미료", "🧂", 0.5),
            "후추": Ingredient("후추", IngredientType.SPICE, 1, "매운 후추", "⚫", 0.8),
            "마늘": Ingredient("마늘", IngredientType.SPICE, 1, "강한 냄새의 마늘", "🧄", 1.0),
            "생강": Ingredient("생강", IngredientType.SPICE, 2, "알싸한 생강", "🫚", 1.2),
            "계피": Ingredient("계피", IngredientType.SPICE, 2, "달콤한 계피", "🪵", 1.5),
            "불꽃 향신료": Ingredient("불꽃 향신료", IngredientType.SPICE, 4, "뜨거운 맛의 향신료", "🔥", 3.0),
            "얼음 향신료": Ingredient("얼음 향신료", IngredientType.SPICE, 4, "차가운 맛의 향신료", "❄️", 3.0),
            "별가루": Ingredient("별가루", IngredientType.SPICE, 5, "별에서 떨어진 신비한 가루", "⭐", 5.0),
            "신의 향신료": Ingredient("신의 향신료", IngredientType.SPICE, 5, "신들만이 사용하는 향신료", "👑", 6.0),
            
            # 액체류
            "물": Ingredient("물", IngredientType.LIQUID, 1, "깨끗한 물", "💧", 0.5),
            "우유": Ingredient("우유", IngredientType.LIQUID, 1, "신선한 우유", "🥛", 1.0),
            "꿀": Ingredient("꿀", IngredientType.LIQUID, 2, "달콤한 꿀", "🍯", 1.5),
            "와인": Ingredient("와인", IngredientType.LIQUID, 3, "고급 와인", "🍷", 2.0),
            "달빛 이슬": Ingredient("달빛 이슬", IngredientType.LIQUID, 3, "달빛에 맺힌 이슬", "🌙", 2.5),
            "정령의 눈물": Ingredient("정령의 눈물", IngredientType.LIQUID, 4, "정령이 흘린 눈물", "💎", 4.0),
            "용의 피": Ingredient("용의 피", IngredientType.LIQUID, 5, "드래곤의 붉은 피", "🩸", 5.0),
            "생명의 물": Ingredient("생명의 물", IngredientType.LIQUID, 5, "생명력이 넘치는 성수", "✨", 6.0),
            
            # 특수재료
            "돌멩이": Ingredient("돌멩이", IngredientType.SPECIAL, 1, "그냥 돌멩이", "🪨", 0.1),
            "철광석": Ingredient("철광석", IngredientType.SPECIAL, 2, "단단한 철광석", "⛏️", 1.0),
            "크리스탈": Ingredient("크리스탈", IngredientType.SPECIAL, 3, "마력이 깃든 크리스탈", "💎", 2.0),
            "요정의 가루": Ingredient("요정의 가루", IngredientType.SPECIAL, 5, "요정들이 남긴 마법 가루", "✨", 4.0),
            "고대 룬": Ingredient("고대 룬", IngredientType.SPECIAL, 5, "고대 마법이 새겨진 룬", "🔮", 5.0),
            "시공간 조각": Ingredient("시공간 조각", IngredientType.SPECIAL, 5, "시공간이 찢어진 조각", "🌀", 6.0),
            "창조의 씨앗": Ingredient("창조의 씨앗", IngredientType.SPECIAL, 5, "모든 것을 창조할 수 있는 씨앗", "🌱", 8.0),
        }
    
    def _init_recipes(self):
        """레시피 데이터 초기화"""
        self.all_recipes = {
            # 기본 요리들 (낮은 우선도)
            "구운 고기": Recipe(
                name="구운 고기",
                ingredients={"고기류": 1.0, "향신료": 0.5},
                effects={"hp_recovery": 20, "attack": 5},
                duration_steps=80,
                description="간단히 구운 고기. 체력 회복과 공격력 증가.",
                icon="🍖",
                priority=1,
                difficulty=1
            ),
            
            "야채 수프": Recipe(
                name="야채 수프",
                ingredients={"채소류": 2.0, "액체류": 1.0},
                effects={"mp_recovery": 15, "defense": 3},
                duration_steps=60,
                description="영양 가득한 야채 수프. MP 회복과 방어력 증가.",
                icon="🍲",
                priority=1,
                difficulty=1
            ),
            
            "과일 샐러드": Recipe(
                name="과일 샐러드",
                ingredients={"과일류": 2.0},
                effects={"hp_recovery": 25, "speed": 5},
                duration_steps=50,
                description="신선한 과일로 만든 샐러드. 체력 회복과 속도 증가.",
                icon="🥗",
                priority=1,
                difficulty=1
            ),
            
            # 중급 요리들
            "멧돼지 스테이크": Recipe(
                name="멧돼지 스테이크",
                ingredients={"고기류": 2.0, "향신료": 1.5, "액체류": 0.5},
                effects={"attack": 15, "critical_rate": 8, "hp_recovery": 40},
                duration_steps=120,
                description="매콤하게 구운 스테이크. 공격력과 치명타율 증가.",
                icon="🥩",
                priority=3,
                difficulty=2
            ),
            
            "마법 죽": Recipe(
                name="마법 죽",
                ingredients={"곡물류": 2.0, "약초류": 1.0, "액체류": 1.5},
                effects={"max_mp": 25, "mp_recovery": 30, "magic_defense": 10},
                duration_steps=150,
                description="마법력을 증진시키는 죽. 최대 MP와 마법 방어력 증가.",
                icon="🍚",
                priority=3,
                difficulty=2
            ),
            
            "치유의 파이": Recipe(
                name="치유의 파이",
                ingredients={"과일류": 3.0, "곡물류": 2.0, "약초류": 1.5},
                effects={"hp_regen": 3},
                duration_steps=200,
                description="매 걸음마다 체력이 회복되는 신비한 파이.",
                icon="🥧",
                priority=4,
                difficulty=3,
                special_effects=["hp_regen_per_step"]
            ),
            
            "전사의 식사": Recipe(
                name="전사의 식사",
                ingredients={"고기류": 3.0, "곡물류": 1.0, "향신료": 1.0},
                effects={"attack": 20, "defense": 15, "max_hp": 30},
                duration_steps=180,
                description="전사를 위한 든든한 식사. 공격력, 방어력, 최대 HP 증가.",
                icon="🍽️",
                priority=5,
                difficulty=2
            ),
            
            # 고급 요리들 (높은 우선도)
            "드래곤 바베큐": Recipe(
                name="드래곤 바베큐",
                ingredients={"고기류": 8.0, "향신료": 5.0, "특수재료": 2.0},
                effects={"all_stats": 30, "fire_resistance": 80, "attack": 40},
                duration_steps=400,
                description="전설적인 드래곤 고기로 만든 바베큐. 모든 능력치 대폭 상승.",
                icon="🐲",
                priority=10,
                difficulty=5,
                special_effects=["fire_immunity", "intimidation"]
            ),
            
            "시간 조작 스튜": Recipe(
                name="시간 조작 스튜",
                ingredients={"과일류": 5.0, "채소류": 3.0, "특수재료": 6.0, "액체류": 2.5},
                effects={"speed": 60, "evasion": 30},
                duration_steps=250,
                description="시간을 조작하는 신비한 스튜. 엄청난 속도와 회피율 획득.",
                icon="⏰",
                priority=9,
                difficulty=5,
                special_effects=["double_turn", "time_slow"]
            ),
            
            "요정의 케이크": Recipe(
                name="요정의 케이크",
                ingredients={"특수재료": 4.0, "과일류": 4.0, "곡물류": 2.0, "액체류": 1.5},
                effects={"luck": 40, "exp_bonus": 100, "all_stats": 15},
                duration_steps=300,
                description="요정들이 만든다는 전설의 케이크. 행운과 경험치 획득량 대폭 증가.",
                icon="🧁",
                priority=8,
                difficulty=4,
                special_effects=["lucky_drops", "exp_multiplier", "rare_encounters"]
            ),
            
            # 특수 효과 요리들
            "독 면역 수프": Recipe(
                name="독 면역 수프",
                ingredients={"채소류": 2.0, "약초류": 2.0, "액체류": 1.0},
                effects={"poison_immunity": 100, "hp_recovery": 20},
                duration_steps=200,
                description="독을 독으로 제압하는 수프. 독에 완전 면역.",
                icon="🍄",
                priority=6,
                difficulty=3,
                special_effects=["poison_immunity", "toxin_absorption"]
            ),
            
            "투명 젤리": Recipe(
                name="투명 젤리",
                ingredients={"액체류": 4.0, "특수재료": 2.0, "과일류": 1.0},
                effects={"stealth": 90, "evasion": 20},
                duration_steps=100,
                description="몸을 투명하게 만드는 신비한 젤리.",
                icon="👻",
                priority=7,
                difficulty=4,
                special_effects=["invisibility", "stealth_attack"]
            ),
            
            "광전사의 고기": Recipe(
                name="광전사의 고기",
                ingredients={"고기류": 3.0, "향신료": 2.0, "약초류": 1.5},
                effects={"berserk_mode": 100, "attack": 50},
                duration_steps=80,
                description="광폭화 상태. 공격력 2배, 방어력 절반.",
                icon="😡",
                priority=5,
                difficulty=3,
                special_effects=["berserk", "double_damage", "half_defense", "fear_immunity"]
            ),
            
            "얼음 여왕의 디저트": Recipe(
                name="얼음 여왕의 디저트",
                ingredients={"채소류": 2.0, "향신료": 3.0, "액체류": 2.0, "과일류": 1.0},
                effects={"freeze_aura": 70, "ice_resistance": 100},
                duration_steps=180,
                description="주변 적들을 얼려버리는 차가운 디저트.",
                icon="🍦",
                priority=6,
                difficulty=4,
                special_effects=["freeze_enemies", "ice_trail", "cold_immunity"]
            ),
            
            # 새로운 창의적인 요리들
            "생명력 폭발 수프": Recipe(
                name="생명력 폭발 수프",
                ingredients={"약초류": 5.0, "과일류": 3.0, "액체류": 6.0, "특수재료": 1.0},
                effects={"max_hp": 100, "hp_regen": 8, "regeneration": 50},
                duration_steps=350,
                description="생명력이 폭발적으로 증가하는 수프.",
                icon="�",
                priority=8,
                difficulty=4,
                special_effects=["super_regen", "wound_healing", "life_steal"]
            ),
            
            "마나 폭풍 리조또": Recipe(
                name="마나 폭풍 리조또",
                ingredients={"곡물류": 3.0, "채소류": 4.0, "액체류": 4.0, "특수재료": 2.0},
                effects={"max_mp": 80, "magic_attack": 40, "mana_efficiency": 50},
                duration_steps=280,
                description="마나 폭풍을 일으키는 강력한 리조또.",
                icon="🌀",
                priority=7,
                difficulty=4,
                special_effects=["mana_overflow", "spell_critical", "mana_shield"]
            ),
            
            "불사조의 향연": Recipe(
                name="불사조의 향연",
                ingredients={"고기류": 6.0, "과일류": 4.0, "향신료": 6.0, "특수재료": 8.0},
                effects={"all_stats": 50, "resurrection": 1},
                duration_steps=500,
                description="죽어도 한 번 부활할 수 있는 전설의 요리.",
                icon="🔥",
                priority=10,
                difficulty=6,
                special_effects=["phoenix_resurrection", "fire_rebirth", "immortality_glimpse"]
            ),
            
            "대지의 축복": Recipe(
                name="대지의 축복",
                ingredients={"채소류": 5.0, "곡물류": 4.0, "약초류": 3.0, "특수재료": 2.0},
                effects={"earth_power": 60, "defense": 30, "stability": 80},
                duration_steps=300,
                description="대지의 힘을 받는 축복받은 요리.",
                icon="🌍",
                priority=6,
                difficulty=4,
                special_effects=["earth_shield", "tremor_resistance", "nature_bond"]
            ),
            
            "바람의 자유": Recipe(
                name="바람의 자유",
                ingredients={"과일류": 4.0, "액체류": 3.0, "특수재료": 3.0},
                effects={"speed": 40, "flight": 80, "wind_mastery": 60},
                duration_steps=200,
                description="바람처럼 자유롭게 날 수 있는 요리.",
                icon="💨",
                priority=7,
                difficulty=5,
                special_effects=["flight", "wind_walk", "air_dash"]
            ),
            
            "지혜의 만찬": Recipe(
                name="지혜의 만찬",
                ingredients={"약초류": 4.0, "곡물류": 3.0, "액체류": 2.0, "특수재료": 4.0},
                effects={"intelligence": 50, "wisdom": 40, "insight": 60},
                duration_steps=400,
                description="지혜와 통찰력을 크게 높이는 만찬.",
                icon="🧠",
                priority=6,
                difficulty=4,
                special_effects=["future_sight", "tactical_genius", "magic_mastery"]
            ),
            
            "악마의 유혹": Recipe(
                name="악마의 유혹",
                ingredients={"고기류": 4.0, "채소류": 2.0, "향신료": 4.0, "특수재료": 3.0},
                effects={"dark_power": 70, "fear_aura": 50, "corruption": 40},
                duration_steps=250,
                description="어둠의 힘을 얻지만 대가가 따르는 위험한 요리.",
                icon="😈",
                priority=4,
                difficulty=5,
                special_effects=["dark_magic", "fear_enemies", "soul_drain", "corruption_risk"]
            ),
            
            "천사의 은총": Recipe(
                name="천사의 은총",
                ingredients={"과일류": 6.0, "액체류": 5.0, "약초류": 4.0, "특수재료": 5.0},
                effects={"holy_power": 80, "purification": 100, "blessing": 60},
                duration_steps=350,
                description="천사의 축복을 받는 신성한 요리.",
                icon="😇",
                priority=9,
                difficulty=5,
                special_effects=["holy_aura", "purify_all", "divine_protection", "heal_others"]
            ),
            
            # 실패작
            "곤죽": Recipe(
                name="곤죽",
                ingredients={},  # 어떤 조합이든 실패하면 이것이 됨
                effects={"hp_recovery": -10, "all_stats": -5},
                duration_steps=30,
                description="요리에 실패해서 만들어진 끔찍한 곤죽. 모든 능력치 감소.",
                icon="🤢",
                priority=0,
                difficulty=0,
                special_effects=["nausea", "bad_taste"]
            ),
        }
    
    def add_ingredient(self, ingredient_name: str, amount: int = 1):
        """식재료 추가"""
        if ingredient_name in self.all_ingredients:
            if ingredient_name in self.ingredients_inventory:
                self.ingredients_inventory[ingredient_name] += amount
            else:
                self.ingredients_inventory[ingredient_name] = amount
            return True
        return False
    
    def get_random_ingredient_drop(self, enemy_level: int = 1) -> Optional[str]:
        """적 처치 시 랜덤 식재료 드롭"""
        # 적 레벨에 따라 드롭률과 희귀도 조정
        drop_chance = 0.3 + (enemy_level * 0.05)  # 기본 30% + 레벨당 5%
        
        if random.random() > drop_chance:
            return None
        
        # 희귀도별 가중치
        rarity_weights = {
            1: 50,  # 일반
            2: 30,  # 희귀
            3: 15,  # 레어
            4: 4,   # 에픽
            5: 1    # 전설
        }
        
        # 적 레벨이 높을수록 좋은 재료 드롭 확률 증가
        if enemy_level >= 5:
            rarity_weights[3] += 10
            rarity_weights[4] += 5
        if enemy_level >= 10:
            rarity_weights[4] += 10
            rarity_weights[5] += 5
        
        available_ingredients = []
        for name, ingredient in self.all_ingredients.items():
            weight = rarity_weights.get(ingredient.rarity, 1)
            available_ingredients.extend([name] * weight)
        
        if available_ingredients:
            return random.choice(available_ingredients)
        return None
    
    def can_cook_with_substitutes(self, recipe_name: str) -> Tuple[bool, Dict[str, List[Tuple[str, float]]]]:
        """레시피를 재료 대체로 요리할 수 있는지 확인"""
        if recipe_name not in self.all_recipes:
            return False, {}
        
        recipe = self.all_recipes[recipe_name]
        substitution_plan = {}
        
        for ingredient_type, needed_value in recipe.ingredients.items():
            # 해당 타입의 재료들을 가치순으로 정렬
            available_ingredients = []
            for name, ingredient in self.all_ingredients.items():
                if ingredient.type.value == ingredient_type and name in self.ingredients_inventory:
                    available_count = self.ingredients_inventory[name]
                    available_ingredients.append((name, ingredient.value, available_count))
            
            if not available_ingredients:
                return False, {}
            
            # 가치가 높은 것부터 사용 (효율적인 대체)
            available_ingredients.sort(key=lambda x: x[1], reverse=True)
            
            current_value = 0.0
            selected_ingredients = []
            
            for name, value, count in available_ingredients:
                if current_value >= needed_value:
                    break
                
                # 필요한 만큼만 사용
                remaining_needed = needed_value - current_value
                use_count = min(count, int(remaining_needed / value) + (1 if remaining_needed % value > 0 else 0))
                
                if use_count > 0:
                    selected_ingredients.append((name, min(remaining_needed / value, use_count)))
                    current_value += value * min(remaining_needed / value, use_count)
            
            if current_value < needed_value:
                return False, {}
            
            substitution_plan[ingredient_type] = selected_ingredients
        
        return True, substitution_plan
    
    def can_cook(self, recipe_name: str) -> bool:
        """레시피를 요리할 수 있는지 확인 (대체 재료 포함)"""
        can_cook, _ = self.can_cook_with_substitutes(recipe_name)
        return can_cook
    
    def cook_dish(self, recipe_name: str) -> Tuple[bool, str]:
        """요리 제작 - 성공/실패와 결과 메시지 반환"""
        can_cook, substitution_plan = self.can_cook_with_substitutes(recipe_name)
        if not can_cook:
            return False, "재료가 부족합니다."
        
        recipe = self.all_recipes[recipe_name]
        
        # 재료 소모
        for ingredient_type, selected_ingredients in substitution_plan.items():
            for ingredient_name, use_amount in selected_ingredients:
                use_count = int(use_amount) + (1 if use_amount % 1 > 0 else 0)
                self.ingredients_inventory[ingredient_name] -= use_count
                if self.ingredients_inventory[ingredient_name] <= 0:
                    del self.ingredients_inventory[ingredient_name]
        
        # 성공 확률 계산 (요리 레벨과 난이도에 따라)
        base_success_rate = 0.8
        level_bonus = min(self.cooking_level * 0.05, 0.4)  # 최대 40% 보너스
        difficulty_penalty = recipe.difficulty * 0.1
        success_rate = max(0.1, base_success_rate + level_bonus - difficulty_penalty)
        
        if random.random() > success_rate:
            # 실패 - 곤죽 생성
            self._apply_cooking_buff(self.all_recipes["곤죽"])
            self._gain_cooking_exp(5)  # 실패해도 조금은 경험치 획득
            return True, f"요리에 실패했습니다! 끔찍한 곤죽이 만들어졌습니다... (성공률: {success_rate*100:.1f}%)"
        
        # 성공
        actual_recipe = self._determine_recipe_result(substitution_plan)
        if actual_recipe != recipe_name:
            # 다른 요리가 만들어짐
            self._apply_cooking_buff(self.all_recipes[actual_recipe])
            self.discovered_recipes.add(actual_recipe)
            self._gain_cooking_exp(recipe.duration_steps // 15)
            return True, f"의도하지 않았지만 {actual_recipe}이(가) 만들어졌습니다!"
        else:
            # 의도한 요리 성공
            self._apply_cooking_buff(recipe)
            self.discovered_recipes.add(recipe_name)
            self._gain_cooking_exp(recipe.duration_steps // 10)
            return True, f"{recipe_name}을(를) 성공적으로 만들었습니다!"
    
    def _determine_recipe_result(self, substitution_plan: Dict[str, List[Tuple[str, float]]]) -> str:
        """사용된 재료 조합에 따라 실제로 만들어질 요리 결정"""
        # 우선도가 높은 레시피부터 확인
        possible_recipes = []
        
        for recipe_name, recipe in self.all_recipes.items():
            if recipe_name == "곤죽":
                continue
            
            matches = True
            for ingredient_type, needed_value in recipe.ingredients.items():
                if ingredient_type not in substitution_plan:
                    matches = False
                    break
                
                total_value = sum(ing[1] * self.all_ingredients[ing[0]].value 
                                for ing in substitution_plan[ingredient_type])
                if total_value < needed_value * 0.8:  # 80% 이상 충족해야 함
                    matches = False
                    break
            
            if matches:
                possible_recipes.append((recipe_name, recipe.priority))
        
        if possible_recipes:
            # 우선도가 가장 높은 레시피 선택
            possible_recipes.sort(key=lambda x: x[1], reverse=True)
            return possible_recipes[0][0]
        
        return "곤죽"  # 어떤 레시피도 매치되지 않으면 곤죽
    
    def _apply_cooking_buff(self, recipe: Recipe):
        """요리 버프 적용"""
        # 기존 같은 음식 버프 제거
        self.active_buffs = [buff for buff in self.active_buffs if buff.recipe_name != recipe.name]
        
        # 새 버프 추가
        new_buff = CookingBuff(
            recipe_name=recipe.name,
            effects=recipe.effects.copy(),
            remaining_steps=recipe.duration_steps,
            special_effects=recipe.special_effects or [],
            icon=recipe.icon
        )
        
        self.active_buffs.append(new_buff)
    
    def update_buffs_on_step(self):
        """걸음마다 버프 업데이트"""
        expired_buffs = []
        
        for buff in self.active_buffs:
            buff.remaining_steps -= 1
            
            # HP 회복 특수 효과 처리
            if "hp_regen_per_step" in buff.special_effects:
                # 파티 전체 HP 회복 (게임 시스템에서 처리)
                pass
            
            if buff.remaining_steps <= 0:
                expired_buffs.append(buff)
        
        # 만료된 버프 제거
        for expired_buff in expired_buffs:
            self.active_buffs.remove(expired_buff)
    
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
    
    def get_active_special_effects(self) -> List[str]:
        """현재 활성화된 특수 효과 목록"""
        special_effects = []
        for buff in self.active_buffs:
            special_effects.extend(buff.special_effects)
        return special_effects
    
    def _gain_cooking_exp(self, amount: int):
        """요리 경험치 획득"""
        self.cooking_experience += amount
        
        # 레벨업 체크
        exp_needed = self.cooking_level * 100
        while self.cooking_experience >= exp_needed:
            self.cooking_experience -= exp_needed
            self.cooking_level += 1
            exp_needed = self.cooking_level * 100
    
    def discover_random_recipe(self) -> Optional[str]:
        """랜덤 레시피 발견"""
        undiscovered = [name for name in self.all_recipes.keys() 
                       if name not in self.discovered_recipes]
        
        if undiscovered and random.random() < 0.1:  # 10% 확률
            discovered = random.choice(undiscovered)
            self.discovered_recipes.add(discovered)
            return discovered
        
        return None
    
    def show_ingredients_inventory(self):
        """식재료 인벤토리 표시"""
        print(f"\n{CYAN}{'='*50}{RESET}")
        print(f"{WHITE}{BOLD}🥕 식재료 인벤토리{RESET}")
        print(f"{CYAN}{'='*50}{RESET}")
        
        if not self.ingredients_inventory:
            print(f"{YELLOW}보유한 식재료가 없습니다.{RESET}")
            return
        
        # 타입별로 분류하여 표시
        by_type = {}
        total_value_by_type = {}
        for ingredient_name, amount in self.ingredients_inventory.items():
            if ingredient_name in self.all_ingredients:
                ingredient = self.all_ingredients[ingredient_name]
                type_name = ingredient.type.value
                if type_name not in by_type:
                    by_type[type_name] = []
                    total_value_by_type[type_name] = 0.0
                by_type[type_name].append((ingredient, amount))
                total_value_by_type[type_name] += ingredient.value * amount
        
        for type_name, items in by_type.items():
            total_value = total_value_by_type[type_name]
            print(f"\n{YELLOW}{type_name} (총 가치: {total_value:.1f}):{RESET}")
            items.sort(key=lambda x: x[0].value, reverse=True)  # 가치순 정렬
            for ingredient, amount in items:
                rarity_color = [WHITE, GREEN, BLUE, MAGENTA, YELLOW][min(ingredient.rarity-1, 4)]
                total_ingredient_value = ingredient.value * amount
                print(f"  {ingredient.icon} {rarity_color}{ingredient.name}{RESET} x{amount} (가치: {ingredient.value:.1f}개당, 총 {total_ingredient_value:.1f})")
                print(f"    {WHITE}{ingredient.description}{RESET}")
    
    def show_available_recipes(self):
        """사용 가능한 레시피 표시"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}📖 발견한 요리 레시피 (우선도순){RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        if not self.discovered_recipes:
            print(f"{YELLOW}발견한 레시피가 없습니다.{RESET}")
            return
        
        # 우선도순으로 정렬
        sorted_recipes = sorted(self.discovered_recipes, 
                              key=lambda x: self.all_recipes[x].priority, reverse=True)
        
        available_count = 0
        for recipe_name in sorted_recipes:
            recipe = self.all_recipes[recipe_name]
            can_make, substitution_plan = self.can_cook_with_substitutes(recipe_name)
            
            color = GREEN if can_make else RED
            status = "✅ 제작 가능" if can_make else "❌ 재료 부족"
            priority_stars = "⭐" * min(recipe.priority, 5)
            
            print(f"\n{color}{recipe.icon} {recipe.name}{RESET} {priority_stars} - {status}")
            print(f"  {WHITE}{recipe.description}{RESET}")
            print(f"  {BLUE}난이도: {'🔥' * recipe.difficulty} | 우선도: {recipe.priority}{RESET}")
            
            # 필요 재료 (타입별)
            print(f"  {CYAN}필요 재료:{RESET}")
            for ingredient_type, needed_value in recipe.ingredients.items():
                # 현재 보유한 해당 타입 재료들
                available_value = 0.0
                available_items = []
                for name, ingredient in self.all_ingredients.items():
                    if ingredient.type.value == ingredient_type and name in self.ingredients_inventory:
                        count = self.ingredients_inventory[name]
                        value = ingredient.value * count
                        available_value += value
                        available_items.append(f"{name}({ingredient.value}x{count})")
                
                need_color = GREEN if available_value >= needed_value else RED
                print(f"    {need_color}{ingredient_type}: {available_value:.1f}/{needed_value:.1f}{RESET}")
                if available_items:
                    print(f"      보유: {', '.join(available_items[:3])}{'...' if len(available_items) > 3 else ''}")
            
            # 효과
            print(f"  {YELLOW}효과:{RESET}")
            for effect, value in recipe.effects.items():
                print(f"    {effect}: +{value}")
            
            print(f"  {MAGENTA}지속시간: {recipe.duration_steps}걸음{RESET}")
            
            if recipe.special_effects:
                print(f"  {CYAN}특수효과: {', '.join(recipe.special_effects)}{RESET}")
            
            if can_make:
                available_count += 1
        
        print(f"\n{GREEN}제작 가능한 요리: {available_count}개{RESET}")
        print(f"{YELLOW}💡 같은 타입의 재료는 가치에 따라 대체 가능합니다!{RESET}")
    
    def show_active_buffs(self):
        """활성 요리 버프 표시"""
        print(f"\n{CYAN}{'='*40}{RESET}")
        print(f"{WHITE}{BOLD}🍳 활성 요리 효과{RESET}")
        print(f"{CYAN}{'='*40}{RESET}")
        
        if not self.active_buffs:
            print(f"{YELLOW}활성화된 요리 효과가 없습니다.{RESET}")
            return
        
        for buff in self.active_buffs:
            print(f"\n{GREEN}{buff.icon} {buff.recipe_name}{RESET}")
            print(f"  {MAGENTA}남은 시간: {buff.remaining_steps}걸음{RESET}")
            
            for effect, value in buff.effects.items():
                print(f"  {YELLOW}{effect}: +{value}{RESET}")
            
            if buff.special_effects:
                print(f"  {CYAN}특수효과: {', '.join(buff.special_effects)}{RESET}")

# 전역 인스턴스
cooking_system = CookingSystem()

def get_cooking_system():
    """요리 시스템 인스턴스 반환"""
    def cook_free_style(self, selected_ingredients: Dict[str, int]) -> Tuple[bool, str]:
        """자유 요리 - 사용자가 직접 재료 선택"""
        # 재료 보유 확인
        for ingredient_name, use_count in selected_ingredients.items():
            if self.ingredients_inventory.get(ingredient_name, 0) < use_count:
                return False, f"{ingredient_name}이(가) 부족합니다."
        
        # 재료 소모
        for ingredient_name, use_count in selected_ingredients.items():
            self.ingredients_inventory[ingredient_name] -= use_count
            if self.ingredients_inventory[ingredient_name] <= 0:
                del self.ingredients_inventory[ingredient_name]
        
        # 사용된 재료를 타입별로 분류
        ingredient_types = {}
        for ingredient_name, use_count in selected_ingredients.items():
            if ingredient_name in self.all_ingredients:
                ingredient = self.all_ingredients[ingredient_name]
                type_name = ingredient.type.value
                if type_name not in ingredient_types:
                    ingredient_types[type_name] = 0.0
                ingredient_types[type_name] += ingredient.value * use_count
        
        # 만들어질 수 있는 요리 찾기
        possible_recipes = []
        for recipe_name, recipe in self.all_recipes.items():
            if recipe_name == "곤죽":
                continue
                
            matches = True
            match_quality = 0.0
            
            for ingredient_type, needed_value in recipe.ingredients.items():
                available_value = ingredient_types.get(ingredient_type, 0.0)
                if available_value < needed_value * 0.6:  # 최소 60% 충족
                    matches = False
                    break
                match_quality += min(available_value / needed_value, 2.0)  # 최대 2배까지 점수
            
            if matches:
                possible_recipes.append((recipe_name, recipe.priority, match_quality))
        
        if not possible_recipes:
            # 실패 - 곤죽
            self._apply_cooking_buff(self.all_recipes["곤죽"])
            self._gain_cooking_exp(3)
            return True, "재료 조합이 맞지 않아 곤죽이 만들어졌습니다..."
        
        # 우선도와 매치 품질을 고려해서 선택
        possible_recipes.sort(key=lambda x: (x[1], x[2]), reverse=True)
        selected_recipe = possible_recipes[0][0]
        
        recipe = self.all_recipes[selected_recipe]
        
        # 성공 확률 계산
        base_success_rate = 0.6  # 자유 요리는 더 어려움
        level_bonus = min(self.cooking_level * 0.04, 0.3)
        difficulty_penalty = recipe.difficulty * 0.15
        success_rate = max(0.05, base_success_rate + level_bonus - difficulty_penalty)
        
        if random.random() > success_rate:
            # 실패
            self._apply_cooking_buff(self.all_recipes["곤죽"])
            self._gain_cooking_exp(5)
            return True, f"요리에 실패했습니다! 곤죽이 만들어졌습니다... (성공률: {success_rate*100:.1f}%)"
        
        # 성공
        self._apply_cooking_buff(recipe)
        self.discovered_recipes.add(selected_recipe)
        self._gain_cooking_exp(recipe.duration_steps // 8)  # 자유 요리는 더 많은 경험치
        
        return True, f"자유 요리로 {selected_recipe}을(를) 발견했습니다!"
    
    def get_random_field_ingredient(self) -> Optional[str]:
        """필드에서 랜덤 식재료 발견"""
        # 필드에서는 낮은 등급 재료가 주로 나옴
        field_drop_chance = 0.15  # 15% 확률
        
        if random.random() > field_drop_chance:
            return None
        
        # 필드에서는 주로 1-3등급 재료
        rarity_weights = {
            1: 60,  # 일반
            2: 30,  # 희귀  
            3: 10,  # 레어
        }
        
        available_ingredients = []
        for name, ingredient in self.all_ingredients.items():
            if ingredient.rarity <= 3:  # 필드에서는 3등급까지만
                weight = rarity_weights.get(ingredient.rarity, 1)
                available_ingredients.extend([name] * weight)
        
        if available_ingredients:
            return random.choice(available_ingredients)
        return None

def get_cooking_system():
    """요리 시스템 인스턴스 반환"""
    return cooking_system