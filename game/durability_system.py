#!/usr/bin/env python3
"""
내구도 시스템 - 장비 손상과 수리 관리
"""

import random
from typing import Dict, List, Optional, Any
from enum import Enum

class DurabilityCondition(Enum):
    """내구도 상태"""
    PERFECT = "완벽"       # 90-100%
    EXCELLENT = "우수"     # 80-89%
    GOOD = "양호"         # 60-79%
    FAIR = "보통"         # 40-59%
    POOR = "나쁨"         # 20-39%
    CRITICAL = "위험"     # 1-19%
    BROKEN = "파괴됨"     # 0%

class DurabilitySystem:
    """내구도 관리 시스템"""
    
    # 내구도가 감소하는 상황들 (30% 감소 조정)
    DURABILITY_LOSS_CONDITIONS = {
        "combat_hit": {
            "chance": 0.53,    # 53% 확률 (75% * 0.7)
            "amount": 1,       # 1 포인트 감소
            "description": "전투 중 공격받음"
        },
        "combat_block": {
            "chance": 0.49,    # 49% 확률 (70% * 0.7)
            "amount": 1,       # 1 포인트 감소
            "description": "공격 방어"
        },
        "critical_hit_taken": {
            "chance": 0.60,    # 60% 확률 (85% * 0.7)
            "amount": 2,       # 2 포인트 감소
            "description": "치명타 피해받음"
        },
        "weapon_use": {
            "chance": 0.49,    # 49% 확률 (70% * 0.7)
            "amount": 1,       # 1 포인트 감소
            "description": "무기 사용"
        },
        "spell_casting": {
            "chance": 0.49,    # 49% 확률 (70% * 0.7)
            "amount": 1,       # 1 포인트 감소
            "description": "마법 시전"
        },
        "environmental_damage": {
            "chance": 0.35,    # 35% 확률 (유지)
            "amount": 2,       # 2 포인트 감소
            "description": "환경 피해 (독, 화염 등)"
        },
        "trap_damage": {
            "chance": 0.60,    # 60% 확률 (유지)
            "amount": 3,       # 3 포인트 감소
            "description": "함정 피해"
        },
        "corrosion_damage": {
            "chance": 0.56,    # 56% 확률 (80% * 0.7)
            "amount": 3,       # 3 포인트 감소
            "description": "부식 효과"
        },
        "acid_damage": {
            "chance": 0.63,    # 63% 확률 (90% * 0.7)
            "amount": 4,       # 4 포인트 감소
            "description": "산성 피해"
        },
        "overuse": {
            "chance": 0.15,    # 15% 확률 (새로운 과사용)
            "amount": 1,       # 1 포인트 감소
            "description": "장비 과사용"
        }
    }
    
    @staticmethod
    def check_durability_loss(equipment, condition: str, protection_active: bool = False) -> bool:
        """내구도 감소 체크 - Item 클래스와 호환"""
        # Item 클래스와 legacy equipment 모두 지원
        if not equipment:
            return False
            
        # Item 클래스인 경우
        if hasattr(equipment, 'max_durability') and equipment.max_durability == 0:
            return False  # 소모품은 내구도 없음
            
        # 내구도 속성 확인
        if not (hasattr(equipment, 'current_durability') and hasattr(equipment, 'max_durability')):
            return False
        
        # 보호 효과가 활성화되어 있으면 내구도 감소 방지
        if protection_active or (hasattr(equipment, 'protection_turns') and equipment.protection_turns > 0):
            if hasattr(equipment, 'protection_turns'):
                equipment.protection_turns = max(0, equipment.protection_turns - 1)
            return False
        
        # 이미 파괴된 장비는 더 이상 감소하지 않음
        if equipment.current_durability <= 0:
            if hasattr(equipment, 'is_broken'):
                equipment.is_broken = True
            return False
        
        condition_data = DurabilitySystem.DURABILITY_LOSS_CONDITIONS.get(condition)
        if not condition_data:
            return False
        
        # 확률 체크
        if random.random() > condition_data["chance"]:
            return False
        
        # 내구도 감소
        damage_amount = condition_data["amount"]
        
        # 고급 장비일수록 내구도가 더 많이 감소 (유지보수가 어려움)
        if hasattr(equipment, 'rarity'):
            rarity_penalty = {
                "일반": 1.0,      # 그대로
                "고급": 1.2,      # 20% 증가
                "희귀": 1.4,      # 40% 증가
                "영웅": 1.6,      # 60% 증가
                "전설": 1.8,      # 80% 증가
                "신화": 2.0,      # 100% 증가
                "유니크": 2.2     # 120% 증가
            }
            
            # ItemRarity enum과 문자열 모두 지원
            if hasattr(equipment.rarity, 'value'):
                rarity_str = equipment.rarity.value
            elif hasattr(equipment.rarity, 'name'):
                rarity_str = equipment.rarity.name
            else:
                rarity_str = str(equipment.rarity)
            
            multiplier = rarity_penalty.get(rarity_str, 1.0)
            damage_amount = max(1, int(damage_amount * multiplier))
        
        # Item 클래스의 damage_durability 메서드 사용 (있으면)
        if hasattr(equipment, 'damage_durability'):
            return equipment.damage_durability(damage_amount)
        else:
            # legacy 방식
            equipment.current_durability = max(0, equipment.current_durability - damage_amount)
            
            # 내구도가 0이 되면 파괴 상태로 설정
            if equipment.current_durability <= 0 and hasattr(equipment, 'is_broken'):
                equipment.is_broken = True
            
            return True
    
    @staticmethod
    def get_durability_condition(equipment) -> DurabilityCondition:
        """내구도 상태 반환"""
        if not equipment or not hasattr(equipment, 'current_durability'):
            return DurabilityCondition.BROKEN
        
        if equipment.current_durability <= 0:
            return DurabilityCondition.BROKEN
        
        percentage = (equipment.current_durability / equipment.max_durability) * 100
        
        if percentage >= 90:
            return DurabilityCondition.PERFECT
        elif percentage >= 80:
            return DurabilityCondition.EXCELLENT
        elif percentage >= 60:
            return DurabilityCondition.GOOD
        elif percentage >= 40:
            return DurabilityCondition.FAIR
        elif percentage >= 20:
            return DurabilityCondition.POOR
        elif percentage > 0:
            return DurabilityCondition.CRITICAL
        else:
            return DurabilityCondition.BROKEN
    
    @staticmethod
    def get_durability_color(condition: DurabilityCondition) -> str:
        """내구도 상태에 따른 색상 코드 반환"""
        colors = {
            DurabilityCondition.PERFECT: '\033[92m',    # 밝은 녹색
            DurabilityCondition.EXCELLENT: '\033[32m',  # 녹색
            DurabilityCondition.GOOD: '\033[93m',       # 노란색
            DurabilityCondition.FAIR: '\033[33m',       # 주황색
            DurabilityCondition.POOR: '\033[31m',       # 빨간색
            DurabilityCondition.CRITICAL: '\033[91m',   # 밝은 빨간색
            DurabilityCondition.BROKEN: '\033[90m'      # 회색
        }
        return colors.get(condition, '\033[0m')
    
    @staticmethod
    def apply_durability_effects(equipment) -> Dict[str, float]:
        """내구도에 따른 성능 감소 효과 계산"""
        if not equipment or not hasattr(equipment, 'current_durability'):
            return {}
        
        if equipment.current_durability <= 0:
            # 파괴된 장비는 모든 효과 0
            return {"effectiveness": 0.0}
        
        percentage = (equipment.current_durability / equipment.max_durability) * 100
        
        # 내구도에 따른 효과 감소
        if percentage >= 80:
            effectiveness = 1.0      # 100% 효과
        elif percentage >= 60:
            effectiveness = 0.9      # 90% 효과
        elif percentage >= 40:
            effectiveness = 0.8      # 80% 효과
        elif percentage >= 20:
            effectiveness = 0.65     # 65% 효과
        elif percentage > 0:
            effectiveness = 0.5      # 50% 효과 (위험 상태)
        else:
            effectiveness = 0.0      # 0% 효과 (파괴됨)
        
        return {"effectiveness": effectiveness}
    
    @staticmethod
    def repair_equipment(equipment, repair_amount: int) -> int:
        """장비 수리 - 실제 수리된 양 반환"""
        if not equipment or not hasattr(equipment, 'current_durability'):
            return 0
        
        old_durability = equipment.current_durability
        equipment.current_durability = min(equipment.max_durability, 
                                         equipment.current_durability + repair_amount)
        
        # 파괴 상태 해제
        if equipment.current_durability > 0:
            equipment.is_broken = False
        
        return equipment.current_durability - old_durability
    
    @staticmethod
    def enhance_max_durability(equipment, enhancement_amount: int, temporary: bool = True):
        """최대 내구도 강화"""
        if not equipment or not hasattr(equipment, 'max_durability'):
            return
        
        if temporary:
            # 임시 강화
            if not hasattr(equipment, 'temp_durability_bonus'):
                equipment.temp_durability_bonus = 0
            equipment.temp_durability_bonus += enhancement_amount
        
        equipment.max_durability += enhancement_amount
        equipment.current_durability += enhancement_amount  # 현재 내구도도 증가
    
    @staticmethod
    def remove_temporary_enhancements(equipment):
        """임시 내구도 강화 효과 제거"""
        if not equipment or not hasattr(equipment, 'temp_durability_bonus'):
            return
        
        if equipment.temp_durability_bonus > 0:
            equipment.max_durability -= equipment.temp_durability_bonus
            equipment.current_durability = min(equipment.current_durability, equipment.max_durability)
            equipment.temp_durability_bonus = 0

class GoldBalanceSystem:
    """골드 시스템 밸런스"""
    
    # 골드 획득 소스별 배율
    GOLD_SOURCES = {
        "enemy_kill": {
            "base": 5,           # 기본 5골드
            "level_multiplier": 1.2,   # 레벨당 20% 증가
            "floor_multiplier": 0.5    # 층당 50% 증가
        },
        "treasure_chest": {
            "base": 25,          # 기본 25골드
            "rarity_multipliers": {
                "일반": 1.0,
                "희귀": 2.0,
                "영웅": 4.0,
                "전설": 8.0
            }
        },
        "quest_reward": {
            "base": 50,          # 기본 50골드
            "difficulty_multipliers": {
                "쉬움": 0.8,
                "보통": 1.0,
                "어려움": 1.5,
                "지옥": 2.5
            }
        },
        "item_sale": {
            "base_multiplier": 0.4,  # 원가의 40%
            "merchant_personality": {
                "generous": 0.6,     # 60% (관대한 상인)
                "normal": 0.4,       # 40% (보통 상인)
                "stingy": 0.25       # 25% (구두쇠 상인)
            }
        }
    }
    
    # 골드 소모 항목별 가격
    GOLD_COSTS = {
        "equipment_repair": {
            "base_per_durability": 2,  # 내구도 1당 2골드
            "rarity_multipliers": {
                "일반": 1.0,
                "고급": 1.5,
                "희귀": 2.0,
                "영웅": 3.0,
                "전설": 5.0,
                "신화": 8.0
            }
        },
        "inn_rest": {
            "base": 10,          # 기본 10골드
            "luxury_multiplier": 3.0,  # 고급실 3배
            "party_size_cost": 5      # 파티원 1명당 5골드 추가
        },
        "skill_training": {
            "base": 100,         # 기본 100골드
            "level_multiplier": 50    # 레벨당 50골드 추가
        },
        "equipment_enhancement": {
            "base": 200,         # 기본 200골드
            "level_multiplier": 100   # 강화 레벨당 100골드 추가
        }
    }
    
    @staticmethod
    def calculate_enemy_gold_drop(enemy_level: int, current_floor: int) -> int:
        """적 처치 시 골드 드롭량 계산"""
        source = GoldBalanceSystem.GOLD_SOURCES["enemy_kill"]
        
        base_gold = source["base"]
        level_bonus = int(enemy_level * source["level_multiplier"])
        floor_bonus = int(current_floor * source["floor_multiplier"])
        
        total_gold = base_gold + level_bonus + floor_bonus
        
        # 랜덤 변동 (±30%)
        variation = random.uniform(0.7, 1.3)
        
        return max(1, int(total_gold * variation))
    
    @staticmethod
    def calculate_repair_cost(equipment, repair_amount: int) -> int:
        """수리 비용 계산"""
        costs = GoldBalanceSystem.GOLD_COSTS["equipment_repair"]
        
        base_cost = repair_amount * costs["base_per_durability"]
        
        # 장비 등급에 따른 배율
        rarity_multiplier = 1.0
        if hasattr(equipment, 'rarity'):
            if hasattr(equipment.rarity, 'value'):
                rarity_multiplier = costs["rarity_multipliers"].get(equipment.rarity.value, 1.0)
            else:
                rarity_multiplier = costs["rarity_multipliers"].get(str(equipment.rarity), 1.0)
        
        final_cost = int(base_cost * rarity_multiplier)
        
        return max(5, final_cost)  # 최소 5골드
    
    @staticmethod
    def calculate_item_sale_price(item_base_price: int, merchant_personality: str = "normal") -> int:
        """아이템 판매 가격 계산"""
        source = GoldBalanceSystem.GOLD_SOURCES["item_sale"]
        
        personality_multiplier = source["merchant_personality"].get(merchant_personality, 0.4)
        
        sale_price = int(item_base_price * personality_multiplier)
        
        return max(1, sale_price)  # 최소 1골드

# 전역 시스템 인스턴스
durability_system = DurabilitySystem()
gold_balance_system = GoldBalanceSystem()

def get_durability_system() -> DurabilitySystem:
    """내구도 시스템 반환"""
    return durability_system

def get_gold_balance_system() -> GoldBalanceSystem:
    """골드 밸런스 시스템 반환"""
    return gold_balance_system
