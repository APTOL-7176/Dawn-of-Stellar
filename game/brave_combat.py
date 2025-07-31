"""
Brave 시스템이 통합된 전투 시스템
"""

from typing import List, Optional, Tuple
import random
import time
from .character import Character
from .brave_system import BraveManager, BraveAttackType, BattleEffects, BraveSkill
from .ffvii_sound_system import get_ffvii_sound_system
from .combat_visual import CombatVisualizer, EffectType, Color
from .new_skill_system import StatusType, get_status_icon, skill_system
from .ascii_effects import enhanced_battle_effect, combat_animator
from .combat_visual import get_combat_visualizer
from .stable_display import get_stable_display
from .input_utils import KeyboardInput

class StatusEffect:
    """상태이상 효과"""
    def __init__(self, status_type: StatusType, duration: int, intensity: float = 1.0):
        self.status_type = status_type
        self.duration = duration
        self.intensity = intensity


class BraveCombatSystem:
    """Brave 기반 전투 시스템"""
    
    def __init__(self):
        self.brave_manager = BraveManager()
        self.visualizer = get_combat_visualizer()
        self.stable_display = get_stable_display()  # 안정적인 출력 시스템 추가
        self.turn_order = []
        self.keyboard = KeyboardInput()  # 키보드 입력 처리
        self.current_turn = 0
        
        # 스킬 시스템 추가
        self.skill_db = skill_system
        
    def start_battle(self, party: List[Character], enemies: List[Character]):
        """전투 시작"""
        print("\n" + "="*80)
        print("🌟 Dawn Of Stellar - Brave Battle! 🌟")
        print("="*80)
        
        # 모든 참전자의 ATB 게이지 초기화
        all_combatants = party + enemies
        for combatant in all_combatants:
            combatant.atb_gauge = 0
        
        # 파티 멤버들의 특성 효과 적용
        for member in party:
            if hasattr(member, 'apply_trait_effects'):
                member.apply_trait_effects("combat_start")
            if hasattr(member, 'trigger_trait_effects'):
                trait_messages = member.trigger_trait_effects("combat_start")
                for msg in trait_messages:
                    print(f"✨ {member.name}: {msg}")
            
        # 전투 루프
        battle_result = self.battle_loop(party, enemies)
        return battle_result
        
    def battle_loop(self, party: List[Character], enemies: List[Character]) -> bool:
        """전투 루프 - 개선된 ATB 시스템"""
        turn_count = 0
        
        while True:
            turn_count += 1
            
            # ATB 게이지가 100%에 도달할 때까지 점진적 업데이트
            max_attempts = 50  # 무한 루프 방지
            attempts = 0
            
            while attempts < max_attempts:
                self.update_atb_gauges(party + enemies)
                
                # ATB 업데이트 후 전투 종료 체크
                if self.check_battle_end(party, enemies):
                    result = self.determine_winner(party, enemies)
                    print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                    return result
                
                action_order = self.get_action_order(party + enemies)
                if action_order:
                    break
                attempts += 1
                time.sleep(0.05)  # 짧은 대기로 자연스러운 ATB 진행
            
            if not action_order:
                print("⚠️ ATB 시스템 오류 - 턴을 건너뜁니다.")
                continue
            
            print(f"\n--- 턴 {turn_count} ---")
            
            # 선택된 캐릭터의 턴 처리
            character = action_order[0]
            
            if not character.is_alive:
                continue
                
            # 상태이상 처리
            if hasattr(character, 'status_manager'):
                character.status_manager.process_turn_effects()
                
            if character in party:
                result = self.player_turn(character, party, enemies)
                if result is not None:  # 전투 종료 신호
                    print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                    return result
            else:
                result = self.enemy_turn(character, party, enemies)
                if result is not None:  # 전투 종료 신호
                    print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                    return result
                
            # 상태이상 턴 종료 처리
            if hasattr(character, 'status_manager'):
                character.status_manager.process_turn_effects()
                
            # 전투 종료 조건 확인
            if self.check_battle_end(party, enemies):
                result = self.determine_winner(party, enemies)
                print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                return result
            
            # 전투가 계속될 때만 턴 종료 일시정지
            print(f"\n{Color.BRIGHT_BLACK}=== 턴 종료 - 로그를 확인하세요 ==={Color.RESET}")
            input(f"{Color.YELLOW}계속하려면 Enter를 누르세요...{Color.RESET}")
            
            time.sleep(0.1)  # 짧은 간격
                
    def player_turn(self, character: Character, party: List[Character], enemies: List[Character]):
        """플레이어 턴"""
        # 전투 종료 체크 - 턴 시작 시 다시 확인
        if self.check_battle_end(party, enemies):
            return self.determine_winner(party, enemies)
            
        # 턴 시작 시 INT BRV 회복 처리
        if hasattr(character, 'recover_int_brv_on_turn_start'):
            recovered = character.recover_int_brv_on_turn_start()
            if recovered > 0:
                print(f"🔄 {character.name}의 BRV가 INT BRV {recovered:,}로 회복되었습니다!")
            
        combat_animator.show_turn_indicator(character.name)
        self.show_battle_status(character, party, enemies)
        
        while True:
            print("\n행동을 선택하세요:")
            print("1. Brave 공격")
            print("2. HP 공격") 
            print("3. 스킬 사용")
            print("4. 아이템 사용")
            print("5. 방어")
            print("6. 전투 도움말")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == "1":
                if self.brave_attack_menu(character, enemies):
                    break
            elif choice == "2":
                if self.hp_attack_menu(character, enemies):
                    break
            elif choice == "3":
                if self.skill_menu(character, party, enemies):
                    break
            elif choice == "4":
                if self.item_menu(character, party):
                    break
            elif choice == "5":
                self.defend_action(character)
                break
            elif choice == "6":
                from .tutorial import show_combat_help
                show_combat_help()
            else:
                print("잘못된 선택입니다.")
                
        # 턴 종료 후 전투 상태 체크
        if self.check_battle_end(party, enemies):
            return self.determine_winner(party, enemies)
        
        return None  # 전투 계속
                
    def skill_menu(self, character: Character, party: List[Character], enemies: List[Character]) -> bool:
        """스킬 메뉴 - 실제 스킬 시스템"""
        # 캐릭터 클래스 가져오기
        character_class = getattr(character, 'character_class', '전사')
        skills = self.skill_db.get_skills(character_class)
        
        if not skills:
            print(f"{character.name}은(는) 사용할 수 있는 스킬이 없습니다.")
            print("방어를 선택합니다.")
            self.defend_action(character)
            return True
        
        print(f"\n{character.name}의 스킬 (MP: {character.current_mp}/{character.max_mp}):")
        print("─" * 50)
        
        available_skills = []
        for i, skill in enumerate(skills):
            mp_cost = skill.get("mp_cost", 0)
            cast_time = skill.get("cast_time", 0)
            cast_info = f" [캐스트:{cast_time}%]" if cast_time > 0 else ""
            
            if character.current_mp >= mp_cost:
                print(f"{i+1}. {skill.get('name', '스킬')} (MP:{mp_cost}){cast_info} - {skill.get('description', '')}")
                available_skills.append(skill)
            else:
                print(f"{i+1}. {skill.get('name', '스킬')} (MP:{mp_cost}){cast_info} - {skill.get('description', '')} [MP 부족]")
        
        print("0. 취소")
        
        if not available_skills:
            print("사용 가능한 스킬이 없습니다. 방어를 선택합니다.")
            self.defend_action(character)
            return True
        
        try:
            choice_str = self.keyboard.get_key()
            choice = int(choice_str) - 1
            
            if choice == -1:  # 취소
                return False
            elif 0 <= choice < len(skills):
                selected_skill = skills[choice]
                mp_cost = selected_skill.get("mp_cost", 0)
                
                if character.current_mp < mp_cost:
                    print(f"MP가 부족합니다! (필요: {mp_cost}, 보유: {character.current_mp})")
                    return False
                
                # 대상 선택
                targets = self._select_skill_targets(selected_skill, character, party, enemies)
                if targets is None:
                    return False  # 취소된 경우
                
                # 스킬 실행 (간단한 구현)
                # MP 소모
                character.current_mp -= selected_skill.get("mp_cost", 0)
                
                # 간단한 스킬 효과 적용
                print(f"✨ {character.name}이(가) {selected_skill.get('name', '스킬')}을(를) 사용했습니다!")
                
                # 시각 효과
                self.visualizer.show_skill_effect(character, selected_skill.get('name', '스킬'), EffectType.SKILL)
                
                return True
            else:
                print("잘못된 선택입니다.")
                return False
                
        except ValueError:
            print("숫자를 입력하세요.")
            return False
    
    def _select_skill_targets(self, skill, caster, party: List[Character], enemies: List[Character]):
        """스킬 대상 선택"""
        target_type = skill.get("target_type", "single_enemy")
        
        if target_type == "self":
            return [caster]
        elif target_type == "all_allies":
            return [char for char in party if char.is_alive]
        elif target_type == "all_enemies":
            return [enemy for enemy in enemies if enemy.is_alive]
        elif target_type == "single_ally":
            alive_allies = [char for char in party if char.is_alive]
            if not alive_allies:
                return []
            
            print("\n대상을 선택하세요:")
            for i, ally in enumerate(alive_allies, 1):
                status = ""
                if ally.current_hp < ally.max_hp:
                    status += f" (HP: {ally.current_hp}/{ally.max_hp})"
                if hasattr(ally, 'wounds') and ally.wounds > 0:
                    status += f" [상처: {ally.wounds}]"
                print(f"{i}. {ally.name}{status}")
            print("0. 취소")
            
            try:
                choice_str = self.keyboard.get_key()
                choice = int(choice_str) - 1
                if choice == -1:
                    return None
                elif 0 <= choice < len(alive_allies):
                    return [alive_allies[choice]]
                else:
                    print("잘못된 선택입니다.")
                    return None
            except ValueError:
                print("숫자를 입력하세요.")
                return None
                
        elif target_type == "single_enemy":
            alive_enemies = [enemy for enemy in enemies if enemy.is_alive]
            if not alive_enemies:
                return []
            
            print("\n대상을 선택하세요:")
            for i, enemy in enumerate(alive_enemies, 1):
                status = f" (HP: {enemy.current_hp}/{enemy.max_hp}"
                if hasattr(enemy, 'is_broken') and enemy.is_broken:
                    status += ", BREAK"
                status += ")"
                print(f"{i}. {enemy.name}{status}")
            print("0. 취소")
            
            try:
                choice_str = self.keyboard.get_key()
                choice = int(choice_str) - 1
                if choice == -1:
                    return None
                elif 0 <= choice < len(alive_enemies):
                    return [alive_enemies[choice]]
                else:
                    print("잘못된 선택입니다.")
                    return None
            except ValueError:
                print("숫자를 입력하세요.")
                return None
        
        return []
        
    def item_menu(self, character: Character, party: List[Character]) -> bool:
        """아이템 메뉴 - 실제 인벤토리 시스템 연동"""
        from .items import ItemDatabase, ItemType
        
        print(f"\n💼 {character.name}의 아이템:")
        print("="*50)
        
        # 인벤토리 아이템 목록 표시
        available_items = []
        item_db = ItemDatabase()
        
        for item_name, quantity in character.inventory.get_items_list():
            item = item_db.get_item(item_name)
            if item and item.item_type == ItemType.CONSUMABLE:
                available_items.append((item, quantity))
        
        if not available_items:
            print("❌ 사용할 수 있는 소모품이 없습니다.")
            return False
        
        print("사용할 아이템을 선택하세요:")
        print("-" * 50)
        for i, (item, quantity) in enumerate(available_items, 1):
            effect_desc = item.get_effect_description() if hasattr(item, 'get_effect_description') else item.description
            print(f"{i}. {item.name} ({quantity}개)")
            print(f"   📝 {effect_desc}")
            if hasattr(item, 'value') and item.value > 0:
                print(f"   💰 가치: {item.value}골드")
            print()
            
        print(f"{len(available_items)+1}. 취소")
        
        try:
            choice_str = self.keyboard.get_key()
            choice = int(choice_str) - 1
            if 0 <= choice < len(available_items):
                selected_item, quantity = available_items[choice]
                
                # 대상 선택 (회복 아이템인 경우)
                if any(effect in selected_item.effects for effect in ["heal", "field_rest", "full_rest"]):
                    target = self.select_heal_target(party)
                    if target:
                        return self.use_item_on_target(character, selected_item, target)
                elif "revive" in selected_item.effects:
                    # 부활 아이템 - 죽은 캐릭터 선택
                    target = self.select_dead_target(party)
                    if target:
                        return self.use_item_on_target(character, selected_item, target)
                else:
                    # 즉시 사용 아이템 (버프, 강화 등)
                    return self.use_item_on_target(character, selected_item, character)
            elif choice == len(available_items):
                return False
        except ValueError:
            pass
            
        print("잘못된 선택입니다.")
        return False
    
    def select_dead_target(self, party: List[Character]) -> Character:
        """부활 대상 선택"""
        dead_party = [p for p in party if not p.is_alive]
        if not dead_party:
            print("부활시킬 수 있는 캐릭터가 없습니다.")
            return None
            
        print("\n부활시킬 대상을 선택하세요:")
        for i, member in enumerate(dead_party, 1):
            print(f"{i}. {member.name} (사망 상태)")
        
        try:
            choice_str = self.keyboard.get_key()
            choice = int(choice_str) - 1
            if 0 <= choice < len(dead_party):
                return dead_party[choice]
        except ValueError:
            pass
        
        return None
    
    def select_heal_target(self, party: List[Character]) -> Character:
        """치료 대상 선택"""
        alive_party = [p for p in party if p.is_alive]
        if not alive_party:
            return None
            
        print("\n대상을 선택하세요:")
        for i, member in enumerate(alive_party, 1):
            hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
            status = "양호" if hp_ratio > 0.7 else "부상" if hp_ratio > 0.3 else "위험"
            print(f"{i}. {member.name} (HP: {member.current_hp}/{member.max_hp} - {status})")
        
        try:
            choice_str = self.keyboard.get_key()
            choice = int(choice_str) - 1
            if 0 <= choice < len(alive_party):
                return alive_party[choice]
        except ValueError:
            pass
        
        return None
    
    def use_item_on_target(self, user: Character, item, target: Character) -> bool:
        """아이템을 대상에게 사용 - 실제 아이템 효과 시스템 연동"""
        # 아이템 사용 이펙트
        self.visualizer.show_skill_effect(user, f"{item.name} 사용", EffectType.HEAL)
        
        # 실제 아이템 효과 적용
        success = item.use_item(target)
        
        if success:
            # 아이템 소모
            user.inventory.remove_item(item.name, 1)
            print(f"✨ {item.name}을(를) 사용했습니다.")
            
            # 추가 효과들 처리
            for effect in item.effects:
                if effect == "temp_strength":
                    boost = item.stats.get("strength_boost", 10)
                    duration = item.stats.get("duration", 3)
                    # 임시 공격력 증가 (상태 효과 시스템과 연동)
                    if hasattr(target, 'temp_attack_bonus'):
                        target.temp_attack_bonus += boost
                    print(f"💪 {target.name}의 공격력이 {boost} 증가했습니다! ({duration}턴)")
                    
                elif effect == "temp_magic":
                    boost = item.stats.get("magic_boost", 15)
                    duration = item.stats.get("duration", 5)
                    # 임시 마법력 증가
                    if hasattr(target, 'temp_magic_bonus'):
                        target.temp_magic_bonus += boost
                    print(f"🔮 {target.name}의 마법력이 {boost} 증가했습니다! ({duration}턴)")
                    
                elif effect == "temp_haste":
                    boost = item.stats.get("speed_boost", 10)
                    duration = item.stats.get("duration", 4)
                    # 임시 속도 증가
                    if hasattr(target, 'temp_speed_bonus'):
                        target.temp_speed_bonus += boost
                    print(f"⚡ {target.name}의 속도가 {boost} 증가했습니다! ({duration}턴)")
                    
                elif effect == "party_barrier":
                    reduction = item.stats.get("damage_reduction", 50)
                    duration = item.stats.get("duration", 3)
                    # 파티 전체 방어막 (간단 구현)
                    print(f"🛡️ 파티 전체에 방어막이 생성되었습니다! ({reduction}% 피해감소, {duration}턴)")
                    
                elif effect == "berserk":
                    atk_boost = item.stats.get("attack_boost", 25)
                    def_penalty = item.stats.get("defense_penalty", 10)
                    duration = item.stats.get("duration", 3)
                    # 광폭화 효과
                    if hasattr(target, 'temp_attack_bonus'):
                        target.temp_attack_bonus += atk_boost
                    if hasattr(target, 'temp_defense_penalty'):
                        target.temp_defense_penalty += def_penalty
                    print(f"😡 {target.name}이(가) 광폭화 상태가 되었습니다! (공격+{atk_boost}, 방어-{def_penalty}, {duration}턴)")
        else:
            print(f"❌ {item.name}을(를) 사용할 수 없습니다.")
        
        return success
                
    def brave_attack_menu(self, attacker: Character, enemies: List[Character]) -> bool:
        """Brave 공격 메뉴"""
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return False
            
        print("\n대상을 선택하세요:")
        for i, enemy in enumerate(alive_enemies, 1):
            print(f"{i}. {enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp}, Brave: {enemy.brave_points})")
            
        try:
            choice_str = self.keyboard.get_key()
            choice = int(choice_str) - 1
            if 0 <= choice < len(alive_enemies):
                target = alive_enemies[choice]
                self.execute_brave_attack(attacker, target)
                return True
        except ValueError:
            pass
            
        print("잘못된 선택입니다.")
        return False
        
    def hp_attack_menu(self, attacker: Character, enemies: List[Character]) -> bool:
        """HP 공격 메뉴"""
        if attacker.brave_points <= 300:  # 500 → 300으로 감소
            print("Brave 포인트가 부족합니다! (최소 300 필요)")
            return False
            
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return False
            
        print("\n대상을 선택하세요:")
        for i, enemy in enumerate(alive_enemies, 1):
            break_status = " [BREAK]" if (hasattr(enemy, 'is_broken') and enemy.is_broken) else ""
            print(f"{i}. {enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp}){break_status}")
            
        try:
            choice_str = self.keyboard.get_key()
            choice = int(choice_str) - 1
            if 0 <= choice < len(alive_enemies):
                target = alive_enemies[choice]
                self.execute_hp_attack(attacker, target)
                return True
        except ValueError:
            pass
            
        print("잘못된 선택입니다.")
        return False
        
    def execute_brave_attack(self, attacker: Character, target: Character):
        """Brave 공격 실행"""
        # 특성 트리거 효과 발동 (공격 시)
        if hasattr(attacker, 'trigger_trait_effects'):
            trait_messages = attacker.trigger_trait_effects("attack")
            for msg in trait_messages:
                print(f"✨ {attacker.name}: {msg}")
        
        # 기본 Brave 공격 스킬 사용
        brave_skills = [skill for skill in attacker.brave_skills if skill.attack_type == BraveAttackType.BRAVE]
        if brave_skills:
            skill = brave_skills[0]  # 첫 번째 Brave 스킬 사용
        else:
            # 기본 공격
            from .brave_system import BraveSkill
            skill = BraveSkill("기본 공격", BraveAttackType.BRAVE, 1.0)
            
        # 스킬 사용 비주얼 이펙트
        self.visualizer.show_skill_effect(attacker, skill.name, EffectType.SKILL)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("skill", skill_name=skill.name, character_name=attacker.name)
        
        # 데미지 계산
        brave_damage = self.brave_manager.calculate_brave_damage(attacker, target, skill)
        
        # 특성 효과 적용
        if hasattr(attacker, 'get_effective_stats'):
            effective_stats = attacker.get_effective_stats()
            # 공격력 보너스 적용
            total_attack = attacker.get_total_attack() if hasattr(attacker, 'get_total_attack') else attacker.physical_attack
            damage_multiplier = 1.0 + (attacker.temp_attack_bonus / max(1, attacker.physical_attack))
            brave_damage = int(brave_damage * damage_multiplier)
        
        # 크리티컬 체크 (특성 보너스 적용)
        crit_chance = 0.1  # 기본 10%
        if hasattr(attacker, 'temp_crit_bonus'):
            crit_chance += attacker.temp_crit_bonus
        
        # 궁수 첫 공격 크리티컬 특성
        if hasattr(attacker, 'temp_first_strike') and attacker.temp_first_strike:
            if not hasattr(attacker, '_has_attacked_in_battle'):
                attacker._has_attacked_in_battle = True
                crit_chance = 1.0  # 100% 크리티컬
        
        critical = random.random() < crit_chance
        if critical:
            brave_damage = int(brave_damage * 1.5)
            
        # 공격 비주얼 이펙트
        effect_type = EffectType.CRITICAL if critical else EffectType.PHYSICAL_ATTACK
        self.visualizer.show_attack_effect(attacker, target, brave_damage, effect_type, skill.name)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("damage", damage=brave_damage, critical=critical)
        
        # Brave 포인트 적용 (더 많은 획득으로 전투 속도 향상)
        gained_brave = int(brave_damage * 0.8)  # 80% 획득 (50% → 80%)
        attacker.add_brave_points(gained_brave)
        
        # BRV 데미지 적용
        target.brave_points -= brave_damage
        
        # BREAK 체크 - BRV가 0 이하가 되면 BREAK 발생
        if target.brave_points <= 0:
            target.brave_points = 0
            # BREAK 상태 적용
            if hasattr(target, 'apply_break_if_needed'):
                if target.apply_break_if_needed():
                    self.visualizer.show_status_change(target, "BREAK!", False)
                    print(f"💥 {target.name}이(가) BREAK 상태가 되었습니다!")
                    # Break 전용 효과음 재생
                    if hasattr(self, 'sound_system'):
                        self.sound_system.play_sfx("break_sound")
                    enhanced_battle_effect("break")
        
        # Brave 변화 비주얼 이펙트
        self.visualizer.show_brave_change(attacker, gained_brave, attacker.brave_points)
            
        enhanced_battle_effect("brave_gain", amount=gained_brave, total=attacker.brave_points)
        
    def execute_hp_attack(self, attacker: Character, target: Character):
        """HP 공격 실행"""
        # HP 공격 스킬 사용
        hp_skills = [skill for skill in attacker.brave_skills if skill.attack_type == BraveAttackType.HP]
        if hp_skills:
            skill = hp_skills[0]  # 첫 번째 HP 스킬 사용
        else:
            # 기본 HP 공격
            from .brave_system import BraveSkill
            skill = BraveSkill("HP 공격", BraveAttackType.HP, 0.0, 1.0)
            
        # 스킬 사용 비주얼 이펙트
        self.visualizer.show_skill_effect(attacker, skill.name, EffectType.SKILL)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("skill", skill_name=skill.name, character_name=attacker.name)
        
        # 데미지 계산
        hp_damage, wound_damage = self.brave_manager.calculate_hp_damage(attacker, target, skill)
        
        # 특성 효과 적용
        if hasattr(attacker, 'temp_attack_bonus'):
            total_attack = attacker.get_total_attack() if hasattr(attacker, 'get_total_attack') else attacker.physical_attack
            damage_multiplier = 1.0 + (attacker.temp_attack_bonus / max(1, attacker.physical_attack))
            hp_damage = int(hp_damage * damage_multiplier)
            wound_damage = int(wound_damage * damage_multiplier)
        
        # 생명 흡수 특성
        life_steal_amount = 0
        if hasattr(attacker, 'temp_life_steal') and attacker.temp_life_steal > 0:
            life_steal_amount = int(hp_damage * attacker.temp_life_steal)
        
        # Break 상태면 데미지 증가
        if hasattr(target, 'is_broken') and target.is_broken:
            hp_damage = int(hp_damage * 1.5)
            wound_damage = int(wound_damage * 1.5)
            print("Break 상태로 데미지 증가!")
            
        # 공격 비주얼 이펙트
        effect_type = EffectType.CRITICAL if (hasattr(target, 'is_broken') and target.is_broken) else EffectType.PHYSICAL_ATTACK
        self.visualizer.show_attack_effect(attacker, target, hp_damage, effect_type, skill.name)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("damage", damage=hp_damage, critical=(hasattr(target, 'is_broken') and target.is_broken))
        
        # 데미지 적용
        actual_hp_damage = target.take_damage(hp_damage)
        target.add_wounds(wound_damage)
        
        # 생명 흡수 적용
        if life_steal_amount > 0:
            healed = attacker.heal(life_steal_amount)
            if healed > 0:
                print(f"💚 {attacker.name}이(가) {healed} HP 회복 (생명 흡수)")
        
        # 특성 트리거 효과 발동
        if hasattr(attacker, 'trigger_trait_effects'):
            if actual_hp_damage > 0:
                trait_messages = attacker.trigger_trait_effects("kill" if target.current_hp <= 0 else "attack")
                for msg in trait_messages:
                    print(f"✨ {attacker.name}: {msg}")
        
        # 공격자 Brave 소모 (HP 공격 후)
        old_brave = attacker.brave_points
        consumed_brave = attacker.consume_brave_points()
        
        print(f"💫 {attacker.name}의 Brave 포인트: {old_brave:,} → 0 (HP 공격으로 소모)")
        
        # Brave 변화 비주얼 이펙트 표시
        self.visualizer.show_brave_change(attacker, old_brave, attacker.brave_points)
        
        # 대상이 죽었는지 확인
        if target.current_hp <= 0:
            target.is_alive = False
            self.visualizer.show_status_change(target, "KO!", False)
            print(f"💀 {target.name}이(가) 쓰러졌습니다!")
            
    def enemy_turn(self, enemy: Character, party: List[Character], enemies: List[Character]):
        """적 턴 (AI)"""
        # 전투 종료 체크 - 턴 시작 시 다시 확인
        if self.check_battle_end(party, enemies):
            return self.determine_winner(party, enemies)
            
        # 턴 시작 시 INT BRV 회복 처리
        if hasattr(enemy, 'recover_int_brv_on_turn_start'):
            recovered = enemy.recover_int_brv_on_turn_start()
            if recovered > 0:
                print(f"🔄 {enemy.name}의 BRV가 INT BRV {recovered:,}로 회복되었습니다!")
            
        alive_party = [p for p in party if p.is_alive]
        if not alive_party:
            return self.determine_winner(party, enemies)
            
        # 개선된 AI 로직 (더 빠른 전투)
        if enemy.brave_points >= 400 and random.random() < 0.5:  # 1000 → 400, 40% → 50%
            # HP 공격 사용
            target = random.choice(alive_party)
            print(f"\n{enemy.name}이(가) {target.name}에게 HP 공격을 시도합니다!")
            self.execute_hp_attack(enemy, target)
        else:
            # Brave 공격 사용
            target = random.choice(alive_party)
            print(f"\n{enemy.name}이(가) {target.name}에게 Brave 공격을 시도합니다!")
            self.execute_brave_attack(enemy, target)
            
        # 턴 종료 후 전투 상태 체크
        if self.check_battle_end(party, enemies):
            return self.determine_winner(party, enemies)
        
        return None  # 전투 계속
            
    def defend_action(self, character: Character):
        """방어 행동 - 비주얼 이펙트 포함"""
        # 방어 애니메이션 (매개변수 순서 수정)
        self.visualizer.show_attack_effect(character, character, 0, EffectType.DEFEND, "방어")
        
        print(f"{character.name}이(가) 방어 태세를 취합니다!")
        # 방어 효과: 다음 받는 데미지 50% 감소
        defense_effect = StatusEffect(StatusType.BOOST_DEF, 1, 2)
        character.status_manager.add_effect(defense_effect)
        
        # Brave 포인트 더 많이 회복 (빠른 전투를 위해)
        old_brave = character.brave_points
        character.add_brave_points(300)  # 200 → 300으로 증가
        
        # 방어 상태 변화 표시
        self.visualizer.show_status_change(character, "방어 태세")
        self.visualizer.show_brave_change(character, old_brave, character.brave_points)
        
    def show_battle_status(self, current_char: Character, party: List[Character], enemies: List[Character]):
        """전투 상황 표시 - 안정적인 비주얼"""
        # 안정적인 전투 화면 사용
        self.stable_display.show_combat_simple(party, enemies, current_char)
        
        # 현재 캐릭터의 상태를 별도로 강조 표시
        if current_char:
            print(f"\n🎯 현재 턴: {Color.BRIGHT_YELLOW}{current_char.name}{Color.RESET}")
            if hasattr(current_char, 'is_broken') and current_char.is_broken:
                print(f"   ⚠️ {Color.BRIGHT_RED}BREAK 상태!{Color.RESET}")
            print(f"   턴 준비 완료!")
            
    def update_atb_gauges(self, all_combatants: List[Character]):
        """ATB 게이지 업데이트 - 속도 기반 차등 업데이트"""
        for combatant in all_combatants:
            if combatant.is_alive:
                # 속도에 따른 ATB 증가량 계산 (속도가 빠를수록 더 빠르게 충전)
                speed = getattr(combatant, 'speed', 50)
                atb_increment = (speed / 50.0) * 8  # 기준 속도 50에서 8씩 증가
                
                # ATB 게이지 업데이트 (최대 100까지)
                combatant.atb_gauge = min(100, combatant.atb_gauge + atb_increment)
                
                # atb_speed 속성이 없으면 speed 기반으로 설정
                if not hasattr(combatant, 'atb_speed'):
                    combatant.atb_speed = speed
                    
    def show_atb_status(self, all_combatants: List[Character]):
        """현재 ATB 상태 표시"""
        print(f"\n{Color.CYAN}⏱️ ATB 상태:{Color.RESET}")
        
        # ATB 순서대로 정렬
        sorted_combatants = sorted(
            [c for c in all_combatants if c.is_alive], 
            key=lambda x: x.atb_gauge, 
            reverse=True
        )
        
        for i, combatant in enumerate(sorted_combatants[:5]):  # 상위 5명만 표시
            is_enemy = hasattr(combatant, 'is_enemy')
            name_color = Color.BRIGHT_RED if is_enemy else Color.BRIGHT_BLUE
            
            atb_gauge = int(combatant.atb_gauge)
            if atb_gauge >= 100:
                bar = f"{Color.BRIGHT_CYAN}{'█'*10}{Color.RESET}"
                status = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
            else:
                filled = atb_gauge // 10
                bar = f"{Color.CYAN}{'█'*filled}{Color.BRIGHT_BLACK}{'░'*(10-filled)}{Color.RESET}"
                status = f"{Color.CYAN}{atb_gauge:3}%{Color.RESET}"
            
            rank = f"{i+1}."
            print(f"  {rank:3} {name_color}{combatant.name:12}{Color.RESET} [{bar}]   {status}")
        
        print()
                
    def get_action_order(self, all_combatants: List[Character]) -> List[Character]:
        """행동 순서 결정 - 우선순위 기반 단일 선택"""
        ready_combatants = [c for c in all_combatants if c.is_alive and c.atb_gauge >= 100]
        
        if not ready_combatants:
            return []
        
        # ATB가 100% 이상인 캐릭터 중 우선순위 결정
        # 1. ATB 게이지가 더 높은 캐릭터
        # 2. 속도가 더 빠른 캐릭터
        # 3. 무작위 (동점인 경우)
        def priority_key(combatant):
            return (combatant.atb_gauge, getattr(combatant, 'speed', 50), random.random())
        
        # 가장 높은 우선순위 캐릭터 선택
        fastest = max(ready_combatants, key=priority_key)
        fastest.atb_gauge = 0  # 선택된 캐릭터만 ATB 초기화
        
        return [fastest]
        
    def check_battle_end(self, party: List[Character], enemies: List[Character]) -> bool:
        """전투 종료 조건 확인"""
        party_alive = any(p.is_alive for p in party)
        enemies_alive = any(e.is_alive for e in enemies)
        
        return not party_alive or not enemies_alive
        
    def determine_winner(self, party: List[Character], enemies: List[Character]) -> bool:
        """승부 결정 - 비주얼 이펙트 포함"""
        party_alive = any(p.is_alive for p in party)
        
        if party_alive:
            # 승리 이펙트
            print(f"\n{Color.BRIGHT_GREEN}{'='*50}")
            print(f"🎉 승리! 🎉")
            print(f"{'='*50}{Color.RESET}")
        else:
            # 패배 이펙트  
            print(f"\n{Color.BRIGHT_RED}{'='*50}")
            print(f"💀 패배... 💀")
            print(f"{'='*50}{Color.RESET}")
            
        return party_alive
