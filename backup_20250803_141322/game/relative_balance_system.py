#!/usr/bin/env python3
"""
🔥 밸런스 수치 재조정 - 절대값 → 상대값 전환 시스템
- 모든 수치를 상대적 기준으로 변경
- 레벨/층수에 따른 동적 스케일링
- 플레이어 친화적 난이도 곡선
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .character import Character

class RelativeBalanceSystem:
    """상대적 밸런스 시스템"""
    
    @staticmethod
    def calculate_relative_damage(attacker_attack: int, defender_defense: int, 
                                base_multiplier: float = 1.0) -> int:
        """상대적 데미지 계산 공식"""
        # 공격력/방어력 비율 기반 계산
        if defender_defense <= 0:
            defender_defense = 1
            
        ratio = attacker_attack / defender_defense
        
        # 로그 스케일링으로 극단적 수치 방지
        if ratio >= 1.0:
            # 공격이 방어보다 높을 때
            damage_multiplier = 1.0 + math.log(ratio) * 0.5
        else:
            # 방어가 공격보다 높을 때
            damage_multiplier = ratio * 0.8
        
        # 기본 데미지는 공격력의 일정 비율
        base_damage = attacker_attack * 0.6  # 공격력의 60%가 기본 데미지
        final_damage = int(base_damage * damage_multiplier * base_multiplier)
        
        return max(1, final_damage)  # 최소 1 데미지
    
    @staticmethod
    def calculate_enemy_stats_by_floor(base_stats: Dict[str, int], floor: int, 
                                     party_average_level: int = 1) -> Dict[str, int]:
        """층수와 파티 레벨에 따른 적 스탯 조정"""
        adjusted_stats = {}
        
        # 기본 스케일링 팩터 (층수 기반)
        floor_factor = 1.0 + (floor - 1) * 0.15  # 층당 15% 증가
        
        # 파티 레벨 기반 조정 (파티가 강하면 적도 강해짐)
        level_factor = 1.0 + (party_average_level - 1) * 0.1  # 레벨당 10% 증가
        
        # 최종 스케일링 팩터
        total_factor = floor_factor * level_factor
        
        # 각 스탯 조정
        for stat_name, base_value in base_stats.items():
            if stat_name in ['hp', 'max_hp']:
                # HP는 더 크게 스케일링 (생존력 확보)
                adjusted_stats[stat_name] = int(base_value * total_factor * 1.2)
            elif stat_name in ['physical_attack', 'magic_attack']:
                # 공격력은 적당히 스케일링
                adjusted_stats[stat_name] = int(base_value * total_factor)
            elif stat_name in ['physical_defense', 'magic_defense']:
                # 방어력은 조금 낮게 스케일링 (플레이어 유리)
                adjusted_stats[stat_name] = int(base_value * total_factor * 0.9)
            elif stat_name == 'speed':
                # 속도는 완만하게 스케일링
                adjusted_stats[stat_name] = int(base_value * (1.0 + (total_factor - 1.0) * 0.6))
            else:
                adjusted_stats[stat_name] = int(base_value * total_factor)
        
        return adjusted_stats
    
    @staticmethod
    def calculate_experience_reward(enemy_level: int, player_level: int, 
                                  base_exp: int = 100) -> int:
        """레벨 차이에 따른 경험치 보상 조정"""
        level_diff = enemy_level - player_level
        
        if level_diff >= 5:
            # 훨씬 강한 적: 큰 보너스
            multiplier = 2.0 + (level_diff - 5) * 0.2
        elif level_diff >= 0:
            # 비슷하거나 약간 강한 적: 기본~보너스
            multiplier = 1.0 + level_diff * 0.2
        elif level_diff >= -3:
            # 약간 약한 적: 약간 감소
            multiplier = 1.0 + level_diff * 0.1
        else:
            # 훨씬 약한 적: 크게 감소
            multiplier = max(0.1, 0.7 + level_diff * 0.05)
        
        return int(base_exp * multiplier)
    
    @staticmethod
    def calculate_gold_reward(enemy_level: int, floor: int, 
                            party_average_level: int = 1) -> int:
        """상대적 골드 보상 계산"""
        # 기본 골드는 층수 기반
        base_gold = 20 + floor * 15
        
        # 적 레벨 보너스
        level_bonus = enemy_level * 5
        
        # 파티 레벨에 따른 조정 (높은 레벨일수록 더 많은 골드 필요)
        level_multiplier = 1.0 + (party_average_level - 1) * 0.15
        
        total_gold = int((base_gold + level_bonus) * level_multiplier)
        
        # 랜덤 변동 (±20%)
        import random
        variation = random.uniform(0.8, 1.2)
        
        return max(1, int(total_gold * variation))
    
    @staticmethod
    def calculate_skill_damage_scaling(caster_level: int, skill_base_power: int, 
                                     stat_value: int, skill_type: str = "magic") -> int:
        """스킬 데미지 스케일링 계산"""
        # 기본 위력
        base_power = skill_base_power
        
        # 레벨 스케일링 (완만한 증가)
        level_bonus = caster_level * 5
        
        # 스탯 스케일링 (상대적)
        if skill_type == "magic":
            stat_scaling = stat_value * 0.8  # 마법 공격력의 80%
        elif skill_type == "physical":
            stat_scaling = stat_value * 0.7  # 물리 공격력의 70%
        else:
            stat_scaling = stat_value * 0.6  # 기타 스킬
        
        total_power = base_power + level_bonus + stat_scaling
        
        return max(1, int(total_power))
    
    @staticmethod
    def calculate_healing_effectiveness(caster_level: int, heal_base_power: int, 
                                      magic_attack: int, target_max_hp: int) -> int:
        """치유 효과 계산 (대상의 최대 HP 기준)"""
        # 기본 치유량
        base_heal = heal_base_power
        
        # 시전자 레벨 보너스
        level_bonus = caster_level * 3
        
        # 마법 공격력 보너스 (적당히)
        stat_bonus = magic_attack * 0.5
        
        # 대상의 최대 HP에 비례한 최소 치유량 보장
        min_heal_ratio = 0.15  # 최소 15% 치유
        min_heal = int(target_max_hp * min_heal_ratio)
        
        total_heal = base_heal + level_bonus + stat_bonus
        
        return max(min_heal, int(total_heal))
    
    @staticmethod
    def calculate_status_duration(caster_level: int, target_level: int, 
                                base_duration: int = 3) -> int:
        """상태이상 지속시간 계산"""
        level_diff = caster_level - target_level
        
        # 레벨 차이에 따른 지속시간 조정
        if level_diff >= 3:
            duration_modifier = 1.5
        elif level_diff >= 0:
            duration_modifier = 1.0 + level_diff * 0.2
        else:
            duration_modifier = max(0.5, 1.0 + level_diff * 0.15)
        
        final_duration = int(base_duration * duration_modifier)
        
        return max(1, min(final_duration, 8))  # 최소 1턴, 최대 8턴
    
    @staticmethod
    def calculate_critical_damage_multiplier(attacker_level: int, critical_rate: float = 0.05) -> float:
        """크리티컬 데미지 배율 계산"""
        base_multiplier = 1.5  # 기본 150% 데미지
        
        # 레벨이 높을수록 크리티컬 위력 증가 (완만하게)
        level_bonus = attacker_level * 0.02  # 레벨당 2% 증가
        
        # 크리티컬 확률이 낮을수록 위력 증가 (트레이드오프)
        rarity_bonus = max(0, (0.2 - critical_rate) * 2)  # 크리티컬이 희귀할수록 강함
        
        final_multiplier = base_multiplier + level_bonus + rarity_bonus

        return min(final_multiplier, 2.0)  # 최대 200% 데미지

    @staticmethod
    def calculate_item_price_scaling(base_price: int, player_level: int, 
                                   floor: int, item_rarity: str = "common") -> int:
        """아이템 가격 스케일링"""
        # 기본 가격
        price = base_price
        
        # 플레이어 레벨에 따른 조정 (경제력 고려)
        level_multiplier = 1.0 + (player_level - 1) * 0.2
        
        # 층수에 따른 조정 (더 깊은 층일수록 비쌈)
        floor_multiplier = 1.0 + (floor - 1) * 0.1
        
        # 희귀도 배율
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 2.5,
            "rare": 6.0,
            "epic": 15.0,
            "legendary": 40.0,
            "mythic": 100.0
        }
        
        rarity_multiplier = rarity_multipliers.get(item_rarity, 1.0)
        
        final_price = int(price * level_multiplier * floor_multiplier * rarity_multiplier)
        
        return max(1, final_price)
    
    @staticmethod
    def calculate_encounter_difficulty(floor: int, party_average_level: int, 
                                     party_size: int = 4) -> Dict[str, float]:
        """조우 난이도 계산"""
        difficulty_factors = {}
        
        # 기본 난이도 (층수 기반)
        base_difficulty = 1.0 + (floor - 1) * 0.1
        
        # 파티 레벨 대비 조정
        if party_average_level > floor:
            # 파티가 층수보다 높으면 난이도 증가
            level_adjustment = 1.0 + (party_average_level - floor) * 0.15
        else:
            # 파티가 층수보다 낮으면 난이도 완화
            level_adjustment = max(0.7, 1.0 - (floor - party_average_level) * 0.1)
        
        # 파티 크기에 따른 조정
        party_adjustment = 1.0 + (party_size - 4) * 0.2  # 4인 기준
        
        final_difficulty = base_difficulty * level_adjustment * party_adjustment
        
        difficulty_factors['combat_difficulty'] = final_difficulty
        difficulty_factors['trap_damage_multiplier'] = final_difficulty * 0.8
        difficulty_factors['reward_multiplier'] = final_difficulty * 1.2
        difficulty_factors['experience_multiplier'] = final_difficulty
        
        return difficulty_factors
    
    @staticmethod
    def get_recommended_party_composition(floor: int) -> Dict[str, Any]:
        """층수에 따른 권장 파티 구성 제안"""
        recommendations = {
            'min_level': max(1, floor - 2),
            'recommended_level': floor,
            'suggested_roles': [],
            'difficulty_warnings': []
        }
        
        # 기본 역할 제안
        recommendations['suggested_roles'] = ['전사/탱커', '마법사/딜러', '성직자/힐러', '도적/유틸리티']
        
        # 층수별 특별 제안
        if floor >= 10:
            recommendations['difficulty_warnings'].append("강력한 적들이 등장합니다. 충분한 회복 아이템을 준비하세요.")
            recommendations['suggested_roles'].append('추가 힐러 또는 서포터')
        
        if floor >= 20:
            recommendations['difficulty_warnings'].append("엘리트 몬스터가 자주 등장합니다. 다양한 대응책을 준비하세요.")
            recommendations['min_level'] = floor - 1
        
        if floor >= 30:
            recommendations['difficulty_warnings'].append("보스급 적들이 등장할 수 있습니다. 최고 수준의 준비가 필요합니다.")
            recommendations['min_level'] = floor
        
        return recommendations

class BalanceValidator:
    """밸런스 검증 시스템"""
    
    @staticmethod
    def validate_damage_range(attacker_stats: Dict, defender_stats: Dict) -> Dict[str, Any]:
        """데미지 범위 검증"""
        balance_system = RelativeBalanceSystem()
        
        # 다양한 시나리오 테스트
        scenarios = [
            {'name': '일반 공격', 'multiplier': 1.0},
            {'name': '약한 공격', 'multiplier': 0.7},
            {'name': '강한 공격', 'multiplier': 1.5},
            {'name': '크리티컬', 'multiplier': 2.0}
        ]
        
        results = {}
        for scenario in scenarios:
            damage = balance_system.calculate_relative_damage(
                attacker_stats['attack'],
                defender_stats['defense'], 
                scenario['multiplier']
            )
            
            # 데미지가 상대방 HP의 몇 %인지 계산
            damage_percent = (damage / defender_stats['hp']) * 100
            
            results[scenario['name']] = {
                'damage': damage,
                'hp_percent': damage_percent,
                'turns_to_kill': math.ceil(defender_stats['hp'] / damage) if damage > 0 else float('inf')
            }
        
        return results
    
    @staticmethod
    def suggest_balance_adjustments(validation_results: Dict) -> List[str]:
        """밸런스 조정 제안"""
        suggestions = []
        
        normal_attack = validation_results.get('일반 공격', {})
        turns_to_kill = normal_attack.get('turns_to_kill', 0)
        
        if turns_to_kill > 10:
            suggestions.append("전투가 너무 길어집니다. 공격력을 높이거나 방어력을 낮추는 것을 고려하세요.")
        elif turns_to_kill < 3:
            suggestions.append("전투가 너무 빨리 끝납니다. 방어력을 높이거나 공격력을 낮추는 것을 고려하세요.")
        
        critical_damage = validation_results.get('크리티컬', {})
        crit_percent = critical_damage.get('hp_percent', 0)
        
        if crit_percent > 80:
            suggestions.append("크리티컬 데미지가 너무 높습니다. 일격사가 너무 자주 발생할 수 있습니다.")
        elif crit_percent < 30:
            suggestions.append("크리티컬 데미지가 너무 낮습니다. 크리티컬의 가치가 부족합니다.")
        
        return suggestions

# 편의 함수들
def calculate_balanced_damage(attacker_attack: int, defender_defense: int, 
                            multiplier: float = 1.0) -> int:
    """편의 함수: 균형잡힌 데미지 계산"""
    return RelativeBalanceSystem.calculate_relative_damage(attacker_attack, defender_defense, multiplier)

def scale_enemy_for_floor(base_stats: Dict[str, int], floor: int, 
                         party_level: int = 1) -> Dict[str, int]:
    """편의 함수: 층수에 맞는 적 스탯 조정"""
    return RelativeBalanceSystem.calculate_enemy_stats_by_floor(base_stats, floor, party_level)

def calculate_fair_rewards(enemy_level: int, floor: int, party_level: int = 1) -> Dict[str, int]:
    """편의 함수: 공정한 보상 계산"""
    return {
        'experience': RelativeBalanceSystem.calculate_experience_reward(enemy_level, party_level),
        'gold': RelativeBalanceSystem.calculate_gold_reward(enemy_level, floor, party_level)
    }

def validate_combat_balance(attacker_stats: Dict, defender_stats: Dict) -> Dict[str, Any]:
    """편의 함수: 전투 밸런스 검증"""
    return BalanceValidator.validate_damage_range(attacker_stats, defender_stats)

# 전역 인스턴스
balance_system = RelativeBalanceSystem()
balance_validator = BalanceValidator()

def get_balance_system() -> RelativeBalanceSystem:
    """밸런스 시스템 반환"""
    return balance_system

def get_balance_validator() -> BalanceValidator:
    """밸런스 검증기 반환"""
    return balance_validator
