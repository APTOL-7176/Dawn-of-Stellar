#!/usr/bin/env python3
"""
상태 이상 시스템 - 완전 구현
Dawn of Stellar의 모든 상태 이상과 버프/디버프 관리
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import random

class StatusType(Enum):
    """상태 이상 타입"""
    BUFF = "buff"
    DEBUFF = "debuff"
    DOT = "dot"  # Damage over Time
    HOT = "hot"  # Heal over Time
    STUN = "stun"
    SILENCE = "silence"
    POISON = "poison"
    BURN = "burn"
    FREEZE = "freeze"
    PARALYZE = "paralyze"
    SLEEP = "sleep"
    CHARM = "charm"
    FEAR = "fear"
    BLIND = "blind"
    WEAKEN = "weaken"
    STRENGTHEN = "strengthen"
    HASTE = "haste"
    SLOW = "slow"
    SHIELD = "shield"
    REGENERATION = "regeneration"
    CURSE = "curse"
    BLESSING = "blessing"

class StatusEffect:
    """상태 이상 효과 클래스"""
    
    def __init__(self, name: str, status_type: StatusType, duration: int, 
                 effect_value: Any, description: str = "", stackable: bool = False,
                 max_stacks: int = 1, tick_timing: str = "start"):
        self.name = name
        self.status_type = status_type
        self.duration = duration
        self.max_duration = duration
        self.effect_value = effect_value
        self.description = description
        self.stackable = stackable
        self.max_stacks = max_stacks
        self.current_stacks = 1
        self.tick_timing = tick_timing  # "start", "end", "both"
        self.is_active = True
        
    def apply_effect(self, character):
        """효과 적용"""
        if not self.is_active or self.duration <= 0:
            return None
            
        result = {"message": "", "damage": 0, "heal": 0, "stat_changes": {}}
        
        # DOT 효과 (독, 화상 등)
        if self.status_type in [StatusType.POISON, StatusType.BURN, StatusType.DOT]:
            damage = self._calculate_dot_damage(character)
            actual_damage = character.take_damage(damage)
            result["damage"] = actual_damage
            result["message"] = f"💀 {character.name}이(가) {self.name}으로 {actual_damage} 피해!"
            
        # HOT 효과 (재생, 치유 등)
        elif self.status_type in [StatusType.REGENERATION, StatusType.HOT]:
            heal = self._calculate_hot_healing(character)
            actual_heal = character.heal(heal)
            result["heal"] = actual_heal
            result["message"] = f"💚 {character.name}이(가) {self.name}으로 {actual_heal} 회복!"
            
        # 스탯 변화 효과
        elif self.status_type in [StatusType.BUFF, StatusType.DEBUFF]:
            self._apply_stat_effects(character, result)
            
        # 특수 상태 효과
        elif self.status_type == StatusType.STUN:
            character.stunned = True
            result["message"] = f"😵 {character.name}이(가) 기절 상태입니다!"
            
        elif self.status_type == StatusType.SILENCE:
            character.silenced = True
            result["message"] = f"🤐 {character.name}이(가) 침묵 상태입니다!"
            
        elif self.status_type == StatusType.PARALYZE:
            character.paralyzed = True
            if random.random() < 0.5:  # 50% 확률로 행동 불가
                result["message"] = f"⚡ {character.name}이(가) 마비로 인해 행동할 수 없습니다!"
            
        elif self.status_type == StatusType.SLEEP:
            character.sleeping = True
            result["message"] = f"😴 {character.name}이(가) 잠들어 있습니다!"
            
        elif self.status_type == StatusType.FREEZE:
            character.frozen = True
            result["message"] = f"🧊 {character.name}이(가) 빙결 상태입니다!"
            
        elif self.status_type == StatusType.BLIND:
            character.blinded = True
            result["message"] = f"👁️ {character.name}이(가) 실명 상태입니다!"
            
        return result
    
    def _calculate_dot_damage(self, character):
        """DOT 데미지 계산"""
        if isinstance(self.effect_value, dict):
            base_damage = self.effect_value.get("damage", 10)
            damage_type = self.effect_value.get("type", "fixed")
            
            if damage_type == "percent":
                return int(character.max_hp * (base_damage / 100))
            elif damage_type == "scaled":
                # 최대 HP에 따른 스케일링
                return int(base_damage + (character.max_hp * 0.02))
            else:
                return base_damage * self.current_stacks
        return self.effect_value * self.current_stacks
    
    def _calculate_hot_healing(self, character):
        """HOT 회복량 계산"""
        if isinstance(self.effect_value, dict):
            base_heal = self.effect_value.get("heal", 10)
            heal_type = self.effect_value.get("type", "fixed")
            
            if heal_type == "percent":
                return int(character.max_hp * (base_heal / 100))
            elif heal_type == "scaled":
                return int(base_heal + (character.max_hp * 0.03))
            else:
                return base_heal * self.current_stacks
        return self.effect_value * self.current_stacks
    
    def _apply_stat_effects(self, character, result):
        """스탯 효과 적용"""
        if not isinstance(self.effect_value, dict):
            return
            
        stat_changes = {}
        
        # 공격력 변화
        if "attack_bonus" in self.effect_value:
            bonus = self.effect_value["attack_bonus"] * self.current_stacks
            character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + bonus
            stat_changes["attack"] = bonus
            
        if "attack_penalty" in self.effect_value:
            penalty = self.effect_value["attack_penalty"] * self.current_stacks
            character.temp_attack_penalty = getattr(character, 'temp_attack_penalty', 0) + penalty
            stat_changes["attack"] = -penalty
            
        # 방어력 변화
        if "defense_bonus" in self.effect_value:
            bonus = self.effect_value["defense_bonus"] * self.current_stacks
            character.temp_defense_bonus = getattr(character, 'temp_defense_bonus', 0) + bonus
            stat_changes["defense"] = bonus
            
        if "defense_penalty" in self.effect_value:
            penalty = self.effect_value["defense_penalty"] * self.current_stacks
            character.temp_defense_penalty = getattr(character, 'temp_defense_penalty', 0) + penalty
            stat_changes["defense"] = -penalty
            
        # 속도 변화
        if "speed_bonus" in self.effect_value:
            bonus = self.effect_value["speed_bonus"] * self.current_stacks
            character.temp_speed_bonus = getattr(character, 'temp_speed_bonus', 0) + bonus
            stat_changes["speed"] = bonus
            
        if "speed_penalty" in self.effect_value:
            penalty = self.effect_value["speed_penalty"] * self.current_stacks
            character.temp_speed_penalty = getattr(character, 'temp_speed_penalty', 0) + penalty
            stat_changes["speed"] = -penalty
            
        # 마법력 변화
        if "magic_bonus" in self.effect_value:
            bonus = self.effect_value["magic_bonus"] * self.current_stacks
            character.temp_magic_bonus = getattr(character, 'temp_magic_bonus', 0) + bonus
            stat_changes["magic"] = bonus
            
        result["stat_changes"] = stat_changes
        
        if stat_changes:
            changes_text = ", ".join([f"{k}{'+'if v>0 else ''}{v}" for k, v in stat_changes.items()])
            buff_type = "강화" if self.status_type == StatusType.BUFF else "약화"
            result["message"] = f"✨ {character.name}의 {changes_text} ({buff_type})"
    
    def update_duration(self):
        """지속시간 업데이트"""
        if self.duration > 0:
            self.duration -= 1
        return self.duration > 0
    
    def add_stack(self):
        """스택 추가"""
        if self.stackable and self.current_stacks < self.max_stacks:
            self.current_stacks += 1
            return True
        return False
    
    def remove_stack(self):
        """스택 제거"""
        if self.current_stacks > 1:
            self.current_stacks -= 1
            return True
        return False

class StatusEffectManager:
    """상태 이상 관리자"""
    
    def __init__(self):
        self.status_templates = self._create_status_templates()
    
    def _create_status_templates(self) -> Dict[str, Dict]:
        """상태 이상 템플릿 생성"""
        return {
            # 독성 효과
            "독": {
                "type": StatusType.POISON,
                "duration": 5,
                "effect": {"damage": 15, "type": "fixed"},
                "description": "매 턴 HP가 감소합니다",
                "stackable": True,
                "max_stacks": 3
            },
            "맹독": {
                "type": StatusType.POISON,
                "duration": 3,
                "effect": {"damage": 8, "type": "percent"},
                "description": "매 턴 최대 HP의 8%씩 감소합니다",
                "stackable": False
            },
            
            # 화상 효과
            "화상": {
                "type": StatusType.BURN,
                "duration": 4,
                "effect": {"damage": 20, "type": "fixed"},
                "description": "매 턴 화상 피해를 입습니다",
                "stackable": True,
                "max_stacks": 5
            },
            "대화상": {
                "type": StatusType.BURN,
                "duration": 6,
                "effect": {"damage": 25, "type": "scaled"},
                "description": "강력한 화상 피해를 지속적으로 입습니다",
                "stackable": False
            },
            
            # 회복 효과
            "재생": {
                "type": StatusType.REGENERATION,
                "duration": 5,
                "effect": {"heal": 25, "type": "fixed"},
                "description": "매 턴 HP가 회복됩니다",
                "stackable": True,
                "max_stacks": 3
            },
            "고속재생": {
                "type": StatusType.REGENERATION,
                "duration": 3,
                "effect": {"heal": 10, "type": "percent"},
                "description": "매 턴 최대 HP의 10%씩 회복합니다",
                "stackable": False
            },
            
            # 버프 효과
            "공격력 강화": {
                "type": StatusType.BUFF,
                "duration": 5,
                "effect": {"attack_bonus": 30},
                "description": "공격력이 증가합니다",
                "stackable": True,
                "max_stacks": 3
            },
            "방어력 강화": {
                "type": StatusType.BUFF,
                "duration": 5,
                "effect": {"defense_bonus": 25},
                "description": "방어력이 증가합니다",
                "stackable": True,
                "max_stacks": 3
            },
            "가속": {
                "type": StatusType.HASTE,
                "duration": 3,
                "effect": {"speed_bonus": 50},
                "description": "행동 속도가 크게 증가합니다",
                "stackable": False
            },
            "마법력 강화": {
                "type": StatusType.BUFF,
                "duration": 4,
                "effect": {"magic_bonus": 40},
                "description": "마법력이 증가합니다",
                "stackable": True,
                "max_stacks": 2
            },
            
            # 디버프 효과
            "공격력 저하": {
                "type": StatusType.DEBUFF,
                "duration": 4,
                "effect": {"attack_penalty": 25},
                "description": "공격력이 감소합니다",
                "stackable": True,
                "max_stacks": 3
            },
            "방어력 저하": {
                "type": StatusType.DEBUFF,
                "duration": 4,
                "effect": {"defense_penalty": 20},
                "description": "방어력이 감소합니다",
                "stackable": True,
                "max_stacks": 3
            },
            "둔화": {
                "type": StatusType.SLOW,
                "duration": 3,
                "effect": {"speed_penalty": 30},
                "description": "행동 속도가 감소합니다",
                "stackable": False
            },
            
            # 상태 이상 효과
            "기절": {
                "type": StatusType.STUN,
                "duration": 2,
                "effect": {},
                "description": "행동할 수 없습니다",
                "stackable": False
            },
            "침묵": {
                "type": StatusType.SILENCE,
                "duration": 3,
                "effect": {},
                "description": "스킬을 사용할 수 없습니다",
                "stackable": False
            },
            "마비": {
                "type": StatusType.PARALYZE,
                "duration": 3,
                "effect": {},
                "description": "50% 확률로 행동할 수 없습니다",
                "stackable": False
            },
            "수면": {
                "type": StatusType.SLEEP,
                "duration": 2,
                "effect": {},
                "description": "잠들어 행동할 수 없습니다 (공격받으면 해제)",
                "stackable": False
            },
            "빙결": {
                "type": StatusType.FREEZE,
                "duration": 2,
                "effect": {"speed_penalty": 80},
                "description": "얼어서 거의 움직일 수 없습니다",
                "stackable": False
            },
            "실명": {
                "type": StatusType.BLIND,
                "duration": 3,
                "effect": {"attack_penalty": 50},
                "description": "공격이 빗나갈 확률이 높습니다",
                "stackable": False
            },
            
            # 특수 효과
            "보호막": {
                "type": StatusType.SHIELD,
                "duration": 5,
                "effect": {"shield_value": 100},
                "description": "일정량의 피해를 흡수합니다",
                "stackable": True,
                "max_stacks": 3
            },
            "축복": {
                "type": StatusType.BLESSING,
                "duration": 10,
                "effect": {"attack_bonus": 15, "defense_bonus": 15, "magic_bonus": 15},
                "description": "모든 능력치가 향상됩니다",
                "stackable": False
            },
            "저주": {
                "type": StatusType.CURSE,
                "duration": 8,
                "effect": {"attack_penalty": 20, "defense_penalty": 20, "damage": 10},
                "description": "모든 능력치가 저하되고 지속 피해를 입습니다",
                "stackable": False
            }
        }
    
    def create_status_effect(self, name: str, custom_duration: Optional[int] = None,
                           custom_effect: Optional[Dict] = None) -> Optional[StatusEffect]:
        """상태 이상 생성"""
        if name not in self.status_templates:
            return None
            
        template = self.status_templates[name].copy()
        duration = custom_duration if custom_duration is not None else template["duration"]
        effect = custom_effect if custom_effect is not None else template["effect"]
        
        return StatusEffect(
            name=name,
            status_type=template["type"],
            duration=duration,
            effect_value=effect,
            description=template["description"],
            stackable=template.get("stackable", False),
            max_stacks=template.get("max_stacks", 1)
        )
    
    def get_available_status_effects(self) -> List[str]:
        """사용 가능한 상태 이상 목록"""
        return list(self.status_templates.keys())
    
    def get_status_description(self, name: str) -> str:
        """상태 이상 설명 반환"""
        if name in self.status_templates:
            return self.status_templates[name]["description"]
        return "알 수 없는 상태 이상"

# 전역 상태 이상 관리자 인스턴스
status_manager = StatusEffectManager()

def apply_status_to_character(character, status_name: str, duration: Optional[int] = None):
    """캐릭터에게 상태 이상 적용"""
    if not hasattr(character, 'status_effects'):
        character.status_effects = []
    
    # 기존 상태 이상 확인
    existing_status = None
    for status in character.status_effects:
        if status.name == status_name:
            existing_status = status
            break
    
    if existing_status:
        if existing_status.stackable:
            existing_status.add_stack()
            existing_status.duration = max(existing_status.duration, duration or existing_status.max_duration)
        else:
            # 지속시간 갱신
            existing_status.duration = duration or existing_status.max_duration
    else:
        # 새로운 상태 이상 추가
        new_status = status_manager.create_status_effect(status_name, duration)
        if new_status:
            character.status_effects.append(new_status)
    
def update_character_status_effects(character):
    """캐릭터의 모든 상태 이상 업데이트"""
    if not hasattr(character, 'status_effects'):
        character.status_effects = []
        return []
    
    results = []
    expired_effects = []
    
    # 모든 상태 이상 처리
    for status in character.status_effects:
        if status.tick_timing in ["start", "both"]:
            result = status.apply_effect(character)
            if result and result["message"]:
                results.append(result)
        
        # 지속시간 감소
        if not status.update_duration():
            expired_effects.append(status)
    
    # 만료된 효과 제거
    for expired in expired_effects:
        character.status_effects.remove(expired)
        results.append({"message": f"⏰ {character.name}의 {expired.name} 효과가 종료되었습니다."})
    
    return results

def remove_status_from_character(character, status_name: str):
    """캐릭터에서 특정 상태 이상 제거"""
    if not hasattr(character, 'status_effects'):
        return False
    
    for status in character.status_effects[:]:
        if status.name == status_name:
            character.status_effects.remove(status)
            return True
    return False

def clear_all_status_effects(character):
    """캐릭터의 모든 상태 이상 제거"""
    if hasattr(character, 'status_effects'):
        character.status_effects.clear()

def get_character_status_summary(character) -> str:
    """캐릭터의 상태 이상 요약"""
    if not hasattr(character, 'status_effects') or not character.status_effects:
        return "상태 이상 없음"
    
    status_list = []
    for status in character.status_effects:
        stack_info = f"×{status.current_stacks}" if status.stackable and status.current_stacks > 1 else ""
        status_list.append(f"{status.name}({status.duration}){stack_info}")
    
    return " | ".join(status_list)
