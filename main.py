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
    from game.display import GameDisplay
    from game.world import GameWorld
    from game.meta_progression import MetaProgression, get_meta_progression
    from game.items import ItemDatabase
    from game.input_utils import KeyboardInput, get_single_key_input
    from game.color_text import (ColorText, Color, bright_cyan, bright_yellow, bright_green, 
                                 bright_white, bright_red, red, green, blue, yellow, 
                                 cyan, magenta, bright_magenta, colored, rarity_colored, RED, RESET)
    from game.merchant import MerchantManager
    from game.permanent_progression import PermanentProgressionSystem
    from game.random_encounters import (RandomEncounterManager, FieldSkillManager, 
                                        get_encounter_manager, get_field_skill_manager)
    from game.tutorial import show_help
    from config import game_config
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

# 🎭 Easy Character Creator - 기본 캐릭터 생성 시스템
try:
    from game.easy_character_creator import get_easy_character_creator
    EASY_CREATOR_AVAILABLE = True
    print("✅ Easy Character Creator 로드 성공 - 기본 캐릭터 생성 시스템 준비완료")
except ImportError as e:
    print(f"⚠️ Easy Character Creator 로드 실패: {e}")
    print("🔄 레거시 캐릭터 생성 시스템을 사용합니다")
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
    UI_SYSTEM_AVAILABLE = True
except ImportError:
    print("⚠️ UI 시스템을 불러올 수 없습니다. (curses 모듈 없음)")
    UI_SYSTEM_AVAILABLE = False
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
    PASSIVE_SELECTION_AVAILABLE = True
except ImportError:
    print("⚠️ 패시브 선택 시스템을 불러올 수 없습니다.")
    PASSIVE_SELECTION_AVAILABLE = False
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
    from game.tutorial import show_tutorial_menu, show_help as show_quick_help
    def show_tutorial():
        print("🎓 튜토리얼을 시작합니다.")
        show_tutorial_menu()
    def show_help():
        show_quick_help()
except ImportError:
    def show_tutorial():
        print("🎓 튜토리얼 시스템을 불러올 수 없습니다.")
    def show_help():
        print("📚 도움말 시스템을 불러올 수 없습니다.")

try:
    from game.item_system import get_item_database
    ITEM_SYSTEM_AVAILABLE = True
except ImportError:
    print("⚠️ 아이템 시스템을 불러올 수 없습니다.")
    ITEM_SYSTEM_AVAILABLE = False
    def get_item_database():
        return None
    
# FFVII 사운드 시스템은 이제 통합 오디오 시스템으로 대체됨
def get_ffvii_sound_system():
    """FFVII 사운드 시스템 호환성 함수"""
    return get_unified_audio_system()


class DawnOfStellarGame:
    """Dawn Of Stellar 메인 게임 클래스 - 완전 통합 시스템"""
    
    def __init__(self):
        # 창 최대화 모드 적용 (게임 시작 시)
        try:
            from config import game_config
            if game_config.FULLSCREEN_MODE:
                print("🖥️ 터미널 창을 최대화하는 중...")
                game_config.apply_terminal_fullscreen()
        except Exception as e:
            print(f"⚠️ 창 최대화 중 오류: {e}")
        
        # 기존 시스템들
        self.display = GameDisplay()
        self.party_manager = PartyManager()
        
        # 오디오 시스템 초기화 먼저
        try:
            from game.audio_system import get_audio_manager
            self.audio_system = get_audio_manager()
        except ImportError:
            self.audio_system = None
        
        self.merchant_manager = MerchantManager()
        self.permanent_progression = PermanentProgressionSystem()
        self.world = GameWorld(party_manager=self.party_manager)
        self.party_passive_effects = []  # 파티 패시브 효과 저장
        self.current_floor = 1  # 현재 층 정보 추가
        
        # 필드 자동 회복 시스템을 위한 걸음 수 추적
        self.step_count = 0
        
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
        
        # 🎵 메인 메뉴 BGM 재생 (통합 사운드 시스템 사용)
        if self.sound_manager and hasattr(self.sound_manager, 'mixer_available') and self.sound_manager.mixer_available:
            try:
                # 메인 메뉴 BGM 재생
                self.sound_manager.play_bgm("Main theme of FFVII", loop=True)
                print("🎵 메인 메뉴 BGM 재생 중...")
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
        
        # 캐릭터 선택이 취소되면 게임 초기화 중단
        if not self.show_character_selection():
            print(f"\n{bright_red('게임 초기화가 취소되었습니다.')}")
            print(f"{bright_cyan('프로그램을 종료합니다...')}")
            return False
            
        self.apply_permanent_bonuses()  # 영구 성장 보너스 적용
        
        # 재기의 기회 사용 횟수 초기화
        self.second_chance_uses = 0
        
        self.world.generate_level()
        
        # 🎵 게임 시작 BGM 재생
        print("🎵 던전 테마로 변경...")
        self.safe_play_bgm("dungeon_theme", loop=True)
        print("✅ 게임 초기화 완료!")
        time.sleep(1)
        return True  # 게임 초기화 성공
        
    def apply_permanent_bonuses(self):
        """영구 성장 보너스 적용 - 개선된 시스템"""
        for member in self.party_manager.members:
            # 게임 인스턴스 참조 추가 (second_chance 능력을 위해)
            member.game_instance = self
            
            # 파티 매니저에도 게임 인스턴스 참조 추가 (시야 계산용)
            if hasattr(self.party_manager, 'set_game_instance'):
                self.party_manager.set_game_instance(self)
            else:
                # 파티 매니저에 게임 인스턴스 참조 직접 설정
                self.party_manager.game_instance = self
            
            # 영구 강화 시스템 보너스 적용
            self.permanent_progression.load_from_file()
            
            # 기본 능력치에 영구 강화 보너스 적용
            for member in self.party_manager.members:
                # HP 보너스
                hp_bonus = self.permanent_progression.get_stat_bonus("hp")
                if hp_bonus > 0:
                    member.max_hp = int(member.max_hp * (1 + hp_bonus / 100))
                    member.current_hp = member.max_hp
                
                # 공격력 보너스
                attack_bonus = self.permanent_progression.get_stat_bonus("physical_attack")
                if attack_bonus > 0:
                    member.physical_attack = int(member.physical_attack * (1 + attack_bonus / 100))
                    member.magic_attack = int(member.magic_attack * (1 + attack_bonus / 100))
                
                # 방어력 보너스
                defense_bonus = self.permanent_progression.get_stat_bonus("physical_defense")
                if defense_bonus > 0:
                    member.physical_defense = int(member.physical_defense * (1 + defense_bonus / 100))
                    member.magic_defense = int(member.magic_defense * (1 + defense_bonus / 100))
                
                # 속도 보너스
                speed_bonus = self.permanent_progression.get_stat_bonus("speed")
                if speed_bonus > 0:
                    member.speed = int(member.speed * (1 + speed_bonus / 100))
            
            # 영구 성장 보너스 적용
            # HP 보너스
            hp_bonus = self.permanent_progression.get_stat_bonus("hp")
            if hp_bonus > 0:
                bonus_hp = int(member.max_hp * (hp_bonus / 100))
                member.max_hp += bonus_hp
                member.current_hp += bonus_hp
            
            # 공격력 보너스
            attack_bonus = self.permanent_progression.get_stat_bonus("physical_attack")
            if attack_bonus > 0:
                member.physical_attack = int(member.physical_attack * (1 + attack_bonus / 100))
                member.magic_attack = int(member.magic_attack * (1 + attack_bonus / 100))
            
            # 방어력 보너스
            defense_bonus = self.permanent_progression.get_stat_bonus("physical_defense")
            if defense_bonus > 0:
                member.physical_defense = int(member.physical_defense * (1 + defense_bonus / 100))
                member.magic_defense = int(member.magic_defense * (1 + defense_bonus / 100))
            
            # 속도 보너스
            speed_bonus = self.permanent_progression.get_stat_bonus("speed")
            if speed_bonus > 0:
                member.speed = int(member.speed * (1 + speed_bonus / 100))
            
            # 골드 보너스
            gold_bonus = self.permanent_progression.get_passive_bonus("gold_rate")
            if gold_bonus > 0:
                bonus_gold = int(member.gold * (gold_bonus / 100))
                member.gold += bonus_gold
        
        # 시작 아이템 제공 (모험가의 준비)
        starting_items_upgrade = self.permanent_progression.upgrades.get("starting_items")
        starting_items_level = starting_items_upgrade.current_level if starting_items_upgrade else 0
        if starting_items_level > 0:
            self.give_starting_items(starting_items_level)
        
        # 패시브 해금용 별조각 지급
        passive_fragments = self.permanent_progression.get_passive_bonus("passive_fragments")
        if passive_fragments > 0:
            self.meta_progression.data['star_fragments'] = self.meta_progression.data.get('star_fragments', 0) + int(passive_fragments)
            print(f"🌟 영구 성장 보너스로 별조각 {int(passive_fragments)}개를 받았습니다!")
    
    def give_starting_items(self, level: int):
        """시작 아이템 제공 - 개선된 시스템"""
        db = ItemDatabase()
        
        # 레벨에 따른 시작 아이템 (더 풍성하게)
        starting_items = []
        if level >= 1:
            starting_items.extend([
                "치료 포션", "치료 포션", "마나 포션", 
                "화염병", "해독제", "빵"
            ])
        if level >= 2:
            starting_items.extend([
                "강철 검", "가죽 갑옷", "힘의 반지",
                "고급 체력 포션", "스크롤: 화염구"
            ])
        if level >= 3:
            starting_items.extend([
                "번개 구슬", "방어막 두루마리", "부활의 깃털",
                "마법 지팡이", "은 목걸이", "만능 치료약"
            ])
        
        # 파티 전체에게 아이템 분배
        items_given = 0
        for member in self.party_manager.members:
            if not starting_items:
                break
                
            # 각 파티원에게 2-3개씩 아이템 지급
            items_for_member = min(3, len(starting_items))
            for _ in range(items_for_member):
                if starting_items:
                    item_name = starting_items.pop(0)
                    item = db.get_item(item_name)
                    if item:
                        success = member.inventory.add_item(item)
                        if success:
                            items_given += 1
                        else:
                            # 인벤토리가 가득 차면 다음 파티원에게
                            break
        
        if items_given > 0:
            print(f"🎁 모험가의 준비로 파티가 {items_given}개의 아이템을 받았습니다!")
        else:
            print("⚠️ 시작 아이템을 지급할 수 없었습니다. (인벤토리 부족)")
        
    def show_character_selection(self):
        """🎭 캐릭터 생성 시스템 - Easy Character Creator (기본)"""
        print(f"\n{bright_cyan('='*60)}")
        print(f"{bright_cyan('🎭 Dawn of Stellar - 캐릭터 생성', True)}")
        print(f"{bright_cyan('='*60)}")
        
        try:
            from game.easy_character_creator import get_easy_character_creator
            
            print(f"{bright_green('✨ 쉬운 캐릭터 생성 시스템을 시작합니다...')}")
            creator = get_easy_character_creator()
            party = creator.show_character_creation_menu()

            if party:
                # 생성된 파티를 게임에 적용
                self.characters = party
                self.current_character_index = 0
                
                # party_manager에도 파티 설정 (중요!)
                if hasattr(self, 'party_manager') and self.party_manager:
                    self.party_manager.members = party
                
                print(f"\n{bright_green('✅ 파티가 성공적으로 준비되었습니다!')}")
                print(f"{bright_cyan('🛡️ 파티원:')} {', '.join([c.name for c in party])}")
                print(f"{bright_yellow('⚔️ 이제 모험을 시작할 수 있습니다!')}")
                return True  # 성공적으로 파티 생성됨
            else:
                # 취소된 경우 메인 메뉴로 돌아가기
                print(f"\n{bright_yellow('❌ 캐릭터 생성이 취소되었습니다.')}")
                print(f"{bright_cyan('🏠 메인 메뉴로 돌아갑니다...')}")
                # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                self._play_main_menu_bgm()
                return False  # 취소됨
                
        except ImportError as e:
            print(f"{bright_red('⚠️ Easy Character Creator 로드 실패:')} {e}")
            print(f"{bright_yellow('🔄 레거시 캐릭터 선택 시스템을 사용합니다.')}")
            # 폴백: 기존 시스템
            return self.show_character_selection_legacy()
    
    def show_character_selection_legacy(self):
        """⚠️ 레거시 캐릭터 선택 시스템 (폴백 전용) - Easy Creator 실패시에만 사용"""
        print(f"\n{bright_yellow('⚠️ 레거시 캐릭터 생성 모드입니다.')}")
        print(f"{bright_cyan('💡 최신 Easy Character Creator 사용을 권장합니다.')}")
        try:
            from game.cursor_menu_system import CursorMenu, MenuAction
            
            # 메타 진행 정보 가져오기
            try:
                stats = self.meta_progression.get_stats()
                progress_info = f"{bright_cyan('플레이 횟수:')} {bright_yellow(str(stats['총 플레이 횟수']))} | {bright_cyan('최고 점수:')} {bright_yellow(str(stats['최고 점수']))} | {bright_cyan('별조각:')} {bright_yellow(str(stats['별조각']))}"
            except (AttributeError, KeyError):
                progress_info = f"{bright_cyan('플레이')} {bright_yellow(str(self.meta_progression.data.get('total_runs', 0)))}회 | {bright_cyan('별조각')} {bright_yellow(str(self.meta_progression.data.get('star_fragments', 0)))}"
            
            all_characters = self.character_db.get_all_characters()
            unlocked_names = self.meta_progression.get_unlocked_characters()
            unlocked_characters = [char for char in all_characters if char['name'] in unlocked_names]
            
            # 메뉴 옵션 생성
            options = []
            descriptions = []
            
            # 해금된 캐릭터들 추가
            for char_data in unlocked_characters:
                upgrade_level = self.meta_progression.get_character_upgrade_level(char_data['name'])
                upgrade_str = f" {bright_green(f'(업그레이드 Lv.{upgrade_level})')}" if upgrade_level > 0 else ""
                
                char_class = char_data['class']
                char_name = f"{bright_white(char_data['name'])} {cyan(f'({char_class})')}{upgrade_str}"
                options.append(char_name)
                
                stats_str = f"{green('HP:')}{char_data['hp']} | {red('P.ATK:')}{char_data['p_atk']} | {blue('M.ATK:')}{char_data['m_atk']} | "
                stats_str += f"{yellow('P.DEF:')}{char_data['p_def']} | {magenta('M.DEF:')}{char_data['m_def']} | {cyan('SPD:')}{char_data['speed']}"
                description = f"{bright_cyan(char_data['description'])}\n{stats_str}\n{bright_yellow('특성:')} {', '.join(char_data['traits'])}"
                descriptions.append(description)
            
            # 추가 옵션들
            options.extend([
                f"🎯 {bright_green('균형잡힌 파티')} {yellow('(추천)')}",
                f"🎲 {blue('랜덤 파티')}",
                f"✋ {bright_white('직접 선택')}"
            ])
            
            descriptions.extend([
                f"{bright_cyan('해금된 캐릭터 중에서 균형잡힌 조합으로 자동 구성합니다')}",
                f"{bright_cyan('해금된 캐릭터 중에서 무작위로 4명을 선택합니다')}",
                f"{bright_cyan('캐릭터를 하나씩 직접 선택합니다')}"
            ])
            
            # 제목에 진행 정보 포함
            title = f"🎭 {bright_cyan('캐릭터 선택')}\n{progress_info}"
            
            # 커서 메뉴 생성 및 실행
            menu = CursorMenu(title, options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None:  # 취소
                return False
            
            # 선택 결과 처리
            if result < len(unlocked_characters):
                # 개별 캐릭터 선택 - 하나 선택 후 나머지 자동
                selected_char = unlocked_characters[result]
                remaining_chars = [c for c in unlocked_characters if c != selected_char]
                auto_selected = random.sample(remaining_chars, min(3, len(remaining_chars)))
                
                party_names = [selected_char["name"]] + [c["name"] for c in auto_selected]
                # 4명이 안되면 부족한 만큼 랜덤 추가
                while len(party_names) < 4 and len(unlocked_names) >= 4:
                    remaining_names = [name for name in unlocked_names if name not in party_names]
                    if remaining_names:
                        party_names.append(random.choice(remaining_names))
                        
                self.create_party_from_names(party_names)
                # 특성 선택은 easy_character_creator에서 이미 처리됨
                
            elif result == len(unlocked_characters):  # 균형잡힌 파티
                party_names = self.get_balanced_unlocked_party(unlocked_names)
                self.create_party_from_names(party_names)
                # 특성 선택은 easy_character_creator에서 이미 처리됨
                
            elif result == len(unlocked_characters) + 1:  # 랜덤 파티
                party_names = self.get_random_unlocked_party(unlocked_names)
                self.create_party_from_names(party_names)
                # 특성 선택은 easy_character_creator에서 이미 처리됨
                
            elif result == len(unlocked_characters) + 2:  # 직접 선택
                result = self.manual_character_selection(unlocked_characters)
                if not result:  # 수동 선택이 취소된 경우
                    return False
                # 특성 선택은 easy_character_creator에서 이미 처리됨
                
            return True  # 성공적으로 파티 생성됨
                
        except ImportError:
            # 폴백: 기존 메뉴 시스템
            return self.show_character_selection_legacy_fallback()
    
    def show_passive_selection_for_party(self):
        """파티 생성 후 패시브 선택 실행 - 새로운 시스템에서는 사용안함"""
        # 새로운 특성 선택 시스템이 easy_character_creator에서 처리하므로 
        # 이 메서드는 더 이상 사용하지 않음
        pass
    
    def select_party_passive_effects(self):
        """파티 전체 패시브 효과 선택"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white
            
            # 사용 가능한 패시브 효과들 (3-10 코스트 시스템)
            all_passive_effects = [
                # 3코스트 패시브 (기본 효과들)
                {
                    "name": "전투의 달인", 
                    "description": "경험치 획득량 +18%",
                    "effect_type": "exp_bonus",
                    "effect_value": {"exp": 0.18},
                    "cost": 3,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "황금 손길", 
                    "description": "골드 획득량 +25%",
                    "effect_type": "gold_bonus", 
                    "effect_value": {"base": 0.25},
                    "cost": 3,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "불굴의 의지",
                    "description": "파티 최대 HP +20%",
                    "effect_type": "hp_bonus",
                    "effect_value": {"hp": 0.20},
                    "cost": 3,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                
                # 4코스트 패시브
                {
                    "name": "요리 장인",
                    "description": "요리 재료 발견율 +40%, 요리 효과 +20%",
                    "effect_type": "cooking_master",
                    "effect_value": {"discovery": 0.40, "effect": 0.20},
                    "cost": 4,
                    "unlock_cost": 120,  # 15 → 120
                    "rarity": "uncommon"
                },
                {
                    "name": "탐험가의 제6감",
                    "description": "숨겨진 아이템 발견율 +45%, 함정 회피율 +55%, 시야 범위 +1",
                    "effect_type": "explorer_instinct",
                    "effect_value": {"item_find": 0.45, "trap_avoid": 0.55, "vision_range": 1},
                    "cost": 4,
                    "unlock_cost": 150,  # 20 → 150
                    "rarity": "uncommon"
                },
                {
                    "name": "생명의 오라",
                    "description": "전투 후 상처 치료 10%, HP 회복 5%, MP +5",
                    "effect_type": "healing_aura",
                    "effect_value": {"wound_heal": 0.10, "hp_heal": 0.05, "mp_regen": 5},
                    "cost": 4,
                    "unlock_cost": 100,  # 12 → 100
                    "rarity": "uncommon"
                },
                {
                    "name": "거상의 안목",
                    "description": "상점 아이템 할인 30%, 판매가 +10%",
                    "effect_type": "merchant_eye",
                    "effect_value": {"discount": 0.30, "sell_bonus": 0.10},
                    "cost": 4,
                    "unlock_cost": 130,  # 18 → 130
                    "rarity": "uncommon"
                },
                
                # 5코스트 패시브
                {
                    "name": "원소 친화",
                    "description": "모든 원소 마법 데미지 +25%, 원소 저항 +25%",
                    "effect_type": "elemental_affinity",
                    "effect_value": {"damage": 0.25, "resist": 0.25},
                    "cost": 5,
                    "unlock_cost": 200,  # 25 → 200
                    "rarity": "rare"
                },
                {
                    "name": "마나 순환",
                    "description": "스킬 사용 시 35% 확률로 MP 소모 없음",
                    "effect_type": "mana_cycle",
                    "effect_value": {"no_cost_chance": 0.35},
                    "cost": 5,
                    "unlock_cost": 180,  # 22 → 180
                    "rarity": "rare"
                },
                {
                    "name": "행운의 별",
                    "description": "크리티컬 확률 +15%, 레어 아이템 드롭율 +35%",
                    "effect_type": "lucky_star",
                    "effect_value": {"crit": 0.15, "rare_drop": 0.35},
                    "cost": 5,
                    "unlock_cost": 160,  # 30 → 160
                    "rarity": "rare"
                },
                
                # 6코스트 패시브
                {
                    "name": "생존 본능",
                    "description": "HP 30% 이하일 때 모든 능력 +40%, 치명상 저항 +20%",
                    "effect_type": "survival_instinct",
                    "effect_value": {"all_boost": 0.40, "hp_threshold": 0.30, "fatal_resist": 0.20},
                    "cost": 6,
                    "unlock_cost": 220,  # 28 → 220
                    "rarity": "rare"
                },
                {
                    "name": "시간의 조율자",
                    "description": "ATB 속도 +30%, 첫 턴 우선권 확률 +70%",
                    "effect_type": "time_master",
                    "effect_value": {"atb_speed": 0.30, "first_turn": 0.70},
                    "cost": 6,
                    "unlock_cost": 250,  # 35 → 250
                    "rarity": "epic"
                },
                
                # 장비/도구 관련 패시브 (4-9코스트)
                {
                    "name": "장비 수호자",
                    "description": "🛡️ 장비 내구도 감소 확률 -25%",
                    "effect_type": "equipment_protection",
                    "effect_value": {"durability_loss_reduction": 0.25},
                    "cost": 4,
                    "unlock_cost": 120,
                    "rarity": "uncommon"
                },
                {
                    "name": "단조 마스터",
                    "description": "� 모든 장비 최대 내구도 +20%",
                    "effect_type": "durability_enhancement",
                    "effect_value": {"max_durability_bonus": 0.20},
                    "cost": 5,
                    "unlock_cost": 180,
                    "rarity": "rare"
                },
                {
                    "name": "장비 분석가",
                    "description": "� 필드 수리 효과 +50%, MP 소모 -25%",
                    "effect_type": "repair_expert",
                    "effect_value": {"repair_bonus": 0.50, "mp_reduction": 0.25},
                    "cost": 6,
                    "unlock_cost": 220,
                    "rarity": "rare"
                },
                {
                    "name": "장인의 혼",
                    "description": "✨ 수리 시 추가 내구도 회복 +10%",
                    "effect_type": "artisan_touch",
                    "effect_value": {"repair_bonus": 0.10},
                    "cost": 6,
                    "unlock_cost": 250,
                    "rarity": "epic"
                },
                {
                    "name": "완벽주의자",
                    "description": "🎯 내구도 80% 이상일 때 모든 능력치 +5%",
                    "effect_type": "perfectionist",
                    "effect_value": {"stat_bonus": 0.05, "durability_threshold": 0.80},
                    "cost": 7,
                    "unlock_cost": 320,
                    "rarity": "epic"
                },
                {
                    "name": "강철 의지",
                    "description": "⚔️ 내구도 감소 -50%, 수리비 -30%",
                    "effect_type": "durability_master",
                    "effect_value": {"durability_loss_reduction": 0.50, "repair_cost_reduction": 0.30},
                    "cost": 8,
                    "unlock_cost": 420,
                    "rarity": "legendary"
                },
                {
                    "name": "절대 보존",
                    "description": "💎 장비가 절대 파괴되지 않음 (최소 1 내구도 유지)",
                    "effect_type": "unbreakable_equipment",
                    "effect_value": {"prevent_destruction": True},
                    "cost": 9,
                    "unlock_cost": 500,
                    "rarity": "mythic"
                },
                
                # 7코스트 패시브 (강력한 효과들)
                {
                    "name": "연금술사의 지혜",
                    "description": "포션 효과 +55%, 독 저항 +40%, 포션 2회 사용",
                    "effect_type": "alchemist_wisdom",
                    "effect_value": {"potion_power": 0.55, "poison_resist": 0.40, "double_use": True},
                    "cost": 7,
                    "unlock_cost": 300,  # 40 → 300
                    "rarity": "epic"
                },
                {
                    "name": "전술가의 감각",
                    "description": "전투 시작 시 파티원 1명 즉시 행동, 시야 범위 +3",
                    "effect_type": "tactician_sense",
                    "effect_value": {"instant_action": 1, "vision_range": 3},
                    "cost": 7,
                    "unlock_cost": 350,  # 45 → 350
                    "rarity": "epic"
                },
                {
                    "name": "보물 사냥꾼",
                    "description": "상자 2개씩 열림, 미믹 간파 80%, 함정 보물화 20%",
                    "effect_type": "treasure_hunter",
                    "effect_value": {"double_chest": True, "mimic_detect": 0.80, "trap_treasure": 0.20},
                    "cost": 7,
                    "unlock_cost": 320,  # 42 → 320
                    "rarity": "epic"
                },
                
                # 8코스트 패시브 (매우 강력한 효과)
                {
                    "name": "던전 정복자",
                    "description": "보스 데미지 +50%, 층 이동 시 부분 회복 30%, 보스 처치 시 별조각 +2",
                    "effect_type": "dungeon_conqueror",
                    "effect_value": {"boss_damage": 0.50, "floor_recovery": 0.30, "boss_fragments": 2},
                    "cost": 8,
                    "unlock_cost": 400,  # 50 → 400
                    "rarity": "legendary"
                },
                {
                    "name": "별의 축복",
                    "description": "모든 상태효과 지속시간 +2턴, 디버프 저항 +60%",
                    "effect_type": "stellar_blessing",
                    "effect_value": {"buff_duration": 2, "debuff_resist": 0.60},
                    "cost": 8,
                    "unlock_cost": 450,  # 55 → 450
                    "rarity": "legendary"
                },
                {
                    "name": "마스터 힐러",
                    "description": "모든 치유 효과 +60%, 부활 스킬 MP 소모 -50%",
                    "effect_type": "master_healer",
                    "effect_value": {"heal_boost": 0.60, "revive_cost": 0.50},
                    "cost": 8,
                    "unlock_cost": 420,  # 48 → 420
                    "rarity": "legendary"
                },
                
                # 9코스트 패시브 (최고급 효과)
                {
                    "name": "운명 조작자",
                    "description": "크리티컬 미스 방지, 회피 실패 시 반격 확률 35%, 운명의 주사위",
                    "effect_type": "fate_manipulator",
                    "effect_value": {"no_crit_miss": True, "counter_chance": 0.35, "fate_dice": True},
                    "cost": 9,
                    "unlock_cost": 500,  # 60 → 500
                    "rarity": "legendary"
                },
                {
                    "name": "불사의 의지",
                    "description": "파티원 죽음 시 20% HP로 부활, 부활 시 2턴 보호막, 1회/층",
                    "effect_type": "undying_will",
                    "effect_value": {"revive_hp": 0.20, "shield_turns": 2, "uses_per_floor": 1},
                    "cost": 9,
                    "unlock_cost": 550,  # 65 → 550
                    "rarity": "mythic"
                },
                {
                    "name": "마법 흡수체",
                    "description": "받는 마법 데미지 55% 감소",
                    "effect_type": "magic_absorber",
                    "effect_value": {"magic_reduction": 0.55},
                    "cost": 9,
                    "unlock_cost": 480,  # 58 → 480
                    "rarity": "mythic"
                },
                
                # 10코스트 패시브 (게임 체인징)
                {
                    "name": "시공간 지배자",
                    "description": "받는 물리/마법 피해 35% 감소, 스킬 쿨다운 -50%",
                    "effect_type": "spacetime_lord",
                    "effect_value": {"damage_reduction": 0.35, "cooldown_reduction": 0.50},
                    "cost": 10,
                    "unlock_cost": 600,  # 70 → 600
                    "rarity": "mythic"
                },
                {
                    "name": "전설의 영웅",
                    "description": "모든 능력치 +20%, 파티 사기 +25%, 영웅적 행동",
                    "effect_type": "legendary_hero",
                    "effect_value": {"all_stats": 0.20, "morale": 0.25, "heroic_actions": True},
                    "cost": 10,
                    "unlock_cost": 650,  # 75 → 650
                    "rarity": "mythic"
                }
            ]
            
            # 현재 최대 코스트 확인 - 영구성장과 연동
            try:
                # 기본 최대 코스트 + 메타 진행 업그레이드 + 영구성장 보너스
                meta_upgrades = self.meta_progression.data.get('max_passive_cost_upgrades', 0) if hasattr(self, 'meta_progression') else 0
                permanent_bonus = int(self.permanent_progression.get_passive_bonus("passive_cost_max")) if hasattr(self, 'permanent_progression') else 0
                
                current_max_cost = 5 + meta_upgrades + permanent_bonus  # 기본 5 + 업그레이드 + 영구성장
                current_max_cost = min(current_max_cost, 10)  # 최대 10으로 제한
                
                unlocked_cost = self.meta_progression.data.get('star_fragments', 0) if hasattr(self, 'meta_progression') else 999
                unlocked_passives = self.meta_progression.data.get('unlocked_passives', []) if hasattr(self, 'meta_progression') else []
                
                # 개발 모드 확인
                from config import game_config
                is_dev_mode = hasattr(game_config, 'DEVELOPMENT_MODE') and game_config.DEVELOPMENT_MODE
                
                if is_dev_mode:
                    # 개발 모드에서는 모든 패시브 해금 및 최대 코스트 확장
                    current_max_cost = 15  # 개발 모드 최대 코스트
                    unlocked_cost = 99999  # 충분한 별조각
                    unlocked_passives = [p['name'] for p in all_passive_effects]  # 모든 패시브 해금
                    print(f"🔧 개발 모드: 모든 패시브 해금, 최대 코스트 {current_max_cost}")
                else:
                    print(f"📊 패시브 코스트: {current_max_cost} (기본 3 + 메타 {meta_upgrades} + 영구성장 {permanent_bonus})")
                
                passive_effects = []
                for passive in all_passive_effects:
                    # 이미 해금했거나, 별조각이 충분하거나, 무료 패시브인 경우
                    if (passive['name'] in unlocked_passives or 
                        passive['unlock_cost'] == 0 or 
                        unlocked_cost >= passive['unlock_cost']):
                        passive_effects.append(passive)
                        
            except Exception:
                # 안전장치: 기본 패시브들만 사용
                current_max_cost = 3
                passive_effects = [p for p in all_passive_effects if p['unlock_cost'] == 0]
            
            # 개발 모드 확인
            from config import game_config
            is_dev_mode = hasattr(game_config, 'DEVELOPMENT_MODE') and game_config.DEVELOPMENT_MODE
            
            selected_passives = []
            used_cost = 0
            
            while used_cost < current_max_cost:
                # 메뉴 옵션 생성
                options = []
                descriptions = []
                
                # 선택 가능한 패시브들 (이미 선택된 것 제외, 코스트가 남은 용량 이하)
                available_passives = [p for p in passive_effects 
                                    if p not in selected_passives 
                                    and p['cost'] <= (current_max_cost - used_cost)]
                
                for passive in available_passives:
                    # 해금 상태에 따른 표시
                    rarity_colors = {
                        "common": "⚪",
                        "uncommon": "💚",
                        "rare": "💙", 
                        "epic": "💜",
                        "legendary": "🧡",
                        "mythic": "❤️"
                    }
                    
                    rarity_color = rarity_colors.get(passive.get('rarity', 'common'), '')
                    unlock_cost = passive.get('unlock_cost', 0)
                    passive_cost = passive.get('cost', 1)
                    if unlock_cost == 0:
                        # 기본 패시브
                        options.append(f"{rarity_color}{passive['name']} [{passive_cost}코스트]")
                    elif passive['name'] in unlocked_passives:
                        # 이미 해금된 패시브
                        options.append(f"{rarity_color}{passive['name']} [{passive_cost}코스트]")
                    else:
                        # 해금 가능한 패시브 (별조각으로 해금)
                        options.append(f"{rarity_color}{passive['name']} [{passive_cost}코스트] 🔓 (별조각 {unlock_cost})")
                    
                    descriptions.append(f"💡 {passive['description']}")
                
                # 최대 코스트 업그레이드 옵션 (별조각이 충분할 때, 개발 모드가 아닐 때, 영구성장으로 최대가 아닐 때)
                max_cost_upgrade_cost = (meta_upgrades + 1) * 50  # 50, 100, 150, ... 별조각
                can_upgrade_with_fragments = (hasattr(self, 'meta_progression') and 
                    unlocked_cost >= max_cost_upgrade_cost and 
                    meta_upgrades < 7 and  # 메타 진행으로는 최대 7단계까지
                    current_max_cost < 10 and  # 아직 최대에 도달하지 않음
                    not is_dev_mode)  # 개발 모드가 아닐 때만
                
                if can_upgrade_with_fragments:
                    options.append(f"⬆️ 최대 코스트 업그레이드 (별조각 {max_cost_upgrade_cost})")
                    descriptions.append(f"최대 패시브 코스트를 {current_max_cost + 1}로 증가시킵니다")
                
                # 해금 정보 추가
                if hasattr(self, 'meta_progression'):
                    current_fragments = self.meta_progression.data.get('star_fragments', 0)
                    cost_info = f"\n현재 별조각: {current_fragments} ⭐ | 사용 코스트: {used_cost}/{current_max_cost}"
                else:
                    cost_info = f"\n사용 코스트: {used_cost}/{current_max_cost}"
                
                # 선택 완료 옵션 (1개 이상 선택했을 때)
                if len(selected_passives) > 0:
                    options.append(f"✅ {bright_white('선택 완료')}")
                    descriptions.append(f"현재 선택된 패시브로 게임을 시작합니다")
                
                # 패시브 없이 시작 옵션
                options.append(f"❌ {bright_white('패시브 없이 시작')}")
                descriptions.append("패시브 효과 없이 게임을 시작합니다")
                
                # 현재 선택 상태 표시
                selected_names = [f"{p['name']}[{p['cost']}]" for p in selected_passives]
                current_selection = ", ".join(selected_names) if selected_names else "없음"
                title = f"🌟 파티 패시브 효과 선택{cost_info}\n현재 선택: {current_selection}"
                
                # 커서 메뉴 생성 및 실행
                menu = CursorMenu(title, options, descriptions, cancellable=True)
                result = menu.run()
                
                if result is None or result == -1:  # 취소 (Q키)
                    print(f"\n{yellow('❌ 패시브 선택이 취소되었습니다.')}")
                    print(f"{bright_cyan('패시브 효과 없이 모험을 시작할지 선택해주세요.')}")
                    
                    # 패시브 없이 시작할지 확인
                    from game.cursor_menu_system import CursorMenu
                    confirm_options = ["🚀 패시브 없이 시작", "🔙 패시브 선택으로 돌아가기"]
                    confirm_descriptions = [
                        "패시브 효과 없이 모험을 시작합니다",
                        "다시 패시브를 선택합니다"
                    ]
                    
                    confirm_menu = CursorMenu(
                        "패시브 선택 취소 확인",
                        confirm_options, confirm_descriptions, cancellable=False
                    )
                    
                    confirm_result = confirm_menu.run()
                    if confirm_result == 0:  # 패시브 없이 시작
                        selected_passives = []
                        break
                    else:  # 패시브 선택으로 돌아가기
                        continue
                elif result < len(available_passives):
                    # 패시브 선택
                    selected_passive = available_passives[result]
                    unlock_cost = selected_passive.get('unlock_cost', 0)
                    passive_name = selected_passive['name']
                    passive_cost = selected_passive.get('cost', 1)
                    
                    # 해금 처리
                    if unlock_cost > 0 and passive_name not in unlocked_passives:
                        if hasattr(self, 'meta_progression'):
                            current_fragments = self.meta_progression.data.get('star_fragments', 0)
                            if current_fragments >= unlock_cost:
                                # 별조각 차감하고 해금
                                self.meta_progression.data['star_fragments'] -= unlock_cost
                                if 'unlocked_passives' not in self.meta_progression.data:
                                    self.meta_progression.data['unlocked_passives'] = []
                                self.meta_progression.data['unlocked_passives'].append(passive_name)
                                self.meta_progression.save_to_file()
                                
                                remaining_fragments = current_fragments - unlock_cost
                                print(f"\n{bright_green('🔓 ' + passive_name + ' 패시브가 해금되었습니다!')}")
                                print(f"{yellow('별조각 ' + str(unlock_cost) + '개를 사용했습니다. (남은 별조각: ' + str(remaining_fragments) + ')')}")
                            else:
                                print(f"\n{red('❌ 별조각이 부족합니다! (필요: ' + str(unlock_cost) + ', 보유: ' + str(current_fragments) + ')')}")
                                continue
                        else:
                            print(f"\n{red('❌ 메타 진행 시스템을 사용할 수 없습니다.')}")
                            continue
                    
                    # 코스트 체크
                    if used_cost + passive_cost > current_max_cost:
                        print(f"\n{red('❌ 코스트가 부족합니다! (필요: ' + str(passive_cost) + ', 남은 코스트: ' + str(current_max_cost - used_cost) + ')')}")
                        continue
                    
                    selected_passives.append(selected_passive)
                    used_cost += passive_cost
                    passive_desc = selected_passive['description']
                    print(f"\n{green('✅ ' + passive_name + ' [' + str(passive_cost) + '코스트] 효과가 선택되었습니다!')}")
                    print(f"{cyan('💡 효과: ' + passive_desc)}")
                    
                    if used_cost >= current_max_cost:
                        print(f"\n{bright_yellow('🎯 최대 코스트(' + str(current_max_cost) + ')에 도달했습니다!')}")
                        break
                        
                # 최대 코스트 업그레이드 처리
                elif (hasattr(self, 'meta_progression') and 
                      result == len(available_passives) and 
                      unlocked_cost >= max_cost_upgrade_cost and 
                      meta_upgrades < 7 and  # 메타 진행으로는 최대 7단계까지
                      current_max_cost < 10 and  # 아직 최대에 도달하지 않음
                      not is_dev_mode):  # 개발 모드가 아닐 때만
                    # 최대 코스트 업그레이드
                    self.meta_progression.data['star_fragments'] -= max_cost_upgrade_cost
                    self.meta_progression.data['max_passive_cost_upgrades'] = meta_upgrades + 1
                    self.meta_progression.save_to_file()
                    
                    old_max_cost = current_max_cost
                    current_max_cost += 1
                    meta_upgrades += 1
                    unlocked_cost -= max_cost_upgrade_cost
                    
                    print(f"\n{bright_green('⬆️ 최대 코스트가 ' + str(old_max_cost) + '에서 ' + str(current_max_cost) + '로 업그레이드되었습니다!')}")
                    print(f"{yellow('별조각 ' + str(max_cost_upgrade_cost) + '개를 사용했습니다.')}")
                    continue
                    
                elif len(selected_passives) > 0 and result == len(available_passives) + (1 if (hasattr(self, 'meta_progression') and unlocked_cost >= max_cost_upgrade_cost and meta_upgrades < 7 and current_max_cost < 10 and not is_dev_mode) else 0):
                    # 선택 완료
                    break
                else:
                    # 패시브 없이 시작
                    selected_passives = []
                    break
            
            # 선택된 패시브 효과 적용
            self.party_passive_effects = selected_passives
            self.apply_passive_effects_to_party()
            
            # 최종 결과 표시
            print(f"\n{bright_cyan('='*60)}")
            if len(selected_passives) == 0:
                print(f"{yellow('🚀 파티가 패시브 효과 없이 모험을 시작합니다.')}")
            else:
                print(f"{green('🎉 파티 패시브 효과가 적용되었습니다:')}")
                for i, passive in enumerate(selected_passives, 1):
                    passive_name = passive['name']
                    passive_desc = passive['description']
                    print(f"  {bright_yellow(f'{i}. {passive_name}')}: {white(passive_desc)}")
            print(f"{bright_cyan('='*60)}")
            
            # 확인창 추가 - 패시브 효과 적용 후 잠시 멈춤
            if len(selected_passives) > 0:
                print(f"\n{bright_white('💡 선택하신 패시브 효과들이 이번 게임에서 활성화됩니다!')}")
                print(f"{bright_cyan('이 효과들은 던전 탐험 중 자동으로 적용됩니다.')}")
                self.keyboard.wait_for_key(f"\n{bright_green('✅ 아무 키나 눌러 모험을 계속하세요...')}")
            else:
                self.keyboard.wait_for_key(f"\n{bright_white('🔑 아무 키나 눌러 계속...')}")
            
        except ImportError as e:
            print(f"패시브 선택 시스템을 불러올 수 없습니다: {e}")
            self.party_passive_effects = []
    
    def apply_passive_effects_to_party(self):
        """선택된 패시브 효과를 파티에 적용"""
        if not hasattr(self, 'party_passive_effects'):
            return
            
        for passive in self.party_passive_effects:
            effect_type = passive['effect_type']
            effect_value = passive['effect_value']
            
            # 파티 전체에 적용되는 효과들
            if effect_type == "hp_bonus":
                # effect_value가 딕셔너리인 경우 적절한 값 추출
                if isinstance(effect_value, dict):
                    bonus_rate = effect_value.get("hp", 0)
                else:
                    bonus_rate = effect_value
                    
                for member in self.party_manager.members:
                    bonus_hp = int(member.max_hp * bonus_rate)
                    member.max_hp += bonus_hp
                    member.current_hp += bonus_hp
                    
            elif effect_type == "mp_bonus":
                if isinstance(effect_value, dict):
                    bonus_rate = effect_value.get("mp", 0)
                else:
                    bonus_rate = effect_value
                    
                for member in self.party_manager.members:
                    bonus_mp = int(member.max_mp * bonus_rate)
                    member.max_mp += bonus_mp
                    member.current_mp += bonus_mp
                    
            elif effect_type == "speed_bonus":
                if isinstance(effect_value, dict):
                    bonus_rate = effect_value.get("speed", 0)
                else:
                    bonus_rate = effect_value
                    
                for member in self.party_manager.members:
                    member.speed = int(member.speed * (1 + bonus_rate))
                    
            elif effect_type == "legendary_hero":
                # 모든 능력치 증가
                if isinstance(effect_value, dict):
                    stats_bonus = effect_value.get("all_stats", 0)
                else:
                    stats_bonus = effect_value  # effect_value가 직접 숫자인 경우
                    
                for member in self.party_manager.members:
                    member.physical_attack = int(member.physical_attack * (1 + stats_bonus))
                    member.magic_attack = int(member.magic_attack * (1 + stats_bonus))
                    member.physical_defense = int(member.physical_defense * (1 + stats_bonus))
                    member.magic_defense = int(member.magic_defense * (1 + stats_bonus))
                    member.speed = int(member.speed * (1 + stats_bonus))
                    
            elif effect_type == "elemental_affinity":
                # 원소 친화력 - 속성 공격력 증가 (멤버의 속성에 따라)
                if isinstance(effect_value, dict):
                    damage_bonus = effect_value.get("damage", 0)
                else:
                    damage_bonus = effect_value  # effect_value가 직접 숫자인 경우
                    
                for member in self.party_manager.members:
                    if hasattr(member, 'magic_attack'):
                        member.magic_attack = int(member.magic_attack * (1 + damage_bonus))
                        
            # 다른 효과들은 게임 진행 중에 동적으로 적용됨
            # (exp_bonus, gold_bonus, cooking_master, explorer_instinct 등)
    
    def get_passive_bonus(self, effect_type: str, bonus_type: str = None):
        """패시브 효과에서 특정 보너스 값 가져오기"""
        if not hasattr(self, 'party_passive_effects'):
            return 0
            
        total_bonus = 0
        for passive in self.party_passive_effects:
            if passive['effect_type'] == effect_type:
                effect_value = passive['effect_value']
                if bonus_type and isinstance(effect_value, dict):
                    total_bonus += effect_value.get(bonus_type, 0)
                elif not bonus_type:
                    total_bonus += effect_value if isinstance(effect_value, (int, float)) else 0
        return total_bonus
    
    def has_passive_effect(self, effect_type: str):
        """특정 패시브 효과가 있는지 확인"""
        if not hasattr(self, 'party_passive_effects'):
            return False
        return any(passive['effect_type'] == effect_type for passive in self.party_passive_effects)
    
    def apply_exp_bonus(self, base_exp: int) -> int:
        """경험치 보너스 적용"""
        bonus = self.get_passive_bonus("exp_bonus")
        return int(base_exp * (1 + bonus))
    
    def apply_gold_bonus(self, base_gold: int) -> int:
        """골드 보너스 적용"""
        bonus = self.get_passive_bonus("gold_bonus")
        return int(base_gold * (1 + bonus))
    
    def apply_merchant_discount(self, price: int) -> int:
        """상인 할인 적용"""
        discount = self.get_passive_bonus("merchant_eye", "discount")
        return int(price * (1 - discount))
    
    def apply_sell_bonus(self, sell_price: int) -> int:
        """판매 보너스 적용"""
        bonus = self.get_passive_bonus("merchant_eye", "sell_bonus")
        return int(sell_price * (1 + bonus))
    
    def check_lucky_star_effects(self):
        """행운의 별 효과 확인 (크리티컬, 레어드롭)"""
        crit_bonus = self.get_passive_bonus("lucky_star", "crit")
        rare_drop_bonus = self.get_passive_bonus("lucky_star", "rare_drop")
        return {"crit_bonus": crit_bonus, "rare_drop_bonus": rare_drop_bonus}
    
    def apply_healing_aura_effects(self):
        """치유의 기운 효과 적용 (전투 후)"""
        if self.has_passive_effect("healing_aura"):
            wound_heal_rate = self.get_passive_bonus("healing_aura", "wound_heal")
            mp_regen = self.get_passive_bonus("healing_aura", "mp_regen")
            
            for member in self.party_manager.members:
                if member.current_hp > 0:  # 살아있는 멤버만
                    # 상처 치료
                    if hasattr(member, 'wounds') and member.wounds > 0:
                        heal_amount = int(member.wounds * wound_heal_rate)
                        member.wounds = max(0, member.wounds - heal_amount)
                    
                    # MP 회복
                    member.current_mp = min(member.max_mp, member.current_mp + mp_regen)
    
    def check_mana_cycle(self) -> bool:
        """마나 순환 효과 확인 (스킬 사용 시 MP 소모 없음 확률)"""
        if self.has_passive_effect("mana_cycle"):
            chance = self.get_passive_bonus("mana_cycle")
            import random
            return random.random() < chance
        return False
    
    def save_game(self):
        """게임 저장 (패시브 효과 포함)"""
        if not SAVE_SYSTEM_AVAILABLE:
            print("💾 저장 시스템을 사용할 수 없습니다.")
            return
            
        try:
            from game.save_system import SaveManager
            save_manager = SaveManager()
            
            # 게임 상태 생성 - party_characters 키 사용
            game_state = {
                'party': [],  # 레거시 호환성
                'party_characters': [],  # 새로운 표준
                'party_passive_effects': self.party_passive_effects,
                'world_state': {},
                'save_version': '2.0'
            }
            
            # 파티 멤버 저장
            for member in self.party_manager.members:
                member_data = {
                    'name': member.name,
                    'character_class': member.character_class,
                    'level': member.level,
                    'experience': member.experience,
                    'current_hp': member.current_hp,
                    'max_hp': member.max_hp,
                    'current_mp': member.current_mp,
                    'max_mp': member.max_mp,
                    'wounds': member.wounds,
                    'physical_attack': member.physical_attack,
                    'magic_attack': member.magic_attack,
                    'physical_defense': member.physical_defense,
                    'magic_defense': member.magic_defense,
                    'speed': member.speed,
                    'active_traits': [{'name': trait.name, 'description': trait.description} for trait in member.active_traits]
                }
                game_state['party'].append(member_data)  # 레거시
                game_state['party_characters'].append(member_data)  # 새로운 표준
            
            # 저장 실행
            if save_manager.save_game(game_state):
                print("✅ 게임이 성공적으로 저장되었습니다!")
            else:
                print("❌ 게임 저장에 실패했습니다.")
                
        except Exception as e:
            print(f"❌ 저장 중 오류 발생: {e}")
    
    def load_game(self):
        """게임 불러오기 (패시브 효과 포함)"""
        if not SAVE_SYSTEM_AVAILABLE:
            print("💾 저장 시스템을 사용할 수 없습니다.")
            input("확인하려면 Enter를 누르세요...")
            return False
            
        try:
            from game.save_system import SaveManager
            
            save_manager = SaveManager()
            print(f"✅ SaveManager 인스턴스 생성 완료")
            
            saves = save_manager.get_save_list()
            
            if not saves:
                print("❌ 저장된 게임이 없습니다.")
                input("확인하려면 Enter를 누르세요...")
                return False
            
            # 저장 파일 선택 UI (간단한 버전)
            print("\n📁 저장된 게임 목록:")
            print("=" * 60)
            for i, save_info in enumerate(saves, 1):
                print(f"{i}. {save_info['name']} - {save_info['date']}")
            print("=" * 60)
            print("불러올 세이브 파일을 선택하세요...")
            
            choice = input("\n불러올 저장 파일 번호: ").strip()
            
            try:
                save_index = int(choice) - 1
                
                if 0 <= save_index < len(saves):
                    save_name = saves[save_index]['name']
                    print(f"\n🔄 '{save_name}' 파일을 불러오는 중...")
                    game_state = save_manager.load_game(save_name)
                    
                    if game_state:
                        print(f"✅ 세이브 파일 로드 완료!")
                        
                        # 게임 상태 복원 및 성공 여부 확인
                        if self.restore_game_state(game_state):
                            print("✅ 게임을 성공적으로 불러왔습니다!")
                            return True
                        else:
                            print("❌ 게임 상태 복원에 실패했습니다.")
                            input("메인 메뉴로 돌아가려면 Enter를 누르세요...")
                            return False
                    else:
                        print("❌ 게임 불러오기에 실패했습니다.")
                        input("메인 메뉴로 돌아가려면 Enter를 누르세요...")
                        return False
                else:
                    print(f"❌ 잘못된 번호입니다. 유효범위: 1-{len(saves)}")
                    input("확인하려면 Enter를 누르세요...")
                    return False
            except ValueError:
                print(f"❌ 숫자를 입력해주세요.")
                input("확인하려면 Enter를 누르세요...")
                return False
            except Exception as choice_error:
                print(f"❌ 선택 처리 중 오류: {choice_error}")
                import traceback
                traceback.print_exc()
                input("확인하려면 Enter를 누르세요...")
                return False
                
        except Exception as e:
            print(f"❌ 불러오기 중 오류 발생: {e}")
            print(f"📋 오류 상세 정보:")
            print(f"   - 오류 타입: {type(e).__name__}")
            print(f"   - 오류 메시지: {str(e)}")
            print(f"   - 발생 위치: load_game 함수")
            import traceback
            traceback.print_exc()
            print("\n오류 진단을 위해 위 정보를 확인하세요...")
            input("메인 메뉴로 돌아가려면 Enter를 누르세요...")
            return False
    
    def restore_game_state(self, game_state):
        """게임 상태 복원 (패시브 효과 포함)"""
        try:
            print("🔄 게임 상태 복원 중...")
            
            # 파티 복원 - 올바른 키 이름 사용
            self.party_manager.members.clear()
            party_data = game_state.get('party_characters', game_state.get('party', []))
            
            if not party_data:
                print("❌ 저장된 파티 정보가 없습니다.")
                return False
            
            restored_count = 0
            for member_data in party_data:
                # 캐릭터 재생성 (기본 캐릭터 생성 후 상태 복원)
                try:
                    if EASY_CREATOR_AVAILABLE:
                        from game.easy_character_creator import EasyCharacterCreator
                        creator = EasyCharacterCreator()
                        character = creator._create_single_character(member_data['character_class'], 1)
                    else:
                        # 폴백: 기본 캐릭터 생성
                        from game.character import Character
                        character = Character(member_data.get('name', '알 수 없음'))
                        character.character_class = member_data.get('character_class', '전사')
                    
                    character.name = member_data['name']
                    
                    # 저장된 상태 복원
                    character.level = member_data.get('level', 1)
                    character.experience = member_data.get('experience', 0)
                    character.current_hp = member_data.get('current_hp', character.max_hp)
                    character.max_hp = member_data.get('max_hp', character.max_hp)
                    character.current_mp = member_data.get('current_mp', character.max_mp)
                    character.max_mp = member_data.get('max_mp', character.max_mp)
                    character.wounds = member_data.get('wounds', 0)
                    
                    # 특성 복원
                    character.active_traits = []
                    trait_count = 0
                    traits_data = member_data.get('active_traits', [])
                    for trait_data in traits_data:
                        # 특성 객체 재생성 (간단한 버전)
                        try:
                            from game.character import CharacterTrait
                            trait = CharacterTrait(trait_data['name'], trait_data['description'], "passive", None)
                            character.active_traits.append(trait)
                            trait_count += 1
                        except Exception as trait_error:
                            print(f"⚠️ 특성 복원 실패: {trait_error}")
                            continue
                    
                    self.party_manager.add_member(character)
                    restored_count += 1
                    print(f"✅ {character.name} 복원 완료")
                    
                except Exception as e:
                    print(f"❌ 캐릭터 복원 중 오류: {e}")
                    continue
            
            if restored_count == 0:
                print("❌ 파티 멤버를 복원할 수 없습니다.")
                return False
            
            # 패시브 효과 복원
            self.party_passive_effects = game_state.get('party_passive_effects', [])
            if self.party_passive_effects:
                print(f"🌟 파티 패시브 효과 {len(self.party_passive_effects)}개를 복원했습니다.")
                try:
                    self.apply_passive_effects_to_party()
                    print("✅ 패시브 효과 적용 완료")
                except Exception as passive_error:
                    print(f"⚠️ 패시브 효과 적용 중 오류: {passive_error}")
            
            print(f"✅ 게임 상태 복원 완료 ({restored_count}명의 캐릭터)")
            for i, member in enumerate(self.party_manager.members, 1):
                print(f"     {i}. {member.name} (Lv.{member.level}, {member.character_class})")
            print("\n복원 상세 로그를 확인하세요...")
            input("게임을 시작하려면 Enter를 누르세요...")
            return True
            
        except Exception as e:
            print(f"❌ 게임 상태 복원 중 오류: {e}")
            import traceback
            traceback.print_exc()
            print(f"\n게임 상태 복원 실패 상세 정보:")
            print(f"오류 타입: {type(e).__name__}")
            print(f"오류 메시지: {str(e)}")
            print("\n오류 로그를 확인하세요...")
            input("아무 키나 눌러 계속...")
            return False
    
    def show_character_selection_legacy_fallback(self):
        """⚠️ 최종 폴백 캐릭터 생성 시스템 (매우 기본적) - 다른 모든 시스템 실패시에만 사용"""
        print(f"\n{bright_red('⚠️ 최종 폴백 모드: 기본 캐릭터 생성')}")
        print(f"{bright_yellow('💡 Easy Character Creator 사용을 강력히 권장합니다.')}")
        """캐릭터 선택 화면 (폴백 시스템)"""
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
        """수동 캐릭터 선택 - 커서 네비게이션"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            selected_characters = []
            
            for i in range(4):
                if len(selected_characters) >= len(unlocked_characters):
                    print(f"해금된 캐릭터가 부족합니다. {len(selected_characters)}명만 선택됩니다.")
                    break
                
                # 이미 선택된 캐릭터를 제외한 사용 가능한 캐릭터
                available_chars = [c for c in unlocked_characters if c not in selected_characters]
                
                if not available_chars:
                    break
                
                # 메뉴 옵션 생성
                options = []
                descriptions = []
                
                for char in available_chars:
                    upgrade_level = self.meta_progression.get_character_upgrade_level(char['name'])
                    upgrade_str = f" (업그레이드 Lv.{upgrade_level})" if upgrade_level > 0 else ""
                    
                    char_name = f"{char['name']} ({char['class']}){upgrade_str}"
                    options.append(char_name)
                    
                    stats_str = f"HP:{char['hp']} | P.ATK:{char['p_atk']} | M.ATK:{char['m_atk']} | "
                    stats_str += f"P.DEF:{char['p_def']} | M.DEF:{char['m_def']} | SPD:{char['speed']}"
                    description = f"{char['description']}\n{stats_str}\n특성: {', '.join(char['traits'])}"
                    descriptions.append(description)
                
                # 현재 선택된 파티원 표시
                selected_names = [c['name'] for c in selected_characters]
                title = f"🎯 파티원 선택 ({i+1}/4)\n현재 선택: {', '.join(selected_names) if selected_names else '없음'}"
                
                # 커서 메뉴 생성 및 실행
                menu = CursorMenu(title, options, descriptions, cancellable=True)
                result = menu.run()
                
                if result is None:  # 취소
                    if selected_characters:
                        # 이미 선택한 캐릭터가 있으면 확인
                        confirm_options = ["✅ 선택한 캐릭터로 시작", "❌ 처음부터 다시"]
                        confirm_descriptions = [
                            f"현재 선택된 {len(selected_characters)}명으로 파티를 구성합니다",
                            "캐릭터 선택을 처음부터 다시 시작합니다"
                        ]
                        
                        confirm_menu = CursorMenu("파티 구성 확인", confirm_options, confirm_descriptions, cancellable=True)
                        confirm_result = confirm_menu.run()
                        
                        if confirm_result == 0:  # 현재 선택으로 시작
                            break
                        elif confirm_result == 1:  # 다시 시작
                            selected_characters = []
                            i = -1  # 루프에서 +1 되므로 -1로 초기화
                            continue
                        else:  # 취소
                            return
                    else:
                        return  # 아무것도 선택하지 않고 취소
                
                # 선택된 캐릭터 추가
                selected_characters.append(available_chars[result])
                
                # 파티가 가득 찼으면 종료
                if len(selected_characters) >= 4:
                    break
            
            # 파티 생성
            if selected_characters:
                party_names = [c["name"] for c in selected_characters]
                self.create_party_from_names(party_names)
            else:
                print("캐릭터를 선택하지 않았습니다. 균형잡힌 파티로 시작합니다.")
                unlocked_names = self.meta_progression.get_unlocked_characters()
                party_names = self.get_balanced_unlocked_party(unlocked_names)
                self.create_party_from_names(party_names)
                
        except ImportError:
            # 폴백: 기존 수동 선택 시스템
            self.manual_character_selection_fallback(unlocked_characters)
    
    def manual_character_selection_fallback(self, unlocked_characters: List):
        """수동 캐릭터 선택 (폴백 시스템)"""
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
                
                # 🎵 파티 생성 완료 후 모험 준비 BGM
                if hasattr(self, 'sound_manager') and self.sound_manager:
                    self.sound_manager.play_bgm("prelude", loop=True)
                
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
        
        # 🎵 파티 생성 완료 후 모험 준비 BGM (prelude)
        self.safe_play_bgm("prelude", loop=True)
        
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
        
        # 특성 선택 단계는 easy_character_creator에서 이미 처리됨
        # 중복 호출 제거 - 특성은 캐릭터 생성 과정에서 이미 선택됨
        
        # 패시브 효과 선택은 start_adventure에서 진행
        
        self.keyboard.wait_for_key("🚀 아무 키나 눌러 모험을 시작하세요...")
        
    def create_party(self):
        """기본 파티 생성 (사용 안함 - show_character_selection으로 대체)"""
        pass
        
    def start_adventure(self):
        """모험 시작 - 간단한 게임 시작"""
        print(f"\n{bright_cyan('🌟 모험을 시작합니다!', True)}")
        
        # 영구 성장 보너스 적용
        self.apply_permanent_bonuses()
        
        # 🎵 던전 테마 BGM을 먼저 설정 (world.generate_level 전에)
        print("🎵 던전 BGM을 시작합니다...")
        try:
            # 초기 던전 BGM 설정
            self.safe_play_bgm("dungeon", loop=True)
            print(f"✅ BGM 재생 중: dungeon (1층 던전)")
        except Exception as e:
            print(f"⚠️ BGM 재생 실패: {e}")
        
    def get_class_emoji(self, character_class: str) -> str:
        """직업별 이모지 반환"""
        class_emojis = {
            # 기본 4클래스
            "전사": "⚔️",
            "아크메이지": "🔮",
            "궁수": "🏹",
            "도적": "🗡️",
            
            # 추가 클래스들
            "성기사": "🛡️",
            "암흑기사": "💀",
            "몽크": "👊",
            "바드": "🎵",
            "네크로맨서": "☠️",
            "용기사": "🐉",
            "검성": "⚡",
            "정령술사": "🌟",
            "암살자": "🔪",
            "기계공학자": "🔧",
            "무당": "🔯",
            "해적": "🏴‍☠️",
            "사무라이": "🗾",
            "드루이드": "🌿",
            "철학자": "📚",
            "시간술사": "⏰",
            "연금술사": "⚗️",
            "검투사": "🏛️",
            "기사": "🐎",
            "신관": "⛪",
            "마검사": "✨",
            "차원술사": "🌌",
            "광전사": "💥"
        }
        return class_emojis.get(character_class, "👤")
    
    def get_hp_color(self, current_hp: int, max_hp: int) -> str:
        """체력에 따른 색상 반환"""
        hp_ratio = current_hp / max_hp if max_hp > 0 else 0
        if hp_ratio > 0.7:
            return bright_green(f"{current_hp}/{max_hp}")
        elif hp_ratio > 0.3:
            return bright_yellow(f"{current_hp}/{max_hp}")
        else:
            return bright_red(f"{current_hp}/{max_hp}")
        
    def start_adventure(self, skip_passive_selection=False):
        """모험 시작 - 간단한 게임 시작"""
        print(f"\n{bright_cyan('🌟 모험을 시작합니다!', True)}")
        
        # 불러오기가 아닌 경우에만 파티 전체 패시브 효과 선택
        if not skip_passive_selection:
            print(f"\n{bright_cyan('🌟 파티 패시브 효과 선택')}")
            print(f"{bright_yellow('파티 전체에 적용되는 패시브 효과를 선택하세요!')}")
            print(f"{bright_white('💡 팁: 선택된 패시브는 이번 게임에만 적용되며, 세이브파일에 저장됩니다.')}")
            self.select_party_passive_effects()
        else:
            print(f"\n{bright_cyan('📋 저장된 패시브 효과가 적용되었습니다.')}")
            if self.party_passive_effects:
                print(f"🌟 활성 패시브: {len(self.party_passive_effects)}개")
        
        # 파티 상태 디버깅
        print(f"\n{bright_yellow('🔍 파티 상태 확인...')}")
        if not self.party_manager.members:
            print(f"{bright_red('❌ 파티 멤버가 없습니다!')}")
            return
        
        alive_count = 0
        for i, member in enumerate(self.party_manager.members, 1):
            hp_status = f"{member.current_hp}/{member.max_hp}"
            is_alive = member.current_hp > 0
            alive_count += 1 if is_alive else 0
            status = bright_green("살아있음") if is_alive else bright_red("사망")
            print(f"  {i}. {member.character_class}: HP {hp_status} - {status}")
        
        if alive_count == 0:
            print(f"{bright_red('❌ 모든 파티 멤버가 사망 상태입니다!')}")
            print(f"{bright_yellow('파티 멤버들의 HP를 복구합니다...')}")
            
            # 파티 멤버 HP 복구
            for member in self.party_manager.members:
                if member.current_hp <= 0:
                    member.current_hp = member.max_hp
                    print(f"  ✅ {member.character_class} HP 복구: {member.current_hp}/{member.max_hp}")
        
        print(f"{bright_green('✅ 파티 상태 정상!')}")
        
        # 영구 성장 보너스 적용
        self.apply_permanent_bonuses()
        
        # 🎵 던전 테마 BGM을 먼저 설정 (world.generate_level 전에)
        print("🎵 던전 BGM을 시작합니다...")
        try:
            # 초기 던전 BGM 설정
            self.safe_play_bgm("dungeon", loop=True)
            print(f"✅ BGM 재생 중: dungeon (1층 던전)")
        except Exception as e:
            print(f"⚠️ BGM 재생 실패: {e}")
        
        # 세계 생성 (BGM 설정 후에)
        self.world.generate_level()
        
        print("✅ 게임 초기화 완료!")
        
        # 파티 정보 개선된 표시
        print(f"\n{bright_green('=== 🎉 파티 정보 🎉 ===')}")
        for i, member in enumerate(self.party_manager.members, 1):
            emoji = self.get_class_emoji(member.character_class)
            hp_display = self.get_hp_color(member.current_hp, member.max_hp)
            
            # 캐릭터 이름이 클래스명과 다르면 실제 이름 표시, 같으면 클래스명만 표시
            if hasattr(member, 'name') and member.name and member.name != member.character_class:
                character_display = f"{bright_white(member.name)} {bright_white('(')}{ bright_yellow(member.character_class)}{bright_white(')')}"
            else:
                character_display = bright_cyan(f"[{member.character_class}]")
                
            print(f"  {bright_cyan(str(i))}. {emoji} {character_display} - HP: {hp_display}")
        
        print(f"\n{bright_yellow(f'🏢 현재 위치: 던전 {self.world.current_level}층')}")
        print(f"{bright_green('🚀 모험이 시작되었습니다!')}")
        print()
        print(f"{bright_cyan('═══ 🎮 게임 조작법 ═══')}")
        print(f"  {bright_yellow('📍 이동:')} {bright_white('WASD 키 또는 방향키')}")
        print(f"  {cyan('📋 메뉴:')} {bright_white('I')}(인벤토리) {bright_white('P')}(파티상태) {bright_white('F')}(필드활동)")  
        print(f"  {magenta('⚙️  기타:')} {bright_white('H')}(도움말) {bright_white('Q')}(종료) {bright_white('B')}(저장)")
        print(f"{bright_cyan('═══════════════════')}")
        print()
        
        # 실제 게임 루프 시작
        print(f"{bright_cyan('🎮 게임이 시작됩니다!')}")
        self.keyboard.wait_for_key("🔑 아무 키나 눌러 게임 시작...")
        
        # 메인 게임 루프 실행
        self.main_game_loop()
        
    def main_game_loop(self):
        """실제 게임 플레이 루프 - 개선된 시스템"""
        floors_cleared = 0
        enemies_defeated = 0
        
        # 게임 시작 시간 기록 (별조각 계산용)
        self.game_start_time = time.time()
        
        # 현재 층 정보 동기화
        self.current_floor = self.world.current_level
        
        while self.running:
            try:
                # 게임 화면 표시
                self.display.show_game_screen(self.party_manager, self.world)
                
                # 플레이어 입력 받기
                action = self.get_player_input()
                
                # 액션 처리
                self.process_action(action)
                
                # 층 클리어 확인 (계단 이용 시)
                if hasattr(self, '_floor_advanced') and self._floor_advanced:
                    floors_cleared = self.world.current_level - 1  # 시작 층이 1이므로
                    self._floor_advanced = False
                
                # 게임 오버 조건 체크
                if not self.party_manager.has_alive_members():
                    print(f"\n{bright_red('💀 파티가 전멸했습니다...', True)}")
                    print("게임 오버!")
                    
                    # 게임 종료 시 영구 진행상황 업데이트
                    self.update_permanent_progression(floors_cleared, enemies_defeated, died=True)
                    break
                    
            except KeyboardInterrupt:
                print(f"\n{bright_yellow('게임을 중단합니다.')}")
                # 중단 시에도 진행상황 저장
                self.update_permanent_progression(floors_cleared, enemies_defeated, died=False)
                break
        
        print(f"\n{bright_cyan('게임이 종료되었습니다.')}")
        
        # 메인 메뉴로 돌아가기 전 메인 BGM 재생
        try:
            if hasattr(self, 'sound_manager') and self.sound_manager:
                print("🎵 메인 테마 음악을 재생합니다...")
                self.sound_manager.play_bgm("main_theme", loop=True)
            elif hasattr(self, 'audio_system') and self.audio_system:
                print("🎵 메인 테마 음악을 재생합니다...")
                self.audio_system.play_bgm("main_theme", loop=True)
        except Exception as e:
            print(f"🔇 BGM 재생 실패: {e}")
        
        input("아무 키나 눌러 메인 메뉴로 돌아가기...")
    
    def update_permanent_progression(self, floors_cleared: int, enemies_defeated: int, died: bool):
        """영구 진행상황 업데이트 - 성과 기반 통합 보상 시스템"""
        try:
            # 사용된 패시브 개수 계산
            passives_used = len(getattr(self, 'party_passive_effects', []))
            
            # 새로운 성과 기반 별조각 계산 (GameWorld에서)
            star_fragments_earned = 0
            gold_earned = 0
            if hasattr(self, 'world') and hasattr(self.world, 'get_star_fragment_reward'):
                # 월드에서 성과 기반 별조각 계산
                star_fragments_earned = self.world.get_star_fragment_reward()
                # 골드 획득량 계산 (기존 파티 골드)
                if hasattr(self, 'party_manager') and hasattr(self.party_manager, 'gold'):
                    gold_earned = self.party_manager.gold
            else:
                # 폴백: 기본 계산법
                star_fragments_earned = floors_cleared * 5 + enemies_defeated
            
            # 메타 진행상황에 별조각 추가 (통합된 화폐 시스템)
            if hasattr(self, 'meta_progression'):
                current_fragments = self.meta_progression.data.get('star_fragments', 0)
                self.meta_progression.data['star_fragments'] = current_fragments + star_fragments_earned
                print(f"🌟 별조각 {star_fragments_earned}개를 획득했습니다! (총: {current_fragments + star_fragments_earned}개)")
                
                # 직업별 플레이 기록 업데이트
                if hasattr(self, 'party_manager') and self.party_manager.members:
                    class_stats = self.meta_progression.data.get('class_play_stats', {})
                    
                    for member in self.party_manager.members:
                        class_name = member.character_class
                        if class_name not in class_stats:
                            class_stats[class_name] = {
                                'plays': 0,
                                'best_floor': 0,
                                'total_kills': 0,
                                'total_floors': 0
                            }
                        
                        # 통계 업데이트
                        class_stats[class_name]['plays'] += 1
                        class_stats[class_name]['best_floor'] = max(class_stats[class_name]['best_floor'], floors_cleared)
                        class_stats[class_name]['total_kills'] += enemies_defeated
                        class_stats[class_name]['total_floors'] += floors_cleared
                    
                    self.meta_progression.data['class_play_stats'] = class_stats
                    self.meta_progression.save_data()  # 저장
            
            # 영구 진행상황에도 별조각 획득 (동일 수량)
            total_fragments = self.permanent_progression.on_run_end(
                floor_reached=floors_cleared,
                kills=enemies_defeated,
                died=died,
                star_fragments_earned=star_fragments_earned,  # 동일 수량의 별조각
                passives_used=passives_used
            )
            
            # 성과 세부 정보 출력
            print(f"\n📊 {bright_cyan('게임 결과')}")
            print(f"도달 층수: {floors_cleared}층")
            print(f"적 처치 수: {enemies_defeated}마리")
            
            # 성과 기반 정보 출력 (GameWorld 데이터 사용)
            if hasattr(self, 'world') and hasattr(self.world, 'performance_metrics'):
                metrics = self.world.performance_metrics
                print(f"완벽한 층: {metrics.get('perfect_floors', 0)}층")
                print(f"탐험률: {metrics.get('exploration_rate', 0):.1%}")
                print(f"무피해 전투: {metrics.get('no_damage_combats', 0)}회")
                print(f"성과 점수: {self.world.calculate_performance_score() if hasattr(self.world, 'calculate_performance_score') else 0}점")
            
            print(f"🌟 별조각: +{star_fragments_earned}개")
            if gold_earned > 0:
                print(f"💰 골드: {gold_earned}개 획득")
            print(f"총 별조각: {total_fragments}")
            
            # 세이브 파일 정리 (게임 종료 시에는 임시 세이브 삭제)
            try:
                if hasattr(self, 'save_manager') and self.save_manager:
                    # 오토세이브 파일 정리
                    import os
                    auto_save_dir = "auto_saves"
                    if os.path.exists(auto_save_dir):
                        for filename in os.listdir(auto_save_dir):
                            if filename.startswith("temp_") or filename.startswith("auto_"):
                                file_path = os.path.join(auto_save_dir, filename)
                                try:
                                    os.remove(file_path)
                                except:
                                    pass
                        print("🗑️ 임시 세이브 파일을 정리했습니다.")
            except:
                pass
            
            # 저장
            self.permanent_progression.save_to_file()
            
        except Exception as e:
            print(f"⚠️ 진행상황 업데이트 중 오류: {e}")
            # 최소한의 진행상황이라도 저장
            if hasattr(self, 'permanent_progression'):
                self.permanent_progression.on_run_end(floors_cleared, enemies_defeated, died)
        
    def load_game(self):
        """게임 불러오기"""
        try:
            if SAVE_SYSTEM_AVAILABLE and self.save_manager:
                # 1. 저장 파일 선택
                save_filename = save_system_show_load_menu(self.save_manager)
                if save_filename:
                    # 2. 선택된 파일에서 게임 상태 로드
                    game_state = self.save_manager.load_game(save_filename)
                    if game_state:
                        # 3. 게임 상태 복원
                        if self.restore_game_state(game_state):
                            print("✅ 게임을 성공적으로 불러왔습니다!")
                            return True
                        else:
                            print("❌ 게임 상태 복원에 실패했습니다.")
                            return False
                    else:
                        print("❌ 저장 파일을 읽는데 실패했습니다.")
                        return False
                else:
                    print("❌ 게임 불러오기가 취소되었습니다.")
                    return False
            else:
                print("⚠️ 저장 시스템을 사용할 수 없습니다.")
                return False
        except Exception as e:
            print(f"❌ 게임 불러오기 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_difficulty_menu(self):
        """난이도 선택 메뉴"""
        from config import game_config
        
        while True:
            print(f"\n{bright_cyan('⚔️ 난이도 설정')}")
            print("="*60)
            print(f"현재 난이도: {game_config.get_difficulty_display_name()}")
            print("="*60)
            
            difficulties = game_config.get_all_difficulties()
            
            for i, difficulty in enumerate(difficulties, 1):
                info = game_config.get_difficulty_info(difficulty)
                current = " ✓" if difficulty == game_config.current_difficulty else ""
                print(f"{i}. {info['color']} {info['name']}{current}")
                print(f"   {info['description']}")
                
                # 세부 설정 표시
                if difficulty == game_config.current_difficulty:
                    print(f"   📊 적 체력: {info['enemy_hp_multiplier']:.1f}배 | 적 공격력: {info['enemy_damage_multiplier']:.1f}배")
                    print(f"   ⚔️ 플레이어 공격력: {info['player_damage_multiplier']:.1f}배 | 별조각: {info['star_fragment_multiplier']:.1f}배")
                print()
            
            print("0. 돌아가기")
            
            try:
                choice = input("\n난이도를 선택하세요: ").strip()
                
                if choice == '0':
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(difficulties):
                        selected_difficulty = difficulties[idx]
                        game_config.set_difficulty(selected_difficulty)
                        print(f"\n✅ 난이도가 '{game_config.get_difficulty_display_name()}'로 변경되었습니다!")
                        input("아무 키나 눌러 계속...")
                        break
                    else:
                        print("❌ 잘못된 선택입니다.")
                else:
                    print("❌ 숫자를 입력해주세요.")
                    
            except ValueError:
                print("❌ 잘못된 입력입니다.")
            except KeyboardInterrupt:
                break

    def show_settings_menu(self):
        """게임 설정 메뉴 (커서 메뉴) - 확장된 설정 시스템"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, bright_white, yellow, green, red, cyan
            
            while True:
                # config.py에서 현재 설정 정보 가져오기
                difficulty = game_config.current_difficulty
                map_size = game_config.current_map_size
                
                # config.py의 설정 정보를 표시에 반영
                difficulty_info = game_config.get_difficulty_info()
                map_info = game_config.get_map_info()
                audio_settings = game_config.get_audio_settings()
                
                options = [
                    f"🎯 난이도: {yellow(game_config.get_difficulty_display_name())}",
                    f"🗺️ 맵 크기: {cyan(game_config.get_map_display_name())}",
                    f"🖥️ 화면 설정 (창 최대화: {'✅' if game_config.FULLSCREEN_MODE else '❌'})",
                    f"🔊 오디오 설정 (볼륨: {int(game_config.MASTER_VOLUME * 100)}%)", 
                    f"🎮 게임플레이 설정 (자동저장: {'✅' if game_config.AUTO_SAVE_ENABLED else '❌'})",
                    f"♿ 접근성 설정 (고대비: {'✅' if game_config.HIGH_CONTRAST_MODE else '❌'})",
                    "🎹 조작키 설정",
                    f"⚡ 성능 설정 (텍스처: {game_config.TEXTURE_QUALITY})",
                    f"📊 개발자 옵션 (모드: {'✅' if game_config.DEVELOPMENT_MODE else '❌'})",
                    "📋 모든 설정 보기",
                    f"✅ {bright_white('설정 완료')}"
                ]
                
                descriptions = [
                    "게임의 전투 난이도를 조정합니다 (적 능력치, 보상 등)",
                    "던전 맵의 크기를 조정합니다 (25x25 ~ 70x70)",
                    "화면 크기, 전체화면, 색상 등 디스플레이 관련 설정",
                    "BGM, 효과음, 볼륨 등 오디오 관련 설정",
                    "자동 저장, 애니메이션, 전투 속도 등 게임플레이 설정",
                    "텍스트 크기, 색상 대비, 속도 조절 등 접근성 설정",
                    "키보드 조작, 단축키 등 입력 관련 설정",
                    "프레임율, 최적화, 리소스 사용량 등 성능 설정", 
                    "개발 모드, 디버깅, 치트 등 개발자 전용 기능",
                    "현재 모든 설정 값을 한눈에 확인합니다",
                    "설정을 저장하고 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("⚙️ 게임 설정", options, descriptions, cancellable=True)
                result = menu.run()
                
                if result is None or result == 10:  # 설정 완료 또는 취소
                    # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                    self._play_main_menu_bgm()
                    break
                elif result == 0:  # 난이도 설정
                    self._show_difficulty_cursor_menu()
                elif result == 1:  # 맵 크기 설정
                    self._show_map_size_cursor_menu()
                elif result == 2:  # 화면 설정
                    self._show_display_settings_menu()
                elif result == 3:  # 오디오 설정
                    self._show_audio_settings_menu()
                elif result == 4:  # 게임플레이 설정
                    self._show_gameplay_settings_menu()
                elif result == 5:  # 접근성 설정
                    self._show_accessibility_settings_menu()
                elif result == 6:  # 조작키 설정
                    self._show_controls_settings_menu()
                elif result == 7:  # 성능 설정
                    self._show_performance_settings_menu()
                elif result == 8:  # 개발자 옵션
                    self._show_developer_options_menu()
                elif result == 9:  # 모든 설정 보기
                    self._show_all_settings_view()
                
        except ImportError:
            # 폴백: 기본 설정 메뉴
            self._show_basic_settings_menu()
    
    def _show_basic_settings_menu(self):
        """기본 설정 메뉴 (폴백)"""
        from config import game_config
        
        while True:
            print(f"\n{bright_cyan('⚙️ 게임 설정')}")
            print("="*60)
            print(f"현재 맵 크기: {game_config.get_map_size_display_name()}")
            print(f"현재 난이도: {game_config.get_difficulty_display_name()}")
            print("="*60)
            
            print("1. 맵 크기 설정")
            print("2. 난이도 설정")
            print("0. 돌아가기")
            
            try:
                choice = input("\n설정을 선택하세요: ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self.show_map_size_menu()
                elif choice == '2':
                    self.show_difficulty_menu()
                else:
                    print("❌ 잘못된 선택입니다.")
                    
            except ValueError:
                print("❌ 잘못된 입력입니다.")
            except KeyboardInterrupt:
                break
    
    def _show_difficulty_cursor_menu(self):
        """난이도 설정 커서 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, green, yellow, red
            
            difficulties = game_config.get_all_difficulties()
            current = game_config.current_difficulty
            
            options = []
            descriptions = []
            
            for diff in difficulties:
                diff_info = game_config.get_difficulty_info(diff)
                is_current = " ✅" if diff == current else ""
                options.append(f"{diff_info['color']} {diff_info['name']}{is_current}")
                
                # 상세 설명 생성
                desc_parts = [diff_info['description']]
                desc_parts.append(f"적 HP: {diff_info['enemy_hp_multiplier']}배")
                desc_parts.append(f"적 공격력: {diff_info['enemy_damage_multiplier']}배")
                desc_parts.append(f"별조각 보상: {diff_info['star_fragment_multiplier']}배")
                descriptions.append(" | ".join(desc_parts))
            
            menu = CursorMenu("🎯 난이도 설정", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is not None and 0 <= result < len(difficulties):
                selected_diff = difficulties[result]
                game_config.set_difficulty(selected_diff)
                print(f"{green('✅')} 난이도가 {game_config.get_difficulty_display_name()}로 변경되었습니다!")
                input("아무 키나 눌러 계속...")
                
        except ImportError:
            self.show_difficulty_menu()
    
    def _show_map_size_cursor_menu(self):
        """맵 크기 설정 커서 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, green
            
            map_sizes = game_config.get_all_map_sizes()
            current = game_config.current_map_size
            
            options = []
            descriptions = []
            
            for size in map_sizes:
                size_info = game_config.get_map_info(size)
                is_current = " ✅" if size == current else ""
                options.append(f"{size_info['color']} {size_info['name']}{is_current}")
                
                # 상세 설명 생성
                desc_parts = [size_info['description']]
                desc_parts.append(f"크기: {size_info['width']}x{size_info['height']}")
                desc_parts.append(f"방 개수: {size_info['room_count']}개")
                descriptions.append(" | ".join(desc_parts))
            
            menu = CursorMenu("🗺️ 맵 크기 설정", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is not None and 0 <= result < len(map_sizes):
                selected_size = map_sizes[result]
                game_config.set_map_size(selected_size)
                print(f"{green('✅')} 맵 크기가 {game_config.get_map_display_name()}로 변경되었습니다!")
                input("아무 키나 눌러 계속...")
                
        except ImportError:
            self.show_map_size_menu()
    
    def _show_sound_info(self):
        """사운드 설정 정보"""
        from game.color_text import bright_cyan, bright_white, yellow, green
        
        print(f"\n{bright_cyan('🔊 사운드 설정 정보')}")
        print("="*60)
        print(f"{bright_white('현재 사운드 시스템:')}")
        
        try:
            from game.audio_system import get_audio_manager
            audio_manager = get_audio_manager()
            if audio_manager and audio_manager.mixer_available:
                print(f"   🎵 BGM: {green('사용 가능')}")
                print(f"   🔊 효과음: {green('사용 가능')}")
                print(f"   📁 사운드 파일: sounds/ 폴더에서 관리")
            else:
                print(f"   🎵 BGM: {yellow('비활성화됨')}")
                print(f"   🔊 효과음: {yellow('비활성화됨')}")
                print(f"   ❓ pygame.mixer가 설치되지 않았거나 오디오 장치가 없습니다")
        except:
            print(f"   ❌ 오디오 시스템을 불러올 수 없습니다")
        
        print(f"\n{bright_white('사운드 파일 위치:')}")
        print("   • BGM: sounds/bgm/")
        print("   • 효과음: sounds/sfx/")
        print("   • 각 상황별로 자동 재생됩니다")
        
        input(f"\n{bright_white('아무 키나 눌러 계속...')}")
    
    def _show_save_info(self):
        """저장/로드 설정 정보"""
        from game.color_text import bright_cyan, bright_white, green, yellow
        
        print(f"\n{bright_cyan('💾 저장/로드 설정')}")
        print("="*60)
        print(f"{bright_white('자동 저장 시스템:')}")
        print(f"   • 게임 진행 중 자동으로 저장됩니다")
        print(f"   • 층 이동 시마다 백업 생성")
        print(f"   • 사망 시 직전 상태 복구 가능")
        
        print(f"\n{bright_white('저장 파일 위치:')}")
        print("   • 메인 저장: saves/")
        print("   • 자동 백업: auto_saves/")
        print("   • 메타 진행: meta_progress.json")
        print("   • 영구 강화: permanent_progress.json")
        
        print(f"\n{bright_white('백업 시스템:')}")
        print("   • 게임 시작 시 자동 백업 생성")
        print("   • 최대 5개까지 백업 보관")
        print("   • 사망 시 복구 옵션 제공")
        
        input(f"\n{bright_white('아무 키나 눌러 계속...')}")
    
    def _show_controls_info(self):
        """조작키 안내"""
        from game.color_text import bright_cyan, bright_white, yellow, green, cyan
        
        print(f"\n{bright_cyan('🎮 게임 조작키 안내')}")
        print("="*60)
        
        print(f"{bright_white('기본 이동:')}")
        print("   W/A/S/D 또는 화살표키: 이동")
        print("   Q: 대각선 이동 (왼쪽 위)")
        print("   E: 대각선 이동 (오른쪽 위)")
        print("   Z: 대각선 이동 (왼쪽 아래)")
        print("   C: 대각선 이동 (오른쪽 아래)")
        
        print(f"\n{bright_white('전투 및 상호작용:')}")
        print("   스페이스바: 턴 넘기기/대기")
        print("   Enter: 확인/상호작용")
        print("   F: 적에게 공격")
        print("   G: 아이템 줍기")
        print("   Tab: 다음 타겟 선택")
        
        print(f"\n{bright_white('소모품 및 정보:')}")
        print("   I: 인벤토리 열기")
        print("   P: 파티 상태 확인")
        print("   M: 미니맵 보기")
        print("   H: 도움말")
        
        print(f"\n{bright_white('시스템:')}")
        print("   ESC: 일시정지/메뉴")
        print("   Ctrl+S: 수동 저장")
        print("   Ctrl+Q: 게임 종료")
        
        input(f"\n{bright_white('아무 키나 눌러 계속...')}")
    
    def _show_dev_mode_info(self):
        """개발 모드 정보"""
        from game.color_text import bright_cyan, bright_white, green, red, yellow
        from config import game_config
        
        print(f"\n{bright_cyan('📊 개발 모드 정보')}")
        print("="*60)
        
        dev_mode = game_config.DEVELOPMENT_MODE
        mode_text = f"{green('활성화됨')}" if dev_mode else f"{red('비활성화됨')}"
        print(f"{bright_white('개발 모드:')} {mode_text}")
        
        if dev_mode:
            print(f"\n{bright_white('활성화된 기능들:')}")
            print(f"   ✅ 모든 직업 해금 ({len(game_config.get_available_classes())}/27개)")
            print(f"   ✅ 모든 패시브 특성 해금")
            print(f"   ✅ 디버그 정보 표시")
            print(f"   ✅ 테스트 명령어 사용 가능")
            print(f"   ✅ 개발자 도구 접근")
            
            print(f"\n{bright_white('개발자 명령어:')}")
            print("   • 치트 코드 사용 가능")
            print("   • 즉시 레벨업/아이템 생성")
            print("   • 맵 생성 테스트")
            print("   • AI 행동 분석")
        else:
            print(f"\n{bright_white('일반 모드 특징:')}")
            print(f"   • 기본 4개 직업만 해금")
            print(f"   • 특성은 게임 플레이로 해금")
            print(f"   • 균형잡힌 게임 진행")
            print(f"   • 정상적인 난이도 곡선")
            
            print(f"\n{yellow('개발 모드 활성화 방법:')}")
            print("   • 게임 폴더의 '개발모드.bat' 실행")
            print("   • 또는 config.py에서 DEVELOPMENT_MODE = True 설정")
        
        input(f"\n{bright_white('아무 키나 눌러 계속...')}")
        """맵 크기 설정 메뉴"""
        from config import game_config
        
        while True:
            print(f"\n{bright_cyan('🗺️  맵 크기 설정')}")
            print("="*60)
            print(f"현재 맵 크기: {game_config.get_map_size_display_name()}")
            print("="*60)
            
            map_sizes = game_config.get_all_map_sizes()
            
            for i, map_size in enumerate(map_sizes, 1):
                info = game_config.get_map_size_info(map_size)
                current = " ✓" if map_size == game_config.current_map_size else ""
                width = info.get('width', 35)
                height = info.get('height', 35)
                print(f"{i}. {info['name']} ({width}x{height}){current}")
                print(f"   {info['description']}")
                print()
            
            print("0. 돌아가기")
            
            try:
                choice = input("\n맵 크기를 선택하세요: ").strip()
                
                if choice == '0':
                    break
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(map_sizes):
                        selected_size = map_sizes[idx]
                        game_config.set_map_size(selected_size)
                        print(f"\n✅ 맵 크기가 '{game_config.get_map_size_display_name()}'로 변경되었습니다!")
                        input("아무 키나 눌러 계속...")
                        break
                    else:
                        print("❌ 잘못된 선택입니다.")
                else:
                    print("❌ 숫자를 입력해주세요.")
                    
            except ValueError:
                print("❌ 잘못된 입력입니다.")
            except KeyboardInterrupt:
                break

    def show_permanent_progression_menu(self):
        """영구 성장 메뉴 표시"""
        try:
            # 영구 진행 시스템 메뉴 표시
            if hasattr(self.permanent_progression, 'show_menu'):
                self.permanent_progression.show_menu()
            else:
                print("📊 영구 성장 시스템")
                print("="*50)
                print(f"총 플레이 횟수: {self.permanent_progression.total_runs}")
                print(f"최고 층수: {self.permanent_progression.best_floor}")
                print(f"별조각: {self.permanent_progression.star_fragments}")
                print("="*50)
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        except Exception as e:
            print(f"❌ 영구 성장 메뉴 표시 중 오류: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")

    def _show_display_settings_menu(self):
        """화면 설정 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu, MenuItem
            from config import game_config
            from game.color_text import bright_cyan, green, red, yellow
            
            while True:
                current_width, current_height = game_config.get_window_size()
                window_size_text = f"{current_width}x{current_height}" if current_width and current_height else "(전체화면)"
                
                options = [
                    f"📺 창 최대화: {green('켜짐') if game_config.FULLSCREEN_MODE else red('꺼짐')}",
                    f"📏 창 크기: {window_size_text}",
                    f"🎚️ UI 크기: {int(game_config.UI_SCALE * 100)}%",
                    f"⚡ FPS 제한: {game_config.FPS_LIMIT}",
                    f"🔄 수직 동기화: {green('켜짐') if getattr(game_config, 'VSYNC_ENABLED', False) else red('꺼짐')}",
                    f"🌈 안티 에일리어싱: {green('켜짐') if game_config.ANTI_ALIASING else red('꺼짐')}",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    "게임 창을 최대 크기로 확장합니다",
                    "창 모드에서의 게임 창 크기를 조정합니다" if not game_config.FULLSCREEN_MODE else "창 최대화 모드에서는 창 크기를 변경할 수 없습니다",
                    "UI 요소들의 크기를 조정합니다 (50% ~ 200%)",
                    "초당 프레임 수를 제한합니다 (30-144)",
                    "화면 찢어짐을 방지합니다",
                    "텍스트와 선의 가장자리를 부드럽게 합니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("🖥️ 화면 설정", options, descriptions)
                result = menu.run()
                
                if result is None or result == 6:
                    break
                elif result == 0:  # 창 최대화
                    game_config.FULLSCREEN_MODE = not game_config.FULLSCREEN_MODE
                    game_config.save_settings()
                    print(f"✅ 창 최대화가 {'켜짐' if game_config.FULLSCREEN_MODE else '꺼짐'}으로 설정되었습니다.")
                    
                    # 창 최대화 설정 즉시 적용
                    if game_config.FULLSCREEN_MODE:
                        print("🖥️ 창 최대화 모드를 적용 중...")
                        game_config.apply_terminal_fullscreen()
                    else:
                        print("💡 창 크기를 다시 조정하려면 수동으로 터미널 창 크기를 변경하세요.")
                    
                    input("아무 키나 눌러 계속...")
                elif result == 1:  # 창 크기
                    if not game_config.FULLSCREEN_MODE:
                        self._change_window_size()
                    else:
                        print("❌ 창 최대화 모드에서는 창 크기를 변경할 수 없습니다.")
                        input("아무 키나 눌러 계속...")
                elif result == 2:  # UI 크기
                    self._change_ui_scale()
                elif result == 3:  # FPS 제한
                    self._change_fps_limit()
                elif result == 4:  # 수직 동기화
                    # VSYNC_ENABLED 속성이 없다면 생성
                    if not hasattr(game_config, 'VSYNC_ENABLED'):
                        game_config.VSYNC_ENABLED = False
                    game_config.VSYNC_ENABLED = not game_config.VSYNC_ENABLED
                    game_config.save_settings()
                    print(f"✅ 수직 동기화가 {'켜짐' if game_config.VSYNC_ENABLED else '꺼짐'}으로 설정되었습니다.")
                elif result == 5:  # 안티 에일리어싱
                    game_config.ANTI_ALIASING = not game_config.ANTI_ALIASING
                    game_config.save_settings()
                    print(f"✅ 안티 에일리어싱이 {'켜짐' if game_config.ANTI_ALIASING else '꺼짐'}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                    
        except Exception as e:
            print(f"❌ 화면 설정 메뉴 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _show_audio_settings_menu(self):
        """오디오 설정 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, green, red, yellow
            
            while True:
                options = [
                    f"🔈 마스터 볼륨: {int(game_config.MASTER_VOLUME * 100)}%",
                    f"🎼 BGM 볼륨: {int(game_config.BGM_VOLUME * 100)}%",
                    f"🎧 효과음 볼륨: {int(game_config.SFX_VOLUME * 100)}%",
                    f"🎤 음성 볼륨: {int(game_config.VOICE_VOLUME * 100)}%",
                    f"🎶 오디오 품질: {yellow(game_config.AUDIO_QUALITY)}",
                    "🔊 오디오 테스트",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    "전체 오디오 볼륨을 조절합니다 (0-100%)",
                    "배경 음악 볼륨을 조절합니다 (0-100%)",
                    "효과음 볼륨을 조절합니다 (0-100%)",
                    "음성 볼륨을 조절합니다 (0-100%)",
                    "오디오 품질을 설정합니다 (low/medium/high)",
                    "현재 볼륨 설정으로 테스트 사운드를 재생합니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("🔊 오디오 설정", options, descriptions)
                result = menu.run()
                
                if result is None or result == 6:
                    break
                elif result == 0:  # 마스터 볼륨
                    self._change_master_volume()
                elif result == 1:  # BGM 볼륨
                    self._change_bgm_volume()
                elif result == 2:  # 효과음 볼륨
                    self._change_sfx_volume()
                elif result == 3:  # 음성 볼륨
                    self._change_voice_volume()
                elif result == 4:  # 오디오 품질
                    self._change_audio_quality()
                elif result == 5:  # 오디오 테스트
                    self._test_audio()
                    
        except Exception as e:
            print(f"❌ 오디오 설정 메뉴 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _show_gameplay_settings_menu(self):
        """게임플레이 설정 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, green, red, yellow
            
            while True:
                options = [
                    f"💾 자동 저장: {green('켜짐') if game_config.AUTO_SAVE_ENABLED else red('꺼짐')}",
                    f"⏱️ 자동 저장 간격: {game_config.AUTO_SAVE_INTERVAL//60}분",
                    f"🎓 튜토리얼: {green('켜짐') if game_config.TUTORIAL_ENABLED else red('꺼짐')}",
                    f"💡 툴팁: {green('켜짐') if game_config.TOOLTIPS_ENABLED else red('꺼짐')}",
                    f"🔒 포커스 잃을 시 일시정지: {green('켜짐') if game_config.PAUSE_ON_LOST_FOCUS else red('꺼짐')}",
                    f"❓ 종료 시 확인: {green('켜짐') if game_config.CONFIRM_EXIT else red('꺼짐')}",
                    f"🎥 카메라 부드러움: {green('켜짐') if game_config.CAMERA_SMOOTHING else red('꺼짐')}",
                    f"⏳ ATB 시스템 설정",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    f"일정 간격마다 자동으로 게임을 저장합니다 ({game_config.AUTO_SAVE_INTERVAL//60}분 간격)",
                    "자동 저장이 수행되는 시간 간격을 설정합니다",
                    "게임 시작 시 튜토리얼을 표시합니다",
                    "UI 요소에 대한 설명 툴팁을 표시합니다",
                    "게임 창이 포커스를 잃으면 자동으로 일시정지합니다",
                    "게임 종료 시 확인 대화상자를 표시합니다",
                    "카메라 이동을 부드럽게 만듭니다",
                    "ATB 게이지 애니메이션과 속도를 설정합니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("🎮 게임플레이 설정", options, descriptions)
                result = menu.run()
                
                if result is None or result == 8:  # 돌아가기 (인덱스 변경)
                    break
                elif result == 0:  # 자동 저장
                    game_config.toggle_auto_save()
                    print(f"✅ 자동 저장이 {'켜짐' if game_config.AUTO_SAVE_ENABLED else '꺼짐'}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 1:  # 자동 저장 간격
                    self._change_auto_save_interval()
                elif result == 2:  # 튜토리얼
                    game_config.toggle_tutorial()
                    print(f"✅ 튜토리얼이 {'켜짐' if game_config.TUTORIAL_ENABLED else '꺼짐'}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 3:  # 툴팁
                    game_config.toggle_tooltips()
                    print(f"✅ 툴팁이 {'켜짐' if game_config.TOOLTIPS_ENABLED else '꺼짐'}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 4:  # 포커스 잃을 시 일시정지
                    game_config.PAUSE_ON_LOST_FOCUS = not game_config.PAUSE_ON_LOST_FOCUS
                    game_config.save_settings()
                    print(f"✅ 포커스 잃을 시 일시정지가 {'켜짐' if game_config.PAUSE_ON_LOST_FOCUS else '꺼짐'}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 5:  # 종료 시 확인
                    game_config.CONFIRM_EXIT = not game_config.CONFIRM_EXIT
                    game_config.save_settings()
                    print(f"✅ 종료 시 확인이 {'켜짐' if game_config.CONFIRM_EXIT else '꺼짐'}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 6:  # 카메라 부드러움
                    game_config.CAMERA_SMOOTHING = not game_config.CAMERA_SMOOTHING
                    game_config.save_settings()
                    print(f"✅ 카메라 부드러움이 {'켜짐' if game_config.CAMERA_SMOOTHING else '꺼짐'}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 7:  # ATB 시스템 설정
                    self._show_atb_settings_menu()
                    
        except Exception as e:
            print(f"❌ 게임플레이 설정 메뉴 오류: {e}")

    def _show_atb_settings_menu(self):
        """ATB 시스템 설정 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.settings import game_settings
            from game.color_text import bright_cyan, green, red, yellow
            
            while True:
                # ATB 설정 현재 상태 가져오기
                atb_settings = game_settings.get_section("atb")
                
                options = [
                    f"🎬 ATB 애니메이션: {green('켜짐') if atb_settings.get('animation_enabled', True) else red('꺼짐')}",
                    f"🎯 애니메이션 FPS: {atb_settings.get('animation_fps', 20)}",
                    f"⚡ ATB 업데이트 속도: {atb_settings.get('update_speed', 1.0)}x",
                    f"📊 퍼센트 표시: {green('켜짐') if atb_settings.get('show_percentage', True) else red('꺼짐')}",
                    f"🌊 부드러운 애니메이션: {green('켜짐') if atb_settings.get('smooth_animation', True) else red('꺼짐')}",
                    "🔄 ATB 설정 초기화",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    "ATB 게이지 애니메이션을 켜거나 끕니다",
                    "ATB 애니메이션의 프레임 속도를 조정합니다 (10-60 FPS)",
                    "ATB 게이지 증가 속도를 조정합니다 (0.5x-3.0x)",
                    "ATB 게이지에 퍼센트를 표시합니다",
                    "ATB 게이지 변화를 부드럽게 애니메이션으로 표시합니다",
                    "모든 ATB 설정을 기본값으로 되돌립니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("⏳ ATB 시스템 설정", options, descriptions)
                result = menu.run()
                
                if result is None or result == 6:  # 돌아가기
                    break
                elif result == 0:  # ATB 애니메이션 토글
                    game_settings.toggle_setting("atb", "animation_enabled")
                    print("✅ ATB 애니메이션 설정이 변경되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 1:  # FPS 변경
                    self._change_atb_fps()
                elif result == 2:  # 업데이트 속도 변경
                    self._change_atb_speed()
                elif result == 3:  # 퍼센트 표시 토글
                    game_settings.toggle_setting("atb", "show_percentage")
                    print("✅ 퍼센트 표시 설정이 변경되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 4:  # 부드러운 애니메이션 토글
                    game_settings.toggle_setting("atb", "smooth_animation")
                    print("✅ 부드러운 애니메이션 설정이 변경되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 5:  # ATB 설정 초기화
                    self._reset_atb_settings()
                    
        except Exception as e:
            print(f"❌ ATB 설정 메뉴 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_atb_fps(self):
        """ATB 애니메이션 FPS 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.settings import game_settings
            
            fps_options = ["10 FPS", "15 FPS", "20 FPS (기본)", "30 FPS", "60 FPS"]
            fps_descriptions = [
                "낮은 FPS - 부드럽지 않지만 성능 절약",
                "보통 FPS - 적당한 성능과 품질",
                "기본 FPS - 권장 설정",
                "높은 FPS - 부드럽지만 더 많은 자원 사용",
                "최고 FPS - 매우 부드럽지만 높은 자원 사용"
            ]
            
            menu = CursorMenu("ATB 애니메이션 FPS 선택", fps_options, fps_descriptions)
            result = menu.run()
            
            fps_values = [10, 15, 20, 30, 60]
            if result is not None and 0 <= result < len(fps_values):
                game_settings.set("atb", "animation_fps", fps_values[result])
                # frame_delay도 자동으로 조정
                frame_delay = 1.0 / fps_values[result]
                game_settings.set("atb", "frame_delay", frame_delay)
                print(f"✅ ATB 애니메이션 FPS가 {fps_values[result]}로 변경되었습니다.")
                input("아무 키나 눌러 계속...")
        except Exception as e:
            print(f"❌ FPS 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_atb_speed(self):
        """ATB 업데이트 속도 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.settings import game_settings
            
            speed_options = [
                "0.5x (매우 느림)", "0.75x (느림)", "1.0x (기본)", 
                "1.25x (조금 빠름)", "1.5x (빠름)", "2.0x (매우 빠름)", "3.0x (극한)"
            ]
            speed_descriptions = [
                "ATB가 매우 천천히 증가합니다",
                "ATB가 천천히 증가합니다", 
                "기본 ATB 증가 속도입니다",
                "ATB가 조금 빠르게 증가합니다",
                "ATB가 빠르게 증가합니다",
                "ATB가 매우 빠르게 증가합니다",
                "ATB가 극한으로 빠르게 증가합니다"
            ]
            
            menu = CursorMenu("ATB 업데이트 속도 선택", speed_options, speed_descriptions)
            result = menu.run()
            
            speed_values = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
            if result is not None and 0 <= result < len(speed_values):
                game_settings.set("atb", "update_speed", speed_values[result])
                print(f"✅ ATB 업데이트 속도가 {speed_values[result]}x로 변경되었습니다.")
                input("아무 키나 눌러 계속...")
        except Exception as e:
            print(f"❌ 속도 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _reset_atb_settings(self):
        """ATB 설정 초기화"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.settings import game_settings
            
            confirm_options = ["예, 초기화합니다", "아니오, 취소합니다"]
            confirm_descriptions = ["모든 ATB 설정을 기본값으로 되돌립니다", "초기화를 취소하고 돌아갑니다"]
            
            menu = CursorMenu("ATB 설정을 초기화하시겠습니까?", confirm_options, confirm_descriptions)
            result = menu.run()
            
            if result == 0:  # 예
                # 기본 ATB 설정으로 초기화
                game_settings.set("atb", "animation_enabled", True)
                game_settings.set("atb", "animation_fps", 20)
                game_settings.set("atb", "update_speed", 1.0)
                game_settings.set("atb", "show_percentage", True)
                game_settings.set("atb", "smooth_animation", True)
                game_settings.set("atb", "frame_delay", 0.05)
                print("✅ ATB 설정이 초기화되었습니다.")
                input("아무 키나 눌러 계속...")
        except Exception as e:
            print(f"❌ ATB 설정 초기화 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _show_accessibility_settings_menu(self):
        """접근성 설정 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, green, red, yellow
            
            while True:
                options = [
                    f"📱 큰 텍스트: {green('켜짐') if game_config.LARGE_TEXT_MODE else red('꺼짐')}",
                    f"🌓 고대비 모드: {green('켜짐') if game_config.HIGH_CONTRAST_MODE else red('꺼짐')}",
                    f"🔤 색맹 지원: {yellow(game_config.COLOR_BLIND_MODE)}",
                    f"🔄 화면 읽기 도구: {green('켜짐') if game_config.SCREEN_READER_SUPPORT else red('꺼짐')}",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    "텍스트를 더 크게 표시합니다",
                    "색상 대비를 높여 가독성을 향상시킵니다",
                    "색맹 사용자를 위한 색상 구분을 지원합니다",
                    "화면 읽기 도구와의 호환성을 향상시킵니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("♿ 접근성 설정", options, descriptions)
                result = menu.run()
                
                if result is None or result == 4:
                    break
                elif result == 0:  # 큰 텍스트
                    game_config.LARGE_TEXT_MODE = not game_config.LARGE_TEXT_MODE
                    game_config.save_settings()
                    print(f"✅ 큰 텍스트가 {'켜짐' if game_config.LARGE_TEXT_MODE else '꺼짐'}으로 설정되었습니다.")
                elif result == 1:  # 고대비 모드
                    game_config.toggle_high_contrast()
                    game_config.save_settings()
                    print(f"✅ 고대비 모드가 {'켜짐' if game_config.HIGH_CONTRAST_MODE else '꺼짐'}으로 설정되었습니다.")
                elif result == 2:  # 색맹 지원
                    self._change_colorblind_mode()
                elif result == 3:  # 화면 읽기 도구
                    game_config.SCREEN_READER_SUPPORT = not game_config.SCREEN_READER_SUPPORT
                    game_config.save_settings()
                    print(f"✅ 화면 읽기 도구 지원이 {'켜짐' if game_config.SCREEN_READER_SUPPORT else '꺼짐'}으로 설정되었습니다.")
                    
        except Exception as e:
            print(f"❌ 접근성 설정 메뉴 오류: {e}")

    def _show_controls_settings_menu(self):
        """조작키 설정 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, green, red, yellow
            
            while True:
                options = [
                    f"⌨️ 키 반복 지연: {int(game_config.KEYBOARD_REPEAT_DELAY * 1000)}ms",
                    f"🎮 게임패드 지원: {green('켜짐') if game_config.GAMEPAD_ENABLED else red('꺼짐')}",
                    f"⏰ 진동 효과: {green('켜짐') if game_config.VIBRATION_ENABLED else red('꺼짐')}",
                    f"🖱️ 마우스 감도: {game_config.MOUSE_SENSITIVITY}",
                    "🎹 키 매핑 확인",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    "키를 눌렀을 때 반복되기까지의 지연 시간",
                    "게임패드 조작을 지원합니다",
                    "게임패드 진동 효과를 활성화합니다",
                    "마우스 감도를 조절합니다",
                    "현재 설정된 키 매핑을 확인합니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("🎹 조작키 설정", options, descriptions)
                result = menu.run()
                
                if result is None or result == 5:
                    break
                elif result == 0:  # 키 반복 지연
                    self._change_key_repeat_delay()
                elif result == 1:  # 게임패드 지원
                    game_config.GAMEPAD_ENABLED = not game_config.GAMEPAD_ENABLED
                    game_config.save_settings()
                    print(f"✅ 게임패드 지원이 {'켜짐' if game_config.GAMEPAD_ENABLED else '꺼짐'}으로 설정되었습니다.")
                elif result == 2:  # 진동 효과
                    game_config.VIBRATION_ENABLED = not game_config.VIBRATION_ENABLED
                    game_config.save_settings()
                    print(f"✅ 진동 효과가 {'켜짐' if game_config.VIBRATION_ENABLED else '꺼짐'}으로 설정되었습니다.")
                elif result == 3:  # 마우스 감도
                    self._change_mouse_sensitivity()
                elif result == 4:  # 키 매핑 확인
                    self._show_key_mappings()
                    
        except Exception as e:
            print(f"❌ 조작키 설정 메뉴 오류: {e}")

    def _show_performance_settings_menu(self):
        """성능 설정 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, green, red, yellow
            
            while True:
                options = [
                    f"🖼️ 프레임율 제한: {game_config.FPS_LIMIT}",
                    f"🎨 텍스처 품질: {yellow(game_config.TEXTURE_QUALITY)}",
                    f"🌑 그림자 품질: {yellow(game_config.SHADOW_QUALITY)}",
                    f"✨ 파티클 효과: {green('켜짐') if game_config.PARTICLE_EFFECTS else red('꺼짐')}",
                    f"💫 모션 블러: {green('켜짐') if game_config.MOTION_BLUR else red('꺼짐')}",
                    f"🌈 안티 에일리어싱: {green('켜짐') if game_config.ANTI_ALIASING else red('꺼짐')}",
                    "📈 시스템 정보 확인",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    "게임 프레임율을 제한합니다 (30-144)",
                    "텍스처 해상도를 설정합니다",
                    "그림자 렌더링 품질을 설정합니다",
                    "파티클 효과를 활성화합니다",
                    "화면 움직임 블러 효과를 활성화합니다",
                    "텍스트와 선의 가장자리를 부드럽게 합니다",
                    "현재 시스템 사양과 상태를 확인합니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("⚡ 성능 설정", options, descriptions)
                result = menu.run()
                
                if result is None or result == 7:
                    break
                elif result == 0:  # 프레임율 제한
                    self._change_fps_limit()
                elif result == 1:  # 텍스처 품질
                    self._change_texture_quality()
                elif result == 2:  # 그림자 품질
                    self._change_shadow_quality()
                elif result == 3:  # 파티클 효과
                    game_config.PARTICLE_EFFECTS = not game_config.PARTICLE_EFFECTS
                    game_config.save_settings()
                    print(f"✅ 파티클 효과가 {'켜짐' if game_config.PARTICLE_EFFECTS else '꺼짐'}으로 설정되었습니다.")
                elif result == 4:  # 모션 블러
                    game_config.MOTION_BLUR = not game_config.MOTION_BLUR
                    game_config.save_settings()
                    print(f"✅ 모션 블러가 {'켜짐' if game_config.MOTION_BLUR else '꺼짐'}으로 설정되었습니다.")
                elif result == 5:  # 안티 에일리어싱
                    game_config.ANTI_ALIASING = not game_config.ANTI_ALIASING
                    game_config.save_settings()
                    print(f"✅ 안티 에일리어싱이 {'켜짐' if game_config.ANTI_ALIASING else '꺼짐'}으로 설정되었습니다.")
                elif result == 6:  # 시스템 정보
                    self._show_system_info()
                    
        except Exception as e:
            print(f"❌ 성능 설정 메뉴 오류: {e}")

    def _show_developer_options_menu(self):
        """개발자 옵션 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            from game.color_text import bright_cyan, green, red, yellow
            
            while True:
                options = [
                    f"🔧 개발 모드: {green('켜짐') if game_config.DEVELOPMENT_MODE else red('꺼짐')}",
                    f"🐛 디버그 모드: {green('켜짐') if getattr(game_config, 'DEBUG_MODE', False) else red('꺼짐')}",
                    f"👁️ 데미지 계산 표시: {green('켜짐') if getattr(game_config, 'SHOW_DAMAGE_CALCULATIONS', False) else red('꺼짐')}",
                    f"♾️ 무한 자원: {green('켜짐') if getattr(game_config, 'INFINITE_RESOURCES', False) else red('꺼짐')}",
                    "📊 개발자 정보 확인",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    "개발자 전용 기능들을 활성화합니다 (모든 직업 해금 등)",
                    "상세한 디버그 정보를 표시합니다",
                    "전투 시 데미지 계산 과정을 표시합니다",
                    "HP, MP, 골드 등이 무제한으로 사용됩니다",
                    "현재 개발자 설정 상태를 확인합니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("📊 개발자 옵션", options, descriptions)
                result = menu.run()
                
                if result is None or result == 5:  # 돌아가기
                    break
                elif result == 0:  # 개발 모드 토글
                    game_config.toggle_development_mode()
                    status = "켜짐" if game_config.DEVELOPMENT_MODE else "꺼짐"
                    print(f"✅ 개발 모드가 {status}으로 설정되었습니다.")
                    if game_config.DEVELOPMENT_MODE:
                        print("🔓 모든 직업과 특성이 해금되었습니다!")
                        print("⚠️ 게임을 재시작하면 완전히 적용됩니다.")
                    else:
                        print("🔒 기본 4개 직업만 사용 가능합니다.")
                        print("⚠️ 게임을 재시작하면 완전히 적용됩니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 1:  # 디버그 모드 토글
                    # DEBUG_MODE가 없으면 추가
                    if not hasattr(game_config, 'DEBUG_MODE'):
                        game_config.DEBUG_MODE = False
                    game_config.DEBUG_MODE = not game_config.DEBUG_MODE
                    game_config.save_settings()
                    status = "켜짐" if game_config.DEBUG_MODE else "꺼짐"
                    print(f"✅ 디버그 모드가 {status}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 2:  # 데미지 계산 표시 토글
                    # SHOW_DAMAGE_CALCULATIONS가 없으면 추가
                    if not hasattr(game_config, 'SHOW_DAMAGE_CALCULATIONS'):
                        game_config.SHOW_DAMAGE_CALCULATIONS = False
                    game_config.SHOW_DAMAGE_CALCULATIONS = not game_config.SHOW_DAMAGE_CALCULATIONS
                    game_config.save_settings()
                    status = "켜짐" if game_config.SHOW_DAMAGE_CALCULATIONS else "꺼짐"
                    print(f"✅ 데미지 계산 표시가 {status}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 3:  # 무한 자원 토글
                    # INFINITE_RESOURCES가 없으면 추가
                    if not hasattr(game_config, 'INFINITE_RESOURCES'):
                        game_config.INFINITE_RESOURCES = False
                    game_config.INFINITE_RESOURCES = not game_config.INFINITE_RESOURCES
                    game_config.save_settings()
                    status = "켜짐" if game_config.INFINITE_RESOURCES else "꺼짐"
                    print(f"✅ 무한 자원이 {status}으로 설정되었습니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 4:  # 개발자 정보 확인
                    self._show_dev_mode_info()
                    
        except Exception as e:
            print(f"❌ 개발자 옵션 메뉴 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _show_all_settings_view(self):
        """모든 설정 보기"""
        try:
            from config import game_config
            from game.color_text import bright_cyan, bright_white
            
            print(f"\n{bright_cyan('📋 모든 설정 보기')}")
            print("=" * 80)
            
            # config.py의 print_all_settings 메서드 사용
            game_config.print_all_settings()
            
            print("=" * 80)
            self.keyboard.wait_for_key("아무 키나 눌러 돌아가기...")
            
        except Exception as e:
            print(f"❌ 설정 보기 오류: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 돌아가기...")
    
    def _show_available_classes(self):
        """사용 가능한 직업 목록 표시"""
        try:
            from game.auto_party_builder import AutoPartyBuilder
            auto_builder = AutoPartyBuilder()
            print("📋 사용 가능한 직업 목록:")
            for i, class_name in enumerate(auto_builder.ALL_CLASSES, 1):
                print(f"  {i:2}. {class_name}")
            print()
        except ImportError:
            print("📋 직업 목록을 불러올 수 없습니다.")
    
    def get_player_input(self):
        """플레이어 입력 받기 - 개선된 입력 시스템"""
        try:
            print(f"\n{bright_cyan('🎮 게임 조작법:')}")
            print(f"  {bright_white('이동:')} W(위), A(왼쪽), S(아래), D(오른쪽)")
            print(f"  {bright_white('메뉴:')} I(인벤토리), P(파티상태), F(필드활동)")  
            print(f"  {bright_white('기타:')} H(도움말), Q(종료), B(저장)")
            print(f"\n{bright_yellow('명령을 입력하세요:')} ", end="")
            return self.keyboard.get_key()
        except Exception as e:
            print(f"⚠️ 입력 처리 오류: {e}")
            return 'q'  # 오류 시 종료
    
    def process_action(self, action):
        """액션 처리 - 이동 및 층 전환 지원"""
        if action.lower() == 'q':
            # 게임 종료 확인창
            if self.confirm_quit():
                self.running = False
            else:
                return  # 취소시 아무것도 하지 않음
            
        elif action.lower() == 'h':
            print(f"\n{bright_cyan('═══════════════════════════════════════')}")
            print(f"{bright_white('          🎮 게임 조작 가이드 🎮')}")
            print(f"{bright_cyan('═══════════════════════════════════════')}")
            print(f"{bright_yellow('📍 이동 조작:')}")
            print(f"   {bright_white('W/A/S/D')} 또는 {bright_white('방향키')} - 캐릭터 이동")
            print()
            print(f"{cyan('📋 메뉴 조작:')}")
            print(f"   {bright_white('I')} - 🎒 인벤토리 (소모품과 장비)")
            print(f"   {bright_white('P')} - 👥 파티 상태 (캐릭터 정보)")  
            print(f"   {bright_white('F')} - 🗺️  필드 활동 (스킬 & 요리 & 상인)")
            print()
            print(f"{magenta('⚙️  시스템 조작:')}")
            print(f"   {bright_white('H')} - ❓ 도움말 (이 화면)")
            print(f"   {bright_white('Q')} - 🚪 게임 종료")
            print(f"   {bright_white('B')} - 💾 게임 저장")
            print(f"{bright_cyan('═══════════════════════════════════════')}")
            print(f"{bright_green('💡 팁: 던전을 탐험하며 몬스터와 전투하고 보물을 찾아보세요!')}")
            print(f"{bright_cyan('═══════════════════════════════════════')}")
            self.keyboard.wait_for_key("🔑 아무 키나 눌러 계속...")
            
        elif action.lower() == 'b':  # B키로 저장
            # 게임 저장
            try:
                if hasattr(self, 'save_manager') and self.save_manager:
                    self.save_current_game()
                else:
                    print("💾 저장 시스템을 사용할 수 없습니다.")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            except Exception as e:
                print(f"❌ 저장 중 오류 발생: {e}")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                
        elif action.lower() == 'i':
            # 인벤토리 메뉴 - 소모품과 장비 선택
            if hasattr(self, 'party_manager') and self.party_manager.members:
                try:
                    from game.cursor_menu_system import create_simple_menu
                    
                    # 메뉴 옵션
                    inventory_options = ["🧪 소모품", "⚔️ 장비", "🤔 장비 해제", "🚪 취소"]
                    inventory_descriptions = [
                        "치유 물약, 버프 아이템 등을 사용합니다",
                        "무기, 방어구, 장신구를 장착합니다",
                        "현재 장착된 장비를 해제합니다",
                        "인벤토리를 닫습니다"
                    ]
                    inventory_descriptions = ["물약, 음식 등 소모품을 확인합니다", "무기, 방어구, 장신구를 확인합니다", "인벤토리를 닫습니다"]
                    
                    inventory_menu = create_simple_menu("🎒 인벤토리", inventory_options, inventory_descriptions)
                    inventory_choice = inventory_menu.run()
                    
                    if inventory_choice == 0:  # 소모품
                        # 소모품 아이템만 수집 (장비 제외) - 실제 아이템 DB 기반
                        consumable_items = []
                        consumable_descriptions = []
                        
                        # 아이템 데이터베이스를 사용한 정확한 분류
                        from game.items import ItemDatabase, ItemType
                        item_db = ItemDatabase()
                        
                        for member in self.party_manager.members:
                            if hasattr(member, 'inventory'):
                                inventory = member.inventory
                                if hasattr(inventory, 'items') and inventory.items:
                                    # inventory.items는 Dict[str, int] 형태 (아이템명: 개수)
                                    for item_name, quantity in inventory.items.items():
                                        # 실제 아이템 데이터베이스에서 아이템 정보 가져오기
                                        item = item_db.get_item(item_name)
                                        
                                        if item:
                                            # 아이템 타입이 CONSUMABLE인 경우만 소모품으로 분류
                                            if item.item_type == ItemType.CONSUMABLE:
                                                consumable_items.append(f"{item_name} x{quantity} ({member.name})")
                                                effect_desc = item.get_effect_description() if hasattr(item, 'get_effect_description') else item.description
                                                consumable_descriptions.append(effect_desc[:50] + "..." if len(effect_desc) > 50 else effect_desc)
                                        else:
                                            # 아이템 DB에 없는 경우 이름 기반 판별 (fallback)
                                            item_name_lower = item_name.lower()
                                            consumable_keywords = [
                                                '물약', '포션', '음료', '빵', '음식', '약', '해독제', 
                                                '스크롤', '두루마리', '폭탄', '화염병', '엘릭서', '비약',
                                                '치료', '회복', '마나', '독', '해독', '버프', '디버프',
                                                '고기', '과일', '야채', '요리', '음식', '간식'
                                            ]
                                            
                                            if any(keyword in item_name_lower for keyword in consumable_keywords):
                                                consumable_items.append(f"{item_name} x{quantity} ({member.name})")
                                                consumable_descriptions.append("미분류 소모품")
                        
                        if consumable_items:
                            menu = create_simple_menu("🧪 파티 소모품", consumable_items, consumable_descriptions)
                            result = menu.run()
                            # 아이템 선택 시 사용 옵션 제공
                            if result is not None and result >= 0:
                                self._handle_consumable_item(result, consumable_items)
                        else:
                            print(f"\n{bright_cyan('=== 🧪 소모품 인벤토리 ===')}")
                            print("소모품이 없습니다.")
                            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                    
                    elif inventory_choice == 1:  # 장비
                        # 장비 아이템만 수집 - 실제 아이템 DB 기반
                        equipment_items = []
                        equipment_descriptions = []
                        
                        # 아이템 데이터베이스를 사용한 정확한 분류
                        from game.items import ItemDatabase, ItemType
                        item_db = ItemDatabase()
                        
                        for member in self.party_manager.members:
                            if hasattr(member, 'inventory'):
                                inventory = member.inventory
                                if hasattr(inventory, 'items') and inventory.items:
                                    # inventory.items는 Dict[str, int] 형태 (아이템명: 개수)
                                    for item_name, quantity in inventory.items.items():
                                        # 실제 아이템 데이터베이스에서 아이템 정보 가져오기
                                        item = item_db.get_item(item_name)
                                        
                                        if item:
                                            # 아이템 타입이 장비인 경우만 장비로 분류
                                            if item.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY]:
                                                # 내구도 정보 추가
                                                durability_info = ""
                                                if hasattr(item, 'get_durability_percentage'):
                                                    durability_pct = item.get_durability_percentage()
                                                    if durability_pct < 100:
                                                        durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
                                                        durability_info = f" {durability_color}{durability_pct:.0f}%"
                                                elif hasattr(item, 'current_durability') and hasattr(item, 'max_durability'):
                                                    durability_pct = (item.current_durability / item.max_durability * 100) if item.max_durability > 0 else 0
                                                    durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
                                                    durability_info = f" {durability_color}{durability_pct:.0f}%"
                                                
                                                equipment_items.append(f"{item_name} x{quantity} ({member.name}){durability_info}")
                                                
                                                # 장비 타입별 설명
                                                type_desc = {
                                                    ItemType.WEAPON: "무기",
                                                    ItemType.ARMOR: "방어구", 
                                                    ItemType.ACCESSORY: "액세서리"
                                                }.get(item.item_type, "장비")
                                                
                                                stats_desc = []
                                                if hasattr(item, 'stats') and item.stats:
                                                    for stat, value in item.stats.items():
                                                        if value > 0:
                                                            stats_desc.append(f"{stat}+{value}")
                                                
                                                # 내구도 정보를 설명에도 추가
                                                durability_desc = ""
                                                if hasattr(item, 'current_durability') and hasattr(item, 'max_durability'):
                                                    durability_desc = f" | 내구도: {item.current_durability}/{item.max_durability}"
                                                elif hasattr(item, 'get_durability_percentage'):
                                                    durability_desc = f" | 내구도: {item.get_durability_percentage():.0f}%"
                                                
                                                desc = f"{type_desc}" + (f" ({', '.join(stats_desc)})" if stats_desc else "") + durability_desc
                                                equipment_descriptions.append(desc[:70] + "..." if len(desc) > 70 else desc)
                                        else:
                                            # 아이템 DB에 없는 경우 이름 기반 판별 (fallback)
                                            item_name_lower = item_name.lower()
                                            equipment_keywords = [
                                                '검', '칼', '도검', '대검', '단검', '활', '궁', '보우', '석궁',
                                                '지팡이', '완드', '스태프', '창', '스피어', '랜스', '도끼', '액스',
                                                '곤봉', '메이스', '해머', '방패', '실드', '갑옷', '아머', '로브',
                                                '투구', '헬름', '장갑', '글러브', '신발', '부츠', 
                                                '반지', '링', '목걸이', '펜던트', '귀걸이', '팔찌'
                                            ]
                                            
                                            if any(keyword in item_name_lower for keyword in equipment_keywords):
                                                equipment_items.append(f"{item_name} x{quantity} ({member.name})")
                                                equipment_descriptions.append("미분류 장비")
                        
                        if equipment_items:
                            menu = create_simple_menu("⚔️ 파티 장비", equipment_items, equipment_descriptions)
                            result = menu.run()
                            if result is not None and result >= 0:
                                self._handle_equipment_item(result, equipment_items)
                        else:
                            print(f"\n{bright_cyan('=== ⚔️ 장비 인벤토리 ===')}")
                            print("장비가 없습니다.")
                            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                    
                    elif inventory_choice == 2:  # 장비 해제
                        self._handle_equipment_unequip()
                    
                    # choice == 3 (취소)는 자동으로 처리
                        
                except ImportError:
                    # 폴백: 기존 방식
                    try:
                        # 인벤토리 시스템이 있는지 확인
                        if hasattr(self.party_manager.members[0], 'inventory'):
                            inventory = self.party_manager.members[0].inventory
                            print(f"\n{bright_cyan('=== 📦 인벤토리 ===')}")
                            if hasattr(inventory, 'items') and inventory.items:
                                for i, item in enumerate(inventory.items, 1):
                                    # 아이템이 객체인지 문자열인지 확인
                                    if hasattr(item, 'name'):
                                        item_name = item.name
                                        item_desc = getattr(item, 'description', '설명 없음')
                                        print(f"{i}. {item_name} - {item_desc}")
                                    elif isinstance(item, str):
                                        print(f"{i}. {item} - 아이템")
                                    else:
                                        print(f"{i}. {str(item)} - 알 수 없는 아이템")
                            else:
                                print("인벤토리가 비어있습니다.")
                        else:
                            print("📦 인벤토리 시스템이 준비되지 않았습니다.")
                    except Exception as e:
                        print(f"📦 인벤토리 표시 중 오류: {e}")
                        print("인벤토리를 표시할 수 없습니다.")
                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            
        elif action.lower() == 'p':
            # 파티 상태 메뉴 - 커서 시스템
            if hasattr(self, 'party_manager') and self.party_manager.members:
                try:
                    from game.cursor_menu_system import create_simple_menu
                    
                    # 파티 멤버 정보 수집
                    member_names = []
                    member_descriptions = []
                    
                    for i, member in enumerate(self.party_manager.members, 1):
                        status = "💚 생존" if member.is_alive else "💀 사망"
                        hp_status = f"❤️ {member.current_hp}/{member.max_hp}"
                        mp_status = f"💙 {member.current_mp}/{member.max_mp}"
                        
                        member_names.append(f"{member.name} ({member.character_class}) - {status}")
                        
                        # 상세 정보를 설명으로
                        details = [hp_status, mp_status, f"⭐ Lv.{member.level} (경험치: {member.experience})"]
                        details.append(f"⚔️ 물리공격력: {member.physical_attack} | 🛡️ 물리방어력: {member.physical_defense}")
                        
                        # 마법 스탯 추가
                        magic_attack = getattr(member, 'magic_attack', getattr(member, 'magical_attack', 0))
                        magic_defense = getattr(member, 'magic_defense', getattr(member, 'magical_defense', 0))
                        details.append(f"🔮 마법공격력: {magic_attack} | 🌟 마법방어력: {magic_defense}")
                        
                        if hasattr(member, 'wounds') and member.wounds > 0:
                            details.append(f"🩸 WOUND: {member.wounds}")
                        
                        member_descriptions.append(" | ".join(details))
                    
                    # 현재 적 정보도 추가 (전투 중인 경우만)
                    # 전투 중인지 확인: brave_combat_system이 활성화되어 있거나 현재 전투 상태인지 체크
                    in_combat = False
                    if hasattr(self, 'brave_combat_system') and self.brave_combat_system:
                        in_combat = getattr(self.brave_combat_system, 'in_combat', False)
                    elif hasattr(self, 'in_combat'):
                        in_combat = self.in_combat
                    
                    if in_combat and hasattr(self, 'world') and hasattr(self.world, 'enemies_positions') and self.world.enemies_positions:
                        member_names.append("🛡️ 현재 적 정보")
                        enemy_info = []
                        for pos, enemy_data in self.world.enemies_positions.items():
                            if isinstance(enemy_data, dict):
                                enemy_name = enemy_data.get('name', '알 수 없는 적')
                                enemy_level = enemy_data.get('level', 1)
                                enemy_hp = enemy_data.get('current_hp', enemy_data.get('hp', 100))
                                enemy_max_hp = enemy_data.get('max_hp', enemy_data.get('hp', 100))
                                enemy_info.append(f"👹 Lv.{enemy_level} {enemy_name} (❤️ {enemy_hp}/{enemy_max_hp})")
                            else:
                                # 간단한 문자열 형태의 적
                                enemy_info.append(f"👹 {enemy_data}")
                        
                        if enemy_info:
                            member_descriptions.append(" | ".join(enemy_info))
                        else:
                            member_descriptions.append("현재 주변에 적이 없습니다")
                    
                    menu = create_simple_menu("👥 파티 상태", member_names, member_descriptions)
                    result = menu.run()
                    
                    # 캐릭터 선택 시 상세 정보 표시 또는 추가 액션 가능
                    if result is not None and result >= 0:
                        selected_member = self.party_manager.members[result]
                        print(f"\n{'='*50}")
                        print(f"✨ {bright_cyan(selected_member.name)} 상세 정보 ✨")
                        print(f"{'='*50}")
                        print(f"🎭 직업: {bright_yellow(selected_member.character_class)}")
                        print(f"⭐ 레벨: {bright_green(selected_member.level)} (경험치: {blue(f'{selected_member.experience:,}')})")
                        
                        # HP 상태 (색상 구분)
                        hp_ratio = selected_member.current_hp / selected_member.max_hp
                        if hp_ratio >= 0.8:
                            hp_color = bright_green
                        elif hp_ratio >= 0.5:
                            hp_color = bright_yellow
                        else:
                            hp_color = bright_red
                        print(f"❤️ HP:         {hp_color(f'{selected_member.current_hp:,}')} / {bright_green(f'{selected_member.max_hp:,}')}")
                        
                        # MP 상태 (색상 구분)
                        mp_ratio = selected_member.current_mp / selected_member.max_mp if selected_member.max_mp > 0 else 1
                        if mp_ratio >= 0.8:
                            mp_color = cyan
                        elif mp_ratio >= 0.5:
                            mp_color = bright_cyan
                        else:
                            mp_color = bright_magenta
                        print(f"💙 MP:         {mp_color(f'{selected_member.current_mp:,}')} / {cyan(f'{selected_member.max_mp:,}')}")
                        
                        print(f"⚔️ 물리공격력:  {bright_red(f'{selected_member.physical_attack:,}')}")
                        print(f"🛡️ 물리방어력:  {bright_cyan(f'{selected_member.physical_defense:,}')}")
                        
                        # 마법공격력과 마법방어력 추가
                        if hasattr(selected_member, 'magic_attack'):
                            print(f"🔮 마법공격력:  {bright_magenta(f'{selected_member.magic_attack:,}')}")
                        elif hasattr(selected_member, 'magical_attack'):
                            print(f"🔮 마법공격력:  {bright_magenta(f'{selected_member.magical_attack:,}')}")
                        else:
                            print(f"🔮 마법공격력:  {bright_magenta('0')}")
                        
                        if hasattr(selected_member, 'magic_defense'):
                            print(f"🌟 마법방어력:  {bright_yellow(f'{selected_member.magic_defense:,}')}")
                        elif hasattr(selected_member, 'magical_defense'):
                            print(f"🌟 마법방어력:  {bright_yellow(f'{selected_member.magical_defense:,}')}")
                        else:
                            print(f"🌟 마법방어력:  {bright_yellow('0')}")
                            
                        print(f"🏃 속도:        {bright_green(f'{selected_member.speed:,}')}")
                        print(f"🎯 명중률:      {cyan(f'{selected_member.accuracy:,}')}")
                        print(f"💨 회피력:      {bright_cyan(f'{selected_member.evasion:,}')}")
                        
                        if hasattr(selected_member, 'wounds') and selected_member.wounds > 0:
                            print(f"🩸 상처: {bright_red(f'{selected_member.wounds:,}')} (제한된 최대 HP: {bright_yellow(f'{selected_member.limited_max_hp:,}')})")
                        
                        # ATB 게이지
                        atb_percentage = int(selected_member.atb_gauge)
                        atb_bar = "█" * (atb_percentage // 10) + "░" * (10 - atb_percentage // 10)
                        print(f"⚡ ATB: {bright_cyan(atb_bar)} {atb_percentage}%")
                        
                        # 속성 정보 표시
                        print(f"\n{bright_cyan('🔮 속성 정보:')}")
                        if hasattr(selected_member, 'get_element_display_info'):
                            element_info = selected_member.get_element_display_info()
                            print(f"   {element_info['display_text']}")
                        elif hasattr(selected_member, 'element_affinity'):
                            print(f"   🔮 기본 속성: {selected_member.element_affinity}")
                            if hasattr(selected_member, 'element_weaknesses') and selected_member.element_weaknesses:
                                weakness_str = ", ".join(selected_member.element_weaknesses)
                                print(f"   💔 약점: {weakness_str}")
                            else:
                                print(f"   💔 약점: 없음")
                            if hasattr(selected_member, 'element_resistances') and selected_member.element_resistances:
                                resistance_str = ", ".join(selected_member.element_resistances)
                                print(f"   🛡️ 저항: {resistance_str}")
                            else:
                                print(f"   🛡️ 저항: 없음")
                        else:
                            print(f"   🔮 기본 속성: 무속성")
                            print(f"   💔 약점: 없음") 
                            print(f"   🛡️ 저항: 없음")
                        
                        # 장착된 장비 정보
                        print(f"\n{bright_cyan('🎒 장착된 장비:')}")
                        equipped_items = selected_member.get_equipped_items()
                        equipment_found = False
                        
                        for slot, item in equipped_items.items():
                            if item:
                                equipment_found = True
                                # 아이템 표시 이름 (내구도 포함)
                                if hasattr(item, 'get_display_name'):
                                    display_name = item.get_display_name()
                                else:
                                    display_name = item.name
                                
                                # 내구도 정보
                                durability_info = ""
                                if hasattr(item, 'get_durability_percentage'):
                                    durability_pct = item.get_durability_percentage()
                                    if durability_pct < 100:
                                        durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
                                        durability_info = f" {durability_color}{durability_pct:.0f}%"
                                elif hasattr(item, 'current_durability') and hasattr(item, 'max_durability'):
                                    durability_pct = (item.current_durability / item.max_durability * 100) if item.max_durability > 0 else 0
                                    durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
                                    durability_info = f" {durability_color}{durability_pct:.0f}%"
                                
                                print(f"   {slot}: {display_name}{durability_info}")
                                
                                # 주요 능력치 보너스 표시
                                if hasattr(item, 'get_effective_stats'):
                                    effective_stats = item.get_effective_stats()
                                    stat_bonuses = []
                                    for stat, value in effective_stats.items():
                                        if isinstance(value, (int, float)) and value > 0:
                                            if stat == "physical_attack":
                                                stat_bonuses.append(f"공격+{value}")
                                            elif stat == "physical_defense":
                                                stat_bonuses.append(f"방어+{value}")
                                            elif stat == "magic_attack":
                                                stat_bonuses.append(f"마공+{value}")
                                            elif stat == "magic_defense":
                                                stat_bonuses.append(f"마방+{value}")
                                            elif stat == "speed":
                                                stat_bonuses.append(f"속도+{value}")
                                            elif stat == "vision_range":
                                                stat_bonuses.append(f"시야+{value}")
                                    
                                    if stat_bonuses:
                                        print(f"      ({', '.join(stat_bonuses)})")
                        
                        if not equipment_found:
                            print("   (장착된 장비 없음)")
                        
                        print(f"{'='*50}")
                        # TODO: 스킬, 특성 등 추가 정보 표시 가능
                        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                        
                except ImportError:
                    # 폴백: 기존 방식
                    print(f"\n{bright_cyan('=== 👥 파티 상태 ===')}")
                    for i, member in enumerate(self.party_manager.members, 1):
                        status = "💚 생존" if member.is_alive else "💀 사망"
                        print(f"{i}. {member.name} ({member.character_class}) - {status}")
                        print(f"   ❤️ HP: {member.current_hp}/{member.max_hp}")
                        print(f"   💙 MP: {member.current_mp}/{member.max_mp}")
                        print(f"   ⭐ 레벨: {member.level} (경험치: {member.experience})")
                        print(f"   ⚔️ 물리공격력: {member.physical_attack} | 🛡️ 물리방어력: {member.physical_defense}")
                        
                        # 마법공격력과 마법방어력 추가
                        magic_attack = getattr(member, 'magic_attack', getattr(member, 'magical_attack', 0))
                        magic_defense = getattr(member, 'magic_defense', getattr(member, 'magical_defense', 0))
                        print(f"   🔮 마법공격력: {magic_attack} | 🌟 마법방어력: {magic_defense}")
                        if hasattr(member, 'wounds') and member.wounds > 0:
                            print(f"   🩸 상처: {member.wounds}")
                        print()
                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            
        elif action.lower() == 'f':
            # 필드 활동 메뉴 - 커서 시스템
            try:
                from game.cursor_menu_system import create_simple_menu
                
                field_options = ["💫 필드 스킬 사용", "🍳 야외 요리 & 채집", "🏪 순회 상인 만나기"]
                field_descriptions = [
                    "파티원의 필드 스킬을 사용합니다",
                    "요리를 하거나 재료를 채집합니다", 
                    "순회 상인과 거래합니다"
                ]
                
                field_menu = create_simple_menu("🌍 필드 활동", field_options, field_descriptions,
                                               self.audio_system, self.keyboard)
                choice = field_menu.run()
                
                if choice == 0:
                    # 필드 스킬 사용 - 원래 시스템 사용
                    try:
                        field_skill_system = get_field_skill_system()
                        field_skill_system.select_caster_and_use_skill(self.party_manager)
                    except Exception as e:
                        print(f"필드 스킬 시스템 오류: {e}")
                        print("기본 필드 스킬 메뉴를 사용합니다.")
                        # 폴백 로직
                        available_skills = self.get_available_field_skills()
                        if available_skills:
                            print("\n💫 사용 가능한 필드 스킬:")
                            for i, (skill_name, character) in enumerate(available_skills, 1):
                                print(f"{i}. {skill_name} ({character.name})")
                            skill_choice = input("스킬 선택 (번호): ")
                            if skill_choice.isdigit() and 1 <= int(skill_choice) <= len(available_skills):
                                skill_name, character = available_skills[int(skill_choice) - 1]
                                self.use_field_skill(skill_name, character)
                        else:
                            print("사용 가능한 필드 스킬이 없습니다.")
                elif choice == 1:
                    # 야외 요리 & 채집 시스템
                    try:
                        from game.field_cooking import FieldCookingInterface
                        cooking_interface = FieldCookingInterface()
                        cooking_interface.show_cooking_menu()
                    except Exception as e:
                        print(f"요리 시스템 오류: {e}")
                        print("기본 요리 메뉴를 사용합니다.")
                        # 폴백: 기존 요리 메뉴
                        print(f"\n{bright_cyan('=== 🍳 요리 메뉴 ===')}")
                        print("1. 🥘 요리하기")
                        print("2. � 레시피 보기")
                        print("3. 🧑‍🍳 요리 기술 확인")
                        print("0. 돌아가기")
                        cook_choice = input("선택: ")
                        if cook_choice == "1":
                            print("\n🥘 요리 재료가 부족합니다.")
                elif choice == 2:
                    # 순회 상인 만나기 - 층별 관리
                    try:
                        current_floor = getattr(self, 'current_floor', 1)
                        if current_floor is None or not isinstance(current_floor, int):
                            current_floor = 1
                            
                        merchant = self.merchant_manager.try_spawn_merchant(current_floor)
                        
                        if merchant:
                            print(f"\n{bright_cyan('=== 🏪 ' + merchant.name + '의 상점 ===')}")
                            print(f"🎒 {merchant.merchant_type} 상인이 {current_floor}층에서 장사를 하고 있습니다!")
                            print(f"💰 보유 골드: {merchant.gold}G | 📦 상품 수: {len(merchant.shop_items)}개")
                            
                            # 상품 갱신 (층이 바뀌었다면)
                            merchant.refresh_inventory_if_needed(current_floor)
                            
                            merchant.show_shop_menu(self.party_manager)
                        else:
                            print(f"\n{bright_cyan('=== 🏪 상인 없음 ===')}")
                            print("이 층에는 상인이 없는 것 같습니다.")
                            spawn_chance = self.merchant_manager.get_spawn_chance(current_floor + 1)
                            print(f"💡 다음 층({current_floor + 1}층)에서 상인을 만날 확률: {spawn_chance:.1%}")
                            
                    except Exception as e:
                        print(f"상인 시스템 오류: {e}")
                        print("상인을 찾을 수 없습니다.")
                elif choice == "4":
                    print("\n�💤 파티가 휴식을 취합니다...")
                    for member in self.party_manager.members:
                        if member.is_alive:
                            heal_amount = member.max_hp // 10
                            member.heal(heal_amount)
                    print("체력이 약간 회복되었습니다.")
            except Exception as e:
                print(f"필드 활동 오류: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            
        # 이동 처리
        elif action.lower() in ['w', 'a', 's', 'd']:
            self.handle_player_movement(action.lower())
            
        # 방향키 처리 (특수 키코드)
        elif action in ['\x1b[A', '\x1b[B', '\x1b[C', '\x1b[D']:  # 방향키
            direction_map = {
                '\x1b[A': 'w',  # 위
                '\x1b[B': 's',  # 아래  
                '\x1b[C': 'd',  # 오른쪽
                '\x1b[D': 'a'   # 왼쪽
            }
            if action in direction_map:
                self.handle_player_movement(direction_map[action])
        else:
            print(f"⚠️ 알 수 없는 명령: '{action}' (도움말: H)")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def handle_player_movement(self, direction):
        """플레이어 이동 처리 - 개선된 오류 처리와 아이템 획득"""
        direction_map = {
            'w': (0, -1),   # 위
            's': (0, 1),    # 아래
            'a': (-1, 0),   # 왼쪽
            'd': (1, 0)     # 오른쪽
        }
        
        if direction not in direction_map:
            print(f"⚠️ 잘못된 방향: {direction}")
            return
            
        dx, dy = direction_map[direction]
        
        try:
            # 이동 가능 여부 확인
            if self.world.can_move(dx, dy):
                # 플레이어 이동 실행
                result = self.world.move_player(dx, dy)
                
                # 결과 처리
                if result == "next_floor":
                    print(f"\n🚪 {bright_green('계단을 발견했습니다!')}")
                    self.advance_to_next_floor()
                elif result == "combat":
                    print(f"\n⚔️ {bright_red('적과 마주쳤습니다!')}")
                    self.keyboard.wait_for_key("아무 키나 눌러 전투 시작...")
                    # 전투 시스템 호출
                    self.start_combat()
                elif result == "moved":
                    # 일반 이동 성공 (조용히 처리)
                    pass
                elif result and hasattr(result, 'name'):  # 아이템 획득
                    print(f"\n💎 {bright_yellow('아이템 발견!')}")
                    # 첫 번째 파티원에게 아이템 추가
                    if self.party_manager.members:
                        first_member = self.party_manager.members[0]
                        if hasattr(first_member, 'inventory'):
                            success = first_member.inventory.add_item(result)
                            if success:
                                print(f"✅ {bright_green(result.name)}을(를) 획득했습니다!")
                                if hasattr(result, 'description'):
                                    print(f"   {result.description}")
                            else:
                                print(f"❌ 인벤토리가 가득 차서 {result.name}을(를) 버렸습니다.")
                        else:
                            print(f"✅ {bright_green(result.name)}을(를) 발견했습니다! (인벤토리 시스템 미구현)")
                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                else:
                    # 예상치 못한 결과
                    if result:
                        print(f"� 알 수 없는 결과: {result}")
                
                # 랜덤 인카운터 체크 (이동 성공 시만)
                # 걸음 수 증가
                if hasattr(self, 'steps_since_last_encounter'):
                    self.steps_since_last_encounter += 1
                else:
                    self.steps_since_last_encounter = 1
                
                # 필드 자동 회복 처리
                self._process_field_regeneration()
                    
                self.check_random_encounter()
                
                # 적들 이동 처리 (플레이어 이동 후)
                if hasattr(self.world, 'move_enemies') and self.world.enemies_positions:
                    enemy_count_before = len(self.world.enemies_positions)
                    self.world.move_enemies()
                    # 적이 실제로 많고 가끔씩만 메시지 표시 (2% 확률로 드물게)
                    if enemy_count_before >= 3 and random.random() < 0.02:
                        print(f"👹 {bright_red('멀리서 적들의 움직임이 감지됩니다...')}")
                
            else:
                # 이동 실패 원인 파악
                new_x = self.world.player_pos[0] + dx
                new_y = self.world.player_pos[1] + dy
                
                if not self.world.is_valid_pos(new_x, new_y):
                    print("🚫 맵 경계를 벗어났습니다.")
                elif not self.world.tiles[new_y][new_x].is_walkable():
                    tile_type = self.world.tiles[new_y][new_x].type.name
                    print(f"🚫 벽({tile_type})으로 막혀 있습니다.")
                else:
                    print("🚫 알 수 없는 이유로 이동할 수 없습니다.")
                    
        except Exception as e:
            print(f"❌ 이동 처리 중 오류 발생: {e}")
            print("디버그 정보:")
            print(f"  - 현재 위치: {self.world.player_pos}")
            print(f"  - 이동 방향: {direction} ({dx}, {dy})")
            if hasattr(self.world, 'tiles'):
                new_x = self.world.player_pos[0] + dx
                new_y = self.world.player_pos[1] + dy
                if self.world.is_valid_pos(new_x, new_y):
                    tile = self.world.tiles[new_y][new_x]
                    print(f"  - 목표 타일: {tile.type.name} (walkable: {tile.is_walkable()})")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def check_random_encounter(self):
        """랜덤 인카운터 체크"""
        try:
            if hasattr(self, 'encounter_manager') and self.encounter_manager:
                # 파티 정보 가져오기
                party = []
                if hasattr(self, 'party_manager') and self.party_manager and hasattr(self.party_manager, 'members'):
                    party = self.party_manager.members
                
                if not party:
                    return  # 파티가 없으면 인카운터 발생 안함
                
                # 현재 층 정보 가져오기
                current_floor = getattr(self.world, 'current_floor', 1) if hasattr(self, 'world') else 1
                
                # 걸음 수 정보 가져오기
                steps_taken = getattr(self, 'steps_since_last_encounter', 0)
                
                # 인카운터 체크
                encounter = self.encounter_manager.check_encounter(party, current_floor, steps_taken)
                if encounter:
                    self.handle_encounter(encounter)
                    # 인카운터 발생 후 걸음 수 초기화
                    self.steps_since_last_encounter = 0
            else:
                # 간단한 랜덤 인카운터 (폴백)
                import random
                if random.random() < 0.05:  # 5% 확률로 낮춤
                    print(f"\n⚔️ {bright_red('적과 마주쳤습니다!')}")
                    self.keyboard.wait_for_key("아무 키나 눌러 전투 시작...")
                    self.start_combat()
        except Exception as e:
            print(f"⚠️ 인카운터 처리 중 오류 발생!")
            print(f"오류 내용: {e}")
            print(f"오류 타입: {type(e).__name__}")
            import traceback
            print("상세한 오류 정보:")
            traceback.print_exc()
            print("\n" + "="*50)
            print("❌ 인카운터 시스템에 문제가 있습니다.")
            print("게임을 계속 진행하지만, 랜덤 조우가 일시적으로 비활성화됩니다.")
            input("🔍 오류 내용을 확인한 후 아무 키나 눌러 계속...")
    
    def _process_field_regeneration(self):
        """필드에서 걸음 수에 따른 자동 회복 처리"""
        try:
            if not hasattr(self, 'steps_since_last_encounter'):
                return
                
            steps = self.steps_since_last_encounter
            if steps <= 0:
                return
                
            # 파티 멤버가 있는지 확인
            if not hasattr(self, 'party_manager') or not self.party_manager.members:
                return
                
            # HP 회복: 2걸음당 1씩
            if steps % 2 == 0:
                for member in self.party_manager.members:
                    if member.is_alive and member.current_hp < member.max_hp:
                        # 상처로 인한 최대 HP 제한 확인
                        max_recoverable_hp = member.max_hp - member.wounds
                        if member.current_hp < max_recoverable_hp:
                            old_hp = member.current_hp
                            member.current_hp = min(max_recoverable_hp, member.current_hp + 1)
                            if member.current_hp > old_hp:
                                # 첫 번째 멤버만 메시지 표시 (스팸 방지)
                                if member == self.party_manager.members[0]:
                                    print(f"💚 자연 회복으로 HP +1 (걸음: {steps})")
            
            # MP와 상처 회복: 3걸음당 1씩
            if steps % 3 == 0:
                hp_regen_occurred = False
                wound_heal_occurred = False
                
                for member in self.party_manager.members:
                    if member.is_alive:
                        # MP 회복
                        if hasattr(member, 'current_mp') and hasattr(member, 'max_mp'):
                            if member.current_mp < member.max_mp:
                                old_mp = member.current_mp
                                member.current_mp = min(member.max_mp, member.current_mp + 1)
                                if member.current_mp > old_mp and not hp_regen_occurred:
                                    print(f"💙 자연 회복으로 MP +1 (걸음: {steps})")
                                    hp_regen_occurred = True
                        
                        # 상처 회복
                        if hasattr(member, 'wounds') and member.wounds > 0:
                            old_wounds = member.wounds
                            member.wounds = max(0, member.wounds - 1)
                            if member.wounds < old_wounds and not wound_heal_occurred:
                                print(f"🩹 자연 회복으로 상처 -1 (걸음: {steps})")
                                wound_heal_occurred = True
                                
        except Exception as e:
            # 회복 시스템 오류는 조용히 처리 (게임 진행에 영향 주지 않음)
            pass
    
    def handle_encounter(self, encounter):
        """인카운터 처리"""
        print("\n" + "="*60)
        print("🎲 랜덤 조우 발생!")
        print("="*60)
        
        # 연타 방지를 위한 강화된 대기 및 입력 버퍼 클리어
        import time
        print("⏳ 잠시 대기 중... (연타 방지)")
        
        # 입력 버퍼 클리어 (여러 번 실행하여 확실히 클리어)
        for _ in range(3):
            self.keyboard.clear_input_buffer()
            time.sleep(0.1)
        
        time.sleep(2.5)  # 대기 시간 증가
        
        # 다시 한 번 입력 버퍼 클리어
        self.keyboard.clear_input_buffer()
        
        if encounter and isinstance(encounter, dict):
            # 인카운터 타입 확인
            encounter_type = encounter.get('type', '알 수 없는 조우')
            message = encounter.get('message', '신비한 일이 일어났습니다.')
            success = encounter.get('success', True)
            
            print(f"\n✨ {bright_cyan(encounter_type)}")
            print(f"📖 {message}")
            
            # 잠시 대기 (사용자가 읽을 시간 제공)
            import time
            time.sleep(1.5)  # 1.5초 대기
            
            # 결과 처리
            if success:
                effects = encounter.get('effects', {})
                if effects:
                    print(f"\n🌟 획득한 효과:")
                    for effect_type, value in effects.items():
                        if effect_type == 'gold':
                            print(f"   💰 골드 +{value}")
                            # 실제 골드 지급
                            if hasattr(self, 'gold'):
                                self.gold += value
                        elif effect_type == 'exp':
                            print(f"   ⭐ 경험치 +{value}")
                            # 파티원들에게 경험치 분배
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                exp_per_member = value // len(self.party_manager.members)
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.gain_experience(exp_per_member)
                        elif effect_type == 'hp_heal':
                            print(f"   ❤️ HP 회복 +{value}")
                            # 파티원들 HP 회복
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.heal(value)
                        elif effect_type == 'mp_heal':
                            print(f"   💙 MP 회복 +{value}")
                            # 파티원들 MP 회복
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.current_mp = min(member.max_mp, member.current_mp + value)
                        else:
                            print(f"   ✨ {effect_type}: {value}")
                    
                    # 효과 적용 후 잠시 대기
                    time.sleep(1.0)
                
                # 단일 효과 처리 (effect)
                effect = encounter.get('effect')
                if effect:
                    if effect == 'elite_encounter':
                        print(f"\n⚔️ {bright_red('강력한 적이 나타났습니다!')}")
                        print("💀 엘리트 몬스터와의 전투가 시작됩니다!")
                        time.sleep(1.5)
                        
                        # 엘리트 몬스터 전투 시작
                        self.start_elite_battle()
                        return  # 전투 후에는 바로 리턴
                    
                    elif effect == 'lucky_wish':
                        print(f"\n🪙 {bright_yellow('동전을 던지시겠습니까?')}")
                        
                        from game.cursor_menu_system import CursorMenu
                        wish_menu = CursorMenu(
                            "🪙 동전 던지기",
                            ["예, 동전을 던집니다", "아니오, 그만둡니다"],
                            ["60% 확률로 보상을 받을 수 있습니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = wish_menu.run()
                        if choice == 0:  # 예
                            import random
                            if random.random() < 0.6:  # 60% 성공률
                                reward_type = random.choice(['gold', 'exp', 'heal'])
                                if reward_type == 'gold':
                                    gold_amount = random.randint(100, 300)
                                    print(f"✨ {bright_green('소원이 이루어졌습니다!')} 💰 골드 +{gold_amount}")
                                    if hasattr(self, 'gold'):
                                        self.gold += gold_amount
                                elif reward_type == 'exp':
                                    exp_amount = random.randint(50, 150)
                                    print(f"✨ {bright_green('소원이 이루어졌습니다!')} ⭐ 경험치 +{exp_amount}")
                                    if hasattr(self, 'party_manager') and self.party_manager.members:
                                        exp_per_member = exp_amount // len(self.party_manager.members)
                                        for member in self.party_manager.members:
                                            if member.is_alive:
                                                member.gain_experience(exp_per_member)
                                else:  # heal
                                    heal_amount = random.randint(30, 80)
                                    print(f"✨ {bright_green('소원이 이루어졌습니다!')} ❤️ 파티 전체 회복 +{heal_amount}")
                                    if hasattr(self, 'party_manager') and self.party_manager.members:
                                        for member in self.party_manager.members:
                                            if member.is_alive:
                                                member.heal(heal_amount)
                            else:
                                print(f"💸 {bright_red('동전이 바닥으로 떨어졌습니다...')} 아무 일도 일어나지 않았습니다.")
                        else:
                            print("🚶 동전을 던지지 않고 지나갑니다.")
                    
                    elif effect == 'training_option':
                        print(f"\n🎯 {bright_yellow('훈련을 받으시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            print(f"💪 {bright_green('훈련을 통해 실력이 향상되었습니다!')}")
                            # 파티원들의 스탯 임시 증가
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.physical_attack += 2
                                        member.physical_defense += 1
                                        print(f"   {member.name}: 공격력 +2, 방어력 +1")
                        else:
                            print("🚶 훈련을 받지 않고 지나갑니다.")
                    
                    elif effect == 'cursed_choice':
                        print(f"\n⚠️ {bright_red('저주받은 제단입니다. 위험할 수 있습니다.')}")
                        print(f"{bright_yellow('제단을 조사하시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            import random
                            if random.random() < 0.4:  # 40% 성공률
                                attack_boost = random.randint(5, 15)
                                print(f"🔥 {bright_green('어둠의 힘을 얻었습니다!')} ⚔️ 공격력 +{attack_boost}")
                                if hasattr(self, 'party_manager') and self.party_manager.members:
                                    for member in self.party_manager.members:
                                        if member.is_alive:
                                            member.physical_attack += attack_boost
                            else:
                                damage = random.randint(10, 30)
                                print(f"💀 {bright_red('저주를 받았습니다!')} 💔 파티 전체 피해 -{damage}")
                                if hasattr(self, 'party_manager') and self.party_manager.members:
                                    for member in self.party_manager.members:
                                        if member.is_alive:
                                            member.take_damage(damage)
                        else:
                            print("🚶 제단을 건드리지 않고 지나갑니다.")
                    
                    elif effect == 'portal_choice':
                        print(f"\n🌀 마법 포털을 조사합니다...")
                        time.sleep(1.0)
                        # 포털 선택 처리는 나중에 구현
                    
                    elif effect == 'time_anomaly':
                        print(f"\n⏰ {bright_yellow('시간 균열에 접근하시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            import random
                            if random.random() < 0.5:  # 50% 성공률
                                effect_type = random.choice(['time_skip', 'time_rewind', 'time_boost'])
                                if effect_type == 'time_skip':
                                    print(f"⚡ {bright_green('시간이 빨라졌습니다!')} 다음 층으로 이동합니다.")
                                    # 다음 층 이동 처리 (구현 필요)
                                elif effect_type == 'time_rewind':
                                    heal_amount = random.randint(50, 100)
                                    print(f"🔄 {bright_green('시간이 되돌아갔습니다!')} 상처가 치유됩니다. +{heal_amount}")
                                    if hasattr(self, 'party_manager') and self.party_manager.members:
                                        for member in self.party_manager.members:
                                            if member.is_alive:
                                                member.heal(heal_amount)
                                else:  # time_boost
                                    print(f"⚡ {bright_green('시간 가속을 받았습니다!')} 행동력이 증가합니다.")
                                    # ATB 가속 효과 (구현 필요)
                            else:
                                damage = random.randint(20, 40)
                                print(f"💥 {bright_red('시간 왜곡에 휘말렸습니다!')} 파티 전체 피해 -{damage}")
                                if hasattr(self, 'party_manager') and self.party_manager.members:
                                    for member in self.party_manager.members:
                                        if member.is_alive:
                                            member.take_damage(damage)
                        else:
                            print("🚶 시간 균열을 피해 지나갑니다.")
                    
                    elif effect == 'shadow_travel':
                        print(f"\n🌑 {bright_yellow('그림자 통로를 이용하시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            if random.random() < 0.7:  # 70% 성공률
                                print(f"🌟 {bright_green('그림자를 통해 안전하게 이동했습니다!')} 적들을 피할 수 있었습니다.")
                                # 인카운터 확률 감소 효과 (구현 필요)
                            else:
                                damage = random.randint(15, 35)
                                print(f"👻 {bright_red('그림자 속에서 길을 잃었습니다!')} 파티 전체 피해 -{damage}")
                                if hasattr(self, 'party_manager') and self.party_manager.members:
                                    for member in self.party_manager.members:
                                        if member.is_alive:
                                            member.take_damage(damage)
                        else:
                            print("🚶 그림자 통로를 지나치고 일반 길로 갑니다.")
                    
                    elif effect == 'divine_blessing':
                        print(f"\n⛪ {bright_yellow('신전에서 기도하시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            heal_amount = random.randint(40, 80)
                            mp_amount = random.randint(20, 40)
                            print(f"✨ {bright_green('신성한 축복을 받았습니다!')}")
                            print(f"   ❤️ HP 회복 +{heal_amount}")
                            print(f"   💙 MP 회복 +{mp_amount}")
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.heal(heal_amount)
                                        member.current_mp = min(member.max_mp, member.current_mp + mp_amount)
                        else:
                            print("🚶 신전을 지나치고 갑니다.")
                    
                    elif effect == 'knowledge_gain':
                        print(f"\n📚 {bright_yellow('고대 서적을 읽으시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            exp_amount = random.randint(100, 200)
                            print(f"📖 {bright_green('고대의 지식을 습득했습니다!')} ⭐ 경험치 +{exp_amount}")
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                exp_per_member = exp_amount // len(self.party_manager.members)
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.gain_experience(exp_per_member)
                        else:
                            print("🚶 서적을 읽지 않고 지나갑니다.")
                    
                    elif effect == 'premium_shop':
                        print(f"\n🚛 {bright_yellow('상인과 거래하시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            print(f"🏪 {bright_green('프리미엄 상점이 열렸습니다!')} 특별한 상품들을 확인하세요.")
                            # 프리미엄 상점 열기 (구현 필요)
                        else:
                            print("🚶 상인과 거래하지 않고 지나갑니다.")
                    
                    elif effect.startswith('element_boost_'):
                        element = effect.replace('element_boost_', '')
                        boost_value = encounter.get('effect_value', 20)
                        print(f"\n🔮 {bright_yellow(f'{element} 원소 노드를 활성화하시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            print(f"⚡ {bright_green(f'{element} 속성 강화를 받았습니다!')} 공격력 +{boost_value}%")
                            # 원소 강화 효과 적용 (구현 필요)
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        # 임시 공격력 증가
                                        member.physical_attack = int(member.physical_attack * (1 + boost_value/100))
                        else:
                            print("🚶 원소 노드를 건드리지 않고 지나갑니다.")
                    
                    elif effect == 'open_shop':
                        print(f"\n🛍️ {bright_green('상점이 열렸습니다!')}")
                        # 상점 시스템 호출 (구현 필요)
                        print("🏪 상인과 거래를 시작합니다...")
                        time.sleep(1.0)
                    
                    elif effect == 'consumables':
                        print(f"\n🎒 {bright_green('소모품을 발견했습니다!')}")
                        import random
                        
                        # 소모품 종류와 개수 결정
                        consumable_types = [
                            ("회복 포션", "💊", "HP를 회복합니다"),
                            ("마나 포션", "🧪", "MP를 회복합니다"),
                            ("해독제", "🟢", "독을 치료합니다"),
                            ("버프 스크롤", "📜", "능력치를 일시적으로 증가시킵니다"),
                            ("투척용 폭탄", "💣", "적에게 데미지를 줍니다")
                        ]
                        
                        num_items = random.randint(1, 3)  # 1-3개의 소모품
                        found_items = random.sample(consumable_types, min(num_items, len(consumable_types)))
                        
                        for item_name, icon, description in found_items:
                            quantity = random.randint(1, 2)  # 각 종류마다 1-2개
                            print(f"{icon} {item_name} x{quantity} - {description}")
                        
                        # 실제 인벤토리에 추가 (간소화된 버전)
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            first_member = self.party_manager.members[0]
                            if hasattr(first_member, 'inventory'):
                                print(f"📦 소모품이 {first_member.name}의 인벤토리에 추가되었습니다!")
                        time.sleep(1.5)
                    
                    elif effect == 'weapon_choice':
                        print(f"\n⚔️ {bright_yellow('무기를 선택하시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            import random
                            weapon_types = ['검', '활', '지팡이', '단검', '도끼']
                            weapon_name = random.choice(weapon_types)
                            attack_bonus = random.randint(5, 15)
                            print(f"⚔️ {bright_green(f'좋은 {weapon_name}을(를) 획득했습니다!')} 공격력 +{attack_bonus}")
                            # 무기 지급 처리 (구현 필요)
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                # 랜덤한 파티원에게 무기 효과 적용
                                member = random.choice(self.party_manager.members)
                                if member.is_alive:
                                    member.physical_attack += attack_bonus
                                    print(f"   {member.name}의 공격력이 증가했습니다!")
                        else:
                            print("🚶 무기를 가져가지 않고 지나갑니다.")
                            
                    elif effect == 'spell_learning':
                        print(f"\n🔯 {bright_yellow('마법진에서 마법을 배우시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            import random
                            spell_types = ['화염구', '치유술', '번개', '얼음 화살', '독 안개']
                            spell_name = random.choice(spell_types)
                            magic_bonus = random.randint(8, 20)
                            print(f"✨ {bright_green(f'{spell_name} 마법을 배웠습니다!')} 마법 공격력 +{magic_bonus}")
                            # 마법 학습 처리
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                # 마법사 우선으로 마법 효과 적용
                                mages = [m for m in self.party_manager.members if '마법사' in m.character_class and m.is_alive]
                                if mages:
                                    mage = random.choice(mages)
                                    mage.magic_attack += magic_bonus
                                    print(f"   {mage.name}의 마법 공격력이 증가했습니다!")
                                else:
                                    # 마법사가 없으면 랜덤 파티원
                                    member = random.choice([m for m in self.party_manager.members if m.is_alive])
                                    member.magic_attack += magic_bonus
                                    print(f"   {member.name}의 마법 공격력이 증가했습니다!")
                        else:
                            print("🚶 마법을 배우지 않고 지나갑니다.")
                            
                    elif effect == 'hermit_advice':
                        print(f"\n🧙 {bright_yellow('은둔자의 조언을 들으시겠습니까?')}")
                        choice = input("y/n: ").lower().strip()
                        if choice in ['y', 'yes', '예', 'ㅇ']:
                            import random
                            advice_types = ['공격 조언', '방어 조언', '마법 조언', '생존 조언']
                            advice = random.choice(advice_types)
                            if advice == '공격 조언':
                                bonus = random.randint(3, 8)
                                print(f"⚔️ {bright_green('공격 기술을 배웠습니다!')} 파티 전체 공격력 +{bonus}")
                                if hasattr(self, 'party_manager') and self.party_manager.members:
                                    for member in self.party_manager.members:
                                        if member.is_alive:
                                            member.physical_attack += bonus
                            elif advice == '방어 조언':
                                bonus = random.randint(2, 6)
                                print(f"🛡️ {bright_green('방어 기술을 배웠습니다!')} 파티 전체 방어력 +{bonus}")
                                if hasattr(self, 'party_manager') and self.party_manager.members:
                                    for member in self.party_manager.members:
                                        if member.is_alive:
                                            member.physical_defense += bonus
                            elif advice == '마법 조언':
                                bonus = random.randint(4, 10)
                                print(f"✨ {bright_green('마법 기술을 배웠습니다!')} 파티 전체 마법력 +{bonus}")
                                if hasattr(self, 'party_manager') and self.party_manager.members:
                                    for member in self.party_manager.members:
                                        if member.is_alive:
                                            member.magic_attack += bonus
                            else:  # 생존 조언
                                bonus = random.randint(10, 25)
                                print(f"❤️ {bright_green('생존 기술을 배웠습니다!')} 파티 전체 최대 HP +{bonus}")
                                if hasattr(self, 'party_manager') and self.party_manager.members:
                                    for member in self.party_manager.members:
                                        if member.is_alive:
                                            member.max_hp += bonus
                                            member.heal(bonus)  # 추가 체력 즉시 회복
                        else:
                            print("🚶 조언을 듣지 않고 지나갑니다.")
                            
                    elif effect == 'blessing':
                        import random
                        blessing_types = ['체력 축복', '마나 축복', '공격 축복', '방어 축복']
                        blessing = random.choice(blessing_types)
                        if blessing == '체력 축복':
                            heal_amount = random.randint(30, 60)
                            print(f"❤️ {bright_green('체력 축복을 받았습니다!')} 파티 전체 회복 +{heal_amount}")
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.heal(heal_amount)
                        elif blessing == '마나 축복':
                            mp_amount = random.randint(20, 40)
                            print(f"💙 {bright_green('마나 축복을 받았습니다!')} 파티 전체 MP 회복 +{mp_amount}")
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.current_mp = min(member.max_mp, member.current_mp + mp_amount)
                        elif blessing == '공격 축복':
                            attack_bonus = random.randint(5, 12)
                            print(f"⚔️ {bright_green('공격 축복을 받았습니다!')} 파티 전체 공격력 +{attack_bonus}")
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.physical_attack += attack_bonus
                        else:  # 방어 축복
                            defense_bonus = random.randint(3, 8)
                            print(f"🛡️ {bright_green('방어 축복을 받았습니다!')} 파티 전체 방어력 +{defense_bonus}")
                            if hasattr(self, 'party_manager') and self.party_manager.members:
                                for member in self.party_manager.members:
                                    if member.is_alive:
                                        member.physical_defense += defense_bonus
                                        
                    elif effect == 'attack_boost':
                        boost_amount = random.randint(8, 15)
                        print(f"💪 {bright_green('힘의 석상 효과!')} 파티 전체 공격력 +{boost_amount}")
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            for member in self.party_manager.members:
                                if member.is_alive:
                                    member.physical_attack += boost_amount
                                    
                    elif effect == 'magic_boost':
                        boost_amount = random.randint(10, 20)
                        print(f"🔮 {bright_green('고대 룬 효과!')} 파티 전체 마법력 +{boost_amount}")
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            for member in self.party_manager.members:
                                if member.is_alive:
                                    member.magic_attack += boost_amount
                                    
                    elif effect == 'mp_restore':
                        restore_amount = random.randint(25, 50)
                        print(f"💎 {bright_green('마나 수정 효과!')} 파티 전체 MP 회복 +{restore_amount}")
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            for member in self.party_manager.members:
                                if member.is_alive:
                                    member.current_mp = min(member.max_mp, member.current_mp + restore_amount)
                                    
                    elif effect == 'map_info':
                        print(f"🗺️ {bright_green('지도 정보를 획득했습니다!')} 이 층의 구조를 파악했습니다.")
                        # 맵 정보 효과 (미니맵 표시 등)
                        
                    elif effect == 'ambush_battle':
                        print(f"\n💀 {bright_red('매복 공격!')}")
                        print("⚠️ 불리한 상황에서 전투가 시작됩니다!")
                        time.sleep(1.5)
                        # 매복 전투 시작
                        self.start_ambush_battle()
                        return  # 전투 후에는 바로 리턴
                        
            else:
                print(f"\n⚠️ {encounter.get('failure_message', '좋지 않은 일이 일어났습니다.')}")
                time.sleep(1.0)
                
            # 특정 인카운터에서만 필드 스킬 사용 옵션 표시
            encounter_type = encounter.get('type', '')
            skill_suggested_encounters = ['shadow_passage', 'time_anomaly', 'ancient_library']
            
            available_skills = self.get_available_field_skills()
            if available_skills and encounter_type in skill_suggested_encounters:
                print(f"\n💫 {bright_green('사용 가능한 필드 스킬이 있습니다!')}")
                print(f"\n────────────────────────────────────────────────────────────")
                
                # 잠시 대기 후 사용자 확인
                time.sleep(0.5)
                print(f"\n🤔 필드 스킬을 사용하시겠습니까?")
                use_skill = input(f"{bright_yellow('필드 스킬 사용? (y/n):')} ").lower().strip()
                
                if use_skill in ['y', 'yes', '예', 'ㅇ']:
                    try:
                        from game.cursor_menu_system import create_simple_menu
                        
                        print(f"\n🎮 💫 필드 스킬 사용")
                        print("="*16)
                        time.sleep(0.3)  # 메뉴 표시 전 잠시 대기
                        
                        skill_options = []
                        skill_descriptions = []
                        
                        for skill_name, character in available_skills:
                            skill_options.append(f"💫 {skill_name} ({character.name})")
                            skill_descriptions.append(f"{character.name}이(가) {skill_name}을(를) 사용합니다")
                        
                        skill_options.append("🚪 넘어가기")
                        skill_descriptions.append("필드 스킬을 사용하지 않고 계속합니다")
                        
                        skill_menu = create_simple_menu("💫 필드 스킬 사용", skill_options, skill_descriptions, clear_screen=False)
                        skill_result = skill_menu.run()
                        
                        if skill_result is not None and 0 <= skill_result < len(available_skills):
                            skill_name, character = available_skills[skill_result]
                            print(f"\n💡 {character.name}이(가) {skill_name}을(를) 사용합니다")
                            print("──────────────────────────────────────────────────")
                            time.sleep(0.5)  # 스킬 사용 전 잠시 대기
                            self.use_field_skill(skill_name, character)
                            time.sleep(1.0)  # 스킬 사용 후 결과 확인 시간
                        # 넘어가기나 취소는 자동으로 처리
                            
                    except ImportError:
                        # 폴백: 기존 텍스트 입력 방식
                        print(f"\n💫 {bright_green('사용 가능한 필드 스킬:')}")
                        for i, (skill_name, character) in enumerate(available_skills, 1):
                            print(f"   {i}. {skill_name} ({character.name})")
                        print(f"   0. 넘어가기")
                        
                        try:
                            choice = input(f"\n{bright_yellow('필드 스킬을 사용하시겠습니까? (번호 입력):')} ")
                            if choice.isdigit():
                                choice_num = int(choice)
                                if 1 <= choice_num <= len(available_skills):
                                    skill_name, character = available_skills[choice_num - 1]
                                    print(f"\n💡 {character.name}이(가) {skill_name}을(를) 사용합니다")
                                    print("──────────────────────────────────────────────────")
                                    time.sleep(0.5)
                                    self.use_field_skill(skill_name, character)
                                    time.sleep(1.0)
                        except (ValueError, IndexError):
                            pass
                else:
                    print(f"\n⏭️ 필드 스킬을 사용하지 않고 계속합니다.")
                    time.sleep(0.5)  # 짧은 대기
        else:
            print(f"\n🎲 {encounter}")
            time.sleep(1.0)  # 일반 인카운터도 대기
        
        print(f"\n" + "="*60)
        print(f"✅ {bright_green('인카운터 처리 완료!')}")
        print("="*60)
        
        # 충분한 대기 시간을 제공
        time.sleep(1.0)  # 완료 메시지 표시 후 대기
        print("📖 위의 내용을 확인하세요...")
        time.sleep(0.5)  # 추가 확인 시간
        
        # 인카운터 처리 완료 후 입력 버퍼 클리어
        self.keyboard.clear_input_buffer()
        input("🎮 아무 키나 눌러 게임을 계속...")
    
    def advance_to_next_floor(self):
        """다음 층으로 진행"""
        old_floor = self.world.current_level
        self.world.current_level += 1
        new_floor = self.world.current_level
        self.current_floor = new_floor  # 현재 층 정보 업데이트
        
        print(f"\n🏢 {old_floor}층에서 {new_floor}층으로 이동합니다...")
        
        # 층 진행 플래그 설정
        self._floor_advanced = True
        
        # auto_save 기능 확인 및 실행
        if self.permanent_progression.has_ability("auto_save"):
            print("💾 자동 저장 중...")
            self.auto_save_game()
        
        # 새 층 생성
        self.world.generate_level()
        
        # 층별 BGM 변경
        self.safe_set_floor_bgm(new_floor)
        
        print(f"🌟 {new_floor}층에 도착했습니다!")
        
        # 파티 체력 일부 회복 (층 이동 보너스)
        for member in self.party_manager.members:
            if member.is_alive:
                heal_amount = int(member.max_hp * 0.1)  # 최대 체력의 10% 회복
                member.heal(heal_amount)
                
        print("💚 층 이동으로 파티원들이 체력을 회복했습니다.")
        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def save_current_game(self):
        """현재 게임 상태 저장"""
        try:
            from game.save_system import GameStateSerializer
            
            # 게임 상태 생성
            game_state = GameStateSerializer.create_game_state(self)
            
            # 저장 실행
            if self.save_manager.save_game(game_state):
                print("✅ 게임이 성공적으로 저장되었습니다!")
            else:
                print("❌ 게임 저장에 실패했습니다.")
                
        except ImportError as e:
            print(f"❌ 저장 시스템 로드 실패: {e}")
        except AttributeError as e:
            print(f"❌ 게임 상태 오류: {e}")
        except Exception as e:
            print(f"❌ 저장 중 오류 발생: {e}")
    
    def auto_save_game(self):
        """자동 저장 실행"""
        try:
            from game.save_system import GameStateSerializer
            import datetime
            
            # 자동 저장 파일명 생성
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_save_name = f"autosave_floor_{self.world.current_level}_{timestamp}"
            
            # 게임 상태 생성
            game_state = GameStateSerializer.create_game_state(self)
            
            # 자동 저장 실행
            if self.save_manager.save_game(game_state, auto_save_name):
                print(f"💾 자동 저장 완료: {auto_save_name}")
            else:
                print("⚠️ 자동 저장에 실패했습니다.")
                
        except Exception as e:
            print(f"⚠️ 자동 저장 중 오류: {e}")
    
    def confirm_quit(self):
        """게임 종료 확인"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.color_text import bright_cyan, bright_yellow, yellow, red, bright_white
            
            print(f"\n{bright_yellow('⚠️  게임을 종료하시겠습니까?')}")
            print(f"{yellow('현재 진행상황이 저장되지 않을 수 있습니다.')}")
            
            options = [
                f"🚫 {red('게임 종료')}",
                f"💾 {bright_white('저장 후 종료')}",
                f"🔄 {bright_cyan('게임 계속하기')}"
            ]
            descriptions = [
                "저장하지 않고 게임을 종료합니다",
                "게임을 저장한 후 종료합니다",
                "게임을 계속 진행합니다"
            ]
            
            menu = CursorMenu("게임 종료 확인", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result == 0:  # 바로 종료
                print(f"\n{red('게임을 종료합니다.')}")
                # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                self._play_main_menu_bgm()
                return True
            elif result == 1:  # 저장 후 종료
                print(f"\n{bright_white('게임을 저장하는 중...')}")
                self.save_current_game()
                print(f"{red('게임을 종료합니다.')}")
                # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                self._play_main_menu_bgm()
                return True
            else:  # 계속하기 또는 취소
                print(f"\n{bright_cyan('게임을 계속합니다.')}")
                return False
                
        except ImportError:
            # 폴백: 간단한 텍스트 확인
            print(f"\n{bright_yellow('⚠️  정말로 게임을 종료하시겠습니까? (y/n)')}")
            while True:
                try:
                    choice = self.keyboard.get_key().lower()
                    if choice == 'y':
                        print(f"{red('게임을 종료합니다.')}")
                        return True
                    elif choice == 'n':
                        print(f"{bright_cyan('게임을 계속합니다.')}")
                        return False
                    else:
                        print("y 또는 n을 입력해주세요.")
                except:
                    break
            return False
        except Exception as e:
            print(f"⚠️ 종료 확인 중 오류: {e}")
            return True  # 오류 시 종료
    
    def _play_main_menu_bgm(self):
        """메인 메뉴 BGM 재생"""
        try:
            if hasattr(self, 'sound_manager') and self.sound_manager:
                print("🎵 메인 테마 음악을 재생합니다...")
                self.sound_manager.play_bgm("main_theme", loop=True)
            elif hasattr(self, 'audio_system') and self.audio_system:
                print("🎵 메인 테마 음악을 재생합니다...")
                self.audio_system.play_bgm("main_theme", loop=True)
        except Exception as e:
            # BGM 재생 실패는 조용히 처리 (게임 진행에 영향 없음)
            pass

    def confirm_quit_main_menu(self):
        """메인 메뉴에서 게임 종료 확인"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.color_text import bright_cyan, bright_yellow, yellow, red, bright_white
            
            print(f"\n{bright_yellow('⚠️  정말로 게임을 종료하시겠습니까?')}")
            
            options = [
                f"🚫 {red('게임 종료')}",
                f"🔄 {bright_cyan('메인 메뉴로 돌아가기')}"
            ]
            descriptions = [
                "게임을 완전히 종료합니다",
                "메인 메뉴로 돌아갑니다"
            ]
            
            menu = CursorMenu("게임 종료 확인", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result == 0:  # 종료
                return True
            else:  # 돌아가기 또는 취소
                return False
                
        except ImportError:
            # 폴백: 간단한 텍스트 확인
            print(f"\n{bright_yellow('⚠️  정말로 게임을 종료하시겠습니까? (y/n)')}")
            while True:
                try:
                    choice = self.keyboard.get_key().lower()
                    if choice == 'y':
                        return True
                    elif choice == 'n':
                        return False
                    else:
                        print("y 또는 n을 입력해주세요.")
                except:
                    break
            return False
        except Exception as e:
            print(f"⚠️ 종료 확인 중 오류: {e}")
            return True  # 오류 시 종료
    
    def quit_game(self):
        """게임 종료"""
        self.running = False
        print(f"\n{bright_yellow('게임을 종료합니다.')}")
        
    def _handle_playing_state(self):
        """플레이 상태 처리"""
        pass
        
    def _handle_paused_state(self):
        """일시정지 상태 처리"""
        pass
        
    def _handle_game_over_state(self):
        """게임 오버 상태 처리"""
        pass
        
    def main_loop(self):
        """메인 게임 루프 - 고급 시스템 통합"""
        # 🎮 게임 매니저가 없으면 직접 메뉴 처리
        if not self.game_manager:
            # 간단한 메뉴 루프
            while self.running:
                try:
                    self._handle_menu_state()
                    if not self.running:
                        break
                except KeyboardInterrupt:
                    self.quit_game()
                    break
            return
            
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
    
    def show_meta_progression_menu(self):
        """메타 진행 통합 메뉴"""
        try:
            from game.cursor_menu_system import create_simple_menu
            
            while True:
                # 현재 진행 상황 정보
                star_fragments = 0
                unlocked_chars = 4  # 기본 4개
                
                if hasattr(self, 'meta_progression') and self.meta_progression:
                    star_fragments = self.meta_progression.data.get('star_fragments', 0)
                    unlocked_chars = len(self.meta_progression.data.get('unlocked_classes', []))
                
                if hasattr(self, 'permanent_progression') and self.permanent_progression:
                    # 영구 강화 시스템도 별조각 사용
                    star_fragments += self.permanent_progression.star_fragments
                
                # 메타 진행 메뉴 옵션
                options = [
                    f"캐릭터 해금 ({unlocked_chars}/27)",
                    "특성 해금",
                    "영구 강화",
                    "업적 확인",
                    "상세 통계",
                    "뒤로 가기"
                ]
                
                descriptions = [
                    f"별조각 {star_fragments}개로 새로운 캐릭터를 해금합니다",
                    f"별조각 {star_fragments}개로 캐릭터 특성을 해금합니다",
                    f"별조각 {star_fragments}개로 영구 능력치를 강화합니다",
                    "달성한 업적과 진행도를 확인합니다",
                    "게임 플레이 통계를 상세히 확인합니다",
                    "메인 메뉴로 돌아갑니다"
                ]
                
                menu = create_simple_menu("메타 진행 시스템", 
                                        options, descriptions, self.audio_system, self.keyboard)
                
                result = menu.run()
                
                if result == 0:  # 캐릭터 해금
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_character_unlock_shop()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 1:  # 특성 해금
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_trait_unlock_shop()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 2:  # 영구 강화
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'permanent_progression') and self.permanent_progression:
                        self.permanent_progression.show_menu()
                    else:
                        print("영구 강화 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 3:  # 업적 확인
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_achievements_menu()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 4:  # 상세 통계
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_detailed_statistics()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 5 or result == -1 or result is None:  # 뒤로 가기
                    self.safe_play_sfx("menu_cancel")
                    break
                    
        except ImportError:
            # 폴백: 텍스트 메뉴
            while True:
                print("\n" + "="*50)
                print("메타 진행 시스템")
                print("="*50)
                print("1. 캐릭터 해금")
                print("2. 특성 해금") 
                print("3. 영구 강화")
                print("4. 업적 확인")
                print("5. 상세 통계")
                print("0. 뒤로 가기")
                
                choice = input("선택: ").strip()
                
                if choice == '1':
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_character_unlock_shop()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif choice == '2':
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_trait_unlock_shop()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif choice == '3':
                    if hasattr(self, 'permanent_progression') and self.permanent_progression:
                        self.permanent_progression.show_menu()
                    else:
                        print("영구 강화 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif choice == '4':
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_achievements_menu()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif choice == '5':
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_detailed_statistics()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif choice == '0':
                    break
                else:
                    print("잘못된 선택입니다.")
                    input("아무 키나 눌러 계속...")

    def _handle_menu_state(self):
        """메뉴 상태 처리 - 커서 네비게이션"""
        try:
            from game.cursor_menu_system import create_simple_menu
            
            # 메인 메뉴 옵션 설정
            options = [
                "🚀 게임 시작",
                "📁 게임 불러오기",
                "⭐ 메타 진행",
                "📖 레시피 컬렉션",
                "📚 튜토리얼",
                "⚙️ 설정",
                "❌ 종료"
            ]
            
            descriptions = [
                "새로운 모험을 시작합니다",
                "이전에 저장된 게임을 불러옵니다",
                "캐릭터 해금, 특성 해금, 영구 강화 등 메타 시스템을 관리합니다",
                "발견한 레시피들을 확인합니다",
                "게임 기본 조작법과 시스템을 학습합니다",
                "게임 옵션, 난이도, 설정을 변경합니다",
                "게임을 종료합니다"
            ]
            
            # 커서 메뉴 생성 및 실행
            menu = create_simple_menu("Dawn Of Stellar - 별빛의 여명", 
                                    options, descriptions, self.audio_system, self.keyboard)
            
            result = menu.run()
            
            # 선택 결과 처리
            if result == 0:  # 게임 시작
                choice = '1'
            elif result == 1:  # 게임 불러오기
                choice = '2'
            elif result == 2:  # 메타 진행
                choice = 'M'  # 메타 진행 메뉴
            elif result == 3:  # 레시피 컬렉션
                choice = '4'
            elif result == 4:  # 튜토리얼
                choice = '5'
            elif result == 5:  # 설정 (난이도 포함)
                choice = '6'
            elif result == 6:  # 종료
                if self.confirm_quit_main_menu():
                    choice = '0'
                else:
                    return  # 확인 취소 시 메뉴 계속
            elif result == -1 or result is None:  # Q로 종료 또는 취소
                if self.confirm_quit_main_menu():
                    choice = '0'
                else:
                    return  # 확인 취소 시 메뉴 계속
            else:
                return
                
        except ImportError:
            # 폴백: 기존 메뉴 시스템
            print("\n" + "="*60)
            print(bright_cyan("🎮 Dawn Of Stellar - 메인 메뉴", True))
            print("="*60)
            print(f"{cyan('1️⃣')}  게임 시작")
            print(f"{blue('2️⃣')}  게임 불러오기") 
            print(f"{yellow('M️⃣')}  메타 진행")
            print(f"{green('4️⃣')}  레시피 컬렉션")
            print(f"{magenta('5️⃣')}  튜토리얼")
            print(f"{bright_white('6️⃣')}  설정")
            print(f"{red('0️⃣')}  종료")
            
            # 영구 진행상황 요약 표시
            if self.permanent_progression.total_runs > 0:
                print(f"\n{cyan('📊 진행상황:')} 플레이 {self.permanent_progression.total_runs}회 | "
                      f"최고 {self.permanent_progression.best_floor}층 | "
                      f"별조각 {bright_yellow(str(self.permanent_progression.star_fragments))}")
            
            # 메타 진행상황도 표시
            if hasattr(self, 'meta_progression') and self.meta_progression:
                star_fragments = self.meta_progression.data.get('star_fragments', 0)
                print(f"{cyan('🌟 별조각:')} {bright_yellow(str(star_fragments))}개")
            
            choice = get_single_key_input(f"\n{bright_white('👉 선택하세요 (1-6, M, 0): ')}")
        
        if choice == 'q' or choice == 'Q':
            # Q키로 종료 확인
            if self.confirm_quit_main_menu():
                choice = '0'
            else:
                return  # 확인 취소 시 메뉴 계속
        elif choice == '1':
            # 게임 시작 (캐릭터 선택)
            self.safe_play_sfx("menu_select")
            game = DawnOfStellarGame()  # 새 인스턴스 생성
            game.permanent_progression = self.permanent_progression  # 영구 진행상황 유지
            
            # 캐릭터 선택이 성공한 경우에만 게임 시작
            if game.show_character_selection():  # 캐릭터 선택 메뉴로 이동
                game.start_adventure()  # main_loop 대신 start_adventure 사용
            else:
                print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                self._play_main_menu_bgm()
                # 게임 객체 정리
                del game
            
        elif choice == '2':
            # 게임 불러오기
            self.safe_play_sfx("menu_select")
            print(f"\n🔄 게임 불러오기를 시작합니다...")
            print(f"📊 현재 영구 진행상황: {self.permanent_progression}")
            
            load_game = DawnOfStellarGame()  # 새 인스턴스 생성
            load_game.permanent_progression = self.permanent_progression  # 영구 진행상황 유지
            
            print(f"✅ 새 게임 인스턴스 생성 완료")
            print(f"🔄 불러오기 함수 호출 중...")
            
            try:
                load_result = load_game.load_game()  # 불러오기 성공 여부 확인
                print(f"📊 불러오기 결과: {load_result}")
                
                if load_result:  # 불러오기 성공
                    print(f"✅ 불러오기 성공! 파티 멤버 수 확인 중...")
                    party_count = len(load_game.party_manager.members) if hasattr(load_game, 'party_manager') else 0
                    print(f"📊 파티 멤버 수: {party_count}")
                    
                    if party_count > 0:  # 파티가 제대로 복원되었는지 확인
                        print(f"✅ 파티 복원 확인 완료. 게임 시작 중...")
                        input("게임을 시작하려면 Enter를 누르세요...")
                        load_game.start_adventure(skip_passive_selection=True)  # 불러오기 시 패시브 선택 건너뛰기
                    else:
                        print("❌ 파티 정보가 복원되지 않았습니다.")
                        print("💡 가능한 원인:")
                        print("   - 세이브 파일의 파티 데이터 손상")
                        print("   - 캐릭터 복원 과정에서 오류")
                        print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                        input("확인하려면 Enter를 누르세요...")
                        self._play_main_menu_bgm()
                        del load_game
                else:
                    print("❌ 게임 불러오기 실패")
                    print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                    input("확인하려면 Enter를 누르세요...")
                    self._play_main_menu_bgm()
                    del load_game
            except Exception as load_error:
                print(f"❌ 불러오기 중 예외 발생: {load_error}")
                import traceback
                traceback.print_exc()
                print(f"\n불러오기 오류 상세 정보를 확인하세요...")
                input("메인 메뉴로 돌아가려면 Enter를 누르세요...")
                self._play_main_menu_bgm()
                del load_game
        
        elif choice == '3':
            # 메타 진행 (통합 메뉴)
            self.safe_play_sfx("menu_select")
            self.show_meta_progression_menu()
            
        elif choice == '4':
            # 레시피 컬렉션
            self.safe_play_sfx("menu_select")
            from game.cooking_system import show_recipe_collection
            show_recipe_collection()
            
        elif choice == '5':
            # 튜토리얼
            self.safe_play_sfx("menu_select")
            show_tutorial()
            
        elif choice == '6':
            # 설정 (난이도 포함)
            self.safe_play_sfx("menu_select")
            self.show_settings_menu()
            
        elif choice == 'M' or choice == 'm':
            # 메타 진행 통합 메뉴
            self.safe_play_sfx("menu_select")
            if hasattr(self, 'meta_progression') and self.meta_progression:
                self.show_meta_progression_menu()
            else:
                print("메타 진행 시스템이 초기화되지 않았습니다.")
                input("아무 키나 눌러 계속...")
        
        elif choice == '0':
            # 게임 종료 확인
            if self.confirm_quit_main_menu():
                self.safe_play_sfx("menu_cancel")
                print(f"\n🌟 {bright_green('게임을 종료합니다. 플레이해주셔서 감사합니다!')}")
                # 영구 진행상황 저장
                self.permanent_progression.save_to_file()
                self.running = False
                return
            # 확인 취소 시 아무것도 하지 않고 메뉴 계속
            
        else:
            error_msg = f"잘못된 선택입니다: '{choice}'"
            self.safe_play_sfx("error")
            print(f"❌ {red(error_msg)}")

    def show_meta_progression_menu(self):
        """메타 진행 통합 메뉴"""
        try:
            from game.cursor_menu_system import create_simple_menu
            
            while True:
                # 현재 자원 상태 - 별조각만 사용
                star_fragments = self.meta_progression.data.get('star_fragments', 0)
                # 영구 강화 시스템의 별조각도 합산
                if hasattr(self, 'permanent_progression') and self.permanent_progression:
                    star_fragments += self.permanent_progression.star_fragments
                
                unlocked_chars = len(self.meta_progression.data.get('unlocked_classes', []))
                unlocked_traits = len(self.meta_progression.data.get('unlocked_traits', []))
                
                status_info = f"별조각: {star_fragments}개\n해금된 캐릭터: {unlocked_chars}/27 | 해금된 특성: {unlocked_traits}개"
                
                options = [
                    "🏪 캐릭터 해금",
                    "🎭 특성 해금",
                    "⚡ 영구 강화",
                    "🏆 업적 시스템",
                    "📊 상세 통계",
                    "🎯 직업 숙련도",
                    "✨ 진행 상황 요약",
                    "🚪 메인 메뉴로"
                ]
                
                descriptions = [
                    f"별조각으로 새로운 캐릭터를 해금합니다 (현재: {star_fragments}개)",
                    f"별조각으로 새로운 특성을 해금합니다 (현재: {unlocked_traits}개 해금)",
                    f"별조각으로 영구 능력치를 강화합니다 (현재: {star_fragments}개)",
                    "달성한 업적들을 확인하고 보상을 받습니다",
                    "게임 플레이 통계를 자세히 확인합니다",
                    "각 직업별 숙련도와 보너스를 확인합니다",
                    "전체 메타 진행 상황을 한눈에 봅니다",
                    "메인 메뉴로 돌아갑니다"
                ]
                
                menu = create_simple_menu(f"⭐ 메타 진행 시스템 ⭐\n{status_info}", 
                                        options, descriptions, self.audio_system, self.keyboard)
                result = menu.run()
                
                if result == 0:  # 캐릭터 해금
                    self.meta_progression.show_character_unlock_shop()
                elif result == 1:  # 특성 해금
                    self.meta_progression.show_trait_unlock_shop()
                elif result == 2:  # 영구 강화
                    self.permanent_progression.show_menu()
                elif result == 3:  # 업적 시스템
                    self.meta_progression.show_achievements_menu()
                elif result == 4:  # 상세 통계
                    self.show_detailed_meta_stats()
                elif result == 5:  # 직업 숙련도
                    self.show_class_mastery_menu()
                elif result == 6:  # 진행 상황 요약
                    self.show_meta_progress_summary()
                else:  # 메인 메뉴로
                    # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                    self._play_main_menu_bgm()
                    break
                    
        except ImportError:
            # 폴백: 텍스트 메뉴
            while True:
                print(f"\n⭐ 메타 진행 시스템 ⭐")
                print("="*50)
                print(f"별조각: {self.meta_progression.data.get('star_fragments', 0)}개")
                print("="*50)
                print("1. 캐릭터 해금")
                print("2. 특성 해금") 
                print("3. 영구 강화")
                print("4. 업적 시스템")
                print("5. 상세 통계")
                print("6. 직업 숙련도")
                print("7. ✨ 진행 상황 요약")
                print("0. 메인 메뉴로")
                
                choice = input("선택: ").strip()
                
                if choice == '1':
                    self.meta_progression.show_character_unlock_shop()
                elif choice == '2':
                    self.meta_progression.show_trait_unlock_shop()
                elif choice == '3':
                    self.permanent_progression.show_menu()
                elif choice == '4':
                    self.meta_progression.show_achievements_menu()
                elif choice == '5':
                    self.show_detailed_meta_stats()
                elif choice == '6':
                    self.show_class_mastery_menu()
                elif choice == '7':
                    self.show_meta_progress_summary()
                elif choice == '0':
                    # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                    self._play_main_menu_bgm()
                    break
                else:
                    print("잘못된 선택입니다.")
                    
    def show_meta_progress_summary(self):
        """메타 진행 상황 요약"""
        try:
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green
            
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_cyan('📈 메타 진행 상황 요약')}")
            print(f"{bright_cyan('='*60)}")
            
            # 기본 통계
            total_runs = self.meta_progression.data.get('total_runs', 0)
            best_score = self.meta_progression.data.get('best_score', 0)
            star_fragments = self.meta_progression.data.get('star_fragments', 0)
            perm_star_fragments = self.permanent_progression.star_fragments
            
            # 영구 진행 통계
            perm_runs = self.permanent_progression.total_runs if hasattr(self.permanent_progression, 'total_runs') else 0
            best_floor = self.permanent_progression.best_floor if hasattr(self.permanent_progression, 'best_floor') else 0
            total_kills = self.permanent_progression.total_kills if hasattr(self.permanent_progression, 'total_kills') else 0
            
            print(f"\n{bright_yellow('🎮 게임 플레이 통계')}")
            print("-" * 40)
            print(f"🕹️  총 플레이 횟수: {bright_white(str(perm_runs))}회")
            print(f"�️  최고 도달 층수: {bright_white(str(best_floor))}층")
            print(f"⚔️  총 적 처치 수: {bright_white(str(total_kills))}마리")
            print(f"📊 최고 점수: {bright_white(f'{best_score:,}')}점")
            
            # 생존율 계산
            if perm_runs > 0 and hasattr(self.permanent_progression, 'total_deaths'):
                deaths = self.permanent_progression.total_deaths
                survival_rate = ((perm_runs - deaths) / perm_runs) * 100
                survival_emoji = "💚" if survival_rate >= 70 else "💛" if survival_rate >= 50 else "❤️"
                print(f"{survival_emoji} 생존율: {bright_white(f'{survival_rate:.1f}%')}")
            
            print(f"\n{bright_yellow('💰 자원 현황')}")
            print("-" * 30)
            total_fragments = star_fragments + perm_star_fragments
            print(f"🌟 총 별조각: {bright_white(str(total_fragments))}개")
            print(f"   📦 메타 진행용: {cyan(str(star_fragments))}개")
            print(f"   ⚡ 영구 강화용: {green(str(perm_star_fragments))}개")
            
            # 소모한 별조각
            spent_fragments = self.meta_progression.data.get('star_fragments_spent', 0)
            if spent_fragments > 0:
                print(f"💸 소모한 별조각: {yellow(str(spent_fragments))}개")
                print(f"📈 총 획득량: {bright_green(str(total_fragments + spent_fragments))}개")
            
            # 해금 상황
            print(f"\n{bright_yellow('🔓 해금 진행률')}")
            print("-" * 30)
            total_chars = 27
            unlocked_chars = len(self.meta_progression.data.get('unlocked_classes', []))
            unlocked_traits = len(self.meta_progression.data.get('unlocked_traits', []))
            
            char_progress = (unlocked_chars / total_chars) * 100
            char_bar = "█" * int(char_progress // 10) + "░" * (10 - int(char_progress // 10))
            char_emoji = "🎉" if char_progress == 100 else "🚀" if char_progress >= 80 else "📈"
            
            print(f"{char_emoji} 캐릭터: {bright_white(str(unlocked_chars))}/{total_chars} ({bright_white(f'{char_progress:.1f}%')})")
            print(f"   [{green(char_bar)}]")
            
            trait_emoji = "🎭" if unlocked_traits >= 100 else "🎪" if unlocked_traits >= 50 else "🎯"
            print(f"{trait_emoji} 특성: {bright_white(str(unlocked_traits))}개 해금")
            
            # 영구 강화 상황
            print(f"\n{bright_yellow('⚡ 영구 강화 현황')}")
            print("-" * 30)
            if hasattr(self.permanent_progression, 'upgrades'):
                total_upgrades = sum(upgrade.current_level for upgrade in self.permanent_progression.upgrades.values())
                max_upgrades = sum(upgrade.max_level for upgrade in self.permanent_progression.upgrades.values())
                upgrade_progress = (total_upgrades / max_upgrades * 100) if max_upgrades > 0 else 0
                upgrade_bar = "█" * int(upgrade_progress // 10) + "░" * (10 - int(upgrade_progress // 10))
                upgrade_emoji = "⭐" if upgrade_progress >= 80 else "💎" if upgrade_progress >= 50 else "🔋"
                
                print(f"{upgrade_emoji} 총 업그레이드 레벨: {bright_white(str(total_upgrades))}/{max_upgrades}")
                print(f"   [{green(upgrade_bar)}] {bright_white(f'{upgrade_progress:.1f}%')}")
                
                # 개별 업그레이드 상위 3개
                top_upgrades = sorted(self.permanent_progression.upgrades.items(), 
                                    key=lambda x: x[1].current_level, reverse=True)[:3]
                if any(upgrade[1].current_level > 0 for upgrade in top_upgrades):
                    print(f"   🏆 주요 강화:")
                    for name, upgrade in top_upgrades:
                        if upgrade.current_level > 0:
                            progress = f"{upgrade.current_level}/{upgrade.max_level}"
                            print(f"     • {upgrade.name}: {cyan(progress)}")
            
            # 업적 달성률
            print(f"\n{bright_yellow('🏆 업적 시스템')}")
            print("-" * 30)
            if hasattr(self.permanent_progression, 'achievements'):
                achievements = self.permanent_progression.achievements
                completed = sum(1 for completed in achievements.values() if completed)
                total_achievements = len(achievements)
                if total_achievements > 0:
                    achievement_rate = (completed / total_achievements) * 100
                    achievement_bar = "█" * int(achievement_rate // 10) + "░" * (10 - int(achievement_rate // 10))
                    achievement_emoji = "🎖️" if achievement_rate == 100 else "🏅" if achievement_rate >= 70 else "🎯"
                    
                    print(f"{achievement_emoji} 달성률: {bright_white(str(completed))}/{total_achievements} ({bright_white(f'{achievement_rate:.1f}%')})")
                    print(f"   [{green(achievement_bar)}]")
                    
                    # 최근 달성한 업적
                    achievement_names = {
                        "first_floor": "🌟 첫 걸음",
                        "deep_dive": "🏔️ 심층 탐험가", 
                        "abyss_explorer": "🌊 심연 정복자",
                        "monster_slayer": "⚔️ 몬스터 헌터",
                        "unstoppable": "🛡️ 불굴의 용사",
                        "synergy_master": "🎭 시너지 마스터",
                        "star_collector": "💫 별빛 수집가"
                    }
                    
                    recent_achievements = [achievement_names.get(key, key) 
                                        for key, completed in achievements.items() if completed]
                    if recent_achievements:
                        print(f"   🎉 달성한 업적: {', '.join(recent_achievements[:3])}")
                        if len(recent_achievements) > 3:
                            print(f"   ... 외 {len(recent_achievements) - 3}개")
            else:
                print(f"� 업적 시스템 준비 중...")
            
            # 직업 숙련도 요약
            print(f"\n{bright_yellow('🎭 직업 숙련도')}")
            print("-" * 30)
            class_stats = self.meta_progression.data.get('class_play_stats', {})
            if class_stats:
                total_classes_played = len(class_stats)
                master_classes = sum(1 for stats in class_stats.values() 
                                   if stats.get('plays', 0) * 10 + stats.get('best_floor', 0) * 5 >= 200)
                expert_classes = sum(1 for stats in class_stats.values() 
                                   if stats.get('plays', 0) * 10 + stats.get('best_floor', 0) * 5 >= 100)
                
                print(f"🎮 플레이한 직업: {bright_white(str(total_classes_played))}개")
                if master_classes > 0:
                    print(f"👑 마스터 등급: {bright_yellow(str(master_classes))}개")
                if expert_classes > 0:
                    print(f"💎 전문가 등급: {bright_green(str(expert_classes))}개")
                
                # 가장 숙련된 직업
                if class_stats:
                    best_class = max(class_stats.items(), 
                                   key=lambda x: x[1].get('plays', 0) * 10 + x[1].get('best_floor', 0) * 5)
                    best_score = best_class[1].get('plays', 0) * 10 + best_class[1].get('best_floor', 0) * 5
                    if best_score > 0:
                        print(f"⭐ 최고 숙련도: {bright_white(best_class[0])} ({best_score}점)")
            else:
                print(f"🎯 첫 게임을 플레이하여 숙련도를 쌓아보세요!")
            
            # 다음 목표 제안
            print(f"\n{bright_yellow('🎯 다음 목표')}")
            print("-" * 30)
            
            goals = []
            if char_progress < 50:
                goals.append("🏪 더 많은 캐릭터 해금")
            if best_floor < 10:
                goals.append("🏔️ 10층 도달 도전")
            elif best_floor < 20:
                goals.append("🌋 20층 정복 도전")
            if unlocked_traits < 50:
                goals.append("🎭 특성 컬렉션 확장")
            if hasattr(self.permanent_progression, 'achievements'):
                uncompleted = sum(1 for completed in self.permanent_progression.achievements.values() if not completed)
                if uncompleted > 0:
                    goals.append(f"🏆 업적 {uncompleted}개 달성")
            
            if not goals:
                goals = ["🎉 모든 목표 달성! 새로운 도전을 찾아보세요!"]
            
            for i, goal in enumerate(goals[:3], 1):
                print(f"   {i}. {goal}")
            
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_green('🎮 계속해서 별빛의 여명을 즐겨주세요! ✨')}")
            
            input(f"\n{bright_white('아무 키나 눌러 계속...')}")
            
        except Exception as e:
            print(f"진행 상황 요약 중 오류 발생: {e}")
            # 폴백: 간단한 요약
            print(f"\n📈 메타 진행 상황 요약")
            print("="*60)
            
            star_fragments = self.meta_progression.data.get('star_fragments', 0)
            perm_star_fragments = self.permanent_progression.star_fragments
            unlocked_chars = len(self.meta_progression.data.get('unlocked_classes', []))
            
            print(f"🌟 별조각: {star_fragments + perm_star_fragments}개")
            print(f"🏪 해금된 캐릭터: {unlocked_chars}/27개")
            
            input("아무 키나 눌러 계속...")

    def show_detailed_meta_stats(self):
        """상세 메타 통계"""
        try:
            from game.cursor_menu_system import create_simple_menu
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green
            
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_cyan('📊 상세 메타 통계')}")
            print(f"{bright_cyan('='*60)}")
            
            # 메타 진행 데이터
            meta_data = self.meta_progression.data if hasattr(self, 'meta_progression') and self.meta_progression else {}
            perm_data = self.permanent_progression if hasattr(self, 'permanent_progression') and self.permanent_progression else None
            
            # 기본 통계
            print(f"\n{bright_yellow('🎮 플레이 통계')}")
            print("-" * 40)
            total_runs = perm_data.total_runs if perm_data else 0
            best_floor = perm_data.best_floor if perm_data else 0
            total_kills = perm_data.total_kills if perm_data else 0
            total_deaths = perm_data.total_deaths if perm_data else 0
            
            print(f"{cyan('총 플레이 횟수:')} {total_runs}회")
            print(f"{cyan('최고 도달 층:')} {best_floor}층")
            print(f"{cyan('총 처치 수:')} {total_kills}마리")
            print(f"{cyan('총 사망 횟수:')} {total_deaths}회")
            
            if total_runs > 0:
                avg_floor = best_floor / total_runs if total_runs > 0 else 0
                survival_rate = ((total_runs - total_deaths) / total_runs * 100) if total_runs > 0 else 0
                avg_kills = total_kills / total_runs if total_runs > 0 else 0
                
                print(f"{cyan('평균 도달 층:')} {avg_floor:.1f}층")
                print(f"{cyan('생존율:')} {survival_rate:.1f}%")
                print(f"{cyan('평균 처치 수:')} {avg_kills:.1f}마리/게임")
            
            # 자원 통계
            print(f"\n{bright_yellow('💰 자원 통계')}")
            print("-" * 40)
            star_fragments = meta_data.get('star_fragments', 0)
            perm_fragments = perm_data.star_fragments if perm_data else 0
            total_fragments = star_fragments + perm_fragments
            spent_fragments = meta_data.get('star_fragments_spent', 0)
            
            print(f"{cyan('현재 별조각:')} {total_fragments}개")
            print(f"{cyan('  - 메타 진행:')} {star_fragments}개")
            print(f"{cyan('  - 영구 강화:')} {perm_fragments}개")
            print(f"{cyan('소모한 별조각:')} {spent_fragments}개")
            print(f"{cyan('총 획득 별조각:')} {total_fragments + spent_fragments}개")
            
            # 해금 통계
            print(f"\n{bright_yellow('🔓 해금 통계')}")
            print("-" * 40)
            unlocked_chars = len(meta_data.get('unlocked_classes', []))
            unlocked_traits = len(meta_data.get('unlocked_traits', []))
            
            print(f"{cyan('해금된 캐릭터:')} {unlocked_chars}/27 ({unlocked_chars/27*100:.1f}%)")
            print(f"{cyan('해금된 특성:')} {unlocked_traits}/135 ({unlocked_traits/135*100:.1f}%)")
            
            # 업적 통계
            if perm_data and hasattr(perm_data, 'achievements'):
                print(f"\n{bright_yellow('🏆 업적 통계')}")
                print("-" * 40)
                achieved = sum(1 for completed in perm_data.achievements.values() if completed)
                total_achievements = len(perm_data.achievements)
                achievement_rate = (achieved / total_achievements * 100) if total_achievements > 0 else 0
                
                print(f"{cyan('달성한 업적:')} {achieved}/{total_achievements} ({achievement_rate:.1f}%)")
                
                # 달성한 업적 목록
                if achieved > 0:
                    print(f"\n{green('✅ 달성한 업적:')}")
                    achievement_names = {
                        "first_floor": "첫 층 도달",
                        "deep_dive": "10층 도달",
                        "abyss_explorer": "20층 도달",
                        "monster_slayer": "100마리 처치",
                        "unstoppable": "10층 무사생환",
                        "synergy_master": "특성 마스터",
                        "star_collector": "별조각 수집가"
                    }
                    
                    for key, completed in perm_data.achievements.items():
                        if completed:
                            name = achievement_names.get(key, key)
                            print(f"  🏆 {name}")
            
            # 영구 업그레이드 통계
            if perm_data and hasattr(perm_data, 'upgrades'):
                print(f"\n{bright_yellow('⚡ 영구 업그레이드')}")
                print("-" * 40)
                
                total_levels = 0
                max_possible_levels = 0
                
                for upgrade in perm_data.upgrades.values():
                    total_levels += upgrade.current_level
                    max_possible_levels += upgrade.max_level
                
                upgrade_progress = (total_levels / max_possible_levels * 100) if max_possible_levels > 0 else 0
                print(f"{cyan('업그레이드 진행률:')} {total_levels}/{max_possible_levels} ({upgrade_progress:.1f}%)")
                
                # 개별 업그레이드 상태
                for upgrade in perm_data.upgrades.values():
                    if upgrade.current_level > 0:
                        progress = f"{upgrade.current_level}/{upgrade.max_level}"
                        print(f"  {green('▪')} {upgrade.name}: {progress}")
            
            print(f"\n{bright_cyan('='*60)}")
            
            # 메뉴 옵션
            options = ["📈 성과 분석", "🎯 목표 설정", "🔄 데이터 새로고침", "🚪 뒤로 가기"]
            descriptions = [
                "플레이 성과를 자세히 분석합니다",
                "다음 목표를 설정하고 계획을 세웁니다", 
                "최신 데이터로 통계를 업데이트합니다",
                "메타 진행 메뉴로 돌아갑니다"
            ]
            
            menu = create_simple_menu("상세 통계 옵션", options, descriptions, 
                                    self.audio_system, self.keyboard)
            result = menu.run()
            
            if result == 0:  # 성과 분석
                self.show_performance_analysis()
            elif result == 1:  # 목표 설정
                self.show_goal_setting()
            elif result == 2:  # 데이터 새로고침
                print(f"\n{bright_green('데이터를 새로고침했습니다!')}")
                input("아무 키나 눌러 계속...")
                self.show_detailed_meta_stats()  # 재귀 호출로 새로고침
            # result == 3 또는 취소시 자동으로 메뉴로 돌아감
                
        except ImportError:
            # 폴백: 간단한 텍스트 통계
            print("\n📊 간단 통계")
            print("="*30)
            if hasattr(self, 'permanent_progression') and self.permanent_progression:
                perm = self.permanent_progression
                print(f"총 플레이: {perm.total_runs}회")
                print(f"최고 층: {perm.best_floor}층")
                print(f"총 처치: {perm.total_kills}마리")
                print(f"별조각: {perm.star_fragments}개")
            else:
                print("통계 데이터가 없습니다.")
            input("아무 키나 눌러 계속...")
        
    def show_performance_analysis(self):
        """성과 분석"""
        try:
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green
            
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_cyan('📈 플레이 성과 분석')}")
            print(f"{bright_cyan('='*60)}")
            
            perm_data = self.permanent_progression if hasattr(self, 'permanent_progression') and self.permanent_progression else None
            
            if not perm_data or perm_data.total_runs == 0:
                print(f"{yellow('아직 플레이 기록이 없습니다.')}")
                input("아무 키나 눌러 계속...")
                return
            
            # 성과 등급 계산
            print(f"\n{bright_yellow('🎯 종합 성과 등급')}")
            print("-" * 40)
            
            score = 0
            factors = []
            
            # 층수 기반 점수 (0-30점)
            floor_score = min(perm_data.best_floor * 1.5, 30)
            score += floor_score
            factors.append(f"최고 층수: {perm_data.best_floor}층 (+{floor_score:.1f}점)")
            
            # 생존율 기반 점수 (0-25점)
            if perm_data.total_runs > 0:
                survival_rate = ((perm_data.total_runs - perm_data.total_deaths) / perm_data.total_runs)
                survival_score = survival_rate * 25
                score += survival_score
                factors.append(f"생존율: {survival_rate*100:.1f}% (+{survival_score:.1f}점)")
            
            # 효율성 점수 (0-20점)
            if perm_data.total_runs > 0:
                avg_kills = perm_data.total_kills / perm_data.total_runs
                efficiency_score = min(avg_kills * 2, 20)
                score += efficiency_score
                factors.append(f"평균 처치 효율: {avg_kills:.1f}마리/게임 (+{efficiency_score:.1f}점)")
            
            # 업적 점수 (0-15점)
            if hasattr(perm_data, 'achievements'):
                achieved = sum(1 for completed in perm_data.achievements.values() if completed)
                total_achievements = len(perm_data.achievements)
                achievement_score = (achieved / total_achievements) * 15 if total_achievements > 0 else 0
                score += achievement_score
                factors.append(f"업적 달성률: {achieved}/{total_achievements} (+{achievement_score:.1f}점)")
            
            # 경험 점수 (0-10점)
            experience_score = min(perm_data.total_runs * 0.5, 10)
            score += experience_score
            factors.append(f"플레이 경험: {perm_data.total_runs}회 (+{experience_score:.1f}점)")
            
            # 등급 결정
            if score >= 85:
                grade = f"{bright_yellow('S')} - 로그라이크 마스터"
                color = bright_yellow
            elif score >= 70:
                grade = f"{bright_green('A')} - 숙련된 모험가"
                color = bright_green
            elif score >= 55:
                grade = f"{green('B')} - 경험있는 탐험가"
                color = green
            elif score >= 40:
                grade = f"{cyan('C')} - 성장하는 모험가"
                color = cyan
            elif score >= 25:
                grade = f"{yellow('D')} - 초보 탐험가"
                color = yellow
            else:
                grade = f"{red('F')} - 견습 모험가"
                color = red
            
            print(f"{color('종합 점수:')} {score:.1f}/100점")
            print(f"{color('성과 등급:')} {grade}")
            
            print(f"\n{bright_yellow('📊 점수 구성')}")
            print("-" * 40)
            for factor in factors:
                print(f"  • {factor}")
            
            # 개선 제안
            print(f"\n{bright_yellow('💡 개선 제안')}")
            print("-" * 40)
            
            suggestions = []
            if perm_data.best_floor < 10:
                suggestions.append("더 깊은 층까지 탐험해보세요 (목표: 10층)")
            if perm_data.total_runs > 0 and (perm_data.total_deaths / perm_data.total_runs) > 0.7:
                suggestions.append("생존 전략을 개선해보세요 (방어력 강화, 회복 아이템 활용)")
            if hasattr(perm_data, 'achievements'):
                unachieved = sum(1 for completed in perm_data.achievements.values() if not completed)
                if unachieved > 0:
                    suggestions.append(f"아직 달성하지 못한 업적 {unachieved}개에 도전해보세요")
            if hasattr(perm_data, 'upgrades'):
                low_upgrades = [u for u in perm_data.upgrades.values() if u.current_level < u.max_level // 2]
                if low_upgrades:
                    suggestions.append("영구 업그레이드를 더 투자해보세요")
            
            if not suggestions:
                suggestions.append("훌륭한 성과입니다! 더 높은 목표에 도전해보세요!")
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
                
            input(f"\n아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"성과 분석 중 오류 발생: {e}")
            input("아무 키나 눌러 계속...")
    
    def show_goal_setting(self):
        """목표 설정"""
        try:
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green
            
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_cyan('🎯 목표 설정 및 계획')}")
            print(f"{bright_cyan('='*60)}")
            
            perm_data = self.permanent_progression if hasattr(self, 'permanent_progression') and self.permanent_progression else None
            meta_data = self.meta_progression.data if hasattr(self, 'meta_progression') and self.meta_progression else {}
            
            # 현재 상태 요약
            print(f"\n{bright_yellow('📊 현재 상태')}")
            print("-" * 30)
            if perm_data:
                print(f"최고 층수: {perm_data.best_floor}층")
                print(f"총 플레이: {perm_data.total_runs}회")
                print(f"별조각: {perm_data.star_fragments}개")
            
            unlocked_chars = len(meta_data.get('unlocked_classes', []))
            print(f"해금 캐릭터: {unlocked_chars}/27개")
            
            # 추천 목표 제시
            print(f"\n{bright_yellow('🏆 추천 목표')}")
            print("-" * 30)
            
            goals = []
            
            # 층수 목표
            if not perm_data or perm_data.best_floor < 5:
                goals.append("🏃 단기 목표: 5층 도달하기")
            elif perm_data.best_floor < 10:
                goals.append("🏃 단기 목표: 10층 도달하기")
            elif perm_data.best_floor < 20:
                goals.append("🏃 중기 목표: 20층 도달하기")
            else:
                goals.append("🏃 고급 목표: 30층 이상 도달하기")
            
            # 해금 목표
            if unlocked_chars < 10:
                needed_fragments = (10 - unlocked_chars) * 100  # 대략적 계산
                goals.append(f"🔓 해금 목표: 10개 캐릭터 해금 (약 {needed_fragments}조각 필요)")
            elif unlocked_chars < 20:
                goals.append("🔓 해금 목표: 20개 캐릭터 해금")
            else:
                goals.append("🔓 완성 목표: 모든 캐릭터 해금")
            
            # 생존 목표
            if perm_data and perm_data.total_runs > 0:
                survival_rate = ((perm_data.total_runs - perm_data.total_deaths) / perm_data.total_runs) * 100
                if survival_rate < 50:
                    goals.append("💪 생존 목표: 생존율 50% 달성")
                elif survival_rate < 75:
                    goals.append("💪 생존 목표: 생존율 75% 달성")
                else:
                    goals.append("💪 마스터 목표: 연속 5회 생존")
            
            # 업적 목표
            if perm_data and hasattr(perm_data, 'achievements'):
                achieved = sum(1 for completed in perm_data.achievements.values() if completed)
                total_achievements = len(perm_data.achievements)
                if achieved < total_achievements // 2:
                    goals.append("🏆 업적 목표: 업적 50% 달성")
                elif achieved < total_achievements:
                    goals.append("🏆 업적 목표: 모든 업적 달성")
            
            for i, goal in enumerate(goals, 1):
                print(f"  {i}. {goal}")
            
            # 달성 전략
            print(f"\n{bright_yellow('📋 달성 전략')}")
            print("-" * 30)
            
            strategies = [
                "• 영구 업그레이드에 별조각 투자하여 기본 능력치 향상",
                "• 다양한 캐릭터와 특성 조합 실험",
                "• 방어력과 회복 아이템에 집중하여 생존율 향상",
                "• 층별 적 패턴 학습 및 전략 수립",
                "• 정기적인 플레이로 경험과 별조각 축적"
            ]
            
            for strategy in strategies:
                print(f"  {strategy}")
            
            # 예상 시간
            print(f"\n{bright_yellow('⏱️ 예상 달성 시간')}")
            print("-" * 30)
            print("• 단기 목표: 1-2주 (꾸준한 플레이)")
            print("• 중기 목표: 1-2개월 (주 3-4회 플레이)")
            print("• 장기 목표: 3-6개월 (완전 마스터)")
            
            print(f"\n{bright_green('화이팅! 목표 달성을 응원합니다! 🎉')}")
            input("아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"목표 설정 중 오류 발생: {e}")
            input("아무 키나 눌러 계속...")
    
    def show_class_mastery_menu(self):
        """직업 숙련도 메뉴"""
        try:
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green
            from game.cursor_menu_system import create_simple_menu
            
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_cyan('🎯 직업 숙련도 시스템')}")
            print(f"{bright_cyan('='*60)}")
            
            # 메타 데이터에서 직업별 플레이 기록 확인
            meta_data = self.meta_progression.data if hasattr(self, 'meta_progression') and self.meta_progression else {}
            class_stats = meta_data.get('class_play_stats', {})
            unlocked_classes = meta_data.get('unlocked_classes', [])
            
            print(f"\n{bright_yellow('📊 직업별 플레이 통계')}")
            print("-" * 50)
            
            if not class_stats:
                print(f"{yellow('아직 직업별 플레이 기록이 없습니다.')}")
                print(f"{cyan('게임을 플레이하면 직업별 숙련도가 기록됩니다!')}")
            else:
                # 플레이 횟수별 정렬
                sorted_classes = sorted(class_stats.items(), key=lambda x: x[1].get('plays', 0), reverse=True)
                
                print(f"{'직업명':<15} {'플레이':<8} {'최고층':<8} {'숙련도':<10} {'보너스'}")
                print("-" * 50)
                
                for class_name, stats in sorted_classes:
                    plays = stats.get('plays', 0)
                    best_floor = stats.get('best_floor', 0)
                    
                    # 숙련도 계산 (플레이 횟수 + 최고 층수 기반)
                    mastery_score = plays * 10 + best_floor * 5
                    
                    # 숙련도 등급
                    if mastery_score >= 200:
                        mastery_level = f"{bright_yellow('마스터')}"
                        bonus = "+15% 모든 능력치"
                    elif mastery_score >= 100:
                        mastery_level = f"{bright_green('전문가')}"
                        bonus = "+10% 모든 능력치"
                    elif mastery_score >= 50:
                        mastery_level = f"{green('숙련자')}"
                        bonus = "+5% 모든 능력치"
                    elif mastery_score >= 20:
                        mastery_level = f"{cyan('경험자')}"
                        bonus = "+3% HP/MP"
                    else:
                        mastery_level = f"{yellow('초보자')}"
                        bonus = "보너스 없음"
                    
                    print(f"{class_name:<15} {plays:<8} {best_floor:<8} {mastery_level:<15} {bonus}")
            
            # 해금된 직업 목록
            print(f"\n{bright_yellow('🔓 해금된 직업')}")
            print("-" * 30)
            
            # 기본 직업들
            base_classes = ["전사", "아크메이지", "궁수", "도적"]
            
            print(f"{green('기본 직업:')} {len(base_classes)}개")
            for class_name in base_classes:
                plays = class_stats.get(class_name, {}).get('plays', 0)
                print(f"  ✅ {class_name} ({plays}회 플레이)")
            
            if unlocked_classes:
                print(f"\n{bright_green('해금된 추가 직업:')} {len(unlocked_classes)}개")
                for class_name in unlocked_classes:
                    if class_name not in base_classes:
                        plays = class_stats.get(class_name, {}).get('plays', 0)
                        print(f"  ✅ {class_name} ({plays}회 플레이)")
            
            # 숙련도 보너스 설명
            print(f"\n{bright_yellow('🎁 숙련도 보너스')}")
            print("-" * 30)
            print(f"{bright_yellow('마스터')} (200+점): +15% 모든 능력치")
            print(f"{bright_green('전문가')} (100+점): +10% 모든 능력치") 
            print(f"{green('숙련자')} (50+점): +5% 모든 능력치")
            print(f"{cyan('경험자')} (20+점): +3% HP/MP")
            print(f"숙련도 점수 = (플레이 횟수 × 10) + (최고 층수 × 5)")
            
            # 추천 직업
            print(f"\n{bright_yellow('💡 추천 플레이 직업')}")
            print("-" * 30)
            
            # 적게 플레이한 해금된 직업 추천
            available_classes = base_classes + unlocked_classes
            underplayed = []
            
            for class_name in available_classes:
                plays = class_stats.get(class_name, {}).get('plays', 0)
                if plays < 3:  # 3회 미만 플레이
                    underplayed.append((class_name, plays))
            
            if underplayed:
                underplayed.sort(key=lambda x: x[1])  # 플레이 횟수 적은 순
                print("숙련도 향상을 위해 이 직업들을 시도해보세요:")
                for class_name, plays in underplayed[:5]:
                    print(f"  🎯 {class_name} (현재 {plays}회)")
            else:
                print("모든 해금된 직업을 충분히 플레이했습니다!")
                print("새로운 직업 해금에 도전해보세요!")
            
            # 메뉴 옵션
            options = ["📈 상세 분석", "🎯 숙련도 목표", "🚪 뒤로 가기"]
            descriptions = [
                "각 직업별 상세한 플레이 분석을 확인합니다",
                "직업 숙련도 향상 목표를 설정합니다",
                "메타 진행 메뉴로 돌아갑니다"
            ]
            
            menu = create_simple_menu("직업 숙련도 옵션", options, descriptions,
                                    self.audio_system, self.keyboard)
            result = menu.run()
            
            if result == 0:  # 상세 분석
                self.show_class_detailed_analysis()
            elif result == 1:  # 숙련도 목표
                self.show_mastery_goals()
            # result == 2 또는 취소시 자동으로 돌아감
                
        except ImportError:
            # 폴백: 간단한 텍스트
            print("\n🎯 직업 숙련도")
            print("="*30)
            print("현재 해금된 직업: 4개 (기본)")
            print("• 전사")
            print("• 아크메이지") 
            print("• 궁수")
            print("• 도적")
            print("\n더 많은 직업을 해금하여 숙련도를 쌓아보세요!")
            input("아무 키나 눌러 계속...")
        except Exception as e:
            print(f"직업 숙련도 메뉴 오류: {e}")
            input("아무 키나 눌러 계속...")
    
    def show_class_detailed_analysis(self):
        """직업별 상세 분석"""
        try:
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green
            from game.cursor_menu_system import create_simple_menu
            
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_cyan('📊 직업별 상세 분석')}")
            print(f"{bright_cyan('='*60)}")
            
            meta_data = self.meta_progression.data if hasattr(self, 'meta_progression') and self.meta_progression else {}
            class_stats = meta_data.get('class_play_stats', {})
            
            if not class_stats:
                print(f"{yellow('아직 직업별 플레이 기록이 없습니다.')}")
                input("아무 키나 눌러 계속...")
                return
            
            # 상위 5개 직업 분석
            sorted_classes = sorted(class_stats.items(), key=lambda x: x[1].get('plays', 0), reverse=True)
            top_classes = sorted_classes[:5]
            
            print(f"\n{bright_yellow('🏆 가장 많이 플레이한 직업 TOP 5')}")
            print("-" * 50)
            
            for rank, (class_name, stats) in enumerate(top_classes, 1):
                plays = stats.get('plays', 0)
                best_floor = stats.get('best_floor', 0)
                total_kills = stats.get('total_kills', 0)
                avg_floor = stats.get('total_floors', 0) / plays if plays > 0 else 0
                avg_kills = total_kills / plays if plays > 0 else 0
                
                print(f"{rank}. {bright_green(class_name)}")
                print(f"   플레이: {plays}회 | 최고층: {best_floor}층")
                print(f"   평균 도달층: {avg_floor:.1f}층 | 평균 처치: {avg_kills:.1f}마리")
                print()
            
            # 효율성 분석
            print(f"{bright_yellow('⚡ 효율성 분석')}")
            print("-" * 30)
            
            efficiency_ranking = []
            for class_name, stats in class_stats.items():
                plays = stats.get('plays', 0)
                if plays > 0:
                    avg_floor = stats.get('total_floors', 0) / plays
                    avg_kills = stats.get('total_kills', 0) / plays
                    efficiency_score = avg_floor * 2 + avg_kills  # 층수에 더 높은 가중치
                    efficiency_ranking.append((class_name, efficiency_score, avg_floor, avg_kills))
            
            efficiency_ranking.sort(key=lambda x: x[1], reverse=True)
            
            print("효율성 순위 (층수×2 + 처치수 기준):")
            for rank, (class_name, score, avg_floor, avg_kills) in enumerate(efficiency_ranking[:5], 1):
                print(f"{rank}. {class_name}: {score:.1f}점 (층수 {avg_floor:.1f}, 처치 {avg_kills:.1f})")
            
            # 성장 가능성 분석
            print(f"\n{bright_yellow('📈 성장 가능성')}")
            print("-" * 30)
            
            underused = [(name, stats) for name, stats in class_stats.items() 
                        if stats.get('plays', 0) < 3 and stats.get('plays', 0) > 0]
            
            if underused:
                print("더 많은 플레이가 필요한 직업:")
                for class_name, stats in underused:
                    plays = stats.get('plays', 0)
                    potential = stats.get('best_floor', 0) * 2  # 잠재력 점수
                    print(f"• {class_name}: {plays}회 플레이, 잠재력 {potential}점")
            else:
                print("모든 직업을 충분히 플레이했습니다!")
            
            # 추천사항
            print(f"\n{bright_yellow('💡 개선 추천')}")
            print("-" * 30)
            
            if efficiency_ranking:
                best_class = efficiency_ranking[0][0]
                print(f"• 가장 효율적인 직업: {bright_green(best_class)}")
                print(f"• 이 직업으로 더 높은 층수에 도전해보세요!")
            
            if underused:
                print(f"• 새로운 도전: {underused[0][0]} 직업을 더 플레이해보세요")
            
            print(f"• 다양한 직업 조합으로 파티를 구성해보세요")
            print(f"• 각 직업의 특성을 활용한 전략을 개발해보세요")
            
            input(f"\n아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"상세 분석 중 오류 발생: {e}")
            input("아무 키나 눌러 계속...")
    
    def show_mastery_goals(self):
        """숙련도 목표 설정"""
        try:
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green
            
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_cyan('🎯 직업 숙련도 목표 설정')}")
            print(f"{bright_cyan('='*60)}")
            
            meta_data = self.meta_progression.data if hasattr(self, 'meta_progression') and self.meta_progression else {}
            class_stats = meta_data.get('class_play_stats', {})
            unlocked_classes = meta_data.get('unlocked_classes', [])
            base_classes = ["전사", "아크메이지", "궁수", "도적"]
            
            all_available = base_classes + unlocked_classes
            
            print(f"\n{bright_yellow('📊 현재 숙련도 현황')}")
            print("-" * 40)
            
            mastery_levels = {
                "마스터": 0,
                "전문가": 0, 
                "숙련자": 0,
                "경험자": 0,
                "초보자": 0
            }
            
            for class_name in all_available:
                stats = class_stats.get(class_name, {'plays': 0, 'best_floor': 0})
                plays = stats.get('plays', 0)
                best_floor = stats.get('best_floor', 0)
                mastery_score = plays * 10 + best_floor * 5
                
                if mastery_score >= 200:
                    mastery_levels["마스터"] += 1
                elif mastery_score >= 100:
                    mastery_levels["전문가"] += 1
                elif mastery_score >= 50:
                    mastery_levels["숙련자"] += 1
                elif mastery_score >= 20:
                    mastery_levels["경험자"] += 1
                else:
                    mastery_levels["초보자"] += 1
            
            for level, count in mastery_levels.items():
                if count > 0:
                    print(f"{level}: {count}개 직업")
            
            # 목표 설정
            print(f"\n{bright_yellow('🎯 추천 목표')}")
            print("-" * 30)
            
            goals = []
            
            # 마스터 목표
            if mastery_levels["마스터"] == 0:
                goals.append("🏆 첫 마스터 직업 달성 (200점 이상)")
            elif mastery_levels["마스터"] < 3:
                goals.append(f"🏆 마스터 직업 3개 달성 (현재 {mastery_levels['마스터']}개)")
            
            # 전문가 목표
            if mastery_levels["전문가"] < 5:
                goals.append(f"💎 전문가 직업 5개 달성 (현재 {mastery_levels['전문가']}개)")
            
            # 초보자 탈출 목표
            if mastery_levels["초보자"] > 0:
                goals.append(f"📈 모든 직업 초보자 탈출 (현재 {mastery_levels['초보자']}개 남음)")
            
            # 전체 해금 목표
            total_unlocked = len(all_available)
            if total_unlocked < 27:
                goals.append(f"🔓 모든 직업 해금 (현재 {total_unlocked}/27개)")
            
            for i, goal in enumerate(goals, 1):
                print(f"{i}. {goal}")
            
            # 달성 계획
            print(f"\n{bright_yellow('📋 달성 계획')}")
            print("-" * 30)
            
            print("단기 목표 (1-2주):")
            print("• 가장 적게 플레이한 직업 3회씩 플레이")
            print("• 한 직업으로 10층 이상 도달")
            
            print("\n중기 목표 (1개월):")
            print("• 주력 직업으로 마스터 등급 달성")
            print("• 5개 직업을 전문가 등급으로 성장")
            
            print("\n장기 목표 (3개월):")
            print("• 모든 해금된 직업을 숙련자 이상으로")
            print("• 새로운 직업 해금 및 숙련도 개발")
            
            print(f"\n{bright_green('꾸준한 플레이로 목표를 달성해보세요! 💪')}")
            input("아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"목표 설정 중 오류 발생: {e}")
            input("아무 키나 눌러 계속...")

    def get_available_field_skills(self):
        """사용 가능한 필드 스킬 목록 반환"""
        available_skills = []
        
        if not hasattr(self, 'party_manager') or not self.party_manager.members:
            return available_skills
        
        # 각 파티원의 필드 스킬 확인
        for member in self.party_manager.members:
            if not member.is_alive:
                continue
                
            # 직업별 필드 스킬 정의
            skills_by_class = {
                "도적": ["자물쇠 해제", "은신"],
                "아크메이지": ["분석", "순간이동"],  
                "성기사": ["정화", "파티 축복"],
                "드루이드": ["파티 치유", "보물 탐지"],
                "무당": ["정화", "분석"],
                "기계공학자": ["자물쇠 해제", "분석"],
                "정령술사": ["순간이동", "파티 축복"]
            }
            
            if member.character_class in skills_by_class:
                for skill in skills_by_class[member.character_class]:
                    available_skills.append((skill, member))
        
        return available_skills
    
    def use_field_skill(self, skill_name, character):
        """필드 스킬 사용"""
        print(f"\n✨ {character.name}이(가) '{skill_name}' 스킬을 사용합니다!")
        
        if skill_name == "자물쇠 해제":
            print("🔓 숨겨진 보물상자를 발견했습니다!")
            # 골드 추가 획득
            bonus_gold = random.randint(50, 150)
            if hasattr(self, 'gold'):
                self.gold += bonus_gold
            print(f"💰 보너스 골드 +{bonus_gold}")
            
        elif skill_name == "은신":
            print("👤 다음 인카운터를 회피할 확률이 증가했습니다!")
            # 은신 효과 플래그 설정 (구현 필요)
            
        elif skill_name == "분석":
            print("🔍 주변 정보를 분석했습니다!")
            # 현재 층의 정보 표시
            print(f"📍 현재 위치: {self.world.current_level}층")
            print(f"🗺️ 맵 크기: {self.world.width}x{self.world.height}")
            
        elif skill_name == "순간이동":
            print("🌀 안전한 위치로 순간이동했습니다!")
            # 플레이어를 안전한 위치로 이동 (구현 필요)
            
        elif skill_name == "정화":
            print("✨ 파티의 상태이상을 정화했습니다!")
            # 파티원들의 상태이상 제거
            for member in self.party_manager.members:
                if hasattr(member, 'status_effects'):
                    member.status_effects.clear()
                    
        elif skill_name == "파티 축복":
            print("🙏 파티 전체에 축복을 내렸습니다!")
            # 임시 능력치 증가 효과
            for member in self.party_manager.members:
                if member.is_alive:
                    member.temp_atk_bonus = getattr(member, 'temp_atk_bonus', 0) + 10
                    member.temp_def_bonus = getattr(member, 'temp_def_bonus', 0) + 10
            print("⚔️ 모든 파티원의 공격력과 방어력이 일시적으로 증가했습니다!")
            
        elif skill_name == "파티 치유":
            print("💚 파티 전체를 치유했습니다!")
            heal_amount = int(character.max_mp * 0.3)  # MP의 30%만큼 치유
            for member in self.party_manager.members:
                if member.is_alive:
                    member.heal(heal_amount)
            print(f"❤️ 모든 파티원이 {heal_amount}만큼 회복했습니다!")
            
        elif skill_name == "보물 탐지":
            print("💎 주변의 숨겨진 보물을 탐지했습니다!")
            # 보물 발견 확률 증가 효과
            print("🔍 다음 인카운터에서 보물 발견 확률이 증가했습니다!")
        
        # MP 소모
        mp_cost = 20
        if character.current_mp >= mp_cost:
            character.current_mp -= mp_cost
            print(f"💙 {character.name}의 MP -{mp_cost}")
        else:
            print("⚠️ MP가 부족하여 효과가 감소했습니다!")

    def start_elite_battle(self):
        """엘리트 전투 시작 (몬스터 소굴) - Brave Combat System 사용"""
        try:
            from game.brave_combat import BraveCombatSystem
            from game.character import Character
            import random
            
            print(f"\n💀 {bright_red('엘리트 몬스터 소굴에 진입합니다!')}")
            print("🔥 강력한 적들이 당신을 기다리고 있습니다...")
            
            # 현재 층수에 맞는 엘리트 적 생성
            current_floor = getattr(self.world, 'current_level', 1)
            
            # 엘리트 몬스터 데이터
            elite_monsters = [
                {
                    "name": "골렘 우두머리",
                    "level": current_floor + 2,
                    "hp_multiplier": 1.8,
                    "attack_multiplier": 1.5,
                    "defense_multiplier": 1.3
                },
                {
                    "name": "오크 족장",
                    "level": current_floor + 2,
                    "hp_multiplier": 1.6,
                    "attack_multiplier": 1.7,
                    "defense_multiplier": 1.2
                },
                {
                    "name": "어둠의 마법사",
                    "level": current_floor + 2,
                    "hp_multiplier": 1.4,
                    "attack_multiplier": 1.8,
                    "defense_multiplier": 1.0
                },
                {
                    "name": "거대 거미",
                    "level": current_floor + 2,
                    "hp_multiplier": 1.5,
                    "attack_multiplier": 1.6,
                    "defense_multiplier": 1.1
                }
            ]
            
            # 랜덤으로 엘리트 몬스터 선택
            elite_data = random.choice(elite_monsters)
            
            # 엘리트 몬스터 생성
            elite_enemy = Character(
                name=elite_data["name"],
                character_class="적",
                level=elite_data["level"]
            )
            
            # 엘리트 능력치 강화
            base_hp = elite_enemy.max_hp
            base_attack = elite_enemy.physical_attack
            base_defense = elite_enemy.physical_defense
            
            elite_enemy.max_hp = int(base_hp * elite_data["hp_multiplier"])
            elite_enemy.current_hp = elite_enemy.max_hp
            elite_enemy.physical_attack = int(base_attack * elite_data["attack_multiplier"])
            elite_enemy.physical_defense = int(base_defense * elite_data["defense_multiplier"])
            
            # 적 마킹
            elite_enemy.is_enemy = True
            elite_enemy.is_elite = True
            
            print(f"⚔️ {elite_data['name']} (레벨 {elite_data['level']})이(가) 나타났습니다!")
            print(f"   HP: {elite_enemy.max_hp} | 공격력: {elite_enemy.physical_attack} | 방어력: {elite_enemy.physical_defense}")
            
            import time
            time.sleep(2.0)  # 긴장감 조성
            
            # 전투 시작 - Brave Combat System 사용
            brave_combat = BraveCombatSystem(self.audio_system, self.audio_system)
            combat_result = brave_combat.start_battle(self.party_manager.members, [elite_enemy])
            
            # 전투 결과 처리
            if combat_result:
                print(f"\n🎉 {bright_green('엘리트 전투 승리!')}")
                
                # 엘리트 적 드롭 시스템 사용
                try:
                    from game.enemy_drop_system import get_drop_system
                    drop_system = get_drop_system()
                    
                    # 엘리트 적으로 마킹
                    elite_enemy.is_elite = True
                    
                    drops = drop_system.calculate_drops(elite_enemy, current_floor, 1)
                    drops = drop_system.apply_drop_bonuses(drops, self.party_manager.members)
                    
                    # 경험치 분배
                    if drops['experience'] > 0:
                        print(f"⭐ 특별 보상 경험치: {drops['experience']}")
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            exp_per_member = int(drops['experience'] * 0.75)  # 전체 경험치의 75%씩 분배
                            for member in self.party_manager.members:
                                if member.is_alive:
                                    member.gain_experience(exp_per_member)
                    
                    # 골드 지급
                    if drops['gold'] > 0:
                        print(f"💰 특별 보상 골드: {drops['gold']}")
                        if hasattr(self, 'gold'):
                            self.gold += drops['gold']
                    
                    # 아이템 드롭
                    for item in drops['items']:
                        print(f"✨ {bright_yellow(f'엘리트 드롭: {item.name}을(를) 획득했습니다!')}")
                        # 아이템 획득 효과음
                        try:
                            if hasattr(self, 'audio_system') and self.audio_system:
                                self.audio_system.play_sfx("item_pickup")
                        except:
                            pass
                        
                        if self.party_manager.members and hasattr(self.party_manager.members[0], 'inventory'):
                            self.party_manager.members[0].inventory.add_item(item)
                    
                    if not drops['items']:
                        print("📦 아이템 드롭 없음")
                        
                except Exception as e:
                    print(f"⚠️ 엘리트 드롭 시스템 오류: {e}")
                    print("드롭 시스템을 사용할 수 없습니다.")
                
                # 전투 통계 업데이트
                if hasattr(self.world, 'combat_stats'):
                    self.world.combat_stats['elite_victories'] = self.world.combat_stats.get('elite_victories', 0) + 1
                
            else:
                print(f"\n💀 {bright_red('엘리트 전투에서 패배했습니다...')}")
                
        except Exception as e:
            print(f"⚠️ 엘리트 전투 시작 중 오류: {e}")
            # 일반 전투로 폴백
            self.start_combat()

    def start_ambush_battle(self):
        """매복 전투 시작 - 불리한 상황에서 시작"""
        try:
            from game.brave_combat import BraveCombatSystem
            from game.character import Character
            import random
            
            print(f"\n💀 {bright_red('매복 공격!')}")
            print("⚠️ 적들에게 기습당했습니다!")
            
            # 현재 층수에 맞는 적 생성 (여러 마리)
            current_floor = getattr(self.world, 'current_level', 1)
            
            # 매복 적 수는 2-4마리
            ambush_enemy_count = random.randint(2, 4)
            ambush_enemies = []
            
            for i in range(ambush_enemy_count):
                try:
                    from game.enemy_system import EnemyManager
                    enemy_manager = EnemyManager()
                    enemy = enemy_manager.spawn_enemy(current_floor)
                    
                    # 매복 공격으로 약간 강화
                    enemy.physical_attack = int(enemy.physical_attack * 1.2)
                    enemy.is_enemy = True
                    
                    ambush_enemies.append(enemy)
                    
                except Exception as e:
                    print(f"❌ 매복 적 생성 중 오류: {e}")
                    # 기본 적 생성 (폴백)
                    basic_enemy = Character(f"매복 고블린 {i+1}", "적")
                    basic_enemy.max_hp = 80 + (current_floor * 15)
                    basic_enemy.current_hp = basic_enemy.max_hp
                    basic_enemy.physical_attack = int((20 + (current_floor * 8)) * 1.2)  # 매복 보너스
                    basic_enemy.physical_defense = 15 + (current_floor * 5)
                    basic_enemy.is_enemy = True
                    ambush_enemies.append(basic_enemy)
            
            print(f"👹 {ambush_enemy_count}마리의 적이 매복 공격을 가합니다!")
            for enemy in ambush_enemies:
                print(f"   - {enemy.name} (HP: {enemy.max_hp}, 공격: {enemy.physical_attack})")
            
            import time
            time.sleep(2.0)  # 긴장감 조성
            
            # 매복 효과: 파티원들의 초기 ATB를 낮춤
            print(f"\n⚠️ {bright_red('기습당해 행동이 늦어집니다!')}")
            if hasattr(self, 'party_manager') and self.party_manager.members:
                for member in self.party_manager.members:
                    if member.is_alive and hasattr(member, 'current_atb'):
                        member.current_atb = max(0, member.current_atb - 30)  # ATB 30 감소
            
            # 전투 시작 - Brave Combat System 사용
            brave_combat = BraveCombatSystem(self.audio_system, self.audio_system)
            combat_result = brave_combat.start_battle(self.party_manager.members, ambush_enemies)
            
            # 전투 결과 처리
            if combat_result:
                print(f"\n🎉 {bright_green('매복 공격을 막아냈습니다!')}")
                
                # 매복 적들 드롭 시스템 사용
                try:
                    from game.enemy_drop_system import get_drop_system
                    drop_system = get_drop_system()
                    
                    total_gold = 0
                    total_exp = 0
                    all_items = []
                    
                    # 각 매복 적에 대해 드롭 계산
                    for enemy in ambush_enemies:
                        drops = drop_system.calculate_drops(enemy, current_floor, 1)
                        drops = drop_system.apply_drop_bonuses(drops, self.party_manager.members)
                        
                        total_gold += drops['gold']
                        total_exp += drops['experience']
                        all_items.extend(drops['items'])
                    
                    # 매복 방어 보너스 (20% 추가)
                    total_gold = int(total_gold * 1.2)
                    total_exp = int(total_exp * 1.2)
                    
                    # 경험치 분배
                    if total_exp > 0:
                        print(f"⭐ 매복 방어 보상 경험치: {total_exp}")
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            exp_per_member = int(total_exp * 0.75)  # 전체 경험치의 75%씩 분배
                            for member in self.party_manager.members:
                                if member.is_alive:
                                    if hasattr(member, 'gain_experience'):
                                        member.gain_experience(exp_per_member)
                                    elif hasattr(member, 'gain_exp'):
                                        member.gain_exp(exp_per_member)
                    
                    # 골드 지급
                    if total_gold > 0:
                        print(f"💰 매복 방어 보상 골드: {total_gold}")
                        if hasattr(self, 'gold'):
                            self.gold += total_gold
                    
                    # 아이템 드롭
                    for item in all_items:
                        print(f"🎁 매복 드롭: {item.name}을(를) 획득했습니다!")
                        # 아이템 획득 효과음
                        try:
                            if hasattr(self, 'audio_system') and self.audio_system:
                                self.audio_system.play_sfx("item_pickup")
                        except:
                            pass
                        
                        if self.party_manager.members and hasattr(self.party_manager.members[0], 'inventory'):
                            self.party_manager.members[0].inventory.add_item(item)
                    
                    if not all_items:
                        print("📦 아이템 드롭 없음")
                        
                except Exception as e:
                    print(f"⚠️ 매복 드롭 시스템 오류: {e}")
                    print("드롭 시스템을 사용할 수 없습니다.")
                
            else:
                print(f"\n💀 {bright_red('매복 공격에 당했습니다...')}")
                
        except Exception as e:
            print(f"⚠️ 매복 전투 시작 중 오류: {e}")
            # 일반 전투로 폴백
            self.start_combat()

    def start_combat(self):
        """전투 시작 - Brave Combat System 사용"""
        try:
            from game.brave_combat import BraveCombatSystem
            
            # 현재 위치의 적 확인 (world.player_pos 사용)
            if hasattr(self.world, 'player_pos'):
                player_x, player_y = self.world.player_pos
            else:
                player_x, player_y = 0, 0  # 기본값
                
            enemies_at_position = []
            
            # 주변 적들 찾기 (world.enemies_positions 사용)
            if hasattr(self.world, 'enemies_positions'):
                for enemy_pos in self.world.enemies_positions:
                    enemy_x, enemy_y = enemy_pos
                    if abs(enemy_x - player_x) <= 1 and abs(enemy_y - player_y) <= 1:
                        # 적 데이터 찾기
                        if hasattr(self.world, 'floor_enemies') and enemy_pos in self.world.floor_enemies:
                            enemy_data = self.world.floor_enemies[enemy_pos]
                            
                            # dict 객체인 경우 Character 객체로 변환
                            if isinstance(enemy_data, dict):
                                # 조용히 변환 (경고 메시지 제거)
                                try:
                                    from game.enemy_system import EnemyManager
                                    enemy_manager = EnemyManager()
                                    enemy_level = enemy_data.get('level', 1)
                                    enemy_type = enemy_data.get('type', '고블린')
                                    enemy_character = enemy_manager.spawn_enemy(enemy_level)
                                    if hasattr(enemy_character, 'name'):
                                        enemies_at_position.append(enemy_character)
                                    else:
                                        # 폴백: 기본 Character 생성
                                        from game.character import Character
                                        fallback_enemy = Character(enemy_type, "적")
                                        fallback_enemy.max_hp = 50 + (enemy_level * 20)
                                        fallback_enemy.current_hp = fallback_enemy.max_hp
                                        fallback_enemy.physical_attack = 15 + (enemy_level * 5)
                                        fallback_enemy.physical_defense = 10 + (enemy_level * 3)
                                        enemies_at_position.append(fallback_enemy)
                                except Exception as e:
                                    print(f"❌ dict 객체 변환 중 오류: {e}")
                                    # 마지막 폴백
                                    from game.character import Character
                                    fallback_enemy = Character("적", "적")
                                    fallback_enemy.max_hp = 50
                                    fallback_enemy.current_hp = 50
                                    fallback_enemy.physical_attack = 15
                                    fallback_enemy.physical_defense = 10
                                    enemies_at_position.append(fallback_enemy)
                            else:
                                # 이미 Character 객체인 경우
                                enemies_at_position.append(enemy_data)
            
            if not enemies_at_position:
                # 랜덤 적 생성
                try:
                    from game.enemy_system import EnemyManager
                    enemy_manager = EnemyManager()
                    enemy = enemy_manager.spawn_enemy(self.world.current_level)
                    enemies_at_position = [enemy]
                    print(f"🦹 {enemy.name}이(가) 나타났습니다!")
                except Exception as e:
                    print(f"❌ 적 생성 중 오류: {e}")
                    # 기본 적 생성 (폴백)
                    from game.character import Character
                    basic_enemy = Character("고블린", "적")
                    basic_enemy.max_hp = 100
                    basic_enemy.current_hp = 100
                    basic_enemy.physical_attack = 25
                    basic_enemy.physical_defense = 20
                    enemies_at_position = [basic_enemy]
                    print(f"⚠️ 기본 적 생성: {basic_enemy.name}")
            
            # Brave 전투 시스템 초기화 및 실행
            brave_combat = BraveCombatSystem(self.audio_system, self.audio_system)
            combat_result = brave_combat.start_battle(self.party_manager.members, enemies_at_position)
            
            # 전투 결과 처리
            if combat_result:
                print(f"\n🎉 {bright_green('승리했습니다!')}")
                
                # 적 드롭 시스템 사용
                try:
                    from game.enemy_drop_system import get_drop_system
                    drop_system = get_drop_system()
                    
                    total_gold = 0
                    total_exp = 0
                    all_items = []
                    
                    # 각 적에 대해 드롭 계산
                    current_floor = getattr(self.world, 'current_floor', 1)
                    party_level = sum(member.level for member in self.party_manager.members) // len(self.party_manager.members)
                    
                    for enemy in enemies_at_position:
                        drops = drop_system.calculate_drops(enemy, current_floor, party_level)
                        
                        # 파티 보너스 적용
                        drops = drop_system.apply_drop_bonuses(drops, self.party_manager.members)
                        
                        total_gold += drops['gold']
                        total_exp += drops['experience']
                        all_items.extend(drops['items'])
                    
                    # 보상 지급
                    print(f"⭐ 경험치 +{total_exp}")
                    print(f"💰 골드 +{total_gold}")
                    
                    if all_items:
                        print(f"📦 아이템 획득:")
                        for item in all_items:
                            print(f"  • {item.name}")
                            # 첫 번째 파티원에게 아이템 추가
                            if hasattr(self.party_manager.members[0], 'inventory'):
                                self.party_manager.members[0].inventory.add_item(item)
                    else:
                        print("📦 아이템 드롭 없음")
                    
                    # 골드 추가
                    if hasattr(self, 'gold'):
                        self.gold += total_gold
                    
                    # 경험치 분배 (개선된 방식: 각 파티원이 전체 경험치의 75%를 받음)
                    exp_per_member = int(total_exp * 0.75)  # 전체 경험치의 75%씩 분배
                    for member in self.party_manager.members:
                        if member.is_alive:
                            if hasattr(member, 'gain_experience'):
                                member.gain_experience(exp_per_member)
                            elif hasattr(member, 'gain_exp'):
                                member.gain_exp(exp_per_member)
                        
                except Exception as e:
                    print(f"⚠️ 드롭 시스템 오류: {e}")
                    print("드롭 시스템을 사용할 수 없습니다.")
                
                print("아무 키나 눌러 계속...")
                self.keyboard.wait_for_key()
                
                # 🎵 승리 후 사용자가 키를 눌렀을 때 던전 BGM으로 복귀
                try:
                    if hasattr(self, 'audio_system') and self.audio_system:
                        self.audio_system.play_bgm("dungeon", loop=True)
                        print("🎵 던전 BGM으로 복귀!")
                    elif hasattr(self, 'sound_manager') and self.sound_manager:
                        self.sound_manager.play_bgm("dungeon")
                        print("🎵 던전 BGM으로 복귀!")
                except Exception as e:
                    print(f"⚠️ 던전 BGM 복구 실패: {e}")
                
                # 적 제거
                    
                    # 각 적에 대해 드롭 계산
                    current_floor = getattr(self.world, 'current_level', 1)
                    party_level = self.party_manager.members[0].level if self.party_manager.members else 1
                    
                    for enemy in enemies_at_position:
                        drops = drop_system.calculate_drops(enemy, current_floor, party_level)
                        
                        # 파티 보너스 적용
                        drops = drop_system.apply_drop_bonuses(drops, self.party_manager.members)
                        
                        total_gold += drops['gold']
                        total_exp += drops['experience']
                        all_items.extend(drops['items'])
                    
                    # 경험치 분배 (개선된 방식: 각 파티원이 전체 경험치의 75%를 받음)
                    if total_exp > 0:
                        print(f"⭐ 경험치 +{total_exp}")
                        exp_per_member = int(total_exp * 1.0)  # 전체 경험치의 100%씩 분배
                        for member in self.party_manager.members:
                            if member.is_alive:
                                if hasattr(member, 'gain_experience'):
                                    member.gain_experience(exp_per_member)
                                elif hasattr(member, 'gain_exp'):
                                    member.gain_exp(exp_per_member)
                    
                    # 골드 지급
                    if total_gold > 0:
                        print(f"💰 골드 +{total_gold}")
                        if hasattr(self, 'gold'):
                            self.gold += total_gold
                        elif hasattr(self, 'party_manager') and hasattr(self.party_manager, 'add_gold'):
                            self.party_manager.add_gold(total_gold)
                    
                    # 아이템 드롭
                    for item in all_items:
                        print(f"🎁 {item.name}을(를) 획득했습니다!")
                        # 아이템 획득 효과음
                        try:
                            if hasattr(self, 'audio_system') and self.audio_system:
                                self.audio_system.play_sfx("item_pickup")
                        except:
                            pass
                        
                        # 첫 번째 파티원 인벤토리에 추가
                        if self.party_manager.members and hasattr(self.party_manager.members[0], 'inventory'):
                            self.party_manager.members[0].inventory.add_item(item)
                    
                    # 아이템이 없으면 드롭 없음 메시지
                    if not all_items:
                        print("📦 아이템 드롭 없음")
                    
                except Exception as e:
                    print(f"⚠️ 드롭 시스템 오류: {e}")
                    # 폴백: 기본 보상
                    exp_reward = 50 * len(enemies_at_position)
                    gold_reward = 25 * len(enemies_at_position)
                    
                    if exp_reward > 0:
                        print(f"⭐ 경험치 +{exp_reward}")
                        exp_per_member = int(exp_reward * 0.75)  # 전체 경험치의 75%씩 분배
                        for member in self.party_manager.members:
                            if member.is_alive:
                                if hasattr(member, 'gain_experience'):
                                    member.gain_experience(exp_per_member)
                                elif hasattr(member, 'gain_exp'):
                                    member.gain_exp(exp_per_member)
                    
                    if gold_reward > 0:
                        print(f"💰 골드 +{gold_reward}")
                        if hasattr(self, 'gold'):
                            self.gold += gold_reward
                
                # 적 제거 (enemies_positions에서)
                for enemy_pos in list(self.world.enemies_positions):
                    enemy_x, enemy_y = enemy_pos
                    if abs(enemy_x - player_x) <= 1 and abs(enemy_y - player_y) <= 1:
                        self.world.enemies_positions.remove(enemy_pos)
                        if hasattr(self.world, 'floor_enemies') and enemy_pos in self.world.floor_enemies:
                            del self.world.floor_enemies[enemy_pos]
                        # 타일에서 적 제거
                        if self.world.is_valid_pos(enemy_x, enemy_y):
                            self.world.tiles[enemy_y][enemy_x].has_enemy = False
                        
            else:
                print(f"\n💀 {bright_red('패배했습니다...')}")
                # 패배 처리 (게임 오버 또는 재시작)
                
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            
        except ImportError as e:
            print(f"⚠️ 전투 시스템 로드 실패: {e}")
            print("기본 전투 시스템을 사용합니다.")
            # 간단한 전투 시뮬레이션
            print("⚔️ 간단한 전투를 진행합니다...")
            victory = random.choice([True, False])
            
            if victory:
                print("🎉 승리했습니다!")
                exp_reward = random.randint(30, 70)
                print(f"⭐ 경험치 +{exp_reward}")
                # 적 제거
                if hasattr(self.world, 'enemies_positions') and self.world.enemies_positions:
                    enemy_pos = self.world.enemies_positions[0]
                    self.world.enemies_positions.remove(enemy_pos)
                    if hasattr(self.world, 'floor_enemies') and enemy_pos in self.world.floor_enemies:
                        del self.world.floor_enemies[enemy_pos]
            else:
                print("💀 패배했습니다...")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        except Exception as e:
            print(f"⚠️ 전투 중 오류 발생: {e}")
            print("전투를 건너뜁니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")

    def _handle_consumable_item(self, result: int, consumable_items: list):
        """소모품 아이템 처리"""
        selected_item_info = consumable_items[result]
        print(f"선택된 아이템: {selected_item_info}")
        
        # 소모품 사용 옵션만 제공
        all_items = []
        item_owners = []
        
        for member in self.party_manager.members:
            if hasattr(member, 'inventory') and hasattr(member.inventory, 'items'):
                for item in member.inventory.items:
                    # 장비 아이템은 건너뛰기
                    if hasattr(item, 'item_type') and item.item_type in ['weapon', 'armor', 'accessory']:
                        continue
                    all_items.append(item)
                    item_owners.append(member)
        
        selected_item = all_items[result] if result < len(all_items) else None
        
        if selected_item:
            try:
                from game.cursor_menu_system import create_simple_menu
                # 소모품 아이템 옵션 구성
                action_options = ["🍶 사용하기", "ℹ️ 정보 보기", "🚪 취소"]
                action_descriptions = ["아이템을 사용합니다", "아이템 정보를 확인합니다", "취소하고 돌아갑니다"]
                
                action_menu = create_simple_menu("아이템 액션", action_options, action_descriptions)
                action_result = action_menu.run()
                
                if action_result == 0:  # 사용하기
                    self._use_party_item(result)
                elif action_result == 1:  # 정보 보기
                    print(f"\n{selected_item_info}의 상세 정보")
                    if hasattr(selected_item, 'description'):
                        print(f"설명: {selected_item.description}")
                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                # 취소는 자동으로 처리
            except ImportError:
                print(f"\n{selected_item_info}의 상세 정보")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        else:
            print(f"\n{selected_item_info}의 상세 정보")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")

    def _handle_equipment_item(self, result: int, equipment_items: list):
        """장비 아이템 처리"""
        if result >= len(equipment_items):
            print("❌ 잘못된 장비 선택입니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            return
            
        selected_item_info = equipment_items[result]
        print(f"선택된 장비: {selected_item_info}")
        
        # 선택된 아이템 정보 파싱 (형식: "아이템명 x개수 (소유자명)")
        import re
        match = re.match(r'(.+?) x(\d+) \((.+?)\)', selected_item_info)
        if not match:
            print("❌ 아이템 정보를 파싱할 수 없습니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            return
            
        item_name = match.group(1).strip()
        quantity = int(match.group(2))
        owner_name = match.group(3).strip()
        
        # 소유자 찾기
        owner = None
        for member in self.party_manager.members:
            if member.name == owner_name:
                owner = member
                break
                
        if not owner:
            print(f"❌ 소유자 {owner_name}를 찾을 수 없습니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            return
        
        # 실제 아이템 객체 가져오기
        from game.items import ItemDatabase
        item_db = ItemDatabase()
        item = item_db.get_item(item_name)
        
        if not item:
            print(f"❌ {item_name}을(를) 아이템 데이터베이스에서 찾을 수 없습니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            return
        
        try:
            from game.cursor_menu_system import create_simple_menu
            # 장비 아이템 옵션 구성
            action_options = ["⚔️ 장착하기", "ℹ️ 정보 보기", "🚪 취소"]
            action_descriptions = ["장비를 장착합니다", "장비 정보를 확인합니다", "취소하고 돌아갑니다"]
            
            action_menu = create_simple_menu("장비 액션", action_options, action_descriptions)
            action_result = action_menu.run()
            
            if action_result == 0:  # 장착하기
                self._equip_item(item, owner)
            elif action_result == 1:  # 정보 보기
                self._show_item_info(item)
            # 취소는 자동으로 처리
        except ImportError:
            print(f"\n{item_name}의 상세 정보")
            self._show_item_info(item)
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            print(f"\n{selected_item_info}의 상세 정보")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")

    def _show_item_info(self, item):
        """아이템 정보 표시"""
        print(f"\n{'='*50}")
        print(f"✨ {item.name} 정보 ✨")
        print(f"{'='*50}")
        print(f"🏷️ 타입: {item.item_type.value}")
        print(f"⭐ 등급: {item.rarity.value}")
        print(f"📝 설명: {item.description}")
        
        # 능력치 정보
        if hasattr(item, 'get_effective_stats'):
            effective_stats = item.get_effective_stats()
            if effective_stats:
                print(f"\n📊 능력치 효과:")
                for stat, value in effective_stats.items():
                    if value > 0:
                        stat_name = {
                            "physical_attack": "물리공격력",
                            "physical_defense": "물리방어력", 
                            "magic_attack": "마법공격력",
                            "magic_defense": "마법방어력",
                            "speed": "속도",
                            "vision_range": "시야범위"
                        }.get(stat, stat)
                        print(f"   {stat_name}: +{value}")
        
        # 내구도 정보
        if hasattr(item, 'current_durability') and hasattr(item, 'max_durability'):
            durability_pct = (item.current_durability / item.max_durability * 100) if item.max_durability > 0 else 0
            print(f"\n🔧 내구도: {item.current_durability}/{item.max_durability} ({durability_pct:.1f}%)")
        
        print(f"{'='*50}")
        self.keyboard.wait_for_key("아무 키나 눌러 계속...")

    def _equip_item(self, item, owner):
        """장비 아이템 장착"""
        try:
            print(f"\n{item.name}을(를) 장착하시겠습니까?")
            print(f"소유자: {owner.name}")
            
            # 파티원 선택 메뉴 (상세 정보 포함)
            from game.cursor_menu_system import create_character_detail_menu
            member_menu = create_character_detail_menu("장착할 파티원 선택", self.party_manager.members)
            member_choice = member_menu.run()
            
            if member_choice is not None and member_choice < len(self.party_manager.members):
                target_member = self.party_manager.members[member_choice]
                
                # 장비 슬롯 결정
                from game.items import ItemType
                slot_map = {
                    ItemType.WEAPON: "weapon",
                    ItemType.ARMOR: "armor",
                    ItemType.ACCESSORY: "accessory"
                }
                
                slot_name = slot_map.get(item.item_type)
                if not slot_name:
                    print(f"❌ {item.name}은(는) 장착할 수 없는 아이템입니다.")
                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                    return
                
                # 현재 장착된 아이템 확인
                current_item = getattr(target_member, f"equipped_{slot_name}", None)
                
                if current_item:
                    print(f"⚠️ {target_member.name}이(가) 이미 {current_item.name}을(를) 장착하고 있습니다.")
                    print("교체하시겠습니까? (Y/N)")
                    
                    choice = input().strip().upper()
                    if choice != 'Y':
                        print("장착을 취소했습니다.")
                        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                        return
                    
                    # 기존 아이템 해제하고 인벤토리에 추가
                    unequipped = target_member.unequip_item(slot_name)
                    if unequipped and hasattr(owner, 'inventory'):
                        owner.inventory.add_item(unequipped.name, 1)
                        print(f"🔄 {unequipped.name}을(를) 해제하고 {owner.name}의 인벤토리에 추가했습니다.")
                
                # 새 아이템 장착
                if target_member.equip_item(item):
                    # 인벤토리에서 아이템 제거
                    if hasattr(owner, 'inventory') and hasattr(owner.inventory, 'remove_item'):
                        owner.inventory.remove_item(item.name, 1)
                    
                    print(f"✅ {target_member.name}에게 {item.name}을(를) 장착했습니다!")
                    
                    # 장비 효과 표시
                    if hasattr(item, 'get_effective_stats'):
                        effective_stats = item.get_effective_stats()
                        if effective_stats:
                            print("📊 장비 효과:")
                            for stat, value in effective_stats.items():
                                if value > 0:
                                    stat_name = {
                                        "physical_attack": "물리공격력",
                                        "physical_defense": "물리방어력",
                                        "magic_attack": "마법공격력", 
                                        "magic_defense": "마법방어력",
                                        "speed": "속도",
                                        "vision_range": "시야범위"
                                    }.get(stat, stat)
                                    print(f"   {stat_name}: +{value}")
                    
                    # 내구도 정보 표시
                    if hasattr(item, 'get_durability_status'):
                        durability_status = item.get_durability_status()
                        if durability_status:
                            print(f"🔧 내구도: {durability_status}")
                            
                else:
                    print(f"❌ {item.name} 장착에 실패했습니다.")
                
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            
        except ImportError:
            print("장비 시스템을 불러올 수 없습니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")

    def _handle_equipment_unequip(self):
        """장비 해제 처리"""
        try:
            from game.cursor_menu_system import create_simple_menu
            
            # 파티원별 장착된 장비 수집
            equipped_items = []
            equipped_descriptions = []
            member_slot_pairs = []  # (member, slot) 쌍
            
            for member in self.party_manager.members:
                equipped = member.get_equipped_items()
                for slot, item in equipped.items():
                    if item:
                        # 아이템 표시 이름 (내구도 포함)
                        if hasattr(item, 'get_display_name'):
                            display_name = item.get_display_name()
                        else:
                            display_name = item.name
                        
                        # 내구도 정보 추가
                        durability_info = ""
                        if hasattr(item, 'get_durability_percentage'):
                            durability_pct = item.get_durability_percentage()
                            if durability_pct < 100:
                                durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
                                durability_info = f" {durability_color}{durability_pct:.0f}%"
                        elif hasattr(item, 'current_durability') and hasattr(item, 'max_durability'):
                            durability_pct = (item.current_durability / item.max_durability * 100) if item.max_durability > 0 else 0
                            durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
                            durability_info = f" {durability_color}{durability_pct:.0f}%"
                        
                        equipped_items.append(f"{member.name}: {display_name} ({slot}){durability_info}")
                        
                        # 설명 (능력치 보너스 및 내구도 포함)
                        description = f"{slot} 슬롯"
                        if hasattr(item, 'get_effective_stats'):
                            effective_stats = item.get_effective_stats()
                            stat_bonuses = []
                            for stat, value in effective_stats.items():
                                if isinstance(value, (int, float)) and value > 0:
                                    if stat == "physical_attack":
                                        stat_bonuses.append(f"공격+{value}")
                                    elif stat == "physical_defense":
                                        stat_bonuses.append(f"방어+{value}")
                                    elif stat == "magic_attack":
                                        stat_bonuses.append(f"마공+{value}")
                                    elif stat == "magic_defense":
                                        stat_bonuses.append(f"마방+{value}")
                                    elif stat == "speed":
                                        stat_bonuses.append(f"속도+{value}")
                                    elif stat == "vision_range":
                                        stat_bonuses.append(f"시야+{value}")
                            
                            if stat_bonuses:
                                description += f" ({', '.join(stat_bonuses)})"
                        
                        # 내구도 정보를 설명에도 추가
                        if hasattr(item, 'current_durability') and hasattr(item, 'max_durability'):
                            description += f" | 내구도: {item.current_durability}/{item.max_durability}"
                        elif hasattr(item, 'get_durability_percentage'):
                            description += f" | 내구도: {item.get_durability_percentage():.0f}%"
                        
                        equipped_descriptions.append(description)
                        member_slot_pairs.append((member, slot))
            
            if not equipped_items:
                print(f"\n{bright_cyan('=== 🔧 장비 해제 ===')}")
                print("장착된 장비가 없습니다.")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                return
            
            # 장비 선택 메뉴 (커서 기반)
            from game.cursor_menu_system import CursorMenu
            
            menu_title = "🔧 해제할 장비 선택"
            menu_options = equipped_items
            menu_descriptions = equipped_descriptions
            
            menu = CursorMenu(
                menu_title,
                menu_options, 
                menu_descriptions,
                audio_manager=getattr(self, 'audio_manager', None),
                keyboard=self.keyboard,
                clear_screen=True,
                extra_content="💡 장비를 선택하여 해제하세요"
            )
            
            result = menu.run()
            
            if result is not None and 0 <= result < len(member_slot_pairs):
                member, slot = member_slot_pairs[result]
                selected_item_name = equipped_items[result]
                
                # 커서 기반 확인 메뉴
                confirm_menu = CursorMenu(
                    f"장비 해제 확인",
                    ["예, 해제합니다", "아니오, 취소합니다"],
                    [
                        f"{selected_item_name}을(를) 해제하고 인벤토리에 추가합니다",
                        "장비 해제를 취소하고 이전 메뉴로 돌아갑니다"
                    ],
                    audio_manager=getattr(self, 'audio_manager', None),
                    keyboard=self.keyboard,
                    clear_screen=True,
                    extra_content=f"📦 선택된 장비: {selected_item_name}"
                )
                
                confirm_result = confirm_menu.run()
                
                if confirm_result == 0:  # 예
                    # 장비 해제 전 현재 장착 상태 확인
                    equipped_item = getattr(member, f"equipped_{slot}", None)
                    
                    if not equipped_item:
                        # 한글 슬롯명으로 다시 시도
                        slot_mapping = {
                            "무기": "weapon",
                            "방어구": "armor", 
                            "장신구": "accessory",
                            "weapon": "무기",
                            "armor": "방어구",
                            "accessory": "장신구"
                        }
                        
                        alternative_slot = slot_mapping.get(slot)
                        if alternative_slot:
                            equipped_item = getattr(member, f"equipped_{alternative_slot}", None)
                            if equipped_item:
                                slot = alternative_slot  # 올바른 슬롯명으로 변경
                    
                    if not equipped_item:
                        print("❌ 해당 슬롯에 장비가 없습니다.")
                        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                        return
                    
                    # 장비 해제 실행
                    try:
                        unequipped_item = member.unequip_item(slot)
                        
                        if unequipped_item:
                            # 해제 후 검증
                            still_equipped = getattr(member, f"equipped_{slot}", None)
                            
                            if still_equipped is not None:
                                print("❌ 장비 해제 과정에서 오류가 발생했습니다.")
                                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                                return
                            
                            # 장비 효과 재적용
                            if hasattr(member, '_apply_equipment_effects'):
                                member._apply_equipment_effects()
                            
                            # 인벤토리에 추가
                            if hasattr(member, 'inventory'):
                                can_add, reason = member.inventory.can_add_item(unequipped_item)
                                if can_add:
                                    member.inventory.add_item(unequipped_item)
                                    print(f"✅ {unequipped_item.name}을(를) 해제하고 인벤토리에 추가했습니다.")
                                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                                else:
                                    print(f"⚠️ 인벤토리에 공간이 부족합니다: {reason}\n장비를 다시 장착합니다.")
                                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                                    # 다시 장착
                                    member.equip_item(unequipped_item)
                            else:
                                print(f"✅ {unequipped_item.name}을(를) 해제했습니다.")
                                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                        else:
                            print("❌ 장비 해제에 실패했습니다.")
                            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                    except Exception as e:
                        print(f"❌ 장비 해제 중 오류 발생: {str(e)}")
                        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                elif confirm_result == 1:  # 아니오
                    print("장비 해제를 취소했습니다.")
                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                
        except ImportError:
            print("장비 해제 시스템을 불러올 수 없습니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")

    def _use_party_item(self, item_index: int):
        """파티 아이템 사용"""
        try:
            # 모든 파티원의 인벤토리에서 아이템 찾기
            all_items = []
            item_owners = []
            
            for member in self.party_manager.members:
                if hasattr(member, 'inventory') and hasattr(member.inventory, 'items'):
                    for item in member.inventory.items:
                        all_items.append(item)
                        item_owners.append(member)
            
            if item_index >= len(all_items):
                print("❌ 잘못된 아이템 선택입니다.")
                return
            
            selected_item = all_items[item_index]
            item_owner = item_owners[item_index]
            
            # 아이템 타입 확인
            if hasattr(selected_item, 'item_type'):
                from game.items import ItemType
                if selected_item.item_type == ItemType.CONSUMABLE:
                    # 치유 물약 사용
                    if "치유" in selected_item.name:
                        # 파티원 선택
                        member_options = []
                        member_descriptions = []
                        
                        for i, member in enumerate(self.party_manager.members):
                            if member.is_alive:
                                status = f"HP: {member.current_hp}/{member.max_hp}"
                                member_options.append(f"{member.name} ({member.character_class})")
                                member_descriptions.append(status)
                        
                        if member_options:
                            from game.cursor_menu_system import create_simple_menu
                            target_menu = create_simple_menu("치료 대상 선택", member_options, member_descriptions)
                            target_result = target_menu.run()
                            
                            if target_result is not None and target_result >= 0:
                                target_member = [m for m in self.party_manager.members if m.is_alive][target_result]
                                
                                # 치유량 계산
                                heal_amount = 50  # 기본 치유량
                                if "작은" in selected_item.name:
                                    heal_amount = 30
                                elif "큰" in selected_item.name:
                                    heal_amount = 100
                                
                                # 치유 적용
                                old_hp = target_member.current_hp
                                target_member.current_hp = min(target_member.max_hp, target_member.current_hp + heal_amount)
                                actual_heal = target_member.current_hp - old_hp
                                
                                print(f"💚 {target_member.name}이(가) {actual_heal} HP 회복했습니다!")
                                print(f"현재 HP: {target_member.current_hp}/{target_member.max_hp}")
                                
                                # 아이템 제거
                                if hasattr(item_owner.inventory, 'remove_item'):
                                    item_owner.inventory.remove_item(selected_item)
                                elif hasattr(item_owner.inventory, 'items'):
                                    item_owner.inventory.items.remove(selected_item)
                                
                                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                            else:
                                print("❌ 사용이 취소되었습니다.")
                        else:
                            print("❌ 치료할 수 있는 파티원이 없습니다.")
                    else:
                        print(f"❌ {selected_item.name}은(는) 아직 사용할 수 없습니다.")
                else:
                    print(f"❌ {selected_item.name}은(는) 소비 아이템이 아닙니다.")
            else:
                print("❌ 아이템 정보를 확인할 수 없습니다.")
                
        except Exception as e:
            print(f"❌ 아이템 사용 중 오류 발생: {e}")

    # 설정 변경 헬퍼 함수들
    def _change_ui_theme(self):
        """UI 테마 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            themes = ["dark", "light", "classic"]
            options = [f"🎨 {theme.capitalize()}" for theme in themes]
            descriptions = [
                "어두운 테마 (기본)",
                "밝은 테마",
                "클래식 테마"
            ]
            
            menu = CursorMenu("🎨 UI 테마 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(themes):
                game_config.ui_theme = themes[result]
                game_config.save_settings()
                print(f"✅ UI 테마가 '{themes[result]}'로 변경되었습니다.")
                
        except Exception as e:
            print(f"❌ UI 테마 변경 오류: {e}")
    
    def _change_screen_dimension(self, dimension):
        """화면 크기 변경"""
        try:
            from config import game_config
            
            current_value = getattr(game_config, f"screen_{dimension}")
            dim_name = "너비" if dimension == "width" else "높이"
            
            print(f"\n현재 화면 {dim_name}: {current_value}")
            
            try:
                new_value = int(input(f"새 화면 {dim_name} (50-200): ").strip())
                if 50 <= new_value <= 200:
                    setattr(game_config, f"screen_{dimension}", new_value)
                    game_config.save_settings()
                    print(f"✅ 화면 {dim_name}가 {new_value}로 변경되었습니다.")
                else:
                    print("❌ 유효한 범위가 아닙니다 (50-200).")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 화면 크기 변경 오류: {e}")
    
    def _change_volume(self, volume_type):
        """볼륨 변경"""
        try:
            from config import game_config
            
            current_value = getattr(game_config, f"{volume_type}_volume")
            volume_name = {"master": "마스터", "bgm": "BGM", "sfx": "효과음"}[volume_type]
            
            print(f"\n현재 {volume_name} 볼륨: {current_value}%")
            
            try:
                new_value = int(input(f"새 {volume_name} 볼륨 (0-100): ").strip())
                if 0 <= new_value <= 100:
                    setattr(game_config, f"{volume_type}_volume", new_value)
                    game_config.save_settings()
                    print(f"✅ {volume_name} 볼륨이 {new_value}%로 변경되었습니다.")
                else:
                    print("❌ 유효한 범위가 아닙니다 (0-100).")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 볼륨 변경 오류: {e}")
    
    def _change_audio_quality(self):
        """오디오 품질 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            qualities = ["low", "medium", "high"]
            options = [f"🔊 {quality.capitalize()}" for quality in qualities]
            descriptions = [
                "낮은 품질 (성능 우선)",
                "중간 품질 (균형)",
                "높은 품질 (품질 우선)"
            ]
            
            menu = CursorMenu("🎶 오디오 품질 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(qualities):
                game_config.audio_quality = qualities[result]
                game_config.save_settings()
                print(f"✅ 오디오 품질이 '{qualities[result]}'로 변경되었습니다.")
                
        except Exception as e:
            print(f"❌ 오디오 품질 변경 오류: {e}")
    
    def _change_auto_save_interval(self):
        """자동 저장 간격 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            print(f"\n현재 자동 저장 간격: {game_config.AUTO_SAVE_INTERVAL//60}분")
            
            try:
                print("새 자동 저장 간격 (1-30분): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = int(input_str)
                    if 1 <= new_value <= 30:
                        game_config.set_auto_save_interval(new_value * 60)  # 초 단위로 저장
                        print(f"✅ 자동 저장 간격이 {new_value}분으로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (1-30분).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
            except Exception as e:
                print(f"❌ 입력 오류: {e}")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 자동 저장 간격 변경 오류: {e}")
            input("아무 키나 눌러 계속...")
    
    def _change_animation_speed(self):
        """애니메이션 속도 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            speeds = ["slow", "normal", "fast", "instant"]
            options = [f"⚡ {speed.capitalize()}" for speed in speeds]
            descriptions = [
                "느린 속도",
                "보통 속도 (기본)",
                "빠른 속도",
                "즉시 실행"
            ]
            
            menu = CursorMenu("⚡ 애니메이션 속도 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(speeds):
                game_config.animation_speed = speeds[result]
                game_config.save_settings()
                print(f"✅ 애니메이션 속도가 '{speeds[result]}'로 변경되었습니다.")
                
        except Exception as e:
            print(f"❌ 애니메이션 속도 변경 오류: {e}")
    
    def _change_text_size(self):
        """텍스트 크기 변경"""
        try:
            from config import game_config
            
            print(f"\n현재 텍스트 크기: {game_config.text_size}")
            
            try:
                new_value = int(input("새 텍스트 크기 (8-24): ").strip())
                if 8 <= new_value <= 24:
                    game_config.text_size = new_value
                    game_config.save_settings()
                    print(f"✅ 텍스트 크기가 {new_value}로 변경되었습니다.")
                else:
                    print("❌ 유효한 범위가 아닙니다 (8-24).")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 텍스트 크기 변경 오류: {e}")
    
    def _change_text_speed(self):
        """텍스트 속도 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            speeds = ["slow", "normal", "fast", "instant"]
            options = [f"📝 {speed.capitalize()}" for speed in speeds]
            descriptions = [
                "느린 속도",
                "보통 속도 (기본)",
                "빠른 속도",
                "즉시 표시"
            ]
            
            menu = CursorMenu("⏰ 텍스트 속도 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(speeds):
                game_config.text_speed = speeds[result]
                game_config.save_settings()
                print(f"✅ 텍스트 속도가 '{speeds[result]}'로 변경되었습니다.")
                
        except Exception as e:
            print(f"❌ 텍스트 속도 변경 오류: {e}")
    
    def _change_key_repeat_delay(self):
        """키 반복 지연 변경"""
        try:
            from config import game_config
            
            print(f"\n현재 키 반복 지연: {game_config.key_repeat_delay}ms")
            
            try:
                new_value = int(input("새 키 반복 지연 (100-1000ms): ").strip())
                if 100 <= new_value <= 1000:
                    game_config.key_repeat_delay = new_value
                    game_config.save_settings()
                    print(f"✅ 키 반복 지연이 {new_value}ms로 변경되었습니다.")
                else:
                    print("❌ 유효한 범위가 아닙니다 (100-1000ms).")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 키 반복 지연 변경 오류: {e}")
    
    def _change_key_repeat_rate(self):
        """키 반복 속도 변경"""
        try:
            from config import game_config
            
            print(f"\n현재 키 반복 속도: {game_config.key_repeat_rate}ms")
            
            try:
                new_value = int(input("새 키 반복 속도 (10-200ms): ").strip())
                if 10 <= new_value <= 200:
                    game_config.key_repeat_rate = new_value
                    game_config.save_settings()
                    print(f"✅ 키 반복 속도가 {new_value}ms로 변경되었습니다.")
                else:
                    print("❌ 유효한 범위가 아닙니다 (10-200ms).")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 키 반복 속도 변경 오류: {e}")
    
    def _show_key_mappings(self):
        """키 매핑 확인"""
        try:
            from game.color_text import bright_cyan, bright_white, yellow
            
            print(f"\n{bright_cyan('🎹 현재 키 매핑')}")
            print("=" * 60)
            print(f"{bright_white('게임 조작:')}")
            print(f"  {yellow('W/A/S/D')} - 이동")
            print(f"  {yellow('Enter')} - 확인/선택")
            print(f"  {yellow('Q')} - 취소/뒤로가기")
            print(f"  {yellow('I')} - 인벤토리")
            print(f"  {yellow('P')} - 파티 상태")
            print(f"  {yellow('F')} - 필드 활동")
            print(f"  {yellow('H')} - 도움말")
            print(f"  {yellow('B')} - 게임 저장")
            print(f"\n{bright_white('메뉴 조작:')}")
            print(f"  {yellow('W/S')} - 커서 위/아래")
            print(f"  {yellow('Enter')} - 선택")
            print(f"  {yellow('Q')} - 취소")
            print(f"  {yellow('I')} - 정보 보기")
            print(f"  {yellow('숫자키')} - 직접 선택")
            print("=" * 60)
            
            self.keyboard.wait_for_key("아무 키나 눌러 돌아가기...")
            
        except Exception as e:
            print(f"❌ 키 매핑 확인 오류: {e}")
    
    def _change_fps_limit(self):
        """프레임율 제한 변경"""
        try:
            from config import game_config
            
            print(f"\n현재 프레임율 제한: {game_config.fps_limit} (0=무제한)")
            
            try:
                new_value = int(input("새 프레임율 제한 (0-144): ").strip())
                if 0 <= new_value <= 144:
                    game_config.fps_limit = new_value
                    game_config.save_settings()
                    limit_text = "무제한" if new_value == 0 else f"{new_value}fps"
                    print(f"✅ 프레임율 제한이 {limit_text}로 변경되었습니다.")
                else:
                    print("❌ 유효한 범위가 아닙니다 (0-144).")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 프레임율 제한 변경 오류: {e}")
    
    def _change_cache_size(self):
        """캐시 크기 변경"""
        try:
            from config import game_config
            
            print(f"\n현재 캐시 크기: {game_config.cache_size}MB")
            
            try:
                new_value = int(input("새 캐시 크기 (16-512MB): ").strip())
                if 16 <= new_value <= 512:
                    game_config.cache_size = new_value
                    game_config.save_settings()
                    print(f"✅ 캐시 크기가 {new_value}MB로 변경되었습니다.")
                else:
                    print("❌ 유효한 범위가 아닙니다 (16-512MB).")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
        except Exception as e:
            print(f"❌ 캐시 크기 변경 오류: {e}")
    
    def _change_process_priority(self):
        """프로세스 우선순위 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            priorities = ["low", "normal", "high"]
            options = [f"⚡ {priority.capitalize()}" for priority in priorities]
            descriptions = [
                "낮은 우선순위 (시스템 부하 감소)",
                "보통 우선순위 (기본)",
                "높은 우선순위 (성능 향상)"
            ]
            
            menu = CursorMenu("🎮 프로세스 우선순위 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(priorities):
                game_config.process_priority = priorities[result]
                game_config.save_settings()
                print(f"✅ 프로세스 우선순위가 '{priorities[result]}'로 변경되었습니다.")
                
        except Exception as e:
            print(f"❌ 프로세스 우선순위 변경 오류: {e}")
    
    def _show_system_info(self):
        """시스템 정보 확인"""
        try:
            import platform
            import os
            from game.color_text import bright_cyan, bright_white, yellow, green
            
            print(f"\n{bright_cyan('📈 시스템 정보')}")
            print("=" * 60)
            
            # 기본 시스템 정보
            print(f"{bright_white('시스템:')}")
            print(f"  OS: {platform.system()} {platform.release()}")
            print(f"  Python: {platform.python_version()}")
            print(f"  아키텍처: {platform.architecture()[0]}")
            
            # 터미널 정보
            try:
                terminal_size = os.get_terminal_size()
                print(f"\n{bright_white('터미널:')}")
                print(f"  크기: {terminal_size.columns}x{terminal_size.lines}")
            except:
                print(f"\n{bright_white('터미널:')} 크기 정보를 가져올 수 없습니다")
            
            # 게임 관련 정보
            from config import game_config
            print(f"\n{bright_white('게임 설정:')}")
            print(f"  화면 크기: {game_config.screen_width}x{game_config.screen_height}")
            print(f"  전체화면: {'켜짐' if game_config.fullscreen_mode else '꺼짐'}")
            print(f"  개발 모드: {'켜짐' if game_config.dev_mode else '꺼짐'}")
            
            print("=" * 60)
            self.keyboard.wait_for_key("아무 키나 눌러 돌아가기...")
            
        except Exception as e:
            print(f"❌ 시스템 정보 확인 오류: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 돌아가기...")

    def _change_master_volume(self):
        """마스터 볼륨 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            current_vol = int(game_config.MASTER_VOLUME * 100)
            print(f"\n현재 마스터 볼륨: {current_vol}%")
            
            try:
                print("새 마스터 볼륨 (0-100): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = int(input_str)
                    if 0 <= new_value <= 100:
                        game_config.set_master_volume(new_value / 100.0)
                        print(f"✅ 마스터 볼륨이 {new_value}%로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (0-100).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 마스터 볼륨 변경 오류: {e}")
            input("아무 키나 눌러 계속...")
    
    def _change_bgm_volume(self):
        """BGM 볼륨 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            current_vol = int(game_config.BGM_VOLUME * 100)
            print(f"\n현재 BGM 볼륨: {current_vol}%")
            
            try:
                print("새 BGM 볼륨 (0-100): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = int(input_str)
                    if 0 <= new_value <= 100:
                        game_config.set_bgm_volume(new_value / 100.0)
                        print(f"✅ BGM 볼륨이 {new_value}%로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (0-100).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ BGM 볼륨 변경 오류: {e}")
            input("아무 키나 눌러 계속...")
    
    def _change_sfx_volume(self):
        """효과음 볼륨 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            current_vol = int(game_config.SFX_VOLUME * 100)
            print(f"\n현재 효과음 볼륨: {current_vol}%")
            
            try:
                print("새 효과음 볼륨 (0-100): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = int(input_str)
                    if 0 <= new_value <= 100:
                        game_config.set_sfx_volume(new_value / 100.0)
                        print(f"✅ 효과음 볼륨이 {new_value}%로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (0-100).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 효과음 볼륨 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_voice_volume(self):
        """음성 볼륨 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            current_vol = int(game_config.VOICE_VOLUME * 100)
            print(f"\n현재 음성 볼륨: {current_vol}%")
            
            try:
                print("새 음성 볼륨 (0-100): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = int(input_str)
                    if 0 <= new_value <= 100:
                        # config.py에 음성 볼륨 설정 메서드가 없다면 직접 설정
                        game_config.VOICE_VOLUME = new_value / 100.0
                        game_config.save_settings()
                        print(f"✅ 음성 볼륨이 {new_value}%로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (0-100).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 음성 볼륨 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_audio_quality(self):
        """오디오 품질 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            qualities = ["low", "medium", "high"]
            options = [f"🔊 {quality.capitalize()}" for quality in qualities]
            descriptions = [
                "낮은 품질 (성능 우선)",
                "중간 품질 (균형)",
                "높은 품질 (품질 우선)"
            ]
            
            current_index = qualities.index(game_config.AUDIO_QUALITY) if game_config.AUDIO_QUALITY in qualities else 1
            options[current_index] += " ✅"
            
            menu = CursorMenu("🎶 오디오 품질 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(qualities):
                selected_quality = qualities[result]
                game_config.AUDIO_QUALITY = selected_quality
                game_config.save_settings()
                print(f"✅ 오디오 품질이 {selected_quality}로 변경되었습니다.")
                input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 오디오 품질 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _test_audio(self):
        """오디오 테스트"""
        try:
            print("\n🎵 오디오 테스트를 실행합니다...")
            
            # 오디오 매니저가 있다면 테스트 사운드 재생
            if hasattr(self, 'sound_manager') and self.sound_manager:
                print("📢 테스트 효과음 재생...")
                self.sound_manager.play_sfx("menu_confirm")
                
                print("🎼 테스트 BGM 재생...")
                self.sound_manager.play_bgm("peaceful", loop=False)
                
                print("✅ 오디오 테스트 완료!")
            else:
                print("⚠️ 오디오 시스템이 비활성화되어 있습니다.")
                
            input("아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"❌ 오디오 테스트 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_window_size(self):
        """창 크기 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            current_width, current_height = game_config.get_window_size()
            print(f"\n현재 창 크기: {current_width}x{current_height}")
            
            try:
                print("새 창 너비 (800-2560): ", end='', flush=True)
                width_str = keyboard.get_string_input()
                if not width_str:
                    print("❌ 입력이 취소되었습니다.")
                    return
                    
                print("새 창 높이 (600-1440): ", end='', flush=True)
                height_str = keyboard.get_string_input()
                if not height_str:
                    print("❌ 입력이 취소되었습니다.")
                    return
                
                width = int(width_str)
                height = int(height_str)
                
                if 800 <= width <= 2560 and 600 <= height <= 1440:
                    game_config.set_window_size(width, height)
                    print(f"✅ 창 크기가 {width}x{height}로 변경되었습니다.")
                else:
                    print("❌ 유효한 범위가 아닙니다 (너비: 800-2560, 높이: 600-1440).")
                    
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 창 크기 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_ui_scale(self):
        """UI 크기 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            current_scale = int(game_config.UI_SCALE * 100)
            print(f"\n현재 UI 크기: {current_scale}%")
            
            try:
                print("새 UI 크기 (50-200%): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = int(input_str)
                    if 50 <= new_value <= 200:
                        game_config.set_ui_scale(new_value / 100.0)
                        print(f"✅ UI 크기가 {new_value}%로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (50-200%).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ UI 크기 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_fps_limit(self):
        """FPS 제한 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            print(f"\n현재 FPS 제한: {game_config.FPS_LIMIT}")
            
            try:
                print("새 FPS 제한 (30-144): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = int(input_str)
                    if 30 <= new_value <= 144:
                        game_config.FPS_LIMIT = new_value
                        game_config.save_settings()
                        print(f"✅ FPS 제한이 {new_value}로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (30-144).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ FPS 제한 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_colorblind_mode(self):
        """색맹 지원 모드 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            modes = ["none", "protanopia", "deuteranopia", "tritanopia"]
            mode_names = ["없음", "적색맹", "녹색맹", "청색맹"]
            
            options = []
            descriptions = []
            current_index = 0
            
            for i, (mode, name) in enumerate(zip(modes, mode_names)):
                is_current = " ✅" if mode == game_config.COLOR_BLIND_MODE else ""
                options.append(f"{name}{is_current}")
                descriptions.append(f"{name} 지원 모드")
                if mode == game_config.COLOR_BLIND_MODE:
                    current_index = i
            
            menu = CursorMenu("🎯 색맹 지원 모드 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(modes):
                selected_mode = modes[result]
                game_config.COLOR_BLIND_MODE = selected_mode
                game_config.save_settings()
                print(f"✅ 색맹 지원 모드가 {mode_names[result]}로 변경되었습니다.")
                input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 색맹 지원 모드 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_key_repeat_delay(self):
        """키 반복 지연 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            current_delay = int(game_config.KEYBOARD_REPEAT_DELAY * 1000)
            print(f"\n현재 키 반복 지연: {current_delay}ms")
            
            try:
                print("새 키 반복 지연 (100-1000ms): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = int(input_str)
                    if 100 <= new_value <= 1000:
                        game_config.KEYBOARD_REPEAT_DELAY = new_value / 1000.0
                        game_config.save_settings()
                        print(f"✅ 키 반복 지연이 {new_value}ms로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (100-1000ms).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 키 반복 지연 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_mouse_sensitivity(self):
        """마우스 감도 변경"""
        try:
            from config import game_config
            from game.input_utils import KeyboardInput
            
            keyboard = KeyboardInput()
            print(f"\n현재 마우스 감도: {game_config.MOUSE_SENSITIVITY}")
            
            try:
                print("새 마우스 감도 (0.1-3.0): ", end='', flush=True)
                input_str = keyboard.get_string_input()
                if input_str:
                    new_value = float(input_str)
                    if 0.1 <= new_value <= 3.0:
                        game_config.MOUSE_SENSITIVITY = new_value
                        game_config.save_settings()
                        print(f"✅ 마우스 감도가 {new_value}로 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다 (0.1-3.0).")
                else:
                    print("❌ 입력이 취소되었습니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                
            input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 마우스 감도 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_texture_quality(self):
        """텍스처 품질 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            qualities = ["low", "medium", "high", "ultra"]
            quality_names = ["낮음", "보통", "높음", "최고"]
            
            options = []
            descriptions = []
            current_index = 0
            
            for i, (quality, name) in enumerate(zip(qualities, quality_names)):
                is_current = " ✅" if quality == game_config.TEXTURE_QUALITY else ""
                options.append(f"{name}{is_current}")
                descriptions.append(f"{name} 품질로 설정")
                if quality == game_config.TEXTURE_QUALITY:
                    current_index = i
            
            menu = CursorMenu("🎨 텍스처 품질 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(qualities):
                selected_quality = qualities[result]
                game_config.TEXTURE_QUALITY = selected_quality
                game_config.save_settings()
                print(f"✅ 텍스처 품질이 {quality_names[result]}로 변경되었습니다.")
                input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 텍스처 품질 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _change_shadow_quality(self):
        """그림자 품질 변경"""
        try:
            from game.cursor_menu_system import CursorMenu
            from config import game_config
            
            qualities = ["off", "low", "medium", "high"]
            quality_names = ["꺼짐", "낮음", "보통", "높음"]
            
            options = []
            descriptions = []
            current_index = 0
            
            for i, (quality, name) in enumerate(zip(qualities, quality_names)):
                is_current = " ✅" if quality == game_config.SHADOW_QUALITY else ""
                options.append(f"{name}{is_current}")
                descriptions.append(f"{name} 품질로 설정")
                if quality == game_config.SHADOW_QUALITY:
                    current_index = i
            
            menu = CursorMenu("🌑 그림자 품질 선택", options, descriptions)
            result = menu.run()
            
            if result is not None and 0 <= result < len(qualities):
                selected_quality = qualities[result]
                game_config.SHADOW_QUALITY = selected_quality
                game_config.save_settings()
                print(f"✅ 그림자 품질이 {quality_names[result]}로 변경되었습니다.")
                input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 그림자 품질 변경 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _show_key_mappings(self):
        """키 매핑 정보 표시"""
        try:
            from game.color_text import bright_cyan, bright_white, yellow, green, cyan
            
            print(f"\n{bright_cyan('🎹 현재 키 매핑')}")
            print("="*60)
            
            print(f"{bright_white('기본 이동:')}")
            print("   W/A/S/D 또는 화살표키: 이동")
            
            print(f"\n{bright_white('메뉴 및 상호작용:')}")
            print("   Enter: 확인/선택")
            print("   I: 인벤토리")
            print("   P: 파티 상태")
            print("   F: 필드 활동 (스킬, 요리, 상인)")
            print("   H: 도움말")
            
            print(f"\n{bright_white('시스템:')}")
            print("   B: 게임 저장")
            print("   Q: 게임 종료")
            
            print(f"\n{bright_white('메뉴 내 조작:')}")
            print("   W/S: 커서 위/아래 이동")
            print("   Enter: 선택")
            print("   Q: 취소/뒤로가기")
            print("   숫자키: 직접 선택")
            
            print("="*60)
            input("아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"❌ 키 매핑 표시 오류: {e}")
            input("아무 키나 눌러 계속...")

    def _show_system_info(self):
        """시스템 정보 표시"""
        try:
            import platform
            import os
            from game.color_text import bright_cyan, bright_white, yellow, green
            
            print(f"\n{bright_cyan('📈 시스템 정보')}")
            print("="*60)
            
            # 기본 시스템 정보
            print(f"{bright_white('운영체제:')} {platform.system()} {platform.release()}")
            print(f"{bright_white('프로세서:')} {platform.processor()}")
            print(f"{bright_white('Python 버전:')} {platform.python_version()}")
            
            # 게임 정보
            print(f"\n{bright_white('게임 정보:')}")
            print(f"   게임 버전: Dawn of Stellar v1.0")
            print(f"   설정 파일: config.py")
            print(f"   세이브 경로: saves/")
            
            print("="*60)
            input("아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"❌ 시스템 정보 확인 오류: {e}")
            input("아무 키나 눌러 계속...")


def main():
    """메인 함수"""
    try:
        # 게임 인스턴스 생성
        game = DawnOfStellarGame()
        
        # 메인 루프 실행
        game.main_loop()
        
    except KeyboardInterrupt:
        print(f"\n{bright_yellow('게임이 중단되었습니다.')}")
    except Exception as e:
        print(f"\n{bright_red(f'오류가 발생했습니다: {e}')}")
    finally:
        print(f"{bright_cyan('게임을 종료합니다.')}")


if __name__ == "__main__":
    main()
