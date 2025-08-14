#!/usr/bin/env python3
"""
장비 아이템 생성 시스템
- 무기/방어구/장신구 종류별 개수 일치
- 밸런스 적용
- 티어별 스탯 조정
- 장비 강화 시스템
- 세트 아이템 시스템
"""

import random
from typing import Dict, List, Optional, Any
from enum import Enum

# balance_system import 오류 처리
try:
    from game.balance_system import (
        EquipmentType, WeaponCategory, ArmorCategory, AccessoryCategory,
        ElementType, get_equipment_stats
    )
except ImportError:
    # 기본 정의로 대체
    class EquipmentType(Enum):
        WEAPON = "weapon"
        ARMOR = "armor"
        ACCESSORY = "accessory"
    
    class WeaponCategory(Enum):
        SWORD = "sword"
        AXE = "axe"
        STAFF = "staff"
        BOW = "bow"
        DAGGER = "dagger"
    
    class ArmorCategory(Enum):
        HEAVY_ARMOR = "heavy_armor"
        LIGHT_ARMOR = "light_armor"
        ROBE = "robe"
    
    class AccessoryCategory(Enum):
        RING = "ring"
        NECKLACE = "necklace"
        EARRING = "earring"

class EnhancementType(Enum):
    """강화 타입"""
    ATTACK = "공격력"
    DEFENSE = "방어력"
    MAGIC = "마법력"
    SPEED = "속도"
    HP = "체력"
    MP = "마나"
    CRITICAL = "크리티컬"
    ACCURACY = "명중"
    EVASION = "회피"
    VISION = "시야"

class SetBonusType(Enum):
    """세트 보너스 타입"""
    WARRIOR_SET = "전사 세트"
    MAGE_SET = "마법사 세트"
    ARCHER_SET = "궁수 세트"
    ROGUE_SET = "도적 세트"
    PALADIN_SET = "성기사 세트"
    DRAGON_SET = "드래곤 세트"
    PHOENIX_SET = "피닉스 세트"
    VOID_SET = "공허 세트"

class ItemTier(Enum):
    """아이템 티어"""
    COMMON = ("일반", 1, "#FFFFFF")
    UNCOMMON = ("고급", 2, "#00FF00")
    RARE = ("희귀", 3, "#0080FF")
    EPIC = ("영웅", 4, "#8000FF")
    LEGENDARY = ("전설", 5, "#FF8000")
    MYTHIC = ("신화", 6, "#FF0000")

class EquipmentGenerator:
    """장비 생성기"""
    
    def __init__(self):
        # 각 카테고리별 이름 템플릿
        self.weapon_names = {
            WeaponCategory.SWORD: ["강철검", "은검", "미스릴검", "드래곤검", "성검", "파멸의검"],
            WeaponCategory.AXE: ["전투도끼", "은도끼", "미스릴도끼", "드래곤도끼", "성스러운도끼", "파괴의도끼"],
            WeaponCategory.SPEAR: ["긴창", "은창", "미스릴창", "드래곤창", "성창", "멸망의창"],
            WeaponCategory.MACE: ["철퇴", "은철퇴", "미스릴철퇴", "드래곤철퇴", "성철퇴", "심판의철퇴"],
            WeaponCategory.DAGGER: ["단검", "은단검", "미스릴단검", "드래곤단검", "성단검", "암살의단검"],
            WeaponCategory.STAFF: ["나무지팡이", "은지팡이", "미스릴지팡이", "드래곤지팡이", "성자의지팡이", "마도왕의지팡이"],
            WeaponCategory.WAND: ["마법봉", "은마법봉", "미스릴마법봉", "드래곤마법봉", "성스러운마법봉", "파멸의마법봉"],
            WeaponCategory.FIST: ["가죽장갑", "은장갑", "미스릴장갑", "드래곤장갑", "성스러운장갑", "파괴의장갑"],
            WeaponCategory.BOW: ["사냥활", "은활", "미스릴활", "드래곤활", "성활", "바람의활"],
            WeaponCategory.CROSSBOW: ["석궁", "은석궁", "미스릴석궁", "드래곤석궁", "성석궁", "관통의석궁"],
            WeaponCategory.GUN: ["화승총", "은총", "미스릴총", "드래곤총", "성총", "멸절의총"],
            WeaponCategory.THROWING: ["투척용칼", "은표창", "미스릴표창", "드래곤표창", "성표창", "파열의표창"]
        }
        
        self.armor_names = {
            # 상체
            ArmorCategory.HEAVY_ARMOR: ["판금갑옷", "은갑옷", "미스릴갑옷", "드래곤갑옷", "성기사갑옷", "불멸의갑옷"],
            ArmorCategory.LIGHT_ARMOR: ["가죽갑옷", "은경갑", "미스릴경갑", "드래곤경갑", "성스러운경갑", "바람의경갑"],
            ArmorCategory.ROBE: ["마법사로브", "은로브", "미스릴로브", "드래곤로브", "대마법사로브", "현자의로브"],
            ArmorCategory.LEATHER: ["단단한가죽옷", "은가죽옷", "미스릴가죽옷", "드래곤가죽옷", "성스러운가죽옷", "그림자가죽옷"],
            
            # 하체
            ArmorCategory.HEAVY_GREAVES: ["판금각반", "은각반", "미스릴각반", "드래곤각반", "성기사각반", "불멸의각반"],
            ArmorCategory.LIGHT_GREAVES: ["가죽각반", "은경각반", "미스릴경각반", "드래곤경각반", "성스러운경각반", "바람의경각반"],
            ArmorCategory.CLOTH_PANTS: ["천바지", "은천바지", "미스릴천바지", "드래곤천바지", "대마법사바지", "현자의바지"],
            ArmorCategory.LEATHER_PANTS: ["가죽바지", "은가죽바지", "미스릴가죽바지", "드래곤가죽바지", "성스러운가죽바지", "그림자가죽바지"],
            
            # 머리
            ArmorCategory.HELMET: ["철투구", "은투구", "미스릴투구", "드래곤투구", "성기사투구", "불멸의투구"],
            ArmorCategory.CAP: ["가죽모자", "은모자", "미스릴모자", "드래곤모자", "성스러운모자", "바람의모자"],
            ArmorCategory.HOOD: ["천후드", "은후드", "미스릴후드", "드래곤후드", "대마법사후드", "현자의후드"],
            ArmorCategory.CIRCLET: ["은서클릿", "미스릴서클릿", "드래곤서클릿", "성스러운서클릿", "현자의서클릿", "신성한서클릿"]
        }
        
        self.accessory_names = {
            # 목걸이류
            AccessoryCategory.NECKLACE: ["철목걸이", "은목걸이", "미스릴목걸이", "드래곤목걸이", "성스러운목걸이", "전설의목걸이"],
            AccessoryCategory.AMULET: ["수호부적", "은부적", "미스릴부적", "드래곤부적", "성스러운부적", "신성한부적"],
            AccessoryCategory.PENDANT: ["작은펜던트", "은펜던트", "미스릴펜던트", "드래곤펜던트", "성스러운펜던트", "전설의펜던트"],
            AccessoryCategory.CHAIN: ["철사슬", "은사슬", "미스릴사슬", "드래곤사슬", "성스러운사슬", "신성한사슬"],
            
            # 반지류
            AccessoryCategory.RING: ["철반지", "은반지", "미스릴반지", "드래곤반지", "성스러운반지", "전설의반지"],
            AccessoryCategory.SIGNET: ["작은인장", "은인장", "미스릴인장", "드래곤인장", "성스러운인장", "왕의인장"],
            AccessoryCategory.BAND: ["철밴드", "은밴드", "미스릴밴드", "드래곤밴드", "성스러운밴드", "신성한밴드"],
            AccessoryCategory.SEAL: ["봉인반지", "은봉인반지", "미스릴봉인반지", "드래곤봉인반지", "성스러운봉인반지", "절대봉인반지"],
            
            # 기타
            AccessoryCategory.EARRING: ["작은귀걸이", "은귀걸이", "미스릴귀걸이", "드래곤귀걸이", "성스러운귀걸이", "전설의귀걸이"],
            AccessoryCategory.BRACELET: ["철팔찌", "은팔찌", "미스릴팔찌", "드래곤팔찌", "성스러운팔찌", "신성한팔찌"],
            AccessoryCategory.BELT: ["가죽벨트", "은벨트", "미스릴벨트", "드래곤벨트", "성스러운벨트", "전설의벨트"],
            AccessoryCategory.CHARM: ["행운의부적", "은부적", "미스릴부적", "드래곤부적", "성스러운부적", "기적의부적"]
        }
    
    def generate_weapon(self, tier: ItemTier = ItemTier.COMMON, 
                       weapon_type: Optional[WeaponCategory] = None) -> Dict[str, Any]:
        """무기 생성"""
        if weapon_type is None:
            weapon_type = random.choice(list(WeaponCategory))
        
        # 장비 스탯 생성
        stats = get_equipment_stats("weapon", weapon_type.value, tier.value[1])
        
        # 이름 선택
        tier_index = tier.value[1] - 1
        name = self.weapon_names[weapon_type][tier_index]
        
        return {
            "name": name,
            "type": "weapon",
            "category": weapon_type.value,
            "tier": tier.value[0],
            "attack": stats.get("attack", 50),
            "accuracy_bonus": stats.get("accuracy_bonus", 0),
            "critical_bonus": stats.get("critical_bonus", 0.0),
            "element": stats.get("element", ElementType.NEUTRAL).value,
            "special": stats.get("special", ""),
            "value": self.calculate_value("weapon", tier),
            "description": f"{tier.value[0]} 등급의 {weapon_type.value}"
        }
    
    def generate_armor(self, tier: ItemTier = ItemTier.COMMON,
                      armor_type: Optional[ArmorCategory] = None) -> Dict[str, Any]:
        """방어구 생성"""
        if armor_type is None:
            armor_type = random.choice(list(ArmorCategory))
        
        # 장비 스탯 생성
        stats = get_equipment_stats("armor", armor_type.value, tier.value[1])
        
        # 이름 선택
        tier_index = tier.value[1] - 1
        name = self.armor_names[armor_type][tier_index]
        
        return {
            "name": name,
            "type": "armor",
            "category": armor_type.value,
            "tier": tier.value[0],
            "defense": stats.get("defense", 30),
            "speed_penalty": stats.get("speed_penalty", 0),
            "special": stats.get("special", ""),
            "value": self.calculate_value("armor", tier),
            "description": f"{tier.value[0]} 등급의 {armor_type.value}"
        }
    
    def generate_accessory(self, tier: ItemTier = ItemTier.COMMON,
                          accessory_type: Optional[AccessoryCategory] = None) -> Dict[str, Any]:
        """장신구 생성"""
        if accessory_type is None:
            accessory_type = random.choice(list(AccessoryCategory))
        
        # 장비 스탯 생성
        stats = get_equipment_stats("accessory", accessory_type.value, tier.value[1])
        
        # 이름 선택
        tier_index = tier.value[1] - 1
        name = self.accessory_names[accessory_type][tier_index]
        
        # 스탯 보너스 적용
        bonuses = {}
        for stat, value in stats.items():
            if stat != "special":
                bonuses[stat] = value
        
        return {
            "name": name,
            "type": "accessory",
            "category": accessory_type.value,
            "tier": tier.value[0],
            "stat_bonuses": bonuses,
            "special": stats.get("special", ""),
            "value": self.calculate_value("accessory", tier),
            "description": f"{tier.value[0]} 등급의 {accessory_type.value}"
        }
    
    def calculate_value(self, equipment_type: str, tier: ItemTier) -> int:
        """장비 가치 계산"""
        base_values = {
            "weapon": 100,
            "armor": 80,
            "accessory": 60
        }
        
        base_value = base_values.get(equipment_type, 50)
        tier_multiplier = tier.value[1] ** 1.5
        
        return int(base_value * tier_multiplier)
    
    def generate_random_equipment(self, tier: ItemTier = ItemTier.COMMON) -> Dict[str, Any]:
        """랜덤 장비 생성"""
        equipment_types = ["weapon", "armor", "accessory"]
        selected_type = random.choice(equipment_types)
        
        if selected_type == "weapon":
            return self.generate_weapon(tier)
        elif selected_type == "armor":
            return self.generate_armor(tier)
        else:
            return self.generate_accessory(tier)
    
    def generate_equipment_set(self, tier: ItemTier = ItemTier.COMMON) -> List[Dict[str, Any]]:
        """완전한 장비 세트 생성 (무기 1, 방어구 3, 장신구 3)"""
        equipment_set = []
        
        # 무기 1개
        equipment_set.append(self.generate_weapon(tier))
        
        # 방어구 3개 (상체, 하체, 머리)
        armor_types = [
            random.choice([ArmorCategory.HEAVY_ARMOR, ArmorCategory.LIGHT_ARMOR, 
                          ArmorCategory.ROBE, ArmorCategory.LEATHER]),
            random.choice([ArmorCategory.HEAVY_GREAVES, ArmorCategory.LIGHT_GREAVES,
                          ArmorCategory.CLOTH_PANTS, ArmorCategory.LEATHER_PANTS]),
            random.choice([ArmorCategory.HELMET, ArmorCategory.CAP,
                          ArmorCategory.HOOD, ArmorCategory.CIRCLET])
        ]
        
        for armor_type in armor_types:
            equipment_set.append(self.generate_armor(tier, armor_type))
        
        # 장신구 3개 (목걸이, 반지, 기타)
        accessory_types = [
            random.choice([AccessoryCategory.NECKLACE, AccessoryCategory.AMULET,
                          AccessoryCategory.PENDANT, AccessoryCategory.CHAIN]),
            random.choice([AccessoryCategory.RING, AccessoryCategory.SIGNET,
                          AccessoryCategory.BAND, AccessoryCategory.SEAL]),
            random.choice([AccessoryCategory.EARRING, AccessoryCategory.BRACELET,
                          AccessoryCategory.BELT, AccessoryCategory.CHARM])
        ]
        
        for accessory_type in accessory_types:
            equipment_set.append(self.generate_accessory(tier, accessory_type))
        
        return equipment_set

# 전역 장비 생성기
equipment_generator = EquipmentGenerator()

def generate_random_equipment(tier: str = "일반") -> Dict[str, Any]:
    """랜덤 장비 생성"""
    tier_map = {
        "일반": ItemTier.COMMON,
        "고급": ItemTier.UNCOMMON,
        "희귀": ItemTier.RARE,
        "영웅": ItemTier.EPIC,
        "전설": ItemTier.LEGENDARY,
        "신화": ItemTier.MYTHIC
    }
    
    item_tier = tier_map.get(tier, ItemTier.COMMON)
    return equipment_generator.generate_random_equipment(item_tier)

def generate_equipment_by_type(equipment_type: str, tier: str = "일반") -> Dict[str, Any]:
    """타입별 장비 생성"""
    tier_map = {
        "일반": ItemTier.COMMON,
        "고급": ItemTier.UNCOMMON,
        "희귀": ItemTier.RARE,
        "영웅": ItemTier.EPIC,
        "전설": ItemTier.LEGENDARY,
        "신화": ItemTier.MYTHIC
    }
    
    item_tier = tier_map.get(tier, ItemTier.COMMON)
    
    if equipment_type == "무기":
        return equipment_generator.generate_weapon(item_tier)
    elif equipment_type == "방어구":
        return equipment_generator.generate_armor(item_tier)
    elif equipment_type == "장신구":
        return equipment_generator.generate_accessory(item_tier)
    else:
        return equipment_generator.generate_random_equipment(item_tier)
