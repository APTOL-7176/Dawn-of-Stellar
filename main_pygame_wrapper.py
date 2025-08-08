#!/usr/bin/env python3
"""
Dawn Of Stellar - pygame 래퍼 버전
게임패드 필수 지원을 위한 pygame 기반 터미널 에뮬레이터
"""

import sys
import os
import pygame
import time
import queue
import threading
from io import StringIO

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

class PygameTerminal:
    """pygame 기반 터미널 에뮬레이터"""
    
    def __init__(self):
        pygame.init()
        
        # 전체화면 설정
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Dawn of Stellar")
        
        # 폰트 로드
        self.load_fonts()
        
        # 터미널 상태
        self.lines = []
        self.max_lines = 100
        self.input_buffer = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # 색상
        self.bg_color = (8, 8, 12)
        self.text_color = (220, 220, 220)
        self.input_color = (100, 255, 100)
        
        # 입력 큐
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
        # 게임패드
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        
        # 게임 스레드
        self.game_thread = None
        self.game_running = False
        
    def load_fonts(self):
        """폰트 로드"""
        try:
            if getattr(sys, 'frozen', False):
                font_path = os.path.join(sys._MEIPASS, "Galmuri11.ttf")
            else:
                font_path = "Galmuri11.ttf"
            self.font = pygame.font.Font(font_path, 18)
        except:
            try:
                if getattr(sys, 'frozen', False):
                    font_path = os.path.join(sys._MEIPASS, "whitrabt.ttf")
                else:
                    font_path = "whitrabt.ttf"
                self.font = pygame.font.Font(font_path, 18)
            except:
                self.font = pygame.font.SysFont('malgun gothic', 18)
    
    def add_output(self, text):
        """출력 추가"""
        lines = str(text).split('\n')
        for line in lines:
            if line.strip():
                self.lines.append(line)
                if len(self.lines) > self.max_lines:
                    self.lines.pop(0)
    
    def get_input(self, prompt=""):
        """입력 받기"""
        if prompt:
            self.add_output(prompt)
        
        self.input_buffer = ""
        waiting_for_input = True
        
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "quit"
                    elif event.key == pygame.K_RETURN:
                        result = self.input_buffer
                        self.add_output(f"> {result}")
                        return result
                    elif event.key == pygame.K_BACKSPACE:
                        if self.input_buffer:
                            self.input_buffer = self.input_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            self.input_buffer += event.unicode
                elif event.type == pygame.JOYBUTTONDOWN:
                    # 게임패드 버튼 매핑
                    if event.button == 0:  # A 버튼 = Enter
                        result = self.input_buffer
                        self.add_output(f"> {result}")
                        return result
                    elif event.button == 1:  # B 버튼 = 취소
                        return ""
                    elif event.button == 2:  # X 버튼 = 백스페이스
                        if self.input_buffer:
                            self.input_buffer = self.input_buffer[:-1]
            
            self.draw()
            pygame.time.Clock().tick(60)
        
        return ""
    
    def draw(self):
        """화면 그리기"""
        self.screen.fill(self.bg_color)
        
        # 텍스트 라인 출력
        y_offset = 30
        line_height = self.font.get_height() + 2
        
        # 화면에 맞는 줄 수 계산
        max_display_lines = (self.screen.get_height() - 100) // line_height
        
        display_lines = self.lines[-max_display_lines:]
        
        for line in display_lines:
            text_surface = self.font.render(str(line), True, self.text_color)
            self.screen.blit(text_surface, (30, y_offset))
            y_offset += line_height
        
        # 입력 라인
        input_text = f"> {self.input_buffer}"
        if self.cursor_visible:
            input_text += "_"
        
        # 입력 배경
        input_bg = pygame.Rect(25, y_offset - 5, self.screen.get_width() - 50, line_height)
        pygame.draw.rect(self.screen, (20, 20, 20), input_bg)
        
        input_surface = self.font.render(input_text, True, self.input_color)
        self.screen.blit(input_surface, (30, y_offset))
        
        # 커서 깜박임
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        pygame.display.flip()

class PygameIO:
    """pygame 터미널용 입출력 클래스"""
    
    def __init__(self, terminal):
        self.terminal = terminal
    
    def write(self, text):
        """출력"""
        if text and text.strip():
            self.terminal.add_output(text.rstrip())
    
    def flush(self):
        """플러시"""
        pass
    
    def readline(self):
        """한 줄 입력"""
        return self.terminal.get_input()

def run_game_with_pygame():
    """pygame 터미널에서 게임 실행"""
    # pygame 터미널 생성
    terminal = PygameTerminal()
    
    # 시작 메시지
    terminal.add_output("=== Dawn of Stellar ===")
    terminal.add_output("pygame 기반 게임패드 지원 모드")
    
    if terminal.joystick:
        terminal.add_output(f"게임패드 감지: {terminal.joystick.get_name()}")
        terminal.add_output("A: 확인, B: 취소, X: 백스페이스")
    else:
        terminal.add_output("게임패드가 감지되지 않았습니다.")
    
    terminal.add_output("아무 키나 눌러서 게임을 시작하세요...")
    terminal.add_output("ESC: 종료")
    
    # 게임 시작 대기
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                else:
                    waiting = False
                    break
            elif event.type == pygame.JOYBUTTONDOWN:
                waiting = False
                break
        
        terminal.draw()
        pygame.time.Clock().tick(60)
    
    try:
        # 게임 실행
        terminal.add_output("게임을 시작합니다...")
        
        # 표준 입출력을 pygame 터미널로 리다이렉션
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        original_stdin = sys.stdin
        
        pygame_io = PygameIO(terminal)
        sys.stdout = pygame_io
        sys.stderr = pygame_io
        
        # 게임 모듈 로드 및 실행
        import importlib.util
        
        if getattr(sys, 'frozen', False):
            main_py_path = os.path.join(sys._MEIPASS, "main.py")
        else:
            main_py_path = "main.py"
        
        spec = importlib.util.spec_from_file_location("game_main", main_py_path)
        game_main_module = importlib.util.module_from_spec(spec)
        
        # input 함수를 pygame 버전으로 교체
        def pygame_input(prompt=""):
            return terminal.get_input(prompt)
        
        # 게임 모듈의 builtins에 pygame input 주입
        import builtins
        original_input = builtins.input
        builtins.input = pygame_input
        
        spec.loader.exec_module(game_main_module)
        
        # 게임 실행
        game_main_module.main()
        
    except Exception as e:
        terminal.add_output(f"오류 발생: {str(e)}")
        terminal.add_output("ESC를 눌러 종료하세요.")
        
        # 오류 후 대기
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False
            terminal.draw()
            pygame.time.Clock().tick(60)
    
    finally:
        # 원래 입출력 복원
        try:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            sys.stdin = original_stdin
            builtins.input = original_input
        except:
            pass
        
        pygame.quit()

if __name__ == "__main__":
    run_game_with_pygame()
