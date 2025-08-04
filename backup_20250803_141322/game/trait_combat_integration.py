"""
특성 효과 전투 시스템 연동 모듈
character.py의 temp_* 속성들을 실제 전투에서 활용하도록 구현
"""

import random
from typing import Dict, Any, List
from .character import Character

class TraitCombatIntegrator:
    """특성 효과를 전투 시스템에 연동하는 클래스"""
    
    @staticmethod
    def apply_attack_trait_effects(attacker: Character, target: Character, base_damage: int) -> int:
        """공격 시 특성 효과를 실제 데미지에 적용"""
        modified_damage = base_damage
        
        # 1. 화염 피해 (temp_fire_damage)
        if getattr(attacker, 'temp_fire_damage', False):
            fire_bonus = int(base_damage * 0.15)  # 15% 추가 화염 피해
            modified_damage += fire_bonus
            print(f"🔥 {attacker.name}의 화염 속성으로 {fire_bonus} 추가 피해!")
            
            # 화상 상태이상 부여 (보스는 저항)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if not is_boss or random.random() > 0.75:  # 보스 75% 저항
                setattr(target, 'is_burning', True)
                setattr(target, 'burn_turns', 3)
                burn_damage = int(target.max_hp * 0.02) if is_boss else int(target.max_hp * 0.04)
                setattr(target, 'burn_damage', burn_damage)
                print(f"🔥 {target.name}이(가) 화상에 걸렸습니다!")
        
        # 2. 독 무기 (temp_poison_weapon)
        if getattr(attacker, 'temp_poison_weapon', False):
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if not is_boss or random.random() > 0.8:  # 보스 80% 저항
                setattr(target, 'is_poisoned', True)
                setattr(target, 'poison_turns', 4)
                poison_damage = int(target.max_hp * 0.03) if is_boss else int(target.max_hp * 0.05)
                setattr(target, 'poison_damage', poison_damage)
                print(f"💚 {attacker.name}의 독 무기로 {target.name}이(가) 중독되었습니다!")
        
        # 3. 신성 피해 (temp_holy_damage)
        if getattr(attacker, 'temp_holy_damage', False):
            # 언데드/악마 타입에게 추가 피해
            enemy_type = getattr(target, 'monster_type', 'normal')
            if enemy_type in ['undead', 'demon', 'dark']:
                holy_bonus = int(base_damage * 0.5)  # 50% 추가 신성 피해
                modified_damage += holy_bonus
                print(f"✨ {attacker.name}의 신성한 힘으로 {target.name}에게 {holy_bonus} 추가 피해!")
            else:
                holy_bonus = int(base_damage * 0.1)  # 일반적으로 10% 추가
                modified_damage += holy_bonus
                print(f"✨ 신성한 힘으로 {holy_bonus} 추가 피해!")
        
        # 4. 관통 피해 (temp_penetration)
        penetration = getattr(attacker, 'temp_penetration', 0)
        if penetration > 0:
            # 적의 방어력 일부 무시
            ignored_defense = int(target.physical_defense * penetration)
            penetration_bonus = int(ignored_defense * 0.5)  # 무시한 방어력의 50%만큼 추가 피해
            modified_damage += penetration_bonus
            print(f"🎯 {attacker.name}의 약점 감지로 방어력 일부 무시! {penetration_bonus} 추가 피해!")
        
        # 5. 폭발 강화 (temp_explosion_boost)
        explosion_boost = getattr(attacker, 'temp_explosion_boost', 0)
        if explosion_boost > 0:
            explosion_bonus = int(base_damage * explosion_boost)
            modified_damage += explosion_bonus
            print(f"💥 {attacker.name}의 폭발 강화로 {explosion_bonus} 추가 피해!")
        
        # 6. 원소 강화 (temp_elemental_boost)
        elemental_boost = getattr(attacker, 'temp_elemental_boost', 0)
        if elemental_boost > 0:
            elemental_bonus = int(base_damage * elemental_boost)
            modified_damage += elemental_bonus
            print(f"🌟 {attacker.name}의 원소 지배력으로 {elemental_bonus} 추가 피해!")
        
        return max(1, modified_damage)  # 최소 1 피해 보장
    
    @staticmethod
    def apply_skill_cost_reduction(character: Character, base_mp_cost: int) -> int:
        """스킬 사용 시 MP 코스트 감소 특성 효과 적용"""
        reduced_cost = base_mp_cost
        
        # 1. 정신 조화 (temp_mental_harmony) - MP 코스트 감소
        mental_harmony = getattr(character, 'temp_mental_harmony', 0)
        if mental_harmony > 0:
            harmony_reduction = int(base_mp_cost * mental_harmony)
            reduced_cost -= harmony_reduction
            if harmony_reduction > 0:
                print(f"🧘 {character.name}의 정신 조화로 MP 비용 {harmony_reduction} 감소!")
        
        # 2. 마력 절약 (temp_mana_efficiency) - MP 코스트 감소
        mana_efficiency = getattr(character, 'temp_mana_efficiency', 0)
        if mana_efficiency > 0:
            efficiency_reduction = int(base_mp_cost * mana_efficiency)
            reduced_cost -= efficiency_reduction
            if efficiency_reduction > 0:
                print(f"✨ {character.name}의 마력 절약으로 MP 비용 {efficiency_reduction} 감소!")
        
        # 3. 신성한 축복 (temp_divine_blessing) - 회복 계열 스킬 코스트 감소
        divine_blessing = getattr(character, 'temp_divine_blessing', 0)
        if divine_blessing > 0:
            # 현재 사용 중인 스킬이 회복 계열인지 확인 (추후 확장 가능)
            blessing_reduction = int(base_mp_cost * divine_blessing * 0.5)  # 50% 효율
            reduced_cost -= blessing_reduction
            if blessing_reduction > 0:
                print(f"🌟 {character.name}의 신성한 축복으로 MP 비용 {blessing_reduction} 감소!")
        
        return max(0, reduced_cost)  # 최소 0 MP (무료 사용 가능)
    
    @staticmethod
    def apply_defense_trait_effects(defender: Character, incoming_damage: int) -> int:
        """방어 시 특성 효과를 실제 피해 감소에 적용"""
        reduced_damage = incoming_damage
        
        # 1. 물리 저항 (temp_physical_resistance)
        physical_resistance = getattr(defender, 'temp_physical_resistance', 0)
        if physical_resistance > 0:
            resistance_reduction = int(incoming_damage * physical_resistance)
            reduced_damage -= resistance_reduction
            print(f"🛡️ {defender.name}의 물리 저항으로 {resistance_reduction} 피해 감소!")
        
        # 2. 언데드 저항 (temp_undead_resistance)
        undead_resistance = getattr(defender, 'temp_undead_resistance', 0)
        if undead_resistance > 0:
            # 공격자가 언데드/어둠 타입인지 확인
            attacker_type = getattr(defender, 'last_attacker_type', 'normal')
            if attacker_type in ['undead', 'dark', 'demon']:
                undead_reduction = int(incoming_damage * undead_resistance)
                reduced_damage -= undead_reduction
                print(f"✨ {defender.name}의 언데드 저항으로 {undead_reduction} 피해 감소!")
        
        # 3. 상태이상 저항 (temp_status_resist)
        status_resist = getattr(defender, 'temp_status_resist', 0)
        if status_resist > 0 and random.random() < status_resist:
            # 모든 상태이상을 해제
            status_effects = ['is_poisoned', 'is_burning', 'is_frozen', 'is_stunned']
            cleansed = False
            for effect in status_effects:
                if getattr(defender, effect, False):
                    setattr(defender, effect, False)
                    cleansed = True
            if cleansed:
                print(f"✨ {defender.name}의 상태이상 저항으로 모든 디버프 해제!")
        
        # 4. 디버프 저항 (temp_debuff_resist)
        debuff_resist = getattr(defender, 'temp_debuff_resist', 0)
        if debuff_resist > 0:
            # 새로운 디버프 부여 방지 확률
            if random.random() < debuff_resist:
                # 이번 공격으로 인한 디버프 방지 플래그 설정
                setattr(defender, 'debuff_prevented_this_turn', True)
                print(f"🛡️ {defender.name}의 디버프 저항으로 상태이상 부여 방지!")
        
        return max(1, reduced_damage)  # 최소 1 피해 보장
    
    @staticmethod
    def apply_hp_recovery_trait_effects(character: Character, base_recovery: int) -> int:
        """HP 회복 시 특성 효과 적용"""
        enhanced_recovery = base_recovery
        
        # 1. 치유 강화 (temp_heal_boost)
        heal_boost = getattr(character, 'temp_heal_boost', 0)
        if heal_boost > 0:
            boost_amount = int(base_recovery * heal_boost)
            enhanced_recovery += boost_amount
            print(f"✨ {character.name}의 치유 숙련으로 {boost_amount} 추가 회복!")
        
        # 2. 포션 강화 (temp_potion_boost)
        potion_boost = getattr(character, 'temp_potion_boost', 0)
        if potion_boost > 0:
            potion_bonus = int(base_recovery * potion_boost)
            enhanced_recovery += potion_bonus
            print(f"⚗️ {character.name}의 연금술 지식으로 {potion_bonus} 추가 회복!")
        
        return enhanced_recovery
    
    @staticmethod
    def apply_turn_start_trait_effects(character: Character) -> List[str]:
        """턴 시작 시 특성 효과 적용"""
        messages = []
        
        # 1. MP 재생 강화 (temp_mp_regen_boost)
        mp_regen_boost = getattr(character, 'temp_mp_regen_boost', 0)
        if mp_regen_boost > 0:
            mp_recovery = int(character.max_mp * mp_regen_boost)
            old_mp = character.current_mp
            character.current_mp = min(character.max_mp, character.current_mp + mp_recovery)
            actual_recovery = character.current_mp - old_mp
            if actual_recovery > 0:
                messages.append(f"🔮 {character.name}의 명상으로 {actual_recovery} MP 회복!")
        
        # 2. 자연의 축복 - MP 회복 (nature_blessing)
        if getattr(character, 'temp_nature_mp_regen', 0) > 0:
            nature_mp = int(character.max_mp * 0.1)  # 최대 MP의 10%
            old_mp = character.current_mp
            character.current_mp = min(character.max_mp, character.current_mp + nature_mp)
            actual_recovery = character.current_mp - old_mp
            if actual_recovery > 0:
                messages.append(f"🌿 자연의 축복으로 {character.name}이(가) {actual_recovery} MP 회복!")
        
        # 3. 드루이드 자연 회복 (nature_heal)
        if getattr(character, 'temp_nature_heal', False):
            nature_heal = int(character.max_hp * 0.05)  # 최대 HP의 5%
            healed = character.heal(nature_heal)
            if healed > 0:
                messages.append(f"🌱 자연의 치유로 {character.name}이(가) {healed} HP 회복!")
        
        # 4. 시야 확장 효과 처리 (temp_vision_bonus)
        vision_bonus = getattr(character, 'temp_vision_bonus', 0)
        if vision_bonus > 0:
            # 적의 약점을 더 잘 파악 (다음 공격에 크리티컬 확률 증가)
            current_crit = getattr(character, 'temp_crit_bonus', 0)
            setattr(character, 'temp_crit_bonus', current_crit + 0.1)  # 10% 크리티컬 확률 증가
            messages.append(f"👁️ {character.name}의 시야 확장으로 적의 약점이 보입니다!")
        
        return messages
        
    @staticmethod
    def apply_turn_end_trait_effects(character: Character) -> List[str]:
        """턴 종료 시 특성 효과 적용"""
        messages = []
        
        # 1. 어둠 조작 - 턴 종료 시 적에게 피해 (temp_dark_pulse)
        dark_pulse = getattr(character, 'temp_dark_pulse', 0)
        if dark_pulse > 0 and random.random() < 0.2:  # 20% 확률
            # 현재 전투 중인 적들에게 피해 (전투 시스템에서 적 리스트를 가져와야 함)
            dark_damage = int(character.magic_attack * 0.3)
            messages.append(f"🌑 {character.name}의 어둠 조작으로 적들이 {dark_damage} 암속성 피해!")
            # 실제 적용은 전투 시스템에서 처리
            setattr(character, 'pending_dark_pulse_damage', dark_damage)
        
        # 2. 바드 턴 힐 (turn_heal)
        if getattr(character, 'temp_turn_heal', False):
            # 파티 전체 소량 회복 (전투 시스템에서 파티 리스트를 가져와야 함)
            heal_amount = int(character.magic_attack * 0.1)
            messages.append(f"🎵 {character.name}의 치유의 노래로 파티 전체가 {heal_amount} HP 회복!")
            setattr(character, 'pending_party_heal', heal_amount)
        
        return messages
    
    @staticmethod
    def apply_skill_cost_reduction(character: Character, base_mp_cost: int) -> int:
        """스킬 MP 소모량 특성 효과 적용"""
        reduced_cost = base_mp_cost
        
        # 1. 지혜 (temp_skill_cost_reduction)
        cost_reduction = getattr(character, 'temp_skill_cost_reduction', 0)
        if cost_reduction > 0:
            reduction_amount = int(base_mp_cost * cost_reduction)
            reduced_cost -= reduction_amount
            print(f"🧠 {character.name}의 지혜로 MP 소모량 {reduction_amount} 감소!")
        
        # 2. 마나 효율성 (temp_mana_efficiency)
        mana_efficiency = getattr(character, 'temp_mana_efficiency', 0)
        if mana_efficiency > 0:
            efficiency_reduction = int(base_mp_cost * mana_efficiency)
            reduced_cost -= efficiency_reduction
            print(f"🔮 {character.name}의 마나 순환으로 MP 소모량 {efficiency_reduction} 감소!")
        
        return max(1, reduced_cost)  # 최소 1 MP 소모 보장
    
    @staticmethod
    def check_future_sight_dodge(character: Character) -> bool:
        """미래 예지로 공격 회피 체크"""
        if getattr(character, 'temp_future_sight', False):
            if random.random() < 0.15:  # 15% 확률로 완전 회피
                print(f"🔮 {character.name}의 미래 예지로 공격을 완전히 회피!")
                return True
        return False
    
    @staticmethod 
    def apply_weapon_mastery_effects(character: Character, weapon_type: str, base_damage: int) -> int:
        """무기 숙련도 특성 효과 적용"""
        enhanced_damage = base_damage
        
        # 1. 검 숙련 (temp_weapon_mastery - 검류 무기)
        if getattr(character, 'temp_weapon_mastery', 0) > 0 and weapon_type in ['sword', 'katana', 'greatsword']:
            mastery_bonus = int(base_damage * character.temp_weapon_mastery)
            enhanced_damage += mastery_bonus
            print(f"⚔️ {character.name}의 검술 숙련으로 {mastery_bonus} 추가 피해!")
        
        # 2. 창 숙련 (lance_master - 창류 무기)  
        if getattr(character, 'temp_lance_mastery', 0) > 0 and weapon_type in ['spear', 'lance', 'halberd']:
            lance_bonus = int(base_damage * character.temp_lance_mastery)
            enhanced_damage += lance_bonus
            print(f"🏇 {character.name}의 창술 숙련으로 {lance_bonus} 추가 피해!")
        
        return enhanced_damage
    
    @staticmethod
    def apply_exp_bonus_effects(character: Character, base_exp: int) -> int:
        """경험치 획득 보너스 특성 효과 적용"""
        bonus_exp = base_exp
        
        # 1. 경험치 보너스 (temp_exp_bonus)
        exp_bonus = getattr(character, 'temp_exp_bonus', 0)
        if exp_bonus > 0:
            bonus_amount = int(base_exp * exp_bonus)
            bonus_exp += bonus_amount
            print(f"📚 {character.name}의 학습 능력으로 {bonus_amount} 추가 경험치!")
        
        # 2. 해적 경험치 (pirate_exp)
        pirate_exp = getattr(character, 'temp_pirate_exp_bonus', 0)
        if pirate_exp > 0:
            pirate_bonus = int(base_exp * pirate_exp)
            bonus_exp += pirate_bonus
            print(f"🏴‍☠️ 해적의 모험심으로 {pirate_bonus} 추가 경험치!")
        
        # 3. 깨달음 (enlightenment)
        enlightenment = getattr(character, 'temp_enlightenment_bonus', 0)
        if enlightenment > 0:
            enlightenment_bonus = int(base_exp * enlightenment)
            bonus_exp += enlightenment_bonus
            print(f"💡 철학적 깨달음으로 {enlightenment_bonus} 추가 경험치!")
        
        return bonus_exp


# 전역 연동 인스턴스 생성
trait_integrator = TraitCombatIntegrator()
