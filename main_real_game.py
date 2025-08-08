#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DawnOfStellar - 실제 게임 pygame 래퍼 버전
게임패드 지원 + 전체화면 + 실제 게임 실행
"""

import pygame
import sys
import os
import threading
import queue
import io
import time
import subprocess
from contextlib import redirect_stdout, redirect_stderr

class GameIO:
    """게임 입출력 관리 클래스"""
    def __init__(self):
        self.input_queue = queue.Queue()
        self.output_buffer = []
        self.max_lines = 40
        
    def add_output(self, text):
        """출력 텍스트 추가"""
        if text.strip():
            lines = text.strip().split('\n')
            for line in lines:
                self.output_buffer.append(line)
                if len(self.output_buffer) > self.max_lines:
                    self.output_buffer.pop(0)
    
    def get_input(self, prompt=""):
        """입력 대기"""
        if prompt:
            self.add_output(prompt)
        
        while True:
            try:
                return self.input_queue.get(timeout=0.1)
            except queue.Empty:
                continue

class PygameTerminal:
    """pygame 기반 터미널 에뮬레이터"""
    
    def __init__(self):
        pygame.init()
        
        # 전체화면 설정
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("DawnOfStellar - 실제 게임")
        
        # 폰트 설정
        try:
            self.font = pygame.font.Font("Galmuri11.ttf", 16)
        except:
            try:
                self.font = pygame.font.Font("whitrabt.ttf", 16)
            except:
                self.font = pygame.font.Font(None, 16)
        
        # 색상
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 100, 255)
        self.RED = (255, 100, 100)
        
        # 게임패드 설정
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        
        # 게임 IO
        self.game_io = GameIO()
        self.current_input = ""
        self.clock = pygame.time.Clock()
        
        # 게임 스레드
        self.game_thread = None
        self.game_running = False
        
    def start_game_thread(self):
        """게임 스레드 시작"""
        self.game_running = True
        self.game_thread = threading.Thread(target=self.run_actual_game, daemon=True)
        self.game_thread.start()
        
    def run_actual_game(self):
        """실제 DawnOfStellar 게임 실행"""
        try:
            # 게임 실행을 위한 환경 설정
            os.environ['PYGAME_MODE'] = '1'
            os.environ['TERMINAL_MODE'] = '1'
            
            # stdout/stderr 캡처
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            old_input = __builtins__['input']
            
            # 입출력 리다이렉션
            sys.stdout = self.OutputCapture(self.game_io)
            sys.stderr = self.OutputCapture(self.game_io)
            __builtins__['input'] = self.game_io.get_input
            
            try:
                # 실제 게임 실행
                exec(open('main.py', encoding='utf-8').read())
            except SystemExit:
                pass
            except Exception as e:
                self.game_io.add_output(f"게임 오류: {e}")
            finally:
                # 원래 입출력 복원
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                __builtins__['input'] = old_input
                
        except Exception as e:
            self.game_io.add_output(f"게임 실행 오류: {e}")
        finally:
            self.game_running = False
    
    class OutputCapture:
        """출력 캡처 클래스"""
        def __init__(self, game_io):
            self.game_io = game_io
            
        def write(self, text):
            self.game_io.add_output(text)
            
        def flush(self):
            pass
    
    def handle_gamepad_input(self, event):
        """게임패드 입력 처리"""
        if event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            
            # A 버튼 (0) = Enter
            if button == 0:
                if self.current_input.strip():
                    self.game_io.input_queue.put(self.current_input)
                    self.game_io.add_output(f"> {self.current_input}")
                    self.current_input = ""
                else:
                    self.game_io.input_queue.put("")
                    
            # B 버튼 (1) = 취소/뒤로가기
            elif button == 1:
                self.game_io.input_queue.put("q")
                self.game_io.add_output("> q")
                
            # X 버튼 (2) = Backspace
            elif button == 2:
                if self.current_input:
                    self.current_input = self.current_input[:-1]
                    
            # Y 버튼 (3) = ESC
            elif button == 3:
                return False  # 종료
                
            # 숫자 버튼들 (방향패드나 추가 버튼들)
            elif button >= 4 and button <= 12:
                number = str((button - 4) % 9 + 1)
                self.current_input += number
                
        return True
    
    def handle_keyboard_input(self, event):
        """키보드 입력 처리"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.current_input.strip():
                    self.game_io.input_queue.put(self.current_input)
                    self.game_io.add_output(f"> {self.current_input}")
                    self.current_input = ""
                else:
                    self.game_io.input_queue.put("")
                    
            elif event.key == pygame.K_BACKSPACE:
                if self.current_input:
                    self.current_input = self.current_input[:-1]
                    
            elif event.key == pygame.K_ESCAPE:
                return False  # 종료
                
            elif event.unicode and event.unicode.isprintable():
                self.current_input += event.unicode
                
        return True
    
    def draw_screen(self):
        """화면 그리기"""
        self.screen.fill(self.BLACK)
        
        # 타이틀
        title = "DawnOfStellar - 실제 게임 (ESC로 종료)"
        title_surface = self.font.render(title, True, self.GREEN)
        self.screen.blit(title_surface, (20, 20))
        
        # 게임패드 상태
        if self.joystick:
            gamepad_text = f"게임패드: {self.joystick.get_name()}"
            gamepad_surface = self.font.render(gamepad_text, True, self.BLUE)
            self.screen.blit(gamepad_surface, (20, 50))
        
        # 게임 출력
        y = 100
        for line in self.game_io.output_buffer:
            if y + 20 > self.height - 100:
                break
            text_surface = self.font.render(line, True, self.WHITE)
            self.screen.blit(text_surface, (20, y))
            y += 20
        
        # 현재 입력
        input_text = f"입력: {self.current_input}_"
        input_surface = self.font.render(input_text, True, self.GREEN)
        self.screen.blit(input_surface, (20, self.height - 60))
        
        # 게임 상태
        status = "게임 실행 중..." if self.game_running else "게임 대기 중"
        status_surface = self.font.render(status, True, self.RED if not self.game_running else self.GREEN)
        self.screen.blit(status_surface, (20, self.height - 30))
        
        pygame.display.flip()
    
    def run(self):
        """메인 루프"""
        # 게임 시작
        self.game_io.add_output("DawnOfStellar 실제 게임을 시작합니다...")
        self.game_io.add_output("게임 로딩 중...")
        
        # 실제 게임 스레드 시작
        self.start_game_thread()
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.JOYBUTTONDOWN:
                    running = self.handle_gamepad_input(event)
                    
                elif event.type in [pygame.KEYDOWN]:
                    running = self.handle_keyboard_input(event)
            
            self.draw_screen()
            self.clock.tick(60)
        
        # 종료
        self.game_running = False
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=1.0)
        
        pygame.quit()

def main():
    """메인 함수"""
    try:
        terminal = PygameTerminal()
        terminal.run()
    except Exception as e:
        print(f"오류 발생: {e}")
        input("계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    main()
