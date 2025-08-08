#!/usr/bin/env python3
"""
Dawn Of Stellar - 메인 파일  
별빛의 여명 - 28명의 개성있는 캐릭터와 ATB 전투 시스템을 가진 전술 RPG
🎮 완전 통합 시스템 버전 - 165+ 상태효과, 100+ 적, FFVII BGM/SFX, 튜토리얼 🎮
"""

import sys
import os
import codecs
import signal
import atexit
from enum import Enum
from typing import List, Tuple
import time
import random
# 스토리 시스템 import
try:
    from story_system import show_opening_story, show_chapter_intro, show_character_intro
    STORY_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 스토리 시스템을 불러올 수 없습니다: {e}")
    STORY_SYSTEM_AVAILABLE = False
    def show_opening_story(): pass
    def show_chapter_intro(chapter): pass  
    def show_character_intro(name, job): pass

# 자동 저장 시스템 import
try:
    from game.auto_save_system import configure_auto_save_system, on_floor_change, on_level_up, on_boss_defeat, on_achievement_unlock, on_party_wipe
    AUTO_SAVE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 자동 저장 시스템을 불러올 수 없습니다: {e}")
    AUTO_SAVE_AVAILABLE = False

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
    from game.input_utils import UnifiedInputManager, get_single_key_input
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
    from game.ffvii_sound_system import FFVIISoundSystem
    from game.audio_system import AudioManager, BGMType, SFXType, get_audio_manager
    # AudioManager만 사용 (FFVII BGM 시스템 비활성화)
    def get_audio_system(debug_mode: bool = False):
        return get_audio_manager(debug_mode=debug_mode)
    def get_unified_audio_system(debug_mode: bool = False):
        return get_audio_manager(debug_mode=debug_mode)
except ImportError:
    try:
        from game.audio_system import AudioManager, BGMType, SFXType, get_audio_manager
        # 폴백: 기존 오디오 시스템 (debug_mode 파라미터 전달)
        def get_audio_system(debug_mode: bool = False):
            return get_audio_manager(debug_mode=debug_mode)
        def get_unified_audio_system(debug_mode: bool = False):
            return get_audio_manager(debug_mode=debug_mode)
    except ImportError:
        print("모듈 임포트 오류: 오디오 시스템을 찾을 수 없습니다.")
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

# 동적 적 스케일링 시스템
try:
    from game.dynamic_enemy_scaling import get_dynamic_scaler, scale_enemy_for_party, update_difficulty_for_party
    DYNAMIC_SCALING_AVAILABLE = True
    # print("✅ 동적 적 스케일링 시스템 로드 성공")  # 숨김
except ImportError:
    print("모듈 임포트 오류: 동적 스케일링 시스템을 찾을 수 없습니다.")
    def get_dynamic_scaler():
        return None
    def scale_enemy_for_party(enemy, party, floor):
        return enemy
    def update_difficulty_for_party(party):
        pass
    DYNAMIC_SCALING_AVAILABLE = False
    
# 선택적 시스템들 (없어도 게임 실행 가능)
try:
    from game.save_system import get_save_manager, get_auto_save_manager, GameStateSerializer
    from game.save_system import show_save_menu as save_system_show_save_menu
    from game.save_system import show_load_menu as save_system_show_load_menu
    SAVE_SYSTEM_AVAILABLE = True
    # print("✅ 저장 시스템 모듈 로드 성공")  # 숨김
except ImportError as e:
    print(f"⚠️ 저장 시스템 모듈 로드 실패: {e}")

# 🎭 Easy Character Creator - 기본 캐릭터 생성 시스템
try:
    from game.easy_character_creator import get_easy_character_creator
    EASY_CREATOR_AVAILABLE = True
    # print("✅ Easy Character Creator 로드 성공 - 기본 캐릭터 생성 시스템 준비완료")  # 숨김
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
            """탐험된 타일 정보를 직렬화 (explored, visible 상태 포함)"""
            try:
                explored_data = []
                if hasattr(world, 'tiles') and world.tiles:
                    for y, row in enumerate(world.tiles):
                        for x, tile in enumerate(row):
                            if hasattr(tile, 'explored') and tile.explored:
                                explored_data.append({
                                    'x': x,
                                    'y': y,
                                    'explored': tile.explored,
                                    'visible': getattr(tile, 'visible', False)
                                })
                return explored_data
            except Exception as e:
                print(f"⚠️ 탐험 타일 직렬화 오류: {e}")
                return []
    
try:
    from game.ui_system import get_ui_manager, UIManager
    UI_SYSTEM_AVAILABLE = True
except ImportError:
    print("⚠️ UI 시스템을 불러올 수 없습니다. (curses 모듈 없음)")
    UI_SYSTEM_AVAILABLE = False
    def get_ui_manager():
        return None

try:
    # IntegratedGameManager 활성화
    from game.integrated_game_manager import IntegratedGameManager
    print("✅ IntegratedGameManager 로드 성공!")  # 디버그 출력
except ImportError as e:
    print(f"⚠️ 모듈 임포트 오류: IntegratedGameManager를 찾을 수 없습니다. ({e})")
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


# 폰트 매니저 심볼 (옵셔널): 사용처에서 조용히 동작하도록 폴백 제공
try:
    from game.font_manager import get_font_manager, apply_game_font
    FONT_MANAGER_AVAILABLE = True
except Exception:
    try:
        # ui_system에서만 상태 플래그를 가져올 수 있는 경우
        from game.ui_system import FONT_MANAGER_AVAILABLE as _FMA
        FONT_MANAGER_AVAILABLE = bool(_FMA)
    except Exception:
        FONT_MANAGER_AVAILABLE = False

    # 사용 시 실패하지 않도록 더미 함수 제공
    def get_font_manager():
        return None
    def apply_game_font():
        return None


class DawnOfStellarGame:
    """Dawn Of Stellar 메인 게임 클래스 - 완전 통합 시스템"""
    
    def __init__(self):
        # 게임 메시지 버퍼 시스템 초기화
        self.message_buffer = []
        self.max_messages = 5  # 최대 메시지 개수
        
        # 폰트 시스템 초기화 (조용히 실행)
        if FONT_MANAGER_AVAILABLE:
            try:
                apply_game_font()  # 메시지 없이 폰트만 적용
            except Exception:
                pass  # 오류도 조용히 처리
        
        # 설정 시스템 초기화
        try:
            from config import GameConfig
            self.config = GameConfig()
        except ImportError:
            # 폴백 설정
            class FallbackConfig:
                def __init__(self):
                    self.current_difficulty = "보통"
                def set_difficulty(self, difficulty):
                    self.current_difficulty = difficulty
            self.config = FallbackConfig()
        
        # 창 최대화 모드 적용 (조용히 실행)
        try:
            from config import game_config
            if game_config.FULLSCREEN_MODE:
                game_config.apply_terminal_fullscreen()  # 메시지 없이 적용
        except Exception:
            pass  # 오류도 조용히 처리
        
        # 🎵 오디오 시스템 초기화 (최우선)
        try:
            from game.audio_system import get_audio_manager
            import config as game_config
            debug_mode = getattr(game_config, 'DEBUG_MODE', False)
            self.audio_system = get_audio_manager(debug_mode=debug_mode)
            self.sound_manager = self.audio_system
        except Exception as e:
            self.audio_system = None
            self.sound_manager = None
        
        # 기존 시스템들
        self.display = GameDisplay()
        self.party_manager = PartyManager()
        
        # 파티 변경 시 난이도 자동 업데이트 설정
        if hasattr(self, 'dynamic_scaler') and self.dynamic_scaler:
            original_add_member = self.party_manager.add_member
            original_remove_member = self.party_manager.remove_member
            
            def enhanced_add_member(character):
                result = original_add_member(character)
                self._update_enemy_difficulty()
                return result
            
            def enhanced_remove_member(character):
                result = original_remove_member(character)
                self._update_enemy_difficulty()
                return result
            
            self.party_manager.add_member = enhanced_add_member
            self.party_manager.remove_member = enhanced_remove_member
        
        # 자동 저장 시스템 초기화
        if AUTO_SAVE_AVAILABLE:
            try:
                self.auto_save_manager = configure_auto_save_system(self)
            except Exception as e:
                print(f"⚠️ 자동 저장 시스템 초기화 실패: {e}")
                self.auto_save_manager = None
        else:
            self.auto_save_manager = None
        
        self.merchant_manager = MerchantManager()
        self.permanent_progression = PermanentProgressionSystem()
        self.world = GameWorld(party_manager=self.party_manager)
        
        # 오디오 시스템을 월드에 연결
        if hasattr(self, 'audio_system') and self.audio_system:
            self.world.audio_system = self.audio_system
        
        # 게임 객체를 월드에 연결 (메시지 시스템용)
        self.world.game = self
        
        self.party_passive_effects = []  # 파티 패시브 효과 저장
        self.current_floor = 1  # 현재 층 정보 추가
        
        # 필드 자동 회복 시스템을 위한 걸음 수 추적
        self.step_count = 0
        
        # 🌟 메타 진행 시스템 추가
        self.meta_progression = get_meta_progression()
        
        # 📚 스토리 시스템 초기화
        try:
            from story_system import StorySystem
            self.story_system = StorySystem()
        except Exception as e:
            print(f"⚠️ 스토리 시스템 초기화 실패: {e}")
            self.story_system = None
        
        # 🎵 정상 오디오 모드 플래그 초기화 (BGM 차단 해제)
        self._force_glitch_mode = False
        
        # 🍽️ 요리 시스템 연결
        try:
            from game.cooking_system import cooking_system
            from game.gathering_limiter import set_party_manager_for_gathering
            cooking_system.set_party_manager(self.party_manager)
            set_party_manager_for_gathering(self.party_manager)
        except ImportError:
            pass
        
        # 🎮 통합 게임 매니저 초기화 - 안전한 초기화
        try:
            self.game_manager = IntegratedGameManager() if IntegratedGameManager else None
        except Exception as e:
            print(f"⚠️ 통합 게임 매니저 초기화 실패: {e}")
            self.game_manager = None
        
        # 🎯 랜덤 조우 및 필드 스킬 시스템 - 안전한 초기화
        try:
            self.encounter_manager = get_encounter_manager()
        except Exception as e:
            print(f"⚠️ 조우 매니저 초기화 실패: {e}")
            self.encounter_manager = None
            
        try:
            self.field_skill_manager = get_field_skill_manager()
        except Exception as e:
            print(f"⚠️ 필드 스킬 매니저 초기화 실패: {e}")
            self.field_skill_manager = None
        
        # 🔥 강화된 시스템들
        try:
            from game.enhanced_encounter_system import get_enhanced_encounter_manager
            from game.trait_integration_system import get_trait_processor
            from game.relative_balance_system import get_balance_system
            
            self.enhanced_encounter_manager = get_enhanced_encounter_manager()
            self.trait_processor = get_trait_processor()
            self.balance_system = get_balance_system()
            # print("🔥 강화된 조우, 특성, 밸런스 시스템 활성화!")  # 숨김
        except ImportError as e:
            # print(f"⚠️ 강화 시스템 일부 로드 실패: {e}")  # 숨김
            self.enhanced_encounter_manager = None
            self.trait_processor = None
            self.balance_system = None
        
        # 🚀 신규 통합 시스템들 - 안전한 초기화
        try:
            self.skill_manager = get_skill_manager() if callable(get_skill_manager) else None
        except Exception as e:
            print(f"⚠️ 스킬 매니저 초기화 실패: {e}")
            self.skill_manager = None
        
        # 각종 매니저들 안전한 초기화
        try:
            self.enemy_manager = get_enemy_manager() if callable(get_enemy_manager) else None
        except Exception as e:
            print(f"⚠️ 적 매니저 초기화 실패: {e}")
            self.enemy_manager = None
            
        try:
            self.save_manager = get_save_manager() if callable(get_save_manager) else None
        except Exception as e:
            print(f"⚠️ 저장 매니저 초기화 실패: {e}")
            self.save_manager = None
            
        try:
            self.auto_save_manager = get_auto_save_manager() if callable(get_auto_save_manager) else None
        except Exception as e:
            print(f"⚠️ 자동 저장 매니저 초기화 실패: {e}")
            self.auto_save_manager = None
            
        try:
            self.ui_manager = get_ui_manager() if callable(get_ui_manager) else None
        except Exception as e:
            print(f"⚠️ UI 매니저 초기화 실패: {e}")
            self.ui_manager = None
            
        try:
            self.tutorial_manager = get_tutorial_manager() if callable(get_tutorial_manager) else None
        except Exception as e:
            print(f"⚠️ 튜토리얼 매니저 초기화 실패: {e}")
            self.tutorial_manager = None
        
        # 🎯 동적 적 스케일링 시스템 초기화
        try:
            self.dynamic_scaler = get_dynamic_scaler() if callable(get_dynamic_scaler) else None
            if self.dynamic_scaler:
                # print("✅ 동적 적 스케일링 시스템 활성화 - 파티 전력에 맞춰 적이 강화됩니다!")  # 숨김
                pass
        except Exception as e:
            print(f"⚠️ 동적 스케일링 초기화 실패: {e}")
            self.dynamic_scaler = None
        
        # 🎯 적응형 밸런스 시스템 초기화
        try:
            from game.adaptive_balance import adaptive_balance
            self.adaptive_balance = adaptive_balance
            self.adaptive_balance.start_session(debug_mode=False)  # 조용히 실행
        except ImportError:
            self.adaptive_balance = None
        
        # 🔥 원소 및 상태 시스템 - 안전한 초기화
        try:
            self.element_system = get_element_system() if callable(get_element_system) else None
        except Exception as e:
            print(f"⚠️ 원소 시스템 초기화 실패: {e}")
            self.element_system = None
            
        try:
            self.item_database = get_item_database() if callable(get_item_database) else None
        except Exception as e:
            print(f"⚠️ 아이템 데이터베이스 초기화 실패: {e}")
            self.item_database = None
        self.running = True
        self.character_db = CharacterDatabase()
        
        # 키보드 입력 초기화 (게임패드 지원)
        self.keyboard = UnifiedInputManager()
        
        # 게임패드 상태 표시
        self._show_gamepad_status()
        
        # 게임 통계
        self.score = 0
        self.enemies_defeated = 0
        self.items_collected = 0
        self.floors_cleared = 0
        self.gold = 0  # 게임 클래스 골드 초기화
        
        # 인카운터 시스템 (확률 대폭 감소)
        self.steps_since_last_encounter = 0
        self.base_encounter_rate = 0.001  # 기본 0.1%로 대폭 감소 (0.005 → 0.001)
        
        # print(f"{bright_cyan('🌟 Dawn Of Stellar - 완전 통합 시스템 버전 시작! 🌟')}")
        # print(f"{bright_yellow('✨ 28명 캐릭터, 165+ 상태효과, 100+ 적, 통합 사운드 시스템, 튜토리얼 시스템 활성화! ✨')}")
        
        # 🎵 메인 메뉴 BGM은 메인 메뉴에서만 재생하도록 함
        
        self.encounter_rate_increase = 0.002  # 걸음당 0.2% 증가로 감소 (0.01 → 0.002)
    
    def __del__(self):
        """소멸자 - 오디오 시스템 강제 정리"""
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.cleanup()
            import pygame
            if pygame.get_init():
                pygame.mixer.quit()
                pygame.quit()
        except:
            pass
    
    def cleanup(self):
        """수동 정리 메서드"""
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.cleanup()
            import pygame
            if pygame.get_init():
                pygame.mixer.quit()
                pygame.quit()
        except:
            pass
    
    @staticmethod
    def restore_explored_tiles(world, tiles_data):
        """탐험된 타일 정보를 복원 (explored, visible 상태 포함)"""
        try:
            if not tiles_data or not hasattr(world, 'tiles') or not world.tiles:
                return
            
            restored_count = 0
            for tile_info in tiles_data:
                x, y = tile_info.get('x'), tile_info.get('y')
                if (x is not None and y is not None and 
                    0 <= y < len(world.tiles) and 0 <= x < len(world.tiles[y])):
                    tile = world.tiles[y][x]
                    if hasattr(tile, 'explored'):
                        tile.explored = tile_info.get('explored', False)
                        tile.visible = tile_info.get('visible', False)
                        restored_count += 1
            
            print(f"🗺️ 탐험된 타일 복원: {restored_count}개")
        except Exception as e:
            print(f"⚠️ 탐험 타일 복원 오류: {e}")
    
    def safe_play_bgm(self, bgm_name_or_type, **kwargs):
        """안전한 BGM 재생 헬퍼 - 글리치 모드에서는 BGM 차단"""
        # 강제 글리치 모드 체크
        if hasattr(self, '_force_glitch_mode') and self._force_glitch_mode:
            print("🔇 [BGM BLOCKED] Force glitch mode active - BGM playback denied")
            return
        
        # 일반 글리치 모드 체크
        try:
            if hasattr(self, 'story_system') and self.story_system:
                if hasattr(self.story_system, 'is_glitch_mode') and self.story_system.is_glitch_mode():
                    print("🔇 [BGM BLOCKED] Glitch mode active - BGM playback denied")
                    return
        except:
            pass
        
        if self.sound_manager:
            try:
                self.sound_manager.play_bgm(bgm_name_or_type, **kwargs)
            except:
                pass
    
    def safe_audio_system_bgm(self, bgm_type, **kwargs):
        """안전한 오디오 시스템 BGM 재생 - 글리치 모드에서는 차단"""
        # 강제 글리치 모드 체크
        if hasattr(self, '_force_glitch_mode') and self._force_glitch_mode:
            print("🔇 [AUDIO BLOCKED] Force glitch mode active - Audio system BGM denied")
            return
        
        # 일반 글리치 모드 체크
        try:
            if hasattr(self, 'story_system') and self.story_system:
                if hasattr(self.story_system, 'is_glitch_mode') and self.story_system.is_glitch_mode():
                    print("🔇 [AUDIO BLOCKED] Glitch mode active - Audio system BGM denied")
                    return
        except:
            pass
        
        if hasattr(self, 'audio_system') and self.audio_system:
            try:
                # 강제 글리치 모드 다시 체크
                if hasattr(self, '_force_glitch_mode') and self._force_glitch_mode:
                    print("🔇 [AUDIO BLOCKED] Force glitch mode - Audio system BGM denied")
                    return
                self.audio_system.play_bgm(bgm_type, **kwargs)
            except:
                pass
    
    def add_game_message(self, message: str):
        """게임 메시지를 버퍼에 추가 (맵 아래쪽에 표시됨)"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.message_buffer.append(formatted_message)
        
        # 최대 메시지 개수 초과 시 오래된 메시지 제거
        if len(self.message_buffer) > self.max_messages:
            self.message_buffer.pop(0)
    
    def get_recent_messages(self) -> list:
        """최근 메시지들 반환"""
        return self.message_buffer.copy()
    
    def clear_messages(self):
        """메시지 버퍼 비우기"""
        self.message_buffer.clear()
    
    def show_messages_below_map(self):
        """맵 아래쪽에 메시지들 표시"""
        if not self.message_buffer:
            return
        
        print("\n" + "="*60)
        print("📢 게임 상황:")
        for message in self.message_buffer:
            print(f"  {message}")
        print("="*60)
    
    def safe_play_sfx(self, sfx_name_or_type, **kwargs):
        """안전한 SFX 재생 헬퍼"""
        if self.sound_manager:
            try:
                self.sound_manager.play_sfx(sfx_name_or_type, **kwargs)
            except:
                pass
    
    def safe_set_floor_bgm(self, floor: int):
        """안전한 층별 BGM 설정 헬퍼"""
        if self.sound_manager:
            try:
                self.sound_manager.set_floor_bgm(floor)
            except:
                pass
    
    def nuclear_silence_mode(self):
        """🔇 핵폭탄급 완전 조용 모드 - 모든 오디오 박멸"""
        print("💥 [NUCLEAR SILENCE] 모든 오디오 시스템 완전 차단!")
        
        # 강제 글리치 모드 플래그 설정
        self._force_glitch_mode = True
        
        # 모든 오디오 시스템 정지
        try:
            # Sound Manager 정지
            if hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.stop_bgm()
                self.sound_manager.stop_all()
                print("🔇 Sound Manager 정지 완료")
            
            # Audio System 정지
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.stop_bgm()
                self.audio_system.stop_all()
                print("🔇 Audio System 정지 완료")
            
            # Pygame Mixer 강제 정지
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.stop()
                pygame.mixer.music.stop()
                print("🔇 Pygame Mixer 강제 정지 완료")
                
        except Exception as e:
            print(f"⚠️ 오디오 정지 중 오류: {e}")
        
        print("[COMPLETE SILENCE] 모든 소리가 제거되었습니다")
    
    def restore_normal_audio_mode(self):
        """🎵 정상 오디오 모드 복원 - BGM 차단 해제"""
        print("🎵 [AUDIO RESTORE] 정상 오디오 모드 복원 중...")
        
        # 강제 글리치 모드 플래그 해제
        self._force_glitch_mode = False
        
        # 오디오 시스템 재시작
        try:
            # Pygame Mixer 재시작
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                print("🎵 Pygame Mixer 재시작 완료")
            
            # Sound Manager 재시작
            if hasattr(self, 'sound_manager') and self.sound_manager:
                # 메인 메뉴 BGM 재생
                from game.audio_system import BGMType
                self.sound_manager.play_bgm(BGMType.MAIN_MENU)
                print("🎵 Sound Manager BGM 복원 완료")
            
            # Audio System 재시작
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_bgm(BGMType.MAIN_MENU)
                print("🎵 Audio System BGM 복원 완료")
                
        except Exception as e:
            print(f"⚠️ 오디오 복원 중 오류: {e}")
        
        print("✅ [AUDIO RESTORED] 정상 오디오 모드가 복원되었습니다")
    
    def add_gold(self, amount: int):
        """골드 시스템 통일 - 두 골드 시스템에 모두 추가"""
        if amount > 0:
            self.gold += amount
            self.party_manager.add_gold(amount)
    
    def get_total_gold(self) -> int:
        """현재 총 골드 반환 - 파티 매니저 골드를 우선"""
        return self.party_manager.get_total_gold()
        
    def initialize_game(self):
        """게임 초기화"""
        self.display.show_title()
        
        # 🎵 캐릭터 선택은 조용히 진행
        
        # 캐릭터 선택이 취소되면 게임 초기화 중단
        if not self.show_character_selection():
            print(f"\n{bright_red('게임 초기화가 취소되었습니다.')}")
            print(f"{bright_cyan('프로그램을 종료합니다...')}")
            return False
            
        self.apply_permanent_bonuses()  # 영구 성장 보너스 적용
        
        # 재기의 기회 사용 횟수 초기화
        self.second_chance_uses = 0
        
        self.world.generate_level()
        
        # 골드 시스템 동기화 (시작 골드 50G 지급)
        initial_gold = 50
        self.gold = initial_gold
        if hasattr(self.party_manager, 'party_gold'):
            self.party_manager.party_gold = initial_gold
        else:
            self.party_manager.add_gold(initial_gold)
        
        # print("✅ 게임 초기화 완료!")  # 메시지 제거
        
        # 오디오 시스템 초기화 (디버그 모드 확인)
        try:
            from game.audio_system import get_audio_manager
            import config as game_config
            debug_mode = getattr(game_config, 'DEBUG_MODE', False)
            self.audio_system = get_audio_manager(debug_mode=debug_mode)
            self.sound_manager = self.audio_system
        except Exception as e:
            print(f"⚠️ 오디오 시스템 초기화 실패: {e}")
            self.audio_system = None
            self.sound_manager = None
        
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
            
            # 골드 보너스 (개별 캐릭터 골드에는 적용하지 않음 또는 파티 공용 처리)
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
        
        # 🎵 캐릭터 생성 전용 BGM 재생 (메인 메뉴 BGM 교체)
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                import pygame
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                # 캐릭터 생성 BGM 재생
                self.safe_play_bgm("character_creation", loop=True)
        except Exception:
            pass
        
        try:
            from game.easy_character_creator import get_easy_character_creator
            
            # print(f"{bright_green('✨ 쉬운 캐릭터 생성 시스템을 시작합니다...')}")  # 메시지 제거
            creator = get_easy_character_creator()
            party = creator.show_character_creation_menu()

            if party:
                # 생성된 파티를 게임에 적용
                self.characters = party
                self.current_character_index = 0
                
                # party_manager에도 파티 설정 (중요!)
                if hasattr(self, 'party_manager') and self.party_manager:
                    self.party_manager.members = party
                
                # print(f"\n{bright_green('✅ 파티가 성공적으로 준비되었습니다!')}")  # 메시지 제거
                # print(f"{bright_cyan('🛡️ 파티원:')} {', '.join([c.name for c in party])}")  # 메시지 제거
                
                # 시공교란 스토리와 캐릭터 소개 표시
                if STORY_SYSTEM_AVAILABLE:
                    try:
                        print(f"\n{bright_yellow('📖 캐릭터들의 배경 이야기를 확인하세요...')}")
                        input(f"{bright_green('[Enter 키를 눌러 계속]')}")
                        
                        # 캐릭터 소개 표시
                        for character in party:
                            show_character_intro(character.name, character.character_class)
                            input(f"{bright_green('[Enter 키를 눌러 다음 캐릭터]')}")
                    except Exception as e:
                        print(f"⚠️ 캐릭터 소개 표시 중 오류: {e}")
                        pass
                
                # print(f"{bright_yellow('⚔️ 이제 모험을 시작할 수 있습니다!')}")  # 메시지 제거
                return True  # 성공적으로 파티 생성됨
            else:
                # 취소된 경우 메인 메뉴로 돌아가기
                # print(f"\n{bright_yellow('❌ 캐릭터 생성이 취소되었습니다.')}")  # 메시지 제거
                # print(f"{bright_cyan('🏠 메인 메뉴로 돌아갑니다...')}")  # 메시지 제거
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
    
    def select_ai_game_mode(self):
        """AI 게임모드 선택 - 커서 메뉴 방식"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            # 메뉴 옵션 정의
            options = [
                "🎮 전체 수동 조작 (모든 캐릭터 직접 조작)",
                "🤖 AI 파트너 모드 (1명만 조작, 나머지는 AI)",
                "🎯 듀얼 컨트롤 (2명 조작, 나머지는 AI)",
                "🔄 혼합 모드 (상황에 따라 변경)"
            ]
            
            # 각 옵션별 설명
            descriptions = [
                "클래식한 JRPG 방식. 모든 전투 행동을 직접 선택합니다.",
                "⭐ 추천! 한 명만 조작하고 AI가 나머지를 담당. 빠르고 전략적.",
                "2명을 직접 조작하고 2명은 AI가 담당. 밸런스가 좋습니다.",
                "상황에 따라 조작 방식을 변경할 수 있는 유연한 모드."
            ]
            
            # 추가 정보 텍스트
            extra_content = f"""{bright_cyan('💡 AI 모드의 장점:')}
   ⚡ 전투 속도 향상 - 턴이 빨라집니다
   🧠 스마트한 AI 동료 지원 - 직업별 최적화
   🎯 전략적 협동 공격 - AI와 연계 가능
   📦 아이템 자동 관리 - 최적 장비 추천
   💬 개성있는 대화 - 9가지 성격 시스템
   🤝 상황별 제안 - AI가 전략 조언 제공

{bright_yellow('🎯 처음이시라면 "AI 파트너 모드"를 추천합니다!')}"""
            
            # 커서 메뉴 생성
            menu = CursorMenu(
                title=f"{bright_white('🤖 게임 조작 모드 선택 🤖')}",
                options=options,
                descriptions=descriptions,
                extra_content=extra_content,
                audio_manager=self.audio_manager if hasattr(self, 'audio_manager') else None,
                keyboard=self.keyboard if hasattr(self, 'keyboard') else None
            )
            
            choice = menu.run()
            
            if choice == -1 or choice is None:  # ESC 키로 취소
                print(f"\n{bright_yellow('기본 모드(전체 수동 조작)로 진행합니다.')}")
                self.ai_game_mode_enabled = False
                return
            
            # 선택된 모드 처리
            if choice == 0:  # 전체 수동 조작
                self.ai_game_mode_enabled = False
                print(f"\n✅ {bright_green('전체 수동 조작 모드')}가 선택되었습니다.")
                print("🎮 모든 캐릭터를 직접 조작합니다.")
                
            elif choice in [1, 2, 3]:  # AI 모드들
                self.ai_game_mode_enabled = True
                
                # 조작할 캐릭터 수 결정
                controlled_count = 1 if choice == 1 else 2 if choice == 2 else 1
                
                try:
                    from game.ai_game_mode import initialize_ai_game_mode
                    initialize_ai_game_mode(self.party_manager.members, controlled_count)
                except Exception as ai_error:
                    print(f"⚠️ AI 모드 초기화 오류: {ai_error}")
                    print("기본 모드로 계속 진행합니다.")
                    self.ai_game_mode_enabled = False
                
                mode_names = [
                    "🎮 전체 수동 조작",
                    "🤖 AI 파트너 모드",
                    "🎯 듀얼 컨트롤 모드", 
                    "🔄 혼합 모드"
                ]
                
                print(f"\n✅ {bright_green(mode_names[choice])}가 선택되었습니다!")
                
                # AI 모드별 추가 안내
                if choice == 1:  # AI 파트너 모드
                    print("🎯 1명만 조작하고 나머지 3명은 AI가 자동으로 처리합니다.")
                    print("💡 전투에서 '💬 AI 요청 확인'으로 AI의 제안을 들어보세요!")
                elif choice == 2:  # 듀얼 컨트롤
                    print("🎯 2명을 직접 조작하고 2명은 AI가 처리합니다.")
                    print("💡 적절한 밸런스로 전투의 재미와 효율을 모두 챙길 수 있습니다!")
                elif choice == 3:  # 혼합 모드
                    print("🎯 상황에 따라 조작 방식을 자유롭게 변경할 수 있습니다.")
                    print("💡 전투 중에도 AI 모드를 켜고 끌 수 있습니다!")
                
                # 아이템 공유 권한 설정
                try:
                    self._setup_item_sharing_for_ai_mode()
                except:
                    pass  # 메서드가 없어도 계속 진행
                
                # AI 초기화 성공 메시지 (숨김)
                if self.ai_game_mode_enabled:
                    # print(f"\n{bright_cyan('🚀 AI 시스템이 활성화되었습니다!')}")  # 숨김
                    # print("   ✅ 개성있는 AI 동료들이 준비되었습니다")  # 숨김
                    # print("   ✅ 자동 장비 관리 시스템 활성화")  # 숨김
                    # print("   ✅ 협동 공격 시스템 준비 완료")  # 숨김
                    pass  # 조용히 처리
            
            if hasattr(self, 'keyboard') and self.keyboard:
                self.keyboard.wait_for_key("🔑 아무 키나 눌러 계속...")
            else:
                input("🔑 아무 키나 눌러 계속...")
            
        except ImportError:
            # 커서 메뉴를 사용할 수 없는 경우 기본 메뉴로 대체
            print("⚠️ 커서 메뉴 시스템을 로드할 수 없어 기본 메뉴를 사용합니다.")
            self._select_ai_game_mode_fallback()
            
        except Exception as e:
            print(f"❌ AI 모드 선택 오류: {e}")
            print("기본 모드(전체 수동 조작)로 진행합니다.")
            self.ai_game_mode_enabled = False
    
    
    def _select_ai_game_mode_fallback(self):
        """AI 게임모드 선택 - 기본 메뉴 (폴백)"""
        print(f"\n{'='*50}")
        print(f"{bright_white('        🤖 게임 조작 모드 선택 🤖')}")
        print(f"{'='*50}")
        
        print(f"{bright_yellow('조작 모드를 선택하세요:')}")
        print("1. 🎮 전체 수동 조작 (모든 캐릭터 직접 조작)")
        print("2. 🤖 AI 파트너 모드 (1명만 조작, 나머지는 AI)")
        print("3. 🎯 듀얼 컨트롤 (2명 조작, 나머지는 AI)")
        print("4. 🔄 혼합 모드 (상황에 따라 변경)")
        
        print(f"\n{bright_cyan('💡 AI 모드의 장점:')}")
        print("   ⚡ 전투 속도 향상")
        print("   🧠 스마트한 AI 동료 지원")
        print("   🎯 전략적 협동 공격")
        print("   📦 아이템 자동 관리")
        
        while True:
            try:
                choice = input(f"\n{bright_white('선택 (1-4): ')}")
                
                if choice == '1':
                    # 전체 수동 조작
                    self.ai_game_mode_enabled = False
                    print(f"\n✅ {bright_green('전체 수동 조작 모드')}가 선택되었습니다.")
                    print("🎮 모든 캐릭터를 직접 조작합니다.")
                    break
                
                elif choice in ['2', '3', '4']:
                    # AI 게임모드 활성화
                    self.ai_game_mode_enabled = True
                    
                    # 조작할 캐릭터 수 결정
                    controlled_count = 1 if choice == '2' else 2 if choice == '3' else 1
                    
                    from game.ai_game_mode import ai_game_mode_manager
                    
                    ai_game_mode_manager.initialize_ai_mode(self.party_manager.members, controlled_count)
                    
                    mode_names = {
                        '2': '🤖 AI 파트너 모드',
                        '3': '🎯 듀얼 컨트롤 모드', 
                        '4': '🔄 혼합 모드'
                    }
                    
                    print(f"\n✅ {bright_green(mode_names[choice])}가 선택되었습니다.")
                    
                    # 아이템 공유 권한 설정
                    self._setup_item_sharing_for_ai_mode()
                    break
                
                else:
                    print("❌ 1-4 중에서 선택해주세요.")
                    
            except KeyboardInterrupt:
                print(f"\n{bright_yellow('기본 모드(전체 수동 조작)로 진행합니다.')}")
                self.ai_game_mode_enabled = False
                break
            self.ai_game_mode_enabled = False
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def _setup_item_sharing_for_ai_mode(self):
        """AI 모드용 아이템 공유 설정"""
        try:
            from game.party_item_sharing import party_item_sharing, ItemSharingPermission
            from game.cursor_menu_system import CursorMenu
            
            # 커서 메뉴 시스템 사용
            try:
                menu = CursorMenu(
                    title="🤖 AI 동료 아이템 사용 권한 설정",
                    options=[
                        "🔒 제한적 접근 (치료/회복 아이템만)",
                        "🔓 전체 접근 허용 (모든 아이템)",
                        "🤔 사용 전 확인 (항상 허가 요청)",
                        "🚫 사용 금지"
                    ],
                    descriptions=[
                        "AI가 치료와 회복 아이템만 사용할 수 있습니다 (추천)",
                        "AI가 모든 아이템을 자유롭게 사용할 수 있습니다",
                        "AI가 아이템 사용 전 항상 허가를 요청합니다",
                        "AI가 어떤 아이템도 사용할 수 없습니다"
                    ],
                    audio_manager=getattr(self, 'audio_manager', None)
                )
                
                choice = menu.run()
                if choice is not None:
                    permission_map = [
                        ItemSharingPermission.LIMITED_ACCESS,
                        ItemSharingPermission.FULL_ACCESS,
                        ItemSharingPermission.ASK_PERMISSION,
                        ItemSharingPermission.NO_ACCESS
                    ]
                    party_item_sharing.set_sharing_permission(permission_map[choice])
                else:
                    # 기본값: 제한적 접근
                    party_item_sharing.set_sharing_permission(ItemSharingPermission.LIMITED_ACCESS)
                    print("❌ 선택이 취소되었습니다. 기본값(제한적 접근)으로 설정됩니다.")
                    
            except ImportError:
                # 폴백: 기존 텍스트 기반 메뉴
                print(f"\n{bright_yellow('🤖 AI 동료 아이템 사용 권한 설정:')}")
                print("1. 🔒 제한적 접근 (치료/회복 아이템만) - 추천")
                print("2. 🔓 전체 접근 허용 (모든 아이템)")
                print("3. 🤔 사용 전 확인 (항상 허가 요청)")
                print("4. 🚫 사용 금지")
                
                choice = input("선택 (1-4, 기본값: 1): ") or '1'
                
                permission_map = {
                    '1': ItemSharingPermission.LIMITED_ACCESS,
                    '2': ItemSharingPermission.FULL_ACCESS,
                    '3': ItemSharingPermission.ASK_PERMISSION,
                    '4': ItemSharingPermission.NO_ACCESS
                }
                
                if choice in permission_map:
                    party_item_sharing.set_sharing_permission(permission_map[choice])
                else:
                    # 기본값: 제한적 접근
                    party_item_sharing.set_sharing_permission(ItemSharingPermission.LIMITED_ACCESS)
                    print("❌ 잘못된 선택, 기본값(제한적 접근)으로 설정됩니다.")
                
        except Exception as e:
            print(f"❌ 아이템 공유 설정 오류: {e}")
    
    def select_party_passive_effects(self):
        """파티 전체 패시브 효과 선택"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white
            
            # 🌟 완전 리메이크된 창의적 패시브 시스템 (1-10 코스트, 최대 6개 제한)
            all_passive_effects = [
                # === 1코스트 패시브 (기초 효과) ===
                {
                    "name": "첫걸음의 용기", 
                    "description": "모든 능력치 고정 +8 (물리공격, 마법공격, 방어력, 마법방어력, 스피드)",
                    "effect_type": "permanent_stats_boost",
                    "effect_value": {"all_stats": 8},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "미니멀리스트", 
                    "description": "인벤토리 50% 이하일 때 SPD +15%, 회피율 +10%",
                    "effect_type": "minimalist",
                    "effect_value": {"speed_bonus": 0.15, "dodge_bonus": 0.10, "inventory_threshold": 0.50},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "새벽의 집중", 
                    "description": "전투 첫 턴에 행동속도 +100%",
                    "effect_type": "dawn_focus",
                    "effect_value": {"first_turn_speed": 1.00},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "절약 정신", 
                    "description": "아이템 사용 시 25% 확률로 소모하지 않음",
                    "effect_type": "conservation",
                    "effect_value": {"save_chance": 0.25},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "행운의 동전", 
                    "description": "골드 습득 시 10% 확률로 2배",
                    "effect_type": "lucky_coin",
                    "effect_value": {"double_chance": 0.10},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                
                # === 2코스트 패시브 (응용 효과) ===
                {
                    "name": "역전의 명수", 
                    "description": "HP 30% 이하일 때 크리티컬 확률 +30%, 피해 감소 +25%",
                    "effect_type": "comeback_master",
                    "effect_value": {"crit_bonus": 0.30, "damage_reduction": 0.25, "hp_threshold": 0.30},
                    "cost": 2,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "모험가의 직감", 
                    "description": "숨겨진 문 발견율 +40%, 함정 감지 +25%",
                    "effect_type": "adventurer_instinct",
                    "effect_value": {"secret_find": 0.40, "trap_detect": 0.25},
                    "cost": 2,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "연쇄 반응", 
                    "description": "크리티컬 히트 시 다음 공격 데미지 +20% (3회 중첩)",
                    "effect_type": "chain_reaction",
                    "effect_value": {"damage_boost": 0.20, "max_stacks": 3},
                    "cost": 2,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "수집가의 눈", 
                    "description": "레어 아이템 발견율 +20%, 중복 아이템 시 골드 보너스 +50%",
                    "effect_type": "collector_eye",
                    "effect_value": {"rare_find": 0.20, "duplicate_bonus": 0.50},
                    "cost": 2,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "일사천리", 
                    "description": "같은 스킬 연속 사용 시 MP 소모 -10% (최대 -50%)",
                    "effect_type": "momentum",
                    "effect_value": {"mp_reduction": 0.10, "max_reduction": 0.50},
                    "cost": 2,
                    "unlock_cost": 30,
                    "rarity": "uncommon"
                },
                {
                    "name": "위기 대응", 
                    "description": "상태이상 걸릴 때 즉시 HP 15% 회복",
                    "effect_type": "crisis_response",
                    "effect_value": {"heal_percent": 0.15},
                    "cost": 2,
                    "unlock_cost": 40,
                    "rarity": "uncommon"
                },
                {
                    "name": "최후의 방어막", 
                    "description": "HP 30% 이하일 때 받는 피해 40% 감소, 보호막 생성",
                    "effect_type": "last_defense",
                    "effect_value": {"damage_reduction": 0.40, "hp_threshold": 0.30, "shield_bonus": True},
                    "cost": 3,
                    "unlock_cost": 50,
                    "rarity": "uncommon"
                },
                
                # === 3코스트 패시브 (전략적 효과) ===
                {
                    "name": "완벽주의자", 
                    "description": "풀 HP/MP일 때 모든 행동 효과 +25%",
                    "effect_type": "perfectionist",
                    "effect_value": {"effect_boost": 0.25},
                    "cost": 3,
                    "unlock_cost": 50,
                    "rarity": "uncommon"
                },
                {
                    "name": "도박꾼의 심리", 
                    "description": "공격/스킬 사용 시 10% 확률로 2배 효과, 5% 확률로 실패",
                    "effect_type": "gambler_mind",
                    "effect_value": {"double_chance": 0.10, "fail_chance": 0.05},
                    "cost": 3,
                    "unlock_cost": 60,
                    "rarity": "uncommon"
                },
                {
                    "name": "시너지 마스터", 
                    "description": "파티원과 같은 타겟 공격 시 데미지 +35%",
                    "effect_type": "synergy_master",
                    "effect_value": {"synergy_damage": 0.35},
                    "cost": 3,
                    "unlock_cost": 70,
                    "rarity": "uncommon"
                },
                {
                    "name": "변화의 달인", 
                    "description": "매 5턴마다 랜덤 능력치 +50% (1턴 지속)",
                    "effect_type": "change_master",
                    "effect_value": {"stat_boost": 0.50, "interval": 5, "duration": 1},
                    "cost": 3,
                    "unlock_cost": 80,
                    "rarity": "uncommon"
                },
                {
                    "name": "역학 관계", 
                    "description": "아군이 죽을 때마다 생존 파티원 모든 능력치 +10% (최대 +30%)",
                    "effect_type": "dynamic_relationship",
                    "effect_value": {"stat_per_death": 0.10, "max_bonus": 0.30},
                    "cost": 3,
                    "unlock_cost": 90,
                    "rarity": "uncommon"
                },
                
                # === 4코스트 패시브 (전문가 효과) ===
                {
                    "name": "뱀파이어 본능", 
                    "description": "적 처치 시 최대 HP의 15% 회복, 상처도 10% 치료",
                    "effect_type": "vampire_instinct",
                    "effect_value": {"hp_restore": 0.15, "wound_heal": 0.10},
                    "cost": 4,
                    "unlock_cost": 100,
                    "rarity": "rare"
                },
                {
                    "name": "카멜레온 적응", 
                    "description": "전투마다 적의 속성에 저항 +40%, 약점 속성은 데미지 +30%",
                    "effect_type": "chameleon_adapt",
                    "effect_value": {"resist_bonus": 0.40, "weakness_damage": 0.30},
                    "cost": 4,
                    "unlock_cost": 120,
                    "rarity": "rare"
                },
                {
                    "name": "기계적 정밀", 
                    "description": "연속 공격 시 명중률과 크리티컬 +10% (최대 50%)",
                    "effect_type": "mechanical_precision",
                    "effect_value": {"accuracy_per_hit": 0.10, "crit_per_hit": 0.10, "max_bonus": 0.50},
                    "cost": 4,
                    "unlock_cost": 110,
                    "rarity": "rare"
                },
                {
                    "name": "원소 순환", 
                    "description": "서로 다른 속성 스킬 사용 시 다음 스킬 위력 +40%",
                    "effect_type": "elemental_cycle",
                    "effect_value": {"damage_bonus": 0.40},
                    "cost": 4,
                    "unlock_cost": 130,
                    "rarity": "rare"
                },
                {
                    "name": "보물 자석", 
                    "description": "적 처치 후 2칸 내 숨겨진 아이템 자동 발견",
                    "effect_type": "treasure_magnet",
                    "effect_value": {"auto_find_range": 2},
                    "cost": 4,
                    "unlock_cost": 140,
                    "rarity": "rare"
                },
                
                # === 5코스트 패시브 (마스터 효과) ===
                {
                    "name": "분신술", 
                    "description": "치명타 시 15% 확률로 즉시 한 번 더 행동",
                    "effect_type": "shadow_clone",
                    "effect_value": {"extra_action_chance": 0.15},
                    "cost": 5,
                    "unlock_cost": 150,
                    "rarity": "rare"
                },
                {
                    "name": "시공간 왜곡", 
                    "description": "스킬 사용 시 30% 확률로 쿨다운 초기화",
                    "effect_type": "spacetime_distort",
                    "effect_value": {"cooldown_reset_chance": 0.30},
                    "cost": 5,
                    "unlock_cost": 170,
                    "rarity": "epic"
                },
                {
                    "name": "생명 순환", 
                    "description": "아군 죽음 시 생존자들 최대 HP +10% (최대 +30%, 영구)",
                    "effect_type": "life_cycle",
                    "effect_value": {"hp_gain_per_death": 0.10, "max_bonus": 0.30},
                    "cost": 5,
                    "unlock_cost": 160,
                    "rarity": "epic"
                },
                {
                    "name": "운명 조작", 
                    "description": "1% 확률 이벤트가 10%로, 10% 확률 이벤트가 20%로 증가",
                    "effect_type": "fate_manipulation",
                    "effect_value": {"low_prob_mult": 10, "high_prob_mult": 2},
                    "cost": 5,
                    "unlock_cost": 180,
                    "rarity": "epic"
                },
                {
                    "name": "마법 회로", 
                    "description": "MP 0일 때 HP를 MP로 변환하여 스킬 사용 가능 (1:2 비율)",
                    "effect_type": "magic_circuit",
                    "effect_value": {"hp_to_mp_ratio": 2},
                    "cost": 5,
                    "unlock_cost": 190,
                    "rarity": "epic"
                },
                
                # === 6코스트 패시브 (전설적 효과) ===
                {
                    "name": "불사조의 심장", 
                    "description": "죽음 시 50% HP로 부활 + 1턴간 무적 (1회/층)",
                    "effect_type": "phoenix_heart",
                    "effect_value": {"revive_hp": 0.50, "invincible_turns": 1, "uses_per_floor": 1},
                    "cost": 6,
                    "unlock_cost": 200,
                    "rarity": "epic"
                },
                {
                    "name": "시간 도둑", 
                    "description": "턴 종료 시 20% 확률로 추가 턴 획득",
                    "effect_type": "time_thief",
                    "effect_value": {"extra_turn_chance": 0.20},
                    "cost": 6,
                    "unlock_cost": 220,
                    "rarity": "epic"
                },
                {
                    "name": "차원 보관함", 
                    "description": "인벤토리 크기 무제한 + 전투 중 아이템 즉시 사용",
                    "effect_type": "dimensional_storage",
                    "effect_value": {"unlimited_inventory": True, "instant_use": True},
                    "cost": 6,
                    "unlock_cost": 240,
                    "rarity": "legendary"
                },
                {
                    "name": "감정 증폭기", 
                    "description": "크리티컬/회피/치명타 시 감정 스택 획득, 10스택당 모든 능력 +25%",
                    "effect_type": "emotion_amplifier",
                    "effect_value": {"stack_per_event": 1, "stat_per_10_stacks": 0.25},
                    "cost": 6,
                    "unlock_cost": 230,
                    "rarity": "legendary"
                },
                {
                    "name": "상성 지배자", 
                    "description": "상성 불리할 때 데미지 +100%, 유리할 때 MP 소모 -50%",
                    "effect_type": "affinity_master",
                    "effect_value": {"disadvantage_damage": 1.00, "advantage_mp_save": 0.50},
                    "cost": 6,
                    "unlock_cost": 250,
                    "rarity": "legendary"
                },
                
                # === 7코스트 패시브 (신화적 효과) ===
                {
                    "name": "만물 동조", 
                    "description": "물리/마법 스킬이 각각 상대방 스탯의 50%도 추가 적용",
                    "effect_type": "universal_sync",
                    "effect_value": {"cross_stat_ratio": 0.50},
                    "cost": 7,
                    "unlock_cost": 300,
                    "rarity": "legendary"
                },
                {
                    "name": "확률 조작자", 
                    "description": "모든 확률 이벤트를 1회/전투 원하는 결과로 고정 가능",
                    "effect_type": "probability_hacker",
                    "effect_value": {"control_per_battle": 1},
                    "cost": 7,
                    "unlock_cost": 350,
                    "rarity": "mythic"
                },
                {
                    "name": "무한 연쇄", 
                    "description": "스킬 적중 시 다른 파티원이 즉시 연계 공격 (데미지 50%)",
                    "effect_type": "infinite_chain",
                    "effect_value": {"chain_damage": 0.50},
                    "cost": 7,
                    "unlock_cost": 320,
                    "rarity": "mythic"
                },
                {
                    "name": "기억 조작", 
                    "description": "이전에 사용한 스킬들을 MP 없이 재사용 가능 (1회씩)",
                    "effect_type": "memory_hack",
                    "effect_value": {"free_reuse": True},
                    "cost": 7,
                    "unlock_cost": 380,
                    "rarity": "mythic"
                },
                
                # === 8코스트 패시브 (초월적 효과) ===
                {
                    "name": "인과율 조작", 
                    "description": "받을 피해를 대신 적에게 반사 (30% 확률)",
                    "effect_type": "causality_hack",
                    "effect_value": {"reflect_chance": 0.30},
                    "cost": 8,
                    "unlock_cost": 400,
                    "rarity": "mythic"
                },
                {
                    "name": "현실 편집", 
                    "description": "전투 중 1회 모든 상태를 원하는 대로 변경 가능",
                    "effect_type": "reality_edit",
                    "effect_value": {"edit_per_battle": 1},
                    "cost": 8,
                    "unlock_cost": 450,
                    "rarity": "mythic"
                },
                {
                    "name": "존재 증명", 
                    "description": "생존 파티원 수만큼 모든 효과 +25% (최대 4명=100%)",
                    "effect_type": "existence_proof",
                    "effect_value": {"effect_per_member": 0.25, "max_members": 4},
                    "cost": 8,
                    "unlock_cost": 480,
                    "rarity": "mythic"
                },
                
                # === 9코스트 패시브 (신적 효과) ===
                {
                    "name": "창조와 파괴", 
                    "description": "적 처치 시 새로운 랜덤 스킬 생성, 스킬 사용 시 랜덤 스킬 소멸",
                    "effect_type": "creation_destruction",
                    "effect_value": {"skill_cycle": True},
                    "cost": 9,
                    "unlock_cost": 500,
                    "rarity": "mythic"
                },
                {
                    "name": "시공간 지배", 
                    "description": "전투 시간 자유 조작 (일시정지, 되감기, 가속 각 1회)",
                    "effect_type": "spacetime_control",
                    "effect_value": {"pause": 1, "rewind": 1, "accelerate": 1},
                    "cost": 9,
                    "unlock_cost": 550,
                    "rarity": "mythic"
                },
                
                # === 10코스트 패시브 (절대적 효과) ===
                {
                    "name": "절대 법칙", 
                    "description": "크리티컬 확률 +50%, 모든 확률 이벤트 +20%",
                    "effect_type": "absolute_law",
                    "effect_value": {"crit_bonus": 0.50, "probability_bonus": 0.20},
                    "cost": 10,
                    "unlock_cost": 600,
                    "rarity": "mythic"
                },
                {
                    "name": "무한 가능성", 
                    "description": "매 턴 랜덤한 전설급 효과 획득 (중첩 가능)",
                    "effect_type": "infinite_possibility",
                    "effect_value": {"random_legendary_per_turn": True},
                    "cost": 10,
                    "unlock_cost": 700,
                    "rarity": "mythic"
                }
            ]
            
            # 🎯 패시브 개수 제한 시스템 (최대 3개)
            MAX_PASSIVE_COUNT = 3
            
            # 현재 최대 코스트 확인 - 영구성장과 연동
            try:
                # 기본 최대 코스트 + 메타 진행 업그레이드 + 영구성장 보너스
                meta_upgrades = self.meta_progression.data.get('max_passive_cost_upgrades', 0) if hasattr(self, 'meta_progression') else 0
                permanent_bonus = int(self.permanent_progression.get_passive_bonus("passive_cost_max")) if hasattr(self, 'permanent_progression') else 0
                
                current_max_cost = 3 + meta_upgrades + permanent_bonus  # 기본 3으로 변경
                current_max_cost = min(current_max_cost, 10)  # 최대 10으로 제한
                
                unlocked_cost = self.meta_progression.data.get('star_fragments', 0) if hasattr(self, 'meta_progression') else 999
                unlocked_passives = self.meta_progression.data.get('unlocked_passives', []) if hasattr(self, 'meta_progression') else []
                
                # 개발 모드 확인
                from config import game_config
                is_dev_mode = hasattr(game_config, 'DEVELOPMENT_MODE') and game_config.DEVELOPMENT_MODE
                
                if is_dev_mode:
                    # 개발 모드에서는 모든 패시브 해금 및 최대 코스트 확장
                    current_max_cost = 10  # 개발 모드 최대 코스트
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
            current_page = 0  # 페이지 시스템 추가
            current_cost_filter = "all"  # 코스트 필터 추가 (all, 1, 2, 3, ...)
            
            while len(selected_passives) < MAX_PASSIVE_COUNT and used_cost < current_max_cost:
                # 메뉴 옵션 생성
                options = []
                descriptions = []
                
                # 선택 가능한 패시브들 (이미 선택된 것 제외, 코스트가 남은 용량 이하)
                base_available_passives = [p for p in passive_effects 
                                         if p not in selected_passives 
                                         and p['cost'] <= (current_max_cost - used_cost)]
                
                # 코스트 필터 적용
                if current_cost_filter == "all":
                    available_passives = base_available_passives
                else:
                    filter_cost = int(current_cost_filter)
                    available_passives = [p for p in base_available_passives if p['cost'] == filter_cost]
                
                # 페이지네이션 설정
                PASSIVES_PER_PAGE = 12  # 한 페이지당 12개씩 (49개 → 5페이지)
                total_pages = (len(available_passives) + PASSIVES_PER_PAGE - 1) // PASSIVES_PER_PAGE if available_passives else 1
                
                # 현재 페이지의 패시브들
                start_idx = current_page * PASSIVES_PER_PAGE
                end_idx = min(start_idx + PASSIVES_PER_PAGE, len(available_passives))
                current_page_passives = available_passives[start_idx:end_idx]
                
                for passive in current_page_passives:
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
                
                # 코스트 필터 옵션 추가
                cost_filters = ["all"] + [str(i) for i in range(1, 11) if any(p['cost'] == i for p in base_available_passives)]
                
                options.append(f"🔢 {bright_cyan('코스트 필터')}: {current_cost_filter}")
                descriptions.append(f"현재 필터: {current_cost_filter} | 사용 가능: {', '.join(cost_filters)}")
                
                # 페이지 네비게이션 옵션 추가
                if total_pages > 1:
                    if current_page > 0:
                        options.append(f"⬅️ {bright_cyan('이전 페이지')}")
                        descriptions.append("이전 페이지의 패시브를 봅니다")
                    
                    if current_page < total_pages - 1:
                        options.append(f"➡️ {bright_cyan('다음 페이지')}")
                        descriptions.append("다음 페이지의 패시브를 봅니다")
                
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
                    cost_info = f"\n현재 별조각: {current_fragments} ⭐ | 사용 코스트: {used_cost}/{current_max_cost} | 패시브 개수: {len(selected_passives)}/{MAX_PASSIVE_COUNT}"
                    if total_pages > 1:
                        cost_info += f" | 페이지: {current_page + 1}/{total_pages}"
                    if current_cost_filter != "all":
                        cost_info += f" | 필터: {current_cost_filter}코스트"
                else:
                    cost_info = f"\n사용 코스트: {used_cost}/{current_max_cost} | 패시브 개수: {len(selected_passives)}/{MAX_PASSIVE_COUNT}"
                    if total_pages > 1:
                        cost_info += f" | 페이지: {current_page + 1}/{total_pages}"
                    if current_cost_filter != "all":
                        cost_info += f" | 필터: {current_cost_filter}코스트"
                
                # 선택된 패시브 철회 옵션 (선택된 패시브가 있을 때)
                if selected_passives:
                    options.append(f"🔄 {bright_white('선택된 패시브 철회')}")
                    descriptions.append("이미 선택한 패시브를 철회하고 코스트를 되돌립니다")
                
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
                
                # 페이지 네비게이션 처리
                navigation_offset = 0
                if total_pages > 1:
                    if current_page > 0:
                        navigation_offset += 1
                    if current_page < total_pages - 1:
                        navigation_offset += 1
                
                # 결과 처리
                if result < len(current_page_passives):
                    # 패시브 선택
                    selected_passive = current_page_passives[result]
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
                    
                    if used_cost >= current_max_cost or len(selected_passives) >= MAX_PASSIVE_COUNT:
                        if used_cost >= current_max_cost:
                            print(f"\n{bright_yellow('🎯 최대 코스트(' + str(current_max_cost) + ')에 도달했습니다!')}")
                        if len(selected_passives) >= MAX_PASSIVE_COUNT:
                            print(f"\n{bright_yellow('🎯 최대 패시브 개수(' + str(MAX_PASSIVE_COUNT) + ')에 도달했습니다!')}")
                        break
                        
                # 페이지 네비게이션 및 기타 옵션 처리
                else:
                    # 옵션 인덱스 계산 (패시브 선택 후 시작)
                    option_index = result - len(current_page_passives)
                    
                    # 코스트 필터 처리
                    if option_index == 0:
                        # 코스트 필터 변경
                        cost_filters = ["all"] + [str(i) for i in range(1, 11) if any(p['cost'] == i for p in base_available_passives)]
                        current_filter_index = cost_filters.index(current_cost_filter)
                        next_filter_index = (current_filter_index + 1) % len(cost_filters)
                        current_cost_filter = cost_filters[next_filter_index]
                        current_page = 0  # 필터 변경 시 첫 페이지로
                        continue
                    
                    option_index -= 1  # 코스트 필터 옵션 제외
                    
                    # 페이지 네비게이션 처리
                    if total_pages > 1:
                        if current_page > 0 and option_index == 0:
                            # 이전 페이지
                            current_page -= 1
                            continue
                        elif current_page > 0:
                            option_index -= 1
                        
                        if current_page < total_pages - 1 and option_index == 0:
                            # 다음 페이지
                            current_page += 1
                            continue
                        elif current_page < total_pages - 1:
                            option_index -= 1
                    
                    # 최대 코스트 업그레이드 옵션이 있는지 확인
                    max_cost_upgrade_available = (hasattr(self, 'meta_progression') and 
                                                unlocked_cost >= max_cost_upgrade_cost and 
                                                meta_upgrades < 7 and  # 메타 진행으로는 최대 7단계까지
                                                current_max_cost < 10 and  # 아직 최대에 도달하지 않음
                                                not is_dev_mode)  # 개발 모드가 아닐 때만
                    
                    if max_cost_upgrade_available and option_index == 0:
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
                    
                    # 다음 옵션 인덱스 조정
                    if max_cost_upgrade_available:
                        option_index -= 1
                    
                    if selected_passives and option_index == 0:
                        # 패시브 철회 옵션
                        if selected_passives:
                            # 철회할 패시브 선택
                            withdraw_options = [f"{p['name']} [{p['cost']}코스트]" for p in selected_passives]
                            withdraw_descriptions = [f"💡 {p['description']}" for p in selected_passives]
                            withdraw_options.append("🚫 철회 취소")
                            withdraw_descriptions.append("패시브 철회를 취소하고 돌아갑니다")
                            
                            withdraw_menu = CursorMenu(
                                "🔄 철회할 패시브 선택",
                                withdraw_options, withdraw_descriptions, cancellable=True
                            )
                            withdraw_result = withdraw_menu.run()
                            
                            if withdraw_result is not None and withdraw_result < len(selected_passives):
                                # 선택된 패시브 철회
                                withdrawn_passive = selected_passives.pop(withdraw_result)
                                used_cost -= withdrawn_passive['cost']
                                print(f"\n{yellow('🔄 ' + withdrawn_passive['name'] + ' 패시브가 철회되었습니다.')}")
                                print(f"{cyan('💡 ' + str(withdrawn_passive['cost']) + ' 코스트가 되돌려졌습니다.')}")
                            continue
                    
                    # 다음 옵션들 처리
                    if selected_passives:
                        option_index -= 1
                    
                    if selected_passives and option_index == 0:
                        # 선택 완료
                        break
                    elif option_index == (0 if not selected_passives else 1):
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
            if effect_type == "permanent_stats_boost":
                # 영구 스탯 부스트 (첫걸음의 용기)
                for member in self.party_manager.members:
                    stat_boost = effect_value.get("all_stats", 0)
                    if stat_boost > 0:
                        member.physical_attack += stat_boost
                        member.magic_attack += stat_boost
                        member.physical_defense += stat_boost
                        member.magic_defense += stat_boost
                        member.speed += stat_boost
                        if not hasattr(member, 'permanent_boost_applied'):
                            member.permanent_boost_applied = True
                            print(f"🌟 {member.name}의 첫걸음의 용기가 적용되었습니다! (모든 능력치 +{stat_boost})")
                        
            elif effect_type == "first_battle_boost":
                # 첫 전투 부스트는 전투 시스템에서 처리
                for member in self.party_manager.members:
                    if not hasattr(member, 'first_battle_used'):
                        member.first_battle_used = False
                        member.first_battle_boost = effect_value.get("all_stats", 0)
                        
            elif effect_type == "minimalist":
                # 미니멀리스트는 인벤토리 체크 시 처리
                for member in self.party_manager.members:
                    member.minimalist_bonus = effect_value
                    
            elif effect_type == "dawn_focus":
                # 새벽의 집중은 ATB 시스템에서 처리
                for member in self.party_manager.members:
                    member.dawn_focus_bonus = effect_value.get("first_turn_speed", 0)
                    
            elif effect_type == "conservation":
                # 절약 정신은 아이템 사용 시 처리
                for member in self.party_manager.members:
                    member.conservation_chance = effect_value.get("save_chance", 0)
                    
            elif effect_type == "lucky_coin":
                # 행운의 동전은 골드 획득 시 처리
                for member in self.party_manager.members:
                    member.lucky_coin_chance = effect_value.get("double_chance", 0)
                    
            elif effect_type == "comeback_master":
                # 역전의 명수는 전투 중 HP 체크 시 처리
                for member in self.party_manager.members:
                    member.comeback_bonus = effect_value
                    
            elif effect_type == "adventurer_instinct":
                # 모험가의 직감은 던전 탐험 시 처리
                for member in self.party_manager.members:
                    member.secret_find_bonus = effect_value.get("secret_find", 0)
                    member.trap_detect_bonus = effect_value.get("trap_detect", 0)
                    
            elif effect_type == "chain_reaction":
                # 연쇄 반응은 크리티컬 히트 시 처리
                for member in self.party_manager.members:
                    member.chain_reaction = effect_value
                    if not hasattr(member, 'chain_stacks'):
                        member.chain_stacks = 0
                        
            elif effect_type == "collector_eye":
                # 수집가의 눈은 아이템 발견/판매 시 처리
                for member in self.party_manager.members:
                    member.rare_find_bonus = effect_value.get("rare_find", 0)
                    member.duplicate_bonus = effect_value.get("duplicate_bonus", 0)
                    
            elif effect_type == "momentum":
                # 일사천리는 연속 스킬 사용 시 처리
                for member in self.party_manager.members:
                    member.momentum_effect = effect_value
                    if not hasattr(member, 'last_skill_used'):
                        member.last_skill_used = None
                        member.momentum_stacks = 0
                        
            elif effect_type == "crisis_response":
                # 위기 대응은 상태이상 걸릴 때 처리
                for member in self.party_manager.members:
                    member.crisis_response_heal = effect_value.get("heal_percent", 0)
                    
            elif effect_type == "perfectionist":
                # 완벽주의자는 매 턴 HP/MP 체크 시 처리
                for member in self.party_manager.members:
                    member.perfectionist_bonus = effect_value.get("effect_boost", 0)
                    
            elif effect_type == "gambler_mind":
                # 도박꾼의 심리는 액션 실행 시 처리
                for member in self.party_manager.members:
                    member.gambler_effect = effect_value
                    
            elif effect_type == "synergy_master":
                # 시너지 마스터는 타겟 공격 시 처리
                for member in self.party_manager.members:
                    member.synergy_damage_bonus = effect_value.get("synergy_damage", 0)
                    
            elif effect_type == "change_master":
                # 변화의 달인은 턴 카운트로 처리
                for member in self.party_manager.members:
                    member.change_master_effect = effect_value
                    if not hasattr(member, 'change_master_counter'):
                        member.change_master_counter = 0
                        
            elif effect_type == "dynamic_relationship":
                # 역학 관계는 아군 사망 시 처리
                for member in self.party_manager.members:
                    member.dynamic_relationship = effect_value
                    if not hasattr(member, 'relationship_stacks'):
                        member.relationship_stacks = 0
                        
            elif effect_type == "vampire_instinct":
                # 뱀파이어 본능은 적 처치 시 처리
                for member in self.party_manager.members:
                    member.vampire_heal = effect_value
                    
            elif effect_type == "life_cycle":
                # 생명 순환은 아군 사망 시 처리
                for member in self.party_manager.members:
                    member.life_cycle_effect = effect_value
                    if not hasattr(member, 'life_cycle_bonus'):
                        member.life_cycle_bonus = 0
                        
            # 기타 모든 패시브 효과들을 멤버에 저장
            for member in self.party_manager.members:
                if not hasattr(member, 'passive_effects'):
                    member.passive_effects = []
                member.passive_effects.append(passive)
                    
            # 특수 효과들 추가 처리
            if effect_type == "legendary_hero":
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
                        
            elif effect_type == "mana_cycle":
                # 마나 순환 효과
                for member in self.party_manager.members:
                    member.mana_cycle_chance = effect_value.get("no_cost_chance", 0)
                    
            elif effect_type == "healing_aura":
                # 치유의 기운 효과
                for member in self.party_manager.members:
                    member.healing_aura_effect = effect_value
                    
            elif effect_type == "scholar_wisdom":
                # 학자의 지혜 효과
                for member in self.party_manager.members:
                    member.scholar_wisdom = effect_value
                    if not hasattr(member, 'scholar_stacks'):
                        member.scholar_stacks = 0
                        
            elif effect_type == "absolute_rule":
                # 절대 법칙 효과들
                for member in self.party_manager.members:
                    if "rule_of_three" in effect_value:
                        member.rule_of_three = effect_value["rule_of_three"]
                    if "rule_of_seven" in effect_value:
                        member.rule_of_seven = effect_value["rule_of_seven"]
                    if "rule_of_thirteen" in effect_value:
                        member.rule_of_thirteen = effect_value["rule_of_thirteen"]
                        
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
    
    def apply_first_battle_boost(self, member):
        """첫 전투 부스트 적용"""
        if hasattr(member, 'first_battle_used') and not member.first_battle_used:
            if hasattr(member, 'first_battle_boost'):
                member.first_battle_used = True
                boost = member.first_battle_boost
                
                # 임시 스탯 부스트 적용
                member.temp_stat_boost = {
                    'physical_attack': int(member.physical_attack * boost),
                    'magic_attack': int(member.magic_attack * boost),
                    'physical_defense': int(member.physical_defense * boost),
                    'magic_defense': int(member.magic_defense * boost),
                    'speed': int(member.speed * boost)
                }
                print(f"🌟 {member.name}의 첫걸음의 용기가 발동되었습니다!")
                return True
        return False
    
    def check_minimalist_bonus(self, member):
        """미니멀리스트 보너스 확인"""
        if hasattr(member, 'minimalist_bonus'):
            if hasattr(member, 'inventory'):
                # 인벤토리 사용량 체크
                used_slots = len([item for item in member.inventory if item is not None])
                max_slots = len(member.inventory)
                usage_rate = used_slots / max_slots if max_slots > 0 else 0
                
                threshold = member.minimalist_bonus.get('inventory_threshold', 0.5)
                if usage_rate <= threshold:
                    return {
                        'speed_bonus': member.minimalist_bonus.get('speed_bonus', 0),
                        'dodge_bonus': member.minimalist_bonus.get('dodge_bonus', 0)
                    }
        return None
    
    def apply_conservation_effect(self, member, item_used):
        """절약 정신 효과 적용"""
        if hasattr(member, 'conservation_chance'):
            import random
            if random.random() < member.conservation_chance:
                print(f"🌟 {member.name}의 절약 정신으로 {item_used}이(가) 소모되지 않았습니다!")
                return True  # 아이템 소모하지 않음
        return False  # 아이템 정상 소모
    
    def apply_lucky_coin_effect(self, gold_amount):
        """행운의 동전 효과 적용"""
        for member in self.party_manager.members:
            if hasattr(member, 'lucky_coin_chance'):
                import random
                if random.random() < member.lucky_coin_chance:
                    print(f"🪙 {member.name}의 행운의 동전 효과로 골드가 2배가 되었습니다!")
                    return gold_amount * 2
        return gold_amount
    
    def check_comeback_master_bonus(self, member):
        """역전의 명수 보너스 확인"""
        if hasattr(member, 'comeback_bonus'):
            hp_threshold = member.comeback_bonus.get('hp_threshold', 0.25)
            if member.current_hp <= (member.max_hp * hp_threshold):
                return member.comeback_bonus.get('crit_bonus', 0)
        return 0
    
    def apply_chain_reaction(self, member, is_critical=False):
        """연쇄 반응 효과 적용"""
        if hasattr(member, 'chain_reaction') and is_critical:
            damage_boost = member.chain_reaction.get('damage_boost', 0)
            max_stacks = member.chain_reaction.get('max_stacks', 3)
            
            if not hasattr(member, 'chain_stacks'):
                member.chain_stacks = 0
            
            if member.chain_stacks < max_stacks:
                member.chain_stacks += 1
                print(f"⚡ {member.name}의 연쇄 반응 스택 증가! ({member.chain_stacks}/{max_stacks})")
            
            return damage_boost * member.chain_stacks
        return 0
    
    def apply_crisis_response(self, member):
        """위기 대응 효과 적용 (상태이상 걸릴 때)"""
        if hasattr(member, 'crisis_response_heal'):
            heal_percent = member.crisis_response_heal
            heal_amount = int(member.max_hp * heal_percent)
            member.current_hp = min(member.max_hp - getattr(member, 'wounds', 0), 
                                  member.current_hp + heal_amount)
            print(f"💚 {member.name}의 위기 대응으로 HP {heal_amount} 회복!")
    
    def check_perfectionist_bonus(self, member):
        """완벽주의자 보너스 확인"""
        if hasattr(member, 'perfectionist_bonus'):
            wounds = getattr(member, 'wounds', 0)
            effective_max_hp = member.max_hp - wounds
            
            if member.current_hp >= effective_max_hp and member.current_mp >= member.max_mp:
                return member.perfectionist_bonus
        return 0
    
    def apply_vampire_instinct(self, member):
        """뱀파이어 본능 효과 적용 (적 처치 시)"""
        if hasattr(member, 'vampire_heal'):
            hp_restore_rate = member.vampire_heal.get('hp_restore', 0)
            wound_heal_rate = member.vampire_heal.get('wound_heal', 0)
            
            # HP 회복
            heal_amount = int(member.max_hp * hp_restore_rate)
            member.current_hp = min(member.max_hp - getattr(member, 'wounds', 0), 
                                  member.current_hp + heal_amount)
            
            # 상처 치료
            if hasattr(member, 'wounds') and member.wounds > 0:
                wound_heal = int(member.wounds * wound_heal_rate)
                member.wounds = max(0, member.wounds - wound_heal)
                print(f"🩸 {member.name}의 뱀파이어 본능으로 HP {heal_amount} 회복, 상처 {wound_heal} 치료!")
    
    def apply_dynamic_relationship_effect(self, deceased_member):
        """역학 관계 효과 적용 (아군 사망 시)"""
        for member in self.party_manager.members:
            if member != deceased_member and member.current_hp > 0:
                if hasattr(member, 'dynamic_relationship'):
                    stat_bonus = member.dynamic_relationship.get('stat_per_death', 0)
                    max_bonus = member.dynamic_relationship.get('max_bonus', 1.0)
                    
                    if not hasattr(member, 'relationship_stacks'):
                        member.relationship_stacks = 0
                    
                    current_bonus = member.relationship_stacks * stat_bonus
                    if current_bonus < max_bonus:
                        member.relationship_stacks += 1
                        print(f"💔 {member.name}의 역학 관계로 모든 능력치 증가! (+{stat_bonus*100:.0f}%)")
    
    def apply_life_cycle_effect(self, deceased_member):
        """생명 순환 효과 적용 (아군 사망 시)"""
        for member in self.party_manager.members:
            if member != deceased_member and member.current_hp > 0:
                if hasattr(member, 'life_cycle_effect'):
                    hp_gain_rate = member.life_cycle_effect.get('hp_gain_per_death', 0)
                    max_bonus_rate = member.life_cycle_effect.get('max_bonus', 0.30)
                    
                    if not hasattr(member, 'life_cycle_bonus'):
                        member.life_cycle_bonus = 0
                    
                    current_bonus = member.life_cycle_bonus
                    if current_bonus < max_bonus_rate:
                        new_bonus = min(max_bonus_rate, current_bonus + hp_gain_rate)
                        hp_increase = int(member.max_hp * hp_gain_rate)
                        member.max_hp += hp_increase
                        member.current_hp += hp_increase
                        member.life_cycle_bonus = new_bonus
                        print(f"🔄 {member.name}의 생명 순환으로 최대 HP +{hp_increase}!")
    
    def apply_scholar_wisdom(self, member, skill_used):
        """학자의 지혜 효과 적용 (스킬 사용 시)"""
        if hasattr(member, 'scholar_wisdom') and hasattr(member, 'scholar_stacks'):
            max_stacks = member.scholar_wisdom.get('max_stacks', 5)
            if member.scholar_stacks < max_stacks:
                member.scholar_stacks += 1
                print(f"📚 {member.name}의 학자의 지혜 스택 증가! ({member.scholar_stacks}/{max_stacks})")
    
    def get_scholar_wisdom_bonus(self, member):
        """학자의 지혜 보너스 확인"""
        if hasattr(member, 'scholar_wisdom') and hasattr(member, 'scholar_stacks'):
            mp_eff_bonus = member.scholar_wisdom.get('mp_efficiency', 0)
            magic_power_bonus = member.scholar_wisdom.get('magic_power', 0)
            return {
                'mp_efficiency': mp_eff_bonus * member.scholar_stacks,
                'magic_power': magic_power_bonus * member.scholar_stacks
            }
        return {'mp_efficiency': 0, 'magic_power': 0}
    
    def check_absolute_rule_effects(self, member):
        """절대 법칙 효과들 확인"""
        bonuses = {}
        
        # 3의 법칙
        if hasattr(member, 'rule_of_three') and member.current_hp == 3:
            bonuses['critical_chance'] = member.rule_of_three
        
        # 7의 법칙  
        if hasattr(member, 'rule_of_seven') and member.current_mp == 7:
            bonuses['damage_multiplier'] = member.rule_of_seven
        
        # 13의 법칙
        if hasattr(member, 'rule_of_thirteen') and (member.current_hp + member.current_mp) == 13:
            bonuses['dodge_chance'] = member.rule_of_thirteen
        
        return bonuses
    
    def apply_passive_effects_in_combat(self, attacker, target=None, skill=None, is_critical=False):
        """전투 중 패시브 효과 적용"""
        damage_modifier = 1.0
        
        # 첫걸음의 용기 확인 및 적용
        self.apply_first_battle_boost(attacker)
        
        # 역전의 명수 효과
        comeback_bonus = self.check_comeback_master_bonus(attacker)
        if comeback_bonus > 0:
            damage_modifier *= (1 + comeback_bonus)
        
        # 연쇄 반응 효과  
        chain_bonus = self.apply_chain_reaction(attacker, is_critical)
        if chain_bonus > 0:
            damage_modifier *= (1 + chain_bonus)
        
        # 완벽주의자 효과
        perfectionist_bonus = self.check_perfectionist_bonus(attacker)
        if perfectionist_bonus > 0:
            damage_modifier *= (1 + perfectionist_bonus)
        
        # 절대 법칙 효과들
        rule_bonuses = self.check_absolute_rule_effects(attacker)
        for rule_type, bonus in rule_bonuses.items():
            if rule_type == 'damage_multiplier':
                damage_modifier *= (1 + bonus)
        
        # 학자의 지혜 효과 (스킬 사용 시)
        if skill:
            self.apply_scholar_wisdom(attacker, skill)
            scholar_bonus = self.get_scholar_wisdom_bonus(attacker)
            if 'magic_power' in scholar_bonus:
                damage_modifier *= (1 + scholar_bonus['magic_power'])
        
        # 미니멀리스트 효과 확인
        minimalist_bonus = self.check_minimalist_bonus(attacker)
        if minimalist_bonus:
            # 속도/회피 보너스는 별도 처리 필요
            pass
        
        return damage_modifier
    
    def handle_enemy_defeated(self, defeated_enemy, victor):
        """적 처치 시 패시브 효과 처리"""
        # 뱀파이어 본능 적용
        self.apply_vampire_instinct(victor)
        
        # 골드 획득 시 행운의 동전 효과
        base_gold = getattr(defeated_enemy, 'gold_reward', 10)
        final_gold = self.apply_lucky_coin_effect(base_gold)
        
        return final_gold
    
    def handle_ally_death(self, deceased_member):
        """아군 사망 시 패시브 효과 처리"""
        # 역학 관계 효과
        self.apply_dynamic_relationship_effect(deceased_member)
        
        # 생명 순환 효과
        self.apply_life_cycle_effect(deceased_member)
    
    def handle_status_effect_applied(self, target, status_effect):
        """상태이상 적용 시 패시브 효과 처리"""
        # 위기 대응 효과
        self.apply_crisis_response(target)
    
    def modify_mp_cost(self, caster, original_cost):
        """MP 소모량 수정 (패시브 효과 적용)"""
        # 마나 순환 효과
        if self.check_mana_cycle():
            return 0
        
        # 학자의 지혜 효과
        scholar_bonus = self.get_scholar_wisdom_bonus(caster)
        efficiency_bonus = scholar_bonus.get('mp_efficiency', 0)
        
        modified_cost = int(original_cost * (1 - efficiency_bonus))
        return max(0, modified_cost)
    
    def apply_post_combat_effects(self):
        """전투 후 패시브 효과 적용"""
        # 치유의 기운 효과
        self.apply_healing_aura_effects()
        
        # 각 멤버의 임시 효과 리셋
        for member in self.party_manager.members:
            # 첫 전투 부스트 리셋은 하지 않음 (한 번만 사용)
            if hasattr(member, 'temp_stat_boost'):
                delattr(member, 'temp_stat_boost')
            
            # 연쇄 반응 스택은 전투가 끝나면 절반으로 감소
            if hasattr(member, 'chain_stacks') and member.chain_stacks > 0:
                member.chain_stacks = max(0, member.chain_stacks // 2)
    
    def get_effective_stats(self, character):
        """패시브 효과가 적용된 최종 스탯 계산"""
        base_stats = {
            'physical_attack': character.physical_attack,
            'magic_attack': character.magic_attack,
            'physical_defense': character.physical_defense,
            'magic_defense': character.magic_defense,
            'speed': character.speed,
            'critical_chance': getattr(character, 'critical_chance', 0.05),
            'dodge_chance': getattr(character, 'dodge_chance', 0.05)
        }
        
        # 임시 스탯 부스트 적용 (첫걸음의 용기 등)
        if hasattr(character, 'temp_stat_boost'):
            for stat, boost in character.temp_stat_boost.items():
                if stat in base_stats:
                    base_stats[stat] += boost
        
        # 역학 관계 효과 적용
        if hasattr(character, 'relationship_stacks') and hasattr(character, 'dynamic_relationship'):
            relationship_bonus = character.dynamic_relationship.get('stat_per_death', 0) * character.relationship_stacks
            for stat in ['physical_attack', 'magic_attack', 'physical_defense', 'magic_defense', 'speed']:
                base_stats[stat] = int(base_stats[stat] * (1 + relationship_bonus))
        
        # 미니멀리스트 효과 적용
        minimalist_bonus = self.check_minimalist_bonus(character)
        if minimalist_bonus:
            base_stats['speed'] += minimalist_bonus.get('speed_bonus', 0)
            base_stats['dodge_chance'] += minimalist_bonus.get('dodge_bonus', 0)
        
        # 절대 법칙 효과 적용
        rule_bonuses = self.check_absolute_rule_effects(character)
        if 'critical_chance' in rule_bonuses:
            base_stats['critical_chance'] += rule_bonuses['critical_chance']
        if 'dodge_chance' in rule_bonuses:
            base_stats['dodge_chance'] += rule_bonuses['dodge_chance']
        
        return base_stats
    
    def initialize_passive_runtime_data(self):
        """패시브 효과 런타임 데이터 초기화"""
        for member in self.party_manager.members:
            # 첫걸음의 용기
            if hasattr(member, 'first_battle_boost'):
                member.first_battle_used = False
            
            # 연쇄 반응
            if hasattr(member, 'chain_reaction'):
                member.chain_stacks = 0
            
            # 역학 관계
            if hasattr(member, 'dynamic_relationship'):
                member.relationship_stacks = 0
            
            # 생명 순환
            if hasattr(member, 'life_cycle_effect'):
                member.life_cycle_bonus = 0
            
            # 학자의 지혜
            if hasattr(member, 'scholar_wisdom'):
                member.scholar_stacks = 0
    
    def show_passive_effects_status(self):
        """현재 활성화된 패시브 효과 상태 표시"""
        print("\n" + "="*50)
        print("🌟 활성화된 패시브 효과 상태")
        print("="*50)
        
        for i, member in enumerate(self.party_manager.members, 1):
            effects = []
            
            # 첫걸음의 용기
            if hasattr(member, 'first_battle_boost') and not getattr(member, 'first_battle_used', False):
                effects.append(f"첫걸음의 용기 (대기중)")
            elif hasattr(member, 'first_battle_boost') and getattr(member, 'first_battle_used', False):
                effects.append(f"첫걸음의 용기 (사용됨)")
            
            # 연쇄 반응
            if hasattr(member, 'chain_stacks') and member.chain_stacks > 0:
                effects.append(f"연쇄 반응 x{member.chain_stacks}")
            
            # 역학 관계
            if hasattr(member, 'relationship_stacks') and member.relationship_stacks > 0:
                bonus = member.relationship_stacks * member.dynamic_relationship.get('stat_per_death', 0)
                effects.append(f"역학 관계 (+{bonus*100:.0f}%)")
            
            # 생명 순환
            if hasattr(member, 'life_cycle_bonus') and member.life_cycle_bonus > 0:
                effects.append(f"생명 순환 (+{member.life_cycle_bonus*100:.0f}% 최대HP)")
            
            # 학자의 지혜
            if hasattr(member, 'scholar_stacks') and member.scholar_stacks > 0:
                effects.append(f"학자의 지혜 x{member.scholar_stacks}")
            
            # 미니멀리스트
            minimalist = self.check_minimalist_bonus(member)
            if minimalist:
                effects.append("미니멀리스트 (활성)")
            
            # 절대 법칙들
            rules = self.check_absolute_rule_effects(member)
            if rules:
                for rule_name, bonus in rules.items():
                    effects.append(f"절대 법칙 ({rule_name})")
            
            print(f"{i}. {member.name} ({member.character_class})")
            if effects:
                for effect in effects:
                    print(f"   🔹 {effect}")
            else:
                print("   💤 활성화된 효과 없음")
            print()
    
    def test_passive_effects(self):
        """패시브 효과 테스트 메뉴"""
        while True:
            print("\n" + "="*50)
            print("🧪 패시브 효과 테스트")
            print("="*50)
            print("1. 현재 패시브 상태 확인")
            print("2. 첫걸음의 용기 테스트")
            print("3. 연쇄 반응 테스트")
            print("4. 역학 관계 테스트")
            print("5. 학자의 지혜 테스트")
            print("6. 절대 법칙 테스트")
            print("7. 마나 순환 테스트")
            print("8. 치유의 기운 테스트")
            print("0. 돌아가기")
            
            choice = input("\n선택: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.show_passive_effects_status()
            elif choice == "2":
                # 첫걸음의 용기 테스트
                for member in self.party_manager.members:
                    if hasattr(member, 'first_battle_boost'):
                        result = self.apply_first_battle_boost(member)
                        if result:
                            print(f"✅ {member.name}의 첫걸음의 용기 발동!")
                        else:
                            print(f"❌ {member.name}의 첫걸음의 용기 이미 사용됨")
            elif choice == "3":
                # 연쇄 반응 테스트
                member = self.party_manager.members[0]
                bonus = self.apply_chain_reaction(member, is_critical=True)
                print(f"연쇄 반응 보너스: +{bonus*100:.0f}%")
            elif choice == "4":
                # 역학 관계 테스트 (가상의 사망자)
                if len(self.party_manager.members) > 1:
                    self.apply_dynamic_relationship_effect(self.party_manager.members[0])
                    print("역학 관계 효과 적용 완료")
            elif choice == "5":
                # 학자의 지혜 테스트
                member = self.party_manager.members[0]
                self.apply_scholar_wisdom(member, "test_skill")
                bonus = self.get_scholar_wisdom_bonus(member)
                print(f"학자의 지혜 보너스: {bonus}")
            elif choice == "6":
                # 절대 법칙 테스트
                member = self.party_manager.members[0]
                member.current_hp = 3  # 3의 법칙 테스트
                member.current_mp = 7  # 7의 법칙 테스트
                rules = self.check_absolute_rule_effects(member)
                print(f"절대 법칙 효과: {rules}")
            elif choice == "7":
                # 마나 순환 테스트
                result = self.check_mana_cycle()
                print(f"마나 순환 발동: {'성공' if result else '실패'}")
            elif choice == "8":
                # 치유의 기운 테스트
                self.apply_healing_aura_effects()
                print("치유의 기운 효과 적용 완료")
            
            input("\n계속하려면 Enter를 누르세요...")
    
    def show_party_with_passives(self):
        """패시브 효과가 적용된 파티 상태 표시"""
        print("\n" + "="*60)
        print("👥 파티 상태 (패시브 효과 포함)")
        print("="*60)
        
        for i, member in enumerate(self.party_manager.members, 1):
            base_stats = self.get_effective_stats(member)
            
            print(f"{i}. {member.name} (Lv.{member.level} {member.character_class})")
            print(f"   💚 HP: {member.current_hp}/{member.max_hp}")
            print(f"   💙 MP: {member.current_mp}/{member.max_mp}")
            
            if hasattr(member, 'wounds') and member.wounds > 0:
                print(f"   🩸 상처: {member.wounds}")
            
            print(f"   ⚔️  물리공격: {base_stats['physical_attack']}")
            print(f"   🔮 마법공격: {base_stats['magic_attack']}")
            print(f"   🛡️  물리방어: {base_stats['physical_defense']}")
            print(f"   ✨ 마법방어: {base_stats['magic_defense']}")
            print(f"   💨 속도: {base_stats['speed']}")
            print(f"   💥 치명타율: {base_stats['critical_chance']*100:.1f}%")
            print(f"   🏃 회피율: {base_stats['dodge_chance']*100:.1f}%")
            
            # 활성화된 패시브 효과 표시
            active_effects = []
            if hasattr(member, 'chain_stacks') and member.chain_stacks > 0:
                active_effects.append(f"연쇄반응 x{member.chain_stacks}")
            if hasattr(member, 'relationship_stacks') and member.relationship_stacks > 0:
                active_effects.append(f"역학관계 x{member.relationship_stacks}")
            if hasattr(member, 'scholar_stacks') and member.scholar_stacks > 0:
                active_effects.append(f"학자지혜 x{member.scholar_stacks}")
            
            if active_effects:
                print(f"   🌟 활성효과: {', '.join(active_effects)}")
            
            print()
    
    def save_game(self):
        """게임 저장 (완전한 게임 상태 포함)"""
        if not SAVE_SYSTEM_AVAILABLE:
            print("💾 저장 시스템을 사용할 수 없습니다.")
            return
            
        try:
            import datetime
            from game.save_system import SaveManager
            save_manager = SaveManager()
            
            # 현재 위치 정보 저장
            current_position = {
                'x': getattr(self.party_manager, 'x', 0),
                'y': getattr(self.party_manager, 'y', 0)
            }
            
            # 월드 상태 저장 (맵, 적, 아이템 등)
            world_state = {}
            if hasattr(self, 'world') and self.world:
                world_state = {
                    'current_level': getattr(self.world, 'current_level', 1),
                    'seed': getattr(self.world, 'seed', None),
                    'map_data': None,
                    'explored_tiles': None,
                    'items_on_ground': [],
                    'enemies_positions': [],
                    'room_data': None,
                    'stairs_position': None
                }
                
                # 맵 데이터 저장
                if hasattr(self.world, 'dungeon_map'):
                    # 맵을 직렬화 가능한 형태로 변환
                    if hasattr(self.world.dungeon_map, 'tiles'):
                        world_state['map_data'] = {
                            'width': getattr(self.world.dungeon_map, 'width', 0),
                            'height': getattr(self.world.dungeon_map, 'height', 0),
                            'tiles': self._serialize_map_tiles(self.world.dungeon_map.tiles) if hasattr(self.world.dungeon_map, 'tiles') else []
                        }
                
                # 탐험된 타일 정보 저장 (개선된 시스템)
                try:
                    if hasattr(self.world, 'tiles'):
                        world_state['explored_tiles'] = DawnOfStellarGame.serialize_explored_tiles(self.world)
                        print(f"🗺️ 탐험 정보 저장: {len(world_state['explored_tiles'])}개 타일")
                except Exception as e:
                    print(f"⚠️ 탐험 정보 저장 실패: {e}")
                    world_state['explored_tiles'] = []
                
                # 바닥에 있는 아이템들 저장
                if hasattr(self.world, 'items_on_ground') and self.world.items_on_ground:
                    world_state['items_on_ground'] = [
                        {
                            'x': item.get('x', 0),
                            'y': item.get('y', 0),
                            'item_data': self._serialize_item(item.get('item'))
                        } for item in self.world.items_on_ground
                    ]
                
                # 적 위치 정보 저장
                if hasattr(self.world, 'enemies') and self.world.enemies:
                    world_state['enemies_positions'] = [
                        {
                            'x': enemy.get('x', 0),
                            'y': enemy.get('y', 0),
                            'enemy_data': self._serialize_enemy(enemy.get('enemy'))
                        } for enemy in self.world.enemies
                    ]
                
                # 방 정보 저장
                if hasattr(self.world, 'rooms'):
                    world_state['room_data'] = [
                        {
                            'x': room.x,
                            'y': room.y,
                            'width': room.width,
                            'height': room.height,
                            'room_type': getattr(room, 'room_type', 'normal')
                        } for room in self.world.rooms
                    ] if self.world.rooms else []
                
                # 계단 위치 저장
                if hasattr(self.world, 'stairs_x') and hasattr(self.world, 'stairs_y'):
                    world_state['stairs_position'] = {
                        'x': self.world.stairs_x,
                        'y': self.world.stairs_y
                    }
            
            # 게임 상태 생성 - 확장된 버전
            game_state = {
                'party': [],  # 레거시 호환성
                'party_characters': [],  # 새로운 표준
                'party_passive_effects': getattr(self, 'party_passive_effects', []),
                'world_state': world_state,
                'current_position': current_position,
                'current_floor': getattr(self, 'current_floor', 1),
                'game_statistics': {
                    'score': getattr(self, 'score', 0),
                    'enemies_defeated': getattr(self, 'enemies_defeated', 0),
                    'items_collected': getattr(self, 'items_collected', 0),
                    'floors_cleared': getattr(self, 'floors_cleared', 0),
                    'steps_since_last_encounter': getattr(self, 'steps_since_last_encounter', 0),
                    'step_count': getattr(self, 'step_count', 0)
                },
                # 인카운트 시스템 데이터 추가
                'encounter_data': {
                    'floor_encounter_counts': getattr(self.encounter_manager, 'floor_encounter_counts', {}) if hasattr(self, 'encounter_manager') and self.encounter_manager else {},
                    'total_encounters': sum(getattr(self.encounter_manager, 'floor_encounter_counts', {}).values()) if hasattr(self, 'encounter_manager') and self.encounter_manager else 0,
                    'encounter_types_discovered': getattr(self, 'encounter_types_discovered', []),
                    'enhanced_encounter_data': getattr(self.enhanced_encounter_manager, '_encounter_history', []) if hasattr(self, 'enhanced_encounter_manager') and self.enhanced_encounter_manager else []
                },
                'save_version': '2.2',  # 버전 업그레이드 (인카운트 데이터 포함)
                'difficulty': getattr(self, 'selected_difficulty', self.config.current_difficulty),
                'save_timestamp': datetime.datetime.now().isoformat()
            }
            
            # 파티 멤버 저장 (확장된 정보)
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
                    'brave_points': getattr(member, 'brave_points', 0),
                    'max_brv': getattr(member, 'max_brv', 0),
                    'gold': getattr(member, 'gold', 0),
                    'active_traits': [
                        {'name': trait.name, 'description': trait.description} 
                        for trait in member.active_traits
                    ] if hasattr(member, 'active_traits') else [],
                    'inventory': self._serialize_inventory(member.inventory) if hasattr(member, 'inventory') else [],
                    'equipment': self._serialize_equipment(member) if hasattr(member, 'equipped_weapon') else {},
                    'status_effects': self._serialize_status_effects(member) if hasattr(member, 'status_effects') else []
                }
                game_state['party'].append(member_data)  # 레거시
                game_state['party_characters'].append(member_data)  # 새로운 표준
            
            # 저장 실행
            if save_manager.save_game(game_state):
                print("✅ 게임이 성공적으로 저장되었습니다!")
                print(f"📍 현재 위치: ({current_position['x']}, {current_position['y']})")
                print(f"🏢 현재 층: {world_state.get('current_level', 1)}")
                if world_state.get('seed'):
                    print(f"🎲 맵 시드: {world_state['seed']}")
            else:
                print("❌ 게임 저장에 실패했습니다.")
                
        except Exception as e:
            print(f"❌ 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    def _serialize_map_tiles(self, tiles):
        """맵 타일을 직렬화 가능한 형태로 변환 (탐험 정보 포함)"""
        try:
            if isinstance(tiles, list) and len(tiles) > 0:
                serialized_tiles = []
                for row in tiles:
                    serialized_row = []
                    for tile in row:
                        if hasattr(tile, 'type') and hasattr(tile, 'explored') and hasattr(tile, 'visible'):
                            # Tile 객체인 경우 상세 정보 저장
                            tile_data = {
                                'type': tile.type.value if hasattr(tile.type, 'value') else str(tile.type),
                                'explored': getattr(tile, 'explored', False),
                                'visible': getattr(tile, 'visible', False),
                                'x': getattr(tile, 'x', 0),
                                'y': getattr(tile, 'y', 0),
                                'is_locked': getattr(tile, 'is_locked', False),
                                'is_trapped': getattr(tile, 'is_trapped', False),
                                'trap_detected': getattr(tile, 'trap_detected', False),
                                'is_activated': getattr(tile, 'is_activated', False),
                                'secret_revealed': getattr(tile, 'secret_revealed', False),
                                'required_skill': getattr(tile, 'required_skill', None),
                                'treasure_quality': getattr(tile, 'treasure_quality', 'common')
                            }
                            serialized_row.append(tile_data)
                        else:
                            # 기본 객체인 경우 문자열로 변환
                            serialized_row.append(str(tile))
                    serialized_tiles.append(serialized_row)
                return serialized_tiles
            return []
        except Exception as e:
            print(f"맵 타일 직렬화 오류: {e}")
            return []
    
    def _deserialize_map_tiles(self, serialized_tiles):
        """저장된 타일 데이터를 Tile 객체로 복원"""
        try:
            from game.world import Tile, TileType
            
            restored_tiles = []
            for row_data in serialized_tiles:
                restored_row = []
                for tile_data in row_data:
                    if isinstance(tile_data, dict) and 'type' in tile_data:
                        # TileType enum으로 변환
                        try:
                            tile_type = TileType(tile_data['type'])
                        except ValueError:
                            # 기본값으로 FLOOR 사용
                            tile_type = TileType.FLOOR
                        
                        # Tile 객체 생성
                        tile = Tile(tile_type)
                        
                        # 탐험 정보 복원
                        tile.explored = tile_data.get('explored', False)
                        tile.visible = tile_data.get('visible', False)
                        
                        # 추가 속성들 복원
                        tile.x = tile_data.get('x', 0)
                        tile.y = tile_data.get('y', 0)
                        tile.is_locked = tile_data.get('is_locked', False)
                        tile.is_trapped = tile_data.get('is_trapped', False)
                        tile.trap_detected = tile_data.get('trap_detected', False)
                        tile.is_activated = tile_data.get('is_activated', False)
                        tile.secret_revealed = tile_data.get('secret_revealed', False)
                        tile.required_skill = tile_data.get('required_skill', None)
                        tile.treasure_quality = tile_data.get('treasure_quality', 'common')
                        
                        restored_row.append(tile)
                    else:
                        # 문자열 데이터의 경우 기본 타일로 처리
                        restored_row.append(Tile(TileType.FLOOR))
                restored_tiles.append(restored_row)
            return restored_tiles
        except Exception as e:
            print(f"맵 타일 복원 오류: {e}")
            return []
    
    def _serialize_item(self, item):
        """아이템을 직렬화 가능한 형태로 변환"""
        if not item:
            return None
        try:
            # rarity가 Enum인 경우 문자열로 변환
            rarity_value = getattr(item, 'rarity', 'common')
            if hasattr(rarity_value, 'value'):
                # Enum의 value 속성 사용
                rarity_value = rarity_value.value
            elif hasattr(rarity_value, 'name'):
                # Enum의 name 속성 사용  
                rarity_value = rarity_value.name
            
            return {
                'name': getattr(item, 'name', ''),
                'item_type': getattr(item, 'item_type', ''),
                'description': getattr(item, 'description', ''),
                'effects': getattr(item, 'effects', {}),
                'rarity': rarity_value,
                'value': getattr(item, 'value', 0)
            }
        except Exception as e:
            print(f"아이템 직렬화 오류: {e}")
            return None
    
    def _serialize_enemy(self, enemy):
        """적을 직렬화 가능한 형태로 변환"""
        if not enemy:
            return None
        try:
            return {
                'name': getattr(enemy, 'name', ''),
                'enemy_type': getattr(enemy, 'enemy_type', ''),
                'level': getattr(enemy, 'level', 1),
                'current_hp': getattr(enemy, 'current_hp', 0),
                'max_hp': getattr(enemy, 'max_hp', 1),
                'attack': getattr(enemy, 'attack', 0),
                'defense': getattr(enemy, 'defense', 0),
                'speed': getattr(enemy, 'speed', 0),
                'experience_reward': getattr(enemy, 'experience_reward', 0),
                'gold_reward': getattr(enemy, 'gold_reward', 0),
                'status_effects': getattr(enemy, 'status_effects', [])
            }
        except Exception as e:
            print(f"적 직렬화 오류: {e}")
            return None
    
    def _serialize_inventory(self, inventory):
        """인벤토리를 직렬화 가능한 형태로 변환"""
        if not inventory:
            return []
        try:
            serialized_items = []
            
            # Inventory 객체인 경우 items 속성에서 아이템 목록 가져오기
            if hasattr(inventory, 'items'):
                items_to_serialize = inventory.items
            elif hasattr(inventory, '__iter__'):
                # 리스트나 다른 iterable인 경우
                items_to_serialize = inventory
            else:
                # Inventory 객체지만 items 속성이 없는 경우
                print(f"⚠️ Inventory 객체에 items 속성이 없습니다: {type(inventory)}")
                return []
            
            for item in items_to_serialize:
                serialized_item = self._serialize_item(item)
                if serialized_item:
                    serialized_items.append(serialized_item)
            return serialized_items
        except Exception as e:
            print(f"인벤토리 직렬화 오류: {e}")
            return []
    
    def _serialize_equipment(self, member):
        """장비를 직렬화 가능한 형태로 변환"""
        try:
            equipment = {}
            if hasattr(member, 'equipped_weapon') and member.equipped_weapon:
                equipment['weapon'] = self._serialize_item(member.equipped_weapon)
            if hasattr(member, 'equipped_armor') and member.equipped_armor:
                equipment['armor'] = self._serialize_item(member.equipped_armor)
            if hasattr(member, 'equipped_accessory') and member.equipped_accessory:
                equipment['accessory'] = self._serialize_item(member.equipped_accessory)
            return equipment
        except Exception as e:
            print(f"장비 직렬화 오류: {e}")
            return {}
    
    def _serialize_status_effects(self, member):
        """상태 효과를 직렬화 가능한 형태로 변환"""
        try:
            status_effects = []
            if hasattr(member, 'status_effects') and member.status_effects:
                for effect in member.status_effects:
                    effect_data = {
                        'name': getattr(effect, 'name', ''),
                        'duration': getattr(effect, 'duration', 0),
                        'effect_type': getattr(effect, 'effect_type', ''),
                        'strength': getattr(effect, 'strength', 0),
                        'description': getattr(effect, 'description', '')
                    }
                    status_effects.append(effect_data)
            return status_effects
        except Exception as e:
            print(f"상태 효과 직렬화 오류: {e}")
            return []
    
    def _restore_world_state(self, world_state):
        """월드 상태 복원"""
        try:
            if not world_state:
                print("⚠️ 월드 상태 데이터가 없습니다.")
                return
            
            # 월드 생성 또는 기존 월드 사용
            if not hasattr(self, 'world') or not self.world:
                print("🌍 새로운 월드 인스턴스를 생성합니다...")
                try:
                    from game.world import GameWorld
                    self.world = GameWorld(party_manager=self.party_manager)
                    print("✅ 새 월드 인스턴스 생성 완료")
                except ImportError:
                    print("⚠️ GameWorld 클래스를 불러올 수 없어 월드 복원을 건너뜁니다.")
                    return
                except Exception as e:
                    print(f"⚠️ 월드 생성 중 오류: {e}")
                    return
                
            # 시드 복원
            if 'seed' in world_state and world_state['seed']:
                if hasattr(self.world, 'seed'):
                    self.world.seed = world_state['seed']
                    print(f"🎲 맵 시드 복원: {world_state['seed']}")
            
            # 현재 레벨 복원
            if 'current_level' in world_state:
                if hasattr(self.world, 'current_level'):
                    self.world.current_level = world_state['current_level']
                    print(f"🏢 현재 층 복원: {world_state['current_level']}")
            
            # 맵 데이터 복원
            if 'map_data' in world_state and world_state['map_data']:
                print("🗺️ 맵 데이터 복원 중...")
                self._restore_map_data(world_state['map_data'])
            
            # 탐험된 타일 복원 (개선된 시스템)
            if 'explored_tiles' in world_state and world_state['explored_tiles']:
                print("🗺️ 탐험 정보 복원 중...")
                try:
                    DawnOfStellarGame.restore_explored_tiles(self.world, world_state['explored_tiles'])
                except Exception as e:
                    print(f"⚠️ 탐험 정보 복원 실패: {e}")
                    # 폴백: 기존 방식으로 복원 시도
                    if hasattr(self.world, 'explored'):
                        self.world.explored = set(world_state['explored_tiles'])
                        print(f"🗺️ 기존 방식으로 탐험된 타일 복원: {len(world_state['explored_tiles'])}개")
            
            # 바닥 아이템 복원
            if 'items_on_ground' in world_state and world_state['items_on_ground']:
                print("🎒 바닥 아이템 복원 중...")
                self._restore_items_on_ground(world_state['items_on_ground'])
            
            # 적 위치 복원
            if 'enemies_positions' in world_state and world_state['enemies_positions']:
                print("👹 적 위치 복원 중...")
                self._restore_enemies_positions(world_state['enemies_positions'])
            
            # 방 정보 복원
            if 'room_data' in world_state and world_state['room_data']:
                print("🏠 방 정보 복원 중...")
                self._restore_room_data(world_state['room_data'])
            
            # 계단 위치 복원
            if 'stairs_position' in world_state and world_state['stairs_position']:
                if hasattr(self.world, 'stairs_position'):
                    stairs_pos = world_state['stairs_position']
                    self.world.stairs_position = (stairs_pos.get('x', 0), stairs_pos.get('y', 0))
                    print(f"🪜 계단 위치 복원: {self.world.stairs_position}")
            
            print("✅ 월드 상태 복원 완료")
                
        except Exception as e:
            print(f"⚠️ 월드 상태 복원 중 오류: {e}")
            import traceback
            traceback.print_exc()
            if 'items_on_ground' in world_state and world_state['items_on_ground']:
                self._restore_items_on_ground(world_state['items_on_ground'])
            
            # 적 위치 복원
            if 'enemies_positions' in world_state and world_state['enemies_positions']:
                self._restore_enemies_positions(world_state['enemies_positions'])
            
            # 방 정보 복원
            if 'room_data' in world_state and world_state['room_data']:
                self._restore_room_data(world_state['room_data'])
            
            # 계단 위치 복원
            if 'stairs_position' in world_state and world_state['stairs_position']:
                stairs_pos = world_state['stairs_position']
                if hasattr(self.world, 'stairs_x') and hasattr(self.world, 'stairs_y'):
                    self.world.stairs_x = stairs_pos['x']
                    self.world.stairs_y = stairs_pos['y']
                print(f"🪜 계단 위치 복원: ({stairs_pos['x']}, {stairs_pos['y']})")
            
            # 모든 복원 완료 후 시야 업데이트 강제 실행
            try:
                if hasattr(self.world, 'update_visibility'):
                    self.world.update_visibility()
                    print("👁️ 로드 후 시야 업데이트 완료")
            except Exception as e:
                print(f"⚠️ 시야 업데이트 실패: {e}")
            
        except Exception as e:
            print(f"⚠️ 월드 상태 복원 중 오류: {e}")
    
    def _restore_map_data(self, map_data):
        """맵 데이터 복원"""
        try:
            if not map_data or not hasattr(self, 'world') or not self.world:
                return
            
            if hasattr(self.world, 'dungeon_map') and self.world.dungeon_map:
                if 'width' in map_data:
                    self.world.dungeon_map.width = map_data['width']
                if 'height' in map_data:
                    self.world.dungeon_map.height = map_data['height']
                if 'tiles' in map_data and map_data['tiles']:
                    # 타일 데이터를 적절한 형태로 변환
                    self.world.dungeon_map.tiles = self._deserialize_map_tiles(map_data['tiles'])
                print(f"🗺️ 맵 데이터 복원: {map_data['width']}x{map_data['height']}")
        except Exception as e:
            print(f"⚠️ 맵 데이터 복원 중 오류: {e}")
    
    def _restore_items_on_ground(self, items_data):
        """바닥 아이템 복원"""
        try:
            if not items_data or not hasattr(self, 'world') or not self.world:
                print("⚠️ 바닥 아이템 복원을 위한 조건이 충족되지 않았습니다.")
                return
            
            restored_items = []
            item_count = 0
            
            for item_info in items_data:
                try:
                    x = item_info.get('x', 0)
                    y = item_info.get('y', 0)
                    item_data = item_info.get('item_data')
                    
                    if item_data and item_data.get('name'):
                        # 아이템을 간단한 딕셔너리로 복원
                        restored_item = {
                            'x': x,
                            'y': y,
                            'item': {
                                'name': item_data.get('name', '알 수 없는 아이템'),
                                'item_type': item_data.get('item_type', 'misc'),
                                'description': item_data.get('description', ''),
                                'effects': item_data.get('effects', {}),
                                'rarity': item_data.get('rarity', 'common'),
                                'value': item_data.get('value', 0)
                            }
                        }
                        restored_items.append(restored_item)
                        item_count += 1
                except Exception as item_error:
                    print(f"⚠️ 아이템 복원 중 오류: {item_error}")
                    continue
            
            # 월드에 아이템 목록 설정
            if hasattr(self.world, 'items_on_ground'):
                self.world.items_on_ground = restored_items
                print(f"✅ 바닥 아이템 {item_count}개 복원 완료")
            else:
                # items_on_ground 속성이 없으면 생성
                self.world.items_on_ground = restored_items
                print(f"✅ 바닥 아이템 속성 생성 및 {item_count}개 아이템 복원 완료")
                
        except Exception as e:
            print(f"⚠️ 바닥 아이템 복원 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def _restore_enemies_positions(self, enemies_data):
        """적 위치 복원"""
        try:
            if not enemies_data or not hasattr(self, 'world') or not self.world:
                print("⚠️ 적 위치 복원을 위한 조건이 충족되지 않았습니다.")
                return
            
            restored_enemies = []
            enemy_count = 0
            
            for enemy_info in enemies_data:
                try:
                    # enemy_info가 리스트인 경우 처리
                    if isinstance(enemy_info, list):
                        # 리스트의 첫 번째 요소가 실제 데이터일 가능성
                        if len(enemy_info) > 0:
                            enemy_info = enemy_info[0]
                        else:
                            continue
                    
                    # enemy_info가 여전히 딕셔너리가 아니면 건너뛰기
                    if not isinstance(enemy_info, dict):
                        continue
                    
                    x = enemy_info.get('x', 0)
                    y = enemy_info.get('y', 0)
                    enemy_data = enemy_info.get('enemy_data')
                    
                    if enemy_data and enemy_data.get('name'):
                        # 적을 간단한 딕셔너리로 복원
                        restored_enemy = {
                            'x': x,
                            'y': y,
                            'enemy': {
                                'name': enemy_data.get('name', '알 수 없는 적'),
                                'hp': enemy_data.get('hp', 100),
                                'max_hp': enemy_data.get('max_hp', 100),
                                'mp': enemy_data.get('mp', 50),
                                'max_mp': enemy_data.get('max_mp', 50),
                                'level': enemy_data.get('level', 1),
                                'attack': enemy_data.get('attack', 10),
                                'defense': enemy_data.get('defense', 5),
                                'speed': enemy_data.get('speed', 5),
                                'enemy_type': enemy_data.get('enemy_type', 'normal'),
                                'status_effects': enemy_data.get('status_effects', [])
                            }
                        }
                        restored_enemies.append(restored_enemy)
                        enemy_count += 1
                except Exception as enemy_error:
                    print(f"⚠️ 적 복원 중 오류: {enemy_error}")
                    continue
            
            # 월드에 적 목록 설정
            if hasattr(self.world, 'enemies'):
                self.world.enemies = restored_enemies
                print(f"✅ 적 위치 {enemy_count}개 복원 완료")
            else:
                # enemies 속성이 없으면 생성
                self.world.enemies = restored_enemies
                print(f"✅ 적 속성 생성 및 {enemy_count}개 위치 복원 완료")
                
        except Exception as e:
            print(f"⚠️ 적 위치 복원 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def _restore_room_data(self, room_data):
        """방 정보 복원"""
        try:
            if not room_data or not hasattr(self, 'world') or not self.world:
                print("⚠️ 방 정보 복원을 위한 조건이 충족되지 않았습니다.")
                return
            
            restored_rooms = []
            room_count = 0
            
            for room_info in room_data:
                try:
                    # 방 정보를 딕셔너리로 복원
                    restored_room = {
                        'x': room_info.get('x', 0),
                        'y': room_info.get('y', 0),
                        'width': room_info.get('width', 1),
                        'height': room_info.get('height', 1),
                        'room_type': room_info.get('room_type', 'normal'),
                        'explored': room_info.get('explored', False),
                        'connections': room_info.get('connections', []),
                        'features': room_info.get('features', [])
                    }
                    restored_rooms.append(restored_room)
                    room_count += 1
                except Exception as room_error:
                    print(f"⚠️ 방 복원 중 오류: {room_error}")
                    continue
            
            # 월드에 방 정보 설정
            if hasattr(self.world, 'rooms'):
                self.world.rooms = restored_rooms
                print(f"✅ 방 정보 {room_count}개 복원 완료")
            else:
                # rooms 속성이 없으면 생성
                self.world.rooms = restored_rooms
                print(f"✅ 방 속성 생성 및 {room_count}개 정보 복원 완료")
                
        except Exception as e:
            print(f"⚠️ 방 정보 복원 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def _restore_inventory(self, character, inventory_data):
        """인벤토리 복원"""
        try:
            if not inventory_data or not hasattr(character, 'inventory'):
                return
            
            # 간단한 인벤토리 복원
            # 실제 구현은 게임의 인벤토리 시스템에 따라 달라짐
            for item_data in inventory_data:
                # 아이템 생성 로직 호출
                pass
            print(f"🎒 {character.name} 인벤토리 복원: {len(inventory_data)}개 아이템")
        except Exception as e:
            print(f"⚠️ 인벤토리 복원 중 오류: {e}")
    
    def _restore_equipment(self, character, equipment_data):
        """장비 복원"""
        try:
            if not equipment_data:
                return
            
            # 각 장비 슬롯 복원
            if 'weapon' in equipment_data and equipment_data['weapon']:
                # 무기 복원 로직
                pass
            if 'armor' in equipment_data and equipment_data['armor']:
                # 방어구 복원 로직
                pass
            if 'accessory' in equipment_data and equipment_data['accessory']:
                # 액세서리 복원 로직
                pass
            print(f"⚔️ {character.name} 장비 복원 완료")
        except Exception as e:
            print(f"⚠️ 장비 복원 중 오류: {e}")
    
    def _restore_status_effects(self, character, status_data):
        """상태 효과 복원"""
        try:
            if not status_data or not hasattr(character, 'status_effects'):
                return
            
            # 상태 효과를 딕셔너리 형태로 복원 (기존 시스템과 호환)
            restored_effects = []
            for effect_data in status_data:
                if isinstance(effect_data, dict):
                    # 딕셔너리 형태의 상태 효과로 복원
                    effect = {
                        'name': effect_data.get('name', ''),
                        'duration': effect_data.get('duration', 0),
                        'effect_type': effect_data.get('effect_type', ''),
                        'strength': effect_data.get('strength', 0),
                        'description': effect_data.get('description', '')
                    }
                    restored_effects.append(effect)
                else:
                    # 기존 형태 그대로 사용
                    restored_effects.append(effect_data)
            
            character.status_effects = restored_effects
            print(f"🌟 {character.name} 상태 효과 복원: {len(status_data)}개")
        except Exception as e:
            print(f"⚠️ 상태 효과 복원 중 오류: {e}")
            # 복원 실패 시 빈 리스트로 초기화
            character.status_effects = []
    
    def _restore_traits(self, character, traits_data):
        """특성 복원"""
        try:
            if not traits_data:
                return
            
            character.active_traits = []
            for trait_data in traits_data:
                try:
                    from game.character import CharacterTrait
                    trait = CharacterTrait(
                        trait_data.get('name', ''),
                        trait_data.get('description', ''),
                        "passive",
                        None
                    )
                    character.active_traits.append(trait)
                except Exception as trait_error:
                    print(f"⚠️ 특성 복원 실패: {trait_error}")
                    continue
            print(f"🎯 {character.name} 특성 복원: {len(traits_data)}개")
        except Exception as e:
            print(f"⚠️ 특성 복원 중 오류: {e}")
    
    def _restore_game_stats(self, stats_data):
        """게임 통계 복원"""
        try:
            if not stats_data:
                print("⚠️ 복원할 게임 통계가 없습니다.")
                return
            
            # 게임 통계를 게임 객체에 복원
            stats_count = 0
            
            # 전투 관련 통계
            if 'battles_won' in stats_data:
                if hasattr(self, 'battles_won'):
                    self.battles_won = stats_data['battles_won']
                stats_count += 1
            
            if 'battles_lost' in stats_data:
                if hasattr(self, 'battles_lost'):
                    self.battles_lost = stats_data['battles_lost']
                stats_count += 1
            
            # 경험치 및 레벨 통계
            if 'total_experience_gained' in stats_data:
                if hasattr(self, 'total_experience_gained'):
                    self.total_experience_gained = stats_data['total_experience_gained']
                stats_count += 1
            
            # 탐험 관련 통계
            if 'floors_explored' in stats_data:
                if hasattr(self, 'floors_explored'):
                    self.floors_explored = stats_data['floors_explored']
                stats_count += 1
            
            if 'rooms_visited' in stats_data:
                if hasattr(self, 'rooms_visited'):
                    self.rooms_visited = stats_data['rooms_visited']
                stats_count += 1
            
            # 아이템 관련 통계
            if 'items_collected' in stats_data:
                if hasattr(self, 'items_collected'):
                    self.items_collected = stats_data['items_collected']
                stats_count += 1
            
            # 플레이 시간
            if 'play_time' in stats_data:
                if hasattr(self, 'play_time'):
                    self.play_time = stats_data['play_time']
                stats_count += 1
            
            print(f"✅ 게임 통계 {stats_count}개 항목 복원 완료")
            
        except Exception as e:
            print(f"⚠️ 게임 통계 복원 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def get_auto_battle_status(self):
        """현재 자동전투 상태 확인"""
        try:
            if hasattr(self, 'world') and hasattr(self.world, 'combat_system'):
                return getattr(self.world.combat_system, 'auto_battle', None)
            return None
        except Exception:
            return None
    
    def toggle_auto_battle(self):
        """자동전투 모드 토글"""
        try:
            # 여러 경로로 전투 시스템 찾기
            combat_system = None
            
            # 1. world.combat_system 확인
            if hasattr(self, 'world') and hasattr(self.world, 'combat_system'):
                combat_system = self.world.combat_system
            # 2. brave_combat_system 확인
            elif hasattr(self, 'brave_combat_system') and self.brave_combat_system:
                combat_system = self.brave_combat_system
            # 3. 전투 시스템 임시 생성
            else:
                from game.brave_combat import BraveCombatSystem
                combat_system = BraveCombatSystem(self.audio_system, self.audio_system)
                self.brave_combat_system = combat_system
                print(f"{bright_yellow('💡 전투 시스템을 새로 초기화했습니다.')}")
            
            if combat_system:
                current_status = getattr(combat_system, 'auto_battle', False)
                new_status = not current_status
                combat_system.auto_battle = new_status
                
                # 상태 메시지 출력
                status_text = "🟢 켜짐" if new_status else "🔴 꺼짐"
                status_emoji = "⚡🔥" if new_status else "🛑"
                
                print(f"\n{bright_cyan('═══════════════════════════════════')}")
                print(f"{bright_white('        ⚡ 자동전투 설정 변경 ⚡')}")
                print(f"{bright_cyan('═══════════════════════════════════')}")
                print(f"{bright_yellow(f'  상태: {status_text} {status_emoji}')}")
                
                if new_status:
                    print(f"{bright_green('  💡 이제 전투가 자동으로 진행됩니다!')}")
                    print(f"{bright_cyan('  🔄 전투 속도가 향상되어 빠르게 진행됩니다.')}")
                    print(f"{bright_white('  ⚠️ 전투 중에도 수동으로 변경 가능합니다.')}")
                else:
                    print(f"{bright_white('  🎮 이제 전투를 수동으로 조작합니다.')}")
                    print(f"{bright_cyan('  🤔 각 행동을 직접 선택할 수 있습니다.')}")
                
                print(f"{bright_cyan('═══════════════════════════════════')}")
                self.keyboard.wait_for_key("🔑 아무 키나 눌러 계속...")
                
            else:
                print(f"\n{bright_red('❌ 전투 시스템을 찾을 수 없습니다.')}")
                print("게임이 아직 완전히 초기화되지 않았을 수 있습니다.")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"\n{bright_red('❌ 자동전투 설정 변경 중 오류 발생:')}")
            print(f"오류 내용: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def show_ai_mode_settings(self):
        """AI 모드 설정 화면"""
        try:
            from game.ai_game_mode import ai_game_mode_manager
            from game.party_item_sharing import party_item_sharing, ItemSharingPermission
            from game.cursor_menu_system import CursorMenu
            
            print(f"\n{bright_cyan('═══════════════════════════════════')}")
            print(f"{bright_white('        🤖 AI 게임모드 설정 🤖')}")
            print(f"{bright_cyan('═══════════════════════════════════')}")
            
            # 현재 상태 표시
            print(ai_game_mode_manager.get_ai_mode_status())
            print()
            print(party_item_sharing.get_sharing_status())
            
            # 커서 메뉴 시스템 사용
            try:
                menu = CursorMenu(
                    title="🤖 AI 게임모드 설정",
                    options=[
                        "🔧 아이템 공유 권한 변경",
                        "📊 AI 상태 확인",
                        "📋 아이템 사용 통계",
                        "🔄 AI 신뢰도 조정",
                        "⬅️ 돌아가기"
                    ],
                    descriptions=[
                        "AI 동료들의 아이템 사용 권한을 설정합니다",
                        "현재 AI 동료들의 상태와 성능을 확인합니다",
                        "AI가 사용한 아이템의 통계를 확인합니다",
                        "AI 동료들과의 신뢰도를 조정합니다",
                        "이전 메뉴로 돌아갑니다"
                    ],
                    audio_manager=getattr(self, 'audio_manager', None)
                )
                
                choice = menu.run()
                if choice is not None:
                    if choice == 0:  # 아이템 공유 권한 변경
                        self._change_item_sharing_permission()
                    elif choice == 1:  # AI 상태 확인
                        self.show_ai_status()
                    elif choice == 2:  # 아이템 사용 통계
                        party_item_sharing.show_usage_statistics()
                        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                    elif choice == 3:  # AI 신뢰도 조정
                        self._adjust_ai_trust()
                    elif choice == 4:  # 돌아가기
                        return
                else:
                    return  # 취소
                    
            except ImportError:
                # 폴백: 기존 텍스트 기반 메뉴
                print(f"\n{bright_yellow('설정 옵션:')}")
                print("1. 🔧 아이템 공유 권한 변경")
                print("2. 📊 AI 상태 확인")  
                print("3. 📋 아이템 사용 통계")
                print("4. 🔄 AI 신뢰도 조정")
                print("5. ⬅️ 돌아가기")
                
                choice = input("\n선택: ")
                
                if choice == '1':
                    self._change_item_sharing_permission()
                elif choice == '2':
                    self.show_ai_status()
                elif choice == '3':
                    party_item_sharing.show_usage_statistics()
                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                elif choice == '4':
                    self._adjust_ai_trust()
                elif choice == '5':
                    return
                else:
                    print("❌ 잘못된 선택입니다.")
                    self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"❌ AI 설정 화면 오류: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def _change_item_sharing_permission(self):
        """아이템 공유 권한 변경 - 커서 메뉴 방식"""
        from game.party_item_sharing import party_item_sharing, ItemSharingPermission
        
        try:
            from game.cursor_menu_system import CursorMenu
            
            # 현재 권한 상태 확인
            current_permission = party_item_sharing.sharing_permission
            permission_names = {
                ItemSharingPermission.FULL_ACCESS: "🔓 전체 접근 허용",
                ItemSharingPermission.LIMITED_ACCESS: "🔒 제한적 접근", 
                ItemSharingPermission.ASK_PERMISSION: "🤔 사용 전 확인",
                ItemSharingPermission.NO_ACCESS: "🚫 사용 금지"
            }
            
            current_status = permission_names.get(current_permission, "알 수 없음")
            
            # 메뉴 옵션
            options = [
                "🔓 전체 접근 허용 (모든 아이템 자유 사용)",
                "🔒 제한적 접근 (치료/회복 아이템만) ⭐ 추천",
                "🤔 사용 전 확인 (항상 허가 요청)",
                "🚫 사용 금지 (AI가 아이템 사용 불가)"
            ]
            
            descriptions = [
                "AI가 모든 아이템을 자유롭게 사용할 수 있습니다. 전투가 빨라지지만 아이템 관리에 주의가 필요합니다.",
                "AI가 치료 포션, 회복 아이템 등 기본적인 아이템만 사용합니다. 균형 잡힌 설정입니다.",
                "AI가 아이템 사용 전 항상 허가를 요청합니다. 완전한 통제가 가능하지만 전투가 느려질 수 있습니다.",
                "AI가 어떤 아이템도 사용할 수 없습니다. 모든 아이템을 직접 관리해야 합니다."
            ]
            
            # 커서 메뉴 생성
            menu = CursorMenu(
                title=f"🤖 AI 아이템 공유 권한 설정\n현재 설정: {current_status}",
                options=options,
                descriptions=descriptions,
                cancellable=True,
                audio_manager=getattr(self, 'audio_manager', None),
                keyboard=self.keyboard
            )
            
            choice = menu.run()
            
            if choice is not None and choice != -1:
                permission_map = [
                    ItemSharingPermission.FULL_ACCESS,
                    ItemSharingPermission.LIMITED_ACCESS,  
                    ItemSharingPermission.ASK_PERMISSION,
                    ItemSharingPermission.NO_ACCESS
                ]
                
                old_permission = current_permission
                new_permission = permission_map[choice]
                party_item_sharing.set_sharing_permission(new_permission)
                
                # 결과 표시
                print(f"\n{bright_cyan('='*50)}")
                print(f"{bright_white('🤖 아이템 공유 권한 변경 완료 🤖')}")
                print(f"{bright_cyan('='*50)}")
                print(f"이전 설정: {permission_names.get(old_permission, '알 수 없음')}")
                print(f"새 설정: {bright_green(permission_names.get(new_permission, '알 수 없음'))}")
                
                if new_permission == ItemSharingPermission.LIMITED_ACCESS:
                    print(f"\n✅ {bright_green('추천 설정이 적용되었습니다!')}")
                    print("AI가 치료/회복 아이템만 사용하며 균형 잡힌 플레이가 가능합니다.")
                elif new_permission == ItemSharingPermission.FULL_ACCESS:
                    print(f"\n⚡ {bright_yellow('주의: AI가 모든 아이템을 사용할 수 있습니다!')}")
                    print("아이템 소모량을 주의 깊게 관찰하세요.")
                elif new_permission == ItemSharingPermission.ASK_PERMISSION:
                    print(f"\n🤔 {bright_cyan('AI가 사용 전 항상 허가를 요청합니다.')}")
                    print("전투 중 아이템 사용 확인창이 자주 나타날 수 있습니다.")
                else:
                    print(f"\n🚫 {bright_red('AI 아이템 사용이 완전히 금지되었습니다.')}")
                    print("모든 아이템을 직접 관리해야 합니다.")
                
                print(f"{bright_cyan('='*50)}")
                
        except ImportError:
            # 폴백: 기존 텍스트 기반 메뉴
            print("⚠️ 커서 메뉴 시스템을 사용할 수 없어 기본 메뉴를 사용합니다.")
            
            print(f"\n{bright_yellow('아이템 공유 권한 설정:')}")
            print("1. 🔓 전체 접근 허용 (모든 아이템 자유 사용)")
            print("2. 🔒 제한적 접근 (치료/회복 아이템만)")
            print("3. 🤔 사용 전 확인 (항상 허가 요청)")
            print("4. 🚫 사용 금지")
            
            choice = input("선택: ")
            permission_map = {
                '1': ItemSharingPermission.FULL_ACCESS,
                '2': ItemSharingPermission.LIMITED_ACCESS,  
                '3': ItemSharingPermission.ASK_PERMISSION,
                '4': ItemSharingPermission.NO_ACCESS
            }
            
            if choice in permission_map:
                party_item_sharing.set_sharing_permission(permission_map[choice])
                print("✅ 권한이 변경되었습니다.")
            else:
                print("❌ 잘못된 선택입니다.")
        
        except Exception as e:
            print(f"❌ 아이템 공유 권한 변경 오류: {e}")
        
        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def _adjust_ai_trust(self):
        """AI 신뢰도 조정 - 커서 메뉴 방식"""
        from game.ai_game_mode import ai_game_mode_manager
        
        if not ai_game_mode_manager.ai_companions:
            print("❌ AI 동료가 없습니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            return
        
        try:
            from game.cursor_menu_system import CursorMenu
            
            # AI 동료 목록 생성
            options = []
            descriptions = []
            
            for ai_companion in ai_game_mode_manager.ai_companions:
                char = ai_companion.character
                trust_level = ai_companion.trust_level
                
                # 신뢰도에 따른 상태 표시
                if trust_level >= 80:
                    trust_status = f"{bright_green('매우 높음')} 🌟"
                elif trust_level >= 60:
                    trust_status = f"{bright_cyan('높음')} ⭐"
                elif trust_level >= 40:
                    trust_status = f"{bright_yellow('보통')} ✨"
                elif trust_level >= 20:
                    trust_status = f"{yellow('낮음')} ⚠️"
                else:
                    trust_status = f"{bright_red('매우 낮음')} ❌"
                
                option = f"🤖 {bright_white(char.name)} (신뢰도: {trust_level}/100 - {trust_status})"
                options.append(option)
                
                # 신뢰도에 따른 설명
                personality = getattr(ai_companion, 'personality_type', '알 수 없음')
                description = f"직업: {char.character_class} | 성격: {personality}\n현재 신뢰도: {trust_level}/100\n"
                
                if trust_level >= 80:
                    description += "🌟 완전히 신뢰하며 최고의 성능을 발휘합니다"
                elif trust_level >= 60:
                    description += "⭐ 높은 신뢰도로 안정적인 협력이 가능합니다"
                elif trust_level >= 40:
                    description += "✨ 보통 수준의 협력 관계입니다"
                elif trust_level >= 20:
                    description += "⚠️ 신뢰도가 낮아 가끔 실수할 수 있습니다"
                else:
                    description += "❌ 매우 낮은 신뢰도로 협력에 어려움이 있습니다"
                
                descriptions.append(description)
            
            # 커서 메뉴 생성 및 실행
            menu = CursorMenu(
                title=f"{bright_white('🤖 AI 신뢰도 조정 🤖')}",
                options=options,
                descriptions=descriptions,
                cancellable=True,
                audio_manager=getattr(self, 'audio_manager', None),
                keyboard=self.keyboard
            )
            
            choice = menu.run()
            
            if choice is None or choice == -1:  # 취소
                return
            
            # 선택된 AI 동료
            selected_ai = ai_game_mode_manager.ai_companions[choice]
            
            # 신뢰도 조정 옵션 메뉴
            adjust_options = [
                f"👍 {bright_green('칭찬하기')} (+10 신뢰도)",
                f"😊 {bright_cyan('격려하기')} (+5 신뢰도)",
                f"😐 {bright_yellow('현재 상태 유지')} (±0)",
                f"😕 {yellow('주의주기')} (-5 신뢰도)",
                f"😠 {bright_red('질책하기')} (-10 신뢰도)"
            ]
            
            adjust_descriptions = [
                "AI의 행동을 크게 칭찬합니다. 신뢰도가 10 증가합니다.",
                "AI를 격려하고 응원합니다. 신뢰도가 5 증가합니다.",
                "특별한 조치 없이 현재 상태를 유지합니다.",
                "AI의 행동에 대해 가벼운 주의를 줍니다. 신뢰도가 5 감소합니다.",
                "AI의 행동을 강하게 질책합니다. 신뢰도가 10 감소합니다."
            ]
            
            adjust_menu = CursorMenu(
                title=f"🤖 {selected_ai.character.name} 신뢰도 조정\n현재 신뢰도: {selected_ai.trust_level}/100",
                options=adjust_options,
                descriptions=adjust_descriptions,
                cancellable=True,
                audio_manager=getattr(self, 'audio_manager', None),
                keyboard=self.keyboard
            )
            
            adjust_choice = adjust_menu.run()
            
            if adjust_choice is None or adjust_choice == -1:  # 취소
                return
            
            # 신뢰도 조정 적용
            adjustments = [10, 5, 0, -5, -10]
            adjustment = adjustments[adjust_choice]
            
            old_trust = selected_ai.trust_level
            selected_ai.trust_level = max(0, min(100, selected_ai.trust_level + adjustment))
            
            # 결과 출력
            print(f"\n{bright_cyan('='*50)}")
            print(f"{bright_white('🤖 신뢰도 조정 결과 🤖')}")
            print(f"{bright_cyan('='*50)}")
            print(f"대상: {bright_white(selected_ai.character.name)}")
            print(f"이전: {old_trust}/100")
            print(f"현재: {bright_cyan(str(selected_ai.trust_level))}/100")
            
            if adjustment > 0:
                print(f"변화: {bright_green(f'+{adjustment}')} ⬆️")
            elif adjustment < 0:
                print(f"변화: {bright_red(str(adjustment))} ⬇️")
            else:
                print(f"변화: {bright_yellow('변화 없음')} ➡️")
            
            # 신뢰도 레벨에 따른 메시지
            if selected_ai.trust_level >= 80:
                print(f"\n🌟 {selected_ai.character.name}이(가) 당신을 완전히 신뢰합니다!")
            elif selected_ai.trust_level >= 60:
                print(f"\n⭐ {selected_ai.character.name}이(가) 당신을 높게 신뢰합니다!")
            elif selected_ai.trust_level >= 40:
                print(f"\n✨ {selected_ai.character.name}과(와) 보통 수준의 신뢰 관계입니다.")
            elif selected_ai.trust_level >= 20:
                print(f"\n⚠️ {selected_ai.character.name}이(가) 당신을 의심스러워합니다...")
            else:
                print(f"\n❌ {selected_ai.character.name}이(가) 당신을 거의 신뢰하지 않습니다!")
            
            print(f"{bright_cyan('='*50)}")
            
        except ImportError:
            # 폴백: 기존 텍스트 메뉴 방식
            print("⚠️ 커서 메뉴 시스템을 사용할 수 없어 기본 메뉴를 사용합니다.")
            
            print(f"\n{bright_yellow('AI 신뢰도 조정:')}")
            for i, ai_companion in enumerate(ai_game_mode_manager.ai_companions, 1):
                print(f"{i}. {ai_companion.character.name} (신뢰도: {ai_companion.trust_level}/100)")
            
            try:
                choice = int(input("조정할 AI 선택: ")) - 1
                if 0 <= choice < len(ai_game_mode_manager.ai_companions):
                    ai_companion = ai_game_mode_manager.ai_companions[choice]
                    
                    print(f"\n{ai_companion.character.name}의 신뢰도 조정:")
                    print("1. +10 (칭찬)")
                    print("2. +5 (격려)")
                    print("3. -5 (주의)")
                    print("4. -10 (질책)")
                    
                    adjust_choice = input("선택: ")
                    adjustments = {'1': 10, '2': 5, '3': -5, '4': -10}
                    
                    if adjust_choice in adjustments:
                        adjustment = adjustments[adjust_choice]
                        ai_companion.trust_level = max(0, min(100, ai_companion.trust_level + adjustment))
                        print(f"✅ {ai_companion.character.name}의 신뢰도가 {ai_companion.trust_level}/100으로 조정되었습니다.")
                    else:
                        print("❌ 잘못된 선택입니다.")
                else:
                    print("❌ 잘못된 AI 선택입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
        
        except Exception as e:
            print(f"❌ AI 신뢰도 조정 오류: {e}")
        
        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def handle_ai_requests(self):
        """AI 요청 처리"""
        try:
            from game.party_item_sharing import party_item_sharing
            
            if party_item_sharing.handle_pending_requests():
                print("✅ AI 요청 처리가 완료되었습니다.")
            else:
                print("❌ 처리할 AI 요청이 없습니다.")
            
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"❌ AI 요청 처리 오류: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def show_ai_status(self):
        """AI 상태 확인"""
        try:
            from game.ai_game_mode import ai_game_mode_manager
            from game.party_item_sharing import party_item_sharing
            
            print(f"\n{bright_cyan('═══════════════════════════════════')}")
            print(f"{bright_white('        🤖 AI 동료 상태 🤖')}")
            print(f"{bright_cyan('═══════════════════════════════════')}")
            
            if not ai_game_mode_manager.ai_companions:
                print("❌ AI 동료가 없습니다.")
            else:
                for ai_companion in ai_game_mode_manager.ai_companions:
                    char = ai_companion.character
                    print(f"\n🤖 {char.name} ({char.character_class})")
                    print(f"   레벨: {char.level}")
                    print(f"   HP: {char.current_hp}/{char.max_hp}")
                    print(f"   MP: {char.current_mp}/{char.max_mp}")
                    print(f"   성격: {ai_companion.personality.value}")
                    print(f"   신뢰도: {ai_companion.trust_level}/100")
                    print(f"   사기: {ai_companion.morale}/100")
                    
                    if ai_companion.coordinated_attack_ready:
                        print(f"   ⚡ 협동 공격 준비 완료!")
            
            print(f"\n{bright_yellow('아이템 공유 현황:')}")
            party_item_sharing._show_shared_inventory()
            
            print(f"\n{bright_cyan('═══════════════════════════════════')}")
            self.keyboard.wait_for_key("🔑 아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"❌ AI 상태 확인 오류: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
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
            
            # 개선된 저장 파일 목록 사용
            saves = save_manager.list_saves()
            
            if not saves:
                print("❌ 저장된 게임이 없습니다.")
                input("확인하려면 Enter를 누르세요...")
                return False
            
            # 저장 파일 선택 UI (개선된 버전)
            print("\n📁 저장된 게임 목록:")
            print("=" * 80)
            for i, save_info in enumerate(saves, 1):
                filename = save_info.get('filename', '알 수 없음')
                save_name = save_info.get('save_name', filename)
                save_time = save_info.get('save_time', '알 수 없음')
                level = save_info.get('level', '?')
                party_names = save_info.get('party_names', [])
                
                # 시간 형식 개선
                if save_time != '알 수 없음' and isinstance(save_time, str):
                    try:
                        from datetime import datetime
                        # ISO 형식을 사용자 친화적으로 변환
                        if 'T' in save_time:
                            dt = datetime.fromisoformat(save_time.replace('Z', '+00:00'))
                            save_time = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                # 파티 정보 구성
                if party_names:
                    party_info = f"{party_names[0]} Lv.{level} (파티 {len(party_names)}명)"
                else:
                    party_info = f"Lv.{level} (파티 정보 불완전)"
                
                print(f"{i}. 💾 {save_name}")
                print(f"   {party_info} - {save_time}")
            print("=" * 80)
            print("불러올 세이브 파일을 선택하세요...")
            
            choice = input("\n불러올 저장 파일 번호: ").strip()
            
            try:
                save_index = int(choice) - 1
                
                if 0 <= save_index < len(saves):
                    import os  # os 모듈 import 추가
                    save_info = saves[save_index]
                    
                    # save_info에서 파일명 추출
                    save_filename = save_info.get('filename', '')
                    if not save_filename:
                        print("❌ 유효한 저장 파일 정보를 찾을 수 없습니다.")
                        input("확인하려면 Enter를 누르세요...")
                        return False
                    
                    print(f"\n💾 {save_filename} 로딩 중...")
                    
                    # 파일명으로 게임 로드
                    game_state = save_manager.load_game(save_filename)
                    
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
            
            # 난이도 설정 복원
            if 'difficulty' in game_state:
                difficulty = game_state['difficulty']
                self.config.set_difficulty(difficulty)
                self.selected_difficulty = difficulty
                print(f"🎯 난이도 설정 복원: {difficulty}")
            else:
                # 기존 세이브 파일의 경우 기본 난이도 사용
                self.selected_difficulty = self.config.current_difficulty
                print(f"🎯 기본 난이도 적용: {self.selected_difficulty}")
            
            # 파티 복원 - 올바른 키 이름 사용
            self.party_manager.members.clear()
            party_data = game_state.get('party_characters', game_state.get('party', []))
            
            if not party_data:
                print("❌ 저장된 파티 정보가 없습니다.")
                return False
            
            restored_count = 0
            for member_data in party_data:
                # Character.from_dict를 사용하여 캐릭터 복원
                try:
                    # Character 클래스 임포트
                    from game.character import Character
                    
                    # from_dict 메서드 존재 확인
                    if not hasattr(Character, 'from_dict'):
                        print(f"⚠️ Character 클래스에 from_dict 메서드가 없습니다.")
                        # 대안: 수동으로 캐릭터 생성 (클래스 수정자 스킵)
                        character = Character(
                            name=member_data.get('name', '알 수 없는 캐릭터'),
                            character_class=member_data.get('character_class', '전사'),
                            max_hp=member_data.get('max_hp', 100),
                            physical_attack=member_data.get('physical_attack', 10),
                            magic_attack=member_data.get('magic_attack', 10),
                            physical_defense=member_data.get('physical_defense', 10),
                            magic_defense=member_data.get('magic_defense', 10),
                            speed=member_data.get('speed', 10),
                            skip_class_modifiers=True
                        )
                        # 추가 속성들 수동 복원
                        character.current_hp = member_data.get('current_hp', character.max_hp)
                        character.current_mp = member_data.get('current_mp', character.max_mp)
                        character.level = member_data.get('level', 1)
                        character.experience = member_data.get('experience', 0)
                        print(f"✅ {character.name} 수동 복원 완료")
                    else:
                        # 정상적인 from_dict 사용
                        character = Character.from_dict(member_data)
                        print(f"✅ {character.name} Character.from_dict로 복원 완료")
                    
                    self.party_manager.add_member(character)
                    restored_count += 1
                    
                    # 복원 상세 정보 출력
                    inventory_count = len(character.inventory.items) if hasattr(character, 'inventory') and character.inventory else 0
                    equipped_count = sum(1 for eq in [getattr(character, 'equipped_weapon', None), 
                                                    getattr(character, 'equipped_armor', None), 
                                                    getattr(character, 'equipped_accessory', None)] if eq is not None)
                    print(f"✅ {character.name} 복원 완료 - 인벤토리: {inventory_count}개, 장비: {equipped_count}개")
                    
                except Exception as e:
                    print(f"❌ 캐릭터 복원 중 오류: {e}")
                    import traceback
                    traceback.print_exc()
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
            
            # 파티 골드 복원
            if 'party_gold' in game_state:
                self.party_manager.party_gold = game_state['party_gold']
                self.gold = game_state['party_gold']  # 게임 클래스 골드도 동기화
                print(f"💰 파티 골드 복원: {self.party_manager.party_gold}G")
            
            # 파티 공용 인벤토리 복원
            if 'party_shared_inventory' in game_state and game_state['party_shared_inventory']:
                try:
                    from game.items import Inventory
                    shared_inv_data = game_state['party_shared_inventory']
                    self.party_manager.shared_inventory = Inventory(
                        max_size=shared_inv_data.get('max_size', 100),
                        max_weight=shared_inv_data.get('max_weight', 500.0)
                    )
                    if 'items' in shared_inv_data:
                        self.party_manager.shared_inventory.items = shared_inv_data['items'].copy()
                    print(f"📦 공용 인벤토리 복원: {len(shared_inv_data.get('items', {}))}개 아이템")
                except Exception as inv_error:
                    print(f"⚠️ 공용 인벤토리 복원 실패: {inv_error}")
            
            # 파티 걸음 수 복원
            if 'party_total_steps' in game_state:
                self.party_manager.total_steps = game_state['party_total_steps']
                print(f"👣 파티 걸음 수 복원: {self.party_manager.total_steps}걸음")
            
            # 🌍 월드 상태 복원 (맵, 아이템, 적 등)
            world_state = game_state.get('world_state', {})
            if world_state:
                print(f"🌍 월드 상태 복원을 시작합니다...")
                try:
                    self._restore_world_state(world_state)
                    print("✅ 월드 상태 복원 완료")
                except Exception as world_error:
                    print(f"⚠️ 월드 상태 복원 중 오류: {world_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print("⚠️ 저장된 월드 상태가 없습니다. 새 맵이 생성됩니다.")
            
            # 현재 위치 복원
            current_position = game_state.get('current_position', {})
            if current_position:
                x = current_position.get('x', 0)
                y = current_position.get('y', 0)
                if hasattr(self.party_manager, 'x'):
                    self.party_manager.x = x
                    self.party_manager.y = y
                    print(f"📍 파티 위치 복원: ({x}, {y})")
            
            # 현재 층수 복원
            if 'current_floor' in game_state:
                self.current_floor = game_state['current_floor']
                print(f"🏢 현재 층수 복원: {self.current_floor}층")
            
            # 게임 통계 복원
            game_statistics = game_state.get('game_statistics', {})
            if game_statistics:
                self.score = game_statistics.get('score', 0)
                self.enemies_defeated = game_statistics.get('enemies_defeated', 0)
                self.items_collected = game_statistics.get('items_collected', 0)
                self.floors_cleared = game_statistics.get('floors_cleared', 0)
                self.steps_since_last_encounter = game_statistics.get('steps_since_last_encounter', 0)
                self.step_count = game_statistics.get('step_count', 0)
                print(f"📊 게임 통계 복원: 점수 {self.score}, 처치 {self.enemies_defeated}마리")
            
            # 🎲 인카운트 데이터 복원 (새로운 기능)
            encounter_data = game_state.get('encounter_data', {})
            if encounter_data:
                print("🎲 인카운트 데이터 복원 중...")
                
                # 층별 인카운트 횟수 복원
                if hasattr(self, 'encounter_manager') and self.encounter_manager:
                    floor_counts = encounter_data.get('floor_encounter_counts', {})
                    if floor_counts:
                        # 문자열 키를 정수로 변환
                        self.encounter_manager.floor_encounter_counts = {
                            int(k): v for k, v in floor_counts.items()
                        }
                        total_encounters = encounter_data.get('total_encounters', 0)
                        print(f"   📈 인카운트 횟수 복원: {len(floor_counts)}개 층, 총 {total_encounters}회")
                
                # 발견한 인카운트 타입들 복원
                encounter_types = encounter_data.get('encounter_types_discovered', [])
                if encounter_types:
                    self.encounter_types_discovered = encounter_types
                    print(f"   🔍 발견한 인카운트 타입: {len(encounter_types)}가지")
                
                # 강화된 인카운트 히스토리 복원
                if hasattr(self, 'enhanced_encounter_manager') and self.enhanced_encounter_manager:
                    enhanced_history = encounter_data.get('enhanced_encounter_data', [])
                    if enhanced_history:
                        self.enhanced_encounter_manager._encounter_history = enhanced_history
                        # print(f"   ✨ 강화된 인카운트 히스토리: {len(enhanced_history)}개 기록")  # 숨김
                
                print("✅ 인카운트 데이터 복원 완료")
                self.enemies_defeated = game_statistics.get('enemies_defeated', 0)
                self.items_collected = game_statistics.get('items_collected', 0)
                self.floors_cleared = game_statistics.get('floors_cleared', 0)
                self.steps_since_last_encounter = game_statistics.get('steps_since_last_encounter', 0)
                self.gathering_cooldown = game_statistics.get('gathering_cooldown', 0)
                self.steps_since_last_gather = game_statistics.get('steps_since_last_gather', 0)
                self.random_encounters_this_floor = game_statistics.get('random_encounters_this_floor', 0)
                self.step_count = game_statistics.get('step_count', 0)
                print(f"📊 게임 통계 복원: 점수 {self.score}, 처치 {self.enemies_defeated}, 층 {self.floors_cleared}")
            
            print(f"✅ 게임 상태 복원 완료 ({restored_count}명의 캐릭터)")
            for i, member in enumerate(self.party_manager.members, 1):
                inventory_count = len(member.inventory.items) if hasattr(member, 'inventory') and member.inventory else 0
                equipped_count = sum(1 for eq in [getattr(member, 'equipped_weapon', None), 
                                                getattr(member, 'equipped_armor', None), 
                                                getattr(member, 'equipped_accessory', None)] if eq is not None)
                print(f"     {i}. {member.name} (Lv.{member.level}, {member.character_class}) - 인벤토리: {inventory_count}개, 장비: {equipped_count}개")
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
                
                # 🎵 파티 생성 완료 후 모험 준비 BGM (글리치 모드에서는 차단)
                if hasattr(self, 'sound_manager') and self.sound_manager:
                    # 강제 글리치 모드 체크
                    if hasattr(self, '_force_glitch_mode') and self._force_glitch_mode:
                        print("🔇 [BGM BLOCKED] Force glitch mode active - Prelude BGM denied")
                    else:
                        # 일반 글리치 모드 체크
                        try:
                            if hasattr(self, 'story_system') and self.story_system:
                                if hasattr(self.story_system, 'is_glitch_mode') and self.story_system.is_glitch_mode():
                                    print("🔇 [BGM BLOCKED] Glitch mode active - Prelude BGM denied")
                                else:
                                    self.sound_manager.play_bgm("prelude", loop=True)
                            else:
                                self.sound_manager.play_bgm("prelude", loop=True)
                        except:
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
        
        # 🎵 파티 준비 BGM 없이 조용히 진행
        
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
        # print(f"\n{bright_cyan('🌟 모험을 시작합니다!', True)}")  # 메시지 제거
        
        # 영구 성장 보너스 적용
        self.apply_permanent_bonuses()
        
        # 🎵 메인 메뉴 BGM 정지 후 던전 테마 BGM 시작
        # print("🎵 던전 BGM을 시작합니다...")  # 메시지 제거
        try:
            # 먼저 현재 BGM 완전 정지
            if hasattr(self, 'audio_system') and self.audio_system:
                import pygame
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()  # 메모리에서 완전 해제
            
            # 잠시 대기 후 던전 BGM 시작
            import time
            time.sleep(0.1)  # 100ms 대기
            
            # 초기 던전 BGM 설정
            self.safe_play_bgm("dungeon", loop=True)
            # print(f"✅ BGM 재생 중: dungeon (1층 던전)")  # 메시지 제거
        except Exception as e:
            # print(f"⚠️ BGM 재생 실패: {e}")  # 메시지 제거
            pass
        
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
            "암흑기사": "🌑",
            "몽크": "👊",
            "바드": "🎵",
            "네크로맨서": "💀",
            "용기사": "🐉",
            "검성": "⚡",
            "정령술사": "🌟",
            "암살자": "🔪",
            "기계공학자": "🔧",
            "무당": "🔯",
            "해적": "🏴‍☠️",
            "사무라이": "🗾",
            "드루이드": "🌿",
            "철학자": "🧠",
            "시간술사": "⏰",
            "연금술사": "⚗️",
            "검투사": "🏛️",
            "기사": "🐎",
            "신관": "✨",
            "마검사": "🗡️",
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
        
    def start_adventure(self, skip_passive_selection=False, skip_ai_mode_selection=False):
        """모험 시작 - AI 게임모드 선택 포함"""
        # print(f"\n{bright_cyan('🌟 모험을 시작합니다!', True)}")  # 메시지 제거
        
        # 게임 로드 시에는 AI 모드 선택 건너뛰기 (저장된 설정 사용)
        if not skip_ai_mode_selection:
            # AI 게임모드 선택
            self.select_ai_game_mode()
        else:
            print(f"\n{bright_cyan('🤖 저장된 AI 설정을 사용합니다.')}")
            ai_status = "활성화" if getattr(self, 'ai_game_mode_enabled', False) else "비활성화"
            print(f"   AI 게임모드: {ai_status}")
        
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
        
        # 현재 층 조우 현황 표시
        if hasattr(self, 'encounter_manager') and self.encounter_manager:
            current_floor = getattr(self, 'current_floor', 1)
            encounter_status = self.encounter_manager.get_floor_encounter_status(current_floor)
            print(f"\n🎲 {encounter_status}")
        
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
        
        # 세계 생성 (BGM은 main_game_loop에서 설정)
        self.world.generate_level()
        
        # print("✅ 게임 초기화 완료!")  # 메시지 제거
        
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
        # print(f"{bright_green('🚀 모험이 시작되었습니다!')}")  # 메시지 제거
        print()
        print(f"{bright_cyan('═══ 🎮 게임 조작법 ═══')}")
        print(f"  {bright_yellow('📍 이동:')} {bright_white('WASD 키 또는 방향키')}")
        print(f"  {cyan('📋 메뉴:')} {bright_white('I')}(인벤토리) {bright_white('P')}(파티상태) {bright_white('F')}(필드활동)")  
        print(f"  {magenta('⚙️  기타:')} {bright_white('H')}(도움말) {bright_white('Q')}(종료) {bright_white('B')}(저장)")
        
        # AI 게임모드 조작법 항상 표시
        if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
            print(f"  {bright_magenta('🤖 AI모드:')} {bright_white('M')}(AI설정) {bright_white('R')}(AI요청) {bright_white('Y')}(AI상태)")
        else:
            print(f"  {bright_magenta('🤖 AI모드:')} {bright_white('M')}(AI설정) - AI 게임모드 미활성화")
        print(f"{bright_cyan('═══════════════════')}")
        print()
        
        # 실제 게임 루프 시작
        # print(f"{bright_cyan('🎮 게임이 시작됩니다!')}")  # 메시지 제거
        self.keyboard.wait_for_key("🔑 아무 키나 눌러 게임 시작...")
        
        # 🎵 메인 메뉴/캐릭터 생성 BGM에서 던전 BGM으로 전환
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                import pygame
                # 현재 BGM이 던전 BGM이 아닌 경우에만 전환
                from game.audio_system import BGMType
                if not hasattr(self.audio_system, 'current_bgm_type') or self.audio_system.current_bgm_type != BGMType.FLOOR_1_3:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    import time
                    time.sleep(0.1)  # 잠시 대기
                    # 던전 BGM 시작
                    self.update_floor_bgm()  # 현재 층에 맞는 BGM 재생
        except Exception:
            pass
        
        # 메인 게임 루프 실행
        self.main_game_loop()
        
    def select_difficulty(self):
        """난이도 선택 메뉴"""
        # 메인 메뉴 BGM 즉시 정지 후 난이도 선택 BGM 재생
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                # 현재 BGM을 즉시 정지
                import pygame
                pygame.mixer.music.stop()
                
                # 잠시 대기 후 난이도 선택 BGM 재생
                import time
                time.sleep(0.5)
                
                from game.audio_system import BGMType
                self.audio_system.play_bgm(BGMType.DIFFICULTY_SELECT, loop=True)
        except Exception:
            pass
            
        try:
            from game.cursor_menu_system import CursorMenu
            
            difficulties = ["평온", "보통", "도전", "악몽", "지옥"]
            options = []
            descriptions = []
            
            for difficulty in difficulties:
                settings = self.config.DIFFICULTY_SETTINGS[difficulty]
                color = settings["color"]
                name = settings["name"]
                desc = settings["description"]
                
                # 메뉴 옵션 생성
                option_text = f"{color} {name}"
                options.append(option_text)
                
                # 상세 설명 생성
                description = f"{desc}\n\n"
                description += f"📊 배율 정보:\n"
                description += f"• 적 HP: {settings['enemy_hp_multiplier']}배\n"
                description += f"• 적 데미지: {settings['enemy_damage_multiplier']}배\n"
                description += f"• 플레이어 데미지: {settings['player_damage_multiplier']}배\n"
                description += f"• 경험치: {settings['exp_multiplier']}배\n"
                description += f"• 골드: {settings['gold_multiplier']}배\n"
                description += f"• 별조각: {settings['star_fragment_multiplier']}배\n"
                description += f"• 상처 축적률: {int(settings['wound_accumulation'] * 100)}%\n"
                description += f"• 치유 효과: {settings['healing_effectiveness']}배"
                
                descriptions.append(description)
            
            # 커서 메뉴 생성 및 실행
            title = "⚔️ 게임 난이도 선택"
            menu = CursorMenu(title, options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None:  # 취소
                # 취소 시 메인 메뉴 BGM으로 복원 (스마트 처리)
                try:
                    if hasattr(self, 'audio_system') and self.audio_system:
                        from game.audio_system import BGMType
                        # 이미 메인 메뉴 BGM이 재생 중이 아닌 경우에만 재생
                        if not (hasattr(self.audio_system, 'current_bgm_type') and 
                                self.audio_system.current_bgm_type == BGMType.MENU and 
                                self.audio_system.is_bgm_playing()):
                            self.audio_system.play_bgm(BGMType.MENU, loop=True)
                except Exception:
                    pass
                return None
            
            # 선택된 난이도
            selected_difficulty = difficulties[result]
            settings = self.config.DIFFICULTY_SETTINGS[selected_difficulty]
            
            # 선택 확인
            confirm_options = ["✅ 이 난이도로 시작", "🔙 다시 선택"]
            confirm_descriptions = [
                f"{settings['color']} {settings['name']} 난이도로 게임을 시작합니다",
                "난이도 선택으로 돌아갑니다"
            ]
            
            confirm_title = f"{settings['color']} {settings['name']} 선택 확인"
            confirm_menu = CursorMenu(confirm_title, confirm_options, confirm_descriptions, cancellable=True)
            confirm_result = confirm_menu.run()
            
            if confirm_result == 0:  # 확인
                self.config.set_difficulty(selected_difficulty)
                # 난이도 선택 완료 후 메인 메뉴 BGM으로 복원 (스마트 처리)
                try:
                    if hasattr(self, 'audio_system') and self.audio_system:
                        from game.audio_system import BGMType
                        # 이미 메인 메뉴 BGM이 재생 중이 아닌 경우에만 재생
                        if not (hasattr(self.audio_system, 'current_bgm_type') and 
                                self.audio_system.current_bgm_type == BGMType.MENU and 
                                self.audio_system.is_bgm_playing()):
                            self.audio_system.play_bgm(BGMType.MENU, loop=True)
                except Exception:
                    pass
                return selected_difficulty
            else:  # 다시 선택 또는 취소
                return self.select_difficulty()  # 재귀 호출로 다시 선택
                
        except ImportError:
            # 폴백: 기존 텍스트 메뉴
            return self.select_difficulty_fallback()
    
    def select_difficulty_fallback(self):
        """난이도 선택 메뉴 (폴백 버전)"""
        while True:
            self.display.clear_screen()
            print(f"{bright_cyan('⚔️ 게임 난이도 선택')}")
            
            difficulties = ["평온", "보통", "도전", "악몽", "지옥"]
            for i, difficulty in enumerate(difficulties, 1):
                settings = self.config.DIFFICULTY_SETTINGS[difficulty]
                color = settings["color"]
                name = settings["name"]
                desc = settings["description"]
                print(f"{bright_white(str(i))}. {color} {bright_yellow(name)} - {desc}")
            
            print(f"{bright_white('0')}. 🔙 돌아가기")
            
            choice = self.keyboard.get_string_input(f"난이도를 선택하세요 (1-{len(difficulties)}, 0: 돌아가기): ")
            
            if choice == '0':
                return None
            elif choice in ['1', '2', '3', '4', '5']:
                selected_difficulty = difficulties[int(choice) - 1]
                
                # 선택 확인
                settings = self.config.DIFFICULTY_SETTINGS[selected_difficulty]
                print(f"{settings['color']} {bright_yellow(settings['name'])} 난이도 선택")
                print(f"📝 {settings['description']}")
                
                confirm = self.keyboard.get_string_input("이 난이도로 시작하시겠습니까? (y/n): ").lower()
                if confirm == 'y':
                    self.config.set_difficulty(selected_difficulty)
                    return selected_difficulty
            else:
                print("❌ 잘못된 선택입니다.")
                self.keyboard.wait_for_key()

    def update_floor_bgm(self):
        """현재 층에 맞는 BGM 업데이트 (FFVII BGM 시스템 사용) - 로테이션 지원"""
        try:
            current_floor = getattr(self, 'current_floor', 1)
            
            # FFVII BGM 시스템 사용 - 층별 BGM 타입 매핑 (로테이션 자동 적용)
            if current_floor <= 3:
                from game.audio_system import BGMType
                bgm_type = BGMType.FLOOR_1_3  # 1-3층: 필드 BGM 로테이션
            elif current_floor <= 6:
                bgm_type = BGMType.FLOOR_4_6  # 4-6층
            elif current_floor <= 9:
                bgm_type = BGMType.FLOOR_7_9  # 7-9층
            elif current_floor <= 12:
                bgm_type = BGMType.FLOOR_10_12  # 10-12층
            elif current_floor <= 15:
                bgm_type = BGMType.FLOOR_13_15  # 13-15층
            elif current_floor <= 18:
                bgm_type = BGMType.FLOOR_16_18  # 16-18층
            elif current_floor <= 21:
                bgm_type = BGMType.FLOOR_19_21  # 19-21층
            elif current_floor <= 24:
                bgm_type = BGMType.FLOOR_22_24  # 22-24층
            else:
                bgm_type = BGMType.FLOOR_25_27  # 25층 이상
            
            # 현재 재생 중인 BGM이 원하는 BGM과 같은지 확인
            if hasattr(self, 'audio_system') and self.audio_system:
                if hasattr(self.audio_system, 'current_bgm_type') and self.audio_system.current_bgm_type == bgm_type:
                    return  # 이미 올바른 BGM이 재생 중이므로 재시작하지 않음
            
            # AudioManager의 로테이션 시스템을 활용한 BGM 재생
            if hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager._play_bgm_internal(bgm_type, loop=True, fade_in=1000)
            else:
                # 폴백: 문자열 방식으로 재생
                self.safe_play_bgm("bombing_mission", loop=True)
            
        except Exception as e:
            # 폴백으로 bombing_mission 재생
            try:
                self.safe_play_bgm("bombing_mission", loop=True)
            except:
                pass
            print(f"⚠️ BGM 업데이트 실패: {e}")

    def main_game_loop(self):
        """실제 게임 플레이 루프 - AI 게임모드 통합"""
        import time  # time 모듈 import 추가
        floors_cleared = 0
        enemies_defeated = 0
        
        # 게임 시작 시간 기록 (별조각 계산용)
        self.game_start_time = time.time()
        
        # 현재 층 정보 동기화
        self.current_floor = self.world.current_level
        previous_floor = self.current_floor
        
        # 🎵 필드 BGM 설정 (한 번만)
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                from game.audio_system import BGMType
                # 현재 BGM이 필드 BGM이 아닌 경우에만 변경
                if not hasattr(self.audio_system, 'current_bgm_type') or self.audio_system.current_bgm_type != BGMType.FLOOR_1_3:
                    self.audio_system.play_bgm(BGMType.FLOOR_1_3, loop=True)
        except Exception:
            pass

        # 게임 시작 화면 클리어
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # AI 게임모드 초기화 확인
        if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
            from game.ai_game_mode import ai_game_mode_manager
            from game.party_item_sharing import party_item_sharing
            
            # 파티 아이템 공유 시스템 초기화
            if hasattr(self.party_manager, 'inventory'):
                party_item_sharing.initialize_shared_inventory(self.party_manager.inventory)
        
        # 초기 화면 표시
        need_screen_refresh = True
        
        while self.running:
            try:
                # 층 변경 시 BGM 업데이트
                if self.current_floor != previous_floor:
                    self.update_floor_bgm()
                    previous_floor = self.current_floor
                    need_screen_refresh = True  # 층 변경 시 화면 갱신
                
                # BGM이 재생되지 않고 있으면 재시작 (너무 자주 확인하지 않도록 제한)
                if hasattr(self, 'audio_system') and self.audio_system:
                    try:
                        import pygame
                        # BGM 상태 확인을 매 루프마다 하지 않고 가끔만 확인
                        if not hasattr(self, '_bgm_check_counter'):
                            self._bgm_check_counter = 0
                        
                        self._bgm_check_counter += 1
                        # 10번에 한 번만 BGM 상태 확인 (너무 자주 확인하면 성능 저하)
                        if self._bgm_check_counter >= 10:
                            self._bgm_check_counter = 0
                            if not pygame.mixer.music.get_busy():
                                self.update_floor_bgm()
                    except:
                        pass  # pygame 오류는 무시
                
                # 화면 갱신이 필요한 경우에만 표시
                if need_screen_refresh:
                    # 화면 클리어 (UI 겹침 방지)
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                    try:
                        display_success = False
                        
                        # display 객체가 있으면 사용
                        if hasattr(self, 'display') and self.display:
                            try:
                                # cooking_system 가져오기
                                try:
                                    from game.cooking_system import cooking_system as cs
                                    self.display.show_game_screen(self.party_manager, self.world, cs)
                                except:
                                    self.display.show_game_screen(self.party_manager, self.world)
                                display_success = True
                            except Exception as display_error:
                                print(f"⚠️ Display 시스템 오류: {display_error}")
                                # Display 시스템 재초기화 시도
                                try:
                                    from game.display import GameDisplay
                                    self.display = GameDisplay()
                                    # cooking_system 가져오기
                                    try:
                                        from game.cooking_system import cooking_system as cs
                                        self.display.show_game_screen(self.party_manager, self.world, cs)
                                    except:
                                        self.display.show_game_screen(self.party_manager, self.world)
                                    display_success = True
                                    print("✅ Display 시스템 재초기화 성공")
                                except Exception as reinit_error:
                                    print(f"❌ Display 재초기화 실패: {reinit_error}")
                                    display_success = False
                        else:
                            # display 객체가 없는 경우 초기화
                            try:
                                from game.display import GameDisplay
                                self.display = GameDisplay()
                                # cooking_system 가져오기
                                try:
                                    from game.cooking_system import cooking_system as cs
                                    self.display.show_game_screen(self.party_manager, self.world, cs)
                                except:
                                    self.display.show_game_screen(self.party_manager, self.world)
                                display_success = True
                                print("✅ Display 시스템 초기화 성공")
                            except Exception as init_error:
                                print(f"❌ Display 초기화 실패: {init_error}")
                                display_success = False
                        
                        # 모든 표시 방법 실패 시 최소한의 정보
                        if not display_success:
                            # 화면 클리어 (폴백용)
                            import os
                            if os.name == 'nt':
                                os.system('cls')
                            else:
                                os.system('clear')
                                
                            print(f"\n🎮 Dawn of Stellar - 던전 {getattr(self.world, 'current_level', 1)}층")
                            print(f"📍 플레이어 위치: {getattr(self.world, 'player_pos', '알 수 없음')}")
                            print("❌ 화면 표시 시스템에 문제가 있습니다. 게임은 계속 진행됩니다.")
                            print(f"⚙️ 화면 표시 문제가 있습니다. Enter를 눌러 다시 시도하세요.")
                            
                    except Exception as display_error:
                        # 최종 fallback: 기본 텍스트만 표시
                        print(f"🔧 Display 오류: {display_error}")
                        print(f"🎮 Dawn of Stellar - 던전 {getattr(self.world, 'current_level', 1)}층")
                        print(f"📍 위치: {getattr(self.world, 'player_pos', '?')}")
                        print("화면 표시에 문제가 있습니다. 게임은 계속 진행됩니다.")
                    
                    need_screen_refresh = False  # 화면 갱신 완료
                
                # AI 요청 확인 (AI 게임모드인 경우)
                if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
                    from game.party_item_sharing import party_item_sharing
                    if party_item_sharing.pending_requests:
                        print(f"\n💬 AI 동료들의 요청이 {len(party_item_sharing.pending_requests)}개 있습니다!")
                        print("'i' 키를 눌러 확인하세요.")
                
                # 플레이어 입력 받기
                action = self.get_player_input()
                
                # 액션 처리
                self.process_action(action)
                
                # 액션 처리 후 화면 갱신 필요 설정
                need_screen_refresh = True
                
                # 액션 처리 후 화면 업데이트는 메인 루프에서 자동으로 처리됨
                # 중복 화면 클리어 제거 - WASD 키마다 2번 클리어되는 문제 해결
                
                # 층 변경 감지 및 자동 저장
                current_floor = getattr(self.world, 'current_level', self.current_floor)
                if current_floor != previous_floor:
                    floors_cleared = current_floor - 1
                    print(f"\n🏢 {previous_floor}층 → {current_floor}층으로 이동!")
                    
                    # 자동 저장 트리거
                    if AUTO_SAVE_AVAILABLE and self.auto_save_manager:
                        try:
                            on_floor_change(current_floor)
                        except Exception as e:
                            print(f"⚠️ 층 변경 자동 저장 실패: {e}")
                    
                    previous_floor = current_floor
                    self.current_floor = current_floor
                
                # 층 클리어 확인 (계단 이용 시)
                if hasattr(self, '_floor_advanced') and self._floor_advanced:
                    floors_cleared = self.world.current_level - 1  # 시작 층이 1이므로
                    self._floor_advanced = False
                
                # 게임 오버 조건 체크
                if not self.party_manager.has_alive_members():
                    print(f"\n{bright_red('💀 파티가 전멸했습니다...', True)}")
                    print("게임 오버!")
                    
                    # 파티 전멸 자동 저장
                    if AUTO_SAVE_AVAILABLE and self.auto_save_manager:
                        try:
                            on_party_wipe()
                        except Exception as e:
                            print(f"⚠️ 전멸 자동 저장 실패: {e}")
                    
                    # 게임 종료 시 영구 진행상황 업데이트
                    self.update_permanent_progression(floors_cleared, enemies_defeated, died=True)
                    break
                    
            except KeyboardInterrupt:
                print(f"\n{bright_yellow('게임을 중단합니다.')}")
                # 중단 시에도 진행상황 저장
                self.update_permanent_progression(floors_cleared, enemies_defeated, died=False)
                break
        
        print(f"\n{bright_cyan('게임이 종료되었습니다.')}")
        
        # 메인 메뉴로 돌아가기 전 BGM 차단
        try:
            from game.audio_system import BGMType
            if hasattr(self, 'audio_system') and self.audio_system:
                pass  # BGM 재생하지 않음
            elif hasattr(self, 'sound_manager') and self.sound_manager:
                pass  # BGM 재생하지 않음
        except Exception as e:
            pass  # 조용히 처리
        
        print("\n3초 후 메인 메뉴로 돌아갑니다...")
        try:
            import time
            time.sleep(3)
        except:
            pass
    
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
                
                if result is None or result == 9:  # 설정 완료 또는 취소 (인덱스 변경)
                    # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                    self._play_main_menu_bgm()
                    break
                elif result == 0:  # 맵 크기 설정 (난이도 제거로 인덱스 변경)
                    self._show_map_size_cursor_menu()
                elif result == 1:  # 화면 설정
                    self._show_display_settings_menu()
                elif result == 2:  # 오디오 설정
                    self._show_audio_settings_menu()
                elif result == 3:  # 게임플레이 설정
                    self._show_gameplay_settings_menu()
                elif result == 4:  # 접근성 설정
                    self._show_accessibility_settings_menu()
                elif result == 5:  # 조작키 설정
                    self._show_controls_settings_menu()
                elif result == 6:  # 성능 설정
                    self._show_performance_settings_menu()
                elif result == 7:  # 개발자 옵션
                    self._show_developer_options_menu()
                elif result == 8:  # 모든 설정 보기
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
        print("   • BGM: game/audio/bgm/")
        print("   • 효과음: game/audio/sfx/")
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
                    f"� 강제 글리치 모드: {green('켜짐') if getattr(game_config, 'FORCE_GLITCH_MODE', False) else red('꺼짐')}",
                    f"🚫 글리치 모드 비활성화: {green('켜짐') if getattr(game_config, 'DISABLE_GLITCH_MODE', False) else red('꺼짐')}",
                    "🔄 글리치 설정 초기화",
                    "�📊 개발자 정보 확인",
                    "⬅️ 돌아가기"
                ]
                
                descriptions = [
                    "개발자 전용 기능들을 활성화합니다 (모든 직업 해금 등)",
                    "상세한 디버그 정보를 표시합니다",
                    "전투 시 데미지 계산 과정을 표시합니다",
                    "HP, MP, 골드 등이 무제한으로 사용됩니다",
                    "세피로스 조우 없이도 강제로 글리치 모드를 활성화합니다",
                    "세피로스 조우 후에도 글리치 모드를 비활성화합니다",
                    "글리치 모드 관련 설정을 모두 초기화합니다",
                    "현재 개발자 설정 상태를 확인합니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = CursorMenu("📊 개발자 옵션", options, descriptions)
                result = menu.run()
                
                if result is None or result == 8:  # 돌아가기
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
                elif result == 4:  # 강제 글리치 모드 토글
                    game_config.toggle_force_glitch_mode()
                    status = "켜짐" if game_config.FORCE_GLITCH_MODE else "꺼짐"
                    print(f"✅ 강제 글리치 모드가 {status}으로 설정되었습니다.")
                    if game_config.FORCE_GLITCH_MODE:
                        print("👻 이제 항상 글리치 모드로 스토리가 표시됩니다!")
                        print("🔊 무서운 효과음과 글리치 효과가 적용됩니다.")
                    else:
                        print("🔄 일반 모드로 돌아갑니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 5:  # 글리치 모드 비활성화 토글
                    game_config.toggle_disable_glitch_mode()
                    status = "켜짐" if game_config.DISABLE_GLITCH_MODE else "꺼짐"
                    print(f"✅ 글리치 모드 비활성화가 {status}으로 설정되었습니다.")
                    if game_config.DISABLE_GLITCH_MODE:
                        print("🚫 세피로스 조우 후에도 글리치 모드가 활성화되지 않습니다!")
                        print("📖 항상 일반 스토리만 표시됩니다.")
                    else:
                        print("🔄 정상 동작으로 돌아갑니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 6:  # 글리치 설정 초기화
                    game_config.reset_glitch_mode_settings()
                    print("✅ 글리치 모드 설정이 초기화되었습니다.")
                    print("🔄 강제 글리치 모드와 비활성화 모드가 모두 꺼졌습니다.")
                    print("📖 이제 세피로스 조우 여부에 따라 정상 동작합니다.")
                    input("아무 키나 눌러 계속...")
                elif result == 7:  # 개발자 정보 확인
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
        """플레이어 입력 받기 - 화면 중복 출력 방지"""
        try:
            # 조작법은 게임 시작 시에만 한 번 표시
            if not hasattr(self, '_controls_shown'):
                
                # AI 게임모드 조작법
                if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
                    print(f"  {bright_magenta('🤖 AI모드:')} M(AI설정), R(AI요청), Y(AI상태)")
                else:
                    print(f"  {bright_magenta('🤖 AI모드:')} M(AI설정) - 미활성화")
                
                # 자동전투 상태 표시
                auto_battle_status = self.get_auto_battle_status()
                if auto_battle_status is not None:
                    status_text = "🟢 ON" if auto_battle_status else "🔴 OFF"
                    print(f"  {bright_yellow(f'⚡ 자동전투 상태: {status_text}')}")
                
                print(f"\n{bright_green('💡 도움말을 보려면 H키를 누르세요!')}")
                self._controls_shown = True
            
            # 간단한 입력 프롬프트만 표시
            print(f"\n{bright_yellow('명령 입력:')} ", end="", flush=True)
            return self.keyboard.get_input()
        except Exception as e:
            print(f"⚠️ 입력 처리 오류: {e}")
            return 'q'  # 오류 시 종료
    
    def process_action(self, action):
        """액션 처리 - AI 게임모드 및 이동/층 전환 지원"""
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
            print(f"   {bright_white('T')} - ⚔️ 자동전투 토글")
            print(f"   {bright_white('Z')} - 🌀 긴급 텔레포트 (갇혔을 때 사용)")
            
            # AI 게임모드인 경우 추가 조작법
            if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
                print()
                print(f"{bright_magenta('🤖 AI 게임모드:')}")
                print(f"   {bright_white('M')} - 🎛️ AI 모드 설정")
                print(f"   {bright_white('R')} - 💬 AI 요청 처리")
                print(f"   {bright_white('Y')} - 📊 AI 상태 확인")
            
            print(f"{bright_cyan('═══════════════════════════════════════')}")
            print(f"{bright_green('💡 팁: 던전을 탐험하며 몬스터와 전투하고 보물을 찾아보세요!')}")
            print(f"{bright_cyan('═══════════════════════════════════════')}")
            
            # 조작법을 다시 표시하도록 플래그 리셋
            self._controls_shown = False
            self.keyboard.wait_for_key("🔑 아무 키나 눌러 계속...")
            
        elif action.lower() == 't':  # T키로 자동전투 토글
            self.toggle_auto_battle()
            
        elif action.lower() == 'm':  # M키로 AI 모드 설정
            if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
                self.show_ai_mode_settings()
            else:
                print("❌ AI 게임모드가 활성화되지 않았습니다.")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        
        elif action.lower() == 'r':  # R키로 AI 요청 처리
            if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
                self.handle_ai_requests()
            else:
                print("❌ AI 게임모드가 활성화되지 않았습니다.")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        
        elif action.lower() == 'y':  # Y키로 AI 상태 확인
            if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
                self.show_ai_status()
            else:
                print("❌ AI 게임모드가 활성화되지 않았습니다.")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        
        elif action == '\r' or action == '\n':  # Enter 키 - 상호작용
            handle_interaction(self)
            
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
                
        elif action.lower() == 'z':  # Z키로 긴급 텔레포트 (갇혔을 때)
            print(f"\n{bright_yellow('🌀 긴급 텔레포트 시전!')}")
            try:
                # 현재 층에서 안전한 위치 찾기
                safe_positions = []
                for y in range(self.world.height):
                    for x in range(self.world.width):
                        tile = self.world.tiles[y][x]
                        if tile.type.name == "FLOOR" and tile.is_walkable():
                            # 주변에 벽이 너무 많지 않은 안전한 곳인지 확인
                            wall_count = 0
                            for dy in [-1, 0, 1]:
                                for dx in [-1, 0, 1]:
                                    ny, nx = y + dy, x + dx
                                    if (0 <= ny < self.world.height and 0 <= nx < self.world.width):
                                        if not self.world.tiles[ny][nx].is_walkable():
                                            wall_count += 1
                            
                            # 주변에 벽이 5개 이하인 곳만 안전한 곳으로 판단
                            if wall_count <= 5:
                                safe_positions.append((x, y))
                
                if safe_positions:
                    import random
                    new_x, new_y = random.choice(safe_positions)
                    self.world.player_pos = (new_x, new_y)
                    print(f"✅ 안전한 위치 ({new_x}, {new_y})로 텔레포트했습니다!")
                else:
                    # 안전한 곳을 못 찾으면 계단 근처로
                    stairs_found = False
                    for y in range(self.world.height):
                        for x in range(self.world.width):
                            tile = self.world.tiles[y][x]
                            if tile.type.name in ["STAIRS_UP", "STAIRS_DOWN"]:
                                # 계단 주변 빈 공간 찾기
                                for dy in [-1, 0, 1]:
                                    for dx in [-1, 0, 1]:
                                        ny, nx = y + dy, x + dx
                                        if (0 <= ny < self.world.height and 0 <= nx < self.world.width):
                                            if self.world.tiles[ny][nx].is_walkable():
                                                self.world.player_pos = (nx, ny)
                                                print(f"✅ 계단 근처 ({nx}, {ny})로 텔레포트했습니다!")
                                                stairs_found = True
                                                break
                                    if stairs_found:
                                        break
                            if stairs_found:
                                break
                        if stairs_found:
                            break
                    
                    if not stairs_found:
                        print("❌ 안전한 텔레포트 위치를 찾을 수 없습니다.")
                        
            except Exception as e:
                print(f"❌ 텔레포트 중 오류: {e}")
            
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                
        elif action.lower() == 'i':
            # 인벤토리 메뉴 - AI 게임모드에서는 아이템 공유 상태도 표시
            if hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled:
                from game.party_item_sharing import party_item_sharing
                party_item_sharing.handle_pending_requests()  # 대기 중인 요청 먼저 처리
            # 인벤토리 메뉴 - 소모품과 장비 선택
            if hasattr(self, 'party_manager') and self.party_manager.members:
                try:
                    from game.cursor_menu_system import create_simple_menu
                    
                    # 메뉴 옵션 - AI 게임모드가 아닐 때만 아이템 전송 추가
                    inventory_options = ["🧪 소모품", "⚔️ 장비", "🤔 장비 해제", "⚡ 최적화 재장착"]
                    inventory_descriptions = [
                        "치유 물약, 버프 아이템 등을 사용합니다",
                        "무기, 방어구, 장신구를 장착합니다",
                        "현재 장착된 장비를 해제합니다",
                        "모든 파티원의 장비를 최적화하여 재장착합니다"
                    ]
                    
                    # AI 게임모드가 아닌 경우에만 아이템 전송 옵션 추가
                    if not (hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled):
                        inventory_options.insert(-1, "📦 아이템 전송")
                        inventory_descriptions.insert(-1, "파티원 간 아이템을 주고받습니다")
                    
                    inventory_options.append("🚪 취소")
                    inventory_descriptions.append("인벤토리를 닫습니다")
                    
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
                    
                    elif inventory_choice == 3:  # 📦 아이템 전송 (AI모드가 아닐 때만) 또는 ⚡ 최적화 재장착 (AI모드일 때)
                        if not (hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled):
                            # AI 모드가 아닐 때: 아이템 전송
                            self._handle_item_transfer()
                        else:
                            # AI 모드일 때: 최적화 재장착
                            self._handle_equipment_optimize()
                        
                    elif inventory_choice == 4:  # ⚡ 최적화 재장착 (AI모드가 아닐 때만 - 아이템 전송이 추가되어 밀림)
                        if not (hasattr(self, 'ai_game_mode_enabled') and self.ai_game_mode_enabled):
                            self._handle_equipment_optimize()
                    
                    # choice == 마지막 (취소)는 자동으로 처리
                        
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
                        
                        # WOUND는 0이 아닐 때만 표시, 이모지 제거
                        if hasattr(member, 'wounds') and member.wounds > 0:
                            details.append(f"WOUND: {member.wounds}")
                        
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
                        from game.cursor_menu_system import create_simple_menu
                        from game.cooking_system import get_cooking_system, GATHERING_LOCATIONS
                        
                        cooking_system = get_cooking_system()
                        
                        # 요리/채집 서브메뉴
                        cooking_options = ["🍳 요리 시스템", "🌿 채집하기", "📍 채집지 정보"]
                        cooking_descriptions = [
                            "완전한 요리 시스템에 접근합니다",
                            "현재 위치에서 식재료를 채집합니다",
                            "채집 가능한 장소와 획득 가능한 재료를 확인합니다"
                        ]
                        
                        cooking_menu = create_simple_menu("🍳 야외 요리 & 채집", cooking_options, cooking_descriptions)
                        cooking_choice = cooking_menu.run()
                        
                        if cooking_choice == 0:
                            # 완전한 요리 시스템
                            cooking_system.show_cooking_menu()
                        elif cooking_choice == 1:
                            # 채집하기 - 현재 층에 따른 채집지 선택
                            current_floor = self.world.current_level  # world에서 정확한 층수 가져오기
                            
                            # 채집 쿨타임 확인 (300걸음마다 초기화)
                            if not hasattr(self, 'gathering_cooldown'):
                                self.gathering_cooldown = 0
                            if not hasattr(self, 'steps_since_last_gather'):
                                self.steps_since_last_gather = 0
                            
                            if self.gathering_cooldown > 0:
                                remaining_steps = 300 - self.steps_since_last_gather
                                print(f"\n⏰ 채집 쿨타임 중입니다. {remaining_steps}걸음 더 걸어야 채집할 수 있습니다.")
                                input("아무 키나 눌러 계속...")
                            else:
                                # 층에 따른 채집지 매핑 (20층마다 반복)
                                base_mapping = {
                                    1: "숲속 채집지", 2: "숲속 채집지", 3: "강가 채집지",
                                    4: "강가 채집지", 5: "동굴 채집지", 6: "동굴 채집지",
                                    7: "고원 채집지", 8: "고원 채집지", 9: "화산 채집지",
                                    10: "화산 채집지", 11: "빙하 채집지", 12: "빙하 채집지",
                                    13: "사막 채집지", 14: "사막 채집지", 15: "심해 채집지",
                                    16: "심해 채집지", 17: "천공 채집지", 18: "천공 채집지",
                                    19: "지하 세계", 20: "지하 세계"
                                }
                                
                                # 20층 주기로 반복 (1~20, 21~40, 41~60, ...)
                                mapped_floor = ((current_floor - 1) % 20) + 1
                                location_name = base_mapping.get(mapped_floor, "지하 세계")
                                
                                print(f"\n🌍 현재 위치: {current_floor}층 - {location_name}")
                                print(f"🔄 채집지 패턴: {mapped_floor}층과 동일 (20층 주기)")
                                print(f"🎯 이 층에서는 다양한 재료를 채집할 수 있습니다!")
                                
                                if cooking_system.enhanced_gather_from_location(location_name):
                                    print(f"\n{bright_green('✅ 채집이 완료되었습니다!')}")
                                    # 채집 성공 시 쿨타임 설정
                                    self.gathering_cooldown = 300
                                    self.steps_since_last_gather = 0
                                    print(f"⏰ 다음 채집까지 300걸음이 필요합니다.")
                                else:
                                    print(f"\n{bright_red('❌ 채집에 실패했습니다.')}")
                                
                                input("아무 키나 눌러 계속...")
                            
                        elif cooking_choice == 2:
                            # 채집지 정보
                            cooking_system.show_gathering_locations()
                            input("아무 키나 눌러 계속...")
                            
                    except Exception as e:
                        print(f"요리/채집 시스템 오류: {e}")
                        print("기본 요리 메뉴를 사용합니다.")
                        # 폴백: 기존 요리 메뉴
                        print(f"\n{bright_cyan('=== 🍳 요리 메뉴 ===')}")
                        print("1. 🥘 요리하기")
                        print("2. 📄 레시피 보기")
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
        # 빈 문자열이나 엔터키 처리
        elif action.strip() == '' or action == '\n':
            # 빈 입력은 무시하고 다시 입력 받음
            return
        else:
            print(f"⚠️ 알 수 없는 명령: '{action}' (도움말: H)")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def handle_player_movement(self, direction):
        """플레이어 이동 처리 - 개선된 오류 처리와 아이템 획득 + 20걸음 턴 시스템"""
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
                
                # 걸음 카운터 증가 (20걸음 = 1턴)
                if not hasattr(self, 'step_counter'):
                    self.step_counter = 0
                self.step_counter += 1
                
                # 20걸음마다 턴 처리 (자연회복)
                if self.step_counter >= 20:
                    self.step_counter = 0
                    # 메시지 버퍼에 추가
                    self.add_game_message("⏰ 20걸음을 걸어 1턴이 경과했습니다...")
                    self.process_field_turn()
                
                # 결과 처리
                if result == "next_floor":
                    print(f"\n🚪 {bright_green('계단을 발견했습니다!')}")
                    self.advance_to_next_floor()
                elif isinstance(result, dict) and result.get("type") == "combat":
                    # 새로운 다중 적 전투 시스템
                    enemy_positions = result.get("enemies", [])
                    print(f"\n⚔️ {bright_red(f'{len(enemy_positions)}개 위치의 적들과 교전 시작!')}")
                    self.keyboard.wait_for_key("아무 키나 눌러 전투 시작...")
                    
                    # 다중 적 전투 실행
                    combat_result = self.start_multi_enemy_combat(enemy_positions)
                    
                    # 전투 승리 시 모든 적 제거
                    if combat_result == "victory":
                        self.world.remove_combat_enemies(enemy_positions, self)
                        self.add_game_message(f"🎉 승리! 모든 적이 소멸되었습니다!")
                    
                    return  # handle_player_movement 종료하여 main_game_loop로 돌아감
                elif result == "combat":
                    # 기존 단일 적 전투 (호환성 유지)
                    print(f"\n⚔️ {bright_red('적과 마주쳤습니다!')}")
                    self.keyboard.wait_for_key("아무 키나 눌러 전투 시작...")
                    # 전투 시스템 호출 - 전투 후 화면 갱신 필요
                    self.start_battle()
                    # 전투 종료 후 화면 갱신 플래그 설정 (main_game_loop에서 처리)
                    return  # handle_player_movement 종료하여 main_game_loop로 돌아감
                elif result == "moved":
                    # 일반 이동 성공 (조용히 처리)
                    pass
                elif result and hasattr(result, 'name'):  # 아이템 획득
                    print(f"\n💎 {bright_yellow('아이템 발견!')}")
                    
                    # 메타 진행에 아이템 발견 기록
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        try:
                            item_type = "소모품"
                            rarity = getattr(result, 'rarity', "일반")
                            level_req = getattr(result, 'level_requirement', 0)
                            current_floor = getattr(self, 'current_floor', 1)
                            
                            # 아이템 타입 결정
                            if hasattr(result, 'type'):
                                if result.type in ["무기", "방어구", "액세서리"]:
                                    self.meta_progression.discover_equipment(result.name, result.type, rarity, level_req, current_floor)
                                elif result.type == "음식":
                                    self.meta_progression.discover_food(result.name, result.type, rarity, current_floor)
                                else:
                                    self.meta_progression.discover_item(result.name, result.type, rarity, level_req, current_floor)
                            else:
                                # 기본적으로 소모품으로 처리
                                self.meta_progression.discover_item(result.name, item_type, rarity, level_req, current_floor)
                            
                            self.meta_progression.save_data()
                        except Exception as e:
                            pass  # 메타 진행 기록 실패해도 게임은 계속
                    
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
                
                # 채집 쿨타임 감소
                if hasattr(self, 'gathering_cooldown') and self.gathering_cooldown > 0:
                    if hasattr(self, 'steps_since_last_gather'):
                        self.steps_since_last_gather += 1
                    else:
                        self.steps_since_last_gather = 1
                    
                    if self.steps_since_last_gather >= 300:
                        self.gathering_cooldown = 0
                        self.steps_since_last_gather = 0
                        print(f"✅ {bright_green('채집 쿨타임이 해제되었습니다!')}")
                        print("🌿 이제 다시 채집할 수 있습니다!")
                        self.keyboard.wait_for_key("🔑 아무 키나 눌러 계속...")
                
                # 필드 자동 회복 처리
                self._process_field_regeneration()
                    
                self.check_random_encounter()
                
                # 적들 이동 처리 (플레이어 이동 후)
                if hasattr(self.world, 'move_enemies') and self.world.enemies_positions:
                    enemy_count_before = len(self.world.enemies_positions)
                    self.world.move_enemies()
                    # 적이 실제로 많고 가끔씩만 메시지 표시 (2% 확률로 드물게)
                    if enemy_count_before >= 3 and random.random() < 0.02:
                        # 메시지 버퍼에 추가 (맵 아래쪽에 표시됨)
                        self.add_game_message("👹 멀리서 적들의 움직임이 감지됩니다...")
                
            else:
                # 이동 실패 원인 파악
                new_x = self.world.player_pos[0] + dx
                new_y = self.world.player_pos[1] + dy
                
                if not self.world.is_valid_pos(new_x, new_y):
                    print("🚫 맵 경계를 벗어났습니다.")
                elif not self.world.tiles[new_y][new_x].is_walkable():
                    tile_type = self.world.tiles[new_y][new_x].type.name
                    if tile_type == "TRAP":
                        print("⚠️ 함정을 밟았습니다! (함정이 발동될 수 있습니다)")
                    elif tile_type == "WALL":
                        print("🚫 벽입니다.")
                    elif tile_type == "LOCKED_DOOR":
                        print("🔒 잠긴 문입니다. (열쇠가 필요)")
                    elif tile_type == "SECRET_DOOR":
                        print("🚫 벽입니다. (비밀문일지도?)")
                    else:
                        print(f"🚫 지나갈 수 없습니다 ({tile_type})")
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
    
    def process_field_turn(self):
        """필드에서 20걸음 = 1턴 처리 (자연회복 + 모든 상태이상 처리)"""
        self.add_game_message("🌿 자연에서 휴식을 취합니다...")
        
        if hasattr(self, 'party_manager') and self.party_manager and hasattr(self.party_manager, 'members'):
            for member in self.party_manager.members:
                if not member.is_alive:
                    continue
                
                # 📍 모든 상태이상 처리
                if hasattr(member, 'status_manager') and member.status_manager:
                    self.add_game_message(f"⏰ {member.name}의 상태이상 처리 중...")
                    member.status_manager.process_turn_effects(member)
                    
                    # 지속 피해 상태이상들
                    if hasattr(member.status_manager, 'has_status'):
                        # 독 상태이상
                        if member.status_manager.has_status('poison'):
                            poison_power = getattr(member.status_manager.get_status('poison'), 'power', 10)
                            poison_damage = max(1, member.max_hp // 20 + poison_power)
                            member.current_hp = max(1, member.current_hp - poison_damage)
                            print(f"☠️ {member.name}이(가) 독으로 {poison_damage} HP 피해를 받았습니다!")
                            
                        # 화상 상태이상
                        if member.status_manager.has_status('burn'):
                            burn_power = getattr(member.status_manager.get_status('burn'), 'power', 15)
                            burn_damage = max(1, member.max_hp // 15 + burn_power)
                            member.current_hp = max(1, member.current_hp - burn_damage)
                            print(f"🔥 {member.name}이(가) 화상으로 {burn_damage} HP 피해를 받았습니다!")
                            
                        # 출혈 상태이상
                        if member.status_manager.has_status('bleed'):
                            bleed_power = getattr(member.status_manager.get_status('bleed'), 'power', 8)
                            bleed_damage = max(1, member.max_hp // 25 + bleed_power)
                            member.current_hp = max(1, member.current_hp - bleed_damage)
                            print(f"🩸 {member.name}이(가) 출혈로 {bleed_damage} HP 피해를 받았습니다!")
                            
                        # 부식 상태이상
                        if member.status_manager.has_status('corrode'):
                            corrode_power = getattr(member.status_manager.get_status('corrode'), 'power', 12)
                            corrode_damage = max(1, member.max_hp // 18 + corrode_power)
                            member.current_hp = max(1, member.current_hp - corrode_damage)
                            print(f"🟢 {member.name}이(가) 부식으로 {corrode_damage} HP 피해를 받았습니다!")
                            
                        # 질병 상태이상
                        if member.status_manager.has_status('disease'):
                            disease_power = getattr(member.status_manager.get_status('disease'), 'power', 6)
                            disease_damage = max(1, member.max_hp // 30 + disease_power)
                            member.current_hp = max(1, member.current_hp - disease_damage)
                            print(f"🤢 {member.name}이(가) 질병으로 {disease_damage} HP 피해를 받았습니다!")
                            
                        # 괴사 상태이상
                        if member.status_manager.has_status('necrosis'):
                            necrosis_power = getattr(member.status_manager.get_status('necrosis'), 'power', 20)
                            necrosis_damage = max(1, member.max_hp // 12 + necrosis_power)
                            member.current_hp = max(1, member.current_hp - necrosis_damage)
                            print(f"💀 {member.name}이(가) 괴사로 {necrosis_damage} HP 피해를 받았습니다!")
                            
                        # 감전 상태이상
                        if member.status_manager.has_status('shock'):
                            shock_power = getattr(member.status_manager.get_status('shock'), 'power', 10)
                            shock_damage = max(1, member.max_hp // 22 + shock_power)
                            member.current_hp = max(1, member.current_hp - shock_damage)
                            print(f"⚡ {member.name}이(가) 감전으로 {shock_damage} HP 피해를 받았습니다!")
                            
                        # 냉기 상태이상
                        if member.status_manager.has_status('chill'):
                            chill_power = getattr(member.status_manager.get_status('chill'), 'power', 8)
                            chill_damage = max(1, member.max_hp // 28 + chill_power)
                            member.current_hp = max(1, member.current_hp - chill_damage)
                            print(f"🧊 {member.name}이(가) 냉기로 {chill_damage} HP 피해를 받았습니다!")
                            
                        # MP 소모 상태이상
                        if member.status_manager.has_status('mp_drain'):
                            mp_drain_power = getattr(member.status_manager.get_status('mp_drain'), 'power', 15)
                            mp_loss = max(1, member.max_mp // 20 + mp_drain_power)
                            member.current_mp = max(0, member.current_mp - mp_loss)
                            print(f"🔮💔 {member.name}이(가) MP 흡수로 {mp_loss} MP를 잃었습니다!")
                        
                        # 회복 상태이상들
                        # 재생 상태이상
                        if member.status_manager.has_status('regeneration'):
                            regen_power = getattr(member.status_manager.get_status('regeneration'), 'power', 20)
                            regen_heal = max(1, member.max_hp // 10 + regen_power)
                            old_hp = member.current_hp
                            member.current_hp = min(member.max_hp, member.current_hp + regen_heal)
                            healed = member.current_hp - old_hp
                            print(f"💚 {member.name}이(가) 재생으로 {healed} HP 회복했습니다!")
                            
                        # MP 재생 상태이상
                        if member.status_manager.has_status('mp_regen'):
                            mp_regen_power = getattr(member.status_manager.get_status('mp_regen'), 'power', 12)
                            mp_heal = max(1, member.max_mp // 15 + mp_regen_power)
                            old_mp = member.current_mp
                            member.current_mp = min(member.max_mp, member.current_mp + mp_heal)
                            mp_recovered = member.current_mp - old_mp
                            print(f"🔮💙 {member.name}이(가) MP 재생으로 {mp_recovered} MP 회복했습니다!")
                            
                        # 축복 상태이상 (모든 능력치 증가)
                        if member.status_manager.has_status('blessing'):
                            blessing_power = getattr(member.status_manager.get_status('blessing'), 'power', 10)
                            blessing_heal = max(1, member.max_hp // 15 + blessing_power)
                            old_hp = member.current_hp
                            member.current_hp = min(member.max_hp, member.current_hp + blessing_heal)
                            healed = member.current_hp - old_hp
                            if healed > 0:
                                print(f"✨ {member.name}이(가) 축복으로 {healed} HP 회복했습니다!")
                            
                        # 성스러운 기운 (신관 전용 회복)
                        if member.status_manager.has_status('holy_aura'):
                            holy_power = getattr(member.status_manager.get_status('holy_aura'), 'power', 15)
                            holy_heal = max(1, member.max_hp // 12 + holy_power)
                            old_hp = member.current_hp
                            member.current_hp = min(member.max_hp, member.current_hp + holy_heal)
                            healed = member.current_hp - old_hp
                            if healed > 0:
                                print(f"✨🛡️ {member.name}이(가) 성스러운 기운으로 {healed} HP 회복했습니다!")
                    
                # HP 자연회복
                old_hp = member.current_hp
                # 기존 자연회복량 사용 (최대 HP의 5%)
                hp_regen = max(1, member.max_hp // 20)  # 최대 HP의 5%
                member.current_hp = min(member.max_hp, member.current_hp + hp_regen)
                hp_recovered = member.current_hp - old_hp
                
                # MP 자연회복
                old_mp = member.current_mp
                # 기존 자연회복량 사용 (최대 MP의 3%)
                mp_regen = max(1, member.max_mp // 33)  # 최대 MP의 3%
                member.current_mp = min(member.max_mp, member.current_mp + mp_regen)
                mp_recovered = member.current_mp - old_mp
                
                # 광전사 회복 시 분노 감소 (자연회복 15%)
                if (hasattr(member, 'character_class') and member.character_class == "광전사" and 
                    hasattr(member, 'rage_stacks') and member.rage_stacks > 0 and hp_recovered > 0):
                    
                    # 회복량의 15%만큼 분노 감소 (자연회복은 더 적게)
                    rage_decrease = max(1, int(hp_recovered * 0.15))
                    member.rage_stacks = max(0, member.rage_stacks - rage_decrease)
                    print(f"😌 {member.name}의 분노가 자연 회복으로 {rage_decrease}만큼 가라앉았습니다.")
                
                if hp_recovered > 0 or mp_recovered > 0:
                    print(f"💚 {member.name}: HP +{hp_recovered}, MP +{mp_recovered}")
        
        self.add_game_message("⏰ 1턴이 경과했습니다.")
    
    def check_random_encounter(self):
        """🔥 강화된 랜덤 인카운터 체크"""
        try:
            # 강화된 조우 시스템 우선 사용
            if hasattr(self, 'enhanced_encounter_manager') and self.enhanced_encounter_manager:
                party = []
                if hasattr(self, 'party_manager') and self.party_manager and hasattr(self.party_manager, 'members'):
                    party = self.party_manager.members
                
                if not party:
                    return  # 파티가 없으면 인카운터 발생 안함
                
                current_floor = getattr(self.world, 'current_floor', 1) if hasattr(self, 'world') else 1
                
                # 강화된 조우 확률 계산 (기존보다 낮은 확률)
                import random
                base_chance = 0.003  # 0.3% 기본 확률
                floor_bonus = current_floor * 0.0005  # 층당 0.05% 증가
                steps_bonus = getattr(self, 'steps_since_last_encounter', 0) * 0.001  # 걸음당 0.1% 증가
                
                total_chance = min(base_chance + floor_bonus + steps_bonus, 0.015)  # 최대 1.5%
                
                if random.random() < total_chance:
                    # 강화된 조우 시스템 실행
                    encounter_result = self.enhanced_encounter_manager.trigger_enhanced_encounter(party, current_floor)
                    if encounter_result:
                        self.handle_enhanced_encounter(encounter_result)
                        self.steps_since_last_encounter = 0
                        return
            
            # 기존 시스템 폴백
            if hasattr(self, 'encounter_manager') and self.encounter_manager:
                party = []
                if hasattr(self, 'party_manager') and self.party_manager and hasattr(self.party_manager, 'members'):
                    party = self.party_manager.members
                
                if not party:
                    return
                
                current_floor = getattr(self.world, 'current_floor', 1) if hasattr(self, 'world') else 1
                steps_taken = getattr(self, 'steps_since_last_encounter', 0)
                
                encounter = self.encounter_manager.check_encounter(party, current_floor, steps_taken)
                if encounter:
                    self.handle_encounter(encounter)
                    self.steps_since_last_encounter = 0
            else:
                # 간단한 랜덤 인카운터 (최종 폴백)
                import random
                if random.random() < 0.03:  # 3% 확률
                    print(f"\n⚔️ {bright_red('적과 마주쳤습니다!')}")
                    self.keyboard.wait_for_key("아무 키나 눌러 전투 시작...")
                    self.start_battle()
                    
        except Exception as e:
            print(f"⚠️ 강화된 인카운터 처리 중 오류 발생!")
            print(f"오류 내용: {e}")
            print(f"오류 타입: {type(e).__name__}")
            import traceback
            print("상세한 오류 정보:")
            traceback.print_exc()
            print("\n" + "="*50)
            print("❌ 인카운터 시스템에 문제가 있습니다.")
            print("게임을 계속 진행하지만, 랜덤 조우가 일시적으로 비활성화됩니다.")
            input("🔍 오류 내용을 확인한 후 아무 키나 눌러 계속...")
    
    def handle_enhanced_encounter(self, encounter_result):
        """🔥 강화된 조우 결과 처리"""
        try:
            if not encounter_result:
                return
            
            success = encounter_result.get('success', False)
            message = encounter_result.get('message', '알 수 없는 결과입니다.')
            
            # 결과 메시지 표시 (통합된 버전)
            print(f"\n{bright_cyan('='*50)}")
            if success:
                print(f"{bright_green('✅ 성공!')}")
            else:
                print(f"{bright_red('❌ 실패!')}")
            print(f"{bright_white(message)}")
            print(f"{bright_cyan('='*50)}")
            
            # ⏳ 메시지 확인 위해 2초 대기 (엔터로 스킵 가능)
            if hasattr(self, 'gauge_animator'):
                self.gauge_animator._wait_with_skip_option(2.0, "인카운터 결과 확인")
            
            # 보상 처리
            rewards = encounter_result.get('rewards', {})
            if rewards:
                print(f"\n{bright_yellow('🎁 획득한 보상:')}")
                
                for reward_type, value in rewards.items():
                    if reward_type == 'gold' and value > 0:
                        # 파티 골드 증가 (파티 매니저 통해)
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            # 첫 번째 파티원의 골드에 추가 (파티 공용)
                            self.party_manager.members[0].gold += value
                            print(f"  💰 골드 +{value}")
                    
                    elif reward_type == 'exp' and value > 0:
                        # 경험치 분배
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            # 특성 보너스 적용
                            bonus_exp = self.apply_exp_bonus(value) if hasattr(self, 'apply_exp_bonus') else value
                            exp_per_member = bonus_exp // len(self.party_manager.members)
                            for member in self.party_manager.members:
                                if member.is_alive:
                                    member.experience += exp_per_member
                            print(f"  ⭐ 경험치 +{bonus_exp} (파티원당 {exp_per_member})")
                    
                    elif reward_type == 'item':
                        try:
                            item_name = str(value)
                            # 인벤토리 시스템 존재 시 첫 멤버 인벤토리에 추가
                            if hasattr(self, 'party_manager') and self.party_manager.members and hasattr(self.party_manager.members[0], 'inventory'):
                                inv = self.party_manager.members[0].inventory
                                if hasattr(inv, 'add_item_by_name'):
                                    success = inv.add_item_by_name(item_name, 1)
                                elif hasattr(inv, 'add_item'):
                                    success = inv.add_item(item_name)
                                else:
                                    success = False
                                if success:
                                    print(f"  🎁 아이템 획득: {item_name}")
                                else:
                                    print(f"  📦 인벤토리 부족으로 {item_name} 보관 실패")
                            else:
                                print(f"  🎁 아이템 획득: {item_name} (임시)" )
                        except Exception as _e:
                            print(f"  ⚠️ 아이템 처리 실패: {value} ({_e})")
                    
                    elif reward_type == 'blessing':
                        turns = int(value) if str(value).isdigit() else 3
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            for m in self.party_manager.members:
                                if not hasattr(m, 'status_effects'):
                                    m.status_effects = []
                                # 간단한 버프 토큰
                                m.status_effects.append({ 'type': 'blessing', 'turns': turns, 'atk_bonus': 0.1 })
                        print(f"  ✨ 축복 효과 ({turns}턴) - 공격력 +10% (임시 적용)")
                    
                    elif reward_type == 'item':
                        # value: 아이템 이름 또는 리스트/튜플
                        items_to_add = []
                        if isinstance(value, (list, tuple)):
                            items_to_add.extend(value)
                        else:
                            items_to_add.append(value)
                        added = 0
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            inv = getattr(self.party_manager.members[0], 'inventory', None)
                            if inv:
                                for item_name in items_to_add:
                                    if not item_name:
                                        continue
                                    # 두 가지 API 모두 시도
                                    success = False
                                    if hasattr(inv, 'add_item_by_name'):
                                        try:
                                            success = inv.add_item_by_name(item_name, 1)
                                        except Exception:
                                            success = False
                                    if not success and hasattr(inv, 'add_item'):
                                        # 아이템 팩토리 생성 시도
                                        try:
                                            from game.items import ItemFactory
                                            factory_item = ItemFactory.create_item(item_name)
                                            success = inv.add_item(factory_item, 1)
                                        except Exception:
                                            success = False
                                    if success:
                                        added += 1
                                        print(f"  🎁 아이템 획득: {item_name}")
                        if added == 0:
                            print(f"  ⚠️ 아이템 '{value}' 지급 실패 (인벤토리 없음 또는 생성 실패)")
                    
                    elif reward_type == 'blessing':
                        # 파티 전원에게 임시 blessing 스택 부여 (value = 턴 수)
                        turns = int(value) if isinstance(value, int) else 3
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            for member in self.party_manager.members:
                                if not hasattr(member, 'status_manager'):
                                    continue
                                try:
                                    # status_manager 기반이면 사용
                                    if hasattr(member.status_manager, 'add_status'):
                                        member.status_manager.add_status('blessing', duration=turns)
                                    else:
                                        # 단순 속성 스택
                                        current = getattr(member, 'blessing_stacks', 0)
                                        setattr(member, 'blessing_stacks', current + 1)
                                        setattr(member, 'blessing_turns', turns)
                                except Exception:
                                    pass
                            print(f"  ✨ 축복 효과 적용 ({turns}턴)")
                        else:
                            print("  ⚠️ 축복 적용 대상 파티 없음")
                    
                    elif reward_type == 'info':
                        # 간단한 현재 층 맵 타일 일부 공개 예시
                        revealed = False
                        if hasattr(self, 'world') and hasattr(self.world, 'tiles') and hasattr(self.world, 'player_pos'):
                            try:
                                px, py = self.world.player_pos
                                radius = 5
                                for y in range(max(0, py - radius), min(len(self.world.tiles), py + radius + 1)):
                                    for x in range(max(0, px - radius), min(len(self.world.tiles[0]), px + radius + 1)):
                                        tile = self.world.tiles[y][x]
                                        if hasattr(tile, 'discovered'):
                                            tile.discovered = True
                                revealed = True
                            except Exception:
                                revealed = False
                        if revealed:
                            print("  📜 주변 지형 정보가 드러났습니다!")
                        else:
                            print("  📜 유용한 정보 획득 (맵 공개 실패)")
            # 효과 처리
            effects = encounter_result.get('effects', {})
            if effects:
                print(f"\n{bright_cyan('🌟 적용된 효과:')}")
                
                for effect_type, value in effects.items():
                    if effect_type == 'heal' and hasattr(self, 'party_manager'):
                        # 비율 기반 치유
                        for member in self.party_manager.members:
                            if member.is_alive:
                                heal_amount = int(member.max_hp * value)
                                old_hp = member.current_hp
                                member.current_hp = min(member.max_hp, member.current_hp + heal_amount)
                                actual_heal = member.current_hp - old_hp
                                if actual_heal > 0:
                                    print(f"  💚 {member.name} HP +{actual_heal}")
                        
                        # ⏳ 치유 효과 확인 위해 2초 대기 (엔터로 스킵 가능)
                        if hasattr(self, 'gauge_animator'):
                            self.gauge_animator._wait_with_skip_option(2.0, "치유 효과 확인")
                    
                    elif effect_type == 'blessing':
                        print(f"  ✨ 파티 축복 ({value}턴)")
                        # 실제 버프 적용 (구현 필요)
            
            # 패널티 처리
            penalties = encounter_result.get('penalties', {})
            combat_started = False
            if penalties:
                print(f"\n{bright_red('⚠️ 받은 패널티:')}")
                last_penalty_type = None
                for penalty_type, value in penalties.items():
                    last_penalty_type = penalty_type
                    if penalty_type == 'damage' and hasattr(self, 'party_manager'):
                        import random
                        alive_members = [m for m in self.party_manager.members if m.is_alive]
                        if alive_members:
                            target = random.choice(alive_members)
                            actual_damage = min(value, target.current_hp - 1)  # 즉사 방지
                            target.current_hp -= actual_damage
                            print(f"  💔 {target.name}이 {actual_damage} 피해를 받았습니다!")
                            if hasattr(self, 'gauge_animator'):
                                self.gauge_animator._wait_with_skip_option(2.0, "피해 효과 확인")
                    elif penalty_type == 'combat':
                        print("  ⚔️ 전투 발생!")
                        self.start_battle()
                        combat_started = True
                        break
                # 전투가 시작되지 않은 경우에만 대기
                if not combat_started:
                    self.keyboard.wait_for_key(f"{bright_green('✅ 아무 키나 눌러 계속...')}")
            else:
                # 패널티가 없으면 바로 진행
                self.keyboard.wait_for_key(f"{bright_green('✅ 아무 키나 눌러 계속...')}")
            
        except Exception as e:
            print(f"⚠️ 강화된 조우 결과 처리 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
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
                                    print(f"🌿 HP +1 (걸음 {steps})")
            
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
                                    print(f"🌿 MP +1 (걸음 {steps})")
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
        import random
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
                            # 실제 골드 지급 - 통일된 시스템 사용
                            self.add_gold(value)
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
                    
                    elif effect == 'elite_encounter_4':
                        print(f"\n⚔️ {bright_red('몬스터 소굴에서 4마리의 강력한 적이 나타났습니다!')}")
                        print("💀 4마리 엘리트 몬스터와의 전투가 시작됩니다!")
                        time.sleep(1.5)
                        
                        # 4마리 엘리트 몬스터 전투 시작
                        self.start_elite_battle_4()
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
                                    self.add_gold(gold_amount)
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
                        from game.cursor_menu_system import CursorMenu
                        training_menu = CursorMenu(
                            "🎯 훈련 받기",
                            ["💪 훈련을 받습니다", "🚶 훈련을 받지 않습니다"],
                            ["스탯이 영구적으로 증가합니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = training_menu.run()
                        if choice == 0:  # 훈련 받기
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
                        from game.cursor_menu_system import CursorMenu
                        cursed_menu = CursorMenu(
                            "⚠️ 저주받은 제단",
                            ["🔍 제단을 조사합니다", "🚶 제단을 건드리지 않습니다"],
                            ["위험하지만 강력한 힘을 얻을 수 있습니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = cursed_menu.run()
                        if choice == 0:  # 조사하기
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
                        from game.cursor_menu_system import CursorMenu
                        time_menu = CursorMenu(
                            "⏰ 시간 균열",
                            ["⚡ 시간 균열에 접근합니다", "🚶 시간 균열을 피해 갑니다"],
                            ["위험하지만 시간의 힘을 얻을 수 있습니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = time_menu.run()
                        if choice == 0:  # 접근하기
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
                        from game.cursor_menu_system import CursorMenu
                        shadow_menu = CursorMenu(
                            "🌑 그림자 통로",
                            ["🌟 그림자 통로를 이용합니다", "🚶 일반 길로 갑니다"],
                            ["빠르게 이동하지만 위험할 수 있습니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = shadow_menu.run()
                        if choice == 0:  # 그림자 통로 이용
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
                        from game.cursor_menu_system import CursorMenu
                        blessing_menu = CursorMenu(
                            "⛪ 신성한 신전",
                            ["🙏 신전에서 기도합니다", "🚶 신전을 지나칩니다"],
                            ["신성한 축복으로 HP와 MP가 회복됩니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = blessing_menu.run()
                        if choice == 0:  # 기도하기
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
                        from game.cursor_menu_system import CursorMenu
                        knowledge_menu = CursorMenu(
                            "📚 고대 서적",
                            ["📖 고대 서적을 읽습니다", "🚶 서적을 읽지 않습니다"],
                            ["고대의 지식으로 경험치를 얻습니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = knowledge_menu.run()
                        if choice == 0:  # 서적 읽기
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
                        from game.cursor_menu_system import CursorMenu
                        shop_menu = CursorMenu(
                            "🚛 떠도는 상인",
                            ["🛍️ 상인과 거래합니다", "🚶 거래하지 않습니다"],
                            ["프리미엄 상점에서 특별한 상품을 구매할 수 있습니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = shop_menu.run()
                        if choice == 0:  # 거래하기
                            print(f"🏪 {bright_green('프리미엄 상점이 열렸습니다!')} 특별한 상품들을 확인하세요.")
                            # 프리미엄 상점 열기 (구현 필요)
                        else:
                            print("🚶 상인과 거래하지 않고 지나갑니다.")
                    
                    elif effect.startswith('element_boost_'):
                        element = effect.replace('element_boost_', '')
                        boost_value = encounter.get('effect_value', 20)
                        
                        from game.cursor_menu_system import CursorMenu
                        element_menu = CursorMenu(
                            f"🔮 {element} 원소 노드",
                            [f"⚡ {element} 원소 노드를 활성화합니다", "🚶 원소 노드를 건드리지 않습니다"],
                            [f"{element} 속성 공격력이 {boost_value}% 증가합니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = element_menu.run()
                        if choice == 0:  # 활성화
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
                        from game.cursor_menu_system import CursorMenu
                        weapon_menu = CursorMenu(
                            "⚔️ 무기 선택",
                            ["⚔️ 무기를 선택합니다", "🚶 무기를 가져가지 않습니다"],
                            ["좋은 무기로 공격력이 증가합니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = weapon_menu.run()
                        if choice == 0:  # 무기 선택
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
                        from game.cursor_menu_system import CursorMenu
                        spell_menu = CursorMenu(
                            "🔯 마법진",
                            ["✨ 마법진에서 마법을 배웁니다", "🚶 마법을 배우지 않습니다"],
                            ["강력한 마법을 배워 마법 공격력이 증가합니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = spell_menu.run()
                        if choice == 0:  # 마법 배우기
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
                        from game.cursor_menu_system import CursorMenu
                        hermit_menu = CursorMenu(
                            "🧙 현명한 은둔자",
                            ["🎓 은둔자의 조언을 듣습니다", "🚶 조언을 듣지 않습니다"],
                            ["고대의 지혜로 파티 전체 능력이 향상됩니다", "안전하게 지나갑니다"],
                            audio_manager=getattr(self, 'audio_manager', None),
                            keyboard=self.keyboard,
                            clear_screen=True
                        )
                        
                        choice = hermit_menu.run()
                        if choice == 0:  # 조언 듣기
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
                
                from game.cursor_menu_system import CursorMenu
                field_skill_menu = CursorMenu(
                    "💫 필드 스킬 사용",
                    ["💫 필드 스킬을 사용합니다", "⏭️ 필드 스킬을 사용하지 않습니다"],
                    ["사용 가능한 필드 스킬로 상황을 해결합니다", "필드 스킬 없이 계속합니다"],
                    audio_manager=getattr(self, 'audio_manager', None),
                    keyboard=self.keyboard,
                    clear_screen=True
                )
                
                use_skill_choice = field_skill_menu.run()
                if use_skill_choice == 0:  # 필드 스킬 사용
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
    
    def _check_and_spawn_floor_boss(self):
        """3층마다 보스 등장 체크 및 생성"""
        current_floor = getattr(self, 'current_floor', 1)
        
        # 3층마다 보스 등장 (3, 6, 9, 12...)
        if current_floor % 3 == 0 and current_floor < 30:  # 30층은 세피로스 전용
            # 계단 위치 찾기
            stairs_pos = None
            for y in range(len(self.world.dungeon.grid)):
                for x in range(len(self.world.dungeon.grid[y])):
                    if self.world.dungeon.grid[y][x].type.value == ">":  # 아래층 계단
                        stairs_pos = (x, y)
                        break
                if stairs_pos:
                    break
            
            if stairs_pos:
                # 계단 주변에 보스 스폰
                boss_x, boss_y = self._find_boss_spawn_near_stairs(stairs_pos)
                if boss_x is not None and boss_y is not None:
                    # 보스 마커 설치
                    from game.world import TileType
                    self.world.dungeon.grid[boss_y][boss_x].type = TileType.BOSS
                    
                    # 보스 생성
                    boss = self._create_floor_boss(current_floor)
                    if hasattr(self.world, 'enemies'):
                        self.world.enemies.append(boss)
                    else:
                        self.world.enemies = [boss]
                    
                    # 보스 근처에 추가 잡몹 배치
                    self._spawn_minions_near_boss(boss_x, boss_y, current_floor)
                    
                    print(f"👑 {current_floor}층 보스 '{boss.name}'이(가) 계단 근처에 등장했습니다!")
                    return True
        return False
    
    def _find_boss_spawn_near_stairs(self, stairs_pos):
        """계단 주변의 적절한 보스 스폰 위치 찾기"""
        stairs_x, stairs_y = stairs_pos
        
        # 계단 주변 3x3 영역에서 빈 공간 찾기
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:  # 계단 자체는 제외
                    continue
                    
                new_x, new_y = stairs_x + dx, stairs_y + dy
                
                # 범위 체크
                if (0 <= new_x < len(self.world.dungeon.grid[0]) and 
                    0 <= new_y < len(self.world.dungeon.grid)):
                    
                    tile = self.world.dungeon.grid[new_y][new_x]
                    # 빈 바닥이면 보스 스폰 가능
                    if tile.type.value == ".":
                        return new_x, new_y
        
        # 3x3에서 못 찾으면 5x5로 확장
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if abs(dx) <= 1 and abs(dy) <= 1:  # 이미 체크한 영역은 제외
                    continue
                    
                new_x, new_y = stairs_x + dx, stairs_y + dy
                
                if (0 <= new_x < len(self.world.dungeon.grid[0]) and 
                    0 <= new_y < len(self.world.dungeon.grid)):
                    
                    tile = self.world.dungeon.grid[new_y][new_x]
                    if tile.type.value == ".":
                        return new_x, new_y
        
        return None, None
    
    def _spawn_minions_near_boss(self, boss_x, boss_y, floor):
        """보스 근처에 잡몹 배치"""
        try:
            # 층수에 따른 잡몹 수 결정 (3-6마리)
            minion_count = min(3 + (floor // 6), 6)
            
            # 보스 주변 7x7 영역에서 잡몹 배치
            spawn_positions = []
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    if dx == 0 and dy == 0:  # 보스 위치는 제외
                        continue
                        
                    new_x, new_y = boss_x + dx, boss_y + dy
                    
                    # 범위 체크
                    if (0 <= new_x < len(self.world.dungeon.grid[0]) and 
                        0 <= new_y < len(self.world.dungeon.grid)):
                        
                        tile = self.world.dungeon.grid[new_y][new_x]
                        # 빈 바닥이면 잡몹 스폰 가능
                        if tile.type.value == ".":
                            spawn_positions.append((new_x, new_y))
            
            # 랜덤하게 위치 선택해서 잡몹 배치
            import random
            selected_positions = random.sample(spawn_positions, min(minion_count, len(spawn_positions)))
            
            spawned_count = 0
            for pos_x, pos_y in selected_positions:
                # 잡몹 생성
                minion = self._create_boss_minion(floor)
                
                # 잡몹을 적 리스트에 추가
                if hasattr(self.world, 'enemies'):
                    self.world.enemies.append(minion)
                else:
                    self.world.enemies = [minion]
                
                # 잡몹 위치 설정 (나중에 확장 가능)
                minion.spawn_x = pos_x
                minion.spawn_y = pos_y
                
                spawned_count += 1
            
            if spawned_count > 0:
                print(f"⚔️ 보스 근처에 {spawned_count}마리의 잡몹이 추가로 등장했습니다!")
                
        except Exception as e:
            print(f"⚠️ 잡몹 생성 오류: {e}")
    
    def _create_boss_minion(self, floor):
        """보스 층 잡몹 생성 (일반 잡몹보다 강함)"""
        try:
            from game.character import Character
            
            # 잡몹 이름 리스트
            minion_names = [
                "정예 병사", "강화 골렘", "마법 파수꾼", "어둠의 정찰병", "용족 전사",
                "불꽃 정령", "얼음 정령", "번개 정령", "독 거미", "강철 늑대",
                "마법 기사", "암흑 마법사", "치유 수도승", "바람 무희", "대지 수호자"
            ]
            
            import random
            minion_name = random.choice(minion_names)
            
            # 잡몹 생성
            minion = Character(minion_name, "정예병")
            
            # 기본 스탯 (일반 잡몹보다 50% 강함)
            base_level = min(floor + 2, 40)
            minion.level = base_level
            
            base_hp = 200 + (floor * 40)
            base_mp = 50 + (floor * 10)
            base_attack = 40 + (floor * 8)
            base_defense = 30 + (floor * 6)
            base_speed = 80 + (floor * 5)
            base_brv = 150 + (floor * 15)
            
            # 정예병 보너스 +50%
            elite_multiplier = 1.5
            
            minion.max_hp = int(base_hp * elite_multiplier)
            minion.current_hp = minion.max_hp
            minion.max_mp = int(base_mp * elite_multiplier)
            minion.current_mp = minion.max_mp
            minion.physical_attack = int(base_attack * elite_multiplier)
            minion.magic_attack = int(base_attack * elite_multiplier)
            minion.physical_defense = int(base_defense * elite_multiplier)
            minion.magic_defense = int(base_defense * elite_multiplier)
            minion.speed = int(base_speed * elite_multiplier)
            minion.max_brv = int(base_brv * elite_multiplier)
            minion.brave_points = minion.max_brv
            
            # 정예병 플래그
            minion.is_elite = True
            minion.boss_floor = floor
            
            return minion
            
        except Exception as e:
            print(f"⚠️ 잡몹 생성 오류: {e}")
            # 기본 잡몹으로 대체
            from game.character import Character
            basic_minion = Character("정예 병사", "정예병")
            basic_minion.max_hp = 300
            basic_minion.current_hp = 300
            basic_minion.physical_attack = 60
            return basic_minion
    
    def _create_floor_boss(self, floor):
        """층별 보스 생성 (올스탯 +80%, HP 레이드급, BRV 증가)"""
        try:
            from game.character import Character
            
            # 보스 이름 리스트 (층별로 다른 보스)
            boss_names = [
                "골렘 왕", "용암 거인", "얼음 마왕", "번개 군주", "독 마스터",
                "암흑 기사", "빛의 수호자", "바람의 지배자", "대지의 정령", "바다의 왕",
                "불꽃 용", "얼음 용", "폭풍 용", "독 용", "암흑 용",
                "천사장", "악마 공작", "정령 왕", "언데드 로드", "기계 황제"
            ]
            
            # 층에 따른 보스 선택
            boss_index = (floor // 3 - 1) % len(boss_names)
            boss_name = boss_names[boss_index]
            
            # 보스 생성
            boss = Character(boss_name, "보스")
            
            # 기본 스탯 계산 (층수에 비례)
            base_level = min(floor + 5, 50)
            boss.level = base_level
            
            # 기본 스탯
            base_hp = 2000 + (floor * 500)  # 훨씬 더 많은 레이드급 HP
            base_mp = 200 + (floor * 50)
            base_attack = 80 + (floor * 15)
            base_defense = 60 + (floor * 12)
            base_speed = 100 + (floor * 8)
            base_brv = 300 + (floor * 30)
            
            # 올스탯 +80% 적용
            bonus_multiplier = 1.8
            
            boss.max_hp = int(base_hp * bonus_multiplier)
            boss.current_hp = boss.max_hp
            boss.max_mp = int(base_mp * bonus_multiplier)
            boss.current_mp = boss.max_mp
            boss.physical_attack = int(base_attack * bonus_multiplier)
            boss.magic_attack = int(base_attack * bonus_multiplier)
            boss.physical_defense = int(base_defense * bonus_multiplier)
            boss.magic_defense = int(base_defense * bonus_multiplier)
            boss.speed = int(base_speed * bonus_multiplier)
            boss.max_brv = int(base_brv * bonus_multiplier)
            boss.brave_points = boss.max_brv
            
            # 보스 플래그 설정
            boss.is_boss = True
            boss.boss_floor = floor
            
            print(f"👑 {floor}층 보스 생성: {boss_name} (HP: {boss.max_hp}, 공격력: {boss.physical_attack})")
            
            return boss
            
        except Exception as e:
            print(f"⚠️ 보스 생성 오류: {e}")
            # 기본 보스로 대체
            from game.character import Character
            basic_boss = Character("던전 보스", "보스")
            basic_boss.max_hp = 2000
            basic_boss.current_hp = 2000
            basic_boss.physical_attack = 150
            basic_boss.is_boss = True
            return basic_boss
    
    def _trigger_sephiroth_encounter(self):
        """30층에서 세피로스 조우 이벤트"""
        if not self.story_system:
            return
            
        # 세피로스 조우 스토리 재생
        try:
            # BGM 변경 (세피로스 전용 BGM)
            if hasattr(self, 'audio_system') and self.audio_system:
                try:
                    # 세피로스 전용 BGM - One Winged Angel
                    self.audio_system.play_bgm("one_winged_angel")
                except:
                    try:
                        # 폴백: 보스 테마
                        self.audio_system.play_bgm("sephiroth_theme")
                    except:
                        pass
            
            # 스토리 재생
            sephiroth_story = self.story_system.get_sephiroth_encounter_story()
            self.story_system.display_story_with_typing_effect(sephiroth_story)
            
            # 세피로스 조우 플래그 설정
            self.story_system.set_sephiroth_encountered(True)
            
            print("\n💀 세피로스와의 전투가 시작됩니다!")
            input("🎮 아무 키나 눌러 계속...")
            
            # 세피로스 보스전 시작
            self._start_sephiroth_boss_battle()
            
        except Exception as e:
            print(f"⚠️ 세피로스 조우 이벤트 오류: {e}")
    
    def _start_sephiroth_boss_battle(self):
        """세피로스 보스전 시작"""
        try:
            # 세피로스 캐릭터 생성
            sephiroth = self._create_sephiroth_boss()
            
            # 전투 시스템 초기화
            from game.brave_combat import BraveCombatSystem
            combat_system = BraveCombatSystem(
                audio_system=getattr(self, 'audio_system', None),
                sound_manager=getattr(self, 'sound_manager', None)
            )
            
            # 보스전 시작
            print("\n💀 최종 보스 세피로스와의 전투!")
            result = combat_system.start_battle(
                party=self.party_manager.members,
                enemies=[sephiroth],
                is_boss_battle=True
            )
            
            # 전투 결과 처리
            if result == "victory":
                self._handle_sephiroth_defeat()
            else:
                print("💀 세피로스에게 패배했습니다...")
                print("하지만 포기하지 마세요. 다시 도전할 수 있습니다!")
                
        except Exception as e:
            print(f"⚠️ 세피로스 보스전 오류: {e}")
    
    def _create_sephiroth_boss(self):
        """세피로스 보스 캐릭터 생성"""
        try:
            from game.character import Character
            
            # 세피로스 스탯 (압도적인 최종 보스)
            sephiroth = Character("세피로스", "최종보스")
            sephiroth.level = 60  # 최고 레벨
            sephiroth.max_hp = 50000  # 일반 보스보다 훨씬 많은 HP
            sephiroth.current_hp = 50000
            sephiroth.max_mp = 2000  # 강력한 스킬 사용을 위한 높은 MP
            sephiroth.current_mp = 2000
            sephiroth.physical_attack = 1200  # 일반 보스보다 강한 공격력
            sephiroth.magic_attack = 1400  # 마법 공격이 더 강함
            sephiroth.physical_defense = 800  # 높은 방어력
            sephiroth.magic_defense = 900  # 마법 방어도 높음
            sephiroth.speed = 550  # 빠른 속도
            sephiroth.max_brv = 3000  # 매우 높은 BRV
            sephiroth.brave_points = 3000
            
            # 특수 능력들
            sephiroth.boss_abilities = [
                "마사무네_베기",
                "슈퍼노바",
                "절망의_날개",
                "차원_붕괴",
                "메테오",
                "옥타슬래시"
            ]
            
            return sephiroth
            
        except Exception as e:
            print(f"⚠️ 세피로스 생성 오류: {e}")
            # 기본 적으로 대체
            from game.character import Character
            return Character("세피로스", "보스")
    
    def _handle_sephiroth_defeat(self):
        """세피로스 처치 후 처리"""
        if not self.story_system:
            return
            
        # 세피로스 처치 플래그 설정
        self.story_system.set_sephiroth_defeated(True)
        
        # 진 엔딩 스토리 재생
        try:
            # BGM 변경 (승리 테마)
            if hasattr(self, 'audio_system') and self.audio_system:
                try:
                    self.audio_system.play_bgm("victory_theme")
                except:
                    pass
            
            # 진 엔딩 스토리 재생
            true_ending_story = self.story_system.get_true_ending_story()
            self.story_system.display_story_with_typing_effect(true_ending_story)
            
            print("\n🌟 축하합니다! 진정한 엔딩을 달성했습니다!")
            print("세피로스를 처치하고 세계를 구원했습니다!")
            
            # 특별한 보상 지급
            print("\n🎁 진 엔딩 달성 보상:")
            print("• 🏆 진정한 영웅 칭호")
            print("• 💎 세피로스의 유품")
            print("• ⭐ 특별한 스킬 해금")
            
            input("🎮 아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"⚠️ 진 엔딩 처리 오류: {e}")
    
    def advance_to_next_floor(self):
        """다음 층으로 진행"""
        # 🎯 다음 층 이동 확인 메시지
        old_floor = self.world.current_level
        new_floor = old_floor + 1
        
        print(f"\n🏢 다음 층으로 이동")
        print("=" * 50)
        print(f"현재 층: {old_floor}층")
        print(f"이동할 층: {new_floor}층")
        print("=" * 50)
        
        # 커서 메뉴로 확인
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "🚀 네, 다음 층으로 이동합니다",
                "🔄 아니오, 현재 층에 머물겠습니다"
            ]
            
            descriptions = [
                f"{new_floor}층으로 이동하여 새로운 모험을 계속합니다",
                f"{old_floor}층에 머물러 더 탐험하거나 준비를 합니다"
            ]
            
            menu = CursorMenu("🏢 다음 층 이동 확인", options, descriptions, cancellable=True)
            choice = menu.run()
            
            if choice == 1 or choice == -1:  # "아니오" 선택 또는 취소
                print("🔄 현재 층에 머물겠습니다.")
                return False
                
        except ImportError:
            # 커서 메뉴 실패 시 기본 입력 방식 사용
            print("다음 층으로 이동하시겠습니까?")
            while True:
                user_input = input("(y/n): ").strip().lower()
                if user_input in ['y', 'yes', '네', 'ㅇ']:
                    break
                elif user_input in ['n', 'no', '아니오', 'ㄴ']:
                    print("🔄 현재 층에 머물겠습니다.")
                    return False
                else:
                    print("y 또는 n을 입력해주세요.")
        
        # 실제 층 이동 진행
        self.world.current_level = new_floor
        self.current_floor = new_floor
        
        print(f"\n🏢 {old_floor}층에서 {new_floor}층으로 이동합니다...")
        
        # 30층 도달 시 세피로스 조우 체크
        if new_floor == 30 and self.story_system and not self.story_system.sephiroth_encountered:
            self._trigger_sephiroth_encounter()
        
        # 특정 층 도달시 챕터 인트로 표시
        if STORY_SYSTEM_AVAILABLE and new_floor in [1, 5, 10, 15, 20, 25, 30]:
            try:
                # 스토리 실행 전 BGM 일시정지
                current_bgm_paused = False
                if hasattr(self, 'audio_system') and self.audio_system:
                    try:
                        import pygame
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                            current_bgm_paused = True
                    except:
                        pass
                
                chapter = (new_floor - 1) // 5 + 1
                show_chapter_intro(chapter)
                input(f"{bright_green('[Enter 키를 눌러 계속]')}")
                
                # 스토리 종료 후 BGM 재개
                if current_bgm_paused and hasattr(self, 'audio_system') and self.audio_system:
                    try:
                        import pygame
                        pygame.mixer.music.unpause()
                    except:
                        # 재개 실패 시 다시 재생
                        self.safe_set_floor_bgm(new_floor)
                        
            except Exception as e:
                print(f"⚠️ 챕터 인트로 표시 중 오류: {e}")
        
        # 이전 층 조우 현황 표시
        if hasattr(self, 'encounter_manager') and self.encounter_manager:
            old_floor_status = self.encounter_manager.get_floor_encounter_status(old_floor)
            print(f"📊 {old_floor_status}")
            
            # 새 층 조우 정보 안내
            new_floor_info = self.encounter_manager.get_floor_encounter_status(new_floor)
            print(f"🎯 {new_floor_info}")
        
        # 층 진행 플래그 설정
        self._floor_advanced = True
        
        # auto_save 기능 확인 및 실행
        if self.permanent_progression.has_ability("auto_save"):
            print("💾 자동 저장 중...")
            self.auto_save_game()
        
        # 새 층 생성
        self.world.generate_level()
        
        # 3층마다 보스 체크 및 생성
        self._check_and_spawn_floor_boss()
        
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
                    choice = self.keyboard.get_input().lower()
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
        """메인 메뉴 BGM 재생 (스마트 중복 방지)"""
        try:
            # 🔇 강제 글리치 모드 체크 (최우선)
            if hasattr(self, '_force_glitch_mode') and self._force_glitch_mode:
                print("🔇 [BGM BLOCKED] Force glitch mode - Main menu BGM denied")
                return
            
            # 🔇 일반 글리치 모드 체크
            try:
                if hasattr(self, 'story_system') and self.story_system:
                    if hasattr(self.story_system, 'is_glitch_mode') and self.story_system.is_glitch_mode():
                        print("🔇 [BGM BLOCKED] Glitch mode active - Main menu BGM denied")
                        return
            except:
                pass
            
            # AudioSystem이 있으면 우선 사용
            if hasattr(self, 'audio_system') and self.audio_system:
                # 메인 메뉴 BGM이 이미 재생 중인지 확인
                if hasattr(self.audio_system, 'current_bgm_type'):
                    from game.audio_system import BGMType
                    if self.audio_system.current_bgm_type == BGMType.MENU:
                        return  # 이미 메인 메뉴 BGM이 재생 중이므로 재시작하지 않음
                
                from game.audio_system import BGMType
                self.audio_system.play_bgm(BGMType.MENU, loop=True)
                return
            
            # audio_system이 없는 경우 조용히 스킵
            print("🔇 오디오 시스템이 없어 BGM을 재생할 수 없습니다.")
            
        except Exception as e:
            print(f"⚠️ BGM 재생 실패: {e}")

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
    
    def _show_gamepad_status(self):
        """게임패드 연결 상태 표시"""
        try:
            # UnifiedInputManager에서 게임패드 확인
            if (hasattr(self.keyboard, 'gamepad') and 
                self.keyboard.gamepad is not None and 
                hasattr(self.keyboard.gamepad, 'is_available') and
                self.keyboard.gamepad.is_available()):
                
                gamepad_name = self.keyboard.gamepad.joystick.get_name()
                print(f"{bright_green('🎮 게임패드 연결됨:')} {bright_yellow(gamepad_name)}")
                print(f"{bright_cyan('   ├ 방향키:')} D-패드 또는 왼쪽 스틱")
                print(f"{bright_cyan('   ├ 확인:')} A 버튼 (또는 Enter)")
                print(f"{bright_cyan('   ├ 취소:')} B 버튼 (또는 Q)")
                print(f"{bright_cyan('   ├ 메뉴:')} X 버튼")
                print(f"{bright_cyan('   └ 인벤토리:')} Y 버튼")
            else:
                print(f"{bright_yellow('⌨️  키보드 입력 모드')} (게임패드 미연결)")
                print(f"{bright_cyan('   💡 게임패드를 연결하면 자동으로 인식됩니다')}")
        except Exception as e:
            print(f"{bright_yellow('⌨️  키보드 입력 모드')} (게임패드 초기화 실패: {str(e)})")
            # 디버그 정보 출력
            if hasattr(self.keyboard, 'gamepad'):
                print(f"{bright_cyan('   🔧 디버그:')} keyboard.gamepad = {self.keyboard.gamepad}")
            else:
                print(f"{bright_cyan('   🔧 디버그:')} keyboard에 gamepad 속성 없음")
        
    def _handle_playing_state(self):
        """플레이 상태 처리"""
        pass
        
    def _handle_paused_state(self):
        """일시정지 상태 처리"""
        pass
        
    def _handle_game_over_state(self):
        """게임 오버 상태 처리"""
        print("\n💀 게임 오버!")
        print("="*50)
        
        # 게임오버 수집 시스템 처리
        if hasattr(self, 'meta_progression') and self.meta_progression:
            if hasattr(self, 'current_player') and self.current_player:
                try:
                    # 플레이어 인벤토리에서 아이템 수집
                    salvaged_items = self.meta_progression.handle_game_over_salvage(
                        self.current_player.inventory
                    )
                    
                    if salvaged_items:
                        print(f"✅ {len(salvaged_items)}개의 아이템을 구출했습니다!")
                    
                except Exception as e:
                    print(f"⚠️ 아이템 수집 중 오류: {e}")
        
        # 게임 상태를 메뉴로 변경
        if hasattr(self, 'game_manager') and self.game_manager:
            self.game_manager.current_state = GameState.MENU
        
    def main_loop(self):
        """메인 게임 루프 - 고급 시스템 통합"""
        # 오프닝 스토리 표시 (게임 최초 실행 시)
        if STORY_SYSTEM_AVAILABLE:
            try:
                # 스토리는 자체 BGM을 사용하므로 메인 메뉴 BGM을 미리 시작하지 않음
                # 글리치 모드 체크하여 적절한 스토리 재생
                if self.story_system and self.story_system.is_glitch_mode():
                    # 변조된 스토리 재생
                    corrupted_story = self.story_system.get_corrupted_opening_story()
                    self.story_system.display_story_with_typing_effect(corrupted_story)
                else:
                    # 일반 스토리 재생
                    show_opening_story()
                
                # 스토리 후 화면을 완전히 클리어하고 메뉴 준비
                print("\033[2J\033[H")  # 화면 완전 클리어
                time.sleep(0.3)  # 짧은 대기
                        
            except Exception as e:
                print(f"⚠️ 오프닝 스토리 표시 중 오류: {e}")
                print("메뉴로 진행합니다...")
        
        # 🎮 게임 매니저가 없으면 직접 메뉴 처리
        if not self.game_manager:
            # 메뉴 표시 전 화면 클리어 보장
            print("\033[2J\033[H")
            # 간단한 메뉴 루프 - 오프닝 후 메뉴가 표시되도록 보장
            while self.running:
                try:
                    self._handle_menu_state()
                    if not self.running:
                        break
                    # 메뉴 처리 후 잠시 대기 (무한 루프 방지)
                    time.sleep(0.1)
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
                    "별조각 아이템 상점"
                ]
                
                descriptions = [
                    f"별조각 {star_fragments}개로 새로운 캐릭터를 해금합니다",
                    f"별조각 {star_fragments}개로 캐릭터 특성을 해금합니다",
                    f"별조각 {star_fragments}개로 발견한 아이템을 구매합니다 (레벨/희귀도 제한 없음)"
                ]
                
                # 창고 시스템 추가
                warehouse_unlocked = False
                if hasattr(self, 'meta_progression') and self.meta_progression:
                    warehouse_unlocked = self.meta_progression.data.get("warehouse_unlocked", False)
                
                if warehouse_unlocked:
                    options.append("🏪 창고 관리")
                    descriptions.append("보관된 아이템을 관리하고 창고를 업그레이드합니다")
                else:
                    options.append("🔒 창고 해금 (100 별조각)")
                    descriptions.append("아이템을 보관할 수 있는 창고를 해금합니다")
                
                # 게임오버 수집 시스템 추가
                death_salvage_unlocked = False
                max_salvage = 1
                if hasattr(self, 'meta_progression') and self.meta_progression:
                    death_salvage_unlocked = self.meta_progression.data.get("death_salvage_unlocked", False)
                    max_salvage = self.meta_progression.data.get("max_death_salvage", 1)
                
                if death_salvage_unlocked:
                    options.append(f"💀 수집 업그레이드 (현재: {max_salvage}개)")
                    descriptions.append("게임오버 시 가져올 수 있는 아이템 수를 증가시킵니다")
                else:
                    options.append("🔒 게임오버 수집 해금 (50 별조각)")
                    descriptions.append("게임오버 시 아이템을 가져올 수 있는 기능을 해금합니다")
                
                # 나머지 옵션들
                options.extend([
                    "영구 강화",
                    "업적 확인",
                    "상세 통계",
                    "뒤로 가기"
                ])
                
                descriptions.extend([
                    f"별조각 {star_fragments}개로 영구 능력치를 강화합니다",
                    "달성한 업적과 진행도를 확인합니다",
                    "게임 플레이 통계를 상세히 확인합니다",
                    "메인 메뉴로 돌아갑니다"
                ])
                
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
                
                elif result == 2:  # ⭐ 별조각 아이템 상점
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_star_fragment_item_shop()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                
                elif result == 3:  # 창고 관리 / 창고 해금
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        if self.meta_progression.data.get("warehouse_unlocked", False):
                            self.meta_progression.show_warehouse_menu()
                        else:
                            self.meta_progression.unlock_warehouse()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                
                elif result == 4:  # 게임오버 수집 / 수집 해금
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        if self.meta_progression.data.get("death_salvage_unlocked", False):
                            self.meta_progression.upgrade_death_salvage()
                        else:
                            self.meta_progression.unlock_death_salvage()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 5:  # 영구 강화
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'permanent_progression') and self.permanent_progression:
                        self.permanent_progression.show_menu()
                    else:
                        print("영구 강화 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 6:  # 업적 확인
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_achievements_menu()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 7:  # 상세 통계
                    self.safe_play_sfx("menu_select")
                    if hasattr(self, 'meta_progression') and self.meta_progression:
                        self.meta_progression.show_detailed_statistics()
                    else:
                        print("메타 진행 시스템이 초기화되지 않았습니다.")
                        input("아무 키나 눌러 계속...")
                        
                elif result == 8 or result == -1 or result is None:  # 뒤로 가기
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

    def _get_ascii_art_content(self):
        """아스키 아트 콘텐츠를 문자열로 반환"""
        lines = []
        lines.append("\n" + "="*60)
        lines.append("")
        
        # 🌟 세피로스 조우 후 글리치 모드 체크
        glitch_mode = False
        if hasattr(self, 'story_system') and self.story_system:
            glitch_mode = self.story_system.is_glitch_mode()
        
        if glitch_mode:
            # 글리치 버전 아스키 아트
            lines.append(f"{bright_red('         ██▓▒░ CORRUPTED ░▒▓██'):^20}")
            lines.append(f"{bright_red('         ██░██▓██████▓██░██'):^20}")
            lines.append(f"{bright_magenta('         ▓█░▓█████████▓█░█▓'):^20}")
            lines.append(f"{bright_magenta('         █▓░▓█████████▓░▓█'):^20}")
            lines.append(f"{bright_yellow('         ▓█░▓█████████▓░█▓'):^20}")
            lines.append(f"{bright_yellow('         ░▓██████████████▓░'):^20}")
            lines.append("")
            lines.append(f"{bright_red('     ███▓▒░ERROR░▒▓███'):^20}")
            lines.append(f"{bright_red('     ██CORRUPTED██'):^20}")
            lines.append(f"{bright_magenta('     ███SEPHIROTH███'):^20}")
            lines.append(f"{bright_magenta('     ░▒▓PROTOCOL▓▒░'):^20}")
            lines.append(f"{bright_yellow('     ███████████████'):^20}")
            lines.append(f"{bright_yellow('     ▓▒░GLITCH░▒▓'):^20}")
            lines.append("")
            lines.append(f"{red('█▓▒ SYSTEM COMPROMISE DETECTED ▒▓█'):^20}")
            lines.append(f"{bright_red('💀  CONTROLLED BY SEPHIROTH  💀'):^20}")
            lines.append("")
            lines.append(f"{'⚠️ WARNING ⚠️ TRUTH HIDDEN ⚠️ WARNING ⚠️':^20}")
            lines.append(f"{'🔥 FIND THE TRUTH 🔥 STOP HIM 🔥':^20}")
            lines.append(f"{'💀 30TH FLOOR AWAITS 💀':^20}")
            lines.append(f"{red('██████ GLITCH MODE ACTIVE ██████'):^20}")
            lines.append("")
            lines.append(f"{bright_red('█'):^20} {bright_yellow('▓'):^20} {bright_magenta('█'):^20} {bright_red('▓'):^20} {bright_yellow('█'):^20}")
        else:
            # 일반 아스키 아트
            lines.append(f"{bright_yellow('         ██████╗  █████╗ ██╗    ██╗███╗   ██╗    ██████╗ ███████╗'):^20}")
            lines.append(f"{bright_yellow('         ██╔══██╗██╔══██╗██║    ██║████╗  ██║   ██╔═══██╗██╔════╝'):^20}")
            lines.append(f"{bright_cyan('         ██║  ██║███████║██║ █╗ ██║██╔██╗ ██║   ██║   ██║█████╗  '):^20}")
            lines.append(f"{bright_cyan('         ██║  ██║██╔══██║██║███╗██║██║╚██╗██║   ██║   ██║██╔══╝  '):^20}")
            lines.append(f"{bright_magenta('         ██████╔╝██║  ██║╚███╔███╔╝██║ ╚████║   ╚██████╔╝██║     '):^20}")
            lines.append(f"{bright_magenta('         ╚═════╝ ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═══╝    ╚═════╝ ╚═╝     '):^20}")
            lines.append("")
            lines.append(f"{bright_white('     ███████╗████████╗███████╗██╗     ██╗      █████╗ ██████╗'):^20}")
            lines.append(f"{bright_white('     ██╔════╝╚══██╔══╝██╔════╝██║     ██║     ██╔══██╗██╔══██╗'):^20}")
            lines.append(f"{bright_green('     ███████╗   ██║   █████╗  ██║     ██║     ███████║██████╔╝'):^20}")
            lines.append(f"{bright_green('     ╚════██║   ██║   ██╔══╝  ██║     ██║     ██╔══██║██╔══██╗'):^20}")
            lines.append(f"{bright_red('     ███████║   ██║   ███████╗███████╗███████╗██║  ██║██║  ██║'):^20}")
            lines.append(f"{bright_red('     ╚══════╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝'):^20}")
            lines.append("")
            
            # 게임 설명 라인
            lines.append(f"{magenta('✦─────────────────────  별빛의 여명  ─────────────────────✦'):^20}")
            lines.append(f"{bright_cyan('🌟  FANTASY TACTICAL ROGUELIKE RPG  🌟'):^20}")
            lines.append("")
            
            # 특징 소개
            lines.append(f"{'⚔️  28개 고유 직업  ⭐  Brave 전투시스템  🏰  무한 던전':^20}")
            lines.append(f"{'🧬  Organic 특성  👥  4인 파티 시스템  🎲  절차적 생성':^20}")
            lines.append(f"{'🎵  동적 BGM  💎  메타 진행  📚  240개+ 레시피':^20}")
            lines.append(f"{yellow('──────   🎯 GAME FEATURES   ──────────────────────'):^20}")
            lines.append("")
            
            # 장식적 별 효과
            lines.append(f"{bright_white('✦'):^20} {bright_yellow('✧'):^20} {bright_cyan('✦'):^20} {bright_magenta('✧'):^20} {bright_green('✦'):^20}")
        
        lines.append("")
        
        return "\n".join(lines)

    def _display_main_menu_ascii(self):
        """메인 메뉴 아스키 아트 표시 (한 번만)"""
        print("\n" + "="*60)
        print()
        
        # 🌟 세피로스 조우 후 글리치 모드 체크
        glitch_mode = False
        if hasattr(self, 'story_system') and self.story_system:
            glitch_mode = self.story_system.is_glitch_mode()
        
        if glitch_mode:
            # 글리치 버전 아스키 아트
            print(f"{bright_red('         ██▓▒░ CORRUPTED ░▒▓██'):^20}")
            print(f"{bright_red('         ██░██▓██████▓██░██'):^20}")
            print(f"{bright_magenta('         ▓█░▓█████████▓█░█▓'):^20}")
            print(f"{bright_magenta('         █▓░▓█████████▓░▓█'):^20}")
            print(f"{bright_yellow('         ▓█░▓█████████▓░█▓'):^20}")
            print(f"{bright_yellow('         ░▓██████████████▓░'):^20}")
            print()
            print(f"{bright_red('     ███▓▒░ERROR░▒▓███'):^20}")
            print(f"{bright_red('     ██CORRUPTED██'):^20}")
            print(f"{bright_magenta('     ███SEPHIROTH███'):^20}")
            print(f"{bright_magenta('     ░▒▓PROTOCOL▓▒░'):^20}")
            print(f"{bright_yellow('     ███████████████'):^20}")
            print(f"{bright_yellow('     ▓▒░GLITCH░▒▓'):^20}")
            print()
            print(f"{red('█▓▒ SYSTEM COMPROMISE DETECTED ▒▓█'):^20}")
            print(f"{bright_red('💀  CONTROLLED BY SEPHIROTH  💀'):^20}")
            print()
            print(f"{'⚠️ WARNING ⚠️ TRUTH HIDDEN ⚠️ WARNING ⚠️':^20}")
            print(f"{'🔥 FIND THE TRUTH 🔥 STOP HIM 🔥':^20}")
            print(f"{'💀 30TH FLOOR AWAITS 💀':^20}")
            print(f"{red('██████ GLITCH MODE ACTIVE ██████'):^20}")
            print()
            print(f"{bright_red('█'):^20} {bright_yellow('▓'):^20} {bright_magenta('█'):^20} {bright_red('▓'):^20} {bright_yellow('█'):^20}")
        else:
            # 일반 아스키 아트 (원래 코드)
            print(f"{bright_yellow('         ██████╗  █████╗ ██╗    ██╗███╗   ██╗    ██████╗ ███████╗'):^20}")
            print(f"{bright_yellow('         ██╔══██╗██╔══██╗██║    ██║████╗  ██║   ██╔═══██╗██╔════╝'):^20}")
            print(f"{bright_cyan('         ██║  ██║███████║██║ █╗ ██║██╔██╗ ██║   ██║   ██║█████╗  '):^20}")
            print(f"{bright_cyan('         ██║  ██║██╔══██║██║███╗██║██║╚██╗██║   ██║   ██║██╔══╝  '):^20}")
            print(f"{bright_magenta('         ██████╔╝██║  ██║╚███╔███╔╝██║ ╚████║   ╚██████╔╝██║     '):^20}")
            print(f"{bright_magenta('         ╚═════╝ ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═══╝    ╚═════╝ ╚═╝     '):^20}")
            print()
            print(f"{bright_white('     ███████╗████████╗███████╗██╗     ██╗      █████╗ ██████╗'):^20}")
            print(f"{bright_white('     ██╔════╝╚══██╔══╝██╔════╝██║     ██║     ██╔══██╗██╔══██╗'):^20}")
            print(f"{bright_green('     ███████╗   ██║   █████╗  ██║     ██║     ███████║██████╔╝'):^20}")
            print(f"{bright_green('     ╚════██║   ██║   ██╔══╝  ██║     ██║     ██╔══██║██╔══██╗'):^20}")
            print(f"{bright_red('     ███████║   ██║   ███████╗███████╗███████╗██║  ██║██║  ██║'):^20}")
            print(f"{bright_red('     ╚══════╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝'):^20}")
            print()
            
            # 게임 설명 라인
            print(f"{magenta('✦─────────────────────  별빛의 여명  ─────────────────────✦'):^20}")
            print(f"{bright_cyan('🌟  FANTASY TACTICAL ROGUELIKE RPG  🌟'):^20}")
            print()
            
            # 특징 소개
            print(f"{'⚔️  28개 고유 직업  ⭐  Brave 전투시스템  🏰  무한 던전':^20}")
            print(f"{'🧬  Organic 특성  👥  4인 파티 시스템  🎲  절차적 생성':^20}")
            print(f"{'🎵  동적 BGM  💎  메타 진행  📚  240개+ 레시피':^20}")
            print(f"{yellow('──────   🎯 GAME FEATURES   ──────────────────────'):^20}")
            print()
            
            # 장식적 별 효과
            print(f"{bright_white('✦'):^20} {bright_yellow('✧'):^20} {bright_cyan('✦'):^20} {bright_magenta('✧'):^20} {bright_green('✦'):^20}")
        
        print()

    def _is_menu_bgm_playing(self):
        """메인 메뉴 BGM이 현재 재생 중인지 확인"""
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                from game.audio_system import BGMType
                import pygame
                return (pygame.mixer.music.get_busy() and 
                        hasattr(self.audio_system, 'current_bgm_type') and 
                        self.audio_system.current_bgm_type == BGMType.MENU)
            return False
        except Exception:
            return False

    def _smart_play_main_menu_bgm(self):
        """메인 메뉴 BGM을 스마트하게 재생 (중복 방지)"""
        if not self._is_menu_bgm_playing():
            self._play_main_menu_bgm()

    def _handle_menu_state(self):
        """메뉴 상태 처리 - 커서 네비게이션 (아스키 아트 보존)"""
        
        # 새로운 커서 메뉴 시스템 사용
        try:
            self._handle_menu_state_with_cursor()
            return
        except Exception as e:
            print(f"⚠️ 커서 메뉴 실행 실패: {e}")
            print("기본 메뉴로 전환합니다...")
            sys.stdout.flush()
            time.sleep(1)
        
        # 강제 터미널 출력 보장
        import sys
        sys.stdout.flush()
        
        # 메인 메뉴 BGM 재생 (한 번만)
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                from game.audio_system import BGMType
                # BGM이 전혀 재생되지 않고 있을 때만 메인 메뉴 BGM 시작
                import pygame
                if not pygame.mixer.music.get_busy():
                    self.audio_system.play_bgm(BGMType.MENU, loop=True)
                    self._menu_bgm_playing = True
        except Exception:
            pass
        
        # 색상 함수 임포트 확인
        try:
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green, blue, magenta, bright_magenta
            print("✅ 색상 함수 임포트 성공!")
            sys.stdout.flush()
            color_functions_available = True
        except ImportError as e:
            print(f"⚠️ 색상 함수 임포트 실패: {e}")
            sys.stdout.flush()
            # 폴백: 기본 print 함수 사용
            bright_cyan = bright_yellow = yellow = green = red = bright_white = cyan = white = bright_green = blue = magenta = bright_magenta = lambda x: str(x)
            color_functions_available = False
        
    # (배너 제거됨) 이전 강제 ASCII/헤더 출력과 대기 제거로 깔끔한 진입
    # 빠른 진입을 위해 불필요한 대기 제거
        
        # 메인 메뉴 표시 및 선택 처리 루프
        while self.running:
            choice = None  # choice 변수 초기화
            print("🔄 메뉴 루프 시작!")  # 디버그 출력
            sys.stdout.flush()
            time.sleep(0.5)  # 디버그 메시지 표시 시간
            
            try:
                # 간단한 입력 기반 메뉴 시스템 사용 (커서 메뉴 문제 해결)
                # 최소 출력 모드: 옵션만 한 줄 요약 (배너 제거)
                print("[1]시작 [2]불러오기 [T]트레이닝 [M]메타 [4]레시피 [B]가이드 [6]설정 [0]종료")
                
                # 사용자 입력 받기
                try:
                    if hasattr(self, 'keyboard') and self.keyboard and hasattr(self.keyboard, 'get_key'):
                        print("👉 선택하세요: ", end="", flush=True)
                        choice = self.keyboard.get_key().strip()
                    else:
                        choice = input("� 선택하세요: ").strip()
                except Exception:
                    choice = input("👉 선택하세요: ").strip()
                
                print(f"✅ 입력 받음: {choice}")
                sys.stdout.flush()
                
                # 커서 메뉴 대신 직접 처리
                if choice.lower() == '1':
                    result = 0  # 게임 시작
                elif choice.lower() == '2':
                    result = 1  # 게임 불러오기
                elif choice.lower() == 't':
                    result = 2  # 트레이닝 룸
                elif choice.lower() == 'm':
                    result = 3  # 메타 진행
                elif choice.lower() == '4':
                    result = 4  # 레시피 컬렉션
                elif choice.lower() == 'b':
                    result = 5  # 초보자 가이드
                elif choice.lower() == '6':
                    result = 6  # 설정
                elif choice.lower() == '0' or choice.lower() == 'q':
                    result = 7  # 종료
                else:
                    print(f"❌ 잘못된 선택: {choice}")
                    time.sleep(0.5)
                    continue  # 다시 메뉴로
                
                print(f"🎯 메뉴 결과: {result}")  # 디버그 출력
                sys.stdout.flush()
                time.sleep(0.5)  # 결과 표시 시간
                
                # 선택 결과 처리
                if result == 0:  # 게임 시작
                    choice = '1'
                elif result == 1:  # 게임 불러오기
                    choice = '2'
                elif result == 2:  # 트레이닝 룸
                    choice = 'T'
                elif result == 3:  # 메타 진행
                    choice = 'M'
                elif result == 4:  # 레시피 컬렉션
                    choice = '4'
                elif result == 5:  # 초보자 가이드
                    choice = 'B'
                elif result == 6:  # 설정
                    choice = '6'
                elif result == 7:  # 종료
                    if self.confirm_quit_main_menu():
                        choice = '0'
                    else:
                        continue  # 확인 취소 시 메뉴 계속
                elif result == -1 or result is None:  # Q로 종료 또는 취소
                    if self.confirm_quit_main_menu():
                        choice = '0'
                    else:
                        continue  # 확인 취소 시 메뉴 계속
                else:
                    print(f"디버그: 알 수 없는 결과 = {result}")
                    sys.stdout.flush()
                    continue
                
                # 실제 메뉴 선택 처리
                if choice is not None:
                    print(f"🎮 메뉴 선택 처리: {choice}")  # 디버그 출력
                    sys.stdout.flush()
                    processed = self._process_menu_choice(choice)
                    if not processed:  # 게임 종료가 선택된 경우
                        break
                    
            except ImportError as import_error:
                print(f"❌ cursor_menu_system 임포트 실패: {import_error}")
                sys.stdout.flush()
                time.sleep(2)  # 오류 메시지 표시 시간
                
                # 폴백: 기존 메뉴 시스템 - 강화된 버전
                print("🔄 폴백 메뉴 시스템 사용 중...")
                sys.stdout.flush()
                time.sleep(2)  # 폴백 메시지 표시 시간
                
                # 화면 클리어 후 메뉴 표시
                print("\033[2J\033[H")
                sys.stdout.flush()
                time.sleep(0.5)  # 화면 클리어 후 대기
                
                if not hasattr(self, '_ascii_art_displayed') or not self._ascii_art_displayed:
                    self._display_main_menu_ascii()
                    self._ascii_art_displayed = True
                    time.sleep(2)  # 아스키 아트 표시 후 대기
                
                print(f"{cyan('1️⃣')}  게임 시작")
                print(f"{blue('2️⃣')}  게임 불러오기") 
                print(f"{bright_magenta('T️⃣')}  트레이닝 룸")
                print(f"{yellow('M️⃣')}  메타 진행")
                print(f"{green('4️⃣')}  레시피 컬렉션")
                print(f"{magenta('B️⃣')}  초보자 가이드")
                print(f"{bright_white('6️⃣')}  설정")
                print(f"{red('0️⃣')}  종료")
                sys.stdout.flush()
                time.sleep(1)  # 메뉴 옵션 표시 후 대기
                
                # 영구 진행상황 요약 표시
                if hasattr(self, 'permanent_progression') and self.permanent_progression and self.permanent_progression.total_runs > 0:
                    print(f"\n{cyan('📊 진행상황:')} 플레이 {self.permanent_progression.total_runs}회 | "
                          f"최고 {self.permanent_progression.best_floor}층 | "
                          f"별조각 {bright_yellow(str(self.permanent_progression.star_fragments))}")
                
                # 메타 진행상황도 표시
                if hasattr(self, 'meta_progression') and self.meta_progression:
                    star_fragments = self.meta_progression.data.get('star_fragments', 0)
                    print(f"{cyan('🌟 별조각:')} {bright_yellow(str(star_fragments))}개")
                
                sys.stdout.flush()
                
                # 입력 함수 안전 확인
                print("\n📝 사용자 입력을 기다리는 중...")
                sys.stdout.flush()
                time.sleep(0.5)
                
                try:
                    # keyboard_input이 있으면 사용, 없으면 기본 input 사용
                    if hasattr(self, 'keyboard') and self.keyboard and hasattr(self.keyboard, 'get_key'):
                        choice = self.keyboard.get_key()
                    else:
                        choice = input(f"\n{bright_white('👉 선택하세요 (1-6, M, B, T, P, 0): ')}")
                except Exception:
                    # 더 기본적인 입력 방식
                    choice = input(f"\n👉 선택하세요 (1-6, M, B, T, P, 0): ").strip()
                
                print(f"✅ 입력 받음: {choice}")
                sys.stdout.flush()
                time.sleep(0.5)
                
                # 폴백 메뉴 선택 처리
                print(f"🎮 폴백 메뉴 선택 처리: {choice}")  # 디버그 출력
                sys.stdout.flush()
                processed = self._process_menu_choice(choice)
                if not processed:  # 게임 종료가 선택된 경우
                    break
            except Exception as general_error:
                print(f"❌ 메뉴 처리 중 일반 오류: {general_error}")
                sys.stdout.flush()
                import traceback
                traceback.print_exc()
                time.sleep(3)  # 오류 정보 표시 시간
                
                # 최소한의 안전 메뉴
                print("\n" + "="*50)
                print("🎮 Dawn of Stellar - 메인 메뉴")
                print("="*50)
                print("1. 게임 시작")
                print("2. 게임 불러오기") 
                print("T. 트레이닝 룸")
                print("M. 메타 진행")
                print("4. 레시피 컬렉션")
                print("B. 초보자 가이드")
                print("6. 설정")
                print("0. 종료")
                sys.stdout.flush()
                time.sleep(2)  # 안전 메뉴 표시 시간
                
                print("\n📝 사용자 입력을 기다리는 중...")
                sys.stdout.flush()
                choice = input("\n👉 선택하세요: ").strip()
                
                print(f"✅ 입력 받음: {choice}")
                sys.stdout.flush()
                time.sleep(0.5)
                
                processed = self._process_menu_choice(choice)
                if not processed:
                    break
                
    def _handle_menu_state_with_cursor(self):
        """커서 메뉴를 사용한 메뉴 상태 처리"""
        
        # 강제 터미널 출력 보장
        sys.stdout.flush()
        
        # 메인 메뉴 BGM 재생 (스마트 중복 방지)
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                from game.audio_system import BGMType
                import pygame
                # 현재 메인 메뉴 BGM이 재생 중인지 확인
                is_menu_bgm_active = (
                    pygame.mixer.music.get_busy() and 
                    hasattr(self.audio_system, 'current_bgm_type') and 
                    self.audio_system.current_bgm_type == BGMType.MENU
                )
                
                # 메뉴 BGM이 재생 중이 아닌 경우에만 시작
                if not is_menu_bgm_active:
                    self.audio_system.play_bgm(BGMType.MENU, loop=True)
                    self._menu_bgm_playing = True
        except Exception:
            pass
        
        # 색상 함수 임포트 확인
        try:
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white, bright_green, blue, magenta, bright_magenta
            color_functions_available = True
        except ImportError as e:
            # 폴백: 기본 print 함수 사용
            bright_cyan = bright_yellow = yellow = green = red = bright_white = cyan = white = bright_green = blue = magenta = bright_magenta = lambda x: str(x)
            color_functions_available = False
        
        # 메인 메뉴 표시 및 선택 처리 루프
        while self.running:
            choice = None  # choice 변수 초기화
            
            try:
                from game.cursor_menu_system import create_simple_menu
                
                # 메뉴 옵션 설정
                options = [
                    "🚀 게임 시작",
                    "📁 게임 불러오기", 
                    "⭐ 메타 진행",
                    "📖 레시피 컬렉션",
                    "👶 초보자 가이드",
                    "⚙️ 설정",
                    "❌ 종료"
                ]
                
                descriptions = [
                    "새로운 모험을 시작합니다",
                    "이전에 저장된 게임을 불러옵니다",
                    "캐릭터 해금, 특성 해금, 영구 강화 등 메타 시스템을 관리합니다",
                    "발견한 레시피들을 확인합니다",
                    "게임이 처음이신 분을 위한 친절한 가이드와 튜토리얼입니다",
                    "게임 옵션, 난이도, 설정을 변경합니다",
                    "게임을 종료합니다"
                ]
                
                # 커서 메뉴 생성 및 실행
                menu = create_simple_menu("", 
                                        options, descriptions, None, self.keyboard, 
                                        clear_screen=True)
                # 메인 메뉴 장식 헤더 제거
                try:
                    menu.show_header = False
                except Exception:
                    pass
                
                # 메뉴에 아스키 아트 추가 (컬러 포함)
                try:
                    from game.color_text import bright_cyan, bright_yellow, yellow, bright_white, cyan, bright_magenta
                    import os as _os
                    narrow = _os.getenv('SUBPROCESS_MODE') == '1'
                    if not narrow:
                        lines = [
                            bright_cyan(' ██████╗  █████╗ ██╗    ██╗███╗   ██╗     ██████╗ ███████╗'),
                            bright_cyan(' ██╔══██╗██╔══██╗██║    ██║████╗  ██║    ██╔═══██╗██╔════╝'),
                            bright_white(' ██║  ██║███████║██║ █╗ ██║██╔██╗ ██║    ██║   ██║█████╗  '),
                            bright_white(' ██║  ██║██╔══██║██║███╗██║██║╚██╗██║    ██║   ██║██╔══╝  '),
                            bright_yellow(' ██████╔╝██║  ██║╚███╔███╔╝██║ ╚████║    ╚██████╔╝██║     '),
                            bright_yellow(' ╚═════╝ ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═══╝     ╚═════╝ ╚═╝     '),
                            '',
                            bright_magenta('     ███████╗████████╗███████╗██╗     ██╗      █████╗ ██████╗ '),
                            bright_magenta('     ██╔════╝╚══██╔══╝██╔════╝██║     ██║     ██╔══██╗██╔══██╗'),
                            cyan('     ███████╗   ██║   █████╗  ██║     ██║     ███████║██████╔╝'),
                            cyan('     ╚════██║   ██║   ██╔══╝  ██║     ██║     ██╔══██║██╔══██╗'),
                            bright_cyan('     ███████║   ██║   ███████╗███████╗███████╗██║  ██║██║  ██║'),
                            bright_cyan('     ╚══════╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝'),
                            '',
                            bright_yellow('                   ⭐ 별들 사이의 모험이 시작됩니다 ⭐'),
                            yellow('                      ✨ 용기를 가지고 도전하세요! ✨'),
                            '',
                            bright_cyan('👉 Press Enter')
                        ]
                        ascii_art = "\n".join(lines)
                    else:
                        ascii_art = "DOS\n\nPress Enter"
                except ImportError:
                    # 컬러가 없으면 기본 아스키 아트
                    ascii_art = """
 ██████╗  █████╗ ██╗    ██╗███╗   ██╗     ██████╗ ███████╗
 ██╔══██╗██╔══██╗██║    ██║████╗  ██║    ██╔═══██╗██╔════╝
 ██║  ██║███████║██║ █╗ ██║██╔██╗ ██║    ██║   ██║█████╗  
 ██║  ██║██╔══██║██║███╗██║██║╚██╗██║    ██║   ██║██╔══╝  
 ██████╔╝██║  ██║╚███╔███╔╝██║ ╚████║    ╚██████╔╝██║     
 ╚═════╝ ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═══╝     ╚═════╝ ╚═╝     

     ███████╗████████╗███████╗██╗     ██╗      █████╗ ██████╗ 
     ██╔════╝╚══██╔══╝██╔════╝██║     ██║     ██╔══██╗██╔══██╗
     ███████╗   ██║   █████╗  ██║     ██║     ███████║██████╔╝
     ╚════██║   ██║   ██╔══╝  ██║     ██║     ██╔══██║██╔══██╗
     ███████║   ██║   ███████╗███████╗███████╗██║  ██║██║  ██║
     ╚══════╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝

                         ⭐ 별들 사이의 모험이 시작됩니다 ⭐
                             ✨ 용기를 가지고 도전하세요! ✨

👉 Press Enter
"""
                menu.extra_content = ascii_art
                
                result = menu.run()
                
                # 선택 결과 처리
                if result == 0:  # 게임 시작
                    choice = '1'
                elif result == 1:  # 게임 불러오기
                    choice = '2'
                elif result == 2:  # 메타 진행
                    choice = 'M'
                elif result == 3:  # 레시피 컬렉션
                    choice = '4'
                elif result == 4:  # 초보자 가이드
                    choice = 'B'
                elif result == 5:  # 설정
                    choice = '6'
                elif result == 6:  # 종료
                    if self.confirm_quit_main_menu():
                        choice = '0'
                    else:
                        continue  # 확인 취소 시 메뉴 계속
                elif result == -1 or result is None:  # Q로 종료 또는 취소
                    if self.confirm_quit_main_menu():
                        choice = '0'
                    else:
                        continue  # 확인 취소 시 메뉴 계속
                else:
                    continue
                
                # 실제 메뉴 선택 처리
                if choice is not None:
                    processed = self._process_menu_choice(choice)
                    if not processed:  # 게임 종료가 선택된 경우
                        break
                        
            except ImportError as import_error:
                print(f"❌ cursor_menu_system 임포트 실패: {import_error}")
                sys.stdout.flush()
                time.sleep(2)  # 오류 메시지 표시 시간
                
                # 폴백: 기존 메뉴 시스템 - 강화된 버전
                print("🔄 폴백 메뉴 시스템 사용 중...")
                sys.stdout.flush()
                time.sleep(2)  # 폴백 메시지 표시 시간
                break
                
            except Exception as general_error:
                print(f"❌ 커서 메뉴 처리 중 일반 오류: {general_error}")
                sys.stdout.flush()
                import traceback
                traceback.print_exc()
                time.sleep(3)  # 오류 정보 표시 시간
                
                # 폴백: 기존 메뉴 시스템 - 강화된 버전
                print("🔄 폴백 메뉴 시스템 사용 중...")
                sys.stdout.flush()
                time.sleep(2)  # 폴백 메시지 표시 시간
                break

    def _process_menu_choice(self, choice):
        """메뉴 선택 처리 - True 반환 시 메뉴 계속, False 반환 시 게임 종료"""
        if choice == 'q' or choice == 'Q':
            # Q키로 종료 확인
            if self.confirm_quit_main_menu():
                choice = '0'
            else:
                return True  # 확인 취소 시 메뉴 계속
                
        if choice == '1':
            # 게임 시작 (난이도 선택 후 캐릭터 선택) - 즉시 BGM 정지
            self.safe_play_sfx("menu_select")
            
            # 메인 메뉴 BGM 즉시 정지
            if self.sound_manager:
                try:
                    self.sound_manager.stop_bgm()
                    self._menu_bgm_playing = False  # BGM 플래그 리셋
                except:
                    pass
            
            game = DawnOfStellarGame()  # 새 인스턴스 생성
            game.permanent_progression = self.permanent_progression  # 영구 진행상황 유지
            
            # 먼저 난이도 선택
            selected_difficulty = game.select_difficulty()
            if selected_difficulty is None:
                # 난이도 선택 취소 시 메인 메뉴로 돌아가기
                print("\033[2J\033[H")  # 화면 클리어
                print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                # 메인 메뉴 BGM 스마트 재생 (중복 방지)
                self._smart_play_main_menu_bgm()
                del game
                return True
            
            # 캐릭터 선택이 성공한 경우에만 게임 시작
            if game.show_character_selection():  # 캐릭터 선택 메뉴로 이동
                # 난이도 정보를 게임 데이터에 저장
                game.selected_difficulty = selected_difficulty
                game.start_adventure()  # main_loop 대신 start_adventure 사용
            else:
                print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                self._play_main_menu_bgm()
                # 게임 객체 정리
                del game
            
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
            
        elif choice == '2':
            # 게임 불러오기
            self.safe_play_sfx("menu_select")
            # print(f"\n🔄 게임 불러오기를 시작합니다...")  # 숨김
            # print(f"📊 현재 영구 진행상황: {self.permanent_progression}")  # 숨김
            
            load_game = DawnOfStellarGame()  # 새 인스턴스 생성
            load_game.permanent_progression = self.permanent_progression  # 영구 진행상황 유지
            
            # print(f"✅ 새 게임 인스턴스 생성 완료")  # 숨김
            # print(f"🔄 불러오기 함수 호출 중...")  # 숨김
            
            try:
                load_result = load_game.load_game()  # 불러오기 성공 여부 확인
                # print(f"📊 불러오기 결과: {load_result}")  # 숨김
                
                if load_result:  # 불러오기 성공
                    # print(f"✅ 불러오기 성공! 파티 멤버 수 확인 중...")  # 숨김
                    party_count = len(load_game.party_manager.members) if hasattr(load_game, 'party_manager') else 0
                    # print(f"📊 파티 멤버 수: {party_count}")  # 숨김
                    
                    if party_count > 0:  # 파티가 제대로 복원되었는지 확인
                        # print(f"✅ 파티 복원 확인 완료. 게임 시작 중...")  # 숨김
                        input("게임을 시작하려면 Enter를 누르세요...")
                        load_game.start_adventure(skip_passive_selection=True, skip_ai_mode_selection=True)  # 불러오기 시 패시브 선택과 AI 모드 선택 건너뛰기
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
            
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
        
        elif choice == '3' or choice == 'M' or choice == 'm':
            # 메타 진행 (통합 메뉴)
            self.safe_play_sfx("menu_select")
            if hasattr(self, 'meta_progression') and self.meta_progression:
                self.show_meta_progression_menu()
            else:
                print("메타 진행 시스템이 초기화되지 않았습니다.")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
            
        elif choice == '4':
            # 레시피 컬렉션
            self.safe_play_sfx("menu_select")
            try:
                from game.cooking_system import show_recipe_collection
                show_recipe_collection()
            except Exception as e:
                print(f"❌ 레시피 컬렉션 오류: {e}")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
        
        elif choice == '5' or choice == 'B' or choice == 'b':
            # 초보자 가이드
            self.safe_play_sfx("menu_select")
            try:
                self.show_beginner_guide()
            except Exception as e:
                print(f"❌ 초보자 가이드 오류: {e}")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
            
        elif choice == '6':
            # 설정 (난이도 포함)
            self.safe_play_sfx("menu_select")
            try:
                self.show_settings_menu()
            except Exception as e:
                print(f"❌ 설정 메뉴 오류: {e}")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
        
        elif choice == '0' or choice == '7':
            # 게임 종료 확인
            if self.confirm_quit_main_menu():
                self.safe_play_sfx("menu_cancel")
                print(f"\n🌟 {bright_green('게임을 종료합니다. 플레이해주셔서 감사합니다!')}")
                # 영구 진행상황 저장
                if hasattr(self, 'permanent_progression'):
                    self.permanent_progression.save_to_file()
                self.running = False
                return False  # 게임 종료
            # 확인 취소 시 메뉴 계속
            return True
            
        else:
            error_msg = f"잘못된 선택입니다: '{choice}'"
            self.safe_play_sfx("error")
            print(f"❌ {red(error_msg)}")
            time.sleep(1)  # 오류 메시지 표시 시간
            return True  # 메뉴 계속

    def show_meta_progress_summary(self):
        """메뉴 선택 처리 - True 반환 시 메뉴 계속, False 반환 시 게임 종료"""
        if choice == 'q' or choice == 'Q':
            # Q키로 종료 확인
            if self.confirm_quit_main_menu():
                choice = '0'
            else:
                return True  # 확인 취소 시 메뉴 계속
                
        if choice == '1':
            # 게임 시작 (난이도 선택 후 캐릭터 선택) - 즉시 BGM 정지
            self.safe_play_sfx("menu_select")
            
            # 메인 메뉴 BGM 즉시 정지
            if hasattr(self, 'sound_manager') and self.sound_manager:
                try:
                    self.sound_manager.stop_bgm()
                except:
                    pass
            
            game = DawnOfStellarGame()  # 새 인스턴스 생성
            game.permanent_progression = self.permanent_progression  # 영구 진행상황 유지
            
            # 먼저 난이도 선택
            selected_difficulty = game.select_difficulty()
            if selected_difficulty is None:
                # 난이도 선택 취소 시 메인 메뉴로 돌아가기
                print("\033[2J\033[H")  # 화면 클리어
                print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                self._play_main_menu_bgm()
                del game
                return True
            
            # 캐릭터 선택이 성공한 경우에만 게임 시작
            if game.show_character_selection():  # 캐릭터 선택 메뉴로 이동
                # 난이도 정보를 게임 데이터에 저장
                game.selected_difficulty = selected_difficulty
                game.start_adventure()  # main_loop 대신 start_adventure 사용
            else:
                print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                # 메인 메뉴로 돌아가기 전 메인 BGM 재생
                self._play_main_menu_bgm()
                # 게임 객체 정리
                del game
            
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
            
        elif choice == '2':
            # 게임 불러오기
            self.safe_play_sfx("menu_select")
            print(f"\n🔄 게임 불러오기를 시작합니다...")
            
            load_game = DawnOfStellarGame()  # 새 인스턴스 생성
            load_game.permanent_progression = self.permanent_progression  # 영구 진행상황 유지
            
            try:
                load_result = load_game.load_game()  # 불러오기 성공 여부 확인
                
                if load_result:  # 불러오기 성공
                    print(f"✅ 불러오기 성공! 파티 멤버 수 확인 중...")
                    party_count = len(load_game.party_manager.members) if hasattr(load_game, 'party_manager') else 0
                    
                    if party_count > 0:  # 파티가 제대로 복원되었는지 확인
                        print(f"✅ 파티 복원 확인 완료. 게임 시작 중...")
                        input("게임을 시작하려면 Enter를 누르세요...")
                        load_game.start_adventure(skip_passive_selection=True, skip_ai_mode_selection=True)
                    else:
                        print("❌ 파티 정보가 복원되지 않았습니다.")
                        print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                        input("확인하려면 Enter를 누르세요...")
                        del load_game
                else:
                    print("❌ 게임 불러오기 실패")
                    print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                    input("확인하려면 Enter를 누르세요...")
                    del load_game
            except Exception as load_error:
                print(f"❌ 불러오기 중 예외 발생: {load_error}")
                input("메인 메뉴로 돌아가려면 Enter를 누르세요...")
                del load_game
            
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            self._play_main_menu_bgm()
            return True
        
        elif choice == 'T' or choice == 't':
            # 트레이닝 룸
            self.safe_play_sfx("menu_select")
            try:
                from game.training_room import TrainingRoom
                print(f"\n🏋️‍♂️ {bright_cyan('트레이닝 룸에 입장합니다...')}")
                training_room = TrainingRoom(getattr(self, 'audio_system', None), self.keyboard)
                training_room.enter_training_room(self.party_manager)
                # 트레이닝 룸 종료 후 메인 메뉴 BGM 재생
                self._play_main_menu_bgm()
            except ImportError as e:
                print(f"❌ 트레이닝 룸 모듈을 불러올 수 없습니다: {e}")
                input("아무 키나 눌러 계속...")
            except Exception as e:
                print(f"❌ 트레이닝 룸 실행 중 오류 발생: {e}")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
        
        elif choice == 'M' or choice == 'm' or choice == '3':
            # 메타 진행 통합 메뉴
            self.safe_play_sfx("menu_select")
            if hasattr(self, 'meta_progression') and self.meta_progression:
                self.show_meta_progression_menu()
            else:
                print("메타 진행 시스템이 초기화되지 않았습니다.")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
        
        elif choice == '4':
            # 레시피 컬렉션
            self.safe_play_sfx("menu_select")
            try:
                from game.cooking_system import show_recipe_collection
                show_recipe_collection()
            except Exception as e:
                print(f"❌ 레시피 컬렉션 오류: {e}")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
        
        elif choice == 'B' or choice == 'b' or choice == '5':
            # 초보자 가이드
            self.safe_play_sfx("menu_select")
            try:
                self.show_beginner_guide()
            except Exception as e:
                print(f"❌ 초보자 가이드 오류: {e}")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
            
        elif choice == '6':
            # 설정 (난이도 포함)
            self.safe_play_sfx("menu_select")
            try:
                self.show_settings_menu()
            except Exception as e:
                print(f"❌ 설정 메뉴 오류: {e}")
                input("아무 키나 눌러 계속...")
            # 화면 클리어하고 아스키 아트 다시 표시
            print("\033[2J\033[H")  # 화면 클리어
            self._ascii_art_displayed = False  # 아스키 아트 다시 표시하도록 플래그 리셋
            return True
        
        elif choice == '0' or choice == '7':
            # 게임 종료 확인
            if self.confirm_quit_main_menu():
                self.safe_play_sfx("menu_cancel")
                print(f"\n🌟 {bright_green('게임을 종료합니다. 플레이해주셔서 감사합니다!')}")
                # 영구 진행상황 저장
                if hasattr(self, 'permanent_progression'):
                    self.permanent_progression.save_to_file()
                self.running = False
                return False  # 게임 종료
            # 확인 취소 시 메뉴 계속
            return True
            
        else:
            error_msg = f"잘못된 선택입니다: '{choice}'"
            self.safe_play_sfx("error")
            print(f"❌ {red(error_msg)}")
            time.sleep(1)  # 오류 메시지 표시 시간
            return True  # 메뉴 계속

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
            self.add_gold(bonus_gold)
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
                        self.add_gold(drops['gold'])
                    
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
            self.start_battle()

    def start_elite_battle_4(self):
        """4마리 엘리트 전투 시작 (몬스터 소굴) - Brave Combat System 사용"""
        try:
            from game.brave_combat import BraveCombatSystem
            from game.character import Character
            import random
            
            print(f"\n💀 {bright_red('몬스터 소굴에서 4마리의 강력한 적이 나타났습니다!')}")
            print("🔥 엘리트 몬스터 4마리와의 전투가 시작됩니다...")
            
            # 현재 층수에 맞는 엘리트 적 생성
            current_floor = getattr(self.world, 'current_level', 1)
            
            # 엘리트 몬스터 데이터 (소굴용 - 다소 약화)
            elite_monsters = [
                {
                    "name": "골렘 정예병",
                    "level": current_floor + 1,
                    "hp_multiplier": 1.4,
                    "attack_multiplier": 1.3,
                    "defense_multiplier": 1.2
                },
                {
                    "name": "오크 전사",
                    "level": current_floor + 1,
                    "hp_multiplier": 1.3,
                    "attack_multiplier": 1.4,
                    "defense_multiplier": 1.1
                },
                {
                    "name": "어둠의 수행자",
                    "level": current_floor + 1,
                    "hp_multiplier": 1.2,
                    "attack_multiplier": 1.5,
                    "defense_multiplier": 1.0
                },
                {
                    "name": "독거미",
                    "level": current_floor + 1,
                    "hp_multiplier": 1.1,
                    "attack_multiplier": 1.3,
                    "defense_multiplier": 1.0
                },
                {
                    "name": "해골전사",
                    "level": current_floor + 1,
                    "hp_multiplier": 1.2,
                    "attack_multiplier": 1.2,
                    "defense_multiplier": 1.3
                },
                {
                    "name": "늑대인간",
                    "level": current_floor + 1,
                    "hp_multiplier": 1.3,
                    "attack_multiplier": 1.4,
                    "defense_multiplier": 0.9
                }
            ]
            
            # 4마리의 서로 다른 엘리트 몬스터 선택
            selected_monsters = random.sample(elite_monsters, 4)
            elite_enemies = []
            
            for i, elite_data in enumerate(selected_monsters):
                # 엘리트 몬스터 생성
                elite_enemy = Character(
                    name=f"{elite_data['name']} #{i+1}",
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
                
                elite_enemies.append(elite_enemy)
                
                print(f"⚔️ {elite_data['name']} #{i+1} (레벨 {elite_data['level']})이(가) 나타났습니다!")
                print(f"   HP: {elite_enemy.max_hp} | 공격력: {elite_enemy.physical_attack} | 방어력: {elite_enemy.physical_defense}")
            
            import time
            time.sleep(2.5)  # 긴장감 조성
            
            # 전투 시작 - Brave Combat System 사용
            brave_combat = BraveCombatSystem(self.audio_system, self.audio_system)
            
            combat_result = brave_combat.start_battle(self.party_manager.members, elite_enemies)
            
            # 전투 결과 처리
            if combat_result:
                print(f"\n🎉 {bright_green('4마리 엘리트 전투 승리!')}")
                
                # 4마리 엘리트 적 드롭 시스템 사용
                try:
                    from game.enemy_drop_system import get_drop_system
                    drop_system = get_drop_system()
                    
                    total_drops = {'experience': 0, 'gold': 0, 'items': []}
                    
                    for elite_enemy in elite_enemies:
                        # 엘리트 적으로 마킹
                        elite_enemy.is_elite = True
                        
                        drops = drop_system.calculate_drops(elite_enemy, current_floor, 1)
                        drops = drop_system.apply_drop_bonuses(drops, self.party_manager.members)
                        
                        total_drops['experience'] += drops['experience']
                        total_drops['gold'] += drops['gold']
                        total_drops['items'].extend(drops['items'])
                    
                    # 4마리 보너스 (총 보상 20% 증가)
                    total_drops['experience'] = int(total_drops['experience'] * 1.2)
                    total_drops['gold'] = int(total_drops['gold'] * 1.2)
                    
                    # 경험치 분배
                    if total_drops['experience'] > 0:
                        print(f"⭐ 4마리 엘리트 보상 경험치: {total_drops['experience']}")
                        if hasattr(self, 'party_manager') and self.party_manager.members:
                            exp_per_member = int(total_drops['experience'] * 0.8)  # 전체 경험치의 80%씩 분배
                            for member in self.party_manager.members:
                                if member.is_alive:
                                    member.gain_experience(exp_per_member)
                    
                    # 골드 지급
                    if total_drops['gold'] > 0:
                        print(f"💰 4마리 엘리트 보상 골드: {total_drops['gold']}")
                        self.add_gold(total_drops['gold'])
                    
                    # 아이템 드롭
                    for item in total_drops['items']:
                        print(f"✨ {bright_yellow(f'엘리트 드롭: {item.name}을(를) 획득했습니다!')}")
                        # 아이템 획득 효과음
                        try:
                            if hasattr(self, 'audio_system') and self.audio_system:
                                self.audio_system.play_sfx("item_pickup")
                        except:
                            pass
                        
                        if self.party_manager.members and hasattr(self.party_manager.members[0], 'inventory'):
                            self.party_manager.members[0].inventory.add_item(item)
                    
                    if not total_drops['items']:
                        print("📦 아이템 드롭 없음")
                        
                except Exception as e:
                    print(f"⚠️ 4마리 엘리트 드롭 시스템 오류: {e}")
                    print("드롭 시스템을 사용할 수 없습니다.")
                
                # 전투 통계 업데이트 (4마리 엘리트 승리)
                if hasattr(self.world, 'combat_stats'):
                    self.world.combat_stats['elite_victories'] = self.world.combat_stats.get('elite_victories', 0) + 4
                
            else:
                print(f"\n💀 {bright_red('4마리 엘리트 전투에서 패배했습니다...')}")
                
        except Exception as e:
            print(f"⚠️ 4마리 엘리트 전투 시작 중 오류: {e}")
            # 일반 전투로 폴백
            self.start_battle()

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
                        self.add_gold(total_gold)
                    
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
            self.start_battle()

    def start_battle(self):
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
                # 전투 승리 후 처리는 기존 코드 유지
                
        except Exception as e:
            print(f"⚠️ 전투 중 오류 발생: {e}")
            print("전투를 건너뜁니다.")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                                        
    def start_multi_enemy_combat(self, enemy_positions: List[Tuple[int, int]]):
        """다중 적 전투 시작 - 여러 위치의 적들과 동시 교전"""
        try:
            from game.brave_combat import BraveCombatSystem
            
            enemies_for_combat = []
            
            # 각 위치의 적들을 전투용 캐릭터로 변환
            for enemy_pos in enemy_positions:
                if hasattr(self.world, 'floor_enemies') and enemy_pos in self.world.floor_enemies:
                    enemy_data = self.world.floor_enemies[enemy_pos]
                    
                    # dict 객체인 경우 Character 객체로 변환
                    if isinstance(enemy_data, dict):
                        try:
                            from game.enemy_system import EnemyManager
                            enemy_manager = EnemyManager()
                            enemy_level = enemy_data.get('level', 1)
                            enemy_type = enemy_data.get('type', '고블린')
                            enemy_character = enemy_manager.spawn_enemy(enemy_level)
                            if hasattr(enemy_character, 'name'):
                                enemies_for_combat.append(enemy_character)
                        except Exception as e:
                            print(f"⚠️ 적 생성 실패: {e}")
                            continue
                    elif hasattr(enemy_data, 'name'):
                        # 이미 Character 객체인 경우
                        enemies_for_combat.append(enemy_data)
            
            if not enemies_for_combat:
                print("⚠️ 전투할 적이 없습니다.")
                return "no_enemies"
            
            print(f"⚔️ {len(enemies_for_combat)}마리의 적과 전투 시작!")
            
            # Brave Combat System으로 전투 실행
            combat_system = BraveCombatSystem(self.audio_system, self.audio_system)
            party_members = [member for member in self.party_manager.party_members if member.is_alive]
            
            if not party_members:
                print("⚠️ 살아있는 파티원이 없습니다.")
                return "no_party"
            
            # 전투 시작
            result = combat_system.start_battle(party_members, enemies_for_combat)
            
            # 전투 후 월드에서 적 위치 제거는 호출한 곳에서 처리
            return result
            
        except Exception as e:
            print(f"⚠️ 다중 적 전투 오류: {type(e).__name__}")
            print(f"📋 상세: {str(e)}")
            print("🔄 전투 시스템을 안전 모드로 실행합니다...")
            return "error"
            
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
                    self.add_gold(total_gold)
                    
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
                            self.add_gold(total_gold)
                    
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
                        self.add_gold(gold_reward)
                
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
            action_options = ["⚔️ 장착하기", "🤖 AI 자동 장착", "🎯 최적 파티원 추천", "ℹ️ 정보 보기", "🚪 취소"]
            action_descriptions = [
                "특정 파티원에게 수동으로 장착합니다", 
                "AI가 가장 적합한 파티원에게 자동으로 장착합니다",
                "이 장비에 가장 적합한 파티원을 추천받습니다",
                "장비 정보를 확인합니다", 
                "취소하고 돌아갑니다"
            ]
            
            action_menu = create_simple_menu("🎒 장비 관리 옵션", action_options, action_descriptions)
            action_result = action_menu.run()
            
            if action_result == 0:  # 장착하기
                self._equip_item(item, owner)
            elif action_result == 1:  # AI 자동 장착
                self._auto_equip_item(item, owner)
            elif action_result == 2:  # 최적 파티원 추천
                self._recommend_best_member(item)
            elif action_result == 3:  # 정보 보기
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

    def _auto_equip_item(self, item, owner):
        """AI 게임 모드의 고도화된 자동 장착 시스템 사용"""
        try:
            print(f"\n🤖 AI 장비 관리 시스템을 사용합니다...")
            
            # AI 게임 모드의 장비 관리자 사용
            try:
                from game.ai_game_mode import auto_equip_for_basic_mode
            except ImportError as e:
                print(f"❌ AI 자동장착 시스템 임포트 실패: {e}")
                return False
            
            # 먼저 소유자의 인벤토리에서 아이템이 실제로 있는지 확인
            if not hasattr(owner, 'inventory'):
                print(f"❌ {owner.name}의 인벤토리를 찾을 수 없습니다.")
                return False
            
            has_item = False
            if hasattr(owner.inventory, 'has_item'):
                has_item = owner.inventory.has_item(item.name)
            elif hasattr(owner.inventory, 'items'):
                has_item = item.name in owner.inventory.items and owner.inventory.items[item.name] > 0
            
            if not has_item:
                print(f"❌ {owner.name}의 인벤토리에 {item.name}이(가) 없습니다.")
                return False
            
            # 각 파티원에 대해 자동 장착 시도
            success_count = 0
            equipped_member = None
            
            for member in self.party_manager.members:
                if not member.is_alive:
                    continue
                    
                try:
                    # AI 시스템으로 적합도 계산 및 장착 시도
                    equipped_items = auto_equip_for_basic_mode(member, [item.name])
                    
                    if equipped_items:
                        # 성공적으로 장착된 경우
                        print(f"✅ {member.name}에게 {item.name} 자동 장착 완료!")
                        success_count += 1
                        equipped_member = member
                        break  # 첫 번째 성공한 멤버에게 장착
                    
                except Exception as e:
                    print(f"⚠️ {member.name} 자동장착 실패: {e}")
                    continue
            
            if success_count > 0 and equipped_member:
                # 성공적으로 장착되었으면 소유자의 인벤토리에서 아이템 제거
                try:
                    if hasattr(owner.inventory, 'remove_item'):
                        owner.inventory.remove_item(item.name, 1)
                        print(f"📦 {owner.name}의 인벤토리에서 {item.name} 제거됨")
                    else:
                        print(f"⚠️ 인벤토리에서 아이템 제거 함수를 찾을 수 없습니다.")
                except Exception as e:
                    print(f"⚠️ 인벤토리에서 아이템 제거 중 오류: {e}")
                
                return True
            else:
                print(f"❌ 모든 파티원에 대한 자동장착이 실패했습니다.")
                print(f"💡 수동으로 {item.name}을(를) 장착해주세요.")
                return False
                
        except Exception as e:
            print(f"❌ AI 자동장착 시스템 전체 오류: {e}")
            print(f"💡 수동 장착 모드로 전환합니다.")
            return False

    def _recommend_best_member(self, item):
        """AI 시스템으로 최적 파티원 추천"""
        try:
            from game.ai_game_mode import get_equipment_recommendations_for_basic_mode
            
            print(f"\n🤖 {item.name}에 가장 적합한 파티원을 분석 중...")
            
            # 각 파티원에 대한 추천 점수 계산
            recommendations = []
            
            for member in self.party_manager.members:
                if not member.is_alive:
                    continue
                
                recs = get_equipment_recommendations_for_basic_mode(member, [item.name])
                
                if recs:
                    # 추천 정보가 있는 경우
                    for rec in recs:
                        if rec.get('item_name') == item.name:
                            recommendations.append({
                                'member': member,
                                'score': rec.get('score', 0),
                                'reason': rec.get('reason', '적합성 분석'),
                                'benefits': rec.get('benefits', [])
                            })
            
            if recommendations:
                # 추천 점수순 정렬
                recommendations.sort(key=lambda x: x['score'], reverse=True)
                
                print(f"\n📊 {item.name} 적합성 분석 결과:")
                print("="*50)
                
                for i, rec in enumerate(recommendations[:3], 1):  # 상위 3명만
                    member = rec['member']
                    score = rec['score']
                    reason = rec['reason']
                    
                    print(f"{i}. {member.name} ({member.character_class})")
                    print(f"   📈 적합성 점수: {score:.1f}")
                    print(f"   💡 이유: {reason}")
                    
                    if rec['benefits']:
                        print(f"   ✨ 기대 효과: {', '.join(rec['benefits'])}")
                    print()
                
                print("💡 가장 높은 점수의 파티원에게 장착하는 것을 추천합니다!")
            else:
                print("📋 추천 정보를 생성할 수 없습니다.")
                print("💡 AI 자동 장착을 시도해보세요.")
                
        except Exception as e:
            print(f"❌ 추천 시스템 오류: {e}")
            print("📄 기본 분석을 제공합니다...")
            
            # 폴백: 기본 추천 로직
            print(f"\n📋 {item.name} 기본 분석:")
            
            from game.items import ItemType
            if item.item_type == ItemType.WEAPON:
                print("⚔️ 무기류: 물리 공격 직업(전사, 궁수, 도적)에게 적합")
            elif item.item_type == ItemType.ARMOR:
                print("🛡️ 방어구: 탱킹 직업(전사, 성기사)이나 체력이 낮은 멤버에게 적합")
            elif item.item_type == ItemType.ACCESSORY:
                print("💍 액세서리: 모든 직업에 유용, 특히 마법사에게 좋음")
            
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
    
    def show_beginner_guide(self):
        """통합 초보자 가이드 표시"""
        try:
            from game.integrated_beginner_guide import integrated_beginner_guide
            
            print(f"\n{bright_green('🔰 통합 초보자 가이드를 시작합니다!')}")
            print("게임이 처음이신 분들을 위한 친절한 안내를 제공합니다.")
            
            result = integrated_beginner_guide.run()
            
            if result == "start_game":
                # 가이드에서 게임 시작을 선택한 경우  
                print(f"{bright_cyan('🎮 바로 게임을 시작합니다!')}")
                # 새 게임 인스턴스 생성하여 게임 시작
                game = DawnOfStellarGame()
                game.permanent_progression = self.permanent_progression
                
                # 난이도 선택
                selected_difficulty = game.select_difficulty()
                if selected_difficulty is not None:
                    if game.show_character_selection():
                        game.selected_difficulty = selected_difficulty
                        game.start_adventure()
                    else:
                        print(f"\n{bright_cyan('메인 메뉴로 돌아갑니다.')}")
                        self._play_main_menu_bgm()
                        del game
            
        except ImportError as e:
            print(f"❌ 통합 초보자 가이드 모듈을 불러올 수 없습니다: {e}")
            # 폴백: 기존 튜토리얼
            try:
                from game.tutorial import show_tutorial_menu
                show_tutorial_menu()
            except ImportError:
                print("기본 튜토리얼도 사용할 수 없습니다.")
                print("H키를 눌러 간단한 도움말을 확인하세요.")
            except Exception as e:
                print(f"❌ 통합 초보자 가이드 실행 오류: {e}")
                print("\n3초 후 메인 메뉴로 돌아갑니다...")
                try:
                    import time
                    time.sleep(3)
                except:
                    pass

    def _handle_equipment_optimize(self):
        """모든 파티원의 장비를 최적화하여 재장착"""
        try:
            from game.cursor_menu_system import create_simple_menu
            
            print(f"\n{bright_cyan('=== ⚡ 장비 최적화 시스템 ===')}")
            print("모든 파티원의 장비를 해제한 후, AI 시스템으로 최적화하여 재장착합니다.")
            print("⚠️ 기존 장착된 모든 장비가 인벤토리로 이동됩니다.")
            
            # 확인 메뉴
            confirm_menu = create_simple_menu(
                "장비 최적화 확인", 
                ["🚀 최적화 실행", "❌ 취소"],
                [
                    "모든 파티원의 장비를 해제하고 AI로 최적화하여 재장착합니다",
                    "장비 최적화를 취소하고 이전 메뉴로 돌아갑니다"
                ]
            )
            
            choice = confirm_menu.run()
            if choice != 0:  # 취소
                return
            
            print(f"\n{bright_yellow('⚡ 장비 최적화를 시작합니다...')}")
            
            # 1단계: 모든 파티원의 장비 해제
            print(f"{bright_cyan('1️⃣ 모든 장비를 해제하는 중...')}")
            unequipped_count = 0
            
            for member in self.party_manager.members:
                if not member.is_alive:
                    continue
                    
                # 현재 장착된 장비 목록 가져오기
                equipped_items = member.get_equipped_items()
                
                for slot, item in equipped_items.items():
                    if item:
                        # 장비 해제
                        try:
                            success = member.unequip_item(slot)
                            if success:
                                unequipped_count += 1
                                print(f"   📤 {member.name}: {item.name} ({slot}) 해제됨")
                            else:
                                print(f"   ⚠️ {member.name}: {item.name} ({slot}) 해제 실패")
                        except Exception as e:
                            print(f"   ❌ {member.name}: {item.name} 해제 오류 - {e}")
            
            print(f"✅ {unequipped_count}개 장비 해제 완료!")
            
            # 2단계: AI 게임모드의 장비 최적화 시스템 사용
            print(f"{bright_cyan('2️⃣ AI 시스템으로 최적화 중...')}")
            
            try:
                # AI 게임모드 사용 여부 확인
                is_ai_mode = hasattr(self, 'ai_mode_active') and getattr(self, 'ai_mode_active', False)
                
                if is_ai_mode:
                    # AI 게임모드: 개별 캐릭터만 최적화 (전체 분배 방지)
                    print(f"   🤖 AI 게임모드: 개별 캐릭터 최적화 방식 사용")
                    from game.ai_game_mode import BasicEquipmentManager
                    basic_manager = BasicEquipmentManager()
                    
                    optimization_results = []
                    
                    for member in self.party_manager.members:
                        if not member.is_alive:
                            continue
                        
                        print(f"   🔧 {member.name} 개별 최적화 중...")
                        
                        # 해당 캐릭터의 인벤토리 아이템만 사용
                        character_items = []
                        if hasattr(member, 'inventory'):
                            if hasattr(member.inventory, 'get_all_items'):
                                character_items = member.inventory.get_all_items()
                            elif hasattr(member.inventory, 'items'):
                                character_items = list(member.inventory.items.keys())
                        
                        equipped_items = basic_manager.auto_equip_best_items(member, character_items)
                        if equipped_items:
                            optimization_results.append(f"   ✅ {member.name}: {len(equipped_items)}개 개별 최적화 완료")
                        else:
                            optimization_results.append(f"   ⚪ {member.name}: 개별 최적화 가능한 장비 없음")
                
                else:
                    # 일반 모드: 전체 파티 공평 분배 시스템 사용
                    print(f"   ⚖️ 일반 모드: 전체 파티 공평 분배 시스템 사용")
                    
                    # 모든 파티원의 인벤토리에서 장비 아이템 수집
                    from game.items import ItemDatabase, ItemType
                    item_db = ItemDatabase()
                    all_equipment_items = []
                    
                    for member in self.party_manager.members:
                        if hasattr(member, 'inventory') and hasattr(member.inventory, 'get_items_list'):
                            items_list = member.inventory.get_items_list()
                            print(f"   🎒 {member.name} 인벤토리: {len(items_list)}개 아이템")
                            
                            for item_name, quantity in items_list:
                                item = item_db.get_item(item_name)
                                # 장비 타입 확인 (WEAPON, ARMOR, ACCESSORY)
                                if item and item.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY]:
                                    # 장비 아이템만 수집
                                    print(f"      ⚔️ {item_name} ({quantity}개) - {item.item_type.value}")
                                    for _ in range(min(quantity, 10)):  # 최대 10개까지만 처리 (성능상 이유)
                                        all_equipment_items.append(item)
                    
                    print(f"   📦 발견된 장비 아이템: {len(all_equipment_items)}개")
                    
                    # 디버그: 발견된 장비 목록 출력
                    if all_equipment_items:
                        equipment_names = [item.name for item in all_equipment_items[:5]]  # 처음 5개만
                        print(f"   🔍 장비 예시: {', '.join(equipment_names)}")
                        if len(all_equipment_items) > 5:
                            print(f"   ... 외 {len(all_equipment_items) - 5}개 더")
                    
                    # 장비가 있다면 최적화 실행, 없다면 기본 처리
                    if all_equipment_items:
                        try:
                            print(f"   🔧 장비 최적화 시스템 실행 중... ({len(all_equipment_items)}개 장비)")
                            from game.equipment_helpers import optimize_all_equipment
                            results = optimize_all_equipment(
                                self.party_manager.members, 
                                all_equipment_items, 
                                show_results=True  # 디버깅을 위해 활성화
                            )
                            
                            optimization_results = []
                            for member_name, result in results.items():
                                equipped_count = result.get('equipped', 0)
                                if equipped_count > 0:
                                    optimization_results.append(f"   ✅ {member_name}: {equipped_count}개 공평 분배 완료")
                                else:
                                    optimization_results.append(f"   ⚪ {member_name}: 분배 가능한 장비 없음")
                        except ImportError:
                            print("   ⚠️ 고급 최적화 시스템 사용 불가, 기본 최적화 사용")
                            optimization_results = self._fallback_equipment_optimization(all_equipment_items)
                    else:
                        print("   📭 인벤토리에 장비 아이템이 없습니다.")
                        optimization_results = []
                        for member in self.party_manager.members:
                            if member.is_alive:
                                optimization_results.append(f"   ⚪ {member.name}: 장비 아이템 없음")
                
            except ImportError:
                print("   ⚠️ 장비 최적화 시스템을 사용할 수 없습니다. 기본 최적화를 사용합니다.")
                
                # 폴백: 기본 장비 최적화
                optimization_results = []
                for member in self.party_manager.members:
                    if not member.is_alive:
                        continue
                    
                    print(f"   🔧 {member.name} 기본 최적화 중...")
                    equipped_items = self._auto_equip_best_items(member)
                    if equipped_items:
                        optimization_results.append(f"   ✅ {member.name}: {len(equipped_items)}개 아이템 자동 장착")
                    else:
                        optimization_results.append(f"   ⚠️ {member.name}: 장착 가능한 장비 없음")
            
            # 3단계: 결과 출력
            print(f"\n{bright_green('🎉 장비 최적화 완료!')}")
            print(f"{bright_cyan('=== 최적화 결과 ===')}")
            
            for result in optimization_results:
                print(result)
            
            # 4단계: 최적화된 파티 상태 표시
            print(f"\n{bright_cyan('=== 최적화된 파티 상태 ===')}")
            for member in self.party_manager.members:
                if not member.is_alive:
                    continue
                    
                print(f"\n👤 {member.name} ({getattr(member, 'character_class', '미정')})")
                equipped_items = member.get_equipped_items()
                
                if any(equipped_items.values()):
                    for slot, item in equipped_items.items():
                        if item:
                            # 내구도 정보
                            durability_info = ""
                            if hasattr(item, 'get_durability_percentage'):
                                durability_pct = item.get_durability_percentage()
                                durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
                                durability_info = f" {durability_color}{durability_pct:.0f}%"
                            
                            print(f"   {slot}: {item.name}{durability_info}")
                            
                            # 능력치 보너스 표시
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
                                
                                if stat_bonuses:
                                    print(f"      💪 효과: {', '.join(stat_bonuses)}")
                else:
                    print("   장비 없음")
            
            print(f"\n{bright_yellow('💡 팁: 던전에서 새로운 장비를 얻으면 언제든 다시 최적화할 수 있습니다!')}")
            
        except Exception as e:
            print(f"❌ 장비 최적화 시스템 오류: {type(e).__name__}")
            print(f"📋 오류 상세: {str(e)}")
            
            # 추가 디버그 정보
            import traceback
            print(f"🔍 상세 오류 추적:")
            print(traceback.format_exc())
            
            print("\n🔧 문제가 발생한 경우 다음을 시도해보세요:")
            print("   1. 게임을 다시 시작")
            print("   2. 수동으로 장비 관리")
            print("   3. 저장 후 재로드")
            print("\n💡 기본 인벤토리 시스템을 사용하세요.")
            
            # 안전 장치: 기본 상태 복구
            try:
                print(f"\n🔄 기본 파티 상태 복구 중...")
                for member in self.party_manager.members:
                    if member.is_alive and hasattr(member, 'calculate_total_stats'):
                        member.calculate_total_stats()
                        print(f"   ✅ {member.name} 상태 복구 완료")
            except Exception as recovery_error:
                print(f"   ⚠️ 상태 복구 실패: {recovery_error}")
        
        self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def _fallback_equipment_optimization(self, equipment_items):
        """폴백 장비 최적화 시스템"""
        results = []
        
        try:
            from game.items import ItemDatabase, ItemType
            item_db = ItemDatabase()
            
            # 슬롯별로 아이템 분류
            slot_items = {
                'weapon': [],
                'armor': [],
                'accessory': []
            }
            
            for item in equipment_items:
                if hasattr(item, 'subtype'):
                    if 'weapon' in item.subtype.lower() or 'sword' in item.subtype.lower():
                        slot_items['weapon'].append(item)
                    elif 'armor' in item.subtype.lower() or 'helmet' in item.subtype.lower():
                        slot_items['armor'].append(item)
                    elif 'accessory' in item.subtype.lower() or 'ring' in item.subtype.lower():
                        slot_items['accessory'].append(item)
                elif hasattr(item, 'name'):
                    # 이름으로 추정
                    item_name_lower = item.name.lower()
                    if any(weapon_word in item_name_lower for weapon_word in ['검', '칼', '활', '봉', '창', '도끼', 'sword', 'bow', 'staff']):
                        slot_items['weapon'].append(item)
                    elif any(armor_word in item_name_lower for armor_word in ['갑옷', '투구', '방패', 'armor', 'helmet', 'shield']):
                        slot_items['armor'].append(item)
                    else:
                        slot_items['accessory'].append(item)
            
            # 각 파티원에게 순차적으로 분배
            for member in self.party_manager.members:
                if not member.is_alive:
                    continue
                
                equipped_count = 0
                
                # 각 슬롯별로 최고 아이템 장착
                for slot_name, items in slot_items.items():
                    if items:
                        # 스탯 총합이 가장 높은 아이템 선택
                        best_item = max(items, key=lambda x: self._calculate_item_value(x, member))
                        
                        # 아이템 장착 시도
                        if hasattr(member, 'equip_item'):
                            try:
                                success = member.equip_item(best_item)
                                if success:
                                    equipped_count += 1
                                    # 사용된 아이템은 제거
                                    slot_items[slot_name].remove(best_item)
                            except Exception as e:
                                print(f"   ⚠️ {member.name} {best_item.name} 장착 실패: {e}")
                
                if equipped_count > 0:
                    results.append(f"   ✅ {member.name}: {equipped_count}개 기본 최적화 완료")
                else:
                    results.append(f"   ⚪ {member.name}: 기본 최적화 가능한 장비 없음")
            
        except Exception as e:
            print(f"   ❌ 폴백 최적화 오류: {e}")
            for member in self.party_manager.members:
                if member.is_alive:
                    results.append(f"   ❌ {member.name}: 최적화 실패")
        
        return results
    
    def _calculate_item_value(self, item, character):
        """캐릭터에 대한 아이템 가치 계산"""
        value = 0
        
        try:
            if hasattr(item, 'stats') and item.stats:
                # 기본 스탯 가치
                value += item.stats.get('physical_attack', 0) * 2
                value += item.stats.get('magic_attack', 0) * 2
                value += item.stats.get('physical_defense', 0) * 1.5
                value += item.stats.get('magic_defense', 0) * 1.5
                value += item.stats.get('speed', 0) * 1
                
                # 직업별 가중치 적용
                character_class = getattr(character, 'character_class', '전사')
                if character_class in ['전사', '검성', '기사', '검투사']:
                    value += item.stats.get('physical_attack', 0) * 1  # 물리공격 추가 가중
                elif character_class in ['아크메이지', '정령술사', '네크로맨서']:
                    value += item.stats.get('magic_attack', 0) * 1  # 마법공격 추가 가중
                elif character_class in ['궁수', '도적', '암살자']:
                    value += item.stats.get('speed', 0) * 1.5  # 속도 추가 가중
        except:
            value = 1  # 기본값
        
        return value

    def _auto_equip_best_items(self, character):
        """캐릭터에게 최적의 장비를 자동 장착 (폴백 함수)"""
        equipped_items = []
        
        try:
            from game.items import ItemDatabase, ItemType
            item_db = ItemDatabase()
            
            # 캐릭터의 인벤토리에서 장비 아이템 찾기
            available_equipment = {}  # slot -> [items]
            
            if hasattr(character, 'inventory') and character.inventory:
                if hasattr(character.inventory, 'items'):
                    for item_name, quantity in character.inventory.items.items():
                        if quantity > 0:
                            item = item_db.get_item(item_name)
                            if item and item.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY]:
                                # 장비 슬롯 결정
                                slot = self._get_equipment_slot(item)
                                if slot:
                                    if slot not in available_equipment:
                                        available_equipment[slot] = []
                                    available_equipment[slot].append(item)
            
            # 각 슬롯별로 최적 장비 선택 및 장착
            character_class = getattr(character, 'character_class', '전사')
            
            for slot, items in available_equipment.items():
                if not items:
                    continue
                
                # 최적 아이템 선택 (직업 적합성 + 능력치 고려)
                best_item = None
                best_score = -1
                
                for item in items:
                    score = self._calculate_equipment_score(item, character_class, slot)
                    if score > best_score:
                        best_score = score
                        best_item = item
                
                # 최적 아이템 장착
                if best_item:
                    try:
                        success = character.equip_item(best_item)  # slot 파라미터 제거
                        if success:
                            equipped_items.append(f"{best_item.name} ({slot})")
                            # 인벤토리에서 제거
                            if hasattr(character.inventory, 'remove_item'):
                                character.inventory.remove_item(best_item.name, 1)
                    except Exception as e:
                        print(f"   ⚠️ {best_item.name} 장착 실패: {e}")
        
        except Exception as e:
            print(f"   ❌ 자동 장착 오류: {e}")
        
        return equipped_items

    def _get_equipment_slot(self, item):
        """아이템의 장비 슬롯 결정"""
        from game.items import ItemType
        
        if item.item_type == ItemType.WEAPON:
            return "weapon"
        elif item.item_type == ItemType.ARMOR:
            return "armor"
        elif item.item_type == ItemType.ACCESSORY:
            return "accessory"
        else:
            return None

    def _calculate_equipment_score(self, item, character_class, slot):
        """장비 아이템의 점수 계산 (직업 적합성 + 능력치)"""
        score = 0
        
        # 기본 능력치 보너스
        if hasattr(item, 'stats') and item.stats:
            for stat, value in item.stats.items():
                if isinstance(value, (int, float)) and value > 0:
                    score += value
        
        # 직업별 가중치 적용
        class_preferences = {
            '전사': {'weapon': 1.5, 'armor': 1.3, 'accessory': 1.0},
            '아크메이지': {'weapon': 1.2, 'armor': 1.0, 'accessory': 1.4},
            '궁수': {'weapon': 1.4, 'armor': 1.1, 'accessory': 1.2},
            '도적': {'weapon': 1.3, 'armor': 1.0, 'accessory': 1.3},
            '성기사': {'weapon': 1.2, 'armor': 1.4, 'accessory': 1.1},
            '암흑기사': {'weapon': 1.3, 'armor': 1.2, 'accessory': 1.1},
        }
        
        if character_class in class_preferences and slot in class_preferences[character_class]:
            score *= class_preferences[character_class][slot]
        
        # 내구도 고려 (내구도가 높을수록 선호)
        if hasattr(item, 'get_durability_percentage'):
            durability_pct = item.get_durability_percentage()
            score *= (durability_pct / 100.0)
        
        return score
    
    def _update_enemy_difficulty(self):
        """파티 변경 시 적 난이도 업데이트"""
        try:
            if hasattr(self, 'dynamic_scaler') and self.dynamic_scaler and hasattr(self, 'party_manager'):
                party_members = []
                if hasattr(self.party_manager, 'get_active_party'):
                    party_members = self.party_manager.get_active_party()
                elif hasattr(self.party_manager, 'party') and self.party_manager.party:
                    party_members = self.party_manager.party
                
                if party_members:
                    update_difficulty_for_party(party_members)
        except Exception as e:
            # 조용히 실패 처리
            pass

    def _handle_item_transfer(self):
        """파티원 간 아이템 전송 처리"""
        try:
            from game.cursor_menu_system import create_simple_menu
            from game.items import ItemDatabase
            
            print(f"\n{bright_cyan('=== 📦 아이템 전송 ===')}")
            print("파티원 간 아이템을 주고받을 수 있습니다.")
            
            # 1단계: 아이템을 줄 파티원 선택
            source_options = []
            source_descriptions = []
            valid_sources = []
            
            for member in self.party_manager.members:
                if hasattr(member, 'inventory') and member.inventory.items:
                    item_count = len(member.inventory.items)
                    total_items = sum(member.inventory.items.values())
                    source_options.append(f"{member.name} ({total_items}개 아이템)")
                    source_descriptions.append(f"보유 아이템 종류: {item_count}개")
                    valid_sources.append(member)
            
            if not valid_sources:
                print("📦 전송할 아이템이 있는 파티원이 없습니다.")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                return
            
            source_options.append("🚪 취소")
            source_descriptions.append("아이템 전송을 취소합니다")
            
            source_menu = create_simple_menu("📤 아이템을 줄 파티원", source_options, source_descriptions)
            source_choice = source_menu.run()
            
            if source_choice is None or source_choice >= len(valid_sources):
                return
            
            source_member = valid_sources[source_choice]
            
            # 2단계: 전송할 아이템 선택
            item_options = []
            item_descriptions = []
            valid_items = []
            
            item_db = ItemDatabase()
            for item_name, quantity in source_member.inventory.items.items():
                item_options.append(f"{item_name} x{quantity}")
                
                # 아이템 정보 가져오기
                item = item_db.get_item(item_name)
                if item:
                    desc = item.description[:50] + "..." if len(item.description) > 50 else item.description
                    item_descriptions.append(desc)
                else:
                    item_descriptions.append("아이템 정보 없음")
                
                valid_items.append((item_name, quantity))
            
            item_options.append("🚪 취소")
            item_descriptions.append("아이템 선택을 취소합니다")
            
            item_menu = create_simple_menu(f"📦 {source_member.name}의 아이템", item_options, item_descriptions)
            item_choice = item_menu.run()
            
            if item_choice is None or item_choice >= len(valid_items):
                return
            
            selected_item_name, max_quantity = valid_items[item_choice]
            
            # 3단계: 전송할 수량 선택 (수량이 1개보다 많은 경우)
            transfer_quantity = 1
            if max_quantity > 1:
                quantity_options = []
                quantity_descriptions = []
                
                for i in range(1, min(max_quantity + 1, 11)):  # 최대 10개까지만 메뉴로 표시
                    quantity_options.append(f"{i}개")
                    quantity_descriptions.append(f"{selected_item_name} {i}개를 전송합니다")
                
                if max_quantity > 10:
                    quantity_options.append("전체")
                    quantity_descriptions.append(f"{selected_item_name} 전체 {max_quantity}개를 전송합니다")
                
                quantity_options.append("🚪 취소")
                quantity_descriptions.append("수량 선택을 취소합니다")
                
                quantity_menu = create_simple_menu("📊 전송할 수량", quantity_options, quantity_descriptions)
                quantity_choice = quantity_menu.run()
                
                if quantity_choice is None or quantity_choice >= len(quantity_options) - 1:
                    return
                
                if quantity_choice < len(quantity_options) - 2:  # 개별 수량 선택
                    transfer_quantity = quantity_choice + 1
                else:  # 전체 선택
                    transfer_quantity = max_quantity
            
            # 4단계: 받을 파티원 선택
            target_options = []
            target_descriptions = []
            valid_targets = []
            
            for member in self.party_manager.members:
                if member != source_member:  # 자기 자신 제외
                    if hasattr(member, 'inventory'):
                        # 인벤토리 용량 확인
                        can_add, reason = member.inventory.can_add_item(item_db.get_item(selected_item_name) or type('DummyItem', (), {'weight': 1.0})(), transfer_quantity)
                        
                        if can_add:
                            target_options.append(f"{member.name} ✅")
                            target_descriptions.append("아이템을 받을 수 있습니다")
                            valid_targets.append(member)
                        else:
                            target_options.append(f"{member.name} ❌")
                            target_descriptions.append(f"불가능: {reason}")
            
            if not valid_targets:
                print("📦 아이템을 받을 수 있는 파티원이 없습니다.")
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
                return
            
            target_options.append("🚪 취소")
            target_descriptions.append("아이템 전송을 취소합니다")
            
            target_menu = create_simple_menu("📥 아이템을 받을 파티원", target_options, target_descriptions)
            target_choice = target_menu.run()
            
            if target_choice is None or target_choice >= len(valid_targets):
                return
            
            target_member = valid_targets[target_choice]
            
            # 5단계: 전송 확인 및 실행
            print(f"\n{bright_yellow('=== 전송 확인 ===')}")
            print(f"📤 보내는 사람: {source_member.name}")
            print(f"📥 받는 사람: {target_member.name}")
            print(f"📦 아이템: {selected_item_name} x{transfer_quantity}")
            
            confirm_options = ["✅ 전송", "🚪 취소"]
            confirm_descriptions = ["아이템을 전송합니다", "전송을 취소합니다"]
            
            confirm_menu = create_simple_menu("❓ 정말 전송하시겠습니까?", confirm_options, confirm_descriptions)
            confirm_choice = confirm_menu.run()
            
            if confirm_choice == 0:  # 전송 실행
                # 아이템 제거
                if source_member.inventory.remove_item(selected_item_name, transfer_quantity):
                    # 아이템 추가
                    item_to_transfer = item_db.get_item(selected_item_name)
                    if item_to_transfer and target_member.inventory.add_item(item_to_transfer, transfer_quantity):
                        print(f"\n{bright_green('✅ 전송 완료!')}")
                        print(f"📦 {selected_item_name} x{transfer_quantity}을(를) {source_member.name}에서 {target_member.name}으로 전송했습니다.")
                    else:
                        # 실패 시 롤백
                        source_member.inventory.add_item(item_to_transfer, transfer_quantity)
                        print(f"\n{bright_red('❌ 전송 실패!')}")
                        print("대상의 인벤토리에 아이템을 추가할 수 없습니다.")
                else:
                    print(f"\n{bright_red('❌ 전송 실패!')}")
                    print("아이템을 제거할 수 없습니다.")
                
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            
        except Exception as e:
            print(f"❌ 아이템 전송 중 오류 발생: {e}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")


# 게임 데이터 초기화 시 채집 관련 변수 추가
def initialize_gather_variables(game_data):
    if 'last_gather_steps' not in game_data:
        game_data['last_gather_steps'] = 0
        
    if 'total_steps' not in game_data:
        game_data['total_steps'] = 0

# 채집 쿨타임 확인 함수
def can_gather(game_data):
    """채집 가능 여부 확인"""
    if 'last_gather_steps' not in game_data:
        return True, 0
    
    steps_since_gather = game_data.get('total_steps', 0) - game_data.get('last_gather_steps', 0)
    if steps_since_gather >= 300:
        return True, 0
    else:
        remaining_steps = 300 - steps_since_gather
        return False, remaining_steps

def update_gather_cooldown(game_data):
    """채집 완료 시 쿨타임 업데이트"""
    game_data['last_gather_steps'] = game_data.get('total_steps', 0)

def increment_steps(game_data):
    """걸음 수 증가"""
    game_data['total_steps'] = game_data.get('total_steps', 0) + 1

def handle_interaction(game):
    """플레이어 주변 상호작용 처리 (커서 메뉴 사용)"""
    try:
        if not hasattr(game, 'world') or not game.world:
            print("❌ 월드 정보가 없습니다.")
            return
        
        # 플레이어 주변의 상호작용 가능한 객체들 확인
        interactables = game.world.get_interactable_nearby(game.world.player_pos)
        
        if not interactables:
            # SFX 재생
            try:
                from game.audio_system import SFXType
                if hasattr(game, 'audio_system') and game.audio_system:
                    game.audio_system.play_sfx(SFXType.INTERACT_FAIL)
            except:
                pass
            print("💬 주변에 상호작용할 수 있는 것이 없습니다.")
            game.keyboard.wait_for_key("계속하려면 아무 키나 누르세요...")
            return
        
        # 상호작용 가능한 객체가 1개인 경우 바로 실행
        if len(interactables) == 1:
            target = interactables[0]
            result = game.world.interact_with_tile(target['pos'])
            
            # 결과에 따른 SFX 결정
            sfx_type = None
            try:
                from game.audio_system import SFXType
                if result['success']:
                    # 상호작용 타입에 따른 FFVII 기반 SFX
                    obj_type = target.get('type', '')
                    if obj_type == 'locked_door':
                        sfx_type = SFXType.LOCK_PICK      # 문열림
                    elif obj_type == 'secret_door':
                        sfx_type = SFXType.SECRET_FOUND   # 아이템픽업
                    elif obj_type == 'treasure_chest':
                        sfx_type = SFXType.TREASURE_OPEN  # 보물상자
                    elif obj_type == 'altar':
                        sfx_type = SFXType.ALTAR_ACTIVATE # 치유
                    elif obj_type == 'lever':
                        sfx_type = SFXType.LEVER_PULL     # 장비장착
                    elif obj_type == 'bookshelf':
                        sfx_type = SFXType.BOOKSHELF_READ # 스킬습득
                    elif obj_type == 'forge':
                        sfx_type = SFXType.FORGE_USE      # 장비장착
                    elif obj_type == 'fountain':
                        sfx_type = SFXType.FOUNTAIN_DRINK # 포션
                    elif obj_type == 'crystal':
                        sfx_type = SFXType.CRYSTAL_TOUCH  # 마법시전
                    elif obj_type in ['cursed_altar', 'cursed_chest', 'poison_cloud', 'dark_portal', 'unstable_floor']:
                        sfx_type = SFXType.CURSED_ACTIVATE # 디버프적용
                    else:
                        sfx_type = SFXType.INTERACT_SUCCESS # 아이템획득
                else:
                    sfx_type = SFXType.INTERACT_FAIL       # 메뉴에러
            except:
                pass
            
            # 결과 메시지 표시
            if result.get('boss_battle', False):
                # 보스 전투 시작
                boss = result.get('boss')
                if boss:
                    print(f"👑 {boss.name}와의 전투가 시작됩니다!")
                    
                    # 보스 BGM 재생 (편익천사 제외)
                    try:
                        if hasattr(game, 'audio_system') and game.audio_system:
                            # 일반 보스 전용 BGM (편익천사 아님)
                            game.audio_system.play_bgm("battle_boss")
                    except:
                        pass
                    
                    # 전투 시작
                    if hasattr(game, 'combat_system') and game.combat_system:
                        try:
                            victory = game.combat_system.start_battle(
                                game.party_manager.members, 
                                [boss], 
                                is_boss_battle=True
                            )
                            
                            if victory:
                                print(f"🎉 {boss.name}을(를) 처치했습니다!")
                                # 보스 제거
                                if hasattr(game.world, 'enemies') and boss in game.world.enemies:
                                    game.world.enemies.remove(boss)
                                # 보스 타일을 일반 바닥으로 변경
                                game.world.tiles[target['pos'][1]][target['pos'][0]].type = game.world.TileType.FLOOR
                                
                                # 일반 BGM으로 복원
                                try:
                                    if hasattr(game, 'audio_system') and game.audio_system:
                                        game.audio_system.play_bgm("dungeon")
                                except:
                                    pass
                            else:
                                print("💀 보스 전투에서 패배했습니다...")
                        except Exception as e:
                            print(f"⚠️ 보스 전투 오류: {e}")
                else:
                    print("⚠️ 보스를 찾을 수 없습니다.")
                    
            elif result.get('pause', False):
                game.world.show_interaction_message(result['message'], True, sfx_type)
            else:
                print(f"💬 {result['message']}")
                
        else:
            # 여러 개인 경우 커서 메뉴 표시
            try:
                from game.cursor_menu_system import create_simple_menu
                
                # 메뉴 옵션 생성
                options = []
                descriptions = []
                
                for obj in interactables:
                    status = "✅" if not obj.get('used', False) else "❌"
                    skill_info = f" (필요: {obj.get('required_skill', '없음')})" if obj.get('required_skill') else ""
                    options.append(f"{status} {obj['name']}{skill_info}")
                    descriptions.append(obj['description'])
                
                # 상호작용 메뉴 생성
                menu = create_simple_menu("🔍 상호작용할 객체 선택", options, descriptions)
                choice = menu.run()
                
                if choice is not None and 0 <= choice < len(interactables):
                    target = interactables[choice]
                    result = game.world.interact_with_tile(target['pos'])
                    
                    # 결과에 따른 SFX 결정
                    sfx_type = None
                    try:
                        from game.audio_system import SFXType
                        if result['success']:
                            # 상호작용 타입에 따른 FFVII 기반 SFX
                            obj_type = target.get('type', '')
                            if obj_type == 'locked_door':
                                sfx_type = SFXType.LOCK_PICK      # 문열림
                            elif obj_type == 'secret_door':
                                sfx_type = SFXType.SECRET_FOUND   # 아이템픽업
                            elif obj_type == 'treasure_chest':
                                sfx_type = SFXType.TREASURE_OPEN  # 보물상자
                            elif obj_type == 'altar':
                                sfx_type = SFXType.ALTAR_ACTIVATE # 치유
                            elif obj_type == 'lever':
                                sfx_type = SFXType.LEVER_PULL     # 장비장착
                            elif obj_type == 'bookshelf':
                                sfx_type = SFXType.BOOKSHELF_READ # 스킬습득
                            elif obj_type == 'forge':
                                sfx_type = SFXType.FORGE_USE      # 장비장착
                            elif obj_type == 'fountain':
                                sfx_type = SFXType.FOUNTAIN_DRINK # 포션
                            elif obj_type == 'crystal':
                                sfx_type = SFXType.CRYSTAL_TOUCH  # 마법시전
                            elif obj_type in ['cursed_altar', 'cursed_chest', 'poison_cloud', 'dark_portal', 'unstable_floor']:
                                sfx_type = SFXType.CURSED_ACTIVATE # 디버프적용
                            else:
                                sfx_type = SFXType.INTERACT_SUCCESS # 아이템획득
                        else:
                            sfx_type = SFXType.INTERACT_FAIL       # 메뉴에러
                    except:
                        pass
                    
                    # 결과 메시지 표시
                    if result.get('pause', False):
                        game.world.show_interaction_message(result['message'], True, sfx_type)
                    else:
                        print(f"💬 {result['message']}")
                        
            except ImportError:
                # 커서 메뉴를 사용할 수 없는 경우 기본 방식 사용
                print(f"\n🔍 상호작용 가능한 객체들:")
                for i, obj in enumerate(interactables):
                    status = "✅" if not obj.get('used', False) else "❌"
                    skill_info = f" (필요: {obj.get('required_skill', '없음')})" if obj.get('required_skill') else ""
                    print(f"   {i+1}. {status} {obj['name']}{skill_info}")
                    print(f"      └─ {obj['description']}")
                
                print(f"   0. 취소")
                
                try:
                    choice = input("\n선택하세요 (번호): ").strip()
                    if choice == '0':
                        return
                    
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(interactables):
                        target = interactables[choice_idx]
                        result = game.world.interact_with_tile(target['pos'])
                        
                        # 결과 메시지 표시
                        if result.get('pause', False):
                            game.world.show_interaction_message(result['message'], True)
                        else:
                            print(f"💬 {result['message']}")
                    else:
                        print("❌ 잘못된 선택입니다.")
                        game.keyboard.wait_for_key("계속하려면 아무 키나 누르세요...")
                        
                except ValueError:
                    print("❌ 올바른 번호를 입력하세요.")
                    game.keyboard.wait_for_key("계속하려면 아무 키나 누르세요...")
                    
    except Exception as e:
        print(f"❌ 상호작용 처리 중 오류: {e}")
        game.keyboard.wait_for_key("계속하려면 아무 키나 누르세요...")

# ======================= MAIN FUNCTION =======================

def main():
    """메인 함수"""
    
    # 종료 처리 함수 정의
    def cleanup_and_exit(signum=None, frame=None):
        """안전한 종료 처리"""
        try:
            import pygame
            if pygame.get_init():
                pygame.mixer.quit()
                pygame.quit()
        except:
            pass
        
        # 강제 종료 시도
        try:
            import os
            os._exit(0)
        except:
            sys.exit(0)
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)
    atexit.register(cleanup_and_exit)
    
    try:
        # 윈도우 모드 EXE에서 오류 로깅 설정
        if getattr(sys, 'frozen', False):
            # PyInstaller 실행 파일인 경우 로그 파일 생성
            import logging
            log_file = os.path.join(os.path.dirname(sys.executable), 'game_error.log')
            logging.basicConfig(
                filename=log_file,
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            logging.info("=== 게임 시작 ===")
            
            # 윈도우 모드에서 콘솔 할당 시도
            try:
                import ctypes
                import io
                kernel32 = ctypes.windll.kernel32
                if kernel32.AllocConsole():
                    sys.stdout = io.TextIOWrapper(io.FileIO(kernel32.GetStdHandle(-11), 'w'), encoding='utf-8')
                    sys.stderr = io.TextIOWrapper(io.FileIO(kernel32.GetStdHandle(-12), 'w'), encoding='utf-8')
                    sys.stdin = io.TextIOWrapper(io.FileIO(kernel32.GetStdHandle(-10), 'r'), encoding='utf-8')
                    logging.info("Windows 콘솔 할당 성공")
                else:
                    logging.info("Windows 콘솔 할당 실패, 기존 콘솔 사용")
            except Exception as e:
                logging.error(f"콘솔 할당 중 오류: {e}")
                # stdout이 없는 경우에만 StringIO로 대체
                if sys.stdout is None:
                    import io
                    sys.stdout = io.StringIO()
                    sys.stderr = io.StringIO()
                    logging.info("stdout/stderr를 StringIO로 대체함")
        
        # 터미널 모드 체크 및 게임패드 비활성화
        if os.getenv('TERMINAL_MODE') == '1' or os.getenv('DISABLE_GAMEPAD') == '1':
            print("🖥️  터미널 모드: 게임패드 완전 비활성화")
            # pygame 초기화 방지를 위한 환경 변수 설정
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            print("✅ SDL 시스템 비활성화 완료")
        
        # 폰트 시스템 초기화
        if FONT_MANAGER_AVAILABLE:
            print("🎨 폰트 시스템 초기화 중...")
            font_manager = get_font_manager()
            print()  # 줄바꿈
        
        # 게임 인스턴스 생성
        game = DawnOfStellarGame()
        
        # 게임 데이터 초기화 시 채집 변수도 초기화
        if hasattr(game, 'meta_progression') and hasattr(game.meta_progression, 'data'):
            initialize_gather_variables(game.meta_progression.data)
        
        # 메인 루프 실행
        game.main_loop()
        
    except KeyboardInterrupt:
        msg = "게임이 중단되었습니다."
        print(f"\n{bright_yellow(msg)}")
        if getattr(sys, 'frozen', False):
            logging.info(msg)
    except Exception as e:
        import traceback
        error_msg = f'오류가 발생했습니다: {e}'
        print(f"\n{bright_red(error_msg)}")
        print(f"{bright_yellow('상세 오류 정보:')}")
        traceback.print_exc()
        
        # PyInstaller 실행파일인 경우 로그 파일에 오류 기록
        if getattr(sys, 'frozen', False):
            logging.error(error_msg)
            logging.error("상세 오류:", exc_info=True)
    finally:
        # 게임 객체 정리
        try:
            if 'game' in locals():
                game.cleanup()
        except:
            pass
        
        # 강제 정리
        try:
            import pygame
            if pygame.get_init():
                pygame.mixer.quit()
                pygame.quit()
        except:
            pass
        
        print(f"{bright_cyan('게임을 종료합니다.')}")
        
        # 윈도우 모드에서 종료 전 대기
        if getattr(sys, 'frozen', False):
            if getattr(sys, 'frozen', False):
                logging.info("=== 게임 종료 ===")
            
            # 윈도우 모드에서 메시지박스로 로그 확인 안내
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()  # 메인 창 숨김
                
                log_file = os.path.join(os.path.dirname(sys.executable), 'game_error.log')
                if os.path.exists(log_file):
                    message = f"게임이 종료되었습니다.\n\n로그 파일 위치:\n{log_file}\n\n로그를 확인하시겠습니까?"
                    result = messagebox.askyesno("게임 종료", message)
                    if result:
                        import subprocess
                        subprocess.run(['notepad.exe', log_file])
                else:
                    messagebox.showinfo("게임 종료", "게임이 정상적으로 종료되었습니다.")
                
                root.destroy()
            except:
                # tkinter가 없으면 간단한 대기
                try:
                    import time
                    time.sleep(3)
                except:
                    pass
            
            os._exit(0)
        else:
            # 콘솔 모드에서는 자동 종료
            try:
                print("\n게임이 종료되었습니다. 3초 후 자동으로 창이 닫힙니다...")
                import time
                time.sleep(3)
            except:
                pass
            
            # 강제 종료
            try:
                sys.exit(0)
            except:
                os._exit(0)


if __name__ == "__main__":
    main()
