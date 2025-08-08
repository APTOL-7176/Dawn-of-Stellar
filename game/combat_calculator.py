#!/usr/bin/env python3
"""
전투 계산 시스템 - 크리티컬, 명중률, 회피율
"""

import random
from typing import Dict, Tuple, Optional
from enum import Enum


class CriticalType(Enum):
    """크리티컬 타입"""
    NORMAL = "일반"
    GREAT = "크리티컬"
    PERFECT = "퍼펙트"
    LEGENDARY = "레전더리"


class AccuracySystem:
    """명중률 시스템"""
    
    @staticmethod
    def calculate_hit_chance(attacker_accuracy: int, defender_evasion: int) -> float:
        """명중률 계산: 공격자 명중률 / 수비자 회피율"""
        # 기본 공식: 명중률 / 회피율
        base_chance = attacker_accuracy / max(defender_evasion, 1)
        
        # 25% ~ 100% 범위로 제한
        hit_chance = max(0.25, min(1.0, base_chance))
        
        return hit_chance
    
    @staticmethod
    def is_hit_successful(attacker_accuracy: int, defender_evasion: int) -> bool:
        """공격이 명중했는지 판정"""
        hit_chance = AccuracySystem.calculate_hit_chance(attacker_accuracy, defender_evasion)
        return random.random() < hit_chance


class CriticalSystem:
    """크리티컬 시스템"""
    
    def __init__(self):
        # 직업별 기본 크리티컬 확률 (평균 10%)
        self.job_critical_rates = {
            "전사": 8,     # 안정적인 물리 딜러
            "팔라딘": 6,   # 탱커, 낮은 크리율
            "다크나이트": 12, # 고위험 고수익
            "궁수": 15,    # 정확성과 크리티컬
            "격투가": 10,  # 균형잡힌 물리 딜러
            "도적": 18,    # 높은 크리티컬
            "닌자": 16,    # 어쌔신 계열
            "흑마법사": 7, # 마법은 크리티컬 낮음
            "백마법사": 4, # 힐러, 매우 낮음
            "적마법사": 9, # 마법 딜러
            "소환사": 8,   # 소환 특화
            "청마법사": 11, # 다양한 스킬
            "시공마법사": 13, # 특수 마법
            "연금술사": 5, # 서포터
            "음유시인": 7, # 버퍼
            "무용가": 14,  # 민첩성 기반
            "기계공": 10,  # 기술 기반
            "검성": 20,    # 검술 마스터
            "마검사": 15,  # 마법검사
            "성기사": 8,   # 성스러운 기사
            "암흑기사": 14, # 어둠의 힘
            "드래곤나이트": 12, # 용의 힘
            "바이킹": 11,  # 해적
            "사무라이": 17, # 일격필살
            "몽크": 13,    # 무술가
            "광전사": 16,  # 분노의 힘
            "마도사": 6,   # 마법 연구자
            "현자": 9      # 지혜로운 마법사
        }
        
        # 크리티컬 단계별 배율
        self.critical_multipliers = {
            CriticalType.NORMAL: 1.0,      # 일반 공격
            CriticalType.GREAT: 1.5,       # 크리티컬
            CriticalType.PERFECT: 2.0,     # 퍼펙트
            CriticalType.LEGENDARY: 3.0    # 레전더리
        }
        
        # 크리티컬 발생 확률 (기본 크리티컬 확률 기준)
        self.critical_thresholds = {
            CriticalType.GREAT: 1.0,       # 기본 크리티컬 확률
            CriticalType.PERFECT: 0.1,     # 기본 확률의 10%
            CriticalType.LEGENDARY: 0.01   # 기본 확률의 1%
        }
    
    def get_base_critical_rate(self, job_name: str) -> int:
        """직업별 기본 크리티컬 확률"""
        return self.job_critical_rates.get(job_name, 10)
    
    def calculate_total_critical_rate(self, character) -> int:
        """총 크리티컬 확률 계산"""
        # 기본 크리티컬 (직업)
        base_rate = self.get_base_critical_rate(character.character_class.value)
        
        # 캐릭터 크리티컬 스탯
        stat_rate = getattr(character, 'critical', 0)
        
        # 장비 보너스 (임시)
        equipment_bonus = 0
        if hasattr(character, 'equipment'):
            for item in character.equipment.values():
                if item and hasattr(item, 'critical_bonus'):
                    equipment_bonus += item.critical_bonus
        
        # 버프 보너스
        buff_bonus = 0
        if hasattr(character, 'active_statuses'):
            for status in character.active_statuses:
                if hasattr(status, 'critical_bonus'):
                    buff_bonus += status.critical_bonus
        
        # 행운 보너스 (행운 10당 크리티컬 1% 추가)
        luck_bonus = getattr(character, 'luck', 0) // 10
        
        total_rate = base_rate + stat_rate + equipment_bonus + buff_bonus + luck_bonus
        
        # 최대 50%로 제한
        return min(50, max(0, total_rate))
    
    def determine_critical_type(self, character, target=None) -> CriticalType:
        """크리티컬 타입 결정"""
        base_critical_rate = self.calculate_total_critical_rate(character)
        
        # 특수 조건 보너스
        bonus_multiplier = 1.0
        
        # 배후 공격 보너스
        if hasattr(character, 'is_behind_target') and character.is_behind_target:
            bonus_multiplier *= 1.5
        
        # 약점 공격 보너스
        if target and hasattr(target, 'weakness_hit') and target.weakness_hit:
            bonus_multiplier *= 1.3
        
        # 낮은 HP일 때 보너스
        if hasattr(character, 'current_hp') and hasattr(character, 'max_hp'):
            if character.current_hp < character.max_hp * 0.3:
                bonus_multiplier *= 1.2
        
        final_rate = base_critical_rate * bonus_multiplier
        
        # 레전더리 크리티컬 판정 (매우 희귀)
        legendary_chance = final_rate * self.critical_thresholds[CriticalType.LEGENDARY] / 100
        if random.random() < legendary_chance:
            return CriticalType.LEGENDARY
        
        # 퍼펙트 크리티컬 판정
        perfect_chance = final_rate * self.critical_thresholds[CriticalType.PERFECT] / 100
        if random.random() < perfect_chance:
            return CriticalType.PERFECT
        
        # 일반 크리티컬 판정
        great_chance = final_rate / 100
        if random.random() < great_chance:
            return CriticalType.GREAT
        
        return CriticalType.NORMAL
    
    def apply_critical_damage(self, base_damage: int, critical_type: CriticalType) -> Tuple[int, str]:
        """크리티컬 데미지 적용"""
        multiplier = self.critical_multipliers[critical_type]
        final_damage = int(base_damage * multiplier)
        
        # 크리티컬 메시지
        messages = {
            CriticalType.NORMAL: "",
            CriticalType.GREAT: "💥 크리티컬!",
            CriticalType.PERFECT: "🌟 퍼펙트 크리티컬!",
            CriticalType.LEGENDARY: "⭐ 레전더리 크리티컬!!!"
        }
        
        return final_damage, messages[critical_type]


class CombatCalculator:
    """전투 계산 통합 시스템"""
    
    def __init__(self):
        self.accuracy_system = AccuracySystem()
        self.critical_system = CriticalSystem()
    
    def calculate_attack_result(self, attacker, defender, base_damage: int, 
                              attack_element=None, defend_element=None) -> Dict:
        """공격 결과 종합 계산"""
        result = {
            "hit": False,
            "critical_type": CriticalType.NORMAL,
            "final_damage": 0,
            "messages": []
        }
        
        # 1. 명중 판정
        attacker_acc = getattr(attacker, 'accuracy', 70)
        defender_eva = getattr(defender, 'evasion', 30)
        
        result["hit"] = self.accuracy_system.is_hit_successful(attacker_acc, defender_eva)
        
        if not result["hit"]:
            result["messages"].append("빗나감!")
            return result
        
        # 2. 크리티컬 판정
        result["critical_type"] = self.critical_system.determine_critical_type(attacker, defender)
        
        # 3. 데미지 계산
        damage = base_damage
        
        # 크리티컬 적용
        damage, crit_msg = self.critical_system.apply_critical_damage(damage, result["critical_type"])
        if crit_msg:
            result["messages"].append(crit_msg)
        
        # 원소 상성 적용 (있다면)
        if attack_element and defend_element:
            try:
                from .elemental_system import calculate_elemental_damage
                damage = calculate_elemental_damage(damage, attack_element, defend_element)
            except ImportError:
                pass
        
        # 방어력 적용 (기본 공식)
        defender_def = getattr(defender, 'defense', 10)
        damage = max(1, damage - defender_def // 2)  # 최소 1 데미지
        
        result["final_damage"] = damage
        
        return result
    
    def get_hit_chance_display(self, attacker_accuracy: int, defender_evasion: int) -> str:
        """명중률 표시용 문자열"""
        chance = self.accuracy_system.calculate_hit_chance(attacker_accuracy, defender_evasion)
        percentage = int(chance * 100)
        
        if percentage >= 95:
            return f"🎯 {percentage}% (확실히 명중)"
        elif percentage >= 80:
            return f"🎯 {percentage}% (높은 명중률)"
        elif percentage >= 60:
            return f"🎯 {percentage}% (보통 명중률)"
        elif percentage >= 40:
            return f"⚠️ {percentage}% (낮은 명중률)"
        else:
            return f"❌ {percentage}% (매우 낮음)"
    
    def get_critical_chance_display(self, character) -> str:
        """크리티컬 확률 표시용 문자열"""
        crit_rate = self.critical_system.calculate_total_critical_rate(character)
        
        if crit_rate >= 30:
            return f"✨ {crit_rate}% (매우 높음)"
        elif crit_rate >= 20:
            return f"✨ {crit_rate}% (높음)"
        elif crit_rate >= 10:
            return f"✨ {crit_rate}% (보통)"
        elif crit_rate >= 5:
            return f"✨ {crit_rate}% (낮음)"
        else:
            return f"✨ {crit_rate}% (매우 낮음)"


# 전역 전투 계산기 인스턴스
_combat_calculator = None

def get_combat_calculator() -> CombatCalculator:
    """전투 계산기 싱글톤 반환"""
    global _combat_calculator
    if _combat_calculator is None:
        _combat_calculator = CombatCalculator()
    return _combat_calculator

def calculate_hit_chance(attacker_accuracy: int, defender_evasion: int) -> float:
    """명중률 계산 (간편 함수)"""
    return AccuracySystem.calculate_hit_chance(attacker_accuracy, defender_evasion)

def is_attack_hit(attacker_accuracy: int, defender_evasion: int) -> bool:
    """공격 명중 판정 (간편 함수)"""
    return AccuracySystem.is_hit_successful(attacker_accuracy, defender_evasion)

def get_critical_rate(character) -> int:
    """캐릭터 크리티컬 확률 반환 (간편 함수)"""
    calculator = get_combat_calculator()
    return calculator.critical_system.calculate_total_critical_rate(character)

def determine_critical(character, target=None) -> CriticalType:
    """크리티컬 타입 결정 (간편 함수)"""
    calculator = get_combat_calculator()
    return calculator.critical_system.determine_critical_type(character, target)


if __name__ == "__main__":
    # 테스트용 캐릭터 클래스
    class TestCharacter:
        def __init__(self, name, job_name, accuracy=70, evasion=30, critical=5, luck=20):
            self.name = name
            self.job_name = job_name
            self.accuracy = accuracy
            self.evasion = evasion
            self.critical = critical
            self.luck = luck
            self.current_hp = 100
            self.max_hp = 100
    
    # 테스트
    print("🧪 전투 계산 시스템 테스트")
    print("=" * 50)
    
    # 캐릭터 생성
    warrior = TestCharacter("전사", "전사", accuracy=85, evasion=25, critical=10, luck=15)
    rogue = TestCharacter("도적", "도적", accuracy=95, evasion=60, critical=15, luck=25)
    
    calculator = get_combat_calculator()
    
    # 명중률 테스트
    print("\n🎯 명중률 테스트:")
    hit_chance = calculate_hit_chance(warrior.accuracy, rogue.evasion)
    print(f"전사(명중85) vs 도적(회피60): {calculator.get_hit_chance_display(warrior.accuracy, rogue.evasion)}")
    
    # 크리티컬 테스트
    print("\n✨ 크리티컬 테스트:")
    warrior_crit = get_critical_rate(warrior)
    rogue_crit = get_critical_rate(rogue)
    print(f"전사 크리티컬: {calculator.get_critical_chance_display(warrior)}")
    print(f"도적 크리티컬: {calculator.get_critical_chance_display(rogue)}")
    
    # 전투 시뮬레이션
    print("\n⚔️ 전투 시뮬레이션 (10회):")
    for i in range(10):
        result = calculator.calculate_attack_result(warrior, rogue, 100)
        if result["hit"]:
            crit_msg = " ".join(result["messages"])
            print(f"{i+1}. 명중 - 데미지: {result['final_damage']} {crit_msg}")
        else:
            print(f"{i+1}. 빗나감!")
