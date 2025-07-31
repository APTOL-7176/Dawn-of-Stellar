#!/usr/bin/env python3
"""
소모품 시스템
100+ 포션, 치료제, 강화제, 전투용 아이템, 특수 아이템
"""

from typing import Dict, List, Optional, Callable, Union
from enum import Enum
import random

# 올바른 모듈에서 import
from .new_skill_system import StatusType, ElementType, get_status_icon

# StatusEffect 클래스 정의
class StatusEffect:
    def __init__(self, status_type: StatusType, duration: int, intensity: int = 1):
        self.status_type = status_type
        self.duration = duration
        self.intensity = intensity
    
    def __str__(self):
        icon = get_status_icon(self.status_type)
        return f"{icon} {self.status_type.value} ({self.duration}턴)"

# ElementSystem 클래스 정의
class ElementSystem:
    def get_element_color(self, element: ElementType) -> str:
        colors = {
            ElementType.NEUTRAL: "⚪",
            ElementType.FIRE: "🔥",
            ElementType.ICE: "❄️", 
            ElementType.LIGHTNING: "⚡",
            ElementType.EARTH: "🌍",
            ElementType.WIND: "💨",
            ElementType.WATER: "💧",
            ElementType.LIGHT: "☀️",
            ElementType.DARK: "🌑",
            ElementType.POISON: "☠️"
        }
        return colors.get(element, "⚪")

element_system = ElementSystem()

class ItemType(Enum):
    """아이템 타입"""
    CONSUMABLE = "소모품"
    KEY_ITEM = "중요템"

class ItemRarity(Enum):
    """아이템 등급"""
    COMMON = "일반"      # 흰색
    RARE = "레어"        # 파란색
    EPIC = "에픽"        # 보라색
    LEGENDARY = "전설"    # 주황색
    MYTHIC = "신화"      # 빨간색

class Item:
    """기본 아이템 클래스"""
    
    def __init__(self, name: str, item_type: ItemType, rarity: ItemRarity,
                 description: str = "", price: int = 0, level_req: int = 1):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.description = description
        self.price = price
        self.level_requirement = level_req
        self.element = ElementType.NEUTRAL
        self.special_effects = []
        
    def get_rarity_color(self) -> str:
        """등급별 색상 코드"""
        colors = {
            ItemRarity.COMMON: "⚪",
            ItemRarity.RARE: "🔵", 
            ItemRarity.EPIC: "🟣",
            ItemRarity.LEGENDARY: "🟠",
            ItemRarity.MYTHIC: "🔴"
        }
        return colors.get(self.rarity, "⚪")
    
    def get_display_name(self) -> str:
        """표시용 이름 (등급 포함)"""
        color = self.get_rarity_color()
        element_icon = element_system.get_element_color(self.element)
        return f"{color}{element_icon}{self.name}"
        
    def get_display_char(self) -> str:
        """표시할 문자 반환"""
        if self.item_type == ItemType.CONSUMABLE:
            return "!"
        return "?"

class Consumable(Item):
    """소모품 클래스"""
    
    def __init__(self, name: str, rarity: ItemRarity, effect_type: str,
                 effect_value: int, target_type: str = "single",
                 status_effects: List[StatusEffect] = None,
                 description: str = "", price: int = 0):
        super().__init__(name, ItemType.CONSUMABLE, rarity, description, price, 1)
        self.effect_type = effect_type  # heal_hp, heal_mp, cure_status, buff_stat 등
        self.effect_value = effect_value
        self.target_type = target_type  # single, all_allies, all_enemies
        self.status_effects = status_effects or []
        self.uses_remaining = 1

class ConsumableDatabase:
    """소모품 데이터베이스"""
    
    def __init__(self):
        self.consumables = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """소모품 데이터베이스 초기화"""
        self._create_consumables()
    
    def _create_consumables(self):
        """소모품 생성 (100+개) - 현재 직업별 스탯에 최적화된 효과"""
        consumables_data = [
            # 💊 기본 치료제류 (26개) - 크게 줄어든 MP 성장량에 맞춘 조정
            ("작은 포션", ItemRarity.COMMON, "heal_hp", 20, "single"),
            ("치료 포션", ItemRarity.COMMON, "heal_hp", 40, "single"),
            ("상급 치료 포션", ItemRarity.RARE, "heal_hp", 80, "single"),
            ("최상급 치료 포션", ItemRarity.EPIC, "heal_hp", 150, "single"),
            ("엘릭서", ItemRarity.LEGENDARY, "heal_hp", 250, "single"),
            ("작은 마나 포션", ItemRarity.COMMON, "heal_mp", 10, "single"),  # MP 회복량 더 감소
            ("마나 포션", ItemRarity.COMMON, "heal_mp", 20, "single"),  # MP 회복량 더 감소
            ("고급 마나 포션", ItemRarity.RARE, "heal_mp", 40, "single"),  # MP 회복량 더 감소
            ("최고급 마나 포션", ItemRarity.EPIC, "heal_mp", 80, "single"),  # MP 회복량 더 감소
            ("신성한 물", ItemRarity.LEGENDARY, "heal_mp", 150, "single"),  # MP 회복량 더 감소
            ("해독제", ItemRarity.COMMON, "cure_poison", 100, "single"),
            ("소독제", ItemRarity.COMMON, "cure_disease", 100, "single"),
            ("진정제", ItemRarity.COMMON, "cure_confuse", 100, "single"),
            ("수면제", ItemRarity.COMMON, "cure_sleep", 100, "single"),
            ("해빙제", ItemRarity.COMMON, "cure_freeze", 100, "single"),
            ("소생약", ItemRarity.RARE, "revive", 30, "single"),  # 부활 시 HP 30%로 감소
            ("완전소생약", ItemRarity.EPIC, "revive", 50, "single"),  # 부활 시 HP 50%로 감소
            ("전체 치료제", ItemRarity.RARE, "heal_hp", 60, "all_allies"),  # 전체 치료량 감소
            ("전체 마나 포션", ItemRarity.RARE, "heal_mp", 30, "all_allies"),  # 전체 MP 회복량 감소
            ("만능 해독제", ItemRarity.EPIC, "cure_all", 100, "single"),
            ("생명의 물약", ItemRarity.LEGENDARY, "full_heal", 100, "single"),
            ("마력의 물약", ItemRarity.LEGENDARY, "full_mp", 100, "single"),
            ("재생 포션", ItemRarity.EPIC, "regen_hp", 15, "single"),  # 턴당 재생량 감소
            ("마나 재생 포션", ItemRarity.EPIC, "regen_mp", 8, "single"),  # 턴당 재생량 감소
            ("신속 회복약", ItemRarity.RARE, "instant_heal", 35, "single"),  # 즉시 회복량 감소
            ("급속 충전제", ItemRarity.RARE, "instant_mp", 25, "single"),  # 즉시 MP 회복량 감소
            
            # 🔺 능력치 강화제류 (22개) - 버프 효과 적절히 조정
            ("힘의 물약", ItemRarity.COMMON, "buff_attack", 3, "single"),  # 버프량 감소
            ("민첩성 물약", ItemRarity.COMMON, "buff_speed", 3, "single"),
            ("방어력 물약", ItemRarity.COMMON, "buff_defense", 3, "single"),
            ("마력 증진제", ItemRarity.COMMON, "buff_magic", 3, "single"),
            ("상급 힘의 물약", ItemRarity.RARE, "buff_attack", 6, "single"),
            ("상급 민첩성 물약", ItemRarity.RARE, "buff_speed", 6, "single"),
            ("상급 방어력 물약", ItemRarity.RARE, "buff_defense", 6, "single"),
            ("상급 마력 증진제", ItemRarity.RARE, "buff_magic", 6, "single"),
            ("전투자의 각성제", ItemRarity.EPIC, "buff_all_combat", 4, "single"),
            ("마법사의 각성제", ItemRarity.EPIC, "buff_all_magic", 4, "single"),
            ("영웅의 엘릭서", ItemRarity.LEGENDARY, "buff_all_stats", 5, "single"),
            ("전체 힘의 물약", ItemRarity.RARE, "buff_attack", 4, "all_allies"),
            ("전체 민첩성 물약", ItemRarity.RARE, "buff_speed", 4, "all_allies"),
            ("전체 방어력 물약", ItemRarity.RARE, "buff_defense", 4, "all_allies"),
            ("전체 마력 증진제", ItemRarity.RARE, "buff_magic", 4, "all_allies"),
            ("용기의 물약", ItemRarity.EPIC, "buff_brave", 15, "single"),  # 용기 버프량 감소
            ("전체 용기의 물약", ItemRarity.EPIC, "buff_brave", 12, "all_allies"),
            ("집중력 향상제", ItemRarity.COMMON, "buff_accuracy", 8, "single"),  # 명중률 버프 감소
            ("행운의 물약", ItemRarity.RARE, "buff_luck", 6, "single"),  # 행운 버프 감소
            ("치명타 증진제", ItemRarity.RARE, "buff_critical", 6, "single"),  # 치명타 버프 감소
            ("마법 저항제", ItemRarity.RARE, "buff_magic_resist", 8, "single"),  # 마법 저항 버프 감소
            ("물리 저항제", ItemRarity.RARE, "buff_physical_resist", 8, "single"),  # 물리 저항 버프 감소
            
            # ⚔️ 전투용 아이템류 (24개) - 피해량 크게 감소
            ("수리검", ItemRarity.COMMON, "damage", 25, "single"),  # 피해량 크게 감소
            ("폭탄", ItemRarity.COMMON, "damage", 35, "single"),
            ("화염병", ItemRarity.COMMON, "fire_damage", 30, "single"),
            ("독 다트", ItemRarity.COMMON, "poison_damage", 20, "single"),
            ("얼음 구슬", ItemRarity.COMMON, "ice_damage", 25, "single"),
            ("번개 구슬", ItemRarity.COMMON, "lightning_damage", 30, "single"),
            ("상급 수리검", ItemRarity.RARE, "damage", 40, "single"),
            ("강화 폭탄", ItemRarity.RARE, "damage", 60, "single"),
            ("지옥불 폭탄", ItemRarity.RARE, "fire_damage", 50, "single"),
            ("맹독 다트", ItemRarity.RARE, "poison_damage", 35, "single"),
            ("절대영도 구슬", ItemRarity.RARE, "ice_damage", 45, "single"),
            ("천둥번개 구슬", ItemRarity.RARE, "lightning_damage", 55, "single"),
            ("전설의 수리검", ItemRarity.EPIC, "damage", 70, "single"),
            ("파멸의 폭탄", ItemRarity.EPIC, "damage", 100, "single"),
            ("용의 숨결", ItemRarity.EPIC, "fire_damage", 80, "single"),
            ("죽음의 독", ItemRarity.EPIC, "poison_damage", 60, "single"),
            ("빙하기 구슬", ItemRarity.EPIC, "ice_damage", 75, "single"),
            ("신의 번개", ItemRarity.EPIC, "lightning_damage", 90, "single"),
            ("전체 공격 폭탄", ItemRarity.RARE, "damage", 40, "all_enemies"),  # 전체 공격 피해 감소
            ("전체 화염 폭탄", ItemRarity.RARE, "fire_damage", 35, "all_enemies"),
            ("전체 독 가스", ItemRarity.RARE, "poison_damage", 25, "all_enemies"),
            ("전체 얼음 폭풍", ItemRarity.RARE, "ice_damage", 30, "all_enemies"),
            ("전체 번개 폭풍", ItemRarity.RARE, "lightning_damage", 40, "all_enemies"),
            ("신성한 폭탄", ItemRarity.LEGENDARY, "holy_damage", 120, "single"),  # 신성 피해 감소
            
            # ✨ 특수 아이템류 (24개) - 특수 효과 적절히 조정
            ("순간이동 두루마리", ItemRarity.RARE, "teleport", 100, "self"),
            ("투명화 포션", ItemRarity.RARE, "invisibility", 3, "self"),  # 지속시간 감소
            ("시간 정지 두루마리", ItemRarity.EPIC, "time_stop", 1, "all"),  # 지속시간 감소
            ("부활의 깃털", ItemRarity.LEGENDARY, "auto_revive", 1, "self"),
            ("마나 실드 두루마리", ItemRarity.EPIC, "mana_shield", 5, "self"),  # 지속시간 감소
            ("반사 물약", ItemRarity.EPIC, "reflect_damage", 3, "self"),  # 지속시간 감소
            ("광전사 물약", ItemRarity.RARE, "berserk", 3, "self"),  # 지속시간 감소
            ("냉정함의 물약", ItemRarity.RARE, "calm_mind", 5, "self"),  # 지속시간 감소
            ("경험치 2배 물약", ItemRarity.EPIC, "double_exp", 5, "all_allies"),  # 지속시간 감소
            ("골드 2배 물약", ItemRarity.EPIC, "double_gold", 5, "all_allies"),  # 지속시간 감소
            ("아이템 드랍 증가제", ItemRarity.RARE, "item_find", 5, "all_allies"),  # 지속시간 감소
            ("탐지 물약", ItemRarity.COMMON, "detect", 10, "all_allies"),
            ("야간 투시 물약", ItemRarity.COMMON, "night_vision", 15, "self"),
            ("수중 호흡 물약", ItemRarity.COMMON, "water_breathing", 20, "self"),
            ("화염 저항 물약", ItemRarity.COMMON, "fire_resist", 8, "self"),  # 지속시간 감소
            ("냉기 저항 물약", ItemRarity.COMMON, "ice_resist", 8, "self"),
            ("독 저항 물약", ItemRarity.COMMON, "poison_resist", 8, "self"),
            ("전기 저항 물약", ItemRarity.COMMON, "lightning_resist", 8, "self"),
            ("모든 원소 저항제", ItemRarity.EPIC, "all_resist", 6, "self"),  # 지속시간 감소
            ("완벽한 회피 물약", ItemRarity.LEGENDARY, "perfect_dodge", 2, "self"),  # 지속시간 감소
            ("무적 물약", ItemRarity.MYTHIC, "invincible", 1, "self"),  # 지속시간 감소
            ("신속 시전 두루마리", ItemRarity.RARE, "fast_cast", 5, "self"),  # 지속시간 감소
            ("마법 무효화 물약", ItemRarity.EPIC, "magic_immunity", 3, "self"),  # 지속시간 감소
            ("물리 무효화 물약", ItemRarity.EPIC, "physical_immunity", 3, "self"),  # 지속시간 감소
            ("마나 엘릭서", ItemRarity.LEGENDARY, "heal_mp", 200, "single"),
            ("완전 회복약", ItemRarity.EPIC, "full_heal", 100, "single"),
            ("부활약", ItemRarity.LEGENDARY, "revive", 50, "single"),
            ("부활의 깃털", ItemRarity.EPIC, "revive", 50, "single"),
            ("만능 치료제", ItemRarity.RARE, "cure_all_status", 100, "single"),
            ("해독제", ItemRarity.COMMON, "cure_poison", 100, "single"),
            ("해열제", ItemRarity.COMMON, "cure_burn", 100, "single"),
            ("해빙제", ItemRarity.COMMON, "cure_freeze", 100, "single"),
            ("마비 치료제", ItemRarity.COMMON, "cure_paralysis", 100, "single"),
            ("정신력 회복제", ItemRarity.RARE, "cure_mental", 100, "single"),
            ("재생 포션", ItemRarity.EPIC, "regen_hp", 25, "single"),
            ("마나 재생 포션", ItemRarity.EPIC, "regen_mp", 15, "single"),
            ("활력 포션", ItemRarity.RARE, "heal_both", 75, "single"),
            ("신성한 물", ItemRarity.LEGENDARY, "divine_heal", 150, "all_allies"),
            ("생명의 샘물", ItemRarity.MYTHIC, "life_water", 400, "all_allies"),
            ("시간 되돌리기 약", ItemRarity.MYTHIC, "time_heal", 250, "single"),
            ("완전 회복 엘릭서", ItemRarity.MYTHIC, "perfect_heal", 500, "all_allies"),
            
            # ⚡ 강화제류 (22개) - 버프 효과 적당히 조정
            ("힘의 약", ItemRarity.COMMON, "buff_attack", 15, "single"),
            ("힘의 물약", ItemRarity.RARE, "buff_attack", 25, "single"),
            ("방어의 약", ItemRarity.COMMON, "buff_defense", 15, "single"),
            ("속도의 약", ItemRarity.COMMON, "buff_speed", 15, "single"),
            ("신속의 물약", ItemRarity.RARE, "buff_speed", 25, "single"),
            ("마력의 약", ItemRarity.RARE, "buff_magic", 20, "single"),
            ("마력의 물약", ItemRarity.RARE, "buff_magic", 25, "single"),
            ("에너지 드링크", ItemRarity.RARE, "atb_boost", 30, "single"),
            ("만능 강화제", ItemRarity.EPIC, "buff_all", 20, "single"),
            ("전투의 영약", ItemRarity.LEGENDARY, "battle_boost", 35, "all_allies"),
            ("영웅의 음료", ItemRarity.EPIC, "hero_boost", 30, "single"),
            ("광폭화 약", ItemRarity.RARE, "berserk", 50, "single"),
            ("광폭화 물약", ItemRarity.EPIC, "berserk", 75, "single"),
            ("집중력 향상제", ItemRarity.RARE, "focus", 20, "single"),
            ("반사신경 향상제", ItemRarity.RARE, "reflex", 20, "single"),
            ("체력 증강제", ItemRarity.EPIC, "hp_boost", 50, "single"),
            ("마나 증강제", ItemRarity.EPIC, "mp_boost", 40, "single"),
            ("재생 촉진제", ItemRarity.EPIC, "regen_boost", 30, "single"),
            ("치명타 증강제", ItemRarity.EPIC, "critical_boost", 15, "single"),
            ("명중률 향상제", ItemRarity.RARE, "accuracy_boost", 20, "single"),
            ("회피력 향상제", ItemRarity.RARE, "evasion_boost", 20, "single"),
            ("저항력 증강제", ItemRarity.EPIC, "resist_boost", 30, "single"),
            
            # 💣 전투용 아이템 (24개) - 데미지 적당히 조정
            ("수리검", ItemRarity.COMMON, "damage_single", 60, "single_enemy"),
            ("폭탄", ItemRarity.RARE, "damage_area", 100, "all_enemies"),
            ("화염병", ItemRarity.RARE, "fire_damage", 80, "all_enemies"),
            ("빙결구", ItemRarity.RARE, "ice_damage", 80, "single_enemy"),
            ("얼음 수정", ItemRarity.RARE, "ice_slow", 70, "single_enemy"),
            ("번개구슬", ItemRarity.RARE, "lightning_damage", 80, "all_enemies"),
            ("번개 구슬", ItemRarity.RARE, "lightning_damage", 80, "all_enemies"),
            ("독가루", ItemRarity.RARE, "poison_damage", 70, "all_enemies"),
            ("독침", ItemRarity.COMMON, "poison_damage", 40, "single_enemy"),
            ("성수", ItemRarity.EPIC, "holy_damage", 150, "all_enemies"),
            ("마탄", ItemRarity.EPIC, "dark_damage", 150, "single_enemy"),
            ("대폭탄", ItemRarity.EPIC, "big_explosion", 200, "all_enemies"),
            ("용의 숨결", ItemRarity.LEGENDARY, "dragon_breath", 300, "all_enemies"),
            ("천벌", ItemRarity.LEGENDARY, "divine_punishment", 350, "single_enemy"),
            ("지옥불", ItemRarity.LEGENDARY, "hellfire", 320, "all_enemies"),
            ("절대영도", ItemRarity.LEGENDARY, "absolute_zero", 300, "all_enemies"),
            ("뇌신의 분노", ItemRarity.LEGENDARY, "thunder_god", 400, "single_enemy"),
            ("대지진", ItemRarity.EPIC, "earthquake", 180, "all_enemies"),
            ("태풍", ItemRarity.EPIC, "hurricane", 150, "all_enemies"),
            ("독성 가스", ItemRarity.EPIC, "toxic_gas", 130, "all_enemies"),
            ("연막탄", ItemRarity.RARE, "blind_enemies", 0, "all_enemies"),
            ("심판의 빛", ItemRarity.MYTHIC, "judgment", 500, "all_enemies"),
            ("종말의 화염", ItemRarity.MYTHIC, "apocalypse", 600, "all_enemies"),
            ("시공 붕괴", ItemRarity.MYTHIC, "spacetime_collapse", 700, "all_enemies"),
            
            # 🎯 특수 아이템 (24개) - 효과 유지
            ("도망치기 연기", ItemRarity.COMMON, "escape", 100, "party"),
            ("순간이동 두루마리", ItemRarity.RARE, "teleport", 100, "party"),
            ("방어막 두루마리", ItemRarity.RARE, "party_barrier", 50, "all_allies"),
            ("시간 정지 모래시계", ItemRarity.MYTHIC, "time_stop", 100, "all"),
            ("자동 부활 깃털", ItemRarity.LEGENDARY, "auto_revive", 100, "single"),
            ("행운의 동전", ItemRarity.EPIC, "luck_boost", 100, "party"),
            ("경험치 2배 책", ItemRarity.EPIC, "exp_double", 100, "party"),
            ("돈 2배 주머니", ItemRarity.EPIC, "gold_double", 100, "party"),
            ("아이템 발견 나침반", ItemRarity.RARE, "item_find", 100, "party"),
            ("적 정보 렌즈", ItemRarity.RARE, "enemy_scan", 100, "party"),
            ("함정 탐지기", ItemRarity.COMMON, "trap_detect", 100, "party"),
            ("벽 통과 망토", ItemRarity.LEGENDARY, "wall_pass", 100, "party"),
            ("투명화 포션", ItemRarity.EPIC, "invisibility", 100, "single"),
            ("거대화 약", ItemRarity.RARE, "giant_size", 100, "single"),
            ("축소화 약", ItemRarity.RARE, "mini_size", 100, "single"),
            ("변신술 주문서", ItemRarity.EPIC, "polymorph", 100, "single"),
            ("복제술 두루마리", ItemRarity.LEGENDARY, "duplicate", 100, "single"),
            ("시간 역행 시계", ItemRarity.MYTHIC, "time_reverse", 100, "party"),
            ("운명 조작 카드", ItemRarity.MYTHIC, "fate_change", 100, "all"),
            ("공간 이동문", ItemRarity.LEGENDARY, "portal", 100, "party"),
            ("차원 균열 생성기", ItemRarity.MYTHIC, "dimension_rift", 100, "all"),
            ("불굴의 의지약", ItemRarity.LEGENDARY, "willpower", 100, "single"),
            ("신의 축복약", ItemRarity.MYTHIC, "divine_blessing", 100, "all_allies"),
            ("완벽한 강화제", ItemRarity.MYTHIC, "perfect_boost", 150, "single"),
        ]
        
        for data in consumables_data:
            name, rarity, effect_type, value, target = data
            consumable = Consumable(name, rarity, effect_type, value, target)
            self.consumables[name] = consumable
    def get_consumable(self, item_name: str) -> Optional[Consumable]:
        """소모품 이름으로 소모품 반환"""
        return self.consumables.get(item_name)
    
    def get_random_consumable(self, rarity: ItemRarity = None) -> Optional[Consumable]:
        """랜덤 소모품 반환"""
        consumables = list(self.consumables.values())
        
        if rarity:
            consumables = [item for item in consumables if item.rarity == rarity]
        
        return random.choice(consumables) if consumables else None
    
    def get_consumables_by_level(self, level: int) -> List[Consumable]:
        """레벨에 맞는 소모품들 반환"""
        return [item for item in self.consumables.values() if item.level_requirement <= level]
    
    def get_consumables_by_effect(self, effect_type: str) -> List[Consumable]:
        """효과 타입별 소모품 반환"""
        return [item for item in self.consumables.values() if item.effect_type == effect_type]
    
    def get_healing_items(self) -> List[Consumable]:
        """치료 아이템들 반환"""
        healing_effects = ["heal_hp", "heal_mp", "heal_both", "full_heal", "divine_heal", "life_water", "perfect_heal"]
        return [item for item in self.consumables.values() if item.effect_type in healing_effects]
    
    def get_battle_items(self) -> List[Consumable]:
        """전투 아이템들 반환"""
        battle_effects = ["damage_single", "damage_area", "fire_damage", "ice_damage", "lightning_damage", 
                         "poison_damage", "holy_damage", "dark_damage", "big_explosion", "dragon_breath",
                         "divine_punishment", "hellfire", "absolute_zero", "thunder_god", "earthquake",
                         "hurricane", "toxic_gas", "judgment", "apocalypse", "spacetime_collapse"]
        return [item for item in self.consumables.values() if item.effect_type in battle_effects]
    
    def get_buff_items(self) -> List[Consumable]:
        """강화 아이템들 반환"""
        buff_effects = ["buff_attack", "buff_defense", "buff_speed", "buff_magic", "buff_all", 
                       "battle_boost", "hero_boost", "berserk", "focus", "reflex", "hp_boost",
                       "mp_boost", "regen_boost", "critical_boost", "accuracy_boost", "evasion_boost",
                       "resist_boost", "perfect_boost"]
        return [item for item in self.consumables.values() if item.effect_type in buff_effects]
    
    def get_special_items(self) -> List[Consumable]:
        """특수 아이템들 반환"""
        special_effects = ["escape", "teleport", "party_barrier", "time_stop", "auto_revive",
                          "luck_boost", "exp_double", "gold_double", "item_find", "enemy_scan",
                          "trap_detect", "wall_pass", "invisibility", "giant_size", "mini_size",
                          "polymorph", "duplicate", "time_reverse", "fate_change", "portal",
                          "dimension_rift", "willpower", "divine_blessing"]
        return [item for item in self.consumables.values() if item.effect_type in special_effects]

# 전역 소모품 데이터베이스
consumable_db = ConsumableDatabase()

def get_consumable_database():
    """소모품 데이터베이스 반환"""
    return consumable_db

def use_consumable(consumable: Consumable, user, target=None, party=None):
    """소모품 사용 함수"""
    if not consumable or consumable.uses_remaining <= 0:
        return False, "사용할 수 없는 아이템입니다."
    
    effect_type = consumable.effect_type
    value = consumable.effect_value
    target_type = consumable.target_type
    
    # 효과 적용 로직은 실제 게임 시스템에 맞게 구현
    success_message = f"{consumable.name}을(를) 사용했습니다."
    
    # 사용 횟수 감소
    consumable.uses_remaining -= 1
    
    return True, success_message
