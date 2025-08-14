#!/usr/bin/env python3
"""
지연 BGM 재생 시스템
던전 생성이나 기타 작업이 완전히 끝난 후에 BGM을 재생하는 시스템
"""

import threading
import time
from typing import Optional, Callable

class DelayedBGMPlayer:
    """지연된 BGM 재생기"""
    
    def __init__(self, sound_system):
        self.sound_system = sound_system
        self.current_thread = None
        self.should_cancel = False
        
    def play_bgm_after_delay(self, bgm_name: str, delay: float = 2.5, 
                           fade_in: float = 2.0, loop: bool = True,
                           condition_check: Optional[Callable] = None):
        """지연 후 BGM 재생 (비동기)"""
        # 이전 지연 재생이 있으면 취소
        self.cancel_delayed_playback()
        
        def delayed_play():
            # 지연 시간 동안 대기
            for i in range(int(delay * 10)):  # 100ms 단위로 체크
                if self.should_cancel:
                    return
                time.sleep(0.1)
                
                # 조건 체크 함수가 있으면 확인
                if condition_check and not condition_check():
                    time.sleep(0.1)  # 조건이 만족되지 않으면 더 대기
                    continue
            
            # 지연 시간이 끝나면 BGM 재생
            if not self.should_cancel:
                self.sound_system.play_bgm(bgm_name, fade_in=fade_in, loop=loop)
        
        # 새로운 스레드에서 지연 재생 시작
        self.should_cancel = False
        self.current_thread = threading.Thread(target=delayed_play, daemon=True)
        self.current_thread.start()
    
    def cancel_delayed_playback(self):
        """지연된 BGM 재생 취소"""
        self.should_cancel = True
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=0.5)
        self.current_thread = None
    
    def play_dungeon_bgm_when_ready(self, floor: int, world=None):
        """던전이 준비되면 BGM 재생"""
        def dungeon_ready_check():
            """던전 생성이 완료되었는지 확인 (더 엄격한 조건)"""
            if not world:
                return False  # world가 없으면 절대 재생하지 않음
            
            # 던전 준비 상태 체크
            if hasattr(world, 'is_dungeon_ready'):
                is_ready = world.is_dungeon_ready()
                if not is_ready:
                    return False
            
            # 추가 안전 체크들
            checks = [
                hasattr(world, 'tiles') and world.tiles is not None,
                hasattr(world, 'player_pos') and world.player_pos != (0, 0),
                hasattr(world, 'rooms') and len(world.rooms) > 0,
                hasattr(world, 'dungeon_ready') and world.dungeon_ready
            ]
            
            return all(checks)  # 모든 조건이 만족되어야 함
        
        bgm_name = self.sound_system.get_dungeon_bgm_by_floor(floor)
        self.play_bgm_after_delay(
            bgm_name, 
            delay=3.0,  # 1.0 -> 3.0초로 증가 (더 긴 지연)
            fade_in=2.0,
            condition_check=dungeon_ready_check
        )

# 전역 지연 BGM 플레이어
_delayed_bgm_player = None

def get_delayed_bgm_player():
    """지연 BGM 플레이어 인스턴스 반환"""
    global _delayed_bgm_player
    if _delayed_bgm_player is None:
        from game.ffvii_sound_system import get_ffvii_sound_system
        _delayed_bgm_player = DelayedBGMPlayer(get_ffvii_sound_system())
    return _delayed_bgm_player
