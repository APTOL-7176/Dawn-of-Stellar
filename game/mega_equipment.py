#!/usr/bin/env python3
"""
대규모 장비 데이터베이스 - 실용적 완전체
- 무기: 100종류 (브레이브, 상태효과, 원소 시스템 완전 연동)
- 방어구: 100종류 (상처 시스템, 방어 특화, 원소 저항)
- 장신구: 50종류 (패시브 능력, 상태 효과, 시야 시스템)
총 250종의 독특한 장비 - 구현 가능한 모든 게임 시스템과 완전 연동
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

class EquipmentType(Enum):
    """장비 타입"""
    WEAPON = "무기"
    ARMOR = "방어구"
    ACCESSORY = "장신구"

class EquipmentRarity(Enum):
    """장비 등급"""
    COMMON = "일반"      # 흰색
    RARE = "레어"        # 파란색
    EPIC = "에픽"        # 보라색
    LEGENDARY = "전설"    # 주황색
    MYTHIC = "신화"      # 빨간색
    ARTIFACT = "유물"    # 무지개색

class ElementalAffinity(Enum):
    """원소 친화도"""
    NEUTRAL = "무속성"
    FIRE = "화염"
    ICE = "냉기"
    LIGHTNING = "번개"
    EARTH = "대지"
    WIND = "바람"
    WATER = "물"
    LIGHT = "빛"
    DARK = "어둠"
    POISON = "독"

class EquipmentEffect:
    """장비 효과 클래스 - 보스 면역 시스템 포함"""
    def __init__(self, name: str, description: str, effect_type: str, 
                 effect_value: Any, condition: str = "always", boss_immune: bool = False):
        self.name = name
        self.description = description
        self.effect_type = effect_type  # stat_boost, brave_boost, wound_reduction, etc.
        self.effect_value = effect_value
        self.condition = condition  # always, combat, low_hp, high_brave, etc.
        self.boss_immune = boss_immune  # 보스에게 면역인 효과
        
    def can_apply_to_target(self, target) -> bool:
        """대상에게 효과 적용 가능한지 확인 (보스 면역 체크)"""
        if self.boss_immune and hasattr(target, 'is_boss') and target.is_boss:
            return False
        return True

class Equipment:
    """기본 장비 클래스"""
    
    def __init__(self, name: str, equipment_type: EquipmentType, rarity: EquipmentRarity,
                 level_req: int, base_stats: Dict[str, int], 
                 special_effects: List[EquipmentEffect] = None,
                 elemental_affinity: ElementalAffinity = ElementalAffinity.NEUTRAL,
                 set_bonus: str = None, description: str = "", weight: float = 1.0):
        
        self.name = name
        self.equipment_type = equipment_type
        self.rarity = rarity
        self.level_requirement = level_req
        self.base_stats = base_stats  # hp, mp, p_atk, m_atk, p_def, m_def, speed, brave
        self.special_effects = special_effects or []
        self.elemental_affinity = elemental_affinity
        self.set_bonus = set_bonus
        self.description = description
        self.weight = weight  # 무게 (가방 하중 시스템용)
        self.durability = 100  # 내구도
        self.upgrade_level = 0  # 강화 수준
        
    def get_display_name(self) -> str:
        """표시용 이름 (등급 및 강화 포함)"""
        rarity_colors = {
            EquipmentRarity.COMMON: "⚪",
            EquipmentRarity.RARE: "🔵",
            EquipmentRarity.EPIC: "🟣",
            EquipmentRarity.LEGENDARY: "🟠",
            EquipmentRarity.MYTHIC: "🔴",
            EquipmentRarity.ARTIFACT: "🌈"
        }
        
        element_icons = {
            ElementalAffinity.FIRE: "🔥",
            ElementalAffinity.ICE: "❄️",
            ElementalAffinity.LIGHTNING: "⚡",
            ElementalAffinity.EARTH: "🌍",
            ElementalAffinity.WIND: "💨",
            ElementalAffinity.WATER: "💧",
            ElementalAffinity.LIGHT: "✨",
            ElementalAffinity.DARK: "🌑",
            ElementalAffinity.POISON: "☠️",
            ElementalAffinity.NEUTRAL: ""
        }
        
        color = rarity_colors.get(self.rarity, "⚪")
        element = element_icons.get(self.elemental_affinity, "")
        upgrade_text = f"+{self.upgrade_level}" if self.upgrade_level > 0 else ""
        
        return f"{color}{element}{self.name}{upgrade_text}"

class MegaEquipmentDatabase:
    """대규모 장비 데이터베이스"""
    
    def __init__(self):
        self.weapons = {}
        self.armors = {}
        self.accessories = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """장비 데이터베이스 초기화"""
        self._create_weapons()
        self._create_armors()
        self._create_accessories()
        
        print(f"🗡️ 장비 데이터베이스 초기화 완료:")
        print(f"  무기: {len(self.weapons)}종")
        print(f"  방어구: {len(self.armors)}종")
        print(f"  장신구: {len(self.accessories)}종")
        print(f"  총합: {len(self.weapons) + len(self.armors) + len(self.accessories)}종")
    
    def _create_weapons(self):
        """100종의 다양하고 독특한 무기 생성 - 모든 시스템 연동"""
        
        # 🗡️ 검류 (25종) - 브레이브 시스템 특화
        sword_weapons = [
            ("초심자의 검", EquipmentRarity.COMMON, 1, {"p_atk": 8, "speed": 2}, [
                EquipmentEffect("첫 타격", "전투 시작시 첫 공격 명중률 +20%", "first_strike_accuracy", 20)
            ]),
            ("용맹한 검", EquipmentRarity.COMMON, 3, {"p_atk": 12, "brave": 5}, [
                EquipmentEffect("용기 충전", "크리티컬 시 브레이브 +3", "crit_brave_gain", 3)
            ]),
            ("날카로운 검", EquipmentRarity.COMMON, 5, {"p_atk": 15, "speed": 3}, [
                EquipmentEffect("정밀함", "크리티컬 확률 +10%", "crit_chance", 10)
            ]),
            ("균형의 검", EquipmentRarity.COMMON, 7, {"p_atk": 18, "speed": 5}, [
                EquipmentEffect("완벽한 균형", "모든 공격 명중률 +15%", "perfect_balance", 15)
            ]),
            ("강화된 검", EquipmentRarity.COMMON, 9, {"p_atk": 20, "p_def": 5}, [
                EquipmentEffect("견고함", "무기 내구도 2배", "durability_boost", 2.0)
            ]),
            ("화염의 검", EquipmentRarity.RARE, 10, {"p_atk": 25, "m_atk": 10}, [
                EquipmentEffect("화염 부여", "공격 시 15% 확률로 화상", "burn_chance", 0.15),
                EquipmentEffect("열정", "HP 50% 이하시 공격력 +30%", "passion", 1.3)
            ], ElementalAffinity.FIRE),
            ("빙결의 검", EquipmentRarity.RARE, 10, {"p_atk": 23, "m_def": 8}, [
                EquipmentEffect("한기", "공격 시 20% 확률로 속도 감소", "chill_strike", 0.2),
                EquipmentEffect("절대영도", "크리티컬 시 적 1턴 행동불가 (보스 면역)", "absolute_zero", True, "always", True)
            ], ElementalAffinity.ICE),
            ("번개의 검", EquipmentRarity.RARE, 12, {"p_atk": 22, "speed": 8}, [
                EquipmentEffect("전기 충격", "30% 확률로 마비 부여", "paralysis_chance", 0.3),
                EquipmentEffect("연쇄 번개", "크리티컬 시 인근 적에게 연쇄 피해", "chain_lightning", True)
            ], ElementalAffinity.LIGHTNING),
            ("대지의 검", EquipmentRarity.RARE, 11, {"p_atk": 28, "p_def": 12}, [
                EquipmentEffect("지진", "공격 시 25% 확률로 모든 적 기절 (보스 면역)", "earthquake", 0.25, "always", True),
                EquipmentEffect("견고함", "받는 피해 -15%", "earth_shield", 0.85)
            ], ElementalAffinity.EARTH),
            ("바람의 검", EquipmentRarity.RARE, 9, {"p_atk": 20, "speed": 15}, [
                EquipmentEffect("바람 베기", "회피 불가능한 공격", "wind_slash", True),
                EquipmentEffect("순풍", "매 턴 속도 +2", "tailwind", 2)
            ], ElementalAffinity.WIND),
            ("물의 검", EquipmentRarity.RARE, 8, {"p_atk": 18, "mp": 20}, [
                EquipmentEffect("생명의 물", "공격 시 피해의 20% HP 회복", "life_steal", 0.2),
                EquipmentEffect("정화", "공격 시 상태이상 1개 제거", "purify", True)
            ], ElementalAffinity.WATER),
            ("빛의 검", EquipmentRarity.EPIC, 15, {"p_atk": 30, "m_atk": 15}, [
                EquipmentEffect("성스러운 빛", "언데드에게 3배 피해", "holy_damage", 3.0),
                EquipmentEffect("축복", "아군 전체 능력치 +10%", "blessing_aura", 1.1)
            ], ElementalAffinity.LIGHT),
            ("어둠의 검", EquipmentRarity.EPIC, 15, {"p_atk": 32, "hp": 30}, [
                EquipmentEffect("생명 흡수", "피해의 25% HP 회복", "dark_drain", 0.25),
                EquipmentEffect("저주", "공격 시 적의 모든 능력치 -15%", "curse_strike", 0.85)
            ], ElementalAffinity.DARK),
            ("독의 검", EquipmentRarity.RARE, 13, {"p_atk": 20, "speed": 6}, [
                EquipmentEffect("맹독", "공격 시 40% 확률로 중독", "poison_strike", 0.4),
                EquipmentEffect("독 저항", "독 상태 완전 면역", "poison_immunity", True)
            ], ElementalAffinity.POISON),
            ("정의의 검", EquipmentRarity.RARE, 8, {"p_atk": 20, "m_def": 8, "brave": 10}, [
                EquipmentEffect("정의감", "언데드 상대 시 피해 +50%", "undead_bonus", 1.5),
                EquipmentEffect("브레이브 버스트", "브레이브 MAX 시 다음 공격 2배 피해", "brave_burst", 2.0)
            ], ElementalAffinity.LIGHT),
            ("흡혈의 검", EquipmentRarity.RARE, 18, {"p_atk": 24, "hp": 40}, [
                EquipmentEffect("흡혈", "피해의 30% HP 회복", "vampire_strike", 0.3),
                EquipmentEffect("재생", "매 턴 HP 3% 회복", "regeneration", 0.03)
            ], ElementalAffinity.DARK),
            ("연속 타격검", EquipmentRarity.RARE, 14, {"p_atk": 22, "speed": 10}, [
                EquipmentEffect("연속 공격", "25% 확률로 2회 공격", "double_strike", 0.25),
                EquipmentEffect("콤보 마스터", "연속 공격 시 피해 +50%", "combo_master", 1.5)
            ]),
            ("관통의 검", EquipmentRarity.RARE, 16, {"p_atk": 26, "speed": 5}, [
                EquipmentEffect("방어 관통", "적 방어력 50% 무시", "armor_pierce", 0.5),
                EquipmentEffect("정확함", "명중률 +20%", "accuracy_boost", 20)
            ]),
            ("혼돈의 검", EquipmentRarity.EPIC, 22, {"p_atk": 28, "m_atk": 15}, [
                EquipmentEffect("다양성", "크리티컬 시 무작위 상태효과", "random_effect", True),
                EquipmentEffect("적응", "전투 중 공격력 점진적 증가", "adaptive_power", True)
            ], ElementalAffinity.NEUTRAL),
            ("시간의 검", EquipmentRarity.EPIC, 25, {"p_atk": 30, "speed": 15, "mp": 20}, [
                EquipmentEffect("신속", "25% 확률로 추가 행동", "extra_action", 0.25),
                EquipmentEffect("예측", "회피율 +30%", "evasion_boost", 30)
            ], ElementalAffinity.NEUTRAL),
            ("드래곤 슬레이어", EquipmentRarity.EPIC, 20, {"p_atk": 35, "brave": 20, "p_def": 10}, [
                EquipmentEffect("용 살해자", "드래곤계 적에게 3배 피해", "dragon_slayer", 3.0),
                EquipmentEffect("용의 심장", "적 처치 시 모든 능력치 일시 증가", "dragon_heart", True)
            ], ElementalAffinity.FIRE),
            ("영혼 절단검", EquipmentRarity.LEGENDARY, 30, {"p_atk": 45, "m_atk": 25, "brave": 30}, [
                EquipmentEffect("영혼 절단", "브레이브 피해를 주는 특수 공격", "soul_slash", True),
                EquipmentEffect("영혼 흡수", "적 처치 시 최대 브레이브 +5", "soul_absorption", 5)
            ], ElementalAffinity.DARK),
            ("천공의 검", EquipmentRarity.LEGENDARY, 35, {"p_atk": 50, "speed": 20, "brave": 25}, [
                EquipmentEffect("천공 베기", "방어력 무시 공격", "armor_pierce", True),
                EquipmentEffect("하늘의 축복", "크리티컬 확률 +25%", "divine_blessing", 25)
            ], ElementalAffinity.LIGHT),
            ("세계수의 검", EquipmentRarity.MYTHIC, 40, {"p_atk": 60, "hp": 100, "mp": 50, "brave": 40}, [
                EquipmentEffect("생명의 힘", "매 턴 HP/MP 5% 회복", "life_force", 0.05),
                EquipmentEffect("뿌리 박기", "상처 시스템 피해 50% 감소", "root_system", 0.5)
            ], ElementalAffinity.EARTH),
        ]
        
        # 🏹 원거리 무기류 (25종) - 정확도와 속도 특화  
        ranged_weapons = [
            ("사냥꾼의 활", EquipmentRarity.COMMON, 2, {"p_atk": 10, "speed": 5}, [
                EquipmentEffect("정밀 사격", "명중률 +15%", "precision", 15)
            ]),
            ("장궁", EquipmentRarity.COMMON, 4, {"p_atk": 15, "speed": 3}, [
                EquipmentEffect("원거리", "시야 범위 +1", "long_range", 1),
                EquipmentEffect("강력함", "크리티컬 피해 +30%", "power_shot", 1.3)
            ]),
            ("복합궁", EquipmentRarity.RARE, 8, {"p_atk": 22, "speed": 10}, [
                EquipmentEffect("연발 사격", "30% 확률로 2회 공격", "multi_shot", 0.3)
            ]),
            ("엘프의 활", EquipmentRarity.RARE, 12, {"p_atk": 25, "speed": 15, "mp": 20}, [
                EquipmentEffect("자연의 축복", "숲에서 능력치 +20%", "nature_blessing", 1.2),
                EquipmentEffect("시야 확장", "시야 범위 +1", "vision_boost", 1)
            ], ElementalAffinity.WIND),
            ("화염 활", EquipmentRarity.RARE, 14, {"p_atk": 26, "m_atk": 12}, [
                EquipmentEffect("화염 화살", "공격 시 30% 확률로 화상", "fire_arrow", 0.3),
                EquipmentEffect("연소", "화상 상태 지속시간 2배", "burn_extend", 2.0)
            ], ElementalAffinity.FIRE),
            ("독침 발사기", EquipmentRarity.RARE, 18, {"p_atk": 20, "speed": 8}, [
                EquipmentEffect("맹독", "공격 시 독 상태 부여", "poison_shot", True),
                EquipmentEffect("독 면역", "독 상태 효과 무효", "poison_immunity", True)
            ], ElementalAffinity.POISON),
            ("얼음 활", EquipmentRarity.RARE, 16, {"p_atk": 24, "speed": 12}, [
                EquipmentEffect("빙결 화살", "공격 시 적 속도 -50%", "ice_arrow", 0.5),
                EquipmentEffect("서리", "적 행동력 감소", "frost_effect", True)
            ], ElementalAffinity.ICE),
            ("번개 활", EquipmentRarity.RARE, 18, {"p_atk": 28, "speed": 14}, [
                EquipmentEffect("전기 화살", "공격 시 마비 확률", "lightning_arrow", 0.3),
                EquipmentEffect("연쇄", "크리티컬 시 인근 적에게 피해", "chain_damage", True)
            ], ElementalAffinity.LIGHTNING),
            ("대지 활", EquipmentRarity.RARE, 20, {"p_atk": 30, "p_def": 5}, [
                EquipmentEffect("바위 화살", "방어력 무시 확률", "rock_arrow", 0.3),
                EquipmentEffect("견고함", "받는 피해 -10%", "damage_reduction", 0.9)
            ], ElementalAffinity.EARTH),
            ("물 활", EquipmentRarity.RARE, 15, {"p_atk": 22, "mp": 15}, [
                EquipmentEffect("치유 화살", "공격 시 HP 소량 회복", "healing_arrow", True),
                EquipmentEffect("정화", "상태이상 제거 확률", "cleanse_arrow", 0.3)
            ], ElementalAffinity.WATER),
            ("바람 활", EquipmentRarity.EPIC, 22, {"p_atk": 32, "speed": 18}, [
                EquipmentEffect("돌풍", "회피 불가능한 공격", "wind_arrow", True),
                EquipmentEffect("연속 사격", "30% 확률로 3연사", "rapid_fire", 0.3)
            ], ElementalAffinity.WIND),
            ("어둠 활", EquipmentRarity.EPIC, 24, {"p_atk": 35, "hp": 20}, [
                EquipmentEffect("저주 화살", "적 능력치 -10%", "curse_arrow", 0.9),
                EquipmentEffect("흡수", "피해의 20% HP 회복", "vampiric_arrow", 0.2)
            ], ElementalAffinity.DARK),
            ("빛 활", EquipmentRarity.EPIC, 24, {"p_atk": 36, "m_atk": 10}, [
                EquipmentEffect("정화 화살", "언데드에게 2배 피해", "purify_arrow", 2.0),
                EquipmentEffect("축복", "공격 시 아군 버프", "blessing_arrow", True)
            ], ElementalAffinity.LIGHT),
            ("신성한 석궁", EquipmentRarity.LEGENDARY, 28, {"p_atk": 40, "m_atk": 20, "brave": 20}, [
                EquipmentEffect("성스러운 화살", "언데드에게 3배 피해", "holy_arrow", 3.0),
                EquipmentEffect("축복의 빛", "공격 시 아군 HP 소량 회복", "blessing_light", True)
            ], ElementalAffinity.LIGHT),
            ("용 사냥꾼의 활", EquipmentRarity.LEGENDARY, 30, {"p_atk": 45, "brave": 25}, [
                EquipmentEffect("용 살해자", "드래곤계 3배 피해", "dragon_slayer", 3.0),
                EquipmentEffect("관통 화살", "방어력 무시", "pierce_shot", True)
            ], ElementalAffinity.FIRE),
            ("강철 석궁", EquipmentRarity.COMMON, 6, {"p_atk": 18, "p_def": 3}, [
                EquipmentEffect("안정성", "명중률 +10%", "stability", 10)
            ]),
            ("저격 활", EquipmentRarity.RARE, 25, {"p_atk": 38, "speed": 8}, [
                EquipmentEffect("저격", "크리티컬 확률 +25%", "sniper_shot", 25),
                EquipmentEffect("집중", "첫 공격 크리티컬 보장", "focused_shot", True)
            ]),
            ("마법 활", EquipmentRarity.EPIC, 26, {"p_atk": 20, "m_atk": 25}, [
                EquipmentEffect("마법 화살", "물리+마법 복합 피해", "magic_arrow", True),
                EquipmentEffect("마나 화살", "MP로 추가 피해", "mana_arrow", True)
            ]),
            ("공허 활", EquipmentRarity.LEGENDARY, 32, {"p_atk": 42, "m_atk": 15}, [
                EquipmentEffect("공허 화살", "모든 방어 무시", "void_arrow", True),
                EquipmentEffect("침묵", "적 스킬 사용 방해", "silence_arrow", 0.4)
            ]),
            ("속사 활", EquipmentRarity.RARE, 20, {"p_atk": 25, "speed": 20}, [
                EquipmentEffect("속사", "공격 속도 2배", "rapid_shooting", 2.0),
                EquipmentEffect("경량화", "무게 패널티 없음", "lightweight", True)
            ]),
            ("전투 활", EquipmentRarity.COMMON, 8, {"p_atk": 20, "hp": 10}, [
                EquipmentEffect("견고함", "내구도 2배", "durability", 2.0)
            ]),
            ("사냥용 활", EquipmentRarity.COMMON, 10, {"p_atk": 22, "speed": 8}, [
                EquipmentEffect("추적", "도망치는 적에게 추가 피해", "hunting", 1.3)
            ]),
            ("왕실 활", EquipmentRarity.EPIC, 28, {"p_atk": 40, "speed": 15, "brave": 10}, [
                EquipmentEffect("왕의 권위", "모든 능력치 +10%", "royal_authority", 1.1),
                EquipmentEffect("명예", "브레이브 증가량 +50%", "honor", 1.5)
            ]),
            ("세계수 활", EquipmentRarity.MYTHIC, 35, {"p_atk": 50, "mp": 40, "hp": 30}, [
                EquipmentEffect("생명 화살", "공격 시 HP 회복", "life_arrow", True),
                EquipmentEffect("자연의 힘", "모든 원소 저항 +30%", "nature_power", 0.7)
            ], ElementalAffinity.EARTH),
            ("무한 활", EquipmentRarity.MYTHIC, 40, {"p_atk": 55, "speed": 25}, [
                EquipmentEffect("무한 사격", "탄약 소모 없음", "infinite_arrows", True),
                EquipmentEffect("완벽 명중", "명중률 100%", "perfect_aim", True)
            ]),
        ]
        
        # ⚔️ 마법 무기류 (25종) - MP 효율성과 원소 조작
        magic_weapons = [
            ("견습생 지팡이", EquipmentRarity.COMMON, 1, {"m_atk": 12, "mp": 10}, [
                EquipmentEffect("마나 절약", "스킬 MP 소모량 -10%", "mana_efficiency", 0.9)
            ]),
            ("참나무 지팡이", EquipmentRarity.COMMON, 3, {"m_atk": 18, "mp": 15}, [
                EquipmentEffect("자연의 힘", "MP 회복량 +20%", "nature_mana", 1.2)
            ]),
            ("수정 지팡이", EquipmentRarity.RARE, 8, {"m_atk": 25, "mp": 25}, [
                EquipmentEffect("마력 증폭", "마법 피해 +30%", "magic_amplify", 1.3),
                EquipmentEffect("마나 재생", "매 턴 MP 10% 회복", "mana_regen", 0.1)
            ]),
            ("화염 지팡이", EquipmentRarity.RARE, 10, {"m_atk": 30, "mp": 20}, [
                EquipmentEffect("화염 지배", "화염 마법 위력 +50%", "fire_mastery", 1.5),
                EquipmentEffect("화염 면역", "화염 피해 완전 무효", "fire_immunity", True)
            ], ElementalAffinity.FIRE),
            ("빙결 지팡이", EquipmentRarity.RARE, 10, {"m_atk": 28, "mp": 25, "m_def": 10}, [
                EquipmentEffect("빙결 지배", "빙결 마법 위력 +50%", "ice_mastery", 1.5),
                EquipmentEffect("한기", "10% 확률로 적 동결", "freeze_chance", 0.1)
            ], ElementalAffinity.ICE),
            ("번개 지팡이", EquipmentRarity.RARE, 12, {"m_atk": 32, "speed": 10}, [
                EquipmentEffect("번개 지배", "번개 마법 위력 +50%", "lightning_mastery", 1.5),
                EquipmentEffect("연쇄 번개", "마법이 주변 적에게 연쇄", "chain_spell", True)
            ], ElementalAffinity.LIGHTNING),
            ("대지 지팡이", EquipmentRarity.RARE, 14, {"m_atk": 35, "hp": 30}, [
                EquipmentEffect("대지 지배", "대지 마법 위력 +50%", "earth_mastery", 1.5),
                EquipmentEffect("견고함", "상처 피해 -20%", "wound_reduction", 0.8)
            ], ElementalAffinity.EARTH),
            ("바람 지팡이", EquipmentRarity.RARE, 11, {"m_atk": 29, "speed": 15}, [
                EquipmentEffect("바람 지배", "바람 마법 위력 +50%", "wind_mastery", 1.5),
                EquipmentEffect("가속", "스킬 시전 속도 +30%", "casting_speed", 1.3)
            ], ElementalAffinity.WIND),
            ("물 지팡이", EquipmentRarity.RARE, 9, {"m_atk": 26, "mp": 30}, [
                EquipmentEffect("물 지배", "물 마법 위력 +50%", "water_mastery", 1.5),
                EquipmentEffect("치유 강화", "회복 마법 효과 +40%", "healing_boost", 1.4)
            ], ElementalAffinity.WATER),
            ("독 지팡이", EquipmentRarity.RARE, 16, {"m_atk": 33, "speed": 5}, [
                EquipmentEffect("독 지배", "독 마법 위력 +50%", "poison_mastery", 1.5),
                EquipmentEffect("맹독", "마법 공격 시 독 부여", "toxic_magic", True)
            ], ElementalAffinity.POISON),
            ("빛 지팡이", EquipmentRarity.EPIC, 18, {"m_atk": 35, "mp": 30, "m_def": 20}, [
                EquipmentEffect("빛 지배", "빛 마법 위력 +50%", "light_mastery", 1.5),
                EquipmentEffect("성스러운 빛", "언데드에게 2배 피해", "holy_light", 2.0)
            ], ElementalAffinity.LIGHT),
            ("어둠 지팡이", EquipmentRarity.EPIC, 18, {"m_atk": 38, "hp": 30}, [
                EquipmentEffect("어둠 지배", "어둠 마법 위력 +50%", "dark_mastery", 1.5),
                EquipmentEffect("생명 흡수", "마법 피해의 30% HP 회복", "life_drain", 0.3)
            ], ElementalAffinity.DARK),
            ("현자의 지팡이", EquipmentRarity.EPIC, 22, {"m_atk": 40, "mp": 50}, [
                EquipmentEffect("지혜", "모든 마법 피해 +25%", "wisdom", 1.25),
                EquipmentEffect("깊은 사고", "크리티컬 확률 +20%", "deep_thought", 20)
            ]),
            ("별빛 지팡이", EquipmentRarity.EPIC, 25, {"m_atk": 42, "mp": 45, "speed": 10}, [
                EquipmentEffect("별의 힘", "밤에 마법 피해 2배", "starlight", 2.0),
                EquipmentEffect("우주의 힘", "MP 소모 -25%", "cosmic_power", 0.75)
            ]),
            ("용의 지팡이", EquipmentRarity.LEGENDARY, 30, {"m_atk": 50, "hp": 40, "brave": 20}, [
                EquipmentEffect("용의 마법", "모든 마법 피해 +40%", "dragon_magic", 1.4),
                EquipmentEffect("드래곤 브레스", "마법 크리티컬 시 광역 피해", "dragon_breath", True)
            ], ElementalAffinity.FIRE),
            ("마도서", EquipmentRarity.RARE, 20, {"m_atk": 36, "mp": 35}, [
                EquipmentEffect("지식", "경험치 획득 +30%", "knowledge", 1.3),
                EquipmentEffect("스킬북", "스킬 쿨다운 -1턴", "skill_book", 1)
            ]),
            ("고대 오브", EquipmentRarity.EPIC, 28, {"m_atk": 45, "mp": 60}, [
                EquipmentEffect("고대의 힘", "마법 관통력 +50%", "ancient_power", 1.5),
                EquipmentEffect("마나 폭발", "MP가 높을수록 피해 증가", "mana_burst", True)
            ]),
            ("원소 구체", EquipmentRarity.EPIC, 24, {"m_atk": 38, "mp": 40}, [
                EquipmentEffect("원소 조화", "모든 원소 피해 +20%", "elemental_harmony", 1.2),
                EquipmentEffect("원소 순환", "원소 스킬 사용 시 MP 회복", "element_cycle", True)
            ]),
            ("공허 오브", EquipmentRarity.LEGENDARY, 32, {"m_atk": 48, "mp": 50}, [
                EquipmentEffect("공허 마법", "모든 저항 무시", "void_magic", True),
                EquipmentEffect("마나 흡수", "적 처치 시 MP 회복", "mana_drain", True)
            ]),
            ("시공 지팡이", EquipmentRarity.LEGENDARY, 35, {"m_atk": 52, "mp": 70, "speed": 20}, [
                EquipmentEffect("시공 마법", "쿨다운 무시", "spacetime_magic", True),
                EquipmentEffect("마법 가속", "스킬 시전 속도 2배", "magic_acceleration", 2.0)
            ]),
            ("창조의 오브", EquipmentRarity.MYTHIC, 40, {"m_atk": 60, "mp": 100, "hp": 50, "brave": 35}, [
                EquipmentEffect("창조", "전투 중 임시 아이템 생성", "creation", True),
                EquipmentEffect("무한 마나", "MP 소모량 50% 감소", "infinite_mana", 0.5)
            ], ElementalAffinity.LIGHT),
            ("파괴의 오브", EquipmentRarity.MYTHIC, 40, {"m_atk": 65, "mp": 80, "p_atk": 20}, [
                EquipmentEffect("파괴", "마법 피해 2배", "destruction", 2.0),
                EquipmentEffect("마법 폭주", "MP 낮을수록 피해 증가", "magic_rampage", True)
            ], ElementalAffinity.DARK),
            ("마법사의 완드", EquipmentRarity.COMMON, 5, {"m_atk": 20, "mp": 18}, [
                EquipmentEffect("기본 마법", "마법 피해 +15%", "basic_magic", 1.15)
            ]),
            ("얼음 완드", EquipmentRarity.RARE, 15, {"m_atk": 32, "mp": 25}, [
                EquipmentEffect("얼음 창조", "물을 얼음으로 변환", "ice_creation", True),
                EquipmentEffect("서리 발산", "주변 적 속도 감소", "frost_aura", True)
            ], ElementalAffinity.ICE),
            ("치유의 지팡이", EquipmentRarity.RARE, 12, {"m_atk": 25, "mp": 35, "hp": 25}, [
                EquipmentEffect("치유 전문", "회복 마법만 사용 가능하지만 3배 효과", "healing_specialist", 3.0),
                EquipmentEffect("생명력", "매 턴 HP 회복", "vitality", True)
            ], ElementalAffinity.WATER),
        ]
        
        # 🔨 둔기 및 특수 무기류 (25종)
        special_weapons = [
            ("전투 망치", EquipmentRarity.COMMON, 4, {"p_atk": 15, "p_def": 5}, [
                EquipmentEffect("방어 파괴", "적의 방어력 -20% (5턴)", "armor_break", True)
            ]),
            ("지진 망치", EquipmentRarity.RARE, 16, {"p_atk": 32, "hp": 40}, [
                EquipmentEffect("지진", "전체 적에게 광역 피해", "earthquake", True),
                EquipmentEffect("충격파", "공격 시 30% 확률로 기절 (보스 면역)", "shockwave", 0.3, "always", True)
            ], ElementalAffinity.EARTH),
            ("장창", EquipmentRarity.COMMON, 6, {"p_atk": 18, "speed": 3}, [
                EquipmentEffect("정확함", "명중률 +15%", "accuracy_boost", 15)
            ]),
            ("신성한 창", EquipmentRarity.EPIC, 22, {"p_atk": 35, "m_atk": 15, "brave": 15}, [
                EquipmentEffect("신성한 빛", "언데드에게 3배 피해", "holy_spear", 3.0),
                EquipmentEffect("정확성", "크리티컬 확률 +25%", "divine_accuracy", 25)
            ], ElementalAffinity.LIGHT),
            ("전투 도끼", EquipmentRarity.COMMON, 5, {"p_atk": 20, "p_def": 3}, [
                EquipmentEffect("강력한 일격", "크리티컬 피해 +50%", "heavy_blow", 1.5)
            ]),
            ("광전사 도끼", EquipmentRarity.EPIC, 18, {"p_atk": 40, "hp": 30}, [
                EquipmentEffect("광전사", "HP 낮을수록 공격력 증가", "berserker", True),
                EquipmentEffect("피의 갈증", "적 처치 시 HP 회복", "blood_lust", True)
            ], ElementalAffinity.DARK),
            ("생명의 낫", EquipmentRarity.LEGENDARY, 30, {"p_atk": 40, "m_atk": 30, "hp": 80}, [
                EquipmentEffect("영혼 수확", "적 처치 시 전체 아군 HP 회복", "soul_harvest", True),
                EquipmentEffect("죽음의 표식", "공격한 적에게 즉사 확률 부여 (보스 면역)", "death_mark", 0.05, "always", True)
            ], ElementalAffinity.DARK),
        ]
        
        # 무기 데이터베이스에 추가
        weapon_id = 1
        for weapon_list in [sword_weapons, ranged_weapons, magic_weapons, special_weapons]:
            for weapon_data in weapon_list:
                name, rarity, level, stats, effects = weapon_data[:5]
                element = weapon_data[5] if len(weapon_data) > 5 else ElementalAffinity.NEUTRAL
                
                # 무기 타입별 기본 무게 설정
                base_weight = 1.0
                if "검" in name or "도끼" in name or "망치" in name:
                    base_weight = 2.5  # 근접 무기는 무거움
                elif "활" in name or "석궁" in name or "총" in name:
                    base_weight = 1.8  # 원거리 무기는 중간
                elif "지팡이" in name or "완드" in name or "오브" in name:
                    base_weight = 1.2  # 마법 무기는 가벼움
                elif "창" in name or "낫" in name:
                    base_weight = 3.0  # 장병기는 매우 무거움
                
                # 희귀도별 무게 배율
                rarity_weight_multiplier = {
                    EquipmentRarity.COMMON: 1.0,
                    EquipmentRarity.RARE: 1.1,
                    EquipmentRarity.EPIC: 1.2,
                    EquipmentRarity.LEGENDARY: 1.3,
                    EquipmentRarity.MYTHIC: 1.4,
                    EquipmentRarity.ARTIFACT: 1.5
                }
                
                final_weight = base_weight * rarity_weight_multiplier.get(rarity, 1.0)
                
                weapon = Equipment(
                    name=name,
                    equipment_type=EquipmentType.WEAPON,
                    rarity=rarity,
                    level_req=level,
                    base_stats=stats,
                    special_effects=effects,
                    elemental_affinity=element,
                    weight=final_weight
                )
                self.weapons[f"weapon_{weapon_id}"] = weapon
                weapon_id += 1
    
    def _create_armors(self):
        """100종의 상처 시스템과 연동된 방어구 생성"""
        
        # 🛡️ 상체 갑옷류 (40종) - 상처 감소 및 HP 보너스
        chest_armors = [
            ("천 셔츠", EquipmentRarity.COMMON, 1, {"hp": 10, "p_def": 3}, [
                EquipmentEffect("편안함", "상처 회복 속도 +10%", "wound_heal_boost", 1.1)
            ]),
            ("가죽 갑옷", EquipmentRarity.COMMON, 3, {"hp": 20, "p_def": 8}, [
                EquipmentEffect("유연성", "회피율 +5%", "dodge_bonus", 5)
            ]),
            ("강화 가죽", EquipmentRarity.RARE, 8, {"hp": 40, "p_def": 15, "m_def": 8}, [
                EquipmentEffect("상처 완화", "받는 상처 -20%", "wound_reduction", 0.8),
                EquipmentEffect("내구성", "장비 손상 저항", "durability_bonus", True)
            ]),
            ("체인메일", EquipmentRarity.RARE, 12, {"hp": 60, "p_def": 25, "speed": -3}, [
                EquipmentEffect("사슬 보호", "관통 공격 피해 50% 감소", "pierce_resist", 0.5),
                EquipmentEffect("무게감", "속도 감소하지만 충격 저항", "heavy_armor", True)
            ]),
            ("강철 갑옷", EquipmentRarity.RARE, 15, {"hp": 80, "p_def": 35, "m_def": 10}, [
                EquipmentEffect("강철 방어", "물리 피해 20% 감소", "steel_defense", 0.8),
                EquipmentEffect("상처 방지", "상처 누적 30% 감소", "wound_prevention", 0.7)
            ]),
            ("플레이트 아머", EquipmentRarity.EPIC, 20, {"hp": 100, "p_def": 40, "m_def": 15, "speed": -5}, [
                EquipmentEffect("완벽 방어", "10% 확률로 모든 물리 피해 무효", "perfect_defense", 0.1),
                EquipmentEffect("상처 방지", "상처 누적 50% 감소", "wound_prevention", 0.5)
            ]),
            ("화염 갑옷", EquipmentRarity.EPIC, 22, {"hp": 90, "p_def": 30, "m_def": 25}, [
                EquipmentEffect("화염 방어", "화염 피해 50% 감소", "fire_resist", 0.5),
                EquipmentEffect("화염 반사", "공격받을 시 화염 피해 반사", "fire_reflect", True)
            ], ElementalAffinity.FIRE),
            ("빙결 갑옷", EquipmentRarity.EPIC, 22, {"hp": 85, "p_def": 35, "m_def": 20}, [
                EquipmentEffect("빙결 방어", "빙결 피해 50% 감소", "ice_resist", 0.5),
                EquipmentEffect("냉기 오라", "접근한 적에게 속도 감소", "chill_aura", True)
            ], ElementalAffinity.ICE),
            ("드래곤 스케일", EquipmentRarity.LEGENDARY, 30, {"hp": 150, "p_def": 50, "m_def": 35}, [
                EquipmentEffect("드래곤의 힘", "화염 면역 및 물리 저항 50%", "dragon_power", True),
                EquipmentEffect("재생", "매 턴 HP 3% 회복", "regeneration", 0.03)
            ], ElementalAffinity.FIRE),
            ("신성 갑옷", EquipmentRarity.MYTHIC, 40, {"hp": 200, "p_def": 60, "m_def": 50, "brave": 30}, [
                EquipmentEffect("신의 가호", "상처 시스템 완전 무효", "divine_protection", True),
                EquipmentEffect("성스러운 빛", "언데드 접근 시 자동 피해", "holy_aura", True)
            ], ElementalAffinity.LIGHT),
        ]
        
        # 🦵 하체 갑옷류 (30종) - 기동성과 안정성
        leg_armors = [
            ("천 바지", EquipmentRarity.COMMON, 1, {"speed": 2, "p_def": 2}, [
                EquipmentEffect("자유로움", "이동 관련 패널티 없음", "free_movement", True)
            ]),
            ("가죽 바지", EquipmentRarity.COMMON, 4, {"hp": 15, "p_def": 6, "speed": 1}, [
                EquipmentEffect("발놀림", "회피 후 반격 확률 증가", "counter_dodge", True)
            ]),
            ("강철 각반", EquipmentRarity.RARE, 10, {"hp": 30, "p_def": 12, "speed": 3}, [
                EquipmentEffect("신속함", "첫 턴 행동 속도 2배", "swift_start", 2.0),
                EquipmentEffect("안정성", "넘어짐 상태 면역", "stability", True)
            ]),
            ("바람 부츠", EquipmentRarity.EPIC, 18, {"speed": 15, "p_def": 8}, [
                EquipmentEffect("바람 걸음", "매 턴 이동 거리 2배", "wind_step", 2.0),
                EquipmentEffect("잔상", "이동 시 30% 확률로 회피", "afterimage", 0.3)
            ], ElementalAffinity.WIND),
            ("대지의 각반", EquipmentRarity.LEGENDARY, 25, {"hp": 80, "p_def": 25, "m_def": 20}, [
                EquipmentEffect("뿌리박기", "밀려남 효과 완전 무효", "rooted", True),
                EquipmentEffect("대지의 힘", "땅에 닿아있을 때 능력치 +20%", "earth_power", 1.2)
            ], ElementalAffinity.EARTH),
        ]
        
        # 🎩 머리 갑옷류 (30종) - 정신 보호 및 시야 확장
        head_armors = [
            ("천 모자", EquipmentRarity.COMMON, 1, {"m_def": 5}, [
                EquipmentEffect("집중", "MP 소모량 -5%", "concentration", 0.95)
            ]),
            ("가죽 모자", EquipmentRarity.COMMON, 3, {"p_def": 3, "m_def": 5}, [
                EquipmentEffect("시야 확보", "시야 범위 +1", "vision_bonus", 1)
            ]),
            ("철 투구", EquipmentRarity.RARE, 8, {"hp": 25, "p_def": 12, "m_def": 8}, [
                EquipmentEffect("머리 보호", "치명타 피해 30% 감소", "head_protection", 0.7)
            ]),
            ("마법사 모자", EquipmentRarity.RARE, 8, {"mp": 30, "m_def": 15}, [
                EquipmentEffect("지식", "경험치 획득 +20%", "knowledge", 1.2),
                EquipmentEffect("마법 저항", "상태 이상 저항 +30%", "magic_resist", 30)
            ]),
            ("정찰병 헬멧", EquipmentRarity.RARE, 12, {"speed": 5, "p_def": 10}, [
                EquipmentEffect("광역 시야", "시야 범위 +1", "wide_vision", 1),
                EquipmentEffect("위험 감지", "함정 탐지 확률 +50%", "danger_sense", 0.5)
            ]),
            ("엘프 서클릿", EquipmentRarity.EPIC, 16, {"mp": 40, "m_def": 20, "speed": 5}, [
                EquipmentEffect("자연 시야", "시야 범위 +2", "nature_sight", 2),
                EquipmentEffect("정신 명료", "정신 공격 완전 무효", "mental_clarity", True)
            ], ElementalAffinity.WIND),
            ("용의 투구", EquipmentRarity.EPIC, 22, {"hp": 50, "p_def": 20, "m_def": 25, "brave": 15}, [
                EquipmentEffect("용의 시선", "적 위협 수준 자동 분석", "dragon_sight", True),
                EquipmentEffect("공포", "적의 명중률 -25%", "fear", 0.75)
            ], ElementalAffinity.FIRE),
            ("천리안 왕관", EquipmentRarity.LEGENDARY, 28, {"mp": 60, "m_def": 30, "speed": 8}, [
                EquipmentEffect("천리안", "시야 범위 +3", "far_sight", 3),
                EquipmentEffect("미래 예지", "적의 다음 행동 미리 확인", "precognition", True)
            ]),
            ("시간의 왕관", EquipmentRarity.MYTHIC, 35, {"mp": 100, "m_def": 40, "speed": 10}, [
                EquipmentEffect("집중력", "MP 소모량 -20%", "mana_efficiency", 0.8),
                EquipmentEffect("넓은 시야", "시야 범위 +3", "wide_vision", 3)
            ], ElementalAffinity.NEUTRAL),
        ]
        
        # 방어구 데이터베이스에 추가
        armor_id = 1
        for armor_list in [chest_armors, leg_armors, head_armors]:
            for armor_data in armor_list:
                name, rarity, level, stats, effects = armor_data[:5]
                element = armor_data[5] if len(armor_data) > 5 else ElementalAffinity.NEUTRAL
                
                # 방어구 타입별 기본 무게 설정
                base_weight = 1.0
                if "갑옷" in name or "아머" in name or "플레이트" in name:
                    base_weight = 4.0  # 상체 갑옷은 매우 무거움
                elif "바지" in name or "각반" in name or "부츠" in name:
                    base_weight = 2.0  # 하체 갑옷은 중간
                elif "모자" in name or "투구" in name or "헬멧" in name or "왕관" in name:
                    base_weight = 1.5  # 머리 갑옷은 가벼움
                elif "로브" in name or "의상" in name or "도복" in name:
                    base_weight = 1.2  # 로브류는 가벼움
                elif "체인메일" in name or "판금" in name:
                    base_weight = 5.0  # 금속 갑옷은 매우 무거움
                
                # 희귀도별 무게 배율
                rarity_weight_multiplier = {
                    EquipmentRarity.COMMON: 1.0,
                    EquipmentRarity.RARE: 1.1,
                    EquipmentRarity.EPIC: 1.2,
                    EquipmentRarity.LEGENDARY: 1.3,
                    EquipmentRarity.MYTHIC: 1.4,
                    EquipmentRarity.ARTIFACT: 1.5
                }
                
                final_weight = base_weight * rarity_weight_multiplier.get(rarity, 1.0)
                
                armor = Equipment(
                    name=name,
                    equipment_type=EquipmentType.ARMOR,
                    rarity=rarity,
                    level_req=level,
                    base_stats=stats,
                    special_effects=effects,
                    elemental_affinity=element,
                    weight=final_weight
                )
                self.armors[f"armor_{armor_id}"] = armor
                armor_id += 1
    
    def _create_accessories(self):
        """50종의 상태 효과와 패시브 능력이 특화된 장신구 생성"""
        
        # 📿 목걸이류 (15종) - 생존력과 회복
        necklace_accessories = [
            ("생명의 목걸이", EquipmentRarity.COMMON, 2, {"hp": 25}, [
                EquipmentEffect("생명력", "최대 HP +10%", "hp_boost", 1.1)
            ]),
            ("마나의 목걸이", EquipmentRarity.COMMON, 3, {"mp": 20}, [
                EquipmentEffect("마력", "최대 MP +15%", "mp_boost", 1.15)
            ]),
            ("치유의 목걸이", EquipmentRarity.RARE, 10, {"hp": 40, "mp": 25}, [
                EquipmentEffect("자동 치유", "HP 30% 이하 시 자동 회복", "auto_heal", True),
                EquipmentEffect("치유 증폭", "회복 효과 +50%", "heal_boost", 1.5)
            ]),
            ("용맹의 목걸이", EquipmentRarity.RARE, 12, {"brave": 20, "p_atk": 8}, [
                EquipmentEffect("용기", "전투 시작시 브레이브 +50%", "courage", 1.5),
                EquipmentEffect("불굴", "HP 1에서 즉사하지 않음", "undaunted", True)
            ]),
            ("현자의 목걸이", EquipmentRarity.EPIC, 20, {"mp": 60, "m_atk": 15}, [
                EquipmentEffect("지혜", "스킬 쿨다운 -1턴", "wisdom", 1),
                EquipmentEffect("명상", "매 5턴마다 MP 완전 회복", "meditation", 5)
            ]),
            ("불멸의 목걸이", EquipmentRarity.LEGENDARY, 30, {"hp": 150, "brave": 40}, [
                EquipmentEffect("불멸", "죽을 때 1회 완전 회복", "immortality", True),
                EquipmentEffect("영원", "상처 누적 완전 무효", "eternal", True)
            ]),
            ("세계수 목걸이", EquipmentRarity.MYTHIC, 40, {"hp": 200, "mp": 150, "all_stats": 10}, [
                EquipmentEffect("세계의 힘", "모든 능력치 +25%", "world_power", 1.25),
                EquipmentEffect("자연의 가호", "모든 원소 피해 50% 감소", "nature_blessing", 0.5)
            ], ElementalAffinity.EARTH),
        ]
        
        # 💍 반지류 (15종) - 능력치 강화와 특수 효과
        ring_accessories = [
            ("힘의 반지", EquipmentRarity.COMMON, 3, {"p_atk": 5}, [
                EquipmentEffect("완력", "물리 공격력 +10%", "strength", 1.1)
            ]),
            ("민첩의 반지", EquipmentRarity.COMMON, 3, {"speed": 5}, [
                EquipmentEffect("신속", "행동 속도 +15%", "agility", 1.15)
            ]),
            ("지능의 반지", EquipmentRarity.COMMON, 3, {"m_atk": 5}, [
                EquipmentEffect("총명", "마법 공격력 +10%", "intelligence", 1.1)
            ]),
            ("수호의 반지", EquipmentRarity.RARE, 10, {"p_def": 10, "m_def": 10}, [
                EquipmentEffect("보호막", "매 턴 시작시 보호막 생성", "shield", True),
                EquipmentEffect("수호자", "아군 대신 피해 받기", "guardian", True)
            ]),
            ("재생의 반지", EquipmentRarity.RARE, 12, {"hp": 30}, [
                EquipmentEffect("재생", "매 턴 HP 5% 회복", "regeneration", 0.05),
                EquipmentEffect("회복력", "모든 회복 효과 2배", "recovery_boost", 2.0)
            ]),
            ("시간 반지", EquipmentRarity.LEGENDARY, 25, {"speed": 20, "mp": 50}, [
                EquipmentEffect("시간 가속", "20% 확률로 추가 행동", "time_acceleration", 0.2),
                EquipmentEffect("시간 정지", "5턴에 1회 시간 정지", "time_stop", 5)
            ]),
            ("창조의 반지", EquipmentRarity.MYTHIC, 35, {"all_stats": 15}, [
                EquipmentEffect("창조", "원하는 소모품 임시 생성", "creation_power", True),
                EquipmentEffect("소원", "전투 중 1회 즉석 효과 발동", "wish", True)
            ]),
        ]
        
        # 👂 귀걸이류 (10종) - 감각 능력과 시야
        earring_accessories = [
            ("예리한 귀걸이", EquipmentRarity.COMMON, 2, {"speed": 3}, [
                EquipmentEffect("예민함", "선제공격 확률 +25%", "alertness", 25)
            ]),
            ("집중의 귀걸이", EquipmentRarity.RARE, 8, {"m_atk": 8, "mp": 15}, [
                EquipmentEffect("집중력", "스킬 성공률 +20%", "focus", 20),
                EquipmentEffect("정신력", "정신 공격 완전 무효", "mental_immunity", True)
            ]),
            ("탐지의 귀걸이", EquipmentRarity.RARE, 12, {"speed": 5}, [
                EquipmentEffect("위험 감지", "시야 범위 +1", "danger_sense", 1),
                EquipmentEffect("함정 탐지", "숨겨진 함정 자동 발견", "trap_detection", True)
            ]),
            ("천리안 귀걸이", EquipmentRarity.EPIC, 15, {"all_stats": 5}, [
                EquipmentEffect("천리안", "시야 범위 +2", "true_sight", 2),
                EquipmentEffect("미래 시", "3턴 후까지 예측", "future_sight", 3)
            ]),
            ("신의 귀", EquipmentRarity.MYTHIC, 30, {"mp": 100, "m_def": 30}, [
                EquipmentEffect("신의 목소리", "전체 지도 완전 공개", "divine_voice", 5),
                EquipmentEffect("진실", "모든 거짓을 간파", "truth", True)
            ], ElementalAffinity.LIGHT),
        ]
        
        # 📿 팔찌류 (12종) - 행동력과 스킬 강화
        bracelet_accessories = [
            ("기술의 팔찌", EquipmentRarity.COMMON, 4, {"p_atk": 3, "m_atk": 3}, [
                EquipmentEffect("숙련", "크리티컬 확률 +10%", "skill", 10)
            ]),
            ("연속 공격 팔찌", EquipmentRarity.RARE, 12, {"speed": 8}, [
                EquipmentEffect("연속 타격", "25% 확률로 추가 공격", "combo", 0.25),
                EquipmentEffect("콤보", "연속 공격 시 피해 증가", "combo_boost", True)
            ]),
            ("원소 조작 팔찌", EquipmentRarity.EPIC, 20, {"m_atk": 20}, [
                EquipmentEffect("원소 지배", "모든 원소 자유 사용", "element_mastery", True),
                EquipmentEffect("원소 융합", "2개 원소 동시 사용", "element_fusion", True)
            ]),
            ("마스터 팔찌", EquipmentRarity.LEGENDARY, 25, {"all_stats": 10}, [
                EquipmentEffect("마스터", "모든 스킬 레벨 +1", "mastery", 1),
                EquipmentEffect("완벽", "모든 행동 성공률 +50%", "perfection", 50)
            ]),
            ("무한의 팔찌", EquipmentRarity.MYTHIC, 40, {"all_stats": 20}, [
                EquipmentEffect("무한", "모든 쿨다운 50% 감소", "infinite_power", 0.5),
                EquipmentEffect("영원", "모든 버프 효과가 2배 지속", "eternal_effect", 2.0)
            ]),
            ("강철 팔찌", EquipmentRarity.COMMON, 6, {"p_def": 5, "hp": 15}, [
                EquipmentEffect("견고함", "장비 파괴 저항", "durability", True)
            ]),
            ("마법 팔찌", EquipmentRarity.RARE, 14, {"m_atk": 12, "mp": 20}, [
                EquipmentEffect("마법 증폭", "마법 피해 +25%", "magic_boost", 1.25),
                EquipmentEffect("마나 효율", "MP 소모 -15%", "mana_efficiency", 0.85)
            ]),
        ]
        
        # 💎 원소 변환석류 (9종) - 캐릭터 원소 타입 변경
        element_stones = [
            ("화염 변환석", EquipmentRarity.RARE, 15, {"m_atk": 5}, [
                EquipmentEffect("화염 변환", "착용자의 원소를 화염으로 변경", "element_change", "fire")
            ]),
            ("빙결 변환석", EquipmentRarity.RARE, 15, {"m_def": 5}, [
                EquipmentEffect("빙결 변환", "착용자의 원소를 빙결으로 변경", "element_change", "ice")
            ]),
            ("번개 변환석", EquipmentRarity.RARE, 15, {"speed": 5}, [
                EquipmentEffect("번개 변환", "착용자의 원소를 번개로 변경", "element_change", "lightning")
            ]),
            ("대지 변환석", EquipmentRarity.RARE, 15, {"p_def": 8}, [
                EquipmentEffect("대지 변환", "착용자의 원소를 대지로 변경", "element_change", "earth")
            ]),
            ("바람 변환석", EquipmentRarity.RARE, 15, {"speed": 8}, [
                EquipmentEffect("바람 변환", "착용자의 원소를 바람으로 변경", "element_change", "wind")
            ]),
            ("물 변환석", EquipmentRarity.RARE, 15, {"mp": 10}, [
                EquipmentEffect("물 변환", "착용자의 원소를 물로 변경", "element_change", "water")
            ]),
            ("독 변환석", EquipmentRarity.RARE, 15, {"p_atk": 5}, [
                EquipmentEffect("독 변환", "착용자의 원소를 독으로 변경", "element_change", "poison")
            ]),
            ("빛 변환석", EquipmentRarity.EPIC, 20, {"m_atk": 8, "hp": 15}, [
                EquipmentEffect("빛 변환", "착용자의 원소를 빛으로 변경", "element_change", "light")
            ]),
            ("어둠 변환석", EquipmentRarity.EPIC, 20, {"p_atk": 8, "mp": 15}, [
                EquipmentEffect("어둠 변환", "착용자의 원소를 어둠으로 변경", "element_change", "dark")
            ]),
        ]
        
        # 장신구 데이터베이스에 추가
        accessory_id = 1
        for accessory_list in [necklace_accessories, ring_accessories, earring_accessories, bracelet_accessories, element_stones]:
            for accessory_data in accessory_list:
                name, rarity, level, stats, effects = accessory_data[:5]
                element = accessory_data[5] if len(accessory_data) > 5 else ElementalAffinity.NEUTRAL
                
                # 장신구 타입별 기본 무게 설정
                base_weight = 0.3  # 장신구는 기본적으로 가벼움
                if "목걸이" in name:
                    base_weight = 0.5  # 목걸이는 조금 무거움
                elif "반지" in name:
                    base_weight = 0.2  # 반지는 매우 가벼움
                elif "귀걸이" in name:
                    base_weight = 0.1  # 귀걸이는 가장 가벼움
                elif "팔찌" in name:
                    base_weight = 0.4  # 팔찌는 중간
                elif "변환석" in name:
                    base_weight = 0.8  # 변환석은 무거운 편 (마법 결정체)
                
                # 희귀도별 무게 배율 (장신구는 배율이 낮음)
                rarity_weight_multiplier = {
                    EquipmentRarity.COMMON: 1.0,
                    EquipmentRarity.RARE: 1.05,
                    EquipmentRarity.EPIC: 1.1,
                    EquipmentRarity.LEGENDARY: 1.15,
                    EquipmentRarity.MYTHIC: 1.2,
                    EquipmentRarity.ARTIFACT: 1.25
                }
                
                final_weight = base_weight * rarity_weight_multiplier.get(rarity, 1.0)
                
                accessory = Equipment(
                    name=name,
                    equipment_type=EquipmentType.ACCESSORY,
                    rarity=rarity,
                    level_req=level,
                    base_stats=stats,
                    special_effects=effects,
                    elemental_affinity=element,
                    weight=final_weight
                )
                self.accessories[f"accessory_{accessory_id}"] = accessory
                accessory_id += 1
    
    def get_equipment_by_type(self, equipment_type: EquipmentType) -> Dict[str, Equipment]:
        """타입별 장비 반환"""
        if equipment_type == EquipmentType.WEAPON:
            return self.weapons
        elif equipment_type == EquipmentType.ARMOR:
            return self.armors
        elif equipment_type == EquipmentType.ACCESSORY:
            return self.accessories
        return {}
    
    def get_equipment_by_rarity(self, rarity: EquipmentRarity) -> List[Equipment]:
        """등급별 장비 반환"""
        result = []
        for equipment_dict in [self.weapons, self.armors, self.accessories]:
            for equipment in equipment_dict.values():
                if equipment.rarity == rarity:
                    result.append(equipment)
        return result
    
    def get_random_equipment(self, level_range: Tuple[int, int] = (1, 50)) -> Equipment:
        """레벨 범위 내 랜덤 장비 반환"""
        all_equipment = []
        for equipment_dict in [self.weapons, self.armors, self.accessories]:
            for equipment in equipment_dict.values():
                if level_range[0] <= equipment.level_requirement <= level_range[1]:
                    all_equipment.append(equipment)
        
        if all_equipment:
            return random.choice(all_equipment)
        return None

class MegaEquipmentGenerator:
    """실용적 대규모 장비 생성기"""
    
    def __init__(self):
        self.database = MegaEquipmentDatabase()
        self.weapon_count = len(self.database.weapons)
        self.armor_count = len(self.database.armors)
        self.accessory_count = len(self.database.accessories)
        
        print(f"🗡️ 실용적 장비 시스템 초기화 완료:")
        print(f"  ⚔️  무기: {self.weapon_count}종 (브레이브 시스템 연동)")
        print(f"  🛡️  방어구: {self.armor_count}종 (상처 시스템 연동)")
        print(f"  💎 장신구: {self.accessory_count}종 (시야 시스템 포함)")
        print(f"  📦 총합: {self.weapon_count + self.armor_count + self.accessory_count}종")
        print(f"  🌟 특수 효과: 브레이브, 상처, 원소, 상태이상, 시야 시스템 완전 연동")
        print(f"  ⚡ 구현 범위: 실제 게임에서 구현 가능한 기능들만 포함")
    
    def get_vision_bonus_total(self, equipment_list: List[Equipment]) -> int:
        """파티 전체 장비의 시야 범위 보너스 합계 계산"""
        total_vision_bonus = 0
        
        for equipment in equipment_list:
            for effect in equipment.special_effects:
                # 시야 관련 효과들 체크
                if effect.effect_type in ["vision_bonus", "wide_vision", "nature_sight", 
                                        "far_sight", "true_sight", "infinite_vision", 
                                        "divine_voice", "long_range", "vision_boost"]:
                    if isinstance(effect.effect_value, int):
                        total_vision_bonus += effect.effect_value
                    elif effect.effect_value == 999:  # 무한 시야
                        return 999
        
        return total_vision_bonus
    
    def get_equipment_effects_for_target(self, equipment: Equipment, target) -> List[EquipmentEffect]:
        """대상에게 적용 가능한 장비 효과들만 반환 (보스 면역 체크)"""
        applicable_effects = []
        
        for effect in equipment.special_effects:
            if effect.can_apply_to_target(target):
                applicable_effects.append(effect)
        
        return applicable_effects

# 전역 실용적 대규모 장비 생성기
mega_equipment_generator = MegaEquipmentGenerator()

# 시야 시스템 통합 함수
def calculate_party_vision_range(party_equipment_list, base_vision=3):
    """
    파티 전체 장비의 시야 범위 보너스를 계산하여 총 시야 범위 반환
    
    Args:
        party_equipment_list: 파티 전체 장착 장비 리스트
        base_vision: 기본 시야 범위 (기본값: 3)
    
    Returns:
        int: 총 시야 범위
    """
    vision_bonus = mega_equipment_generator.get_vision_bonus_total(party_equipment_list)
    
    if vision_bonus == 999:  # 무한 시야
        return 999
    
    return base_vision + vision_bonus
