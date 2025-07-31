"""
사운드 시스템 (pygame 기반 + 칩튠 SFX)
"""

import threading
import time
from typing import Dict, Optional
from enum import Enum

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    # pygame 없음 메시지 제거

try:
    from .chiptune_sfx import get_chiptune_sfx, play_chiptune_sound
    CHIPTUNE_AVAILABLE = True
except ImportError:
    CHIPTUNE_AVAILABLE = False
    # 칩튠 사운드 시스템 메시지 제거


class SoundType(Enum):
    """사운드 타입"""
    BGM = "bgm"
    SFX = "sfx"
    VOICE = "voice"


class SoundManager:
    """사운드 관리자"""
    
    def __init__(self):
        self.enabled = PYGAME_AVAILABLE
        self.bgm_volume = 0.5
        self.sfx_volume = 0.7
        self.sounds: Dict[str, any] = {}
        self.current_bgm = None
        
        if self.enabled:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                # 초기화 메시지 제거
            except:
                self.enabled = False
                # 초기화 실패 메시지 제거
                
    def load_sound(self, name: str, file_path: str, sound_type: SoundType = SoundType.SFX):
        """사운드 파일 로드"""
        if not self.enabled:
            return False
            
        try:
            if sound_type == SoundType.BGM:
                # BGM은 스트리밍으로 처리
                self.sounds[name] = {"path": file_path, "type": sound_type}
            else:
                # SFX는 메모리에 로드
                sound = pygame.mixer.Sound(file_path)
                self.sounds[name] = {"sound": sound, "type": sound_type}
            return True
        except Exception as e:
            print(f"사운드 로드 실패 ({name}): {e}")
            return False
            
    def play_sfx(self, name: str, volume: Optional[float] = None):
        """효과음 재생"""
        if not self.enabled or name not in self.sounds:
            # 칩튠 대체 사운드 재생
            if CHIPTUNE_AVAILABLE:
                play_chiptune_sound(name)
            return
            
        try:
            sound_data = self.sounds[name]
            if sound_data["type"] == SoundType.SFX:
                if "dummy" in sound_data:
                    # 더미 사운드의 경우 텍스트 출력 또는 칩튠으로 대체
                    if "text" in sound_data:
                        print(sound_data["text"])
                    elif CHIPTUNE_AVAILABLE:
                        play_chiptune_sound(name)
                    else:
                        print(f"♪ {name} 사운드 재생")
                elif "sound" in sound_data:
                    sound = sound_data["sound"]
                    if volume is not None:
                        sound.set_volume(volume)
                    else:
                        sound.set_volume(self.sfx_volume)
                    sound.play()
        except Exception as e:
            print(f"효과음 재생 실패 ({name}): {e}")
            # 실패 시 칩튠으로 대체
            if CHIPTUNE_AVAILABLE:
                play_chiptune_sound(name)
            
    def play_bgm(self, name: str, loops: int = -1, volume: Optional[float] = None):
        """배경음악 재생"""
        if not self.enabled or name not in self.sounds:
            return
            
        try:
            sound_data = self.sounds[name]
            if sound_data["type"] == SoundType.BGM:
                pygame.mixer.music.load(sound_data["path"])
                if volume is not None:
                    pygame.mixer.music.set_volume(volume)
                else:
                    pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(loops)
                self.current_bgm = name
        except Exception as e:
            print(f"배경음악 재생 실패 ({name}): {e}")
            
    def stop_bgm(self):
        """배경음악 정지"""
        if self.enabled:
            pygame.mixer.music.stop()
            self.current_bgm = None
            
    def pause_bgm(self):
        """배경음악 일시정지"""
        if self.enabled:
            pygame.mixer.music.pause()
            
    def resume_bgm(self):
        """배경음악 재개"""
        if self.enabled:
            pygame.mixer.music.unpause()
            
    def set_bgm_volume(self, volume: float):
        """배경음악 볼륨 설정 (0.0 ~ 1.0)"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.bgm_volume)
            
    def set_sfx_volume(self, volume: float):
        """효과음 볼륨 설정 (0.0 ~ 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def cleanup(self):
        """사운드 시스템 정리"""
        if self.enabled:
            pygame.mixer.quit()


class GameSounds:
    """게임 사운드 정의"""
    
    def __init__(self, sound_manager: SoundManager):
        self.sound_manager = sound_manager
        self.setup_sounds()
        
    def setup_sounds(self):
        """기본 사운드 설정 (실제 파일이 있다면)"""
        # FFVII BGM 맵핑 (층별 던전 탐험용)
        self.ffvii_bgm_map = {
            # 초기층 (1-3층): 평화로운 탐험
            "peaceful_dungeon": "Anxious Heart",
            "starting_dungeon": "Tifa's Theme",
            "town_exploration": "Under the Rotting Pizza",
            
            # 중반층 (4-7층): 모험적인 탐험
            "adventure_dungeon": "Main Theme of FFVII",
            "mysterious_dungeon": "Cosmo Canyon",
            "forest_dungeon": "Forest Temple",
            "cave_dungeon": "Caves of Narshe",
            
            # 후반층 (8-12층): 긴장감 있는 탐험
            "dark_dungeon": "Mako Reactor",
            "dangerous_dungeon": "Hurry Up!",
            "deep_dungeon": "Infiltrating Shinra",
            "shadow_dungeon": "Trail of Blood",
            "action_dungeon": "Opening - Bombing Mission",
            
            # 심층 (13-16층): 위험한 탐험
            "deeper_dungeon": "City of the Ancients",
            "ancient_dungeon": "Sleeping Forest",
            "ruins_dungeon": "Temple of the Ancients",
            "forgotten_dungeon": "Whirlwind Maze",
            
            # 최심층 (17-20층): 절망적인 탐험
            "nightmare_dungeon": "Jenova ABSOLUTE",
            "chaos_dungeon": "The Promised Land",
            "void_dungeon": "Reunion",
            "abyss_dungeon": "Lifestream",
            
            # 특수 상황
            "title_bgm": "Prelude",
            "victory": "Fanfare",
            "game_over": "Game Over",
        }
        
        # 전투 BGM (별도)
        self.ffvii_battle_bgm = {
            "normal_battle": "Fighting",
            "mini_boss": "Those Who Fight",
            "major_boss": "Birth of a God",
            "final_boss": "One-Winged Angel",
            "boss_battle": "Those Who Fight Further",
        }
        
        # 실제 사운드 파일들이 있다면 로드
        sound_files = {
            # 전투 효과음
            "brave_attack": "sounds/sfx/brave_attack.wav",
            "hp_attack": "sounds/sfx/hp_attack.wav",
            "break_sound": "sounds/sfx/break.wav",
            "critical_hit": "sounds/sfx/critical.wav",
            
            # UI 효과음
            "menu_select": "sounds/sfx/menu_select.wav",
            "menu_confirm": "sounds/sfx/menu_confirm.wav",
            "item_get": "sounds/sfx/item_get.wav",
            "combat_start": "sounds/sfx/combat_start.wav",
            
            # 상태 효과음
            "heal": "sounds/sfx/heal.wav",
            "poison": "sounds/sfx/poison.wav",
            "level_up": "sounds/sfx/level_up.wav",
        }
        
        # 실제로는 파일이 없으므로 더미 사운드로 대체
        self.create_dummy_sounds()
        
    def create_dummy_sounds(self):
        """더미 사운드 생성 (FFVII 스타일 SFX)"""
        # FFVII 스타일 효과음 매핑
        ffvii_sfx_sounds = {
            # 물리 공격 SFX
            "slash_combo": "🗡️ *SLASH-SLASH-SLASH!*",
            "sword_hit": "⚔️ *CLANG!*",
            "critical_hit": "💥 *CRITICAL HIT!*",
            "final_strike": "💀 *FINISHING BLOW!*",
            "warrior_roar": "🦁 *ROOOAR!*",
            "berserker_rage": "😡 *RAGE MODE!*",
            "gladiator_roar": "🏛️ *GLADIATOR!*",
            
            # 마법 SFX
            "fire_spell": "🔥 *FWOOSH!*",
            "ice_spell": "❄️ *FREEZE!*", 
            "lightning_spell": "⚡ *ZAP!*",
            "earth_spell": "🌍 *RUMBLE!*",
            "wind_spell": "💨 *WHOOSH!*",
            "water_spell": "💧 *SPLASH!*",
            "light_spell": "✨ *SHINE!*",
            "dark_spell": "🌑 *SHADOW!*",
            "poison_spell": "☠️ *POISON!*",
            
            # 원소 정령 소환
            "fire_summon": "🔥👹 *IFRIT SUMMONED!*",
            "ice_summon": "❄️🧊 *SHIVA SUMMONED!*",
            "lightning_summon": "⚡🐲 *RAMUH SUMMONED!*",
            "earth_summon": "🌍🗿 *TITAN SUMMONED!*",
            "elemental_storm": "🌪️ *ELEMENTAL CHAOS!*",
            
            # 치유 및 지원 SFX
            "heal_spell": "💚 *CURE!*",
            "holy_heal": "🕊️ *HOLY LIGHT!*",
            "water_heal": "💧💚 *AQUA HEAL!*",
            "mass_heal": "💚✨ *CURAGA!*",
            "buff_spell": "🌟 *BUFF APPLIED!*",
            "debuff_spell": "💀 *DEBUFF CAST!*",
            
            # 특수 스킬 SFX
            "time_stop": "⏰ *TIME STOP!*",
            "stealth": "👻 *VANISH!*",
            "poison_apply": "☠️ *POISON APPLIED!*",
            "ultimate_slash": "🌟⚔️ *OMNISLASH!*",
            "cosmic_truth": "🌌 *COSMIC POWER!*",
            "meteor_impact": "☄️ *METEOR!*",
            
            # 브레이브 시스템 SFX
            "brave_attack": "💪 *BRAVE ATTACK!*",
            "hp_attack": "❤️‍🔥 *HP ATTACK!*",
            "break_sound": "💥 *B-R-E-A-K!*",
            "brave_boost": "📈 *BRAVE UP!*",
            
            # UI 및 시스템 SFX
            "menu_select": "📋 *SELECT*",
            "menu_confirm": "✅ *CONFIRM*",
            "item_get": "🎁 *ITEM GET!*",
            "combat_start": "⚔️ *BATTLE START!*",
            "level_up": "🌟 *LEVEL UP!*",
            "victory": "🎉 *VICTORY!*",
            "defeat": "💀 *DEFEAT...*",
            
            # 크리티컬 및 특수 효과
            "perfect_critical": "🌟💥 *PERFECT!*",
            "legendary_critical": "⭐💥 *LEGENDARY!*",
            "miss": "💨 *MISS!*",
            "dodge": "🏃 *DODGE!*",
            "counter": "🔄 *COUNTER!*",
            
            # 상태이상 SFX
            "burn": "🔥 *BURNING!*",
            "freeze": "❄️ *FROZEN!*",
            "paralysis": "⚡ *PARALYZED!*",
            "poison": "☠️ *POISONED!*",
            "curse": "👹 *CURSED!*",
            "regeneration": "💚 *REGEN!*",
        }
        
        # 더미 사운드로 등록
        for sound_name, sound_text in ffvii_sfx_sounds.items():
            self.sound_manager.sounds[sound_name] = {
                "type": SoundType.SFX, 
                "dummy": True,
                "text": sound_text
            }
    
    def get_dungeon_bgm_by_floor(self, floor: int) -> str:
        """층수에 따른 던전 BGM 반환"""
        if floor <= 3:
            bgm_pool = ["peaceful_dungeon", "starting_dungeon", "town_exploration"]
        elif floor <= 7:
            bgm_pool = ["adventure_dungeon", "mysterious_dungeon", "forest_dungeon", "cave_dungeon"]
        elif floor <= 12:
            bgm_pool = ["dark_dungeon", "dangerous_dungeon", "deep_dungeon", "shadow_dungeon", "action_dungeon"]
        elif floor <= 16:
            bgm_pool = ["deeper_dungeon", "ancient_dungeon", "ruins_dungeon", "forgotten_dungeon"]
        else:
            bgm_pool = ["nightmare_dungeon", "chaos_dungeon", "void_dungeon", "abyss_dungeon"]
        
        # 층수 기반으로 일관된 BGM 선택
        import random
        random.seed(floor)  # 같은 층은 항상 같은 BGM
        selected_bgm = random.choice(bgm_pool)
        
        return self.ffvii_bgm_map.get(selected_bgm, "Main Theme of FFVII")
    
    def get_battle_bgm(self, is_boss: bool = False, boss_type: str = "normal") -> str:
        """전투 상황에 따른 BGM 반환"""
        if is_boss:
            if boss_type == "final":
                return self.ffvii_battle_bgm["final_boss"]
            elif boss_type == "major":
                return self.ffvii_battle_bgm["major_boss"]
            else:
                return self.ffvii_battle_bgm["mini_boss"]
        else:
            return self.ffvii_battle_bgm["normal_battle"]
    
    def play_ffvii_bgm(self, bgm_key: str):
        """FFVII BGM 재생 (텍스트 출력)"""
        if bgm_key in self.ffvii_bgm_map:
            bgm_title = self.ffvii_bgm_map[bgm_key]
            print(f"🎵 Now Playing: {bgm_title}")
        elif bgm_key in self.ffvii_battle_bgm:
            bgm_title = self.ffvii_battle_bgm[bgm_key]
            print(f"🎵 Battle Music: {bgm_title}")
        else:
            print(f"🎵 BGM: {bgm_key}")
            
    def play_brave_attack(self):
        """Brave 공격 사운드"""
        if self.sound_manager.enabled:
            self.sound_manager.play_sfx("brave_attack")
        else:
            print("♪ Brave 공격")
            
    def play_hp_attack(self):
        """HP 공격 사운드"""
        if self.sound_manager.enabled:
            self.sound_manager.play_sfx("hp_attack")
        else:
            print("♪ HP 공격")
            
    def play_break_sound(self):
        """Break 사운드"""
        if self.sound_manager.enabled:
            self.sound_manager.play_sfx("break_sound")
        else:
            print("B R E A K !")
            
    def play_critical_hit(self):
        """크리티컬 히트 사운드"""
        if self.sound_manager.enabled:
            self.sound_manager.play_sfx("critical_hit")
        else:
            print("CRITICAL!")
            
    def play_heal_sound(self):
        """치유 사운드"""
        if self.sound_manager.enabled:
            self.sound_manager.play_sfx("heal")
        else:
            print("♪ 치유")
            
    def play_menu_sound(self):
        """메뉴 선택 사운드"""
        if self.sound_manager.enabled:
            self.sound_manager.play_sfx("menu_select")
        else:
            print("♪ 메뉴")
    
    def play_item_get_sound(self):
        """아이템 획득 사운드"""
        if self.sound_manager.enabled:
            self.sound_manager.play_sfx("item_get")
        else:
            print("♪ 아이템 획득")
    
    def play_combat_start_sound(self):
        """전투 시작 사운드"""
        if self.sound_manager.enabled:
            self.sound_manager.play_sfx("combat_start")
        else:
            print("♪ 전투 시작")


# 전역 사운드 매니저 인스턴스
_sound_manager = None
_game_sounds = None

def get_sound_manager() -> SoundManager:
    """전역 사운드 매니저 반환"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager

def get_game_sounds() -> GameSounds:
    """전역 게임 사운드 반환"""
    global _game_sounds
    if _game_sounds is None:
        _game_sounds = GameSounds(get_sound_manager())
    return _game_sounds

def play_sound_effect(effect_name: str):
    """간편한 효과음 재생 함수 (칩튠 우선)"""
    # 먼저 칩튠 사운드 시도
    if CHIPTUNE_AVAILABLE:
        try:
            play_chiptune_sound(effect_name)
            return
        except Exception as e:
            print(f"칩튠 사운드 재생 실패: {e}")
    
    # 폴백: 기존 사운드 시스템 또는 텍스트
    sounds = get_game_sounds()
    
    effect_map = {
        "brave_attack": sounds.play_brave_attack,
        "hp_attack": sounds.play_hp_attack,
        "break": sounds.play_break_sound,
        "critical": sounds.play_critical_hit,
        "heal": sounds.play_heal_sound,
        "menu": sounds.play_menu_sound,
        "item_get": sounds.play_item_get_sound,
        "combat_start": sounds.play_combat_start_sound,
    }
    
    if effect_name in effect_map:
        effect_map[effect_name]()
    else:
        print(f"♪ {effect_name} 사운드")
