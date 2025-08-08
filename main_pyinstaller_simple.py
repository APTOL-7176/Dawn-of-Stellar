#!/usr/bin/env python3
"""
Dawn Of Stellar - 간단한 PyInstaller 메인 파일 (윈도우 모드 전용)
"""

import sys
import os

def main():
    """간단한 메인 함수 - PyInstaller 전용"""
    # sys 모듈을 안전하게 저장
    import sys as system_module
    
    try:
        print("Dawn of Stellar 시작 중...")
        
        # PyInstaller 환경에서 pygame 초기화
        is_frozen = getattr(system_module, 'frozen', False)
        if is_frozen:
            import pygame
            import os
            
            # 환경 변수 설정
            os.environ['SDL_VIDEODRIVER'] = 'windib'
            
            # pygame 초기화
            pygame.init()
            pygame.display.init()
            
            # 전체화면 설정
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            pygame.display.set_caption("Dawn of Stellar")
            
            # 검은 화면 표시
            screen.fill((0, 0, 0))
            pygame.display.flip()
            
            print("전체화면 초기화 완료")
        
        # 게임 시작
        from main import DawnOfStellarGame
        
        game = DawnOfStellarGame()
        
        # 필요한 속성들 초기화
        if not hasattr(game, 'running'):
            game.running = True
        
        if not hasattr(game, 'game_manager'):
            try:
                from game.integrated_game_manager import IntegratedGameManager
                game.game_manager = IntegratedGameManager()
            except:
                game.game_manager = None
        
        if not hasattr(game, 'keyboard'):
            try:
                from game.input_utils import UnifiedInputManager
                game.keyboard = UnifiedInputManager()
            except:
                class FallbackKeyboard:
                    def get_key(self): return None
                    def is_key_pressed(self, key): return False
                game.keyboard = FallbackKeyboard()
        
        if not hasattr(game, 'story_system'):
            try:
                from story_system import StorySystem
                game.story_system = StorySystem()
            except:
                game.story_system = None
        
        print("게임 시작!")
        game.main_loop()
        print("게임 종료")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
        # 윈도우 모드에서 오류 메시지 표시
        is_frozen = getattr(system_module, 'frozen', False)
        if is_frozen:
            try:
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Dawn of Stellar 오류", f"게임 실행 실패:\n{e}")
                root.destroy()
            except:
                pass
        
        return 1
    
    return 0

if __name__ == "__main__":
    main()
