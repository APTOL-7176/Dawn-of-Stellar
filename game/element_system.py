#!/usr/bin/env python3
"""
속성 시스템
10가지 속성과 상성 관계, 스킬/아이템 연동
"""

from typing import Dict, List, Optional
from enum import Enum
import random

class ElementType(Enum):
    """속성 타입"""
    FIRE = "화염"        # 🔥 화염
    ICE = "빙결"         # ❄️ 빙결  
    LIGHTNING = "번개"   # ⚡ 번개
    EARTH = "대지"       # 🌍 대지
    WIND = "바람"        # 💨 바람
    WATER = "물"         # 💧 물
    LIGHT = "빛"         # ✨ 빛
    DARK = "어둠"        # 🌑 어둠
    POISON = "독"        # ☠️ 독
    NEUTRAL = "무속성"   # ⚪ 무속성

class ElementalAffinity(Enum):
    """속성 친화도"""
    ABSORB = "흡수"      # 200% 회복
    RESIST = "저항"      # 50% 데미지
    WEAK = "약점"        # 150% 데미지
    IMMUNE = "무효"      # 0% 데미지
    NORMAL = "보통"      # 100% 데미지

class ElementSystem:
    """속성 시스템 관리 클래스"""
    
    def __init__(self):
        self.weakness_chart = self._initialize_weakness_chart()
        self.element_effects = self._initialize_element_effects()
        
    def _initialize_weakness_chart(self) -> Dict[ElementType, Dict[ElementType, float]]:
        """속성 상성표 초기화"""
        chart = {}
        
        # 기본값: 모든 속성은 서로에게 보통 (1.0배)
        for elem1 in ElementType:
            chart[elem1] = {}
            for elem2 in ElementType:
                chart[elem1][elem2] = 1.0
        
        # 🔥 화염 상성
        chart[ElementType.FIRE][ElementType.ICE] = 1.5      # 화염 → 빙결 (강함)
        chart[ElementType.FIRE][ElementType.WATER] = 0.5    # 화염 → 물 (약함)
        chart[ElementType.FIRE][ElementType.WIND] = 1.2     # 화염 → 바람 (조금 강함)
        chart[ElementType.FIRE][ElementType.EARTH] = 0.8    # 화염 → 대지 (조금 약함)
        
        # ❄️ 빙결 상성
        chart[ElementType.ICE][ElementType.FIRE] = 0.5      # 빙결 → 화염 (약함)
        chart[ElementType.ICE][ElementType.WATER] = 1.3     # 빙결 → 물 (강함)
        chart[ElementType.ICE][ElementType.LIGHTNING] = 0.8 # 빙결 → 번개 (약함)
        
        # ⚡ 번개 상성
        chart[ElementType.LIGHTNING][ElementType.WATER] = 1.5   # 번개 → 물 (강함)
        chart[ElementType.LIGHTNING][ElementType.EARTH] = 0.5   # 번개 → 대지 (약함)
        chart[ElementType.LIGHTNING][ElementType.WIND] = 1.3    # 번개 → 바람 (강함)
        
        # 🌍 대지 상성
        chart[ElementType.EARTH][ElementType.LIGHTNING] = 1.5   # 대지 → 번개 (강함)
        chart[ElementType.EARTH][ElementType.WIND] = 0.5        # 대지 → 바람 (약함)
        chart[ElementType.EARTH][ElementType.WATER] = 0.8       # 대지 → 물 (약함)
        
        # 💨 바람 상성
        chart[ElementType.WIND][ElementType.EARTH] = 1.5        # 바람 → 대지 (강함)
        chart[ElementType.WIND][ElementType.FIRE] = 0.8         # 바람 → 화염 (약함)
        chart[ElementType.WIND][ElementType.LIGHTNING] = 0.7    # 바람 → 번개 (약함)
        
        # 💧 물 상성
        chart[ElementType.WATER][ElementType.FIRE] = 1.5        # 물 → 화염 (강함)
        chart[ElementType.WATER][ElementType.LIGHTNING] = 0.5   # 물 → 번개 (약함)
        chart[ElementType.WATER][ElementType.ICE] = 0.7         # 물 → 빙결 (약함)
        
        # ✨ 빛 상성
        chart[ElementType.LIGHT][ElementType.DARK] = 1.5        # 빛 → 어둠 (강함)
        chart[ElementType.LIGHT][ElementType.POISON] = 1.3      # 빛 → 독 (강함)
        
        # 🌑 어둠 상성
        chart[ElementType.DARK][ElementType.LIGHT] = 1.5        # 어둠 → 빛 (강함)
        chart[ElementType.DARK][ElementType.POISON] = 1.2       # 어둠 → 독 (강함)
        
        # ☠️ 독 상성
        chart[ElementType.POISON][ElementType.LIGHT] = 0.7      # 독 → 빛 (약함)
        chart[ElementType.POISON][ElementType.WATER] = 1.2      # 독 → 물 (강함)
        
        return chart
    
    def _initialize_element_effects(self) -> Dict[ElementType, Dict[str, any]]:
        """속성별 특수 효과 정의"""
        effects = {
            ElementType.FIRE: {
                "status_inflict": "화상",
                "status_chance": 0.15,
                "damage_over_time": 10,
                "description": "지속 화상 피해를 입힐 수 있음"
            },
            ElementType.ICE: {
                "status_inflict": "빙결",
                "status_chance": 0.12,
                "speed_reduction": 0.5,
                "description": "적을 얼려 행동 속도를 늦출 수 있음"
            },
            ElementType.LIGHTNING: {
                "status_inflict": "마비",
                "status_chance": 0.18,
                "accuracy_reduction": 0.3,
                "description": "마비로 적의 명중률을 떨어뜨릴 수 있음"
            },
            ElementType.EARTH: {
                "status_inflict": "중량",
                "status_chance": 0.10,
                "movement_reduction": 0.7,
                "description": "무거워져 이동력이 감소함"
            },
            ElementType.WIND: {
                "status_inflict": "혼란",
                "status_chance": 0.14,
                "accuracy_reduction": 0.4,
                "description": "혼란에 빠져 행동이 불안정해짐"
            },
            ElementType.WATER: {
                "status_inflict": "축축함",
                "status_chance": 0.16,
                "fire_weakness": 1.3,
                "description": "화염 공격에 더 큰 피해를 받음"
            },
            ElementType.LIGHT: {
                "status_inflict": "신성화",
                "status_chance": 0.08,
                "healing_boost": 1.5,
                "description": "신성한 빛으로 치유 효과 증가"
            },
            ElementType.DARK: {
                "status_inflict": "저주",
                "status_chance": 0.13,
                "all_stats_reduction": 0.9,
                "description": "모든 능력치가 감소하는 저주"
            },
            ElementType.POISON: {
                "status_inflict": "중독",
                "status_chance": 0.20,
                "poison_damage": 15,
                "description": "강력한 독으로 지속 피해"
            },
            ElementType.NEUTRAL: {
                "status_inflict": None,
                "status_chance": 0.0,
                "description": "속성 상성에 영향받지 않음"
            }
        }
        return effects
    
    def get_damage_multiplier(self, attacker_element: ElementType, 
                            defender_element: ElementType) -> float:
        """속성 상성에 따른 데미지 배율 반환"""
        if attacker_element == ElementType.NEUTRAL:
            return 1.0
        
        return self.weakness_chart.get(attacker_element, {}).get(defender_element, 1.0)
    
    def get_element_effectiveness_text(self, multiplier: float) -> str:
        """속성 효과를 텍스트로 반환"""
        if multiplier >= 1.5:
            return "효과가 뛰어났다!"
        elif multiplier >= 1.2:
            return "효과적이다!"
        elif multiplier <= 0.5:
            return "효과가 미약하다..."
        elif multiplier <= 0.8:
            return "효과가 별로다..."
        else:
            return ""
    
    def apply_element_status(self, target, element: ElementType) -> bool:
        """속성에 따른 상태이상 적용"""
        effect = self.element_effects.get(element)
        if not effect or not effect["status_inflict"]:
            return False
        
        if random.random() < effect["status_chance"]:
            status_name = effect["status_inflict"]
            # 상태이상 적용 로직 (status_effects.py와 연동)
            return True
        return False
    
    def get_element_color(self, element: ElementType) -> str:
        """속성별 색상 코드 반환"""
        colors = {
            ElementType.FIRE: "🔥",
            ElementType.ICE: "❄️",
            ElementType.LIGHTNING: "⚡",
            ElementType.EARTH: "🌍",
            ElementType.WIND: "💨",
            ElementType.WATER: "💧",
            ElementType.LIGHT: "✨",
            ElementType.DARK: "🌑",
            ElementType.POISON: "☠️",
            ElementType.NEUTRAL: "⚪"
        }
        return colors.get(element, "⚪")
    
    def get_random_element(self, exclude_neutral: bool = False) -> ElementType:
        """랜덤 속성 반환"""
        elements = list(ElementType)
        if exclude_neutral:
            elements.remove(ElementType.NEUTRAL)
        return random.choice(elements)
    
    def get_opposing_element(self, element: ElementType) -> Optional[ElementType]:
        """대립 속성 반환"""
        opposites = {
            ElementType.FIRE: ElementType.ICE,
            ElementType.ICE: ElementType.FIRE,
            ElementType.LIGHTNING: ElementType.EARTH,
            ElementType.EARTH: ElementType.WIND,
            ElementType.WIND: ElementType.LIGHTNING,
            ElementType.WATER: ElementType.FIRE,
            ElementType.LIGHT: ElementType.DARK,
            ElementType.DARK: ElementType.LIGHT,
            ElementType.POISON: ElementType.LIGHT,
        }
        return opposites.get(element)

# 전역 속성 시스템 인스턴스
element_system = ElementSystem()

def get_element_system():
    """속성 시스템 인스턴스 반환"""
    return element_system
