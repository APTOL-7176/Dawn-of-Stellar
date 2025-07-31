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
        """시전자 선택하고 스킬 사용"""
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
        """시전자 선택 후 스킬 실행"""
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

# 전역 필드 스킬 시스템 인스턴스
field_skill_system = FieldSkillSystem()

def get_field_skill_system() -> FieldSkillSystem:
    """필드 스킬 시스템 반환"""
    return field_skill_system
