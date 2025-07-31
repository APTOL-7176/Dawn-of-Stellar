"""
칩튠 스타일 사운드 생성기
pygame을 사용하여 실시간으로 8bit 스타일 사운드 생성
"""

import pygame
import numpy as np
import threading
import time
from typing import Dict, Optional
from enum import Enum


class ChiptuneGenerator:
    """칩튠 스타일 사운드 생성기"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        # 스테레오로 초기화하고 볼륨 증가
        pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
    def generate_tone(self, frequency: float, duration: float, 
                     wave_type: str = "square", volume: float = 0.5) -> np.ndarray:
        """기본 톤 생성 (스테레오)"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))  # 스테레오 배열
        
        for i in range(frames):
            time_point = float(i) / self.sample_rate
            
            if wave_type == "square":
                # 사각파 (8bit 게임 특유의 소리)
                sample = volume if np.sin(2 * np.pi * frequency * time_point) >= 0 else -volume
            elif wave_type == "triangle":
                # 삼각파
                sample = volume * (2 * np.arcsin(np.sin(2 * np.pi * frequency * time_point)) / np.pi)
            elif wave_type == "sawtooth":
                # 톱니파
                sample = volume * (2 * (frequency * time_point - np.floor(frequency * time_point + 0.5)))
            elif wave_type == "noise":
                # 노이즈 (타격음 등에 사용)
                sample = volume * (np.random.random() * 2 - 1)
            else:
                sample = 0
                
            arr[i] = [sample, sample]  # 좌우 채널 동일
                
        return arr
        
    def generate_chord(self, frequencies: list, duration: float, 
                      wave_type: str = "square", volume: float = 0.2) -> np.ndarray:
        """화음 생성"""
        result = np.zeros(int(duration * self.sample_rate))
        for freq in frequencies:
            tone = self.generate_tone(freq, duration, wave_type, volume / len(frequencies))
            result += tone
        return result
        
    def apply_envelope(self, wave: np.ndarray, attack: float = 0.01, 
                      decay: float = 0.1, sustain: float = 0.7, 
                      release: float = 0.2) -> np.ndarray:
        """ADSR 엔벨로프 적용"""
        frames = len(wave)
        envelope = np.ones(frames)
        
        # Attack
        attack_frames = int(attack * self.sample_rate)
        if attack_frames > 0:
            envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
            
        # Decay
        decay_frames = int(decay * self.sample_rate)
        if decay_frames > 0 and attack_frames + decay_frames < frames:
            envelope[attack_frames:attack_frames + decay_frames] = np.linspace(1, sustain, decay_frames)
            
        # Sustain
        sustain_start = attack_frames + decay_frames
        sustain_end = frames - int(release * self.sample_rate)
        if sustain_start < sustain_end:
            envelope[sustain_start:sustain_end] = sustain
            
        # Release
        release_frames = int(release * self.sample_rate)
        if release_frames > 0:
            envelope[-release_frames:] = np.linspace(sustain, 0, release_frames)
            
        return wave * envelope


class ChiptuneSFX:
    """칩튠 효과음 라이브러리"""
    
    def __init__(self):
        self.generator = ChiptuneGenerator()
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}
        
    def _array_to_sound(self, arr: np.ndarray) -> pygame.mixer.Sound:
        """numpy 배열을 pygame Sound 객체로 변환"""
        # 16bit 정수로 변환
        sound_array = (arr * 32767).astype(np.int16)
        return pygame.mixer.Sound(sound_array)
        
    def create_brave_attack_sound(self) -> pygame.mixer.Sound:
        """Brave 공격 효과음"""
        # 상승하는 톤으로 Brave 획득 느낌
        duration = 0.3
        frames = int(duration * self.generator.sample_rate)
        wave = np.zeros(frames)
        
        # 주파수가 상승하는 효과
        for i in range(frames):
            t = i / self.generator.sample_rate
            freq = 440 + (220 * t)  # 440Hz에서 660Hz로 상승
            wave[i] = 0.3 * (1 if np.sin(2 * np.pi * freq * t) >= 0 else -1)
            
        wave = self.generator.apply_envelope(wave, 0.01, 0.05, 0.8, 0.24)
        return self._array_to_sound(wave)
        
    def create_hp_attack_sound(self) -> pygame.mixer.Sound:
        """HP 공격 효과음"""
        # 강력한 임팩트 사운드
        duration = 0.4
        
        # 저음 임팩트 + 노이즈
        impact = self.generator.generate_tone(80, 0.1, "square", 0.5)
        noise = self.generator.generate_tone(0, 0.15, "noise", 0.3)
        
        # 상승하는 하이톤
        high_tone = self.generator.generate_tone(880, 0.25, "triangle", 0.2)
        
        # 결합
        wave = np.concatenate([impact, noise + high_tone[:len(noise)]])
        if len(wave) < duration * self.generator.sample_rate:
            padding = int(duration * self.generator.sample_rate) - len(wave)
            wave = np.concatenate([wave, np.zeros(padding)])
            
        return self._array_to_sound(wave)
        
    def create_break_sound(self) -> pygame.mixer.Sound:
        """Break 효과음"""
        # 깨지는 소리 (하강하는 노이즈)
        duration = 0.6
        frames = int(duration * self.generator.sample_rate)
        wave = np.zeros(frames)
        
        for i in range(frames):
            t = i / self.generator.sample_rate
            # 하강하는 주파수
            freq = 800 * (1 - t)
            noise_intensity = 0.4 * (1 - t)
            
            # 사각파 + 노이즈
            square = 1 if np.sin(2 * np.pi * freq * t) >= 0 else -1
            noise = np.random.random() * 2 - 1
            
            wave[i] = square * 0.3 + noise * noise_intensity
            
        return self._array_to_sound(wave)
        
    def create_critical_sound(self) -> pygame.mixer.Sound:
        """크리티컬 히트 효과음"""
        # 화려한 상승음
        duration = 0.5
        
        # 빠른 아르페지오 효과
        notes = [523, 659, 784, 1047]  # C, E, G, C (한 옥타브 위)
        wave = np.zeros(int(duration * self.generator.sample_rate))
        
        note_duration = duration / len(notes)
        for i, freq in enumerate(notes):
            start_frame = int(i * note_duration * self.generator.sample_rate)
            end_frame = int((i + 1) * note_duration * self.generator.sample_rate)
            
            note_wave = self.generator.generate_tone(freq, note_duration, "triangle", 0.4)
            note_wave = self.generator.apply_envelope(note_wave, 0.01, 0.02, 0.9, 0.07)
            
            wave[start_frame:start_frame + len(note_wave)] += note_wave
            
        return self._array_to_sound(wave)
        
    def create_heal_sound(self) -> pygame.mixer.Sound:
        """회복 효과음"""
        # 따뜻한 화음
        frequencies = [261, 329, 392]  # C, E, G 메이저 코드
        duration = 0.4
        
        wave = self.generator.generate_chord(frequencies, duration, "triangle", 0.3)
        wave = self.generator.apply_envelope(wave, 0.05, 0.1, 0.8, 0.25)
        
        return self._array_to_sound(wave)
        
    def create_menu_sound(self) -> pygame.mixer.Sound:
        """메뉴 선택 효과음"""
        # 짧은 블립 사운드
        wave = self.generator.generate_tone(800, 0.1, "square", 0.2)
        wave = self.generator.apply_envelope(wave, 0.01, 0.02, 0.7, 0.07)
        
        return self._array_to_sound(wave)
        
    def create_level_up_sound(self) -> pygame.mixer.Sound:
        """레벨업 효과음"""
        # 승리의 팬파르
        notes = [523, 659, 784, 1047, 1319]  # C, E, G, C, E (상승)
        duration = 1.0
        
        wave = np.zeros(int(duration * self.generator.sample_rate))
        note_duration = 0.15
        
        for i, freq in enumerate(notes):
            start_frame = int(i * note_duration * self.generator.sample_rate)
            note_wave = self.generator.generate_tone(freq, note_duration, "triangle", 0.3)
            note_wave = self.generator.apply_envelope(note_wave, 0.01, 0.03, 0.8, 0.11)
            
            end_frame = start_frame + len(note_wave)
            if end_frame <= len(wave):
                wave[start_frame:end_frame] += note_wave
                
        return self._array_to_sound(wave)
        
    def get_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        """사운드 캐시에서 가져오거나 생성"""
        if sound_name not in self.sound_cache:
            if sound_name == "brave_attack":
                self.sound_cache[sound_name] = self.create_brave_attack_sound()
            elif sound_name == "hp_attack":
                self.sound_cache[sound_name] = self.create_hp_attack_sound()
            elif sound_name == "break":
                self.sound_cache[sound_name] = self.create_break_sound()
            elif sound_name == "critical":
                self.sound_cache[sound_name] = self.create_critical_sound()
            elif sound_name == "heal":
                self.sound_cache[sound_name] = self.create_heal_sound()
            elif sound_name == "menu":
                self.sound_cache[sound_name] = self.create_menu_sound()
            elif sound_name == "level_up":
                self.sound_cache[sound_name] = self.create_level_up_sound()
            else:
                return None
                
        return self.sound_cache[sound_name]
        
    def play_sound(self, sound_name: str, volume: float = 1.0):
        """사운드 재생"""
        sound = self.get_sound(sound_name)
        if sound:
            sound.set_volume(volume)
            sound.play()


# 전역 칩튠 사운드 매니저
_chiptune_sfx = None

def get_chiptune_sfx() -> ChiptuneSFX:
    """전역 칩튠 사운드 매니저 반환"""
    global _chiptune_sfx
    if _chiptune_sfx is None:
        try:
            _chiptune_sfx = ChiptuneSFX()
        except Exception as e:
            print(f"칩튠 사운드 시스템 초기화 실패: {e}")
            _chiptune_sfx = None
    return _chiptune_sfx

def play_chiptune_sound(sound_name: str, volume: float = 0.7):
    """칩튠 사운드 재생"""
    sfx = get_chiptune_sfx()
    if sfx:
        try:
            sfx.play_sound(sound_name, volume)
        except Exception as e:
            print(f"사운드 재생 실패 ({sound_name}): {e}")
    else:
        # 폴백: 텍스트 표시
        print(f"♪ {sound_name} 사운드")
