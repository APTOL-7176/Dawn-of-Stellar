#!/usr/bin/env python3
"""
새로운 스킬 시스템 - 28종 직업별 스킬 (MP 효율성 개선)
"""

from typing import Dict, List, Any
from enum import Enum

class SkillType(Enum):
    BRV_ATTACK = "BRV공격"
    HP_ATTACK = "HP공격"
    BRV_HP_ATTACK = "BRV+HP공격"
    HEAL = "치유"
    BUFF = "버프"
    DEBUFF = "디버프"
    FIELD = "필드"
    SPECIAL = "특수"
    ULTIMATE = "궁극기"
    COUNTER = "반격"

class TargetType(Enum):
    SELF = "자신"
    SINGLE_ALLY = "아군1명"
    ALL_ALLIES = "아군전체"
    SINGLE_ENEMY = "적1명"
    ALL_ENEMIES = "적전체"
    DEAD_ALLY = "죽은아군1명"

class ElementType(Enum):
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

class BarrierType(Enum):
    """보호막 종류"""
    PHYSICAL = "물리보호막"
    MAGICAL = "마법보호막"
    ELEMENTAL = "원소보호막"
    HOLY = "신성보호막"
    SHADOW = "어둠보호막"
    ABSORB = "흡수보호막"
    REFLECT = "반사보호막"

class DamageType(Enum):
    PHYSICAL = "물리"
    MAGICAL = "마법"
    HYBRID = "복합"  # 물리+마법

class DefenseType(Enum):
    PHYSICAL_DEF = "물리방어"
    MAGICAL_DEF = "마법방어"
    BOTH_DEF = "복합방어"

class PenetrationType(Enum):
    """방어력 관통 타입"""
    NONE = "관통없음"
    PHYSICAL_PIERCE = "물리관통"    # 물리방어 일부 무시
    MAGICAL_PIERCE = "마법관통"     # 마법방어 일부 무시
    TRUE_DAMAGE = "고정피해"        # penetration_rate 비율만큼 방어력 1로 고정 계산
    ARMOR_BREAK = "방어파괴"        # 방어력 감소 후 공격
    
    # TRUE_DAMAGE 설명:
    # 기존: (ATK / DEF) * modifiers
    # TRUE_DAMAGE: (ATK / 1) * penetration_rate + (ATK / DEF) * (1 - penetration_rate)
    # 예: 20% TRUE_DAMAGE = 20%는 방어무시, 80%는 일반계산

class StatusType(Enum):
    # === 버프 상태 ===
    BOOST_ATK = "공격력증가"
    BOOST_DEF = "방어력증가"
    BOOST_SPD = "속도증가"
    BOOST_ACCURACY = "명중률증가"
    BOOST_CRIT = "치명타증가"
    BOOST_DODGE = "회피율증가"
    BLESSING = "축복"
    REGENERATION = "재생"
    INVINCIBLE = "무적"
    REFLECT = "반사"
    HASTE = "가속"
    FOCUS = "집중"
    RAGE = "분노"
    INSPIRATION = "영감"
    GUARDIAN = "수호"
    
    # === 보호막 시스템 ===
    BARRIER = "보호막"
    MAGIC_BARRIER = "마법보호막"
    FIRE_SHIELD = "화염방패"
    ICE_SHIELD = "빙결방패"
    HOLY_SHIELD = "성스러운방패"
    SHADOW_SHIELD = "그림자방패"
    
    # === 디버프 상태 ===
    REDUCE_ATK = "공격력감소"
    REDUCE_DEF = "방어력감소"
    REDUCE_SPD = "속도감소"
    REDUCE_ACCURACY = "명중률감소"
    VULNERABLE = "취약"
    EXPOSED = "노출"
    WEAKNESS = "허약"
    CONFUSION = "혼란"
    TERROR = "공포"
    DESPAIR = "절망"
    
    # === 상태이상 ===
    POISON = "독"
    BURN = "화상"
    FREEZE = "빙결"
    CHILL = "냉기"
    SHOCK = "감전"
    BLEED = "출혈"
    CORRODE = "부식"
    DISEASE = "질병"
    NECROSIS = "괴사"
    MADNESS = "광기"
    PETRIFY = "석화"
    
    # === 행동 제약 ===
    STUN = "기절"
    SLEEP = "수면"
    SILENCE = "침묵"
    BLIND = "실명"
    PARALYZE = "마비"
    CHARM = "매혹"
    DOMINATE = "지배"
    ROOT = "속박"
    SLOW = "둔화"
    
    # === 특수 상태 ===
    CURSE = "저주"
    FEAR = "공포"
    STEALTH = "은신"
    BERSERK = "광폭화"
    TAUNT = "도발"
    COUNTER = "반격태세"
    VAMPIRE = "흡혈"
    SPIRIT_LINK = "정신연결"
    TIME_STOP = "시간정지"
    PHASE = "위상변화"
    
    # === 추가 상태이상 ===
    MP_REGEN = "MP재생"
    MP_DRAIN = "MP소모"
    STRENGTHEN = "강화"
    WEAKEN = "약화"
    SHIELD = "보호막"

def get_status_icon(status_type: StatusType) -> str:
    """상태이상 아이콘 반환"""
    icons = {
        # 버프
        StatusType.BOOST_ATK: "⚔️",
        StatusType.BOOST_DEF: "🛡️", 
        StatusType.BOOST_SPD: "💨",
        StatusType.BOOST_ACCURACY: "🎯",
        StatusType.BOOST_CRIT: "💥",
        StatusType.BOOST_DODGE: "💃",
        StatusType.BLESSING: "✨",
        StatusType.REGENERATION: "💚",
        StatusType.INVINCIBLE: "🌟",
        StatusType.REFLECT: "🪞",
        StatusType.HASTE: "🏃",
        StatusType.FOCUS: "🎯",
        StatusType.RAGE: "😡",
        StatusType.INSPIRATION: "💡",
        StatusType.GUARDIAN: "🛡️✨",
        
        # 보호막
        StatusType.BARRIER: "🔵",
        StatusType.MAGIC_BARRIER: "🔮",
        StatusType.FIRE_SHIELD: "🔥🛡️",
        StatusType.ICE_SHIELD: "🧊🛡️",
        StatusType.HOLY_SHIELD: "✨🛡️",
        StatusType.SHADOW_SHIELD: "🌑🛡️",
        
        # 디버프
        StatusType.REDUCE_ATK: "⚔️💔",
        StatusType.REDUCE_DEF: "🛡️💔",
        StatusType.REDUCE_SPD: "🐌",
        StatusType.REDUCE_ACCURACY: "🎯💔",
        StatusType.VULNERABLE: "💀",
        StatusType.EXPOSED: "👁️",
        StatusType.WEAKNESS: "😵",
        StatusType.CONFUSION: "💫",
        StatusType.TERROR: "😱",
        StatusType.DESPAIR: "😞",
        
        # 상태이상
        StatusType.POISON: "☠️",
        StatusType.BURN: "🔥",
        StatusType.FREEZE: "🧊", 
        StatusType.SHOCK: "⚡",
        StatusType.BLEED: "🩸",
        StatusType.CORRODE: "🟢",
        StatusType.DISEASE: "🤢",
        StatusType.NECROSIS: "💀",
        StatusType.MADNESS: "🤪",
        StatusType.PETRIFY: "🗿",
        
        # 행동 제약
        StatusType.STUN: "💫",
        StatusType.SLEEP: "😴",
        StatusType.SILENCE: "🤐",
        StatusType.BLIND: "🙈",
        StatusType.PARALYZE: "⚡💥",
        StatusType.CHARM: "💖",
        StatusType.DOMINATE: "🧠",
        StatusType.ROOT: "🌿",
        StatusType.SLOW: "🐌",
        
        # 특수
        StatusType.CURSE: "💀",
        StatusType.FEAR: "😨",
        StatusType.STEALTH: "👤",
        StatusType.BERSERK: "🔴",
        StatusType.TAUNT: "😤",
        StatusType.COUNTER: "↩️",
        StatusType.VAMPIRE: "🧛",
        StatusType.SPIRIT_LINK: "🔗",
        StatusType.TIME_STOP: "⏰",
        StatusType.PHASE: "👻",
    }
    return icons.get(status_type, "❓")

class NewSkillSystem:
    """새로운 스킬 시스템 - 28종 직업별 최적화"""
    
    def __init__(self):
        self.skills_by_class = self._initialize_all_skills()
        self.cooldowns = {}  # {character_id: {skill_name: remaining_turns}}
        # 스킬 계수 전역 배수 (1.5배로 모든 스킬 데미지 증가)
        self.skill_power_multiplier = 1.5
        # 적 스킬 전용 계수 (1.1배로 적 스킬 강화)
        self.enemy_skill_power_multiplier = 1.1
        # 아군 스킬 MP 소모량 배수 (1.6배로 증가)
        self.ally_mp_cost_multiplier = 1.6
    
    def _initialize_all_skills(self) -> Dict[str, List[Dict[str, Any]]]:
        """28종 직업별 스킬 초기화 - 각 직업의 개성과 유기성 강화"""
        return {
            # === 물리 전사 계열 ===
            "전사": [
                {"name": "분노 축적", "type": SkillType.BUFF, "target": TargetType.SELF, 
                 "mp_cost": 2, "cooldown": 0, "description": "분노를 쌓아 다음 물리공격력 증가",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 2, "intensity": 1.3}]},
                {"name": "방패 들기", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 1, "cooldown": 1, "description": "방어 태세로 전환, 물리방어력 증가",
                 "defense_type": DefenseType.PHYSICAL_DEF,
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 3, "intensity": 1.5}]},
                {"name": "강타", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "hp_power": 110, "cast_time": 10, "accuracy": 85, "description": "물리공격력 기반 강력한 HP 타격",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "전사의 외침", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "cooldown": 3, "description": "아군 전체 물리공격력 증가",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2}]},
                {"name": "돌진 베기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "hp_power": 140, "cast_time": 15, "description": "물리공격력 기반 HP 직접 타격",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "광전사의 각성", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 12, "cooldown": 6, "cast_time": 25, "description": "물리공격력과 물리방어력 대폭 증가",
                 "damage_type": DamageType.PHYSICAL, "defense_type": DefenseType.PHYSICAL_DEF,
                 "status_effects": [{"type": StatusType.BERSERK, "duration": 5, "intensity": 2.0}]}
            ],
            
            "검성": [
                {"name": "검심 집중", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "검에 집중하여 물리공격력과 크리티컬 확률 증가",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 3, "intensity": 1.2}]},
                {"name": "일섬", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "hp_power": 120, "cast_time": 12, "accuracy": 95, "description": "물리공격력 기반 빠르고 정확한 HP 베기",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "검기 방출", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "brv_power": 75, "description": "물리공격력 기반 검기로 모든 적 공격",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "반격 태세", "type": SkillType.COUNTER, "target": TargetType.SELF,
                 "mp_cost": 4, "cooldown": 2, "description": "물리공격 받을 시 물리공격력으로 반격",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.COUNTER, "duration": 3, "intensity": 1.5}]},
                {"name": "연속 베기", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "brv_power": 30, "hp_power": 23, "consecutive_attacks": 3, "cast_time": 20,
                 "description": "물리공격력으로 3연속 베기 (각각 독립적인 데미지, 개별 타격 30%)",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "무념무상", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 15, "cooldown": 8, "cast_time": 40, "description": "모든 디버프 무효, 완벽한 검술",
                 "special_effects": ["immunity", "perfect_accuracy"]}
            ],
            
            "검투사": [
                {"name": "투기장의 기술", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 2, "brv_power": 105, "description": "기본 검투 기술"},
                {"name": "군중의 함성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "관중의 응원으로 능력치 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.3}]},
                {"name": "네트 던지기", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "description": "적의 움직임 봉쇄",
                 "status_effects": [{"type": StatusType.STUN, "duration": 2, "intensity": 1.0}]},
                {"name": "트라이던트 찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "hp_power": 135, "description": "삼지창으로 강력한 공격"},
                {"name": "결투자의 명예", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 6, "description": "HP 낮을수록 공격력 증가",
                 "special_effects": ["honor_boost"]},
                {"name": "콜로세움의 왕", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "brv_power": 100, "hp_power": 80, "cooldown": 7, "cast_time": 30,
                 "description": "검투장을 지배하는 궁극기", "damage_type": DamageType.PHYSICAL,
                 "penetration_type": PenetrationType.PHYSICAL_PIERCE, "penetration_rate": 0.35}
            ],
            
            "광전사": [
                {"name": "광기의 씨앗", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 1, "description": "자신에게 피해를 입혀 광폭화 준비",
                 "special_effects": ["self_damage", "rage_build"]},
                {"name": "무모한 돌격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "hp_power": 125, "cast_time": 20, "accuracy": 75, "description": "정확도 낮지만 강력한 HP 공격"},
                {"name": "피의 갈증", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "hp_power": 120, "drain_hp": True, "drain_rate": 0.4, "cast_time": 15,
                 "description": "적을 공격하여 체력을 흡수"},
                {"name": "광란의 연타", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 18, "consecutive_attacks": 4, "cast_time": 25,
                 "description": "광폭한 4연속 공격 (각각 독립적인 데미지, 개별 타격 18%)"},
                {"name": "분노 폭발", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "brv_power": 85, "hp_power": 65, "area_attack": True, "cast_time": 30,
                 "description": "모든 적에게 광기의 힘을 방출"},
                {"name": "버서커의 최후", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 15, "brv_power": 120, "hp_power": 100, "cooldown": 5, "cast_time": 10,
                 "description": "[궁극기] 현재 HP의 30%를 소모하여 모든 적에게 치명적인 광역 공격, 희생한 HP만큼 데미지 보너스 (물리 관통 50%)", "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["sacrifice_power"], "penetration_type": PenetrationType.PHYSICAL_PIERCE,
                 "penetration_rate": 0.5, "hp_sacrifice_rate": 0.30}
            ],
            
            # === 기사 계열 ===
            "기사": [
                {"name": "방패 방어", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "방어력 증가 및 아군 보호 준비",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.4}]},
                {"name": "창 돌격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 115, "description": "기사의 기본 창술"},
                {"name": "아군 보호", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 4, "description": "아군에게 보호막 부여",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 5, "intensity": 1.0}]},
                {"name": "기사도 정신", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "cooldown": 3, "description": "아군 전체 방어력 증가",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.3}]},
                {"name": "성스러운 돌격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 130, "element": ElementType.LIGHT, "cast_time": 12,
                 "description": "성스러운 힘의 돌격"},
                {"name": "수호기사의 맹세", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 16, "cooldown": 6, "cast_time": 35, "description": "아군 전체를 완벽하게 보호",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 6, "intensity": 2.0}]}
            ],
            
            "성기사": [
                {"name": "신앙의 힘", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "신앙으로 마법공격력과 마법방어력 증가",
                 "damage_type": DamageType.MAGICAL, "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.3}]},
                {"name": "성스러운 타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 100, "element": ElementType.LIGHT, 
                 "description": "마법공격력 기반, 언데드에게 특효", "damage_type": DamageType.MAGICAL},
                {"name": "축복", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "description": "아군의 물리방어력과 마법방어력 증가",
                 "defense_type": DefenseType.BOTH_DEF,
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 5, "intensity": 1.0}]},
                {"name": "치유의 빛", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 110, "element": ElementType.LIGHT, 
                 "description": "마법공격력 기반 성스러운 치유", "damage_type": DamageType.MAGICAL},
                {"name": "부활", "type": SkillType.SPECIAL, "target": TargetType.DEAD_ALLY,
                 "mp_cost": 15, "cast_time": 45, "cooldown": 5, "element": ElementType.LIGHT,
                 "description": "죽은 아군을 HP 50%로 부활시킴", "special_effects": ["resurrect"]},
                {"name": "천사의 강림", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "hp_power": 100, "element": ElementType.LIGHT, "cooldown": 8, "cast_time": 50,
                 "description": "마법공격력 기반 천사의 심판", "damage_type": DamageType.MAGICAL}
            ],
            
            "암흑기사": [
                {"name": "어둠의 계약", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "HP를 소모해 물리공격력 증가",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["dark_pact"]},
                {"name": "생명 흡수", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 105, "element": ElementType.DARK, 
                 "description": "물리공격력으로 공격하고 HP 회복", "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["life_steal"]},
                {"name": "저주의 검", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "element": ElementType.DARK, "description": "적의 물리방어력 저하 및 저주",
                 "defense_type": DefenseType.PHYSICAL_DEF,
                 "status_effects": [{"type": StatusType.CURSE, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_DEF, "duration": 4, "intensity": 0.7},
                                   {"type": StatusType.VULNERABLE, "duration": 3, "intensity": 1.0}]},
                {"name": "어둠의 보호", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 6, "description": "어둠의 힘으로 물리방어력 증가",
                 "defense_type": DefenseType.PHYSICAL_DEF,
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.4}]},
                {"name": "흡혈", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 125, "element": ElementType.DARK, 
                 "description": "물리공격력 기반 강력한 생명 흡수", "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["vampire_strike"]},
                {"name": "어둠의 지배자", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "brv_power": 90, "hp_power": 75, "element": ElementType.DARK,
                 "cooldown": 7, "cast_time": 35, "description": "물리+마법혼합 어둠의 저주", 
                 "damage_type": DamageType.HYBRID,
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.CURSE, "duration": 6, "intensity": 1.5},
                                   {"type": StatusType.DOMINATE, "duration": 1, "intensity": 1.0}]}
            ],
            
            "용기사": [
                {"name": "용의 비늘", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "용의 힘으로 물리방어력 증가",
                 "defense_type": DefenseType.PHYSICAL_DEF,
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.4}]},
                {"name": "드래곤 클로", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 120, "element": ElementType.FIRE, 
                 "description": "물리공격력 기반 용의 발톱 공격", "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BLEED, "duration": 3, "intensity": 1.0}]},
                {"name": "화염 숨결", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "brv_power": 75, "element": ElementType.FIRE, 
                 "description": "마법공격력 기반 용의 화염 브레스", "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BURN, "duration": 4, "intensity": 1.0}]},
                {"name": "용의 위엄", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "description": "모든 적의 물리방어력과 마법방어력 감소",
                 "defense_type": DefenseType.BOTH_DEF,
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_DEF, "duration": 4, "intensity": 0.7},
                                   {"type": StatusType.TERROR, "duration": 2, "intensity": 1.0}]},
                {"name": "드래곤 스피어", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 150, "element": ElementType.FIRE, "cast_time": 18,
                 "description": "물리공격력 기반 용의 힘이 깃든 창술", "damage_type": DamageType.PHYSICAL},
                {"name": "드래곤 로드", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "brv_power": 110, "hp_power": 90, "element": ElementType.FIRE,
                 "cooldown": 8, "cast_time": 60, "description": "물리+마법혼합 진정한 용의 힘 해방", 
                 "damage_type": DamageType.HYBRID,
                 "status_effects": [{"type": StatusType.BURN, "duration": 5, "intensity": 1.5},
                                   {"type": StatusType.TERROR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_DEF, "duration": 5, "intensity": 0.5}]}
            ],
            
            # === 마법사 계열 ===
            "아크메이지": [
                {"name": "마나 집중", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "마법공격력 대폭 증가",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.4}]},
                {"name": "매직 미사일", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 120, "accuracy": 100, "description": "마법공격력 기반 확실한 마법",
                 "damage_type": DamageType.MAGICAL},
                {"name": "파이어볼", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 7, "brv_power": 80, "element": ElementType.FIRE, "description": "마법공격력 기반 화염구",
                 "damage_type": DamageType.MAGICAL},
                {"name": "마법 방어막", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "cooldown": 3, "description": "마법방어력 대폭 증가",
                 "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 5, "intensity": 1.3}]},
                {"name": "라이트닝 볼트", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "hp_power": 170, "element": ElementType.LIGHTNING, "cast_time": 20,
                 "description": "마법공격력 기반 강력한 번개 마법", "damage_type": DamageType.MAGICAL,
                 "penetration_type": PenetrationType.MAGICAL_PIERCE, "penetration_rate": 0.25},
                {"name": "메테오", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 25, "brv_power": 150, "hp_power": 120, "element": ElementType.FIRE,
                 "cooldown": 8, "cast_time": 80, "description": "마법공격력 기반 운석 소환 마법",
                 "damage_type": DamageType.MAGICAL, "penetration_type": PenetrationType.MAGICAL_PIERCE,
                 "penetration_rate": 0.4}
            ],
            
            "정령술사": [
                {"name": "정령과의 교감", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "정령의 힘으로 마법공격력 증가",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.3}]},
                {"name": "화염 정령", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 100, "element": ElementType.FIRE, 
                 "description": "마법공격력 기반 화염 정령 소환", "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BURN, "duration": 3, "intensity": 1.0}]},
                {"name": "물 정령의 치유", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 100, "element": ElementType.WATER, 
                 "description": "마법공격력 기반 물 정령의 치유력", "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.BLESSING, "duration": 3, "intensity": 1.0}]},
                {"name": "바람 정령의 축복", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "description": "마법방어력과 속도 증가",
                 "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.4}]},
                {"name": "대지 정령의 분노", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "hp_power": 110, "element": ElementType.EARTH, "cast_time": 25,
                 "description": "마법공격력 기반 대지가 분노하여 모든 적 공격", "damage_type": DamageType.MAGICAL},
                {"name": "사대 정령 소환", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 28, "brv_power": 100, "hp_power": 85, "cooldown": 9, "cast_time": 70,
                 "description": "마법공격력 기반 모든 정령의 힘을 빌려 공격", "damage_type": DamageType.MAGICAL,
                 "penetration_type": PenetrationType.MAGICAL_PIERCE, "penetration_rate": 0.35}
            ],
            
            "시간술사": [
                {"name": "시간 가속", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "description": "자신의 시간 흐름 가속으로 마법공격력 증가",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.6}]},
                {"name": "시간 왜곡", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "description": "적의 시간 흐름 둔화 및 마법방어력 감소",
                 "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.STUN, "duration": 2, "intensity": 1.0}]},
                {"name": "시간 되돌리기", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 8, "heal_power": 120, "description": "마법공격력 기반 시간을 되돌려 상처 치유",
                 "damage_type": DamageType.MAGICAL},
                {"name": "미래 예지", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 9, "cooldown": 4, "description": "미래를 보아 마법방어력과 회피율 증가",
                 "defense_type": DefenseType.MAGICAL_DEF,
                 "special_effects": ["foresight"]},
                {"name": "시간 정지", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "cooldown": 5, "cast_time": 30, "description": "마법공격력으로 적들의 시간 정지",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.TIME_STOP, "duration": 1, "intensity": 1.0},
                                   {"type": StatusType.PARALYZE, "duration": 2, "intensity": 1.0}],
                 "is_field_skill": True},
                {"name": "시공간 붕괴", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 30, "brv_power": 130, "hp_power": 110, "cooldown": 10, "cast_time": 90,
                 "description": "마법공격력 기반 시공간을 비틀어 절대적 파괴", "damage_type": DamageType.MAGICAL,
                 "penetration_type": PenetrationType.TRUE_DAMAGE, "penetration_rate": 0.3}
            ],
            
            "차원술사": [
                {"name": "차원 균열", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 110, "description": "마법공격력으로 공간을 찢어 공격",
                 "damage_type": DamageType.MAGICAL},
                {"name": "순간이동", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 6, "description": "차원을 넘나들어 마법방어력과 회피율 증가",
                 "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 3, "intensity": 1.5}]},
                {"name": "공간 왜곡", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "description": "공간을 비틀어 적들 마법방어력 감소 및 혼란",
                 "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.BLIND, "duration": 3, "intensity": 1.0}]},
                {"name": "차원 방패", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 10, "cooldown": 3, "description": "다차원 마법방어막",
                 "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 4, "intensity": 1.5}]},
                {"name": "공간 절단", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 14, "hp_power": 160, "cast_time": 28, "description": "마법공격력으로 공간 자체를 베어내기",
                 "damage_type": DamageType.MAGICAL},
                {"name": "차원 폭풍", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 32, "brv_power": 140, "hp_power": 120, "cooldown": 9, "cast_time": 75,
                 "description": "마법공격력 기반 다차원의 폭풍으로 모든 것을 삼킴", "damage_type": DamageType.MAGICAL}
            ],
            
            "철학자": [
                {"name": "진리 탐구", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "지혜로 마법공격력 증가",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 6, "intensity": 1.3}]},
                {"name": "진실 간파", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "description": "철학적 통찰로 적의 모든 비밀과 약점을 간파",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.LIGHT,
                 "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.VULNERABLE, "duration": 4, "intensity": 1.5}],
                 "special_effects": ["analyze_enemy", "reveal_all_stats", "true_sight"]},
                {"name": "지혜의 빛", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "description": "지혜로 아군 전체 마법공격력 향상",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2}]},
                {"name": "존재 부정", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 12, "hp_power": 140, "cast_time": 25, "description": "마법공격력으로 적의 존재 자체를 부정",
                 "damage_type": DamageType.MAGICAL},
                {"name": "철학적 사고", "type": SkillType.SPECIAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 10, "cooldown": 4, "description": "깊은 사고로 모든 상태이상 해제",
                 "special_effects": ["dispel_all"]},
                {"name": "절대 진리", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 35, "brv_power": 150, "hp_power": 130, "cooldown": 10, "cast_time": 100,
                 "description": "마법공격력 기반 절대적 진리의 힘으로 모든 것을 압도", "damage_type": DamageType.MAGICAL,
                 "penetration_type": PenetrationType.TRUE_DAMAGE, "penetration_rate": 0.25}
            ],
            
            # === 원거리 & 민첩 계열 ===
            "궁수": [
                {"name": "조준", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "물리공격력과 정확도, 크리티컬 확률 증가",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2}]},
                {"name": "정밀 사격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 100, "accuracy": 98, "description": "물리공격력 기반 정확한 화살 사격",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "관통 화살", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "brv_power": 75, "description": "물리공격력으로 모든 적을 관통하는 화살",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "정찰 화살", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "element": ElementType.NEUTRAL, "description": "적의 모든 정보를 파악하고 약점 노출",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.EXPOSED, "duration": 5, "intensity": 1.0}],
                 "special_effects": ["analyze_enemy", "reveal_weakness"]},
                {"name": "연사", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "brv_power": 80, "hp_power": 60, "description": "물리공격력 기반 조준 상태시 추가 피해",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "천공의 화살", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "brv_power": 110, "hp_power": 90, "cooldown": 6, "cast_time": 35,
                 "description": "물리공격력 기반 하늘을 가르는 완벽한 화살", "damage_type": DamageType.PHYSICAL,
                 "penetration_type": PenetrationType.PHYSICAL_PIERCE, "penetration_rate": 0.3}
            ],
            
            "암살자": [
                {"name": "그림자 숨기", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "은신하여 물리공격력 증가 및 다음 공격 크리티컬 확정",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.STEALTH, "duration": 2, "intensity": 1.0},
                                   {"type": StatusType.BOOST_CRIT, "duration": 2, "intensity": 2.0},
                                   {"type": StatusType.BOOST_ATK, "duration": 2, "intensity": 1.2}]},
                {"name": "기습", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 120, "description": "물리공격력 기반 은신 상태에서 강력함",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "독 바르기", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "무기에 독 발라 물리공격력 추가 피해",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["poison_weapon"],
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1}]},
                {"name": "연막탄", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "cooldown": 3, "description": "모든 적 물리방어력 감소 및 실명",
                 "defense_type": DefenseType.PHYSICAL_DEF,
                 "status_effects": [{"type": StatusType.BLIND, "duration": 3, "intensity": 1.0}],
                 "is_field_skill": True},
                {"name": "암살술", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 170, "description": "물리공격력 기반 치명적인 급소 공격",
                 "damage_type": DamageType.PHYSICAL},
                {"name": "그림자 분신", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 15, "brv_power": 90, "hp_power": 70, "cooldown": 7, "cast_time": 10,
                 "description": "물리공격력 기반 분신이 모든 적을 동시 공격", "damage_type": DamageType.PHYSICAL}
            ],
            
            "도적": [
                {"name": "재빠른 손놀림", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "물리공격력과 속도 증가 및 회피율 상승",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.3},
                                   {"type": StatusType.BOOST_DODGE, "duration": 4, "intensity": 1.2}]},
                {"name": "기습 공격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 110, "description": "물리공격력 기반 빠른 속도의 기습",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.NEUTRAL,
                 "status_effects": [{"type": StatusType.EXPOSED, "duration": 2, "intensity": 1.0}]},
                {"name": "아이템 훔치기", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "description": "적의 아이템을 훔치고 버프/디버프 전이",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["steal_item", "steal_buff"]},
                {"name": "연속 베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 85, "description": "물리공격력으로 속도 버프시 3회 연속 공격",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.WIND,
                 "status_effects": [{"type": StatusType.BLEED, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["multi_hit"], "penetration_type": PenetrationType.ARMOR_BREAK,
                 "penetration_rate": 0.15},
                {"name": "숨겨둔 아이템", "type": SkillType.FIELD, "target": TargetType.SELF,
                 "mp_cost": 6, "cooldown": 3, "description": "순간이동하며 모든 아군 회복 (마법공격력 기반)",
                 "damage_type": DamageType.MAGICAL, "heal_power": 80, "element": ElementType.DARK,
                 "is_field_skill": True, "special_effects": ["teleport_heal"]},
                {"name": "완벽한 도둑질", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "cooldown": 5, "description": "물리공격력으로 모든 적 공격하며 아이템 획득",
                 "damage_type": DamageType.PHYSICAL, "brv_power": 70, "hp_power": 50,
                 "special_effects": ["mass_steal", "confusion"]}
            ],
            
            "해적": [
                {"name": "이도류", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "물리공격력과 치명타율 대폭 증가",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.3},
                                   {"type": StatusType.BOOST_CRIT, "duration": 4, "intensity": 1.5}]},
                {"name": "칼부림", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 115, "description": "물리공격력으로 양손 검 난도질",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.LIGHTNING,
                 "status_effects": [{"type": StatusType.BLEED, "duration": 4, "intensity": 1.2}]},
                {"name": "바다의 저주", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "element": ElementType.WATER, "description": "바다의 저주로 모든 능력 감소",
                 "defense_type": DefenseType.BOTH_DEF,
                 "status_effects": [{"type": StatusType.CURSE, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_SPD, "duration": 4, "intensity": 0.7}]},
                {"name": "해적의 함성", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 5, "cooldown": 3, "description": "동료들 사기 진작 및 공포 면역",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 3, "intensity": 1.2},
                                   {"type": StatusType.INSPIRATION, "duration": 5, "intensity": 1.0}]},
                {"name": "해상 치료술", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 90, "description": "바다의 정령 힘으로 전체 치유 (마법공격력 기반)",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.WATER,
                 "is_field_skill": True, "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}]},
                {"name": "폭풍의 함대", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 17, "brv_power": 100, "hp_power": 80, "element": ElementType.WATER,
                 "cooldown": 6, "cast_time": 20, "description": "물리+마법 혼합 유령 함대의 일제 사격",
                 "damage_type": DamageType.HYBRID, "status_effects": [{"type": StatusType.FEAR, "duration": 2, "intensity": 1.0}]}
            ],
            
            "사무라이": [
                {"name": "무사도", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "무사의 정신으로 물리공격력과 정신력 향상",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2},
                                   {"type": StatusType.FOCUS, "duration": 5, "intensity": 1.0}]},
                {"name": "거합베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 125, "description": "물리공격력 기반 일순간의 발도술",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.LIGHTNING,
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 2, "intensity": 1.0}]},
                {"name": "명상", "type": SkillType.HEAL, "target": TargetType.SELF,
                 "mp_cost": 4, "heal_power": 80, "description": "마법공격력 기반 정신 집중으로 HP 회복",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.NEUTRAL,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}]},
                {"name": "진검승부", "type": SkillType.COUNTER, "target": TargetType.SELF,
                 "mp_cost": 5, "cooldown": 2, "description": "반격 태세, 공격받으면 3배 반격 및 보호막 생성",
                 "status_effects": [{"type": StatusType.COUNTER, "duration": 3, "intensity": 3.0},
                                   {"type": StatusType.BARRIER, "duration": 3, "intensity": 1.5}]},
                {"name": "사무라이 치유법", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 85, "description": "무사의 정신력으로 전체 치유 (마법공격력 기반)",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.LIGHT,
                 "is_field_skill": True, "status_effects": [{"type": StatusType.BLESSING, "duration": 4, "intensity": 1.0}]},
                {"name": "오의 무상베기", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 20, "brv_power": 120, "hp_power": 100, "cooldown": 8, "cast_time": 40,
                 "description": "물리공격력 기반 무사의 최고 오의", "damage_type": DamageType.PHYSICAL,
                 "element": ElementType.NEUTRAL, "status_effects": [{"type": StatusType.PETRIFY, "duration": 1, "intensity": 1.0}],
                 "penetration_type": PenetrationType.TRUE_DAMAGE, "penetration_rate": 0.2}
            ],
            
            # === 마법 지원 계열 ===
            "바드": [
                {"name": "용기의 노래", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "description": "마법공격력으로 아군 공격력과 치명타율 증가",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2},
                                   {"type": StatusType.BOOST_CRIT, "duration": 4, "intensity": 1.3}]},
                {"name": "회복의 선율", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "heal_power": 70, "description": "마법공격력 기반 모든 아군 치유 및 재생 부여",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}]},
                {"name": "절망의 노래", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "description": "적들의 사기 저하 및 모든 능력 감소",
                 "defense_type": DefenseType.BOTH_DEF, "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.DESPAIR, "duration": 4, "intensity": 1.0}]},
                {"name": "신속의 리듬", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "cooldown": 3, "description": "아군 속도와 회피율 대폭 증가",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.3},
                                   {"type": StatusType.HASTE, "duration": 4, "intensity": 1.0}]},
                {"name": "천상의 치유가", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 120, "description": "마법공격력으로 강력한 전체 치유 및 상태이상 해제",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.LIGHT,
                 "is_field_skill": True, "special_effects": ["dispel_debuffs"]},
                {"name": "천상의 합창", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 25, "cooldown": 10, "cast_time": 55, "description": "마법공격력으로 모든 아군 대규모 치유 및 일시적 보호",
                 "damage_type": DamageType.MAGICAL, "heal_power": 150, "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.INVINCIBLE, "duration": 1, "intensity": 1.0}],
                 "special_effects": ["mass_heal"]}
            ],
            
            "무당": [
                {"name": "정령 소환", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "정령의 힘으로 마법공격력과 영적 보호 증가",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.3},
                                   {"type": StatusType.SPIRIT_LINK, "duration": 5, "intensity": 1.0}]},
                {"name": "저주의 인형", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "description": "저주 인형으로 지속 피해 및 능력 봉인",
                 "element": ElementType.DARK, "defense_type": DefenseType.MAGICAL_DEF,
                 "status_effects": [{"type": StatusType.CURSE, "duration": 6, "intensity": 1.0},
                                   {"type": StatusType.NECROSIS, "duration": 4, "intensity": 1.0}]},
                {"name": "치유의 춤", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 80, "description": "마법공격력 기반 무당의 춤으로 치유 및 정화",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.EARTH,
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 3, "intensity": 1.0}]},
                {"name": "영혼 파악", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "description": "적의 정보 완전 파악 및 정신 공격",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.CONFUSION, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["analyze_enemy", "soul_damage"]},
                {"name": "정령 치유술", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 100, "description": "정령들의 힘으로 강력한 전체 치유 (마법공격력 기반)",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.WATER,
                 "is_field_skill": True, "status_effects": [{"type": StatusType.REGENERATION, "duration": 5, "intensity": 1.2}]},
                {"name": "대자연의 심판", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "brv_power": 110, "hp_power": 90, "element": ElementType.EARTH,
                 "cooldown": 8, "cast_time": 30, "description": "마법공격력으로 자연의 모든 힘을 빌려 심판",
                 "damage_type": DamageType.MAGICAL, "status_effects": [{"type": StatusType.PETRIFY, "duration": 2, "intensity": 1.0}]}
            ],
            
            "드루이드": [
                {"name": "자연과의 교감", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "자연의 힘으로 능력 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2}]},
                {"name": "가시 덩굴", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "element": ElementType.EARTH, "description": "가시로 적들 속박",
                 "status_effects": [{"type": StatusType.STUN, "duration": 2, "intensity": 1.0}]},
                {"name": "자연 치유", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "heal_power": 90, "element": ElementType.EARTH, "description": "자연의 생명력"},
                {"name": "동물 변신", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 7, "cooldown": 3, "description": "야생동물로 변신, 모든 능력 증가",
                 "status_effects": [{"type": StatusType.BERSERK, "duration": 4, "intensity": 1.5}]},
                {"name": "번개 폭풍", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 120, "element": ElementType.LIGHTNING, "cast_time": 20,
                 "description": "자연의 번개를 소환"},
                {"name": "가이아의 분노", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 24, "brv_power": 120, "hp_power": 100, "element": ElementType.EARTH,
                 "cooldown": 8, "cast_time": 40, "description": "대지의 여신이 직접 심판"}
            ],
            
            "신관": [
                {"name": "신의 가호", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 5, "description": "모든 아군에게 보호막",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 5, "intensity": 1.0}]},
                {"name": "성스러운 빛", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 100, "element": ElementType.LIGHT, "description": "언데드 특효"},
                {"name": "대치유술", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 7, "heal_power": 150, "element": ElementType.LIGHT, "description": "강력한 신성 치유"},
                {"name": "부활술", "type": SkillType.SPECIAL, "target": TargetType.DEAD_ALLY,
                 "mp_cost": 12, "cooldown": 4, "cast_time": 20, "description": "죽은 아군을 부활시킴",
                 "special_effects": ["resurrect"]},
                {"name": "신벌", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "hp_power": 160, "element": ElementType.LIGHT, "cast_time": 15,
                 "description": "신의 벌로 사악한 적 처벌"},
                {"name": "천국의 문", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 25, "cooldown": 8, "cast_time": 50, "description": "천국의 힘으로 모든 것 회복",
                 "heal_power": 300, "special_effects": ["divine_blessing"]}
            ],
            
            "성직자": [
                {"name": "평화의 기도", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "description": "아군들의 마음을 안정시킴",
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.GUARDIAN, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.INSPIRATION, "duration": 3, "intensity": 1.0}]},
                {"name": "정화의 빛", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "element": ElementType.LIGHT, "description": "모든 디버프 제거",
                 "special_effects": ["dispel_debuffs"]},
                {"name": "신성한 치유", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 85, "element": ElementType.LIGHT, "description": "전체 치유",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.HOLY_SHIELD, "duration": 4, "intensity": 1.0}]},
                {"name": "침묵의 서약", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "description": "적들을 침묵시킴",
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 3, "intensity": 1.0}]},
                {"name": "순교자의 길", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 9, "cooldown": 4, "description": "자신의 HP를 소모해 아군 완전 치유",
                 "special_effects": ["martyrdom"]},
                {"name": "신의 심판", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "hp_power": 120, "element": ElementType.LIGHT, "cooldown": 7, "cast_time": 20,
                 "description": "신의 이름으로 모든 죄를 심판"}
            ],
            
            # === 특수 계열 ===
            "몽크": [
                {"name": "기 수련", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "내면의 기를 단련하여 능력 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2},
                                   {"type": StatusType.FOCUS, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.BOOST_ACCURACY, "duration": 5, "intensity": 1.3}]},
                {"name": "연속 주먹", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 90, "description": "기 수련 상태시 2회 공격",
                 "special_effects": ["combo_attack"]},
                {"name": "명상", "type": SkillType.HEAL, "target": TargetType.SELF,
                 "mp_cost": 4, "heal_power": 100, "description": "명상으로 HP와 MP 회복",
                 "special_effects": ["mp_restore"],
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.INSPIRATION, "duration": 3, "intensity": 1.0}]},
                {"name": "기 폭발", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "brv_power": 75, "hp_power": 55, "description": "내재된 기를 폭발시킴"},
                {"name": "철의 주먹", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 145, "description": "강철같은 주먹 공격"},
                {"name": "깨달음의 경지", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 18, "cooldown": 6, "cast_time": 20, "description": "완전한 깨달음으로 모든 능력 초월",
                 "special_effects": ["enlightenment"]}
            ],
            
            "마검사": [
                {"name": "마검 각성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "물리공격력과 마법공격력 동시 증가",
                 "damage_type": DamageType.HYBRID,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.3}]},
                {"name": "마법 검격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 110, "element": ElementType.NEUTRAL, 
                 "description": "물리공격력+마법공격력 복합 피해", "damage_type": DamageType.HYBRID},
                {"name": "원소 부여", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "description": "검에 마법력을 부여하여 복합 공격력 증가",
                 "damage_type": DamageType.HYBRID, "special_effects": ["elemental_weapon"]},
                {"name": "마검진", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "cooldown": 3, "description": "마법진으로 지속 마법 피해",
                 "damage_type": DamageType.MAGICAL, "is_field_skill": True, "special_effects": ["magic_field"]},
                {"name": "마력 폭발", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 150, "cast_time": 10, 
                 "description": "물리+마법 복합 에너지 폭발", "damage_type": DamageType.HYBRID},
                {"name": "마검의 진리", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "brv_power": 115, "hp_power": 95, "cooldown": 7, "cast_time": 20,
                 "description": "물리와 마법의 완벽한 융합 공격", "damage_type": DamageType.HYBRID}
            ],
            
            "연금술사": [
                {"name": "물질 변환", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "재료를 변환하여 임시 아이템 생성",
                 "special_effects": ["transmute_item"]},
                {"name": "독성 폭탄", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "brv_power": 80, "element": ElementType.POISON, "description": "독성 폭탄 투척",
                 "status_effects": [{"type": StatusType.POISON, "duration": 4, "intensity": 1.0}]},
                {"name": "회복 포션", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "heal_power": 120, "description": "즉석에서 포션 제조"},
                {"name": "강화 주사", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "description": "일시적 능력 강화 약물",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.4}]},
                {"name": "산성 용해", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 140, "element": ElementType.POISON, "description": "강산으로 적 용해"},
                {"name": "철학자의 돌", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 25, "cooldown": 8, "cast_time": 30, "description": "전설의 돌로 모든 것을 황금으로",
                 "special_effects": ["philosophers_stone"]}
            ],
            
            "기계공학자": [
                {"name": "기계 조립", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "전투 중 간이 기계 제작",
                 "special_effects": ["craft_gadget"]},
                {"name": "톱니바퀴 투척", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 105, "description": "회전하는 톱니바퀴 공격"},
                {"name": "자동 포탑", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 7, "cooldown": 4, "description": "자동으로 공격하는 포탑 설치",
                 "is_field_skill": True, "special_effects": ["auto_turret"]},
                {"name": "기계 수리", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "heal_power": 100, "description": "기계적 수리로 치유"},
                {"name": "폭발 장치", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 9, "hp_power": 110, "cast_time": 25, "description": "폭발 장치로 광역 피해"},
                {"name": "메카닉 아머", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 20, "cooldown": 7, "cast_time": 20, "description": "강력한 기계 갑옷 착용",
                 "special_effects": ["mech_suit"]}
            ],
            
            "네크로맨서": [
                {"name": "시체 소생", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 5, "description": "언데드 하수인 소환",
                 "special_effects": ["summon_undead"]},
                {"name": "생명력 흡수", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 95, "element": ElementType.DARK, "description": "생명력을 빨아들임",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["life_drain"],
                 "status_effects": [{"type": StatusType.NECROSIS, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.WEAKNESS, "duration": 3, "intensity": 1.0}]},
                {"name": "공포 주입", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 7, "element": ElementType.DARK, "description": "모든 적에게 공포",
                 "status_effects": [{"type": StatusType.FEAR, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.MADNESS, "duration": 2, "intensity": 1.0},
                                   {"type": StatusType.TERROR, "duration": 3, "intensity": 1.0}]},
                {"name": "뼈 감옥", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "description": "적을 뼈로 만든 감옥에 가둠",
                 "status_effects": [{"type": StatusType.ROOT, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.PARALYZE, "duration": 2, "intensity": 1.0},
                                   {"type": StatusType.PETRIFY, "duration": 1, "intensity": 1.0}]},
                {"name": "죽음의 손길", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 11, "hp_power": 160, "element": ElementType.DARK, "cast_time": 10,
                 "description": "죽음의 마법으로 직접 공격"},
                {"name": "언데드 군단", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 28, "brv_power": 120, "hp_power": 100, "element": ElementType.DARK,
                 "cooldown": 9, "cast_time": 40, "description": "거대한 언데드 군단 소환"}
            ]
        }
        
        return class_skills.get(class_name, [])

    def get_skill_by_name(self, skill_name: str):
        """스킬 이름으로 스킬 데이터 검색"""
        for skills in self.class_skills.values():
            for skill in skills:
                if skill["name"] == skill_name:
                    return skill
        return None
    
    def get_skills_by_type(self, skill_type: SkillType) -> List[Dict]:
        """스킬 타입별로 모든 스킬 검색"""
        matching_skills = []
        for skills in self.class_skills.values():
            for skill in skills:
                if skill["type"] == skill_type:
                    matching_skills.append(skill)
        return matching_skills
    
    def get_class_ultimate_skills(self, class_name: str) -> List[Dict]:
        """클래스의 궁극기 스킬들 반환"""
        skills = self.get_class_skills(class_name)
        return [skill for skill in skills if skill["type"] == SkillType.ULTIMATE]
    
    def calculate_skill_damage(self, skill: Dict, attacker_stats: Dict, defender_stats: Dict = None, is_ally_attacker: bool = True) -> Dict:
        """스킬 데미지 계산 (아군/적 구분하여 배수 적용)"""
        damage_result = {
            "brv_damage": 0,
            "hp_damage": 0,
            "critical": False,
            "elemental_bonus": 1.0
        }
        
        # 사용할 배수 결정
        multiplier = self.skill_power_multiplier if is_ally_attacker else self.enemy_skill_power_multiplier
        
        # BRV 데미지 계산
        if "brv_power" in skill:
            base_brv = attacker_stats.get("atk", 100) * (skill["brv_power"] / 100) * multiplier
            if defender_stats:
                defense_factor = max(0.1, 1.0 - (defender_stats.get("def", 50) / 200))
                damage_result["brv_damage"] = int(base_brv * defense_factor)
            else:
                damage_result["brv_damage"] = int(base_brv)
        
        # HP 데미지 계산
        if "hp_power" in skill:
            base_hp = attacker_stats.get("atk", 100) * (skill["hp_power"] / 100) * multiplier
            if defender_stats:
                defense_factor = max(0.1, 1.0 - (defender_stats.get("def", 50) / 200))
                damage_result["hp_damage"] = int(base_hp * defense_factor)
            else:
                damage_result["hp_damage"] = int(base_hp)
        
        return damage_result
    
    def get_adjusted_mp_cost(self, skill: Dict, is_ally: bool = True) -> int:
        """아군/적에 따른 MP 소모량 계산"""
        base_mp_cost = skill.get("mp_cost", 0)
        if is_ally:
            # 아군은 MP 소모량 증가
            return int(base_mp_cost * self.ally_mp_cost_multiplier)
        else:
            # 적은 기본 MP 소모량
            return base_mp_cost
    
    def can_use_skill(self, skill: Dict, caster_stats: Dict, is_ally: bool = True) -> tuple[bool, str]:
        """스킬 사용 가능 여부 확인"""
        # MP 확인 (아군/적에 따른 조정된 MP 소모량)
        current_mp = caster_stats.get("current_mp", 0)
        required_mp = self.get_adjusted_mp_cost(skill, is_ally)
        
        if current_mp < required_mp:
            return False, f"MP 부족 (필요: {required_mp}, 현재: {current_mp})"
        
        # 쿨다운 확인 (실제 구현 시 필요)
        if skill.get("cooldown", 0) > 0:
            skill_cooldown = self.get_skill_cooldown(caster_stats.get("character_id", "unknown"), skill["name"])
            if skill_cooldown > 0:
                return False, f"쿨다운 중 (남은 턴: {skill_cooldown})"
        
        return True, "사용 가능"
    
    def get_skill_cooldown(self, character_id: str, skill_name: str) -> int:
        """캐릭터의 특정 스킬 쿨다운 확인"""
        if character_id not in self.cooldowns:
            return 0
        return self.cooldowns[character_id].get(skill_name, 0)
    
    def set_skill_cooldown(self, character_id: str, skill_name: str, cooldown_turns: int):
        """캐릭터의 스킬 쿨다운 설정"""
        if character_id not in self.cooldowns:
            self.cooldowns[character_id] = {}
        self.cooldowns[character_id][skill_name] = cooldown_turns
    
    def reduce_cooldowns(self, character_id: str):
        """캐릭터의 모든 스킬 쿨다운 1턴 감소"""
        if character_id in self.cooldowns:
            for skill_name in list(self.cooldowns[character_id].keys()):
                self.cooldowns[character_id][skill_name] = max(0, self.cooldowns[character_id][skill_name] - 1)
                if self.cooldowns[character_id][skill_name] == 0:
                    del self.cooldowns[character_id][skill_name]
    
    def reduce_all_cooldowns(self):
        """모든 캐릭터의 쿨다운 1턴 감소"""
        for character_id in list(self.cooldowns.keys()):
            self.reduce_cooldowns(character_id)
            if not self.cooldowns[character_id]:  # 빈 딕셔너리면 삭제
                del self.cooldowns[character_id]
    
    def get_skills(self, class_name: str) -> List[Dict[str, Any]]:
        """특정 클래스의 스킬 목록 반환 (호환성을 위한 메서드)"""
        return self.skills_by_class.get(class_name, [])
    
    def get_class_skills(self, class_name: str) -> List[Dict[str, Any]]:
        """특정 클래스의 스킬 목록 반환"""
        return self.skills_by_class.get(class_name, [])
    
    def get_skill_mp_cost(self, skill: Dict[str, Any], is_ally: bool = True) -> int:
        """스킬의 실제 MP 소모량 계산 (아군은 배수 적용)"""
        base_mp_cost = skill.get('mp_cost', 0)
        if is_ally:
            return int(base_mp_cost * self.ally_mp_cost_multiplier)
        else:
            return base_mp_cost  # 적은 MP 배수 적용 안함
    
    def get_enemy_skill_power(self, skill_power: float) -> float:
        """적 스킬의 위력에 배수 적용"""
        return skill_power * self.enemy_skill_power_multiplier
skill_system = NewSkillSystem()

# 편의 함수들
def get_class_skills(class_name: str) -> List[Dict]:
    """특정 클래스의 스킬 목록 반환"""
    return skill_system.get_class_skills(class_name)

def get_skill_by_name(skill_name: str) -> Dict:
    """스킬 이름으로 스킬 정보 검색"""
    return skill_system.get_skill_by_name(skill_name)

def calculate_skill_damage(skill: Dict, attacker_stats: Dict, defender_stats: Dict = None) -> Dict:
    """스킬 데미지 계산"""
    return skill_system.calculate_skill_damage(skill, attacker_stats, defender_stats)

def can_use_skill(skill: Dict, caster_stats: Dict) -> tuple[bool, str]:
    """스킬 사용 가능 여부 확인"""
    return skill_system.can_use_skill(skill, caster_stats)


if __name__ == "__main__":
    # 테스트 코드
    print("=== 새로운 스킬 시스템 테스트 ===")
    
    # 전사 스킬 테스트
    warrior_skills = get_class_skills("전사")
    print(f"\n전사 스킬 ({len(warrior_skills)}개):")
    for skill in warrior_skills:
        print(f"- {skill['name']}: {skill['description']} (MP: {skill['mp_cost']})")
    
    # 아크메이지 스킬 테스트  
    archmage_skills = get_class_skills("아크메이지")
    print(f"\n아크메이지 스킬 ({len(archmage_skills)}개):")
    for skill in archmage_skills:
        print(f"- {skill['name']}: {skill['description']} (MP: {skill['mp_cost']})")
    
    # 궁극기 스킬 테스트
    ultimate_skills = skill_system.get_skills_by_type(SkillType.ULTIMATE)
    print(f"\n모든 궁극기 ({len(ultimate_skills)}개):")
    for skill in ultimate_skills:
        print(f"- {skill['name']}: MP {skill['mp_cost']}, 쿨다운 {skill.get('cooldown', 0)}턴")
    
    # 모든 클래스 스킬 수 확인
    total_skills = 0
    print(f"\n=== 클래스별 스킬 수 ===")
    for class_name in ["전사", "검성", "검투사", "광전사", "기사", "성기사", "암흑기사", "용기사",
                      "아크메이지", "정령술사", "시간술사", "차원술사", "철학자",
                      "궁수", "암살자", "도적", "해적", "사무라이", "바드", "무당", "드루이드", 
                      "신관", "성직자", "몽크", "마검사", "연금술사", "기계공학자", "네크로맨서"]:
        skills = get_class_skills(class_name)
        total_skills += len(skills)
        print(f"{class_name}: {len(skills)}개 스킬")
    
    print(f"\n총 {total_skills}개의 스킬이 구현되었습니다!") 


    
    def get_skills_for_class(self, character_class: str) -> List[Dict[str, Any]]:
        """직업별 스킬 반환"""
        return self.skills_by_class.get(character_class, [])
    
    def get_skill_by_name(self, character_class: str, skill_name: str) -> Dict[str, Any]:
        """특정 스킬 검색"""
        skills = self.get_skills_for_class(character_class)
        for skill in skills:
            if skill["name"] == skill_name:
                return skill
        return None
    
    def execute_skill_effects(self, skill_data: Dict[str, Any], caster, targets: List, **kwargs) -> List[str]:
        """스킬의 실제 효과 실행"""
        messages = []
        skill_type = skill_data.get("skill_type", SkillType.BRV_ATTACK)
        effects = skill_data.get("effects", [])
        
        # 기본 피해/치유 처리
        base_value = skill_data.get("base_value", 0)
        scaling = skill_data.get("scaling", {})
        
        for target in targets:
            if not target:
                continue
                
            # 피해 계산
            if skill_type in [SkillType.BRV_ATTACK, SkillType.HP_ATTACK, SkillType.BRV_HP_ATTACK]:
                damage = self._calculate_skill_damage(skill_data, caster, target)
                target.current_hp = max(1, target.current_hp - damage)
                messages.append(f"💥 {target.name}이(가) {damage} 피해를 받았습니다!")
                
                # 공격 시 특수 효과 처리
                attack_messages = caster.process_attack_effects(target, damage)
                messages.extend(attack_messages)
            
            # 치유 계산
            elif skill_type == SkillType.HEAL:
                heal_amount = self._calculate_heal_amount(skill_data, caster)
                old_hp = target.current_hp
                target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                actual_heal = target.current_hp - old_hp
                if actual_heal > 0:
                    messages.append(f"💚 {target.name}이(가) {actual_heal} HP 회복했습니다!")
        
        # 상태 효과 적용
        for effect in effects:
            if effect.get("type") == "status":
                status_name = effect.get("status")
                duration = effect.get("duration", 3)
                intensity = effect.get("intensity", 1.0)
                
                for target in targets:
                    if hasattr(target, 'status_manager') and target.status_manager:
                        target.status_manager.add_status(status_name, duration, intensity)
                        messages.append(f"✨ {target.name}에게 {status_name} 효과 적용! ({duration}턴)")
            
            elif effect.get("type") == "buff":
                buff_type = effect.get("buff_type")
                buff_value = effect.get("value", 10)
                duration = effect.get("duration", 5)
                
                for target in targets:
                    if buff_type == "attack":
                        target.temp_attack_bonus = getattr(target, 'temp_attack_bonus', 0) + buff_value
                        target.temp_attack_duration = duration
                    elif buff_type == "defense":
                        target.temp_defense_bonus = getattr(target, 'temp_defense_bonus', 0) + buff_value
                        target.temp_defense_duration = duration
                    elif buff_type == "speed":
                        target.temp_speed_bonus = getattr(target, 'temp_speed_bonus', 0) + buff_value
                        target.temp_speed_duration = duration
                    elif buff_type == "magic":
                        target.temp_magic_bonus = getattr(target, 'temp_magic_bonus', 0) + buff_value
                        target.temp_magic_duration = duration
                    
                    messages.append(f"🔆 {target.name}의 {buff_type} +{buff_value} ({duration}턴)")
            
            elif effect.get("type") == "debuff":
                debuff_type = effect.get("debuff_type")
                debuff_value = effect.get("value", 10)
                duration = effect.get("duration", 3)
                
                for target in targets:
                    if debuff_type == "attack":
                        target.temp_attack_bonus = getattr(target, 'temp_attack_bonus', 0) - debuff_value
                        target.temp_attack_duration = duration
                    elif debuff_type == "defense":
                        target.temp_defense_bonus = getattr(target, 'temp_defense_bonus', 0) - debuff_value
                        target.temp_defense_duration = duration
                    elif debuff_type == "speed":
                        target.temp_speed_bonus = getattr(target, 'temp_speed_bonus', 0) - debuff_value
                        target.temp_speed_duration = duration
                    
                    messages.append(f"🔽 {target.name}의 {debuff_type} -{debuff_value} ({duration}턴)")
            
            elif effect.get("type") == "special":
                special_type = effect.get("special_type")
                
                if special_type == "summon":
                    summon_type = effect.get("summon_type", "골렘")
                    duration = effect.get("duration", 10)
                    caster.temp_summoned_ally = summon_type
                    caster.temp_ally_duration = duration
                    messages.append(f"🤖 {summon_type} 소환! ({duration}턴)")
                
                elif special_type == "teleport":
                    caster.temp_dodge_bonus = getattr(caster, 'temp_dodge_bonus', 0) + 100
                    caster.temp_teleport_duration = 1
                    messages.append(f"🌀 {caster.name}이(가) 순간이동으로 다음 공격 회피!")
                
                elif special_type == "time_stop":
                    caster.temp_extra_turn = True
                    messages.append(f"⏰ 시간 정지! {caster.name}이(가) 추가 턴 획득!")
                
                elif special_type == "barrier":
                    barrier_type = effect.get("barrier_type", "물리보호막")
                    barrier_value = effect.get("value", 50)
                    duration = effect.get("duration", 5)
                    
                    for target in targets:
                        target.temp_barrier_hp = getattr(target, 'temp_barrier_hp', 0) + barrier_value
                        target.temp_barrier_duration = duration
                        messages.append(f"🛡️ {target.name}에게 {barrier_type} ({barrier_value}) 적용!")
                
                elif special_type == "transform":
                    transform_type = effect.get("transform_type", "늑대")
                    duration = effect.get("duration", 5)
                    bonus = effect.get("bonus", 20)
                    
                    caster.temp_transform_type = transform_type
                    caster.temp_transform_duration = duration
                    caster.temp_attack_bonus = getattr(caster, 'temp_attack_bonus', 0) + bonus
                    caster.temp_speed_bonus = getattr(caster, 'temp_speed_bonus', 0) + bonus
                    messages.append(f"🐺 {caster.name}이(가) {transform_type}로 변신! 공격력/속도 +{bonus}")
        
        return messages
    
    def _calculate_skill_damage(self, skill_data: Dict, caster, target) -> int:
        """스킬 피해 계산"""
        base_value = skill_data.get("base_value", 0)
        scaling = skill_data.get("scaling", {})
        
        # 스케일링 계산
        total_damage = base_value
        
        if "physical_attack" in scaling:
            total_damage += int(caster.physical_attack * scaling["physical_attack"])
        if "magic_attack" in scaling:
            total_damage += int(caster.magic_attack * scaling["magic_attack"])
        if "max_hp" in scaling:
            total_damage += int(caster.max_hp * scaling["max_hp"])
        if "current_hp" in scaling:
            total_damage += int(caster.current_hp * scaling["current_hp"])
        if "missing_hp" in scaling:
            missing_hp = caster.max_hp - caster.current_hp
            total_damage += int(missing_hp * scaling["missing_hp"])
        
        # 방어력 적용
        damage_type = skill_data.get("damage_type", DamageType.PHYSICAL)
        if damage_type == DamageType.PHYSICAL:
            defense = target.physical_defense
        elif damage_type == DamageType.MAGICAL:
            defense = target.magic_defense
        else:  # HYBRID
            defense = (target.physical_defense + target.magic_defense) // 2
        
        # 피해 공식: (공격력 / 방어력) * 기타 수정치
        if defense > 0:
            final_damage = max(1, int(total_damage * (total_damage / (total_damage + defense))))
        else:
            final_damage = total_damage
        
        return max(1, final_damage)
    
    def _calculate_heal_amount(self, skill_data: Dict, caster) -> int:
        """치유량 계산"""
        base_value = skill_data.get("base_value", 0)
        scaling = skill_data.get("scaling", {})
        
        total_heal = base_value
        
        if "magic_attack" in scaling:
            total_heal += int(caster.magic_attack * scaling["magic_attack"])
        if "max_hp" in scaling:
            total_heal += int(caster.max_hp * scaling["max_hp"])
        
        return max(1, total_heal)

# 전역 인스턴스
new_skill_system = NewSkillSystem()
