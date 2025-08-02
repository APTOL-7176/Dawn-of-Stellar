"""
Brave 시스템이 통합된 전투 시스템 - 로깅 시스템 통합
"""

from typing import List, Optional, Tuple
import random
import time
from .character import Character, StatusEffect
from .brave_system import BraveManager, BraveAttackType, BattleEffects, BraveSkill
from .ffvii_sound_system import get_ffvii_sound_system
from .combat_visual import CombatVisualizer, EffectType, Color
from .new_skill_system import StatusType, get_status_icon, skill_system
from .ascii_effects import enhanced_battle_effect, combat_animator
from .combat_visual import get_combat_visualizer
from .stable_display import get_stable_display
from .input_utils import KeyboardInput
from .display import GameDisplay

# BGM 타입 import 시도
try:
    from .audio_system import BGMType, get_audio_manager
except ImportError:
    BGMType = None
    get_audio_manager = None


class BraveCombatSystem:
    """Brave 기반 전투 시스템"""
    
    # ATB 시스템 상수 (100배 확장)
    ATB_MAX = 10000  # 100 → 10000 (100배)
    ATB_READY_THRESHOLD = 10000  # 100% → 10000
    ATB_DISPLAY_SCALE = 100  # 표시용 스케일 (10000 → 100으로 변환)
    
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
        
        # 전투 로깅 시스템 초기화
        from combat_logger import CombatLogger
        self.combat_logger = CombatLogger()
        
        # 🔊 오디오 시스템 진단
        print(f"🎵 오디오 시스템 진단:")
        print(f"  - audio_system: {type(self.audio_system).__name__ if self.audio_system else 'None'}")
        print(f"  - sound_manager: {type(self.sound_manager).__name__ if self.sound_manager else 'None'}")
        print(f"📊 전투 로깅 시스템 활성화됨: {self.combat_logger.session_id}")
        
        # 스킬 시스템 추가
        self.skill_db = skill_system
    
    
    def get_brave_color_emoji(self, brave_points: int) -> str:
        """Brave 포인트에 따른 통일된 이모지 반환"""
        return "⚡"  # 모든 Brave 포인트에 동일 이모지 사용
        
    def start_battle(self, party: List[Character], enemies: List[Character]):
        """전투 시작 - 로깅 시스템 통합"""
        # 현재 파티와 적군 정보 저장 (스킬 승리 체크용)
        self._current_party = party
        self._current_enemies = enemies
        
        # 입력 버퍼 클리어 (전투 시작 전)
        if hasattr(self, 'keyboard') and self.keyboard:
            self.keyboard.clear_input_buffer()
        
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
        
        # 📊 전투 로깅 시작
        self.battle_start_time = time.time()  # 전투 시작 시간 기록
        self.combat_logger.start_battle(party, enemies)
        
        print("\n" + "="*80)
        print("🌟 Dawn Of Stellar - Brave Battle! 🌟")
        print("="*80)
        
        # 모든 참전자의 ATB 게이지 초기화 및 검증
        all_combatants = party + enemies
        valid_combatants = []
        for combatant in all_combatants:
            # dict 객체인 경우 Character 객체로 변환 필요
            if isinstance(combatant, dict):
                print(f"⚠️ 경고: {combatant}는 dict 객체입니다. Character 객체가 아닙니다.")
                continue
            
            # ATB 게이지 속성 확인 및 초기화
            if not hasattr(combatant, 'atb_gauge'):
                combatant.atb_gauge = 0
                print(f"✨ {combatant.name}에 ATB 게이지를 추가했습니다.")
            else:
                combatant.atb_gauge = 0
            
            # 기본 속도 속성 확인
            if not hasattr(combatant, 'speed'):
                combatant.speed = 100
                print(f"✨ {combatant.name}에 기본 속도(100)를 설정했습니다.")
            
            valid_combatants.append(combatant)
        
        if len(valid_combatants) != len(all_combatants):
            print(f"⚠️ 주의: {len(all_combatants) - len(valid_combatants)}개의 무효한 캐릭터가 감지되었습니다.")
        
        # 참조 저장 (action_order 계산용)
        self._current_party = [c for c in party if c in valid_combatants]
        self._current_enemies = [c for c in enemies if c in valid_combatants]
        
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
        
        # 파티 정보를 클래스 변수로 저장
        self._current_party = party
        self._current_enemies = enemies
        
        while True:
            turn_count += 1
            
            # ATB 게이지가 100%에 도달할 때까지 점진적 업데이트
            max_attempts = 200  # 더 많은 시도로 안정성 확보
            attempts = 0
            
            while attempts < max_attempts:
                # ATB 애니메이션과 함께 업데이트 (첫 번째 시도에서만 애니메이션 표시)
                show_animation = (attempts == 0)
                self.update_atb_gauges(party + enemies, show_animation)
                
                # ATB 업데이트 후 전투 종료 체크
                if self.check_battle_end(party, enemies):
                    result = self.determine_winner(party, enemies)
                    print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                    return result
                
                action_order = self.get_action_order(party + enemies)
                if action_order:
                    break
                attempts += 1
                time.sleep(0.1)  # ATB 업데이트 간 딜레이 감소 (더 부드럽게)
            
            if not action_order:
                # ATB 강제 증가로 교착 상태 해결
                print("⚠️ ATB 교착 상태 - 모든 캐릭터의 ATB를 증가시킵니다.")
                for combatant in party + enemies:
                    if combatant.is_alive and hasattr(combatant, 'atb_gauge'):
                        combatant.atb_gauge = min(self.ATB_MAX, combatant.atb_gauge + 1000)
                # 다시 시도
                action_order = self.get_action_order(party + enemies)
                if not action_order:
                    print("❌ ATB 시스템 복구 실패 - 전투를 강제 종료합니다.")
                    return "draw"
            
            print(f"\n--- 턴 {turn_count} ---")
            
            # 선택된 캐릭터의 턴 처리
            character = action_order[0]
            
            if not character.is_alive:
                continue
                
            # 상태이상 처리
            if hasattr(character, 'status_manager'):
                character.status_manager.process_turn_effects(character)
                
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
            
            # 턴 완료 후 ATB 초기화 (중복 초기화 방지)
            if hasattr(character, 'atb_gauge'):
                character.atb_gauge = 0
                print(f"🔄 {character.name}의 턴 완료 - ATB 초기화")
                
            # 상태이상 턴 종료 처리
            if hasattr(character, 'status_manager'):
                character.status_manager.process_turn_effects(character)
                
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
                # BREAK 상태 해제 체크
                if getattr(character, 'is_broken', False) and character.brave_points > 0:
                    character.is_broken = False
                    print(f"✨ {character.name}의 BREAK 상태가 해제되었습니다!")
            
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
        
        # 현재 차례 안내 - 간소화
        print(f"\n{Color.BRIGHT_CYAN}👉 {character.name}의 차례 - 행동을 선택하세요{Color.RESET}")
        
        while True:
            try:
                from .cursor_menu_system import create_simple_menu
                
                # 직업별 Brave 공격 설명 생성
                character_class = getattr(character, 'character_class', '전사')
                class_brave_descriptions = {
                    "전사": "⚡ 방패 강타: 20% 확률로 적 기절",
                    "아크메이지": "⚡ 마력 파동: 적의 마법방어력 10% 감소",
                    "궁수": "⚡ 삼연사: 빠른 3연속 공격",
                    "도적": "⚡ 독침: 독 상태이상 부여",
                    "성기사": "⚡ 성스러운 타격: 공격하며 아군 회복",
                    "암흑기사": "⚡ 흡혈 베기: 피해의 30% HP 회복",
                    "몽크": "⚡ 연환 타격: 타격 표식 중첩",
                    "바드": "⚡ 음파 공격: 아군 사기 증진",
                    "네크로맨서": "⚡ 생명력 흡수: 피해의 50% MP 회복",
                    "용기사": "⚡ 화염 강타: 화상 상태이상 부여",
                    "검성": "⚡ 검기 베기: 뒤의 적들에게도 피해",
                    "정령술사": "⚡ 원소 탄환: 랜덤 원소 약점 적용",
                    "암살자": "⚡ 그림자 습격: 높은 크리티컬 확률",
                    "기계공학자": "⚡ 레이저 사격: 장비 내구도 감소",
                    "무당": "⚡ 영혼 타격: 방어력 무시 피해",
                    "해적": "⚡ 이도류 난타: 30% 확률로 2회 공격",
                    "사무라이": "⚡ 거합 베기: HP 낮을수록 강화",
                    "드루이드": "⚡ 자연의 분노: 공격 후 HP 회복",
                    "철학자": "⚡ 논리적 반박: 다음 턴 회피율 증가",
                    "시간술사": "⚡ 시간 조작: 적의 행동 지연",
                    "연금술사": "⚡ 화학 폭발: 주변 적에게 연쇄 피해",
                    "검투사": "⚡ 투기장 기술: 반격 확률 증가",
                    "기사": "⚡ 창 돌격: 관통 피해",
                    "신관": "⚡ 축복의 빛: 아군에게 축복 버프",
                    "마검사": "⚡ 마법검기: 물리+마법 피해",
                    "차원술사": "⚡ 차원 균열: 적의 정확도 감소",
                    "광전사": "⚡ 광폭화 난타: HP 낮을수록 강화"
                }
                
                # 직업별 HP 공격 설명 생성
                class_hp_descriptions = {
                    "전사": "💀 파괴의 일격: 방어구 내구도 대폭 감소",
                    "아크메이지": "💀 마력 폭발: 주변 적들에게도 피해",
                    "궁수": "💀 관통사격: 뒤의 적들에게 관통 피해",
                    "도적": "💀 암살: 저체력 적 즉사 가능 (보스 제외)",
                    "성기사": "💀 심판의 빛: 아군 전체 상태이상 해제",
                    "암흑기사": "💀 흡혈 강타: 피해의 60% HP 대량 회복",
                    "몽크": "💀 폭렬권: 표식 폭발로 추가 피해",
                    "바드": "💀 영혼의 노래: 아군 전체 회복+버프",
                    "네크로맨서": "💀 영혼 흡수: MP 탈취 및 회복",
                    "용기사": "💀 드래곤 브레스: 광역 화염 피해",
                    "검성": "💀 일섬: 방어력 무시 고정 피해",
                    "정령술사": "💀 원소 융합: 모든 원소 효과 적용",
                    "암살자": "💀 그림자 처형: 3연속 공격",
                    "기계공학자": "💀 메가 레이저: 장비 완전 파괴",
                    "무당": "💀 영혼 분리: 방어력 완전 무시",
                    "해적": "💀 해적의 보물: 4가지 무기 연속 공격",
                    "사무라이": "💀 무사도 비의: 필사의 일격",
                    "드루이드": "💀 자연의 심판: 아군 회복+자연 축복",
                    "철학자": "💀 진리의 깨달음: 약점 공격+버프 해제",
                    "시간술사": "💀 시간 정지: 4연속 공격",
                    "연금술사": "💀 대폭발 반응: 광역 폭발 피해",
                    "검투사": "💀 검투장의 피날레: 4연속 콤보",
                    "기사": "💀 성스러운 돌격: 성스러운 관통 공격",
                    "신관": "💀 신의 심판: 아군 전체 대량 회복",
                    "마검사": "💀 마검 오의: 물리+마법 융합 공격",
                    "차원술사": "💀 차원 붕괴: 공간 자체로 공격",
                    "광전사": "💀 최후의 광기: 광폭화로 최강 일격"
                }
                
                brave_desc = class_brave_descriptions.get(character_class, "⚡ 기본 공격: Brave 포인트 획득")
                hp_desc = class_hp_descriptions.get(character_class, "💀 기본 HP 공격: 적에게 HP 피해")
                
                action_options = ["⚔️ Brave 공격", "💀 HP 공격", "✨ 스킬 사용", "🧪 아이템 사용", "🛡️ 방어", "🌟 특성 활성화", "📊 실시간 상태", "❓ 전투 도움말"]
                action_descriptions = [
                    f"Brave를 높여 강력한 공격을 준비합니다\n{brave_desc}",
                    f"축적된 Brave로 적에게 데미지를 줍니다 (최소 300 BRV 필요)\n{hp_desc}",
                    "캐릭터의 특수 스킬을 사용합니다 (MP 소모)",
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
                    f"⚔️ {character.name}의 차례", 
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
                    # ATB 실시간 업데이트 표시
                    self._show_realtime_atb_status(party, enemies)
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
                
                # 빈 리스트가 반환된 경우 (유효한 대상이 없음)
                if isinstance(targets, list) and len(targets) == 0:
                    target_type = selected_skill.get("target", "single_enemy")
                    if hasattr(target_type, 'value'):
                        target_type_str = target_type.value
                    else:
                        target_type_str = str(target_type).lower()
                    
                    if target_type_str in ["죽은아군1명", "dead_ally"]:
                        print("❌ 부활시킬 대상이 없어 스킬을 취소합니다.")
                    else:
                        print("❌ 유효한 대상이 없어 스킬을 취소합니다.")
                    return False
                
                # 스킬 실행 - 캐스트 타임 적용
                cast_time = selected_skill.get("cast_time", 0)
                
                if cast_time > 0:
                    # 캐스트 타임이 있는 스킬 - ATB 시스템 사용
                    print(f"✨ {character.name}이(가) {selected_skill.get('name', '스킬')} 캐스팅을 시작합니다! [캐스트:{cast_time}%]")
                    
                    # MP 소모는 캐스팅 시작 시
                    character.current_mp -= selected_skill.get("mp_cost", 0)
                    
                    # 캐스팅 시작
                    current_time = getattr(self, 'battle_time', 0)
                    
                    # 캐스팅 관련 속성이 없으면 초기화
                    if not hasattr(character, 'casting_skill'):
                        character.casting_skill = None
                        character.casting_targets = None
                        character.casting_start_time = None
                        character.casting_duration = None
                        character.is_casting = False
                    
                    if hasattr(character, 'start_casting'):
                        character.start_casting(selected_skill, targets, current_time, cast_time)
                    else:
                        # 폴백: 직접 속성 설정
                        character.casting_skill = selected_skill
                        character.casting_targets = targets
                        character.casting_start_time = current_time
                        character.casting_duration = cast_time
                        character.casting_cast_time = cast_time  # ATB 기반 캐스팅용
                        character.is_casting = True
                        character.atb_gauge = 0  # 캐스팅 시작 시 ATB 초기화
                else:
                    # 즉시 시전 스킬
                    self._execute_skill_immediately(selected_skill, character, targets)
                
                return True
            else:
                print("잘못된 선택입니다.")
                return False
                
        except Exception as e:
            print(f"❌ 스킬 메뉴 오류: {e}")
            # 폴백: 방어 선택
            self.defend_action(character)
            return True
    
    def _execute_skill_immediately(self, skill, character, targets):
        """스킬 즉시 실행 (캐스트 타임 없는 스킬용)"""
        # MP 소모
        character.current_mp -= skill.get("mp_cost", 0)
        
        # 실제 스킬 효과 적용
        print(f"✨ {character.name}이(가) {skill.get('name', '스킬')}을(를) 사용했습니다!")
        
        # 🔊 스킬 사용 SFX 재생
        self._play_skill_sfx(skill)
        
        # 시각 효과
        if hasattr(self, 'visualizer') and self.visualizer:
            self.visualizer.show_skill_effect(character, skill.get('name', '스킬'), EffectType.SKILL)
        
        # 실제 스킬 효과 적용
        self._apply_skill_effects(skill, character, targets)
        
        # 스킬 사용 후 전투 종료 체크 (팡파레 재생 포함)
        if hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
            if self.check_battle_end(self._current_party, self._current_enemies):
                winner = self.determine_winner(self._current_party, self._current_enemies)
                if winner:  # 승리 시 팡파레 재생
                    try:
                        print(f"\n{Color.BRIGHT_CYAN}전투가 종료되었습니다!{Color.RESET}")
                        # 같은 팡파레 재생 로직 사용
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
                return winner  # 전투 종료 신호 반환
    
    def complete_casting(self, character):
        """캐스팅 완료 처리 - 게임 종료 시 예외처리 포함"""
        try:
            if not hasattr(character, 'casting_skill') or not character.casting_skill:
                return
            
            # 캐릭터가 전투불능 상태인지 체크
            if not character.is_alive:
                print(f"⚠️ {character.name}이(가) 전투불능 상태로 캐스팅이 중단되었습니다.")
                self._clear_casting_state(character)
                return
            
            skill = character.casting_skill
            targets = getattr(character, 'casting_targets', [])
            
            # 대상들이 여전히 유효한지 체크
            valid_targets = []
            for target in targets:
                if hasattr(target, 'is_alive') and target.is_alive:
                    valid_targets.append(target)
                else:
                    print(f"⚠️ 대상 {getattr(target, 'name', '알 수 없음')}이(가) 유효하지 않아 제외됩니다.")
            
            # 유효한 대상이 없으면 캐스팅 취소
            if not valid_targets and skill.get('target') not in ['self', '자신']:
                print(f"⚠️ 유효한 대상이 없어 {character.name}의 {skill.get('name', '스킬')} 캐스팅이 취소되었습니다.")
                self._clear_casting_state(character)
                return
            
            print(f"✨ {character.name}의 {skill.get('name', '스킬')} 캐스팅이 완료되었습니다!")
            
            # 🔊 스킬 사용 SFX 재생
            self._play_skill_sfx(skill)
            
            # 시각 효과
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.show_skill_effect(character, skill.get('name', '스킬'), EffectType.SKILL)
            
            # 실제 스킬 효과 적용
            self._apply_skill_effects(skill, character, valid_targets if valid_targets else targets)
            
            # 캐스팅 완료 후 전투 종료 체크 (중복 방지)
            if hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
                if self.check_battle_end(self._current_party, self._current_enemies):
                    # 전투 종료만 체크하고 승리 처리는 다른 곳에서 담당
                    return True  # 전투 종료 신호만 반환
            
        except Exception as e:
            print(f"❌ 캐스팅 완료 중 오류 발생: {e}")
        finally:
            # 캐스팅 상태 초기화 (항상 실행)
            self._clear_casting_state(character)
    
    def _clear_casting_state(self, character):
        """캐스팅 상태 완전 초기화"""
        try:
            character.casting_skill = None
            character.casting_targets = None
            character.casting_start_time = None
            character.casting_duration = None
            character.is_casting = False
        except Exception as e:
            print(f"⚠️ 캐스팅 상태 초기화 중 오류: {e}")
    
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
                        status += f" [WOUND: {ally.wounds}]"
                    
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
                        status += f" [WOUND: {ally.wounds}]"
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
                break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}" if (hasattr(enemy, 'is_broken') and enemy.is_broken) else ""
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
                break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}" if (hasattr(enemy, 'is_broken') and enemy.is_broken) else ""
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
            # 직업별 기본 공격
            from .brave_system import BraveSkill
            skill = self._get_class_specific_basic_attack(attacker)
            
        # 스킬 사용 비주얼 이펙트
        if hasattr(self, 'visualizer') and self.visualizer:
            self.visualizer.show_skill_effect(attacker, skill.name, EffectType.SKILL)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("skill", skill_name=skill.name, character_name=attacker.name)
        
        # HP 희생 처리
        if hasattr(skill, 'hp_sacrifice_rate') and skill.hp_sacrifice_rate > 0:
            sacrifice_hp = max(1, int(attacker.current_hp * skill.hp_sacrifice_rate))
            attacker.current_hp = max(1, attacker.current_hp - sacrifice_hp)
            print(f"💔 {attacker.name}이(가) {sacrifice_hp} HP를 희생하여 위력을 극대화!")
            
            # 희생한 HP만큼 추가 데미지 보너스 (스킬 데미지 계산에 반영)
            attacker.temp_sacrifice_power = getattr(attacker, 'temp_sacrifice_power', 0) + sacrifice_hp * 2
        
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
        
        # 데미지 계산 - 강화된 로깅 시스템 사용
        # 아군과 적군을 구분하여 배율 조정
        if hasattr(skill, '__dict__') and skill.__dict__.get('name') != '기본 공격':
            # 스킬의 경우 - BraveSkill 객체의 brave_multiplier 사용
            original_power = skill.brave_multiplier  # 배율을 그대로 사용 (1.5 = 150%)
            if hasattr(attacker, 'character_class'):  # 아군(플레이어 캐릭터)
                brv_power = int(original_power * 100 * 0.8)  # 아군 스킬 80%로 조정 (기본공격의 1.6배 정도)
            else:  # 적군
                brv_power = int(original_power * 100 * 0.8)  # 적군 스킬 80%로 약화
        elif hasattr(skill, 'name') and skill.name != '기본 공격':
            # 스킬의 경우 - BraveSkill 객체의 brave_multiplier 사용
            original_power = getattr(skill, 'brave_multiplier', 1.0)  # 배율을 그대로 사용
            if hasattr(attacker, 'character_class'):  # 아군(플레이어 캐릭터)
                brv_power = int(original_power * 100 * 0.8)  # 아군 스킬 80%로 조정 (기본공격의 1.6배 정도)
            else:  # 적군
                brv_power = int(original_power * 100 * 0.8)  # 적군 스킬 80%로 약화
        else:
            # 기본 공격의 경우 - 적군을 약화
            if hasattr(attacker, 'character_class'):  # 아군(플레이어 캐릭터)
                brv_power = 50  # 아군 기본공격 50% 유지
            else:  # 적군
                brv_power = 65  # 적군 기본공격 65%로 약화 (75% → 65%)
            
        brave_damage = self._calculate_brv_damage(skill.__dict__ if hasattr(skill, '__dict__') else {"name": skill.name, "brv_power": brv_power}, attacker, target, brv_power)
        
        # BRV 피해량 2.5배 증가 (전투 속도 개선) - 이미 combat_logger에서 적용됨
        # brave_damage = int(brave_damage * 2.5)  # 제거
        
        # BRV 데미지 최소/최댓값 제한 (1 ~ 999999)
        brave_damage = max(1, min(999999, brave_damage))
        
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
        
        # Brave 포인트 적용 (아군/적군 구분)
        if attacker and hasattr(attacker, 'character_class') and attacker.character_class != "Enemy":
            # 아군 → 적: 33% 획득 (1/3)
            gained_brave = int(brave_damage * 0.33)
        else:
            # 적 → 아군: 300% 획득 (3배)
            gained_brave = int(brave_damage * 3)
        
        attacker.add_brave_points(gained_brave)
        
        # BRV 데미지 적용
        target.brave_points -= brave_damage
        
        # BREAK 체크 - BRV가 0 이하가 되면 BREAK 발생
        if target.brave_points <= 0:
            target.brave_points = 0
            # BREAK 상태 적용
            if not getattr(target, 'is_broken', False):
                target.is_broken = True
                
                # ATB 게이지 초기화 (BREAK 시)
                target.atb_gauge = 0
                print(f"🔄 {target.name}의 ATB 게이지가 초기화되었습니다!")
                
                # 캐스팅 중단 (BREAK 시)
                if hasattr(target, 'is_casting') and target.is_casting:
                    skill_name = getattr(target, 'casting_skill', {}).get('name', '스킬')
                    print(f"❌ {target.name}의 {skill_name} 캐스팅이 중단되었습니다!")
                    self._clear_casting_state(target)
                
                self.visualizer.show_status_change(target, "BREAK!", False)
                print(f"💥 {target.name}이(가) BREAK 상태가 되었습니다!")
                # Break 전용 효과음 재생
                if hasattr(self, 'sound_system'):
                    self.sound_system.play_sfx("break_sound")
                enhanced_battle_effect("break")
        
        # Brave 변화 비주얼 이펙트
        self.visualizer.show_brave_change(attacker, gained_brave, attacker.brave_points)
            
        enhanced_battle_effect("brave_gain", amount=gained_brave, total=attacker.brave_points)
        
        # 직업별 특수 효과 적용
        if hasattr(skill, 'name'):
            self._apply_class_specific_brv_effects(attacker, target, skill, brave_damage)
    
    def _get_class_specific_basic_attack(self, character: Character):
        """직업별 특화된 기본공격 반환 (28개 직업 완전 지원)"""
        from .brave_system import BraveSkill
        
        character_class = getattr(character, 'character_class', '전사')
        
        # 직업별 기본공격 정의 (28개 직업)
        class_attacks = {
            "전사": BraveSkill("방패 강타", BraveAttackType.BRAVE, 0.4, description="방패로 강하게 내려쳐 적을 기절시킬 확률"),
            "아크메이지": BraveSkill("마력 파동", BraveAttackType.BRAVE, 0.25, description="마력을 파동으로 방출하여 적의 마법방어력 감소"),
            "궁수": BraveSkill("삼연사", BraveAttackType.BRAVE, 0.15, description="빠르게 세 발의 화살을 연속 발사"),
            "도적": BraveSkill("독침", BraveAttackType.BRAVE, 0.3, description="독을 바른 단검으로 공격하여 독 상태이상 부여"),
            "성기사": BraveSkill("성스러운 타격", BraveAttackType.BRAVE, 0.35, description="성스러운 힘이 깃든 공격으로 아군 회복 효과"),
            "암흑기사": BraveSkill("흡혈 베기", BraveAttackType.BRAVE, 0.45, description="적의 생명력을 흡수하여 자신의 HP 회복"),
            "몽크": BraveSkill("연환 타격", BraveAttackType.BRAVE, 0.28, description="연속 타격으로 적에게 '표식' 중첩"),
            "바드": BraveSkill("음파 공격", BraveAttackType.BRAVE, 0.2, description="음파로 공격하며 아군들의 사기 증진"),
            "네크로맨서": BraveSkill("생명력 흡수", BraveAttackType.BRAVE, 0.35, description="적의 생명력을 흡수하여 MP 회복"),
            "용기사": BraveSkill("화염 강타", BraveAttackType.BRAVE, 0.42, description="용의 숨결을 실은 공격으로 화상 부여"),
            "검성": BraveSkill("검기 베기", BraveAttackType.BRAVE, 0.38, description="검기를 날려 원거리에서도 공격 가능"),
            "정령술사": BraveSkill("원소 탄환", BraveAttackType.BRAVE, 0.3, description="랜덤 원소로 공격하며 속성 약점 적용"),
            "암살자": BraveSkill("그림자 습격", BraveAttackType.BRAVE, 0.5, description="그림자에서 나타나 강력한 일격, 높은 크리티컬 확률"),
            "기계공학자": BraveSkill("레이저 사격", BraveAttackType.BRAVE, 0.32, description="레이저로 정밀 타격하며 장비 내구도 감소"),
            "무당": BraveSkill("영혼 타격", BraveAttackType.BRAVE, 0.25, description="영혼을 직접 타격하여 방어력 무시"),
            "해적": BraveSkill("이도류 난타", BraveAttackType.BRAVE, 0.2, description="양손 무기로 연속 공격"),
            "사무라이": BraveSkill("거합 베기", BraveAttackType.BRAVE, 0.55, description="단숨에 베는 강력한 일격, 낮은 HP일수록 강화"),
            "드루이드": BraveSkill("자연의 분노", BraveAttackType.BRAVE, 0.3, description="자연의 힘으로 공격하며 턴마다 HP 회복"),
            "철학자": BraveSkill("논리적 반박", BraveAttackType.BRAVE, 0.15, description="적의 행동을 예측하여 반격, 높은 회피율"),
            "시간술사": BraveSkill("시간 조작", BraveAttackType.BRAVE, 0.25, description="시간을 조작하여 적의 행동 지연"),
            "연금술사": BraveSkill("화학 폭발", BraveAttackType.BRAVE, 0.35, description="화학 반응으로 폭발 피해, 주변 적에게도 영향"),
            "검투사": BraveSkill("투기장 기술", BraveAttackType.BRAVE, 0.4, description="검투장에서 익힌 기술로 반격 확률 증가"),
            "기사": BraveSkill("창 돌격", BraveAttackType.BRAVE, 0.45, description="창으로 돌격하여 관통 피해"),
            "신관": BraveSkill("축복의 빛", BraveAttackType.BRAVE, 0.2, description="적을 공격하면서 아군에게 축복 버프 부여"),
            "마검사": BraveSkill("마법검기", BraveAttackType.BRAVE, 0.4, description="물리와 마법이 결합된 공격"),
            "차원술사": BraveSkill("차원 균열", BraveAttackType.BRAVE, 0.35, description="차원을 찢어 공간 피해"),
            "광전사": BraveSkill("광폭화 난타", BraveAttackType.BRAVE, 0.6, description="이성을 잃고 폭주하는 공격, HP가 낮을수록 강화"),
        }
        
        return class_attacks.get(character_class, BraveSkill("기본 공격", BraveAttackType.BRAVE, 0.33))
        
    def _apply_class_specific_brv_effects(self, attacker: Character, target: Character, skill, damage: int):
        """직업별 BRV 공격 특수 효과 적용 (28개 직업 완전 지원)"""
        character_class = getattr(attacker, 'character_class', '전사')
        
        if character_class == "전사" and skill.name == "방패 강타":
            # 20% 확률로 적 기절 (보스는 저항)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            stun_chance = 0.05 if is_boss else 0.2  # 보스 5%, 일반 20%
            if random.random() < stun_chance:
                setattr(target, 'is_stunned', True)
                print(f"💫 {target.name}이(가) 기절했습니다!")
            elif is_boss:
                print(f"🛡️ {target.name}이(가) 기절에 저항했습니다!")
                
        elif character_class == "아크메이지" and skill.name == "마력 파동":
            # 적의 마법방어력 곱적용 감소 (보스는 저항) + 원거리
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss and random.random() < 0.7:  # 보스는 70% 저항
                print(f"🛡️ {target.name}이(가) 마력 파동에 저항했습니다!")
            else:
                reduction_multiplier = 0.9 if is_boss else 0.85  # 보스 10% 감소, 일반 15% 감소
                current_mdef_mult = getattr(target, 'temp_mdef_multiplier', 1.0)
                setattr(target, 'temp_mdef_multiplier', current_mdef_mult * reduction_multiplier)
                setattr(target, 'mdef_reduction_turns', 3)
                reduction_percent = int((1 - reduction_multiplier) * 100)
                print(f"🔮 {target.name}의 마법방어력이 {reduction_percent}% 감소했습니다!")
            
            # 마법 원거리 공격 - ATB 소모량 감소
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(attacker.atb_gauge * 0.25)  # 25% 절약
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"🌟 마법 원거리 공격으로 ATB {atb_save//self.ATB_DISPLAY_SCALE}% 절약!")
            
        elif character_class == "궁수" and skill.name == "삼연사":
            # 3연타 추가 공격 (원거리 - ATB 30% 절약)
            for i in range(2):  # 이미 1번 공격했으므로 2번 더
                additional_damage = int(damage * 0.7)  # 후속 공격은 70% 위력
                target.brave_points -= additional_damage
                gained_brave = int(additional_damage * 0.33)
                attacker.add_brave_points(gained_brave)
                print(f"🏹 연속 공격 {i+2}번째: {additional_damage} BRV 피해!")
            
            # 원거리 공격 - ATB 소모량 감소
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(attacker.atb_gauge * 0.3)  # 30% 절약
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"🎯 원거리 공격으로 ATB {atb_save//self.ATB_DISPLAY_SCALE}% 절약!")
                
        elif character_class == "도적" and skill.name == "독침":
            # 독 상태이상 부여 (보스는 저항)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss and random.random() < 0.8:  # 보스는 80% 저항
                print(f"🛡️ {target.name}이(가) 독에 저항했습니다!")
            else:
                setattr(target, 'is_poisoned', True)
                setattr(target, 'poison_turns', 3)
                poison_damage = int(target.max_hp * 0.03) if is_boss else int(target.max_hp * 0.05)  # 보스 3%, 일반 5%
                setattr(target, 'poison_damage', poison_damage)
                print(f"💚 {target.name}이(가) 독에 중독되었습니다!")
            
        elif character_class == "성기사" and skill.name == "성스러운 타격":
            # 공격하면서 아군 중 HP가 가장 낮은 대상 회복
            if hasattr(self, '_current_party') and self._current_party:
                lowest_hp_ally = min([ally for ally in self._current_party if ally.current_hp > 0], 
                                   key=lambda x: x.current_hp / x.max_hp, default=None)
                if lowest_hp_ally:
                    heal_amount = int(damage * 0.3)
                    lowest_hp_ally.heal(heal_amount)
                    print(f"✨ {lowest_hp_ally.name}이(가) {heal_amount} HP 회복!")
                    
        elif character_class == "암흑기사" and skill.name == "흡혈 베기":
            # 가한 피해의 30% HP 회복
            heal_amount = int(damage * 0.3)
            attacker.heal(heal_amount)
            print(f"🩸 {attacker.name}이(가) {heal_amount} HP 회복!")
            
        elif character_class == "몽크" and skill.name == "연환 타격":
            # 적에게 '타격 표식' 중첩 (최대 5중첩, 받는 물리피해 곱적용 증가)
            current_marks = getattr(target, 'strike_marks', 0)
            new_marks = min(current_marks + 1, 5)
            setattr(target, 'strike_marks', new_marks)
            
            # 곱적용 피해 증가
            current_damage_mult = getattr(target, 'temp_damage_taken_multiplier', 1.0)
            mark_multiplier = 1.0 + (new_marks * 0.06)  # 중첩당 6% 증가
            setattr(target, 'temp_damage_taken_multiplier', mark_multiplier)
            
            damage_increase = int(new_marks * 6)
            print(f"👊 {target.name}에게 타격 표식 {new_marks}중첩! (받는 물리피해 +{damage_increase}%)")
            
        elif character_class == "바드" and skill.name == "음파 공격":
            # 아군 전체 사기 증진 (곱적용 버프)
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally.current_hp > 0:
                        current_attack_mult = getattr(ally, 'temp_attack_multiplier', 1.0)
                        setattr(ally, 'temp_attack_multiplier', current_attack_mult * 1.08)  # 8% 증가
                        setattr(ally, 'morale_boost_turns', 3)
                print(f"🎵 아군 전체의 사기가 높아졌습니다! (공격력 8% 증가)")
                
        elif character_class == "네크로맨서" and skill.name == "생명력 흡수":
            # 가한 피해의 30% MP 회복 (제한적)
            mp_recover = int(damage * 0.3)  # 50% → 30%로 감소
            old_mp = attacker.current_mp
            max_recover = int(attacker.max_mp * 0.15)  # 최대 MP의 15%까지만 회복 가능
            actual_recover = min(mp_recover, max_recover, attacker.max_mp - attacker.current_mp)
            attacker.current_mp = min(attacker.max_mp, attacker.current_mp + actual_recover)
            if actual_recover > 0:
                print(f"💀 {attacker.name}이(가) {actual_recover} MP 회복! (제한적 흡수)")
                
        elif character_class == "용기사" and skill.name == "화염 강타":
            # 화상 상태이상 부여 (보스는 저항)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss and random.random() < 0.75:  # 보스는 75% 저항
                print(f"🛡️ {target.name}이(가) 화상에 저항했습니다!")
            else:
                setattr(target, 'is_burning', True)
                setattr(target, 'burn_turns', 3)
                burn_damage = int(target.max_hp * 0.02) if is_boss else int(target.max_hp * 0.04)  # 보스 2%, 일반 4%
                setattr(target, 'burn_damage', burn_damage)
                print(f"🔥 {target.name}이(가) 화상에 걸렸습니다!")
            
        elif character_class == "검성" and skill.name == "검기 베기":
            # 검기가 뒤의 적들에게도 피해 (50% 위력)
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                if other_enemies:
                    splash_damage = int(damage * 0.5)
                    for enemy in other_enemies[:2]:  # 최대 2명까지
                        enemy.brave_points -= splash_damage
                        print(f"⚔️ 검기가 {enemy.name}에게도 {splash_damage} BRV 피해!")
                        
        elif character_class == "정령술사" and skill.name == "원소 탄환":
            # 랜덤 원소 속성 약점 적용
            elements = ["화염", "냉기", "번개", "독"]
            element = random.choice(elements)
            bonus_damage = int(damage * 0.2)
            target.brave_points -= bonus_damage
            print(f"🌟 {element} 속성 약점! 추가 {bonus_damage} BRV 피해!")
            
        elif character_class == "암살자" and skill.name == "그림자 습격":
            # 높은 크리티컬 확률로 추가 공격
            if random.random() < 0.4:  # 40% 확률
                crit_damage = int(damage * 0.8)
                target.brave_points -= crit_damage
                gained_brave = int(crit_damage * 0.33)
                attacker.add_brave_points(gained_brave)
                print(f"🗡️ 그림자 크리티컬! 추가 {crit_damage} BRV 피해!")
                
        elif character_class == "기계공학자" and skill.name == "레이저 사격":
            # 적의 장비 내구도 감소 + 원거리
            if hasattr(target, 'equipped_weapon') and target.equipped_weapon:
                if hasattr(target.equipped_weapon, 'durability'):
                    target.equipped_weapon.durability = max(0, target.equipped_weapon.durability - 5)
                    print(f"🔧 {target.name}의 무기 내구도가 5 감소!")
            
            # 레이저 원거리 공격 - ATB 소모량 감소
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(attacker.atb_gauge * 0.20)  # 20% 절약
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"⚡ 레이저 원거리 공격으로 ATB {atb_save//self.ATB_DISPLAY_SCALE}% 절약!")
                    
        elif character_class == "무당" and skill.name == "영혼 타격":
            # 방어력 무시 피해
            spirit_damage = int(damage * 0.5)
            target.brave_points -= spirit_damage
            print(f"👻 영혼 직격! 방어력 무시 {spirit_damage} 추가 BRV 피해!")
            
        elif character_class == "해적" and skill.name == "이도류 난타":
            # 30% 확률로 2회 공격
            if random.random() < 0.3:
                second_damage = int(damage * 0.8)
                target.brave_points -= second_damage
                gained_brave = int(second_damage * 0.33)
                attacker.add_brave_points(gained_brave)
                print(f"⚔️ 이도류 연속 공격! 추가 {second_damage} BRV 피해!")
                
        elif character_class == "사무라이" and skill.name == "거합 베기":
            # HP가 낮을수록 피해 증가
            hp_ratio = attacker.current_hp / attacker.max_hp
            if hp_ratio < 0.5:
                bonus_damage = int(damage * (1 - hp_ratio))
                target.brave_points -= bonus_damage
                print(f"⚔️ 각오의 일격! HP가 낮아 추가 {bonus_damage} BRV 피해!")
                
        elif character_class == "드루이드" and skill.name == "자연의 분노":
            # 공격 후 자신 HP 회복
            heal_amount = int(damage * 0.2)
            attacker.heal(heal_amount)
            print(f"🌿 자연의 가호로 {attacker.name}이(가) {heal_amount} HP 회복!")
            
        elif character_class == "철학자" and skill.name == "논리적 반박":
            # 다음 턴 회피율 증가
            setattr(attacker, 'temp_dodge_bonus', getattr(attacker, 'temp_dodge_bonus', 0) + 0.3)
            setattr(attacker, 'dodge_bonus_turns', 2)
            print(f"🧠 논리적 분석으로 {attacker.name}의 회피율이 증가!")
            
        elif character_class == "시간술사" and skill.name == "시간 조작":
            # 적의 다음 턴 지연 (ATB 곱적용 감소)
            if hasattr(target, 'atb_gauge'):
                current_atb_mult = getattr(target, 'temp_atb_multiplier', 1.0)
                is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
                reduction = 0.85 if is_boss else 0.7  # 보스 15% 감소, 일반 30% 감소
                setattr(target, 'temp_atb_multiplier', current_atb_mult * reduction)
                setattr(target, 'time_slow_turns', 3)
                reduction_percent = int((1 - reduction) * 100)
                print(f"⏱️ {target.name}의 시간이 {reduction_percent}% 지연되었습니다!")
                
        elif character_class == "연금술사" and skill.name == "화학 폭발":
            # 주변 적들에게 연쇄 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                if other_enemies:
                    chain_damage = int(damage * 0.3)
                    for enemy in other_enemies:
                        enemy.brave_points -= chain_damage
                        print(f"💥 화학 폭발이 {enemy.name}에게 {chain_damage} BRV 피해!")
                        
        elif character_class == "검투사" and skill.name == "투기장 기술":
            # 반격 준비 상태
            setattr(attacker, 'counter_ready', True)
            setattr(attacker, 'counter_turns', 2)
            print(f"🏛️ {attacker.name}이(가) 반격 태세를 갖췄습니다!")
            
        elif character_class == "기사" and skill.name == "창 돌격":
            # 관통 피해로 뒤의 적에게도 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                enemy_index = self._current_enemies.index(target)
                if enemy_index < len(self._current_enemies) - 1:
                    next_enemy = self._current_enemies[enemy_index + 1]
                    if next_enemy.current_hp > 0:
                        pierce_damage = int(damage * 0.6)
                        next_enemy.brave_points -= pierce_damage
                        print(f"🏇 창이 관통하여 {next_enemy.name}에게 {pierce_damage} BRV 피해!")
                        
        elif character_class == "신관" and skill.name == "축복의 빛":
            # 아군 전체에게 축복 버프 부여
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally.current_hp > 0:
                        setattr(ally, 'blessed', True)
                        setattr(ally, 'blessed_turns', 3)
                print(f"🌟 아군 전체가 축복을 받았습니다!")
                
        elif character_class == "마검사" and skill.name == "마법검기":
            # 물리와 마법 피해 동시 적용
            magic_damage = int(damage * 0.5)
            target.brave_points -= magic_damage
            print(f"⚡ 마법검기 추가 피해! {magic_damage} BRV 마법 피해!")
            
        elif character_class == "차원술사" and skill.name == "차원 균열":
            # 공간 왜곡으로 적의 정확도 감소
            setattr(target, 'accuracy_debuff', getattr(target, 'accuracy_debuff', 0) + 0.2)
            setattr(target, 'accuracy_debuff_turns', 3)
            print(f"🌀 {target.name}의 공간이 왜곡되어 정확도가 감소!")
            
        elif character_class == "광전사" and skill.name == "광폭화 난타":
            # HP가 낮을수록 추가 공격
            hp_ratio = attacker.current_hp / attacker.max_hp
            if hp_ratio < 0.3:  # 30% 이하일 때
                bonus_attacks = 2
                for i in range(bonus_attacks):
                    bonus_damage = int(damage * 0.4)
                    target.brave_points -= bonus_damage
                    print(f"😤 광폭화 연타 {i+1}! {bonus_damage} BRV 피해!")
                print(f"💀 광전사의 광기가 폭발했습니다!")
        
    def _get_class_specific_hp_attack(self, character: Character):
        """직업별 특화된 HP 공격 반환 (28개 직업 완전 지원)"""
        from .brave_system import BraveSkill
        
        character_class = getattr(character, 'character_class', '전사')
        
        # 직업별 HP 공격 정의 (28개 직업)
        class_hp_attacks = {
            "전사": BraveSkill("파괴의 일격", BraveAttackType.HP, 0.0, 1.1, description="강력한 일격으로 적의 방어구 내구도 감소"),
            "아크메이지": BraveSkill("마력 폭발", BraveAttackType.HP, 0.0, 1.2, description="마력을 폭발시켜 주변 적들에게도 피해"),
            "궁수": BraveSkill("관통사격", BraveAttackType.HP, 0.0, 1.0, description="강력한 화살로 적을 관통, 뒤의 적들에게도 피해"),
            "도적": BraveSkill("암살", BraveAttackType.HP, 0.0, 1.3, description="치명적인 급소 공격, 크리티컬 확률 대폭 증가"),
            "성기사": BraveSkill("심판의 빛", BraveAttackType.HP, 0.0, 1.1, description="성스러운 빛으로 공격하며 아군 전체 상태이상 해제"),
            "암흑기사": BraveSkill("흡혈 강타", BraveAttackType.HP, 0.0, 1.15, description="강력한 흡혈 공격으로 대량 HP 회복"),
            "몽크": BraveSkill("폭렬권", BraveAttackType.HP, 0.0, 1.0, description="표식이 붙은 적 공격 시 표식 폭발로 추가 피해"),
            "바드": BraveSkill("영혼의 노래", BraveAttackType.HP, 0.0, 0.9, description="적의 영혼을 뒤흔들며 아군 전체 회복"),
            "네크로맨서": BraveSkill("영혼 흡수", BraveAttackType.HP, 0.0, 1.1, description="적의 영혼을 흡수하여 강력한 피해와 함께 MP 대량 회복"),
            "용기사": BraveSkill("드래곤 브레스", BraveAttackType.HP, 0.0, 1.3, description="용의 숨결로 광역 화염 피해"),
            "검성": BraveSkill("일섬", BraveAttackType.HP, 0.0, 1.25, description="완벽한 검기로 일격에 베어넘기는 기술"),
            "정령술사": BraveSkill("원소 융합", BraveAttackType.HP, 0.0, 1.15, description="모든 원소를 융합한 파괴적인 공격"),
            "암살자": BraveSkill("그림자 처형", BraveAttackType.HP, 0.0, 1.4, description="그림자에서 나타나는 완벽한 암살 기술"),
            "기계공학자": BraveSkill("메가 레이저", BraveAttackType.HP, 0.0, 1.2, description="강력한 레이저로 관통 피해와 장비 파괴"),
            "무당": BraveSkill("영혼 분리", BraveAttackType.HP, 0.0, 1.0, description="적의 영혼을 직접 공격하여 방어력 완전 무시"),
            "해적": BraveSkill("해적의 보물", BraveAttackType.HP, 0.0, 1.1, description="숨겨진 보물 무기로 연속 공격"),
            "사무라이": BraveSkill("무사도 비의", BraveAttackType.HP, 0.0, 1.5, description="HP가 낮을수록 강해지는 필사의 일격"),
            "드루이드": BraveSkill("자연의 심판", BraveAttackType.HP, 0.0, 1.0, description="자연의 힘으로 적을 심판하며 아군 전체 회복"),
            "철학자": BraveSkill("진리의 깨달음", BraveAttackType.HP, 0.0, 0.8, description="논리적 공격으로 적의 약점을 정확히 타격"),
            "시간술사": BraveSkill("시간 정지", BraveAttackType.HP, 0.0, 1.1, description="시간을 정지시켜 연속 공격"),
            "연금술사": BraveSkill("대폭발 반응", BraveAttackType.HP, 0.0, 1.3, description="화학 반응으로 거대한 폭발 생성"),
            "검투사": BraveSkill("검투장의 피날레", BraveAttackType.HP, 0.0, 1.2, description="관중들의 환호 속에서 화려한 마무리"),
            "기사": BraveSkill("성스러운 돌격", BraveAttackType.HP, 0.0, 1.15, description="신성한 힘이 깃든 창으로 돌격"),
            "신관": BraveSkill("신의 심판", BraveAttackType.HP, 0.0, 0.9, description="적을 심판하면서 아군 전체 HP 회복"),
            "마검사": BraveSkill("마검 오의", BraveAttackType.HP, 0.0, 1.25, description="물리와 마법의 완벽한 융합 기술"),
            "차원술사": BraveSkill("차원 붕괴", BraveAttackType.HP, 0.0, 1.2, description="차원을 붕괴시켜 공간 자체로 공격"),
            "광전사": BraveSkill("최후의 광기", BraveAttackType.HP, 0.0, 1.6, description="모든 것을 내던진 광폭한 최후의 일격"),
        }
        
        return class_hp_attacks.get(character_class, BraveSkill("기본 HP 공격", BraveAttackType.HP, 0.0, 0.8))
        
    def _apply_class_specific_hp_effects(self, attacker: Character, target: Character, skill, hp_damage: int):
        """직업별 HP 공격 특수 효과 적용 (28개 직업 완전 지원)"""
        character_class = getattr(attacker, 'character_class', '전사')
        
        if character_class == "전사" and skill.name == "파괴의 일격":
            # 방어구 내구도 대폭 감소
            if hasattr(target, 'equipped_armor') and target.equipped_armor:
                if hasattr(target.equipped_armor, 'durability'):
                    durability_loss = 15
                    target.equipped_armor.durability = max(0, target.equipped_armor.durability - durability_loss)
                    print(f"🛡️ {target.name}의 방어구 내구도가 {durability_loss} 감소!")
                    
        elif character_class == "아크메이지" and skill.name == "마력 폭발":
            # 주변 적들에게도 피해 (원본의 50%)
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for other_enemy in other_enemies[:2]:  # 최대 2명까지
                    splash_damage = int(hp_damage * 0.5)
                    other_enemy.take_damage(splash_damage)
                    print(f"💥 마력 폭발 연쇄 피해! {other_enemy.name}이(가) {splash_damage} 피해!")
                    
        elif character_class == "궁수" and skill.name == "관통사격":
            # 뒤의 적들에게 관통 피해 (원본의 70%) + 원거리 ATB 절약
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for other_enemy in other_enemies:
                    pierce_damage = int(hp_damage * 0.7)
                    other_enemy.take_damage(pierce_damage)
                    print(f"🏹 관통 피해! {other_enemy.name}이(가) {pierce_damage} 피해!")
            
            # 원거리 HP 공격 - ATB 소모량 감소
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(self.ATB_MAX * 0.25)  # 25% 절약 (HP 공격이므로 고정값)
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"🎯 원거리 HP 공격으로 ATB {atb_save//self.ATB_DISPLAY_SCALE}% 절약!")
                
        elif character_class == "도적" and skill.name == "암살":
            # 80% 확률로 즉사 효과 (HP 20% 이하 적 대상, 보스급 제외)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if not is_boss and target.current_hp <= target.max_hp * 0.2 and random.random() < 0.8:
                target.current_hp = 0
                print(f"💀 암살 성공! {target.name}이(가) 즉사했습니다!")
            else:
                # 즉사하지 않으면 크리티컬 피해
                crit_multiplier = 2.0 if is_boss else 1.5  # 보스에게는 2배, 일반에게는 1.5배
                extra_damage = int(hp_damage * crit_multiplier)
                target.take_damage(extra_damage)
                print(f"🗡️ 치명상! 추가 {extra_damage} 피해!")
                
        elif character_class == "성기사" and skill.name == "심판의 빛":
            # 아군 전체 상태이상 해제 및 회복
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally.current_hp > 0:
                        # 상태이상 해제
                        setattr(ally, 'is_poisoned', False)
                        setattr(ally, 'is_burning', False)
                        setattr(ally, 'is_stunned', False)
                        # 소량 회복
                        heal_amount = int(ally.max_hp * 0.1)
                        ally.heal(heal_amount)
                print(f"✨ 성스러운 빛으로 아군 전체 정화 및 회복!")
                        
        elif character_class == "암흑기사" and skill.name == "흡혈 강타":
            # 가한 피해의 60% HP 회복
            heal_amount = int(hp_damage * 0.6)
            attacker.heal(heal_amount)
            print(f"🩸 강력한 흡혈로 {attacker.name}이(가) {heal_amount} HP 회복!")
            
        elif character_class == "몽크" and skill.name == "폭렬권":
            # 타격 표식 폭발 추가 피해 (현재 HP 비율 기반)
            marks = getattr(target, 'strike_marks', 0)
            if marks > 0:
                is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
                if is_boss:
                    explosion_damage = int(target.current_hp * 0.04 * marks)  # 보스는 중첩당 현재 HP의 4%
                else:
                    explosion_damage = int(target.current_hp * 0.08 * marks)  # 일반은 중첩당 현재 HP의 8%
                target.take_damage(explosion_damage)
                setattr(target, 'strike_marks', 0)  # 표식 소모
                print(f"💥 표식 폭발! {marks}개 표식으로 {explosion_damage} 추가 피해!")
                
        elif character_class == "바드" and skill.name == "영혼의 노래":
            # 아군 전체 회복 및 버프
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally.current_hp > 0:
                        heal_amount = int(ally.max_hp * 0.15)
                        ally.heal(heal_amount)
                        setattr(ally, 'temp_attack_bonus', getattr(ally, 'temp_attack_bonus', 0) + 10)
                print(f"🎵 영혼의 노래로 아군 전체 회복 및 공격력 증가!")
                
        elif character_class == "네크로맨서" and skill.name == "영혼 흡수":
            # MP 제한적 회복 및 적의 MP 흡수
            mp_drain = int(hp_damage * 0.2)  # 30% → 20%로 감소
            if hasattr(target, 'current_mp'):
                drained_mp = min(target.current_mp, mp_drain)
                target.current_mp -= drained_mp
                
                # 회복량 제한
                max_recover = int(attacker.max_mp * 0.2)  # 최대 MP의 20%까지만
                actual_recover = min(drained_mp, max_recover, attacker.max_mp - attacker.current_mp)
                attacker.current_mp = min(attacker.max_mp, attacker.current_mp + actual_recover)
                print(f"💀 영혼 흡수로 {actual_recover} MP 탈취! (제한적 흡수)")
                
        elif character_class == "용기사" and skill.name == "드래곤 브레스":
            # 광역 화염 피해 및 화상 (보스는 상태이상 저항)
            if hasattr(self, '_current_enemies') and self._current_enemies:
                for enemy in self._current_enemies:
                    if enemy != target and enemy.current_hp > 0:
                        fire_damage = int(hp_damage * 0.4)
                        enemy.take_damage(fire_damage)
                        
                        # 화상 효과 (보스는 저항)
                        is_boss = getattr(enemy, 'is_boss', False) or enemy.max_hp > 2000
                        if not is_boss or random.random() > 0.8:  # 보스 80% 저항
                            setattr(enemy, 'is_burning', True)
                            setattr(enemy, 'burn_turns', 4)
                            burn_damage = int(enemy.max_hp * 0.02) if is_boss else int(enemy.max_hp * 0.04)
                            setattr(enemy, 'burn_damage', burn_damage)
                            print(f"🔥 드래곤 브레스! {enemy.name}이(가) {fire_damage} 화염 피해 및 화상!")
                        else:
                            print(f"🔥 드래곤 브레스! {enemy.name}이(가) {fire_damage} 화염 피해! (화상 저항)")
                        
        elif character_class == "검성" and skill.name == "일섬":
            # 완벽한 베기로 방어력 무시 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss:
                ignore_damage = int(target.current_hp * 0.15)  # 보스는 현재 HP의 15%
            else:
                ignore_damage = int(target.current_hp * 0.35)  # 일반 적은 현재 HP의 35%
            target.take_damage(ignore_damage)
            print(f"⚔️ 완벽한 일섬! 방어력 무시 {ignore_damage} 고정 피해!")
            
        elif character_class == "정령술사" and skill.name == "원소 융합":
            # 모든 원소 효과 동시 적용 (보스는 저항)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            
            # 화염 효과
            if not is_boss or random.random() > 0.75:  # 보스 75% 저항
                setattr(target, 'is_burning', True)
                setattr(target, 'burn_turns', 3)
                print(f"🔥 화염 효과 적용!")
            elif is_boss:
                print(f"🛡️ {target.name}이(가) 화염에 저항!")
                
            # 냉기 효과 (속도 감소) - 디버프이므로 보스에게도 적용
            current_speed_mult = getattr(target, 'temp_speed_multiplier', 1.0)
            reduction = 0.85 if is_boss else 0.7  # 보스 15% 감소, 일반 30% 감소
            setattr(target, 'temp_speed_multiplier', current_speed_mult * reduction)
            setattr(target, 'speed_debuff_turns', 3)
            
            # 번개 효과 (기절 확률)
            stun_chance = 0.1 if is_boss else 0.3  # 보스 10%, 일반 30%
            if random.random() < stun_chance:
                setattr(target, 'is_stunned', True)
                print(f"⚡ 번개로 기절!")
            elif is_boss:
                print(f"🛡️ {target.name}이(가) 기절에 저항!")
                
            print(f"🌟 원소 융합! {target.name}에게 다중 원소 효과 적용!")
            
        elif character_class == "암살자" and skill.name == "그림자 처형":
            # 그림자에서 연속 공격
            for i in range(3):  # 3연속 공격
                shadow_damage = int(hp_damage * 0.4)
                target.take_damage(shadow_damage)
                print(f"🗡️ 그림자 연격 {i+1}: {shadow_damage} 피해!")
                
        elif character_class == "기계공학자" and skill.name == "메가 레이저":
            # 관통 레이저 및 장비 완전 파괴 + 원거리 ATB 절약
            if hasattr(self, '_current_enemies') and self._current_enemies:
                hit_targets = [target] + [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for hit_target in hit_targets:
                    if hit_target != target:
                        laser_damage = int(hp_damage * 0.6)
                        hit_target.take_damage(laser_damage)
                        print(f"⚡ 레이저 관통! {hit_target.name}이(가) {laser_damage} 피해!")
                    # 장비 파괴
                    if hasattr(hit_target, 'equipped_weapon') and hit_target.equipped_weapon:
                        if hasattr(hit_target.equipped_weapon, 'durability'):
                            hit_target.equipped_weapon.durability = 0
                            print(f"🔧 {hit_target.name}의 무기가 완전히 파괴되었습니다!")
            
            # 원거리 HP 공격 - ATB 소모량 감소
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(self.ATB_MAX * 0.20)  # 20% 절약
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"⚡ 메가 레이저 원거리 공격으로 ATB {atb_save//self.ATB_DISPLAY_SCALE}% 절약!")
                            
        elif character_class == "무당" and skill.name == "영혼 분리":
            # 방어력 완전 무시 및 영혼 디버프 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss:
                soul_damage = int(target.current_hp * 0.12)  # 보스는 현재 HP의 12%
            else:
                soul_damage = int(target.current_hp * 0.28)  # 일반 적은 현재 HP의 28%
            target.take_damage(soul_damage)
            setattr(target, 'soul_weakness', True)  # 영혼 약화 (모든 저항 감소)
            setattr(target, 'soul_weakness_turns', 5)
            print(f"👻 영혼 분리! {soul_damage} 고정 피해 및 영혼 약화!")
            
        elif character_class == "해적" and skill.name == "해적의 보물":
            # 숨겨진 보물 무기들로 연속 공격
            weapons = ["구식 대포", "저주받은 검", "크라켄의 촉수", "바다뱀의 독침"]
            for weapon in weapons:
                weapon_damage = int(hp_damage * 0.3)
                target.take_damage(weapon_damage)
                print(f"🏴‍☠️ {weapon} 공격! {weapon_damage} 피해!")
                
        elif character_class == "사무라이" and skill.name == "무사도 비의":
            # HP가 낮을수록 강해지는 필사의 일격
            hp_ratio = attacker.current_hp / attacker.max_hp
            desperation_multiplier = 2.0 - hp_ratio  # HP가 낮을수록 최대 2배
            bonus_damage = int(hp_damage * (desperation_multiplier - 1))
            target.take_damage(bonus_damage)
            print(f"⚔️ 무사도 비의! 필사의 각오로 {bonus_damage} 추가 피해!")
            # 반격 확률 증가
            setattr(attacker, 'temp_counter_rate', 0.5)
            
        elif character_class == "드루이드" and skill.name == "자연의 심판":
            # 자연의 힘으로 심판하며 아군 회복
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally.current_hp > 0:
                        nature_heal = int(ally.max_hp * 0.2)
                        ally.heal(nature_heal)
                        # 자연의 축복 (독/화상 저항)
                        setattr(ally, 'nature_blessing', True)
                        setattr(ally, 'nature_blessing_turns', 3)
                print(f"🌿 자연의 심판! 아군 전체 회복 및 자연의 축복!")
                
        elif character_class == "철학자" and skill.name == "진리의 깨달음":
            # 논리적 약점 공격으로 정확한 피해 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss:
                weakness_damage = int(target.current_hp * 0.08)  # 보스는 현재 HP의 8%
            else:
                weakness_damage = int(target.current_hp * 0.22)  # 일반 적은 현재 HP의 22%
            target.take_damage(weakness_damage)
            # 적의 모든 버프 해제 (디버프는 보스에게도 적용)
            if hasattr(target, 'temp_attack_bonus'):
                setattr(target, 'temp_attack_bonus', 0)
            if hasattr(target, 'temp_defense_bonus'):
                setattr(target, 'temp_defense_bonus', 0)
            print(f"🧠 진리의 깨달음! 약점 {weakness_damage} 피해 및 모든 버프 해제!")
            
        elif character_class == "시간술사" and skill.name == "시간 정지":
            # 시간 정지 중 연속 공격
            for i in range(4):  # 4회 연속 공격
                time_damage = int(hp_damage * 0.25)
                target.take_damage(time_damage)
                print(f"⏰ 시간 정지 공격 {i+1}: {time_damage} 피해!")
            # 적의 ATB 게이지 곱적용 감소
            if hasattr(target, 'atb_gauge'):
                current_atb_mult = getattr(target, 'temp_atb_multiplier', 1.0)
                is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
                time_reduction = 0.7 if is_boss else 0.5  # 보스 30% 감소, 일반 50% 감소
                setattr(target, 'temp_atb_multiplier', current_atb_mult * time_reduction)
                setattr(target, 'time_stop_turns', 2)
                reduction_percent = int((1 - time_reduction) * 100)
                print(f"⏱️ {target.name}의 시간이 {reduction_percent}% 크게 지연되었습니다!")
                
        elif character_class == "연금술사" and skill.name == "대폭발 반응":
            # 거대한 폭발로 광역 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                for enemy in self._current_enemies:
                    if enemy.current_hp > 0:
                        explosion_damage = int(hp_damage * 0.8) if enemy == target else int(hp_damage * 0.5)
                        enemy.take_damage(explosion_damage)
                        # 폭발 후유증 (방어력 곱적용 감소)
                        setattr(enemy, 'explosion_weakness', True)
                        setattr(enemy, 'explosion_weakness_turns', 3)
                        current_def_mult = getattr(enemy, 'temp_defense_multiplier', 1.0)
                        is_boss = getattr(enemy, 'is_boss', False) or enemy.max_hp > 2000
                        def_reduction = 0.9 if is_boss else 0.8  # 보스 10% 감소, 일반 20% 감소
                        setattr(enemy, 'temp_defense_multiplier', current_def_mult * def_reduction)
                        if enemy != target:
                            print(f"💥 대폭발 연쇄! {enemy.name}이(가) {explosion_damage} 피해!")
                reduction_percent = int((1 - (0.9 if any(getattr(e, 'is_boss', False) or e.max_hp > 2000 for e in self._current_enemies) else 0.8)) * 100)
                print(f"💥 연금술 대폭발! 모든 적이 방어력 {reduction_percent}% 감소!")
                
        elif character_class == "검투사" and skill.name == "검투장의 피날레":
            # 화려한 연속 기술
            combo_attacks = ["검 휘두르기", "방패 돌격", "회전 베기", "마무리 찌르기"]
            for attack in combo_attacks:
                combo_damage = int(hp_damage * 0.3)
                target.take_damage(combo_damage)
                print(f"🏛️ {attack}! {combo_damage} 피해!")
            # 관중의 환호로 아군 사기 증진
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    setattr(ally, 'crowd_cheer_bonus', True)
                    setattr(ally, 'temp_attack_bonus', getattr(ally, 'temp_attack_bonus', 0) + 15)
                print(f"👏 관중의 환호로 아군 전체 공격력 증가!")
                
        elif character_class == "기사" and skill.name == "성스러운 돌격":
            # 신성한 힘의 창 돌격
            holy_damage = int(hp_damage * 0.5)  # 추가 성스러운 피해
            target.take_damage(holy_damage)
            print(f"✨ 성스러운 힘 추가 피해: {holy_damage}!")
            # 관통으로 뒤의 적들에게도 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for other_enemy in other_enemies:
                    pierce_damage = int(hp_damage * 0.4)
                    other_enemy.take_damage(pierce_damage)
                    print(f"🛡️ 성스러운 돌격 관통! {other_enemy.name}이(가) {pierce_damage} 피해!")
                    
        elif character_class == "신관" and skill.name == "신의 심판":
            # 적을 심판하면서 아군 전체 대량 회복
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally.current_hp > 0:
                        divine_heal = int(ally.max_hp * 0.3)  # 30% 회복
                        ally.heal(divine_heal)
                        # 신의 가호 (모든 저항 증가)
                        setattr(ally, 'divine_protection', True)
                        setattr(ally, 'divine_protection_turns', 4)
                print(f"✨ 신의 심판! 아군 전체 대량 회복 및 신의 가호!")
                
        elif character_class == "마검사" and skill.name == "마검 오의":
            # 물리와 마법의 완벽한 융합
            magic_damage = int(hp_damage * 0.7)  # 마법 추가 피해
            target.take_damage(magic_damage)
            print(f"⚡ 마법검기 융합! 마법 추가 피해: {magic_damage}!")
            # 검기 파동으로 주변 적들에게도 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for other_enemy in other_enemies:
                    wave_damage = int(hp_damage * 0.4)
                    other_enemy.take_damage(wave_damage)
                    print(f"⚔️ 마검 파동! {other_enemy.name}이(가) {wave_damage} 피해!")
                    
        elif character_class == "차원술사" and skill.name == "차원 붕괴":
            # 차원 붕괴로 공간 자체가 공격 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss:
                space_damage = int(target.current_hp * 0.10)  # 보스는 현재 HP의 10%
            else:
                space_damage = int(target.current_hp * 0.25)  # 일반 적은 현재 HP의 25%
            target.take_damage(space_damage)
            print(f"🌀 차원 붕괴! 공간 자체의 {space_damage} 고정 피해!")
            # 차원 왜곡으로 모든 적의 능력치 감소 (디버프는 보스에게도 적용)
            if hasattr(self, '_current_enemies') and self._current_enemies:
                for enemy in self._current_enemies:
                    if enemy.current_hp > 0:
                        setattr(enemy, 'dimension_distortion', True)
                        setattr(enemy, 'dimension_distortion_turns', 4)
                        # 곱적용 디버프
                        current_reduction = getattr(enemy, 'temp_all_stats_multiplier', 1.0)
                        setattr(enemy, 'temp_all_stats_multiplier', current_reduction * 0.8)  # 20% 감소
                print(f"🌀 차원 왜곡! 모든 적의 능력치 20% 감소!")
                
        elif character_class == "광전사" and skill.name == "최후의 광기":
            # 모든 것을 내던진 광폭한 공격
            hp_ratio = attacker.current_hp / attacker.max_hp
            madness_multiplier = 3.0 - (hp_ratio * 2)  # HP가 낮을수록 최대 3배
            madness_damage = int(hp_damage * (madness_multiplier - 1))
            target.take_damage(madness_damage)
            print(f"😡 최후의 광기! 광폭화로 {madness_damage} 추가 피해!")
            # 자신도 피해를 입지만 공격력 대폭 증가
            self_damage = int(attacker.max_hp * 0.1)
            attacker.current_hp = max(1, attacker.current_hp - self_damage)
            setattr(attacker, 'berserk_mode', True)
            setattr(attacker, 'temp_attack_bonus', getattr(attacker, 'temp_attack_bonus', 0) + 50)
            print(f"😡 광전사 모드! 공격력 대폭 증가하지만 {self_damage} 자해 피해!")
            # 30% 확률로 즉사 효과 (보스급 제외)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if not is_boss and random.random() < 0.3:
                target.current_hp = 0
                print(f"💀 치명적인 암살! {target.name}이(가) 즉사했습니다!")
            else:
                # 즉사하지 않으면 크리티컬 피해
                crit_bonus = int(hp_damage * 0.5)
                target.take_damage(crit_bonus, 0)
                print(f"🗡️ 치명타 추가 피해: {crit_bonus} HP!")
                
        elif character_class == "성기사" and skill.name == "심판의 빛":
            # 아군 전체 상태이상 해제 및 소량 회복
            if hasattr(self, 'party') and self.party:
                for ally in self.party:
                    if ally.current_hp > 0:
                        # 상태이상 해제
                        debuffs = ['is_poisoned', 'is_burning', 'is_frozen', 'is_stunned']
                        for debuff in debuffs:
                            if hasattr(ally, debuff):
                                setattr(ally, debuff, False)
                        # 소량 회복
                        heal_amount = int(hp_damage * 0.15)
                        ally.heal(heal_amount)
                        print(f"✨ {ally.name} 상태이상 해제 & {heal_amount} HP 회복!")
                        
        elif character_class == "검사" and skill.name == "일섬":
            # 완벽한 베기로 방어력 무시 + 출혈 효과
            print(f"⚔️ 완벽한 일섬! 방어력을 무시하고 베어냅니다!")
            setattr(target, 'is_bleeding', True)
            setattr(target, 'bleeding_turns', 3)
            setattr(target, 'bleeding_damage', int(hp_damage * 0.1))
            
        elif character_class == "성직자" and skill.name == "신성한 심판":
            # 아군 전체 HP 회복
            if hasattr(self, 'party') and self.party:
                heal_amount = int(hp_damage * 0.4)
                for ally in self.party:
                    if ally.current_hp > 0:
                        ally.heal(heal_amount)
                        print(f"🌟 신성한 빛이 {ally.name}을(를) {heal_amount} HP 회복!")
                        
        elif character_class == "암흑기사" and skill.name == "흡혈 강타":
            # 가한 피해의 60% HP 회복
            heal_amount = int(hp_damage * 0.6)
            attacker.heal(heal_amount)
            print(f"🩸 강력한 흡혈로 {attacker.name}이(가) {heal_amount} HP 회복!")
            
        elif character_class == "몽크" and skill.name == "폭렬권":
            # 타격 표식 폭발 효과
            strike_marks = getattr(target, 'strike_marks', 0)
            if strike_marks > 0:
                explosion_damage = strike_marks * int(hp_damage * 0.2)  # 중첩당 20% 추가 피해
                target.take_damage(explosion_damage, 0)
                setattr(target, 'strike_marks', 0)  # 표식 제거
                print(f"💥 타격 표식 {strike_marks}중첩 폭발! 추가 {explosion_damage} HP 피해!")
                
                # 표식 폭발로 아군 회복
                if hasattr(self, 'party') and self.party:
                    heal_amount = int(explosion_damage * 0.3)
                    for ally in self.party:
                        if ally.current_hp > 0:
                            ally.heal(heal_amount)
                    print(f"✨ 표식 폭발 에너지가 아군들을 {heal_amount} HP 회복!")
        
    def execute_hp_attack(self, attacker: Character, target: Character):
        """HP 공격 실행"""
        # HP 공격 스킬 사용
        hp_skills = [skill for skill in attacker.brave_skills if skill.attack_type == BraveAttackType.HP]
        if hp_skills:
            skill = hp_skills[0]  # 첫 번째 HP 스킬 사용
        else:
            # 직업별 기본 HP 공격
            skill = self._get_class_specific_hp_attack(attacker)
            
        return self._execute_hp_attack_on_target(attacker, target, skill, True)  # BRV 소모 포함
            
    def execute_area_hp_attack(self, attacker: Character, targets: List[Character], skill=None):
        """광역 HP 공격 실행 - BRV 한 번만 소모하고 모든 대상에게 동일한 파워로 공격"""
        if not targets:
            return
            
        if skill is None:
            # HP 공격 스킬 사용
            hp_skills = [skill for skill in attacker.brave_skills if skill.attack_type == BraveAttackType.HP]
            if hp_skills:
                skill = hp_skills[0]  # 첫 번째 HP 스킬 사용
            else:
                # 직업별 기본 HP 공격 (광역용)
                skill = self._get_class_specific_hp_attack(attacker)
                # 광역 공격시 위력 조정
                skill.hp_multiplier *= 0.8  # 80%로 감소
        
        # BRV 소모를 미리 저장 (모든 대상에게 같은 파워로 공격하기 위해)
        stored_brave = attacker.brave_points
        
        print(f"💥 {attacker.name}의 {skill.name}으로 {len(targets)}명을 동시에 공격!")
        
        total_damage = 0
        for i, target in enumerate(targets):
            if not target.is_alive:
                continue
                
            # 첫 번째 대상이 아닌 경우 저장된 BRV 값으로 복원
            if i > 0:
                attacker.brave_points = stored_brave
            
            # 마지막 대상인지 확인 (BRV 소모는 마지막에만)
            is_last_target = (i == len(targets) - 1)
            damage = self._execute_hp_attack_on_target(attacker, target, skill, is_last_target)
            total_damage += damage
            
            # 연속공격 간 짧은 딜레이
            time.sleep(0.2)
            
        print(f"💀 총 {total_damage} 데미지를 가했습니다!")
    
    def _execute_hp_attack_on_target(self, attacker: Character, target: Character, skill, consume_brave: bool = True):
        """단일 대상에게 HP 공격 실행 (내부 메서드)"""
    def _execute_hp_attack_on_target(self, attacker: Character, target: Character, skill, consume_brave: bool = True):
        """단일 대상에게 HP 공격 실행 (내부 메서드)"""
        # 스킬 사용 비주얼 이펙트
        if hasattr(self, 'visualizer') and self.visualizer:
            self.visualizer.show_skill_effect(attacker, skill.name, EffectType.SKILL)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("skill", skill_name=skill.name, character_name=attacker.name)
        
        # HP 희생 처리 (최초 1회만)
        if consume_brave and hasattr(skill, 'hp_sacrifice_rate') and skill.hp_sacrifice_rate > 0:
            sacrifice_hp = max(1, int(attacker.current_hp * skill.hp_sacrifice_rate))
            attacker.current_hp = max(1, attacker.current_hp - sacrifice_hp)
            print(f"💔 {attacker.name}이(가) {sacrifice_hp} HP를 희생하여 위력을 극대화!")
            
            # 희생한 HP만큼 추가 데미지 보너스
            attacker.temp_sacrifice_power = getattr(attacker, 'temp_sacrifice_power', 0) + sacrifice_hp * 2
        
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
            return 0
        
        # 데미지 계산
        hp_damage, wound_damage = self.brave_manager.calculate_hp_damage(attacker, target, skill)
        
        # 🔥 HP 공격 데미지 배율은 damage_calculator.py에서 통합 처리됨
        # (적군 HP 공격은 이미 0.01125 배율 적용)
        
        # 특성 효과 적용
        if hasattr(attacker, 'temp_attack_bonus'):
            hp_damage = int(hp_damage * (1 + attacker.temp_attack_bonus))
            
        # 요리 효과 적용 (플레이어만)
        if hasattr(attacker, 'character_class') and attacker.character_class != "Enemy":
            try:
                multiplier, status_msg = self._get_cooking_multiplier(attacker)
                hp_damage = int(hp_damage * multiplier)
                
                # 상태 메시지 출력
                if status_msg:
                    print(status_msg)
            except Exception:
                # 요리 시스템 오류 시 무시
                pass
        
        # 생명 흡수 효과
        life_steal_rate = getattr(attacker, 'life_steal_rate', 0.0)
        life_steal_amount = int(hp_damage * life_steal_rate) if life_steal_rate > 0 else 0
        
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
        
        # 직업별 HP 공격 특수 효과 적용
        if hasattr(skill, 'name'):
            self._apply_class_specific_hp_effects(attacker, target, skill, actual_hp_damage)
        
        # BRV 소모 (마지막 대상인 경우에만)
        if consume_brave:
            old_brave = attacker.brave_points
            consumed_brave = attacker.consume_brave_points()
            
            print(f"💫 {attacker.name}의 Brave 포인트: {old_brave} → 0 (HP 공격으로 소모)")
            
            # Brave 변화 비주얼 이펙트 표시
            self.visualizer.show_brave_change(attacker, old_brave, attacker.brave_points)
        
        # 대상이 죽었는지 확인
        if target.current_hp <= 0:
            self.visualizer.show_death_effect(target)
            enhanced_battle_effect("death", character_name=target.name)
            
        return actual_hp_damage
        
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
            
            # 🔊 적 처치 SFX 재생
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("enemy_defeat")
            elif hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.play_sfx("enemy_defeat")
            
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
                # BREAK 상태 해제 체크
                if getattr(enemy, 'is_broken', False) and enemy.brave_points > 0:
                    enemy.is_broken = False
                    print(f"✨ {enemy.name}의 BREAK 상태가 해제되었습니다!")
            
        alive_party = [p for p in party if p.is_alive]
        if not alive_party:
            return self.determine_winner(party, enemies)
            
        print(f"\n👹 {enemy.name}의 턴!")
        
        # 개선된 AI 로직 (더 빠른 전투)
        if enemy.brave_points >= 400 and random.random() < 0.5:  # 1000 → 400, 40% → 50%
            # HP 공격 사용
            target = random.choice(alive_party)
            print(f"💀 {enemy.name}이(가) {target.name}에게 HP 공격을 시도합니다!")
            self.execute_hp_attack(enemy, target)
        else:
            # Brave 공격 사용
            target = random.choice(alive_party)
            print(f"⚔️ {enemy.name}이(가) {target.name}에게 Brave 공격을 시도합니다!")
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
        
        # 모든 캐릭터의 평균 속도 계산
        all_chars = party + enemies
        alive_chars = [char for char in all_chars if char.is_alive]
        if alive_chars:
            avg_speed = sum(getattr(char, 'speed', 50) for char in alive_chars) / len(alive_chars)
        else:
            avg_speed = 50  # 기본값
        
        print(f"\n{Color.BRIGHT_CYAN}{'─'*78}{Color.RESET}")
        print(f"{Color.BRIGHT_WHITE}⚔️ DAWN OF STELLAR - BRAVE BATTLE ⚔️{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'─'*78}{Color.RESET}")
        
        # 파티 상태 표시
        print(f"\n{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        print(f"{Color.BRIGHT_WHITE}🛡️  아군 파티 상태{Color.RESET}")
        print(f"{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        
        for i, member in enumerate(party, 1):
            if member.is_alive:  # 모든 살아있는 아군 표시
                # 현재 턴 캐릭터 강조
                if member == current_char:
                    name_color = Color.BRIGHT_CYAN
                    status_icon = "▶"
                else:
                    name_color = Color.WHITE
                    status_icon = " "
                
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
                
                # ATB 게이지 - 캐스팅 중이면 캐스팅 진행도 표시
                atb_gauge = getattr(member, 'atb_gauge', 0)
                
                # 캐스팅 상태 체크
                if hasattr(member, 'is_casting') and member.is_casting:
                    # ATB 기반 캐스팅 진행도 계산 (스케일링된 게이지)
                    cast_time = getattr(member, 'casting_cast_time', 25)  # 기본 25%
                    casting_progress = min(1.0, member.atb_gauge / cast_time)  # 실제 진행도 (0.0 ~ 1.0)
                    casting_percent = int(casting_progress * 100)  # 표시용 퍼센트 (0 ~ 100%)
                    casting_filled = int(casting_progress * 10)  # 게이지 채움 칸수 (0 ~ 10)
                    atb_display = f"{Color.BRIGHT_MAGENTA}🔮{casting_percent:3}%{Color.RESET}"
                    atb_bar = f"{Color.BRIGHT_MAGENTA}{'▰'*casting_filled}{Color.BRIGHT_BLACK}{'▱'*(10-casting_filled)} {Color.RESET}"
                    atb_icon = "🔮"
                elif atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display = f"{Color.BRIGHT_YELLOW}READY{Color.RESET}"  # 색상 적용
                    atb_bar = f"{Color.BRIGHT_YELLOW}{'▰'*10}{Color.RESET}"
                    atb_icon = "⏳"
                else:
                    atb_percent = int(atb_gauge // self.ATB_DISPLAY_SCALE)  # 디스플레이용 스케일 변환
                    # 진행도에 따른 그라데이션 색상 (푸른색 → 하늘색)
                    if atb_percent >= 80:
                        atb_color = Color.BRIGHT_CYAN  # 80% 이상: 밝은 하늘색
                    elif atb_percent >= 60:
                        atb_color = Color.CYAN  # 60-80%: 하늘색
                    elif atb_percent >= 40:
                        atb_color = Color.BLUE  # 40-60%: 푸른색
                    else:
                        atb_color = Color.BRIGHT_BLUE  # 40% 미만: 어두운 파랑
                    
                    atb_display = f"{atb_color}{atb_percent}%{Color.RESET}"
                    filled = int(min(10, max(0, atb_percent // 10)))  # 0-10 범위로 제한
                    atb_bar = f"{atb_color}{'▰'*filled}{Color.BRIGHT_BLACK}{'▱'*(10-filled)}{Color.RESET}"
                    atb_icon = "⏳"
                
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
                
                # 상태이상 아이콘들
                status_icons = ""
                if hasattr(member, 'is_casting') and member.is_casting:
                    status_icons += " 🔮"
                if hasattr(member, 'is_broken_state') and member.is_broken_state:
                    status_icons += " 💥"
                if hasattr(member, 'is_stunned') and member.is_stunned:
                    status_icons += " 💫"
                if hasattr(member, 'temp_speed_penalty') and getattr(member, 'temp_speed_penalty', 0) > 0:
                    status_icons += " 🐢"
                if hasattr(member, 'is_poisoned') and member.is_poisoned:
                    status_icons += " 💚"
                if hasattr(member, 'is_burning') and member.is_burning:
                    status_icons += " 🔥"
                if hasattr(member, 'is_frozen') and member.is_frozen:
                    status_icons += " ❄️"
                
                # 캐스팅/브레이크 상태 확인
                casting_status = ""
                if hasattr(member, 'is_casting') and member.is_casting:
                    skill_name = getattr(member, 'casting_skill_name', '알 수 없는 스킬')
                    casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
                
                break_status = ""
                if hasattr(member, 'is_broken_state') and member.is_broken_state:
                    break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                elif hasattr(member, 'is_broken') and member.is_broken:
                    break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                
                # ATB 바 생성 (새로운 방식)
                atb_gauge = getattr(member, 'atb_gauge', 0)
                atb_bar = self._create_atb_bar(atb_gauge, True, True, member)
                
                # 3줄 형식 (턴이 왔을 때)
                print(f"{status_icon}{class_icon} Lv.{getattr(member, 'level', 1)} {name_color}{member.name}{Color.RESET}{status_icons}")
                
                # HP/MP 게이지와 값들
                hp_value_str = f"{hp_color}{member.current_hp}{Color.RESET} / {Color.WHITE}{member.max_hp}{Color.RESET}"
                mp_value_str = f"{mp_color}{member.current_mp}{Color.RESET} / {Color.WHITE}{member.max_mp}{Color.RESET}"
                hp_bar_colored = f"[{hp_color}{hp_bar.replace(' ', '')}{Color.RESET}]"
                mp_bar_colored = f"[{mp_color}{mp_bar.replace(' ', '')}{Color.RESET}]"
                
                # BRV 색상 (0-299면 빨간색, MAX BRV = 현재 BRV일 때 마젠타)
                if brave_points <= 299:
                    brv_color = Color.BRIGHT_RED
                elif brave_points >= member.brave_manager.get_max_brave(member):  # MAX BRV = 현재 BRV일 때 마젠타
                    brv_color = Color.BRIGHT_MAGENTA
                else:
                    brv_color = Color.BRIGHT_YELLOW
                
                # SPD 색상 (상대적 속도 - 실제 평균 대비 퍼센트)
                member_speed = getattr(member, 'speed', 50)
                speed_ratio = (member_speed / avg_speed) if avg_speed > 0 else 1.0
                speed_percent_diff = (speed_ratio - 1.0) * 100  # 평균 대비 퍼센트 차이
                
                if speed_percent_diff >= 30:  # +30% 이상
                    spd_color = Color.BRIGHT_GREEN  # 매우 빠름
                elif speed_percent_diff >= 15:  # +15% 이상
                    spd_color = Color.GREEN  # 빠름
                elif speed_percent_diff >= -15:  # ±15% 이내
                    spd_color = Color.WHITE  # 보통
                elif speed_percent_diff >= -30:  # -15% ~ -30%
                    spd_color = Color.YELLOW  # 느림
                else:  # -30% 미만
                    spd_color = Color.BRIGHT_RED  # 매우 느림
                
                print(f"{hp_icon} HP: {hp_value_str} {hp_bar_colored} | {mp_icon} MP: {mp_value_str} {mp_bar_colored} | {brv_color}⚡ BRV: {brave_points}{Color.RESET}  |")
                
                # ATB 라인 - TIME으로 표시 (대괄호는 흰색)
                atb_bar_display = f"{Color.WHITE}[{atb_bar}]{Color.RESET}"
                print(f"        ⏳ TIME: {atb_bar_display} {atb_display} | SPD: {spd_color}{member_speed}{Color.RESET}{casting_status}{break_status} |")
                print()
                
            else:
                # 전투불능 상태 표시 (모든 전투불능 멤버)
                if member == current_char:
                    status_icon = "▶"
                else:
                    status_icon = " "
                print(f"{status_icon} 💀 {Color.RED}{member.name} - 전투불능{Color.RESET}")
                print()
        
        # 적 상태 표시
        print(f"\n{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
        print(f"{Color.BRIGHT_WHITE}⚔️  적군 상태{Color.RESET}")
        print(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
        
        alive_enemies = [e for e in enemies if e.is_alive]
        for i, enemy in enumerate(alive_enemies, 1):
            # 현재 턴 적 강조
            if enemy == current_char:
                name_color = Color.BRIGHT_RED
                status_icon = "▶"
            else:
                name_color = Color.WHITE
                status_icon = " "
            
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
            
            # ATB 게이지 - 캐스팅 중이면 캐스팅 진행도 표시
            atb_gauge = getattr(enemy, 'atb_gauge', 0)
            
            # 캐스팅 상태 체크
            if hasattr(enemy, 'is_casting') and enemy.is_casting:
                # ATB 기반 캐스팅 진행도 계산 (스케일링된 게이지)
                cast_time = getattr(enemy, 'casting_cast_time', 25)  # 기본 25%
                casting_progress = min(1.0, enemy.atb_gauge / cast_time)  # 실제 진행도 (0.0 ~ 1.0)
                casting_percent = int(casting_progress * 100)  # 표시용 퍼센트 (0 ~ 100%)
                casting_filled = int(casting_progress * 10)  # 게이지 채움 칸수 (0 ~ 10)
                atb_display = f"{Color.BRIGHT_MAGENTA}🔮{casting_percent:3}%{Color.RESET}"
                atb_bar = f"{Color.BRIGHT_MAGENTA}{'▰'*casting_filled}{Color.BRIGHT_BLACK}{'▱'*(10-casting_filled)} {Color.RESET}"
                atb_icon = "🔮"
            elif atb_gauge >= self.ATB_READY_THRESHOLD:
                atb_display = f"{Color.BRIGHT_YELLOW}READY{Color.RESET}"  # 색상 적용
                atb_bar = f"{Color.BRIGHT_YELLOW}{'▰'*10}{Color.RESET}"
                atb_icon = "⚡"
            else:
                atb_percent = int(atb_gauge // self.ATB_DISPLAY_SCALE)  # 디스플레이용 스케일 변환
                # 진행도에 따른 그라데이션 색상 (푸른색 → 하늘색)
                if atb_percent >= 80:
                    atb_color = Color.BRIGHT_CYAN  # 80% 이상: 밝은 하늘색
                elif atb_percent >= 60:
                    atb_color = Color.CYAN  # 60-80%: 하늘색
                elif atb_percent >= 40:
                    atb_color = Color.BLUE  # 40-60%: 푸른색
                else:
                    atb_color = Color.BRIGHT_BLUE  # 40% 미만: 어두운 파랑
                
                atb_display = f"{atb_color}{atb_percent}%{Color.RESET}"
                filled = int(min(10, max(0, atb_percent // 10)))  # 0-10 범위로 제한
                atb_bar = f"{atb_color}{'▰'*filled}{Color.BRIGHT_BLACK}{'▱'*(10-filled)}{Color.RESET}"
                atb_icon = "⏳" if atb_percent < 50 else "🔶"
            
            # 상태이상 아이콘들 (실제 상태이상 시스템 연동)
            status_icons = ""
            
            # 캐스팅 상태
            if hasattr(enemy, 'is_casting') and enemy.is_casting:
                status_icons += " 🔮"
            
            # BREAK 상태
            if hasattr(enemy, 'is_broken') and enemy.is_broken:
                status_icons += " 💥"
            elif hasattr(enemy, 'is_broken_state') and enemy.is_broken_state:
                status_icons += " 💥"
            
            # 실제 상태이상 시스템에서 상태 확인
            if hasattr(enemy, 'status_effects') and enemy.status_effects:
                try:
                    from .status_effects import StatusType
                    from .new_skill_system import get_status_icon
                    
                    status_types_found = []
                    for effect in enemy.status_effects:
                        if effect.status_type not in status_types_found:
                            status_types_found.append(effect.status_type)
                            icon = get_status_icon(effect.status_type)
                            status_icons += f" {icon}"
                except ImportError:
                    # 폴백: 구버전 호환
                    pass
            
            # 임시 상태 (구버전 호환)
            if hasattr(enemy, 'temp_speed_penalty') and getattr(enemy, 'temp_speed_penalty', 0) > 0:
                status_icons += " 🟦"  # 둔화
            
            # 캐스팅/브레이크 상태 확인
            casting_status = ""
            if hasattr(enemy, 'is_casting') and enemy.is_casting:
                skill_name = getattr(enemy, 'casting_skill_name', '알 수 없는 스킬')
                casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
            
            break_status = ""
            if hasattr(enemy, 'is_broken_state') and enemy.is_broken_state:
                break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
            elif hasattr(enemy, 'is_broken') and enemy.is_broken:
                break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
            
            # Brave 포인트
            brave_points = getattr(enemy, 'brave_points', 0)
            
            # ATB 바 생성 (새로운 방식)
            atb_gauge = getattr(enemy, 'atb_gauge', 0)
            atb_bar = self._create_atb_bar(atb_gauge, True, False, enemy)
            
            # 3줄 형식 (적군 턴이 왔을 때)
            print(f"{status_icon} ⚔️ {name_color}{enemy.name}{Color.RESET}{status_icons}")
            
            # HP 값과 BRV 색상 개선
            hp_value_str = f"{hp_color}{enemy.current_hp}{Color.RESET} / {Color.WHITE}{enemy.max_hp}{Color.RESET}"
            
            # BRV 색상 (0-299면 빨간색, MAX BRV = 현재 BRV일 때 마젠타)
            if brave_points <= 299:
                brv_color = Color.BRIGHT_RED
            elif brave_points >= getattr(enemy, 'brave_manager', type('obj', (), {'get_max_brave': lambda x: 9999})()).get_max_brave(enemy):  # MAX BRV = 현재 BRV일 때 마젠타
                brv_color = Color.BRIGHT_MAGENTA
            else:
                brv_color = Color.BRIGHT_YELLOW
            
            # SPD 색상 (상대적 속도 - 실제 평균 대비 퍼센트)
            enemy_speed = getattr(enemy, 'speed', 50)
            speed_ratio = (enemy_speed / avg_speed) if avg_speed > 0 else 1.0
            speed_percent_diff = (speed_ratio - 1.0) * 100  # 평균 대비 퍼센트 차이
            
            if speed_percent_diff >= 30:  # +30% 이상
                spd_color = Color.BRIGHT_GREEN  # 매우 빠름
            elif speed_percent_diff >= 15:  # +15% 이상
                spd_color = Color.GREEN  # 빠름
            elif speed_percent_diff >= -15:  # ±15% 이내
                spd_color = Color.WHITE  # 보통
            elif speed_percent_diff >= -30:  # -15% ~ -30%
                spd_color = Color.YELLOW  # 느림
            else:  # -30% 미만
                spd_color = Color.BRIGHT_RED  # 매우 느림
            
            print(f"{hp_icon} HP: {hp_value_str} | {brv_color}⚡ BRV: {brave_points}{Color.RESET}  |")
            
            # ATB 라인 - TIME으로 표시 (대괄호는 흰색)
            atb_bar_display = f"{Color.WHITE}[{atb_bar}]{Color.RESET}"
            print(f"        ⏳ TIME: {atb_bar_display} {atb_display} | SPD: {spd_color}{enemy_speed}{Color.RESET}{casting_status}{break_status} |")
            print()

    def _get_party_status_string(self, current_char: Character, party: List[Character], enemies: List[Character]) -> str:
        """파티 상태를 문자열로 반환 (메뉴 통합 표시용)"""
        status_lines = []
        
        # 모든 캐릭터의 평균 속도 계산
        all_chars = party + enemies
        alive_chars = [char for char in all_chars if char.is_alive]
        if alive_chars:
            avg_speed = sum(getattr(char, 'speed', 50) for char in alive_chars) / len(alive_chars)
        else:
            avg_speed = 50  # 기본값
        
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
            if member.is_alive:  # 모든 살아있는 아군 표시
                # 현재 턴 캐릭터 강조
                if member == current_char:
                    name_color = Color.BRIGHT_CYAN
                    status_icon = "▶"
                else:
                    name_color = Color.WHITE
                    status_icon = " "
                
                # 클래스 아이콘과 레벨
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
                level_display = f"Lv.{getattr(member, 'level', 1):2}"
                
                # HP 상태 색상과 아이콘
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
                
                # MP 게이지 바 생성
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                mp_bar_length = 10
                mp_filled = int((mp_ratio * mp_bar_length))
                mp_bar = "▰" * mp_filled + "▱" * (mp_bar_length - mp_filled) + " "
                
                # MP 상태 색상과 아이콘
                if mp_ratio > 0.5:
                    mp_color = Color.BRIGHT_BLUE
                    mp_icon = "💙"
                elif mp_ratio > 0.2:
                    mp_color = Color.BLUE
                    mp_icon = "💜"
                else:
                    mp_color = Color.BRIGHT_BLACK
                    mp_icon = "🤍"
                
                # ATB 게이지 표시
                atb_gauge = getattr(member, 'atb_gauge', 0)
                if hasattr(member, 'is_casting') and member.is_casting:
                    cast_time = getattr(member, 'casting_cast_time', 25)
                    casting_progress = min(1.0, member.atb_gauge / cast_time)
                    casting_percent = int(casting_progress * 100)
                    atb_display = f"{Color.BRIGHT_MAGENTA}🔮{casting_percent:3}%{Color.RESET}"
                    atb_icon = "🔮"
                elif atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display = f"{Color.BRIGHT_YELLOW}READY{Color.RESET}"  # 색상 적용
                    atb_icon = "⏳"
                else:
                    atb_percent = int(atb_gauge // self.ATB_DISPLAY_SCALE)
                    # 진행도에 따른 그라데이션 색상 (푸른색 → 하늘색)
                    if atb_percent >= 80:
                        atb_color = Color.BRIGHT_CYAN  # 80% 이상: 밝은 하늘색
                    elif atb_percent >= 60:
                        atb_color = Color.CYAN  # 60-80%: 하늘색
                    elif atb_percent >= 40:
                        atb_color = Color.BLUE  # 40-60%: 푸른색
                    else:
                        atb_color = Color.BRIGHT_BLUE  # 40% 미만: 어두운 파랑
                    
                    atb_display = f"{atb_color}{atb_percent:3}%{Color.RESET}"
                    atb_icon = "⏳"
                
                # ATB 바 생성
                atb_bar = self._create_atb_bar(atb_gauge, True, True, member)
                
                # Brave 포인트와 색상
                brave_points = getattr(member, 'brave_points', 0)
                if brave_points <= 299:
                    brv_color = Color.BRIGHT_RED
                elif brave_points >= member.brave_manager.get_max_brave(member):  # MAX BRV = 현재 BRV일 때 마젠타
                    brv_color = Color.BRIGHT_MAGENTA
                else:
                    brv_color = Color.BRIGHT_YELLOW
                
                # SPD 색상 (상대적 속도 - 실제 평균 대비 퍼센트)
                member_speed = getattr(member, 'speed', 50)
                speed_ratio = (member_speed / avg_speed) if avg_speed > 0 else 1.0
                speed_percent_diff = (speed_ratio - 1.0) * 100  # 평균 대비 퍼센트 차이
                
                if speed_percent_diff >= 30:  # +30% 이상
                    spd_color = Color.BRIGHT_GREEN  # 매우 빠름
                elif speed_percent_diff >= 15:  # +15% 이상
                    spd_color = Color.GREEN  # 빠름
                elif speed_percent_diff >= -15:  # ±15% 이내
                    spd_color = Color.WHITE  # 보통
                elif speed_percent_diff >= -30:  # -15% ~ -30%
                    spd_color = Color.YELLOW  # 느림
                else:  # -30% 미만
                    spd_color = Color.BRIGHT_RED  # 매우 느림
                
                # 캐스팅/브레이크 상태 확인
                casting_status = ""
                if hasattr(member, 'is_casting') and member.is_casting:
                    skill_name = getattr(member, 'casting_skill_name', '알 수 없는 스킬')
                    casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
                
                break_status = ""
                if hasattr(member, 'is_broken_state') and member.is_broken_state:
                    break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                elif hasattr(member, 'is_broken') and member.is_broken:
                    break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                
                # 상태이상 아이콘들
                status_icons = ""
                if hasattr(member, 'is_casting') and member.is_casting:
                    status_icons += " 🔮"
                if hasattr(member, 'is_broken_state') and member.is_broken_state:
                    status_icons += " 💥"
                elif hasattr(member, 'is_broken') and member.is_broken:
                    status_icons += " 💥"
                if hasattr(member, 'status_effects') and member.status_effects:
                    try:
                        from .status_effects import StatusType
                        from .new_skill_system import get_status_icon
                        
                        status_types_found = []
                        for effect in member.status_effects:
                            if effect.status_type not in status_types_found:
                                status_types_found.append(effect.status_type)
                                icon = get_status_icon(effect.status_type)
                                status_icons += f" {icon}"
                    except ImportError:
                        pass
                if hasattr(member, 'temp_speed_penalty') and getattr(member, 'temp_speed_penalty', 0) > 0:
                    status_icons += " 🟦"
                
                # HP 게이지 바 생성
                hp_bar_length = 10
                hp_filled = int((hp_ratio * hp_bar_length))
                hp_bar = "▰" * hp_filled + "▱" * (hp_bar_length - hp_filled) + " "
                
                # ATB 바 생성 - 기본 색상 (상태이상일 때만 색 변경)
                atb_bar = self._create_atb_bar(atb_gauge, True, True, member)
                
                # 2줄 형식 (로딩 중일 때) - 간격 조정
                status_lines.append(f"        {class_icon} {member.name}{status_icons}")
                
                # HP/MP 게이지와 ATB 진행률 표시
                hp_bar_colored = f"[{hp_color}{hp_bar}{Color.RESET}]"
                mp_bar_colored = f"[{mp_color}{mp_bar}{Color.RESET}]"
                
                status_lines.append(f"        {hp_icon} HP: {hp_color}{member.current_hp}{Color.RESET} / {Color.WHITE}{member.max_hp}{Color.RESET}  {hp_bar_colored} | {mp_icon} MP: {mp_color}{member.current_mp}{Color.RESET} / {Color.WHITE}{member.max_mp}{Color.RESET}  {mp_bar_colored} | {brv_color}⚡ BRV: {brave_points}{Color.RESET}  |")
                
                # ATB 진행률 표시 (대괄호는 흰색)
                atb_bar_simple = f"{Color.WHITE}[{atb_bar}]{Color.RESET}"
                if hasattr(member, 'is_casting') and member.is_casting:
                    cast_time = getattr(member, 'casting_cast_time', 25)
                    casting_progress = min(1.0, member.atb_gauge / cast_time)
                    casting_percent = int(casting_progress * 100)
                    atb_display_simple = f"{Color.BRIGHT_MAGENTA}{casting_percent}%{Color.RESET}"
                elif atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display_simple = f"{Color.BRIGHT_YELLOW}READY{Color.RESET}"
                else:
                    atb_percent = int(atb_gauge // self.ATB_DISPLAY_SCALE)
                    # 진행도에 따른 그라데이션 색상
                    if atb_percent >= 80:
                        atb_color = Color.BRIGHT_CYAN  
                    elif atb_percent >= 60:
                        atb_color = Color.CYAN  
                    elif atb_percent >= 40:
                        atb_color = Color.BLUE  
                    else:
                        atb_color = Color.BRIGHT_BLUE 
                    atb_display_simple = f"{atb_color}{atb_percent}%{Color.RESET}"
                
                status_lines.append(f"        {atb_icon} TIME: {atb_bar_simple} {atb_display_simple} | SPD: {spd_color}{member_speed}{Color.RESET}{casting_status}{break_status} |")
                status_lines.append("")  # 빈 줄 추가
            else:
                # 전투불능 상태 표시 (모든 전투불능 멤버)
                if member == current_char:
                    status_icon = "▶"
                else:
                    status_icon = " "
                status_lines.append(f"{status_icon} 💀 {Color.RED}{member.name} - 전투불능{Color.RESET}")
                status_lines.append("")
        
        # 적군 상태 (상세하게)
        alive_enemies = [e for e in enemies if e.is_alive]
        if alive_enemies:
            status_lines.append(f"\n{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
            status_lines.append(f"{Color.BRIGHT_WHITE}⚔️  적군 상태{Color.RESET}")
            status_lines.append(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
            
            for i, enemy in enumerate(alive_enemies, 1):
                # 현재 턴 적 강조
                if enemy == current_char:
                    name_color = Color.BRIGHT_RED
                    status_icon = "▶"
                else:
                    name_color = Color.WHITE
                    status_icon = " "
                
                # HP 상태 색상
                hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
                if hp_ratio > 0.7:
                    hp_color = Color.BRIGHT_GREEN
                elif hp_ratio > 0.4:
                    hp_color = Color.YELLOW
                else:
                    hp_color = Color.BRIGHT_RED
                
                # ATB 게이지 - 새로운 방식 사용
                atb_gauge = getattr(enemy, 'atb_gauge', 0)
                atb_bar = self._create_atb_bar(atb_gauge, True, False, enemy)
                
                # 캐스팅/브레이크 상태 확인
                casting_status = ""
                if hasattr(enemy, 'is_casting') and enemy.is_casting:
                    skill_name = getattr(enemy, 'casting_skill_name', '알 수 없는 스킬')
                    casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
                
                break_status = ""
                if hasattr(enemy, 'is_broken_state') and enemy.is_broken_state:
                    break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                elif hasattr(enemy, 'is_broken') and enemy.is_broken:
                    break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                
                # 상태이상 아이콘들 (실제 상태이상 시스템 연동)
                status_icons = ""
                
                # 캐스팅 상태
                if hasattr(enemy, 'is_casting') and enemy.is_casting:
                    status_icons += " 🔮"
                
                # BREAK 상태
                if hasattr(enemy, 'is_broken') and enemy.is_broken:
                    status_icons += " 💥"
                elif hasattr(enemy, 'is_broken_state') and enemy.is_broken_state:
                    status_icons += " 💥"
                
                # 실제 상태이상 시스템에서 상태 확인
                if hasattr(enemy, 'status_effects') and enemy.status_effects:
                    from .status_effects import StatusType
                    from .new_skill_system import get_status_icon
                    
                    status_types_found = []
                    for effect in enemy.status_effects:
                        if effect.status_type not in status_types_found:
                            status_types_found.append(effect.status_type)
                            icon = get_status_icon(effect.status_type)
                            status_icons += f" {icon}"
                
                # 임시 상태 (구버전 호환)
                if hasattr(enemy, 'temp_speed_penalty') and getattr(enemy, 'temp_speed_penalty', 0) > 0:
                    status_icons += " 🟦"  # 둔화
                
                brave_points = getattr(enemy, 'brave_points', 0)
                
                # 2줄짜리 ATB 업데이트용 형태 (적군 - 게이지 포함)
                # HP 상태 색상
                hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
                if hp_ratio > 0.7:
                    hp_color = Color.BRIGHT_GREEN
                elif hp_ratio > 0.4:
                    hp_color = Color.YELLOW
                else:
                    hp_color = Color.BRIGHT_RED
                    
                # ATB 게이지와 캐스팅/브레이크 상태
                atb_gauge = getattr(enemy, 'atb_gauge', 0)
                if hasattr(enemy, 'is_casting') and enemy.is_casting:
                    cast_time = getattr(enemy, 'casting_cast_time', 25)
                    casting_progress = min(1.0, enemy.atb_gauge / cast_time)
                    casting_percent = int(casting_progress * 100)
                    atb_display = f"{Color.BRIGHT_MAGENTA}🔮{casting_percent:3}%{Color.RESET}"
                    atb_icon = "🔮"
                elif atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display = f"{Color.BRIGHT_YELLOW}READY{Color.RESET}"  # 색상 적용
                    atb_icon = "⚡"
                else:
                    atb_percent = int(atb_gauge // self.ATB_DISPLAY_SCALE)
                    # 진행도에 따른 그라데이션 색상 (푸른색 → 하늘색)
                    if atb_percent >= 80:
                        atb_color = Color.BRIGHT_CYAN  # 80% 이상: 밝은 하늘색
                    elif atb_percent >= 60:
                        atb_color = Color.CYAN  # 60-80%: 하늘색
                    elif atb_percent >= 40:
                        atb_color = Color.BLUE  # 40-60%: 푸른색
                    else:
                        atb_color = Color.BRIGHT_BLUE  # 40% 미만: 어두운 파랑
                    
                    atb_display = f"{atb_color}{atb_percent}%{Color.RESET}"
                    atb_icon = "⏳"
                
                atb_bar = self._create_atb_bar(atb_gauge, True, False, enemy)
                
                # Brave 포인트
                brave_points = getattr(enemy, 'brave_points', 0)
                
                # 상태이상 아이콘들
                status_icons = ""
                if hasattr(enemy, 'is_casting') and enemy.is_casting:
                    status_icons += " 🔮"
                if hasattr(enemy, 'is_broken') and enemy.is_broken:
                    status_icons += " 💥"
                elif hasattr(enemy, 'is_broken_state') and enemy.is_broken_state:
                    status_icons += " 💥"
                if hasattr(enemy, 'temp_speed_penalty') and getattr(enemy, 'temp_speed_penalty', 0) > 0:
                    status_icons += " 🟦"
                
                # 캐스팅/브레이크 상태 확인
                casting_status = ""
                if hasattr(enemy, 'is_casting') and enemy.is_casting:
                    skill_name = getattr(enemy, 'casting_skill_name', '알 수 없는 스킬')
                    casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
                
                # BRV 색상 (0-299면 빨간색, MAX BRV = 현재 BRV일 때 마젠타)
                if brave_points <= 299:
                    brv_color = Color.BRIGHT_RED
                elif brave_points >= getattr(enemy, 'brave_manager', type('obj', (), {'get_max_brave': lambda x: 9999})()).get_max_brave(enemy):  # MAX BRV = 현재 BRV일 때 마젠타
                    brv_color = Color.BRIGHT_MAGENTA
                else:
                    brv_color = Color.BRIGHT_YELLOW
                
                # SPD 색상 (상대적 속도 - 실제 평균 대비 퍼센트)
                enemy_speed = getattr(enemy, 'speed', 50)
                speed_ratio = (enemy_speed / avg_speed) if avg_speed > 0 else 1.0
                speed_percent_diff = (speed_ratio - 1.0) * 100  # 평균 대비 퍼센트 차이
                
                if speed_percent_diff >= 30:  # +30% 이상
                    spd_color = Color.BRIGHT_GREEN  # 매우 빠름
                elif speed_percent_diff >= 15:  # +15% 이상
                    spd_color = Color.GREEN  # 빠름
                elif speed_percent_diff >= -15:  # ±15% 이내
                    spd_color = Color.WHITE  # 보통
                elif speed_percent_diff >= -30:  # -15% ~ -30%
                    spd_color = Color.YELLOW  # 느림
                else:  # -30% 미만
                    spd_color = Color.BRIGHT_RED  # 매우 느림
                
                # HP 값 색상 적용
                hp_value_str = f"{hp_color}{enemy.current_hp}{Color.RESET}"
                
                # HP 게이지 바 생성
                hp_bar_length = 10
                hp_filled = int((hp_ratio * hp_bar_length))
                hp_bar = "▰" * hp_filled + "▱" * (hp_bar_length - hp_filled) + " "
                hp_bar_colored = f"[{hp_color}{hp_bar}{Color.RESET}]"
                
                # 2줄 형식 (적군 로딩 중일 때) - 간격 조정
                status_lines.append(f"        ⚔️ {enemy.name}{status_icons}")
                status_lines.append(f"        {hp_icon} HP: {hp_color}{enemy.current_hp}{Color.RESET} / {Color.WHITE}{enemy.max_hp}{Color.RESET}  {hp_bar_colored} | {brv_color}⚡ BRV: {brave_points}{Color.RESET}  |")
                
                # ATB 진행률 표시 (대괄호는 흰색)
                atb_bar_simple = f"{Color.WHITE}[{Color.RESET}{atb_bar}{Color.WHITE} ]{Color.RESET}"
                if hasattr(enemy, 'is_casting') and enemy.is_casting:
                    cast_time = getattr(enemy, 'casting_cast_time', 25)
                    casting_progress = min(1.0, enemy.atb_gauge / cast_time)
                    casting_percent = int(casting_progress * 100)
                    atb_display_simple = f"{casting_percent}%"
                elif atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display_simple = "READY"
                else:
                    atb_percent = int(atb_gauge // self.ATB_DISPLAY_SCALE)
                    atb_display_simple = f"{atb_percent}%"
                
                status_lines.append(f"        {atb_icon} TIME: {atb_bar_simple} {atb_display_simple} | SPD: {spd_color}{enemy_speed}{Color.RESET}{casting_status}{break_status} |")
                status_lines.append("")  # 빈 줄 추가
        
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
            
    def _get_cooking_multiplier(self, character):
        """요리 효과에 따른 데미지 배율 및 상태 메시지 반환"""
        try:
            from game.field_cooking import get_brv_cooking_modifiers
            cooking_modifiers = get_brv_cooking_modifiers()
            
            multiplier = 1.0
            status_msg = ""
            
            # BRV 데미지 보너스 적용
            if "brv_damage_multiplier" in cooking_modifiers:
                multiplier *= cooking_modifiers["brv_damage_multiplier"]
                if cooking_modifiers["brv_damage_multiplier"] > 1.0:
                    bonus_percent = int((cooking_modifiers["brv_damage_multiplier"] - 1.0) * 100)
                    status_msg = f"🍳 요리 효과로 데미지 {bonus_percent}% 증가!"
            
            return multiplier, status_msg
            
        except ImportError:
            # 요리 시스템이 없으면 기본값 반환
            return 1.0, ""
        except Exception as e:
            # 오류 발생 시 기본값 반환
            return 1.0, ""
            
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
                        brave_status = "⚡"
                        
                        # BREAK 상태 확인
                        break_status = ""
                        if hasattr(member, 'is_broken_state') and member.is_broken_state:
                            break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                        
                        menu_options.append(f"{hp_status} {member.name} ({member.character_class}){break_status}")
                        menu_descriptions.append(f"HP: {member.current_hp}/{member.max_hp} | MP: {member.current_mp}/{member.max_mp} | BRV: {brave}{break_status}")
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
                    break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}" if hasattr(enemy, 'is_broken') and enemy.is_broken else ""
                    
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
                    break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}" if hasattr(enemy, 'is_broken') and enemy.is_broken else ""
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
                print(f"  🩸 WOUND: {character.wounds} ({wound_severity})")
                print(f"  🏥 치료 가능 HP: {character.max_hp - character.wounds}")
            else:
                print(f"  🩹 WOUND: 없음 (건강)")
        
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
        # 디스플레이용으로 100 스케일로 변환
        display_atb = atb_gauge // self.ATB_DISPLAY_SCALE
        atb_bar = "█" * int(display_atb/5) + "░" * (20-int(display_atb/5))
        atb_color = Color.BRIGHT_CYAN if atb_gauge >= self.ATB_READY_THRESHOLD else Color.CYAN if display_atb >= 75 else Color.BLUE
        print(f"\n⏱️ ATB (액션 타임 배틀):")
        print(f"  게이지: {Color.WHITE}[{atb_color}{atb_bar}{Color.WHITE}] {int(display_atb)}%{Color.RESET}")
        if atb_gauge >= self.ATB_READY_THRESHOLD:
            print(f"  상태: ⚡ 행동 준비 완료!")
        else:
            turns_to_ready = int((self.ATB_READY_THRESHOLD - atb_gauge) / 800)  # ATB 스케일에 맞춰 계산 조정
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
        print(f"  총 HP: {total_ally_hp}/{total_ally_max_hp} ({int(total_ally_hp/total_ally_max_hp*100) if total_ally_max_hp > 0 else 0}%)")
        print(f"  총 BRV: {total_ally_brave}")
        print(f"  HP 공격 가능: {len([p for p in alive_allies if getattr(p, 'brave_points', 0) >= 300])}명")
        
        # 적군 요약
        alive_enemies = [e for e in enemies if e.is_alive]
        total_enemy_hp = sum(e.current_hp for e in alive_enemies)
        total_enemy_max_hp = sum(e.max_hp for e in alive_enemies)
        total_enemy_brave = sum(getattr(e, 'brave_points', 0) for e in alive_enemies)
        
        print(f"\n{Color.BRIGHT_RED}⚔️ 적군 현황:{Color.RESET}")
        print(f"  생존자: {len(alive_enemies)}명")
        print(f"  총 HP: {total_enemy_hp}/{total_enemy_max_hp} ({int(total_enemy_hp/total_enemy_max_hp*100) if total_enemy_max_hp > 0 else 0}%)")
        print(f"  총 BRV: {total_enemy_brave}")
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
            
            if atb_gauge >= self.ATB_READY_THRESHOLD:
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
            
    def update_atb_gauges(self, all_combatants: List[Character], show_animation: bool = False):
        """ATB 게이지 업데이트 - 상대적 속도 기반 차등 업데이트 및 캐스팅 체크 (애니메이션 지원)"""
        # 파티 정보 저장 (애니메이션에서 사용)
        party = [c for c in all_combatants if hasattr(c, 'character_class')]  # 아군 구분 (임시)
        self._current_party = party
        
        # 설정 로드
        try:
            from ..config import GameConfig
            config = GameConfig()
            atb_settings = config.ATB_SETTINGS
        except ImportError:
            # 기본 설정
            atb_settings = {
                "animation_enabled": True,
                "animation_fps": 10,  # 0.1초 간격으로 조정
                "update_speed": 1.0,
                "show_percentage": True,
                "smooth_animation": True,
                "frame_delay": 0.1  # 0.1초로 변경
            }
        
        current_time = getattr(self, 'battle_time', 0)
        self.battle_time = current_time + 1  # 시간 증가
        
        # 애니메이션이 활성화되고 요청된 경우
        if show_animation and atb_settings.get("animation_enabled", True):
            self._update_atb_with_animation(all_combatants, atb_settings)
        else:
            self._update_atb_instant(all_combatants, atb_settings)
    
    def _update_atb_instant(self, all_combatants: List[Character], atb_settings: dict):
        """ATB 즉시 업데이트 (애니메이션 없음) - 상대적 속도 기반"""
        speed_multiplier = atb_settings.get("update_speed", 1.0)
        
        # 상대적 속도 계산을 위한 평균 속도
        alive_combatants = [c for c in all_combatants if not isinstance(c, dict) and c.is_alive and hasattr(c, 'atb_gauge')]
        if not alive_combatants:
            return
        
        total_speed = sum(getattr(c, 'speed', 100) for c in alive_combatants)
        avg_speed = total_speed / len(alive_combatants)
        
        # 5초 내에 게이지 충전 목표로 기본 증가량 조정 (10 프레임 * 5초 = 50프레임)
        base_increase = self.ATB_MAX // 50
        
        for combatant in all_combatants:
            # dict 객체 체크
            if isinstance(combatant, dict):
                print(f"⚠️ 경고: ATB 업데이트 중 dict 객체 발견: {combatant}")
                continue
                
            if combatant.is_alive and hasattr(combatant, 'atb_gauge'):
                # 상대적 속도 계산
                speed = getattr(combatant, 'speed', 100)
                relative_speed = speed / avg_speed
                
                # 캐스팅 중인 경우 ATB 기반 캐스팅 처리
                if hasattr(combatant, 'is_casting') and combatant.is_casting:
                    atb_increase = max(base_increase, int(base_increase * relative_speed * speed_multiplier))
                    combatant.atb_gauge = min(self.ATB_MAX, combatant.atb_gauge + atb_increase)
                    
                    # 캐스팅 완료 체크 - ATB 기반
                    cast_time = getattr(combatant, 'casting_cast_time', 2500)  # 기본 25% → 2500
                    required_atb = cast_time  # 캐스팅이면 ATB cast_time에서 완료
                    
                    if combatant.atb_gauge >= required_atb:
                        # 캐스팅 완료
                        display_atb = combatant.atb_gauge // self.ATB_DISPLAY_SCALE
                        display_required = required_atb // self.ATB_DISPLAY_SCALE
                        print(f"✨ {combatant.name}의 캐스팅이 완료되었습니다! (ATB: {display_atb}% >= {display_required}%)")
                        self.complete_casting(combatant)
                        combatant.atb_gauge = 0  # ATB 초기화
                    continue
                
                # 일반적인 ATB 게이지 증가 (상대적 속도 기반)
                atb_increase = max(base_increase, int(base_increase * relative_speed * speed_multiplier))
                combatant.atb_gauge = min(self.ATB_MAX, combatant.atb_gauge + atb_increase)
    
    def _update_atb_with_animation(self, all_combatants: List[Character], atb_settings: dict):
        """ATB 애니메이션과 함께 업데이트 - 상대적 속도 기반"""
        import time
        import os
        
        speed_multiplier = atb_settings.get("update_speed", 1.0)
        frame_delay = atb_settings.get("frame_delay", 0.1)  # 0.1초로 변경
        show_percentage = atb_settings.get("show_percentage", True)
        
        # 상대적 속도 계산을 위한 평균 속도
        alive_combatants = [c for c in all_combatants if not isinstance(c, dict) and c.is_alive and hasattr(c, 'atb_gauge')]
        if not alive_combatants:
            return
        
        total_speed = sum(getattr(c, 'speed', 100) for c in alive_combatants)
        avg_speed = total_speed / len(alive_combatants)
        
        # 5초 내에 게이지 충전 목표로 기본 증가량 조정 (10 프레임 * 5초 = 50프레임)
        base_increase = self.ATB_MAX // 50
        
        # 이전 ATB 값들 저장
        previous_atb = {}
        for combatant in alive_combatants:
            if hasattr(combatant, 'atb_gauge'):
                previous_atb[id(combatant)] = combatant.atb_gauge
        
        # ATB 업데이트 계산
        for combatant in all_combatants:
            if isinstance(combatant, dict):
                continue
                
            if combatant.is_alive and hasattr(combatant, 'atb_gauge'):
                # 상대적 속도 계산
                speed = getattr(combatant, 'speed', 100)
                relative_speed = speed / avg_speed
                
                # 캐스팅 중인 경우 ATB 기반 캐스팅 처리
                if hasattr(combatant, 'is_casting') and combatant.is_casting:
                    atb_increase = max(base_increase, int(base_increase * relative_speed * speed_multiplier))
                    new_atb = min(self.ATB_MAX, combatant.atb_gauge + atb_increase)
                    
                    # 아군/적군 구분 확인  
                    is_ally = combatant in self._current_party if hasattr(self, '_current_party') else None
                    # 애니메이션으로 ATB 증가 표시
                    self._animate_atb_change(combatant, combatant.atb_gauge, new_atb, frame_delay, show_percentage, is_ally)
                    combatant.atb_gauge = new_atb
                    
                    # 캐스팅 완료 체크
                    cast_time = getattr(combatant, 'casting_cast_time', 2500)
                    if combatant.atb_gauge >= cast_time:
                        display_atb = combatant.atb_gauge // self.ATB_DISPLAY_SCALE
                        display_required = cast_time // self.ATB_DISPLAY_SCALE
                        print(f"✨ {combatant.name}의 캐스팅이 완료되었습니다! (ATB: {display_atb}% >= {display_required}%)")
                        self.complete_casting(combatant)
                        combatant.atb_gauge = 0
                    continue
                
                # 일반적인 ATB 게이지 증가 (상대적 속도 기반)
                atb_increase = max(base_increase, int(base_increase * relative_speed * speed_multiplier))
                new_atb = min(self.ATB_MAX, combatant.atb_gauge + atb_increase)
                
                # 애니메이션으로 ATB 증가 표시
                if new_atb != combatant.atb_gauge:
                    # 아군/적군 구분 확인
                    is_ally = combatant in self._current_party if hasattr(self, '_current_party') else None
                    self._animate_atb_change(combatant, combatant.atb_gauge, new_atb, frame_delay, show_percentage, is_ally)
                
                combatant.atb_gauge = new_atb
    
    def _animate_atb_change(self, character: Character, old_atb: int, new_atb: int, frame_delay: float, show_percentage: bool, is_ally: bool = None):
        """ATB 변화를 애니메이션으로 표시"""
        import time
        import os
        
        if old_atb == new_atb:
            return
        
        # 애니메이션 프레임 수 계산 (최대 10프레임)
        total_change = new_atb - old_atb
        frames = min(10, max(1, abs(total_change) // 100))  # ATB 변화량에 따라 프레임 수 조정
        
        change_per_frame = total_change / frames
        current_atb = old_atb
        
        for frame in range(frames):
            current_atb += change_per_frame
            
            # 현재 위치에서만 ATB 바 표시 - 화살표 추가
            display_atb = int(current_atb // self.ATB_DISPLAY_SCALE)
            atb_bar = self._create_atb_bar(current_atb, show_percentage, is_ally, character)
            
            # 화살표 표시 (진행 방향)
            if display_atb >= 99:
                arrow = "→ READY!"
            elif display_atb >= 80:
                arrow = "→→→"
            elif display_atb >= 50:
                arrow = "→→"
            else:
                arrow = "→"
            
            # 아군/적군 구분 아이콘
            side_icon = "🛡️" if is_ally else "⚔️" if is_ally is False else "⏳"
            
            # 캐릭터 정보 표시 (HP/MP/BRV 포함)
            if is_ally:
                # 아군은 HP, MP, BRV 모두 표시
                hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
                mp_ratio = character.current_mp / max(1, character.max_mp) if character.max_mp > 0 else 0
                brave = getattr(character, 'brave_points', 0)
                
                # HP 색상
                if hp_ratio > 0.7:
                    hp_color = Color.BRIGHT_GREEN
                elif hp_ratio > 0.4:
                    hp_color = Color.YELLOW
                elif hp_ratio > 0.15:
                    hp_color = Color.BRIGHT_RED
                else:
                    hp_color = Color.RED
                
                # MP 색상
                if mp_ratio > 0.7:
                    mp_color = Color.BRIGHT_CYAN
                elif mp_ratio > 0.3:
                    mp_color = Color.CYAN
                else:
                    mp_color = Color.BLUE
                
                # 상태이상 아이콘들 (실제 상태이상 시스템 연동)
                status_icons = ""
                
                # 캐스팅 상태
                if hasattr(character, 'is_casting') and character.is_casting:
                    status_icons += " 🔮"
                
                # BREAK 상태
                if hasattr(character, 'is_broken_state') and character.is_broken_state:
                    status_icons += " 💥"
                elif hasattr(character, 'is_broken') and character.is_broken:
                    status_icons += " 💥"
                
                # 실제 상태이상 시스템에서 상태 확인
                if hasattr(character, 'status_effects') and character.status_effects:
                    try:
                        from .status_effects import StatusType
                        from .new_skill_system import get_status_icon
                        
                        status_types_found = []
                        for effect in character.status_effects:
                            if effect.status_type not in status_types_found:
                                status_types_found.append(effect.status_type)
                                icon = get_status_icon(effect.status_type)
                                status_icons += f" {icon}"
                    except ImportError:
                        # 폴백: 구버전 호환
                        pass
                
                # 임시 상태 (구버전 호환)
                if hasattr(character, 'temp_speed_penalty') and getattr(character, 'temp_speed_penalty', 0) > 0:
                    status_icons += " 🟦"  # 둔화
                
                print(f"\r{side_icon} {Color.BRIGHT_CYAN}{character.name}{Color.RESET}: HP: {hp_color}{character.current_hp}{Color.RESET} | MP: {mp_color}{character.current_mp}{Color.RESET} | BRV: {brave}{status_icons}", end="", flush=True)
                print(f"\r⏳ {atb_bar} | SPD: {getattr(character, 'speed', 100)}", end="", flush=True)
            else:
                # 적군은 HP, BRV만 표시
                hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
                brave = getattr(character, 'brave_points', 0)
                
                # HP 색상
                if hp_ratio > 0.7:
                    hp_color = Color.BRIGHT_GREEN
                elif hp_ratio > 0.4:
                    hp_color = Color.YELLOW
                elif hp_ratio > 0.15:
                    hp_color = Color.BRIGHT_RED
                else:
                    hp_color = Color.RED
                
                # 상태이상 아이콘들 (실제 상태이상 시스템 연동)
                status_icons = ""
                
                # 캐스팅 상태
                if hasattr(character, 'is_casting') and character.is_casting:
                    status_icons += " 🔮"
                
                # BREAK 상태
                if hasattr(character, 'is_broken') and character.is_broken:
                    status_icons += " 💥"
                elif hasattr(character, 'is_broken_state') and character.is_broken_state:
                    status_icons += " 💥"
                
                # 실제 상태이상 시스템에서 상태 확인
                if hasattr(character, 'status_effects') and character.status_effects:
                    try:
                        from .status_effects import StatusType
                        from .new_skill_system import get_status_icon
                        
                        status_types_found = []
                        for effect in character.status_effects:
                            if effect.status_type not in status_types_found:
                                status_types_found.append(effect.status_type)
                                icon = get_status_icon(effect.status_type)
                                status_icons += f" {icon}"
                    except ImportError:
                        # 폴백: 구버전 호환
                        pass
                
                # 임시 상태 (구버전 호환)
                if hasattr(character, 'temp_speed_penalty') and getattr(character, 'temp_speed_penalty', 0) > 0:
                    status_icons += " 🟦"  # 둔화
                
                print(f"\r{side_icon} {Color.BRIGHT_RED}{character.name}{Color.RESET}: HP: {hp_color}{character.current_hp}{Color.RESET} | BRV: {brave}{status_icons}", end="", flush=True)
                print(f"\r⏳ {atb_bar} {arrow} | SPD: {getattr(character, 'speed', 100)}", end="", flush=True)
            
            time.sleep(frame_delay)
        
        # 최종 값으로 설정
        final_display_atb = int(new_atb // self.ATB_DISPLAY_SCALE)
        final_atb_bar = self._create_atb_bar(new_atb, show_percentage, is_ally, character)
        side_icon = "🛡️" if is_ally else "⚔️" if is_ally is False else "⏳"
        
        # 캐스팅/브레이크 상태 확인
        casting_status = ""
        if hasattr(character, 'is_casting') and character.is_casting:
            skill_name = getattr(character, 'casting_skill_name', '알 수 없는 스킬')
            casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
        
        break_status = ""
        if hasattr(character, 'is_broken_state') and character.is_broken_state:
            break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
        elif hasattr(character, 'is_broken') and character.is_broken:
            break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
        
        # 최종 상태 출력 (2줄 형식)
        if is_ally:
            # 아군은 HP, MP, BRV 모두 표시
            hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
            mp_ratio = character.current_mp / max(1, character.max_mp) if character.max_mp > 0 else 0
            brave = getattr(character, 'brave_points', 0)
            
            # HP 색상
            if hp_ratio > 0.7:
                hp_color = Color.BRIGHT_GREEN
            elif hp_ratio > 0.4:
                hp_color = Color.YELLOW
            elif hp_ratio > 0.15:
                hp_color = Color.BRIGHT_RED
            else:
                hp_color = Color.RED
            
            # MP 색상
            if mp_ratio > 0.7:
                mp_color = Color.BRIGHT_CYAN
            elif mp_ratio > 0.3:
                mp_color = Color.CYAN
            else:
                mp_color = Color.BLUE
            
            # 상태이상 아이콘들 (실제 상태이상 시스템 연동)
            status_icons = ""
            
            # 캐스팅 상태
            if hasattr(character, 'is_casting') and character.is_casting:
                status_icons += " 🔮"
            
            # BREAK 상태
            if hasattr(character, 'is_broken_state') and character.is_broken_state:
                status_icons += " �"
            elif hasattr(character, 'is_broken') and character.is_broken:
                status_icons += " �"
            
            # 실제 상태이상 시스템에서 상태 확인
            if hasattr(character, 'status_effects') and character.status_effects:
                try:
                    from .status_effects import StatusType
                    from .new_skill_system import get_status_icon
                    
                    status_types_found = []
                    for effect in character.status_effects:
                        if effect.status_type not in status_types_found:
                            status_types_found.append(effect.status_type)
                            icon = get_status_icon(effect.status_type)
                            status_icons += f" {icon}"
                except ImportError:
                    # 폴백: 구버전 호환
                    pass
            
            # 임시 상태 (구버전 호환)
            if hasattr(character, 'temp_speed_penalty') and getattr(character, 'temp_speed_penalty', 0) > 0:
                status_icons += " 🟦"  # 둔화
            
            print(f"\r{side_icon} {Color.BRIGHT_CYAN}{character.name}{Color.RESET}: HP: {hp_color}{character.current_hp}{Color.RESET} | MP: {mp_color}{character.current_mp}{Color.RESET} | BRV: {brave}{status_icons}")
            print(f"⏳ {final_atb_bar} | SPD: {getattr(character, 'speed', 100)}{casting_status}{break_status}")
            print()  # 아군 간 줄바꿈
        else:
            # 적군은 HP, BRV만 표시
            hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
            brave = getattr(character, 'brave_points', 0)
            
            # HP 색상
            if hp_ratio > 0.7:
                hp_color = Color.BRIGHT_GREEN
            elif hp_ratio > 0.4:
                hp_color = Color.YELLOW
            elif hp_ratio > 0.15:
                hp_color = Color.BRIGHT_RED
            else:
                hp_color = Color.RED
            
            # 상태이상 아이콘들 (실제 상태이상 시스템 연동)
            status_icons = ""
            
            # 캐스팅 상태
            if hasattr(character, 'is_casting') and character.is_casting:
                status_icons += " 🔮"
            
            # BREAK 상태
            if hasattr(character, 'is_broken') and character.is_broken:
                status_icons += " �"
            elif hasattr(character, 'is_broken_state') and character.is_broken_state:
                status_icons += " �"
            
            # 실제 상태이상 시스템에서 상태 확인
            if hasattr(character, 'status_effects') and character.status_effects:
                try:
                    from .status_effects import StatusType
                    from .new_skill_system import get_status_icon
                    
                    status_types_found = []
                    for effect in character.status_effects:
                        if effect.status_type not in status_types_found:
                            status_types_found.append(effect.status_type)
                            icon = get_status_icon(effect.status_type)
                            status_icons += f" {icon}"
                except ImportError:
                    # 폴백: 구버전 호환
                    pass
            
            # 임시 상태 (구버전 호환)
            if hasattr(character, 'temp_speed_penalty') and getattr(character, 'temp_speed_penalty', 0) > 0:
                status_icons += " 🟦"  # 둔화
            
            print(f"\r{side_icon} {Color.BRIGHT_RED}{character.name}{Color.RESET}: HP: {hp_color}{character.current_hp}{Color.RESET} | BRV: {brave}{status_icons}")
            print(f"⏳ {final_atb_bar} | SPD: {getattr(character, 'speed', 100)}{casting_status}{break_status}")
            print()  # 적군 간 줄바꿈
    
    def _create_atb_bar(self, atb_gauge: int, show_percentage: bool = True, is_ally: bool = None, character: Character = None) -> str:
        """ATB 게이지 바 생성 (아군/적군 구분 지원) - 향상된 포맷 및 상태별 색상"""
        # Color 클래스는 이미 파일 상단에서 import됨
        
        display_atb = atb_gauge // self.ATB_DISPLAY_SCALE
        filled = int(min(10, max(0, display_atb // 10)))  # int로 변환
        empty = int(10 - filled)  # int로 변환
        
        # 캐릭터 상태에 따른 색상 결정
        if character:
            # 캐스팅 중인 경우 - 보라색
            if hasattr(character, 'is_casting') and character.is_casting:
                bar_color = Color.BRIGHT_MAGENTA
            # 기절 등으로 움직일 수 없는 경우 - 회색
            elif hasattr(character, 'is_stunned') and character.is_stunned:
                bar_color = Color.BRIGHT_BLACK
            elif hasattr(character, 'is_paralyzed') and character.is_paralyzed:
                bar_color = Color.BRIGHT_BLACK
            # 느려진 상태 - 파란색
            elif hasattr(character, 'temp_speed_penalty') and getattr(character, 'temp_speed_penalty', 0) > 0:
                bar_color = Color.BLUE
            # 아군/적군 구분 (기본 색상)
            elif is_ally == True or (hasattr(character, 'character_class') and character.character_class != "Enemy"):
                bar_color = Color.BRIGHT_CYAN  # 아군: 밝은 청록색
            else:
                bar_color = Color.BRIGHT_RED  # 적군: 밝은 빨간색
        else:
            # 캐릭터 정보가 없으면 기본 청록색
            bar_color = Color.CYAN
        
        # READY 상태인 경우 더 밝은 색상으로 전체 바 표시
        if atb_gauge >= self.ATB_READY_THRESHOLD:
            if character and hasattr(character, 'is_casting') and character.is_casting:
                ready_bar = f"{Color.BRIGHT_MAGENTA}{'▰'*10}{Color.RESET}"
            elif character and (hasattr(character, 'is_stunned') and character.is_stunned):
                ready_bar = f"{Color.BRIGHT_BLACK}{'▰'*10}{Color.RESET}"
            else:
                # READY 상태는 주황색으로 표시
                ready_bar = f"{Color.BRIGHT_YELLOW}{'▰'*10}{Color.RESET}"
                
            # 아군인 경우 READY 바에도 공백 추가
            if is_ally == True or (character and hasattr(character, 'character_class') and character.character_class != "Enemy"):
                bar = f"{ready_bar} "  # 아군용 공백 추가
            else:
                bar = ready_bar  # 적군은 공백 없음
        else:
            # 진행도에 따른 그라데이션 색상 (푸른색 → 하늘색)
            if display_atb >= 80:
                progress_color = Color.BRIGHT_CYAN  # 80% 이상: 밝은 하늘색
            elif display_atb >= 60:
                progress_color = Color.CYAN  # 60-80%: 하늘색
            elif display_atb >= 40:
                progress_color = Color.BLUE  # 40-60%: 푸른색
            else:
                progress_color = Color.BRIGHT_BLUE  # 40% 미만: 어두운 파랑
                
            # 부분적으로 채워진 바 (그라데이션 색상 적용) - 아군에게 공백 추가
            filled_part = f"{progress_color}{'▰'*filled}{Color.RESET}"
            empty_part = f"{Color.BRIGHT_BLACK}{'▱'*empty}{Color.RESET}"
            
            # 아군인 경우 뒤에 공백 추가
            if is_ally == True or (character and hasattr(character, 'character_class') and character.character_class != "Enemy"):
                bar = f"{filled_part}{empty_part} "  # 아군용 공백 추가
            else:
                bar = f"{filled_part}{empty_part}"  # 적군은 공백 없음
        
        # 기본적으로 바만 반환 (색상 별도 적용)
        return bar
    
    def _show_realtime_atb_status(self, party: List[Character], enemies: List[Character]):
        """실시간 ATB 상태 표시 (3초간)"""
        import time
        import os
        
        print(f"\n{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        print(f"{Color.BRIGHT_WHITE}⏳ 실시간 ATB 상태 - Dawn of Stellar{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'='*80}{Color.RESET}")
        
        all_combatants = party + enemies
        start_time = time.time()
        
        try:
            # 설정 로드
            from ..config import GameConfig
            config = GameConfig()
            atb_settings = config.ATB_SETTINGS
        except ImportError:
            atb_settings = {
                "animation_enabled": True,
                "show_percentage": True,
                "frame_delay": 0.05
            }
        
        while time.time() - start_time < 3.0:  # 3초간 표시
            # 화면 클리어 (커서를 맨 위로)
            print(f"\033[{len(all_combatants) + 10}A", end="")  # 위로 이동
            
            print(f"{Color.BRIGHT_CYAN}⏳ 실시간 ATB 상태{Color.RESET}")
            print(f"{Color.BRIGHT_CYAN}{'═'*80}{Color.RESET}")
            
            # 아군 파티 표시
            print(f"{Color.BRIGHT_GREEN}🛡️ 아군 파티{Color.RESET}")
            print(f"{Color.GREEN}{'─'*80}{Color.RESET}")
            for combatant in all_combatants:
                if isinstance(combatant, dict) or not combatant.is_alive:
                    continue
                if combatant in party:
                    atb_gauge = getattr(combatant, 'atb_gauge', 0)
                    atb_bar = self._create_atb_bar(atb_gauge, atb_settings.get("show_percentage", True), is_ally=True, character=combatant)
                    
                    # HP/MP/BRV 정보 추가
                    hp_ratio = combatant.current_hp / combatant.max_hp if combatant.max_hp > 0 else 0
                    mp_ratio = combatant.current_mp / max(1, combatant.max_mp) if combatant.max_mp > 0 else 0
                    brave = getattr(combatant, 'brave_points', 0)
                    
                    # HP 색상 (상태에 따라)
                    if hp_ratio > 0.7:
                        hp_color = Color.BRIGHT_GREEN
                    elif hp_ratio > 0.4:
                        hp_color = Color.YELLOW
                    elif hp_ratio > 0.15:
                        hp_color = Color.BRIGHT_RED
                    else:
                        hp_color = Color.RED
                    
                    # MP 색상 (상태에 따라)
                    if mp_ratio > 0.7:
                        mp_color = Color.BRIGHT_CYAN
                    elif mp_ratio > 0.3:
                        mp_color = Color.CYAN
                    else:
                        mp_color = Color.BLUE
                    
                    # ATB 표시 정보
                    display_atb = int(atb_gauge // self.ATB_DISPLAY_SCALE)
                    
                    # 캐스팅 상태 확인
                    casting_status = ""
                    if hasattr(combatant, 'is_casting') and combatant.is_casting:
                        skill_name = getattr(combatant, 'casting_skill_name', '알 수 없는 스킬')
                        casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
                    
                    # BREAK 상태 확인
                    break_status = ""
                    if hasattr(combatant, 'is_broken_state') and combatant.is_broken_state:
                        break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                    
                    # 상태이상 확인
                    status_effects = ""
                    if hasattr(combatant, 'is_stunned') and combatant.is_stunned:
                        status_effects += f" {Color.BRIGHT_BLACK}[기절]{Color.RESET}"
                    if hasattr(combatant, 'temp_speed_penalty') and getattr(combatant, 'temp_speed_penalty', 0) > 0:
                        status_effects += f" {Color.BLUE}[둔화]{Color.RESET}"
                    
                    print(f"  {Color.BRIGHT_CYAN}{combatant.name:12}{Color.RESET}: HP: {hp_color}{combatant.current_hp:4}{Color.RESET} | MP: {mp_color}{combatant.current_mp:3}{Color.RESET} | BRV: {brave:4}")
                    print(f"    ⏳ {atb_bar} | SPD: {getattr(combatant, 'speed', 100):3}{casting_status}{break_status}{status_effects}")
                    print()  # 아군 간 줄바꿈
            
            print(f"{Color.GREEN}{'─'*80}{Color.RESET}")
            
            # 적군 표시
            print(f"{Color.BRIGHT_RED}⚔️ 적군{Color.RESET}")
            print(f"{Color.RED}{'─'*80}{Color.RESET}")
            for combatant in all_combatants:
                if isinstance(combatant, dict) or not combatant.is_alive:
                    continue
                if combatant not in party:
                    atb_gauge = getattr(combatant, 'atb_gauge', 0)
                    atb_bar = self._create_atb_bar(atb_gauge, atb_settings.get("show_percentage", True), is_ally=False, character=combatant)
                    
                    # HP/BRV 정보 추가 (적군은 MP 정보 없음)
                    hp_ratio = combatant.current_hp / combatant.max_hp if combatant.max_hp > 0 else 0
                    brave = getattr(combatant, 'brave_points', 0)
                    
                    # HP 색상 (상태에 따라)
                    if hp_ratio > 0.7:
                        hp_color = Color.BRIGHT_GREEN
                    elif hp_ratio > 0.4:
                        hp_color = Color.YELLOW
                    elif hp_ratio > 0.15:
                        hp_color = Color.BRIGHT_RED
                    else:
                        hp_color = Color.RED
                    
                    # ATB 표시 정보
                    display_atb = int(atb_gauge // self.ATB_DISPLAY_SCALE)
                    
                    # 캐스팅 상태 확인
                    casting_status = ""
                    if hasattr(combatant, 'is_casting') and combatant.is_casting:
                        skill_name = getattr(combatant, 'casting_skill_name', '알 수 없는 스킬')
                        casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
                    
                    # BREAK 상태 확인
                    break_status = ""
                    if hasattr(combatant, 'is_broken') and combatant.is_broken:
                        break_status = f" {Color.BRIGHT_RED}[BREAK]{Color.RESET}"
                    
                    # 상태이상 확인
                    status_effects = ""
                    if hasattr(combatant, 'is_stunned') and combatant.is_stunned:
                        status_effects += f" {Color.BRIGHT_BLACK}[기절]{Color.RESET}"
                    if hasattr(combatant, 'temp_speed_penalty') and getattr(combatant, 'temp_speed_penalty', 0) > 0:
                        status_effects += f" {Color.BLUE}[둔화]{Color.RESET}"
                    
                    print(f"  {Color.BRIGHT_RED}{combatant.name:12}{Color.RESET}: HP: {hp_color}{combatant.current_hp:4}{Color.RESET} | BRV: {brave:4}")
                    print(f"    ⏳ {atb_bar} | SPD: {getattr(combatant, 'speed', 100):3}{casting_status}{break_status}{status_effects}")
                    print()  # 적군 간 줄바꿈
                
                
            print(f"{Color.BRIGHT_CYAN}{'═'*80}{Color.RESET}")
            print(f"{Color.YELLOW}ESC를 눌러 종료...{Color.RESET}")
            
            # 키 입력 체크 (논블로킹)
            try:
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\x1b':  # ESC 키
                        break
            except ImportError:
                # Unix 시스템에서는 select 사용
                import select
                import sys
                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1)
                    if key == '\x1b':  # ESC 키
                        break
            
            # ATB 업데이트
            self.update_atb_gauges(all_combatants, show_animation=False)
            
            time.sleep(atb_settings.get("frame_delay", 0.05))
        
        print(f"\n{Color.BRIGHT_GREEN}실시간 ATB 상태 표시 종료{Color.RESET}")
        input("계속하려면 Enter를 누르세요...")
        
        # 화면 클리어
        os.system('cls' if os.name == 'nt' else 'clear')
                
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
            
            # 캐스팅 상태 체크
            casting_info = ""
            if hasattr(combatant, 'is_casting') and combatant.is_casting:
                if hasattr(combatant, 'get_casting_progress'):
                    progress = combatant.get_casting_progress(getattr(self, 'battle_time', 0))
                else:
                    progress = 0.5  # 기본값
                skill_name = getattr(combatant, 'casting_skill', {}).get('name', '스킬')
                casting_info = f" 🔮 {skill_name}: [{progress*100:.0f}%]"
                
            atb_gauge = int(getattr(combatant, 'atb_gauge', 0))
            # 디스플레이용으로 100 스케일로 변환
            display_atb = atb_gauge // self.ATB_DISPLAY_SCALE
            if atb_gauge >= self.ATB_READY_THRESHOLD:
                bar = f"{Color.BRIGHT_CYAN}{'█'*10}{Color.RESET}"
                status = f"{Color.BRIGHT_CYAN}⚡READY{Color.RESET}"
            else:
                filled = int(min(10, max(0, display_atb // 10)))  # 0-10 범위로 제한
                bar = f"{Color.CYAN}{'█'*filled}{Color.BRIGHT_BLACK}{'░'*(10-filled)}{Color.RESET}"
                status = f"{Color.CYAN}{display_atb:3}%{Color.RESET}"  # 디스플레이 ATB 값 사용
            
            rank = f"{i+1}."
            print(f"  {rank:3} {name_color}{combatant.name:12}{Color.RESET} [{bar}]   {status}{casting_info}")
        
        print()
                
    def get_action_order(self, all_combatants: List[Character]) -> List[Character]:
        """행동 순서 결정 - 공정한 우선순위 기반 단일 선택"""
        ready_combatants = [c for c in all_combatants if c.is_alive and c.atb_gauge >= self.ATB_READY_THRESHOLD]
        
        if not ready_combatants:
            return []
        
        # ATB가 100% 이상인 캐릭터 중 우선순위 결정 (10000 스케일)
        # 1. ATB 게이지가 더 높은 캐릭터 (더 중요한 가중치)
        # 2. 속도가 더 빠른 캐릭터
        # 3. 무작위 (동점인 경우 - 아군/적군 편향 방지)
        def priority_key(combatant):
            # ATB 게이지를 1000배로 가중치를 높여서 주요 우선순위로 만듦
            atb_weight = combatant.atb_gauge * 1000
            speed_weight = getattr(combatant, 'speed', 50)
            # 완전한 무작위로 아군/적군 편향 제거
            random_tiebreaker = random.random() * 100
            return (atb_weight, speed_weight, random_tiebreaker)
        
        # 가장 높은 우선순위 캐릭터 선택
        fastest = max(ready_combatants, key=priority_key)
        
        # 디버그 정보 출력 (턴 순서 문제 해결 확인용)
        party_ready = [c for c in ready_combatants if c in getattr(self, '_current_party', [])]
        enemy_ready = [c for c in ready_combatants if c in getattr(self, '_current_enemies', [])]
        
        if len(party_ready) > 0 and len(enemy_ready) > 0:
            selected_type = "아군" if fastest in getattr(self, '_current_party', []) else "적군"
            print(f"🎯 턴 선택: {selected_type} {fastest.name} (ATB:{fastest.atb_gauge:.1f}, SPD:{getattr(fastest, 'speed', 50)})")
            print(f"   준비된 아군: {len(party_ready)}명, 적군: {len(enemy_ready)}명")
        
        return [fastest]
        
    def check_battle_end(self, party: List[Character], enemies: List[Character]) -> bool:
        """전투 종료 조건 확인"""
        party_alive = any(p.is_alive for p in party)
        enemies_alive = any(e.is_alive for e in enemies)
        
        return not party_alive or not enemies_alive
        
    def determine_winner(self, party: List[Character], enemies: List[Character]) -> bool:
        """승부 결정 - 비주얼 이펙트 포함"""
        party_alive = any(p.is_alive for p in party)
        
        # 전투 종료 로깅
        winner = "플레이어" if party_alive else "적"
        battle_duration = time.time() - getattr(self, 'battle_start_time', time.time())
        self.combat_logger.log_battle_end(winner, battle_duration)
        
        if party_alive:
            # 🎵 승리 BGM 재생
            try:
                if BGMType and get_audio_manager:
                    audio_mgr = get_audio_manager()
                    if audio_mgr:
                        audio_mgr.play_bgm(BGMType.VICTORY)
                        print(f"🎵 승리 BGM 재생!")
                    else:
                        print(f"⚠️ 오디오 매니저를 가져올 수 없습니다")
                else:
                    print(f"⚠️ 오디오 시스템을 임포트할 수 없습니다")
            except Exception as e:
                print(f"⚠️ 승리 BGM 재생 실패: {e}")
            
            # 승리 이펙트
            print(f"\n{Color.BRIGHT_GREEN}{'='*50}")
            print(f"🎉 승리! 🎉")
            print(f"{'='*50}{Color.RESET}")
            
            # 승리 후 일시정지 - 사용자가 결과를 확인할 시간
            print(f"\n{Color.BRIGHT_YELLOW}전투에서 승리했습니다!{Color.RESET}")
            
            # 전투 통계 출력
            summary = self.combat_logger.get_session_summary()
            print(f"\n📊 전투 통계:")
            print(f"  플레이어 총 데미지: {summary['total_player_damage']}")
            print(f"  적 총 데미지: {summary['total_enemy_damage']}")
            print(f"  총 치유량: {summary['total_healing']}")
            print(f"  로그 파일: {summary['log_file']}")
            
            input(f"{Color.YELLOW}계속하려면 Enter를 누르세요...{Color.RESET}")
            
            # 승리 후 입력 버퍼 클리어
            if hasattr(self, 'keyboard') and self.keyboard:
                self.keyboard.clear_input_buffer()
            
        else:
            # 패배 이펙트  
            print(f"\n{Color.BRIGHT_RED}{'='*50}")
            print(f"💀 패배... 💀")
            print(f"{'='*50}{Color.RESET}")
            
            # 패배 후 일시정지 - 사용자가 결과를 확인할 시간
            print(f"\n{Color.BRIGHT_RED}전투에서 패배했습니다...{Color.RESET}")
            
            # 전투 통계 출력
            summary = self.combat_logger.get_session_summary()
            print(f"\n📊 전투 통계:")
            print(f"  플레이어 총 데미지: {summary['total_player_damage']}")
            print(f"  적 총 데미지: {summary['total_enemy_damage']}")
            print(f"  총 치유량: {summary['total_healing']}")
            print(f"  로그 파일: {summary['log_file']}")
            
            input(f"{Color.RED}계속하려면 Enter를 누르세요...{Color.RESET}")
            
            # 패배 후 입력 버퍼 클리어
            if hasattr(self, 'keyboard') and self.keyboard:
                self.keyboard.clear_input_buffer()
            
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
                print(f"💥 {target.name}에게 {actual_damage} HP 데미지!")
                
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
                print(f"💥 {target.name}에게 {actual_damage} HP 데미지!")
                
            elif skill_type == SkillType.HEAL:
                # 치유
                heal_amount = self._calculate_heal_amount(skill, caster)
                actual_heal = target.heal(heal_amount)
                print(f"💚 {target.name}이(가) {actual_heal} HP 회복!")
                
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
        """BRV 데미지 계산 - 로깅 시스템 통합"""
        return self.combat_logger.calculate_brv_damage_with_log(skill, caster, target, brv_power)
    
    def _calculate_hp_damage_from_skill(self, skill, caster, target, hp_power):
        """스킬의 HP 데미지 계산 - 로깅 시스템 통합"""
        final_damage = self.combat_logger.calculate_hp_damage_with_log(skill, caster, target, hp_power)
        
        # HP 공격 후 BRV 소모 (오페라 옴니아 방식)
        if hasattr(caster, 'consume_brave_points'):
            consumed_brv = caster.consume_brave_points()
            print(f"  {caster.name}의 BRV {consumed_brv} 소모됨")
        else:
            # 폴백: 직접 BRV를 0으로
            caster.brave_points = 0
            print(f"  {caster.name}의 BRV가 0이 되었습니다")
        
        return final_damage
    
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
    
    def _apply_special_skill(self, skill, caster, target):
        """특수 스킬 효과 적용"""
        skill_name = skill.get("name", "")
        
        # 연속공격 효과
        if "연속" in skill_name or skill.get("consecutive_attacks", 0) > 0:
            attacks = skill.get("consecutive_attacks", 2)
            print(f"⚔️ {skill_name}: {attacks}연속 공격!")
            
            total_damage = 0
            for i in range(attacks):
                print(f"  🗡️ {i+1}번째 공격:")
                
                # 각 공격별 BRV/HP 데미지 적용
                if skill.get("brv_power", 0) > 0:
                    brv_damage = self._calculate_brv_damage(skill, caster, target, skill.get("brv_power"))
                    old_brv = target.brave_points
                    target.brave_points -= brv_damage
                    target.brave_points = max(0, target.brave_points)
                    print(f"    ⚡ BRV: {old_brv} → {target.brave_points} (-{brv_damage})")
                    total_damage += brv_damage
                
                if skill.get("hp_power", 0) > 0:
                    hp_damage = self._calculate_hp_damage_from_skill(skill, caster, target, skill.get("hp_power"))
                    actual_damage = target.take_damage(hp_damage)
                    print(f"    💥 HP: -{actual_damage}")
                    total_damage += actual_damage
                
                # BREAK 체크
                if target.brave_points <= 0 and hasattr(target, 'apply_break_if_needed'):
                    if target.apply_break_if_needed():
                        print(f"    💥 {target.name}이(가) BREAK 상태가 되었습니다!")
                
                # 대상이 죽으면 연속공격 중단
                if not target.is_alive:
                    print(f"    ⚰️ {target.name}이(가) 쓰러졌습니다! 연속공격 중단.")
                    
                    # 🔊 적 처치 SFX 재생
                    if hasattr(self, 'audio_system') and self.audio_system:
                        self.audio_system.play_sfx("enemy_defeat")
                    elif hasattr(self, 'sound_manager') and self.sound_manager:
                        self.sound_manager.play_sfx("enemy_defeat")
                    
                    break
                    
                # 연속공격 간 짧은 딜레이
                time.sleep(0.3)
            
            print(f"💀 총 {total_damage} 데미지 가함!")
            
        # 전체공격 효과
        elif "전체" in skill_name or skill.get("area_attack", False):
            print(f"💥 {skill_name}: 전체 공격!")
            # 이미 targets에 전체가 포함되어 있으므로 개별 처리는 상위에서 수행됨
            
        # 흡혈 효과
        elif "흡혈" in skill_name or skill.get("drain_hp", False):
            if skill.get("hp_power", 0) > 0:
                hp_damage = self._calculate_hp_damage_from_skill(skill, caster, target, skill.get("hp_power"))
                actual_damage = target.take_damage(hp_damage)
                
                # 가한 데미지의 일정 비율만큼 회복
                drain_rate = skill.get("drain_rate", 0.3)  # 30% 기본
                heal_amount = int(actual_damage * drain_rate)
                actual_heal = caster.heal(heal_amount)
                
                print(f"💥 {target.name}에게 {actual_damage} HP 데미지!")
                print(f"💚 {caster.name}이(가) {actual_heal} HP 흡혈 회복!")
        
        # 무모한 돌격 효과
        elif "무모한 돌격" in skill_name:
            # 무모한 돌격: 강력한 HP 공격 + 자신도 데미지
            damage_to_target = self._calculate_hp_damage_from_skill(skill, caster, target, 150)
            actual_damage = target.take_damage(damage_to_target)
            print(f"💥 {target.name}에게 {actual_damage} 데미지! (무모한 돌격)")
            
            # 자신에게도 반동 데미지
            self_damage = int(damage_to_target * 0.3)
            caster.take_damage(self_damage)
            print(f"💢 {caster.name}도 반동으로 {self_damage} 데미지를 받았습니다!")
        
        # 영혼 파악 효과
        elif "영혼 파악" in skill_name:
            # 영혼 파악: 적의 정보 표시 + 정신 데미지
            print(f"👁️ {caster.name}이(가) {target.name}의 영혼을 들여다봅니다...")
            
            # 적 정보 분석 표시
            print(f"📊 === {target.name}의 상태 분석 ===")
            print(f"  ❤️ HP: {target.current_hp}/{target.max_hp} ({target.current_hp/target.max_hp*100:.1f}%)")
            if hasattr(target, 'brave_points'):
                print(f"  ⚡ BRV: {target.brave_points}")
            if hasattr(target, 'physical_attack'):
                print(f"  ⚔️ 물리공격: {target.physical_attack}")
            if hasattr(target, 'physical_defense'):
                print(f"  🛡️ 물리방어: {target.physical_defense}")
            if hasattr(target, 'wounds') and target.wounds > 0:
                print(f"  🩸 WOUND: {target.wounds}")
            
            # 특수 상태 확인
            if hasattr(target, 'is_broken') and target.is_broken:
                print(f"  💥 상태: BREAK")
            
            # 정신 데미지 (작은 HP 데미지)
            soul_damage = int(getattr(caster, 'magic_attack', 100) * 0.5)  # 마법공격력의 50%
            actual_damage = target.take_damage(soul_damage)
            print(f"🧠 정신 공격으로 {actual_damage} 데미지!")
        
        # 진실 간파 효과
        elif "진실 간파" in skill_name:
            # 진실 간파: 철학자의 스킬 - 적의 약점과 진실 노출
            print(f"🔍 {caster.name}이(가) 철학의 힘으로 {target.name}의 진실을 간파합니다...")
            
            # 적의 상세 정보 표시 (철학자의 지혜)
            print("=" * 50)
            print(f"📖 【{target.name}의 진실】")
            print("=" * 50)
            
            # 기본 스탯 분석
            defense_ratio = target.defense / caster.attack if hasattr(caster, 'attack') and caster.attack > 0 else 1.0
            threat_level = "낮음" if defense_ratio < 0.7 else "보통" if defense_ratio < 1.3 else "높음"
            
            print(f"🛡️ 방어력: {getattr(target, 'defense', getattr(target, 'physical_defense', 0))} (위협도: {threat_level})")
            print(f"⚔️ 공격력: {getattr(target, 'attack', getattr(target, 'physical_attack', 0))}")
            
            # BRV 정보가 있다면 표시
            if hasattr(target, 'current_brave'):
                print(f"💎 현재 BRV: {target.current_brave}")
                if hasattr(target, 'max_brave'):
                    print(f"💎 최대 BRV: {target.max_brave}")
            elif hasattr(target, 'brave_points'):
                print(f"💎 현재 BRV: {target.brave_points}")
            
            # 약점 노출 효과
            vulnerability_bonus = 0.35  # 35% 추가 데미지
            duration = 3  # 3턴 지속
            
            if hasattr(target, 'temp_vulnerability'):
                target.temp_vulnerability = max(target.temp_vulnerability, vulnerability_bonus)
            else:
                target.temp_vulnerability = vulnerability_bonus
                
            if hasattr(target, 'vulnerability_turns'):
                target.vulnerability_turns = max(target.vulnerability_turns, duration)
            else:
                target.vulnerability_turns = duration
            
            print("=" * 50)
            print(f"⚠️ 【약점 노출】")
            print(f"   📈 받는 데미지 +{vulnerability_bonus*100:.0f}% ({duration}턴)")
            print(f"   🎯 철학자의 지혜가 적의 약점을 드러냈습니다!")
            print("=" * 50)
            
            # 정신적 충격 데미지 (진실을 마주한 충격)
            psychic_damage = int(getattr(caster, 'magic_attack', 100) * 0.8)  # 철학자의 정신력 기반
            actual_damage = target.take_damage(psychic_damage)
            print(f"🧠 진실의 충격! {target.name}에게 {actual_damage} 정신 데미지!")
        
        # 기본적인 단일 공격 (특수 효과 없음)
        else:
            if skill.get("brv_power", 0) > 0:
                brv_damage = self._calculate_brv_damage(skill, caster, target, skill.get("brv_power"))
                old_brv = target.brave_points
                target.brave_points -= brv_damage
                target.brave_points = max(0, target.brave_points)
                print(f"⚡ {target.name}의 BRV: {old_brv} → {target.brave_points} (-{brv_damage})")
                
                # BREAK 체크
                if target.brave_points <= 0 and hasattr(target, 'apply_break_if_needed'):
                    if target.apply_break_if_needed():
                        print(f"💥 {target.name}이(가) BREAK 상태가 되었습니다!")
            
            if skill.get("hp_power", 0) > 0:
                hp_damage = self._calculate_hp_damage_from_skill(skill, caster, target, skill.get("hp_power"))
                actual_damage = target.take_damage(hp_damage)
                print(f"💥 {target.name}에게 {actual_damage} HP 데미지!")