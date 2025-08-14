# -*- coding: utf-8 -*-
"""
Dawn of Stellar 밸런스 통합 시스템 (2025.08.10)

유저의 도적 독 밸런스 조정을 기준으로 한 종합적 밸런스 시스템
- 독 위력: 25% → 60% (2.4배 증가) 기준
- 지속시간: 2-4턴 표준화
- 방어력 관련: 보수적 조정 (최대 ±20%)
- 물리/마법 스탯 분리 체계 존중
"""

from typing import Dict, List, Tuple, Any
import random
from enum import Enum

class BalanceType(Enum):
    CONSERVATIVE = "conservative"  # 방어력, 체력 등 민감한 스탯
    MODERATE = "moderate"         # 일반적인 효과들
    AGGRESSIVE = "aggressive"     # 공격력, 독 등 직접적 피해

class StatType(Enum):
    PHYSICAL_ATTACK = "physical_attack"
    MAGIC_ATTACK = "magic_attack"
    PHYSICAL_DEFENSE = "physical_defense"
    MAGIC_DEFENSE = "magic_defense"
    ACCURACY = "accuracy"
    EVASION = "evasion"
    SPEED = "speed"
    HP = "hp"
    MP = "mp"

class BalanceConfig:
    """밸런스 설정 - 유저의 도적 독 조정을 기준으로 한 계수들"""
    
    # 기준: 유저가 독 계수를 25% → 60%로 증가 (2.4배)
    POISON_BASE_MULTIPLIER = 2.4
    
    # 지속시간 표준화 (유저 요청사항)
    DURATION_LIMITS = {
        "min": 2,
        "max": 4,
        "poison_max": 5,  # 독은 예외적으로 5턴까지 허용
        "debuff_max": 4,  # 디버프는 최대 4턴
        "buff_max": 4     # 버프는 최대 4턴
    }
    
    # 밸런스 타입별 조정 계수
    BALANCE_MULTIPLIERS = {
        BalanceType.CONSERVATIVE: {
            "min": 0.85,  # 최대 15% 감소
            "max": 1.15   # 최대 15% 증가
        },
        BalanceType.MODERATE: {
            "min": 0.75,  # 최대 25% 감소
            "max": 1.35   # 최대 35% 증가
        },
        BalanceType.AGGRESSIVE: {
            "min": 0.6,   # 최대 40% 감소
            "max": 2.4    # 최대 140% 증가 (독 기준)
        }
    }
    
    # 스탯별 밸런스 타입 분류
    STAT_BALANCE_TYPES = {
        StatType.PHYSICAL_DEFENSE: BalanceType.CONSERVATIVE,
        StatType.MAGIC_DEFENSE: BalanceType.CONSERVATIVE,
        StatType.HP: BalanceType.CONSERVATIVE,
        StatType.PHYSICAL_ATTACK: BalanceType.MODERATE,
        StatType.MAGIC_ATTACK: BalanceType.MODERATE,
        StatType.ACCURACY: BalanceType.MODERATE,
        StatType.EVASION: BalanceType.MODERATE,
        StatType.SPEED: BalanceType.MODERATE,
        StatType.MP: BalanceType.MODERATE,
    }

class BalanceIntegrationSystem:
    """밸런스 통합 시스템"""
    
    def __init__(self):
        self.config = BalanceConfig()
        self.adjustment_log = []
    
    def standardize_duration(self, current_duration: int, effect_type: str = "general") -> int:
        """지속시간 표준화 (2-4턴 기준)"""
        limits = self.config.DURATION_LIMITS
        
        if effect_type == "poison":
            max_duration = limits["poison_max"]
        elif effect_type == "debuff":
            max_duration = limits["debuff_max"]
        elif effect_type == "buff":
            max_duration = limits["buff_max"]
        else:
            max_duration = limits["max"]
        
        # 현재 지속시간을 표준 범위로 조정
        if current_duration < limits["min"]:
            standardized = limits["min"]
        elif current_duration > max_duration:
            standardized = max_duration
        else:
            standardized = current_duration
        
        if standardized != current_duration:
            self.adjustment_log.append(f"지속시간 조정: {current_duration}턴 → {standardized}턴 ({effect_type})")
        
        return standardized
    
    def calculate_balanced_power(self, current_power: float, stat_type: StatType) -> float:
        """스탯 타입에 따른 밸런스 조정된 위력 계산"""
        balance_type = self.config.STAT_BALANCE_TYPES.get(stat_type, BalanceType.MODERATE)
        multipliers = self.config.BALANCE_MULTIPLIERS[balance_type]
        
        # 현재 위력이 너무 낮으면 적당히 상향
        if current_power < 0.5:
            adjusted_power = min(current_power * 1.5, multipliers["max"])
        # 현재 위력이 너무 높으면 적당히 하향
        elif current_power > 2.0:
            adjusted_power = max(current_power * 0.8, multipliers["min"])
        else:
            adjusted_power = current_power
        
        # 밸런스 타입 한계 내에서 조정
        adjusted_power = max(multipliers["min"], min(adjusted_power, multipliers["max"]))
        
        if abs(adjusted_power - current_power) > 0.05:
            self.adjustment_log.append(
                f"{stat_type.value} 위력 조정: {current_power:.2f} → {adjusted_power:.2f} ({balance_type.value})"
            )
        
        return adjusted_power
    
    def generate_poison_config(self, base_attack_ratio: float = 0.6) -> Dict[str, Any]:
        """독 설정 생성 (유저의 60% 기준 사용)"""
        return {
            "attack_ratio": base_attack_ratio,  # 공격력의 60% (유저 기준)
            "duration": self.standardize_duration(4, "poison"),  # 4턴 표준
            "stacking": True,
            "amplification": 0.5,  # 독 증폭 계수 (유저가 0.3→0.5로 증가)
            "corrosive_defense_reduction": 0.3,  # 부식 방어력 감소 30%
            "max_stacks": 10
        }
    
    def generate_status_effect_config(self, effect_name: str, current_config: Dict) -> Dict[str, Any]:
        """상태 효과 설정 생성"""
        # 현재 설정에서 지속시간과 위력 추출
        current_duration = current_config.get("duration", 3)
        current_power = current_config.get("power", 1.0)
        
        # 효과 타입 결정
        if "poison" in effect_name.lower() or "독" in effect_name:
            effect_type = "poison"
            stat_type = StatType.PHYSICAL_ATTACK  # 독은 공격력 기반
        elif any(keyword in effect_name.lower() for keyword in ["defense", "방어", "def"]):
            effect_type = "debuff"
            stat_type = StatType.PHYSICAL_DEFENSE
        elif any(keyword in effect_name.lower() for keyword in ["attack", "공격", "atk"]):
            effect_type = "buff"
            stat_type = StatType.PHYSICAL_ATTACK
        else:
            effect_type = "general"
            stat_type = StatType.PHYSICAL_ATTACK
        
        # 표준화된 설정 생성
        balanced_config = {
            "duration": self.standardize_duration(current_duration, effect_type),
            "power": self.calculate_balanced_power(current_power, stat_type),
            "effect_type": effect_type,
            "stat_type": stat_type.value
        }
        
        return balanced_config
    
    def apply_skill_balance_adjustments(self) -> Dict[str, Any]:
        """스킬 시스템 밸런스 조정사항 생성"""
        adjustments = {
            "poison_system": self.generate_poison_config(),
            "duration_adjustments": {},
            "power_adjustments": {},
            "new_limits": self.config.DURATION_LIMITS.copy()
        }
        
        # 일반적인 스킬 효과들의 표준화
        common_effects = [
            {"name": "스턴", "current": {"duration": 2, "power": 1.0}},
            {"name": "빙결", "current": {"duration": 2, "power": 1.0}},
            {"name": "화상", "current": {"duration": 3, "power": 1.0}},
            {"name": "감전", "current": {"duration": 3, "power": 1.0}},
            {"name": "약화", "current": {"duration": 4, "power": 0.7}},
            {"name": "둔화", "current": {"duration": 3, "power": 0.5}},
            {"name": "실명", "current": {"duration": 3, "power": 0.5}},
            {"name": "공격력강화", "current": {"duration": 3, "power": 1.2}},
            {"name": "방어력강화", "current": {"duration": 3, "power": 1.2}},
            {"name": "크리티컬강화", "current": {"duration": 4, "power": 1.5}},
        ]
        
        for effect in common_effects:
            balanced = self.generate_status_effect_config(effect["name"], effect["current"])
            adjustments["duration_adjustments"][effect["name"]] = balanced["duration"]
            adjustments["power_adjustments"][effect["name"]] = balanced["power"]
        
        return adjustments
    
    def generate_enemy_balance_adjustments(self) -> Dict[str, Any]:
        """적 시스템 밸런스 조정사항 생성"""
        return {
            "stat_scaling": {
                "physical_defense": {
                    "base_multiplier": 1.0,
                    "max_adjustment": 0.15,  # 최대 15% 조정 (보수적)
                    "balance_type": "conservative"
                },
                "magic_defense": {
                    "base_multiplier": 1.0,
                    "max_adjustment": 0.15,  # 최대 15% 조정 (보수적)
                    "balance_type": "conservative"
                },
                "physical_attack": {
                    "base_multiplier": 1.0,
                    "max_adjustment": 0.25,  # 최대 25% 조정 (중간)
                    "balance_type": "moderate"
                },
                "magic_attack": {
                    "base_multiplier": 1.0,
                    "max_adjustment": 0.25,  # 최대 25% 조정 (중간)
                    "balance_type": "moderate"
                }
            },
            "status_resistance": {
                "poison_resistance": 0.2,  # 20% 독 저항
                "stun_resistance": 0.3,    # 30% 스턴 저항
                "debuff_resistance": 0.15  # 15% 일반 디버프 저항
            },
            "level_scaling": {
                "hp_per_level": 25,        # 레벨당 HP 증가량
                "attack_per_level": 3,     # 레벨당 공격력 증가량
                "defense_per_level": 2     # 레벨당 방어력 증가량 (보수적)
            }
        }
    
    def get_comprehensive_balance_report(self) -> str:
        """종합 밸런스 리포트 생성"""
        skill_adjustments = self.apply_skill_balance_adjustments()
        enemy_adjustments = self.generate_enemy_balance_adjustments()
        
        report = """
=== Dawn of Stellar 밸런스 통합 시스템 리포트 ===

🎯 밸런스 철학:
- 유저의 도적 독 조정(25%→60%)을 기준점으로 사용
- 방어력 관련 스탯은 보수적 조정 (최대 ±15%)
- 지속시간 표준화: 2-4턴 (독은 5턴까지)
- 물리/마법 스탯 분리 체계 완전 존중

🔧 주요 조정사항:

1. 독 시스템 표준화:
   - 공격력 비율: 60% (유저 기준점)
   - 지속시간: 4-5턴 표준
   - 독 증폭: 0.5 계수
   - 부식 효과: 방어력 30% 감소

2. 지속시간 표준화:
   - 일반 효과: 2-4턴
   - 독 효과: 2-5턴
   - 버프: 2-4턴
   - 디버프: 2-4턴

3. 방어력 보수적 조정:
   - 물리방어: 최대 ±15%
   - 마법방어: 최대 ±15%
   - 체력: 최대 ±15%

4. 공격력 중간 조정:
   - 물리공격: 최대 ±25%
   - 마법공격: 최대 ±25%
   - 정확도/회피: 최대 ±25%

📊 적용된 조정 로그:
"""
        
        for log_entry in self.adjustment_log:
            report += f"   • {log_entry}\n"
        
        report += f"""

🔍 구체적 수치:
- 독 기본 계수: {skill_adjustments['poison_system']['attack_ratio']:.1%}
- 독 증폭 계수: {skill_adjustments['poison_system']['amplification']}
- 부식 방어감소: {skill_adjustments['poison_system']['corrosive_defense_reduction']:.1%}
- 표준 지속시간 범위: {skill_adjustments['new_limits']['min']}-{skill_adjustments['new_limits']['max']}턴

💡 구현 권장사항:
1. new_skill_system.py 의 지속시간들을 2-4턴으로 통일
2. 방어력 관련 효과들의 위력을 15% 이내로 제한
3. 독 시스템을 유저 기준(60%)으로 통일
4. 물리/마법 스탯을 별도로 처리하는 로직 확인

=== 리포트 끝 ===
"""
        
        return report
    
    def export_balance_config(self) -> Dict[str, Any]:
        """밸런스 설정을 다른 시스템에서 사용할 수 있도록 내보내기"""
        return {
            "skill_adjustments": self.apply_skill_balance_adjustments(),
            "enemy_adjustments": self.generate_enemy_balance_adjustments(),
            "balance_config": {
                "duration_limits": self.config.DURATION_LIMITS,
                "balance_multipliers": self.config.BALANCE_MULTIPLIERS,
                "stat_balance_types": {k.value: v.value for k, v in self.config.STAT_BALANCE_TYPES.items()}
            }
        }

# 사용 예시
if __name__ == "__main__":
    balance_system = BalanceIntegrationSystem()
    
    # 밸런스 리포트 생성
    report = balance_system.get_comprehensive_balance_report()
    print(report)
    
    # 설정 내보내기
    config = balance_system.export_balance_config()
    
    # 독 설정 예시
    poison_config = balance_system.generate_poison_config()
    print(f"\n독 설정 예시: {poison_config}")
