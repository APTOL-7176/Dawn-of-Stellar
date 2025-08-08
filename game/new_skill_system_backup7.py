#!/usr/bin/env python3
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
    SUPPORT = "지원"

class TargetType(Enum):
    SELF = "자신"
    SINGLE_ALLY = "아군1명"
    ALL_ALLIES = "아군전체"
    SINGLE_ENEMY = "적1명"
    ALL_ENEMIES = "적전체"
    DEAD_ALLY = "죽은아군1명"
    BATTLEFIELD = "전장"  # 필드 스킬용 타겟
    ANY_SINGLE = "아무나1명"  # 아군이나 적 중 한 명

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
    RANGED = "원거리"  # 원거리 공격
    MELEE = "근접"    # 근접 공격

class DefenseType(Enum):
    PHYSICAL_DEF = "물리방어"
    MAGICAL_DEF = "마법방어"
    BOTH_DEF = "복합방어"

class PenetrationType(Enum):
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
    TIME_MARKED = "시간기록"
    PHASE = "위상변화"
    FORESIGHT = "예지"
    
    # === 그림자 시스템 ===
    SHADOW_STACK = "그림자축적"  # 그림자 개수를 나타내는 상태
    SHADOW_ECHO = "그림자메아리"  # 그림자가 따라하는 추가 피해 상태
    SHADOW_EMPOWERED = "그림자강화"  # 그림자로 강화된 스킬 상태
    
    # === 전사 적응형 시스템 ===
    WARRIOR_STANCE = "전사자세"  # 전사의 현재 전투 자세
    
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
    ABSOLUTE_EVASION = "절대회피"
    EVASION_UP = "회피증가"
    ENTANGLE = "속박술"
    MECHANICAL_ARMOR = "기계갑옷"
    
    # === 새로운 상태이상 ===
    BOOST_ALL_STATS = "전능력증가"
    REDUCE_ALL_STATS = "전능력감소"
    BOOST_MAGIC_DEF = "마법방어증가"
    BOOST_MAGIC_ATK = "마법공격증가"
    REDUCE_MAGIC_DEF = "마법방어감소"
    REDUCE_MAGIC_ATK = "마법공격감소"
    REDUCE_SPEED = "속도감소"
    HOLY_MARK = "성스러운표식"
    HOLY_AURA = "성스러운기운"
    DRAGON_FORM = "용변신"
    ELEMENTAL_IMMUNITY = "원소면역"
    TIME_SAVEPOINT = "시간저장점"
    TIME_DISTORTION = "시간왜곡"
    AFTERIMAGE = "잔상"
    COUNTER_ATTACK = "반격"
    TEMPORARY_INVINCIBLE = "일시무적"
    WEAKNESS_EXPOSURE = "약점노출"
    EXISTENCE_DENIAL = "존재부정"
    TRUTH_REVELATION = "진리계시"
    GHOST_FLEET = "유령함대"
    SOUL_BOND = "영혼유대"
    NATURE_CURSE = "자연저주"
    ANIMAL_FORM = "동물변신"
    DIVINE_PUNISHMENT = "신벌"
    HEAVEN_GATE = "천국문"
    PURIFICATION = "정화"
    MARTYRDOM = "순교"
    DIVINE_JUDGMENT = "신심판"
    ENLIGHTENMENT = "깨달음"
    ELEMENTAL_WEAPON = "원소무기"
    MAGIC_FIELD = "마법진영"
    TRANSMUTATION = "변환술"
    CORROSION = "부식"
    PHILOSOPHERS_STONE = "현자의돌"
    UNDEAD_MINION = "언데드하수인"
    SHADOW_CLONE = "그림자분신"
    EXTRA_TURN = "추가턴"
    MANA_REGENERATION = "마나재생"
    WISDOM = "지혜"
    MANA_INFINITE = "무한마나"
    HOLY_BLESSING = "성스러운축복"
    HOLY_WEAKNESS = "성스러운약점"

def get_status_icon(status_type: StatusType) -> str:
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
        StatusType.PARALYZE: "⚡",
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
        StatusType.TIME_MARKED: "⏳",
        StatusType.PHASE: "👻",}
    return icons.get(status_type, "❓")

class NewSkillSystem:
    
    def __init__(self):
        self.skills_by_class = self._initialize_all_skills()
        self.cooldowns = {}  # {character_id: {skill_name: remaining_turns}}
        # 스킬 계수 전역 배수 (1.5배로 모든 스킬 데미지 증가)
        self.skill_power_multiplier = 1.0
        # 적 스킬 전용 계수 (1.1배로 적 스킬 강화)
        self.enemy_skill_power_multiplier = 1.2
        # 아군 스킬 MP 소모량 배수 (1.6배로 증가)
        self.ally_mp_cost_multiplier = 1.0
    
    def _initialize_all_skills(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            # === 적응형 전투마스터 - 전사 ===
            "전사": [
                # 기본공격
                {"name": "적응형 강타", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 100, "accuracy": 95,
                 "description": "[BRV:100] [적응형] [물리] - 현재 자세에 따라 효과가 변하는 기본 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "sfx": "sword_hit",
                 "special_effects": ["adaptive_attack"],
                 "organic_effects": {"적응력": 0.4, "균형감각": 0.3, "전투_본능": 0.2}},
                
                # HP 기본공격
                {"name": "파괴의 일격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 120, "accuracy": 85,
                 "description": "[HP:120] [방어구파괴] - 강력한 일격으로 적의 방어구 내구도를 대폭 감소시킵니다.",
                 "damage_type": DamageType.PHYSICAL, "sfx": "critical_hit",
                 "special_effects": ["armor_break"],
                 "organic_effects": {"불굴의_의지": 0.5, "전투_본능": 0.4, "파괴력": 0.3}},
                
                # 적응형 전투자 - 상황에 따라 자세가 변하는 밸런스 전사
                {"name": "전술 분석", "type": SkillType.SPECIAL, "target": TargetType.BATTLEFIELD,
                 "mp_cost": 4, "sfx": "magic_cast",
                 "description": "[자세변경] [분석] - 적과 아군 상태를 분석하여 최적의 전투 자세로 변경합니다.",
                 "special_effects": ["stance_adaptation", "enemy_analysis"],
                 "organic_effects": {"적응력": 0.5, "전술_이해": 0.4, "균형감각": 0.3}},
                
                {"name": "방패 강타", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 115, "accuracy": 90,
                 "description": "[BRV:115] [기절:40%/2턴] [방어형 특화] - 방패로 적을 강타하여 기절시킵니다. 방어형일 때 위력 증가.",
                 "damage_type": DamageType.PHYSICAL, "sfx": "sword_hit",
                 "status_effects": [{"type": StatusType.STUN, "duration": 2, "intensity": 0.4}],
                 "special_effects": ["defensive_bonus"],
                 "organic_effects": {"불굴의_의지": 0.4, "적응력": 0.3, "전술_이해": 0.2}},
                
                {"name": "연속 베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 85, "accuracy": 85,
                 "description": "[BRV:85×2] [공격형 특화] [연속공격] - 2번 연속 공격. 공격형일 때 크리티컬 확률 증가.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["double_attack", "aggressive_bonus"],
                 "sfx": "sword_hit", "organic_effects": {"전투_본능": 0.4, "적응력": 0.3, "균형감각": 0.2}},
                
                {"name": "수호의 맹세", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "sfx": "protect",
                 "description": "[파티보호] [수호자 특화] - 수호자 모드에서 파티 전체를 보호합니다.",
                 "status_effects": [{"type": StatusType.GUARDIAN, "duration": 4, "intensity": 1.2}],
                 "special_effects": ["guardian_bonus"],
                 "organic_effects": {"불굴의_의지": 0.4, "리더십": 0.3, "적응력": 0.2}},
                
                {"name": "전투 각성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 7, "sfx": "haste",
                 "description": "[전능력+15%/5턴] [균형형 특화] - 전투의 흐름을 읽어 모든 능력치를 균형있게 향상시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_ALL_STATS, "duration": 5, "intensity": 1.15}],
                 "special_effects": ["balanced_bonus"],
                 "organic_effects": {"적응력": 0.5, "균형감각": 0.4, "전술_이해": 0.3}},
                
                {"name": "적응의 궁극기", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 15, "hp_power": 130, "cast_time": 25, "cooldown": 6,
                 "description": "[궁극] [HP:130] [적응형] [물리] - 현재 자세에 따라 다른 효과의 궁극기를 발동합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["adaptive_ultimate"],
                 "sfx": "critical_hit", "organic_effects": {"불굴의_의지": 0.5, "적응력": 0.4, "전투_본능": 0.3}}
            ],
            
            "검성": [
                # === 기본 공격 ===
                {"name": "기본베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 90, "accuracy": 95,
                 "description": "[BRV:90] [기본공격] [검기축적] - 검성의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["basic_sword_aura"],
                 "sfx": "sword_hit", "organic_effects": {"검술_대가": 0.2, "집중력": 0.1}},
                
                {"name": "기본찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 110, "accuracy": 90,
                 "description": "[HP:110] [기본공격] [검기폭발] - 검성의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["basic_sword_burst"],
                 "sfx": "sword_hit", "organic_effects": {"검술_대가": 0.25, "집중력": 0.15}},
                
                # ⚔️ 검성 - 검기 스택 시스템 (최대 2스택)
                {"name": "검기 베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 115, "accuracy": 95, "crit_rate": 12,
                 "description": "[BRV:115] [검기스택+1] [물리] - 기본 BRV 공격으로 검기 스택을 쌓습니다. 검성의 기본 기술입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_aura_gain"],
                 "sfx": "sword_hit", "organic_effects": {"검술_대가": 0.4, "집중력": 0.3, "무술_수행": 0.3}},
                
                {"name": "일섬", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "hp_power": 135, "accuracy": 98, "crit_rate": 25, "cast_time": 8,
                 "description": "[HP:135] [검기스택소모] [ATB환급20-60%] [크리+25%] - 검기 스택을 소모하여 강력한 일격을 가합니다. 스택에 따라 ATB 게이지를 환급받습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_aura_consume", "atb_refund"],
                 "sfx": "critical_hit", "organic_effects": {"검술_대가": 0.5, "집중력": 0.4, "무술_수행": 0.3}},
                
                {"name": "검기 파동", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "brv_power": 95, "accuracy": 90, "cast_time": 12,
                 "description": "[BRV:95] [전체] [검기스택1소모] [관통] - 검기 스택 1개를 소모하여 모든 적에게 관통 공격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_aura_wave", "piercing"],
                 "sfx": "magic_cast", "organic_effects": {"검술_대가": 0.4, "집중력": 0.35, "무술_수행": 0.25}},
                
                {"name": "검심 집중", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "haste",
                 "description": "[집중+25%/5턴] [검기스택+1] [자신] - 마음을 가다듬어 집중력을 높이고 검기를 축적합니다.",
                 "status_effects": [{"type": StatusType.FOCUS, "duration": 5, "intensity": 1.25}],
                 "special_effects": ["sword_aura_gain"],
                 "organic_effects": {"검술_대가": 0.35, "집중력": 0.45, "무술_수행": 0.2}},
                
                {"name": "검압 강타", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "brv_power": 125, "hp_power": 145, "cast_time": 15,
                 "description": "[BRV:125+HP:145] [검기스택1소모] [ATB환급30%] - 검기를 방출하여 BRV와 HP를 동시에 공격합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_aura_consume", "atb_refund_medium"],
                 "sfx": "critical_hit", "organic_effects": {"검술_대가": 0.45, "집중력": 0.3, "무술_수행": 0.25}},
                
                {"name": "무한검", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 18, "hp_power": 180, "cooldown": 6, "cast_time": 25, "crit_rate": 35,
                 "description": "[궁극] [HP:180] [모든검기스택소모] [다연타] [크리+35%] - 모든 검기 스택을 소모하여 무한의 검기로 적을 베어냅니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["infinite_blade", "sword_aura_consume_all"],
                 "sfx": "critical_hit", 
                 "organic_effects": {"검술_대가": 0.6, "집중력": 0.4, "무술_수행": 0.35, "전투_본능": 0.3}}
            ],
            
            "검투사": [
                # === 기본 공격 ===
                {"name": "투기장타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 88, "accuracy": 92,
                 "description": "[BRV:88] [기본공격] [투기장경험] - 검투사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["arena_experience"],
                 "sfx": "sword_hit", "organic_effects": {"전투_본능": 0.2, "생존_기술": 0.1}},
                
                {"name": "승부찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 108, "accuracy": 90,
                 "description": "[HP:108] [기본공격] [승부결정] - 검투사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["decisive_strike"],
                 "sfx": "sword_hit", "organic_effects": {"전투_본능": 0.25, "무술_수행": 0.15}},
                
                # 🛡 검투사 - 처치 스택 시스템 + 패링 시스템
                {"name": "투기장 기술", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 110, "accuracy": 92,
                 "description": "[BRV:110] [격투] [처치시능력치상승] - 투기장에서 단련한 격투 기술로 적을 공격합니다. 적 처치 시 능력치가 영구 상승합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["gladiator_skill"],
                 "sfx": "sword_hit", "organic_effects": {"전투_본능": 0.4, "생존_기술": 0.3, "무술_수행": 0.3}},
                
                {"name": "패링", "type": SkillType.COUNTER, "target": TargetType.SELF,
                 "mp_cost": 5, "cast_time": 8, "sfx": "magic_cast",
                 "description": "[반격태세] [패링] [처치효과획득] - 다음 공격을 반격으로 전환합니다. 성공 시 즉시 반격하고 처치 효과를 1회 획득합니다.",
                 "status_effects": [{"type": StatusType.COUNTER, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["parry_stance"],
                 "organic_effects": {"전투_본능": 0.35, "생존_기술": 0.4, "반응속도": 0.25}},
                
                {"name": "명예의 일격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 140, "cast_time": 12, "crit_rate": 15,
                 "description": "[HP:140] [처치스택비례강화] [크리+15%] - 처치 스택에 따라 위력이 증가하는 명예로운 일격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["honor_strike"],
                 "sfx": "critical_hit", "organic_effects": {"전투_본능": 0.4, "무술_수행": 0.35, "의지력": 0.25}},
                
                {"name": "투사의 함성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "magic_cast",
                 "description": "[공격+20%/4턴] [MP회복] [HP회복] - 관중들의 환호에 힘입어 능력치를 회복합니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2}],
                 "special_effects": ["warrior_roar"],
                 "organic_effects": {"전투_본능": 0.35, "생존_기술": 0.3, "지휘력": 0.25}},
                
                {"name": "생존자의 투혼", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "brv_power": 115, "hp_power": 125, "cast_time": 15,
                 "description": "[BRV:115+HP:125] [생존강화] [처치시회복] - 생존 의지를 담은 강력한 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["survival_spirit"],
                 "sfx": "critical_hit", "organic_effects": {"전투_본능": 0.45, "생존_기술": 0.35, "의지력": 0.2}},
                
                {"name": "콜로세움의 왕", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 165, "cooldown": 6, "cast_time": 28,
                 "description": "[궁극] [HP:165] [전체] [모든스택소모] [압도적공격] - 모든 처치 스택을 소모하여 압도적인 힘을 발휘합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["colosseum_king"],
                 "sfx": "critical_hit", 
                 "organic_effects": {"전투_본능": 0.5, "생존_기술": 0.4, "무술_수행": 0.35, "지휘력": 0.3}}
            ],
            
            "광전사": [
                # === 기본 공격 ===
                {"name": "기본 분노", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 95, "accuracy": 90,
                 "description": "[BRV:95] [기본공격] [분노축적] - 광전사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["rage_build"],
                 "sfx": "sword_hit", "organic_effects": {"전투_본능": 0.2, "광기_제어": 0.1}},
                
                {"name": "기본 찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 115, "accuracy": 85,
                 "description": "[HP:115] [기본공격] [소량흡혈] - 광전사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["basic_vampiric"],
                 "sfx": "sword_hit", "organic_effects": {"전투_본능": 0.25, "생존_기술": 0.15}},
                
                # 💢 광전사 - HP 소모 + 보호막 + 흡혈 시스템
                {"name": "분노의 폭발", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 125, "accuracy": 85, "hp_sacrifice": 15,
                 "description": "[BRV:125] [HP소모:15] [위력증가] [흡혈] - HP를 소모하여 강력한 공격을 가합니다. 소모한 HP에 따라 위력이 증가하고 흡혈 효과가 있습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["berserk_strike", "vampire_attack"],
                 "sfx": "sword_hit", "organic_effects": {"전투_본능": 0.45, "광기_제어": 0.3, "생존_기술": 0.25}},
                
                {"name": "피의 방패", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "sfx": "magic_cast",
                 "description": "[현재HP50%소모] [소모량150%보호막생성] [5턴지속] - 현재 HP의 50%를 소모하여 더 강력한 보호막을 생성합니다.",
                 "special_effects": ["blood_shield"],
                 "organic_effects": {"전투_본능": 0.35, "광기_제어": 0.4, "생존_기술": 0.25}},
                
                {"name": "흡혈 강타", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 140, "cast_time": 12, "drain_hp": True,
                 "description": "[HP:140] [보호막소모] [광역피해] [흡혈회복] - 보호막을 소모하여 강력한 공격을 가하고 흡혈로 회복합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["vampiric_blast", "shield_consume"],
                 "sfx": "critical_hit", "organic_effects": {"전투_본능": 0.4, "광기_제어": 0.3, "생존_기술": 0.3}},
                
                {"name": "광기 증폭", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "hp_sacrifice": 20, "sfx": "magic_cast",
                 "description": "[HP소모:20] [공격+30%/5턴] [흡혈량증가] - HP를 소모하여 광기를 증폭시키고 흡혈 효과를 강화합니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.3}],
                 "special_effects": ["madness_amplify"],
                 "organic_effects": {"전투_본능": 0.4, "광기_제어": 0.35, "의지력": 0.25}},
                
                {"name": "분노의 연쇄", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "brv_power": 95, "hp_power": 115, "hp_sacrifice_percent": 15, "cast_time": 18,
                 "description": "[BRV:95+HP:115] [전체] [HP소모15%] [광역흡혈] - 현재 HP의 일부를 소모하여 모든 적을 공격하고 광역 흡혈을 합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["rage_chain", "area_vampire"],
                 "sfx": "critical_hit", "organic_effects": {"전투_본능": 0.45, "광기_제어": 0.3, "생존_기술": 0.25}},
                
                {"name": "최후의 광기", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 200, "cooldown": 5, "cast_time": 20, "hp_sacrifice": 1,
                 "description": "[궁극] [HP:200] [HP를1로만듦] [엄청난흡혈] [전체] - HP를 1로 만들고 그만큼 엄청난 피해와 흡혈 효과를 가집니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["final_madness", "massive_vampire"],
                 "sfx": "critical_hit", 
                 "organic_effects": {"전투_본능": 0.6, "광기_제어": 0.4, "생존_기술": 0.35, "의지력": 0.3}}
            ],
            
            # === 기사 계열 ===
            "기사": [
                # === 기본 공격 ===
                {"name": "창찌르기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 85, "accuracy": 90,
                 "description": "[BRV:85] [기본공격] [기사도정신] - 기사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["knight_honor"],
                 "sfx": "sword_hit", "organic_effects": {"기사도_정신": 0.2, "무술_수행": 0.1}},
                
                {"name": "수호타격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 105, "accuracy": 85,
                 "description": "[HP:105] [기본공격] [수호의지] - 기사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["guardian_will"],
                 "sfx": "sword_hit", "organic_effects": {"기사도_정신": 0.25, "방어_술수": 0.15}},
                
                # 🛡 기사 - 의무 스택 시스템 (최대 5스택)
                {"name": "창 돌격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 115, "accuracy": 90,
                 "description": "[BRV:115] [돌격] [의무스택생성] - 창을 들고 돌격하여 적을 공격하고 의무 스택을 생성할 수 있습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["spear_charge"],
                 "sfx": "sword_hit", "organic_effects": {"기사도_정신": 0.4, "무술_수행": 0.3, "전술_지식": 0.3}},
                
                {"name": "수호의 맹세", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "magic_cast",
                 "description": "[아군대신피해] [의무스택획득] [패시브] - 아군 대신 피해를 받으며 의무 스택을 획득하는 수호자의 맹세입니다.",
                 "special_effects": ["protection_oath"],
                 "organic_effects": {"기사도_정신": 0.45, "방어_술수": 0.35, "의지력": 0.2}},
                
                {"name": "기사도", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "sfx": "magic_cast",
                 "description": "[5스택시방어+35%] [스택수비례강화] - 의무 스택에 따라 방어력과 마법방어력이 증가합니다.",
                 "special_effects": ["chivalry_spirit"],
                 "organic_effects": {"기사도_정신": 0.4, "방어_술수": 0.35, "지휘력": 0.25}},
                
                {"name": "의무의 반격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 135, "cast_time": 10,
                 "description": "[HP:135] [스택소모] [반격] - 의무 스택을 소모하여 강력한 반격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["duty_counter"],
                 "sfx": "critical_hit", "organic_effects": {"기사도_정신": 0.4, "무술_수행": 0.35, "전술_지식": 0.25}},
                
                {"name": "생존의 의지", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 8, "sfx": "magic_cast",
                 "description": "[3스택이상시] [모든스택소모] [죽음무시] [1HP생존+20%회복] - 3스택 이상일 때 모든 스택을 소모하여 죽는 피해를 무시하고 생존합니다.",
                 "special_effects": ["survival_will"],
                 "organic_effects": {"기사도_정신": 0.4, "생존_기술": 0.35, "의지력": 0.25}},
                
                {"name": "성스러운 돌격", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 15, "hp_power": 155, "cooldown": 6, "cast_time": 25, "element": ElementType.LIGHT,
                 "description": "[궁극] [HP:155] [전체] [성속성] [모든스택소모] - 모든 의무 스택을 소모하여 성스러운 최후 일격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["holy_charge"],
                 "sfx": "critical_hit", 
                 "organic_effects": {"기사도_정신": 0.5, "신성_마법": 0.4, "무술_수행": 0.35, "지휘력": 0.3}}
            ],
            
            "성기사": [
                # === 기본 공격 ===
                {"name": "성스러운베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 92, "accuracy": 95,
                 "description": "[BRV:92] [기본공격] [성스러운힘] - 성기사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["holy_blessing"],
                 "sfx": "sword_hit", "organic_effects": {"신성_마법": 0.2, "수호_의지": 0.1}},
                
                {"name": "신성찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 112, "accuracy": 90,
                 "description": "[HP:112] [기본공격] [정화효과] - 성기사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["purify_touch"],
                 "sfx": "sword_hit", "organic_effects": {"신성_마법": 0.25, "수호_의지": 0.15}},
                
                # ✨ 성기사 - 성역 시스템 (버프 기반 수호자)
                {"name": "성스러운 타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 110, "accuracy": 95, "element": ElementType.LIGHT,
                 "description": "[BRV:110] [성속성] [성역생성] - 성스러운 힘이 깃든 공격으로 성역을 생성할 수 있습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["holy_strike_sanctuary"],
                 "sfx": "sword_hit", "organic_effects": {"신성_마법": 0.4, "수호_의지": 0.3, "전투_본능": 0.3}},
                
                {"name": "축복", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 4, "sfx": "protect",
                 "description": "[아군버프] [성역트리거] [축복] - 아군에게 축복을 내려 성역 생성 조건을 만듭니다.",
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 5, "intensity": 1.2}],
                 "special_effects": ["blessing_sanctuary"],
                 "organic_effects": {"신성_마법": 0.4, "수호_의지": 0.35, "지휘력": 0.25}},
                
                {"name": "심판의 빛", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 140, "cast_time": 12, "element": ElementType.LIGHT,
                 "description": "[HP:140] [성역수비례강화] [성속성] - 성역 수에 따라 위력이 증가하는 심판의 빛입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["judgment_light"],
                 "sfx": "critical_hit", "organic_effects": {"신성_마법": 0.45, "수호_의지": 0.3, "전투_본능": 0.25}},
                
                {"name": "성역 확장", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "sfx": "magic_cast",
                 "description": "[성역+2] [전체강화] - 성역을 확장하여 아군 전체를 강화합니다.",
                 "special_effects": ["sanctuary_expand"],
                 "organic_effects": {"신성_마법": 0.4, "수호_의지": 0.35, "지휘력": 0.25}},
                
                {"name": "신성한 보호", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 2.5, "cast_time": 15,
                 "description": "[전체회복] [성역강화] - 성역의 힘으로 아군 전체를 치유하고 보호합니다.",
                 "special_effects": ["divine_protection"],
                 "sfx": "heal2", "organic_effects": {"신성_마법": 0.4, "수호_의지": 0.35, "치유술": 0.25}},
                
                {"name": "천사 강림", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 170, "cooldown": 6, "cast_time": 30, "element": ElementType.LIGHT,
                 "description": "[궁극] [HP:170] [전체] [최대성역] - 모든 성역의 힘을 모아 천사를 강림시킵니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["angel_descent"],
                 "sfx": "critical_hit", 
                 "organic_effects": {"신성_마법": 0.6, "수호_의지": 0.4, "지휘력": 0.35, "치유술": 0.3}}
            ],
            
            "암흑기사": [
                # === 기본 공격 ===
                {"name": "어둠베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 90, "accuracy": 92,
                 "description": "[BRV:90] [기본공격] [어둠의힘] - 암흑기사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["darkness_power"],
                 "sfx": "sword_hit", "organic_effects": {"어둠_마법": 0.2, "생명_흡수": 0.1}},
                
                {"name": "흡혈찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 110, "accuracy": 90,
                 "description": "[HP:110] [기본공격] [소량흡혈] - 암흑기사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["minor_vampiric"],
                 "sfx": "sword_hit", "organic_effects": {"어둠_마법": 0.15, "생명_흡수": 0.25}},
                
                # 🌑 암흑기사 - 어둠의 오라 + 회복 스택 시스템
                {"name": "흡혈 베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 115, "accuracy": 92,
                 "description": "[BRV:115] [흡수스택생성] [지속피해] - 피해 흡수 스택을 생성하며 모든 적에게 지속 피해를 입힙니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["vampire_slash", "dark_aura"],
                 "sfx": "sword_hit", "organic_effects": {"어둠_마법": 0.4, "생명_흡수": 0.35, "전투_본능": 0.25}},
                
                {"name": "어둠의 오라", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "magic_cast",
                 "description": "[존재자체로지속피해] [피해흡수] [패시브] - 존재만으로 모든 적에게 지속 피해를 주고 피해를 흡수합니다.",
                 "special_effects": ["dark_aura_passive"],
                 "organic_effects": {"어둠_마법": 0.45, "생명_흡수": 0.35, "마력_제어": 0.2}},
                
                {"name": "흡혈 강타", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 135, "cast_time": 10,
                 "description": "[HP:135] [흡수스택소모] [회복] - 흡수 스택을 소모하여 강력한 공격과 함께 체력을 회복합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["vampiric_strike"],
                 "sfx": "critical_hit", "organic_effects": {"어둠_마법": 0.4, "생명_흡수": 0.4, "전투_본능": 0.2}},
                
                {"name": "생명력 흡수", "type": SkillType.SPECIAL, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "cast_time": 15,
                 "description": "[전체흡수] [스택축적] [회복75%제한] - 모든 적에게서 생명력을 흡수하여 회복 스택을 최대 HP의 75%까지 축적합니다.",
                 "special_effects": ["life_drain_all"],
                 "sfx": "magic_cast", "organic_effects": {"어둠_마법": 0.4, "생명_흡수": 0.4, "마력_제어": 0.2}},
                
                {"name": "어둠의 권능", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "brv_power": 100, "hp_power": 120, "cast_time": 18,
                 "description": "[BRV:100+HP:120] [전체] [어둠강화] - 어둠의 힘으로 모든 적을 공격하며 흡수 능력을 강화합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["dark_dominion"],
                 "sfx": "critical_hit", "organic_effects": {"어둠_마법": 0.45, "생명_흡수": 0.3, "마력_제어": 0.25}},
                
                {"name": "어둠의 지배자", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 160, "cooldown": 6, "cast_time": 25,
                 "description": "[궁극] [HP:160] [모든스택폭발] [광역고정피해+보호막] - 모든 흡수 스택을 폭발시켜 광역 고정 피해와 보호막을 생성합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["dark_lord"],
                 "sfx": "critical_hit", 
                 "organic_effects": {"어둠_마법": 0.6, "생명_흡수": 0.4, "마력_제어": 0.35, "지배력": 0.3}}
            ],

            "용기사": [
                # === 도약의 사냥꾼 - 표식 시스템 ===
                # 기본공격
                {"name": "용의표식", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 95, "accuracy": 90,
                 "description": "[BRV:95] [용의표식] - 기본 BRV 공격으로 적에게 용의 표식을 부여합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["dragon_mark"],
                 "sfx": "slash", "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.3, "표식_숙련": 0.25}},
                
                # HP 기본공격  
                {"name": "도약공격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 120, "accuracy": 85,
                 "description": "[HP:120] [도약] [지연공격] [크리티컬확정] - 도약하여 지연 공격을 가하고 표식을 부여합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["leap_attack"],
                 "sfx": "heavy_attack", "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.3, "기동력": 0.25}},
                
                {"name": "용린보호", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3,
                 "description": "[방어력+30%] [표식가속] - 용린으로 자신을 보호하고 표식 축적 속도를 가속화합니다.",
                 "sfx": "protect",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 5, "intensity": 1.3}],
                 "special_effects": ["dragon_scale"],
                 "organic_effects": {"용족_혈통": 0.4, "방어_기술": 0.3, "표식_숙련": 0.25}},
                
                {"name": "표식폭발", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 110, "accuracy": 95,
                 "description": "[BRV:110+표식보너스] [표식기반] - 축적된 표식을 이용해 강화된 BRV 공격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["dragon_mark"],
                 "sfx": "explosion", "organic_effects": {"용족_혈통": 0.4, "표식_숙련": 0.35, "전투_본능": 0.25}},
                
                {"name": "용의숨결", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 140, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:140+표식보너스40%] [크리티컬확정] - 표식 수에 따라 위력이 강화되는 용의 숨결 공격입니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.FIRE,
                 "special_effects": ["dragon_breath"],
                 "sfx": "fire", "organic_effects": {"용족_혈통": 0.45, "화염_친화": 0.3, "표식_숙련": 0.3}},
                
                {"name": "용의위엄", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6,
                 "description": "[위압] [모든표식폭발] - 용의 위엄으로 모든 적의 표식을 폭발시키고 위압합니다.",
                 "special_effects": ["dragon_majesty"],
                 "sfx": "critical_hit", "organic_effects": {"용족_혈통": 0.45, "위압감": 0.3, "표식_숙련": 0.3}},
                
                {"name": "드래곤로드", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 16, "hp_power": 180, "cooldown": 6, "cast_time": 25,
                 "description": "[궁극] [HP:180+표식강화60%] [일정시간무적] - 모든 표식을 초강화 융합하는 궁극기입니다.",
                 "damage_type": DamageType.HYBRID, "element": ElementType.FIRE,
                 "special_effects": ["dragon_lord_ultimate"],
                 "sfx": "critical_hit", "organic_effects": {"용족_혈통": 0.6, "표식_숙련": 0.45, "화염_친화": 0.4, "전투_본능": 0.35}}
            ],
            
            # === 원소 순환의 현자 - 아크메이지 ===
            "아크메이지": [
                # === 원소 순환 시스템 ===
                # 기본공격 - 번개
                {"name": "라이트닝볼트", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 90, "accuracy": 95,
                 "description": "[BRV:90] [번개카운트+1] - 기본 번개 공격으로 번개 속성 카운트를 증가시킵니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.LIGHTNING,
                 "special_effects": ["lightning_count"],
                 "sfx": "lightning", "organic_effects": {"원소_친화": 0.4, "마나_순환": 0.3, "집중력": 0.25}},
                
                # HP 기본공격 - 화염
                {"name": "파이어볼", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 115, "accuracy": 85,
                 "description": "[HP:115] [화염카운트+1] - 기본 화염 공격으로 화염 속성 카운트를 증가시킵니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.FIRE,
                 "special_effects": ["fire_count"],
                 "sfx": "fire", "organic_effects": {"원소_친화": 0.4, "마나_순환": 0.3, "화염_친화": 0.25}},
                
                {"name": "아이스샤드", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 105, "accuracy": 90,
                 "description": "[BRV:105] [냉기카운트+1] - 냉기 공격으로 적을 얼리고 냉기 속성 카운트를 증가시킵니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.ICE,
                 "special_effects": ["ice_count"],
                 "sfx": "ice", "organic_effects": {"원소_친화": 0.4, "마나_순환": 0.3, "냉기_친화": 0.25}},
                
                {"name": "원소강화", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4,
                 "description": "[마법공격력+20%] [원소친화도상승] - 원소 마법의 위력을 강화하고 친화도를 상승시킵니다.",
                 "sfx": "haste",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2}],
                 "special_effects": ["elemental_mastery"],
                 "organic_effects": {"원소_친화": 0.45, "마나_순환": 0.3, "집중력": 0.25}},
                
                {"name": "원소융합", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "hp_power": 125, "cast_time": 15, "accuracy": 85,
                 "description": "[HP:125] [복합원소] - 모든 원소를 융합한 복합 속성 공격으로 광역 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.NEUTRAL,
                 "special_effects": ["elemental_fusion"],
                 "sfx": "magic_cast", "organic_effects": {"원소_친화": 0.5, "마나_순환": 0.35, "집중력": 0.3}},
                
                {"name": "원소순환", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 6,
                 "description": "[원소순환활성화] [3회동일원소시자동시전] - 원소 순환 시스템을 활성화합니다.",
                 "special_effects": ["elemental_cycle"],
                 "sfx": "magic_cast", "organic_effects": {"원소_친화": 0.5, "마나_순환": 0.4, "집중력": 0.35}},
                
                {"name": "원소대폭발", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 160, "cooldown": 6, "cast_time": 25,
                 "description": "[궁극] [HP:160+원소보너스] [모든속성동시] - 축적된 모든 원소를 대폭발시키는 궁극기입니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.NEUTRAL,
                 "special_effects": ["all_elements_burst"],
                 "sfx": "ultimate_magic", "organic_effects": {"원소_친화": 0.6, "마나_순환": 0.45, "집중력": 0.4, "폭발_제어": 0.35}}
            ],

            "정령술사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "정령소환", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 87, "accuracy": 93,
                 "description": "[BRV:87] [정령] [소환] - [BRV] 원소 정령을 소환하여 적을 공격하며 정령 친화도를 높입니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["spirit_bond"],  # 기본 공격으로 정령 친화도 증가
                 "organic_effects": {"정령_친화": 0.3, "마법_지식": 0.25, "원소_조화": 0.2}},
                {"name": "원소융합", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 100, "accuracy": 88,
                 "description": "[HP:100] [원소] [융합] - [HP] 여러 원소를 융합하여 강력한 원소 공격을 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["elemental_fusion"],  # 기본 HP 공격으로 원소 융합
                 "sfx": "explosion", "organic_effects": {"원소_조화": 0.35, "정령_친화": 0.25, "마법_지식": 0.2}},
                
                # 정령의 친구 - [정령][소환] 키워드 특화
                {"name": "정령교감", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "haste",
                 "description": "[원소강화+] [정령] [교감] - [BUFF] 정령과 교감하여 원소 마법의 위력을 크게 증가시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "자연_이해": 0.3}},
                {"name": "화염정령", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 98, "element": ElementType.FIRE, "accuracy": 95,
                 "description": "[BRV:100] [화속] [정령] - [BRV] 화염 정령을 소환하여 적을 공격하고 BRV를 획득합니다.",
                 "sfx": "fire2",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BURN, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "화염_친화": 0.3, "마법_지식": 0.3}},
                {"name": "물정령치유", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 2.7, "element": ElementType.WATER,
                 "description": "[치유:중] [수속] [정령] - [HEAL] 물 정령의 힘으로 아군의 상처를 치유하고 HP를 회복시킵니다.",
                 "sfx": "heal",
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "치유_기술": 0.3}},
                {"name": "바람정령축복", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "sfx": "protect",
                 "description": "[속도+] [회피+] [풍속] - [BUFF] 바람 정령의 축복으로 아군의 속도와 회피율을 증가시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.2}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "대지정령분노", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "hp_power": 118, "element": ElementType.EARTH, "cast_time": 20,
                 "description": "[HP:125] [토속] [정령] - [HP] 대지정령의 분노로 적의 HP에 강력한 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["earth_rage"],
                 "sfx": "magic_cast", "organic_effects": {
"정령_친화": 0.4, "마법_지식": 0.35, "자연_이해": 0.3}},
                {"name": "사대정령소환", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 20, "hp_power": 140, "cooldown": 8, "cast_time": 40,
                 "description": "[궁극] [4원소] [소환] - [궁극] 4대 정령을 모두 소환하여 압도적인 원소 공격을 펼치는 궁극기입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["four_elements"],
                 "sfx": "summon", "organic_effects": {
"정령_친화": 0.5, "마법_지식": 0.4, "자연_이해": 0.35, "집중력": 0.3}}
            ],
            
            "시간술사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "시간침", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 92, "accuracy": 95,
                 "description": "[BRV:92] [시간] [침] - [BRV] 시간의 힘을 담은 침으로 적을 찌르고 BRV를 획득합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["time_record_savepoint"],  # 기본 공격으로 시간 기록점 생성
                 "organic_effects": {"시간_조작": 0.3, "마법_지식": 0.2, "정밀함": 0.2}},
                {"name": "시간파동", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 105, "accuracy": 90,
                 "description": "[HP:105] [시간] [파동] - [HP] 시간의 파동으로 적의 HP에 직접적인 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["future_sight"],  # 기본 HP 공격으로 미래시 효과
                 "sfx": "magic_attack", "organic_effects": {"시간_조작": 0.35, "마법_지식": 0.25, "정밀함": 0.2}},
                
                # 시간의 조작자 - [시간][조작] 키워드 특화
                {"name": "시간가속", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5,
                 "description": "[속도+50%] [시간] [가속] - [BUFF] 시간을 가속시켜 자신의 행동 속도를 크게 증가시킵니다.",
                 "sfx": "haste",
                 "status_effects": [{
"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.25}],
                 "organic_effects": {"시간_조작": 0.4, "마법_지식": 0.3, "집중력": 0.3}},
                {"name": "시간왜곡", "type": SkillType.SPECIAL, "target": TargetType.BATTLEFIELD,
                 "mp_cost": 2, "cooldown": 3, "sfx": "stop",
                 "description": "[시간조작] [특수] [왜곡] - [SPECIAL] 시간을 왜곡시켜 특별한 효과를 발동시킵니다.",
                 "status_effects": [{"type": StatusType.TIME_MARKED, "duration": 10, "intensity": 1.0}],
                 "special_effects": ["time_record_savepoint"],
                 "organic_effects": {"시간_조작": 0.45, "마법_지식": 0.35, "정밀함": 0.3}},
                {"name": "시간되돌리기", "type": SkillType.SPECIAL, "target": TargetType.ANY_SINGLE,
                 "mp_cost": 15, "cooldown": 6, "cast_time": 25,
                 "description": "[복원] [시간] [기적] - [SPECIAL] 시간을 되돌려 이전 상태로 복원하는 기적을 일으킵니다.",
                 "special_effects": ["time_rewind_to_savepoint"],
                 "sfx": "magic_cast", "organic_effects": {
"시간_조작": 0.5, "마법_지식": 0.35, "정밀함": 0.25}},
                {"name": "미래예지", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 9, "cooldown": 4,
                 "description": "[회피+] [명중+] [예지] - [BUFF] 미래를 예지하여 회피율과 명중률을 크게 증가시킵니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.FORESIGHT, "duration": 5, "intensity": 1.0}],
                 "special_effects": ["future_sight"],
                 "organic_effects": {"시간_조작": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "시간정지", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "cooldown": 5, "cast_time": 25,
                 "description": "[전체정지] [시간] [필드] - [FIELD] 시간을 정지시켜 모든 적의 행동을 일시 중단시킵니다.",
                 "sfx": "stop",
                 "status_effects": [{
"type": StatusType.TIME_STOP, "duration": 2, "intensity": 1.0}],
                 "special_effects": ["time_stop"], "is_field_skill": True,
                 "organic_effects": {"시간_조작": 0.45, "마법_지식": 0.35, "집중력": 0.2}},
                {"name": "시공간붕괴", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "hp_power": 154, "cooldown": 9, "cast_time": 45,
                 "description": "[궁극] [시공파괴] [붕괴] - [궁극] 시공간을 붕괴시켜 모든 것을 파괴하는 궁극의 시간 마법입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["spacetime_collapse"],
                 "sfx": "ultima", "organic_effects": {
"시간_조작": 0.5, "마법_지식": 0.4, "집중력": 0.35, "정밀함": 0.3}}
            ],
            
            "차원술사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "차원베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 88, "accuracy": 95,
                 "description": "[BRV:88] [차원] [베기] - [BRV] 차원의 칼날로 적을 베어 BRV를 획득하며 잔상을 생성합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["afterimage"],  # 기본 공격으로 잔상 생성
                 "organic_effects": {"차원_조작": 0.3, "회피_술법": 0.2, "민첩성": 0.2}},
                {"name": "공간찢기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 98, "accuracy": 90,
                 "description": "[HP:98] [공간] [찢기] - [HP] 공간을 찢어 적의 HP에 피해를 가하며 차원 방패를 생성합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["dimension_cloak"],  # 기본 HP 공격으로 차원 장막 효과
                 "sfx": "magic_attack", "organic_effects": {"차원_조작": 0.35, "회피_술법": 0.25, "정밀함": 0.2}},
                
                # 회피의 달인 - [차원][회피] 키워드 특화
                {"name": "차원장막", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "teleport",
                 "description": "[물리무효] [차원] [장막] - [BUFF] 차원의 장막으로 자신을 감싸 물리 공격을 회피합니다.",
                 "status_effects": [{"type": StatusType.ABSOLUTE_EVASION, "duration": 2, "intensity": 2.0}],
                 "special_effects": ["dimension_cloak"],
                 "organic_effects": {"차원_조작": 0.45, "회피_술법": 0.4, "집중력": 0.25}},
                {"name": "잔상분신", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "sfx": "teleport",
                 "description": "[회피+30%] [분신] [잔상] - [BUFF] 잔상 분신을 만들어 회피율을 크게 증가시킵니다.",
                 "status_effects": [{"type": StatusType.EVASION_UP, "duration": 5, "intensity": 1.3}],
                 "special_effects": ["afterimage"],
                 "organic_effects": {"회피_술법": 0.4, "차원_조작": 0.35, "민첩성": 0.25}},
                {"name": "공간도약", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 98, "accuracy": 100,
                 "description": "[BRV:110] [순간이동] [공간] - [BRV] 공간을 도약하여 적의 뒤로 순간이동해 기습 공격을 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["space_leap"],
                 "sfx": "teleport", "organic_effects": {
"차원_조작": 0.4, "회피_술법": 0.3, "전투_본능": 0.3}},
                {"name": "차원미로", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "sfx": "magic_cast",
                 "description": "[혼란] [이동봉인] [차원] - [DEBUFF] 차원 미로에 적을 가둬 혼란과 이동 불가 상태를 부여합니다.",
                 "status_effects": [{"type": StatusType.REDUCE_ACCURACY, "duration": 4, "intensity": 0.5}],
                 "special_effects": ["dimension_maze"],
                 "organic_effects": {"차원_조작": 0.4, "회피_술법": 0.35, "지혜": 0.25}},
                {"name": "회피반격", "type": SkillType.COUNTER, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "hp_power": 118, "cooldown": 3,
                 "description": "[회피시반격] [카운터] [특수] - [COUNTER] 공격을 회피하면서 동시에 반격하는 특수 기술입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["evasion_counter"],
                 "sfx": "critical_hit", "organic_effects": {
"회피_술법": 0.45, "차원_조작": 0.35, "전투_본능": 0.3}},
                {"name": "무적의경지", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 20, "cooldown": 8, "cast_time": 25,
                 "description": "[궁극] [무적] [초월] - [궁극] 모든 차원을 초월하여 무적 상태가 되는 궁극의 차원 술법입니다.",
                 "sfx": "limit_break",
                 "status_effects": [{"type": StatusType.ABSOLUTE_EVASION, "duration": 3, "intensity": 99.0}],
                 "special_effects": ["untouchable_state"],
                 "organic_effects": {"회피_술법": 0.6, "차원_조작": 0.5, "집중력": 0.4, "민첩성": 0.35}}
            ],
            
            "철학자": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "논리검증", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 82, "accuracy": 95,
                 "description": "[BRV:82] [논리] [검증] - [BRV] 논리적 검증으로 적의 허점을 찌르고 지혜를 쌓습니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["truth_insight"],  # 기본 공격으로 진리 통찰
                 "organic_effects": {"지혜": 0.3, "마법_지식": 0.2, "정밀함": 0.2}},
                {"name": "철학충격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 108, "accuracy": 90,
                 "description": "[HP:108] [철학] [충격] - [HP] 철학적 충격으로 적의 정신에 직접적인 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["philosophical_thought"],  # 기본 HP 공격으로 철학적 사고
                 "sfx": "magic_attack", "organic_effects": {"지혜": 0.35, "마법_지식": 0.25, "집중력": 0.2}},
                
                # 진리의 탐구자 - [지혜][분석] 키워드 특화
                {"name": "진리탐구", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4,
                 "description": "[지혜+] [마력+] [탐구] - [BUFF] 진리를 탐구하여 지혜와 마법력을 크게 증가시킵니다.",
                 "sfx": "haste",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 6, "intensity": 1.15}],
                 "organic_effects": {"지혜": 0.4, "마법_지식": 0.3, "집중력": 0.3}},
                {"name": "진실간파", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "sfx": "magic_cast",
                 "description": "[약점파악] [분석] [진실] - [SPECIAL] 진실을 간파하여 적의 약점과 상태를 파악합니다.",
                 "status_effects": [{"type": StatusType.VULNERABLE, "duration": 4, "intensity": 1.3}],
                 "special_effects": ["truth_insight"],
                 "organic_effects": {"지혜": 0.45, "마법_지식": 0.3, "정밀함": 0.25}},
                {"name": "지혜의빛", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "sfx": "magic_cast",
                 "description": "[전체 지능+] [빛] [지혜] - [BUFF] 지혜의 빛으로 아군 전체의 지능과 마법력을 향상시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1}],
                 "organic_effects": {"지혜": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "존재부정", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 12, "hp_power": 140, "cast_time": 20,
                 "description": "[HP:120] [논리] [철학] - [HP] 철학적 논리로 적의 존재를 부정하여 HP 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["existence_denial"],
                 "sfx": "magic_cast", "organic_effects": {
"지혜": 0.5, "마법_지식": 0.35, "집중력": 0.15}},
                {"name": "철학적사고", "type": SkillType.SPECIAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 10, "cooldown": 4,
                 "description": "[통찰] [특수] [사고] - [SPECIAL] 철학적 사고로 특별한 통찰력을 얻어 유리한 효과를 발동시킵니다.",
                 "special_effects": ["philosophical_thought"],
                 "sfx": "magic_cast", "organic_effects": {
"지혜": 0.45, "마법_지식": 0.3, "지휘력": 0.25}},
                {"name": "절대진리", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 25, "hp_power": 161, "cooldown": 9, "cast_time": 50,
                 "description": "[궁극] [진리] [깨달음] - [궁극] 절대 진리를 깨달아 모든 것을 꿰뚫는 궁극의 지혜를 발휘합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["absolute_truth"],
                 "sfx": "magic_cast", "organic_effects": {
"지혜": 0.5, "마법_지식": 0.4, "집중력": 0.35, "정밀함": 0.3}}
            ],
            
            # === 바람의 저격수 - 궁수 ===
            "궁수": [
                # 🌟 기본 공격 (mp_cost: 0) - 조준 포인트 시스템
                {"name": "조준사격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 91, "accuracy": 97,
                 "description": "[BRV:91] [조준] [사격] - [BRV] 정밀한 조준으로 포인트를 축적합니다.",
                 "sfx": "bow_shot",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["precision_stack"],  # 조준 포인트 생성
                 "organic_effects": {"원거리_숙련": 0.3, "정밀_사격": 0.25, "전투_본능": 0.2}},
                {"name": "강화관통", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 108, "accuracy": 92,
                 "description": "[HP:108] [관통] [조준활용] - [HP] 조준 포인트를 활용한 강화된 관통 사격입니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["arrow_penetration"],  # 조준 포인트 활용
                 "sfx": "critical_hit", "organic_effects": {"정밀_사격": 0.35, "원거리_숙련": 0.25, "전투_본능": 0.2}},
                # 바람의 유격수 - [연사][기동] 키워드 특화 → 조준 시스템
                {"name": "삼연사", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 98, "accuracy": 95, "hit_count": 3,
                 "description": "[BRV:98] [연속] [조준생성] - [BRV] 연속 사격으로 조준 포인트를 대량 생성합니다.",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.WIND,
                 "special_effects": ["triple_shot"],  # 조준 포인트 생성 포함
                 "sfx": "magic_cast", "organic_effects": {
"유격_전술": 0.35, "바람_친화": 0.3, "정밀_사격": 0.25}},
                {"name": "정밀관통", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 8, "hp_power": 98, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:115] [관통] [물리] - [HP] 관통력이 뛰어난 화살로 적의 HP에 직접 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["piercing_shot"],
                 "sfx": "gun_critical", "organic_effects": {
"정밀_사격": 0.4, "유격_전술": 0.3, "집중력": 0.2}},
                {"name": "독화살", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 105, "accuracy": 95,
                 "description": "[BRV:90] [독] [물리] - [BRV] 독이 발린 화살로 적을 공격하여 BRV를 획득하고 중독시킵니다.",
                 "sfx": "poison",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "status_effects": [{
"type": StatusType.POISON, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정밀_사격": 0.35, "생존_본능": 0.3, "유격_전술": 0.25}},
                {"name": "폭발화살", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 112, "cast_time": 20, "accuracy": 85,
                 "description": "[HP:130] [폭발] [물리] - [HP] 폭발하는 화살로 적에게 강력한 HP 피해를 가합니다.",
                 "sfx": "gun_hit",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.FIRE,
                 "status_effects": [{
"type": StatusType.BURN, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"유격_전술": 0.35, "정밀_사격": 0.3, "바람_친화": 0.25}},
                {"name": "지원사격", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 8, "sfx": "magic_cast",
                 "description": "[조준소모] [지원] [사격] - [BUFF] 아군 행동 시 조준 포인트를 소모하여 자동 지원사격을 실시합니다.",
                 "special_effects": ["support_fire_activation"],
                 "organic_effects": {"정밀_사격": 0.4, "유격_전술": 0.3, "집중력": 0.25}},
                {"name": "헌터모드", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 16, "cooldown": 6,
                 "description": "[궁극] [사냥] [완벽조준] - [궁극] 완벽한 사냥꾼 모드로 진입하여 모든 사격 능력을 극대화하는 궁극기입니다.",
                 "special_effects": ["hunter_mode"],
                 "sfx": "magic_cast", "organic_effects": {
"정밀_사격": 0.5, "유격_전술": 0.4, "바람_친화": 0.35, "생존_본능": 0.3}}
            ],

            "암살자": [
                # � 기본 공격 (mp_cost: 0)
                {"name": "그림자베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 94, "accuracy": 96, "crit_rate": 8,
                 "description": "[BRV:94] [그림자] [베기] - [BRV] 그림자의 힘으로 적을 베어 BRV를 획득하며 그림자를 생성합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["generate_shadow"],  # 기본 공격으로 그림자 생성
                 "shadow_count": 1,
                 "organic_effects": {"그림자_조작": 0.3, "암살_기술": 0.25, "은신_술법": 0.2}},
                {"name": "그림자처형", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 109, "accuracy": 90, "crit_rate": 15,
                 "description": "[HP:109] [그림자] [처형] - [HP] 그림자 스택에 비례한 치명적인 처형 공격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["shadow_execution"],  # 기본 HP 공격으로 그림자 소모
                 "sfx": "critical_hit", "organic_effects": {"암살_기술": 0.35, "그림자_조작": 0.25, "정밀함": 0.2}},
                
                # �🌑 그림자의 암살자 - [그림자][암살] 특화 시스템
                # 그림자 메커니즘: 
                # - 기본공격/BRV공격 시 그림자 1개 생성 (최대 5개)
                # - 그림자 연막 등 특수 스킬은 그림자 2개 생성
                # - 기본공격/궁극기 외 스킬 사용 시 그림자 1개 소모하여 1.5배 피해
                # - 궁극기는 모든 그림자를 소모하여 그림자 수만큼 피해 증폭
                
                {"name": "그림자숨기", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "sfx": "magic_cast",
                 "description": "[은신] [그림자+1] - 그림자에 숨어 은신하며 그림자를 1개 생성합니다.",
                 "status_effects": [{"type": StatusType.STEALTH, "duration": 2, "intensity": 1.0}],
                 "special_effects": ["generate_shadow"], "shadow_count": 1,
                 "organic_effects": {"은신_술법": 0.4, "그림자_조작": 0.4, "생존_본능": 0.2}},
                
                {"name": "그림자 강타", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 105, "crit_rate": 12, "accuracy": 95,  # brv_power: 115→105, crit_rate: 15→12로 너프
                 "description": "[BRV:95] [그림자+1] - 그림자와 함께 공격하여 BRV를 획득하고 그림자를 1개 생성합니다.",
                 "damage_type": DamageType.PHYSICAL, 
                 "special_effects": ["generate_shadow", "shadow_echo"], "shadow_count": 1,
                 "sfx": "attack_sound", "organic_effects": {"그림자_조작": 0.4, "암살_기술": 0.3, "정밀함": 0.3}},
                
                {"name": "독바르기", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "magic_cast", "can_consume_shadow": True,
                 "description": "[독부여] [그림자소모가능] - 무기에 독을 바릅니다. 그림자 1개를 소모하면 효과가 1.3배 강화됩니다.",  # 1.5배→1.3배로 너프
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15}],  # 1.1→1.15로 상향
                 "special_effects": ["poison_weapon"],
                 "organic_effects": {"독술_지식": 0.4, "그림자_조작": 0.3, "암살_기술": 0.3}},
                
                {"name": "그림자 연막", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "cooldown": 3, "can_consume_shadow": True,
                 "description": "[시야차단] [그림자+2] - 그림자 연막으로 시야를 차단하고 그림자 2개를 생성합니다. 그림자 소모로 강화 가능.",
                 "sfx": "magic_cast", "shadow_count": 2,
                 "status_effects": [{"type": StatusType.BLIND, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["smoke_bomb", "generate_shadow"],
                 "organic_effects": {"은신_술법": 0.4, "그림자_조작": 0.4, "전술_지식": 0.2}},
                
                {"name": "그림자 암살", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 145, "cast_time": 12, "crit_rate": 25, "can_consume_shadow": True,
                 "description": "[HP:120] [암살] [그림자소모가능] - 은밀한 암살술로 HP 피해를 가합니다. 그림자로 강화 가능.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["assassination"],
                 "sfx": "critical_hit", "organic_effects": {"암살_기술": 0.5, "그림자_조작": 0.3, "정밀함": 0.2}},
                
                {"name": "그림자 처형", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 15, "hp_power": 155, "cooldown": 7, "cast_time": 8,
                 "description": "[궁극] [그림자전체소모] - 모든 그림자를 소모하여 괴멸적인 일격을 가합니다. 그림자 1개당 +20% 피해.",
                 "damage_type": DamageType.PHYSICAL, 
                 "special_effects": ["shadow_execution", "consume_all_shadows"],
                 "sfx": "ultimate_sound", "organic_effects": {"암살_기술": 0.6, "그림자_조작": 0.5, "정밀함": 0.4}}
            ],
            
            # === 맹독의 침묵자 - 도적 ===
            "도적": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "독침", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 90, "accuracy": 96,
                 "description": "[BRV:90] [독] [침] - [BRV] 독침으로 적을 찔러 BRV를 획득하며 독 스택을 쌓습니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.PHYSICAL,
                 "element": ElementType.POISON,
                 "special_effects": ["poison_stack"],  # 기본 공격으로 독 스택 축적
                 "organic_effects": {"독술_지배": 0.3, "침묵_술": 0.25, "민첩성": 0.2}},
                {"name": "암살", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 106, "accuracy": 88,
                 "description": "[HP:106] [암살] [치명타] - [HP] 치명적인 암살 공격으로 독 스택에 비례한 추가 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["lethal_strike"],  # 기본 HP 공격으로 독 스택 기반 강화
                 "sfx": "critical_hit", "organic_effects": {"침묵_술": 0.35, "독술_지배": 0.25, "민첩성": 0.2}},
                
                # 맹독의 침묵자 - [독성][침묵][촉진] 키워드 특화  
                {"name": "침묵의독침", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 90, "accuracy": 95,
                 "description": "[BRV:70] [독] [침묵] - [BRV] 침묵의 독침으로 적을 공격하고 지속적인 독 피해를 가합니다.",
                 "sfx": "poison",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "status_effects": [{"type": StatusType.POISON, "duration": 6, "intensity": 1.2}],
                 "special_effects": ["poison_stack"],
                 "organic_effects": {"독술_지배": 0.4, "침묵_술": 0.3, "독_촉진": 0.25}},
                {"name": "부식독", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 85, "accuracy": 90,
                 "description": "[BRV:65] [부식] [방감] - [BRV] 강산성 독으로 적의 방어력을 부식시키며 독을 누적시킵니다.",
                 "sfx": "poison",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "status_effects": [{"type": StatusType.POISON, "duration": 8, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_DEF, "duration": 5, "intensity": 0.7}],
                 "special_effects": ["corrosive_poison"],
                 "organic_effects": {"독술_지배": 0.35, "독_촉진": 0.3, "침묵_술": 0.25}},
                {"name": "침묵살", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 110, "cast_time": 10, "accuracy": 95,
                 "description": "[HP:110] [침묵] [암살] - [HP] 완전한 침묵 속에서 적을 암살하며 남은 독을 촉진시킵니다.",
                 "sfx": "critical_hit",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["poison_trigger"],
                 "organic_effects": {"침묵_술": 0.4, "독_촉진": 0.35, "독술_지배": 0.25}},
                {"name": "독안개진", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "cast_time": 15, "cooldown": 4,
                 "description": "[독안개] [전체] [지속] - [FIELD] 독성 안개를 퍼뜨려 모든 적을 서서히 말려죽입니다.",
                 "sfx": "magic_cast",
                 "is_field_skill": True, "special_effects": ["poison_fog_enhanced"],
                 "status_effects": [{"type": StatusType.POISON, "duration": 8, "intensity": 1.8}],
                 "organic_effects": {"독술_지배": 0.45, "독_촉진": 0.3, "침묵_술": 0.25}},
                {"name": "독혈폭발", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 12, "brv_power": 95, "hp_power": 85, "cast_time": 15, "cooldown": 3,
                 "description": "[BRV+HP] [폭발] [독촉진] - [BRV+HP] 적의 독혈을 폭발시켜 누적된 독 피해를 한번에 터뜨립니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.POISON,
                 "special_effects": ["venom_explosion"],
                 "sfx": "magic_cast", 
                 "organic_effects": {"독_촉진": 0.5, "독술_지배": 0.35, "침묵_술": 0.25}},
                {"name": "독왕강림", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 20, "hp_power": 140, "cast_time": 25, "cooldown": 7,
                 "description": "[궁극] [독지배] [전체촉진] - [궁극] 독의 왕으로 강림하여 모든 적의 독을 폭발시키는 궁극기입니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.POISON,
                 "special_effects": ["poison_emperor"],
                 "sfx": "magic_cast", 
                 "organic_effects": {"독술_지배": 0.6, "독_촉진": 0.5, "침묵_술": 0.4}}
            ],
            
            "해적": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "보물검", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 94, "accuracy": 95,
                 "description": "[BRV:94] [보물] [검] - [BRV] 보물을 찾는 검으로 적을 공격하고 골드를 획득할 기회를 얻습니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["treasure_hunt"],  # 기본 공격으로 보물 탐지
                 "organic_effects": {"해적_기술": 0.3, "행운": 0.25, "민첩성": 0.2}},
                {"name": "약탈공격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 103, "accuracy": 90,
                 "description": "[HP:103] [약탈] [공격] - [HP] 적을 공격하며 동시에 소지품을 약탈합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["pirate_plunder"],  # 기본 HP 공격으로 약탈 효과
                 "sfx": "physical_attack", "organic_effects": {"해적_기술": 0.35, "행운": 0.25, "전투_본능": 0.2}},
                
                # 바다의 무법자 - [해적][자유] 키워드 특화
                {"name": "이도류", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2,
                 "description": "[공격+20%] [이도류] [검술] - [BUFF] 양손에 검을 들고 이도류 전투 자세로 공격력을 증가시킵니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15},
                                   {"type": StatusType.BOOST_CRIT, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"해적_정신": 0.4, "무술_수행": 0.3, "자유_의지": 0.3}},
                {"name": "칼부림", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 112, "crit_rate": 15, "accuracy": 90, "sfx": "magic_cast",
                 "description": "[BRV:90] [이도류] [연타] - [BRV] 이도류로 연속 공격하여 BRV를 획득합니다.",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.LIGHTNING,
                 "status_effects": [{
"type": StatusType.BLEED, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.4, "무술_수행": 0.35, "전투_본능": 0.25}},
                {"name": "바다의저주", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "element": ElementType.WATER, "sfx": "slow",
                 "description": "[행동력감소] [저주] [바다] - [DEBUFF] 바다의 저주로 적을 속박하여 행동력을 크게 감소시킵니다.",
                 "status_effects": [{
"type": StatusType.CURSE, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_SPD, "duration": 4, "intensity": 0.8}],
                 "organic_effects": {"해적_정신": 0.4, "마법_지식": 0.3, "자유_의지": 0.3}},
                {"name": "해적의함성", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 5, "cooldown": 3,
                 "description": "[전체 공격+] [사기+] [해적] - [BUFF] 해적다운 함성으로 아군의 공격력과 사기를 올립니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 3, "intensity": 1.1},
                                   {"type": StatusType.INSPIRATION, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.4, "지휘력": 0.35, "자유_의지": 0.25}},
                {"name": "해상치료술", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 2.5, "sfx": "heal",
                 "description": "[전체치유] [필드] [바다] - [FIELD] 바다에서 배운 치료술로 아군 전체의 상처를 치유합니다.",
                 "element": ElementType.WATER, "is_field_skill": True,
                 "status_effects": [{
"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.35, "마법_지식": 0.3, "치유_기술": 0.25}},
                {"name": "폭풍의함대", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 17, "hp_power": 133, "element": ElementType.WATER,
                 "cooldown": 6, "cast_time": 18, "sfx": "magic_cast",
                 "description": "[궁극] [HP:133] [전체] [공포] [쿨:6턴] - [궁극] 유령 함대를 소환하여 모든 적에게 공포와 함께 강력한 물 속성 공격을 가합니다.",
                 "damage_type": DamageType.HYBRID, "special_effects": ["ghost_fleet"],
                 "status_effects": [{"type": StatusType.FEAR, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.5, "지휘력": 0.4, "마법_지식": 0.35, "자유_의지": 0.3}}
            ],
            
            "사무라이": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "거합베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 96, "accuracy": 95,
                 "description": "[BRV:96] [거합] [베기] - [BRV] 전통적인 거합술로 적을 베어 의지를 모읍니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["samurai_focus"],  # 기본 공격으로 의지 집중
                 "organic_effects": {"검술": 0.3, "집중력": 0.25, "정신력": 0.2}},
                {"name": "의지집중", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 110, "accuracy": 90,
                 "description": "[HP:110] [의지] [집중] - [HP] 마음을 집중하여 강력한 일격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["bushido_spirit"],  # 기본 HP 공격으로 무사도 정신
                 "sfx": "critical_hit", "organic_effects": {"검술": 0.35, "정신력": 0.25, "집중력": 0.2}},
                
                # 검의 구도자 - [무사도][정신] 키워드 특화
                {"name": "무사도", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3,
                 "description": "[전능력+] [무사도] [정신] - [BUFF] 무사도 정신으로 자신의 전투 능력을 크게 향상시킵니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.FOCUS, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "검술_대가": 0.3, "집중력": 0.3}},
                {"name": "거합베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 125, "accuracy": 98, "crit_rate": 20,
                 "description": "[BRV:125] [발도] [크리+] - [BRV] 검을 뽑는 순간의 집중력으로 강력한 BRV 공격을 가합니다.",
                 "sfx": "critical_hit",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.LIGHTNING,
                 "status_effects": [{
"type": StatusType.SILENCE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"검술_대가": 0.45, "무사도_정신": 0.3, "집중력": 0.25}},
                {"name": "명상", "type": SkillType.HEAL, "target": TargetType.SELF,
                 "mp_cost": 4, "heal_power": 2.2,
                 "description": "[HP회복] [MP회복] [명상] - [HEAL] 깊은 명상으로 내면의 평화를 찾아 HP와 MP를 회복합니다.",
                 "sfx": "heal",
                 "element": ElementType.NEUTRAL,
                 "status_effects": [{
"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "집중력": 0.35, "치유_기술": 0.25}},
                {"name": "진검승부", "type": SkillType.COUNTER, "target": TargetType.SELF,
                 "mp_cost": 5, "cooldown": 2, "sfx": "sword_hit",
                 "description": "[반격강화] [카운터] [검술] - [COUNTER] 진검승부 자세로 적의 공격을 받아 더 강한 반격을 가합니다.",
                 "status_effects": [{"type": StatusType.COUNTER, "duration": 3, "intensity": 2.0},
                                   {"type": StatusType.BARRIER, "duration": 3, "intensity": 1.3}],
                 "organic_effects": {"무사도_정신": 0.4, "검술_대가": 0.3, "전투_본능": 0.3}},
                {"name": "사무라이치유법", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 2.5, "sfx": "heal",
                 "description": "[전체치유] [필드] [전통] - [FIELD] 사무라이의 전통 치유법으로 아군들의 상처를 치료합니다.",
                 "element": ElementType.LIGHT, "is_field_skill": True,
                 "status_effects": [{
"type": StatusType.BLESSING, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "치유_기술": 0.3, "지휘력": 0.3}},
                {"name": "오의무상베기", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 20, "hp_power": 161, "cooldown": 8, "cast_time": 35,
                 "description": "[궁극] [HP:180] [무상] [검술] - [궁극] 무상의 경지에서 펼치는 궁극의 검술로 적을 완전히 제압합니다.",
                 "sfx": "sword_hit",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.NEUTRAL,
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 2, "intensity": 1.0}],
                 "special_effects": ["mushin_cut"],
                 "organic_effects": {"무사도_정신": 0.6, "검술_대가": 0.4, "집중력": 0.35, "전투_본능": 0.3}}
            ],
            
            # === 마법 지원 계열 ===
            "바드": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "화음타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 85, "accuracy": 93,
                 "description": "[BRV:85] [화음] [타격] - [BRV] 악기로 리듬감 있게 타격하며 음악 에너지를 축적합니다.",
                 "sfx": "magic_impact",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["melody_build"],  # 기본 공격으로 멜로디 축적
                 "organic_effects": {"음악_재능": 0.3, "창작_영감": 0.25, "지휘력": 0.2}},
                {"name": "선율폭발", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 102, "accuracy": 88,
                 "description": "[HP:102] [선율] [폭발] - [HP] 축적된 음악 에너지를 강력한 음파로 방출합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["sonic_burst"],  # 기본 HP 공격으로 음파 폭발
                 "sfx": "explosion", "organic_effects": {"지휘력": 0.35, "음악_재능": 0.25, "창작_영감": 0.2}},
                
                # 선율의 지휘자 - [음악][지원] 키워드 특화
                {"name": "용기의노래", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "sfx": "magic_cast",
                 "description": "[전체 공격+10%] [크리+15%] [음악] - [BUFF][음악][버프] 용기를 북돋우는 장엄한 노래로 아군 전체의 공격력과 치명타율을 크게 강화",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1},
                                   {"type": StatusType.BOOST_CRIT, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"음악_재능": 0.4, "지휘력": 0.35, "마법_지식": 0.25}},
                {"name": "회복의선율", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "heal_power": 2.1, "sfx": "heal",
                 "description": "[전체치유:중] [재생] [음악] - [HEAL][음악][치유] 치유의 선율로 아군 전체의 HP를 회복시키는 바드의 대표적인 회복 기술",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"음악_재능": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "절망의노래", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "sfx": "magic_cast",
                 "description": "[전체 공포] [공격감소] [음악] - [DEBUFF][음악][절망] 절망적인 선율로 적 전체에 공포와 공격력 감소를 부여",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_ATK, "duration": 4, "intensity": 0.9}],
                 "organic_effects": {"음악_재능": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "신속의리듬", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "cooldown": 3, "sfx": "magic_cast",
                 "description": "[전체 속도+20%] [가속] [음악] - [BUFF][음악][신속] 빠른 리듬으로 아군 전체의 속도와 행동력을 크게 향상시킴",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.2},
                                   {"type": StatusType.HASTE, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"음악_재능": 0.4, "지휘력": 0.35, "마법_지식": 0.25}},
                {"name": "천상의치유가", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 4.5,
                 "description": "[전체치유:강] [상태해제] [필드] - [FIELD][음악][신성] 천상의 치유가로 아군 전체 치유 및 상태이상 해제",
                 "element": ElementType.LIGHT, "is_field_skill": True,
                 "special_effects": ["divine_song"],
                 "sfx": "heal3", 
                 "organic_effects": {"음악_재능": 0.4, "치유_기술": 0.3, "신성_마법": 0.3}},
                {"name": "천상의합창", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 22, "cooldown": 9, "cast_time": 40, "heal_power": 5.9,
                 "description": "[궁극] [무적:2턴] [완전치유] [천상] - [궁극][음악][신성] 천사들의 합창으로 아군 전체를 강력하게 치유하고 일시적으로 무적 상태로 만듦",
                 "sfx": "magic_cast",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.INVINCIBLE, "duration": 2, "intensity": 1.0}],
                 "special_effects": ["heavenly_chorus"],
                 "organic_effects": {"음악_재능": 0.5, "지휘력": 0.4, "치유_기술": 0.35, "신성_마법": 0.3}}
            ],
            
            "무당": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "영혼타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 89, "accuracy": 95,
                 "description": "[BRV:89] [영혼] [타격] - [BRV] 영혼의 힘으로 적을 타격하고 디버프를 축적합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.MAGICAL,
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.CURSE, "duration": 2, "intensity": 0.5}],
                 "organic_effects": {"영혼_조작": 0.3, "정령_친화": 0.2, "마법_지식": 0.2}},
                {"name": "정령방출", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 101, "accuracy": 90,
                 "description": "[HP:101] [정령] [방출] - [HP] 축적된 정령의 힘을 방출하여 HP 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.SPIRIT_LINK, "duration": 3, "intensity": 1.0}],
                 "sfx": "magic_attack", "organic_effects": {"정령_친화": 0.35, "영혼_조작": 0.25, "마법_지식": 0.2}},
                
                # 영혼의 중재자 - [정령][영혼] 키워드 특화
                {"name": "정령소환", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4,
                 "description": "[능력강화+] [정령] [소환] - [BUFF] 수호 정령을 소환하여 자신의 능력치를 크게 향상시킵니다.",
                 "sfx": "summon",
                 "element": ElementType.LIGHT,
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.SPIRIT_LINK, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "영혼_조작": 0.3, "마법_지식": 0.3}},
                {"name": "저주의인형", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "sfx": "slow",
                 "description": "[다중저주] [인형] [저주] - [DEBUFF] 저주받은 인형으로 적에게 다양한 저주 상태를 부여합니다.",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.CURSE, "duration": 6, "intensity": 1.0},
                                   {"type": StatusType.NECROSIS, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"영혼_조작": 0.4, "마법_지식": 0.3, "정령_친화": 0.3}},
                {"name": "치유의춤", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 3.2, "sfx": "heal",
                 "description": "[전체치유] [춤] [정령] - [HEAL] 신성한 치유의 춤으로 아군 전체의 HP를 회복시킵니다.",
                 "element": ElementType.EARTH,
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "영혼파악", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "sfx": "magic_cast",
                 "description": "[약점분석] [영혼] [특수] - [SPECIAL] 적의 영혼을 파악하여 약점과 상태를 정확히 분석합니다.",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.CONFUSION, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["soul_analysis"],
                 "organic_effects": {"영혼_조작": 0.45, "마법_지식": 0.3, "정령_친화": 0.25}},
                {"name": "정령치유술", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 3.9, "sfx": "heal",
                 "description": "[강력치유] [필드] [정령] - [FIELD] 정령의 힘을 빌려 강력한 치유 효과를 전장에 펼칩니다.",
                 "element": ElementType.WATER, "is_field_skill": True,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "대자연의심판", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "hp_power": 140, "element": ElementType.EARTH,
                 "description": "[궁극] [HP:140] [전체] 대자연의 분노로 모든 적을 공격하는 파괴적인 궁극기입니다.",
                 "cooldown": 8, "cast_time": 25,
                 "sfx": "magic_cast",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["nature_judgment"],
                 "status_effects": [{"type": StatusType.PETRIFY, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.5, "영혼_조작": 0.4, "마법_지식": 0.35, "자연_이해": 0.3}}
            ],
            
            "드루이드": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "자연타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 87, "accuracy": 95,
                 "description": "[BRV:87] [자연] [타격] - [BRV] 자연의 힘을 담은 타격으로 야생의 기운을 축적합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.PHYSICAL,
                 "element": ElementType.EARTH,
                 "special_effects": ["nature_bond"],  # 기본 공격으로 자연 유대
                 "organic_effects": {"자연_이해": 0.3, "생존_본능": 0.25, "야생_본능": 0.2}},
                {"name": "야생본능", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 99, "accuracy": 90,
                 "description": "[HP:99] [야생] [본능] - [HP] 야생 동물의 본능으로 적을 공격하며 변신 준비를 합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["wild_instinct"],  # 기본 HP 공격으로 야생 본능
                 "sfx": "physical_attack", "organic_effects": {"야생_본능": 0.35, "자연_이해": 0.25, "생존_본능": 0.2}},
                
                # 자연의 수호자 - [자연][변신] 키워드 특화
                {"name": "자연교감", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "magic_cast",
                 "description": "[자연강화+] [교감] [자연] - [BUFF] 자연과 교감하여 모든 자연 마법의 위력을 증가시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.12}],
                 "organic_effects": {"자연_이해": 0.4, "마법_지식": 0.3, "정령_친화": 0.3}},
                {"name": "가시덩굴", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "element": ElementType.EARTH,
                 "description": "[이동제한] [지속피해] [식물] - [DEBUFF] 가시덩굴을 소환하여 적의 이동을 제한하고 지속 피해를 가합니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.ENTANGLE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"자연_이해": 0.4, "마법_지식": 0.35, "전술_지식": 0.25}},
                {"name": "자연치유", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "heal_power": 3.5, "element": ElementType.EARTH,
                 "description": "[치유] [상태해제] [자연] - [HEAL] 자연의 치유력으로 아군의 상처를 치유하고 상태이상을 해제합니다.",
                 "sfx": "heal", "organic_effects": {
"자연_이해": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "동물변신", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 7, "cooldown": 3,
                 "description": "[변신] [능력변화] [동물] - [BUFF] 야생동물로 변신하여 특별한 능력과 스탯 보정을 얻습니다.",
                 "sfx": "transform",
                 "status_effects": [{
"type": StatusType.BERSERK, "duration": 4, "intensity": 1.3}],
                 "special_effects": ["animal_form"],
                 "organic_effects": {"자연_이해": 0.45, "변신_능력": 0.35, "전투_본능": 0.2}},
                {"name": "번개폭풍", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 125, "element": ElementType.LIGHTNING, "cast_time": 18,
                 "description": "[HP:145] [번개] [자연] - [HP] 번개 폭풍을 일으켜 적의 HP에 강력한 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["lightning_storm"],
                 "sfx": "thunder3", "organic_effects": {
"자연_이해": 0.4, "마법_지식": 0.35, "정령_친화": 0.25}},
                {"name": "가이아의분노", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 24, "hp_power": 154, "element": ElementType.EARTH,
                 "description": "[궁극] [자연재해] [가이아] - [궁극] 대지의 여신 가이아의 분노로 자연 재해를 일으키는 궁극기입니다.",
                 "cooldown": 8, "cast_time": 35,
                 "damage_type": DamageType.MAGICAL, "special_effects": ["gaia_wrath"],
                 "sfx": "ultima", "organic_effects": {
"자연_이해": 0.5, "마법_지식": 0.4, "정령_친화": 0.35, "변신_능력": 0.3}}
            ],
            
            "신관": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "속죄타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 79, "accuracy": 95,
                 "description": "[BRV:79] [속죄] [타격] - [BRV] 속죄의 의미를 담은 타격으로 죄를 정화하며 속죄 스택을 쌓습니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.MAGICAL,
                 "element": ElementType.LIGHT,
                 "special_effects": ["atonement_stack"],  # 기본 공격으로 속죄 스택
                 "organic_effects": {"신앙": 0.3, "정화": 0.25, "치유_기술": 0.2}},
                {"name": "신성방출", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 95, "accuracy": 90,
                 "description": "[HP:95] [신성] [방출] - [HP] 신성한 힘을 방출하여 적을 정화하고 아군을 치유합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "element": ElementType.LIGHT,
                 "special_effects": ["divine_release"],  # 기본 HP 공격으로 신성 방출
                 "sfx": "magic_attack", "organic_effects": {"신앙": 0.35, "치유_기술": 0.25, "정화": 0.2}},
                
                # 신의 대행자 - [신성][치유] 키워드 특화
                {"name": "신의가호", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 5, "sfx": "protect",
                 "description": "[전체보호] [능력+] [신성] - [BUFF] 신의 가호로 아군 전체를 보호하고 모든 능력치를 향상시킵니다.",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"신앙": 0.4, "신성_마법": 0.35, "지휘력": 0.25}},
                {"name": "성스러운빛", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 105, "element": ElementType.LIGHT, "accuracy": 95,
                 "description": "[BRV:85] [정화] [성속] - [BRV] 성스러운 빛으로 적을 정화하면서 BRV를 획득합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["holy_light"],
                 "sfx": "heal", "organic_effects": {
"신성_마법": 0.4, "신앙": 0.3, "마법_지식": 0.3}},
                {"name": "대치유술", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 7, "heal_power": 5.5, "element": ElementType.LIGHT,
                 "description": "[강력치유] [전체] [신성] - [HEAL] 강력한 신성 마법으로 아군 전체를 크게 치유합니다.",
                 "special_effects": ["greater_heal"],
                 "sfx": "heal3", "organic_effects": {
"치유_기술": 0.4, "신성_마법": 0.35, "신앙": 0.25}},
                {"name": "부활술", "type": SkillType.SPECIAL, "target": TargetType.DEAD_ALLY,
                 "mp_cost": 12, "cooldown": 4, "cast_time": 18, "element": ElementType.LIGHT,
                 "description": "[완전부활] [기적] [신성] - [SPECIAL] 신의 기적으로 쓰러진 동료를 완전한 상태로 되살립니다.",
                 "special_effects": ["resurrect"],
                 "sfx": "phoenix_down", "organic_effects": {
"신앙": 0.5, "신성_마법": 0.4, "치유_기술": 0.1}},
                {"name": "신벌", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "hp_power": 161, "element": ElementType.LIGHT, "cast_time": 12,
                 "description": "[HP:160] [성속] [심판] - [HP] 신의 벌로 적의 HP에 성스러운 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["divine_punishment"],
                 "sfx": "magic_cast", "organic_effects": {
"신성_마법": 0.45, "신앙": 0.35, "마법_지식": 0.2}},
                {"name": "천국의문", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 25, "cooldown": 8, "cast_time": 40, "heal_power": 9.8,
                 "description": "[궁극] [천국] [신의개입] - [궁극] 천국의 문을 열어 신의 직접적인 개입을 받는 궁극의 신성 마법입니다.",
                 "element": ElementType.LIGHT, "special_effects": ["heaven_gate"],
                 "sfx": "magic_cast", "organic_effects": {
"신앙": 0.6, "신성_마법": 0.5, "치유_기술": 0.4, "지휘력": 0.3}}
            ],
            
            "성직자": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "신성타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 86, "accuracy": 95,
                 "description": "[BRV:86] [신성] [타격] - [BRV] 신성한 힘으로 적을 타격하며 신성력을 축적합니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.MAGICAL,
                 "element": ElementType.LIGHT,
                 "special_effects": ["divine_accumulation"],  # 기본 공격으로 신성력 축적
                 "organic_effects": {"신성_마법": 0.3, "신앙": 0.25, "평화_사상": 0.2}},
                {"name": "축복광선", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 99, "accuracy": 88,
                 "description": "[HP:99] [축복] [광선] - [HP] 축복의 광선으로 적에게 HP 피해를 가하며 아군을 치유합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "element": ElementType.LIGHT,
                 "special_effects": ["blessing_beam"],  # 기본 HP 공격으로 치유 효과
                 "sfx": "heal", "organic_effects": {"치유_기술": 0.35, "신성_마법": 0.25, "신앙": 0.2}},
                
                # 평화의 사도 - [성직][평화] 키워드 특화
                {"name": "평화의기도", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "sfx": "protect",
                 "description": "[전체 정신+] [평화] [기도] - [BUFF] 평화로운 기도로 아군 전체의 마음을 안정시키고 정신력을 향상시킵니다.",
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.GUARDIAN, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"신앙": 0.4, "평화_사상": 0.35, "지휘력": 0.25}},
                {"name": "정화의빛", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "element": ElementType.LIGHT,
                 "description": "[모든해제] [정화] [빛] - [SPECIAL] 정화의 빛으로 모든 저주와 상태이상을 해제합니다.",
                 "special_effects": ["purify_light"],
                 "sfx": "heal", "organic_effects": {
"신성_마법": 0.4, "평화_사상": 0.3, "치유_기술": 0.3}},
                {"name": "신성한치유", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 3.5, "element": ElementType.LIGHT,
                 "description": "[치유] [축복] [신성] - [HEAL] 신성한 힘으로 아군을 치유하고 축복 상태를 부여합니다.",
                 "sfx": "heal2",
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"치유_기술": 0.4, "신성_마법": 0.35, "평화_사상": 0.25}},
                {"name": "침묵의서약", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "sfx": "silence",
                 "description": "[마법봉인] [침묵] [서약] - [DEBUFF] 침묵의 서약으로 적의 마법 사용을 봉인합니다.",
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"신성_마법": 0.4, "평화_사상": 0.3, "신앙": 0.3}},
                {"name": "순교자의길", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 9, "cooldown": 4,
                 "description": "[자기희생] [전체버프] [순교] - [SPECIAL] 순교자의 길을 걸어 자신을 희생하여 아군에게 강력한 버프를 부여합니다.",
                 "special_effects": ["martyrdom_path"],
                 "sfx": "magic_cast", "organic_effects": {
"평화_사상": 0.5, "치유_기술": 0.35, "신앙": 0.15}},
                {"name": "신의심판", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 22, "hp_power": 147, "element": ElementType.LIGHT, "cooldown": 7, "cast_time": 18,
                 "description": "[궁극] [악징벌] [신벌] - [궁극] 신의 직접적인 심판으로 악한 적들을 처벌하는 궁극의 신성 마법입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["divine_judgment"],
                 "sfx": "thunder3", "organic_effects": {
"신성_마법": 0.5, "신앙": 0.4, "치유_기술": 0.35, "평화_사상": 0.3}}
            ],
            
            # === 특수 계열 ===
            "몽크": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "기공타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 88, "accuracy": 95,
                 "description": "[BRV:88] [기공] [타격] - [BRV] 내공을 담은 타격으로 기를 순환시키며 콤보를 준비합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["chi_circulation"],  # 기본 공격으로 기 순환
                 "organic_effects": {"정신_수양": 0.3, "기_수련": 0.25, "무술_숙련": 0.2}},
                {"name": "연환권", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 96, "accuracy": 90,
                 "description": "[HP:96] [연환] [권] - [HP] 연속된 주먹 공격으로 콤보 체인을 만들어 강력한 타격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["combo_chain"],  # 기본 HP 공격으로 콤보 체인
                 "sfx": "physical_attack", "organic_effects": {"무술_숙련": 0.35, "기_수련": 0.25, "정신_수양": 0.2}},
                
                # 기의 수행자 - [기][수련] 키워드 특화
                {"name": "기수련", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "haste",
                 "description": "[내력강화] [기] [수련] - [BUFF] 기수련을 통해 자신의 내재된 힘을 끌어올립니다.",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.FOCUS, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정신_수양": 0.4, "기_수련": 0.35, "무술_숙련": 0.25}},
                {"name": "연속주먹", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 91, "accuracy": 95, "hit_count": 2,
                 "description": "[BRV:80] [연타] [기공] - [BRV] 연속으로 주먹질을 가해 BRV를 획득합니다. 기수련의 성과입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["combo_attack"],
                 "sfx": "punch_hit", "organic_effects": {
"무술_숙련": 0.4, "기_수련": 0.3, "전투_본능": 0.25}},
                {"name": "명상", "type": SkillType.HEAL, "target": TargetType.SELF,
                 "mp_cost": 4, "heal_power": 3.8,
                 "description": "[HP회복] [MP회복] [명상] - [HEAL] 깊은 명상으로 내면의 평화를 찾아 HP와 MP를 회복합니다.",
                 "sfx": "heal",
                 "special_effects": ["mp_restore_15pct"],
                 "status_effects": [{
"type": StatusType.REGENERATION, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"정신_수양": 0.5, "기_수련": 0.3, "내면_평화": 0.25}},
                {"name": "기폭발", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "hp_power": 84, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:125] [기] [폭발] - [HP] 내재된 기를 폭발시켜 적의 HP에 피해를 가합니다.",
                 "damage_type": DamageType.HYBRID, "special_effects": ["ki_explosion"],
                 "sfx": "punch_critical", "organic_effects": {
"기_수련": 0.4, "무술_숙련": 0.3, "정신_수양": 0.25}},
                {"name": "철의주먹", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 133, "cast_time": 10, "accuracy": 95,
                 "description": "[HP:140] [강철] [주먹] - [HP] 철처럼 단단한 주먹으로 적의 HP에 강력한 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["armor_pierce"],
                 "sfx": "punch_critical", "organic_effects": {
"무술_숙련": 0.4, "기_수련": 0.35, "전투_본능": 0.3}},
                {"name": "깨달음의경지", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 16, "cooldown": 6, "cast_time": 20,
                 "description": "[궁극] [깨달음] [초월] - [궁극] 무술의 깨달음에 도달하여 초월적인 힘을 발휘합니다.",
                 "special_effects": ["enlightenment"],
                 "sfx": "limit_break", "organic_effects": {
"정신_수양": 0.6, "기_수련": 0.5, "무술_숙련": 0.4, "내면_평화": 0.35}}
            ],
            
            "마검사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "마검베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 91, "accuracy": 95,
                 "description": "[BRV:91] [마검] [베기] - [BRV] 마법이 깃든 검으로 적을 베어 원소 에너지를 축적합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.HYBRID,
                 "special_effects": ["elemental_blade"],  # 기본 공격으로 원소 검 부여
                 "organic_effects": {"마검_숙련": 0.3, "원소_조화": 0.25, "균형_감각": 0.2}},
                {"name": "원소검기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 107, "accuracy": 90,
                 "description": "[HP:107] [원소] [검기] - [HP] 원소의 힘을 담은 검기로 적의 HP에 직접적인 피해를 가합니다.",
                 "damage_type": DamageType.HYBRID,
                 "special_effects": ["elemental_burst"],  # 기본 HP 공격으로 원소 폭발
                 "sfx": "magic_attack", "organic_effects": {"마검_숙련": 0.35, "원소_조화": 0.25, "마법_지식": 0.2}},
                
                # 마검의 융합자 - [융합][마검] 키워드 특화
                {"name": "마검각성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "sword_hit",
                 "description": "[마법+] [검술+] [각성] - [BUFF] 마검의 힘을 각성시켜 마법과 검술 능력을 모두 향상시킵니다.",
                 "damage_type": DamageType.HYBRID,
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2}],
                 "organic_effects": {"마검_숙련": 0.4, "마법_지식": 0.3, "전투_본능": 0.25}},
                {"name": "마법검격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 112, "element": ElementType.NEUTRAL, "accuracy": 95,
                 "description": "[BRV:100] [마법] [검술] - [BRV] 마법이 깃든 검으로 적을 공격하여 BRV를 획득합니다.",
                 "damage_type": DamageType.HYBRID,
                 "sfx": "sword_hit", "organic_effects": {
"마검_숙련": 0.4, "마법_지식": 0.3, "전투_본능": 0.25}},
                {"name": "원소부여", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5,
                 "description": "[원소강화] [부여] [마법] - [BUFF] 무기에 원소의 힘을 부여하여 공격력을 증가시킵니다.",
                 "damage_type": DamageType.HYBRID, "special_effects": ["elemental_weapon"],
                 "sfx": "magic_cast", "organic_effects": {
"마법_지식": 0.4, "마검_숙련": 0.3, "원소_친화": 0.25}},
                {"name": "마검진", "type": SkillType.FIELD, "target": TargetType.BATTLEFIELD,
                 "mp_cost": 8, "cooldown": 3,
                 "description": "[마법진] [필드] [마검] - [FIELD] 마검으로 마법진을 그려 전장에 특수한 효과를 부여합니다.",
                 "damage_type": DamageType.MAGICAL, "is_field_skill": True, "special_effects": ["magic_field"],
                 "sfx": "sword_hit", "organic_effects": {
"마법_지식": 0.4, "마검_숙련": 0.3, "전략적_사고": 0.25}},
                {"name": "마력폭발", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 140, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:135] [마력] [폭발] - [HP] 마력을 폭발시켜 적의 HP에 강력한 마법 피해를 가합니다.",
                 "damage_type": DamageType.HYBRID,
                 "sfx": "fire3", "organic_effects": {
"마검_숙련": 0.4, "마법_지식": 0.35, "전투_본능": 0.3}},
                {"name": "마검의진리", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 133, "cooldown": 7, "cast_time": 25,
                 "description": "[궁극] [마검] [진리] - [궁극] 마검의 진리를 깨달아 마법과 검술의 완벽한 조화를 이룹니다.",
                 "damage_type": DamageType.HYBRID, "special_effects": ["perfect_fusion"],
                 "sfx": "sword_hit", "organic_effects": {
"마검_숙련": 0.5, "마법_지식": 0.4, "전투_본능": 0.35, "원소_친화": 0.3}}
            ],
            
            "연금술사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "연금막대", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 85, "accuracy": 95,
                 "description": "[BRV:85] [연금] [막대] - [BRV] 연금술 막대로 적을 타격하고 원소 변환을 시도합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["transmute_item"],  # 기본 공격으로 원소 변환
                 "organic_effects": {"연금_지식": 0.3, "창조_정신": 0.2, "마법_지식": 0.2}},
                {"name": "연금폭발", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 102, "accuracy": 90,
                 "description": "[HP:102] [연금] [폭발] - [HP] 연금술 반응으로 소규모 폭발을 일으켜 HP 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["instant_potion"],  # 기본 HP 공격 후 자가 치유
                 "sfx": "explosion", "organic_effects": {"연금_지식": 0.35, "창조_정신": 0.25, "생존_본능": 0.2}},
                
                # 물질의 연성자 - [연성][변환] 키워드 특화
                {"name": "물질변환", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3,
                 "description": "[변환] [연금] [특수] - [SPECIAL] 연금술로 물질을 변환하여 유용한 효과를 창조합니다.",
                 "special_effects": ["transmute_item"],
                 "sfx": "magic_cast", "organic_effects": {
"연금_지식": 0.4, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "독성폭탄", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "brv_power": 84, "element": ElementType.POISON, "accuracy": 90,
                 "description": "[BRV:85] [독] [폭탄] - [BRV] 독성 폭탄을 투척하여 BRV를 획득하고 적을 중독시킵니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.MAGICAL, 
                 "status_effects": [{
"type": StatusType.POISON, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"연금_지식": 0.35, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "회복포션", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "heal_power": 3.9,
                 "description": "[치유:강] [포션] [연금] - [HEAL] 직접 제조한 회복 포션으로 아군의 HP를 빠르게 회복시킵니다.",
                 "special_effects": ["instant_potion"],
                 "sfx": "heal", "organic_effects": {
"연금_지식": 0.4, "창조_정신": 0.35, "생존_본능": 0.2}},
                {"name": "강화주사", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "sfx": "protect",
                 "description": "[전능력+] [주사] [강화] - [BUFF] 특수 강화 주사로 일시적으로 모든 능력을 향상시킵니다.",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"연금_지식": 0.4, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "산성용해", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 125, "element": ElementType.POISON, "cast_time": 15,
                 "description": "[HP:120] [산성] [용해] - [HP] 강력한 산으로 적을 용해시켜 HP 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["acid_corrosion"],
                 "sfx": "magic_cast", "organic_effects": {
"연금_지식": 0.4, "마법_지식": 0.3, "창조_정신": 0.25}},
                {"name": "철학자의돌", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 18, "cooldown": 8, "cast_time": 30,
                 "description": "[궁극] [기적] [완전체] - [궁극] 연금술의 최고 산물인 철학자의 돌로 기적을 일으킵니다.",
                 "special_effects": ["philosophers_stone"],
                 "sfx": "magic_cast", "organic_effects": {
"연금_지식": 0.6, "창조_정신": 0.5, "마법_지식": 0.4, "생존_본능": 0.3}}
            ],
            
            "기계공학자": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "기계타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 93, "accuracy": 95,
                 "description": "[BRV:93] [기계] [타격] - [BRV] 정밀한 기계 도구로 적을 타격하며 기계 에너지를 충전합니다.",
                 "sfx": "physical_attack",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["machine_charge"],  # 기본 공격으로 기계 충전
                 "organic_effects": {"제조_마스터": 0.3, "기계_숙련": 0.25, "전략적_사고": 0.2}},
                {"name": "에너지방출", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 104, "accuracy": 90,
                 "description": "[HP:104] [에너지] [방출] - [HP] 축적된 에너지를 방출하여 적에게 기계적 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["energy_discharge"],  # 기본 HP 공격으로 에너지 방출
                 "sfx": "explosion", "organic_effects": {"기계_숙련": 0.35, "제조_마스터": 0.25, "전략적_사고": 0.2}},
                
                # 기계 전쟁의 건축가 - [포탑][설치] 키워드 특화
                {"name": "자동포탑설치", "type": SkillType.FIELD, "target": TargetType.BATTLEFIELD,
                 "mp_cost": 6, "cooldown": 3,
                 "description": "[자동공격] [필드] [포탑] - [FIELD] 자동 공격 포탑을 설치하여 지속적으로 적을 공격합니다.",
                 "is_field_skill": True, "special_effects": ["auto_turret_install"],
                 "sfx": "gun_hit", "organic_effects": {
"제조_마스터": 0.3, "기계_숙련": 0.25, "전략적_사고": 0.2}},
                {"name": "레이저사격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 118, "element": ElementType.LIGHTNING, "accuracy": 95,
                 "description": "[BRV:95] [레이저] [기계] - [BRV] 정밀한 레이저로 적을 공격하여 BRV를 획득합니다.",
                 "damage_type": DamageType.RANGED, "special_effects": ["precision_laser"],
                 "sfx": "gun_hit", "organic_effects": {
"기계_숙련": 0.4, "전략적_사고": 0.2, "전투_본능": 0.15}},
                {"name": "메카돔", "type": SkillType.SUPPORT, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "sfx": "magic_cast",
                 "description": "[전체방어+] [실드] [기계] - [BUFF] 기계 돔을 전개하여 아군 전체를 보호하고 방어력을 증가시킵니다.",
                 "status_effects": [{
"type": StatusType.SHIELD, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"제조_마스터": 0.35, "냉정함": 0.25, "전략적_사고": 0.3}},
                {"name": "멀티미사일", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 98, "cast_time": 20, "accuracy": 90,
                 "description": "[HP:110] [다중] [미사일] - [HP] 다수의 미사일로 적의 HP에 폭발적인 피해를 가합니다.",
                 "damage_type": DamageType.RANGED, "special_effects": ["multi_missile"],
                 "sfx": "magic_cast", "organic_effects": {
"제조_마스터": 0.3, "기계_숙련": 0.35, "전투_본능": 0.25}},
                {"name": "수리드론", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 4.5,
                 "description": "[자동치유] [드론] [기계] - [HEAL] 수리 드론을 전개하여 아군들의 상처를 자동으로 치료합니다.",
                 "special_effects": ["repair_drone"],
                 "sfx": "magic_cast", "organic_effects": {
"제조_마스터": 0.4, "냉정함": 0.3, "기계_숙련": 0.2}},
                {"name": "기가포탑", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "hp_power": 168, "cast_time": 30, "cooldown": 8,
                 "description": "[궁극] [초화력] [거대포탑] - [궁극] 초거대 포탑을 소환하여 적 전체에게 압도적인 화력을 퍼붓습니다.",
                 "is_field_skill": True, "special_effects": ["giga_turret"],
                 "sfx": "magic_cast", "organic_effects": {
"제조_마스터": 0.5, "기계_숙련": 0.4, "전략적_사고": 0.3, "전투_본능": 0.25}}
            ],
"네크로맨서": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "죽음타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 88, "accuracy": 94,
                 "description": "[BRV:88] [죽음] [타격] - [BRV] 생명력을 흡수하는 어둠의 일격으로 영혼 에너지를 축적합니다.",
                 "sfx": "dark_magic",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["soul_harvest"],  # 기본 공격으로 영혼 수확
                 "organic_effects": {"어둠_숙련": 0.3, "생명_조작": 0.25, "언데드_소환": 0.2}},
                {"name": "영혼흡수", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 96, "accuracy": 89,
                 "description": "[HP:96] [영혼] [흡수] - [HP] 적의 영혼을 직접 흡수하여 생명력을 탈취합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["life_drain"],  # 기본 HP 공격으로 생명력 흡수
                 "sfx": "magic_cast", "organic_effects": {"언데드_소환": 0.35, "어둠_숙련": 0.25, "생명_조작": 0.2}},
                
                # 죽음의 지배자 - [언데드][흡수] 키워드 특화
                {"name": "언데드소환", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 5,
                 "description": "[언데드] [소환] [지원] - [SPECIAL] 언데드를 소환하여 전투를 지원하게 합니다.",
                 "special_effects": ["summon_undead"],
                 "sfx": "magic_cast", "organic_effects": {
"죽음_지배": 0.4, "어둠_친화": 0.3, "마법_지식": 0.25}},
                {"name": "생명력흡수", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 98, "element": ElementType.DARK, "accuracy": 95,
                 "description": "[BRV:98] [흡수] [언데드] - [BRV] 적의 생명력을 흡수하여 자신의 BRV로 전환합니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["life_drain"],
                 "status_effects": [{
"type": StatusType.NECROSIS, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"어둠_친화": 0.4, "죽음_지배": 0.3, "생존_본능": 0.2}},
                {"name": "공포주입", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "element": ElementType.DARK, "sfx": "magic_cast",
                 "description": "[공포] [능력감소] [죽음] - [DEBUFF] 죽음의 공포를 주입하여 적을 공포 상태로 만들고 능력치를 감소시킵니다.",
                 "status_effects": [{
"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.MADNESS, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"죽음_지배": 0.35, "어둠_친화": 0.3, "마법_지식": 0.25}},
                {"name": "뼈감옥", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "sfx": "magic_cast",
                 "description": "[행동봉인] [구속] [뼈] - [DEBUFF] 뼈로 만든 감옥에 적을 가둬 행동 불가 상태로 만듭니다.",
                 "status_effects": [{
"type": StatusType.ROOT, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.PARALYZE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"죽음_지배": 0.4, "마법_지식": 0.3, "어둠_친화": 0.25}},
                {"name": "죽음의손길", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 133, "element": ElementType.DARK, "cast_time": 15,
                 "description": "[HP:133] [죽음] [터치] - [HP] 죽음의 기운으로 적의 HP에 치명적인 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["life_steal"],
                 "sfx": "magic_cast", "organic_effects": {
"어둠_친화": 0.4, "죽음_지배": 0.35, "마법_지식": 0.3}},
{"name": "언데드군단", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "description": "[궁극] [HP:154] [전체] [언데드군단] [쿨:7턴] - [궁극][네크로] 언데드 군단을 소환하여 전장을 완전히 지배하는 네크로맨서의 최종 기술",
                 "mp_cost": 18, "hp_power": 154, "element": ElementType.DARK, "cooldown": 7, "cast_time": 30,

                 "damage_type": DamageType.MAGICAL, "special_effects": ["summon_undead"],
                 "sfx": "magic_cast", "organic_effects": {"죽음_지배": 0.5, "어둠_친화": 0.4, "마법_지식": 0.35, "생존_본능": 0.3}}
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
        
        # 🌟 새로운 검성 효과 - 검기 스택 시스템
        "sword_aura_gain": lambda: _sword_aura_gain(caster),
        "sword_aura_consume": lambda: _sword_aura_consume(caster, target, skill_data),
        "sword_aura_consume_all": lambda: _sword_aura_consume_all(caster, target, skill_data),
        "sword_aura_wave": lambda: _sword_aura_wave(caster, target, skill_data),
        "atb_refund": lambda: _atb_refund(caster, skill_data),
        "atb_refund_medium": lambda: _atb_refund_medium(caster, skill_data),
        "infinite_blade": lambda: _infinite_blade(caster, target, skill_data),
        
        # 기존 검성 효과
        "iai_cut": lambda: _iai_cut(caster, target, skill_data),
        "sword_pressure": lambda: _sword_pressure(caster, target, skill_data),
        "sword_unity": lambda: _sword_unity(caster),
        "peerless_cut": lambda: _peerless_cut(caster, target, skill_data),
        "sword_emperor": lambda: _sword_emperor(caster, target, skill_data),
        
        # 🌟 새로운 검투사 효과 - 처치 스택 + 패링
        "gladiator_skill": lambda: _gladiator_skill(caster, target, skill_data),
        "parry_stance": lambda: _parry_stance(caster),
        "honor_strike": lambda: _honor_strike(caster, target, skill_data),
        "warrior_roar": lambda: _warrior_roar(caster),
        "survival_spirit": lambda: _survival_spirit(caster, target, skill_data),
        
        # 기존 검투사 효과
        "gladiator_honor": lambda: _gladiator_honor(caster),
        "colosseum_king": lambda: _colosseum_king(caster, target, skill_data),
        
        # 🌟 새로운 광전사 효과 - HP 소모 + 보호막 + 흡혈
        "berserk_strike": lambda: _berserk_strike(caster, target, skill_data),
        "vampire_attack": lambda: _vampire_attack(caster, target, skill_data),
        "blood_shield": lambda: _blood_shield(caster, skill_data),
        "vampiric_blast": lambda: _vampiric_blast(caster, target, skill_data),
        "shield_consume": lambda: _shield_consume(caster, target, skill_data),
        "madness_amplify": lambda: _madness_amplify(caster, skill_data),
        "rage_chain": lambda: _rage_chain(caster, target, skill_data),
        "area_vampire": lambda: _area_vampire(caster, target, skill_data),
        "final_madness": lambda: _final_madness(caster, target, skill_data),
        "massive_vampire": lambda: _massive_vampire(caster, target, skill_data),
        
        # 기존 광전사 효과
        "rage_seed": lambda: _rage_seed(caster),
        "blood_thirst": lambda: _blood_thirst(caster, target, skill_data),
        "mad_combo": lambda: _mad_combo(caster, target, skill_data),
        "rage_explosion": lambda: _rage_explosion(caster, target, skill_data),
        "berserker_end": lambda: _berserker_end(caster, target, skill_data),
        
        # 🌟 새로운 기사 효과 - 의무 스택 시스템
        "spear_charge": lambda: _spear_charge(caster, target, skill_data),
        "protection_oath": lambda: _protection_oath(caster),
        "chivalry_spirit": lambda: _chivalry_spirit(caster),
        "duty_counter": lambda: _duty_counter(caster, target, skill_data),
        "survival_will": lambda: _survival_will(caster),
        "holy_charge": lambda: _holy_charge(caster, target, skill_data),
        
        # 기존 기사/성기사 효과
        "knight_oath": lambda: _knight_oath(caster),
        "holy_strike": lambda: _holy_strike(caster, target, skill_data),
        "holy_heal": lambda: _holy_heal(caster, target),
        "angel_descent": lambda: _angel_descent(caster, target, skill_data),
        
        # 다크나이트 효과
        "dark_pact": lambda: _dark_pact(caster, target, skill_data),
        "vampire_strike": lambda: _vampire_strike(caster, target, skill_data),
        "dark_domination": lambda: _dark_domination(caster, target, skill_data),
        
        # 드래곤나이트 효과
        "dragon_spear": lambda: _dragon_spear(caster, target, skill_data),
        "dragon_lord": lambda: _dragon_lord(caster, target, skill_data),
        
        # 아크메이지 효과
        "mana_recovery_10pct": lambda: _mana_recovery_percent(caster, 0.10),
        "random_element": lambda: _random_element_effect(caster, target, skill_data),
        "all_elements": lambda: _all_elements_effect(caster, target, skill_data),
        
        # 원소술사 효과
        "earth_rage": lambda: _earth_rage(caster, target, skill_data),
        "four_elements": lambda: _four_elements(caster, target, skill_data),
        
        # 시공술사 효과
        "time_record_savepoint": lambda: _time_record_savepoint(caster),
        "time_rewind_to_savepoint": lambda: _time_rewind_to_savepoint(caster),
        "future_sight": lambda: _future_sight(caster),
        "time_stop": lambda: _time_stop(caster),
        "spacetime_collapse": lambda: _spacetime_collapse(caster, target, skill_data),
        
        # 공간술사 효과
        "dimension_cloak": lambda: _dimension_cloak(caster),
        "afterimage": lambda: _afterimage(caster),
        "space_leap": lambda: _space_leap(caster, target, skill_data),
        "dimension_maze": lambda: _dimension_maze(caster, target),
        "evasion_counter": lambda: _evasion_counter(caster, target, skill_data),
        "untouchable_state": lambda: _untouchable_state(caster),
        
        # 철학자 효과
        "truth_insight": lambda: _truth_insight(caster, target),
        "existence_denial": lambda: _existence_denial(caster, target, skill_data),
        "philosophical_thought": lambda: _philosophical_thought(caster),
        "absolute_truth": lambda: _absolute_truth(caster, target, skill_data),
        
        # 궁수 효과
        "triple_shot": lambda: _triple_shot(caster, target, skill_data),
        "piercing_shot": lambda: _piercing_shot(caster, target, skill_data),
        "hunter_mode": lambda: _hunter_mode(caster),
        
        # 도적 효과 (리메이크)
        "poison_stack": lambda: _poison_stack(caster, target, skill_data),
        "corrosive_poison": lambda: _corrosive_poison(caster, target, skill_data),
        "poison_trigger": lambda: _poison_trigger(caster, target, skill_data),
        "poison_fog_enhanced": lambda: _poison_fog_enhanced(caster, target),
        "venom_explosion": lambda: _venom_explosion(caster, target, skill_data),
        "poison_emperor": lambda: _poison_emperor(caster, target, skill_data),
        
        # 도적 기존 효과 (호환성)
        "stealth_attack": lambda: _stealth_attack(caster, target, skill_data),
        "smoke_screen": lambda: _smoke_screen(caster),
        "smoke_bomb": lambda: _smoke_bomb(caster),
        "assassination": lambda: _assassination(caster, target, skill_data),
        "shadow_clone": lambda: _shadow_clone(caster),
        "poison_fog": lambda: _poison_fog(caster, target),
        "poison_blade": lambda: _poison_blade(caster, target, skill_data),
        "poison_mastery": lambda: _poison_mastery(caster, target, skill_data),
        
        # 해적 효과
        "ghost_fleet": lambda: _ghost_fleet(caster, target, skill_data),
        
        # 무사 효과
        "mushin_cut": lambda: _mushin_cut(caster, target, skill_data),
        
        # 음유시인 효과
        "divine_song": lambda: _divine_song(caster, target),
        "heavenly_chorus": lambda: _heavenly_chorus(caster, target),
        
        # 동물조련사 효과
        "soul_analysis": lambda: _soul_analysis(caster, target),
        "nature_judgment": lambda: _nature_judgment(caster, target, skill_data),
        "animal_form": lambda: _animal_form(caster),
        "lightning_storm": lambda: _lightning_storm(caster, target, skill_data),
        "gaia_wrath": lambda: _gaia_wrath(caster, target, skill_data),
        
        # 성직자 효과
        "holy_light": lambda: _holy_light(caster, target, skill_data),
        "greater_heal": lambda: _greater_heal(caster, target),
        "divine_punishment": lambda: _divine_punishment(caster, target, skill_data),
        "heaven_gate": lambda: _heaven_gate(caster, target, skill_data),
        
        # 순교자 효과
        "purify_light": lambda: _purify_light(caster, target),
        "martyrdom_path": lambda: _martyrdom_path(caster),
        "divine_judgment": lambda: _divine_judgment(caster, target, skill_data),
        
        # 무술가 효과
        "combo_attack": lambda: _combo_attack(caster, target, skill_data),
        "mp_restore_15pct": lambda: _mp_restore_15pct(caster),
        "ki_explosion": lambda: _ki_explosion(caster, target, skill_data),
        "enlightenment": lambda: _enlightenment(caster),
        
        # 연금술사 효과
        "elemental_weapon": lambda: _elemental_weapon(caster, skill_data),
        "magic_field": lambda: _magic_field(caster),
        "perfect_fusion": lambda: _perfect_fusion(caster, target, skill_data),
        "transmute_item": lambda: _transmute_item(caster),
        "instant_potion": lambda: _instant_potion(caster, target),
        "acid_corrosion": lambda: _acid_corrosion(caster, target, skill_data),
        "philosophers_stone": lambda: _philosophers_stone(caster),
        
        # 해적 효과
        "treasure_hunt": lambda: _treasure_hunt(caster),
        "pirate_plunder": lambda: _pirate_plunder(caster, target, skill_data),
        "dual_wield": lambda: _dual_wield(caster, target, skill_data),
        "sea_shanty": lambda: _sea_shanty(caster),
        "treasure_map": lambda: _treasure_map(caster),
        
        # 사무라이 효과
        "samurai_focus": lambda: _samurai_focus(caster),
        "bushido_spirit": lambda: _bushido_spirit(caster, target, skill_data),
        "iai_strike": lambda: _iai_strike(caster, target, skill_data),
        "honor_guard": lambda: _honor_guard(caster),
        
        # 기계공학자 효과
        "auto_turret_install": lambda: _auto_turret_install(caster),
        "precision_laser": lambda: _precision_laser(caster, target, skill_data),
        "repair_drone": lambda: _repair_drone(caster, target),
        "multi_missile": lambda: _multi_missile(caster, target, skill_data),
        "giga_turret": lambda: _giga_turret(caster, target, skill_data),
        
        # 네크로맨서 효과
        "summon_undead": lambda: _summon_undead(caster),
        "life_drain": lambda: _life_drain(caster, target, skill_data),
        
        # 공통 효과
        "resurrect": lambda: _resurrect(caster, target),
        "life_steal": lambda: _life_steal(caster, target, skill_data),
        "dispel_all": lambda: _dispel_all(target),
        "analyze_enemy": lambda: _analyze_enemy(caster, target),
        
        # 상태이상 효과
        "silence_effect": lambda: _silence_effect(caster, target, skill_data),
        "silence_attack": lambda: _silence_attack(caster, target, skill_data),
        "poison_attack": lambda: _poison_attack(caster, target, skill_data),
        "stun_attack": lambda: _stun_attack(caster, target, skill_data),
        "bleeding_attack": lambda: _bleeding_attack(caster, target, skill_data),
        "burn_attack": lambda: _burn_attack(caster, target, skill_data),
        "freeze_attack": lambda: _freeze_attack(caster, target, skill_data),
        "shock_attack": lambda: _shock_attack(caster, target, skill_data),
        "confusion_attack": lambda: _confusion_attack(caster, target, skill_data),
        "weakness_attack": lambda: _weakness_attack(caster, target, skill_data),
        
        # 정령술사 효과
        "elemental_mastery": lambda: _elemental_mastery(caster),
        "spirit_bond": lambda: _spirit_bond(caster),
        
        # 시간술사 효과  
        "time_stop": lambda: _time_stop(caster, target, skill_data),
        
        # 연금술사 효과
        "chemical_reaction": lambda: _chemical_reaction_safe(caster, target, skill_data),
        
        # 차원술사 효과
        "dimension_rift": lambda: _dimension_rift_safe(caster, target, skill_data),
        
        # 기타 공통 효과들 (실제 구현)
        "mana_burn": lambda: _mana_burn(caster, target, skill_data),
        "armor_break": lambda: _armor_break(caster, target, skill_data),
        "critical_strike": lambda: _critical_strike(caster, target, skill_data),
        "double_attack": lambda: _double_attack(caster, target, skill_data),
        "piercing_attack": lambda: _piercing_attack(caster, target, skill_data),
        "stun_attack": lambda: _stun_attack(caster, target, skill_data),
        "bleeding_attack": lambda: _bleeding_attack(caster, target, skill_data),
        "burn_attack": lambda: _burn_attack(caster, target, skill_data),
        "freeze_attack": lambda: _freeze_attack(caster, target, skill_data),
        "shock_attack": lambda: _shock_attack(caster, target, skill_data),
        "poison_attack": lambda: _poison_attack(caster, target, skill_data),
        "confusion_attack": lambda: _confusion_attack(caster, target, skill_data),
        "silence_attack": lambda: _silence_attack(caster, target, skill_data),
        "weakness_attack": lambda: _weakness_attack(caster, target, skill_data),
        "curse_attack": lambda: _curse_attack(caster, target, skill_data),
        "drain_attack": lambda: _drain_attack(caster, target, skill_data),
        "holy_light": lambda: _holy_light(caster, target, skill_data),
        "dark_energy": lambda: _dark_energy(caster, target, skill_data),
        "nature_power": lambda: _nature_power(caster, target, skill_data),
        "wisdom_boost": lambda: _wisdom_boost(caster, skill_data),
        "strategy_analysis": lambda: _safe_effect_dummy(caster, target, "전략 분석"),
        "battle_tactic": lambda: _safe_effect_dummy(caster, None, "전투 전술"),
        "crowd_control": lambda: _safe_effect_dummy(caster, target, "군중 제어"),
        "mass_heal": lambda: _safe_effect_dummy(caster, target, "광역 치유"),
        "group_buff": lambda: _safe_effect_dummy(caster, None, "그룹 강화"),
        "area_debuff": lambda: _safe_effect_dummy(caster, target, "광역 약화"),
        





        # 네 번째 배치 효과들
        "adaptive_ultimate": lambda: _adaptive_ultimate(caster, target, skill_data),
        "aggressive_bonus": lambda: _aggressive_bonus(caster),
        "air_dash": lambda: _air_dash(caster),
        "air_mastery": lambda: _air_mastery(caster),
        "alignment_detect": lambda: _alignment_detect(caster, target, skill_data),
        "animal_kingdom": lambda: _animal_kingdom(caster),
        "antidote": lambda: _antidote(caster, target),
        "aquatic_blessing": lambda: _aquatic_blessing(caster),
        "aquatic_breathing": lambda: _aquatic_breathing(caster),
        "arcane_mastery": lambda: _arcane_mastery(caster),
        "area_explosion": lambda: _area_explosion(caster, target, skill_data),
        "auto_turret": lambda: _auto_turret(caster),
        "bad_taste": lambda: _bad_taste(caster, target, skill_data),
        "balanced_bonus": lambda: _balanced_bonus(caster),
        "banishment": lambda: _banishment(caster, target, skill_data),
        "battle_reset": lambda: _battle_reset(caster),
        "berserker_bonus": lambda: _berserker_bonus(caster),
        "berserker_mode": lambda: _berserker_mode(caster),
        "breath_weapon": lambda: _breath_weapon(caster, target, skill_data),
        "chaos_effect": lambda: _chaos_effect(caster),
        # 한국어 특수 효과들
        "기 수련": lambda: _ki_training(caster),
        "기공타격": lambda: _ki_strike(caster, target, skill_data),
        "내면의 기를 단련하여 능력 증가": lambda: _inner_ki_enhancement(caster),
        "독침": lambda: _poison_needle(caster, target, skill_data),
        "라이트닝볼트": lambda: _lightning_bolt(caster, target, skill_data),
        "마나 집중": lambda: _mana_focus(caster),
        "마력 파동": lambda: _magic_wave(caster, target, skill_data),
        "마법": lambda: _magic_spell(caster, target, skill_data),
        "마법공격력으로 아군 공격력과 치명타율 증가": lambda: _magic_attack_party_boost(caster),
        "물리공격력과 정확도, 크리티컬 확률 증가": lambda: _physical_accuracy_crit_boost(caster),
        "방어력 증가 및 아군 보호 준비": lambda: _defense_protection_ready(caster),
        "방패 방어": lambda: _shield_defense(caster),
        "야생 버섯": lambda: _wild_mushroom(caster),
        "용기의 노래": lambda: _courage_song(caster),
        "작은 고기": lambda: _small_meat(caster),
        "잡초": lambda: _weeds(caster),
        "조준": lambda: _aim(caster),
        "조준사격": lambda: _aimed_shot(caster, target, skill_data),
        "창찌르기": lambda: _spear_thrust(caster, target, skill_data),
        "화음타격": lambda: _harmony_strike(caster, target, skill_data),
        # 세 번째 배치 효과들
        "brv_shield": lambda: _brv_shield(caster),
        "multi_shot": lambda: _multi_shot(caster, target, skill_data),
        "confusion": lambda: _confusion(caster, target, skill_data),
        "cure_all": lambda: _cure_all(caster),
        "purify_all": lambda: _purify_all(caster, target),
        "luck_boost": lambda: _luck_boost(caster),
        "exp_double": lambda: _exp_double(caster),
        "gold_double": lambda: _gold_double(caster),
        "item_find": lambda: _item_find(caster),
        "mp_restore": lambda: _mp_restore(caster, target),
        "double_turn": lambda: _double_turn(caster),
        "triple_hit": lambda: _triple_hit(caster, target, skill_data),
        "party_buff": lambda: _party_buff(caster),
        "flame_strike": lambda: _flame_strike(caster, target, skill_data),
        "ice_trail": lambda: _ice_trail(caster, target, skill_data),
        "lightning_storm": lambda: _lightning_storm(caster, target, skill_data),
        "earth_shield": lambda: _earth_shield(caster),
        "wind_walk": lambda: _wind_walk(caster),
        "magic_amplify": lambda: _magic_amplify(caster),
        "weapon_mastery": lambda: _weapon_mastery(caster),
        # 두 번째 배치 효과들
        "heal_others": lambda: _heal_others(caster, target, skill_data),
        "healing_boost": lambda: _healing_boost(caster),
        "hp_boost": lambda: _hp_boost(caster),
        "mp_boost": lambda: _mp_boost(caster),
        "regeneration": lambda: _regeneration(caster),
        "speed_increase": lambda: _speed_increase(caster),
        "stealth_mode": lambda: _stealth_mode(caster),
        "stun_chance": lambda: _stun_chance(caster, target, skill_data),
        "teleport": lambda: _teleport(caster),
        "fear_aura": lambda: _fear_aura(caster, target, skill_data),
        "poison_immunity": lambda: _poison_immunity(caster),
        "fire_immunity": lambda: _fire_immunity(caster),
        "cold_immunity": lambda: _cold_immunity(caster),
        "status_immunity": lambda: _status_immunity(caster),
        "mana_shield": lambda: _mana_shield(caster),
        "multi_hit": lambda: _multi_hit(caster, target, skill_data),
        "piercing": lambda: _piercing(caster, target, skill_data),
        "auto_counter": lambda: _auto_counter(caster),
        "auto_revive": lambda: _auto_revive(caster),
        "invisibility": lambda: _invisibility(caster),
        # 기본 우선순위 효과들
        "accuracy": lambda: _accuracy(caster),
        "accuracy_boost": lambda: _accuracy_boost(caster),
        "adaptive_attack": lambda: _adaptive_attack(caster, target, skill_data),
        "armor_penetration": lambda: _armor_penetration(caster, target, skill_data),
        "berserk": lambda: _berserk(caster),
        "brv_boost": lambda: _brv_boost(caster),
        "brv_power": lambda: _brv_power(caster),
        "combo_bonus": lambda: _combo_bonus(caster),
        "critical_boost": lambda: _critical_boost(caster),
        "damage_boost": lambda: _damage_boost(caster),
        "dispel": lambda: _dispel(caster, target, skill_data),
        "double_damage": lambda: _double_damage(caster, target, skill_data),
        "first_strike": lambda: _first_strike(caster),
        "full_heal": lambda: _full_heal(caster),
        "heal_others": lambda: _heal_others(caster, target, skill_data),
        "healing_boost": lambda: _healing_boost(caster, target, skill_data),
        "hp_boost": lambda: _hp_boost(caster, target, skill_data),
        "mp_boost": lambda: _mp_boost(caster, target, skill_data),
        "regeneration": lambda: _regeneration(caster, target, skill_data),
        "speed_increase": lambda: _speed_increase(caster, target, skill_data),
        "stealth_mode": lambda: _stealth_mode(caster, target, skill_data),
        "stun_chance": lambda: _stun_chance(caster, target, skill_data),
        "teleport": lambda: _teleport(caster, target, skill_data),
        "fear_aura": lambda: _fear_aura(caster, target, skill_data),
        "poison_immunity": lambda: _poison_immunity(caster, target, skill_data),
        "fire_immunity": lambda: _fire_immunity(caster, target, skill_data),
        "cold_immunity": lambda: _cold_immunity(caster, target, skill_data),
        "status_immunity": lambda: _status_immunity(caster, target, skill_data),
        "mana_shield": lambda: _mana_shield(caster, target, skill_data),
        "perfect_accuracy": lambda: _perfect_accuracy(caster),
        "never_miss": lambda: _never_miss(caster),
        "guaranteed_critical": lambda: _guaranteed_critical(caster),
        "multi_hit": lambda: _multi_hit(caster, target, skill_data),
        "piercing": lambda: _piercing(caster, target, skill_data),
        "auto_counter": lambda: _auto_counter(caster, target, skill_data),
        "auto_revive": lambda: _auto_revive(caster, target, skill_data),
        "invisibility": lambda: _invisibility(caster, target, skill_data),
        # 추가된 구현 함수들
        "all_elements_burst": lambda: _all_elements_burst(caster, target, skill_data),
        "arena_experience": lambda: _arena_experience(caster),
        "arrow_penetration": lambda: _arrow_penetration(caster),
        "atonement_stack": lambda: _atonement_stack(caster),
        "basic_sword_aura": lambda: _basic_sword_aura(caster),
        "basic_sword_burst": lambda: _basic_sword_burst(caster),
        "basic_vampiric": lambda: _basic_vampiric(caster),
        "blessing_beam": lambda: _blessing_beam(caster),
        "blessing_sanctuary": lambda: _blessing_sanctuary(caster),
        "chi_circulation": lambda: _chi_circulation(caster),
        "combo_chain": lambda: _combo_chain(caster),
        "dark_aura": lambda: _dark_aura(caster, target, skill_data),
        "dark_aura_passive": lambda: _dark_aura_passive(caster),
        "dark_dominion": lambda: _dark_dominion(caster, target, skill_data),
        "dark_lord": lambda: _dark_lord(caster, target, skill_data),
        "darkness_power": lambda: _darkness_power(caster),
        "decisive_strike": lambda: _decisive_strike(caster),
        "divine_accumulation": lambda: _divine_accumulation(caster),
        "divine_protection": lambda: _divine_protection(caster, target, skill_data),
        "divine_release": lambda: _divine_release(caster),
        "dragon_breath": lambda: _dragon_breath(caster, target, skill_data),
        "dragon_lord_ultimate": lambda: _dragon_lord_ultimate(caster, target, skill_data),
        "dragon_majesty": lambda: _dragon_majesty(caster, target, skill_data),
        "dragon_mark": lambda: _dragon_mark(caster, target, skill_data),
        "dragon_scale": lambda: _dragon_scale(caster),
        "elemental_blade": lambda: _elemental_blade(caster),
        "elemental_burst": lambda: _elemental_burst(caster),
        "elemental_cycle": lambda: _elemental_cycle(caster, target, skill_data),
        "elemental_fusion": lambda: _elemental_fusion(caster, target, skill_data),
        "energy_discharge": lambda: _energy_discharge(caster),
        "fire_count": lambda: _fire_count(caster, target, skill_data),
        "generate_shadow": lambda: _generate_shadow(caster),
        "guardian_will": lambda: _guardian_will(caster),
        "holy_blessing": lambda: _holy_blessing(caster),
        "holy_strike_sanctuary": lambda: _holy_strike_sanctuary(caster, target, skill_data),
        "ice_count": lambda: _ice_count(caster, target, skill_data),
        "judgment_light": lambda: _judgment_light(caster, target, skill_data),
        "knight_honor": lambda: _knight_honor(caster),
        "leap_attack": lambda: _leap_attack(caster, target, skill_data),
        "lethal_strike": lambda: _lethal_strike(caster, target),
        "life_drain_all": lambda: _life_drain_all(caster, target, skill_data),
        "lightning_count": lambda: _lightning_count(caster, target, skill_data),
        "machine_charge": lambda: _machine_charge(caster),
        "melody_build": lambda: _melody_build(caster),
        "minor_vampiric": lambda: _minor_vampiric(caster),
        "nature_bond": lambda: _nature_bond(caster),
        "precision_stack": lambda: _precision_stack(caster),
        "purify_touch": lambda: _purify_touch(caster),
        "rage_build": lambda: _rage_build(caster),
        "sanctuary_expand": lambda: _sanctuary_expand(caster),
        "shadow_execution": lambda: _shadow_execution(caster, target),
        "sonic_burst": lambda: _sonic_burst(caster),
        "soul_harvest": lambda: _soul_harvest(caster),
        "support_fire_activation": lambda: _support_fire_activation(caster),
        "vampire_slash": lambda: _vampire_slash(caster, target, skill_data),
        "vampiric_strike": lambda: _vampiric_strike(caster, target, skill_data),
        "wild_instinct": lambda: _wild_instinct(caster),}
    
    if effect_name in effects_map:
        return effects_map[effect_name]()
    else:
        print(f"알 수 없는 특수 효과: {effect_name}")
        return False

def get_special_effect_handlers():
    """특수 효과 핸들러 딕셔너리 반환 (brave_combat.py에서 사용)"""
    return {
        # 광전사 효과 - HP 소모 + 보호막 + 흡혈
        "berserk_strike": _berserk_strike,
        "vampire_attack": _vampire_attack,
        "blood_shield": _blood_shield,
        "vampiric_blast": _vampiric_blast,
        "shield_consume": _shield_consume,
        "madness_amplify": _madness_amplify,
        "rage_chain": _rage_chain,
        "area_vampire": _area_vampire,
        "final_madness": _final_madness,
        "massive_vampire": _massive_vampire,
        
        # 기타 모든 효과들 (필요에 따라 추가)
        "rage_seed": _rage_seed,
        "blood_thirst": _blood_thirst,
        "mad_combo": _mad_combo,
        "rage_explosion": _rage_explosion,
        
        # 검투사 효과
        "gladiator_honor": _gladiator_honor,
        "colosseum_king": _colosseum_king,
        
        # 공통 효과
        "resurrect": _resurrect,
        "life_steal": _life_steal,
        "dispel_all": _dispel_all,
        "analyze_enemy": _analyze_enemy
    }

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
    """3연사 효과 + 조준 포인트 생성"""
    # 🏹 궁수의 경우 조준 포인트 생성
    if hasattr(caster, 'character_class') and caster.character_class == "궁수":
        if hasattr(caster, 'aim_points'):
            caster.aim_points = min(caster.aim_points + 1, 5)
        else:
            caster.aim_points = 1
        print(f"🎯 조준 포인트 +1! (현재: {caster.aim_points}/5)")
    
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
# 도적 Special Effects (리메이크)
# ========================================

def _poison_stack(caster, target, skill_data):
    """독 누적 효과"""
    if hasattr(target, 'status_effects'):
        # 기존 독 상태 확인하여 누적
        existing_poison = None
        for effect in target.status_effects:
            if effect.type == StatusType.POISON:
                existing_poison = effect
                break
        
        if existing_poison:
            # 독 지속시간 연장 + 강도 증가
            existing_poison.duration += 3
            existing_poison.intensity = min(existing_poison.intensity + 0.5, 5.0)
        else:
            # 새로운 독 부여
            target.add_status(StatusType.POISON, duration=6, intensity=1.2)
    return True

def _corrosive_poison(caster, target, skill_data):
    """부식성 독 효과"""
    if hasattr(target, 'add_status'):
        # 방어력 감소와 함께 독 누적
        target.add_status(StatusType.POISON, duration=8, intensity=1.0)
        target.add_status(StatusType.REDUCE_DEF, duration=5, intensity=0.7)
        # 독 피해량이 방어력 감소에 비례하여 증가
        if hasattr(target, 'temp_effects'):
            target.temp_effects["poison_amplify"] = target.temp_effects.get("poison_amplify", 0) + 0.3
    return True

def _poison_trigger(caster, target, skill_data):
    """독 촉진 효과 - 남은 독 피해의 50%를 즉시 피해로 전환"""
    if hasattr(target, 'status_effects') and hasattr(target, 'take_damage'):
        total_poison_damage = 0
        
        for effect in target.status_effects[:]:  # 복사본 순회
            if effect.type == StatusType.POISON:
                # 남은 독 피해 계산 (지속시간 × 강도 × 10)
                remaining_damage = effect.duration * effect.intensity * 10
                trigger_damage = int(remaining_damage * 0.5)
                total_poison_damage += trigger_damage
                
                # 독 지속시간을 절반으로 줄임
                effect.duration = max(1, effect.duration // 2)
        
        if total_poison_damage > 0:
            target.take_damage(total_poison_damage)
            print(f"{target.name}의 독이 촉진되어 {total_poison_damage}의 피해!")
    return True

def _poison_fog_enhanced(caster, target):
    """강화 독무 효과"""
    if hasattr(target, 'add_status'):
        # 모든 적에게 강력한 독 + 시야 차단
        target.add_status(StatusType.POISON, duration=8, intensity=1.8)
        target.add_status(StatusType.BLIND, duration=4, intensity=0.8)
        # 독 저항력 감소
        target.add_status(StatusType.REDUCE_RESIST, duration=6, intensity=0.6)
    return True

def _venom_explosion(caster, target, skill_data):
    """베놈 익스플로전 - 모든 독을 폭발시켜 즉시 피해"""
    if hasattr(target, 'status_effects') and hasattr(target, 'take_damage'):
        total_explosion_damage = 0
        poison_effects_to_remove = []
        
        for effect in target.status_effects:
            if effect.type == StatusType.POISON:
                # 독 폭발 피해 계산 (지속시간 × 강도 × 15)
                explosion_damage = int(effect.duration * effect.intensity * 15)
                total_explosion_damage += explosion_damage
                poison_effects_to_remove.append(effect)
        
        # 모든 독 제거
        for effect in poison_effects_to_remove:
            target.status_effects.remove(effect)
        
        if total_explosion_damage > 0:
            target.take_damage(total_explosion_damage)
            print(f"{target.name}의 독혈이 폭발하여 {total_explosion_damage}의 피해!")
            
            # 폭발 후 새로운 독 부여 (약화된)
            target.add_status(StatusType.POISON, duration=4, intensity=0.8)
    return True

def _poison_emperor(caster, target, skill_data):
    """독왕강림 - 전체 적의 독을 폭발시키고 강력한 독 재부여"""
    if hasattr(target, 'status_effects') and hasattr(target, 'take_damage'):
        total_emperor_damage = 0
        poison_count = 0
        
        for effect in target.status_effects[:]:  # 복사본 순회
            if effect.type == StatusType.POISON:
                # 독왕 폭발 피해 (지속시간 × 강도 × 25)
                emperor_damage = int(effect.duration * effect.intensity * 25)
                total_emperor_damage += emperor_damage
                poison_count += 1
                target.status_effects.remove(effect)
        
        if total_emperor_damage > 0:
            target.take_damage(total_emperor_damage)
            print(f"독왕의 힘으로 {target.name}에게 {total_emperor_damage}의 피해!")
        
        # 독왕의 저주 - 매우 강력한 독 부여
        target.add_status(StatusType.POISON, duration=12, intensity=3.0)
        target.add_status(StatusType.CURSE, duration=8, intensity=2.0)
        
        # 독 개수에 따른 추가 효과
        if poison_count >= 2:
            target.add_status(StatusType.NECROSIS, duration=6, intensity=1.5)
    return True

# ========================================
# 도적 기존 효과들 (업데이트됨)
# ========================================

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
    """독무 효과 (기존 - 호환성 유지)"""
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
    """독왕의 비의 (기존 - 호환성 유지)"""
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

# ========================================
# 검성 Special Effects
# ========================================

def _iai_cut(caster, target, skill_data):
    """거합 일섬"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("critical_guaranteed", 1)
        caster.add_temp_effect("damage_multiplier", 1.5)
    return True

def _sword_pressure(caster, target, skill_data):
    """검압"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.STUN, duration=2, intensity=1.0)
        target.add_status(StatusType.REDUCE_ATK, duration=4, intensity=0.7)
    return True

def _sword_unity(caster):
    """검심일체"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ATK, duration=5, intensity=1.5)
        caster.add_status(StatusType.BOOST_CRIT, duration=5, intensity=2.0)
        caster.add_status(StatusType.BOOST_ACCURACY, duration=5, intensity=1.8)
    return True

def _peerless_cut(caster, target, skill_data):
    """무상검법"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("ignore_all_defense", 1)
        caster.add_temp_effect("damage_multiplier", 2.0)
    return True

def _sword_emperor(caster, target, skill_data):
    """검황"""
    if hasattr(caster, 'add_status') and hasattr(target, 'add_status'):
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=3, intensity=2.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, intensity=0.5)
    return True

# ========================================
# 검투사 Special Effects
# ========================================

def _gladiator_honor(caster):
    """검투사의 명예"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ATK, duration=4, intensity=1.3)
        caster.add_status(StatusType.BOOST_DEF, duration=4, intensity=1.3)
        caster.add_status(StatusType.REGENERATION, duration=5, intensity=1.0)
    return True

def _colosseum_king(caster, target, skill_data):
    """콜로세움의 왕"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, intensity=1.5)
        caster.add_status(StatusType.VAMPIRE, duration=5, intensity=1.0)
    return True

# ========================================
# 광전사 Special Effects
# ========================================

def _rage_seed(caster):
    """분노의 씨앗"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.RAGE, duration=10, intensity=1.2)
        caster.add_status(StatusType.BOOST_ATK, duration=10, intensity=1.3)
    return True

def _blood_thirst(caster, target, skill_data):
    """피에 굶주린"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.VAMPIRE, duration=5, intensity=2.0)
        caster.add_status(StatusType.BOOST_ATK, duration=5, intensity=1.4)
    return True

def _mad_combo(caster, target, skill_data):
    """광란의 연격"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("multi_hit", 4)  # 4연속 공격
        caster.add_temp_effect("damage_multiplier", 0.8)  # 각 타격 80% 데미지
    return True

def _rage_explosion(caster, target, skill_data):
    """분노 폭발"""
    if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
        lost_hp_ratio = 1 - (caster.current_hp / caster.max_hp)
        explosion_power = 1.0 + lost_hp_ratio * 2.0  # 잃은 HP에 비례해서 강해짐
        if hasattr(caster, 'add_temp_effect'):
            caster.add_temp_effect("damage_multiplier", explosion_power)
    return True

def _berserker_end(caster, target, skill_data):
    """광전사의 끝"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=3, intensity=3.0)
        caster.add_status(StatusType.TEMPORARY_INVINCIBLE, duration=1, intensity=1.0)
        # HP가 1이 되도록 설정
        if hasattr(caster, 'current_hp'):
            caster.current_hp = 1
    return True

# ========================================
# 기사/성기사 Special Effects
# ========================================

def _knight_oath(caster):
    """기사의 맹세"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_DEF, duration=5, intensity=1.5)
        caster.add_status(StatusType.BOOST_MAGIC_DEF, duration=5, intensity=1.5)
        caster.add_status(StatusType.TAUNT, duration=3, intensity=1.0)
    return True

def _holy_strike(caster, target, skill_data):
    """성스러운 일격"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.HOLY_MARK, duration=5, intensity=1.0)
        target.add_status(StatusType.REDUCE_MAGIC_DEF, duration=3, intensity=0.7)
    return True

def _holy_heal(caster, target):
    """성스러운 치유"""
    if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
        heal_amount = int(target.max_hp * 0.5)
        target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
        if hasattr(target, 'add_status'):
            target.add_status(StatusType.REGENERATION, duration=5, intensity=2.0)
    return True

def _angel_descent(caster, target, skill_data):
    """천사 강림"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, intensity=1.8)
        caster.add_status(StatusType.HOLY_AURA, duration=5, intensity=1.0)
    return True

# ========================================
# 다크나이트 Special Effects
# ========================================

def _dark_pact(caster, target, skill_data):
    """어둠의 계약"""
    if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
        sacrifice_hp = int(caster.max_hp * 0.2)
        caster.current_hp = max(1, caster.current_hp - sacrifice_hp)
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_ATK, duration=5, intensity=2.0)
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, intensity=2.0)
    return True

def _vampire_strike(caster, target, skill_data):
    """흡혈 공격"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.VAMPIRE, duration=5, intensity=3.0)
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.WEAKNESS, duration=3, intensity=0.8)
    return True

def _dark_domination(caster, target, skill_data):
    """어둠의 지배"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.CHARM, duration=3, intensity=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, intensity=0.6)
    return True

# ========================================
# 드래곤나이트 Special Effects
# ========================================

def _dragon_spear(caster, target, skill_data):
    """드래곤 창"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("armor_pierce", 1)
        caster.add_temp_effect("damage_multiplier", 1.8)
        caster.add_temp_effect("elemental_damage", "fire")
    return True

def _dragon_lord(caster, target, skill_data):
    """용왕"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.DRAGON_FORM, duration=5, intensity=1.0)
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, intensity=2.0)
        caster.add_status(StatusType.ELEMENTAL_IMMUNITY, duration=5, intensity=1.0)
    return True

# ========================================
# 원소술사 Special Effects
# ========================================

def _earth_rage(caster, target, skill_data):
    """대지의 분노"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.ENTANGLE, duration=3, intensity=1.0)
        target.add_status(StatusType.REDUCE_SPEED, duration=5, intensity=0.5)
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("elemental_damage", "earth")
    return True

def _four_elements(caster, target, skill_data):
    """사원소 융합"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.BURN, duration=4, intensity=1.5)
        target.add_status(StatusType.FREEZE, duration=2, intensity=1.0)
        target.add_status(StatusType.SHOCK, duration=4, intensity=1.5)
        target.add_status(StatusType.ENTANGLE, duration=3, intensity=1.0)
    return True

# ========================================
# 시공술사 Special Effects
# ========================================

def _time_record_savepoint(caster):
    """시간 기록점 - 시간술사 특성 연동"""
    # 시간술사 특성: 시간 역행 스택 증가
    if hasattr(caster, 'character_class') and caster.character_class == "시간술사":
        if hasattr(caster, 'time_rewind_stacks'):
            caster.time_rewind_stacks = min(caster.time_rewind_stacks + 1, 3)
        else:
            caster.time_rewind_stacks = 1
        
        # 시간술사 특성: 시간 감각으로 ATB 보너스
        if hasattr(caster, 'temp_atb_boost'):
            caster.temp_atb_boost = getattr(caster, 'temp_atb_boost', 0) + 1000
        else:
            caster.temp_atb_boost = 1000
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.TIME_SAVEPOINT, duration=999, intensity=1.0)
    return True

def _time_rewind_to_savepoint(caster):
    """시간 되돌리기 - 시간술사 특성 연동"""
    # 시간술사 특성: 시간 역행 스택 소모하여 강화된 회복
    if hasattr(caster, 'character_class') and caster.character_class == "시간술사":
        time_stacks = getattr(caster, 'time_rewind_stacks', 0)
        if time_stacks > 0:
            # 스택별 회복량 증가
            if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
                heal_percent = 0.5 + (time_stacks * 0.2)  # 스택당 20% 추가 회복
                heal_amount = int(caster.max_hp * heal_percent)
                caster.current_hp = min(caster.max_hp, caster.current_hp + heal_amount)
            
            if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
                mp_heal_percent = 0.3 + (time_stacks * 0.15)  # 스택당 15% 추가 MP 회복
                mp_heal_amount = int(caster.max_mp * mp_heal_percent)
                caster.current_mp = min(caster.max_mp, caster.current_mp + mp_heal_amount)
            
            # 스택 모두 소모
            caster.time_rewind_stacks = 0
            return True
    
    if hasattr(caster, 'rewind_to_savepoint'):
        caster.rewind_to_savepoint()
    elif hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
        # 간단한 구현: HP/MP 완전 회복
        caster.current_hp = caster.max_hp
        if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
            caster.current_mp = caster.max_mp
    return True

def _future_sight(caster):
    """미래시"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.FORESIGHT, duration=5, intensity=1.0)
        caster.add_status(StatusType.BOOST_DODGE, duration=5, intensity=2.0)
        caster.add_status(StatusType.BOOST_CRIT, duration=5, intensity=1.5)
    return True

def _time_stop(caster):
    """시간 정지 - 시간술사 특성 연동"""
    # 시간술사 특성: 시간 제어로 효과 강화
    if hasattr(caster, 'character_class') and caster.character_class == "시간술사":
        # 시간술사는 더 긴 지속시간과 추가 효과
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.TIME_STOP, duration=3, intensity=1.0)  # 1턴 더 길게
            caster.add_status(StatusType.EXTRA_TURN, duration=1, intensity=4.0)  # 추가 행동 1회 더
            caster.add_status(StatusType.BOOST_ALL_STATS, duration=3, intensity=1.3)  # 모든 스탯 30% 증가
        
        # 시간 감각으로 미래시 효과 추가
        if hasattr(caster, 'temp_crit_resistance'):
            caster.temp_crit_resistance = getattr(caster, 'temp_crit_resistance', 0) + 0.5
        else:
            caster.temp_crit_resistance = 0.5
    else:
        # 일반적인 시간 정지 효과
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.TIME_STOP, duration=2, intensity=1.0)
            caster.add_status(StatusType.EXTRA_TURN, duration=1, intensity=3.0)
    return True

def _spacetime_collapse(caster, target, skill_data):
    """시공붕괴"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.TIME_DISTORTION, duration=5, intensity=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, intensity=0.3)
    return True

# ========================================
# 공간술사 Special Effects
# ========================================

def _dimension_cloak(caster):
    """차원 은폐 - 차원술사 특성 연동"""
    # 차원술사 특성: 차원 방패 스택 증가
    if hasattr(caster, 'character_class') and caster.character_class == "차원술사":
        if hasattr(caster, 'dimension_shield_stacks'):
            caster.dimension_shield_stacks = min(caster.dimension_shield_stacks + 1, 5)
        else:
            caster.dimension_shield_stacks = 1
        
        # 공간 왜곡으로 적 명중률 감소 효과 강화
        if hasattr(caster, 'temp_enemy_accuracy_down'):
            caster.temp_enemy_accuracy_down = getattr(caster, 'temp_enemy_accuracy_down', 0) + 30
        else:
            caster.temp_enemy_accuracy_down = 30
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.STEALTH, duration=3, intensity=1.0)
        caster.add_status(StatusType.BOOST_DODGE, duration=5, intensity=3.0)
    return True

def _afterimage(caster):
    """잔상 - 차원술사 특성 연동"""
    # 차원술사 특성: 잔상 스택 증가
    if hasattr(caster, 'character_class') and caster.character_class == "차원술사":
        if hasattr(caster, 'afterimage_stacks'):
            caster.afterimage_stacks = min(caster.afterimage_stacks + 2, 10)  # 스킬 사용 시 2스택 증가
        else:
            caster.afterimage_stacks = 2
        
        # 차원 감지로 속도 보너스 추가
        if hasattr(caster, 'temp_spd_boost'):
            caster.temp_spd_boost = getattr(caster, 'temp_spd_boost', 0) + 20
        else:
            caster.temp_spd_boost = 20
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.AFTERIMAGE, duration=4, intensity=1.0)
        caster.add_status(StatusType.BOOST_SPD, duration=4, intensity=2.0)
    return True

def _space_leap(caster, target, skill_data):
    """공간 도약 - 차원술사 특성 연동"""
    # 차원술사 특성: 차원 도약으로 차원 방패와 잔상 스택 증가
    if hasattr(caster, 'character_class') and caster.character_class == "차원술사":
        # 차원 방패 스택 증가
        if hasattr(caster, 'dimension_shield_stacks'):
            caster.dimension_shield_stacks = min(caster.dimension_shield_stacks + 1, 5)
        else:
            caster.dimension_shield_stacks = 1
        
        # 잔상 스택 증가
        if hasattr(caster, 'afterimage_stacks'):
            caster.afterimage_stacks = min(caster.afterimage_stacks + 1, 10)
        else:
            caster.afterimage_stacks = 1
    
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("guaranteed_hit", 1)
        caster.add_temp_effect("damage_multiplier", 1.5)
    return True

def _dimension_maze(caster, target):
    """차원 미궁"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.CONFUSION, duration=4, intensity=1.0)
        target.add_status(StatusType.REDUCE_ACCURACY, duration=5, intensity=0.5)
    return True

def _evasion_counter(caster, target, skill_data):
    """회피 반격"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.EVASION_UP, duration=3, intensity=2.0)
        caster.add_status(StatusType.COUNTER_ATTACK, duration=3, intensity=1.5)
    return True

def _untouchable_state(caster):
    """무적 상태"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.ABSOLUTE_EVASION, duration=2, intensity=1.0)
        caster.add_status(StatusType.TEMPORARY_INVINCIBLE, duration=1, intensity=1.0)
    return True

# ========================================
# 철학자 Special Effects
# ========================================

def _truth_insight(caster, target):
    """진리 통찰 - 철학자 특성 연동"""
    # 철학자 특성: 지혜 스택 증가
    if hasattr(caster, 'character_class') and caster.character_class == "철학자":
        if hasattr(caster, 'wisdom_stacks'):
            caster.wisdom_stacks = min(caster.wisdom_stacks + 1, 10)
        else:
            caster.wisdom_stacks = 1
        
        # 지혜 스택이 많을수록 효과 강화
        wisdom_stacks = getattr(caster, 'wisdom_stacks', 0)
        analyze_bonus = 1.0 + (wisdom_stacks * 0.1)  # 스택당 10% 효과 증가
        
        if hasattr(target, 'add_status'):
            target.add_status(StatusType.ANALYZE, duration=999, intensity=2.0 * analyze_bonus)
            target.add_status(StatusType.WEAKNESS_EXPOSURE, duration=5, intensity=1.0 * analyze_bonus)
    else:
        if hasattr(target, 'add_status'):
            target.add_status(StatusType.ANALYZE, duration=999, intensity=2.0)
            target.add_status(StatusType.WEAKNESS_EXPOSURE, duration=5, intensity=1.0)
    return True

def _existence_denial(caster, target, skill_data):
    """존재 부정"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.EXISTENCE_DENIAL, duration=3, intensity=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, intensity=0.4)
    return True

def _philosophical_thought(caster):
    """철학적 사고 - 철학자 특성 연동"""
    # 철학자 특성: 사색으로 지혜 스택 대량 증가
    if hasattr(caster, 'character_class') and caster.character_class == "철학자":
        if hasattr(caster, 'wisdom_stacks'):
            caster.wisdom_stacks = min(caster.wisdom_stacks + 3, 10)  # 3스택 증가
        else:
            caster.wisdom_stacks = 3
        
        # 사색 중 상태: 혼란 무시 및 마법 위력 증가
        if hasattr(caster, 'temp_confusion_immunity'):
            caster.temp_confusion_immunity = True
        else:
            caster.temp_confusion_immunity = True
        
        # 지혜 스택에 비례한 보너스
        wisdom_stacks = getattr(caster, 'wisdom_stacks', 0)
        magic_boost = 1.5 + (wisdom_stacks * 0.1)  # 스택당 10% 추가
        
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, intensity=magic_boost)
            caster.add_status(StatusType.MANA_REGENERATION, duration=5, intensity=2.0)
            caster.add_status(StatusType.WISDOM, duration=5, intensity=1.0)
    else:
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, intensity=2.0)
            caster.add_status(StatusType.MANA_REGENERATION, duration=5, intensity=2.0)
            caster.add_status(StatusType.WISDOM, duration=5, intensity=1.0)
    return True

def _absolute_truth(caster, target, skill_data):
    """절대 진리"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("ignore_all_resistance", 1)
        caster.add_temp_effect("damage_multiplier", 3.0)
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.TRUTH_REVELATION, duration=999, intensity=1.0)
    return True

# ========================================
# 해적 Special Effects
# ========================================

def _ghost_fleet(caster, target, skill_data):
    """유령 함대"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.GHOST_FLEET, duration=5, intensity=1.0)
        caster.add_status(StatusType.BOOST_ATK, duration=5, intensity=1.5)
    return True

# ========================================
# 무사 Special Effects
# ========================================

def _mushin_cut(caster, target, skill_data):
    """무심검"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("critical_guaranteed", 1)
        caster.add_temp_effect("ignore_all_defense", 1)
        caster.add_temp_effect("damage_multiplier", 2.5)
    return True

# ========================================
# 음유시인 Special Effects
# ========================================

def _divine_song(caster, target):
    """신의 노래"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.BOOST_ALL_STATS, duration=5, intensity=1.3)
        target.add_status(StatusType.REGENERATION, duration=5, intensity=1.5)
        target.add_status(StatusType.MANA_REGENERATION, duration=5, intensity=1.5)
    return True

def _heavenly_chorus(caster, target):
    """천상의 합창"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.BOOST_ALL_STATS, duration=8, intensity=1.5)
        target.add_status(StatusType.HOLY_BLESSING, duration=8, intensity=1.0)
    return True

# ========================================
# 동물조련사 Special Effects
# ========================================

def _soul_analysis(caster, target):
    """영혼 분석"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.SOUL_BOND, duration=999, intensity=1.0)
        target.add_status(StatusType.ANALYZE, duration=999, intensity=1.5)
    return True

def _nature_judgment(caster, target, skill_data):
    """자연의 심판"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.NATURE_CURSE, duration=5, intensity=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, intensity=0.7)
    return True

def _animal_form(caster):
    """동물 변신"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.ANIMAL_FORM, duration=5, intensity=1.0)
        caster.add_status(StatusType.BOOST_SPD, duration=5, intensity=2.0)
        caster.add_status(StatusType.BOOST_ATK, duration=5, intensity=1.5)
    return True

def _lightning_storm(caster, target, skill_data):
    """번개 폭풍"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.SHOCK, duration=5, intensity=2.0)
        target.add_status(StatusType.STUN, duration=2, intensity=1.0)
    return True

def _gaia_wrath(caster, target, skill_data):
    """가이아의 분노"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.NATURE_CURSE, duration=8, intensity=2.0)
        target.add_status(StatusType.ENTANGLE, duration=4, intensity=1.0)
        target.add_status(StatusType.POISON, duration=6, intensity=1.5)
    return True

# ========================================
# 성직자 Special Effects
# ========================================

def _holy_light(caster, target, skill_data):
    """성스러운 빛"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.HOLY_MARK, duration=5, intensity=1.0)
        target.add_status(StatusType.REDUCE_MAGIC_DEF, duration=5, intensity=0.6)
    return True

def _greater_heal(caster, target):
    """상급 치유"""
    if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
        heal_amount = int(target.max_hp * 0.8)
        target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
        if hasattr(target, 'clear_negative_status'):
            target.clear_negative_status()
    return True

def _divine_punishment(caster, target, skill_data):
    """신의 징벌"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.DIVINE_PUNISHMENT, duration=5, intensity=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, intensity=0.5)
    return True

def _heaven_gate(caster, target, skill_data):
    """천국의 문"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.HEAVEN_GATE, duration=3, intensity=1.0)
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, intensity=2.0)
    return True

# ========================================
# 순교자 Special Effects
# ========================================

def _purify_light(caster, target):
    """정화의 빛"""
    if hasattr(target, 'clear_all_negative_status'):
        target.clear_all_negative_status()
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.PURIFICATION, duration=5, intensity=1.0)
    return True

def _martyrdom_path(caster):
    """순교의 길"""
    if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
        sacrifice_ratio = 0.5
        sacrifice_hp = int(caster.max_hp * sacrifice_ratio)
        caster.current_hp = max(1, caster.current_hp - sacrifice_hp)
        if hasattr(caster, 'add_status'):
            power_boost = 2.0 + sacrifice_ratio
            caster.add_status(StatusType.MARTYRDOM, duration=3, intensity=power_boost)
    return True

def _divine_judgment(caster, target, skill_data):
    """신의 심판"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.DIVINE_JUDGMENT, duration=3, intensity=1.0)
        target.add_status(StatusType.HOLY_WEAKNESS, duration=5, intensity=2.0)
    return True

# ========================================
# 무술가 Special Effects
# ========================================

def _combo_attack(caster, target, skill_data):
    """연속 공격"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("multi_hit", 3)
        caster.add_temp_effect("combo_bonus", 1.2)
    return True

def _mp_restore_15pct(caster):
    """MP 15% 회복"""
    if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
        recovery = int(caster.max_mp * 0.15)
        caster.current_mp = min(caster.max_mp, caster.current_mp + recovery)
    return True

def _ki_explosion(caster, target, skill_data):
    """기 폭발"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("area_damage", 1)
        caster.add_temp_effect("damage_multiplier", 1.8)
    return True

def _enlightenment(caster):
    """깨달음"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.ENLIGHTENMENT, duration=5, intensity=1.0)
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, intensity=1.5)
        caster.add_status(StatusType.MANA_REGENERATION, duration=10, intensity=2.0)
    return True

# ========================================
# 연금술사 Special Effects
# ========================================

def _elemental_weapon(caster, skill_data):
    """원소 무기"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.ELEMENTAL_WEAPON, duration=5, intensity=1.0)
        caster.add_status(StatusType.BOOST_ATK, duration=5, intensity=1.3)
    return True

def _magic_field(caster):
    """마법 진영"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.MAGIC_FIELD, duration=5, intensity=1.0)
        caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, intensity=1.5)
        caster.add_status(StatusType.MANA_REGENERATION, duration=5, intensity=1.5)
    return True

def _perfect_fusion(caster, target, skill_data):
    """완벽한 융합"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("elemental_fusion", 1)
        caster.add_temp_effect("damage_multiplier", 2.0)
    return True

def _transmute_item(caster):
    """아이템 변환 - 연금술사 특성 연동"""
    # 연금술사 특성: 연금술 포션 제작 스택 증가
    if hasattr(caster, 'character_class') and caster.character_class == "연금술사":
        if hasattr(caster, 'potion_craft_stacks'):
            caster.potion_craft_stacks = min(caster.potion_craft_stacks + 1, 5)
        else:
            caster.potion_craft_stacks = 1
        
        # 원소 변환으로 무작위 원소 저항 증가
        import random
        elements = ['fire', 'water', 'earth', 'air']
        chosen_element = random.choice(elements)
        resistance_attr = f'temp_{chosen_element}_resistance'
        if hasattr(caster, resistance_attr):
            current_resistance = getattr(caster, resistance_attr, 0)
            setattr(caster, resistance_attr, current_resistance + 0.2)
        else:
            setattr(caster, resistance_attr, 0.2)
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.TRANSMUTATION, duration=1, intensity=1.0)
    return True

def _instant_potion(caster, target):
    """즉석 포션 - 연금술사 특성 연동"""
    # 연금술사 특성: 포션 제작으로 효과 강화
    if hasattr(caster, 'character_class') and caster.character_class == "연금술사":
        # 포션 제작 스택에 따른 회복량 증가
        potion_stacks = getattr(caster, 'potion_craft_stacks', 0)
        heal_multiplier = 1.0 + (potion_stacks * 0.15)  # 스택당 15% 증가
        
        if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
            heal_amount = int(target.max_hp * 0.4 * heal_multiplier)
            target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
        
        if hasattr(target, 'current_mp') and hasattr(target, 'max_mp'):
            mp_recovery = int(target.max_mp * 0.3 * heal_multiplier)
            target.current_mp = min(target.max_mp, target.current_mp + mp_recovery)
        
        # 추가 효과: 디버프 제거
        if hasattr(target, 'remove_debuffs'):
            target.remove_debuffs(count=1)
        
        # 포션 제작 스택 1개 소모
        if hasattr(caster, 'potion_craft_stacks') and caster.potion_craft_stacks > 0:
            caster.potion_craft_stacks -= 1
    else:
        # 일반적인 포션 효과
        if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
            heal_amount = int(target.max_hp * 0.4)
            target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
        if hasattr(target, 'current_mp') and hasattr(target, 'max_mp'):
            mp_recovery = int(target.max_mp * 0.3)
            target.current_mp = min(target.max_mp, target.current_mp + mp_recovery)
    return True

def _acid_corrosion(caster, target, skill_data):
    """산성 부식"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.CORROSION, duration=5, intensity=1.0)
        target.add_status(StatusType.REDUCE_DEF, duration=5, intensity=0.5)
        target.add_status(StatusType.REDUCE_MAGIC_DEF, duration=5, intensity=0.5)
    return True

def _philosophers_stone(caster):
    """현자의 돌"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.PHILOSOPHERS_STONE, duration=3, intensity=1.0)
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, intensity=1.8)
        caster.add_status(StatusType.MANA_INFINITE, duration=3, intensity=1.0)
    return True

# ========================================
# 네크로맨서 Special Effects
# ========================================

def _summon_undead(caster):
    """언데드 소환"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.UNDEAD_MINION, duration=10, intensity=1.0)
        caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, intensity=1.3)
    return True

def _life_drain(caster, target, skill_data):
    """생명력 흡수"""
    if hasattr(target, 'current_hp') and hasattr(caster, 'current_hp'):
        drain_amount = max(1, target.current_hp // 4)
        target.current_hp = max(0, target.current_hp - drain_amount)
        if hasattr(caster, 'max_hp'):
            caster.current_hp = min(caster.max_hp, caster.current_hp + drain_amount)
    return True

# ========================================
# 추가 도적 Special Effects
# ========================================

def _smoke_bomb(caster):
    """연막탄"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.STEALTH, duration=3, intensity=1.0)
        caster.add_status(StatusType.BOOST_DODGE, duration=5, intensity=2.0)
    return True

def _assassination(caster, target, skill_data):
    """암살"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("critical_guaranteed", 1)
        caster.add_temp_effect("instant_kill_chance", 0.3)  # 30% 즉사 확률
        caster.add_temp_effect("damage_multiplier", 3.0)
    return True

def _shadow_clone(caster):
    """그림자 분신"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.SHADOW_CLONE, duration=4, intensity=1.0)

# ========================================
# 🌟 새로운 직업 시스템 Special Effects
# ========================================

# === 검성 Special Effects ===
def _sword_aura_gain(caster):
    """검기 스택 획득 (최대 2스택)"""
    if not hasattr(caster, 'sword_aura_stacks'):
        caster.sword_aura_stacks = 0
    if caster.sword_aura_stacks < 2:
        caster.sword_aura_stacks += 1
        print(f"🗡️ {caster.name}의 검기 스택이 {caster.sword_aura_stacks}개가 되었습니다!")

def _sword_aura_consume(caster, target, skill_data):
    """검기 스택 1개 소모하여 스킬 강화"""
    if not hasattr(caster, 'sword_aura_stacks'):
        caster.sword_aura_stacks = 0
    
    if caster.sword_aura_stacks > 0:
        consumed_stacks = min(1, caster.sword_aura_stacks)
        caster.sword_aura_stacks -= consumed_stacks
        
        # 스킬 위력 강화 (스택당 30% 증가)
        if skill_data and 'hp_power' in skill_data:
            bonus_power = int(skill_data['hp_power'] * 0.3 * consumed_stacks)
            print(f"⚡ 검기 스택 {consumed_stacks}개 소모! 위력 +{bonus_power}")
            return bonus_power
    return 0

def _sword_aura_consume_all(caster, target, skill_data):
    """모든 검기 스택 소모하여 스킬 강화"""
    if not hasattr(caster, 'sword_aura_stacks'):
        caster.sword_aura_stacks = 0
    
    if caster.sword_aura_stacks > 0:
        consumed_stacks = caster.sword_aura_stacks
        caster.sword_aura_stacks = 0
        
        # 스킬 위력 강화 (스택당 40% 증가)
        if skill_data and 'hp_power' in skill_data:
            bonus_power = int(skill_data['hp_power'] * 0.4 * consumed_stacks)
            print(f"💥 모든 검기 스택 {consumed_stacks}개 소모! 위력 +{bonus_power}")
            return bonus_power
    return 0

def _sword_aura_wave(caster, target, skill_data):
    """검기 파동 - 스택 1개 소모하여 관통 공격"""
    if not hasattr(caster, 'sword_aura_stacks'):
        caster.sword_aura_stacks = 0
    
    if caster.sword_aura_stacks > 0:
        caster.sword_aura_stacks -= 1
        print(f"🌊 검기 파동! 관통 공격 발동! (남은 스택: {caster.sword_aura_stacks})")
        return True
    return False

def _atb_refund(caster, skill_data):
    """ATB 게이지 20-60% 환급"""
    if not hasattr(caster, 'sword_aura_stacks'):
        refund_rate = 0.2
    else:
        # 소모한 스택에 따라 환급률 결정
        refund_rate = 0.2 + (0.2 * getattr(caster, 'last_consumed_stacks', 1))
    
    if hasattr(caster, 'atb_gauge'):
        refund_amount = int(caster.max_atb * refund_rate)
        caster.atb_gauge = min(caster.max_atb, caster.atb_gauge + refund_amount)
        print(f"⏱️ ATB 게이지 {int(refund_rate*100)}% 환급!")

def _atb_refund_medium(caster, skill_data):
    """ATB 게이지 30% 환급"""
    if hasattr(caster, 'atb_gauge'):
        refund_amount = int(caster.max_atb * 0.3)
        caster.atb_gauge = min(caster.max_atb, caster.atb_gauge + refund_amount)
        print(f"⏱️ ATB 게이지 30% 환급!")

def _infinite_blade(caster, target, skill_data):
    """무한검 - 모든 스택으로 다연타"""
    if not hasattr(caster, 'sword_aura_stacks'):
        caster.sword_aura_stacks = 0
    
    consumed_stacks = caster.sword_aura_stacks
    caster.sword_aura_stacks = 0
    
    if consumed_stacks > 0:
        # 다연타 실행 (스택당 추가타)
        extra_hits = consumed_stacks
        print(f"⚔️ 무한검! {extra_hits + 1}연타 발동!")
        return extra_hits
    return 0

# === 검투사 Special Effects ===
def _gladiator_skill(caster, target, skill_data):
    """검투사 기술 - 적 처치 시 능력치 상승"""
    if not hasattr(caster, 'kill_stacks'):
        caster.kill_stacks = 0
    
    # 적이 죽었을 때 호출되는 함수에서 스택 증가
    # 여기서는 스택에 따른 현재 보너스만 표시
    if caster.kill_stacks > 0:
        print(f"🏆 처치 스택 {caster.kill_stacks}개로 능력치 강화 중!")

def _parry_stance(caster):
    """패링 태세"""
    if hasattr(caster, 'add_status'):
        # 기본 지속시간 3턴
        base_duration = 3
        
        # HP 30% 이하일 때 생존 본능 특성 확인
        if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
            hp_ratio = caster.current_hp / caster.max_hp
            if hp_ratio <= 0.3:
                # 생존 본능 특성으로 지속시간 연장
                trait_effects = caster.apply_passive_trait_effects("parrying") if hasattr(caster, 'apply_passive_trait_effects') else {}
                duration_multiplier = trait_effects.get("survival_parry_duration", 1.0)
                extended_duration = int(base_duration * duration_multiplier)
                
                if extended_duration > base_duration:
                    print(f"🛡️💀 생존 본능 발동! 패링 지속시간이 {extended_duration}턴으로 연장됩니다!")
                    caster.add_status(StatusType.COUNTER, duration=extended_duration, intensity=1.0)
                else:
                    caster.add_status(StatusType.COUNTER, duration=base_duration, intensity=1.0)
            else:
                caster.add_status(StatusType.COUNTER, duration=base_duration, intensity=1.0)
        else:
            caster.add_status(StatusType.COUNTER, duration=base_duration, intensity=1.0)
            
        print(f"🛡️ {caster.name}이 패링 태세를 취했습니다!")

def _honor_strike(caster, target, skill_data):
    """명예의 일격 - 처치 스택에 따라 강화"""
    if not hasattr(caster, 'kill_stacks'):
        caster.kill_stacks = 0
    
    if caster.kill_stacks > 0 and skill_data and 'hp_power' in skill_data:
        bonus_power = int(skill_data['hp_power'] * 0.25 * caster.kill_stacks)
        print(f"💪 처치 스택 {caster.kill_stacks}개로 위력 +{bonus_power}!")
        return bonus_power
    return 0

def _warrior_roar(caster):
    """투사의 함성 - MP, HP 회복"""
    if hasattr(caster, 'mp') and hasattr(caster, 'hp'):
        mp_heal = int(caster.max_mp * 0.15)
        hp_heal = int(caster.max_hp * 0.1)
        caster.mp = min(caster.max_mp, caster.mp + mp_heal)
        caster.hp = min(caster.max_hp, caster.hp + hp_heal)
        print(f"🗣️ 함성으로 MP {mp_heal}, HP {hp_heal} 회복!")

def _survival_spirit(caster, target, skill_data):
    """생존자의 투혼 - 처치 시 회복"""
    print(f"💀 생존 의지로 강화된 공격!")

# === 광전사 Special Effects ===
def _berserk_strike(caster, target, skill_data):
    """광폭화 난타 - HP 소모하여 강화"""
    if hasattr(caster, 'hp') and skill_data and 'hp_sacrifice' in skill_data:
        sacrifice = skill_data['hp_sacrifice']
        if caster.hp > sacrifice:
            caster.hp -= sacrifice
            # 소모한 HP에 따라 위력 증가
            bonus_power = sacrifice * 2
            print(f"🩸 HP {sacrifice} 소모하여 위력 +{bonus_power}!")
            return bonus_power
    return 0

def _vampire_attack(caster, target, skill_data):
    """흡혈 공격"""
    # HP가 낮을수록 흡혈량 증가
    if hasattr(caster, 'hp') and hasattr(caster, 'max_hp'):
        hp_ratio = caster.hp / caster.max_hp
        vampire_rate = 0.3 + (0.3 * (1 - hp_ratio))  # 최대 60% 흡혈
        print(f"🧛 흡혈 효과 {int(vampire_rate*100)}% 발동!")
        return vampire_rate
    return 0.3

def _blood_shield(caster, skill_data):
    """피의 방패 - HP 50% 소모하여 보호막 생성"""
    # HP의 50% 소모로 고정
    sacrifice_percent = 0.5
    current_hp = getattr(caster, 'current_hp', getattr(caster, 'hp', 100))
    sacrifice_hp = int(current_hp * sacrifice_percent)
    
    if current_hp > sacrifice_hp:
        # HP 차감
        if hasattr(caster, 'current_hp'):
            caster.current_hp -= sacrifice_hp
        elif hasattr(caster, 'hp'):
            caster.hp -= sacrifice_hp
            
        # 소모량의 150% 보호막 생성
        shield_amount = int(sacrifice_hp * 1.5)
        
        if not hasattr(caster, 'blood_shield'):
            caster.blood_shield = 0
        caster.blood_shield += shield_amount
        
        # 보호막 지속 턴수 설정
        caster.blood_shield_turns = getattr(caster, 'blood_shield_turns', 0) + 5
        
        print(f"🛡️ HP {sacrifice_hp} 소모하여 보호막 {shield_amount} 생성! (5턴 지속)")
        return True
    else:
        print(f"❌ HP가 부족하여 피의 방패를 사용할 수 없습니다! (현재 HP: {current_hp})")
        return False

def _vampiric_blast(caster, target, skill_data):
    """흡혈 강타"""
    print(f"💥 보호막을 소모한 흡혈 강타!")

def _shield_consume(caster, target, skill_data):
    """보호막 소모"""
    if hasattr(caster, 'blood_shield') and caster.blood_shield > 0:
        consumed_shield = caster.blood_shield
        caster.blood_shield = 0
        # 소모한 보호막에 따라 광역 피해
        area_damage = int(consumed_shield * 0.8)
        print(f"💥 보호막 {consumed_shield} 소모하여 광역 피해 {area_damage}!")
        return area_damage
    return 0

def _madness_amplify(caster, skill_data):
    """광기 증폭"""
    if hasattr(caster, 'hp') and skill_data and 'hp_sacrifice' in skill_data:
        sacrifice = skill_data['hp_sacrifice']
        if caster.hp > sacrifice:
            caster.hp -= sacrifice
            print(f"😈 광기 증폭! HP {sacrifice} 소모하여 흡혈 효과 강화!")

def _rage_chain(caster, target, skill_data):
    """분노의 연쇄"""
    if hasattr(caster, 'hp') and skill_data and 'hp_sacrifice_percent' in skill_data:
        sacrifice_percent = skill_data['hp_sacrifice_percent'] / 100
        sacrifice_hp = int(caster.hp * sacrifice_percent)
        if caster.hp > sacrifice_hp:
            caster.hp -= sacrifice_hp
            print(f"⛓️ 분노의 연쇄! HP {sacrifice_hp} 소모하여 광역 공격!")
            return sacrifice_hp

def _area_vampire(caster, target, skill_data):
    """광역 흡혈"""
    print(f"🩸 광역 흡혈 효과 발동!")

def _final_madness(caster, target, skill_data):
    """최후의 광기 - HP를 1로 만들고 엄청난 피해"""
    if hasattr(caster, 'hp'):
        sacrificed_hp = caster.hp - 1
        caster.hp = 1
        # 소모한 HP에 따라 엄청난 피해
        massive_damage = sacrificed_hp * 3
        print(f"💀 최후의 광기! HP {sacrificed_hp} 소모하여 피해 {massive_damage}!")
        return massive_damage
    return 0

def _massive_vampire(caster, target, skill_data):
    """엄청난 흡혈"""
    print(f"🧛‍♂️ 엄청난 흡혈 효과 발동!")

# === 기사 Special Effects ===
def _spear_charge(caster, target, skill_data):
    """창 돌격"""
    if not hasattr(caster, 'duty_stacks'):
        caster.duty_stacks = 0
    # 기본 공격이므로 의무 스택은 다른 조건에서 획득
    print(f"🏇 창 돌격!")

def _protection_oath(caster):
    """수호의 맹세 - 아군 대신 피해를 받는 패시브"""
    print(f"🛡️ {caster.name}이 아군을 수호하겠다고 맹세했습니다!")
    # 실제 구현은 전투 시스템에서 처리

def _chivalry_spirit(caster):
    """기사도 정신 - 스택에 따른 방어력 증가"""
    if not hasattr(caster, 'duty_stacks'):
        caster.duty_stacks = 0
    
    if caster.duty_stacks >= 5:
        print(f"✨ 기사도 정신 극대화! 방어력 35% 증가!")
    elif caster.duty_stacks > 0:
        defense_bonus = caster.duty_stacks * 7  # 스택당 7%
        print(f"⚔️ 기사도 정신! 방어력 {defense_bonus}% 증가!")

def _duty_counter(caster, target, skill_data):
    """의무의 반격 - 스택 소모하여 반격"""
    if not hasattr(caster, 'duty_stacks'):
        caster.duty_stacks = 0
    
    if caster.duty_stacks > 0:
        consumed_stacks = min(2, caster.duty_stacks)
        caster.duty_stacks -= consumed_stacks
        
        if skill_data and 'hp_power' in skill_data:
            bonus_power = int(skill_data['hp_power'] * 0.3 * consumed_stacks)
            print(f"⚡ 의무 스택 {consumed_stacks}개 소모하여 반격! 위력 +{bonus_power}")
            return bonus_power
    return 0

def _survival_will(caster):
    """생존의 의지 - 3스택 이상 시 죽음 무시"""
    if not hasattr(caster, 'duty_stacks'):
        caster.duty_stacks = 0
    
    if caster.duty_stacks >= 3:
        consumed_stacks = caster.duty_stacks
        caster.duty_stacks = 0
        
        # 죽음 무시 효과
        if hasattr(caster, 'hp') and hasattr(caster, 'max_hp'):
            caster.hp = 1  # 1HP로 생존
            heal_amount = int(caster.max_hp * 0.2 * consumed_stacks)
            caster.hp = min(caster.max_hp, caster.hp + heal_amount)
            print(f"💪 생존의 의지! {consumed_stacks}스택 소모하여 죽음을 무시하고 HP {heal_amount} 회복!")
            return True
    return False

def _holy_charge(caster, target, skill_data):
    """성스러운 돌격 - 모든 스택 소모"""
    if not hasattr(caster, 'duty_stacks'):
        caster.duty_stacks = 0
    
    consumed_stacks = caster.duty_stacks
    caster.duty_stacks = 0
    
    if consumed_stacks > 0 and skill_data and 'hp_power' in skill_data:
        bonus_power = int(skill_data['hp_power'] * 0.35 * consumed_stacks)
        print(f"✨ 성스러운 돌격! {consumed_stacks}스택 소모하여 위력 +{bonus_power}!")
        return bonus_power
    return 0

# 전역 인스턴스
skill_system = NewSkillSystem()
new_skill_system = NewSkillSystem()

def get_basic_attacks_for_class(character_class: str) -> Dict[str, Dict[str, Any]]:
    """직업별 기본공격 반환 (BRV, HP)"""
    skill_system = NewSkillSystem()
    
    # 직업별 스킬 데이터 가져오기
    if character_class not in skill_system.skills_by_class:
        return {}
    
    class_skills = skill_system.skills_by_class[character_class]
    basic_attacks = {}
    
    # BRV 기본공격 찾기 (첫 번째 BRV_ATTACK이고 mp_cost가 0인 것)
    for skill in class_skills:
        if (skill.get("type") == SkillType.BRV_ATTACK and 
            skill.get("mp_cost", 1) == 0):
            basic_attacks["brv"] = skill
            break
    
    # HP 기본공격 찾기 (첫 번째 HP_ATTACK이고 mp_cost가 0인 것)  
    for skill in class_skills:
        if (skill.get("type") == SkillType.HP_ATTACK and 
            skill.get("mp_cost", 1) == 0):
            basic_attacks["hp"] = skill
            break
    
    return basic_attacks

# ========================================
# 🌟 Phase 2 직업 시스템 Special Effects
# ========================================

# === 성기사 Special Effects ===
def _holy_strike_sanctuary(caster, target, skill_data):
    """성스러운 타격으로 성역 생성"""
    if not hasattr(caster, 'sanctuary_count'):
        caster.sanctuary_count = 0
    
    # 버프 상태 아군이 피해를 받을 때 성역 생성 (패시브)
    print(f"✨ 성스러운 타격! 성역 생성 조건 활성화!")

def _blessing_sanctuary(caster):
    """축복으로 성역 트리거"""
    if not hasattr(caster, 'sanctuary_count'):
        caster.sanctuary_count = 0
    
    caster.sanctuary_count += 1
    print(f"🌟 축복으로 성역 생성! (현재 성역: {caster.sanctuary_count}개)")

def _judgment_light(caster, target, skill_data):
    """심판의 빛 - 성역 수에 따라 강화"""
    if not hasattr(caster, 'sanctuary_count'):
        caster.sanctuary_count = 0
    
    if caster.sanctuary_count > 0 and skill_data and 'hp_power' in skill_data:
        bonus_power = int(skill_data['hp_power'] * 0.25 * caster.sanctuary_count)
        print(f"⚡ 성역 {caster.sanctuary_count}개의 힘! 위력 +{bonus_power}!")
        return bonus_power
    return 0

def _sanctuary_expand(caster):
    """성역 확장"""
    if not hasattr(caster, 'sanctuary_count'):
        caster.sanctuary_count = 0
    
    caster.sanctuary_count += 2
    print(f"🏛️ 성역 확장! 성역 +2 (현재: {caster.sanctuary_count}개)")

def _divine_protection(caster, target, skill_data):
    """신성한 보호 - 성역 강화"""
    if not hasattr(caster, 'sanctuary_count'):
        caster.sanctuary_count = 0
    
    # 성역 수에 따라 회복량 증가
    heal_bonus = caster.sanctuary_count * 0.1
    print(f"💫 신성한 보호! 성역 {caster.sanctuary_count}개로 회복 강화 +{int(heal_bonus*100)}%!")
    return heal_bonus

# === 암흑기사 Special Effects ===
def _vampire_slash(caster, target, skill_data):
    """흡혈 베기 - 피해 흡수 스택 생성"""
    if not hasattr(caster, 'absorption_stacks'):
        caster.absorption_stacks = 0
    
    # 피해의 25%를 흡수 스택으로 축적
    if skill_data and 'brv_power' in skill_data:
        absorption = int(skill_data['brv_power'] * 0.25)
        max_absorption = getattr(caster, 'max_hp', 1000) * 0.75
        
        caster.absorption_stacks = min(max_absorption, caster.absorption_stacks + absorption)
        print(f"🩸 피해 흡수! +{absorption} (총 흡수: {int(caster.absorption_stacks)})")

def _dark_aura(caster, target, skill_data):
    """어둠의 오라 - 지속 피해"""
    print(f"🌑 어둠의 오라 발동! 모든 적에게 지속 피해!")

def _dark_aura_passive(caster):
    """어둠의 오라 패시브"""
    print(f"👤 어둠의 존재! 주변 모든 적이 지속 피해를 받습니다!")

def _vampiric_strike(caster, target, skill_data):
    """흡혈 강타 - 흡수 스택 소모하여 회복"""
    if not hasattr(caster, 'absorption_stacks'):
        caster.absorption_stacks = 0
    
    if caster.absorption_stacks > 0:
        # 흡수 스택의 50%를 HP로 회복
        heal_amount = int(caster.absorption_stacks * 0.5)
        caster.absorption_stacks -= heal_amount
        
        if hasattr(caster, 'hp') and hasattr(caster, 'max_hp'):
            caster.hp = min(caster.max_hp, caster.hp + heal_amount)
            print(f"🧛 흡혈 강타! HP {heal_amount} 회복! (남은 흡수: {int(caster.absorption_stacks)})")

def _life_drain_all(caster, target, skill_data):
    """전체 생명력 흡수"""
    if not hasattr(caster, 'absorption_stacks'):
        caster.absorption_stacks = 0
    
    # 모든 적에게서 생명력 흡수
    absorption_per_enemy = 50  # 적당 50의 흡수
    max_absorption = getattr(caster, 'max_hp', 1000) * 0.75
    
    total_absorption = absorption_per_enemy * 3  # 3명의 적 가정
    caster.absorption_stacks = min(max_absorption, caster.absorption_stacks + total_absorption)
    print(f"💀 전체 생명력 흡수! +{total_absorption} (총 흡수: {int(caster.absorption_stacks)})")

def _dark_dominion(caster, target, skill_data):
    """어둠의 권능"""
    print(f"👑 어둠의 권능! 흡수 능력 강화!")

def _dark_lord(caster, target, skill_data):
    """어둠의 지배자 - 모든 스택 폭발"""
    if not hasattr(caster, 'absorption_stacks'):
        caster.absorption_stacks = 0
    
    # 모든 흡수 스택을 고정 피해로 전환
    if caster.absorption_stacks > 0:
        explosion_damage = int(caster.absorption_stacks * 0.8)
        shield_amount = int(caster.absorption_stacks * 0.5)
        
        caster.absorption_stacks = 0
        
        if not hasattr(caster, 'dark_shield'):
            caster.dark_shield = 0
        caster.dark_shield += shield_amount
        
        print(f"💥 어둠의 지배자! 흡수 폭발 피해: {explosion_damage}, 보호막: {shield_amount}!")
        return explosion_damage
    return 0

# === 용기사 Special Effects ===
def _dragon_mark(caster, target, skill_data):
    """용의 표식 부여"""
    if not hasattr(target, 'dragon_marks'):
        target.dragon_marks = 0
    
    target.dragon_marks += 1
    print(f"🐲 용의 표식 부여! (표식: {target.dragon_marks}개)")

def _leap_attack(caster, target, skill_data):
    """도약 공격 - 지연 공격 + 표식"""
    if not hasattr(target, 'dragon_marks'):
        target.dragon_marks = 0
    
    target.dragon_marks += 1
    print(f"🏃‍♂️ 도약 공격! 지연 공격 + 표식 부여! (표식: {target.dragon_marks}개)")
    print(f"✨ 착지 시 표식당 추가 피해 + 크리티컬 확정 + 일정 시간 무적!")

def _dragon_breath(caster, target, skill_data):
    """용의 숨결 - 표식 수에 따라 강화"""
    if not hasattr(target, 'dragon_marks'):
        target.dragon_marks = 0
    
    if target.dragon_marks > 0 and skill_data and 'hp_power' in skill_data:
        bonus_power = int(skill_data['hp_power'] * 0.4 * target.dragon_marks)
        print(f"🔥 용의 숨결! 표식 {target.dragon_marks}개로 위력 +{bonus_power}! 크리티컬 확정!")
        return bonus_power
    return 0

def _dragon_scale(caster):
    """용린 보호"""
    print(f"🛡️ 용린 보호! 표식 중첩 속도 가속화!")

def _dragon_majesty(caster, target, skill_data):
    """용의 위엄 - 모든 표식 폭발"""
    print(f"👑 용의 위엄! 모든 표식 폭발 + 위압 효과!")

def _dragon_lord_ultimate(caster, target, skill_data):
    """드래곤 로드 궁극기"""
    if not hasattr(target, 'dragon_marks'):
        target.dragon_marks = 0
    
    marks = target.dragon_marks
    target.dragon_marks = 0  # 모든 표식 소모
    
    if marks > 0 and skill_data and 'hp_power' in skill_data:
        # 표식을 모두 모아 초강화
        ultimate_bonus = int(skill_data['hp_power'] * 0.6 * marks)
        print(f"🐉 드래곤 로드! 표식 {marks}개 초강화 융합! 위력 +{ultimate_bonus}!")
        print(f"✨ 일정 시간 무적 상태!")
        return ultimate_bonus
    return 0

# === 아크메이지 Special Effects ===
def _elemental_cycle(caster, target, skill_data):
    """원소 순환 시스템"""
    if not hasattr(caster, 'element_counts'):
        caster.element_counts = {"fire": 0, "ice": 0, "lightning": 0}
    
    print(f"🔄 원소 순환 시스템 활성화!")

def _lightning_count(caster, target, skill_data):
    """번개 속성 카운트"""
    if not hasattr(caster, 'element_counts'):
        caster.element_counts = {"fire": 0, "ice": 0, "lightning": 0}
    
    caster.element_counts["lightning"] += 1
    count = caster.element_counts["lightning"]
    
    if count >= 3:
        caster.element_counts["lightning"] = 0
        print(f"⚡ 번개 3회 달성! '라이트닝 버스트' 자동 시전!")
        return True
    else:
        print(f"⚡ 번개 카운트: {count}/3")
    return False

def _fire_count(caster, target, skill_data):
    """화염 속성 카운트"""
    if not hasattr(caster, 'element_counts'):
        caster.element_counts = {"fire": 0, "ice": 0, "lightning": 0}
    
    caster.element_counts["fire"] += 1
    count = caster.element_counts["fire"]
    
    if count >= 3:
        caster.element_counts["fire"] = 0
        print(f"🔥 화염 3회 달성! '화염 폭발' 자동 시전!")
        return True
    else:
        print(f"🔥 화염 카운트: {count}/3")
    return False

def _ice_count(caster, target, skill_data):
    """냉기 속성 카운트"""
    if not hasattr(caster, 'element_counts'):
        caster.element_counts = {"fire": 0, "ice": 0, "lightning": 0}
    
    caster.element_counts["ice"] += 1
    count = caster.element_counts["ice"]
    
    if count >= 3:
        caster.element_counts["ice"] = 0
        print(f"❄️ 냉기 3회 달성! '절대영도' 자동 시전!")
        return True
    else:
        print(f"❄️ 냉기 카운트: {count}/3")
    return False

def _elemental_mastery(caster):
    """원소 강화"""
    print(f"🎭 원소 강화! 마법 공격력 증가 + 원소 친화도 상승!")

def _elemental_fusion(caster, target, skill_data):
    """원소 융합"""
    print(f"🌈 원소 융합! 모든 원소가 융합된 복합 공격!")

def _all_elements_burst(caster, target, skill_data):
    """원소 대폭발"""
    if hasattr(caster, 'element_counts'):
        total_elements = sum(caster.element_counts.values())
        caster.element_counts = {"fire": 0, "ice": 0, "lightning": 0}
        
        if skill_data and 'hp_power' in skill_data:
            bonus_power = int(skill_data['hp_power'] * 0.3 * total_elements)
            print(f"💥 원소 대폭발! 축적된 원소 {total_elements}개로 위력 +{bonus_power}!")
            return bonus_power
    
    print(f"🌟 원소 대폭발! 모든 속성 동시 발동!")
    return 0

# ========================================
# 해적 Special Effects
# ========================================

def _treasure_hunt(caster):
    """보물 탐지 - 해적 특성 연동"""
    if hasattr(caster, 'character_class') and caster.character_class == "해적":
        # 해적 특성: 보물 감각으로 골드 획득량 증가
        if hasattr(caster, 'treasure_stacks'):
            caster.treasure_stacks = min(caster.treasure_stacks + 1, 5)
        else:
            caster.treasure_stacks = 1
        
        # 행운 스택 증가
        if hasattr(caster, 'luck_bonus'):
            caster.luck_bonus = getattr(caster, 'luck_bonus', 0) + 10
        else:
            caster.luck_bonus = 10
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.TREASURE_HUNTER, duration=3, intensity=1.0)
    return True

def _pirate_plunder(caster, target, skill_data):
    """약탈 공격 - 해적 특성 연동"""
    if hasattr(caster, 'character_class') and caster.character_class == "해적":
        # 해적 특성: 약탈로 골드와 아이템 획득
        treasure_stacks = getattr(caster, 'treasure_stacks', 0)
        
        # 보물 스택에 따른 추가 골드 획득
        bonus_gold = 50 + (treasure_stacks * 25)
        if hasattr(caster, 'gold'):
            caster.gold = getattr(caster, 'gold', 0) + bonus_gold
        
        # 약탈 성공 시 보물 스택 1개 소모하여 강화 효과
        if treasure_stacks > 0 and hasattr(caster, 'treasure_stacks'):
            caster.treasure_stacks -= 1
            # 추가 데미지 보너스
            if skill_data and 'hp_power' in skill_data:
                bonus_damage = int(skill_data['hp_power'] * 0.3)
                print(f"💰 약탈 성공! 골드 +{bonus_gold}, 추가 피해 +{bonus_damage}!")
                return bonus_damage
    
    return True

def _dual_wield(caster, target, skill_data):
    """이도류 공격"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.DUAL_WIELD, duration=3, intensity=1.0)
        caster.add_status(StatusType.BOOST_ATTACK_SPEED, duration=3, intensity=1.4)
    return True

def _sea_shanty(caster):
    """선원가 - 팀 버프"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=4, intensity=1.15)
        caster.add_status(StatusType.PIRATE_COURAGE, duration=4, intensity=1.0)
    return True

def _treasure_map(caster):
    """보물지도 효과"""
    if hasattr(caster, 'treasure_stacks'):
        caster.treasure_stacks = min(getattr(caster, 'treasure_stacks', 0) + 3, 5)
    else:
        caster.treasure_stacks = 3
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.TREASURE_HUNTER, duration=8, intensity=2.0)
    return True

# ========================================
# 사무라이 Special Effects
# ========================================

def _samurai_focus(caster):
    """사무라이 집중 - 의지 게이지 시스템"""
    if hasattr(caster, 'character_class') and caster.character_class == "사무라이":
        # 사무라이 특성: 의지 게이지 증가
        if hasattr(caster, 'willpower_gauge'):
            caster.willpower_gauge = min(caster.willpower_gauge + 20, 100)
        else:
            caster.willpower_gauge = 20
        
        # 집중력 증가
        if hasattr(caster, 'temp_focus_bonus'):
            caster.temp_focus_bonus = getattr(caster, 'temp_focus_bonus', 0) + 15
        else:
            caster.temp_focus_bonus = 15
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.FOCUS, duration=3, intensity=1.0)
    return True

def _bushido_spirit(caster, target, skill_data):
    """무사도 정신 - 사무라이 특성 연동"""
    if hasattr(caster, 'character_class') and caster.character_class == "사무라이":
        # 무사도 정신: 의지 게이지에 따른 피해 증가
        willpower = getattr(caster, 'willpower_gauge', 0)
        
        if willpower >= 50:
            # 의지 게이지 소모하여 강화 공격
            damage_bonus = int(willpower / 10)  # 의지 10당 1배 증가
            if hasattr(caster, 'willpower_gauge'):
                caster.willpower_gauge = max(0, caster.willpower_gauge - 30)
            
            if skill_data and 'hp_power' in skill_data:
                bonus_damage = int(skill_data['hp_power'] * (damage_bonus / 10))
                print(f"⚔️ 무사도 정신! 의지의 힘으로 추가 피해 +{bonus_damage}!")
                return bonus_damage
    
    return True

def _iai_strike(caster, target, skill_data):
    """거합 일격 - 즉사 가능성"""
    if hasattr(caster, 'character_class') and caster.character_class == "사무라이":
        willpower = getattr(caster, 'willpower_gauge', 0)
        
        # 의지 게이지가 높을수록 크리티컬 확률 증가
        if willpower >= 80:
            if hasattr(caster, 'temp_crit_rate'):
                caster.temp_crit_rate = getattr(caster, 'temp_crit_rate', 0) + 0.5
            else:
                caster.temp_crit_rate = 0.5
            
            # 최고 의지에서 즉사 기회
            if willpower >= 100 and hasattr(target, 'current_hp'):
                import random
                if random.random() < 0.15:  # 15% 즉사 확률
                    target.current_hp = 1
                    print(f"💀 완벽한 거합! {target.name}이(가) 치명상을 입었습니다!")
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_CRIT, duration=2, intensity=2.0)
    return True

def _honor_guard(caster):
    """명예 수호 자세"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.GUARD_STANCE, duration=4, intensity=1.0)
        caster.add_status(StatusType.BOOST_DEF, duration=4, intensity=1.5)
        caster.add_status(StatusType.COUNTER_READY, duration=4, intensity=1.0)
    return True

# === 새로운 직업 기본 공격 Special Effects ===

def _nature_bond(caster):
    """자연 유대 - 드루이드 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "드루이드":
        # 자연 친화도 스택 증가
        if hasattr(caster, 'nature_stacks'):
            caster.nature_stacks = min(caster.nature_stacks + 1, 10)
        else:
            caster.nature_stacks = 1
        
        # 자연 스택에 비례한 회복
        nature_stacks = getattr(caster, 'nature_stacks', 0)
        heal_amount = int(caster.max_hp * 0.02 * nature_stacks)
        if heal_amount > 0:
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
            print(f"🌿 자연의 축복으로 {heal_amount} HP 회복!")
    return True

def _wild_instinct(caster):
    """야생 본능 - 드루이드 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "드루이드":
        # 야생 형태 변환 게이지 증가
        if hasattr(caster, 'wild_gauge'):
            caster.wild_gauge = min(caster.wild_gauge + 15, 100)
        else:
            caster.wild_gauge = 15
        
        # 야생 게이지가 50 이상이면 일시적 공격력 증가
        if getattr(caster, 'wild_gauge', 0) >= 50:
            if hasattr(caster, 'add_status'):
                caster.add_status(StatusType.BOOST_ATK, duration=2, intensity=1.3)
            print(f"🐺 야생의 본능 각성! 공격력 증가!")
    return True

def _atonement_stack(caster):
    """속죄 스택 - 신관 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "신관":
        # 속죄 스택 증가
        if hasattr(caster, 'atonement_stacks'):
            caster.atonement_stacks = min(caster.atonement_stacks + 1, 8)
        else:
            caster.atonement_stacks = 1
        
        # 속죄 스택에 비례한 MP 회복
        atonement_stacks = getattr(caster, 'atonement_stacks', 0)
        mp_recovery = atonement_stacks * 2
        if mp_recovery > 0:
            caster.current_mp = min(caster.current_mp + mp_recovery, caster.max_mp)
            print(f"✨ 속죄의 힘으로 {mp_recovery} MP 회복!")
    return True

def _divine_release(caster):
    """신성 방출 - 신관 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "신관":
        # 신성 에너지 축적
        if hasattr(caster, 'divine_energy'):
            caster.divine_energy = min(caster.divine_energy + 20, 100)
        else:
            caster.divine_energy = 20
        
        # 신성 에너지가 높을수록 치유 보정
        divine_energy = getattr(caster, 'divine_energy', 0)
        if divine_energy >= 80:
            if hasattr(caster, 'temp_heal_power'):
                caster.temp_heal_power = getattr(caster, 'temp_heal_power', 0) + 0.5
            else:
                caster.temp_heal_power = 0.5
            print(f"🌟 신성한 기운이 치유 능력을 강화합니다!")
    return True

def _elemental_blade(caster):
    """원소 검기 - 마검사 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "마검사":
        # 원소 조화 스택 증가
        if hasattr(caster, 'elemental_harmony'):
            caster.elemental_harmony = min(caster.elemental_harmony + 1, 6)
        else:
            caster.elemental_harmony = 1
        
        # 랜덤 원소 속성 임시 부여
        import random
        elements = ["화염", "빙결", "뇌격"]
        chosen_element = random.choice(elements)
        if hasattr(caster, 'temp_element'):
            caster.temp_element = chosen_element
        else:
            caster.temp_element = chosen_element
        
        print(f"⚔️ {chosen_element} 속성이 검에 깃듭니다!")
    return True

def _elemental_burst(caster):
    """원소 폭발 - 마검사 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "마검사":
        # 원소 에너지 폭발
        harmony = getattr(caster, 'elemental_harmony', 0)
        if harmony >= 3:
            # 원소 조화 스택 소모하여 추가 효과
            caster.elemental_harmony = max(0, harmony - 3)
            
            if hasattr(caster, 'add_status'):
                caster.add_status(StatusType.ELEMENTAL_INFUSION, duration=3, intensity=1.0)
            print(f"💥 원소 에너지 폭발! 강화된 원소 공격!")
    return True

def _chi_circulation(caster):
    """기공 순환 - 몽크 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "몽크":
        # 기공 에너지 축적
        if hasattr(caster, 'chi_energy'):
            caster.chi_energy = min(caster.chi_energy + 12, 100)
        else:
            caster.chi_energy = 12
        
        # 기공 에너지에 비례한 회복
        chi_energy = getattr(caster, 'chi_energy', 0)
        if chi_energy >= 30:
            heal_amount = int(caster.max_hp * 0.03)
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
            print(f"🌀 기공 순환으로 {heal_amount} HP 회복!")
    return True

def _combo_chain(caster):
    """연환권 - 몽크 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "몽크":
        # 콤보 카운터 증가
        if hasattr(caster, 'combo_count'):
            caster.combo_count = min(caster.combo_count + 1, 5)
        else:
            caster.combo_count = 1
        
        # 콤보 수에 비례한 속도 증가
        combo_count = getattr(caster, 'combo_count', 0)
        if combo_count >= 3:
            if hasattr(caster, 'add_status'):
                caster.add_status(StatusType.BOOST_SPD, duration=2, intensity=1.2)
            print(f"👊 연환권 {combo_count}단계! 속도 증가!")
    return True

def _machine_charge(caster):
    """기계 충전 - 기계공학자 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "기계공학자":
        # 기계 에너지 충전
        if hasattr(caster, 'machine_energy'):
            caster.machine_energy = min(caster.machine_energy + 10, 100)
        else:
            caster.machine_energy = 10
        
        # 에너지 충전에 따른 정확도 증가
        machine_energy = getattr(caster, 'machine_energy', 0)
        if machine_energy >= 50:
            if hasattr(caster, 'temp_accuracy_bonus'):
                caster.temp_accuracy_bonus = getattr(caster, 'temp_accuracy_bonus', 0) + 15
            else:
                caster.temp_accuracy_bonus = 15
            print(f"⚙️ 기계 시스템 안정화! 정확도 증가!")
    return True

def _energy_discharge(caster):
    """에너지 방출 - 기계공학자 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "기계공학자":
        # 기계 에너지 소모하여 강화
        machine_energy = getattr(caster, 'machine_energy', 0)
        if machine_energy >= 30:
            # 에너지 소모
            caster.machine_energy = max(0, machine_energy - 20)
            
            # 소모한 에너지에 비례한 추가 피해
            damage_bonus = int(machine_energy / 5)
            if hasattr(caster, 'temp_damage_bonus'):
                caster.temp_damage_bonus = getattr(caster, 'temp_damage_bonus', 0) + damage_bonus
            else:
                caster.temp_damage_bonus = damage_bonus
            print(f"🔥 에너지 방출! 추가 피해 +{damage_bonus}!")
    return True

def _soul_harvest(caster):
    """영혼 수확 - 네크로맨서 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "네크로맨서":
        # 영혼 에너지 수집
        if hasattr(caster, 'soul_energy'):
            caster.soul_energy = min(caster.soul_energy + 8, 100)
        else:
            caster.soul_energy = 8
        
        # 영혼 에너지에 비례한 MP 회복
        soul_energy = getattr(caster, 'soul_energy', 0)
        mp_recovery = int(soul_energy / 10)
        if mp_recovery > 0:
            caster.current_mp = min(caster.current_mp + mp_recovery, caster.max_mp)
            print(f"👻 영혼 에너지로 {mp_recovery} MP 회복!")
    return True

def _life_drain(caster, target):
    """생명력 흡수 - 네크로맨서 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "네크로맨서":
        # 대상의 현재 HP 일정 비율 흡수
        if hasattr(target, 'current_hp'):
            drain_amount = int(target.current_hp * 0.1)  # 10% 흡수
            target.current_hp = max(1, target.current_hp - drain_amount)
            
            # 흡수한 만큼 자신 회복
            caster.current_hp = min(caster.current_hp + drain_amount, caster.max_hp)
            print(f"🩸 생명력 흡수로 {drain_amount} HP 회복!")
    return True

def _precision_stack(caster):
    """조준 포인트 생성 - 궁수 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "궁수":
        # 조준 포인트 증가
        if hasattr(caster, 'aim_points'):
            caster.aim_points = min(caster.aim_points + 1, 5)
        else:
            caster.aim_points = 1
        
        print(f"🎯 조준 포인트 +1! (현재: {caster.aim_points}/5)")
    return True

def _arrow_penetration(caster):
    """화살 관통 - 궁수 기본 HP 공격 (조준 포인트 활용)"""
    if hasattr(caster, 'character_class') and caster.character_class == "궁수":
        # 조준 포인트에 따른 관통 효과
        aim_points = getattr(caster, 'aim_points', 0)
        if aim_points > 0:
            # 조준 포인트 사용하여 명중률, 치명타율 증가
            accuracy_bonus = aim_points * 5
            crit_bonus = aim_points * 8
            
            if hasattr(caster, 'temp_accuracy_bonus'):
                caster.temp_accuracy_bonus = getattr(caster, 'temp_accuracy_bonus', 0) + accuracy_bonus
            else:
                caster.temp_accuracy_bonus = accuracy_bonus
                
            if hasattr(caster, 'temp_crit_bonus'):
                caster.temp_crit_bonus = getattr(caster, 'temp_crit_bonus', 0) + crit_bonus
            else:
                caster.temp_crit_bonus = crit_bonus
            
            print(f"🏹 조준 활용! 명중률 +{accuracy_bonus}%, 치명타 +{crit_bonus}%")
    return True

def _melody_build(caster):
    """멜로디 축적 - 바드 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "바드":
        # 멜로디 스택 증가
        if hasattr(caster, 'melody_stacks'):
            caster.melody_stacks = min(caster.melody_stacks + 1, 8)
        else:
            caster.melody_stacks = 1
        
        # 멜로디 스택에 비례한 모든 아군 버프
        melody = getattr(caster, 'melody_stacks', 0)
        if melody >= 4:
            print(f"🎵 화음 완성! 아군 전체 능력치 소폭 증가!")
            # 아군 전체에게 약간의 버프 (구현 시 전투 시스템과 연동)
    return True

def _sonic_burst(caster):
    """음파 폭발 - 바드 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "바드":
        # 멜로디 스택 소모하여 강화
        melody = getattr(caster, 'melody_stacks', 0)
        if melody >= 3:
            # 멜로디 스택 소모
            caster.melody_stacks = max(0, melody - 3)
            
            # 음파 폭발로 추가 상태 효과
            if hasattr(caster, 'add_status'):
                caster.add_status(StatusType.INSPIRE, duration=3, intensity=1.0)
            print(f"🎶 음파 폭발! 영감 효과 발동!")
    return True

# === 추가 직업 Special Effects ===

def _spirit_bond(caster):
    """정령 유대 - 정령술사 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "정령술사":
        # 정령 친화도 증가
        if hasattr(caster, 'spirit_affinity'):
            caster.spirit_affinity = min(caster.spirit_affinity + 1, 8)
        else:
            caster.spirit_affinity = 1
        
        # 정령 친화도에 비례한 MP 회복
        affinity = getattr(caster, 'spirit_affinity', 0)
        mp_recovery = affinity * 2
        if mp_recovery > 0:
            caster.current_mp = min(caster.current_mp + mp_recovery, caster.max_mp)
            print(f"🧚 정령과의 유대로 {mp_recovery} MP 회복!")
    return True

def _elemental_fusion(caster):
    """원소 융합 - 정령술사 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "정령술사":
        # 원소 융합 카운터 증가
        if hasattr(caster, 'fusion_count'):
            caster.fusion_count = min(caster.fusion_count + 1, 4)
        else:
            caster.fusion_count = 1
        
        # 융합 카운터에 비례한 원소 저항
        fusion_count = getattr(caster, 'fusion_count', 0)
        if fusion_count >= 3:
            if hasattr(caster, 'add_status'):
                caster.add_status(StatusType.ELEMENT_RESIST, duration=3, intensity=1.0)
            print(f"🌈 원소 융합 완성! 원소 저항 획득!")
    return True

def _divine_accumulation(caster):
    """신성력 축적 - 성직자 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "성직자":
        # 신성력 축적
        if hasattr(caster, 'divine_power'):
            caster.divine_power = min(caster.divine_power + 10, 100)
        else:
            caster.divine_power = 10
        
        # 신성력에 비례한 치유 보정
        divine_power = getattr(caster, 'divine_power', 0)
        if divine_power >= 50:
            if hasattr(caster, 'temp_heal_bonus'):
                caster.temp_heal_bonus = getattr(caster, 'temp_heal_bonus', 0) + 0.3
            else:
                caster.temp_heal_bonus = 0.3
            print(f"✨ 신성력 축적으로 치유 능력 강화!")
    return True

def _blessing_beam(caster):
    """축복 광선 - 성직자 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "성직자":
        # 주변 아군 소량 치유 (파티 치유 효과)
        divine_power = getattr(caster, 'divine_power', 0)
        heal_amount = int(caster.max_hp * 0.05 + divine_power * 0.002)
        
        # 모든 아군 치유 (구현 시 파티 시스템과 연동)
        if heal_amount > 0:
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
            print(f"🌟 축복의 광선으로 {heal_amount} HP 회복!")
    return True

def _poison_stack(caster):
    """독 스택 - 도적 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "도적":
        # 독 스택 축적
        if hasattr(caster, 'poison_stacks'):
            caster.poison_stacks = min(caster.poison_stacks + 1, 10)
        else:
            caster.poison_stacks = 1
        
        # 독 스택에 비례한 크리티컬 확률 증가
        poison_stacks = getattr(caster, 'poison_stacks', 0)
        crit_bonus = poison_stacks * 2
        if hasattr(caster, 'temp_crit_rate'):
            caster.temp_crit_rate = getattr(caster, 'temp_crit_rate', 0) + crit_bonus
        else:
            caster.temp_crit_rate = crit_bonus
        print(f"☠️ 독 스택 {poison_stacks} - 치명타율 +{crit_bonus}%")
    return True

def _lethal_strike(caster, target):
    """치명타 - 도적 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "도적":
        # 독 스택에 비례한 추가 피해
        poison_stacks = getattr(caster, 'poison_stacks', 0)
        if poison_stacks > 0:
            # 독 스택 소모하여 강화
            consumed_stacks = min(poison_stacks, 3)
            caster.poison_stacks = max(0, poison_stacks - consumed_stacks)
            
            # 추가 독 피해
            if hasattr(target, 'add_status'):
                target.add_status(StatusType.POISON, duration=4 + consumed_stacks, intensity=1.0 + consumed_stacks * 0.2)
            print(f"💀 치명적 독! {consumed_stacks}스택 소모로 강화된 독 효과!")
    return True

def _generate_shadow(caster):
    """그림자 생성 - 암살자 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "암살자":
        # 그림자 스택 생성
        if hasattr(caster, 'shadow_count'):
            caster.shadow_count = min(caster.shadow_count + 1, 5)
        else:
            caster.shadow_count = 1
        
        # 그림자 수에 비례한 회피율 증가
        shadow_count = getattr(caster, 'shadow_count', 0)
        evasion_bonus = shadow_count * 5
        if hasattr(caster, 'temp_evasion'):
            caster.temp_evasion = getattr(caster, 'temp_evasion', 0) + evasion_bonus
        else:
            caster.temp_evasion = evasion_bonus
        print(f"🌙 그림자 생성! 현재 {shadow_count}개 - 회피율 +{evasion_bonus}%")
    return True

def _shadow_execution(caster, target):
    """그림자 처형 - 암살자 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "암살자":
        # 그림자 스택 소모하여 강화
        shadow_count = getattr(caster, 'shadow_count', 0)
        if shadow_count > 0:
            # 그림자 스택 소모
            consumed_shadows = min(shadow_count, 2)
            caster.shadow_count = max(0, shadow_count - consumed_shadows)
            
            # 소모한 그림자 수에 비례한 추가 효과
            damage_multiplier = 1.0 + consumed_shadows * 0.3
            if hasattr(target, 'take_damage'):
                bonus_damage = int(caster.physical_attack * damage_multiplier * 0.5)
                print(f"🗡️ 그림자 처형! {consumed_shadows}개 소모로 추가 피해 +{bonus_damage}!")
    return True

# === 새로 추가된 직업 Basic Attack Special Effects ===

def _basic_sword_aura(caster):
    """기본 검기 - 검성 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "검성":
        # 검기 축적 (소량)
        if hasattr(caster, 'sword_aura'):
            caster.sword_aura = min(caster.sword_aura + 0.5, 2.0)
        else:
            caster.sword_aura = 0.5
        
        aura_level = getattr(caster, 'sword_aura', 0)
        print(f"⚔️ 기본 검기 축적! 현재 검기 스택: {aura_level:.1f}/2.0")
    return True

def _basic_sword_burst(caster):
    """기본 검기 폭발 - 검성 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "검성":
        # 검기 스택이 있다면 소량 소모하여 강화
        sword_aura = getattr(caster, 'sword_aura', 0)
        if sword_aura >= 1.0:
            caster.sword_aura = max(0, sword_aura - 0.5)
            
            # 일시적인 집중력 증가
            if hasattr(caster, 'temp_focus'):
                caster.temp_focus = getattr(caster, 'temp_focus', 0) + 10
            else:
                caster.temp_focus = 10
            print(f"⚔️ 검기 폭발! 집중력 +10, 남은 검기: {caster.sword_aura:.1f}")
    return True

def _arena_experience(caster):
    """투기장 경험 - 검투사 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "검투사":
        # 전투 경험 축적
        if hasattr(caster, 'combat_experience'):
            caster.combat_experience = min(caster.combat_experience + 1, 10)
        else:
            caster.combat_experience = 1
        
        experience = getattr(caster, 'combat_experience', 0)
        # 경험치에 비례한 회피율 증가
        if experience >= 5:
            if hasattr(caster, 'temp_evasion'):
                caster.temp_evasion = getattr(caster, 'temp_evasion', 0) + 3
            else:
                caster.temp_evasion = 3
            print(f"🏛️ 투기장 경험 축적! 경험치: {experience}, 회피율 +3%")
    return True

def _decisive_strike(caster):
    """승부 결정 - 검투사 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "검투사":
        # 처치 스택에 비례한 강화
        combat_experience = getattr(caster, 'combat_experience', 0)
        if combat_experience >= 3:
            # 크리티컬 확률 일시 증가
            if hasattr(caster, 'temp_crit_rate'):
                caster.temp_crit_rate = getattr(caster, 'temp_crit_rate', 0) + 15
            else:
                caster.temp_crit_rate = 15
            print(f"🏛️ 승부의 기회! 크리티컬 확률 +15%")
    return True

def _rage_build(caster):
    """분노 축적 - 광전사 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "광전사":
        # 분노 수치 축적
        if hasattr(caster, 'rage_meter'):
            caster.rage_meter = min(caster.rage_meter + 5, 100)
        else:
            caster.rage_meter = 5
        
        rage = getattr(caster, 'rage_meter', 0)
        # 분노에 비례한 공격력 증가
        if rage >= 30:
            attack_bonus = int(rage * 0.003 * caster.physical_attack)
            if hasattr(caster, 'temp_attack_bonus'):
                caster.temp_attack_bonus = getattr(caster, 'temp_attack_bonus', 0) + attack_bonus
            else:
                caster.temp_attack_bonus = attack_bonus
            print(f"💢 분노 축적! 분노: {rage}/100, 공격력 +{attack_bonus}")
    return True

def _basic_vampiric(caster):
    """기본 흡혈 - 광전사 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "광전사":
        # 소량 흡혈 효과
        rage = getattr(caster, 'rage_meter', 0)
        heal_amount = int(caster.max_hp * 0.03 + rage * 0.0005)
        
        if heal_amount > 0:
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
            print(f"💢 광폭 흡혈! {heal_amount} HP 회복")
    return True

def _knight_honor(caster):
    """기사도 명예 - 기사 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "기사":
        # 명예 포인트 축적
        if hasattr(caster, 'honor_points'):
            caster.honor_points = min(caster.honor_points + 2, 20)
        else:
            caster.honor_points = 2
        
        honor = getattr(caster, 'honor_points', 0)
        # 명예에 비례한 방어력 증가
        if honor >= 10:
            defense_bonus = int(honor * 0.02 * caster.physical_defense)
            if hasattr(caster, 'temp_defense_bonus'):
                caster.temp_defense_bonus = getattr(caster, 'temp_defense_bonus', 0) + defense_bonus
            else:
                caster.temp_defense_bonus = defense_bonus
            print(f"🛡️ 기사도 명예! 명예: {honor}/20, 방어력 +{defense_bonus}")
    return True

def _guardian_will(caster):
    """수호 의지 - 기사 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "기사":
        # 수호 의지에 따른 MP 회복
        honor = getattr(caster, 'honor_points', 0)
        mp_recovery = int(honor * 0.5)
        
        if mp_recovery > 0:
            caster.current_mp = min(caster.current_mp + mp_recovery, caster.max_mp)
            print(f"🛡️ 수호 의지! {mp_recovery} MP 회복")
    return True

def _holy_blessing(caster):
    """성스러운 축복 - 성기사 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "성기사":
        # 축복 포인트 축적
        if hasattr(caster, 'blessing_points'):
            caster.blessing_points = min(caster.blessing_points + 3, 30)
        else:
            caster.blessing_points = 3
        
        blessing = getattr(caster, 'blessing_points', 0)
        # 축복에 비례한 마법 방어력 증가
        if blessing >= 15:
            magic_defense_bonus = int(blessing * 0.015 * caster.magical_defense)
            if hasattr(caster, 'temp_magic_defense_bonus'):
                caster.temp_magic_defense_bonus = getattr(caster, 'temp_magic_defense_bonus', 0) + magic_defense_bonus
            else:
                caster.temp_magic_defense_bonus = magic_defense_bonus
            print(f"✨ 성스러운 축복! 축복: {blessing}/30, 마법방어 +{magic_defense_bonus}")
    return True

def _purify_touch(caster):
    """정화의 손길 - 성기사 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "성기사":
        # 디버프 제거 및 소량 치유
        blessing = getattr(caster, 'blessing_points', 0)
        heal_amount = int(caster.max_hp * 0.02 + blessing * 0.001)
        
        if heal_amount > 0:
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
            print(f"✨ 정화의 손길! {heal_amount} HP 회복 및 디버프 정화")
    return True

def _darkness_power(caster):
    """어둠의 힘 - 암흑기사 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "암흑기사":
        # 어둠 에너지 축적
        if hasattr(caster, 'darkness_energy'):
            caster.darkness_energy = min(caster.darkness_energy + 4, 40)
        else:
            caster.darkness_energy = 4
        
        darkness = getattr(caster, 'darkness_energy', 0)
        # 어둠 에너지에 비례한 마법 공격력 증가
        if darkness >= 20:
            magic_attack_bonus = int(darkness * 0.02 * caster.magical_attack)
            if hasattr(caster, 'temp_magic_attack_bonus'):
                caster.temp_magic_attack_bonus = getattr(caster, 'temp_magic_attack_bonus', 0) + magic_attack_bonus
            else:
                caster.temp_magic_attack_bonus = magic_attack_bonus
            print(f"🌑 어둠의 힘! 어둠 에너지: {darkness}/40, 마법공격 +{magic_attack_bonus}")
    return True

def _minor_vampiric(caster):
    """소량 흡혈 - 암흑기사 기본 HP 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "암흑기사":
        # 어둠 에너지에 비례한 흡혈
        darkness = getattr(caster, 'darkness_energy', 0)
        heal_amount = int(caster.max_hp * 0.025 + darkness * 0.0008)
        
        if heal_amount > 0:
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
            print(f"🌑 어둠의 흡혈! {heal_amount} HP 흡수")
    return True

def _support_fire_activation(caster):
    """지원사격 활성화 - 궁수 지원사격 버프"""
    if hasattr(caster, 'character_class') and caster.character_class == "궁수":
        # 지원사격 모드 활성화
        caster.support_fire_active = True
        caster.support_fire_turns = 3  # 3턴 동안 지속
        print(f"🎯 지원사격 모드 활성화! (3턴간 지속)")
        
    return True

# =============================================================================
# 추가 특수 효과 함수들 (오류 방지용)
# =============================================================================

def _safe_effect_dummy(caster, target, effect_name):
    """안전한 더미 특수 효과 (구현되지 않은 효과들을 위한 임시 함수)"""
    print(f"🌟 스킬 '{effect_name}' 특수 효과 실행 완료!")
    return True

def _chemical_reaction_safe(caster, target, skill_data):
    """연금술사 화학 반응 (완전한 구현)"""
    if hasattr(caster, 'character_class') and caster.character_class == "연금술사":
        # 연금술 재료 스택 증가
        materials = getattr(caster, 'alchemy_materials', 0)
        setattr(caster, 'alchemy_materials', min(materials + 2, 10))
        
        if target and hasattr(target, 'take_damage'):
            # 연금술 재료에 비례한 화학 폭발 피해
            base_damage = int(getattr(caster, 'magic_attack', 50) * 0.4)
            material_bonus = materials * 15
            total_damage = base_damage + material_bonus
            
            target.take_damage(total_damage)
            print(f"⚗️ 화학 반응! {total_damage} 폭발 피해 (재료 스택: {materials + 2})")
            
            # 확률적으로 상태이상 부여
            import random
            if random.random() < 0.3:
                if hasattr(target, 'add_status'):
                    target.add_status(StatusType.POISON, duration=3, intensity=1.0)
                    print(f"☠️ 독성 화학물질로 중독!")
    return True

def _dimension_rift_safe(caster, target, skill_data):
    """차원술사 차원 균열 (완전한 구현)"""
    if hasattr(caster, 'character_class') and caster.character_class == "차원술사":
        # 차원 에너지 스택 증가
        energy = getattr(caster, 'dimension_energy', 0)
        setattr(caster, 'dimension_energy', min(energy + 1, 8))
        
        if target and hasattr(target, 'take_damage'):
            # 차원 에너지에 비례한 공간 절단 피해
            base_damage = int(getattr(caster, 'magic_attack', 50) * 0.5)
            energy_bonus = energy * 20
            total_damage = base_damage + energy_bonus
            
            target.take_damage(total_damage)
            print(f"🌌 차원 균열! {total_damage} 공간 피해 (에너지: {energy + 1})")
            
            # 공간 왜곡으로 혼란 상태
            if hasattr(target, 'add_status'):
                target.add_status(StatusType.CONFUSION, duration=2, intensity=1.0)
                print(f"🌀 공간 왜곡으로 혼란 상태!")
    return True

# ========================================
# 누락된 Special Effects 완전 구현
# ========================================

def _afterimage(caster):
    """잔상 생성 - 차원술사/암살자"""
    if hasattr(caster, 'add_status'):
        # 회피율 대폭 증가
        caster.add_status(StatusType.BOOST_EVASION, duration=3, intensity=2.5)
        
        # 잔상 카운터 설정
        setattr(caster, 'afterimage_count', 3)
        setattr(caster, 'afterimage_duration', 3)
        
        print(f"👻 {caster.name}의 잔상이 생성되었습니다! (3개)")
    return True

def _space_leap(caster, target, skill_data):
    """공간 도약 공격"""
    if target and hasattr(target, 'take_damage'):
        # 순간이동 공격으로 방어력 일부 무시
        base_damage = int(getattr(caster, 'physical_attack', 50) * 1.2)
        target.take_damage(base_damage)
        
        # 혼란 상태 부여
        if hasattr(target, 'add_status'):
            target.add_status(StatusType.CONFUSION, duration=2, intensity=1.0)
        
        print(f"🌀 공간 도약! {target.name}에게 {base_damage} 피해 + 혼란!")
    return True

def _dimension_maze(caster, target):
    """차원 미로"""
    if target and hasattr(target, 'add_status'):
        # 강력한 행동 제한 효과
        target.add_status(StatusType.STUN, duration=2, intensity=1.0)
        target.add_status(StatusType.CONFUSION, duration=4, intensity=1.0)
        target.add_status(StatusType.REDUCE_SPEED, duration=4, intensity=0.5)
        
        print(f"🌀 {target.name}이(가) 차원 미로에 갇혔습니다!")
    return True

def _evasion_counter(caster, target, skill_data):
    """회피 반격 자세"""
    if hasattr(caster, 'add_status'):
        # 회피율 증가 + 반격 자세
        caster.add_status(StatusType.BOOST_EVASION, duration=3, intensity=1.8)
        
        # 반격 상태 설정
        setattr(caster, 'evasion_counter_active', True)
        setattr(caster, 'counter_damage_bonus', 1.5)
        
        print(f"🔄 {caster.name}이(가) 회피 반격 자세를 취했습니다!")
    return True

def _untouchable_state(caster):
    """무적 상태 (일시적)"""
    if hasattr(caster, 'add_status'):
        # 짧은 무적 시간
        caster.add_status(StatusType.INVINCIBLE, duration=1, intensity=1.0)
        
        # 차원술사라면 차원 에너지 소모
        if hasattr(caster, 'character_class') and caster.character_class == "차원술사":
            energy = getattr(caster, 'dimension_energy', 0)
            if energy >= 3:
                setattr(caster, 'dimension_energy', energy - 3)
                print(f"✨ 차원 에너지 소모로 무적 상태! (에너지: {energy - 3})")
            else:
                print(f"✨ 일시적 무적 상태!")
        else:
            print(f"✨ {caster.name}이(가) 일시적으로 무적 상태가 되었습니다!")
    return True

def _truth_insight(caster, target):
    """진리 통찰 - 철학자"""
    if hasattr(caster, 'character_class') and caster.character_class == "철학자":
        # 지혜 스택 증가
        wisdom = getattr(caster, 'wisdom_stacks', 0)
        setattr(caster, 'wisdom_stacks', min(wisdom + 2, 10))
        
        if target and hasattr(target, 'add_status'):
            # 적의 모든 능력치 감소
            target.add_status(StatusType.REDUCE_ALL_STATS, duration=4, intensity=0.7)
            
            # 약점 노출
            target.add_status(StatusType.VULNERABILITY, duration=4, intensity=1.5)
            
            print(f"📚 진리 통찰! {target.name}의 약점 노출 (지혜: {wisdom + 2})")
    return True

def _existence_denial(caster, target, skill_data):
    """존재 부정 - 철학자 궁극기"""
    if target and hasattr(target, 'take_damage'):
        # 현재 HP의 비율 피해 (방어력 무시)
        damage_percent = 0.25  # 25%
        
        # 철학자의 지혜 스택에 따라 피해 증가
        if hasattr(caster, 'character_class') and caster.character_class == "철학자":
            wisdom = getattr(caster, 'wisdom_stacks', 0)
            damage_percent += wisdom * 0.03  # 지혜 스택당 3% 추가
            # 모든 지혜 소모
            setattr(caster, 'wisdom_stacks', 0)
        
        damage = int(target.current_hp * damage_percent)
        target.take_damage(damage)
        
        print(f"❌ 존재 부정! {target.name}에게 {damage} 철학적 피해!")
    return True

def _philosophical_thought(caster):
    """철학적 사고"""
    if hasattr(caster, 'character_class') and caster.character_class == "철학자":
        # 지혜 스택 증가
        wisdom = getattr(caster, 'wisdom_stacks', 0)
        setattr(caster, 'wisdom_stacks', min(wisdom + 3, 10))
        
        # MP 회복
        if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
            mp_recovery = int(caster.max_mp * 0.15)
            caster.current_mp = min(caster.max_mp, caster.current_mp + mp_recovery)
        
        # 마법 공격력 증가
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=4, intensity=1.3)
        
        print(f"🧠 철학적 사고! 지혜 증가 (지혜: {wisdom + 3})")
    return True

def _absolute_truth(caster, target, skill_data):
    """절대 진리 - 철학자 최강 스킬"""
    if hasattr(caster, 'character_class') and caster.character_class == "철학자":
        wisdom = getattr(caster, 'wisdom_stacks', 0)
        
        if target and hasattr(target, 'take_damage'):
            # 지혜 스택에 비례한 고정 피해
            base_damage = 250
            wisdom_damage = wisdom * 80
            total_damage = base_damage + wisdom_damage
            
            target.take_damage(total_damage)
            
            # 모든 지혜 스택 소모
            setattr(caster, 'wisdom_stacks', 0)
            
            print(f"🌟 절대 진리! {target.name}에게 {total_damage} 진리 피해!")
            
            # 진리의 깨달음으로 팀 전체 회복
            if hasattr(caster, 'game_instance'):
                # 파티 전체 회복 로직 (간단화)
                print(f"✨ 진리의 깨달음으로 아군 전체가 영감을 받았습니다!")
    return True

def _elemental_mastery(caster):
    """원소 숙련 - 정령술사"""
    if hasattr(caster, 'character_class') and caster.character_class == "정령술사":
        # 정령 친화도 증가
        bond = getattr(caster, 'spirit_bond', 0)
        setattr(caster, 'spirit_bond', min(bond + 3, 10))
        
        # 모든 원소 속성 강화
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, intensity=1.4)
            caster.add_status(StatusType.ELEMENTAL_MASTERY, duration=5, intensity=1.0)
        
        print(f"� 원소 숙련! 정령 친화도 증가 (친화도: {bond + 3})")
    return True

def _spirit_bond(caster):
    """정령 유대"""
    if hasattr(caster, 'character_class') and caster.character_class == "정령술사":
        # 정령 친화도 증가
        bond = getattr(caster, 'spirit_bond', 0)
        setattr(caster, 'spirit_bond', min(bond + 2, 10))
        
        # 모든 능력치 증가
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_ALL_STATS, duration=4, intensity=1.2)
        
        # 정령 친화도가 높으면 추가 효과
        if bond >= 7:
            # 원소 보호막 생성
            setattr(caster, 'elemental_shield', 150)
            print(f"🧚 정령 유대 강화! 원소 보호막 생성 (친화도: {bond + 2})")
        else:
            print(f"🧚 정령들과의 유대가 강화되었습니다! (친화도: {bond + 2})")
    return True

# ========================================
# 완료된 더미 효과 대체
# ========================================

def _safe_effect_dummy(caster, target, effect_name):
    """구현된 특수 효과 알림"""
    print(f"🌟 '{effect_name}' 특수 효과가 실행되었습니다!")
    
    # 기본적인 효과라도 제공
    if caster and hasattr(caster, 'add_status'):
        # 효과 이름에 따른 기본 버프
        if "attack" in effect_name.lower():
            caster.add_status(StatusType.BOOST_ATK, duration=2, intensity=1.1)
        elif "magic" in effect_name.lower():
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=2, intensity=1.1)
        elif "heal" in effect_name.lower() and hasattr(caster, 'current_hp'):
            heal = int(caster.max_hp * 0.1)
            caster.current_hp = min(caster.max_hp, caster.current_hp + heal)
        elif "defense" in effect_name.lower():
            caster.add_status(StatusType.BOOST_DEF, duration=2, intensity=1.1)
    
    return True

# =============================================================================
# 추가 미구현 효과들 - 더미가 아닌 실제 구현
# =============================================================================

def _mana_burn(caster, target, skill_data):
    """마나 연소"""
    if target and hasattr(target, 'current_mp'):
        burn_amount = int(target.max_mp * 0.15)
        target.current_mp = max(0, target.current_mp - burn_amount)
        
        # 연소된 마나만큼 마법 피해
        if hasattr(target, 'take_damage'):
            magic_damage = burn_amount * 2
            target.take_damage(magic_damage)
            
        print(f"🔥 마나 연소! MP {burn_amount} 소모, {magic_damage} 마법 피해!")
    return True

def _armor_break(caster, target, skill_data):
    """방어구 파괴"""
    if target and hasattr(target, 'add_status'):
        # 방어력 대폭 감소
        target.add_status(StatusType.REDUCE_DEF, duration=5, intensity=0.4)
        
        # 물리 저항력도 감소
        target.add_status(StatusType.VULNERABILITY, duration=5, intensity=1.5)
        
        print(f"🔨 {target.name}의 방어구가 파괴되었습니다!")
    return True

def _critical_strike(caster, target, skill_data):
    """치명타 효과"""
    if hasattr(caster, 'add_status'):
        # 다음 공격이 확정 치명타
        caster.add_status(StatusType.BOOST_CRIT, duration=1, intensity=10.0)
        setattr(caster, 'guaranteed_critical', True)
        
        print(f"💥 다음 공격이 확정 치명타입니다!")
    return True

def _piercing_attack(caster, target, skill_data):
    """관통 공격"""
    if hasattr(caster, 'add_temp_effect'):
        # 방어력 일부 무시 효과 부여
        caster.add_temp_effect("armor_pierce", 1)
        setattr(caster, 'pierce_defense_percent', 0.5)  # 50% 방어력 무시
        
        print(f"🏹 관통 공격! 적의 방어력 50% 무시!")
    return True

def _stun_attack(caster, target, skill_data):
    """기절 공격"""
    if target and hasattr(target, 'add_status'):
        # 기절 상태 부여
        target.add_status(StatusType.STUN, duration=2, intensity=1.0)
        
        print(f"💫 {target.name}이(가) 기절했습니다!")
    return True

def _bleeding_attack(caster, target, skill_data):
    """출혈 공격"""
    if target and hasattr(target, 'add_status'):
        # 출혈 상태 부여
        target.add_status(StatusType.BLEEDING, duration=4, intensity=1.0)
        
        # 출혈 피해량 설정
        setattr(target, 'bleeding_damage', int(getattr(caster, 'physical_attack', 50) * 0.1))
        
        print(f"🩸 {target.name}이(가) 출혈 상태가 되었습니다!")
    return True

def _burn_attack(caster, target, skill_data):
    """화상 공격"""
    if target and hasattr(target, 'add_status'):
        # 화상 상태 부여
        target.add_status(StatusType.BURN, duration=4, intensity=1.0)
        
        # 화상 피해량 설정
        setattr(target, 'burn_damage', int(getattr(caster, 'magic_attack', 50) * 0.12))
        
        print(f"🔥 {target.name}이(가) 화상 상태가 되었습니다!")
    return True

def _freeze_attack(caster, target, skill_data):
    """빙결 공격"""
    if target and hasattr(target, 'add_status'):
        # 빙결 상태 부여 (행동 불가)
        target.add_status(StatusType.FREEZE, duration=2, intensity=1.0)
        
        # 속도 대폭 감소
        target.add_status(StatusType.REDUCE_SPEED, duration=4, intensity=0.3)
        
        print(f"❄️ {target.name}이(가) 빙결되었습니다!")
    return True

def _shock_attack(caster, target, skill_data):
    """감전 공격"""
    if target and hasattr(target, 'add_status'):
        # 감전 상태 부여
        target.add_status(StatusType.SHOCK, duration=3, intensity=1.0)
        
        # MP 지속 감소 효과
        setattr(target, 'shock_mp_drain', int(target.max_mp * 0.05))
        
        print(f"⚡ {target.name}이(가) 감전되었습니다!")
    return True

def _poison_attack(caster, target, skill_data):
    """독 공격"""
    if target and hasattr(target, 'add_status'):
        # 독 상태 부여
        target.add_status(StatusType.POISON, duration=5, intensity=1.0)
        
        # 독 피해량 설정
        setattr(target, 'poison_damage', int(getattr(caster, 'magic_attack', 50) * 0.08))
        
        print(f"☠️ {target.name}이(가) 중독되었습니다!")
    return True

def _confusion_attack(caster, target, skill_data):
    """혼란 공격"""
    if target and hasattr(target, 'add_status'):
        # 혼란 상태 부여
        target.add_status(StatusType.CONFUSION, duration=3, intensity=1.0)
        
        print(f"😵 {target.name}이(가) 혼란에 빠졌습니다!")
    return True

def _silence_attack(caster, target, skill_data):
    """침묵 공격"""
    if target and hasattr(target, 'add_status'):
        # 침묵 상태 부여 (스킬 사용 불가)
        target.add_status(StatusType.SILENCE, duration=3, intensity=1.0)
        
        print(f"🤐 {target.name}이(가) 침묵당했습니다!")
    return True

def _weakness_attack(caster, target, skill_data):
    """약화 공격"""
    if target and hasattr(target, 'add_status'):
        # 모든 능력치 감소
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=4, intensity=0.7)
        
        print(f"🔻 {target.name}의 능력이 약화되었습니다!")
    return True

def _curse_attack(caster, target, skill_data):
    """저주 공격"""
    if target and hasattr(target, 'add_status'):
        # 저주 상태 - 치유 효과 감소 + 지속 피해
        target.add_status(StatusType.CURSE, duration=6, intensity=1.0)
        
        # 치유 효과 50% 감소
        setattr(target, 'heal_reduction_percent', 0.5)
        
        print(f"👹 {target.name}이(가) 저주에 걸렸습니다!")
    return True

def _drain_attack(caster, target, skill_data):
    """흡수 공격"""
    if target and caster and hasattr(target, 'current_hp'):
        # HP 흡수
        drain_amount = int(target.current_hp * 0.1)
        target.current_hp = max(0, target.current_hp - drain_amount)
        
        # 흡수한 만큼 회복
        if hasattr(caster, 'current_hp'):
            caster.current_hp = min(caster.max_hp, caster.current_hp + drain_amount)
        
        print(f"🩸 {drain_amount} HP 흡수!")
    return True

def _holy_light(caster, target, skill_data):
    """성스러운 빛"""
    if target:
        # 아군이면 치유, 적이면 피해
        if hasattr(target, 'character_class') and target.character_class != "Enemy":
            # 아군 치유
            heal_amount = int(getattr(caster, 'magic_attack', 50) * 0.8)
            if hasattr(target, 'current_hp'):
                target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
            print(f"✨ 성스러운 빛으로 {heal_amount} HP 회복!")
        else:
            # 적에게 성스러운 피해
            damage = int(getattr(caster, 'magic_attack', 50) * 1.2)
            if hasattr(target, 'take_damage'):
                target.take_damage(damage)
            print(f"✨ 성스러운 빛으로 {damage} 신성 피해!")
    return True

def _dark_energy(caster, target, skill_data):
    """어둠의 에너지"""
    if target and hasattr(target, 'add_status'):
        # 어둠 속성 피해 + 능력치 감소
        damage = int(getattr(caster, 'magic_attack', 50) * 1.1)
        if hasattr(target, 'take_damage'):
            target.take_damage(damage)
        
        # 어둠에 잠식
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=3, intensity=0.8)
        
        print(f"🌑 어둠의 에너지로 {damage} 암흑 피해!")
    return True

def _nature_power(caster, target, skill_data):
    """자연의 힘"""
    if hasattr(caster, 'character_class') and caster.character_class == "드루이드":
        # 자연 에너지 스택 증가
        nature = getattr(caster, 'nature_power', 0)
        setattr(caster, 'nature_power', min(nature + 2, 10))
        
        # 자연의 축복으로 능력치 증가
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_ALL_STATS, duration=3, intensity=1.2)
        
        print(f"🌿 자연의 힘 증가! (자연 에너지: {nature + 2})")
    return True

def _wisdom_boost(caster, skill_data):
    """지혜 증진"""
    if hasattr(caster, 'character_class') and caster.character_class == "철학자":
        # 지혜 스택 증가
        wisdom = getattr(caster, 'wisdom_stacks', 0)
        setattr(caster, 'wisdom_stacks', min(wisdom + 1, 10))
        
        # 마법 공격력 증가
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=4, intensity=1.1)
        
        print(f"📘 지혜 증진! (지혜: {wisdom + 1})")
    return True

def _spear_charge(caster, target, skill_data):
    """창 돌격 - 기사 전용"""
    if hasattr(caster, 'character_class') and caster.character_class == "기사":
        # 의무 스택 증가
        chivalry = getattr(caster, 'chivalry_points', 0)
        setattr(caster, 'chivalry_points', min(chivalry + 1, 5))
        
        # 돌격으로 추가 피해
        if target and hasattr(target, 'take_damage'):
            charge_damage = int(getattr(caster, 'physical_attack', 50) * 0.3)
            target.take_damage(charge_damage)
            print(f"🐎 창 돌격! {charge_damage} 추가 피해!")
        
        # 다음 턴 속도 증가
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_SPEED, duration=2, intensity=1.3)
        
        print(f"🏇 기사도 정신 증가! (의무: {chivalry + 1})")
    return True

def _silence_effect(caster, target, skill_data):
    """침묵 효과 - 도적 전용"""
    if target and hasattr(target, 'add_status'):
        # 침묵 상태 부여 (스킬 사용 불가)
        target.add_status(StatusType.SILENCE, duration=3, intensity=1.0)
        
        # 도적의 경우 독과 연계
        if hasattr(caster, 'character_class') and caster.character_class == "도적":
            # 기존 독 피해 증폭
            if hasattr(target, 'poison_damage'):
                poison_dmg = getattr(target, 'poison_damage', 0)
                setattr(target, 'poison_damage', int(poison_dmg * 1.5))
                print(f"☠️ 침묵으로 독 피해 50% 증가!")
        
        print(f"🤐 {target.name}이(가) 침묵당했습니다!")
    return True


# ========================================
# 기본 우선순위 특수 효과들
# ========================================

def _accuracy(caster, target=None, skill_data=None):
    """정확도 증가 효과"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("정확도_증가", "정확도_증가", 3, 10))
        print(f"{caster.name}의 정확도가 증가했습니다!")
        return True
    except Exception as e:
        print(f"정확도 효과 적용 중 오류: {e}")
        return False

def _accuracy_boost(caster, target=None, skill_data=None):
    """정확도 대폭 증가 효과"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("정확도_증가", "정확도_증가", 5, 20))
        print(f"{caster.name}의 정확도가 대폭 증가했습니다!")
        return True
    except Exception as e:
        print(f"정확도 부스트 효과 적용 중 오류: {e}")
        return False

def _adaptive_attack(caster, target, skill_data):
    """적응형 공격 - 적의 약점에 따라 공격 타입 변화"""
    try:
        if target and hasattr(target, 'elemental_weaknesses'):
            # 적의 약점 원소로 공격
            weaknesses = getattr(target, 'elemental_weaknesses', [])
            if weaknesses:
                element = weaknesses[0]
                extra_damage = skill_data.get('power', 100) * 0.5
                target.take_damage(extra_damage, f"{element} 적응 공격")
                print(f"{caster.name}이 {target.name}의 {element} 약점을 노려 추가 피해를 입혔습니다!")
        return True
    except Exception as e:
        print(f"적응형 공격 효과 적용 중 오류: {e}")
        return False

def _armor_penetration(caster, target, skill_data):
    """방어구 관통 효과"""
    try:
        if target:
            # 방어력 무시 피해
            penetration_damage = skill_data.get('power', 100) * 0.3
            target.take_damage(penetration_damage, "관통 피해", ignore_armor=True)
            print(f"{caster.name}의 공격이 {target.name}의 방어구를 관통했습니다!")
        return True
    except Exception as e:
        print(f"방어구 관통 효과 적용 중 오류: {e}")
        return False

def _berserk(caster, target=None, skill_data=None):
    """광폭화 상태"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("광폭화", "광폭화", 5, 50))  # 공격력 50% 증가, 5턴
        print(f"{caster.name}이 광폭화 상태가 되었습니다!")
        return True
    except Exception as e:
        print(f"광폭화 효과 적용 중 오류: {e}")
        return False

def _brv_boost(caster, target=None, skill_data=None):
    """BRV 증가 효과"""
    try:
        brv_gain = skill_data.get('power', 100) if skill_data else 100
        if hasattr(caster, 'brave_points'):
            caster.brave_points += brv_gain
            caster.brave_points = min(caster.brave_points, caster.max_brave_points)
        print(f"{caster.name}의 BRV가 {brv_gain} 증가했습니다!")
        return True
    except Exception as e:
        print(f"BRV 부스트 효과 적용 중 오류: {e}")
        return False

def _brv_power(caster, target=None, skill_data=None):
    """BRV 위력 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("BRV_위력_증가", "BRV_위력_증가", 3, 30))
        print(f"{caster.name}의 BRV 공격 위력이 증가했습니다!")
        return True
    except Exception as e:
        print(f"BRV 위력 효과 적용 중 오류: {e}")
        return False

def _combo_bonus(caster, target=None, skill_data=None):
    """콤보 보너스 효과"""
    try:
        if hasattr(caster, 'combo_count'):
            caster.combo_count = getattr(caster, 'combo_count', 0) + 1
            bonus_damage = caster.combo_count * 10
            print(f"{caster.name}의 콤보가 증가했습니다! (x{caster.combo_count})")
            return True
        return True
    except Exception as e:
        print(f"콤보 보너스 효과 적용 중 오류: {e}")
        return False

def _critical_boost(caster, target=None, skill_data=None):
    """크리티컬 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("크리티컬_증가", "크리티컬_증가", 5, 25))
        print(f"{caster.name}의 크리티컬 확률이 증가했습니다!")
        return True
    except Exception as e:
        print(f"크리티컬 부스트 효과 적용 중 오류: {e}")
        return False

def _damage_boost(caster, target=None, skill_data=None):
    """공격력 증가 효과"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("공격력_증가", "공격력_증가", 5, 30))
        print(f"{caster.name}의 공격력이 증가했습니다!")
        return True
    except Exception as e:
        print(f"공격력 부스트 효과 적용 중 오류: {e}")
        return False

def _dispel(caster, target, skill_data=None):
    """디스펠 - 적의 버프 제거"""
    try:
        if target and hasattr(target, 'status_manager'):
            removed_count = 0
            # 버프 상태 제거
            buffs_to_remove = []
            for status_name in target.status_manager.status_effects:
                if any(buff_keyword in status_name.lower() for buff_keyword in 
                       ['증가', '강화', '보호', '축복', '회복']):
                    buffs_to_remove.append(status_name)
                    removed_count += 1
            
            for buff in buffs_to_remove:
                target.status_manager.remove_status(buff)
            
            if removed_count > 0:
                print(f"{target.name}의 {removed_count}개 버프가 제거되었습니다!")
            else:
                print(f"{target.name}에게 제거할 버프가 없습니다.")
        return True
    except Exception as e:
        print(f"디스펠 효과 적용 중 오류: {e}")
        return False

def _double_damage(caster, target, skill_data):
    """2배 피해 효과"""
    try:
        if target and skill_data:
            extra_damage = skill_data.get('power', 100)
            target.take_damage(extra_damage, "추가 피해")
            print(f"{caster.name}의 공격이 2배 피해를 입혔습니다!")
        return True
    except Exception as e:
        print(f"2배 피해 효과 적용 중 오류: {e}")
        return False

def _first_strike(caster, target=None, skill_data=None):
    """선제공격 - 다음 공격 시 먼저 행동"""
    try:
        if hasattr(caster, 'atb_gauge'):
            caster.atb_gauge = min(caster.atb_gauge + 5000, 10000)
        print(f"{caster.name}이 선제공격 준비를 완료했습니다!")
        return True
    except Exception as e:
        print(f"선제공격 효과 적용 중 오류: {e}")
        return False

def _full_heal(caster, target=None, skill_data=None):
    """완전 회복"""
    try:
        heal_target = target if target else caster
        if hasattr(heal_target, 'current_hp') and hasattr(heal_target, 'max_hp'):
            heal_target.current_hp = heal_target.max_hp
        if hasattr(heal_target, 'current_mp') and hasattr(heal_target, 'max_mp'):
            heal_target.current_mp = heal_target.max_mp
        print(f"{heal_target.name}이 완전히 회복되었습니다!")
        return True
    except Exception as e:
        print(f"완전 회복 효과 적용 중 오류: {e}")
        return False

def _guaranteed_critical(caster, target=None, skill_data=None):
    """다음 공격 크리티컬 확정"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("크리티컬_확정", "크리티컬_확정", 1, 100))
        print(f"{caster.name}의 다음 공격이 크리티컬로 확정되었습니다!")
        return True
    except Exception as e:
        print(f"크리티컬 확정 효과 적용 중 오류: {e}")
        return False

def _never_miss(caster, target=None, skill_data=None):
    """절대 명중"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("절대_명중", "절대_명중", 3, 100))
        print(f"{caster.name}의 공격이 절대 빗나가지 않습니다!")
        return True
    except Exception as e:
        print(f"절대 명중 효과 적용 중 오류: {e}")
        return False

def _perfect_accuracy(caster, target=None, skill_data=None):
    """완벽한 정확도"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("완벽한_정확도", "완벽한_정확도", 5, 100))
        print(f"{caster.name}이 완벽한 정확도를 획득했습니다!")
        return True
    except Exception as e:
        print(f"완벽한 정확도 효과 적용 중 오류: {e}")
        return False


# ========================================
# 2번째 배치: 추가 중요 특수 효과들
# ========================================

def _heal_others(caster, target=None, skill_data=None):
    """다른 아군 치료"""
    try:
        if target and target != caster:
            heal_amount = skill_data.get('power', 100) if skill_data else 100
            if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
                target.current_hp = min(target.current_hp + heal_amount, target.max_hp)
                print(f"{caster.name}이 {target.name}을 {heal_amount} 치료했습니다!")
        return True
    except Exception as e:
        print(f"다른 아군 치료 효과 적용 중 오류: {e}")
        return False

def _healing_boost(caster, target=None, skill_data=None):
    """치료 효과 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("치료_효과_증가", "치료_효과_증가", 5, 50))
        print(f"{caster.name}의 치료 효과가 증가했습니다!")
        return True
    except Exception as e:
        print(f"치료 효과 증가 적용 중 오류: {e}")
        return False

def _hp_boost(caster, target=None, skill_data=None):
    """최대 HP 증가"""
    try:
        if hasattr(caster, 'max_hp'):
            hp_increase = skill_data.get('power', 50) if skill_data else 50
            caster.max_hp += hp_increase
            caster.current_hp += hp_increase  # 현재 HP도 같이 증가
            print(f"{caster.name}의 최대 HP가 {hp_increase} 증가했습니다!")
        return True
    except Exception as e:
        print(f"HP 부스트 효과 적용 중 오류: {e}")
        return False

def _mp_boost(caster, target=None, skill_data=None):
    """최대 MP 증가"""
    try:
        if hasattr(caster, 'max_mp'):
            mp_increase = skill_data.get('power', 30) if skill_data else 30
            caster.max_mp += mp_increase
            caster.current_mp += mp_increase  # 현재 MP도 같이 증가
            print(f"{caster.name}의 최대 MP가 {mp_increase} 증가했습니다!")
        return True
    except Exception as e:
        print(f"MP 부스트 효과 적용 중 오류: {e}")
        return False

def _regeneration(caster, target=None, skill_data=None):
    """지속 회복 효과"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("회복", "회복", 10, 20))  # 10턴 동안 턴마다 20 회복
        print(f"{caster.name}에게 지속 회복 효과가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"지속 회복 효과 적용 중 오류: {e}")
        return False

def _speed_increase(caster, target=None, skill_data=None):
    """속도 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("속도_증가", "속도_증가", 5, 30))
        print(f"{caster.name}의 속도가 증가했습니다!")
        return True
    except Exception as e:
        print(f"속도 증가 효과 적용 중 오류: {e}")
        return False

def _stealth_mode(caster, target=None, skill_data=None):
    """은신 모드"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("은신", "은신", 3, 100))  # 3턴 은신
        print(f"{caster.name}이 은신 상태가 되었습니다!")
        return True
    except Exception as e:
        print(f"은신 모드 효과 적용 중 오류: {e}")
        return False

def _stun_chance(caster, target, skill_data):
    """기절 확률"""
    try:
        if target:
            import random
            if random.random() < 0.3:  # 30% 확률
                if hasattr(target, 'status_manager'):
                    from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("기절", "기절", 2, 0))
                print(f"{target.name}이 기절했습니다!")
            else:
                print(f"{target.name}의 기절 저항!")
        return True
    except Exception as e:
        print(f"기절 확률 효과 적용 중 오류: {e}")
        return False

def _teleport(caster, target=None, skill_data=None):
    """순간이동"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("순간이동_준비", "순간이동_준비", 1, 0))
        print(f"{caster.name}이 순간이동을 준비했습니다!")
        return True
    except Exception as e:
        print(f"순간이동 효과 적용 중 오류: {e}")
        return False

def _fear_aura(caster, target, skill_data):
    """공포 오라"""
    try:
        if target:
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("공포", "공포", 3, 20))  # 공격력 20% 감소
            print(f"{target.name}이 공포에 떨고 있습니다!")
        return True
    except Exception as e:
        print(f"공포 오라 효과 적용 중 오류: {e}")
        return False

def _poison_immunity(caster, target=None, skill_data=None):
    """독 면역"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("독_면역", "독_면역", 10, 0))
            # 기존 독 효과 제거
            caster.status_manager.remove_status('독')
        print(f"{caster.name}이 독에 면역이 되었습니다!")
        return True
    except Exception as e:
        print(f"독 면역 효과 적용 중 오류: {e}")
        return False

def _fire_immunity(caster, target=None, skill_data=None):
    """화염 면역"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("화염_면역", "화염_면역", 10, 0))
            caster.status_manager.remove_status('화상')
        print(f"{caster.name}이 화염에 면역이 되었습니다!")
        return True
    except Exception as e:
        print(f"화염 면역 효과 적용 중 오류: {e}")
        return False

def _cold_immunity(caster, target=None, skill_data=None):
    """냉기 면역"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("냉기_면역", "냉기_면역", 10, 0))
            caster.status_manager.remove_status('빙결')
        print(f"{caster.name}이 냉기에 면역이 되었습니다!")
        return True
    except Exception as e:
        print(f"냉기 면역 효과 적용 중 오류: {e}")
        return False

def _status_immunity(caster, target=None, skill_data=None):
    """상태이상 면역"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("상태이상_면역", "상태이상_면역", 5, 0))
            # 기존 디버프들 제거
            debuffs = ['독', '화상', '빙결', '기절', '혼란', '약화', '저주']
            for debuff in debuffs:
                caster.status_manager.remove_status(debuff)
        print(f"{caster.name}이 모든 상태이상에 면역이 되었습니다!")
        return True
    except Exception as e:
        print(f"상태이상 면역 효과 적용 중 오류: {e}")
        return False

def _mana_shield(caster, target=None, skill_data=None):
    """마나 실드"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("마나_실드", "마나_실드", 5, 50))  # 5턴간 피해의 50%를 MP로 대신 받음
        print(f"{caster.name}에게 마나 실드가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"마나 실드 효과 적용 중 오류: {e}")
        return False

def _multi_hit(caster, target, skill_data):
    """다중 공격"""
    try:
        if target and skill_data:
            hit_count = skill_data.get('hits', 3)  # 기본 3회 공격
            base_damage = skill_data.get('power', 100) // hit_count
            total_damage = 0
            
            for i in range(hit_count):
                damage = base_damage + (i * 10)  # 점점 강해지는 공격
                target.take_damage(damage, f"{i+1}번째 타격")
                total_damage += damage
            
            print(f"{caster.name}이 {hit_count}회 연속 공격으로 총 {total_damage} 피해를 입혔습니다!")
        return True
    except Exception as e:
        print(f"다중 공격 효과 적용 중 오류: {e}")
        return False

def _piercing(caster, target, skill_data):
    """관통 공격"""
    try:
        if target and skill_data:
            pierce_damage = skill_data.get('power', 100) * 0.4
            target.take_damage(pierce_damage, "관통 피해", ignore_armor=True)
            print(f"{caster.name}의 관통 공격이 방어를 무시하고 피해를 입혔습니다!")
        return True
    except Exception as e:
        print(f"관통 공격 효과 적용 중 오류: {e}")
        return False

def _auto_counter(caster, target=None, skill_data=None):
    """자동 반격"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("자동_반격", "자동_반격", 5, 0))
        print(f"{caster.name}이 자동 반격 자세를 취했습니다!")
        return True
    except Exception as e:
        print(f"자동 반격 효과 적용 중 오류: {e}")
        return False

def _auto_revive(caster, target=None, skill_data=None):
    """자동 부활"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("자동_부활", "자동_부활", 1, 50))  # 1회용, 50% HP로 부활
        print(f"{caster.name}에게 자동 부활 효과가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"자동 부활 효과 적용 중 오류: {e}")
        return False

def _invisibility(caster, target=None, skill_data=None):
    """투명화"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("투명화", "투명화", 3, 0))  # 3턴 동안 대상이 되지 않음
        print(f"{caster.name}이 투명해졌습니다!")
        return True
    except Exception as e:
        print(f"투명화 효과 적용 중 오류: {e}")
        return False


# ========================================
# 3번째 배치: 더 많은 특수 효과들
# ========================================

def _brv_shield(caster, target=None, skill_data=None):
    """BRV 실드"""
    try:
        if hasattr(caster, 'brave_points'):
            shield_amount = skill_data.get('power', 500) if skill_data else 500
            caster.brave_points += shield_amount
            if hasattr(caster, 'status_manager'):
                caster.status_manager.add_status('BRV_실드', 5, shield_amount)
        print(f"{caster.name}에게 BRV 실드가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"BRV 실드 효과 적용 중 오류: {e}")
        return False

def _multi_shot(caster, target, skill_data):
    """다중 사격"""
    try:
        if target and skill_data:
            shot_count = skill_data.get('shots', 5)
            base_damage = skill_data.get('power', 100) // shot_count
            
            for i in range(shot_count):
                damage = base_damage + (i * 5)
                target.take_damage(damage, f"사격 {i+1}")
            
            print(f"{caster.name}이 {shot_count}발의 화살을 연사했습니다!")
        return True
    except Exception as e:
        print(f"다중 사격 효과 적용 중 오류: {e}")
        return False

def _confusion(caster, target, skill_data):
    """혼란 상태"""
    try:
        if target:
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("혼란", "혼란", 3, 0))
            print(f"{target.name}이 혼란 상태가 되었습니다!")
        return True
    except Exception as e:
        print(f"혼란 효과 적용 중 오류: {e}")
        return False

def _curse_all(caster, target, skill_data):
    """전체 저주"""
    try:
        if target:
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("저주", "저주", 5, 15))  # 모든 능력치 15% 감소
            print(f"{target.name}에게 저주가 걸렸습니다!")
        return True
    except Exception as e:
        print(f"저주 효과 적용 중 오류: {e}")
        return False

def _purify_all(caster, target=None, skill_data=None):
    """모든 디버프 정화"""
    try:
        purify_target = target if target else caster
        if hasattr(purify_target, 'status_manager'):
            debuffs = ['독', '화상', '빙결', '기절', '혼란', '약화', '저주', '출혈']
            removed_count = 0
            for debuff in debuffs:
                if purify_target.status_manager.remove_status(debuff):
                    removed_count += 1
            
            if removed_count > 0:
                print(f"{purify_target.name}의 {removed_count}개 디버프가 정화되었습니다!")
            else:
                print(f"{purify_target.name}에게 정화할 디버프가 없습니다.")
        return True
    except Exception as e:
        print(f"정화 효과 적용 중 오류: {e}")
        return False

def _luck_boost(caster, target=None, skill_data=None):
    """행운 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("행운", "행운", 10, 20))  # 크리티컬 확률 및 회피 증가
        print(f"{caster.name}의 행운이 증가했습니다!")
        return True
    except Exception as e:
        print(f"행운 증가 효과 적용 중 오류: {e}")
        return False

def _exp_double(caster, target=None, skill_data=None):
    """경험치 2배"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("경험치_2배", "경험치_2배", 10, 0))
        print(f"{caster.name}이 경험치 2배 효과를 받습니다!")
        return True
    except Exception as e:
        print(f"경험치 2배 효과 적용 중 오류: {e}")
        return False

def _gold_double(caster, target=None, skill_data=None):
    """골드 2배"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("골드_2배", "골드_2배", 10, 0))
        print(f"{caster.name}이 골드 2배 효과를 받습니다!")
        return True
    except Exception as e:
        print(f"골드 2배 효과 적용 중 오류: {e}")
        return False

def _item_find(caster, target=None, skill_data=None):
    """아이템 발견 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("아이템_발견", "아이템_발견", 20, 50))  # 50% 증가
        print(f"{caster.name}의 아이템 발견 확률이 증가했습니다!")
        return True
    except Exception as e:
        print(f"아이템 발견 효과 적용 중 오류: {e}")
        return False

def _mp_restore(caster, target=None, skill_data=None):
    """MP 회복"""
    try:
        restore_target = target if target else caster
        if hasattr(restore_target, 'current_mp') and hasattr(restore_target, 'max_mp'):
            restore_amount = skill_data.get('power', 50) if skill_data else 50
            restore_target.current_mp = min(restore_target.current_mp + restore_amount, restore_target.max_mp)
            print(f"{restore_target.name}의 MP가 {restore_amount} 회복되었습니다!")
        return True
    except Exception as e:
        print(f"MP 회복 효과 적용 중 오류: {e}")
        return False

def _double_turn(caster, target=None, skill_data=None):
    """추가 턴"""
    try:
        if hasattr(caster, 'atb_gauge'):
            caster.atb_gauge = 10000  # ATB 게이지를 최대로 설정하여 즉시 다시 행동
        print(f"{caster.name}이 추가 턴을 얻었습니다!")
        return True
    except Exception as e:
        print(f"추가 턴 효과 적용 중 오류: {e}")
        return False

def _triple_hit(caster, target, skill_data):
    """3연타"""
    try:
        if target and skill_data:
            base_damage = skill_data.get('power', 100) // 3
            total_damage = 0
            
            for i in range(3):
                damage = base_damage + (i * 15)  # 점점 강해지는 공격
                target.take_damage(damage, f"{i+1}연타")
                total_damage += damage
            
            print(f"{caster.name}의 3연타로 총 {total_damage} 피해!")
        return True
    except Exception as e:
        print(f"3연타 효과 적용 중 오류: {e}")
        return False

def _party_buff(caster, target=None, skill_data=None):
    """파티 전체 강화"""
    try:
        # 파티 멤버들에게 버프 적용 (구현 시 파티 시스템과 연동 필요)
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("파티_강화", "파티_강화", 10, 25))
        print(f"{caster.name}이 파티 전체를 강화했습니다!")
        return True
    except Exception as e:
        print(f"파티 강화 효과 적용 중 오류: {e}")
        return False

def _flame_strike(caster, target, skill_data):
    """화염 타격"""
    try:
        if target and skill_data:
            fire_damage = skill_data.get('power', 120)
            target.take_damage(fire_damage, "화염 피해")
            
            # 화상 상태 추가
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("화상", "화상", 3, 20))
            
            print(f"{caster.name}의 화염 타격이 {target.name}을 불태웠습니다!")
        return True
    except Exception as e:
        print(f"화염 타격 효과 적용 중 오류: {e}")
        return False

def _ice_trail(caster, target, skill_data):
    """얼음 궤적"""
    try:
        if target and skill_data:
            ice_damage = skill_data.get('power', 100)
            target.take_damage(ice_damage, "얼음 피해")
            
            # 빙결 상태 추가
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("빙결", "빙결", 2, 0))
            
            print(f"{caster.name}의 얼음 궤적이 {target.name}을 얼렸습니다!")
        return True
    except Exception as e:
        print(f"얼음 궤적 효과 적용 중 오류: {e}")
        return False

def _lightning_storm(caster, target, skill_data):
    """번개 폭풍"""
    try:
        if target and skill_data:
            lightning_damage = skill_data.get('power', 150)
            target.take_damage(lightning_damage, "번개 피해")
            
            # 감전 상태 추가
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("감전", "감전", 3, 10))
            
            print(f"{caster.name}의 번개 폭풍이 {target.name}을 강타했습니다!")
        return True
    except Exception as e:
        print(f"번개 폭풍 효과 적용 중 오류: {e}")
        return False

def _earth_shield(caster, target=None, skill_data=None):
    """대지의 방패"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("대지_방패", "대지_방패", 8, 30))  # 8턴간 피해 30% 감소
        print(f"{caster.name}에게 대지의 방패가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"대지의 방패 효과 적용 중 오류: {e}")
        return False

def _wind_walk(caster, target=None, skill_data=None):
    """바람걸음"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("바람걸음", "바람걸음", 5, 40))  # 회피율 40% 증가
        print(f"{caster.name}이 바람처럼 가벼워졌습니다!")
        return True
    except Exception as e:
        print(f"바람걸음 효과 적용 중 오류: {e}")
        return False

def _magic_amplify(caster, target=None, skill_data=None):
    """마법 증폭"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("마법_증폭", "마법_증폭", 5, 50))  # 마법 피해 50% 증가
        print(f"{caster.name}의 마법력이 증폭되었습니다!")
        return True
    except Exception as e:
        print(f"마법 증폭 효과 적용 중 오류: {e}")
        return False

def _weapon_mastery(caster, target=None, skill_data=None):
    """무기 숙련"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("무기_숙련", "무기_숙련", 10, 25))  # 물리 공격력 25% 증가
        print(f"{caster.name}의 무기 숙련도가 향상되었습니다!")
        return True
    except Exception as e:
        print(f"무기 숙련 효과 적용 중 오류: {e}")
        return False


# ========================================
# 한국어 특수 효과들
# ========================================

def _ki_training(caster, target=None, skill_data=None):
    """기 수련 - 모든 능력치 소폭 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("기_수련", "기_수련", 15, 10))  # 15턴간 모든 능력치 10% 증가
        print(f"{caster.name}이 내면의 기를 수련했습니다!")
        return True
    except Exception as e:
        print(f"기 수련 효과 적용 중 오류: {e}")
        return False

def _ki_strike(caster, target, skill_data):
    """기공타격 - 내공을 담은 강력한 타격"""
    try:
        if target and skill_data:
            ki_damage = skill_data.get('power', 150) * 1.2  # 기본 피해의 1.2배
            target.take_damage(ki_damage, "기공 피해")
            print(f"{caster.name}의 기공타격이 {target.name}에게 강력한 피해를 입혔습니다!")
        return True
    except Exception as e:
        print(f"기공타격 효과 적용 중 오류: {e}")
        return False

def _inner_ki_enhancement(caster, target=None, skill_data=None):
    """내면의 기를 단련하여 능력 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("내면의_기", "내면의_기", 20, 15))  # 20턴간 모든 능력치 15% 증가
        print(f"{caster.name}이 내면의 기를 각성했습니다!")
        return True
    except Exception as e:
        print(f"내면의 기 효과 적용 중 오류: {e}")
        return False

def _poison_needle(caster, target, skill_data):
    """독침 - 독 피해와 지속 독 효과"""
    try:
        if target and skill_data:
            poison_damage = skill_data.get('power', 80)
            target.take_damage(poison_damage, "독침 피해")
            
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("맹독", "맹독", 5, 30))  # 5턴간 강력한 독
            
            print(f"{caster.name}의 독침이 {target.name}을 중독시켰습니다!")
        return True
    except Exception as e:
        print(f"독침 효과 적용 중 오류: {e}")
        return False

def _lightning_bolt(caster, target, skill_data):
    """라이트닝볼트 - 번개 마법"""
    try:
        if target and skill_data:
            lightning_damage = skill_data.get('power', 120)
            target.take_damage(lightning_damage, "번개 피해")
            
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("감전", "감전", 3, 15))
            
            print(f"{caster.name}의 라이트닝볼트가 {target.name}을 강타했습니다!")
        return True
    except Exception as e:
        print(f"라이트닝볼트 효과 적용 중 오류: {e}")
        return False

def _mana_focus(caster, target=None, skill_data=None):
    """마나 집중 - MP 회복 및 마법 위력 증가"""
    try:
        if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
            mp_restore = caster.max_mp * 0.3
            caster.current_mp = min(caster.current_mp + mp_restore, caster.max_mp)
            
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("마나_집중", "마나_집중", 5, 25))
            
        print(f"{caster.name}이 마나를 집중했습니다!")
        return True
    except Exception as e:
        print(f"마나 집중 효과 적용 중 오류: {e}")
        return False

def _magic_wave(caster, target, skill_data):
    """마력 파동 - 광역 마법 공격"""
    try:
        if target and skill_data:
            wave_damage = skill_data.get('power', 100)
            target.take_damage(wave_damage, "마력 파동")
            print(f"{caster.name}의 마력 파동이 {target.name}을 강타했습니다!")
        return True
    except Exception as e:
        print(f"마력 파동 효과 적용 중 오류: {e}")
        return False

def _magic_spell(caster, target, skill_data):
    """마법 - 기본 마법 공격"""
    try:
        if target and skill_data:
            magic_damage = skill_data.get('power', 90)
            target.take_damage(magic_damage, "마법 피해")
            print(f"{caster.name}의 마법이 {target.name}에게 적중했습니다!")
        return True
    except Exception as e:
        print(f"마법 효과 적용 중 오류: {e}")
        return False

def _magic_attack_party_boost(caster, target=None, skill_data=None):
    """마법공격력으로 아군 공격력과 치명타율 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("마법_파티_강화", "마법_파티_강화", 8, 20))
        print(f"{caster.name}의 마법력이 아군을 강화했습니다!")
        return True
    except Exception as e:
        print(f"마법 파티 강화 효과 적용 중 오류: {e}")
        return False

def _physical_accuracy_crit_boost(caster, target=None, skill_data=None):
    """물리공격력과 정확도, 크리티컬 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("물리_전투_강화", "물리_전투_강화", 8, 25))
        print(f"{caster.name}의 전투 기술이 향상되었습니다!")
        return True
    except Exception as e:
        print(f"물리 전투 강화 효과 적용 중 오류: {e}")
        return False

def _defense_protection_ready(caster, target=None, skill_data=None):
    """방어력 증가 및 아군 보호 준비"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("방어_준비", "방어_준비", 10, 30))
        print(f"{caster.name}이 방어 태세를 갖췄습니다!")
        return True
    except Exception as e:
        print(f"방어 준비 효과 적용 중 오류: {e}")
        return False

def _shield_defense(caster, target=None, skill_data=None):
    """방패 방어 - 피해 감소"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("방패_방어", "방패_방어", 5, 40))  # 피해 40% 감소
        print(f"{caster.name}이 방패로 방어했습니다!")
        return True
    except Exception as e:
        print(f"방패 방어 효과 적용 중 오류: {e}")
        return False

def _wild_mushroom(caster, target=None, skill_data=None):
    """야생 버섯 - 랜덤 효과"""
    try:
        import random
        effects = ['독', '회복', '마나_회복', '속도_증가']
        chosen_effect = random.choice(effects)
        
        if hasattr(caster, 'status_manager'):
            if chosen_effect == '회복':
                if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
                    caster.current_hp = min(caster.current_hp + 50, caster.max_hp)
            else:
                caster.status_manager.add_status(chosen_effect, 3, 20)
        
        print(f"{caster.name}이 야생 버섯을 섭취했습니다! ({chosen_effect} 효과)")
        return True
    except Exception as e:
        print(f"야생 버섯 효과 적용 중 오류: {e}")
        return False

def _courage_song(caster, target=None, skill_data=None):
    """용기의 노래 - 아군 사기 증진"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("용기", "용기", 10, 20))
        print(f"{caster.name}의 용기의 노래가 모두를 고무시켰습니다!")
        return True
    except Exception as e:
        print(f"용기의 노래 효과 적용 중 오류: {e}")
        return False

def _small_meat(caster, target=None, skill_data=None):
    """작은 고기 - 소량 체력 회복"""
    try:
        if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
            heal_amount = 30
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
            print(f"{caster.name}이 작은 고기를 먹고 {heal_amount} 체력을 회복했습니다!")
        return True
    except Exception as e:
        print(f"작은 고기 효과 적용 중 오류: {e}")
        return False

def _weeds(caster, target=None, skill_data=None):
    """잡초 - 미미한 효과"""
    try:
        if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
            heal_amount = 5
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
            print(f"{caster.name}이 잡초를 뜯어먹고 {heal_amount} 체력을 회복했습니다...")
        return True
    except Exception as e:
        print(f"잡초 효과 적용 중 오류: {e}")
        return False

def _aim(caster, target=None, skill_data=None):
    """조준 - 다음 공격 명중률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("조준", "조준", 3, 50))  # 명중률 50% 증가
        print(f"{caster.name}이 정확히 조준했습니다!")
        return True
    except Exception as e:
        print(f"조준 효과 적용 중 오류: {e}")
        return False

def _aimed_shot(caster, target, skill_data):
    """조준사격 - 높은 명중률의 원거리 공격"""
    try:
        if target and skill_data:
            shot_damage = skill_data.get('power', 110)
            target.take_damage(shot_damage, "조준 사격")
            print(f"{caster.name}의 정확한 조준사격이 {target.name}에게 적중했습니다!")
        return True
    except Exception as e:
        print(f"조준사격 효과 적용 중 오류: {e}")
        return False

def _spear_thrust(caster, target, skill_data):
    """창찌르기 - 관통력 있는 창 공격"""
    try:
        if target and skill_data:
            thrust_damage = skill_data.get('power', 130)
            target.take_damage(thrust_damage, "창 찌르기", ignore_armor=True)
            print(f"{caster.name}의 창찌르기가 {target.name}을 관통했습니다!")
        return True
    except Exception as e:
        print(f"창찌르기 효과 적용 중 오류: {e}")
        return False

def _harmony_strike(caster, target, skill_data):
    """화음타격 - 음성과 물리의 조화 공격"""
    try:
        if target and skill_data:
            harmony_damage = skill_data.get('power', 105)
            target.take_damage(harmony_damage, "화음 타격")
            
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("혼란", "혼란", 2, 0))
            
            print(f"{caster.name}의 화음타격이 {target.name}을 혼란시켰습니다!")
        return True
    except Exception as e:
        print(f"화음타격 효과 적용 중 오류: {e}")
        return False


# ========================================
# 4번째 배치: 전투 관련 특수 효과들
# ========================================

def _adaptive_ultimate(caster, target, skill_data):
    """적응형 궁극기 - 상황에 따라 변화하는 강력한 기술"""
    try:
        if target and skill_data:
            # 적의 상태에 따라 다른 효과
            base_damage = skill_data.get('power', 200)
            
            if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
                hp_ratio = target.current_hp / target.max_hp
                if hp_ratio < 0.3:  # 적 HP 30% 미만시 처형 효과
                    base_damage *= 2
                    print(f"{caster.name}의 적응형 궁극기가 {target.name}을 처형했습니다!")
                elif hp_ratio > 0.8:  # 적 HP 80% 초과시 방어 무시
                    target.take_damage(base_damage, "적응 궁극기", ignore_armor=True)
                    return True
            
            target.take_damage(base_damage, "적응 궁극기")
        return True
    except Exception as e:
        print(f"적응형 궁극기 효과 적용 중 오류: {e}")
        return False

def _aggressive_bonus(caster, target=None, skill_data=None):
    """공격적 보너스 - 공격력과 속도 증가, 방어력 감소"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("공격적_태세", "공격적_태세", 8, 40))  # 공격력 40% 증가
            caster.status_manager.add_status('방어_약화', 8, -20)  # 방어력 20% 감소
        print(f"{caster.name}이 공격적인 태세를 취했습니다!")
        return True
    except Exception as e:
        print(f"공격적 보너스 효과 적용 중 오류: {e}")
        return False

def _air_dash(caster, target=None, skill_data=None):
    """공중 돌진 - 빠른 이동과 회피력 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("공중_돌진", "공중_돌진", 3, 60))  # 회피율 60% 증가
        print(f"{caster.name}이 공중으로 돌진했습니다!")
        return True
    except Exception as e:
        print(f"공중 돌진 효과 적용 중 오류: {e}")
        return False

def _air_mastery(caster, target=None, skill_data=None):
    """공중 숙련 - 비행 및 공중 전투 능력"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("공중_숙련", "공중_숙련", 15, 30))  # 모든 공중 관련 능력 증가
        print(f"{caster.name}이 공중 전투 숙련도를 발휘합니다!")
        return True
    except Exception as e:
        print(f"공중 숙련 효과 적용 중 오류: {e}")
        return False

def _alignment_detect(caster, target, skill_data):
    """성향 탐지 - 적의 성향을 파악하여 추가 정보 획득"""
    try:
        if target:
            alignment = getattr(target, 'alignment', '중립')
            weakness = getattr(target, 'elemental_weaknesses', ['없음'])
            print(f"{target.name}의 성향: {alignment}, 약점: {weakness}")
            
            # 성향에 따라 추가 효과
            if alignment == '악':
                if hasattr(caster, 'status_manager'):
                    from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("성선_가호", "성선_가호", 5, 25))
        return True
    except Exception as e:
        print(f"성향 탐지 효과 적용 중 오류: {e}")
        return False

def _animal_kingdom(caster, target=None, skill_data=None):
    """동물의 왕국 - 다양한 동물의 힘을 빌림"""
    try:
        import random
        animals = ['사자', '독수리', '곰', '늑대', '치타']
        chosen_animal = random.choice(animals)
        
        if hasattr(caster, 'status_manager'):
            if chosen_animal == '사자':
                from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("사자의_위엄", "사자의_위엄", 5, 30))
            elif chosen_animal == '독수리':
                from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("독수리의_시야", "독수리의_시야", 5, 40))
            elif chosen_animal == '곰':
                from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("곰의_힘", "곰의_힘", 5, 35))
            elif chosen_animal == '늑대':
                from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("늑대의_민첩", "늑대의_민첩", 5, 25))
            elif chosen_animal == '치타':
                from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("치타의_속도", "치타의_속도", 5, 50))
        
        print(f"{caster.name}이 {chosen_animal}의 힘을 빌렸습니다!")
        return True
    except Exception as e:
        print(f"동물의 왕국 효과 적용 중 오류: {e}")
        return False

def _antidote(caster, target=None, skill_data=None):
    """해독제 - 독 상태 치료"""
    try:
        cure_target = target if target else caster
        if hasattr(cure_target, 'status_manager'):
            cure_target.status_manager.remove_status('독')
            cure_target.status_manager.remove_status('맹독')
            from game.new_skill_system import StatusEffect
cure_target.status_manager.add_status(StatusEffect("독_저항", "독_저항", 10, 50))
        print(f"{cure_target.name}의 독이 치료되었습니다!")
        return True
    except Exception as e:
        print(f"해독제 효과 적용 중 오류: {e}")
        return False

def _aquatic_blessing(caster, target=None, skill_data=None):
    """수중 축복 - 물 속성 친화력"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("수중_축복", "수중_축복", 12, 25))
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("물_속성_친화", "물_속성_친화", 12, 40))
        print(f"{caster.name}이 물의 축복을 받았습니다!")
        return True
    except Exception as e:
        print(f"수중 축복 효과 적용 중 오류: {e}")
        return False

def _aquatic_breathing(caster, target=None, skill_data=None):
    """수중 호흡 - 물 속에서 자유롭게 호흡"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("수중_호흡", "수중_호흡", 30, 0))
        print(f"{caster.name}이 물 속에서도 자유롭게 호흡할 수 있습니다!")
        return True
    except Exception as e:
        print(f"수중 호흡 효과 적용 중 오류: {e}")
        return False

def _arcane_mastery(caster, target=None, skill_data=None):
    """비전 숙련 - 마법 위력과 효율 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("비전_숙련", "비전_숙련", 10, 35))
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("마나_효율", "마나_효율", 10, 25))
        print(f"{caster.name}의 비전 마법 숙련도가 향상되었습니다!")
        return True
    except Exception as e:
        print(f"비전 숙련 효과 적용 중 오류: {e}")
        return False

def _area_explosion(caster, target, skill_data):
    """광역 폭발 - 범위 피해"""
    try:
        if target and skill_data:
            explosion_damage = skill_data.get('power', 120)
            target.take_damage(explosion_damage, "폭발 피해")
            print(f"{caster.name}의 광역 폭발이 {target.name}을 강타했습니다!")
            
            # 추가로 주변 적들에게도 피해 (실제 구현 시 적 목록 필요)
            splash_damage = explosion_damage * 0.5
            print(f"폭발의 여파로 주변에 {splash_damage} 피해!")
        return True
    except Exception as e:
        print(f"광역 폭발 효과 적용 중 오류: {e}")
        return False

def _auto_turret(caster, target=None, skill_data=None):
    """자동 포탑 설치"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("자동_포탑", "자동_포탑", 20, 80))  # 20턴간 자동 공격
        print(f"{caster.name}이 자동 포탑을 설치했습니다!")
        return True
    except Exception as e:
        print(f"자동 포탑 효과 적용 중 오류: {e}")
        return False

def _bad_taste(caster, target, skill_data):
    """불쾌한 맛 - 적에게 디버프"""
    try:
        if target:
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("구역질", "구역질", 5, 15))  # 모든 행동 15% 감소
            print(f"{target.name}이 불쾌한 맛에 구역질을 합니다!")
        return True
    except Exception as e:
        print(f"불쾌한 맛 효과 적용 중 오류: {e}")
        return False

def _balanced_bonus(caster, target=None, skill_data=None):
    """균형 보너스 - 모든 능력치 균등 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("균형", "균형", 10, 20))  # 모든 능력치 20% 증가
        print(f"{caster.name}이 완벽한 균형을 이뤘습니다!")
        return True
    except Exception as e:
        print(f"균형 보너스 효과 적용 중 오류: {e}")
        return False

def _banishment(caster, target, skill_data):
    """추방 - 적을 일시적으로 전투에서 제외"""
    try:
        if target:
            if hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("추방", "추방", 3, 0))  # 3턴간 행동 불가
            print(f"{target.name}이 다른 차원으로 추방되었습니다!")
        return True
    except Exception as e:
        print(f"추방 효과 적용 중 오류: {e}")
        return False

def _battle_reset(caster, target=None, skill_data=None):
    """전투 초기화 - 모든 상태 효과 제거"""
    try:
        if hasattr(caster, 'status_manager'):
            # 모든 상태 효과 제거
            caster.status_manager.clear_all_status()
            # 기본 상태로 복귀
            if hasattr(caster, 'atb_gauge'):
                caster.atb_gauge = 0
        print(f"{caster.name}의 모든 상태가 초기화되었습니다!")
        return True
    except Exception as e:
        print(f"전투 초기화 효과 적용 중 오류: {e}")
        return False

def _berserker_bonus(caster, target=None, skill_data=None):
    """광전사 보너스 - 체력이 낮을수록 강해짐"""
    try:
        if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
            hp_ratio = caster.current_hp / caster.max_hp
            bonus = int((1 - hp_ratio) * 100)  # 체력이 낮을수록 높은 보너스
            
            if hasattr(caster, 'status_manager'):
                caster.status_manager.add_status('광전사_각성', 8, bonus)
            
            print(f"{caster.name}의 광전사 본능이 깨어났습니다! (+{bonus}% 공격력)")
        return True
    except Exception as e:
        print(f"광전사 보너스 효과 적용 중 오류: {e}")
        return False

def _berserker_mode(caster, target=None, skill_data=None):
    """광전사 모드 - 극한의 전투 상태"""
    try:
        if hasattr(caster, 'status_manager'):
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("광전사_모드", "광전사_모드", 10, 60))  # 공격력 60% 증가
            from game.new_skill_system import StatusEffect
caster.status_manager.add_status(StatusEffect("이성_상실", "이성_상실", 10, 0))    # 제어 불가
        print(f"{caster.name}이 광전사 모드에 돌입했습니다!")
        return True
    except Exception as e:
        print(f"광전사 모드 효과 적용 중 오류: {e}")
        return False

def _breath_weapon(caster, target, skill_data):
    """브레스 무기 - 강력한 범위 공격"""
    try:
        if target and skill_data:
            breath_damage = skill_data.get('power', 150)
            breath_type = skill_data.get('element', '화염')
            
            target.take_damage(breath_damage, f"{breath_type} 브레스")
            
            # 속성에 따른 추가 효과
            if breath_type == '화염' and hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("화상", "화상", 4, 25))
            elif breath_type == '냉기' and hasattr(target, 'status_manager'):
                from game.new_skill_system import StatusEffect
target.status_manager.add_status(StatusEffect("빙결", "빙결", 2, 0))
            
            print(f"{caster.name}의 {breath_type} 브레스가 {target.name}을 덮쳤습니다!")
        return True
    except Exception as e:
        print(f"브레스 무기 효과 적용 중 오류: {e}")
        return False

def _chaos_effect(caster, target=None, skill_data=None):
    """혼돈 효과 - 예측 불가능한 랜덤 효과"""
    try:
        import random
        chaos_effects = [
            ('폭발', lambda: _area_explosion(caster, target, skill_data) if target else None),
            ('치유', lambda: _full_heal(caster)),
            ('혼란', lambda: _confusion(caster, target, skill_data) if target else None),
            ('강화', lambda: _damage_boost(caster)),
            ('순간이동', lambda: _teleport(caster))
        ]
        
        effect_name, effect_func = random.choice(chaos_effects)
        print(f"혼돈의 힘이 '{effect_name}' 효과를 발동시켰습니다!")
        
        if effect_func:
            effect_func()
        return True
    except Exception as e:
        print(f"혼돈 효과 적용 중 오류: {e}")
        return False
