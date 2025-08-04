#!/usr/bin/env python3
"""
게임 밸런스 시스템
- 명중률/회피율 공식 (최대 회피율 75%)
- 장비 밸런스 시스템
- 속성 시스템 (기본 무속성)
"""

import random
import math
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class EquipmentType(Enum):
    """장비 타입"""
    WEAPON = "무기"
    ARMOR = "방어구"
    ACCESSORY = "장신구"

class WeaponCategory(Enum):
    """무기 종류 (각 타입별 동일한 개수)"""
    # 근접 무기 (8개)
    SWORD = "검"
    AXE = "도끼"
    SPEAR = "창"
    MACE = "둔기"
    DAGGER = "단검"
    STAFF = "지팡이"
    WAND = "마법봉"
    FIST = "권투글러브"
    
    # 원거리 무기 (4개)
    BOW = "활"
    CROSSBOW = "석궁"
    GUN = "총"
    THROWING = "투척무기"

class ArmorCategory(Enum):
    """방어구 종류 (각 부위별 동일한 개수)"""
    # 상체 방어구 (4개)
    HEAVY_ARMOR = "중갑옷"
    LIGHT_ARMOR = "경갑옷"
    ROBE = "로브"
    LEATHER = "가죽갑옷"
    
    # 하체 방어구 (4개)
    HEAVY_GREAVES = "중갑 각반"
    LIGHT_GREAVES = "경갑 각반"
    CLOTH_PANTS = "천 바지"
    LEATHER_PANTS = "가죽 바지"
    
    # 머리 방어구 (4개)
    HELMET = "투구"
    CAP = "모자"
    HOOD = "후드"
    CIRCLET = "서클릿"

class AccessoryCategory(Enum):
    """장신구 종류 (각 타입별 동일한 개수)"""
    # 목걸이류 (4개)
    NECKLACE = "목걸이"
    AMULET = "부적"
    PENDANT = "펜던트"
    CHAIN = "체인"
    
    # 반지류 (4개)
    RING = "반지"
    SIGNET = "인장"
    BAND = "밴드"
    SEAL = "봉인반지"
    
    # 기타 (4개)
    EARRING = "귀걸이"
    BRACELET = "팔찌"
    BELT = "벨트"
    CHARM = "행운의부적"  # charm과 amulet 구분

class ElementType(Enum):
    """속성 타입 (기본 무속성)"""
    NEUTRAL = "무속성"  # 기본 속성
    FIRE = "화염"
    ICE = "빙결"
    LIGHTNING = "번개"
    EARTH = "대지"
    WIND = "바람"
    WATER = "물"
    LIGHT = "빛"
    DARK = "어둠"
    POISON = "독"

class CombatFormulas:
    """전투 공식들"""
    
    @staticmethod
    def calculate_hit_chance(attacker_accuracy: int, target_evasion: int) -> float:
        """명중률 계산 (최대 회피율 75% 제한)"""
        # 기본 명중률 90%
        base_hit_rate = 90.0
        
        # 정확도와 회피력의 차이
        accuracy_diff = attacker_accuracy - target_evasion
        
        # 정확도 차이에 따른 명중률 보정
        hit_rate = base_hit_rate + (accuracy_diff * 0.5)
        
        # 최소 25% 명중률 보장, 최대 95% 명중률 제한
        hit_rate = max(25.0, min(95.0, hit_rate))
        
        return hit_rate  # 퍼센트로 반환
    
    @staticmethod
    def calculate_evasion_rate(target_evasion: int, attacker_accuracy: int) -> float:
        """회피율 계산 (최대 75% 제한)"""
        # 기본 회피율 계산
        base_evasion = 15.0  # 기본 회피율 15%
        
        # 회피력과 명중력의 차이
        evasion_diff = target_evasion - attacker_accuracy
        
        # 회피력 차이에 따른 회피율 보정
        evasion_rate = base_evasion + (evasion_diff * 0.3)
        
        # 최소 5% 회피율, 최대 75% 회피율 제한
        evasion_rate = max(5.0, min(75.0, evasion_rate))
        
        return evasion_rate  # 퍼센트로 반환
    
    @staticmethod
    def calculate_damage(attacker_attack: int, target_defense: int, 
                        base_power: int, is_critical: bool = False,
                        element_multiplier: float = 1.0) -> int:
        """데미지 계산 공식"""
        # 공격력/방어력 비율 계산
        defense_effective = max(1, target_defense)
        power_ratio = attacker_attack / defense_effective
        
        # 기본 데미지
        base_damage = int(base_power * power_ratio)
        
        # 크리티컬 데미지 (1.5배)
        if is_critical:
            base_damage = int(base_damage * 1.5)
        
        # 속성 상성
        base_damage = int(base_damage * element_multiplier)
        
        # 최소 1 데미지 보장
        return max(1, base_damage)
    
    @staticmethod
    def calculate_cast_time(skill_power: int, character_magic: int) -> float:
        """캐스팅 시간 계산 (ATB 퍼센트로 반환)"""
        # 스킬 파워가 높을수록 캐스팅 시간 증가
        # 캐릭터 마력이 높을수록 캐스팅 시간 감소
        
        base_cast_time = skill_power / 50.0  # 기본 캐스팅 시간 (ATB %)
        magic_reduction = character_magic / 100.0  # 마력 감소량
        
        cast_time_percent = max(0.0, base_cast_time - magic_reduction)
        
        # 최대 캐스팅 시간 100% ATB 제한
        return min(100.0, cast_time_percent)
    
    @staticmethod
    def calculate_cooldown_reduction(character_level: int, equipment_bonus: int = 0) -> float:
        """쿨다운 감소율 계산"""
        # 레벨과 장비에 따른 쿨다운 감소
        level_reduction = character_level * 0.01  # 레벨당 1%
        total_reduction = level_reduction + (equipment_bonus * 0.01)
        
        # 최대 50% 감소 제한
        return min(0.5, total_reduction)
    
    @staticmethod
    def calculate_critical_chance(attacker_luck: int, base_crit: float = 0.05) -> float:
        """크리티컬 확률 계산"""
        # 기본 5% + 운 스탯에 따른 보너스
        crit_chance = base_crit + (attacker_luck * 0.001)  # 운 100당 10% 증가
        
        # 최대 50% 크리티컬 제한
        return min(0.50, crit_chance)

class EquipmentBalance:
    """장비 밸런스 시스템"""
    
    def __init__(self):
        self.weapon_balance = self._init_weapon_balance()
        self.armor_balance = self._init_armor_balance()
        self.accessory_balance = self._init_accessory_balance()
    
    def _init_weapon_balance(self) -> Dict[WeaponCategory, Dict[str, Any]]:
        """무기 밸런스 데이터"""
        return {
            # 근접 무기들 - 각각 다른 특성
            WeaponCategory.SWORD: {
                "attack_range": (50, 120),
                "accuracy_bonus": 10,
                "critical_bonus": 0.05,
                "element": ElementType.NEUTRAL,
                "special": "균형잡힌 성능"
            },
            WeaponCategory.AXE: {
                "attack_range": (70, 140),
                "accuracy_bonus": -5,
                "critical_bonus": 0.08,
                "element": ElementType.NEUTRAL,
                "special": "높은 공격력, 낮은 명중률"
            },
            WeaponCategory.SPEAR: {
                "attack_range": (45, 110),
                "accuracy_bonus": 15,
                "critical_bonus": 0.03,
                "element": ElementType.NEUTRAL,
                "special": "높은 명중률, 낮은 크리티컬"
            },
            WeaponCategory.MACE: {
                "attack_range": (60, 125),
                "accuracy_bonus": 0,
                "critical_bonus": 0.04,
                "element": ElementType.NEUTRAL,
                "special": "방어력 무시 효과"
            },
            WeaponCategory.DAGGER: {
                "attack_range": (35, 90),
                "accuracy_bonus": 20,
                "critical_bonus": 0.12,
                "element": ElementType.NEUTRAL,
                "special": "빠른 속도, 높은 크리티컬"
            },
            WeaponCategory.STAFF: {
                "attack_range": (40, 100),
                "accuracy_bonus": 5,
                "critical_bonus": 0.02,
                "element": ElementType.NEUTRAL,
                "special": "마법력 증가"
            },
            WeaponCategory.WAND: {
                "attack_range": (30, 80),
                "accuracy_bonus": 8,
                "critical_bonus": 0.03,
                "element": ElementType.NEUTRAL,
                "special": "마나 효율 증가"
            },
            WeaponCategory.FIST: {
                "attack_range": (40, 95),
                "accuracy_bonus": 25,
                "critical_bonus": 0.06,
                "element": ElementType.NEUTRAL,
                "special": "연속 공격 가능"
            },
            
            # 원거리 무기들
            WeaponCategory.BOW: {
                "attack_range": (55, 115),
                "accuracy_bonus": 20,
                "critical_bonus": 0.07,
                "element": ElementType.NEUTRAL,
                "special": "원거리 공격"
            },
            WeaponCategory.CROSSBOW: {
                "attack_range": (65, 130),
                "accuracy_bonus": 15,
                "critical_bonus": 0.09,
                "element": ElementType.NEUTRAL,
                "special": "관통 효과"
            },
            WeaponCategory.GUN: {
                "attack_range": (60, 125),
                "accuracy_bonus": 12,
                "critical_bonus": 0.08,
                "element": ElementType.NEUTRAL,
                "special": "무시 방어력"
            },
            WeaponCategory.THROWING: {
                "attack_range": (45, 105),
                "accuracy_bonus": 10,
                "critical_bonus": 0.05,
                "element": ElementType.NEUTRAL,
                "special": "다중 대상"
            }
        }
    
    def _init_armor_balance(self) -> Dict[ArmorCategory, Dict[str, Any]]:
        """방어구 밸런스 데이터"""
        return {
            # 상체 방어구
            ArmorCategory.HEAVY_ARMOR: {
                "defense_range": (60, 120),
                "speed_penalty": -10,
                "special": "높은 방어력, 속도 감소"
            },
            ArmorCategory.LIGHT_ARMOR: {
                "defense_range": (40, 80),
                "speed_penalty": 0,
                "special": "균형잡힌 성능"
            },
            ArmorCategory.ROBE: {
                "defense_range": (20, 50),
                "speed_penalty": 5,
                "special": "마법 저항력 증가"
            },
            ArmorCategory.LEATHER: {
                "defense_range": (35, 70),
                "speed_penalty": 2,
                "special": "회피율 증가"
            },
            
            # 하체 방어구 (상체의 60% 성능)
            ArmorCategory.HEAVY_GREAVES: {
                "defense_range": (36, 72),
                "speed_penalty": -6,
                "special": "높은 방어력"
            },
            ArmorCategory.LIGHT_GREAVES: {
                "defense_range": (24, 48),
                "speed_penalty": 0,
                "special": "균형잡힌 성능"
            },
            ArmorCategory.CLOTH_PANTS: {
                "defense_range": (12, 30),
                "speed_penalty": 3,
                "special": "마법 저항력"
            },
            ArmorCategory.LEATHER_PANTS: {
                "defense_range": (21, 42),
                "speed_penalty": 1,
                "special": "회피율 증가"
            },
            
            # 머리 방어구 (상체의 40% 성능)
            ArmorCategory.HELMET: {
                "defense_range": (24, 48),
                "speed_penalty": -4,
                "special": "크리티컬 저항"
            },
            ArmorCategory.CAP: {
                "defense_range": (16, 32),
                "speed_penalty": 0,
                "special": "균형잡힌 성능"
            },
            ArmorCategory.HOOD: {
                "defense_range": (8, 20),
                "speed_penalty": 2,
                "special": "은신 보너스"
            },
            ArmorCategory.CIRCLET: {
                "defense_range": (14, 28),
                "speed_penalty": 1,
                "special": "마나 증가"
            }
        }
    
    def _init_accessory_balance(self) -> Dict[AccessoryCategory, Dict[str, Any]]:
        """장신구 밸런스 데이터"""
        return {
            # 목걸이류 - 주로 공격력/마법력
            AccessoryCategory.NECKLACE: {
                "stat_bonus": {"attack": (5, 15), "magic_power": (5, 15)},
                "special": "공격력과 마법력 증가"
            },
            AccessoryCategory.AMULET: {
                "stat_bonus": {"defense": (8, 20), "magic_defense": (8, 20)},
                "special": "방어력과 마법 방어력 증가"
            },
            AccessoryCategory.PENDANT: {
                "stat_bonus": {"hp": (20, 50), "mp": (10, 25)},
                "special": "HP와 MP 증가"
            },
            AccessoryCategory.CHAIN: {
                "stat_bonus": {"speed": (5, 12), "evasion": (5, 12)},
                "special": "속도와 회피력 증가"
            },
            
            # 반지류 - 특수 효과 중심
            AccessoryCategory.RING: {
                "stat_bonus": {"critical": (3, 8), "accuracy": (5, 10)},
                "special": "크리티컬과 명중률 증가"
            },
            AccessoryCategory.SIGNET: {
                "stat_bonus": {"all_stats": (2, 5)},
                "special": "모든 스탯 소량 증가"
            },
            AccessoryCategory.BAND: {
                "stat_bonus": {"hp_regen": (1, 3), "mp_regen": (1, 2)},
                "special": "HP/MP 재생"
            },
            AccessoryCategory.SEAL: {
                "stat_bonus": {"status_resist": (10, 25)},
                "special": "상태이상 저항"
            },
            
            # 기타 장신구
            AccessoryCategory.EARRING: {
                "stat_bonus": {"luck": (8, 15), "critical": (2, 5)},
                "special": "운과 크리티컬 증가"
            },
            AccessoryCategory.BRACELET: {
                "stat_bonus": {"speed": (3, 8), "cast_speed": (5, 12)},
                "special": "속도와 시전속도 증가"
            },
            AccessoryCategory.BELT: {
                "stat_bonus": {"carry_weight": (50, 100), "item_find": (5, 10)},
                "special": "소지 무게와 아이템 발견율 증가"
            },
            AccessoryCategory.CHARM: {
                "stat_bonus": {"exp_bonus": (5, 15), "gold_find": (10, 20)},
                "special": "경험치와 골드 획득량 증가"
            }
        }

class FieldSkillBalance:
    """필드 스킬 밸런스 (걸음 수 기준 쿨다운)"""
    
    # 캐릭터 클래스별 사용 가능한 필드 스킬 - 실제 게임 직업에 맞게 수정
    CLASS_FIELD_SKILLS = {
        "전사": ["보물 탐지", "야외 치료", "집단 축복", "장비 수리"],
        "아크메이지": ["마법 이동", "환경 정화", "보물 탐지", "내구도 강화", "완벽 수리", "장비 보호"],
        "궁수": ["보물 탐지", "던전 분석", "집단 은신"],
        "도적": ["자물쇠 해제", "보물 탐지", "집단 은신"],
        "성기사": ["야외 치료", "환경 정화", "집단 축복", "내구도 강화", "장비 보호"],
        "암흑기사": ["환경 정화", "던전 분석", "마법 이동"],
        "몽크": ["야외 치료", "집단 축복", "던전 분석"],
        "바드": ["집단 축복", "환경 정화", "보물 탐지"],
        "네크로맨서": ["환경 정화", "던전 분석", "마법 이동"],
        "용기사": ["집단 축복", "마법 이동", "야외 치료"],
        "검성": ["자물쇠 해제", "던전 분석", "집단 축복", "내구도 분석"],
        "정령술사": ["환경 정화", "마법 이동", "야외 치료", "내구도 강화", "장비 보호"],
        "암살자": ["집단 은신", "자물쇠 해제", "보물 탐지"],
        "기계공학자": ["자물쇠 해제", "던전 분석", "보물 탐지", "장비 수리", "내구도 강화", "완벽 수리", "내구도 분석"],
        "무당": ["환경 정화", "야외 치료", "집단 축복", "내구도 강화", "장비 보호"],
        "해적": ["보물 탐지", "자물쇠 해제", "집단 은신"],
        "사무라이": ["자물쇠 해제", "던전 분석", "집단 축복"],
        "드루이드": ["야외 치료", "환경 정화", "보물 탐지", "장비 수리", "장비 보호"],
        "철학자": ["던전 분석", "환경 정화", "집단 축복", "장비 수리", "내구도 분석"],
        "시간술사": ["마법 이동", "던전 분석", "환경 정화", "완벽 수리", "내구도 분석"],
        "연금술사": ["환경 정화", "야외 치료", "보물 탐지", "장비 수리", "내구도 강화", "완벽 수리", "내구도 분석"],
        "검투사": ["야외 치료", "집단 축복", "보물 탐지"],
        "기사": ["집단 축복", "야외 치료", "던전 분석"],
        "신관": ["야외 치료", "환경 정화", "집단 축복"],
        "마검사": ["마법 이동", "집단 축복", "보물 탐지", "내구도 강화", "장비 보호"],
        "차원술사": ["마법 이동", "던전 분석", "환경 정화", "장비 보호"],
        "광전사": ["집단 축복", "야외 치료", "보물 탐지"],
        # 모든 직업이 기본 스킬들을 사용할 수 있도록
        "기본": ["보물 탐지", "야외 치료", "자물쇠 해제", "환경 정화", "장비 수리", "내구도 분석"]
    }
    
    FIELD_SKILLS = {
        "보물 탐지": {
            "cooldown_steps": 300,
            "mp_cost": 15,
            "success_rate": 0.7,
            "target_type": "none",
            "description": "숨겨진 보물이나 비밀 통로를 찾습니다.",
            "classes": ["전사", "아크메이지", "궁수", "도적", "바드", "암살자", "기계공학자", "해적", "드루이드", "연금술사", "검투사", "마검사", "광전사", "기본"]
        },
        "야외 치료": {
            "cooldown_steps": 400,
            "mp_cost": 20,
            "heal_ratio": 0.4,
            "target_type": "ally",
            "description": "자연의 힘으로 아군을 치료합니다.",
            "classes": ["전사", "성기사", "몽크", "정령술사", "무당", "드루이드", "연금술사", "검투사", "기사", "신관", "광전사", "기본"]
        },
        "마법 이동": {
            "cooldown_steps": 1000,
            "mp_cost": 25,
            "target_type": "none",
            "description": "마법으로 안전한 곳으로 순간이동합니다.",
            "classes": ["아크메이지", "암흑기사", "네크로맨서", "용기사", "정령술사", "시간술사", "마검사", "차원술사"]
        },
        "자물쇠 해제": {
            "cooldown_steps": 200,
            "mp_cost": 10,
            "success_rate": 0.8,
            "target_type": "none",
            "description": "잠긴 문이나 상자를 엽니다.",
            "classes": ["도적", "검성", "암살자", "기계공학자", "해적", "사무라이", "기본"]
        },
        "환경 정화": {
            "cooldown_steps": 500,
            "mp_cost": 18,
            "target_type": "party",
            "description": "독성, 저주 등 환경 디버프를 정화합니다.",
            "classes": ["아크메이지", "성기사", "암흑기사", "바드", "네크로맨서", "정령술사", "무당", "드루이드", "철학자", "시간술사", "연금술사", "신관", "차원술자", "기본"]
        },
        "집단 은신": {
            "cooldown_steps": 600,
            "mp_cost": 22,
            "duration": 180,
            "target_type": "party",
            "description": "파티 전체를 은신시켜 적의 탐지를 피합니다.",
            "classes": ["궁수", "도적", "암살자", "해적"]
        },
        "던전 분석": {
            "cooldown_steps": 400,
            "mp_cost": 15,
            "target_type": "none",
            "description": "던전의 구조와 위험 요소를 분석합니다.",
            "classes": ["궁수", "암흑기사", "몽크", "네크로맨서", "검성", "기계공학자", "사무라이", "철학자", "시간술사", "기사", "차원술사"]
        },
        "집단 축복": {
            "cooldown_steps": 800,
            "mp_cost": 30,
            "duration": 300,
            "target_type": "party",
            "description": "파티 전체에 축복을 내려 능력치를 증가시킵니다.",
            "classes": ["전사", "성기사", "몽크", "바드", "용기사", "검성", "무당", "철학자", "검투사", "기사", "신관", "마검사", "광전사"]
        },
        # 내구도 관련 필드 스킬들
        "장비 수리": {
            "cooldown_steps": 300,
            "mp_cost": 20,
            "target_type": "ally",
            "description": "손상된 장비를 마법으로 수리합니다.",
            "classes": ["전사", "기계공학자", "연금술사", "철학자", "드루이드", "검투사", "기본"]
        },
        "내구도 강화": {
            "cooldown_steps": 600,
            "mp_cost": 35,
            "target_type": "ally",
            "description": "장비의 최대 내구도를 일시적으로 증가시킵니다.",
            "classes": ["아크메이지", "성기사", "기계공학자", "정령술사", "무당", "연금술사", "마검사"]
        },
        "완벽 수리": {
            "cooldown_steps": 1200,
            "mp_cost": 60,
            "target_type": "party",
            "description": "파티의 모든 장비를 완전히 수리합니다.",
            "classes": ["아크메이지", "기계공학자", "연금술사", "시간술사"]
        },
        "내구도 분석": {
            "cooldown_steps": 100,  # 150 -> 100으로 쿨다운도 감소
            "mp_cost": 3,           # 8 -> 3으로 MP 소모 크게 감소
            "target_type": "none",
            "description": "파티 장비의 상태를 마법으로 정밀 분석하고 수리 계획을 제공합니다.",
            "classes": ["기계공학자", "연금술사", "철학자", "시간술사", "검성", "기본"]
        },
        "장비 보호": {
            "cooldown_steps": 800,
            "mp_cost": 40,
            "target_type": "party",
            "description": "일정 시간 동안 장비 내구도 감소를 방지합니다.",
            "classes": ["아크메이지", "성기사", "정령술사", "무당", "드루이드", "마검사", "차원술사"]
        }
    }
    
    @staticmethod
    def get_available_skills(character_class: str) -> List[str]:
        """캐릭터 클래스에 따른 사용 가능한 필드 스킬 반환"""
        return FieldSkillBalance.CLASS_FIELD_SKILLS.get(character_class, [])
    
    @staticmethod
    def get_skill_info(skill_name: str) -> Dict[str, Any]:
        """특정 필드 스킬의 정보 반환"""
        return FieldSkillBalance.FIELD_SKILLS.get(skill_name, {})
    
    @staticmethod
    def calculate_heal_amount(caster_stats: Dict[str, int], base_ratio: float = 0.3) -> int:
        """시전자 스탯 기반 회복량 계산"""
        # 공격력, 마법력, HP, 방어력 등을 종합적으로 계산
        total_power = (
            caster_stats.get("physical_attack", 0) * 0.3 +
            caster_stats.get("magic_attack", 0) * 0.4 +
            caster_stats.get("max_hp", 0) * 0.001 +
            caster_stats.get("physical_defense", 0) * 0.2 +
            caster_stats.get("magic_defense", 0) * 0.1
        )
        
        return int(total_power * base_ratio)

class SkillBalance:
    """스킬 밸런스 (고정 캐스트 타임 및 쿨다운)"""
    
    # 스킬별 고정 캐스트 타임 (ATB 퍼센트)
    CAST_TIMES = {
        # HP 공격 스킬들
        "렌졸리어": 15.0,
        "브레이버": 0.0,
        "크로스 슬래시": 8.0,
        "클라이막틱": 25.0,
        "피니시 터치": 20.0,
        "메테오": 30.0,
        "바하무트": 40.0,
        "나이츠 오브 라운드": 50.0,
        
        # BRV 공격 스킬들
        "썬더": 5.0,
        "케어": 3.0,
        "파이어": 5.0,
        "블리자드": 5.0,
        "큐어": 8.0,
        "라이프": 15.0,
        "헤이스트": 10.0,
        "슬로우": 8.0,
        "포이즌": 6.0,
        "리젠": 12.0,
        
        # 궁극기들
        "옴니슬래시": 35.0,
        "초신성": 45.0,
        "대지진": 25.0,
        "최종 천국": 60.0,
        
        # 버프/디버프
        "어택 업": 5.0,
        "가드 업": 5.0,
        "스피드 업": 7.0,
        "매직 업": 6.0,
        "디스펠": 10.0,
        "실렌스": 8.0,
        "슬립": 6.0,
    }
    
    # 스킬별 고정 쿨다운 (턴 수)
    COOLDOWNS = {
        # HP 공격 스킬들 (강력할수록 긴 쿨다운)
        "렌졸리어": 3,
        "브레이버": 0,  # 기본 공격은 쿨다운 없음
        "크로스 슬래시": 2,
        "클라이막틱": 5,
        "피니시 터치": 4,
        "메테오": 6,
        "바하무트": 8,
        "나이츠 오브 라운드": 12,
        
        # BRV 공격 스킬들
        "썬더": 1,
        "케어": 2,
        "파이어": 1,
        "블리자드": 1,
        "큐어": 3,
        "라이프": 8,
        "헤이스트": 4,
        "슬로우": 3,
        "포이즌": 2,
        "리젠": 5,
        
        # 궁극기들 (매우 긴 쿨다운)
        "옴니슬래시": 10,
        "초신성": 15,
        "대지진": 8,
        "최종 천국": 20,
        
        # 버프/디버프
        "어택 업": 3,
        "가드 업": 3,
        "스피드 업": 4,
        "매직 업": 3,
        "디스펠": 5,
        "실렌스": 4,
        "슬립": 3,
    }
    
    @staticmethod
    def get_cast_time(skill_name: str) -> float:
        """스킬별 고정 캐스트 타임 반환 (ATB 퍼센트)"""
        return SkillBalance.CAST_TIMES.get(skill_name, 0.0)
    
    @staticmethod
    def get_cooldown(skill_name: str) -> int:
        """스킬별 고정 쿨다운 반환 (턴 수)"""
        return SkillBalance.COOLDOWNS.get(skill_name, 0)
    
    @staticmethod
    def calculate_heal_amount(caster_stats: Dict[str, int], skill_name: str, base_power: int = 100) -> int:
        """시전자 스탯 기반 회복량 계산"""
        # 회복 스킬은 시전자의 스탯에 비례
        if skill_name in ["케어", "큐어", "라이프", "리젠"]:
            # 마법 공격력과 최대 HP를 주로 활용
            magic_power = caster_stats.get("magic_attack", 50)
            max_hp = caster_stats.get("max_hp", 500)
            physical_attack = caster_stats.get("physical_attack", 50)
            
            # 스킬별 계수 적용
            skill_multipliers = {
                "케어": 0.8,     # 약한 회복
                "큐어": 1.5,     # 강한 회복
                "라이프": 2.0,   # 매우 강한 회복
                "리젠": 0.6      # 지속 회복
            }
            
            multiplier = skill_multipliers.get(skill_name, 1.0)
            
            # 종합 회복력 계산
            heal_power = (magic_power * 1.5 + max_hp * 0.05 + physical_attack * 0.3) * multiplier
            
            return max(10, int(heal_power))  # 최소 10의 회복량 보장
        
        return base_power

# 전역 밸런스 매니저
balance_manager = {
    "combat": CombatFormulas(),
    "equipment": EquipmentBalance(),
    "field_skills": FieldSkillBalance(),
    "skills": SkillBalance()
}

def get_balance_manager() -> Dict[str, Any]:
    """밸런스 매니저 반환"""
    return balance_manager

def calculate_hit_rate(attacker_accuracy: int, target_evasion: int) -> float:
    """명중률 계산 (최대 회피율 75% 제한)"""
    return CombatFormulas.calculate_hit_chance(attacker_accuracy, target_evasion)

def calculate_damage(attacker_attack: int, target_defense: int, base_power: int,
                    is_critical: bool = False, element_multiplier: float = 1.0) -> int:
    """데미지 계산"""
    return CombatFormulas.calculate_damage(
        attacker_attack, target_defense, base_power, is_critical, element_multiplier
    )

def get_equipment_stats(equipment_type: str, category: str, tier: int = 1) -> Dict[str, Any]:
    """장비 스탯 계산"""
    balance = balance_manager["equipment"]
    
    if equipment_type == "weapon":
        weapon_cat = WeaponCategory(category)
        stats = balance.weapon_balance[weapon_cat].copy()
        # 티어에 따른 스탯 조정
        min_attack, max_attack = stats["attack_range"]
        stats["attack"] = random.randint(
            min_attack + (tier - 1) * 10,
            max_attack + (tier - 1) * 15
        )
        return stats
    
    elif equipment_type == "armor":
        armor_cat = ArmorCategory(category)
        stats = balance.armor_balance[armor_cat].copy()
        min_def, max_def = stats["defense_range"]
        stats["defense"] = random.randint(
            min_def + (tier - 1) * 8,
            max_def + (tier - 1) * 12
        )
        return stats
    
    elif equipment_type == "accessory":
        acc_cat = AccessoryCategory(category)
        stats = balance.accessory_balance[acc_cat].copy()
        # 티어에 따른 보너스 조정
        for stat, (min_val, max_val) in stats["stat_bonus"].items():
            stats[stat] = random.randint(
                min_val + (tier - 1) * 2,
                max_val + (tier - 1) * 3
            )
        return stats
    
    return {}

def is_skill_ready(skill_name: str, last_use_steps: int, current_steps: int) -> bool:
    """필드 스킬 사용 가능 여부 (걸음 수 기반 쿨다운 체크)"""
    if skill_name in FieldSkillBalance.FIELD_SKILLS:
        cooldown_steps = FieldSkillBalance.FIELD_SKILLS[skill_name]["cooldown_steps"]
        return (current_steps - last_use_steps) >= cooldown_steps
    return True

def get_field_skill_targets(skill_name: str) -> str:
    """필드 스킬의 대상 타입 반환"""
    if skill_name in FieldSkillBalance.FIELD_SKILLS:
        return FieldSkillBalance.FIELD_SKILLS[skill_name].get("target_type", "none")
    return "none"
