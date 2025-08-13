# -*- coding: utf-8 -*-
"""
통합 장비 시스템
모든 장비 관련 기능을 하나로 통합한 시스템
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import math

# ===== 장비 관련 Enum 정의 =====

class EquipmentType(Enum):
    """장비 타입"""
    WEAPON = "무기"
    ARMOR = "방어구"
    ACCESSORY = "장신구"
    CONSUMABLE = "소비품"

class EquipmentRarity(Enum):
    """장비 희귀도"""
    COMMON = ("일반", 1.0, "⚪")
    UNCOMMON = ("고급", 1.5, "🟢")
    RARE = ("희귀", 2.0, "🔵")
    EPIC = ("영웅", 3.0, "🟣")
    LEGENDARY = ("전설", 5.0, "🟡")
    MYTHIC = ("신화", 10.0, "🔴")
    CURSED = ("저주받은", 0.5, "💀")
    
    def __init__(self, korean_name: str, multiplier: float, symbol: str):
        self.korean_name = korean_name
        self.multiplier = multiplier
        self.symbol = symbol

class WeaponCategory(Enum):
    """무기 카테고리"""
    SWORD = "검"
    AXE = "도끼"
    DAGGER = "단검"
    BOW = "활"
    STAFF = "지팡이"
    MACE = "메이스"
    GLOVES = "장갑"
    HARP = "하프"
    SPEAR = "창"
    GUN = "총"
    BOOK = "서적"
    WHIP = "채찍"
    WAND = "마법봉"
    FIST = "권투글러브"
    CROSSBOW = "석궁"
    THROWING = "투척무기"

class ArmorCategory(Enum):
    """방어구 카테고리"""
    LIGHT = "경갑"
    MEDIUM = "중갑"
    HEAVY = "중갑"
    ROBE = "로브"
    CLOTHING = "의복"
    SUIT = "슈트"

class AccessoryCategory(Enum):
    """장신구 카테고리"""
    RING = "반지"
    NECKLACE = "목걸이"
    EARRING = "귀걸이"
    BRACELET = "팔찌"
    BELT = "벨트"
    BOOTS = "신발"
    CLOAK = "망토"
    CHARM = "부적"
    GLASSES = "안경"
    BOOK = "책"
    WINGS = "날개"
    HEART = "심장"
    GLOVES = "장갑"
    HELMET = "투구"
    CHALICE = "성배"
    QUIVER = "화살통"
    WATCH = "시계"
    ORB = "오브"
    SHIELD = "방패"

class AdditionalOptionTier(Enum):
    """추가옵션 등급"""
    BASIC = ("기본", 1.0, 0.4)  # (이름, 효과 배율, 확률)
    ENHANCED = ("강화", 1.5, 0.3)
    SUPERIOR = ("우수", 2.0, 0.2)
    PERFECT = ("완벽", 3.0, 0.08)
    LEGENDARY = ("전설", 5.0, 0.02)
    
    def __init__(self, korean_name: str, multiplier: float, probability: float):
        self.korean_name = korean_name
        self.multiplier = multiplier
        self.probability = probability

class SpecialEffect(Enum):
    """특수 효과 (완성된 버전)"""
    # 기본 스탯 퍼센트 증가
    ATTACK_PERCENT = "공격력_퍼센트_증가"
    MAGIC_ATTACK_PERCENT = "마법공격력_퍼센트_증가"
    DEFENSE_PERCENT = "방어력_퍼센트_증가"
    MAGIC_DEFENSE_PERCENT = "마법방어력_퍼센트_증가"
    HP_PERCENT = "생명력_퍼센트_증가"
    MP_PERCENT = "마나_퍼센트_증가"
    SPEED_PERCENT = "속도_퍼센트_증가"
    
    # 기본 스탯 고정값 증가
    ATTACK_FLAT = "공격력_고정값_증가"
    MAGIC_ATTACK_FLAT = "마법공격력_고정값_증가"
    DEFENSE_FLAT = "방어력_고정값_증가"
    MAGIC_DEFENSE_FLAT = "마법방어력_고정값_증가"
    HP_FLAT = "생명력_고정값_증가"
    MP_FLAT = "마나_고정값_증가"
    SPEED_FLAT = "속도_고정값_증가"
    
    # 전투 효과
    CRITICAL_RATE = "치명타율_증가"
    CRITICAL_DAMAGE = "치명타_피해_증가"
    ACCURACY = "명중률_증가"
    EVASION = "회피율_증가"
    LIFE_STEAL = "생명력_흡수"
    THORNS = "가시_피해"
    COUNTER_ATTACK = "반격_확률"
    BLOCK_CHANCE = "방어_확률"
    
    # 확장 전투 효과
    SIGHT_RANGE = "시야_범위_증가"
    MOVEMENT_SPEED = "이동속도_증가"
    MAGIC_RESISTANCE = "마법_저항"
    PHYSICAL_RESISTANCE = "물리_저항"
    STATUS_RESISTANCE = "상태이상_저항"
    
    # 원소 피해 (10가지)
    FIRE_DAMAGE = "화염_피해"
    ICE_DAMAGE = "빙결_피해"
    LIGHTNING_DAMAGE = "번개_피해"
    EARTH_DAMAGE = "대지_피해"
    WIND_DAMAGE = "바람_피해"
    WATER_DAMAGE = "물_피해"
    LIGHT_DAMAGE = "빛_피해"
    DARK_DAMAGE = "어둠_피해"
    POISON_DAMAGE = "독_피해"
    ARCANE_DAMAGE = "비전_피해"
    
    # 원소 저항 (10가지)
    FIRE_RESISTANCE = "화염_저항"
    ICE_RESISTANCE = "빙결_저항"
    LIGHTNING_RESISTANCE = "번개_저항"
    EARTH_RESISTANCE = "대지_저항"
    WIND_RESISTANCE = "바람_저항"
    WATER_RESISTANCE = "물_저항"
    LIGHT_RESISTANCE = "빛_저항"
    DARK_RESISTANCE = "어둠_저항"
    POISON_RESISTANCE = "독_저항"
    ARCANE_RESISTANCE = "비전_저항"
    
    # 상태이상 효과
    POISON_CHANCE = "독_확률"
    BURN_CHANCE = "화상_확률"
    FREEZE_CHANCE = "빙결_확률"
    STUN_CHANCE = "기절_확률"
    BLIND_CHANCE = "실명_확률"
    SILENCE_CHANCE = "침묵_확률"
    
    # 전투 시 특수 효과
    MANA_BURN = "마나_번"
    POISON_ON_HIT = "공격_시_독"
    FREEZE_ON_HIT = "공격_시_빙결"
    LIGHTNING_CHAIN = "번개_연쇄"
    HEAL_ON_KILL = "처치_시_회복"
    MP_ON_KILL = "처치_시_마나_회복"
    
    # 방어 시 특수 효과
    DAMAGE_REFLECTION = "피해_반사"
    SHIELD_ON_HIT = "피격_시_방패_생성"
    HP_REGENERATION = "생명력_재생"
    MP_REGENERATION = "마나_재생"
    DAMAGE_REDUCTION = "피해_감소"
    
    # 스킬 관련 효과
    SKILL_COOLDOWN_REDUCTION = "스킬_쿨다운_감소"
    MANA_COST_REDUCTION = "마나_소모_감소"
    CAST_SPEED = "시전_속도_증가"
    SKILL_DAMAGE = "스킬_피해_증가"
    SKILL_RANGE = "스킬_범위_증가"
    SPELL_POWER = "주문력_증가"
    
    # 특별 효과
    EXPERIENCE_BOOST = "경험치_증가"
    GOLD_BOOST = "골드_획득_증가"
    ITEM_DROP_RATE = "아이템_드롭률_증가"
    RARE_DROP_RATE = "희귀_아이템_드롭률_증가"
    LUCK = "행운_증가"
    TELEPORT_CHANCE = "순간이동_확률"
    TIME_SLOW = "시간_둔화"
    
    # 내구도 관련
    SELF_REPAIR = "자가_수리"
    DURABILITY_BONUS = "내구도_증가"
    UNBREAKABLE = "파괴_불가"
    
    # 직업별 특수 효과
    WARRIOR_RAGE_BONUS = "전사_분노_보너스"
    MAGE_MANA_EFFICIENCY = "마법사_마나_효율"
    ARCHER_RANGE_BONUS = "궁수_사거리_보너스"
    ASSASSIN_STEALTH_BONUS = "암살자_은신_보너스"
    STEALTH_BOOST = "은신_효과_증가"
    MONK_CHI_BONUS = "몽크_기_보너스"
    BARD_MELODY_POWER = "바드_멜로디_위력"
    
    # BRV 시스템 (브레이브 시스템)
    MAX_BRV_PERCENT = "최대BRV_퍼센트_증가"
    MAX_BRV_FLAT = "최대BRV_고정값_증가"
    BRV_MAX_MULTIPLIER = "최대BRV_배수_증가"
    INT_BRV_PERCENT = "초기BRV_퍼센트_증가"
    INT_BRV_FLAT = "초기BRV_고정값_증가"
    BRV_INITIAL_BOOST = "초기BRV_부스트"
    BRV_GAIN_RATE = "BRV_획득_효율_증가"
    BRV_DAMAGE_BONUS = "BRV_피해_보너스"
    BRV_BREAK_BONUS = "BRV_브레이크_보너스"
    
    # ATB 시스템 (액티브 타임 배틀)
    ATB_SPEED = "ATB_속도_증가"
    ATB_GAUGE_START = "ATB_게이지_시작값_증가"
    ATB_INITIAL_BOOST = "ATB_초기_부스트"
    ATB_BOOST_ON_KILL = "처치시_ATB_증가"
    ATB_BOOST_ON_CRIT = "치명타시_ATB_증가"
    
    # 불릿타임 시스템
    BULLET_TIME_CHANCE = "불릿타임_발동_확률"
    BULLET_TIME_DURATION = "불릿타임_지속시간_증가"
    BULLET_TIME_SLOWDOWN = "불릿타임_둔화_효과_증가"
    BULLET_TIME_EFFICIENCY = "불릿타임_효율_증가"
    
    # 저주 효과
    CURSED_ATTACK_REDUCTION = "저주_공격력_감소"
    CURSED_DEFENSE_REDUCTION = "저주_방어력_감소"
    CURSED_SPEED_REDUCTION = "저주_속도_감소"
    CURSED_LUCK_REDUCTION = "저주_행운_감소"
    CURSED_HP_DRAIN = "저주_체력_지속_감소"
    CURSED_MP_DRAIN = "저주_마나_지속_감소"
    CURSE_WEAKNESS = "저주_약화"
    CURSE_FRAGILITY = "저주_취약성"
    
    # 추가 저주 효과들
    CURSE_EXHAUSTION = "저주_피로"
    CURSE_DRAIN = "저주_흡수"
    CURSE_CLUMSINESS = "저주_서투름"
    CURSE_SLUGGISHNESS = "저주_둔화"
    CURSE_MISFORTUNE = "저주_불운"
    CURSE_INEFFICIENCY = "저주_비효율"
    CURSE_WASTE = "저주_낭비"
    CURSE_BRV_DECAY = "저주_BRV_감소"
    CURSE_ATB_DELAY = "저주_ATB_지연"
    CURSE_BULLET_TIME_DISRUPTION = "저주_불릿타임_방해"
    
    # 그림자 시스템 특수 효과
    SHADOW_STEP = "그림자_이동"
    SHADOW_EMPOWERMENT = "그림자_강화"
    SHADOW_ECHO = "그림자_메아리"
    
    # 누락된 특수 효과들
    INSANITY_BOOST = "광기_증폭"
    CHAOS_MAGIC = "혼돈_마법"
    BETRAYAL_STRIKE = "배신의_일격"
    GREED_CURSE = "탐욕의_저주"
    HEALING_BOOST = "치유_효과_증가"
    
    # 추가 전투 효과
    SLOW_ON_HIT = "공격_시_둔화"
    COOLDOWN_REDUCTION = "쿨다운_감소"
    TREASURE_FIND = "보물_발견율"
    TRAP_DETECTION = "함정_탐지"
    ALL_STATS = "모든_스탯_증가"
    GOLD_FIND = "골드_획득량_증가"
    DODGE_CHANCE = "회피_확률"
    MANA_EFFICIENCY = "마나_효율"
    MANA_REGENERATION = "마나_재생"
    UNDEAD_DAMAGE = "언데드_추가_피해"
    CURSE_IMMUNITY = "저주_면역"
    STEALTH_ATTACK = "은신_공격"
    
    # 궁수 특수 효과
    PIERCING_SHOT = "관통_사격"
    MULTI_SHOT = "다중_사격"
    EAGLE_EYE = "독수리의_눈"
    ACCURACY_BOOST = "명중률_증가"
    
    # 특수 능력 효과
    PHOENIX_REBIRTH = "불사조_부활"
    FIRE_IMMUNITY = "화염_면역"
    TIDAL_WAVE = "해일"
    WATER_MASTERY = "수속성_숙련도"
    EARTHQUAKE = "지진"
    STUN_ON_HIT = "공격_시_기절"
    WIND_SLASH = "바람_베기"
    DOUBLE_ATTACK = "연속_공격"
    STARFALL = "별똥별"
    INFINITE_MANA = "무한_마나"
    DEMON_PACT = "악마의_계약"
    FLIGHT = "비행_능력"
    DIVINE_PROTECTION = "신의_가호"
    DRAGON_BREATH = "용의_숨결"
    INTIMIDATION = "위압"
    TENTACLE_GRAB = "촉수_포획"
    MULTI_HIT = "다중_타격"
    UNDEAD_MASTERY = "언데드_숙련도"
    LIFE_DRAIN = "생명력_흡수_확률"
    SKY_WALK = "공중_보행"
    WIND_MASTERY = "바람_숙련도"
    GOLDEN_TOUCH = "황금_터치"
    WORLD_BEARER = "세계_운반자"
    IMMOVABLE = "불굴"
    STRENGTH_BOOST = "힘_증가"
    HASTE = "가속"
    VAMPIRIC_CURSE = "흡혈_저주"
    BERSERK_MODE = "광전사_모드"
    DESPAIR_AURA = "절망_오라"
    DOOM_STRIKE = "파멸의_일격"
    MADNESS = "광기"
    PAIN_SHARE = "고통_공유"
    NECROMANCY = "네크로맨시"
    POWER_AT_COST = "대가를_치르는_힘"
    CURSED_HEALING = "저주받은_치유"
    LIFE_DRAIN_AURA = "생명력_흡수_오라"
    BACKSTAB_BOOST = "배후_공격_증가"
    LUCKY_CURSE = "행운의_저주"
    GAMBLER_STRIKE = "도박_공격"
    CRITICAL_GAMBLE = "치명타_도박"
    RANDOM_SPELL = "랜덤_주문"
    MANA_CHAOS = "마나_혼돈"
    RISKY_DEFENSE = "위험한_방어"
    ADRENALINE_RUSH = "아드레날린_분출"
    CHAOS_BOOST = "혼돈_증폭"
    RANDOM_EFFECT = "랜덤_효과"
    ADVENTURE_SPIRIT = "모험_정신"
    TREASURE_HUNT = "보물_사냥"
    MADNESS_POWER = "광기의_힘"
    INSANE_INSIGHT = "광적_통찰"
    EXPLOSIVE_HIT = "폭발_타격"
    BERSERKER_RAGE = "광전사_분노"
    FATE_ARROW = "운명의_화살"
    TIME_STEAL = "시간_도둑질"
    LIFE_GAMBLE = "생명_도박"
    RESURRECTION_CHANCE = "부활_확률"
    UNPREDICTABLE_MAGIC = "예측불가_마법"
    SPELL_REFLECTION = "주문_반사"
    EXPERIMENT_BOOST = "실험_증폭"
    ALCHEMY_MASTERY = "연금술_숙련도"
    TIME_STOP = "시간_정지"
    TELEPORT = "순간이동"
    LUCKY_SHOT = "행운의_사격"
    SOUL_SHIELD = "영혼_보호막"
    
    # 관통력 및 고정 피해 효과
    PHYSICAL_PENETRATION = "물리_관통력"
    MAGIC_PENETRATION = "마법_관통력"
    TRUE_DAMAGE = "고정_피해"
    ARMOR_IGNORE = "방어력_무시"
    PERCENTAGE_DAMAGE = "비율_피해"
    LOST_HP_DAMAGE = "잃은_체력_비례_피해"
    CURRENT_HP_DAMAGE = "현재_체력_비례_피해"
    MAX_HP_DAMAGE = "최대_체력_비례_피해"
    ENEMY_LOW_HP_DAMAGE = "적_저체력_추가_피해"
    ENEMY_HIGH_HP_DAMAGE = "적_고체력_추가_피해"
    CONDITIONAL_PENETRATION = "조건부_관통력"
    SOUL_DAMAGE = "영혼_피해"
    PERFECT_CLARITY = "완벽한_명료함"
    
    # 세트 효과
    SET_BONUS_2 = "세트_효과_2개"
    SET_BONUS_3 = "세트_효과_3개"
    SET_BONUS_4 = "세트_효과_4개"
    SET_BONUS_FULL = "세트_효과_풀세트"
    
    @property
    def korean_name(self) -> str:
        """한국어 이름 반환"""
        korean_names = {
            # 기본 스탯 (고정값)
            "공격력_고정값_증가": "공격력",
            "마법공격력_고정값_증가": "마법공격력",
            "방어력_고정값_증가": "방어력",
            "마법방어력_고정값_증가": "마법방어력",
            "생명력_고정값_증가": "체력",
            "마나_고정값_증가": "마나",
            "속도_고정값_증가": "속도",
            
            # 기본 스탯 (퍼센트)
            "공격력_퍼센트_증가": "공격력 %",
            "마법공격력_퍼센트_증가": "마법공격력 %",
            "방어력_퍼센트_증가": "방어력 %",
            "마법방어력_퍼센트_증가": "마법방어력 %",
            "생명력_퍼센트_증가": "체력 %",
            "마나_퍼센트_증가": "마나 %",
            "속도_퍼센트_증가": "속도 %",
            
            # 전투 효과
            "치명타율_증가": "치명타 확률",
            "치명타_피해_증가": "치명타 피해",
            "회피율_증가": "회피 확률",
            "생명력_흡수": "생명력 흡수",
            "명중률_증가": "명중률",
            "방어_확률": "방어 확률",
            "반격_확률": "반격 확률",
            
            # 원소 효과
            "화염_피해": "화염 피해",
            "빙결_피해": "빙결 피해",
            "번개_피해": "번개 피해",
            "대지_피해": "대지 피해",
            "바람_피해": "바람 피해",
            "물_피해": "물 피해",
            "어둠_피해": "어둠 피해",
            "빛_피해": "빛 피해",
            "독_피해": "독 피해",
            # "비전_피해": "비전 피해",  # 제거됨 - 비전 속성 없음
            
            # 원소 저항
            "화염_저항": "화염 저항",
            "빙결_저항": "빙결 저항",
            "번개_저항": "번개 저항",
            "대지_저항": "대지 저항",
            "바람_저항": "바람 저항",
            "물_저항": "물 저항",
            "어둠_저항": "어둠 저항",
            "빛_저항": "빛 저항",
            "독_저항": "독 저항",
            # "비전_저항": "비전 저항",  # 제거됨 - 비전 속성 없음
            
            # 상태이상 효과
            "독_확률": "독 확률",
            "화상_확률": "화상 확률",
            "빙결_확률": "빙결 확률",
            "기절_확률": "기절 확률",
            "실명_확률": "실명 확률",
            "침묵_확률": "침묵 확률",
            
            # 유틸리티 효과
            "시야_범위_증가": "시야 범위",
            "경험치_증가": "경험치 보너스",
            "골드_획득_증가": "골드 보너스",
            "아이템_드롭률_증가": "아이템 드롭률",
            "희귀_아이템_드롭률_증가": "희귀 아이템 드롭률",
            "이동속도_증가": "이동 속도",
            
            # 특수 능력
            "마나_재생": "마나 재생",
            "생명력_재생": "체력 재생",
            "주문력_증가": "주문력",
            "스킬_쿨다운_감소": "쿨다운 감소",
            "시전_속도_증가": "시전 속도",
            
            # 직업별 특수 효과
            "전사_분노_보너스": "전사 분노 보너스",
            "마법사_마나_효율": "마법사 마나 효율",
            "궁수_사거리_보너스": "궁수 사거리 보너스",
            "암살자_은신_보너스": "암살자 은신 보너스",
            "은신_효과_증가": "은신 효과",
            "몽크_기_보너스": "몽크 기 보너스",
            "바드_멜로디_위력": "바드 멜로디 위력",
            
            # BRV 시스템
            "최대BRV_퍼센트_증가": "최대 BRV %",
            "최대BRV_고정값_증가": "최대 BRV",
            "초기BRV_퍼센트_증가": "초기 BRV %",
            "초기BRV_고정값_증가": "초기 BRV",
            "BRV_획득_효율_증가": "BRV 획득 효율",
            "BRV_피해_보너스": "BRV 피해 보너스",
            "BRV_브레이크_보너스": "BRV 브레이크 보너스",
            
            # ATB 시스템
            "ATB_속도_증가": "ATB 속도",
            "ATB_게이지_시작값_증가": "ATB 시작값",
            "처치시_ATB_증가": "처치시 ATB 증가",
            "치명타시_ATB_증가": "치명타시 ATB 증가",
            
            # 불릿타임 시스템
            "불릿타임_발동_확률": "불릿타임 발동 확률",
            "불릿타임_지속시간_증가": "불릿타임 지속시간",
            "불릿타임_둔화_효과_증가": "불릿타임 둔화 효과",
            
            # 저주 효과
            "저주_공격력_감소": "저주: 공격력 감소",
            "저주_방어력_감소": "저주: 방어력 감소",
            "저주_속도_감소": "저주: 속도 감소",
            "저주_행운_감소": "저주: 행운 감소",
            "저주_체력_지속_감소": "저주: 체력 지속 감소",
            "저주_마나_지속_감소": "저주: 마나 지속 감소",
            
            # 그림자 시스템 특수 효과
            "그림자_이동": "그림자 이동",
            "그림자_강화": "그림자 강화",
            "그림자_메아리": "그림자 메아리",
            
            # 특수 효과
            "광기_증폭": "광기 증폭",
            "혼돈_마법": "혼돈 마법",
            "배신의_일격": "배신의 일격",
            "탐욕의_저주": "탐욕의 저주",
            "치유_효과_증가": "치유 효과 증가",
            
            # 신규 리스크-리턴 효과들
            "광폭화_모드": "광폭화 모드",
            "유리대포": "유리대포",
            "흡혈_저주": "흡혈의 저주",
            "마나_과부하": "마나 과부하",
            "시공간_불안정": "시공간 불안정",
            "영혼_결속": "영혼 결속",
            "치명타_과부하": "치명타 과부하",
            "원소_혼돈": "원소 혼돈",
            "죽음의_소원": "죽음의 소원",
            "행운의_저주": "행운의 저주",
            "분노_축적": "분노 축적",
            "환영_타격": "환영 타격",
            "광전사_광란": "광전사 광란",
            "마나_누출": "마나 누출",
            "양날의_검": "양날의 검",
            
            # 관통력 및 고정 피해 효과
            "물리_관통력": "물리 관통력",
            "마법_관통력": "마법 관통력",
            "고정_피해": "고정 피해",
            "방어력_무시": "방어력 무시",
            "비율_피해": "비율 피해",
            "잃은_체력_비례_피해": "잃은 체력 비례 피해",
            "현재_체력_비례_피해": "현재 체력 비례 피해",
            "최대_체력_비례_피해": "최대 체력 비례 피해",
            "적_저체력_추가_피해": "적 저체력 추가 피해",
            "적_고체력_추가_피해": "적 고체력 추가 피해",
            "조건부_관통력": "조건부 관통력",
            "영혼_피해": "영혼 피해",
            "완벽한_명료함": "완벽한 명료함"
        }
        return korean_names.get(self.value, self.value)

# ===== 장비 효과 클래스 =====

@dataclass
class EquipmentEffect:
    """장비 효과 클래스"""
    effect_type: SpecialEffect
    value: float
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 직렬화"""
        return {
            "effect_type": self.effect_type.value,
            "value": self.value,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EquipmentEffect':
        """딕셔너리에서 역직렬화"""
        effect_type = SpecialEffect(data["effect_type"])
        return cls(
            effect_type=effect_type,
            value=data["value"],
            description=data.get("description", "")
        )

# ===== 장비 클래스 =====

@dataclass
class Equipment:
    """통합 장비 클래스"""
    name: str
    equipment_type: EquipmentType
    rarity: EquipmentRarity
    level: int = 1
    
    # 기본 스탯
    stats: Dict[str, int] = field(default_factory=dict)
    
    # 내구도
    durability: int = 100
    max_durability: int = 100
    
    # 특수 효과
    special_effects: List[EquipmentEffect] = field(default_factory=list)
    
    # 강화 관련
    enhancement_level: int = 0
    max_enhancement: int = 15
    
    # 세트 장비 관련
    set_name: str = ""
    set_piece_id: int = 0
    
    # 추가옵션 시스템
    additional_options: List[EquipmentEffect] = field(default_factory=list)
    cursed_options: List[EquipmentEffect] = field(default_factory=list)
    max_additional_options: int = 3
    
    # 기타 속성
    description: str = ""
    weight: float = 0.0
    sell_price: int = 0
    is_starting_item: bool = False
    is_unique: bool = False
    is_cursed: bool = False
    
    def get_total_stats(self) -> Dict[str, int]:
        """강화 레벨을 포함한 총 스탯 계산"""
        total_stats = self.stats.copy()
        
        # 강화 보너스 적용
        enhancement_multiplier = 1.0 + (self.enhancement_level * 0.1)
        for stat, value in total_stats.items():
            total_stats[stat] = int(value * enhancement_multiplier)
        
        return total_stats
    
    def get_display_name(self) -> str:
        """표시용 이름 (강화 레벨 포함)"""
        name = f"{self.rarity.symbol} {self.name}"
        if self.enhancement_level > 0:
            name += f" +{self.enhancement_level}"
        return name
    
    def enhance(self) -> bool:
        """장비 강화"""
        if self.enhancement_level >= self.max_enhancement:
            return False
        
        # 강화 성공률 계산 (레벨이 높을수록 낮아짐)
        success_rate = max(0.1, 1.0 - (self.enhancement_level * 0.05))
        
        if random.random() < success_rate:
            self.enhancement_level += 1
            return True
        return False
    
    def repair(self, amount: int = None) -> int:
        """장비 수리"""
        if amount is None:
            amount = self.max_durability
        
        old_durability = self.durability
        self.durability = min(self.max_durability, self.durability + amount)
        return self.durability - old_durability
    
    def take_damage(self, amount: int = 1) -> bool:
        """내구도 감소"""
        if self.has_effect(SpecialEffect.UNBREAKABLE):
            return True
        
        self.durability = max(0, self.durability - amount)
        return self.durability > 0
    
    def has_effect(self, effect_type: SpecialEffect) -> bool:
        """특정 효과 보유 여부 확인"""
        return any(effect.effect_type == effect_type for effect in self.special_effects)
    
    def get_effect_value(self, effect_type: SpecialEffect) -> float:
        """특정 효과의 값 반환"""
        for effect in self.special_effects:
            if effect.effect_type == effect_type:
                return effect.value
        return 0.0
    
    def get_all_effects(self) -> List[EquipmentEffect]:
        """모든 효과 반환 (기본 + 추가옵션 + 저주)"""
        all_effects = self.special_effects.copy()
        all_effects.extend(self.additional_options)
        all_effects.extend(self.cursed_options)
        return all_effects
    
    def add_additional_option(self, effect: EquipmentEffect, tier: AdditionalOptionTier) -> bool:
        """추가옵션 추가"""
        if len(self.additional_options) >= self.max_additional_options:
            return False
        
        # 등급에 따른 효과 배율 적용
        enhanced_effect = EquipmentEffect(
            effect_type=effect.effect_type,
            value=effect.value * tier.multiplier,
            description=f"[{tier.korean_name}] {effect.description}"
        )
        
        self.additional_options.append(enhanced_effect)
        return True
    
    def add_curse(self, curse_effect: EquipmentEffect) -> None:
        """저주 효과 추가"""
        self.cursed_options.append(curse_effect)
        self.is_cursed = True
    
    def reroll_additional_option(self, index: int, new_effect: EquipmentEffect, new_tier: AdditionalOptionTier) -> bool:
        """추가옵션 리롤 (저주된 옵션은 리롤 불가)"""
        if index >= len(self.additional_options):
            return False
        
        # 저주된 옵션인지 확인 (저주된 옵션은 리롤 불가)
        if any(curse.effect_type == self.additional_options[index].effect_type for curse in self.cursed_options):
            return False
        
        enhanced_effect = EquipmentEffect(
            effect_type=new_effect.effect_type,
            value=new_effect.value * new_tier.multiplier,
            description=f"[{new_tier.korean_name}] {new_effect.description}"
        )
        
        self.additional_options[index] = enhanced_effect
        return True
    
    def calculate_weight(self) -> float:
        """장비 무게 계산 (0.25~8kg 범위)"""
        base_weight = 1.0
        
        # 장비 타입별 기본 무게
        if self.equipment_type == EquipmentType.WEAPON:
            base_weight = 2.0
        elif self.equipment_type == EquipmentType.ARMOR:
            base_weight = 4.0
        elif self.equipment_type == EquipmentType.ACCESSORY:
            base_weight = 0.5
        
        # 희귀도에 따른 무게 조정
        rarity_multiplier = {
            EquipmentRarity.COMMON: 0.8,
            EquipmentRarity.UNCOMMON: 1.0,
            EquipmentRarity.RARE: 1.2,
            EquipmentRarity.EPIC: 1.5,
            EquipmentRarity.LEGENDARY: 2.0,
            EquipmentRarity.MYTHIC: 3.0
        }.get(self.rarity, 1.0)
        
        # 최종 무게 계산 (0.25~8kg 범위로 제한)
        final_weight = base_weight * rarity_multiplier * random.uniform(0.7, 1.3)
        return max(0.25, min(8.0, final_weight))
    
    def enhance_equipment(self, materials: Dict[str, int] = None, success_rate_bonus: float = 0.0) -> Dict[str, Any]:
        """장비 강화 시스템"""
        if self.enhancement_level >= self.max_enhancement:
            return {"success": False, "message": "최대 강화 단계에 도달했습니다.", "destroyed": False}
        
        # 강화 성공률 계산 (적당한 수준)
        base_success_rates = {
            0: 0.95,   # +1: 95%
            1: 0.90,   # +2: 90%
            2: 0.85,   # +3: 85%
            3: 0.80,   # +4: 80%
            4: 0.75,   # +5: 75%
            5: 0.70,   # +6: 70%
            6: 0.65,   # +7: 65%
            7: 0.60,   # +8: 60%
            8: 0.55,   # +9: 55%
            9: 0.50,   # +10: 50%
            10: 0.45,  # +11: 45%
            11: 0.40,  # +12: 40%
            12: 0.35,  # +13: 35%
            13: 0.30,  # +14: 30%
            14: 0.25   # +15: 25%
        }
        
        success_rate = base_success_rates.get(self.enhancement_level, 0.20) + success_rate_bonus
        success_rate = min(0.95, max(0.05, success_rate))  # 5%~95% 범위로 제한
        
        # 강화 시도
        rand = random.random()
        
        if rand < success_rate:
            # 강화 성공
            self.enhancement_level += 1
            self._apply_enhancement_bonus()
            return {"success": True, "message": f"강화 성공! +{self.enhancement_level}", "destroyed": False}
        else:
            # 강화 실패 - 등급 감소 및 내구도 감소
            penalty_applied = False
            penalty_message = "강화에 실패했습니다."
            
            # +5강부터 내구도 감소 (점진적 증가)
            if self.enhancement_level >= 5:
                durability_loss = min(10 + (self.enhancement_level - 5) * 5, 50)  # 최대 50까지
                self.durability = max(1, self.durability - durability_loss)
                penalty_message += f" 내구도가 {durability_loss} 감소했습니다."
                penalty_applied = True
            
            # +7강부터 등급 감소 확률
            if self.enhancement_level >= 7:
                downgrade_chance = min(0.1 + (self.enhancement_level - 7) * 0.05, 0.5)  # 최대 50%
                if random.random() < downgrade_chance:
                    old_level = self.enhancement_level
                    self.enhancement_level = max(0, self.enhancement_level - 1)
                    self._apply_enhancement_bonus()
                    penalty_message += f" 강화 등급이 +{old_level}에서 +{self.enhancement_level}로 감소했습니다."
                    penalty_applied = True
            
            return {"success": False, "message": penalty_message, "destroyed": False}
    
    def _apply_enhancement_bonus(self) -> None:
        """강화 보너스 적용"""
        # 강화 단계당 스탯 증가 (적당한 수준)
        enhancement_bonus = self.enhancement_level * 0.05  # 5%씩 증가
        
        # 기본 스탯에 보너스 적용
        for stat in self.stats:
            if stat in ['attack', 'magic_attack', 'defense', 'magic_defense', 'hp', 'mp']:
                # 기본값을 다시 계산하여 보너스 적용
                base_value = self.stats[stat] / (1 + max(0, self.enhancement_level - 1) * 0.05) if self.enhancement_level > 0 else self.stats[stat]
                self.stats[stat] = int(base_value * (1 + enhancement_bonus))
    
    def get_enhancement_cost(self) -> Dict[str, int]:
        """강화 비용 계산"""
        base_cost = 100
        level_multiplier = (self.enhancement_level + 1) ** 2
        rarity_multiplier = {
            EquipmentRarity.COMMON: 1.0,
            EquipmentRarity.UNCOMMON: 1.5,
            EquipmentRarity.RARE: 2.0,
            EquipmentRarity.EPIC: 3.0,
            EquipmentRarity.LEGENDARY: 5.0,
            EquipmentRarity.MYTHIC: 8.0
        }.get(self.rarity, 1.0)
        
        gold_cost = int(base_cost * level_multiplier * rarity_multiplier)
        
        return {
            "gold": gold_cost
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 직렬화"""
        return {
            "name": self.name,
            "equipment_type": self.equipment_type.value,
            "rarity": self.rarity.name,
            "level": self.level,
            "stats": self.stats,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "special_effects": [effect.to_dict() for effect in self.special_effects],
            "enhancement_level": self.enhancement_level,
            "max_enhancement": self.max_enhancement,
            "set_name": self.set_name,
            "set_piece_id": self.set_piece_id,
            "additional_options": [effect.to_dict() for effect in self.additional_options],
            "cursed_options": [effect.to_dict() for effect in self.cursed_options],
            "max_additional_options": self.max_additional_options,
            "is_cursed": self.is_cursed,
            "description": self.description,
            "weight": self.weight,
            "sell_price": self.sell_price,
            "is_starting_item": self.is_starting_item,
            "is_unique": self.is_unique
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Equipment':
        """딕셔너리에서 역직렬화"""
        equipment = cls(
            name=data["name"],
            equipment_type=EquipmentType(data["equipment_type"]),
            rarity=EquipmentRarity[data["rarity"]],
            level=data.get("level", 1),
            stats=data.get("stats", {}),
            durability=data.get("durability", 100),
            max_durability=data.get("max_durability", 100),
            enhancement_level=data.get("enhancement_level", 0),
            max_enhancement=data.get("max_enhancement", 15),
            set_name=data.get("set_name", ""),
            set_piece_id=data.get("set_piece_id", 0),
            description=data.get("description", ""),
            weight=data.get("weight", 0.0),
            sell_price=data.get("sell_price", 0),
            is_starting_item=data.get("is_starting_item", False),
            is_unique=data.get("is_unique", False)
        )
        
        # 추가 옵션 및 저주 관련 속성 복원
        equipment.max_additional_options = data.get("max_additional_options", 3)
        equipment.is_cursed = data.get("is_cursed", False)
        
        # 특수 효과 복원
        for effect_data in data.get("special_effects", []):
            equipment.special_effects.append(EquipmentEffect.from_dict(effect_data))
        
        # 추가 옵션 복원
        for effect_data in data.get("additional_options", []):
            equipment.additional_options.append(EquipmentEffect.from_dict(effect_data))
        
        # 저주 옵션 복원
        for effect_data in data.get("cursed_options", []):
            equipment.cursed_options.append(EquipmentEffect.from_dict(effect_data))
        
        return equipment

# ===== 장비 생성기 =====

class UnifiedEquipmentGenerator:
    """통합 장비 생성기"""
    
    def __init__(self):
        self.weapon_templates = self._init_weapon_templates()
        self.armor_templates = self._init_armor_templates()
        self.accessory_templates = self._init_accessory_templates()
        self.unique_equipment = self._init_unique_equipment()
        self.cursed_equipment = self._init_cursed_equipment()  # 신규: 저주받은 장비
        self.risk_return_equipment = self._init_risk_return_equipment()  # 신규: 리스크-리턴 장비
        self.set_equipment = self._init_set_equipment()
        self.additional_option_pool = self._init_additional_option_pool()
        self.curse_pool = self._init_curse_pool()
    
    def _init_additional_option_pool(self) -> Dict[AdditionalOptionTier, List[Dict]]:
        """추가 옵션 풀 초기화 - 공격력/마법공격력, 방어력/마법방어력을 동급으로 밸런스 조정"""
        return {
            AdditionalOptionTier.BASIC: [
                # 기본 공격 옵션들 (동급)
                {"effect": SpecialEffect.ATTACK_PERCENT, "min_value": 0.03, "max_value": 0.08, "description": "공격력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_ATTACK_PERCENT, "min_value": 0.03, "max_value": 0.08, "description": "마법 공격력 +{:.1%}"},
                # 기본 방어 옵션들 (동급)
                {"effect": SpecialEffect.DEFENSE_PERCENT, "min_value": 0.03, "max_value": 0.08, "description": "방어력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_DEFENSE_PERCENT, "min_value": 0.03, "max_value": 0.08, "description": "마법 방어력 +{:.1%}"},
                # 기타 기본 옵션들
                {"effect": SpecialEffect.HP_PERCENT, "min_value": 0.05, "max_value": 0.12, "description": "체력 +{:.1%}"},
                {"effect": SpecialEffect.MP_PERCENT, "min_value": 0.05, "max_value": 0.12, "description": "마나 +{:.1%}"},
                {"effect": SpecialEffect.CRITICAL_RATE, "min_value": 0.02, "max_value": 0.05, "description": "치명타율 +{:.1%}"},
                {"effect": SpecialEffect.ACCURACY, "min_value": 0.03, "max_value": 0.07, "description": "명중률 +{:.1%}"},
                {"effect": SpecialEffect.EVASION, "min_value": 0.02, "max_value": 0.05, "description": "회피율 +{:.1%}"},
                {"effect": SpecialEffect.BRV_GAIN_RATE, "min_value": 0.05, "max_value": 0.15, "description": "BRV 획득률 +{:.1%}"},
                {"effect": SpecialEffect.ATB_SPEED, "min_value": 0.03, "max_value": 0.08, "description": "ATB 속도 +{:.1%}"},
            ],
            AdditionalOptionTier.ENHANCED: [
                # 강화 공격 옵션들 (동급)
                {"effect": SpecialEffect.ATTACK_PERCENT, "min_value": 0.08, "max_value": 0.15, "description": "공격력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_ATTACK_PERCENT, "min_value": 0.08, "max_value": 0.15, "description": "마법 공격력 +{:.1%}"},
                # 강화 방어 옵션들 (동급)
                {"effect": SpecialEffect.DEFENSE_PERCENT, "min_value": 0.08, "max_value": 0.15, "description": "방어력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_DEFENSE_PERCENT, "min_value": 0.08, "max_value": 0.15, "description": "마법 방어력 +{:.1%}"},
                # 기타 강화 옵션들
                {"effect": SpecialEffect.CRITICAL_DAMAGE, "min_value": 0.08, "max_value": 0.18, "description": "치명타 피해 +{:.1%}"},
                {"effect": SpecialEffect.LIFE_STEAL, "min_value": 0.03, "max_value": 0.08, "description": "생명력 흡수 +{:.1%}"},
                {"effect": SpecialEffect.SKILL_COOLDOWN_REDUCTION, "min_value": 0.05, "max_value": 0.12, "description": "스킬 쿨다운 -{:.1%}"},
                {"effect": SpecialEffect.MANA_COST_REDUCTION, "min_value": 0.05, "max_value": 0.12, "description": "마나 소모 -{:.1%}"},
                {"effect": SpecialEffect.BRV_MAX_MULTIPLIER, "min_value": 0.08, "max_value": 0.20, "description": "최대 BRV +{:.1%}"},
                {"effect": SpecialEffect.BULLET_TIME_EFFICIENCY, "min_value": 0.05, "max_value": 0.15, "description": "불릿타임 효율 +{:.1%}"},
                {"effect": SpecialEffect.FIRE_RESISTANCE, "min_value": 0.08, "max_value": 0.15, "description": "화염 저항 +{:.1%}"},
                {"effect": SpecialEffect.ICE_RESISTANCE, "min_value": 0.08, "max_value": 0.15, "description": "빙결 저항 +{:.1%}"},
            ],
            AdditionalOptionTier.SUPERIOR: [
                # 우수 공격 옵션들 (동급)
                {"effect": SpecialEffect.ATTACK_PERCENT, "min_value": 0.15, "max_value": 0.25, "description": "공격력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_ATTACK_PERCENT, "min_value": 0.15, "max_value": 0.25, "description": "마법 공격력 +{:.1%}"},
                # 우수 방어 옵션들 (동급)
                {"effect": SpecialEffect.DEFENSE_PERCENT, "min_value": 0.15, "max_value": 0.25, "description": "방어력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_DEFENSE_PERCENT, "min_value": 0.15, "max_value": 0.25, "description": "마법 방어력 +{:.1%}"},
                # 기타 우수 옵션들
                {"effect": SpecialEffect.CRITICAL_RATE, "min_value": 0.08, "max_value": 0.15, "description": "치명타율 +{:.1%}"},
                {"effect": SpecialEffect.CRITICAL_DAMAGE, "min_value": 0.18, "max_value": 0.35, "description": "치명타 피해 +{:.1%}"},
                {"effect": SpecialEffect.SPELL_POWER, "min_value": 0.12, "max_value": 0.25, "description": "주문력 +{:.1%}"},
                {"effect": SpecialEffect.CAST_SPEED, "min_value": 0.10, "max_value": 0.20, "description": "시전 속도 +{:.1%}"},
                {"effect": SpecialEffect.BRV_INITIAL_BOOST, "min_value": 0.15, "max_value": 0.30, "description": "초기 BRV +{:.1%}"},
                {"effect": SpecialEffect.ATB_INITIAL_BOOST, "min_value": 0.10, "max_value": 0.25, "description": "초기 ATB +{:.1%}"},
                {"effect": SpecialEffect.EXPERIENCE_BOOST, "min_value": 0.10, "max_value": 0.20, "description": "경험치 획득 +{:.1%}"},
                {"effect": SpecialEffect.GOLD_BOOST, "min_value": 0.10, "max_value": 0.20, "description": "골드 획득 +{:.1%}"},
            ],
            AdditionalOptionTier.PERFECT: [
                # 완벽 공격 옵션들 (동급)
                {"effect": SpecialEffect.ATTACK_PERCENT, "min_value": 0.25, "max_value": 0.40, "description": "공격력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_ATTACK_PERCENT, "min_value": 0.25, "max_value": 0.40, "description": "마법 공격력 +{:.1%}"},
                # 완벽 방어 옵션들 (동급)
                {"effect": SpecialEffect.DEFENSE_PERCENT, "min_value": 0.25, "max_value": 0.40, "description": "방어력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_DEFENSE_PERCENT, "min_value": 0.25, "max_value": 0.40, "description": "마법 방어력 +{:.1%}"},
                # 기타 완벽 옵션들
                {"effect": SpecialEffect.HP_PERCENT, "min_value": 0.20, "max_value": 0.35, "description": "체력 +{:.1%}"},
                {"effect": SpecialEffect.CRITICAL_DAMAGE, "min_value": 0.35, "max_value": 0.60, "description": "치명타 피해 +{:.1%}"},
                {"effect": SpecialEffect.LIFE_STEAL, "min_value": 0.08, "max_value": 0.15, "description": "생명력 흡수 +{:.1%}"},
                {"effect": SpecialEffect.SKILL_COOLDOWN_REDUCTION, "min_value": 0.15, "max_value": 0.25, "description": "스킬 쿨다운 -{:.1%}"},
                {"effect": SpecialEffect.BRV_MAX_MULTIPLIER, "min_value": 0.25, "max_value": 0.45, "description": "최대 BRV +{:.1%}"},
                {"effect": SpecialEffect.BULLET_TIME_DURATION, "min_value": 0.15, "max_value": 0.30, "description": "불릿타임 지속시간 +{:.1%}"},
                {"effect": SpecialEffect.ITEM_DROP_RATE, "min_value": 0.15, "max_value": 0.30, "description": "아이템 드롭률 +{:.1%}"},
                {"effect": SpecialEffect.RARE_DROP_RATE, "min_value": 0.10, "max_value": 0.25, "description": "레어 드롭률 +{:.1%}"},
            ],
            AdditionalOptionTier.LEGENDARY: [
                # 전설 공격 옵션들 (동급)
                {"effect": SpecialEffect.ATTACK_PERCENT, "min_value": 0.40, "max_value": 0.70, "description": "공격력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_ATTACK_PERCENT, "min_value": 0.40, "max_value": 0.70, "description": "마법 공격력 +{:.1%}"},
                # 전설 방어 옵션들 (동급)
                {"effect": SpecialEffect.DEFENSE_PERCENT, "min_value": 0.40, "max_value": 0.70, "description": "방어력 +{:.1%}"},
                {"effect": SpecialEffect.MAGIC_DEFENSE_PERCENT, "min_value": 0.40, "max_value": 0.70, "description": "마법 방어력 +{:.1%}"},
                # 기타 전설 옵션들
                {"effect": SpecialEffect.CRITICAL_RATE, "min_value": 0.15, "max_value": 0.30, "description": "치명타율 +{:.1%}"},
                {"effect": SpecialEffect.CRITICAL_DAMAGE, "min_value": 0.60, "max_value": 1.00, "description": "치명타 피해 +{:.1%}"},
                {"effect": SpecialEffect.SPELL_POWER, "min_value": 0.30, "max_value": 0.60, "description": "주문력 +{:.1%}"},
                {"effect": SpecialEffect.BRV_MAX_MULTIPLIER, "min_value": 0.50, "max_value": 0.80, "description": "최대 BRV +{:.1%}"},
                {"effect": SpecialEffect.BRV_GAIN_RATE, "min_value": 0.25, "max_value": 0.50, "description": "BRV 획득률 +{:.1%}"},
                {"effect": SpecialEffect.ATB_SPEED, "min_value": 0.20, "max_value": 0.40, "description": "ATB 속도 +{:.1%}"},
                {"effect": SpecialEffect.BULLET_TIME_EFFICIENCY, "min_value": 0.25, "max_value": 0.50, "description": "불릿타임 효율 +{:.1%}"},
                {"effect": SpecialEffect.EXPERIENCE_BOOST, "min_value": 0.30, "max_value": 0.60, "description": "경험치 획득 +{:.1%}"},
            ]
        }
    
    def _init_curse_pool(self) -> List[Dict]:
        """저주 옵션 풀 초기화"""
        return [
            {"effect": SpecialEffect.CURSE_WEAKNESS, "min_value": 0.10, "max_value": 0.25, "description": "[저주] 공격력 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_FRAGILITY, "min_value": 0.10, "max_value": 0.25, "description": "[저주] 방어력 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_EXHAUSTION, "min_value": 0.15, "max_value": 0.30, "description": "[저주] 최대 체력 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_DRAIN, "min_value": 0.15, "max_value": 0.30, "description": "[저주] 최대 마나 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_CLUMSINESS, "min_value": 0.08, "max_value": 0.20, "description": "[저주] 명중률 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_SLUGGISHNESS, "min_value": 0.10, "max_value": 0.25, "description": "[저주] 속도 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_MISFORTUNE, "min_value": 0.05, "max_value": 0.15, "description": "[저주] 치명타율 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_INEFFICIENCY, "min_value": 0.10, "max_value": 0.25, "description": "[저주] 스킬 쿨다운 +{:.1%}"},
            {"effect": SpecialEffect.CURSE_WASTE, "min_value": 0.15, "max_value": 0.30, "description": "[저주] 마나 소모 +{:.1%}"},
            {"effect": SpecialEffect.CURSE_BRV_DECAY, "min_value": 0.15, "max_value": 0.35, "description": "[저주] BRV 획득률 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_ATB_DELAY, "min_value": 0.10, "max_value": 0.25, "description": "[저주] ATB 속도 -{:.1%}"},
            {"effect": SpecialEffect.CURSE_BULLET_TIME_DISRUPTION, "min_value": 0.20, "max_value": 0.40, "description": "[저주] 불릿타임 효율 -{:.1%}"},
        ]
    
    def _init_weapon_templates(self) -> Dict[str, Dict]:
        """무기 템플릿 초기화 - 직업 제한 없음으로 변칙 플레이 허용"""
        return {
            # 기본 무기들
            "철검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 15},
                "classes": []  # 직업 제한 없음
            },
            "마법 지팡이": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 10, "magic_attack": 20},
                "classes": []
            },
            "활": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.BOW,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 14},
                "classes": []
            },
            "단검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.DAGGER,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 12},
                "classes": []
            },
            
            # 추가 기본 무기들 (50종)
            "강철검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 22},
                "classes": []
            },
            "은검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 30, "magic_attack": 5},
                "classes": []
            },
            "미스릴검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"attack": 40, "speed": 5},
                "classes": []
            },
            "전투도끼": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.AXE,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 18},
                "classes": []
            },
            "대형도끼": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.AXE,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 28, "speed": -3},
                "classes": []
            },
            "바이킹도끼": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.AXE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 35, "critical_rate": 0.1},
                "classes": []
            },
            "긴창": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SPEAR,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 16, "speed": 2},
                "classes": []
            },
            "기병창": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SPEAR,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 24, "speed": 3},
                "classes": []
            },
            "삼지창": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SPEAR,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 32, "critical_damage": 0.2},
                "classes": []
            },
            "철퇴": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.MACE,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 17, "defense": 2},
                "classes": []
            },
            "전쟁망치": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.MACE,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 26, "defense": 3},
                "classes": []
            },
            "성스러운망치": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.MACE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 33, "magic_attack": 10},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIGHT_DAMAGE, 15, "빛 속성 피해 +15")
                ],
                "classes": []
            },
            "암살단검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.DAGGER,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 19, "speed": 5},
                "classes": []
            },
            "독단검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.DAGGER,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 25, "speed": 7},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.POISON_ON_HIT, 0.25, "독 적용 확률 +25%")
                ],
                "classes": []
            },
            "마법봉": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 12, "magic_attack": 28, "mp": 20},
                "classes": []
            },
            "원소지팡이": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 15, "magic_attack": 35, "mp": 40},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.FIRE_DAMAGE, 10, "화염 피해 +10"),
                    EquipmentEffect(SpecialEffect.ICE_DAMAGE, 10, "빙결 피해 +10")
                ],
                "classes": []
            },
            "장궁": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.BOW,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 21, "speed": -1},
                "classes": []
            },
            "복합궁": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.BOW,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 28, "critical_rate": 0.15},
                "classes": []
            },
            "석궁": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.BOW,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 25, "speed": -2},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.3, "치명타 피해 +30%")
                ],
                "classes": []
            },
            "가죽장갑": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.GLOVES,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 13, "speed": 3},
                "classes": []
            },
            "철갑장갑": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.GLOVES,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 20, "defense": 5},
                "classes": []
            },
            "마법장갑": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.GLOVES,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 18, "magic_attack": 15, "speed": 5},
                "classes": []
            },
            "바드하프": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.HARP,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"magic_attack": 25, "mp": 30},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.15, "경험치 +15%")
                ],
                "classes": []
            },
            "전투하프": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.HARP,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 20, "magic_attack": 30, "mp": 50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CAST_SPEED, 0.2, "시전 속도 +20%")
                ],
                "classes": []
            },
            "머스킷총": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.GUN,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 30, "speed": -3},
                "classes": []
            },
            "권총": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.GUN,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 22, "speed": 2},
                "classes": []
            },
            "마법총": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.GUN,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 25, "magic_attack": 20},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.ARCANE_DAMAGE, 12, "비전 피해 +12")
                ],
                "classes": []
            },
            "마법서": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.BOOK,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"magic_attack": 32, "mp": 60},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.MANA_COST_REDUCTION, 0.1, "마나 소모 -10%")
                ],
                "classes": []
            },
            "고서": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.BOOK,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 38, "mp": 80},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.15, "주문력 +15%"),
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.1, "경험치 +10%")
                ],
                "classes": []
            }
        }
    
    def _init_armor_templates(self) -> Dict[str, Dict]:
        """방어구 템플릿 초기화"""
        return {
            # 기본 방어구들 - 직업 제한 제거
            "가죽 갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"defense": 8, "speed": 2},
                "classes": []  # 직업 제한 없음
            },
            "철 갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"defense": 15, "speed": -2},
                "classes": []
            },
            "마법사 로브": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"defense": 5, "magic_defense": 12, "mp": 30},
                "classes": []
            },
            
            # 추가 방어구들 (50종)
            "강화가죽갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 12, "speed": 3, "dodge_rate": 0.05},
                "classes": []
            },
            "도적의망토": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 10, "speed": 8, "dodge_rate": 0.15},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.STEALTH_BOOST, 0.2, "은신 효과 +20%")
                ],
                "classes": []
            },
            "그림자갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"defense": 15, "speed": 10, "dodge_rate": 0.25},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SHADOW_EMPOWERMENT, 0.15, "그림자 강화 15%"),
                    EquipmentEffect(SpecialEffect.STEALTH_BOOST, 0.3, "은신 효과 +30%")
                ],
                "classes": []
            },
            "강철갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 22, "speed": -1},
                "classes": []
            },
            "기사갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 30, "magic_defense": 10, "hp": 50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.1, "받는 피해 -10%")
                ],
                "classes": []
            },
            "용린갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"defense": 40, "magic_defense": 20, "hp": 100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.FIRE_RESISTANCE, 0.5, "화염 저항 +50%"),
                    EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.15, "받는 피해 -15%")
                ],
                "classes": []
            },
            "견습마법사로브": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 8, "magic_defense": 18, "mp": 50},
                "classes": []
            },
            "대마법사로브": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 12, "magic_defense": 25, "mp": 80, "magic_attack": 10},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.15, "주문력 +15%")
                ],
                "classes": []
            },
            "원소술사로브": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"defense": 15, "magic_defense": 35, "mp": 120, "magic_attack": 20},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.FIRE_DAMAGE, 10, "화염 피해 +10"),
                    EquipmentEffect(SpecialEffect.ICE_DAMAGE, 10, "빙결 피해 +10"),
                    EquipmentEffect(SpecialEffect.LIGHTNING_DAMAGE, 10, "번개 피해 +10")
                ],
                "classes": []
            },
            "사슬갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.MEDIUM,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"defense": 12, "speed": 0},
                "classes": []
            },
            "판금갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 25, "speed": -3},
                "classes": []
            },
            "미스릴갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.MEDIUM,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 20, "magic_defense": 15, "speed": 2},
                "classes": []
            },
            "아다만트갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"defense": 50, "magic_defense": 30, "hp": 150},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.25, "받는 피해 -25%"),
                    EquipmentEffect(SpecialEffect.DAMAGE_REFLECTION, 0.2, "피해 반사 +20%")
                ],
                "classes": []
            },
            "바바리안가죽": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 10, "attack": 5, "speed": 3},
                "classes": []
            },
            "전투복": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"defense": 6, "speed": 4},
                "classes": []
            },
            "닌자복": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 8, "speed": 12, "dodge_rate": 0.2},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.STEALTH_BOOST, 0.4, "은신 효과 +40%"),
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.1, "치명타 확률 +10%")
                ],
                "classes": []
            },
            "성직자복": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 10, "magic_defense": 20, "mp": 60},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIGHT_DAMAGE, 8, "빛 속성 피해 +8")
                ],
                "classes": []
            },
            "대주교복": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 15, "magic_defense": 30, "mp": 100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIGHT_DAMAGE, 15, "빛 속성 피해 +15"),
                    EquipmentEffect(SpecialEffect.HEALING_BOOST, 0.25, "치유 효과 +25%")
                ],
                "classes": []
            },
            "네크로맨서로브": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 12, "magic_defense": 22, "mp": 90},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SHADOW_ECHO, 0.12, "그림자 메아리 12% 확률"),
                    EquipmentEffect(SpecialEffect.LIFE_STEAL, 0.1, "생명력 흡수 +10%")
                ],
                "classes": []
            },
            "드루이드로브": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 14, "magic_defense": 24, "mp": 85, "hp": 30},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EARTH_DAMAGE, 10, "자연 피해 +10"),
                    EquipmentEffect(SpecialEffect.HP_REGENERATION, 5, "체력 재생 +5/턴")
                ],
                "classes": []
            },
            "궁수갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 11, "speed": 5, "critical_rate": 0.05},
                "classes": []
            },
            "레인저갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 16, "speed": 7, "critical_rate": 0.1},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EARTH_DAMAGE, 8, "자연 피해 +8"),
                    EquipmentEffect(SpecialEffect.EVASION, 0.1, "회피율 +10%")
                ],
                "classes": []
            },
            "해적코트": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 9, "speed": 6, "luck": 3},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.GOLD_FIND, 0.15, "골드 획득량 +15%")
                ],
                "classes": []
            },
            "선장코트": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 13, "speed": 8, "luck": 5},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.GOLD_FIND, 0.25, "골드 획득량 +25%"),
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.1, "경험치 +10%")
                ],
                "classes": []
            },
            "바드의상": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 7, "magic_defense": 10, "mp": 40, "speed": 3},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.2, "경험치 +20%")
                ],
                "classes": []
            },
            "마스터바드의상": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.LIGHT,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 11, "magic_defense": 16, "mp": 70, "speed": 5},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.3, "경험치 +30%"),
                    EquipmentEffect(SpecialEffect.CAST_SPEED, 0.15, "시전 속도 +15%")
                ],
                "classes": []
            }
        }
    
    def _init_accessory_templates(self) -> Dict[str, Dict]:
        """장신구 템플릿 초기화 - 직업 제한 없음으로 변칙 플레이 허용"""
        return {
            # 기본 장신구들 - 직업 제한 제거
            "힘의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"attack": 3},
                "classes": []  # 직업 제한 없음
            },
            "민첩의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"speed": 5},
                "classes": []
            },
            "지혜의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"magic_attack": 5},
                "classes": []
            },
            
            # 추가 장신구들 (100종)
            "체력의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"hp": 25},
                "classes": []
            },
            "마나의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"mp": 30},
                "classes": []
            },
            "방어의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.COMMON,
                "base_stats": {"defense": 5},
                "classes": []
            },
            "행운의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"luck": 3},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.05, "치명타 확률 +5%")
                ],
                "classes": []
            },
            "재생의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"hp": 40},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.HP_REGENERATION, 3, "체력 재생 +3/턴")
                ],
                "classes": []
            },
            "흡혈의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 8},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIFE_STEAL, 0.15, "생명력 흡수 +15%")
                ],
                "classes": []
            },
            "원소의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"magic_attack": 12},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.FIRE_DAMAGE, 8, "화염 피해 +8"),
                    EquipmentEffect(SpecialEffect.ICE_DAMAGE, 8, "빙결 피해 +8")
                ],
                "classes": []
            },
            "용의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 15, "magic_attack": 15, "hp": 80},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.FIRE_RESISTANCE, 0.3, "화염 저항 +30%"),
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.25, "치명타 피해 +25%")
                ],
                "classes": []
            },
            "그림자 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"speed": 8, "dodge_rate": 0.1},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SHADOW_STEP, 0.15, "그림자 이동 15% 확률"),
                    EquipmentEffect(SpecialEffect.STEALTH_BOOST, 0.2, "은신 효과 +20%")
                ],
                "classes": []
            },
            "빛의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 10, "magic_defense": 8},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIGHT_DAMAGE, 12, "빛 속성 피해 +12"),
                    EquipmentEffect(SpecialEffect.HEALING_BOOST, 0.2, "치유 효과 +20%")
                ],
                "classes": []
            },
            "자연의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"hp": 60, "mp": 40},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EARTH_DAMAGE, 10, "자연 피해 +10"),
                    EquipmentEffect(SpecialEffect.MP_REGENERATION, 2, "마나 재생 +2/턴")
                ],
                "classes": []
            },
            "번개의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"speed": 10, "magic_attack": 8},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIGHTNING_DAMAGE, 15, "번개 피해 +15"),
                    EquipmentEffect(SpecialEffect.CAST_SPEED, 0.15, "시전 속도 +15%")
                ],
                "classes": []
            },
            "얼음의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 12, "defense": 6},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.ICE_DAMAGE, 18, "빙결 피해 +18"),
                    EquipmentEffect(SpecialEffect.SLOW_ON_HIT, 0.2, "공격 시 둔화 20% 확률")
                ],
                "classes": []
            },
            "독의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 10, "speed": 5},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.POISON_ON_HIT, 0.3, "독 적용 확률 +30%"),
                    EquipmentEffect(SpecialEffect.POISON_RESISTANCE, 0.5, "독 저항 +50%")
                ],
                "classes": []
            },
            "보호의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"defense": 8, "magic_defense": 8},
                "classes": []
            },
            "활력의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"hp": 50, "stamina": 20},
                "classes": []
            },
            "집중의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"mp": 60, "magic_attack": 8},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.MANA_COST_REDUCTION, 0.1, "마나 소모 -10%")
                ],
                "classes": []
            },
            "전투의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 12, "critical_rate": 0.08},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.2, "치명타 피해 +20%")
                ],
                "classes": []
            },
            "마법의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 15, "mp": 80},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.12, "주문력 +12%")
                ],
                "classes": []
            },
            "수호의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"hp": 100, "defense": 15, "magic_defense": 15},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.1, "받는 피해 -10%")
                ],
                "classes": []
            },
            "파괴의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"attack": 20, "magic_attack": 20},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.15, "치명타 확률 +15%"),
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.3, "치명타 피해 +30%")
                ],
                "classes": []
            },
            "시간의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"speed": 15, "mp": 100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CAST_SPEED, 0.25, "시전 속도 +25%"),
                    EquipmentEffect(SpecialEffect.COOLDOWN_REDUCTION, 0.2, "쿨다운 감소 +20%")
                ],
                "classes": []
            },
            "영혼의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"hp": 150, "mp": 150},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.HP_REGENERATION, 8, "체력 재생 +8/턴"),
                    EquipmentEffect(SpecialEffect.MP_REGENERATION, 8, "마나 재생 +8/턴")
                ],
                "classes": []
            },
            "학자의 안경": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLASSES,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"magic_attack": 10, "mp": 40},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.15, "경험치 +15%")
                ],
                "classes": []
            },
            "전투안경": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLASSES,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"critical_rate": 0.12, "accuracy": 0.1},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.25, "치명타 피해 +25%")
                ],
                "classes": []
            },
            "마법안경": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLASSES,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 18, "mp": 70},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.18, "주문력 +18%"),
                    EquipmentEffect(SpecialEffect.MANA_COST_REDUCTION, 0.15, "마나 소모 -15%")
                ],
                "classes": []
            },
            "투시안경": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLASSES,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"luck": 5, "critical_rate": 0.1},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.TREASURE_FIND, 0.3, "보물 발견율 +30%"),
                    EquipmentEffect(SpecialEffect.TRAP_DETECTION, 0.5, "함정 탐지 +50%")
                ],
                "classes": []
            },
            "힘의 벨트": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BELT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"attack": 8, "hp": 30},
                "classes": []
            },
            "민첩의 벨트": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BELT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"speed": 8, "dodge_rate": 0.08},
                "classes": []
            },
            "지혜의 벨트": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BELT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"magic_attack": 10, "mp": 50},
                "classes": []
            },
            "체력의 벨트": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BELT,
                "rarity": EquipmentRarity.UNCOMMON,
                "base_stats": {"hp": 80, "stamina": 30},
                "classes": []
            },
            "마스터 벨트": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BELT,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 12, "magic_attack": 12, "speed": 6},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.ALL_STATS, 5, "모든 스탯 +5")
                ],
                "classes": []
            },
            "용사의 벨트": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BELT,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"attack": 18, "defense": 12, "hp": 100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.12, "받는 피해 -12%"),
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.1, "치명타 확률 +10%")
                ],
                "classes": []
            },
            "대마법사 벨트": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BELT,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"magic_attack": 25, "mp": 120, "magic_defense": 15},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.2, "주문력 +20%"),
                    EquipmentEffect(SpecialEffect.MP_REGENERATION, 5, "마나 재생 +5/턴")
                ],
                "classes": []
            },
            "전설의 벨트": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BELT,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 25, "magic_attack": 25, "hp": 150, "mp": 150},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.ALL_STATS, 10, "모든 스탯 +10"),
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.25, "경험치 +25%")
                ],
                "classes": []
            }
        }
    
    def _init_unique_equipment(self) -> Dict[str, Dict]:
        """유니크 장비 초기화 (기존 + 확장)"""
        unique_items = {
            "엑스칼리버": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 50, "magic_attack": 25},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.15, "치명타율 +15%"),
                    EquipmentEffect(SpecialEffect.LIGHT_DAMAGE, 20, "빛 속성 피해 +20"),
                    EquipmentEffect(SpecialEffect.UNBREAKABLE, 1, "파괴되지 않음")
                ],
                "classes": [],
                "is_unique": True,
                "description": "전설의 성검. 빛의 힘이 깃들어 있어 어둠을 물리친다."
            },
            
            "아르카나 스태프": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"magic_attack": 40, "mp": 100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.MAGE_MANA_EFFICIENCY, 0.25, "마나 효율 +25%"),
                    EquipmentEffect(SpecialEffect.CAST_SPEED, 0.20, "시전 속도 +20%"),
                    EquipmentEffect(SpecialEffect.ARCANE_DAMAGE, 15, "비전 피해 +15")
                ],
                "classes": [],
                "is_unique": True,
                "description": "고대 마법사들이 사용했던 비전의 지팡이. 깊은 마법 지식이 담겨있다."
            },
            
            "그림자 단검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.DAGGER,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 25, "speed": 10},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.ASSASSIN_STEALTH_BONUS, 0.30, "은신 보너스 +30%"),
                    EquipmentEffect(SpecialEffect.POISON_ON_HIT, 0.15, "공격 시 독 15% 확률"),
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.10, "치명타율 +10%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "그림자에서 태어난 단검. 조용하고 치명적인 공격을 가능하게 한다."
            },
            
            # 신규 유니크 아이템들
            "영원의 하프": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.HARP,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"magic_attack": 35, "mp": 80},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.BARD_MELODY_POWER, 0.50, "멜로디 위력 +50%"),
                    EquipmentEffect(SpecialEffect.MP_REGENERATION, 10, "마나 재생 +10"),
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.25, "파티 경험치 +25%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "천상의 선율이 깃든 하프. 들은 자는 모두 치유되고 고무된다."
            },
            
            "천공의 창": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SPEAR,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 45, "speed": 5},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIGHTNING_DAMAGE, 25, "번개 피해 +25"),
                    EquipmentEffect(SpecialEffect.LIGHTNING_CHAIN, 0.30, "30% 확률로 번개 연쇄"),
                    EquipmentEffect(SpecialEffect.SKILL_RANGE, 0.40, "스킬 범위 +40%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "하늘의 번개를 담은 창. 적들을 꿰뚫으며 번개를 퍼뜨린다."
            },
            
            "세계수의 지팡이": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.MYTHIC,
                "base_stats": {"magic_attack": 60, "hp": 100, "mp": 150},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.HP_REGENERATION, 15, "체력 재생 +15"),
                    EquipmentEffect(SpecialEffect.MP_REGENERATION, 15, "마나 재생 +15"),
                    EquipmentEffect(SpecialEffect.EARTH_DAMAGE, 30, "대지 피해 +30"),
                    EquipmentEffect(SpecialEffect.HEAL_ON_KILL, 20, "처치 시 체력 회복 +20")
                ],
                "classes": [],
                "is_unique": True,
                "description": "세계수에서 떨어진 가지로 만든 지팡이. 생명의 힘이 넘쳐흐른다."
            },
            
            "암흑의 총": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.GUN,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"attack": 40, "critical_rate": 0.20},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DARK_DAMAGE, 20, "어둠 피해 +20"),
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.50, "치명타 피해 +50%"),
                    EquipmentEffect(SpecialEffect.SILENCE_CHANCE, 0.15, "침묵 확률 +15%")
                ],
                "classes": [],  # 직업 제한 제거
                "is_unique": True,
                "description": "어둠의 힘으로 만들어진 총. 조용하지만 치명적이다."
            },
            
            # 추가 유니크 장비들 (50종)
            "시간의 검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 40, "speed": 20, "critical_rate": 0.2},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.TIME_STOP, 0.05, "시간 정지 5% 확률"),
                    EquipmentEffect(SpecialEffect.CAST_SPEED, 0.3, "시전 속도 +30%"),
                    EquipmentEffect(SpecialEffect.COOLDOWN_REDUCTION, 0.25, "쿨다운 감소 +25%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "시간을 조작하는 신비한 검. 시간의 흐름을 멈출 수 있다."
            },
            "공간의 지팡이": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"magic_attack": 45, "mp": 200, "magic_defense": 20},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.TELEPORT, 0.1, "순간이동 10% 확률"),
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.35, "주문력 +35%"),
                    EquipmentEffect(SpecialEffect.MP_REGENERATION, 10, "마나 재생 +10/턴")
                ],
                "classes": [],
                "is_unique": True,
                "description": "공간을 조작하는 마법 지팡이. 순간이동의 힘을 담고 있다."
            },
            "운명의 활": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.BOW,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 38, "luck": 10, "critical_rate": 0.25},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LUCKY_SHOT, 0.15, "행운의 화살 15% 확률"),
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.5, "치명타 피해 +50%"),
                    EquipmentEffect(SpecialEffect.TREASURE_FIND, 0.4, "보물 발견율 +40%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "운명을 가르는 활. 행운의 화살이 적을 관통한다."
            },
            "영혼의 갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"defense": 35, "magic_defense": 35, "hp": 200, "mp": 200},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SOUL_SHIELD, 0.2, "영혼 보호막 20% 확률"),
                    EquipmentEffect(SpecialEffect.HP_REGENERATION, 10, "체력 재생 +10/턴"),
                    EquipmentEffect(SpecialEffect.MP_REGENERATION, 10, "마나 재생 +10/턴")
                ],
                "classes": [],
                "is_unique": True,
                "description": "영혼의 힘으로 만들어진 갑옷. 생명과 마나를 동시에 보호한다."
            },
            "불사조의 깃털": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"hp": 300, "fire_resistance": 0.8},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.PHOENIX_REBIRTH, 1, "부활 1회"),
                    EquipmentEffect(SpecialEffect.FIRE_IMMUNITY, 1, "화염 면역"),
                    EquipmentEffect(SpecialEffect.FIRE_DAMAGE, 25, "화염 피해 +25")
                ],
                "classes": [],
                "is_unique": True,
                "description": "불사조의 깃털로 만든 목걸이. 죽음에서 되살아나는 힘을 준다."
            },
            "바다의 삼지창": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SPEAR,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 42, "magic_attack": 30, "water_damage": 20},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.TIDAL_WAVE, 0.08, "해일 8% 확률"),
                    EquipmentEffect(SpecialEffect.WATER_MASTERY, 0.3, "수속성 숙련도 +30%"),
                    EquipmentEffect(SpecialEffect.HEALING_BOOST, 0.25, "치유 효과 +25%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "바다의 신이 사용했던 삼지창. 바다의 모든 힘을 담고 있다."
            },
            "대지의 망치": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.MACE,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 50, "defense": 20, "earth_damage": 25},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EARTHQUAKE, 0.1, "지진 10% 확률"),
                    EquipmentEffect(SpecialEffect.STUN_ON_HIT, 0.15, "공격 시 기절 15% 확률"),
                    EquipmentEffect(SpecialEffect.EARTH_DAMAGE, 30, "대지 피해 +30")
                ],
                "classes": [],
                "is_unique": True,
                "description": "대지의 힘이 깃든 망치. 땅을 흔들어 적을 무너뜨린다."
            },
            
            # 관통력 및 고정 피해 관련 새로운 아이템들
            "복수의 검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"attack": 35, "critical_rate": 0.15},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LOST_HP_DAMAGE, 0.17, "잃은 체력 17% 비례 피해"),
                    EquipmentEffect(SpecialEffect.PHYSICAL_PENETRATION, 15, "물리 관통력 +15"),
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.3, "치명타 피해 +30%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "상처받을수록 강해지는 검. 잃은 체력에 비례해 더 큰 피해를 준다."
            },
            
            "절망의 지팡이": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"magic_attack": 40, "mp": 100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LOST_HP_DAMAGE, 0.13, "잃은 체력 13% 비례 마법 피해"),
                    EquipmentEffect(SpecialEffect.MAGIC_PENETRATION, 20, "마법 관통력 +20"),
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.25, "주문력 +25%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "절망이 깊을수록 강력해지는 지팡이. 고통을 마법의 힘으로 바꾼다."
            },
            
            "생명력 망치": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.MACE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 30, "hp": 150},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CURRENT_HP_DAMAGE, 0.15, "현재 체력 15% 비례 피해"),
                    EquipmentEffect(SpecialEffect.TRUE_DAMAGE, 10, "고정 피해 +10"),
                    EquipmentEffect(SpecialEffect.LIFE_STEAL, 0.2, "생명력 흡수 20%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "생명력이 충만할수록 강해지는 망치. 체력에 비례한 신성한 피해를 준다."
            },
            
            "생명력 구슬": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.WAND,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 25, "hp": 200, "mp": 80},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CURRENT_HP_DAMAGE, 0.12, "현재 체력 12% 비례 마법 피해"),
                    EquipmentEffect(SpecialEffect.TRUE_DAMAGE, 8, "고정 피해 +8"),
                    EquipmentEffect(SpecialEffect.HP_REGENERATION, 5, "체력 재생 +5")
                ],
                "classes": [],
                "is_unique": True,
                "description": "생명의 에너지가 응축된 구슬. 건강할수록 더 강력한 마법을 사용할 수 있다."
            },
            
            "포식자의 발톱": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.GLOVES,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"attack": 32, "speed": 15, "critical_rate": 0.2},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.ENEMY_LOW_HP_DAMAGE, 0.5, "적 저체력시 피해 +50%"),
                    EquipmentEffect(SpecialEffect.PHYSICAL_PENETRATION, 12, "물리 관통력 +12"),
                    EquipmentEffect(SpecialEffect.LIFE_STEAL, 0.15, "생명력 흡수 15%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "약한 먹이를 노리는 포식자의 발톱. 상대가 약할수록 더 치명적이다."
            },
            
            "처형자의 도끼": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.AXE,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"attack": 45, "critical_damage": 0.4},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.ENEMY_LOW_HP_DAMAGE, 0.75, "적 저체력시 피해 +75%"),
                    EquipmentEffect(SpecialEffect.ARMOR_IGNORE, 0.3, "방어력 무시 30%"),
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.1, "치명타율 +10%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "처형을 위해 만들어진 도끼. 약해진 적에게는 절대적인 위력을 발휘한다."
            },
            
            "관통 건틀릿": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLOVES,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 20, "defense": 15},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.PHYSICAL_PENETRATION, 25, "물리 관통력 +25"),
                    EquipmentEffect(SpecialEffect.MAGIC_PENETRATION, 15, "마법 관통력 +15"),
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.08, "치명타율 +8%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "모든 방어를 관통하는 건틀릿. 어떤 갑옷도 무의미하게 만든다."
            },
            
            "공허 수정": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.ORB,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"magic_attack": 30, "mp": 100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.MAGIC_PENETRATION, 30, "마법 관통력 +30"),
                    EquipmentEffect(SpecialEffect.TRUE_DAMAGE, 15, "고정 피해 +15"),
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.2, "주문력 +20%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "공허의 힘이 응축된 수정. 모든 마법 방어를 무시하고 관통한다."
            },
            
            "진실 피해 증폭기": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.CHARM,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.TRUE_DAMAGE, 25, "고정 피해 +25"),
                    EquipmentEffect(SpecialEffect.PERCENTAGE_DAMAGE, 0.05, "비율 피해 +5%"),
                    EquipmentEffect(SpecialEffect.ARMOR_IGNORE, 0.5, "방어력 무시 50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "진실만이 남는 증폭기. 모든 거짓된 방어를 꿰뚫어 본다."
            },
            
            "광전사의 가면": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.HELMET,
                "rarity": EquipmentRarity.EPIC,
                "base_stats": {"attack": 25, "hp": -50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CONDITIONAL_PENETRATION, 0.3, "체력 50% 이하시 관통력 +30"),
                    EquipmentEffect(SpecialEffect.LOST_HP_DAMAGE, 0.27, "잃은 체력 27% 비례 피해"),
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.5, "치명타 피해 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "광전사의 분노가 깃든 가면. 상처받을수록 더 강력해진다."
            },
            
            "사냥꾼의 조준경": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLASSES,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"accuracy": 0.2, "critical_rate": 0.15},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CONDITIONAL_PENETRATION, 0.25, "치명타시 관통력 +25"),
                    EquipmentEffect(SpecialEffect.ENEMY_HIGH_HP_DAMAGE, 0.3, "적 고체력시 피해 +30%"),
                    EquipmentEffect(SpecialEffect.SIGHT_RANGE, 0.5, "시야 범위 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "완벽한 사냥을 위한 조준경. 적의 약점을 정확히 노린다."
            },
            
            "적응형 갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.MEDIUM,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"defense": 30, "magic_defense": 30, "hp": 150},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.PERCENTAGE_DAMAGE, 0.03, "받은 피해의 3%를 고정 피해로 반사"),
                    EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.15, "피해 감소 15%"),
                    EquipmentEffect(SpecialEffect.ALL_STATS, 5, "모든 스탯 +5")
                ],
                "classes": [],
                "is_unique": True,
                "description": "상황에 따라 적응하는 갑옷. 받은 피해를 학습해 더 강해진다."
            },
            "바람의 단검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.DAGGER,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 35, "speed": 25, "dodge_rate": 0.2},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.WIND_SLASH, 0.12, "바람 베기 12% 확률"),
                    EquipmentEffect(SpecialEffect.DOUBLE_ATTACK, 0.2, "연속 공격 20% 확률"),
                    EquipmentEffect(SpecialEffect.STEALTH_BOOST, 0.3, "은신 효과 +30%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "바람처럼 빠른 단검. 적이 알아채기 전에 베어낸다."
            },
            "별의 로브": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"magic_attack": 40, "mp": 250, "magic_defense": 30},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.STARFALL, 0.08, "별똥별 8% 확률"),
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.4, "주문력 +40%"),
                    EquipmentEffect(SpecialEffect.MANA_COST_REDUCTION, 0.25, "마나 소모 -25%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "별빛으로 짜여진 로브. 하늘의 별들이 도움을 준다."
            },
            "무한의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"all_stats": 15},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.INFINITE_MANA, 0.05, "무한 마나 5% 확률"),
                    EquipmentEffect(SpecialEffect.ALL_STATS, 20, "모든 스탯 +20"),
                    EquipmentEffect(SpecialEffect.EXPERIENCE_BOOST, 0.5, "경험치 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "무한의 힘을 담은 반지. 모든 것을 초월한다."
            },
            "악마의 계약서": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BOOK,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"attack": 30, "magic_attack": 30, "hp": -50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DEMON_PACT, 1, "악마의 계약"),
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.3, "치명타 확률 +30%"),
                    EquipmentEffect(SpecialEffect.LIFE_STEAL, 0.25, "생명력 흡수 +25%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "악마와의 계약서. 강력한 힘을 주지만 대가가 따른다."
            },
            "천사의 날개": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.WINGS,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"speed": 20, "magic_defense": 25, "light_resistance": 0.9},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.FLIGHT, 1, "비행 능력"),
                    EquipmentEffect(SpecialEffect.DIVINE_PROTECTION, 0.1, "신의 가호 10% 확률"),
                    EquipmentEffect(SpecialEffect.HEALING_BOOST, 0.5, "치유 효과 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "천사의 날개. 하늘을 날 수 있는 신성한 힘을 준다."
            },
            "용의 심장": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.HEART,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"hp": 500, "attack": 25, "fire_resistance": 0.7},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DRAGON_BREATH, 0.1, "용의 숨결 10% 확률"),
                    EquipmentEffect(SpecialEffect.FIRE_IMMUNITY, 1, "화염 면역"),
                    EquipmentEffect(SpecialEffect.INTIMIDATION, 0.2, "위압 20% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "고대 용의 심장. 용의 모든 힘을 담고 있다."
            },
            "크라켄의 촉수": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.WHIP,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"attack": 38, "reach": 3, "water_damage": 20},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.TENTACLE_GRAB, 0.15, "촉수 포획 15% 확률"),
                    EquipmentEffect(SpecialEffect.MULTI_HIT, 0.2, "다중 타격 20% 확률"),
                    EquipmentEffect(SpecialEffect.WATER_MASTERY, 0.4, "수속성 숙련도 +40%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "바다 괴물 크라켄의 촉수. 적을 붙잡아 끌어당긴다."
            },
            "리치의 지팡이": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"magic_attack": 50, "mp": 300, "hp": -100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.UNDEAD_MASTERY, 0.5, "언데드 숙련도 +50%"),
                    EquipmentEffect(SpecialEffect.LIFE_DRAIN, 0.2, "생명력 흡수 20% 확률"),
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.6, "주문력 +60%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "리치 왕의 지팡이. 강력하지만 생명력을 갉아먹는다."
            },
            "페가수스의 편자": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BOOTS,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"speed": 30, "dodge_rate": 0.25},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.SKY_WALK, 1, "공중 보행"),
                    EquipmentEffect(SpecialEffect.WIND_MASTERY, 0.3, "바람 숙련도 +30%"),
                    EquipmentEffect(SpecialEffect.MOVEMENT_SPEED, 0.5, "이동 속도 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "페가수스의 편자. 하늘을 걸을 수 있게 해준다."
            },
            "미다스의 장갑": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLOVES,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"luck": 15, "gold_find": 2.0},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.GOLDEN_TOUCH, 0.1, "황금 터치 10% 확률"),
                    EquipmentEffect(SpecialEffect.TREASURE_FIND, 1.0, "보물 발견율 +100%"),
                    EquipmentEffect(SpecialEffect.GOLD_BOOST, 3.0, "골드 획득 +300%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "미다스 왕의 장갑. 만지는 것을 황금으로 바꾼다."
            },
            "아틀라스의 어깨갑": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"defense": 40, "hp": 400, "carry_capacity": 1000},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.WORLD_BEARER, 1, "세계 운반자"),
                    EquipmentEffect(SpecialEffect.IMMOVABLE, 0.3, "불굴 30% 확률"),
                    EquipmentEffect(SpecialEffect.STRENGTH_BOOST, 0.5, "힘 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "아틀라스의 어깨갑. 세상의 무게를 견딜 수 있다."
            },
            "헤르메스의 신발": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BOOTS,
                "rarity": EquipmentRarity.LEGENDARY,
                "base_stats": {"speed": 35, "dodge_rate": 0.3},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.TELEPORT, 0.15, "순간이동 15% 확률"),
                    EquipmentEffect(SpecialEffect.HASTE, 0.2, "가속 20% 확률"),
                    EquipmentEffect(SpecialEffect.MOVEMENT_SPEED, 1.0, "이동 속도 +100%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "헤르메스의 신발. 바람보다 빠르게 움직일 수 있다."
            }
        }
        return unique_items
    
    def _init_cursed_equipment(self) -> Dict[str, Dict]:
        """저주받은 장비 초기화 - 강력하지만 부작용이 있는 장비들"""
        return {
            "흡혈의 검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"attack": 45},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIFE_STEAL, 0.30, "생명력 흡수 +30%"),
                    EquipmentEffect(SpecialEffect.VAMPIRIC_CURSE, -20, "최대 체력 -20")
                ],
                "classes": [],  # 직업 제한 없음
                "is_unique": True,
                "description": "강력한 생명력 흡수 능력을 가지지만, 사용자의 생명력을 갉아먹는다."
            },
            
            "광전사의 대검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"attack": 60},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.BERSERK_MODE, 0.50, "공격력 +50%"),
                    EquipmentEffect(SpecialEffect.DEFENSE_PERCENT, -0.30, "방어력 -30%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "전투에서 광폭한 힘을 주지만, 방어를 포기해야 한다."
            },
            
            # 추가 저주받은 장비들 (15종)
            "절망의 갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.HEAVY,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"defense": 50, "speed": -15, "luck": -10},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DESPAIR_AURA, 0.2, "절망 오라 20% 확률"),
                    EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.3, "받는 피해 -30%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "절망에 빠진 자들의 갑옷. 강력한 방어력을 주지만 희망을 앗아간다."
            },
            "파멸의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"attack": 25, "hp": -200},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DOOM_STRIKE, 0.1, "파멸의 일격 10% 확률"),
                    EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 1.0, "치명타 피해 +100%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "파멸을 부르는 반지. 엄청난 힘을 주지만 생명을 갉아먹는다."
            },
            "저주받은 왕관": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.HELMET,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"magic_attack": 40, "mp": 150, "sanity": -50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.MADNESS, 0.15, "광기 15% 확률"),
                    EquipmentEffect(SpecialEffect.SPELL_POWER, 0.5, "주문력 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "저주받은 왕의 왕관. 강력한 마법력을 주지만 정신을 잠식한다."
            },
            "고통의 채찍": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.WHIP,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"attack": 35, "hp": -50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.PAIN_SHARE, 0.3, "고통 공유 30% 확률"),
                    EquipmentEffect(SpecialEffect.LIFE_STEAL, 0.2, "생명력 흡수 +20%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "고통을 즐기는 채찍. 적과 자신 모두에게 고통을 준다."
            },
            "망자의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"magic_attack": 30, "hp": -150},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.UNDEAD_MASTERY, 0.4, "언데드 숙련도 +40%"),
                    EquipmentEffect(SpecialEffect.NECROMANCY, 0.15, "네크로맨시 15% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "망자들의 영혼이 깃든 목걸이. 죽음과 친해지게 해준다."
            },
            "악마의 계약서": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BOOK,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"all_stats": 20, "soul": -100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.DEMON_PACT, 1, "악마의 계약"),
                    EquipmentEffect(SpecialEffect.POWER_AT_COST, 0.5, "대가를 치르는 힘 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "악마와의 계약서. 모든 능력이 향상되지만 영혼을 담보로 한다."
            },
            "광기의 마스크": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.HELMET,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"magic_attack": 35, "sanity": -100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.INSANITY_BOOST, 0.3, "광기 증폭 30%"),
                    EquipmentEffect(SpecialEffect.CHAOS_MAGIC, 0.2, "혼돈 마법 20% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "광기에 빠진 마법사의 마스크. 강력한 마법을 쓸 수 있지만 정신이 무너진다."
            },
            "저주받은 성배": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.CHALICE,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"hp": 300, "mp": 200, "regeneration": -10},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CURSED_HEALING, 0.3, "저주받은 치유 30% 확률"),
                    EquipmentEffect(SpecialEffect.LIFE_DRAIN_AURA, 0.1, "생명력 흡수 오라 10% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "저주받은 성배. 큰 생명력을 주지만 자연 회복을 방해한다."
            },
            "배신자의 단검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.DAGGER,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"attack": 40, "critical_rate": 0.3, "loyalty": -50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.BACKSTAB_BOOST, 0.5, "배후 공격 +50%"),
                    EquipmentEffect(SpecialEffect.BETRAYAL_STRIKE, 0.1, "배신의 일격 10% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "배신자가 사용했던 단검. 강력하지만 때로는 주인을 배신한다."
            },
            "탐욕의 장갑": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLOVES,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"gold_find": 3.0, "karma": -100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.GREED_CURSE, 1, "탐욕의 저주"),
                    EquipmentEffect(SpecialEffect.GOLD_BOOST, 5.0, "골드 획득 +500%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "탐욕에 빠진 자의 장갑. 엄청난 부를 가져다주지만 영혼을 타락시킨다."
            }
        }
    
    def _init_risk_return_equipment(self) -> Dict[str, Dict]:
        """리스크-리턴 장비 초기화 - 도박성이 강한 장비들"""
        return {
            "운명의 주사위 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.CURSED,
                "base_stats": {"luck": 10},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LUCKY_CURSE, 0.10, "10% 확률로 극운, 2% 확률로 극흉"),
                    EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.15, "치명타율 +15%"),
                    EquipmentEffect(SpecialEffect.RARE_DROP_RATE, 0.50, "희귀 아이템 드롭률 +50%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "운명을 도박으로 거는 자를 위한 목걸이. 큰 행운이 따르지만 때로는 재앙도 함께 온다."
            },
            
            # 추가 리스크-리턴 장비들 (20종)
            "도박꾼의 검": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.SWORD,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 25, "luck": 5},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.GAMBLER_STRIKE, 0.2, "도박 공격 20% 확률 (2배 피해 또는 빗나감)"),
                    EquipmentEffect(SpecialEffect.CRITICAL_GAMBLE, 0.15, "치명타 도박 15% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "도박꾼이 사용하던 검. 큰 승부를 걸 때 진가를 발휘한다."
            },
            "변덕스러운 지팡이": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.STAFF,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 30, "mp": 100},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.RANDOM_SPELL, 0.25, "랜덤 주문 25% 확률"),
                    EquipmentEffect(SpecialEffect.MANA_CHAOS, 0.1, "마나 혼돈 10% 확률 (0 또는 2배)")
                ],
                "classes": [],
                "is_unique": True,
                "description": "예측할 수 없는 마법을 발동하는 지팡이. 때로는 기적을, 때로는 재앙을 부른다."
            },
            "위험한 갑옷": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.MEDIUM,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"defense": 20, "dodge_rate": 0.15},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.RISKY_DEFENSE, 0.3, "위험한 방어 30% 확률 (완전 회피 또는 2배 피해)"),
                    EquipmentEffect(SpecialEffect.ADRENALINE_RUSH, 0.2, "아드레날린 분출 20% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "위험을 즐기는 자의 갑옷. 극한 상황에서 놀라운 힘을 발휘한다."
            },
            "혼돈의 반지": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.RING,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"all_stats": 5},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.CHAOS_BOOST, 0.2, "혼돈 증폭 20% 확률 (모든 스탯 2배 또는 절반)"),
                    EquipmentEffect(SpecialEffect.RANDOM_EFFECT, 0.1, "랜덤 효과 10% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "혼돈의 힘이 깃든 반지. 예측할 수 없는 변화를 가져온다."
            },
            "모험가의 부츠": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.BOOTS,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"speed": 15, "luck": 8},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.ADVENTURE_SPIRIT, 0.15, "모험 정신 15% 확률 (보상 2배 또는 함정)"),
                    EquipmentEffect(SpecialEffect.TREASURE_HUNT, 0.25, "보물 사냥 25% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "진정한 모험가의 부츠. 위험한 길일수록 큰 보상이 기다린다."
            },
            "광인의 마스크": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.HELMET,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 20, "sanity": -20},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.MADNESS_POWER, 0.2, "광기의 힘 20% 확률 (주문력 3배 또는 실패)"),
                    EquipmentEffect(SpecialEffect.INSANE_INSIGHT, 0.1, "광적 통찰 10% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "광인이 쓰던 마스크. 정신을 잃을수록 강해진다."
            },
            "폭발하는 망치": {
                "type": EquipmentType.WEAPON,
                "category": WeaponCategory.MACE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 35, "hp": -30},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EXPLOSIVE_HIT, 0.15, "폭발 타격 15% 확률 (광역 피해 + 자폭 피해)"),
                    EquipmentEffect(SpecialEffect.BERSERKER_RAGE, 0.2, "광전사 분노 20% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "폭발하는 망치. 적을 박살내지만 자신도 다친다."
            },
            "운명의 화살통": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.QUIVER,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"attack": 15, "critical_rate": 0.1},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.FATE_ARROW, 0.2, "운명의 화살 20% 확률 (즉사 또는 빗나감)"),
                    EquipmentEffect(SpecialEffect.LUCKY_SHOT, 0.15, "행운의 사격 15% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "운명이 깃든 화살통. 한 발로 모든 것을 결정한다."
            },
            "시간 도둑의 시계": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.WATCH,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"speed": 20, "mp": -50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.TIME_STEAL, 0.1, "시간 도둑질 10% 확률 (추가 턴 또는 턴 상실)"),
                    EquipmentEffect(SpecialEffect.HASTE, 0.25, "가속 25% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "시간을 훔치는 신비한 시계. 때로는 시간을 얻고, 때로는 잃는다."
            },
            "생명의 도박사 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.NECKLACE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"hp": 100, "regeneration": 5},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.LIFE_GAMBLE, 0.15, "생명 도박 15% 확률 (체력 회복 또는 손실)"),
                    EquipmentEffect(SpecialEffect.RESURRECTION_CHANCE, 0.05, "부활 확률 5%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "생명을 걸고 도박하는 목걸이. 죽음의 문턱에서 기적을 부른다."
            },
            "예측불가 로브": {
                "type": EquipmentType.ARMOR,
                "category": ArmorCategory.ROBE,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_defense": 25, "mp": 150},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.UNPREDICTABLE_MAGIC, 0.2, "예측불가 마법 20% 확률"),
                    EquipmentEffect(SpecialEffect.SPELL_REFLECTION, 0.1, "주문 반사 10% 확률")
                ],
                "classes": [],
                "is_unique": True,
                "description": "예측할 수 없는 마법이 깃든 로브. 무엇이 일어날지 아무도 모른다."
            },
            "위험한 실험 장갑": {
                "type": EquipmentType.ACCESSORY,
                "category": AccessoryCategory.GLOVES,
                "rarity": EquipmentRarity.RARE,
                "base_stats": {"magic_attack": 25, "hp": -50},
                "special_effects": [
                    EquipmentEffect(SpecialEffect.EXPERIMENT_BOOST, 0.2, "실험 증폭 20% 확률 (효과 2배 또는 역효과)"),
                    EquipmentEffect(SpecialEffect.ALCHEMY_MASTERY, 0.3, "연금술 숙련도 +30%")
                ],
                "classes": [],
                "is_unique": True,
                "description": "위험한 실험을 위한 장갑. 성공하면 큰 성과를, 실패하면 큰 피해를 준다."
            }
        }
    
    def _init_set_equipment(self) -> Dict[str, List[Dict]]:
        """세트 장비 초기화 - 다양한 세트 장비들과 세트 효과 정의"""
        return {
            # 용의 세트 - 공격력과 방어력 균형
            "용의 세트": [
                {
                    "name": "용의 검",
                    "type": EquipmentType.WEAPON,
                    "category": WeaponCategory.SWORD,
                    "rarity": EquipmentRarity.EPIC,
                    "base_stats": {"attack": 35, "critical_rate": 0.1},
                    "set_piece_id": 1,
                    "set_name": "용의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.FIRE_DAMAGE, 15, "화염 피해 +15")
                    ]
                },
                {
                    "name": "용의 갑옷",
                    "type": EquipmentType.ARMOR,
                    "category": ArmorCategory.HEAVY,
                    "rarity": EquipmentRarity.EPIC,
                    "base_stats": {"defense": 30, "hp": 100},
                    "set_piece_id": 2,
                    "set_name": "용의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.FIRE_RESISTANCE, 0.2, "화염 저항 +20%")
                    ]
                },
                {
                    "name": "용의 목걸이",
                    "type": EquipmentType.ACCESSORY,
                    "category": AccessoryCategory.NECKLACE,
                    "rarity": EquipmentRarity.EPIC,
                    "base_stats": {"hp": 80, "mp": 50},
                    "set_piece_id": 3,
                    "set_name": "용의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.HP_REGENERATION, 5, "체력 재생 +5/턴")
                    ]
                }
            ],
            
            # 암살자의 세트 - 속도와 치명타 특화
            "암살자의 세트": [
                {
                    "name": "그림자 단검",
                    "type": EquipmentType.WEAPON,
                    "category": WeaponCategory.DAGGER,
                    "rarity": EquipmentRarity.RARE,
                    "base_stats": {"attack": 28, "speed": 8, "critical_rate": 0.15},
                    "set_piece_id": 1,
                    "set_name": "암살자의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.STEALTH_ATTACK, 0.3, "은신 공격 확률 +30%")
                    ]
                },
                {
                    "name": "그림자 망토",
                    "type": EquipmentType.ARMOR,
                    "category": ArmorCategory.LIGHT,
                    "rarity": EquipmentRarity.RARE,
                    "base_stats": {"defense": 18, "speed": 12, "evasion": 0.2},
                    "set_piece_id": 2,
                    "set_name": "암살자의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.DODGE_CHANCE, 0.15, "회피 확률 +15%")
                    ]
                },
                {
                    "name": "그림자 반지",
                    "type": EquipmentType.ACCESSORY,
                    "category": AccessoryCategory.RING,
                    "rarity": EquipmentRarity.RARE,
                    "base_stats": {"speed": 10, "critical_damage": 0.25},
                    "set_piece_id": 3,
                    "set_name": "암살자의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.2, "치명타 피해 +20%")
                    ]
                }
            ],
            
            # 마법사의 세트 - 마법력과 마나 특화
            "마법사의 세트": [
                {
                    "name": "현자의 지팡이",
                    "type": EquipmentType.WEAPON,
                    "category": WeaponCategory.STAFF,
                    "rarity": EquipmentRarity.EPIC,
                    "base_stats": {"attack": 20, "magic_attack": 45, "mp": 100},
                    "set_piece_id": 1,
                    "set_name": "마법사의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.MANA_EFFICIENCY, 0.2, "마나 효율 +20%")
                    ]
                },
                {
                    "name": "현자의 로브",
                    "type": EquipmentType.ARMOR,
                    "category": ArmorCategory.ROBE,
                    "rarity": EquipmentRarity.EPIC,
                    "base_stats": {"defense": 15, "magic_attack": 25, "mp": 150},
                    "set_piece_id": 2,
                    "set_name": "마법사의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.SPELL_POWER, 0.15, "주문력 +15%")
                    ]
                },
                {
                    "name": "현자의 오브",
                    "type": EquipmentType.ACCESSORY,
                    "category": AccessoryCategory.ORB,
                    "rarity": EquipmentRarity.EPIC,
                    "base_stats": {"magic_attack": 30, "mp": 120},
                    "set_piece_id": 3,
                    "set_name": "마법사의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.MANA_REGENERATION, 10, "마나 재생 +10/턴")
                    ]
                }
            ],
            
            # 성기사의 세트 - 방어력과 신성 피해 특화
            "성기사의 세트": [
                {
                    "name": "성스러운 검",
                    "type": EquipmentType.WEAPON,
                    "category": WeaponCategory.SWORD,
                    "rarity": EquipmentRarity.LEGENDARY,
                    "base_stats": {"attack": 40, "magic_attack": 20, "defense": 10},
                    "set_piece_id": 1,
                    "set_name": "성기사의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.LIGHT_DAMAGE, 25, "빛 속성 피해 +25"),
                        EquipmentEffect(SpecialEffect.UNDEAD_DAMAGE, 0.5, "언데드 추가 피해 +50%")
                    ]
                },
                {
                    "name": "성스러운 갑옷",
                    "type": EquipmentType.ARMOR,
                    "category": ArmorCategory.HEAVY,
                    "rarity": EquipmentRarity.LEGENDARY,
                    "base_stats": {"defense": 45, "hp": 200, "magic_resistance": 0.3},
                    "set_piece_id": 2,
                    "set_name": "성기사의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.15, "받는 피해 -15%"),
                        EquipmentEffect(SpecialEffect.CURSE_IMMUNITY, 1.0, "저주 면역")
                    ]
                },
                {
                    "name": "성스러운 방패",
                    "type": EquipmentType.ACCESSORY,
                    "category": AccessoryCategory.SHIELD,
                    "rarity": EquipmentRarity.LEGENDARY,
                    "base_stats": {"defense": 25, "hp": 150, "block_chance": 0.25},
                    "set_piece_id": 3,
                    "set_name": "성기사의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.BLOCK_CHANCE, 0.2, "방어 확률 +20%"),
                        EquipmentEffect(SpecialEffect.HEALING_BOOST, 0.3, "치유 효과 +30%")
                    ]
                }
            ],
            
            # 궁수의 세트 - 원거리 공격과 정확도 특화
            "궁수의 세트": [
                {
                    "name": "엘븐 장궁",
                    "type": EquipmentType.WEAPON,
                    "category": WeaponCategory.BOW,
                    "rarity": EquipmentRarity.RARE,
                    "base_stats": {"attack": 32, "critical_rate": 0.2, "accuracy": 0.15},
                    "set_piece_id": 1,
                    "set_name": "궁수의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.PIERCING_SHOT, 0.25, "관통 사격 확률 +25%")
                    ]
                },
                {
                    "name": "엘븐 가죽갑옷",
                    "type": EquipmentType.ARMOR,
                    "category": ArmorCategory.MEDIUM,
                    "rarity": EquipmentRarity.RARE,
                    "base_stats": {"defense": 22, "speed": 8, "evasion": 0.15},
                    "set_piece_id": 2,
                    "set_name": "궁수의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.MOVEMENT_SPEED, 0.2, "이동 속도 +20%")
                    ]
                },
                {
                    "name": "엘븐 화살통",
                    "type": EquipmentType.ACCESSORY,
                    "category": AccessoryCategory.QUIVER,
                    "rarity": EquipmentRarity.RARE,
                    "base_stats": {"attack": 15, "critical_damage": 0.3},
                    "set_piece_id": 3,
                    "set_name": "궁수의 세트",
                    "special_effects": [
                        EquipmentEffect(SpecialEffect.MULTI_SHOT, 0.15, "다중 사격 확률 +15%")
                    ]
                }
            ]
        }
    
    def generate_equipment(self, name: str, level: int = 1, enhancement: int = 0) -> Optional[Equipment]:
        """장비 생성 - 일반 장비와 세트 장비 모두 지원"""
        # 모든 템플릿에서 검색 (세트 장비 포함)
        template = None
        
        # 일반 템플릿에서 검색
        for templates in [self.weapon_templates, self.armor_templates, 
                         self.accessory_templates, self.unique_equipment, 
                         self.cursed_equipment, self.risk_return_equipment]:
            if name in templates:
                template = templates[name]
                break
        
        # 세트 장비에서 검색
        if not template:
            for set_name, set_pieces in self.set_equipment.items():
                for piece in set_pieces:
                    if piece["name"] == name:
                        template = piece
                        break
                if template:
                    break
        
        if not template:
            return None
        
        # 장비 생성
        equipment = Equipment(
            name=name,
            equipment_type=template["type"],
            rarity=template.get("rarity", EquipmentRarity.COMMON),
            level=level,
            stats=template["base_stats"].copy(),
            enhancement_level=enhancement,
            is_unique=template.get("is_unique", False)
        )
        
        # 카테고리 설정
        if "category" in template:
            equipment.category = template["category"]
        
        # 특수 효과 추가
        if "special_effects" in template:
            equipment.special_effects = template["special_effects"].copy()
        
        # 세트 장비 정보 추가
        if "set_name" in template:
            equipment.set_name = template["set_name"]
            equipment.set_piece_id = template["set_piece_id"]
        
        # 추가 옵션 생성 (시작 아이템이 아닌 경우에만)
        if not template.get("is_starting_item", False):
            additional_options = self.generate_additional_options(equipment)
            equipment.additional_options = additional_options
        else:
            # 시작 아이템은 추가 옵션 없음 고정
            equipment.additional_options = []
        
        # 무게 계산 (시작 아이템은 무게 0으로 간주)
        if template.get("is_starting_item", False):
            equipment.weight = 0
        else:
            equipment.weight = equipment.calculate_weight()
        
        return equipment
    
    def generate_random_equipment(self, level: int = 1, rarity: EquipmentRarity = None) -> Equipment:
        """랜덤 장비 생성"""
        if rarity is None:
            # 희귀도 랜덤 결정
            rand = random.random()
            if rand < 0.5:
                rarity = EquipmentRarity.COMMON
            elif rand < 0.8:
                rarity = EquipmentRarity.UNCOMMON
            elif rand < 0.95:
                rarity = EquipmentRarity.RARE
            elif rand < 0.99:
                rarity = EquipmentRarity.EPIC
            else:
                rarity = EquipmentRarity.LEGENDARY
        
        # 장비 타입 랜덤 선택
        equipment_type = random.choice([EquipmentType.WEAPON, EquipmentType.ARMOR, EquipmentType.ACCESSORY])
        
        # 해당 타입의 템플릿에서 랜덤 선택
        if equipment_type == EquipmentType.WEAPON:
            template_name = random.choice(list(self.weapon_templates.keys()))
        elif equipment_type == EquipmentType.ARMOR:
            template_name = random.choice(list(self.armor_templates.keys()))
        else:
            template_name = random.choice(list(self.accessory_templates.keys()))
        
        equipment = self.generate_equipment(template_name, level)
        if equipment:
            equipment.rarity = rarity
            # 희귀도에 따른 스탯 보정 (30~60% 감소 적용)
            reduction_factor = self._get_equipment_reduction_factor(rarity)
            for stat, value in equipment.stats.items():
                adjusted_value = int(value * rarity.multiplier * reduction_factor)
                equipment.stats[stat] = max(1, adjusted_value)  # 최소값 1 보장
            
            # 추가 옵션 재생성 (랜덤 장비는 항상 추가 옵션 생성)
            additional_options = self.generate_additional_options(equipment)
            equipment.additional_options = additional_options
            
            # 무게 재계산
            equipment.weight = equipment.calculate_weight()
        
        return equipment
    
    def get_starting_equipment_for_class(self, character_class: str) -> List[Equipment]:
        """직업별 시작 장비 생성"""
        starting_equipment = []
        
        # 각 템플릿에서 해당 직업에 맞는 장비 찾기
        for templates in [self.weapon_templates, self.armor_templates, self.accessory_templates]:
            for name, template in templates.items():
                if character_class in template.get("classes", []):
                    # 템플릿을 복사해 시작 아이템 플래그를 명시
                    template = template.copy()
                    template["is_starting_item"] = True
                    # 임시로 템플릿에 주입하기 위해 generate_equipment 사용 전에 표식
                    # generate_equipment는 내부에서 template 조회하므로, 사본을 반영하기 위해 직접 생성 경로로 우회 불가
                    # 대신 생성 후 플래그/무게/옵션을 재보정한다.
                    equipment = self.generate_equipment(name)
                    if equipment:
                        equipment.is_starting_item = True
                        # 시작 아이템은 무게 0, 추가 옵션 제거
                        try:
                            equipment.weight = 0
                            equipment.additional_options = []
                        except Exception:
                            pass
                        starting_equipment.append(equipment)
                    break  # 각 타입별로 하나씩만
        
        return starting_equipment
    
    def generate_set_equipment(self, set_name: str, level: int = 1, enhancement: int = 0) -> List[Equipment]:
        """세트 장비 전체 생성"""
        if set_name not in self.set_equipment:
            return []
        
        set_pieces = []
        for piece_template in self.set_equipment[set_name]:
            equipment = self.generate_equipment(piece_template["name"], level, enhancement)
            if equipment:
                set_pieces.append(equipment)
        
        return set_pieces
    
    def get_available_sets(self) -> List[str]:
        """사용 가능한 세트 목록 반환"""
        return list(self.set_equipment.keys())
    
    def get_set_info(self, set_name: str) -> Dict[str, Any]:
        """세트 정보 반환"""
        if set_name not in self.set_equipment:
            return {}
        
        set_info = {
            "name": set_name,
            "pieces": [],
            "bonuses": {
                "2_piece": [],
                "3_piece": []
            }
        }
        
        # 세트 구성품 정보
        for piece in self.set_equipment[set_name]:
            piece_info = {
                "name": piece["name"],
                "type": piece["type"].value,
                "rarity": piece["rarity"].value,
                "stats": piece["base_stats"]
            }
            set_info["pieces"].append(piece_info)
        
        # 세트 보너스 정보 (더미 매니저로 효과 확인)
        dummy_manager = EquipmentManager()
        two_piece_effects = dummy_manager._get_set_bonus_effects(set_name, 2)
        three_piece_effects = dummy_manager._get_set_bonus_effects(set_name, 3)
        
        set_info["bonuses"]["2_piece"] = [effect.description for effect in two_piece_effects]
        set_info["bonuses"]["3_piece"] = [effect.description for effect in three_piece_effects]
        
        return set_info

# ===== 장비 관리자 =====

class EquipmentManager:
    """장비 관리자 클래스"""
    
    def __init__(self):
        self.generator = UnifiedEquipmentGenerator()
        self.equipped_items: Dict[str, Optional[Equipment]] = {
            "weapon": None,
            "armor": None,
            "accessory1": None,
            "accessory2": None,
            "accessory3": None
        }
    
    def equip_item(self, equipment: Equipment, slot: str = None) -> bool:
        """장비 착용"""
        if slot is None:
            slot = self._determine_slot(equipment)
        
        if slot not in self.equipped_items:
            return False
        
        # 장신구의 경우 빈 슬롯 찾기
        if equipment.equipment_type == EquipmentType.ACCESSORY and slot.startswith("accessory"):
            for i in range(1, 4):
                accessory_slot = f"accessory{i}"
                if self.equipped_items[accessory_slot] is None:
                    self.equipped_items[accessory_slot] = equipment
                    return True
            return False  # 모든 장신구 슬롯이 차있음
        
        self.equipped_items[slot] = equipment
        return True
    
    def unequip_item(self, slot: str) -> Optional[Equipment]:
        """장비 해제"""
        if slot not in self.equipped_items:
            return None
        
        equipment = self.equipped_items[slot]
        self.equipped_items[slot] = None
        return equipment
    
    def _determine_slot(self, equipment: Equipment) -> str:
        """장비 타입에 따른 슬롯 결정"""
        if equipment.equipment_type == EquipmentType.WEAPON:
            return "weapon"
        elif equipment.equipment_type == EquipmentType.ARMOR:
            return "armor"
        elif equipment.equipment_type == EquipmentType.ACCESSORY:
            return "accessory1"  # 첫 번째 장신구 슬롯
        return ""
    
    def get_total_stats(self) -> Dict[str, int]:
        """착용 중인 모든 장비의 총 스탯 계산"""
        total_stats = {}
        
        for equipment in self.equipped_items.values():
            if equipment is not None:
                equipment_stats = equipment.get_total_stats()
                for stat, value in equipment_stats.items():
                    total_stats[stat] = total_stats.get(stat, 0) + value
        
        return total_stats
    
    def get_all_effects(self) -> List[EquipmentEffect]:
        """착용 중인 모든 장비의 특수 효과 반환"""
        all_effects = []
        
        for equipment in self.equipped_items.values():
            if equipment is not None:
                all_effects.extend(equipment.special_effects)
        
        return all_effects
    
    def check_set_bonuses(self) -> Dict[str, int]:
        """세트 효과 확인"""
        set_counts = {}
        
        for equipment in self.equipped_items.values():
            if equipment is not None and equipment.set_name:
                set_counts[equipment.set_name] = set_counts.get(equipment.set_name, 0) + 1
        
        return set_counts
    
    def get_set_effects(self) -> List[EquipmentEffect]:
        """활성화된 세트 효과 반환"""
        set_counts = self.check_set_bonuses()
        set_effects = []
        
        for set_name, count in set_counts.items():
            effects = self._get_set_bonus_effects(set_name, count)
            set_effects.extend(effects)
        
        return set_effects
    
    def _get_set_bonus_effects(self, set_name: str, piece_count: int) -> List[EquipmentEffect]:
        """세트별 보너스 효과 정의"""
        effects = []
        
        if set_name == "용의 세트":
            if piece_count >= 2:
                effects.append(EquipmentEffect(SpecialEffect.FIRE_DAMAGE, 20, "[2세트] 화염 피해 +20"))
                effects.append(EquipmentEffect(SpecialEffect.FIRE_RESISTANCE, 0.15, "[2세트] 화염 저항 +15%"))
            if piece_count >= 3:
                effects.append(EquipmentEffect(SpecialEffect.ATTACK_BOOST, 0.2, "[3세트] 공격력 +20%"))
                effects.append(EquipmentEffect(SpecialEffect.DEFENSE_BOOST, 0.2, "[3세트] 방어력 +20%"))
                effects.append(EquipmentEffect(SpecialEffect.DRAGON_SLAYER, 1.0, "[3세트] 용족 특효"))
        
        elif set_name == "암살자의 세트":
            if piece_count >= 2:
                effects.append(EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.15, "[2세트] 치명타율 +15%"))
                effects.append(EquipmentEffect(SpecialEffect.STEALTH_ATTACK, 0.2, "[2세트] 은신 공격 확률 +20%"))
            if piece_count >= 3:
                effects.append(EquipmentEffect(SpecialEffect.SPEED_BOOST, 0.25, "[3세트] 속도 +25%"))
                effects.append(EquipmentEffect(SpecialEffect.CRITICAL_DAMAGE, 0.3, "[3세트] 치명타 피해 +30%"))
                effects.append(EquipmentEffect(SpecialEffect.SHADOW_STEP, 1.0, "[3세트] 그림자 이동"))
        
        elif set_name == "마법사의 세트":
            if piece_count >= 2:
                effects.append(EquipmentEffect(SpecialEffect.MAGIC_ATTACK_BOOST, 0.2, "[2세트] 마법 공격력 +20%"))
                effects.append(EquipmentEffect(SpecialEffect.MANA_EFFICIENCY, 0.15, "[2세트] 마나 효율 +15%"))
            if piece_count >= 3:
                effects.append(EquipmentEffect(SpecialEffect.SPELL_POWER, 0.25, "[3세트] 주문력 +25%"))
                effects.append(EquipmentEffect(SpecialEffect.MANA_REGENERATION, 15, "[3세트] 마나 재생 +15/턴"))
                effects.append(EquipmentEffect(SpecialEffect.ARCANE_MASTERY, 1.0, "[3세트] 비전 숙련"))
        
        elif set_name == "성기사의 세트":
            if piece_count >= 2:
                effects.append(EquipmentEffect(SpecialEffect.LIGHT_DAMAGE, 30, "[2세트] 빛 속성 피해 +30"))
                effects.append(EquipmentEffect(SpecialEffect.DAMAGE_REDUCTION, 0.1, "[2세트] 받는 피해 -10%"))
            if piece_count >= 3:
                effects.append(EquipmentEffect(SpecialEffect.HEALING_BOOST, 0.4, "[3세트] 치유 효과 +40%"))
                effects.append(EquipmentEffect(SpecialEffect.UNDEAD_DAMAGE, 0.75, "[3세트] 언데드 추가 피해 +75%"))
                effects.append(EquipmentEffect(SpecialEffect.DIVINE_PROTECTION, 1.0, "[3세트] 신성한 보호"))
        
        elif set_name == "궁수의 세트":
            if piece_count >= 2:
                effects.append(EquipmentEffect(SpecialEffect.CRITICAL_RATE, 0.1, "[2세트] 치명타율 +10%"))
                effects.append(EquipmentEffect(SpecialEffect.ACCURACY_BOOST, 0.2, "[2세트] 명중률 +20%"))
            if piece_count >= 3:
                effects.append(EquipmentEffect(SpecialEffect.PIERCING_SHOT, 0.3, "[3세트] 관통 사격 확률 +30%"))
                effects.append(EquipmentEffect(SpecialEffect.MULTI_SHOT, 0.25, "[3세트] 다중 사격 확률 +25%"))
                effects.append(EquipmentEffect(SpecialEffect.EAGLE_EYE, 1.0, "[3세트] 독수리의 눈"))
        
        return effects
    
    def get_total_stats_with_sets(self) -> Dict[str, Any]:
        """세트 효과를 포함한 총 스탯 계산"""
        total_stats = self.get_total_stats()
        set_effects = self.get_set_effects()
        
        # 세트 효과 적용
        for effect in set_effects:
            if effect.effect_type == SpecialEffect.ATTACK_BOOST:
                current_attack = total_stats.get('attack', 0)
                total_stats['attack'] = int(current_attack * (1 + effect.value))
            elif effect.effect_type == SpecialEffect.DEFENSE_BOOST:
                current_defense = total_stats.get('defense', 0)
                total_stats['defense'] = int(current_defense * (1 + effect.value))
            elif effect.effect_type == SpecialEffect.MAGIC_ATTACK_BOOST:
                current_magic_attack = total_stats.get('magic_attack', 0)
                total_stats['magic_attack'] = int(current_magic_attack * (1 + effect.value))
            elif effect.effect_type == SpecialEffect.SPEED_BOOST:
                current_speed = total_stats.get('speed', 0)
                total_stats['speed'] = int(current_speed * (1 + effect.value))
        
        return total_stats
    
    def get_all_effects_with_sets(self) -> List[EquipmentEffect]:
        """장비 효과와 세트 효과를 모두 포함한 효과 목록 반환"""
        equipment_effects = self.get_all_effects()
        set_effects = self.get_set_effects()
        
        return equipment_effects + set_effects

# ===== 전역 인스턴스 =====

# 전역 장비 생성기
unified_equipment_generator = UnifiedEquipmentGenerator()

# ===== 장비 효과 적용 시스템 =====

class EquipmentEffectApplier:
    """장비 효과 적용 클래스"""
    
    @staticmethod
    def apply_equipment_effects(character_stats: Dict[str, Any], equipment_manager: EquipmentManager) -> Dict[str, Any]:
        """장비 효과를 캐릭터 스탯에 적용"""
        modified_stats = character_stats.copy()
        
        # 기본 스탯 보너스 적용
        equipment_stats = equipment_manager.get_total_stats()
        for stat, value in equipment_stats.items():
            if stat in modified_stats:
                modified_stats[stat] += value
        
        # 특수 효과 적용
        all_effects = equipment_manager.get_all_effects()
        
        for effect in all_effects:
            EquipmentEffectApplier._apply_single_effect(modified_stats, effect)
        
        # 세트 효과 적용
        set_bonuses = equipment_manager.check_set_bonuses()
        for set_name, count in set_bonuses.items():
            EquipmentEffectApplier._apply_set_bonus(modified_stats, set_name, count)
        
        return modified_stats
    
    @staticmethod
    def _apply_single_effect(stats: Dict[str, Any], effect: EquipmentEffect):
        """단일 효과 적용"""
        effect_type = effect.effect_type
        value = effect.value
        
        # 퍼센트 증가 효과
        if effect_type == SpecialEffect.ATTACK_PERCENT:
            stats['attack'] = int(stats.get('attack', 0) * (1 + value))
        elif effect_type == SpecialEffect.MAGIC_ATTACK_PERCENT:
            stats['magic_attack'] = int(stats.get('magic_attack', 0) * (1 + value))
        elif effect_type == SpecialEffect.DEFENSE_PERCENT:
            stats['defense'] = int(stats.get('defense', 0) * (1 + value))
        elif effect_type == SpecialEffect.MAGIC_DEFENSE_PERCENT:
            stats['magic_defense'] = int(stats.get('magic_defense', 0) * (1 + value))
        elif effect_type == SpecialEffect.HP_PERCENT:
            stats['hp'] = int(stats.get('hp', 0) * (1 + value))
            stats['max_hp'] = int(stats.get('max_hp', 0) * (1 + value))
        elif effect_type == SpecialEffect.MP_PERCENT:
            stats['mp'] = int(stats.get('mp', 0) * (1 + value))
            stats['max_mp'] = int(stats.get('max_mp', 0) * (1 + value))
        elif effect_type == SpecialEffect.SPEED_PERCENT:
            stats['speed'] = int(stats.get('speed', 0) * (1 + value))
        
        # 고정값 증가 효과
        elif effect_type == SpecialEffect.ATTACK_FLAT:
            stats['attack'] = stats.get('attack', 0) + int(value)
        elif effect_type == SpecialEffect.MAGIC_ATTACK_FLAT:
            stats['magic_attack'] = stats.get('magic_attack', 0) + int(value)
        elif effect_type == SpecialEffect.DEFENSE_FLAT:
            stats['defense'] = stats.get('defense', 0) + int(value)
        elif effect_type == SpecialEffect.MAGIC_DEFENSE_FLAT:
            stats['magic_defense'] = stats.get('magic_defense', 0) + int(value)
        elif effect_type == SpecialEffect.HP_FLAT:
            stats['hp'] = stats.get('hp', 0) + int(value)
            stats['max_hp'] = stats.get('max_hp', 0) + int(value)
        elif effect_type == SpecialEffect.MP_FLAT:
            stats['mp'] = stats.get('mp', 0) + int(value)
            stats['max_mp'] = stats.get('max_mp', 0) + int(value)
        elif effect_type == SpecialEffect.SPEED_FLAT:
            stats['speed'] = stats.get('speed', 0) + int(value)
        
        # 전투 관련 효과
        elif effect_type == SpecialEffect.CRITICAL_RATE:
            stats['critical_rate'] = stats.get('critical_rate', 0.0) + value
        elif effect_type == SpecialEffect.CRITICAL_DAMAGE:
            stats['critical_damage'] = stats.get('critical_damage', 1.5) + value
        elif effect_type == SpecialEffect.ACCURACY:
            stats['accuracy'] = stats.get('accuracy', 0.9) + value
        elif effect_type == SpecialEffect.EVASION:
            stats['evasion'] = stats.get('evasion', 0.0) + value
        elif effect_type == SpecialEffect.LIFE_STEAL:
            stats['life_steal'] = stats.get('life_steal', 0.0) + value
        elif effect_type == SpecialEffect.BLOCK_CHANCE:
            stats['block_chance'] = stats.get('block_chance', 0.0) + value
        
        # 원소 피해 효과
        elif effect_type in [SpecialEffect.FIRE_DAMAGE, SpecialEffect.ICE_DAMAGE, 
                           SpecialEffect.LIGHTNING_DAMAGE, SpecialEffect.EARTH_DAMAGE,
                           SpecialEffect.WIND_DAMAGE, SpecialEffect.WATER_DAMAGE,
                           SpecialEffect.LIGHT_DAMAGE, SpecialEffect.DARK_DAMAGE,
                           SpecialEffect.POISON_DAMAGE, SpecialEffect.ARCANE_DAMAGE]:
            element_key = f"{effect_type.value}_bonus"
            stats[element_key] = stats.get(element_key, 0) + int(value)
        
        # 원소 저항 효과
        elif effect_type in [SpecialEffect.FIRE_RESISTANCE, SpecialEffect.ICE_RESISTANCE,
                           SpecialEffect.LIGHTNING_RESISTANCE, SpecialEffect.EARTH_RESISTANCE,
                           SpecialEffect.WIND_RESISTANCE, SpecialEffect.WATER_RESISTANCE,
                           SpecialEffect.LIGHT_RESISTANCE, SpecialEffect.DARK_RESISTANCE,
                           SpecialEffect.POISON_RESISTANCE, SpecialEffect.ARCANE_RESISTANCE]:
            resistance_key = f"{effect_type.value}_value"
            stats[resistance_key] = stats.get(resistance_key, 0.0) + value
        
        # 특별 효과
        elif effect_type == SpecialEffect.EXPERIENCE_BOOST:
            stats['exp_multiplier'] = stats.get('exp_multiplier', 1.0) + value
        elif effect_type == SpecialEffect.GOLD_BOOST:
            stats['gold_multiplier'] = stats.get('gold_multiplier', 1.0) + value
        elif effect_type == SpecialEffect.ITEM_DROP_RATE:
            stats['item_drop_rate'] = stats.get('item_drop_rate', 1.0) + value
        elif effect_type == SpecialEffect.RARE_DROP_RATE:
            stats['rare_drop_rate'] = stats.get('rare_drop_rate', 1.0) + value
        
        # 스킬 관련 효과
        elif effect_type == SpecialEffect.SKILL_COOLDOWN_REDUCTION:
            stats['cooldown_reduction'] = stats.get('cooldown_reduction', 0.0) + value
        elif effect_type == SpecialEffect.MANA_COST_REDUCTION:
            stats['mana_cost_reduction'] = stats.get('mana_cost_reduction', 0.0) + value
        elif effect_type == SpecialEffect.CAST_SPEED:
            stats['cast_speed'] = stats.get('cast_speed', 1.0) + value
        elif effect_type == SpecialEffect.SPELL_POWER:
            stats['spell_power'] = stats.get('spell_power', 1.0) + value
        
        # 재생 효과
        elif effect_type == SpecialEffect.HP_REGENERATION:
            stats['hp_regen'] = stats.get('hp_regen', 0) + int(value)
        elif effect_type == SpecialEffect.MP_REGENERATION:
            stats['mp_regen'] = stats.get('mp_regen', 0) + int(value)
    
    @staticmethod
    def _apply_set_bonus(stats: Dict[str, Any], set_name: str, count: int):
        """세트 효과 적용"""
        # 용의 세트 예시
        if set_name == "용의 세트":
            if count >= 2:
                stats['attack'] = stats.get('attack', 0) + 10
                stats['defense'] = stats.get('defense', 0) + 10
            if count >= 3:
                stats['fire_damage_bonus'] = stats.get('fire_damage_bonus', 0) + 20
                stats['fire_resistance_value'] = stats.get('fire_resistance_value', 0.0) + 0.2
    
    def generate_additional_options(self, equipment: Equipment, force_count: int = None) -> List[EquipmentEffect]:
        """추가 옵션 생성"""
        additional_options = []
        
        # 추가 옵션 개수 결정 (최소 1개, 최대 3개)
        if force_count is not None:
            option_count = min(max(force_count, 1), 3)
        else:
            # 확률에 따른 추가 옵션 개수 결정
            rand = random.random()
            if rand < 0.6:  # 60% - 1개
                option_count = 1
            elif rand < 0.85:  # 25% - 2개
                option_count = 2
            else:  # 15% - 3개
                option_count = 3
        
        # 저주 확률 체크 (매우 낮은 확률)
        curse_chance = 0.02  # 2% 확률
        
        for i in range(option_count):
            # 저주 여부 결정
            if random.random() < curse_chance:
                curse_option = self._generate_curse_option()
                additional_options.append(curse_option)
                equipment.is_cursed = True
            else:
                # 일반 추가 옵션 생성
                tier = self._determine_option_tier(equipment.rarity)
                option = self._generate_additional_option(tier)
                additional_options.append(option)
        
        return additional_options



    def _determine_option_tier(self, equipment_rarity: EquipmentRarity) -> AdditionalOptionTier:
        """장비 등급에 따른 추가 옵션 등급 결정 (낮은 등급에서 높은 등급 옵션 극도로 제한)"""
        base_probabilities = {
            EquipmentRarity.COMMON: {
                AdditionalOptionTier.BASIC: 0.98,
                AdditionalOptionTier.ENHANCED: 0.02,
                AdditionalOptionTier.SUPERIOR: 0.00,
                AdditionalOptionTier.PERFECT: 0.00,
                AdditionalOptionTier.LEGENDARY: 0.00
            },
            EquipmentRarity.UNCOMMON: {
                AdditionalOptionTier.BASIC: 0.85,
                AdditionalOptionTier.ENHANCED: 0.14,
                AdditionalOptionTier.SUPERIOR: 0.01,
                AdditionalOptionTier.PERFECT: 0.00,
                AdditionalOptionTier.LEGENDARY: 0.00
            },
            EquipmentRarity.RARE: {
                AdditionalOptionTier.BASIC: 0.60,
                AdditionalOptionTier.ENHANCED: 0.30,
                AdditionalOptionTier.SUPERIOR: 0.09,
                AdditionalOptionTier.PERFECT: 0.01,
                AdditionalOptionTier.LEGENDARY: 0.00
            },
            EquipmentRarity.EPIC: {
                AdditionalOptionTier.BASIC: 0.35,
                AdditionalOptionTier.ENHANCED: 0.40,
                AdditionalOptionTier.SUPERIOR: 0.20,
                AdditionalOptionTier.PERFECT: 0.04,
                AdditionalOptionTier.LEGENDARY: 0.01
            },
            EquipmentRarity.LEGENDARY: {
                AdditionalOptionTier.BASIC: 0.15,
                AdditionalOptionTier.ENHANCED: 0.30,
                AdditionalOptionTier.SUPERIOR: 0.35,
                AdditionalOptionTier.PERFECT: 0.15,
                AdditionalOptionTier.LEGENDARY: 0.05
            },
            EquipmentRarity.MYTHIC: {
                AdditionalOptionTier.BASIC: 0.05,
                AdditionalOptionTier.ENHANCED: 0.15,
                AdditionalOptionTier.SUPERIOR: 0.30,
                AdditionalOptionTier.PERFECT: 0.35,
                AdditionalOptionTier.LEGENDARY: 0.15
            }
        }
        
        probabilities = base_probabilities.get(equipment_rarity, base_probabilities[EquipmentRarity.COMMON])
        
        rand = random.random()
        cumulative = 0.0
        
        for tier, prob in probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                return tier
        
        return AdditionalOptionTier.BASIC
    
    def _generate_additional_option(self, tier: AdditionalOptionTier) -> EquipmentEffect:
        """특정 등급의 추가 옵션 생성"""
        option_pool = self.additional_option_pool[tier]
        option_template = random.choice(option_pool)
        
        # 값 범위 내에서 랜덤 생성
        min_val = option_template["min_value"]
        max_val = option_template["max_value"]
        value = random.uniform(min_val, max_val)
        
        # 설명 포맷팅
        description = f"[{tier.korean_name}] {option_template['description'].format(value)}"
        
        return EquipmentEffect(
            effect_type=option_template["effect"],
            value=value,
            description=description
        )
    
    def _generate_curse_option(self) -> EquipmentEffect:
        """저주 옵션 생성"""
        curse_template = random.choice(self.curse_pool)
        
        # 값 범위 내에서 랜덤 생성
        min_val = curse_template["min_value"]
        max_val = curse_template["max_value"]
        value = random.uniform(min_val, max_val)
        
        # 설명 포맷팅
        description = curse_template["description"].format(value)
        
        return EquipmentEffect(
            effect_type=curse_template["effect"],
            value=value,
            description=description
        )
    
    def reroll_additional_option(self, equipment: Equipment, option_index: int) -> bool:
        """추가 옵션 리롤 (저주는 리롤 불가)"""
        if option_index >= len(equipment.additional_options):
            return False
        
        current_option = equipment.additional_options[option_index]
        
        # 저주 옵션은 리롤 불가
        if any(curse_effect.value in current_option.effect_type.value for curse_effect in [
            SpecialEffect.CURSE_WEAKNESS, SpecialEffect.CURSE_FRAGILITY, SpecialEffect.CURSE_EXHAUSTION,
            SpecialEffect.CURSE_DRAIN, SpecialEffect.CURSE_CLUMSINESS, SpecialEffect.CURSE_SLUGGISHNESS,
            SpecialEffect.CURSE_MISFORTUNE, SpecialEffect.CURSE_INEFFICIENCY, SpecialEffect.CURSE_WASTE,
            SpecialEffect.CURSE_BRV_DECAY, SpecialEffect.CURSE_ATB_DELAY, SpecialEffect.CURSE_BULLET_TIME_DISRUPTION
        ]):
            return False
        
        # 기존 옵션의 등급을 파악하여 같은 등급 또는 더 좋은 등급으로 리롤
        current_tier = self._get_option_tier_from_description(current_option.description)
        
        # 75% 확률로 같은 등급, 20% 확률로 한 등급 상승, 5% 확률로 두 등급 상승
        rand = random.random()
        if rand < 0.75:
            new_tier = current_tier
        elif rand < 0.95:
            new_tier = self._upgrade_tier(current_tier, 1)
        else:
            new_tier = self._upgrade_tier(current_tier, 2)
        
        # 새로운 옵션 생성
        new_option = self._generate_additional_option(new_tier)
        equipment.additional_options[option_index] = new_option
        
        return True
    
    def _get_option_tier_from_description(self, description: str) -> AdditionalOptionTier:
        """설명에서 옵션 등급 추출"""
        for tier in AdditionalOptionTier:
            if f"[{tier.korean_name}]" in description:
                return tier
        return AdditionalOptionTier.BASIC
    
    def _upgrade_tier(self, current_tier: AdditionalOptionTier, levels: int) -> AdditionalOptionTier:
        """등급 상승"""
        tiers = list(AdditionalOptionTier)
        current_index = tiers.index(current_tier)
        new_index = min(current_index + levels, len(tiers) - 1)
        return tiers[new_index]
    
    def _get_equipment_reduction_factor(self, rarity: EquipmentRarity) -> float:
        """장비 등급에 따른 효과 감소 계수 (30~60% 감소)"""
        reduction_map = {
            EquipmentRarity.COMMON: 0.70,      # 30% 감소
            EquipmentRarity.UNCOMMON: 0.65,    # 35% 감소
            EquipmentRarity.RARE: 0.60,        # 40% 감소
            EquipmentRarity.EPIC: 0.50,        # 50% 감소
            EquipmentRarity.LEGENDARY: 0.45,   # 55% 감소
            EquipmentRarity.MYTHIC: 0.40       # 60% 감소
        }
        return reduction_map.get(rarity, 0.70)

# 호환성을 위한 별칭들
EquipmentGenerator = UnifiedEquipmentGenerator
equipment_generator = unified_equipment_generator
equipment_effect_applier = EquipmentEffectApplier()