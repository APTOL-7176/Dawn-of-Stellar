"""
캐릭터 및 파티 관리 시스템 (Brave 시스템 포함)
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
import random
from .new_skill_system import StatusType, get_status_icon

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
        
    def add_status(self, status_effect: StatusEffect) -> bool:
        """상태이상 추가"""
        existing = self.get_status(status_effect.status_type)
        if existing:
            existing.duration = max(existing.duration, status_effect.duration)
            return False
        else:
            self.status_effects.append(status_effect)
            self.effects = self.status_effects  # 별칭 업데이트
            return True
    
    def get_status(self, status_type: StatusType):
        """특정 상태이상 반환"""
        for effect in self.status_effects:
            if effect.status_type == status_type:
                return effect
        return None
    
    def process_turn_effects(self) -> List[str]:
        """턴 처리 - 호환성 유지"""
        messages = []
        for effect in self.status_effects[:]:
            effect.duration -= 1
            if effect.duration <= 0:
                self.status_effects.remove(effect)
                messages.append(f"{effect.status_type.value} 효과가 해제되었습니다.")
        self.effects = self.status_effects  # 별칭 업데이트
        return messages
    
    def get_status_display(self) -> str:
        """상태이상 표시"""
        if not self.status_effects:
            return ""
        icons = [get_status_icon(effect.status_type) for effect in self.status_effects]
        return " ".join(icons)
    
    def can_act(self) -> bool:
        """행동 가능 여부"""
        blocking = [StatusType.STUN, StatusType.SLEEP, StatusType.FREEZE, StatusType.PETRIFY]
        return not any(effect.status_type in blocking for effect in self.status_effects)
    
    def get_stat_modifiers(self) -> dict:
        """스탯 수정치 반환 (곱셈용 배율)"""
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
            if effect.status_type == StatusType.BUFF_ATTACK:
                modifiers['physical_attack'] *= (1.0 + effect.value * 0.01)
                modifiers['magic_attack'] *= (1.0 + effect.value * 0.01)
            elif effect.status_type == StatusType.BUFF_DEFENSE:
                modifiers['physical_defense'] *= (1.0 + effect.value * 0.01)
                modifiers['magic_defense'] *= (1.0 + effect.value * 0.01)
            elif effect.status_type == StatusType.BUFF_SPEED:
                modifiers['speed'] *= (1.0 + effect.value * 0.01)
            elif effect.status_type == StatusType.DEBUFF_ATTACK:
                modifiers['physical_attack'] *= (1.0 - effect.value * 0.01)
                modifiers['magic_attack'] *= (1.0 - effect.value * 0.01)
            elif effect.status_type == StatusType.DEBUFF_DEFENSE:
                modifiers['physical_defense'] *= (1.0 - effect.value * 0.01)
                modifiers['magic_defense'] *= (1.0 - effect.value * 0.01)
            elif effect.status_type == StatusType.DEBUFF_SPEED:
                modifiers['speed'] *= (1.0 - effect.value * 0.01)
        
        return modifiers
    
    def add_effect(self, effect: StatusEffect):
        """상태이상 효과 추가 (호환성)"""
        self.add_status(effect)
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
        self.effect_value = effect_value
        self.is_active = True
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
        
        # 도적 특성
        if "item_no_turn" in effect:
            character.item_no_turn_cost = True
            
        if "treasure_sense" in effect:
            character.temp_treasure_bonus = effect["treasure_sense"]
            
        if "poison_chance" in effect:
            character.temp_poison_chance = effect["poison_chance"]
        
        # 성기사 특성
        if "holy_resistance" in effect:
            character.temp_undead_resistance = effect["holy_resistance"]
            
        if "holy_damage" in effect:
            character.temp_holy_damage = True
            
        if "protection_bonus" in effect:
            character.temp_protection_bonus = effect["protection_bonus"]
        
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
        
        # 암살자 특성
        if "shadow_step" in effect:
            character.temp_first_strike = True
            
        if "critical_expert" in effect:
            character.temp_crit_bonus += effect["critical_expert"]
            
        if "poison_weapon" in effect:
            character.temp_poison_weapon = True
        
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
        
        # 암흑기사 특성
        if trigger_type == "fatal_damage" and "undying_will" in effect:
            if self.stack_count < effect["undying_will"]:
                character.hp = character.max_hp
                character.mp = character.max_mp
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
        """액티브 효과 발동"""
        if not self.is_active or self.effect_type != "active" or self.cooldown > 0:
            return False
            
        effect = self.effect_value
        
        # 도적 특성
        if "stealth_duration" in effect:
            character.stealth_turns = effect["stealth_duration"]
            self.cooldown = 10  # 10턴 쿨다운
            return True
        
        return False
    
    def update_cooldown(self):
        """쿨다운 업데이트"""
        if self.cooldown > 0:
            self.cooldown -= 1
    
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
        """클래스별 고유 특성 반환 (5개씩, 2개 선택 가능)"""
        trait_sets = {
            "전사": [
                CharacterTrait("불굴의 의지", "HP가 25% 이하일 때 공격력 50% 증가", "passive", {"low_hp_damage_boost": 1.5}),
                CharacterTrait("전투 광기", "적을 처치할 때마다 다음 공격의 피해량 20% 증가", "trigger", {"kill_damage_stack": 0.2}),
                CharacterTrait("방어 숙련", "방어 시 받는 피해 30% 추가 감소", "passive", {"defense_bonus": 0.3}),
                CharacterTrait("위협적 존재", "전투 시작 시 적들의 공격력 10% 감소", "passive", {"enemy_attack_debuff": 0.1}),
                CharacterTrait("피의 갈증", "HP가 50% 이상일 때 공격속도 25% 증가", "passive", {"high_hp_speed_boost": 1.25})
            ],
            
            "아크메이지": [
                CharacterTrait("마나 순환", "스킬 사용 시 30% 확률로 MP 소모량 절반", "passive", {"mana_efficiency": 0.3}),
                CharacterTrait("원소 지배", "속성 마법 사용 시 해당 속성 저항 20% 증가", "passive", {"elemental_mastery": 0.2}),
                CharacterTrait("마법 연구자", "전투 후 획득 경험치 15% 증가", "passive", {"exp_bonus": 0.15}),
                CharacterTrait("마법 폭주", "크리티컬 마법 시 주변 적들에게 연쇄 피해", "trigger", {"magic_chain": True}),
                CharacterTrait("마력 집중", "MP가 75% 이상일 때 마법 피해 40% 증가", "passive", {"high_mp_magic_boost": 1.4})
            ],
            
            "궁수": [
                CharacterTrait("정밀 사격", "크리티컬 확률 25% 증가", "passive", {"crit_chance_bonus": 0.25}),
                CharacterTrait("원거리 숙련", "첫 공격 시 항상 크리티컬", "trigger", {"first_strike_crit": True}),
                CharacterTrait("민첩한 몸놀림", "회피 확률 20% 증가", "passive", {"dodge_bonus": 0.2}),
                CharacterTrait("사냥꾼의 직감", "적의 약점을 간파해 방어력 무시 확률 15%", "passive", {"weakness_detect": 0.15}),
                CharacterTrait("바람의 가호", "이동 시 다음 공격의 명중률과 피해량 15% 증가", "passive", {"movement_bonus": 1.15})
            ],
            
            "도적": [
                CharacterTrait("그림자 은신", "전투 시작 시 3턴간 은신 상태", "active", {"stealth_duration": 3}),
                CharacterTrait("치명적 급소", "크리티컬 시 추가 출혈 효과 부여", "trigger", {"crit_bleed": True}),
                CharacterTrait("빠른 손놀림", "아이템 사용 시 턴 소모하지 않음", "passive", {"item_no_turn": True}),
                CharacterTrait("도적의 직감", "함정과 보물 발견 확률 50% 증가", "passive", {"treasure_sense": 0.5}),
                CharacterTrait("독 숙련", "모든 공격에 10% 확률로 독 효과 추가", "passive", {"poison_chance": 0.1})
            ],
            
            "성기사": [
                CharacterTrait("신성한 가호", "언데드와 악마에게 받는 피해 50% 감소", "passive", {"holy_resistance": 0.5}),
                CharacterTrait("치유의 빛", "공격 시 30% 확률로 파티원 전체 소량 회복", "trigger", {"heal_on_attack": 0.3}),
                CharacterTrait("정의의 분노", "아군이 쓰러질 때 공격력과 마법력 30% 증가", "trigger", {"justice_rage": 0.3}),
                CharacterTrait("축복받은 무기", "모든 공격에 성속성 추가 피해", "passive", {"holy_damage": True}),
                CharacterTrait("수호의 맹세", "파티원 보호 시 받는 피해 50% 감소", "passive", {"protection_bonus": 0.5})
            ],
            
            "암흑기사": [
                CharacterTrait("생명 흡수", "가한 피해의 15%만큼 HP 회복", "passive", {"life_steal": 0.15}),
                CharacterTrait("어둠의 계약", "HP가 낮을수록 공격력 증가 (최대 100%)", "passive", {"dark_pact": True}),
                CharacterTrait("공포 오라", "적들이 간헐적으로 행동 불가", "passive", {"fear_aura": 0.2}),
                CharacterTrait("불사의 의지", "치명상 시 1회 한정 완전 회복", "trigger", {"undying_will": 1}),
                CharacterTrait("어둠 조작", "턴 종료 시 20% 확률로 적에게 암속성 피해", "passive", {"dark_pulse": 0.2})
            ],
            
            "몽크": [
                CharacterTrait("내공 순환", "MP가 가득 찰 때마다 모든 능력치 일시 증가", "trigger", {"chi_burst": True}),
                CharacterTrait("연타 숙련", "연속 공격 시마다 피해량 누적 증가", "passive", {"combo_multiplier": 0.1}),
                CharacterTrait("정신 수양", "상태이상 저항 50% 증가", "passive", {"status_resist": 0.5}),
                CharacterTrait("기절 공격", "일정 확률로 적을 기절시켜 1턴 행동 불가", "trigger", {"stun_chance": 0.2}),
                CharacterTrait("참선의 깨달음", "전투 중 매 5턴마다 MP 완전 회복", "passive", {"meditation_recovery": 5})
            ],
            
            # 새로운 직업들 추가 (21개 더 필요)
            "바드": [
                CharacterTrait("전투 노래", "파티원들의 공격력 15% 증가", "passive", {"party_damage_boost": 0.15}),
                CharacterTrait("치유의 선율", "턴 종료 시 파티 전체 소량 회복", "passive", {"turn_heal": True}),
                CharacterTrait("용기의 찬송", "파티원들의 크리티컬 확률 10% 증가", "passive", {"party_crit_boost": 0.1}),
                CharacterTrait("마법 해제", "적의 버프를 무효화하는 확률 25%", "trigger", {"dispel_chance": 0.25}),
                CharacterTrait("영감의 리듬", "스킬 사용 시 아군의 MP 회복", "trigger", {"inspire_mp": True})
            ],
            
            "네크로맨서": [
                CharacterTrait("어둠의 계약", "적 처치 시 MP 회복량 2배", "trigger", {"dark_pact_mp": 2.0}),
                CharacterTrait("생명력 흡수", "적에게 피해를 줄 때 HP와 MP 동시 회복", "passive", {"life_mana_drain": True}),
                CharacterTrait("저주술", "공격 시 25% 확률로 적에게 저주 부여", "trigger", {"curse_chance": 0.25}),
                CharacterTrait("죽음의 오라", "주변 적들의 회복 효과 50% 감소", "passive", {"anti_heal_aura": 0.5}),
                CharacterTrait("영혼 흡수", "적 처치 시 최대 MP 일시 증가", "trigger", {"soul_harvest": True})
            ],
            
            "용기사": [
                CharacterTrait("용의 숨결", "모든 공격에 화염 속성 추가", "passive", {"dragon_breath": True}),
                CharacterTrait("비늘 방어", "받는 물리 피해 15% 감소", "passive", {"scale_armor": 0.15}),
                CharacterTrait("용의 분노", "HP가 낮을수록 공격속도 증가", "passive", {"dragon_rage": True}),
                CharacterTrait("날개 돌격", "크리티컬 시 추가 행동 기회", "trigger", {"wing_strike": True}),
                CharacterTrait("용족의 긍지", "디버프 저항 40% 증가", "passive", {"debuff_resist": 0.4})
            ],
            
            "검성": [
                CharacterTrait("검술 달인", "무기 공격력 30% 증가", "passive", {"sword_mastery": 0.3}),
                CharacterTrait("연속 베기", "공격 성공 시 30% 확률로 즉시 재공격", "trigger", {"combo_strike": 0.3}),
                CharacterTrait("검기 충격", "공격 시 25% 확률로 2배 피해", "trigger", {"sword_impact": 2.0}),
                CharacterTrait("완벽한 방어", "방어 시 100% 피해 무효화", "trigger", {"perfect_guard": True}),
                CharacterTrait("검의 의지", "무기 파괴 무효", "passive", {"weapon_protection": True})
            ],
            
            "정령술사": [
                CharacterTrait("정령 친화", "모든 속성 마법 위력 25% 증가", "passive", {"elemental_affinity": 0.25}),
                CharacterTrait("자연의 축복", "턴 시작 시 MP 자동 회복", "passive", {"nature_blessing": True}),
                CharacterTrait("원소 조화", "서로 다른 속성 연계 시 추가 피해", "trigger", {"element_combo": True}),
                CharacterTrait("마나 순환", "마법 사용 시 50% 확률로 MP 소모량 절반", "passive", {"mana_cycle": 0.5}),
                CharacterTrait("원소 폭발", "마법 크리티컬 시 광역 피해", "trigger", {"elemental_blast": True})
            ],
            
            "암살자": [
                CharacterTrait("그림자 이동", "첫 턴에 반드시 선공", "passive", {"shadow_step": True}),
                CharacterTrait("치명타 특화", "크리티컬 확률 40% 증가", "passive", {"critical_expert": 0.4}),
                CharacterTrait("독날 무기", "모든 공격에 독 효과", "passive", {"poison_weapon": True}),
                CharacterTrait("은신 공격", "은신 상태에서 공격 시 피해 200% 증가", "trigger", {"stealth_attack": 2.0}),
                CharacterTrait("연막탄", "전투 도중 은신 상태 진입 가능", "active", {"smoke_bomb": True})
            ],
            
            "기계공학자": [
                CharacterTrait("자동 포탑", "전투 시작 시 포탑 설치", "active", {"auto_turret": True}),
                CharacterTrait("기계 정비", "전투 후 5턴간 장비 효과 10% 증가 (중첩 가능)", "trigger", {"machine_maintenance": {"bonus": 0.1, "duration": 5}}),
                CharacterTrait("폭탄 제작", "소모품 폭탄 무한 사용", "passive", {"bomb_craft": True}),
                CharacterTrait("강화 장비", "모든 장비 효과 20% 증가", "passive", {"gear_enhance": 0.2}),
                CharacterTrait("오버클럭", "일시적으로 모든 능력치 50% 증가", "active", {"overclock": 0.5})
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
                CharacterTrait("식물 조종", "적의 이동 제한 스킬", "active", {"plant_control": True}),
                CharacterTrait("동물 변신", "전투 중 능력치 배분 변경 가능", "active", {"shape_shift": True}),
                CharacterTrait("계절의 힘", "전투마다 랜덤 속성 강화", "passive", {"seasonal_power": True})
            ],
            
            "철학자": [
                CharacterTrait("현자의 지혜", "모든 스킬 MP 소모량 20% 감소", "passive", {"wisdom": 0.2}),
                CharacterTrait("논리적 사고", "적의 패턴 분석으로 회피율 증가", "passive", {"logic": True}),
                CharacterTrait("깨달음", "경험치 획득량 25% 증가", "passive", {"enlightenment": 0.25}),
                CharacterTrait("사색의 힘", "MP가 가득 찰 때마다 지혜 스택 증가", "trigger", {"contemplation": True}),
                CharacterTrait("철학적 논증", "적을 혼란에 빠뜨리는 스킬", "active", {"confusion": True})
            ],
            
            "시간술사": [
                CharacterTrait("시간 정지", "적의 행동을 1턴 지연", "active", {"time_stop": True}),
                CharacterTrait("과거 회귀", "한 번 받은 피해 되돌리기", "trigger", {"time_rewind": True}),
                CharacterTrait("시간 인식", "적의 다음 행동 타입 미리 파악", "passive", {"time_sense": True}),
                CharacterTrait("순간 가속", "크리티컬 시 20% 확률로 즉시 재행동", "trigger", {"instant_accel": 0.2}),
                CharacterTrait("인과 조작", "공격 실패 시 재계산 가능", "trigger", {"causality_fix": True})
            ],
            
            "연금술사": [
                CharacterTrait("포션 제조", "회복 아이템 효과 2배", "passive", {"potion_craft": 2.0}),
                CharacterTrait("원소 변환", "적의 속성 저항 무시", "passive", {"transmute": True}),
                CharacterTrait("폭발물 전문", "폭발 계열 스킬 위력 50% 증가", "passive", {"explosion": 0.5}),
                CharacterTrait("실험 정신", "디버프 지속시간 25% 증가", "passive", {"experiment": 0.25}),
                CharacterTrait("마법 물질", "모든 공격에 랜덤 속성 추가", "passive", {"magic_substance": True})
            ],
            
            "검투사": [
                CharacterTrait("관중의 환호", "적을 많이 처치할수록 능력치 증가", "trigger", {"crowd_cheer": True}),
                CharacterTrait("검투 기술", "반격 확률 30% 증가", "passive", {"gladiator_skill": 0.3}),
                CharacterTrait("투기장 경험", "1대1 전투 시 모든 능력치 25% 증가", "trigger", {"arena_exp": 0.25}),
                CharacterTrait("생존 본능", "HP 30% 이하에서 회피율 50% 증가", "passive", {"survival": 0.5}),
                CharacterTrait("전사의 혼", "파티원이 전멸해도 5턴간 홀로 전투 지속", "trigger", {"warrior_soul": 5})
            ],
            
            "기사": [
                CharacterTrait("명예의 수호", "아군 보호 시 받는 피해 30% 감소", "passive", {"honor_guard": 0.3}),
                CharacterTrait("창술 숙련", "창류 무기 공격력 35% 증가", "passive", {"lance_master": 0.35}),
                CharacterTrait("기사도 정신", "디버프 지속시간 50% 감소", "passive", {"chivalry": 0.5}),
                CharacterTrait("용맹한 돌격", "첫 공격이 크리티컬일 시 추가 피해", "trigger", {"brave_charge": True}),
                CharacterTrait("영광의 맹세", "파티원 수만큼 능력치 증가", "passive", {"glory_oath": True})
            ],
            
            "신관": [
                CharacterTrait("신의 가호", "치명타 무효화 확률 20%", "passive", {"divine_grace": 0.2}),
                CharacterTrait("성스러운 빛", "언데드에게 2배 피해", "passive", {"holy_light": 2.0}),
                CharacterTrait("치유 특화", "모든 회복 효과 50% 증가", "passive", {"heal_mastery": 0.5}),
                CharacterTrait("축복의 기도", "파티 전체 버프 효과", "active", {"blessing": True}),
                CharacterTrait("신탁", "랜덤하게 강력한 기적 발생", "trigger", {"oracle": True})
            ],
            
            "마검사": [
                CharacterTrait("마검 일체", "물리와 마법 공격력 동시 적용", "passive", {"magic_sword": True}),
                CharacterTrait("마력 충전", "공격할 때마다 MP 회복", "passive", {"mana_charge": True}),
                CharacterTrait("검기 폭발", "검 공격에 마법 피해 추가", "passive", {"sword_blast": True}),
                CharacterTrait("이중 속성", "두 가지 속성 동시 공격", "passive", {"dual_element": True}),
                CharacterTrait("마검 오의", "궁극기 사용 시 모든 적에게 피해", "trigger", {"mystic_art": True})
            ],
            
            "차원술사": [
                CharacterTrait("차원 보관", "무제한 아이템 보관", "passive", {"dimension_storage": True}),
                CharacterTrait("공간 이동", "위치 변경으로 공격 회피", "trigger", {"teleport": True}),
                CharacterTrait("차원 균열", "적에게 고정 피해 (보스 50% 감소)", "active", {"dimension_rift": True}),
                CharacterTrait("평행우주", "공격 실패 시 재시도 가능", "trigger", {"parallel_world": True}),
                CharacterTrait("공간 왜곡", "적의 정확도 30% 감소", "passive", {"space_distortion": 0.3})
            ],
            
            "광전사": [
                CharacterTrait("광기 상태", "HP가 낮을수록 공격력과 속도 증가", "passive", {"berserker_rage": True}),
                CharacterTrait("무모한 돌진", "방어 무시하고 최대 피해 공격", "active", {"reckless_charge": True}),
                CharacterTrait("고통 무시", "상태이상 무효", "passive", {"pain_ignore": True}),
                CharacterTrait("전투 광증", "적 처치 시 즉시 재행동", "trigger", {"battle_frenzy": True}),
                CharacterTrait("불사의 의지", "치명상 시 3턴간 불사 상태", "trigger", {"undying_will": 3})
            ]
        }
        
        return trait_sets.get(character_class, [])
    
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
    """게임 캐릭터 클래스 (Brave 시스템 포함)"""
    
    def __init__(self, name: str, character_class: str, max_hp: int, 
                 physical_attack: int, magic_attack: int, 
                 physical_defense: int, magic_defense: int, speed: int):
        # Brave 시스템 초기화
        super().__init__()
        
        self.name = name
        self.character_class = character_class
        
        # 클래스 특화 적용
        specialization = CharacterClassManager.get_class_specialization(character_class)
        hp_modifier = specialization.get("hp_bonus", 1.0)
        mp_modifier = specialization.get("mp_efficiency", 1.0)
        
        self.max_hp = int(max_hp * hp_modifier)
        self.current_hp = self.max_hp
        self.wounds = 0  # 상처 누적량
        self.max_mp = self._get_class_base_mp(character_class)  # 클래스별 고정 MP
        self.current_mp = self.max_mp  # 현재 MP
        self.steps_taken = 0  # 걸음 수 (상처 회복용)
        self.physical_attack = physical_attack
        self.magic_attack = magic_attack
        self.physical_defense = physical_defense
        self.magic_defense = magic_defense
        self.speed = speed
        self.level = 1
        self.experience = 0
        self.experience_to_next = 30  # 다음 레벨까지 필요한 경험치
        self.atb_gauge = 0  # ATB 게이지 (0-100)
        self.atb_speed = speed  # ATB 충전 속도는 스피드 수치 기반
        self.is_alive = True
        
        # 크리티컬 및 명중/회피 시스템
        self.critical_rate = self._get_class_base_critical_rate(character_class)  # 기본 크리티컬 확률
        self.accuracy = 85 + (speed // 10)  # 기본 명중률 (85% + 스피드 보너스)
        self.evasion = 10 + (speed // 5)   # 기본 회피율 (10% + 스피드 보너스)
        
        # 특성 시스템
        available_traits = CharacterClassManager.get_class_traits(character_class)
        self.available_traits = available_traits  # 선택 가능한 모든 특성
        self.active_traits = []  # 선택된 활성 특성 (최대 2개)
        self.specialization = specialization
        self.preferred_damage_type = specialization.get("damage_type", "physical")
        
        # 상태이상 관리자
        self.status_manager = StatusManager()
        
        # 인벤토리 (개인 인벤토리) 및 경제 시스템
        self.max_carry_weight = 15.0 + (self.physical_attack * 0.05)  # 체력에 따른 하중 한계
        self.inventory = Inventory(max_size=15, max_weight=self.max_carry_weight)  # 실제 계산된 하중 제한
        self.gold = 0  # 개인 골드는 0 (파티 공용으로 관리)
        
        # 장비 슬롯
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_accessory = None
        
        # Brave 시스템 스킬 초기화
        self.brave_skills = BraveSkillDatabase.get_character_skills(character_class)
        
        # 추가 Brave 스탯들 (직업별 기초값 적용)
        # 직업별 기초 BRV 설정
        job_base_brv = {
            # 물리 딜러 - 높은 기본 MAX BRV
            "전사": {"int_brv": 1283, "max_brv": 2847},
            "검성": {"int_brv": 1337, "max_brv": 3091},
            "용기사": {"int_brv": 1401, "max_brv": 3192},
            "암흑기사": {"int_brv": 1297, "max_brv": 2983},
            "검투사": {"int_brv": 1361, "max_brv": 3158},
            "광전사": {"int_brv": 1103, "max_brv": 3467},  # 극단적 - 낮은 INT, 높은 MAX
            "사무라이": {"int_brv": 1343, "max_brv": 3041},
            
            # 마법사 - 높은 기본 INT BRV
            "아크메이지": {"int_brv": 1687, "max_brv": 2223},
            "네크로맨서": {"int_brv": 1623, "max_brv": 2031},
            "정령술사": {"int_brv": 1751, "max_brv": 2183},
            "시간술사": {"int_brv": 1827, "max_brv": 1914},  # 최고 INT, 낮은 MAX
            "차원술사": {"int_brv": 1797, "max_brv": 2067},
            "마법사": {"int_brv": 1567, "max_brv": 2149},
            "연금술사": {"int_brv": 1493, "max_brv": 2109},
            "철학자": {"int_brv": 1663, "max_brv": 1989},
            
            # 균형형 - 중간 기초값
            "성기사": {"int_brv": 1371, "max_brv": 2614},
            "기사": {"int_brv": 1233, "max_brv": 2691},
            "성직자": {"int_brv": 1429, "max_brv": 2458},
            "신관": {"int_brv": 1413, "max_brv": 2501},
            "마검사": {"int_brv": 1303, "max_brv": 2651},
            "기계공학자": {"int_brv": 1273, "max_brv": 2573},
            "무당": {"int_brv": 1457, "max_brv": 2383},
            
            # 민첩형 - 높은 INT BRV, 낮은 MAX BRV
            "도적": {"int_brv": 1561, "max_brv": 2031},
            "암살자": {"int_brv": 1631, "max_brv": 1989},
            "궁수": {"int_brv": 1507, "max_brv": 2109},
            "몽크": {"int_brv": 1439, "max_brv": 2223},
            "해적": {"int_brv": 1365, "max_brv": 2261},
            "드루이드": {"int_brv": 1535, "max_brv": 2071},
            
            # 지원형 - 안정적 기초값
            "바드": {"int_brv": 1587, "max_brv": 2301},
        }
        
        # 직업별 기초값 적용 (기본값 포함)
        base_stats = job_base_brv.get(character_class, {"int_brv": 1200, "max_brv": 2400})
        
        self.int_brv = base_stats["int_brv"]  # 고정값으로 변경
        self.max_brv = base_stats["max_brv"]  # 고정값으로 변경
        self.brv_regen = speed // 10  # Brave 자동 회복량
        self.brave_bonus_rate = 1.0  # Brave 획득 배율
        self.brv_efficiency = 1.0  # Brave 효율성
        
        # 저장 시스템 호환을 위한 Brave 속성들
        self.current_brave = 400  # 현재 Brave 포인트
        self.max_brave = 99999     # 최대 Brave 포인트
        self.initial_brave = 400 # 초기 Brave 포인트
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
            elif trait.effect_type == "trigger" and situation in ["combat_start", "on_attack", "on_kill", "on_damage"]:
                effects.update(self._apply_trigger_trait(trait, situation, **kwargs))
            elif trait.effect_type == "active" and situation == "active_use":
                effects.update(self._apply_active_trait(trait, **kwargs))
                
        return effects
    
    def _apply_passive_trait(self, trait, situation: str, **kwargs) -> Dict[str, Any]:
        """패시브 특성 효과 적용"""
        effects = {}
        
        # trait가 딕셔너리인 경우와 객체인 경우 모두 처리
        if isinstance(trait, dict):
            effect_value = trait.get('effect_value', {})
        else:
            effect_value = getattr(trait, 'effect_value', {})
        
        # 전사 특성들
        if "low_hp_damage_boost" in effect_value and self.current_hp <= self.max_hp * 0.25:
            effects["damage_multiplier"] = effect_value["low_hp_damage_boost"]
        
        if "defense_bonus" in effect_value and situation == "defending":
            effects["defense_bonus"] = effect_value["defense_bonus"]
            
        # 마법사 특성들
        if "mana_efficiency" in effect_value and situation == "skill_use":
            if random.random() < effect_value["mana_efficiency"]:
                effects["mp_cost_reduction"] = 0.5
                
        if "exp_bonus" in effect_value and situation == "combat_end":
            effects["exp_multiplier"] = 1.0 + effect_value["exp_bonus"]
            
        # 궁수 특성들  
        if "crit_chance_bonus" in effect_value and situation == "attacking":
            effects["crit_chance_bonus"] = effect_value["crit_chance_bonus"]
            
        if "dodge_bonus" in effect_value and situation == "defending":
            effects["dodge_chance_bonus"] = effect_value["dodge_bonus"]
            
        # 도적 특성들
        if "item_no_turn" in effect_value and situation == "item_use":
            effects["no_turn_cost"] = True
            
        # 성기사 특성들
        if "holy_resistance" in effect_value and situation == "taking_damage":
            enemy_type = kwargs.get("enemy_type", "")
            if enemy_type in ["undead", "demon"]:
                effects["damage_reduction"] = effect_value["holy_resistance"]
                
        if "holy_damage" in effect_value and situation == "attacking":
            effects["holy_damage_bonus"] = True
            
        # 암흑기사 특성들
        if "life_steal" in effect_value and situation == "attacking":
            effects["life_steal_bonus"] = effect_value["life_steal"]
            
        if "dark_pact" in effect_value and situation == "attacking":
            hp_ratio = self.current_hp / self.max_hp
            damage_bonus = (1.0 - hp_ratio) * 1.0  # 낮을수록 최대 100% 증가
            effects["damage_multiplier"] = 1.0 + damage_bonus
            
        # 몽크 특성들
        if "combo_multiplier" in effect_value and situation == "attacking":
            combo_count = kwargs.get("combo_count", 0)
            effects["combo_damage"] = 1.0 + (combo_count * effect_value["combo_multiplier"])
            
        if "status_resist" in effect_value and situation == "status_effect":
            effects["status_resistance"] = effect_value["status_resist"]
            
        return effects
    
    def _apply_trigger_trait(self, trait: CharacterTrait, situation: str, **kwargs) -> Dict[str, Any]:
        """트리거 특성 효과 적용"""
        effects = {}
        effect_value = trait.effect_value
        
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
        
        if len(selected_traits) == 0:
            print(f"{YELLOW}{self.name}이(가) 패시브 특성을 선택하지 않았습니다.{RESET}")
        else:
            print(f"{GREEN}{self.name}의 선택된 특성:{RESET}")
            for trait in self.active_traits:
                print(f"  {YELLOW}• {trait.name}{RESET}: {trait.description}")
        
        return True
    
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
            elif trait.effect_type == "trigger":
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
        """상처에 의해 제한된 최대 HP"""
        return self.max_hp - self.wounds
        
    @property
    def max_wounds(self) -> int:
        """최대 상처량 (최대 HP의 75%)"""
        return int(self.max_hp * 0.75)
        
    def add_wounds(self, wound_amount: int):
        """상처 추가 (direct wound damage)"""
        if not self.is_alive:
            return
        
        wound_amount = max(0, int(wound_amount))
        self.wounds = min(self.wounds + wound_amount, self.max_wounds)
        
    def take_damage(self, damage: int) -> int:
        """데미지를 받고 실제 입은 데미지량 반환"""
        if not self.is_alive:
            return 0
            
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        
        # 상처 누적 (받은 데미지의 25%)
        wound_increase = int(actual_damage * 0.25)
        self.wounds = min(self.wounds + wound_increase, self.max_wounds)
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            print(f"{self.name}이(가) 쓰러졌습니다!")
            
        return actual_damage
        
    def heal(self, heal_amount: int) -> int:
        """회복하고 실제 회복량 반환"""
        if not self.is_alive:
            return 0
            
        # 제한된 최대 HP까지 회복
        possible_heal = min(heal_amount, self.limited_max_hp - self.current_hp)
        self.current_hp += possible_heal
        
        # 초과 회복량이 있다면 상처 회복
        excess_heal = heal_amount - possible_heal
        if excess_heal > 0:
            wound_heal = int(excess_heal * 0.25)
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
        """ATB 게이지 업데이트"""
        if self.is_alive:
            self.atb_gauge = min(100, self.atb_gauge + self.atb_speed)
            
    def reset_atb(self):
        """ATB 게이지 리셋"""
        self.atb_gauge = 0
        
    def can_act(self) -> bool:
        """행동 가능한지 확인"""
        return self.is_alive and self.atb_gauge >= 100 and self.status_manager.can_act()
        
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
        return self.status_manager.process_turn_effects()
        
    def equip_item(self, item: Item) -> bool:
        """아이템 장착"""
        if item.item_type.value == "무기":
            self.equipped_weapon = item
        elif item.item_type.value == "방어구":
            self.equipped_armor = item
        elif item.item_type.value == "장신구":
            self.equipped_accessory = item
        else:
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
            
            # 다음 레벨까지 필요한 경험치 계산 (레벨당 증가)
            self.experience_to_next = 30 + (self.level - 1) * 8
            
            print(f"🎉 {self.name}이(가) 레벨 {old_level} → {self.level}로 상승!")
            self.show_stat_gains(stat_gains)
            
        return leveled_up
    
    def calculate_level_up_gains(self) -> dict:
        """레벨업 시 능력치 증가량 계산"""
        # 클래스별 성장률 (MP 성장량을 대폭 줄임)
        growth_rates = {
            "전사": {"hp": 25, "mp": 1, "p_atk": 6, "m_atk": 2, "p_def": 5, "m_def": 2, "speed": 3},
            "아크메이지": {"hp": 15, "mp": 3, "p_atk": 2, "m_atk": 8, "p_def": 2, "m_def": 6, "speed": 4},
            "궁수": {"hp": 18, "mp": 1, "p_atk": 6, "m_atk": 2, "p_def": 3, "m_def": 4, "speed": 7},
            "도적": {"hp": 16, "mp": 1, "p_atk": 5, "m_atk": 2, "p_def": 2, "m_def": 2, "speed": 8},
            "성기사": {"hp": 20, "mp": 2, "p_atk": 4, "m_atk": 6, "p_def": 5, "m_def": 6, "speed": 2},
            "암흑기사": {"hp": 22, "mp": 1, "p_atk": 6, "m_atk": 4, "p_def": 4, "m_def": 4, "speed": 4},
            "몽크": {"hp": 19, "mp": 2, "p_atk": 5, "m_atk": 2, "p_def": 4, "m_def": 4, "speed": 6},
            "바드": {"hp": 14, "mp": 2, "p_atk": 2, "m_atk": 5, "p_def": 2, "m_def": 4, "speed": 5},
            "네크로맨서": {"hp": 12, "mp": 3, "p_atk": 2, "m_atk": 8, "p_def": 2, "m_def": 6, "speed": 4},
            "용기사": {"hp": 28, "mp": 1, "p_atk": 6, "m_atk": 2, "p_def": 6, "m_def": 4, "speed": 2},
            "검성": {"hp": 21, "mp": 1, "p_atk": 7, "m_atk": 2, "p_def": 4, "m_def": 4, "speed": 4},
            "정령술사": {"hp": 13, "mp": 3, "p_atk": 2, "m_atk": 8, "p_def": 2, "m_def": 6, "speed": 4},
            "암살자": {"hp": 14, "mp": 1, "p_atk": 6, "m_atk": 2, "p_def": 2, "m_def": 2, "speed": 8},
            "기계공학자": {"hp": 17, "mp": 2, "p_atk": 4, "m_atk": 4, "p_def": 4, "m_def": 4, "speed": 4},
            "무당": {"hp": 16, "mp": 2, "p_atk": 2, "m_atk": 6, "p_def": 4, "m_def": 6, "speed": 2},
            "해적": {"hp": 20, "mp": 1, "p_atk": 6, "m_atk": 2, "p_def": 4, "m_def": 2, "speed": 6},
            "사무라이": {"hp": 20, "mp": 1, "p_atk": 7, "m_atk": 2, "p_def": 4, "m_def": 4, "speed": 4},
            "드루이드": {"hp": 16, "mp": 2, "p_atk": 2, "m_atk": 6, "p_def": 4, "m_def": 6, "speed": 4},
            "철학자": {"hp": 14, "mp": 3, "p_atk": 2, "m_atk": 5, "p_def": 2, "m_def": 6, "speed": 3},
            "시간술사": {"hp": 12, "mp": 3, "p_atk": 2, "m_atk": 8, "p_def": 2, "m_def": 6, "speed": 4},
            "연금술사": {"hp": 15, "mp": 2, "p_atk": 2, "m_atk": 6, "p_def": 2, "m_def": 4, "speed": 4},
            "검투사": {"hp": 24, "mp": 1, "p_atk": 7, "m_atk": 2, "p_def": 4, "m_def": 2, "speed": 4},
            "기사": {"hp": 30, "mp": 1, "p_atk": 5, "m_atk": 2, "p_def": 7, "m_def": 4, "speed": 2},
            "신관": {"hp": 18, "mp": 2, "p_atk": 2, "m_atk": 6, "p_def": 4, "m_def": 8, "speed": 2},
            "마검사": {"hp": 18, "mp": 2, "p_atk": 5, "m_atk": 6, "p_def": 4, "m_def": 4, "speed": 4},
            "차원술사": {"hp": 12, "mp": 3, "p_atk": 2, "m_atk": 8, "p_def": 2, "m_def": 6, "speed": 4},
            "광전사": {"hp": 26, "mp": 1, "p_atk": 9, "m_atk": 1, "p_def": 2, "m_def": 1, "speed": 5},
            "마법사": {"hp": 13, "mp": 3, "p_atk": 2, "m_atk": 8, "p_def": 2, "m_def": 6, "speed": 4},
            "성직자": {"hp": 18, "mp": 2, "p_atk": 2, "m_atk": 6, "p_def": 4, "m_def": 8, "speed": 2},
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
        self.atb_speed = self.speed
        
        # Brave 능력치도 재계산
        self.update_brave_on_level_up()
    
    def update_brave_on_level_up(self):
        """레벨업 시 Brave 능력치 업데이트"""
        try:
            from .balance import GameBalance
            balance_stats = GameBalance.get_character_brave_stats(self.character_class, self.level)
            
            # 기존 Brave 비율 유지하면서 업데이트
            old_brave_ratio = self.current_brave / max(1, self.int_brv)
            
            self.int_brv = balance_stats['int_brv']
            self.max_brv = balance_stats['max_brv']
            self.current_brave = int(self.int_brv * old_brave_ratio)
            self.brave_bonus_rate = balance_stats.get('brv_efficiency', 1.0)
            self.brv_loss_resistance = balance_stats.get('brv_loss_resistance', 1.0)
        except:
            # 기본값으로 증가 (대폭 강화)
            # 레벨당 더 큰 폭으로 증가하도록 수정
            level_multiplier = 1 + (self.level - 1) * 0.15  # 레벨당 15% 증가
            base_int_brv = 1000 + (self.speed * 10)
            base_max_brv = 99999 + (self.physical_attack * 50)
            
            self.int_brv = int(base_int_brv * level_multiplier)
            self.max_brv = int(base_max_brv * level_multiplier)
            
            # 직업별 BRV 성장 특성 (레벨당 고정 증가량)
            job_brv_growth = {
                # 물리 딜러 - 높은 MAX BRV
                "전사": {"int_brv": 40, "max_brv": 7.5},
                "검성": {"int_brv": 45, "max_brv": 8.0},
                "용기사": {"int_brv": 50, "max_brv": 8.75},
                "암흑기사": {"int_brv": 42, "max_brv": 7.75},
                "검투사": {"int_brv": 48, "max_brv": 8.5},
                "광전사": {"int_brv": 35, "max_brv": 10.0},  # 극단적 MAX BRV
                "사무라이": {"int_brv": 45, "max_brv": 8.125},
                
                # 마법사 - 높은 INT BRV
                "아크메이지": {"int_brv": 80, "max_brv": 5.0},
                "네크로맨서": {"int_brv": 75, "max_brv": 4.5},
                "정령술사": {"int_brv": 85, "max_brv": 4.75},
                "시간술사": {"int_brv": 90, "max_brv": 4.25},  # 최고 INT BRV
                "차원술사": {"int_brv": 88, "max_brv": 4.375},
                "마법사": {"int_brv": 70, "max_brv": 4.625},
                "연금술사": {"int_brv": 65, "max_brv": 4.875},
                "철학자": {"int_brv": 78, "max_brv": 4.7},
                
                # 균형형 - 중간 성장
                "성기사": {"int_brv": 55, "max_brv": 6.25},
                "기사": {"int_brv": 50, "max_brv": 6.5},
                "성직자": {"int_brv": 60, "max_brv": 5.75},
                "신관": {"int_brv": 58, "max_brv": 5.875},
                "마검사": {"int_brv": 52, "max_brv": 6.125},
                "기계공학자": {"int_brv": 48, "max_brv": 6.0},
                "무당": {"int_brv": 62, "max_brv": 5.5},
                
                # 민첩형 - 빠른 BRV 회복
                "도적": {"int_brv": 65, "max_brv": 4.5},
                "암살자": {"int_brv": 70, "max_brv": 4.25},
                "궁수": {"int_brv": 60, "max_brv": 4.75},
                "몽크": {"int_brv": 58, "max_brv": 4.875},
                "해적": {"int_brv": 55, "max_brv": 5.0},
                "드루이드": {"int_brv": 62, "max_brv": 4.625},
                
                # 지원형 - 안정적 성장
                "바드": {"int_brv": 68, "max_brv": 5.25},
            }
            
            # 직업별 성장 적용 (기본값 포함)
            growth = job_brv_growth.get(self.character_class, {"int_brv": 50, "max_brv": 200})
            
            self.int_brv += self.level * growth["int_brv"]
            self.max_brv += self.level * growth["max_brv"]
    
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
                skills.append("연사")
        
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
        ratio = self.atb_gauge / 100
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
            if hasattr(member, 'equipment'):
                for slot, equipment in member.equipment.items():
                    if equipment and hasattr(equipment, 'stats') and equipment.stats:
                        vision_bonus += equipment.stats.get('vision_range', 0)
        
        return base_vision + vision_bonus
    
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
    
    def equip_item(self, item) -> bool:
        """아이템 착용"""
        if not hasattr(item, 'item_type'):
            return False
            
        from .items import ItemType
        
        if item.item_type == ItemType.WEAPON:
            self.equipped_weapon = item
            print(f"{self.name}이(가) {item.name}을(를) 착용했습니다.")
        elif item.item_type == ItemType.ARMOR:
            self.equipped_armor = item
            print(f"{self.name}이(가) {item.name}을(를) 착용했습니다.")
        elif item.item_type == ItemType.ACCESSORY:
            self.equipped_accessory = item
            print(f"{self.name}이(가) {item.name}을(를) 착용했습니다.")
        else:
            return False
        
        # 장비 효과 적용
        self._apply_equipment_effects()
        return True
    
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
        self.equipment_speed_bonus = 0
        
        # 착용 중인 장비들의 효과 적용
        equipped_items = [item for item in [self.equipped_weapon, self.equipped_armor, self.equipped_accessory] if item]
        
        for item in equipped_items:
            if hasattr(item, 'stats'):
                stats = item.stats
                self.equipment_attack_bonus += stats.get('physical_attack', 0)
                self.equipment_defense_bonus += stats.get('physical_defense', 0)
                self.equipment_magic_bonus += stats.get('magic_attack', 0)
                self.equipment_speed_bonus += stats.get('speed', 0)
    
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
    
    def get_total_speed(self) -> int:
        """장비 보너스가 포함된 총 속도"""
        base_speed = self.speed + self.temp_speed_bonus
        equipment_bonus = getattr(self, 'equipment_speed_bonus', 0)
        return base_speed + equipment_bonus
