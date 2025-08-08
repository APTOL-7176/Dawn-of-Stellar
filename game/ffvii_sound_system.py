#!/usr/bin/env python3
"""
FFVII 사운드 팩 사용 시스템
실제 BGM과 SFX 파일들을 사용하는 향상된 사운드 시스템
"""

import pygame
import os
import random
from typing import Dict, Optional, Any
from enum import Enum
from pathlib import Path

class AudioCategory(Enum):
    BGM = "bgm"
    SFX = "sfx"
    UI = "ui"
    VOICE = "voice"
    AMBIENT = "ambient"

class FFVIISoundSystem:
    """FFVII 사운드 팩을 사용하는 사운드 시스템"""
    
    def __init__(self, debug_mode: bool = False):
        self.enabled = True
        self.debug_mode = debug_mode  # 디버그 모드 설정
        self.sounds = {}
        self.bgm_tracks = {}
        self.sfx_sounds = {}
        
        # 볼륨 설정
        self.master_volume = 0.7
        self.category_volumes = {
            AudioCategory.BGM: 0.6,
            AudioCategory.SFX: 0.8,
            AudioCategory.AMBIENT: 0.4,
            AudioCategory.UI: 0.7,
            AudioCategory.VOICE: 0.8
        }
        
        # 재생 채널
        self.current_bgm = None
        self.bgm_channel = None
        self.ambient_channel = None
        
        # 경로 설정
        self.base_path = Path("sounds")
        self.bgm_path = self.base_path / "bgm"
        self.sfx_path = self.base_path / "sfx"
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.set_num_channels(16)
            self._initialize_ffvii_sounds()
            if self.debug_mode:
                print("🎵 FFVII 사운드 시스템 초기화 완료!")
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ 사운드 시스템 초기화 실패: {e}")
            self.enabled = False
    
    def _initialize_ffvii_sounds(self):
        """FFVII 사운드 파일들을 로드하고 매핑"""
        self._load_bgm_tracks()
        self._load_sfx_sounds()
        self._setup_game_sound_mapping()
    
    def _load_bgm_tracks(self):
        """FFVII BGM 트랙들을 로드"""
        # 조용히 로드 (로그 출력 제거)
        
        # 게임 상황별 BGM 매핑
        self.bgm_mapping = {
            # 메인 테마들
            'title': '01-The Prelude.mp3',
            'main_theme': '25-Main Theme of Final Fantasy VII.mp3',
            'menu_theme': '01-The Prelude.mp3',           # 메인 메뉴용
            
            # 평화로운 지역
            'town': '27-Good Night, Until Tomorrow!.mp3',
            'safe_area': '13-Flowers Blooming in the Church.mp3',
            'character_select': '06-Tifa\'s Theme.mp3',
            
            # 기존 시스템 호환성을 위한 별칭들
            'bombing_mission': '03-Bombing Mission.mp3',    # 폭파 임무
            'mako_reactor': '04-Mako Reactor.mp3',          # 마코로 1호기
            'tifa_theme': '06-Tifa\'s Theme.mp3',           # 티파의 테마
            
            # 던전/탐험
            'dungeon': '04-Mako Reactor.mp3',
            'dungeon_theme': '04-Mako Reactor.mp3',        # 던전 테마용
            'dungeon_deep': '09-Lurking in the Darkness.mp3',
            'mysterious': '33-Chasing the Black-Caped Man.mp3',
            'cave': '46-Cosmo Canyon.mp3',
            
            # 전투
            'battle': '11-Fighting.mp3',
            'boss_battle': '21-Still More Fighting.mp3',
            'boss_theme': '21-Still More Fighting.mp3',    # 보스 테마용
            'final_boss': '38-J-E-N-O-V-A.mp3',
            'epic_battle': '87-One-Winged Angel.mp3',
            
            # 이벤트
            'victory': '12-Fanfare.mp3',
            'success': '59-A Great Success.mp3',
            'game_over': '39-Continue.mp3',
            'tension': '05-Anxious Heart.mp3',
            'urgent': '08-Hurry!.mp3',
            
            # 스토리
            'sad': '65-Aeris\' Theme.mp3',
            'dramatic': '52-The Nightmare\'s Beginning.mp3',
            'peaceful': '15-Underneath the Rotting Pizza.mp3',  # 1층 던전 BGM으로 변경!
            'credits': '89-Staff Roll.mp3'
        }
        
        # BGM 파일들을 실제로 로드
        for name, filename in self.bgm_mapping.items():
            file_path = self.bgm_path / filename
            if file_path.exists():
                try:
                    # pygame.mixer.music 대신 Sound 객체 사용 (더 나은 제어)
                    self.bgm_tracks[name] = str(file_path)
                    if self.debug_mode:
                        print(f"  ✅ {name}: {filename}")
                except Exception as e:
                    if self.debug_mode:
                        print(f"  ❌ {name} 로드 실패: {e}")
            else:
                if self.debug_mode:
                    print(f"  ⚠️ {name} 파일 없음: {filename}")
    
    def _load_sfx_sounds(self):
        """FFVII SFX 사운드들을 로드"""
        if self.debug_mode:
            print("🎵 FFVII SFX 로딩 중...")
        
        # 게임 액션별 SFX 매핑 (FFVII 공식 사운드 인덱스 기반)
        self.sfx_mapping = {
            # UI 사운드 (정확한 FFVII 인덱스 기반)
            'menu_navigate': '000.wav',    # 0 - Cursor Movement
            'save_ready': '001.wav',       # 1 - Save is Ready
            'menu_error': '002.wav',       # 2 - Invalid Choice  
            'menu_cancel': '003.wav',      # 3 - Cancel
            'miss': '004.wav',             # 4 - Missed Hit
            'atb_ready': '001.wav',        # ATB 턴 준비됨 (Save is Ready 사운드 재사용)
            'menu_select': '000.wav',      # 메뉴 선택 (커서 이동 사운드)
            'menu_confirm': '001.wav',     # 확인 (Save is Ready)
            
            # 치료/포션 사운드
            'heal': '005.wav',             # 5 - Cure Spell / Potion
            'potion_drink': '005.wav',     # 포션 사용
            'high_potion': '006.wav',      # 6 - High Potion
            'cure2': '007.wav',            # 7 - Cure 2 / X-Potion
            'cure3': '068.wav',            # 68 - Cure 3 / Elixir
            
            # 마법 시전
            'magic_cast': '012.wav',       # 12 - Preparing to Cast Magic
            'fire': '008.wav',             # 8 - Fire Spell
            'fire2': '009.wav',            # 9 - Fire 2
            'fire3': '141.wav',            # 141 - Fire 3
            'bolt': '010.wav',             # 10 - Bolt Spell
            'bolt2': '011.wav',            # 11 - Bolt 2 / Thunder Sound
            'bolt3': '069.wav',            # 69 - Bolt 3
            'ice': '023.wav',              # 23 - Ice Spell
            'ice3': '028.wav',             # 28 - Ice 3
            'quake': '070.wav',            # 70 - Quake Spell
            'bio': '062.wav',              # 62 - Bio Spell
            'demi': '029.wav',             # 29 - Demi Spell Main
            'comet': '075.wav',            # 75 - Comet Spell
            'flare': '369.wav',            # 369 - Flare Spell (first half)
            'ultima': '307.wav',           # 307 - Ultima Spell
            
            # 전투 사운드
            'sword_hit': '017.wav',        # 17 - Cloud's Sword Hit
            'sword_critical': '026.wav',   # 26 - Cloud Critical Sword Hit
            'slash': '017.wav',            # 17 - Cloud's Sword Hit (별칭)
            'arrow': '014.wav',            # 14 - Gun Hit (화살 대용)
            'gun_hit': '014.wav',          # 14 - Gun Hit
            'gun_critical': '045.wav',     # 45 - Barrett Critical Gun Hit
            'staff_hit': '049.wav',        # 49 - Aerith Staff Hit
            'staff_critical': '022.wav',   # 22 - Aerith Critical Staff Hit
            'punch': '027.wav',            # 27 - Punch
            'enemy_hit': '034.wav',        # 34 - Enemy Punch-type Attack
            'enemy_death': '021.wav',      # 21 - Enemy Death
            'boss_death': '445.wav',       # 445 - Boss Death
            'critical_hit': '026.wav',     # Cloud Critical Sword Hit
            'grenade': '019.wav',          # 19 - Grenade Item Explosion
            
            # 아이템/장비 사운드
            'item_use': '020.wav',         # 20 - Using an Item / Grabbing
            'item_pickup': '357.wav',      # 357 - Obtained Something
            'treasure_open': '253.wav',    # 253 - Treasure Chest Opening
            'equip': '444.wav',            # 444 - Equipping
            'buying': '261.wav',           # 261 - Buying Something
            'gil_pickup': '170.wav',       # 170 - Gil Coin
            
            # 환경/이동 사운드
            'door_open': '121.wav',        # 121 - Door Opening
            'elevator': '041.wav',         # 41 - Elevators
            'footsteps': '027.wav',        # 발소리 (Punch 사운드 재사용)
            'jumping': '054.wav',          # 54 - Jumping
            'landing': '055.wav',          # 55 - Landing
            'save_point': '356.wav',       # 356 - Save Point
            'save_game': '206.wav',        # 206 - Save is Launched
            
            # 전투 시스템
            'battle_start': '042.wav',     # 42 - Battle Swirl
            'escape': '025.wav',           # 25 - Escaping from a Battle
            'limit_break': '035.wav',      # 35 - Limit Break
            'dodge': '061.wav',            # 61 - Dodging an Attack
            'block': '061.wav',            # 방어 (회피 사운드 재사용)
            
            # 상태 효과
            'haste': '082.wav',            # 82 - Haste Spell
            'slow': '064.wav',             # 64 - Slow Spell
            'sleep': '072.wav',            # 72 - Sleep Spell
            'silence': '083.wav',          # 83 - Silence Spell
            'protect': '093.wav',          # 93 - Protect Spell
            'shell': '066.wav',            # 66 - Shell Spell
            'reflect': '071.wav',          # 71 - Reflect Spell
            'wall': '067.wav',             # 67 - Wall Spell
            'regen': '090.wav',            # 90 - Regen Spell
            'break_spell': '084.wav',      # 84 - Break Spell
            'stop': '086.wav',             # 86 - Stop Spell
            'berserk': '065.wav',          # 65 - Berserk Spell
            
            # 레벨업/성장
            'level_up': '381.wav',         # 381 - Fourth Limit Break Acquired
            'ability_learn': '381.wav',    # 능력 습득 (레벨업 사운드 재사용)
            'stat_increase': '381.wav',    # 스탯 증가 (레벨업 사운드 재사용)
            
            # 브레이브 시스템 (리미트 브레이크 사운드들 활용)
            'brave_attack': '035.wav',     # 35 - Limit Break
            'hp_attack': '026.wav',        # Cloud Critical Sword Hit
            'break_sound': '148.wav',      # 148 - Status Ailment Inflicted
            
            # 특수 이벤트
            'victory_fanfare': '012.wav',  # 승리 (FF7의 팡파레는 BGM)
            'game_start': '001.wav',       # 게임 시작
            'boss_roar': '429.wav',        # 429 - Weapon Roaring
            'alert': '059.wav',            # 59 - Alert
            'computer': '058.wav',         # 58 - Computer Bip
            
            # 환경 효과
            'wind_howl': '094.wav',        # 94 - Wind
            'water_drip': '403.wav',       # 403 - Some Splash
            'fire_crackle': '008.wav',     # Fire Spell 재사용
            'thunder': '011.wav',          # Bolt 2 / Thunder Sound
            'electricity': '143.wav',     # 143 - Electricity
            
            # 동물/몬스터 사운드
            'chocobo_happy': '273.wav',    # 273 - Chocobo Happy
            'chocobo_sad': '272.wav',      # 272 - Chocobo Sad
            'dog_bark': '245.wav',         # 245 - Dog Barking
            'moogle': '244.wav',           # 244 - Moogle
            'cat_meow': '452.wav',         # 452 - Meow
            
            # 특수 게임 메커니즘
            'materia_glow': '190.wav',     # 190 - Materia Glowing
            'phone_ring': '448.wav',       # 448 - PHS Ringing
            'machine_react': '266.wav',    # 266 - Some Machine Reacting
            'earning_points': '485.wav',   # 485 - Earning Points /GP
            'winning_prize': '250.wav',    # 250 - Winning a Prize
            'applause': '438.wav',         # 438 - Applauses
            
            # 피아노 사운드 (미니게임용)
            'piano_do': '506.wav',         # 506 - Piano Do
            'piano_re': '507.wav',         # 507 - Piano Re
            'piano_mi': '508.wav',         # 508 - Piano Mi
            'piano_fa': '509.wav',         # 509 - Piano Fa
            'piano_sol': '510.wav',        # 510 - Piano Sol
            'piano_la': '511.wav',         # 511 - Piano La
            'piano_si': '512.wav',         # 512 - Piano Si
        }
        
        # SFX 파일들을 실제로 로드
        loaded_count = 0
        for name, filename in self.sfx_mapping.items():
            file_path = self.sfx_path / filename
            if file_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(file_path))
                    self.sfx_sounds[name] = sound
                    loaded_count += 1
                except Exception as e:
                    if self.debug_mode:
                        print(f"  ❌ {name} 로드 실패: {e}")
                    # Fallback 비활성화 - 로드 실패한 SFX는 건너뜀
            else:
                # 파일이 없으면 건너뜀 (Fallback 비활성화)
                if self.debug_mode:
                    print(f"  ⚠️ {name} 파일 없음: {file_path}")
        
        if self.debug_mode:
            print(f"  ✅ {loaded_count}개 SFX 로드됨")
    
    def _setup_game_sound_mapping(self):
        """게임에서 사용할 수 있도록 사운드 매핑 통합"""
        # BGM과 SFX를 통합하여 하나의 sounds 딕셔너리로 관리
        self.sounds = {}
        self.sounds.update(self.bgm_tracks)
        self.sounds.update({name: sound for name, sound in self.sfx_sounds.items()})
        
        if self.debug_mode:
            print(f"🎵 총 {len(self.sounds)}개 사운드 준비 완료!")
            print(f"  📀 BGM: {len(self.bgm_tracks)}개")
            print(f"  🔊 SFX: {len(self.sfx_sounds)}개")
    
    def play_sound(self, sound_name: str, category: AudioCategory = AudioCategory.SFX, 
                   volume_override: Optional[float] = None, loop: int = 0):
        """사운드 재생"""
        if not self.enabled:
            return None
        
        try:
            if sound_name in self.sfx_sounds:
                # SFX 재생
                sound = self.sfx_sounds[sound_name]
                volume = volume_override or (self.master_volume * self.category_volumes[category])
                sound.set_volume(volume)
                return sound.play(loop)
            elif sound_name in self.bgm_tracks:
                # BGM은 별도 처리
                return self.play_bgm(sound_name)
            else:
                # 디버그 모드가 아닌 경우 사운드 오류 메시지 숨기기
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    print(f"⚠️ 사운드 없음: {sound_name}")
                return None
                
        except Exception as e:
            print(f"사운드 재생 실패 ({sound_name}): {e}")
            return None
    
    def play_sfx(self, sfx_name: str, volume: float = 1.0, fallback: str = None):
        """효과음 재생 (편의 메서드)"""
        if self.debug_mode:
            print(f"🎵 SFX 재생 요청: {sfx_name}")
        
        # 요청된 사운드가 없으면 fallback 사용
        if sfx_name not in self.sfx_sounds and fallback and fallback in self.sfx_sounds:
            if self.debug_mode:
                print(f"🎵 SFX fallback 사용: {sfx_name} -> {fallback}")
            sfx_name = fallback
        elif sfx_name not in self.sfx_sounds:
            if self.debug_mode:
                print(f"🎵 SFX 파일 없음: {sfx_name}")
            return False
            
        return self.play_sound(sfx_name, AudioCategory.SFX, volume)
    
    def play_bgm(self, bgm_name: str, fade_in: float = 1.0, loop: bool = True):
        """배경음악 재생"""
        if not self.enabled:
            return
        
        # 🔇 글리치 모드 체크 - FFVII sound system BGM 차단
        try:
            import __main__
            if hasattr(__main__, 'game'):
                game = __main__.game
                # 강제 글리치 모드 체크
                if hasattr(game, '_force_glitch_mode') and game._force_glitch_mode:
                    print("🔇 [FFVII SOUND BLOCKED] Force glitch mode - FFVII BGM denied")
                    return
                # 일반 글리치 모드 체크
                if hasattr(game, 'story_system') and game.story_system:
                    if hasattr(game.story_system, 'is_glitch_mode') and game.story_system.is_glitch_mode():
                        print("🔇 [FFVII SOUND BLOCKED] Glitch mode - FFVII BGM denied")
                        return
        except:
            pass
        
        # 같은 BGM이 이미 재생 중이면 계속 재생
        if self.current_bgm == bgm_name and pygame.mixer.music.get_busy():
            if self.debug_mode:
                print(f"🎵 BGM 이미 재생 중: {bgm_name}")
            return
        
        # 다른 BGM이 재생 중이면 부드러운 페이드아웃 후 전환
        if self.current_bgm and self.current_bgm != bgm_name:
            if self.debug_mode:
                print(f"🎵 BGM 변경: {self.current_bgm} → {bgm_name}")
            # 💀 직접 pygame 호출 주석처리 - 밤샌 고생 끝!
            # pygame.mixer.music.fadeout(300)  # 300ms 페이드아웃
            # pygame.time.wait(350)  # 페이드아웃 완료 대기
        
        if bgm_name in self.bgm_tracks:
            try:
                file_path = self.bgm_tracks[bgm_name]
                
                # 💀 직접 pygame 호출 완전 주석처리 - 밤샌 고생 끝!
                # pygame.mixer.music.load(file_path)
                
                volume = self.master_volume * self.category_volumes[AudioCategory.BGM]
                
                # 💀 직접 pygame 호출 주석처리 - 밤샌 고생 끝!
                # pygame.mixer.music.play(-1 if loop else 0)
                
                print(f"🔇 [FFVII BGM BLOCKED] '{bgm_name}' 호출 차단됨")
                
                # 부드러운 페이드인 효과
                if fade_in > 0:
                    pygame.mixer.music.set_volume(0.0)
                    # 점진적 볼륨 증가로 부드러운 시작
                    final_volume = volume
                    steps = 8  # 더 세밀한 페이드인
                    step_delay = max(30, int(fade_in * 1000 / steps))  # 더 부드러운 전환
                    
                    for i in range(steps + 1):
                        current_vol = (i / steps) * final_volume
                        pygame.mixer.music.set_volume(current_vol)
                        if i < steps:
                            pygame.time.wait(step_delay)
                else:
                    pygame.mixer.music.set_volume(volume)
                
                self.current_bgm = bgm_name
                if self.debug_mode:
                    print(f"🎵 BGM 재생: {bgm_name}")
                
            except Exception as e:
                if self.debug_mode:
                    print(f"BGM 재생 실패: {e}")
        else:
            if self.debug_mode:
                print(f"BGM 없음: {bgm_name}")
    
    def stop_bgm(self):
        """BGM 중지"""
        try:
            pygame.mixer.music.stop()
        except:
            pass
        self.current_bgm = None
    
    def fade_out_bgm(self, duration: float = 2.0):
        """BGM 페이드아웃"""
        try:
            pygame.mixer.music.fadeout(int(duration * 1000))
        except:
            self.stop_bgm()
        self.current_bgm = None
    
    def set_master_volume(self, volume: float):
        """마스터 볼륨 설정 (0.0 ~ 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        
        # 현재 재생중인 BGM 볼륨도 업데이트
        if self.current_bgm:
            bgm_volume = self.master_volume * self.category_volumes[AudioCategory.BGM]
            pygame.mixer.music.set_volume(bgm_volume)
    
    def set_category_volume(self, category: AudioCategory, volume: float):
        """카테고리별 볼륨 설정"""
        self.category_volumes[category] = max(0.0, min(1.0, volume))
    
    def set_volume(self, category: AudioCategory, volume: float):
        """볼륨 설정 (호환성을 위한 별칭)"""
        return self.set_category_volume(category, volume)
    
    def get_available_bgm(self):
        """사용 가능한 BGM 목록 반환"""
        return list(self.bgm_tracks.keys())
    
    def get_available_sfx(self):
        """사용 가능한 SFX 목록 반환"""
        return list(self.sfx_sounds.keys())
    
    def get_dungeon_bgm_by_floor(self, floor: int) -> str:
        """층수에 따른 던전 BGM 반환 (FFVII 테마 기반)"""
        if floor <= 3:
            # 초기층: 평화로운 탐험
            bgm_pool = ["peaceful", "safe_area", "town"]
        elif floor <= 7:
            # 중반층: 모험적인 탐험
            bgm_pool = ["dungeon", "cave", "mysterious"]
        elif floor <= 12:
            # 후반층: 긴장감 있는 탐험
            bgm_pool = ["dungeon_deep", "tension", "urgent"]
        elif floor <= 16:
            # 심층: 위험한 탐험
            bgm_pool = ["dramatic", "dungeon_deep", "tension"]
        else:
            # 최심층: 절망적인 탐험
            bgm_pool = ["dramatic", "sad", "tension"]
        
        # 층수 기반으로 일관된 BGM 선택
        import random
        random.seed(floor)  # 같은 층은 항상 같은 BGM
        selected_bgm = random.choice(bgm_pool)
        
        return selected_bgm
    
    def get_battle_bgm(self, is_boss: bool = False, boss_type: str = "normal") -> str:
        """전투 상황에 따른 BGM 반환"""
        if is_boss:
            if boss_type == "final":
                return "final_boss"
            elif boss_type == "major":
                return "epic_battle"
            elif boss_type == "mini":
                return "boss_battle"
            else:
                return "boss_theme"
        else:
            return "battle"
    
    def play_dungeon_bgm(self, floor: int, delay: float = 0.0):
        """던전 층수에 맞는 BGM 재생"""
        if delay > 0:
            # 지연 시간이 있으면 대기 후 재생
            pygame.time.wait(int(delay * 1000))
        bgm_name = self.get_dungeon_bgm_by_floor(floor)
        self.play_bgm(bgm_name, fade_in=2.0)  # 더 긴 페이드인으로 부드러운 시작
        
    def play_battle_bgm(self, is_boss: bool = False, boss_type: str = "normal"):
        """전투 상황에 맞는 BGM 재생"""
        bgm_name = self.get_battle_bgm(is_boss, boss_type)
        self.play_bgm(bgm_name, fade_in=0.8)  # 빠른 페이드인

# 전역 사운드 시스템 인스턴스
_ffvii_sound_system = None

def get_ffvii_sound_system():
    """FFVII 사운드 시스템 인스턴스 반환"""
    global _ffvii_sound_system
    if _ffvii_sound_system is None:
        _ffvii_sound_system = FFVIISoundSystem()
    return _ffvii_sound_system

# 편의 함수들
def play_bgm(name: str, **kwargs):
    """BGM 재생"""
    get_ffvii_sound_system().play_bgm(name, **kwargs)

def play_sfx(name: str, **kwargs):
    """SFX 재생"""
    get_ffvii_sound_system().play_sfx(name, **kwargs)

def stop_bgm():
    """BGM 중지"""
    get_ffvii_sound_system().stop_bgm()

if __name__ == "__main__":
    # 테스트
    sound_system = FFVIISoundSystem()
    print("FFVII 사운드 시스템 테스트 완료!")
