#!/usr/bin/env python3
"""
🛡️ 전사 적응형 시스템 - 게임 통합 버전
new_skill_syst            WarriorStance.GUARDIAN: {
                'name': '🛠️ 수호자',  # 🛡️ → 🛠️로 변경하여 방어형과 구별
                'physical_defense_bonus': 0.2,  # 0.3 → 0.2로 너프
                'magic_defense_bonus': 0.25,    # 0.4 → 0.25로 너프
                'skill_power_bonus': 0.2,       # 0.3 → 0.2로 너프
                'speed_bonus': 0.05,            # 0.1 → 0.05로 너프
                'description': '파티원 보호 중심'
            }동하여 실제 게임에서 사용
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

# 기존 시스템에서 import
try:
    from .new_skill_system import StatusType
    from .character import StatusEffect
except ImportError:
    # 테스트 환경에서는 더미 클래스 사용
    class StatusType:
        WARRIOR_STANCE = "warrior_stance"
    class StatusEffect:
        def __init__(self, status_type, duration=999, intensity=0, data=None):
            self.status_type = status_type
            self.duration = duration
            self.intensity = intensity
            self.data = data or {}

class WarriorStance(Enum):
    """전사 전투 자세 (6단계 완전체)"""
    ATTACK = 0      # 공격 자세: 공격력 강화
    DEFENSE = 1     # 방어 자세: 방어력 강화  
    BALANCED = 2    # 균형 자세: 종합 능력치 향상
    BERSERKER = 3   # 광전사: 극한 공격력, 위험 증가
    GUARDIAN = 4    # 수호자: 파티 보호 특화
    SPEED = 5       # 속도 자세: 기동성 및 행동 속도 강화

class WarriorAdaptiveSystem:
    """전사 적응형 시스템 - 게임 통합 버전"""
    
    def __init__(self):
        self.stance_bonuses = {
            WarriorStance.ATTACK: {
                'name': '⚔️ 공격 자세',
                'physical_attack_bonus': 0.25,  # 25% 공격력 증가
                'mastery_attack_bonus': 0.20,   # 6단계 완전체: 추가 20% 공격력
                'description': '공격에 특화된 자세'
            },
            WarriorStance.DEFENSE: {
                'name': '🛡️ 방어 자세',
                'physical_defense_bonus': 0.3,  # 30% 방어력 증가
                'magic_defense_bonus': 0.2,     # 20% 마법 방어력 증가
                'mastery_defense_bonus': 0.25,  # 6단계 완전체: 추가 25% 방어력
                'description': '방어에 특화된 자세'
            },
            WarriorStance.BALANCED: {
                'name': '⚖️ 균형 자세',
                'physical_attack_bonus': 0.15,  # 15% 공격력 증가
                'physical_defense_bonus': 0.15, # 15% 방어력 증가
                'mastery_all_stats_bonus': 0.12, # 6단계 완전체: 모든 능력치 12% 증가 (너프됨)
                'description': '균형잡힌 종합 능력 향상'
            },
            WarriorStance.BERSERKER: {
                'name': '💀 광전사 자세',
                'physical_attack_bonus': 0.4,   # 40% 공격력 증가
                'speed_bonus': 0.25,            # 25% 속도 증가
                'mastery_critical_bonus': 0.15, # 6단계 완전체: 15% 크리티컬 확률 증가
                'physical_defense_bonus': -0.15, # 15% 방어력 감소 (위험 요소)
                'description': '극한 공격력, 높은 위험도'
            },
            WarriorStance.GUARDIAN: {
                'name': '🛠️ 수호자 자세',
                'physical_defense_bonus': 0.35, # 35% 방어력 증가
                'magic_defense_bonus': 0.25,    # 25% 마법 방어력 증가
                'party_protection': True,       # 아군 보호 효과
                'mastery_healing_bonus': 0.30,  # 6단계 완전체: 회복량 30% 증가
                'description': '파티원 보호에 특화된 자세'
            },
            WarriorStance.SPEED: {
                'name': '⚡ 속도 자세',
                'speed_bonus': 0.4,             # 40% 속도 증가
                'physical_attack_bonus': 0.15,  # 15% 공격력 증가
                'evasion_bonus': 0.2,           # 20% 회피율 증가
                'mastery_atb_speed_bonus': 0.35, # 6단계 완전체: 35% 행동 속도 증가 (너프됨)
                'description': '극한 기동성과 행동 속도'
            }
        }
    
    def get_current_stance(self, warrior) -> WarriorStance:
        """현재 전사의 자세 조회 (6단계 시스템)"""
        # current_stance 속성이 있으면 우선 사용
        if hasattr(warrior, 'current_stance') and isinstance(warrior.current_stance, int):
            stance_id = warrior.current_stance
            if 0 <= stance_id <= 5:
                return WarriorStance(stance_id)
        
        # 기존 상태효과 시스템 확인
        if not hasattr(warrior, 'status_effects'):
            return WarriorStance.BALANCED
        
        for effect in warrior.status_effects:
            if hasattr(effect, 'status_type') and effect.status_type == StatusType.WARRIOR_STANCE:
                try:
                    return WarriorStance(int(effect.intensity))
                except (ValueError, AttributeError):
                    if hasattr(effect, 'stance_data'):
                        stance_value = effect.stance_data.get('stance', 2)
                        try:
                            return WarriorStance(stance_value)
                        except ValueError:
                            pass
                    return WarriorStance.BALANCED
        
        return WarriorStance.BALANCED
    
    def get_stance_icon(self, warrior) -> str:
        """전사의 현재 자세 아이콘 반환"""
        current_stance = self.get_current_stance(warrior)
        stance_name = self.stance_bonuses[current_stance]['name']
        # 아이콘만 추출 (이모지 부분만)
        icon = stance_name.split()[0] if stance_name else '⚖️'
        return icon
    
    def get_stance_display_name(self, warrior) -> str:
        """전사의 현재 자세 표시명 반환"""
        current_stance = self.get_current_stance(warrior)
        return self.stance_bonuses[current_stance]['name']
    
    def set_warrior_stance(self, warrior, stance: WarriorStance):
        """전사의 자세 설정 (6단계 시스템)"""
        if not hasattr(warrior, 'status_effects'):
            warrior.status_effects = []
        
        # 이전 자세 저장
        previous_stance = getattr(warrior, 'current_stance', 2)
        
        # current_stance 속성 직접 설정
        warrior.current_stance = stance.value
        
        # 기존 자세 상태 제거
        warrior.status_effects = [
            effect for effect in warrior.status_effects 
            if not (hasattr(effect, 'status_type') and effect.status_type == StatusType.WARRIOR_STANCE)
        ]
        
        # 새 자세 상태 추가
        stance_data = {
            'stance': stance.value,
            'name': self.stance_bonuses[stance]['name'],
            'bonuses': self.stance_bonuses[stance]
        }
        stance_effect = StatusEffect(
            name=f"warrior_stance_{stance.name.lower()}",
            status_type=StatusType.BUFF,
            duration=999,
            effect_value=stance.value
        )
        
        # 자세 변경 시 특성 효과 적용 (적응형 무술 등)
        if previous_stance != stance.value and hasattr(warrior, 'apply_trait_effects'):
            trait_effects = warrior.apply_trait_effects("stance_change")
            if trait_effects.get("stance_change_boost"):
                print(f"🥋 {warrior.name}의 적응형 무술이 발동! 다음 공격 위력 증가!")
                if not hasattr(warrior, 'next_attack_boost'):
                    warrior.next_attack_boost = trait_effects["stance_change_boost"]
        
        # stance 정보를 별도 속성으로 저장
        stance_effect.stance_data = stance_data
        warrior.status_effects.append(stance_effect)
    
    def analyze_situation_and_adapt(self, warrior, allies: List, enemies: List) -> bool:
        """상황 분석 후 자세 적응 (변경되었으면 True 반환)"""
        current_stance = self.get_current_stance(warrior)
        optimal_stance = self._determine_optimal_stance(warrior, allies, enemies)
        
        if current_stance != optimal_stance:
            old_name = self.stance_bonuses[current_stance]['name']
            new_name = self.stance_bonuses[optimal_stance]['name']
            print(f"🔄 {warrior.name}의 전투 자세 변경: {old_name} → {new_name}")
            
            self.set_warrior_stance(warrior, optimal_stance)
            return True
        
        return False
    
    def _determine_optimal_stance(self, warrior, allies: List, enemies: List) -> WarriorStance:
        """최적 자세 결정"""
        hp_ratio = warrior.current_hp / warrior.max_hp
        
        # 적 분석
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return WarriorStance.BALANCED
        
        enemy_power = sum(getattr(e, 'physical_attack', 0) + getattr(e, 'magic_attack', 0) for e in alive_enemies)
        warrior_defense = getattr(warrior, 'physical_defense', 0) + getattr(warrior, 'magic_defense', 0)
        threat_ratio = enemy_power / max(1, warrior_defense)
        
        # 파티원 상태 분석
        alive_allies = [ally for ally in allies if ally.is_alive]
        critical_allies = len([ally for ally in alive_allies if ally.current_hp / ally.max_hp < 0.3])
        
        # 자세 결정 로직
        if hp_ratio <= 0.25:
            return WarriorStance.BERSERKER
        elif critical_allies >= 2:
            return WarriorStance.GUARDIAN
        elif threat_ratio >= 2.0 or hp_ratio <= 0.4:
            return WarriorStance.DEFENSIVE
        elif enemy_power < 50 and hp_ratio >= 0.7:
            return WarriorStance.AGGRESSIVE
        else:
            return WarriorStance.BALANCED
    
    def apply_stance_bonuses(self, warrior, base_damage: int, skill_type: str = "") -> int:
        """자세 보너스 적용 (특성 효과 포함)"""
        current_stance = self.get_current_stance(warrior)
        bonuses = self.stance_bonuses[current_stance]
        
        modified_damage = base_damage
        
        # 특성 효과 적용
        if hasattr(warrior, 'apply_trait_effects'):
            warrior.current_stance = current_stance.value  # 현재 자세 정보 설정
            trait_effects = warrior.apply_trait_effects("attacking")
            
            # 전장의 지배자: 자세 보너스 증폭
            stance_amplify = trait_effects.get("stance_bonus_amplify", 1.0)
            
            # 전투 본능: 공격형/광전사에서 크리티컬 확률 증가 (실제 크리티컬 적용)
            if trait_effects.get("crit_chance_bonus") and current_stance.value in ["aggressive", "berserker"]:
                # 크리티컬 확률 증가를 실제 크리티컬 데미지로 적용
                import random
                crit_chance = trait_effects["crit_chance_bonus"]  # 0.2 (20%)
                if random.random() < crit_chance:
                    modified_damage = int(modified_damage * 1.5)  # 1.5배 크리티컬 데미지
                    print(f"💥 전투 본능 크리티컬 발동! 데미지 1.5배!")
            
            # 균형감각: 균형 자세에서 모든 능력치 증가
            if trait_effects.get("all_stats_multiplier") and current_stance.value == "balanced":
                modified_damage = int(modified_damage * trait_effects["all_stats_multiplier"])
        else:
            stance_amplify = 1.0
            
        # 다음 공격 부스트 효과 적용 (적응형 무술)
        if hasattr(warrior, 'next_attack_boost'):
            modified_damage = int(modified_damage * warrior.next_attack_boost)
            delattr(warrior, 'next_attack_boost')  # 일회성 효과이므로 제거
            print(f"🔥 적응형 무술 효과 적용! 공격력 증가!")
        
        # 공격력 보너스 (특성으로 증폭)
        if skill_type in ['physical', 'attack']:
            attack_bonus = bonuses.get('physical_attack_bonus', 0) * stance_amplify
            modified_damage = int(modified_damage * (1 + attack_bonus))
        
        # 스킬 위력 보너스 (특성으로 증폭)
        if skill_type == 'skill':
            skill_bonus = bonuses.get('skill_power_bonus', 0) * stance_amplify
            modified_damage = int(modified_damage * (1 + skill_bonus))
        
        return modified_damage
    
    def get_stance_display(self, warrior) -> str:
        """자세 상태 표시"""
        current_stance = self.get_current_stance(warrior)
        stance_info = self.stance_bonuses[current_stance]
        return stance_info['name']
    
    def get_stance_description(self, warrior) -> str:
        """자세 설명"""
        current_stance = self.get_current_stance(warrior)
        stance_info = self.stance_bonuses[current_stance]
        return stance_info['description']


# 전역 전사 시스템 인스턴스
_warrior_system = None

def get_warrior_system() -> WarriorAdaptiveSystem:
    """전사 시스템 인스턴스 반환 (싱글톤)"""
    global _warrior_system
    if _warrior_system is None:
        _warrior_system = WarriorAdaptiveSystem()
    return _warrior_system


# new_skill_system.py에 추가할 StatusType
# StatusType 클래스에 다음 추가:
# WARRIOR_STANCE = "warrior_stance"
