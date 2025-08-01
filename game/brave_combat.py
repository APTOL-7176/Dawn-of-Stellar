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
from .display import GameDisplay

class StatusEffect:
    """상태이상 효과"""
    def __init__(self, status_type: StatusType, duration: int, intensity: float = 1.0):
        self.status_type = status_type
        self.duration = duration
        self.intensity = intensity


class BraveCombatSystem:
    """Brave 기반 전투 시스템"""
    
    def __init__(self, audio_system=None, sound_manager=None):
        self.brave_manager = BraveManager()
        self.visualizer = get_combat_visualizer()
        self.stable_display = get_stable_display()  # 안정적인 출력 시스템 추가
        self.display = GameDisplay()  # GameDisplay 객체 추가
        self.turn_order = []
        self.keyboard = KeyboardInput()  # 키보드 입력 처리
        self.current_turn = 0
        
        # 오디오 시스템
        self.audio_system = audio_system
        self.sound_manager = sound_manager
        
        # 🔊 오디오 시스템 진단
        print(f"🎵 오디오 시스템 진단:")
        print(f"  - audio_system: {type(self.audio_system).__name__ if self.audio_system else 'None'}")
        print(f"  - sound_manager: {type(self.sound_manager).__name__ if self.sound_manager else 'None'}")
        
        # 스킬 시스템 추가
        self.skill_db = skill_system
    
    
    def get_brave_color_emoji(self, brave_points: int) -> str:
        """Brave 포인트에 따른 통일된 이모지 반환"""
        return "⚡"  # 모든 Brave 포인트에 동일 이모지 사용
        
    def start_battle(self, party: List[Character], enemies: List[Character]):
        """전투 시작"""
        # 🔊 전투 진입 SFX 재생
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("battle_start")  # 전투 진입 효과음
                print("🔊 전투 진입!")
            elif hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.play_sfx("battle_start")
                print("🔊 전투 진입!")
        except Exception as e:
            print(f"⚠️ 전투 진입 SFX 재생 실패: {e}")
        
        # 🎵 전투 BGM 재생
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_bgm("battle", loop=True)
                print("🎵 전투 BGM 시작!")
            elif hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.play_bgm("battle")
                print("🎵 전투 BGM 시작!")
        except Exception as e:
            print(f"⚠️ 전투 BGM 재생 실패: {e}")
        
        print("\n" + "="*80)
        print("🌟 Dawn Of Stellar - Brave Battle! 🌟")
        print("="*80)
        
        # 모든 참전자의 ATB 게이지 초기화
        all_combatants = party + enemies
        for combatant in all_combatants:
            # dict 객체인 경우 Character 객체로 변환 필요
            if isinstance(combatant, dict):
                print(f"⚠️ 경고: {combatant}는 dict 객체입니다. Character 객체가 아닙니다.")
                continue
            if hasattr(combatant, 'atb_gauge'):
                combatant.atb_gauge = 0
            else:
                print(f"⚠️ 경고: {combatant}에 atb_gauge 속성이 없습니다.")
        
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
        
        # 승리 시에는 BGM이 이미 재생되고 있으므로 바로 복구하지 않음
        # 패배 시에만 즉시 BGM 복구
        if not battle_result:  # 패배 시에만
            # 🎵 전투 종료 후 BGM 복구
            try:
                if hasattr(self, 'audio_system') and self.audio_system:
                    self.audio_system.play_bgm("dungeon", loop=True)
                    print("🎵 던전 BGM으로 복귀!")
                elif hasattr(self, 'sound_manager') and self.sound_manager:
                    self.sound_manager.play_bgm("dungeon")
                    print("🎵 던전 BGM으로 복귀!")
            except Exception as e:
                print(f"⚠️ 던전 BGM 복구 실패: {e}")
        
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
                    # 🎵 승리 시 즉시 BGM 재생
                    if result:  # 승리 시
                        try:
                            if hasattr(self, 'audio_system') and self.audio_system:
                                from .audio_system import BGMType
                                self.audio_system.play_bgm(BGMType.VICTORY)
                                print("🎵 승리 BGM 재생 시작!")
                            elif hasattr(self, 'sound_manager') and self.sound_manager:
                                self.sound_manager.play_bgm("victory")
                                print("🎵 승리 BGM 재생 시작!")
                        except Exception as e:
                            print(f"⚠️ 승리 BGM 재생 실패: {e}")
                    
                    print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                    return result
            else:
                result = self.enemy_turn(character, party, enemies)
                if result is not None:  # 전투 종료 신호
                    # 🎵 승리 시 즉시 BGM 재생
                    if result:  # 승리 시
                        try:
                            if hasattr(self, 'audio_system') and self.audio_system:
                                from .audio_system import BGMType
                                self.audio_system.play_bgm(BGMType.VICTORY)
                                print("🎵 승리 BGM 재생 시작!")
                            elif hasattr(self, 'sound_manager') and self.sound_manager:
                                self.sound_manager.play_bgm("victory")
                                print("🎵 승리 BGM 재생 시작!")
                        except Exception as e:
                            print(f"⚠️ 승리 BGM 재생 실패: {e}")
                    
                    print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                    return result
                
            # 상태이상 턴 종료 처리
            if hasattr(character, 'status_manager'):
                character.status_manager.process_turn_effects()
                
            # 전투 종료 조건 확인
            if self.check_battle_end(party, enemies):
                result = self.determine_winner(party, enemies)
                print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                
                # 🎵 승리 팡파레 재생 (1회만)
                try:
                    if result:  # 승리 시
                        if hasattr(self, 'audio_system') and self.audio_system:
                            # SFX로 팡파레 1회 재생
                            self.audio_system.play_sfx("victory")
                            print("🎵 승리 팡파레 재생!")
                        elif hasattr(self, 'sound_manager') and self.sound_manager:
                            # 폴백: SFX 재생 시도
                            self.sound_manager.play_sfx("victory")
                            print("🎵 승리 팡파레 재생!")
                except Exception as e:
                    print(f"⚠️ 승리 팡파레 재생 실패: {e}")
                
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
                print(f"🔄 {character.name}의 BRV가 INT BRV {recovered}로 회복되었습니다!")
            
        combat_animator.show_turn_indicator(character.name)
        self.show_battle_status(character, party, enemies)
        
        # 캐릭터 특성 쿨다운과 지속효과 업데이트
        if hasattr(character, 'traits'):
            for trait in character.traits:
                trait.update_cooldown()
                if hasattr(trait, 'update_duration_effects'):
                    effects = trait.update_duration_effects(character)
                    for effect in effects:
                        print(f"✨ {effect}")
        
        # 현재 차례 안내
        print(f"\n{Color.BRIGHT_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}👉 {character.name}의 차례 - 행동을 선택하세요{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.RESET}")
        
        while True:
            try:
                from .cursor_menu_system import create_simple_menu
                
                action_options = ["⚔️ Brave 공격", "💀 HP 공격", "✨ 스킬 사용", "🧪 아이템 사용", "🛡️ 방어", "🌟 특성 활성화", "📊 실시간 상태", "❓ 전투 도움말"]
                action_descriptions = [
                    "Brave를 높여 강력한 공격을 준비합니다",
                    "축적된 Brave로 적에게 데미지를 줍니다",
                    "캐릭터의 특수 스킬을 사용합니다",
                    "회복 아이템이나 버프 아이템을 사용합니다",
                    "방어 태세로 받는 피해를 줄입니다",
                    "액티브 특성을 활성화합니다",
                    "현재 전투 상황을 자세히 확인합니다",
                    "전투 시스템에 대한 도움말을 봅니다"
                ]
                
                # 파티 상태를 문자열로 생성
                party_status = self._get_party_status_string(character, party, enemies)
                
                # 상태창과 메뉴를 통합하여 표시
                action_menu = create_simple_menu(
                    f"🎮 {character.name}의 행동", 
                    action_options, 
                    action_descriptions, 
                    clear_screen=True,
                    extra_content=party_status
                )
                choice = action_menu.run()
                
                if choice == 0:  # Brave 공격
                    if self.brave_attack_menu(character, enemies):
                        break
                elif choice == 1:  # HP 공격
                    if self.hp_attack_menu(character, enemies):
                        break
                elif choice == 2:  # 스킬 사용
                    if self.skill_menu(character, party, enemies):
                        break
                elif choice == 3:  # 아이템 사용
                    if self.item_menu(character, party):
                        break
                elif choice == 4:  # 방어
                    self.defend_action(character)
                    break
                elif choice == 5:  # 특성 활성화
                    if self.trait_activation_menu(character):
                        break
                elif choice == 6:  # 실시간 상태
                    self.show_detailed_combat_status(character, party, enemies)
                    # 상태 조회 후 다시 전투 화면 표시
                    self.show_battle_status(character, party, enemies)
                    input("\n계속하려면 Enter를 누르세요...")
                elif choice == 7:  # 전투 도움말
                    from .tutorial import show_combat_help
                    show_combat_help()
                elif choice is None:  # 취소
                    continue
                else:
                    print("잘못된 선택입니다.")
                    
            except ImportError:
                # 폴백: 기존 방식
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
                
    def trait_activation_menu(self, character: Character) -> bool:
        """특성 활성화 메뉴"""
        if not hasattr(character, 'active_traits') or not character.active_traits:
            print(f"\n❌ {character.name}은(는) 활성화할 수 있는 특성이 없습니다.")
            input("아무 키나 눌러 계속...")
            return False
        
        # 액티브 타입 특성만 필터링
        active_traits = []
        for trait in character.active_traits:
            if hasattr(trait, 'trait_type') and trait.trait_type == "active":
                active_traits.append(trait)
            elif isinstance(trait, dict) and trait.get('trait_type') == "active":
                active_traits.append(trait)
        
        if not active_traits:
            print(f"\n❌ {character.name}은(는) 활성화할 수 있는 액티브 특성이 없습니다.")
            print(f"💡 패시브 특성은 항상 활성화되어 있습니다.")
            input("아무 키나 눌러 계속...")
            return False
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            trait_options = []
            trait_descriptions = []
            
            for trait in active_traits:
                if hasattr(trait, 'name'):
                    trait_name = trait.name
                    trait_desc = getattr(trait, 'description', '특수 효과')
                else:
                    trait_name = trait.get('name', '알 수 없는 특성')
                    trait_desc = trait.get('description', '특수 효과')
                
                # 특성이 이미 활성화되어 있는지 체크
                is_active = False
                if hasattr(trait, 'is_active'):
                    is_active = trait.is_active
                elif isinstance(trait, dict):
                    is_active = trait.get('is_active', False)
                
                if is_active:
                    trait_options.append(f"🟢 {trait_name} (활성화됨)")
                    trait_descriptions.append(f"{trait_desc} - 이미 활성화된 상태")
                else:
                    trait_options.append(f"⚪ {trait_name}")
                    trait_descriptions.append(f"{trait_desc} - 클릭하여 활성화")
            
            menu = create_simple_menu(f"🌟 {character.name}의 특성 활성화", trait_options, trait_descriptions, clear_screen=False)
            choice = menu.run()
            
            if choice is None or choice == -1:  # 취소
                return False
            elif 0 <= choice < len(active_traits):
                selected_trait = active_traits[choice]
                
                # 특성이 이미 활성화되어 있는지 체크
                is_active = False
                if hasattr(selected_trait, 'is_active'):
                    is_active = selected_trait.is_active
                elif isinstance(selected_trait, dict):
                    is_active = selected_trait.get('is_active', False)
                
                if is_active:
                    print(f"💡 {selected_trait.get('name', selected_trait.name)}은(는) 이미 활성화되어 있습니다.")
                    return False
                else:
                    # 특성 활성화
                    if hasattr(selected_trait, 'is_active'):
                        selected_trait.is_active = True
                    elif isinstance(selected_trait, dict):
                        selected_trait['is_active'] = True
                    
                    trait_name = selected_trait.get('name', selected_trait.name) if isinstance(selected_trait, dict) else selected_trait.name
                    print(f"✨ {character.name}이(가) '{trait_name}' 특성을 활성화했습니다!")
                    
                    # 특성별 특수 효과 적용
                    self._apply_trait_activation_effect(character, selected_trait)
                    
                    return True
            else:
                print("잘못된 선택입니다.")
                return False
                
        except Exception as e:
            print(f"❌ 특성 활성화 오류: {e}")
            return False
    
    def _apply_trait_activation_effect(self, character: Character, trait):
        """특성 활성화 효과 적용"""
        trait_name = trait.get('name') if isinstance(trait, dict) else trait.name
        
        if trait_name == "동물 변신":
            # 동물 변신 특성 - 형태 선택
            forms = ["🐺 늑대 (공격+30%)", "🐻 곰 (방어+30%)", "🦅 독수리 (회피+25%)"]
            form_descriptions = [
                "공격력이 30% 증가합니다",
                "방어력이 30% 증가합니다", 
                "회피율이 25% 증가합니다"
            ]
            
            try:
                from .cursor_menu_system import create_simple_menu
                form_menu = create_simple_menu(f"🌟 {character.name}의 변신 형태 선택", forms, form_descriptions, clear_screen=False)
                form_choice = form_menu.run()
                
                if form_choice == 0:  # 늑대
                    character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + int(character.physical_attack * 0.3)
                    print(f"🐺 {character.name}이(가) 늑대로 변신했습니다! 공격력이 증가합니다!")
                elif form_choice == 1:  # 곰
                    character.temp_defense_bonus = getattr(character, 'temp_defense_bonus', 0) + int(character.physical_defense * 0.3)
                    print(f"🐻 {character.name}이(가) 곰으로 변신했습니다! 방어력이 증가합니다!")
                elif form_choice == 2:  # 독수리
                    character.temp_dodge_bonus = getattr(character, 'temp_dodge_bonus', 0) + 25
                    print(f"🦅 {character.name}이(가) 독수리로 변신했습니다! 회피율이 증가합니다!")
                    
            except ImportError:
                # 폴백: 자동으로 늑대 형태
                character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + int(character.physical_attack * 0.3)
                print(f"🐺 {character.name}이(가) 늑대로 변신했습니다! 공격력이 증가합니다!")
        
        else:
            # 다른 특성들의 기본 효과
            print(f"✨ {trait_name} 특성 효과가 적용되었습니다!")
    
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

        try:
            from .cursor_menu_system import create_simple_menu
            
            # 스킬 옵션과 설명 준비
            skill_options = []
            skill_descriptions = []
            available_skills = []
            
            for skill in skills:
                mp_cost = skill.get("mp_cost", 0)
                cast_time = skill.get("cast_time", 0)
                cast_info = f" [캐스트:{cast_time}%]" if cast_time > 0 else ""
                skill_name = skill.get('name', '스킬')
                
                if character.current_mp >= mp_cost:
                    skill_options.append(f"✨ {skill_name} (MP:{mp_cost}){cast_info}")
                    skill_descriptions.append(skill.get('description', ''))
                    available_skills.append(skill)
                else:
                    skill_options.append(f"🚫 {skill_name} (MP:{mp_cost}){cast_info} [MP 부족]")
                    skill_descriptions.append(f"{skill.get('description', '')} - MP 부족")
                    available_skills.append(None)  # 사용 불가능한 스킬
            
            if not any(skill for skill in available_skills if skill is not None):
                print("사용 가능한 스킬이 없습니다. 방어를 선택합니다.")
                self.defend_action(character)
                return True
            
            menu = create_simple_menu(
                f"✨ {character.name}의 스킬 선택", 
                skill_options, 
                skill_descriptions, 
                clear_screen=True
            )
            choice = menu.run()
            
            if choice is None or choice == -1:  # 취소
                return False
            elif 0 <= choice < len(available_skills):
                selected_skill = available_skills[choice]
                
                if selected_skill is None:  # MP 부족한 스킬 선택
                    print(f"MP가 부족합니다!")
                    return False
                
                # 대상 선택
                targets = self._select_skill_targets(selected_skill, character, party, enemies)
                if targets is None:
                    return False  # 취소된 경우
                
                # 스킬 실행 - 실제 효과 적용
                # MP 소모
                character.current_mp -= selected_skill.get("mp_cost", 0)
                
                # 실제 스킬 효과 적용
                print(f"✨ {character.name}이(가) {selected_skill.get('name', '스킬')}을(를) 사용했습니다!")
                
                # 🔊 스킬 사용 SFX 재생
                self._play_skill_sfx(selected_skill)
                
                # 시각 효과
                if hasattr(self, 'visualizer') and self.visualizer:
                    self.visualizer.show_skill_effect(character, selected_skill.get('name', '스킬'), EffectType.SKILL)
                
                # 실제 스킬 효과 적용
                self._apply_skill_effects(selected_skill, character, targets)
                
                return True
            else:
                print("잘못된 선택입니다.")
                return False
                
        except Exception as e:
            print(f"❌ 스킬 메뉴 오류: {e}")
            # 폴백: 방어 선택
            self.defend_action(character)
            return True
    
    def _select_skill_targets(self, skill, caster, party: List[Character], enemies: List[Character]):
        """스킬 대상 선택"""
        target_type = skill.get("target", "single_enemy")
        
        # TargetType enum을 문자열로 변환
        if hasattr(target_type, 'value'):
            target_type_str = target_type.value
        else:
            target_type_str = str(target_type).lower()
        
        # 타겟 타입별 처리
        if target_type_str in ["자신", "self"]:
            return [caster]
        elif target_type_str in ["아군전체", "all_allies"]:
            return [char for char in party if char.is_alive]
        elif target_type_str in ["적전체", "all_enemies"]:
            return [enemy for enemy in enemies if enemy.is_alive]
        elif target_type_str in ["아군1명", "single_ally"]:
            alive_allies = [char for char in party if char.is_alive]
            if not alive_allies:
                return []
            
            try:
                from .cursor_menu_system import create_simple_menu
                
                options = []
                descriptions = []
                
                for ally in alive_allies:
                    status = ""
                    if ally.current_hp < ally.max_hp:
                        status += f" (HP: {ally.current_hp}/{ally.max_hp})"
                    if hasattr(ally, 'wounds') and ally.wounds > 0:
                        status += f" [상처: {ally.wounds}]"
                    
                    option_text = f"{ally.name}{status}"
                    desc = f"레벨: {ally.level} | 클래스: {ally.character_class}"
                    
                    options.append(option_text)
                    descriptions.append(desc)
                
                menu = create_simple_menu("🎯 스킬 대상 선택", options, descriptions, clear_screen=True)
                result = menu.run()
                
                if result == -1:  # 취소
                    return None
                
                if 0 <= result < len(alive_allies):
                    return [alive_allies[result]]
                
                return None
                
            except ImportError:
                # 폴백: 기존 방식
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
                
        elif target_type_str in ["적1명", "single_enemy"]:
            alive_enemies = [enemy for enemy in enemies if enemy.is_alive]
            if not alive_enemies:
                return []
            
            try:
                from .cursor_menu_system import create_simple_menu
                
                options = []
                descriptions = []
                
                for enemy in alive_enemies:
                    status = f" (HP: {enemy.current_hp}/{enemy.max_hp}"
                    if hasattr(enemy, 'is_broken') and enemy.is_broken:
                        status += ", BREAK"
                    status += ")"
                    
                    option_text = f"{enemy.name}{status}"
                    desc = f"상태: {'브레이크' if hasattr(enemy, 'is_broken') and enemy.is_broken else '정상'}"
                    
                    options.append(option_text)
                    descriptions.append(desc)
                
                menu = create_simple_menu("⚔️ 공격 대상 선택", options, descriptions, clear_screen=True)
                result = menu.run()
                
                if result == -1:  # 취소
                    return None
                
                if 0 <= result < len(alive_enemies):
                    return [alive_enemies[result]]
                
                return None
                
            except ImportError:
                # 폴백: 기존 방식
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
        elif target_type_str in ["죽은아군1명", "dead_ally"]:
            dead_allies = [char for char in party if not char.is_alive]
            if not dead_allies:
                print("부활시킬 대상이 없습니다.")
                return []
            
            print("\n부활시킬 대상을 선택하세요:")
            for i, ally in enumerate(dead_allies, 1):
                print(f"{i}. {ally.name} (사망)")
            print("0. 취소")
            
            try:
                choice_str = self.keyboard.get_key()
                choice = int(choice_str) - 1
                if choice == -1:
                    return None
                elif 0 <= choice < len(dead_allies):
                    return [dead_allies[choice]]
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
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            options = []
            descriptions = []
            
            for item, quantity in available_items:
                effect_desc = item.get_effect_description() if hasattr(item, 'get_effect_description') else item.description
                option_text = f"{item.name} ({quantity}개)"
                desc_text = f"{effect_desc}"
                if hasattr(item, 'value') and item.value > 0:
                    desc_text += f" | 가치: {item.value}골드"
                
                options.append(option_text)
                descriptions.append(desc_text)
            
            menu = create_simple_menu("⚔️ 전투 아이템 사용", options, descriptions, clear_screen=True)
            choice = menu.run()
            
            if choice == -1:  # 취소
                return False
            
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
            
            return False
            
        except ImportError:
            # 폴백: 기존 방식
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
        """부활 대상 선택 - 커서 방식"""
        dead_party = [p for p in party if not p.is_alive]
        if not dead_party:
            print("부활시킬 수 있는 캐릭터가 없습니다.")
            return None
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            options = []
            descriptions = []
            
            for member in dead_party:
                option_text = f"{member.name} (사망 상태)"
                desc = f"레벨: {member.level} | 클래스: {member.character_class}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("💀 부활 대상 선택", options, descriptions, clear_screen=True)
            result = menu.run()
            
            if result == -1:  # 취소
                return None
            
            if 0 <= result < len(dead_party):
                return dead_party[result]
            
            return None
            
        except ImportError:
            # 폴백: 기존 방식
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
        """치료 대상 선택 - 커서 방식"""
        alive_party = [p for p in party if p.is_alive]
        if not alive_party:
            return None
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            options = []
            descriptions = []
            
            for member in alive_party:
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                status = "양호" if hp_ratio > 0.7 else "부상" if hp_ratio > 0.3 else "위험"
                
                option_text = f"{member.name} (HP: {member.current_hp}/{member.max_hp})"
                desc = f"상태: {status} | HP: {hp_ratio:.1%}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("🎯 치료 대상 선택", options, descriptions, clear_screen=True)
            result = menu.run()
            
            if result == -1:  # 취소
                return None
            
            if 0 <= result < len(alive_party):
                return alive_party[result]
            
            return None
            
        except ImportError:
            # 폴백: 기존 방식
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
            
        try:
            from .cursor_menu_system import create_simple_menu
            
            options = []
            descriptions = []
            
            for enemy in alive_enemies:
                option_text = f"{enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp}, Brave: {enemy.brave_points})"
                desc = f"대상: {enemy.name} | 상태: {'브레이크' if hasattr(enemy, 'is_broken') and enemy.is_broken else '정상'}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("⚔️ Brave 공격 대상 선택", options, descriptions, clear_screen=True)
            result = menu.run()
            
            if result is not None and 0 <= result < len(alive_enemies):
                target = alive_enemies[result]
                self.execute_brave_attack(attacker, target)
                return True
            return False
            
        except ImportError:
            # 폴백: 기존 방식
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
    
    def _create_colored_hp_gauge(self, current_hp: int, max_hp: int, gauge_length: int = 10) -> str:
        """색깔이 있는 HP 게이지 생성"""
        if max_hp <= 0:
            return "[__________]"
        
        hp_ratio = current_hp / max_hp
        filled_length = int(hp_ratio * gauge_length)
        empty_length = gauge_length - filled_length
        
        # HP 비율에 따른 색깔 결정
        if hp_ratio > 0.7:
            color = Color.BRIGHT_GREEN  # 70% 이상: 초록색
        elif hp_ratio > 0.3:
            color = Color.BRIGHT_YELLOW  # 30-70%: 노란색
        else:
            color = Color.BRIGHT_RED  # 30% 미만: 빨간색
        
        # 게이지 생성
        filled_bar = "█" * filled_length
        empty_bar = "░" * empty_length
        
        return f"[{color}{filled_bar}{Color.RESET}{empty_bar}]"
        
    def hp_attack_menu(self, attacker: Character, enemies: List[Character]) -> bool:
        """HP 공격 메뉴"""
        if attacker.brave_points <= 300:  # 500 → 300으로 감소
            print("Brave 포인트가 부족합니다! (최소 300 필요)")
            return False
            
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return False
            
        try:
            from .cursor_menu_system import create_simple_menu
            
            options = []
            descriptions = []
            
            for enemy in alive_enemies:
                # HP 게이지 색깔 생성
                hp_gauge = self._create_colored_hp_gauge(enemy.current_hp, enemy.max_hp)
                break_status = " [BREAK]" if (hasattr(enemy, 'is_broken') and enemy.is_broken) else ""
                option_text = f"{enemy.name} {hp_gauge}{break_status}"
                desc = f"대상: {enemy.name} | HP: {enemy.current_hp}/{enemy.max_hp} | 상태: {'브레이크' if hasattr(enemy, 'is_broken') and enemy.is_broken else '정상'}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("💀 HP 공격 대상 선택", options, descriptions, clear_screen=True)
            result = menu.run()
            
            if result is not None and 0 <= result < len(alive_enemies):
                target = alive_enemies[result]
                self.execute_hp_attack(attacker, target)
                return True
            return False
            
        except ImportError:
            # 폴백: 기존 방식
            print("\n대상을 선택하세요:")
            for i, enemy in enumerate(alive_enemies, 1):
                hp_gauge = self._create_colored_hp_gauge(enemy.current_hp, enemy.max_hp)
                break_status = " [BREAK]" if (hasattr(enemy, 'is_broken') and enemy.is_broken) else ""
                print(f"{i}. {enemy.name} {hp_gauge}{break_status}")
                
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
        if hasattr(self, 'visualizer') and self.visualizer:
            self.visualizer.show_skill_effect(attacker, skill.name, EffectType.SKILL)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("skill", skill_name=skill.name, character_name=attacker.name)
        
        # 회피 체크 먼저 수행
        if self._check_dodge(attacker, target):
            # 회피 SFX 재생
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("dodge")
            elif hasattr(self, 'sound_manager'):
                self.sound_manager.play_sfx("dodge")
            
            # 회피 비주얼 이펙트 (이곳에서만 메시지 출력)
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.show_miss_effect(attacker, target)
            enhanced_battle_effect("dodge", character_name=target.name)
            return
        
        # 데미지 계산
        brave_damage = self.brave_manager.calculate_brave_damage(attacker, target, skill)
        
        # BRV 피해량 3배 증가 (전투 속도 개선)
        brave_damage = int(brave_damage * 3.0)
        
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
            print(f"💥 치명타! {attacker.name}")
            
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
        if hasattr(self, 'visualizer') and self.visualizer:
            self.visualizer.show_skill_effect(attacker, skill.name, EffectType.SKILL)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("skill", skill_name=skill.name, character_name=attacker.name)
        
        # 회피 체크 먼저 수행
        if self._check_dodge(attacker, target):
            # 회피 SFX 재생
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("dodge")
            elif hasattr(self, 'sound_manager'):
                self.sound_manager.play_sfx("dodge")
            
            # 회피 비주얼 이펙트 (이곳에서만 메시지 출력)
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.show_miss_effect(attacker, target)
            enhanced_battle_effect("dodge", character_name=target.name)
            return
        
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
            print("💥 치명타! Break 상태로 데미지 증가!")
            
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
        
        print(f"💫 {attacker.name}의 Brave 포인트: {old_brave} → 0 (HP 공격으로 소모)")
        
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
                print(f"🔄 {enemy.name}의 BRV가 INT BRV {recovered}로 회복되었습니다!")
            
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
        """전투 상황 표시 - 더욱 이쁘고 깔끔한 디자인"""
        # 화면 클리어
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"\n{Color.BRIGHT_CYAN}{'─'*78}{Color.RESET}")
        print(f"{Color.BRIGHT_WHITE}⚔️ DAWN OF STELLAR - BRAVE BATTLE ⚔️{Color.RESET}")
        print(f"{Color.BRIGHT_YELLOW}현재 차례: {current_char.name}{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'─'*78}{Color.RESET}")
        
        # 파티 상태 표시
        print(f"\n{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        print(f"{Color.BRIGHT_WHITE}🛡️  아군 파티 상태{Color.RESET}")
        print(f"{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        
        for i, member in enumerate(party, 1):
            if member.is_alive:
                # 현재 턴 캐릭터 강조
                name_color = Color.BRIGHT_CYAN if member == current_char else Color.WHITE
                status_icon = "▶" if member == current_char else " "
                
                # HP 상태 색상과 바
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                if hp_ratio > 0.7:
                    hp_color = Color.BRIGHT_GREEN
                    hp_icon = "💚"
                elif hp_ratio > 0.4:
                    hp_color = Color.YELLOW
                    hp_icon = "💛"
                elif hp_ratio > 0.15:
                    hp_color = Color.BRIGHT_RED
                    hp_icon = "🧡"
                else:
                    hp_color = Color.RED
                    hp_icon = "❤️"
                
                # MP 상태 색상과 바
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                if mp_ratio > 0.5:
                    mp_color = Color.BRIGHT_BLUE
                    mp_icon = "💙"
                elif mp_ratio > 0.2:
                    mp_color = Color.BLUE
                    mp_icon = "💜"
                else:
                    mp_color = Color.BRIGHT_BLACK
                    mp_icon = "🤍"
                
                # ATB 게이지 - 더 이쁜 디자인
                atb_gauge = getattr(member, 'atb_gauge', 0)
                if atb_gauge >= 100:
                    atb_display = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
                    atb_bar = f"{Color.BRIGHT_CYAN}{'▰'*10} {Color.RESET}"
                    atb_icon = "⏳"
                else:
                    atb_percent = int(atb_gauge)
                    atb_display = f"{Color.CYAN}{atb_percent:3}%{Color.RESET}"
                    filled = int(atb_gauge / 10)
                    atb_bar = f"{Color.CYAN}{'▰'*filled}{Color.BRIGHT_BLACK}{'▱'*(10-filled)} {Color.RESET}"
                    atb_icon = "⏳" if atb_gauge < 50 else "⏳"
                
                # 레벨과 클래스 아이콘
                level_display = f"Lv.{getattr(member, 'level', 1):2}"
                character_class = getattr(member, 'character_class', '모험가')
                class_icon = {
                    # 기본 4개 직업
                    '전사': '⚔️', '아크메이지': '🔮', '궁수': '🏹', '도적': '🗡️',
                    # 기본 확장 직업
                    '성기사': '🛡️', '암흑기사': '💀', '몽크': '👊', '바드': '🎵', '네크로맨서': '💀',
                    # 중급 직업
                    '용기사': '🐉', '검성': '⚔️', '정령술사': '🌟', '암살자': '🔪', '기계공학자': '🔧',
                    # 고급 직업
                    '무당': '🔯', '해적': '🏴‍☠️', '사무라이': '🗾', '드루이드': '🌿', '철학자': '📘',
                    # 마스터 직업
                    '시간술사': '⏰', '연금술사': '⚗️', '검투사': '🏛️', '기사': '🐎', '신관': '✨',
                    # 전설 직업
                    '마검사': '⚡', '차원술사': '🌌', '광전사': '💥'
                }.get(character_class, '🎭')
                
                # HP/MP 게이지 바 생성
                hp_bar_length = 10
                hp_filled = int((hp_ratio * hp_bar_length))
                hp_bar = "▰" * hp_filled + "▱" * (hp_bar_length - hp_filled) + " "
                
                mp_bar_length = 10
                mp_filled = int((mp_ratio * mp_bar_length))
                mp_bar = "▰" * mp_filled + "▱" * (mp_bar_length - mp_filled) + " "
                
                # Brave 포인트
                brave_points = getattr(member, 'brave_points', 0)
                
                # 첫 번째 줄: 번호와 클래스 아이콘, 레벨, 이름
                print(f"       {'─'*60}")
                print(f"  {status_icon} {i}. {class_icon} {level_display}  {name_color}{member.name:15}{Color.RESET}")
                
                # 두 번째 줄: HP/MP 게이지
                print(f"        {hp_color}💚 HP {member.current_hp:3}{Color.WHITE}/{member.max_hp:3}  {Color.WHITE}[{hp_color}{hp_bar}{Color.WHITE}]{Color.RESET}  {mp_color}💙 MP {member.current_mp:3}{Color.WHITE}/{member.max_mp:3}  {Color.WHITE}[{mp_color}{mp_bar}{Color.WHITE}]{Color.RESET}")
                
                # 세 번째 줄: ATB와 BRV
                info3 = f"       {atb_icon} ATB: {Color.WHITE}[{atb_bar}]{Color.WHITE} {atb_display}"
                info3 += f"  ⚡ BRV {Color.BRIGHT_YELLOW}{brave_points}{Color.RESET}"
                
                # 상태 이상 표시
                status_effects = []
                if hasattr(member, 'is_broken') and member.is_broken:
                    status_effects.append(f"{Color.BRIGHT_MAGENTA}💀BREAK{Color.RESET}")
                if hasattr(member, 'wounds') and member.wounds > 0:
                    wounds_ratio = member.wounds / member.max_hp if member.max_hp > 0 else 0
                    if wounds_ratio > 0.3:
                        status_effects.append(f"{Color.RED}🩸중상{Color.RESET}")
                    elif wounds_ratio > 0.1:
                        status_effects.append(f"{Color.YELLOW}🩹부상{Color.RESET}")
                
                if status_effects:
                    info3 += f"  {' '.join(status_effects)}"
                
                print(f"{info3}")
                print(f"       {'─'*60}")
                
            else:
                print(f"       {'─'*60}")
                print(f"    {i}. 💀 {Color.RED}{member.name} - 전투불능{Color.RESET}")
                print(f"       {'─'*60}")
        
        # 적 상태 표시
        print(f"\n{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
        print(f"{Color.BRIGHT_WHITE}⚔️  적군 상태{Color.RESET}")
        print(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
        
        alive_enemies = [e for e in enemies if e.is_alive]
        for i, enemy in enumerate(alive_enemies, 1):
            # 현재 턴 적 강조
            name_color = Color.BRIGHT_RED if enemy == current_char else Color.WHITE
            status_icon = "▶" if enemy == current_char else " "
            
            # HP 상태 색상과 아이콘
            hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
            if hp_ratio > 0.7:
                hp_color = Color.BRIGHT_GREEN
                hp_icon = "💚"
            elif hp_ratio > 0.4:
                hp_color = Color.YELLOW
                hp_icon = "💛"
            elif hp_ratio > 0.15:
                hp_color = Color.BRIGHT_RED
                hp_icon = "🧡"
            else:
                hp_color = Color.RED
                hp_icon = "❤️"
            
            # ATB 게이지
            atb_gauge = getattr(enemy, 'atb_gauge', 0)
            if atb_gauge >= 100:
                atb_display = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
                atb_bar = f"{Color.BRIGHT_CYAN}{'▰'*10} {Color.RESET}"
                atb_icon = "⚡"
            else:
                atb_percent = int(atb_gauge)
                atb_display = f"{Color.CYAN}{atb_percent:3}%{Color.RESET}"
                filled = int(atb_gauge / 10)
                atb_bar = f"{Color.CYAN}{'▰'*filled}{Color.BRIGHT_BLACK}{'▱'*(10-filled)} {Color.RESET}"
                atb_icon = "⏳" if atb_gauge < 50 else "🔶"
            
            # 첫 번째 줄: 적 기본 정보 (레벨 포함)
            brave_points = getattr(enemy, 'brave_points', 0)
            enemy_level = getattr(enemy, 'level', 1)
            info1 = f"{Color.BRIGHT_BLACK}  {status_icon} {i}.{Color.RESET} 👹 {Color.BRIGHT_WHITE}Lv.{enemy_level:2}{Color.RESET} {name_color}{enemy.name:12}{Color.RESET}"
            info1 += f" {hp_icon}{hp_color}{enemy.current_hp:4}{Color.WHITE}/{enemy.max_hp:4}{Color.RESET}"
            info1 += f" ⚡{Color.BRIGHT_YELLOW}{brave_points:5}{Color.RESET}"
            
            # 두 번째 줄: ATB와 상태
            info2 = f"{Color.BRIGHT_BLACK}       {atb_icon} ATB: {Color.WHITE}[{atb_bar}]{Color.WHITE} {atb_display}{Color.RESET}"
            
            # 상태 이상 표시
            if hasattr(enemy, 'is_broken') and enemy.is_broken:
                info2 += f"  {Color.BRIGHT_MAGENTA}💀BREAK - 받는 HP 데미지 1.5배{Color.RESET}"
            
            print(f"{info1}")
            print(f"{info2}")
            if i < len(alive_enemies):
                print(f"{Color.BRIGHT_BLACK}       {'─'*50}{Color.RESET}")

    def _get_party_status_string(self, current_char: Character, party: List[Character], enemies: List[Character]) -> str:
        """파티 상태를 문자열로 반환 (메뉴 통합 표시용)"""
        status_lines = []
        
        # 헤더
        status_lines.append(f"{Color.BRIGHT_CYAN}{'─'*78}{Color.RESET}")
        status_lines.append(f"{Color.BRIGHT_WHITE}⚔️ DAWN OF STELLAR - BRAVE BATTLE ⚔️{Color.RESET}")
        status_lines.append(f"{Color.BRIGHT_YELLOW}현재 차례: {current_char.name}{Color.RESET}")
        status_lines.append(f"{Color.BRIGHT_CYAN}{'─'*78}{Color.RESET}")
        
        # 파티 상태
        status_lines.append(f"\n{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        status_lines.append(f"{Color.BRIGHT_WHITE}🛡️  아군 파티 상태{Color.RESET}")
        status_lines.append(f"{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        
        for i, member in enumerate(party, 1):
            if member.is_alive:
                # 현재 턴 캐릭터 강조
                name_color = Color.BRIGHT_CYAN if member == current_char else Color.WHITE
                status_icon = "▶" if member == current_char else " "
                
                # HP 상태 색상
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                if hp_ratio > 0.7:
                    hp_color = Color.BRIGHT_GREEN
                elif hp_ratio > 0.4:
                    hp_color = Color.YELLOW
                else:
                    hp_color = Color.BRIGHT_RED
                
                # MP 상태 색상
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                if mp_ratio > 0.5:
                    mp_color = Color.BRIGHT_BLUE
                else:
                    mp_color = Color.BLUE
                
                # ATB 게이지
                atb_gauge = getattr(member, 'atb_gauge', 0)
                if atb_gauge >= 100:
                    atb_display = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
                    atb_bar = f"{Color.BRIGHT_CYAN}{'▰'*10} {Color.RESET}"
                else:
                    atb_percent = int(atb_gauge)
                    atb_display = f"{Color.CYAN}{atb_percent:3}%{Color.RESET}"
                    filled = int(atb_gauge / 10)
                    atb_bar = f"{Color.CYAN}{'▰'*filled}{Color.BRIGHT_BLACK}{'▱'*(10-filled)} {Color.RESET}"
                
                # 클래스 아이콘
                character_class = getattr(member, 'character_class', '모험가')
                class_icon = {
                    '전사': '⚔️', '아크메이지': '🔮', '궁수': '🏹', '도적': '🗡️',
                    '성기사': '🛡️', '암흑기사': '💀', '몽크': '👊', '바드': '🎵',
                    '네크로맨서': '💀', '용기사': '🐉', '검성': '⚔️', '정령술사': '🌟',
                    '암살자': '🔪', '기계공학자': '🔧', '무당': '🔯', '해적': '🏴‍☠️',
                    '사무라이': '🗾', '드루이드': '🌿', '철학자': '📘', '시간술사': '⏰',
                    '연금술사': '⚗️', '검투사': '🏛️', '기사': '🐎', '신관': '✨',
                    '마검사': '⚡', '차원술사': '🌌', '광전사': '💥'
                }.get(character_class, '🎭')
                
                # HP/MP 게이지 바
                hp_bar_length = 10
                hp_filled = int((hp_ratio * hp_bar_length))
                hp_bar = "▰" * hp_filled + "▱" * (hp_bar_length - hp_filled) + " "
                
                mp_bar_length = 10
                mp_filled = int((mp_ratio * mp_bar_length))
                mp_bar = "▰" * mp_filled + "▱" * (mp_bar_length - mp_filled) + " "
                
                brave_points = getattr(member, 'brave_points', 0)
                level_display = f"Lv.{getattr(member, 'level', 1):2}"
                
                # 상태 라인들 추가
                status_lines.append(f"       {'─'*60}")
                status_lines.append(f"  {status_icon} {i}. {class_icon} {level_display}  {name_color}{member.name:15}{Color.RESET}")
                status_lines.append(f"        {hp_color}💚 HP {member.current_hp:3}{Color.WHITE}/{member.max_hp:3}  {Color.WHITE}[{hp_color}{hp_bar}{Color.WHITE}]{Color.RESET}  {mp_color}💙 MP {member.current_mp:3}{Color.WHITE}/{member.max_mp:3}  {Color.WHITE}[{mp_color}{mp_bar}{Color.WHITE}]{Color.RESET}")
                
                info3 = f"       ⏳ ATB: {Color.WHITE}[{atb_bar}]{Color.WHITE} {atb_display}"
                info3 += f"  ⚡ BRV {Color.BRIGHT_YELLOW}{brave_points}{Color.RESET}"
                status_lines.append(info3)
                status_lines.append(f"       {'─'*60}")
            else:
                status_lines.append(f"       {'─'*60}")
                status_lines.append(f"    {i}. 💀 {Color.RED}{member.name} - 전투불능{Color.RESET}")
                status_lines.append(f"       {'─'*60}")
        
        # 적군 상태 (상세하게)
        alive_enemies = [e for e in enemies if e.is_alive]
        if alive_enemies:
            status_lines.append(f"\n{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
            status_lines.append(f"{Color.BRIGHT_WHITE}⚔️  적군 상태{Color.RESET}")
            status_lines.append(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
            
            for i, enemy in enumerate(alive_enemies, 1):
                # 현재 턴 적 강조
                name_color = Color.BRIGHT_RED if enemy == current_char else Color.WHITE
                status_icon = "▶" if enemy == current_char else " "
                
                # HP 상태 색상
                hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
                if hp_ratio > 0.7:
                    hp_color = Color.BRIGHT_GREEN
                elif hp_ratio > 0.4:
                    hp_color = Color.YELLOW
                else:
                    hp_color = Color.BRIGHT_RED
                
                # ATB 게이지
                atb_gauge = getattr(enemy, 'atb_gauge', 0)
                if atb_gauge >= 100:
                    atb_display = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
                    atb_bar = f"{Color.BRIGHT_CYAN}{'▰'*10} {Color.RESET}"
                else:
                    atb_percent = int(atb_gauge)
                    atb_display = f"{Color.CYAN}{atb_percent:3}%{Color.RESET}"
                    filled = int(atb_gauge / 10)
                    atb_bar = f"{Color.CYAN}{'▰'*filled}{Color.BRIGHT_BLACK}{'▱'*(10-filled)} {Color.RESET}"
                
                # HP 게이지 바
                hp_bar_length = 10
                hp_filled = int((hp_ratio * hp_bar_length))
                hp_bar = "▰" * hp_filled + "▱" * (hp_bar_length - hp_filled) + " "
                
                brave_points = getattr(enemy, 'brave_points', 0)
                break_status = " [BREAK]" if (hasattr(enemy, 'is_broken') and enemy.is_broken) else ""
                
                # 적 정보 표시
                status_lines.append(f"       {'─'*60}")
                status_lines.append(f"  {status_icon} {i}. 👹 {name_color}{enemy.name:15}{Color.RESET}{break_status}")
                status_lines.append(f"        {hp_color}❤️ HP {enemy.current_hp:3}{Color.WHITE}/{enemy.max_hp:3}  {Color.WHITE}[{hp_color}{hp_bar}{Color.WHITE}]{Color.RESET}  ⚡ BRV {Color.BRIGHT_YELLOW}{brave_points}{Color.RESET}")
                
                info3 = f"       ⏳ ATB: {Color.WHITE}[{atb_bar}]{Color.WHITE} {atb_display}"
                status_lines.append(info3)
                status_lines.append(f"       {'─'*60}")
        
        return "\n".join(status_lines)

    def _play_skill_sfx(self, skill):
        """스킬 사용 SFX 재생 - 실제 존재하는 스킬 기반"""
        try:
            from .new_skill_system import SkillType
            
            skill_type = skill.get("type", SkillType.BRV_ATTACK)
            skill_name = skill.get("name", "").lower()
            
            # 실제 존재하는 스킬명 기반 특별 SFX 매핑
            special_skill_sfx = {
                # === 전사 계열 ===
                "분노 축적": "berserk",
                "방패 들기": "protect", 
                "강타": "sword_hit",
                "전사의 외침": "protect",
                "돌진 베기": "critical_hit",
                "광전사의 각성": "limit_break",
                
                # === 검성 계열 ===
                "검심 집중": "protect",
                "일섬": "sword_hit",
                "검기 방출": "sword_hit",
                "반격 태세": "protect",
                "연속 베기": "sword_hit",
                "무념무상": "limit_break",
                
                # === 검투사 계열 ===
                "투기장의 기술": "sword_hit",
                "군중의 함성": "berserk",
                "네트 던지기": "item_use",
                "트라이던트 찌르기": "critical_hit",
                "결투자의 명예": "protect",
                "콜로세움의 왕": "limit_break",
                
                # === 광전사 계열 ===
                "광기의 씨앗": "berserk",
                "무모한 돌격": "critical_hit",
                "피의 갈증": "heal",
                "광란의 일격": "critical_hit",
                "분노 폭발": "limit_break",
                "버서커의 최후": "limit_break",
                
                # === 기사 계열 ===
                "방패 방어": "protect",
                "창 돌격": "sword_hit",
                "아군 보호": "protect",
                "기사도 정신": "protect",
                "성스러운 돌격": "critical_hit",
                "수호기사의 맹세": "limit_break",
                
                # === 성기사 계열 ===
                "신앙의 힘": "protect",
                "성스러운 타격": "sword_hit",
                "축복": "heal",
                "치유의 빛": "heal2",
                "부활": "phoenix_down",
                "천사의 강림": "limit_break",
                
                # === 암흑기사 계열 ===
                "어둠의 계약": "poison",
                "생명 흡수": "heal",
                "저주의 검": "poison",
                "어둠의 보호": "protect",
                "흡혈": "heal",
                "어둠의 지배자": "limit_break",
                
                # === 용기사 계열 ===
                "용의 비늘": "protect",
                "드래곤 클로": "critical_hit",
                "화염 숨결": "fire",
                "용의 위엄": "berserk",
                "드래곤 스피어": "critical_hit",
                "드래곤 로드": "limit_break",
                
                # === 아크메이지 계열 ===
                "마나 집중": "magic_cast",
                "매직 미사일": "magic_cast",
                "파이어볼": "fire",
                "마법 방어막": "barrier",
                "라이트닝 볼트": "thunder",
                "메테오": "fire3",
                
                # === 정령술사 계열 ===
                "정령과의 교감": "summon",
                "화염 정령": "fire",
                "물 정령의 치유": "heal2",
                "바람 정령의 축복": "haste",
                "대지 정령의 분노": "fire2",
                "사대 정령 소환": "limit_break",
                
                # === 시간술사 계열 ===
                "시간 가속": "haste",
                "시간 왜곡": "slow",
                "시간 되돌리기": "heal3",
                "미래 예지": "protect",
                "시간 정지": "stop",
                "시공간 붕괴": "limit_break",
                
                # === 차원술사 계열 ===
                "차원 균열": "magic_cast",
                "순간이동": "teleport",
                "공간 왜곡": "slow",
                "차원 방패": "barrier",
                "공간 절단": "critical_hit",
                "차원 폭풍": "limit_break",
                
                # === 철학자 계열 ===
                "진리 탐구": "magic_cast",
                "진실 간파": "magic_cast",
                "지혜의 빛": "heal",
                "존재 부정": "critical_hit",
                "철학적 사고": "protect",
                "절대 진리": "limit_break",
                
                # === 궁수 계열 ===
                "조준": "protect",
                "정밀 사격": "gun_hit",
                "관통 화살": "gun_critical",
                "정찰 화살": "gun_hit",
                "연사": "gun_critical",
                "천공의 화살": "limit_break",
                
                # === 암살자 계열 ===
                "그림자 숨기": "silence",
                "기습": "critical_hit",
                "독 바르기": "poison",
                "연막탄": "silence",
                "암살술": "critical_hit",
                "그림자 분신": "limit_break",
                
                # === 도적 계열 ===
                "재빠른 손놀림": "haste",
                "기습 공격": "critical_hit",
                "아이템 훔치기": "item_pickup",
                "연속 베기": "sword_hit",
                "숨겨둔 아이템": "item_use",
                "완벽한 도둑질": "limit_break",
                
                # === 해적 계열 ===
                "이도류": "sword_hit",
                "칼부림": "sword_hit",
                "바다의 저주": "poison",
                "해적의 함성": "berserk",
                "해상 치료술": "heal2",
            }
            
            # 1순위: 특별한 스킬명 매핑
            if skill_name in special_skill_sfx:
                sfx_name = special_skill_sfx[skill_name]
            
            # 2순위: 스킬 타입별 기본 SFX
            elif skill_type == SkillType.BRV_ATTACK:
                # BRV 공격을 무기/공격 스타일별로 세분화
                if any(keyword in skill_name for keyword in ["검", "베기", "검기", "검술", "일섬", "칼", "클로"]):
                    sfx_name = "sword_hit"
                elif any(keyword in skill_name for keyword in ["사격", "화살", "총", "활", "정밀"]):
                    sfx_name = "gun_hit"
                elif any(keyword in skill_name for keyword in ["주먹", "펀치", "타격", "몽크", "기습"]):
                    sfx_name = "punch_hit"
                elif any(keyword in skill_name for keyword in ["돌격", "충격", "강타", "미사일"]):
                    sfx_name = "critical_hit"
                elif any(keyword in skill_name for keyword in ["마법", "정령", "차원", "매직"]):
                    sfx_name = "magic_cast"
                else:
                    sfx_name = "sword_hit"  # 기본 물리 공격
                    
            elif skill_type == SkillType.HP_ATTACK:
                # HP 공격을 강도별로 분류
                if any(keyword in skill_name for keyword in ["필살", "궁극", "죽음", "파괴", "스피어", "절단"]):
                    sfx_name = "limit_break"
                elif any(keyword in skill_name for keyword in ["크리티컬", "치명", "강타", "일격", "흡혈", "암살"]):
                    sfx_name = "critical_hit"
                elif any(keyword in skill_name for keyword in ["볼트", "번개", "전기"]):
                    sfx_name = "thunder"
                else:
                    sfx_name = "critical_hit"  # 기본 HP 공격
                    
            elif skill_type == SkillType.BRV_HP_ATTACK:
                # 복합 공격
                if any(keyword in skill_name for keyword in ["폭발", "연사", "분신"]):
                    sfx_name = "limit_break"
                else:
                    sfx_name = "sword_hit"
                
            elif skill_type == SkillType.HEAL:
                # 치유를 강도별로 분류
                if any(keyword in skill_name for keyword in ["되돌리기", "부활", "완전"]):
                    sfx_name = "heal3"
                elif any(keyword in skill_name for keyword in ["정령", "빛", "치료술"]):
                    sfx_name = "heal2"
                else:
                    sfx_name = "heal"
                    
            elif skill_type == SkillType.BUFF:
                # 버프를 종류별로 분류
                if any(keyword in skill_name for keyword in ["방어", "보호", "방패", "방벽", "집중", "태세"]):
                    sfx_name = "protect"
                elif any(keyword in skill_name for keyword in ["속도", "민첩", "가속", "손놀림"]):
                    sfx_name = "haste"
                elif any(keyword in skill_name for keyword in ["축복", "정신", "힘", "교감"]):
                    sfx_name = "heal"
                elif any(keyword in skill_name for keyword in ["배리어", "방어막"]):
                    sfx_name = "barrier"
                elif any(keyword in skill_name for keyword in ["함성", "외침", "분노", "축적"]):
                    sfx_name = "berserk"
                else:
                    sfx_name = "protect"
                    
            elif skill_type == SkillType.DEBUFF:
                # 디버프를 종류별로 분류
                if any(keyword in skill_name for keyword in ["독", "바르기", "저주", "맹독"]):
                    sfx_name = "poison"
                elif any(keyword in skill_name for keyword in ["침묵", "봉인", "연막"]):
                    sfx_name = "silence"
                elif any(keyword in skill_name for keyword in ["수면", "잠", "자장가"]):
                    sfx_name = "sleep"
                elif any(keyword in skill_name for keyword in ["정지", "스톱", "왜곡"]):
                    sfx_name = "stop"
                elif any(keyword in skill_name for keyword in ["둔화", "감속", "왜곡"]):
                    sfx_name = "slow"
                elif any(keyword in skill_name for keyword in ["위엄", "공포"]):
                    sfx_name = "berserk"
                else:
                    sfx_name = "poison"
                    
            elif skill_type == SkillType.SPECIAL:
                # 특수 스킬
                if any(keyword in skill_name for keyword in ["훔치기", "도둑질"]):
                    sfx_name = "item_pickup"
                elif any(keyword in skill_name for keyword in ["계약", "간파", "예지"]):
                    sfx_name = "magic_cast"
                elif any(keyword in skill_name for keyword in ["부활", "되살리기"]):
                    sfx_name = "phoenix_down"
                elif any(keyword in skill_name for keyword in ["사고", "명예"]):
                    sfx_name = "protect"
                else:
                    sfx_name = "magic_cast"
                    
            elif skill_type == SkillType.ULTIMATE:
                # 궁극기를 속성별로 분류
                if any(keyword in skill_name for keyword in ["화염", "불", "파이어", "메테오", "로드"]):
                    sfx_name = "fire3"
                elif any(keyword in skill_name for keyword in ["냉기", "얼음", "블리자드"]):
                    sfx_name = "ice3"
                elif any(keyword in skill_name for keyword in ["번개", "전기", "썬더", "볼트"]):
                    sfx_name = "thunder3"
                elif any(keyword in skill_name for keyword in ["소환", "정령", "강림"]):
                    sfx_name = "summon"
                elif any(keyword in skill_name for keyword in ["붕괴", "폭풍", "진리"]):
                    sfx_name = "ultima"
                else:
                    sfx_name = "limit_break"
                    
            elif skill_type == SkillType.FIELD:
                # 필드 스킬
                if any(keyword in skill_name for keyword in ["연막", "숨기기"]):
                    sfx_name = "silence"
                elif any(keyword in skill_name for keyword in ["치료", "회복"]):
                    sfx_name = "heal2"
                elif any(keyword in skill_name for keyword in ["정지", "시간"]):
                    sfx_name = "stop"
                else:
                    sfx_name = "magic_cast"
                    
            elif skill_type == SkillType.COUNTER:
                # 반격 스킬
                sfx_name = "protect"
            else:
                # 기본 SFX
                sfx_name = "menu_confirm"
            
            # SFX 재생 (폴백 지원)
            if sfx_name:
                success = False
                if self.audio_system:
                    success = self.audio_system.play_sfx(sfx_name)
                    if not success:
                        # 폴백 SFX 시도
                        fallback_sfx = self._get_fallback_sfx(skill_type)
                        success = self.audio_system.play_sfx(fallback_sfx)
                        if success:
                            print(f"🔊 {skill.get('name', '스킬')} 효과음 (폴백): {fallback_sfx}")
                    else:
                        print(f"🔊 {skill.get('name', '스킬')} 효과음: {sfx_name}")
                elif self.sound_manager:
                    success = self.sound_manager.play_sfx(sfx_name)
                    if not success:
                        fallback_sfx = self._get_fallback_sfx(skill_type)
                        success = self.sound_manager.play_sfx(fallback_sfx)
                        if success:
                            print(f"🔊 {skill.get('name', '스킬')} 효과음 (폴백): {fallback_sfx}")
                    else:
                        print(f"🔊 {skill.get('name', '스킬')} 효과음: {sfx_name}")
                else:
                    print(f"⚠️ 오디오 시스템 없음")
                    
        except Exception as e:
            print(f"⚠️ SFX 재생 오류: {e}")
            
    def _check_dodge(self, attacker: Character, target: Character) -> bool:
        """회피 체크 - 명중률 vs 회피율 계산"""
        try:
            # 공격자 명중률 계산
            attacker_accuracy = getattr(attacker, 'accuracy', 85)
            
            # 적의 명중률 감소 효과 적용 (연막탄 등)
            if hasattr(target, 'temp_enemy_accuracy_down') and target.temp_enemy_accuracy_down > 0:
                attacker_accuracy -= target.temp_enemy_accuracy_down
            
            # 수비자 회피율 계산
            target_evasion = getattr(target, 'evasion', 10)
            
            # 임시 회피 보너스 적용
            if hasattr(target, 'temp_dodge_bonus'):
                target_evasion += target.temp_dodge_bonus
                
            # 차원술사 공간 이동 - 100% 회피
            if hasattr(target, 'temp_dimension_dodge') and target.temp_dimension_dodge:
                return True
                
            # 생존 본능 특성 - HP 30% 이하에서 회피율 50% 증가
            if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
                if target.current_hp <= target.max_hp * 0.3:
                    if hasattr(target, 'temp_dodge_bonus'):
                        # 생존 본능이 있는 캐릭터인지 확인
                        for trait in getattr(target, 'traits', []):
                            if "생존 본능" in trait.name:
                                target_evasion += 50
                                break
            
            # 명중률 계산 공식: (공격자 명중률 / 수비자 회피율) * 100
            # 최소 5%, 최대 95% 명중률 보장
            if target_evasion <= 0:
                target_evasion = 1  # 0 나누기 방지
            hit_chance = min(95, max(5, (attacker_accuracy / target_evasion) * 100))
            
            # 회피 판정
            import random
            dodge_roll = random.randint(1, 100)
            is_dodged = dodge_roll > hit_chance
            
            return is_dodged
            
        except Exception as e:
            print(f"⚠️ 회피 체크 오류: {e}")
            return False  # 오류 시 회피하지 않음
            
    def _get_fallback_sfx(self, skill_type):
        """스킬 타입별 폴백 SFX 반환"""
        try:
            from .new_skill_system import SkillType
            fallback_map = {
                SkillType.BRV_ATTACK: "sword_hit",
                SkillType.HP_ATTACK: "critical_hit", 
                SkillType.BRV_HP_ATTACK: "limit_break",
                SkillType.HEAL: "heal",
                SkillType.BUFF: "protect",
                SkillType.DEBUFF: "poison",
                SkillType.SPECIAL: "magic_cast",
                SkillType.ULTIMATE: "limit_break",
                SkillType.FIELD: "magic_cast",
                SkillType.COUNTER: "protect"
            }
            return fallback_map.get(skill_type, "menu_confirm")
        except:
            return "menu_confirm"
            
    def _show_hit_evasion_test(self, party: List[Character], enemies: List[Character]):
        """명중률/회피율 테스트 화면"""
        while True:
            print(f"\n{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
            print(f"{Color.BRIGHT_YELLOW}🎯 명중률/회피율 테스트{Color.RESET}")
            print(f"{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
            
            try:
                from .cursor_menu_system import create_simple_menu
                
                # 모든 살아있는 캐릭터 목록
                all_chars = [c for c in party + enemies if c.is_alive]
                
                # 공격자 선택 메뉴
                attacker_options = []
                attacker_descriptions = []
                
                for char in all_chars:
                    accuracy = getattr(char, 'accuracy', 85)
                    temp_dodge = getattr(char, 'temp_dodge_bonus', 0)
                    char_type = "🛡️" if char in party else "⚔️"
                    
                    attacker_options.append(f"{char_type} {char.name}")
                    attacker_descriptions.append(f"명중률: {accuracy}% | 임시 회피: +{temp_dodge}%")
                
                attacker_options.append("🔙 돌아가기")
                attacker_descriptions.append("상세 상태 메뉴로 돌아갑니다")
                
                attacker_menu = create_simple_menu("🎯 공격자 선택", attacker_options, attacker_descriptions, clear_screen=True)
                attacker_choice = attacker_menu.run()
                
                if attacker_choice is None or attacker_choice == len(attacker_options) - 1:
                    break
                    
                attacker = all_chars[attacker_choice]
                
                # 대상 선택 메뉴
                target_options = []
                target_descriptions = []
                
                for char in all_chars:
                    if char != attacker:  # 자기 자신 제외
                        evasion = getattr(char, 'evasion', 10)
                        temp_dodge = getattr(char, 'temp_dodge_bonus', 0)
                        temp_dimension = getattr(char, 'temp_dimension_dodge', False)
                        char_type = "🛡️" if char in party else "⚔️"
                        
                        target_options.append(f"{char_type} {char.name}")
                        special_status = " [차원이동]" if temp_dimension else ""
                        target_descriptions.append(f"회피율: {evasion}% | 회피보너스: +{temp_dodge}%{special_status}")
                
                target_options.append("🔙 돌아가기")
                target_descriptions.append("공격자 선택으로 돌아갑니다")
                
                target_menu = create_simple_menu("🛡️ 대상 선택", target_options, target_descriptions, clear_screen=True)
                target_choice = target_menu.run()
                
                if target_choice is None or target_choice == len(target_options) - 1:
                    continue
                    
                # 자기 자신이 아닌 캐릭터 중에서 선택
                available_targets = [c for c in all_chars if c != attacker]
                target = available_targets[target_choice]
                
                # 명중률 계산 및 테스트 실행
                self._run_hit_evasion_simulation(attacker, target)
                
            except ImportError:
                # 폴백: 간단한 텍스트 메뉴
                print("\n🎯 간단 명중률 테스트:")
                print("1. 모든 캐릭터 상호 명중률 표시")
                print("2. 돌아가기")
                
                try:
                    choice = int(input("선택: "))
                    if choice == 1:
                        self._show_all_hit_rates(party, enemies)
                    elif choice == 2:
                        break
                except:
                    continue
    
    def _run_hit_evasion_simulation(self, attacker: Character, target: Character):
        """명중률/회피율 시뮬레이션 실행"""
        print(f"\n{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        print(f"{Color.BRIGHT_YELLOW}🎯 {attacker.name} → {target.name} 명중률 테스트{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        
        # 스탯 정보 표시
        attacker_accuracy = getattr(attacker, 'accuracy', 85)
        target_evasion = getattr(target, 'evasion', 10)
        target_dodge_bonus = getattr(target, 'temp_dodge_bonus', 0)
        target_dimension_dodge = getattr(target, 'temp_dimension_dodge', False)
        enemy_accuracy_down = getattr(target, 'temp_enemy_accuracy_down', 0)
        
        print(f"\n📊 기본 스탯:")
        print(f"  🏹 {attacker.name} 명중률: {attacker_accuracy}%")
        if enemy_accuracy_down > 0:
            print(f"    - 적 명중률 감소: -{enemy_accuracy_down}% (연막탄 등)")
        print(f"  🏃 {target.name} 회피율: {target_evasion}%")
        if target_dodge_bonus > 0:
            print(f"    + 임시 회피 보너스: +{target_dodge_bonus}%")
        if target_dimension_dodge:
            print(f"    + 차원 이동: 100% 회피!")
        
        # 생존 본능 특성 체크
        survival_bonus = 0
        if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
            if target.current_hp <= target.max_hp * 0.3:
                for trait in getattr(target, 'traits', []):
                    if "생존 본능" in trait.name:
                        survival_bonus = 50
                        print(f"    + 생존 본능 (HP 30% 이하): +{survival_bonus}%")
                        break
        
        # 최종 명중률 계산
        if target_dimension_dodge:
            hit_chance = 0
            print(f"\n💫 차원 이동으로 인한 100% 회피!")
        else:
            final_accuracy = attacker_accuracy - enemy_accuracy_down
            final_evasion = target_evasion + target_dodge_bonus + survival_bonus
            hit_chance = min(95, max(25, (final_accuracy / max(final_evasion, 1)) * 100))
            
            print(f"\n🎲 최종 계산:")
            print(f"  명중률 공식: min(95, max(25, (공격자명중률 / 수비자회피율) * 100))")
            print(f"  실제 계산: min(95, max(25, ({final_accuracy} / {final_evasion}) * 100))")
            print(f"  💥 최종 명중률: {hit_chance:.1f}%")
            print(f"  💨 회피 확률: {100-hit_chance:.1f}%")
        
        # 시뮬레이션 실행
        print(f"\n🎮 100회 시뮬레이션 실행 중...")
        import random
        hits = 0
        dodges = 0
        
        for i in range(100):
            if target_dimension_dodge:
                dodges += 1
            else:
                roll = random.randint(1, 100)
                if roll <= hit_chance:
                    hits += 1
                else:
                    dodges += 1
        
        print(f"\n📈 시뮬레이션 결과:")
        print(f"  💥 명중: {hits}회 ({hits}%)")
        print(f"  💨 회피: {dodges}회 ({dodges}%)")
        print(f"  📊 이론치: 명중 {hit_chance:.1f}% / 회피 {100-hit_chance:.1f}%")
        
        if abs(hits - hit_chance) <= 10:
            print(f"  ✅ 시뮬레이션 결과가 이론치와 거의 일치합니다!")
        else:
            print(f"  ⚠️ 시뮬레이션 결과와 이론치에 차이가 있습니다 (확률의 오차)")
        
        input(f"\n{Color.BRIGHT_GREEN}⏎ 계속하려면 Enter를 누르세요...{Color.RESET}")
    
    def _show_all_hit_rates(self, party: List[Character], enemies: List[Character]):
        """모든 캐릭터 간 명중률 매트릭스 표시"""
        print(f"\n{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        print(f"{Color.BRIGHT_YELLOW}🎯 전체 명중률 매트릭스{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        
        all_chars = [c for c in party + enemies if c.is_alive]
        
        print(f"\n📊 공격자 → 대상 명중률:")
        print(f"{'공격자':<12} {'→':<3} {'대상':<12} {'명중률':<8} {'회피율':<8}")
        print("-" * 50)
        
        for attacker in all_chars:
            attacker_accuracy = getattr(attacker, 'accuracy', 85)
            attacker_type = "🛡️" if attacker in party else "⚔️"
            
            for target in all_chars:
                if target != attacker:
                    target_evasion = getattr(target, 'evasion', 10)
                    target_dodge = getattr(target, 'temp_dodge_bonus', 0)
                    target_dimension = getattr(target, 'temp_dimension_dodge', False)
                    target_type = "🛡️" if target in party else "⚔️"
                    
                    if target_dimension:
                        hit_chance = 0
                    else:
                        final_evasion = target_evasion + target_dodge
                        hit_chance = min(95, max(25, (attacker_accuracy / max(final_evasion, 1)) * 100))
                    
                    attacker_name = f"{attacker_type}{attacker.name[:8]}"
                    target_name = f"{target_type}{target.name[:8]}"
                    
                    print(f"{attacker_name:<12} {'→':<3} {target_name:<12} {hit_chance:>6.1f}% {100-hit_chance:>6.1f}%")
        
        input(f"\n{Color.BRIGHT_GREEN}⏎ 계속하려면 Enter를 누르세요...{Color.RESET}")
    
    def _get_fallback_sfx(self, skill_type):
        """SFX 폴백 매핑"""
        from .new_skill_system import SkillType
        
        fallback_map = {
            SkillType.BRV_ATTACK: "sword_hit",
            SkillType.HP_ATTACK: "critical_hit", 
            SkillType.BRV_HP_ATTACK: "sword_hit",
            SkillType.HEAL: "heal",
            SkillType.BUFF: "protect",
            SkillType.DEBUFF: "poison",
            SkillType.SPECIAL: "magic_cast",
            SkillType.ULTIMATE: "limit_break"
        }
        
        return fallback_map.get(skill_type, "menu_confirm")

    def show_detailed_combat_status(self, current_char: Character, party: List[Character], enemies: List[Character]):
        """상세한 전투 상태 표시 - 개별 캐릭터 상세 조회 가능"""
        while True:
            print(f"\n{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
            print(f"{Color.BRIGHT_CYAN}📊 실시간 상태 - 상세 조회{Color.RESET}")
            print(f"{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
            
            try:
                from .cursor_menu_system import create_simple_menu
                
                # 메뉴 옵션 구성
                menu_options = []
                menu_descriptions = []
                
                # 아군 파티 멤버들
                for i, member in enumerate(party, 1):
                    if member.is_alive:
                        hp_ratio = member.current_hp / member.max_hp
                        mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                        brave = getattr(member, 'brave_points', 0)
                        
                        hp_status = "🟢" if hp_ratio > 0.7 else "🟡" if hp_ratio > 0.4 else "🔴"
                        mp_status = "🔵" if mp_ratio > 0.5 else "🟣"
                        brave_status = "⚡" if brave >= 500 else "✨" if brave >= 300 else "💧"
                        
                        menu_options.append(f"{hp_status} {member.name} ({member.character_class})")
                        menu_descriptions.append(f"HP: {member.current_hp}/{member.max_hp} | MP: {member.current_mp}/{member.max_mp} | BRV: {brave}")
                    else:
                        menu_options.append(f"💀 {member.name} (전투불능)")
                        menu_descriptions.append("상태: 사망 - 상세 정보 없음")
                
                # 구분선
                menu_options.append("─── 적군 정보 ───")
                menu_descriptions.append("적군들의 상태를 확인할 수 있습니다")
                
                # 적군들
                alive_enemies = [e for e in enemies if e.is_alive]
                for enemy in alive_enemies:
                    hp_ratio = enemy.current_hp / enemy.max_hp
                    brave = getattr(enemy, 'brave_points', 0)
                    
                    hp_status = "🟢" if hp_ratio > 0.7 else "🟡" if hp_ratio > 0.4 else "🔴"
                    brave_status = "⚡" if brave >= 500 else "✨" if brave >= 300 else "💧"
                    break_status = " [BREAK]" if hasattr(enemy, 'is_broken') and enemy.is_broken else ""
                    
                    menu_options.append(f"{hp_status} {enemy.name}{break_status}")
                    menu_descriptions.append(f"HP: {enemy.current_hp}/{enemy.max_hp} | BRV: {brave}")
                
                # 전투 정보
                menu_options.append("─── 전투 정보 ───")
                menu_descriptions.append("전체 전투 상황과 턴 순서를 확인합니다")
                
                menu_options.append("📊 전투 현황 요약")
                menu_descriptions.append("현재 전투의 전체적인 상황을 요약해서 봅니다")
                
                menu_options.append("⏰ 턴 순서 예측")
                menu_descriptions.append("ATB 게이지를 기반으로 다음 턴 순서를 예측합니다")
                
                menu_options.append("🎯 명중률/회피율 테스트")
                menu_descriptions.append("캐릭터들 간의 명중률과 회피율을 테스트해봅니다")
                
                menu_options.append("🔙 돌아가기")
                menu_descriptions.append("전투 화면으로 돌아갑니다")
                
                menu = create_simple_menu("📊 실시간 상태 조회", menu_options, menu_descriptions, clear_screen=True)
                choice = menu.run()
                
                if choice is None or choice == len(menu_options) - 1:  # 돌아가기
                    break
                elif choice < len(party):  # 파티 멤버 선택
                    selected_member = party[choice]
                    self._show_character_detail(selected_member, True)
                elif choice == len(party):  # 구분선 (적군)
                    continue
                elif choice < len(party) + 1 + len(alive_enemies):  # 적군 선택
                    enemy_index = choice - len(party) - 1
                    selected_enemy = alive_enemies[enemy_index]
                    self._show_character_detail(selected_enemy, False)
                elif choice == len(party) + 1 + len(alive_enemies):  # 구분선 (전투 정보)
                    continue
                elif choice == len(party) + 2 + len(alive_enemies):  # 전투 현황 요약
                    self._show_battle_summary(current_char, party, enemies)
                elif choice == len(party) + 3 + len(alive_enemies):  # 턴 순서 예측
                    self._show_turn_order_prediction(party + enemies)
                elif choice == len(party) + 4 + len(alive_enemies):  # 명중률/회피율 테스트
                    self._show_hit_evasion_test(party, enemies)
                
            except ImportError:
                # 폴백: 간단한 정보만 표시
                print(f"\n{Color.BRIGHT_BLUE}🛡️ 아군 파티:{Color.RESET}")
                for i, member in enumerate(party, 1):
                    if member.is_alive:
                        hp_ratio = int(member.current_hp/member.max_hp*100)
                        mp_ratio = int(member.current_mp/max(1,member.max_mp)*100)
                        brave = getattr(member, 'brave_points', 0)
                        print(f"  {i}. {member.name}: HP {hp_ratio}% | MP {mp_ratio}% | BRV {brave}")
                    else:
                        print(f"  {i}. {member.name}: 💀 사망")
                
                print(f"\n{Color.BRIGHT_RED}⚔️ 적군:{Color.RESET}")
                for i, enemy in enumerate(alive_enemies, 1):
                    hp_ratio = int(enemy.current_hp/enemy.max_hp*100)
                    brave = getattr(enemy, 'brave_points', 0)
                    break_status = " [BREAK]" if hasattr(enemy, 'is_broken') and enemy.is_broken else ""
                    print(f"  {i}. {enemy.name}: HP {hp_ratio}% | BRV {brave}{break_status}")
                
                break
    
    def _show_character_detail(self, character: Character, is_ally: bool):
        """개별 캐릭터의 매우 상세한 정보 표시"""
        print(f"\n{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        if is_ally:
            print(f"{Color.BRIGHT_BLUE}🛡️ {character.name} 상세 정보{Color.RESET}")
        else:
            print(f"{Color.BRIGHT_RED}⚔️ {character.name} 상세 정보{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        
        # 기본 정보
        print(f"\n📋 기본 정보:")
        print(f"  이름: {character.name}")
        if hasattr(character, 'character_class'):
            print(f"  클래스: {character.character_class}")
        if hasattr(character, 'level'):
            print(f"  레벨: {character.level}")
        
        # 생명력 상태
        print(f"\n💚 생명력 상태:")
        hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
        hp_bar = "█" * int(hp_ratio * 20) + "░" * (20 - int(hp_ratio * 20))
        hp_color = Color.BRIGHT_GREEN if hp_ratio > 0.7 else Color.YELLOW if hp_ratio > 0.4 else Color.BRIGHT_RED
        print(f"  HP: {Color.WHITE}[{hp_color}{hp_bar}{Color.WHITE}] {character.current_hp}{Color.WHITE}/{character.max_hp} ({int(hp_ratio*100)}%){Color.RESET}")
        
        # 상처 시스템 (아군만)
        if is_ally and hasattr(character, 'wounds'):
            if character.wounds > 0:
                wound_ratio = character.wounds / character.max_hp if character.max_hp > 0 else 0
                wound_severity = "경상" if wound_ratio < 0.1 else "중상" if wound_ratio < 0.3 else "중태"
                print(f"  🩸 상처: {character.wounds} ({wound_severity})")
                print(f"  🏥 치료 가능 HP: {character.max_hp - character.wounds}")
            else:
                print(f"  🩹 상처: 없음 (건강)")
        
        # 마나 상태 (아군만)
        if is_ally and hasattr(character, 'current_mp'):
            mp_ratio = character.current_mp / character.max_mp if character.max_mp > 0 else 0
            mp_bar = "█" * int(mp_ratio * 20) + "░" * (20 - int(mp_ratio * 20))
            mp_color = Color.BRIGHT_CYAN if mp_ratio > 0.7 else Color.BLUE if mp_ratio > 0.3 else Color.BRIGHT_BLACK
            print(f"\n💙 마나 상태:")
            print(f"  MP: {Color.WHITE}[{mp_color}{mp_bar}{Color.WHITE}] {character.current_mp}{Color.WHITE}/{character.max_mp} ({int(mp_ratio*100)}%){Color.RESET}")
        
        # Brave 시스템
        brave_points = getattr(character, 'brave_points', 0)
        print(f"\n⚡ Brave 시스템:")
        # 통일된 이모지와 색상 사용
        brave_status = "전투력" if brave_points >= 300 else "축적중"
        brave_color = Color.BRIGHT_YELLOW
        
        print(f"  BRV: {brave_color}{brave_points}{Color.RESET} ({brave_status})")
        
        # BREAK 상태
        if hasattr(character, 'is_broken') and character.is_broken:
            print(f"  💥 상태: {Color.BRIGHT_MAGENTA}BREAK - 받는 HP 데미지 1.5배{Color.RESET}")
        
        # ATB 게이지
        atb_gauge = getattr(character, 'atb_gauge', 0)
        atb_bar = "█" * int(atb_gauge/5) + "░" * (20-int(atb_gauge/5))
        atb_color = Color.BRIGHT_CYAN if atb_gauge >= 100 else Color.CYAN if atb_gauge >= 75 else Color.BLUE
        print(f"\n⏱️ ATB (액션 타임 배틀):")
        print(f"  게이지: {Color.WHITE}[{atb_color}{atb_bar}{Color.WHITE}] {int(atb_gauge)}%{Color.RESET}")
        if atb_gauge >= 100:
            print(f"  상태: ⚡ 행동 준비 완료!")
        else:
            turns_to_ready = int((100 - atb_gauge) / 8)  # 대략적인 계산
            print(f"  예상: {turns_to_ready}턴 후 행동 가능")
        
        # 능력치 (아군만)
        if is_ally:
            print(f"\n{Color.BRIGHT_CYAN}⚔️ 전투 능력치{Color.RESET}")
            print(f"{Color.CYAN}{'─'*50}{Color.RESET}")
            
            if hasattr(character, 'physical_attack'):
                # 공격력 색상 계산
                atk_color = Color.BRIGHT_RED if character.physical_attack >= 100 else Color.RED if character.physical_attack >= 80 else Color.YELLOW if character.physical_attack >= 60 else Color.WHITE
                print(f"  {Color.BRIGHT_RED}⚔️  물리 공격력:{Color.RESET} {atk_color}{character.physical_attack:3}{Color.RESET}")
                
            if hasattr(character, 'magic_attack'):
                # 마법력 색상 계산
                mag_color = Color.BRIGHT_MAGENTA if character.magic_attack >= 100 else Color.MAGENTA if character.magic_attack >= 80 else Color.BLUE if character.magic_attack >= 60 else Color.WHITE
                print(f"  {Color.BRIGHT_MAGENTA}🔮  마법 공격력:{Color.RESET} {mag_color}{character.magic_attack:3}{Color.RESET}")
                
            if hasattr(character, 'physical_defense'):
                # 물리 방어력 색상 계산
                pdef_color = Color.BRIGHT_BLUE if character.physical_defense >= 100 else Color.BLUE if character.physical_defense >= 80 else Color.CYAN if character.physical_defense >= 60 else Color.WHITE
                print(f"  {Color.BRIGHT_BLUE}🛡️  물리 방어력:{Color.RESET} {pdef_color}{character.physical_defense:3}{Color.RESET}")
                
            if hasattr(character, 'magic_defense'):
                # 마법 방어력 색상 계산
                mdef_color = Color.BRIGHT_CYAN if character.magic_defense >= 100 else Color.CYAN if character.magic_defense >= 80 else Color.BLUE if character.magic_defense >= 60 else Color.WHITE
                print(f"  {Color.BRIGHT_CYAN}✨  마법 방어력:{Color.RESET} {mdef_color}{character.magic_defense:3}{Color.RESET}")
                
            if hasattr(character, 'speed'):
                # 속도 색상 계산
                spd_color = Color.BRIGHT_YELLOW if character.speed >= 100 else Color.YELLOW if character.speed >= 80 else Color.GREEN if character.speed >= 60 else Color.WHITE
                print(f"  {Color.BRIGHT_YELLOW}⚡  속도:{Color.RESET}         {spd_color}{character.speed:3}{Color.RESET}")
            
            print(f"{Color.CYAN}{'─'*50}{Color.RESET}")
        
        # 특성 정보 (아군만)
        if is_ally and hasattr(character, 'traits') and character.traits:
            print(f"\n🌟 특성:")
            for trait in character.traits:
                trait_name = trait.name if hasattr(trait, 'name') else str(trait)
                if hasattr(trait, 'effect_type'):
                    if trait.effect_type == "active":
                        if hasattr(trait, 'cooldown') and trait.cooldown > 0:
                            print(f"  {trait_name} (액티브) - 쿨다운: {trait.cooldown}턴")
                        else:
                            print(f"  {trait_name} (액티브) - 사용 가능")
                    else:
                        print(f"  {trait_name} (패시브) - 항상 활성")
                else:
                    print(f"  {trait_name}")
        
        # 상태 효과
        if hasattr(character, 'status_effects') and character.status_effects:
            print(f"\n🎭 상태 효과:")
            for effect in character.status_effects:
                effect_name = effect.name if hasattr(effect, 'name') else str(effect)
                duration = effect.duration if hasattr(effect, 'duration') else "?"
                print(f"  {effect_name} ({duration}턴 남음)")
        
        input(f"\n{Color.YELLOW}계속하려면 Enter를 누르세요...{Color.RESET}")
    
    def _show_battle_summary(self, current_char: Character, party: List[Character], enemies: List[Character]):
        """전투 현황 요약"""
        print(f"\n{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}📊 전투 현황 요약{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        
        # 아군 요약
        alive_allies = [p for p in party if p.is_alive]
        total_ally_hp = sum(p.current_hp for p in alive_allies)
        total_ally_max_hp = sum(p.max_hp for p in alive_allies)
        total_ally_brave = sum(getattr(p, 'brave_points', 0) for p in alive_allies)
        
        print(f"\n{Color.BRIGHT_BLUE}🛡️ 아군 현황:{Color.RESET}")
        print(f"  생존자: {len(alive_allies)}/{len(party)}명")
        print(f"  총 HP: {total_ally_hp:,}/{total_ally_max_hp:,} ({int(total_ally_hp/total_ally_max_hp*100) if total_ally_max_hp > 0 else 0}%)")
        print(f"  총 BRV: {total_ally_brave:,}")
        print(f"  HP 공격 가능: {len([p for p in alive_allies if getattr(p, 'brave_points', 0) >= 300])}명")
        
        # 적군 요약
        alive_enemies = [e for e in enemies if e.is_alive]
        total_enemy_hp = sum(e.current_hp for e in alive_enemies)
        total_enemy_max_hp = sum(e.max_hp for e in alive_enemies)
        total_enemy_brave = sum(getattr(e, 'brave_points', 0) for e in alive_enemies)
        
        print(f"\n{Color.BRIGHT_RED}⚔️ 적군 현황:{Color.RESET}")
        print(f"  생존자: {len(alive_enemies)}명")
        print(f"  총 HP: {total_enemy_hp:,}/{total_enemy_max_hp:,} ({int(total_enemy_hp/total_enemy_max_hp*100) if total_enemy_max_hp > 0 else 0}%)")
        print(f"  총 BRV: {total_enemy_brave:,}")
        print(f"  BREAK 상태: {len([e for e in alive_enemies if hasattr(e, 'is_broken') and e.is_broken])}명")
        
        # 전투 분석
        print(f"\n{Color.BRIGHT_YELLOW}📈 전투 분석:{Color.RESET}")
        
        ally_advantage = total_ally_hp / max(1, total_enemy_hp)
        if ally_advantage > 1.5:
            print(f"  • 🟢 아군 우세 (HP 비율: {ally_advantage:.1f}:1)")
        elif ally_advantage > 0.8:
            print(f"  • 🟡 균등한 상황 (HP 비율: {ally_advantage:.1f}:1)")
        else:
            print(f"  • 🔴 아군 열세 (HP 비율: {ally_advantage:.1f}:1)")
        
        brave_advantage = total_ally_brave / max(1, total_enemy_brave)
        if brave_advantage > 1.5:
            print(f"  • ⚡ BRV 우세 - 적극적인 HP 공격 추천")
        elif brave_advantage < 0.7:
            print(f"  • 💧 BRV 열세 - 방어적인 플레이 추천")
        else:
            print(f"  • ✨ BRV 균등")
        
        input(f"\n{Color.YELLOW}계속하려면 Enter를 누르세요...{Color.RESET}")
    
    def _show_turn_order_prediction(self, all_combatants: List[Character]):
        """턴 순서 예측"""
        print(f"\n{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}⏰ 턴 순서 예측{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        
        # 유효한 전투원만 필터링
        valid_combatants = [c for c in all_combatants if hasattr(c, 'atb_gauge') and c.is_alive]
        
        # ATB 게이지 순으로 정렬
        sorted_by_atb = sorted(valid_combatants, key=lambda x: getattr(x, 'atb_gauge', 0), reverse=True)
        
        print(f"\n🎯 현재 ATB 순서:")
        for i, combatant in enumerate(sorted_by_atb[:8], 1):  # 상위 8명만
            atb_gauge = getattr(combatant, 'atb_gauge', 0)
            is_ally = combatant in [c for c in all_combatants if hasattr(c, 'character_class')]
            
            if atb_gauge >= 100:
                status = f"{Color.BRIGHT_CYAN}⚡준비완료{Color.RESET}"
            elif atb_gauge >= 75:
                status = f"{Color.CYAN}🔶거의 준비{Color.RESET}"
            else:
                status = f"{Color.BLUE}⏳대기중{Color.RESET}"
            
            side_indicator = "🛡️" if is_ally else "⚔️"
            print(f"  {i}. {side_indicator} {combatant.name}: {status} ({int(atb_gauge)}%)")
        
        # 다음 턴 예측
        print(f"\n🔮 다음 5턴 예측:")
        prediction_combatants = [(c, getattr(c, 'atb_gauge', 0)) for c in valid_combatants]
        
        for turn in range(1, 6):
            # ATB 시뮬레이션
            for i, (combatant, atb) in enumerate(prediction_combatants):
                speed = getattr(combatant, 'speed', 50)
                atb_increment = (speed / 50.0) * 8
                prediction_combatants[i] = (combatant, min(100, atb + atb_increment))
            
            # 100% 도달한 캐릭터 찾기
            ready_combatants = [(c, atb) for c, atb in prediction_combatants if atb >= 100]
            if ready_combatants:
                # 가장 높은 ATB의 캐릭터
                next_combatant = max(ready_combatants, key=lambda x: x[1])[0]
                is_ally = next_combatant in [c for c in all_combatants if hasattr(c, 'character_class')]
                side_indicator = "🛡️" if is_ally else "⚔️"
                
                print(f"  턴 {turn}: {side_indicator} {next_combatant.name}")
                
                # 해당 캐릭터의 ATB를 0으로 리셋
                for i, (c, atb) in enumerate(prediction_combatants):
                    if c == next_combatant:
                        prediction_combatants[i] = (c, 0)
                        break
        
        input(f"\n{Color.YELLOW}계속하려면 Enter를 누르세요...{Color.RESET}")
            
    def update_atb_gauges(self, all_combatants: List[Character]):
        """ATB 게이지 업데이트 - 속도 기반 차등 업데이트"""
        for combatant in all_combatants:
            # dict 객체 체크
            if isinstance(combatant, dict):
                print(f"⚠️ 경고: ATB 업데이트 중 dict 객체 발견: {combatant}")
                continue
                
            if combatant.is_alive and hasattr(combatant, 'atb_gauge'):
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
        
        # dict 객체 필터링 및 유효한 combatant만 선택
        valid_combatants = []
        for c in all_combatants:
            if isinstance(c, dict):
                print(f"⚠️ 경고: dict 객체 발견, 건너뜀: {c}")
                continue
            if c.is_alive and hasattr(c, 'atb_gauge'):
                valid_combatants.append(c)
        
        # ATB 순서대로 정렬
        sorted_combatants = sorted(
            valid_combatants, 
            key=lambda x: getattr(x, 'atb_gauge', 0), 
            reverse=True
        )
        
        for i, combatant in enumerate(sorted_combatants[:5]):  # 상위 5명만 표시
            is_enemy = hasattr(combatant, 'is_enemy')
            name_color = Color.BRIGHT_RED if is_enemy else Color.BRIGHT_BLUE
            
            atb_gauge = int(getattr(combatant, 'atb_gauge', 0))
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
            
            # 승리 후 일시정지 - 사용자가 결과를 확인할 시간
            print(f"\n{Color.BRIGHT_YELLOW}전투에서 승리했습니다!{Color.RESET}")
            input(f"{Color.YELLOW}계속하려면 Enter를 누르세요...{Color.RESET}")
            
        else:
            # 패배 이펙트  
            print(f"\n{Color.BRIGHT_RED}{'='*50}")
            print(f"💀 패배... 💀")
            print(f"{'='*50}{Color.RESET}")
            
            # 패배 후 일시정지 - 사용자가 결과를 확인할 시간
            print(f"\n{Color.BRIGHT_RED}전투에서 패배했습니다...{Color.RESET}")
            input(f"{Color.RED}계속하려면 Enter를 누르세요...{Color.RESET}")
            
        return party_alive
    
    def _apply_skill_effects(self, skill, caster, targets):
        """스킬 효과 적용 - New Skill System 호환"""
        from .new_skill_system import SkillType
        
        skill_type = skill.get("type", SkillType.BRV_ATTACK)
        skill_name = skill.get("name", "알 수 없는 스킬")
        
        print(f"🎯 스킬 '{skill_name}' 효과 적용 중...")
        
        for target in targets:
            if skill_type == SkillType.BRV_ATTACK:
                # Brave 공격 - BRV 데미지
                brv_power = skill.get("brv_power", 100)
                damage = self._calculate_brv_damage(skill, caster, target, brv_power)
                
                # BRV 데미지 적용
                old_brv = target.brave_points
                target.brave_points -= damage
                target.brave_points = max(0, target.brave_points)
                
                print(f"⚡ {target.name}의 BRV: {old_brv} → {target.brave_points} (-{damage})")
                
                # 무모한 돌격의 특수 효과: 시전자 BRV 증가
                if "무모한 돌격" in skill_name:
                    brv_gain = int(damage * 0.5)  # 가한 데미지의 50%만큼 BRV 증가
                    old_caster_brv = caster.brave_points
                    caster.brave_points += brv_gain
                    print(f"💪 {caster.name}의 BRV: {old_caster_brv} → {caster.brave_points} (+{brv_gain}) [무모한 돌격 효과]")
                            
                # BREAK 체크
                if target.brave_points <= 0 and hasattr(target, 'apply_break_if_needed'):
                    if target.apply_break_if_needed():
                        print(f"💥 {target.name}이(가) BREAK 상태가 되었습니다!")
                
            elif skill_type == SkillType.HP_ATTACK:
                # HP 공격 - HP 데미지
                hp_power = skill.get("hp_power", 120)
                damage = self._calculate_hp_damage_from_skill(skill, caster, target, hp_power)
                actual_damage = target.take_damage(damage)
                print(f"💥 {target.name}에게 {actual_damage:,} HP 데미지!")
                
            elif skill_type == SkillType.BRV_HP_ATTACK:
                # BRV + HP 복합 공격
                brv_power = skill.get("brv_power", 80)
                hp_power = skill.get("hp_power", 80)
                
                # BRV 데미지
                brv_damage = self._calculate_brv_damage(skill, caster, target, brv_power)
                old_brv = target.brave_points
                target.brave_points -= brv_damage
                target.brave_points = max(0, target.brave_points)
                print(f"⚡ {target.name}의 BRV: {old_brv} → {target.brave_points} (-{brv_damage})")
                
                # HP 데미지
                hp_damage = self._calculate_hp_damage_from_skill(skill, caster, target, hp_power)
                actual_damage = target.take_damage(hp_damage)
                print(f"💥 {target.name}에게 {actual_damage:,} HP 데미지!")
                
            elif skill_type == SkillType.HEAL:
                # 치유
                heal_amount = self._calculate_heal_amount(skill, caster)
                actual_heal = target.heal(heal_amount)
                print(f"💚 {target.name}이(가) {actual_heal:,} HP 회복!")
                
            elif skill_type == SkillType.BUFF:
                # 버프 적용
                self._apply_skill_buff(skill, target)
                print(f"✨ {target.name}에게 버프 적용!")
                
            elif skill_type == SkillType.DEBUFF:
                # 디버프 적용
                self._apply_skill_debuff(skill, target)
                print(f"💀 {target.name}에게 디버프 적용!")
            
            elif skill_type == SkillType.SPECIAL or skill_type == SkillType.ULTIMATE:
                # 특수/궁극기 스킬
                self._apply_special_skill(skill, caster, target)
                
    def _calculate_brv_damage(self, skill, caster, target, brv_power):
        """BRV 데미지 계산"""
        base_attack = getattr(caster, 'physical_attack', 100)
        
        # 회피 체크 (새로운 시스템 사용)
        if self._check_dodge(caster, target):
            print(f"💨 {target.name}이(가) {caster.name}의 {skill.get('name', '스킬')}을(를) 피했습니다!")
            # 회피 SFX 재생
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("dodge")
            elif hasattr(self, 'sound_manager'):
                self.sound_manager.play_sfx("dodge")
            return 0
        
        # 데미지 계산
        import random
        damage = int(brv_power * (base_attack / 100) * random.uniform(0.8, 1.2))
        return max(damage, 1)
    
    def _calculate_hp_damage_from_skill(self, skill, caster, target, hp_power):
        """스킬의 HP 데미지 계산"""
        base_attack = getattr(caster, 'physical_attack', 100)
        target_def = getattr(target, 'physical_defense', 50)
        
        # 기본 데미지 공식
        damage = int(hp_power * (base_attack / max(target_def, 1)) * 1.0)
        
        # Break 상태면 1.5배 데미지
        if hasattr(target, 'is_broken') and target.is_broken:
            damage = int(damage * 1.5)
            print("💥 BREAK 상태로 데미지 증가!")
            
        return max(damage, 1)
    
    def _apply_special_skill(self, skill, caster, target):
        """특수 스킬 효과"""
        skill_name = skill.get("name", "").lower()
        
        if "무모한 돌격" in skill_name:
            # 무모한 돌격: 강력한 HP 공격 + 자신도 데미지
            damage_to_target = self._calculate_hp_damage_from_skill(skill, caster, target, 150)
            actual_damage = target.take_damage(damage_to_target)
            print(f"💥 {target.name}에게 {actual_damage:,} 데미지! (무모한 돌격)")
            
            # 자신에게도 반동 데미지
            self_damage = int(damage_to_target * 0.3)
            caster.take_damage(self_damage)
            print(f"💢 {caster.name}도 반동으로 {self_damage} 데미지를 받았습니다!")
            
        else:
            # 기본 특수 효과
            damage = self._calculate_hp_damage_from_skill(skill, caster, target, 130)
            actual_damage = target.take_damage(damage)
            print(f"✨ {target.name}에게 {actual_damage:,} 특수 데미지!")
            
    def _apply_skill_buff(self, skill, target):
        """스킬 버프 적용"""
        # 간단한 버프 시스템
        buff_type = skill.get("buff_type", "attack")
        buff_value = skill.get("buff_value", 10)
        
        if buff_type == "attack" and hasattr(target, 'temp_attack_bonus'):
            target.temp_attack_bonus = getattr(target, 'temp_attack_bonus', 0) + buff_value
            
    def _apply_skill_debuff(self, skill, target):
        """스킬 디버프 적용"""
        # 간단한 디버프 시스템
        debuff_type = skill.get("debuff_type", "defense")
        debuff_value = skill.get("debuff_value", 10)
        
        if debuff_type == "defense" and hasattr(target, 'temp_defense_penalty'):
            target.temp_defense_penalty = getattr(target, 'temp_defense_penalty', 0) + debuff_value
    
    def _calculate_heal_amount(self, skill, caster):
        """힐량 계산"""
        base_heal = skill.get("base_value", skill.get("heal_power", 100))
        magic_attack = getattr(caster, 'magic_attack', 100)
        
        # 힐량 = 기본량 + (마법공격력 * 0.5)
        heal_amount = int(base_heal + (magic_attack * 0.5))
        return max(heal_amount, 1)
    
    def _apply_buff(self, skill, target):
        """버프 적용"""
        # 간단한 버프 시스템
        buff_type = skill.get("buff_type", "attack")
        buff_value = skill.get("buff_value", 10)
        duration = skill.get("duration", 3)
        
        if buff_type == "attack":
            if hasattr(target, 'temp_attack_bonus'):
                target.temp_attack_bonus += buff_value
            else:
                target.temp_attack_bonus = buff_value
    
    def _apply_debuff(self, skill, target):
        """디버프 적용"""
        # 간단한 디버프 시스템
        debuff_type = skill.get("debuff_type", "defense")
        debuff_value = skill.get("debuff_value", 10)
        duration = skill.get("duration", 3)
        
        if debuff_type == "defense":
            if hasattr(target, 'temp_defense_penalty'):
                target.temp_defense_penalty += debuff_value
            else:
                target.temp_defense_penalty = debuff_value