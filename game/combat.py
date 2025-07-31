"""
ATB 전투 시스템 (Brave 시스템 통합)
"""

from typing import List, Optional, Tuple, Dict, Any
import random
import time
from .character import Character
from .brave_combat import BraveCombatSystem


class ItemEffectProcessor:
    """아이템 효과 처리 클래스"""
    
    @staticmethod
    def apply_weapon_effects(attacker: Character, target: Character, weapon_effects: List[str], damage: int) -> Dict[str, Any]:
        """무기 효과 적용"""
        effects_applied = {}
        bonus_damage = 0
        
        for effect in weapon_effects:
            if effect.startswith("life_steal"):
                # 생명 흡수
                steal_amount = int(effect.split("_")[-1])
                heal_amount = damage * steal_amount // 100
                attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal_amount)
                effects_applied["life_steal"] = heal_amount
                
            elif effect.startswith("burn_chance"):
                # 화상 효과
                chance = int(effect.split("_")[-1])
                if random.randint(1, 100) <= chance:
                    # 화상 상태이상 적용 (3턴간 매턴 5 피해)
                    effects_applied["burn"] = True
                    
            elif effect.startswith("crit_chance"):
                # 크리티컬 확률 증가
                chance = int(effect.split("_")[-1])
                if random.randint(1, 100) <= chance:
                    bonus_damage = damage // 2  # 50% 추가 피해
                    effects_applied["critical"] = True
                    
            elif effect == "demon_slayer":
                # 악마 특효 (임시로 모든 적에게 20% 추가 피해)
                bonus_damage = damage * 20 // 100
                effects_applied["demon_slayer"] = True
                
            elif effect.startswith("atb_drain"):
                # ATB 드레인 (상대방 행동력 감소)
                effects_applied["atb_drain"] = True
                
            elif effect == "ignore_all_defense":
                # 모든 방어력 무시
                effects_applied["ignore_defense"] = True
                
            elif effect.startswith("chain_lightning"):
                # 연쇄 번개 (추가 광역 피해)
                effects_applied["chain_lightning"] = damage // 3
                
        return effects_applied, bonus_damage
    
    @staticmethod
    def apply_armor_effects(defender: Character, armor_effects: List[str], incoming_damage: int) -> Dict[str, Any]:
        """방어구 효과 적용"""
        effects_applied = {}
        damage_reduction = 0
        
        for effect in armor_effects:
            if effect.startswith("block_chance"):
                # 블록 확률
                chance = int(effect.split("_")[-1])
                if random.randint(1, 100) <= chance:
                    damage_reduction = incoming_damage // 2  # 50% 피해 감소
                    effects_applied["block"] = True
                    
            elif effect.startswith("spell_reflect"):
                # 마법 반사
                chance = int(effect.split("_")[-1])
                if random.randint(1, 100) <= chance:
                    effects_applied["spell_reflect"] = incoming_damage // 2
                    
            elif effect == "fire_immunity":
                # 화염 면역
                effects_applied["fire_immunity"] = True
                
            elif effect.startswith("dodge_chance"):
                # 회피 확률
                chance = int(effect.split("_")[-1])
                if random.randint(1, 100) <= chance:
                    damage_reduction = incoming_damage  # 완전 회피
                    effects_applied["dodge"] = True
                    
        return effects_applied, damage_reduction
    
    @staticmethod
    def apply_accessory_effects(character: Character, accessory_effects: List[str]) -> Dict[str, Any]:
        """장신구 효과 적용 (지속 효과)"""
        effects_applied = {}
        
        for effect in accessory_effects:
            if effect.startswith("life_steal"):
                # 생명 흡수
                amount = int(effect.split("_")[-1])
                effects_applied["life_steal"] = amount
                
            elif effect == "hp_regen":
                # 체력 재생
                regen_amount = character.max_hp // 20  # 최대 체력의 5%
                character.current_hp = min(character.max_hp, character.current_hp + regen_amount)
                effects_applied["hp_regen"] = regen_amount
                
            elif effect == "mana_efficiency":
                # 마나 효율 (스킬 MP 소모량 감소)
                effects_applied["mana_efficiency"] = True
                
            elif effect == "exp_boost_25":
                # 경험치 25% 추가
                effects_applied["exp_boost"] = 25
                
        return effects_applied


class CombatAction:
    """전투 액션 클래스"""
    
    def __init__(self, actor: Character, action_type: str, target: Optional[Character] = None, 
                 skill_name: str = "일반 공격", modifier: float = 1.0):
        self.actor = actor
        self.action_type = action_type  # "attack", "defend", "skill", "item", "brave", "hp_attack"
        self.target = target
        self.skill_name = skill_name
        self.modifier = modifier
        self.damage_type = "physical"  # "physical" 또는 "magic"


class CombatManager:
    """ATB 전투 관리자 (Brave 시스템 포함)"""
    
    def __init__(self):
        self.party_members: List[Character] = []
        self.enemies: List[Character] = []
        self.combat_active = False
        self.brave_combat = BraveCombatSystem()  # Brave 전투 시스템
        self.turn_queue: List[Character] = []
        self.combat_log: List[str] = []
        
    def start_combat(self, party: List[Character], enemies: List[Character]):
        """전투 시작 (Brave 시스템 사용)"""
        self.party_members = party
        self.enemies = enemies
        self.combat_active = True
        self.combat_log = []
        
        # 요리 효과를 전투 전에 적용
        self._apply_cooking_effects_to_party()
        
        # Brave 전투 시스템으로 전투 실행
        result = self.brave_combat.start_battle(party, enemies)
        
        # 전투 후 요리 효과 정리
        self._cleanup_cooking_effects_from_party()
        
        self.combat_active = False
        return result
    
    def _apply_cooking_effects_to_party(self):
        """전투 시작 전 파티에 요리 효과 적용"""
        try:
            from game.field_cooking import get_cooking_effects_for_party
            cooking_effects = get_cooking_effects_for_party()
            
            if not cooking_effects:
                return
            
            print(f"\n🍳 요리 효과가 전투에 적용됩니다!")
            
            for member in self.party_members:
                if not member.is_alive:
                    continue
                
                # 임시 스탯 보너스 저장
                if not hasattr(member, '_cooking_bonuses'):
                    member._cooking_bonuses = {}
                
                # 스탯 증가
                if "attack" in cooking_effects:
                    bonus = cooking_effects["attack"]
                    member.physical_attack += bonus
                    member._cooking_bonuses["attack"] = bonus
                    print(f"  {member.name} 공격력 +{bonus}")
                
                if "defense" in cooking_effects:
                    bonus = cooking_effects["defense"]
                    member.physical_defense += bonus
                    member._cooking_bonuses["defense"] = bonus
                    print(f"  {member.name} 방어력 +{bonus}")
                
                if "speed" in cooking_effects:
                    bonus = cooking_effects["speed"]
                    member.agility += bonus
                    member._cooking_bonuses["speed"] = bonus
                    print(f"  {member.name} 속도 +{bonus}")
                
                if "magic_defense" in cooking_effects:
                    bonus = cooking_effects["magic_defense"]
                    member.magic_defense += bonus
                    member._cooking_bonuses["magic_defense"] = bonus
                    print(f"  {member.name} 마법 방어력 +{bonus}")
                
                if "all_stats" in cooking_effects:
                    bonus = cooking_effects["all_stats"]
                    member.physical_attack += bonus
                    member.physical_defense += bonus
                    member.agility += bonus
                    member.magic_defense += bonus
                    member._cooking_bonuses["all_stats"] = bonus
                    print(f"  {member.name} 모든 능력치 +{bonus}")
                
                if "evasion" in cooking_effects:
                    bonus = cooking_effects["evasion"]
                    member.luck += bonus  # 운을 회피율로 활용
                    member._cooking_bonuses["evasion"] = bonus
                    print(f"  {member.name} 회피율 +{bonus}")
                
                if "critical_rate" in cooking_effects:
                    bonus = cooking_effects["critical_rate"]
                    if not hasattr(member, '_temp_crit_bonus'):
                        member._temp_crit_bonus = 0
                    member._temp_crit_bonus += bonus
                    member._cooking_bonuses["critical_rate"] = bonus
                    print(f"  {member.name} 치명타율 +{bonus}%")
        
        except ImportError:
            pass  # 요리 시스템이 없을 경우 무시
    
    def _cleanup_cooking_effects_from_party(self):
        """전투 후 파티에서 요리 효과 제거"""
        for member in self.party_members:
            if hasattr(member, '_cooking_bonuses'):
                bonuses = member._cooking_bonuses
                
                # 스탯 복원
                if "attack" in bonuses:
                    member.physical_attack -= bonuses["attack"]
                if "defense" in bonuses:
                    member.physical_defense -= bonuses["defense"]
                if "speed" in bonuses:
                    member.agility -= bonuses["speed"]
                if "magic_defense" in bonuses:
                    member.magic_defense -= bonuses["magic_defense"]
                if "all_stats" in bonuses:
                    bonus = bonuses["all_stats"]
                    member.physical_attack -= bonus
                    member.physical_defense -= bonus
                    member.agility -= bonus
                    member.magic_defense -= bonus
                if "evasion" in bonuses:
                    member.luck -= bonuses["evasion"]
                if "critical_rate" in bonuses:
                    if hasattr(member, '_temp_crit_bonus'):
                        member._temp_crit_bonus -= bonuses["critical_rate"]
                
                # 임시 보너스 정리
                del member._cooking_bonuses
        
        # 전투 루프 시작
        self.combat_loop()
        
    def combat_loop(self):
        """메인 전투 루프"""
        while self.combat_active:
            # ATB 게이지 업데이트
            self.update_atb_gauges()
            
            # 행동 준비된 캐릭터 처리
            ready_characters = self.get_ready_characters()
            
            for character in ready_characters:
                if not self.combat_active:
                    break
                    
                self.process_character_turn(character)
                
            # 전투 종료 조건 체크
            if self.check_combat_end():
                break
                
            # 짧은 대기 (ATB 시뮬레이션)
            time.sleep(0.1)
            
    def update_atb_gauges(self):
        """모든 캐릭터의 ATB 게이지 업데이트"""
        all_combatants = self.party_members + self.enemies
        for combatant in all_combatants:
            combatant.update_atb()
            
    def get_ready_characters(self) -> List[Character]:
        """행동 준비된 캐릭터들 반환 (파티 우선)"""
        ready_party = [char for char in self.party_members if char.can_act()]
        ready_enemies = [char for char in self.enemies if char.can_act()]
        
        # 파티 멤버를 먼저 처리하여 플레이어가 우선권을 가지도록
        return ready_party + ready_enemies
        
    def process_character_turn(self, character: Character):
        """캐릭터 턴 처리"""
        if not character.is_alive:
            return
            
        # 상태이상 처리
        status_messages = character.process_status_effects()
        for message in status_messages:
            self.log(message)
            
        # 상태이상으로 인해 행동 불가능하면 턴 종료
        if not character.status_manager.can_act():
            character.reset_atb()
            return
            
        print(f"\n{'='*60}")
        print(f"{character.name}의 턴!")
        
        if character in self.party_members:
            # 플레이어 캐릭터 턴
            action = self.get_player_action(character)
        else:
            # 적 AI 턴
            action = self.get_enemy_action(character)
            
        self.execute_action(action)
        character.reset_atb()
        
        # 전투 상태 표시
        self.show_combat_status()
        
    def get_player_action(self, character: Character) -> CombatAction:
        """플레이어 액션 입력"""
        while True:
            print(f"\n{character.name}의 행동을 선택하세요:")
            print("1. 공격")
            print("2. 방어")
            print("3. 스킬")
            print("4. 아이템")
            
            choice = input("선택 (1-4): ").strip()
            
            if choice == "1":
                target = self.select_target(self.enemies, "공격할 대상을 선택하세요:")
                if target:
                    return CombatAction(character, "attack", target)
                    
            elif choice == "2":
                return CombatAction(character, "defend")
                
            elif choice == "3":
                skill_action = self.select_skill(character)
                if skill_action:
                    return skill_action
                    
            elif choice == "4":
                print("아이템 시스템은 아직 구현되지 않았습니다.")
                
            else:
                print("잘못된 선택입니다.")
                
    def get_enemy_action(self, enemy: Character) -> CombatAction:
        """개선된 적 AI 액션 결정 (새로운 스킬 시스템 연동)"""
        alive_party = [char for char in self.party_members if char.is_alive]
        
        if not alive_party:
            return CombatAction(enemy, "defend")
        
        # AI 전략 결정
        enemy_hp_ratio = enemy.current_hp / enemy.limited_max_hp
        
        # 체력이 낮으면 회복 시도 (20% 이하일 때)
        if enemy_hp_ratio < 0.2 and random.random() < 0.3:
            return CombatAction(enemy, "heal", enemy, "자가치료", 0.3)
        
        # 타겟 선택 전략
        target = self._select_enemy_target(alive_party)
        
        # 적 스킬 사용 확률 (레벨과 체력에 따라 조정)
        skill_chance = 0.15 + (enemy.level * 0.05) + (1 - enemy_hp_ratio) * 0.25
        
        if random.random() < skill_chance:
            return self._select_enemy_skill_from_system(enemy, target)
        else:
            return CombatAction(enemy, "attack", target)
    
    def _select_enemy_skill_from_system(self, enemy: Character, target: Character) -> CombatAction:
        """적이 새로운 스킬 시스템에서 스킬 선택"""
        from .new_skill_system import NewSkillSystem, SkillType
        
        skill_system = NewSkillSystem()
        
        # 적의 클래스가 없으면 기본 스킬 사용
        if not hasattr(enemy, 'character_class') or not enemy.character_class:
            return self._select_generic_enemy_skill(enemy, target)
        
        # 적의 클래스별 스킬 가져오기
        enemy_skills = skill_system.get_skills_by_class(enemy.character_class)
        
        if not enemy_skills:
            return self._select_generic_enemy_skill(enemy, target)
        
        # MP가 있는 스킬만 필터링
        usable_skills = [skill for skill in enemy_skills 
                        if skill.get("mp_cost", 0) <= enemy.current_mp]
        
        if not usable_skills:
            return CombatAction(enemy, "attack", target)
        
        # 전투 상황에 맞는 스킬 선택
        preferred_skills = []
        
        for skill in usable_skills:
            skill_type = skill.get("type")
            target_type = skill.get("target")
            
            # 공격 스킬 우선
            if skill_type in [SkillType.BRV_ATTACK, SkillType.HP_ATTACK, SkillType.BRV_HP_ATTACK]:
                preferred_skills.append(skill)
            
            # 체력이 낮으면 치유 스킬 선호
            elif skill_type == SkillType.HEAL and enemy.current_hp < enemy.limited_max_hp * 0.5:
                preferred_skills.append(skill)
                preferred_skills.append(skill)  # 가중치 증가
            
            # 아군이 많으면 전체공격 선호
            elif target_type and "적전체" in str(target_type):
                alive_party = [char for char in self.party_members if char.is_alive]
                if len(alive_party) >= 3:
                    preferred_skills.append(skill)
                    preferred_skills.append(skill)  # 가중치 증가
        
        # 선호 스킬이 없으면 아무 스킬이나
        if not preferred_skills:
            preferred_skills = usable_skills
        
        # 랜덤 선택
        selected_skill = random.choice(preferred_skills)
        
        # MP 소모
        mp_cost = selected_skill.get("mp_cost", 0)
        enemy.use_mp(mp_cost)
        
        # 액션 생성
        action = CombatAction(enemy, "skill", target, selected_skill["name"])
        action.skill_data = selected_skill
        
        return action
    
    def _select_generic_enemy_skill(self, enemy: Character, target: Character) -> CombatAction:
        """일반적인 적 스킬 (클래스가 없는 적용)"""
        possible_skills = [
            {"name": "강공격", "type": "strong_attack", "modifier": 1.4, "mp_cost": 5},
            {"name": "독공격", "type": "poison_attack", "modifier": 0.9, "mp_cost": 8},
            {"name": "화염공격", "type": "burn_attack", "modifier": 1.1, "mp_cost": 10},
            {"name": "전체공격", "type": "area_attack", "modifier": 0.7, "mp_cost": 15}
        ]
        
        # MP로 사용 가능한 스킬 필터링
        usable_skills = [skill for skill in possible_skills 
                        if skill["mp_cost"] <= enemy.current_mp]
        
        if not usable_skills:
            return CombatAction(enemy, "attack", target)
        
        selected_skill = random.choice(usable_skills)
        enemy.use_mp(selected_skill["mp_cost"])
        
        if selected_skill["type"] == "area_attack":
            action = CombatAction(enemy, "area_attack", None, selected_skill["name"], selected_skill["modifier"])
        else:
            action = CombatAction(enemy, "skill", target, selected_skill["name"], selected_skill["modifier"])
            
        action.skill_type = selected_skill["type"]
        return action
    
    def _select_enemy_target(self, alive_party: List[Character]) -> Character:
        """적의 타겟 선택 전략"""
        # 가중치 기반 타겟 선택
        weights = []
        for member in alive_party:
            weight = 1.0
            
            # 체력이 낮은 적 우선
            hp_ratio = member.current_hp / member.limited_max_hp
            weight += (1 - hp_ratio) * 2
            
            # 힐러나 마법사 우선
            if member.character_class in ["치료사", "대마법사", "정령술사"]:
                weight += 1.5
                
            # 방어력이 낮은 적 우선
            effective_stats = member.get_effective_stats()
            avg_defense = (effective_stats["physical_defense"] + effective_stats["magic_defense"]) / 2
            weight += max(0, (20 - avg_defense) * 0.1)
            
            weights.append(weight)
        
        return random.choices(alive_party, weights=weights)[0]
    
    def _select_enemy_skill(self, enemy: Character, target: Character, alive_party: List[Character]) -> CombatAction:
        """적의 스킬 선택"""
        possible_skills = [
            {"name": "독공격", "type": "poison_attack", "modifier": 0.8, "chance": 0.3},
            {"name": "화염공격", "type": "burn_attack", "modifier": 1.2, "chance": 0.25},
            {"name": "빙결공격", "type": "freeze_attack", "modifier": 0.9, "chance": 0.2},
            {"name": "강공격", "type": "strong_attack", "modifier": 1.5, "chance": 0.4},
            {"name": "전체공격", "type": "area_attack", "modifier": 0.7, "chance": 0.15}
        ]
        
        # 스킬 중 하나를 확률적으로 선택
        available_skills = [skill for skill in possible_skills if random.random() < skill["chance"]]
        
        if not available_skills:
            return CombatAction(enemy, "attack", target)
        
        selected_skill = random.choice(available_skills)
        
        if selected_skill["type"] == "area_attack":
            action = CombatAction(enemy, "area_attack", None, selected_skill["name"], selected_skill["modifier"])
        else:
            action = CombatAction(enemy, "skill", target, selected_skill["name"], selected_skill["modifier"])
            
        action.skill_type = selected_skill["type"]
        return action
            
    def select_target(self, candidates: List[Character], prompt: str) -> Optional[Character]:
        """대상 선택"""
        alive_candidates = [char for char in candidates if char.is_alive]
        
        if not alive_candidates:
            print("선택 가능한 대상이 없습니다.")
            return None
            
        print(f"\n{prompt}")
        for i, candidate in enumerate(alive_candidates, 1):
            print(f"{i}. {candidate.name} (HP: {candidate.current_hp}/{candidate.limited_max_hp})")
            
        while True:
            try:
                choice = int(input("선택: ")) - 1
                if 0 <= choice < len(alive_candidates):
                    return alive_candidates[choice]
                else:
                    print("잘못된 선택입니다.")
            except ValueError:
                print("숫자를 입력하세요.")
                
    def select_skill(self, character: Character) -> Optional[CombatAction]:
        """스킬 선택 (새로운 스킬 시스템 연동)"""
        from .new_skill_system import NewSkillSystem
        
        skill_system = NewSkillSystem()
        character_skills = skill_system.get_skills_by_class(character.character_class)
        
        if not character_skills:
            print(f"{character.character_class}의 스킬이 없습니다.")
            return None
        
        print(f"\n{character.name}의 MP: {character.current_mp}/{character.max_mp}")
        print("사용 가능한 스킬:")
        
        available_skills = []
        for i, skill in enumerate(character_skills, 1):
            mp_cost = skill.get("mp_cost", 0)
            status = "" if character.current_mp >= mp_cost else " [MP 부족]"
            print(f"{i}. {skill['name']} - {skill.get('description', '')} (MP: {mp_cost}){status}")
            available_skills.append(skill)
        
        print("0. 취소")
        
        while True:
            try:
                choice = int(input("스킬 선택: "))
                if choice == 0:
                    return None
                elif 1 <= choice <= len(available_skills):
                    skill = available_skills[choice - 1]
                    mp_cost = skill.get("mp_cost", 0)
                    
                    # MP 확인
                    if character.current_mp < mp_cost:
                        print(f"MP가 부족합니다! (필요: {mp_cost}, 보유: {character.current_mp})")
                        continue
                    
                    # MP 소모
                    character.use_mp(mp_cost)
                    
                    # 스킬 액션 생성
                    return self.create_skill_action(character, skill)
                        
                else:
                    print("잘못된 선택입니다.")
            except ValueError:
                print("숫자를 입력하세요.")
    
    def create_skill_action(self, character: Character, skill: dict) -> Optional[CombatAction]:
        """스킬 데이터로부터 전투 액션 생성"""
        from .new_skill_system import SkillType, TargetType, DamageType
        
        skill_type = skill.get("type")
        target_type = skill.get("target")
        
        # 타겟 선택
        target = None
        if target_type == TargetType.SINGLE_ENEMY:
            target = self.select_target(self.enemies, "공격할 대상을 선택하세요:")
        elif target_type == TargetType.SINGLE_ALLY:
            target = self.select_target(self.party_members, "대상을 선택하세요:")
        elif target_type == TargetType.SELF:
            target = character
        elif target_type == TargetType.DEAD_ALLY:
            dead_allies = [char for char in self.party_members if not char.is_alive]
            if dead_allies:
                target = self.select_target(dead_allies, "부활시킬 대상을 선택하세요:")
            else:
                print("부활시킬 대상이 없습니다.")
                return None
        
        # 액션 생성
        action = CombatAction(character, "skill", target, skill["name"])
        action.skill_data = skill
        
        # SFX 재생
        self.play_skill_sfx(skill)
        
        return action
                
    def play_skill_sfx(self, skill: dict):
        """스킬 SFX 재생 (FFVII 효과음 사용)"""
        try:
            from .audio import get_unified_audio_system
            
            audio_system = get_unified_audio_system()
            skill_name = skill.get("name", "")
            element = skill.get("element")
            skill_type = skill.get("type")
            
            # 스킬별 FFVII SFX 매핑
            ffvii_sfx_map = {
                # 물리 공격 스킬
                "연속베기": "sword_hit",        # 17 - Cloud's Sword Hit
                "분노 축적": "sword_hit",        # 17 - Cloud's Sword Hit
                "광전사의 각성": "critical_hit",  # 26 - Cloud Critical Sword Hit
                "콜로세움의 왕": "critical_hit",  # 26 - Cloud Critical Sword Hit
                "버서커의 최후": "critical_hit",  # 26 - Cloud Critical Sword Hit
                
                # 마법 스킬 (원소별)
                "파이어볼": "fire",             # 8 - Fire Spell
                "파이어": "fire",               # 8 - Fire Spell
                "파이어가": "fire",             # 141 - Fire 3
                "라이트닝 볼트": "thunder",      # 10 - Bolt Spell
                "썬더": "thunder",              # 10 - Bolt Spell
                "썬더가": "thunder",            # 69 - Bolt 3
                "메테오": "ice",                # 75 - Comet Spell (메테오와 비슷)
                "아이스 스피어": "ice",          # 23 - Ice Spell
                "블리자드": "ice",              # 23 - Ice Spell
                "블리자가": "ice",              # 28 - Ice 3
                "화염 정령": "fire",            # 8 - Fire Spell
                "사대 정령 소환": "summon",      # 190 - Materia Glowing
                
                # 치유 스킬
                "치유술": "heal",               # 5 - Cure Spell / Potion
                "신성한 치유": "heal",          # 68 - Cure 3 / Elixir
                "물 정령의 치유": "heal",       # 5 - Cure Spell / Potion
                "대치유술": "heal",             # 68 - Cure 3 / Elixir
                "케어루": "heal",               # 68 - Cure 3 / Elixir
                
                # 특수 스킬
                "시간 정지": "menu_cancel",     # 86 - Stop Spell
                "그림자 숨기": "teleport",      # 54 - Jumping (텔레포트로 대체)
                "독 바르기": "poison",          # 62 - Bio Spell
                "오의 무상베기": "critical_hit", # 26 - Cloud Critical Sword Hit
                "절대 진리": "magic_cast",      # 12 - Preparing to Cast Magic
                
                # 상태 효과 스킬
                "헤이스트": "haste",            # 82 - Haste Spell
                "슬로우": "slow",               # 64 - Slow Spell
                "프로텍트": "protect",          # 93 - Protect Spell
                "셸": "barrier",                # 66 - Shell Spell
                "사일런스": "silence",          # 83 - Silence Spell
                "스톱": "menu_cancel",          # 86 - Stop Spell
            }
            
            # 원소별 기본 SFX
            element_sfx_map = {
                "화염": "fire",      # 8 - Fire Spell
                "냉기": "ice",       # 23 - Ice Spell  
                "번개": "thunder",   # 10 - Bolt Spell
                "대지": "magic_cast", # 12 - Preparing to Cast Magic
                "바람": "magic_cast", # 12 - Preparing to Cast Magic
                "물": "heal",        # 5 - Cure Spell / Potion
                "빛": "heal",        # 5 - Cure Spell / Potion
                "어둠": "poison",    # 62 - Bio Spell
                "독": "poison"       # 62 - Bio Spell
            }
            
            # 스킬 이름으로 우선 검색
            sfx_name = ffvii_sfx_map.get(skill_name)
            
            # 없으면 원소로 검색
            if not sfx_name and element:
                element_name = element.value if hasattr(element, 'value') else str(element)
                sfx_name = element_sfx_map.get(element_name)
            
            # 그래도 없으면 타입별 기본 SFX
            if not sfx_name:
                if "ATTACK" in str(skill_type):
                    sfx_name = "sword_hit"      # 17 - Cloud's Sword Hit
                elif "HEAL" in str(skill_type):
                    sfx_name = "heal"           # 5 - Cure Spell / Potion
                elif "BUFF" in str(skill_type):
                    sfx_name = "menu_confirm"   # 93 - Protect Spell
                elif "DEBUFF" in str(skill_type):
                    sfx_name = "poison"         # 62 - Bio Spell
                else:
                    sfx_name = "magic_cast"     # 12 - Preparing to Cast Magic
            
            # FFVII 효과음 재생
            audio_system.play_sfx(sfx_name)
            
        except Exception as e:
            # SFX 재생 실패해도 게임은 계속
            pass
                
    def execute_action(self, action: CombatAction):
        """액션 실행 (새로운 스킬 시스템 연동)"""
        actor = action.actor
        
        if action.action_type == "attack":
            self.execute_attack(actor, action.target, action.modifier)
            
        elif action.action_type == "defend":
            self.execute_defend(actor)
            
        elif action.action_type == "skill":
            self.execute_new_skill(actor, action)
            
        elif action.action_type == "heal":
            self.execute_heal(actor, action.target, action.modifier)
            
        elif action.action_type == "area_attack":
            damage_type = getattr(action, 'damage_type', 'physical')
            self.execute_area_attack(actor, action.modifier, action.skill_name, damage_type)
    
    def execute_new_skill(self, actor: Character, action: CombatAction):
        """새로운 스킬 시스템 스킬 실행"""
        from .new_skill_system import SkillType, TargetType, DamageType, PenetrationType
        
        skill = action.skill_data
        skill_name = skill["name"]
        skill_type = skill.get("type")
        target_type = skill.get("target")
        
        self.log(f"{actor.name}이(가) {skill_name}을(를) 사용했습니다!")
        
        # 스킬 타입별 실행
        if skill_type == SkillType.BRV_ATTACK:
            self.execute_brv_attack(actor, action.target, skill)
        elif skill_type == SkillType.HP_ATTACK:
            self.execute_hp_attack(actor, action.target, skill)
        elif skill_type == SkillType.BRV_HP_ATTACK:
            self.execute_brv_hp_attack(actor, action.target, skill)
        elif skill_type == SkillType.HEAL:
            self.execute_skill_heal(actor, action.target, skill)
        elif skill_type == SkillType.BUFF:
            self.execute_buff(actor, action.target, skill)
        elif skill_type == SkillType.DEBUFF:
            self.execute_debuff(actor, action.target, skill)
        elif skill_type == SkillType.FIELD:
            self.execute_field_skill(actor, skill)
        elif skill_type == SkillType.SPECIAL:
            self.execute_special_skill(actor, action.target, skill)
        elif skill_type == SkillType.ULTIMATE:
            self.execute_ultimate_skill(actor, action.target, skill)
        elif skill_type == SkillType.COUNTER:
            self.execute_counter_skill(actor, skill)
        else:
            self.log(f"알 수 없는 스킬 타입: {skill_type}")
    
    def execute_brv_attack(self, actor: Character, target: Character, skill: dict):
        """BRV 공격 실행"""
        if not target or not target.is_alive:
            self.log(f"{actor.name}의 {skill['name']}이(가) 빗나갔습니다.")
            return
        
        # 명중 판정
        if not self.is_attack_hit(actor, target):
            self.log(f"  → {actor.name}의 공격이 빗나갔습니다!")
            # 빗나감 효과음
            try:
                from .audio import get_unified_audio_system
                get_unified_audio_system().play_sfx("miss")  # 4 - Missed Hit
            except:
                pass
            return
        
        # 크리티컬 판정
        is_critical = self.is_critical_hit(actor, skill)
        critical_multiplier = 1.5 if is_critical else 1.0
        
        brv_power = skill.get("brv_power", 100)
        
        # 데미지 타입 가져오기
        from .new_skill_system import DamageType
        damage_type = skill.get("damage_type", DamageType.PHYSICAL)
        
        # 데미지 계산 (BRV 공격은 일반적으로 낮은 피해)
        base_damage = self.calculate_skill_damage(actor, target, skill, (brv_power / 100.0) * critical_multiplier)
        actual_damage = target.take_damage(base_damage)
        
        damage_type_str = self.get_damage_type_string(damage_type)
        
        # 로그 및 효과음
        if is_critical:
            self.log(f"  → {actor.name}의 크리티컬! {target.name}에게 {actual_damage} {damage_type_str} 데미지!")
            try:
                from .audio import get_unified_audio_system
                get_unified_audio_system().play_sfx("critical_hit")  # 26 - Cloud Critical Sword Hit
            except:
                pass
        else:
            self.log(f"  → {target.name}에게 {actual_damage} {damage_type_str} 데미지!")
        
        # 스킬 효과음 재생
        self.play_skill_sfx(skill)
        
        # 상태이상 적용
        self.apply_skill_status_effects(actor, target, skill)
        
        if not target.is_alive:
            self.log(f"{target.name}이(가) 쓰러졌습니다!")
    
    def execute_hp_attack(self, actor: Character, target: Character, skill: dict):
        """HP 공격 실행"""
        if not target or not target.is_alive:
            self.log(f"{actor.name}의 {skill['name']}이(가) 빗나갔습니다.")
            return
        
        hp_power = skill.get("hp_power", 100)
        
        # HP 공격은 더 강력한 데미지
        base_damage = self.calculate_skill_damage(actor, target, skill, hp_power / 100.0)
        actual_damage = target.take_damage(base_damage)
        
        # 데미지 타입 가져오기
        from .new_skill_system import DamageType
        damage_type = skill.get("damage_type", DamageType.PHYSICAL)
        damage_type_str = self.get_damage_type_string(damage_type)
        self.log(f"  → {target.name}에게 {actual_damage} {damage_type_str} 데미지!")
        
        # 상태이상 적용
        self.apply_skill_status_effects(actor, target, skill)
        
        if not target.is_alive:
            self.log(f"{target.name}이(가) 쓰러졌습니다!")
    
    def execute_brv_hp_attack(self, actor: Character, target: Character, skill: dict):
        """BRV+HP 공격 실행"""
        if not target or not target.is_alive:
            self.log(f"{actor.name}의 {skill['name']}이(가) 빗나갔습니다.")
            return
        
        brv_power = skill.get("brv_power", 80)
        hp_power = skill.get("hp_power", 60)
        
        # BRV 공격 먼저
        brv_damage = self.calculate_skill_damage(actor, target, skill, brv_power / 100.0)
        brv_actual = target.take_damage(brv_damage)
        
        # 데미지 타입 가져오기
        from .new_skill_system import DamageType
        damage_type = skill.get("damage_type", DamageType.PHYSICAL)
        damage_type_str = self.get_damage_type_string(damage_type)
        self.log(f"  → {target.name}에게 {brv_actual} {damage_type_str} 데미지! (BRV)")
        
        # 타겟이 살아있으면 HP 공격
        if target.is_alive:
            hp_damage = self.calculate_skill_damage(actor, target, skill, hp_power / 100.0)
            hp_actual = target.take_damage(hp_damage)
            self.log(f"  → {target.name}에게 {hp_actual} {damage_type_str} 데미지! (HP)")
        
        # 상태이상 적용
        self.apply_skill_status_effects(actor, target, skill)
        
        if not target.is_alive:
            self.log(f"{target.name}이(가) 쓰러졌습니다!")
    
    def execute_skill_heal(self, healer: Character, target: Character, skill: dict):
        """스킬 치유 실행"""
        if not target:
            return
        
        heal_power = skill.get("heal_power", 100)
        
        # 치유량 계산 (마법공격력 기반)
        base_heal = int(healer.magic_attack * (heal_power / 100.0))
        actual_heal = target.heal(base_heal)
        
        self.log(f"  → {target.name}이(가) {actual_heal} HP 회복했습니다!")
        
        # 치유 스킬의 상태이상 적용 (주로 버프)
        self.apply_skill_status_effects(healer, target, skill)
    
    def execute_buff(self, caster: Character, target: Character, skill: dict):
        """버프 스킬 실행"""
        target_type = skill.get("target")
        
        if target_type.value == "아군전체":
            targets = [member for member in self.party_members if member.is_alive]
            self.log(f"  → 아군 전체에게 버프 적용!")
        elif target_type.value == "자신":
            targets = [caster]
            self.log(f"  → {caster.name}에게 버프 적용!")
        else:
            targets = [target] if target else []
            if targets:
                self.log(f"  → {target.name}에게 버프 적용!")
        
        for t in targets:
            self.apply_skill_status_effects(caster, t, skill)
    
    def execute_debuff(self, caster: Character, target: Character, skill: dict):
        """디버프 스킬 실행"""
        target_type = skill.get("target")
        
        if target_type.value == "적전체":
            targets = [enemy for enemy in self.enemies if enemy.is_alive]
            self.log(f"  → 모든 적에게 디버프 적용!")
        else:
            targets = [target] if target else []
            if targets:
                self.log(f"  → {target.name}에게 디버프 적용!")
        
        for t in targets:
            self.apply_skill_status_effects(caster, t, skill)
    
    def execute_field_skill(self, caster: Character, skill: dict):
        """필드 스킬 실행"""
        # 필드 스킬은 전체에 영향
        all_targets = self.party_members + self.enemies
        
        self.log(f"  → 전장에 {skill['name']} 효과 발동!")
        
        for target in all_targets:
            if target.is_alive:
                self.apply_skill_status_effects(caster, target, skill)
    
    def execute_special_skill(self, caster: Character, target: Character, skill: dict):
        """특수 스킬 실행"""
        special_effects = skill.get("special_effects", [])
        
        for effect in special_effects:
            if effect == "analyze_enemy":
                self.log(f"  → {target.name}의 정보를 분석했습니다!")
                self.show_enemy_info(target)
            elif effect == "life_steal":
                # 생명 흡수는 데미지와 함께 처리
                if target and target.is_alive:
                    damage = self.calculate_skill_damage(caster, target, skill, 1.0)
                    actual_damage = target.take_damage(damage)
                    heal = actual_damage // 2
                    caster.heal(heal)
                    self.log(f"  → {target.name}에게 {actual_damage} 데미지, {caster.name}이(가) {heal} HP 회복!")
            else:
                self.log(f"  → 특수 효과 '{effect}' 발동!")
        
        # 일반적인 상태이상도 적용
        if target:
            self.apply_skill_status_effects(caster, target, skill)
    
    def execute_ultimate_skill(self, caster: Character, target: Character, skill: dict):
        """궁극기 실행"""
        target_type = skill.get("target")
        
        self.log(f"🌟 {caster.name}의 궁극기 발동! 🌟")
        
        if target_type.value == "적전체":
            targets = [enemy for enemy in self.enemies if enemy.is_alive]
            self.log(f"  → 모든 적을 공격!")
            
            brv_power = skill.get("brv_power", 100)
            hp_power = skill.get("hp_power", 100)
            
            for t in targets:
                if brv_power > 0:
                    brv_damage = self.calculate_skill_damage(caster, t, skill, brv_power / 100.0)
                    brv_actual = t.take_damage(brv_damage)
                    self.log(f"    → {t.name}에게 {brv_actual} 데미지!")
                
                if t.is_alive and hp_power > 0:
                    hp_damage = self.calculate_skill_damage(caster, t, skill, hp_power / 100.0)
                    hp_actual = t.take_damage(hp_damage)
                    self.log(f"    → {t.name}에게 {hp_actual} 추가 데미지!")
                
                self.apply_skill_status_effects(caster, t, skill)
                
        elif target_type.value == "아군전체":
            targets = [member for member in self.party_members if member.is_alive]
            self.log(f"  → 아군 전체 지원!")
            
            for t in targets:
                self.apply_skill_status_effects(caster, t, skill)
        
        else:
            # 단일 대상 궁극기
            if target and target.is_alive:
                brv_power = skill.get("brv_power", 120)
                hp_power = skill.get("hp_power", 100)
                
                total_damage = self.calculate_skill_damage(caster, target, skill, (brv_power + hp_power) / 100.0)
                actual_damage = target.take_damage(total_damage)
                self.log(f"  → {target.name}에게 {actual_damage} 강력한 데미지!")
                
                self.apply_skill_status_effects(caster, target, skill)
    
    def execute_counter_skill(self, caster: Character, skill: dict):
        """반격 스킬 실행"""
        self.log(f"  → {caster.name}이(가) 반격 태세를 취했습니다!")
        self.apply_skill_status_effects(caster, caster, skill)
    
    def calculate_skill_damage(self, attacker: Character, target: Character, skill: dict, power_multiplier: float) -> int:
        """스킬 데미지 계산 (관통 시스템 포함)"""
        from .new_skill_system import DamageType, PenetrationType
        
        damage_type = skill.get("damage_type", DamageType.PHYSICAL)
        penetration_type = skill.get("penetration_type", PenetrationType.NONE)
        penetration_rate = skill.get("penetration_rate", 0.0)
        
        # 기본 공격력 결정
        if damage_type == DamageType.PHYSICAL:
            base_attack = attacker.physical_attack
            target_defense = target.physical_defense
        elif damage_type == DamageType.MAGICAL:
            base_attack = attacker.magic_attack  
            target_defense = target.magic_defense
        else:  # HYBRID
            base_attack = (attacker.physical_attack + attacker.magic_attack) / 2
            target_defense = (target.physical_defense + target.magic_defense) / 2
        
        # 관통 시스템 적용
        if penetration_type == PenetrationType.TRUE_DAMAGE:
            # TRUE_DAMAGE: 일부는 방어무시, 나머지는 일반계산
            true_damage = base_attack * power_multiplier * penetration_rate
            normal_damage = (base_attack / max(1, target_defense)) * power_multiplier * (1 - penetration_rate)
            total_damage = true_damage + normal_damage
        elif penetration_type == PenetrationType.PHYSICAL_PIERCE:
            # 물리 방어력 일부 무시
            reduced_defense = target_defense * (1 - penetration_rate)
            total_damage = (base_attack / max(1, reduced_defense)) * power_multiplier
        elif penetration_type == PenetrationType.MAGICAL_PIERCE:
            # 마법 방어력 일부 무시  
            reduced_defense = target_defense * (1 - penetration_rate)
            total_damage = (base_attack / max(1, reduced_defense)) * power_multiplier
        elif penetration_type == PenetrationType.ARMOR_BREAK:
            # 방어구 파괴 후 공격
            target_defense = max(1, target_defense * (1 - penetration_rate))
            total_damage = (base_attack / target_defense) * power_multiplier
        else:
            # 일반 데미지 계산
            total_damage = (base_attack / max(1, target_defense)) * power_multiplier
        
        # 원소 상성 적용
        element_multiplier = self.calculate_element_multiplier(skill, target)
        total_damage *= element_multiplier
        
        # 최소/최대 데미지 제한
        total_damage = max(1, min(int(total_damage), attacker.level * 100))
        
        return int(total_damage)
    
    def calculate_hit_chance(self, attacker: Character, target: Character) -> float:
        """명중률 계산 (25% ~ 100%)"""
        # 기본 공식: 공격자 명중률 / 수비자 회피율
        base_hit_rate = attacker.accuracy / max(1, target.evasion)
        
        # 레벨 차이 보정 (레벨이 높을수록 명중률 증가)
        level_diff = attacker.level - target.level
        level_bonus = level_diff * 2  # 레벨 차이당 2% 보정
        
        # 최종 명중률 계산
        final_hit_rate = base_hit_rate + level_bonus
        
        # 25% ~ 100% 범위로 제한
        return max(25.0, min(100.0, final_hit_rate))
    
    def calculate_critical_chance(self, attacker: Character, skill: dict = None) -> float:
        """크리티컬 확률 계산"""
        base_critical = attacker.critical_rate
        
        # 스킬별 크리티컬 보너스
        skill_critical_bonus = 0.0
        if skill:
            skill_critical_bonus = skill.get("critical_bonus", 0.0)
        
        # 장비/아이템 크리티컬 보너스 (추후 확장)
        equipment_bonus = 0.0
        
        # 특성 크리티컬 보너스 (추후 확장)
        trait_bonus = 0.0
        
        # 최종 크리티컬 확률
        total_critical = base_critical + skill_critical_bonus + equipment_bonus + trait_bonus
        
        # 0% ~ 50% 범위로 제한 (너무 높으면 밸런스 문제)
        return max(0.0, min(50.0, total_critical))
    
    def is_attack_hit(self, attacker: Character, target: Character) -> bool:
        """공격이 명중하는지 판정"""
        import random
        
        hit_chance = self.calculate_hit_chance(attacker, target)
        roll = random.uniform(0, 100)
        
        return roll <= hit_chance
    
    def is_critical_hit(self, attacker: Character, skill: dict = None) -> bool:
        """크리티컬 히트 판정"""
        import random
        
        critical_chance = self.calculate_critical_chance(attacker, skill)
        roll = random.uniform(0, 100)
        
        return roll <= critical_chance
    
    def calculate_element_multiplier(self, skill: dict, target: Character) -> float:
        """원소 상성 계산 (세부적인 배율 적용)"""
        element = skill.get("element")
        if not element:
            return 1.0
        
        # 상세한 원소 상성표 (공격 원소 -> 상대 약점/저항)
        element_chart = {
            "화염": {
                "super_effective": ["냉기", "얼음", "식물", "언데드"],  # 1.8배
                "effective": ["바람", "금속"],                        # 1.4배
                "normal": ["화염", "대지", "빛"],                     # 1.0배
                "resist": ["물", "바다"],                            # 0.8배
                "immune": ["용암", "불꽃정령"]                        # 0.6배
            },
            "냉기": {
                "super_effective": ["화염", "물", "용", "비행"],      # 1.8배
                "effective": ["대지", "식물"],                       # 1.4배
                "normal": ["냉기", "바람", "금속"],                  # 1.0배
                "resist": ["얼음", "언데드"],                        # 0.8배
                "immune": ["빙결정령", "절대영도"]                    # 0.6배
            },
            "번개": {
                "super_effective": ["물", "바다", "금속", "비행"],    # 1.8배
                "effective": ["기계", "사이보그"],                   # 1.4배
                "normal": ["번개", "화염", "빛"],                    # 1.0배
                "resist": ["대지", "고무", "절연"],                  # 0.8배
                "immune": ["뇌전정령", "절연체"]                     # 0.6배
            },
            "대지": {
                "super_effective": ["번개", "화염", "독", "기계"],    # 1.8배
                "effective": ["금속", "광물"],                       # 1.4배
                "normal": ["대지", "물", "어둠"],                    # 1.0배
                "resist": ["바람", "비행", "식물"],                  # 0.8배
                "immune": ["대지정령", "부유"]                       # 0.6배
            },
            "바람": {
                "super_effective": ["비행", "독", "가스", "연기"],    # 1.8배
                "effective": ["화염", "냉기"],                       # 1.4배
                "normal": ["바람", "번개", "빛"],                    # 1.0배
                "resist": ["대지", "중량급"],                        # 0.8배
                "immune": ["풍신", "진공"]                          # 0.6배
            },
            "물": {
                "super_effective": ["화염", "대지", "사막", "용암"],  # 1.8배
                "effective": ["독", "산성"],                         # 1.4배
                "normal": ["물", "냉기", "식물"],                    # 1.0배
                "resist": ["번개", "기름"],                          # 0.8배
                "immune": ["수신", "물속생물"]                       # 0.6배
            },
            "빛": {
                "super_effective": ["어둠", "언데드", "악마", "그림자"], # 1.8배
                "effective": ["독", "저주"],                         # 1.4배
                "normal": ["빛", "번개", "바람"],                    # 1.0배
                "resist": ["신성", "천사"],                          # 0.8배
                "immune": ["광명신", "순수빛"]                       # 0.6배
            },
            "어둠": {
                "super_effective": ["빛", "신성", "천사", "정령"],    # 1.8배
                "effective": ["정신", "환상"],                       # 1.4배
                "normal": ["어둠", "독", "대지"],                    # 1.0배
                "resist": ["언데드", "악마"],                        # 0.8배
                "immune": ["암흑신", "무"]                           # 0.6배
            },
            "독": {
                "super_effective": ["식물", "생물", "자연", "치유"],  # 1.8배
                "effective": ["물", "대지"],                         # 1.4배
                "normal": ["독", "어둠", "산성"],                    # 1.0배
                "resist": ["기계", "언데드", "독면역"],              # 0.8배
                "immune": ["독신", "완전면역"]                       # 0.6배
            }
        }
        
        element_name = element.value if hasattr(element, 'value') else str(element)
        
        # 대상의 원소 속성 확인 (캐릭터에 element_type 속성이 있다면)
        target_elements = []
        if hasattr(target, 'element_type'):
            if isinstance(target.element_type, list):
                target_elements = target.element_type
            else:
                target_elements = [target.element_type]
        elif hasattr(target, 'element_weakness'):
            # 기존 약점 시스템 호환
            target_elements = getattr(target, 'element_weakness', [])
        elif hasattr(target, 'name'):
            # 이름으로 원소 추정
            name = target.name.lower()
            if any(keyword in name for keyword in ['불', '화염', '파이어']):
                target_elements = ['화염']
            elif any(keyword in name for keyword in ['얼음', '냉기', '아이스']):
                target_elements = ['냉기']
            elif any(keyword in name for keyword in ['번개', '전기', '썬더']):
                target_elements = ['번개']
            elif any(keyword in name for keyword in ['땅', '대지', '어스']):
                target_elements = ['대지']
            elif any(keyword in name for keyword in ['바람', '윈드']):
                target_elements = ['바람']
            elif any(keyword in name for keyword in ['물', '워터']):
                target_elements = ['물']
            elif any(keyword in name for keyword in ['빛', '라이트', '홀리']):
                target_elements = ['빛']
            elif any(keyword in name for keyword in ['어둠', '다크', '섀도우']):
                target_elements = ['어둠']
            elif any(keyword in name for keyword in ['독', '포이즌']):
                target_elements = ['독']
        
        # 상성 계산
        if element_name in element_chart and target_elements:
            chart = element_chart[element_name]
            
            # 여러 원소를 가진 경우 가장 효과적인 배율 적용
            multipliers = []
            for target_element in target_elements:
                if target_element in chart["super_effective"]:
                    multipliers.append(1.8)
                elif target_element in chart["effective"]:
                    multipliers.append(1.4)
                elif target_element in chart["resist"]:
                    multipliers.append(0.8)
                elif target_element in chart["immune"]:
                    multipliers.append(0.6)
                else:
                    multipliers.append(1.0)
            
            # 가장 높은 배율 반환 (공격자에게 유리하게)
            return max(multipliers) if multipliers else 1.0
        
        return 1.0  # 기본 배율
    
    def get_damage_type_string(self, damage_type) -> str:
        """데미지 타입을 문자열로 변환"""
        from .new_skill_system import DamageType
        
        if damage_type == DamageType.PHYSICAL:
            return "물리"
        elif damage_type == DamageType.MAGICAL:
            return "마법"
        elif damage_type == DamageType.HYBRID:
            return "복합"
        else:
            return "일반"
    
    def apply_skill_status_effects(self, caster: Character, target: Character, skill: dict):
        """스킬의 상태이상 효과 적용"""
        from .new_skill_system import StatusType, get_status_icon
        
        status_effects = skill.get("status_effects", [])
        
        for effect_data in status_effects:
            try:
                status_type = effect_data.get("type")
                duration = effect_data.get("duration", 3)
                intensity = effect_data.get("intensity", 1)
                
                # StatusType enum 확인
                if isinstance(status_type, str):
                    # 문자열인 경우 StatusType에서 찾기
                    for status_enum in StatusType:
                        if status_enum.value == status_type or status_enum.name == status_type:
                            status_type = status_enum
                            break
                
                if not isinstance(status_type, StatusType):
                    continue
                
                # 캐릭터에 상태효과 적용
                self._apply_status_effect_to_character(target, status_type, duration, intensity)
                
                # 로그 출력
                icon = get_status_icon(status_type)
                self.log(f"    → {target.name}에게 {icon} {status_type.value} 효과 적용! (지속: {duration}턴)")
                    
            except Exception as e:
                # 상태이상 적용 실패해도 게임은 계속
                status_name = str(effect_data.get("type", "알 수 없음"))
                self.log(f"    → {target.name}에게 {status_name} 효과 적용!")
    
    def _apply_status_effect_to_character(self, character: Character, status_type, duration: int, intensity: int = 1):
        """캐릭터에게 상태효과 적용"""
        from .new_skill_system import StatusType
        
        # 캐릭터의 상태효과 시스템이 없다면 임시 딕셔너리 생성
        if not hasattr(character, 'status_effects'):
            character.status_effects = {}
        
        # 상태효과 저장
        character.status_effects[status_type] = {
            'duration': duration,
            'intensity': intensity,
            'applied_turn': getattr(self, 'current_turn', 0)
        }
    
    def process_status_effects(self, character: Character):
        """캐릭터의 상태효과 처리 (턴 시작/종료 시 호출)"""
        from .new_skill_system import StatusType, get_status_icon
        
        if not hasattr(character, 'status_effects'):
            return
        
        expired_effects = []
        
        for status_type, effect_data in character.status_effects.items():
            duration = effect_data['duration']
            intensity = effect_data['intensity']
            
            # 상태효과 적용
            self._apply_status_effect_tick(character, status_type, intensity)
            
            # 지속시간 감소
            effect_data['duration'] -= 1
            
            if effect_data['duration'] <= 0:
                expired_effects.append(status_type)
                icon = get_status_icon(status_type)
                self.log(f"{character.name}의 {icon} {status_type.value} 효과가 사라졌습니다.")
        
        # 만료된 효과 제거
        for status_type in expired_effects:
            del character.status_effects[status_type]
    
    def _apply_status_effect_tick(self, character: Character, status_type, intensity: int):
        """상태효과의 턴별 효과 적용"""
        from .new_skill_system import StatusType
        
        # 지속 피해 상태효과들
        damage_effects = {
            StatusType.POISON: 3 * intensity,
            StatusType.BURN: 4 * intensity,
            StatusType.BLEED: 2 * intensity,
            StatusType.CORRODE: 5 * intensity,
            StatusType.NECROSIS: 8 * intensity,
        }
        
        # 지속 회복 상태효과들
        heal_effects = {
            StatusType.REGENERATION: 5 * intensity,
        }
        
        if status_type in damage_effects:
            damage = damage_effects[status_type]
            character.take_damage(damage)
            self.log(f"  {character.name}이(가) {status_type.value}로 {damage} 피해를 입었습니다!")
            
        elif status_type in heal_effects:
            heal = heal_effects[status_type]
            old_hp = character.current_hp
            character.current_hp = min(character.limited_max_hp, character.current_hp + heal)
            actual_heal = character.current_hp - old_hp
            if actual_heal > 0:
                self.log(f"  {character.name}이(가) {status_type.value}로 {actual_heal} HP를 회복했습니다!")
    
    def get_character_status_display(self, character: Character) -> str:
        """캐릭터의 상태효과를 문자열로 표시"""
        from .new_skill_system import get_status_icon
        
        if not hasattr(character, 'status_effects') or not character.status_effects:
            return ""
        
        status_icons = []
        for status_type, effect_data in character.status_effects.items():
            icon = get_status_icon(status_type)
            duration = effect_data['duration']
            status_icons.append(f"{icon}({duration})")
        
        return " ".join(status_icons)
    
    def show_enemy_info(self, enemy: Character):
        """적 정보 표시"""
        print(f"\n=== {enemy.name} 정보 ===")
        print(f"레벨: {enemy.level}")
        print(f"HP: {enemy.current_hp}/{enemy.limited_max_hp}")
        print(f"MP: {enemy.current_mp}/{enemy.max_mp}")
        print(f"물리공격력: {enemy.physical_attack}")
        print(f"마법공격력: {enemy.magic_attack}")
        print(f"물리방어력: {enemy.physical_defense}")
        print(f"마법방어력: {enemy.magic_defense}")
        print(f"속도: {enemy.speed}")
        
        if hasattr(enemy, 'element_weakness'):
            print(f"약점: {', '.join(enemy.element_weakness)}")
        if hasattr(enemy, 'element_resistance'):
            print(f"저항: {', '.join(enemy.element_resistance)}")
        print("="*30)
            
    def execute_skill_attack(self, attacker: Character, target: Character, modifier: float, skill_name: str, damage_type: str):
        """스킬 공격 실행"""
        if not target or not target.is_alive:
            self.log(f"{attacker.name}의 {skill_name}이(가) 빗나갔습니다.")
            return
            
        damage = attacker.calculate_damage_to(target, modifier, damage_type)
        actual_damage = target.take_damage(damage)
        
        damage_type_str = "물리" if damage_type == "physical" else "마법"
        self.log(f"{attacker.name}이(가) {skill_name}으로 {target.name}을(를) 공격했습니다! [{actual_damage} {damage_type_str} 데미지]")
        
        # 상태이상 적용 체크
        self._apply_skill_status_effects(attacker, target, skill_name)
        
        if not target.is_alive:
            self.log(f"{target.name}이(가) 쓰러졌습니다!")
            
    def _apply_skill_status_effects(self, attacker: Character, target: Character, skill_name: str):
        """스킬에 따른 상태이상 적용"""
        from .new_skill_system import StatusType, get_status_icon
        
        # 스킬별 상태이상 효과 정의
        skill_effects = {
            "독공격": [(StatusType.POISON, 5, 0.6)],
            "화염공격": [(StatusType.BURN, 3, 0.5)],
            "빙결공격": [(StatusType.FREEZE, 2, 0.4)],
            "기절공격": [(StatusType.STUN, 1, 0.3)],
            "마비공격": [(StatusType.PARALYZE, 3, 0.4)],
            "수면공격": [(StatusType.SLEEP, 2, 0.3)],
            "침묵공격": [(StatusType.SILENCE, 4, 0.5)],
            "실명공격": [(StatusType.BLIND, 3, 0.4)],
            "혼란공격": [(StatusType.CONFUSION, 3, 0.3)],
            "매혹공격": [(StatusType.CHARM, 2, 0.2)],
        }
        
        # 스킬 이름에서 상태효과 찾기
        for skill_key, effects in skill_effects.items():
            if skill_key in skill_name:
                for status_type, duration, chance in effects:
                    if random.random() < chance:
                        self._apply_status_effect_to_character(target, status_type, duration)
                        icon = get_status_icon(status_type)
                        self.log(f"    → {target.name}이(가) {icon} {status_type.value} 상태가 되었습니다!")
                break
            
    def execute_attack(self, attacker: Character, target: Character, modifier: float = 1.0, skill_name: str = "공격"):
        """공격 실행"""
        if not target or not target.is_alive:
            self.log(f"{attacker.name}의 공격이 빗나갔습니다.")
            return
        
        # 명중 판정
        if not self.is_attack_hit(attacker, target):
            self.log(f"  → {attacker.name}의 공격이 빗나갔습니다!")
            # 빗나감 효과음
            try:
                from .audio import get_unified_audio_system
                get_unified_audio_system().play_sfx("miss")  # 4 - Missed Hit
            except:
                pass
            return
        
        # 크리티컬 판정
        is_critical = self.is_critical_hit(attacker)
        critical_multiplier = 1.5 if is_critical else 1.0
            
        # 공격 타입 결정 (물리/마법 중 더 높은 공격력 사용)
        damage_type = "physical" if attacker.physical_attack >= attacker.magic_attack else "magic"
        damage = attacker.calculate_damage_to(target, modifier * critical_multiplier, damage_type)
        actual_damage = target.take_damage(damage)
        
        damage_type_str = "물리" if damage_type == "physical" else "마법"
        
        # 로그 및 효과음
        if is_critical:
            if skill_name == "공격":
                self.log(f"{attacker.name}의 크리티컬! {target.name}에게 {actual_damage} {damage_type_str} 데미지!")
            else:
                self.log(f"{attacker.name}의 {skill_name} 크리티컬! {target.name}에게 {actual_damage} {damage_type_str} 데미지!")
            
            # 크리티컬 효과음
            try:
                from .audio import get_unified_audio_system
                get_unified_audio_system().play_sfx("critical_hit")  # 26 - Cloud Critical Sword Hit
            except:
                pass
        else:
            if skill_name == "공격":
                self.log(f"{attacker.name}이(가) {target.name}을(를) {damage_type_str} 공격했습니다! [{actual_damage} 데미지]")
            else:
                self.log(f"{attacker.name}이(가) {skill_name}으로 {target.name}을(를) 공격했습니다! [{actual_damage} {damage_type_str} 데미지]")
            
            # 일반 공격 효과음
            try:
                from .audio import get_unified_audio_system
                get_unified_audio_system().play_sfx("sword_hit")  # 17 - Cloud's Sword Hit
            except:
                pass
            
        if not target.is_alive:
            self.log(f"{target.name}이(가) 쓰러졌습니다!")
            # 적 사망 효과음
            try:
                from .audio import get_unified_audio_system
                get_unified_audio_system().play_sfx("victory")  # 승리 사운드
            except:
                pass
            
    def execute_defend(self, character: Character):
        """방어 실행"""
        # 방어 시 ATB 게이지를 조금 더 빨리 충전
        character.atb_gauge += 20
        self.log(f"{character.name}이(가) 방어 태세를 취했습니다.")
        
    def execute_heal(self, healer: Character, target: Character, modifier: float):
        """회복 실행"""
        if not target:
            return
            
        heal_amount = int(target.max_hp * modifier)
        actual_heal = target.heal(heal_amount)
        
        self.log(f"{healer.name}이(가) {target.name}을(를) 회복했습니다! [{actual_heal} HP 회복]")
        
    def execute_area_attack(self, attacker: Character, modifier: float, skill_name: str, damage_type: str = "physical"):
        """전체 공격 실행"""
        if attacker in self.party_members:
            targets = [enemy for enemy in self.enemies if enemy.is_alive]
        else:
            targets = [member for member in self.party_members if member.is_alive]
            
        damage_type_str = "물리" if damage_type == "physical" else "마법"
        self.log(f"{attacker.name}이(가) {skill_name}을(를) 사용했습니다! ({damage_type_str} 전체공격)")
        
        for target in targets:
            damage = attacker.calculate_damage_to(target, modifier, damage_type)
            actual_damage = target.take_damage(damage)
            self.log(f"  → {target.name}에게 {actual_damage} {damage_type_str} 데미지!")
            
    def check_combat_end(self) -> bool:
        """전투 종료 조건 확인"""
        alive_party = [char for char in self.party_members if char.is_alive]
        alive_enemies = [char for char in self.enemies if char.is_alive]
        
        if not alive_party:
            self.log("파티가 전멸했습니다...")
            self.combat_active = False
            return True
            
        if not alive_enemies:
            self.log("승리했습니다!")
            self.give_rewards()
            self.combat_active = False
            return True
            
        return False
        
    def give_rewards(self):
        """보상 지급"""
        exp_reward = random.randint(50, 100)
        self.log(f"경험치 {exp_reward}를 획득했습니다!")
        
        for member in self.party_members:
            if member.is_alive:
                leveled_up = member.gain_experience(exp_reward)
                if leveled_up:
                    # 레벨업 효과음 및 시각 효과
                    try:
                        from .ascii_effects import play_ascii_sound
                        play_ascii_sound("level_up")
                    except:
                        pass
                
    def show_combat_status(self):
        """전투 상태 표시"""
        print(f"\n{'='*60}")
        print("=== 파티 상태 ===")
        for member in self.party_members:
            print(f"  {member.get_status_string()}")
            
        print("\n=== 적 상태 ===")
        for enemy in self.enemies:
            if enemy.is_alive:
                print(f"  {enemy.get_status_string()}")
                
        # 최근 로그 표시
        if self.combat_log:
            print(f"\n=== 전투 로그 ===")
            for log in self.combat_log[-3:]:  # 최근 3개만 표시
                print(f"  {log}")
                
    def log(self, message: str):
        """전투 로그 추가"""
        self.combat_log.append(message)
        print(f">> {message}")
