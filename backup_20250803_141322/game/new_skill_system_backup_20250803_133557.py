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
    BATTLEFIELD = "전장"  # 필드 스킬용 타겟

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
    MANA_SHIELD = "마나실드"
    ANALYZE = "분석"
    TRANSCENDENCE = "초월"
    AUTO_TURRET = "자동포탑"
    REPAIR_DRONE = "수리드론"
    MECHANICAL_ARMOR = "기계갑옷"

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
            # === 적응형 전투마스터 - 전사 ===
            "전사": [
                # 균형의 수호자 - [균형][적응] 키워드 특화
                {"name": "방패강타", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 80, "accuracy": 95,
                 "description": "[균형][적응] 방어력 기반 공격. HP 상태에 따라 효과 변화",
                 "damage_type": DamageType.PHYSICAL, "sfx": "shield_bash",
                 "status_effects": [{"type": StatusType.STUN, "duration": 1, "intensity": 0.3}],
                 "organic_effects": {"불굴의_의지": 0.3, "균형감각": 0.25, "전투_본능": 0.2}},
                {"name": "철벽방어", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "[균형][방어] 방어력 15% 증가 + 물리 피해 감소",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"불굴의_의지": 0.4, "균형감각": 0.3}},
                {"name": "연속베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 60, "accuracy": 90,
                 "description": "[적응][연속] 2회 연속 공격. 첫 타 성공 시 두 번째 타격 위력 증가",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["double_attack"],
                 "organic_effects": {"전투_본능": 0.35, "균형감각": 0.25, "불굴의_의지": 0.15}},
                {"name": "전투함성", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "description": "[균형][지원] 아군 공격력 12% 증가 + 기운 회복",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.12}],
                 "organic_effects": {"균형감각": 0.3, "전투_본능": 0.25, "리더십": 0.2}},
                {"name": "파괴의일격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 90, "cast_time": 15, "accuracy": 85,
                 "description": "[적응][파괴] 강력한 단일 공격. 적 방어력 일부 무시",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["armor_pierce"],
                 "organic_effects": {"전투_본능": 0.4, "불굴의_의지": 0.3, "균형감각": 0.2}},
                {"name": "전사의격노", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 15, "hp_power": 120, "cast_time": 20, "cooldown": 6,
                 "description": "[궁극][격노] HP가 낮을수록 강력. 크리티컬 확률 대폭 증가",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["berserker_rage"],
                 "organic_effects": {"불굴의_의지": 0.5, "전투_본능": 0.4, "균형감각": 0.3}}
            ],
            
            "검성": [
                # 검의 성인 - [검술][집중] 키워드 특화
                {"name": "검기응축", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[집중][검기] 검기를 응축하여 공격력 20% 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"검술_대가": 0.4, "집중력": 0.35, "무술_수행": 0.25}},
                {"name": "일섬", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 85, "accuracy": 98, "crit_rate": 20,
                 "description": "[검술][일격] 번개같은 일섬. 높은 치명타율",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["iai_cut"],
                 "organic_effects": {"검술_대가": 0.45, "집중력": 0.3, "무술_수행": 0.25}},
                {"name": "검압베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 100, "accuracy": 92,
                 "description": "[검술][검압] 검기로 강력한 단일 공격",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_pressure"],
                 "organic_effects": {"검술_대가": 0.4, "집중력": 0.3, "무술_수행": 0.3}},
                {"name": "검심일체", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "description": "[집중][검심] 검과 마음이 하나 되어 회피율과 명중률 증가",
                 "status_effects": [{"type": StatusType.FOCUS, "duration": 6, "intensity": 1.3}],
                 "special_effects": ["sword_unity"],
                 "organic_effects": {"검술_대가": 0.4, "집중력": 0.4, "무술_수행": 0.2}},
                {"name": "무쌍베기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 105, "crit_rate": 15, "cast_time": 16,
                 "description": "[검술][무쌍] 완벽한 검술로 적을 베어냄",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["peerless_cut"],
                 "organic_effects": {"검술_대가": 0.5, "집중력": 0.3, "무술_수행": 0.2}},
                {"name": "검제비의", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 17, "hp_power": 115, "cooldown": 7, "cast_time": 35,
                 "description": "[궁극][검술] 검의 제왕 비의. 적 전체를 베는 절대검술",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_emperor"],
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"검술_대가": 0.6, "집중력": 0.4, "무술_수행": 0.35, "전투_본능": 0.3}}
            ],
            
            "검투사": [
                # 투기장의 전사 - [검투][생존] 키워드 특화
                {"name": "투기장의기술", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 2, "brv_power": 75, "description": "[검투][기본] 기본 검투 기술",
                 "damage_type": DamageType.PHYSICAL,
                 "organic_effects": {"전투_본능": 0.4, "생존_기술": 0.3, "무술_수행": 0.3}},
                {"name": "군중의함성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[검투][응원] 관중의 응원으로 공격력 15% 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"전투_본능": 0.35, "생존_기술": 0.3, "지휘력": 0.25}},
                {"name": "네트던지기", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "description": "[검투][구속] 네트로 적의 움직임 봉쇄",
                 "status_effects": [{"type": StatusType.STUN, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"전투_본능": 0.4, "생존_기술": 0.3, "정밀함": 0.3}},
                {"name": "트라이던트찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "hp_power": 95, "cast_time": 14, "crit_rate": 10,
                 "description": "[검투][창술] 삼지창으로 강력한 찌르기 공격",
                 "damage_type": DamageType.PHYSICAL,
                 "organic_effects": {"전투_본능": 0.4, "무술_수행": 0.35, "정밀함": 0.25}},
                {"name": "결투자의명예", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 6, "description": "[검투][명예] HP가 낮을수록 공격력 증가",
                 "special_effects": ["gladiator_honor"],
                 "organic_effects": {"전투_본능": 0.4, "생존_기술": 0.35, "의지력": 0.25}},
                {"name": "콜로세움의왕", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 100, "cooldown": 7, "cast_time": 30,
                 "description": "[궁극][검투] 검투장을 지배하는 최강의 기술",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["colosseum_king"],
                 "organic_effects": {"전투_본능": 0.5, "생존_기술": 0.4, "무술_수행": 0.35, "지휘력": 0.3}}
            ],
            
            "광전사": [
                # 광기의 전사 - [광폭][희생] 키워드 특화
                {"name": "광기의씨앗", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 1, "description": "[광폭][자해] 자신에게 피해를 입혀 광폭화 준비",
                 "special_effects": ["rage_seed"],
                 "organic_effects": {"전투_본능": 0.4, "광기_제어": 0.35, "생존_기술": 0.25}},
                {"name": "무모한돌격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "hp_power": 90, "cast_time": 15, "accuracy": 75,
                 "description": "[광폭][돌격] 정확도 낮지만 강력한 HP 공격",
                 "damage_type": DamageType.PHYSICAL,
                 "organic_effects": {"전투_본능": 0.45, "광기_제어": 0.3, "무술_수행": 0.25}},
                {"name": "피의갈증", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "hp_power": 85, "drain_hp": True, "drain_rate": 0.3, "cast_time": 15,
                 "description": "[광폭][흡혈] 적을 공격하여 체력 30% 흡수",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["blood_thirst"],
                 "organic_effects": {"전투_본능": 0.4, "광기_제어": 0.3, "생존_기술": 0.3}},
                {"name": "광란의연타", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 45, "consecutive_attacks": 4, "cast_time": 20,
                 "description": "[광폭][연타] 광기의 4연속 공격",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["mad_combo"],
                 "organic_effects": {"전투_본능": 0.4, "광기_제어": 0.35, "무술_수행": 0.25}},
                {"name": "분노폭발", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "brv_power": 60, "hp_power": 50, "cast_time": 25,
                 "description": "[광폭][폭발] 모든 적에게 광기의 힘 방출",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["rage_explosion"],
                 "organic_effects": {"전투_본능": 0.4, "광기_제어": 0.35, "무술_수행": 0.25}},
                {"name": "버서커의최후", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 15, "hp_power": 110, "cooldown": 5, "cast_time": 10,
                 "description": "[궁극][희생] 현재 HP 25% 희생하여 치명적 광역 공격",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["berserker_end"],
                 "hp_sacrifice_rate": 0.25,
                 "organic_effects": {"전투_본능": 0.5, "광기_제어": 0.4, "생존_기술": 0.35, "의지력": 0.3}}
            ],
            
            # === 기사 계열 ===
            "기사": [
                # 명예로운 기사 - [기사도][방어] 키워드 특화
                {"name": "방패방어", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "[방어][기사도] 방어력 20% 증가 및 아군 보호 준비",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.2}],
                 "organic_effects": {"방어_술수": 0.4, "기사도_정신": 0.35, "전술_지식": 0.25}},
                {"name": "창돌격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 80, "accuracy": 90,
                 "description": "[기사도][창술] 기사의 기본 창술 공격",
                 "damage_type": DamageType.PHYSICAL,
                 "organic_effects": {"무술_수행": 0.4, "기사도_정신": 0.3, "전투_본능": 0.3}},
                {"name": "아군보호", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 4, "description": "[수호][기사도] 아군에게 보호막 부여",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"기사도_정신": 0.4, "지휘력": 0.3, "방어_술수": 0.3}},
                {"name": "기사도정신", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "cooldown": 3, "description": "[기사도][지휘] 아군 전체 방어력 15% 증가",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"기사도_정신": 0.45, "지휘력": 0.35, "방어_술수": 0.2}},
                {"name": "성스러운돌격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 95, "element": ElementType.LIGHT, "cast_time": 12,
                 "description": "[기사도][신성] 성스러운 힘의 돌격",
                 "damage_type": DamageType.PHYSICAL,
                 "organic_effects": {"기사도_정신": 0.4, "신성_마법": 0.3, "무술_수행": 0.3}},
                {"name": "수호기사의맹세", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 16, "cooldown": 6, "cast_time": 30,
                 "description": "[궁극][수호] 아군 전체를 완벽하게 보호하는 기사의 맹세",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 6, "intensity": 2.0}],
                 "special_effects": ["knight_oath"],
                 "organic_effects": {"기사도_정신": 0.5, "지휘력": 0.4, "방어_술수": 0.35, "신성_마법": 0.3}}
            ],
            
            "성기사": [
                # 신성한 수호자 - [신성][수호] 키워드 특화
                {"name": "신앙의힘", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[신성][수호] 신앙으로 마법력과 방어력 증가",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"신앙": 0.4, "성스러운_힘": 0.3, "수호_의지": 0.25}},
                {"name": "성스러운타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 75, "element": ElementType.LIGHT, "accuracy": 95,
                 "description": "[신성][타격] 성스러운 힘으로 공격. 언데드에게 특효",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["holy_strike"],
                 "organic_effects": {"성스러운_힘": 0.4, "신앙": 0.3, "전투_본능": 0.25}},
                {"name": "축복", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "description": "[신성][축복] 아군에게 축복 부여. 방어력 15% 증가",
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.BOOST_DEF, "duration": 5, "intensity": 1.15}],
                 "organic_effects": {"신앙": 0.4, "수호_의지": 0.35, "성스러운_힘": 0.25}},
                {"name": "치유의빛", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 80, "element": ElementType.LIGHT,
                 "description": "[신성][치유] 성스러운 빛으로 강력한 치유",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["holy_heal"],
                 "organic_effects": {"성스러운_힘": 0.4, "신앙": 0.35, "수호_의지": 0.3}},
                {"name": "부활", "type": SkillType.SPECIAL, "target": TargetType.DEAD_ALLY,
                 "mp_cost": 12, "cast_time": 30, "cooldown": 5, "element": ElementType.LIGHT,
                 "description": "[신성][기적] 죽은 아군을 50% HP로 부활시킴",
                 "special_effects": ["resurrect"],
                 "organic_effects": {"신앙": 0.5, "성스러운_힘": 0.4, "수호_의지": 0.35}},
                {"name": "천사의강림", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 90, "element": ElementType.LIGHT, "cooldown": 8, "cast_time": 35,
                 "description": "[궁극][신성] 천사의 힘으로 적 전체 심판",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["angel_descent"],
                 "organic_effects": {"성스러운_힘": 0.5, "신앙": 0.4, "수호_의지": 0.35, "전투_본능": 0.3}}
            ],
            
            "암흑기사": [
                # 어둠의 계약자 - [어둠][흡수] 키워드 특화
                {"name": "어둠의계약", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[어둠][계약] HP 10% 소모로 공격력 20% 증가",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["dark_pact"],
                 "organic_effects": {"어둠_지배": 0.4, "생명력_조작": 0.3, "전투_본능": 0.25}},
                {"name": "생명흡수", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 70, "element": ElementType.DARK, "accuracy": 95,
                 "description": "[흡수][어둠] 공격하며 피해의 30%만큼 HP 회복",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["life_steal"],
                 "organic_effects": {"생명력_조작": 0.4, "어둠_지배": 0.3, "전투_본능": 0.25}},
                {"name": "저주의검", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "element": ElementType.DARK, "description": "[어둠][저주] 적의 방어력 감소와 저주",
                 "status_effects": [{"type": StatusType.CURSE, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_DEF, "duration": 4, "intensity": 0.85}],
                 "organic_effects": {"어둠_지배": 0.4, "생명력_조작": 0.3, "마법_지식": 0.25}},
                {"name": "어둠의보호", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 6, "description": "[어둠][방어] 어둠의 힘으로 방어력 25% 증가",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.25}],
                 "organic_effects": {"어둠_지배": 0.35, "생명력_조작": 0.3, "전투_본능": 0.25}},
                {"name": "흡혈", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 85, "element": ElementType.DARK, "cast_time": 10,
                 "description": "[흡수][강력] 강력한 생명 흡수 공격. 피해의 50% 회복",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["vampire_strike"],
                 "organic_effects": {"생명력_조작": 0.4, "어둠_지배": 0.35, "전투_본능": 0.3}},
                {"name": "어둠의지배자", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 100, "element": ElementType.DARK, "cooldown": 7, "cast_time": 30,
                 "description": "[궁극][어둠] 어둠으로 모든 적을 지배하고 저주",
                 "damage_type": DamageType.HYBRID, "special_effects": ["dark_domination"],
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.CURSE, "duration": 6, "intensity": 1.5}],
                 "organic_effects": {"어둠_지배": 0.5, "생명력_조작": 0.4, "전투_본능": 0.35, "마법_지식": 0.3}}
            ],
            
            "용기사": [
                # 드래곤의 후예 - [용족][화염] 키워드 특화
                {"name": "용의비늘", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[용족][방어] 용의 비늘로 방어력 20% 증가",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"용족_혈통": 0.4, "화염_친화": 0.3, "전투_본능": 0.25}},
                {"name": "드래곤클로", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 80, "element": ElementType.FIRE, "accuracy": 95,
                 "description": "[용족][발톱] 용의 발톱으로 공격. 출혈 효과",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{"type": StatusType.BLEED, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.3, "화염_친화": 0.25}},
                {"name": "화염숨결", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "brv_power": 60, "element": ElementType.FIRE, "accuracy": 90,
                 "description": "[화염][브레스] 용의 화염 브레스로 적 전체 공격",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BURN, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"화염_친화": 0.4, "용족_혈통": 0.35, "마법_지식": 0.25}},
                {"name": "용의위엄", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "description": "[용족][위압] 용의 위엄으로 모든 적 위축",
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_DEF, "duration": 4, "intensity": 0.85}],
                 "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.3, "마법_지식": 0.25}},
                {"name": "드래곤스피어", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 100, "element": ElementType.FIRE, "cast_time": 18,
                 "description": "[용족][창술] 용의 힘이 깃든 강력한 창 공격",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["dragon_spear"],
                 "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.35, "화염_친화": 0.3}},
                {"name": "드래곤로드", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "hp_power": 110, "element": ElementType.FIRE, "cooldown": 8, "cast_time": 40,
                 "description": "[궁극][용족] 진정한 용의 힘 해방. 적 전체 화염 심판",
                 "damage_type": DamageType.HYBRID, "special_effects": ["dragon_lord"],
                 "status_effects": [{"type": StatusType.BURN, "duration": 5, "intensity": 1.5},
                                   {"type": StatusType.TERROR, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"용족_혈통": 0.6, "화염_친화": 0.5, "전투_본능": 0.4, "마법_지식": 0.35}}
            ],
            
            # === 진화하는 현자 - 아크메이지 ===
            "아크메이지": [
                # 원소의 연구자 - [진화][연구] 키워드 특화
                {"name": "마력파동", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 85, "accuracy": 100,
                 "description": "[진화][연구] 순수 마력 방출. 사용할수록 위력 증가",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.NEUTRAL,
                 "special_effects": ["mana_recovery_10pct"],
                 "organic_effects": {"마나_순환": 0.35, "연구_정신": 0.3, "마법_친화": 0.25}},
                {"name": "원소융합", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 90, "accuracy": 95,
                 "description": "[연구][융합] 3가지 원소를 융합한 마법. 랜덤 속성 부여",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["random_element"],
                 "organic_effects": {"연구_정신": 0.4, "마법_친화": 0.3, "집중력": 0.2}},
                {"name": "마나실드", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "description": "[진화][방어] 마법 피해 흡수 보호막. MP로 피해 흡수",
                 "status_effects": [{"type": StatusType.MANA_SHIELD, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"마나_순환": 0.4, "집중력": 0.3, "마법_친화": 0.25}},
                {"name": "마법폭발", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 75, "cast_time": 20, "accuracy": 90,
                 "description": "[융합][폭발] 마력을 폭발시켜 적 전체 공격. 화상 부여",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.FIRE,
                 "status_effects": [{"type": StatusType.BURN, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"마법_친화": 0.35, "연구_정신": 0.3, "집중력": 0.25}},
                {"name": "시공술", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "description": "[진화][조작] 시간과 공간을 조작하여 적 행동 지연",
                 "status_effects": [{"type": StatusType.SLOW, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"연구_정신": 0.4, "집중력": 0.35, "마나_순환": 0.2}},
                {"name": "아르카나", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "hp_power": 105, "cast_time": 30, "cooldown": 7,
                 "description": "[궁극][아르카나] 모든 원소의 힘을 담은 궁극 마법",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["all_elements"],
                 "organic_effects": {"마법_친화": 0.5, "연구_정신": 0.4, "마나_순환": 0.35, "집중력": 0.3}}
            ],

            "정령술사": [
                # 정령의 친구 - [정령][소환] 키워드 특화
                {"name": "정령교감", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "[정령][교감] 정령의 힘으로 마법공격력 15% 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "자연_이해": 0.3}},
                {"name": "화염정령", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 70, "element": ElementType.FIRE, "accuracy": 95,
                 "description": "[정령][화염] 화염 정령 소환하여 공격",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BURN, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "화염_친화": 0.3, "마법_지식": 0.3}},
                {"name": "물정령치유", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 75, "element": ElementType.WATER,
                 "description": "[정령][치유] 물 정령의 순수한 치유력",
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "치유_기술": 0.3}},
                {"name": "바람정령축복", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "description": "[정령][바람] 바람 정령의 축복. 속도 20% 증가",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.2}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "대지정령분노", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "hp_power": 85, "element": ElementType.EARTH, "cast_time": 20,
                 "description": "[정령][대지] 대지 정령의 분노. 적 전체 공격",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["earth_rage"],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.35, "자연_이해": 0.3}},
                {"name": "사대정령소환", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 20, "hp_power": 100, "cooldown": 8, "cast_time": 40,
                 "description": "[궁극][정령] 모든 정령의 힘을 빌려 궁극의 마법",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["four_elements"],
                 "organic_effects": {"정령_친화": 0.5, "마법_지식": 0.4, "자연_이해": 0.35, "집중력": 0.3}}
            ],
            
            "시간술사": [
                # 시간의 조작자 - [시간][조작] 키워드 특화
                {"name": "시간가속", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "description": "[시간][가속] 자신의 시간을 가속하여 속도 25% 증가",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.25}],
                 "organic_effects": {"시간_조작": 0.4, "마법_지식": 0.3, "집중력": 0.3}},
                {"name": "시간왜곡", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "description": "[시간][디버프] 적의 시간을 왜곡하여 행동 방해",
                 "status_effects": [{"type": StatusType.SLOW, "duration": 3, "intensity": 0.7}],
                 "organic_effects": {"시간_조작": 0.4, "마법_지식": 0.35, "정밀함": 0.25}},
                {"name": "시간되돌리기", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 8, "heal_power": 90, "description": "[시간][치유] 시간을 되돌려 상처 복구",
                 "special_effects": ["time_heal"],
                 "organic_effects": {"시간_조작": 0.4, "마법_지식": 0.3, "치유_기술": 0.3}},
                {"name": "미래예지", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 9, "cooldown": 4, "description": "[시간][예지] 미래를 보아 회피율 증가",
                 "status_effects": [{"type": StatusType.FORESIGHT, "duration": 5, "intensity": 1.0}],
                 "special_effects": ["future_sight"],
                 "organic_effects": {"시간_조작": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "시간정지", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "cooldown": 5, "cast_time": 25, "description": "[시간][정지] 시간을 멈춰 적들 행동 봉쇄",
                 "status_effects": [{"type": StatusType.TIME_STOP, "duration": 1, "intensity": 1.0}],
                 "special_effects": ["time_stop"], "is_field_skill": True,
                 "organic_effects": {"시간_조작": 0.45, "마법_지식": 0.35, "집중력": 0.2}},
                {"name": "시공간붕괴", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "hp_power": 110, "cooldown": 9, "cast_time": 45,
                 "description": "[궁극][시간] 시공간을 붕괴시켜 절대적 파괴",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["spacetime_collapse"],
                 "organic_effects": {"시간_조작": 0.5, "마법_지식": 0.4, "집중력": 0.35, "정밀함": 0.3}}
            ],
            
            "차원술사": [
                # 차원의 조작자 - [차원][공간] 키워드 특화
                {"name": "차원균열", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 75, "accuracy": 95,
                 "description": "[차원][균열] 공간을 찢어 적 공격",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["dimension_rift"],
                 "organic_effects": {"차원_조작": 0.4, "마법_지식": 0.35, "정밀함": 0.25}},
                {"name": "순간이동", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 6, "description": "[차원][이동] 차원을 넘나들어 속도와 회피율 증가",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 3, "intensity": 1.25},
                                   {"type": StatusType.EVASION_UP, "duration": 3, "intensity": 1.2}],
                 "organic_effects": {"차원_조작": 0.45, "마법_지식": 0.3, "집중력": 0.25}},
                {"name": "공간왜곡", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "description": "[차원][왜곡] 공간을 비틀어 적들 혼란",
                 "status_effects": [{"type": StatusType.CONFUSION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"차원_조작": 0.4, "마법_지식": 0.35, "정밀함": 0.25}},
                {"name": "차원방패", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 10, "cooldown": 3, "description": "[차원][방어] 다차원 마법방어막",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"차원_조작": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "공간절단", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 14, "hp_power": 110, "cast_time": 20,
                 "description": "[차원][절단] 공간 자체를 베어내는 강력한 공격",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["space_cut"],
                 "organic_effects": {"차원_조작": 0.5, "마법_지식": 0.35, "정밀함": 0.15}},
                {"name": "차원폭풍", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 24, "hp_power": 115, "cooldown": 8, "cast_time": 40,
                 "description": "[궁극][차원] 다차원의 폭풍으로 모든 적 파괴",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["dimension_storm"],
                 "organic_effects": {"차원_조작": 0.5, "마법_지식": 0.4, "집중력": 0.35, "정밀함": 0.3}}
            ],
            
            "철학자": [
                # 진리의 탐구자 - [지혜][분석] 키워드 특화
                {"name": "진리탐구", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "[지혜][탐구] 깊은 사색으로 마법공격력 15% 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 6, "intensity": 1.15}],
                 "organic_effects": {"지혜": 0.4, "마법_지식": 0.3, "집중력": 0.3}},
                {"name": "진실간파", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "description": "[분석][지혜] 적의 약점을 간파하여 취약 상태 부여",
                 "status_effects": [{"type": StatusType.VULNERABLE, "duration": 4, "intensity": 1.3}],
                 "special_effects": ["truth_insight"],
                 "organic_effects": {"지혜": 0.45, "마법_지식": 0.3, "정밀함": 0.25}},
                {"name": "지혜의빛", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "description": "[지혜][지휘] 지혜로 아군 전체 마법공격력 10% 향상",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1}],
                 "organic_effects": {"지혜": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "존재부정", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 12, "hp_power": 100, "cast_time": 20,
                 "description": "[지혜][부정] 철학적 논리로 적의 존재 자체를 부정",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["existence_denial"],
                 "organic_effects": {"지혜": 0.5, "마법_지식": 0.35, "집중력": 0.15}},
                {"name": "철학적사고", "type": SkillType.SPECIAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 10, "cooldown": 4, "description": "[지혜][해제] 깊은 사고로 모든 상태이상 해제",
                 "special_effects": ["philosophical_thought"],
                 "organic_effects": {"지혜": 0.45, "마법_지식": 0.3, "지휘력": 0.25}},
                {"name": "절대진리", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 25, "hp_power": 115, "cooldown": 9, "cast_time": 50,
                 "description": "[궁극][진리] 절대적 진리의 힘으로 모든 적 압도",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["absolute_truth"],
                 "organic_effects": {"지혜": 0.5, "마법_지식": 0.4, "집중력": 0.35, "정밀함": 0.3}}
            ],
            
            # === 바람의 저격수 - 궁수 ===
            "궁수": [
                # 바람의 유격수 - [연사][기동] 키워드 특화
                {"name": "연사", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 70, "accuracy": 95, "hit_count": 3,
                 "description": "[연사][기동] 3발 연속 사격. 각 발마다 명중률 증가",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.WIND,
                 "special_effects": ["triple_shot"],
                 "organic_effects": {"유격_전술": 0.35, "바람_친화": 0.3, "정밀_사격": 0.25}},
                {"name": "관통사격", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "hp_power": 70, "cast_time": 15, "accuracy": 90,
                 "description": "[기동][관통] 모든 적을 관통하는 강력한 화살. 적 수만큼 위력 증가",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["piercing_shot"],
                 "organic_effects": {"정밀_사격": 0.4, "유격_전술": 0.3, "집중력": 0.2}},
                {"name": "독화살", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 75, "accuracy": 95,
                 "description": "[연사][독성] 독을 바른 화살로 공격. 지속 독 피해",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "status_effects": [{"type": StatusType.POISON, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정밀_사격": 0.35, "생존_본능": 0.3, "유격_전술": 0.25}},
                {"name": "폭발화살", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 80, "cast_time": 20, "accuracy": 85,
                 "description": "[기동][폭발] 폭발하는 화살로 광역 공격. 화상 효과",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.FIRE,
                 "status_effects": [{"type": StatusType.BURN, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"유격_전술": 0.35, "정밀_사격": 0.3, "바람_친화": 0.25}},
                {"name": "바람보조", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 6, "description": "[기동][바람] 바람의 힘으로 회피율과 이동속도 증가",
                 "status_effects": [{"type": StatusType.BOOST_DODGE, "duration": 5, "intensity": 1.3},
                                   {"type": StatusType.BOOST_SPD, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"바람_친화": 0.4, "유격_전술": 0.35, "생존_본능": 0.2}},
                {"name": "헌터모드", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 16, "cooldown": 6, "description": "[궁극][사냥] 궁극의 사냥꾼 모드. 치명타율 100% + 연사 강화",
                 "special_effects": ["hunter_mode"],
                 "organic_effects": {"정밀_사격": 0.5, "유격_전술": 0.4, "바람_친화": 0.35, "생존_본능": 0.3}}
            ],

            
            "암살자": [
                # 그림자의 암살자 - [은신][암살] 키워드 특화
                {"name": "그림자숨기", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "[은신][그림자] 은신하여 다음 공격 치명타 확정",
                 "status_effects": [{"type": StatusType.STEALTH, "duration": 2, "intensity": 1.0},
                                   {"type": StatusType.BOOST_CRIT, "duration": 2, "intensity": 2.0}],
                 "organic_effects": {"은신_술법": 0.4, "정밀함": 0.3, "생존_본능": 0.3}},
                {"name": "기습", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 85, "crit_rate": 25, "accuracy": 95,
                 "description": "[암살][기습] 은신 상태에서 강력한 기습 공격",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["stealth_attack"],
                 "organic_effects": {"은신_술법": 0.4, "암살_기술": 0.35, "정밀함": 0.25}},
                {"name": "독바르기", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[독성][강화] 무기에 독을 발라 공격력 10% 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1}],
                 "special_effects": ["poison_weapon"],
                 "organic_effects": {"독술_지식": 0.4, "암살_기술": 0.3, "정밀함": 0.3}},
                {"name": "연막탄", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "cooldown": 3, "description": "[은신][방해] 연막으로 적들 실명",
                 "status_effects": [{"type": StatusType.BLIND, "duration": 3, "intensity": 1.0}],
                 "is_field_skill": True, "special_effects": ["smoke_bomb"],
                 "organic_effects": {"은신_술법": 0.4, "전술_지식": 0.3, "생존_본능": 0.3}},
                {"name": "암살술", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 120, "cast_time": 12, "crit_rate": 30,
                 "description": "[암살][치명] 치명적인 급소 공격. 높은 치명타율",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["assassination"],
                 "organic_effects": {"암살_기술": 0.5, "정밀함": 0.3, "은신_술법": 0.2}},
                {"name": "그림자분신", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 15, "hp_power": 95, "cooldown": 7, "cast_time": 8,
                 "description": "[궁극][분신] 그림자 분신이 모든 적을 동시 암살",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["shadow_clone"],
                 "organic_effects": {"은신_술법": 0.5, "암살_기술": 0.4, "정밀함": 0.35, "생존_본능": 0.3}}
            ],
            
            # === 독술의 암살자 - 도적 ===
            "도적": [
                # 독술의 암살자 - [독성][정밀] 키워드 특화  
                {"name": "독침", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 75, "accuracy": 95,
                 "description": "[독성][정밀] 독을 바른 침으로 정확한 급소 공격. 독 누적과 마비",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "status_effects": [{"type": StatusType.POISON, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.PARALYZE, "duration": 1, "intensity": 0.3}],
                 "organic_effects": {"독_숙련": 0.4, "정밀_조준": 0.3, "은신_술": 0.25}},
                {"name": "암살", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "hp_power": 110, "cast_time": 15, "accuracy": 90,
                 "description": "[정밀][은신] 은신에서 나타나 치명적 일격. 크리티컬 보장",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["stealth_attack"],
                 "status_effects": [{"type": StatusType.STUN, "duration": 1, "intensity": 1.0}],
                 "organic_effects": {"은신_술": 0.4, "정밀_조준": 0.35, "독_숙련": 0.2}},
                {"name": "연막탄", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "description": "[은신][혼란] 독성 연기로 적 전체 실명. 자신은 회피율 증가",
                 "status_effects": [{"type": StatusType.BLIND, "duration": 3, "intensity": 0.7}],
                 "special_effects": ["smoke_screen"],
                 "organic_effects": {"은신_술": 0.35, "빠른손놀림": 0.3, "독_숙련": 0.25}},
                {"name": "독무", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "cast_time": 20, "cooldown": 4,
                 "description": "[독성][광역] 전장에 독 안개 생성. 적 전체 지속 독 피해",
                 "is_field_skill": True, "special_effects": ["poison_fog"],
                 "status_effects": [{"type": StatusType.POISON, "duration": 5, "intensity": 1.5}],
                 "organic_effects": {"독_숙련": 0.5, "은신_술": 0.3, "빠른손놀림": 0.25}},
                {"name": "독날투척", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 80, "accuracy": 90,
                 "description": "[독성][원거리] 독을 바른 투척용 단검. 원거리 독 공격",
                 "damage_type": DamageType.RANGED, "element": ElementType.POISON,
                 "special_effects": ["poison_blade"],
                 "organic_effects": {"독_숙련": 0.35, "정밀_조준": 0.3, "빠른손놀림": 0.25}},
                {"name": "독왕의비의", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 18, "hp_power": 140, "cast_time": 25, "cooldown": 7,
                 "description": "[궁극][독성] 독술의 궁극기. 맹독 + 즉사 확률",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "special_effects": ["poison_mastery"],
                 "organic_effects": {"독_숙련": 0.6, "은신_술": 0.4, "정밀_조준": 0.35, "빠른손놀림": 0.3}}
            ],
            
            "해적": [
                # 바다의 무법자 - [해적][자유] 키워드 특화
                {"name": "이도류", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "description": "[해적][무법] 두 개의 검으로 공격력과 치명타율 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15},
                                   {"type": StatusType.BOOST_CRIT, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"해적_정신": 0.4, "무술_수행": 0.3, "자유_의지": 0.3}},
                {"name": "칼부림", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 80, "crit_rate": 15, "accuracy": 90,
                 "description": "[해적][난도질] 양손 검으로 무자비한 난도질",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.LIGHTNING,
                 "status_effects": [{"type": StatusType.BLEED, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.4, "무술_수행": 0.35, "전투_본능": 0.25}},
                {"name": "바다의저주", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "element": ElementType.WATER, "description": "[해적][저주] 바다의 저주로 적 약화",
                 "status_effects": [{"type": StatusType.CURSE, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_SPD, "duration": 4, "intensity": 0.8}],
                 "organic_effects": {"해적_정신": 0.4, "마법_지식": 0.3, "자유_의지": 0.3}},
                {"name": "해적의함성", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 5, "cooldown": 3, "description": "[해적][지휘] 동료들 사기 진작. 공격력 10% 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 3, "intensity": 1.1},
                                   {"type": StatusType.INSPIRATION, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.4, "지휘력": 0.35, "자유_의지": 0.25}},
                {"name": "해상치료술", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 70, "description": "[해적][치유] 바다 정령의 치유력",
                 "element": ElementType.WATER, "is_field_skill": True,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.35, "마법_지식": 0.3, "치유_기술": 0.25}},
                {"name": "폭풍의함대", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 17, "hp_power": 95, "element": ElementType.WATER,
                 "cooldown": 6, "cast_time": 18, "description": "[궁극][해적] 유령 함대의 일제 사격",
                 "damage_type": DamageType.HYBRID, "special_effects": ["ghost_fleet"],
                 "status_effects": [{"type": StatusType.FEAR, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.5, "지휘력": 0.4, "마법_지식": 0.35, "자유_의지": 0.3}}
            ],
            
            "사무라이": [
                # 검의 구도자 - [무사도][정신] 키워드 특화
                {"name": "무사도", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[무사도][정신] 무사의 정신으로 공격력과 집중력 향상",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.FOCUS, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "검술_대가": 0.3, "집중력": 0.3}},
                {"name": "거합베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 90, "accuracy": 98, "crit_rate": 20,
                 "description": "[무사도][발도] 일순간의 발도술. 높은 명중률과 치명타율",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.LIGHTNING,
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"검술_대가": 0.45, "무사도_정신": 0.3, "집중력": 0.25}},
                {"name": "명상", "type": SkillType.HEAL, "target": TargetType.SELF,
                 "mp_cost": 4, "heal_power": 65, "description": "[정신][치유] 정신 집중으로 HP 회복",
                 "element": ElementType.NEUTRAL,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "집중력": 0.35, "치유_기술": 0.25}},
                {"name": "진검승부", "type": SkillType.COUNTER, "target": TargetType.SELF,
                 "mp_cost": 5, "cooldown": 2, "description": "[무사도][반격] 반격 태세. 공격받으면 강력한 반격",
                 "status_effects": [{"type": StatusType.COUNTER, "duration": 3, "intensity": 2.0},
                                   {"type": StatusType.BARRIER, "duration": 3, "intensity": 1.3}],
                 "organic_effects": {"무사도_정신": 0.4, "검술_대가": 0.3, "전투_본능": 0.3}},
                {"name": "사무라이치유법", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 70, "description": "[정신][치유] 무사의 정신력으로 전체 치유",
                 "element": ElementType.LIGHT, "is_field_skill": True,
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "치유_기술": 0.3, "지휘력": 0.3}},
                {"name": "오의무상베기", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 20, "hp_power": 115, "cooldown": 8, "cast_time": 35,
                 "description": "[궁극][무사도] 무사의 최고 오의. 적 전체를 베는 절대검술",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.NEUTRAL,
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 2, "intensity": 1.0}],
                 "special_effects": ["mushin_cut"],
                 "organic_effects": {"무사도_정신": 0.6, "검술_대가": 0.4, "집중력": 0.35, "전투_본능": 0.3}}
            ],
            
            # === 마법 지원 계열 ===
            "바드": [
                # 선율의 지휘자 - [음악][지원] 키워드 특화
                {"name": "용기의노래", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "description": "[음악][지원] 용기를 북돋는 노래. 아군 공격력 10% 증가",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1},
                                   {"type": StatusType.BOOST_CRIT, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"음악_재능": 0.4, "지휘력": 0.35, "마법_지식": 0.25}},
                {"name": "회복의선율", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "heal_power": 60, "description": "[음악][치유] 치유의 선율로 전체 회복",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"음악_재능": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "절망의노래", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "description": "[음악][디버프] 적들의 사기 저하. 공포 부여",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_ATK, "duration": 4, "intensity": 0.9}],
                 "organic_effects": {"음악_재능": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "신속의리듬", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "cooldown": 3, "description": "[음악][리듬] 아군 속도 20% 증가",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.2},
                                   {"type": StatusType.HASTE, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"음악_재능": 0.4, "지휘력": 0.35, "마법_지식": 0.25}},
                {"name": "천상의치유가", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 90, "description": "[음악][신성] 천상의 치유가로 전체 치유 및 상태이상 해제",
                 "element": ElementType.LIGHT, "is_field_skill": True,
                 "special_effects": ["divine_song"],
                 "organic_effects": {"음악_재능": 0.4, "치유_기술": 0.3, "신성_마법": 0.3}},
                {"name": "천상의합창", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 22, "cooldown": 9, "cast_time": 40, "heal_power": 120,
                 "description": "[궁극][음악] 천상의 합창으로 대규모 치유와 일시적 무적",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.INVINCIBLE, "duration": 1, "intensity": 1.0}],
                 "special_effects": ["heavenly_chorus"],
                 "organic_effects": {"음악_재능": 0.5, "지휘력": 0.4, "치유_기술": 0.35, "신성_마법": 0.3}}
            ],
            
            "무당": [
                # 영혼의 중재자 - [정령][영혼] 키워드 특화
                {"name": "정령소환", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "[정령][소환] 정령의 힘으로 마법공격력과 영적 보호 증가",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.SPIRIT_LINK, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "영혼_조작": 0.3, "마법_지식": 0.3}},
                {"name": "저주의인형", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "description": "[영혼][저주] 저주 인형으로 지속 피해 및 능력 봉인",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.CURSE, "duration": 6, "intensity": 1.0},
                                   {"type": StatusType.NECROSIS, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"영혼_조작": 0.4, "마법_지식": 0.3, "정령_친화": 0.3}},
                {"name": "치유의춤", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 65, "description": "[정령][치유] 무당의 춤으로 치유 및 정화",
                 "element": ElementType.EARTH,
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "영혼파악", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "description": "[영혼][분석] 적의 영혼을 파악하여 정보 획득 및 정신 공격",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.CONFUSION, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["soul_analysis"],
                 "organic_effects": {"영혼_조작": 0.45, "마법_지식": 0.3, "정령_친화": 0.25}},
                {"name": "정령치유술", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 80, "description": "[정령][치유] 정령들의 힘으로 강력한 전체 치유",
                 "element": ElementType.WATER, "is_field_skill": True,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "대자연의심판", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "hp_power": 100, "element": ElementType.EARTH,
                 "cooldown": 8, "cast_time": 25,
                 "description": "[궁극][정령] 자연의 모든 힘을 빌려 적들을 심판",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["nature_judgment"],
                 "status_effects": [{"type": StatusType.PETRIFY, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.5, "영혼_조작": 0.4, "마법_지식": 0.35, "자연_이해": 0.3}}
            ],
            
            "드루이드": [
                # 자연의 수호자 - [자연][변신] 키워드 특화
                {"name": "자연교감", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[자연][교감] 자연의 힘으로 마법공격력 12% 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.12}],
                 "organic_effects": {"자연_이해": 0.4, "마법_지식": 0.3, "정령_친화": 0.3}},
                {"name": "가시덩굴", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "element": ElementType.EARTH, "description": "[자연][속박] 가시로 적들 속박",
                 "status_effects": [{"type": StatusType.ENTANGLE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"자연_이해": 0.4, "마법_지식": 0.35, "전술_지식": 0.25}},
                {"name": "자연치유", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "heal_power": 70, "element": ElementType.EARTH,
                 "description": "[자연][치유] 자연의 생명력으로 전체 치유",
                 "organic_effects": {"자연_이해": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "동물변신", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 7, "cooldown": 3, "description": "[변신][강화] 야생동물로 변신하여 능력 증가",
                 "status_effects": [{"type": StatusType.BERSERK, "duration": 4, "intensity": 1.3}],
                 "special_effects": ["animal_form"],
                 "organic_effects": {"자연_이해": 0.45, "변신_능력": 0.35, "전투_본능": 0.2}},
                {"name": "번개폭풍", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 90, "element": ElementType.LIGHTNING, "cast_time": 18,
                 "description": "[자연][폭풍] 자연의 번개를 소환하여 적 전체 공격",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["lightning_storm"],
                 "organic_effects": {"자연_이해": 0.4, "마법_지식": 0.35, "정령_친화": 0.25}},
                {"name": "가이아의분노", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 24, "hp_power": 110, "element": ElementType.EARTH,
                 "cooldown": 8, "cast_time": 35, "description": "[궁극][자연] 대지의 여신이 직접 내리는 심판",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["gaia_wrath"],
                 "organic_effects": {"자연_이해": 0.5, "마법_지식": 0.4, "정령_친화": 0.35, "변신_능력": 0.3}}
            ],
            
            "신관": [
                # 신의 대행자 - [신성][치유] 키워드 특화
                {"name": "신의가호", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 5, "description": "[신성][보호] 모든 아군에게 신의 보호막",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"신앙": 0.4, "신성_마법": 0.35, "지휘력": 0.25}},
                {"name": "성스러운빛", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 75, "element": ElementType.LIGHT, "accuracy": 95,
                 "description": "[신성][공격] 언데드에게 특효. 성스러운 빛으로 공격",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["holy_light"],
                 "organic_effects": {"신성_마법": 0.4, "신앙": 0.3, "마법_지식": 0.3}},
                {"name": "대치유술", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 7, "heal_power": 110, "element": ElementType.LIGHT,
                 "description": "[치유][신성] 강력한 신성 치유로 대량 회복",
                 "special_effects": ["greater_heal"],
                 "organic_effects": {"치유_기술": 0.4, "신성_마법": 0.35, "신앙": 0.25}},
                {"name": "부활술", "type": SkillType.SPECIAL, "target": TargetType.DEAD_ALLY,
                 "mp_cost": 12, "cooldown": 4, "cast_time": 18, "element": ElementType.LIGHT,
                 "description": "[기적][신성] 신의 기적으로 죽은 아군을 60% HP로 부활",
                 "special_effects": ["resurrect"],
                 "organic_effects": {"신앙": 0.5, "신성_마법": 0.4, "치유_기술": 0.1}},
                {"name": "신벌", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "hp_power": 115, "element": ElementType.LIGHT, "cast_time": 12,
                 "description": "[신성][심판] 신의 벌로 사악한 적 처벌",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["divine_punishment"],
                 "organic_effects": {"신성_마법": 0.45, "신앙": 0.35, "마법_지식": 0.2}},
                {"name": "천국의문", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 25, "cooldown": 8, "cast_time": 40, "heal_power": 200,
                 "description": "[궁극][기적] 천국의 힘으로 모든 것을 완전 회복",
                 "element": ElementType.LIGHT, "special_effects": ["heaven_gate"],
                 "organic_effects": {"신앙": 0.6, "신성_마법": 0.5, "치유_기술": 0.4, "지휘력": 0.3}}
            ],
            
            "성직자": [
                # 평화의 사도 - [성직][평화] 키워드 특화
                {"name": "평화의기도", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "description": "[성직][평화] 아군들의 마음을 안정시켜 능력 향상",
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.GUARDIAN, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"신앙": 0.4, "평화_사상": 0.35, "지휘력": 0.25}},
                {"name": "정화의빛", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "element": ElementType.LIGHT, "description": "[성직][정화] 모든 디버프 제거",
                 "special_effects": ["purify_light"],
                 "organic_effects": {"신성_마법": 0.4, "평화_사상": 0.3, "치유_기술": 0.3}},
                {"name": "신성한치유", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 70, "element": ElementType.LIGHT,
                 "description": "[치유][성직] 신성한 힘으로 전체 치유",
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"치유_기술": 0.4, "신성_마법": 0.35, "평화_사상": 0.25}},
                {"name": "침묵의서약", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "description": "[성직][침묵] 적들을 침묵시켜 마법 봉쇄",
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"신성_마법": 0.4, "평화_사상": 0.3, "신앙": 0.3}},
                {"name": "순교자의길", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 9, "cooldown": 4, "description": "[성직][희생] 자신의 HP 25% 소모해 아군 완전 치유",
                 "special_effects": ["martyrdom_path"],
                 "organic_effects": {"평화_사상": 0.5, "치유_기술": 0.35, "신앙": 0.15}},
                {"name": "신의심판", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 22, "hp_power": 105, "element": ElementType.LIGHT, "cooldown": 7, "cast_time": 18,
                 "description": "[궁극][성직] 적을 심판하고 동시에 아군 전체 회복",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["divine_judgment"],
                 "organic_effects": {"신성_마법": 0.5, "신앙": 0.4, "치유_기술": 0.35, "평화_사상": 0.3}}
            ],
            
            # === 특수 계열 ===
            "몽크": [
                # 기의 수행자 - [기][수련] 키워드 특화
                {"name": "기수련", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[기][수련] 내면의 기를 단련하여 공격력과 집중력 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.FOCUS, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정신_수양": 0.4, "기_수련": 0.35, "무술_숙련": 0.25}},
                {"name": "연속주먹", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 65, "accuracy": 95, "hit_count": 2,
                 "description": "[기][연속] 기의 흐름에 따른 2회 연속 공격",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["combo_attack"],
                 "organic_effects": {"무술_숙련": 0.4, "기_수련": 0.3, "전투_본능": 0.25}},
                {"name": "명상", "type": SkillType.HEAL, "target": TargetType.SELF,
                 "mp_cost": 4, "heal_power": 75, "description": "[수련][회복] 명상으로 HP와 MP 동시 회복",
                 "special_effects": ["mp_restore_15pct"],
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"정신_수양": 0.5, "기_수련": 0.3, "내면_평화": 0.25}},
                {"name": "기폭발", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "hp_power": 60, "cast_time": 15, "accuracy": 90,
                 "description": "[기][폭발] 내재된 기를 폭발시켜 적 전체 공격",
                 "damage_type": DamageType.HYBRID, "special_effects": ["ki_explosion"],
                 "organic_effects": {"기_수련": 0.4, "무술_숙련": 0.3, "정신_수양": 0.25}},
                {"name": "철의주먹", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 95, "cast_time": 10, "accuracy": 95,
                 "description": "[수련][강철] 강철같이 단련된 주먹으로 강력한 일격",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["armor_pierce"],
                 "organic_effects": {"무술_숙련": 0.4, "기_수련": 0.35, "전투_본능": 0.3}},
                {"name": "깨달음의경지", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 16, "cooldown": 6, "cast_time": 20,
                 "description": "[궁극][깨달음] 완전한 깨달음으로 모든 능력 초월",
                 "special_effects": ["enlightenment"],
                 "organic_effects": {"정신_수양": 0.6, "기_수련": 0.5, "무술_숙련": 0.4, "내면_평화": 0.35}}
            ],
            
            "마검사": [
                # 마검의 융합자 - [융합][마검] 키워드 특화
                {"name": "마검각성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "description": "[융합][각성] 물리력과 마법력 동시 증가",
                 "damage_type": DamageType.HYBRID,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2}],
                 "organic_effects": {"마검_숙련": 0.4, "마법_지식": 0.3, "전투_본능": 0.25}},
                {"name": "마법검격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 80, "element": ElementType.NEUTRAL, "accuracy": 95,
                 "description": "[마검][융합] 물리력과 마법력을 융합한 검격",
                 "damage_type": DamageType.HYBRID,
                 "organic_effects": {"마검_숙련": 0.4, "마법_지식": 0.3, "전투_본능": 0.25}},
                {"name": "원소부여", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "description": "[마검][원소] 검에 원소 마법 부여. 다음 공격에 원소 효과",
                 "damage_type": DamageType.HYBRID, "special_effects": ["elemental_weapon"],
                 "organic_effects": {"마법_지식": 0.4, "마검_숙련": 0.3, "원소_친화": 0.25}},
                {"name": "마검진", "type": SkillType.FIELD, "target": TargetType.BATTLEFIELD,
                 "mp_cost": 8, "cooldown": 3, "description": "[융합][필드] 마법진 생성. 적 전체 지속 피해",
                 "damage_type": DamageType.MAGICAL, "is_field_skill": True, "special_effects": ["magic_field"],
                 "organic_effects": {"마법_지식": 0.4, "마검_숙련": 0.3, "전략적_사고": 0.25}},
                {"name": "마력폭발", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 100, "cast_time": 15, "accuracy": 90,
                 "description": "[마검][폭발] 물리와 마법 에너지 동시 폭발",
                 "damage_type": DamageType.HYBRID,
                 "organic_effects": {"마검_숙련": 0.4, "마법_지식": 0.35, "전투_본능": 0.3}},
                {"name": "마검의진리", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 95, "cooldown": 7, "cast_time": 25,
                 "description": "[궁극][융합] 물리와 마법의 완벽한 융합 공격",
                 "damage_type": DamageType.HYBRID, "special_effects": ["perfect_fusion"],
                 "organic_effects": {"마검_숙련": 0.5, "마법_지식": 0.4, "전투_본능": 0.35, "원소_친화": 0.3}}
            ],
            
            "연금술사": [
                # 물질의 연성자 - [연성][변환] 키워드 특화
                {"name": "물질변환", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "description": "[연성][변환] 재료를 변환하여 임시 아이템 생성",
                 "special_effects": ["transmute_item"],
                 "organic_effects": {"연금_지식": 0.4, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "독성폭탄", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "brv_power": 60, "element": ElementType.POISON, "accuracy": 90,
                 "description": "[연성][독성] 연금술로 제조한 독성 폭탄 투척",
                 "damage_type": DamageType.MAGICAL, 
                 "status_effects": [{"type": StatusType.POISON, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"연금_지식": 0.35, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "회복포션", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "heal_power": 80, "description": "[연성][회복] 즉석에서 고급 포션 제조",
                 "special_effects": ["instant_potion"],
                 "organic_effects": {"연금_지식": 0.4, "창조_정신": 0.35, "생존_본능": 0.2}},
                {"name": "강화주사", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "description": "[변환][강화] 능력 강화 약물 제조. 20% 공격력 증가",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"연금_지식": 0.4, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "산성용해", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 90, "element": ElementType.POISON, "cast_time": 15,
                 "description": "[연성][부식] 강산으로 적의 방어력과 생명력 용해",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["acid_corrosion"],
                 "organic_effects": {"연금_지식": 0.4, "마법_지식": 0.3, "창조_정신": 0.25}},
                {"name": "철학자의돌", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 18, "cooldown": 8, "cast_time": 30,
                 "description": "[궁극][연성] 전설의 돌로 모든 것을 황금으로 변환",
                 "special_effects": ["philosophers_stone"],
                 "organic_effects": {"연금_지식": 0.6, "창조_정신": 0.5, "마법_지식": 0.4, "생존_본능": 0.3}}
            ],
            
            "기계공학자": [
                # 기계 전쟁의 건축가 - [포탑][설치] 키워드 특화
                {"name": "자동포탑설치", "type": SkillType.FIELD, "target": TargetType.BATTLEFIELD,
                 "mp_cost": 6, "cooldown": 3, "description": "[포탑][설치] 전장에 자동 공격 포탑 설치. 3턴간 매턴 적 전체 공격",
                 "is_field_skill": True, "special_effects": ["auto_turret_install"],
                 "organic_effects": {"제조_마스터": 0.3, "기계_숙련": 0.25, "전략적_사고": 0.2}},
                {"name": "레이저사격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 85, "element": ElementType.LIGHTNING, "accuracy": 95,
                 "description": "[포탑][정밀] 고에너지 레이저로 정확한 사격",
                 "damage_type": DamageType.RANGED, "special_effects": ["precision_laser"],
                 "organic_effects": {"기계_숙련": 0.4, "전략적_사고": 0.2, "전투_본능": 0.15}},
                {"name": "메카돔", "type": SkillType.SUPPORT, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "description": "[설치][방어] 아군 전체를 보호하는 기계식 방어막 전개",
                 "status_effects": [{"type": StatusType.SHIELD, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"제조_마스터": 0.35, "냉정함": 0.25, "전략적_사고": 0.3}},
                {"name": "멀티미사일", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 70, "cast_time": 20, "accuracy": 90,
                 "description": "[포탑][폭발] 여러 발의 유도 미사일 동시 발사",
                 "damage_type": DamageType.RANGED, "special_effects": ["multi_missile"],
                 "organic_effects": {"제조_마스터": 0.3, "기계_숙련": 0.35, "전투_본능": 0.25}},
                {"name": "수리드론", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 90, "description": "[설치][회복] 자동 수리 드론 투입으로 아군 치료",
                 "special_effects": ["repair_drone"],
                 "organic_effects": {"제조_마스터": 0.4, "냉정함": 0.3, "기계_숙련": 0.2}},
                {"name": "기가포탑", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "hp_power": 120, "cast_time": 30, "cooldown": 8, 
                 "description": "[포탑][궁극] 거대한 파괴 포탑 소환. 적 전체에 압도적 화력 집중",
                 "is_field_skill": True, "special_effects": ["giga_turret"],
                 "organic_effects": {"제조_마스터": 0.5, "기계_숙련": 0.4, "전략적_사고": 0.3, "전투_본능": 0.25}}
            ],
            
            "네크로맨서": [
                # 죽음의 지배자 - [언데드][흡수] 키워드 특화
                {"name": "언데드소환", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 5, "description": "[언데드][소환] 언데드 하수인 소환. 전투 중 자동 공격",
                 "special_effects": ["summon_undead"],
                 "organic_effects": {"죽음_지배": 0.4, "어둠_친화": 0.3, "마법_지식": 0.25}},
                {"name": "생명력흡수", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 70, "element": ElementType.DARK, "accuracy": 95,
                 "description": "[흡수][어둠] 적의 생명력을 빨아들여 자신을 회복",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["life_drain"],
                 "status_effects": [{"type": StatusType.NECROSIS, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"어둠_친화": 0.4, "죽음_지배": 0.3, "생존_본능": 0.2}},
                {"name": "공포주입", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "element": ElementType.DARK, "description": "[언데드][공포] 모든 적에게 공포와 광기",
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.MADNESS, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"죽음_지배": 0.35, "어둠_친화": 0.3, "마법_지식": 0.25}},
                {"name": "뼈감옥", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "description": "[언데드][속박] 뼈로 만든 감옥에 적을 가둠",
                 "status_effects": [{"type": StatusType.ROOT, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.PARALYZE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"죽음_지배": 0.4, "마법_지식": 0.3, "어둠_친화": 0.25}},
                {"name": "죽음의손길", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 95, "element": ElementType.DARK, "cast_time": 15,
                 "description": "[흡수][어둠] 죽음의 마법으로 직접 생명력 흡수",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["life_steal"],
                 "organic_effects": {"어둠_친화": 0.4, "죽음_지배": 0.35, "마법_지식": 0.3}},
                {"name": "언데드군단", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "hp_power": 110, "element": ElementType.DARK, "cooldown": 7, "cast_time": 30,
                 "description": "[궁극][언데드] 거대한 언데드 군단 소환. 적 전체 공격",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["summon_undead"],
                 "organic_effects": {"죽음_지배": 0.5, "어둠_친화": 0.4, "마법_지식": 0.35, "생존_본능": 0.3}}
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


# ========================================
# Special Effects 처리 함수들
# ========================================

def apply_special_effect(effect_name: str, caster, target=None, skill_data=None):
    """특수 효과 적용"""
    effects_map = {
        # 전사 효과
        "double_attack": lambda: _double_attack(caster, target, skill_data),
        "armor_pierce": lambda: _armor_pierce(caster, target, skill_data),
        "berserker_rage": lambda: _berserker_rage(caster, skill_data),
        
        # 아크메이지 효과
        "mana_recovery_10pct": lambda: _mana_recovery_percent(caster, 0.10),
        "random_element": lambda: _random_element_effect(caster, target, skill_data),
        "all_elements": lambda: _all_elements_effect(caster, target, skill_data),
        
        # 궁수 효과
        "triple_shot": lambda: _triple_shot(caster, target, skill_data),
        "piercing_shot": lambda: _piercing_shot(caster, target, skill_data),
        "hunter_mode": lambda: _hunter_mode(caster),
        
        # 도적 효과
        "poison_weapon": lambda: _poison_weapon(caster, target, skill_data),
        "stealth_attack": lambda: _stealth_attack(caster, target, skill_data),
        "smoke_screen": lambda: _smoke_screen(caster),
        "poison_fog": lambda: _poison_fog(caster, target),
        "poison_blade": lambda: _poison_blade(caster, target, skill_data),
        "poison_mastery": lambda: _poison_mastery(caster, target, skill_data),
        
        # 기계공학자 효과
        "auto_turret_install": lambda: _auto_turret_install(caster),
        "precision_laser": lambda: _precision_laser(caster, target, skill_data),
        "repair_drone": lambda: _repair_drone(caster, target),
        "multi_missile": lambda: _multi_missile(caster, target, skill_data),
        "giga_turret": lambda: _giga_turret(caster, target, skill_data),
        
        # 공통 효과
        "resurrect": lambda: _resurrect(caster, target),
        "life_steal": lambda: _life_steal(caster, target, skill_data),
        "dispel_all": lambda: _dispel_all(target),
        "analyze_enemy": lambda: _analyze_enemy(caster, target),
    }
    
    if effect_name in effects_map:
        return effects_map[effect_name]()
    else:
        print(f"알 수 없는 특수 효과: {effect_name}")
        return False

# ========================================
# 전사 Special Effects
# ========================================

def _double_attack(caster, target, skill_data):
    """연속 공격 효과"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ATK, duration=2, intensity=1.2)
    return True

def _armor_pierce(caster, target, skill_data):
    """방어력 관통 효과"""
    # 다음 공격이 방어력 50% 무시
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("armor_pierce", 1)
    return True

def _berserker_rage(caster, skill_data):
    """광전사 분노 효과"""
    if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
        hp_ratio = caster.current_hp / caster.max_hp
        rage_bonus = max(1.2, 2.0 - hp_ratio)  # HP 낮을수록 강함
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.RAGE, duration=3, intensity=rage_bonus)
    return True

# ========================================
# 아크메이지 Special Effects
# ========================================

def _mana_recovery_percent(caster, percent):
    """마나 회복 (퍼센트)"""
    if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
        recovery = int(caster.max_mp * percent)
        caster.current_mp = min(caster.max_mp, caster.current_mp + recovery)
    return True

def _random_element_effect(caster, target, skill_data):
    """랜덤 원소 속성 부여"""
    import random
    elements = [ElementType.FIRE, ElementType.ICE, ElementType.LIGHTNING, 
                ElementType.EARTH, ElementType.WIND, ElementType.WATER]
    random_element = random.choice(elements)
    
    # 스킬에 원소 속성 추가
    if skill_data:
        skill_data["element"] = random_element
    return True

def _all_elements_effect(caster, target, skill_data):
    """모든 원소 속성 동시 적용"""
    if hasattr(target, 'add_status'):
        # 각 원소별 상태이상 부여
        target.add_status(StatusType.BURN, duration=3, intensity=1.0)      # 화염
        target.add_status(StatusType.FREEZE, duration=2, intensity=1.0)    # 냉기
        target.add_status(StatusType.SHOCK, duration=3, intensity=1.0)     # 번개
    return True

# ========================================
# 궁수 Special Effects
# ========================================

def _triple_shot(caster, target, skill_data):
    """3연사 효과"""
    # 기본 피해의 60%씩 3번 공격
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("triple_shot", 1)
    return True

def _piercing_shot(caster, target, skill_data):
    """관통 사격 효과"""
    # 모든 적에게 피해
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("piercing_attack", 1)
    return True

def _hunter_mode(caster):
    """헌터 모드 활성화"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_CRIT, duration=5, intensity=2.0)
        caster.add_status(StatusType.BOOST_ACCURACY, duration=5, intensity=1.5)
    return True

# ========================================
# 도적 Special Effects
# ========================================

def _poison_weapon(caster, target, skill_data):
    """무기에 독 바르기"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.POISON, duration=5, intensity=1.0)
    return True

def _stealth_attack(caster, target, skill_data):
    """은신 공격"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.STEALTH, duration=2, intensity=1.0)
    return True

def _smoke_screen(caster):
    """연막탄 효과"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_DODGE, duration=4, intensity=1.5)
    return True

def _poison_fog(caster, target):
    """독무 효과"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.POISON, duration=5, intensity=2.0)
    return True

def _poison_blade(caster, target, skill_data):
    """독날 투척"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.POISON, duration=4, intensity=1.5)
        target.add_status(StatusType.REDUCE_DEF, duration=3, intensity=0.8)
    return True

def _poison_mastery(caster, target, skill_data):
    """독왕의 비의"""
    if hasattr(target, 'add_status'):
        # 강력한 독 + 즉사 확률
        target.add_status(StatusType.POISON, duration=10, intensity=3.0)
        target.add_status(StatusType.NECROSIS, duration=5, intensity=2.0)
    return True

# ========================================
# 기계공학자 Special Effects
# ========================================

def _auto_turret_install(caster):
    """자동 포탑 설치"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.AUTO_TURRET, duration=3, intensity=1.0)
    return True

def _precision_laser(caster, target, skill_data):
    """정밀 레이저"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("perfect_accuracy", 1)
    return True

def _repair_drone(caster, target):
    """수리 드론"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.REPAIR_DRONE, duration=3, intensity=1.0)
        target.add_status(StatusType.REGENERATION, duration=5, intensity=1.5)
    return True

def _multi_missile(caster, target, skill_data):
    """멀티 미사일"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("multi_hit", 3)  # 3발 동시 발사
    return True

def _giga_turret(caster, target, skill_data):
    """기가 포탑"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.AUTO_TURRET, duration=5, intensity=3.0)
    return True

# ========================================
# 공통 Special Effects
# ========================================

def _resurrect(caster, target):
    """부활술"""
    if hasattr(target, 'current_hp') and target.current_hp <= 0:
        target.current_hp = target.max_hp // 2
        return True
    return False

def _life_steal(caster, target, skill_data):
    """생명력 흡수"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.VAMPIRE, duration=3, intensity=1.0)
    return True

def _dispel_all(target):
    """모든 상태이상 해제"""
    if hasattr(target, 'clear_all_status'):
        target.clear_all_status()
    return True

def _analyze_enemy(caster, target):
    """적 분석"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.ANALYZE, duration=999, intensity=1.0)
    return True

# 전역 인스턴스
new_skill_system = NewSkillSystem()
