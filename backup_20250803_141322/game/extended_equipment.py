#!/usr/bin/env python3
"""
확장된 장비 시스템
- 무기: 24종류 (근접 12개, 마법 6개, 원거리 6개)
- 방어구: 24종류 (상체 8개, 하체 8개, 머리 8개)
- 장신구: 24종류 (목 8개, 손 8개, 기타 8개)
"""

from enum import Enum
from typing import Dict, List, Optional, Any

class ExtendedWeaponCategory(Enum):
    """확장된 무기 카테고리 (24개)"""
    # 근접 무기 (12개)
    LONGSWORD = "장검"
    SHORTSWORD = "단검"
    KATANA = "카타나"
    SCIMITAR = "시미터"
    BATTLEAXE = "전투도끼"
    HATCHET = "손도끼"
    WARAXE = "전쟁도끼"
    PIKE = "파이크"
    SPEAR = "창"
    HALBERD = "미늘창"
    MACE = "철퇴"
    WARHAMMER = "전쟁망치"
    
    # 마법 무기 (6개)
    WIZARD_STAFF = "마법사지팡이"
    BATTLE_STAFF = "전투지팡이"
    CRYSTAL_WAND = "수정완드"
    ELEMENTAL_WAND = "속성완드"
    ORBS = "오브"
    GRIMOIRE = "마도서"
    
    # 원거리 무기 (6개)
    LONGBOW = "장궁"
    SHORTBOW = "단궁"
    CROSSBOW = "석궁"
    REPEATING_CROSSBOW = "연발석궁"
    THROWING_KNIVES = "투척칼"
    SLING = "투석기"

class ExtendedArmorCategory(Enum):
    """확장된 방어구 카테고리 (25개)"""
    # 상체 방어구 (9개)
    FULL_PLATE = "풀플레이트"
    HALF_PLATE = "하프플레이트"
    CHAIN_MAIL = "체인메일"
    SCALE_MAIL = "스케일메일"
    LEATHER_ARMOR = "가죽갑옷"
    STUDDED_LEATHER = "스터드가죽"
    PADDED_ARMOR = "패딩갑옷"
    MAGE_ROBE = "마법사로브"
    BATTLE_VEST = "전투조끼"
    
    # 하체 방어구 (8개)
    PLATE_GREAVES = "판금각반"
    CHAIN_GREAVES = "체인각반"
    SCALE_GREAVES = "스케일각반"
    LEATHER_PANTS = "가죽바지"
    CLOTH_PANTS = "천바지"
    REINFORCED_PANTS = "강화바지"
    BATTLE_SKIRT = "전투치마"
    MAGE_PANTS = "마법사바지"
    
    # 머리 방어구 (8개)
    GREAT_HELM = "그레이트헬름"
    BASCINET = "바시넷"
    CHAINMAIL_COIF = "체인코이프"
    LEATHER_CAP = "가죽모자"
    CLOTH_HAT = "천모자"
    BANDANA = "반다나"
    WIZARD_HAT = "마법사모자"
    CIRCLET = "서클릿"

class ExtendedAccessoryCategory(Enum):
    """확장된 장신구 카테고리 (24개)"""
    # 목 장신구 (8개)
    GOLD_NECKLACE = "금목걸이"
    SILVER_NECKLACE = "은목걸이"
    CRYSTAL_PENDANT = "수정펜던트"
    JEWELED_PENDANT = "보석펜던트"
    PROTECTIVE_AMULET = "보호부적"
    POWER_AMULET = "힘의부적"
    CHAIN_OF_BINDING = "구속의사슬"
    TORQUE = "토크"
    
    # 손 장신구 (8개)
    SIGNET_RING = "인장반지"
    BAND_RING = "밴드반지"
    JEWELED_RING = "보석반지"
    MAGIC_RING = "마법반지"
    LEATHER_GLOVES = "가죽장갑"
    SILK_GLOVES = "실크장갑"
    GAUNTLETS = "건틀릿"
    BRACERS = "브레이서"
    
    # 기타 장신구 (8개)
    STUD_EARRINGS = "스터드귀걸이"
    HOOP_EARRINGS = "후프귀걸이"
    LEATHER_BELT = "가죽벨트"
    CHAIN_BELT = "체인벨트"
    LEATHER_BOOTS = "가죽신발"
    METAL_BOOTS = "금속신발"
    SILK_CLOAK = "실크망토"
    FUR_CLOAK = "모피망토"

class ExtendedEquipmentGenerator:
    """확장된 장비 생성기"""
    
    def __init__(self):
        self.weapon_stats = self._init_weapon_stats()
        self.armor_stats = self._init_armor_stats()
        self.accessory_stats = self._init_accessory_stats()
        
        # 무기별 이름 템플릿 (티어별 6단계)
        self.weapon_names = {
            ExtendedWeaponCategory.LONGSWORD: ["철검", "강철검", "은검", "미스릴검", "드래곤검", "신검"],
            ExtendedWeaponCategory.SHORTSWORD: ["단검", "예리한단검", "은단검", "미스릴단검", "용단검", "신의단검"],
            ExtendedWeaponCategory.KATANA: ["카타나", "예리한카타나", "은카타나", "미스릴카타나", "용카타나", "신의카타나"],
            ExtendedWeaponCategory.SCIMITAR: ["시미터", "곡도", "은시미터", "미스릴시미터", "용시미터", "신의시미터"],
            ExtendedWeaponCategory.BATTLEAXE: ["전투도끼", "무거운도끼", "은도끼", "미스릴도끼", "용도끼", "신의도끼"],
            ExtendedWeaponCategory.HATCHET: ["손도끼", "예리한손도끼", "은손도끼", "미스릴손도끼", "용손도끼", "신의손도끼"],
            ExtendedWeaponCategory.WARAXE: ["전쟁도끼", "대형도끼", "은전쟁도끼", "미스릴전쟁도끼", "용전쟁도끼", "신의전쟁도끼"],
            ExtendedWeaponCategory.PIKE: ["파이크", "긴파이크", "은파이크", "미스릴파이크", "용파이크", "신의파이크"],
            ExtendedWeaponCategory.SPEAR: ["창", "긴창", "은창", "미스릴창", "용창", "신의창"],
            ExtendedWeaponCategory.HALBERD: ["미늘창", "전투미늘창", "은미늘창", "미스릴미늘창", "용미늘창", "신의미늘창"],
            ExtendedWeaponCategory.MACE: ["철퇴", "무거운철퇴", "은철퇴", "미스릴철퇴", "용철퇴", "신의철퇴"],
            ExtendedWeaponCategory.WARHAMMER: ["전쟁망치", "대형망치", "은망치", "미스릴망치", "용망치", "신의망치"],
            ExtendedWeaponCategory.WIZARD_STAFF: ["마법지팡이", "현자지팡이", "은지팡이", "미스릴지팡이", "용지팡이", "대마법사지팡이"],
            ExtendedWeaponCategory.BATTLE_STAFF: ["전투지팡이", "강화지팡이", "은전투지팡이", "미스릴전투지팡이", "용전투지팡이", "신의전투지팡이"],
            ExtendedWeaponCategory.CRYSTAL_WAND: ["수정완드", "투명수정완드", "은수정완드", "미스릴수정완드", "용수정완드", "신성수정완드"],
            ExtendedWeaponCategory.ELEMENTAL_WAND: ["속성완드", "강화속성완드", "은속성완드", "미스릴속성완드", "용속성완드", "신의속성완드"],
            ExtendedWeaponCategory.ORBS: ["마법구슬", "빛나는구슬", "은구슬", "미스릴구슬", "용구슬", "신의구슬"],
            ExtendedWeaponCategory.GRIMOIRE: ["마도서", "고대마도서", "은장마도서", "미스릴마도서", "용마도서", "신의마도서"],
            ExtendedWeaponCategory.LONGBOW: ["장궁", "강궁", "은장궁", "미스릴장궁", "용장궁", "신궁"],
            ExtendedWeaponCategory.SHORTBOW: ["단궁", "민첩한궁", "은단궁", "미스릴단궁", "용단궁", "신의단궁"],
            ExtendedWeaponCategory.CROSSBOW: ["석궁", "강화석궁", "은석궁", "미스릴석궁", "용석궁", "신의석궁"],
            ExtendedWeaponCategory.REPEATING_CROSSBOW: ["연발석궁", "고속석궁", "은연발석궁", "미스릴연발석궁", "용연발석궁", "신의연발석궁"],
            ExtendedWeaponCategory.THROWING_KNIVES: ["투척칼", "날카로운투척칼", "은투척칼", "미스릴투척칼", "용투척칼", "신의투척칼"],
            ExtendedWeaponCategory.SLING: ["투석기", "정밀투석기", "은투석기", "미스릴투석기", "용투석기", "신의투석기"]
        }
    
    def _init_weapon_stats(self) -> Dict:
        """무기별 기본 스탯 초기화"""
        return {
            # 근접 무기들
            ExtendedWeaponCategory.LONGSWORD: {"attack": (60, 120), "accuracy": 10, "critical": 0.05, "speed": 0},
            ExtendedWeaponCategory.SHORTSWORD: {"attack": (40, 80), "accuracy": 15, "critical": 0.08, "speed": 5},
            ExtendedWeaponCategory.KATANA: {"attack": (55, 110), "accuracy": 12, "critical": 0.12, "speed": 3},
            ExtendedWeaponCategory.SCIMITAR: {"attack": (50, 100), "accuracy": 13, "critical": 0.07, "speed": 4},
            ExtendedWeaponCategory.BATTLEAXE: {"attack": (80, 140), "accuracy": -5, "critical": 0.06, "speed": -5},
            ExtendedWeaponCategory.HATCHET: {"attack": (45, 85), "accuracy": 8, "critical": 0.04, "speed": 2},
            ExtendedWeaponCategory.WARAXE: {"attack": (90, 150), "accuracy": -8, "critical": 0.08, "speed": -8},
            ExtendedWeaponCategory.PIKE: {"attack": (70, 130), "accuracy": 5, "critical": 0.03, "speed": -3},
            ExtendedWeaponCategory.SPEAR: {"attack": (55, 115), "accuracy": 12, "critical": 0.04, "speed": 1},
            ExtendedWeaponCategory.HALBERD: {"attack": (75, 135), "accuracy": 0, "critical": 0.05, "speed": -4},
            ExtendedWeaponCategory.MACE: {"attack": (65, 125), "accuracy": 0, "critical": 0.04, "speed": -2},
            ExtendedWeaponCategory.WARHAMMER: {"attack": (85, 145), "accuracy": -3, "critical": 0.06, "speed": -6},
            
            # 마법 무기들
            ExtendedWeaponCategory.WIZARD_STAFF: {"attack": (40, 90), "magic_bonus": 25, "mp_bonus": 20, "speed": -1},
            ExtendedWeaponCategory.BATTLE_STAFF: {"attack": (60, 110), "magic_bonus": 15, "mp_bonus": 10, "speed": 0},
            ExtendedWeaponCategory.CRYSTAL_WAND: {"attack": (30, 70), "magic_bonus": 30, "mp_bonus": 25, "speed": 2},
            ExtendedWeaponCategory.ELEMENTAL_WAND: {"attack": (35, 75), "magic_bonus": 28, "mp_bonus": 15, "speed": 1},
            ExtendedWeaponCategory.ORBS: {"attack": (25, 65), "magic_bonus": 35, "mp_bonus": 30, "speed": 3},
            ExtendedWeaponCategory.GRIMOIRE: {"attack": (20, 60), "magic_bonus": 40, "mp_bonus": 35, "speed": -2},
            
            # 원거리 무기들
            ExtendedWeaponCategory.LONGBOW: {"attack": (50, 110), "accuracy": 15, "critical": 0.06, "range": 8},
            ExtendedWeaponCategory.SHORTBOW: {"attack": (40, 90), "accuracy": 18, "critical": 0.08, "range": 6},
            ExtendedWeaponCategory.CROSSBOW: {"attack": (70, 130), "accuracy": 20, "critical": 0.04, "range": 7},
            ExtendedWeaponCategory.REPEATING_CROSSBOW: {"attack": (45, 95), "accuracy": 12, "critical": 0.06, "range": 5},
            ExtendedWeaponCategory.THROWING_KNIVES: {"attack": (35, 75), "accuracy": 10, "critical": 0.12, "range": 4},
            ExtendedWeaponCategory.SLING: {"attack": (30, 70), "accuracy": 8, "critical": 0.03, "range": 6}
        }
    
    def _init_armor_stats(self) -> Dict:
        """방어구별 기본 스탯 초기화"""
        return {
            # 상체 방어구
            ExtendedArmorCategory.FULL_PLATE: {"defense": (50, 100), "hp_bonus": 30, "speed": -10},
            ExtendedArmorCategory.HALF_PLATE: {"defense": (40, 80), "hp_bonus": 20, "speed": -6},
            ExtendedArmorCategory.CHAIN_MAIL: {"defense": (35, 70), "hp_bonus": 15, "speed": -4},
            ExtendedArmorCategory.SCALE_MAIL: {"defense": (38, 75), "hp_bonus": 18, "speed": -5},
            ExtendedArmorCategory.LEATHER_ARMOR: {"defense": (25, 50), "hp_bonus": 10, "speed": 0},
            ExtendedArmorCategory.STUDDED_LEATHER: {"defense": (30, 60), "hp_bonus": 12, "speed": -1},
            ExtendedArmorCategory.PADDED_ARMOR: {"defense": (20, 40), "hp_bonus": 8, "speed": 1},
            ExtendedArmorCategory.MAGE_ROBE: {"defense": (15, 35), "mp_bonus": 25, "magic_defense": 20},
            
            # 하체 방어구
            ExtendedArmorCategory.PLATE_GREAVES: {"defense": (25, 50), "hp_bonus": 15, "speed": -5},
            ExtendedArmorCategory.CHAIN_GREAVES: {"defense": (20, 40), "hp_bonus": 10, "speed": -3},
            ExtendedArmorCategory.SCALE_GREAVES: {"defense": (22, 45), "hp_bonus": 12, "speed": -4},
            ExtendedArmorCategory.LEATHER_PANTS: {"defense": (15, 30), "hp_bonus": 5, "speed": 1},
            ExtendedArmorCategory.CLOTH_PANTS: {"defense": (10, 20), "mp_bonus": 10, "speed": 2},
            ExtendedArmorCategory.REINFORCED_PANTS: {"defense": (18, 35), "hp_bonus": 8, "speed": 0},
            ExtendedArmorCategory.BATTLE_SKIRT: {"defense": (16, 32), "hp_bonus": 6, "speed": 2},
            ExtendedArmorCategory.MAGE_PANTS: {"defense": (8, 18), "mp_bonus": 15, "magic_defense": 10},
            
            # 머리 방어구
            ExtendedArmorCategory.GREAT_HELM: {"defense": (20, 40), "hp_bonus": 10, "speed": -3},
            ExtendedArmorCategory.BASCINET: {"defense": (15, 30), "hp_bonus": 8, "speed": -2},
            ExtendedArmorCategory.CHAINMAIL_COIF: {"defense": (12, 25), "hp_bonus": 6, "speed": -1},
            ExtendedArmorCategory.LEATHER_CAP: {"defense": (8, 16), "hp_bonus": 3, "speed": 0},
            ExtendedArmorCategory.CLOTH_HAT: {"defense": (5, 10), "mp_bonus": 8, "speed": 1},
            ExtendedArmorCategory.BANDANA: {"defense": (3, 8), "speed": 2, "accuracy": 3},
            ExtendedArmorCategory.WIZARD_HAT: {"defense": (6, 12), "mp_bonus": 15, "magic_defense": 8},
            ExtendedArmorCategory.CIRCLET: {"defense": (4, 10), "mp_bonus": 12, "magic_defense": 6}
        }
    
    def _init_accessory_stats(self) -> Dict:
        """장신구별 기본 스탯 초기화"""
        return {
            # 목 장신구
            ExtendedAccessoryCategory.GOLD_NECKLACE: {"all_stats": 3, "value_bonus": 0.2},
            ExtendedAccessoryCategory.SILVER_NECKLACE: {"all_stats": 2, "value_bonus": 0.1},
            ExtendedAccessoryCategory.CRYSTAL_PENDANT: {"mp_bonus": 15, "magic_defense": 5},
            ExtendedAccessoryCategory.JEWELED_PENDANT: {"hp_bonus": 15, "defense": 3},
            ExtendedAccessoryCategory.PROTECTIVE_AMULET: {"defense": 8, "magic_defense": 8},
            ExtendedAccessoryCategory.POWER_AMULET: {"attack": 8, "magic_attack": 8},
            ExtendedAccessoryCategory.CHAIN_OF_BINDING: {"speed": -2, "defense": 12},
            ExtendedAccessoryCategory.TORQUE: {"hp_bonus": 20, "attack": 5},
            
            # 손 장신구
            ExtendedAccessoryCategory.SIGNET_RING: {"all_stats": 2, "leadership": 5},
            ExtendedAccessoryCategory.BAND_RING: {"speed": 3, "accuracy": 5},
            ExtendedAccessoryCategory.JEWELED_RING: {"mp_bonus": 10, "hp_bonus": 10},
            ExtendedAccessoryCategory.MAGIC_RING: {"magic_attack": 12, "mp_bonus": 8},
            ExtendedAccessoryCategory.LEATHER_GLOVES: {"accuracy": 8, "speed": 2},
            ExtendedAccessoryCategory.SILK_GLOVES: {"magic_attack": 6, "mp_bonus": 5},
            ExtendedAccessoryCategory.GAUNTLETS: {"attack": 10, "defense": 5},
            ExtendedAccessoryCategory.BRACERS: {"defense": 6, "accuracy": 4},
            
            # 기타 장신구
            ExtendedAccessoryCategory.STUD_EARRINGS: {"accuracy": 6, "critical": 0.02},
            ExtendedAccessoryCategory.HOOP_EARRINGS: {"speed": 4, "evasion": 3},
            ExtendedAccessoryCategory.LEATHER_BELT: {"hp_bonus": 8, "defense": 2},
            ExtendedAccessoryCategory.CHAIN_BELT: {"defense": 6, "speed": -1},
            ExtendedAccessoryCategory.LEATHER_BOOTS: {"speed": 5, "evasion": 2},
            ExtendedAccessoryCategory.METAL_BOOTS: {"defense": 8, "speed": -2},
            ExtendedAccessoryCategory.SILK_CLOAK: {"magic_defense": 10, "mp_bonus": 5},
            ExtendedAccessoryCategory.FUR_CLOAK: {"hp_bonus": 12, "cold_resist": 0.3}
        }

# 전역 확장 장비 생성기
extended_equipment_generator = ExtendedEquipmentGenerator()
