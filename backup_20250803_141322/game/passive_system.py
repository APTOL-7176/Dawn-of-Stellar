#!/usr/bin/env python3
"""
패시브 시스템 - 6가지 패시브 중 2개 선택
게임 시작 전 선택, 일부는 잠금 해제 필요
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import json
import os


class PassiveType(Enum):
    """패시브 타입 (6가지)"""
    COMBAT_MASTERY = "전투 숙련"     # 전투 관련 보너스
    SURVIVAL_INSTINCT = "생존 본능"  # 생존 관련 보너스  
    TREASURE_HUNTER = "보물 사냥꾼"  # 아이템/골드 관련
    ARCANE_KNOWLEDGE = "비전 지식"   # 마법 관련 보너스
    TACTICAL_GENIUS = "전술 천재"    # 파티/전략 관련
    FORTUNE_SEEKER = "행운 추구자"   # 운/확률 관련


@dataclass
class PassiveEffect:
    """패시브 효과"""
    name: str
    description: str
    effect_type: str  # stat_bonus, special_effect, probability_bonus
    effect_value: Any
    unlock_condition: Optional[str] = None


class PassiveSkill:
    """패시브 스킬"""
    
    def __init__(self, passive_type: PassiveType, name: str, description: str, 
                 effects: List[PassiveEffect], unlock_condition: Optional[str] = None):
        self.passive_type = passive_type
        self.name = name
        self.description = description
        self.effects = effects
        self.unlock_condition = unlock_condition
        self.is_unlocked = unlock_condition is None  # 조건 없으면 기본 해금
    
    def check_unlock(self, player_stats: Dict) -> bool:
        """잠금 해제 조건 확인"""
        if self.is_unlocked:
            return True
            
        if not self.unlock_condition:
            return True
            
        # 조건 파싱 및 확인
        condition_parts = self.unlock_condition.split(":")
        if len(condition_parts) != 2:
            return False
            
        condition_type, requirement = condition_parts
        
        if condition_type == "wins":
            return player_stats.get("total_wins", 0) >= int(requirement)
        elif condition_type == "floor":
            return player_stats.get("best_floor", 0) >= int(requirement)
        elif condition_type == "gold":
            return player_stats.get("total_gold", 0) >= int(requirement)
        elif condition_type == "runs":
            return player_stats.get("total_runs", 0) >= int(requirement)
            
        return False


class PassiveSystem:
    """패시브 시스템 관리"""
    
    def __init__(self):
        self.available_passives = self._initialize_passives()
        self.selected_passives = []  # 선택된 2개 패시브
        self.unlocked_passives = []  # 해금된 패시브 목록
        
    def _initialize_passives(self) -> Dict[PassiveType, List[PassiveSkill]]:
        """6가지 패시브 초기화"""
        passives = {
            PassiveType.COMBAT_MASTERY: [
                PassiveSkill(
                    PassiveType.COMBAT_MASTERY,
                    "전투의 달인",
                    "공격력 +15%, 크리티컬 확률 +10%",
                    [
                        PassiveEffect("공격력 증가", "모든 공격력 15% 증가", "stat_bonus", {"attack": 0.15}),
                        PassiveEffect("크리티컬 증가", "크리티컬 확률 10% 증가", "stat_bonus", {"critical": 0.10})
                    ]
                ),
                PassiveSkill(
                    PassiveType.COMBAT_MASTERY,
                    "무기 전문가",
                    "무기 공격 시 추가 데미지 +20%, 명중률 +15%",
                    [
                        PassiveEffect("무기 특화", "무기 공격 데미지 20% 증가", "special_effect", {"weapon_damage": 0.20}),
                        PassiveEffect("정확한 타격", "명중률 15% 증가", "stat_bonus", {"accuracy": 0.15})
                    ],
                    unlock_condition="wins:50"
                )
            ],
            
            PassiveType.SURVIVAL_INSTINCT: [
                PassiveSkill(
                    PassiveType.SURVIVAL_INSTINCT,
                    "생존자",
                    "체력 +25%, 방어력 +20%, 상처 회복속도 +50%",
                    [
                        PassiveEffect("체력 강화", "최대 HP 25% 증가", "stat_bonus", {"hp": 0.25}),
                        PassiveEffect("방어 강화", "방어력 20% 증가", "stat_bonus", {"defense": 0.20}),
                        PassiveEffect("빠른 회복", "상처 치유 속도 50% 증가", "special_effect", {"wound_heal": 0.50})
                    ]
                ),
                PassiveSkill(
                    PassiveType.SURVIVAL_INSTINCT,
                    "불굴의 의지",
                    "HP 20% 이하에서 모든 능력치 +30%, 즉사 공격 무효",
                    [
                        PassiveEffect("절망적 상황", "HP 20% 이하일 때 모든 능력치 30% 증가", "special_effect", {"desperate_boost": 0.30}),
                        PassiveEffect("즉사 면역", "즉사 공격을 무시", "special_effect", {"death_immunity": True})
                    ],
                    unlock_condition="floor:20"
                )
            ],
            
            PassiveType.TREASURE_HUNTER: [
                PassiveSkill(
                    PassiveType.TREASURE_HUNTER,
                    "보물 탐지",
                    "골드 획득량 +40%, 아이템 드롭률 +25%",
                    [
                        PassiveEffect("황금 감각", "골드 획득량 40% 증가", "stat_bonus", {"gold_rate": 0.40}),
                        PassiveEffect("아이템 운", "아이템 드롭률 25% 증가", "stat_bonus", {"item_drop": 0.25})
                    ]
                ),
                PassiveSkill(
                    PassiveType.TREASURE_HUNTER,
                    "전설의 수집가",
                    "희귀 아이템 확률 +50%, 상점 할인 30%",
                    [
                        PassiveEffect("희귀템 사냥꾼", "희귀 아이템 확률 50% 증가", "stat_bonus", {"rare_item": 0.50}),
                        PassiveEffect("상인의 친구", "상점에서 30% 할인", "special_effect", {"shop_discount": 0.30})
                    ],
                    unlock_condition="gold:10000"
                )
            ],
            
            PassiveType.ARCANE_KNOWLEDGE: [
                PassiveSkill(
                    PassiveType.ARCANE_KNOWLEDGE,
                    "마법 숙련자",
                    "마법력 +20%, MP 회복속도 +30%, 캐스팅 시간 -25%",
                    [
                        PassiveEffect("마법 증폭", "마법력 20% 증가", "stat_bonus", {"magic": 0.20}),
                        PassiveEffect("마나 흐름", "MP 회복속도 30% 증가", "special_effect", {"mp_regen": 0.30}),
                        PassiveEffect("빠른 시전", "캐스팅 시간 25% 감소", "special_effect", {"cast_speed": 0.25})
                    ]
                ),
                PassiveSkill(
                    PassiveType.ARCANE_KNOWLEDGE,
                    "원소 조작자",
                    "모든 속성 데미지 +30%, 속성 상성 보너스 +100%",
                    [
                        PassiveEffect("원소 지배", "속성 데미지 30% 증가", "special_effect", {"element_damage": 0.30}),
                        PassiveEffect("상성 극대화", "속성 상성 보너스 100% 증가", "special_effect", {"element_bonus": 1.00})
                    ],
                    unlock_condition="runs:15"
                )
            ],
            
            PassiveType.TACTICAL_GENIUS: [
                PassiveSkill(
                    PassiveType.TACTICAL_GENIUS,
                    "전략가",
                    "파티 전체 속도 +15%, 스킬 쿨다운 -20%",
                    [
                        PassiveEffect("팀워크", "파티 전체 속도 15% 증가", "special_effect", {"party_speed": 0.15}),
                        PassiveEffect("효율적 전술", "모든 스킬 쿨다운 20% 감소", "special_effect", {"cooldown_reduction": 0.20})
                    ]
                ),
                PassiveSkill(
                    PassiveType.TACTICAL_GENIUS,
                    "완벽한 지휘관",
                    "파티 전체 모든 능력치 +10%, ATB 게이지 충전 +25%",
                    [
                        PassiveEffect("지휘 보너스", "파티 전체 모든 능력치 10% 증가", "special_effect", {"party_all_stats": 0.10}),
                        PassiveEffect("빠른 행동", "ATB 게이지 충전속도 25% 증가", "special_effect", {"atb_speed": 0.25})
                    ],
                    unlock_condition="floor:15"
                )
            ],
            
            PassiveType.FORTUNE_SEEKER: [
                PassiveSkill(
                    PassiveType.FORTUNE_SEEKER,
                    "행운아",
                    "운 +30%, 회피율 +15%, 크리티컬 회피 +20%",
                    [
                        PassiveEffect("행운 증가", "운 스탯 30% 증가", "stat_bonus", {"luck": 0.30}),
                        PassiveEffect("행운한 회피", "회피율 15% 증가", "stat_bonus", {"evasion": 0.15}),
                        PassiveEffect("위기 탈출", "크리티컬 회피 20% 증가", "special_effect", {"crit_avoid": 0.20})
                    ]
                ),
                PassiveSkill(
                    PassiveType.FORTUNE_SEEKER,
                    "운명 조작자",
                    "모든 확률 판정 +25%, 턴당 5% 확률로 추가 행동",
                    [
                        PassiveEffect("확률 조작", "모든 확률 판정 25% 보너스", "special_effect", {"probability_bonus": 0.25}),
                        PassiveEffect("운명의 여신", "턴당 5% 확률로 추가 행동", "special_effect", {"extra_turn": 0.05})
                    ],
                    unlock_condition="runs:25"
                )
            ]
        }
        
        return passives
    
    def get_available_passives(self, player_stats: Dict) -> List[PassiveSkill]:
        """선택 가능한 패시브 목록 (해금된 것만)"""
        available = []
        
        for passive_type, passive_list in self.available_passives.items():
            for passive in passive_list:
                if passive.check_unlock(player_stats):
                    passive.is_unlocked = True
                    available.append(passive)
        
        return available
    
    def select_passives(self, passive1: PassiveSkill, passive2: PassiveSkill) -> bool:
        """2개 패시브 선택"""
        if len(self.selected_passives) >= 2:
            self.selected_passives.clear()
        
        if passive1 == passive2:
            return False  # 같은 패시브 중복 선택 불가
            
        self.selected_passives = [passive1, passive2]
        return True
    
    def get_selected_passives(self) -> List[PassiveSkill]:
        """선택된 패시브 반환"""
        return self.selected_passives.copy()
    
    def apply_passive_effects(self, character, situation: str = "general") -> Dict[str, Any]:
        """패시브 효과 적용"""
        total_effects = {}
        
        for passive in self.selected_passives:
            for effect in passive.effects:
                if effect.effect_type == "stat_bonus":
                    # 스탯 보너스
                    for stat, bonus in effect.effect_value.items():
                        if stat not in total_effects:
                            total_effects[stat] = 0
                        total_effects[stat] += bonus
                        
                elif effect.effect_type == "special_effect":
                    # 특수 효과
                    for effect_name, value in effect.effect_value.items():
                        total_effects[effect_name] = value
        
        return total_effects
    
    def get_passive_description(self) -> str:
        """현재 선택된 패시브 설명"""
        if not self.selected_passives:
            return "선택된 패시브가 없습니다."
        
        descriptions = []
        for i, passive in enumerate(self.selected_passives, 1):
            descriptions.append(f"{i}. {passive.name}: {passive.description}")
        
        return "\n".join(descriptions)
    
    def save_selection(self, filename: str = "passive_selection.json"):
        """패시브 선택 저장"""
        data = {
            "selected_passives": [
                {
                    "type": passive.passive_type.value,
                    "name": passive.name
                }
                for passive in self.selected_passives
            ]
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"패시브 선택 저장 실패: {e}")
    
    def load_selection(self, filename: str = "passive_selection.json"):
        """패시브 선택 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.selected_passives.clear()
            
            for saved_passive in data.get("selected_passives", []):
                passive_type = PassiveType(saved_passive["type"])
                passive_name = saved_passive["name"]
                
                # 해당 패시브 찾기
                for passive in self.available_passives[passive_type]:
                    if passive.name == passive_name:
                        self.selected_passives.append(passive)
                        break
                        
        except FileNotFoundError:
            print("저장된 패시브 선택이 없습니다.")
        except Exception as e:
            print(f"패시브 선택 로드 실패: {e}")


def show_passive_selection_menu(player_stats: Dict) -> PassiveSystem:
    """패시브 선택 메뉴 표시 - 커서 방식"""
    passive_system = PassiveSystem()
    available_passives = passive_system.get_available_passives(player_stats)
    
    if len(available_passives) < 2:
        print("❌ 선택 가능한 패시브가 부족합니다. (최소 2개 필요)")
        return passive_system
    
    try:
        from .cursor_menu_system import create_simple_menu
        
        print("\n" + "="*80)
        print("🎯 패시브 선택 - 2개를 선택하세요")
        print("="*80)
        
        # 첫 번째 패시브 선택
        options = []
        descriptions = []
        
        for passive in available_passives:
            unlock_status = "🔓" if passive.is_unlocked else "🔒"
            type_icon = {
                PassiveType.COMBAT_MASTERY: "⚔️",
                PassiveType.SURVIVAL_INSTINCT: "🛡️", 
                PassiveType.TREASURE_HUNTER: "💰",
                PassiveType.ARCANE_KNOWLEDGE: "🔮",
                PassiveType.TACTICAL_GENIUS: "🧠",
                PassiveType.FORTUNE_SEEKER: "🍀"
            }.get(passive.passive_type, "❓")
            
            option_text = f"{unlock_status} {type_icon} {passive.name}"
            if not passive.is_unlocked:
                option_text += " [잠김]"
                
            options.append(option_text)
            
            desc = passive.description
            if not passive.is_unlocked and passive.unlock_condition:
                desc += f" | 🔒 해금 조건: {passive.unlock_condition}"
            descriptions.append(desc)
        
        # 첫 번째 선택
        menu1 = create_simple_menu("1번째 패시브 선택", options, descriptions)
        first_result = menu1.run()
        
        if first_result == -1 or first_result >= len(available_passives):
            return passive_system
            
        first_passive = available_passives[first_result]
        if not first_passive.is_unlocked:
            print("❌ 잠긴 패시브입니다!")
            return passive_system
        
        # 두 번째 패시브 선택 (첫 번째 제외)
        second_options = []
        second_descriptions = []
        second_available = []
        
        for i, passive in enumerate(available_passives):
            if i == first_result:  # 이미 선택된 패시브는 제외
                continue
                
            unlock_status = "🔓" if passive.is_unlocked else "🔒"
            type_icon = {
                PassiveType.COMBAT_MASTERY: "⚔️",
                PassiveType.SURVIVAL_INSTINCT: "🛡️", 
                PassiveType.TREASURE_HUNTER: "💰",
                PassiveType.ARCANE_KNOWLEDGE: "🔮",
                PassiveType.TACTICAL_GENIUS: "🧠",
                PassiveType.FORTUNE_SEEKER: "🍀"
            }.get(passive.passive_type, "❓")
            
            option_text = f"{unlock_status} {type_icon} {passive.name}"
            if not passive.is_unlocked:
                option_text += " [잠김]"
                
            second_options.append(option_text)
            
            desc = passive.description
            if not passive.is_unlocked and passive.unlock_condition:
                desc += f" | 🔒 해금 조건: {passive.unlock_condition}"
            second_descriptions.append(desc)
            second_available.append(passive)
        
        menu2 = create_simple_menu("2번째 패시브 선택", second_options, second_descriptions)
        second_result = menu2.run()
        
        if second_result == -1 or second_result >= len(second_available):
            return passive_system
            
        second_passive = second_available[second_result]
        if not second_passive.is_unlocked:
            print("❌ 잠긴 패시브입니다!")
            return passive_system
        
        # 선택 적용
        passive_system.select_passives(first_passive, second_passive)
        
        print(f"\n🎯 최종 선택:")
        print(passive_system.get_passive_description())
        
        # 선택 저장
        passive_system.save_selection()
        
        return passive_system
        
    except ImportError:
        # 폴백: 기존 텍스트 메뉴
        return _show_passive_selection_menu_fallback(player_stats, passive_system, available_passives)

def _show_passive_selection_menu_fallback(player_stats: Dict, passive_system, available_passives) -> PassiveSystem:
    """패시브 선택 메뉴 폴백 (기존 방식)"""
    print("\n📋 선택 가능한 패시브:")
    for i, passive in enumerate(available_passives, 1):
        unlock_status = "🔓" if passive.is_unlocked else "🔒"
        type_icon = {
            PassiveType.COMBAT_MASTERY: "⚔️",
            PassiveType.SURVIVAL_INSTINCT: "🛡️", 
            PassiveType.TREASURE_HUNTER: "💰",
            PassiveType.ARCANE_KNOWLEDGE: "🔮",
            PassiveType.TACTICAL_GENIUS: "🧠",
            PassiveType.FORTUNE_SEEKER: "🍀"
        }
        
        icon = type_icon.get(passive.passive_type, "❓")
        print(f"\n{i:2}. {unlock_status} {icon} {passive.name} ({passive.passive_type.value})")
        print(f"     {passive.description}")
        
        if not passive.is_unlocked and passive.unlock_condition:
            print(f"     🔒 해금 조건: {passive.unlock_condition}")
    
    # 2개 선택
    selected_passives = []
    for selection_num in [1, 2]:
        while True:
            try:
                choice = input(f"\n{selection_num}번째 패시브 선택 (1-{len(available_passives)}): ")
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(available_passives):
                    selected_passive = available_passives[choice_idx]
                    
                    if not selected_passive.is_unlocked:
                        print("❌ 잠긴 패시브입니다!")
                        continue
                    
                    if selected_passive in selected_passives:
                        print("❌ 이미 선택한 패시브입니다!")
                        continue
                    
                    selected_passives.append(selected_passive)
                    print(f"✅ {selected_passive.name} 선택됨!")
                    break
                else:
                    print("❌ 잘못된 번호입니다!")
                    
            except ValueError:
                print("❌ 숫자를 입력하세요!")
    
    # 선택 적용
    passive_system.select_passives(selected_passives[0], selected_passives[1])
    
    print(f"\n🎯 최종 선택:")
    print(passive_system.get_passive_description())
    
    # 선택 저장
    passive_system.save_selection()
    
    return passive_system


# 전역 패시브 시스템
global_passive_system = PassiveSystem()

def get_passive_system() -> PassiveSystem:
    """패시브 시스템 반환"""
    return global_passive_system
