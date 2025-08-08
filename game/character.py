"""
캐릭터 및 파티 관리 시스템 (Brave 시스템 포함)
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
import random
from .new_skill_system import StatusType, get_status_icon
from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, magenta, blue

# 전역 전투 상태 변수
_combat_active = False

def set_combat_active(active: bool):
    """전투 상태 설정"""
    global _combat_active
    _combat_active = active

def is_combat_active() -> bool:
    """전투 상태 확인"""
    return _combat_active

class StatusEffect:
    """상태이상 효과"""
    def __init__(self, status_type: StatusType, duration: int, intensity: float = 1.0):
        self.status_type = status_type
        self.duration = duration
        self.intensity = intensity
        self.stack_count = 1

class StatusManager:
    """간단한 상태이상 관리자"""
    def __init__(self):
        self.status_effects: List[StatusEffect] = []
        self.effects = self.status_effects  # 호환성을 위한 별칭
        self.name = "StatusManager"  # name 속성 추가
        
    def add_status(self, status_effect, duration=None, intensity=None) -> bool:
        """상태이상 추가 (다양한 매개변수 형태 지원)"""
        # StatusEffect 객체가 직접 전달된 경우
        if hasattr(status_effect, 'status_type'):
            status_obj = status_effect
        else:
            # 문자열과 추가 매개변수로 전달된 경우
            if isinstance(status_effect, str):
                # 문자열에서 StatusType으로 변환
                try:
                    if hasattr(StatusType, status_effect.upper()):
                        status_type = getattr(StatusType, status_effect.upper())
                    else:
                        # 기본 StatusType 설정
                        status_type = StatusType.BUFF
                except:
                    status_type = StatusType.BUFF
                
                status_obj = StatusEffect(
                    name=status_effect,
                    status_type=status_type,
                    duration=duration or 3,
                    intensity=intensity or 1
                )
            else:
                return False
        
        existing = self.get_status(status_obj.status_type)
        if existing:
            existing.duration = max(existing.duration, status_obj.duration)
            return False
        else:
            self.status_effects.append(status_obj)
            self.effects = self.status_effects  # 별칭 업데이트
            return True
    
    def get_status(self, status_type: StatusType):
        """특정 상태이상 반환"""
        for effect in self.status_effects:
            if effect.status_type == status_type:
                return effect
        return None
    
    def has_status(self, status_type: StatusType) -> bool:
        """특정 상태이상이 있는지 확인"""
        return self.get_status(status_type) is not None
    
    def process_turn_effects(self, character=None) -> List[str]:
        """턴 처리 - 상태이상 효과 적용 (자동 애니메이션)"""
        messages = []
        
        # 캐릭터 객체가 제공되지 않으면 빈 메시지 리스트 반환
        if character is None:
            return messages
            
        # 캐릭터 이름 안전하게 가져오기
        char_name = getattr(character, 'name', '알 수 없는 캐릭터')
        
        for effect in self.status_effects[:]:
            # 독 데미지 처리
            if effect.status_type == StatusType.POISON:
                damage = int(character.max_hp * 0.05 * effect.intensity)
                character.current_hp = max(1, character.current_hp - damage)
                messages.append(f"☠️ {char_name}이(가) 독 데미지 {damage}를 받았습니다!")
            
            # 화상 데미지 처리
            elif effect.status_type == StatusType.BURN:
                damage = int(character.max_hp * 0.03 * effect.intensity)
                character.current_hp = max(1, character.current_hp - damage)
                messages.append(f"🔥 {char_name}이(가) 화상 데미지 {damage}를 받았습니다!")
            
            # 재생 효과 처리
            elif effect.status_type == StatusType.REGENERATION:
                heal = int(character.max_hp * 0.08 * effect.intensity)
                old_hp = character.current_hp
                character.current_hp = min(character.max_hp, character.current_hp + heal)
                actual_heal = character.current_hp - old_hp
                if actual_heal > 0:
                    messages.append(f"💚 {char_name}이(가) 재생으로 {actual_heal} 회복했습니다!")
            
            # 출혈 효과
            elif effect.status_type == StatusType.BLEED:
                damage = int(character.max_hp * 0.04 * effect.intensity)
                character.current_hp = max(1, character.current_hp - damage)
                messages.append(f"🩸 {char_name}이(가) 출혈로 {damage} 피해를 받았습니다!")
            
            # 부식 효과
            elif effect.status_type == StatusType.CORRODE:
                damage = int(character.max_hp * 0.03 * effect.intensity)
                character.current_hp = max(1, character.current_hp - damage)
                messages.append(f"🧪 {char_name}이(가) 부식으로 {damage} 피해를 받았습니다!")
            
            # 괴사 효과
            elif effect.status_type == StatusType.NECROSIS:
                damage = int(character.max_hp * 0.08 * effect.intensity)
                character.current_hp = max(1, character.current_hp - damage)
                messages.append(f"💀 {char_name}이(가) 괴사로 {damage} 피해를 받았습니다!")
            
            # 냉기 효과
            elif effect.status_type == StatusType.CHILL:
                if hasattr(character, 'temp_speed_bonus'):
                    character.temp_speed_bonus = getattr(character, 'temp_speed_bonus', 0) - int(character.speed * 0.2 * effect.intensity)
                messages.append(f"🧊 {char_name}이(가) 냉기에 움직임이 둔해졌습니다!")
            
            # 감전 효과
            elif effect.status_type == StatusType.SHOCK:
                if hasattr(character, 'temp_cooldown_increase'):
                    character.temp_cooldown_increase = getattr(character, 'temp_cooldown_increase', 0) + 1
                messages.append(f"⚡ {char_name}이(가) 감전으로 인해 행동이 둔해졌습니다!")
            
            # MP 재생
            elif effect.status_type == StatusType.MP_REGEN:
                if hasattr(character, 'current_mp') and hasattr(character, 'max_mp'):
                    mp_heal = int(character.max_mp * 0.05 * effect.intensity)
                    old_mp = character.current_mp
                    character.current_mp = min(character.max_mp, character.current_mp + mp_heal)
                    actual_mp_heal = character.current_mp - old_mp
                    if actual_mp_heal > 0:
                        messages.append(f"💙 {char_name}이(가) {actual_mp_heal} MP를 회복했습니다!")
            
            # MP 소모
            elif effect.status_type == StatusType.MP_DRAIN:
                if hasattr(character, 'current_mp'):
                    mp_damage = int(character.max_mp * 0.04 * effect.intensity)
                    character.current_mp = max(0, character.current_mp - mp_damage)
                    messages.append(f"💜 {char_name}이(가) {mp_damage} MP를 잃었습니다!")
            
            # 공포 효과
            elif effect.status_type == StatusType.FEAR:
                if hasattr(self, 'temp_accuracy_penalty'):
                    character.temp_accuracy_penalty = getattr(self, 'temp_accuracy_penalty', 0) + int(20 * effect.intensity)
                    character.temp_dodge_penalty = getattr(self, 'temp_dodge_penalty', 0) + int(15 * effect.intensity)
                messages.append(f"😰 {character.name}이(가) 공포에 떨고 있습니다!")
            
            # 매혹 효과
            elif effect.status_type == StatusType.CHARM:
                messages.append(f"💖 {character.name}이(가) 매혹에 빠져 있습니다!")
            
            # 지배 효과
            elif effect.status_type == StatusType.DOMINATE:
                messages.append(f"👁️ {character.name}이(가) 정신을 지배당하고 있습니다!")
            
            # 혼란 효과
            elif effect.status_type == StatusType.CONFUSION:
                messages.append(f"😵‍💫 {character.name}이(가) 혼란에 빠져 있습니다!")
            
            # 광기 효과
            elif effect.status_type == StatusType.MADNESS:
                if hasattr(self, 'temp_attack_bonus'):
                    character.temp_attack_bonus = getattr(self, 'temp_attack_bonus', 0) + int(15 * effect.intensity)
                if hasattr(self, 'temp_defense_bonus'):
                    self.temp_defense_bonus = getattr(self, 'temp_defense_bonus', 0) - int(10 * effect.intensity)
                messages.append(f"🤪 {self.name}이(가) 광기에 휩싸였습니다!")
            
            # 저주 효과
            elif effect.status_type == StatusType.CURSE:
                curse_penalty = int(5 * effect.intensity)
                for stat in ['temp_attack_bonus', 'temp_defense_bonus', 'temp_magic_bonus', 'temp_speed_bonus']:
                    if hasattr(self, stat):
                        setattr(self, stat, getattr(self, stat, 0) - curse_penalty)
                messages.append(f"🌑 {self.name}이(가) 저주에 걸려 모든 능력이 감소했습니다!")
            
            # 축복 효과
            elif effect.status_type == StatusType.BLESSING:
                blessing_bonus = int(8 * effect.intensity)
                for stat in ['temp_attack_bonus', 'temp_defense_bonus', 'temp_magic_bonus', 'temp_speed_bonus']:
                    if hasattr(self, stat):
                        setattr(self, stat, getattr(self, stat, 0) + blessing_bonus)
                messages.append(f"✨ {self.name}이(가) 축복을 받아 모든 능력이 증가했습니다!")
            
            # 버프/디버프 효과는 스탯 계산에서 처리
            elif effect.status_type in [StatusType.STRENGTHEN, StatusType.WEAKEN, 
                                       StatusType.HASTE, StatusType.SLOW, StatusType.SHIELD]:
                # 이미 get_stat_modifiers에서 처리됨
                pass
            
            # 상태이상 지속시간 감소
            effect.duration -= 1
            if effect.duration <= 0:
                self.status_effects.remove(effect)
                messages.append(f"✨ {self.name}의 {effect.status_type.value} 효과가 해제되었습니다!")
        
        return messages
    
    def get_status_display(self) -> str:
        """상태이상 표시"""
        if not self.status_effects:
            return ""
        icons = [get_status_icon(effect.status_type) for effect in self.status_effects]
        return " ".join(icons)
    
    def can_act(self) -> bool:
        """행동 가능 여부 - 확장된 상태이상 체크"""
        # 완전 행동 불가 상태
        blocking_states = [
            StatusType.STUN, StatusType.SLEEP, StatusType.FREEZE, 
            StatusType.PETRIFY, StatusType.PARALYZE, StatusType.TIME_STOP
        ]
        
        if any(effect.status_type in blocking_states for effect in self.status_effects):
            return False
            
        # 혼란/매혹/지배 상태에서는 행동 가능하지만 제어 불가
        return True
    
    def can_use_skills(self) -> bool:
        """스킬 사용 가능 여부"""
        silencing_states = [StatusType.SILENCE, StatusType.MADNESS]
        return not any(effect.status_type in silencing_states for effect in self.status_effects)
    
    def apply_status(self, status_type_str: str, duration: int, intensity: int = 1) -> bool:
        """상태이상 적용 (문자열 타입 처리)"""
        try:
            # 문자열을 StatusType으로 변환
            if isinstance(status_type_str, str):
                # 독 -> POISON 변환
                status_mapping = {
                    '독': StatusType.POISON,
                    '화상': StatusType.BURN,
                    '출혈': StatusType.BLEED,
                    '재생': StatusType.REGENERATION,
                    '마비': StatusType.PARALYZE,
                    '기절': StatusType.STUN,
                    '수면': StatusType.SLEEP,
                    '냉기': StatusType.CHILL,
                    '감전': StatusType.SHOCK,
                    '빙결': StatusType.FREEZE,
                    '석화': StatusType.PETRIFY,
                    '침묵': StatusType.SILENCE,
                    '부식': StatusType.CORRODE,
                    '괴사': StatusType.NECROSIS,
                    '강화': StatusType.STRENGTHEN,
                    '약화': StatusType.WEAKEN,
                    '가속': StatusType.HASTE,
                    '감속': StatusType.SLOW,
                    '보호': StatusType.SHIELD,
                    '매혹': StatusType.CHARM,
                    '지배': StatusType.DOMINATE,
                    '혼란': StatusType.CONFUSION,
                    '광기': StatusType.MADNESS,
                    '저주': StatusType.CURSE,
                    '축복': StatusType.BLESSING,
                    '시간정지': StatusType.TIME_STOP
                }
                
                status_type = status_mapping.get(status_type_str, StatusType.POISON)
            else:
                status_type = status_type_str
            
            # StatusEffect 생성 및 추가
            status_effect = StatusEffect(
                name=f"{status_type.name.lower()}_effect",
                status_type=status_type,
                duration=duration,
                effect_value=intensity
            )
            return self.add_status(status_effect)
            
        except Exception as e:
            print(f"⚠️ 상태이상 적용 오류: {e}")
            return False
    
    def is_controlled(self) -> bool:
        """적에게 조종당하는 상태인지"""
        control_states = [StatusType.CHARM, StatusType.DOMINATE, StatusType.CONFUSION]
        return any(effect.status_type in control_states for effect in self.status_effects)
    
    def has_stealth(self) -> bool:
        """은신 상태인지"""
        return any(effect.status_type == StatusType.STEALTH for effect in self.status_effects)
    
    def has_invincibility(self) -> bool:
        """무적 상태인지"""
        return any(effect.status_type == StatusType.INVINCIBLE for effect in self.status_effects)
    
    def get_stat_modifiers(self) -> dict:
        """스탯 수정치 반환 (곱셈용 배율) - 확장된 상태이상 포함"""
        modifiers = {
            'physical_attack': 1.0,
            'magic_attack': 1.0,
            'physical_defense': 1.0,
            'magic_defense': 1.0,
            'speed': 1.0,
            'accuracy': 1.0,
            'evasion': 1.0,
            'critical_rate': 1.0
        }
        
        for effect in self.status_effects:
            # 기본 버프/디버프
            if effect.status_type == StatusType.BOOST_ATK:
                modifiers['physical_attack'] *= (1.0 + effect.intensity * 0.2)
                modifiers['magic_attack'] *= (1.0 + effect.intensity * 0.2)
            elif effect.status_type == StatusType.BOOST_DEF:
                modifiers['physical_defense'] *= (1.0 + effect.intensity * 0.2)
                modifiers['magic_defense'] *= (1.0 + effect.intensity * 0.2)
            elif effect.status_type == StatusType.BOOST_SPD:
                modifiers['speed'] *= (1.0 + effect.intensity * 0.3)
            elif effect.status_type == StatusType.BOOST_ACCURACY:
                modifiers['accuracy'] *= (1.0 + effect.intensity * 0.15)
            elif effect.status_type == StatusType.BOOST_CRIT:
                modifiers['critical_rate'] *= (1.0 + effect.intensity * 0.25)
            elif effect.status_type == StatusType.BOOST_DODGE:
                modifiers['evasion'] *= (1.0 + effect.intensity * 0.2)
                
            # 디버프
            elif effect.status_type == StatusType.REDUCE_ATK:
                modifiers['physical_attack'] *= (1.0 - effect.intensity * 0.2)
                modifiers['magic_attack'] *= (1.0 - effect.intensity * 0.2)
            elif effect.status_type == StatusType.REDUCE_DEF:
                modifiers['physical_defense'] *= (1.0 - effect.intensity * 0.2)
                modifiers['magic_defense'] *= (1.0 - effect.intensity * 0.2)
            elif effect.status_type == StatusType.REDUCE_SPD:
                modifiers['speed'] *= (1.0 - effect.intensity * 0.3)
            elif effect.status_type == StatusType.REDUCE_ACCURACY:
                modifiers['accuracy'] *= (1.0 - effect.intensity * 0.15)
                
            # 특수 상태
            elif effect.status_type == StatusType.VULNERABLE:
                modifiers['physical_defense'] *= 0.5
                modifiers['magic_defense'] *= 0.5
            elif effect.status_type == StatusType.EXPOSED:
                modifiers['evasion'] *= 0.3
            elif effect.status_type == StatusType.WEAKNESS:
                modifiers['physical_attack'] *= 0.7
                modifiers['magic_attack'] *= 0.7
            elif effect.status_type == StatusType.HASTE:
                modifiers['speed'] *= 1.5
            elif effect.status_type == StatusType.SLOW:
                modifiers['speed'] *= 0.6
            elif effect.status_type == StatusType.FOCUS:
                modifiers['accuracy'] *= 1.3
                modifiers['critical_rate'] *= 1.2
            elif effect.status_type == StatusType.RAGE:
                modifiers['physical_attack'] *= 1.4
                modifiers['physical_defense'] *= 0.8
            elif effect.status_type == StatusType.BERSERK:
                modifiers['physical_attack'] *= 1.6
                modifiers['magic_attack'] *= 1.6
                modifiers['physical_defense'] *= 0.6
                modifiers['magic_defense'] *= 0.6
                modifiers['accuracy'] *= 0.8
            elif effect.status_type == StatusType.BLIND:
                modifiers['accuracy'] *= 0.3
            elif effect.status_type == StatusType.TERROR:
                modifiers['physical_attack'] *= 0.6
                modifiers['magic_attack'] *= 0.6
                modifiers['speed'] *= 0.7
                
            # 호환성을 위한 이전 버프/디버프
            elif hasattr(effect.status_type, 'value'):
                if 'BUFF_ATTACK' in effect.status_type.value:
                    modifiers['physical_attack'] *= (1.0 + effect.intensity * 0.01)
                    modifiers['magic_attack'] *= (1.0 + effect.intensity * 0.01)
                elif 'BUFF_DEFENSE' in effect.status_type.value:
                    modifiers['physical_defense'] *= (1.0 + effect.intensity * 0.01)
                    modifiers['magic_defense'] *= (1.0 + effect.intensity * 0.01)
                elif 'BUFF_SPEED' in effect.status_type.value:
                    modifiers['speed'] *= (1.0 + effect.intensity * 0.01)
                elif 'DEBUFF_ATTACK' in effect.status_type.value:
                    modifiers['physical_attack'] *= (1.0 - effect.intensity * 0.01)
                    modifiers['magic_attack'] *= (1.0 - effect.intensity * 0.01)
                elif 'DEBUFF_DEFENSE' in effect.status_type.value:
                    modifiers['physical_defense'] *= (1.0 - effect.intensity * 0.01)
                    modifiers['magic_defense'] *= (1.0 - effect.intensity * 0.01)
                elif 'DEBUFF_SPEED' in effect.status_type.value:
                    modifiers['speed'] *= (1.0 - effect.intensity * 0.01)
        
        return modifiers
    
    def add_effect(self, effect: StatusEffect):
        """상태이상 효과 추가 (호환성)"""
        self.add_status(effect)
        self.effects = self.status_effects  # 별칭 업데이트
    
    def clear_all_effects(self):
        """모든 상태이상 효과 제거"""
        self.status_effects.clear()
        self.effects = self.status_effects  # 별칭 업데이트
    
    def get_active_effects(self) -> List[str]:
        """활성 상태이상 목록"""
        return [effect.status_type.value for effect in self.status_effects]
from .items import Inventory, Item, ItemDatabase
from .brave_system import BraveMixin, BraveSkillDatabase
from config import game_config

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'

# 색상 함수들
def red(text): return f"{RED}{text}{RESET}"
def green(text): return f"{GREEN}{text}{RESET}"
def yellow(text): return f"{YELLOW}{text}{RESET}"
def blue(text): return f"{BLUE}{text}{RESET}"
def magenta(text): return f"{MAGENTA}{text}{RESET}"
def cyan(text): return f"{CYAN}{text}{RESET}"
def white(text): return f"{WHITE}{text}{RESET}"
def bright_black(text): return f"\033[90m{text}{RESET}"
def bright_yellow(text): return f"\033[93m{text}{RESET}"
def bright_white(text): return f"\033[97m{text}{RESET}"

# TYPE_CHECKING을 사용하여 순환 import 방지
if TYPE_CHECKING:
    from .smart_ai import SmartEnemyAI


class CharacterTrait:
    """캐릭터 특성 클래스"""
    
    def __init__(self, name: str, description: str, effect_type: str, effect_value: Any):
        self.name = name
        self.description = description
        self.effect_type = effect_type  # "passive", "active", "trigger"
        self.trait_type = effect_type  # trait_type 별칭 추가 (호환성)
        self.effect_value = effect_value
        # active 특성은 초기에 비활성화, passive/trigger는 항상 활성화
        self.is_active = (effect_type != "active")
        self.cooldown = 0
        self.max_cooldown = 0
        self.stack_count = 0
        self.max_stacks = 1
    
    def apply_passive_effect(self, character):
        """패시브 효과 적용"""
        if not self.is_active or self.effect_type != "passive":
            return
            
        effect = self.effect_value
        
        # 전사 특성
        if "low_hp_damage_boost" in effect:
            if character.current_hp <= character.max_hp * 0.25:
                character.temp_attack_bonus = character.physical_attack * (effect["low_hp_damage_boost"] - 1)
        
        if "defense_bonus" in effect:
            character.temp_defense_bonus = character.physical_defense * effect["defense_bonus"]
        
        if "enemy_attack_debuff" in effect:
            # 전투 시작 시 적용되는 효과 - 전투 시스템에서 처리
            pass
            
        if "high_hp_speed_boost" in effect:
            if character.current_hp >= character.max_hp * 0.5:
                character.temp_speed_bonus = character.speed * (effect["high_hp_speed_boost"] - 1)
        
        # 아크메이지 특성
        if "mana_efficiency" in effect:
            # 스킬 사용 시 처리
            pass
            
        if "elemental_mastery" in effect:
            character.temp_resistance_bonus = 0.2
            
        if "exp_bonus" in effect:
            character.temp_exp_bonus = effect["exp_bonus"]
            
        if "high_mp_magic_boost" in effect:
            if character.current_mp >= character.max_mp * 0.75:
                character.temp_magic_bonus = character.magic_attack * (effect["high_mp_magic_boost"] - 1)
        
        # 궁수 특성
        if "crit_chance_bonus" in effect:
            character.temp_crit_bonus = effect["crit_chance_bonus"]
            
        if "dodge_bonus" in effect:
            character.temp_dodge_bonus = effect["dodge_bonus"]
            
        if "weakness_detect" in effect:
            character.temp_penetration = effect["weakness_detect"]
            
        if "movement_bonus" in effect:
            # 이동 후 적용되는 효과
            pass
        
        # 도적 특성 (리메이크)
        if "poison_mastery" in effect:
            character.temp_poison_always = True
            character.temp_poison_boost = effect.get("poison_boost", 1.5)
            
        if "silence_chance" in effect:
            character.temp_silence_chance = effect["silence_chance"]
            
        if "poison_trigger" in effect:
            character.temp_poison_trigger = effect["poison_trigger"]
            
        if "poison_immunity" in effect:
            character.temp_poison_immunity = True
            character.temp_poison_reflect = effect.get("poison_reflect", False)
            
        if "poison_spread" in effect:
            character.temp_poison_spread = True
        
        # 성기사 특성
        if "holy_resistance" in effect:
            character.temp_undead_resistance = effect["holy_resistance"]
            
        if "holy_damage" in effect:
            character.temp_holy_damage = True
            
        if "protection_bonus" in effect:
            character.temp_protection_bonus = effect["protection_bonus"]
        
        # 시간술사 특성
        if "time_sense" in effect:
            character.temp_time_sense = True  # 적의 다음 행동 예측
            
        if "time_acceleration" in effect:
            character.temp_atb_boost = effect["time_acceleration"]  # ATB 충전 속도 증가
            
        if "future_sight" in effect:
            character.temp_crit_resistance = effect["future_sight"]  # 크리티컬 받을 확률 감소
            
        if "time_control" in effect:
            character.temp_debuff_reduction = effect["time_control"]  # 디버프 지속시간 감소
        
        # 차원술사 특성
        if "space_distortion" in effect:
            character.temp_enemy_accuracy_down = getattr(character, 'temp_enemy_accuracy_down', 0) + int(effect["space_distortion"] * 100)
        
        # 연금술사 특성
        if "potion_craft" in effect:
            character.temp_potion_multiplier = effect["potion_craft"]
            
        if "transmute" in effect:
            character.temp_ignore_resistance = True
            
        if "explosion" in effect:
            character.temp_explosion_boost = effect["explosion"]
            
        if "experiment" in effect:
            character.temp_debuff_duration_boost = effect["experiment"]
            
        if "magic_substance" in effect:
            character.temp_random_element = True  # 공격마다 랜덤 속성 부여
        
        # 철학자 특성
        if "wisdom" in effect:
            character.temp_mp_efficiency = 1.0 - effect["wisdom"]  # MP 소모량 감소
            
        if "logic" in effect:
            character.temp_logic_dodge_bonus = 0.15  # 패턴 분석으로 회피율 15% 증가
            
        if "enlightenment" in effect:
            character.temp_exp_bonus = effect["enlightenment"]  # 경험치 획득량 증가
        
        # 암흑기사 특성
        if "life_steal" in effect:
            character.temp_life_steal = effect["life_steal"]
            
        if "dark_pact" in effect:
            hp_ratio = character.current_hp / character.max_hp
            damage_boost = min(1.0, (1.0 - hp_ratio))
            character.temp_attack_bonus = character.physical_attack * damage_boost
            
        if "fear_aura" in effect:
            character.temp_fear_aura = effect["fear_aura"]
            
        if "dark_pulse" in effect:
            character.temp_dark_pulse = effect["dark_pulse"]
        
        # 몽크 특성
        if "combo_multiplier" in effect:
            # 연속 공격 시 처리
            pass
            
        if "status_resist" in effect:
            character.temp_status_resist = effect["status_resist"]
            
        if "meditation_recovery" in effect:
            # 턴 카운트 처리
            pass
        
        # 바드 특성
        if "party_damage_boost" in effect:
            # 파티 전체 공격력 증가 - 파티 시스템에서 처리
            pass
            
        if "turn_heal" in effect:
            # 턴 종료 시 파티 힐 - 턴 시스템에서 처리
            pass
            
        if "party_crit_boost" in effect:
            # 파티 크리티컬 증가 - 파티 시스템에서 처리
            pass
        
        # 네크로맨서 특성
        if "life_mana_drain" in effect:
            # 공격 시 HP/MP 동시 회복 - 공격 시스템에서 처리
            pass
            
        if "anti_heal_aura" in effect:
            # 적 회복 효과 감소 - 전투 시스템에서 처리
            pass
        
        # 용기사 특성
        if "dragon_breath" in effect:
            character.temp_fire_damage = True
            
        if "scale_armor" in effect:
            character.temp_physical_resistance = effect["scale_armor"]
            
        if "dragon_rage" in effect:
            hp_ratio = character.current_hp / character.max_hp
            speed_boost = (1.0 - hp_ratio) * 0.5  # 최대 50% 속도 증가
            character.temp_speed_bonus = character.speed * speed_boost
            
        if "debuff_resist" in effect:
            character.temp_debuff_resist = effect["debuff_resist"]
        
        # 검성 특성
        if "sword_mastery" in effect:
            # 무기가 검류일 때만 적용 - 장비 시스템에서 처리
            if hasattr(character, 'equipped_weapon') and character.equipped_weapon:
                character.temp_weapon_mastery = effect["sword_mastery"]
                
        if "weapon_protection" in effect:
            character.temp_weapon_immunity = True
        
        # 정령술사 특성
        if "elemental_affinity" in effect:
            character.temp_elemental_boost = effect["elemental_affinity"]
            
        if "nature_blessing" in effect:
            # 턴 시작 시 MP 회복 - 턴 시스템에서 처리
            pass
            
        if "mana_cycle" in effect:
            character.temp_mana_efficiency = effect["mana_cycle"]
        
        # 암살자 특성 - 그림자 시스템
        if "shadow_generation" in effect:
            if not hasattr(character, 'shadow_count'):
                character.shadow_count = 0
            character.shadow_count += effect["shadow_generation"]
            
        if "shadow_power" in effect:
            shadow_count = getattr(character, 'shadow_count', 0)
            character.temp_attack_bonus += character.physical_attack * (effect["shadow_power"] * shadow_count)
        
        if "shadow_defense" in effect:
            # 그림자 방어 시스템 - 피격 시 그림자 소모로 50% 피해 감소
            character.temp_shadow_defense = True
            character.temp_shadow_defense_reduction = effect.get("reduction", 0.5)  # 기본 50% 감소
        
        # 기계공학자 특성
        if "gear_enhance" in effect:
            character.temp_equipment_boost = effect["gear_enhance"]
            
        if "bomb_craft" in effect:
            character.temp_infinite_bombs = True
        
        # 무당 특성
        if "field_vision" in effect:
            character.temp_vision_bonus = effect["field_vision"]
            
        if "spirit_protection" in effect:
            character.temp_status_resist += effect["spirit_protection"]
            
        if "exorcism" in effect:
            character.temp_undead_damage = effect["exorcism"]
            
        if "shaman_intuition" in effect:
            character.temp_crit_immunity = effect["shaman_intuition"]
            
        if "spirit_shield" in effect:
            character.temp_death_immunity = True
        
        # 해적 특성
        if "treasure_hunter" in effect:
            character.temp_gold_bonus = effect["treasure_hunter"]
            
        if "sea_rage" in effect:
            # 연속 공격 시 처리 - 전투 시스템에서 처리
            pass
            
        if "pirate_exp" in effect:
            character.temp_exp_bonus += effect["pirate_exp"]
        
        # 사무라이 특성
        if "katana_master" in effect:
            # 검류 무기 사용 시 처리 - 장비 시스템에서 처리
            pass
            
        if "meditation" in effect:
            character.temp_mp_regen_boost = effect["meditation"]
            
        if "honor_oath" in effect:
            character.temp_all_stats_bonus = effect["honor_oath"]
        
        # 드루이드 특성
        if "nature_blessing_heal" in effect:
            # 턴 시작 시 HP/MP 회복 - 턴 시스템에서 처리
            pass
            
        if "nature_heal" in effect:
            # 야외에서 지속 회복 - 필드 시스템에서 처리
            pass
            
        if "seasonal_power" in effect:
            # 랜덤 속성 강화 - 전투 시작 시 처리
            pass
        
        # 철학자 특성
        if "wisdom" in effect:
            character.temp_skill_cost_reduction = effect["wisdom"]
            
        if "logic" in effect:
            character.temp_pattern_analysis = True
            
        if "enlightenment" in effect:
            character.temp_exp_bonus += effect["enlightenment"]
        
        # 시간술사 특성
        if "time_sense" in effect:
            character.temp_future_sight = True
        
        # 연금술사 특성
        if "potion_craft" in effect:
            character.temp_potion_boost = effect["potion_craft"]
            
        if "transmute" in effect:
            character.temp_ignore_resistance = True
            
        if "explosion" in effect:
            character.temp_explosion_boost = effect["explosion"]
            
        if "experiment" in effect:
            character.temp_debuff_duration = effect["experiment"]
            
        if "magic_substance" in effect:
            character.temp_random_element = True
        
        # 검투사 특성
        if "gladiator_skill" in effect:
            character.temp_counter_chance = effect["gladiator_skill"]
            
        if "survival" in effect:
            if character.current_hp <= character.max_hp * 0.3:
                character.temp_dodge_bonus += effect["survival"]
        
        # 기사 특성
        if "honor_guard" in effect:
            character.temp_guard_bonus = effect["honor_guard"]
            
        if "lance_master" in effect:
            # 창류 무기 사용 시 처리
            pass
            
        if "chivalry" in effect:
            character.temp_debuff_resistance = effect["chivalry"]
            
        if "glory_oath" in effect:
            # 파티원 수에 따른 보너스 - 파티 시스템에서 처리
            pass
        
        # 신관 특성
        if "divine_grace" in effect:
            character.temp_crit_negation = effect["divine_grace"]
            
        if "holy_light" in effect:
            character.temp_undead_damage_bonus = effect["holy_light"]
            
        if "heal_mastery" in effect:
            character.temp_heal_boost = effect["heal_mastery"]
        
        # 마검사 특성
        if "magic_sword" in effect:
            character.temp_hybrid_damage = True
            
        if "mana_charge" in effect:
            character.temp_attack_mp_gain = True
            
        if "sword_blast" in effect:
            character.temp_magic_weapon = True
            
        if "dual_element" in effect:
            character.temp_dual_element = True
        
        # 차원술사 특성
        if "dimension_storage" in effect:
            character.temp_unlimited_storage = True
            
        if "space_distortion" in effect:
            character.temp_enemy_accuracy_down = effect["space_distortion"]
        
        # 광전사 특성
        if "berserker_rage" in effect:
            hp_ratio = character.current_hp / character.max_hp
            rage_bonus = (1.0 - hp_ratio) * 1.0  # HP가 낮을수록 강해짐
            character.temp_attack_bonus += character.physical_attack * rage_bonus
            character.temp_speed_bonus += character.speed * rage_bonus
            
        if "pain_ignore" in effect:
            character.temp_status_immunity = True
    
    def trigger_effect(self, character, trigger_type, **kwargs):
        """트리거 효과 발동"""
        if not self.is_active or self.effect_type != "trigger":
            return False
            
        effect = self.effect_value
        
        # 전사 특성
        if trigger_type == "kill" and "kill_damage_stack" in effect:
            character.temp_next_attack_bonus = effect["kill_damage_stack"]
            return True
        
        # 아크메이지 특성
        if trigger_type == "magic_crit" and "magic_chain" in effect:
            # 연쇄 피해 처리
            return True
        
        # 궁수 특성
        if trigger_type == "first_attack" and "first_strike_crit" in effect:
            return True
        
        # 도적 특성
        if trigger_type == "crit" and "crit_bleed" in effect:
            # 출혈 효과 추가
            return True
        
        # 암살자 특성 - 그림자 분신 공격
        if trigger_type == "attack" and "shadow_clone_attack" in effect:
            shadow_count = getattr(character, 'shadow_count', 0)
            if shadow_count > 0:
                character.shadow_count -= 1
                # 추가 공격 데미지 (그림자 1개 소모로 50% 추가 피해)
                character.temp_next_attack_bonus = 0.5
                print(f"👤 {character.name}이(가) 그림자를 소모하여 분신 공격! (남은 그림자: {character.shadow_count})")
                return True
        
        # 성기사 특성
        if trigger_type == "attack" and "heal_on_attack" in effect:
            import random
            if random.random() < effect["heal_on_attack"]:
                # 파티 힐 처리
                return True
        
        if trigger_type == "ally_down" and "justice_rage" in effect:
            character.temp_attack_bonus += character.physical_attack * effect["justice_rage"]
            character.temp_magic_bonus += character.magic_attack * effect["justice_rage"]
            return True
        
        # 시간술사 특성 - 시간 역행
        if trigger_type == "fatal_damage" and "time_rewind" in effect:
            if not hasattr(character, 'time_rewind_used'):
                character.time_rewind_used = 0
            
            if character.time_rewind_used < effect["time_rewind"]:
                # 이전 상태로 복구 (HP 80% 회복)
                character.current_hp = int(character.max_hp * 0.8)
                character.current_mp = int(character.max_mp * 0.8)
                character.time_rewind_used += 1
                print(f"⏰ {character.name}이(가) 시간을 역행하여 상태를 복구했습니다!")
                return True
        
        # 차원술사 특성 - 차원 방벽 (전투 시작)
        if trigger_type == "battle_start" and "dimension_shield" in effect:
            if not hasattr(character, 'dimension_shields'):
                character.dimension_shields = effect["dimension_shield"]
                print(f"🛡️ {character.name}이(가) 차원 방벽을 전개했습니다! ({character.dimension_shields}회 완전 회피)")
                return True
        
        # 차원술사 특성 - 잔상 숙련 (회피 성공 시)
        if trigger_type == "dodge_success" and "afterimage_master" in effect:
            if not hasattr(character, 'afterimage_stacks'):
                character.afterimage_stacks = 0
            character.afterimage_stacks += effect["afterimage_master"]
            print(f"👻 {character.name}이(가) 잔상 스택 {effect['afterimage_master']}개를 획득했습니다! (총 {character.afterimage_stacks}개)")
            return True
        
        # 차원술사 특성 - 차원 이동 (공격 후)
        if trigger_type == "after_attack" and "dimension_step" in effect:
            import random
            if random.random() < effect["dimension_step"]:
                character.temp_next_dodge_guaranteed = True
                print(f"🌀 {character.name}이(가) 차원 이동으로 다음 공격을 자동 회피합니다!")
                return True
        
        # 차원술사 특성 - 차원 균열 (반격 시)
        if trigger_type == "counter_attack" and "dimension_counter" in effect:
            afterimage_stacks = getattr(character, 'afterimage_stacks', 0)
            if afterimage_stacks > 0:
                character.temp_next_attack_multiplier = effect["dimension_counter"]
                character.afterimage_stacks -= 1
                print(f"💥 {character.name}이(가) 잔상을 소모하여 차원 균열 반격! (피해 {effect['dimension_counter']}배)")
                return True
        
        # 철학자 특성 - 사색의 힘 (MP 가득 찰 때)
        if trigger_type == "mp_full" and "contemplation" in effect:
            if not hasattr(character, 'wisdom_stacks'):
                character.wisdom_stacks = 0
            character.wisdom_stacks += 1
            # 지혜 스택당 마법공격력 10% 증가
            character.temp_magic_bonus += character.magic_attack * 0.1
            print(f"🧠 {character.name}이(가) 사색으로 지혜를 얻었습니다! (지혜 스택: {character.wisdom_stacks})")
            return True
        
        # 암흑기사 특성
        if trigger_type == "fatal_damage" and "undying_will" in effect:
            if self.stack_count < effect["undying_will"]:
                character.current_hp = character.max_hp
                character.current_mp = character.max_mp
                self.stack_count += 1
                return True
        
        # 몽크 특성
        if trigger_type == "mp_full" and "chi_burst" in effect:
            character.temp_all_stats_boost = True
            return True
        
        if trigger_type == "attack" and "stun_chance" in effect:
            import random
            if random.random() < effect["stun_chance"]:
                return True
        
        return False
    
    def activate_effect(self, character):
        """액티브 효과 발동 - 완전 구현"""
        if not self.is_active or self.effect_type != "active" or self.cooldown > 0:
            return False
            
        effect = self.effect_value
        activated = False
        
        # 도적 특성 (리메이크) - 은신 관련 제거
        if "stealth_duration" in effect:
            character.stealth_turns = effect["stealth_duration"]
            self.cooldown = 10  # 10턴 쿨다운
            self.max_cooldown = 10
            activated = True
            print(f"✨ {character.name}이(가) 은신 상태에 진입했습니다! (지속: {effect['stealth_duration']}턴)")
        
        # 시간술사 특성 - 시간 정지 (액티브)
        if "time_stop" in effect:
            # 모든 적의 ATB 게이지를 50% 감소
            character.temp_time_stop_effect = True
            self.cooldown = 12
            self.max_cooldown = 12
            activated = True
            print(f"⏰ {character.name}이(가) 시간을 정지시켰습니다! 모든 적의 ATB 게이지 감소!")
        
        # 시간술사 특성 - 시간 가속 (액티브)
        if "time_haste" in effect:
            # 아군 전체의 ATB 게이지를 크게 증가
            character.temp_time_haste_effect = True
            self.cooldown = 8
            self.max_cooldown = 8
            activated = True
            print(f"⚡ {character.name}이(가) 시간을 가속시켰습니다! 아군 전체 ATB 게이지 증가!")
        
        # 차원술사 특성 - 차원 도약 (액티브)
        if "dimension_leap" in effect:
            # 즉시 턴 순서를 맨 앞으로 이동 + 다음 공격 필중
            character.temp_dimension_leap = True
            character.temp_next_attack_guaranteed_hit = True
            self.cooldown = 10
            self.max_cooldown = 10
            activated = True
            print(f"🌀 {character.name}이(가) 차원을 도약하여 시공간을 조작했습니다!")
        
        # 차원술사 특성 - 공간 왜곡 (액티브)
        if "space_warp" in effect:
            # 적 전체에게 혼란 상태 부여 (2턴간 행동 불가)
            character.temp_space_warp_effect = True
            self.cooldown = 15
            self.max_cooldown = 15
            activated = True
            print(f"🌪️ {character.name}이(가) 공간을 왜곡시켰습니다! 적 전체 혼란 상태!")
        
        # 연금술사 특성 - 플라스크 폭발 (액티브)
        if "flask_explosion" in effect:
            # 광역 폭발 공격 (마법 공격력 기반)
            character.temp_flask_explosion_damage = int(character.magic_attack * 2.5)
            character.temp_flask_explosion_targets = "all_enemies"
            self.cooldown = 8
            self.max_cooldown = 8
            activated = True
            print(f"💥 {character.name}이(가) 폭발 플라스크를 던졌습니다! 적 전체 공격!")
        
        # 연금술사 특성 - 원소 변환 (액티브)
        if "elemental_transmute" in effect:
            # 다음 3번의 공격에 모든 속성 동시 부여
            character.temp_multi_element_attacks = 3
            self.cooldown = 12
            self.max_cooldown = 12
            activated = True
            print(f"🔮 {character.name}이(가) 원소를 변환했습니다! 다음 3회 공격에 모든 속성 동시 부여!")
        
        # 철학자 특성 - 철학적 논증 (액티브)
        if "confusion" in effect:
            # 적 전체에게 혼란 상태 부여 + 지혜 스택당 추가 효과
            wisdom_stacks = getattr(character, 'wisdom_stacks', 0)
            confusion_duration = 2 + wisdom_stacks  # 기본 2턴 + 지혜 스택당 1턴
            character.temp_confusion_effect = confusion_duration
            character.temp_confusion_targets = "all_enemies"
            self.cooldown = 10
            self.max_cooldown = 10
            activated = True
            print(f"🤔 {character.name}이(가) 철학적 논증으로 적들을 혼란에 빠뜨렸습니다! ({confusion_duration}턴)")
        
        # 철학자 특성 - 진리 탐구 (액티브)
        if "truth_seeking" in effect:
            # 적의 모든 정보 공개 + 약점 노출
            character.temp_truth_seeking = True
            self.cooldown = 15
            self.max_cooldown = 15
            activated = True
            print(f"🔍 {character.name}이(가) 진리를 탐구하여 적의 본질을 간파했습니다!")
        
        # 암살자 특성 - 그림자 폭발 (궁극기)
        if "shadow_explosion" in effect:
            shadow_count = getattr(character, 'shadow_count', 0)
            
            if shadow_count >= 3:  # 최소 3개 그림자 필요
                # 모든 그림자를 소모하여 강력한 광역 공격
                character.temp_ultimate_damage = character.physical_attack * (1.5 + shadow_count * 0.5)
                character.temp_ultimate_targets = "all_enemies"  # 전체 적 대상
                character.shadow_count = 0  # 모든 그림자 소모
                self.cooldown = 15  # 긴 쿨다운
                self.max_cooldown = 15
                activated = True
                print(f"💥 {character.name}이(가) 모든 그림자({shadow_count}개)를 폭발시켰습니다! 적 전체 공격!")
            else:
                print(f"❌ 그림자가 부족합니다! (필요: 최소 3개, 보유: {shadow_count})")
        
        # 기계공학자 특성 - 자동 포탑
        if "auto_turret" in effect:
            # 포탑 설치 (전투에서 지속 피해 제공) - 물리공격력 비례
            character.temp_turret_damage = int(character.physical_attack * 0.8)  # 물리공격력의 80%
            character.temp_turret_duration = 5
            self.cooldown = 12
            self.max_cooldown = 12
            activated = True
            print(f"🔧 {character.name}이(가) 자동 포탑을 설치했습니다! (지속: 5턴, 턴당 {character.temp_turret_damage} 피해)")
            print("⏸️ [ENTER를 눌러 계속...]")
            input()  # 사용자가 ENTER를 누를 때까지 대기
        
        # 기계공학자 특성 - 오버클럭
        if "overclock" in effect:
            # 모든 능력치 일시 증가
            boost_amount = effect["overclock"]
            character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + int(character.physical_attack * boost_amount)
            character.temp_magic_bonus = getattr(character, 'temp_magic_bonus', 0) + int(character.magic_attack * boost_amount)
            character.temp_speed_bonus = getattr(character, 'temp_speed_bonus', 0) + int(character.speed * boost_amount)
            character.temp_overclock_duration = 3  # 3턴 지속
            self.cooldown = 15
            self.max_cooldown = 15
            activated = True
            print(f"⚡ {character.name}이(가) 오버클럭을 활성화했습니다! 모든 능력치 {int(boost_amount*100)}% 증가! (3턴)")
        
        # 드루이드 특성 - 식물 조종
        if "plant_control" in effect:
            # 적의 이동 제한 및 피해 - 마법공격력 비례
            character.temp_plant_control_damage = int(character.magic_attack * 0.6)  # 마법공격력의 60%
            character.temp_plant_control_duration = 4
            self.cooldown = 10
            self.max_cooldown = 10
            activated = True
            print(f"🌿 {character.name}이(가) 식물을 조종하여 적을 속박합니다! (4턴간 턴당 {character.temp_plant_control_damage} 피해)")
        
        # 드루이드 특성 - 동물 변신
        if "shape_shift" in effect:
            # 이미 전투 시스템에서 처리됨
            self.cooldown = 6
            self.max_cooldown = 6
            activated = True
        
        # 철학자 특성 - 시간 정지
        if "time_stop" in effect:
            # 다음 턴에 2번 행동
            character.temp_extra_turn = True
            self.cooldown = 20
            self.max_cooldown = 20
            activated = True
            print(f"⏰ {character.name}이(가) 시간을 조작합니다! 다음 턴에 2번 행동 가능!")
        
        # 연금술사 특성 - 대폭발
        if "mega_explosion" in effect:
            # 광역 피해 및 자신도 피해
            character.temp_mega_explosion = True
            character.temp_explosion_damage = character.magic_attack * 3
            self.cooldown = 25
            self.max_cooldown = 25
            activated = True
            print(f"💥 {character.name}이(가) 대폭발을 준비합니다! 강력한 광역 피해!")
        
        # 차원술사 특성 - 차원 이동
        if "dimension_teleport" in effect:
            # 회피율 100% 및 반격 기회
            character.temp_dimension_dodge = True
            character.temp_dimension_duration = 2
            self.cooldown = 18
            self.max_cooldown = 18
            activated = True
            print(f"🌀 {character.name}이(가) 차원을 이동합니다! 2턴간 모든 공격 회피!")
        
        # 차원술사 특성 - 차원 균열
        if "dimension_rift" in effect:
            # 마법공격력 비례 고정 피해 (보스는 50% 감소)
            dimension_damage = int(character.magic_attack * 2.5)  # 마법공격력의 250%
            character.temp_dimension_rift_damage = dimension_damage
            character.temp_dimension_rift_duration = 1  # 즉시 적용
            self.cooldown = 25
            self.max_cooldown = 25
            activated = True
            print(f"🌌 {character.name}이(가) 차원 균열을 생성합니다! 강력한 공간 피해! ({dimension_damage} 피해)")
        
        # 시간술사 특성 - 시간 역행
        if "time_rewind" in effect:
            # HP/MP 완전 회복 및 모든 쿨다운 초기화
            character.current_hp = character.max_hp
            character.current_mp = character.max_mp
            # 다른 특성들의 쿨다운 초기화
            for trait in character.traits:
                if trait != self:  # 자신은 제외
                    trait.cooldown = 0
            self.cooldown = 30  # 매우 긴 쿨다운
            self.max_cooldown = 30
            activated = True
            print(f"⏪ {character.name}이(가) 시간을 역행시킵니다! HP/MP 완전 회복 및 모든 쿨다운 초기화!")
        
        # 광전사 특성 - 광전사 모드
        if "berserker_mode" in effect:
            # 공격력 대폭 증가, 방어력 감소, 상태이상 무시
            character.temp_berserker_attack = int(character.physical_attack * 1.5)
            character.temp_berserker_defense = int(character.physical_defense * 0.5)
            character.temp_status_immunity = True
            character.temp_berserker_duration = 5
            self.cooldown = 20
            self.max_cooldown = 20
            activated = True
            print(f"😤 {character.name}이(가) 광전사 모드에 돌입! 공격력 150%, 방어력 50%, 상태이상 무시! (5턴)")
        
        # 성공적으로 활성화된 경우에만 쿨다운 적용
        return activated
    
    def update_cooldown(self):
        """쿨다운 업데이트 - 개선된 버전"""
        if self.cooldown > 0:
            self.cooldown -= 1
            return True  # 쿨다운 중
        return False  # 쿨다운 완료
    
    def update_duration_effects(self, character):
        """지속 효과 업데이트"""
        updated_effects = []
        
        # 오버클럭 지속시간 관리
        if hasattr(character, 'temp_overclock_duration') and character.temp_overclock_duration > 0:
            character.temp_overclock_duration -= 1
            if character.temp_overclock_duration <= 0:
                # 오버클럭 효과 제거
                character.temp_attack_bonus = max(0, getattr(character, 'temp_attack_bonus', 0) - int(character.physical_attack * 0.5))
                character.temp_magic_bonus = max(0, getattr(character, 'temp_magic_bonus', 0) - int(character.magic_attack * 0.5))
                character.temp_speed_bonus = max(0, getattr(character, 'temp_speed_bonus', 0) - int(character.speed * 0.5))
                updated_effects.append("오버클럭 효과 종료")
        
        # 자동 포탑 지속시간 관리
        if hasattr(character, 'temp_turret_duration') and character.temp_turret_duration > 0:
            character.temp_turret_duration -= 1
            if character.temp_turret_duration <= 0:
                character.temp_turret_damage = 0
                updated_effects.append("자동 포탑 해제")
        
        # 식물 조종 지속시간 관리
        if hasattr(character, 'temp_plant_control_duration') and character.temp_plant_control_duration > 0:
            character.temp_plant_control_duration -= 1
            if character.temp_plant_control_duration <= 0:
                character.temp_plant_control_damage = 0
                updated_effects.append("식물 조종 효과 종료")
        
        # 차원 이동 지속시간 관리
        if hasattr(character, 'temp_dimension_duration') and character.temp_dimension_duration > 0:
            character.temp_dimension_duration -= 1
            if character.temp_dimension_duration <= 0:
                character.temp_dimension_dodge = False
                updated_effects.append("차원 이동 효과 종료")
        
        # 광전사 모드 지속시간 관리
        if hasattr(character, 'temp_berserker_duration') and character.temp_berserker_duration > 0:
            character.temp_berserker_duration -= 1
            if character.temp_berserker_duration <= 0:
                character.temp_berserker_attack = 0
                character.temp_berserker_defense = 0
                character.temp_status_immunity = False
                updated_effects.append("광전사 모드 종료")
        
        # 은신 지속시간 관리
        if hasattr(character, 'stealth_turns') and character.stealth_turns > 0:
            character.stealth_turns -= 1
            if character.stealth_turns <= 0:
                updated_effects.append("은신 효과 종료")
        
        # 적 명중률 감소 지속시간 관리
        if hasattr(character, 'temp_enemy_accuracy_duration') and character.temp_enemy_accuracy_duration > 0:
            character.temp_enemy_accuracy_duration -= 1
            if character.temp_enemy_accuracy_duration <= 0:
                character.temp_enemy_accuracy_down = 0
                updated_effects.append("연막탄 효과 종료")
        
        return updated_effects
    
    def reset_temp_effects(self, character):
        """임시 효과 초기화"""
        character.temp_attack_bonus = 0
        character.temp_defense_bonus = 0
        character.temp_magic_bonus = 0
        character.temp_speed_bonus = 0
        character.temp_crit_bonus = 0
        character.temp_dodge_bonus = 0
        character.temp_exp_bonus = 0
        character.temp_resistance_bonus = 0
        character.temp_penetration = 0
        character.temp_life_steal = 0
        character.temp_fear_aura = 0
        character.temp_dark_pulse = 0
        character.temp_status_resist = 0
        character.temp_treasure_bonus = 0
        character.temp_poison_chance = 0
        character.temp_undead_resistance = 0
        character.temp_protection_bonus = 0
        character.temp_next_attack_bonus = 0
        character.item_no_turn_cost = False
        character.temp_holy_damage = False
        character.temp_all_stats_boost = False
        character.stealth_turns = 0
        
        # 추가 효과들
        character.temp_fire_damage = False
        character.temp_physical_resistance = 0
        character.temp_debuff_resist = 0
        character.temp_weapon_mastery = 0
        character.temp_weapon_immunity = False
        character.temp_elemental_boost = 0
        character.temp_mana_efficiency = 0
        character.temp_first_strike = False
        character.temp_poison_weapon = False
        character.temp_equipment_boost = 0
        character.temp_infinite_bombs = False
        character.temp_vision_bonus = 0
        character.temp_undead_damage = 0
        character.temp_crit_immunity = 0
        character.temp_death_immunity = False
        character.temp_gold_bonus = 0
        character.temp_mp_regen_boost = 0
        character.temp_all_stats_bonus = 0
        character.temp_skill_cost_reduction = 0
        character.temp_pattern_analysis = False
        character.temp_future_sight = False
        character.temp_potion_boost = 0
        character.temp_ignore_resistance = False
        character.temp_explosion_boost = 0
        character.temp_debuff_duration = 0
        character.temp_random_element = False
        character.temp_counter_chance = 0
        character.temp_guard_bonus = 0
        character.temp_debuff_resistance = 0
        character.temp_crit_negation = 0
        character.temp_undead_damage_bonus = 0
        character.temp_heal_boost = 0
        character.temp_hybrid_damage = False
        character.temp_attack_mp_gain = False
        character.temp_magic_weapon = False
        character.temp_dual_element = False
        character.temp_unlimited_storage = False
        character.temp_enemy_accuracy_down = 0
        character.temp_status_immunity = False


class CharacterClassManager:
    """캐릭터 클래스별 특성 관리자"""
    
    @staticmethod
    def unlock_all_classes():
        """모든 직업 클래스를 해금합니다"""
        return game_config.get_available_classes()
    
    @staticmethod
    def get_all_available_classes() -> List[str]:
        """사용 가능한 모든 직업 클래스 목록을 반환합니다"""
        return game_config.get_available_classes()
    
    @staticmethod
    def is_class_unlocked(character_class: str) -> bool:
        """특정 직업이 해금되었는지 확인합니다"""
        return game_config.is_class_unlocked(character_class)
    
    @staticmethod
    def get_class_traits(character_class: str) -> List[CharacterTrait]:
        """클래스별 고유 특성 반환 (5개씩) - 중복 제거 및 완전 통합"""
        trait_sets = {
            # === 전사계 - 적응형 시스템과 균형 유지 ===
            "전사": [
                CharacterTrait("적응형 무술", "전투 중 자세 변경 시 다음 공격 위력 30% 증가", "trigger", {"stance_change_boost": 1.3}),
                CharacterTrait("전장의 지배자", "같은 자세 유지 시 턴마다 능력치 누적 증가 (턴당 +5%, 최대 35%)", "passive", {"stance_mastery_stack": {"growth_per_turn": 0.05, "max_bonus": 0.35}}),
                CharacterTrait("불굴의 의지", "모든 자세에서 매 턴 HP 8% 회복", "passive", {"universal_regeneration": 0.08}),
                CharacterTrait("전투 본능", "자세 변경 스킬 MP 소모 없음", "passive", {"stance_change_no_mp": True}),
                CharacterTrait("6단계 완전체", "6가지 자세 완전 숙달: 모든 자세에서 특화 보너스 획득 (공격:공격력+20%, 방어:방어력+25%, 균형:올스탯+12%, 광전사:크리+15%, 수호자:회복+30%, 신속:속도+35%)", "passive", {"stance_mastery": True})
            ],
            
            "성기사": [
                CharacterTrait("성역의 수호자", "성역 지속시간 50% 증가", "passive", {"sanctuary_duration": 1.5}),
                CharacterTrait("축복의 빛", "버프 상태 아군 수에 따라 성역 생성 확률 증가", "trigger", {"blessing_sanctuary": True}),
                CharacterTrait("신성한 힘", "성역 1개당 치유 효과 15% 증가", "passive", {"holy_healing": 0.15}),
                CharacterTrait("정의의 심판", "성역이 5개 이상일 때 모든 공격에 성속성 추가", "trigger", {"divine_judgment": 5}),
                CharacterTrait("천사의 가호", "성역 효과 범위 2배 확장", "passive", {"sanctuary_range": 2.0})
            ],
            
            "암흑기사": [
                CharacterTrait("어둠의 권능", "흡수 스택 최대치 +25% (HP의 100%까지)", "passive", {"absorption_limit": 1.25}),
                CharacterTrait("생명력 지배", "흡수 스택으로 회복 시 효율 30% 증가", "passive", {"absorption_efficiency": 1.3}),
                CharacterTrait("어둠의 오라", "적이 많을수록 지속 피해 증가", "passive", {"dark_aura_scale": True}),
                CharacterTrait("불사의 계약", "흡수 스택이 50% 이상일 때 디버프 면역", "trigger", {"undead_immunity": 0.5}),
                CharacterTrait("어둠의 군주", "궁극기 사용 시 모든 적에게 공포 부여", "trigger", {"dark_lord_fear": True})
            ],
            
            "기사": [
                CharacterTrait("의무의 수호자", "아군 보호 시 의무 스택 추가 획득", "trigger", {"duty_protection": True}),
                CharacterTrait("기사도 정신", "의무 스택 3개 이상일 때 모든 능력치 20% 증가", "passive", {"chivalry_boost": 0.2}),
                CharacterTrait("불굴의 방어", "의무 스택 5개일 때 다음 치명상 무효화", "trigger", {"immortal_duty": 5}),
                CharacterTrait("수호 본능", "파티원 HP 30% 이하일 때 자동으로 보호", "trigger", {"auto_protect": 0.3}),
                CharacterTrait("기사의 맹세", "아군이 죽을 때 모든 의무 스택 회복", "trigger", {"oath_recovery": True})
            ],
            
            "용기사": [
                CharacterTrait("표식 달인", "표식 부여 확률 30% 증가", "passive", {"mark_mastery": 0.3}),
                CharacterTrait("도약의 숙련자", "도약 공격 시 무적 시간 50% 증가", "passive", {"leap_mastery": 1.5}),
                CharacterTrait("용의 혈통", "표식 중첩 속도 25% 증가", "passive", {"mark_speed": 1.25}),
                CharacterTrait("드래곤 하트", "표식이 3개 이상일 때 화염 저항 50% 증가", "trigger", {"dragon_resistance": 0.5}),
                CharacterTrait("용왕의 권능", "모든 표식 폭발 시 추가 화염 피해", "trigger", {"dragon_explosion": True})
            ],
            
            # === 원거리계 ===
            "궁수": [
                CharacterTrait("정밀 사격", "크리티컬 확률 25% 증가", "passive", {"crit_chance_bonus": 0.25}),
                CharacterTrait("원거리 숙련", "첫 공격 시 항상 크리티컬", "trigger", {"first_strike_crit": True}),
                CharacterTrait("민첩한 몸놀림", "회피 확률 20% 증가", "passive", {"dodge_bonus": 0.2}),
                CharacterTrait("사냥꾼의 직감", "적의 약점을 간파해 방어력 무시 확률 15%", "passive", {"weakness_detect": 0.15}),
                CharacterTrait("바람의 가호", "이동 시 다음 공격의 명중률과 피해량 15% 증가", "passive", {"movement_bonus": 1.15})
            ],
            
            # === 마법계 ===
            "아크메이지": [
                CharacterTrait("원소 순환 마스터", "동일 원소 2회만으로도 자동 발동", "passive", {"element_cycle_fast": 2}),
                CharacterTrait("마법 연구자", "원소 카운트 지속시간 50% 증가", "passive", {"element_duration": 1.5}),
                CharacterTrait("원소 친화", "모든 원소 마법 위력 20% 증가", "passive", {"elemental_mastery": 0.2}),
                CharacterTrait("대마법사", "원소 대폭발 재사용 대기시간 50% 감소", "passive", {"ultimate_cooldown": 0.5}),
                CharacterTrait("원소의 현자", "원소 3개 축적 시 모든 원소 저항 25% 증가", "trigger", {"elemental_sage": 0.25})
            ],
            
            "정령술사": [
                CharacterTrait("정령 친화", "모든 속성 마법 위력 25% 증가", "passive", {"elemental_affinity": 0.25}),
                CharacterTrait("자연의 축복", "턴 시작 시 MP 자동 회복", "passive", {"nature_blessing": True}),
                CharacterTrait("원소 조화", "서로 다른 속성 연계 시 추가 피해", "trigger", {"element_combo": True}),
                CharacterTrait("마나 순환", "마법 사용 시 50% 확률로 MP 소모량 절반", "passive", {"mana_cycle": 0.5}),
                CharacterTrait("원소 폭발", "마법 크리티컬 시 광역 피해", "trigger", {"elemental_blast": True})
            ],
            
            "네크로맨서": [
                CharacterTrait("어둠의 계약", "적 처치 시 MP 회복량 2배", "trigger", {"dark_pact_mp": 2.0}),
                CharacterTrait("생명력 흡수", "적에게 피해를 줄 때 HP와 MP 동시 회복", "passive", {"life_mana_drain": True}),
                CharacterTrait("저주술", "공격 시 25% 확률로 적에게 저주 부여", "trigger", {"curse_chance": 0.25}),
                CharacterTrait("죽음의 오라", "주변 적들의 회복 효과 50% 감소", "passive", {"anti_heal_aura": 0.5}),
                CharacterTrait("영혼 흡수", "적 처치 시 최대 MP 일시 증가", "trigger", {"soul_harvest": True})
            ],
            
            "시간술사": [
                CharacterTrait("시간 파동", "ATB 게이지 감소량 마스터리", "passive", {"time_mastery": True}),
                CharacterTrait("시간 지연", "적 ATB 지연 효과 강화", "passive", {"time_delay_boost": 1.5}),
                CharacterTrait("시간 가속", "아군 ATB 가속 효과 강화", "passive", {"time_accel_boost": 1.5}),
                CharacterTrait("시간의 달인", "모든 시간 조작 스킬 25% 강화", "passive", {"temporal_mastery": 0.25}),
                CharacterTrait("시공 왜곡", "궁극기 시 모든 적 5턴 느려짐", "trigger", {"spacetime_distort": 5})
            ],
            
            "연금술사": [
                CharacterTrait("폭발 연구", "폭발 계열 스킬 위력 40% 증가", "passive", {"explosion": 0.4}),
                CharacterTrait("플라스크 달인", "공격 시 25% 확률로 폭발 효과 (마법공격력 2.5배)", "trigger", {"flask_mastery": 0.25}),
                CharacterTrait("원소 변환", "공격 시 랜덤한 속성 효과 부여", "passive", {"elemental_transmute": True}),
                CharacterTrait("연금 숙련", "모든 마법 스킬 MP 소모량 20% 감소", "passive", {"mana_efficiency": 0.8}),
                CharacterTrait("생명 연성", "체력 회복 효과 50% 증가", "passive", {"healing_boost": 1.5})
            ],
            
            "차원술사": [
                CharacterTrait("차원 방벽", "전투 시작 시 보호막 자동 생성", "passive", {"dimension_barrier": True}),
                CharacterTrait("잔상 숙련", "회피 성공 시 다음 공격 치명타 확정", "trigger", {"afterimage_mastery": True}),
                CharacterTrait("차원 도약", "공격 받을 때 50% 확률로 완전 회피", "passive", {"dimension_dodge": 0.5}),
                CharacterTrait("공간 왜곡", "적의 정확도 30% 감소", "passive", {"space_distortion": 0.3}),
                CharacterTrait("차원 귀환", "HP 30% 이하 시 즉시 회복 + 무적 1턴", "trigger", {"dimension_return": True})
            ],
            
            # === 하이브리드계 ===
            "검성": [
                CharacterTrait("검기 집중", "BRV 공격 시 20% 확률로 검기 스택 2개 획득", "trigger", {"sword_aura_double": 0.2}),
                CharacterTrait("일섬의 달인", "검기 스택 소모 시 ATB 환급량 20% 증가", "passive", {"atb_refund_boost": 0.2}),
                CharacterTrait("검의 이치", "검기 스택 최대치 +1 (최대 3스택)", "passive", {"max_sword_aura": 3}),
                CharacterTrait("명경지수", "HP 50% 이상일 때 크리티컬 확률 25% 증가", "passive", {"high_hp_crit": 0.25}),
                CharacterTrait("검신의 축복", "검기 스택이 최대일 때 모든 공격 크리티컬", "trigger", {"max_stack_crit": True})
            ],
            
            "검투사": [
                CharacterTrait("투기장의 경험", "적 처치 시 능력치 상승폭 25% 증가", "passive", {"kill_stack_boost": 0.25}),
                CharacterTrait("패링 마스터", "패링 시 반격 피해 120% 증가", "passive", {"parry_damage_boost": 1.2}),
                CharacterTrait("생존 본능", "HP 30% 이하일 때 패링 지속시간 연장", "trigger", {"survival_parry_duration": 3.0}),
                CharacterTrait("투사의 긍지", "처치 스택 3개 이상일 때 디버프 면역", "trigger", {"gladiator_immunity": 3}),
                CharacterTrait("콜로세움의 영웅", "적 처치 시 100% 확률로 즉시 행동", "trigger", {"heroic_action": 1.0})
            ],
            
            "광전사": [
                CharacterTrait("피의 갈증", "HP 소모량 15% 감소, 흡혈 효과 25% 증가", "passive", {"blood_efficiency": {"hp_cost": 0.85, "lifesteal": 1.25}}),
                CharacterTrait("광기의 힘", "HP가 낮을수록 보호막 생성량 증가", "passive", {"rage_shield": True}),
                CharacterTrait("불굴의 의지", "HP 15% 이하일 때 받는 피해 50% 감소", "trigger", {"last_stand": 0.5}),
                CharacterTrait("혈투의 광기", "HP가 낮을수록 공격력과 치명타율 증가", "passive", {"hp_based_rage": True}),
                CharacterTrait("최후의 일격", "HP 10% 이하일 때 다음 공격이 치명타 + 200% 추가 피해", "trigger", {"last_strike": {"threshold": 0.1, "damage_multiplier": 3.0}})
            ],
            
            "마검사": [
                CharacterTrait("마검 일체", "물리와 마법 공격력 동시 적용", "passive", {"magic_sword": True}),
                CharacterTrait("마력 충전", "공격할 때마다 MP 회복", "passive", {"mana_charge": True}),
                CharacterTrait("검기 폭발", "검 공격에 마법 피해 추가", "passive", {"sword_blast": True}),
                CharacterTrait("이중 속성", "두 가지 속성 동시 공격", "passive", {"dual_element": True}),
                CharacterTrait("마검 오의", "궁극기 사용 시 모든 적에게 피해", "trigger", {"mystic_art": True})
            ],
            
            "암살자": [
                CharacterTrait("그림자 조작", "전투 시작 시 그림자 3개 생성", "passive", {"shadow_generation": 3}),
                CharacterTrait("그림자 강화", "그림자 1개당 공격력 15% 증가", "passive", {"shadow_power": 0.15}),
                CharacterTrait("그림자 분신", "그림자 소모로 추가 공격 가능", "trigger", {"shadow_clone_attack": True}),
                CharacterTrait("그림자 방어", "피격 시 그림자 1개 소모로 50% 피해 감소", "passive", {"shadow_defense": {"reduction": 0.5}}),
                CharacterTrait("그림자 숙련", "그림자 개수에 비례하여 크리티컬 확률 최대 40%, 회피율 최대 30% 증가", "passive", {"shadow_mastery": {"crit_per_shadow": 8, "dodge_per_shadow": 6, "max_shadows": 5}})
            ],
            
            # === 서포터계 ===
            "바드": [
                CharacterTrait("전투 노래", "파티원들의 공격력 15% 증가", "passive", {"party_damage_boost": 0.15}),
                CharacterTrait("치유의 선율", "턴 종료 시 파티 전체 소량 회복", "passive", {"turn_heal": True}),
                CharacterTrait("용기의 찬송", "파티원들의 크리티컬 확률 10% 증가", "passive", {"party_crit_boost": 0.1}),
                CharacterTrait("마법 해제", "적의 버프를 무효화하는 확률 25%", "trigger", {"dispel_chance": 0.25}),
                CharacterTrait("영감의 리듬", "스킬 사용 시 아군의 MP 회복", "trigger", {"inspire_mp": True})
            ],
            
            "신관": [
                CharacterTrait("신의 가호", "치명타 무효화 확률 20%", "passive", {"divine_grace": 0.2}),
                CharacterTrait("성스러운 빛", "언데드에게 2배 피해", "passive", {"holy_light": 2.0}),
                CharacterTrait("치유 특화", "모든 회복 효과 50% 증가", "passive", {"heal_mastery": 0.5}),
                CharacterTrait("축복의 오라", "파티 전체 디버프 저항 30% 증가", "passive", {"blessing_aura": 0.3}),
                CharacterTrait("신탁", "랜덤하게 강력한 기적 발생", "trigger", {"oracle": True})
            ],
            
            "몽크": [
                CharacterTrait("내공 순환", "MP가 가득 찰 때마다 모든 능력치 일시 증가", "trigger", {"chi_burst": True}),
                CharacterTrait("연타 숙련", "연속 공격 시마다 피해량 누적 증가", "passive", {"combo_multiplier": 0.1}),
                CharacterTrait("정신 수양", "상태이상 저항 50% 증가", "passive", {"status_resist": 0.5}),
                CharacterTrait("기절 공격", "일정 확률로 적을 기절시켜 1턴 행동 불가", "trigger", {"stun_chance": 0.2}),
                CharacterTrait("참선의 깨달음", "전투 중 매 5턴마다 MP 완전 회복", "passive", {"meditation_recovery": 5})
            ],
            
            # === 특수 직업들 ===
            "도적": [
                CharacterTrait("독술 지배", "모든 공격에 독 효과 부여, 독 피해량 50% 증가", "passive", {"poison_mastery": True, "poison_boost": 1.5}),
                CharacterTrait("침묵 술", "공격 시 30% 확률로 적의 스킬 봉인 2턴", "trigger", {"silence_chance": 0.3}),
                CharacterTrait("독 촉진", "독에 걸린 적 공격 시 남은 독 피해의 25%를 즉시 피해", "trigger", {"poison_trigger": 0.25}),
                CharacterTrait("맹독 면역", "모든 독과 상태이상에 완전 면역, 독 공격 받을 때 반사", "passive", {"poison_immunity": True, "poison_reflect": True}),
                CharacterTrait("독왕의 권능", "적이 독으로 죽을 때 주변 적들에게 독 전파", "trigger", {"poison_spread": True})
            ],
            
            "기계공학자": [
                CharacterTrait("기계 정밀", "전투 시작 시 정밀도 향상 (명중률과 크리티컬률 20% 증가)", "passive", {"machine_precision": {"accuracy": 0.2, "crit": 0.2}}),
                CharacterTrait("기계 정비", "전투 후 5턴간 장비 효과 10% 증가 (중첩 가능)", "trigger", {"machine_maintenance": {"bonus": 0.1, "duration": 5}}),
                CharacterTrait("폭탄 제작", "소모품 폭탄 무한 사용", "passive", {"bomb_craft": True}),
                CharacterTrait("강화 장비", "모든 장비 효과 20% 증가", "passive", {"gear_enhance": 0.2}),
                CharacterTrait("기계 숙련", "공격력과 마법공격력 15% 증가, MP 회복량 50% 증가", "passive", {"machine_mastery": {"attack_boost": 0.15, "magic_attack_boost": 0.15, "mp_recovery": 0.5}})
            ],
            
            "무당": [
                CharacterTrait("시야 확장", "필드 시야 범위 +1", "passive", {"field_vision": 1}),
                CharacterTrait("정령 가호", "상태이상 저항 40% 증가", "passive", {"spirit_protection": 0.4}),
                CharacterTrait("악령 퇴치", "언데드에게 추가 피해 50%", "passive", {"exorcism": 0.5}),
                CharacterTrait("무당의 직감", "크리티컬 받을 확률 30% 감소", "passive", {"shaman_intuition": 0.3}),
                CharacterTrait("영적 보호", "즉사 공격 무효", "passive", {"spirit_shield": True})
            ],
            
            "해적": [
                CharacterTrait("보물 사냥꾼", "골드 획득량 30% 증가", "passive", {"treasure_hunter": 0.3}),
                CharacterTrait("이도류 전투", "공격 시 30% 확률로 2회 공격", "trigger", {"dual_strike": 0.3}),
                CharacterTrait("바다의 분노", "연속 공격 시 피해량 누적 증가", "passive", {"sea_rage": True}),
                CharacterTrait("럭키 스트라이크", "크리티컬 시 20% 확률로 골드 추가 획득", "trigger", {"lucky_strike": 0.2}),
                CharacterTrait("해적의 경험", "전투 후 경험치 15% 추가 획득", "passive", {"pirate_exp": 0.15})
            ],
            
            "사무라이": [
                CharacterTrait("일격필살", "HP 25% 이하일 때 크리티컬 확률 50% 증가", "passive", {"iai_mastery": 0.5}),
                CharacterTrait("카타나 숙련", "검류 무기 공격력 40% 증가", "passive", {"katana_master": 0.4}),
                CharacterTrait("참선", "전투 외 MP 회복 속도 2배", "passive", {"meditation": 2.0}),
                CharacterTrait("무사도", "HP 10% 이하일 때 모든 공격 크리티컬", "trigger", {"bushido": True}),
                CharacterTrait("명예의 맹세", "디버프 무효, 모든 능력치 15% 증가", "passive", {"honor_oath": 0.15})
            ],
            
            "드루이드": [
                CharacterTrait("자연의 가호", "턴 시작 시 HP/MP 소량 회복", "passive", {"nature_blessing_heal": True}),
                CharacterTrait("자연 치유", "야외에서 지속적인 HP 회복", "passive", {"nature_heal": True}),
                CharacterTrait("식물 친화", "적들의 속도 20% 감소 오라", "passive", {"plant_mastery": {"speed_debuff": 0.2}}),
                CharacterTrait("야생 본능", "공격력 30%, 방어력 30%, 회피율 25% 중 하나가 랜덤하게 증가", "passive", {"wild_instinct": True}),
                CharacterTrait("계절의 힘", "전투마다 랜덤 속성 강화", "passive", {"seasonal_power": True})
            ],
            
            "철학자": [
                CharacterTrait("현자의 지혜", "모든 스킬 MP 소모량 20% 감소", "passive", {"wisdom": 0.2}),
                CharacterTrait("논리적 사고", "적의 패턴 분석으로 회피율 15% 증가", "passive", {"logic": True}),
                CharacterTrait("깨달음", "경험치 획득량 25% 증가", "passive", {"enlightenment": 0.25}),
                CharacterTrait("사색의 힘", "MP 가득 찰 때마다 지혜 스택 증가 (마법공격력 10% 증가)", "trigger", {"contemplation": True}),
                CharacterTrait("철학적 통찰", "적 전체의 능력치 10% 감소 오라", "passive", {"philosophical_insight": 0.1})
            ]
        }
        


        
        return trait_sets.get(character_class, [])
    
    @staticmethod
    def get_trait_sfx_mapping(trait_name: str) -> str:
        """특성별 SFX 매핑 - 특성 발동 시 재생할 사운드"""
        trait_sfx = {
            "방패 강타": "sword_hit",
            "파괴의 일격": "critical_hit",
            "검기 집중": "magic_cast",
            "일섬의 달인": "critical_hit",
            "검의 이치": "haste",
            "명경지수": "heal",
            "검신의 축복": "protect",
            "그림자 조작": "magic_cast",
            "그림자 강화": "berserk",
            "그림자 분신": "teleport",
            "그림자 숙련": "haste",
            "그림자 방어": "protect",
            "기계 정밀": "machine_start",
            "기계 숙련": "power_up",
            "플라스크 달인": "explosion",
            "원소 변환": "magic_cast",
            "축복의 오라": "holy_blessing",
            "철학적 통찰": "wisdom_aura",
            "식물 친화": "nature_call",
            "야생 본능": "wild_instinct",
            "마력 파동": "magic_cast",
            "마력 폭발": "fire3",
            "원소 순환 마스터": "magic_cast",
            "원소 친화": "haste",
            "원소의 현자": "limit_break",
            "정령 친화": "heal",
            "자연의 축복": "protect",
            "삼연사": "gun_hit",
            "관통사격": "gun_critical",
            "정밀 사격": "gun_hit",
            "민첩한 몸놀림": "haste",
            "바람의 가호": "protect",
            "독술 지배": "poison",
            "독 촉진": "poison",
            "맹독 면역": "protect",
            "독왕의 권능": "limit_break",
            "저주술": "slow",
            "신성한 가호": "protect",
            "치유의 빛": "heal",
            "정의의 분노": "thunder3",
            "축복받은 무기": "haste",
            "수호의 맹세": "protect",
            "성역의 수호자": "shell",
            "천사의 가호": "heal3",
            "생명 흡수": "magic_cast",
            "어둠의 계약": "dark3",
            "공포 오라": "slow",
            "불사의 의지": "protect",
            "어둠 조작": "dark2",
            "어둠의 권능": "dark3",
            "어둠의 군주": "limit_break",
            "용의 숨결": "fire3",
            "용의 분노": "fire2",
            "드래곤 하트": "protect",
            "용왕의 권능": "limit_break",
            "표식 달인": "haste",
        }
        
        return trait_sfx.get(trait_name, "trait_activate")  # 기본 SFX
    
    @staticmethod
    def get_trait_activation_conditions(trait_name: str) -> Dict[str, Any]:
        """특성별 발동 조건 및 효과 상세 정보"""
        conditions = {
            # === 검성 특성 조건 ===
            "검기 집중": {
                "condition": "BRV 공격 시",
                "probability": 0.2,
                "effect_duration": 0,
                "stack_limit": 2,
                "description": "BRV 공격 시 20% 확률로 검기 스택 2개 획득"
            },
            "일섬의 달인": {
                "condition": "검기 스택 소모 시",
                "probability": 1.0,
                "effect_duration": 0,
                "atb_refund": 0.2,
                "description": "검기 스택 소모 시 ATB 환급량 20% 증가"
            },
            
            # === 암살자 특성 조건 ===
            "그림자 조작": {
                "condition": "전투 시작 시",
                "probability": 1.0,
                "effect_duration": -1,
                "initial_shadows": 3,
                "description": "전투 시작 시 그림자 3개 생성"
            },
            "그림자 강화": {
                "condition": "그림자 보유 시",
                "probability": 1.0,
                "effect_duration": -1,
                "attack_bonus_per_shadow": 0.15,
                "description": "그림자 1개당 공격력 15% 증가"
            },
            
            # === 검투사 특성 조건 ===
            "투기장의 경험": {
                "condition": "적 처치 시",
                "probability": 1.0,
                "effect_duration": -1,
                "stat_boost": 0.25,
                "description": "적 처치 시 능력치 상승폭 25% 증가"
            },
            "패링 마스터": {
                "condition": "패링 시도 시",
                "probability": 1.0,
                "effect_duration": 0,
                "parry_damage_boost": 1.2,
                "description": "패링 시 반격 피해 120% 증가"
            },
            
            # === 광전사 특성 조건 ===
            "피의 갈증": {
                "condition": "HP 소모 스킬 사용 시",
                "probability": 1.0,
                "effect_duration": 0,
                "hp_cost_reduction": 0.15,
                "lifesteal_boost": 0.25,
                "description": "HP 소모량 15% 감소, 흡혈 효과 25% 증가"
            },
            "광기의 힘": {
                "condition": "HP 비율에 따라",
                "probability": 1.0,
                "effect_duration": -1,
                "shield_scaling": True,
                "description": "HP가 낮을수록 보호막 생성량 증가"
            },
            
            # === 성기사 특성 조건 ===
            "성역의 수호자": {
                "condition": "성역 생성 시",
                "probability": 1.0,
                "effect_duration": 1.5,
                "duration_multiplier": 1.5,
                "description": "성역 지속시간 50% 증가"
            },
            "축복의 빛": {
                "condition": "버프 상태 아군 수에 따라",
                "probability": "variable",
                "effect_duration": 0,
                "sanctuary_chance_boost": True,
                "description": "버프 상태 아군 수에 따라 성역 생성 확률 증가"
            },
            
            # === 아크메이지 특성 조건 ===
            "원소 순환 마스터": {
                "condition": "원소 마법 사용 시",
                "probability": 1.0,
                "effect_duration": 0,
                "cycle_requirement": 2,
                "description": "동일 원소 2회만으로도 자동 발동"
            },
            "원소의 현자": {
                "condition": "원소 3개 축적 시",
                "probability": 1.0,
                "effect_duration": -1,
                "resistance_bonus": 0.25,
                "description": "원소 3개 축적 시 모든 원소 저항 25% 증가"
            },
            
            # === 새로 추가된 특성 조건 ===
            "그림자 숙련": {
                "condition": "그림자 보유 시",
                "probability": 1.0,
                "effect_duration": -1,
                "crit_per_shadow": 8,
                "dodge_per_shadow": 6,
                "max_bonus": {"crit": 40, "dodge": 30},
                "description": "그림자 개수에 비례하여 크리티컬과 회피 증가"
            },
            "기계 정밀": {
                "condition": "전투 시작 시",
                "probability": 1.0,
                "effect_duration": -1,
                "accuracy_bonus": 0.2,
                "crit_bonus": 0.2,
                "description": "전투 시작 시 정밀도 향상"
            },
            "기계 숙련": {
                "condition": "지속 효과",
                "probability": 1.0,
                "effect_duration": -1,
                "attack_boost": 0.15,
                "magic_attack_boost": 0.15,
                "mp_recovery": 0.5,
                "description": "공격력과 마법공격력 15% 증가, MP 회복량 50% 증가"
            },
            "플라스크 달인": {
                "condition": "공격 시",
                "probability": 0.25,
                "effect_duration": 0,
                "explosion_multiplier": 2.5,
                "description": "공격 시 25% 확률로 폭발 효과"
            },
            "원소 변환": {
                "condition": "공격 시",
                "probability": 1.0,
                "effect_duration": 0,
                "element_types": ["fire", "ice", "lightning", "earth"],
                "description": "공격 시 랜덤한 속성 효과 부여"
            },
            "축복의 오라": {
                "condition": "지속 효과",
                "probability": 1.0,
                "effect_duration": -1,
                "debuff_resistance": 0.3,
                "description": "파티 전체 디버프 저항 30% 증가"
            },
            "식물 친화": {
                "condition": "지속 효과",
                "probability": 1.0,
                "effect_duration": -1,
                "speed_debuff": 0.2,
                "description": "적들의 속도 20% 감소 오라"
            },
            "야생 본능": {
                "condition": "전투 시작 시",
                "probability": 1.0,
                "effect_duration": -1,
                "random_bonus": {"attack": 0.3, "defense": 0.3, "dodge": 0.25},
                "description": "랜덤한 능력치 증가"
            },
            "철학적 통찰": {
                "condition": "지속 효과",
                "probability": 1.0,
                "effect_duration": -1,
                "enemy_debuff": 0.1,
                "description": "적 전체의 능력치 10% 감소 오라"
            }
        }
        
        return conditions.get(trait_name, {
            "condition": "특정 조건 시",
            "probability": 1.0,
            "effect_duration": 0,
            "description": "특성 효과가 발동됩니다"
        })
    
    @staticmethod  
    def get_class_specialization(character_class: str) -> Dict[str, Any]:
        """클래스별 특화 능력 (28종 완전 확장)"""
        specializations = {
            "전사": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 0.8,
                "hp_bonus": 1.2,
                "unique_ability": "taunt"
            },
            
            "아크메이지": {
                "damage_type": "magic", 
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.8,
                "hp_bonus": 0.9,
                "unique_ability": "arcane_mastery"
            },
            
            "궁수": {
                "damage_type": "physical",
                "primary_stat": "speed",
                "mp_efficiency": 1.0,
                "hp_bonus": 1.0,
                "unique_ability": "precise_shot"
            },
            
            "도적": {
                "damage_type": "physical", 
                "primary_stat": "speed",
                "mp_efficiency": 1.1,
                "hp_bonus": 0.9,
                "unique_ability": "stealth"
            },
            
            "성기사": {
                "damage_type": "magic",
                "primary_stat": "magic_attack", 
                "mp_efficiency": 1.2,
                "hp_bonus": 1.15,
                "unique_ability": "holy_magic"
            },
            
            "암흑기사": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 0.9,
                "hp_bonus": 1.1, 
                "unique_ability": "life_drain"
            },
            
            "몽크": {
                "damage_type": "physical",
                "primary_stat": "speed",
                "mp_efficiency": 1.3,
                "hp_bonus": 1.05,
                "unique_ability": "chi_control"
            },
            
            "바드": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.4,
                "hp_bonus": 0.85,
                "unique_ability": "party_buff"
            },
            
            "네크로맨서": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.6,
                "hp_bonus": 0.8,
                "unique_ability": "undead_summon"
            },
            
            "용기사": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 0.9,
                "hp_bonus": 1.15,
                "unique_ability": "dragon_power"
            },
            
            "검성": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 1.0,
                "hp_bonus": 1.1,
                "unique_ability": "sword_master"
            },
            
            "정령술사": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.7,
                "hp_bonus": 0.85,
                "unique_ability": "elemental_summon"
            },
            
            "암살자": {
                "damage_type": "physical",
                "primary_stat": "speed",
                "mp_efficiency": 1.1,
                "hp_bonus": 0.8,
                "unique_ability": "critical_strike"
            },
            
            "기계공학자": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 1.2,
                "hp_bonus": 1.0,
                "unique_ability": "gadget_craft"
            },
            
            "무당": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.5,
                "hp_bonus": 0.9,
                "unique_ability": "spirit_power"
            },
            
            "해적": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 0.8,
                "hp_bonus": 1.05,
                "unique_ability": "dual_wield"
            },
            
            "사무라이": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 1.0,
                "hp_bonus": 1.0,
                "unique_ability": "katana_art"
            },
            
            "드루이드": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.3,
                "hp_bonus": 1.0,
                "unique_ability": "nature_magic"
            },
            
            "철학자": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 2.0,
                "hp_bonus": 0.75,
                "unique_ability": "wisdom_power"
            },
            
            "시간술사": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.9,
                "hp_bonus": 0.8,
                "unique_ability": "time_control"
            },
            
            "연금술사": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.4,
                "hp_bonus": 0.85,
                "unique_ability": "transmutation"
            },
            
            "검투사": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 0.7,
                "hp_bonus": 1.15,
                "unique_ability": "arena_skill"
            },
            
            "기사": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 0.9,
                "hp_bonus": 1.2,
                "unique_ability": "lance_charge"
            },
            
            "신관": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.6,
                "hp_bonus": 1.0,
                "unique_ability": "divine_power"
            },
            
            "마검사": {
                "damage_type": "hybrid",
                "primary_stat": "physical_attack",
                "mp_efficiency": 1.3,
                "hp_bonus": 1.05,
                "unique_ability": "magic_weapon"
            },
            
            "차원술사": {
                "damage_type": "magic",
                "primary_stat": "magic_attack",
                "mp_efficiency": 1.8,
                "hp_bonus": 0.75,
                "unique_ability": "dimension_magic"
            },
            
            "광전사": {
                "damage_type": "physical",
                "primary_stat": "physical_attack",
                "mp_efficiency": 0.5,
                "hp_bonus": 1.25,
                "unique_ability": "berserker_rage"
            }
        }
        
        return specializations.get(character_class, {
            "damage_type": "physical",
            "primary_stat": "physical_attack", 
            "mp_efficiency": 1.0,
            "hp_bonus": 1.0,
            "unique_ability": "none"
        })


class Character(BraveMixin):
    """게임 캐릭터 클래스 (Brave 시스템 포함) - 자동 애니메이션 지원"""
    
    def __init__(self, name: str, character_class: str, max_hp: int = None, 
                 physical_attack: int = None, magic_attack: int = None, 
                 physical_defense: int = None, magic_defense: int = None, speed: int = None,
                 skip_class_modifiers: bool = False):
        # Brave 시스템 초기화
        super().__init__()
        
        self.name = name
        self.character_class = character_class
        
        # 🎯 클래스별 기본 스탯 설정 (클래스 보너스 적용 안 함)
        class_defaults = {
            "전사": {"hp": 210, "p_atk": 60, "m_atk": 40, "p_def": 60, "m_def": 60, "speed": 60},
            "아크메이지": {"hp": 121, "p_atk": 43, "m_atk": 78, "p_def": 33, "m_def": 67, "speed": 58},
            "궁수": {"hp": 164, "p_atk": 74, "m_atk": 33, "p_def": 44, "m_def": 43, "speed": 68},
            "도적": {"hp": 150, "p_atk": 64, "m_atk": 38, "p_def": 43, "m_def": 49, "speed": 93},
            "성기사": {"hp": 197, "p_atk": 67, "m_atk": 38, "p_def": 76, "m_def": 62, "speed": 43},
            "암흑기사": {"hp": 189, "p_atk": 71, "m_atk": 54, "p_def": 58, "m_def": 51, "speed": 52},
            "몽크": {"hp": 172, "p_atk": 82, "m_atk": 51, "p_def": 59, "m_def": 64, "speed": 76},
            "바드": {"hp": 107, "p_atk": 43, "m_atk": 66, "p_def": 38, "m_def": 58, "speed": 69},
            "네크로맨서": {"hp": 134, "p_atk": 44, "m_atk": 84, "p_def": 39, "m_def": 74, "speed": 48},
            "용기사": {"hp": 181, "p_atk": 78, "m_atk": 62, "p_def": 67, "m_def": 58, "speed": 61},
            "검성": {"hp": 164, "p_atk": 83, "m_atk": 31, "p_def": 51, "m_def": 47, "speed": 71},
            "정령술사": {"hp": 107, "p_atk": 49, "m_atk": 85, "p_def": 42, "m_def": 69, "speed": 59},
            "암살자": {"hp": 134, "p_atk": 81, "m_atk": 28, "p_def": 34, "m_def": 39, "speed": 87},
            "기계공학자": {"hp": 156, "p_atk": 63, "m_atk": 59, "p_def": 54, "m_def": 48, "speed": 53},
            "무당": {"hp": 121, "p_atk": 48, "m_atk": 86, "p_def": 44, "m_def": 77, "speed": 64},
            "해적": {"hp": 164, "p_atk": 74, "m_atk": 34, "p_def": 52, "m_def": 41, "speed": 77},
            "사무라이": {"hp": 167, "p_atk": 74, "m_atk": 45, "p_def": 58, "m_def": 53, "speed": 67},
            "드루이드": {"hp": 175, "p_atk": 53, "m_atk": 81, "p_def": 48, "m_def": 69, "speed": 59},
            "철학자": {"hp": 107, "p_atk": 38, "m_atk": 76, "p_def": 54, "m_def": 86, "speed": 49},
            "시간술사": {"hp": 121, "p_atk": 54, "m_atk": 77, "p_def": 49, "m_def": 64, "speed": 57},
            "연금술사": {"hp": 135, "p_atk": 59, "m_atk": 72, "p_def": 44, "m_def": 58, "speed": 54},
            "검투사": {"hp": 172, "p_atk": 79, "m_atk": 41, "p_def": 56, "m_def": 48, "speed": 64},
            "기사": {"hp": 216, "p_atk": 79, "m_atk": 46, "p_def": 72, "m_def": 54, "speed": 48},
            "신관": {"hp": 143, "p_atk": 42, "m_atk": 79, "p_def": 57, "m_def": 89, "speed": 52},
            "마검사": {"hp": 164, "p_atk": 67, "m_atk": 70, "p_def": 54, "m_def": 61, "speed": 58},
            "차원술사": {"hp": 84, "p_atk": 33, "m_atk": 88, "p_def": 28, "m_def": 72, "speed": 47},
            "광전사": {"hp": 327, "p_atk": 64, "m_atk": 13, "p_def": 22, "m_def": 21, "speed": 74},
            "마법사": {"hp": 121, "p_atk": 43, "m_atk": 78, "p_def": 33, "m_def": 67, "speed": 58},  # 아크메이지와 동일
            "성직자": {"hp": 143, "p_atk": 42, "m_atk": 79, "p_def": 57, "m_def": 89, "speed": 52},  # 신관과 동일
        }
        
        # 기본값 설정 (항상 사용 가능)
        defaults = class_defaults.get(character_class, class_defaults["전사"])  # 기본값은 전사
        
        # 기본 스탯값 설정 (1레벨 캐릭터용)
        if max_hp is None:
            max_hp = defaults["hp"]
            physical_attack = defaults["p_atk"]
            magic_attack = defaults["m_atk"]
            physical_defense = defaults["p_def"]
            magic_defense = defaults["m_def"]
            speed = defaults["speed"]
        
        # 클래스 특화 정보 항상 가져오기 (스킵 여부와 상관없이)
        specialization = CharacterClassManager.get_class_specialization(character_class)
        
        if skip_class_modifiers:
            # 🔧 로딩 모드: 클래스 보정 건너뛰기 (이미 보정된 값들)
            hp_modifier = 1.0
            mp_modifier = 1.0
            self.max_hp = max_hp  # 보정 없이 원본값 사용
            self._current_hp = max_hp  # 나중에 save_system에서 정확한 값으로 덮어씀
        else:
            # 클래스 특화 적용
            hp_modifier = specialization.get("hp_bonus", 1.0)
            mp_modifier = specialization.get("mp_efficiency", 1.0)
            self.max_hp = int(max_hp * hp_modifier)
            self._current_hp = self.max_hp  # 내부 저장용
        self.wounds = 0  # 상처 누적량
        
        if skip_class_modifiers:
            # 로딩 모드에서는 클래스별 MP도 원본값 유지
            self.max_mp = self._get_class_base_mp(character_class)  # 클래스별 정확한 MP (나중에 저장된 값으로 덮어쓸 예정)
        else:
            self.max_mp = self._get_class_base_mp(character_class)  # 클래스별 고정 MP
        self._current_mp = self.max_mp  # 내부 저장용
        self.steps_taken = 0  # 걸음 수 (상처 회복용)
        
        # 애니메이션 비활성화 플래그 (초기화 중에는 애니메이션 안 함)
        self._animation_enabled = False
        
        # 스탯 할당 - None 체크와 함께
        self.physical_attack = physical_attack if physical_attack is not None else defaults["p_atk"]
        self.magic_attack = magic_attack if magic_attack is not None else defaults["m_atk"]
        self.physical_defense = physical_defense if physical_defense is not None else defaults["p_def"]
        self.magic_defense = magic_defense if magic_defense is not None else defaults["m_def"]
        self.speed = speed if speed is not None else defaults["speed"]
        
        # 💨 기믹 초기화 (디버그 메시지 최소화)
        # print(f"💨 [FORCE INIT] {name} ({character_class}) 기믹 강제 초기화...")
        
        # 기본 기믹들 - 안전한 초기화
        self.poison_stacks = 0
        # 이제 self.physical_attack은 안전하게 설정되어 있음
        self.max_poison_stacks = max(10, int(self.physical_attack * 1.5))
        
        # 직업별 기믹
        if character_class == "전사":
            # 6단계 전사 자세 시스템 초기화
            self.current_stance = 2  # 0=공격, 1=방어, 2=균형, 3=광전사, 4=수호자, 5=속도 (기본: 균형)
            self.warrior_stance = 'balanced'  # attack, defense, balanced, berserker, guardian, speed
            self.warrior_focus = 0
            # 전사 자세 변경 메서드 추가
            self.available_stances = ['attack', 'defense', 'balanced', 'berserker', 'guardian', 'speed']
        elif character_class == "아크메이지":
            self.fire_count = 0
            self.ice_count = 0
            self.lightning_count = 0
        elif character_class == "궁수":
            self.aim_points = 0
            self.precision_points = 0
        elif character_class == "암살자":
            self.shadow_count = 0
            self.shadows = 0
        elif character_class == "검성":
            self.sword_aura = 0
            self.sword_aura_stacks = 0
        elif character_class == "바드":
            self.melody_stacks = 0
            self.song_power = 0
            self.melody_notes = []  # DO/RE/MI 시스템용 멜로디 노트 리스트
            self.current_melody = ""  # 현재 연주 중인 멜로디 문자열
        elif character_class == "광전사":
            self.rage_stacks = 0
            self.berserk_level = 0
        elif character_class == "몽크":
            self.chi_points = 0
            self.ki_energy = 0
            self.strike_marks = 0
        
        # print(f"💨 [FORCE INIT] {name} 기믹 초기화 완료!")
        
        self.level = 1
        self.experience = 0
        self.experience_to_next = 30  # 다음 레벨까지 필요한 경험치
        self.atb_gauge = 0  # ATB 게이지 (0-1000) - 전투 시스템과 스케일 일치
        self.atb_speed = speed  # ATB 충전 속도는 스피드 수치 기반 (나중에 장비 적용 시 업데이트됨)
        self.is_alive = True
        
        # 캐스팅 시스템 속성
        self.casting_skill = None      # 현재 캐스팅 중인 스킬
        self.casting_targets = None    # 캐스팅 대상들
        self.casting_start_time = None # 캐스팅 시작 시간
        self.casting_duration = None   # 캐스팅 지속 시간
        self.casting_start_atb = 0     # 캐스팅 시작 ATB 값
        self.is_casting = False        # 캐스팅 상태 플래그
        
        # 속성 시스템 추가
        self.element_affinity = self._get_class_element_affinity(character_class)
        self.element_weaknesses = self._get_class_element_weaknesses(character_class)
        self.element_resistances = self._get_class_element_resistances(character_class)
        
        # 크리티컬 및 명중/회피 시스템 - 안전한 초기화
        self.critical_rate = self._get_class_base_critical_rate(character_class)  # 기본 크리티컬 확률
        # 이제 self.speed는 안전하게 설정되어 있음
        self.accuracy = 85 + (self.speed // 10)  # 기본 명중률 (85% + 스피드 보너스)
        self.evasion = 10 + (self.speed // 5)   # 기본 회피율 (10% + 스피드 보너스)
        
        # 상태이상 관련 속성 추가
        self.stunned = False
        self.silenced = False
        self.paralyzed = False
        self.sleeping = False
        self.frozen = False
        self.blinded = False
        self.charmed = False
        self.feared = False
        self.cursed = False
        self.blessed = False
        self.weakened = False
        self.strengthened = False
        self.hasted = False
        self.slowed = False
        self.shielded = False
        self.poisoned = False
        self.burning = False
        self.regenerating = False
        
        # 도적 전용 베놈 파워 시스템 (대폭 강화)
        if character_class == "도적":
            self.venom_power = 0      # 현재 베놈 파워
            self.venom_power_max = 200  # 최대 베놈 파워 (100 → 200으로 2배 증가)
        else:
            self.venom_power = 0
            self.venom_power_max = 0
        
        # 직업별 특수 시스템 초기화 (기존 시스템 활용)
        # 암살자 그림자 시스템 (이미 구현되어 있음 - shadow_count)
        if not hasattr(self, 'shadow_count'):
            self.shadow_count = 0
        
        # 철학자 지혜 시스템 (이미 구현되어 있음 - wisdom_stacks)  
        if not hasattr(self, 'wisdom_stacks'):
            self.wisdom_stacks = 0
        
        # 전사 스탠스 시스템 (이미 구현되어 있음 - current_stance)
        if character_class == "전사" and not hasattr(self, 'current_stance'):
            self.current_stance = "balanced"
        elif character_class != "전사":
            self.current_stance = None
        
        # 특성 시스템
        available_traits = CharacterClassManager.get_class_traits(character_class)
        self.available_traits = available_traits  # 선택 가능한 모든 특성
        self.active_traits = []  # 선택된 활성 특성 (최대 2개)
        self.selected_traits = []  # easy_character_creator 호환성을 위한 별칭
        self.specialization = specialization
        self.preferred_damage_type = specialization.get("damage_type", "physical")
        
        # 상태이상 관리자
        self.status_manager = StatusManager()
        
        # 인벤토리 (개인 인벤토리) 및 경제 시스템 - 안전한 초기화
        # 이제 self.physical_attack은 안전하게 설정되어 있음
        self.max_carry_weight = 15.0 + (self.physical_attack * 0.05)  # 체력에 따른 하중 한계
        self.inventory = Inventory(max_size=15, max_weight=self.max_carry_weight)  # 실제 계산된 하중 제한
        self.gold = 0  # 개인 골드는 0 (파티 공용으로 관리)
        
        # 장비 슬롯
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_accessory = None
        
        # Brave 시스템 스킬 초기화
        self.brave_skills = BraveSkillDatabase.get_character_skills(character_class)
        
        # 추가 Brave 스탯들 - GameBalance 시스템 사용
        # GameBalance에서 직업별 BRV 값 가져오기
        from .balance import GameBalance
        try:
            brave_stats = GameBalance.get_character_brave_stats(character_class, level=1)
            self.int_brv = brave_stats["int_brv"]
            self.max_brv = brave_stats["max_brv"]
            self.brv_efficiency = brave_stats["brv_efficiency"]
            self.brv_loss_resistance = brave_stats["brv_loss_resistance"]
        except Exception as e:
            # 기본값 사용
            self.int_brv = 350
            self.max_brv = 2800
            self.brv_efficiency = 1.0
            self.brv_loss_resistance = 1.0
        # 이제 self.speed는 안전하게 설정되어 있음
        self.brv_regen = self.speed // 10  # Brave 자동 회복량
        self.brave_bonus_rate = 1.0  # Brave 획득 배율
        self.brv_efficiency = 1.0  # Brave 효율성
        
        # 저장 시스템 호환을 위한 Brave 속성들 - 밸런스 조정됨
        self.current_brave = 40  # 현재 Brave 포인트 (1/10)
        self.max_brave = 9999     # 최대 Brave 포인트
        self.initial_brave = 40 # 초기 Brave 포인트 (1/10)
        self.is_broken = False   # Break 상태 여부
        
        # AI 시스템 (적 캐릭터를 위한)
        self.ai: Optional['SmartEnemyAI'] = None  # SmartEnemyAI 인스턴스가 들어갈 예정
        
        # 플레이어 스킬 시스템
        self._player_skill_system = None  # 플레이어 스킬 시스템 인스턴스
        
        # Brave 포인트를 INT BRV로 초기화
        self.initialize_brave_points()
        
        # 특성 시스템 임시 효과 변수들
        self.temp_attack_bonus = 0
        self.temp_defense_bonus = 0
        self.temp_magic_bonus = 0
        self.temp_speed_bonus = 0
        self.temp_crit_bonus = 0
        self.temp_dodge_bonus = 0
        self.temp_exp_bonus = 0
        self.temp_resistance_bonus = 0
        self.temp_penetration = 0
        self.temp_life_steal = 0
        self.temp_fear_aura = 0
        self.temp_dark_pulse = 0
        self.temp_status_resist = 0
        self.temp_treasure_bonus = 0
        self.temp_poison_chance = 0
        self.temp_undead_resistance = 0
        self.temp_protection_bonus = 0
        self.temp_next_attack_bonus = 0
        self.item_no_turn_cost = False
        self.temp_holy_damage = False
        self.temp_all_stats_boost = False
        self.stealth_turns = 0
        
        # 추가 특성 효과 변수들
        self.temp_fire_damage = False
        self.temp_physical_resistance = 0
        self.temp_debuff_resist = 0
        self.temp_weapon_mastery = 0
        self.temp_weapon_immunity = False
        self.temp_elemental_boost = 0
        self.temp_mana_efficiency = 0
        self.temp_first_strike = False
        self.temp_poison_weapon = False
        self.temp_equipment_boost = 0
        self.temp_infinite_bombs = False
        self.temp_vision_bonus = 0
        self.temp_undead_damage = 0
        self.temp_crit_immunity = 0
        self.temp_death_immunity = False
        self.temp_gold_bonus = 0
        self.temp_mp_regen_boost = 0
        self.temp_all_stats_bonus = 0
        
        # 🏹 궁수 전용 조준 포인트 시스템
        if character_class == "궁수":
            self.aim_points = 0  # 조준 포인트 (최대 5)
            self.max_aim_points = 5  # 최대 조준 포인트
            self.support_fire_active = False  # 지원사격 활성화 상태
            # print(f"🏹 [MECHANIC INIT] 궁수 {name} 조준 시스템 초기화")
            # print(f"🏹 [MECHANIC INIT] - aim_points: {self.aim_points}/{self.max_aim_points}")
            # print(f"🏹 [MECHANIC INIT] - support_fire_active: {self.support_fire_active}")
        
        # 🗡️ 도적 전용 독 시스템 (독화살, 독침 등)
        if character_class == "도적":
            self.poison_stacks = 0  # 독 스택 (최대 공격력 * 1.5)
            self.max_poison_stacks = max(10, int(self.physical_attack * 1.5))  # 최대 독 스택 (공격력 기반)
            self.venom_power = 0  # 독액 흡수력 (%)
            self.poison_immunity = False  # 독 면역
            # print(f"🗡️ [MECHANIC INIT] 도적 {name} 독 시스템 초기화")
            # print(f"🗡️ [MECHANIC INIT] - poison_stacks: {self.poison_stacks}/{self.max_poison_stacks}")
            # print(f"🗡️ [MECHANIC INIT] - venom_power: {self.venom_power}%, poison_immunity: {self.poison_immunity}")
        
        # 💨 강제 기믹 초기화 - 이미 위에서 완료됨
        
        # 🔪 암살자 전용 그림자 시스템
        if character_class == "암살자":
            self.shadow_count = 0  # 그림자 스택 (최대 5)
            self.max_shadow_count = 5  # 최대 그림자 스택
            self.stealth_mode = False  # 은신 모드
            self.assassination_ready = False  # 암살 준비 상태
            # print(f"🔪 [MECHANIC INIT] 암살자 {name} 그림자 시스템 초기화")
            # print(f"🔪 [MECHANIC INIT] - shadow_count: {self.shadow_count}/{self.max_shadow_count}")
            # print(f"🔪 [MECHANIC INIT] - stealth_mode: {self.stealth_mode}, assassination_ready: {self.assassination_ready}")
        
        # 💢 광전사 전용 분노 시스템
        if character_class == "광전사":
            self.rage_stacks = 0  # 분노 스택 (최대 10)
            self.max_rage_stacks = 10  # 최대 분노 스택
            self.berserk_mode = False  # 광폭화 모드
            self.blood_shield = 0  # 피의 방패
            # print(f"💢 [DEBUG] 광전사 {name} 초기화 완료 - rage_stacks: {self.rage_stacks}, berserk_mode: {self.berserk_mode}")
        
        # ⚔️ 검성 전용 검기 시스템
        if character_class == "검성":
            self.sword_aura = 0  # 검기 스택 (최대 5)
            self.max_sword_aura = 5  # 최대 검기 스택
            self.sword_aura_stacks = 0  # 검기 오라 스택 (별명)
            # print(f"⚔️ [DEBUG] 검성 {name} 초기화 완료 - sword_aura: {self.sword_aura}")
        
        # 🐉 용기사 전용 용의 힘 시스템
        if character_class == "용기사":
            self.dragon_marks = 0  # 용의 표식 (최대 3)
            self.max_dragon_marks = 3  # 최대 용의 표식
            self.dragon_power = 0  # 용의 힘
            self.dragon_breath_ready = False  # 드래곤 브레스 준비
            # print(f"🐉 [DEBUG] 용기사 {name} 초기화 완료 - dragon_marks: {self.dragon_marks}")
        
        # 👊 몽크 전용 기 에너지 시스템
        if character_class == "몽크":
            self.ki_energy = 0  # 기 에너지 (최대 100)
            self.max_ki_energy = 100  # 최대 기 에너지
            self.combo_count = 0  # 연계 공격 카운트
            self.strike_marks = 0  # 타격 표식
            # print(f"👊 [DEBUG] 몽크 {name} 초기화 완료 - ki_energy: {self.ki_energy}, combo_count: {self.combo_count}")
        
        # 🎵 바드 전용 음표 시스템
        if character_class == "바드":
            self.melody_stacks = 0  # 음표 스택 (최대 7: 도 레 미 파 솔 라 시)
            self.max_melody_stacks = 7  # 최대 음표 스택
            self.song_power = 0  # 노래의 힘
            self.current_song = None  # 현재 연주 중인 노래
            self.melody_notes = []  # 멜로디 노트 리스트
            self.current_melody = ""  # 현재 멜로디 표시
            # print(f"🎵 [DEBUG] 바드 {name} 초기화 완료 - melody_stacks: {self.melody_stacks}")
        
        # 💀 네크로맨서 전용 네크로 에너지 시스템
        if character_class == "네크로맨서":
            self.necro_energy = 0  # 네크로 에너지 (최대 50)
            self.max_necro_energy = 50  # 최대 네크로 에너지
            self.soul_power = 0  # 영혼력
            self.undead_count = 0  # 언데드 소환 개수
            # print(f"💀 [DEBUG] 네크로맨서 {name} 초기화 완료 - necro_energy: {self.necro_energy}, soul_power: {self.soul_power}")
        
        # 🌟 정령술사 전용 정령 친화도 시스템
        if character_class == "정령술사":
            self.spirit_bond = 0  # 정령 친화도 (최대 25)
            self.max_spirit_bond = 25  # 최대 정령 친화도
            self.elemental_affinity = 0  # 원소 친화도
            # print(f"🌟 [DEBUG] 정령술사 {name} 초기화 완료 - spirit_bond: {self.spirit_bond}")
        
        # ⏰ 시간술사 전용 시간 조작 시스템
        if character_class == "시간술사":
            self.time_marks = 0  # 시간 기록점 (최대 7)
            self.max_time_marks = 7  # 최대 시간 기록점
            self.time_manipulation_stacks = 0  # 시간 조작 스택
            self.temporal_energy = 0  # 시간 에너지
            # print(f"⏰ [DEBUG] 시간술사 {name} 초기화 완료 - time_marks: {self.time_marks}")
        
        # 🔮 아크메이지 전용 원소 카운트 시스템  
        if character_class == "아크메이지":
            self.fire_count = 0  # 화염 원소 카운트
            self.ice_count = 0   # 빙결 원소 카운트
            self.lightning_count = 0  # 번개 원소 카운트
            self.earth_count = 0  # 대지 원소 카운트
            self.wind_count = 0   # 바람 원소 카운트
            self.water_count = 0  # 물 원소 카운트
            # print(f"🔮 [DEBUG] 아크메이지 {name} 초기화 완료 - 원소 카운트들: Fire:{self.fire_count}, Ice:{self.ice_count}")
        
        # 🏛️ 검투사 전용 투기장 시스템
        if character_class == "검투사":
            self.arena_points = 0  # 투기장 포인트 (최대 20)
            self.max_arena_points = 20  # 최대 투기장 포인트  
            self.gladiator_experience = 0  # 검투사 경험
            # print(f"🏛️ [DEBUG] 검투사 {name} 초기화 완료 - arena_points: {self.arena_points}")
        
        # 디버깅을 위한 전체 특수 속성 출력
        # print(f"🔍 [DEBUG] {character_class} {name} 특수 속성 초기화 완료")
        self.temp_skill_cost_reduction = 0
        self.temp_pattern_analysis = False
        self.temp_future_sight = False
        self.temp_potion_boost = 0
        self.temp_ignore_resistance = False
        self.temp_explosion_boost = 0
        self.temp_debuff_duration = 0
        self.temp_random_element = False
        self.temp_counter_chance = 0
        self.temp_guard_bonus = 0
        self.temp_debuff_resistance = 0
        self.temp_crit_negation = 0
        self.temp_undead_damage_bonus = 0
        self.temp_heal_boost = 0
        self.temp_hybrid_damage = False
        self.temp_attack_mp_gain = False
        self.temp_magic_weapon = False
        self.temp_dual_element = False
        self.temp_unlimited_storage = False
        self.temp_enemy_accuracy_down = 0
        self.temp_status_immunity = False
        
        # 장비 보너스 변수들
        self.equipment_attack_bonus = 0
        self.equipment_defense_bonus = 0
        self.equipment_magic_bonus = 0
        self.equipment_speed_bonus = 0
        
        # 초기화 완료 후 애니메이션 활성화
        self._animation_enabled = True
    
    # HP/MP/BRV 자동 애니메이션 프로퍼티들
    @property
    def current_hp(self):
        """현재 HP 프로퍼티"""
        return self._current_hp
    
    @current_hp.setter
    def current_hp(self, value):
        """HP 변경 시 자동 애니메이션 (전투 중에만)"""
        if not hasattr(self, '_current_hp'):
            self._current_hp = value
            return
            
        old_value = self._current_hp
        # safe guard for get_total_max_hp method
        try:
            max_hp_limit = self.get_total_max_hp()
        except (AttributeError, TypeError):
            # fallback to max_hp property or basic value
            try:
                max_hp_limit = self.max_hp
            except (AttributeError, TypeError):
                max_hp_limit = getattr(self, '_max_hp', getattr(self, '_base_max_hp', 150))
        
        self._current_hp = max(0, min(value, max_hp_limit))
        
        # 전투 중이고 초기화 완료 후에만 애니메이션 실행
        if (hasattr(self, '_animation_enabled') and self._animation_enabled and 
            is_combat_active() and old_value != self._current_hp):
            try:
                from .ui_animations import animate_hp_change
                animate_hp_change(self, old_value, self._current_hp)
            except ImportError:
                pass  # 애니메이션 모듈이 없으면 무시
    
    @property
    def current_mp(self):
        """현재 MP 프로퍼티"""
        return self._current_mp
    
    @current_mp.setter
    def current_mp(self, value):
        """MP 변경 시 자동 애니메이션 (전투 중에만)"""
        if not hasattr(self, '_current_mp'):
            self._current_mp = value
            return
            
        old_value = self._current_mp
        # safe guard for get_total_max_mp method
        try:
            max_mp_limit = self.get_total_max_mp()
        except (AttributeError, TypeError):
            # fallback to max_mp property or basic value
            try:
                max_mp_limit = self.max_mp
            except (AttributeError, TypeError):
                max_mp_limit = getattr(self, '_max_mp', getattr(self, '_base_max_mp', 20))
        
        self._current_mp = max(0, min(value, max_mp_limit))
        
        # 전투 중이고 초기화 완료 후에만 애니메이션 실행
        if (hasattr(self, '_animation_enabled') and self._animation_enabled and 
            is_combat_active() and old_value != self._current_mp):
            try:
                from .ui_animations import animate_mp_change
                animate_mp_change(self, old_value, self._current_mp)
            except ImportError:
                pass  # 애니메이션 모듈이 없으면 무시
    
    @property 
    def brave_points(self):
        """현재 BRV 프로퍼티"""
        return getattr(self, '_brave_points', self.current_brave)
    
    @brave_points.setter
    def brave_points(self, value):
        """BRV 변경 시 자동 애니메이션"""
        if not hasattr(self, '_brave_points'):
            self._brave_points = value
            return
            
        old_value = self._brave_points
        self._brave_points = max(0, value)
        
        # 전투 중이고 초기화 완료 후에만 애니메이션 실행
        if (hasattr(self, '_animation_enabled') and self._animation_enabled and 
            is_combat_active() and old_value != self._brave_points):
            try:
                from .ui_animations import animate_brv_change
                animate_brv_change(self, old_value, self._brave_points)
            except ImportError:
                pass  # 애니메이션 모듈이 없으면 무시
        
        # current_brave와 동기화 유지
        self.current_brave = self._brave_points
    
    @property
    def max_hp(self):
        """장비 보너스가 포함된 최대 HP"""
        base_hp = getattr(self, '_base_max_hp', getattr(self, '_max_hp', 150))
        equipment_bonus = getattr(self, 'equipment_hp_bonus', 0)
        return base_hp + equipment_bonus
    
    @max_hp.setter 
    def max_hp(self, value):
        """기본 최대 HP 설정"""
        self._base_max_hp = value
        # 기존 _max_hp와 호환성 유지
        self._max_hp = value
    
    @property
    def max_mp(self):
        """장비 보너스가 포함된 최대 MP"""
        base_mp = getattr(self, '_base_max_mp', getattr(self, '_max_mp', 20))
        equipment_bonus = getattr(self, 'equipment_mp_bonus', 0)
        return base_mp + equipment_bonus
    
    @max_mp.setter
    def max_mp(self, value):
        """기본 최대 MP 설정"""
        self._base_max_mp = value
        # 기존 _max_mp와 호환성 유지
        self._max_mp = value
    
    def disable_animations(self):
        """애니메이션 비활성화 (대량 처리 시 사용)"""
        self._animation_enabled = False
    
    def enable_animations(self):
        """애니메이션 활성화"""
        self._animation_enabled = True
    
    def _get_class_element_affinity(self, character_class: str) -> str:
        """클래스별 기본 속성 친화도 반환 (모든 직업은 기본적으로 무속성)"""
        # 기본적으로 모든 직업은 무속성으로 설정
        class_elements = {
            "전사": "무속성",
            "검성": "무속성", 
            "검투사": "무속성",
            "광전사": "무속성",
            "기사": "무속성",
            "성기사": "무속성",  # 빛 속성으로 변경할 수도 있음
            "암흑기사": "무속성",  # 어둠 속성으로 변경할 수도 있음
            "용기사": "무속성",
            "아크메이지": "무속성",
            "정령술사": "무속성",  # 다양한 원소 사용
            "시간술사": "무속성",
            "차원술사": "무속성",
            "철학자": "무속성",
            "궁수": "무속성",
            "암살자": "무속성",
            "도적": "무속성",
            "해적": "무속성",
            "사무라이": "무속성",
            "바드": "무속성",
            "무당": "무속성",
            "드루이드": "무속성",
            "신관": "무속성",
            "성직자": "무속성",
            "몽크": "무속성",
            "마검사": "무속성",
            "연금술사": "무속성",
            "기계공학자": "무속성",
            "네크로맨서": "무속성"
        }
        return class_elements.get(character_class, "무속성")
    
    def _get_class_element_weaknesses(self, character_class: str) -> List[str]:
        """클래스별 약점 속성 반환 (기본적으로 약점 없음)"""
        # 현재는 모든 직업이 약점 없음으로 설정
        # 추후 밸런스에 따라 조정 가능
        return []
    
    def _get_class_element_resistances(self, character_class: str) -> List[str]:
        """클래스별 저항 속성 반환 (기본적으로 저항 없음)"""
        # 현재는 모든 직업이 저항 없음으로 설정
        # 추후 밸런스에 따라 조정 가능
        return []
    
    def get_element_display_info(self) -> Dict[str, Any]:
        """속성 정보를 표시용으로 반환"""
        return {
            "affinity": self.element_affinity,
            "weaknesses": self.element_weaknesses,
            "resistances": self.element_resistances,
            "display_text": self._format_element_display()
        }
    
    def _format_element_display(self) -> str:
        """속성 정보를 문자열로 포맷팅"""
        lines = []
        lines.append(f"🔮 기본 속성: {self.element_affinity}")
        
        if self.element_weaknesses:
            weakness_str = ", ".join(self.element_weaknesses)
            lines.append(f"💔 약점: {weakness_str}")
        else:
            lines.append(f"💔 약점: 없음")
            
        if self.element_resistances:
            resistance_str = ", ".join(self.element_resistances)
            lines.append(f"🛡️ 저항: {resistance_str}")
        else:
            lines.append(f"🛡️ 저항: 없음")
            
        return "\n".join(lines)
    
    def _get_class_base_mp(self, character_class: str) -> int:
        """클래스별 기본 최대 MP 반환"""
        base_mp_by_class = {
            "전사": 32,
            "아크메이지": 89,
            "궁수": 45,
            "도적": 41,
            "성기사": 67,
            "암흑기사": 53,
            "몽크": 58,
            "바드": 73,
            "네크로맨서": 84,
            "용기사": 48,
            "검성": 39,
            "정령술사": 94,
            "암살자": 35,
            "기계공학자": 61,
            "무당": 76,
            "해적": 37,
            "사무라이": 43,
            "드루이드": 71,
            "철학자": 97,
            "시간술사": 103,
            "연금술사": 69,
            "검투사": 29,
            "기사": 34,
            "신관": 81,
            "마검사": 62,
            "차원술사": 91,
            "광전사": 22,
            "마법사": 86,
            "성직자": 78,
            "Enemy": 50
        }
        
        return base_mp_by_class.get(character_class, 120)
    
    def _get_class_base_critical_rate(self, character_class: str) -> float:
        """클래스별 기본 크리티컬 확률 (%)"""
        base_critical_by_class = {
            "전사": 8.0,        # 낮은 크리티컬
            "마법사": 6.0,      # 가장 낮은 크리티컬
            "도적": 15.0,       # 높은 크리티컬
            "성직자": 7.0,      # 낮은 크리티컬
            "기사": 9.0,        # 낮은 크리티컬
            "암살자": 18.0,     # 매우 높은 크리티컬
            "검성": 12.0,       # 높은 크리티컬
            "광전사": 11.0,     # 중간 크리티컬
            "검투사": 13.0,     # 높은 크리티컬
            "사무라이": 14.0,   # 높은 크리티컬
            "마검사": 10.0,     # 중간 크리티컬
            "용기사": 9.0,      # 낮은 크리티컬
            "해적": 12.0,       # 높은 크리티컬
            "정령술사": 8.0,    # 낮은 크리티컬
            "시간술사": 7.0,    # 낮은 크리티컬
            "차원술사": 6.0,    # 낮은 크리티컬
            "연금술사": 9.0,    # 낮은 크리티컬
            "드루이드": 8.0,    # 낮은 크리티컬
            "무당": 7.0,        # 낮은 크리티컬
            "철학자": 5.0,      # 가장 낮은 크리티컬
            "기계공학자": 10.0, # 중간 크리티컬
            "Enemy": 8.0        # 적 기본 크리티컬
        }
        
        return base_critical_by_class.get(character_class, 10.0)
        
    def apply_trait_effects(self, situation: str, **kwargs) -> Dict[str, Any]:
        """특성 효과 적용"""
        effects = {}
        
        # active_traits 사용 (traits 대신)
        if not hasattr(self, 'active_traits'):
            self.active_traits = []
        
        for trait in self.active_traits:
            # trait가 딕셔너리인 경우와 객체인 경우 모두 처리
            if isinstance(trait, dict):
                is_active = trait.get('is_active', True)
                effect_type = trait.get('effect_type', 'passive')
            else:
                is_active = getattr(trait, 'is_active', True)
                effect_type = getattr(trait, 'effect_type', 'passive')
            
            if not is_active:
                continue
                
            if effect_type == "passive":
                effects.update(self._apply_passive_trait(trait, situation, **kwargs))
            elif effect_type == "trigger" and situation in ["combat_start", "on_attack", "on_kill", "on_damage"]:
                effects.update(self._apply_trigger_trait(trait, situation, **kwargs))
            elif effect_type == "active" and situation == "active_use":
                effects.update(self._apply_active_trait(trait, **kwargs))
                
        return effects
    
    def _apply_passive_trait(self, trait, situation: str, **kwargs) -> Dict[str, Any]:
        """패시브 특성 효과 적용 - 새로운 직업 시스템 대응"""
        effects = {}
        
        # trait가 딕셔너리인 경우와 객체인 경우 모두 처리
        if isinstance(trait, dict):
            effect_value = trait.get('effect_value', {})
            trait_name = trait.get('name', '')
        else:
            effect_value = getattr(trait, 'effect_value', {})
            trait_name = getattr(trait, 'name', '')
        
        # === 암살자 특성 ===
        if trait_name == "그림자 조작" and situation == "combat_start":
            # 전투 시작 시 그림자 3개 생성
            if not hasattr(self, 'shadow_count'):
                self.shadow_count = 0
            self.shadow_count += 3
            effects["shadow_generation"] = 3
            
        if trait_name == "그림자 강화" and situation == "attacking":
            # 그림자 1개당 공격력 15% 증가
            shadow_count = getattr(self, 'shadow_count', 0)
            if shadow_count > 0:
                effects["shadow_damage_boost"] = shadow_count * 0.15
        
        if trait_name == "그림자 숙련":
            # 그림자 개수에 비례하여 크리티컬과 회피 증가
            shadow_count = getattr(self, 'shadow_count', 0)
            if shadow_count > 0:
                crit_bonus = min(shadow_count * 8, 40)  # 최대 40%
                dodge_bonus = min(shadow_count * 6, 30)  # 최대 30%
                effects["shadow_crit_bonus"] = crit_bonus
                effects["shadow_dodge_bonus"] = dodge_bonus
        
        if trait_name == "그림자 방어" and situation == "defending":
            # 피격 시 그림자 1개 소모로 50% 피해 감소
            shadow_count = getattr(self, 'shadow_count', 0)
            if shadow_count > 0:
                self.shadow_count -= 1
                effects["damage_reduction"] = 0.5
                effects["shadow_consumed"] = True
        
        # === 기계공학자 특성 ===
        if trait_name == "기계 정밀" and situation == "combat_start":
            # 전투 시작 시 정밀도 향상
            effects["accuracy_bonus"] = 0.2
            effects["crit_bonus"] = 0.2
        
        if trait_name == "기계 숙련":
            # 공격력과 마법공격력 15% 증가, MP 회복량 50% 증가
            effects["attack_boost"] = 0.15
            effects["magic_attack_boost"] = 0.15
            effects["mp_recovery_boost"] = 0.5
        
        # === 드루이드 특성 ===
        if trait_name == "식물 친화" and situation == "combat_start":
            # 적들의 속도 20% 감소 오라
            effects["speed_debuff_aura"] = 0.2
        
        if trait_name == "야생 본능" and situation == "combat_start":
            # 랜덤한 능력치 증가
            import random
            bonus_type = random.choice(["attack", "defense", "dodge"])
            if bonus_type == "attack":
                effects["attack_boost"] = 0.3
            elif bonus_type == "defense":
                effects["defense_boost"] = 0.3
            else:
                effects["dodge_bonus"] = 0.25
        
        # === 연금술사 특성 ===
        if trait_name == "플라스크 달인" and situation == "attacking":
            import random
            if random.random() < 0.25:  # 25% 확률로 폭발 효과
                effects["flask_explosion"] = True
                effects["explosion_damage"] = self.magic_attack * 2.5
        
        if trait_name == "원소 변환" and situation == "attacking":
            # 공격 시 랜덤한 속성 효과 부여
            import random
            element_types = ["fire", "ice", "lightning", "earth"]
            selected_element = random.choice(element_types)
            effects["element_effect"] = selected_element
        
        # === 신관 특성 ===
        if trait_name == "축복의 오라":
            # 파티 전체 디버프 저항 30% 증가
            effects["party_debuff_resistance"] = 0.3
        
        # === 철학자 특성 ===
        if trait_name == "철학적 통찰":
            # 적 전체의 능력치 10% 감소 오라
            effects["enemy_stat_debuff"] = 0.1
        
        # === 검성 특성 ===
        if trait_name == "검기 집중" and situation == "sword_aura_gain":
            import random
            if random.random() < 0.2:  # 20% 확률로 검기 스택 2개 획득
                effects["double_sword_aura"] = True
                
        if trait_name == "일섬의 달인" and situation == "atb_refund":
            effects["atb_refund_bonus"] = 0.2  # ATB 환급량 20% 증가
            
        if trait_name == "검의 이치":
            effects["max_sword_aura"] = 3  # 검기 스택 최대치 +1
            
        if trait_name == "명경지수" and situation == "attacking":
            if self.current_hp >= self.max_hp * 0.5:
                effects["crit_bonus"] = 0.25  # HP 50% 이상일 때 크리티컬 25% 증가
                
        if trait_name == "검신의 축복" and situation == "attacking":
            if hasattr(self, 'sword_aura_stacks') and self.sword_aura_stacks >= 2:
                effects["guaranteed_crit"] = True  # 검기 스택 최대일 때 크리티컬 확정
        
        # === 검투사 특성 ===
        if trait_name == "투기장의 경험" and situation == "kill_stack":
            effects["kill_stack_boost"] = 0.25  # 처치 시 능력치 상승폭 25% 증가
            
        if trait_name == "패링 마스터" and situation == "parrying":
            effects["parry_damage_boost"] = 1.2  # 패링 시 반격 피해 120% 증가
            
        if trait_name == "생존 본능" and situation == "parrying":
            if self.current_hp <= self.max_hp * 0.3:
                effects["survival_parry_duration"] = 3.0  # HP 30% 이하일 때 패링 지속시간 3배 연장
        
        # === 광전사 특성 ===
        if trait_name == "피의 갈증":
            effects["hp_cost_reduction"] = 0.85  # HP 소모량 15% 감소
            effects["lifesteal_boost"] = 1.25  # 흡혈 효과 25% 증가
            
        if trait_name == "광기의 힘" and situation == "shield_generation":
            hp_ratio = self.current_hp / self.max_hp
            effects["rage_shield_bonus"] = (1.0 - hp_ratio) * 0.5  # HP 낮을수록 보호막 증가
            
        # === 광전사 특성 ===
        if trait_name == "혈투의 광기" and situation == "stat_calculation":
            hp_ratio = self.current_hp / self.max_hp
            if hp_ratio <= 0.15:  # HP 15% 이하일 때
                # 공격력 100% 증가 (너프됨, 이전: 300%)
                effects["berserker_rage_attack"] = 1.0  # 100% 공격력 증가
                effects["all_attacks_hp"] = True  # 모든 공격이 HP 공격으로 변환
                print(f"🔥 {self.name}의 혈투의 광기 발동! 공격력 100% 증가!")
            elif hp_ratio < 0.5:  # HP 50% 이하일 때 (기존 효과)
                rage_multiplier = (1.0 - hp_ratio) * 2  # HP가 낮을수록 강화
                effects["rage_attack_bonus"] = rage_multiplier * 0.3  # 공격력 증가
                effects["rage_crit_bonus"] = rage_multiplier * 0.25   # 치명타율 증가
        
        if trait_name == "피의 갈증" and situation == "lifesteal":
            effects["lifesteal_bonus"] = 0.25  # 흡혈 효과 25% 증가
            effects["hp_cost_reduction"] = 0.15  # HP 소모량 15% 감소
        
        if trait_name == "광기의 힘" and situation == "shield_creation":
            hp_ratio = self.current_hp / self.max_hp
            rage_shield_bonus = (1.0 - hp_ratio) * 0.5  # HP가 낮을수록 보호막 증가
            effects["rage_shield_bonus"] = rage_shield_bonus
        
        if trait_name == "불굴의 의지" and situation == "damage_taken":
            if self.current_hp <= self.max_hp * 0.15:  # HP 15% 이하일 때
                effects["last_stand_reduction"] = 0.5  # 받는 피해 50% 감소
        
        # === 차원술사 특성 ===
        if trait_name == "차원 방벽" and situation == "combat_start":
            # 전투 시작 시 보호막 자동 생성 (최대 HP의 20%)
            shield_amount = int(self.max_hp * 0.2)
            effects["dimension_barrier"] = shield_amount
            
        if trait_name == "잔상 숙련" and situation == "dodge_success":
            # 회피 성공 시 다음 공격 치명타 확정
            effects["next_attack_crit"] = True
            
        if trait_name == "차원 도약" and situation == "being_attacked":
            # 공격 받을 때 50% 확률로 완전 회피
            import random
            if random.random() < 0.5:
                effects["dimension_dodge"] = True
                
        if trait_name == "공간 왜곡" and situation == "being_targeted":
            # 적의 정확도 30% 감소
            effects["enemy_accuracy_reduction"] = 0.3
            
        if trait_name == "차원 귀환" and situation == "damage_taken":
            if self.current_hp <= self.max_hp * 0.3:  # HP 30% 이하일 때
                # 즉시 HP 회복 + 1턴 무적
                heal_amount = int(self.max_hp * 0.3)
                effects["dimension_return_heal"] = heal_amount
                effects["dimension_invincible"] = 1  # 1턴 무적
        
        # === 기사 특성 ===
        if trait_name == "의무의 수호자" and situation == "protecting_ally":
            effects["extra_duty_stack"] = True  # 아군 보호 시 의무 스택 추가 획득
            
        if trait_name == "기사도 정신" and situation == "stat_calculation":
            if hasattr(self, 'duty_stacks') and self.duty_stacks >= 3:
                effects["chivalry_boost"] = 0.2  # 의무 스택 3개 이상일 때 모든 능력치 20% 증가
        
        # === 전사 특성 ===
        if trait_name == "전장의 지배자" and situation == "stance_bonus":
            # 같은 자세 유지 시 능력치 누적 증가 구현
            effects["stance_mastery_stack"] = {
                "growth_per_turn": 0.03,
                "max_bonus": 0.35
            }
            
        if trait_name == "6단계 완전체" and situation == "stance_bonus":
            # 6가지 자세 완전 숙달 효과
            effects["stance_mastery"] = True
            
        if trait_name == "적응형 무술" and situation == "stance_change":
            # 자세 변경 시 다음 공격 위력 30% 증가
            effects["stance_change_boost"] = 1.3
            
        if trait_name == "불굴의 의지" and situation == "turn_start":
            # 모든 자세에서 매 턴 HP 8% 회복
            heal_amount = int(self.max_hp * 0.08)
            self.heal(heal_amount, show_animation=False)
            effects["universal_regeneration"] = True
            
        if trait_name == "전투 본능" and situation == "skill_cost":
            # 자세 변경 스킬 MP 소모 없음
            effects["stance_change_no_mp"] = True
        
        # === 성기사 특성 ===
        if trait_name == "성역의 수호자":
            effects["sanctuary_duration"] = 1.5  # 성역 지속시간 50% 증가
            
        if trait_name == "신성한 힘" and situation == "healing":
            sanctuary_count = getattr(self, 'sanctuary_count', 0)
            effects["holy_healing_bonus"] = sanctuary_count * 0.15  # 성역 1개당 치유 15% 증가
        
        # === 암흑기사 특성 ===
        if trait_name == "어둠의 권능":
            effects["absorption_limit_bonus"] = 1.25  # 흡수 스택 최대치 +25%
            
        if trait_name == "생명력 지배" and situation == "absorption_healing":
            effects["absorption_efficiency"] = 1.3  # 흡수 스택 회복 효율 30% 증가
        
        # === 용기사 특성 ===
        if trait_name == "표식 달인" and situation == "dragon_marking":
            effects["mark_chance_bonus"] = 0.3  # 표식 부여 확률 30% 증가
            
        if trait_name == "도약의 숙련자" and situation == "leap_attack":
            effects["leap_invincible_duration"] = 1.5  # 무적 시간 50% 증가
        
        # === 아크메이지 특성 ===
        if trait_name == "원소 순환 마스터":
            effects["fast_element_cycle"] = 2  # 동일 원소 2회만으로도 자동 발동
            
        if trait_name == "원소 친화" and situation == "elemental_attack":
            effects["elemental_damage_bonus"] = 0.2  # 모든 원소 마법 위력 20% 증가
        
        # === 기존 직업 특성 (유지) ===
        if trait_name == "마나 순환" and situation == "spell_cast":
            import random
            if random.random() < 0.3:
                effects["mana_efficiency"] = 0.5  # 30% 확률로 MP 소모량 절반
        
        return effects
        
        # 마법사 계열 특성들
        if trait_name == "마력 집중" and situation == "skill_use":
            effects["mp_cost_reduction"] = 0.25  # 25% MP 소모 감소
            effects["spell_power"] = 1.2  # 20% 마법 위력 증가
            
        if trait_name == "마나 순환" and situation == "turn_end":
            effects["mp_regeneration"] = int(self.max_mp * 0.1)  # 최대 MP의 10% 회복
            
        if trait_name == "원소 지배" and situation == "magic_attack":
            effects["elemental_mastery"] = True
            effects["spell_power"] = 1.3  # 30% 마법 위력 증가
            
        if trait_name == "마법 폭주" and situation == "low_mp":
            if self.current_mp <= self.max_mp * 0.3:
                effects["spell_power"] = 1.5  # 50% 마법 위력 증가
                effects["mp_cost_reduction"] = 0.5  # 50% MP 소모 감소
        
        if trait_name == "마법 연구자" and situation == "combat_end":
            effects["exp_multiplier"] = 1.3  # 30% 경험치 증가
            
        # 궁수 계열 특성들
        if trait_name == "정밀 사격" and situation == "ranged_attack":
            effects["crit_chance_bonus"] = 0.3  # 30% 크리티컬 확률 증가
            effects["accuracy_bonus"] = 0.25  # 25% 명중률 증가
            
        if trait_name == "민첩한 몸놀림" and situation in ["defending", "dodging"]:
            effects["dodge_chance_bonus"] = 0.25  # 25% 회피율 증가
            effects["speed_bonus"] = 0.2  # 20% 속도 증가
            
        if trait_name == "원거리 숙련" and situation == "ranged_attack":
            effects["damage_multiplier"] = 1.25  # 25% 데미지 증가
            effects["range_bonus"] = 2  # 사거리 증가
            
        if trait_name == "바람의 가호" and situation == "turn_start":
            effects["speed_bonus"] = 0.15  # 15% 속도 증가
            effects["atb_bonus"] = 10  # ATB 보너스
            
        if trait_name == "사냥꾼의 직감" and situation == "combat_start":
            effects["first_strike"] = True  # 선제공격 확률 증가
            
        # 도적 특성 (리메이크)
        if trait_name == "독술 지배" and situation in ["attacking", "poison_attack"]:
            effects["poison_always"] = True  # 모든 공격에 독 부여
            effects["poison_boost"] = 1.5  # 독 피해량 50% 증가
            
        if trait_name == "침묵 술" and situation == "attacking":
            effects["silence_chance"] = 0.3  # 30% 침묵 부여 확률
            effects["silence_duration"] = 2  # 2턴 지속
            
        if trait_name == "독 촉진" and situation == "poison_target_attack":
            effects["poison_trigger"] = 0.25  # 남은 독 피해의 25% 즉시 피해
            
        if trait_name == "맹독 면역" and situation in ["poison_defense", "status_defense"]:
            effects["poison_immunity"] = True  # 독 완전 면역
            effects["status_immunity"] = 0.7  # 70% 상태이상 저항
            effects["poison_reflect"] = True  # 독 공격 반사
            
        if trait_name == "독왕의 권능" and situation == "poison_kill":
            effects["poison_spread"] = True  # 독으로 처치 시 주변에 독 전파
            effects["poison_aura"] = 2  # 2칸 범위
            
        # 성기사 계열 특성들
        if trait_name == "치유의 빛" and situation in ["healing", "turn_end"]:
            effects["healing_bonus"] = 0.3  # 30% 치유량 증가
            effects["self_regeneration"] = int(self.max_hp * 0.05)  # 5% HP 재생
            
        if trait_name == "신성한 가호" and situation == "defending":
            effects["holy_resistance"] = 0.5  # 50% 어둠/언데드 저항
            effects["status_immunity"] = ["curse", "fear"]  # 저주, 공포 면역
            
        if trait_name == "축복받은 무기" and situation == "attacking":
            enemy_type = kwargs.get("enemy_type", "")
            if enemy_type in ["undead", "demon", "dark"]:
                effects["holy_damage"] = 1.5  # 150% 신성 데미지
                
        if trait_name == "수호의 맹세" and situation == "protecting":
            effects["protect_bonus"] = True
            effects["damage_reduction"] = 0.3  # 30% 데미지 감소
            
        if trait_name == "정의의 분노" and situation == "ally_injured":
            effects["damage_multiplier"] = 1.4  # 40% 데미지 증가
            effects["accuracy_bonus"] = 0.3  # 30% 명중률 증가
            
        # 암흑기사 계열 특성들
        if trait_name == "생명 흡수" and situation == "attacking":
            effects["life_steal"] = 0.3  # 30% 생명력 흡수
            
        if trait_name == "어둠의 계약" and situation == "attacking":
            hp_cost = int(self.max_hp * 0.1)  # HP 10% 소모
            if self.current_hp > hp_cost:
                effects["hp_cost"] = hp_cost
                effects["damage_multiplier"] = 1.5  # 50% 데미지 증가
                
        if trait_name == "불사의 의지" and situation == "near_death":
            if self.current_hp <= self.max_hp * 0.2:
                effects["death_resistance"] = 0.7  # 70% 죽음 저항
                effects["damage_reduction"] = 0.4  # 40% 데미지 감소
                
        if trait_name == "어둠 조작" and situation == "magic_attack":
            effects["dark_mastery"] = True
            effects["spell_power"] = 1.25  # 25% 마법 위력 증가
            
        if trait_name == "공포 오라" and situation == "combat_presence":
            effects["enemy_debuff"] = {"accuracy": -0.2, "speed": -0.15}  # 적 디버프
            
        # 몽크 계열 특성들
        if trait_name == "내공 순환" and situation in ["turn_end", "meditation"]:
            effects["mp_regeneration"] = int(self.max_mp * 0.15)  # 15% MP 회복
            effects["hp_regeneration"] = int(self.max_hp * 0.08)  # 8% HP 회복
            
        if trait_name == "연타 숙련" and situation == "combo_attack":
            combo_count = kwargs.get("combo_count", 0)
            effects["combo_multiplier"] = 1.0 + (combo_count * 0.2)  # 콤보당 20% 증가
            
        if trait_name == "정신 수양" and situation in ["status_effect", "mental_attack"]:
            effects["status_resistance"] = 0.6  # 60% 상태이상 저항
            effects["mental_immunity"] = True  # 정신 계열 면역
            
        if trait_name == "참선의 깨달음" and situation == "turn_start":
            effects["wisdom_bonus"] = True
            effects["skill_cooldown_reduction"] = 1  # 스킬 쿨다운 1턴 감소
            
        if trait_name == "기절 공격" and situation == "unarmed_attack":
            effects["stun_chance"] = 0.25  # 25% 기절 확률
            
        # 바드 계열 특성들  
        if trait_name == "영감 부여" and situation == "party_support":
            effects["party_buff"] = {"attack": 0.15, "speed": 0.1}  # 파티 버프
            
        if trait_name == "다중 주문" and situation == "spell_casting":
            effects["multi_cast_chance"] = 0.3  # 30% 다중 시전 확률
            
        if trait_name == "재생의 노래" and situation == "turn_end":
            effects["party_healing"] = int(self.max_hp * 0.1)  # 파티 힐링
            
        if trait_name == "마법 저항" and situation == "magic_defense":
            effects["magic_resistance"] = 0.3  # 30% 마법 저항
            
        if trait_name == "카리스마" and situation == "social_interaction":
            effects["negotiation_bonus"] = True
            effects["shop_discount"] = 0.1  # 10% 상점 할인
            
        # === 차원술사 새 특성 ===
        if trait_name == "차원 방벽" and situation == "combat_start":
            barrier_amount = int(self.max_hp * 0.3)  # 최대 HP 30% 보호막
            effects["auto_barrier"] = barrier_amount
            
        if trait_name == "잔상 숙련" and situation == "dodge_success":
            effects["next_attack_critical"] = True  # 다음 공격 치명타 확정
            
        if trait_name == "차원 도약" and situation == "being_attacked":
            if random.random() < 0.5:  # 50% 확률
                effects["complete_dodge"] = True  # 완전 회피
                
        if trait_name == "차원 귀환" and situation == "low_hp":
            if self.current_hp <= self.max_hp * 0.3:  # HP 30% 이하일 때
                heal_amount = int(self.max_hp * 0.5)  # 50% 회복
                effects["emergency_heal"] = heal_amount
                effects["invincible_turns"] = 1  # 1턴 무적
            
        return effects
    
    def _apply_trigger_trait(self, trait: CharacterTrait, situation: str, **kwargs) -> Dict[str, Any]:
        """트리거 특성 효과 적용 - 새로운 특성들 포함"""
        effects = {}
        
        # trait가 딕셔너리인 경우와 객체인 경우 모두 처리
        if isinstance(trait, dict):
            effect_value = trait.get('effect_value', {})
            trait_name = trait.get('name', '')
        else:
            effect_value = getattr(trait, 'effect_value', {})
            trait_name = getattr(trait, 'name', '')
            
        # === 광전사 트리거 특성 ===
        if trait_name == "불굴의 의지" and situation == "damage_taken":
            if self.current_hp <= self.max_hp * 0.15:  # HP 15% 이하일 때
                effects["last_stand_reduction"] = 0.5  # 받는 피해 50% 감소
                
        if trait_name == "광전사의 최후" and situation == "ultimate_use":
            effects["berserker_immortal"] = 1  # 1턴간 무적
            
        # === 차원술사 트리거 특성 ===
        if trait_name == "잔상 숙련" and situation == "dodge_success":
            effects["next_attack_crit"] = True  # 다음 공격 치명타 확정
            
        if trait_name == "차원 귀환" and situation == "low_hp":
            if self.current_hp <= self.max_hp * 0.3:  # HP 30% 이하일 때
                heal_amount = int(self.max_hp * 0.3)
                effects["dimension_return_heal"] = heal_amount
                effects["dimension_invincible"] = 1  # 1턴 무적
                
        # === 검투사 트리거 특성 ===
        if trait_name == "생존 본능" and situation == "parrying":
            if self.current_hp <= self.max_hp * 0.3:
                effects["survival_parry_duration"] = 3.0  # 패링 지속시간 3배 연장
                
        if trait_name == "투사의 긍지" and situation == "debuff_check":
            if hasattr(self, 'kill_stacks') and self.kill_stacks >= 3:
                effects["debuff_immunity"] = True  # 디버프 면역
                
        if trait_name == "콜로세움의 영웅" and situation == "on_kill":
            effects["immediate_action"] = True  # 즉시 행동
        
        # === 기존 트리거 특성들 ===
        if situation == "on_kill" and "kill_damage_stack" in effect_value:
            # 적 처치 시 다음 공격 피해량 증가
            current_stack = getattr(self, "_kill_damage_stack", 0)
            self._kill_damage_stack = current_stack + effect_value["kill_damage_stack"]
            effects["next_attack_bonus"] = self._kill_damage_stack
            
        elif situation == "on_attack" and "first_strike_crit" in effect_value:
            # 첫 공격은 항상 크리티컬
            if not hasattr(self, "_has_attacked"):
                self._has_attacked = True
                effects["guaranteed_critical"] = True
                
        elif situation == "on_attack" and "heal_on_attack" in effect_value:
            # 공격 시 파티 힐링
            if random.random() < effect_value["heal_on_attack"]:
                effects["party_heal"] = self.max_hp * 0.1
                
        elif situation == "on_damage" and "justice_rage" in effect_value:
            # 아군이 쓰러질 때 분노
            if kwargs.get("ally_defeated", False):
                effects["stat_boost"] = effect_value["justice_rage"]
                
        return effects
        
    def _apply_active_trait(self, trait: CharacterTrait, **kwargs) -> Dict[str, Any]:
        """액티브 특성 효과 적용"""
        effects = {}
        effect_value = trait.effect_value
        
        if "stealth_duration" in effect_value:
            # 은신 효과 활성화
            effects["stealth_turns"] = effect_value["stealth_duration"]
            
        return effects
        
    def select_passive_traits(self, trait_indices: List[int]) -> bool:
        """패시브 특성 선택 (0-2개 선택 가능)"""
        # 개발 모드가 아닌 경우 패시브 해금 확인
        if not game_config.are_all_passives_unlocked():
            # 일반 모드에서는 특정 패시브만 해금
            unlocked_traits = self._get_unlocked_traits()
            available_indices = []
            for i in trait_indices:
                if 0 <= i < len(self.available_traits):
                    if self.available_traits[i].name in unlocked_traits:
                        available_indices.append(i)
                    else:
                        print(f"{RED}'{self.available_traits[i].name}' 특성은 아직 해금되지 않았습니다.{RESET}")
                        return False
            trait_indices = available_indices
        
        # 0-2개 선택 가능으로 변경
        if len(trait_indices) > 2:
            print(f"{RED}최대 2개의 특성만 선택할 수 있습니다.{RESET}")
            return False
            
        if len(trait_indices) != len(set(trait_indices)):
            print(f"{RED}같은 특성을 중복으로 선택할 수 없습니다.{RESET}")
            return False
            
        selected_traits = []
        for i in trait_indices:
            if 0 <= i < len(self.available_traits):
                selected_traits.append(self.available_traits[i])
            else:
                print(f"{RED}잘못된 특성 번호입니다: {i+1}{RESET}")
                return False
        
        self.active_traits = selected_traits
        self.selected_traits = selected_traits  # easy_character_creator 호환성을 위해 추가
        
        if len(selected_traits) == 0:
            print(f"{YELLOW}{self.name}이(가) 패시브 특성을 선택하지 않았습니다.{RESET}")
        else:
            print(f"{GREEN}{self.name}의 선택된 특성:{RESET}")
            for trait in self.active_traits:
                print(f"  {YELLOW}• {trait.name}{RESET}: {trait.description}")
        
        return True
    
    def select_traits(self, mode: str = "normal"):
        """특성 선택 메서드 - 커서 메뉴 시스템 사용"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white
            
            # 캐릭터 정보 헤더 표시
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_cyan(f'🎭 {self.name} ({self.character_class}) - 특성 선택')}")
            print(f"{bright_cyan('='*60)}")
            
            # 캐릭터 기본 능력치 표시
            print(f"{cyan('📊 기본 능력치:')}")
            print(f"  💪 물리공격: {self.physical_attack:3d}  🔮 마법공격: {self.magic_attack:3d}")
            print(f"  🛡️  물리방어: {self.physical_defense:3d}  🛡️ 마법방어: {self.magic_defense:3d}")
            print(f"  ❤️  H  P: {self.max_hp:3d}  💙 M  P: {self.max_mp:3d}")
            print(f"  ⚡ 초기BRV: {self.initial_brave:3d}  🔥 최대BRV: {self.max_brave:3d}")
            print(f"  🏃 속  도: {self.speed:3d}")
            print()
            
            print(f"{bright_yellow('💡 0-2개의 특성을 선택할 수 있습니다 (패시브 없이도 게임 가능)')}")
            print(f"{yellow('❓ 특성을 선택하면 게임에서 자동으로 발동됩니다')}")
            print()
            
            # 개발 모드 확인
            from config import game_config
            is_dev_mode = hasattr(game_config, 'DEVELOPMENT_MODE') and game_config.DEVELOPMENT_MODE
            
            available_traits = []
            if is_dev_mode:
                available_traits = self.available_traits
                print(f"{cyan('🔧 개발 모드: 모든 특성 사용 가능')}")
            else:
                # 일반 모드에서는 해금된 특성만
                unlocked_names = self._get_unlocked_traits()
                available_traits = [trait for trait in self.available_traits if trait.name in unlocked_names]
                if available_traits:
                    print(f"{green(f'🔓 해금된 특성: {len(available_traits)}개')}")
                else:
                    print(f"{red('🔒 해금된 특성이 없습니다')}")
            
            if not available_traits:
                print(f"\n{yellow('패시브 없이 게임을 진행합니다.')}")
                input(f"{white('계속하려면 Enter를 누르세요...')}")
                return
            
            # 선택된 특성들 저장
            selected_traits = []
            
            while len(selected_traits) < 2:
                # 메뉴 옵션 생성
                options = []
                descriptions = []
                
                # 사용 가능한 특성들 (선택되지 않은 것만)
                available_for_selection = [trait for trait in available_traits if trait not in selected_traits]
                
                for trait in available_for_selection:
                    status = "✅" if is_dev_mode else "🔓"
                    options.append(f"{trait.name} {status}")
                    descriptions.append(f"💡 {trait.description}")
                
                # 선택 완료 옵션 (1개 이상 선택했을 때만)
                if len(selected_traits) > 0:
                    options.append(f"✅ {bright_white('선택 완료')}")
                    descriptions.append(f"현재 선택된 특성 {len(selected_traits)}개로 게임을 시작합니다")
                
                # 패시브 없이 시작 옵션
                options.append(f"❌ {bright_white('패시브 없이 시작')}")
                descriptions.append("특성을 선택하지 않고 게임을 시작합니다")
                
                # 현재 선택 상태 표시
                selected_names = [trait.name for trait in selected_traits]
                current_selection = ", ".join(selected_names) if selected_names else "없음"
                title = f"🎮 특성 선택 ({len(selected_traits)}/2)\n현재 선택: {current_selection}"
                
                # 커서 메뉴 생성 및 실행 (취소 가능하도록 설정)
                menu = CursorMenu(title, options, descriptions, cancellable=True)
                result = menu.run()
                
                if result is None or result == -1:  # 취소 (Q키)
                    print(f"\n{yellow('❌ 특성 선택이 취소되었습니다.')}")
                    print(f"{yellow('패시브 없이 게임을 진행합니다.')}")
                    selected_traits = []
                    break
                elif result < len(available_for_selection):
                    # 특성 선택
                    selected_trait = available_for_selection[result]
                    selected_traits.append(selected_trait)
                    print(f"\n{green(f'✅ {selected_trait.name} 특성이 선택되었습니다!')}")
                    print(f"{cyan(f'💡 효과: {selected_trait.description}')}")
                    
                    if len(selected_traits) == 2:
                        print(f"\n{bright_yellow('🎯 최대 개수(2개)의 특성을 선택했습니다!')}")
                        break
                elif len(selected_traits) > 0 and result == len(available_for_selection):
                    # 선택 완료 (1개 이상 선택된 경우)
                    break
                else:
                    # 패시브 없이 시작
                    selected_traits = []
                    break
            
            # 선택된 특성 적용
            self.active_traits = selected_traits
            self.selected_traits = selected_traits  # easy_character_creator 호환성을 위해 추가
            
            # 최종 결과 표시
            print(f"\n{bright_cyan('='*50)}")
            if len(selected_traits) == 0:
                print(f"{yellow(f'🚀 {self.name}이(가) 패시브 특성 없이 게임을 시작합니다.')}")
            else:
                print(f"{green(f'🎉 {self.name}의 최종 선택된 특성:')}")
                for i, trait in enumerate(self.active_traits, 1):
                    print(f"  {bright_yellow(f'{i}. {trait.name}')}: {white(trait.description)}")
            print(f"{bright_cyan('='*50)}")
            
        except ImportError as e:
            print(f"커서 메뉴 시스템을 불러올 수 없습니다: {e}")
            # 폴백: 기존 시스템 사용
            self.select_passive_traits([])
    
    def _get_unlocked_traits(self) -> List[str]:
        """일반 모드에서 해금된 패시브 특성 목록 반환"""
        # 기본적으로 아무 패시브도 해금되지 않음
        basic_unlocked = {
            "전사": [],
            "아크메이지": [],
            "궁수": [],
            "도적": [],
        }
        
        return basic_unlocked.get(self.character_class, [])
    
    def display_available_traits(self):
        """선택 가능한 특성 목록 표시"""
        print(f"\n{CYAN}=== {self.name} ({self.character_class}) 특성 선택 ==={RESET}")
        print(f"{YELLOW}0-2개의 특성을 선택할 수 있습니다 (패시브 없이도 게임 가능):{RESET}\n")
        
        # 개발 모드가 아닌 경우 해금된 특성만 표시
        if not game_config.are_all_passives_unlocked():
            unlocked_traits = self._get_unlocked_traits()
            if len(unlocked_traits) == 0:
                print(f"{RED}🔒 일반 모드: 해금된 패시브가 없습니다.{RESET}")
                print(f"{YELLOW}💡 게임을 진행하여 패시브를 해금하세요!{RESET}\n")
                return
            else:
                print(f"{MAGENTA}🔒 일반 모드: 해금된 특성만 표시{RESET}\n")
        
        available_count = 0
        for i, trait in enumerate(self.available_traits):
            # 일반 모드에서는 해금 상태 확인
            if not game_config.are_all_passives_unlocked():
                is_unlocked = trait.name in self._get_unlocked_traits()
                if not is_unlocked:
                    continue  # 해금되지 않은 특성은 표시하지 않음
                lock_status = f" {GREEN}✅{RESET}"
            else:
                lock_status = f" {GREEN}✅{RESET}"
            
            available_count += 1
            print(f"{WHITE}{i+1:2}. {BOLD}{trait.name}{RESET}{lock_status}")
            print(f"     {trait.description}")
            print()
        
        if available_count == 0 and not game_config.are_all_passives_unlocked():
            print(f"{YELLOW}현재 선택 가능한 패시브가 없습니다. 패시브 없이 진행하세요!{RESET}")
        
        print(f"{CYAN}💡 팁: 패시브를 선택하지 않고 Enter만 누르면 패시브 없이 게임을 시작할 수 있습니다.{RESET}")
        print()
    
    def get_trait_effects_for_situation(self, situation: str, **kwargs) -> Dict[str, Any]:
        """현재 상황에 맞는 특성 효과 반환"""
        all_effects = {}
        
        for trait in self.active_traits:
            # trait가 딕셔너리인 경우와 객체인 경우 모두 처리
            if isinstance(trait, dict):
                is_active = trait.get('is_active', True)
                effect_type = trait.get('effect_type', 'passive')
            else:
                is_active = getattr(trait, 'is_active', True)
                effect_type = getattr(trait, 'effect_type', 'passive')
                
            if not is_active:
                continue
                
            if effect_type == "passive":
                effects = self._apply_passive_trait(trait, situation, **kwargs)
                all_effects.update(effects)
            elif effect_type == "trigger":
                effects = self._apply_trigger_trait(trait, situation, **kwargs)
                all_effects.update(effects)
                
        return all_effects
    
    def get_effective_stats(self, situation: str = "normal", **kwargs) -> Dict[str, int]:
        """특성이 적용된 실제 능력치 반환"""
        base_stats = {
            "physical_attack": self.physical_attack,
            "magic_attack": self.magic_attack,
            "physical_defense": self.physical_defense,
            "magic_defense": self.magic_defense,
            "speed": self.speed
        }
        
        # 특성 효과 적용
        trait_effects = self.apply_trait_effects(situation, **kwargs)
        
        # 능력치 수정
        if "damage_multiplier" in trait_effects:
            if self.preferred_damage_type == "physical":
                base_stats["physical_attack"] = int(base_stats["physical_attack"] * trait_effects["damage_multiplier"])
            else:
                base_stats["magic_attack"] = int(base_stats["magic_attack"] * trait_effects["damage_multiplier"])
                
        if "stat_boost" in trait_effects:
            boost = trait_effects["stat_boost"]
            base_stats["physical_attack"] = int(base_stats["physical_attack"] * (1 + boost))
            base_stats["magic_attack"] = int(base_stats["magic_attack"] * (1 + boost))
            
        return base_stats
        
    def set_brave_stats_from_data(self, char_data: dict):
        """캐릭터 데이터에서 Brave 스탯 설정 (안전한 예외처리 포함)"""
        try:
            from .balance import GameBalance
            
            # 데이터베이스에 명시된 값이 있으면 검증 후 사용
            if 'int_brv' in char_data and 'max_brv' in char_data:
                self.int_brv = GameBalance.validate_brave_value(
                    char_data['int_brv'], 
                    GameBalance.MIN_INT_BRV, 
                    GameBalance.MAX_INT_BRV
                )
                self.max_brv = GameBalance.validate_brave_value(
                    char_data['max_brv'],
                    GameBalance.MIN_MAX_BRV,
                    GameBalance.MAX_MAX_BRV
                )
                
                # INT BRV가 MAX BRV보다 큰 경우 보정
                if self.int_brv > self.max_brv:
                    self.int_brv = min(self.int_brv, self.max_brv)
                    
            else:
                # 없으면 밸런스 시스템에서 계산
                balance_stats = GameBalance.get_character_brave_stats(self.character_class, self.level)
                self.int_brv = balance_stats['int_brv']
                self.max_brv = balance_stats['max_brv']
                
            # 추가 밸런스 스탯 적용 (안전한 기본값 포함)
            balance_stats = GameBalance.get_character_brave_stats(self.character_class, self.level)
            self.brave_bonus_rate = balance_stats.get('brv_efficiency', 1.0)
            self.brv_loss_resistance = balance_stats.get('brv_loss_resistance', 1.0)
            
            # Brave 포인트 재설정
            self.initialize_brave_points()
            
        except Exception as e:
            # 오류 발생 시 안전한 기본값 설정
            import logging
            logging.warning(f"Error setting brave stats for {self.name}: {e}")
            
            self.int_brv = 800
            self.max_brv = 99500
            self.brave_bonus_rate = 1.0
            self.brv_loss_resistance = 1.0
            self.initialize_brave_points()
        
    @property
    def limited_max_hp(self) -> int:
        """상처에 의해 제한된 최대 HP (장비 보너스 포함)"""
        try:
            return self.get_total_max_hp() - self.wounds
        except (AttributeError, TypeError):
            # get_total_max_hp 메서드가 없거나 오류 시 기본 max_hp 사용
            return self.max_hp - self.wounds
        
    @property
    def max_wounds(self) -> int:
        """최대 상처량 (최대 HP의 75%, 장비 보너스 포함)"""
        try:
            return int(self.get_total_max_hp() * 0.75)
        except (AttributeError, TypeError):
            # get_total_max_hp 메서드가 없거나 오류 시 기본 max_hp 사용
            return int(self.max_hp * 0.75)
        
    def add_wounds(self, wound_amount: int):
        """상처 추가 (direct wound damage)"""
        if not self.is_alive:
            return
        
        wound_amount = max(0, int(wound_amount))
        self.wounds = min(self.wounds + wound_amount, self.max_wounds)
        
    def take_damage(self, damage: int, damage_source: str = "", ignore_armor: bool = False) -> int:
        """데미지를 받고 실제 입은 데미지량 반환"""
        if not self.is_alive:
            return 0
        
        # 🌑 암살자 그림자 방어 (피격 시 그림자 1개 소모로 50% 피해 감소)
        if (self.character_class == "암살자" and 
            hasattr(self, 'status_effects') and 
            any(effect.status_type == "그림자축적" for effect in self.status_effects) and
            damage > 0):
            
            # 그림자 스택을 찾아서 1개 소모
            for effect in self.status_effects[:]:  # 복사본으로 순회
                if effect.status_type == "그림자축적":
                    if effect.effect_value > 0:
                        # 그림자 방어 발동
                        original_damage = damage
                        damage = int(damage * 0.5)  # 50% 피해 감소
                        reduced_damage = original_damage - damage
                        
                        # 그림자 1개 소모
                        effect.effect_value -= 1
                        print(f"🌑💀 그림자 방어 발동! 그림자 1개를 소모하여 {reduced_damage} 피해 감소 ({original_damage} → {damage})")
                        
                        # 그림자가 0개가 되면 상태효과 제거
                        if effect.effect_value <= 0:
                            self.status_effects.remove(effect)
                            print(f"🌑 {self.name}의 마지막 그림자가 사라졌습니다...")
                        else:
                            print(f"🌑 잔여 그림자: {effect.effect_value}개")
                    break

        # 🛡️ 피의 방패 보호막 확인 (암흑기사)
        if hasattr(self, 'blood_shield') and self.blood_shield > 0:
            shield_absorbed = min(damage, self.blood_shield)
            self.blood_shield -= shield_absorbed
            damage -= shield_absorbed
            print(f"🛡️ 피의 방패가 {shield_absorbed} 데미지를 흡수! (보호막 잔여: {self.blood_shield})")
            
            # 보호막이 모두 소진되면 지속시간도 초기화
            if self.blood_shield <= 0:
                self.blood_shield = 0
                if hasattr(self, 'blood_shield_turns'):
                    self.blood_shield_turns = 0
                print("🛡️ 피의 방패가 완전히 파괴되었습니다!")
            
            # 보호막이 모든 데미지를 흡수한 경우
            if damage <= 0:
                return shield_absorbed
        
        # 수호자 보호 효과 확인 (파티원 중에 수호자 자세 전사가 있는지)
        try:
            guardian_protection = self._check_guardian_protection()
            if guardian_protection:
                damage = int(damage * 0.7)  # 수호자가 있으면 30% 데미지 감소
                print(f"🛠️ 수호자의 보호로 {self.name}이(가) 받는 데미지 30% 감소!")
        except AttributeError:
            # _check_guardian_protection 메서드가 없는 경우 무시
            pass
            
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        
        # 상처 누적 (받은 데미지의 25%)
        wound_increase = int(actual_damage * 0.25)
        self.wounds = min(self.wounds + wound_increase, self.max_wounds)
        
        if self.current_hp <= 0:
            self.current_hp = 0
            
            # 재기의 기회 (Second Chance) 능력 확인
            if hasattr(self, 'game_instance') and self.game_instance:
                if hasattr(self.game_instance, 'permanent_progression'):
                    permanent_prog = self.game_instance.permanent_progression
                    if permanent_prog.has_ability("second_chance"):
                        # 게임당 사용 가능 횟수 확인
                        if not hasattr(self.game_instance, 'second_chance_uses'):
                            self.game_instance.second_chance_uses = 0
                        
                        max_uses = permanent_prog.upgrades["second_chance"].current_level
                        if self.game_instance.second_chance_uses < max_uses:
                            # 20% 확률로 부활
                            import random
                            if random.random() < 0.20:  # 20% 확률
                                revival_hp = int(self.max_hp * 0.30)  # 30% HP로 부활
                                self.current_hp = revival_hp
                                self.is_alive = True
                                self.game_instance.second_chance_uses += 1
                                
                                print(f"\n✨ {self.name}이(가) 재기의 기회로 부활했습니다! ({self.game_instance.second_chance_uses}/{max_uses})")
                                print(f"💖 HP {revival_hp}로 되살아났습니다!")
                                return actual_damage
            
            # 부활하지 못했거나 능력이 없는 경우
            self.is_alive = False
            print(f"{self.name}이(가) 쓰러졌습니다!")
            
        return actual_damage
        
    def heal(self, heal_amount: int) -> int:
        """회복하고 실제 회복량 반환 - 영구 성장 보너스 적용"""
        if not self.is_alive:
            return 0
            
        # 상처 치유술 업그레이드 보너스 적용
        healing_bonus = 1.0
        if hasattr(self, 'game_instance') and self.game_instance and hasattr(self.game_instance, 'permanent_progression'):
            wound_healing_bonus = self.game_instance.permanent_progression.get_passive_bonus("wound_healing")
            if wound_healing_bonus > 0:
                healing_bonus = 1.0 + (wound_healing_bonus / 100.0)
        
        # 전사 특성: 불굴의 의지 - 방어형 자세에서 회복량 2배
        if (hasattr(self, 'apply_trait_effects') and 
            hasattr(self, 'current_stance') and 
            self.current_stance == "defensive"):
            trait_effects = self.apply_trait_effects("healing")
            healing_multiplier = trait_effects.get("healing_multiplier", 1.0)
            healing_bonus *= healing_multiplier
            if healing_multiplier > 1.0:
                print(f"🛡️ {self.name}의 불굴의 의지 (방어형)로 회복량 {int((healing_multiplier-1)*100)}% 증가!")
                
        # 치유량에 보너스 적용
        enhanced_heal_amount = int(heal_amount * healing_bonus)
        
        # 제한된 최대 HP까지 회복
        possible_heal = min(enhanced_heal_amount, self.limited_max_hp - self.current_hp)
        self.current_hp += possible_heal
        
        # 초과 회복량이 있다면 상처 회복 (보너스도 적용)
        excess_heal = enhanced_heal_amount - possible_heal
        if excess_heal > 0:
            wound_heal = int(excess_heal * 0.25 * healing_bonus)  # 상처 치유에도 보너스 적용
            actual_wound_heal = min(wound_heal, self.wounds)
            self.wounds -= actual_wound_heal
            
            # 상처가 회복되면 추가로 HP 회복 가능
            additional_heal = min(actual_wound_heal, self.max_hp - self.current_hp)
            self.current_hp += additional_heal
            possible_heal += additional_heal
            
        return possible_heal
        
    def revive(self, hp_percentage: float = 0.25):
        """부활 (기본적으로 최대 HP의 25%로)"""
        if self.is_alive:
            return
            
        self.is_alive = True
        self.current_hp = int(self.limited_max_hp * hp_percentage)
        print(f"{self.name}이(가) 부활했습니다!")
    
    def use_mp(self, mp_cost: int) -> bool:
        """MP 사용"""
        if self.current_mp >= mp_cost:
            self.current_mp -= mp_cost
            return True
        return False
    
    def recover_mp(self, mp_amount: int):
        """MP 회복"""
        self.current_mp = min(self.max_mp, self.current_mp + mp_amount)
    
    def on_step_taken(self):
        """걸음을 걸었을 때 호출 (상처와 MP 회복)"""
        self.steps_taken += 1
        
        # 매 3걸음마다 상처가 1씩 회복
        if self.steps_taken % 3 == 0 and self.wounds > 0:
            self.wounds = max(0, self.wounds - 1)
        
        # 매 2걸음마다 MP가 1씩 회복
        if self.steps_taken % 2 == 0:
            self.recover_mp(1)
    
    def get_mp_bar(self, length: int = 10) -> str:
        """MP 바 표시"""
        if self.max_mp == 0:
            return "[" + "□" * length + "]"
        
        filled = int((self.current_mp / self.max_mp) * length)
        empty = length - filled
        return "[" + "■" * filled + "□" * empty + "]"
        
    def update_atb(self):
        """ATB 게이지 업데이트 - 안전한 버전"""
        if self.is_alive and hasattr(self, 'atb_gauge'):
            # ATB 업데이트 속도를 1/5로 느리게 조정
            old_gauge = self.atb_gauge
            self.atb_gauge = min(1000, self.atb_gauge + (self.atb_speed / 5.0))
            
            # 디버그: ATB 변화 확인
            if abs(self.atb_gauge - old_gauge) > 0:
                pass  # 필요시 디버그 출력
            
            # 안전장치: 1000을 절대 초과하지 않도록
            if self.atb_gauge > 1000:
                self.atb_gauge = 1000
            
    def reset_atb(self):
        """ATB 게이지 리셋 - 강화된 버전"""
        self.atb_gauge = 0
        # 추가: 캐스팅 관련 상태도 리셋
        if hasattr(self, 'is_casting'):
            self.is_casting = False
        if hasattr(self, 'casting_skill'):
            self.casting_skill = None
        
    def can_act(self) -> bool:
        """행동 가능한지 확인 - 개선된 버전"""
        if not self.is_alive:
            return False
        if not hasattr(self, 'atb_gauge'):
            self.atb_gauge = 0
            return False
        if self.atb_gauge < 1000:
            return False
        if hasattr(self, 'status_manager') and not self.status_manager.can_act():
            return False
        return True
        
    def get_effective_stats(self) -> dict:
        """상태이상과 장비를 고려한 실제 능력치"""
        base_stats = {
            "physical_attack": self.physical_attack,
            "magic_attack": self.magic_attack,
            "physical_defense": self.physical_defense,
            "magic_defense": self.magic_defense,
            "speed": self.speed
        }
        
        # 장비 보너스 적용
        if self.equipped_weapon:
            for stat, bonus in self.equipped_weapon.stats.items():
                if stat in base_stats:
                    base_stats[stat] += bonus
                    
        if self.equipped_armor:
            for stat, bonus in self.equipped_armor.stats.items():
                if stat in base_stats:
                    base_stats[stat] += bonus
                    
        if self.equipped_accessory:
            for stat, bonus in self.equipped_accessory.stats.items():
                if stat in base_stats:
                    base_stats[stat] += bonus
        
        # 상태이상 수정치 적용
        modifiers = self.status_manager.get_stat_modifiers()
        for stat in base_stats:
            base_stats[stat] = int(base_stats[stat] * modifiers.get(stat, 1.0))
            
        return base_stats
    
    def get_current_attack_element(self) -> str:
        """현재 공격 속성 반환 (장신구에 의한 변경 포함)"""
        # 속성 변경 장신구 확인
        if self.equipped_accessory and hasattr(self.equipped_accessory, 'attack_element'):
            return self.equipped_accessory.attack_element
        
        # 무기의 속성 확인
        if self.equipped_weapon and hasattr(self.equipped_weapon, 'element'):
            return self.equipped_weapon.element
        
        # 기본적으로 무속성
        return "무속성"
    
    def has_elemental_accessory(self) -> bool:
        """속성 변경 장신구를 착용하고 있는지 확인"""
        return (self.equipped_accessory and 
                hasattr(self.equipped_accessory, 'attack_element') and
                self.equipped_accessory.attack_element != "무속성")
    
    def get_elemental_bonus_effects(self) -> dict:
        """속성 장신구의 특수 효과 반환"""
        if not self.has_elemental_accessory():
            return {}
        
        return getattr(self.equipped_accessory, 'special_effects', {})
    
    def get_current_carry_weight(self) -> float:
        """현재 들고 있는 무게 반환"""
        total_weight = self.inventory.get_total_weight()
        
        # 장착된 아이템 무게 추가
        if self.equipped_weapon and hasattr(self.equipped_weapon, 'weight'):
            total_weight += self.equipped_weapon.weight
        if self.equipped_armor and hasattr(self.equipped_armor, 'weight'):
            total_weight += self.equipped_armor.weight
        if self.equipped_accessory and hasattr(self.equipped_accessory, 'weight'):
            total_weight += self.equipped_accessory.weight
            
        return total_weight
    
    def can_carry_item(self, item_weight: float) -> bool:
        """아이템을 들 수 있는지 확인"""
        return (self.get_current_carry_weight() + item_weight) <= self.max_carry_weight
    
    def get_carry_capacity_ratio(self) -> float:
        """하중 용량 비율 반환 (0.0 ~ 1.0)"""
        return self.get_current_carry_weight() / self.max_carry_weight
    
    def is_overloaded(self) -> bool:
        """과중량 상태인지 확인"""
        return self.get_current_carry_weight() > self.max_carry_weight
    
    def get_overload_penalty(self) -> Dict[str, float]:
        """과중량 페널티 반환"""
        if not self.is_overloaded():
            return {}
        
        overload_ratio = self.get_current_carry_weight() / self.max_carry_weight
        penalty_multiplier = max(0.0, overload_ratio - 1.0)
        
        return {
            "speed_penalty": penalty_multiplier * 0.5,  # 속도 50% 감소
            "accuracy_penalty": penalty_multiplier * 0.3,  # 명중률 30% 감소
            "stamina_drain": penalty_multiplier * 2.0  # 스태미나 소모 증가
        }
        
    def add_status_effect(self, effect: StatusEffect) -> str:
        """상태이상 추가"""
        return self.status_manager.add_effect(effect)
        
    def cure_all_status_effects(self) -> List[str]:
        """모든 부정적 상태이상 치료"""
        return self.status_manager.cure_all_negative_effects()
        
    def process_status_effects(self) -> List[str]:
        """상태이상 처리 (턴 시작 시)"""
        return self.status_manager.process_turn_effects(self)
        
    def equip_item(self, item: Item) -> bool:
        """아이템 장착 (인벤토리 연동 포함) - 중복 제거 방지"""
        # 먼저 인벤토리에서 아이템이 있는지 확인
        if hasattr(self, 'inventory') and self.inventory:
            if not self.inventory.has_item(item.name):
                print(f"⚠️ {self.name}의 인벤토리에 {item.name}이(가) 없습니다.")
                return False
            
            # 🔒 현재 수량 확인 (디버그용)
            current_count = self.inventory.items.get(item.name, 0)
            print(f"🔍 장착 전 {item.name} 보유 수량: {current_count}개")
        
        # 기존 장착된 아이템이 있다면 인벤토리로 반환
        old_item = None
        if item.item_type.value == "무기":
            old_item = self.equipped_weapon
            self.equipped_weapon = item
        elif item.item_type.value == "방어구":
            old_item = self.equipped_armor
            self.equipped_armor = item
        elif item.item_type.value == "장신구":
            old_item = self.equipped_accessory
            self.equipped_accessory = item
        else:
            return False
        
        # 기존 아이템을 인벤토리로 반환
        if old_item and hasattr(self, 'inventory') and self.inventory:
            self.inventory.add_item(old_item, 1)
            print(f"📦 {old_item.name}을(를) 인벤토리로 반환했습니다.")
        
        # 🎯 새 아이템을 인벤토리에서 1개만 제거 (안전한 제거)
        if hasattr(self, 'inventory') and self.inventory:
            if self.inventory.has_item(item.name):
                # 제거 전 수량 확인
                before_count = self.inventory.items.get(item.name, 0)
                success = self.inventory.remove_item(item.name, 1)
                after_count = self.inventory.items.get(item.name, 0)
                
                if success:
                    print(f"🎒 {item.name}을(를) 장착했습니다. ({before_count}개 → {after_count}개)")
                else:
                    print(f"❌ {item.name} 제거 실패")
                    return False
            else:
                print(f"⚠️ 장착 시점에 {item.name}이(가) 인벤토리에 없습니다.")
                return False
        
        return True
    
    def unequip_item(self, slot: str) -> Optional[Item]:
        """아이템 장착 해제"""
        unequipped_item = None
        
        if slot == "무기" or slot == "weapon":
            unequipped_item = self.equipped_weapon
            self.equipped_weapon = None
        elif slot == "방어구" or slot == "armor":
            unequipped_item = self.equipped_armor
            self.equipped_armor = None
        elif slot == "장신구" or slot == "accessory":
            unequipped_item = self.equipped_accessory
            self.equipped_accessory = None
        
        return unequipped_item
    
    def get_equipped_items(self) -> Dict[str, Optional[Item]]:
        """장착된 아이템 목록 반환"""
        return {
            "무기": self.equipped_weapon,
            "방어구": self.equipped_armor,
            "장신구": self.equipped_accessory
        }
    
    def gain_experience(self, exp: int) -> bool:
        """경험치 획득 및 레벨업 처리"""
        self.experience += exp
        leveled_up = False
        
        while self.experience >= self.experience_to_next:
            leveled_up = True
            self.experience -= self.experience_to_next
            old_level = self.level
            self.level += 1
            
            # 능력치 증가
            stat_gains = self.calculate_level_up_gains()
            self.apply_level_up_gains(stat_gains)
            
            # 다음 레벨까지 필요한 경험치 계산 (더 가파른 곡선)
            # 기본 90 + 레벨^1.3 * 40로 곡선 증가
            import math
            self.experience_to_next = int(90 + (self.level ** 1.3) * 40)
            
            print(f"🎉 {self.name}이(가) 레벨 {old_level} → {self.level}로 상승!")
            self.show_stat_gains(stat_gains)
            
            # 레벨업 자동 저장 트리거
            try:
                from game.auto_save_system import on_level_up
                on_level_up(self.name, self.level)
            except Exception as e:
                # 자동 저장 실패해도 게임 진행에는 영향 없음
                pass
            
        return leveled_up
    
    def calculate_level_up_gains(self) -> dict:
        """레벨업 시 능력치 증가량 계산"""
        # 클래스별 성장률 (MP 성장량을 대폭 줄임)
        growth_rates = {
            "전사": {"hp": 18, "mp": 2, "p_atk": 4, "m_atk": 3, "p_def": 4, "m_def": 4, "speed": 4},
            "아크메이지": {"hp": 11, "mp": 4, "p_atk": 2, "m_atk": 7, "p_def": 2, "m_def": 5, "speed": 4},  # 총 35
            "궁수": {"hp": 15, "mp": 2, "p_atk": 6, "m_atk": 2, "p_def": 3, "m_def": 3, "speed": 6},  # 총 37
            "도적": {"hp": 13, "mp": 1, "p_atk": 6, "m_atk": 2, "p_def": 3, "m_def": 3, "speed": 8},  # 총 36
            "성기사": {"hp": 17, "mp": 3, "p_atk": 5, "m_atk": 3, "p_def": 6, "m_def": 5, "speed": 3},  # 총 42
            "암흑기사": {"hp": 17, "mp": 2, "p_atk": 6, "m_atk": 4, "p_def": 4, "m_def": 4, "speed": 4},  # 총 41
            "몽크": {"hp": 15, "mp": 2, "p_atk": 7, "m_atk": 3, "p_def": 4, "m_def": 4, "speed": 6},  # 총 41
            "바드": {"hp": 10, "mp": 3, "p_atk": 3, "m_atk": 5, "p_def": 3, "m_def": 4, "speed": 5},  # 총 33
            "네크로맨서": {"hp": 12, "mp": 4, "p_atk": 2, "m_atk": 7, "p_def": 2, "m_def": 6, "speed": 3},  # 총 36
            "용기사": {"hp": 16, "mp": 2, "p_atk": 6, "m_atk": 4, "p_def": 5, "m_def": 4, "speed": 4},  # 총 41
            "검성": {"hp": 15, "mp": 1, "p_atk": 7, "m_atk": 2, "p_def": 4, "m_def": 3, "speed": 5},  # 총 37
            "정령술사": {"hp": 10, "mp": 4, "p_atk": 3, "m_atk": 7, "p_def": 3, "m_def": 5, "speed": 4},  # 총 36
            "암살자": {"hp": 12, "mp": 1, "p_atk": 7, "m_atk": 2, "p_def": 2, "m_def": 2, "speed": 8},  # 총 34
            "기계공학자": {"hp": 14, "mp": 2, "p_atk": 5, "m_atk": 4, "p_def": 4, "m_def": 3, "speed": 4},  # 총 36
            "무당": {"hp": 11, "mp": 3, "p_atk": 3, "m_atk": 7, "p_def": 3, "m_def": 6, "speed": 4},  # 총 37
            "해적": {"hp": 15, "mp": 1, "p_atk": 6, "m_atk": 2, "p_def": 4, "m_def": 3, "speed": 6},  # 총 37
            "사무라이": {"hp": 15, "mp": 1, "p_atk": 6, "m_atk": 3, "p_def": 4, "m_def": 4, "speed": 5},  # 총 38
            "드루이드": {"hp": 16, "mp": 3, "p_atk": 3, "m_atk": 6, "p_def": 3, "m_def": 5, "speed": 4},  # 총 40
            "철학자": {"hp": 10, "mp": 4, "p_atk": 2, "m_atk": 6, "p_def": 4, "m_def": 7, "speed": 3},  # 총 36
            "시간술사": {"hp": 11, "mp": 4, "p_atk": 3, "m_atk": 6, "p_def": 3, "m_def": 5, "speed": 4},  # 총 36
            "연금술사": {"hp": 12, "mp": 3, "p_atk": 4, "m_atk": 6, "p_def": 3, "m_def": 4, "speed": 4},  # 총 36
            "검투사": {"hp": 15, "mp": 1, "p_atk": 7, "m_atk": 3, "p_def": 4, "m_def": 3, "speed": 5},  # 총 38
            "기사": {"hp": 19, "mp": 1, "p_atk": 6, "m_atk": 3, "p_def": 6, "m_def": 4, "speed": 3},  # 총 42
            "신관": {"hp": 13, "mp": 3, "p_atk": 3, "m_atk": 6, "p_def": 4, "m_def": 7, "speed": 3},  # 총 39
            "마검사": {"hp": 15, "mp": 2, "p_atk": 5, "m_atk": 5, "p_def": 4, "m_def": 4, "speed": 4},  # 총 39
            "차원술사": {"hp": 8, "mp": 4, "p_atk": 2, "m_atk": 8, "p_def": 2, "m_def": 6, "speed": 3},  # 총 33
            "광전사": {"hp": 29, "mp": 1, "p_atk": 5, "m_atk": 1, "p_def": 1, "m_def": 1, "speed": 6},  # 총 44
            "마법사": {"hp": 11, "mp": 4, "p_atk": 2, "m_atk": 7, "p_def": 2, "m_def": 5, "speed": 4},  # 총 35
            "성직자": {"hp": 13, "mp": 3, "p_atk": 3, "m_atk": 6, "p_def": 4, "m_def": 7, "speed": 3},  # 총 39
            "Enemy": {"hp": 20, "mp": 1, "p_atk": 4, "m_atk": 4, "p_def": 4, "m_def": 4, "speed": 3}
        }
        
        base_growth = growth_rates.get(self.character_class, growth_rates["Enemy"])
        
        # 약간의 랜덤 요소 추가 (±5%)
        gains = {}
        for stat, base_gain in base_growth.items():
            variation = random.randint(-5, 5) / 100
            gains[stat] = max(1, int(base_gain * (1 + variation)))
            
        return gains
    
    def apply_level_up_gains(self, gains: dict):
        """레벨업 능력치 증가 적용"""
        self.max_hp += gains["hp"]
        self.current_hp += gains["hp"]  # 레벨업 시 HP도 같이 회복
        
        # MP 성장 적용
        if "mp" in gains:
            self.max_mp += gains["mp"]
            self.current_mp += gains["mp"]  # 레벨업 시 MP도 같이 회복
        
        self.physical_attack += gains["p_atk"]
        self.magic_attack += gains["m_atk"]
        self.physical_defense += gains["p_def"]
        self.magic_defense += gains["m_def"]
        self.speed += gains["speed"]
        self.atb_speed = self.get_total_speed()  # 장비 보너스 포함된 속도로 업데이트
        
        # Brave 능력치도 재계산
        self.update_brave_on_level_up()
    
    def update_brave_on_level_up(self):
        """레벨업 시 Brave 능력치 업데이트"""
        try:
            from .balance import GameBalance
            
            # 이전 값 저장 (디버그용)
            old_int_brv = self.int_brv
            old_max_brv = self.max_brv
            
            balance_stats = GameBalance.get_character_brave_stats(self.character_class, self.level)
            
            # 기존 Brave 비율 유지하면서 업데이트
            old_brave_ratio = self.current_brave / max(1, self.int_brv)
            
            self.int_brv = balance_stats['int_brv']
            self.max_brv = balance_stats['max_brv']
            self.current_brave = int(self.int_brv * old_brave_ratio)
            self.brave_bonus_rate = balance_stats.get('brv_efficiency', 1.0)
            self.brv_loss_resistance = balance_stats.get('brv_loss_resistance', 1.0)
        except Exception as e:
            # GameBalance 실패 시 간단한 백업 성장
            level_multiplier = 1 + (self.level - 1) * 0.12  # 레벨당 12% 증가
            base_int_brv = 350  # 적정 기본값
            base_max_brv = 2800  # 적정 기본값
            
            self.int_brv = int(base_int_brv * level_multiplier)
            self.max_brv = int(base_max_brv * level_multiplier)
    
    def show_stat_gains(self, gains: dict):
        """능력치 증가 표시"""
        print(f"  💪 HP +{gains['hp']}, MP +{gains.get('mp', 0)}, 물리공격 +{gains['p_atk']}, 마법공격 +{gains['m_atk']}")
        print(f"  🛡️ 물리방어 +{gains['p_def']}, 마법방어 +{gains['m_def']}, 속도 +{gains['speed']}")
        print(f"  ⚡ 현재 HP: {self.current_hp}/{self.max_hp}, MP: {self.current_mp}/{self.max_mp}")

    def get_skills(self) -> List[str]:
        """캐릭터가 사용할 수 있는 스킬 목록"""
        # 기본 스킬
        skills = ["공격", "방어"]
        
        # 레벨에 따른 스킬 해금
        if self.level >= 3:
            if self.character_class in ["전사", "기사"]:
                skills.append("강타")
            elif self.character_class in ["마법사", "성직자"]:
                skills.append("힐")
            elif self.character_class == "도적":
                skills.append("독 찌르기")
            elif self.character_class == "궁수":
                skills.append("관통사격")
        
        if self.level >= 5:
            if self.character_class == "전사":
                skills.append("분노")
            elif self.character_class == "마법사":
                skills.append("파이어볼")
            elif self.character_class == "성직자":
                skills.append("축복")
            elif self.character_class == "기사":
                skills.append("가드")
            elif self.character_class == "도적":
                skills.append("그림자 이동")
            elif self.character_class == "궁수":
                skills.append("삼연사")
        
        return skills
        
    def use_item(self, item_name: str) -> bool:
        """아이템 사용"""
        if not self.inventory.has_item(item_name):
            return False
            
        # 아이템 데이터베이스에서 아이템 찾기
        all_items = ItemDatabase.get_all_items()
        item = None
        for db_item in all_items:
            if db_item.name == item_name:
                item = db_item
                break
                
        if item and item.use_item(self):
            self.inventory.remove_item(item_name, 1)
            return True
        return False
        
    def calculate_damage_to(self, target: 'Character', skill_modifier: float = 1.0, 
                           damage_type: str = None) -> int:
        """대상에게 가할 데미지 계산"""
        if not self.is_alive or not target.is_alive:
            return 0
            
        # 데미지 타입 결정 (지정되지 않으면 선호하는 타입 사용)
        if damage_type is None:
            damage_type = self.preferred_damage_type
            
        # 실제 능력치 가져오기
        attacker_stats = self.get_effective_stats()
        defender_stats = target.get_effective_stats()
            
        # 공격력과 방어력 선택
        if damage_type == "magic":
            attacker_power = attacker_stats["magic_attack"]
            defender_defense = defender_stats["magic_defense"]
        else:  # physical
            attacker_power = attacker_stats["physical_attack"]
            defender_defense = defender_stats["physical_defense"]
            
        # 기본 데미지 계산: (공격력 / 방어력) * 기타 요소
        base_damage = (attacker_power / max(defender_defense, 1)) * skill_modifier
        
        # 레벨 차이 보정 (레벨당 5% 보너스/페널티)
        level_modifier = 1.0 + ((self.level - target.level) * 0.05)
        
        # 스피드 차이 보정 (빠른 캐릭터가 약간 유리)
        speed_modifier = 1.0 + ((attacker_stats["speed"] - defender_stats["speed"]) * 0.01)
        
        # 랜덤 요소 (90% ~ 110%)
        random_modifier = random.uniform(0.9, 1.1)
        
        final_damage = int(base_damage * level_modifier * speed_modifier * random_modifier)
        return max(1, final_damage)  # 최소 1 데미지
        
    def get_status_string(self) -> str:
        """상태 문자열 반환"""
        hp_bar = self.get_hp_bar()
        mp_bar = self.get_mp_bar()
        atb_bar = self.get_atb_bar()
        
        # 이름을 고정 길이로 자르거나 패딩
        name_field = f"{self.name[:10]:10}"  # 최대 10글자로 제한하고 패딩
        class_field = f"{self.character_class[:8]:8}"  # 최대 8글자로 제한하고 패딩
        
        # HP/MP에 이모지와 색상 추가
        hp_ratio = self.current_hp / self.limited_max_hp if self.limited_max_hp > 0 else 0
        mp_ratio = self.current_mp / self.max_mp if self.max_mp > 0 else 0
        
        # HP 색상 및 이모지
        if hp_ratio > 0.3:
            hp_text = green(f"HP {self.current_hp:3}/{self.limited_max_hp:3}")
        else:
            hp_text = red(f"HP {self.current_hp:3}/{self.limited_max_hp:3}")

        # MP 색상 및 이모지
        if mp_ratio > 0.7:
            mp_text = cyan(f"MP {self.current_mp:3}/{self.max_mp:3}")
        elif mp_ratio > 0.3:
            mp_text = blue(f"MP {self.current_mp:3}/{self.max_mp:3}")
        else:
            mp_text = magenta(f"MP {self.current_mp:3}/{self.max_mp:3}")
        
        status = f"{name_field} | {class_field} | Lv.{self.level:2} | "
        status += f"{hp_text} {hp_bar} | "
        status += f"{mp_text} {mp_bar} | "
        status += f"ATB {atb_bar} | SPD:{self.get_effective_stats()['speed']:2}"
        
        # 캐릭터별 기믹 표시 추가 - 이모지와 함께
        mechanics = ""
        
        # 전사 자세 시스템
        if hasattr(self, 'current_stance') and self.current_stance:
            stance_emoji = {"balanced": "⚖️", "aggressive": "⚔️", "defensive": "🛡️", 
                          "swift": "💨", "berserker": "💀", "guardian": "🗡️"}
            stance_names = {"balanced": "BAL", "aggressive": "ATK", "defensive": "DEF",
                          "swift": "SPD", "berserker": "RAGE", "guardian": "GUARD"}
            emoji = stance_emoji.get(self.current_stance, "⚖️")
            name = stance_names.get(self.current_stance, "BAL")
            mechanics += f" {emoji}STANCE:{name}"
        
        # 궁수 조준 포인트
        if hasattr(self, 'aim_points') and self.aim_points > 0:
            mechanics += f" 🎯AIM:{self.aim_points}"
        elif hasattr(self, 'precision_points') and self.precision_points > 0:
            mechanics += f" 🎯AIM:{self.precision_points}"
        
        # 도적 독 스택
        if hasattr(self, 'poison_stacks') and self.poison_stacks > 0:
            mechanics += f" 🐍VENOM:{self.poison_stacks}"
        elif hasattr(self, 'venom_power') and self.venom_power > 0:
            mechanics += f" 🐍VENOM:{self.venom_power}%"
        
        # 암살자 그림자
        if hasattr(self, 'shadow_count') and self.shadow_count > 0:
            mechanics += f" 🌑SHADOW:{self.shadow_count}"
        elif hasattr(self, 'shadows') and self.shadows > 0:
            mechanics += f" 🌑SHADOW:{self.shadows}"
        
        # 검성 검기
        if hasattr(self, 'sword_aura') and self.sword_aura > 0:
            mechanics += f" ⚡AURA:{self.sword_aura}"
        elif hasattr(self, 'sword_aura_stacks') and self.sword_aura_stacks > 0:
            mechanics += f" ⚡AURA:{self.sword_aura_stacks}"
        
        # 바드 멜로디 - 한글 음계 표시
        if hasattr(self, 'melody_notes') and len(self.melody_notes) > 0:
            note_names = ["도", "레", "미", "파", "솔", "라", "시"]
            melody_str = "/".join([note_names[note] for note in self.melody_notes if 0 <= note < len(note_names)])
            mechanics += f" 🎵MELODY:{melody_str}"
        elif hasattr(self, 'melody_stacks') and self.melody_stacks > 0:
            mechanics += f" 🎵MELODY:{self.melody_stacks}"
        elif hasattr(self, 'song_power') and self.song_power > 0:
            mechanics += f" 🎵MELODY:{self.song_power}"
        
        # 광전사 분노 (0일 때도 표시)
        if hasattr(self, 'rage_stacks'):
            mechanics += f" 💥RAGE:{self.rage_stacks}"
        elif hasattr(self, 'rage_points'):
            mechanics += f" 💥RAGE:{self.rage_points}"
        
        # 몽크 기
        if hasattr(self, 'ki_energy') and self.ki_energy > 0:
            mechanics += f" 🔥KI:{self.ki_energy}"
        elif hasattr(self, 'combo_count') and self.combo_count > 0:
            mechanics += f" 👊COMBO:{self.combo_count}"
        
        # 네크로맨서 네크로 에너지
        if hasattr(self, 'necro_energy') and self.necro_energy > 0:
            mechanics += f" 💀NECRO:{self.necro_energy}"
        elif hasattr(self, 'soul_power') and self.soul_power > 0:
            mechanics += f" 👻SOUL:{self.soul_power}"
        
        # 정령술사 정령 친화도
        if hasattr(self, 'spirit_bond') and self.spirit_bond > 0:
            mechanics += f" 🌟SPIRIT:{self.spirit_bond}"
        elif hasattr(self, 'elemental_affinity') and self.elemental_affinity > 0:
            mechanics += f" 🌟ELEM:{self.elemental_affinity}"
        
        # 시간술사 시간 조작
        if hasattr(self, 'time_marks') and self.time_marks > 0:
            mechanics += f" ⏰TIME:{self.time_marks}"
        elif hasattr(self, 'temporal_energy') and self.temporal_energy > 0:
            mechanics += f" ⏰TEMP:{self.temporal_energy}"
        
        # 아크메이지 원소 카운트
        if hasattr(self, 'fire_count') and self.fire_count > 0:
            mechanics += f" 🔥FIRE:{self.fire_count}"
        if hasattr(self, 'ice_count') and self.ice_count > 0:
            mechanics += f" ❄️ICE:{self.ice_count}"
        if hasattr(self, 'lightning_count') and self.lightning_count > 0:
            mechanics += f" ⚡LIGHT:{self.lightning_count}"
        
        # 용기사 용인
        if hasattr(self, 'dragon_marks') and self.dragon_marks > 0:
            mechanics += f" 🐲DRAGON:{self.dragon_marks}"
        elif hasattr(self, 'dragon_energy') and self.dragon_energy > 0:
            mechanics += f" 🐲ENERGY:{self.dragon_energy}"
        
        # 기계공학자 차지
        if hasattr(self, 'charge_level') and self.charge_level > 0:
            mechanics += f" 🔧CHARGE:{self.charge_level}"
        elif hasattr(self, 'turret_count') and self.turret_count > 0:
            mechanics += f" 🤖TURRET:{self.turret_count}"
        
        # 연금술사 연금 에너지
        if hasattr(self, 'alchemy_energy') and self.alchemy_energy > 0:
            mechanics += f" ⚗️ALCHEMY:{self.alchemy_energy}"
        
        # 검투사 투기장
        if hasattr(self, 'arena_points') and self.arena_points > 0:
            mechanics += f" 🏟️ARENA:{self.arena_points}"
        elif hasattr(self, 'gladiator_stacks') and self.gladiator_stacks > 0:
            mechanics += f" ⚔️GLAD:{self.gladiator_stacks}"
        
        # 무당 영혼력
        if hasattr(self, 'spirit_power') and self.spirit_power > 0:
            mechanics += f" 👻SPIRIT:{self.spirit_power}"
        elif hasattr(self, 'ritual_power') and self.ritual_power > 0:
            mechanics += f" 🔮RITUAL:{self.ritual_power}"
        
        # 차원술사 차원 에너지
        if hasattr(self, 'dimension_energy') and self.dimension_energy > 0:
            mechanics += f" 🌀DIM:{self.dimension_energy}"
        elif hasattr(self, 'portal_count') and self.portal_count > 0:
            mechanics += f" 🌀PORTAL:{self.portal_count}"
        
        status += mechanics
        
        # 상태이상 표시
        active_effects = self.status_manager.get_active_effects()
        if active_effects:
            status += f" | {'/'.join(active_effects[:2])}"  # 최대 2개만 표시
        
        if not self.is_alive:
            status += " [사망]"
            
        return status
        
    def get_hp_bar(self, length: int = 10) -> str:
        """HP 바 문자열 생성 (색상 적용, 간결한 형태)"""
        if self.limited_max_hp == 0:
            return red("✗✗✗✗✗")
            
        ratio = self.current_hp / self.limited_max_hp
        filled = int(ratio * length)
        bar = "█" * filled + "░" * (length - filled)
        
        # HP 비율에 따른 색상 적용
        if ratio > 0.7:
            return green(f"{bar}")
        elif ratio > 0.3:
            return yellow(f"{bar}")
        else:
            return red(f"{bar}")
        
    def get_mp_bar(self, length: int = 10) -> str:
        """MP 바 문자열 생성 (색상 적용, 간결한 형태)"""
        if self.max_mp == 0:
            return bright_black("─────")
            
        ratio = self.current_mp / self.max_mp
        filled = int(ratio * length)
        bar = "█" * filled + "░" * (length - filled)
        
        # MP 비율에 따른 색상 적용
        if ratio > 0.7:
            return cyan(f"{bar}")
        elif ratio > 0.3:
            return blue(f"{bar}")
        else:
            return magenta(f"{bar}")
        
    def get_atb_bar(self, length: int = 6) -> str:
        """ATB 게이지 바 문자열 생성 (색상 적용, 간결한 형태)"""
        # 캐스팅 중인 경우 캐스팅 진행률 표시
        if hasattr(self, 'is_casting') and self.is_casting:
            # 캐스팅 진행률 계산 (ATB 게이지 변화량 기준)
            if hasattr(self, 'casting_start_atb') and hasattr(self, 'atb_gauge'):
                cast_progress = (self.atb_gauge - self.casting_start_atb) / (10000 - self.casting_start_atb) if (10000 - self.casting_start_atb) > 0 else 0
                cast_progress = max(0, min(1.0, cast_progress))
            else:
                # 캐스팅 정보가 없다면 현재 ATB 비율 사용
                cast_progress = min(1.0, self.atb_gauge / 10000)
            
            filled = int(cast_progress * length)
            bar = "█" * filled + "░" * (length - filled)
            return bright_cyan(f"{bar}")
        
        # ATB 게이지는 0~10000 범위 (READY_THRESHOLD = 10000)
        ready_threshold = 10000
        ratio = min(1.0, self.atb_gauge / ready_threshold)
        filled = int(ratio * length)
        bar = "█" * filled + "░" * (length - filled)
        
        # ATB 게이지에 따른 색상 적용
        if ratio >= 1.0:
            return bright_yellow(f"{bar}")
        elif ratio > 0.7:
            return yellow(f"{bar}")
        else:
            return bright_white(f"{bar}")
    
    # === 플레이어 스킬 시스템 통합 ===
    
    def set_player_skill_system(self, skill_system):
        """플레이어 스킬 시스템 설정"""
        self._player_skill_system = skill_system
    
    def get_available_skills(self) -> List[Dict[str, Any]]:
        """사용 가능한 스킬 목록 반환"""
        if self._player_skill_system is None:
            return []
        return self._player_skill_system.get_available_skills(self)
    
    def can_use_skill(self, skill: Dict[str, Any]) -> bool:
        """스킬 사용 가능 여부 확인"""
        if self._player_skill_system is None:
            return False
        return self._player_skill_system.can_use_skill(self, skill)
    
    def use_skill(self, skill: Dict[str, Any], targets: List['Character'], allies: List['Character'] = None) -> List[str]:
        """스킬 사용"""
        if self._player_skill_system is None:
            return ["스킬 시스템이 없습니다."]
        
        if not self.can_use_skill(skill):
            return [f"{skill['name']} 사용 불가 (MP 부족 또는 기타 조건 미충족)"]
        
        return self._player_skill_system.execute_skill(self, skill, targets, allies)
    
    def get_skill_info(self, skill: Dict[str, Any]) -> str:
        """스킬 정보 텍스트 반환"""
        if self._player_skill_system is None:
            return "스킬 정보 없음"
        return self._player_skill_system.get_skill_description(skill)


class PartyManager:
    """파티 관리자 클래스"""
    
    def __init__(self):
        self.members: List[Character] = []
        self.max_size = 4
        self.shared_inventory = Inventory(max_size=100)  # 공용 인벤토리 (확장)
        self.party_gold = 0  # 파티 통합 골드
        self.total_steps = 0  # 총 걸음 수 추적
        self.game_instance = None  # 게임 인스턴스 참조 (패시브 효과용)
    
    def set_game_instance(self, game_instance):
        """게임 인스턴스 참조 설정"""
        self.game_instance = game_instance
        
    def get_total_carry_capacity(self) -> float:
        """파티 전체 하중 한계 계산 (전체 순수 공격력 기반) - 더 엄격하게"""
        total_attack = sum(member.physical_attack for member in self.get_alive_members())
        base_capacity = 10.0  # 기본 하중 (20 -> 50으로 증가)
        attack_bonus = total_attack * 0.025  # 공격력당 0.2kg (0.05 -> 0.2로 증가)
        return base_capacity + attack_bonus
        
    def get_current_carry_weight(self) -> float:
        """현재 파티 하중 계산 (식재료 포함)"""
        weight = self.shared_inventory.get_total_weight()
        
        # 식재료 무게 추가
        try:
            from game.cooking_system import cooking_system
            ingredient_weight = cooking_system.get_total_inventory_weight()
            weight += ingredient_weight
        except ImportError:
            pass
        
        return weight
    
    def add_step(self):
        """걸음 수 증가"""
        self.total_steps += 1
        
    def can_add_item_weight(self, weight: float) -> bool:
        """아이템 추가 가능 여부 (하중 기준)"""
        current_weight = self.get_current_carry_weight()
        max_weight = self.get_total_carry_capacity()
        return (current_weight + weight) <= max_weight
    
    def get_total_vision_range(self) -> int:
        """파티 전체의 시야 범위 계산"""
        base_vision = 3  # 기본 시야 범위
        vision_bonus = 0
        
        # 살아있는 모든 파티 멤버의 장비에서 vision_range 보너스 합산
        for member in self.get_alive_members():
            # 각 장비 슬롯 확인 (equipped_weapon, equipped_armor, equipped_accessory)
            equipment_slots = {
                'weapon': getattr(member, 'equipped_weapon', None),
                'armor': getattr(member, 'equipped_armor', None),
                'accessory': getattr(member, 'equipped_accessory', None)
            }
            
            for slot_name, equipment in equipment_slots.items():
                if equipment and hasattr(equipment, 'stats') and equipment.stats:
                    equipment_vision = equipment.stats.get('vision_range', 0)
                    if equipment_vision > 0:
                        vision_bonus += equipment_vision
        
        # 패시브 효과에서 시야 보너스 확인
        passive_vision_bonus = 0
        if hasattr(self, 'game_instance') and self.game_instance and hasattr(self.game_instance, 'party_passive_effects'):
            for passive in self.game_instance.party_passive_effects:
                effect_value = passive.get('effect_value', {})
                
                # 탐험가의 제6감 패시브
                if passive.get('effect_type') == 'explorer_instinct':
                    passive_vision = effect_value.get('vision_range', 0)
                    if passive_vision > 0:
                        passive_vision_bonus += passive_vision
                
                # 전술가의 감각 패시브
                elif passive.get('effect_type') == 'tactician_sense':
                    passive_vision = effect_value.get('vision_range', 0)
                    if passive_vision > 0:
                        passive_vision_bonus += passive_vision
        
        vision_bonus += passive_vision_bonus
        total_vision = base_vision + vision_bonus
        return total_vision
    
    def add_member(self, character: Character) -> bool:
        """파티 멤버 추가"""
        if len(self.members) >= self.max_size:
            print(f"파티가 가득 찼습니다. (최대 {self.max_size}명)")
            return False
            
        # 개별 골드를 파티 골드로 통합
        if hasattr(character, 'gold'):
            self.party_gold += character.gold
            character.gold = 0  # 개별 골드 초기화
            
        self.members.append(character)
        print(f"{character.name}이(가) 파티에 합류했습니다.")
        return True
        
    def remove_member(self, character: Character) -> bool:
        """파티 멤버 제거"""
        if character in self.members:
            self.members.remove(character)
            print(f"{character.name}이(가) 파티를 떠났습니다.")
            return True
        return False
        
    def has_members(self) -> bool:
        """파티에 멤버가 있는지 확인"""
        return len(self.members) > 0
        
    def get_alive_members(self) -> List[Character]:
        """살아있는 파티 멤버들 반환"""
        return [member for member in self.members if member.is_alive]
    
    def has_alive_members(self) -> bool:
        """살아있는 파티 멤버가 있는지 확인"""
        return len(self.get_alive_members()) > 0
        
    def get_dead_members(self) -> List[Character]:
        """죽은 파티 멤버들 반환"""
        return [member for member in self.members if not member.is_alive]
        
    def is_party_defeated(self) -> bool:
        """파티가 전멸했는지 확인"""
        return len(self.get_alive_members()) == 0
    
    @property
    def average_level(self) -> float:
        """파티의 평균 레벨 반환"""
        alive_members = self.get_alive_members()
        if not alive_members:
            return 1.0  # 기본값
        
        total_level = sum(getattr(member, 'level', 1) for member in alive_members)
        return total_level / len(alive_members)
        
    @property
    def party_members(self) -> List[Character]:
        """파티 멤버 목록 반환 (호환성을 위한 별칭)"""
        return self.members
    
    @property
    def party(self) -> List[Character]:
        """파티 멤버 목록 반환 (호환성을 위한 별칭)"""
        return self.members
    
    def get_all_members(self) -> List[Character]:
        """모든 파티 멤버 반환 (호환성을 위한 메서드)"""
        return self.members
    
    def get_active_party(self) -> List[Character]:
        """활성 파티 멤버 반환 (살아있는 멤버들)"""
        return self.get_alive_members()
    
    def update_atb_all(self):
        """모든 파티 멤버의 ATB 게이지 업데이트"""
        for member in self.members:
            member.update_atb()
            
    def process_all_status_effects(self) -> List[str]:
        """모든 멤버의 상태이상 처리"""
        all_messages = []
        for member in self.members:
            if member.is_alive:
                messages = member.process_status_effects()
                all_messages.extend(messages)
        return all_messages
    
    def add_gold(self, amount: int):
        """파티 골드 추가"""
        self.party_gold += amount
        
    def spend_gold(self, amount: int) -> bool:
        """파티 골드 소비"""
        if self.party_gold >= amount:
            self.party_gold -= amount
            return True
        return False
        
    def get_total_gold(self) -> int:
        """파티 총 골드 반환"""
        return self.party_gold
        
    def add_item_to_party_inventory(self, item: Dict, quantity: int = 1) -> bool:
        """파티 공용 인벤토리에 아이템 추가"""
        item_weight = item.get('weight', 1.0) * quantity
        
        if not self.can_add_item_weight(item_weight):
            print(f"하중 초과로 {item['name']}을(를) 추가할 수 없습니다.")
            return False
            
        return self.shared_inventory.add_item(item, quantity)
        
    def remove_item_from_party_inventory(self, item_name: str, quantity: int = 1) -> bool:
        """파티 공용 인벤토리에서 아이템 제거"""
        return self.shared_inventory.remove_item(item_name, quantity)
    
    def discard_party_item(self, item_name: str, quantity: int = 1) -> bool:
        """파티 아이템 버리기"""
        if self.shared_inventory.has_item(item_name):
            success = self.shared_inventory.remove_item(item_name, quantity)
            if success:
                print(f"{item_name} {quantity}개를 버렸습니다.")
                return True
            else:
                print(f"{item_name}을(를) 버리지 못했습니다.")
                return False
        else:
            print(f"파티 인벤토리에 {item_name}이(가) 없습니다.")
            return False
        
    def get_party_inventory_summary(self) -> str:
        """파티 인벤토리 요약"""
        current_weight = self.get_current_carry_weight()
        max_weight = self.get_total_carry_capacity()
        weight_percentage = (current_weight / max_weight) * 100 if max_weight > 0 else 0
        
        summary = f"파티 인벤토리:\n"
        summary += f"하중: {current_weight:.1f}/{max_weight:.1f}kg ({weight_percentage:.1f}%)\n"
        summary += f"골드: {self.party_gold}G\n"
        summary += f"아이템 수: {len(self.shared_inventory.items)}\n"
        
        return summary
        
    def spend_gold(self, amount: int) -> bool:
        """파티 골드 사용"""
        if self.party_gold >= amount:
            self.party_gold -= amount
            return True
        return False
        
    def get_total_gold(self) -> int:
        """총 파티 골드 반환"""
        return self.party_gold
        
    def has_enough_gold(self, amount: int) -> bool:
        """충분한 골드가 있는지 확인"""
        return self.party_gold >= amount
            
    def get_ready_members(self) -> List[Character]:
        """행동 준비된 파티 멤버들 반환"""
        return [member for member in self.members if member.can_act()]
        
    def heal_all(self, heal_amount: int):
        """모든 파티 멤버 회복"""
        for member in self.get_alive_members():
            healed = member.heal(heal_amount)
            if healed > 0:
                print(f"{member.name}이(가) {healed} HP 회복했습니다.")
                
    def rest(self):
        """휴식 (모든 멤버 회복)"""
        print("파티가 휴식을 취합니다...")
        for member in self.members:
            if member.is_alive:
                # 최대 HP의 50% 회복
                heal_amount = int(member.max_hp * 0.5)
                healed = member.heal(heal_amount)
                print(f"{member.name}: {healed} HP 회복")
    
    # === 플레이어 스킬 시스템 통합 ===
    
    def set_player_skill_system(self, skill_system):
        """플레이어 스킬 시스템 설정"""
        self._player_skill_system = skill_system
    
    def get_available_skills(self) -> List[Dict[str, Any]]:
        """사용 가능한 스킬 목록 반환"""
        if self._player_skill_system is None:
            return []
        return self._player_skill_system.get_available_skills(self)
    
    def can_use_skill(self, skill: Dict[str, Any]) -> bool:
        """스킬 사용 가능 여부 확인"""
        if self._player_skill_system is None:
            return False
        return self._player_skill_system.can_use_skill(self, skill)
    
    def use_skill(self, skill: Dict[str, Any], targets: List['Character'], allies: List['Character'] = None) -> List[str]:
        """스킬 사용"""
        if self._player_skill_system is None:
            return ["스킬 시스템이 없습니다."]
        
        if not self.can_use_skill(skill):
            return [f"{skill['name']} 사용 불가 (MP 부족 또는 기타 조건 미충족)"]
        
        return self._player_skill_system.execute_skill(self, skill, targets, allies)
    
    def get_skill_info(self, skill: Dict[str, Any]) -> str:
        """스킬 정보 텍스트 반환"""
        if self._player_skill_system is None:
            return "스킬 정보 없음"
        return self._player_skill_system.get_skill_description(skill)
    
    # === 특성 시스템 메서드 ===
    
    def apply_trait_effects(self):
        """모든 활성 특성의 패시브 효과 적용"""
        # 임시 효과 초기화
        for trait in self.active_traits:
            trait.reset_temp_effects(self)
        
        # 패시브 효과 적용
        for trait in self.active_traits:
            trait.apply_passive_effect(self)
    
    def trigger_trait_effects(self, trigger_type: str, **kwargs) -> List[str]:
        """특성 트리거 효과 발동"""
        results = []
        
        for trait in self.active_traits:
            if trait.trigger_effect(self, trigger_type, **kwargs):
                results.append(f"{trait.name} 효과 발동!")
        
        return results
    
    def get_effective_stats(self) -> Dict[str, int]:
        """임시 효과가 적용된 실제 스탯 반환"""
        return {
            "attack": self.physical_attack + self.temp_attack_bonus,
            "magic_attack": self.magic_attack + self.temp_magic_bonus,
            "defense": self.physical_defense + self.temp_defense_bonus,
            "speed": self.speed + self.temp_speed_bonus,
            "critical_rate": self.critical_rate + self.temp_crit_bonus,
            "evasion": self.evasion + self.temp_dodge_bonus
        }
    
    # 중복된 equip_item 메서드 제거 - 인벤토리 연동 버전만 사용
    
    def unequip_item(self, slot: str) -> bool:
        """아이템 해제"""
        if slot == "weapon" and self.equipped_weapon:
            item = self.equipped_weapon
            self.equipped_weapon = None
            print(f"{self.name}이(가) {item.name}을(를) 해제했습니다.")
        elif slot == "armor" and self.equipped_armor:
            item = self.equipped_armor
            self.equipped_armor = None
            print(f"{self.name}이(가) {item.name}을(를) 해제했습니다.")
        elif slot == "accessory" and self.equipped_accessory:
            item = self.equipped_accessory
            self.equipped_accessory = None
            print(f"{self.name}이(가) {item.name}을(를) 해제했습니다.")
        else:
            return False
        
        # 장비 효과 재계산
        self._apply_equipment_effects()
        return True
    
    def _apply_equipment_effects(self):
        """착용 중인 장비의 효과 적용"""
        # 장비 보너스 초기화
        self.equipment_attack_bonus = 0
        self.equipment_defense_bonus = 0
        self.equipment_magic_bonus = 0
        self.equipment_magic_defense_bonus = 0  # 마법방어 보너스 추가
        self.equipment_speed_bonus = 0
        self.equipment_hp_bonus = 0
        self.equipment_mp_bonus = 0
        
        # 착용 중인 장비들의 효과 적용
        equipped_items = [item for item in [self.equipped_weapon, self.equipped_armor, self.equipped_accessory] if item]
        
        for item in equipped_items:
            if hasattr(item, 'stats'):
                stats = item.stats
                self.equipment_attack_bonus += stats.get('physical_attack', 0)
                self.equipment_defense_bonus += stats.get('physical_defense', 0)
                self.equipment_magic_bonus += stats.get('magic_attack', 0)
                self.equipment_magic_defense_bonus += stats.get('magic_defense', 0)  # 마법방어 적용
                self.equipment_speed_bonus += stats.get('speed', 0)
                self.equipment_hp_bonus += stats.get('max_hp', 0)
                self.equipment_mp_bonus += stats.get('max_mp', 0)
        
        # ATB 속도도 장비 보너스 반영
        self.atb_speed = self.get_total_speed()
    
    def get_total_attack(self) -> int:
        """장비 보너스가 포함된 총 공격력"""
        base_attack = self.physical_attack + self.temp_attack_bonus
        equipment_bonus = getattr(self, 'equipment_attack_bonus', 0)
        return base_attack + equipment_bonus
    
    def get_total_defense(self) -> int:
        """장비 보너스가 포함된 총 방어력"""
        base_defense = self.physical_defense + self.temp_defense_bonus
        equipment_bonus = getattr(self, 'equipment_defense_bonus', 0)
        return base_defense + equipment_bonus
    
    def get_total_magic_attack(self) -> int:
        """장비 보너스가 포함된 총 마법 공격력"""
        base_magic = self.magic_attack + self.temp_magic_bonus
        equipment_bonus = getattr(self, 'equipment_magic_bonus', 0)
        return base_magic + equipment_bonus
    
    def get_total_max_hp(self) -> int:
        """장비 보너스가 포함된 총 최대 HP"""
        base_hp = self.max_hp
        equipment_bonus = getattr(self, 'equipment_hp_bonus', 0)
        return base_hp + equipment_bonus
    
    def get_total_max_mp(self) -> int:
        """장비 보너스가 포함된 총 최대 MP"""
        base_mp = self.max_mp
        equipment_bonus = getattr(self, 'equipment_mp_bonus', 0)
        return base_mp + equipment_bonus
    
    def start_casting(self, skill, targets, current_time, duration):
        """캐스팅 시작"""
        self.casting_skill = skill
        self.casting_targets = targets
        self.casting_start_time = current_time
        self.casting_duration = duration
        self.casting_start_atb = self.atb_gauge  # 캐스팅 시작 ATB 기록
        self.is_casting = True
        print(f"🔮 {self.name}이(가) {skill.get('name', '스킬')} 캐스팅을 시작합니다! [{duration}% 소요]")
    
    def update_casting(self, current_time):
        """캐스팅 진행 상황 업데이트"""
        if not self.is_casting or not self.casting_start_time:
            return False
        
        elapsed_time = current_time - self.casting_start_time
        if elapsed_time >= self.casting_duration:
            return True  # 캐스팅 완료
        return False
    
    def is_casting_ready_atb(self):
        """ATB 기반 캐스팅 완료 체크"""
        if not self.is_casting:
            return False
        
        # 캐스팅 시작 ATB와 필요한 ATB 증가량 확인
        if hasattr(self, 'casting_start_atb') and hasattr(self, 'casting_duration'):
            if self.casting_duration <= 0:
                return True  # 즉시 완료
            
            # casting_duration만큼의 ATB가 증가했는지 확인
            atb_progress = self.atb_gauge - self.casting_start_atb
            return atb_progress >= self.casting_duration
        
        # 폴백: ATB 게이지가 1000에 도달하면 캐스팅 완료
        return self.atb_gauge >= 1000
    
    def get_casting_progress(self):
        """캐스팅 진행률 반환 (0.0 ~ 1.0)"""
        if not self.is_casting:
            return 0.0
        
        # 시간 기반 진행률 (더 확실한 방법)
        if hasattr(self, 'casting_start_time') and hasattr(self, 'casting_duration') and self.casting_start_time:
            import time
            elapsed_time = time.time() - self.casting_start_time
            
            # casting_duration을 초 단위로 변환
            # 일반적으로 캐스팅 시간은 1-5초 정도가 적당
            if self.casting_duration > 100:  # ATB 단위인 경우 (100 이상)
                duration_seconds = self.casting_duration / 500.0  # ATB를 초로 변환 (더 빠르게)
            elif self.casting_duration > 10:  # 중간 값
                duration_seconds = self.casting_duration / 100.0
            else:  # 이미 초 단위인 경우
                duration_seconds = max(1.0, self.casting_duration)  # 최소 1초
            
            if duration_seconds <= 0:
                return 1.0
                
            progress = elapsed_time / duration_seconds
            return min(1.0, max(0.0, progress))
        
        # ATB 기반 진행률 (폴백)
        if hasattr(self, 'casting_start_atb') and hasattr(self, 'casting_duration'):
            if self.casting_duration <= 0:
                return 1.0  # 즉시 완료
            
            atb_progress = (self.atb_gauge - self.casting_start_atb)
            progress_ratio = atb_progress / self.casting_duration
            return min(1.0, max(0.0, progress_ratio))
        
        return 0.0
    
    def complete_casting(self):
        """캐스팅 완료"""
        skill = self.casting_skill
        targets = self.casting_targets
        
        # 캐스팅 상태 초기화
        self.casting_skill = None
        self.casting_targets = None
        self.casting_start_time = None
        self.casting_duration = None
        self.casting_start_atb = 0  # 캐스팅 시작 ATB 초기화
        self.is_casting = False
        
        return skill, targets
    
    def cancel_casting(self):
        """캐스팅 취소"""
        if self.is_casting:
            print(f"❌ {self.name}의 캐스팅이 취소되었습니다!")
            self.casting_skill = None
            self.casting_targets = None
            self.casting_start_time = None
            self.casting_duration = None
            self.casting_start_atb = 0  # 캐스팅 시작 ATB 초기화
            self.is_casting = False
    
    def get_casting_progress(self, current_time):
        """캐스팅 진행률 반환 (0.0 ~ 1.0)"""
        if not self.is_casting or not self.casting_start_time:
            return 0.0
        
        elapsed_time = current_time - self.casting_start_time
        return min(elapsed_time / self.casting_duration, 1.0)
    
    def get_total_speed(self) -> int:
        """장비 보너스가 포함된 총 속도"""
        base_speed = self.speed + getattr(self, 'temp_speed_bonus', 0)
        equipment_bonus = getattr(self, 'equipment_speed_bonus', 0)
        return base_speed + equipment_bonus
    
    def get_total_attack(self) -> int:
        """장비 보너스가 포함된 총 공격력"""
        base_attack = self.physical_attack + getattr(self, 'temp_attack_bonus', 0)
        equipment_bonus = getattr(self, 'equipment_attack_bonus', 0)
        return base_attack + equipment_bonus
    
    def get_total_defense(self) -> int:
        """장비 보너스가 포함된 총 방어력"""
        base_defense = self.physical_defense + getattr(self, 'temp_defense_bonus', 0)
        equipment_bonus = getattr(self, 'equipment_defense_bonus', 0)
        return base_defense + equipment_bonus
    
    def get_total_magic_attack(self) -> int:
        """장비 보너스가 포함된 총 마법 공격력"""
        base_magic = self.magic_attack + getattr(self, 'temp_magic_bonus', 0)
        equipment_bonus = getattr(self, 'equipment_magic_bonus', 0)
        return base_magic + equipment_bonus
    
    def get_total_magic_defense(self) -> int:
        """장비 보너스가 포함된 총 마법 방어력"""
        base_magic_def = self.magic_defense + getattr(self, 'temp_magic_defense_bonus', 0)
        equipment_bonus = getattr(self, 'equipment_magic_defense_bonus', 0)
        return base_magic_def + equipment_bonus
    
    # ==================== 실제 효과 처리 메서드들 ====================
    
    def process_attack_effects(self, target, damage_dealt: int, is_crit: bool = False) -> List[str]:
        """공격 시 발동되는 모든 효과 처리"""
        messages = []
        
        # 1. 검투사 반격 확률 처리 (공격받을 때)
        if hasattr(target, 'temp_counter_chance') and target.temp_counter_chance > 0:
            import random
            if random.random() < (target.temp_counter_chance / 100):
                counter_damage = int(target.get_total_attack() * 0.8)
                self.current_hp = max(1, self.current_hp - counter_damage)
                messages.append(f"⚔️ {target.name}이(가) 반격하여 {self.name}에게 {counter_damage} 피해!")
        
        # 2. 기사 수호 보너스 처리 (파티원 보호)
        if hasattr(self, 'temp_guard_bonus') and self.temp_guard_bonus > 0:
            # 파티원이 있을 때 데미지 감소
            guard_reduction = int(damage_dealt * (self.temp_guard_bonus / 100))
            if guard_reduction > 0:
                messages.append(f"🛡️ {self.name}의 수호로 피해 {guard_reduction} 감소!")
                return messages, max(1, damage_dealt - guard_reduction)
        
        # 3. 생명력 흡수 효과
        if hasattr(self, 'temp_life_steal') and self.temp_life_steal > 0:
            heal_amount = int(damage_dealt * self.temp_life_steal)
            if heal_amount > 0:
                old_hp = self.current_hp
                self.current_hp = min(self.max_hp, self.current_hp + heal_amount)
                actual_heal = self.current_hp - old_hp
                if actual_heal > 0:
                    messages.append(f"🩸 {self.name}이(가) 생명력을 {actual_heal} 흡수!")
        
        # 4. 독 무기 효과 (도적/암살자)
        if hasattr(self, 'temp_poison_weapon') and self.temp_poison_weapon:
            if hasattr(target, 'status_manager') and target.status_manager:
                target.status_manager.add_status("독", 3, 1.0)
                messages.append(f"☠️ {target.name}이(가) 독에 중독되었습니다!")
        
        # 5. 화염 피해 효과 (용기사)
        if hasattr(self, 'temp_fire_damage') and self.temp_fire_damage:
            fire_damage = int(damage_dealt * 0.3)
            if hasattr(target, 'status_manager') and target.status_manager:
                target.status_manager.add_status("화상", 3, 1.0)
                messages.append(f"🔥 {target.name}이(가) 화상을 입었습니다!")
        
        # 6. 공포 오라 효과 (암흑기사)
        if hasattr(self, 'temp_fear_aura') and self.temp_fear_aura > 0:
            if hasattr(target, 'status_manager') and target.status_manager:
                import random
                if random.random() < (self.temp_fear_aura / 100):
                    target.status_manager.add_status("공포", 2, 1.0)
                    messages.append(f"😰 {target.name}이(가) 공포에 떨고 있습니다!")
        
        # 7. MP 회복 효과 (마검사)
        if hasattr(self, 'temp_attack_mp_gain') and self.temp_attack_mp_gain:
            mp_gain = min(5, self.max_mp - self.current_mp)
            if mp_gain > 0:
                self.current_mp += mp_gain
                messages.append(f"💙 {self.name}이(가) 공격으로 {mp_gain} MP 회복!")
        
        return messages
    
    def process_skill_effects(self, skill_name: str, targets: List, skill_data: dict) -> List[str]:
        """스킬 사용 시 발동되는 효과 처리"""
        messages = []
        
        # 1. 철학자 지혜 효과 - 스킬 비용 감소
        if hasattr(self, 'temp_skill_cost_reduction') and self.temp_skill_cost_reduction > 0:
            cost_reduction = int(skill_data.get('mp_cost', 0) * self.temp_skill_cost_reduction)
            if cost_reduction > 0:
                self.current_mp += cost_reduction  # MP 일부 반환
                messages.append(f"🧠 지혜로 인해 MP {cost_reduction} 절약!")
        
        # 2. 아크메이지 마나 효율 효과
        if hasattr(self, 'temp_mana_efficiency') and self.temp_mana_efficiency > 0:
            if skill_data.get('skill_type') == 'magic':
                import random
                if random.random() < self.temp_mana_efficiency:
                    # MP 소모 없이 시전
                    mp_cost = skill_data.get('mp_cost', 0)
                    self.current_mp += mp_cost
                    messages.append(f"✨ 마나 순환으로 MP 소모 없이 시전!")
        
        # 3. 바드 다중 주문 효과
        if hasattr(self, 'temp_multi_cast') and self.temp_multi_cast:
            # 추가 시전 기회 (이미 전투 시스템에서 처리됨)
            messages.append(f"🎵 다중 주문으로 추가 시전!")
        
        # 4. 네크로맨서 생명력/마나 동시 흡수
        if hasattr(self, 'temp_life_mana_drain') and self.temp_life_mana_drain:
            for target in targets:
                if hasattr(target, 'current_hp') and target.current_hp > 0:
                    drain_amount = min(10, target.current_hp - 1)
                    target.current_hp -= drain_amount
                    self.current_hp = min(self.max_hp, self.current_hp + drain_amount)
                    self.current_mp = min(self.max_mp, self.current_mp + drain_amount // 2)
                    messages.append(f"🧛 {target.name}으로부터 생명력과 마나를 흡수!")
        
        # 5. 연금술사 랜덤 속성 효과
        if hasattr(self, 'temp_random_element') and self.temp_random_element:
            import random
            elements = ["화염", "냉기", "번개", "독"]
            chosen_element = random.choice(elements)
            messages.append(f"⚗️ 랜덤 속성 발동: {chosen_element} 효과!")
            
            # 속성별 추가 효과
            for target in targets:
                if hasattr(target, 'status_manager') and target.status_manager:
                    if chosen_element == "화염":
                        target.status_manager.add_status("화상", 3, 1.0)
                    elif chosen_element == "냉기":
                        target.status_manager.add_status("냉기", 2, 1.0)
                    elif chosen_element == "번개":
                        target.status_manager.add_status("감전", 2, 1.0)
                    elif chosen_element == "독":
                        target.status_manager.add_status("독", 4, 1.0)
        
        return messages
    
    def process_defense_effects(self, attacker, incoming_damage: int) -> tuple[int, List[str]]:
        """방어/피격 시 발동되는 효과 처리"""
        messages = []
        final_damage = incoming_damage
        
        # 1. 철학자 패턴 분석 효과
        if hasattr(self, 'temp_pattern_analysis') and self.temp_pattern_analysis:
            # 동일한 공격자의 연속 공격 시 피해 감소
            if hasattr(self, 'last_attacker') and self.last_attacker == attacker.name:
                damage_reduction = int(final_damage * 0.2)  # 20% 감소
                final_damage -= damage_reduction
                messages.append(f"🧠 패턴 분석으로 피해 {damage_reduction} 감소!")
            self.last_attacker = attacker.name
        
        # 2. 시간술사 미래 시야 효과
        if hasattr(self, 'temp_future_sight') and self.temp_future_sight:
            import random
            if random.random() < 0.3:  # 30% 확률로 회피
                final_damage = 0
                messages.append(f"👁️ 미래 시야로 공격을 완전히 회피!")
        
        # 3. 무당 영적 보호 효과
        if hasattr(self, 'temp_spirit_protection') and self.temp_spirit_protection > 0:
            spirit_reduction = int(final_damage * (self.temp_spirit_protection / 100))
            final_damage = max(1, final_damage - spirit_reduction)
            messages.append(f"👻 영적 보호로 피해 {spirit_reduction} 감소!")
        
        # 4. 용기사 비늘 방어 효과
        if hasattr(self, 'temp_physical_resistance') and self.temp_physical_resistance > 0:
            resistance_reduction = int(final_damage * self.temp_physical_resistance)
            final_damage = max(1, final_damage - resistance_reduction)
            messages.append(f"🐉 비늘 방어로 피해 {resistance_reduction} 감소!")
        
        # 5. 차원술사 공간 왜곡 효과
        if hasattr(self, 'temp_enemy_accuracy_down') and self.temp_enemy_accuracy_down > 0:
            import random
            if random.random() < (self.temp_enemy_accuracy_down / 100):
                final_damage = 0
                messages.append(f"🌀 공간 왜곡으로 공격이 빗나갔습니다!")
        
        # 6. 차원술사 차원 회피 효과
        if hasattr(self, 'temp_dimension_dodge') and self.temp_dimension_dodge:
            final_damage = 0
            messages.append(f"🌌 차원 이동으로 모든 공격 회피!")
        
        # 7. 사무라이 생존 의지 효과
        if hasattr(self, 'temp_survival_bonus') and self.temp_survival_bonus > 0:
            if self.current_hp <= self.max_hp * 0.3:  # 저체력일 때
                survival_reduction = int(final_damage * (self.temp_survival_bonus / 100))
                final_damage = max(1, final_damage - survival_reduction)
                messages.append(f"⚔️ 생존 의지로 피해 {survival_reduction} 감소!")
        
        return final_damage, messages
    
    def process_turn_start_effects(self) -> List[str]:
        """턴 시작 시 발동되는 효과들"""
        messages = []
        
        # 1. 드루이드 자연의 축복 - 턴 시작 시 HP/MP 회복
        if hasattr(self, 'temp_nature_blessing') and self.temp_nature_blessing:
            hp_heal = int(self.max_hp * 0.05)
            mp_heal = int(self.max_mp * 0.05)
            
            old_hp = self.current_hp
            self.current_hp = min(self.max_hp, self.current_hp + hp_heal)
            actual_hp_heal = self.current_hp - old_hp
            
            old_mp = self.current_mp
            self.current_mp = min(self.max_mp, self.current_mp + mp_heal)
            actual_mp_heal = self.current_mp - old_mp
            
            if actual_hp_heal > 0 or actual_mp_heal > 0:
                messages.append(f"🌿 자연의 축복: HP +{actual_hp_heal}, MP +{actual_mp_heal}")
        
        # 2. 정령술사 자연과의 대화 - MP 회복
        if hasattr(self, 'temp_nature_communion') and self.temp_nature_communion:
            mp_gain = int(self.max_mp * 0.08)
            old_mp = self.current_mp
            self.current_mp = min(self.max_mp, self.current_mp + mp_gain)
            actual_mp_gain = self.current_mp - old_mp
            if actual_mp_gain > 0:
                messages.append(f"🧚 자연과의 대화로 MP {actual_mp_gain} 회복!")
        
        # 3. 사무라이 명상 효과 - MP 재생 증가
        if hasattr(self, 'temp_mp_regen_boost') and self.temp_mp_regen_boost > 0:
            meditation_mp = int(self.max_mp * (self.temp_mp_regen_boost / 100))
            old_mp = self.current_mp
            self.current_mp = min(self.max_mp, self.current_mp + meditation_mp)
            actual_mp = self.current_mp - old_mp
            if actual_mp > 0:
                messages.append(f"🧘 명상으로 MP {actual_mp} 추가 회복!")
        
        # 4. 몽크 참선의 깨달음 - 상태이상 저항
        if hasattr(self, 'temp_meditation_recovery') and self.temp_meditation_recovery:
            if hasattr(self, 'status_manager') and self.status_manager:
                removed_count = 0
                for status_type in ["독", "화상", "공포", "혼란"]:
                    if self.status_manager.remove_status(status_type):
                        removed_count += 1
                if removed_count > 0:
                    messages.append(f"🧘‍♂️ 참선으로 {removed_count}개 상태이상 치료!")
        
        # 5. 자동 포탑 공격 (기계공학자)
        if hasattr(self, 'temp_turret_damage') and self.temp_turret_damage > 0:
            messages.append(f"🔧 자동 포탑이 적에게 {self.temp_turret_damage} 피해!")
        
        # 6. 식물 조종 피해 (드루이드)
        if hasattr(self, 'temp_plant_control_damage') and self.temp_plant_control_damage > 0:
            messages.append(f"🌿 조종된 식물이 적에게 {self.temp_plant_control_damage} 피해!")
        
        return messages
    
    def process_kill_effects(self, killed_enemy) -> List[str]:
        """적 처치 시 발동되는 효과들"""
        messages = []
        
        # 1. 전사 피의 갈증 - 처치 시 다음 공격 강화
        if hasattr(self, 'temp_kill_bonus') and self.temp_kill_bonus > 0:
            self.temp_next_attack_bonus = getattr(self, 'temp_next_attack_bonus', 0) + self.temp_kill_bonus
            messages.append(f"⚔️ 피의 갈증 발동! 다음 공격 +{self.temp_kill_bonus}")
        
        # 2. 해적 바다의 분노 - 연속 처치 시 공격력 누적
        if hasattr(self, 'temp_sea_rage') and self.temp_sea_rage:
            kill_stack = getattr(self, 'kill_stack_count', 0) + 1
            self.kill_stack_count = kill_stack
            rage_bonus = kill_stack * 5  # 처치당 공격력 +5
            self.temp_attack_bonus = getattr(self, 'temp_attack_bonus', 0) + 5
            messages.append(f"🏴‍☠️ 바다의 분노 ({kill_stack}스택): 공격력 +{rage_bonus}")
        
        # 3. 네크로맨서 영혼 조작 - 처치 시 MP 회복
        if hasattr(self, 'temp_soul_harvest') and self.temp_soul_harvest:
            mp_gain = min(15, self.max_mp - self.current_mp)
            if mp_gain > 0:
                self.current_mp += mp_gain
                messages.append(f"💀 영혼을 수확하여 MP {mp_gain} 회복!")
        
        return messages
    
    def process_critical_hit_effects(self, target, damage: int) -> List[str]:
        """치명타 발동 시 효과들"""
        messages = []
        
        # 1. 도적 치명적 급소 - 크리티컬 시 출혈
        if hasattr(self, 'temp_crit_bleed') and self.temp_crit_bleed:
            if hasattr(target, 'status_manager') and target.status_manager:
                target.status_manager.add_status("출혈", 4, 1.5)
                messages.append(f"🩸 치명적 급소 적중! {target.name}이(가) 심한 출혈!")
        
        # 2. 아크메이지 마법 연쇄 - 마법 크리티컬 시 추가 피해
        if hasattr(self, 'temp_magic_chain') and self.temp_magic_chain:
            chain_damage = int(damage * 0.5)
            messages.append(f"⚡ 마법 연쇄 발동! 추가 피해 {chain_damage}!")
        
        return messages
    
    # ==================== 패시브 효과 실제 적용 ====================
    
    def apply_all_passive_effects(self):
        """모든 패시브 효과 적용 (턴 시작/전투 시작 시 호출)"""
        # 기존 임시 효과 초기화
        self.reset_temp_bonuses()
        
        # 활성화된 특성들의 패시브 효과 적용
        for trait in self.active_traits:
            trait.apply_passive_effect(self)
        
        # 장비 패시브 효과 적용
        if hasattr(self, 'equipped_weapon') and self.equipped_weapon:
            self.equipped_weapon.apply_equipment_effects(self, "passive")
        if hasattr(self, 'equipped_armor') and self.equipped_armor:
            self.equipped_armor.apply_equipment_effects(self, "passive")
        if hasattr(self, 'equipped_accessory') and self.equipped_accessory:
            self.equipped_accessory.apply_equipment_effects(self, "passive")
    
    def reset_temp_bonuses(self):
        """턴 시작 시 임시 보너스 초기화"""
        # 기본 임시 보너스들
        self.temp_attack_bonus = 0
        self.temp_defense_bonus = 0
        self.temp_magic_bonus = 0
        self.temp_speed_bonus = 0
        self.temp_crit_bonus = 0
        self.temp_dodge_bonus = 0
        self.temp_accuracy_bonus = 0
        
        # 저항 관련
        self.temp_magic_resistance = 0
        self.temp_physical_resistance = 0
        self.temp_status_resist = 0
        
        # 특수 효과들
        self.temp_life_steal = 0
        self.temp_penetration = 0
        self.temp_vision_bonus = 0
        
        # 상태 플래그들
        self.temp_poison_weapon = False
        self.temp_fire_damage = False
        self.temp_holy_damage = False
        self.temp_weapon_immunity = False
        self.temp_first_strike = False
        self.temp_ignore_resistance = False
        self.temp_random_element = False
    
    def calculate_final_stats(self) -> dict:
        """최종 스탯 계산 (모든 보너스 포함)"""
        final_stats = {
            'physical_attack': self.physical_attack + getattr(self, 'temp_attack_bonus', 0),
            'magic_attack': self.magic_attack + getattr(self, 'temp_magic_bonus', 0),
            'physical_defense': self.physical_defense + getattr(self, 'temp_defense_bonus', 0),
            'magic_defense': self.magic_defense + getattr(self, 'temp_magic_defense_bonus', 0),
            'speed': self.speed + getattr(self, 'temp_speed_bonus', 0),
            'crit_chance': getattr(self, 'base_crit_chance', 5) + getattr(self, 'temp_crit_bonus', 0),
            'dodge_chance': getattr(self, 'base_dodge_chance', 5) + getattr(self, 'temp_dodge_bonus', 0),
            'accuracy': getattr(self, 'base_accuracy', 85) + getattr(self, 'temp_accuracy_bonus', 0)
        }
        
        # 장비 보너스 추가
        final_stats['physical_attack'] += getattr(self, 'equipment_attack_bonus', 0)
        final_stats['magic_attack'] += getattr(self, 'equipment_magic_bonus', 0)
        final_stats['physical_defense'] += getattr(self, 'equipment_defense_bonus', 0)
        final_stats['magic_defense'] += getattr(self, 'equipment_magic_defense_bonus', 0)
        final_stats['speed'] += getattr(self, 'equipment_speed_bonus', 0)
        
        return final_stats
    
    def update_duration_effects(self) -> List[str]:
        """모든 지속시간 효과 업데이트"""
        messages = []
        
        # 버프 지속시간 관리
        duration_attributes = [
            ('temp_attack_duration', 'temp_attack_bonus', '공격력 버프'),
            ('temp_defense_duration', 'temp_defense_bonus', '방어력 버프'),
            ('temp_magic_duration', 'temp_magic_bonus', '마법력 버프'),
            ('temp_speed_duration', 'temp_speed_bonus', '속도 버프'),
            ('temp_weapon_blessing_duration', 'temp_crit_bonus', '무기 축복'),
            ('temp_armor_blessing_duration', 'temp_defense_bonus', '방어구 축복'),
            ('temp_immunity_duration', 'temp_status_immunity', '상태이상 면역'),
            ('temp_overflow_duration', 'temp_mana_overflow', '마나 오버플로우'),
            ('temp_exp_duration', 'temp_exp_multiplier', '경험치 부스트'),
            ('temp_gold_duration', 'temp_gold_multiplier', '골드 부스트'),
            ('temp_transform_duration', 'temp_transformation', '변신 효과')
        ]
        
        for duration_attr, effect_attr, effect_name in duration_attributes:
            if hasattr(self, duration_attr):
                duration = getattr(self, duration_attr)
                if duration > 0:
                    setattr(self, duration_attr, duration - 1)
                    if duration - 1 <= 0:
                        # 효과 종료
                        if hasattr(self, effect_attr):
                            setattr(self, effect_attr, False if isinstance(getattr(self, effect_attr), bool) else 0)
                        messages.append(f"⏰ {effect_name} 효과가 종료되었습니다!")
        
        # 특수 지속시간 효과들
        special_durations = [
            ('temp_treasure_vision_duration', 'temp_treasure_vision', '보물 탐지'),
            ('temp_teleport_duration', 'temp_dodge_bonus', '순간이동'),
            ('temp_ally_duration', 'temp_summoned_ally', '소환수'),
            ('stealth_turns', 'stealth_turns', '은신'),
            ('temp_enemy_accuracy_duration', 'temp_enemy_accuracy_down', '연막탄')
        ]
        
        for duration_attr, effect_attr, effect_name in special_durations:
            if hasattr(self, duration_attr):
                duration = getattr(self, duration_attr)
                if duration > 0:
                    setattr(self, duration_attr, duration - 1)
                    if duration - 1 <= 0:
                        if hasattr(self, effect_attr):
                            setattr(self, effect_attr, False if isinstance(getattr(self, effect_attr), bool) else 0)
                        messages.append(f"⏰ {effect_name} 효과가 종료되었습니다!")
        
        return messages
    
    def create_copy(self):
        """캐릭터의 완전한 복사본 생성 (트레이닝 룸용)"""
        import copy
        
        # 완전한 딥카피 생성
        copied_char = copy.deepcopy(self)
        
        # 객체 ID가 다른지 확인하기 위해 별도의 인스턴스로 처리
        copied_char.name = f"{self.name} (복사본)"
        
        return copied_char
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """딕셔너리에서 Character 객체 생성"""
        try:
            # 기본 정보 추출
            name = data.get('name', 'Unknown')
            character_class = data.get('character_class', '전사')
            max_hp = data.get('max_hp', 100)
            physical_attack = data.get('physical_attack', 10)
            magic_attack = data.get('magic_attack', 10)
            physical_defense = data.get('physical_defense', 10)
            magic_defense = data.get('magic_defense', 10)
            speed = data.get('speed', 10)
            
            # Character 인스턴스 생성 (클래스 수정자 스킵)
            character = cls(name, character_class, max_hp, 
                          physical_attack, magic_attack,
                          physical_defense, magic_defense, speed,
                          skip_class_modifiers=True)
            
            # 추가 속성들 복원
            character.current_hp = data.get('current_hp', character.max_hp)
            character.current_mp = data.get('current_mp', character.max_mp)
            character.level = data.get('level', 1)
            character.experience = data.get('experience', 0)
            character.experience_to_next = data.get('experience_to_next', 30)
            character.atb_gauge = data.get('atb_gauge', 0)
            character.brave_points = data.get('brave_points', 0)
            character.wounds = data.get('wounds', 0)
            
            # 인벤토리 복원
            if 'inventory' in data:
                from .items import Inventory
                if isinstance(data['inventory'], dict):
                    # 새로운 Inventory 인스턴스 생성 후 데이터 복원
                    character.inventory = Inventory()
                    character.inventory.items = data['inventory'].get('items', {})
                    character.inventory.money = data['inventory'].get('money', 0)
                elif hasattr(data['inventory'], 'items'):
                    character.inventory = data['inventory']
                else:
                    from .items import Inventory
                    character.inventory = Inventory()
            
            # 장비 복원
            if 'equipped_weapon' in data and data['equipped_weapon']:
                from .items import ItemDatabase
                item_db = ItemDatabase()
                weapon_data = data['equipped_weapon']
                if isinstance(weapon_data, dict):
                    weapon_name = weapon_data.get('name', '')
                    weapon_item = item_db.get_item(weapon_name)
                    if weapon_item:
                        character.equipped_weapon = weapon_item
                        
            if 'equipped_armor' in data and data['equipped_armor']:
                from .items import ItemDatabase
                item_db = ItemDatabase()
                armor_data = data['equipped_armor']
                if isinstance(armor_data, dict):
                    armor_name = armor_data.get('name', '')
                    armor_item = item_db.get_item(armor_name)
                    if armor_item:
                        character.equipped_armor = armor_item
            
            # 특성 복원
            if 'active_traits' in data:
                character.active_traits = data['active_traits']
            
            # 상태 효과 복원
            if 'status_manager' in data:
                character.status_manager = data['status_manager']
            
            # 기타 속성들
            character.is_alive = data.get('is_alive', True)
            
            return character
            
        except Exception as e:
            print(f"❌ Character.from_dict 오류: {e}")
            # 기본 캐릭터 반환
            return cls("Unknown", "전사", 100, 10, 10, 10, 10, 10)
    
    def start_turn(self):
        """턴 시작 시 특성 효과 적용"""
        if hasattr(self, 'apply_trait_effects'):
            trait_effects = self.apply_trait_effects("turn_start")
            
            # 불굴의 의지: 턴당 체력 회복
            turn_healing = trait_effects.get("turn_healing", 0)
            if turn_healing > 0:
                old_hp = self.current_hp
                self.current_hp = min(self.max_hp, self.current_hp + turn_healing)
                healed = self.current_hp - old_hp
                if healed > 0:
                    print(f"💚 {self.name}의 불굴의 의지로 {healed} HP 회복!")
    
    def end_turn(self):
        """턴 종료 시 특성 효과 적용"""
        if hasattr(self, 'apply_trait_effects'):
            trait_effects = self.apply_trait_effects("turn_end")
            
            # 기타 턴 종료 시 효과들을 여기에 추가 가능
    
    def _check_guardian_protection(self) -> bool:
        """수호자 보호 효과 확인 (파티원 중 수호자 자세 전사가 있는지)"""
        # 게임 인스턴스를 통해 파티원 확인
        if hasattr(self, 'game_instance') and self.game_instance:
            if hasattr(self.game_instance, 'party_manager') and self.game_instance.party_manager:
                party_members = self.game_instance.party_manager.get_all_members()
                for member in party_members:
                    if (member != self and member.is_alive and 
                        member.character_class == "전사" and
                        hasattr(member, 'current_stance') and
                        member.current_stance == "guardian"):
                        # 균형감각 특성도 확인
                        if hasattr(member, 'apply_trait_effects'):
                            trait_effects = member.apply_trait_effects("protecting")
    
    def _force_initialize_all_mechanics(self, character_class: str):
        """💨 모든 직업의 기믹을 강제로 초기화 - 확실한 기믹 표시를 위한 강력한 방법"""
        print(f"💨 [FORCE INIT] {self.name} ({character_class}) 모든 기믹 강제 초기화 시작...")
        
        # 기본 기믹들 (모든 직업 공통)
        if not hasattr(self, 'poison_stacks'):
            self.poison_stacks = 0
        if not hasattr(self, 'max_poison_stacks'):
            self.max_poison_stacks = max(10, int(self.physical_attack * 1.5))
        
        # 직업별 특화 기믹 강제 설정
        if character_class == "전사":
            if not hasattr(self, 'warrior_stance'):
                self.warrior_stance = 'balanced'
            if not hasattr(self, 'warrior_focus'):
                self.warrior_focus = 0
        elif character_class == "아크메이지":
            if not hasattr(self, 'fire_count'):
                self.fire_count = 0
            if not hasattr(self, 'ice_count'):
                self.ice_count = 0
            if not hasattr(self, 'lightning_count'):
                self.lightning_count = 0
        elif character_class == "궁수":
            if not hasattr(self, 'aim_points'):
                self.aim_points = 0
            if not hasattr(self, 'precision_points'):
                self.precision_points = 0
        elif character_class == "암살자":
            if not hasattr(self, 'shadow_count'):
                self.shadow_count = 0
            if not hasattr(self, 'shadows'):
                self.shadows = 0
        elif character_class == "검성":
            if not hasattr(self, 'sword_aura'):
                self.sword_aura = 0
            if not hasattr(self, 'sword_aura_stacks'):
                self.sword_aura_stacks = 0
        elif character_class == "바드":
            if not hasattr(self, 'melody_stacks'):
                self.melody_stacks = 0
            if not hasattr(self, 'song_power'):
                self.song_power = 0
        elif character_class == "광전사":
            if not hasattr(self, 'rage_stacks'):
                self.rage_stacks = 0
            if not hasattr(self, 'berserk_level'):
                self.berserk_level = 0
        elif character_class == "몽크":
            if not hasattr(self, 'chi_points'):
                self.chi_points = 0
            if not hasattr(self, 'ki_energy'):
                self.ki_energy = 0
            if not hasattr(self, 'strike_marks'):
                self.strike_marks = 0
    
    def change_warrior_stance(self, new_stance_id: int) -> bool:
        """전사 자세 변경 (6단계 완전체 시스템)"""
        if self.character_class != "전사":
            return False
        
        if not (0 <= new_stance_id <= 5):
            return False
        
        old_stance = getattr(self, 'current_stance', 2)
        self.current_stance = new_stance_id
        
        # 자세 변경 보너스 (적응형 무술 특성)
        trait_effects = self.apply_trait_effects("stance_change")
        if trait_effects.get("stance_change_boost"):
            # 다음 공격 위력 30% 증가 효과 적용
            self.temp_next_attack_bonus = trait_effects["stance_change_boost"]
            print(f"🥋 적응형 무술 발동! 다음 공격 위력 {(trait_effects['stance_change_boost']-1)*100:.0f}% 증가!")
        
        # 자세별 즉시 효과 적용
        self._apply_stance_effects(new_stance_id)
        
        old_name = self._get_stance_name(old_stance)
        new_name = self._get_stance_name(new_stance_id)
        print(f"⚔️ {self.name}이(가) {old_name}에서 {new_name}로 자세를 변경했습니다!")
        return True
    
    def _apply_stance_effects(self, stance_id: int):
        """6단계 자세별 효과 적용 (6단계 완전체 특성 + 전장의 지배자 누적 효과 반영)"""
        # 기존 자세 효과 초기화
        self.temp_attack_bonus = getattr(self, 'temp_attack_bonus', 0)
        self.temp_defense_bonus = getattr(self, 'temp_defense_bonus', 0)
        self.temp_speed_bonus = getattr(self, 'temp_speed_bonus', 0)
        self.temp_crit_bonus = getattr(self, 'temp_crit_bonus', 0)
        
        # 특성 효과 확인
        trait_effects = self.apply_trait_effects("stance_bonus")
        stance_amplify = trait_effects.get("stance_bonus_amplify", 1.0)  # 구 전장의 지배자
        mastery_bonus = trait_effects.get("stance_mastery", False)       # 6단계 완전체
        
        # 전장의 지배자 누적 효과 처리
        mastery_stack_config = trait_effects.get("stance_mastery_stack", None)
        mastery_stack_bonus = 1.0
        if mastery_stack_config:
            # 같은 자세 유지 턴 수 추가
            if not hasattr(self, 'stance_hold_turns'):
                self.stance_hold_turns = 0
            if not hasattr(self, 'previous_stance_id'):
                self.previous_stance_id = stance_id
            
            if self.previous_stance_id == stance_id:
                self.stance_hold_turns += 1
            else:
                self.stance_hold_turns = 1
                self.previous_stance_id = stance_id
            
            # 누적 보너스 계산 (턴당 3%, 최대 35%)
            growth_rate = mastery_stack_config.get("growth_per_turn", 0.03)
            max_bonus = mastery_stack_config.get("max_bonus", 0.35)
            accumulated_bonus = min(self.stance_hold_turns * growth_rate, max_bonus)
            mastery_stack_bonus = 1.0 + accumulated_bonus
        
        # 6가지 자세별 효과 (특성으로 증폭)
        if stance_id == 0:  # 공격 자세
            attack_boost = int(self.physical_attack * 0.25 * stance_amplify * mastery_stack_bonus)
            self.temp_attack_bonus += attack_boost
            if mastery_bonus:
                self.temp_attack_bonus += int(self.physical_attack * 0.20)  # 6단계 완전체: 공격력 +20%
                
        elif stance_id == 1:  # 방어 자세
            defense_boost = int(self.physical_defense * 0.3 * stance_amplify * mastery_stack_bonus)
            self.temp_defense_bonus += defense_boost
            # 마법 방어력도 +25% 추가
            magic_defense_boost = int(self.magic_defense * 0.25 * stance_amplify * mastery_stack_bonus)
            if hasattr(self, 'temp_magic_defense_bonus'):
                self.temp_magic_defense_bonus += magic_defense_boost
            else:
                self.temp_magic_defense_bonus = magic_defense_boost
            if mastery_bonus:
                self.temp_defense_bonus += int(self.physical_defense * 0.25)  # 6단계 완전체: 방어력 +25%
                # 마법 방어력도 추가 보너스
                if hasattr(self, 'temp_magic_defense_bonus'):
                    self.temp_magic_defense_bonus += int(self.magic_defense * 0.25)
                else:
                    self.temp_magic_defense_bonus = int(self.magic_defense * 0.25)
                
        elif stance_id == 2:  # 균형 자세
            balance_boost = int(min(self.physical_attack, self.physical_defense) * 0.15 * stance_amplify * mastery_stack_bonus)
            self.temp_attack_bonus += balance_boost
            self.temp_defense_bonus += balance_boost
            if mastery_bonus:
                # 6단계 완전체: 모든 능력치 12% 증가 (너프됨)
                self.temp_attack_bonus += int(self.physical_attack * 0.12)
                self.temp_defense_bonus += int(self.physical_defense * 0.12)
                self.temp_speed_bonus += int(self.speed * 0.12)
                
        elif stance_id == 3:  # 광전사 자세
            berserker_boost = int(self.physical_attack * 0.4 * stance_amplify * mastery_stack_bonus)
            self.temp_attack_bonus += berserker_boost
            self.temp_speed_bonus += int(self.speed * 0.25 * mastery_stack_bonus)
            if mastery_bonus:
                self.temp_crit_bonus += 0.15  # 6단계 완전체: 크리티컬 +15%
                
        elif stance_id == 4:  # 수호자 자세
            guardian_boost = int(self.physical_defense * 0.35 * stance_amplify * mastery_stack_bonus)
            self.temp_defense_bonus += guardian_boost
            if mastery_bonus:
                # 6단계 완전체: 회복량 +30%
                if hasattr(self, 'healing_multiplier'):
                    self.healing_multiplier *= 1.30
                else:
                    self.healing_multiplier = 1.30
                
        elif stance_id == 5:  # 속도 자세
            speed_boost = int(self.speed * 0.4 * stance_amplify * mastery_stack_bonus)
            self.temp_speed_bonus += speed_boost
            self.temp_attack_bonus += int(self.physical_attack * 0.15 * mastery_stack_bonus)
            if mastery_bonus:
                # 6단계 완전체: 행동 속도 35% 증가 (너프됨)
                if hasattr(self, 'atb_speed'):
                    self.atb_speed = int(self.atb_speed * 1.35)
                self.temp_speed_bonus += int(self.speed * 0.35)
    
    def _get_stance_name(self, stance_id: int) -> str:
        """자세 이름 반환 (6단계)"""
        stance_names = {
            0: '⚔️ 공격 자세',
            1: '🛡️ 방어 자세', 
            2: '⚖️ 균형 자세',
            3: '💀 광전사 자세',
            4: '🛠️ 수호자 자세',
            5: '⚡ 속도 자세'
        }
        return stance_names.get(stance_id, '❓ 알 수 없는 자세')
    
    def get_available_stances(self) -> list:
        """사용 가능한 자세 목록 반환 (6단계)"""
        if self.character_class != "전사":
            return []
        return [0, 1, 2, 3, 4, 5]  # 숫자 기반 인덱스
    
    def get_stance_description(self, stance_id: int) -> str:
        """자세 설명 반환 (6단계 완전체 포함)"""
        descriptions = {
            0: "공격력 25% 증가, 6단계 완전체: 공격력 추가 20% 증가",
            1: "방어력 30% 증가, 6단계 완전체: 방어력 추가 25% 증가", 
            2: "균형잡힌 능력치 향상, 6단계 완전체: 모든 스탯 12% 증가",
            3: "공격력 40% + 속도 25% 증가, 6단계 완전체: 크리티컬 15% 증가",
            4: "방어력 35% 증가 + 아군 보호, 6단계 완전체: 회복량 30% 증가",
            5: "속도 40% + 공격력 15% 증가, 6단계 완전체: 행동속도 35% 증가"
        }
        return descriptions.get(stance_id, "알 수 없는 자세")
    
    # === 바드 전용 멜로디 시스템 ===
    def _add_melody_note(self, note: int):
        """멜로디 노트 추가 (0=DO, 1=RE, 2=MI, 3=FA, 4=SO, 5=LA, 6=TI)"""
        if self.character_class != "바드":
            return False
        
        if 0 <= note <= 6 and len(self.melody_notes) < 7:
            self.melody_notes.append(note)
            self._update_melody_display()
            return True
        return False
    
    def _clear_melody(self):
        """멜로디 초기화"""
        if self.character_class != "바드":
            return
        self.melody_notes.clear()
        self.current_melody = ""
    
    def _update_melody_display(self):
        """멜로디 표시 업데이트"""
        if self.character_class != "바드":
            return
        
        note_names = ["DO", "RE", "MI", "FA", "SO", "LA", "TI"]
        if self.melody_notes:
            melody_str = "/".join([note_names[note] for note in self.melody_notes if 0 <= note < len(note_names)])
            self.current_melody = melody_str
        else:
            self.current_melody = ""
    
    def _get_current_melody_display(self) -> str:
        """현재 멜로디 표시 반환"""
        if self.character_class != "바드":
            return ""
        
        if self.melody_notes:
            note_names = ["DO", "RE", "MI", "FA", "SO", "LA", "TI"]
            return "/".join([note_names[note] for note in self.melody_notes if 0 <= note < len(note_names)])
        return "MELODY:0"
        
        print(f"💨 [FORCE INIT] {self.name} ({character_class}) 기믹 강제 초기화 완료!")