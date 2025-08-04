#!/usr/bin/env python3
"""
BGM 및 음향 효과 시스템
"""

from config import game_config

class BGMManager:
    """BGM 관리 클래스"""
    
    def __init__(self):
        self.current_track = None
        self.is_playing = False
        
    def play_bgm(self, scene: str):
        """특정 장면의 BGM 재생"""
        track = game_config.get_bgm_track(scene)
        
        if track != self.current_track:
            self.stop_bgm()
            self.current_track = track
            self._start_playback(track)
    
    def _start_playback(self, track: str):
        """BGM 재생 시작 (실제 구현에서는 pygame 등 사용)"""
        print(f"🎵 BGM 재생: {track}")
        self.is_playing = True
        
        # BGM 정보 표시
        if track == "prelude":
            print("   ♪ Final Fantasy VII - Prelude")
            print("   ♪ 캐릭터 선택 테마")
        elif track == "Main theme of FFVII":
            print("   ♪ Final Fantasy VII - Main Theme")
            print("   ♪ 메인 메뉴 테마")
    
    def stop_bgm(self):
        """BGM 정지"""
        if self.is_playing:
            print(f"🔇 BGM 정지: {self.current_track}")
            self.is_playing = False
            self.current_track = None
    
    def fade_out(self, duration: float = 2.0):
        """BGM 페이드 아웃"""
        if self.is_playing:
            print(f"🎵 BGM 페이드 아웃 ({duration}초)")
            self.stop_bgm()
    
    def set_volume(self, volume: float):
        """볼륨 설정 (0.0 ~ 1.0)"""
        volume = max(0.0, min(1.0, volume))
        print(f"🔊 볼륨 설정: {int(volume * 100)}%")

# 전역 BGM 매니저 인스턴스
bgm_manager = BGMManager()

def play_character_select_bgm():
    """캐릭터 선택 BGM 재생"""
    bgm_manager.play_bgm("character_select")

def play_main_menu_bgm():
    """메인 메뉴 BGM 재생"""
    bgm_manager.play_bgm("main_menu")

def stop_all_bgm():
    """모든 BGM 정지"""
    bgm_manager.stop_bgm()
