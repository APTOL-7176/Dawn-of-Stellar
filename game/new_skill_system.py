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
        StatusType.TIME_MARKED: "⏳",
        StatusType.PHASE: "👻",}
    return icons.get(status_type, "❓")

class NewSkillSystem:
    
    def __init__(self):
        self.skills_by_class = self._initialize_all_skills()
        self.cooldowns = {}  # {character_id: {skill_name: remaining_turns}}
        # 스킬 계수 전역 배수 (1.5배로 모든 스킬 데미지 증가)
        self.skill_power_multiplier = 1.25
        # 적 스킬 전용 계수 (1.1배로 적 스킬 강화)
        self.enemy_skill_power_multiplier = 1.2
        # 아군 스킬 MP 소모량 배수 (1.6배로 증가)
        self.ally_mp_cost_multiplier = 1.75
    
    def _initialize_all_skills(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            # === 적응형 전투마스터 - 전사 ===
            "전사": [
                # 균형의 수호자 - [균형][적응] 키워드 특화
                {"name": "방패강타", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 3, "brv_power": 112, "accuracy": 95,
                 "description": "[BRV:112] [기절:30%/2턴] [물리] - 방패로 적을 강타하여 BRV를 획득하고 기절시킵니다.",
                 
                 "damage_type": DamageType.PHYSICAL, "sfx": "shield_bash",
                 "status_effects": [{
"type": StatusType.STUN, "duration": 2, "intensity": 0.3}],
                 "organic_effects": {"불굴의_의지": 0.3, "균형감각": 0.25, "전투_본능": 0.2}},
                {"name": "철벽방어", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 4, "sfx": "protect",
                 "description": "[방어+15%/4턴] [자신] - 자신의 방어력을 크게 강화합니다.",
                 
                 "status_effects": [{
"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"불굴의_의지": 0.4, "균형감각": 0.3}},
                {"name": "연속베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 5, "brv_power": 84, "accuracy": 90,
                 "description": "[BRV:84×2] [연속공격] [물리] - 2번 연속으로 베어 BRV를 획득합니다.",
                 
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["double_attack"],
                 "sfx": "sword_hit", "organic_effects": {
"전투_본능": 0.35, "균형감각": 0.25, "불굴의_의지": 0.15}},
                {"name": "전투함성", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 
                 "mp_cost": 6, "sfx": "haste",
                 "description": "[전체 공격+12%/5턴] [리더십] - 아군 전체의 공격력을 증가시키는 함성을 지릅니다.",
                 
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.12}],
                 "organic_effects": {"균형감각": 0.3, "전투_본능": 0.25, "리더십": 0.2}},
                {"name": "파괴의일격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 8, "hp_power": 125, "cast_time": 15, "accuracy": 85,
                 "description": "[HP:125] [관통] [물리] - [HP] 강력한 일격으로 적의 HP에 직접 피해를 가합니다. 방어력을 관통합니다.",
                 
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["armor_pierce"],
                 "sfx": "critical_hit", "organic_effects": {
"전투_본능": 0.4, "불굴의_의지": 0.3, "균형감각": 0.2}},
                {"name": "전사의격노", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 15, "hp_power": 168, "cast_time": 20, "cooldown": 6,
                 "description": "[궁극] [HP:168] [광분] [물리] [쿨:6턴] - [궁극] 전사의 분노를 폭발시켜 적에게 엄청난 피해를 가하는 궁극기입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["berserker_rage"],
                 "sfx": "critical_hit", "organic_effects": {
"불굴의_의지": 0.5, "전투_본능": 0.4, "균형감각": 0.3}}
            ],
            
            "검성": [
                # 검의 성인 - [검술][집중] 키워드 특화
                {"name": "검기응축", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 3, "sfx": "haste",
                 "description": "[공격+20%/5턴] [자신] [검술] - [BUFF] 검에 기를 모아 공격력을 크게 증가시킵니다. 검술 대가의 힘을 발휘합니다.",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"검술_대가": 0.4, "집중력": 0.35, "무술_수행": 0.25}},
                {"name": "일섬", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 4, "brv_power": 118, "accuracy": 98, "crit_rate": 20,
                 "description": "[BRV:118] [크리+20%] [물리] [발도] - [BRV] 순간적인 발도술로 적을 베어 BRV를 획득합니다. 높은 명중률과 크리티컬 확률을 가집니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["iai_cut"],
                 "sfx": "critical_hit", "organic_effects": {
"검술_대가": 0.45, "집중력": 0.3, "무술_수행": 0.25}},
                {"name": "검압베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 6, "brv_power": 140, "accuracy": 92,
                 "description": "[BRV:140] [검압] [물리] - [BRV] 검압을 방출하여 강력한 BRV 공격을 가합니다. 높은 위력을 자랑합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_pressure"],
                 "sfx": "sword_hit", "organic_effects": {
"검술_대가": 0.4, "집중력": 0.3, "무술_수행": 0.3}},
                {"name": "검심일체", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 5, "sfx": "haste",
                 "description": "[집중+30%/6턴] [검술강화] - [BUFF] 검과 마음을 하나로 만들어 집중력을 극대화시킵니다. 검술의 경지에 도달합니다.",
                 "status_effects": [{
"type": StatusType.FOCUS, "duration": 6, "intensity": 1.3}],
                 "special_effects": ["sword_unity"],
                 "organic_effects": {"검술_대가": 0.4, "집중력": 0.4, "무술_수행": 0.2}},
                {"name": "무쌍베기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 9, "hp_power": 147, "crit_rate": 15, "cast_time": 16,
                 "description": "[HP:147] [크리+15%] [물리] - [HP] 무쌍의 검술로 적에게 직접적인 HP 피해를 가합니다. 크리티컬 확률이 높습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["peerless_cut"],
                 "sfx": "critical_hit", "organic_effects": {
"검술_대가": 0.5, "집중력": 0.3, "무술_수행": 0.2}},
                {"name": "검제비의", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 17, "hp_power": 161, "cooldown": 7, "cast_time": 35,
                 "description": "[궁극] [HP:161] [전체] [침묵:3턴] [쿨:7턴] - [궁극] 검의 황제가 되어 모든 적을 베는 궁극 오의입니다. 적을 침묵시킬 수 있습니다.",
                 "sfx": "sword_hit",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_emperor"],
                 "status_effects": [{
"type": StatusType.SILENCE, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"검술_대가": 0.6, "집중력": 0.4, "무술_수행": 0.35, "전투_본능": 0.3}}
            ],
            
            "검투사": [
                # 투기장의 전사 - [검투][생존] 키워드 특화
                {"name": "투기장의기술", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,

                 "mp_cost": 2, "brv_power": 105,
                 "description": "[BRV:105] [격투] [물리] - [BRV] 투기장에서 단련한 격투 기술로 적을 공격하여 BRV를 획득합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.4, "생존_기술": 0.3, "무술_수행": 0.3}},
                {"name": "군중의함성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 3, "sfx": "magic_cast",
                 "description": "[공격+15%/4턴] [자신] [버프] - [BUFF] 관중들의 환호성에 힘입어 아군 전체의 사기를 올립니다.",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"전투_본능": 0.35, "생존_기술": 0.3, "지휘력": 0.25}},
                {"name": "네트던지기", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 4, "sfx": "magic_cast",
                 "description": "[기절:2턴] [속박] [디버프] - [DEBUFF] 그물을 던져 적의 움직임을 제한하고 속도를 감소시킵니다.",
                 "status_effects": [{
"type": StatusType.STUN, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"전투_본능": 0.4, "생존_기술": 0.3, "정밀함": 0.3}},
                {"name": "트라이던트찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 5, "hp_power": 133, "cast_time": 14, "crit_rate": 10,
                 "description": "[HP:133] [크리+10%] [물리] [삼지창] - [HP] 삼지창으로 적을 찔러 직접적인 HP 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.4, "무술_수행": 0.35, "정밀함": 0.25}},
                {"name": "결투자의명예", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 
                 "mp_cost": 6,
                 "description": "[특수] [명예회복] [검투사] - [SPECIAL] 결투자의 명예를 걸고 특별한 효과를 발동시킵니다.",
                 "special_effects": ["gladiator_honor"],
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.4, "생존_기술": 0.35, "의지력": 0.25}},
                {"name": "콜로세움의왕", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 16, "hp_power": 140, "cooldown": 7, "cast_time": 30,
                 "description": "[궁극] [HP:140] [전체] [왕의위엄] [쿨:7턴] - [궁극] 콜로세움의 왕이 되어 압도적인 힘을 발휘하는 궁극기입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["colosseum_king"],
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.5, "생존_기술": 0.4, "무술_수행": 0.35, "지휘력": 0.3}}
            ],
            
            "광전사": [
                # 광기의 전사 - [광폭][희생] 키워드 특화
                {"name": "광기의씨앗", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 
                 "mp_cost": 2,
                 "description": "[광기상태] [특수] [각성] - [SPECIAL] 내면의 광기를 일깨워 특별한 전투 상태로 진입합니다.",
                 "special_effects": ["rage_seed"],
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.4, "광기_제어": 0.35, "생존_기술": 0.25}},
                {"name": "무모한돌격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 3, "hp_power": 125, "cast_time": 15, "accuracy": 75,
                 "description": "[HP:130] [돌진] [물리] - [HP] 무모하게 돌진하여 적에게 강력한 HP 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.45, "광기_제어": 0.3, "무술_수행": 0.25}},
                {"name": "피의갈증", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 4, "hp_power": 118, "drain_hp": True, "drain_rate": 0.3, "cast_time": 15,
                 "description": "[흡혈강화] [특수] [피증폭] - [SPECIAL] 피에 대한 갈증으로 특수한 전투 효과를 얻습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["blood_thirst"],
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.4, "광기_제어": 0.3, "생존_기술": 0.3}},
                {"name": "광란의연타", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 6, "brv_power": 62, "consecutive_attacks": 4, "cast_time": 20,
                 "description": "[연속공격] [광란] [물리] - [SPECIAL] 광란 상태에서 연속으로 공격하는 특수 기술입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["mad_combo"],
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.4, "광기_제어": 0.35, "무술_수행": 0.25}},
                {"name": "분노폭발", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 8, "brv_power": 84, "hp_power": 70, "cast_time": 25,
                 "description": "[BRV+HP] [분노] [폭발] - [BRV][HP] 분노를 폭발시켜 BRV 획득과 HP 피해를 동시에 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["rage_explosion"],
                 "sfx": "limit_break", "organic_effects": {
"전투_본능": 0.4, "광기_제어": 0.35, "무술_수행": 0.25}},
                {"name": "버서커의최후", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 15, "hp_power": 154, "cooldown": 5, "cast_time": 10,
                 "description": "[궁극] [최후발악] [광분] - [궁극] 광전사의 최후 발악으로 모든 것을 걸고 공격하는 궁극기입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["berserker_end"],
                 "hp_sacrifice_rate": 0.25,
                 "sfx": "magic_cast", "organic_effects": {
"전투_본능": 0.5, "광기_제어": 0.4, "생존_기술": 0.35, "의지력": 0.3}}
            ],
            
            # === 기사 계열 ===
            "기사": [
                # 명예로운 기사 - [기사도][방어] 키워드 특화
                {"name": "방패방어", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 2,
                 "description": "[방어+25%/4턴] [자신] - [BUFF] 방패로 방어 자세를 취하여 방어력을 크게 증가시킵니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.2}],
                 "organic_effects": {"방어_술수": 0.4, "기사도_정신": 0.35, "전술_지식": 0.25}},
                {"name": "창돌격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 3, "brv_power": 112, "accuracy": 90,
                 "description": "[BRV:105] [돌격] [물리] - [BRV] 창을 들고 돌격하여 적을 공격하고 BRV를 획득합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "sfx": "magic_cast", "organic_effects": {
"무술_수행": 0.4, "기사도_정신": 0.3, "전투_본능": 0.3}},
                {"name": "아군보호", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 
                 "mp_cost": 4,
                 "description": "[전체 방어+15%] [보호] - [BUFF] 아군을 보호하는 기사의 의무로 아군 전체의 방어력을 향상시킵니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BARRIER, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"기사도_정신": 0.4, "지휘력": 0.3, "방어_술수": 0.3}},
                {"name": "기사도정신", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 
                 "mp_cost": 6, "cooldown": 3,
                 "description": "[전능력+10%] [기사도] - [BUFF] 기사도 정신으로 자신의 모든 능력치를 향상시킵니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"기사도_정신": 0.45, "지휘력": 0.35, "방어_술수": 0.2}},
                {"name": "성스러운돌격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 8, "hp_power": 133, "element": ElementType.LIGHT, "cast_time": 12,
                 "description": "[HP:120] [성속] [돌격] - [HP] 성스러운 힘을 담은 돌격으로 적의 HP에 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "sfx": "magic_cast", "organic_effects": {
"기사도_정신": 0.4, "신성_마법": 0.3, "무술_수행": 0.3}},
                {"name": "수호기사의맹세", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 
                 "mp_cost": 16, "cooldown": 6, "cast_time": 30,
                 "description": "[궁극] [완벽보호] [맹세] - [궁극] 수호기사의 맹세로 아군을 완벽하게 보호하는 궁극기입니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BARRIER, "duration": 6, "intensity": 2.0}],
                 "special_effects": ["knight_oath"],
                 "organic_effects": {"기사도_정신": 0.5, "지휘력": 0.4, "방어_술수": 0.35, "신성_마법": 0.3}}
            ],
            
            "성기사": [
                # 신성한 수호자 - [신성][수호] 키워드 특화
                {"name": "신앙의힘", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 3,
                 "description": "[성속강화] [신앙] [버프] - [BUFF] 신에 대한 믿음으로 성스러운 힘을 얻어 능력치를 향상시킵니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"신앙": 0.4, "성스러운_힘": 0.3, "수호_의지": 0.25}},
                {"name": "성스러운타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 4, "brv_power": 105, "element": ElementType.LIGHT, "accuracy": 95,
                 "description": "[BRV:95] [성속] [정화] - [BRV] 성스러운 힘을 담은 공격으로 적을 타격하여 BRV를 획득합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["holy_strike"],
                 "sfx": "staff_hit", "organic_effects": {
"성스러운_힘": 0.4, "신앙": 0.3, "전투_본능": 0.25}},
                {"name": "축복", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 
                 "mp_cost": 5, "sfx": "protect",
                 "description": "[전체 축복] [보호막] [성속] - [BUFF] 신의 축복으로 아군의 능력치를 향상시키고 보호막을 씌웁니다.",
                 "status_effects": [{
"type": StatusType.BLESSING, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.BOOST_DEF, "duration": 5, "intensity": 1.15}],
                 "organic_effects": {"신앙": 0.4, "수호_의지": 0.35, "성스러운_힘": 0.25}},
                {"name": "치유의빛", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 
                 "mp_cost": 6, "heal_power": 3.1, "element": ElementType.LIGHT,
                 "description": "[치유:중] [성속] [빛] - [HEAL] 성스러운 빛으로 아군의 상처를 치유하고 HP를 회복시킵니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["holy_heal"],
                 "sfx": "heal2", "organic_effects": {
"성스러운_힘": 0.4, "신앙": 0.35, "수호_의지": 0.3}},
                {"name": "부활", "type": SkillType.SPECIAL, "target": TargetType.DEAD_ALLY,
                 
                 "mp_cost": 12, "cast_time": 30, "cooldown": 5, "element": ElementType.LIGHT,
                 "description": "[되살림] [기적] [성속] - [SPECIAL] 신의 기적으로 쓰러진 아군을 되살려냅니다.",
                 "special_effects": ["resurrect"],
                 "sfx": "phoenix_down", "organic_effects": {
"신앙": 0.5, "성스러운_힘": 0.4, "수호_의지": 0.35}},
                {"name": "천사의강림", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 16, "hp_power": 125, "element": ElementType.LIGHT, "cooldown": 8, "cast_time": 35,
                 "description": "[궁극] [천사소환] [신성] - [궁극] 천사를 강림시켜 압도적인 성스러운 힘을 발휘하는 궁극기입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["angel_descent"],
                 "sfx": "limit_break", "organic_effects": {
"성스러운_힘": 0.5, "신앙": 0.4, "수호_의지": 0.35, "전투_본능": 0.3}}
            ],
            
            "암흑기사": [
                # 어둠의 계약자 - [어둠][흡수] 키워드 특화
                {"name": "어둠의계약", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 
                 "mp_cost": 3,
                 "description": "[어둠강화] [계약] [특수] - [SPECIAL] 어둠의 힘과 계약하여 특별한 능력을 얻습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["dark_pact"],
                 "sfx": "magic_cast", "organic_effects": {
"어둠_지배": 0.4, "생명력_조작": 0.3, "전투_본능": 0.25}},
                {"name": "생명흡수", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 4, "brv_power": 98, "element": ElementType.DARK, "accuracy": 95,
                 "description": "[BRV:90] [흡혈] [어둠] - [BRV] 적의 생명력을 흡수하여 자신의 BRV로 전환합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["life_steal"],
                 "sfx": "magic_cast", "organic_effects": {
"생명력_조작": 0.4, "어둠_지배": 0.3, "전투_본능": 0.25}},
                {"name": "저주의검", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 5, "element": ElementType.DARK, "sfx": "sword_hit",
                 "description": "[저주부여] [어둠] [디버프] - [DEBUFF] 저주받은 검으로 적을 공격하여 저주 상태를 부여합니다.",
                 "status_effects": [{
"type": StatusType.CURSE, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_DEF, "duration": 4, "intensity": 0.85}],
                 "organic_effects": {"어둠_지배": 0.4, "생명력_조작": 0.3, "마법_지식": 0.25}},
                {"name": "어둠의보호", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 6, "sfx": "magic_cast",
                 "description": "[암속방어+] [어둠] [보호] - [BUFF] 어둠의 힘으로 자신을 보호하여 방어력을 증가시킵니다.",
                 "status_effects": [{
"type": StatusType.BOOST_DEF, "duration": 4, "intensity": 1.25}],
                 "organic_effects": {"어둠_지배": 0.35, "생명력_조작": 0.3, "전투_본능": 0.25}},
                {"name": "흡혈", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 8, "hp_power": 118, "element": ElementType.DARK, "cast_time": 10,
                 "description": "[HP:100] [흡혈] [어둠] - [HP] 적을 공격하여 HP 피해를 가하고 자신의 체력을 회복합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["vampire_strike"],
                 "sfx": "magic_cast", "organic_effects": {
"생명력_조작": 0.4, "어둠_지배": 0.35, "전투_본능": 0.3}},
                {"name": "어둠의지배자", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 16, "hp_power": 140, "element": ElementType.DARK, "cooldown": 7, "cast_time": 30,
                 "description": "[궁극] [어둠지배] [암속] - [궁극] 어둠의 지배자가 되어 모든 적을 압도하는 궁극기입니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.HYBRID, "special_effects": ["dark_domination"],
                 "status_effects": [{
"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.CURSE, "duration": 6, "intensity": 1.5}],
                 "organic_effects": {"어둠_지배": 0.5, "생명력_조작": 0.4, "전투_본능": 0.35, "마법_지식": 0.3}}
            ],
            
            "용기사": [
                # 드래곤의 후예 - [용족][화염] 키워드 특화
                {"name": "용의비늘", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 3,
                 "description": "[방어+30%] [용족] [비늘] - [BUFF] 용의 비늘처럼 단단한 보호막으로 자신을 감쌉니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BOOST_DEF, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"용족_혈통": 0.4, "화염_친화": 0.3, "전투_본능": 0.25}},
                {"name": "드래곤클로", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 4, "brv_power": 112, "element": ElementType.FIRE, "accuracy": 95,
                 "description": "[BRV:115] [용족] [발톱] - [BRV] 용의 발톱으로 적을 할퀴어 BRV를 획득합니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.PHYSICAL,
                 "status_effects": [{
"type": StatusType.BLEED, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.3, "화염_친화": 0.25}},
                {"name": "화염숨결", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 6, "brv_power": 84, "element": ElementType.FIRE, "accuracy": 90,
                 "description": "[BRV:108] [화속] [브레스] - [BRV] 용의 화염 숨결로 적을 공격하여 BRV를 획득합니다.",
                 "sfx": "fire",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{
"type": StatusType.BURN, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"화염_친화": 0.4, "용족_혈통": 0.35, "마법_지식": 0.25}},
                {"name": "용의위엄", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 5, "sfx": "magic_cast",
                 "description": "[위압] [능력감소] [용족] - [DEBUFF] 용의 위엄으로 적을 위압하여 공격력과 방어력을 감소시킵니다.",
                 "status_effects": [{
"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_DEF, "duration": 4, "intensity": 0.85}],
                 "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.3, "마법_지식": 0.25}},
                {"name": "드래곤스피어", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 9, "hp_power": 140, "element": ElementType.FIRE, "cast_time": 18,
                 "description": "[HP:140] [화속] [창술] - [HP] 용의 힘을 담은 창 공격으로 적의 HP에 강력한 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["dragon_spear"],
                 "sfx": "magic_cast", "organic_effects": {
"용족_혈통": 0.4, "전투_본능": 0.35, "화염_친화": 0.3}},
                {"name": "드래곤로드", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 18, "hp_power": 154, "element": ElementType.FIRE, "cooldown": 8, "cast_time": 40,
                 "description": "[궁극] [용화] [지배] - [궁극] 용의 군주가 되어 압도적인 용의 힘을 발휘하는 궁극기입니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.HYBRID, "special_effects": ["dragon_lord"],
                 "status_effects": [{
"type": StatusType.BURN, "duration": 5, "intensity": 1.5},
                                   {"type": StatusType.TERROR, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"용족_혈통": 0.6, "화염_친화": 0.5, "전투_본능": 0.4, "마법_지식": 0.35}}
            ],
            
            # === 진화하는 현자 - 아크메이지 ===
            "아크메이지": [
                # 원소의 연구자 - [진화][연구] 키워드 특화
                {"name": "마력파동", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 4, "brv_power": 118, "accuracy": 100,
                 "description": "[BRV:95] [마법] [파동] - [BRV] 마력의 파동을 방출하여 적을 공격하고 BRV를 획득합니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.NEUTRAL,
                 "special_effects": ["mana_recovery_10pct"],
                 "sfx": "magic_cast", "organic_effects": {
"마나_순환": 0.35, "연구_정신": 0.3, "마법_친화": 0.25}},
                {"name": "원소융합", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 6, "brv_power": 125, "accuracy": 95,
                 "description": "[BRV:105] [원소] [융합] - [BRV] 여러 원소를 융합하여 강력한 마법 공격으로 BRV를 획득합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["random_element"],
                 "sfx": "magic_cast", "organic_effects": {
"연구_정신": 0.4, "마법_친화": 0.3, "집중력": 0.2}},
                {"name": "마나실드", "type": SkillType.BUFF, "target": TargetType.SELF,
                 
                 "mp_cost": 5,
                 "description": "[마법방어+] [실드] [마나] - [BUFF] 마나로 방어막을 형성하여 마법 피해를 흡수합니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.MANA_SHIELD, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"마나_순환": 0.4, "집중력": 0.3, "마법_친화": 0.25}},
                {"name": "마법폭발", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 10, "hp_power": 105, "cast_time": 20, "accuracy": 90,
                 "description": "[HP:135] [마법] [폭발] - [HP] 마법을 폭발시켜 적의 HP에 직접 피해를 가합니다.",
                 "sfx": "magic_cast",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.FIRE,
                 "status_effects": [{
"type": StatusType.BURN, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"마법_친화": 0.35, "연구_정신": 0.3, "집중력": 0.25}},
                {"name": "시공술", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "sfx": "magic_cast",
                 "description": "[시공왜곡] [디버프] [마법] - [DEBUFF] 시공간을 조작하여 적의 행동을 제한하고 혼란시킵니다.",
                 "status_effects": [{
"type": StatusType.SLOW, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"연구_정신": 0.4, "집중력": 0.35, "마나_순환": 0.2}},
                {"name": "아르카나", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "hp_power": 147, "cast_time": 30, "cooldown": 7,
                 "description": "[궁극] [비밀마법] [초월] - [궁극] 최고 수준의 비밀 마법으로 엄청난 위력을 발휘하는 궁극기입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["all_elements"],
                 "sfx": "ultima", "organic_effects": {
"마법_친화": 0.5, "연구_정신": 0.4, "마나_순환": 0.35, "집중력": 0.3}}
            ],

            "정령술사": [
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
                # 회피의 달인 - [차원][회피] 키워드 특화
                {"name": "차원장막", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "vanish",
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
                # 바람의 유격수 - [연사][기동] 키워드 특화
                {"name": "연사", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 98, "accuracy": 95, "hit_count": 3,
                 "description": "[BRV:85] [연속] [물리] - [BRV] 연속으로 화살을 발사하여 BRV를 획득합니다.",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.WIND,
                 "special_effects": ["triple_shot"],
                 "sfx": "magic_cast", "organic_effects": {
"유격_전술": 0.35, "바람_친화": 0.3, "정밀_사격": 0.25}},
                {"name": "관통사격", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 
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
                {"name": "바람보조", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 6, "sfx": "magic_cast",
                 "description": "[명중+] [크리+] [바람] - [BUFF] 바람의 도움을 받아 명중률과 크리티컬 확률을 증가시킵니다.",
                 "status_effects": [{
"type": StatusType.BOOST_DODGE, "duration": 5, "intensity": 1.3},
                                   {"type": StatusType.BOOST_SPD, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"바람_친화": 0.4, "유격_전술": 0.35, "생존_본능": 0.2}},
                {"name": "헌터모드", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 16, "cooldown": 6,
                 "description": "[궁극] [사냥] [완벽조준] - [궁극] 완벽한 사냥꾼 모드로 진입하여 모든 사격 능력을 극대화하는 궁극기입니다.",
                 "special_effects": ["hunter_mode"],
                 "sfx": "magic_cast", "organic_effects": {
"정밀_사격": 0.5, "유격_전술": 0.4, "바람_친화": 0.35, "생존_본능": 0.3}}
            ],

            
            "암살자": [
                # 그림자의 암살자 - [은신][암살] 키워드 특화
                {"name": "그림자숨기", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "sfx": "magic_cast",
                 "description": "[은신] [회피+] [그림자] - [BUFF] 그림자에 숨어 은신 상태가 되어 적의 공격을 회피합니다.",
                 "status_effects": [{
"type": StatusType.STEALTH, "duration": 2, "intensity": 1.0},
                                   {"type": StatusType.BOOST_CRIT, "duration": 2, "intensity": 2.0}],
                 "organic_effects": {"은신_술법": 0.4, "정밀함": 0.3, "생존_본능": 0.3}},
                {"name": "기습", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 118, "crit_rate": 25, "accuracy": 95,
                 "description": "[BRV:95] [기습] [그림자] - [BRV] 그림자에서 나타나 기습 공격으로 BRV를 획득합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["stealth_attack"],
                 "sfx": "magic_cast", "organic_effects": {
"은신_술법": 0.4, "암살_기술": 0.35, "정밀함": 0.25}},
                {"name": "독바르기", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "magic_cast",
                 "description": "[독부여] [특수] [독] - [SPECIAL] 무기에 독을 발라 다음 공격에 독 효과를 추가합니다.",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1}],
                 "special_effects": ["poison_weapon"],
                 "organic_effects": {"독술_지식": 0.4, "암살_기술": 0.3, "정밀함": 0.3}},
                {"name": "연막탄", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 6, "cooldown": 3,
                 "description": "[시야차단] [혼란] [연막] - [FIELD] 연막탄을 터뜨려 전장을 연기로 가려 시야를 차단합니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BLIND, "duration": 3, "intensity": 1.0}],
                 "is_field_skill": True, "special_effects": ["smoke_bomb"],
                 "organic_effects": {"은신_술법": 0.4, "전술_지식": 0.3, "생존_본능": 0.3}},
                {"name": "암살술", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 168, "cast_time": 12, "crit_rate": 30,
                 "description": "[HP:140] [암살] [치명] - [HP] 은밀한 암살 기술로 적의 HP에 치명적인 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["assassination"],
                 "sfx": "critical_hit", "organic_effects": {
"암살_기술": 0.5, "정밀함": 0.3, "은신_술법": 0.2}},
                {"name": "그림자분신", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 15, "hp_power": 133, "cooldown": 7, "cast_time": 8,
                 "description": "[궁극] [분신] [다중공격] - [궁극] 그림자 분신술로 여러 개의 분신을 만들어 동시 공격하는 궁극기입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["shadow_clone"],
                 "sfx": "magic_cast", "organic_effects": {
"은신_술법": 0.5, "암살_기술": 0.4, "정밀함": 0.35, "생존_본능": 0.3}}
            ],
            
            # === 독술의 암살자 - 도적 ===
            "도적": [
                # 독술의 암살자 - [독성][정밀] 키워드 특화  
                {"name": "독침", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 3, "brv_power": 105, "accuracy": 95,
                 "description": "[BRV:80] [독] [암기] - [BRV] 독침을 던져 적을 공격하고 독 상태를 부여합니다.",
                 "sfx": "poison",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "status_effects": [{
"type": StatusType.POISON, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.PARALYZE, "duration": 2, "intensity": 0.3}],
                 "organic_effects": {"독_숙련": 0.4, "정밀_조준": 0.3, "은신_술": 0.25}},
                {"name": "암살", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 10, "hp_power": 154, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:150] [암살] [치명] - [HP] 급소를 노린 암살 공격으로 적의 HP에 직접 피해를 가합니다.",
                 "sfx": "critical_hit",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["stealth_attack"],
                 "status_effects": [{
"type": StatusType.STUN, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"은신_술": 0.4, "정밀_조준": 0.35, "독_숙련": 0.2}},
                {"name": "연막탄", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 6,
                 "description": "[시야차단] [혼란] [연막] - [FIELD] 연막탄을 터뜨려 전장을 연기로 가려 시야를 차단합니다.",
                 "sfx": "magic_cast",
                 "status_effects": [{
"type": StatusType.BLIND, "duration": 3, "intensity": 0.7}],
                 "special_effects": ["smoke_screen"],
                 "organic_effects": {"은신_술": 0.35, "빠른손놀림": 0.3, "독_숙련": 0.25}},
                {"name": "독무", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 12, "cast_time": 20, "cooldown": 4,
                 "description": "[전체독] [필드] [독안개] - [FIELD] 독성 안개를 퍼뜨려 전장에 있는 모든 적을 중독시킵니다.",
                 "sfx": "magic_cast",
                 "is_field_skill": True, "special_effects": ["poison_fog"],
                 "status_effects": [{
"type": StatusType.POISON, "duration": 5, "intensity": 1.5}],
                 "organic_effects": {"독_숙련": 0.5, "은신_술": 0.3, "빠른손놀림": 0.25}},
                {"name": "독날투척", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 
                 "mp_cost": 5, "brv_power": 112, "accuracy": 90,
                 "description": "[BRV:88] [독] [투척] - [BRV] 독이 발린 수리검을 던져 적을 공격하고 중독시킵니다.",
                 "damage_type": DamageType.RANGED, "element": ElementType.POISON,
                 "special_effects": ["poison_blade"],
                 "sfx": "magic_cast", "organic_effects": {
"독_숙련": 0.35, "정밀_조준": 0.3, "빠른손놀림": 0.25}},
                {"name": "독왕의비의", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 18, "hp_power": 196, "cast_time": 25, "cooldown": 7,
                 "description": "[궁극] [독지배] [죽음] - [궁극] 독의 왕이 되어 치명적인 독으로 모든 적을 죽음으로 이끄는 궁극기입니다.",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "special_effects": ["poison_mastery"],
                 "sfx": "magic_cast", "organic_effects": {
"독_숙련": 0.6, "은신_술": 0.4, "정밀_조준": 0.35, "빠른손놀림": 0.3}}
            ],
            
            "해적": [
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
        
        # 검성 효과
        "iai_cut": lambda: _iai_cut(caster, target, skill_data),
        "sword_pressure": lambda: _sword_pressure(caster, target, skill_data),
        "sword_unity": lambda: _sword_unity(caster),
        "peerless_cut": lambda: _peerless_cut(caster, target, skill_data),
        "sword_emperor": lambda: _sword_emperor(caster, target, skill_data),
        
        # 검투사 효과
        "gladiator_honor": lambda: _gladiator_honor(caster),
        "colosseum_king": lambda: _colosseum_king(caster, target, skill_data),
        
        # 광전사 효과
        "rage_seed": lambda: _rage_seed(caster),
        "blood_thirst": lambda: _blood_thirst(caster, target, skill_data),
        "mad_combo": lambda: _mad_combo(caster, target, skill_data),
        "rage_explosion": lambda: _rage_explosion(caster, target, skill_data),
        "berserker_end": lambda: _berserker_end(caster, target, skill_data),
        
        # 기사/성기사 효과
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
        
        # 도적 효과
        "poison_weapon": lambda: _poison_weapon(caster, target, skill_data),
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
        "analyze_enemy": lambda: _analyze_enemy(caster, target)}
    
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
    """시간 기록점"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.TIME_SAVEPOINT, duration=999, intensity=1.0)
    return True

def _time_rewind_to_savepoint(caster):
    """시간 되돌리기"""
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
    """시간 정지"""
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
    """차원 은폐"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.STEALTH, duration=3, intensity=1.0)
        caster.add_status(StatusType.BOOST_DODGE, duration=5, intensity=3.0)
    return True

def _afterimage(caster):
    """잔상"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.AFTERIMAGE, duration=4, intensity=1.0)
        caster.add_status(StatusType.BOOST_SPD, duration=4, intensity=2.0)
    return True

def _space_leap(caster, target, skill_data):
    """공간 도약"""
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
    """진리 통찰"""
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
    """철학적 사고"""
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
    """아이템 변환"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.TRANSMUTATION, duration=1, intensity=1.0)
    return True

def _instant_potion(caster, target):
    """즉석 포션"""
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
        caster.add_status(StatusType.BOOST_DODGE, duration=4, intensity=2.5)
    return True



# 전역 인스턴스
skill_system = NewSkillSystem()
new_skill_system = NewSkillSystem()
