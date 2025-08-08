#!/usr/bin/env python3
"""
Dawn Of Stellar - 게임패드 지원 전용 메인 파일
콘솔 창 최소화 + pygame 게임 창 별도 표시
"""

import sys
import os
import pygame
import time

# PyInstaller 환경 확인
if getattr(sys, 'frozen', False):
    # PyInstaller로 실행된 경우
    application_path = sys._MEIPASS
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    # 콘솔 창 숨기기
    import ctypes
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
else:
    # 일반 Python으로 실행된 경우
    application_path = os.path.dirname(os.path.abspath(__file__))

def create_game_window():
    """게임 전용 pygame 창 생성"""
    pygame.init()
    
    # 전체화면 모드
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Dawn of Stellar")
    
    # 한글 폰트 로드
    try:
        if getattr(sys, 'frozen', False):
            # PyInstaller 환경
            font_path = os.path.join(sys._MEIPASS, "Galmuri11.ttf")
        else:
            font_path = "Galmuri11.ttf"
        font = pygame.font.Font(font_path, 24)
    except:
        try:
            # 백업 폰트
            if getattr(sys, 'frozen', False):
                font_path = os.path.join(sys._MEIPASS, "whitrabt.ttf")
            else:
                font_path = "whitrabt.ttf"
            font = pygame.font.Font(font_path, 24)
        except:
            # 시스템 기본 폰트
            font = pygame.font.SysFont('malgun gothic', 24)
    
    return screen, font

def show_loading_screen(screen, font):
    """로딩 화면 표시"""
    screen.fill((0, 0, 0))
    
    # 타이틀
    title = font.render("Dawn of Stellar", True, (255, 255, 255))
    title_rect = title.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 100))
    screen.blit(title, title_rect)
    
    # 로딩 메시지
    loading = font.render("Loading game...", True, (200, 200, 200))
    loading_rect = loading.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(loading, loading_rect)
    
    # 게임패드 안내
    gamepad_text = font.render("Gamepad supported - Press any key to continue", True, (150, 150, 150))
    gamepad_rect = gamepad_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
    screen.blit(gamepad_text, gamepad_rect)
    
    # ESC 안내
    esc_text = font.render("Press ESC to exit", True, (100, 100, 100))
    esc_rect = esc_text.get_rect(center=(screen.get_width()//2, screen.get_height() - 50))
    screen.blit(esc_text, esc_rect)
    
    pygame.display.flip()

def main():
    """메인 함수"""
    try:
        # 로그 파일 생성
        with open("gamepad_log.txt", "w", encoding="utf-8") as f:
            f.write("Dawn of Stellar - Gamepad Mode Started\n")
            f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
        
        # pygame 창 생성
        screen, font = create_game_window()
        
        # 게임패드 초기화
        pygame.joystick.init()
        joystick = None
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            with open("gamepad_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Gamepad detected: {joystick.get_name()}\n")
        
        # 로딩 화면 표시
        show_loading_screen(screen, font)
        
        # 키 입력 대기 (게임패드 또는 키보드)
        waiting = True
        clock = pygame.time.Clock()
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                    else:
                        # 게임 시작
                        waiting = False
                        start_game(screen, font)
                elif event.type == pygame.JOYBUTTONDOWN:
                    # 게임패드 버튼으로 게임 시작
                    waiting = False
                    start_game(screen, font)
            
            clock.tick(60)
        
        pygame.quit()
        
    except Exception as e:
        # 오류 로그
        with open("gamepad_error.txt", "w", encoding="utf-8") as f:
            f.write(f"Error: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())

def start_game(screen, font):
    """실제 게임 시작"""
    try:
        # 게임 시작 메시지
        screen.fill((0, 0, 0))
        start_text = font.render("Starting Dawn of Stellar...", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(start_text, start_rect)
        
        # 곧 콘솔로 전환된다는 안내
        switch_text = font.render("Starting Dawn of Stellar...", True, (200, 200, 200))
        switch_rect = switch_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
        screen.blit(switch_text, switch_rect)
        
        pygame.display.flip()
        time.sleep(2)
        
        # pygame 창 닫기
        pygame.quit()
        
        # 콘솔 창 다시 보이기
        import ctypes
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)  # SW_NORMAL
        except:
            pass
        
        # 실제 게임 모듈 로드 및 실행
        import importlib.util
        
        # PyInstaller 환경에서 main.py 경로 찾기
        if getattr(sys, 'frozen', False):
            main_py_path = os.path.join(sys._MEIPASS, "main.py")
        else:
            main_py_path = "main.py"
        
        with open("gamepad_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Loading main.py from: {main_py_path}\n")
        
        spec = importlib.util.spec_from_file_location("game_main", main_py_path)
        game_main_module = importlib.util.module_from_spec(spec)
        
        spec.loader.exec_module(game_main_module)
        
        # 게임 실행
        with open("gamepad_log.txt", "a", encoding="utf-8") as f:
            f.write("Starting game main...\n")
        
        # 게임 실행
        game_main_module.main()
        
    except Exception as e:
        with open("gamepad_error.txt", "a", encoding="utf-8") as f:
            f.write(f"Game start error: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())

if __name__ == "__main__":
    main()
