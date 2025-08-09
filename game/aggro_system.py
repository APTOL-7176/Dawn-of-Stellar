#!/usr/bin/env python3
"""
🎯 동적 어그로 시스템 - Dawn of Stellar
적 AI의 타겟팅을 현실적으로 만드는 시스템
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
from dataclasses import dataclass

class AggroType(Enum):
    """어그로 타입"""
    DAMAGE = "damage"           # 피해량 기반
    HEALING = "healing"         # 힐링 기반  
    THREAT = "threat"           # 위협도 기반
    TAUNT = "taunt"            # 도발 기반
    PROTECTION = "protection"   # 보호 기반
    DEBUFF = "debuff"          # 디버프 기반

@dataclass
class AggroEvent:
    """어그로 이벤트"""
    source: str  # 행동한 캐릭터
    target: str  # 대상 (없을 수도 있음)
    action_type: str  # 행동 타입
    aggro_type: AggroType
    base_value: float  # HP 비율 변동량 (0.0 ~ 1.0)
    multiplier: float = 1.0  # 배율
    duration: int = 5  # 지속 턴수

class DynamicAggroSystem:
    """동적 어그로 시스템"""
    
    def __init__(self):
        # 캐릭터별 어그로 테이블 {enemy_id: {ally_id: aggro_value}}
        self.aggro_table: Dict[str, Dict[str, float]] = {}
        
        # 어그로 가중치 설정
        self.aggro_weights = {
            AggroType.DAMAGE: 1.0,      # 피해량 = 어그로
            AggroType.HEALING: 1.5,     # 힐링은 1.5배 어그로
            AggroType.THREAT: 2.0,      # 위협 스킬은 2배
            AggroType.TAUNT: 3.0,       # 도발은 3배
            AggroType.PROTECTION: 0.8,  # 보호는 0.8배
            AggroType.DEBUFF: 1.2       # 디버프는 1.2배
        }
        
        # 역할별 기본 어그로 배율
        self.role_aggro_multipliers = {
            "탱커": 1.2,    # 탱커는 기본적으로 높은 어그로
            "힐러": 1.4,    # 힐러는 매우 높은 어그로
            "딜러": 1.0,    # 딜러는 기본
            "서포터": 1.1   # 서포터는 낮은 어그로
        }
        
        # 어그로 감소율 (매 턴마다)
        self.aggro_decay_rate = 0.03  # 3%씩 감소 (더 완만하게)
        
        # 어그로는 상대적 개념 - 최대치 무제한
        self.min_aggro = 1.0   # 최소 1 (0이 되면 타겟팅에서 제외)
        self.max_aggro = float('inf')  # 실질적 무한
        
        # 어그로 메시지 표시 여부 (테스트 후 False로 변경 예정)
        self.show_aggro_messages = False  # 기본적으로 숨김
        
        # HP 비율 기반 어그로 배율 (비율 변동량을 실제 어그로로 변환)
        self.hp_ratio_multiplier = 100.0  # 10% HP 변동 = 10 어그로
        
    def get_party_size(self, enemy_id: str) -> int:
        """해당 적에 대한 아군 파티 크기 반환"""
        if enemy_id not in self.aggro_table:
            return 4  # 기본값
        return len(self.aggro_table[enemy_id])
        
    def initialize_enemy(self, enemy_id: str, allies: List):
        """적 캐릭터의 어그로 테이블 초기화"""
        if enemy_id not in self.aggro_table:
            self.aggro_table[enemy_id] = {}
            
        # 모든 아군에 대해 기본 어그로 설정
        for ally in allies:
            ally_id = getattr(ally, 'name', str(ally))
            if ally_id not in self.aggro_table[enemy_id]:
                # 역할에 따른 기본 어그로
                role = self._determine_role(ally)
                base_aggro = 10.0 * self.role_aggro_multipliers.get(role, 1.0)
                self.aggro_table[enemy_id][ally_id] = base_aggro
    
    def _determine_role(self, character) -> str:
        """캐릭터의 역할 판단"""
        char_class = getattr(character, 'character_class', '').lower()
        
        # 탱커 계열
        if char_class in ['전사', '기사', '성기사', '암흑기사', '검투사']:
            return "탱커"
        
        # 힐러 계열  
        elif char_class in ['신관', '드루이드', '연금술사']:
            return "힐러"
            
        # 서포터 계열
        elif char_class in ['바드', '시간술사', '철학자']:
            return "서포터"
            
        # 나머지는 딜러
        else:
            return "딜러"
    
    def add_aggro_event(self, enemy_id: str, event: AggroEvent):
        """어그로 이벤트 추가 (HP 비율 기반, 총합 균형 유지, 최소 10% 보장)"""
        if enemy_id not in self.aggro_table:
            return
            
        source_id = event.source
        if source_id not in self.aggro_table[enemy_id]:
            self.aggro_table[enemy_id][source_id] = 10.0
        
        # HP 비율 기반 어그로 계산 (0.0~1.0 비율을 실제 어그로 값으로 변환)
        aggro_value = event.base_value * self.hp_ratio_multiplier * event.multiplier
        aggro_value *= self.aggro_weights[event.aggro_type]
        
        # 타겟에게 어그로 추가
        old_aggro = self.aggro_table[enemy_id][source_id]
        self.aggro_table[enemy_id][source_id] += aggro_value
        
        # 증가한 어그로 양 계산
        aggro_increase = self.aggro_table[enemy_id][source_id] - old_aggro
        
        # 다른 아군들의 어그로를 균형 조정 (총합 유지)
        self._balance_aggro_distribution(enemy_id, source_id, aggro_increase)
        
        # 전체적으로 최소 10% 보장 재조정
        self._enforce_minimum_aggro_percentage(enemy_id)
        
        # 어그로 메시지는 표시하지 않음 (전황 분석에서만 표시)
    
    def _enforce_minimum_aggro_percentage(self, enemy_id: str):
        """모든 아군의 어그로가 최소 10% 이상이 되도록 강제 조정"""
        if enemy_id not in self.aggro_table:
            return
            
        aggro_dict = self.aggro_table[enemy_id]
        if not aggro_dict:
            return
            
        ally_count = len(aggro_dict)
        total_aggro = sum(aggro_dict.values())
        min_aggro_per_ally = total_aggro * 0.10  # 전체의 10%
        
        # 최소 어그로 미달 체크 및 조정
        adjustments_needed = {}
        total_shortage = 0
        
        for ally_id, aggro_value in aggro_dict.items():
            if aggro_value < min_aggro_per_ally:
                shortage = min_aggro_per_ally - aggro_value
                adjustments_needed[ally_id] = shortage
                total_shortage += shortage
        
        if not adjustments_needed:
            return  # 모든 아군이 이미 10% 이상
            
        # 초과 어그로를 가진 아군들에서 부족분 차감
        excess_allies = [aid for aid in aggro_dict.keys() if aid not in adjustments_needed]
        if not excess_allies:
            # 모든 아군이 최소치 미달이면 균등 분배
            for ally_id in aggro_dict.keys():
                aggro_dict[ally_id] = total_aggro / ally_count
        else:
            # 부족분을 초과 어그로 아군들에게서 차감
            reduction_per_excess = total_shortage / len(excess_allies)
            
            # 먼저 미달 아군들을 최소치로 올림
            for ally_id, shortage in adjustments_needed.items():
                aggro_dict[ally_id] = min_aggro_per_ally
            
            # 초과 아군들에서 차감 (단, 최소치는 보장)
            for ally_id in excess_allies:
                new_value = aggro_dict[ally_id] - reduction_per_excess
                aggro_dict[ally_id] = max(min_aggro_per_ally, new_value)
    
    def add_damage_taken_event(self, enemy_id: str, damaged_ally: str, hp_ratio_lost: float):
        """아군이 피해를 받았을 때 어그로 감소 (최소 10% 보장)"""
        if enemy_id not in self.aggro_table:
            return
            
        if damaged_ally not in self.aggro_table[enemy_id]:
            return
            
        # 받은 피해 비율만큼 어그로 감소
        aggro_reduction = hp_ratio_lost * self.hp_ratio_multiplier * 0.8  # 80% 적용
        
        old_aggro = self.aggro_table[enemy_id][damaged_ally]
        self.aggro_table[enemy_id][damaged_ally] -= aggro_reduction
        
        # 감소한 어그로 양 계산
        aggro_decrease = old_aggro - self.aggro_table[enemy_id][damaged_ally]
        
        # 다른 아군들의 어그로를 균형 조정 (감소한 만큼 다른 아군들이 증가)
        self._balance_aggro_distribution(enemy_id, damaged_ally, -aggro_decrease)
        
        # 전체적으로 최소 10% 보장 재조정
        self._enforce_minimum_aggro_percentage(enemy_id)
    
    def get_primary_target(self, enemy_id: str, alive_allies: List) -> Optional[str]:
        """확률 기반 타겟 선정 (어그로 비율로 확률 계산, 최소 10% 보장)"""
        if enemy_id not in self.aggro_table:
            return None
            
        alive_ally_names = [getattr(ally, 'name', str(ally)) for ally in alive_allies]
        
        # 살아있는 아군 중에서만 선택
        valid_targets = {
            ally_id: aggro for ally_id, aggro in self.aggro_table[enemy_id].items()
            if ally_id in alive_ally_names and aggro >= self.min_aggro
        }
        
        if not valid_targets:
            return None
        
        # 최소 확률 10% 보장 시스템
        ally_count = len(valid_targets)
        min_probability = 0.10  # 10%
        guaranteed_total = min_probability * ally_count  # 전체 최소 보장 확률
        
        # 원래 어그로 총합
        original_total = sum(valid_targets.values())
        
        if original_total <= 0:
            # 모든 어그로가 0이면 균등 분배
            adjusted_aggro = {ally_id: min_probability for ally_id in valid_targets.keys()}
        else:
            # 어그로 비율 계산
            aggro_ratios = {ally_id: aggro / original_total for ally_id, aggro in valid_targets.items()}
            
            # 최소 확률 보장 조정
            adjusted_aggro = {}
            remaining_probability = 1.0 - guaranteed_total
            
            for ally_id, ratio in aggro_ratios.items():
                # 기본 최소 확률 + 남은 확률의 어그로 비율만큼
                adjusted_aggro[ally_id] = min_probability + (ratio * remaining_probability)
        
        # 확률 기반 선택
        total_adjusted = sum(adjusted_aggro.values())
        rand_value = random.uniform(0, total_adjusted)
        cumulative = 0
        
        for ally_id, probability in adjusted_aggro.items():
            cumulative += probability
            if rand_value <= cumulative:
                return ally_id
        
        # 혹시 모를 경우를 위한 백업
        return list(valid_targets.keys())[-1]
    
    def get_aggro_distribution(self, enemy_id: str) -> Dict[str, float]:
        """어그로 분포 반환 (디버깅용)"""
        if enemy_id not in self.aggro_table:
            return {}
        return self.aggro_table[enemy_id].copy()
    
    def decay_aggro(self, enemy_id: str):
        """어그로 자연 감소 (매 턴 호출)"""
        if enemy_id not in self.aggro_table:
            return
            
        for ally_id in self.aggro_table[enemy_id]:
            current = self.aggro_table[enemy_id][ally_id]
            decayed = current * (1 - self.aggro_decay_rate)
            self.aggro_table[enemy_id][ally_id] = max(decayed, self.min_aggro)
    
    def reset_enemy_aggro(self, enemy_id: str):
        """특정 적의 어그로 초기화"""
        if enemy_id in self.aggro_table:
            del self.aggro_table[enemy_id]
    
    def clear_all_aggro(self):
        """모든 어그로 초기화"""
        self.aggro_table.clear()
    
    def _balance_aggro_distribution(self, enemy_id: str, target_id: str, aggro_change: float):
        """어그로 변동 시 다른 아군들의 어그로를 비례적으로 조정하여 총합 유지 + 최소 10% 보장"""
        if enemy_id not in self.aggro_table:
            return
            
        aggro_dict = self.aggro_table[enemy_id]
        other_targets = [tid for tid in aggro_dict.keys() if tid != target_id]
        
        if not other_targets or aggro_change == 0:
            return
            
        # 전체 어그로 총합 계산
        total_aggro = sum(aggro_dict.values())
        ally_count = len(aggro_dict)
        min_aggro_per_ally = total_aggro * 0.10  # 전체의 10%씩
        
        # 변동량을 다른 아군들에게 역방향으로 분배
        adjustment_per_target = -aggro_change / len(other_targets)
        
        for other_id in other_targets:
            aggro_dict[other_id] += adjustment_per_target
            
            # 최소 10% 보장
            if aggro_dict[other_id] < min_aggro_per_ally:
                shortage = min_aggro_per_ally - aggro_dict[other_id]
                aggro_dict[other_id] = min_aggro_per_ally
                
                # 부족분을 다른 아군들에게서 차감 (균등 분배)
                remaining_targets = [tid for tid in aggro_dict.keys() if tid != other_id]
                if remaining_targets:
                    reduction_per_remaining = shortage / len(remaining_targets)
                    for remaining_id in remaining_targets:
                        aggro_dict[remaining_id] = max(min_aggro_per_ally, 
                                                     aggro_dict[remaining_id] - reduction_per_remaining)
    
    def get_aggro_status(self, enemy_id: str) -> str:
        """특정 적의 어그로 상태 정보 반환 (전황 분석용) - 실제 어그로 수치 표시"""
        if enemy_id not in self.aggro_table:
            return f"{enemy_id}: 어그로 정보 없음"
            
        aggro_dict = self.aggro_table[enemy_id]
        if not aggro_dict:
            return f"{enemy_id}: 어그로 정보 없음"
            
        # 어그로 순으로 정렬 (실제 어그로 값 기준)
        sorted_aggro = sorted(aggro_dict.items(), key=lambda x: x[1], reverse=True)
        
        status_lines = [f"📊 {enemy_id} 어그로 현황 (최소 10% 보장):"]
        total_aggro = sum(aggro_dict.values())
        
        for i, (target_id, aggro_value) in enumerate(sorted_aggro):
            # 1위만 🔥 표시, 나머지는 공백
            if i == 0:
                rank_icon = "🔥"
            else:
                rank_icon = "  "  # 공백
            percentage = (aggro_value / total_aggro) * 100 if total_aggro > 0 else 0
            status_lines.append(f"  {rank_icon} {target_id}: {aggro_value:.1f} ({percentage:.1f}%)")
            
        return "\n".join(status_lines)
    
    def get_all_aggro_status(self) -> str:
        """모든 적의 어그로 상태 반환 (전황 분석용)"""
        if not self.aggro_table:
            return "📊 어그로 정보가 없습니다."
            
        status_sections = []
        for enemy_id in self.aggro_table.keys():
            status_sections.append(self.get_aggro_status(enemy_id))
            
        return "\n\n".join(status_sections)

# 글로벌 어그로 시스템 인스턴스
_aggro_system = None

def get_aggro_system() -> DynamicAggroSystem:
    """글로벌 어그로 시스템 반환"""
    global _aggro_system
    if _aggro_system is None:
        _aggro_system = DynamicAggroSystem()
    return _aggro_system

def create_aggro_event(source_name: str, action_type: str, base_value: float, 
                      aggro_type: AggroType, target_name: str = "", 
                      multiplier: float = 1.0) -> AggroEvent:
    """어그로 이벤트 생성 헬퍼 함수"""
    return AggroEvent(
        source=source_name,
        target=target_name,
        action_type=action_type,
        aggro_type=aggro_type,
        base_value=base_value,
        multiplier=multiplier
    )

# 액션별 어그로 이벤트 생성 헬퍼들 (HP 비율 기반)
def create_damage_aggro(attacker_name: str, damage: float, target_max_hp: float) -> AggroEvent:
    """공격 어그로 이벤트 (HP 비율 기반)"""
    hp_ratio = min(damage / max(target_max_hp, 1), 1.0)  # 최대 100%
    return create_aggro_event(attacker_name, "attack", hp_ratio, AggroType.DAMAGE)

def create_healing_aggro(healer_name: str, heal_amount: float, target_max_hp: float) -> AggroEvent:
    """힐링 어그로 이벤트 (HP 비율 기반)"""
    hp_ratio = min(heal_amount / max(target_max_hp, 1), 1.0)  # 최대 100%
    return create_aggro_event(healer_name, "heal", hp_ratio, AggroType.HEALING)

def create_taunt_aggro(tank_name: str, taunt_power: float = 0.5) -> AggroEvent:
    """도발 어그로 이벤트 (고정 비율)"""
    return create_aggro_event(tank_name, "taunt", taunt_power, AggroType.TAUNT)

def create_debuff_aggro(caster_name: str, debuff_severity: float = 0.3) -> AggroEvent:
    """디버프 어그로 이벤트 (고정 비율)"""
    return create_aggro_event(caster_name, "debuff", debuff_severity, AggroType.DEBUFF)

def create_damage_taken_event(aggro_system, enemy_id: str, damaged_ally: str, 
                             damage_taken: float, ally_max_hp: float):
    """아군이 피해를 받았을 때 어그로 감소 처리"""
    hp_ratio_lost = min(damage_taken / max(ally_max_hp, 1), 1.0)
    aggro_system.add_damage_taken_event(enemy_id, damaged_ally, hp_ratio_lost)

if __name__ == "__main__":
    # 테스트 코드 (HP 비율 기반)
    aggro_system = get_aggro_system()
    
    # 가상의 캐릭터들
    class TestChar:
        def __init__(self, name, char_class, max_hp=1000):
            self.name = name
            self.character_class = char_class
            self.max_hp = max_hp
    
    allies = [
        TestChar("탱커", "전사", 1200),
        TestChar("힐러", "신관", 800), 
        TestChar("딜러", "궁수", 900),
        TestChar("서포터", "바드", 850)
    ]
    
    # 적 초기화
    aggro_system.initialize_enemy("고블린", allies)
    
    # HP 비율 기반 이벤트 추가
    print("=== HP 비율 기반 어그로 테스트 ===")
    
    # 딜러가 적에게 150 데미지 (적 HP 1000 기준)
    aggro_system.add_aggro_event("고블린", create_damage_aggro("딜러", 150, 1000))
    print("딜러가 적에게 150 데미지 (15% HP)")
    
    # 힐러가 탱커를 100 회복 (탱커 HP 1200 기준)  
    aggro_system.add_aggro_event("고블린", create_healing_aggro("힐러", 100, 1200))
    print("힐러가 탱커를 100 회복 (8.3% HP)")
    
    # 탱커가 도발
    aggro_system.add_aggro_event("고블린", create_taunt_aggro("탱커", 0.5))
    print("탱커가 도발 (50% 비율)")
    
    # 딜러가 피해를 받음
    create_damage_taken_event(aggro_system, "고블린", "딜러", 200, 900)
    print("딜러가 200 데미지를 받음 (22% HP 손실)")
    
    # 타겟 선정
    target = aggro_system.get_primary_target("고블린", allies)
    print(f"\n🎯 고블린의 주요 타겟: {target}")
    
    # 어그로 상태 확인
    print(f"\n{aggro_system.get_aggro_status('고블린')}")
    
    # 총합 확인
    distribution = aggro_system.get_aggro_distribution("고블린")
    total = sum(distribution.values())
    print(f"\n총 어그로: {total:.1f}")
    print("개별 어그로:")
    for ally, aggro in distribution.items():
        print(f"   {ally}: {aggro:.1f}")
