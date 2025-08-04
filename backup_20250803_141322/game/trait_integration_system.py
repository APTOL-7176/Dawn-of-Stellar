#!/usr/bin/env python3
"""
🔥 특성 시스템 실제 연동 - temp_ 속성들의 게임 내 활용
- 모든 temp_ 속성들을 실제 게임 로직에 연결
- 상대적 수치 시스템으로 밸런스 개선
- 특성 효과의 시각적 피드백 강화
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .character import Character

class TraitEffectProcessor:
    """특성 효과 처리기 - temp_ 속성들을 실제 게임에 적용"""
    
    @staticmethod
    def apply_combat_bonuses(character: 'Character') -> Dict[str, float]:
        """전투 관련 temp_ 보너스들을 실제 수치로 변환"""
        bonuses = {
            'physical_attack_multiplier': 1.0,
            'magic_attack_multiplier': 1.0,
            'physical_defense_multiplier': 1.0,
            'magic_defense_multiplier': 1.0,
            'speed_multiplier': 1.0,
            'critical_rate_bonus': 0.0,
            'dodge_rate_bonus': 0.0,
            'accuracy_bonus': 0.0,
            'penetration_bonus': 0.0,
            'life_steal_rate': 0.0
        }
        
        # temp_attack_bonus를 비율로 변환 (절대값 → 상대값)
        if hasattr(character, 'temp_attack_bonus') and character.temp_attack_bonus > 0:
            base_attack = max(character.physical_attack, character.magic_attack)
            bonus_ratio = min(character.temp_attack_bonus / base_attack, 1.5)  # 최대 150% 보너스
            bonuses['physical_attack_multiplier'] += bonus_ratio
            bonuses['magic_attack_multiplier'] += bonus_ratio
        
        # temp_defense_bonus를 비율로 변환
        if hasattr(character, 'temp_defense_bonus') and character.temp_defense_bonus > 0:
            base_defense = max(character.physical_defense, character.magic_defense)
            bonus_ratio = min(character.temp_defense_bonus / base_defense, 1.0)  # 최대 100% 보너스
            bonuses['physical_defense_multiplier'] += bonus_ratio
            bonuses['magic_defense_multiplier'] += bonus_ratio
        
        # temp_speed_bonus를 비율로 변환
        if hasattr(character, 'temp_speed_bonus') and character.temp_speed_bonus > 0:
            speed_ratio = min(character.temp_speed_bonus / character.speed, 0.8)  # 최대 80% 보너스
            bonuses['speed_multiplier'] += speed_ratio
        
        # temp_crit_bonus를 확률로 변환
        if hasattr(character, 'temp_crit_bonus') and character.temp_crit_bonus > 0:
            bonuses['critical_rate_bonus'] = min(character.temp_crit_bonus, 50.0)  # 최대 50% 크리티컬 확률 증가
        
        # temp_dodge_bonus를 확률로 변환
        if hasattr(character, 'temp_dodge_bonus') and character.temp_dodge_bonus > 0:
            bonuses['dodge_rate_bonus'] = min(character.temp_dodge_bonus, 40.0)  # 최대 40% 회피율 증가
        
        # temp_penetration을 관통력으로 변환
        if hasattr(character, 'temp_penetration') and character.temp_penetration > 0:
            bonuses['penetration_bonus'] = min(character.temp_penetration, 30.0)  # 최대 30% 방어력 무시
        
        # temp_life_steal을 생명력 흡수로 변환
        if hasattr(character, 'temp_life_steal') and character.temp_life_steal > 0:
            bonuses['life_steal_rate'] = min(character.temp_life_steal, 25.0)  # 최대 25% 생명력 흡수
            
        return bonuses
    
    @staticmethod
    def apply_damage_modifiers(attacker: 'Character', defender: 'Character', 
                             base_damage: int, damage_type: str = "physical") -> int:
        """공격 시 특성 효과 적용"""
        final_damage = base_damage
        
        # 공격자의 특성 효과
        bonuses = TraitEffectProcessor.apply_combat_bonuses(attacker)
        
        if damage_type == "physical":
            final_damage *= bonuses['physical_attack_multiplier']
        elif damage_type == "magic":
            final_damage *= bonuses['magic_attack_multiplier']
        
        # 관통력 적용
        if bonuses['penetration_bonus'] > 0:
            penetration_chance = bonuses['penetration_bonus'] / 100.0
            if random.random() < penetration_chance:
                final_damage *= 1.3  # 관통 시 30% 추가 데미지
                print(f"⚡ {attacker.name}의 공격이 방어력을 관통했습니다!")
        
        # 특수 데미지 타입들
        if hasattr(attacker, 'temp_holy_damage') and attacker.temp_holy_damage:
            if hasattr(defender, 'character_class') and defender.character_class in ["네크로맨서", "암흑기사"]:
                final_damage *= 1.5
                print(f"✨ 신성한 데미지가 {defender.name}에게 효과적입니다!")
        
        if hasattr(attacker, 'temp_fire_damage') and attacker.temp_fire_damage:
            final_damage *= 1.2
            print(f"🔥 화염 속성 추가 데미지!")
        
        if hasattr(attacker, 'temp_undead_damage') and attacker.temp_undead_damage > 0:
            # 언데드 타입 적에게 추가 데미지 (구현 필요)
            final_damage += attacker.temp_undead_damage
        
        # 생명력 흡수
        if bonuses['life_steal_rate'] > 0:
            life_steal_chance = bonuses['life_steal_rate'] / 100.0
            if random.random() < life_steal_chance:
                heal_amount = int(final_damage * 0.3)  # 데미지의 30% 회복
                old_hp = attacker.current_hp
                attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal_amount)
                actual_heal = attacker.current_hp - old_hp
                if actual_heal > 0:
                    print(f"💚 {attacker.name}이 {actual_heal} HP를 흡수했습니다!")
        
        return int(final_damage)
    
    @staticmethod
    def apply_defense_modifiers(defender: 'Character', incoming_damage: int, 
                              damage_type: str = "physical") -> int:
        """방어 시 특성 효과 적용"""
        final_damage = incoming_damage
        
        # 방어자의 특성 효과
        bonuses = TraitEffectProcessor.apply_combat_bonuses(defender)
        
        # 기본 방어력 보너스
        if damage_type == "physical":
            defense_reduction = bonuses['physical_defense_multiplier'] - 1.0
        elif damage_type == "magic":
            defense_reduction = bonuses['magic_defense_multiplier'] - 1.0
        else:
            defense_reduction = 0.0
        
        # 방어력이 높을수록 데미지 감소 (상대적 계산)
        base_defense = defender.physical_defense if damage_type == "physical" else defender.magic_defense
        total_defense = base_defense * bonuses.get(f'{damage_type}_defense_multiplier', 1.0)
        
        # 방어력 기반 데미지 감소 공식 개선
        damage_reduction = min(total_defense / (total_defense + final_damage), 0.8)  # 최대 80% 감소
        final_damage *= (1.0 - damage_reduction)
        
        # 특수 저항
        if hasattr(defender, 'temp_physical_resistance') and damage_type == "physical":
            resistance = min(defender.temp_physical_resistance, 50.0) / 100.0
            final_damage *= (1.0 - resistance)
            if resistance > 0:
                print(f"🛡️ {defender.name}의 물리 저항!")
        
        if hasattr(defender, 'temp_status_resist') and defender.temp_status_resist > 0:
            # 상태이상 저항은 별도 처리
            pass
        
        # 크리티컬 면역
        if hasattr(defender, 'temp_crit_immunity') and defender.temp_crit_immunity > 0:
            crit_immunity_chance = min(defender.temp_crit_immunity, 100.0) / 100.0
            if random.random() < crit_immunity_chance:
                print(f"🛡️ {defender.name}이 크리티컬을 무효화했습니다!")
                # 크리티컬 데미지를 일반 데미지로 감소 (구현 방법에 따라 조정)
                final_damage *= 0.7
        
        return max(1, int(final_damage))  # 최소 1 데미지
    
    @staticmethod
    def calculate_dodge_chance(defender: 'Character') -> float:
        """회피율 계산 (특성 보너스 포함)"""
        base_dodge = defender.evasion if hasattr(defender, 'evasion') else 10.0
        
        bonuses = TraitEffectProcessor.apply_combat_bonuses(defender)
        final_dodge = base_dodge + bonuses['dodge_rate_bonus']
        
        # 속도 기반 추가 회피율
        speed_bonus = (defender.speed * bonuses['speed_multiplier'] - defender.speed) * 0.1
        final_dodge += speed_bonus
        
        return min(final_dodge, 75.0) / 100.0  # 최대 75% 회피율
    
    @staticmethod
    def calculate_critical_chance(attacker: 'Character') -> float:
        """크리티컬 확률 계산 (특성 보너스 포함)"""
        base_crit = attacker.critical_rate if hasattr(attacker, 'critical_rate') else 5.0
        
        bonuses = TraitEffectProcessor.apply_combat_bonuses(attacker)
        final_crit = base_crit + bonuses['critical_rate_bonus']
        
        return min(final_crit, 95.0) / 100.0  # 최대 95% 크리티컬 확률
    
    @staticmethod
    def apply_utility_effects(character: 'Character', context: str = "general") -> Dict[str, Any]:
        """유틸리티 특성 효과 적용"""
        effects = {}
        
        # 경험치 보너스
        if hasattr(character, 'temp_exp_bonus') and character.temp_exp_bonus > 0:
            effects['exp_multiplier'] = 1.0 + (character.temp_exp_bonus / 100.0)
        
        # 골드 보너스
        if hasattr(character, 'temp_gold_bonus') and character.temp_gold_bonus > 0:
            effects['gold_multiplier'] = 1.0 + (character.temp_gold_bonus / 100.0)
        
        # 보물 발견 보너스
        if hasattr(character, 'temp_treasure_bonus') and character.temp_treasure_bonus > 0:
            effects['treasure_find_bonus'] = character.temp_treasure_bonus
        
        # 시야 보너스
        if hasattr(character, 'temp_vision_bonus') and character.temp_vision_bonus > 0:
            effects['vision_range_bonus'] = character.temp_vision_bonus
        
        # MP 효율성
        if hasattr(character, 'temp_mana_efficiency') and character.temp_mana_efficiency > 0:
            effects['mp_cost_reduction'] = min(character.temp_mana_efficiency, 50.0) / 100.0
        
        # 스킬 비용 감소
        if hasattr(character, 'temp_skill_cost_reduction') and character.temp_skill_cost_reduction > 0:
            effects['skill_cost_reduction'] = min(character.temp_skill_cost_reduction, 40.0) / 100.0
        
        # 치유 효과 증폭
        if hasattr(character, 'temp_heal_boost') and character.temp_heal_boost > 0:
            effects['heal_effectiveness'] = 1.0 + (character.temp_heal_boost / 100.0)
        
        # 포션 효과 증폭
        if hasattr(character, 'temp_potion_boost') and character.temp_potion_boost > 0:
            effects['potion_effectiveness'] = 1.0 + (character.temp_potion_boost / 100.0)
        
        return effects
    
    @staticmethod
    def apply_special_abilities(character: 'Character', target: 'Character' = None, 
                              context: str = "combat") -> List[str]:
        """특수 능력 발동 (불린 타입 temp_ 속성들)"""
        activated_abilities = []
        
        # 첫 번째 공격 우선권
        if hasattr(character, 'temp_first_strike') and character.temp_first_strike:
            activated_abilities.append("⚡ 선제공격 준비!")
        
        # 독 무기
        if hasattr(character, 'temp_poison_weapon') and character.temp_poison_weapon:
            if target and random.random() < 0.3:  # 30% 확률
                activated_abilities.append(f"☠️ {character.name}의 독 무기가 {target.name}을 중독시켰습니다!")
                # 실제 독 상태이상 적용 (구현 필요)
        
        # 무한 폭탄
        if hasattr(character, 'temp_infinite_bombs') and character.temp_infinite_bombs:
            activated_abilities.append("💣 무한 폭탄 효과 활성화!")
        
        # 죽음 면역
        if hasattr(character, 'temp_death_immunity') and character.temp_death_immunity:
            if character.current_hp <= 0:
                character.current_hp = 1
                activated_abilities.append(f"✨ {character.name}이 죽음을 면역했습니다!")
        
        # 패턴 분석
        if hasattr(character, 'temp_pattern_analysis') and character.temp_pattern_analysis:
            activated_abilities.append("🧠 적의 패턴을 분석 중...")
        
        # 미래 시야
        if hasattr(character, 'temp_future_sight') and character.temp_future_sight:
            activated_abilities.append("👁️ 미래를 예측하여 회피율 상승!")
        
        # 저항 무시
        if hasattr(character, 'temp_ignore_resistance') and character.temp_ignore_resistance:
            activated_abilities.append("⚡ 모든 저항을 무시합니다!")
        
        # 랜덤 속성
        if hasattr(character, 'temp_random_element') and character.temp_random_element:
            elements = ["화염", "빙결", "번개", "대지"]
            random_element = random.choice(elements)
            activated_abilities.append(f"🌟 랜덤 속성: {random_element}!")
        
        # 하이브리드 데미지
        if hasattr(character, 'temp_hybrid_damage') and character.temp_hybrid_damage:
            activated_abilities.append("⚔️🔮 물리+마법 하이브리드 공격!")
        
        # 공격 시 MP 획득
        if hasattr(character, 'temp_attack_mp_gain') and character.temp_attack_mp_gain:
            mp_gain = random.randint(3, 8)
            character.current_mp = min(character.max_mp, character.current_mp + mp_gain)
            activated_abilities.append(f"💙 공격으로 MP {mp_gain} 회복!")
        
        # 마법 무기
        if hasattr(character, 'temp_magic_weapon') and character.temp_magic_weapon:
            activated_abilities.append("✨ 물리 공격이 마법 데미지로 변환!")
        
        # 이중 속성
        if hasattr(character, 'temp_dual_element') and character.temp_dual_element:
            activated_abilities.append("🌟⚡ 이중 속성 공격 발동!")
        
        # 무제한 저장소
        if hasattr(character, 'temp_unlimited_storage') and character.temp_unlimited_storage:
            activated_abilities.append("🎒 무제한 인벤토리 활성화!")
        
        # 상태이상 면역
        if hasattr(character, 'temp_status_immunity') and character.temp_status_immunity:
            activated_abilities.append("🛡️ 모든 상태이상에 면역!")
        
        return activated_abilities
    
    @staticmethod
    def reset_temporary_effects(character: 'Character', reset_type: str = "turn_end"):
        """임시 효과 초기화"""
        if reset_type == "turn_end":
            # 턴 종료 시 감소하는 효과들
            decreasing_effects = [
                'stealth_turns', 'temp_next_attack_bonus'
            ]
            
            for effect in decreasing_effects:
                if hasattr(character, effect):
                    current_value = getattr(character, effect)
                    if isinstance(current_value, (int, float)) and current_value > 0:
                        setattr(character, effect, current_value - 1)
        
        elif reset_type == "combat_end":
            # 전투 종료 시 초기화되는 효과들
            combat_effects = [
                'temp_next_attack_bonus', 'temp_first_strike',
                'temp_pattern_analysis', 'temp_future_sight',
                'stealth_turns'
            ]
            
            for effect in combat_effects:
                if hasattr(character, effect):
                    if isinstance(getattr(character, effect), bool):
                        setattr(character, effect, False)
                    else:
                        setattr(character, effect, 0)
    
    @staticmethod
    def get_active_trait_display(character: 'Character') -> List[str]:
        """현재 활성화된 특성 효과들을 표시용으로 반환"""
        active_effects = []
        
        # 수치 보너스들
        if hasattr(character, 'temp_attack_bonus') and character.temp_attack_bonus > 0:
            bonus_percent = int((character.temp_attack_bonus / character.physical_attack) * 100)
            active_effects.append(f"⚔️ 공격력 +{bonus_percent}%")
        
        if hasattr(character, 'temp_defense_bonus') and character.temp_defense_bonus > 0:
            bonus_percent = int((character.temp_defense_bonus / character.physical_defense) * 100)
            active_effects.append(f"🛡️ 방어력 +{bonus_percent}%")
        
        if hasattr(character, 'temp_speed_bonus') and character.temp_speed_bonus > 0:
            bonus_percent = int((character.temp_speed_bonus / character.speed) * 100)
            active_effects.append(f"💨 속도 +{bonus_percent}%")
        
        if hasattr(character, 'temp_crit_bonus') and character.temp_crit_bonus > 0:
            active_effects.append(f"💥 크리티컬 +{character.temp_crit_bonus}%")
        
        # 특수 효과들
        if hasattr(character, 'temp_first_strike') and character.temp_first_strike:
            active_effects.append("⚡ 선제공격")
        
        if hasattr(character, 'temp_death_immunity') and character.temp_death_immunity:
            active_effects.append("✨ 죽음면역")
        
        if hasattr(character, 'stealth_turns') and character.stealth_turns > 0:
            active_effects.append(f"🥷 은신 ({character.stealth_turns}턴)")
        
        if hasattr(character, 'temp_status_immunity') and character.temp_status_immunity:
            active_effects.append("🛡️ 상태면역")
        
        return active_effects

# 전역 인스턴스
trait_processor = TraitEffectProcessor()

def get_trait_processor() -> TraitEffectProcessor:
    """특성 효과 처리기 반환"""
    return trait_processor

def apply_trait_effects_to_damage(attacker: 'Character', defender: 'Character', 
                                base_damage: int, damage_type: str = "physical") -> int:
    """편의 함수: 데미지에 특성 효과 적용"""
    return trait_processor.apply_damage_modifiers(attacker, defender, base_damage, damage_type)

def apply_trait_effects_to_defense(defender: 'Character', incoming_damage: int, 
                                 damage_type: str = "physical") -> int:
    """편의 함수: 방어에 특성 효과 적용"""
    return trait_processor.apply_defense_modifiers(defender, incoming_damage, damage_type)

def calculate_trait_dodge_chance(character: 'Character') -> float:
    """편의 함수: 특성 포함 회피율 계산"""
    return trait_processor.calculate_dodge_chance(character)

def calculate_trait_critical_chance(character: 'Character') -> float:
    """편의 함수: 특성 포함 크리티컬 확률 계산"""
    return trait_processor.calculate_critical_chance(character)

def get_character_utility_bonuses(character: 'Character') -> Dict[str, Any]:
    """편의 함수: 캐릭터의 유틸리티 보너스 반환"""
    return trait_processor.apply_utility_effects(character)

def trigger_special_abilities(character: 'Character', target: 'Character' = None) -> List[str]:
    """편의 함수: 특수 능력 발동"""
    return trait_processor.apply_special_abilities(character, target)

def reset_character_temporary_effects(character: 'Character', reset_type: str = "turn_end"):
    """편의 함수: 임시 효과 초기화"""
    trait_processor.reset_temporary_effects(character, reset_type)
