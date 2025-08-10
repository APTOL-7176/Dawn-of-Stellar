#!/usr/bin/env python3
"""
통합 데미지 계산 시스템 (Unified Damage System)
=====================================

모든 데미지 계산 공식을 중앙화하여 일관성 있고 밸런싱하기 쉬운 시스템 구축

🎯 주요 기능:
- BRV 데미지 계산 통합
- HP 데미지 계산 통합
- 크리티컬 데미지 계산
- 속성 데미지 계산
- 상태이상 데미지 계산
- 특성 보정 적용
- 밸런스 조정 중앙화

📊 데미지 계산 공식:
================

1. 기본 BRV 데미지:
   기본_데미지 = (공격력 - 방어력 * 0.5) * 스킬_배율 * 레벨_보정

2. HP 데미지:
   HP_데미지 = BRV_포인트 * HP_배율 * 0.115 (밸런스 조정값)

3. 크리티컬 데미지:
   크리티컬_데미지 = 기본_데미지 * (1.5 + 운_보정)

4. 속성 상성:
   최종_데미지 = 기본_데미지 * 속성_배율 (0.5 ~ 2.0)

5. 상처 시스템:
   상처_데미지 = HP_데미지 * 0.25
   최대_상처 = 최대_HP * 0.75
"""

import math
import random
from typing import Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass


# 안전한 색상 상수 정의
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'DIM': '\033[2m', 
    'UNDERLINE': '\033[4m',
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'BRIGHT_BLACK': '\033[90m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_YELLOW': '\033[93m',
    'BRIGHT_BLUE': '\033[94m',
    'BRIGHT_MAGENTA': '\033[95m',
    'BRIGHT_CYAN': '\033[96m',
    'BRIGHT_WHITE': '\033[97m',
    'BG_BLACK': '\033[40m',
    'BG_RED': '\033[41m',
    'BG_GREEN': '\033[42m',
    'BG_YELLOW': '\033[43m',
    'BG_BLUE': '\033[44m',
    'BG_MAGENTA': '\033[45m',
    'BG_CYAN': '\033[46m',
    'BG_WHITE': '\033[47m'
}

def get_color(color_name):
    """안전한 색상 코드 반환"""
    return COLORS.get(color_name, '')

# Enum import 추가
from enum import Enum

# UI 애니메이션 대기 함수 import
try:
    from .ui_animations import SequentialGaugeAnimator
    UI_ANIMATIONS_AVAILABLE = True
except ImportError:
    UI_ANIMATIONS_AVAILABLE = False

# 기존 시스템에서 import
try:
    from .new_skill_system import DamageType as SkillDamageType, ElementType as SkillElementType
    SKILL_SYSTEM_AVAILABLE = True
    print("✅ new_skill_system에서 타입 정의 가져옴")
except ImportError:
    print("⚠️ new_skill_system 가져오기 실패, 자체 정의 사용")
    SKILL_SYSTEM_AVAILABLE = False

# 통합된 타입 정의 (기존 시스템과 호환)
class DamageType(Enum):
    """데미지 타입 정의"""
    PHYSICAL = "physical"    # 물리 데미지
    MAGICAL = "magical"      # 마법 데미지
    TRUE = "true"           # 고정 데미지 (방어 무시)
    HEALING = "healing"     # 회복
    DOT = "dot"            # 지속 데미지

class ElementType(Enum):
    """속성 타입 정의"""
    NONE = "무속성"
    FIRE = "화염"
    ICE = "빙결"
    THUNDER = "번개"
    EARTH = "대지"
    WIND = "바람"
    WATER = "물"
    LIGHT = "빛"
    DARK = "어둠"
    POISON = "독"

# 색상 정의
class Color:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    DIM = '\033[2m'

@dataclass
class DamageResult:
    """데미지 계산 결과"""
    base_damage: int = 0
    critical_damage: int = 0
    elemental_bonus: float = 1.0
    trait_bonus: float = 1.0
    final_damage: int = 0
    is_critical: bool = False
    damage_type: DamageType = DamageType.PHYSICAL
    element: ElementType = ElementType.NONE
    wound_damage: int = 0
    
    # 상세 계산 과정
    attacker_attack: int = 0
    defender_defense: int = 0
    skill_multiplier: float = 1.0
    level_bonus: float = 1.0
    calculation_steps: list = None
    
    def __post_init__(self):
        if self.calculation_steps is None:
            self.calculation_steps = []

class UnifiedDamageSystem:
    """통합 데미지 계산 시스템"""
    
    # =====================================
    # 🎯 핵심 밸런스 상수
    # =====================================
    
    # BRV 데미지 관련
    BRV_BASE_MULTIPLIER = 2.0     # 기본 BRV 배율 (5.0에서 0.1으로 대폭 감소하여 밸런스 조정)
    BRV_DEFENSE_REDUCTION = 1.0    # 방어력 감소 비율 (0%) - 실제 게임과 동일
    BRV_LEVEL_BONUS_PER_LEVEL = 0.0  # 레벨당 데미지 보너스 (0%)

    # HP 데미지 관련
    HP_DAMAGE_MULTIPLIER = 0.1   # HP 데미지 기본 배율 (밸런스 조정)
    HP_SKILL_POWER_SCALING = 1.5   # HP 스킬 위력 스케일링
    HP_DEFENSE_REDUCTION = 0.5     # HP 공격의 방어력 영향 비율 (50% 감소)
    
    # 크리티컬 관련
    BASE_CRITICAL_RATE = 0.05      # 기본 크리티컬 확률 (5%)
    BASE_CRITICAL_MULTIPLIER = 1.5 # 기본 크리티컬 배율
    LUCK_CRITICAL_BONUS = 0.002    # 운 스탯당 크리티컬 확률 증가
    
    # 상처 시스템
    WOUND_DAMAGE_RATIO = 0.25      # 받은 데미지의 25%가 상처로 전환
    MAX_WOUND_RATIO = 0.75         # 최대 상처는 최대 HP의 75%
    WOUND_HEAL_RATIO = 0.25        # 초과 회복의 25%로 상처 치료
    
    # 속성 상성 배율
    ELEMENT_WEAKNESS_MULTIPLIER = 1.5    # 약점 공격 배율
    ELEMENT_RESISTANCE_MULTIPLIER = 0.75  # 저항 공격 배율
    ELEMENT_NEUTRAL_MULTIPLIER = 1.0     # 중립 배율
    
    def __init__(self, debug_mode: bool = True):  # 기본값을 True로 변경하여 이쁜 로그 활성화
        self.debug_mode = debug_mode
        self._calculation_history = []
        
    # =====================================
    # 🔥 BRV 데미지 계산 (핵심 시스템)
    # =====================================
    
    def calculate_brv_damage(self, 
                           attacker, 
                           target, 
                           skill: Dict[str, Any], 
                           base_power: Optional[float] = None) -> DamageResult:
        """
        통합 BRV 데미지 계산
        
        Args:
            attacker: 공격자
            target: 대상
            skill: 스킬 정보
            base_power: 기본 위력 (스킬에서 가져올 수 없을 때)
            
        Returns:
            DamageResult: 상세한 데미지 계산 결과
        """
        result = DamageResult()
        result.damage_type = DamageType.PHYSICAL
        
        # 1. 기본 스탯 추출
        result.attacker_attack = self._get_attack_stat(attacker, skill)
        result.defender_defense = self._get_defense_stat(target, skill)
        
        # 2. 스킬 위력 결정
        result.skill_multiplier = base_power or skill.get('brv_power', 1.0)
        
        # 3. 레벨 보너스 계산
        attacker_level = getattr(attacker, 'level', 1)
        result.level_bonus = 1.0 + (attacker_level * self.BRV_LEVEL_BONUS_PER_LEVEL)
        
        # 4. 기본 데미지 계산 (BRV_BASE_MULTIPLIER 적용)
        # 방어력 계산: 실제 방어력이 아닌 감소율로 사용
        if self.BRV_DEFENSE_REDUCTION == 1.0:
            # 방어력을 그대로 나누는 방식
            effective_defense = max(1, result.defender_defense)
            raw_attack = result.attacker_attack / effective_defense
        else:
            # 기존 방식 (방어력 감소)
            defense_reduction = result.defender_defense * self.BRV_DEFENSE_REDUCTION
            raw_attack = max(1, result.attacker_attack - defense_reduction)
        
        base_damage_before_multiplier = raw_attack * result.skill_multiplier * result.level_bonus
        result.base_damage = int(base_damage_before_multiplier * self.BRV_BASE_MULTIPLIER)
        
        if self.BRV_DEFENSE_REDUCTION == 1.0:
            result.calculation_steps.append(
                f"기본 데미지: ({result.attacker_attack} ÷ {effective_defense:.1f}) × {result.skill_multiplier} × {result.level_bonus:.2f} × {self.BRV_BASE_MULTIPLIER} = {result.base_damage}"
            )
        else:
            defense_reduction = result.defender_defense * self.BRV_DEFENSE_REDUCTION
            result.calculation_steps.append(
                f"기본 데미지: ({result.attacker_attack} - {defense_reduction:.1f}) × {result.skill_multiplier} × {result.level_bonus:.2f} × {self.BRV_BASE_MULTIPLIER} = {result.base_damage}"
            )
        
        # 5. 크리티컬 판정
        result.is_critical = self._check_critical_hit(attacker)
        if result.is_critical:
            critical_multiplier = self._get_critical_multiplier(attacker)
            result.critical_damage = int(result.base_damage * critical_multiplier)
            result.calculation_steps.append(
                f"크리티컬 히트! {result.base_damage} × {critical_multiplier:.2f} = {result.critical_damage}"
            )
        else:
            result.critical_damage = result.base_damage
        
        # 6. 속성 상성 적용
        result.elemental_bonus = self._calculate_elemental_bonus(skill, attacker, target)
        elemental_damage = int(result.critical_damage * result.elemental_bonus)
        if result.elemental_bonus != 1.0:
            result.calculation_steps.append(
                f"속성 보정: {result.critical_damage} × {result.elemental_bonus:.2f} = {elemental_damage}"
            )
        
        # 7. 특성 보정 적용
        result.trait_bonus = self._calculate_trait_bonus(skill, attacker, target, DamageType.PHYSICAL)
        trait_damage = int(elemental_damage * result.trait_bonus)
        if result.trait_bonus != 1.0:
            result.calculation_steps.append(
                f"특성 보정: {elemental_damage} × {result.trait_bonus:.2f} = {trait_damage}"
            )
        
        # 8. 최종 데미지 결정
        result.final_damage = max(1, trait_damage)  # 최소 1 데미지 보장
        
        # 9. 디버그 출력
        if self.debug_mode:
            self._print_damage_calculation("BRV 데미지", result)
            
            # 1초 대기 (아무 키나 눌러서 스킵 가능) - 윈도우 호환 버전
            import time
            import threading
            import msvcrt
            
            def wait_for_key():
                """키 입력을 대기하는 함수"""
                msvcrt.getch()
            
            # 키 입력을 기다리는 스레드 시작
            key_thread = threading.Thread(target=wait_for_key)
            key_thread.daemon = True
            key_thread.start()
            
            # 1초 대기하거나 키 입력까지 대기
            for i in range(10):  # 1초 = 10 × 0.1초
                if not key_thread.is_alive():
                    break
                time.sleep(0.1)
            
        return result
    
    # =====================================
    # ⚡ HP 데미지 계산
    # =====================================
    
    def calculate_hp_damage(self, 
                          attacker, 
                          target, 
                          skill: Dict[str, Any], 
                          brv_points: Optional[int] = None,
                          hp_power: Optional[float] = None) -> Tuple[DamageResult, int]:
        """
        통합 HP 데미지 계산 (방어력 영향 포함)
        
        Args:
            attacker: 공격자
            target: 대상
            skill: 스킬 정보
            brv_points: BRV 포인트 (없으면 공격자의 현재 BRV 사용)
            hp_power: HP 스킬 위력 (없으면 스킬에서 가져옴)
            
        Returns:
            Tuple[DamageResult, int]: (HP 데미지 결과, 상처 데미지)
        """
        result = DamageResult()
        result.damage_type = DamageType.PHYSICAL
        
        # 1. BRV 포인트 결정
        if brv_points is None:
            brv_points = getattr(attacker, 'brave_points', 0)
        
        # 2. HP 스킬 위력 (매개변수 우선, 없으면 스킬에서 가져옴)
        if hp_power is None:
            hp_power = skill.get('hp_power', 1.0)
        
        # 3. 방어력 적용 (HP 공격은 BRV 공격보다 방어력 영향 적음)
        damage_type = skill.get('damage_type', 'physical')
        if damage_type == 'magical':
            defender_defense = getattr(target, 'magic_defense', 50)
        else:
            defender_defense = getattr(target, 'physical_defense', 50)
        
        # HP 공격의 방어력 감소 (30% 적용)
        defense_reduction = defender_defense * self.HP_DEFENSE_REDUCTION
        defense_multiplier = max(0.2, 1.0 - (defense_reduction / 100))  # 최소 20%는 보장

        # 4. 기본 HP 데미지 계산 (방어력 적용)
        base_hp_damage = brv_points * hp_power * self.HP_DAMAGE_MULTIPLIER * self.HP_SKILL_POWER_SCALING * defense_multiplier
        result.base_damage = int(base_hp_damage)
        
        result.calculation_steps.append(
            f"기본 HP 데미지: {brv_points} × {hp_power} × {self.HP_DAMAGE_MULTIPLIER} × {self.HP_SKILL_POWER_SCALING} × {defense_multiplier:.3f} = {result.base_damage}"
        )
        result.calculation_steps.append(
            f"방어력 적용: {defender_defense} × {self.HP_DEFENSE_REDUCTION} = {defense_reduction:.1f} 감소 (최종 배율: {defense_multiplier:.3f})"
        )
        
        # 5. 속성 상성 적용
        result.elemental_bonus = self._calculate_elemental_bonus(skill, attacker, target)
        elemental_damage = int(result.base_damage * result.elemental_bonus)
        if result.elemental_bonus != 1.0:
            result.calculation_steps.append(
                f"속성 보정: {result.base_damage} × {result.elemental_bonus:.2f} = {elemental_damage}"
            )
        
        # 6. 특성 보정 적용
        result.trait_bonus = self._calculate_trait_bonus(skill, attacker, target, DamageType.PHYSICAL)
        trait_damage = int(elemental_damage * result.trait_bonus)
        if result.trait_bonus != 1.0:
            result.calculation_steps.append(
                f"특성 보정: {elemental_damage} × {result.trait_bonus:.2f} = {trait_damage}"
            )
        
        # 7. 최종 HP 데미지
        result.final_damage = max(1, trait_damage)
        
        # 8. 상처 데미지 계산
        result.wound_damage = int(result.final_damage * self.WOUND_DAMAGE_RATIO)
        
        result.calculation_steps.append(
            f"상처 데미지: {result.final_damage} × {self.WOUND_DAMAGE_RATIO} = {result.wound_damage}"
        )
        
        # 9. 디버그 출력
        if self.debug_mode:
            self._print_damage_calculation("HP 데미지", result)
            
            # 1초 대기 (아무 키나 눌러서 스킵 가능) - 윈도우 호환 버전
            import time
            import threading
            import msvcrt
            
            def wait_for_enter():
                """키 입력을 대기하는 함수"""
                msvcrt.getch()
            
            # 키 입력을 기다리는 스레드 시작
            key_thread = threading.Thread(target=wait_for_enter)
            key_thread.daemon = True
            key_thread.start()
            
            # 1초 대기하거나 키 입력까지 대기
            for i in range(10):  # 1초 = 10 × 0.1초
                if not key_thread.is_alive():
                    break
                time.sleep(0.1)
            
        return result, result.wound_damage
    
    # =====================================
    # 🔮 마법 데미지 계산
    # =====================================
    
    def calculate_magic_damage(self, 
                             attacker, 
                             target, 
                             skill: Dict[str, Any], 
                             base_power: Optional[float] = None) -> DamageResult:
        """마법 데미지 계산 (BRV 마법)"""
        result = self.calculate_brv_damage(attacker, target, skill, base_power)
        result.damage_type = DamageType.MAGICAL
        
        # 마법 공격력과 마법 방어력 사용
        result.attacker_attack = getattr(attacker, 'magic_attack', 50)
        result.defender_defense = getattr(target, 'magic_defense', 50)
        
        # 마법 데미지 재계산 (BRV_BASE_MULTIPLIER 적용)
        if self.BRV_DEFENSE_REDUCTION == 1.0:
            # 방어력을 그대로 나누는 방식
            effective_defense = max(1, result.defender_defense)
            raw_attack = result.attacker_attack / effective_defense
        else:
            # 기존 방식 (방어력 감소)
            defense_reduction = result.defender_defense * self.BRV_DEFENSE_REDUCTION
            raw_attack = max(1, result.attacker_attack - defense_reduction)
        
        base_damage_before_multiplier = raw_attack * result.skill_multiplier * result.level_bonus
        result.base_damage = int(base_damage_before_multiplier * self.BRV_BASE_MULTIPLIER)
        
        # 나머지 계산은 동일
        return result
    
    # =====================================
    # 💚 회복 계산
    # =====================================
    
    def calculate_healing(self, 
                        caster, 
                        target, 
                        skill: Dict[str, Any], 
                        base_power: Optional[float] = None) -> DamageResult:
        """회복량 계산"""
        result = DamageResult()
        result.damage_type = DamageType.HEALING
        
        # 1. 치유력 결정 (마법 공격력 기반)
        heal_power = getattr(caster, 'magic_attack', 50)
        skill_power = base_power or skill.get('heal_power', skill.get('brv_power', 1.0))
        
        # 2. 기본 회복량
        base_heal = int(heal_power * skill_power * 0.8)  # 회복량 배율
        result.base_damage = base_heal  # 편의상 damage 필드 사용
        
        # 3. 특성 보정
        result.trait_bonus = self._calculate_trait_bonus(skill, caster, target, DamageType.HEALING)
        final_heal = int(base_heal * result.trait_bonus)
        result.final_damage = final_heal
        
        # 4. 상처 치료량 계산
        # safe guard for max_hp access
        try:
            target_max_hp = target.max_hp
        except (AttributeError, TypeError):
            target_max_hp = getattr(target, '_max_hp', getattr(target, '_base_max_hp', 150))
        
        # safe guard for current_hp access
        try:
            target_current_hp = target.current_hp
        except (AttributeError, TypeError):
            target_current_hp = getattr(target, '_current_hp', target_max_hp)
        
        excess_heal = max(0, final_heal - (target_max_hp - target_current_hp))
        result.wound_damage = int(excess_heal * self.WOUND_HEAL_RATIO)  # 상처 치료량
        
        return result
    
    # =====================================
    # 🔥 DOT 데미지 계산
    # =====================================
    
    def calculate_dot_damage(self, 
                           character, 
                           effect_name: str, 
                           base_damage: int, 
                           duration: int) -> DamageResult:
        """지속 데미지(DOT) 계산"""
        result = DamageResult()
        result.damage_type = DamageType.DOT
        
        # 기본 DOT 데미지 (최대 HP 비례)
        # safe guard for max_hp access
        try:
            max_hp = character.max_hp
        except (AttributeError, TypeError):
            max_hp = getattr(character, '_max_hp', getattr(character, '_base_max_hp', 100))
        
        dot_damage = max(1, int(max_hp * 0.05))  # 최대 HP의 5%
        
        # 효과별 조정
        if effect_name == "독":
            dot_damage = int(dot_damage * 0.8)
        elif effect_name == "화상":
            dot_damage = int(dot_damage * 1.2)
        elif effect_name == "출혈":
            dot_damage = int(dot_damage * 1.0)
        
        result.final_damage = dot_damage
        return result
    
    # =====================================
    # 🎯 보조 계산 함수들
    # =====================================
    
    def _get_attack_stat(self, character, skill: Dict[str, Any]) -> int:
        """공격력 스탯 가져오기"""
        damage_type = skill.get('damage_type', 'physical')
        if damage_type == 'magical':
            return getattr(character, 'magic_attack', 50)
        else:
            return getattr(character, 'physical_attack', 50)
    
    def _get_defense_stat(self, character, skill: Dict[str, Any]) -> int:
        """방어력 스탯 가져오기"""
        damage_type = skill.get('damage_type', 'physical')
        if damage_type == 'magical':
            return getattr(character, 'magic_defense', 50)
        else:
            return getattr(character, 'physical_defense', 50)
    
    def _check_critical_hit(self, attacker) -> bool:
        """크리티컬 히트 판정"""
        luck = getattr(attacker, 'luck', 0)
        critical_rate = self.BASE_CRITICAL_RATE + (luck * self.LUCK_CRITICAL_BONUS)
        return random.random() < critical_rate
    
    def _get_critical_multiplier(self, attacker) -> float:
        """크리티컬 배율 계산"""
        luck = getattr(attacker, 'luck', 0)
        return self.BASE_CRITICAL_MULTIPLIER + (luck * 0.01)  # 운 1당 1% 추가
    
    def _calculate_elemental_bonus(self, skill: Dict[str, Any], attacker, target) -> float:
        """속성 상성 보너스 계산"""
        skill_element = skill.get('element', 'none')
        if skill_element == 'none':
            return 1.0
        
        # 대상의 약점/저항 확인
        weaknesses = getattr(target, 'element_weaknesses', [])
        resistances = getattr(target, 'element_resistances', [])
        
        if skill_element in weaknesses:
            return self.ELEMENT_WEAKNESS_MULTIPLIER
        elif skill_element in resistances:
            return self.ELEMENT_RESISTANCE_MULTIPLIER
        else:
            return self.ELEMENT_NEUTRAL_MULTIPLIER
    
    def _calculate_trait_bonus(self, skill: Dict[str, Any], attacker, target, damage_type: DamageType) -> float:
        """특성 보너스 계산"""
        bonus = 1.0
        
        # 공격자의 특성 확인
        if hasattr(attacker, 'active_traits'):
            for trait in attacker.active_traits:
                try:
                    # trait가 딕셔너리인 경우
                    if isinstance(trait, dict):
                        if trait.get('type') == 'damage_bonus':
                            bonus *= trait.get('multiplier', 1.0)
                        elif trait.get('effect_type') == 'damage_bonus':
                            effect_value = trait.get('effect_value', {})
                            if isinstance(effect_value, dict):
                                bonus *= effect_value.get('multiplier', 1.0)
                            elif isinstance(effect_value, (int, float)):
                                bonus *= effect_value
                    # trait가 객체인 경우 (CharacterTrait)
                    elif hasattr(trait, 'effect_value'):
                        trait_type = getattr(trait, 'trait_type', getattr(trait, 'effect_type', ''))
                        if trait_type == 'damage_bonus':
                            effect_value = getattr(trait, 'effect_value', 1.0)
                            if isinstance(effect_value, dict):
                                bonus *= effect_value.get('multiplier', 1.0)
                            elif isinstance(effect_value, (int, float)):
                                bonus *= effect_value
                except Exception as e:
                    # 특성 처리 중 오류가 발생해도 계속 진행
                    continue
        
        # 대상의 방어 특성 확인
        if hasattr(target, 'active_traits'):
            for trait in target.active_traits:
                try:
                    # trait가 딕셔너리인 경우
                    if isinstance(trait, dict):
                        if trait.get('type') == 'damage_reduction':
                            bonus *= (1.0 - trait.get('reduction', 0.0))
                        elif trait.get('effect_type') == 'damage_reduction':
                            effect_value = trait.get('effect_value', {})
                            if isinstance(effect_value, dict):
                                bonus *= (1.0 - effect_value.get('reduction', 0.0))
                            elif isinstance(effect_value, (int, float)):
                                bonus *= (1.0 - effect_value)
                    # trait가 객체인 경우 (CharacterTrait)
                    elif hasattr(trait, 'effect_value'):
                        trait_type = getattr(trait, 'trait_type', getattr(trait, 'effect_type', ''))
                        if trait_type == 'damage_reduction':
                            effect_value = getattr(trait, 'effect_value', 0.0)
                            if isinstance(effect_value, dict):
                                bonus *= (1.0 - effect_value.get('reduction', 0.0))
                            elif isinstance(effect_value, (int, float)):
                                bonus *= (1.0 - effect_value)
                except Exception as e:
                    # 특성 처리 중 오류가 발생해도 계속 진행
                    continue
        
        return bonus
    
    def _print_damage_calculation(self, calculation_type: str, result: DamageResult):
        """데미지 계산 과정 출력 - 간소화된 버전"""
        
        # 계산 타입에 따른 이모지와 색상 설정
        if "BRV" in calculation_type:
            type_emoji = "⚔️"
            type_color = Color.BRIGHT_BLUE
            damage_emoji = "💫"
        elif "HP" in calculation_type:
            type_emoji = "💀"
            type_color = Color.BRIGHT_RED
            damage_emoji = "💥"
        else:
            type_emoji = "✨"
            type_color = Color.BRIGHT_YELLOW
            damage_emoji = "⭐"
        
        # 간단한 헤더만 출력
        header = f"{type_emoji} {calculation_type} 계산 결과 {type_emoji}"
        print(f"\n{type_color}╭{'─' * (len(header) + 6)}╮{get_color('RESET')}")
        print(f"{type_color} {header} {get_color('RESET')}")
        print(f"{type_color}╰{'─' * (len(header) + 6)}╯{get_color('RESET')}")


# =====================================
# 🌟 전역 인스턴스 및 편의 함수
# =====================================

# 전역 인스턴스
_unified_damage_system = None

def get_damage_system(debug_mode: bool = True) -> UnifiedDamageSystem:  # 기본값을 True로 변경
    """통합 데미지 시스템 인스턴스 가져오기"""
    global _unified_damage_system
    if _unified_damage_system is None:
        _unified_damage_system = UnifiedDamageSystem(debug_mode)
    return _unified_damage_system

# 편의 함수들
def calculate_brv_damage(attacker, target, skill: Dict[str, Any], base_power: Optional[float] = None) -> DamageResult:
    """BRV 데미지 계산 편의 함수"""
    return get_damage_system().calculate_brv_damage(attacker, target, skill, base_power)

def calculate_hp_damage(attacker, target, skill: Dict[str, Any], brv_points: Optional[int] = None, hp_power: Optional[float] = None) -> Tuple[DamageResult, int]:
    """HP 데미지 계산 편의 함수"""
    return get_damage_system().calculate_hp_damage(attacker, target, skill, brv_points, hp_power)

def calculate_magic_damage(attacker, target, skill: Dict[str, Any], base_power: Optional[float] = None) -> DamageResult:
    """마법 데미지 계산 편의 함수"""
    return get_damage_system().calculate_magic_damage(attacker, target, skill, base_power)

def calculate_healing(caster, target, skill: Dict[str, Any], base_power: Optional[float] = None) -> DamageResult:
    """회복 계산 편의 함수"""
    return get_damage_system().calculate_healing(caster, target, skill, base_power)

# =====================================
# 🔧 설정 및 디버그 함수
# =====================================

def set_debug_mode(enabled: bool):
    """디버그 모드 설정"""
    system = get_damage_system()
    system.debug_mode = enabled

def get_damage_constants() -> Dict[str, float]:
    """현재 데미지 상수들 반환"""
    return {
        "BRV_BASE_MULTIPLIER": UnifiedDamageSystem.BRV_BASE_MULTIPLIER,
        "BRV_DEFENSE_REDUCTION": UnifiedDamageSystem.BRV_DEFENSE_REDUCTION,
        "HP_DAMAGE_MULTIPLIER": UnifiedDamageSystem.HP_DAMAGE_MULTIPLIER,
        "HP_DEFENSE_REDUCTION": UnifiedDamageSystem.HP_DEFENSE_REDUCTION,
        "BASE_CRITICAL_RATE": UnifiedDamageSystem.BASE_CRITICAL_RATE,
        "BASE_CRITICAL_MULTIPLIER": UnifiedDamageSystem.BASE_CRITICAL_MULTIPLIER,
        "WOUND_DAMAGE_RATIO": UnifiedDamageSystem.WOUND_DAMAGE_RATIO,
        "MAX_WOUND_RATIO": UnifiedDamageSystem.MAX_WOUND_RATIO,
    }

def update_damage_constants(**kwargs):
    """데미지 상수 업데이트"""
    for key, value in kwargs.items():
        if hasattr(UnifiedDamageSystem, key):
            setattr(UnifiedDamageSystem, key, value)
            print(f"✅ {key} = {value}로 업데이트되었습니다.")
        else:
            print(f"❌ {key}는 유효한 상수가 아닙니다.")

if __name__ == "__main__":
    # 테스트 코드
    print("🧪 통합 데미지 시스템 테스트")
    
    # 모의 캐릭터 생성
    class MockCharacter:
        def __init__(self, name, **stats):
            self.name = name
            for key, value in stats.items():
                setattr(self, key, value)
    
    attacker = MockCharacter("테스트 전사", 
                           level=10, 
                           physical_attack=100, 
                           magic_attack=50,
                           brave_points=500,
                           luck=10)
    
    target = MockCharacter("테스트 적", 
                         physical_defense=60, 
                         magic_defense=40,
                         max_hp=1000,
                         current_hp=800)
    
    skill = {
        "name": "테스트 스킬",
        "brv_power": 1.5,
        "hp_power": 1.0,
        "element": "fire"
    }
    
    # 디버그 모드로 테스트
    set_debug_mode(True)
    
    print("\n🗡️ BRV 데미지 테스트:")
    brv_result = calculate_brv_damage(attacker, target, skill)
    
    print("\n⚡ HP 데미지 테스트:")
    hp_result, wound = calculate_hp_damage(attacker, target, skill)
    
    print(f"\n📊 현재 데미지 상수:")
    constants = get_damage_constants()
    for key, value in constants.items():
        print(f"  {key}: {value}")
