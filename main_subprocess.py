#!/usr/bin/env python3
"""
Dawn Of Stellar - 서브프로세스 실행 버전
pygame 창 유지 + 게임 별도 실행
"""

import sys
import os
import pygame
import subprocess
import time

# PyInstaller 환경 확인
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    # 콘솔 창 숨기기
    import ctypes
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

class TerminalEmulator:
    """pygame에서 터미널 에뮬레이션"""
    
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.lines = []
        self.max_lines = 50
        self.current_input = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # 색상 정의
        self.bg_color = (8, 8, 12)
        self.text_color = (220, 220, 220)
        self.input_color = (100, 255, 100)
        self.cursor_color = (255, 255, 255)
        self.error_color = (255, 100, 100)
        
    def add_line(self, text):
        """텍스트 라인 추가"""
        self.lines.append(str(text))
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)
    
    def draw(self):
        """화면에 터미널 그리기"""
        self.screen.fill(self.bg_color)
        
        # 텍스트 라인들 그리기
        y_offset = 30
        line_height = self.font.get_height() + 4
        
        # 화면 크기에 맞춰 표시할 줄 수 계산
        max_lines = (self.screen.get_height() - 100) // line_height
        
        for line in self.lines[-max_lines:]:
            text_surface = self.font.render(str(line), True, self.text_color, None)
            self.screen.blit(text_surface, (30, y_offset))
            y_offset += line_height
        
        # 현재 입력 라인 그리기
        input_text = f"> {self.current_input}"
        if self.cursor_visible:
            input_text += "_"
        
        # 입력 라인 배경
        input_bg_rect = pygame.Rect(25, y_offset - 5, self.screen.get_width() - 50, line_height)
        pygame.draw.rect(self.screen, (20, 20, 20), input_bg_rect)
        
        input_surface = self.font.render(input_text, True, self.input_color, None)
        self.screen.blit(input_surface, (30, y_offset))
        
        # 커서 깜박임
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        pygame.display.flip()

def create_fullscreen_terminal():
    """전체화면 터미널 생성"""
    pygame.init()
    pygame.mixer.quit()  # 사운드 비활성화로 중복 방지
    
    # 전체화면 모드
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
    pygame.display.set_caption("Dawn of Stellar - Launcher")
    
    # 한글 폰트 로드
    try:
        if getattr(sys, 'frozen', False):
            font_path = os.path.join(sys._MEIPASS, "Galmuri11.ttf")
        else:
            font_path = "Galmuri11.ttf"
        font = pygame.font.Font(font_path, 20)
    except:
        try:
            if getattr(sys, 'frozen', False):
                font_path = os.path.join(sys._MEIPASS, "whitrabt.ttf")
            else:
                font_path = "whitrabt.ttf"
            font = pygame.font.Font(font_path, 20)
        except:
            font = pygame.font.SysFont('malgun gothic', 20)
    
    return screen, font

def run_game_subprocess():
    """게임을 서브프로세스로 실행"""
    try:
        if getattr(sys, 'frozen', False):
            # PyInstaller 환경에서는 Python으로 직접 실행
            python_exe = sys.executable
            main_py_path = os.path.join(sys._MEIPASS, "main.py")
            
            # 서브프로세스로 게임 실행
            process = subprocess.Popen(
                [python_exe, main_py_path],
                cwd=sys._MEIPASS,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return process
        else:
            # 개발 환경
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return process
            
    except Exception as e:
        print(f"게임 실행 오류: {e}")
        return None

def main():
    """메인 함수"""
    try:
        # 전체화면 터미널 생성
        screen, font = create_fullscreen_terminal()
        terminal = TerminalEmulator(screen, font)
        
        # 게임패드 초기화
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            terminal.add_line(f"게임패드 감지: {joystick.get_name()}")
        else:
            terminal.add_line("게임패드가 감지되지 않았습니다.")
        
        terminal.add_line("Dawn of Stellar - 게임 런처")
        terminal.add_line("아무 키나 눌러서 게임을 시작하세요...")
        terminal.add_line("게임은 별도 콘솔 창에서 실행됩니다.")
        terminal.add_line("ESC를 눌러서 종료")
        
        clock = pygame.time.Clock()
        game_started = False
        game_process = None
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # 게임 프로세스 종료
                        if game_process and game_process.poll() is None:
                            game_process.terminate()
                        running = False
                    elif not game_started:
                        # 게임 시작
                        game_started = True
                        terminal.add_line("게임을 시작합니다...")
                        terminal.add_line("별도 콘솔 창이 열립니다...")
                        game_process = run_game_subprocess()
                        if game_process:
                            terminal.add_line("게임이 성공적으로 시작되었습니다!")
                            terminal.add_line("게임 창을 확인하세요.")
                        else:
                            terminal.add_line("게임 시작에 실패했습니다.")
                            game_started = False
                elif event.type == pygame.JOYBUTTONDOWN and not game_started:
                    # 게임패드로 게임 시작
                    game_started = True
                    terminal.add_line("게임패드로 게임을 시작합니다...")
                    terminal.add_line("별도 콘솔 창이 열립니다...")
                    game_process = run_game_subprocess()
                    if game_process:
                        terminal.add_line("게임이 성공적으로 시작되었습니다!")
                        terminal.add_line("게임 창을 확인하세요.")
                    else:
                        terminal.add_line("게임 시작에 실패했습니다.")
                        game_started = False
            
            # 게임 프로세스 상태 확인
            if game_process and game_process.poll() is not None:
                # 게임이 종료됨
                terminal.add_line("게임이 종료되었습니다.")
                terminal.add_line("다시 시작하려면 아무 키나 누르세요.")
                game_started = False
                game_process = None
            
            # 화면 업데이트
            terminal.draw()
            clock.tick(60)
        
        # 정리
        if game_process and game_process.poll() is None:
            game_process.terminate()
        
        pygame.quit()
        
    except Exception as e:
        print(f"오류: {str(e)}")
        input("Enter를 눌러 종료...")

if __name__ == "__main__":
    main()
