#!/usr/bin/env python3
"""
원소 상성 시스템 - FFVII 스타일 원소 상성표
"""

from enum import Enum
from typing import Dict, List, Tuple


class ElementType(Enum):
    """원소 타입"""
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
    HOLY = "신성"
    GRAVITY = "중력"


class ElementalChart:
    """원소 상성표 시스템"""
    
    def __init__(self):
        # 원소 상성표 (공격 원소 -> 방어 원소 -> 배율)
        self.effectiveness_chart = {
            ElementType.FIRE: {
                ElementType.ICE: 1.8,      # 화염 vs 냉기 = 강함
                ElementType.EARTH: 1.5,    # 화염 vs 대지 = 강함
                ElementType.WIND: 1.3,     # 화염 vs 바람 = 약간 강함
                ElementType.WATER: 0.6,    # 화염 vs 물 = 약함
                ElementType.FIRE: 0.8,     # 화염 vs 화염 = 저항
                ElementType.NEUTRAL: 1.0,  # 기본
            },
            
            ElementType.ICE: {
                ElementType.FIRE: 0.6,     # 냉기 vs 화염 = 약함
                ElementType.WATER: 1.6,    # 냉기 vs 물 = 강함
                ElementType.EARTH: 1.4,    # 냉기 vs 대지 = 강함
                ElementType.WIND: 1.2,     # 냉기 vs 바람 = 약간 강함
                ElementType.ICE: 0.8,      # 냉기 vs 냉기 = 저항
                ElementType.LIGHTNING: 0.9, # 냉기 vs 번개 = 약간 약함
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.LIGHTNING: {
                ElementType.WATER: 1.8,    # 번개 vs 물 = 강함
                ElementType.WIND: 1.6,     # 번개 vs 바람 = 강함
                ElementType.EARTH: 0.7,    # 번개 vs 대지 = 약함
                ElementType.ICE: 1.3,      # 번개 vs 냉기 = 약간 강함
                ElementType.LIGHTNING: 0.8, # 번개 vs 번개 = 저항
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.EARTH: {
                ElementType.LIGHTNING: 1.7, # 대지 vs 번개 = 강함
                ElementType.FIRE: 0.7,     # 대지 vs 화염 = 약함
                ElementType.ICE: 0.8,      # 대지 vs 냉기 = 약함
                ElementType.WIND: 0.9,     # 대지 vs 바람 = 약간 약함
                ElementType.WATER: 1.4,    # 대지 vs 물 = 강함
                ElementType.EARTH: 0.8,    # 대지 vs 대지 = 저항
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.WIND: {
                ElementType.EARTH: 1.6,    # 바람 vs 대지 = 강함
                ElementType.FIRE: 0.8,     # 바람 vs 화염 = 약함
                ElementType.ICE: 0.9,      # 바람 vs 냉기 = 약간 약함
                ElementType.LIGHTNING: 0.7, # 바람 vs 번개 = 약함
                ElementType.WATER: 1.3,    # 바람 vs 물 = 약간 강함
                ElementType.WIND: 0.8,     # 바람 vs 바람 = 저항
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.WATER: {
                ElementType.FIRE: 1.8,     # 물 vs 화염 = 강함
                ElementType.LIGHTNING: 0.6, # 물 vs 번개 = 약함
                ElementType.ICE: 0.7,      # 물 vs 냉기 = 약함
                ElementType.EARTH: 0.8,    # 물 vs 대지 = 약함
                ElementType.WIND: 0.9,     # 물 vs 바람 = 약간 약함
                ElementType.WATER: 0.8,    # 물 vs 물 = 저항
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.LIGHT: {
                ElementType.DARK: 1.8,     # 빛 vs 어둠 = 강함
                ElementType.POISON: 1.6,   # 빛 vs 독 = 강함
                ElementType.LIGHT: 0.8,    # 빛 vs 빛 = 저항
                ElementType.HOLY: 1.2,     # 빛 vs 신성 = 약간 강함
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.DARK: {
                ElementType.LIGHT: 0.6,    # 어둠 vs 빛 = 약함
                ElementType.HOLY: 0.7,     # 어둠 vs 신성 = 약함
                ElementType.DARK: 0.8,     # 어둠 vs 어둠 = 저항
                ElementType.POISON: 1.4,   # 어둠 vs 독 = 강함
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.POISON: {
                ElementType.LIGHT: 0.6,    # 독 vs 빛 = 약함
                ElementType.HOLY: 0.7,     # 독 vs 신성 = 약함
                ElementType.DARK: 0.9,     # 독 vs 어둠 = 약간 약함
                ElementType.WATER: 0.8,    # 독 vs 물 = 약함
                ElementType.POISON: 0.8,   # 독 vs 독 = 저항
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.HOLY: {
                ElementType.DARK: 1.8,     # 신성 vs 어둠 = 강함
                ElementType.POISON: 1.7,   # 신성 vs 독 = 강함
                ElementType.LIGHT: 0.9,    # 신성 vs 빛 = 약간 약함
                ElementType.HOLY: 0.8,     # 신성 vs 신성 = 저항
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.GRAVITY: {
                ElementType.WIND: 1.5,     # 중력 vs 바람 = 강함
                ElementType.GRAVITY: 0.8,  # 중력 vs 중력 = 저항
                ElementType.NEUTRAL: 1.0,
            },
            
            ElementType.NEUTRAL: {
                # 무속성은 모든 원소에 1.0배율
                ElementType.FIRE: 1.0,
                ElementType.ICE: 1.0,
                ElementType.LIGHTNING: 1.0,
                ElementType.EARTH: 1.0,
                ElementType.WIND: 1.0,
                ElementType.WATER: 1.0,
                ElementType.LIGHT: 1.0,
                ElementType.DARK: 1.0,
                ElementType.POISON: 1.0,
                ElementType.HOLY: 1.0,
                ElementType.GRAVITY: 1.0,
                ElementType.NEUTRAL: 1.0,
            }
        }
        
        # 원소별 특수 효과
        self.elemental_effects = {
            ElementType.FIRE: {
                "status_chance": 0.15,
                "status_type": "burn",
                "description": "화상 상태이상 부여 가능"
            },
            ElementType.ICE: {
                "status_chance": 0.12,
                "status_type": "freeze",
                "description": "빙결 상태이상 부여 가능"
            },
            ElementType.LIGHTNING: {
                "status_chance": 0.10,
                "status_type": "paralysis",
                "description": "마비 상태이상 부여 가능"
            },
            ElementType.POISON: {
                "status_chance": 0.20,
                "status_type": "poison",
                "description": "독 상태이상 부여 가능"
            },
            ElementType.DARK: {
                "status_chance": 0.08,
                "status_type": "curse",
                "description": "저주 상태이상 부여 가능"
            },
            ElementType.HOLY: {
                "healing_bonus": 1.2,
                "description": "치유 효과 20% 증가"
            }
        }
    
    def get_effectiveness(self, attack_element: ElementType, defend_element: ElementType) -> float:
        """원소 상성 배율 반환 (0.6 ~ 1.8)"""
        if attack_element in self.effectiveness_chart:
            return self.effectiveness_chart[attack_element].get(defend_element, 1.0)
        return 1.0
    
    def get_element_description(self, element: ElementType) -> str:
        """원소 설명 반환"""
        descriptions = {
            ElementType.FIRE: "🔥 화염 - 냉기와 대지에 강함, 물에 약함",
            ElementType.ICE: "❄️ 냉기 - 물과 대지에 강함, 화염에 약함",
            ElementType.LIGHTNING: "⚡ 번개 - 물과 바람에 강함, 대지에 약함",
            ElementType.EARTH: "🌍 대지 - 번개와 물에 강함, 화염에 약함",
            ElementType.WIND: "💨 바람 - 대지에 강함, 번개에 약함",
            ElementType.WATER: "💧 물 - 화염에 강함, 번개에 약함",
            ElementType.LIGHT: "✨ 빛 - 어둠과 독에 강함",
            ElementType.DARK: "🌑 어둠 - 독에 강함, 빛에 약함",
            ElementType.POISON: "☠️ 독 - 상태이상 특화",
            ElementType.HOLY: "🕊️ 신성 - 어둠과 독에 강함, 치유 강화",
            ElementType.GRAVITY: "🌌 중력 - 바람에 강함",
            ElementType.NEUTRAL: "⚪ 무속성 - 균등한 효과"
        }
        return descriptions.get(element, "알 수 없는 원소")
    
    def get_weakness_chart(self, element: ElementType) -> List[Tuple[ElementType, float]]:
        """특정 원소의 약점들 반환"""
        weaknesses = []
        for attack_elem, defense_dict in self.effectiveness_chart.items():
            multiplier = defense_dict.get(element, 1.0)
            if multiplier > 1.0:  # 1.0보다 크면 약점
                weaknesses.append((attack_elem, multiplier))
        
        # 배율이 높은 순으로 정렬
        weaknesses.sort(key=lambda x: x[1], reverse=True)
        return weaknesses
    
    def get_resistance_chart(self, element: ElementType) -> List[Tuple[ElementType, float]]:
        """특정 원소의 저항들 반환"""
        resistances = []
        for attack_elem, defense_dict in self.effectiveness_chart.items():
            multiplier = defense_dict.get(element, 1.0)
            if multiplier < 1.0:  # 1.0보다 작으면 저항
                resistances.append((attack_elem, multiplier))
        
        # 배율이 낮은 순으로 정렬
        resistances.sort(key=lambda x: x[1])
        return resistances
    
    def display_full_chart(self):
        """전체 상성표 출력"""
        print("🌟 원소 상성표 🌟")
        print("=" * 60)
        
        for element in ElementType:
            print(f"\n{self.get_element_description(element)}")
            
            weaknesses = self.get_weakness_chart(element)
            if weaknesses:
                print(f"  약점: ", end="")
                weak_strs = [f"{w[0].value}({w[1]}배)" for w in weaknesses]
                print(", ".join(weak_strs))
            
            resistances = self.get_resistance_chart(element)
            if resistances:
                print(f"  저항: ", end="")
                resist_strs = [f"{r[0].value}({r[1]}배)" for r in resistances]
                print(", ".join(resist_strs))


# 전역 원소 상성표 인스턴스
_elemental_chart = None

def get_elemental_chart() -> ElementalChart:
    """원소 상성표 싱글톤 반환"""
    global _elemental_chart
    if _elemental_chart is None:
        _elemental_chart = ElementalChart()
    return _elemental_chart

def calculate_elemental_damage(base_damage: int, attack_element: ElementType, defend_element: ElementType) -> int:
    """원소 상성을 고려한 데미지 계산"""
    chart = get_elemental_chart()
    multiplier = chart.get_effectiveness(attack_element, defend_element)
    final_damage = int(base_damage * multiplier)
    
    return final_damage

def get_elemental_status_chance(attack_element: ElementType) -> Tuple[str, float]:
    """원소별 상태이상 부여 확률 반환"""
    chart = get_elemental_chart()
    effect_data = chart.elemental_effects.get(attack_element, {})
    
    status_type = effect_data.get("status_type", "")
    chance = effect_data.get("status_chance", 0.0)
    
    return status_type, chance


if __name__ == "__main__":
    # 원소 상성표 테스트
    chart = ElementalChart()
    chart.display_full_chart()
    
    # 테스트 데미지 계산
    print("\n🧪 데미지 계산 테스트:")
    test_cases = [
        (100, ElementType.FIRE, ElementType.ICE),
        (100, ElementType.FIRE, ElementType.WATER),
        (100, ElementType.LIGHTNING, ElementType.WATER),
        (100, ElementType.NEUTRAL, ElementType.FIRE),
    ]
    
    for base_dmg, atk_elem, def_elem in test_cases:
        final_dmg = calculate_elemental_damage(base_dmg, atk_elem, def_elem)
        multiplier = chart.get_effectiveness(atk_elem, def_elem)
        print(f"{atk_elem.value} vs {def_elem.value}: {base_dmg} → {final_dmg} ({multiplier}배)")
