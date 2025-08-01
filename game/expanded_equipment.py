"""
확장된 장비 시스템 - 다양하고 독특한 효과를 가진 장비들
"""

from typing import Dict, List, Optional, Any, Tuple
import random
from enum import Enum
from dataclasses import dataclass

class EquipmentRarity(Enum):
    """장비 희귀도"""
    COMMON = "일반"
    UNCOMMON = "고급"
    RARE = "희귀"
    EPIC = "영웅"
    LEGENDARY = "전설"
    MYTHIC = "신화"
    UNIQUE = "유니크"

class EquipmentType(Enum):
    """장비 타입"""
    WEAPON = "무기"
    ARMOR = "갑옷"
    HELMET = "투구"
    GLOVES = "장갑"
    BOOTS = "부츠"
    ACCESSORY = "장신구"
    SHIELD = "방패"

class SpecialEffect(Enum):
    """특수 효과 타입"""
    # 전투 효과
    ELEMENTAL_DAMAGE = "원소 피해"
    CRITICAL_CHANCE = "치명타 확률"
    VAMPIRIC = "흡혈"
    THORNS = "가시"
    BERSERKER = "광전사"
    MANA_BURN = "마나 번"
    
    # 내구도 관련
    SELF_REPAIR = "자가 수리"
    DURABILITY_BOOST = "내구도 증가"
    UNBREAKABLE = "파괴 불가"
    
    # 스탯 효과
    STAT_GROWTH = "능력치 성장"
    EXP_BOOST = "경험치 증가"
    GOLD_BOOST = "골드 증가"
    
    # 특별 효과
    PHASE_SHIFT = "위상 변화"
    TIME_SLOW = "시간 지연"
    LUCK_BOOST = "행운 증가"
    SKILL_COOLDOWN = "스킬 쿨다운"

@dataclass
class EquipmentEffect:
    """장비 효과"""
    effect_type: SpecialEffect
    value: float
    description: str
    proc_chance: float = 1.0  # 발동 확률 (0.0-1.0)

class Equipment:
    """확장된 장비 클래스"""
    
    def __init__(self, name: str, equipment_type: EquipmentType, rarity: EquipmentRarity):
        self.name = name
        self.equipment_type = equipment_type
        self.rarity = rarity
        
        # 기본 스탯
        self.physical_attack = 0
        self.magic_attack = 0
        self.physical_defense = 0
        self.magic_defense = 0
        self.speed = 0
        self.hp_bonus = 0
        self.mp_bonus = 0
        
        # 내구도
        self.max_durability = self._calculate_base_durability()
        self.current_durability = self.max_durability
        self.is_broken = False
        self.protection_turns = 0
        
        # 특수 효과
        self.special_effects: List[EquipmentEffect] = []
        
        # 세트 장비 관련
        self.set_name: Optional[str] = None
        self.set_piece_id: Optional[str] = None
        
        # 강화
        self.enhancement_level = 0
        self.max_enhancement = 15
        
        # 기타
        self.level_requirement = 1
        self.class_restriction: List[str] = []
        
    def _calculate_base_durability(self) -> int:
        """희귀도에 따른 기본 내구도 계산"""
        base_durability = {
            EquipmentRarity.COMMON: 50,
            EquipmentRarity.UNCOMMON: 75,
            EquipmentRarity.RARE: 100,
            EquipmentRarity.EPIC: 150,
            EquipmentRarity.LEGENDARY: 200,
            EquipmentRarity.MYTHIC: 300,
            EquipmentRarity.UNIQUE: 250
        }
        return base_durability.get(self.rarity, 50)
    
    def add_effect(self, effect: EquipmentEffect):
        """특수 효과 추가"""
        self.special_effects.append(effect)
    
    def get_total_stats(self) -> Dict[str, int]:
        """강화 레벨을 포함한 총 스탯 계산"""
        enhancement_multiplier = 1 + (self.enhancement_level * 0.1)
        
        return {
            'physical_attack': int(self.physical_attack * enhancement_multiplier),
            'magic_attack': int(self.magic_attack * enhancement_multiplier),
            'physical_defense': int(self.physical_defense * enhancement_multiplier),
            'magic_defense': int(self.magic_defense * enhancement_multiplier),
            'speed': int(self.speed * enhancement_multiplier),
            'hp_bonus': int(self.hp_bonus * enhancement_multiplier),
            'mp_bonus': int(self.mp_bonus * enhancement_multiplier)
        }
    
    def get_durability_percentage(self) -> float:
        """내구도 퍼센트 반환"""
        return self.current_durability / self.max_durability if self.max_durability > 0 else 0.0
    
    def apply_durability_effects(self) -> Dict[str, float]:
        """내구도에 따른 성능 감소 적용"""
        durability_ratio = self.get_durability_percentage()
        
        if durability_ratio > 0.75:
            effectiveness = 1.0
        elif durability_ratio > 0.5:
            effectiveness = 0.9
        elif durability_ratio > 0.25:
            effectiveness = 0.75
        elif durability_ratio > 0:
            effectiveness = 0.5
        else:
            effectiveness = 0.1  # 파괴된 상태에서도 최소 성능
        
        return {
            'effectiveness': effectiveness,
            'stat_multiplier': effectiveness
        }

class EquipmentGenerator:
    """장비 생성기"""
    
    def __init__(self):
        self.weapon_templates = self._init_weapon_templates()
        self.armor_templates = self._init_armor_templates()
        self.accessory_templates = self._init_accessory_templates()
        self.unique_equipments = self._init_unique_equipments()
        
    def _init_weapon_templates(self) -> Dict[str, Dict]:
        """무기 템플릿 초기화"""
        return {
            # 일반 무기
            "나무 막대기": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.COMMON,
                "stats": {"physical_attack": 5},
                "level": 1
            },
            "철검": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.COMMON,
                "stats": {"physical_attack": 12},
                "level": 3
            },
            "강철검": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.UNCOMMON,
                "stats": {"physical_attack": 18, "speed": 2},
                "level": 5
            },
            
            # 마법 무기
            "마법사의 지팡이": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.UNCOMMON,
                "stats": {"magic_attack": 15, "mp_bonus": 10},
                "level": 4,
                "effects": [
                    EquipmentEffect(SpecialEffect.MANA_BURN, 0.1, "10% 확률로 적의 MP 흡수")
                ]
            },
            
            # 특수 무기
            "흡혈검": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.RARE,
                "stats": {"physical_attack": 25, "hp_bonus": 15},
                "level": 8,
                "effects": [
                    EquipmentEffect(SpecialEffect.VAMPIRIC, 0.15, "피해의 15%를 HP로 흡수", 0.3)
                ]
            },
            
            "광전사의 도끼": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.EPIC,
                "stats": {"physical_attack": 35, "speed": -5},
                "level": 12,
                "effects": [
                    EquipmentEffect(SpecialEffect.BERSERKER, 2.0, "HP가 낮을수록 공격력 증가")
                ]
            },
            
            "시간의 검": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.LEGENDARY,
                "stats": {"physical_attack": 45, "speed": 10},
                "level": 18,
                "effects": [
                    EquipmentEffect(SpecialEffect.TIME_SLOW, 0.2, "20% 확률로 적의 행동 지연", 0.2)
                ]
            },
            
            "위상검": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.MYTHIC,
                "stats": {"physical_attack": 60, "magic_attack": 30},
                "level": 25,
                "effects": [
                    EquipmentEffect(SpecialEffect.PHASE_SHIFT, 0.3, "30% 확률로 물리/마법 피해 무시", 0.3)
                ]
            }
        }
    
    def _init_armor_templates(self) -> Dict[str, Dict]:
        """방어구 템플릿 초기화"""
        return {
            # 갑옷
            "가죽 갑옷": {
                "type": EquipmentType.ARMOR,
                "rarity": EquipmentRarity.COMMON,
                "stats": {"physical_defense": 8, "speed": 1},
                "level": 1
            },
            
            "강철 갑옷": {
                "type": EquipmentType.ARMOR,
                "rarity": EquipmentRarity.UNCOMMON,
                "stats": {"physical_defense": 15, "hp_bonus": 20},
                "level": 5
            },
            
            "가시 갑옷": {
                "type": EquipmentType.ARMOR,
                "rarity": EquipmentRarity.RARE,
                "stats": {"physical_defense": 22, "hp_bonus": 30},
                "level": 10,
                "effects": [
                    EquipmentEffect(SpecialEffect.THORNS, 0.5, "받은 피해의 50%를 반사")
                ]
            },
            
            "자가수리 갑옷": {
                "type": EquipmentType.ARMOR,
                "rarity": EquipmentRarity.EPIC,
                "stats": {"physical_defense": 30, "hp_bonus": 50},
                "level": 15,
                "effects": [
                    EquipmentEffect(SpecialEffect.SELF_REPAIR, 5, "매 턴 내구도 5 회복")
                ]
            },
            
            # 투구
            "철 투구": {
                "type": EquipmentType.HELMET,
                "rarity": EquipmentRarity.COMMON,
                "stats": {"physical_defense": 5, "magic_defense": 3},
                "level": 2
            },
            
            "지혜의 관": {
                "type": EquipmentType.HELMET,
                "rarity": EquipmentRarity.RARE,
                "stats": {"magic_defense": 18, "mp_bonus": 25},
                "level": 12,
                "effects": [
                    EquipmentEffect(SpecialEffect.EXP_BOOST, 0.2, "경험치 20% 추가 획득")
                ]
            },
            
            # 장갑
            "도둑의 장갑": {
                "type": EquipmentType.GLOVES,
                "rarity": EquipmentRarity.UNCOMMON,
                "stats": {"speed": 8, "physical_attack": 5},
                "level": 6,
                "effects": [
                    EquipmentEffect(SpecialEffect.GOLD_BOOST, 0.3, "골드 30% 추가 획득")
                ]
            },
            
            "행운의 장갑": {
                "type": EquipmentType.GLOVES,
                "rarity": EquipmentRarity.EPIC,
                "stats": {"speed": 12, "physical_attack": 8},
                "level": 16,
                "effects": [
                    EquipmentEffect(SpecialEffect.LUCK_BOOST, 0.25, "치명타 확률 25% 증가"),
                    EquipmentEffect(SpecialEffect.CRITICAL_CHANCE, 0.15, "치명타 피해 15% 증가")
                ]
            },
            
            # 부츠
            "바람의 부츠": {
                "type": EquipmentType.BOOTS,
                "rarity": EquipmentRarity.RARE,
                "stats": {"speed": 15, "physical_defense": 8},
                "level": 9,
                "effects": [
                    EquipmentEffect(SpecialEffect.SKILL_COOLDOWN, 0.2, "스킬 쿨다운 20% 감소")
                ]
            }
        }
    
    def _init_accessory_templates(self) -> Dict[str, Dict]:
        """장신구 템플릿 초기화"""
        return {
            "힘의 반지": {
                "type": EquipmentType.ACCESSORY,
                "rarity": EquipmentRarity.UNCOMMON,
                "stats": {"physical_attack": 10},
                "level": 3
            },
            
            "마법의 목걸이": {
                "type": EquipmentType.ACCESSORY,
                "rarity": EquipmentRarity.RARE,
                "stats": {"magic_attack": 15, "mp_bonus": 20},
                "level": 8
            },
            
            "성장의 부적": {
                "type": EquipmentType.ACCESSORY,
                "rarity": EquipmentRarity.EPIC,
                "stats": {"hp_bonus": 30, "mp_bonus": 30},
                "level": 14,
                "effects": [
                    EquipmentEffect(SpecialEffect.STAT_GROWTH, 0.05, "레벨업 시 스탯 5% 추가 증가")
                ]
            },
            
            "불멸의 심장": {
                "type": EquipmentType.ACCESSORY,
                "rarity": EquipmentRarity.LEGENDARY,
                "stats": {"hp_bonus": 100, "physical_defense": 15, "magic_defense": 15},
                "level": 20,
                "effects": [
                    EquipmentEffect(SpecialEffect.UNBREAKABLE, 1.0, "내구도 감소 면역")
                ]
            }
        }
    
    def _init_unique_equipments(self) -> Dict[str, Dict]:
        """유니크 장비 초기화"""
        return {
            "드래곤슬레이어": {
                "type": EquipmentType.WEAPON,
                "rarity": EquipmentRarity.UNIQUE,
                "stats": {"physical_attack": 80, "magic_attack": 20},
                "level": 30,
                "effects": [
                    EquipmentEffect(SpecialEffect.ELEMENTAL_DAMAGE, 1.5, "드래곤계 적에게 150% 피해"),
                    EquipmentEffect(SpecialEffect.DURABILITY_BOOST, 2.0, "내구도 2배 증가")
                ],
                "description": "전설 속 용을 처치한 영웅의 검"
            },
            
            "시공의 갑옷": {
                "type": EquipmentType.ARMOR,
                "rarity": EquipmentRarity.UNIQUE,
                "stats": {"physical_defense": 50, "magic_defense": 50, "hp_bonus": 200},
                "level": 35,
                "effects": [
                    EquipmentEffect(SpecialEffect.TIME_SLOW, 0.5, "받는 모든 피해 50% 지연"),
                    EquipmentEffect(SpecialEffect.SELF_REPAIR, 10, "매 턴 내구도 10 회복")
                ],
                "description": "시간을 조작하는 신비한 갑옷"
            },
            
            "무한의 건틀릿": {
                "type": EquipmentType.GLOVES,
                "rarity": EquipmentRarity.UNIQUE,
                "stats": {"physical_attack": 30, "magic_attack": 30, "speed": 20},
                "level": 25,
                "effects": [
                    EquipmentEffect(SpecialEffect.CRITICAL_CHANCE, 0.5, "치명타 확률 50% 증가"),
                    EquipmentEffect(SpecialEffect.MANA_BURN, 0.3, "공격 시 30% 확률로 적 MP 소모"),
                    EquipmentEffect(SpecialEffect.VAMPIRIC, 0.1, "피해의 10%를 HP/MP로 흡수")
                ],
                "description": "무한한 힘을 담은 전설의 장갑"
            }
        }
    
    def generate_equipment(self, equipment_name: str, enhancement_level: int = 0) -> Optional[Equipment]:
        """장비 생성"""
        # 모든 템플릿에서 검색
        template = None
        for templates in [self.weapon_templates, self.armor_templates, 
                         self.accessory_templates, self.unique_equipments]:
            if equipment_name in templates:
                template = templates[equipment_name]
                break
        
        if not template:
            return None
        
        # 장비 객체 생성
        equipment = Equipment(
            name=equipment_name,
            equipment_type=template["type"],
            rarity=template["rarity"]
        )
        
        # 스탯 적용
        stats = template.get("stats", {})
        for stat, value in stats.items():
            setattr(equipment, stat, value)
        
        # 레벨 제한
        equipment.level_requirement = template.get("level", 1)
        
        # 특수 효과 적용
        effects = template.get("effects", [])
        for effect in effects:
            equipment.add_effect(effect)
        
        # 강화 레벨 적용
        equipment.enhancement_level = min(enhancement_level, equipment.max_enhancement)
        
        # 설명
        equipment.description = template.get("description", f"{equipment.rarity.value} {equipment.equipment_type.value}")
        
        return equipment
    
    def get_random_equipment_by_level(self, character_level: int, rarity_bias: float = 0.0) -> Equipment:
        """레벨에 맞는 랜덤 장비 생성"""
        suitable_equipments = []
        
        # 모든 템플릿에서 레벨에 맞는 장비 찾기
        for templates in [self.weapon_templates, self.armor_templates, self.accessory_templates]:
            for name, template in templates.items():
                req_level = template.get("level", 1)
                if req_level <= character_level <= req_level + 5:  # 레벨 범위
                    suitable_equipments.append(name)
        
        if not suitable_equipments:
            return self.generate_equipment("나무 막대기")
        
        # 희귀도 바이어스 적용하여 선택
        if rarity_bias > 0:
            # 높은 희귀도 장비 선호
            weighted_equipments = []
            for name in suitable_equipments:
                template = None
                for templates in [self.weapon_templates, self.armor_templates, self.accessory_templates]:
                    if name in templates:
                        template = templates[name]
                        break
                
                if template:
                    rarity_weight = {
                        EquipmentRarity.COMMON: 1,
                        EquipmentRarity.UNCOMMON: 2,
                        EquipmentRarity.RARE: 4,
                        EquipmentRarity.EPIC: 8,
                        EquipmentRarity.LEGENDARY: 16
                    }.get(template["rarity"], 1)
                    
                    for _ in range(int(rarity_weight * (1 + rarity_bias))):
                        weighted_equipments.append(name)
            
            selected_name = random.choice(weighted_equipments)
        else:
            selected_name = random.choice(suitable_equipments)
        
        return self.generate_equipment(selected_name)

# 전역 장비 생성기 인스턴스
_equipment_generator = None

def get_equipment_generator() -> EquipmentGenerator:
    """장비 생성기 싱글톤 반환"""
    global _equipment_generator
    if _equipment_generator is None:
        _equipment_generator = EquipmentGenerator()
    return _equipment_generator

# 편의 함수들
def create_equipment(name: str, enhancement: int = 0) -> Optional[Equipment]:
    """장비 생성 편의 함수"""
    return get_equipment_generator().generate_equipment(name, enhancement)

def get_random_equipment(level: int, rarity_bias: float = 0.0) -> Equipment:
    """랜덤 장비 생성 편의 함수"""
    return get_equipment_generator().get_random_equipment_by_level(level, rarity_bias)
