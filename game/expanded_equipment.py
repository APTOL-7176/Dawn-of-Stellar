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
    # 기본 스탯 증가 (퍼센트)
    ATTACK_PERCENT = "공격력 %"
    MAGIC_PERCENT = "마법력 %"
    DEFENSE_PERCENT = "방어력 %"
    MAGIC_DEFENSE_PERCENT = "마법방어력 %"
    HP_PERCENT = "생명력 %"
    MP_PERCENT = "마나 %"
    SPEED_PERCENT = "속도 %"
    
    # 기본 스탯 증가 (고정값)
    ATTACK_FLAT = "공격력"
    MAGIC_FLAT = "마법력"
    DEFENSE_FLAT = "방어력" 
    MAGIC_DEFENSE_FLAT = "마법방어력"
    HP_FLAT = "생명력"
    MP_FLAT = "마나"
    SPEED_FLAT = "속도"
    
    # 전투 효과 (나누기 공식 기반)
    CRITICAL_CHANCE = "치명타율"  # 공격자 크리티컬 / 적 크리티컬 저항
    CRITICAL_DAMAGE = "치명타 피해"
    DODGE_CHANCE = "회피율"      # 아군 회피 / 적 명중률
    BLOCK_CHANCE = "막기 확률"
    ACCURACY = "명중률"          # 공격자 명중 / 적 회피
    VAMPIRIC = "흡혈"
    THORNS = "가시"
    
    # 원소 관련 (모든 10가지 원소)
    FIRE_DAMAGE = "화염 피해"
    ICE_DAMAGE = "빙결 피해"
    LIGHTNING_DAMAGE = "번개 피해"
    EARTH_DAMAGE = "대지 피해"
    WIND_DAMAGE = "바람 피해"
    WATER_DAMAGE = "물 피해"
    LIGHT_DAMAGE = "빛 피해"
    DARK_DAMAGE = "어둠 피해"
    POISON_DAMAGE = "독 피해"
    NEUTRAL_DAMAGE = "무속성 피해"
    
    FIRE_RESIST = "화염 저항"
    ICE_RESIST = "빙결 저항"
    LIGHTNING_RESIST = "번개 저항"
    EARTH_RESIST = "대지 저항"
    WIND_RESIST = "바람 저항"
    WATER_RESIST = "물 저항"
    LIGHT_RESIST = "빛 저항"
    DARK_RESIST = "어둠 저항"
    POISON_RESIST = "독 저항"
    NEUTRAL_RESIST = "무속성 저항"
    
    # 스킬 관련
    SKILL_COOLDOWN = "스킬 쿨다운 감소"
    MP_COST_REDUCTION = "마나 소모 감소"
    CAST_SPEED = "시전 속도"
    
    # 특별 효과
    EXP_BOOST = "경험치 증가"
    GOLD_BOOST = "골드 증가"
    DROP_RATE = "아이템 드롭률"
    LUCK_BOOST = "행운 증가"
    
    # 내구도 관련
    SELF_REPAIR = "자가 수리"
    DURABILITY_BOOST = "내구도 증가"
    UNBREAKABLE = "파괴 불가"

@dataclass
class EquipmentEffect:
    """장비 효과"""
    effect_type: SpecialEffect
    value: float
    description: str
    proc_chance: float = 1.0  # 발동 확률 (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """효과를 딕셔너리로 직렬화"""
        return {
            'effect_type': self.effect_type.value,
            'value': self.value,
            'description': self.description,
            'proc_chance': self.proc_chance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EquipmentEffect':
        """딕셔너리에서 효과 객체 복원"""
        # SpecialEffect enum 복원
        effect_type = None
        for effect in SpecialEffect:
            if effect.value == data['effect_type']:
                effect_type = effect
                break
        
        if effect_type is None:
            # 알 수 없는 효과 타입인 경우 기본값으로 설정
            effect_type = SpecialEffect.ATTACK_FLAT
        
        return cls(
            effect_type=effect_type,
            value=data.get('value', 0),
            description=data.get('description', ''),
            proc_chance=data.get('proc_chance', 1.0)
        )
    
    def to_dict(self) -> Dict[str, any]:
        """세이브를 위한 딕셔너리 변환"""
        return {
            'effect_type': self.effect_type.value,
            'value': self.value,
            'description': self.description,
            'proc_chance': self.proc_chance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'EquipmentEffect':
        """딕셔너리에서 EquipmentEffect 객체 생성"""
        # SpecialEffect enum 찾기
        effect_type = None
        for effect in SpecialEffect:
            if effect.value == data['effect_type']:
                effect_type = effect
                break
        
        if effect_type is None:
            # 기본값으로 ATTACK_PERCENT 사용
            effect_type = SpecialEffect.ATTACK_PERCENT
        
        return cls(
            effect_type=effect_type,
            value=data.get('value', 0),
            description=data.get('description', ''),
            proc_chance=data.get('proc_chance', 1.0)
        )

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
        
    def to_dict(self) -> Dict[str, Any]:
        """장비를 딕셔너리로 직렬화 (세이브용)"""
        return {
            'name': self.name,
            'equipment_type': self.equipment_type.value,
            'rarity': self.rarity.value,
            'physical_attack': self.physical_attack,
            'magic_attack': self.magic_attack,
            'physical_defense': self.physical_defense,
            'magic_defense': self.magic_defense,
            'speed': self.speed,
            'hp_bonus': self.hp_bonus,
            'mp_bonus': self.mp_bonus,
            'max_durability': self.max_durability,
            'current_durability': self.current_durability,
            'is_broken': self.is_broken,
            'protection_turns': self.protection_turns,
            'special_effects': [effect.to_dict() for effect in self.special_effects],
            'set_name': self.set_name,
            'set_piece_id': self.set_piece_id,
            'enhancement_level': self.enhancement_level,
            'max_enhancement': self.max_enhancement,
            'level_requirement': self.level_requirement,
            'class_restriction': self.class_restriction
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Equipment':
        """딕셔너리에서 장비 객체 복원 (로드용)"""
        # EquipmentType과 EquipmentRarity enum 복원
        equipment_type = EquipmentType(data['equipment_type'])
        rarity = EquipmentRarity(data['rarity'])
        
        # 장비 객체 생성
        equipment = cls(data['name'], equipment_type, rarity)
        
        # 스탯 복원
        equipment.physical_attack = data.get('physical_attack', 0)
        equipment.magic_attack = data.get('magic_attack', 0)
        equipment.physical_defense = data.get('physical_defense', 0)
        equipment.magic_defense = data.get('magic_defense', 0)
        equipment.speed = data.get('speed', 0)
        equipment.hp_bonus = data.get('hp_bonus', 0)
        equipment.mp_bonus = data.get('mp_bonus', 0)
        
        # 내구도 복원
        equipment.max_durability = data.get('max_durability', 50)
        equipment.current_durability = data.get('current_durability', equipment.max_durability)
        equipment.is_broken = data.get('is_broken', False)
        equipment.protection_turns = data.get('protection_turns', 0)
        
        # 특수 효과 복원
        equipment.special_effects = []
        for effect_data in data.get('special_effects', []):
            equipment.special_effects.append(EquipmentEffect.from_dict(effect_data))
        
        # 기타 속성 복원
        equipment.set_name = data.get('set_name')
        equipment.set_piece_id = data.get('set_piece_id')
        equipment.enhancement_level = data.get('enhancement_level', 0)
        equipment.max_enhancement = data.get('max_enhancement', 15)
        equipment.level_requirement = data.get('level_requirement', 1)
        equipment.class_restriction = data.get('class_restriction', [])
        
        return equipment
        
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
    
    def apply_equipment_effects(self, character, action_type: str = "passive", **kwargs) -> List[str]:
        """장비 특수 효과 적용"""
        messages = []
        
        for effect in self.special_effects:
            # 발동 확률 체크
            import random
            if random.random() > effect.proc_chance:
                continue
                
            effect_type = effect.effect_type
            value = effect.value
            
            # 패시브 효과들
            if action_type == "passive":
                if effect_type == SpecialEffect.VISION_RANGE:
                    character.temp_vision_bonus = getattr(character, 'temp_vision_bonus', 0) + int(value)
                    
                elif effect_type == SpecialEffect.SPEED_BOOST:
                    character.temp_speed_bonus = getattr(character, 'temp_speed_bonus', 0) + int(value)
                    
                elif effect_type == SpecialEffect.CRIT_CHANCE:
                    character.temp_crit_bonus = getattr(character, 'temp_crit_bonus', 0) + value
                    
                elif effect_type == SpecialEffect.MAGIC_RESIST:
                    character.temp_magic_resistance = getattr(character, 'temp_magic_resistance', 0) + value
            
            # 공격 시 효과들
            elif action_type == "attack":
                target = kwargs.get('target')
                damage = kwargs.get('damage', 0)
                
                if effect_type == SpecialEffect.LIFE_STEAL:
                    heal_amount = int(damage * value)
                    old_hp = character.current_hp
                    character.current_hp = min(character.max_hp, character.current_hp + heal_amount)
                    actual_heal = character.current_hp - old_hp
                    if actual_heal > 0:
                        messages.append(f"🩸 {self.name} 효과: 생명력 {actual_heal} 흡수!")
                
                elif effect_type == SpecialEffect.MANA_BURN and target:
                    mp_burn = min(int(value * 10), getattr(target, 'current_mp', 0))
                    if mp_burn > 0:
                        target.current_mp -= mp_burn
                        messages.append(f"💙 {self.name} 효과: {target.name}의 MP {mp_burn} 소모!")
                
                elif effect_type == SpecialEffect.POISON_CHANCE and target:
                    if hasattr(target, 'status_manager') and target.status_manager:
                        target.status_manager.add_status("독", 3, 1.0)
                        messages.append(f"☠️ {self.name} 효과: {target.name} 중독!")
                
                elif effect_type == SpecialEffect.FIRE_DAMAGE and target:
                    fire_damage = int(damage * value)
                    if hasattr(target, 'status_manager') and target.status_manager:
                        target.status_manager.add_status("화상", 3, 1.0)
                        messages.append(f"🔥 {self.name} 효과: {target.name} 화상!")
                
                elif effect_type == SpecialEffect.ICE_SLOW and target:
                    if hasattr(target, 'status_manager') and target.status_manager:
                        target.status_manager.add_status("냉기", 2, 1.0)
                        messages.append(f"🧊 {self.name} 효과: {target.name} 감속!")
                
                elif effect_type == SpecialEffect.LIGHTNING_CHAIN and target:
                    chain_damage = int(damage * 0.5)
                    messages.append(f"⚡ {self.name} 효과: 연쇄 번개 {chain_damage} 피해!")
            
            # 방어 시 효과들
            elif action_type == "defend":
                attacker = kwargs.get('attacker')
                incoming_damage = kwargs.get('damage', 0)
                
                if effect_type == SpecialEffect.DAMAGE_REFLECT and attacker:
                    reflect_damage = int(incoming_damage * value)
                    if hasattr(attacker, 'current_hp'):
                        attacker.current_hp = max(1, attacker.current_hp - reflect_damage)
                        messages.append(f"🛡️ {self.name} 효과: {reflect_damage} 피해 반사!")
                
                elif effect_type == SpecialEffect.SHIELD_CHANCE:
                    import random
                    if random.random() < value:
                        messages.append(f"🛡️ {self.name} 효과: 공격 완전 차단!")
                        return messages, 0  # 피해 무효화
                
                elif effect_type == SpecialEffect.HP_REGEN:
                    regen_amount = int(character.max_hp * value)
                    old_hp = character.current_hp
                    character.current_hp = min(character.max_hp, character.current_hp + regen_amount)
                    actual_regen = character.current_hp - old_hp
                    if actual_regen > 0:
                        messages.append(f"💚 {self.name} 효과: HP {actual_regen} 재생!")
            
            # 스킬 사용 시 효과들
            elif action_type == "skill":
                skill_data = kwargs.get('skill_data', {})
                
                if effect_type == SpecialEffect.MP_REDUCTION:
                    mp_save = int(skill_data.get('mp_cost', 0) * value)
                    character.current_mp += mp_save
                    messages.append(f"💎 {self.name} 효과: MP {mp_save} 절약!")
                
                elif effect_type == SpecialEffect.COOLDOWN_REDUCTION:
                    messages.append(f"⏱️ {self.name} 효과: 쿨다운 {int(value*100)}% 감소!")
                
                elif effect_type == SpecialEffect.ELEMENT_CHANGE:
                    new_element = kwargs.get('new_element', '화염')
                    messages.append(f"🌟 {self.name} 효과: 속성이 {new_element}로 변경!")
            
            # 특수 효과들
            elif action_type == "special":
                if effect_type == SpecialEffect.TELEPORT_CHANCE:
                    character.temp_dodge_bonus = getattr(character, 'temp_dodge_bonus', 0) + 50
                    messages.append(f"🌀 {self.name} 효과: 순간이동으로 회피율 증가!")
                
                elif effect_type == SpecialEffect.TIME_SLOW:
                    character.temp_enemy_speed_down = getattr(character, 'temp_enemy_speed_down', 0) + int(value)
                    messages.append(f"⏰ {self.name} 효과: 적의 시간 지연!")
                
                elif effect_type == SpecialEffect.LUCK_BOOST:
                    character.temp_luck_bonus = getattr(character, 'temp_luck_bonus', 0) + value
                    messages.append(f"🍀 {self.name} 효과: 행운 증가!")
        
        return messages
    
    def enhance_equipment(self) -> bool:
        """장비 강화"""
        if self.enhancement_level >= self.max_enhancement:
            return False
        
        import random
        success_rate = max(0.1, 1.0 - (self.enhancement_level * 0.05))
        
        if random.random() < success_rate:
            self.enhancement_level += 1
            return True
        return False
    
    def repair_equipment(self, repair_amount: int = None):
        """장비 수리"""
        if repair_amount is None:
            self.current_durability = self.max_durability
        else:
            self.current_durability = min(self.max_durability, self.current_durability + repair_amount)
        
        self.is_broken = False
        self.protection_turns = 0
    
    def to_dict(self) -> Dict[str, any]:
        """세이브를 위한 딕셔너리 변환"""
        return {
            'name': self.name,
            'equipment_type': self.equipment_type.value,
            'rarity': self.rarity.value,
            'physical_attack': self.physical_attack,
            'magic_attack': self.magic_attack,
            'physical_defense': self.physical_defense,
            'magic_defense': self.magic_defense,
            'speed': self.speed,
            'hp_bonus': self.hp_bonus,
            'mp_bonus': self.mp_bonus,
            'max_durability': self.max_durability,
            'current_durability': self.current_durability,
            'is_broken': self.is_broken,
            'protection_turns': self.protection_turns,
            'special_effects': [effect.to_dict() for effect in self.special_effects],
            'set_name': self.set_name,
            'set_piece_id': self.set_piece_id,
            'enhancement_level': self.enhancement_level,
            'max_enhancement': self.max_enhancement,
            'level_requirement': self.level_requirement,
            'class_restriction': self.class_restriction,
            'description': getattr(self, 'description', '')
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'Equipment':
        """딕셔너리에서 Equipment 객체 생성"""
        equipment = cls(
            name=data['name'],
            equipment_type=EquipmentType(data['equipment_type']),
            rarity=EquipmentRarity(data['rarity'])
        )
        
        # 기본 스탯 복원
        equipment.physical_attack = data.get('physical_attack', 0)
        equipment.magic_attack = data.get('magic_attack', 0)
        equipment.physical_defense = data.get('physical_defense', 0)
        equipment.magic_defense = data.get('magic_defense', 0)
        equipment.speed = data.get('speed', 0)
        equipment.hp_bonus = data.get('hp_bonus', 0)
        equipment.mp_bonus = data.get('mp_bonus', 0)
        
        # 내구도 복원
        equipment.max_durability = data.get('max_durability', 100)
        equipment.current_durability = data.get('current_durability', equipment.max_durability)
        equipment.is_broken = data.get('is_broken', False)
        equipment.protection_turns = data.get('protection_turns', 0)
        
        # 특수 효과 복원
        equipment.special_effects = []
        for effect_data in data.get('special_effects', []):
            effect = EquipmentEffect.from_dict(effect_data)
            equipment.special_effects.append(effect)
        
        # 기타 속성 복원
        equipment.set_name = data.get('set_name')
        equipment.set_piece_id = data.get('set_piece_id')
        equipment.enhancement_level = data.get('enhancement_level', 0)
        equipment.max_enhancement = data.get('max_enhancement', 15)
        equipment.level_requirement = data.get('level_requirement', 1)
        equipment.class_restriction = data.get('class_restriction', [])
        equipment.description = data.get('description', '')
        
        return equipment

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
        
        # 특수 옵션 자동 생성 및 적용
        equipment = apply_special_options_to_equipment(equipment)
        
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

# 특수 옵션 생성 시스템
def generate_special_options(rarity: EquipmentRarity) -> List[EquipmentEffect]:
    """희귀도에 따른 특수 옵션 생성"""
    special_effects = []
    
    # 희귀도별 옵션 개수 (낮은 희귀도 극도로 제한)
    option_count = {
        EquipmentRarity.COMMON: 0,                    # 일반: 절대 옵션 없음
        EquipmentRarity.UNCOMMON: random.choices([0, 1], weights=[80, 20])[0],  # 고급: 80% 확률로 0개, 20% 확률로 1개
        EquipmentRarity.RARE: random.choices([1, 2], weights=[70, 30])[0],      # 희귀: 70% 확률로 1개, 30% 확률로 2개
        EquipmentRarity.EPIC: random.choices([2, 3], weights=[60, 40])[0],      # 영웅: 60% 확률로 2개, 40% 확률로 3개
        EquipmentRarity.LEGENDARY: random.randint(3, 4),                        # 전설: 3-4개
        EquipmentRarity.MYTHIC: random.randint(4, 6),                           # 신화: 4-6개
        EquipmentRarity.UNIQUE: random.randint(3, 5)                            # 유니크: 3-5개
    }
    
    num_options = option_count.get(rarity, 0)
    if num_options == 0:
        return special_effects
    
    # 가능한 특수 옵션들
    possible_effects = [
        # 기본 스탯 증가 (퍼센트) - 모든 희귀도
        (SpecialEffect.ATTACK_PERCENT, 5, 25, "공격력 +{}%"),
        (SpecialEffect.MAGIC_PERCENT, 5, 25, "마법력 +{}%"),
        (SpecialEffect.DEFENSE_PERCENT, 5, 20, "방어력 +{}%"),
        (SpecialEffect.MAGIC_DEFENSE_PERCENT, 5, 20, "마법방어력 +{}%"),
        (SpecialEffect.HP_PERCENT, 3, 15, "생명력 +{}%"),
        (SpecialEffect.MP_PERCENT, 5, 20, "마나 +{}%"),
        (SpecialEffect.SPEED_PERCENT, 3, 15, "속도 +{}%"),
        
        # 기본 스탯 증가 (고정값) - 모든 희귀도
        (SpecialEffect.ATTACK_FLAT, 10, 50, "공격력 +{}"),
        (SpecialEffect.MAGIC_FLAT, 10, 50, "마법력 +{}"),
        (SpecialEffect.DEFENSE_FLAT, 8, 40, "방어력 +{}"),
        (SpecialEffect.MAGIC_DEFENSE_FLAT, 8, 40, "마법방어력 +{}"),
        (SpecialEffect.HP_FLAT, 20, 100, "생명력 +{}"),
        (SpecialEffect.MP_FLAT, 15, 75, "마나 +{}"),
        (SpecialEffect.SPEED_FLAT, 5, 25, "속도 +{}"),
        
        # 전투 효과 (중급 이상) - 나누기 공식 기반
        (SpecialEffect.CRITICAL_CHANCE, 10, 50, "치명타율 +{}"),  # 크리티컬 스탯 증가
        (SpecialEffect.CRITICAL_DAMAGE, 10, 50, "치명타 피해 +{}%"),
        (SpecialEffect.DODGE_CHANCE, 10, 50, "회피율 +{}"),      # 회피 스탯 증가
        (SpecialEffect.ACCURACY, 10, 50, "명중률 +{}"),          # 명중 스탯 증가
        (SpecialEffect.BLOCK_CHANCE, 5, 25, "막기 확률 +{}%"),
        (SpecialEffect.VAMPIRIC, 1, 8, "흡혈 {}%"),
        
        # 원소 효과 (고급 이상) - 모든 10가지 원소
        (SpecialEffect.FIRE_DAMAGE, 10, 30, "화염 피해 +{}"),
        (SpecialEffect.ICE_DAMAGE, 10, 30, "빙결 피해 +{}"),
        (SpecialEffect.LIGHTNING_DAMAGE, 10, 30, "번개 피해 +{}"),
        (SpecialEffect.EARTH_DAMAGE, 10, 30, "대지 피해 +{}"),
        (SpecialEffect.WIND_DAMAGE, 10, 30, "바람 피해 +{}"),
        (SpecialEffect.WATER_DAMAGE, 10, 30, "물 피해 +{}"),
        (SpecialEffect.LIGHT_DAMAGE, 8, 35, "빛 피해 +{}"),
        (SpecialEffect.DARK_DAMAGE, 8, 35, "어둠 피해 +{}"),
        (SpecialEffect.POISON_DAMAGE, 5, 25, "독 피해 +{}"),
        (SpecialEffect.NEUTRAL_DAMAGE, 12, 40, "무속성 피해 +{}"),
        
        (SpecialEffect.FIRE_RESIST, 5, 30, "화염 저항 +{}%"),
        (SpecialEffect.ICE_RESIST, 5, 30, "빙결 저항 +{}%"),
        (SpecialEffect.LIGHTNING_RESIST, 5, 30, "번개 저항 +{}%"),
        (SpecialEffect.EARTH_RESIST, 5, 30, "대지 저항 +{}%"),
        (SpecialEffect.WIND_RESIST, 5, 30, "바람 저항 +{}%"),
        (SpecialEffect.WATER_RESIST, 5, 30, "물 저항 +{}%"),
        (SpecialEffect.LIGHT_RESIST, 5, 30, "빛 저항 +{}%"),
        (SpecialEffect.DARK_RESIST, 5, 30, "어둠 저항 +{}%"),
        (SpecialEffect.POISON_RESIST, 5, 30, "독 저항 +{}%"),
        (SpecialEffect.NEUTRAL_RESIST, 5, 30, "무속성 저항 +{}%"),
        
        # 스킬 관련 (영웅 이상)
        (SpecialEffect.SKILL_COOLDOWN, 5, 25, "스킬 쿨다운 -{}%"),
        (SpecialEffect.MP_COST_REDUCTION, 5, 20, "마나 소모 -{}%"),
        (SpecialEffect.CAST_SPEED, 10, 40, "시전 속도 +{}%"),
        
        # 특별 효과 (전설 이상)
        (SpecialEffect.EXP_BOOST, 10, 50, "경험치 +{}%"),
        (SpecialEffect.GOLD_BOOST, 15, 60, "골드 +{}%"),
        (SpecialEffect.DROP_RATE, 5, 25, "아이템 드롭률 +{}%"),
        (SpecialEffect.LUCK_BOOST, 1, 10, "행운 +{}"),
        
        # 내구도 관련 (신화급)
        (SpecialEffect.SELF_REPAIR, 1, 5, "자가 수리 {}%"),
        (SpecialEffect.DURABILITY_BOOST, 20, 100, "내구도 +{}%"),
    ]
    
    # 희귀도별 효과 필터링 (극도로 엄격하게)
    if rarity == EquipmentRarity.COMMON:
        # 일반: 아예 옵션 없음
        possible_effects = []
    elif rarity == EquipmentRarity.UNCOMMON:
        # 고급: 오직 기본 스탯 고정값만 (매우 제한적)
        possible_effects = possible_effects[7:14]  # 고정값만
    elif rarity == EquipmentRarity.RARE:
        # 희귀: 기본 스탯 전체만 (퍼센트 + 고정값)
        possible_effects = possible_effects[:14]
    elif rarity == EquipmentRarity.EPIC:
        # 영웅: 기본 스탯 + 전투 효과만 (원소 아직 없음)
        possible_effects = possible_effects[:20]
    elif rarity == EquipmentRarity.LEGENDARY:
        # 전설: 기본 스탯 + 전투 + 원소 일부 (화염, 빙결, 번개만)
        basic_combat = possible_effects[:20]
        basic_elements = possible_effects[20:26]  # 화염, 빙결, 번개 피해만
        basic_resists = possible_effects[30:33]   # 화염, 빙결, 번개 저항만
        possible_effects = basic_combat + basic_elements + basic_resists
    # 신화급과 유니크만 모든 효과 가능
    
    # 중복 없이 랜덤 선택
    selected_effects = random.sample(possible_effects, min(num_options, len(possible_effects)))
    
    for effect_type, min_val, max_val, desc_format in selected_effects:
        value = random.randint(min_val, max_val)
        description = desc_format.format(value)
        
        # 발동 확률 (대부분 100%, 일부 강력한 효과는 낮음)
        proc_chance = 1.0
        if effect_type in [SpecialEffect.THORNS, SpecialEffect.BLOCK_CHANCE, 
                          SpecialEffect.SELF_REPAIR]:
            proc_chance = 0.3 + (0.1 * (list(EquipmentRarity).index(rarity)))
            proc_chance = min(1.0, proc_chance)
        
        special_effects.append(EquipmentEffect(
            effect_type=effect_type,
            value=value,
            description=description,
            proc_chance=proc_chance
        ))
    
    return special_effects

def enhance_equipment(equipment: Equipment, enhancement_materials: Dict[str, int] = None) -> Dict[str, any]:
    """장비 강화 시스템"""
    if not equipment:
        return {"success": False, "message": "강화할 장비가 없습니다."}
    
    current_level = equipment.enhancement_level
    max_level = equipment.max_enhancement
    
    if current_level >= max_level:
        return {"success": False, "message": f"이미 최대 강화 단계 (+{max_level})입니다."}
    
    # 강화 성공률 계산
    success_rate = calculate_enhancement_success_rate(current_level, equipment.rarity)
    
    # 강화 비용 계산
    cost = calculate_enhancement_cost(current_level, equipment.rarity)
    
    # 강화 시도
    import random
    success = random.random() < success_rate
    
    if success:
        equipment.enhancement_level += 1
        new_level = equipment.enhancement_level
        
        # 특정 레벨에서 추가 특수 옵션 획득 (5, 10, 15)
        if new_level in [5, 10, 15] and new_level <= max_level:
            bonus_effects = generate_enhancement_bonus_effects(equipment.rarity, new_level)
            equipment.special_effects.extend(bonus_effects)
            bonus_msg = f" (레벨 {new_level} 보너스 효과 획득!)"
        else:
            bonus_msg = ""
        
        return {
            "success": True, 
            "message": f"강화 성공! +{current_level} → +{new_level}{bonus_msg}",
            "new_level": new_level,
            "bonus_effects": bonus_effects if new_level in [5, 10, 15] else []
        }
    else:
        # 강화 실패
        failure_result = handle_enhancement_failure(equipment, current_level)
        return failure_result

def calculate_enhancement_success_rate(current_level: int, rarity: EquipmentRarity) -> float:
    """강화 성공률 계산"""
    base_rates = {
        # 레벨별 기본 성공률
        0: 0.95,   # +0 → +1: 95%
        1: 0.90,   # +1 → +2: 90%
        2: 0.85,   # +2 → +3: 85%
        3: 0.80,   # +3 → +4: 80%
        4: 0.75,   # +4 → +5: 75%
        5: 0.65,   # +5 → +6: 65%
        6: 0.55,   # +6 → +7: 55%
        7: 0.45,   # +7 → +8: 45%
        8: 0.35,   # +8 → +9: 35%
        9: 0.25,   # +9 → +10: 25%
        10: 0.20,  # +10 → +11: 20%
        11: 0.15,  # +11 → +12: 15%
        12: 0.10,  # +12 → +13: 10%
        13: 0.08,  # +13 → +14: 8%
        14: 0.05,  # +14 → +15: 5%
    }
    
    base_rate = base_rates.get(current_level, 0.05)
    
    # 희귀도 보정
    rarity_bonus = {
        EquipmentRarity.COMMON: 0.1,      # +10%
        EquipmentRarity.UNCOMMON: 0.05,   # +5%
        EquipmentRarity.RARE: 0.0,        # 기본
        EquipmentRarity.EPIC: -0.05,      # -5%
        EquipmentRarity.LEGENDARY: -0.1,  # -10%
        EquipmentRarity.MYTHIC: -0.15,    # -15%
        EquipmentRarity.UNIQUE: -0.05     # -5%
    }
    
    final_rate = base_rate + rarity_bonus.get(rarity, 0.0)
    return max(0.01, min(1.0, final_rate))  # 최소 1%, 최대 100%

def calculate_enhancement_cost(current_level: int, rarity: EquipmentRarity) -> Dict[str, int]:
    """강화 비용 계산"""
    base_cost = 100 * (2 ** current_level)  # 지수적 증가
    
    rarity_multiplier = {
        EquipmentRarity.COMMON: 0.5,
        EquipmentRarity.UNCOMMON: 0.7,
        EquipmentRarity.RARE: 1.0,
        EquipmentRarity.EPIC: 1.5,
        EquipmentRarity.LEGENDARY: 2.0,
        EquipmentRarity.MYTHIC: 3.0,
        EquipmentRarity.UNIQUE: 2.5
    }
    
    final_cost = int(base_cost * rarity_multiplier.get(rarity, 1.0))
    
    return {
        "gold": final_cost,
        "enhancement_stones": 1 + (current_level // 5),  # 5레벨마다 +1
        "blessing_powder": 1 if current_level >= 10 else 0  # +10 이상부터 필요
    }

def generate_enhancement_bonus_effects(rarity: EquipmentRarity, level: int) -> List[EquipmentEffect]:
    """강화 보너스 효과 생성 (5, 10, 15 레벨)"""
    bonus_effects = []
    
    if level == 5:
        # +5 보너스: 기본 스탯 소폭 증가
        effect_type = random.choice([
            SpecialEffect.ATTACK_FLAT, SpecialEffect.DEFENSE_FLAT, 
            SpecialEffect.HP_FLAT, SpecialEffect.MP_FLAT
        ])
        value = random.randint(5, 15)
        description = f"강화 보너스: {effect_type.value} +{value}"
        
    elif level == 10:
        # +10 보너스: 전투 효과
        effect_type = random.choice([
            SpecialEffect.CRITICAL_CHANCE, SpecialEffect.DODGE_CHANCE,
            SpecialEffect.ACCURACY, SpecialEffect.VAMPIRIC
        ])
        if effect_type == SpecialEffect.VAMPIRIC:
            value = random.randint(1, 3)
            description = f"강화 보너스: 흡혈 {value}%"
        else:
            value = random.randint(5, 15)
            description = f"강화 보너스: {effect_type.value} +{value}"
            
    elif level == 15:
        # +15 보너스: 특별 효과
        effect_type = random.choice([
            SpecialEffect.EXP_BOOST, SpecialEffect.GOLD_BOOST,
            SpecialEffect.SELF_REPAIR, SpecialEffect.DURABILITY_BOOST
        ])
        if effect_type == SpecialEffect.SELF_REPAIR:
            value = random.randint(1, 3)
            description = f"강화 보너스: 자가 수리 {value}%"
        else:
            value = random.randint(10, 25)
            description = f"강화 보너스: {effect_type.value} +{value}%"
    
    bonus_effects.append(EquipmentEffect(
        effect_type=effect_type,
        value=value,
        description=description,
        proc_chance=1.0
    ))
    
    return bonus_effects

def handle_enhancement_failure(equipment: Equipment, current_level: int) -> Dict[str, any]:
    """강화 실패 처리"""
    if current_level >= 10:
        # +10 이상에서 실패 시 레벨 감소 위험
        downgrade_chance = 0.3 + (current_level - 10) * 0.1  # 30% + 레벨당 10%
        
        if random.random() < downgrade_chance:
            equipment.enhancement_level = max(0, current_level - 1)
            return {
                "success": False,
                "message": f"강화 실패! 레벨이 하락했습니다. +{current_level} → +{equipment.enhancement_level}",
                "downgraded": True
            }
    
    return {
        "success": False,
        "message": "강화 실패! 레벨은 유지됩니다.",
        "downgraded": False
    }

def apply_special_options_to_equipment(equipment: Equipment):
    """장비에 특수 옵션 적용"""
    if not equipment.special_effects:
        equipment.special_effects = generate_special_options(equipment.rarity)
    
    # 장비 설명에 특수 옵션 추가
    if hasattr(equipment, 'description'):
        if equipment.special_effects:
            option_desc = "\n특수 옵션:"
            for effect in equipment.special_effects:
                option_desc += f"\n  • {effect.description}"
                if effect.proc_chance < 1.0:
                    option_desc += f" ({int(effect.proc_chance*100)}% 확률)"
            equipment.description += option_desc
    
    return equipment
