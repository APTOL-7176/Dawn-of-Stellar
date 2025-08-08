#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DawnOfStellar - 개선된 pygame 래퍼
한글 폰트 지원 + 게임패드 + 실제 게임 실행
"""

import pygame
import sys
import os
import threading
import queue
import subprocess
import time
import platform
import shutil
from pathlib import Path

# pkg_resources는 선택적 import
try:
    import pkg_resources
except ImportError:
    pkg_resources = None

class GameLauncher:
    """pygame 기반 게임 런처 (BGM 지원)"""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # 오디오 믹서 초기화
        
        # 화면 설정 (전체 창 모드 - 최대화된 창)
        info = pygame.display.Info()
        self.width = info.current_w - 100  # 작업표시줄 공간 확보
        self.height = info.current_h - 100
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("DawnOfStellar - 게임 런처")
        
        # BGM 시스템
        self.bgm_volume = 0.3
        self.sfx_volume = 0.5
        self.bgm_playing = False
        
        # BGM 파일 경로 (에어리스 교회 테마)
        self.bgm_files = [
            "game/audio/bgm/13-Flowers Blooming in the Church.mp3",  # 에어리스 교회 테마
            "game/audio/bgm/26-Ahead on Our Way.mp3",  # 평화로운 BGM
            "game/audio/bgm/39-Continue.mp3",  # 부드러운 BGM
        ]
        
        # 효과음 (버튼 클릭 등)
        self.sfx_files = {
            "button_hover": "game/audio/sfx/000.wav",     # 커서 이동 (메뉴 선택)
            "button_select": "game/audio/sfx/001.wav",    # 확인 (메뉴 확인)
            "button_back": "game/audio/sfx/003.wav"       # 취소 (메뉴 취소)
        }
        
        # BGM 시작
        self.start_bgm()
        
        # 폰트 설정
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.korean_font_large = None
        self.korean_font_medium = None
        self.korean_font_small = None
        
        # 폰트 로드 시도 (한글 지원 폰트 우선)
        font_paths = [
            "Galmuri11.ttf",                   # 1순위: 한글 지원 폰트
            "C:/Windows/Fonts/malgun.ttf",     # 2순위: 맑은고딕 (한글)
            "C:/Windows/Fonts/gulim.ttf",      # 3순위: 굴림 (한글)
            "whitrabt.ttf",                    # 4순위: 영어 전용 폰트
            "C:/Windows/Fonts/consola.ttf",    # Consolas (영어 고정폭)
            "C:/Windows/Fonts/arial.ttf",      # Arial (영어)
        ]
        
        # 한글 폰트 우선 로드
        korean_fonts = ["Galmuri11.ttf", "C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/gulim.ttf"]
        for korean_font_path in korean_fonts:
            try:
                if os.path.exists(korean_font_path):
                    self.korean_font_large = pygame.font.Font(korean_font_path, 24)
                    self.korean_font_medium = pygame.font.Font(korean_font_path, 18)
                    self.korean_font_small = pygame.font.Font(korean_font_path, 14)
                    print(f"한글 폰트 로드 성공: {korean_font_path}")
                    break
            except Exception as e:
                print(f"한글 폰트 로드 실패 {korean_font_path}: {e}")
                continue
        
        # 기본 폰트 로드
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    self.font_large = pygame.font.Font(font_path, 24)
                    self.font_medium = pygame.font.Font(font_path, 18)
                    self.font_small = pygame.font.Font(font_path, 14)
                    print(f"기본 폰트 로드 성공: {font_path}")
                    break
            except Exception as e:
                print(f"폰트 로드 실패 {font_path}: {e}")
                continue
        
        # 폰트를 찾지 못한 경우 기본 폰트 사용
        if not self.font_large:
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 14)
            print("기본 폰트 사용")
        
        # 색상
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (100, 150, 255)
        self.RED = (255, 100, 100)
        self.YELLOW = (255, 255, 100)
        
        # 게임패드 설정
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"게임패드 연결됨: {self.joystick.get_name()}")
        
        self.clock = pygame.time.Clock()
        self.selected_option = 0
        self.options = [
            ("Python 개발 모드", "Python 런처 실행 (권장)"),
            ("전체 창 모드", "게임을 전체화면으로 실행"),
            ("간단한 테스트 게임", "pygame 테스트 실행"),
            ("게임패드 전용 버전", "게임패드 전용 모드 실행"),
            ("실제 게임 실행", "main.py 직접 실행"),
            ("시스템 설정", "고급 설정 및 도구"),
            ("PyInstaller 빌드", "exe 파일 생성"),
            ("게임패드 테스트", "게임패드 입력 확인"),
            ("BGM 설정", "음악 볼륨 조절"),
            ("종료", "프로그램 종료")
        ]
    
    def start_bgm(self):
        """BGM 시작"""
        try:
            for bgm_file in self.bgm_files:
                if os.path.exists(bgm_file):
                    pygame.mixer.music.load(bgm_file)
                    pygame.mixer.music.set_volume(self.bgm_volume)
                    pygame.mixer.music.play(-1)  # 무한 반복
                    self.bgm_playing = True
                    print(f"BGM 시작: {bgm_file}")
                    break
            else:
                print("BGM 파일을 찾을 수 없습니다.")
        except Exception as e:
            print(f"BGM 로드 실패: {e}")
    
    def play_sfx(self, sfx_name):
        """효과음 재생"""
        try:
            if sfx_name in self.sfx_files:
                sfx_file = self.sfx_files[sfx_name]
                if os.path.exists(sfx_file):
                    sound = pygame.mixer.Sound(sfx_file)
                    sound.set_volume(self.sfx_volume)
                    sound.play()
        except Exception as e:
            print(f"효과음 재생 실패: {e}")
    
    def stop_bgm(self):
        """BGM 정지"""
        try:
            pygame.mixer.music.stop()
            self.bgm_playing = False
        except Exception as e:
            print(f"BGM 정지 실패: {e}")
    
    def adjust_bgm_volume(self, change):
        """BGM 볼륨 조절"""
        self.bgm_volume = max(0.0, min(1.0, self.bgm_volume + change))
        if self.bgm_playing:
            pygame.mixer.music.set_volume(self.bgm_volume)
        return self.bgm_volume
    
    def render_text(self, text, font, color, center_x=None, y=None):
        """텍스트 렌더링 (한글 지원 강화)"""
        try:
            # 한글 텍스트인지 확인
            has_korean = any('\uac00' <= char <= '\ud7af' for char in text)
            
            # 사용할 폰트 결정
            if has_korean and self.korean_font_large:
                # 한글이 포함되어 있고 한글 폰트가 있는 경우
                if font == self.font_large:
                    use_font = self.korean_font_large
                elif font == self.font_medium:
                    use_font = self.korean_font_medium
                elif font == self.font_small:
                    use_font = self.korean_font_small
                else:
                    use_font = self.korean_font_large
            else:
                # 영어만 있거나 한글 폰트가 없는 경우
                use_font = font
            
            surface = use_font.render(text, True, color)
            
            if center_x is not None:
                x = center_x - surface.get_width() // 2
            else:
                x = 50
            
            if y is not None:
                self.screen.blit(surface, (x, y))
                return y + surface.get_height() + 10
                
        except Exception as e:
            # 렌더링 실패 시 기본 폰트로 대체
            print(f"텍스트 렌더링 오류: {e} (텍스트: {text})")
            try:
                surface = pygame.font.Font(None, 24).render(text, True, color)
                if center_x is not None:
                    x = center_x - surface.get_width() // 2
                else:
                    x = 50
                
                if y is not None:
                    self.screen.blit(surface, (x, y))
                    return y + surface.get_height() + 10
            except:
                print(f"기본 폰트도 실패, 텍스트 건너뜀: {text}")
        
        return y
    
    def handle_input(self, event):
        """입력 처리 (키보드 + 게임패드)"""
        if event.type == pygame.KEYDOWN:
            # 화살표 + WASD 지원
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self.play_sfx("button_hover")  # 효과음 추가
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self.play_sfx("button_hover")  # 효과음 추가
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.play_sfx("button_select")  # 효과음 추가
                return self.execute_option()
            elif event.key == pygame.K_ESCAPE:
                self.play_sfx("button_back")  # 효과음 추가
                return False
            # 숫자키로 직접 선택
            elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                option_num = event.key - pygame.K_1
                if option_num < len(self.options):
                    self.selected_option = option_num
                    self.play_sfx("button_select")  # 효과음 추가
                    return self.execute_option()
                
        elif event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            if button == 0:  # A 버튼 (확인)
                self.play_sfx("button_select")  # 효과음 추가
                return self.execute_option()
            elif button == 1:  # B 버튼 (종료)
                self.play_sfx("button_back")  # 효과음 추가
                return False
            elif button == 2:  # X 버튼
                pass  # 예약됨
            elif button == 3:  # Y 버튼
                pass  # 예약됨
                
        elif event.type == pygame.JOYHATMOTION:
            # 십자 패드 (D-Pad) 지원
            x, y = event.value
            if y == 1:  # 위쪽
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self.play_sfx("button_hover")  # 효과음 추가
            elif y == -1:  # 아래쪽
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self.play_sfx("button_hover")  # 효과음 추가
                
        elif event.type == pygame.JOYAXISMOTION:
            # 아날로그 스틱 지원 (왼쪽 스틱)
            if event.axis == 1:  # 세로축
                if event.value < -0.5:  # 위쪽
                    if not hasattr(self, '_stick_moved') or not self._stick_moved:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                        self.play_sfx("button_hover")  # 효과음 추가
                        self._stick_moved = True
                elif event.value > 0.5:  # 아래쪽
                    if not hasattr(self, '_stick_moved') or not self._stick_moved:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                        self.play_sfx("button_hover")  # 효과음 추가
                        self._stick_moved = True
                else:
                    self._stick_moved = False
        
        return True
    
    def execute_option(self):
        """선택된 옵션 실행"""
        option = self.options[self.selected_option][0]
        
        if option == "Python 개발 모드":
            self.launch_python_mode()
        elif option == "전체 창 모드":
            self.launch_full_window_mode()
        elif option == "간단한 테스트 게임":
            self.launch_test_mode()
        elif option == "게임패드 전용 버전":
            self.launch_gamepad_mode()
        elif option == "실제 게임 실행":
            self.launch_real_game()
        elif option == "시스템 설정":
            self.launch_system_settings()
        elif option == "PyInstaller 빌드":
            self.launch_pyinstaller_build()
        elif option == "게임패드 테스트":
            self.gamepad_test()
        elif option == "BGM 설정":
            self.bgm_settings()
        elif option == "종료":
            self.stop_bgm()  # 종료 시 BGM 정지
            return False
            
        return True
    
    def launch_python_mode(self):
        """Python 런처 실행"""
        try:
            # 새 프로세스로 Python 런처 실행 (백그라운드)
            self.show_message("Python 런처를 실행합니다...", 1)
            
            if os.path.exists(".venv/Scripts/python.exe"):
                process = subprocess.Popen([".venv/Scripts/python.exe", "python_launcher.py"])
            else:
                process = subprocess.Popen(["python", "python_launcher.py"])
            
            # Python 런처 실행 후 바로 메시지 표시
            self.show_message("Python 런처가 실행되었습니다! (런처는 계속 사용 가능)", 2)
            
        except Exception as e:
            self.show_message(f"실행 오류: {e}", 3)
    
    def launch_real_game(self):
        """실제 게임 실행"""
        try:
            # 새 프로세스로 실제 게임 실행 (백그라운드)
            self.show_message("실제 게임을 실행합니다...", 1)
            
            if os.path.exists(".venv/Scripts/python.exe"):
                # Popen으로 백그라운드 실행
                process = subprocess.Popen([".venv/Scripts/python.exe", "main.py"])
            else:
                process = subprocess.Popen(["python", "main.py"])
            
            # 게임 실행 후 바로 메시지 표시
            self.show_message("게임이 실행되었습니다! (런처는 계속 사용 가능)", 2)
            
        except Exception as e:
            self.show_message(f"실행 오류: {e}", 3)
    
    def launch_full_window_mode(self):
        """전체 창 모드 실행 (실제 게임을 전체화면으로)"""
        try:
            self.show_message("전체 창 모드로 게임을 실행합니다...", 1)
            
            # 실제 게임을 전체화면 모드로 실행
            if os.path.exists(".venv/Scripts/python.exe"):
                # 환경변수로 전체화면 모드 설정
                env = os.environ.copy()
                env['FULLSCREEN_MODE'] = '1'
                env['DISPLAY_MODE'] = 'fullscreen'
                
                process = subprocess.Popen([".venv/Scripts/python.exe", "main.py"], env=env)
            else:
                env = os.environ.copy()
                env['FULLSCREEN_MODE'] = '1'
                env['DISPLAY_MODE'] = 'fullscreen'
                
                process = subprocess.Popen(["python", "main.py"], env=env)
            
            self.show_message("전체 창 모드 게임이 실행되었습니다!", 2)
                
        except Exception as e:
            self.show_message(f"실행 오류: {e}", 3)
    
    def launch_test_mode(self):
        """테스트 게임 실행 (간단한 pygame 테스트)"""
        try:
            self.show_message("간단한 테스트 게임을 실행합니다...", 1)
            
            # main_simple_test.py가 있으면 실행
            if os.path.exists("main_simple_test.py"):
                if os.path.exists(".venv/Scripts/python.exe"):
                    process = subprocess.Popen([".venv/Scripts/python.exe", "main_simple_test.py"])
                else:
                    process = subprocess.Popen(["python", "main_simple_test.py"])
                
                self.show_message("테스트 게임이 실행되었습니다!", 2)
            else:
                self.show_message("테스트 파일(main_simple_test.py)을 찾을 수 없습니다", 3)
                
        except Exception as e:
            self.show_message(f"실행 오류: {e}", 3)
    
    def launch_gamepad_mode(self):
        """게임패드 전용 버전 실행 (게임패드 최적화 모드)"""
        try:
            self.show_message("게임패드 전용 모드로 게임을 실행합니다...", 1)
            
            # 게임패드 최적화 환경변수 설정
            if os.path.exists(".venv/Scripts/python.exe"):
                env = os.environ.copy()
                env['GAMEPAD_ONLY'] = '1'
                env['ENABLE_GAMEPAD'] = '1'
                env['DISABLE_KEYBOARD'] = '1'
                
                process = subprocess.Popen([".venv/Scripts/python.exe", "main.py"], env=env)
            else:
                env = os.environ.copy()
                env['GAMEPAD_ONLY'] = '1'
                env['ENABLE_GAMEPAD'] = '1'
                env['DISABLE_KEYBOARD'] = '1'
                
                process = subprocess.Popen(["python", "main.py"], env=env)
            
            self.show_message("게임패드 전용 모드 게임이 실행되었습니다!", 2)
                
        except Exception as e:
            self.show_message(f"실행 오류: {e}", 3)
    
    def launch_build_mode(self):
        """PyInstaller 빌드 메뉴"""
        try:
            self.show_build_menu()
                
        except Exception as e:
            self.show_message(f"빌드 오류: {e}", 3)
    
    def launch_pyinstaller_build(self):
        """PyInstaller 빌드 메뉴 (별칭)"""
        self.launch_build_mode()

    def gamepad_test(self):
        """게임패드 테스트"""
        if not self.joystick:
            self.show_message("게임패드가 연결되지 않았습니다!", 2)
            return
        
        test_running = True
        button_pressed = []
        
        while test_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    test_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        test_running = False
                elif event.type == pygame.JOYBUTTONDOWN:
                    button_pressed.append(f"버튼 {event.button} 눌림")
                    if len(button_pressed) > 10:
                        button_pressed.pop(0)
                    if event.button == 1:  # B 버튼으로 종료
                        test_running = False
            
            # 화면 그리기
            self.screen.fill(self.BLACK)
            
            y = 50
            y = self.render_text("게임패드 테스트", self.font_large, self.GREEN, self.width//2, y)
            y += 20
            
            if self.joystick:
                y = self.render_text(f"게임패드: {self.joystick.get_name()}", self.font_medium, self.WHITE, self.width//2, y)
                y = self.render_text("버튼을 눌러보세요! (B 버튼으로 종료)", self.font_small, self.YELLOW, self.width//2, y)
                y += 30
                
                for msg in button_pressed:
                    y = self.render_text(msg, self.font_small, self.BLUE, self.width//2, y)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def show_message(self, message, duration):
        """메시지 표시"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            
            self.screen.fill(self.BLACK)
            self.render_text(message, self.font_medium, self.WHITE, self.width//2, self.height//2)
            pygame.display.flip()
            self.clock.tick(60)
    
    def draw_screen(self):
        """화면 그리기"""
        self.screen.fill(self.BLACK)
        
        # 타이틀
        y = 30
        y = self.render_text("*** D A W N   O F   S T E L L A R ***", self.font_large, self.GREEN, self.width//2, y)
        y = self.render_text("통합 런처 v3.3.0 - pygame BGM 버전", self.font_medium, self.YELLOW, self.width//2, y)
        y += 20
        
        # 설명
        y = self.render_text("[PAD] 게임패드 지원 + 최적화된 통합 런처", self.font_small, self.BLUE, self.width//2, y)
        y = self.render_text("[OPT] 오디오 파일 정리 완료 (558MB 절약!)", self.font_small, self.BLUE, self.width//2, y)
        
        # BGM 상태 표시
        bgm_status = "[BGM] 재생 중" if self.bgm_playing else "[---] BGM 정지됨"
        y = self.render_text(bgm_status, self.font_small, self.GREEN if self.bgm_playing else self.RED, self.width//2, y)
        y += 20
        
        # 게임패드 상태
        if self.joystick:
            y = self.render_text(f"게임패드: {self.joystick.get_name()}", self.font_small, self.GREEN, self.width//2, y)
        else:
            y = self.render_text("게임패드: 연결되지 않음", self.font_small, self.RED, self.width//2, y)
        
        y += 30
        
        # 옵션들
        for i, (option, desc) in enumerate(self.options):
            color = self.YELLOW if i == self.selected_option else self.WHITE
            y = self.render_text(f"[{i+1}] {option}", self.font_medium, color, self.width//2, y)
            
            if i == self.selected_option:
                y = self.render_text(f"    → {desc}", self.font_small, self.GREEN, self.width//2, y)
            
            y += 10
        
        # 컨트롤 가이드
        y += 30
        y = self.render_text("[CTRL] 컨트롤 가이드", self.font_medium, self.BLUE, self.width//2, y)
        
        if self.joystick:
            y = self.render_text("• A 버튼 / Enter: 선택", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text("• B 버튼 / ESC: 종료", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text("• 십자패드 / 스틱: 이동", self.font_small, self.WHITE, self.width//2, y)
        else:
            y = self.render_text("• 방향키 / WASD: 이동", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text("• Enter / Space: 선택", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text("• ESC: 종료", self.font_small, self.WHITE, self.width//2, y)
        
        y = self.render_text("• 숫자키 1-9: 직접 선택", self.font_small, self.WHITE, self.width//2, y)
        
        # 조작법
        y += 50
        y = self.render_text("조작법:", self.font_small, self.WHITE, self.width//2, y)
        y = self.render_text("키보드: ↑↓/WS 선택, Enter 실행, ESC 종료, 1-4 직접선택", self.font_small, self.WHITE, self.width//2, y)
        y = self.render_text("게임패드: X/Y 선택, A 실행, B 종료", self.font_small, self.WHITE, self.width//2, y)
        
        pygame.display.flip()
    
    def run(self):
        """메인 루프"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    result = self.handle_input(event)
                    if result is False:
                        running = False
            
            self.draw_screen()
            self.clock.tick(60)
        
        pygame.quit()
    
    def build_full_window(self):
        """전체 창 버전 빌드"""
        try:
            self.show_message("전체 창 버전을 빌드 중입니다... (잠시만 기다려주세요)", 2)
            
            cmd = [
                ".venv/Scripts/python.exe", "-m", "PyInstaller", 
                "--onefile", "--windowed", 
                "--name", "DawnOfStellar_FullWindow",
                "--add-data=main.py;.",
                "--add-data=config.py;.",
                "--add-data=story_system.py;.",
                "--add-data=python_launcher.py;.",
                "--add-data=game;game",
                "--add-data=assets;assets",
                "--add-data=Galmuri11.ttf;.",
                "--add-data=whitrabt.ttf;.",
                "--hidden-import=pygame",
                "--hidden-import=tkinter",
                "main_game_launcher.py"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists("dist/DawnOfStellar_FullWindow.exe"):
                self.show_message("빌드 완료! 전체 창 버전을 실행합니다...", 1)
                subprocess.Popen(["dist/DawnOfStellar_FullWindow.exe"])
            else:
                self.show_message("빌드 실패!", 3)
                
        except Exception as e:
            self.show_message(f"빌드 오류: {e}", 3)
    
    def build_test_game(self):
        """테스트 게임 빌드"""
        try:
            self.show_message("테스트 게임을 빌드 중입니다...", 2)
            
            cmd = [
                ".venv/Scripts/python.exe", "-m", "PyInstaller",
                "--onefile", "--windowed",
                "--name", "DawnOfStellar_SimpleTest",
                "--add-data=Galmuri11.ttf;.",
                "--hidden-import=pygame",
                "main_simple_test.py"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists("dist/DawnOfStellar_SimpleTest.exe"):
                self.show_message("빌드 완료! 테스트 게임을 실행합니다...", 1)
                subprocess.Popen(["dist/DawnOfStellar_SimpleTest.exe"])
            else:
                self.show_message("빌드 실패!", 3)
                
        except Exception as e:
            self.show_message(f"빌드 오류: {e}", 3)
    
    def build_gamepad_version(self):
        """게임패드 버전 빌드"""
        try:
            self.show_message("게임패드 버전을 빌드 중입니다...", 2)
            
            cmd = [
                ".venv/Scripts/python.exe", "-m", "PyInstaller",
                "--onefile", "--windowed",
                "--name", "DawnOfStellar_Gamepad",
                "--add-data=main.py;.",
                "--add-data=config.py;.",
                "--add-data=story_system.py;.",
                "--add-data=game;game",
                "--add-data=assets;assets",
                "--add-data=Galmuri11.ttf;.",
                "--add-data=whitrabt.ttf;.",
                "--hidden-import=pygame",
                "--hidden-import=tkinter",
                "main_pygame_wrapper.py"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists("dist/DawnOfStellar_Gamepad.exe"):
                self.show_message("빌드 완료! 게임패드 버전을 실행합니다...", 1)
                subprocess.Popen(["dist/DawnOfStellar_Gamepad.exe"])
            else:
                self.show_message("빌드 실패!", 3)
                
        except Exception as e:
            self.show_message(f"빌드 오류: {e}", 3)
    
    def show_build_menu(self):
        """빌드 메뉴 표시"""
        build_options = [
            "전체 창 버전 빌드",
            "테스트 게임 빌드", 
            "게임패드 버전 빌드",
            "모든 버전 빌드",
            "뒤로 가기"
        ]
        
        selected = 0
        while True:
            self.screen.fill(self.BLACK)
            
            y = 50
            y = self.render_text("PyInstaller 빌드 메뉴", self.font_large, self.GREEN, self.width//2, y)
            y += 50
            
            for i, option in enumerate(build_options):
                color = self.YELLOW if i == selected else self.WHITE
                y = self.render_text(f"[{i+1}] {option}", self.font_medium, color, self.width//2, y)
            
            y += 30
            y = self.render_text("화살표키로 선택, Enter로 실행", self.font_small, self.BLUE, self.width//2, y)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(build_options)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(build_options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:
                            self.build_full_window()
                            return
                        elif selected == 1:
                            self.build_test_game()
                            return
                        elif selected == 2:
                            self.build_gamepad_version()
                            return
                        elif selected == 3:
                            self.build_all_versions()
                            return
                        elif selected == 4:
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return
            
            self.clock.tick(60)
    
    def build_all_versions(self):
        """모든 버전 빌드"""
        self.show_message("모든 버전을 빌드합니다... (시간이 오래 걸립니다)", 2)
        self.build_full_window()
        self.build_test_game()
        self.build_gamepad_version()
        self.show_message("모든 빌드가 완료되었습니다!", 3)
    
    def launch_system_settings(self):
        """시스템 설정 및 고급 도구"""
        settings_running = True
        selected = 0
        
        settings_options = [
            "게임 캐시 정리",
            "오디오 파일 정리",
            "로그 파일 정리", 
            "세이브 파일 백업",
            "시스템 정보 확인",
            "폰트 설치 확인",
            "Python 환경 확인",
            "뒤로가기"
        ]
        
        while settings_running:
            self.screen.fill(self.BLACK)
            
            y = 50
            y = self.render_text("[SYS] 시스템 설정", self.font_large, self.GREEN, self.width//2, y)
            y += 30
            
            for i, option in enumerate(settings_options):
                color = self.YELLOW if i == selected else self.WHITE
                y = self.render_text(f"[{i+1}] {option}", self.font_medium, color, self.width//2, y)
            
            y += 30
            y = self.render_text("게임패드: A(선택) B(뒤로) | 키보드: Enter(선택) ESC(뒤로)", self.font_small, self.BLUE, self.width//2, y)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(settings_options)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(settings_options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:
                            self.clean_game_cache()
                        elif selected == 1:
                            self.clean_audio_files()
                        elif selected == 2:
                            self.clean_log_files()
                        elif selected == 3:
                            self.backup_save_files()
                        elif selected == 4:
                            self.show_system_info()
                        elif selected == 5:
                            self.check_fonts()
                        elif selected == 6:
                            self.check_python_env()
                        elif selected == 7:
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A 버튼
                        if selected == 7:
                            return
                        # 해당 기능 실행
                    elif event.button == 1:  # B 버튼
                        return
                elif event.type == pygame.JOYHATMOTION:
                    x, y_joy = event.value
                    if y_joy == 1:
                        selected = (selected - 1) % len(settings_options)
                    elif y_joy == -1:
                        selected = (selected + 1) % len(settings_options)
            
            self.clock.tick(60)
    
    def clean_game_cache(self):
        """게임 캐시 정리"""
        self.show_message("게임 캐시를 정리합니다...", 1)
        try:
            cache_dirs = ["__pycache__", ".pytest_cache", "build", "dist"]
            cleaned = 0
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    import shutil
                    shutil.rmtree(cache_dir)
                    cleaned += 1
            self.show_message(f"{cleaned}개 캐시 디렉토리 정리 완료!", 2)
        except Exception as e:
            self.show_message(f"캐시 정리 오류: {e}", 3)
    
    def clean_audio_files(self):
        """오디오 파일 정리 (안전한 버전)"""
        self.show_message("사용하지 않는 오디오 파일을 분석합니다...", 2)
        try:
            # 실제 사용되는 파일들만 확인하는 안전한 방식
            from pathlib import Path
            import json
            
            # 게임에서 실제 사용되는 BGM 목록 읽기
            used_files = set()
            
            # audio.py에서 매핑된 파일들 추출
            audio_file = Path("game/audio.py")
            if audio_file.exists():
                with open(audio_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # .mp3 파일명들 찾기
                    import re
                    mp3_files = re.findall(r'[\'"]([\d\w\s\-\.,!()]+\.mp3)[\'"]', content)
                    used_files.update(mp3_files)
            
            # 현재 BGM 디렉토리의 파일들 확인
            bgm_dir = Path("game/audio/bgm")
            total_files = len(list(bgm_dir.glob("*.mp3"))) if bgm_dir.exists() else 0
            used_count = len(used_files)
            
            self.show_message(f"전체: {total_files}개, 사용: {used_count}개 BGM 파일", 3)
            
        except Exception as e:
            self.show_message(f"분석 오류: {e}", 3)
    
    def clean_log_files(self):
        """로그 파일 정리"""
        self.show_message("로그 파일을 정리합니다...", 1)
        try:
            log_files = ["game_error.log", "debug.log", "combat_log.json"]
            cleaned = 0
            for log_file in log_files:
                if os.path.exists(log_file):
                    os.remove(log_file)
                    cleaned += 1
            self.show_message(f"{cleaned}개 로그 파일 정리 완료!", 2)
        except Exception as e:
            self.show_message(f"로그 정리 오류: {e}", 3)
    
    def backup_save_files(self):
        """세이브 파일 백업"""
        self.show_message("세이브 파일을 백업합니다...", 1)
        try:
            import shutil
            from datetime import datetime
            
            save_files = ["savegame.json", "config.json"]
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            backed_up = 0
            for save_file in save_files:
                if os.path.exists(save_file):
                    shutil.copy2(save_file, os.path.join(backup_dir, save_file))
                    backed_up += 1
                    
            self.show_message(f"{backed_up}개 파일을 {backup_dir}에 백업 완료!", 2)
        except Exception as e:
            self.show_message(f"백업 오류: {e}", 3)
    
    def show_system_info(self):
        """시스템 정보 표시"""
        info_running = True
        
        while info_running:
            self.screen.fill(self.BLACK)
            
            y = 50
            y = self.render_text("[PC] 시스템 정보", self.font_large, self.GREEN, self.width//2, y)
            y += 30
            
            y = self.render_text(f"OS: {platform.system()} {platform.release()}", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text(f"Python: {sys.version.split()[0]}", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text(f"pygame: {pygame.version.ver}", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text(f"화면 크기: {self.width}x{self.height}", self.font_small, self.WHITE, self.width//2, y)
            
            if self.joystick:
                y = self.render_text(f"게임패드: {self.joystick.get_name()}", self.font_small, self.GREEN, self.width//2, y)
            else:
                y = self.render_text("게임패드: 연결되지 않음", self.font_small, self.RED, self.width//2, y)
            
            y += 30
            y = self.render_text("ESC: 뒤로가기", self.font_small, self.BLUE, self.width//2, y)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    info_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        info_running = False
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 1:  # B 버튼
                        info_running = False
            
            self.clock.tick(60)
    
    def check_fonts(self):
        """폰트 설치 확인"""
        self.show_message("폰트 설치 상태를 확인합니다...", 1)
        font_status = []
        
        font_files = ["Galmuri11.ttf", "whitrabt.ttf"]
        for font_file in font_files:
            if os.path.exists(font_file):
                font_status.append(f"{font_file}: 설치됨")
            else:
                font_status.append(f"{font_file}: 없음")
        
        status_text = " | ".join(font_status)
        self.show_message(status_text, 3)
    
    def check_python_env(self):
        """Python 환경 확인"""
        self.show_message("Python 환경을 확인합니다...", 1)
        try:
            if pkg_resources:
                installed = [d.project_name for d in pkg_resources.working_set]
                required = ['pygame', 'numpy', 'requests']
                
                status = []
                for req in required:
                    if req in installed:
                        status.append(f"{req}: 설치됨")
                    else:
                        status.append(f"{req}: 없음")
                
                self.show_message(" | ".join(status), 3)
            else:
                self.show_message("pkg_resources 모듈이 없어 확인할 수 없습니다", 2)
        except Exception as e:
            self.show_message(f"환경 확인 오류: {e}", 3)
    
    def show_build_menu(self):
        """빌드 메뉴 표시"""
        build_options = [
            "전체 창 버전 빌드",
            "테스트 게임 빌드", 
            "게임패드 버전 빌드",
            "모든 버전 빌드",
            "뒤로 가기"
        ]
        
        selected = 0
        while True:
            self.screen.fill(self.BLACK)
            
            y = 50
            y = self.render_text("PyInstaller 빌드 메뉴", self.font_large, self.GREEN, self.width//2, y)
            y += 50
            
            for i, option in enumerate(build_options):
                color = self.YELLOW if i == selected else self.WHITE
                y = self.render_text(f"[{i+1}] {option}", self.font_medium, color, self.width//2, y)
            
            y += 30
            y = self.render_text("화살표키로 선택, Enter로 실행", self.font_small, self.BLUE, self.width//2, y)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(build_options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(build_options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:
                            self.build_full_window()
                        elif selected == 1:
                            self.build_test_game()
                        elif selected == 2:
                            self.build_gamepad_version()
                        elif selected == 3:
                            self.build_all_versions()
                        elif selected == 4:
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A 버튼
                        if selected == 0:
                            self.build_full_window()
                        elif selected == 1:
                            self.build_test_game()
                        elif selected == 2:
                            self.build_gamepad_version()
                        elif selected == 3:
                            self.build_all_versions()
                        elif selected == 4:
                            return
                    elif event.button == 1:  # B 버튼
                        return
                elif event.type == pygame.JOYHATMOTION:
                    x, y_joy = event.value
                    if y_joy == 1:
                        selected = (selected - 1) % len(build_options)
                    elif y_joy == -1:
                        selected = (selected + 1) % len(build_options)
            
            self.clock.tick(60)
    
    def build_all_versions(self):
        """모든 버전 빌드"""
        self.show_message("모든 버전을 빌드합니다... (시간이 오래 걸립니다)", 2)
        self.build_full_window()
        self.build_test_game()
        self.build_gamepad_version()
        self.show_message("모든 빌드가 완료되었습니다!", 3)
    
    def build_full_window(self):
        """전체 창 버전 빌드"""
        try:
            self.show_message("전체 창 버전을 빌드 중입니다... (잠시만 기다려주세요)", 2)
            
            cmd = [
                ".venv/Scripts/python.exe", "-m", "PyInstaller", 
                "--onefile", "--windowed", 
                "--name", "DawnOfStellar_FullWindow",
                "--add-data=main.py;.",
                "--add-data=config.py;.",
                "--add-data=game;game",
                "--add-data=assets;assets",
                "--add-data=Galmuri11.ttf;.",
                "--add-data=whitrabt.ttf;.",
                "--hidden-import=pygame",
                "--hidden-import=tkinter",
                "main_game_launcher.py"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists("dist/DawnOfStellar_FullWindow.exe"):
                self.show_message("빌드 완료! 전체 창 버전을 실행합니다...", 1)
                subprocess.Popen(["dist/DawnOfStellar_FullWindow.exe"])
            else:
                self.show_message("빌드 실패!", 3)
                
        except Exception as e:
            self.show_message(f"빌드 오류: {e}", 3)
    
    def build_test_game(self):
        """테스트 게임 빌드"""
        try:
            self.show_message("테스트 게임을 빌드 중입니다...", 2)
            
            cmd = [
                ".venv/Scripts/python.exe", "-m", "PyInstaller",
                "--onefile", "--windowed",
                "--name", "DawnOfStellar_SimpleTest",
                "--add-data=Galmuri11.ttf;.",
                "--hidden-import=pygame",
                "main_simple_test.py"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists("dist/DawnOfStellar_SimpleTest.exe"):
                self.show_message("빌드 완료! 테스트 게임을 실행합니다...", 1)
                subprocess.Popen(["dist/DawnOfStellar_SimpleTest.exe"])
            else:
                self.show_message("빌드 실패!", 3)
                
        except Exception as e:
            self.show_message(f"빌드 오류: {e}", 3)
    
    def build_gamepad_version(self):
        """게임패드 버전 빌드"""
        try:
            self.show_message("게임패드 버전을 빌드 중입니다...", 2)
            
            cmd = [
                ".venv/Scripts/python.exe", "-m", "PyInstaller",
                "--onefile", "--windowed",
                "--name", "DawnOfStellar_Gamepad",
                "--add-data=main.py;.",
                "--add-data=config.py;.",
                "--add-data=game;game",
                "--add-data=assets;assets",
                "--add-data=Galmuri11.ttf;.",
                "--add-data=whitrabt.ttf;.",
                "--hidden-import=pygame",
                "--hidden-import=tkinter",
                "main_pygame_wrapper.py"
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists("dist/DawnOfStellar_Gamepad.exe"):
                self.show_message("빌드 완료! 게임패드 버전을 실행합니다...", 1)
                subprocess.Popen(["dist/DawnOfStellar_Gamepad.exe"])
            else:
                self.show_message("빌드 실패!", 3)
                
        except Exception as e:
            self.show_message(f"빌드 오류: {e}", 3)
            
            self.clock.tick(60)
    
    def check_fonts(self):
        """폰트 설치 확인"""
        self.show_message("폰트 설치 상태를 확인합니다...", 1)
        font_status = []
        
        font_files = ["Galmuri11.ttf", "whitrabt.ttf"]
        for font_file in font_files:
            if os.path.exists(font_file):
                font_status.append(f"[OK] {font_file}")
            else:
                font_status.append(f"[NO] {font_file}")
        
        status_text = " | ".join(font_status)
        self.show_message(status_text, 3)
    
    def check_python_env(self):
        """Python 환경 확인"""
        self.show_message("Python 환경을 확인합니다...", 1)
        try:
            if pkg_resources:
                installed = [d.project_name for d in pkg_resources.working_set]
                required = ['pygame', 'numpy', 'requests']
                
                status = []
                for req in required:
                    if req.lower() in [p.lower() for p in installed]:
                        status.append(f"[OK]{req}")
                    else:
                        status.append(f"[NO]{req}")
                
                self.show_message(" | ".join(status), 3)
            else:
                self.show_message("pkg_resources 모듈이 없어 확인할 수 없습니다", 2)
        except Exception as e:
            self.show_message(f"환경 확인 오류: {e}", 3)
    
    def bgm_settings(self):
        """BGM 설정"""
        settings_running = True
        
        while settings_running:
            self.screen.fill(self.BLACK)
            
            y = 50
            y = self.render_text("[BGM] BGM 설정", self.font_large, self.GREEN, self.width//2, y)
            y += 30
            
            # 현재 상태 표시
            bgm_status = "재생 중" if self.bgm_playing else "정지됨"
            y = self.render_text(f"BGM 상태: {bgm_status}", self.font_medium, self.WHITE, self.width//2, y)
            y = self.render_text(f"BGM 볼륨: {int(self.bgm_volume * 100)}%", self.font_medium, self.WHITE, self.width//2, y)
            y = self.render_text(f"효과음 볼륨: {int(self.sfx_volume * 100)}%", self.font_medium, self.WHITE, self.width//2, y)
            y += 30
            
            # 조작법
            y = self.render_text("조작법:", self.font_medium, self.YELLOW, self.width//2, y)
            y = self.render_text("← → : BGM 볼륨 조절", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text("↑ ↓ : 효과음 볼륨 조절", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text("1,2,3 : 효과음 테스트 (hover, select, back)", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text("스페이스 : BGM 재생/정지", self.font_small, self.WHITE, self.width//2, y)
            y = self.render_text("ESC : 뒤로가기", self.font_small, self.WHITE, self.width//2, y)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_LEFT:
                        self.adjust_bgm_volume(-0.1)
                    elif event.key == pygame.K_RIGHT:
                        self.adjust_bgm_volume(0.1)
                    elif event.key == pygame.K_UP:
                        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + 0.1))
                    elif event.key == pygame.K_DOWN:
                        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume - 0.1))
                    elif event.key == pygame.K_SPACE:
                        if self.bgm_playing:
                            self.stop_bgm()
                        else:
                            self.start_bgm()
                    elif event.key == pygame.K_1:
                        self.play_sfx("button_hover")  # 효과음 테스트
                    elif event.key == pygame.K_2:
                        self.play_sfx("button_select")  # 효과음 테스트
                    elif event.key == pygame.K_3:
                        self.play_sfx("button_back")  # 효과음 테스트
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 1:  # B 버튼 (뒤로가기)
                        return
                    elif event.button == 0:  # A 버튼 (BGM 토글)
                        if self.bgm_playing:
                            self.stop_bgm()
                        else:
                            self.start_bgm()
                    elif event.button == 2:  # X 버튼 (효과음 테스트 1)
                        self.play_sfx("button_hover")
                    elif event.button == 3:  # Y 버튼 (효과음 테스트 2)
                        self.play_sfx("button_select")
                elif event.type == pygame.JOYHATMOTION:
                    x, y_joy = event.value
                    if x == -1:  # 왼쪽 (BGM 볼륨 감소)
                        self.adjust_bgm_volume(-0.1)
                    elif x == 1:  # 오른쪽 (BGM 볼륨 증가)
                        self.adjust_bgm_volume(0.1)
                    elif y_joy == 1:  # 위쪽 (효과음 볼륨 증가)
                        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + 0.1))
                    elif y_joy == -1:  # 아래쪽 (효과음 볼륨 감소)
                        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume - 0.1))
            
            self.clock.tick(60)

def main():
    """메인 함수"""
    try:
        launcher = GameLauncher()
        launcher.run()
    except Exception as e:
        print(f"오류 발생: {e}")
        input("계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    main()
