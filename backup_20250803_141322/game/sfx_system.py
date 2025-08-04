"""
간단한 SFX 시스템 - 요리용
"""

import pygame
import os

class SFXSystem:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init()
            self.sounds = {}
            self._load_cooking_sounds()
        except Exception as e:
            print(f"SFX 시스템 초기화 실패: {e}")
            self.enabled = False
    
    def _load_cooking_sounds(self):
        """요리 관련 사운드 로드 - FFVII 스타일"""
        sound_files = {
            'cooking_success': 'sounds/sfx/ff7_item_get.wav',  # 아이템 획득 사운드
            'cooking_failure': 'sounds/sfx/ff7_error.wav',     # 에러 사운드
            'cooking_start': 'sounds/sfx/ff7_menu_select.wav', # 메뉴 선택 사운드
            'ingredient_chop': 'sounds/sfx/ff7_sword_hit1.wav', # 검격 사운드 (재료 자르기)
            'sizzle': 'sounds/sfx/ff7_fire_magic.wav',         # 파이어 마법 (지글지글)
            'boiling': 'sounds/sfx/ff7_water_magic.wav',       # 워터 마법 (끓는 소리)
            'recipe_discovered': 'sounds/sfx/ff7_fanfare.wav', # 팡파레 (새 레시피 발견)
            'level_up': 'sounds/sfx/ff7_level_up.wav',         # 레벨업 (요리 레벨업)
            'quick_cook': 'sounds/sfx/ff7_cursor.wav'          # 커서 이동 (빠른 요리)
        }
        
        for sound_name, file_path in sound_files.items():
            if os.path.exists(file_path):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                except Exception as e:
                    print(f"사운드 로드 실패 {file_path}: {e}")
            else:
                print(f"SFX 파일 없음: {file_path}")
    
    def play(self, sound_name: str, volume: float = 0.7):
        """사운드 재생"""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            print(f"사운드 재생 실패 {sound_name}: {e}")
    
    def play_cooking_success(self):
        """요리 성공 사운드"""
        self.play('cooking_success', 0.8)
    
    def play_cooking_failure(self):
        """요리 실패 사운드"""
        self.play('cooking_failure', 0.6)
    
    def play_cooking_start(self):
        """요리 시작 사운드"""
        self.play('cooking_start', 0.5)
