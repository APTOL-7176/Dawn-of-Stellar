#!/usr/bin/env python3
"""
속성 변경 장신구 시스템
- 착용자의 공격 속성을 변경하는 특수 장신구들
- 각 속성별로 다양한 종류 제공
"""

import random
from typing import Dict, List, Optional, Any
from enum import Enum
from equipment_system import ItemTier, AccessoryCategory
from .balance_system import ElementType

class ElementalAccessory:
    """속성 변경 장신구"""
    
    def __init__(self, name: str, element: ElementType, tier: ItemTier, 
                 category: AccessoryCategory, special_effects: Dict[str, Any] = None):
        self.name = name
        self.element = element
        self.tier = tier
        self.category = category
        self.special_effects = special_effects or {}
        
    def get_elemental_bonus(self) -> Dict[str, Any]:
        """속성별 추가 보너스"""
        bonuses = {
            ElementType.FIRE: {
                "damage_bonus": 0.1,
                "burn_chance": 0.15,
                "description": "화염 속성 공격, 화상 확률"
            },
            ElementType.ICE: {
                "damage_bonus": 0.08,
                "freeze_chance": 0.12,
                "speed_reduction": 0.2,
                "description": "빙결 속성 공격, 동결 확률"
            },
            ElementType.LIGHTNING: {
                "damage_bonus": 0.12,
                "shock_chance": 0.18,
                "critical_bonus": 0.05,
                "description": "번개 속성 공격, 감전 확률"
            },
            ElementType.EARTH: {
                "damage_bonus": 0.06,
                "armor_pierce": 0.25,
                "stun_chance": 0.1,
                "description": "대지 속성 공격, 방어 관통"
            },
            ElementType.WIND: {
                "damage_bonus": 0.09,
                "speed_bonus": 0.15,
                "evasion_bonus": 0.1,
                "description": "바람 속성 공격, 속도 증가"
            },
            ElementType.WATER: {
                "damage_bonus": 0.07,
                "healing_bonus": 0.2,
                "mp_recovery": 0.15,
                "description": "물 속성 공격, 회복 효과"
            },
            ElementType.LIGHT: {
                "damage_bonus": 0.11,
                "undead_bonus": 0.5,
                "purify_chance": 0.2,
                "description": "빛 속성 공격, 언데드 특효"
            },
            ElementType.DARK: {
                "damage_bonus": 0.13,
                "life_steal": 0.15,
                "curse_chance": 0.1,
                "description": "어둠 속성 공격, 생명력 흡수"
            },
            ElementType.POISON: {
                "damage_bonus": 0.05,
                "poison_chance": 0.3,
                "dot_damage": 0.2,
                "description": "독 속성 공격, 독 상태 확률"
            },
            ElementType.NEUTRAL: {
                "damage_bonus": 0.0,
                "stability": 1.0,
                "description": "무속성 공격, 안정적인 데미지"
            }
        }
        return bonuses.get(self.element, bonuses[ElementType.NEUTRAL])

class ElementalAccessoryGenerator:
    """속성 장신구 생성기"""
    
    def __init__(self):
        # 속성별 장신구 이름 템플릿
        self.elemental_names = {
            ElementType.FIRE: {
                "목걸이": ["불꽃목걸이", "화염의목걸이", "용의목걸이", "태양의목걸이", "화신의목걸이", "불멸의화염목걸이"],
                "반지": ["화염반지", "불꽃반지", "용의반지", "태양반지", "화신반지", "불멸의화염반지"],
                "귀걸이": ["불꽃귀걸이", "화염귀걸이", "용의귀걸이", "태양귀걸이", "화신귀걸이", "불멸의화염귀걸이"],
                "팔찌": ["화염팔찌", "불꽃팔찌", "용의팔찌", "태양팔찌", "화신팔찌", "불멸의화염팔찌"]
            },
            ElementType.ICE: {
                "목걸이": ["얼음목걸이", "빙결의목걸이", "서리의목걸이", "블리자드목걸이", "빙신의목걸이", "절대영도목걸이"],
                "반지": ["얼음반지", "빙결반지", "서리반지", "블리자드반지", "빙신반지", "절대영도반지"],
                "귀걸이": ["얼음귀걸이", "빙결귀걸이", "서리귀걸이", "블리자드귀걸이", "빙신귀걸이", "절대영도귀걸이"],
                "팔찌": ["얼음팔찌", "빙결팔찌", "서리팔찌", "블리자드팔찌", "빙신팔찌", "절대영도팔찌"]
            },
            ElementType.LIGHTNING: {
                "목걸이": ["번개목걸이", "전기의목걸이", "천둥의목걸이", "폭풍의목걸이", "뇌신의목걸이", "천벌의번개목걸이"],
                "반지": ["번개반지", "전기반지", "천둥반지", "폭풍반지", "뇌신반지", "천벌의번개반지"],
                "귀걸이": ["번개귀걸이", "전기귀걸이", "천둥귀걸이", "폭풍귀걸이", "뇌신귀걸이", "천벌의번개귀걸이"],
                "팔찌": ["번개팔찌", "전기팔찌", "천둥팔찌", "폭풍팔찌", "뇌신팔찌", "천벌의번개팔찌"]
            },
            ElementType.EARTH: {
                "목걸이": ["대지목걸이", "돌의목걸이", "바위의목걸이", "산의목걸이", "지신의목걸이", "대지모신의목걸이"],
                "반지": ["대지반지", "돌반지", "바위반지", "산의반지", "지신반지", "대지모신의반지"],
                "귀걸이": ["대지귀걸이", "돌귀걸이", "바위귀걸이", "산의귀걸이", "지신귀걸이", "대지모신의귀걸이"],
                "팔찌": ["대지팔찌", "돌팔찌", "바위팔찌", "산의팔찌", "지신팔찌", "대지모신의팔찌"]
            },
            ElementType.WIND: {
                "목걸이": ["바람목걸이", "돌풍의목걸이", "태풍의목걸이", "질풍의목걸이", "풍신의목걸이", "천공의바람목걸이"],
                "반지": ["바람반지", "돌풍반지", "태풍반지", "질풍반지", "풍신반지", "천공의바람반지"],
                "귀걸이": ["바람귀걸이", "돌풍귀걸이", "태풍귀걸이", "질풍귀걸이", "풍신귀걸이", "천공의바람귀걸이"],
                "팔찌": ["바람팔찌", "돌풍팔찌", "태풍팔찌", "질풍팔찌", "풍신팔찌", "천공의바람팔찌"]
            },
            ElementType.WATER: {
                "목걸이": ["물의목걸이", "파도의목걸이", "바다의목걸이", "해류의목걸이", "수신의목걸이", "심해의물목걸이"],
                "반지": ["물의반지", "파도반지", "바다반지", "해류반지", "수신반지", "심해의물반지"],
                "귀걸이": ["물의귀걸이", "파도귀걸이", "바다귀걸이", "해류귀걸이", "수신귀걸이", "심해의물귀걸이"],
                "팔찌": ["물의팔찌", "파도팔찌", "바다팔찌", "해류팔찌", "수신팔찌", "심해의물팔찌"]
            },
            ElementType.LIGHT: {
                "목걸이": ["빛의목걸이", "성광의목걸이", "천사의목걸이", "신성한목걸이", "광명의목걸이", "절대광명목걸이"],
                "반지": ["빛의반지", "성광반지", "천사반지", "신성한반지", "광명반지", "절대광명반지"],
                "귀걸이": ["빛의귀걸이", "성광귀걸이", "천사귀걸이", "신성한귀걸이", "광명귀걸이", "절대광명귀걸이"],
                "팔찌": ["빛의팔찌", "성광팔찌", "천사팔찌", "신성한팔찌", "광명팔찌", "절대광명팔찌"]
            },
            ElementType.DARK: {
                "목걸이": ["어둠목걸이", "암흑의목걸이", "악마의목걸이", "저주의목걸이", "암신의목걸이", "절대암흑목걸이"],
                "반지": ["어둠반지", "암흑반지", "악마반지", "저주반지", "암신반지", "절대암흑반지"],
                "귀걸이": ["어둠귀걸이", "암흑귀걸이", "악마귀걸이", "저주귀걸이", "암신귀걸이", "절대암흑귀걸이"],
                "팔찌": ["어둠팔찌", "암흑팔찌", "악마팔찌", "저주팔찌", "암신팔찌", "절대암흑팔찌"]
            },
            ElementType.POISON: {
                "목걸이": ["독의목걸이", "맹독의목걸이", "독사의목걸이", "독액의목걸이", "독신의목걸이", "절대독성목걸이"],
                "반지": ["독의반지", "맹독반지", "독사반지", "독액반지", "독신반지", "절대독성반지"],
                "귀걸이": ["독의귀걸이", "맹독귀걸이", "독사귀걸이", "독액귀걸이", "독신귀걸이", "절대독성귀걸이"],
                "팔찌": ["독의팔찌", "맹독팔찌", "독사팔찌", "독액팔찌", "독신팔찌", "절대독성팔찌"]
            },
            ElementType.NEUTRAL: {
                "목걸이": ["기본목걸이", "일반목걸이", "무속성목걸이", "균형목걸이", "중립목걸이", "무속성의목걸이"],
                "반지": ["기본반지", "일반반지", "무속성반지", "균형반지", "중립반지", "무속성의반지"],
                "귀걸이": ["기본귀걸이", "일반귀걸이", "무속성귀걸이", "균형귀걸이", "중립귀걸이", "무속성의귀걸이"],
                "팔찌": ["기본팔찌", "일반팔찌", "무속성팔찌", "균형팔찌", "중립팔찌", "무속성의팔찌"]
            }
        }
    
    def generate_elemental_accessory(self, element: ElementType, tier: ItemTier, 
                                   accessory_type: str = None) -> Dict[str, Any]:
        """속성 장신구 생성"""
        if accessory_type is None:
            accessory_type = random.choice(["목걸이", "반지", "귀걸이", "팔찌"])
        
        # 이름 선택
        tier_index = tier.value[1] - 1
        element_names = self.elemental_names.get(element, self.elemental_names[ElementType.NEUTRAL])
        type_names = element_names.get(accessory_type, ["기본장신구"] * 6)
        name = type_names[min(tier_index, len(type_names) - 1)]
        
        # 속성 보너스 가져오기
        elemental_bonus = ElementalAccessory(name, element, tier, None).get_elemental_bonus()
        
        # 기본 스탯 계산
        base_stats = {
            "attack_bonus": tier.value[1] * 5,
            "element_change": element.value,
            "special_power": tier.value[1] * 10
        }
        
        # 속성별 특수 효과 추가
        special_effects = elemental_bonus.copy()
        special_effects.update(self._get_tier_bonus(tier))
        
        return {
            "name": name,
            "type": "elemental_accessory",
            "category": accessory_type,
            "tier": tier,
            "element": element.value,  # 문자열로 변경
            "attack_element": element.value,  # 착용자의 공격 속성 변경
            "stat_bonuses": base_stats,
            "special_effects": special_effects,
            "value": self.calculate_value(tier, element),
            "description": f"{element.value} 속성으로 공격 속성을 변경하는 {tier.value[0]} 등급 {accessory_type}"
        }
    
    def _get_tier_bonus(self, tier: ItemTier) -> Dict[str, Any]:
        """티어별 추가 보너스"""
        tier_bonuses = {
            ItemTier.COMMON: {"power_multiplier": 1.0},
            ItemTier.UNCOMMON: {"power_multiplier": 1.2, "secondary_effect": True},
            ItemTier.RARE: {"power_multiplier": 1.5, "secondary_effect": True, "resistance": 0.1},
            ItemTier.EPIC: {"power_multiplier": 2.0, "secondary_effect": True, "resistance": 0.2, "aura_effect": True},
            ItemTier.LEGENDARY: {"power_multiplier": 2.5, "secondary_effect": True, "resistance": 0.3, "aura_effect": True, "unique_skill": True},
            ItemTier.MYTHIC: {"power_multiplier": 3.0, "secondary_effect": True, "resistance": 0.5, "aura_effect": True, "unique_skill": True, "god_tier": True}
        }
        return tier_bonuses.get(tier, tier_bonuses[ItemTier.COMMON])
    
    def calculate_value(self, tier: ItemTier, element: ElementType) -> int:
        """속성 장신구 가치 계산"""
        base_value = 150  # 속성 장신구는 비싸다
        tier_multiplier = tier.value[1] ** 2
        
        # 특수 속성 보너스
        element_bonus = 1.0
        if element in [ElementType.LIGHT, ElementType.DARK]:
            element_bonus = 1.5  # 빛/어둠은 희귀
        elif element == ElementType.POISON:
            element_bonus = 1.3  # 독도 특수
            
        return int(base_value * tier_multiplier * element_bonus)
    
    def generate_random_elemental_accessory(self, tier: ItemTier = None) -> Dict[str, Any]:
        """랜덤 속성 장신구 생성"""
        if tier is None:
            tier = random.choice(list(ItemTier))
        
        # 무속성 제외하고 랜덤 선택
        elements = [e for e in ElementType if e != ElementType.NEUTRAL]
        element = random.choice(elements)
        
        return self.generate_elemental_accessory(element, tier)

# 전역 속성 장신구 생성기
elemental_accessory_generator = ElementalAccessoryGenerator()

def generate_elemental_accessory(element_name: str = None, tier: str = "일반") -> Dict[str, Any]:
    """속성 장신구 생성 함수"""
    tier_map = {
        "일반": ItemTier.COMMON,
        "고급": ItemTier.UNCOMMON,
        "희귀": ItemTier.RARE,
        "영웅": ItemTier.EPIC,
        "전설": ItemTier.LEGENDARY,
        "신화": ItemTier.MYTHIC
    }
    
    element_map = {
        "화염": ElementType.FIRE,
        "빙결": ElementType.ICE,
        "번개": ElementType.LIGHTNING,
        "대지": ElementType.EARTH,
        "바람": ElementType.WIND,
        "물": ElementType.WATER,
        "빛": ElementType.LIGHT,
        "어둠": ElementType.DARK,
        "독": ElementType.POISON
    }
    
    item_tier = tier_map.get(tier, ItemTier.COMMON)
    
    if element_name and element_name in element_map:
        element = element_map[element_name]
        return elemental_accessory_generator.generate_elemental_accessory(element, item_tier)
    else:
        return elemental_accessory_generator.generate_random_elemental_accessory(item_tier)
