#!/usr/bin/env python3
from typing import Dict, List, Any
from enum import Enum
import random

# StatusType import
try:
    from .status_effects import StatusType
except ImportError:
    # 간단한 StatusType 정의
    class StatusType:
        POISON = "poison"
        BURN = "burn"
        BOOST_ATK = "boost_atk"

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

def check_ultimate_conditions(caster, skill_name: str) -> tuple[bool, str]:
    """궁극기 사용 조건 체크 - 직업별 기믹 시스템 활용 (고유 최대치 존중)"""
    character_class = getattr(caster, 'character_class', '전사')
    base_attack = getattr(caster, 'physical_attack', getattr(caster, 'attack', 100))
    
    # 직업별 궁극기 조건 체크 (각 직업의 고유 최대치 기반 - 난이도 완화)
    if character_class == "도적":
        if "독혈촉진" in skill_name:
            poison_stacks = getattr(caster, 'poison_stacks', 0)
            # 도적 맹독 최대치는 공격력 기반으로 동적 계산 (공격력 / 10, 최소 8, 최대 96)
            attack_power = safe_get_attack_stat(caster, 'physical_attack', 100)
            max_poison = max(8, min(96, attack_power // 10))  # 공격력의 1/10, 8~96 범위
            required_poison = max(3, int(max_poison * 0.3))  # 최대치의 30% 이상 (더 완화)
            if poison_stacks < required_poison:
                return False, f"독혈촉진은 맹독 스택이 {required_poison} 이상 필요합니다. (현재: {poison_stacks}/{max_poison}, 공격력: {attack_power})"
                
    elif character_class == "궁수":
        if "정밀 관통사격" in skill_name:
            aim_points = getattr(caster, 'aim_points', 0)
            max_aim = getattr(caster, 'max_aim_points', 10)  # 궁수 조준 포인트 최대 10 (고정)
            required_aim = max(4, int(max_aim * 0.5))  # 최대치의 50% 이상 (70%→50%)
            if aim_points < required_aim:
                return False, f"정밀 관통사격은 조준 포인트가 {required_aim} 이상 필요합니다. (현재: {aim_points}/{max_aim})"
                
    elif character_class == "암살자":
        if "그림자 처형" in skill_name:
            shadow_count = getattr(caster, 'shadow_count', 0)
            max_shadows = getattr(caster, 'max_shadow_count', 5)  # 암살자 그림자 최대 5
            required_shadows = max(2, int(max_shadows * 0.6))  # 최대치의 60% 이상 (80%→60%)
            if shadow_count < required_shadows:
                return False, f"그림자 처형은 그림자가 {required_shadows}개 이상 필요합니다. (현재: {shadow_count}/{max_shadows})"
                
    elif character_class == "검성":
        if "일섬" in skill_name:
            sword_aura = getattr(caster, 'sword_aura', 0)
            max_sword_aura = getattr(caster, 'max_sword_aura', 10)  # 검성 검기 최대 10
            required_aura = max(5, int(max_sword_aura * 0.6))  # 최대치의 60% 이상 (80%→60%)
            if sword_aura < required_aura:
                return False, f"일섬은 검기가 {required_aura} 이상 필요합니다. (현재: {sword_aura}/{max_sword_aura})"
                
    elif character_class == "바드":
        if "영혼의 노래" in skill_name:
            melody_stacks = getattr(caster, 'melody_stacks', 0)
            max_melody = getattr(caster, 'max_melody_stacks', 7)  # 바드 멜로디 최대 7
            required_melody = 7  # 바드는 무조건 최대치 7이어야 궁극기 사용 가능
            if melody_stacks < required_melody:
                return False, f"영혼의 노래는 멜로디 스택이 {required_melody} 이상 필요합니다. (현재: {melody_stacks}/{max_melody})"
                
    elif character_class == "광전사":
        if "최후의 광기" in skill_name:
            rage_stacks = getattr(caster, 'rage_stacks', 0)
            max_rage = getattr(caster, 'max_rage_stacks', 100)  # 광전사 분노 최대 100 (고정)
            required_rage = max(40, int(max_rage * 0.6))  # 최대치의 60% 이상 (80%→60%)
            if rage_stacks < required_rage:
                return False, f"최후의 광기는 분노가 {required_rage} 이상 필요합니다. (현재: {rage_stacks}/{max_rage})"
                
    elif character_class == "아크메이지":
        if "마력 폭발" in skill_name:
            fire_count = getattr(caster, 'fire_count', 0)
            ice_count = getattr(caster, 'ice_count', 0)
            lightning_count = getattr(caster, 'lightning_count', 0)
            max_element = getattr(caster, 'max_element_count', 20)  # 아크메이지 원소 최대 20
            total_elements = fire_count + ice_count + lightning_count
            required_elements = max(8, int(max_element * 0.5))  # 최대치의 50% 이상 (75%→50%)
            if total_elements < required_elements:
                return False, f"마력 폭발은 원소 카운트가 총 {required_elements} 이상 필요합니다. (현재: {total_elements}/{max_element})"
                
    elif character_class == "용기사":
        if "드래곤 브레스" in skill_name:
            dragon_marks = getattr(caster, 'dragon_marks', 0)
            max_dragon = getattr(caster, 'max_dragon_marks', 10)  # 용기사 드래곤 각인 최대 10
            required_marks = max(4, int(max_dragon * 0.5))  # 최대치의 50% 이상 (70%→50%)
            if dragon_marks < required_marks:
                return False, f"드래곤 브레스는 드래곤 각인이 {required_marks} 이상 필요합니다. (현재: {dragon_marks}/{max_dragon})"
                
    elif character_class == "몽크":
        if "폭렬권" in skill_name:
            strike_marks = getattr(caster, 'strike_marks', 0)
            chi_points = getattr(caster, 'chi_points', 0)
            max_chi = getattr(caster, 'max_chi_points', 10)  # 몽크 기 에너지 최대 10
            required_chi = max(5, int(max_chi * 0.6))  # 최대치의 60% 이상 (80%→60%)
            required_strikes = max(2, strike_marks)  # 타격 표식 2개 이상 (3→2)
            if chi_points < required_chi or strike_marks < required_strikes:
                return False, f"폭렬권은 기 에너지 {required_chi} 이상, 타격 표식 {required_strikes} 이상 필요합니다. (현재: 기 {chi_points}/{max_chi}, 표식 {strike_marks})"
    
    # 전사 계열 (난이도 완화)
    elif character_class == "전사":
        if "천지개벽" in skill_name or "파멸의 일격" in skill_name:
            warrior_focus = getattr(caster, 'warrior_focus', 0)
            required_focus = max(5, warrior_focus)  # 전사 집중도 5 이상 (8→5)
            if warrior_focus < required_focus:
                return False, f"전사 궁극기는 전사 집중도 {required_focus} 이상 필요합니다. (현재: {warrior_focus})"
                
    elif character_class == "성기사":
        if "천벌의 심판" in skill_name or "성스러운 희생" in skill_name:
            holy_power = getattr(caster, 'holy_power', 0)
            max_holy = getattr(caster, 'max_holy_power', 15)  # 성기사 성력 최대 15
            required_holy = max(6, int(max_holy * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if holy_power < required_holy:
                return False, f"성기사 궁극기는 성력이 {required_holy} 이상 필요합니다. (현재: {holy_power}/{max_holy})"
                
    elif character_class == "암흑기사":
        if "흡혈 궁극기" in skill_name or "어둠의 지배" in skill_name:
            dark_power = getattr(caster, 'dark_power', 0)
            max_dark = getattr(caster, 'max_dark_power', 12)  # 암흑기사 암흑력 최대 12
            required_dark = max(5, int(max_dark * 0.5))  # 최대치의 50% 이상 (75%→50%)
            if dark_power < required_dark:
                return False, f"암흑기사 궁극기는 암흑력이 {required_dark} 이상 필요합니다. (현재: {dark_power}/{max_dark})"
    
    # 마법사 계열 추가 (난이도 완화)
    elif character_class == "네크로맨서":
        if "죽음의 군주" in skill_name or "영혼 지배" in skill_name:
            soul_power = getattr(caster, 'soul_power', 0)
            max_soul = getattr(caster, 'max_soul_power', 15)  # 네크로맨서 영혼력 최대 15
            required_soul = max(6, int(max_soul * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if soul_power < required_soul:
                return False, f"네크로맨서 궁극기는 영혼력이 {required_soul} 이상 필요합니다. (현재: {soul_power}/{max_soul})"
                
    elif character_class == "정령술사":
        if "원소 융합" in skill_name or "정령왕 소환" in skill_name:
            elemental_harmony = getattr(caster, 'elemental_harmony', 0)
            max_harmony = getattr(caster, 'max_elemental_harmony', 8)  # 정령술사 원소 조화 최대 8
            required_harmony = max(4, int(max_harmony * 0.6))  # 최대치의 60% 이상 (80%→60%)
            if elemental_harmony < required_harmony:
                return False, f"정령술사 궁극기는 원소 조화가 {required_harmony} 이상 필요합니다. (현재: {elemental_harmony}/{max_harmony})"
    
    # 특수 직업들 추가 (난이도 완화)
    elif character_class == "시간술사":
        if "시간 정지" in skill_name or "시간 역행" in skill_name:
            time_energy = getattr(caster, 'time_energy', 0)
            max_time = getattr(caster, 'max_time_energy', 12)  # 시간술사 시간 에너지 최대 12
            required_time = max(5, int(max_time * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if time_energy < required_time:
                return False, f"시간술사 궁극기는 시간 에너지가 {required_time} 이상 필요합니다. (현재: {time_energy}/{max_time})"
                
    elif character_class == "연금술사":
        if "대폭발 반응" in skill_name or "현자의 돌" in skill_name:
            formula_mastery = getattr(caster, 'formula_mastery', 0)
            max_formula = getattr(caster, 'max_formula_mastery', 10)  # 연금술사 공식 숙련도 최대 10
            required_formula = max(4, int(max_formula * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if formula_mastery < required_formula:
                return False, f"연금술사 궁극기는 공식 숙련도가 {required_formula} 이상 필요합니다. (현재: {formula_mastery}/{max_formula})"
                
    elif character_class == "차원술사":
        if "차원 붕괴" in skill_name or "공간 절단" in skill_name:
            dimension_control = getattr(caster, 'dimension_control', 0)
            max_dimension = getattr(caster, 'max_dimension_control', 8)  # 차원술사 차원 제어력 최대 8
            required_dimension = max(3, int(max_dimension * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if dimension_control < required_dimension:
                return False, f"차원술사 궁극기는 차원 제어력이 {required_dimension} 이상 필요합니다. (현재: {dimension_control}/{max_dimension})"
                
    elif character_class == "마검사":
        if "마검 오의" in skill_name or "마검 해방" in skill_name:
            sword_magic_sync = getattr(caster, 'sword_magic_sync', 0)
            max_sync = getattr(caster, 'max_sword_magic_sync', 12)  # 마검사 검마 동조 최대 12
            required_sync = max(5, int(max_sync * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if sword_magic_sync < required_sync:
                return False, f"마검사 궁극기는 검마 동조가 {required_sync} 이상 필요합니다. (현재: {sword_magic_sync}/{max_sync})"
    
    # 기타 특수 직업들 (난이도 완화)
    elif character_class == "기계공학자":
        if "메가 레이저" in skill_name or "기계 군단" in skill_name:
            mechanical_energy = getattr(caster, 'mechanical_energy', 0)
            max_mechanical = getattr(caster, 'max_mechanical_energy', 20)  # 기계공학자 기계 에너지 최대 20
            required_mechanical = max(8, int(max_mechanical * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if mechanical_energy < required_mechanical:
                return False, f"기계공학자 궁극기는 기계 에너지가 {required_mechanical} 이상 필요합니다. (현재: {mechanical_energy}/{max_mechanical})"
                
    elif character_class == "무당":
        if "영혼 분리" in skill_name or "조상령 소환" in skill_name:
            spirit_connection = getattr(caster, 'spirit_connection', 0)
            max_spirit = getattr(caster, 'max_spirit_connection', 10)  # 무당 영혼 연결 최대 10
            required_spirit = max(4, int(max_spirit * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if spirit_connection < required_spirit:
                return False, f"무당 궁극기는 영혼 연결이 {required_spirit} 이상 필요합니다. (현재: {spirit_connection}/{max_spirit})"
    
    # 모험가 계열 (난이도 완화)
    elif character_class == "해적":
        if "해적의 보물" in skill_name or "유령선 소환" in skill_name:
            treasure_count = getattr(caster, 'treasure_count', 0)
            max_treasure = getattr(caster, 'max_treasure_count', 8)  # 해적 보물 개수 최대 8
            required_treasure = max(3, int(max_treasure * 0.5))  # 최대치의 50% 이상 (75%→50%)
            if treasure_count < required_treasure:
                return False, f"해적 궁극기는 보물이 {required_treasure}개 이상 필요합니다. (현재: {treasure_count}/{max_treasure})"
                
    elif character_class == "사무라이":
        if "무사도 비의" in skill_name or "천검무" in skill_name:
            bushido_spirit = getattr(caster, 'bushido_spirit', 0)
            max_bushido = getattr(caster, 'max_bushido_spirit', 15)  # 사무라이 무사도 정신 최대 15
            required_bushido = max(6, int(max_bushido * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if bushido_spirit < required_bushido:
                return False, f"사무라이 궁극기는 무사도 정신이 {required_bushido} 이상 필요합니다. (현재: {bushido_spirit}/{max_bushido})"
    
    # 자연 계열 (난이도 완화)
    elif character_class == "드루이드":
        if "자연의 심판" in skill_name or "세계수 소환" in skill_name:
            nature_connection = getattr(caster, 'nature_connection', 0)
            max_nature = getattr(caster, 'max_nature_connection', 12)  # 드루이드 자연 연결 최대 12
            required_nature = max(5, int(max_nature * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if nature_connection < required_nature:
                return False, f"드루이드 궁극기는 자연 연결이 {required_nature} 이상 필요합니다. (현재: {nature_connection}/{max_nature})"
    
    # 학자 계열 (난이도 완화)
    elif character_class == "철학자":
        if "진리의 깨달음" in skill_name or "현실 부정" in skill_name:
            wisdom_level = getattr(caster, 'wisdom_level', 0)
            max_wisdom = getattr(caster, 'max_wisdom_level', 20)  # 철학자 지혜 수준 최대 20
            required_wisdom = max(8, int(max_wisdom * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if wisdom_level < required_wisdom:
                return False, f"철학자 궁극기는 지혜 수준이 {required_wisdom} 이상 필요합니다. (현재: {wisdom_level}/{max_wisdom})"
    
    # 전투 계열 (난이도 완화)
    elif character_class == "검투사":
        if "검투장의 피날레" in skill_name or "콜로세움 소환" in skill_name:
            gladiator_fame = getattr(caster, 'gladiator_fame', 0)
            max_fame = getattr(caster, 'max_gladiator_fame', 10)  # 검투사 명성 최대 10
            required_fame = max(3, int(max_fame * 0.4))  # 최대치의 40% 이상 (이미 쉬움 → 더 완화)
            if gladiator_fame < required_fame:
                return False, f"검투사 궁극기는 검투사 명성이 {required_fame} 이상 필요합니다. (현재: {gladiator_fame}/{max_fame})"
                
    elif character_class == "기사":
        if "성스러운 돌격" in skill_name or "기사도 맹세" in skill_name:
            chivalry_honor = getattr(caster, 'chivalry_honor', 0)
            max_honor = getattr(caster, 'max_chivalry_honor', 12)  # 기사 기사도 명예 최대 12
            required_honor = max(5, int(max_honor * 0.5))  # 최대치의 50% 이상 (80%→50%)
            if chivalry_honor < required_honor:
                return False, f"기사 궁극기는 기사도 명예가 {required_honor} 이상 필요합니다. (현재: {chivalry_honor}/{max_honor})"
    
    # 신앙 계열 (난이도 완화)
    elif character_class == "신관":
        if "신의 심판" in skill_name or "천사 강림" in skill_name:
            divine_faith = getattr(caster, 'divine_faith', 0)
            max_faith = getattr(caster, 'max_divine_faith', 18)  # 신관 신앙심 최대 18
            required_faith = max(6, int(max_faith * 0.4))  # 최대치의 40% 이상 (80%→40%)
            if divine_faith < required_faith:
                return False, f"신관 궁극기는 신앙심이 {required_faith} 이상 필요합니다. (현재: {divine_faith}/{max_faith})"
    
    # 기타 직업들은 MP 조건만 체크 (기존 방식)
    else:
        required_mp = 25  # 기본 궁극기 MP 요구량 (25로 증가)
        if caster.current_mp < required_mp:
            return False, f"궁극기는 MP {required_mp} 이상 필요합니다. (현재: {caster.current_mp})"
    
    return True, "조건 충족"

def check_free_ultimate_usage(caster) -> bool:
    """전투당 1회 무료 궁극기 사용 체크"""
    if not hasattr(caster, 'free_ultimate_used'):
        caster.free_ultimate_used = False
    return not caster.free_ultimate_used

def use_free_ultimate(caster):
    """무료 궁극기 사용 표시"""
    caster.free_ultimate_used = True
    print(f"⭐ {caster.name}이(가) 조건을 충족하여 무료 궁극기를 사용합니다!")

def reset_free_ultimate(caster):
    """전투 시작 시 무료 궁극기 초기화"""
    caster.free_ultimate_used = False

def track_berserker_damage(character, damage_amount: int, is_self_damage: bool = False):
    """광전사 피해 추적 - 자체 피해와 외부 피해 모두 포함 (1~99999 범위)"""
    if (hasattr(character, 'character_class') and character.character_class == "광전사" and 
        damage_amount > 0):
        
        # recent_damage_taken 속성에 피해량 저장
        if not hasattr(character, 'recent_damage_taken'):
            character.recent_damage_taken = 0
        
        # 피해량을 1~99999 범위로 제한
        tracked_damage = max(1, min(99999, damage_amount))
        character.recent_damage_taken += tracked_damage
        
        damage_type = "자체 피해" if is_self_damage else "받은 피해"
        print(f"💢 {character.name}의 {damage_type}가 분노에 축적됩니다... ({tracked_damage} 피해)")
        
        return True
    return False

def _berserker_bonus(character) -> int:
    """광전사 특성: 잃은 HP 25%만큼 공격력 증가 (최대 순수공격력의 75%까지)"""
    if (hasattr(character, 'character_class') and character.character_class == "광전사"):
        max_hp = getattr(character, 'max_hp', 1000)
        current_hp = getattr(character, 'current_hp', max_hp)
        
        # 잃은 HP 비율 계산
        lost_hp_ratio = max(0, (max_hp - current_hp) / max_hp)
        
        # 기본 공격력 가져오기
        base_attack = getattr(character, 'physical_attack', getattr(character, 'attack', 100))
        
        # 잃은 HP 25%만큼 공격력 보너스 (최대 순수공격력의 75%까지)
        bonus_ratio = min(lost_hp_ratio * 0.25, 0.75)  # 최대 75% 보너스
        bonus_attack = int(base_attack * bonus_ratio)
        final_attack = base_attack + bonus_attack
        
        # 1~99999 범위로 제한
        final_attack = max(1, min(99999, final_attack))
        
        if bonus_attack > 0:
            print(f"💀 {character.name}의 광전사 분노: 잃은 HP {lost_hp_ratio*100:.1f}% → 공격력 +{bonus_attack} (최대 {base_attack*0.75:.0f})")
        
        return final_attack
    
    return getattr(character, 'physical_attack', getattr(character, 'attack', 100))

class StatusEffect:
    """상태 효과 클래스"""
    def __init__(self, name: str, type_: str, duration: int = 1, power: int = 0):
        self.name = name
        self.type = type_
        self.duration = duration
        self.power = power
        
    def apply(self, target):
        """상태 효과 적용"""
        if hasattr(target, 'status_manager') and target.status_manager:
            target.status_manager.apply_status(self.type, self.duration, self.power)
        elif hasattr(target, 'apply_status_effect'):
            target.apply_status_effect(self.type, self.duration, self.power)
    
    def __str__(self):
        return f"{self.name}({self.duration}턴)"

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
    BOOST_ALL_STATS = "모든능력치증가"  # 추가
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

# ========================================
# 🛡️ 안전한 스탯 접근 유틸리티 함수들
# ========================================

def safe_get_attack_stat(character, stat_name='physical_attack', default=100):
    """안전하게 공격 스탯을 가져오는 함수"""
    value = getattr(character, stat_name, None)
    if value is None:
        return default
    return value

def safe_get_hp_stat(character, stat_name='max_hp', default=1000):
    """안전하게 HP 스탯을 가져오는 함수"""
    value = getattr(character, stat_name, None)
    if value is None:
        return default
    return value

def safe_get_brv_stat(character, stat_name='brave_points', default=500):
    """안전하게 BRV 스탯을 가져오는 함수"""
    value = getattr(character, stat_name, None)
    if value is None:
        return default
    return value
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
                 "description": "[BRV:100] [6단계 적응형] [물리] - 현재 자세(공격/방어/균형/광전사/수호자/신속)에 따라 효과가 변하는 기본 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "sfx": "017.wav",
                 "special_effects": ["adaptive_attack"],
                 "organic_effects": {"적응력": 0.4, "균형감각": 0.3, "전투_본능": 0.2}},
                
                # HP 기본공격
                {"name": "파괴의 일격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 120, "accuracy": 85,
                 "description": "[HP:120] [방어구파괴] - 강력한 일격으로 적의 방어구 내구도를 대폭 감소시킵니다.",
                 "damage_type": DamageType.PHYSICAL, "sfx": "026.wav",
                 "special_effects": ["armor_break"],
                 "organic_effects": {"불굴의_의지": 0.5, "전투_본능": 0.4, "파괴력": 0.3}},
                
                # 6단계 완전체 전술 분석 - 상황에 따라 6가지 자세 변경
                {"name": "전술 분석", "type": SkillType.SUPPORT, "target": TargetType.SELF,
                 "mp_cost": 5, "sfx": "012.wav",
                 "description": "[6단계 자세변경] [분석] - 적과 아군 상태를 분석하여 6가지 전투 자세 중 최적의 자세로 변경합니다. (공격/방어/균형/광전사/수호자/신속)",
                 "special_effects": ["stance_adaptation", "enemy_analysis"],
                 "organic_effects": {"적응력": 0.5, "전술_이해": 0.4, "균형감각": 0.3}},
                
                # 개별 자세 변경 스킬들 추가
                {"name": "자세: 균형", "type": SkillType.SUPPORT, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "082.wav",
                 "description": "[자세변경] [균형] - 균형 자세로 변경하여 안정적인 전투를 준비합니다.",
                 "special_effects": ["stance_balanced"],
                 "organic_effects": {"균형감각": 0.4, "적응력": 0.3}},
                
                {"name": "방패 강타", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 115, "accuracy": 90,
                 "description": "[BRV:115] [기절:40%/2턴] [방어형 특화] - 방패로 적을 강타하여 기절시킵니다. 방어형일 때 위력 증가.",
                 "damage_type": DamageType.PHYSICAL, "sfx": "017.wav",
                 "status_effects": [{"type": StatusType.STUN, "duration": 2, "intensity": 0.4}],
                 "special_effects": ["defensive_bonus"],
                 "organic_effects": {"불굴의_의지": 0.4, "적응력": 0.3, "전술_이해": 0.2}},
                
                {"name": "연속 베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 85, "accuracy": 85,
                 "description": "[BRV:85×2] [공격형 특화] [연속공격] - 2번 연속 공격. 공격형일 때 크리티컬 확률 증가.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["double_attack", "aggressive_bonus"],
                 "sfx": "017.wav", "organic_effects": {"전투_본능": 0.4, "적응력": 0.3, "균형감각": 0.2}},
                
                {"name": "수호의 맹세", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "sfx": "093.wav",
                 "description": "[파티보호] [수호자 특화] - 수호자 모드에서 파티 전체를 보호합니다.",
                 "status_effects": [{"type": StatusType.GUARDIAN, "duration": 4, "intensity": 1.2}],
                 "special_effects": ["guardian_bonus"],
                 "organic_effects": {"불굴의_의지": 0.4, "리더십": 0.3, "적응력": 0.2}},
                
                {"name": "전투 각성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 7, "sfx": "082.wav",
                 "description": "[전능력+15%/5턴] [균형형 특화] - 전투의 흐름을 읽어 모든 능력치를 균형있게 향상시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_ALL_STATS, "duration": 5, "intensity": 1.15}],
                 "special_effects": ["balanced_bonus"],
                 "organic_effects": {"적응력": 0.5, "균형감각": 0.4, "전술_이해": 0.3}},
                
                {"name": "적응의 궁극기", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 15, "hp_power": 130, "cast_time": 25, "cooldown": 6,
                 "description": "[궁극] [HP:130] [6단계 적응형] [물리] - 현재 자세(공격/방어/균형/광전사/수호자/신속)에 따라 다른 효과의 궁극기를 발동합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["adaptive_ultimate"],
                 "sfx": "026.wav", "organic_effects": {"불굴의_의지": 0.5, "적응력": 0.4, "전투_본능": 0.3}}
            ],
            
            "검성": [
                # === 기본 공격 ===
                {"name": "기본베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 90, "accuracy": 95,
                 "description": "[BRV:90] [기본공격] [검기축적] - 검성의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["basic_sword_aura"],
                 "sfx": "017.wav", "organic_effects": {"검술_대가": 0.2, "집중력": 0.1}},
                
                {"name": "기본찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 110, "accuracy": 90,
                 "description": "[HP:110] [기본공격] [검기폭발] - 검성의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["basic_sword_burst"],
                 "sfx": "017.wav", "organic_effects": {"검술_대가": 0.25, "집중력": 0.15}},
                
                # ⚔️ 검성 - 검기 스택 시스템 (최대 2스택)
                {"name": "검기 베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 115, "accuracy": 95, "crit_rate": 12,
                 "description": "[BRV:115] [검기스택+1] [물리] - 기본 BRV 공격으로 검기 스택을 쌓습니다. 검성의 기본 기술입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_aura_gain"],
                 "sfx": "017.wav", "organic_effects": {"검술_대가": 0.4, "집중력": 0.3, "무술_수행": 0.3}},
                
                {"name": "일섬", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "hp_power": 135, "accuracy": 98, "crit_rate": 25, "cast_time": 8,
                 "description": "[HP:135] [검기스택소모] [ATB환급20-60%] [크리+25%] - 검기 스택을 소모하여 강력한 일격을 가합니다. 스택에 따라 ATB 게이지를 환급받습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_aura_consume", "atb_refund"],
                 "sfx": "026.wav", "organic_effects": {"검술_대가": 0.5, "집중력": 0.4, "무술_수행": 0.3}},
                
                {"name": "검기 파동", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "brv_power": 95, "accuracy": 90, "cast_time": 12,
                 "description": "[BRV:95] [전체] [검기스택1소모] [관통] - 검기 스택 1개를 소모하여 모든 적에게 관통 공격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_aura_wave", "piercing"],
                 "sfx": "012.wav", "organic_effects": {"검술_대가": 0.4, "집중력": 0.35, "무술_수행": 0.25}},
                
                {"name": "검심 집중", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "082.wav",
                 "description": "[집중+25%/5턴] [검기스택+1] [자신] - 마음을 가다듬어 집중력을 높이고 검기를 축적합니다.",
                 "status_effects": [{"type": StatusType.FOCUS, "duration": 5, "intensity": 1.25}],
                 "special_effects": ["sword_aura_gain"],
                 "organic_effects": {"검술_대가": 0.35, "집중력": 0.45, "무술_수행": 0.2}},
                
                {"name": "검압 강타", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "brv_power": 125, "hp_power": 145, "cast_time": 15,
                 "description": "[BRV:125+HP:145] [검기스택1소모] [ATB환급30%] - 검기를 방출하여 BRV와 HP를 동시에 공격합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["sword_aura_consume", "atb_refund_medium"],
                 "sfx": "026.wav", "organic_effects": {"검술_대가": 0.45, "집중력": 0.3, "무술_수행": 0.25}},
                
                {"name": "무한검", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 18, "hp_power": 180, "cooldown": 6, "cast_time": 25, "crit_rate": 35,
                 "description": "[궁극] [HP:180] [모든검기스택소모] [다연타] [크리+35%] - 모든 검기 스택을 소모하여 무한의 검기로 적을 베어냅니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["infinite_blade", "sword_aura_consume_all"],
                 "sfx": "026.wav", 
                 "organic_effects": {"검술_대가": 0.6, "집중력": 0.4, "무술_수행": 0.35, "전투_본능": 0.3}}
            ],
            
            "검투사": [
                # === 기본 공격 ===
                {"name": "투기장타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 88, "accuracy": 92,
                 "description": "[BRV:88] [기본공격] [투기장경험] - 검투사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["arena_experience"],
                 "sfx": "017.wav", "organic_effects": {"전투_본능": 0.2, "생존_기술": 0.1}},
                
                {"name": "승부찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 108, "accuracy": 90,
                 "description": "[HP:108] [기본공격] [승부결정] - 검투사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["decisive_strike"],
                 "sfx": "017.wav", "organic_effects": {"전투_본능": 0.25, "무술_수행": 0.15}},
                
                # 🛡 검투사 - 처치 스택 시스템 + 패링 시스템
                {"name": "투기장 기술", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 110, "accuracy": 92,
                 "description": "[BRV:110] [격투] [처치시능력치상승] - 투기장에서 단련한 격투 기술로 적을 공격합니다. 적 처치 시 능력치가 영구 상승합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["gladiator_skill"],
                 "sfx": "017.wav", "organic_effects": {"전투_본능": 0.4, "생존_기술": 0.3, "무술_수행": 0.3}},
                
                {"name": "패링", "type": SkillType.COUNTER, "target": TargetType.SELF,
                 "mp_cost": 5, "cast_time": 8, "sfx": "012.wav",
                 "description": "[반격태세] [패링] [처치효과획득] - 다음 공격을 반격으로 전환합니다. 성공 시 즉시 반격하고 처치 효과를 1회 획득합니다.",
                 "status_effects": [{"type": StatusType.COUNTER, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["parry_stance"],
                 "organic_effects": {"전투_본능": 0.35, "생존_기술": 0.4, "반응속도": 0.25}},
                
                {"name": "명예의 일격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 140, "cast_time": 12, "crit_rate": 15,
                 "description": "[HP:140] [처치스택비례강화] [크리+15%] - 처치 스택에 따라 위력이 증가하는 명예로운 일격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["honor_strike"],
                 "sfx": "026.wav", "organic_effects": {"전투_본능": 0.4, "무술_수행": 0.35, "의지력": 0.25}},
                
                {"name": "투사의 함성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "012.wav",
                 "description": "[공격+20%/4턴] [MP회복] [HP회복] - 관중들의 환호에 힘입어 능력치를 회복합니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2}],
                 "special_effects": ["warrior_roar"],
                 "organic_effects": {"전투_본능": 0.35, "생존_기술": 0.3, "지휘력": 0.25}},
                
                {"name": "생존자의 투혼", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "brv_power": 115, "hp_power": 125, "cast_time": 15,
                 "description": "[BRV:115+HP:125] [생존강화] [처치시회복] - 생존 의지를 담은 강력한 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["survival_spirit"],
                 "sfx": "026.wav", "organic_effects": {"전투_본능": 0.45, "생존_기술": 0.35, "의지력": 0.2}},
                
                {"name": "콜로세움의 왕", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 165, "cooldown": 6, "cast_time": 28,
                 "description": "[궁극] [HP:165] [전체] [모든스택소모] [압도적공격] - 모든 처치 스택을 소모하여 압도적인 힘을 발휘합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["colosseum_king"],
                 "sfx": "026.wav", 
                 "organic_effects": {"전투_본능": 0.5, "생존_기술": 0.4, "무술_수행": 0.35, "지휘력": 0.3}}
            ],
            
            "광전사": [
                # === 기본 공격 ===
                {"name": "원시의 분노", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 95, "accuracy": 90,
                 "description": "[BRV:95] [기본공격] [분노축적] - 원시적 본능을 깨워 분노를 축적하는 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["rage_build"],
                 "sfx": "017.wav", "organic_effects": {"전투_본능": 0.2, "광기_제어": 0.1}},
                
                {"name": "흡혈 일격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 115, "accuracy": 85,
                 "description": "[HP:115] [기본공격] [소량흡혈] - 적의 생명력을 흡수하는 잔혹한 일격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["basic_vampiric"],
                 "sfx": "017.wav", "organic_effects": {"전투_본능": 0.25, "생존_기술": 0.15}},
                
                # 💢 광전사 - HP 소모 + 보호막 + 흡혈 시스템
                {"name": "분노의 폭발", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 2, "brv_power": 125, "accuracy": 85, "hp_sacrifice": 15,
                 "description": "[BRV:125] [HP소모:15] [위력증가] [흡혈] - HP를 소모하여 강력한 공격을 가합니다. 소모한 HP에 따라 위력이 증가하고 흡혈 효과가 있습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["berserk_strike", "vampire_attack"],
                 "sfx": "017.wav", "organic_effects": {"전투_본능": 0.45, "광기_제어": 0.3, "생존_기술": 0.25}},
                
                {"name": "피의 방패", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "012.wav",
                 "description": "[현재HP50%소모] [소모량150%보호막생성] [소모량20%만큼최대HP증가] [5턴지속] - 현재 HP의 50%를 소모하여 더 강력한 보호막을 생성하고, 소모한 HP의 20%만큼 최대 HP가 증가합니다.",
                 "special_effects": ["blood_shield", "blood_max_hp_boost"],
                 "organic_effects": {"전투_본능": 0.35, "광기_제어": 0.4, "생존_기술": 0.25}},
                
                {"name": "흡혈 강타", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "hp_power": 140, "cast_time": 12, "drain_hp": True,
                 "description": "[HP:140] [보호막소모] [광역피해] [흡혈회복] - 보호막을 소모하여 강력한 공격을 가하고 흡혈로 회복합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["vampiric_blast", "shield_consume"],
                 "sfx": "026.wav", "organic_effects": {"전투_본능": 0.4, "광기_제어": 0.3, "생존_기술": 0.3}},
                
                {"name": "광기 증폭", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "hp_sacrifice": 20, "sfx": "012.wav",
                 "description": "[HP소모:20] [공격+30%/5턴] [흡혈량증가] - HP를 소모하여 광기를 증폭시키고 흡혈 효과를 강화합니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.3}],
                 "special_effects": ["madness_amplify"],
                 "organic_effects": {"전투_본능": 0.4, "광기_제어": 0.35, "의지력": 0.25}},
                
                {"name": "분노의 연쇄", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "brv_power": 95, "hp_power": 115, "hp_sacrifice_percent": 15, "cast_time": 18,
                 "description": "[BRV:95+HP:115] [전체] [HP소모15%] [광역흡혈] - 현재 HP의 일부를 소모하여 모든 적을 공격하고 광역 흡혈을 합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["rage_chain", "area_vampire"],
                 "sfx": "026.wav", "organic_effects": {"전투_본능": 0.45, "광기_제어": 0.3, "생존_기술": 0.25}},
                
                {"name": "최후의 광기", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 200, "cooldown": 5, "cast_time": 20, "hp_sacrifice": 1,
                 "description": "[궁극] [HP:200] [HP를1로만듦] [엄청난흡혈] [전체] - HP를 1로 만들고 그만큼 엄청난 피해와 흡혈 효과를 가집니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["final_madness", "massive_vampire"],
                 "sfx": "026.wav", 
                 "organic_effects": {"전투_본능": 0.6, "광기_제어": 0.4, "생존_기술": 0.35, "의지력": 0.3}}
            ],
            
            # === 기사 계열 ===
            "기사": [
                # === 기본 공격 ===
                {"name": "창찌르기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 85, "accuracy": 90,
                 "description": "[BRV:85] [기본공격] [기사도정신] - 기사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["knight_honor"],
                 "sfx": "017.wav", "organic_effects": {"기사도_정신": 0.2, "무술_수행": 0.1}},
                
                {"name": "수호타격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 105, "accuracy": 85,
                 "description": "[HP:105] [기본공격] [수호의지] - 기사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["guardian_will"],
                 "sfx": "017.wav", "organic_effects": {"기사도_정신": 0.25, "방어_술수": 0.15}},
                
                # 🛡 기사 - 의무 스택 시스템 (최대 5스택)
                {"name": "창 돌격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 115, "accuracy": 90,
                 "description": "[BRV:115] [돌격] [의무스택생성] - 창을 들고 돌격하여 적을 공격하고 의무 스택을 생성할 수 있습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["spear_charge"],
                 "sfx": "017.wav", "organic_effects": {"기사도_정신": 0.4, "무술_수행": 0.3, "전술_지식": 0.3}},
                
                {"name": "수호의 맹세", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "012.wav",
                 "description": "[아군대신피해] [의무스택획득] [패시브] - 아군 대신 피해를 받으며 의무 스택을 획득하는 수호자의 맹세입니다.",
                 "special_effects": ["protection_oath"],
                 "organic_effects": {"기사도_정신": 0.45, "방어_술수": 0.35, "의지력": 0.2}},
                
                {"name": "기사도", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "sfx": "012.wav",
                 "description": "[5스택시방어+35%] [스택수비례강화] - 의무 스택에 따라 방어력과 마법방어력이 증가합니다.",
                 "special_effects": ["chivalry_spirit"],
                 "organic_effects": {"기사도_정신": 0.4, "방어_술수": 0.35, "지휘력": 0.25}},
                
                {"name": "의무의 반격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 135, "cast_time": 10,
                 "description": "[HP:135] [스택소모] [반격] - 의무 스택을 소모하여 강력한 반격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["duty_counter"],
                 "sfx": "026.wav", "organic_effects": {"기사도_정신": 0.4, "무술_수행": 0.35, "전술_지식": 0.25}},
                
                {"name": "생존의 의지", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 8, "sfx": "012.wav",
                 "description": "[3스택이상시] [모든스택소모] [죽음무시] [1HP생존+20%회복] - 3스택 이상일 때 모든 스택을 소모하여 죽는 피해를 무시하고 생존합니다.",
                 "special_effects": ["survival_will"],
                 "organic_effects": {"기사도_정신": 0.4, "생존_기술": 0.35, "의지력": 0.25}},
                
                {"name": "성스러운 돌격", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 15, "hp_power": 155, "cooldown": 6, "cast_time": 25, "element": ElementType.LIGHT,
                 "description": "[궁극] [HP:155] [전체] [성속성] [모든스택소모] - 모든 의무 스택을 소모하여 성스러운 최후 일격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["holy_charge"],
                 "sfx": "026.wav", 
                 "organic_effects": {"기사도_정신": 0.5, "신성_마법": 0.4, "무술_수행": 0.35, "지휘력": 0.3}}
            ],
            
            "성기사": [
                # === 기본 공격 ===
                {"name": "성스러운베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 92, "accuracy": 95,
                 "description": "[BRV:92] [기본공격] [성스러운힘] - 성기사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["holy_blessing"],
                 "sfx": "017.wav", "organic_effects": {"신성_마법": 0.2, "수호_의지": 0.1}},
                
                {"name": "신성찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 112, "accuracy": 90,
                 "description": "[HP:112] [기본공격] [정화효과] - 성기사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["purify_touch"],
                 "sfx": "017.wav", "organic_effects": {"신성_마법": 0.25, "수호_의지": 0.15}},
                
                # ✨ 성기사 - 성역 시스템 (버프 기반 수호자)
                {"name": "성스러운 타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 110, "accuracy": 95, "element": ElementType.LIGHT,
                 "description": "[BRV:110] [성속성] [성역생성] - 성스러운 힘이 깃든 공격으로 성역을 생성할 수 있습니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["holy_strike_sanctuary"],
                 "sfx": "017.wav", "organic_effects": {"신성_마법": 0.4, "수호_의지": 0.3, "전투_본능": 0.3}},
                
                {"name": "축복", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 4, "sfx": "093.wav",
                 "description": "[아군버프] [성역트리거] [축복] - 아군에게 축복을 내려 성역 생성 조건을 만듭니다.",
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 5, "intensity": 1.2}],
                 "special_effects": ["blessing_sanctuary"],
                 "organic_effects": {"신성_마법": 0.4, "수호_의지": 0.35, "지휘력": 0.25}},
                
                {"name": "심판의 빛", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 140, "cast_time": 12, "element": ElementType.LIGHT,
                 "description": "[HP:140] [성역수비례강화] [성속성] - 성역 수에 따라 위력이 증가하는 심판의 빛입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["judgment_light"],
                 "sfx": "026.wav", "organic_effects": {"신성_마법": 0.45, "수호_의지": 0.3, "전투_본능": 0.25}},
                
                {"name": "성역 확장", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "sfx": "012.wav",
                 "description": "[성역+2] [전체강화] - 성역을 확장하여 아군 전체를 강화합니다.",
                 "special_effects": ["sanctuary_expand"],
                 "organic_effects": {"신성_마법": 0.4, "수호_의지": 0.35, "지휘력": 0.25}},
                
                {"name": "신성한 보호", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 2.5, "cast_time": 15,
                 "description": "[전체회복] [성역강화] - 성역의 힘으로 아군 전체를 치유하고 보호합니다.",
                 "special_effects": ["divine_protection"],
                 "sfx": "006.wav", "organic_effects": {"신성_마법": 0.4, "수호_의지": 0.35, "치유술": 0.25}},
                
                {"name": "천사 강림", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 170, "cooldown": 6, "cast_time": 30, "element": ElementType.LIGHT,
                 "description": "[궁극] [HP:170] [전체] [최대성역] - 모든 성역의 힘을 모아 천사를 강림시킵니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["angel_descent"],
                 "sfx": "026.wav", 
                 "organic_effects": {"신성_마법": 0.6, "수호_의지": 0.4, "지휘력": 0.35, "치유술": 0.3}}
            ],
            
            "암흑기사": [
                # === 기본 공격 ===
                {"name": "어둠베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 90, "accuracy": 92,
                 "description": "[BRV:90] [기본공격] [어둠의힘] - 암흑기사의 기본 BRV 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["darkness_power"],
                 "sfx": "017.wav", "organic_effects": {"어둠_마법": 0.2, "생명_흡수": 0.1}},
                
                {"name": "흡혈찌르기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 110, "accuracy": 90,
                 "description": "[HP:110] [기본공격] [소량흡혈] - 암흑기사의 기본 HP 공격입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["minor_vampiric"],
                 "sfx": "017.wav", "organic_effects": {"어둠_마법": 0.15, "생명_흡수": 0.25}},
                
                # 🌑 암흑기사 - 어둠의 오라 + 회복 스택 시스템
                {"name": "흡혈 베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 115, "accuracy": 92,
                 "description": "[BRV:115] [흡수스택생성] [지속피해] - 피해 흡수 스택을 생성하며 모든 적에게 지속 피해를 입힙니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["vampire_slash", "dark_aura"],
                 "sfx": "017.wav", "organic_effects": {"어둠_마법": 0.4, "생명_흡수": 0.35, "전투_본능": 0.25}},
                
                {"name": "어둠의 오라", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "012.wav",
                 "description": "[존재자체로지속피해] [피해흡수] [패시브] - 존재만으로 모든 적에게 지속 피해를 주고 피해를 흡수합니다.",
                 "special_effects": ["dark_aura_passive"],
                 "organic_effects": {"어둠_마법": 0.45, "생명_흡수": 0.35, "마력_제어": 0.2}},
                
                {"name": "흡혈 강타", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 135, "cast_time": 10,
                 "description": "[HP:135] [흡수스택소모] [회복] - 흡수 스택을 소모하여 강력한 공격과 함께 체력을 회복합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["vampiric_strike"],
                 "sfx": "026.wav", "organic_effects": {"어둠_마법": 0.4, "생명_흡수": 0.4, "전투_본능": 0.2}},
                
                {"name": "생명력 흡수", "type": SkillType.SPECIAL, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "cast_time": 15,
                 "description": "[전체흡수] [스택축적] [회복75%제한] - 모든 적에게서 생명력을 흡수하여 회복 스택을 최대 HP의 75%까지 축적합니다.",
                 "special_effects": ["life_drain_all"],
                 "sfx": "012.wav", "organic_effects": {"어둠_마법": 0.4, "생명_흡수": 0.4, "마력_제어": 0.2}},
                
                {"name": "어둠의 권능", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "brv_power": 100, "hp_power": 120, "cast_time": 18,
                 "description": "[BRV:100+HP:120] [전체] [어둠강화] - 어둠의 힘으로 모든 적을 공격하며 흡수 능력을 강화합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["dark_dominion"],
                 "sfx": "026.wav", "organic_effects": {"어둠_마법": 0.45, "생명_흡수": 0.3, "마력_제어": 0.25}},
                
                {"name": "어둠의 지배자", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 160, "cooldown": 6, "cast_time": 25,
                 "description": "[궁극] [HP:160] [모든스택폭발] [광역고정피해+보호막] - 모든 흡수 스택을 폭발시켜 광역 고정 피해와 보호막을 생성합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["dark_lord"],
                 "sfx": "026.wav", 
                 "organic_effects": {"어둠_마법": 0.6, "생명_흡수": 0.4, "마력_제어": 0.35, "지배력": 0.3}}
            ],

            "용기사": [
                # === 도약의 사냥꾼 - 표식 시스템 ===
                # 기본공격
                {"name": "용의표식", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 95, "accuracy": 90,
                 "description": "[BRV:95] [용의표식] - 기본 BRV 공격으로 적에게 용의 표식을 부여합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["dragon_mark"],
                 "sfx": "017.wav", "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.3, "표식_숙련": 0.25}},
                
                # HP 기본공격  
                {"name": "도약공격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 120, "accuracy": 85,
                 "description": "[HP:120] [도약] [지연공격] [크리티컬확정] - 도약하여 지연 공격을 가하고 표식을 부여합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["leap_attack"],
                 "sfx": "026.wav", "organic_effects": {"용족_혈통": 0.4, "전투_본능": 0.3, "기동력": 0.25}},
                
                {"name": "용린보호", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3,
                 "description": "[방어력+30%] [표식가속] - 용린으로 자신을 보호하고 표식 축적 속도를 가속화합니다.",
                 "sfx": "093.wav",
                 "status_effects": [{"type": StatusType.BOOST_DEF, "duration": 5, "intensity": 1.3}],
                 "special_effects": ["dragon_scale"],
                 "organic_effects": {"용족_혈통": 0.4, "방어_기술": 0.3, "표식_숙련": 0.25}},
                
                {"name": "표식폭발", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 110, "accuracy": 95,
                 "description": "[BRV:110+표식보너스] [표식기반] - 축적된 표식을 이용해 강화된 BRV 공격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["dragon_mark"],
                 "sfx": "019.wav", "organic_effects": {"용족_혈통": 0.4, "표식_숙련": 0.35, "전투_본능": 0.25}},
                
                {"name": "용의숨결", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 140, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:140+표식보너스40%] [크리티컬확정] - 표식 수에 따라 위력이 강화되는 용의 숨결 공격입니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.FIRE,
                 "special_effects": ["dragon_breath"],
                 "sfx": "008.wav", "organic_effects": {"용족_혈통": 0.45, "화염_친화": 0.3, "표식_숙련": 0.3}},
                
                {"name": "용의위엄", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6,
                 "description": "[위압] [모든표식폭발] - 용의 위엄으로 모든 적의 표식을 폭발시키고 위압합니다.",
                 "special_effects": ["dragon_majesty"],
                 "sfx": "026.wav", "organic_effects": {"용족_혈통": 0.45, "위압감": 0.3, "표식_숙련": 0.3}},
                
                {"name": "드래곤로드", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 16, "hp_power": 180, "cooldown": 6, "cast_time": 25,
                 "description": "[궁극] [HP:180+표식강화60%] [일정시간무적] - 모든 표식을 초강화 융합하는 궁극기입니다.",
                 "damage_type": DamageType.HYBRID, "element": ElementType.FIRE,
                 "special_effects": ["dragon_lord_ultimate"],
                 "sfx": "026.wav", "organic_effects": {"용족_혈통": 0.6, "표식_숙련": 0.45, "화염_친화": 0.4, "전투_본능": 0.35}},
                
                # 추가 스킬 - 용기사 6번째 스킬
                {"name": "용족의힘", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 10,
                 "description": "[공격력+50%] [용족각성] - 용족의 피가 각성하여 공격력이 크게 증가하고 표식 효과가 강화됩니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.5}],
                 "special_effects": ["dragon_awakening"],
                 "sfx": "082.wav", "organic_effects": {"용족_혈통": 0.6, "전투_본능": 0.4, "표식_숙련": 0.3}}
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
                 "sfx": "010.wav", "organic_effects": {"원소_친화": 0.4, "마나_순환": 0.3, "집중력": 0.25}},
                
                # HP 기본공격 - 화염
                {"name": "파이어볼", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 115, "accuracy": 85,
                 "description": "[HP:115] [화염카운트+1] - 기본 화염 공격으로 화염 속성 카운트를 증가시킵니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.FIRE,
                 "special_effects": ["fire_count"],
                 "sfx": "008.wav", "organic_effects": {"원소_친화": 0.4, "마나_순환": 0.3, "화염_친화": 0.25}},
                
                {"name": "아이스샤드", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 105, "accuracy": 90,
                 "description": "[BRV:105] [냉기카운트+1] - 냉기 공격으로 적을 얼리고 냉기 속성 카운트를 증가시킵니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.ICE,
                 "special_effects": ["ice_count"],
                 "sfx": "023.wav", "organic_effects": {"원소_친화": 0.4, "마나_순환": 0.3, "냉기_친화": 0.25}},
                
                {"name": "원소강화", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4,
                 "description": "[마법공격력+20%] [원소친화도상승] - 원소 마법의 위력을 강화하고 친화도를 상승시킵니다.",
                 "sfx": "082.wav",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2}],
                 "special_effects": ["elemental_mastery"],
                 "organic_effects": {"원소_친화": 0.45, "마나_순환": 0.3, "집중력": 0.25}},
                
                {"name": "원소융합", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "hp_power": 125, "cast_time": 15, "accuracy": 85,
                 "description": "[HP:125] [복합원소] - 모든 원소를 융합한 복합 속성 공격으로 광역 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.NEUTRAL,
                 "special_effects": ["elemental_fusion"],
                 "sfx": "012.wav", "organic_effects": {"원소_친화": 0.5, "마나_순환": 0.35, "집중력": 0.3}},
                
                {"name": "원소순환", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 6,
                 "description": "[원소순환활성화] [3회동일원소시자동시전] - 원소 순환 시스템을 활성화합니다.",
                 "special_effects": ["elemental_cycle"],
                 "sfx": "012.wav", "organic_effects": {"원소_친화": 0.5, "마나_순환": 0.4, "집중력": 0.35}},
                
                {"name": "원소대폭발", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 160, "cooldown": 6, "cast_time": 25,
                 "description": "[궁극] [HP:160+원소보너스] [모든속성동시] - 축적된 모든 원소를 대폭발시키는 궁극기입니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.NEUTRAL,
                 "special_effects": ["all_elements_burst"],
                 "sfx": "307.wav", "organic_effects": {"원소_친화": 0.6, "마나_순환": 0.45, "집중력": 0.4, "폭발_제어": 0.35}},
                
                # 아크메이지 6번째 스킬 추가
                {"name": "마력폭풍", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "brv_power": 95, "accuracy": 88, "cast_time": 12,
                 "description": "[BRV:95] [전체공격] [마력방어력감소30%] - 강력한 마력의 폭풍으로 모든 적의 마법방어력을 크게 감소시킵니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.NEUTRAL,
                 "status_effects": [{"type": StatusType.BURN, "duration": 4, "intensity": 0.7}],
                 "special_effects": ["magic_storm"],
                 "sfx": "012.wav", "organic_effects": {"원소_친화": 0.5, "마나_순환": 0.4, "집중력": 0.35, "마력_제어": 0.3}}
            ],

            "정령술사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "정령소환", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 87, "accuracy": 93,
                 "description": "[BRV:87] [정령] [소환] - [BRV] 원소 정령을 소환하여 적을 공격하며 정령 친화도를 높입니다.",
                 "sfx": "012.wav",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["spirit_bond"],  # 기본 공격으로 정령 친화도 증가
                 "organic_effects": {"정령_친화": 0.3, "마법_지식": 0.25, "원소_조화": 0.2}},
                {"name": "원소융합", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 100, "accuracy": 88,
                 "description": "[HP:100] [원소] [융합] - [HP] 여러 원소를 융합하여 강력한 원소 공격을 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["elemental_fusion"],  # 기본 HP 공격으로 원소 융합
                 "sfx": "019.wav", "organic_effects": {"원소_조화": 0.35, "정령_친화": 0.25, "마법_지식": 0.2}},
                
                # 정령의 친구 - [정령][소환] 키워드 특화
                {"name": "정령교감", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "082.wav",
                 "description": "[원소강화+] [정령] [교감] - [BUFF] 정령과 교감하여 원소 마법의 위력을 크게 증가시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "자연_이해": 0.3}},
                {"name": "화염정령", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 98, "element": ElementType.FIRE, "accuracy": 95,
                 "description": "[BRV:100] [화속] [정령] - [BRV] 화염 정령을 소환하여 적을 공격하고 BRV를 획득합니다.",
                 "sfx": "009.wav",
                 "damage_type": DamageType.MAGICAL,
                 "status_effects": [{"type": StatusType.BURN, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "화염_친화": 0.3, "마법_지식": 0.3}},
                {"name": "물정령치유", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 2.7, "element": ElementType.WATER,
                 "description": "[치유:중] [수속] [정령] - [HEAL] 물 정령의 힘으로 아군의 상처를 치유하고 HP를 회복시킵니다.",
                 "sfx": "005.wav",
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "치유_기술": 0.3}},
                {"name": "바람정령축복", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "sfx": "093.wav",
                 "description": "[속도+] [회피+] [풍속] - [BUFF] 바람 정령의 축복으로 아군의 속도와 회피율을 증가시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.2}],
                 "organic_effects": {"정령_친화": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "대지정령분노", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "hp_power": 118, "element": ElementType.EARTH, "cast_time": 20,
                 "description": "[HP:125] [토속] [정령] - [HP] 대지정령의 분노로 적의 HP에 강력한 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["earth_rage"],
                 "sfx": "012.wav", "organic_effects": {
"정령_친화": 0.4, "마법_지식": 0.35, "자연_이해": 0.3}},
                {"name": "사대정령소환", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 20, "hp_power": 140, "cooldown": 8, "cast_time": 40,
                 "description": "[궁극] [4원소] [소환] - [궁극] 4대 정령을 모두 소환하여 압도적인 원소 공격을 펼치는 궁극기입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["four_elements"],
                 "sfx": "190.wav", "organic_effects": {
"정령_친화": 0.5, "마법_지식": 0.4, "자연_이해": 0.35, "집중력": 0.3}}
            ],
            
            
            "시간술사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "시간침", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 92, "accuracy": 95,
                 "description": "[BRV:92] [시간] [침] - [BRV] 시간의 힘을 담은 침으로 적을 찌르고 BRV를 획득합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["time_record_savepoint"],  # 기본 공격으로 시간 기록점 생성
                 "organic_effects": {"시간_조작": 0.3, "마법_지식": 0.2, "정밀함": 0.2}},
                {"name": "시간파동", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 105, "accuracy": 90,
                 "description": "[HP:105] [시간] [파동] - [HP] 시간의 파동으로 적의 HP에 직접적인 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["future_sight"],  # 기본 HP 공격으로 미래시 효과
                 "sfx": "012.wav", "organic_effects": {"시간_조작": 0.35, "마법_지식": 0.25, "정밀함": 0.2}},
                
                # 시간의 조작자 - [시간][조작] 키워드 특화
                {"name": "시간가속", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5,
                 "description": "[속도+50%] [시간] [가속] - [BUFF] 시간을 가속시켜 자신의 행동 속도를 크게 증가시킵니다.",
                 "sfx": "082.wav",
                 "status_effects": [{
"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.25}],
                 "organic_effects": {"시간_조작": 0.4, "마법_지식": 0.3, "집중력": 0.3}},
                {"name": "시간왜곡", "type": SkillType.SPECIAL, "target": TargetType.BATTLEFIELD,
                 "mp_cost": 2, "cooldown": 3, "sfx": "086.wav",
                 "description": "[시간조작] [특수] [왜곡] - [SPECIAL] 시간을 왜곡시켜 특별한 효과를 발동시킵니다.",
                 "status_effects": [{"type": StatusType.TIME_MARKED, "duration": 10, "intensity": 1.0}],
                 "special_effects": ["time_record_savepoint"],
                 "organic_effects": {"시간_조작": 0.45, "마법_지식": 0.35, "정밀함": 0.3}},
                {"name": "시간되돌리기", "type": SkillType.SPECIAL, "target": TargetType.ANY_SINGLE,
                 "mp_cost": 15, "cooldown": 6, "cast_time": 25,
                 "description": "[복원] [시간] [기적] - [SPECIAL] 시간을 되돌려 이전 상태로 복원하는 기적을 일으킵니다.",
                 "special_effects": ["time_rewind_to_savepoint"],
                 "sfx": "012.wav", "organic_effects": {
"시간_조작": 0.5, "마법_지식": 0.35, "정밀함": 0.25}},
                {"name": "미래예지", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 9, "cooldown": 4,
                 "description": "[회피+] [명중+] [예지] - [BUFF] 미래를 예지하여 회피율과 명중률을 크게 증가시킵니다.",
                 "sfx": "012.wav",
                 "status_effects": [{
"type": StatusType.FORESIGHT, "duration": 5, "intensity": 1.0}],
                 "special_effects": ["future_sight"],
                 "organic_effects": {"시간_조작": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "시간정지", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 12, "cooldown": 5, "cast_time": 25,
                 "description": "[전체정지] [시간] [필드] - [FIELD] 시간을 정지시켜 모든 적의 행동을 일시 중단시킵니다.",
                 "sfx": "086.wav",
                 "status_effects": [{
"type": StatusType.TIME_STOP, "duration": 2, "intensity": 1.0}],
                 "special_effects": ["time_stop"], "is_field_skill": True,
                 "organic_effects": {"시간_조작": 0.45, "마법_지식": 0.35, "집중력": 0.2}},
                {"name": "시공간붕괴", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "hp_power": 154, "cooldown": 9, "cast_time": 45,
                 "description": "[궁극] [시공파괴] [붕괴] - [궁극] 시공간을 붕괴시켜 모든 것을 파괴하는 궁극의 시간 마법입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["spacetime_collapse"],
                 "sfx": "307.wav", "organic_effects": {
"시간_조작": 0.5, "마법_지식": 0.4, "집중력": 0.35, "정밀함": 0.3}}
            ],
            
            "차원술사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "차원베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 88, "accuracy": 95,
                 "description": "[BRV:88] [차원] [베기] - [BRV] 차원의 칼날로 적을 베어 BRV를 획득하며 잔상을 생성합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["afterimage"],  # 기본 공격으로 잔상 생성
                 "organic_effects": {"차원_조작": 0.3, "회피_술법": 0.2, "민첩성": 0.2}},
                {"name": "공간찢기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 98, "accuracy": 90,
                 "description": "[HP:98] [공간] [찢기] - [HP] 공간을 찢어 적의 HP에 피해를 가하며 차원 방패를 생성합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["dimension_cloak"],  # 기본 HP 공격으로 차원 장막 효과
                 "sfx": "012.wav", "organic_effects": {"차원_조작": 0.35, "회피_술법": 0.25, "정밀함": 0.2}},
                
                # 회피의 달인 - [차원][회피] 키워드 특화
                {"name": "차원장막", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "054.wav",
                 "description": "[물리무효] [차원] [장막] - [BUFF] 차원의 장막으로 자신을 감싸 물리 공격을 회피합니다.",
                 "status_effects": [{"type": StatusType.ABSOLUTE_EVASION, "duration": 2, "intensity": 2.0}],
                 "special_effects": ["dimension_cloak"],
                 "organic_effects": {"차원_조작": 0.45, "회피_술법": 0.4, "집중력": 0.25}},
                {"name": "잔상분신", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5, "sfx": "054.wav",
                 "description": "[회피+30%] [분신] [잔상] - [BUFF] 잔상 분신을 만들어 회피율을 크게 증가시킵니다.",
                 "status_effects": [{"type": StatusType.EVASION_UP, "duration": 5, "intensity": 1.3}],
                 "special_effects": ["afterimage"],
                 "organic_effects": {"회피_술법": 0.4, "차원_조작": 0.35, "민첩성": 0.25}},
                {"name": "공간도약", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 98, "accuracy": 100,
                 "description": "[BRV:110] [순간이동] [공간] - [BRV] 공간을 도약하여 적의 뒤로 순간이동해 기습 공격을 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["space_leap"],
                 "sfx": "054.wav", "organic_effects": {
"차원_조작": 0.4, "회피_술법": 0.3, "전투_본능": 0.3}},
                {"name": "차원미로", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "sfx": "012.wav",
                 "description": "[혼란] [이동봉인] [차원] - [DEBUFF] 차원 미로에 적을 가둬 혼란과 이동 불가 상태를 부여합니다.",
                 "status_effects": [{"type": StatusType.REDUCE_ACCURACY, "duration": 4, "intensity": 0.5}],
                 "special_effects": ["dimension_maze"],
                 "organic_effects": {"차원_조작": 0.4, "회피_술법": 0.35, "지혜": 0.25}},
                {"name": "회피반격", "type": SkillType.COUNTER, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "hp_power": 118, "cooldown": 3,
                 "description": "[회피시반격] [카운터] [특수] - [COUNTER] 공격을 회피하면서 동시에 반격하는 특수 기술입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["evasion_counter"],
                 "sfx": "026.wav", "organic_effects": {
"회피_술법": 0.45, "차원_조작": 0.35, "전투_본능": 0.3}},
                {"name": "무적의경지", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 20, "cooldown": 8, "cast_time": 25,
                 "description": "[궁극] [무적] [초월] - [궁극] 모든 차원을 초월하여 무적 상태가 되는 궁극의 차원 술법입니다.",
                 "sfx": "035.wav",
                 "status_effects": [{"type": StatusType.ABSOLUTE_EVASION, "duration": 3, "intensity": 99.0}],
                 "special_effects": ["untouchable_state"],
                 "organic_effects": {"회피_술법": 0.6, "차원_조작": 0.5, "집중력": 0.4, "민첩성": 0.35}}
            ],
            
            "철학자": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "논리검증", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 82, "accuracy": 95,
                 "description": "[BRV:82] [논리] [검증] - [BRV] 논리적 검증으로 적의 허점을 찌르고 지혜를 쌓습니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["truth_insight"],  # 기본 공격으로 진리 통찰
                 "organic_effects": {"지혜": 0.3, "마법_지식": 0.2, "정밀함": 0.2}},
                {"name": "철학충격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 108, "accuracy": 90,
                 "description": "[HP:108] [철학] [충격] - [HP] 철학적 충격으로 적의 정신에 직접적인 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["philosophical_thought"],  # 기본 HP 공격으로 철학적 사고
                 "sfx": "012.wav", "organic_effects": {"지혜": 0.35, "마법_지식": 0.25, "집중력": 0.2}},
                
                # 진리의 탐구자 - [지혜][분석] 키워드 특화
                {"name": "진리탐구", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4,
                 "description": "[지혜+] [마력+] [탐구] - [BUFF] 진리를 탐구하여 지혜와 마법력을 크게 증가시킵니다.",
                 "sfx": "082.wav",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 6, "intensity": 1.15}],
                 "organic_effects": {"지혜": 0.4, "마법_지식": 0.3, "집중력": 0.3}},
                {"name": "진실간파", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "sfx": "012.wav",
                 "description": "[약점파악] [분석] [진실] - [SPECIAL] 진실을 간파하여 적의 약점과 상태를 파악합니다.",
                 "status_effects": [{"type": StatusType.VULNERABLE, "duration": 4, "intensity": 1.3}],
                 "special_effects": ["truth_insight"],
                 "organic_effects": {"지혜": 0.45, "마법_지식": 0.3, "정밀함": 0.25}},
                {"name": "지혜의빛", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "sfx": "012.wav",
                 "description": "[전체 지능+] [빛] [지혜] - [BUFF] 지혜의 빛으로 아군 전체의 지능과 마법력을 향상시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1}],
                 "organic_effects": {"지혜": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "존재부정", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 12, "hp_power": 140, "cast_time": 20,
                 "description": "[HP:120] [논리] [철학] - [HP] 철학적 논리로 적의 존재를 부정하여 HP 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["existence_denial"],
                 "sfx": "012.wav", "organic_effects": {
"지혜": 0.5, "마법_지식": 0.35, "집중력": 0.15}},
                {"name": "철학적사고", "type": SkillType.SPECIAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 10, "cooldown": 4,
                 "description": "[통찰] [특수] [사고] - [SPECIAL] 철학적 사고로 특별한 통찰력을 얻어 유리한 효과를 발동시킵니다.",
                 "special_effects": ["philosophical_thought"],
                 "sfx": "012.wav", "organic_effects": {
"지혜": 0.45, "마법_지식": 0.3, "지휘력": 0.25}},
                {"name": "절대진리", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 25, "hp_power": 161, "cooldown": 9, "cast_time": 50,
                 "description": "[궁극] [진리] [깨달음] - [궁극] 절대 진리를 깨달아 모든 것을 꿰뚫는 궁극의 지혜를 발휘합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["absolute_truth"],
                 "sfx": "012.wav", "organic_effects": {
"지혜": 0.5, "마법_지식": 0.4, "집중력": 0.35, "정밀함": 0.3}}
            ],
            
            # === 바람의 저격수 - 궁수 ===
            "궁수": [
                # 🌟 기본 공격 (mp_cost: 0) - 조준 포인트 시스템
                {"name": "조준사격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 91, "accuracy": 97,
                 "description": "[BRV:91] [조준] [사격] - [BRV] 정밀한 조준으로 포인트를 축적합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["precision_stack"],  # 조준 포인트 생성
                 "organic_effects": {"원거리_숙련": 0.3, "정밀_사격": 0.25, "전투_본능": 0.2}},
                {"name": "강화관통", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 108, "accuracy": 92,
                 "description": "[HP:108] [관통] [조준활용] - [HP] 조준 포인트를 활용한 강화된 관통 사격입니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["arrow_penetration"],  # 조준 포인트 활용
                 "sfx": "026.wav", "organic_effects": {"정밀_사격": 0.35, "원거리_숙련": 0.25, "전투_본능": 0.2}},
                # 바람의 유격수 - [연사][기동] 키워드 특화 → 조준 시스템
                {"name": "삼연사", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 98, "accuracy": 95, "hit_count": 3,
                 "description": "[BRV:98] [연속] [조준생성] - [BRV] 연속 사격으로 조준 포인트를 대량 생성합니다.",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.WIND,
                 "special_effects": ["triple_shot"],  # 조준 포인트 생성 포함
                 "sfx": "012.wav", "organic_effects": {
"유격_전술": 0.35, "바람_친화": 0.3, "정밀_사격": 0.25}},
                {"name": "정밀관통", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 
                 "mp_cost": 8, "hp_power": 98, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:115] [관통] [물리] - [HP] 관통력이 뛰어난 화살로 적의 HP에 직접 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["piercing_shot"],
                 "sfx": "045.wav", "organic_effects": {
"정밀_사격": 0.4, "유격_전술": 0.3, "집중력": 0.2}},
                {"name": "독화살", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 105, "accuracy": 95,
                 "description": "[BRV:90] [독] [물리] - [BRV] 독이 발린 화살로 적을 공격하여 BRV를 획득하고 중독시킵니다.",
                 "sfx": "062.wav",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "status_effects": [{
"type": StatusType.POISON, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정밀_사격": 0.35, "생존_본능": 0.3, "유격_전술": 0.25}},
                {"name": "폭발화살", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 112, "cast_time": 20, "accuracy": 85,
                 "description": "[HP:130] [폭발] [물리] - [HP] 폭발하는 화살로 적에게 강력한 HP 피해를 가합니다.",
                 "sfx": "014.wav",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.FIRE,
                 "status_effects": [{
"type": StatusType.BURN, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"유격_전술": 0.35, "정밀_사격": 0.3, "바람_친화": 0.25}},
                {"name": "지원사격", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 8, "sfx": "012.wav",
                 "description": "[조준소모] [지원] [사격] - [BUFF] 아군 행동 시 조준 포인트를 소모하여 자동 지원사격을 실시합니다.",
                 "special_effects": ["support_fire_activation"],
                 "organic_effects": {"정밀_사격": 0.4, "유격_전술": 0.3, "집중력": 0.25}},
                {"name": "헌터모드", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 16, "cooldown": 6,
                 "description": "[궁극] [사냥] [완벽조준] - [궁극] 완벽한 사냥꾼 모드로 진입하여 모든 사격 능력을 극대화하는 궁극기입니다.",
                 "special_effects": ["hunter_mode"],
                 "sfx": "012.wav", "organic_effects": {
"정밀_사격": 0.5, "유격_전술": 0.4, "바람_친화": 0.35, "생존_본능": 0.3}}
            ],

            "암살자": [
                # � 기본 공격 (mp_cost: 0)
                {"name": "그림자베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 94, "accuracy": 96, "crit_rate": 8,
                 "description": "[BRV:94] [그림자] [베기] - [BRV] 그림자의 힘으로 적을 베어 BRV를 획득하며 그림자를 생성합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["generate_shadow"],  # 기본 공격으로 그림자 생성
                 "shadow_count": 1,
                 "organic_effects": {"그림자_조작": 0.3, "암살_기술": 0.25, "은신_술법": 0.2}},
                {"name": "그림자처형", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 109, "accuracy": 90, "crit_rate": 15,
                 "description": "[HP:109] [그림자] [처형] - [HP] 그림자 스택에 비례한 치명적인 처형 공격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["shadow_execution"],  # 기본 HP 공격으로 그림자 소모
                 "sfx": "026.wav", "organic_effects": {"암살_기술": 0.35, "그림자_조작": 0.25, "정밀함": 0.2}},
                
                # �🌑 그림자의 암살자 - [그림자][암살] 특화 시스템
                # 그림자 메커니즘: 
                # - 기본공격/BRV공격 시 그림자 1개 생성 (최대 5개)
                # - 그림자 연막 등 특수 스킬은 그림자 2개 생성
                # - 기본공격/궁극기 외 스킬 사용 시 그림자 1개 소모하여 1.5배 피해
                # - 궁극기는 모든 그림자를 소모하여 그림자 수만큼 피해 증폭
                
                {"name": "그림자숨기", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2, "sfx": "012.wav",
                 "description": "[은신] [그림자+1] - 그림자에 숨어 은신하며 그림자를 1개 생성합니다.",
                 "status_effects": [{"type": StatusType.STEALTH, "duration": 2, "intensity": 1.0}],
                 "special_effects": ["generate_shadow"], "shadow_count": 1,
                 "organic_effects": {"은신_술법": 0.4, "그림자_조작": 0.4, "생존_본능": 0.2}},
                
                {"name": "그림자 강타", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 105, "crit_rate": 12, "accuracy": 95,  # brv_power: 115→105, crit_rate: 15→12로 너프
                 "description": "[BRV:95] [그림자+1] - 그림자와 함께 공격하여 BRV를 획득하고 그림자를 1개 생성합니다.",
                 "damage_type": DamageType.PHYSICAL, 
                 "special_effects": ["generate_shadow", "shadow_echo"], "shadow_count": 1,
                 "sfx": "017.wav", "organic_effects": {"그림자_조작": 0.4, "암살_기술": 0.3, "정밀함": 0.3}},
                
                {"name": "독바르기", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "012.wav", "can_consume_shadow": True,
                 "description": "[독부여] [그림자소모가능] - 무기에 독을 바릅니다. 그림자 1개를 소모하면 효과가 1.3배 강화됩니다.",  # 1.5배→1.3배로 너프
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15}],  # 1.1→1.15로 상향
                 "special_effects": ["poison_weapon"],
                 "organic_effects": {"독술_지식": 0.4, "그림자_조작": 0.3, "암살_기술": 0.3}},
                
                {"name": "그림자 연막", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "cooldown": 3, "can_consume_shadow": True,
                 "description": "[시야차단] [그림자+2] - 그림자 연막으로 시야를 차단하고 그림자 2개를 생성합니다. 그림자 소모로 강화 가능.",
                 "sfx": "012.wav", "shadow_count": 2,
                 "status_effects": [{"type": StatusType.BLIND, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["smoke_bomb", "generate_shadow"],
                 "organic_effects": {"은신_술법": 0.4, "그림자_조작": 0.4, "전술_지식": 0.2}},
                
                {"name": "그림자 암살", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 145, "cast_time": 12, "crit_rate": 25, "can_consume_shadow": True,
                 "description": "[HP:120] [암살] [그림자소모가능] - 은밀한 암살술로 HP 피해를 가합니다. 그림자로 강화 가능.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["assassination"],
                 "sfx": "026.wav", "organic_effects": {"암살_기술": 0.5, "그림자_조작": 0.3, "정밀함": 0.2}},
                
                {"name": "그림자 처형", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 15, "hp_power": 155, "cooldown": 7, "cast_time": 8,
                 "description": "[궁극] [그림자전체소모] - 모든 그림자를 소모하여 괴멸적인 일격을 가합니다. 그림자 1개당 +20% 피해.",
                 "damage_type": DamageType.PHYSICAL, 
                 "special_effects": ["shadow_execution", "consume_all_shadows"],
                 "sfx": "035.wav", "organic_effects": {"암살_기술": 0.6, "그림자_조작": 0.5, "정밀함": 0.4}}
            ],
            
            # === 맹독의 침묵자 - 도적 ===
            "도적": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "독침", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 90, "accuracy": 96,
                 "description": "[BRV:90] [독] [침] - [BRV] 독침으로 적을 찔러 BRV를 획득하며 독 스택을 쌓습니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "element": ElementType.POISON,
                 "status_effects": [{"type": StatusType.POISON, "duration": 4, "intensity": 1.0}],
                 "special_effects": ["poison_stack"],
                 "organic_effects": {"독술_지배": 0.3, "침묵_술": 0.25, "민첩성": 0.2}},
                {"name": "암살", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 106, "accuracy": 88,
                 "description": "[HP:106] [암살] [치명타] - [HP] 치명적인 암살 공격으로 독 스택에 비례한 추가 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["lethal_strike"],
                 "sfx": "026.wav", "organic_effects": {"침묵_술": 0.35, "독술_지배": 0.25, "민첩성": 0.2}},
                
                # 🧬 독술의 대가 - 6개 특화 스킬
                {"name": "부식독침", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 85, "accuracy": 95,
                 "description": "[BRV:85] [부식] [침묵] - [BRV] 강산성 독침으로 방어력을 부식시키고 침묵 효과를 부여합니다.",
                 "sfx": "062.wav",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.POISON,
                 "status_effects": [{"type": StatusType.POISON, "duration": 6, "intensity": 1.2},
                                   {"type": StatusType.REDUCE_DEF, "duration": 5, "intensity": 0.7},
                                   {"type": StatusType.SILENCE, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["poison_stack", "corrosive_poison"],
                 "organic_effects": {"독술_지배": 0.4, "침묵_술": 0.35, "독_촉진": 0.25}},
                {"name": "침묵암살", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 110, "cast_time": 10, "accuracy": 95,
                 "description": "[HP:110] [침묵] [독촉진] - [HP] 완전한 침묵 속에서 적을 암살하며 남은 독을 촉진시킵니다.",
                 "sfx": "026.wav",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["poison_trigger"],
                 "organic_effects": {"침묵_술": 0.4, "독_촉진": 0.35, "독술_지배": 0.25}},
                {"name": "독성안개", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "cast_time": 15, "cooldown": 4,
                 "description": "[독안개] [전체] [지속] - [FIELD] 독성 안개를 퍼뜨려 모든 적을 서서히 말려죽이고 역병을 확산시킵니다.",
                 "sfx": "012.wav",
                 "is_field_skill": True, "special_effects": ["poison_fog_enhanced", "plague_spread"],
                 "status_effects": [{"type": StatusType.POISON, "duration": 8, "intensity": 1.8}],
                 "organic_effects": {"독술_지배": 0.45, "독_촉진": 0.35, "침묵_술": 0.25}},
                {"name": "베놈폭발", "type": SkillType.BRV_HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 12, "brv_power": 95, "hp_power": 85, "cast_time": 15, "cooldown": 3,
                 "description": "[BRV+HP] [폭발] [독성칵테일] - [BRV+HP] 독성 칵테일을 터뜨려 누적된 독 피해를 폭발시킵니다.",
                 "damage_type": DamageType.MAGICAL, "element": ElementType.POISON,
                 "special_effects": ["venom_explosion", "toxic_cocktail"],
                 "sfx": "010.wav", 
                 "organic_effects": {"독_촉진": 0.5, "독술_지배": 0.35, "침묵_술": 0.25}},
                {"name": "독성필드", "type": SkillType.FIELD, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 15, "cast_time": 20, "cooldown": 6,
                 "description": "[독필드] [전체] [지속] - [FIELD] 전장에 독성 지대를 생성하여 지속적으로 적들을 독에 중독시키고 폭발시킵니다.",
                 "sfx": "012.wav",
                 "is_field_skill": True, "special_effects": ["poison_field", "venom_burst"],
                 "organic_effects": {"독술_지배": 0.45, "독_촉진": 0.4, "침묵_술": 0.3}},
                {"name": "베놈흡수", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 18, "cast_time": 25, "cooldown": 7,
                 "description": "[흡수] [보호막] [독왕강림] - [BUFF] 모든 적의 독을 흡수하여 베놈 보호막을 생성하고 독왕의 힘을 각성합니다.",
                 "sfx": "012.wav",
                 "special_effects": ["venom_absorption", "poison_emperor"],
                 "organic_effects": {"독술_지배": 0.6, "독_촉진": 0.5, "침묵_술": 0.4}}
                
                # 기존 스킬들 (비활성화)
                # {"name": "침묵의독침", ...},  # 부식독침으로 통합
                # {"name": "부식독", ...},      # 부식독침으로 통합
                # {"name": "침묵살", ...},      # 침묵암살로 통합
                # {"name": "독안개진", ...},    # 독성안개로 통합
                # {"name": "독혈폭발", ...},    # 베놈폭발로 통합
                # {"name": "독왕강림", ...},    # 베놈흡수로 통합
                # {"name": "독성칵테일", ...},  # 베놈폭발로 통합
                # {"name": "역병확산", ...},    # 독성안개로 통합
                # {"name": "독폭발", ...},      # 독성필드로 통합
            ],
            
            "해적": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "보물검", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 94, "accuracy": 95,
                 "description": "[BRV:94] [보물] [검] - [BRV] 보물을 찾는 검으로 적을 공격하고 골드를 획득할 기회를 얻습니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["treasure_hunt"],  # 기본 공격으로 보물 탐지
                 "organic_effects": {"해적_기술": 0.3, "행운": 0.25, "민첩성": 0.2}},
                {"name": "약탈공격", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 103, "accuracy": 90,
                 "description": "[HP:103] [약탈] [공격] - [HP] 적을 공격하며 동시에 소지품을 약탈합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["pirate_plunder"],  # 기본 HP 공격으로 약탈 효과
                 "sfx": "017.wav", "organic_effects": {"해적_기술": 0.35, "행운": 0.25, "전투_본능": 0.2}},
                
                # 바다의 무법자 - [해적][자유] 키워드 특화
                {"name": "이도류", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 2,
                 "description": "[공격+20%] [이도류] [검술] - [BUFF] 양손에 검을 들고 이도류 전투 자세로 공격력을 증가시킵니다.",
                 "sfx": "012.wav",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.15},
                                   {"type": StatusType.BOOST_CRIT, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"해적_정신": 0.4, "무술_수행": 0.3, "자유_의지": 0.3}},
                {"name": "칼부림", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 3, "brv_power": 112, "crit_rate": 15, "accuracy": 90, "sfx": "012.wav",
                 "description": "[BRV:90] [이도류] [연타] - [BRV] 이도류로 연속 공격하여 BRV를 획득합니다.",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.LIGHTNING,
                 "special_effects": ["combo_attack"],  # 이도류 연타 공격 추가
                 "status_effects": [{
"type": StatusType.BLEED, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.4, "무술_수행": 0.35, "전투_본능": 0.25}},
                {"name": "바다의저주", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "element": ElementType.WATER, "sfx": "064.wav",
                 "description": "[행동력감소] [저주] [바다] - [DEBUFF] 바다의 저주로 적을 속박하여 행동력을 크게 감소시킵니다.",
                 "status_effects": [{
"type": StatusType.CURSE, "duration": 4, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_SPD, "duration": 4, "intensity": 0.8}],
                 "organic_effects": {"해적_정신": 0.4, "마법_지식": 0.3, "자유_의지": 0.3}},
                {"name": "해적의함성", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 5, "cooldown": 3,
                 "description": "[전체 공격+] [사기+] [해적] - [BUFF] 해적다운 함성으로 아군의 공격력과 사기를 올립니다.",
                 "sfx": "012.wav",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 3, "intensity": 1.1},
                                   {"type": StatusType.INSPIRATION, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.4, "지휘력": 0.35, "자유_의지": 0.25}},
                {"name": "해상치료술", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 2.5, "sfx": "005.wav",
                 "description": "[전체치유] [필드] [바다] - [FIELD] 바다에서 배운 치료술로 아군 전체의 상처를 치유합니다.",
                 "element": ElementType.WATER, "is_field_skill": True,
                 "status_effects": [{
"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"해적_정신": 0.35, "마법_지식": 0.3, "치유_기술": 0.25}},
                {"name": "폭풍의함대", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 17, "hp_power": 133, "element": ElementType.WATER,
                 "cooldown": 6, "cast_time": 18, "sfx": "012.wav",
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
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["samurai_focus"],  # 기본 공격으로 의지 집중
                 "organic_effects": {"검술": 0.3, "집중력": 0.25, "정신력": 0.2}},
                {"name": "의지집중", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 110, "accuracy": 90,
                 "description": "[HP:110] [의지] [집중] - [HP] 마음을 집중하여 강력한 일격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["bushido_spirit"],  # 기본 HP 공격으로 무사도 정신
                 "sfx": "026.wav", "organic_effects": {"검술": 0.35, "정신력": 0.25, "집중력": 0.2}},
                
                # 검의 구도자 - [무사도][정신] 키워드 특화
                {"name": "무사도", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3,
                 "description": "[전능력+] [무사도] [정신] - [BUFF] 무사도 정신으로 자신의 전투 능력을 크게 향상시킵니다.",
                 "sfx": "012.wav",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.FOCUS, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "검술_대가": 0.3, "집중력": 0.3}},
                {"name": "거합베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 125, "accuracy": 98, "crit_rate": 20,
                 "description": "[BRV:125] [발도] [크리+] - [BRV] 검을 뽑는 순간의 집중력으로 강력한 BRV 공격을 가합니다.",
                 "sfx": "026.wav",
                 "damage_type": DamageType.PHYSICAL, "element": ElementType.LIGHTNING,
                 "status_effects": [{
"type": StatusType.SILENCE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"검술_대가": 0.45, "무사도_정신": 0.3, "집중력": 0.25}},
                {"name": "명상", "type": SkillType.HEAL, "target": TargetType.SELF,
                 "mp_cost": 4, "heal_power": 2.2,
                 "description": "[HP회복] [MP회복] [명상] - [HEAL] 깊은 명상으로 내면의 평화를 찾아 HP와 MP를 회복합니다.",
                 "sfx": "005.wav",
                 "element": ElementType.NEUTRAL,
                 "status_effects": [{
"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "집중력": 0.35, "치유_기술": 0.25}},
                {"name": "진검승부", "type": SkillType.COUNTER, "target": TargetType.SELF,
                 "mp_cost": 5, "cooldown": 2, "sfx": "017.wav",
                 "description": "[반격강화] [카운터] [검술] - [COUNTER] 진검승부 자세로 적의 공격을 받아 더 강한 반격을 가합니다.",
                 "status_effects": [{"type": StatusType.COUNTER, "duration": 3, "intensity": 2.0},
                                   {"type": StatusType.BARRIER, "duration": 3, "intensity": 1.3}],
                 "organic_effects": {"무사도_정신": 0.4, "검술_대가": 0.3, "전투_본능": 0.3}},
                {"name": "사무라이치유법", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 2.5, "sfx": "005.wav",
                 "description": "[전체치유] [필드] [전통] - [FIELD] 사무라이의 전통 치유법으로 아군들의 상처를 치료합니다.",
                 "element": ElementType.LIGHT, "is_field_skill": True,
                 "status_effects": [{
"type": StatusType.BLESSING, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"무사도_정신": 0.4, "치유_기술": 0.3, "지휘력": 0.3}},
                {"name": "오의무상베기", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 20, "hp_power": 161, "cooldown": 8, "cast_time": 35,
                 "description": "[궁극] [HP:180] [무상] [검술] - [궁극] 무상의 경지에서 펼치는 궁극의 검술로 적을 완전히 제압합니다.",
                 "sfx": "017.wav",
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
                 "sfx": "012.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["melody_build"],  # 기본 공격으로 멜로디 축적
                 "organic_effects": {"음악_재능": 0.3, "창작_영감": 0.25, "지휘력": 0.2}},
                {"name": "선율폭발", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 102, "accuracy": 88,
                 "description": "[HP:102] [선율] [폭발] - [HP] 축적된 음악 에너지를 강력한 음파로 방출합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["sonic_burst"],  # 기본 HP 공격으로 음파 폭발
                 "sfx": "019.wav", "organic_effects": {"지휘력": 0.35, "음악_재능": 0.25, "창작_영감": 0.2}},
                
                # 선율의 지휘자 - [음악][지원] 키워드 특화
                {"name": "용기의노래", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "sfx": "012.wav",
                 "description": "[전체 공격+10%] [크리+15%] [음악] - [BUFF][음악][버프] 용기를 북돋우는 장엄한 노래로 아군 전체의 공격력과 치명타율을 크게 강화",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.1},
                                   {"type": StatusType.BOOST_CRIT, "duration": 4, "intensity": 1.15}],
                 "organic_effects": {"음악_재능": 0.4, "지휘력": 0.35, "마법_지식": 0.25}},
                {"name": "회복의선율", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "heal_power": 2.1, "sfx": "005.wav",
                 "description": "[전체치유:중] [재생] [음악] - [HEAL][음악][치유] 치유의 선율로 아군 전체의 HP를 회복시키는 바드의 대표적인 회복 기술",
                 "element": ElementType.LIGHT,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"음악_재능": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "절망의노래", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "sfx": "012.wav",
                 "description": "[전체 공포] [공격감소] [음악] - [DEBUFF][음악][절망] 절망적인 선율로 적 전체에 공포와 공격력 감소를 부여",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.REDUCE_ATK, "duration": 4, "intensity": 0.9}],
                 "organic_effects": {"음악_재능": 0.4, "마법_지식": 0.3, "지휘력": 0.3}},
                {"name": "신속의리듬", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "cooldown": 3, "sfx": "012.wav",
                 "description": "[전체 속도+20%] [가속] [음악] - [BUFF][음악][신속] 빠른 리듬으로 아군 전체의 속도와 행동력을 크게 향상시킴",
                 "status_effects": [{"type": StatusType.BOOST_SPD, "duration": 4, "intensity": 1.2},
                                   {"type": StatusType.HASTE, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"음악_재능": 0.4, "지휘력": 0.35, "마법_지식": 0.25}},
                {"name": "천상의치유가", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 4.5,
                 "description": "[전체치유:강] [상태해제] [필드] - [FIELD][음악][신성] 천상의 치유가로 아군 전체 치유 및 상태이상 해제",
                 "element": ElementType.LIGHT, "is_field_skill": True,
                 "special_effects": ["divine_song"],
                 "sfx": "068.wav", 
                 "organic_effects": {"음악_재능": 0.4, "치유_기술": 0.3, "신성_마법": 0.3}},
                {"name": "천상의합창", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 22, "cooldown": 9, "cast_time": 40, "heal_power": 5.9,
                 "description": "[궁극] [무적:2턴] [완전치유] [천상] - [궁극][음악][신성] 천사들의 합창으로 아군 전체를 강력하게 치유하고 일시적으로 무적 상태로 만듦",
                 "sfx": "012.wav",
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
                 "sfx": "017.wav",
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
                 "sfx": "012.wav", "organic_effects": {"정령_친화": 0.35, "영혼_조작": 0.25, "마법_지식": 0.2}},
                
                # 영혼의 중재자 - [정령][영혼] 키워드 특화
                {"name": "정령소환", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4,
                 "description": "[능력강화+] [정령] [소환] - [BUFF] 수호 정령을 소환하여 자신의 능력치를 크게 향상시킵니다.",
                 "sfx": "190.wav",
                 "element": ElementType.LIGHT,
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.SPIRIT_LINK, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "영혼_조작": 0.3, "마법_지식": 0.3}},
                {"name": "저주의인형", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "sfx": "064.wav",
                 "description": "[다중저주] [인형] [저주] - [DEBUFF] 저주받은 인형으로 적에게 다양한 저주 상태를 부여합니다.",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.CURSE, "duration": 6, "intensity": 1.0},
                                   {"type": StatusType.NECROSIS, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"영혼_조작": 0.4, "마법_지식": 0.3, "정령_친화": 0.3}},
                {"name": "치유의춤", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 3.2, "sfx": "005.wav",
                 "description": "[전체치유] [춤] [정령] - [HEAL] 신성한 치유의 춤으로 아군 전체의 HP를 회복시킵니다.",
                 "element": ElementType.EARTH,
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "영혼파악", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "sfx": "012.wav",
                 "description": "[약점분석] [영혼] [특수] - [SPECIAL] 적의 영혼을 파악하여 약점과 상태를 정확히 분석합니다.",
                 "element": ElementType.DARK,
                 "status_effects": [{"type": StatusType.CONFUSION, "duration": 3, "intensity": 1.0}],
                 "special_effects": ["soul_analysis"],
                 "organic_effects": {"영혼_조작": 0.45, "마법_지식": 0.3, "정령_친화": 0.25}},
                {"name": "정령치유술", "type": SkillType.FIELD, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "heal_power": 3.9, "sfx": "005.wav",
                 "description": "[강력치유] [필드] [정령] - [FIELD] 정령의 힘을 빌려 강력한 치유 효과를 전장에 펼칩니다.",
                 "element": ElementType.WATER, "is_field_skill": True,
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "대자연의심판", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 22, "hp_power": 140, "element": ElementType.EARTH,
                 "description": "[궁극] [HP:140] [전체] 대자연의 분노로 모든 적을 공격하는 파괴적인 궁극기입니다.",
                 "cooldown": 8, "cast_time": 25,
                 "sfx": "012.wav",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["nature_judgment"],
                 "status_effects": [{"type": StatusType.PETRIFY, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"정령_친화": 0.5, "영혼_조작": 0.4, "마법_지식": 0.35, "자연_이해": 0.3}}
            ],
            
            "드루이드": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "자연타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 87, "accuracy": 95,
                 "description": "[BRV:87] [자연] [타격] - [BRV] 자연의 힘을 담은 타격으로 야생의 기운을 축적합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "element": ElementType.EARTH,
                 "special_effects": ["nature_bond"],  # 기본 공격으로 자연 유대
                 "organic_effects": {"자연_이해": 0.3, "생존_본능": 0.25, "야생_본능": 0.2}},
                {"name": "야생본능", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 99, "accuracy": 90,
                 "description": "[HP:99] [야생] [본능] - [HP] 야생 동물의 본능으로 적을 공격하며 변신 준비를 합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["wild_instinct"],  # 기본 HP 공격으로 야생 본능
                 "sfx": "017.wav", "organic_effects": {"야생_본능": 0.35, "자연_이해": 0.25, "생존_본능": 0.2}},
                
                # 자연의 수호자 - [자연][변신] 키워드 특화
                {"name": "자연교감", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "012.wav",
                 "description": "[자연강화+] [교감] [자연] - [BUFF] 자연과 교감하여 모든 자연 마법의 위력을 증가시킵니다.",
                 "status_effects": [{"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.12}],
                 "organic_effects": {"자연_이해": 0.4, "마법_지식": 0.3, "정령_친화": 0.3}},
                {"name": "가시덩굴", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "element": ElementType.EARTH,
                 "description": "[이동제한] [지속피해] [식물] - [DEBUFF] 가시덩굴을 소환하여 적의 이동을 제한하고 지속 피해를 가합니다.",
                 "sfx": "012.wav",
                 "status_effects": [{
"type": StatusType.ENTANGLE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"자연_이해": 0.4, "마법_지식": 0.35, "전술_지식": 0.25}},
                {"name": "자연치유", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 6, "heal_power": 3.5, "element": ElementType.EARTH,
                 "description": "[치유] [상태해제] [자연] - [HEAL] 자연의 치유력으로 아군의 상처를 치유하고 상태이상을 해제합니다.",
                 "sfx": "005.wav", "organic_effects": {
"자연_이해": 0.4, "치유_기술": 0.35, "마법_지식": 0.25}},
                {"name": "동물변신", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 7, "cooldown": 3,
                 "description": "[변신] [능력변화] [동물] - [BUFF] 야생동물로 변신하여 특별한 능력과 스탯 보정을 얻습니다.",
                 "sfx": "266.wav",
                 "status_effects": [{
"type": StatusType.BERSERK, "duration": 4, "intensity": 1.3}],
                 "special_effects": ["animal_form"],
                 "organic_effects": {"자연_이해": 0.45, "변신_능력": 0.35, "전투_본능": 0.2}},
                {"name": "번개폭풍", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 125, "element": ElementType.LIGHTNING, "cast_time": 18,
                 "description": "[HP:145] [번개] [자연] - [HP] 번개 폭풍을 일으켜 적의 HP에 강력한 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["lightning_storm"],
                 "sfx": "069.wav", "organic_effects": {
"자연_이해": 0.4, "마법_지식": 0.35, "정령_친화": 0.25}},
                {"name": "가이아의분노", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 24, "hp_power": 154, "element": ElementType.EARTH,
                 "description": "[궁극] [자연재해] [가이아] - [궁극] 대지의 여신 가이아의 분노로 자연 재해를 일으키는 궁극기입니다.",
                 "cooldown": 8, "cast_time": 35,
                 "damage_type": DamageType.MAGICAL, "special_effects": ["gaia_wrath"],
                 "sfx": "307.wav", "organic_effects": {
"자연_이해": 0.5, "마법_지식": 0.4, "정령_친화": 0.35, "변신_능력": 0.3}}
            ],
            
            "신관": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "속죄타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 79, "accuracy": 95,
                 "description": "[BRV:79] [속죄] [타격] - [BRV] 속죄의 의미를 담은 타격으로 죄를 정화하며 속죄 스택을 쌓습니다.",
                 "sfx": "017.wav",
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
                 "sfx": "012.wav", "organic_effects": {"신앙": 0.35, "치유_기술": 0.25, "정화": 0.2}},
                
                # 신의 대행자 - [신성][치유] 키워드 특화
                {"name": "신의가호", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 5, "sfx": "093.wav",
                 "description": "[전체보호] [능력+] [신성] - [BUFF] 신의 가호로 아군 전체를 보호하고 모든 능력치를 향상시킵니다.",
                 "status_effects": [{"type": StatusType.BARRIER, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"신앙": 0.4, "신성_마법": 0.35, "지휘력": 0.25}},
                {"name": "성스러운빛", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 6, "brv_power": 105, "element": ElementType.LIGHT, "accuracy": 95,
                 "description": "[BRV:85] [정화] [성속] - [BRV] 성스러운 빛으로 적을 정화하면서 BRV를 획득합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["holy_light"],
                 "sfx": "005.wav", "organic_effects": {
"신성_마법": 0.4, "신앙": 0.3, "마법_지식": 0.3}},
                {"name": "대치유술", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 7, "heal_power": 5.5, "element": ElementType.LIGHT,
                 "description": "[강력치유] [전체] [신성] - [HEAL] 강력한 신성 마법으로 아군 전체를 크게 치유합니다.",
                 "special_effects": ["greater_heal"],
                 "sfx": "068.wav", "organic_effects": {
"치유_기술": 0.4, "신성_마법": 0.35, "신앙": 0.25}},
                {"name": "부활술", "type": SkillType.SPECIAL, "target": TargetType.DEAD_ALLY,
                 "mp_cost": 12, "cooldown": 4, "cast_time": 18, "element": ElementType.LIGHT,
                 "description": "[완전부활] [기적] [신성] - [SPECIAL] 신의 기적으로 쓰러진 동료를 완전한 상태로 되살립니다.",
                 "special_effects": ["resurrect"],
                 "sfx": "379.wav", "organic_effects": {
"신앙": 0.5, "신성_마법": 0.4, "치유_기술": 0.1}},
                {"name": "신벌", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 10, "hp_power": 161, "element": ElementType.LIGHT, "cast_time": 12,
                 "description": "[HP:160] [성속] [심판] - [HP] 신의 벌로 적의 HP에 성스러운 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["divine_punishment"],
                 "sfx": "012.wav", "organic_effects": {
"신성_마법": 0.45, "신앙": 0.35, "마법_지식": 0.2}},
                {"name": "천국의문", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 25, "cooldown": 8, "cast_time": 40, "heal_power": 9.8,
                 "description": "[궁극] [천국] [신의개입] - [궁극] 천국의 문을 열어 신의 직접적인 개입을 받는 궁극의 신성 마법입니다.",
                 "element": ElementType.LIGHT, "special_effects": ["heaven_gate"],
                 "sfx": "012.wav", "organic_effects": {
"신앙": 0.6, "신성_마법": 0.5, "치유_기술": 0.4, "지휘력": 0.3}}
            ],
            
            "성직자": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "신성타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 86, "accuracy": 95,
                 "description": "[BRV:86] [신성] [타격] - [BRV] 신성한 힘으로 적을 타격하며 신성력을 축적합니다.",
                 "sfx": "012.wav",
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
                 "sfx": "005.wav", "organic_effects": {"치유_기술": 0.35, "신성_마법": 0.25, "신앙": 0.2}},
                
                # 평화의 사도 - [성직][평화] 키워드 특화
                {"name": "평화의기도", "type": SkillType.BUFF, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 4, "sfx": "093.wav",
                 "description": "[전체 정신+] [평화] [기도] - [BUFF] 평화로운 기도로 아군 전체의 마음을 안정시키고 정신력을 향상시킵니다.",
                 "status_effects": [{"type": StatusType.BLESSING, "duration": 5, "intensity": 1.0},
                                   {"type": StatusType.GUARDIAN, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"신앙": 0.4, "평화_사상": 0.35, "지휘력": 0.25}},
                {"name": "정화의빛", "type": SkillType.SPECIAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "element": ElementType.LIGHT,
                 "description": "[모든해제] [정화] [빛] - [SPECIAL] 정화의 빛으로 모든 저주와 상태이상을 해제합니다.",
                 "special_effects": ["purify_light"],
                 "sfx": "005.wav", "organic_effects": {
"신성_마법": 0.4, "평화_사상": 0.3, "치유_기술": 0.3}},
                {"name": "신성한치유", "type": SkillType.HEAL, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 7, "heal_power": 3.5, "element": ElementType.LIGHT,
                 "description": "[치유] [축복] [신성] - [HEAL] 신성한 힘으로 아군을 치유하고 축복 상태를 부여합니다.",
                 "sfx": "006.wav",
                 "status_effects": [{"type": StatusType.REGENERATION, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"치유_기술": 0.4, "신성_마법": 0.35, "평화_사상": 0.25}},
                {"name": "침묵의서약", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "sfx": "083.wav",
                 "description": "[마법봉인] [침묵] [서약] - [DEBUFF] 침묵의 서약으로 적의 마법 사용을 봉인합니다.",
                 "status_effects": [{"type": StatusType.SILENCE, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"신성_마법": 0.4, "평화_사상": 0.3, "신앙": 0.3}},
                {"name": "순교자의길", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 9, "cooldown": 4,
                 "description": "[자기희생] [전체버프] [순교] - [SPECIAL] 순교자의 길을 걸어 자신을 희생하여 아군에게 강력한 버프를 부여합니다.",
                 "special_effects": ["martyrdom_path"],
                 "sfx": "012.wav", "organic_effects": {
"평화_사상": 0.5, "치유_기술": 0.35, "신앙": 0.15}},
                {"name": "신의심판", "type": SkillType.ULTIMATE, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 22, "hp_power": 147, "element": ElementType.LIGHT, "cooldown": 7, "cast_time": 18,
                 "description": "[궁극] [악징벌] [신벌] - [궁극] 신의 직접적인 심판으로 악한 적들을 처벌하는 궁극의 신성 마법입니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["divine_judgment"],
                 "sfx": "069.wav", "organic_effects": {
"신성_마법": 0.5, "신앙": 0.4, "치유_기술": 0.35, "평화_사상": 0.3}}
            ],
            
            # === 특수 계열 ===
            "몽크": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "기공타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 88, "accuracy": 95,
                 "description": "[BRV:88] [기공] [타격] - [BRV] 내공을 담은 타격으로 기를 순환시키며 콤보를 준비합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["chi_circulation"],  # 기본 공격으로 기 순환
                 "organic_effects": {"정신_수양": 0.3, "기_수련": 0.25, "무술_숙련": 0.2}},
                {"name": "연환권", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 96, "accuracy": 90,
                 "description": "[HP:96] [연환] [권] - [HP] 연속된 주먹 공격으로 콤보 체인을 만들어 강력한 타격을 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["combo_chain"],  # 기본 HP 공격으로 콤보 체인
                 "sfx": "017.wav", "organic_effects": {"무술_숙련": 0.35, "기_수련": 0.25, "정신_수양": 0.2}},
                
                # 기의 수행자 - [기][수련] 키워드 특화
                {"name": "기수련", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 3, "sfx": "082.wav",
                 "description": "[내력강화] [기] [수련] - [BUFF] 기수련을 통해 자신의 내재된 힘을 끌어올립니다.",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.15},
                                   {"type": StatusType.FOCUS, "duration": 5, "intensity": 1.0}],
                 "organic_effects": {"정신_수양": 0.4, "기_수련": 0.35, "무술_숙련": 0.25}},
                {"name": "연속주먹", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 91, "accuracy": 95, "hit_count": 2,
                 "description": "[BRV:80] [연타] [기공] - [BRV] 연속으로 주먹질을 가해 BRV를 획득합니다. 기수련의 성과입니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["combo_attack"],
                 "sfx": "027.wav", "organic_effects": {
"무술_숙련": 0.4, "기_수련": 0.3, "전투_본능": 0.25}},
                {"name": "명상", "type": SkillType.HEAL, "target": TargetType.SELF,
                 "mp_cost": 4, "heal_power": 3.8,
                 "description": "[HP회복] [MP회복] [명상] - [HEAL] 깊은 명상으로 내면의 평화를 찾아 HP와 MP를 회복합니다.",
                 "sfx": "005.wav",
                 "special_effects": ["mp_restore_15pct"],
                 "status_effects": [{
"type": StatusType.REGENERATION, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"정신_수양": 0.5, "기_수련": 0.3, "내면_평화": 0.25}},
                {"name": "기폭발", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 8, "hp_power": 84, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:125] [기] [폭발] - [HP] 내재된 기를 폭발시켜 적의 HP에 피해를 가합니다.",
                 "damage_type": DamageType.HYBRID, "special_effects": ["ki_explosion"],
                 "sfx": "289.wav", "organic_effects": {
"기_수련": 0.4, "무술_숙련": 0.3, "정신_수양": 0.25}},
                {"name": "철의주먹", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "hp_power": 133, "cast_time": 10, "accuracy": 95,
                 "description": "[HP:140] [강철] [주먹] - [HP] 철처럼 단단한 주먹으로 적의 HP에 강력한 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL, "special_effects": ["armor_pierce"],
                 "sfx": "289.wav", "organic_effects": {
"무술_숙련": 0.4, "기_수련": 0.35, "전투_본능": 0.3}},
                {"name": "깨달음의경지", "type": SkillType.ULTIMATE, "target": TargetType.SELF,
                 "mp_cost": 16, "cooldown": 6, "cast_time": 20,
                 "description": "[궁극] [깨달음] [초월] - [궁극] 무술의 깨달음에 도달하여 초월적인 힘을 발휘합니다.",
                 "special_effects": ["enlightenment"],
                 "sfx": "035.wav", "organic_effects": {
"정신_수양": 0.6, "기_수련": 0.5, "무술_숙련": 0.4, "내면_평화": 0.35}}
            ],
            
            "마검사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "마검베기", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 91, "accuracy": 95,
                 "description": "[BRV:91] [마검] [베기] - [BRV] 마법이 깃든 검으로 적을 베어 원소 에너지를 축적합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.HYBRID,
                 "special_effects": ["elemental_blade"],  # 기본 공격으로 원소 검 부여
                 "organic_effects": {"마검_숙련": 0.3, "원소_조화": 0.25, "균형_감각": 0.2}},
                {"name": "원소검기", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 107, "accuracy": 90,
                 "description": "[HP:107] [원소] [검기] - [HP] 원소의 힘을 담은 검기로 적의 HP에 직접적인 피해를 가합니다.",
                 "damage_type": DamageType.HYBRID,
                 "special_effects": ["elemental_burst"],  # 기본 HP 공격으로 원소 폭발
                 "sfx": "012.wav", "organic_effects": {"마검_숙련": 0.35, "원소_조화": 0.25, "마법_지식": 0.2}},
                
                # 마검의 융합자 - [융합][마검] 키워드 특화
                {"name": "마검각성", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 4, "sfx": "017.wav",
                 "description": "[마법+] [검술+] [각성] - [BUFF] 마검의 힘을 각성시켜 마법과 검술 능력을 모두 향상시킵니다.",
                 "damage_type": DamageType.HYBRID,
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 4, "intensity": 1.2}],
                 "organic_effects": {"마검_숙련": 0.4, "마법_지식": 0.3, "전투_본능": 0.25}},
                {"name": "마법검격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 5, "brv_power": 112, "element": ElementType.NEUTRAL, "accuracy": 95,
                 "description": "[BRV:100] [마법] [검술] - [BRV] 마법이 깃든 검으로 적을 공격하여 BRV를 획득합니다.",
                 "damage_type": DamageType.HYBRID,
                 "sfx": "017.wav", "organic_effects": {
"마검_숙련": 0.4, "마법_지식": 0.3, "전투_본능": 0.25}},
                {"name": "원소부여", "type": SkillType.BUFF, "target": TargetType.SELF,
                 "mp_cost": 5,
                 "description": "[원소강화] [부여] [마법] - [BUFF] 무기에 원소의 힘을 부여하여 공격력을 증가시킵니다.",
                 "damage_type": DamageType.HYBRID, "special_effects": ["elemental_weapon"],
                 "sfx": "012.wav", "organic_effects": {
"마법_지식": 0.4, "마검_숙련": 0.3, "원소_친화": 0.25}},
                {"name": "마검진", "type": SkillType.FIELD, "target": TargetType.BATTLEFIELD,
                 "mp_cost": 8, "cooldown": 3,
                 "description": "[마법진] [필드] [마검] - [FIELD] 마검으로 마법진을 그려 전장에 특수한 효과를 부여합니다.",
                 "damage_type": DamageType.MAGICAL, "is_field_skill": True, "special_effects": ["magic_field"],
                 "sfx": "017.wav", "organic_effects": {
"마법_지식": 0.4, "마검_숙련": 0.3, "전략적_사고": 0.25}},
                {"name": "마력폭발", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 140, "cast_time": 15, "accuracy": 90,
                 "description": "[HP:135] [마력] [폭발] - [HP] 마력을 폭발시켜 적의 HP에 강력한 마법 피해를 가합니다.",
                 "damage_type": DamageType.HYBRID,
                 "sfx": "141.wav", "organic_effects": {
"마검_숙련": 0.4, "마법_지식": 0.35, "전투_본능": 0.3}},
                {"name": "마검의진리", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 16, "hp_power": 133, "cooldown": 7, "cast_time": 25,
                 "description": "[궁극] [마검] [진리] - [궁극] 마검의 진리를 깨달아 마법과 검술의 완벽한 조화를 이룹니다.",
                 "damage_type": DamageType.HYBRID, "special_effects": ["perfect_fusion"],
                 "sfx": "017.wav", "organic_effects": {
"마검_숙련": 0.5, "마법_지식": 0.4, "전투_본능": 0.35, "원소_친화": 0.3}}
            ],
            
            "연금술사": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "연금막대", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 85, "accuracy": 95,
                 "description": "[BRV:85] [연금] [막대] - [BRV] 연금술 막대로 적을 타격하고 원소 변환을 시도합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["transmute_item"],  # 기본 공격으로 원소 변환
                 "organic_effects": {"연금_지식": 0.3, "창조_정신": 0.2, "마법_지식": 0.2}},
                {"name": "연금폭발", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 102, "accuracy": 90,
                 "description": "[HP:102] [연금] [폭발] - [HP] 연금술 반응으로 소규모 폭발을 일으켜 HP 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["instant_potion"],  # 기본 HP 공격 후 자가 치유
                 "sfx": "019.wav", "organic_effects": {"연금_지식": 0.35, "창조_정신": 0.25, "생존_본능": 0.2}},
                
                # 물질의 연성자 - [연성][변환] 키워드 특화
                {"name": "물질변환", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 3,
                 "description": "[변환] [연금] [특수] - [SPECIAL] 연금술로 물질을 변환하여 유용한 효과를 창조합니다.",
                 "special_effects": ["transmute_item"],
                 "sfx": "012.wav", "organic_effects": {
"연금_지식": 0.4, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "독성폭탄", "type": SkillType.BRV_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 5, "brv_power": 84, "element": ElementType.POISON, "accuracy": 90,
                 "description": "[BRV:85] [독] [폭탄] - [BRV] 독성 폭탄을 투척하여 BRV를 획득하고 적을 중독시킵니다.",
                 "sfx": "012.wav",
                 "damage_type": DamageType.MAGICAL, 
                 "status_effects": [{
"type": StatusType.POISON, "duration": 4, "intensity": 1.0}],
                 "organic_effects": {"연금_지식": 0.35, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "회복포션", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 5, "heal_power": 3.9,
                 "description": "[치유:강] [포션] [연금] - [HEAL] 직접 제조한 회복 포션으로 아군의 HP를 빠르게 회복시킵니다.",
                 "special_effects": ["instant_potion"],
                 "sfx": "005.wav", "organic_effects": {
"연금_지식": 0.4, "창조_정신": 0.35, "생존_본능": 0.2}},
                {"name": "강화주사", "type": SkillType.BUFF, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "sfx": "093.wav",
                 "description": "[전능력+] [주사] [강화] - [BUFF] 특수 강화 주사로 일시적으로 모든 능력을 향상시킵니다.",
                 "status_effects": [{
"type": StatusType.BOOST_ATK, "duration": 5, "intensity": 1.2}],
                 "organic_effects": {"연금_지식": 0.4, "창조_정신": 0.3, "마법_지식": 0.25}},
                {"name": "산성용해", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 8, "hp_power": 125, "element": ElementType.POISON, "cast_time": 15,
                 "description": "[HP:120] [산성] [용해] - [HP] 강력한 산으로 적을 용해시켜 HP 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["acid_corrosion"],
                 "sfx": "012.wav", "organic_effects": {
"연금_지식": 0.4, "마법_지식": 0.3, "창조_정신": 0.25}},
                {"name": "철학자의돌", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 18, "cooldown": 8, "cast_time": 30,
                 "description": "[궁극] [기적] [완전체] - [궁극] 연금술의 최고 산물인 철학자의 돌로 기적을 일으킵니다.",
                 "special_effects": ["philosophers_stone"],
                 "sfx": "012.wav", "organic_effects": {
"연금_지식": 0.6, "창조_정신": 0.5, "마법_지식": 0.4, "생존_본능": 0.3}}
            ],
            
            "기계공학자": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "기계타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 93, "accuracy": 95,
                 "description": "[BRV:93] [기계] [타격] - [BRV] 정밀한 기계 도구로 적을 타격하며 기계 에너지를 충전합니다.",
                 "sfx": "017.wav",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["machine_charge"],  # 기본 공격으로 기계 충전
                 "organic_effects": {"제조_마스터": 0.3, "기계_숙련": 0.25, "전략적_사고": 0.2}},
                {"name": "에너지방출", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 104, "accuracy": 90,
                 "description": "[HP:104] [에너지] [방출] - [HP] 축적된 에너지를 방출하여 적에게 기계적 피해를 가합니다.",
                 "damage_type": DamageType.PHYSICAL,
                 "special_effects": ["energy_discharge"],  # 기본 HP 공격으로 에너지 방출
                 "sfx": "019.wav", "organic_effects": {"기계_숙련": 0.35, "제조_마스터": 0.25, "전략적_사고": 0.2}},
                
                # 기계 전쟁의 건축가 - [포탑][설치] 키워드 특화
                {"name": "자동포탑설치", "type": SkillType.SUPPORT, "target": TargetType.SELF,
                 "mp_cost": 6, "cooldown": 3,
                 "description": "[자동공격] [필드] [포탑] - [FIELD] 자동 공격 포탑을 설치하여 지속적으로 적을 공격합니다.",
                 "is_field_skill": True, "special_effects": ["auto_turret_install"],
                 "sfx": "014.wav", "organic_effects": {
"제조_마스터": 0.3, "기계_숙련": 0.25, "전략적_사고": 0.2}},
                {"name": "레이저사격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 118, "element": ElementType.LIGHTNING, "accuracy": 95,
                 "description": "[BRV:95] [레이저] [기계] - [BRV] 정밀한 레이저로 적을 공격하여 BRV를 획득합니다.",
                 "damage_type": DamageType.RANGED, "special_effects": ["precision_laser"],
                 "sfx": "014.wav", "organic_effects": {
"기계_숙련": 0.4, "전략적_사고": 0.2, "전투_본능": 0.15}},
                {"name": "메카돔", "type": SkillType.SUPPORT, "target": TargetType.ALL_ALLIES,
                 "mp_cost": 8, "sfx": "012.wav",
                 "description": "[전체방어+] [실드] [기계] - [BUFF] 기계 돔을 전개하여 아군 전체를 보호하고 방어력을 증가시킵니다.",
                 "status_effects": [{
"type": StatusType.SHIELD, "duration": 4, "intensity": 1.3}],
                 "organic_effects": {"제조_마스터": 0.35, "냉정함": 0.25, "전략적_사고": 0.3}},
                {"name": "멀티미사일", "type": SkillType.HP_ATTACK, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 10, "hp_power": 98, "cast_time": 20, "accuracy": 90,
                 "description": "[HP:110] [다중] [미사일] - [HP] 다수의 미사일로 적의 HP에 폭발적인 피해를 가합니다.",
                 "damage_type": DamageType.RANGED, "special_effects": ["multi_missile"],
                 "sfx": "012.wav", "organic_effects": {
"제조_마스터": 0.3, "기계_숙련": 0.35, "전투_본능": 0.25}},
                {"name": "수리드론", "type": SkillType.HEAL, "target": TargetType.SINGLE_ALLY,
                 "mp_cost": 6, "heal_power": 4.5,
                 "description": "[자동치유] [드론] [기계] - [HEAL] 수리 드론을 전개하여 아군들의 상처를 자동으로 치료합니다.",
                 "special_effects": ["repair_drone"],
                 "sfx": "012.wav", "organic_effects": {
"제조_마스터": 0.4, "냉정함": 0.3, "기계_숙련": 0.2}},
                {"name": "기가포탑", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 18, "hp_power": 168, "cast_time": 30, "cooldown": 8,
                 "description": "[궁극] [초화력] [거대포탑] - [궁극] 초거대 포탑을 소환하여 적 전체에게 압도적인 화력을 퍼붓습니다.",
                 "is_field_skill": True, "special_effects": ["giga_turret"],
                 "sfx": "012.wav", "organic_effects": {
"제조_마스터": 0.5, "기계_숙련": 0.4, "전략적_사고": 0.3, "전투_본능": 0.25}}
            ],
"네크로맨서": [
                # 🌟 기본 공격 (mp_cost: 0)
                {"name": "죽음타격", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "brv_power": 88, "accuracy": 94,
                 "description": "[BRV:88] [죽음] [타격] - [BRV] 생명력을 흡수하는 어둠의 일격으로 영혼 에너지를 축적합니다.",
                 "sfx": "062.wav",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["soul_harvest"],  # 기본 공격으로 영혼 수확
                 "organic_effects": {"어둠_숙련": 0.3, "생명_조작": 0.25, "언데드_소환": 0.2}},
                {"name": "영혼흡수", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 0, "hp_power": 96, "accuracy": 89,
                 "description": "[HP:96] [영혼] [흡수] - [HP] 적의 영혼을 직접 흡수하여 생명력을 탈취합니다.",
                 "damage_type": DamageType.MAGICAL,
                 "special_effects": ["life_drain"],  # 기본 HP 공격으로 생명력 흡수
                 "sfx": "012.wav", "organic_effects": {"언데드_소환": 0.35, "어둠_숙련": 0.25, "생명_조작": 0.2}},
                
                # 죽음의 지배자 - [언데드][흡수] 키워드 특화
                {"name": "언데드소환", "type": SkillType.SPECIAL, "target": TargetType.SELF,
                 "mp_cost": 5,
                 "description": "[언데드] [소환] [지원] - [SPECIAL] 언데드를 소환하여 전투를 지원하게 합니다.",
                 "special_effects": ["summon_undead"],
                 "sfx": "012.wav", "organic_effects": {
"죽음_지배": 0.4, "어둠_친화": 0.3, "마법_지식": 0.25}},
                {"name": "생명력흡수", "type": SkillType.BRV_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 4, "brv_power": 98, "element": ElementType.DARK, "accuracy": 95,
                 "description": "[BRV:98] [흡수] [언데드] - [BRV] 적의 생명력을 흡수하여 자신의 BRV로 전환합니다.",
                 "sfx": "012.wav",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["life_drain"],
                 "status_effects": [{
"type": StatusType.NECROSIS, "duration": 3, "intensity": 1.0}],
                 "organic_effects": {"어둠_친화": 0.4, "죽음_지배": 0.3, "생존_본능": 0.2}},
                {"name": "공포주입", "type": SkillType.DEBUFF, "target": TargetType.ALL_ENEMIES,
                 "mp_cost": 6, "element": ElementType.DARK, "sfx": "012.wav",
                 "description": "[공포] [능력감소] [죽음] - [DEBUFF] 죽음의 공포를 주입하여 적을 공포 상태로 만들고 능력치를 감소시킵니다.",
                 "status_effects": [{
"type": StatusType.FEAR, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.MADNESS, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"죽음_지배": 0.35, "어둠_친화": 0.3, "마법_지식": 0.25}},
                {"name": "뼈감옥", "type": SkillType.DEBUFF, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 7, "sfx": "012.wav",
                 "description": "[행동봉인] [구속] [뼈] - [DEBUFF] 뼈로 만든 감옥에 적을 가둬 행동 불가 상태로 만듭니다.",
                 "status_effects": [{
"type": StatusType.ROOT, "duration": 3, "intensity": 1.0},
                                   {"type": StatusType.PARALYZE, "duration": 2, "intensity": 1.0}],
                 "organic_effects": {"죽음_지배": 0.4, "마법_지식": 0.3, "어둠_친화": 0.25}},
                {"name": "죽음의손길", "type": SkillType.HP_ATTACK, "target": TargetType.SINGLE_ENEMY,
                 "mp_cost": 9, "hp_power": 133, "element": ElementType.DARK, "cast_time": 15,
                 "description": "[HP:133] [죽음] [터치] - [HP] 죽음의 기운으로 적의 HP에 치명적인 피해를 가합니다.",
                 "damage_type": DamageType.MAGICAL, "special_effects": ["life_steal"],
                 "sfx": "012.wav", "organic_effects": {
"어둠_친화": 0.4, "죽음_지배": 0.35, "마법_지식": 0.3}},
{"name": "언데드군단", "type": SkillType.ULTIMATE, "target": TargetType.ALL_ENEMIES,
                 "description": "[궁극] [HP:154] [전체] [언데드군단] [쿨:7턴] - [궁극][네크로] 언데드 군단을 소환하여 전장을 완전히 지배하는 네크로맨서의 최종 기술",
                 "mp_cost": 18, "hp_power": 154, "element": ElementType.DARK, "cooldown": 7, "cast_time": 30,

                 "damage_type": DamageType.MAGICAL, "special_effects": ["summon_undead"],
                 "sfx": "012.wav", "organic_effects": {"죽음_지배": 0.5, "어둠_친화": 0.4, "마법_지식": 0.35, "생존_본능": 0.3}}
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
    
    def get_skills_for_class(self, character_class: str) -> List[Dict[str, Any]]:
        """직업별 스킬 반환 (편의 메서드)"""
        return self.get_class_skills(character_class)
    
    def execute_skill(self, caster, skill_data: Dict[str, Any], target=None) -> bool:
        """스킬 실행 (테스트용 간편 메서드)"""
        try:
            # 타겟 리스트 생성
            targets = [target] if target else [caster]
            
            # 스킬 효과 실행
            messages = self.execute_skill_effects(skill_data, caster, targets)
            
            # 메시지 출력
            for message in messages:
                print(message)
            
            return True
        except Exception as e:
            print(f"❌ 스킬 실행 중 오류: {e}")
            return False
    
    def execute_skill_effects(self, skill_data: Dict[str, Any], caster, targets: List, **kwargs) -> List[str]:
        """스킬의 실제 효과 실행"""
        messages = []
        
        # 올바른 스킬 타입 확인 (type 필드 사용)
        skill_type = skill_data.get("type", SkillType.BRV_ATTACK)
        special_effects = skill_data.get("special_effects", [])
        
        # 스킬명 출력
        skill_name = skill_data.get("name", "Unknown Skill")
        print(f"🎯 {caster.name}이(가) {skill_name} 사용!")
        
        for target in targets:
            if not target:
                continue
            
            # 스킬 타입에 따른 피해 계산 및 적용
            if skill_type == SkillType.BRV_ATTACK:
                # BRV 공격
                damage = self._calculate_brv_damage(skill_data, caster, target)
                old_brv = getattr(target, 'brave_points', 0)
                new_brv = max(0, old_brv - damage)
                target.brave_points = new_brv
                
                # 공격자 BRV 증가
                caster.brave_points = getattr(caster, 'brave_points', 0) + damage
                messages.append(f"💙 {target.name}의 BRV {damage} 감소, {caster.name} BRV +{damage}")
                
            elif skill_type == SkillType.HP_ATTACK:
                # HP 공격
                damage = self._calculate_hp_damage(skill_data, caster, target)
                old_hp = target.current_hp
                target.current_hp = max(1, target.current_hp - damage)
                actual_damage = old_hp - target.current_hp
                
                # 공격자 BRV 소모
                consumed_brv = getattr(caster, 'brave_points', 0)
                caster.brave_points = 0
                messages.append(f"💥 {target.name}에게 {actual_damage} HP 피해! (BRV {consumed_brv} 소모)")
        
        # 🎯 특수 효과 처리 (직업별 기믹)
        if special_effects:
            for effect in special_effects:
                try:
                    # 직접 정의된 메서드 먼저 확인
                    if hasattr(self, f'_apply_{effect}'):
                        effect_func = getattr(self, f'_apply_{effect}')
                        effect_result = effect_func(caster, targets[0] if targets else None, skill_data)
                        if effect_result:
                            messages.append(f"✨ {effect} 효과 발동!")
                    else:
                        # 글로벌 함수 확인 - 매개변수 개수에 따른 처리
                        effect_func = globals().get(f'_{effect}')
                        if effect_func:
                            try:
                                # 매개변수 3개 시도 (caster, target, skill_data)
                                if effect in ['poison_stack', 'dragon_mark', 'leap_attack', 
                                            'life_drain', 'elemental_fusion']:
                                    effect_result = effect_func(caster, targets[0] if targets else None, skill_data)
                                    if effect_result:
                                        messages.append(f"✨ {effect} 효과 발동!")
                                # 매개변수 2개 시도 (caster, target)
                                elif effect in ['shadow_execution', 'lethal_strike']:
                                    effect_result = effect_func(caster, targets[0] if targets else None)
                                    if effect_result:
                                        messages.append(f"✨ {effect} 효과 발동!")
                                # 매개변수 1개 시도 (caster)
                                else:
                                    effect_result = effect_func(caster)
                                    if effect_result:
                                        messages.append(f"✨ {effect} 효과 발동!")
                            except Exception as e:
                                # 오류 시 더 적은 매개변수로 재시도
                                try:
                                    effect_result = effect_func(caster)
                                    if effect_result:
                                        messages.append(f"✨ {effect} 효과 발동!")
                                except Exception:
                                    print(f"⚠️ {effect} 효과 처리 중 오류: {e}")
                except Exception as e:
                    print(f"⚠️ {effect} 효과 처리 중 오류: {e}")
        
        return messages
    
    def _calculate_brv_damage(self, skill_data: Dict[str, Any], caster, target) -> int:
        """BRV 피해 계산"""
        base_power = skill_data.get('brv_power', 50)
        caster_attack = getattr(caster, 'physical_attack', 50)
        target_defense = getattr(target, 'physical_defense', 30)
        
        # BRV 피해 공식
        damage = int((base_power * caster_attack) / max(1, target_defense * 0.5))
        return max(1, damage)
    
    def _calculate_hp_damage(self, skill_data: Dict[str, Any], caster, target) -> int:
        """HP 피해 계산"""
        hp_power = skill_data.get('hp_power', 100)
        caster_brv = getattr(caster, 'brave_points', 100)
        
        # HP 피해는 BRV 포인트 * HP 파워로 계산
        damage = int(caster_brv * (hp_power / 100.0))
        return max(1, damage)
    
    def _calculate_skill_damage(self, skill_data: Dict[str, Any], caster, target) -> int:
        """스킬 피해 계산 (호환성을 위한 기존 메서드)"""
        base_power = skill_data.get('brv_power', skill_data.get('hp_power', 50))
        caster_attack = getattr(caster, 'physical_attack', 50)
        target_defense = getattr(target, 'physical_defense', 30)
        
        # 간단한 피해 공식
        damage = int((base_power * caster_attack) / max(1, target_defense))
        return max(1, damage)
    
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

# 클래스 추가 메서드들을 NewSkillSystem 클래스 안으로 이동

def get_skills_for_class(character_class: str) -> List[Dict[str, Any]]:
    """직업별 스킬 반환 (전역 함수)"""
    return skill_system.get_class_skills(character_class)

def get_skill_by_name(character_class: str, skill_name: str) -> Dict[str, Any]:
    """특정 스킬 검색 (전역 함수)"""
    skills = get_skills_for_class(character_class)
    for skill in skills:
        if skill["name"] == skill_name:
            return skill
    return None

# 스킬 시스템 초기화

# === 스킬 실행 함수들 ===

def apply_special_effect(effect_name: str, caster, target=None, skill_data=None):
    """특수 효과 적용"""
    try:
        # 직접 처리할 효과들
        if effect_name == "stance_adaptation":
            return _stance_adaptation(caster)
        elif effect_name == "enemy_analysis":
            return _enemy_analysis(caster)
        elif effect_name == "rage_build":
            return _rage_build(caster)
        elif effect_name == "basic_vampiric":
            return _basic_vampiric(caster, target, skill_data)
        # ... 기타 효과들
        return []
    except Exception as e:
        print(f"특수 효과 {effect_name} 적용 중 오류: {e}")
        return []
    
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
            # 정확한 나눗셈 공식: 공격력을 방어력으로 나누고 최소 1 데미지 보장
            final_damage = max(1, int(total_damage / defense))
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
    try:
        # 직접 처리할 효과들
        if effect_name == "stance_adaptation":
            return _stance_adaptation(caster)
        elif effect_name == "enemy_analysis":
            return _enemy_analysis(caster)
        elif effect_name == "adaptive_ultimate":
            return _adaptive_ultimate(caster, target, skill_data)
        elif effect_name == "guardian_bonus":
            return _guardian_bonus(caster)
        elif effect_name == "melody_build":
            return _melody_build(caster)
        elif effect_name == "holy_blessing":
            return _holy_blessing(caster)
        elif effect_name == "ice_count":
            return _ice_count(caster, target, skill_data)
        elif effect_name == "fire_count":
            return _fire_count(caster, target, skill_data)
        elif effect_name == "lightning_count":
            return _lightning_count(caster, target, skill_data)
    except Exception as e:
        print(f"특수 효과 '{effect_name}' 적용 중 오류: {e}")
        return False
    
    effects_map = {
        # 전사 효과
        "double_attack": lambda caster, target=None, skill_data=None: _double_attack(caster, target, skill_data),
        "armor_pierce": lambda caster, target=None, skill_data=None: _armor_pierce(caster, target, skill_data),
        "berserker_rage": lambda caster, target=None, skill_data=None: _berserker_rage(caster, skill_data),
        
        # 🌟 새로운 검성 효과 - 검기 스택 시스템
        "sword_aura_gain": lambda caster, target=None, skill_data=None: _sword_aura_gain(caster),
        "sword_aura_consume": lambda caster, target=None, skill_data=None: _sword_aura_consume(caster, target, skill_data),
        "sword_aura_consume_all": lambda caster, target=None, skill_data=None: _sword_aura_consume_all(caster, target, skill_data),
        "sword_aura_wave": lambda caster, target=None, skill_data=None: _sword_aura_wave(caster, target, skill_data),
        "atb_refund": lambda caster, target=None, skill_data=None: _atb_refund(caster, skill_data),
        "atb_refund_medium": lambda caster, target=None, skill_data=None: _atb_refund_medium(caster, skill_data),
        "infinite_blade": lambda caster, target=None, skill_data=None: _infinite_blade(caster, target, skill_data),
        
        # 기존 검성 효과
        "iai_cut": lambda caster, target=None, skill_data=None: _iai_cut(caster, target, skill_data),
        "sword_pressure": lambda caster, target=None, skill_data=None: _sword_pressure(caster, target, skill_data),
        "sword_unity": lambda caster, target=None, skill_data=None: _sword_unity(caster),
        "peerless_cut": lambda caster, target=None, skill_data=None: _peerless_cut(caster, target, skill_data),
        "sword_emperor": lambda caster, target=None, skill_data=None: _sword_emperor(caster, target, skill_data),
        
        # 🌟 새로운 검투사 효과 - 처치 스택 + 패링
        "gladiator_skill": lambda caster, target=None, skill_data=None: _gladiator_skill(caster, target, skill_data),
        "parry_stance": lambda caster, target=None, skill_data=None: _parry_stance(caster),
        "honor_strike": lambda caster, target=None, skill_data=None: _honor_strike(caster, target, skill_data),
        "warrior_roar": lambda caster, target=None, skill_data=None: _warrior_roar(caster),
        "survival_spirit": lambda caster, target=None, skill_data=None: _survival_spirit(caster, target, skill_data),
        
        # 기존 검투사 효과
        "gladiator_honor": lambda caster, target=None, skill_data=None: _gladiator_honor(caster),
        "colosseum_king": lambda caster, target=None, skill_data=None: _colosseum_king(caster, target, skill_data),
        
        # 🌟 새로운 광전사 효과 - HP 소모 + 보호막 + 흡혈
        "berserk_strike": lambda caster, target=None, skill_data=None: _berserk_strike(caster, target, skill_data),
        "vampire_attack": lambda caster, target=None, skill_data=None: _vampire_attack(caster, target, skill_data),
        "blood_shield": lambda caster, target=None, skill_data=None: _blood_shield(caster, skill_data),
        "blood_max_hp_boost": lambda caster, target=None, skill_data=None: _blood_max_hp_boost(caster, skill_data),
        "vampiric_blast": lambda caster, target=None, skill_data=None: _vampiric_blast(caster, target, skill_data),
        "shield_consume": lambda caster, target=None, skill_data=None: _shield_consume(caster, target, skill_data),
        "madness_amplify": lambda caster, target=None, skill_data=None: _madness_amplify(caster, skill_data),
        "rage_chain": lambda caster, target=None, skill_data=None: _rage_chain(caster, target, skill_data),
        "area_vampire": lambda caster, target=None, skill_data=None: _area_vampire(caster, target, skill_data),
        "final_madness": lambda caster, target=None, skill_data=None: _final_madness(caster, target, skill_data),
        "massive_vampire": lambda caster, target=None, skill_data=None: _massive_vampire(caster, target, skill_data),
        
        # 기존 광전사 효과
        "rage_seed": lambda caster, target=None, skill_data=None: _rage_seed(caster),
        "blood_thirst": lambda caster, target=None, skill_data=None: _blood_thirst(caster, target, skill_data),
        "mad_combo": lambda caster, target=None, skill_data=None: _mad_combo(caster, target, skill_data),
        "rage_explosion": lambda caster, target=None, skill_data=None: _rage_explosion(caster, target, skill_data),
        "berserker_end": lambda caster, target=None, skill_data=None: _berserker_end(caster, target, skill_data),
        
        # 🌟 새로운 기사 효과 - 의무 스택 시스템
        "spear_charge": lambda caster, target=None, skill_data=None: _spear_charge(caster, target, skill_data),
        "protection_oath": lambda caster, target=None, skill_data=None: _protection_oath(caster),
        "chivalry_spirit": lambda caster, target=None, skill_data=None: _chivalry_spirit(caster),
        "duty_counter": lambda caster, target=None, skill_data=None: _duty_counter(caster, target, skill_data),
        "survival_will": lambda caster, target=None, skill_data=None: _survival_will(caster),
        "holy_charge": lambda caster, target=None, skill_data=None: _holy_charge(caster, target, skill_data),
        
        # 기존 기사/성기사 효과
        "knight_oath": lambda caster, target=None, skill_data=None: _knight_oath(caster),
        "holy_strike": lambda caster, target=None, skill_data=None: _holy_strike(caster, target, skill_data),
        "holy_heal": lambda caster, target=None, skill_data=None: _holy_heal(caster, target),
        "angel_descent": lambda caster, target=None, skill_data=None: _angel_descent(caster, target, skill_data),
        
        # 다크나이트 효과
        "dark_pact": lambda caster, target=None, skill_data=None: _dark_pact(caster, target, skill_data),
        "vampire_strike": lambda caster, target=None, skill_data=None: _vampire_strike(caster, target, skill_data),
        "dark_domination": lambda caster, target=None, skill_data=None: _dark_domination(caster, target, skill_data),
        
        # 드래곤나이트 효과
        "dragon_spear": lambda caster, target=None, skill_data=None: _dragon_spear(caster, target, skill_data),
        "dragon_lord": lambda caster, target=None, skill_data=None: _dragon_lord(caster, target, skill_data),
        
        # 아크메이지 효과
        "mana_recovery_10pct": lambda: _mana_recovery_percent(caster, 0.10),
        "random_element": lambda caster, target=None, skill_data=None: _random_element_effect(caster, target, skill_data),
        "all_elements": lambda caster, target=None, skill_data=None: _all_elements_effect(caster, target, skill_data),
        
        # 원소술사 효과
        "earth_rage": lambda caster, target=None, skill_data=None: _earth_rage(caster, target, skill_data),
        "four_elements": lambda caster, target=None, skill_data=None: _four_elements(caster, target, skill_data),
        
        # 시공술사 효과
        "time_record_savepoint": lambda caster, target=None, skill_data=None: _time_record_savepoint(caster, target, skill_data),
        "time_rewind_to_savepoint": lambda caster, target=None, skill_data=None: _time_rewind_to_savepoint(caster),
        "future_sight": lambda caster, target=None, skill_data=None: _future_sight(caster),
        "time_stop": lambda caster, target=None, skill_data=None: _time_stop(caster),
        "spacetime_collapse": lambda caster, target=None, skill_data=None: _spacetime_collapse(caster, target, skill_data),
        
        # 공간술사 효과
        "dimension_cloak": lambda caster, target=None, skill_data=None: _dimension_cloak(caster),
        "afterimage": lambda caster, target=None, skill_data=None: _afterimage(caster),
        "space_leap": lambda caster, target=None, skill_data=None: _space_leap(caster, target, skill_data),
        "dimension_maze": lambda caster, target=None, skill_data=None: _dimension_maze(caster, target),
        "evasion_counter": lambda caster, target=None, skill_data=None: _evasion_counter(caster, target, skill_data),
        "untouchable_state": lambda caster, target=None, skill_data=None: _untouchable_state(caster),
        
        # 철학자 효과
        "truth_insight": lambda caster, target=None, skill_data=None: _truth_insight(caster, target),
        "existence_denial": lambda caster, target=None, skill_data=None: _existence_denial(caster, target, skill_data),
        "philosophical_thought": lambda caster, target=None, skill_data=None: _philosophical_thought(caster),
        "absolute_truth": lambda caster, target=None, skill_data=None: _absolute_truth(caster, target, skill_data),
        
        # 궁수 효과
        "triple_shot": lambda caster, target=None, skill_data=None: _triple_shot(caster, target, skill_data),
        "piercing_shot": lambda caster, target=None, skill_data=None: _piercing_shot(caster, target, skill_data),
        "hunter_mode": lambda caster, target=None, skill_data=None: _hunter_mode(caster),
        
        # 도적 효과 (리메이크)
        "poison_weapon": lambda caster, target=None, skill_data=None: _poison_weapon(caster, target, skill_data),
        "poison_stack": lambda caster, target=None, skill_data=None: _poison_stack(caster, target, skill_data),
        "corrosive_poison": lambda caster, target=None, skill_data=None: _corrosive_poison(caster, target, skill_data),
        "poison_trigger": lambda caster, target=None, skill_data=None: _poison_trigger(caster, target, skill_data),
        "poison_fog_enhanced": lambda caster, target=None, skill_data=None: _poison_fog_enhanced(caster, target),
        "venom_explosion": lambda caster, target=None, skill_data=None: _venom_explosion(caster, target, skill_data),
        "poison_emperor": lambda caster, target=None, skill_data=None: _poison_emperor(caster, target, skill_data),
        
        # 도적 고급 독 시스템
        "toxic_cocktail": lambda caster, target=None, skill_data=None: _toxic_cocktail(caster, target, skill_data),
        "poison_field": lambda caster, target=None, skill_data=None: _poison_field(caster, target, skill_data),
        "plague_spread": lambda caster, target=None, skill_data=None: _plague_spread(caster, target, skill_data),
        "venom_burst": lambda caster, target=None, skill_data=None: _venom_burst(caster, target, skill_data),
        "venom_absorption": lambda caster, target=None, skill_data=None: _venom_absorption(caster, target, skill_data),
        
        # 도적 기존 효과 (호환성)
        "stealth_attack": lambda caster, target=None, skill_data=None: _stealth_attack(caster, target, skill_data),
        "smoke_screen": lambda caster, target=None, skill_data=None: _smoke_screen(caster),
        "smoke_bomb": lambda caster, target=None, skill_data=None: _smoke_bomb(caster),
        "assassination": lambda caster, target=None, skill_data=None: _assassination(caster, target, skill_data),
        "shadow_clone": lambda caster, target=None, skill_data=None: _shadow_clone(caster),
        "poison_fog": lambda caster, target=None, skill_data=None: _poison_fog(caster, target),
        "poison_blade": lambda caster, target=None, skill_data=None: _poison_blade(caster, target, skill_data),
        "poison_mastery": lambda caster, target=None, skill_data=None: _poison_mastery(caster, target, skill_data),
        
        # 해적 효과
        "ghost_fleet": lambda caster, target=None, skill_data=None: _ghost_fleet(caster, target, skill_data),
        
        # 무사 효과
        "mushin_cut": lambda caster, target=None, skill_data=None: _mushin_cut(caster, target, skill_data),
        
        # 음유시인 효과
        "divine_song": lambda caster, target=None, skill_data=None: _divine_song(caster, target),
        "heavenly_chorus": lambda caster, target=None, skill_data=None: _heavenly_chorus(caster, target, skill_data),
        
        # 동물조련사 효과
        "soul_analysis": lambda caster, target=None, skill_data=None: _soul_analysis(caster, target),
        "nature_judgment": lambda caster, target=None, skill_data=None: _nature_judgment(caster, target, skill_data),
        "animal_form": lambda caster, target=None, skill_data=None: _animal_form(caster),
        "lightning_storm": lambda caster, target=None, skill_data=None: _lightning_storm(caster, target, skill_data),
        "gaia_wrath": lambda caster, target=None, skill_data=None: _gaia_wrath(caster, target, skill_data),
        
        # 성직자 효과
        "holy_light": lambda caster, target=None, skill_data=None: _holy_light(caster, target, skill_data),
        "greater_heal": lambda caster, target=None, skill_data=None: _greater_heal(caster, target),
        "divine_punishment": lambda caster, target=None, skill_data=None: _divine_punishment(caster, target, skill_data),
        "heaven_gate": lambda caster, target=None, skill_data=None: _heaven_gate(caster, target, skill_data),
        
        # 순교자 효과
        "purify_light": lambda caster, target=None, skill_data=None: _purify_light(caster, target),
        "martyrdom_path": lambda caster, target=None, skill_data=None: _martyrdom_path(caster),
        "divine_judgment": lambda caster, target=None, skill_data=None: _divine_judgment(caster, target, skill_data),
        
        # 무술가 효과
        "combo_attack": lambda caster, target=None, skill_data=None: _combo_attack(caster, target, skill_data),
        "mp_restore_15pct": lambda: _mp_restore_15pct(caster),
        "ki_explosion": lambda caster, target=None, skill_data=None: _ki_explosion(caster, target, skill_data),
        "enlightenment": lambda caster, target=None, skill_data=None: _enlightenment(caster),
        
        # 연금술사 효과
        "elemental_weapon": lambda caster, target=None, skill_data=None: _elemental_weapon(caster, skill_data),
        "magic_field": lambda caster, target=None, skill_data=None: _magic_field(caster),
        "perfect_fusion": lambda caster, target=None, skill_data=None: _perfect_fusion(caster, target, skill_data),
        "transmute_item": lambda caster, target=None, skill_data=None: _transmute_item(caster),
        "instant_potion": lambda caster, target=None, skill_data=None: _instant_potion(caster, target),
        "acid_corrosion": lambda caster, target=None, skill_data=None: _acid_corrosion(caster, target, skill_data),
        "philosophers_stone": lambda caster, target=None, skill_data=None: _philosophers_stone(caster),
        
        # 해적 효과
        "treasure_hunt": lambda caster, target=None, skill_data=None: _treasure_hunt(caster),
        "pirate_plunder": lambda caster, target=None, skill_data=None: _pirate_plunder(caster, target, skill_data),
        "dual_wield": lambda caster, target=None, skill_data=None: _dual_wield(caster, target, skill_data),
        "sea_shanty": lambda caster, target=None, skill_data=None: _sea_shanty(caster),
        "treasure_map": lambda caster, target=None, skill_data=None: _treasure_map(caster),
        
        # 사무라이 효과
        "samurai_focus": lambda caster, target=None, skill_data=None: _samurai_focus(caster),
        "bushido_spirit": lambda caster, target=None, skill_data=None: _bushido_spirit(caster, target, skill_data),
        "iai_strike": lambda caster, target=None, skill_data=None: _iai_strike(caster, target, skill_data),
        "honor_guard": lambda caster, target=None, skill_data=None: _honor_guard(caster),
        
        # 기계공학자 효과
        "auto_turret_install": lambda caster, target=None, skill_data=None: _auto_turret_install(caster),
        "precision_laser": lambda caster, target=None, skill_data=None: _precision_laser(caster, target, skill_data),
        "repair_drone": lambda caster, target=None, skill_data=None: _repair_drone(caster, target),
        "multi_missile": lambda caster, target=None, skill_data=None: _multi_missile(caster, target, skill_data),
        "giga_turret": lambda caster, target=None, skill_data=None: _giga_turret(caster, target, skill_data),
        
        # 네크로맨서 효과
        "summon_undead": lambda caster, target=None, skill_data=None: _summon_undead(caster),
        "life_drain": lambda caster, target=None, skill_data=None: _life_drain(caster, target, skill_data),
        
        # 공통 효과
        "resurrect": lambda caster, target=None, skill_data=None: _resurrect(caster, target),
        "life_steal": lambda caster, target=None, skill_data=None: _life_steal(caster, target, skill_data),
        "dispel_all": lambda caster, target=None, skill_data=None: _dispel_all(target),
        "analyze_enemy": lambda caster, target=None, skill_data=None: _analyze_enemy(caster, target),
        
        # 상태이상 효과
        "silence_effect": lambda caster, target=None, skill_data=None: _silence_effect(caster, target, skill_data),
        "silence_attack": lambda caster, target=None, skill_data=None: _silence_attack(caster, target, skill_data),
        "poison_attack": lambda caster, target=None, skill_data=None: _poison_attack(caster, target, skill_data),
        "stun_attack": lambda caster, target=None, skill_data=None: _stun_attack(caster, target, skill_data),
        "bleeding_attack": lambda caster, target=None, skill_data=None: _bleeding_attack(caster, target, skill_data),
        "burn_attack": lambda caster, target=None, skill_data=None: _burn_attack(caster, target, skill_data),
        "freeze_attack": lambda caster, target=None, skill_data=None: _freeze_attack(caster, target, skill_data),
        "shock_attack": lambda caster, target=None, skill_data=None: _shock_attack(caster, target, skill_data),
        "confusion_attack": lambda caster, target=None, skill_data=None: _confusion_attack(caster, target, skill_data),
        "weakness_attack": lambda caster, target=None, skill_data=None: _weakness_attack(caster, target, skill_data),
        
        # 정령술사 효과
        "elemental_mastery": lambda caster, target=None, skill_data=None: _elemental_mastery(caster),
        "spirit_bond": lambda caster, target=None, skill_data=None: _spirit_bond(caster),
        
        # 시간술사 효과  
        "time_stop": lambda caster, target=None, skill_data=None: _time_stop(caster, target, skill_data),
        
        # 연금술사 효과
        "chemical_reaction": lambda caster, target=None, skill_data=None: _chemical_reaction_safe(caster, target, skill_data),
        
        # 차원술사 효과
        "dimension_rift": lambda caster, target=None, skill_data=None: _dimension_rift_safe(caster, target, skill_data),
        
        # 기타 공통 효과들 (실제 구현)
        "mana_burn": lambda caster, target=None, skill_data=None: _mana_burn(caster, target, skill_data),
        "armor_break": lambda caster, target=None, skill_data=None: _armor_break(caster, target, skill_data),
        "critical_strike": lambda caster, target=None, skill_data=None: _critical_strike(caster, target, skill_data),
        "double_attack": lambda caster, target=None, skill_data=None: _double_attack(caster, target, skill_data),
        "piercing_attack": lambda caster, target=None, skill_data=None: _piercing_attack(caster, target, skill_data),
        "stun_attack": lambda caster, target=None, skill_data=None: _stun_attack(caster, target, skill_data),
        "bleeding_attack": lambda caster, target=None, skill_data=None: _bleeding_attack(caster, target, skill_data),
        "burn_attack": lambda caster, target=None, skill_data=None: _burn_attack(caster, target, skill_data),
        "freeze_attack": lambda caster, target=None, skill_data=None: _freeze_attack(caster, target, skill_data),
        "shock_attack": lambda caster, target=None, skill_data=None: _shock_attack(caster, target, skill_data),
        "poison_attack": lambda caster, target=None, skill_data=None: _poison_attack(caster, target, skill_data),
        "confusion_attack": lambda caster, target=None, skill_data=None: _confusion_attack(caster, target, skill_data),
        "silence_attack": lambda caster, target=None, skill_data=None: _silence_attack(caster, target, skill_data),
        "weakness_attack": lambda caster, target=None, skill_data=None: _weakness_attack(caster, target, skill_data),
        "curse_attack": lambda caster, target=None, skill_data=None: _curse_attack(caster, target, skill_data),
        "drain_attack": lambda caster, target=None, skill_data=None: _drain_attack(caster, target, skill_data),
        "holy_light": lambda caster, target=None, skill_data=None: _holy_light(caster, target, skill_data),
        "dark_energy": lambda caster, target=None, skill_data=None: _dark_energy(caster, target, skill_data),
        "nature_power": lambda caster, target=None, skill_data=None: _nature_power(caster, target, skill_data),
        "wisdom_boost": lambda caster, target=None, skill_data=None: _wisdom_boost(caster, skill_data),
        "strategy_analysis": lambda caster, target=None, skill_data=None: _safe_effect_dummy(caster, target, "전략 분석"),
        "battle_tactic": lambda caster, target=None, skill_data=None: _safe_effect_dummy(caster, None, "전투 전술"),
        "crowd_control": lambda caster, target=None, skill_data=None: _safe_effect_dummy(caster, target, "군중 제어"),
        "mass_heal": lambda caster, target=None, skill_data=None: _safe_effect_dummy(caster, target, "광역 치유"),
        "group_buff": lambda caster, target=None, skill_data=None: _safe_effect_dummy(caster, None, "그룹 강화"),
        "area_debuff": lambda caster, target=None, skill_data=None: _safe_effect_dummy(caster, target, "광역 약화"),
        










        # 최종 대용량 배치 효과들
        "poison_immunity": lambda caster, target=None, skill_data=None: _poison_immunity(caster),
        "poison_resist": lambda caster, target=None, skill_data=None: _poison_resist(caster),
        "power_up": lambda caster, target=None, skill_data=None: _power_up(caster),
        "precision_strike": lambda caster, target=None, skill_data=None: _precision_strike(caster, target, skill_data),
        "quick_cast": lambda caster, target=None, skill_data=None: _quick_cast(caster),
        "rage_mode": lambda caster, target=None, skill_data=None: _rage_mode(caster),
        "rapid_fire": lambda caster, target=None, skill_data=None: _rapid_fire(caster, target, skill_data),
        "regeneration": lambda caster, target=None, skill_data=None: _regeneration(caster),
        "restore_mp": lambda caster, target=None, skill_data=None: _restore_mp(caster),
        "revival": lambda caster, target=None, skill_data=None: _revival(caster),
        "shadow_step": lambda caster, target=None, skill_data=None: _shadow_step(caster),
        "shield_bash": lambda caster, target=None, skill_data=None: _shield_bash(caster, target, skill_data),
        "shock_wave": lambda caster, target=None, skill_data=None: _shock_wave(caster, target, skill_data),
        "silence": lambda caster, target=None, skill_data=None: _silence(caster, target, skill_data),
        "slow": lambda caster, target=None, skill_data=None: _slow(caster, target, skill_data),
        "spell_steal": lambda caster, target=None, skill_data=None: _spell_steal(caster, target, skill_data),
        "stun": lambda caster, target=None, skill_data=None: _stun(caster, target, skill_data),
        "summon_elemental": lambda caster, target=None, skill_data=None: _summon_elemental(caster),
        "teleport_strike": lambda caster, target=None, skill_data=None: _teleport_strike(caster, target, skill_data),
        "time_stop": lambda caster, target=None, skill_data=None: _time_stop(caster),
        "vampiric_strike": lambda caster, target=None, skill_data=None: _vampiric_strike(caster, target, skill_data),
        "weather_control": lambda caster, target=None, skill_data=None: _weather_control(caster),
        "wind_barrier": lambda caster, target=None, skill_data=None: _wind_barrier(caster),
        "wind_elementalist": lambda caster, target=None, skill_data=None: _wind_elementalist(caster),
        "wound_healing": lambda caster, target=None, skill_data=None: _wound_healing(caster),
        "absorb_power": lambda caster, target=None, skill_data=None: _absorb_power(caster, target, skill_data),
        "acid_splash": lambda caster, target=None, skill_data=None: _acid_splash(caster, target, skill_data),
        "ancient_power": lambda caster, target=None, skill_data=None: _ancient_power(caster),
        "armor_break": lambda caster, target=None, skill_data=None: _armor_break(caster, target, skill_data),
        "battle_frenzy": lambda caster, target=None, skill_data=None: _battle_frenzy(caster),
        "berserker_rage": lambda caster, target=None, skill_data=None: _berserker_rage(caster),
        "blood_pact": lambda caster, target=None, skill_data=None: _blood_pact(caster),
        "chaos_bolt": lambda caster, target=None, skill_data=None: _chaos_bolt(caster, target, skill_data),
        "curse_break": lambda caster, target=None, skill_data=None: _curse_break(caster),
        "divine_protection": lambda caster, target=None, skill_data=None: _divine_protection(caster),
        "dragon_breath": lambda caster, target=None, skill_data=None: _dragon_breath(caster, target, skill_data),
        "earth_shake": lambda caster, target=None, skill_data=None: _earth_shake(caster, target, skill_data),
        "energy_drain": lambda caster, target=None, skill_data=None: _energy_drain(caster, target, skill_data),
        "final_strike": lambda caster, target=None, skill_data=None: _final_strike(caster, target, skill_data),
        "flame_burst": lambda caster, target=None, skill_data=None: _flame_burst(caster, target, skill_data),
        "force_field": lambda caster, target=None, skill_data=None: _force_field(caster),
        "frost_nova": lambda caster, target=None, skill_data=None: _frost_nova(caster, target, skill_data),
        "holy_light": lambda caster, target=None, skill_data=None: _holy_light(caster),
        "ice_blast": lambda caster, target=None, skill_data=None: _ice_blast(caster, target, skill_data),
        "invisible_strike": lambda caster, target=None, skill_data=None: _invisible_strike(caster, target, skill_data),
        "life_drain": lambda caster, target=None, skill_data=None: _life_drain(caster, target, skill_data),
        "lightning_bolt": lambda caster, target=None, skill_data=None: _lightning_bolt(caster, target, skill_data),
        "mass_heal": lambda caster, target=None, skill_data=None: _mass_heal(caster),
        "meteor_strike": lambda caster, target=None, skill_data=None: _meteor_strike(caster, target, skill_data),
        "poison_cloud": lambda caster, target=None, skill_data=None: _poison_cloud(caster, target, skill_data),
        "power_drain": lambda caster, target=None, skill_data=None: _power_drain(caster, target, skill_data),
        "psychic_blast": lambda caster, target=None, skill_data=None: _psychic_blast(caster, target, skill_data),
        "shadow_bind": lambda caster, target=None, skill_data=None: _shadow_bind(caster, target, skill_data),
        "soul_burn": lambda caster, target=None, skill_data=None: _soul_burn(caster, target, skill_data),
        "spell_break": lambda caster, target=None, skill_data=None: _spell_break(caster, target, skill_data),
        "thunder_storm": lambda caster, target=None, skill_data=None: _thunder_storm(caster, target, skill_data),
        "time_warp": lambda caster, target=None, skill_data=None: _time_warp(caster, target, skill_data),
        "tornado": lambda caster, target=None, skill_data=None: _tornado(caster, target, skill_data),
        "undead_army": lambda caster, target=None, skill_data=None: _undead_army(caster),
        "void_strike": lambda caster, target=None, skill_data=None: _void_strike(caster, target, skill_data),
        "war_cry": lambda caster, target=None, skill_data=None: _war_cry(caster),
        "weakness": lambda caster, target=None, skill_data=None: _weakness(caster, target, skill_data),
        "wind_slash": lambda caster, target=None, skill_data=None: _wind_slash(caster, target, skill_data),
        "winter_storm": lambda caster, target=None, skill_data=None: _winter_storm(caster, target, skill_data),
        "action_surge": lambda caster, target=None, skill_data=None: _action_surge(caster),
        "adrenaline_rush": lambda caster, target=None, skill_data=None: _adrenaline_rush(caster),
        "agility_boost": lambda caster, target=None, skill_data=None: _agility_boost(caster),
        "all_stats_up": lambda caster, target=None, skill_data=None: _all_stats_up(caster),
        "amplify_magic": lambda caster, target=None, skill_data=None: _amplify_magic(caster),
        "ancient_wisdom": lambda caster, target=None, skill_data=None: _ancient_wisdom(caster),
        "angel_blessing": lambda caster, target=None, skill_data=None: _angel_blessing(caster),
        "animal_instinct": lambda caster, target=None, skill_data=None: _animal_instinct(caster),
        "arcane_power": lambda caster, target=None, skill_data=None: _arcane_power(caster),
        "armor_pierce": lambda caster, target=None, skill_data=None: _armor_pierce(caster, target, skill_data),
        "astral_projection": lambda caster, target=None, skill_data=None: _astral_projection(caster),
        "avatar_form": lambda caster, target=None, skill_data=None: _avatar_form(caster),
        "berserk_mode": lambda caster, target=None, skill_data=None: _berserk_mode(caster),
        "blade_dance": lambda caster, target=None, skill_data=None: _blade_dance(caster, target, skill_data),
        "blood_magic": lambda caster, target=None, skill_data=None: _blood_magic(caster),
        "bone_armor": lambda caster, target=None, skill_data=None: _bone_armor(caster),
        "chain_lightning": lambda caster, target=None, skill_data=None: _chain_lightning(caster, target, skill_data),
        "chaos_magic": lambda caster, target=None, skill_data=None: _chaos_magic(caster),
        "charm": lambda caster, target=None, skill_data=None: _charm(caster, target, skill_data),
        "clone_strike": lambda caster, target=None, skill_data=None: _clone_strike(caster, target, skill_data),
        "combat_reflexes": lambda caster, target=None, skill_data=None: _combat_reflexes(caster),
        "crystal_barrier": lambda caster, target=None, skill_data=None: _crystal_barrier(caster),
        "curse_of_weakness": lambda caster, target=None, skill_data=None: _curse_of_weakness(caster, target, skill_data),
        "darkness_shroud": lambda caster, target=None, skill_data=None: _darkness_shroud(caster),
        "death_touch": lambda caster, target=None, skill_data=None: _death_touch(caster, target, skill_data),
        "demon_form": lambda caster, target=None, skill_data=None: _demon_form(caster),
        "divine_favor": lambda caster, target=None, skill_data=None: _divine_favor(caster),
        "dragon_scale": lambda caster, target=None, skill_data=None: _dragon_scale(caster),
        "earthquake": lambda caster, target=None, skill_data=None: _earthquake(caster, target, skill_data),
        "elemental_fury": lambda caster, target=None, skill_data=None: _elemental_fury(caster),
        "enchanted_weapon": lambda caster, target=None, skill_data=None: _enchanted_weapon(caster),
        "eternal_guard": lambda caster, target=None, skill_data=None: _eternal_guard(caster),
        "fire_storm": lambda caster, target=None, skill_data=None: _fire_storm(caster, target, skill_data),
        "ghost_form": lambda caster, target=None, skill_data=None: _ghost_form(caster),
        "giant_strength": lambda caster, target=None, skill_data=None: _giant_strength(caster),
        "haste": lambda caster, target=None, skill_data=None: _haste(caster),
        "ice_storm": lambda caster, target=None, skill_data=None: _ice_storm(caster, target, skill_data),
        "iron_skin": lambda caster, target=None, skill_data=None: _iron_skin(caster),
        "last_stand": lambda caster, target=None, skill_data=None: _last_stand(caster),
        "light_speed": lambda caster, target=None, skill_data=None: _light_speed(caster),
        "mage_armor": lambda caster, target=None, skill_data=None: _mage_armor(caster),
        "mass_confusion": lambda caster, target=None, skill_data=None: _mass_confusion(caster, target, skill_data),
        "nature_blessing": lambda caster, target=None, skill_data=None: _nature_blessing(caster),
        "perfect_defense": lambda caster, target=None, skill_data=None: _perfect_defense(caster),
        "phoenix_rebirth": lambda caster, target=None, skill_data=None: _phoenix_rebirth(caster),
        "poison_strike": lambda caster, target=None, skill_data=None: _poison_strike(caster, target, skill_data),
        "protect_ally": lambda caster, target=None, skill_data=None: _protect_ally(caster),
        "rage_strike": lambda caster, target=None, skill_data=None: _rage_strike(caster, target, skill_data),
        "reflect_damage": lambda caster, target=None, skill_data=None: _reflect_damage(caster),
        "sacred_light": lambda caster, target=None, skill_data=None: _sacred_light(caster),
        "spirit_form": lambda caster, target=None, skill_data=None: _spirit_form(caster),
        "stone_skin": lambda caster, target=None, skill_data=None: _stone_skin(caster),
        "ultimate_power": lambda caster, target=None, skill_data=None: _ultimate_power(caster),
        "vampire_bite": lambda caster, target=None, skill_data=None: _vampire_bite(caster, target, skill_data),
        "void_magic": lambda caster, target=None, skill_data=None: _void_magic(caster),
        "wall_of_force": lambda caster, target=None, skill_data=None: _wall_of_force(caster),
        "whirlwind": lambda caster, target=None, skill_data=None: _whirlwind(caster, target, skill_data),
        "wild_magic": lambda caster, target=None, skill_data=None: _wild_magic(caster),
        "zone_of_silence": lambda caster, target=None, skill_data=None: _zone_of_silence(caster, target, skill_data),
        # 여덟 번째 배치 효과들
        "illusion_clone": lambda caster, target=None, skill_data=None: _illusion_clone(caster),
        "immunity_boost": lambda caster, target=None, skill_data=None: _immunity_boost(caster),
        "instant_teleport": lambda caster, target=None, skill_data=None: _instant_teleport(caster),
        "invisible": lambda caster, target=None, skill_data=None: _invisible(caster),
        "lightning_strike": lambda caster, target=None, skill_data=None: _lightning_strike(caster, target, skill_data),
        "mana_burn": lambda caster, target=None, skill_data=None: _mana_burn(caster, target, skill_data),
        "mana_shield": lambda caster, target=None, skill_data=None: _mana_shield(caster),
        "magic_amplify": lambda caster, target=None, skill_data=None: _magic_amplify(caster),
        "magic_barrier": lambda caster, target=None, skill_data=None: _magic_barrier(caster),
        "magic_counter": lambda caster, target=None, skill_data=None: _magic_counter(caster),
        "magic_mirror": lambda caster, target=None, skill_data=None: _magic_mirror(caster),
        "magic_resist": lambda caster, target=None, skill_data=None: _magic_resist(caster),
        "meditation": lambda caster, target=None, skill_data=None: _meditation(caster),
        "mental_fortitude": lambda caster, target=None, skill_data=None: _mental_fortitude(caster),
        "metamagic": lambda caster, target=None, skill_data=None: _metamagic(caster),
        "mind_control": lambda caster, target=None, skill_data=None: _mind_control(caster, target, skill_data),
        "mirror_image": lambda caster, target=None, skill_data=None: _mirror_image(caster),
        "mp_boost": lambda caster, target=None, skill_data=None: _mp_boost(caster),
        "phase_shift": lambda caster, target=None, skill_data=None: _phase_shift(caster),
        # 일곱 번째 배치 효과들
        "evasion_boost": lambda caster, target=None, skill_data=None: _evasion_boost(caster),
        "explosive_finish": lambda caster, target=None, skill_data=None: _explosive_finish(caster, target, skill_data),
        "extra_turn": lambda caster, target=None, skill_data=None: _extra_turn(caster),
        "fear_aura": lambda caster, target=None, skill_data=None: _fear_aura(caster, target, skill_data),
        "fire_affinity": lambda caster, target=None, skill_data=None: _fire_affinity(caster),
        "fire_elementalist": lambda caster, target=None, skill_data=None: _fire_elementalist(caster),
        "fire_immunity": lambda caster, target=None, skill_data=None: _fire_immunity(caster),
        "fire_resist": lambda caster, target=None, skill_data=None: _fire_resist(caster),
        "flame_aura": lambda caster, target=None, skill_data=None: _flame_aura(caster),
        "frost_armor": lambda caster, target=None, skill_data=None: _frost_armor(caster),
        "fury_mode": lambda caster, target=None, skill_data=None: _fury_mode(caster),
        "gravity_control": lambda caster, target=None, skill_data=None: _gravity_control(caster, target, skill_data),
        "guard_stance": lambda caster, target=None, skill_data=None: _guard_stance(caster),
        "healing_factor": lambda caster, target=None, skill_data=None: _healing_factor(caster),
        "health_steal": lambda caster, target=None, skill_data=None: _health_steal(caster, target, skill_data),
        "hp_boost": lambda caster, target=None, skill_data=None: _hp_boost(caster),
        "ice_armor": lambda caster, target=None, skill_data=None: _ice_armor(caster),
        "ice_elementalist": lambda caster, target=None, skill_data=None: _ice_elementalist(caster),
        "ice_resist": lambda caster, target=None, skill_data=None: _ice_resist(caster),
        "ice_shield": lambda caster, target=None, skill_data=None: _ice_shield(caster),
        # 여섯 번째 배치 효과들
        "double_strike": lambda caster, target=None, skill_data=None: _double_strike(caster, target, skill_data),
        "draconic_might": lambda caster, target=None, skill_data=None: _draconic_might(caster),
        "earth_elementalist": lambda caster, target=None, skill_data=None: _earth_elementalist(caster),
        "earth_power": lambda caster, target=None, skill_data=None: _earth_power(caster),
        "earth_resonance": lambda caster, target=None, skill_data=None: _earth_resonance(caster),
        "electric_boost": lambda caster, target=None, skill_data=None: _electric_boost(caster),
        "electric_field": lambda caster, target=None, skill_data=None: _electric_field(caster),
        "elemental_armor": lambda caster, target=None, skill_data=None: _elemental_armor(caster),
        "elemental_barrier": lambda caster, target=None, skill_data=None: _elemental_barrier(caster),
        "elemental_mastery": lambda caster, target=None, skill_data=None: _elemental_mastery(caster),
        "elemental_overload": lambda caster, target=None, skill_data=None: _elemental_overload(caster),
        "energy_absorption": lambda caster, target=None, skill_data=None: _energy_absorption(caster, target, skill_data),
        "energy_boost": lambda caster, target=None, skill_data=None: _energy_boost(caster),
        "energy_focus": lambda caster, target=None, skill_data=None: _energy_focus(caster),
        "energy_overload": lambda caster, target=None, skill_data=None: _energy_overload(caster),
        "energy_recharge": lambda caster, target=None, skill_data=None: _energy_recharge(caster),
        "enhanced_accuracy": lambda caster, target=None, skill_data=None: _enhanced_accuracy(caster),
        "enhanced_luck": lambda caster, target=None, skill_data=None: _enhanced_luck(caster),
        "enhanced_reflexes": lambda caster, target=None, skill_data=None: _enhanced_reflexes(caster),
        "eternal_flame": lambda caster, target=None, skill_data=None: _eternal_flame(caster),
        # 다섯 번째 배치 효과들
        "chronos_blessing": lambda caster, target=None, skill_data=None: _chronos_blessing(caster),
        "combo_mark": lambda caster, target=None, skill_data=None: _combo_mark(caster, target, skill_data),
        "combo_multiplier": lambda caster, target=None, skill_data=None: _combo_multiplier(caster),
        "combo_strike": lambda caster, target=None, skill_data=None: _combo_strike(caster, target, skill_data),
        "complete_wound_healing": lambda caster, target=None, skill_data=None: _complete_wound_healing(caster, target),
        "constitution_boost": lambda caster, target=None, skill_data=None: _constitution_boost(caster),
        "consume_all_shadows": lambda caster, target=None, skill_data=None: _consume_all_shadows(caster),
        "corruption_risk": lambda caster, target=None, skill_data=None: _corruption_risk(caster),
        "cosmic_insight": lambda caster, target=None, skill_data=None: _cosmic_insight(caster),
        "courage_boost": lambda caster, target=None, skill_data=None: _courage_boost(caster),
        "craft_gadget": lambda caster, target=None, skill_data=None: _craft_gadget(caster),
        "critical_damage_up": lambda caster, target=None, skill_data=None: _critical_damage_up(caster),
        "critical_rate_up": lambda caster, target=None, skill_data=None: _critical_rate_up(caster),
        "damage_stack": lambda caster, target=None, skill_data=None: _damage_stack(caster),
        "dark_magic": lambda caster, target=None, skill_data=None: _dark_magic(caster, target, skill_data),
        "deep_recovery": lambda caster, target=None, skill_data=None: _deep_recovery(caster),
        "defensive_bonus": lambda caster, target=None, skill_data=None: _defensive_bonus(caster),
        "deploy_robot": lambda caster, target=None, skill_data=None: _deploy_robot(caster),
        "dimension_storm": lambda caster, target=None, skill_data=None: _dimension_storm(caster, target, skill_data),
        "dimensional_shift": lambda caster, target=None, skill_data=None: _dimensional_shift(caster),
        # 네 번째 배치 효과들
        "adaptive_ultimate": lambda caster, target=None, skill_data=None: _adaptive_ultimate(caster, target, skill_data),
        "aggressive_bonus": lambda caster, target=None, skill_data=None: _aggressive_bonus(caster),
        "stance_adaptation": lambda caster, target=None, skill_data=None: _stance_adaptation(caster),
        "enemy_analysis": lambda caster, target=None, skill_data=None: _enemy_analysis(caster),
        "guardian_bonus": lambda caster, target=None, skill_data=None: _guardian_bonus(caster),
        "air_dash": lambda caster, target=None, skill_data=None: _air_dash(caster),
        "air_mastery": lambda caster, target=None, skill_data=None: _air_mastery(caster),
        "alignment_detect": lambda caster, target=None, skill_data=None: _alignment_detect(caster, target, skill_data),
        "animal_kingdom": lambda caster, target=None, skill_data=None: _animal_kingdom(caster),
        "antidote": lambda caster, target=None, skill_data=None: _antidote(caster, target),
        "aquatic_blessing": lambda caster, target=None, skill_data=None: _aquatic_blessing(caster),
        "aquatic_breathing": lambda caster, target=None, skill_data=None: _aquatic_breathing(caster),
        "arcane_mastery": lambda caster, target=None, skill_data=None: _arcane_mastery(caster),
        "area_explosion": lambda caster, target=None, skill_data=None: _area_explosion(caster, target, skill_data),
        "auto_turret": lambda caster, target=None, skill_data=None: _auto_turret(caster),
        "bad_taste": lambda caster, target=None, skill_data=None: _bad_taste(caster, target, skill_data),
        "balanced_bonus": lambda caster, target=None, skill_data=None: _balanced_bonus(caster),
        "banishment": lambda caster, target=None, skill_data=None: _banishment(caster, target, skill_data),
        "battle_reset": lambda caster, target=None, skill_data=None: _battle_reset(caster),
        "berserker_bonus": lambda caster, target=None, skill_data=None: _berserker_bonus(caster),
        "berserker_mode": lambda caster, target=None, skill_data=None: _berserker_mode(caster),
        "breath_weapon": lambda caster, target=None, skill_data=None: _breath_weapon(caster, target, skill_data),
        "chaos_effect": lambda caster, target=None, skill_data=None: _chaos_effect(caster),
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
        "brv_shield": lambda caster, target=None, skill_data=None: _brv_shield(caster),
        "multi_shot": lambda caster, target=None, skill_data=None: _multi_shot(caster, target, skill_data),
        "confusion": lambda caster, target=None, skill_data=None: _confusion(caster, target, skill_data),
        "cure_all": lambda caster, target=None, skill_data=None: _cure_all(caster),
        "purify_all": lambda caster, target=None, skill_data=None: _purify_all(caster, target),
        "luck_boost": lambda caster, target=None, skill_data=None: _luck_boost(caster),
        "exp_double": lambda caster, target=None, skill_data=None: _exp_double(caster),
        "gold_double": lambda caster, target=None, skill_data=None: _gold_double(caster),
        "item_find": lambda caster, target=None, skill_data=None: _item_find(caster),
        "mp_restore": lambda caster, target=None, skill_data=None: _mp_restore(caster, target),
        "double_turn": lambda caster, target=None, skill_data=None: _double_turn(caster),
        "triple_hit": lambda caster, target=None, skill_data=None: _triple_hit(caster, target, skill_data),
        "party_buff": lambda caster, target=None, skill_data=None: _party_buff(caster),
        "flame_strike": lambda caster, target=None, skill_data=None: _flame_strike(caster, target, skill_data),
        "ice_trail": lambda caster, target=None, skill_data=None: _ice_trail(caster, target, skill_data),
        "lightning_storm": lambda caster, target=None, skill_data=None: _lightning_storm(caster, target, skill_data),
        "earth_shield": lambda caster, target=None, skill_data=None: _earth_shield(caster),
        "wind_walk": lambda caster, target=None, skill_data=None: _wind_walk(caster),
        "magic_amplify": lambda caster, target=None, skill_data=None: _magic_amplify(caster),
        "weapon_mastery": lambda caster, target=None, skill_data=None: _weapon_mastery(caster),
        # 두 번째 배치 효과들
        "heal_others": lambda caster, target=None, skill_data=None: _heal_others(caster, target, skill_data),
        "healing_boost": lambda caster, target=None, skill_data=None: _healing_boost(caster),
        "hp_boost": lambda caster, target=None, skill_data=None: _hp_boost(caster),
        "mp_boost": lambda caster, target=None, skill_data=None: _mp_boost(caster),
        "regeneration": lambda caster, target=None, skill_data=None: _regeneration(caster),
        "speed_increase": lambda caster, target=None, skill_data=None: _speed_increase(caster),
        "stealth_mode": lambda caster, target=None, skill_data=None: _stealth_mode(caster),
        "stun_chance": lambda caster, target=None, skill_data=None: _stun_chance(caster, target, skill_data),
        "teleport": lambda caster, target=None, skill_data=None: _teleport(caster),
        "fear_aura": lambda caster, target=None, skill_data=None: _fear_aura(caster, target, skill_data),
        "poison_immunity": lambda caster, target=None, skill_data=None: _poison_immunity(caster),
        "fire_immunity": lambda caster, target=None, skill_data=None: _fire_immunity(caster),
        "cold_immunity": lambda caster, target=None, skill_data=None: _cold_immunity(caster),
        "status_immunity": lambda caster, target=None, skill_data=None: _status_immunity(caster),
        "mana_shield": lambda caster, target=None, skill_data=None: _mana_shield(caster),
        "multi_hit": lambda caster, target=None, skill_data=None: _multi_hit(caster, target, skill_data),
        "piercing": lambda caster, target=None, skill_data=None: _piercing(caster, target, skill_data),
        "auto_counter": lambda caster, target=None, skill_data=None: _auto_counter(caster),
        "auto_revive": lambda caster, target=None, skill_data=None: _auto_revive(caster),
        "invisibility": lambda caster, target=None, skill_data=None: _invisibility(caster),
        # 기본 우선순위 효과들
        "accuracy": lambda caster, target=None, skill_data=None: _accuracy(caster),
        "accuracy_boost": lambda caster, target=None, skill_data=None: _accuracy_boost(caster),
        "adaptive_attack": lambda caster, target=None, skill_data=None: _adaptive_attack(caster, target, skill_data),
        "armor_penetration": lambda caster, target=None, skill_data=None: _armor_penetration(caster, target, skill_data),
        "berserk": lambda caster, target=None, skill_data=None: _berserk(caster),
        "brv_boost": lambda caster, target=None, skill_data=None: _brv_boost(caster),
        "brv_power": lambda caster, target=None, skill_data=None: _brv_power(caster),
        "combo_bonus": lambda caster, target=None, skill_data=None: _combo_bonus(caster),
        "critical_boost": lambda caster, target=None, skill_data=None: _critical_boost(caster),
        "damage_boost": lambda caster, target=None, skill_data=None: _damage_boost(caster),
        "dispel": lambda caster, target=None, skill_data=None: _dispel(caster, target, skill_data),
        "double_damage": lambda caster, target=None, skill_data=None: _double_damage(caster, target, skill_data),
        "first_strike": lambda caster, target=None, skill_data=None: _first_strike(caster),
        "full_heal": lambda caster, target=None, skill_data=None: _full_heal(caster),
        "heal_others": lambda caster, target=None, skill_data=None: _heal_others(caster, target, skill_data),
        "healing_boost": lambda caster, target=None, skill_data=None: _healing_boost(caster, target, skill_data),
        "hp_boost": lambda caster, target=None, skill_data=None: _hp_boost(caster, target, skill_data),
        "mp_boost": lambda caster, target=None, skill_data=None: _mp_boost(caster, target, skill_data),
        "regeneration": lambda caster, target=None, skill_data=None: _regeneration(caster, target, skill_data),
        "speed_increase": lambda caster, target=None, skill_data=None: _speed_increase(caster, target, skill_data),
        "stealth_mode": lambda caster, target=None, skill_data=None: _stealth_mode(caster, target, skill_data),
        "stun_chance": lambda caster, target=None, skill_data=None: _stun_chance(caster, target, skill_data),
        "teleport": lambda caster, target=None, skill_data=None: _teleport(caster, target, skill_data),
        "fear_aura": lambda caster, target=None, skill_data=None: _fear_aura(caster, target, skill_data),
        "poison_immunity": lambda caster, target=None, skill_data=None: _poison_immunity(caster, target, skill_data),
        "fire_immunity": lambda caster, target=None, skill_data=None: _fire_immunity(caster, target, skill_data),
        "cold_immunity": lambda caster, target=None, skill_data=None: _cold_immunity(caster, target, skill_data),
        "status_immunity": lambda caster, target=None, skill_data=None: _status_immunity(caster, target, skill_data),
        "mana_shield": lambda caster, target=None, skill_data=None: _mana_shield(caster, target, skill_data),
        "perfect_accuracy": lambda caster, target=None, skill_data=None: _perfect_accuracy(caster),
        "never_miss": lambda caster, target=None, skill_data=None: _never_miss(caster),
        "guaranteed_critical": lambda caster, target=None, skill_data=None: _guaranteed_critical(caster),
        "multi_hit": lambda caster, target=None, skill_data=None: _multi_hit(caster, target, skill_data),
        "piercing": lambda caster, target=None, skill_data=None: _piercing(caster, target, skill_data),
        "auto_counter": lambda caster, target=None, skill_data=None: _auto_counter(caster, target, skill_data),
        "auto_revive": lambda caster, target=None, skill_data=None: _auto_revive(caster, target, skill_data),
        "invisibility": lambda caster, target=None, skill_data=None: _invisibility(caster, target, skill_data),
        # 추가된 구현 함수들
        "all_elements_burst": lambda caster, target=None, skill_data=None: _all_elements_burst(caster, target, skill_data),
        "arena_experience": lambda caster, target=None, skill_data=None: _arena_experience(caster),
        "arrow_penetration": lambda caster, target=None, skill_data=None: _arrow_penetration(caster),
        "atonement_stack": lambda caster, target=None, skill_data=None: _atonement_stack(caster),
        "basic_sword_aura": lambda caster, target=None, skill_data=None: _basic_sword_aura(caster),
        "basic_sword_burst": lambda caster, target=None, skill_data=None: _basic_sword_burst(caster),
        "basic_vampiric": lambda caster, target=None, skill_data=None: _basic_vampiric(caster),
        "blessing_beam": lambda caster, target=None, skill_data=None: _blessing_beam(caster),
        "blessing_sanctuary": lambda caster, target=None, skill_data=None: _blessing_sanctuary(caster),
        "chi_circulation": lambda caster, target=None, skill_data=None: _chi_circulation(caster),
        "combo_chain": lambda caster, target=None, skill_data=None: _combo_chain(caster),
        "dark_aura": lambda caster, target=None, skill_data=None: _dark_aura(caster, target, skill_data),
        "dark_aura_passive": lambda caster, target=None, skill_data=None: _dark_aura_passive(caster),
        "dark_dominion": lambda caster, target=None, skill_data=None: _dark_dominion(caster, target, skill_data),
        "dark_lord": lambda caster, target=None, skill_data=None: _dark_lord(caster, target, skill_data),
        "darkness_power": lambda caster, target=None, skill_data=None: _darkness_power(caster),
        "decisive_strike": lambda caster, target=None, skill_data=None: _decisive_strike(caster),
        "divine_accumulation": lambda caster, target=None, skill_data=None: _divine_accumulation(caster),
        "divine_protection": lambda caster, target=None, skill_data=None: _divine_protection(caster, target, skill_data),
        "divine_release": lambda caster, target=None, skill_data=None: _divine_release(caster),
        "dragon_breath": lambda caster, target=None, skill_data=None: _dragon_breath(caster, target, skill_data),
        "dragon_lord_ultimate": lambda caster, target=None, skill_data=None: _dragon_lord_ultimate(caster, target, skill_data),
        "dragon_majesty": lambda caster, target=None, skill_data=None: _dragon_majesty(caster, target, skill_data),
        "dragon_mark": lambda caster, target=None, skill_data=None: _dragon_mark(caster, target, skill_data),
        "dragon_scale": lambda caster, target=None, skill_data=None: _dragon_scale(caster),
        "elemental_blade": lambda caster, target=None, skill_data=None: _elemental_blade(caster),
        "elemental_burst": lambda caster, target=None, skill_data=None: _elemental_burst(caster),
        "elemental_cycle": lambda caster, target=None, skill_data=None: _elemental_cycle(caster, target, skill_data),
        "elemental_fusion": lambda caster, target=None, skill_data=None: _elemental_fusion(caster, target, skill_data),
        "energy_discharge": lambda caster, target=None, skill_data=None: _energy_discharge(caster),
        "fire_count": lambda caster, target=None, skill_data=None: _fire_count(caster, target, skill_data),
        "generate_shadow": lambda caster, target=None, skill_data=None: _generate_shadow(caster),
        "guardian_will": lambda caster, target=None, skill_data=None: _guardian_will(caster),
        "holy_blessing": lambda caster, target=None, skill_data=None: _holy_blessing(caster),
        "holy_strike_sanctuary": lambda caster, target=None, skill_data=None: _holy_strike_sanctuary(caster, target, skill_data),
        "ice_count": lambda caster, target=None, skill_data=None: _ice_count(caster, target, skill_data),
        "judgment_light": lambda caster, target=None, skill_data=None: _judgment_light(caster, target, skill_data),
        "knight_honor": lambda caster, target=None, skill_data=None: _knight_honor(caster),
        "leap_attack": lambda caster, target=None, skill_data=None: _leap_attack(caster, target, skill_data),
        "lethal_strike": lambda caster, target=None, skill_data=None: _lethal_strike(caster, target),
        "life_drain_all": lambda caster, target=None, skill_data=None: _life_drain_all(caster, target, skill_data),
        "lightning_count": lambda caster, target=None, skill_data=None: _lightning_count(caster, target, skill_data),
        "machine_charge": lambda caster, target=None, skill_data=None: _machine_charge(caster),
        "melody_build": lambda caster, target=None, skill_data=None: _melody_build(caster),
        "minor_vampiric": lambda caster, target=None, skill_data=None: _minor_vampiric(caster),
        "nature_bond": lambda caster, target=None, skill_data=None: _nature_bond(caster, target, skill_data),
        "precision_stack": lambda caster, target=None, skill_data=None: _precision_stack(caster),
        "purify_touch": lambda caster, target=None, skill_data=None: _purify_touch(caster),
        "rage_build": lambda caster, target=None, skill_data=None: _rage_build(caster),
        "sanctuary_expand": lambda caster, target=None, skill_data=None: _sanctuary_expand(caster),
        "shadow_execution": lambda caster, target=None, skill_data=None: _shadow_execution(caster, target),
        "sonic_burst": lambda caster, target=None, skill_data=None: _sonic_burst(caster),
        "soul_harvest": lambda caster, target=None, skill_data=None: _soul_harvest(caster),
        "support_fire_activation": lambda caster, target=None, skill_data=None: _support_fire_activation(caster),
        "vampire_slash": lambda caster, target=None, skill_data=None: _vampire_slash(caster, target, skill_data),
        "vampiric_strike": lambda caster, target=None, skill_data=None: _vampiric_strike(caster, target, skill_data),
        "wild_instinct": lambda caster, target=None, skill_data=None: _wild_instinct(caster),
        
        # 🔧 언더바 없는 특수 효과명 호환성 추가 (실제 존재하는 것만)
        "armorbreak": lambda caster, target=None, skill_data=None: _armor_break(caster, target, skill_data),
        "spearcharge": lambda caster, target=None, skill_data=None: _spear_charge(caster, target, skill_data), 
        "corrosivepoison": lambda caster, target=None, skill_data=None: _corrosive_poison(caster, target, skill_data),
        "shadowclone": lambda caster, target=None, skill_data=None: _shadow_clone(caster),
        "elementalfusion": lambda caster, target=None, skill_data=None: _elemental_fusion(caster, target, skill_data),
        
        # 추가 호환성 (존재하는 함수만)
        "adaptiveattack": lambda caster, target=None, skill_data=None: _adaptive_attack(caster, target, skill_data),
        "doubleattack": lambda caster, target=None, skill_data=None: _double_attack(caster, target, skill_data),
        "basicswordaura": lambda caster, target=None, skill_data=None: _basic_sword_aura(caster, target, skill_data),
        "basicswordburst": lambda caster, target=None, skill_data=None: _basic_sword_burst(caster, target, skill_data),
        "swordauragain": lambda caster, target=None, skill_data=None: _sword_aura_gain(caster),
        "swordauraconsume": lambda caster, target=None, skill_data=None: _sword_aura_consume(caster, target, skill_data),
        "swordaurawave": lambda caster, target=None, skill_data=None: _sword_aura_wave(caster, target, skill_data),
        "atbrefund": lambda caster, target=None, skill_data=None: _atb_refund(caster),
        "infiniteblade": lambda caster, target=None, skill_data=None: _infinite_blade(caster, target, skill_data),
        
        # 추가 효과들 (언더바 제거)
        "dragonmark": lambda caster, target=None, skill_data=None: _dragon_mark(caster, target, skill_data),
        "dragonbreath": lambda caster, target=None, skill_data=None: _dragon_breath(caster, target, skill_data),
        "dragon_scale": lambda caster, target=None, skill_data=None: _dragon_scale(caster),
        "leap_attack": lambda caster, target=None, skill_data=None: _leap_attack(caster, target, skill_data),
        "vampiric_strike": lambda caster, target=None, skill_data=None: _vampiric_strike(caster, target, skill_data),
        }
    
    if effect_name in effects_map:
        return effects_map[effect_name]()
    else:
        # 언더바 없는 버전이 들어오면 언더바 버전으로 변환 시도
        underscore_name = effect_name.replace('_', '').replace('-', '')
        for key in effects_map.keys():
            if key.replace('_', '').replace('-', '') == underscore_name:
                return effects_map[key]()
        
        print(f"⚠️ 알 수 없는 특수 효과: {effect_name}")
        return False

def get_special_effect_handlers():
    """특수 효과 핸들러 딕셔너리 반환 (brave_combat.py에서 사용)"""
    return {
        # 광전사 효과 - HP 소모 + 보호막 + 흡혈
        "berserk_strike": _berserk_strike,
        "vampire_attack": _vampire_attack,
        "blood_shield": _blood_shield,
        "blood_max_hp_boost": _blood_max_hp_boost,
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
        
        # 원소 마법 효과
        "elemental_mastery": _elemental_mastery,
        "elemental_weakness": _elemental_weakness,
        "elemental_fusion": _elemental_fusion,
        
        # 도적 독 효과
        "poison_stack": _poison_stack,
        "venom_burst": _venom_burst,
        "deadly_poison": _deadly_poison,
        "poison_amplify": _poison_amplify,
        "corrosive_poison": _corrosive_poison,
        "poison_weapon": _poison_weapon,
        
        # 용기사 효과
        "dragon_scale": _dragon_scale,
        "draconic_might": _draconic_might,
        "dragon_breath": _dragon_breath,
        
        # 공통 효과
        "resurrect": _resurrect,
        "life_steal": _life_steal,
        "dispel_all": _dispel_all,
        "analyze_enemy": _analyze_enemy,
        
        # 기본공격 효과들
        "adaptive_attack": _adaptive_attack,
        "armor_break": _armor_break,
        "stance_adaptation": _stance_adaptation,
        "enemy_analysis": _enemy_analysis,
        "guardian_bonus": _guardian_bonus,
        
        # 추가 기본 효과들
        "accuracy": _accuracy,
        "accuracy_boost": _accuracy_boost,
        "brv_boost": _brv_boost,
        "damage_boost": _damage_boost,
        "critical_boost": _critical_boost,
        "never_miss": _never_miss,
        "perfect_accuracy": _perfect_accuracy,
        "guaranteed_critical": _guaranteed_critical,
        "first_strike": _first_strike,
        "berserk": _berserk,
        "combo_bonus": _combo_bonus,
        "double_damage": _double_damage,
        "piercing": _piercing,
        "multi_hit": _multi_hit,
        "stun_chance": _stun_chance,
        "armor_penetration": _armor_penetration,
        
        # 검성 검기 효과들
        "basic_sword_aura": _basic_sword_aura,
        "basic_sword_burst": _basic_sword_burst,
        "sword_aura_gain": _sword_aura_gain,
        "sword_aura_consume": _sword_aura_consume,
        "sword_aura_wave": _sword_aura_wave,
        "atb_refund": _atb_refund,
        "atb_refund_medium": _atb_refund_medium,
        "infinite_blade": _infinite_blade,
        "sword_aura_consume_all": _sword_aura_consume_all,
        
        # 검투사 효과들
        "arena_experience": _arena_experience,
        "decisive_strike": _decisive_strike,
        "gladiator_skill": _gladiator_skill,
        "parry_stance": _parry_stance,
        "honor_strike": _honor_strike,
        "warrior_roar": _warrior_roar,
        "survival_spirit": _survival_spirit,
        
        # 광전사 효과들
        "rage_build": _rage_build,
        "basic_vampiric": _basic_vampiric,
        
        # 전사 자세 효과들
        "double_attack": _double_attack,
        "aggressive_bonus": _aggressive_bonus,
        "defensive_bonus": _defensive_bonus,
        "balanced_bonus": _balanced_bonus,
        "adaptive_ultimate": _adaptive_ultimate,
        "stance_adaptation": _stance_adaptation,
        "enemy_analysis": _enemy_analysis,
        "guardian_bonus": _guardian_bonus,
        
        # 아크메이지 효과들
        "magic_wave": _magic_wave,
        "magic_blast": _magic_blast,
        "random_element_effect": _random_element_effect,
        "mana_recovery": _mana_recovery,
        "elemental_fusion": _elemental_fusion,
        "mana_explosion": _mana_explosion,
        "overload_magic": _overload_magic,
        "chain_magic": _chain_magic,
        "ultimate_magic": _ultimate_magic,
        
        # 궁수 효과들
        "triple_shot": _triple_shot,
        "piercing_shot": _piercing_shot,
        "rapid_fire": _rapid_fire,
        "precision_shot": _precision_shot,
        "arrow_rain": _arrow_rain,
        "explosive_arrow": _explosive_arrow,
        "wind_shot": _wind_shot,
        "ultimate_shot": _ultimate_shot,
        
        # 누락된 핵심 효과들
        "truth_insight": _truth_insight,
        "life_drain": _life_drain,
        "combo_attack": _combo_attack,
        "summon_undead": _summon_undead,
        
        # 누락된 모든 특수 효과들 추가
        "absolute_truth": lambda caster, target=None, skill_data=None: _absolute_truth(caster, target, skill_data),
        "acid_corrosion": lambda caster, target=None, skill_data=None: _acid_corrosion(caster, target, skill_data),
        "afterimage": lambda caster, target=None, skill_data=None: _afterimage(caster, target, skill_data),
        "all_elements_burst": _all_elements_burst,
        "angel_descent": lambda caster, target=None, skill_data=None: _angel_descent(caster, target, skill_data),
        "animal_form": lambda caster, target=None, skill_data=None: _animal_form(caster),
        "armor_pierce": _armor_pierce,
        "arrow_penetration": lambda caster, target=None, skill_data=None: _arrow_penetration(caster, target, skill_data),
        "assassination": _guaranteed_critical,
        "atonement_stack": lambda caster, target=None, skill_data=None: _atonement_stack(caster, target, skill_data),
        "auto_turret_install": lambda caster, target=None, skill_data=None: _auto_turret_install(caster),
        "blessing_beam": lambda caster, target=None, skill_data=None: _blessing_beam(caster),
        "blessing_sanctuary": lambda caster, target=None, skill_data=None: _blessing_sanctuary(caster),
        "bushido_spirit": lambda caster, target=None, skill_data=None: _bushido_spirit(caster, target, skill_data),
        "chi_circulation": lambda caster, target=None, skill_data=None: _chi_circulation(caster, target, skill_data),
        "chivalry_spirit": lambda caster, target=None, skill_data=None: _chivalry_spirit(caster, target, skill_data),
        "combo_chain": _combo_attack,
        "consume_all_shadows": lambda caster, target=None, skill_data=None: _consume_all_shadows(caster, target, skill_data),
        "dark_aura": lambda caster, target=None, skill_data=None: _dark_aura(caster, target, skill_data),
        "dark_aura_passive": lambda caster, target=None, skill_data=None: _dark_aura_passive(caster, target, skill_data),
        "dark_dominion": lambda caster, target=None, skill_data=None: _dark_dominion(caster, target, skill_data),
        "dark_lord": lambda caster, target=None, skill_data=None: _dark_lord(caster, target, skill_data),
        "darkness_power": lambda caster, target=None, skill_data=None: _darkness_power(caster, target, skill_data),
        "dimension_cloak": lambda caster, target=None, skill_data=None: _dimension_cloak(caster, target, skill_data),
        "dimension_maze": lambda caster, target=None, skill_data=None: _dimension_maze(caster, target, skill_data),
        "divine_accumulation": lambda caster, target=None, skill_data=None: _divine_accumulation(caster, target, skill_data),
        "divine_judgment": lambda caster, target=None, skill_data=None: _divine_judgment(caster, target, skill_data),
        "divine_protection": lambda caster, target=None, skill_data=None: _divine_protection(caster, target, skill_data),
        "divine_punishment": lambda caster, target=None, skill_data=None: _divine_punishment(caster, target, skill_data),
        "divine_release": lambda caster, target=None, skill_data=None: _divine_release(caster),
        "divine_song": lambda caster, target=None, skill_data=None: _divine_song(caster, target, skill_data),
        "dragon_awakening": lambda caster, target=None, skill_data=None: _dragon_awakening(caster, target, skill_data),
        "dragon_lord_ultimate": lambda caster, target=None, skill_data=None: _dragon_lord_ultimate(caster, target, skill_data),
        "dragon_majesty": lambda caster, target=None, skill_data=None: _dragon_majesty(caster, target, skill_data),
        "dragon_mark": lambda caster, target=None, skill_data=None: _dragon_mark(caster, target, skill_data),
        "duty_counter": lambda caster, target=None, skill_data=None: _duty_counter(caster, target, skill_data),
        "earth_rage": lambda caster, target=None, skill_data=None: _earth_rage(caster, target, skill_data),
        "elemental_blade": lambda caster, target=None, skill_data=None: _elemental_blade(caster),
        "elemental_burst": lambda caster, target=None, skill_data=None: _elemental_burst(caster, target, skill_data),
        "elemental_cycle": lambda caster, target=None, skill_data=None: _elemental_cycle(caster, target, skill_data),
        "elemental_weapon": lambda caster, target=None, skill_data=None: _elemental_weapon(caster, skill_data),
        "energy_discharge": lambda caster, target=None, skill_data=None: _energy_discharge(caster, target, skill_data),
        "enlightenment": lambda caster, target=None, skill_data=None: _enlightenment(caster, target, skill_data),
        "evasion_counter": lambda caster, target=None, skill_data=None: _evasion_counter(caster, target, skill_data),
        "existence_denial": lambda caster, target=None, skill_data=None: _existence_denial(caster, target, skill_data),
        "fire_count": lambda caster, target=None, skill_data=None: _fire_count(caster, target, skill_data),
        "four_elements": _all_elements_effect,
        "future_sight": lambda caster, target=None, skill_data=None: _future_sight(caster, target, skill_data),
        "gaia_wrath": lambda caster, target=None, skill_data=None: _gaia_wrath(caster, target, skill_data),
        "generate_shadow": lambda caster, target=None, skill_data=None: _generate_shadow(caster),
        "ghost_fleet": lambda caster, target=None, skill_data=None: _ghost_fleet(caster, target, skill_data),
        "giga_turret": lambda caster, target=None, skill_data=None: _giga_turret(caster, target, skill_data),
        "greater_heal": lambda caster, target=None, skill_data=None: _greater_heal(caster, target, skill_data),
        "guardian_will": lambda caster, target=None, skill_data=None: _guardian_will(caster),
        "heaven_gate": lambda caster, target=None, skill_data=None: _heaven_gate(caster, target, skill_data),
        "heavenly_chorus": lambda caster, target=None, skill_data=None: _heavenly_chorus(caster, target, skill_data),
        "holy_blessing": lambda caster, target=None, skill_data=None: _holy_blessing(caster),
        "holy_charge": lambda caster, target=None, skill_data=None: _holy_charge(caster, target, skill_data),
        "holy_light": lambda caster, target=None, skill_data=None: _holy_light(caster, target, skill_data),
        "holy_strike_sanctuary": lambda caster, target=None, skill_data=None: _holy_strike_sanctuary(caster, target, skill_data),
        "hunter_mode": _hunter_mode,
        "instant_potion": lambda caster, target=None, skill_data=None: _instant_potion(caster, target, skill_data),
        "judgment_light": lambda caster, target=None, skill_data=None: _judgment_light(caster, target, skill_data),
        "ki_explosion": lambda caster, target=None, skill_data=None: _ki_explosion(caster, target, skill_data),
        "knight_honor": lambda caster, target=None, skill_data=None: _knight_honor(caster),
        "leap_attack": lambda caster, target=None, skill_data=None: _leap_attack(caster, target, skill_data),
        "lethal_strike": _guaranteed_critical,
        "life_drain_all": _life_drain,
        "lightning_count": lambda caster, target=None, skill_data=None: _lightning_count(caster, target, skill_data),
        "lightning_storm": lambda caster, target=None, skill_data=None: _lightning_storm(caster, target, skill_data),
        "machine_charge": lambda caster, target=None, skill_data=None: _machine_charge(caster),
        "magic_field": lambda caster, target=None, skill_data=None: _magic_field(caster, target, skill_data),
        "magic_storm": lambda caster, target=None, skill_data=None: _magic_storm(caster, target, skill_data),
        "martyrdom_path": lambda caster, target=None, skill_data=None: _martyrdom_path(caster, target, skill_data),
        "minor_vampiric": _basic_vampiric,
        "mp_restore_15pct": lambda caster, target=None, skill_data=None: _mana_recovery_percent(caster, 0.15),
        "multi_missile": lambda caster, target=None, skill_data=None: _multi_missile(caster, target, skill_data),
        "mushin_cut": _guaranteed_critical,
        "nature_bond": lambda caster, target=None, skill_data=None: _nature_bond(caster, target, skill_data),
        "nature_judgment": lambda caster, target=None, skill_data=None: _nature_judgment(caster, target, skill_data),
        "perfect_fusion": lambda caster, target=None, skill_data=None: _perfect_fusion(caster, target, skill_data),
        "philosophers_stone": lambda caster, target=None, skill_data=None: _philosophers_stone(caster, target, skill_data),
        "philosophical_thought": lambda caster, target=None, skill_data=None: _philosophical_thought(caster, target, skill_data),
        "pirate_plunder": lambda caster, target=None, skill_data=None: _pirate_plunder(caster, target, skill_data),
        "plague_spread": lambda caster, target=None, skill_data=None: _plague_spread(caster, target, skill_data),
        "poison_emperor": lambda caster, target=None, skill_data=None: _poison_emperor(caster, target, skill_data),
        "poison_field": lambda caster, target=None, skill_data=None: _poison_field(caster, target, skill_data),
        "poison_fog_enhanced": lambda caster, target=None, skill_data=None: _poison_fog_enhanced(caster, target, skill_data),
        "poison_trigger": lambda caster, target=None, skill_data=None: _poison_trigger(caster, target, skill_data),
        "precision_laser": lambda caster, target=None, skill_data=None: _precision_laser(caster, target, skill_data),
        "precision_stack": lambda caster, target=None, skill_data=None: _precision_stack(caster, target, skill_data),
        "protection_oath": lambda caster, target=None, skill_data=None: _protection_oath(caster, target, skill_data),
        "purify_light": lambda caster, target=None, skill_data=None: _purify_light(caster, target),
        "purify_touch": lambda caster, target=None, skill_data=None: _purify_touch(caster),
        "repair_drone": lambda caster, target=None, skill_data=None: _repair_drone(caster, target, skill_data),
        "samurai_focus": lambda caster, target=None, skill_data=None: _samurai_focus(caster, target, skill_data),
        "sanctuary_expand": lambda caster, target=None, skill_data=None: _sanctuary_expand(caster, target, skill_data),
        "shadow_echo": lambda caster, target=None, skill_data=None: _shadow_echo(caster, target, skill_data),
        "shadow_execution": lambda caster, target=None, skill_data=None: _shadow_execution(caster, target, skill_data),
        "smoke_bomb": lambda caster, target=None, skill_data=None: _smoke_bomb(caster, target, skill_data),
        "sonic_burst": lambda caster, target=None, skill_data=None: _sonic_burst(caster),
        "soul_analysis": lambda caster, target=None, skill_data=None: _soul_analysis(caster, target),
        "soul_harvest": _soul_harvest,
        "space_leap": lambda caster, target=None, skill_data=None: _space_leap(caster, target, skill_data),
        "spacetime_collapse": lambda caster, target=None, skill_data=None: _spacetime_collapse(caster, target, skill_data),
        "spear_charge": lambda caster, target=None, skill_data=None: _spear_charge(caster, target, skill_data),
        "spirit_bond": lambda caster, target=None, skill_data=None: _spirit_bond(caster, target, skill_data),
        "support_fire_activation": lambda caster, target=None, skill_data=None: _support_fire_activation(caster, target, skill_data),
        "survival_will": lambda caster, target=None, skill_data=None: _survival_will(caster, target, skill_data),
        "time_record_savepoint": lambda caster, target=None, skill_data=None: _time_record_savepoint(caster, target, skill_data),
        "time_rewind_to_savepoint": lambda caster, target=None, skill_data=None: _time_rewind_to_savepoint(caster, target, skill_data),
        "time_stop": lambda caster, target=None, skill_data=None: _time_stop(caster, target, skill_data),
        "toxic_cocktail": lambda caster, target=None, skill_data=None: _toxic_cocktail(caster, target, skill_data),
        "transmute_item": lambda caster, target=None, skill_data=None: _transmute_item(caster, target, skill_data),
        "treasure_hunt": lambda caster, target=None, skill_data=None: _treasure_hunt(caster, target, skill_data),
        "untouchable_state": lambda caster, target=None, skill_data=None: _untouchable_state(caster, target, skill_data),
        "vampire_slash": _basic_vampiric,
        "vampiric_strike": _basic_vampiric,
        "venom_absorption": lambda caster, target=None, skill_data=None: _venom_absorption(caster, target, skill_data),
        "venom_explosion": lambda caster, target=None, skill_data=None: _venom_explosion(caster, target, skill_data),
        "wild_instinct": lambda caster, target=None, skill_data=None: _wild_instinct(caster, target, skill_data),
        
        # 기존 효과들로 매핑 
        "absolute_defense": lambda caster, target=None, skill_data=None: _absolute_defense(caster, target, skill_data),
        "shield_bash": lambda caster, target=None, skill_data=None: _shield_bash(caster, target, skill_data),
        "blood_drain": _basic_vampiric,
        "dark_blessing": lambda caster, target=None, skill_data=None: _dark_blessing(caster, target, skill_data),
        "meditation": _mana_recovery,
        "fury_blow": lambda caster, target=None, skill_data=None: _fury_blow(caster, target, skill_data),
        "soul_song": lambda caster, target=None, skill_data=None: _soul_song(caster, target, skill_data),
        "death_touch": lambda caster, target=None, skill_data=None: _death_touch(caster, target, skill_data),
        "shadow_strike": lambda caster, target=None, skill_data=None: _shadow_strike(caster, target, skill_data),
        "laser_shot": lambda caster, target=None, skill_data=None: _laser_shot(caster, target, skill_data),
        "mega_laser": lambda caster, target=None, skill_data=None: _mega_laser(caster, target, skill_data),
        "spirit_strike": lambda caster, target=None, skill_data=None: _spirit_strike(caster, target, skill_data),
        "soul_separation": lambda caster, target=None, skill_data=None: _soul_separation(caster, target, skill_data),
        "dual_wield_combo": _double_attack,
        "pirate_treasure": lambda caster, target=None, skill_data=None: _pirate_treasure(caster, target, skill_data),
        "iai_slash": _guaranteed_critical,
        "bushido_secret": _guaranteed_critical,
        "nature_wrath": lambda caster, target=None, skill_data=None: _nature_wrath(caster, target, skill_data),
        "logical_refutation": lambda caster, target=None, skill_data=None: _logical_refutation(caster, target, skill_data),
        "truth_enlightenment": lambda caster, target=None, skill_data=None: _truth_enlightenment(caster, target, skill_data),
        "arena_technique": lambda caster, target=None, skill_data=None: _arena_technique(caster, target, skill_data),
        "arena_finale": lambda caster, target=None, skill_data=None: _arena_finale(caster, target, skill_data),
        "lance_charge": lambda caster, target=None, skill_data=None: _lance_charge(caster, target, skill_data),
        "blessing_light": lambda caster, target=None, skill_data=None: _blessing_light(caster, target, skill_data),
        "magic_sword_aura": lambda caster, target=None, skill_data=None: _magic_sword_aura(caster, target, skill_data),
        "magic_sword_mastery": lambda caster, target=None, skill_data=None: _magic_sword_mastery(caster, target, skill_data),
        "berserker_combo": _berserk,
        "flame_burst": lambda caster, target=None, skill_data=None: _flame_burst(caster, target, skill_data),
        "frost_nova": lambda caster, target=None, skill_data=None: _frost_nova(caster, target, skill_data),
        "lightning_strike": lambda caster, target=None, skill_data=None: _lightning_strike(caster, target, skill_data),
        "earth_shake": lambda caster, target=None, skill_data=None: _earth_shake(caster, target, skill_data),
        "healing_boost": lambda caster, target=None, skill_data=None: _healing_boost(caster, target, skill_data),
        "mana_drain": _mana_recovery,
        "status_immunity": lambda caster, target=None, skill_data=None: None,
        
        # 바드 효과들
        "melody_build": _melody_build,
        "sonic_burst": _sonic_burst,
        
        # 전사 자세 효과들 - 누락된 것들 추가
        "stance_balanced": _balanced_bonus,
        "stance_aggressive": _aggressive_bonus,
        "stance_defensive": _defensive_bonus,
        "stance_berserk": _berserk
    }

# ========================================
# 전사 Special Effects
# ========================================

def _double_attack(caster, target, skill_data):
    """연속 공격 효과"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ATK, duration=2, power=1.2)
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
            caster.add_status(StatusType.RAGE, duration=3, power=rage_bonus)
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
        target.add_status(StatusType.BURN, duration=3, power=1.0)      # 화염
        target.add_status(StatusType.FREEZE, duration=2, power=1.0)    # 냉기
        target.add_status(StatusType.SHOCK, duration=3, power=1.0)     # 번개
    return True

# ========================================
# 궁수 Special Effects
# ========================================

def _triple_shot(caster, target, skill_data):
    """3연사 효과 + 조준 포인트 생성 (데미지는 스킬 정의에서 처리)"""
    try:
        # 🏹 궁수의 경우 조준 포인트 생성
        if hasattr(caster, 'character_class') and caster.character_class == "궁수":
            if hasattr(caster, 'aim_points'):
                caster.aim_points = min(caster.aim_points + 1, 5)
            else:
                caster.aim_points = 1
            print(f"🎯 조준 포인트 +1! (현재: {caster.aim_points}/5)")
        
        print(f"🏹 삼연사 발동! 연속으로 3발의 화살을 발사합니다!")
        return True
        
    except Exception as e:
        print(f"삼연사 효과 적용 중 오류: {e}")
        return False

def _piercing_shot(caster, target, skill_data):
    """관통 사격 효과 - 지원사격 스택 증가 (데미지는 스킬 정의에서 처리)"""
    try:
        # 🏹 궁수의 경우 지원사격 스택 증가
        if hasattr(caster, 'character_class') and caster.character_class == "궁수":
            if hasattr(caster, 'support_fire_stacks'):
                caster.support_fire_stacks = min(caster.support_fire_stacks + 2, 8)
            else:
                caster.support_fire_stacks = 2
            print(f"🎯 지원사격 스택 +2! (현재: {caster.support_fire_stacks}/8)")
        
        print(f"🏹💥 관통 사격! 강력한 화살이 적을 관통합니다!")
        return True
        
    except Exception as e:
        print(f"관통 사격 효과 적용 중 오류: {e}")
        return False

def _hunter_mode(caster):
    """헌터 모드 활성화"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_CRIT, duration=5, power=2.0)
        caster.add_status(StatusType.BOOST_ACCURACY, duration=5, power=1.5)
    return True

# ========================================
# 도적 Special Effects (리메이크)
# ========================================

def _poison_weapon(caster, target, skill_data):
    """독 무기 - 도적 공격력 기반 독 효과 추가"""
    try:
        if not target:
            return False
        
        # 도적 공격력 기반 독 강도 계산 (안전한 기본값 설정)
        caster_attack = safe_get_attack_stat(caster, 'physical_attack', 100)
        
        # 공격력의 15%를 독 강도로 사용 (최소 30, 최대 99999)
        poison_intensity = max(30, min(99999, int(caster_attack * 0.15)))
        
        # 독 상태 효과 부여
        if hasattr(target, 'add_status'):
            target.add_status(StatusType.POISON, duration=4, power=poison_intensity)
            print(f"☠️ {target.name}에게 강력한 독이 묻었습니다! (독성: {poison_intensity})")
        elif hasattr(target, 'status_effects'):
            # 수동으로 독 상태 추가
            poison_effect = type('PoisonEffect', (), {
                'type': StatusType.POISON,
                'duration': 4,
                'intensity': poison_intensity,
                'name': '맹독'
            })()
            target.status_effects.append(poison_effect)
            print(f"☠️ {target.name}에게 맹독이 묻었습니다! (독성: {poison_intensity})")
        else:
            print(f"☠️ 맹독성 공격이 {target.name}을 크게 약화시켰습니다!")
        
        return True
    except Exception as e:
        print(f"독 무기 효과 적용 중 오류: {e}")
        return False

def _poison_stack(caster, target, skill_data):
    """독 누적 효과 - 도적 공격력 기반"""
    try:
        if not target:
            return False
        
        # 도적 공격력 기반 독 강도 계산 (대폭 강화) - 안전한 기본값 설정
        caster_attack = safe_get_attack_stat(caster, 'physical_attack', 100)
        
        # 공격력의 80%를 독 강도로 사용 (20% → 80%로 4배 증가, 최소 160, 최대 99999)
        base_poison_intensity = max(160, min(99999, int(caster_attack * 0.80)))
        
        # 🧪 도적 전용: BRV 공격 시 venom_power 증가
        if hasattr(caster, 'character_class') and caster.character_class == "도적":
            if hasattr(caster, 'venom_power') and hasattr(caster, 'venom_power_max'):
                # 공격력의 일부(5%)만큼 venom 증가 (최소 3, 최대 15)
                venom_gain = max(3, min(15, int(caster_attack * 0.05)))
                old_venom = caster.venom_power
                caster.venom_power = min(caster.venom_power + venom_gain, caster.venom_power_max)
                
                # venom 증가 메시지 표시
                if caster.venom_power > old_venom:
                    new_venom = caster.venom_power
                    gain_amount = new_venom - old_venom
                    print(f"🧪 독침 공격! Venom Power: {old_venom} → {new_venom} (+{gain_amount})")
                    
                    # venom이 최대치에 도달했을 때 특별 메시지
                    if caster.venom_power >= caster.venom_power_max:
                        print(f"💀 [VENOM MAX] 도적의 독액이 최고조에 달했습니다! ({caster.venom_power}/{caster.venom_power_max})")
            
        # 독 상태 확인하여 누적
        existing_poison = None
        if hasattr(target, 'status_effects') and target.status_effects:
            for effect in target.status_effects:
                if hasattr(effect, 'type') and effect.type == StatusType.POISON:
                    existing_poison = effect
                    break
        
        if existing_poison:
            # 독 지속시간 연장 + 강도 증가 (도적 공격력 반영)
            old_duration = getattr(existing_poison, 'duration', 0)
            old_intensity = getattr(existing_poison, 'intensity', 1.0)
            existing_poison.duration = old_duration + 3
            # 기존 독에 새로운 독 강도의 50% 추가
            intensity_increase = base_poison_intensity * 0.5
            existing_poison.intensity = min(old_intensity + intensity_increase, caster_attack * 0.6)
            
            # 독 누적 메시지 표시
            print(f"☠️ 맹독 누적! {old_intensity:.0f} → {existing_poison.intensity:.0f} 독성 | {old_duration} → {existing_poison.duration}턴")
            print(f"   💀 도적의 맹독이 더욱 강력해졌습니다!")
        else:
            # 새로운 독 부여 (도적 공격력 기반 - 대폭 강화)
            if hasattr(target, 'add_status'):
                # StatusEffect 호환성을 위해 effect_value 사용
                poison_damage_per_turn = int(base_poison_intensity * 0.3)  # 독 강도의 30%가 턴당 피해
                total_poison_damage = poison_damage_per_turn * 6
                target.add_status(StatusType.POISON, duration=6, effect_value=poison_damage_per_turn)
                print(f"☠️ 강력한 독 부여! 6턴간 매턴 {poison_damage_per_turn} 피해 (총 {total_poison_damage})")
            else:
                print(f"☠️ {getattr(target, 'name', '대상')}에게 강력한 독을 부여했습니다!")
        return True
    except Exception as e:
        print(f"독 효과 적용 중 오류: {e}")
        return False

def _corrosive_poison(caster, target, skill_data):
    """부식성 독 효과 - 도적 공격력 기반"""
    try:
        if not target:
            return False
        
        # 도적 공격력 기반 독 강도 계산 - 안전한 기본값 설정
        caster_attack = safe_get_attack_stat(caster, 'physical_attack', 100)
        
        # 공격력의 25%를 독 강도로 사용 (최소 50, 최대 99999)
        poison_intensity = max(50, min(99999, int(caster_attack * 0.25)))
        
        if hasattr(target, 'add_status'):
            # 방어력 감소와 함께 강력한 독 누적
            target.add_status(StatusType.POISON, duration=8, power=poison_intensity)
            target.add_status(StatusType.REDUCE_DEF, duration=5, power=0.7)
            print(f"☠️ {target.name}에게 부식성 맹독이 스며들었습니다! (독성: {poison_intensity})")
            
            # 독 피해량이 방어력 감소에 비례하여 증가
            if hasattr(target, 'temp_effects'):
                target.temp_effects["poison_amplify"] = target.temp_effects.get("poison_amplify", 0) + 0.3
        else:
            print(f"☠️ 부식성 맹독이 {target.name}의 방어력을 녹여냅니다!")
        return True
    except Exception as e:
        print(f"부식성 독 효과 적용 중 오류: {e}")
        return False

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
    """강화 독무 효과 - 광역 독무로 여러 적에게 독과 디버프 부여"""
    try:
        print(f"🌫️ {caster.name}이 강화된 독무를 전개합니다!")
        
        # 주 대상에게 강력한 독 효과
        if target and hasattr(target, 'add_status'):
            target.add_status(StatusType.POISON, duration=8, power=2.0)
            target.add_status(StatusType.BLIND, duration=5, power=0.8)
            target.add_status(StatusType.WEAKNESS, duration=6, power=0.6)
            print(f"☠️ {target.name}이 독무의 중심에 휩싸였습니다!")
        
        # 주변 적들에게도 독무 확산
        try:
            import random
            # 전투 중인 다른 적들 찾기
            if hasattr(caster, 'combat_manager') and caster.combat_manager:
                enemies = getattr(caster.combat_manager, 'enemies', [])
            elif hasattr(target, 'combat_manager') and target.combat_manager:
                enemies = getattr(target.combat_manager, 'enemies', [])
            else:
                enemies = []
            
            fog_victims = 0
            for enemy in enemies:
                if enemy != target and hasattr(enemy, 'add_status'):
                    # 70% 확률로 독무에 휩쓸림
                    if random.random() < 0.7:
                        enemy.add_status(StatusType.POISON, duration=5, power=1.2)
                        enemy.add_status(StatusType.BLIND, duration=3, power=0.5)
                        fog_victims += 1
            
            if fog_victims > 0:
                print(f"🌪️ {fog_victims}명의 적이 독무에 휩쓸렸습니다!")
            
        except Exception as fog_error:
            print(f"독무 확산 중 오류: {fog_error}")
        
        return True
    except Exception as e:
        print(f"강화 독무 효과 적용 중 오류: {e}")
        return False

def _venom_explosion(caster, target, skill_data):
    """베놈 익스플로전 - 모든 독을 폭발시켜 즉시 피해"""
    try:
        if not target or not hasattr(target, 'status_effects'):
            return False
            
        total_explosion_damage = 0
        poison_effects_to_remove = []
        
        for effect in target.status_effects:
            if hasattr(effect, 'type') and effect.type == StatusType.POISON:
                # 독 폭발 피해 계산 (지속시간 × 강도 × 15)
                explosion_damage = int(effect.duration * effect.intensity * 15)
                total_explosion_damage += explosion_damage
                poison_effects_to_remove.append(effect)
        
        # 독 효과 제거
        for effect in poison_effects_to_remove:
            if effect in target.status_effects:
                target.status_effects.remove(effect)
        
        # 폭발 효과 (독 개수에 따른 디버프 효과)
        if poison_effects_to_remove:
            poison_count = len(poison_effects_to_remove)
            print(f"💥 베놈 익스플로전! {poison_count}개의 독이 폭발!")
            
            # 독 개수에 따른 상태이상 부여
            if hasattr(target, 'add_status'):
                if poison_count >= 3:
                    target.add_status(StatusType.STUN, duration=2, power=1.0)
                    print(f"😵 독 폭발로 기절!")
                elif poison_count >= 2:
                    target.add_status(StatusType.WEAKNESS, duration=4, power=0.7)
                    print(f"💔 독 폭발로 약화!")
                else:
                    target.add_status(StatusType.SLOW, duration=3, power=0.5)
                    print(f"🌫️ 독 폭발로 둔화!")

            # 추가 효과: 주변 적들에게 독 확산 (30% 확률)
            import random
            if random.random() < 0.3:
                print(f"🌪️ 독이 주변으로 확산됩니다!")
                
                # 주변 적들에게 독 확산 로직
                try:
                    # brave_combat에서 현재 전투 중인 적들을 가져오기 시도
                    if hasattr(caster, 'combat_manager') and caster.combat_manager:
                        enemies = getattr(caster.combat_manager, 'enemies', [])
                    elif hasattr(target, 'combat_manager') and target.combat_manager:
                        enemies = getattr(target.combat_manager, 'enemies', [])
                    else:
                        # 전역에서 현재 전투 매니저 찾기
                        import sys
                        current_module = sys.modules.get(__name__)
                        if hasattr(current_module, 'current_combat') and current_module.current_combat:
                            enemies = getattr(current_module.current_combat, 'enemies', [])
                        else:
                            enemies = []
                    
                    poison_spread_count = 0
                    for enemy in enemies:
                        if enemy != target and hasattr(enemy, 'add_status'):
                            # 30% 확률로 각 적에게 독 확산
                            if random.random() < 0.3:
                                enemy.add_status(StatusType.POISON, duration=3, power=0.8)
                                poison_spread_count += 1
                    
                    if poison_spread_count > 0:
                        print(f"☠️ {poison_spread_count}명의 적에게 독이 확산되었습니다!")
                    else:
                        print(f"💨 독 확산 대상이 없습니다.")
                        
                except Exception as spread_error:
                    print(f"독 확산 중 오류: {spread_error}")
                    # 간단한 확산 효과라도 적용
                    print(f"🌫️ 독성 가스가 전장에 퍼졌습니다!")
        else:
            print(f"💨 {target.name}에게 폭발시킬 독이 없습니다.")
        
        return True
    except Exception as e:
        print(f"베놈 익스플로전 효과 적용 중 오류: {e}")
        return False

def _poison_emperor(caster, target, skill_data):
    """독왕강림 - 전체 적의 독을 폭발시키고 강력한 독 재부여"""
    try:
        if not target or not hasattr(target, 'status_effects'):
            return False
            
        total_emperor_damage = 0
        poison_count = 0
        
        for effect in target.status_effects[:]:  # 복사본 순회
            if hasattr(effect, 'type') and effect.type == StatusType.POISON:
                # 독왕 폭발 피해 (지속시간 × 강도 × 25)
                emperor_damage = int(effect.duration * effect.intensity * 25)
                total_emperor_damage += emperor_damage
                poison_count += 1
                target.status_effects.remove(effect)
        
        if total_emperor_damage > 0:
            if hasattr(target, 'take_damage'):
                target.take_damage(total_emperor_damage)
            else:
                target.current_hp = max(0, target.current_hp - total_emperor_damage)
            print(f"👑 독왕의 힘으로 {target.name}에게 {total_emperor_damage}의 피해!")
        
        # 독왕의 저주 - 매우 강력한 독 부여
        if hasattr(target, 'add_status'):
            target.add_status(StatusType.POISON, duration=12, power=3.0)
            target.add_status(StatusType.CURSE, duration=8, power=2.0)
            
            # 독 개수에 따른 추가 효과
            if poison_count >= 2:
                target.add_status(StatusType.WEAKNESS, duration=6, power=1.5)
                print(f"💀 {target.name}이 독왕의 저주에 걸렸습니다!")
        
        return True
    except Exception as e:
        print(f"독왕강림 효과 적용 중 오류: {e}")
        return False

# ========================================
# 도적 기존 효과들 (업데이트됨)
# ========================================

def _stealth_attack(caster, target, skill_data):
    """은신 공격"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.STEALTH, duration=2, power=1.0)
    return True

def _smoke_screen(caster):
    """연막탄 효과"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_DODGE, duration=4, power=1.5)
    return True

def _poison_fog(caster, target):
    """독무 효과 (기존 - 호환성 유지)"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.POISON, duration=5, power=2.0)
    return True

def _poison_blade(caster, target, skill_data):
    """독날 투척"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.POISON, duration=4, power=1.5)
        target.add_status(StatusType.REDUCE_DEF, duration=3, power=0.8)
    return True

def _poison_mastery(caster, target, skill_data):
    """독왕의 비의 (기존 - 호환성 유지)"""
    if hasattr(target, 'add_status'):
        # 강력한 독 + 즉사 확률
        target.add_status(StatusType.POISON, duration=10, power=3.0)
        target.add_status(StatusType.NECROSIS, duration=5, power=2.0)
    return True

# ========================================
# 도적 고급 독 시스템 특수 효과들
# ========================================

def _toxic_cocktail(caster, target, skill_data):
    """독성 칵테일 - 다양한 독 효과를 한번에 부여"""
    try:
        if not target or not hasattr(target, 'add_status'):
            return False
            
        print(f"🧪 {caster.name}이 독성 칵테일을 투척합니다!")
        
        # 기본 독
        target.add_status(StatusType.POISON, duration=6, power=1.5)
        
        # 부식성 독 (방어력 감소)
        target.add_status(StatusType.REDUCE_DEF, duration=8, power=0.7)
        
        # 신경독 (속도 감소)
        target.add_status(StatusType.SLOW, duration=5, power=0.6)
        
        # 마비독 (행동 불가 확률)
        import random
        if random.random() < 0.3:
            target.add_status(StatusType.STUN, duration=2, power=1.0)
            print(f"💫 {target.name}이 마비독에 의해 마비되었습니다!")
        
        print(f"☠️ {target.name}에게 복합 독성 효과가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"독성 칵테일 효과 적용 중 오류: {e}")
        return False

def _poison_field(caster, target=None, skill_data=None):
    """독성 필드 - 전장에 독 지대 생성"""
    try:
        print(f"☠️ {caster.name}이 독성 필드를 전개합니다!")
        
        # 도적에게 독 필드 상태 부여 (5턴간 모든 공격에 독 효과)
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.POISON_FIELD, duration=5, power=1.0)
        
        # 모든 적에게 즉시 독 부여
        try:
            if hasattr(caster, 'combat_manager') and caster.combat_manager:
                enemies = getattr(caster.combat_manager, 'enemies', [])
            else:
                enemies = [target] if target else []
            
            field_victims = 0
            for enemy in enemies:
                if enemy and hasattr(enemy, 'add_status'):
                    enemy.add_status(StatusType.POISON, duration=4, power=1.0)
                    field_victims += 1
            
            if field_victims > 0:
                print(f"🌪️ {field_victims}명의 적이 독성 필드에 노출되었습니다!")
        
        except Exception as field_error:
            print(f"독성 필드 생성 중 오류: {field_error}")
        
        return True
    except Exception as e:
        print(f"독성 필드 효과 적용 중 오류: {e}")
        return False

def _plague_spread(caster, target, skill_data):
    """역병 확산 - 독에 걸린 적들끼리 서로 독을 전파"""
    try:
        if not target:
            return False
            
        print(f"🦠 {caster.name}이 역병을 확산시킵니다!")
        
        # 대상의 독 상태를 확인
        target_poison = None
        if hasattr(target, 'status_effects'):
            for effect in target.status_effects:
                if hasattr(effect, 'type') and effect.type == StatusType.POISON:
                    target_poison = effect
                    break
        
        if not target_poison:
            # 대상에게 독이 없으면 기본 독 부여
            if hasattr(target, 'add_status'):
                target.add_status(StatusType.POISON, duration=6, power=1.2)
                target_poison = True
        
        # 다른 적들에게 역병 전파
        if target_poison:
            try:
                if hasattr(caster, 'combat_manager') and caster.combat_manager:
                    enemies = getattr(caster.combat_manager, 'enemies', [])
                else:
                    enemies = []
                
                plague_victims = 0
                for enemy in enemies:
                    if enemy != target and hasattr(enemy, 'add_status'):
                        # 거리에 따른 전파 확률 (가까울수록 높음)
                        import random
                        spread_chance = 0.6  # 기본 60% 확률
                        
                        if random.random() < spread_chance:
                            # 전파된 독은 원본보다 강함
                            if target_poison and hasattr(target_poison, 'intensity'):
                                plague_intensity = min(target_poison.intensity * 1.2, 3.0)
                                plague_duration = max(target_poison.duration - 1, 3)
                            else:
                                plague_intensity = 1.5
                                plague_duration = 5
                            
                            enemy.add_status(StatusType.POISON, duration=plague_duration, power=plague_intensity)
                            plague_victims += 1
                
                if plague_victims > 0:
                    print(f"🦠 역병이 {plague_victims}명의 적에게 전파되었습니다!")
                else:
                    print(f"💨 역병 전파 대상이 없습니다.")
            
            except Exception as spread_error:
                print(f"역병 전파 중 오류: {spread_error}")
        
        return True
    except Exception as e:
        print(f"역병 확산 효과 적용 중 오류: {e}")
        return False

def _venom_burst(caster, target, skill_data):
    """독 폭발 - 도적 공격력 기반 베놈 익스플로전"""
    try:
        if not target:
            return False
        
        # 도적 공격력 기반 폭발 위력 계산
        caster_attack = getattr(caster, 'physical_attack', 100)
        # 공격력이 높을수록 폭발 피해 계수 증가
        explosion_multiplier = 8 + (caster_attack / 50.0)  # 기본 8 + 추가 계수
        explosion_multiplier = min(15, max(8, explosion_multiplier))  # 8~15배
            
        print(f"💥 {caster.name}이 맹독을 폭발시킵니다!")
        
        burst_damage = 0
        poison_found = False
        
        # 대상의 독 효과 확인
        if hasattr(target, 'status_effects'):
            for effect in target.status_effects[:]:
                if hasattr(effect, 'type') and effect.type == StatusType.POISON:
                    # 독 폭발 피해 계산 (도적 공격력 반영)
                    explosion_damage = int(effect.duration * effect.intensity * explosion_multiplier)
                    burst_damage += explosion_damage
                    poison_found = True
                    
                    # 축적된 독 데미지 양을 줄임 (지속시간과 강도 모두 감소)
                    effect.duration = max(1, effect.duration - 2)  # 지속시간 2턴 감소
                    effect.intensity = max(0.3, effect.intensity * 0.6)  # 강도 60%로 감소
        
        if burst_damage > 0:
            if hasattr(target, 'take_damage'):
                target.take_damage(burst_damage)
            else:
                target.current_hp = max(0, target.current_hp - burst_damage)
            print(f"💥 독 폭발로 {target.name}에게 {burst_damage} 피해!")
            print(f"🩹 {target.name}의 독 효과가 약화되었습니다!")
        elif not poison_found:
            # 독이 없으면 약한 독 부여
            if hasattr(target, 'add_status'):
                target.add_status(StatusType.POISON, duration=4, power=1.0)
                print(f"☠️ {target.name}에게 독을 부여했습니다!")
        
        return True
    except Exception as e:
        print(f"독 폭발 효과 적용 중 오류: {e}")
        return False

def _venom_absorption(caster, target=None, skill_data=None):
    """베놈 흡수 - 모든 적의 독을 흡수하여 보호막 생성"""
    try:
        print(f"🧬 {caster.name}이 독을 흡수합니다!")
        
        total_venom_absorbed = 0
        
        # 모든 적에서 독 흡수
        try:
            if hasattr(caster, 'combat_manager') and caster.combat_manager:
                enemies = getattr(caster.combat_manager, 'enemies', [])
            elif target:
                enemies = [target]
            else:
                enemies = []
            
            for enemy in enemies:
                if hasattr(enemy, 'status_effects'):
                    poison_effects_to_remove = []
                    
                    for effect in enemy.status_effects:
                        if hasattr(effect, 'type') and effect.type == StatusType.POISON:
                            # 흡수할 독 수치 계산 (지속시간 × 강도 × 2)
                            venom_value = int(effect.duration * effect.intensity * 2)
                            total_venom_absorbed += venom_value
                            poison_effects_to_remove.append(effect)
                    
                    # 독 효과 제거
                    for effect in poison_effects_to_remove:
                        if effect in enemy.status_effects:
                            enemy.status_effects.remove(effect)
                    
                    if poison_effects_to_remove:
                        print(f"☠️ {enemy.name}에서 독을 흡수했습니다!")
        
        except Exception as absorption_error:
            print(f"독 흡수 중 오류: {absorption_error}")
        
        # 흡수한 독 수치로 보호막 생성
        if total_venom_absorbed > 0:
            # 베놈 파워 축적 (표시용)
            venom_power_gain = max(1, total_venom_absorbed // 20)
            
            # 도적에게 베놈 파워 상태 추가/누적
            if not hasattr(caster, 'venom_power'):
                caster.venom_power = 0
            
            caster.venom_power += venom_power_gain

            # 최대 베놈 파워 제한 (200%)
            caster.venom_power = min(caster.venom_power, 200)
            
            # 베놈 보호막 생성 (흡수량의 60%)
            shield_value = max(30, total_venom_absorbed // 2)
            
            if hasattr(caster, 'add_status'):
                # 기존 베놈 보호막과 중첩
                existing_shield = 0
                for effect in getattr(caster, 'status_effects', []):
                    if hasattr(effect, 'type') and effect.type == StatusType.BARRIER:
                        existing_shield += getattr(effect, 'intensity', 0)
                        caster.status_effects.remove(effect)
                        break
                
                total_shield = shield_value + existing_shield
                caster.add_status(StatusType.BARRIER, duration=20, power=total_shield)
            
            print(f"🧬 독 흡수 완료! VENOM: {caster.venom_power}% (+{venom_power_gain})")
            print(f"🧬 베놈 보호막: {total_shield} 피해 흡수!")
        else:
            print(f"💨 흡수할 독이 없습니다.")
        
        return True
    except Exception as e:
        print(f"베놈 흡수 효과 적용 중 오류: {e}")
        return False

# ========================================
# 기계공학자 Special Effects
# ========================================

def _auto_turret_install(caster):
    """자동 포탑 설치"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.AUTO_TURRET, duration=3, power=1.0)
    return True

def _precision_laser(caster, target, skill_data):
    """정밀 레이저 - BRV 드레인 + 완벽한 명중률"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("perfect_accuracy", 1)
    
    # BRV 드레인 효과 추가
    if target and hasattr(target, 'current_brv') and hasattr(caster, 'current_brv'):
        target_brv = safe_get_brv_stat(target, 'current_brv', 0)
        drain_amount = min(target_brv * 0.15, 200)  # 대상 BRV의 15% 또는 최대 200
        if drain_amount > 0:
            target.current_brv = max(0, target.current_brv - drain_amount)
            caster.current_brv = min(getattr(caster, 'max_brv', 1000), getattr(caster, 'current_brv', 0) + drain_amount)
            print(f"⚡ {caster.name}의 정밀 레이저가 {target.name}의 BRV {drain_amount:.0f}을 흡수했습니다!")
    
    return True

def _repair_drone(caster, target):
    """수리 드론"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.REPAIR_DRONE, duration=3, power=1.0)
        target.add_status(StatusType.REGENERATION, duration=5, power=1.5)
    return True

def _multi_missile(caster, target, skill_data):
    """멀티 미사일"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("multi_hit", 3)  # 3발 동시 발사
    return True

def _giga_turret(caster, target, skill_data):
    """기가 포탑"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.AUTO_TURRET, duration=5, power=3.0)
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
        caster.add_status(StatusType.VAMPIRE, duration=3, power=1.0)
    return True

def _dispel_all(target):
    """모든 상태이상 해제"""
    if hasattr(target, 'clear_all_status'):
        target.clear_all_status()
    return True

def _analyze_enemy(caster, target):
    """적 분석"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.ANALYZE, duration=999, power=1.0)
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
        target.add_status(StatusType.STUN, duration=2, power=1.0)
        target.add_status(StatusType.REDUCE_ATK, duration=4, power=0.7)
    return True

def _sword_unity(caster):
    """검심일체"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ATK, duration=5, power=1.5)
        caster.add_status(StatusType.BOOST_CRIT, duration=5, power=2.0)
        caster.add_status(StatusType.BOOST_ACCURACY, duration=5, power=1.8)
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
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=3, power=2.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, power=0.5)
    return True

# ========================================
# 검투사 Special Effects
# ========================================

def _gladiator_honor(caster):
    """검투사의 명예"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ATK, duration=4, power=1.3)
        caster.add_status(StatusType.BOOST_DEF, duration=4, power=1.3)
        caster.add_status(StatusType.REGENERATION, duration=5, power=1.0)
    return True

def _colosseum_king(caster, target, skill_data):
    """콜로세움의 왕"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, power=1.5)
        caster.add_status(StatusType.VAMPIRE, duration=5, power=1.0)
    return True

# ========================================
# 광전사 Special Effects
# ========================================

def _rage_seed(caster):
    """분노의 씨앗"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.RAGE, duration=10, power=1.2)
        caster.add_status(StatusType.BOOST_ATK, duration=10, power=1.3)
    return True

def _blood_thirst(caster, target, skill_data):
    """피에 굶주린"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.VAMPIRE, duration=5, power=2.0)
        caster.add_status(StatusType.BOOST_ATK, duration=5, power=1.4)
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
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=3, power=3.0)
        caster.add_status(StatusType.TEMPORARY_INVINCIBLE, duration=1, power=1.0)
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
        caster.add_status(StatusType.BOOST_DEF, duration=5, power=1.5)
        caster.add_status(StatusType.BOOST_MAGIC_DEF, duration=5, power=1.5)
        caster.add_status(StatusType.TAUNT, duration=3, power=1.0)
    return True

def _holy_strike(caster, target, skill_data):
    """성스러운 일격"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.HOLY_MARK, duration=5, power=1.0)
        target.add_status(StatusType.REDUCE_MAGIC_DEF, duration=3, power=0.7)
    return True

def _holy_heal(caster, target):
    """성스러운 치유"""
    if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
        target_max_hp = safe_get_hp_stat(target, 'max_hp', 1000)
        heal_amount = int(target_max_hp * 0.5)
        target.current_hp = min(target_max_hp, getattr(target, 'current_hp', 0) + heal_amount)
        if hasattr(target, 'add_status'):
            target.add_status(StatusType.REGENERATION, duration=5, power=2.0)
    return True

def _angel_descent(caster, target, skill_data):
    """천사 강림"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, power=1.8)
        caster.add_status(StatusType.HOLY_AURA, duration=5, power=1.0)
    return True

# ========================================
# 다크나이트 Special Effects
# ========================================

def _dark_pact(caster, target, skill_data):
    """어둠의 계약"""
    if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
        caster_max_hp = safe_get_hp_stat(caster, 'max_hp', 1000)
        sacrifice_hp = int(caster_max_hp * 0.2)
        caster.current_hp = max(1, getattr(caster, 'current_hp', caster_max_hp) - sacrifice_hp)
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_ATK, duration=5, power=2.0)
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, power=2.0)
    return True

def _vampire_strike(caster, target, skill_data):
    """흡혈 공격"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.VAMPIRE, duration=5, power=3.0)
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.WEAKNESS, duration=3, power=0.8)
    return True

def _dark_domination(caster, target, skill_data):
    """어둠의 지배"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.CHARM, duration=3, power=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, power=0.6)
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
        caster.add_status(StatusType.DRAGON_FORM, duration=5, power=1.0)
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, power=2.0)
        caster.add_status(StatusType.ELEMENTAL_IMMUNITY, duration=5, power=1.0)
    return True

# ========================================
# 원소술사 Special Effects
# ========================================

def _earth_rage(caster, target, skill_data):
    """대지의 분노"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.ENTANGLE, duration=3, power=1.0)
        target.add_status(StatusType.REDUCE_SPEED, duration=5, power=0.5)
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("elemental_damage", "earth")
    return True

def _four_elements(caster, target, skill_data):
    """사원소 융합"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.BURN, duration=4, power=1.5)
        target.add_status(StatusType.FREEZE, duration=2, power=1.0)
        target.add_status(StatusType.SHOCK, duration=4, power=1.5)
        target.add_status(StatusType.ENTANGLE, duration=3, power=1.0)
    return True

# ========================================
# 시공술사 Special Effects
# ========================================

def _time_record_savepoint(caster, target=None, skill_data=None):
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
        
        print(f"⏰ {caster.name}이(가) 시간 기록점을 생성했습니다! (스택: {getattr(caster, 'time_rewind_stacks', 1)})")
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.TIME_SAVEPOINT, duration=999, power=1.0)
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
        caster.add_status(StatusType.FORESIGHT, duration=5, power=1.0)
        caster.add_status(StatusType.BOOST_DODGE, duration=5, power=2.0)
        caster.add_status(StatusType.BOOST_CRIT, duration=5, power=1.5)
    return True

def _time_stop(caster):
    """시간 정지 - 시간술사 특성 연동"""
    # 시간술사 특성: 시간 제어로 효과 강화
    if hasattr(caster, 'character_class') and caster.character_class == "시간술사":
        # 시간술사는 더 긴 지속시간과 추가 효과
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.TIME_STOP, duration=3, power=1.0)  # 1턴 더 길게
            caster.add_status(StatusType.EXTRA_TURN, duration=1, power=4.0)  # 추가 행동 1회 더
            caster.add_status(StatusType.BOOST_ALL_STATS, duration=3, power=1.3)  # 모든 스탯 30% 증가
        
        # 시간 감각으로 미래시 효과 추가
        if hasattr(caster, 'temp_crit_resistance'):
            caster.temp_crit_resistance = getattr(caster, 'temp_crit_resistance', 0) + 0.5
        else:
            caster.temp_crit_resistance = 0.5
    else:
        # 일반적인 시간 정지 효과
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.TIME_STOP, duration=2, power=1.0)
            caster.add_status(StatusType.EXTRA_TURN, duration=1, power=3.0)
    return True

def _spacetime_collapse(caster, target, skill_data):
    """시공붕괴"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.TIME_DISTORTION, duration=5, power=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, power=0.3)
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
        caster.add_status(StatusType.STEALTH, duration=3, power=1.0)
        caster.add_status(StatusType.BOOST_DODGE, duration=5, power=3.0)
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
        caster.add_status(StatusType.AFTERIMAGE, duration=4, power=1.0)
        caster.add_status(StatusType.BOOST_SPD, duration=4, power=2.0)
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
        target.add_status(StatusType.CONFUSION, duration=4, power=1.0)
        target.add_status(StatusType.REDUCE_ACCURACY, duration=5, power=0.5)
    return True

def _evasion_counter(caster, target, skill_data):
    """회피 반격"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.EVASION_UP, duration=3, power=2.0)
        caster.add_status(StatusType.COUNTER_ATTACK, duration=3, power=1.5)
    return True

def _untouchable_state(caster):
    """무적 상태"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.ABSOLUTE_EVASION, duration=2, power=1.0)
        caster.add_status(StatusType.TEMPORARY_INVINCIBLE, duration=1, power=1.0)
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
            target.add_status(StatusType.ANALYZE, duration=999, power=2.0 * analyze_bonus)
            target.add_status(StatusType.WEAKNESS_EXPOSURE, duration=5, power=1.0 * analyze_bonus)
    else:
        if hasattr(target, 'add_status'):
            target.add_status(StatusType.ANALYZE, duration=999, power=2.0)
            target.add_status(StatusType.WEAKNESS_EXPOSURE, duration=5, power=1.0)
    return True

def _existence_denial(caster, target, skill_data):
    """존재 부정"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.EXISTENCE_DENIAL, duration=3, power=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, power=0.4)
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
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, power=magic_boost)
            caster.add_status(StatusType.MANA_REGENERATION, duration=5, power=2.0)
            caster.add_status(StatusType.WISDOM, duration=5, power=1.0)
    else:
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, power=2.0)
            caster.add_status(StatusType.MANA_REGENERATION, duration=5, power=2.0)
            caster.add_status(StatusType.WISDOM, duration=5, power=1.0)
    return True

def _absolute_truth(caster, target, skill_data):
    """절대 진리"""
    if hasattr(caster, 'add_temp_effect'):
        caster.add_temp_effect("ignore_all_resistance", 1)
        caster.add_temp_effect("damage_multiplier", 3.0)
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.TRUTH_REVELATION, duration=999, power=1.0)
    return True

# ========================================
# 해적 Special Effects
# ========================================

def _ghost_fleet(caster, target, skill_data):
    """유령 함대"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.GHOST_FLEET, duration=5, power=1.0)
        caster.add_status(StatusType.BOOST_ATK, duration=5, power=1.5)
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
        target.add_status(StatusType.BOOST_ALL_STATS, duration=5, power=1.3)
        target.add_status(StatusType.REGENERATION, duration=5, power=1.5)
        target.add_status(StatusType.MANA_REGENERATION, duration=5, power=1.5)
    return True

def _heavenly_chorus(caster, target, skill_data=None):
    """천상의 합창 - 바드 궁극기"""
    try:
        if target and hasattr(target, 'add_status'):
            # 강력한 버프 효과
            target.add_status(StatusType.BOOST_ALL_STATS, duration=8, power=1.5)
            target.add_status(StatusType.HOLY_BLESSING, duration=8, power=1.0)
            
            # 바드의 멜로디 스택 활용
            if hasattr(caster, 'character_class') and caster.character_class == "바드":
                melody_stacks = getattr(caster, 'melody_stacks', 0)
                if melody_stacks > 0:
                    # 멜로디 스택에 비례한 추가 효과
                    bonus_duration = melody_stacks // 2
                    if hasattr(target, 'add_status'):
                        target.add_status(StatusType.REGENERATION, duration=5 + bonus_duration, power=2.0)
                    
                    # 멜로디 스택 소모
                    caster.melody_stacks = 0
                    print(f"🎵 천상의 합창! {melody_stacks}개 멜로디로 강화된 효과!")
                else:
                    print(f"🎵 천상의 합창! 신성한 치유와 버프!")
            else:
                print(f"🎵 천상의 합창! 모든 능력치 강화!")
        
        return True
    except Exception as e:
        print(f"천상의 합창 효과 적용 중 오류: {e}")
        return False

# ========================================
# 동물조련사 Special Effects
# ========================================

def _soul_analysis(caster, target):
    """영혼 분석 - 적의 약점과 상태를 파악"""
    try:
        if target and hasattr(target, 'status_manager') and target.status_manager:
            # 적에게 영혼 결속과 분석 효과 부여
            from game.status_effects import StatusType
            target.status_manager.add_status(StatusType.SOUL_BOND, 999, 1.0)  # 영혼 결속 (받는 피해 증가)
            target.status_manager.add_status(StatusType.ANALYZE, 999, 1.5)    # 분석됨 (크리티컬 확률 증가)
            print(f"🔮 {caster.name}이 {target.name}의 영혼을 파악했습니다!")
            print(f"   📍 약점 분석 완료 - 받는 피해 증가, 크리티컬 확률 증가")
        elif target and hasattr(target, 'add_status'):
            target.add_status('영혼결속', 999, 1.0)
            target.add_status('분석됨', 999, 1.5)
            print(f"🔮 {caster.name}이 {target.name}의 영혼을 파악했습니다!")
        else:
            print(f"🔮 {caster.name}이 적의 영혼 상태를 분석합니다!")
        return True
    except Exception as e:
        print(f"영혼 분석 중 오류: {e}")
        return False

def _nature_judgment(caster, target, skill_data):
    """자연의 심판"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.NATURE_CURSE, duration=5, power=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, power=0.7)
    return True

def _animal_form(caster):
    """동물 변신"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.ANIMAL_FORM, duration=5, power=1.0)
        caster.add_status(StatusType.BOOST_SPD, duration=5, power=2.0)
        caster.add_status(StatusType.BOOST_ATK, duration=5, power=1.5)
    return True

def _lightning_storm(caster, target, skill_data):
    """번개 폭풍"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.SHOCK, duration=5, power=2.0)
        target.add_status(StatusType.STUN, duration=2, power=1.0)
    return True

def _gaia_wrath(caster, target, skill_data):
    """가이아의 분노"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.NATURE_CURSE, duration=8, power=2.0)
        target.add_status(StatusType.ENTANGLE, duration=4, power=1.0)
        target.add_status(StatusType.POISON, duration=6, power=1.5)
    return True

# ========================================
# 성직자 Special Effects
# ========================================

def _holy_light(caster, target, skill_data):
    """성스러운 빛"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.HOLY_MARK, duration=5, power=1.0)
        target.add_status(StatusType.REDUCE_MAGIC_DEF, duration=5, power=0.6)
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
        target.add_status(StatusType.DIVINE_PUNISHMENT, duration=5, power=1.0)
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=5, power=0.5)
    return True

def _heaven_gate(caster, target, skill_data):
    """천국의 문"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.HEAVEN_GATE, duration=3, power=1.0)
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, power=2.0)
    return True

# ========================================
# 순교자 Special Effects
# ========================================

def _purify_light(caster, target):
    """정화의 빛"""
    if hasattr(target, 'clear_all_negative_status'):
        target.clear_all_negative_status()
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.PURIFICATION, duration=5, power=1.0)
    return True

def _martyrdom_path(caster):
    """순교의 길"""
    if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
        sacrifice_ratio = 0.5
        sacrifice_hp = int(caster.max_hp * sacrifice_ratio)
        caster.current_hp = max(1, caster.current_hp - sacrifice_hp)
        if hasattr(caster, 'add_status'):
            power_boost = 2.0 + sacrifice_ratio
            caster.add_status(StatusType.MARTYRDOM, duration=3, power=power_boost)
    return True

def _divine_judgment(caster, target, skill_data):
    """신의 심판"""
    if hasattr(target, 'add_status'):
        target.add_status(StatusType.DIVINE_JUDGMENT, duration=3, power=1.0)
        target.add_status(StatusType.HOLY_WEAKNESS, duration=5, power=2.0)
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
        caster.add_status(StatusType.ENLIGHTENMENT, duration=5, power=1.0)
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, power=1.5)
        caster.add_status(StatusType.MANA_REGENERATION, duration=10, power=2.0)
    return True

# ========================================
# 연금술사 Special Effects
# ========================================

def _elemental_weapon(caster, skill_data):
    """원소 무기"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.ELEMENTAL_WEAPON, duration=5, power=1.0)
        caster.add_status(StatusType.BOOST_ATK, duration=5, power=1.3)
    return True

def _magic_field(caster):
    """마법 진영"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.MAGIC_FIELD, duration=5, power=1.0)
        caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, power=1.5)
        caster.add_status(StatusType.MANA_REGENERATION, duration=5, power=1.5)
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
        caster.add_status(StatusType.TRANSMUTATION, duration=1, power=1.0)
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
        target.add_status(StatusType.CORROSION, duration=5, power=1.0)
        target.add_status(StatusType.REDUCE_DEF, duration=5, power=0.5)
        target.add_status(StatusType.REDUCE_MAGIC_DEF, duration=5, power=0.5)
    return True

def _philosophers_stone(caster):
    """현자의 돌"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.PHILOSOPHERS_STONE, duration=3, power=1.0)
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=5, power=1.8)
        caster.add_status(StatusType.MANA_INFINITE, duration=3, power=1.0)
    return True

# ========================================
# 네크로맨서 Special Effects
# ========================================

def _summon_undead(caster):
    """언데드 소환"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.UNDEAD_MINION, duration=10, power=1.0)
        caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=5, power=1.3)
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
        caster.add_status(StatusType.STEALTH, duration=3, power=1.0)
        caster.add_status(StatusType.BOOST_DODGE, duration=5, power=2.0)
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
        caster.add_status(StatusType.SHADOW_CLONE, duration=4, power=1.0)

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
        # ATB_READY_THRESHOLD 사용 (1000)
        max_atb = 1000  # BraveCombatSystem.ATB_READY_THRESHOLD
        refund_amount = int(max_atb * refund_rate)
        caster.atb_gauge = min(max_atb, caster.atb_gauge + refund_amount)
        print(f"⏱️ ATB 게이지 {int(refund_rate*100)}% 환급!")

def _atb_refund_medium(caster, skill_data):
    """ATB 게이지 30% 환급"""
    if hasattr(caster, 'atb_gauge'):
        # ATB_READY_THRESHOLD 사용 (1000)
        max_atb = 1000  # BraveCombatSystem.ATB_READY_THRESHOLD
        refund_amount = int(max_atb * 0.3)
        caster.atb_gauge = min(max_atb, caster.atb_gauge + refund_amount)
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
                    caster.add_status(StatusType.COUNTER, duration=extended_duration, power=1.0)
                else:
                    caster.add_status(StatusType.COUNTER, duration=base_duration, power=1.0)
            else:
                caster.add_status(StatusType.COUNTER, duration=base_duration, power=1.0)
        else:
            caster.add_status(StatusType.COUNTER, duration=base_duration, power=1.0)
            
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
        caster_max_mp = getattr(caster, 'max_mp', 100)
        caster_max_hp = safe_get_hp_stat(caster, 'max_hp', 1000)
        
        mp_heal = int(caster_max_mp * 0.15)
        hp_heal = int(caster_max_hp * 0.1)
        
        caster.mp = min(caster_max_mp, getattr(caster, 'mp', 0) + mp_heal)
        caster.hp = min(caster_max_hp, getattr(caster, 'hp', 0) + hp_heal)
        print(f"🗣️ 함성으로 MP {mp_heal}, HP {hp_heal} 회복!")

def _survival_spirit(caster, target, skill_data):
    """생존자의 투혼 - 처치 시 회복"""
    print(f"💀 생존 의지로 강화된 공격!")

# === 광전사 Special Effects ===
def _berserk_strike(caster, target, skill_data):
    """광폭화 난타 - HP 소모하여 강화"""
    if hasattr(caster, 'current_hp') and skill_data and 'hp_sacrifice' in skill_data:
        sacrifice = skill_data['hp_sacrifice']
        if caster.current_hp > sacrifice:
            caster.current_hp -= sacrifice
            # 소모한 HP에 따라 위력 증가
            bonus_power = sacrifice * 2
            print(f"🩸 HP {sacrifice} 소모하여 위력 +{bonus_power}!")
            return bonus_power
    elif hasattr(caster, 'hp') and skill_data and 'hp_sacrifice' in skill_data:
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
    if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
        hp_ratio = caster.current_hp / caster.max_hp
        vampire_rate = 0.3 + (0.3 * (1 - hp_ratio))  # 최대 60% 흡혈
        print(f"🧛 흡혈 효과 {int(vampire_rate*100)}% 발동!")
        return vampire_rate
    elif hasattr(caster, 'hp') and hasattr(caster, 'max_hp'):
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
        print("💀 HP가 부족하여 피의 방패를 사용할 수 없습니다!")
        return False

def _blood_max_hp_boost(caster, skill_data):
    """피의 방패 추가 효과 - 소모한 HP의 20%만큼 최대 HP 증가 (5턴)"""
    # 현재 HP 확인
    current_hp = getattr(caster, 'current_hp', getattr(caster, 'hp', 100))
    max_hp = getattr(caster, 'max_hp', 1000)
    
    # 방금 전 소모한 HP의 50% 계산
    sacrifice_hp = int((current_hp / 0.5) * 0.5)  # 역산으로 소모량 계산
    
    # 소모량의 20%만큼 최대 HP 증가
    max_hp_boost = int(sacrifice_hp * 0.2)
    
    # 최대 HP 증가 상태 저장
    if not hasattr(caster, 'blood_max_hp_boost'):
        caster.blood_max_hp_boost = 0
    if not hasattr(caster, 'blood_max_hp_boost_turns'):
        caster.blood_max_hp_boost_turns = 0
    
    caster.blood_max_hp_boost += max_hp_boost
    caster.blood_max_hp_boost_turns = 5  # 5턴 지속
    
    # 실제 최대 HP 증가 적용
    if hasattr(caster, 'max_hp'):
        caster.max_hp += max_hp_boost
    
    print(f"💪 피의 광기로 최대 HP가 {max_hp_boost} 증가했습니다! (5턴 지속)")
    return True

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
    if hasattr(caster, 'current_hp'):
        sacrificed_hp = caster.current_hp - 1
        caster.current_hp = 1
        # 소모한 HP에 따라 엄청난 피해
        massive_damage = sacrificed_hp * 3
        print(f"💀 최후의 광기! HP {sacrificed_hp} 소모하여 피해 {massive_damage}!")
        print(f"💀 {caster.name}의 HP가 1이 되었습니다!")
        return massive_damage
    elif hasattr(caster, 'hp'):
        sacrificed_hp = caster.hp - 1
        caster.hp = 1
        # 소모한 HP에 따라 엄청난 피해
        massive_damage = sacrificed_hp * 3
        print(f"💀 최후의 광기! HP {sacrificed_hp} 소모하여 피해 {massive_damage}!")
        print(f"💀 {caster.name}의 HP가 1이 되었습니다!")
        return massive_damage
    return 0

def _massive_vampire(caster, target, skill_data):
    """엄청난 흡혈"""
    print(f"🧛‍♂️ 엄청난 흡혈 효과 발동!")

# === 기사 Special Effects ===
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
    if not hasattr(caster, 'holy_count'):
        caster.holy_count = 0  # 처음에만 초기화
    
    caster.sanctuary_count += 1
    caster.holy_count = min(caster.holy_count + 1, 5)  # HOLY 게이지 증가 (최대 5)
    
    print(f"🌟 축복으로 성역 생성! (현재 성역: {caster.sanctuary_count}개, HOLY: {caster.holy_count}/5)")

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
        
        # 올바른 속성 사용 및 heal 메서드 활용
        if hasattr(caster, 'heal'):
            caster.heal(heal_amount)
            print(f"🧛 흡혈 강타! HP {heal_amount} 회복! (남은 흡수: {int(caster.absorption_stacks)})")
        elif hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
            caster.current_hp = min(caster.max_hp, caster.current_hp + heal_amount)
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
    try:
        if not hasattr(caster, 'element_counts'):
            caster.element_counts = {"fire": 0, "ice": 0, "lightning": 0}
        
        caster.element_counts["ice"] += 1
        count = caster.element_counts["ice"]
        
        print(f"❄️ {caster.name}이(가) 냉기 속성을 발동! (현재: {count}/3)")
        
        if count >= 3:
            caster.element_counts["ice"] = 0
            print(f"❄️ 냉기 3회 달성! '절대영도' 효과 발동!")
            
            # 절대영도 효과: 대상을 빙결시키거나 추가 피해
            if target and hasattr(target, 'status_manager'):
                try:
                    # 빙결 상태 효과 적용
                    if hasattr(target.status_manager, 'add_status'):
                        target.status_manager.add_status("freeze", duration=2, power=0)
                    elif hasattr(target.status_manager, 'apply_status'):
                        target.status_manager.apply_status("freeze", 2, 0)
                    print(f"❄️ {target.name}이(가) 2턴간 빙결되었습니다!")
                except Exception as e:
                    print(f"⚠️ 빙결 적용 실패: {e}")
                    # 빙결 실패 시 대신 추가 피해
                    if hasattr(target, 'current_hp'):
                        freeze_damage = int(getattr(target, 'max_hp', 100) * 0.1)
                        target.current_hp = max(0, target.current_hp - freeze_damage)
                        print(f"❄️ 대신 냉기 피해 {freeze_damage} 적용!")
            
            return True  # 특수 효과 발동됨
        
        return False
    except Exception as e:
        print(f"⚠️ ice_count 효과 처리 중 오류: {e}")
        return False

def _elemental_mastery(caster):
    """원소 강화"""
    print(f"🎭 원소 강화! 마법 공격력 증가 + 원소 친화도 상승!")

def _elemental_fusion(caster, target, skill_data):
    """원소 융합 (데미지는 스킬 정의에서 처리)"""
    try:
        fusion_bonus = 0
        
        # 원소 축적 확인
        if hasattr(caster, 'element_counts'):
            total_elements = sum(caster.element_counts.values())
            if total_elements >= 2:
                # 2개 이상의 원소가 있으면 융합 효과
                fusion_bonus = total_elements * 10  # 원소당 +10% 데미지 (스킬 시스템에서 적용)
                print(f"🌈 원소 융합! {total_elements}개 원소로 융합 보너스 +{fusion_bonus}%!")
                
                # 융합 후 원소 절반 소모
                for element in caster.element_counts:
                    caster.element_counts[element] = caster.element_counts[element] // 2
            else:
                print(f"🌈 원소 융합! 기본 위력으로 발동!")
        else:
            print(f"🌈 원소 융합! 모든 원소가 융합된 복합 공격!")
        
        return True
        
    except Exception as e:
        print(f"원소 융합 효과 적용 중 오류: {e}")
        return False

def _all_elements_burst(caster, target, skill_data):
    """원소 대폭발 (데미지는 스킬 정의에서 처리)"""
    try:
        if hasattr(caster, 'element_counts'):
            total_elements = sum(caster.element_counts.values())
            
            if total_elements > 0:
                # 축적된 원소 수에 따른 보너스 (스킬 시스템에서 적용됨)
                bonus_percentage = total_elements * 5  # 원소당 +5% 데미지
                
                # 모든 원소 소모
                caster.element_counts = {"fire": 0, "ice": 0, "lightning": 0}
                print(f"💥 원소 대폭발! 축적된 원소 {total_elements}개로 위력 +{bonus_percentage}%!")
                print(f"🌟 모든 원소가 한 번에 폭발합니다!")
            else:
                print(f"🌟 원소 대폭발! 기본 위력으로 발동!")
        else:
            print(f"🌟 원소 대폭발! 모든 속성 동시 발동!")
        
        return True
    
    except Exception as e:
        print(f"원소 대폭발 효과 적용 중 오류: {e}")
        return False

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
        caster.add_status(StatusType.TREASURE_HUNTER, duration=3, power=1.0)
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
        caster.add_status(StatusType.DUAL_WIELD, duration=3, power=1.0)
        caster.add_status(StatusType.BOOST_ATTACK_SPEED, duration=3, power=1.4)
    return True

def _sea_shanty(caster):
    """선원가 - 팀 버프"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.BOOST_ALL_STATS, duration=4, power=1.15)
        caster.add_status(StatusType.PIRATE_COURAGE, duration=4, power=1.0)
    return True

def _treasure_map(caster):
    """보물지도 효과"""
    if hasattr(caster, 'treasure_stacks'):
        caster.treasure_stacks = min(getattr(caster, 'treasure_stacks', 0) + 3, 5)
    else:
        caster.treasure_stacks = 3
    
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.TREASURE_HUNTER, duration=8, power=2.0)
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
        caster.add_status(StatusType.FOCUS, duration=3, power=1.0)
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
        caster.add_status(StatusType.BOOST_CRIT, duration=2, power=2.0)
    return True

def _honor_guard(caster):
    """명예 수호 자세"""
    if hasattr(caster, 'add_status'):
        caster.add_status(StatusType.GUARD_STANCE, duration=4, power=1.0)
        caster.add_status(StatusType.BOOST_DEF, duration=4, power=1.5)
        caster.add_status(StatusType.COUNTER_READY, duration=4, power=1.0)
    return True

# === 새로운 직업 기본 공격 Special Effects ===

def _nature_bond(caster, target=None, skill_data=None):
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
                caster.add_status(StatusType.BOOST_ATK, duration=2, power=1.3)
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
                caster.add_status(StatusType.ELEMENTAL_INFUSION, duration=3, power=1.0)
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
                caster.add_status(StatusType.BOOST_SPD, duration=2, power=1.2)
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
        
        # 최대 MP의 8% 회복으로 변경
        mp_recovery = int(caster.max_mp * 0.08)
        if mp_recovery > 0:
            caster.current_mp = min(caster.current_mp + mp_recovery, caster.max_mp)
            print(f"👻 영혼 에너지로 {mp_recovery} MP 회복! (최대 MP의 8%)")
    return True

def _precision_stack(caster):
    """조준 포인트 생성 - 궁수 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "궁수":
        # 조준 포인트 증가 전 상태 로그
        old_points = getattr(caster, 'aim_points', 0)
        print(f"🏹 [AIM LOG] {caster.name} - 조준 포인트 증가 전: {old_points}/5")
        
        # 조준 포인트 증가
        if hasattr(caster, 'aim_points'):
            caster.aim_points = min(caster.aim_points + 1, 5)
        else:
            caster.aim_points = 1
        
        # 조준 포인트 증가 후 상태 로그
        new_points = getattr(caster, 'aim_points', 0)
        print(f"🏹 [AIM LOG] {caster.name} - 조준 포인트 증가 후: {new_points}/5 (+{new_points - old_points})")
        print(f"🎯 [AIM LOG] 조준 포인트 +1! (현재: {caster.aim_points}/5)")
    else:
        print(f"🚫 [AIM LOG] {getattr(caster, 'name', 'Unknown')} - 궁수가 아니므로 조준 불가 (직업: {getattr(caster, 'character_class', 'Unknown')})")
    return True

def _arrow_penetration(caster):
    """화살 관통 - 궁수 기본 HP 공격 (조준 포인트 활용)"""
    if hasattr(caster, 'character_class') and caster.character_class == "궁수":
        # 조준 포인트에 따른 관통 효과
        aim_points = getattr(caster, 'aim_points', 0)
        if aim_points > 0:
            # 조준 포인트 사용하여 명중률, 치명타율 증가 (배율 방식)
            accuracy_multiplier = 1.0 + (aim_points * 0.08)  # 포인트당 +8% 명중률
            crit_multiplier = 1.0 + (aim_points * 0.12)  # 포인트당 +12% 치명타율
            
            caster.temp_accuracy_multiplier = getattr(caster, 'temp_accuracy_multiplier', 1.0) * accuracy_multiplier
            caster.temp_crit_multiplier = getattr(caster, 'temp_crit_multiplier', 1.0) * crit_multiplier
            
            accuracy_bonus = int((accuracy_multiplier - 1.0) * 100)
            crit_bonus = int((crit_multiplier - 1.0) * 100)
            
            print(f"🏹 조준 활용! 명중률 +{accuracy_bonus}%, 치명타 +{crit_bonus}%")
    return True

def _melody_build(caster):
    """멜로디 축적 - 바드 기본 BRV 공격"""
    
    if hasattr(caster, 'character_class') and caster.character_class == "바드":
        # melody_notes 배열에 새로운 음계 추가 (0~6: 도 레 미 파 솔 라 시)
        if not hasattr(caster, 'melody_notes'):
            caster.melody_notes = []
        
        old_melody_count = len(caster.melody_notes)
        
        if len(caster.melody_notes) < 7:
            new_note = len(caster.melody_notes)  # 순차적으로 음계 추가
            caster.melody_notes.append(new_note)
            
            # 멜로디 표시 업데이트
            if hasattr(caster, '_update_melody_display'):
                caster._update_melody_display()
        
        # melody_stacks도 호환성을 위해 업데이트
        if not hasattr(caster, 'melody_stacks'):
            caster.melody_stacks = 0
        caster.melody_stacks = len(caster.melody_notes)
        
        # 음계 이름 배열 (영어 대문자)
        notes = ["DO", "RE", "MI", "FA", "SO", "LA", "TI"]
        current_notes_str = "/".join([notes[note] for note in caster.melody_notes if 0 <= note < len(notes)])
        
        print(f"🎵 {caster.name}이(가) 멜로디를 쌓았습니다! 현재음계: {current_notes_str} ({len(caster.melody_notes)}/7)")
        
        # 멜로디 스택에 비례한 모든 아군 버프
        melody_count = len(caster.melody_notes)
        if melody_count >= 4:
            print(f"🎵 화음 완성! 아군 전체 능력치 소폭 증가!")
        
        if melody_count >= 7:
            print(f"🎵🎶 완전한 음계 완성! 모든 음표가 활성화되었습니다! 🎶🎵")
    else:
        print(f"⚠️ [DEBUG] 바드가 아닌 캐릭터가 melody_build 시도: {getattr(caster, 'character_class', 'Unknown')}")
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
                caster.add_status(StatusType.INSPIRE, duration=3, power=1.0)
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
                target.add_status(StatusType.POISON, duration=4 + consumed_stacks, power=1.0 + consumed_stacks * 0.2)
            print(f"💀 치명적 독! {consumed_stacks}스택 소모로 강화된 독 효과!")
    return True

def _generate_shadow(caster):
    """그림자 생성 - 암살자 기본 BRV 공격"""
    if hasattr(caster, 'character_class') and caster.character_class == "암살자":
        # 그림자 생성 전 상태 로그
        old_shadows = getattr(caster, 'shadow_count', 0)
        print(f"🌙 [SHADOW LOG] {caster.name} - 그림자 생성 전: {old_shadows}/5")
        
        # 그림자 스택 생성
        if hasattr(caster, 'shadow_count'):
            caster.shadow_count = min(caster.shadow_count + 1, 5)
        else:
            caster.shadow_count = 1
        
        # 그림자 생성 후 상태 로그
        new_shadows = getattr(caster, 'shadow_count', 0)
        print(f"🌙 [SHADOW LOG] {caster.name} - 그림자 생성 후: {new_shadows}/5 (+{new_shadows - old_shadows})")
        
        # 그림자 수에 비례한 회피율 증가 (배율 방식)
        shadow_count = getattr(caster, 'shadow_count', 0)
        evasion_multiplier = 1.0 + (shadow_count * 0.1)  # 그림자당 +10% 회피율
        caster.temp_evasion_multiplier = getattr(caster, 'temp_evasion_multiplier', 1.0) * evasion_multiplier
        print(f"🌙 [SHADOW LOG] 그림자 생성! 현재 {shadow_count}개 - 회피율 배율: {evasion_multiplier:.1f}x")
    else:
        print(f"🚫 [SHADOW LOG] {getattr(caster, 'name', 'Unknown')} - 암살자가 아니므로 그림자 생성 불가 (직업: {getattr(caster, 'character_class', 'Unknown')})")
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
    """분노 축적 - 광전사 기본 BRV 공격 (개선된 공격력 기반 시스템)"""
    if hasattr(caster, 'character_class') and caster.character_class == "광전사":
        # rage_stacks 사용으로 통일
        if not hasattr(caster, 'rage_stacks'):
            caster.rage_stacks = 0
        
        # 🔥 공격력 기반 최대 분노 스택 계산 (1~99999 범위)
        base_attack = getattr(caster, 'physical_attack', 100)
        max_rage_stacks = max(1, min(99999, base_attack * 50))  # 공격력 * 50, 최소 1, 최대 99999
        
        if not hasattr(caster, 'max_rage_stacks'):
            caster.max_rage_stacks = max_rage_stacks
        
        old_rage = caster.rage_stacks
        # 기본적으로 1스택 증가
        rage_increase = 1
        
        # 💥 최근 받은 피해가 있으면 추가 분노 획득 (1~99999 범위)
        if hasattr(caster, 'recent_damage_taken') and caster.recent_damage_taken > 0:
            # 받은 피해의 10%만큼 추가 분노 (최소 1, 최대 99999)
            damage_rage = max(1, min(99999, caster.recent_damage_taken // 10))
            rage_increase += damage_rage
            print(f"💢 받은 피해로 인한 추가 분노! +{damage_rage}")
            caster.recent_damage_taken = 0  # 초기화
        
        caster.rage_stacks = min(caster.rage_stacks + rage_increase, caster.max_rage_stacks)
        
        # 하위 호환성을 위한 기존 변수들도 업데이트
        caster.rage_meter = min(99999, caster.rage_stacks * 10)  # rage_meter = 스택 * 10
        caster.rage_count = caster.rage_stacks
        
        print(f"💢 {caster.name}이(가) 분노를 축적했습니다! (현재: {caster.rage_stacks}/{caster.max_rage_stacks})")
        
        # 🔥 분노에 비례한 공격력 증가 (더 강력하게)
        if caster.rage_stacks >= 5:
            # 분노 스택당 공격력의 2% 증가 (기존 1.5%에서 증가)
            attack_bonus_ratio = min(5.0, caster.rage_stacks * 0.02)  # 최대 500% 증가 제한
            attack_bonus = int(attack_bonus_ratio * base_attack)
            
            if hasattr(caster, 'temp_attack_bonus'):
                caster.temp_attack_bonus = getattr(caster, 'temp_attack_bonus', 0) + attack_bonus
            else:
                caster.temp_attack_bonus = attack_bonus
            print(f"💢 분노로 인한 공격력 증가! +{attack_bonus} ({attack_bonus_ratio*100:.1f}%)")
            
            # 🩸 높은 분노 시 체력 소모 (리스크)
            if caster.rage_stacks >= caster.max_rage_stacks * 0.8:  # 80% 이상일 때
                hp_cost = max(1, caster.max_hp // 50)  # 최대 체력의 2%
                caster.current_hp = max(1, caster.current_hp - hp_cost)
                print(f"💢 극한 분노로 체력 소모! -{hp_cost} HP")
                # 자체 피해도 분노에 축적
                track_berserker_damage(caster, hp_cost, is_self_damage=True)
    return True
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
        
        # HOLY 수치 증가 (UI 표시용)
        if hasattr(caster, 'holy_count'):
            caster.holy_count = min(caster.holy_count + 1, 10)
        else:
            caster.holy_count = 1
        
        # 성역 생성 (sanctuary_count 증가)
        if hasattr(caster, 'sanctuary_count'):
            caster.sanctuary_count = min(caster.sanctuary_count + 1, 5)
        else:
            caster.sanctuary_count = 1
        
        blessing = getattr(caster, 'blessing_points', 0)
        holy_count = getattr(caster, 'holy_count', 0)
        sanctuary = getattr(caster, 'sanctuary_count', 0)
        
        # 축복에 비례한 마법 방어력 증가
        if blessing >= 15:
            magic_defense_bonus = int(blessing * 0.015 * getattr(caster, 'magical_defense', 50))
            if hasattr(caster, 'temp_magic_defense_bonus'):
                caster.temp_magic_defense_bonus = getattr(caster, 'temp_magic_defense_bonus', 0) + magic_defense_bonus
            else:
                caster.temp_magic_defense_bonus = magic_defense_bonus
            print(f"✨ 성스러운 축복! HOLY: {holy_count}, 성역: {sanctuary}, 마법방어 +{magic_defense_bonus}")
        else:
            print(f"✨ 성스러운 축복! HOLY: {holy_count}, 성역: {sanctuary}")
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
    # print(f"🌟 스킬 '{effect_name}' 특수 효과 실행 완료!")
    return True

def _chemical_reaction_safe(caster, target, skill_data):
    """연금술사 화학 반응 (완전한 구현)"""
    if hasattr(caster, 'character_class') and caster.character_class == "연금술사":
        # 연금술 재료 스택 증가
        materials = getattr(caster, 'alchemy_materials', 0)
        setattr(caster, 'alchemy_materials', min(materials + 2, 10))
        
        if target and hasattr(target, 'take_damage'):
            # 연금술 재료에 비례한 화학 폭발 피해 (마법력 배율 증가)
            base_damage = int(getattr(caster, 'magic_attack', 50) * 0.4)
            material_multiplier = 1.0 + ((materials + 2) * 0.12)  # 재료당 +12% 마법력 배율
            total_damage = int(base_damage * material_multiplier)
            
            target.take_damage(total_damage)
            print(f"⚗️ 화학 반응! {total_damage} 폭발 피해 (재료: {materials + 2}, 배율: {material_multiplier:.1f}x)")
            
            # 확률적으로 상태이상 부여
            import random
            if random.random() < 0.3:
                if hasattr(target, 'add_status'):
                    target.add_status(StatusType.POISON, duration=3, power=1.0)
                    print(f"☠️ 독성 화학물질로 중독!")
    return True

def _dimension_rift_safe(caster, target, skill_data):
    """차원술사 차원 균열 (완전한 구현)"""
    if hasattr(caster, 'character_class') and caster.character_class == "차원술사":
        # 차원 에너지 스택 증가
        energy = getattr(caster, 'dimension_energy', 0)
        setattr(caster, 'dimension_energy', min(energy + 1, 8))
        
        if target and hasattr(target, 'take_damage'):
            # 차원 에너지에 비례한 공간 절단 피해 (마법력 배율 증가)
            base_damage = int(getattr(caster, 'magic_attack', 50) * 0.5)
            energy_multiplier = 1.0 + (energy * 0.15)  # 에너지당 +15% 마법력 배율
            total_damage = int(base_damage * energy_multiplier)
            
            target.take_damage(total_damage)
            print(f"🌌 차원 균열! {total_damage} 공간 피해 (에너지: {energy + 1}, 배율: {energy_multiplier:.1f}x)")
            
            # 공간 왜곡으로 혼란 상태
            if hasattr(target, 'add_status'):
                target.add_status(StatusType.CONFUSION, duration=2, power=1.0)
                print(f"🌀 공간 왜곡으로 혼란 상태!")
    return True

# ========================================
# 누락된 Special Effects 완전 구현
# ========================================

def _mana_burn(caster, target, skill_data):
    """마나 연소"""
    if target and hasattr(target, 'current_mp'):
        burn_amount = int(target.max_mp * 0.15)
        target.current_mp = max(0, target.current_mp - burn_amount)
        
        # 연소된 마나에 따른 추가 효과 (데미지는 스킬 정의에서 처리)
        if burn_amount > 0:
            bonus_percentage = burn_amount * 2  # 소모된 MP당 +2% 데미지
            print(f"🔥 마나 연소! MP {burn_amount} 소모로 추가 효과 +{bonus_percentage}%!")
        else:
            print(f"🔥 마나 연소 발동!")
    return True

def _armor_break(caster, target, skill_data):
    """방어구 파괴"""
    if target and hasattr(target, 'add_status'):
        # 방어력 대폭 감소
        target.add_status(StatusType.REDUCE_DEF, duration=5, power=0.4)
        
        # 물리 저항력도 감소
        target.add_status(StatusType.VULNERABILITY, duration=5, power=1.5)
        
        print(f"🔨 {target.name}의 방어구가 파괴되었습니다!")
    return True

def _critical_strike(caster, target, skill_data):
    """치명타 효과"""
    if hasattr(caster, 'add_status'):
        # 다음 공격이 확정 치명타
        caster.add_status(StatusType.BOOST_CRIT, duration=1, power=10.0)
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
        target.add_status(StatusType.STUN, duration=2, power=1.0)
        
        print(f"💫 {target.name}이(가) 기절했습니다!")
    return True

def _bleeding_attack(caster, target, skill_data):
    """출혈 공격"""
    if target and hasattr(target, 'add_status'):
        # 출혈 상태 부여
        target.add_status(StatusType.BLEEDING, duration=4, power=1.0)
        
        # 출혈 피해량 설정
        setattr(target, 'bleeding_damage', int(getattr(caster, 'physical_attack', 50) * 0.1))
        
        print(f"🩸 {target.name}이(가) 출혈 상태가 되었습니다!")
    return True

def _burn_attack(caster, target, skill_data):
    """화상 공격"""
    if target and hasattr(target, 'add_status'):
        # 화상 상태 부여
        target.add_status(StatusType.BURN, duration=4, power=1.0)
        
        # 화상 피해량 설정
        setattr(target, 'burn_damage', int(getattr(caster, 'magic_attack', 50) * 0.12))
        
        print(f"🔥 {target.name}이(가) 화상 상태가 되었습니다!")
    return True

def _freeze_attack(caster, target, skill_data):
    """빙결 공격"""
    if target and hasattr(target, 'add_status'):
        # 빙결 상태 부여 (행동 불가)
        target.add_status(StatusType.FREEZE, duration=2, power=1.0)
        
        # 속도 대폭 감소
        target.add_status(StatusType.REDUCE_SPEED, duration=4, power=0.3)
        
        print(f"❄️ {target.name}이(가) 빙결되었습니다!")
    return True

def _shock_attack(caster, target, skill_data):
    """감전 공격"""
    if target and hasattr(target, 'add_status'):
        # 감전 상태 부여
        target.add_status(StatusType.SHOCK, duration=3, power=1.0)
        
        # MP 지속 감소 효과
        setattr(target, 'shock_mp_drain', int(target.max_mp * 0.05))
        
        print(f"⚡ {target.name}이(가) 감전되었습니다!")
    return True

def _poison_attack(caster, target, skill_data):
    """독 공격"""
    if target and hasattr(target, 'add_status'):
        # 독 상태 부여
        target.add_status(StatusType.POISON, duration=5, power=1.0)
        
        # 독 피해량 설정
        setattr(target, 'poison_damage', int(getattr(caster, 'magic_attack', 50) * 0.08))
        
        print(f"☠️ {target.name}이(가) 중독되었습니다!")
    return True

def _confusion_attack(caster, target, skill_data):
    """혼란 공격"""
    if target and hasattr(target, 'add_status'):
        # 혼란 상태 부여
        target.add_status(StatusType.CONFUSION, duration=3, power=1.0)
        
        print(f"😵 {target.name}이(가) 혼란에 빠졌습니다!")
    return True

def _silence_attack(caster, target, skill_data):
    """침묵 공격"""
    if target and hasattr(target, 'add_status'):
        # 침묵 상태 부여 (스킬 사용 불가)
        target.add_status(StatusType.SILENCE, duration=3, power=1.0)
        
        print(f"🤐 {target.name}이(가) 침묵당했습니다!")
    return True

def _weakness_attack(caster, target, skill_data):
    """약화 공격"""
    if target and hasattr(target, 'add_status'):
        # 모든 능력치 감소
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=4, power=0.7)
        
        print(f"🔻 {target.name}의 능력이 약화되었습니다!")
    return True

def _curse_attack(caster, target, skill_data):
    """저주 공격"""
    if target and hasattr(target, 'add_status'):
        # 저주 상태 - 치유 효과 감소 + 지속 피해
        target.add_status(StatusType.CURSE, duration=6, power=1.0)
        
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

def _dark_energy(caster, target, skill_data):
    """어둠의 에너지 (데미지는 스킬 정의에서 처리)"""
    if target and hasattr(target, 'add_status'):
        # 어둠에 잠식 효과
        target.add_status(StatusType.REDUCE_ALL_STATS, duration=3, power=0.8)
        
        print(f"🌑 어둠의 에너지가 {target.name}을 잠식합니다!")
    return True

def _nature_power(caster, target, skill_data):
    """자연의 힘"""
    if hasattr(caster, 'character_class') and caster.character_class == "드루이드":
        # 자연 에너지 스택 증가
        nature = getattr(caster, 'nature_power', 0)
        setattr(caster, 'nature_power', min(nature + 2, 10))
        
        # 자연의 축복으로 능력치 증가
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_ALL_STATS, duration=3, power=1.2)
        
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
            caster.add_status(StatusType.BOOST_MAGIC_ATK, duration=4, power=1.1)
        
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
            print(f"🐎 창 돌격! 강력한 돌격으로 추가 효과!")
        
        # 다음 턴 속도 증가
        if hasattr(caster, 'add_status'):
            caster.add_status(StatusType.BOOST_SPEED, duration=2, power=1.3)
        
        print(f"🏇 기사도 정신 증가! (의무: {chivalry + 1})")
    return True

def _silence_effect(caster, target, skill_data):
    """침묵 효과 - 도적 전용"""
    if target and hasattr(target, 'add_status'):
        # 침묵 상태 부여 (스킬 사용 불가)
        target.add_status(StatusType.SILENCE, duration=3, power=1.0)
        
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
            caster.status_manager.add_status('정확도_증가', 3, 10)
        print(f"{caster.name}의 정확도가 증가했습니다!")
        return True
    except Exception as e:
        print(f"정확도 효과 적용 중 오류: {e}")
        return False

def _accuracy_boost(caster, target=None, skill_data=None):
    """정확도 대폭 증가 효과"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('정확도_증가', 5, 20)
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
            target.take_damage(penetration_damage, "관통 피해", True)
            print(f"{caster.name}의 공격이 {target.name}의 방어구를 관통했습니다!")
        return True
    except Exception as e:
        print(f"방어구 관통 효과 적용 중 오류: {e}")
        return False

def _berserk(caster, target=None, skill_data=None):
    """광폭화 상태"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('광폭화', 5, 50)  # 공격력 50% 증가, 5턴
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
            caster.status_manager.add_status('BRV_위력_증가', 3, 30)
        print(f"{caster.name}의 BRV 공격 위력이 증가했습니다!")
        return True
    except Exception as e:
        print(f"BRV 위력 효과 적용 중 오류: {e}")
        return False

def _combo_bonus(caster, target=None, skill_data=None):
    """콤보 보너스 효과 - 공격력 비례 배율 증가"""
    try:
        if hasattr(caster, 'combo_count'):
            caster.combo_count = getattr(caster, 'combo_count', 0) + 1
            # 콤보당 공격력 8% 증가 (배율 방식)
            caster.temp_combo_multiplier = getattr(caster, 'temp_combo_multiplier', 1.0) + 0.08
            print(f"{caster.name}의 콤보가 증가했습니다! (x{caster.combo_count}, 공격력 배율: {caster.temp_combo_multiplier:.2f})")
            return True
        return True
    except Exception as e:
        print(f"콤보 보너스 효과 적용 중 오류: {e}")
        return False

def _critical_boost(caster, target=None, skill_data=None):
    """크리티컬 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('크리티컬_증가', 5, 25)
        print(f"{caster.name}의 크리티컬 확률이 증가했습니다!")
        return True
    except Exception as e:
        print(f"크리티컬 부스트 효과 적용 중 오류: {e}")
        return False

def _damage_boost(caster, target=None, skill_data=None):
    """공격력 증가 효과"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('공격력_증가', 5, 30)
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
            critical_effect = StatusEffect("크리티컬_확정", "크리티컬_확정", 1, 100)
            caster.status_manager.add_status(critical_effect)
        print(f"{caster.name}의 다음 공격이 크리티컬로 확정되었습니다!")
        return True
    except Exception as e:
        print(f"크리티컬 확정 효과 적용 중 오류: {e}")
        return False

def _never_miss(caster, target=None, skill_data=None):
    """절대 명중"""
    try:
        if hasattr(caster, 'status_manager'):
            miss_effect = StatusEffect("절대_명중", "절대_명중", 3, 100)
            caster.status_manager.add_status(miss_effect)
        print(f"{caster.name}의 공격이 절대 빗나가지 않습니다!")
        return True
    except Exception as e:
        print(f"절대 명중 효과 적용 중 오류: {e}")
        return False

def _perfect_accuracy(caster, target=None, skill_data=None):
    """완벽한 정확도"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('완벽한_정확도', 5, 100)
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
            caster.status_manager.add_status('치료_효과_증가', 5, 50)
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
            caster.status_manager.add_status('회복', 10, 20)  # 10턴 동안 턴마다 20 회복
        print(f"{caster.name}에게 지속 회복 효과가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"지속 회복 효과 적용 중 오류: {e}")
        return False

def _speed_increase(caster, target=None, skill_data=None):
    """속도 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('속도_증가', 5, 30)
        print(f"{caster.name}의 속도가 증가했습니다!")
        return True
    except Exception as e:
        print(f"속도 증가 효과 적용 중 오류: {e}")
        return False

def _stealth_mode(caster, target=None, skill_data=None):
    """은신 모드"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('은신', 3, 100)  # 3턴 은신
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
                    target.status_manager.add_status('기절', 2, 0)
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
            caster.status_manager.add_status('순간이동_준비', 1, 0)
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
                target.status_manager.add_status('공포', 3, 20)  # 공격력 20% 감소
            print(f"{target.name}이 공포에 떨고 있습니다!")
        return True
    except Exception as e:
        print(f"공포 오라 효과 적용 중 오류: {e}")
        return False

def _poison_immunity(caster, target=None, skill_data=None):
    """독 면역"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('독_면역', 10, 0)
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
            caster.status_manager.add_status('화염_면역', 10, 0)
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
            caster.status_manager.add_status('냉기_면역', 10, 0)
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
            caster.status_manager.add_status('상태이상_면역', 5, 0)
            # 기존 디버프들 제거
            debuffs = ['독', '화상', '빙결', '기절', '혼란', '약화', '저주']
            for debuff in debuffs:
                caster.status_manager.remove_status(debuff)
        print(f"{caster.name}이 모든 상태이상에 면역이 되었습니다!")
        return True
    except Exception as e:
        print(f"상태이상 면역 효과 적용 중 오류: {e}")
        return False

# ========================================
# 누락된 특수 효과 함수들
# ========================================

def _stance_adaptation(caster):
    """자세 적응 - 전사의 전술분석 스킬"""
    try:
        if hasattr(caster, 'character_class') and caster.character_class == "전사":
            # warrior_stance 속성을 확인하고 수정
            current_stance = getattr(caster, 'warrior_stance', 'balanced')
            
            if current_stance == 'balanced':
                caster.warrior_stance = 'attack'
                print(f"⚔️ 전술분석으로 자세 변경: 균형형 → 공격형")
            elif current_stance == 'attack':
                caster.warrior_stance = 'defense'
                print(f"⚔️ 전술분석으로 자세 변경: 공격형 → 방어형")
            elif current_stance == 'defense':
                caster.warrior_stance = 'speed'
                print(f"⚔️ 전술분석으로 자세 변경: 방어형 → 신속형")
            elif current_stance == 'speed':
                caster.warrior_stance = 'berserker'
                print(f"⚔️ 전술분석으로 자세 변경: 신속형 → 광전사")
            elif current_stance == 'berserker':
                caster.warrior_stance = 'guardian'
                print(f"⚔️ 전술분석으로 자세 변경: 광전사 → 수호자")
            else:  # guardian 또는 기타
                caster.warrior_stance = 'balanced'
                print(f"⚔️ 전술분석으로 자세 변경: {current_stance} → 균형형")
            
            caster.temp_stance_bonus = True
            caster.temp_accuracy_bonus = getattr(caster, 'temp_accuracy_bonus', 0) + 20
            caster.temp_crit_bonus = getattr(caster, 'temp_crit_bonus', 0) + 15
            
            print(f"🧠 전술분석 완료! 새 자세: {caster.warrior_stance}")
            return True
        return True
    except Exception as e:
        print(f"전술분석 효과 적용 중 오류: {e}")
        return False

def _enemy_analysis(caster):
    """적 분석"""
    try:
        caster.temp_enemy_weakness_detection = True
        print(f"🎯 적의 약점을 파악했습니다!")
        return True
    except Exception as e:
        print(f"적 분석 효과 적용 중 오류: {e}")
        return False

def _adaptive_ultimate(caster, target, skill_data):
    """적응형 궁극기"""
    try:
        current_stance = getattr(caster, 'stance', 'BAL')
        print(f"🌟 적응형 궁극기 발동! 자세: {current_stance}")
        return True
    except Exception as e:
        print(f"적응형 궁극기 효과 적용 중 오류: {e}")
        return False

def _guardian_bonus(caster):
    """수호자 보너스"""
    try:
        caster.temp_defense_bonus = getattr(caster, 'temp_defense_bonus', 0) + 15
        print(f"🛡️ 수호 효과 발동!")
        return True
    except Exception as e:
        print(f"수호자 보너스 효과 적용 중 오류: {e}")
        return False

def _fire_count(caster, target, skill_data):
    """화염 속성 카운트"""
    try:
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
    except Exception as e:
        print(f"화염 카운트 효과 적용 중 오류: {e}")
        return False

def _lightning_count(caster, target, skill_data):
    """번개 속성 카운트"""
    try:
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
    except Exception as e:
        print(f"번개 카운트 효과 적용 중 오류: {e}")
        return False

def _mana_shield(caster, target=None, skill_data=None):
    """마나 실드"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마나_실드', 5, 50)  # 5턴간 피해의 50%를 MP로 대신 받음
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
            target.take_damage(pierce_damage, "관통 피해", True)
            print(f"{caster.name}의 관통 공격이 방어를 무시하고 피해를 입혔습니다!")
        return True
    except Exception as e:
        print(f"관통 공격 효과 적용 중 오류: {e}")
        return False

def _auto_counter(caster, target=None, skill_data=None):
    """자동 반격"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('자동_반격', 5, 0)
        print(f"{caster.name}이 자동 반격 자세를 취했습니다!")
        return True
    except Exception as e:
        print(f"자동 반격 효과 적용 중 오류: {e}")
        return False

def _auto_revive(caster, target=None, skill_data=None):
    """자동 부활"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('자동_부활', 1, 50)  # 1회용, 50% HP로 부활
        print(f"{caster.name}에게 자동 부활 효과가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"자동 부활 효과 적용 중 오류: {e}")
        return False

def _invisibility(caster, target=None, skill_data=None):
    """투명화"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('투명화', 3, 0)  # 3턴 동안 대상이 되지 않음
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
                target.status_manager.add_status('혼란', 3, 0)
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
                target.status_manager.add_status('저주', 5, 15)  # 모든 능력치 15% 감소
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
            caster.status_manager.add_status('행운', 10, 20)  # 크리티컬 확률 및 회피 증가
        print(f"{caster.name}의 행운이 증가했습니다!")
        return True
    except Exception as e:
        print(f"행운 증가 효과 적용 중 오류: {e}")
        return False

def _exp_double(caster, target=None, skill_data=None):
    """경험치 2배"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('경험치_2배', 10, 0)
        print(f"{caster.name}이 경험치 2배 효과를 받습니다!")
        return True
    except Exception as e:
        print(f"경험치 2배 효과 적용 중 오류: {e}")
        return False

def _gold_double(caster, target=None, skill_data=None):
    """골드 2배"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('골드_2배', 10, 0)
        print(f"{caster.name}이 골드 2배 효과를 받습니다!")
        return True
    except Exception as e:
        print(f"골드 2배 효과 적용 중 오류: {e}")
        return False

def _item_find(caster, target=None, skill_data=None):
    """아이템 발견 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('아이템_발견', 20, 50)  # 50% 증가
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
            caster.status_manager.add_status('파티_강화', 10, 25)
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
                target.status_manager.add_status('화상', 3, 20)
            
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
                target.status_manager.add_status('빙결', 2, 0)
            
            print(f"{caster.name}의 얼음 궤적이 {target.name}을 얼렸습니다!")
        return True
    except Exception as e:
        print(f"얼음 궤적 효과 적용 중 오류: {e}")
        return False

def _earth_shield(caster, target=None, skill_data=None):
    """대지의 방패"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('대지_방패', 8, 30)  # 8턴간 피해 30% 감소
        print(f"{caster.name}에게 대지의 방패가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"대지의 방패 효과 적용 중 오류: {e}")
        return False

def _wind_walk(caster, target=None, skill_data=None):
    """바람걸음"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('바람걸음', 5, 40)  # 회피율 40% 증가
        print(f"{caster.name}이 바람처럼 가벼워졌습니다!")
        return True
    except Exception as e:
        print(f"바람걸음 효과 적용 중 오류: {e}")
        return False

def _magic_amplify(caster, target=None, skill_data=None):
    """마법 증폭"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마법_증폭', 5, 50)  # 마법 피해 50% 증가
        print(f"{caster.name}의 마법력이 증폭되었습니다!")
        return True
    except Exception as e:
        print(f"마법 증폭 효과 적용 중 오류: {e}")
        return False

def _weapon_mastery(caster, target=None, skill_data=None):
    """무기 숙련"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('무기_숙련', 10, 25)  # 물리 공격력 25% 증가
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
            caster.status_manager.add_status('기_수련', 15, 10)  # 15턴간 모든 능력치 10% 증가
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
            caster.status_manager.add_status('내면의_기', 20, 15)  # 20턴간 모든 능력치 15% 증가
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
                target.status_manager.add_status('맹독', 5, 30)  # 5턴간 강력한 독
            
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
                target.status_manager.add_status('감전', 3, 15)
            
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
            caster.status_manager.add_status('마나_집중', 5, 25)
            
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

def _magic_blast(caster, target, skill_data):
    """마력 폭발 - 강력한 마법 폭발"""
    try:
        if target and skill_data:
            blast_damage = skill_data.get('power', 150)
            # 마법 공격력 기반으로 피해 증가
            magic_attack = getattr(caster, 'magic_attack', 100)
            final_damage = int(blast_damage * (1 + magic_attack / 500))
            target.take_damage(final_damage, "마력 폭발")
            print(f"{caster.name}의 마력 폭발이 {target.name}에게 {final_damage} 피해!")
            
            # 주변 적들에게도 절반 피해
            if hasattr(target, 'nearby_enemies'):
                for nearby in target.nearby_enemies:
                    splash_damage = final_damage // 2
                    nearby.take_damage(splash_damage, "마력 폭발 (연쇄)")
                    print(f"연쇄 폭발로 {nearby.name}에게 {splash_damage} 피해!")
        return True
    except Exception as e:
        print(f"마력 폭발 효과 적용 중 오류: {e}")
        return False

def _mana_recovery(caster, target=None, skill_data=None):
    """마나 회복 - 아크메이지 MP 재생 효과"""
    try:
        magic_attack = getattr(caster, 'magic_attack', 50)
        mp_restore = int(magic_attack * 0.3)
        
        # MP 회복
        old_mp = caster.current_mp
        caster.current_mp = min(caster.max_mp, caster.current_mp + mp_restore)
        actual_restore = caster.current_mp - old_mp
        
        print(f"🔮 {caster.name}의 마나가 {actual_restore} 회복되었습니다.")
        return True
    except Exception as e:
        print(f"마나 회복 효과 적용 중 오류: {e}")
        return False

def _mana_explosion(caster, target, skill_data=None):
    """마나 폭발 - MP 소모하여 강력한 피해"""
    try:
        mp_cost = min(30, caster.current_mp)
        if mp_cost <= 0:
            print("마나가 부족합니다!")
            return False
        
        caster.current_mp -= mp_cost
        
        # MP 소모량에 비례한 피해
        magic_attack = getattr(caster, 'magic_attack', 50)
        base_damage = int(magic_attack * (1 + mp_cost / 20))
        
        target.take_damage(base_damage, "마나 폭발")
        print(f"🌟 {caster.name}의 마나 폭발이 {target.name}에게 {base_damage} 마법 피해!")
        return True
    except Exception as e:
        print(f"마나 폭발 효과 적용 중 오류: {e}")
        return False

def _overload_magic(caster, target, skill_data=None):
    """과부하 마법 - 높은 피해, MP 역류 위험"""
    try:
        magic_attack = getattr(caster, 'magic_attack', 50)
        base_damage = int(magic_attack * 2.5)
        
        target.take_damage(base_damage, "과부하 마법")
        
        # 15% 확률로 MP 역류 (자신이 피해)
        if random.random() < 0.15:
            recoil_damage = int(caster.max_hp * 0.1)
            caster.take_damage(recoil_damage, "마법 역류")
            print(f"⚡ {caster.name}의 과부하 마법이 {target.name}에게 {base_damage} 피해! 하지만 역류로 {recoil_damage} 피해를 받았습니다!")
        else:
            print(f"⚡ {caster.name}의 과부하 마법이 {target.name}에게 {base_damage} 마법 피해!")
        return True
    except Exception as e:
        print(f"과부하 마법 효과 적용 중 오류: {e}")
        return False

def _chain_magic(caster, target, skill_data=None):
    """연쇄 마법 - 여러 적에게 전파되는 마법"""
    try:
        magic_attack = getattr(caster, 'magic_attack', 50)
        base_damage = int(magic_attack * 0.8)
        
        target.take_damage(base_damage, "연쇄 마법")
        targets_hit = 1
        
        # 주변 적들에게 연쇄 (최대 3명)
        if hasattr(target, 'nearby_enemies'):
            chain_count = 0
            for enemy in target.nearby_enemies:
                if chain_count < 2:
                    chain_damage = int(base_damage * (0.7 ** (chain_count + 1)))
                    enemy.take_damage(chain_damage, "연쇄 마법")
                    targets_hit += 1
                    chain_count += 1
        
        print(f"⚡ {caster.name}의 연쇄 마법이 {targets_hit}명의 적에게 연쇄 피해!")
        return True
    except Exception as e:
        print(f"연쇄 마법 효과 적용 중 오류: {e}")
        return False

def _ultimate_magic(caster, target, skill_data=None):
    """궁극 마법 - 아크메이지의 최강 마법"""
    try:
        magic_attack = getattr(caster, 'magic_attack', 50)
        base_damage = int(magic_attack * 3.0)
        
        # MP를 절반 소모
        mp_cost = caster.current_mp // 2
        caster.current_mp -= mp_cost
        
        target.take_damage(base_damage, "궁극 마법")
        
        # 30% 확률로 즉사 효과 (보스 제외)
        if not getattr(target, 'is_boss', False) and random.random() < 0.3:
            target.current_hp = 0
            print(f"🌟 {caster.name}의 궁극 마법! {target.name}이(가) 즉사했습니다!")
        else:
            print(f"🌟 {caster.name}의 궁극 마법이 {target.name}에게 {base_damage} 마법 피해!")
        return True
    except Exception as e:
        print(f"궁극 마법 효과 적용 중 오류: {e}")
        return False

def _precision_shot(caster, target, skill_data=None):
    """정밀 사격 - 궁수의 크리티컬 확률 증가 공격"""
    try:
        physical_attack = getattr(caster, 'physical_attack', 30)
        base_damage = int(physical_attack * 1.2)
        
        # 크리티컬 확률 대폭 증가 (기본 + 40%)
        crit_chance = getattr(caster, 'critical_rate', 5) + 40
        is_critical = random.random() < (crit_chance / 100)
        
        if is_critical:
            base_damage = int(base_damage * 2.0)
            target.take_damage(base_damage, "정밀 사격 (크리티컬)")
            print(f"🎯 {caster.name}의 정밀 사격! 크리티컬 히트! {target.name}에게 {base_damage} 피해!")
        else:
            target.take_damage(base_damage, "정밀 사격")
            print(f"🎯 {caster.name}의 정밀 사격이 {target.name}에게 {base_damage} 피해!")
        return True
    except Exception as e:
        print(f"정밀 사격 효과 적용 중 오류: {e}")
        return False

def _arrow_rain(caster, target, skill_data=None):
    """화살비 - 여러 적에게 화살 공격"""
    try:
        physical_attack = getattr(caster, 'physical_attack', 30)
        base_damage = int(physical_attack * 0.6)
        
        targets_hit = 1
        target.take_damage(base_damage, "화살비")
        
        # 주변 모든 적에게 피해
        if hasattr(target, 'nearby_enemies'):
            for enemy in target.nearby_enemies:
                enemy.take_damage(base_damage, "화살비")
                targets_hit += 1
        
        print(f"🏹 {caster.name}의 화살비가 {targets_hit}명의 적에게 피해!")
        return True
    except Exception as e:
        print(f"화살비 효과 적용 중 오류: {e}")
        return False

def _explosive_arrow(caster, target, skill_data=None):
    """폭발 화살 - 폭발 범위 피해"""
    try:
        physical_attack = getattr(caster, 'physical_attack', 30)
        base_damage = int(physical_attack * 1.5)
        
        # 주 대상에게 피해
        target.take_damage(base_damage, "폭발 화살")
        
        # 폭발 범위 피해 (70%)
        explosion_damage = int(base_damage * 0.7)
        if hasattr(target, 'nearby_enemies'):
            for enemy in target.nearby_enemies:
                enemy.take_damage(explosion_damage, "폭발 화살 (폭발)")
        
        print(f"💥 {caster.name}의 폭발 화살이 {target.name}에게 {base_damage} 피해 + 폭발 피해!")
        return True
    except Exception as e:
        print(f"폭발 화살 효과 적용 중 오류: {e}")
        return False

def _wind_shot(caster, target, skill_data=None):
    """바람 사격 - 관통 효과 화살"""
    try:
        physical_attack = getattr(caster, 'physical_attack', 30)
        base_damage = int(physical_attack * 1.3)
        
        targets_hit = 1
        target.take_damage(base_damage, "바람 사격")
        
        # 직선상의 모든 적 관통 (최대 3명)
        if hasattr(target, 'nearby_enemies'):
            pierce_count = 0
            for enemy in target.nearby_enemies:
                if pierce_count < 2:
                    pierce_damage = int(base_damage * (0.9 ** (pierce_count + 1)))
                    enemy.take_damage(pierce_damage, "바람 사격 (관통)")
                    targets_hit += 1
                    pierce_count += 1
        
        print(f"💨 {caster.name}의 바람 사격이 {targets_hit}명의 적을 관통!")
        return True
    except Exception as e:
        print(f"바람 사격 효과 적용 중 오류: {e}")
        return False

def _ultimate_shot(caster, target, skill_data=None):
    """궁극 사격 - 궁수의 최강 기술"""
    try:
        physical_attack = getattr(caster, 'physical_attack', 30)
        base_damage = int(physical_attack * 3.5)
        
        # 반드시 크리티컬
        base_damage = int(base_damage * 2.0)
        
        # 방어력 무시 피해
        actual_damage = int(base_damage * 0.9)
        target.current_hp = max(0, target.current_hp - actual_damage)
        
        # 30% 확률로 즉사 (보스 제외)
        if not getattr(target, 'is_boss', False) and random.random() < 0.3:
            target.current_hp = 0
            print(f"🎯 {caster.name}의 궁극 사격! {target.name}이(가) 즉사했습니다!")
        else:
            print(f"🎯 {caster.name}의 궁극 사격이 {target.name}에게 {actual_damage} 치명적 피해!")
        return True
    except Exception as e:
        print(f"궁극 사격 효과 적용 중 오류: {e}")
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
            caster.status_manager.add_status('마법_파티_강화', 8, 20)
        print(f"{caster.name}의 마법력이 아군을 강화했습니다!")
        return True
    except Exception as e:
        print(f"마법 파티 강화 효과 적용 중 오류: {e}")
        return False

def _physical_accuracy_crit_boost(caster, target=None, skill_data=None):
    """물리공격력과 정확도, 크리티컬 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('물리_전투_강화', 8, 25)
        print(f"{caster.name}의 전투 기술이 향상되었습니다!")
        return True
    except Exception as e:
        print(f"물리 전투 강화 효과 적용 중 오류: {e}")
        return False

def _defense_protection_ready(caster, target=None, skill_data=None):
    """방어력 증가 및 아군 보호 준비"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('방어_준비', 10, 30)
        print(f"{caster.name}이 방어 태세를 갖췄습니다!")
        return True
    except Exception as e:
        print(f"방어 준비 효과 적용 중 오류: {e}")
        return False

def _shield_defense(caster, target=None, skill_data=None):
    """방패 방어 - 피해 감소"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('방패_방어', 5, 40)  # 피해 40% 감소
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
            caster.status_manager.add_status('용기', 10, 20)
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
            caster.status_manager.add_status('조준', 3, 50)  # 명중률 50% 증가
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
            target.take_damage(thrust_damage, "창 찌르기", True)
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
                target.status_manager.add_status('혼란', 2, 0)
            
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
                    target.take_damage(base_damage, "적응 궁극기", True)
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
            caster.status_manager.add_status('공격적_태세', 8, 40)  # 공격력 40% 증가
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
            caster.status_manager.add_status('공중_돌진', 3, 60)  # 회피율 60% 증가
        print(f"{caster.name}이 공중으로 돌진했습니다!")
        return True
    except Exception as e:
        print(f"공중 돌진 효과 적용 중 오류: {e}")
        return False

def _air_mastery(caster, target=None, skill_data=None):
    """공중 숙련 - 비행 및 공중 전투 능력"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('공중_숙련', 15, 30)  # 모든 공중 관련 능력 증가
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
                    caster.status_manager.add_status('성선_가호', 5, 25)
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
                caster.status_manager.add_status('사자의_위엄', 5, 30)
            elif chosen_animal == '독수리':
                caster.status_manager.add_status('독수리의_시야', 5, 40)
            elif chosen_animal == '곰':
                caster.status_manager.add_status('곰의_힘', 5, 35)
            elif chosen_animal == '늑대':
                caster.status_manager.add_status('늑대의_민첩', 5, 25)
            elif chosen_animal == '치타':
                caster.status_manager.add_status('치타의_속도', 5, 50)
        
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
            cure_target.status_manager.add_status('독_저항', 10, 50)
        print(f"{cure_target.name}의 독이 치료되었습니다!")
        return True
    except Exception as e:
        print(f"해독제 효과 적용 중 오류: {e}")
        return False

def _aquatic_blessing(caster, target=None, skill_data=None):
    """수중 축복 - 물 속성 친화력"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('수중_축복', 12, 25)
            caster.status_manager.add_status('물_속성_친화', 12, 40)
        print(f"{caster.name}이 물의 축복을 받았습니다!")
        return True
    except Exception as e:
        print(f"수중 축복 효과 적용 중 오류: {e}")
        return False

def _aquatic_breathing(caster, target=None, skill_data=None):
    """수중 호흡 - 물 속에서 자유롭게 호흡"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('수중_호흡', 30, 0)
        print(f"{caster.name}이 물 속에서도 자유롭게 호흡할 수 있습니다!")
        return True
    except Exception as e:
        print(f"수중 호흡 효과 적용 중 오류: {e}")
        return False

def _arcane_mastery(caster, target=None, skill_data=None):
    """비전 숙련 - 마법 위력과 효율 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('비전_숙련', 10, 35)
            caster.status_manager.add_status('마나_효율', 10, 25)
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
            caster.status_manager.add_status('자동_포탑', 20, 80)  # 20턴간 자동 공격
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
                target.status_manager.add_status('구역질', 5, 15)  # 모든 행동 15% 감소
            print(f"{target.name}이 불쾌한 맛에 구역질을 합니다!")
        return True
    except Exception as e:
        print(f"불쾌한 맛 효과 적용 중 오류: {e}")
        return False

def _balanced_bonus(caster, target=None, skill_data=None):
    """균형 보너스 - 모든 능력치 균등 증가"""
    try:
        if hasattr(caster, 'status_manager') and caster.status_manager:
            # StatusType enum을 사용하여 상태 추가
            from game.status_effects import StatusType
            caster.status_manager.add_status(StatusType.BUFF, 10, 20)  # 모든 능력치 20% 증가
            print(f"{caster.name}이 완벽한 균형을 이뤘습니다!")
        elif hasattr(caster, 'add_status'):
            # 기본적인 상태 추가
            caster.add_status('균형', 10, 20)
            print(f"{caster.name}이 완벽한 균형을 이뤘습니다!")
        else:
            print(f"{caster.name}의 스탯이 일시적으로 증가합니다!")
        return True
    except Exception as e:
        print(f"균형 보너스 효과 적용 중 오류: {e}")
        return False

def _banishment(caster, target, skill_data):
    """추방 - 적을 일시적으로 전투에서 제외"""
    try:
        if target:
            if hasattr(target, 'status_manager'):
                target.status_manager.add_status('추방', 3, 0)  # 3턴간 행동 불가
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
    """광전사 보너스 - 잃은 HP의 절댓값만큼 공격력 증가"""
    try:
        if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
            hp_ratio = caster.current_hp / caster.max_hp
            lost_hp_ratio = 1 - hp_ratio  # 잃은 HP 비율
            
            # 잃은 HP의 절댓값만큼 공격력 증가 (최대 75%까지)
            attack_bonus = min(int(lost_hp_ratio * 100), 75)  # 최대 75% 공격력 증가
            
            # 최대 HP 증가 (생존력 향상)
            max_hp_bonus = int(lost_hp_ratio * 50)  # 잃은 HP 비율의 50%만큼 최대 HP 증가
            
            if hasattr(caster, 'status_manager'):
                caster.status_manager.add_status('광전사_각성', 8, attack_bonus)
                if max_hp_bonus > 0:
                    caster.status_manager.add_status('생존본능', 8, max_hp_bonus)
            
            # 임시 스탯 보정
            if hasattr(caster, 'temp_attack_bonus'):
                caster.temp_attack_bonus = getattr(caster, 'temp_attack_bonus', 0) + (caster.max_hp * lost_hp_ratio * 0.5)
            else:
                caster.temp_attack_bonus = caster.max_hp * lost_hp_ratio * 0.5
                
            if hasattr(caster, 'temp_max_hp_bonus'):
                caster.temp_max_hp_bonus = getattr(caster, 'temp_max_hp_bonus', 0) + max_hp_bonus
            else:
                caster.temp_max_hp_bonus = max_hp_bonus
            
            if attack_bonus > 0 or max_hp_bonus > 0:
                print(f"💀 {caster.name}의 광전사 본능이 깨어났습니다!")
                if attack_bonus > 0:
                    print(f"   🗡️ 공격력 +{attack_bonus}% (잃은 HP: {lost_hp_ratio*100:.1f}%)")
                if max_hp_bonus > 0:
                    print(f"   💚 최대 HP +{max_hp_bonus}% (생존 본능)")
        return True
    except Exception as e:
        print(f"광전사 보너스 효과 적용 중 오류: {e}")
        return False

def _berserker_mode(caster, target=None, skill_data=None):
    """광전사 모드 - 극한의 전투 상태"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('광전사_모드', 10, 60)  # 공격력 60% 증가
            caster.status_manager.add_status('이성_상실', 10, 0)    # 제어 불가
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
                target.status_manager.add_status('화상', 4, 25)
            elif breath_type == '냉기' and hasattr(target, 'status_manager'):
                target.status_manager.add_status('빙결', 2, 0)
            
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


# ========================================
# 5번째 배치: 능력치 및 상태 관련 특수 효과들
# ========================================

def _chronos_blessing(caster, target=None, skill_data=None):
    """크로노스의 축복 - 시간 조작 능력"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('시간_조작', 8, 30)
            caster.status_manager.add_status('시간_가속', 8, 25)
        print(f"{caster.name}이 시간의 축복을 받았습니다!")
        return True
    except Exception as e:
        print(f"크로노스의 축복 효과 적용 중 오류: {e}")
        return False

def _combo_mark(caster, target, skill_data):
    """콤보 표시 - 적에게 콤보 누적 마크"""
    try:
        if target:
            if hasattr(target, 'status_manager'):
                current_mark = getattr(target, 'combo_mark', 0)
                target.combo_mark = current_mark + 1
                target.status_manager.add_status(f'콤보_마크_{target.combo_mark}', 10, target.combo_mark * 10)
            print(f"{target.name}에게 콤보 마크 {getattr(target, 'combo_mark', 1)}이 적용되었습니다!")
        return True
    except Exception as e:
        print(f"콤보 마크 효과 적용 중 오류: {e}")
        return False

def _combo_multiplier(caster, target=None, skill_data=None):
    """콤보 배율 - 콤보 수에 따른 피해 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            combo_count = getattr(caster, 'combo_count', 0) + 1
            caster.combo_count = combo_count
            multiplier = min(combo_count * 15, 200)  # 최대 200%
            caster.status_manager.add_status('콤보_배율', 5, multiplier)
        print(f"{caster.name}의 콤보 배율이 증가했습니다! (x{getattr(caster, 'combo_count', 1)})")
        return True
    except Exception as e:
        print(f"콤보 배율 효과 적용 중 오류: {e}")
        return False

def _combo_strike(caster, target, skill_data):
    """콤보 공격 - 콤보 수만큼 연속 공격"""
    try:
        if target and skill_data:
            combo_count = getattr(caster, 'combo_count', 1)
            base_damage = skill_data.get('power', 100) // combo_count
            total_damage = 0
            
            for i in range(combo_count):
                damage = base_damage + (i * 10)
                target.take_damage(damage, f"콤보 {i+1}")
                total_damage += damage
            
            print(f"{caster.name}의 {combo_count}콤보 공격으로 총 {total_damage} 피해!")
        return True
    except Exception as e:
        print(f"콤보 공격 효과 적용 중 오류: {e}")
        return False

def _complete_wound_healing(caster, target=None, skill_data=None):
    """완전 상처 치유 - 모든 상처와 디버프 치료"""
    try:
        heal_target = target if target else caster
        if hasattr(heal_target, 'wounds'):
            heal_target.wounds = 0
        if hasattr(heal_target, 'status_manager'):
            # 모든 디버프 제거
            debuffs = ['독', '화상', '빙결', '기절', '혼란', '약화', '저주', '출혈', '감전']
            for debuff in debuffs:
                heal_target.status_manager.remove_status(debuff)
        print(f"{heal_target.name}의 모든 상처와 디버프가 완전히 치유되었습니다!")
        return True
    except Exception as e:
        print(f"완전 상처 치유 효과 적용 중 오류: {e}")
        return False

def _constitution_boost(caster, target=None, skill_data=None):
    """체질 강화 - 체력과 저항력 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('체질_강화', 15, 25)  # 체력과 저항력 25% 증가
        print(f"{caster.name}의 체질이 강화되었습니다!")
        return True
    except Exception as e:
        print(f"체질 강화 효과 적용 중 오류: {e}")
        return False

def _consume_all_shadows(caster, target=None, skill_data=None):
    """모든 그림자 소모 - 그림자를 소모하여 강력한 효과"""
    try:
        shadow_count = getattr(caster, 'shadow_count', 0)
        if shadow_count > 0:
            # 그림자 수만큼 능력치 증가
            boost_amount = shadow_count * 20
            if hasattr(caster, 'status_manager'):
                caster.status_manager.add_status('그림자_흡수', 8, boost_amount)
            caster.shadow_count = 0
            print(f"{caster.name}이 {shadow_count}개의 그림자를 소모하여 힘을 얻었습니다!")
        else:
            print(f"{caster.name}에게 소모할 그림자가 없습니다!")
        return True
    except Exception as e:
        print(f"모든 그림자 소모 효과 적용 중 오류: {e}")
        return False

def _corruption_risk(caster, target=None, skill_data=None):
    """타락 위험 - 강력한 힘과 부작용"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('타락의_힘', 10, 50)  # 공격력 50% 증가
            caster.status_manager.add_status('타락_부작용', 10, -15)  # 방어력 15% 감소
        print(f"{caster.name}이 타락의 힘을 얻었지만 위험에 빠졌습니다!")
        return True
    except Exception as e:
        print(f"타락 위험 효과 적용 중 오류: {e}")
        return False

def _cosmic_insight(caster, target=None, skill_data=None):
    """우주적 통찰 - 모든 것을 꿰뚫어보는 능력"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('우주적_통찰', 12, 40)
            caster.status_manager.add_status('진실_시야', 12, 100)
        print(f"{caster.name}이 우주의 진리를 깨달았습니다!")
        return True
    except Exception as e:
        print(f"우주적 통찰 효과 적용 중 오류: {e}")
        return False

def _courage_boost(caster, target=None, skill_data=None):
    """용기 증진 - 두려움 제거 및 공격력 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.remove_status('공포')
            caster.status_manager.remove_status('두려움')
            caster.status_manager.add_status('용기', 8, 30)
        print(f"{caster.name}의 용기가 솟구쳤습니다!")
        return True
    except Exception as e:
        print(f"용기 증진 효과 적용 중 오류: {e}")
        return False

def _craft_gadget(caster, target=None, skill_data=None):
    """기계 제작 - 유용한 도구 생성"""
    try:
        import random
        gadgets = ['치료_드론', '공격_터렛', '방어_실드', '스캔_장치', '부스터']
        gadget = random.choice(gadgets)
        
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status(gadget, 15, 25)
        
        print(f"{caster.name}이 {gadget}을 제작했습니다!")
        return True
    except Exception as e:
        print(f"기계 제작 효과 적용 중 오류: {e}")
        return False

def _critical_damage_up(caster, target=None, skill_data=None):
    """크리티컬 피해 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('크리티컬_피해_증가', 8, 40)
        print(f"{caster.name}의 크리티컬 피해가 증가했습니다!")
        return True
    except Exception as e:
        print(f"크리티컬 피해 증가 효과 적용 중 오류: {e}")
        return False

def _critical_rate_up(caster, target=None, skill_data=None):
    """크리티컬 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('크리티컬_확률_증가', 8, 25)
        print(f"{caster.name}의 크리티컬 확률이 증가했습니다!")
        return True
    except Exception as e:
        print(f"크리티컬 확률 증가 효과 적용 중 오류: {e}")
        return False

def _damage_stack(caster, target=None, skill_data=None):
    """피해 누적 - 공격할 때마다 피해 배율 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            current_stack = getattr(caster, 'damage_stack', 0)
            caster.damage_stack = current_stack + 1
            # 스택당 공격력 6% 증가 (배율 방식)
            stack_multiplier = 1.0 + (caster.damage_stack * 0.06)
            caster.temp_damage_stack_multiplier = stack_multiplier
            caster.status_manager.add_status('피해_누적', 10, int(stack_multiplier * 100))
        print(f"{caster.name}의 피해 누적이 증가했습니다! (스택: {getattr(caster, 'damage_stack', 1)}, 배율: {stack_multiplier:.2f}x)")
        return True
    except Exception as e:
        print(f"피해 누적 효과 적용 중 오류: {e}")
        return False

def _dark_magic(caster, target, skill_data):
    """암흑 마법 - 강력하지만 위험한 마법"""
    try:
        if target and skill_data:
            dark_damage = skill_data.get('power', 140)
            target.take_damage(dark_damage, "암흑 마법")
            
            # 시전자에게도 부작용
            if hasattr(caster, 'current_hp'):
                backlash = dark_damage * 0.1
                caster.current_hp = max(1, caster.current_hp - backlash)
            
            print(f"{caster.name}의 암흑 마법이 {target.name}을 강타했지만 시전자도 상처를 입었습니다!")
        return True
    except Exception as e:
        print(f"암흑 마법 효과 적용 중 오류: {e}")
        return False

def _deep_recovery(caster, target=None, skill_data=None):
    """깊은 회복 - 시간이 지남에 따라 점진적 회복"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('깊은_회복', 20, 30)  # 20턴간 턴마다 30 회복
        print(f"{caster.name}에게 깊은 회복 효과가 적용되었습니다!")
        return True
    except Exception as e:
        print(f"깊은 회복 효과 적용 중 오류: {e}")
        return False

def _defensive_bonus(caster, target=None, skill_data=None):
    """방어 보너스 - 방어력 및 저항력 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('방어_보너스', 10, 35)
        print(f"{caster.name}의 방어력이 증가했습니다!")
        return True
    except Exception as e:
        print(f"방어 보너스 효과 적용 중 오류: {e}")
        return False

def _deploy_robot(caster, target=None, skill_data=None):
    """로봇 배치 - 자동 전투 로봇 소환"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('전투_로봇', 25, 60)  # 25턴간 자동 공격
        print(f"{caster.name}이 전투 로봇을 배치했습니다!")
        return True
    except Exception as e:
        print(f"로봇 배치 효과 적용 중 오류: {e}")
        return False

def _dimension_storm(caster, target, skill_data):
    """차원 폭풍 - 차원을 찢는 강력한 공격"""
    try:
        if target and skill_data:
            storm_damage = skill_data.get('power', 180)
            target.take_damage(storm_damage, "차원 폭풍")
            
            # 공간 왜곡 효과
            if hasattr(target, 'status_manager'):
                target.status_manager.add_status('공간_왜곡', 5, 30)
            
            print(f"{caster.name}의 차원 폭풍이 {target.name}을 공간째로 찢어버렸습니다!")
        return True
    except Exception as e:
        print(f"차원 폭풍 효과 적용 중 오류: {e}")
        return False

def _dimensional_shift(caster, target=None, skill_data=None):
    """차원 이동 - 다른 차원으로 일시 이동"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('차원_이동', 3, 0)  # 3턴간 공격 받지 않음
        print(f"{caster.name}이 다른 차원으로 이동했습니다!")
        return True
    except Exception as e:
        print(f"차원 이동 효과 적용 중 오류: {e}")
        return False


# ========================================
# 6번째 배치: 원소 및 자연 관련 특수 효과들
# ========================================

def _double_strike(caster, target, skill_data):
    """이중 공격 - 두 번 연속 공격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 80)
            target.take_damage(damage, "첫 번째 공격")
            target.take_damage(damage, "두 번째 공격")
            print(f"{caster.name}의 이중 공격으로 {target.name}에게 {damage * 2} 피해!")
        return True
    except Exception as e:
        print(f"이중 공격 효과 적용 중 오류: {e}")
        return False

def _draconic_might(caster, target=None, skill_data=None):
    """용의 힘 - 드래곤의 힘으로 능력치 대폭 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('용의_힘', 12, 60)  # 모든 능력치 60% 증가
            caster.status_manager.add_status('용의_비늘', 12, 40)  # 방어력 추가 증가
        print(f"{caster.name}이 용의 힘을 각성했습니다!")
        return True
    except Exception as e:
        print(f"용의 힘 효과 적용 중 오류: {e}")
        return False

def _earth_elementalist(caster, target=None, skill_data=None):
    """대지 정령술사 - 대지 원소 마스터리"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('대지_마스터리', 15, 45)
            caster.status_manager.add_status('토속성_강화', 15, 50)
        print(f"{caster.name}이 대지의 힘을 다스리게 되었습니다!")
        return True
    except Exception as e:
        print(f"대지 정령술사 효과 적용 중 오류: {e}")
        return False

def _earth_power(caster, target=None, skill_data=None):
    """대지의 힘 - 땅으로부터 힘을 얻음"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('대지의_힘', 10, 35)
            caster.status_manager.add_status('견고함', 10, 30)
        print(f"{caster.name}이 대지로부터 힘을 얻었습니다!")
        return True
    except Exception as e:
        print(f"대지의 힘 효과 적용 중 오류: {e}")
        return False

def _earth_resonance(caster, target=None, skill_data=None):
    """대지 공명 - 대지와 동조하여 안정성 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('대지_공명', 12, 25)
            caster.status_manager.remove_status('혼란')
            caster.status_manager.remove_status('공포')
        print(f"{caster.name}이 대지와 공명하여 정신이 안정되었습니다!")
        return True
    except Exception as e:
        print(f"대지 공명 효과 적용 중 오류: {e}")
        return False

def _electric_boost(caster, target=None, skill_data=None):
    """전기 강화 - 전기 계열 능력 증폭"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('전기_강화', 8, 40)
            caster.status_manager.add_status('번개_친화', 8, 30)
        print(f"{caster.name}의 전기 계열 능력이 강화되었습니다!")
        return True
    except Exception as e:
        print(f"전기 강화 효과 적용 중 오류: {e}")
        return False

def _electric_field(caster, target=None, skill_data=None):
    """전기장 - 주변에 전기 필드 생성"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('전기장', 15, 25)  # 적 접근 시 피해
        print(f"{caster.name} 주변에 전기장이 형성되었습니다!")
        return True
    except Exception as e:
        print(f"전기장 효과 적용 중 오류: {e}")
        return False

def _elemental_armor(caster, target=None, skill_data=None):
    """원소 갑옷 - 모든 원소 저항 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            elements = ['화염', '빙결', '번개', '독', '대지', '바람']
            for element in elements:
                caster.status_manager.add_status(f'{element}_저항', 20, 40)
        print(f"{caster.name}이 원소 갑옷으로 보호받고 있습니다!")
        return True
    except Exception as e:
        print(f"원소 갑옷 효과 적용 중 오류: {e}")
        return False

def _elemental_barrier(caster, target=None, skill_data=None):
    """원소 장벽 - 원소 공격 완전 차단"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('원소_장벽', 5, 100)  # 5턴간 원소 공격 무효
        print(f"{caster.name}이 원소 장벽에 보호받고 있습니다!")
        return True
    except Exception as e:
        print(f"원소 장벽 효과 적용 중 오류: {e}")
        return False

def _elemental_overload(caster, target=None, skill_data=None):
    """원소 과부하 - 원소 능력 극한 증폭"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('원소_과부하', 6, 80)  # 강력하지만 짧은 지속시간
            caster.status_manager.add_status('과부하_부작용', 6, -20)  # 부작용
        print(f"{caster.name}의 원소 능력이 과부하 상태가 되었습니다!")
        return True
    except Exception as e:
        print(f"원소 과부하 효과 적용 중 오류: {e}")
        return False

def _energy_absorption(caster, target, skill_data):
    """에너지 흡수 - 적의 에너지를 흡수"""
    try:
        if target and hasattr(target, 'current_mp'):
            absorbed = min(target.current_mp, 50)
            target.current_mp -= absorbed
            if hasattr(caster, 'current_mp'):
                caster.current_mp = min(caster.current_mp + absorbed, getattr(caster, 'max_mp', 100))
            print(f"{caster.name}이 {target.name}으로부터 {absorbed} MP를 흡수했습니다!")
        return True
    except Exception as e:
        print(f"에너지 흡수 효과 적용 중 오류: {e}")
        return False

def _energy_boost(caster, target=None, skill_data=None):
    """에너지 증진 - MP 회복량 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('에너지_증진', 12, 50)
        print(f"{caster.name}의 에너지 회복력이 증가했습니다!")
        return True
    except Exception as e:
        print(f"에너지 증진 효과 적용 중 오류: {e}")
        return False

def _energy_focus(caster, target=None, skill_data=None):
    """에너지 집중 - 모든 MP를 한 번에 집중"""
    try:
        if hasattr(caster, 'current_mp') and hasattr(caster, 'status_manager'):
            mp_boost = caster.current_mp // 2
            caster.current_mp -= mp_boost
            caster.status_manager.add_status('집중_에너지', 5, mp_boost)
        print(f"{caster.name}이 에너지를 집중했습니다!")
        return True
    except Exception as e:
        print(f"에너지 집중 효과 적용 중 오류: {e}")
        return False

def _energy_overload(caster, target=None, skill_data=None):
    """에너지 과부하 - 최대 MP 일시 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('에너지_과부하', 8, 100)  # 최대 MP 증가
            # MP 과소모 위험
            caster.status_manager.add_status('과부하_위험', 8, 0)
        print(f"{caster.name}의 에너지가 과부하 상태가 되었습니다!")
        return True
    except Exception as e:
        print(f"에너지 과부하 효과 적용 중 오류: {e}")
        return False

def _energy_recharge(caster, target=None, skill_data=None):
    """에너지 재충전 - MP 즉시 회복"""
    try:
        if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
            recharge_amount = min(80, caster.max_mp - caster.current_mp)
            caster.current_mp += recharge_amount
            print(f"{caster.name}의 MP가 {recharge_amount} 회복되었습니다!")
        return True
    except Exception as e:
        print(f"에너지 재충전 효과 적용 중 오류: {e}")
        return False

def _enhanced_accuracy(caster, target=None, skill_data=None):
    """정확도 향상 - 명중률과 크리티컬 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('정확도_향상', 10, 30)
            caster.status_manager.add_status('집중', 10, 20)
        print(f"{caster.name}의 정확도가 향상되었습니다!")
        return True
    except Exception as e:
        print(f"정확도 향상 효과 적용 중 오류: {e}")
        return False

def _enhanced_luck(caster, target=None, skill_data=None):
    """행운 증진 - 운 스탯 및 크리티컬 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('행운_증진', 15, 40)
        print(f"{caster.name}의 행운이 증진되었습니다!")
        return True
    except Exception as e:
        print(f"행운 증진 효과 적용 중 오류: {e}")
        return False

def _enhanced_reflexes(caster, target=None, skill_data=None):
    """반사신경 강화 - 회피율과 반격 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('반사신경_강화', 12, 35)
            caster.status_manager.add_status('반격_확률', 12, 25)
        print(f"{caster.name}의 반사신경이 강화되었습니다!")
        return True
    except Exception as e:
        print(f"반사신경 강화 효과 적용 중 오류: {e}")
        return False

def _eternal_flame(caster, target=None, skill_data=None):
    """영원한 불꽃 - 꺼지지 않는 화염 보호"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('영원한_불꽃', 25, 30)
            caster.status_manager.remove_status('빙결')
            caster.status_manager.remove_status('냉기')
        print(f"{caster.name}이 영원한 불꽃에 둘러싸였습니다!")
        return True
    except Exception as e:
        print(f"영원한 불꽃 효과 적용 중 오류: {e}")
        return False


# ========================================
# 7번째 배치: 고급 전투 및 전략 특수 효과들
# ========================================

def _evasion_boost(caster, target=None, skill_data=None):
    """회피 증진 - 회피율 대폭 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('회피_증진', 10, 45)
        print(f"{caster.name}의 회피 능력이 증진되었습니다!")
        return True
    except Exception as e:
        print(f"회피 증진 효과 적용 중 오류: {e}")
        return False

def _explosive_finish(caster, target, skill_data):
    """폭발 마무리 - 적 체력이 낮을수록 강한 폭발"""
    try:
        if target and skill_data:
            hp_ratio = getattr(target, 'current_hp', 100) / getattr(target, 'max_hp', 100)
            base_damage = skill_data.get('power', 120)
            explosion_damage = base_damage * (2 - hp_ratio)  # 체력 낮을수록 강함
            target.take_damage(explosion_damage, "폭발 마무리")
            print(f"{caster.name}의 폭발 마무리로 {target.name}에게 {explosion_damage:.0f} 피해!")
        return True
    except Exception as e:
        print(f"폭발 마무리 효과 적용 중 오류: {e}")
        return False

def _extra_turn(caster, target=None, skill_data=None):
    """추가 턴 - 다음 턴을 즉시 얻음"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('추가_턴', 1, 1)
        print(f"{caster.name}이 추가 턴을 얻었습니다!")
        return True
    except Exception as e:
        print(f"추가 턴 효과 적용 중 오류: {e}")
        return False

def _fire_affinity(caster, target=None, skill_data=None):
    """화염 친화 - 화염 계열 능력 강화"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('화염_친화', 15, 50)
            caster.status_manager.remove_status('빙결')
        print(f"{caster.name}이 화염과 친화되었습니다!")
        return True
    except Exception as e:
        print(f"화염 친화 효과 적용 중 오류: {e}")
        return False

def _fire_elementalist(caster, target=None, skill_data=None):
    """화염 정령술사 - 화염 원소 마스터리"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('화염_마스터리', 15, 60)
            caster.status_manager.add_status('화속성_강화', 15, 55)
        print(f"{caster.name}이 화염의 힘을 완전히 다스리게 되었습니다!")
        return True
    except Exception as e:
        print(f"화염 정령술사 효과 적용 중 오류: {e}")
        return False

def _fire_resist(caster, target=None, skill_data=None):
    """화염 저항 - 화염 피해 감소"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('화염_저항', 20, 60)
        print(f"{caster.name}이 화염에 저항력을 얻었습니다!")
        return True
    except Exception as e:
        print(f"화염 저항 효과 적용 중 오류: {e}")
        return False

def _flame_aura(caster, target=None, skill_data=None):
    """화염 오라 - 주변에 화염 보호막 생성"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('화염_오라', 18, 35)
        print(f"{caster.name} 주변에 화염 오라가 형성되었습니다!")
        return True
    except Exception as e:
        print(f"화염 오라 효과 적용 중 오류: {e}")
        return False

def _frost_armor(caster, target=None, skill_data=None):
    """서리 갑옷 - 빙결 보호와 반격 피해"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('서리_갑옷', 15, 40)
            caster.status_manager.add_status('빙결_면역', 15, 100)
        print(f"{caster.name}이 서리 갑옷을 두르고 있습니다!")
        return True
    except Exception as e:
        print(f"서리 갑옷 효과 적용 중 오류: {e}")
        return False

def _fury_mode(caster, target=None, skill_data=None):
    """분노 모드 - 공격력 대폭 증가, 방어력 감소"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('분노_모드', 8, 70)  # 공격력 70% 증가
            caster.status_manager.add_status('분노_취약', 8, -30)  # 방어력 30% 감소
        print(f"{caster.name}이 분노에 휩싸여 공격적이 되었습니다!")
        return True
    except Exception as e:
        print(f"분노 모드 효과 적용 중 오류: {e}")
        return False

def _gravity_control(caster, target, skill_data):
    """중력 조절 - 적의 행동 속도 감소"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('중력_압박', 8, 40)  # 속도 감소
            target.status_manager.add_status('무거움', 8, 30)
        print(f"{target.name}이 {caster.name}의 중력 조절에 짓눌렸습니다!")
        return True
    except Exception as e:
        print(f"중력 조절 효과 적용 중 오류: {e}")
        return False

def _guard_stance(caster, target=None, skill_data=None):
    """방어 자세 - 방어력 증가, 반격 확률 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('방어_자세', 10, 50)
            caster.status_manager.add_status('반격_준비', 10, 35)
        print(f"{caster.name}이 방어 자세를 취했습니다!")
        return True
    except Exception as e:
        print(f"방어 자세 효과 적용 중 오류: {e}")
        return False

def _healing_factor(caster, target=None, skill_data=None):
    """치유 인자 - 지속적인 자동 회복"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('치유_인자', 25, 20)  # 25턴간 턴마다 20 회복
        print(f"{caster.name}의 치유 인자가 활성화되었습니다!")
        return True
    except Exception as e:
        print(f"치유 인자 효과 적용 중 오류: {e}")
        return False

def _health_steal(caster, target, skill_data):
    """체력 흡수 - 적의 HP를 흡수"""
    try:
        if target and skill_data:
            steal_amount = skill_data.get('power', 60)
            if hasattr(target, 'current_hp'):
                actual_steal = min(steal_amount, target.current_hp)
                target.current_hp -= actual_steal
                if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
                    caster.current_hp = min(caster.current_hp + actual_steal, caster.max_hp)
                print(f"{caster.name}이 {target.name}으로부터 {actual_steal} HP를 흡수했습니다!")
        return True
    except Exception as e:
        print(f"체력 흡수 효과 적용 중 오류: {e}")
        return False

def _ice_armor(caster, target=None, skill_data=None):
    """얼음 갑옷 - 물리 피해 감소 및 냉기 보호"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('얼음_갑옷', 12, 45)
            caster.status_manager.add_status('냉기_면역', 12, 100)
        print(f"{caster.name}이 얼음 갑옷으로 보호받고 있습니다!")
        return True
    except Exception as e:
        print(f"얼음 갑옷 효과 적용 중 오류: {e}")
        return False

def _ice_elementalist(caster, target=None, skill_data=None):
    """빙결 정령술사 - 얼음 원소 마스터리"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('빙결_마스터리', 15, 55)
            caster.status_manager.add_status('빙속성_강화', 15, 50)
        print(f"{caster.name}이 얼음의 힘을 완전히 다스리게 되었습니다!")
        return True
    except Exception as e:
        print(f"빙결 정령술사 효과 적용 중 오류: {e}")
        return False

def _ice_resist(caster, target=None, skill_data=None):
    """빙결 저항 - 얼음 피해 및 빙결 효과 저항"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('빙결_저항', 20, 65)
            caster.status_manager.remove_status('빙결')
        print(f"{caster.name}이 얼음에 저항력을 얻었습니다!")
        return True
    except Exception as e:
        print(f"빙결 저항 효과 적용 중 오류: {e}")
        return False

def _ice_shield(caster, target=None, skill_data=None):
    """얼음 방패 - 일회성 피해 완전 차단"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('얼음_방패', 8, 1)  # 1회 완전 차단
        print(f"{caster.name}이 얼음 방패로 보호받고 있습니다!")
        return True
    except Exception as e:
        print(f"얼음 방패 효과 적용 중 오류: {e}")
        return False


# ========================================
# 8번째 배치: 마법 및 환상 특수 효과들
# ========================================

def _illusion_clone(caster, target=None, skill_data=None):
    """환상 분신 - 회피율 극대화"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('환상_분신', 8, 80)  # 회피율 80% 증가
        print(f"{caster.name}이 환상 분신을 만들어냈습니다!")
        return True
    except Exception as e:
        print(f"환상 분신 효과 적용 중 오류: {e}")
        return False

def _immunity_boost(caster, target=None, skill_data=None):
    """면역력 강화 - 모든 상태이상 저항"""
    try:
        if hasattr(caster, 'status_manager'):
            status_effects = ['독', '마비', '혼란', '기절', '공포', '매혹', '저주']
            for effect in status_effects:
                caster.status_manager.add_status(f'{effect}_저항', 15, 70)
        print(f"{caster.name}의 면역력이 강화되었습니다!")
        return True
    except Exception as e:
        print(f"면역력 강화 효과 적용 중 오류: {e}")
        return False

def _instant_teleport(caster, target=None, skill_data=None):
    """순간이동 - 즉시 안전한 위치로 이동"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('순간이동', 1, 0)  # 1턴간 공격 받지 않음
        print(f"{caster.name}이 순간이동했습니다!")
        return True
    except Exception as e:
        print(f"순간이동 효과 적용 중 오류: {e}")
        return False

def _invisible(caster, target=None, skill_data=None):
    """투명화 - 적의 타겟팅에서 제외"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('투명화', 5, 100)  # 5턴간 타겟팅 불가
        print(f"{caster.name}이 투명해졌습니다!")
        return True
    except Exception as e:
        print(f"투명화 효과 적용 중 오류: {e}")
        return False

def _lightning_strike(caster, target, skill_data):
    """번개 강타 - 강력한 전기 공격"""
    try:
        if target and skill_data:
            lightning_damage = skill_data.get('power', 150)
            target.take_damage(lightning_damage, "번개 강타")
            
            # 감전 효과
            if hasattr(target, 'status_manager'):
                target.status_manager.add_status('감전', 4, 20)
            
            print(f"{caster.name}의 번개가 {target.name}을 강타했습니다!")
        return True
    except Exception as e:
        print(f"번개 강타 효과 적용 중 오류: {e}")
        return False

def _magic_barrier(caster, target=None, skill_data=None):
    """마법 장벽 - 마법 피해 완전 차단"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마법_장벽', 6, 100)  # 6턴간 마법 공격 무효
        print(f"{caster.name}이 마법 장벽으로 보호받고 있습니다!")
        return True
    except Exception as e:
        print(f"마법 장벽 효과 적용 중 오류: {e}")
        return False

def _magic_counter(caster, target=None, skill_data=None):
    """마법 반격 - 마법 공격 받을 시 자동 반격"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마법_반격', 10, 40)
        print(f"{caster.name}이 마법 반격 자세를 취했습니다!")
        return True
    except Exception as e:
        print(f"마법 반격 효과 적용 중 오류: {e}")
        return False

def _magic_mirror(caster, target=None, skill_data=None):
    """마법 거울 - 마법 공격 반사"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마법_거울', 5, 80)  # 80% 확률로 반사
        print(f"{caster.name}이 마법 거울로 둘러싸였습니다!")
        return True
    except Exception as e:
        print(f"마법 거울 효과 적용 중 오류: {e}")
        return False

def _magic_resist(caster, target=None, skill_data=None):
    """마법 저항 - 마법 피해 감소"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마법_저항', 15, 50)
        print(f"{caster.name}이 마법에 저항력을 얻었습니다!")
        return True
    except Exception as e:
        print(f"마법 저항 효과 적용 중 오류: {e}")
        return False

def _meditation(caster, target=None, skill_data=None):
    """명상 - MP 회복 및 정신력 증가"""
    try:
        if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
            mp_recovery = min(100, caster.max_mp - caster.current_mp)
            caster.current_mp += mp_recovery
        
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('명상', 10, 30)
            caster.status_manager.remove_status('혼란')
        
        print(f"{caster.name}이 명상으로 정신을 집중했습니다!")
        return True
    except Exception as e:
        print(f"명상 효과 적용 중 오류: {e}")
        return False

def _mental_fortitude(caster, target=None, skill_data=None):
    """정신력 강화 - 정신 공격 저항"""
    try:
        if hasattr(caster, 'status_manager'):
            mental_effects = ['혼란', '공포', '매혹', '정신_지배']
            for effect in mental_effects:
                caster.status_manager.add_status(f'{effect}_저항', 20, 80)
        print(f"{caster.name}의 정신력이 강화되었습니다!")
        return True
    except Exception as e:
        print(f"정신력 강화 효과 적용 중 오류: {e}")
        return False

def _metamagic(caster, target=None, skill_data=None):
    """메타매직 - 다음 마법의 효과 강화"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('메타매직', 3, 100)  # 다음 3번의 마법 2배 효과
        print(f"{caster.name}이 메타매직을 준비했습니다!")
        return True
    except Exception as e:
        print(f"메타매직 효과 적용 중 오류: {e}")
        return False

def _mind_control(caster, target, skill_data):
    """정신 지배 - 적을 일시적으로 조종"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('정신_지배', 3, 0)  # 3턴간 조종
        print(f"{target.name}이 {caster.name}의 정신 지배에 걸렸습니다!")
        return True
    except Exception as e:
        print(f"정신 지배 효과 적용 중 오류: {e}")
        return False

def _mirror_image(caster, target=None, skill_data=None):
    """거울상 - 여러 개의 분신 생성"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('거울상', 10, 60)  # 회피율 증가
            mirror_count = 3
            for i in range(mirror_count):
                caster.status_manager.add_status(f'분신_{i+1}', 10, 20)
        print(f"{caster.name}이 {mirror_count}개의 거울상을 만들어냈습니다!")
        return True
    except Exception as e:
        print(f"거울상 효과 적용 중 오류: {e}")
        return False

def _phase_shift(caster, target=None, skill_data=None):
    """위상 변환 - 물리 공격 회피"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('위상_변환', 4, 90)  # 4턴간 물리 공격 90% 회피
        print(f"{caster.name}이 위상을 변환하여 흐릿해졌습니다!")
        return True
    except Exception as e:
        print(f"위상 변환 효과 적용 중 오류: {e}")
        return False


# ========================================
# 최종 대용량 배치: 남은 모든 특수 효과들
# ========================================

def _poison_resist(caster, target=None, skill_data=None):
    """독 저항"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('독_저항', 25, 80)
        return True
    except: return False

def _power_up(caster, target=None, skill_data=None):
    """파워 업"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('파워_업', 12, 40)
        return True
    except: return False

def _precision_strike(caster, target, skill_data):
    """정밀 타격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 120) * 1.5  # 크리티컬 확정
            target.take_damage(damage, "정밀 타격")
        return True
    except: return False

def _quick_cast(caster, target=None, skill_data=None):
    """빠른 시전"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('빠른_시전', 8, 50)
        return True
    except: return False

def _rage_mode(caster, target=None, skill_data=None):
    """분노 모드"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('분노', 10, 60)
            caster.status_manager.add_status('분노_취약', 10, -20)
        return True
    except: return False

def _rapid_fire(caster, target, skill_data):
    """연사"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 50)
            for i in range(3):
                target.take_damage(damage, f"연사 {i+1}")
        return True
    except: return False

def _restore_mp(caster, target=None, skill_data=None):
    """MP 회복"""
    try:
        if hasattr(caster, 'current_mp') and hasattr(caster, 'max_mp'):
            caster.current_mp = min(caster.current_mp + 120, caster.max_mp)
        return True
    except: return False

def _revival(caster, target=None, skill_data=None):
    """부활"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('부활_보험', 1, 50)  # 1회 50% HP로 부활
        return True
    except: return False

def _shadow_step(caster, target=None, skill_data=None):
    """그림자 이동"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('그림자_이동', 5, 70)
        return True
    except: return False

def _shield_bash(caster, target, skill_data):
    """방패 강타"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 80)
            target.take_damage(damage, "방패 강타")
            if hasattr(target, 'status_manager'):
                target.status_manager.add_status('기절', 2, 0)
        return True
    except: return False

def _shock_wave(caster, target, skill_data):
    """충격파"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 110)
            target.take_damage(damage, "충격파")
        return True
    except: return False

def _silence(caster, target, skill_data):
    """침묵"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('침묵', 5, 0)
        return True
    except: return False

def _slow(caster, target, skill_data):
    """둔화"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('둔화', 8, 40)
        return True
    except: return False

def _spell_steal(caster, target, skill_data):
    """마법 훔치기"""
    try:
        if target and hasattr(target, 'status_manager'):
            # 상대방의 버프를 훔쳐옴
            buffs = ['공격력_증가', '방어력_증가', '속도_증가']
            for buff in buffs:
                if target.status_manager.has_status(buff):
                    target.status_manager.remove_status(buff)
                    if hasattr(caster, 'status_manager'):
                        caster.status_manager.add_status(buff, 8, 30)
        return True
    except: return False

def _stun(caster, target, skill_data):
    """기절"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('기절', 3, 0)
        return True
    except: return False

def _summon_elemental(caster, target=None, skill_data=None):
    """정령 소환"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('정령_동료', 20, 50)
        return True
    except: return False

def _teleport_strike(caster, target, skill_data):
    """순간이동 공격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 140)
            target.take_damage(damage, "순간이동 공격")
        return True
    except: return False

def _weather_control(caster, target=None, skill_data=None):
    """날씨 조절"""
    try:
        if hasattr(caster, 'status_manager'):
            import random
            weather = random.choice(['폭풍', '번개', '눈보라', '안개'])
            caster.status_manager.add_status(f'{weather}_날씨', 15, 30)
        return True
    except: return False

def _wind_barrier(caster, target=None, skill_data=None):
    """바람 장벽"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('바람_장벽', 12, 40)
        return True
    except: return False

def _wind_elementalist(caster, target=None, skill_data=None):
    """바람 정령술사"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('바람_마스터리', 15, 55)
        return True
    except: return False

def _wound_healing(caster, target=None, skill_data=None):
    """상처 치유"""
    try:
        heal_target = target if target else caster
        if hasattr(heal_target, 'wounds'):
            heal_target.wounds = max(0, heal_target.wounds - 100)
        return True
    except: return False

def _absorb_power(caster, target, skill_data):
    """힘 흡수"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('힘_흡수', 8, -30)
            if hasattr(caster, 'status_manager'):
                caster.status_manager.add_status('흡수된_힘', 8, 30)
        return True
    except: return False

def _acid_splash(caster, target, skill_data):
    """산성 물질"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 90)
            target.take_damage(damage, "산성 공격")
            if hasattr(target, 'status_manager'):
                target.status_manager.add_status('부식', 6, 15)
        return True
    except: return False

def _ancient_power(caster, target=None, skill_data=None):
    """고대의 힘"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('고대의_힘', 12, 80)
        return True
    except: return False

def _battle_frenzy(caster, target=None, skill_data=None):
    """전투 광기"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('전투_광기', 15, 100)
        return True
    except: return False

def _blood_pact(caster, target=None, skill_data=None):
    """혈액 계약"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('혈액_계약', 20, 50)
        return True
    except: return False

def _chaos_bolt(caster, target, skill_data):
    """혼돈의 화살"""
    try:
        if target and skill_data:
            import random
            damage = random.randint(50, 200)  # 랜덤 피해
            target.take_damage(damage, "혼돈의 화살")
        return True
    except: return False

def _curse_break(caster, target=None, skill_data=None):
    """저주 해제"""
    try:
        heal_target = target if target else caster
        if hasattr(heal_target, 'status_manager'):
            curses = ['저주', '악마의_저주', '사악한_저주']
            for curse in curses:
                heal_target.status_manager.remove_status(curse)
        return True
    except: return False

def _earth_shake(caster, target, skill_data):
    """지진"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 130)
            target.take_damage(damage, "지진")
        return True
    except: return False

def _energy_drain(caster, target, skill_data):
    """에너지 흡수"""
    try:
        if target and hasattr(target, 'current_mp'):
            drained = min(target.current_mp, 60)
            target.current_mp -= drained
            if hasattr(caster, 'current_mp'):
                caster.current_mp += drained
        return True
    except: return False

def _final_strike(caster, target, skill_data):
    """최후의 일격"""
    try:
        if target and skill_data:
            hp_ratio = getattr(caster, 'current_hp', 100) / getattr(caster, 'max_hp', 100)
            damage = skill_data.get('power', 200) * (2 - hp_ratio)
            target.take_damage(damage, "최후의 일격")
        return True
    except: return False

def _flame_burst(caster, target, skill_data):
    """화염 폭발"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 160)
            target.take_damage(damage, "화염 폭발")
        return True
    except: return False

def _force_field(caster, target=None, skill_data=None):
    """역장"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('역장', 8, 80)
        return True
    except: return False

def _frost_nova(caster, target, skill_data):
    """서리 폭발"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 120)
            target.take_damage(damage, "서리 폭발")
            if hasattr(target, 'status_manager'):
                target.status_manager.add_status('빙결', 4, 0)
        return True
    except: return False

def _ice_blast(caster, target, skill_data):
    """얼음 폭발"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 140)
            target.take_damage(damage, "얼음 폭발")
        return True
    except: return False

def _invisible_strike(caster, target, skill_data):
    """은신 공격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 150)  # 필중 + 크리티컬
            target.take_damage(damage, "은신 공격")
        return True
    except: return False

def _mass_heal(caster, target=None, skill_data=None):
    """대규모 치유"""
    try:
        if hasattr(caster, 'current_hp') and hasattr(caster, 'max_hp'):
            heal_amount = 150
            caster.current_hp = min(caster.current_hp + heal_amount, caster.max_hp)
        return True
    except: return False

def _meteor_strike(caster, target, skill_data):
    """유성 충돌"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 250)
            target.take_damage(damage, "유성 충돌")
        return True
    except: return False

def _poison_cloud(caster, target, skill_data):
    """독 구름"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('독_구름', 10, 25)
        return True
    except: return False

def _power_drain(caster, target, skill_data):
    """힘 빼기"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('힘_감소', 8, -40)
        return True
    except: return False

def _psychic_blast(caster, target, skill_data):
    """정신 공격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 110)
            target.take_damage(damage, "정신 공격")
        return True
    except: return False

def _shadow_bind(caster, target, skill_data):
    """그림자 속박"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('그림자_속박', 6, 0)
        return True
    except: return False

def _soul_burn(caster, target, skill_data):
    """영혼 연소"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 100)
            target.take_damage(damage, "영혼 연소")
        return True
    except: return False

def _spell_break(caster, target, skill_data):
    """마법 해제"""
    try:
        if target and hasattr(target, 'status_manager'):
            buffs = ['마법_강화', '원소_강화', '마력_증진']
            for buff in buffs:
                target.status_manager.remove_status(buff)
        return True
    except: return False

def _thunder_storm(caster, target, skill_data):
    """뇌우"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 170)
            target.take_damage(damage, "뇌우")
        return True
    except: return False

def _time_warp(caster, target=None, skill_data=None):
    """시간 왜곡 - 시간을 왜곡하여 특별한 효과 발동"""
    try:
        print(f"⏰🌪️ {caster.name}이(가) 시간을 왜곡시킵니다!")
        
        # 전장의 모든 적과 아군에게 시간 왜곡 효과 적용
        if hasattr(caster, 'status_manager'):
            # 시전자는 시간 왜곡의 주인이므로 이득 효과
            from .character import StatusEffect
            time_effect = StatusEffect(StatusType.TIME_DISTORTION, 5, 1.0)
            caster.status_manager.add_status(time_effect)
            print(f"⏰ {caster.name}은(는) 시간 왜곡의 중심에서 시공간을 조작합니다!")
        
        return True
    except Exception as e:
        print(f"❌ 시간 왜곡 시전 실패: {e}")
        return False

def _tornado(caster, target, skill_data):
    """토네이도"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 155)
            target.take_damage(damage, "토네이도")
        return True
    except: return False

def _undead_army(caster, target=None, skill_data=None):
    """언데드 군단"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('언데드_군단', 30, 100)
        return True
    except: return False

def _void_strike(caster, target, skill_data):
    """공허 공격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 200)
            target.take_damage(damage, "공허 공격")
        return True
    except: return False

def _war_cry(caster, target=None, skill_data=None):
    """전쟁의 함성"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('전쟁의_함성', 12, 50)
        return True
    except: return False

def _weakness(caster, target, skill_data):
    """약화"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('약화', 10, -35)
        return True
    except: return False

def _wind_slash(caster, target, skill_data):
    """바람 베기"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 115)
            target.take_damage(damage, "바람 베기")
        return True
    except: return False

def _winter_storm(caster, target, skill_data):
    """겨울 폭풍"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 145)
            target.take_damage(damage, "겨울 폭풍")
        return True
    except: return False

# 추가 간단 효과들 (남은 공간 채우기용)
def _action_surge(caster, target=None, skill_data=None):
    """행동 급증"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('행동_급증', 5, 50)
        return True
    except: return False

def _adrenaline_rush(caster, target=None, skill_data=None):
    """아드레날린 분출"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('아드레날린', 8, 60)
        return True
    except: return False

def _agility_boost(caster, target=None, skill_data=None):
    """민첩성 증가"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('민첩성_증가', 12, 40)
        return True
    except: return False

def _all_stats_up(caster, target=None, skill_data=None):
    """모든 능력치 상승"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('전능력_상승', 15, 30)
        return True
    except: return False

def _amplify_magic(caster, target=None, skill_data=None):
    """마법 증폭"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마법_증폭_강화', 10, 70)
        return True
    except: return False

def _ancient_wisdom(caster, target=None, skill_data=None):
    """고대의 지혜"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('고대의_지혜', 20, 45)
        return True
    except: return False

def _angel_blessing(caster, target=None, skill_data=None):
    """천사의 축복"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('천사의_축복', 25, 35)
        return True
    except: return False

def _animal_instinct(caster, target=None, skill_data=None):
    """야생의 본능"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('야생의_본능', 12, 55)
        return True
    except: return False

def _arcane_power(caster, target=None, skill_data=None):
    """비전의 힘"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('비전의_힘', 15, 65)
        return True
    except: return False

def _astral_projection(caster, target=None, skill_data=None):
    """영혼 투사"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('영혼_투사', 6, 90)
        return True
    except: return False

def _avatar_form(caster, target=None, skill_data=None):
    """아바타 형태"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('아바타_형태', 20, 100)
        return True
    except: return False

def _berserk_mode(caster, target=None, skill_data=None):
    """광전사 모드"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('광전사_모드', 12, 150)
        return True
    except: return False

def _blade_dance(caster, target, skill_data):
    """검무"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 70)
            for i in range(4):  # 4번 공격
                target.take_damage(damage, f"검무 {i+1}")
        return True
    except: return False

def _blood_magic(caster, target=None, skill_data=None):
    """혈액 마법"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('혈액_마법', 10, 80)
        return True
    except: return False

def _bone_armor(caster, target=None, skill_data=None):
    """뼈 갑옷"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('뼈_갑옷', 18, 50)
        return True
    except: return False

def _chain_lightning(caster, target, skill_data):
    """연쇄 번개"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 120)
            target.take_damage(damage, "연쇄 번개")
        return True
    except: return False

def _chaos_magic(caster, target=None, skill_data=None):
    """혼돈 마법"""
    try:
        if hasattr(caster, 'status_manager'):
            import random
            effect_value = random.randint(20, 100)
            caster.status_manager.add_status('혼돈_마법', 8, effect_value)
        return True
    except: return False

def _charm(caster, target, skill_data):
    """매혹"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('매혹', 5, 0)
        return True
    except: return False

def _clone_strike(caster, target, skill_data):
    """분신 공격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 90)
            target.take_damage(damage * 2, "분신 공격")  # 2배 피해
        return True
    except: return False

def _combat_reflexes(caster, target=None, skill_data=None):
    """전투 반사신경"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('전투_반사신경', 12, 45)
        return True
    except: return False

def _crystal_barrier(caster, target=None, skill_data=None):
    """수정 장벽"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('수정_장벽', 10, 70)
        return True
    except: return False

def _curse_of_weakness(caster, target, skill_data):
    """약화의 저주"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('약화의_저주', 15, -50)
        return True
    except: return False

def _darkness_shroud(caster, target=None, skill_data=None):
    """어둠의 장막"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('어둠의_장막', 8, 60)
        return True
    except: return False

def _death_touch(caster, target, skill_data):
    """죽음의 손길"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 300)  # 강력한 단일 공격
            target.take_damage(damage, "죽음의 손길")
        return True
    except: return False

def _demon_form(caster, target=None, skill_data=None):
    """악마 형태"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('악마_형태', 15, 120)
        return True
    except: return False

def _divine_favor(caster, target=None, skill_data=None):
    """신의 은총"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('신의_은총', 20, 40)
        return True
    except: return False

def _earthquake(caster, target, skill_data):
    """대지진"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 180)
            target.take_damage(damage, "대지진")
        return True
    except: return False

def _elemental_fury(caster, target=None, skill_data=None):
    """원소의 분노"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('원소의_분노', 12, 85)
        return True
    except: return False

def _enchanted_weapon(caster, target=None, skill_data=None):
    """마법 무기"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마법_무기', 25, 50)
        return True
    except: return False

def _eternal_guard(caster, target=None, skill_data=None):
    """영원한 수호"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('영원한_수호', 30, 75)
        return True
    except: return False

def _fire_storm(caster, target, skill_data):
    """화염 폭풍"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 190)
            target.take_damage(damage, "화염 폭풍")
        return True
    except: return False

def _ghost_form(caster, target=None, skill_data=None):
    """유령 형태"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('유령_형태', 8, 85)
        return True
    except: return False

def _giant_strength(caster, target=None, skill_data=None):
    """거인의 힘"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('거인의_힘', 15, 100)
        return True
    except: return False

def _haste(caster, target=None, skill_data=None):
    """가속"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('가속', 10, 60)
        return True
    except: return False

def _ice_storm(caster, target, skill_data):
    """얼음 폭풍"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 175)
            target.take_damage(damage, "얼음 폭풍")
        return True
    except: return False

def _iron_skin(caster, target=None, skill_data=None):
    """강철 피부"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('강철_피부', 15, 80)
        return True
    except: return False

def _last_stand(caster, target=None, skill_data=None):
    """최후의 저항"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('최후의_저항', 8, 200)
        return True
    except: return False

def _light_speed(caster, target=None, skill_data=None):
    """광속"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('광속', 5, 150)
        return True
    except: return False

def _mage_armor(caster, target=None, skill_data=None):
    """마법사 갑옷"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('마법사_갑옷', 20, 40)
        return True
    except: return False

def _mass_confusion(caster, target, skill_data):
    """대혼란"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('대혼란', 8, 0)
        return True
    except: return False

def _nature_blessing(caster, target=None, skill_data=None):
    """자연의 축복"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('자연의_축복', 25, 45)
        return True
    except: return False

def _perfect_defense(caster, target=None, skill_data=None):
    """완벽한 방어"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('완벽한_방어', 3, 100)
        return True
    except: return False

def _phoenix_rebirth(caster, target=None, skill_data=None):
    """불사조의 환생"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('불사조_환생', 1, 100)
        return True
    except: return False

def _poison_strike(caster, target, skill_data):
    """독 공격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 85)
            target.take_damage(damage, "독 공격")
            if hasattr(target, 'status_manager'):
                target.status_manager.add_status('독', 8, 20)
        return True
    except: return False

def _protect_ally(caster, target=None, skill_data=None):
    """동료 보호"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('동료_보호', 12, 50)
        return True
    except: return False

def _rage_strike(caster, target, skill_data):
    """분노의 일격"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 140)
            target.take_damage(damage, "분노의 일격")
        return True
    except: return False

def _reflect_damage(caster, target=None, skill_data=None):
    """피해 반사"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('피해_반사', 10, 50)
        return True
    except: return False

def _sacred_light(caster, target=None, skill_data=None):
    """성스러운 빛"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('성스러운_빛', 15, 55)
        return True
    except: return False

def _spirit_form(caster, target=None, skill_data=None):
    """영혼 형태"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('영혼_형태', 6, 80)
        return True
    except: return False

def _stone_skin(caster, target=None, skill_data=None):
    """돌 피부"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('돌_피부', 20, 60)
        return True
    except: return False

def _ultimate_power(caster, target=None, skill_data=None):
    """궁극의 힘"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('궁극의_힘', 10, 200)
        return True
    except: return False

def _vampire_bite(caster, target, skill_data):
    """흡혈귀의 이빨"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 95)
            target.take_damage(damage, "흡혈귀의 이빨")
            if hasattr(caster, 'current_hp'):
                caster.current_hp += damage * 0.7
        return True
    except: return False

def _void_magic(caster, target=None, skill_data=None):
    """공허 마법"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('공허_마법', 12, 90)
        return True
    except: return False

def _wall_of_force(caster, target=None, skill_data=None):
    """힘의 벽"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.add_status('힘의_벽', 15, 100)
        return True
    except: return False

def _whirlwind(caster, target, skill_data):
    """회오리바람"""
    try:
        if target and skill_data:
            damage = skill_data.get('power', 125)
            target.take_damage(damage, "회오리바람")
        return True
    except: return False

def _wild_magic(caster, target=None, skill_data=None):
    """야생 마법"""
    try:
        if hasattr(caster, 'status_manager'):
            import random
            effects = ['야생_마법_1', '야생_마법_2', '야생_마법_3']
            effect = random.choice(effects)
            caster.status_manager.add_status(effect, 10, random.randint(30, 80))
        return True
    except: return False

def _zone_of_silence(caster, target, skill_data):
    """침묵 구역"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('침묵_구역', 12, 0)
        return True
    except: return False

def _cure_all(caster, target=None, skill_data=None):
    """모든 상태이상 치료"""
    try:
        if hasattr(caster, 'status_manager'):
            caster.status_manager.clear_all_negative_status()
        return True
    except Exception as e:
        print(f"치료 효과 적용 중 오류: {e}")
        return False

# ========================================
# 누락된 특수 효과 함수들 (중복 제거됨)
# ========================================
    return False

def _enemy_analysis(caster):
    """적 분석 - 전사 전술 스킬"""
    if hasattr(caster, 'character_class') and caster.character_class == "전사":
        if not hasattr(caster, 'enemy_data'):
            caster.enemy_data = {}
        
        print(f"🔍 {caster.name}이(가) 적의 약점을 분석합니다!")
        
        # 다음 공격 명중률 및 크리티컬 확률 증가
        if hasattr(caster, 'add_temp_effect'):
            caster.add_temp_effect("accuracy_boost", 1.3)
            caster.add_temp_effect("crit_boost", 1.2)
        return True
    return False

def _guardian_bonus(caster):
    """수호자 보너스 - 전사 수호 자세"""
    if hasattr(caster, 'character_class') and caster.character_class == "전사":
        print(f"🛡️ {caster.name}이(가) 수호자 자세로 방어력을 강화합니다!")
        
        # 방어력 증가 및 아군 보호 효과
        if hasattr(caster, 'add_temp_effect'):
            caster.add_temp_effect("defense_boost", 1.4)
            caster.add_temp_effect("protect_allies", 1.0)
        return True
    return False

def _elemental_weakness(caster, target=None, skill_data=None):
    """원소 약점 부여 - 적에게 원소 약점 상태 부여"""
    try:
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('원소_약점', 8, 30)  # 8턴간 원소 피해 30% 증가
        print(f"{target.name if target else '대상'}에게 원소 약점을 부여했습니다!")
        return True
    except Exception as e:
        print(f"원소 약점 효과 적용 중 오류: {e}")
        return False

def _deadly_poison(caster, target=None, skill_data=None):
    """치명독 - 도적 공격력 기반 강력한 독 상태이상 부여"""
    try:
        if not target:
            return False
        
        # 도적 공격력 기반 치명독 강도 계산
        caster_attack = getattr(caster, 'physical_attack', 100)
        # 공격력의 35%를 독 강도로 사용 (최소 70, 최대 99999)
        deadly_poison_intensity = max(70, min(99999, int(caster_attack * 0.35)))
        
        if target and hasattr(target, 'status_manager'):
            target.status_manager.add_status('치명독', 10, deadly_poison_intensity)  # 10턴간 강력한 독
        print(f"{target.name if target else '대상'}에게 치명적인 맹독을 주입했습니다! (독성: {deadly_poison_intensity})")
        return True
    except Exception as e:
        print(f"치명독 효과 적용 중 오류: {e}")
        return False

def _poison_amplify(caster, target=None, skill_data=None):
    """독 증폭 - 도적 공격력 기반으로 기존 독 효과 강화"""
    try:
        if not target:
            return False
        
        # 도적 공격력 기반 증폭 계수 계산
        caster_attack = getattr(caster, 'physical_attack', 100)
        # 공격력이 높을수록 증폭 효과 증가 (1.3배 ~ 2.5배)
        amplify_factor = 1.3 + (caster_attack / 500.0)  # 최대 2.3배
        amplify_factor = min(2.5, max(1.3, amplify_factor))
        
        if target and hasattr(target, 'status_manager'):
            # 기존 독 효과가 있으면 강화
            if target.status_manager.has_status('독'):
                target.status_manager.amplify_status('독', amplify_factor)
                print(f"{target.name if target else '대상'}의 독이 {amplify_factor:.1f}배 증폭되었습니다!")
            else:
                # 독이 없으면 새로 부여 (도적 공격력 기반)
                new_poison_intensity = max(60, int(caster_attack * 0.2))
                target.status_manager.add_status('독', 6, new_poison_intensity)
                print(f"{target.name if target else '대상'}에게 맹독을 주입했습니다! (독성: {new_poison_intensity})")
        return True
    except Exception as e:
        print(f"독 증폭 효과 적용 중 오류: {e}")
        return False


def _magnetic_field_manipulation(caster, target, skill_data):
    """자기장 조작 - 아군 금속 장비 강화"""
    try:
        if hasattr(caster, 'party_members'):
            for ally in caster.party_members:
                if ally and ally.is_alive:
                    # 금속 장비 보너스 적용 (아군만)
                    ally.temp_equipment_bonus = getattr(ally, 'temp_equipment_bonus', 1.0) * 1.2
                    print(f"⚡ {ally.name}의 금속 장비가 강화되었습니다!")
        return True
    except: 
        return False

def _emp_explosion(caster, target, skill_data):
    """EMP 폭발 - 적 전체 피해 + 장비 무력화"""
    try:
        if hasattr(caster, 'get_enemies'):
            enemies = caster.get_enemies()
            for enemy in enemies:
                if enemy and enemy.is_alive:
                    # 피해 적용
                    enemy.take_damage(500, "EMP 폭발")
                    # 적의 장비 효과 무력화 (임시)
                    if hasattr(enemy, 'status_manager'):
                        from .status_effects import StatusEffect
                        enemy.status_manager.add_status(
                            StatusEffect("장비무력화", "장비무력화", 2, -50)
                        )
                    print(f"💥 {enemy.name}의 장비가 무력화되었습니다!")
        return True
    except: 
        return False

def _robot_summon(caster, target, skill_data):
    """로봇 소환 - 전투 로봇 소환"""
    try:
        if hasattr(caster, 'summon_ally'):
            # 전투 로봇 소환 (임시 동료)
            robot_stats = {
                'name': '전투로봇',
                'hp': 300,
                'attack': 150,
                'duration': 3
            }
            caster.summon_ally(robot_stats)
            print(f"🤖 {caster.name}이(가) 전투로봇을 소환했습니다!")
        return True
    except: 
        return False


def _note_attack(caster, target, skill_data):
    """음표 발사 - 단일 적 공격"""
    try:
        if target and target.is_alive:
            target.take_damage(180, "음표 공격")
            if hasattr(target, 'status_manager'):
                from .status_effects import StatusEffect
                target.status_manager.add_status(
                    StatusEffect("혼란", "혼란", 2, -20)
                )
            print(f"🎵 {target.name}이(가) 음표 공격으로 혼란에 빠졌습니다!")
        return True
    except: 
        return False

def _sound_amplification(caster, target, skill_data):
    """음향 증폭 - 전체 적 공격"""
    try:
        if hasattr(caster, 'get_enemies'):
            enemies = caster.get_enemies()
            for enemy in enemies:
                if enemy and enemy.is_alive:
                    enemy.take_damage(120, "음향 증폭")
                    if hasattr(enemy, 'status_manager'):
                        from .status_effects import StatusEffect
                        enemy.status_manager.add_status(
                            StatusEffect("기절", "기절", 1, -100)
                        )
            print(f"🔊 음향 증폭으로 적들이 기절했습니다!")
        return True
    except: 
        return False

def _harmony_heal(caster, target, skill_data):
    """화음 치료 - 아군 전체 회복"""
    try:
        if hasattr(caster, 'party_members'):
            for ally in caster.party_members:
                if ally and ally.is_alive:
                    old_hp = ally.current_hp
                    ally.current_hp = min(ally.max_hp, ally.current_hp + 180)
                    actual_heal = ally.current_hp - old_hp
                    if actual_heal > 0:
                        print(f"💚 {ally.name}이(가) {actual_heal} HP 회복!")
                    
                    # 상태이상 1개 해제
                    if hasattr(ally, 'status_manager'):
                        ally.status_manager.remove_random_debuff()
        return True
    except: 
        return False


def _soul_strike(caster, target, skill_data):
    """영혼 타격 - 마법 기반 공격 + MP 감소"""
    try:
        if target and target.is_alive:
            # 마법 공격력 기반 피해
            magic_bonus = getattr(caster, 'magic_attack', 20)
            damage = 250 + int(magic_bonus * 0.5)
            target.take_damage(damage, "영혼 타격", damage_type="magic")
            
            # MP 감소
            if hasattr(target, 'current_mp'):
                target.current_mp = max(0, target.current_mp - 50)
                print(f"💜 {target.name}의 MP가 50 감소했습니다!")
            
            print(f"👻 {target.name}이(가) 영혼 타격으로 {damage} 피해!")
        return True
    except: 
        return False

def _soul_separation(caster, target, skill_data):
    """영혼 분리 - 즉사 또는 강력한 피해"""
    try:
        if target and target.is_alive:
            # HP 30% 이하면 즉사
            if target.current_hp <= target.max_hp * 0.3:
                target.current_hp = 0
                print(f"💀 {target.name}의 영혼이 분리되어 즉사했습니다!")
            else:
                # 아니면 강력한 피해 + 마비
                magic_bonus = getattr(caster, 'magic_attack', 20)
                damage = 400 + int(magic_bonus * 0.8)
                target.take_damage(damage, "영혼 분리", damage_type="magic")
                
                if hasattr(target, 'status_manager'):
                    from .status_effects import StatusEffect
                    target.status_manager.add_status(
                        StatusEffect("마비", "마비", 2, -80)
                    )
                print(f"👻 {target.name}이(가) 영혼 분리로 {damage} 피해 + 마비!")
        return True
    except: 
        return False

def _ancestor_summon(caster, target, skill_data):
    """조상 소환 - 조상령 소환 + 아군 강화"""
    try:
        # 조상령 소환
        if hasattr(caster, 'summon_ally'):
            ancestor_stats = {
                'name': '조상령',
                'hp': 400,
                'magic_attack': 200,
                'duration': 4
            }
            caster.summon_ally(ancestor_stats)
            print(f"🌟 {caster.name}이(가) 조상령을 소환했습니다!")
        
        # 아군 전체 강화
        if hasattr(caster, 'party_members'):
            for ally in caster.party_members:
                if ally and ally.is_alive:
                    ally.temp_all_stats_bonus = getattr(ally, 'temp_all_stats_bonus', 1.0) * 1.15
                    print(f"✨ {ally.name}이(가) 조상의 축복을 받았습니다!")
        return True
    except: 
        return False

# ========================================
# 누락된 특수 효과 함수들 구현
# ========================================

def _dragon_awakening(caster, target, skill_data):
    """용의 각성 - 용기사 궁극 변신"""
    try:
        if hasattr(caster, 'status_manager'):
            from .status_effects import StatusType
            caster.status_manager.add_status(StatusType.BUFF, 10, 100)  # 10턴간 모든 능력치 2배
            print(f"🐉 {caster.name}이 용의 힘으로 각성합니다!")
        return True
    except:
        return False

def _magic_storm(caster, target, skill_data):
    """마법 폭풍 - 광범위 마법 공격"""
    try:
        damage = int(caster.magic_attack * 2.5)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            print(f"🌪️ 마법 폭풍으로 {target.name}에게 {damage} 피해!")
        return True
    except:
        return False

def _shadow_echo(caster, target, skill_data):
    """그림자 메아리 - 그림자 수만큼 추가 공격"""
    try:
        shadow_count = getattr(caster, 'shadow_count', 0)
        if shadow_count > 0:
            echo_damage = int(caster.attack * 0.3 * shadow_count)
            if target and hasattr(target, 'current_hp'):
                target.current_hp = max(0, target.current_hp - echo_damage)
                print(f"👤 그림자 메아리로 {echo_damage} 추가 피해!")
        return True
    except:
        return False

def _absolute_defense(caster, target, skill_data):
    """절대 방어 - 완전 무적"""
    try:
        if hasattr(caster, 'status_manager'):
            from .status_effects import StatusType
            caster.status_manager.add_status(StatusType.INVINCIBLE, 3, 1.0)  # 3턴간 무적
            print(f"🛡️ {caster.name}이 절대 방어 상태가 됩니다!")
        return True
    except:
        return False

def _dark_blessing(caster, target, skill_data):
    """어둠의 축복 - 어둠 속성 강화"""
    try:
        if hasattr(caster, 'status_manager'):
            from .status_effects import StatusType
            caster.status_manager.add_status(StatusType.DARK_POWER, 5, 50)  # 5턴간 어둠 공격력 +50%
            print(f"🌑 {caster.name}이 어둠의 힘을 받습니다!")
        return True
    except:
        return False

def _fury_blow(caster, target, skill_data):
    """분노의 일격 - 분노에 비례한 강력한 공격"""
    try:
        rage_multiplier = getattr(caster, 'rage_level', 1)
        damage = int(caster.attack * 1.5 * rage_multiplier)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            print(f"💢 분노의 일격으로 {target.name}에게 {damage} 피해!")
        return True
    except:
        return False

def _soul_song(caster, target, skill_data):
    """영혼의 노래 - 아군 회복 + 적 혼란"""
    try:
        if target and hasattr(target, 'character_class'):
            # 아군이면 회복
            if hasattr(caster, 'party') and target in caster.party:
                heal = int(caster.magic_attack * 0.8)
                max_hp = getattr(target, 'max_hp', target.current_hp)
                target.current_hp = min(max_hp, target.current_hp + heal)
                print(f"🎵 영혼의 노래로 {target.name}이 {heal} 회복!")
            else:
                # 적이면 혼란
                if hasattr(target, 'status_manager'):
                    from .status_effects import StatusType
                    target.status_manager.add_status(StatusType.CONFUSION, 3, 1.0)
                    print(f"🎵 영혼의 노래로 {target.name}이 혼란에 빠집니다!")
        return True
    except:
        return False

def _shadow_strike(caster, target, skill_data):
    """그림자 타격 - 은밀한 공격"""
    try:
        damage = int(caster.attack * 1.3)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            # 그림자 생성
            shadow_count = getattr(caster, 'shadow_count', 0)
            caster.shadow_count = min(shadow_count + 1, 5)  # 최대 5개
            print(f"🌑 그림자 타격으로 {target.name}에게 {damage} 피해! (그림자 +1)")
        return True
    except:
        return False

def _laser_shot(caster, target, skill_data):
    """레이저 사격 - 정확한 에너지 공격"""
    try:
        damage = int(caster.magic_attack * 1.2)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            print(f"⚡ 레이저 사격으로 {target.name}에게 {damage} 피해!")
        return True
    except:
        return False

def _mega_laser(caster, target, skill_data):
    """메가 레이저 - 강력한 에너지 광선"""
    try:
        damage = int(caster.magic_attack * 3.0)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            print(f"💥 메가 레이저로 {target.name}에게 {damage} 피해!")
        return True
    except:
        return False

def _spirit_strike(caster, target, skill_data):
    """영령 타격 - 영적 공격"""
    try:
        damage = int(caster.magic_attack * 1.4)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            if hasattr(target, 'status_manager'):
                from .status_effects import StatusType
                target.status_manager.add_status(StatusType.FEAR, 2, 1.0)
            print(f"👻 영령 타격으로 {target.name}에게 {damage} 피해 + 공포!")
        return True
    except:
        return False

def _pirate_treasure(caster, target, skill_data):
    """해적의 보물 - 골드 획득"""
    try:
        gold_gain = 100 + (caster.level * 10)
        if hasattr(caster, 'gold'):
            caster.gold += gold_gain
        print(f"💰 {caster.name}이 보물을 발견하여 {gold_gain} 골드를 획득!")
        return True
    except:
        return False

def _nature_wrath(caster, target, skill_data):
    """자연의 분노 - 자연계 공격"""
    try:
        damage = int(caster.magic_attack * 1.8)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            print(f"🌿 자연의 분노로 {target.name}에게 {damage} 피해!")
        return True
    except:
        return False

def _logical_refutation(caster, target, skill_data):
    """논리적 반박 - 적의 능력 무력화"""
    try:
        if target and hasattr(target, 'status_manager'):
            from .status_effects import StatusType
            target.status_manager.add_status(StatusType.SILENCE, 3, 1.0)  # 침묵
            target.status_manager.add_status(StatusType.REDUCE_ALL_STATS, 3, 0.5)  # 능력치 반감
            print(f"🤔 논리적 반박으로 {target.name}의 능력이 무력화됩니다!")
        return True
    except:
        return False

def _truth_enlightenment(caster, target, skill_data):
    """진리의 깨달음 - 궁극의 지혜"""
    try:
        if hasattr(caster, 'status_manager'):
            from .status_effects import StatusType
            caster.status_manager.add_status(StatusType.OMNISCIENCE, 5, 1.0)  # 전지전능
            print(f"✨ {caster.name}이 진리를 깨달아 전지전능한 상태가 됩니다!")
        return True
    except:
        return False

def _arena_technique(caster, target, skill_data):
    """투기장 기술 - 검투사 전용 기술"""
    try:
        damage = int(caster.attack * 1.4)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            print(f"⚔️ 투기장 기술로 {target.name}에게 {damage} 피해!")
        return True
    except:
        return False

def _arena_finale(caster, target, skill_data):
    """투기장의 피날레 - 검투사 궁극기"""
    try:
        damage = int(caster.attack * 2.5)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            print(f"🏟️ 투기장의 피날레로 {target.name}에게 {damage} 결정타!")
        return True
    except:
        return False

def _lance_charge(caster, target, skill_data):
    """창 돌격 - 기사의 돌격"""
    try:
        damage = int(caster.attack * 1.6)
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            print(f"🏹 창 돌격으로 {target.name}에게 {damage} 관통 피해!")
        return True
    except:
        return False

def _blessing_light(caster, target, skill_data):
    """축복의 빛 - 신성한 빛"""
    try:
        target_char = target if target else caster
        heal = int(caster.magic_attack * 1.2)
        if hasattr(target_char, 'current_hp'):
            max_hp = getattr(target_char, 'max_hp', target_char.current_hp)
            target_char.current_hp = min(max_hp, target_char.current_hp + heal)
            print(f"✨ 축복의 빛으로 {target_char.name}이 {heal} 회복!")
        return True
    except:
        return False

def _magic_sword_aura(caster, target, skill_data):
    """마검 오라 - 마법검사 버프"""
    try:
        if hasattr(caster, 'status_manager'):
            from .status_effects import StatusType
            caster.status_manager.add_status(StatusType.MAGIC_WEAPON, 5, 50)  # 5턴간 마법 공격력 +50%
            print(f"⚔️ {caster.name}의 검에 마법 오라가 깃듭니다!")
        return True
    except:
        return False

def _magic_sword_mastery(caster, target, skill_data):
    """마검 숙련 - 마법검사 궁극 숙련"""
    try:
        if hasattr(caster, 'status_manager'):
            from .status_effects import StatusType
            caster.status_manager.add_status(StatusType.MASTER_SWORDSMAN, 10, 1.0)  # 검술 달인
            print(f"🗡️ {caster.name}이 마검술의 달인이 됩니다!")
        return True
    except:
        return False

def _shield_bash(caster, target, skill_data):
    """방패 강타 - 방패로 적을 공격"""
    try:
        damage = int(caster.defense * 1.2)  # 방어력 기반 피해
        if target and hasattr(target, 'current_hp'):
            target.current_hp = max(0, target.current_hp - damage)
            if hasattr(target, 'status_manager'):
                from .status_effects import StatusType
                target.status_manager.add_status(StatusType.STUN, 1, 1.0)
            print(f"🛡️ 방패 강타로 {target.name}에게 {damage} 피해 + 기절!")
        return True
    except:
        return False

def _death_touch(caster, target, skill_data):
    """죽음의 손길 - 즉사 공격"""
    try:
        if target and hasattr(target, 'current_hp'):
            # 확률적 즉사 (레벨 차이에 따라)
            death_chance = max(5, 20 - (target.level - caster.level))
            import random
            if random.randint(1, 100) <= death_chance:
                target.current_hp = 0
                print(f"💀 {target.name}이 죽음의 손길에 쓰러집니다!")
            else:
                damage = int(caster.magic_attack * 1.5)
                target.current_hp = max(0, target.current_hp - damage)
                print(f"💀 죽음의 손길로 {target.name}에게 {damage} 피해!")
        return True
    except:
        return False
