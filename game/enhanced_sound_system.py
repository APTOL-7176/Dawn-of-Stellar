#!/usr/bin/env python3
"""
강화된 사운드 시스템
BGM, SFX, 음성, 환경음을 포함한 종합 오디오 관리
"""

import pygame
import random
import threading
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple
from .chiptune_sfx import get_chiptune_sfx, play_chiptune_sound


class AudioCategory(Enum):
    """오디오 카테고리"""
    BGM = "bgm"           # 배경음악
    SFX = "sfx"           # 효과음
    AMBIENT = "ambient"   # 환경음
    VOICE = "voice"       # 음성
    UI = "ui"            # UI 사운드


class EnhancedSoundSystem:
    """강화된 사운드 시스템"""
    
    def __init__(self):
        self.enabled = True
        self.master_volume = 0.8
        self.category_volumes = {
            AudioCategory.BGM: 0.4,
            AudioCategory.SFX: 0.8,
            AudioCategory.AMBIENT: 0.3,
            AudioCategory.VOICE: 0.9,
            AudioCategory.UI: 0.7
        }
        
        self.sounds = {}
        self.current_bgm = None
        self.bgm_channel = None
        self.ambient_channel = None
        self.fade_thread = None
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.set_num_channels(16)  # 더 많은 채널
            self._initialize_sound_library()
            print("🎵 강화된 사운드 시스템 초기화 완료!")
        except Exception as e:
            print(f"⚠️ 사운드 시스템 초기화 실패: {e}")
            self.enabled = False
    
    def _initialize_sound_library(self):
        """사운드 라이브러리 초기화"""
        # 전투 사운드
        self.create_combat_sounds()
        
        # UI 사운드
        self.create_ui_sounds()
        
        # 환경 사운드
        self.create_ambient_sounds()
        
        # 스킬 & 마법 사운드
        self.create_magic_sounds()
        
        # 아이템 사운드
        self.create_item_sounds()
        
        # 🎵 BGM 생성
        self.create_bgm_tracks()
    
    def create_combat_sounds(self):
        """전투 사운드 생성"""
        combat_sounds = {
            'sword_swing': {'freq': [220, 440], 'duration': 0.2, 'wave': 'square'},
            'sword_hit': {'freq': [150, 300, 200], 'duration': 0.15, 'wave': 'saw'},
            'magic_cast': {'freq': [660, 880, 1100], 'duration': 0.5, 'wave': 'sine'},
            'critical_hit': {'freq': [880, 1100, 1320, 1760], 'duration': 0.3, 'wave': 'square'},
            'block': {'freq': [100, 150], 'duration': 0.1, 'wave': 'noise'},
            'dodge': {'freq': [440, 660], 'duration': 0.1, 'wave': 'triangle'},
            'enemy_hit': {'freq': [80, 120], 'duration': 0.2, 'wave': 'saw'},
            'boss_roar': {'freq': [60, 80, 100], 'duration': 1.0, 'wave': 'saw'},
            
            # 적 종류별 사운드
            'enemy_death_goblin': {'freq': [180, 150, 120], 'duration': 0.4, 'wave': 'saw'},
            'enemy_death_orc': {'freq': [120, 100, 80], 'duration': 0.5, 'wave': 'saw'},
            'enemy_death_skeleton': {'freq': [200, 150, 100, 80], 'duration': 0.6, 'wave': 'noise'},
            'enemy_death_dragon': {'freq': [60, 80, 100, 120], 'duration': 1.0, 'wave': 'saw'},
            
            # Brave 시스템 사운드
            'brave_attack': {'freq': [660, 880, 1100, 1320], 'duration': 0.4, 'wave': 'square'},
            'hp_attack': {'freq': [440, 550, 660], 'duration': 0.3, 'wave': 'triangle'},
            'break_sound': {'freq': [220, 180, 150, 120], 'duration': 0.5, 'wave': 'saw'}
        }
        
        for name, params in combat_sounds.items():
            self.sounds[name] = self._generate_chiptune_sound(**params)
    
    def create_ui_sounds(self):
        """UI 사운드 생성"""
        ui_sounds = {
            'menu_select': {'freq': [880], 'duration': 0.1, 'wave': 'sine'},
            'menu_navigate': {'freq': [660], 'duration': 0.08, 'wave': 'triangle'},
            'menu_confirm': {'freq': [660, 880], 'duration': 0.2, 'wave': 'triangle'},
            'menu_cancel': {'freq': [440, 330], 'duration': 0.15, 'wave': 'square'},
            'menu_error': {'freq': [220, 200, 180], 'duration': 0.3, 'wave': 'saw'},
            'page_turn': {'freq': [1100, 1320], 'duration': 0.08, 'wave': 'triangle'},
            'inventory_open': {'freq': [880, 1100, 1320], 'duration': 0.3, 'wave': 'sine'},
            'shop_bell': {'freq': [1760, 1980, 2200], 'duration': 0.4, 'wave': 'sine'},
            'game_start': {'freq': [440, 550, 660, 880], 'duration': 0.8, 'wave': 'sine'},
            'game_over': {'freq': [220, 180, 150, 120], 'duration': 1.5, 'wave': 'saw'},
            'victory': {'freq': [880, 1100, 1320, 1540, 1760], 'duration': 1.2, 'wave': 'sine'},
            'defeat': {'freq': [330, 220, 150, 100], 'duration': 1.0, 'wave': 'saw'}
        }
        
        for name, params in ui_sounds.items():
            self.sounds[name] = self._generate_chiptune_sound(**params)
    
    def create_ambient_sounds(self):
        """환경 사운드 생성"""
        ambient_sounds = {
            'dungeon_drip': {'freq': [880, 660], 'duration': 0.2, 'wave': 'sine'},
            'wind_howl': {'freq': [150, 200, 180], 'duration': 2.0, 'wave': 'noise'},
            'footsteps': {'freq': [100, 120], 'duration': 0.1, 'wave': 'noise'},
            'door_creak': {'freq': [80, 90, 100], 'duration': 0.8, 'wave': 'saw'},
            'chest_open': {'freq': [440, 880, 1320], 'duration': 0.5, 'wave': 'triangle'},
            'treasure_sparkle': {'freq': [1760, 2200, 2640], 'duration': 0.3, 'wave': 'sine'},
            'treasure_open': {'freq': [660, 880, 1100, 1320], 'duration': 0.6, 'wave': 'triangle'},
            'secret_found': {'freq': [1320, 1540, 1760, 1980], 'duration': 0.8, 'wave': 'sine'},
            'battle_start': {'freq': [220, 330, 440], 'duration': 0.5, 'wave': 'square'},
            'normal_hit': {'freq': [440, 330], 'duration': 0.1, 'wave': 'square'},
            'enemy_death': {'freq': [220, 180, 150], 'duration': 0.4, 'wave': 'saw'}
        }
        
        for name, params in ambient_sounds.items():
            self.sounds[name] = self._generate_chiptune_sound(**params)
    
    def create_magic_sounds(self):
        """마법 & 스킬 사운드 생성"""
        magic_sounds = {
            'heal_spell': {'freq': [660, 880, 1100, 1320], 'duration': 0.8, 'wave': 'sine'},
            'fire_spell': {'freq': [220, 440, 330, 550], 'duration': 0.6, 'wave': 'saw'},
            'ice_spell': {'freq': [1100, 880, 660, 440], 'duration': 0.7, 'wave': 'triangle'},
            'lightning_spell': {'freq': [1760, 1320, 1980, 1540], 'duration': 0.4, 'wave': 'square'},
            'buff_cast': {'freq': [880, 1100, 1320, 1540], 'duration': 0.6, 'wave': 'sine'},
            'debuff_cast': {'freq': [330, 220, 180, 150], 'duration': 0.6, 'wave': 'saw'},
            'teleport': {'freq': [2200, 1760, 1320, 880], 'duration': 0.5, 'wave': 'sine'}
        }
        
        for name, params in magic_sounds.items():
            self.sounds[name] = self._generate_chiptune_sound(**params)
    
    def create_item_sounds(self):
        """아이템 사운드 생성"""
        item_sounds = {
            'item_pickup': {'freq': [880, 1100], 'duration': 0.2, 'wave': 'triangle'},
            'gold_pickup': {'freq': [1320, 1540, 1760], 'duration': 0.3, 'wave': 'sine'},
            'potion_drink': {'freq': [440, 550, 660], 'duration': 0.4, 'wave': 'triangle'},
            'equip_weapon': {'freq': [330, 440], 'duration': 0.3, 'wave': 'square'},
            'equip_armor': {'freq': [220, 330], 'duration': 0.4, 'wave': 'saw'},
            'level_up': {'freq': [660, 880, 1100, 1320, 1540], 'duration': 1.0, 'wave': 'sine'},
            'quest_complete': {'freq': [880, 1100, 1320, 1540, 1760], 'duration': 1.2, 'wave': 'triangle'},
            'heal': {'freq': [880, 1100, 1320], 'duration': 0.6, 'wave': 'sine'},
            'magic_cast': {'freq': [1100, 1320, 1540], 'duration': 0.5, 'wave': 'triangle'},
            'weapon_break': {'freq': [220, 180, 150], 'duration': 0.6, 'wave': 'saw'},
            'armor_break': {'freq': [200, 160, 120], 'duration': 0.7, 'wave': 'saw'}
        }
        
        for name, params in item_sounds.items():
            self.sounds[name] = self._generate_chiptune_sound(**params)
    
    def create_bgm_tracks(self):
        """BGM 트랙 생성 - 각 상황별 배경음악"""
        print("🎵 BGM 트랙 생성 중...")
        
        # 각 BGM은 여러 음표로 구성된 멜로디
        bgm_tracks = {
            'town_bgm': {
                'melody': [
                    (523, 0.5), (659, 0.5), (784, 0.5), (659, 0.5),  # C5-E5-G5-E5
                    (523, 0.5), (440, 0.5), (523, 1.0),              # C5-A4-C5
                    (440, 0.5), (523, 0.5), (659, 0.5), (523, 0.5),  # A4-C5-E5-C5
                    (440, 1.0), (392, 1.0)                           # A4-G4
                ],
                'tempo': 120,
                'wave': 'sine'
            },
            
            'dungeon_bgm': {
                'melody': [
                    (330, 0.8), (294, 0.4), (330, 0.4), (370, 0.4),  # E4-D4-E4-F#4
                    (330, 0.8), (294, 0.8),                          # E4-D4
                    (262, 0.8), (294, 0.4), (330, 0.4), (294, 0.4),  # C4-D4-E4-D4
                    (262, 1.2), (247, 0.8)                           # C4-B3
                ],
                'tempo': 80,
                'wave': 'triangle'
            },
            
            'battle_bgm': {
                'melody': [
                    (440, 0.25), (494, 0.25), (523, 0.25), (587, 0.25),  # A4-B4-C5-D5
                    (659, 0.5), (587, 0.25), (523, 0.25),                # E5-D5-C5
                    (494, 0.25), (523, 0.25), (494, 0.25), (440, 0.25),  # B4-C5-B4-A4
                    (392, 0.5), (440, 0.5)                               # G4-A4
                ],
                'tempo': 140,
                'wave': 'square'
            },
            
            'victory_bgm': {
                'melody': [
                    (523, 0.3), (659, 0.3), (784, 0.3), (1047, 0.6),    # C5-E5-G5-C6
                    (880, 0.3), (784, 0.3), (659, 0.3), (523, 0.6),     # A5-G5-E5-C5
                    (659, 0.3), (784, 0.3), (880, 0.3), (1047, 0.9)     # E5-G5-A5-C6
                ],
                'tempo': 150,
                'wave': 'sine'
            },
            
            'boss_bgm': {
                'melody': [
                    (208, 0.5), (233, 0.25), (208, 0.25), (185, 0.5),   # G#3-A#3-G#3-F#3
                    (175, 0.5), (196, 0.5),                             # F3-G3
                    (208, 0.5), (233, 0.25), (262, 0.25), (294, 0.5),   # G#3-A#3-C4-D4
                    (330, 0.75), (294, 0.25), (262, 0.5)                # E4-D4-C4
                ],
                'tempo': 100,
                'wave': 'saw'
            }
        }
        
        for name, track_data in bgm_tracks.items():
            self.sounds[name] = self._generate_bgm_track(**track_data)
    
    def _generate_bgm_track(self, melody: List[Tuple[int, float]], tempo: int, wave: str = 'sine'):
        """멜로디로 BGM 트랙 생성"""
        try:
            import numpy as np
            sample_rate = 22050
            beat_duration = 60.0 / tempo  # BPM을 초당 비트로 변환
            
            # 전체 트랙 길이 계산
            total_duration = sum(note[1] * beat_duration for note in melody)
            total_samples = int(sample_rate * total_duration)
            
            # BGM 데이터 생성
            bgm_data = np.zeros(total_samples)
            current_sample = 0
            
            for freq, duration in melody:
                note_duration = duration * beat_duration
                note_samples = int(sample_rate * note_duration)
                
                if current_sample + note_samples > total_samples:
                    note_samples = total_samples - current_sample
                
                t = np.linspace(0, note_duration, note_samples)
                
                # 파형 생성
                if wave == 'sine':
                    note_wave = np.sin(2 * np.pi * freq * t)
                elif wave == 'triangle':
                    note_wave = 2 * np.arcsin(np.sin(2 * np.pi * freq * t)) / np.pi
                elif wave == 'square':
                    note_wave = np.sign(np.sin(2 * np.pi * freq * t))
                elif wave == 'saw':
                    note_wave = 2 * (freq * t - np.floor(freq * t + 0.5))
                
                # 엔벨로프 적용 (ADSR - 간단한 버전)
                attack_samples = min(int(0.05 * sample_rate), note_samples // 4)
                release_samples = min(int(0.1 * sample_rate), note_samples // 4)
                
                envelope = np.ones(note_samples)
                # Attack
                if attack_samples > 0:
                    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
                # Release
                if release_samples > 0:
                    envelope[-release_samples:] = np.linspace(1, 0, release_samples)
                
                note_wave *= envelope * 0.3  # 볼륨 조절
                
                # BGM에 추가
                end_sample = min(current_sample + note_samples, total_samples)
                bgm_data[current_sample:end_sample] = note_wave[:end_sample - current_sample]
                current_sample += note_samples
                
                if current_sample >= total_samples:
                    break
            
            # 스테레오로 변환
            stereo_data = np.column_stack((bgm_data, bgm_data))
            audio_data = (stereo_data * 32767).astype(np.int16)
            
            return pygame.sndarray.make_sound(audio_data)
            
        except Exception as e:
            print(f"BGM 생성 실패: {e}")
            # 폴백: 간단한 톤 생성
            return self._generate_chiptune_sound([440], 2.0, 'sine')
    
    def _generate_chiptune_sound(self, freq: List[int], duration: float, wave: str = 'sine'):
        """칩튠 사운드 생성"""
        try:
            return get_chiptune_sfx(freq, duration, wave)
        except:
            # 폴백: 간단한 사인파 생성
            import numpy as np
            sample_rate = 22050
            samples = int(sample_rate * duration)
            
            if isinstance(freq, list):
                # 주파수 변화가 있는 경우
                wave_data = np.zeros(samples)
                chunk_size = samples // len(freq)
                
                for i, f in enumerate(freq):
                    start = i * chunk_size
                    end = min((i + 1) * chunk_size, samples)
                    t = np.linspace(0, duration * (end - start) / samples, end - start)
                    
                    if wave == 'sine':
                        chunk = np.sin(2 * np.pi * f * t)
                    elif wave == 'square':
                        chunk = np.sign(np.sin(2 * np.pi * f * t))
                    elif wave == 'triangle':
                        chunk = 2 * np.arcsin(np.sin(2 * np.pi * f * t)) / np.pi
                    elif wave == 'saw':
                        chunk = 2 * (f * t - np.floor(f * t + 0.5))
                    else:  # noise
                        chunk = np.random.uniform(-1, 1, len(t))
                    
                    wave_data[start:end] = chunk
            else:
                # 단일 주파수
                t = np.linspace(0, duration, samples)
                if wave == 'sine':
                    wave_data = np.sin(2 * np.pi * freq * t)
                elif wave == 'square':
                    wave_data = np.sign(np.sin(2 * np.pi * freq * t))
                elif wave == 'triangle':
                    wave_data = 2 * np.arcsin(np.sin(2 * np.pi * freq * t)) / np.pi
                elif wave == 'saw':
                    wave_data = 2 * (freq * t - np.floor(freq * t + 0.5))
                else:  # noise
                    wave_data = np.random.uniform(-1, 1, samples)
            
            # 볼륨 조절 및 페이드
            envelope = np.ones_like(wave_data)
            fade_samples = min(samples // 10, sample_rate // 20)  # 페이드 시간
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            
            wave_data *= envelope * 0.3  # 볼륨 조절
            
            # 스테레오로 변환
            stereo_data = np.column_stack((wave_data, wave_data))
            audio_data = (stereo_data * 32767).astype(np.int16)
            
            return pygame.sndarray.make_sound(audio_data)
    
    def play_sound(self, sound_name: str, category: AudioCategory = AudioCategory.SFX, 
                   volume_override: Optional[float] = None, loop: int = 0):
        """사운드 재생"""
        if not self.enabled or sound_name not in self.sounds:
            return None
        
        try:
            sound = self.sounds[sound_name]
            volume = volume_override or (self.master_volume * self.category_volumes[category])
            sound.set_volume(volume)
            
            return sound.play(loop)
        except Exception as e:
            print(f"사운드 재생 실패 ({sound_name}): {e}")
            return None
    
    def play_sfx(self, sfx_name: str, volume: float = 1.0):
        """효과음 재생 (편의 메서드)"""
        return self.play_sound(sfx_name, AudioCategory.SFX, volume)
    
    def play_bgm(self, bgm_name: str, fade_in: float = 2.0, loop: bool = True):
        """배경음악 재생"""
        if not self.enabled:
            return
        
        # 기존 BGM 페이드아웃
        if self.current_bgm and self.bgm_channel:
            self.fade_out_bgm(1.0)
        
        # BGM 파일명 매핑
        bgm_map = {
            'town': 'town_bgm',
            'dungeon': 'dungeon_bgm', 
            'battle': 'battle_bgm',
            'victory': 'victory_bgm',
            'boss': 'boss_bgm'
        }
        
        actual_bgm_name = bgm_map.get(bgm_name, bgm_name)
        
        # 새 BGM 시작
        if actual_bgm_name in self.sounds:
            try:
                volume = self.master_volume * self.category_volumes[AudioCategory.BGM]
                sound = self.sounds[actual_bgm_name]
                sound.set_volume(volume)
                
                # 무한 루프로 재생
                self.bgm_channel = sound.play(-1 if loop else 0)
                self.current_bgm = actual_bgm_name
                
                print(f"🎵 BGM 재생: {bgm_name} ({actual_bgm_name})")
                
            except Exception as e:
                print(f"BGM 재생 실패: {e}")
                # 폴백: 앰비언트 사운드 사용
                self.play_ambient_loop(bgm_name)
        else:
            print(f"BGM 없음: {actual_bgm_name}, 앰비언트로 대체")
            self.play_ambient_loop(bgm_name)
    
    def fade_out_bgm(self, duration: float = 2.0):
        """BGM 페이드아웃"""
        if self.bgm_channel and self.bgm_channel.get_busy():
            try:
                pygame.mixer.fadeout(int(duration * 1000))
            except:
                self.bgm_channel.stop()
        self.current_bgm = None
        self.bgm_channel = None
    
    def stop_bgm(self):
        """BGM 중지"""
        if self.bgm_channel:
            self.bgm_channel.stop()
        self.current_bgm = None
        self.bgm_channel = None
    
    def play_ambient_loop(self, ambient_type: str):
        """환경음 루프 재생"""
        ambient_map = {
            'dungeon': 'dungeon_drip',
            'battle': 'wind_howl',
            'town': 'footsteps',
            'victory': 'treasure_sparkle'
        }
        
        if ambient_type in ambient_map:
            sound_name = ambient_map[ambient_type]
            self.ambient_channel = self.play_sound(sound_name, AudioCategory.AMBIENT, loop=-1)
    
    def fade_out_bgm(self, fade_time: float = 2.0):
        """BGM 페이드아웃"""
        if self.bgm_channel:
            try:
                # pygame.mixer.fadeout는 모든 채널에 영향을 주므로 수동으로 처리
                self.bgm_channel.fadeout(int(fade_time * 1000))
            except:
                pass
    
    def stop_bgm(self):
        """BGM 정지"""
        if self.bgm_channel:
            try:
                self.bgm_channel.stop()
                self.bgm_channel = None
                self.current_bgm = None
            except:
                pass
    
    def set_volume(self, category: AudioCategory, volume: float):
        """카테고리별 볼륨 설정"""
        self.category_volumes[category] = max(0.0, min(1.0, volume))
    
    def set_master_volume(self, volume: float):
        """마스터 볼륨 설정"""
        self.master_volume = max(0.0, min(1.0, volume))
    
    def toggle_sound(self):
        """사운드 on/off 토글"""
        self.enabled = not self.enabled
        if not self.enabled and self.ambient_channel:
            self.ambient_channel.stop()
    
    def play_random_combat_sound(self):
        """랜덤 전투 사운드 재생"""
        combat_sounds = ['sword_swing', 'sword_hit', 'magic_cast', 'critical_hit']
        sound = random.choice(combat_sounds)
        self.play_sound(sound, AudioCategory.SFX)
    
    def play_ui_feedback(self, action: str):
        """UI 피드백 사운드"""
        ui_map = {
            'select': 'menu_select',
            'confirm': 'menu_confirm', 
            'cancel': 'menu_cancel',
            'error': 'menu_error',
            'page': 'page_turn',
            'inventory': 'inventory_open',
            'shop': 'shop_bell'
        }
        
        if action in ui_map:
            self.play_sound(ui_map[action], AudioCategory.UI)


# 전역 강화 사운드 시스템 인스턴스
enhanced_audio = EnhancedSoundSystem()


def play_enhanced_sfx(sound_name: str, category: str = 'sfx'):
    """간편한 사운드 재생 함수"""
    cat_map = {
        'sfx': AudioCategory.SFX,
        'ui': AudioCategory.UI,
        'ambient': AudioCategory.AMBIENT,
        'voice': AudioCategory.VOICE,
        'bgm': AudioCategory.BGM
    }
    
    category_enum = cat_map.get(category, AudioCategory.SFX)
    enhanced_audio.play_sound(sound_name, category_enum)


def play_combat_sequence(action_type: str):
    """전투 액션에 따른 사운드 시퀀스"""
    sequences = {
        'attack': ['sword_swing', 'sword_hit'],
        'magic': ['magic_cast', 'fire_spell'],
        'critical': ['sword_swing', 'critical_hit'],
        'defend': ['block'],
        'dodge': ['dodge'],
        'heal': ['heal_spell']
    }
    
    if action_type in sequences:
        for i, sound in enumerate(sequences[action_type]):
            threading.Timer(i * 0.2, lambda s=sound: enhanced_audio.play_sound(s)).start()
