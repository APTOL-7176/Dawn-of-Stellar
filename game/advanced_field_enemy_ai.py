#!/usr/bin/env python3
"""
Dawn of Stellar - 고급 필드 적 AI 시스템
다양한 적 종류, 스킬, 패시브, 접두사 시스템 포함
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

class EnemyType(Enum):
    """적 기본 타입"""
    BEAST = "야수"           # 물리 공격형
    UNDEAD = "언데드"        # 마법 저항형
    DEMON = "악마"           # 균형형
    CONSTRUCT = "구조체"     # 방어형
    ELEMENTAL = "정령"       # 원소형
    HUMANOID = "인간형"      # 기술형
    DRAGON = "드래곤"        # 보스형
    ABERRATION = "기형체"    # 특수형

class EnemyBehavior(Enum):
    """적 행동 패턴"""
    AGGRESSIVE = "공격적"    # 무조건 돌진
    CAUTIOUS = "신중한"      # 체력 낮으면 후퇴
    TACTICAL = "전술적"      # 협력 공격
    TERRITORIAL = "영역형"   # 영역 방어
    AMBUSH = "매복형"        # 기습 공격
    SUPPORT = "지원형"       # 아군 보조
    BERSERKER = "광전사"     # 체력 낮을수록 강해짐
    PACK_HUNTER = "무리사냥" # 집단 행동

class EnemyPrefix(Enum):
    """적 접두사 (능력 강화)"""
    ELITE = "정예"           # 모든 능력치 +50%
    ANCIENT = "고대"         # HP +100%, 특수 스킬
    CORRUPTED = "타락한"     # 독 면역, 독 공격
    BLESSED = "축복받은"     # 회복 능력, 신성 공격
    SAVAGE = "야만적인"      # 공격력 +100%, 방어력 -50%
    ARMORED = "중장갑"       # 방어력 +200%, 속도 -50%
    SWIFT = "민첩한"         # 속도 +100%, 회피율 증가
    MAGICAL = "마법적인"     # 마법 공격, 마나 보유
    POISONOUS = "독성"       # 독 공격, 독 면역
    REGENERATING = "재생"    # 턴마다 HP 회복
    EXPLOSIVE = "폭발성"     # 죽을 때 폭발
    INVISIBLE = "투명한"     # 은신 능력
    BERSERKING = "광폭한"    # 체력 낮을수록 강해짐
    ICY = "얼음"             # 빙결 공격
    FIERY = "화염"           # 화상 공격
    ELECTRIC = "전기"        # 마비 공격

@dataclass
class EnemySkill:
    """적 스킬 정의"""
    name: str
    description: str
    mp_cost: int
    cooldown: int
    damage_multiplier: float
    special_effects: List[str] = field(default_factory=list)
    target_type: str = "single"  # single, all, self
    skill_type: str = "attack"   # attack, debuff, buff, heal

@dataclass
class EnemyPassive:
    """적 패시브 능력"""
    name: str
    description: str
    effect_type: str  # stat, resistance, special
    effect_value: float
    condition: str = "always"  # always, low_hp, combat_start, etc.

@dataclass
class EnemyTemplate:
    """적 템플릿"""
    name: str
    enemy_type: EnemyType
    behavior: EnemyBehavior
    base_hp: int
    base_attack: int
    base_defense: int
    base_speed: int
    base_mp: int = 0
    level_scaling: float = 1.2
    skills: List[EnemySkill] = field(default_factory=list)
    passives: List[EnemyPassive] = field(default_factory=list)
    ai_aggression: float = 1.0  # 0.0 ~ 2.0
    ai_intelligence: float = 1.0  # 0.0 ~ 2.0
    special_abilities: List[str] = field(default_factory=list)

class AdvancedFieldEnemyAI:
    """고급 필드 적 AI 시스템"""
    
    def __init__(self):
        self.enemy_templates = self._initialize_enemy_templates()
        self.enemy_skills = self._initialize_enemy_skills()
        self.enemy_passives = self._initialize_enemy_passives()
        self.floor_prefixes = self._initialize_floor_prefixes()
        
    def _initialize_enemy_templates(self) -> Dict[str, EnemyTemplate]:
        """적 템플릿 초기화"""
        templates = {}
        
        # 🐺 야수형 적들
        templates["늑대"] = EnemyTemplate(
            name="늑대",
            enemy_type=EnemyType.BEAST,
            behavior=EnemyBehavior.PACK_HUNTER,
            base_hp=45, base_attack=18, base_defense=8, base_speed=15,
            ai_aggression=1.3, ai_intelligence=0.8,
            special_abilities=["pack_coordination", "howl"]
        )
        
        templates["곰"] = EnemyTemplate(
            name="곰",
            enemy_type=EnemyType.BEAST,
            behavior=EnemyBehavior.TERRITORIAL,
            base_hp=80, base_attack=25, base_defense=15, base_speed=8,
            ai_aggression=0.8, ai_intelligence=0.6,
            special_abilities=["charge", "intimidate"]
        )
        
        templates["거미"] = EnemyTemplate(
            name="거미",
            enemy_type=EnemyType.BEAST,
            behavior=EnemyBehavior.AMBUSH,
            base_hp=30, base_attack=15, base_defense=5, base_speed=20,
            ai_aggression=1.1, ai_intelligence=1.2,
            special_abilities=["web_trap", "poison_bite"]
        )
        
        # 💀 언데드형 적들
        templates["스켈레톤"] = EnemyTemplate(
            name="스켈레톤",
            enemy_type=EnemyType.UNDEAD,
            behavior=EnemyBehavior.AGGRESSIVE,
            base_hp=35, base_attack=20, base_defense=12, base_speed=10,
            ai_aggression=1.5, ai_intelligence=0.4,
            special_abilities=["bone_throw", "undead_resilience"]
        )
        
        templates["좀비"] = EnemyTemplate(
            name="좀비",
            enemy_type=EnemyType.UNDEAD,
            behavior=EnemyBehavior.BERSERKER,
            base_hp=60, base_attack=16, base_defense=6, base_speed=6,
            ai_aggression=2.0, ai_intelligence=0.2,
            special_abilities=["infectious_bite", "undying_rage"]
        )
        
        templates["유령"] = EnemyTemplate(
            name="유령",
            enemy_type=EnemyType.UNDEAD,
            behavior=EnemyBehavior.CAUTIOUS,
            base_hp=40, base_attack=22, base_defense=20, base_speed=18,
            base_mp=30, ai_aggression=0.7, ai_intelligence=1.4,
            special_abilities=["phase_shift", "life_drain"]
        )
        
        # 👹 악마형 적들
        templates["임프"] = EnemyTemplate(
            name="임프",
            enemy_type=EnemyType.DEMON,
            behavior=EnemyBehavior.TACTICAL,
            base_hp=25, base_attack=14, base_defense=8, base_speed=16,
            base_mp=20, ai_aggression=1.0, ai_intelligence=1.3,
            special_abilities=["fire_dart", "teleport"]
        )
        
        templates["오크"] = EnemyTemplate(
            name="오크",
            enemy_type=EnemyType.DEMON,
            behavior=EnemyBehavior.AGGRESSIVE,
            base_hp=55, base_attack=22, base_defense=12, base_speed=11,
            ai_aggression=1.4, ai_intelligence=0.7,
            special_abilities=["weapon_throw", "battle_roar"]
        )
        
        # 🤖 구조체형 적들
        templates["골렘"] = EnemyTemplate(
            name="골렘",
            enemy_type=EnemyType.CONSTRUCT,
            behavior=EnemyBehavior.TERRITORIAL,
            base_hp=100, base_attack=20, base_defense=25, base_speed=5,
            ai_aggression=0.5, ai_intelligence=0.8,
            special_abilities=["stone_skin", "earthquake"]
        )
        
        templates["기계병"] = EnemyTemplate(
            name="기계병",
            enemy_type=EnemyType.CONSTRUCT,
            behavior=EnemyBehavior.TACTICAL,
            base_hp=65, base_attack=18, base_defense=18, base_speed=12,
            base_mp=15, ai_aggression=1.0, ai_intelligence=1.5,
            special_abilities=["laser_shot", "self_repair"]
        )
        
        # 🔥 정령형 적들
        templates["화염정령"] = EnemyTemplate(
            name="화염정령",
            enemy_type=EnemyType.ELEMENTAL,
            behavior=EnemyBehavior.AGGRESSIVE,
            base_hp=45, base_attack=24, base_defense=10, base_speed=14,
            base_mp=40, ai_aggression=1.2, ai_intelligence=1.1,
            special_abilities=["fireball", "burn_aura"]
        )
        
        templates["얼음정령"] = EnemyTemplate(
            name="얼음정령",
            enemy_type=EnemyType.ELEMENTAL,
            behavior=EnemyBehavior.CAUTIOUS,
            base_hp=50, base_attack=20, base_defense=15, base_speed=10,
            base_mp=35, ai_aggression=0.8, ai_intelligence=1.3,
            special_abilities=["ice_shard", "freeze_aura"]
        )
        
        # 👥 인간형 적들
        templates["도적"] = EnemyTemplate(
            name="도적",
            enemy_type=EnemyType.HUMANOID,
            behavior=EnemyBehavior.AMBUSH,
            base_hp=40, base_attack=20, base_defense=8, base_speed=18,
            ai_aggression=1.1, ai_intelligence=1.4,
            special_abilities=["sneak_attack", "poison_blade"]
        )
        
        templates["마법사"] = EnemyTemplate(
            name="마법사",
            enemy_type=EnemyType.HUMANOID,
            behavior=EnemyBehavior.SUPPORT,
            base_hp=35, base_attack=16, base_defense=6, base_speed=12,
            base_mp=50, ai_aggression=0.6, ai_intelligence=1.8,
            special_abilities=["magic_missile", "heal_allies"]
        )
        
        templates["전사"] = EnemyTemplate(
            name="전사",
            enemy_type=EnemyType.HUMANOID,
            behavior=EnemyBehavior.TACTICAL,
            base_hp=70, base_attack=24, base_defense=16, base_speed=10,
            ai_aggression=1.2, ai_intelligence=1.2,
            special_abilities=["shield_bash", "war_cry"]
        )
        
        # 🐲 드래곤형 적들 (보스급)
        templates["와이번"] = EnemyTemplate(
            name="와이번",
            enemy_type=EnemyType.DRAGON,
            behavior=EnemyBehavior.TERRITORIAL,
            base_hp=150, base_attack=30, base_defense=20, base_speed=16,
            base_mp=60, ai_aggression=1.0, ai_intelligence=1.6,
            special_abilities=["breath_attack", "aerial_strike"]
        )
        
        # 👁️ 기형체형 적들
        templates["촉수괴물"] = EnemyTemplate(
            name="촉수괴물",
            enemy_type=EnemyType.ABERRATION,
            behavior=EnemyBehavior.BERSERKER,
            base_hp=85, base_attack=26, base_defense=12, base_speed=8,
            ai_aggression=1.6, ai_intelligence=0.9,
            special_abilities=["tentacle_slam", "mind_blast"]
        )
        
        return templates
    
    def _initialize_enemy_skills(self) -> Dict[str, EnemySkill]:
        """적 스킬 초기화"""
        skills = {}
        
        # 야수 스킬
        skills["pack_howl"] = EnemySkill(
            name="무리 울음",
            description="주변 늑대들의 공격력을 증가시킨다",
            mp_cost=10, cooldown=3, damage_multiplier=0.0,
            special_effects=["buff_allies_attack"], target_type="all", skill_type="buff"
        )
        
        skills["charge"] = EnemySkill(
            name="돌진",
            description="적에게 돌진하여 큰 피해를 준다",
            mp_cost=5, cooldown=2, damage_multiplier=1.8,
            special_effects=["knockback"], target_type="single", skill_type="attack"
        )
        
        skills["web_trap"] = EnemySkill(
            name="거미줄 함정",
            description="적을 거미줄로 묶어 이동을 제한한다",
            mp_cost=8, cooldown=4, damage_multiplier=0.5,
            special_effects=["immobilize"], target_type="single", skill_type="debuff"
        )
        
        skills["poison_bite"] = EnemySkill(
            name="독 물기",
            description="독성 공격으로 지속 피해를 준다",
            mp_cost=6, cooldown=2, damage_multiplier=1.2,
            special_effects=["poison"], target_type="single", skill_type="attack"
        )
        
        # 언데드 스킬
        skills["bone_throw"] = EnemySkill(
            name="뼈 투척",
            description="뼈를 던져서 원거리 공격한다",
            mp_cost=3, cooldown=1, damage_multiplier=1.1,
            special_effects=["ranged"], target_type="single", skill_type="attack"
        )
        
        skills["life_drain"] = EnemySkill(
            name="생명력 흡수",
            description="적의 생명력을 흡수하여 자신을 회복한다",
            mp_cost=12, cooldown=3, damage_multiplier=1.0,
            special_effects=["heal_self"], target_type="single", skill_type="attack"
        )
        
        skills["phase_shift"] = EnemySkill(
            name="위상 이동",
            description="잠시 무형화되어 물리 공격을 회피한다",
            mp_cost=15, cooldown=5, damage_multiplier=0.0,
            special_effects=["ethereal"], target_type="self", skill_type="buff"
        )
        
        # 악마 스킬
        skills["fire_dart"] = EnemySkill(
            name="화염 다트",
            description="작은 화염탄을 연사한다",
            mp_cost=4, cooldown=1, damage_multiplier=0.8,
            special_effects=["fire_damage"], target_type="single", skill_type="attack"
        )
        
        skills["teleport"] = EnemySkill(
            name="순간이동",
            description="즉시 다른 위치로 이동한다",
            mp_cost=10, cooldown=4, damage_multiplier=0.0,
            special_effects=["teleport"], target_type="self", skill_type="buff"
        )
        
        skills["battle_roar"] = EnemySkill(
            name="전투 함성",
            description="아군들을 격려하여 사기를 높인다",
            mp_cost=8, cooldown=3, damage_multiplier=0.0,
            special_effects=["buff_allies_all"], target_type="all", skill_type="buff"
        )
        
        # 구조체 스킬
        skills["earthquake"] = EnemySkill(
            name="지진",
            description="지면을 흔들어 모든 적에게 피해를 준다",
            mp_cost=20, cooldown=5, damage_multiplier=1.5,
            special_effects=["area_damage"], target_type="all", skill_type="attack"
        )
        
        skills["self_repair"] = EnemySkill(
            name="자가 수리",
            description="손상된 부분을 자동으로 수리한다",
            mp_cost=12, cooldown=4, damage_multiplier=0.0,
            special_effects=["heal_large"], target_type="self", skill_type="heal"
        )
        
        skills["laser_shot"] = EnemySkill(
            name="레이저 사격",
            description="정확한 레이저 공격을 가한다",
            mp_cost=6, cooldown=2, damage_multiplier=1.4,
            special_effects=["pierce"], target_type="single", skill_type="attack"
        )
        
        # 정령 스킬
        skills["fireball"] = EnemySkill(
            name="화염구",
            description="거대한 화염구를 던진다",
            mp_cost=15, cooldown=3, damage_multiplier=2.0,
            special_effects=["fire_damage", "burn"], target_type="single", skill_type="attack"
        )
        
        skills["ice_shard"] = EnemySkill(
            name="얼음 파편",
            description="날카로운 얼음 조각을 발사한다",
            mp_cost=10, cooldown=2, damage_multiplier=1.3,
            special_effects=["ice_damage", "slow"], target_type="single", skill_type="attack"
        )
        
        skills["freeze_aura"] = EnemySkill(
            name="빙결 오라",
            description="주변에 차가운 기운을 퍼뜨린다",
            mp_cost=18, cooldown=4, damage_multiplier=0.8,
            special_effects=["freeze_all"], target_type="all", skill_type="debuff"
        )
        
        # 인간형 스킬
        skills["sneak_attack"] = EnemySkill(
            name="기습 공격",
            description="은밀하게 접근하여 치명적인 공격을 가한다",
            mp_cost=8, cooldown=3, damage_multiplier=2.5,
            special_effects=["critical_high"], target_type="single", skill_type="attack"
        )
        
        skills["magic_missile"] = EnemySkill(
            name="마법 미사일",
            description="추적하는 마법 미사일을 발사한다",
            mp_cost=12, cooldown=2, damage_multiplier=1.6,
            special_effects=["magic_damage", "homing"], target_type="single", skill_type="attack"
        )
        
        skills["heal_allies"] = EnemySkill(
            name="동료 치유",
            description="주변 아군들을 치유한다",
            mp_cost=16, cooldown=3, damage_multiplier=0.0,
            special_effects=["heal_allies"], target_type="all", skill_type="heal"
        )
        
        skills["shield_bash"] = EnemySkill(
            name="방패 강타",
            description="방패로 강하게 내려쳐 기절시킨다",
            mp_cost=7, cooldown=3, damage_multiplier=1.2,
            special_effects=["stun"], target_type="single", skill_type="attack"
        )
        
        # 드래곤 스킬
        skills["breath_attack"] = EnemySkill(
            name="브레스 공격",
            description="강력한 브레스로 광범위한 피해를 준다",
            mp_cost=25, cooldown=4, damage_multiplier=2.8,
            special_effects=["area_damage", "fire_damage"], target_type="all", skill_type="attack"
        )
        
        skills["aerial_strike"] = EnemySkill(
            name="공중 강타",
            description="하늘에서 급강하하여 공격한다",
            mp_cost=18, cooldown=3, damage_multiplier=2.2,
            special_effects=["knockdown"], target_type="single", skill_type="attack"
        )
        
        # 기형체 스킬
        skills["tentacle_slam"] = EnemySkill(
            name="촉수 강타",
            description="여러 촉수로 동시에 공격한다",
            mp_cost=14, cooldown=2, damage_multiplier=1.8,
            special_effects=["multi_hit"], target_type="single", skill_type="attack"
        )
        
        skills["mind_blast"] = EnemySkill(
            name="정신 폭발",
            description="정신공격으로 혼란을 일으킨다",
            mp_cost=20, cooldown=4, damage_multiplier=1.0,
            special_effects=["confusion", "magic_damage"], target_type="all", skill_type="debuff"
        )
        
        return skills
    
    def _initialize_enemy_passives(self) -> Dict[str, EnemyPassive]:
        """적 패시브 능력 초기화"""
        passives = {}
        
        # 야수 패시브
        passives["pack_instinct"] = EnemyPassive(
            name="무리 본능",
            description="같은 종족이 근처에 있으면 공격력 증가",
            effect_type="stat", effect_value=0.2, condition="allies_nearby"
        )
        
        passives["natural_armor"] = EnemyPassive(
            name="천연 갑옷",
            description="두꺼운 가죽으로 물리 저항 증가",
            effect_type="resistance", effect_value=0.15, condition="always"
        )
        
        passives["predator_instinct"] = EnemyPassive(
            name="포식자 본능",
            description="적의 체력이 낮을수록 공격력 증가",
            effect_type="special", effect_value=0.5, condition="enemy_low_hp"
        )
        
        # 언데드 패시브
        passives["undead_resilience"] = EnemyPassive(
            name="언데드의 인내",
            description="즉사 공격과 독에 면역",
            effect_type="resistance", effect_value=1.0, condition="always"
        )
        
        passives["negative_energy"] = EnemyPassive(
            name="부정 에너지",
            description="치유 마법에 피해를 받는다",
            effect_type="special", effect_value=-1.0, condition="heal_received"
        )
        
        passives["death_curse"] = EnemyPassive(
            name="죽음의 저주",
            description="죽을 때 공격자에게 저주를 건다",
            effect_type="special", effect_value=1.0, condition="on_death"
        )
        
        # 악마 패시브
        passives["fire_immunity"] = EnemyPassive(
            name="화염 면역",
            description="화염 공격에 완전 면역",
            effect_type="resistance", effect_value=1.0, condition="fire_damage"
        )
        
        passives["demonic_regeneration"] = EnemyPassive(
            name="악마의 재생",
            description="턴마다 체력을 조금씩 회복한다",
            effect_type="special", effect_value=0.05, condition="turn_start"
        )
        
        passives["corruption_aura"] = EnemyPassive(
            name="타락 오라",
            description="주변 적들의 방어력을 감소시킨다",
            effect_type="special", effect_value=-0.1, condition="enemy_nearby"
        )
        
        # 구조체 패시브
        passives["magic_resistance"] = EnemyPassive(
            name="마법 저항",
            description="모든 마법 공격 피해 감소",
            effect_type="resistance", effect_value=0.3, condition="magic_damage"
        )
        
        passives["self_maintenance"] = EnemyPassive(
            name="자가 정비",
            description="전투 시작 시 일부 체력 회복",
            effect_type="special", effect_value=0.1, condition="combat_start"
        )
        
        passives["overload"] = EnemyPassive(
            name="과부하",
            description="체력이 낮을 때 공격력과 속도 증가",
            effect_type="special", effect_value=0.8, condition="low_hp"
        )
        
        # 정령 패시브
        passives["elemental_affinity"] = EnemyPassive(
            name="원소 친화",
            description="같은 원소 공격에 면역, 반대 원소에 약함",
            effect_type="special", effect_value=1.0, condition="elemental"
        )
        
        passives["energy_form"] = EnemyPassive(
            name="에너지 형태",
            description="물리 공격 피해 50% 감소",
            effect_type="resistance", effect_value=0.5, condition="physical_damage"
        )
        
        passives["unstable_core"] = EnemyPassive(
            name="불안정한 핵",
            description="죽을 때 폭발하여 주변에 피해",
            effect_type="special", effect_value=2.0, condition="on_death"
        )
        
        # 인간형 패시브
        passives["tactical_genius"] = EnemyPassive(
            name="전술 천재",
            description="아군이 많을수록 모든 능력치 증가",
            effect_type="special", effect_value=0.15, condition="allies_count"
        )
        
        passives["weapon_mastery"] = EnemyPassive(
            name="무기 숙련",
            description="무기 공격 시 크리티컬 확률 증가",
            effect_type="special", effect_value=0.2, condition="weapon_attack"
        )
        
        passives["combat_training"] = EnemyPassive(
            name="전투 훈련",
            description="모든 기본 능력치 10% 증가",
            effect_type="stat", effect_value=0.1, condition="always"
        )
        
        # 드래곤 패시브
        passives["dragon_fear"] = EnemyPassive(
            name="용의 공포",
            description="주변 적들의 공격력과 명중률 감소",
            effect_type="special", effect_value=-0.2, condition="enemy_nearby"
        )
        
        passives["ancient_power"] = EnemyPassive(
            name="고대의 힘",
            description="시간이 지날수록 더 강해진다",
            effect_type="special", effect_value=0.05, condition="turn_count"
        )
        
        passives["thick_scales"] = EnemyPassive(
            name="두꺼운 비늘",
            description="모든 피해 20% 감소",
            effect_type="resistance", effect_value=0.2, condition="always"
        )
        
        # 기형체 패시브
        passives["madness_aura"] = EnemyPassive(
            name="광기 오라",
            description="주변 적들이 랜덤하게 행동한다",
            effect_type="special", effect_value=0.3, condition="enemy_nearby"
        )
        
        passives["adaptive_evolution"] = EnemyPassive(
            name="적응 진화",
            description="받은 피해 타입에 점점 저항을 얻는다",
            effect_type="special", effect_value=0.1, condition="damage_received"
        )
        
        passives["eldritch_horror"] = EnemyPassive(
            name="공포스러운 존재",
            description="처음 만나는 적은 첫 턴에 행동 불가",
            effect_type="special", effect_value=1.0, condition="first_encounter"
        )
        
        return passives
    
    def _initialize_floor_prefixes(self) -> Dict[int, List[EnemyPrefix]]:
        """층별 등장 가능한 접두사 정의"""
        return {
            # 1-5층: 기본 접두사
            1: [EnemyPrefix.SWIFT, EnemyPrefix.SAVAGE],
            2: [EnemyPrefix.SWIFT, EnemyPrefix.SAVAGE, EnemyPrefix.ARMORED],
            3: [EnemyPrefix.SWIFT, EnemyPrefix.SAVAGE, EnemyPrefix.ARMORED, EnemyPrefix.POISONOUS],
            4: [EnemyPrefix.SWIFT, EnemyPrefix.SAVAGE, EnemyPrefix.ARMORED, EnemyPrefix.POISONOUS, EnemyPrefix.MAGICAL],
            5: [EnemyPrefix.SWIFT, EnemyPrefix.SAVAGE, EnemyPrefix.ARMORED, EnemyPrefix.POISONOUS, EnemyPrefix.MAGICAL, EnemyPrefix.REGENERATING],
            
            # 6-10층: 중급 접두사
            6: [EnemyPrefix.ELITE, EnemyPrefix.CORRUPTED, EnemyPrefix.ICY, EnemyPrefix.FIERY],
            7: [EnemyPrefix.ELITE, EnemyPrefix.CORRUPTED, EnemyPrefix.ICY, EnemyPrefix.FIERY, EnemyPrefix.ELECTRIC],
            8: [EnemyPrefix.ELITE, EnemyPrefix.CORRUPTED, EnemyPrefix.ICY, EnemyPrefix.FIERY, EnemyPrefix.ELECTRIC, EnemyPrefix.EXPLOSIVE],
            9: [EnemyPrefix.ELITE, EnemyPrefix.CORRUPTED, EnemyPrefix.BLESSED, EnemyPrefix.BERSERKING],
            10: [EnemyPrefix.ELITE, EnemyPrefix.ANCIENT, EnemyPrefix.BLESSED, EnemyPrefix.BERSERKING, EnemyPrefix.INVISIBLE],
            
            # 11층 이상: 모든 접두사 가능
            11: list(EnemyPrefix)
        }
    
    def get_floor_enemies(self, floor: int) -> List[str]:
        """층별 등장 적 종류 반환"""
        floor_ranges = {
            (1, 3): ["늑대", "거미", "스켈레톤"],
            (4, 6): ["늑대", "거미", "스켈레톤", "곰", "좀비", "임프"],
            (7, 10): ["곰", "좀비", "임프", "오크", "골렘", "도적"],
            (11, 15): ["오크", "골렘", "도적", "기계병", "화염정령", "마법사"],
            (16, 20): ["기계병", "화염정령", "얼음정령", "마법사", "전사", "유령"],
            (21, 30): ["얼음정령", "전사", "유령", "촉수괴물", "와이번"],
            (31, 50): ["촉수괴물", "와이번", "고대 골렘", "드래곤 로드", "섀도우 마스터"],
            (51, 100): ["모든 정예 적들"]
        }
        
        for (min_floor, max_floor), enemies in floor_ranges.items():
            if min_floor <= floor <= max_floor:
                return enemies
        
        # 100층 이후는 모든 적 + 특별한 적들
        return list(self.enemy_templates.keys())
    
    def generate_enemy(self, floor: int, force_prefix: EnemyPrefix = None) -> Dict[str, Any]:
        """층수에 맞는 적 생성 (접두사 포함) - 기존 Enemy 시스템과 밸런스 통합"""
        # 층별 등장 적 목록에서 선택
        available_enemies = self.get_floor_enemies(floor)
        enemy_name = random.choice(available_enemies)
        
        if enemy_name not in self.enemy_templates:
            enemy_name = "늑대"  # 기본값
        
        template = self.enemy_templates[enemy_name]
        
        # 🔄 기존 enemy_system.py와 밸런스 맞추기
        try:
            from game.enemy_system import Enemy, EnemyType
            # 기존 시스템의 스탯 참조
            base_stats_map = {
                "늑대": (45, 18, 8, 15),
                "거미": (30, 15, 5, 20), 
                "스켈레톤": (35, 20, 12, 10),
                "곰": (80, 25, 15, 8),
                "좀비": (60, 16, 6, 6),
                "임프": (25, 14, 8, 16),
                "오크": (55, 22, 12, 11),
                "골렘": (100, 20, 25, 5),
                "도적": (40, 20, 8, 18),
                "마법사": (35, 16, 6, 12),
                "전사": (70, 24, 16, 10),
                "화염정령": (45, 24, 10, 14),
                "얼음정령": (50, 20, 15, 10),
                "유령": (40, 22, 20, 18),
                "기계병": (65, 18, 18, 12),
                "와이번": (150, 30, 20, 16),
                "촉수괴물": (85, 26, 12, 8)
            }
            
            # 기존 시스템 스탯 사용 또는 템플릿 기본값
            if enemy_name in base_stats_map:
                base_hp, base_attack, base_defense, base_speed = base_stats_map[enemy_name]
            else:
                base_hp, base_attack, base_defense, base_speed = template.base_hp, template.base_attack, template.base_defense, template.base_speed
        except:
            # 기존 시스템 없으면 템플릿 사용
            base_hp, base_attack, base_defense, base_speed = template.base_hp, template.base_attack, template.base_defense, template.base_speed
        
        # 접두사 적용 확률 (층수가 높을수록 확률 증가)
        prefix_chance = min(0.05 + (floor * 0.02), 0.5)  # 최대 50%
        prefix = None
        
        if force_prefix or random.random() < prefix_chance:
            # 해당 층에서 사용 가능한 접두사 목록
            available_prefixes = []
            for min_floor, prefixes in self.floor_prefixes.items():
                if floor >= min_floor:
                    available_prefixes = prefixes
            
            if available_prefixes:
                prefix = force_prefix or random.choice(available_prefixes)
        
        # 🔥 기존 시스템 호환 레벨 스케일링 (더 보수적)
        level = max(1, floor)
        # 기존 시스템 참고하여 스케일링 완화
        if floor <= 5:
            scale = 1.0 + (floor - 1) * 0.2  # 1층=1.0, 5층=1.8
        elif floor <= 15:
            scale = 1.8 + (floor - 5) * 0.15  # 6층~15층 점진적 증가
        elif floor <= 30:
            scale = 3.3 + (floor - 15) * 0.1  # 16층~30층 완만한 증가
        else:
            scale = 4.8 + (floor - 30) * 0.05  # 31층 이후 매우 완만
        
        # 기본 스탯 계산 (기존 시스템 호환)
        enemy_data = {
            "name": enemy_name,
            "display_name": f"{prefix.value + ' ' if prefix else ''}{enemy_name}",
            "type": template.enemy_type.value,
            "behavior": template.behavior.value,
            "level": level,
            "max_hp": int(base_hp * scale),
            "current_hp": int(base_hp * scale),
            "attack": int(base_attack * scale),
            "defense": int(base_defense * scale),
            "speed": int(base_speed * scale),
            "max_mp": int(template.base_mp * scale),
            "current_mp": int(template.base_mp * scale),
            "ai_aggression": template.ai_aggression,
            "ai_intelligence": template.ai_intelligence,
            "special_abilities": template.special_abilities.copy(),
            "skills": [skill.name for skill in template.skills],
            "passives": [passive.name for passive in template.passives],
            "prefix": prefix.value if prefix else None,
            # 🎯 기존 시스템 호환 보상 계산
            "experience_reward": int(max(5, floor * 2 * scale)),
            "gold_reward": int(max(2, floor * 1 * scale)),
            "last_skill_use": {},  # 스킬 쿨다운 관리
            "status_effects": {},  # 상태 이상
            "ai_memory": {  # AI 기억 시스템
                "player_last_seen": None,
                "ally_positions": [],
                "threat_level": 1.0,
                "preferred_target": None
            }
        }
        
        # 접두사 효과 적용
        if prefix:
            enemy_data = self._apply_prefix_effects(enemy_data, prefix)
        
        return enemy_data
    
    def _apply_prefix_effects(self, enemy_data: Dict[str, Any], prefix: EnemyPrefix) -> Dict[str, Any]:
        """접두사 효과 적용"""
        if prefix == EnemyPrefix.ELITE:
            # 모든 능력치 +50%
            enemy_data["max_hp"] = int(enemy_data["max_hp"] * 1.5)
            enemy_data["current_hp"] = enemy_data["max_hp"]
            enemy_data["attack"] = int(enemy_data["attack"] * 1.5)
            enemy_data["defense"] = int(enemy_data["defense"] * 1.5)
            enemy_data["speed"] = int(enemy_data["speed"] * 1.5)
            enemy_data["experience_reward"] = int(enemy_data["experience_reward"] * 2)
            enemy_data["gold_reward"] = int(enemy_data["gold_reward"] * 2)
            
        elif prefix == EnemyPrefix.ANCIENT:
            # HP +100%, 특수 스킬 추가
            enemy_data["max_hp"] = int(enemy_data["max_hp"] * 2.0)
            enemy_data["current_hp"] = enemy_data["max_hp"]
            enemy_data["special_abilities"].append("ancient_wisdom")
            enemy_data["skills"].append("time_stop")
            enemy_data["experience_reward"] = int(enemy_data["experience_reward"] * 3)
            
        elif prefix == EnemyPrefix.CORRUPTED:
            # 독 면역, 독 공격
            enemy_data["special_abilities"].extend(["poison_immunity", "poison_attack"])
            enemy_data["passives"].append("corruption_aura")
            
        elif prefix == EnemyPrefix.BLESSED:
            # 회복 능력, 신성 공격
            enemy_data["special_abilities"].extend(["healing", "holy_damage"])
            enemy_data["skills"].append("divine_protection")
            
        elif prefix == EnemyPrefix.SAVAGE:
            # 공격력 +100%, 방어력 -50%
            enemy_data["attack"] = int(enemy_data["attack"] * 2.0)
            enemy_data["defense"] = int(enemy_data["defense"] * 0.5)
            enemy_data["ai_aggression"] = min(2.0, enemy_data["ai_aggression"] * 1.5)
            
        elif prefix == EnemyPrefix.ARMORED:
            # 방어력 +200%, 속도 -50%
            enemy_data["defense"] = int(enemy_data["defense"] * 3.0)
            enemy_data["speed"] = int(enemy_data["speed"] * 0.5)
            enemy_data["special_abilities"].append("damage_reduction")
            
        elif prefix == EnemyPrefix.SWIFT:
            # 속도 +100%, 회피율 증가
            enemy_data["speed"] = int(enemy_data["speed"] * 2.0)
            enemy_data["special_abilities"].append("high_evasion")
            
        elif prefix == EnemyPrefix.MAGICAL:
            # 마법 공격, 마나 보유
            enemy_data["max_mp"] = max(30, enemy_data["max_mp"] * 2)
            enemy_data["current_mp"] = enemy_data["max_mp"]
            enemy_data["skills"].extend(["magic_missile", "mana_shield"])
            
        elif prefix == EnemyPrefix.POISONOUS:
            # 독 공격, 독 면역
            enemy_data["special_abilities"].extend(["poison_attack", "poison_immunity"])
            enemy_data["passives"].append("toxic_skin")
            
        elif prefix == EnemyPrefix.REGENERATING:
            # 턴마다 HP 회복
            enemy_data["special_abilities"].append("regeneration")
            enemy_data["passives"].append("fast_healing")
            
        elif prefix == EnemyPrefix.EXPLOSIVE:
            # 죽을 때 폭발
            enemy_data["special_abilities"].append("death_explosion")
            enemy_data["passives"].append("unstable_core")
            
        elif prefix == EnemyPrefix.INVISIBLE:
            # 은신 능력
            enemy_data["special_abilities"].extend(["stealth", "surprise_attack"])
            enemy_data["ai_intelligence"] = min(2.0, enemy_data["ai_intelligence"] * 1.3)
            
        elif prefix == EnemyPrefix.BERSERKING:
            # 체력 낮을수록 강해짐
            enemy_data["special_abilities"].append("berserker_rage")
            enemy_data["passives"].append("rage_mode")
            
        elif prefix == EnemyPrefix.ICY:
            # 빙결 공격
            enemy_data["special_abilities"].extend(["ice_attack", "freeze_aura"])
            enemy_data["skills"].append("ice_shard")
            
        elif prefix == EnemyPrefix.FIERY:
            # 화상 공격
            enemy_data["special_abilities"].extend(["fire_attack", "burn_aura"])
            enemy_data["skills"].append("fireball")
            
        elif prefix == EnemyPrefix.ELECTRIC:
            # 마비 공격
            enemy_data["special_abilities"].extend(["electric_attack", "shock_aura"])
            enemy_data["skills"].append("lightning_bolt")
        
        return enemy_data
    
    def calculate_intelligent_move(self, enemy_data: Dict[str, Any], enemy_pos: Tuple[int, int], 
                                 player_pos: Tuple[int, int], ally_positions: List[Tuple[int, int]],
                                 world_map) -> Tuple[int, int]:
        """고급 지능형 이동 계산"""
        enemy_x, enemy_y = enemy_pos
        player_x, player_y = player_pos
        
        behavior = enemy_data.get("behavior", "공격적")
        aggression = enemy_data.get("ai_aggression", 1.0)
        intelligence = enemy_data.get("ai_intelligence", 1.0)
        current_hp_ratio = enemy_data.get("current_hp", 1) / max(1, enemy_data.get("max_hp", 1))
        
        # 가능한 이동 위치들
        possible_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                new_x, new_y = enemy_x + dx, enemy_y + dy
                if world_map.is_valid_pos(new_x, new_y) and world_map._can_move_to(new_x, new_y):
                    possible_moves.append((new_x, new_y))
        
        if not possible_moves:
            return enemy_pos  # 이동 불가
        
        # 각 이동 위치의 점수 계산
        move_scores = {}
        
        for move_pos in possible_moves:
            move_x, move_y = move_pos
            score = 0
            
            # 플레이어와의 거리
            distance_to_player = abs(move_x - player_x) + abs(move_y - player_y)
            
            # 행동 패턴별 점수 계산
            if behavior == "공격적":
                # 플레이어에게 더 가까이 가려고 함
                score += (10 - distance_to_player) * aggression
                
            elif behavior == "신중한":
                if current_hp_ratio > 0.5:
                    # 체력이 충분하면 공격적
                    score += (10 - distance_to_player) * aggression
                else:
                    # 체력이 낮으면 도망
                    score += distance_to_player * 2
                    
            elif behavior == "전술적":
                # 아군과의 협력 고려
                ally_support = 0
                for ally_pos in ally_positions:
                    ally_distance = abs(move_x - ally_pos[0]) + abs(move_y - ally_pos[1])
                    if ally_distance <= 3:  # 3칸 이내 아군
                        ally_support += 1
                
                # 플레이어 접근 + 아군 지원
                score += (8 - distance_to_player) * aggression + ally_support * intelligence
                
            elif behavior == "영역형":
                # 특정 영역 방어 (스폰 지점 중심)
                spawn_distance = abs(move_x - enemy_data.get("spawn_x", enemy_x)) + abs(move_y - enemy_data.get("spawn_y", enemy_y))
                if spawn_distance <= 5:
                    score += 5 - spawn_distance
                if distance_to_player <= 3:
                    score += 3  # 플레이어가 가까이 오면 대응
                    
            elif behavior == "매복형":
                # 플레이어 주변에서 기다리기
                if 2 <= distance_to_player <= 4:
                    score += intelligence * 3
                elif distance_to_player <= 1:
                    score += aggression * 5  # 기습!
                    
            elif behavior == "지원형":
                # 아군 근처에서 지원
                ally_support = 0
                for ally_pos in ally_positions:
                    ally_distance = abs(move_x - ally_pos[0]) + abs(move_y - ally_pos[1])
                    if ally_distance <= 2:
                        ally_support += 2
                score += ally_support * intelligence
                
            elif behavior == "광전사":
                # 체력 낮을수록 더 공격적
                rage_bonus = (1.0 - current_hp_ratio) * 2
                score += (10 - distance_to_player) * (aggression + rage_bonus)
                
            elif behavior == "무리사냥":
                # 같은 종족끼리 뭉치기
                pack_bonus = 0
                for ally_pos in ally_positions:
                    ally_distance = abs(move_x - ally_pos[0]) + abs(move_y - ally_pos[1])
                    if ally_distance <= 2:
                        pack_bonus += 1
                
                if pack_bonus >= 2:  # 무리가 형성되면 공격적
                    score += (8 - distance_to_player) * aggression * 1.5
                else:  # 무리 형성을 위해 모이기
                    score += pack_bonus * intelligence
            
            # 지형 보너스 (지능이 높을수록 지형 활용)
            terrain_bonus = 0
            if hasattr(world_map, 'tiles') and world_map.is_valid_pos(move_x, move_y):
                tile = world_map.tiles[move_y][move_x]
                tile_type = str(tile.type) if hasattr(tile, 'type') else 'FLOOR'
                
                # 엄폐물 활용
                if 'WALL' in tile_type:
                    terrain_bonus += intelligence * 2
                elif 'DOOR' in tile_type:
                    terrain_bonus += intelligence * 1
            
            score += terrain_bonus
            
            # 랜덤 요소 (지능이 낮을수록 랜덤성 증가)
            random_factor = random.uniform(-2, 2) * (2.0 - intelligence)
            score += random_factor
            
            move_scores[move_pos] = score
        
        # 최고 점수의 이동 위치 선택
        best_move = max(move_scores.items(), key=lambda x: x[1])
        return best_move[0]
    
    def should_use_skill(self, enemy_data: Dict[str, Any], available_skills: List[str], 
                        combat_situation: Dict[str, Any]) -> Optional[str]:
        """적이 스킬을 사용할지 결정"""
        if not available_skills or enemy_data.get("current_mp", 0) <= 0:
            return None
        
        behavior = enemy_data.get("behavior", "공격적")
        intelligence = enemy_data.get("ai_intelligence", 1.0)
        current_hp_ratio = enemy_data.get("current_hp", 1) / max(1, enemy_data.get("max_hp", 1))
        
        # 스킬 사용 우선순위 계산
        skill_priorities = {}
        
        for skill_name in available_skills:
            if skill_name not in self.enemy_skills:
                continue
                
            skill = self.enemy_skills[skill_name]
            priority = 0
            
            # 마나 비용 확인
            if skill.mp_cost > enemy_data.get("current_mp", 0):
                continue
            
            # 쿨다운 확인
            last_used = enemy_data.get("last_skill_use", {}).get(skill_name, 0)
            current_turn = combat_situation.get("current_turn", 0)
            if current_turn - last_used < skill.cooldown:
                continue
            
            # 스킬 타입별 우선순위
            if skill.skill_type == "attack":
                if behavior in ["공격적", "광전사"]:
                    priority += 3
                elif behavior == "전술적":
                    priority += 2
                    
            elif skill.skill_type == "heal":
                if current_hp_ratio < 0.3:
                    priority += 5  # 체력 낮으면 최우선
                elif behavior == "지원형":
                    priority += 2
                    
            elif skill.skill_type == "buff":
                ally_count = len(combat_situation.get("allies", []))
                if ally_count > 1 and behavior in ["지원형", "전술적"]:
                    priority += 3
                    
            elif skill.skill_type == "debuff":
                if behavior in ["전술적", "매복형"]:
                    priority += 2
            
            # 지능이 높을수록 스킬 사용 빈도 증가
            priority = int(priority * intelligence)
            
            # 상황별 보너스
            enemy_count = len(combat_situation.get("enemies", []))
            if skill.target_type == "all" and enemy_count > 2:
                priority += 2
            
            skill_priorities[skill_name] = priority
        
        # 가장 높은 우선순위 스킬 선택
        if skill_priorities:
            best_skill = max(skill_priorities.items(), key=lambda x: x[1])
            if best_skill[1] > 0:
                return best_skill[0]
        
        return None

# 전역 인스턴스 생성
advanced_field_ai = AdvancedFieldEnemyAI()

def generate_floor_enemies(floor: int, enemy_count: int) -> List[Dict[str, Any]]:
    """층별 적 생성 (메인 함수)"""
    enemies = []
    
    for _ in range(enemy_count):
        enemy = advanced_field_ai.generate_enemy(floor)
        enemies.append(enemy)
    
    return enemies

def get_intelligent_enemy_move(enemy_data: Dict[str, Any], enemy_pos: Tuple[int, int],
                              player_pos: Tuple[int, int], ally_positions: List[Tuple[int, int]],
                              world_map) -> Tuple[int, int]:
    """지능형 적 이동 계산 (메인 함수)"""
    return advanced_field_ai.calculate_intelligent_move(
        enemy_data, enemy_pos, player_pos, ally_positions, world_map
    )

def get_enemy_skill_choice(enemy_data: Dict[str, Any], combat_situation: Dict[str, Any]) -> Optional[str]:
    """적 스킬 선택 (메인 함수)"""
    available_skills = enemy_data.get("skills", [])
    return advanced_field_ai.should_use_skill(enemy_data, available_skills, combat_situation)

if __name__ == "__main__":
    # 테스트 코드
    print("🧠 고급 필드 적 AI 시스템 테스트")
    
    # 다양한 층의 적 생성 테스트
    for floor in [1, 5, 10, 20, 50]:
        print(f"\n🏢 {floor}층 적 생성:")
        enemies = generate_floor_enemies(floor, 3)
        for enemy in enemies:
            print(f"  - {enemy['display_name']} (레벨 {enemy['level']}) HP:{enemy['current_hp']} 공격:{enemy['attack']}")
            if enemy.get('skills'):
                print(f"    스킬: {', '.join(enemy['skills'])}")
            if enemy.get('special_abilities'):
                print(f"    특수능력: {', '.join(enemy['special_abilities'])}")
