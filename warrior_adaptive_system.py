#!/usr/bin/env python3
"""
🛡️ 전사 적응형 전투 시스템
상황에 따라 자동으로 전투 스타일이 변화하는 밸런스형 시스템
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

class WarriorStance(Enum):
    """전사 전투 자세"""
    DEFENSIVE = "defensive"     # 방어형: HP 낮을 때, 강한 적 상대
    AGGRESSIVE = "aggressive"   # 공격형: HP 높을 때, 약한 적 상대
    BALANCED = "balanced"       # 균형형: 기본 상태
    BERSERKER = "berserker"     # 광전사: 위급 상황 (HP 25% 이하)
    GUARDIAN = "guardian"       # 수호자: 파티원 보호 필요 시

class EnemyAnalysis:
    """적 분석 결과"""
    PHYSICAL_HEAVY = "physical_heavy"    # 물리 공격 위주
    MAGIC_HEAVY = "magic_heavy"         # 마법 공격 위주
    BALANCED_ENEMY = "balanced_enemy"    # 균형형 적
    WEAK_ENEMY = "weak_enemy"           # 약한 적
    STRONG_ENEMY = "strong_enemy"       # 강한 적
    BOSS_ENEMY = "boss_enemy"           # 보스급 적

@dataclass
class AdaptiveStats:
    """적응형 스탯 보정"""
    physical_attack_bonus: float = 0.0
    magic_attack_bonus: float = 0.0
    physical_defense_bonus: float = 0.0
    magic_defense_bonus: float = 0.0
    speed_bonus: float = 0.0
    critical_rate_bonus: float = 0.0
    skill_power_bonus: float = 0.0
    stance_name: str = "균형"

class WarriorAdaptiveSystem:
    """전사 적응형 시스템"""
    
    def __init__(self):
        self.current_stance = WarriorStance.BALANCED
        self.stance_duration = 0  # 자세 유지 턴 수
        self.adaptation_history = []  # 적응 이력
        
        # 자세별 스탯 보정
        self.stance_bonuses = {
            WarriorStance.DEFENSIVE: AdaptiveStats(
                physical_defense_bonus=0.5,
                magic_defense_bonus=0.3,
                speed_bonus=-0.2,
                skill_power_bonus=0.2,
                stance_name="🛡️ 방어형"
            ),
            WarriorStance.AGGRESSIVE: AdaptiveStats(
                physical_attack_bonus=0.4,
                critical_rate_bonus=0.25,
                speed_bonus=0.3,
                physical_defense_bonus=-0.1,
                stance_name="⚔️ 공격형"
            ),
            WarriorStance.BALANCED: AdaptiveStats(
                physical_attack_bonus=0.1,
                physical_defense_bonus=0.1,
                magic_defense_bonus=0.1,
                stance_name="⚖️ 균형형"
            ),
            WarriorStance.BERSERKER: AdaptiveStats(
                physical_attack_bonus=0.8,
                critical_rate_bonus=0.5,
                speed_bonus=0.5,
                physical_defense_bonus=-0.3,
                magic_defense_bonus=-0.3,
                stance_name="💀 광전사"
            ),
            WarriorStance.GUARDIAN: AdaptiveStats(
                physical_defense_bonus=0.3,
                magic_defense_bonus=0.4,
                skill_power_bonus=0.3,
                speed_bonus=0.1,
                stance_name="🛡️ 수호자"
            )
        }
    
    def analyze_battle_situation(self, warrior, allies: List, enemies: List) -> Dict:
        """전투 상황 분석"""
        situation = {
            'warrior_hp_ratio': warrior.current_hp / warrior.max_hp,
            'party_avg_hp': sum(ally.current_hp / ally.max_hp for ally in allies if ally.is_alive) / len([a for a in allies if a.is_alive]),
            'critical_allies': len([ally for ally in allies if ally.is_alive and ally.current_hp / ally.max_hp < 0.3]),
            'enemy_count': len([enemy for enemy in enemies if enemy.is_alive]),
            'enemy_analysis': self._analyze_enemies(enemies),
            'threat_level': self._calculate_threat_level(warrior, enemies)
        }
        
        return situation
    
    def _analyze_enemies(self, enemies: List) -> Dict:
        """적들 분석"""
        if not enemies:
            return {'type': EnemyAnalysis.WEAK_ENEMY, 'total_power': 0}
        
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return {'type': EnemyAnalysis.WEAK_ENEMY, 'total_power': 0}
        
        # 적들의 공격 유형 분석
        total_physical = sum(getattr(e, 'physical_attack', 0) for e in alive_enemies)
        total_magic = sum(getattr(e, 'magic_attack', 0) for e in alive_enemies)
        total_power = total_physical + total_magic
        
        # 적 유형 결정
        if total_power > 200:  # 강한 적
            enemy_type = EnemyAnalysis.BOSS_ENEMY if len(alive_enemies) == 1 else EnemyAnalysis.STRONG_ENEMY
        elif total_power > 100:
            enemy_type = EnemyAnalysis.BALANCED_ENEMY
        else:
            enemy_type = EnemyAnalysis.WEAK_ENEMY
        
        # 공격 유형 분석
        if total_magic > total_physical * 1.5:
            attack_preference = EnemyAnalysis.MAGIC_HEAVY
        elif total_physical > total_magic * 1.5:
            attack_preference = EnemyAnalysis.PHYSICAL_HEAVY
        else:
            attack_preference = EnemyAnalysis.BALANCED_ENEMY
        
        return {
            'type': enemy_type,
            'attack_preference': attack_preference,
            'total_power': total_power,
            'physical_ratio': total_physical / max(1, total_power),
            'magic_ratio': total_magic / max(1, total_power)
        }
    
    def _calculate_threat_level(self, warrior, enemies: List) -> float:
        """위협 수준 계산 (0.0 ~ 3.0)"""
        if not enemies:
            return 0.0
        
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return 0.0
        
        enemy_power = sum(getattr(e, 'physical_attack', 0) + getattr(e, 'magic_attack', 0) for e in alive_enemies)
        warrior_defense = getattr(warrior, 'physical_defense', 0) + getattr(warrior, 'magic_defense', 0)
        
        threat_ratio = enemy_power / max(1, warrior_defense)
        return min(3.0, threat_ratio)
    
    def adapt_stance(self, warrior, allies: List, enemies: List) -> Tuple[WarriorStance, AdaptiveStats]:
        """상황에 따른 자세 적응"""
        situation = self.analyze_battle_situation(warrior, allies, enemies)
        new_stance = self._determine_optimal_stance(situation)
        
        # 자세 변경 시 메시지 출력
        if new_stance != self.current_stance:
            old_stance_name = self.stance_bonuses[self.current_stance].stance_name
            new_stance_name = self.stance_bonuses[new_stance].stance_name
            print(f"🔄 {warrior.name}의 전투 자세 변경: {old_stance_name} → {new_stance_name}")
            self.stance_duration = 0
            self.adaptation_history.append({
                'turn': len(self.adaptation_history) + 1,
                'old_stance': self.current_stance,
                'new_stance': new_stance,
                'reason': self._get_adaptation_reason(situation, new_stance)
            })
        else:
            self.stance_duration += 1
        
        self.current_stance = new_stance
        return new_stance, self.stance_bonuses[new_stance]
    
    def _determine_optimal_stance(self, situation: Dict) -> WarriorStance:
        """최적 자세 결정"""
        hp_ratio = situation['warrior_hp_ratio']
        threat_level = situation['threat_level']
        critical_allies = situation['critical_allies']
        enemy_analysis = situation['enemy_analysis']
        
        # 1. 위급 상황 (HP 25% 이하) - 광전사 모드
        if hp_ratio <= 0.25:
            return WarriorStance.BERSERKER
        
        # 2. 파티원 보호 필요 - 수호자 모드
        if critical_allies >= 2:
            return WarriorStance.GUARDIAN
        
        # 3. 높은 위협 상황 - 방어 모드
        if threat_level >= 2.0 or hp_ratio <= 0.4:
            return WarriorStance.DEFENSIVE
        
        # 4. 약한 적 상대 - 공격 모드
        if (enemy_analysis['type'] == EnemyAnalysis.WEAK_ENEMY and hp_ratio >= 0.7) or \
           (hp_ratio >= 0.8 and threat_level <= 1.0):
            return WarriorStance.AGGRESSIVE
        
        # 5. 기본 상황 - 균형 모드
        return WarriorStance.BALANCED
    
    def _get_adaptation_reason(self, situation: Dict, new_stance: WarriorStance) -> str:
        """적응 이유 설명"""
        reasons = {
            WarriorStance.BERSERKER: "위급 상황! 최후의 발악!",
            WarriorStance.GUARDIAN: "파티원 보호가 필요함",
            WarriorStance.DEFENSIVE: "강한 적 상대, 방어 우선",
            WarriorStance.AGGRESSIVE: "약한 적 상대, 빠른 처리",
            WarriorStance.BALANCED: "안정적인 균형 유지"
        }
        return reasons.get(new_stance, "상황 적응")
    
    def get_stance_display(self) -> str:
        """현재 자세 표시"""
        stance_info = self.stance_bonuses[self.current_stance]
        duration_display = f"({self.stance_duration}턴)" if self.stance_duration > 0 else ""
        return f"{stance_info.stance_name} {duration_display}"
    
    def apply_stance_effects(self, warrior, base_stats: Dict) -> Dict:
        """자세 효과 적용"""
        stance_bonus = self.stance_bonuses[self.current_stance]
        modified_stats = base_stats.copy()
        
        # 스탯 보정 적용
        modified_stats['physical_attack'] = int(base_stats.get('physical_attack', 0) * (1 + stance_bonus.physical_attack_bonus))
        modified_stats['magic_attack'] = int(base_stats.get('magic_attack', 0) * (1 + stance_bonus.magic_attack_bonus))
        modified_stats['physical_defense'] = int(base_stats.get('physical_defense', 0) * (1 + stance_bonus.physical_defense_bonus))
        modified_stats['magic_defense'] = int(base_stats.get('magic_defense', 0) * (1 + stance_bonus.magic_defense_bonus))
        modified_stats['speed'] = int(base_stats.get('speed', 0) * (1 + stance_bonus.speed_bonus))
        
        return modified_stats
    
    def get_skill_recommendations(self, warrior, enemies: List) -> List[str]:
        """자세에 따른 스킬 추천"""
        recommendations = {
            WarriorStance.DEFENSIVE: ["방패 강타", "철벽 방어", "반격"],
            WarriorStance.AGGRESSIVE: ["파괴의 일격", "연속 베기", "돌진"],
            WarriorStance.BALANCED: ["균형 잡힌 공격", "적응형 베기"],
            WarriorStance.BERSERKER: ["광란의 난타", "최후의 일격", "분노 폭발"],
            WarriorStance.GUARDIAN: ["보호 의지", "수호 방패", "치유 오라"]
        }
        
        return recommendations.get(self.current_stance, ["기본 공격"])


def demo_warrior_adaptive_system():
    """전사 적응형 시스템 데모"""
    print("🛡️ 전사 적응형 전투 시스템 데모")
    print("=" * 60)
    
    class MockCharacter:
        def __init__(self, name, hp=100, max_hp=100, physical_attack=50, magic_attack=10):
            self.name = name
            self.current_hp = hp
            self.max_hp = max_hp
            self.physical_attack = physical_attack
            self.magic_attack = magic_attack
            self.physical_defense = 30
            self.magic_defense = 20
            self.speed = 50
            self.is_alive = hp > 0
    
    # 테스트 캐릭터들
    warrior = MockCharacter("용감한 전사", 120, 150)
    ally1 = MockCharacter("궁수", 80, 100)
    ally2 = MockCharacter("마법사", 20, 80)  # 위급 상태
    
    # 다양한 적 시나리오
    scenarios = [
        {
            "name": "약한 고블린들",
            "enemies": [MockCharacter("고블린1", 30, 30, 20, 5), MockCharacter("고블린2", 25, 30, 18, 3)]
        },
        {
            "name": "강한 오크 전사",
            "enemies": [MockCharacter("오크 전사", 200, 200, 80, 20)]
        },
        {
            "name": "마법사 적들",
            "enemies": [MockCharacter("어둠 마법사", 120, 120, 20, 90), MockCharacter("불 마법사", 100, 100, 15, 85)]
        },
        {
            "name": "보스급 드래곤",
            "enemies": [MockCharacter("고대 드래곤", 500, 500, 120, 100)]
        }
    ]
    
    warrior_system = WarriorAdaptiveSystem()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 시나리오 {i}: {scenario['name']}")
        print("-" * 40)
        
        # 전사 HP 상태 변화 시뮬레이션
        hp_states = [150, 120, 80, 30]  # 건강 → 부상 → 위험 → 위급 (25% 이하)
        
        for hp in hp_states:
            warrior.current_hp = hp
            
            stance, stats = warrior_system.adapt_stance(warrior, [ally1, ally2], scenario['enemies'])
            
            print(f"  전사 HP: {warrior.current_hp}/{warrior.max_hp} ({warrior.current_hp/warrior.max_hp*100:.0f}%)")
            print(f"  현재 자세: {warrior_system.get_stance_display()}")
            print(f"  추천 스킬: {', '.join(warrior_system.get_skill_recommendations(warrior, scenario['enemies']))}")
            print()
    
    print("🎯 적응형 시스템 특징:")
    print("• HP 상태에 따른 자동 자세 변경")
    print("• 적의 유형 분석 후 최적 대응")
    print("• 파티원 상태 고려한 보호 모드")
    print("• 위급 상황 시 광전사 모드 발동")

if __name__ == "__main__":
    demo_warrior_adaptive_system()
