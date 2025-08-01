#!/usr/bin/env python3
"""
필드 스킬 시스템 - 시전자 선택 기능 포함
"""

from typing import List, Dict, Any, Optional
from .character import Character, PartyManager
from .balance_system import FieldSkillBalance, get_field_skill_targets
from .field_cooking import get_field_cooking_interface

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

class FieldSkillSystem:
    """필드 스킬 사용 시스템"""
    
    def __init__(self):
        self.skill_cooldowns = {}  # 캐릭터별 스킬 쿨다운 추적
        self.available_skills = list(FieldSkillBalance.FIELD_SKILLS.keys())  # 사용 가능한 스킬 목록
        
    def can_use_skill(self, caster: Character, skill_name: str) -> bool:
        """스킬 사용 가능 여부 확인"""
        # 스킬 존재 확인
        skill_data = FieldSkillBalance.FIELD_SKILLS.get(skill_name)
        if not skill_data:
            return False
        
        # 클래스 제한 확인
        character_class = getattr(caster, 'character_class', '전사')
        allowed_classes = skill_data.get("classes", [])
        if allowed_classes and character_class not in allowed_classes:
            return False
            
        # MP 확인
        mp_cost = skill_data["mp_cost"]
        if caster.current_mp < mp_cost:
            return False
        
        # 쿨다운 확인
        caster_key = f"{caster.name}_{skill_name}"
        if caster_key in self.skill_cooldowns:
            last_use_steps = self.skill_cooldowns[caster_key]
            cooldown_steps = skill_data["cooldown_steps"]
            if (caster.steps_taken - last_use_steps) < cooldown_steps:
                return False
        
        return True
    
    def get_skill_cooldown_remaining(self, caster: Character, skill_name: str) -> int:
        """남은 쿨다운 걸음 수 반환"""
        skill_data = FieldSkillBalance.FIELD_SKILLS.get(skill_name)
        if not skill_data:
            return 0
            
        caster_key = f"{caster.name}_{skill_name}"
        if caster_key not in self.skill_cooldowns:
            return 0
            
        last_use_steps = self.skill_cooldowns[caster_key]
        cooldown_steps = skill_data["cooldown_steps"]
        elapsed_steps = caster.steps_taken - last_use_steps
        
        return max(0, cooldown_steps - elapsed_steps)
    
    def display_available_skills(self, party: PartyManager):
        """사용 가능한 필드 스킬 표시"""
        print(f"\n{CYAN}⚡ 필드 스킬 메뉴{RESET}")
        print("="*70)
        
        # 파티 멤버들이 사용할 수 있는 스킬 수집
        available_skills = {}
        for member in party.get_alive_members():
            character_class = getattr(member, 'character_class', '전사')
            for skill_name, skill_data in FieldSkillBalance.FIELD_SKILLS.items():
                allowed_classes = skill_data.get("classes", [])
                if character_class in allowed_classes:
                    if skill_name not in available_skills:
                        available_skills[skill_name] = []
                    
                    # 사용 가능 여부 확인
                    if self.can_use_skill(member, skill_name):
                        available_skills[skill_name].append(f"{member.name}")
                    else:
                        cooldown = self.get_skill_cooldown_remaining(member, skill_name)
                        if cooldown > 0:
                            available_skills[skill_name].append(f"{member.name}({cooldown}걸음)")
                        elif member.current_mp < skill_data['mp_cost']:
                            available_skills[skill_name].append(f"{member.name}(MP부족)")
                        else:
                            available_skills[skill_name].append(f"{member.name}(사용불가)")
        
        if not available_skills:
            print(f"\n{RED}❌ 현재 사용할 수 있는 필드 스킬이 없습니다.{RESET}")
            print(f"{YELLOW}💡 파티원의 MP가 부족하거나 쿨다운 중일 수 있습니다.{RESET}")
            return
        
        # 스킬 목록 표시
        skill_index = 1
        for skill_name, casters in available_skills.items():
            skill_data = FieldSkillBalance.FIELD_SKILLS[skill_name]
            print(f"\n{WHITE}{skill_index}. {skill_name}{RESET}")
            print(f"   📝 {skill_data['description']}")
            print(f"   💫 MP 소모: {skill_data['mp_cost']}")
            print(f"   ⏰ 쿨다운: {skill_data['cooldown_steps']}걸음")
            print(f"   🎯 대상: {self._get_target_desc(skill_data.get('target_type', 'none'))}")
            
            # 사용 가능한 시전자 표시
            usable_casters = [c for c in casters if "(" not in c]
            unusable_casters = [c for c in casters if "(" in c]
            
            if usable_casters:
                print(f"   ✅ 사용 가능: {GREEN}{', '.join(usable_casters)}{RESET}")
            if unusable_casters:
                print(f"   ⏳ 대기 중: {YELLOW}{', '.join(unusable_casters)}{RESET}")
            
            skill_index += 1
    
    def _get_target_desc(self, target_type: str) -> str:
        """대상 타입 설명 반환"""
        target_descs = {
            "none": "대상 없음",
            "ally": "아군 선택",
            "party": "파티 전체"
        }
        return target_descs.get(target_type, "알 수 없음")
    
    def select_caster_and_use_skill(self, party: PartyManager) -> bool:
        """시전자 선택하고 스킬 사용 - 커서 시스템"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            # 파티 멤버들이 사용할 수 있는 스킬 수집
            available_skills = {}
            for member in party.get_alive_members():
                character_class = getattr(member, 'character_class', '전사')
                for skill_name, skill_data in FieldSkillBalance.FIELD_SKILLS.items():
                    allowed_classes = skill_data.get("classes", [])
                    if character_class in allowed_classes:
                        if skill_name not in available_skills:
                            available_skills[skill_name] = []
                        
                        # 사용 가능 여부 확인
                        if self.can_use_skill(member, skill_name):
                            available_skills[skill_name].append(member.name)
            
            if not available_skills:
                print(f"\n{RED}❌ 현재 사용할 수 있는 필드 스킬이 없습니다.{RESET}")
                print(f"{YELLOW}💡 파티원의 MP가 부족하거나 쿨다운 중일 수 있습니다.{RESET}")
                return False
            
            # 스킬 옵션 구성
            skill_options = []
            skill_descriptions = []
            skill_list = []
            
            # 스킬 이모지 맵핑
            skill_emojis = {
                "환경 정화": "🌿",
                "던전 분석": "🔍", 
                "집단 축복": "🙏",
                "장비 수리": "🔧",
                "내구도 분석": "📊",
                "보물 탐지": "💎",
                "야외 치료": "💚",
                "자물쇠 해제": "🗝️",
                "마법 이동": "🌀",
                "내구도 강화": "⚔️",
                "장비 보호": "🛡️"
            }
            
            for skill_name, casters in available_skills.items():
                if casters:  # 사용 가능한 캐릭터가 있는 스킬만
                    skill_data = FieldSkillBalance.FIELD_SKILLS[skill_name]
                    emoji = skill_emojis.get(skill_name, "✨")
                    skill_options.append(f"{emoji} {skill_name}")
                    skill_descriptions.append(f"{skill_data['description']} (MP: {skill_data['mp_cost']}, 사용가능: {', '.join(casters)})")
                    skill_list.append(skill_name)
            
            if not skill_options:
                print(f"\n{RED}❌ 사용 가능한 필드 스킬이 없습니다.{RESET}")
                return False
            
            # 스킬 선택 메뉴
            skill_menu = create_simple_menu("🎮 ⚡ 필드 스킬", skill_options, skill_descriptions)
            skill_choice = skill_menu.run()
            
            if skill_choice is None:
                return False
            
            selected_skill = skill_list[skill_choice]
            return self._execute_skill_with_caster_selection(party, selected_skill)
            
        except ImportError:
            # 폴백: 기존 텍스트 시스템
            return self._legacy_select_caster_and_use_skill(party)
    
    def _legacy_select_caster_and_use_skill(self, party: PartyManager) -> bool:
        """기존 텍스트 기반 스킬 선택"""
        self.display_available_skills(party)
        
        try:
            # 스킬 선택
            print(f"\n{YELLOW}사용할 스킬 번호를 입력하세요 (0: 취소):{RESET}")
            skill_choice = int(input(f"{CYAN}>>> {RESET}"))
            
            if skill_choice == 0:
                return False
            
            skill_names = list(FieldSkillBalance.FIELD_SKILLS.keys())
            if 1 <= skill_choice <= len(skill_names):
                skill_name = skill_names[skill_choice - 1]
                return self._execute_skill_with_caster_selection(party, skill_name)
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return False
                
        except (ValueError, KeyboardInterrupt):
            print(f"{RED}취소되었습니다.{RESET}")
            return False
    
    def _execute_skill_with_caster_selection(self, party: PartyManager, skill_name: str) -> bool:
        """시전자 선택 후 스킬 실행 - 커서 시스템"""
        skill_data = FieldSkillBalance.FIELD_SKILLS[skill_name]
        
        # 사용 가능한 시전자 찾기
        available_casters = []
        for member in party.get_alive_members():
            if self.can_use_skill(member, skill_name):
                available_casters.append(member)
        
        if not available_casters:
            print(f"{RED}{skill_name}을(를) 사용할 수 있는 캐릭터가 없습니다.{RESET}")
            return False
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            # 시전자 옵션 구성
            caster_options = []
            caster_descriptions = []
            
            for caster in available_casters:
                mp_after = caster.current_mp - skill_data["mp_cost"]
                caster_options.append(f"{caster.name}")
                caster_descriptions.append(f"MP: {caster.current_mp} → {mp_after}")
            
            # 시전자 선택 메뉴
            caster_menu = create_simple_menu(f"{skill_name} 시전자 선택", caster_options, caster_descriptions)
            caster_choice = caster_menu.run()
            
            if caster_choice is None:
                return False
            
            selected_caster = available_casters[caster_choice]
            return self._execute_skill(party, selected_caster, skill_name)
            
        except ImportError:
            # 폴백: 기존 텍스트 시스템
            return self._legacy_execute_skill_with_caster_selection(party, skill_name)
    
    def _legacy_execute_skill_with_caster_selection(self, party: PartyManager, skill_name: str) -> bool:
        """기존 텍스트 기반 시전자 선택"""
        skill_data = FieldSkillBalance.FIELD_SKILLS[skill_name]
        
        # 사용 가능한 시전자 찾기
        available_casters = []
        for member in party.get_alive_members():
            if self.can_use_skill(member, skill_name):
                available_casters.append(member)
        
        if not available_casters:
            print(f"{RED}{skill_name}을(를) 사용할 수 있는 캐릭터가 없습니다.{RESET}")
            return False
        
        # 시전자 선택
        print(f"\n{YELLOW}{skill_name}을(를) 사용할 캐릭터를 선택하세요:{RESET}")
        for i, caster in enumerate(available_casters, 1):
            mp_after = caster.current_mp - skill_data["mp_cost"]
            print(f"{WHITE}{i}. {caster.name}{RESET} (MP: {caster.current_mp} → {mp_after})")
        
        try:
            caster_choice = int(input(f"{CYAN}>>> {RESET}"))
            if 1 <= caster_choice <= len(available_casters):
                selected_caster = available_casters[caster_choice - 1]
                return self._execute_skill(party, selected_caster, skill_name)
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return False
                
        except (ValueError, KeyboardInterrupt):
            print(f"{RED}취소되었습니다.{RESET}")
            return False
    
    def _execute_skill(self, party: PartyManager, caster: Character, skill_name: str) -> bool:
        """실제 스킬 실행"""
        skill_data = FieldSkillBalance.FIELD_SKILLS[skill_name]
        target_type = skill_data.get("target_type", "none")
        
        # MP 소모
        caster.use_mp(skill_data["mp_cost"])
        
        # 쿨다운 설정
        caster_key = f"{caster.name}_{skill_name}"
        self.skill_cooldowns[caster_key] = caster.steps_taken
        
        print(f"\n{GREEN}{caster.name}이(가) {skill_name}을(를) 사용합니다!{RESET}")
        
        # 스킬 효과 적용
        success = True
        
        if skill_name == "보물 탐지":
            success = self._treasure_detection(party, caster)
        elif skill_name == "야외 치료":
            success = self._field_healing(party, caster, target_type)
        elif skill_name == "마법 이동":
            success = self._magic_teleport(party, caster)
        elif skill_name == "자물쇠 해제":
            success = self._lock_picking(party, caster)
        elif skill_name == "환경 정화":
            success = self._environmental_cleanse(party, caster)
        elif skill_name == "집단 은신":
            success = self._group_stealth(party, caster)
        elif skill_name == "던전 분석":
            success = self._dungeon_analysis(party, caster)
        elif skill_name == "집단 축복":
            success = self._group_blessing(party, caster)
        elif skill_name == "장비 수리":
            success = self._equipment_repair(party, caster, target_type)
        elif skill_name == "내구도 강화":
            success = self._durability_enhancement(party, caster, target_type)
        elif skill_name == "완벽 수리":
            success = self._perfect_repair(party, caster)
        elif skill_name == "내구도 분석":
            success = self._durability_analysis(party, caster)
        elif skill_name == "장비 보호":
            success = self._equipment_protection(party, caster)
        
        return success
    
    def _treasure_detection(self, party: PartyManager, caster: Character) -> bool:
        """보물 탐지 효과"""
        import random
        
        skill_data = FieldSkillBalance.FIELD_SKILLS["보물 탐지"]
        success_rate = skill_data["success_rate"]
        
        if random.random() < success_rate:
            print(f"{YELLOW}✨ 숨겨진 보물을 발견했습니다!{RESET}")
            # 실제 게임에서는 보물 생성 로직 호출
            return True
        else:
            print(f"{BLUE}이 지역에는 특별한 보물이 없는 것 같습니다.{RESET}")
            return False
    
    def _field_healing(self, party: PartyManager, caster: Character, target_type: str) -> bool:
        """야외 치료 효과"""
        caster_stats = {
            "magic_attack": caster.magic_attack,
            "max_hp": caster.max_hp,
            "physical_attack": caster.physical_attack,
            "physical_defense": caster.physical_defense,
            "magic_defense": caster.magic_defense
        }
        
        heal_amount = FieldSkillBalance.calculate_heal_amount(caster_stats, 0.3)
        
        if target_type == "ally":
            # 대상 선택
            injured_allies = [m for m in party.get_alive_members() if m.current_hp < m.limited_max_hp]
            if not injured_allies:
                print(f"{BLUE}치료가 필요한 동료가 없습니다.{RESET}")
                return False
            
            print(f"\n{YELLOW}치료할 대상을 선택하세요:{RESET}")
            for i, ally in enumerate(injured_allies, 1):
                hp_after = min(ally.limited_max_hp, ally.current_hp + heal_amount)
                print(f"{WHITE}{i}. {ally.name}{RESET} (HP: {ally.current_hp} → {hp_after})")
            
            try:
                target_choice = int(input(f"{CYAN}>>> {RESET}"))
                if 1 <= target_choice <= len(injured_allies):
                    target = injured_allies[target_choice - 1]
                    healed = target.heal(heal_amount)
                    print(f"{GREEN}{target.name}이(가) {healed} HP 회복했습니다!{RESET}")
                    return True
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
                    return False
            except (ValueError, KeyboardInterrupt):
                print(f"{RED}취소되었습니다.{RESET}")
                return False
        else:
            # 파티 전체 치료
            healed_members = []
            for member in party.get_alive_members():
                healed = member.heal(heal_amount)
                if healed > 0:
                    healed_members.append(f"{member.name}({healed})")
            
            if healed_members:
                print(f"{GREEN}파티 전체가 회복했습니다: {', '.join(healed_members)}{RESET}")
                return True
            else:
                print(f"{BLUE}치료가 필요한 동료가 없습니다.{RESET}")
                return False
    
    def _magic_teleport(self, party: PartyManager, caster: Character) -> bool:
        """마법 이동 효과"""
        print(f"{MAGENTA}✨ 마법의 힘으로 안전한 곳으로 이동했습니다!{RESET}")
        # 실제 게임에서는 던전 탈출 또는 안전 지역 이동 로직 호출
        return True
    
    def _lock_picking(self, party: PartyManager, caster: Character) -> bool:
        """자물쇠 해제 효과"""
        import random
        
        skill_data = FieldSkillBalance.FIELD_SKILLS["자물쇠 해제"]
        success_rate = skill_data["success_rate"]
        
        if random.random() < success_rate:
            print(f"{GREEN}🔓 자물쇠를 성공적으로 해제했습니다!{RESET}")
            # 실제 게임에서는 잠긴 문/상자 해제 로직 호출
            return True
        else:
            print(f"{RED}🔒 자물쇠 해제에 실패했습니다.{RESET}")
            return False
    
    def _environmental_cleanse(self, party: PartyManager, caster: Character) -> bool:
        """환경 정화 효과"""
        cleansed_members = []
        for member in party.get_alive_members():
            cured_effects = member.cure_all_status_effects()
            if cured_effects:
                cleansed_members.append(f"{member.name}({'/'.join(cured_effects)})")
        
        if cleansed_members:
            print(f"{GREEN}🌿 환경과 파티가 정화되었습니다: {', '.join(cleansed_members)}{RESET}")
        else:
            print(f"{BLUE}🌿 환경을 정화했지만 특별한 효과는 없었습니다.{RESET}")
        
        return True
    
    def _group_stealth(self, party: PartyManager, caster: Character) -> bool:
        """집단 은신 효과"""
        print(f"{BLUE}👤 파티 전체가 은신 상태가 되었습니다! (3분간 적 회피 가능){RESET}")
        # 실제 게임에서는 은신 상태 부여 로직 호출
        return True
    
    def _dungeon_analysis(self, party: PartyManager, caster: Character) -> bool:
        """던전 분석 효과"""
        import random
        
        # 가상의 던전 정보 생성
        danger_level = random.choice(["안전", "보통", "위험", "매우 위험"])
        treasure_chance = random.randint(10, 90)
        
        print(f"{CYAN}🔍 던전 분석 결과:{RESET}")
        print(f"   위험도: {danger_level}")
        print(f"   보물 확률: {treasure_chance}%")
        print(f"   추천 경로: {'동쪽' if random.random() > 0.5 else '서쪽'} 통로")
        
        return True
    
    def _group_blessing(self, party: PartyManager, caster: Character) -> bool:
        """집단 축복 효과"""
        print(f"{YELLOW}✨ 파티 전체에 강력한 축복이 내려졌습니다! (5분간 모든 능력치 증가){RESET}")
        # 실제 게임에서는 버프 효과 부여 로직 호출
        
        # 임시로 각 멤버에게 축복 메시지
        for member in party.get_alive_members():
            print(f"   {member.name}: 모든 능력치 +20% (5분)")
        
        return True

    def _equipment_repair(self, party: PartyManager, caster: Character, target_type: str) -> bool:
        """장비 수리 필드 스킬 - 고급 장비일수록 수리량 감소"""
        print(f"{GREEN}🔧 {caster.name}이(가) 장비를 수리합니다!{RESET}")
        
        # 수리 가능한 장비가 있는 파티원 찾기
        repairable_members = []
        for member in party.get_alive_members():
            if hasattr(member, 'equipment') and member.equipment:
                for slot, equipment in member.equipment.items():
                    if equipment and hasattr(equipment, 'current_durability'):
                        if equipment.current_durability < equipment.max_durability:
                            repairable_members.append((member, slot, equipment))
        
        if not repairable_members:
            print(f"{BLUE}수리가 필요한 장비가 없습니다.{RESET}")
            return False
        
        if target_type == "ally":
            # 커서 시스템으로 장비 선택
            print(f"\n{YELLOW}⬆️⬇️ 방향키로 수리할 장비를 선택하세요 (Enter: 선택, ESC: 취소):{RESET}")
            
            selected_index = 0
            while True:
                # 화면 지우기 (간단한 방법)
                print("\033[H\033[J", end="")
                print(f"{YELLOW}⬆️⬇️ 방향키로 수리할 장비를 선택하세요 (Enter: 선택, ESC: 취소):{RESET}")
                
                for i, (member, slot, equipment) in enumerate(repairable_members):
                    durability_percent = int((equipment.current_durability / equipment.max_durability) * 100)
                    
                    # 희귀도별 수리 효율 계산
                    rarity_penalty = self._get_repair_efficiency(equipment)
                    
                    # 선택된 항목 강조
                    if i == selected_index:
                        print(f"{CYAN}>>> {member.name}의 {equipment.name} <<<{RESET}")
                        print(f"    내구도: {equipment.current_durability}/{equipment.max_durability} ({durability_percent}%)")
                        print(f"    수리 효율: {rarity_penalty*100:.0f}% ({equipment.rarity.value if hasattr(equipment, 'rarity') else '일반'})")
                    else:
                        print(f"    {member.name}의 {equipment.name}")
                        print(f"    내구도: {equipment.current_durability}/{equipment.max_durability} ({durability_percent}%)")
                
                # 간단한 입력 처리 (실제로는 키보드 입력 라이브러리 필요)
                try:
                    user_input = input(f"\n{CYAN}선택 (w/s: 이동, enter: 선택, q: 취소): {RESET}")
                    if user_input.lower() == 'w' and selected_index > 0:
                        selected_index -= 1
                    elif user_input.lower() == 's' and selected_index < len(repairable_members) - 1:
                        selected_index += 1
                    elif user_input == '' or user_input.lower() == 'enter':
                        break
                    elif user_input.lower() == 'q':
                        print(f"{RED}취소되었습니다.{RESET}")
                        return False
                except (KeyboardInterrupt, EOFError):
                    print(f"{RED}취소되었습니다.{RESET}")
                    return False
            
            member, slot, equipment = repairable_members[selected_index]
            
            # 희귀도별 수리 효율 적용
            repair_efficiency = self._get_repair_efficiency(equipment)
            base_repair = 50 + (caster.magic_attack // 2)
            actual_repair = int(base_repair * repair_efficiency)
            repair_amount = min(actual_repair, equipment.max_durability - equipment.current_durability)
            
            equipment.current_durability += repair_amount
            if equipment.current_durability >= equipment.max_durability:
                equipment.current_durability = equipment.max_durability
                equipment.is_broken = False
            
            print(f"{GREEN}✨ {equipment.name}을(를) {repair_amount}만큼 수리했습니다!{RESET}")
            print(f"   내구도: {equipment.current_durability}/{equipment.max_durability}")
            if repair_efficiency < 1.0:
                print(f"   {YELLOW}고급 장비로 인해 수리 효율이 {repair_efficiency*100:.0f}%로 감소했습니다.{RESET}")
            return True
        else:
            # 파티 전체 장비 수리 (낮은 수리량)
            repair_base = 8 + (caster.magic_attack // 8)
            repaired_items = []
            
            for member, slot, equipment in repairable_members:
                # 희귀도별 수리 효율 적용
                repair_efficiency = self._get_repair_efficiency(equipment)
                actual_repair_base = int(repair_base * repair_efficiency)
                repair_amount = min(actual_repair_base, equipment.max_durability - equipment.current_durability)
                
                equipment.current_durability += repair_amount
                if equipment.current_durability >= equipment.max_durability:
                    equipment.current_durability = equipment.max_durability
                    equipment.is_broken = False
                
                if repair_amount > 0:
                    efficiency_note = f" (효율 {repair_efficiency*100:.0f}%)" if repair_efficiency < 1.0 else ""
                    repaired_items.append(f"{member.name}의 {equipment.name}(+{repair_amount}){efficiency_note}")
            
            if repaired_items:
                print(f"{GREEN}🔧 파티 장비 수리 완료:{RESET}")
                for item in repaired_items:
                    print(f"   {item}")
                return True
            else:
                print(f"{BLUE}수리할 장비가 없었습니다.{RESET}")
                return False
    
    def _get_repair_efficiency(self, equipment) -> float:
        """희귀도별 수리 효율 반환 (고급 장비일수록 수리하기 어려움)"""
        if not hasattr(equipment, 'rarity'):
            return 1.0
        
        rarity_efficiency = {
            "일반": 1.0,      # 100% 효율
            "고급": 0.85,     # 85% 효율
            "희귀": 0.70,     # 70% 효율
            "영웅": 0.55,     # 55% 효율
            "전설": 0.40,     # 40% 효율
            "신화": 0.25,     # 25% 효율
            "유니크": 0.15    # 15% 효율
        }
        
        rarity_value = equipment.rarity.value if hasattr(equipment.rarity, 'value') else str(equipment.rarity)
        return rarity_efficiency.get(rarity_value, 1.0)

    def _durability_enhancement(self, party: PartyManager, caster: Character, target_type: str) -> bool:
        """내구도 강화 필드 스킬 - 일시적으로 최대 내구도 증가"""
        print(f"{YELLOW}✨ {caster.name}이(가) 장비에 보호 마법을 겁니다!{RESET}")
        
        # 강화 가능한 장비 찾기
        enhanceable_members = []
        for member in party.get_alive_members():
            if hasattr(member, 'equipment') and member.equipment:
                for slot, equipment in member.equipment.items():
                    if equipment and hasattr(equipment, 'max_durability'):
                        enhanceable_members.append((member, slot, equipment))
        
        if not enhanceable_members:
            print(f"{BLUE}강화할 장비가 없습니다.{RESET}")
            return False
        
        enhancement_value = 10 + (caster.magic_attack // 10)  # 마법 공격력에 따른 강화량
        
        if target_type == "ally":
            # 단일 대상 강화 (더 높은 강화량)
            print(f"\n{YELLOW}강화할 장비를 선택하세요:{RESET}")
            for i, (member, slot, equipment) in enumerate(enhanceable_members, 1):
                print(f"{WHITE}{i}. {member.name}의 {equipment.name}{RESET}")
                print(f"   최대 내구도: {equipment.max_durability}")
            
            try:
                choice = int(input(f"{CYAN}>>> {RESET}"))
                if 1 <= choice <= len(enhanceable_members):
                    member, slot, equipment = enhanceable_members[choice - 1]
                    
                    # 임시 강화 효과 부여 (전투 후 사라짐)
                    if not hasattr(equipment, 'temp_durability_bonus'):
                        equipment.temp_durability_bonus = 0
                    
                    bonus = enhancement_value * 2
                    equipment.temp_durability_bonus += bonus
                    equipment.max_durability += bonus
                    equipment.current_durability += bonus  # 현재 내구도도 증가
                    
                    print(f"{GREEN}✨ {equipment.name}의 최대 내구도가 {bonus}만큼 증가했습니다!{RESET}")
                    print(f"   새로운 내구도: {equipment.current_durability}/{equipment.max_durability}")
                    return True
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
                    return False
            except (ValueError, KeyboardInterrupt):
                print(f"{RED}취소되었습니다.{RESET}")
                return False
        else:
            # 파티 전체 강화
            enhanced_items = []
            for member, slot, equipment in enhanceable_members:
                if not hasattr(equipment, 'temp_durability_bonus'):
                    equipment.temp_durability_bonus = 0
                
                equipment.temp_durability_bonus += enhancement_value
                equipment.max_durability += enhancement_value
                equipment.current_durability += enhancement_value
                enhanced_items.append(f"{member.name}의 {equipment.name}(+{enhancement_value})")
            
            if enhanced_items:
                print(f"{GREEN}✨ 파티 장비 강화 완료:{RESET}")
                for item in enhanced_items:
                    print(f"   {item}")
                return True
            else:
                print(f"{BLUE}강화할 장비가 없었습니다.{RESET}")
                return False

    def _perfect_repair(self, party: PartyManager, caster: Character) -> bool:
        """완벽 수리 - 모든 장비를 최대 내구도로 복구"""
        print(f"{MAGENTA}🌟 {caster.name}이(가) 완벽한 수리 마법을 시전합니다!{RESET}")
        
        repaired_items = []
        for member in party.get_alive_members():
            if hasattr(member, 'equipment') and member.equipment:
                for slot, equipment in member.equipment.items():
                    if equipment and hasattr(equipment, 'current_durability'):
                        if equipment.current_durability < equipment.max_durability:
                            repair_amount = equipment.max_durability - equipment.current_durability
                            equipment.current_durability = equipment.max_durability
                            equipment.is_broken = False
                            repaired_items.append(f"{member.name}의 {equipment.name}(완전수리)")
        
        if repaired_items:
            print(f"{GREEN}🌟 완벽 수리 완료:{RESET}")
            for item in repaired_items:
                print(f"   {item}")
            return True
        else:
            print(f"{BLUE}수리가 필요한 장비가 없었습니다.{RESET}")
            return False

    def _durability_analysis(self, party: PartyManager, caster: Character) -> bool:
        """내구도 분석 - 고급 장비 정보와 수리 예측 제공 (MP 소모 크게 감소)"""
        print(f"{CYAN}🔍 {caster.name}이(가) 마법으로 장비 상태를 정밀 분석합니다!{RESET}")
        print("="*80)
        
        analysis_found = False
        total_repair_cost = 0
        critical_equipment = []
        
        for member in party.get_alive_members():
            member_has_equipment = False
            member_info = []
            
            if hasattr(member, 'equipment') and member.equipment:
                for slot, equipment in member.equipment.items():
                    if equipment and hasattr(equipment, 'current_durability'):
                        member_has_equipment = True
                        analysis_found = True
                        
                        durability_percent = int((equipment.current_durability / equipment.max_durability) * 100)
                        status_color = GREEN if durability_percent >= 80 else YELLOW if durability_percent >= 50 else RED
                        
                        # 내구도 상태 분석
                        if durability_percent >= 90:
                            condition = "완벽"
                            condition_icon = "💎"
                        elif durability_percent >= 70:
                            condition = "양호"
                            condition_icon = "✨"
                        elif durability_percent >= 40:
                            condition = "보통"
                            condition_icon = "🔧"
                        elif durability_percent >= 20:
                            condition = "나쁨"
                            condition_icon = "⚠️"
                        else:
                            condition = "위험"
                            condition_icon = "🚨"
                            critical_equipment.append(f"{member.name}의 {equipment.name}")
                        
                        # 희귀도별 수리 비용과 효율 계산
                        repair_needed = equipment.max_durability - equipment.current_durability
                        rarity_multiplier = self._get_repair_cost_multiplier(equipment)
                        estimated_cost = int(repair_needed * 3 * rarity_multiplier)  # 상인 수리비 예측
                        repair_efficiency = self._get_repair_efficiency(equipment)
                        total_repair_cost += estimated_cost
                        
                        # 장비 희귀도 정보
                        rarity_info = ""
                        if hasattr(equipment, 'rarity'):
                            rarity_value = equipment.rarity.value if hasattr(equipment.rarity, 'value') else str(equipment.rarity)
                            rarity_color = self._get_rarity_color(rarity_value)
                            rarity_info = f" ({rarity_color}{rarity_value}{RESET})"
                        
                        member_info.append(f"   {condition_icon} {slot}: {equipment.name}{rarity_info}")
                        member_info.append(f"      내구도: {status_color}{equipment.current_durability}/{equipment.max_durability} ({durability_percent}%){RESET}")
                        member_info.append(f"      상태: {condition}")
                        member_info.append(f"      상인 수리비: {estimated_cost}G | 필드수리 효율: {repair_efficiency*100:.0f}%")
                        
                        # 특수 분석 정보
                        if hasattr(equipment, 'temp_durability_bonus') and equipment.temp_durability_bonus > 0:
                            member_info.append(f"      {CYAN}✨ 임시 강화: +{equipment.temp_durability_bonus} 내구도{RESET}")
                        
                        if equipment.is_broken:
                            member_info.append(f"      {RED}💀 파괴된 상태! 즉시 수리 필요{RESET}")
                        
                        # 내구도 예측 (다음 전투 후)
                        predicted_loss = self._predict_durability_loss(equipment)
                        if predicted_loss > 0:
                            predicted_durability = max(0, equipment.current_durability - predicted_loss)
                            predicted_percent = int((predicted_durability / equipment.max_durability) * 100)
                            member_info.append(f"      📊 전투 후 예측: {predicted_durability}/{equipment.max_durability} ({predicted_percent}%)")
            
            if member_has_equipment:
                print(f"\n{WHITE}📋 {member.name}의 장비 분석 결과:{RESET}")
                for info in member_info:
                    print(info)
        
        if analysis_found:
            print(f"\n{CYAN}📊 종합 분석 결과:{RESET}")
            print(f"   💰 총 예상 수리비: {total_repair_cost}G")
            print(f"   📈 파티 골드: {getattr(party, 'gold', 0)}G")
            
            if critical_equipment:
                print(f"\n{RED}🚨 즉시 수리 권장:{RESET}")
                for equipment in critical_equipment:
                    print(f"   ⚠️ {equipment}")
            
            # 수리 우선순위 제안
            print(f"\n{YELLOW}💡 수리 우선순위 제안:{RESET}")
            print(f"   1. 파괴된 장비 (성능 0%)")
            print(f"   2. 위험 상태 장비 (성능 50%)")
            print(f"   3. 고급 장비 (수리 효율 낮음)")
            
            return True
        else:
            print(f"{BLUE}분석할 장비가 없습니다.{RESET}")
            return False
    
    def _get_repair_cost_multiplier(self, equipment) -> float:
        """희귀도별 수리 비용 배수 반환"""
        if not hasattr(equipment, 'rarity'):
            return 1.0
        
        rarity_cost = {
            "일반": 1.0,
            "고급": 1.5,
            "희귀": 2.0,
            "영웅": 3.0,
            "전설": 4.5,
            "신화": 6.0,
            "유니크": 8.0
        }
        
        rarity_value = equipment.rarity.value if hasattr(equipment.rarity, 'value') else str(equipment.rarity)
        return rarity_cost.get(rarity_value, 1.0)
    
    def _get_rarity_color(self, rarity: str) -> str:
        """희귀도별 색상 반환"""
        colors = {
            "일반": WHITE,
            "고급": GREEN,
            "희귀": BLUE,
            "영웅": MAGENTA,
            "전설": YELLOW,
            "신화": RED,
            "유니크": CYAN
        }
        return colors.get(rarity, WHITE)
    
    def _predict_durability_loss(self, equipment) -> int:
        """다음 전투에서 예상되는 내구도 손실 계산"""
        # 기본 예상 손실량 (평균적인 전투 기준)
        base_loss = 3
        
        # 희귀도별 손실 증가 (고급 장비일수록 더 손실)
        if hasattr(equipment, 'rarity'):
            rarity_loss = {
                "일반": 1.0,
                "고급": 1.2,
                "희귀": 1.4,
                "영웅": 1.6,
                "전설": 1.8,
                "신화": 2.0,
                "유니크": 2.2
            }
            
            rarity_value = equipment.rarity.value if hasattr(equipment.rarity, 'value') else str(equipment.rarity)
            multiplier = rarity_loss.get(rarity_value, 1.0)
            return int(base_loss * multiplier)
        
        return base_loss
        
        return base_loss

    def _equipment_protection(self, party: PartyManager, caster: Character, target_type: str) -> bool:
        
        return True

    def _equipment_protection(self, party: PartyManager, caster: Character) -> bool:
        """장비 보호 - 일정 시간 동안 내구도 감소 방지"""
        print(f"{BLUE}🛡️ {caster.name}이(가) 보호 마법을 시전합니다!{RESET}")
        
        protected_items = []
        for member in party.get_alive_members():
            if hasattr(member, 'equipment') and member.equipment:
                for slot, equipment in member.equipment.items():
                    if equipment:
                        # 보호 효과 부여 (내구도 감소 면역)
                        if not hasattr(equipment, 'protection_turns'):
                            equipment.protection_turns = 0
                        
                        protection_duration = 5 + (caster.magic_attack // 15)  # 마법 공격력에 따른 지속시간
                        equipment.protection_turns = max(equipment.protection_turns, protection_duration)
                        protected_items.append(f"{member.name}의 {equipment.name}")
        
        if protected_items:
            print(f"{GREEN}🛡️ 장비 보호 완료 ({5 + (caster.magic_attack // 15)}턴):{RESET}")
            for item in protected_items:
                print(f"   {item}")
            print(f"{BLUE}💡 보호된 장비는 일정 시간 동안 내구도가 감소하지 않습니다!{RESET}")
            return True
        else:
            print(f"{BLUE}보호할 장비가 없었습니다.{RESET}")
            return False

# 전역 필드 스킬 시스템 인스턴스
field_skill_system = FieldSkillSystem()

def get_field_skill_system() -> FieldSkillSystem:
    """필드 스킬 시스템 반환"""
    return field_skill_system
