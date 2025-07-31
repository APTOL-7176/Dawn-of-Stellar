#!/usr/bin/env python3
"""
Fallback SFX 시스템 - 실제 사운드 파일이 없을 때 사용
"""

import pygame
import random
import math
import time

class FallbackSFXGenerator:
    """프로그래밍으로 생성하는 간단한 SFX"""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        
    def generate_tone(self, frequency, duration, amplitude=0.3, wave_type='sine'):
        """기본 톤 생성"""
        frames = int(duration * self.sample_rate)
        arr = []
        
        for i in range(frames):
            time_val = float(i) / self.sample_rate
            
            if wave_type == 'sine':
                wave = math.sin(frequency * 2 * math.pi * time_val)
            elif wave_type == 'square':
                wave = 1 if math.sin(frequency * 2 * math.pi * time_val) > 0 else -1
            elif wave_type == 'saw':
                wave = 2 * (time_val * frequency - math.floor(time_val * frequency + 0.5))
            else:
                wave = random.uniform(-1, 1)  # noise
                
            # 페이드 아웃
            fade = 1.0 if i < frames * 0.8 else (frames - i) / (frames * 0.2)
            arr.append(int(wave * amplitude * fade * 32767))
            
        return arr
    
    def generate_fire_sound(self):
        """화염 사운드"""
        return self.generate_tone(150, 0.5, 0.2, 'noise')
    
    def generate_ice_sound(self):
        """얼음 사운드"""
        return self.generate_tone(800, 0.3, 0.3, 'sine')
    
    def generate_thunder_sound(self):
        """번개 사운드"""
        return self.generate_tone(100, 0.8, 0.4, 'noise')
    
    def generate_sword_sound(self):
        """검 사운드"""
        return self.generate_tone(600, 0.2, 0.3, 'saw')
    
    def generate_magic_sound(self):
        """마법 사운드"""
        return self.generate_tone(400, 0.4, 0.2, 'sine')
    
    def generate_heal_sound(self):
        """치유 사운드"""
        return self.generate_tone(800, 0.6, 0.25, 'sine')
    
    def play_generated_sound(self, sound_data):
        """생성된 사운드 재생"""
        try:
            # 스테레오로 변환
            stereo_data = []
            for sample in sound_data:
                stereo_data.extend([sample, sample])
            
            # pygame sound 객체 생성
            sound_array = pygame.sndarray.make_sound(pygame.array.array('h', stereo_data))
            sound_array.play()
            return True
        except Exception as e:
            print(f"생성된 사운드 재생 실패: {e}")
            return False

class EnhancedSFXSystem:
    """향상된 SFX 시스템 (fallback 포함)"""
    
    def __init__(self, original_system):
        self.original_system = original_system
        self.fallback_generator = FallbackSFXGenerator()
        
        # SFX 매핑
        self.sfx_mapping = {
            'fire_whoosh': 'fire',
            'fire_explosion': 'fire',
            'flame_burst': 'fire',
            'ice_shatter': 'ice',
            'freeze_blast': 'ice',
            'absolute_zero': 'ice',
            'thunder_crack': 'thunder',
            'lightning_bolt': 'thunder',
            'chain_lightning': 'thunder',
            'sword_clash': 'sword',
            'blade_strike': 'sword',
            'heavy_impact': 'sword',
            'magic_generic': 'magic',
            'spell_cast': 'magic',
            'arcane_blast': 'magic',
            'heal_spell': 'heal',
            'holy_light': 'heal',
            'divine_blessing': 'heal',
            'explosion': 'fire',
            'wind_cutting': 'magic',
            'earth_rumble': 'thunder',
            'poison_splash': 'magic'
        }
    
    def play_sfx(self, sfx_name, volume=1.0):
        """SFX 재생 (fallback 포함)"""
        # 먼저 원래 시스템에서 시도
        if self.original_system.play_sfx(sfx_name, volume):
            return True
        
        # fallback 사운드 생성 및 재생
        sound_type = self.sfx_mapping.get(sfx_name, 'magic')
        
        try:
            if sound_type == 'fire':
                sound_data = self.fallback_generator.generate_fire_sound()
            elif sound_type == 'ice':
                sound_data = self.fallback_generator.generate_ice_sound()
            elif sound_type == 'thunder':
                sound_data = self.fallback_generator.generate_thunder_sound()
            elif sound_type == 'sword':
                sound_data = self.fallback_generator.generate_sword_sound()
            elif sound_type == 'heal':
                sound_data = self.fallback_generator.generate_heal_sound()
            else:  # magic
                sound_data = self.fallback_generator.generate_magic_sound()
            
            return self.fallback_generator.play_generated_sound(sound_data)
        except Exception as e:
            if self.original_system.debug_mode:
                print(f"🎵 Fallback SFX 생성 실패: {sfx_name} - {e}")
            return False

def test_enhanced_sfx():
    """향상된 SFX 시스템 테스트"""
    print("=== 🎵 향상된 SFX 시스템 테스트 ===")
    
    # 기존 시스템 초기화
    from game.ffvii_sound_system import FFVIISoundSystem
    original_system = FFVIISoundSystem(debug_mode=True)
    
    # 향상된 시스템 초기화
    enhanced_system = EnhancedSFXSystem(original_system)
    
    # 테스트할 SFX 목록
    test_sfx = [
        "fire_whoosh",
        "ice_shatter", 
        "thunder_crack",
        "sword_clash",
        "magic_generic",
        "heal_spell",
        "explosion",
        "wind_cutting"
    ]
    
    print("🎮 향상된 SFX 테스트 시작...")
    
    for sfx_name in test_sfx:
        print(f"\n🔊 테스트 중: {sfx_name}")
        result = enhanced_system.play_sfx(sfx_name)
        print(f"   결과: {'성공' if result else '실패'}")
        time.sleep(0.8)  # 0.8초 대기
    
    print("\n✅ 향상된 SFX 테스트 완료!")
    print("💡 실제 사운드 파일이 없어도 프로그래밍으로 생성된 사운드가 재생됩니다!")

if __name__ == "__main__":
    test_enhanced_sfx()
