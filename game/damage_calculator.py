"""
데미지 계산 시스템 - 로깅 기능이 통합된 데미지 계산
"""

import random
from typing import Dict, Any, Optional
from .combat_logger import combat_logger

class DamageCalculator:
    """로깅이 통합된 데미지 계산 시스템"""
    
    @staticmethod
    def calculate_brv_damage(attacker, target, skill_power: float = 100.0, 
                           skill_name: str = None, multipliers: Dict = None) -> int:
        """BRV 데미지 계산 및 로깅"""
        from .balance import GameBalance
        
        # 기본 스탯 가져오기
        attacker_atk = getattr(attacker, 'physical_attack', 100)
        target_def = getattr(target, 'physical_defense', 50)
        
        # 회피 체크
        if DamageCalculator._check_dodge(attacker, target):
            combat_logger.log_damage(attacker, target, "BRV", 0, skill_name, 
                                   {"result": "DODGED"})
            return 0
        
        # 기본 데미지 계산
        base_damage = GameBalance.calculate_brave_damage(attacker_atk, target_def)
        
        # 스킬 배율 적용
        skill_damage = int(base_damage * (skill_power / 100.0))
        
        # 추가 배율들 적용
        final_multipliers = multipliers or {}
        
        # 스킬 데미지 배율 (일반공격 대비 1.2-1.5배)
        if skill_power >= 150:  # 강력한 스킬
            skill_multiplier = 1.4
        elif skill_power >= 120:  # 중간 스킬
            skill_multiplier = 1.3
        else:  # 기본 스킬
            skill_multiplier = 1.2
            
        final_multipliers['skill_multiplier'] = skill_multiplier
        skill_damage = int(skill_damage * skill_multiplier)
        
        # 플레이어/적 구분 배율
        if hasattr(attacker, 'character_class'):  # 플레이어
            player_multiplier = 1.0
        else:  # 적
            player_multiplier = 0.9
            
        final_multipliers['actor_type_multiplier'] = player_multiplier
        skill_damage = int(skill_damage * player_multiplier)
        
        # 랜덤 변수
        random_factor = random.uniform(0.95, 1.05)
        final_multipliers['random_factor'] = random_factor
        final_damage = int(skill_damage * random_factor)
        
        # 최종 제한
        final_damage = max(10, min(9999, final_damage))
        
        # 간소화된 로그 기록
        combat_logger.log_damage(attacker, target, "BRV", final_damage, skill_name, {})
        
        return final_damage
    
    @staticmethod
    def calculate_hp_damage(attacker, target, hp_power: float = 100.0, 
                          skill_name: str = None, multipliers: Dict = None) -> int:
        """HP 데미지 계산 및 로깅"""
        from .balance import GameBalance
        
        # BRV 포인트 기반 데미지
        brave_points = getattr(attacker, 'brave_points', 500)
        
        # 기본 데미지 계산
        base_damage = int(brave_points * (hp_power / 100.0))
        
        # 추가 배율들
        final_multipliers = multipliers or {}
        
        # 기본 HP 데미지 배율 (GameBalance에서)
        hp_base_multiplier = GameBalance.HP_DAMAGE_MULTIPLIER
        final_multipliers['hp_base_multiplier'] = hp_base_multiplier
        base_damage = int(base_damage * hp_base_multiplier)
        
        # 플레이어/적 구분 배율
        if hasattr(attacker, 'character_class'):  # 플레이어
            actor_multiplier = 1.0
        else:  # 적 - HP 공격 배율을 1/3로 추가 감소
            actor_multiplier = 0.01125  # 0.03375 × (1/3) = 0.01125
            
        final_multipliers['actor_multiplier'] = actor_multiplier
        base_damage = int(base_damage * actor_multiplier)
        
        # Break 상태 보너스
        break_bonus = 1.0
        if hasattr(target, 'is_broken_state') and target.is_broken_state:
            break_bonus = GameBalance.BREAK_DAMAGE_BONUS
            final_multipliers['break_bonus'] = break_bonus
            base_damage = int(base_damage * break_bonus)
        
        # 취약점 효과 (진실 간파 등)
        vulnerability_bonus = 1.0
        if hasattr(target, 'temp_vulnerability') and target.temp_vulnerability > 0:
            vulnerability_bonus = 1.0 + target.temp_vulnerability
            final_multipliers['vulnerability_bonus'] = vulnerability_bonus
            base_damage = int(base_damage * vulnerability_bonus)
            
            # 취약점 지속시간 감소
            if hasattr(target, 'vulnerability_turns'):
                target.vulnerability_turns -= 1
                if target.vulnerability_turns <= 0:
                    target.temp_vulnerability = 0
                    target.vulnerability_turns = 0
        
        # 최소 데미지 보장
        final_damage = max(base_damage, 10)
        
        # 간소화된 로그 기록
        combat_logger.log_damage(attacker, target, "HP", final_damage, skill_name, {})
        
        # BRV 소모 처리 (로그 간소화)
        if hasattr(attacker, 'consume_brave_points'):
            attacker.consume_brave_points()
        else:
            attacker.brave_points = 0
        
        return final_damage
    
    @staticmethod
    def calculate_heal_amount(caster, target, heal_power: float = 100.0, 
                            skill_name: str = None) -> int:
        """힐량 계산 및 로깅"""
        # 기본 힐량
        magic_attack = getattr(caster, 'magic_attack', 100)
        base_heal = int(heal_power + (magic_attack * 0.5))
        
        # 랜덤 변수
        random_factor = random.uniform(0.9, 1.1)
        final_heal = int(base_heal * random_factor)
        final_heal = max(final_heal, 1)
        
        # 간소화된 로그 기록
        combat_logger.log_damage(caster, target, "HEAL", final_heal, skill_name, {})
        
        return final_heal
    
    @staticmethod
    def _check_dodge(attacker, target) -> bool:
        """회피 체크"""
        attacker_speed = getattr(attacker, 'speed', 100)
        target_speed = getattr(target, 'speed', 100)
        
        # 속도 차이에 따른 회피율 (최대 15%)
        speed_diff = target_speed - attacker_speed
        dodge_rate = min(0.15, max(0.02, speed_diff / 1000))
        
        return random.random() < dodge_rate
    
    @staticmethod
    def apply_damage_to_target(target, damage: int, damage_type: str = "HP") -> Dict:
        """대상에게 데미지 적용 및 결과 반환"""
        result = {
            "damage_dealt": 0,
            "target_defeated": False,
            "hp_before": getattr(target, 'current_hp', 0),
            "hp_after": 0,
            "brv_before": getattr(target, 'brave_points', 0),
            "brv_after": 0
        }
        
        if damage_type == "HP":
            # HP 데미지
            actual_damage = min(damage, target.current_hp)
            target.current_hp -= actual_damage
            result["damage_dealt"] = actual_damage
            result["hp_after"] = target.current_hp
            result["brv_after"] = getattr(target, 'brave_points', 0)
            
            # 사망 체크
            if target.current_hp <= 0:
                target.current_hp = 0
                target.is_alive = False
                result["target_defeated"] = True
                combat_logger.log_character_death(target)
                
            # 상처 시스템 적용
            if hasattr(target, 'wounds'):
                wound_damage = int(actual_damage * 0.25)
                max_wounds = int(target.max_hp * 0.75)
                target.wounds = min(target.wounds + wound_damage, max_wounds)
                
        elif damage_type == "BRV":
            # BRV 데미지
            if hasattr(target, 'brave_points'):
                actual_damage = min(damage, target.brave_points)
                target.brave_points -= actual_damage
                result["damage_dealt"] = actual_damage
                result["hp_after"] = getattr(target, 'current_hp', 0)
                result["brv_after"] = target.brave_points
                
                # Break 상태 체크
                if target.brave_points <= 0 and hasattr(target, 'is_broken_state'):
                    target.is_broken_state = True
                    combat_logger.log_status_effect(target, "Break", "applied")
        
        elif damage_type == "HEAL":
            # 힐링
            if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
                # 제한된 최대 HP (상처 고려)
                max_healable_hp = target.max_hp
                if hasattr(target, 'wounds'):
                    max_healable_hp = target.max_hp - target.wounds
                
                heal_amount = min(damage, max_healable_hp - target.current_hp)
                target.current_hp += heal_amount
                result["damage_dealt"] = heal_amount
                result["hp_after"] = target.current_hp
                result["brv_after"] = getattr(target, 'brave_points', 0)
                
                # 초과 힐링으로 상처 치료 (25% 효율)
                excess_heal = damage - heal_amount
                if excess_heal > 0 and hasattr(target, 'wounds') and target.wounds > 0:
                    wound_heal = int(excess_heal * 0.25)
                    target.wounds = max(0, target.wounds - wound_heal)
        
        return result

# 전역 계산기 인스턴스
damage_calculator = DamageCalculator()
