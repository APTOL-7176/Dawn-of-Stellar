#!/usr/bin/env python3
"""
Dawn Of Stellar - 전체화면 터미널 에뮬레이터
게임패드 지원 + pygame 창에서 게임 실행
"""

import sys
import os
import pygame
import time
import io

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
        
        # 색상 정의 (더 선명한 색상)
        self.bg_color = (8, 8, 12)  # 약간 푸른 검정
        self.text_color = (220, 220, 220)  # 밝은 회색
        self.input_color = (100, 255, 100)  # 밝은 녹색
        self.cursor_color = (255, 255, 255)
        self.error_color = (255, 100, 100)  # 에러용 빨간색
        
        # 출력 캡처
        self.output_buffer = io.StringIO()
        
    def add_line(self, text):
        """텍스트 라인 추가"""
        self.lines.append(str(text))
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)
    
    def add_input_char(self, char):
        """입력 문자 추가"""
        if char == '\b':  # 백스페이스
            if self.current_input:
                self.current_input = self.current_input[:-1]
        elif char == '\r' or char == '\n':  # 엔터
            return self.current_input
        else:
            self.current_input += char
        return None
    
    def draw(self):
        """화면에 터미널 그리기 - 고화질 렌더링"""
        self.screen.fill(self.bg_color)
        
        # 텍스트 라인들 그리기 (안티앨리어싱 적용)
        y_offset = 30
        line_height = self.font.get_height() + 4  # 줄 간격 증가
        
        # 화면 크기에 맞춰 표시할 줄 수 계산
        max_lines = (self.screen.get_height() - 100) // line_height
        
        for line in self.lines[-max_lines:]:  # 화면에 맞는 줄 수만 표시
            # 안티앨리어싱으로 부드러운 텍스트 렌더링
            text_surface = self.font.render(str(line), True, self.text_color, None)
            self.screen.blit(text_surface, (30, y_offset))
            y_offset += line_height
        
        # 현재 입력 라인 그리기 (더 눈에 띄게)
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
        if self.cursor_timer > 30:  # 0.5초마다 깜박임
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        # 화면 업데이트 (더블 버퍼링)
        pygame.display.flip()

def create_fullscreen_terminal():
    """전체화면 터미널 생성 - 고화질 + 듀얼 폰트"""
    pygame.init()
    
    # 고해상도 전체화면 모드
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
    pygame.display.set_caption("Dawn of Stellar - Terminal")
    
    # 화질 개선 설정
    pygame.font.init()
    
    # 듀얼 폰트 시스템 - 영어와 한글 따로 로드
    eng_font = None
    kor_font = None
    
    # 영어 폰트 (whitrabt)
    try:
        if getattr(sys, 'frozen', False):
            eng_font_path = os.path.join(sys._MEIPASS, "whitrabt.ttf")
        else:
            eng_font_path = "whitrabt.ttf"
        eng_font = pygame.font.Font(eng_font_path, 20)
    except:
        eng_font = pygame.font.SysFont('consolas', 20)
    
    # 한글 폰트 (Galmuri11)
    try:
        if getattr(sys, 'frozen', False):
            kor_font_path = os.path.join(sys._MEIPASS, "Galmuri11.ttf")
        else:
            kor_font_path = "Galmuri11.ttf"
        kor_font = pygame.font.Font(kor_font_path, 20)
    except:
        kor_font = pygame.font.SysFont('malgun gothic', 20)
    
    # 기본 폰트로 한글 폰트 사용 (fallback)
    font = kor_font if kor_font else eng_font
    
    return screen, font

class GameOutputCapture:
    """게임 출력 캡처 클래스"""
    
    def __init__(self, terminal):
        self.terminal = terminal
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
    
    def write(self, text):
        """출력 캡처"""
        if text.strip():
            self.terminal.add_line(text.strip())
        return len(text)
    
    def flush(self):
        """플러시"""
        pass

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
        
        terminal.add_line("Dawn of Stellar - 전체화면 모드")
        terminal.add_line("아무 키나 눌러서 게임을 시작하세요...")
        terminal.add_line("ESC를 눌러서 종료")
        
        clock = pygame.time.Clock()
        game_started = False
        game_finished = False
        game_step = 0  # 게임 실행 단계
        game_main_module = None
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif not game_started and not game_finished:
                        # 게임 시작
                        game_started = True
                        game_step = 1
                        terminal.add_line("게임을 시작합니다...")
                elif event.type == pygame.JOYBUTTONDOWN and not game_started and not game_finished:
                    # 게임패드로 게임 시작
                    game_started = True
                    game_step = 1
                    terminal.add_line("게임패드로 게임을 시작합니다...")
            
            # 게임 실행 단계별 처리 (메인 스레드에서)
            if game_started and not game_finished:
                if game_step == 1:
                    # 1단계: 게임 모듈 로드
                    terminal.add_line("=== Dawn of Stellar 시작 ===")
                    terminal.add_line("게임 모듈을 로드하는 중...")
                    game_step = 2
                elif game_step == 2:
                    # 2단계: 실제 모듈 로드
                    try:
                        import importlib.util
                        
                        if getattr(sys, 'frozen', False):
                            main_py_path = os.path.join(sys._MEIPASS, "main.py")
                        else:
                            main_py_path = "main.py"
                        
                        terminal.add_line(f"게임 모듈 로드: {main_py_path}")
                        
                        if not os.path.exists(main_py_path):
                            terminal.add_line(f"오류: {main_py_path} 파일을 찾을 수 없습니다.")
                            game_finished = True
                            game_step = 0
                        else:
                            spec = importlib.util.spec_from_file_location("game_main", main_py_path)
                            if spec is None:
                                terminal.add_line("오류: 게임 모듈을 로드할 수 없습니다.")
                                game_finished = True
                                game_step = 0
                            else:
                                game_main_module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(game_main_module)
                                terminal.add_line("게임 모듈 로드 완료!")
                                game_step = 3
                    except Exception as e:
                        terminal.add_line(f"모듈 로드 오류: {str(e)}")
                        game_finished = True
                        game_step = 0
                elif game_step == 3:
                    # 3단계: 게임 실행 준비
                    terminal.add_line("게임 시작!")
                    terminal.add_line("=" * 50)
                    terminal.add_line("게임이 별도 창에서 실행됩니다...")
                    game_step = 4
                elif game_step == 4:
                    # 4단계: 실제 게임 실행 (메인 스레드에서)
                    try:
                        if game_main_module:
                            game_main_module.main()
                        game_finished = True
                        terminal.add_line("게임이 정상적으로 종료되었습니다.")
                        terminal.add_line("ESC를 눌러 나가세요.")
                    except SystemExit:
                        game_finished = True
                        terminal.add_line("게임이 정상적으로 종료되었습니다.")
                        terminal.add_line("ESC를 눌러 나가세요.")
                    except Exception as e:
                        game_finished = True
                        terminal.add_line(f"게임 실행 오류: {str(e)}")
                        terminal.add_line("ESC를 눌러 나가세요.")
                    game_step = 0
            
            # 화면 업데이트
            terminal.draw()
            clock.tick(60)
        
        pygame.quit()
        
    except Exception as e:
        print(f"오류: {str(e)}")
        input("Enter를 눌러 종료...")

if __name__ == "__main__":
    main()
