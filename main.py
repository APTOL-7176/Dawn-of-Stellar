#!/usr/bin/env python3
"""
Dawn Of Stellar - 메인 파일  
별빛의 여명 - 28명의 개성있는 캐릭터와 ATB 전투 시스템을 가진 전술 RPG
🎮 완전 통합 시스템 버전 - 165+ 상태효과, 100+ 적, FFVII BGM/SFX, 튜토리얼 🎮
"""

import sys
import time
import random
from typing import List, Tuple, Dict, Any
from enum import Enum

# Windows용 curses 대안
try:
    import curses
except ImportError:
    # Windows에서 curses가 없을 경우 더미 모듈
    class DummyCurses:
        def initscr(self): pass
        def endwin(self): pass
        def cbreak(self): pass
        def noecho(self): pass
        def curs_set(self, visibility): pass
    curses = DummyCurses()

# 게임 상태 정의
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class ParticleType(Enum):
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    HEALING = "healing"
    SPARK = "spark"
    STAR = "star"
    BLOOD = "blood"

try:
    from game.character import Character, PartyManager
    from game.character_database import CharacterDatabase
    from game.combat import CombatManager
    from game.display import GameDisplay
    from game.world import GameWorld
    from game.meta_progression import MetaProgression, get_meta_progression
    from game.items import ItemDatabase
    from game.input_utils import KeyboardInput, get_single_key_input
    from game.color_text import (ColorText, Color, bright_cyan, bright_yellow, bright_green, 
                                 bright_white, bright_red, red, green, blue, yellow, 
                                 cyan, magenta, colored, rarity_colored, RED, RESET)
    from game.merchant import MerchantManager
    from game.permanent_progression import PermanentProgressionSystem
    from game.random_encounters import (RandomEncounterManager, FieldSkillManager, 
                                        get_encounter_manager, get_field_skill_manager)
    import config as game_config
except ImportError as e:
    print(f"핵심 모듈 임포트 오류: {e}")
    print("필요한 게임 모듈을 찾을 수 없습니다.")
    sys.exit(1)

# 🚀 완전 통합된 신규 시스템들
try:
    from game.new_skill_system import NewSkillSystem
    def get_skill_manager():
        return NewSkillSystem()
    SkillManager = NewSkillSystem
except ImportError:
    print("모듈 임포트 오류: new_skill_system 모듈을 찾을 수 없습니다.")
    def get_skill_manager():
        return None
    
try:
    from game.audio_system import AudioManager, BGMType, SFXType, get_audio_manager
    # 최종 시스템 사용: 3층 단위 BGM + 순환/랜덤 시스템
    def get_audio_system(debug_mode: bool = False):
        return get_audio_manager()
    def get_unified_audio_system(debug_mode: bool = False):
        return get_audio_manager()
except ImportError:
    print("모듈 임포트 오류: audio_system을 찾을 수 없습니다.")
    def get_audio_system(debug_mode: bool = False):
        return None
    def get_unified_audio_system(debug_mode: bool = False):
        return None
    
try:
    from game.enemy_system import get_enemy_manager, EnemyManager
except ImportError:
    print("모듈 임포트 오류: get_enemy_manager 함수를 찾을 수 없습니다.")
    def get_enemy_manager():
        return None
    
# 선택적 시스템들 (없어도 게임 실행 가능)
try:
    from game.save_system import get_save_manager, get_auto_save_manager, GameStateSerializer
    from game.save_system import show_save_menu as save_system_show_save_menu
    from game.save_system import show_load_menu as save_system_show_load_menu
    SAVE_SYSTEM_AVAILABLE = True
    print("✅ 저장 시스템 모듈 로드 성공")
except ImportError as e:
    print(f"⚠️ 저장 시스템 모듈 로드 실패: {e}")

# 새로운 캐릭터 생성 시스템
try:
    from game.easy_character_creator import get_easy_character_creator
    EASY_CREATOR_AVAILABLE = True
    print("✅ 쉬운 캐릭터 생성 시스템 로드 성공")
except ImportError as e:
    print(f"⚠️ 쉬운 캐릭터 생성 시스템 로드 실패: {e}")
    EASY_CREATOR_AVAILABLE = False
    SAVE_SYSTEM_AVAILABLE = False
    def get_save_manager():
        return None
    
    def get_auto_save_manager():
        return None
    def get_auto_save_manager():
        return None

    def save_system_show_save_menu(save_manager):
        print("⚠️ 저장 시스템을 사용할 수 없습니다.")
        return "CANCEL"
    
    def save_system_show_load_menu(save_manager):
        print("⚠️ 저장 시스템을 사용할 수 없습니다.")
        return None
    
    class GameStateSerializer:
        @staticmethod
        def create_game_state(game):
            print("⚠️ 저장 시스템을 사용할 수 없습니다.")
            return {}
        
        @staticmethod
        def serialize_character(character):
            return {}
        
        @staticmethod
        def deserialize_character(char_data):
            return None
        
        @staticmethod
        def serialize_explored_tiles(world):
            return []
        
        @staticmethod
        def restore_explored_tiles(world, tiles):
            pass
    
try:
    from game.ui_system import get_ui_manager, UIManager
except ImportError:
    print("모듈 임포트 오류: ui_system 모듈을 찾을 수 없습니다.")
    def get_ui_manager():
        return None

try:
    from game.integrated_game_manager import IntegratedGameManager
except ImportError:
    print("모듈 임포트 오류: IntegratedGameManager를 찾을 수 없습니다.")
    IntegratedGameManager = None
    
try:
    from game.tutorial_system import get_tutorial_manager, TutorialManager, show_tutorial_selection_menu
except ImportError:
    print("모듈 임포트 오류: tutorial_system 모듈을 찾을 수 없습니다.")
    def get_tutorial_manager():
        return None
    def show_tutorial_selection_menu():
        return None
    
try:
    from game.auto_party_builder import get_auto_party_builder, AutoPartyBuilder
except ImportError:
    print("모듈 임포트 오류: auto_party_builder 모듈을 찾을 수 없습니다.")
    def get_auto_party_builder():
        return None
    
try:
    from game.field_skill_system import get_field_skill_system, FieldSkillSystem
except ImportError:
    print("모듈 임포트 오류: field_skill_system 모듈을 찾을 수 없습니다.")
    def get_field_skill_system():
        return None
    
try:
    from game.passive_selection import show_passive_selection_ui
except ImportError:
    print("모듈 임포트 오류: passive_selection 모듈을 찾을 수 없습니다.")
    def show_passive_selection_ui(*args):
        return []
    
try:
    from game.adaptive_balance import adaptive_balance
except ImportError:
    print("모듈 임포트 오류: adaptive_balance 모듈을 찾을 수 없습니다.")
    def adaptive_balance(*args):
        return None

# 🔥 기존 호환 시스템들
try:
    from game.element_system import ElementSystem, ElementType, get_element_system
except ImportError:
    print("모듈 임포트 오류: element_system 모듈을 찾을 수 없습니다.")
    def get_element_system():
        return None
    
try:
    from game.new_skill_system import StatusType
    StatusType = StatusType
    StatusEffect = None
    StatusManager = None
except ImportError:
    print("모듈 임포트 오류: new_skill_system 모듈을 찾을 수 없습니다.")
    StatusType = None
    StatusEffect = None

# 튜토리얼 시스템 (옵셔널)
try:
    from game.tutorial import show_tutorial, show_help
except ImportError:
    def show_tutorial():
        print("🎓 튜토리얼 시스템을 불러올 수 없습니다.")
    def show_help():
        print("📚 도움말 시스템을 불러올 수 없습니다.")

try:
    from game.item_system import get_item_database
except ImportError:
    print("모듈 임포트 오류: item_system 모듈을 찾을 수 없습니다.")
    def get_item_database():
        return None
    
# FFVII 사운드 시스템은 이제 통합 오디오 시스템으로 대체됨
def get_ffvii_sound_system():
    """FFVII 사운드 시스템 호환성 함수"""
    return get_unified_audio_system()


class DawnOfStellarGame:
    """Dawn Of Stellar 메인 게임 클래스 - 완전 통합 시스템"""
    
    def __init__(self):
        # 기존 시스템들
        self.display = GameDisplay()
        self.party_manager = PartyManager()
        self.combat_manager = CombatManager()
        self.merchant_manager = MerchantManager()
        self.permanent_progression = PermanentProgressionSystem()
        self.world = GameWorld(party_manager=self.party_manager)
        
        # 🌟 메타 진행 시스템 추가
        self.meta_progression = get_meta_progression()
        
        # � 요리 시스템 연결
        try:
            from game.cooking_system import cooking_system
            from game.gathering_limiter import set_party_manager_for_gathering
            cooking_system.set_party_manager(self.party_manager)
            set_party_manager_for_gathering(self.party_manager)
        except ImportError:
            pass
        
        # �🎮 통합 게임 매니저 초기화
        self.game_manager = IntegratedGameManager() if IntegratedGameManager else None
        
        # 🎯 랜덤 조우 및 필드 스킬 시스템
        self.encounter_manager = get_encounter_manager()
        self.field_skill_manager = get_field_skill_manager()
        
        # 🚀 신규 통합 시스템들
        self.skill_manager = get_skill_manager() if callable(get_skill_manager) else None
        
        # 🎵 안전한 오디오 시스템 초기화
        try:
            print("🎵 오디오 시스템을 초기화하는 중...")
            self.audio_system = get_unified_audio_system(debug_mode=True) if callable(get_unified_audio_system) else None
            self.sound_manager = self.audio_system  # 통합된 오디오 시스템 사용
            
            if self.sound_manager and hasattr(self.sound_manager, 'mixer_available') and self.sound_manager.mixer_available:
                print("✅ 오디오 시스템 초기화 성공!")
            else:
                print("🔇 오디오 시스템을 사용할 수 없습니다. 사운드 없이 게임을 진행합니다.")
                
        except Exception as e:
            print(f"⚠️ 사운드 시스템 초기화 실패: {e}")
            print("🔇 사운드 없이 게임을 계속합니다.")
            self.audio_system = None
            self.sound_manager = None
        
        self.enemy_manager = get_enemy_manager() if callable(get_enemy_manager) else None
        self.save_manager = get_save_manager() if callable(get_save_manager) else None
        self.auto_save_manager = get_auto_save_manager() if callable(get_auto_save_manager) else None
        self.ui_manager = get_ui_manager() if callable(get_ui_manager) else None
        self.tutorial_manager = get_tutorial_manager() if callable(get_tutorial_manager) else None
        
        # 🎯 적응형 밸런스 시스템 초기화
        try:
            from game.adaptive_balance import adaptive_balance
            self.adaptive_balance = adaptive_balance
            self.adaptive_balance.start_session()
        except ImportError:
            self.adaptive_balance = None
        
        # 🔥 원소 및 상태 시스템
        self.element_system = get_element_system() if callable(get_element_system) else None
        self.item_database = get_item_database() if callable(get_item_database) else None
        self.running = True
        self.character_db = CharacterDatabase()
        
        # 키보드 입력 초기화
        self.keyboard = KeyboardInput()
        
        # 게임 통계
        self.score = 0
        self.enemies_defeated = 0
        self.items_collected = 0
        self.floors_cleared = 0
        
        # 인카운터 시스템
        self.steps_since_last_encounter = 0
        self.base_encounter_rate = 0.005  # 기본 0.5%로 원복
        
        print(f"{bright_cyan('🌟 Dawn Of Stellar - 완전 통합 시스템 버전 시작! 🌟')}")
        print(f"{bright_yellow('✨ 28명 캐릭터, 165+ 상태효과, 100+ 적, 통합 사운드 시스템, 튜토리얼 시스템 활성화! ✨')}")
        
        # 🎵 시작 BGM 재생 (통합 사운드 시스템 사용)
        if self.sound_manager and hasattr(self.sound_manager, 'mixer_available') and self.sound_manager.mixer_available:
            try:
                self.sound_manager.set_floor_bgm(1)
                print("🎵 시작 BGM 재생 중...")
            except Exception as e:
                print(f"⚠️ BGM 재생 실패: {e}")
        else:
            print("🔇 사운드 매니저를 사용할 수 없습니다.")
        
        self.encounter_rate_increase = 0.01  # 걸음당 1% 증가로 원복
    
    def safe_play_bgm(self, bgm_name_or_type, **kwargs):
        """안전한 BGM 재생 헬퍼"""
        if self.sound_manager and hasattr(self.sound_manager, 'mixer_available') and self.sound_manager.mixer_available:
            try:
                self.sound_manager.play_bgm(bgm_name_or_type, **kwargs)
            except Exception as e:
                print(f"⚠️ BGM 재생 실패: {e}")
    
    def safe_play_sfx(self, sfx_name_or_type, **kwargs):
        """안전한 SFX 재생 헬퍼"""
        if self.sound_manager and hasattr(self.sound_manager, 'mixer_available') and self.sound_manager.mixer_available:
            try:
                self.sound_manager.play_sfx(sfx_name_or_type, **kwargs)
            except Exception as e:
                print(f"⚠️ SFX 재생 실패: {e}")
    
    def safe_set_floor_bgm(self, floor: int):
        """안전한 층별 BGM 설정 헬퍼"""
        if self.sound_manager and hasattr(self.sound_manager, 'set_floor_bgm'):
            try:
                self.sound_manager.set_floor_bgm(floor)
            except Exception as e:
                print(f"⚠️ 층별 BGM 설정 실패: {e}")
        
    def initialize_game(self):
        """게임 초기화"""
        # 🎵 메인 메뉴 BGM 재생
        print("🎵 메인 테마 재생 중...")
        self.safe_play_bgm("Main theme of FFVII", loop=True)
        
        self.display.show_title()
        
        # 🎵 캐릭터 선택 BGM으로 변경
        print("🎵 캐릭터 선택 음악으로 변경...")
        self.safe_play_bgm("prelude", loop=True)
        
        self.show_character_selection()
        self.apply_permanent_bonuses()  # 영구 성장 보너스 적용
        self.world.generate_level()
        
        # 🎵 게임 시작 BGM 재생
        print("🎵 던전 테마로 변경...")
        self.safe_play_bgm("dungeon_theme", loop=True)
        print("✅ 게임 초기화 완료!")
        time.sleep(1)
        
    def apply_permanent_bonuses(self):
        """영구 성장 보너스 적용"""
        for member in self.party_manager.members:
            self.meta_progression.apply_bonuses_to_character(member)
            gold_bonus = self.permanent_progression.get_passive_bonus("gold_rate")
            if gold_bonus > 0:
                bonus_gold = int(member.gold * (gold_bonus / 100))
                member.gold += bonus_gold
        
        # 시작 아이템 제공 (모험가의 준비)
        starting_items_upgrade = self.permanent_progression.upgrades.get("starting_items")
        starting_items_level = starting_items_upgrade.current_level if starting_items_upgrade else 0
        if starting_items_level > 0:
            self.give_starting_items(starting_items_level)
    
    def give_starting_items(self, level: int):
        """시작 아이템 제공"""
        db = ItemDatabase()
        
        # 레벨에 따른 시작 아이템
        starting_items = []
        if level >= 1:
            starting_items.extend(["치료 포션", "마나 포션", "화염병"])
        if level >= 2:
            starting_items.extend(["강철 검", "가죽 갑옷"])
        if level >= 3:
            starting_items.extend(["번개 구슬", "방어막 두루마리", "부활의 깃털"])
        
        # 첫 번째 파티원에게 아이템 추가
        if self.party_manager.members and starting_items:
            first_member = self.party_manager.members[0]
            for item_name in starting_items:
                item = db.get_item(item_name)
                if item:
                    success = first_member.inventory.add_item(item)
                    if not success:
                        break  # 인벤토리가 가득 차면 중단
        
    def show_character_selection(self):
        """새로운 캐릭터 생성 시스템 사용"""
        if EASY_CREATOR_AVAILABLE:
            print(f"\n{bright_cyan('🎭 새로운 캐릭터 생성 시스템', True)}")
            print("="*60)
            
            easy_creator = get_easy_character_creator()
            created_party = easy_creator.show_character_creation_menu()
            
            if created_party:
                # 생성된 파티를 게임에 적용
                self.party_manager.members = []  # 기존 파티 clear
                for character in created_party:
                    self.party_manager.add_member(character)
                
                print(f"\n{bright_green('✅ 파티 생성 완료!', True)}")
                print(f"총 {len(created_party)}명의 파티원이 준비되었습니다.")
                
                # 파티 요약 표시
                for i, member in enumerate(self.party_manager.members, 1):
                    print(f"{i}. {member.name} ({member.character_class}) - HP: {member.max_hp}")
                
                return
            else:
                print(f"{bright_yellow('파티 생성이 취소되었습니다. 기본 파티로 시작합니다.')}")
                # 기본 파티 생성으로 fallback
                self.show_character_selection_legacy()
        else:
            # Easy Creator가 없으면 기존 시스템 사용
            self.show_character_selection_legacy()
    
    def show_character_selection_legacy(self):
        """캐릭터 선택 화면 (기존 시스템)"""
        print("\n" + "="*100)
        print("캐릭터 선택 - 해금된 캐릭터 중 4명을 선택하세요")
        print("="*100)
        
        # 메타 진행 정보 표시
        try:
            stats = self.meta_progression.get_stats()
            print(f"플레이 횟수: {stats['총 플레이 횟수']} | 최고 점수: {stats['최고 점수']} | 별조각: {stats['별조각']}")
        except (AttributeError, KeyError) as e:
            print(f"진행 정보: 플레이 {self.meta_progression.data.get('total_runs', 0)}회 | "
                  f"별조각 {self.meta_progression.data.get('star_fragments', 0)}")
        print()
        
        all_characters = self.character_db.get_all_characters()
        unlocked_names = self.meta_progression.get_unlocked_characters()
        
        # 해금된 캐릭터만 필터링
        unlocked_characters = [char for char in all_characters if char['name'] in unlocked_names]
        
        # 해금된 캐릭터 목록 표시
        for i, char_data in enumerate(unlocked_characters, 1):
            upgrade_level = self.meta_progression.get_character_upgrade_level(char_data['name'])
            upgrade_str = f" (업그레이드 Lv.{upgrade_level})" if upgrade_level > 0 else ""
            
            print(f"{i:2}. {char_data['name']:12} ({char_data['class']:12}){upgrade_str} - {char_data['description']}")
            stats_str = f"    HP:{char_data['hp']:3} | P.ATK:{char_data['p_atk']:2} | M.ATK:{char_data['m_atk']:2} | "
            stats_str += f"P.DEF:{char_data['p_def']:2} | M.DEF:{char_data['m_def']:2} | SPD:{char_data['speed']:2}"
            print(stats_str)
            print(f"    특성: {', '.join(char_data['traits'])}")
            print()
            
        print("선택 옵션:")
        print(f"{len(unlocked_characters)+1}. 균형잡힌 파티 (추천)")
        print(f"{len(unlocked_characters)+2}. 랜덤 파티")
        print("0. 직접 선택")
        
        choice = get_single_key_input(f"\n👉 선택하세요 (0-{len(unlocked_characters)+2}): ")
        
        if choice == str(len(unlocked_characters)+1):
            # 균형잡힌 파티 (해금된 캐릭터 중에서)
            party_names = self.get_balanced_unlocked_party(unlocked_names)
            self.create_party_from_names(party_names)
            
        elif choice == str(len(unlocked_characters)+2):
            # 랜덤 파티 (해금된 캐릭터 중에서)
            party_names = self.get_random_unlocked_party(unlocked_names)
            self.create_party_from_names(party_names)
            
        elif choice == "0":
            # 직접 선택
            self.manual_character_selection(unlocked_characters)
            
        else:
            try:
                char_index = int(choice) - 1
                if 0 <= char_index < len(unlocked_characters):
                    # 하나 선택 후 나머지 자동
                    selected_char = unlocked_characters[char_index]
                    remaining_chars = [c for c in unlocked_characters if c != selected_char]
                    auto_selected = random.sample(remaining_chars, min(3, len(remaining_chars)))
                    
                    party_names = [selected_char["name"]] + [c["name"] for c in auto_selected]
                    # 4명이 안되면 부족한 만큼 랜덤 추가
                    while len(party_names) < 4 and len(unlocked_names) >= 4:
                        remaining_names = [name for name in unlocked_names if name not in party_names]
                        if remaining_names:
                            party_names.append(random.choice(remaining_names))
                            
                    self.create_party_from_names(party_names)
                else:
                    print("잘못된 선택입니다. 균형잡힌 파티로 시작합니다.")
                    party_names = self.get_balanced_unlocked_party(unlocked_names)
                    self.create_party_from_names(party_names)
            except ValueError:
                print("잘못된 입력입니다. 균형잡힌 파티로 시작합니다.")
                party_names = self.get_balanced_unlocked_party(unlocked_names)
                self.create_party_from_names(party_names)
                
    def get_balanced_unlocked_party(self, unlocked_names: List[str]) -> List[str]:
        """해금된 캐릭터 중 균형잡힌 파티 구성"""
        return self.character_db.get_balanced_party_from_list(unlocked_names)
        
    def get_random_unlocked_party(self, unlocked_names: List[str]) -> List[str]:
        """해금된 캐릭터 중 랜덤 파티"""
        return random.sample(unlocked_names, min(4, len(unlocked_names)))
                
    def manual_character_selection(self, unlocked_characters: List):
        """수동 캐릭터 선택 - 해금된 캐릭터만"""
        selected_indices: List[int] = []
        
        for i in range(4):
            if len(selected_indices) >= len(unlocked_characters):
                print(f"해금된 캐릭터가 부족합니다. {len(selected_indices)}명만 선택됩니다.")
                break
                
            while True:
                try:
                    print(f"\n{i+1}번째 파티 멤버를 선택하세요:")
                    
                    # 사용 가능한 캐릭터 표시
                    available_chars = [c for idx, c in enumerate(unlocked_characters) if idx not in selected_indices]
                    for j, char in enumerate(available_chars):
                        upgrade_level = self.meta_progression.get_character_upgrade_level(char['name'])
                        upgrade_str = f" (업그레이드 Lv.{upgrade_level})" if upgrade_level > 0 else ""
                        print(f"  {j+1}. {char['name']:12} ({char['class']:12}){upgrade_str}")
                    
                    choice = int(input("번호 입력: ")) - 1
                    
                    if 0 <= choice < len(available_chars):
                        # available_chars에서의 인덱스를 unlocked_characters에서의 인덱스로 변환
                        selected_char = available_chars[choice]
                        original_index = next(idx for idx, c in enumerate(unlocked_characters) if c == selected_char)
                        selected_indices.append(original_index)
                        print(f"{selected_char['name']} 선택됨!")
                        break
                    else:
                        print("잘못된 선택입니다.")
                        
                except ValueError:
                    print("숫자를 입력하세요.")
                    
        party_names = [unlocked_characters[i]["name"] for i in selected_indices]
        self.create_party_from_names(party_names)
        
    def create_auto_party(self):
        """자동 파티 생성 - 새로운 Easy Character Creator 사용"""
        # 🎵 파티 생성 화면 BGM 재생 (평화로운 테마)
        if hasattr(self, 'sound_manager') and self.sound_manager:
            self.sound_manager.play_bgm("peaceful", loop=True)
        
        if EASY_CREATOR_AVAILABLE:
            print(f"\n{bright_cyan('🎭 새로운 캐릭터 생성 시스템', True)}")
            print("="*60)
            
            easy_creator = get_easy_character_creator()
            created_party = easy_creator.show_character_creation_menu()
            
            if created_party:
                # 생성된 파티를 게임에 적용
                self.party_manager.members = []  # 기존 파티 clear
                for character in created_party:
                    self.party_manager.add_member(character)
                
                print(f"\n{bright_green('✅ 파티 생성 완료!', True)}")
                print(f"총 {len(created_party)}명의 파티원이 준비되었습니다.")
                
                # 🎵 파티 생성 완료 BGM 재생
                if hasattr(self, 'sound_manager') and self.sound_manager:
                    self.sound_manager.play_bgm("character_select", loop=True)
                
                self.keyboard.wait_for_key("🚀 아무 키나 눌러 모험을 시작하세요...")
                return
            else:
                print(f"{bright_yellow('파티 생성이 취소되었습니다. 기본 파티로 시작합니다.')}")
                # 기본 파티 생성으로 fallback
                self.create_auto_party_legacy()
        else:
            # Easy Creator가 없으면 기존 시스템 사용
            self.create_auto_party_legacy()
    
    def create_auto_party_legacy(self):
        """자동 파티 생성 (기존 시스템)"""
        # 🎵 파티 생성 화면 BGM 재생 (평화로운 테마)
        self.safe_play_bgm("peaceful", loop=True)
        
        print(f"\n{bright_cyan('🤖 자동 파티 생성 시스템', True)}")
        print("="*60)
        
        # 해금된 직업 목록과 스탯 표시
        self._show_available_classes()
        
        # 사용자 선택 캐릭터 입력받기
        print(f"\n{bright_yellow('원하는 캐릭터가 있나요? (선택사항)')}")
        print("포함시키고 싶은 캐릭터 직업을 입력하세요 (쉼표로 구분)")
        print("예: 전사, 아크메이지 또는 그냥 엔터키를 눌러 완전 자동 생성")
        
        user_input = self.keyboard.get_key().strip()
        
        user_selected = []
        if user_input:
            # 입력 파싱
            selected_classes = [cls.strip() for cls in user_input.split(',')]
            
            # 유효한 직업인지 확인
            from game.auto_party_builder import AutoPartyBuilder
            auto_builder = AutoPartyBuilder()
            for class_name in selected_classes:
                if class_name in auto_builder.ALL_CLASSES:
                    user_selected.append(class_name)
                else:
                    print(f"{yellow(f'경고: {class_name}는 유효하지 않은 직업입니다.')}")
        
        # 자동 파티 생성
        from game.auto_party_builder import AutoPartyBuilder
        auto_builder = AutoPartyBuilder()
        party_members = auto_builder.create_balanced_party(user_selected, 4)
        
        # 파티 매니저에 추가
        for character in party_members:
            self.party_manager.add_member(character)
        
        print(f"\n{bright_green('파티 생성 완료! 🎉')}")
        
        # 🎵 파티 생성 완료 BGM 재생 (캐릭터 선택 테마)
        self.safe_play_bgm("character_select", loop=True)
        
        self.keyboard.wait_for_key("🚀 아무 키나 눌러 모험을 시작하세요...")
        
        # 영구 성장 보너스만 적용 (세계 생성은 start_adventure에서)
        self.apply_permanent_bonuses()
        
        print("✅ 파티 생성 완료!")
        time.sleep(1)
    
    def create_party_from_names(self, party_names: List[str]):
        """이름 목록으로부터 파티 생성"""
        print(f"\n선택된 파티:")
        
        for name in party_names:
            char_data = self.character_db.get_character_by_name(name)
            if char_data:
                character = self.character_db.create_character_from_data(char_data)
                self.party_manager.add_member(character)
                print(f"  {character.name} ({character.character_class})")
        
        print(f"\n파티 생성 완료! 총 {len(self.party_manager.members)}명의 영웅이 준비되었습니다.")
        
        # 특성 선택 단계
        if game_config.are_all_passives_unlocked():
            print(f"\n{bright_cyan('🎯 특성 선택 단계 (개발 모드)')}")
            for member in self.party_manager.members:
                try:
                    member.select_traits("development")
                except Exception as e:
                    print(f"{RED}특성 선택 중 오류 발생: {e}{RESET}")
                    member.active_traits = []  # 빈 특성으로 초기화
        else:
            print(f"\n{bright_yellow('🔒 일반 모드: 특성 해금 시스템은 추후 업데이트 예정')}")
            for member in self.party_manager.members:
                member.active_traits = []  # 빈 특성으로 초기화
        
        self.keyboard.wait_for_key("🚀 아무 키나 눌러 모험을 시작하세요...")
        
    def create_party(self):
        """기본 파티 생성 (사용 안함 - show_character_selection으로 대체)"""
        pass
        
    def start_adventure(self):
        """모험 시작 - 간단한 게임 시작"""
        print(f"\n{bright_cyan('🌟 모험을 시작합니다!', True)}")
        
        # 세계 생성 및 초기화
        self.apply_permanent_bonuses()
        self.world.generate_level()
        
        # 🎵 층수에 맞는 BGM 재생 (던전 테마)
        print("🎵 게임 BGM을 시작합니다...")
        try:
            # 현재 층수에 따른 BGM 선택
            current_floor = getattr(self.world, 'current_level', 1)
            if current_floor <= 10:
                bgm_name = "dungeon"  # 초반 던전
            elif current_floor <= 20:
                bgm_name = "dungeon_deep"  # 깊은 던전
            else:
                bgm_name = "mysterious"  # 신비로운 던전
            
            self.safe_play_bgm(bgm_name, loop=True)
            print(f"✅ BGM 재생 중: {bgm_name}")
        except Exception as e:
            print(f"⚠️ BGM 재생 실패: {e}")
        
        print("✅ 게임 초기화 완료!")
        
        # 파티 정보 간단 표시
        print(f"\n{bright_green('=== 파티 정보 ===')}")
        for i, member in enumerate(self.party_manager.members, 1):
            print(f"{i}. {member.name} ({member.character_class}) - HP: {member.current_hp}/{member.max_hp}")
        
        print(f"\n{bright_yellow(f'현재 위치: 던전 {self.world.current_level}층')}")
        print(f"{bright_green('모험이 시작되었습니다!')}")
        print()
        print("🎮 게임 조작법:")
        print("  이동: WASD 키")
        print("  메뉴: I(인벤토리), P(파티상태), F(필드활동), C(요리)")  
        print("  기타: H(도움말), Q(종료)")
        print()
        
        # 실제 게임 루프 시작
        print(f"{bright_cyan('🎮 게임이 시작됩니다!')}")
        self.keyboard.wait_for_key("🔑 아무 키나 눌러 게임 시작...")
        
        # 메인 게임 루프 실행
        self.main_game_loop()
        
    def main_game_loop(self):
        """실제 게임 플레이 루프"""
        while self.running:
            try:
                # 게임 화면 표시
                self.display.show_game_screen(self.party_manager, self.world)
                
                # 플레이어 입력 받기
                action = self.get_player_input()
                
                # 액션 처리
                self.process_action(action)
                
                # 게임 오버 조건 체크
                if not self.party_manager.has_alive_members():
                    print(f"\n{bright_red('💀 파티가 전멸했습니다...', True)}")
                    print("게임 오버!")
                    break
                    
            except KeyboardInterrupt:
                print(f"\n{bright_yellow('게임을 중단합니다.')}")
                break
        
        print(f"\n{bright_cyan('게임이 종료되었습니다.')}")
        input("아무 키나 눌러 메인 메뉴로 돌아가기...")
        
    def main_loop(self):
        """메인 게임 루프 - 고급 시스템 통합"""
        # 🎮 게임 매니저 상태를 메뉴로 시작
        self.game_manager.change_state(GameState.MENU)
        
        # 🔄 메인 루프
        while self.running:
            try:
                # ⏱️ 프레임 타이밍
                frame_start = time.time()
                
                # 🎮 게임 매니저 업데이트
                self.game_manager.update(0.016)  # 약 60 FPS
                
                # 🎮 현재 상태에 따른 처리
                if self.game_manager.current_state == GameState.MENU:
                    self._handle_menu_state()
                elif self.game_manager.current_state == GameState.PLAYING:
                    self._handle_playing_state()
                elif self.game_manager.current_state == GameState.PAUSED:
                    self._handle_paused_state()
                elif self.game_manager.current_state == GameState.GAME_OVER:
                    self._handle_game_over_state()
                    break
                
                # 🎯 간단한 프레임 제한
                frame_time = time.time() - frame_start
                if frame_time < 0.016:  # 60 FPS 제한
                    time.sleep(0.016 - frame_time)
                
            except KeyboardInterrupt:
                self.quit_game()
    
    def _handle_menu_state(self):
        """메뉴 상태 처리"""
        self.display.show_main_menu()
        print(f"\n{Color.BRIGHT_CYAN.value}🌟 Dawn Of Stellar - 고급 시스템 버전 🌟{Color.RESET.value}")
        print(f"{Color.BRIGHT_YELLOW.value}✨ 향상된 사운드, AI, UI, 밸런스 시스템이 활성화되었습니다! ✨{Color.RESET.value}")
        print("\n🎮 명령:")
        print("  [Enter] 게임 시작")
        print("  [A] 업적 보기")
        print("  [S] 설정")
        print("  [Q] 종료")
        
        key = self.keyboard.get_key()
        
        if key == '\r' or key == '\n':  # Enter
            if not self.party_manager.has_members():
                self.show_character_selection()
            self.game_manager.change_state(GameState.PLAYING)
        elif key.lower() == 'a':
            self.game_manager.change_state(GameState.ACHIEVEMENTS)
            self._show_achievements()
        elif key.lower() == 's':
            self.game_manager.change_state(GameState.SETTINGS)
            self._show_settings()
        elif key.lower() == 'q':
            self.quit_game()
    
    def _handle_playing_state(self):
        """게임 플레이 상태 처리"""
        # 🔍 시야 시스템 업데이트
        self.world.update_visibility()
        
        self.display.show_game_screen(self.party_manager, self.world)
        action = self.get_player_input()
        self.process_action(action)
    
    def _handle_paused_state(self):
        """일시정지 상태 처리"""
        print(f"\n{Color.BRIGHT_YELLOW.value}⏸️  게임 일시정지 ⏸️{Color.RESET.value}")
        print("🎮 명령:")
        print("  [Enter] 게임 재개")
        print("  [M] 메인 메뉴로")
        print("  [S] 설정")
        
        key = self.keyboard.get_key()
        
        if key == '\r' or key == '\n':
            self.game_manager.change_state(GameState.PLAYING)
        elif key.lower() == 'm':
            self.game_manager.change_state(GameState.MENU)
        elif key.lower() == 's':
            self.game_manager.change_state(GameState.SETTINGS)
            self._show_settings()
    
    def _handle_game_over_state(self):
        """게임 오버 상태 처리"""
        print(f"\n{Color.BRIGHT_RED.value}💀 게임 오버 💀{Color.RESET.value}")
        
        # 🏆 최종 통계 표시
        stats = self.game_manager.get_current_stats()
        print(f"\n📊 최종 결과:")
        print(f"  🗡️  처치한 적: {self.enemies_defeated}")
        print(f"  🏢 도달한 층: {self.world.current_level}")
        print(f"  ⏰ 플레이 시간: {stats['game_data']['play_time']:.1f}초")
        print(f"  🏆 해금된 업적: {stats['achievements_unlocked']}")
        
        # 🌟 메타 진행 기록
        victory = False  # 게임 오버이므로 승리 아님
        rewards = self.meta_progression.record_game_end(
            score=self.score,
            enemies_defeated=self.enemies_defeated,
            items_collected=self.items_collected,
            floors_cleared=self.world.current_level,
            victory=victory
        )
        
        # 💰 획득한 별조각 표시
        if rewards["star_fragments"] > 0:
            print(f"\n✨ 별조각 {rewards['star_fragments']}개 획득!")
        
        # 🔓 새로 해금된 직업 표시
        if rewards["unlocked_classes"]:
            print(f"🔓 새로운 직업 해금: {', '.join(rewards['unlocked_classes'])}")
        
        # 🏆 새로운 업적 표시
        if rewards["achievements"]:
            print(f"🏆 업적 달성: {', '.join(rewards['achievements'])}")
        
        # 💾 진행도 자동 저장
        self.game_manager.progression_system.save_progress()
        
        # 🎯 적응형 밸런스 데이터 저장
        if hasattr(self, 'adaptive_balance') and self.adaptive_balance:
            self.adaptive_balance.save_balance_data()
        
        print(f"\n{Color.BRIGHT_CYAN.value}진행도가 저장되었습니다!{Color.RESET.value}")
        print("아무 키나 누르면 메인 메뉴로 돌아갑니다...")
        
        self.keyboard.get_key()
        self.game_manager.change_state(GameState.MENU)
    
    def _show_achievements(self):
        """업적 화면 표시"""
        print(f"\n{Color.BRIGHT_YELLOW.value}🏆 업적 시스템 🏆{Color.RESET.value}")
        
        unlocked = self.game_manager.progression_system.unlocked_achievements
        total = len(self.game_manager.progression_system.achievements)
        
        print(f"달성률: {len(unlocked)}/{total} ({len(unlocked)/total*100:.1f}%)")
        print("\n📋 주요 업적:")
        
        # 상위 5개 업적만 표시
        for i, (aid, achievement) in enumerate(list(self.game_manager.progression_system.achievements.items())[:5]):
            status = "✅" if achievement.is_unlocked else "⏳"
            progress = self.game_manager.progression_system.get_achievement_progress(aid)
            
            if achievement.is_unlocked:
                print(f"  {status} {achievement.name}: {achievement.description}")
            else:
                # 진행도 표시
                progress_text = ""
                if progress:
                    prog_values = list(progress.values())
                    if prog_values:
                        avg_progress = sum(prog_values) / len(prog_values)
                        progress_text = f" ({avg_progress:.1%})"
                
                print(f"  {status} {achievement.name}: {achievement.description}{progress_text}")
        
        print("\n[ESC] 돌아가기")
        self.keyboard.get_key()
        self.game_manager.change_state(GameState.MENU)
    
    def _show_settings(self):
        """설정 화면 표시"""
        print(f"\n{Color.BRIGHT_BLUE.value}⚙️ 게임 설정 ⚙️{Color.RESET.value}")
        
        settings = self.game_manager.settings
        print("\n🔊 오디오 설정:")
        print(f"  마스터 볼륨: {int(float(str(settings['master_volume'])) * 100)}%")
        print(f"  효과음 볼륨: {int(float(str(settings['sfx_volume'])) * 100)}%")
        print(f"  배경음 볼륨: {int(float(str(settings['bgm_volume'])) * 100)}%")
        
        print("\n🎮 게임플레이 설정:")
        print(f"  자동 난이도 조절: {'활성화' if settings['difficulty_auto_adjust'] else '비활성화'}")
        print(f"  UI 애니메이션: {'활성화' if settings['ui_animations'] else '비활성화'}")
        print(f"  파티클 효과: {'활성화' if settings['particle_effects'] else '비활성화'}")
        
        print(f"\n⚖️ 현재 난이도: {self.game_manager.balance_system.current_difficulty.value}")
        
        print("\n[ESC] 돌아가기")
        self.keyboard.get_key()
        self.game_manager.change_state(self.game_manager.previous_state or GameState.MENU)
                
    def get_player_input(self) -> str:
        """플레이어 입력 받기 (키 하나만)"""
        print("\n🎮 명령: (WASD)이동 (I)인벤토리 (P)파티상태 (F)필드활동 (C)요리 (E)모험종료")
        print("   📁 (1)저장 (2)불러오기 (Q)저장&종료 (H)도움말")
        print("👉 ", end='', flush=True)
        
        key = self.keyboard.get_key()
        print(key.upper())  # 입력한 키 표시
        
        # 키 매핑
        key_map = {
            'w': 'w', 's': 's', 'a': 'a', 'd': 'd',  # 이동
            'i': 'i', 'p': 'p', 'f': 'f', 'c': 'c', 'e': 'quit', 'h': 'h',  # 메뉴
            '1': 'save', '2': 'load', 'q': 'save_and_quit',  # 저장/불러오기
            '\x1b': 'quit',  # ESC키도 모험종료로
            '\r': '',     # Enter는 무시
            '\n': '',     # 줄바꿈 무시
        }
        
        return key_map.get(key, key)
        
    def process_action(self, action: str):
        """액션 처리"""
        if action == 'quit':
            self.quit_game()
        elif action == 'save_and_quit':
            self.save_and_quit()
        elif action in ['w', 'a', 's', 'd']:
            self.move_party(action)
        elif action == 'i':
            self.show_inventory()
        elif action == 'u':
            self.show_field_item_menu()
        elif action == 'p':
            self.show_party_status()
        elif action == 'f':
            self.show_field_skill_menu()
        elif action == 'c':
            self.show_cooking_menu()
        elif action == 'save':
            self.save_game()
        elif action == 'load':
            self.load_game()
        elif action == 'h':
            show_help()
        elif action == 'test':
            self.test_combat()
        elif action == '':
            # 빈 입력 (Enter, 줄바꿈 등) 무시
            pass
        else:
            if action:  # 빈 문자열이 아닌 경우만 메시지 출력
                print(f"잘못된 선택입니다: '{action}'")
                print("도움말을 보려면 'H'를 누르세요.")
                self.safe_play_sfx("menu_error")
    
    def show_cooking_menu(self):
        """요리 메뉴 표시"""
        from game.field_cooking import get_field_cooking_interface
        field_cooking = get_field_cooking_interface(self.party_manager)
        field_cooking.show_cooking_menu()
    
    def _handle_ingredient_drops(self, enemies):
        """적 처치 시 식재료 드롭 처리 (개선된 시스템)"""
        from game.field_cooking import handle_enemy_defeat
        
        for enemy in enemies:
            enemy_name = getattr(enemy, 'name', '알 수 없는 적')
            enemy_level = getattr(enemy, 'level', 1)
            
            # 개선된 적별 특정 드롭 시스템 사용
            dropped_ingredients = handle_enemy_defeat(enemy_name, enemy_level)
            
            if dropped_ingredients:
                print(f"\n💀 {enemy_name} 처치로 인한 식재료 획득:")
                for ingredient in dropped_ingredients:
                    print(f"   📦 {ingredient}")
                    
                # 식재료 획득 효과음
                try:
                    self.safe_play_sfx("item_pickup")
                except:
                    pass
    
    def _update_cooking_buffs(self):
        """요리 버프 업데이트"""
        from game.field_cooking import update_cooking_buffs_on_step, get_cooking_effects_for_party, apply_cooking_effects_to_character
        
        # 걸음마다 버프 지속시간 감소
        update_cooking_buffs_on_step()
        
        # 현재 활성화된 요리 효과를 파티원들에게 적용
        cooking_effects = get_cooking_effects_for_party()
        if cooking_effects:
            for member in self.party_manager.get_alive_members():
                # 지속 회복 효과 등을 적용
                apply_cooking_effects_to_character(member, cooking_effects)
            
    def move_party(self, direction: str):
        """파티 이동"""
        directions = {'w': (0, -1), 's': (0, 1), 'a': (-1, 0), 'd': (1, 0)}
        dx, dy = directions[direction]
        
        if self.world.can_move(dx, dy):
            result = self.world.move_player(dx, dy)
            
            # � 걸음 수 증가
            self.party_manager.add_step()
            
            # �👥 적들의 이동 처리 (플레이어 이동 후)
            self.world.move_enemies()
            
            # 걸음 회복 시스템 (모든 파티원)
            for member in self.party_manager.members:
                if member.is_alive:
                    member.on_step_taken()
            
            # 채집 쿨다운 알림 확인
            try:
                from game.gathering_limiter import check_gathering_cooldown_notification
                check_gathering_cooldown_notification()
            except ImportError:
                pass
            
            # 패시브 효과 업데이트
            self.update_passive_effects()
            
            # 🍳 요리 버프 업데이트
            self._update_cooking_buffs()
            
            # 턴 기반 효과 적용 (일정 걸음마다)
            if self.steps_since_last_encounter % 5 == 0:  # 5걸음마다
                self.apply_turn_based_effects()
            
            # 이동 결과 처리
            if result == "combat":
                # 적이 있는 위치 계산 (플레이어가 이동하려던 위치)
                enemy_pos = (self.world.player_pos[0] + dx, self.world.player_pos[1] + dy)
                # 실제 적과 충돌한 경우만 전투 시작
                self.start_combat(enemy_pos)
                # 전투 후 인카운터 리셋
                self.steps_since_last_encounter = 0
            elif result == "next_floor":
                # 다음 층 이동
                self.move_to_next_floor()
            elif result:  # 아이템 획득
                # 첫 번째 살아있는 파티원에게 아이템 추가
                alive_members = self.party_manager.get_alive_members()
                if alive_members and hasattr(result, 'name'):  # result가 아이템인지 확인
                    target_member = alive_members[0]  # 첫 번째 멤버에게 추가
                    if target_member.inventory.add_item(result):
                        print(f"💰 {target_member.name}이(가) {result.get_colored_name()}을(를) 획득했습니다!")
                        # 아이템 희귀도별 효과음
                        rarity = getattr(result, 'rarity', None)
                        if rarity and rarity.name in ["유니크", "레전더리"]:
                            self.safe_play_sfx("winning_prize")  # 특별한 아이템
                        elif rarity and rarity.name in ["레어", "에픽"]:
                            self.safe_play_sfx("treasure_open")  # 좋은 아이템
                        else:
                            self.safe_play_sfx("item_pickup")  # 일반 아이템
                        self.items_collected += 1
                        
                        # 아이템 획득 메시지를 천천히 보여주기
                        self.keyboard.wait_for_key("🔑 아무 키나 눌러 계속...")
                    else:
                        print(f"⚠️ {target_member.name}의 인벤토리가 가득 찼습니다!")
                        # 인벤토리 가득함 효과음
                        self.safe_play_sfx("menu_error")
                        self.keyboard.wait_for_key("🔑 아무 키나 눌러 계속...")
                pass
            else:
                # 일반 이동 - 랜덤 인카운터 체크
                self.check_random_encounter()
        else:
            print("그 방향으로는 갈 수 없습니다.")
    
    def check_random_encounter(self):
        """확장된 랜덤 조우 시스템 - 전투뿐만 아니라 다양한 이벤트 (쿨타임 강화)"""
        self.steps_since_last_encounter += 1
        
        # 요리 버프 업데이트
        self._update_cooking_buffs()
        
        # 필드 식재료 발견 체크 (5% 확률)
        if random.random() < 0.05:
            from game.field_cooking import handle_field_ingredient_find
            handle_field_ingredient_find()
        
        # 최소 걸음 수 제한 (50걸음 이하에서는 조우 발생 안함)
        if self.steps_since_last_encounter < 50:
            return
        
        # 현재 인카운터 확률 계산 (기존 방식)
        current_rate = self.base_encounter_rate + (self.steps_since_last_encounter * self.encounter_rate_increase)
        current_rate = min(current_rate, 0.3)  # 최대 30%로 원복
        
        # 걸음 수 증가 (50걸음마다 정보 표시)
        if self.steps_since_last_encounter % 50 == 0:
            print(f"🚶 {self.steps_since_last_encounter}걸음 | 인카운터 확률: {current_rate:.1%}")
        
        # 랜덤 조우 발생 체크
        if random.random() < current_rate:
            print(f"\n✨ {self.steps_since_last_encounter}걸음 후 무언가를 발견했습니다!")
            
            # 첫 번째 딜레이 - 조우 발견 메시지 확인
            time.sleep(1.0)
            print("🔍 자세히 살펴보고 있습니다...")
            time.sleep(0.8)
            self.keyboard.wait_for_key("🔑 계속하려면 아무 키나 누르세요...")
            
            # 60% 전투, 25% 랜덤 조우, 15% 채집지 발견
            encounter_roll = random.random()
            if encounter_roll < 0.6:
                # 기존 전투 시스템
                print("💥 적과 마주쳤습니다!")
                time.sleep(0.5)
                self.keyboard.wait_for_key("⚔️ 전투 준비! 아무 키나 누르세요...")
                self.start_combat()
            elif encounter_roll < 0.85:
                # 새로운 랜덤 조우 시스템
                time.sleep(0.5)
                self.keyboard.wait_for_key("🎲 특별한 조우가 시작됩니다! 아무 키나 누르세요...")
                self.trigger_random_encounter()
            else:
                # 채집지 발견
                time.sleep(0.5)
                self.keyboard.wait_for_key("🌍 채집지를 발견했습니다! 아무 키나 누르세요...")
                self._trigger_gathering_encounter()
            
            # 조우 발생 후 쿨타임 (20걸음)
            self.steps_since_last_encounter = -20
    
    def _trigger_gathering_encounter(self):
        """채집지 발견 인카운터"""
        try:
            from game.field_cooking import handle_gathering_encounter
            handle_gathering_encounter()
        except ImportError:
            print("🌿 신비한 식물들이 자라는 곳을 발견했지만 채집 도구가 없습니다...")
    
    def trigger_random_encounter(self):
        """랜덤 조우 발생 처리"""
        try:
            # 현재 파티 멤버들 가져오기
            party_members = self.party_manager.get_alive_members()
            current_floor = self.world.current_level
            
            # 전투 확률 체크 (30%)
            if random.random() < self.encounter_manager.get_combat_chance():
                # 전투 발생
                print("💥 적과 마주쳤습니다!")
                time.sleep(0.5)
                self.keyboard.wait_for_key("⚔️ 전투가 불가피합니다! 아무 키나 누르세요...")
                self.start_combat()
                return
            
            # 랜덤 조우 실행
            result = self.encounter_manager.trigger_random_encounter(party_members, current_floor)
            
            if result and result.get("success"):
                # 조우 메시지 표시
                print(f"\n{result['message']}")
                
                # 조우 정보 확인을 위한 첫 번째 대기
                time.sleep(1.2)
                self.keyboard.wait_for_key("📖 상황을 파악했습니다. 계속하려면 아무 키나 누르세요...")
                
                # 조우 효과 처리
                self.handle_encounter_effects(result, party_members)
                
                # 최종 확인 대기
                time.sleep(0.8)
                self.keyboard.wait_for_key("✅ 조우가 완료되었습니다. 계속하려면 아무 키나 누르세요...")
            else:
                # 조우 실패 시 기본 전투
                print("💥 결국 적과 마주쳤습니다!")
                time.sleep(0.5)
                self.keyboard.wait_for_key("⚔️ 전투가 불가피합니다! 아무 키나 누르세요...")
                self.start_combat()
                
        except Exception as e:
            print(f"⚠️ 랜덤 조우 처리 중 오류: {e}")
            time.sleep(0.5)
            self.keyboard.wait_for_key("🔧 오류가 발생했습니다. 계속하려면 아무 키나 누르세요...")
            # 오류 시 기본 전투로 대체
            self.start_combat()
    
    def handle_encounter_effects(self, result: Dict[str, Any], party_members: List):
        """조우 효과 처리"""
        effect = result.get("effect")
        effect_value = result.get("effect_value")  # effect_value 추출
        
        if not effect:
            return
            
        # 골드 획득
        if "gold" in result:
            gold_amount = result["gold"]
            self.party_manager.add_shared_gold(gold_amount)
            self.sound_manager.play_sfx("item_pickup")
            time.sleep(0.5)
            self.keyboard.wait_for_key(f"💰 {gold_amount} 골드를 획득했습니다! 계속하려면 아무 키나 누르세요...")
        
        # 아이템 획득
        if "item" in result:
            item_name = result["item"]
            # 아이템 데이터베이스에서 실제 아이템 생성
            try:
                db = ItemDatabase()
                item = db.get_item(item_name) or db.get_random_item_by_stage(self.world.current_level)
                if item and party_members:
                    if party_members[0].inventory.add_item(item):
                        print(f"🎁 {item.get_colored_name()}을(를) 획득했습니다!")
                        self.sound_manager.play_sfx("treasure_open")
                        # 아이템 획득 메시지 확인 대기
                        time.sleep(1.0)
                        self.keyboard.wait_for_key("🎯 아이템을 자세히 살펴보세요. 계속하려면 아무 키나 누르세요...")
                        
                        # 아이템 정보 표시
                        if hasattr(item, 'description') and item.description:
                            print(f"📝 {item.description}")
                            time.sleep(0.8)
                            self.keyboard.wait_for_key("📚 아이템 정보를 확인했습니다. 계속하려면 아무 키나 누르세요...")
                    else:
                        print("⚠️ 인벤토리가 가득 찼습니다!")
                        time.sleep(0.8)
                        self.keyboard.wait_for_key("📦 인벤토리 공간이 부족합니다. 계속하려면 아무 키나 누르세요...")
            except Exception as e:
                print(f"아이템 생성 중 오류: {e}")
                time.sleep(0.5)
                self.keyboard.wait_for_key("🔧 아이템 처리 중 문제가 발생했습니다. 계속하려면 아무 키나 누르세요...")
        
        # 효과별 처리
        if effect == "open_shop":
            time.sleep(0.5)
            self.keyboard.wait_for_key("🏪 상인이 나타났습니다! 거래를 시작하려면 아무 키나 누르세요...")
            self.open_random_merchant()
        elif effect == "elite_encounter":
            print("🔥 강력한 적이 나타났습니다!")
            time.sleep(1.0)
            self.keyboard.wait_for_key("💀 엘리트 몬스터입니다! 준비하세요. 계속하려면 아무 키나 누르세요...")
            self.start_elite_combat()
        elif effect == "map_reveal":
            self.reveal_map_area()
            self.sound_manager.play_sfx("magic_cast")
            time.sleep(0.8)
            self.keyboard.wait_for_key("🗺️ 주변 지역이 밝혀졌습니다! 계속하려면 아무 키나 누르세요...")
        elif effect == "mp_restore":
            self.restore_party_mp()
            self.sound_manager.play_sfx("heal")
            time.sleep(0.8)
            self.keyboard.wait_for_key("💙 마나가 회복되었습니다! 계속하려면 아무 키나 누르세요...")
        elif effect == "hp_restore":
            self.restore_party_hp()
            self.sound_manager.play_sfx("heal")
            time.sleep(0.8)
            self.keyboard.wait_for_key("❤️ 체력이 회복되었습니다! 계속하려면 아무 키나 누르세요...")
        elif effect == "portal_choice":
            time.sleep(0.5)
            self.keyboard.wait_for_key("🌀 신비한 포털을 발견했습니다! 선택하려면 아무 키나 누르세요...")
            self.handle_portal_choice()
        elif effect == "teleport_option":
            time.sleep(0.5)
            self.keyboard.wait_for_key("✨ 순간이동의 기회입니다! 선택하려면 아무 키나 누르세요...")
            self.handle_teleport_option()
        elif effect in ["blessing", "divine_blessing"]:
            self.apply_party_blessing()
            self.sound_manager.play_sfx("heal")
            time.sleep(1.0)
            self.keyboard.wait_for_key("🙏 신성한 축복을 받았습니다! 계속하려면 아무 키나 누르세요...")
        elif effect == "ambush_battle":
            print("💀 매복에 당했습니다! 불리한 전투가 시작됩니다!")
            time.sleep(1.0)
            self.keyboard.wait_for_key("⚠️ 매복 상황입니다! 전투 준비하세요. 계속하려면 아무 키나 누르세요...")
            self.start_ambush_combat()
        else:
            # 기타 효과들은 일시적 버프로 처리 (effect_value 포함)
            self.apply_temporary_effect(effect, party_members, effect_value)
            time.sleep(0.8)
            self.keyboard.wait_for_key("✨ 특별한 효과가 적용되었습니다! 계속하려면 아무 키나 누르세요...")
    
    def open_random_merchant(self):
        """랜덤 상인 조우 처리"""
        try:
            # 임시 상인 생성
            merchant = self.merchant_manager.create_floor_merchant(self.world.current_level)
            if merchant:
                print(f"💰 {merchant.name}과 거래를 시작합니다!")
                self.show_merchant_interface(merchant)
            else:
                print("상인이 갑자기 사라져버렸습니다...")
        except Exception as e:
            print(f"상인 조우 처리 중 오류: {e}")
    
    def start_elite_combat(self):
        """엘리트 전투 시작 (더 강한 적)"""
        # 기존 전투보다 강한 적 생성
        enemies = self.create_enemies()
        # 엘리트 보정 적용 (HP와 공격력 1.5배)
        for enemy in enemies:
            enemy.max_hp = int(enemy.max_hp * 1.5)
            enemy.current_hp = enemy.max_hp
            enemy.physical_attack = int(enemy.physical_attack * 1.3)
            enemy.physical_defense = int(enemy.physical_defense * 1.2)
        
        self.sound_manager.play_sfx("battle_start")
        print("🔥 엘리트 전투가 시작됩니다!")
        
        # 전투 시작 전 추가 대기
        time.sleep(1.0)
        self.keyboard.wait_for_key("⚔️ 강력한 적과의 전투입니다! 준비되면 아무 키나 누르세요...")
        
        # 일반 전투와 동일하게 처리하되 더 좋은 보상
        party_members = self.party_manager.get_alive_members()
        result = self.combat_manager.start_combat(party_members, enemies)
        
        if result:  # 승리 시 추가 보상
            print("🏆 엘리트 전투 승리! 특별한 보상을 받았습니다!")
            time.sleep(1.0)
            self.keyboard.wait_for_key("🎉 엘리트 몬스터를 처치했습니다! 보상을 확인하세요...")
            
            # 추가 경험치
            bonus_exp = self.world.current_level * 50
            for member in party_members:
                if hasattr(member, 'experience'):
                    member.experience += bonus_exp
                    print(f"  {member.name}: 보너스 +{bonus_exp} EXP")
            
            # 추가 골드
            bonus_gold = random.randint(100, 300) * self.world.current_level
            self.party_manager.add_shared_gold(bonus_gold)
            print(f"💰 보너스 골드 {bonus_gold}G 획득!")
            
            time.sleep(1.0)
            self.keyboard.wait_for_key("💎 엘리트 보상을 모두 받았습니다! 계속하려면 아무 키나 누르세요...")
    
    def start_ambush_combat(self):
        """매복 전투 (불리한 조건)"""
        enemies = self.create_enemies()
        party_members = self.party_manager.get_alive_members()
        
        # 매복 페널티: 파티원들의 첫 턴 스킵
        print("⚠️ 매복당해서 첫 턴을 잃습니다!")
        
        # 매복 상황 설명을 위한 추가 대기
        time.sleep(1.0)
        self.keyboard.wait_for_key("💀 불리한 상황입니다! 전투를 시작하려면 아무 키나 누르세요...")
        
        self.sound_manager.play_sfx("battle_start")
        result = self.combat_manager.start_combat(party_members, enemies, ambush=True)
        
        # 일반 전투와 동일한 후처리
        if result:
            print("🎉 매복에도 불구하고 승리했습니다!")
            time.sleep(0.8)
            self.keyboard.wait_for_key("🏆 역경을 이겨냈습니다! 계속하려면 아무 키나 누르세요...")
        else:
            print("💀 매복당해 패배했습니다...")
            time.sleep(1.0)
            self.keyboard.wait_for_key("😵 전투에서 패배했습니다. 계속하려면 아무 키나 누르세요...")
    
    def reveal_map_area(self):
        """맵 일부 공개"""
        # 현재 위치 주변 넓은 범위를 탐색한 것으로 처리
        px, py = self.world.player_pos
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                x, y = px + dx, py + dy
                if self.world.is_valid_pos(x, y):
                    self.world.tiles[y][x].explored = True
                    # 시야 범위도 확장
                    if abs(dx) <= 3 and abs(dy) <= 3:
                        self.world.tiles[y][x].visible = True
        
        print("🗺️ 주변 지역의 지도가 머릿속에 떠올랐습니다!")
    
    def restore_party_mp(self):
        """파티 MP 회복"""
        for member in self.party_manager.members:
            if member.is_alive:
                restore_amount = int(member.max_mp * 0.5)  # 50% 회복
                member.current_mp = min(member.max_mp, member.current_mp + restore_amount)
                print(f"💙 {member.name}의 MP가 {restore_amount} 회복되었습니다!")
    
    def restore_party_hp(self):
        """파티 HP 회복"""
        for member in self.party_manager.members:
            if member.is_alive:
                restore_amount = int(member.max_hp * 0.3)  # 30% 회복
                member.current_hp = min(member.limited_max_hp, member.current_hp + restore_amount)
                print(f"❤️ {member.name}의 HP가 {restore_amount} 회복되었습니다!")
    
    def handle_portal_choice(self):
        """포털 선택 처리"""
        print("\n🌀 포털에 들어가시겠습니까?")
        print("1. 들어간다 (위험하지만 보상이 클 수 있음)")
        print("2. 무시한다")
        
        choice = input("선택: ").strip()
        
        if choice == "1":
            portal_outcomes = [
                ("상층 포털", "한 층 위로 이동했습니다!", "floor_up"),
                ("보물방 포털", "숨겨진 보물방을 발견했습니다!", "treasure_room"),
                ("위험한 포털", "위험한 곳으로 떨어졌습니다!", "danger_room"),
                ("원점 포털", "제자리로 돌아왔습니다.", "nothing")
            ]
            
            outcome = random.choice(portal_outcomes)
            print(f"✨ {outcome[1]}")
            
            if outcome[2] == "floor_up":
                self.move_to_next_floor()
            elif outcome[2] == "treasure_room":
                self.enter_treasure_room()
            elif outcome[2] == "danger_room":
                print("💀 강적들이 나타났습니다!")
                self.start_elite_combat()
        else:
            print("포털을 무시하고 지나갔습니다.")
    
    def handle_teleport_option(self):
        """텔레포트 옵션 처리"""
        print("\n✨ 어디로 이동하시겠습니까?")
        print("1. 계단 근처로")
        print("2. 안전한 곳으로") 
        print("3. 취소")
        
        choice = input("선택: ").strip()
        
        if choice == "1":
            # 계단 위치 찾기
            stairs_pos = None
            for y in range(self.world.height):
                for x in range(self.world.width):
                    if (self.world.tiles[y][x].type.name == "STAIRS_DOWN" if hasattr(self.world.tiles[y][x].type, 'name') else False):
                        stairs_pos = (x, y)
                        break
                if stairs_pos:
                    break
            
            if stairs_pos:
                self.world.player_pos = stairs_pos
                print("⚡ 계단 근처로 순간이동했습니다!")
                self.sound_manager.play_sfx("teleport")
            else:
                print("계단을 찾을 수 없습니다.")
                
        elif choice == "2":
            # 안전한 위치 (적이 없는 곳)로 이동
            safe_positions = []
            for y in range(1, self.world.height-1):
                for x in range(1, self.world.width-1):
                    if (self.world.tiles[y][x].is_walkable() and 
                        (x, y) not in self.world.enemies_positions):
                        safe_positions.append((x, y))
            
            if safe_positions:
                new_pos = random.choice(safe_positions)
                self.world.player_pos = new_pos
                print("⚡ 안전한 곳으로 순간이동했습니다!")
                self.sound_manager.play_sfx("teleport")
            else:
                print("안전한 곳을 찾을 수 없습니다.")
        
        if choice in ["1", "2"]:
            self.world.update_visibility()
    
    def apply_party_blessing(self):
        """파티 축복 효과"""
        print("🙏 신성한 축복이 파티를 감쌉니다!")
        for member in self.party_manager.members:
            if member.is_alive:
                # 임시 스탯 증가 (게임 세션 동안 유지)
                if not hasattr(member, 'blessing_bonus'):
                    member.blessing_bonus = True
                    member.physical_attack += 5
                    member.physical_defense += 5
                    member.magic_attack += 5
                    member.magic_defense += 5
                    print(f"✨ {member.name}이 축복을 받았습니다! (모든 스탯 +5)")
    
    def apply_temporary_effect(self, effect: str, party_members: List, effect_value: int = None):
        """임시 효과 적용"""
        effect_messages = {
            "exp_bonus": "🎓 지혜의 가호로 다음 전투에서 경험치가 증가합니다!",
            "attack_boost": "⚔️ 힘의 가호로 공격력이 일시적으로 증가했습니다!",
            "luck_boost": "🍀 행운의 가호로 좋은 일이 일어날 확률이 증가했습니다!",
            "magic_boost": "🔮 마법력이 일시적으로 증가했습니다!",
            "stealth_mode": "👤 은신 상태가 되어 적과 마주칠 확률이 감소합니다!",
            "unlock_bonus": "🔓 자물쇠 해제 능력이 향상되었습니다!",
            "time_slow": "⏰ 시간 감각이 예민해져 전투에서 유리해집니다!",
            "trap_immunity": "🛡️ 함정에 대한 저항력이 생겼습니다!",
            # 원소 강화 효과들
            "element_boost_화염": "🔥 화염 원소의 힘으로 화염 공격력이 증가했습니다!",
            "element_boost_빙결": "❄️ 빙결 원소의 힘으로 얼음 공격력이 증가했습니다!",
            "element_boost_번개": "⚡ 번개 원소의 힘으로 전기 공격력이 증가했습니다!",
            "element_boost_대지": "🌍 대지 원소의 힘으로 땅 공격력이 증가했습니다!",
            "element_boost_바람": "💨 바람 원소의 힘으로 풍속성 공격력이 증가했습니다!",
            "element_boost_물": "🌊 물 원소의 힘으로 수속성 공격력이 증가했습니다!",
            "element_boost_빛": "✨ 빛 원소의 힘으로 신성 공격력이 증가했습니다!",
            "element_boost_어둠": "🌑 어둠 원소의 힘으로 암흑 공격력이 증가했습니다!",
            "element_boost_독": "☠️ 독 원소의 힘으로 독성 공격력이 증가했습니다!",
        }
        
        message = effect_messages.get(effect, f"✨ 알 수 없는 효과: {effect}")
        print(message)
        
        # 원소 강화 효과 적용
        if effect.startswith("element_boost_"):
            element = effect.replace("element_boost_", "")
            # effect_value로부터 강화량 추출 (기본값 20%)
            boost_amount = effect_value if effect_value and isinstance(effect_value, (int, float)) else 20
            
            for member in party_members:
                if not hasattr(member, 'elemental_bonus'):
                    member.elemental_bonus = {}
                member.elemental_bonus[element] = boost_amount
                print(f"   ⬆️ {member.name}의 {element} 속성 공격력 +{boost_amount}%")
        
        # 임시 효과를 파티매니저나 월드에 저장하여 나중에 활용
        if not hasattr(self, 'temporary_effects'):
            self.temporary_effects = {}
        
        self.temporary_effects[effect] = {
            'duration': 10,  # 10턴 지속
            'applied_turn': getattr(self, 'current_turn', 0)
        }
    
    def enter_treasure_room(self):
        """보물방 입장"""
        print("🏛️ 숨겨진 보물방에 들어왔습니다!")
        
        # 여러 보물 생성
        num_treasures = random.randint(2, 4)
        total_gold = 0
        
        for i in range(num_treasures):
            if random.random() < 0.7:  # 70% 확률로 골드
                gold = random.randint(100, 500) * self.world.current_level
                total_gold += gold
            else:  # 30% 확률로 아이템
                try:
                    db = ItemDatabase()
                    item = db.get_random_item_by_stage(self.world.current_level + 2)  # 좀 더 좋은 아이템
                    if item and self.party_manager.members:
                        first_member = self.party_manager.members[0]
                        if first_member.inventory.add_item(item):
                            print(f"🎁 {item.get_colored_name()}을(를) 발견했습니다!")
                            print("🔑 아무 키나 눌러 계속...")
                            self.keyboard.get_key()
                        else:
                            print("⚠️ 인벤토리가 가득 차서 아이템을 가져갈 수 없습니다!")
                            print("🔑 아무 키나 눌러 계속...")
                            self.keyboard.get_key()
                except Exception as e:
                    print(f"보물 생성 중 오류: {e}")
        
        if total_gold > 0:
            self.party_manager.add_shared_gold(total_gold)
            print(f"💰 총 {total_gold} 골드를 발견했습니다!")
        
        self.sound_manager.play_sfx("winning_prize")
            
    def show_inventory(self):
        """인벤토리 표시 및 관리 (색상 및 무게 시스템 포함)"""
        while True:
            print("\n" + "="*60)
            print(bright_cyan("📦 파티 인벤토리", True))
            print("="*60)
            
            # 무게 및 골드 정보 표시 (정렬된 형태)
            total_weight = 0.0
            max_weight = 0.0
            
            print(f"\n{bright_white('파티원 상태:', True)}")
            for member in self.party_manager.members:
                member_weight = member.inventory.get_total_weight()
                total_weight += member_weight
                max_weight += member.inventory.max_weight
                
                weight_ratio = member.inventory.get_weight_ratio()
                weight_color = Color.GREEN if weight_ratio < 0.7 else Color.YELLOW if weight_ratio < 0.9 else Color.RED
                
                # 이름과 무게 정보
                weight_field = f"{member_weight:.1f}/{member.inventory.max_weight:.1f}kg"
                print(f"{cyan(member.name)} | {colored(weight_field, weight_color)}")
                
                # HP/MP 게이지를 이름 밑에 표시
                hp_field = f"HP:{member.current_hp:3}/{member.limited_max_hp:3}"
                mp_field = f"MP:{member.current_mp:3}/{member.max_mp:3}"
                hp_bar = member.get_hp_bar(10)
                mp_bar = member.get_mp_bar(10)
                
                print(f"    {hp_field} {hp_bar} | {mp_field} {mp_bar}")
                print()  # 빈 줄로 구분
            
            print(f"\n전체: {colored(f'{total_weight:.1f}', ColorText.hp_color(int(total_weight*10), int(max_weight*10)))}/{max_weight:.1f}kg"
                  f" | 파티 골드: {bright_yellow(f'{self.party_manager.get_total_gold()}G', True)}")
            
            # 모든 파티원의 아이템 수집
            all_items = []
            for member in self.party_manager.members:
                for item_name, quantity in member.inventory.get_items_list():
                    db = ItemDatabase()
                    item = db.get_item(item_name)
                    if item:
                        all_items.append((item, member, quantity))
            
            if not all_items:
                print(red("아이템이 없습니다."))
            else:
                print(f"\n{bright_white('아이템 목록:', True)}")
                for i, (item, owner, quantity) in enumerate(all_items, 1):
                    # 희귀도별 색상
                    item_name = rarity_colored(item.name, item.rarity.value)
                    
                    # 수량 표시
                    qty_str = f" x{quantity}" if quantity > 1 else ""
                    
                    # 무게 정보
                    weight_info = f" ({item.weight:.1f}kg)"
                    
                    print(f"{i:2}. {item_name}{qty_str} ({cyan(item.item_type.value)}){weight_info} - {green(owner.name)}")
                    
                    # 아이템 효과를 더 이해하기 쉽게 표시
                    if item.stats:
                        effect_parts = []
                        for k, v in item.stats.items():
                            if k == "damage_amount":
                                effect_parts.append(f"공격력 {bright_green(f'+{v}')}")
                            elif k == "element":
                                element_names = {"ice": "얼음", "fire": "불", "lightning": "번개", "earth": "땅", "water": "물", "wind": "바람"}
                                element_name = element_names.get(v.lower(), v)
                                effect_parts.append(f"속성: {cyan(element_name)}")
                            elif k == "physical_attack":
                                effect_parts.append(f"물리공격 {bright_green(f'+{v}')}")
                            elif k == "magic_attack":
                                effect_parts.append(f"마법공격 {bright_green(f'+{v}')}")
                            elif k == "physical_defense":
                                effect_parts.append(f"물리방어 {bright_green(f'+{v}')}")
                            elif k == "magic_defense":
                                effect_parts.append(f"마법방어 {bright_green(f'+{v}')}")
                            elif k == "speed":
                                effect_parts.append(f"속도 {bright_green(f'+{v}')}")
                            elif k == "max_hp":
                                effect_parts.append(f"최대HP {bright_green(f'+{v}')}")
                            else:
                                effect_parts.append(f"{k}: {bright_green(f'+{v}')}")
                        
                        if effect_parts:
                            print(f"     📈 스탯: {', '.join(effect_parts)}")
                    
                    # 소모품 효과 표시 추가
                    elif hasattr(item, 'effect_type') and item.effect_type:
                        effect_desc = self.get_consumable_effect_description(item)
                        if effect_desc:
                            print(f"     ✨ 효과: {cyan(effect_desc)}")
                    
                    if hasattr(item, 'effects') and item.effects:
                        special_parts = []
                        for effect in item.effects:
                            if effect == "ice_damage":
                                special_parts.append(f"{cyan('얼음 피해')}")
                            elif effect == "freeze":
                                special_parts.append(f"{blue('빙결 효과')}")
                            elif effect == "cure_silence":
                                special_parts.append(f"{green('침묵 치료')}")
                            elif effect == "fire_damage":
                                special_parts.append(f"{red('화염 피해')}")
                            elif effect == "poison":
                                special_parts.append(f"{magenta('독 효과')}")
                            elif effect == "heal":
                                special_parts.append(f"{green('회복 효과')}")
                            elif effect == "luck_boost":
                                special_parts.append(f"{yellow('행운 증가')}")
                            elif effect == "critical_boost":
                                special_parts.append(f"{red('치명타율 증가')}")
                            elif effect == "defense_boost":
                                special_parts.append(f"{blue('방어력 증가')}")
                            elif effect == "attack_boost":
                                special_parts.append(f"{red('공격력 증가')}")
                            elif effect == "mp_regeneration":
                                special_parts.append(f"{cyan('MP 재생')}")
                            elif effect == "hp_regeneration":
                                special_parts.append(f"{green('HP 재생')}")
                            elif effect == "magic_resistance":
                                special_parts.append(f"{magenta('마법 저항')}")
                            elif effect == "poison_immunity":
                                special_parts.append(f"{green('독 면역')}")
                            elif effect == "fire_resistance":
                                special_parts.append(f"{red('화염 저항')}")
                            elif effect == "ice_resistance":
                                special_parts.append(f"{cyan('냉기 저항')}")
                            elif effect == "status_immunity":
                                special_parts.append(f"{yellow('상태이상 면역')}")
                            else:
                                # 알 수 없는 특수 효과는 원래 이름 표시
                                special_parts.append(f"{magenta(effect)}")
                        
                        if special_parts:
                            print(f"     특수: {', '.join(special_parts)}")
            
            print(f"\n{bright_white('명령:', True)}")
            print(f"{yellow('(1-N)')} 아이템 사용/장착  {yellow('(S)')} 상점  {yellow('(E)')} 장비 현황  {yellow('(M)')} 아이템 이동")
            print(f"{yellow('(D)')} 아이템 버리기  {yellow('(Q)')} 나가기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == 'q':
                self.sound_manager.play_sfx("menu_cancel")
                break
            elif choice == 'e':
                self.sound_manager.play_sfx("menu_select")
                self.show_equipment_status()
            elif choice == 's':
                self.sound_manager.play_sfx("menu_select")
                self.show_shop_interface()
            elif choice == 'm':
                self.sound_manager.play_sfx("menu_select")
                self.show_item_transfer_interface()
            elif choice == 'd':
                self.sound_manager.play_sfx("menu_select")
                self.discard_item_interface()
            elif choice.isdigit():
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(all_items):
                        item, owner, quantity = all_items[index]
                        self.sound_manager.play_sfx("menu_select")
                        self.use_or_equip_item(item, owner)
                    else:
                        self.sound_manager.play_sfx("menu_error")
                except ValueError:
                    self.sound_manager.play_sfx("menu_error")
    
    def get_consumable_effect_description(self, item):
        """소모품 효과 설명 생성"""
        if not hasattr(item, 'effect_type'):
            return ""
        
        effect_type = item.effect_type
        effect_value = getattr(item, 'effect_value', 0)
        target_type = getattr(item, 'target_type', 'single')
        
        target_str = "전체" if target_type == "all_allies" else "단일"
        
        if effect_type == "heal_hp":
            return f"HP {effect_value} 회복 ({target_str})"
        elif effect_type == "heal_mp":
            return f"MP {effect_value} 회복 ({target_str})"
        elif effect_type == "cure_poison":
            return "독 상태 치료"
        elif effect_type == "cure_all":
            return "모든 상태이상 치료"
        elif effect_type == "revive":
            return f"{effect_value}% HP로 부활"
        elif effect_type.startswith("buff_"):
            stat_name = effect_type.replace("buff_", "")
            stat_korean = {
                "attack": "공격력",
                "defense": "방어력", 
                "speed": "속도",
                "magic": "마법력"
            }.get(stat_name, stat_name)
            return f"{stat_korean} +{effect_value} 버프 (10턴)"
        else:
            return f"{effect_type} 효과"
    
    def show_shop_interface(self):
        """상점 인터페이스"""
        # 현재 층에서 상인 찾기
        merchant = self.merchant_manager.try_spawn_merchant(self.world.current_floor)
        
        if not merchant:
            print(red("이 층에는 상인이 없습니다."))
            self.keyboard.get_key()
            return
        
        while True:
            print("\n" + "="*60)
            print(bright_yellow(f"🏪 {merchant.name}의 상점", True))
            print("="*60)
            
            # 상점 정보 표시
            for line in merchant.get_shop_display():
                print(line)
            
            print(f"\n{bright_white('명령:', True)}")
            print(f"{green('(B)')} 구매  {yellow('(S)')} 판매  {red('(Q)')} 나가기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == 'q':
                self.sound_manager.play_sfx("menu_cancel")
                break
            elif choice == 'b':
                self.sound_manager.play_sfx("menu_select")
                self.buy_from_merchant(merchant)
            elif choice == 's':
                self.sound_manager.play_sfx("menu_select")
                self.sell_to_merchant(merchant)
            else:
                self.sound_manager.play_sfx("menu_error")
    
    def buy_from_merchant(self, merchant):
        """상인에게서 구매"""
        if not merchant.shop_items:
            print(red("판매할 아이템이 없습니다."))
            self.keyboard.get_key()
            return
        
        print(f"\n{bright_green('구매할 아이템을 선택하세요:', True)}")
        for i, shop_item in enumerate(merchant.shop_items, 1):
            item_name = rarity_colored(shop_item.item.name, shop_item.item.rarity.value)
            print(f"{i}. {item_name} - {yellow(f'{shop_item.price}G')} (재고: {shop_item.stock})")
        
        print(f"\n{cyan('구매자를 선택하세요:')}")
        print(f"파티 골드: {bright_yellow(f'{self.party_manager.get_total_gold()}G', True)}")
        print()
        for i, member in enumerate(self.party_manager.members, 1):
            # 정렬된 형태로 파티원 정보 표시 (더 긴 막대)
            name_field = f"{member.name[:10]:10}"
            hp_field = f"HP:{member.current_hp:3}/{member.limited_max_hp:3}"
            hp_bar = member.get_hp_bar(8)
            
            member_info = f"{i}. {cyan(name_field)} | {hp_field} {hp_bar}"
            print(member_info)
        
        print("아이템 번호와 구매자 번호를 입력하세요 (예: 1 2) 또는 Q로 취소:")
        
        try:
            user_input = input().strip()
            if user_input.lower() == 'q':
                return
            
            item_idx, buyer_idx = map(int, user_input.split())
            item_idx -= 1
            buyer_idx -= 1
            
            if 0 <= item_idx < len(merchant.shop_items) and 0 <= buyer_idx < len(self.party_manager.members):
                buyer = self.party_manager.members[buyer_idx]
                success, message = merchant.buy_item_with_party_gold(self.party_manager, buyer, item_idx)
                
                if success:
                    print(bright_green(message))
                else:
                    print(red(message))
            else:
                print(red("잘못된 선택입니다."))
        except:
            print(red("잘못된 입력입니다."))
        
        self.keyboard.get_key()
    
    def sell_to_merchant(self, merchant):
        """상인에게 판매 (개인 인벤토리 + 파티 인벤토리)"""
        # 판매할 수 있는 아이템 목록
        sellable_items = []
        
        # 개인 인벤토리 아이템
        for member in self.party_manager.members:
            for item_name, quantity in member.inventory.get_items_list():
                sellable_items.append((item_name, member, quantity, "개인"))
        
        # 파티 공용 인벤토리 아이템
        for item_name, quantity in self.party_manager.shared_inventory.get_items_list():
            sellable_items.append((item_name, None, quantity, "파티"))
        
        if not sellable_items:
            print(red("판매할 아이템이 없습니다."))
            self.keyboard.get_key()
            return
        
        print(f"\n{bright_yellow('판매할 아이템을 선택하세요:', True)}")
        for i, (item_name, owner, quantity, source) in enumerate(sellable_items, 1):
            db = ItemDatabase()
            item = db.get_item(item_name)
            if item:
                estimated_price = int(item.value * 0.6)  # 추정 판매가
                item_display = rarity_colored(item_name, item.rarity.value)
                
                # 소유자/소스 정보를 정렬된 형태로 표시
                if source == "파티":
                    owner_field = f"{'파티 공용':10}"
                else:
                    owner_field = f"{owner.name:10}"
                qty_field = f"x{quantity:2}"
                price_field = f"예상: {estimated_price}G"
                
                item_info = f"{i:2}. {item_display} {qty_field} | {green(owner_field)} | {yellow(price_field)}"
                print(item_info)
        
        print("판매할 아이템 번호를 입력하세요 (Q로 취소):")
        
        try:
            user_input = input().strip()
            if user_input.lower() == 'q':
                return
            
            item_idx = int(user_input) - 1
            
            if 0 <= item_idx < len(sellable_items):
                item_name, owner, _, source = sellable_items[item_idx]
                
                if source == "파티":
                    # 파티 공용 인벤토리에서 판매
                    success, message = merchant.sell_party_item(self.party_manager, item_name)
                else:
                    # 개인 인벤토리에서 판매
                    success, message = merchant.sell_item_to_party(self.party_manager, owner, item_name)
                
                if success:
                    print(bright_green(message))
                else:
                    print(red(message))
            else:
                print(red("잘못된 선택입니다."))
        except:
            print(red("잘못된 입력입니다."))
        
        self.keyboard.get_key()
    
    def discard_item_interface(self):
        """아이템 버리기 인터페이스"""
        # 버릴 수 있는 아이템 목록 (개인 + 파티 인벤토리)
        discardable_items = []
        
        # 개인 인벤토리 아이템
        for member in self.party_manager.members:
            for item_name, quantity in member.inventory.get_items_list():
                discardable_items.append((item_name, member, quantity, "개인"))
        
        # 파티 공용 인벤토리 아이템
        for item_name, quantity in self.party_manager.shared_inventory.get_items_list():
            discardable_items.append((item_name, None, quantity, "파티"))
        
        if not discardable_items:
            print(red("버릴 아이템이 없습니다."))
            self.keyboard.get_key()
            return
        
        print(f"\n{bright_red('⚠️  아이템 버리기', True)}")
        print(f"{yellow('주의: 버린 아이템은 복구할 수 없습니다!')}")
        print("="*50)
        
        for i, (item_name, owner, quantity, source) in enumerate(discardable_items, 1):
            db = ItemDatabase()
            item = db.get_item(item_name)
            if item:
                item_display = rarity_colored(item_name, item.rarity.value)
                
                # 소유자/소스 정보
                if source == "파티":
                    owner_field = f"{'파티 공용':10}"
                else:
                    owner_field = f"{owner.name:10}"
                    
                qty_field = f"x{quantity:2}"
                weight_field = f"({item.weight:.1f}kg)"
                
                item_info = f"{i:2}. {item_display} {qty_field} | {green(owner_field)} | {weight_field}"
                print(item_info)
        
        print(f"\n버릴 아이템 번호를 입력하세요 (Q로 취소):")
        
        try:
            user_input = input().strip()
            if user_input.lower() == 'q':
                return
            
            item_idx = int(user_input) - 1
            
            if 0 <= item_idx < len(discardable_items):
                item_name, owner, quantity, source = discardable_items[item_idx]
                
                # 확인 메시지
                print(f"\n정말로 {bright_red(item_name)}을(를) 버리시겠습니까? (Y/N)")
                confirm = self.keyboard.get_key().lower()
                
                if confirm == 'y':
                    if source == "파티":
                        # 파티 공용 인벤토리에서 버리기
                        success = self.party_manager.discard_party_item(item_name, 1)
                    else:
                        # 개인 인벤토리에서 버리기
                        success = owner.inventory.remove_item(item_name, 1)
                        if success:
                            print(f"{item_name}을(를) 버렸습니다.")
                        else:
                            print(f"{item_name}을(를) 버리지 못했습니다.")
                    
                    if success:
                        self.sound_manager.play_sfx("item_discard")
                        print(bright_green(f"{item_name}을(를) 성공적으로 버렸습니다."))
                    else:
                        self.sound_manager.play_sfx("menu_error")
                else:
                    print("버리기를 취소했습니다.")
            else:
                print(red("잘못된 선택입니다."))
        except:
            print(red("잘못된 입력입니다."))
        
        self.keyboard.get_key()
    
    def show_item_transfer_interface(self):
        """아이템 이동 인터페이스 (개인 ↔ 파티 공용)"""
        while True:
            # 이동 가능한 아이템 목록 수집
            transferable_items = []
            
            # 개인 인벤토리 아이템들
            for member in self.party_manager.members:
                for item_name, quantity in member.inventory.get_items_list():
                    transferable_items.append((item_name, member, quantity, "개인→파티"))
            
            # 파티 공용 인벤토리 아이템들
            for item_name, quantity in self.party_manager.shared_inventory.get_items_list():
                transferable_items.append((item_name, None, quantity, "파티→개인"))
            
            if not transferable_items:
                print(red("이동할 아이템이 없습니다."))
                self.keyboard.get_key()
                return
            
            print(f"\n{bright_cyan('📦 아이템 이동', True)}")
            print("="*60)
            print(f"{yellow('개인 인벤토리 ↔ 파티 공용 인벤토리')}")
            print("="*60)
            
            # 아이템 목록 표시
            for i, (item_name, owner, quantity, direction) in enumerate(transferable_items, 1):
                db = ItemDatabase()
                item = db.get_item(item_name)
                if item:
                    item_display = rarity_colored(item_name, item.rarity.value)
                    
                    # 소유자/방향 정보
                    if direction == "개인→파티":
                        source_info = f"{owner.name:10} → 파티공용"
                    else:
                        source_info = f"파티공용 → {'개인선택':10}"
                    
                    qty_field = f"x{quantity:2}"
                    weight_field = f"({item.weight:.1f}kg)"
                    
                    item_info = f"{i:2}. {item_display} {qty_field} | {cyan(source_info)} | {weight_field}"
                    print(item_info)
            
            print(f"\n{bright_white('명령:', True)}")
            print(f"{yellow('(1-N)')} 아이템 이동  {yellow('(Q)')} 나가기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == 'q':
                self.sound_manager.play_sfx("menu_cancel")
                break
            elif choice.isdigit():
                try:
                    item_idx = int(choice) - 1
                    
                    if 0 <= item_idx < len(transferable_items):
                        item_name, owner, quantity, direction = transferable_items[item_idx]
                        self.sound_manager.play_sfx("menu_select")
                        self._transfer_item(item_name, owner, direction)
                    else:
                        print(red("잘못된 선택입니다."))
                        self.sound_manager.play_sfx("menu_error")
                        self.keyboard.get_key()
                except ValueError:
                    print(red("숫자를 입력해주세요."))
                    self.sound_manager.play_sfx("menu_error")
                    self.keyboard.get_key()
    
    def _transfer_item(self, item_name, source_owner, direction):
        """아이템 이동 실행"""
        db = ItemDatabase()
        item = db.get_item(item_name)
        
        if not item:
            print(red(f"아이템 '{item_name}'을 찾을 수 없습니다."))
            self.keyboard.get_key()
            return
        
        if direction == "개인→파티":
            # 개인 → 파티 공용
            if source_owner.inventory.has_item(item_name):
                # 파티 공용 인벤토리 용량 확인
                can_add, reason = self.party_manager.shared_inventory.can_add_item(item)
                if can_add:
                    source_owner.inventory.remove_item(item_name, 1)
                    self.party_manager.shared_inventory.add_item(item)
                    print(bright_green(f"{item_name}을(를) {source_owner.name}에서 파티 공용으로 이동했습니다."))
                    self.sound_manager.play_sfx("item_move")
                else:
                    print(red(f"파티 공용 인벤토리에 공간이 부족합니다: {reason}"))
                    self.sound_manager.play_sfx("menu_error")
            else:
                print(red(f"{source_owner.name}이 {item_name}을 가지고 있지 않습니다."))
                self.sound_manager.play_sfx("menu_error")
        
        else:
            # 파티 공용 → 개인 (파티원 선택)
            print(f"\n{item_name}을(를) 누가 가져갈까요?")
            print("="*40)
            
            for i, member in enumerate(self.party_manager.members, 1):
                # 해당 파티원이 아이템을 받을 수 있는지 확인
                can_add, reason = member.inventory.can_add_item(item)
                
                weight_info = f"{member.inventory.get_total_weight():.1f}/{member.inventory.max_weight:.1f}kg"
                status = bright_green("✓") if can_add else red("✗")
                
                member_info = f"{i}. {member.name:10} | {weight_info} {status}"
                if not can_add:
                    member_info += f" ({red(reason)})"
                
                print(member_info)
            
            print(f"\n파티원 번호를 선택하세요 (Q로 취소):")
            
            try:
                choice = self.keyboard.get_key().lower()
                if choice == 'q':
                    return
                
                member_idx = int(choice) - 1
                
                if 0 <= member_idx < len(self.party_manager.members):
                    target_member = self.party_manager.members[member_idx]
                    
                    # 받을 수 있는지 다시 확인
                    can_add, reason = target_member.inventory.can_add_item(item)
                    if can_add:
                        self.party_manager.shared_inventory.remove_item(item_name, 1)
                        target_member.inventory.add_item(item)
                        print(bright_green(f"{item_name}을(를) 파티 공용에서 {target_member.name}으로 이동했습니다."))
                        self.sound_manager.play_sfx("item_move")
                    else:
                        print(red(f"{target_member.name}이 {item_name}을 받을 수 없습니다: {reason}"))
                        self.sound_manager.play_sfx("menu_error")
                else:
                    print(red("잘못된 선택입니다."))
                    self.sound_manager.play_sfx("menu_error")
            except ValueError:
                print(red("숫자를 입력해주세요."))
                self.sound_manager.play_sfx("menu_error")
        
        self.keyboard.get_key()

    def show_permanent_progression_menu(self):
        """영구 성장 메뉴 표시"""
        while True:
            print("\n" + "="*60)
            print(bright_yellow("✨ 영구 성장 시스템", True))
            print("="*60)
            
            # 진행상황 표시
            for line in self.permanent_progression.get_upgrade_menu_display():
                if "별의 정수:" in line:
                    print(bright_yellow(line, True))
                elif "총 플레이:" in line:
                    print(cyan(line))
                elif "영구 업그레이드" in line:
                    print(bright_white(line, True))
                else:
                    print(line)
            
            print(f"\n{bright_white('명령:', True)}")
            print(f"{green('(1-10)')} 업그레이드 구매  {red('(Q)')} 돌아가기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == 'q':
                self.sound_manager.play_sfx("menu_cancel")
                break
            elif choice.isdigit():
                try:
                    upgrade_index = int(choice) - 1
                    upgrade_list = list(self.permanent_progression.upgrades.keys())
                    
                    if 0 <= upgrade_index < len(upgrade_list):
                        upgrade_id = upgrade_list[upgrade_index]
                        success, message = self.permanent_progression.purchase_upgrade(upgrade_id)
                        
                        if success:
                            print(bright_green(message))
                            # 영구 진행상황 저장
                            self.permanent_progression.save_to_file()
                        else:
                            print(red(message))
                        
                        self.keyboard.get_key()
                    else:
                        print(red("잘못된 선택입니다."))
                        self.keyboard.get_key()
                except ValueError:
                    print(red("숫자를 입력해주세요."))
                    self.keyboard.get_key()
    
    def show_equipment_status(self):
        """장비 현황 표시 및 관리"""
        while True:
            print("\n" + "="*80)
            print("⚔️ 장비 현황")
            print("="*80)
            
            # 파티원 번호와 장비 정보를 저장할 리스트
            member_equipment = []
            
            for i, member in enumerate(self.party_manager.members, 1):
                # 파티원 기본 정보 (정렬된 형태, 더 긴 막대)
                name_field = f"{member.name[:10]:10}"
                class_field = f"{member.character_class[:8]:8}"
                hp_field = f"HP:{member.current_hp:3}/{member.limited_max_hp:3}"
                mp_field = f"MP:{member.current_mp:3}/{member.max_mp:3}"
                
                hp_bar = member.get_hp_bar(10)
                mp_bar = member.get_mp_bar(10)
                
                member_status = f"{cyan(name_field)} | {class_field} | {hp_field} {hp_bar} | {mp_field} {mp_bar}"
                print(f"\n{bright_white(f'[{i}] {member.name}', True)}")
                print(f"{member_status}")
                
                # 장비 정보 저장 및 표시
                equipped_items = member.get_equipped_items()
                member_equipment.append((member, equipped_items))
                
                weapon_display = equipped_items["무기"].name if equipped_items["무기"] else red("없음")
                armor_display = equipped_items["방어구"].name if equipped_items["방어구"] else red("없음") 
                accessory_display = equipped_items["장신구"].name if equipped_items["장신구"] else red("없음")
                
                print(f"  {'무기:':8} {weapon_display}")
                print(f"  {'방어구:':8} {armor_display}")
                print(f"  {'장신구:':8} {accessory_display}")
            
            print(f"\n{bright_white('명령:', True)}")
            print(f"{yellow('(1-4)')} 파티원 선택  {yellow('(Q)')} 나가기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == 'q':
                self.sound_manager.play_sfx("menu_cancel")
                break
            elif choice.isdigit():
                try:
                    member_index = int(choice) - 1
                    if 0 <= member_index < len(self.party_manager.members):
                        self.sound_manager.play_sfx("menu_select")
                        self.manage_member_equipment(self.party_manager.members[member_index])
                    else:
                        self.sound_manager.play_sfx("menu_error")
                except ValueError:
                    self.sound_manager.play_sfx("menu_error")
                except ValueError:
                    pass
    
    def manage_member_equipment(self, member):
        """특정 파티원의 장비 관리"""
        while True:
            print(f"\n" + "="*60)
            print(f"⚔️ {member.name}의 장비 관리")
            print("="*60)
            
            equipped_items = member.get_equipped_items()
            
            # 장착된 아이템 표시
            equipment_options = []
            
            for slot_name, item in equipped_items.items():
                if item:
                    equipment_options.append((slot_name, item))
                    item_name = rarity_colored(item.name, item.rarity.value)
                    
                    # 스탯 정보 표시
                    stats_info = ""
                    if item.stats:
                        stats_info = " (" + ", ".join([f"{k}+{v}" for k, v in item.stats.items()]) + ")"
                    
                    print(f"{len(equipment_options)}. {yellow(slot_name)}: {item_name}{stats_info}")
                else:
                    print(f"   {yellow(slot_name)}: {red('없음')}")
            
            if not equipment_options:
                print(red("장착된 장비가 없습니다."))
                print(f"\n{yellow('(Q)')} 나가기")
            else:
                print(f"\n{bright_white('명령:', True)}")
                print(f"{yellow('(1-N)')} 장비 해제  {yellow('(Q)')} 나가기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == 'q':
                self.sound_manager.play_sfx("menu_cancel")
                break
            elif choice.isdigit() and equipment_options:
                try:
                    equipment_index = int(choice) - 1
                    if 0 <= equipment_index < len(equipment_options):
                        self.sound_manager.play_sfx("menu_select")
                        slot_name, item = equipment_options[equipment_index]
                        self.unequip_item_from_member(member, slot_name, item)
                except ValueError:
                    pass
    
    def unequip_item_from_member(self, member, slot_name, item):
        """파티원에게서 아이템 장착 해제"""
        # 장착 해제
        unequipped_item = member.unequip_item(slot_name)
        
        if unequipped_item:
            # 인벤토리에 공간이 있는지 확인
            can_add, reason = member.inventory.can_add_item(unequipped_item)
            if not can_add:
                print(red(f"⚠️ {member.name}의 인벤토리에 공간이 없습니다! ({reason})"))
                # 장착을 다시 원상복구
                member.equip_item(unequipped_item)
                self.sound_manager.play_sfx("menu_error")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                return
            
            # 인벤토리에 추가
            member.inventory.add_item(unequipped_item)
            
            # 장비 효과 제거
            self.remove_equipment_effects(member, unequipped_item)
            
            # 장착 해제 효과음
            self.sound_manager.play_sfx("item_use")
            
            print(green(f"✅ {member.name}이(가) {unequipped_item.name}을(를) 해제했습니다!"))
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        else:
            print(red("장착 해제에 실패했습니다."))
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def use_or_equip_item(self, item, owner):
        """아이템 사용 또는 장착"""
        if item.item_type.value == "소모품":
            # 소모품 사용
            success = self.use_consumable_item(item, owner)
            if success:
                owner.inventory.remove_item(item)
                print(f"✅ {item.name}을(를) 사용했습니다.")
                # 소모품 사용 효과음
                self.sound_manager.play_sfx("item_use")
                time.sleep(0.5)
                self.keyboard.wait_for_key("🔑 효과를 확인하세요. 계속하려면 아무 키나 누르세요...")
            else:
                print(f"❌ {item.name}을(를) 사용할 수 없습니다.")
                self.sound_manager.play_sfx("menu_error")
                time.sleep(0.5)
                self.keyboard.wait_for_key("🔑 계속하려면 아무 키나 누르세요...")
        else:
            # 장비 아이템 - 파티원 선택
            self.select_party_member_for_equipment(item, owner)
    
    def use_consumable_item(self, item, owner):
        """소모품 사용 효과 처리"""
        try:
            # 기본 아이템 효과가 있는지 확인
            if hasattr(item, 'effect_type') and hasattr(item, 'effect_value'):
                return self.apply_consumable_effect(item, owner)
            
            # 아이템 이름으로 특별 효과 처리
            item_name = item.name
            
            # 🍶 HP 회복 아이템
            if "포션" in item_name and ("치료" in item_name or "작은" in item_name):
                heal_amount = self.get_heal_amount_by_name(item_name)
                return self.heal_character_hp(owner, heal_amount)
            
            # 🧪 MP 회복 아이템
            elif "마나" in item_name:
                mp_amount = self.get_mp_amount_by_name(item_name)
                return self.heal_character_mp(owner, mp_amount)
            
            # 💊 상태 치료 아이템
            elif "해독제" in item_name:
                return self.cure_status_effect(owner, "독")
            elif "해열제" in item_name:
                return self.cure_status_effect(owner, "화상")
            elif "해빙제" in item_name:
                return self.cure_status_effect(owner, "빙결")
            elif "진정제" in item_name:
                return self.cure_status_effect(owner, "혼란")
            elif "만능" in item_name and "치료제" in item_name:
                return self.cure_all_status_effects(owner)
            
            # ⚔️ 공격 아이템 (전투 중에만 사용 가능하도록 확장 가능)
            elif any(word in item_name for word in ["수리검", "폭탄", "화염병", "독 다트"]):
                print("💥 전투용 아이템입니다. 전투 중에 사용하세요.")
                return False
            
            # ✨ 특수 아이템
            elif "부활" in item_name:
                return self.revive_character(owner)
            elif "엘릭서" in item_name:
                return self.use_elixir(owner, item_name)
            elif "축복" in item_name:
                return self.apply_blessing(owner)
            
            else:
                print(f"⚠️ {item_name}의 사용법을 모르겠습니다.")
                return False
                
        except Exception as e:
            print(f"❌ 아이템 사용 중 오류 발생: {e}")
            return False
    
    def apply_consumable_effect(self, item, owner):
        """소모품 객체의 효과 적용"""
        effect_type = item.effect_type
        effect_value = item.effect_value
        target_type = getattr(item, 'target_type', 'single')
        
        if target_type == "single":
            targets = [owner]
        elif target_type == "all_allies":
            targets = self.party_manager.get_alive_members()
        else:
            targets = [owner]
        
        success = False
        for target in targets:
            if effect_type == "heal_hp":
                success |= self.heal_character_hp(target, effect_value)
            elif effect_type == "heal_mp":
                success |= self.heal_character_mp(target, effect_value)
            elif effect_type == "cure_poison":
                success |= self.cure_status_effect(target, "독")
            elif effect_type == "cure_all":
                success |= self.cure_all_status_effects(target)
            elif effect_type == "revive":
                success |= self.revive_character(target, effect_value)
            elif effect_type.startswith("buff_"):
                success |= self.apply_stat_buff(target, effect_type, effect_value)
        
        return success
    
    def get_heal_amount_by_name(self, item_name):
        """아이템 이름으로 회복량 결정"""
        if "작은" in item_name:
            return 25
        elif "상급" in item_name:
            return 80
        elif "최상급" in item_name:
            return 150
        elif "엘릭서" in item_name:
            return 999  # 완전 회복
        else:
            return 50  # 기본 치료 포션
    
    def get_mp_amount_by_name(self, item_name):
        """아이템 이름으로 MP 회복량 결정"""
        if "작은" in item_name:
            return 15
        elif "고급" in item_name:
            return 40
        elif "최고급" in item_name:
            return 80
        elif "신성한" in item_name:
            return 150
        else:
            return 25  # 기본 마나 포션
    
    def heal_character_hp(self, character, amount):
        """캐릭터 HP 회복"""
        if not character.is_alive:
            print(f"💀 {character.name}은(는) 죽어있어서 치료할 수 없습니다.")
            return False
        
        old_hp = character.current_hp
        max_healable = character.limited_max_hp
        
        if amount == 999:  # 완전 회복
            character.current_hp = max_healable
            healed = max_healable - old_hp
        else:
            character.current_hp = min(max_healable, character.current_hp + amount)
            healed = character.current_hp - old_hp
        
        if healed > 0:
            print(f"❤️ {character.name}의 HP가 {healed} 회복되었습니다! ({old_hp} -> {character.current_hp})")
            # 상처 치료도 시도
            if character.current_hp >= character.limited_max_hp:
                wound_heal = min(character.wounds, healed // 4)  # 초과 회복량의 1/4만큼 상처 치료
                if wound_heal > 0:
                    character.wounds = max(0, character.wounds - wound_heal)
                    character.update_limited_max_hp()
                    print(f"🩹 상처가 {wound_heal} 치료되었습니다!")
            return True
        else:
            print(f"💯 {character.name}은(는) 이미 최대 체력입니다.")
            return False
    
    def heal_character_mp(self, character, amount):
        """캐릭터 MP 회복"""
        if not character.is_alive:
            print(f"💀 {character.name}은(는) 죽어있어서 마나를 회복할 수 없습니다.")
            return False
        
        old_mp = character.current_mp
        
        if amount == 999:  # 완전 회복
            character.current_mp = character.max_mp
        else:
            character.current_mp = min(character.max_mp, character.current_mp + amount)
        
        healed = character.current_mp - old_mp
        
        if healed > 0:
            print(f"💙 {character.name}의 MP가 {healed} 회복되었습니다! ({old_mp} -> {character.current_mp})")
            return True
        else:
            print(f"💯 {character.name}은(는) 이미 최대 마나입니다.")
            return False
    
    def cure_status_effect(self, character, status_name):
        """특정 상태이상 치료"""
        if not character.is_alive:
            print(f"💀 {character.name}은(는) 죽어있어서 치료할 수 없습니다.")
            return False
        
        # 상태이상 확인 및 제거
        if hasattr(character, 'status_effects') and character.status_effects:
            removed = []
            for effect in character.status_effects[:]:
                if status_name in effect.name or status_name in effect.description:
                    character.status_effects.remove(effect)
                    removed.append(effect.name)
            
            if removed:
                print(f"✨ {character.name}의 {', '.join(removed)} 상태가 치료되었습니다!")
                return True
        
        print(f"🔍 {character.name}은(는) {status_name} 상태가 아닙니다.")
        return False
    
    def cure_all_status_effects(self, character):
        """모든 상태이상 치료"""
        if not character.is_alive:
            print(f"💀 {character.name}은(는) 죽어있어서 치료할 수 없습니다.")
            return False
        
        if hasattr(character, 'status_effects') and character.status_effects:
            removed_count = len(character.status_effects)
            character.status_effects.clear()
            print(f"✨ {character.name}의 모든 상태이상({removed_count}개)이 치료되었습니다!")
            return True
        else:
            print(f"🔍 {character.name}은(는) 상태이상이 없습니다.")
            return False
    
    def revive_character(self, character, hp_percent=50):
        """캐릭터 부활"""
        if character.is_alive:
            print(f"💯 {character.name}은(는) 이미 살아있습니다.")
            return False
        
        # 부활 처리
        character.current_hp = max(1, int(character.max_hp * hp_percent / 100))
        character.is_alive = True
        
        print(f"🌟 {character.name}이(가) 부활했습니다! (HP: {character.current_hp})")
        return True
    
    def use_elixir(self, character, item_name):
        """엘릭서 사용 (완전 회복 + 추가 효과)"""
        if not character.is_alive:
            print(f"💀 {character.name}은(는) 죽어있어서 사용할 수 없습니다.")
            return False
        
        # 완전 회복
        character.current_hp = character.max_hp
        character.current_mp = character.max_mp
        
        # 상처도 일부 치료
        if character.wounds > 0:
            wound_heal = character.wounds // 2
            character.wounds = max(0, character.wounds - wound_heal)
            character.update_limited_max_hp()
            print(f"🩹 상처 {wound_heal}이 치료되었습니다!")
        
        # 모든 상태이상 치료
        if hasattr(character, 'status_effects'):
            character.status_effects.clear()
        
        print(f"💎 {character.name}이(가) 완전히 회복되었습니다!")
        return True
    
    def apply_stat_buff(self, character, buff_type, value):
        """스탯 버프 적용"""
        if not character.is_alive:
            return False
        
        # 임시 버프 시스템 (간단한 구현)
        if not hasattr(character, 'temporary_buffs'):
            character.temporary_buffs = {}
        
        duration = 10  # 10턴 지속
        
        if buff_type == "buff_attack":
            character.physical_attack += value
            buff_name = f"공격력 +{value}"
        elif buff_type == "buff_defense":
            character.physical_defense += value
            buff_name = f"방어력 +{value}"
        elif buff_type == "buff_speed":
            character.speed += value
            character.atb_speed = character.speed
            buff_name = f"속도 +{value}"
        elif buff_type == "buff_magic":
            character.magic_attack += value
            buff_name = f"마법력 +{value}"
        else:
            return False
        
        character.temporary_buffs[buff_type] = {
            'value': value,
            'duration': duration,
            'name': buff_name
        }
        
        print(f"⬆️ {character.name}에게 {buff_name} 버프가 적용되었습니다! ({duration}턴)")
        return True
    
    def apply_blessing(self, character):
        """축복 효과 적용"""
        if not character.is_alive:
            return False
        
        # 모든 스탯 소폭 증가
        character.physical_attack += 2
        character.magic_attack += 2
        character.physical_defense += 2
        character.magic_defense += 2
        character.speed += 1
        
        print(f"🙏 {character.name}이(가) 축복을 받았습니다! (모든 스탯 증가)")
        return True
    
    def update_passive_effects(self):
        """모든 파티원의 패시브 효과 업데이트"""
        for member in self.party_manager.members:
            if member.is_alive:
                self.apply_character_passives(member)
    
    def apply_character_passives(self, character):
        """캐릭터의 패시브 효과 적용"""
        # 임시 보너스 초기화
        character.temp_attack_bonus = 0
        character.temp_defense_bonus = 0
        character.temp_speed_bonus = 0
        character.temp_magic_bonus = 0
        character.temp_crit_bonus = 0
        character.temp_dodge_bonus = 0
        character.temp_exp_bonus = 0
        character.temp_resistance_bonus = 0
        character.temp_penetration = 0
        
        # 활성 특성들의 패시브 효과 적용
        if hasattr(character, 'active_traits'):
            # active_traits가 딕셔너리인 경우 values()를 사용
            traits = character.active_traits.values() if isinstance(character.active_traits, dict) else character.active_traits
            for trait in traits:
                if hasattr(trait, 'apply_passive_effect'):
                    trait.apply_passive_effect(character)
        
        # 장비 패시브 효과 적용
        if hasattr(character, 'equipment_effects'):
            for effect in character.equipment_effects:
                if effect['type'] == 'hp_regen' and random.random() < 0.3:  # 30% 확률로 턴마다 회복
                    character.current_hp = min(character.limited_max_hp, 
                                             character.current_hp + effect['value'])
                elif effect['type'] == 'mp_regen' and random.random() < 0.3:
                    character.current_mp = min(character.max_mp, 
                                             character.current_mp + effect['value'])
    
    def apply_turn_based_effects(self):
        """턴 기반 효과 적용 (패시브, 버프, 디버프 등)"""
        for member in self.party_manager.members:
            if not member.is_alive:
                continue
            
            # 패시브 효과 업데이트
            self.apply_character_passives(member)
            
            # 임시 버프 감소
            if hasattr(member, 'temporary_buffs'):
                expired_buffs = []
                for buff_type, buff_data in member.temporary_buffs.items():
                    buff_data['duration'] -= 1
                    if buff_data['duration'] <= 0:
                        expired_buffs.append(buff_type)
                        # 버프 효과 제거
                        self.remove_temporary_buff(member, buff_type, buff_data)
                
                # 만료된 버프 제거
                for buff_type in expired_buffs:
                    del member.temporary_buffs[buff_type]
                    print(f"⏰ {member.name}의 {buff_data['name']} 버프가 종료되었습니다.")
            
            # 상태이상 턴 감소
            if hasattr(member, 'status_effects') and member.status_effects:
                expired_effects = []
                for effect in member.status_effects:
                    if hasattr(effect, 'duration'):
                        effect.duration -= 1
                        if effect.duration <= 0:
                            expired_effects.append(effect)
                
                # 만료된 상태이상 제거
                for effect in expired_effects:
                    member.status_effects.remove(effect)
                    print(f"⏰ {member.name}의 {effect.name} 상태가 종료되었습니다.")
    
    def remove_temporary_buff(self, character, buff_type, buff_data):
        """임시 버프 효과 제거"""
        value = buff_data['value']
        
        if buff_type == "buff_attack":
            character.physical_attack = max(0, character.physical_attack - value)
        elif buff_type == "buff_defense":
            character.physical_defense = max(0, character.physical_defense - value)
        elif buff_type == "buff_speed":
            character.speed = max(1, character.speed - value)
            character.atb_speed = character.speed
        elif buff_type == "buff_magic":
            character.magic_attack = max(0, character.magic_attack - value)
    
    def select_party_member_for_equipment(self, item, current_owner):
        """장비 아이템을 장착할 파티원 선택"""
        while True:
            print(f"\n{bright_white('📦 장비 장착', True)} - {item.get_colored_name()}")
            print(f"현재 소유자: {cyan(current_owner.name)}")
            
            if item.stats:
                stats_str = ", ".join([f"{k}: {bright_green(f'+{v}')}" for k, v in item.stats.items()])
                print(f"효과: {stats_str}")
            
            print(f"\n{bright_white('장착할 파티원을 선택하세요:', True)}")
            
            alive_members = self.party_manager.get_alive_members()
            for i, member in enumerate(alive_members, 1):
                # 현재 해당 슬롯에 장착된 아이템 확인
                equipped_items = member.get_equipped_items()
                current_equipped = None
                
                if item.item_type.value == "무기":
                    current_equipped = equipped_items["무기"]
                elif item.item_type.value == "방어구":
                    current_equipped = equipped_items["방어구"]
                elif item.item_type.value == "장신구":
                    current_equipped = equipped_items["장신구"]
                
                equipped_info = f" (현재: {current_equipped.name})" if current_equipped else " (빈 슬롯)"
                status_icon = "💀" if not member.is_alive else "✨"
                
                print(f"{i}. {status_icon} {member.name}{equipped_info}")
            
            print(f"{len(alive_members)+1}. {red('취소')}")
            
            choice = self.keyboard.get_key()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(alive_members):
                    target_member = alive_members[choice_num - 1]
                    self.sound_manager.play_sfx("menu_select")
                    self.equip_item_to_member(item, current_owner, target_member)
                    break
                elif choice_num == len(alive_members) + 1:
                    self.sound_manager.play_sfx("menu_cancel")
                    break
                else:
                    self.sound_manager.play_sfx("menu_error")
            else:
                self.sound_manager.play_sfx("menu_error")
    
    def equip_item_to_member(self, item, current_owner, target_member):
        """선택된 파티원에게 아이템 장착"""
        # 장착 가능 여부 먼저 확인
        slot_name = item.item_type.value
        if slot_name not in ["무기", "방어구", "장신구"]:
            print(f"❌ {item.name}은(는) 장착할 수 없는 아이템입니다.")
            self.sound_manager.play_sfx("menu_error")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            return
        
        # 기존 장착 아이템 확인
        old_item = None
        if slot_name == "무기":
            old_item = target_member.equipped_weapon
        elif slot_name == "방어구":
            old_item = target_member.equipped_armor
        elif slot_name == "장신구":
            old_item = target_member.equipped_accessory
        
        # 인벤토리 공간 확인 (기존 아이템이 있을 때만)
        if old_item:
            can_add, reason = current_owner.inventory.can_add_item(old_item)
            if not can_add:
                print(f"❌ {current_owner.name}의 인벤토리에 {old_item.name}을(를) 보관할 수 없습니다: {reason}")
                self.sound_manager.play_sfx("menu_error")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                return
        
        # 아이템이 어느 인벤토리에 있는지 확인하고 제거
        item_removed = False
        
        # 1. 개인 인벤토리에서 먼저 찾기
        if current_owner.inventory.has_item(item.name):
            if current_owner.inventory.remove_item(item.name, 1):
                item_removed = True
                print(f"📦 {current_owner.name}의 개인 인벤토리에서 {item.name}을(를) 가져왔습니다.")
        
        # 2. 개인 인벤토리에 없으면 공용 인벤토리에서 찾기
        if not item_removed and hasattr(self.party_manager, 'shared_inventory'):
            if self.party_manager.shared_inventory.has_item(item.name):
                if self.party_manager.shared_inventory.remove_item(item.name, 1):
                    item_removed = True
                    print(f"📦 파티 공용 인벤토리에서 {item.name}을(를) 가져왔습니다.")
        
        # 3. 어디에서도 찾을 수 없으면 오류
        if not item_removed:
            print(f"❌ {item.name}을(를) 어느 인벤토리에서도 찾을 수 없습니다.")
            self.sound_manager.play_sfx("menu_error")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            return
        
        # 기존 아이템이 있다면 장착 해제 및 인벤토리 이동
        if old_item:
            # 기존 아이템 효과 제거
            self.remove_equipment_effects(target_member, old_item)
            # 장착 해제
            target_member.unequip_item(slot_name)
            
            # 기존 아이템을 적절한 인벤토리에 추가
            if current_owner.inventory.can_add_item(old_item)[0]:
                current_owner.inventory.add_item(old_item)
                print(f"📦 {old_item.name}을(를) {current_owner.name}의 인벤토리로 이동했습니다.")
            elif hasattr(self.party_manager, 'shared_inventory'):
                self.party_manager.shared_inventory.add_item(old_item.name, 1)
                print(f"📦 {old_item.name}을(를) 파티 공용 인벤토리로 이동했습니다.")
            else:
                print(f"⚠️ 인벤토리가 가득 차서 {old_item.name}을(를) 버렸습니다.")
        
        # 새 아이템 장착
        if target_member.equip_item(item):
            print(f"✅ {target_member.name}이(가) {item.name}을(를) 장착했습니다!")
            # 장비 장착 효과음
            self.sound_manager.play_sfx("equip")
            # 장비 효과 적용
            self.apply_equipment_effects(target_member, item)
        else:
            # 장착 실패 시 아이템을 적절한 인벤토리에 돌려줌
            if current_owner.inventory.can_add_item(item)[0]:
                current_owner.inventory.add_item(item)
                print(f"❌ {item.name}을(를) 장착할 수 없습니다. {current_owner.name}의 인벤토리로 반환했습니다.")
            elif hasattr(self.party_manager, 'shared_inventory'):
                self.party_manager.shared_inventory.add_item(item.name, 1)
                print(f"❌ {item.name}을(를) 장착할 수 없습니다. 파티 공용 인벤토리로 반환했습니다.")
            else:
                print(f"❌ {item.name}을(를) 장착할 수 없습니다.")
            self.sound_manager.play_sfx("menu_error")
        
        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def apply_equipment_effects(self, character, item):
        """장비 효과 적용 (개선된 버전)"""
        if not item or not hasattr(item, 'stats'):
            return
        
        print(f"⚡ {character.name}에게 {item.name}의 효과를 적용합니다...")
        
        # 기본 스탯 효과
        if item.stats:
            applied_effects = []
            for stat, value in item.stats.items():
                if stat == "physical_attack":
                    character.physical_attack += value
                    applied_effects.append(f"물리공격력 +{value}")
                elif stat == "magic_attack":
                    character.magic_attack += value
                    applied_effects.append(f"마법공격력 +{value}")
                elif stat == "physical_defense":
                    character.physical_defense += value
                    applied_effects.append(f"물리방어력 +{value}")
                elif stat == "magic_defense":
                    character.magic_defense += value
                    applied_effects.append(f"마법방어력 +{value}")
                elif stat == "speed":
                    character.speed += value
                    character.atb_speed = character.speed
                    applied_effects.append(f"속도 +{value}")
                elif stat == "max_hp":
                    character.max_hp += value
                    character.update_limited_max_hp()  # 제한 최대 HP 업데이트
                    applied_effects.append(f"최대HP +{value}")
                elif stat == "max_mp":
                    character.max_mp += value
                    applied_effects.append(f"최대MP +{value}")
                elif stat == "accuracy":
                    if not hasattr(character, 'accuracy_bonus'):
                        character.accuracy_bonus = 0
                    character.accuracy_bonus += value
                    applied_effects.append(f"명중률 +{value}%")
                elif stat == "critical_rate":
                    if not hasattr(character, 'critical_rate_bonus'):
                        character.critical_rate_bonus = 0
                    character.critical_rate_bonus += value
                    applied_effects.append(f"치명타율 +{value}%")
                elif stat == "dodge_rate":
                    if not hasattr(character, 'dodge_rate_bonus'):
                        character.dodge_rate_bonus = 0
                    character.dodge_rate_bonus += value
                    applied_effects.append(f"회피율 +{value}%")
            
            if applied_effects:
                print(f"  📈 능력치 증가: {', '.join(applied_effects)}")
        
        # 특수 효과 적용
        if hasattr(item, 'special_effects') and item.special_effects:
            self.apply_special_equipment_effects(character, item.special_effects)
        
        # 장비별 고유 효과
        self.apply_unique_equipment_effects(character, item)
    
    def apply_special_equipment_effects(self, character, special_effects):
        """특수 장비 효과 적용"""
        if not hasattr(character, 'equipment_effects'):
            character.equipment_effects = []
        
        for effect in special_effects:
            effect_type = effect.get('type', '')
            effect_value = effect.get('value', 0)
            
            if effect_type == "hp_regeneration":
                character.equipment_effects.append({
                    'type': 'hp_regen',
                    'value': effect_value,
                    'description': f"턴마다 HP {effect_value} 회복"
                })
                print(f"  🔄 HP 재생 효과: 턴마다 {effect_value} 회복")
            
            elif effect_type == "mp_regeneration":
                character.equipment_effects.append({
                    'type': 'mp_regen',
                    'value': effect_value,
                    'description': f"턴마다 MP {effect_value} 회복"
                })
                print(f"  🔄 MP 재생 효과: 턴마다 {effect_value} 회복")
            
            elif effect_type == "damage_reflection":
                character.equipment_effects.append({
                    'type': 'reflect_damage',
                    'value': effect_value,
                    'description': f"받은 피해의 {effect_value}% 반사"
                })
                print(f"  🛡️ 피해 반사: {effect_value}%")
            
            elif effect_type == "element_resistance":
                element = effect.get('element', 'all')
                character.equipment_effects.append({
                    'type': 'element_resist',
                    'element': element,
                    'value': effect_value,
                    'description': f"{element} 속성 저항 +{effect_value}%"
                })
                print(f"  🛡️ {element} 속성 저항 +{effect_value}%")
            
            elif effect_type == "status_immunity":
                status = effect.get('status', '')
                character.equipment_effects.append({
                    'type': 'status_immune',
                    'status': status,
                    'description': f"{status} 상태이상 면역"
                })
                print(f"  🛡️ {status} 상태이상 면역")
    
    def apply_unique_equipment_effects(self, character, item):
        """장비별 고유 효과 적용"""
        item_name = item.name.lower()
        
        # 검류 특수 효과
        if "검" in item.name:
            if "화염" in item.name:
                self.add_weapon_element_effect(character, "화염", "공격 시 화상 확률")
            elif "얼음" in item.name:
                self.add_weapon_element_effect(character, "얼음", "공격 시 빙결 확률")
            elif "번개" in item.name:
                self.add_weapon_element_effect(character, "번개", "공격 시 마비 확률")
            elif "독" in item.name:
                self.add_weapon_element_effect(character, "독", "공격 시 중독 확률")
        
        # 방어구 특수 효과
        elif "갑옷" in item.name or "로브" in item.name:
            if "마법" in item.name:
                self.add_armor_effect(character, "magic_protection", "마법 피해 감소")
            elif "물리" in item.name:
                self.add_armor_effect(character, "physical_protection", "물리 피해 감소")
            elif "신성" in item.name:
                self.add_armor_effect(character, "holy_protection", "상태이상 저항")
        
        # 장신구 특수 효과
        elif "반지" in item.name or "목걸이" in item.name or "팔찌" in item.name:
            if "행운" in item.name:
                self.add_accessory_effect(character, "luck_boost", "아이템 드랍률 증가")
            elif "경험치" in item.name:
                self.add_accessory_effect(character, "exp_boost", "경험치 획득량 증가")
            elif "마나" in item.name:
                self.add_accessory_effect(character, "mana_efficiency", "MP 소모량 감소")
    
    def add_weapon_element_effect(self, character, element, description):
        """무기 속성 효과 추가"""
        if not hasattr(character, 'weapon_effects'):
            character.weapon_effects = []
        
        character.weapon_effects.append({
            'type': 'element_attack',
            'element': element,
            'chance': 25,  # 25% 확률
            'description': description
        })
        print(f"  ⚔️ {description} (25% 확률)")
    
    def add_armor_effect(self, character, effect_type, description):
        """방어구 효과 추가"""
        if not hasattr(character, 'armor_effects'):
            character.armor_effects = []
        
        character.armor_effects.append({
            'type': effect_type,
            'value': 15,  # 15% 효과
            'description': description
        })
        print(f"  🛡️ {description} (15% 효과)")
    
    def add_accessory_effect(self, character, effect_type, description):
        """장신구 효과 추가"""
        if not hasattr(character, 'accessory_effects'):
            character.accessory_effects = []
        
        character.accessory_effects.append({
            'type': effect_type,
            'value': 20,  # 20% 효과
            'description': description
        })
        print(f"  💍 {description} (20% 효과)")
    
    def remove_equipment_effects(self, character, item):
        """장비 효과 제거 (개선된 버전)"""
        if not item or not hasattr(item, 'stats'):
            return
        
        print(f"⚡ {character.name}에게서 {item.name}의 효과를 제거합니다...")
        
        # 기본 스탯 효과 제거
        if item.stats:
            removed_effects = []
            for stat, value in item.stats.items():
                if stat == "physical_attack":
                    character.physical_attack = max(0, character.physical_attack - value)
                    removed_effects.append(f"물리공격력 -{value}")
                elif stat == "magic_attack":
                    character.magic_attack = max(0, character.magic_attack - value)
                    removed_effects.append(f"마법공격력 -{value}")
                elif stat == "physical_defense":
                    character.physical_defense = max(0, character.physical_defense - value)
                    removed_effects.append(f"물리방어력 -{value}")
                elif stat == "magic_defense":
                    character.magic_defense = max(0, character.magic_defense - value)
                    removed_effects.append(f"마법방어력 -{value}")
                elif stat == "speed":
                    character.speed = max(1, character.speed - value)
                    character.atb_speed = character.speed
                    removed_effects.append(f"속도 -{value}")
                elif stat == "max_hp":
                    character.max_hp = max(1, character.max_hp - value)
                    character.current_hp = min(character.current_hp, character.max_hp)
                    character.update_limited_max_hp()
                    removed_effects.append(f"최대HP -{value}")
                elif stat == "max_mp":
                    character.max_mp = max(0, character.max_mp - value)
                    character.current_mp = min(character.current_mp, character.max_mp)
                    removed_effects.append(f"최대MP -{value}")
                elif stat == "accuracy":
                    if hasattr(character, 'accuracy_bonus'):
                        character.accuracy_bonus = max(0, character.accuracy_bonus - value)
                    removed_effects.append(f"명중률 -{value}%")
                elif stat == "critical_rate":
                    if hasattr(character, 'critical_rate_bonus'):
                        character.critical_rate_bonus = max(0, character.critical_rate_bonus - value)
                    removed_effects.append(f"치명타율 -{value}%")
                elif stat == "dodge_rate":
                    if hasattr(character, 'dodge_rate_bonus'):
                        character.dodge_rate_bonus = max(0, character.dodge_rate_bonus - value)
                    removed_effects.append(f"회피율 -{value}%")
            
            if removed_effects:
                print(f"  📉 능력치 감소: {', '.join(removed_effects)}")
        
        # 특수 효과 제거
        self.remove_special_equipment_effects(character, item)
    
    def remove_special_equipment_effects(self, character, item):
        """특수 장비 효과 제거"""
        # 장비 효과 리스트에서 해당 아이템의 효과 제거
        if hasattr(character, 'equipment_effects'):
            character.equipment_effects = [
                effect for effect in character.equipment_effects 
                if not self.is_effect_from_item(effect, item)
            ]
        
        # 무기/방어구/장신구 효과 제거
        if hasattr(character, 'weapon_effects'):
            character.weapon_effects.clear()
        if hasattr(character, 'armor_effects'):
            character.armor_effects.clear()
        if hasattr(character, 'accessory_effects'):
            character.accessory_effects.clear()
        
        print(f"  🔄 특수 효과가 제거되었습니다.")
    
    def is_effect_from_item(self, effect, item):
        """효과가 특정 아이템에서 온 것인지 확인 (간단한 구현)"""
        # 더 정교한 추적이 필요하다면 아이템별 고유 ID 시스템 도입 가능
        return True  # 현재는 단순하게 모든 효과 제거
        
    def show_party_status(self):
        """파티 상태 표시 (요리 버프 및 적응형 밸런스 포함)"""
        from game.field_cooking import get_field_cooking_interface
        
        # 기본 파티 상태 표시
        self.display.show_party_status(self.party_manager)
        
        # 요리 버프 상태 추가 표시
        field_cooking = get_field_cooking_interface(self.party_manager)
        field_cooking.cooking_system.show_active_buffs()
        
        # 🎯 적응형 밸런스 정보 표시
        if hasattr(self, 'adaptive_balance') and self.adaptive_balance:
            performance_summary = self.adaptive_balance.get_performance_summary()
            if performance_summary['total_battles'] > 0:
                print(f"\n{bright_cyan('🎯 적응형 난이도 시스템', True)}")
                print(f"현재 난이도: {performance_summary['difficulty']}")
                print(f"플레이어 레벨: {cyan(performance_summary['skill_level'].replace('_', ' ').title())}")
                win_rate_text = f"{performance_summary['win_rate']:.1%}"
                print(f"승률: {bright_green(win_rate_text)}")
                if performance_summary['total_battles'] >= 5:
                    score_text = f"{performance_summary['average_recent_score']:.1f}/100"
                    print(f"최근 성과: {yellow(score_text)}")
                print("="*50)
        
    def show_field_item_menu(self):
        """필드 아이템 사용 메뉴"""
        from game.field_item_system import get_field_item_system
        
        field_item_system = get_field_item_system()
        
        try:
            # 필드 아이템 메뉴 표시
            used = field_item_system.show_field_item_menu(self.party_manager)
            
            if used:
                print(f"\n{bright_green('✅ 아이템을 사용했습니다!', True)}")
                self.sound_manager.play_sfx("item_use")
                
                # 아이템 사용 후 파티 상태 업데이트
                self.display.show_party_status(self.party_manager)
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            else:
                print(f"\n{yellow('취소되었습니다.')}")
                
        except Exception as e:
            print(f"❌ 필드 아이템 시스템 오류: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def show_field_skill_menu(self):
        """필드 스킬 및 요리 메뉴"""
        from game.field_skill_selector import get_field_skill_selector
        from game.field_cooking import get_field_cooking_interface
        
        # 필드 스킬 선택기 가져오기
        field_skill_selector = get_field_skill_selector()
        field_cooking = get_field_cooking_interface(self.party_manager)
        
        while True:
            print("\n" + "="*70)
            print(f"{bright_cyan('⚡ 필드 활동 메뉴', True)}")
            print("="*70)
            
            # 파티 상태 간단 표시
            print(f"\n{bright_white('파티 상태:', True)}")
            for member in self.party_manager.get_alive_members():
                print(f"  {member.get_status_string()}")
            
            print(f"\n{bright_white('📋 활동 선택:', True)}")
            print(f"{green('1.')} ⚡ 필드 스킬 사용")
            print(f"{green('2.')} 🍳 요리 & 채집")
            print(f"{red('0.')} 🚪 나가기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == '0':
                self.sound_manager.play_sfx("menu_cancel")
                break
            elif choice == '1':
                self._show_field_skills_submenu(field_skill_selector)
            elif choice == '2':
                field_cooking.show_cooking_menu()
            else:
                print(f"{red('❌ 잘못된 선택입니다.')}")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def _show_field_skills_submenu(self, field_skill_selector):
        """필드 스킬 서브메뉴"""
        while True:
            print("\n" + "="*70)
            print(f"{bright_cyan('⚡ 필드 스킬 사용', True)}")
            print("="*70)
            
            # 사용 가능한 필드 스킬 목록
            available_skills = field_skill_selector.get_available_skills(self.party_manager)
            
            if not available_skills:
                print(f"\n{red('❌ 현재 사용할 수 있는 필드 스킬이 없습니다.')}")
                print(f"{yellow('💡 파티원의 MP가 부족하거나 쿨다운 중일 수 있습니다.')}")
                self.keyboard.wait_for_key("아무 키나 눌러 돌아가기...")
                break
            
            print(f"\n{bright_white('🎯 사용 가능한 필드 스킬:', True)}")
            
            skill_choices = []
            for i, skill_id in enumerate(available_skills, 1):
                skill_info = field_skill_selector.field_skills[skill_id]
                capable_members = field_skill_selector.get_capable_members(self.party_manager, skill_id)
                
                print(f"\n{bright_white(f'{i}.')} {skill_info['name']}")
                print(f"   {skill_info['description']}")
                print(f"   💙 MP 소모: {cyan(str(skill_info['mp_cost']))} | ⏰ 쿨다운: {skill_info['cooldown']}턴")
                
                # 사용 가능한 시전자 표시
                caster_names = [f"{green(member.name)}" for member in capable_members]
                print(f"   👥 사용 가능: {', '.join(caster_names)}")
                
                skill_choices.append(skill_id)
            
            print(f"\n{red('0.')} 돌아가기")
            
            print(f"\n{bright_white('명령:', True)}")
            print(f"{yellow('(1-N)')} 필드 스킬 사용  {red('(0)')} 돌아가기")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == '0':
                self.sound_manager.play_sfx("menu_cancel")
                break
            elif choice.isdigit():
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(skill_choices):
                        skill_id = skill_choices[choice_num - 1]
                        self.sound_manager.play_sfx("menu_select")
                        
                        # 필드 스킬 사용
                        result = field_skill_selector.use_field_skill(
                            self.party_manager, 
                            skill_id, 
                            world=self.world
                        )
                        
                        if result["success"]:
                            print(f"\n{green('✅ 성공!')}")
                            print(result["message"])
                            
                            # 성공시 시간 경과 효과
                            self.steps_since_last_encounter += 1
                            
                        else:
                            print(f"\n{red('❌ 실패!')}")
                            print(result["message"])
                            self.sound_manager.play_sfx("menu_error")
                        
                        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                    else:
                        self.sound_manager.play_sfx("menu_error")
                        print(f"{red('❌ 잘못된 선택입니다.')}")
                except ValueError:
                    self.sound_manager.play_sfx("menu_error")
                    print(f"{red('❌ 숫자를 입력해주세요.')}")
            else:
                self.sound_manager.play_sfx("menu_error")
                print(f"{red('❌ 잘못된 입력입니다.')}")
        
    def start_combat(self, enemy_pos: Tuple[int, int] = None):
        """전투 시작 - 고급 시스템 통합"""
        print("\n적과 마주쳤습니다!")
        
        # 전투 전 패시브 효과 업데이트
        self.update_passive_effects()
        
        # 🎮 게임 상태 변경
        self.game_manager.change_state(GameState.PLAYING)
        
        # 적 생성 (위치 기반 고정 씨드)
        enemies = self.create_enemies(enemy_pos)
        
        # 🤖 각 적에게 스마트 AI 부여
        for i, enemy in enumerate(enemies):
            enemy_type = getattr(enemy, 'enemy_type', 'default')
            enemy_id = f"enemy_{i}_{random.randint(1000, 9999)}"  # time 대신 랜덤 ID 사용
            enemy_ai = self.game_manager.create_enemy_ai(enemy_id, enemy_type)
            enemy.ai = enemy_ai  # AI 연결
        
        # 🔊 전투 시작 사운드 및 BGM
        from game.audio_system import play_battle_start_sfx, play_battle_bgm, play_boss_bgm
        play_battle_start_sfx()
        
        # 보스 전투인지 확인 (적 중에 보스가 있는지)
        is_boss_battle = any(hasattr(enemy, 'rank') and enemy.rank in ['보스', '전설'] for enemy in enemies)
        if is_boss_battle:
            play_boss_bgm()
        else:
            play_battle_bgm()
        
        # ✨ 전투 시작 파티클 효과
        if enemy_pos:
            self.game_manager.ui_system.create_particle_burst(
                enemy_pos[0] * 40, enemy_pos[1] * 40,  # 화면 좌표로 변환
                ParticleType.SPARK, 15
            )
        
        # 💡 파티 AI 조언 받기
        party_members = self.party_manager.get_alive_members()
        battle_state = {
            'enemies': enemies,
            'current_floor': self.world.current_level,
            'party_health_ratio': sum(m.current_hp / m.max_hp for m in party_members) / len(party_members)
        }
        party_suggestion = self.game_manager.get_party_ai_suggestion(party_members, enemies, battle_state)
        
        # 전투 진행
        result = self.combat_manager.start_combat(party_members, enemies)
        
        # 🎯 전투 결과에 따른 고급 시스템 처리
        if result:  # 승리
            # 💰 승리 통계 업데이트
            for enemy in enemies:
                self.game_manager.handle_combat_event("enemy_defeated", {
                    'enemy_type': getattr(enemy, 'enemy_type', 'default'),
                    'enemy_id': getattr(enemy, 'ai', None) and enemy.ai and hasattr(enemy.ai, 'personality'),
                    'position': enemy_pos or self.world.player_pos,
                    'difficulty': self.game_manager.balance_system.current_difficulty.value
                })
            
            # 🔊 승리 사운드 & BGM
            from game.audio_system import play_victory_bgm
            self.sound_manager.play_sfx("victory")
            play_victory_bgm()  # audio_system의 함수 사용
            
            # 🎵 승리 BGM이 재생되도록 잠시 대기
            import time
            time.sleep(1.5)  # 1.5초 대기하여 승리 BGM을 들을 수 있게 함
            
            # ✨ 승리 파티클
            victory_pos = enemy_pos or self.world.player_pos
            self.game_manager.ui_system.create_particle_burst(
                victory_pos[0] * 40, victory_pos[1] * 40,
                ParticleType.STAR, 20
            )
            
            # 📍 맵에서 적 제거 및 플레이어 이동
            if enemy_pos:
                self.world.remove_enemy(enemy_pos)
                self.world.player_pos = enemy_pos
                self.world.update_visibility()
            else:
                self.world.remove_enemy(self.world.player_pos)
            
            # 📊 통계 업데이트
            self.enemies_defeated += 1
            
            # 💎 전리품 드롭 (확률은 밸런스 시스템이 조정) - 위치 기반 고정 씨드
            enemy_pos_seed = hash(f"combat_drop_{self.world.current_level}_{enemy_pos}") % (2**32) if enemy_pos else hash(f"combat_drop_{self.world.current_level}_{self.world.player_pos}") % (2**32)
            random.seed(enemy_pos_seed)
            
            loot_chance = 0.4 * self.game_manager.balance_system.get_loot_modifier()
            if random.random() < loot_chance:
                from game.items import ItemDatabase
                dropped_items = ItemDatabase.get_random_loot(self.world.current_level, 1)
                for item in dropped_items:
                    drop_pos = self.world.player_pos
                    self.world.floor_items[drop_pos] = item
                    if drop_pos not in self.world.items_positions:
                        self.world.items_positions.append(drop_pos)
                        self.world.tiles[drop_pos[1]][drop_pos[0]].has_item = True
                    
                    # 💰 아이템 획득 이벤트
                    self.game_manager.handle_exploration_event("treasure_found", {
                        'item': item,
                        'position': drop_pos
                    })
                    
                    print(f"💎 {item.get_colored_name()}이(가) 떨어졌습니다!")
            
            # 💫 전투 승리 결과 표시 및 팡파레
            self._show_victory_fanfare_and_summary(enemies)
            
            # 🥕 식재료 드롭 체크
            self._handle_ingredient_drops(enemies)
            
            # NOTE: 경험치 부여는 _show_victory_fanfare_and_summary()에서 처리됨
            
            input(f"\n{bright_white('전투 결과를 확인하셨습니다. 계속하려면 Enter를 누르세요...', True)}")
            
            # 🎵 던전 BGM으로 복귀
            from game.audio_system import set_floor_bgm
            current_floor = getattr(self.world, 'current_level', 1)
            set_floor_bgm(current_floor)
        
        else:  # 패배
            # 🎯 적응형 밸런스 시스템에 패배 기록
            if hasattr(self, 'adaptive_balance') and self.adaptive_balance:
                alive_party = [m for m in self.party_manager.members if m.is_alive]
                avg_hp_remaining = sum(m.current_hp / m.limited_max_hp for m in alive_party) / len(self.party_manager.members)
                
                battle_duration = 30.0  # 기본값
                damage_taken = sum(m.limited_max_hp - m.current_hp for m in self.party_manager.members)
                damage_dealt = 0  # 패배 시 적에게 준 피해량 추정 필요
                
                self.adaptive_balance.record_battle_result(
                    won=False,
                    player_hp_remaining=avg_hp_remaining,
                    battle_duration=battle_duration,
                    damage_dealt=damage_dealt,
                    damage_taken=damage_taken,
                    items_used=0
                )
            
            # 💀 패배 사운드
            self.game_manager.sound_system.play_sfx("defeat")
            
            # 🎵 게임 오버 BGM
            self.game_manager.sound_system.play_bgm("game_over", loop=False)
            
            # 💥 패배 파티클
            defeat_pos = enemy_pos or self.world.player_pos
            self.game_manager.ui_system.create_particle_burst(
                defeat_pos[0] * 40, defeat_pos[1] * 40,
                ParticleType.BLOOD, 25
            )
            
            # 📊 패배 통계
            final_stats = {
                'survival_time': time.time() - float(str(self.game_manager.game_data['session_start'])),
                'enemies_defeated': self.enemies_defeated,
                'floor_reached': self.world.current_level
            }
            
            # 🎮 게임 오버 처리
            self.game_manager.change_state(GameState.GAME_OVER, final_stats=final_stats)
            
            # 💀 전투 패배 결과 표시 및 일시정지
            print(f"\n{red('💀 전투 패배...', True)}")
            print("파티가 전멸했습니다.")
            input(f"\n{bright_white('게임 오버 화면을 확인하셨습니다. 계속하려면 Enter를 누르세요...', True)}")
        
        # 전투 종료 후 공통 처리
        print(f"\n{cyan('전투가 종료되었습니다.')}")
        
        # 🔊 필드 BGM으로 복귀
        from game.audio_system import set_floor_bgm
        current_floor = getattr(self.world, 'current_level', 1)
        set_floor_bgm(current_floor)
        
        # 전투 후 조우 쿨타임 적용 (20걸음 추가)
        self.steps_since_last_encounter = max(self.steps_since_last_encounter, -20)
        
        
    def create_enemies(self, enemy_pos: Tuple[int, int] = None) -> List[Character]:
        """적 생성 - enemy_system.py 사용 (위치 기반 고정 씨드)"""
        try:
            from game.enemy_system import get_enemy_manager
            enemy_manager = get_enemy_manager()
            
            # 위치 기반 고정 씨드 설정 (같은 위치에서는 항상 같은 적)
            if enemy_pos:
                enemy_seed = hash(f"enemy_{self.world.current_level}_{enemy_pos[0]}_{enemy_pos[1]}") % (2**32)
            else:
                enemy_seed = hash(f"enemy_{self.world.current_level}_{self.world.player_pos[0]}_{self.world.player_pos[1]}") % (2**32)
            random.seed(enemy_seed)
            
            # 현재 층수에 맞는 적들 생성
            current_floor = getattr(self.world, 'current_level', 1)
            enemy_group = enemy_manager.spawn_encounter(current_floor, len(self.party_manager.members))
            
            # Enemy 객체를 Character 객체로 변환
            enemies = []
            for enemy in enemy_group:
                # Character 객체 생성
                character = Character(
                    name=f"Lv.{enemy.level} {enemy.name}",
                    character_class="Enemy",
                    max_hp=enemy.max_hp,
                    physical_attack=enemy.physical_attack,
                    magic_attack=enemy.magic_attack,
                    physical_defense=enemy.physical_defense,
                    magic_defense=enemy.magic_defense,
                    speed=enemy.speed
                )
                
                # 레벨과 Brave 스탯 설정
                character.level = enemy.level
                character.experience = 0
                
                # Brave 스탯 설정
                character.int_brv = getattr(enemy, 'current_brv', 400)
                character.max_brv = getattr(enemy, 'max_brv', 2000)
                character.brave_points = character.int_brv
                character.brv_efficiency = 0.8
                character.brv_loss_resistance = 0.9
                
                enemies.append(character)
            
            return enemies
            
        except Exception as e:
            print(f"⚠️ Enemy 시스템 사용 실패, 기본 적 생성: {e}")
            # 기본 적 생성 로직 (fallback)
            return self._create_basic_enemies()
    
    def _create_basic_enemies(self) -> List[Character]:
        """기본 적 생성 (fallback) - enemy_system.py 사용"""
        try:
            # enemy_system.py를 다시 시도
            from game.enemy_system import get_enemy_manager
            enemy_manager = get_enemy_manager()
            
            current_floor = getattr(self.world, 'current_level', 1)
            enemy_group = enemy_manager.spawn_encounter(current_floor, len(self.party_manager.members))
            
            # Enemy 객체를 Character 객체로 변환
            enemies = []
            for enemy in enemy_group:
                character = Character(
                    name=f"Lv.{enemy.level} {enemy.name}",
                    character_class="Enemy",
                    max_hp=enemy.max_hp,
                    physical_attack=enemy.physical_attack,
                    magic_attack=enemy.magic_attack,
                    physical_defense=enemy.physical_defense,
                    magic_defense=enemy.magic_defense,
                    speed=enemy.speed
                )
                
                # AI 시스템 연결
                character.ai = enemy.ai
                character.level = enemy.level
                enemies.append(character)
            
            print(f"🎯 enemy_system.py로 {len(enemies)}마리 적 생성 성공 (fallback)")
            return enemies
            
        except Exception as e:
            print(f"⚠️ fallback에서도 enemy_system 실패: {e}")
            # 최후의 fallback - 간단한 적 하나만 생성
            return self._create_emergency_enemy()
    
    def _create_emergency_enemy(self) -> List[Character]:
        """응급 적 생성 (최후의 fallback)"""
        current_floor = getattr(self.world, 'current_level', 1)
        enemy_level = max(1, current_floor + random.randint(-1, 2))
        
        # 현재 층수에 맞는 단순한 적 생성
        enemy = Character(
            name=f"Lv.{enemy_level} 적",
            character_class="Enemy",
            max_hp=60 + (enemy_level * 15),
            physical_attack=15 + (enemy_level * 3),
            magic_attack=10 + (enemy_level * 2),
            physical_defense=12 + (enemy_level * 2),
            magic_defense=10 + (enemy_level * 2),
            speed=12 + enemy_level
        )
        enemy.level = enemy_level
        
        print(f"⚠️ 응급 적 생성: {enemy.name}")
        return [enemy]
    
    def _show_victory_fanfare_and_summary(self, enemies: List[Character]):
        """승리 팡파레 및 정산 표시"""
        import time
        from game.audio_system import play_victory_bgm
        
        # � 적응형 밸런스 시스템에 승리 기록
        if hasattr(self, 'adaptive_balance') and self.adaptive_balance:
            alive_party = [m for m in self.party_manager.members if m.is_alive]
            avg_hp_remaining = sum(m.current_hp / m.limited_max_hp for m in alive_party) / len(alive_party) if alive_party else 0.0
            
            # 전투 지속 시간 추정 (간단한 추정)
            battle_duration = 30.0  # 기본값, 실제로는 전투 시작 시간을 기록해야 함
            
            # 피해량 추정 (최대 HP - 현재 HP)
            damage_taken = sum(m.limited_max_hp - m.current_hp for m in self.party_manager.members)
            damage_dealt = sum(getattr(enemy, 'max_hp', 100) for enemy in enemies)  # 적 최대 HP 합계로 추정
            
            self.adaptive_balance.record_battle_result(
                won=True,
                player_hp_remaining=avg_hp_remaining,
                battle_duration=battle_duration,
                damage_dealt=damage_dealt,
                damage_taken=damage_taken,
                items_used=0  # 아이템 사용량 추적 필요
            )
        
        # �🎵 승리 BGM 재생
        play_victory_bgm()
        
        # 🎉 승리 팡파레 애니메이션
        print("\n" + "="*80)
        print(f"{bright_green('🏆 VICTORY! 🏆', True)}")
        print("="*80)
        
        # 잠시 대기로 임팩트 증가
        time.sleep(0.5)
        
        print(f"\n{bright_yellow('⚔️ 전투 결과', True)}")
        print(f"🗡️  처치한 적: {cyan(str(len(enemies)))}마리")
        
        # 적별 정보 표시
        for i, enemy in enumerate(enemies, 1):
            enemy_level = getattr(enemy, 'level', 1)
            print(f"  {i}. {enemy.name} (Lv.{enemy_level})")
        
        # 🎯 경험치 계산 및 분배
        self._calculate_and_distribute_exp(enemies)
        
        # 💰 골드 획득
        gold_earned = self._calculate_gold_reward(enemies)
        if gold_earned > 0:
            print(f"\n💰 골드 획득: {bright_yellow(f'+{gold_earned}G')}")
            # 파티 골드에 추가 (파티 인벤토리가 있다면)
            if hasattr(self.party_manager, 'shared_inventory'):
                self.party_manager.shared_inventory.gold += gold_earned
        
        # 📊 파티 상태 요약
        print(f"\n{bright_cyan('👥 파티 상태', True)}")
        for member in self.party_manager.members:
            if member.is_alive:
                hp_percent = int((member.current_hp / member.max_hp) * 100)
                mp_percent = int((member.current_mp / member.max_mp) * 100) if member.max_mp > 0 else 100
                print(f"  {green('✅')} {member.name} Lv.{member.level} | HP {hp_percent}% | MP {mp_percent}%")
            else:
                print(f"  {red('💀')} {member.name} - 전투불능")
        
        print("\n" + "="*80)
        
        # 승리 대기
        time.sleep(1.0)  # 1초 대기
        
    def _calculate_and_distribute_exp(self, enemies: List[Character]):
        """경험치 계산 및 분배"""
        total_exp = 0
        for enemy in enemies:
            # 적 레벨에 따른 기하급수적 경험치 (레벨^1.5 * 20)
            enemy_level = getattr(enemy, 'level', 1)
            enemy_exp = int(enemy_level ** 1.5 * 20)
            total_exp += enemy_exp
            
        print(f"\n💫 경험치 획득: {bright_yellow(f'+{total_exp} EXP')}")
        
        # 파티원들에게 경험치 분배 (기존 character.py 시스템 사용)
        for member in self.party_manager.members:
            if member.is_alive:  # 살아있는 멤버만 경험치 획득
                print(f"  {member.name}: ", end="")
                leveled_up = member.gain_experience(total_exp)  # character.py의 기존 시스템 사용
                
                if leveled_up:
                    # 레벨업 효과음
                    self.sound_manager.play_sfx("level_up")
    
    def _calculate_gold_reward(self, enemies: List[Character]) -> int:
        """골드 보상 계산"""
        total_gold = 0
        for enemy in enemies:
            enemy_level = getattr(enemy, 'level', 1)
            # 적 레벨에 따른 골드 (레벨 * 5~15 랜덤)
            enemy_gold = enemy_level * random.randint(5, 15)
            total_gold += enemy_gold
        
        return total_gold
        
    def test_combat(self):
        """전투 테스트"""
        print("\n=== 전투 테스트 ===")
        self.start_combat()  # 테스트에서는 enemy_pos 없이 호출
        
    def quit_game(self):
        """게임 종료 (별조각 지급)"""
        # 이미 별조각을 받았는지 체크
        if hasattr(self, '_essence_already_given') and self._essence_already_given:
            print(f"\n{bright_green('게임을 종료합니다. 별빛의 여명이 함께하길!')}")
            self.running = False
            return
        
        # 영구 성장 시스템에 게임 결과 반영
        if hasattr(self, 'world') and hasattr(self, 'party_manager'):
            current_floor = getattr(self.world, 'current_floor', 0)
            total_kills = 0
            
            # 파티 전체의 처치 수 계산 (간단한 예시)
            for member in self.party_manager.members:
                # 캐릭터 레벨로 대략적인 처치 수 추정
                total_kills += (member.level - 1) * 3
            
            # 죽음 여부 확인 (모든 파티원이 죽었는지)
            died = all(member.current_hp <= 0 for member in self.party_manager.members)
            
            # 영구 성장 시스템에 기록
            self.permanent_progression.on_run_end(current_floor, total_kills, died)
            
            # 결과 표시
            print(f"\n{bright_cyan('🌟 모험 결과', True)}")
            print(f"도달 층수: {yellow(str(current_floor))}")
            print(f"처치 수: {green(str(total_kills))}")
            
            if died:
                print(red("💀 파티가 전멸했습니다..."))
            else:
                print(green("✅ 안전하게 탈출했습니다!"))
            
            # 별의 정수 획득 표시
            essence_gained = current_floor + (total_kills // 5)
            if essence_gained > 0:
                print(f"별의 정수 {bright_yellow(f'+{essence_gained}')} 획득!")
            
            # 영구 진행상황 저장
            self.permanent_progression.save_to_file()
            
            # 별조각 지급 완료 플래그 설정
            self._essence_already_given = True
        
        print(f"\n{bright_green('게임을 종료합니다. 별빛의 여명이 함께하길!')}")
        self.running = False
    
    def save_and_quit(self):
        """저장 후 종료 (별조각 지급 없음)"""
        print(f"\n{bright_cyan('💾 저장 후 모험 종료', True)}")
        
        # 게임 저장
        saved = self._save_game_silently()
        
        if saved:
            print(f"{bright_green('✅ 게임이 저장되었습니다!')}")
        else:
            print(f"{bright_red('❌ 저장에 실패했습니다.')}")
        
        # 별조각 지급 없이 종료
        print(f"\n{bright_green('게임을 종료합니다. 다음에 다시 만나요!')}")
        self.running = False
    
    def _save_game_silently(self) -> bool:
        """조용히 게임 저장 (UI 없이)"""
        try:
            game_state = GameStateSerializer.create_game_state(self)
            save_name = f"quicksave_{int(time.time())}"
            success = self.save_manager.save_game(game_state, save_name)
            return success
        except Exception as e:
            print(f"저장 오류: {e}")
            return False
    
    def save_game(self):
        """게임 저장"""
        print("\n💾 게임 저장 중...")
        try:
            print("게임 상태 생성 중...")
            game_state = GameStateSerializer.create_game_state(self)
            print(f"게임 상태 생성 완료 (레벨: {game_state.get('current_level', '?')})")
            
            print("저장 메뉴 표시 중...")
            save_name = save_system_show_save_menu(self.save_manager)
            
            if save_name == "CANCEL":
                print("저장이 취소되었습니다.")
                self.sound_manager.play_sfx("menu_cancel")
                return
            
            print(f"저장 파일명: {save_name}")
            if self.save_manager.save_game(game_state, save_name):
                print(f"{bright_green('✅ 게임이 성공적으로 저장되었습니다!', True)}")
                # 저장 성공 효과음
                self.sound_manager.play_sfx("save_game")
                input(f"\n{bright_white('저장 완료! 계속하려면 Enter를 누르세요...', True)}")
            else:
                print(f"{red('❌ 게임 저장에 실패했습니다.', True)}")
                self.sound_manager.play_sfx("menu_error")
                input(f"\n{red('저장 실패! 오류를 확인하고 계속하려면 Enter를 누르세요...', True)}")
                
        except Exception as e:
            print(f"{red('❌ 저장 중 오류가 발생했습니다:', True)} {str(e)}")
            print(f"{yellow('📋 자세한 오류 정보:', True)}")
            import traceback
            traceback.print_exc()
            self.sound_manager.play_sfx("menu_error")
            input(f"\n{red('오류 발생! 위 내용을 확인하고 계속하려면 Enter를 누르세요...', True)}")
            self.sound_manager.play_sfx("menu_error")
    
    def load_game(self):
        """게임 불러오기"""
        print("\n📁 게임 불러오는 중...")
        try:
            save_name = save_system_show_load_menu(self.save_manager)
            
            if save_name is None:
                print("불러오기가 취소되었습니다.")
                self.sound_manager.play_sfx("menu_cancel")
                return
            
            game_state = self.save_manager.load_game(save_name)
            
            if game_state is None:
                print("게임 불러오기에 실패했습니다.")
                self.sound_manager.play_sfx("menu_error")
                return
            
            # 게임 상태 복원
            self.restore_game_state(game_state)
            print("게임이 성공적으로 불러와졌습니다!")
            # 로드 성공 효과음
            self.sound_manager.play_sfx("save_ready")
            
        except Exception as e:
            print(f"불러오기 중 오류가 발생했습니다: {e}")
            self.sound_manager.play_sfx("menu_error")
    
    def restore_game_state(self, game_state: dict):
        """저장된 상태에서 게임 복원"""
        try:
            # 게임 통계 복원
            self.score = game_state.get('score', 0)
            self.enemies_defeated = game_state.get('enemies_defeated', 0)
            self.items_collected = game_state.get('items_collected', 0)
            self.floors_cleared = game_state.get('floors_cleared', 0)
            self.steps_since_last_encounter = game_state.get('steps_since_last_encounter', 0)
            
            # 월드 상태 복원
            if 'world_state' in game_state:
                world_state = game_state['world_state']
                self.world.current_level = world_state.get('current_level', 1)
                self.world.enemies_positions = world_state.get('enemies_positions', [])
                self.world.items_positions = world_state.get('items_positions', [])
                
                # 타일 상태 복원
                if 'explored_tiles' in world_state:
                    GameStateSerializer.restore_explored_tiles(self.world, world_state['explored_tiles'])
            
            # 월드 재생성 (레벨에 맞게) - 플레이어 위치 복원 전에 실행
            self.world.generate_level()
            
            # 플레이어 위치 복원 (월드 재생성 후)
            if 'player_position' in game_state:
                self.world.player_pos = tuple(game_state['player_position'])
                # 위치 복원 후 시야 업데이트
                self.world.update_visibility()
            
            # 파티 복원
            if 'party_characters' in game_state:
                self.party_manager.members = []
                for char_data in game_state['party_characters']:
                    character = GameStateSerializer.deserialize_character(char_data)
                    self.party_manager.add_member(character)
            
            print(f"레벨 {self.world.current_level} 상태로 복원되었습니다.")
            
        except Exception as e:
            print(f"게임 상태 복원 중 오류: {e}")
            raise
    
    def move_to_next_floor(self):
        """다음 층으로 이동"""
        # 🎉 층 클리어 팡파레 표시
        self._show_floor_clear_fanfare()
        
        # 다음 층 이동 여부 선택
        while True:
            print(f"\n{bright_cyan('🚪 다음 층으로 이동하시겠습니까?', True)}")
            print(f"{green('1.')} 다음 층으로 이동")
            print(f"{yellow('2.')} 현재 층에서 더 탐험")
            print(f"{red('3.')} 게임 저장 후 종료")
            
            choice = self.keyboard.get_key().lower()
            
            if choice == '1':
                break  # 다음 층으로 이동
            elif choice == '2':
                print(f"\n{bright_green('현재 층에서 탐험을 계속합니다!')}")
                return  # 함수 종료, 현재 층 유지
            elif choice == '3':
                self.save_and_quit()
                return
            else:
                print(f"{red('❌ 잘못된 선택입니다. 1, 2, 3 중에서 선택하세요.')}")
                continue
        
        # 파티 회복 (일부)
        print(f"\n{bright_cyan('⚡ 층 이동 회복', True)}")
        print("다음 층으로 이동하며 파티가 일부 회복됩니다...")
        
        recovery_summary = []
        for character in self.party_manager.members:
            if character.is_alive:
                # HP 25% 회복
                heal_amount = character.max_hp // 4
                old_hp = character.current_hp
                character.heal(heal_amount)
                actual_heal = character.current_hp - old_hp
                
                # MP 50% 회복
                mp_heal = character.max_mp // 2
                old_mp = character.current_mp
                character.current_mp = min(character.max_mp, character.current_mp + mp_heal)
                actual_mp_heal = character.current_mp - old_mp
                
                # Brave 리셋
                if hasattr(character, 'current_brave'):
                    character.current_brave = character.int_brv
                if hasattr(character, 'brave_points'):
                    character.brave_points = max(character.brave_points, character.int_brv)
                
                recovery_summary.append({
                    'name': character.name,
                    'hp_heal': actual_heal,
                    'mp_heal': actual_mp_heal,
                    'hp_percent': int((character.current_hp / character.max_hp) * 100),
                    'mp_percent': int((character.current_mp / character.max_mp) * 100) if character.max_mp > 0 else 100
                })
        
        # 회복 결과 표시
        for recovery in recovery_summary:
            print(f"  {green('✅')} {recovery['name']}: HP +{recovery['hp_heal']} ({recovery['hp_percent']}%), MP +{recovery['mp_heal']} ({recovery['mp_percent']}%)")
        
        # 다음 레벨 생성
        print(f"\n{bright_yellow('🌟 새로운 층 진입!', True)}")
        self.world.generate_next_level()
        
        # 🎵 새로운 층의 BGM 재생
        from game.audio_system import set_floor_bgm
        current_floor = getattr(self.world, 'current_level', 1)
        set_floor_bgm(current_floor)
        print(f"🎵 {current_floor}층 BGM으로 변경됩니다...")
        
        # 인카운터 카운터 강제 쿨타임 적용
        self.steps_since_last_encounter = -40
        
        # 메타 진행 업데이트
        if hasattr(self, 'meta_progression'):
            self.meta_progression.update_floors_cleared(self.floors_cleared)
        
        print(f"\n{bright_white('준비되셨나요?', True)}")
        self.keyboard.wait_for_key("🔑 아무 키나 눌러 다음 층 탐험을 계속하세요...")
    
    def _show_floor_clear_fanfare(self):
        """층 클리어 팡파레 표시"""
        import time
        from game.audio_system import play_victory_bgm
        
        # 🎵 승리 BGM 재생
        play_victory_bgm()
        
        # 층 클리어 효과음
        self.sound_manager.play_sfx("victory_fanfare")
        
        # 🎉 층 클리어 애니메이션
        print("\n" + "🌟"*30)
        print(f"{bright_green('🏆 FLOOR CLEAR! 🏆', True)}")
        print("🌟"*30)
        
        time.sleep(0.5)
        
        current_level = self.world.current_level
        print(f"\n{bright_yellow('📍 층 클리어 보고서', True)}")
        print(f"🚪 클리어한 층: {cyan(f'{current_level}층')}")
        
        # 층 클리어 보상 계산
        self.floors_cleared += 1
        floor_bonus = current_level * 100
        self.score += floor_bonus
        
        print(f"📈 클리어 보너스: {bright_yellow(f'+{floor_bonus}점')}")
        print(f"💫 총 점수: {bright_yellow(str(self.score))}점")
        print(f"📊 총 클리어 층수: {cyan(str(self.floors_cleared))}층")
        
        # 진행도 표시
        if current_level < 50:
            progress = (current_level / 50) * 100
            print(f"🎯 진행도: {cyan(f'{progress:.1f}%')} (50층 기준)")
        else:
            print(f"🎯 {bright_green('모든 층을 돌파했습니다!', True)}")
        
        print("\n" + "🌟"*30)
        
        time.sleep(1.0)  # 1초 대기
    
    def _show_available_classes(self):
        """해금된 직업 목록과 스탯 표시"""
        from game.character import CharacterClassManager
        from game.auto_party_builder import get_auto_party_builder
        
        # 해금된 직업 목록 가져오기
        available_classes = CharacterClassManager.get_all_available_classes()
        auto_builder = get_auto_party_builder()
        
        print(f"\n{bright_cyan('📋 사용 가능한 직업 목록', True)}")
        print("="*80)
        
        # 역할별로 분류하여 표시
        role_colors = {
            "탱커": red,
            "딜러": yellow, 
            "마법사": magenta,
            "서포터": green,
            "하이브리드": cyan
        }
        
        for role, classes in auto_builder.ROLE_CLASSES.items():
            # 해당 역할에 해금된 직업이 있는지 확인
            unlocked_in_role = [cls for cls in classes if cls in available_classes]
            if not unlocked_in_role:
                continue
                
            print(f"\n{role_colors.get(role, bright_white)(f'【{role}】')}")
            
            for class_name in unlocked_in_role:
                # 스탯 정보 가져오기
                stats = auto_builder._get_class_base_stats(class_name)
                
                # 스탯을 보기 좋게 포맷팅
                stat_str = f"HP{stats['hp']:3d} | 물공{stats['physical_attack']:2d} | 마공{stats['magic_attack']:2d} | 물방{stats['physical_defense']:2d} | 마방{stats['magic_defense']:2d} | 속도{stats['speed']:2d}"
                
                print(f"  • {bright_white(f'{class_name:<8s}')} {stat_str}")
        
        print(f"\n{bright_cyan('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', True)}")
        

def main():
    """메인 함수"""
    print("Dawn Of Stellar - 별빛의 여명을 시작합니다...")
    
    # 한글 인코딩 설정
    try:
        from game.encoding_utils import setup_korean_encoding
        encoding_methods = setup_korean_encoding()
        if encoding_methods:
            print(f"✅ 한글 인코딩이 설정되었습니다: {', '.join(encoding_methods[:2])}")
        else:
            print("⚠️  한글 인코딩 설정에 실패했습니다. 일부 문자가 깨져 보일 수 있습니다.")
    except ImportError:
        # 인코딩 유틸리티가 없어도 게임 진행
        import os
        if os.name == 'nt':  # Windows
            try:
                import locale
                locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
            except:
                try:
                    sys.stdout.reconfigure(encoding='utf-8')
                    sys.stderr.reconfigure(encoding='utf-8')
                except:
                    pass  # 인코딩 설정 실패해도 게임 진행
    
    # 메인 메뉴
    game = DawnOfStellarGame()
    
    # 영구 진행상황 로드
    game.permanent_progression.load_from_file()
    
    # 🎵 메인 메뉴 BGM 재생
    if hasattr(game, 'ffvii_sound') and game.ffvii_sound:
        game.ffvii_sound.play_bgm("title", loop=True)
    elif hasattr(game, 'sound_manager') and game.sound_manager:
        game.sound_manager.play_bgm("title", loop=True)
    
    while True:
        print("\n" + "="*60)
        print(bright_cyan("🎮 Dawn Of Stellar - 메인 메뉴", True))
        print("="*60)
        print(f"{cyan('1️⃣')}  게임 시작 (자동 파티)")
        print(f"{blue('2️⃣')}  게임 불러오기") 
        print(f"{magenta('3️⃣')}  영구 성장") 
        print(f"{yellow('4️⃣')}  도움말")
        print(f"{red('0️⃣')}  종료")
        
        # 영구 진행상황 요약 표시
        if game.permanent_progression.total_runs > 0:
            print(f"\n{cyan('📊 진행상황:')} 플레이 {game.permanent_progression.total_runs}회 | "
                  f"최고 {game.permanent_progression.best_floor}층 | "
                  f"별의 정수 {bright_yellow(str(game.permanent_progression.stellar_essence))}")
        
        choice = get_single_key_input(f"\n{bright_white('👉 선택하세요 (0-4): ')}")
        
        if choice == '1':
            # 게임 시작 (자동 파티)
            game.sound_manager.play_sfx("menu_select")
            auto_game = DawnOfStellarGame()  # 새 인스턴스 생성
            auto_game.permanent_progression = game.permanent_progression  # 영구 진행상황 유지
            auto_game.create_auto_party()
            auto_game.start_adventure()  # main_loop 대신 start_adventure 사용
            
        elif choice == '2':
            # 게임 불러오기
            game.sound_manager.play_sfx("menu_select")
            load_game = DawnOfStellarGame()  # 새 인스턴스 생성
            load_game.permanent_progression = game.permanent_progression  # 영구 진행상황 유지
            load_game.load_game()
            if len(load_game.party_manager.members) > 0:  # 불러오기 성공시
                load_game.start_adventure()  # main_loop 대신 start_adventure 사용
        
        elif choice == '3':
            # 영구 성장 메뉴
            game.sound_manager.play_sfx("menu_select")
            game.show_permanent_progression_menu()
            
        elif choice == '4':
            # 도움말
            game.sound_manager.play_sfx("menu_select")
            show_help()
            
        elif choice == '0':
            # 게임 종료
            game.sound_manager.play_sfx("menu_cancel")
            print(f"\n🌟 {bright_green('게임을 종료합니다. 플레이해주셔서 감사합니다!')}")
            # 영구 진행상황 저장
            game.permanent_progression.save_to_file()
            break
            
        else:
            error_msg = f"잘못된 선택입니다: '{choice}'"
            game.sound_manager.play_sfx("error")
            print(f"❌ {red(error_msg)}")


if __name__ == "__main__":
    main()
