#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dawn of Stellar - 통합 Python 런처 v3.0.0
게임패드 안전 모드 + 모든 기능 통합 + 커서 메뉴 + SFX/BGM
마지막 업데이트: 2025년 8월 9일
"""

import os
import sys
import time
import shutil
import subprocess
import webbrowser
import glob
import threading
import platform
import json
from datetime import datetime

# 오디오 시스템 임포트 (선택적)
try:
    import pygame
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ pygame이 설치되지 않았습니다. 오디오 기능이 비활성화됩니다.")

class LauncherAudio:
    """런처 전용 오디오 시스템"""
    
    def __init__(self):
        self.enabled = AUDIO_AVAILABLE
        self.bgm_channel = None
        self.sfx_channel = None
        
        if self.enabled:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.load_sounds()
            except Exception as e:
                self.enabled = False
    
    def load_sounds(self):
        """사운드 파일 로드 - 실제 파일 구조에 맞게"""
        try:
            # BGM (런처용 - FF7 음악 사용)
            launcher_bgm_candidates = [
                "game/audio/bgm/13-Flowers Blooming in the Church.mp3",  # 평화로운 음악
            ]
            
            self.launcher_bgm = None
            for bgm_path in launcher_bgm_candidates:
                if os.path.exists(bgm_path):
                    try:
                        self.launcher_bgm = pygame.mixer.Sound(bgm_path)
                        break
                    except:
                        continue
            
            # SFX (게임과 동일한 매핑 사용)
            sfx_mapping = {
                'cursor': 'game/audio/sfx/000.wav',     # menu_select - 커서 이동
                'select': 'game/audio/sfx/000.wav',     # menu_select - 커서 이동  
                'confirm': 'game/audio/sfx/001.wav',    # menu_confirm - 확인
                'cancel': 'game/audio/sfx/003.wav',     # menu_cancel - 취소
                'startup': None                         # 시작음 없음
            }
            
            self.sfx = {}
            for name, path in sfx_mapping.items():
                if path and os.path.exists(path):
                    try:
                        self.sfx[name] = pygame.mixer.Sound(path)
                    except Exception as e:
                        self.sfx[name] = None
                else:
                    self.sfx[name] = None
                    
        except Exception as e:
            self.enabled = False
            print(f"오디오 로드 실패: {e}")
    
    def play_bgm(self, fade_in=True):
        """BGM 재생"""
        if not self.enabled or not self.launcher_bgm:
            return
        
        try:
            if fade_in:
                self.bgm_channel = pygame.mixer.Sound.play(self.launcher_bgm, loops=-1)
                self.bgm_channel.set_volume(0.0)
                self.fade_in_bgm()
            else:
                self.bgm_channel = pygame.mixer.Sound.play(self.launcher_bgm, loops=-1)
                self.bgm_channel.set_volume(0.3)
        except:
            pass
    
    def fade_in_bgm(self):
        """BGM 페이드 인"""
        def fade():
            if not self.bgm_channel:
                return
            for i in range(31):
                try:
                    volume = i / 100.0  # 0.0 to 0.3
                    self.bgm_channel.set_volume(volume)
                    time.sleep(0.05)
                except:
                    break
        
        threading.Thread(target=fade, daemon=True).start()
    
    def fade_out_bgm(self):
        """BGM 페이드 아웃"""
        def fade():
            if not self.bgm_channel:
                return
            for i in range(30, -1, -1):
                try:
                    volume = i / 100.0
                    self.bgm_channel.set_volume(volume)
                    time.sleep(0.05)
                except:
                    break
            try:
                if self.bgm_channel:
                    self.bgm_channel.stop()
            except:
                pass
        
        threading.Thread(target=fade, daemon=True).start()
    
    def stop_bgm(self):
        """BGM 정지"""
        if self.bgm_channel:
            try:
                self.bgm_channel.stop()
            except:
                pass
    
    def play_sfx(self, sound_name):
        """SFX 재생"""
        if not self.enabled or sound_name not in self.sfx or not self.sfx[sound_name]:
            return
        
        try:
            self.sfx[sound_name].play()
        except:
            pass

class CursorMenu:
    """커서 기반 메뉴 시스템"""
    
    def __init__(self, audio_system=None):
        self.audio = audio_system
        self.cursor_pos = 0
        self.menu_items = []
        self.title = ""
        self.subtitle = ""
        
    def set_menu(self, title, subtitle, items):
        """메뉴 설정"""
        self.title = title
        self.subtitle = subtitle
        self.menu_items = items
        self.cursor_pos = 0
    
    def draw_ascii_art(self):
        """간단한 ASCII 아트 출력"""
        art = """
    ════════════════════════════════════════════════════════════════
               🌟 Dawn of Stellar - 통합 Python 런처 🌟
                      별들의 새벽 - 로그라이크 RPG
    ════════════════════════════════════════════════════════════════
        """
        return art
    
    def draw_menu(self):
        """메뉴 그리기"""
        clear_screen()
        set_console_font()
        
        # 아스키 아트
        print(self.draw_ascii_art())
        
        # 제목과 부제목
        print(f"\n📋 {self.title}")
        print("═" * (len(self.title) + 4))
        if self.subtitle:
            print(f"💡 {self.subtitle}")
        print()
        
        # 메뉴 항목들
        for i, (key, label, desc) in enumerate(self.menu_items):
            cursor = "► " if i == self.cursor_pos else "  "
            if i == self.cursor_pos:
                color = "\033[93m"  # 노란색 (선택됨)
                label_color = "\033[97m\033[1m"  # 밝은 흰색 + 굵게
            else:
                color = "\033[96m"  # 청록색 (일반)
                label_color = "\033[37m"  # 회색
            
            print(f"{color}{cursor}[{key}] {label_color}{label}\033[0m")
            if desc and i == self.cursor_pos:
                print(f"     \033[90m💭 {desc}\033[0m")
        
        print("\n" + "─" * 70)
        print("🎮 조작법: \033[93mW/S\033[0m 이동  │  \033[92mEnter\033[0m 선택  │  \033[91mESC\033[0m 종료  │  \033[94m숫자/문자\033[0m 직접선택")
        
        # 시스템 정보 표시
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        print(f"\n\033[90m📊 시스템: Python {python_version} │ {platform.system()} │ {current_time}\033[0m")
        
        # 오디오 상태 표시
        if hasattr(self, 'audio') and self.audio and self.audio.enabled:
            print("\033[90m🎵 오디오: 활성화됨\033[0m")
        else:
            print("\033[90m🔇 오디오: 비활성화됨\033[0m")
    
    def get_input(self):
        """키보드 입력 처리 - 입력 버퍼 정리 포함"""
        if os.name == 'nt':
            import msvcrt
            
            # 입력 버퍼 비우기 (중복 입력 방지)
            while msvcrt.kbhit():
                msvcrt.getch()
            
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    
                    # 입력 후 잠시 대기 (중복 입력 방지)
                    time.sleep(0.1)
                    
                    if key == b'\xe0':  # 화살표 키
                        key = msvcrt.getch()
                        if key == b'H':  # ↑
                            self.cursor_pos = (self.cursor_pos - 1) % len(self.menu_items)
                            if self.audio:
                                self.audio.play_sfx('cursor')
                            return 'UP'
                        elif key == b'P':  # ↓
                            self.cursor_pos = (self.cursor_pos + 1) % len(self.menu_items)
                            if self.audio:
                                self.audio.play_sfx('cursor')
                            return 'DOWN'
                    
                    elif key == b'\r':  # Enter
                        if self.audio:
                            self.audio.play_sfx('confirm')
                        return 'SELECT'
                    
                    elif key == b'\x1b':  # ESC
                        if self.audio:
                            self.audio.play_sfx('cancel')
                        return 'EXIT'
                    
                    elif key in [b'w', b'W']:  # W키로 위로 이동
                        self.cursor_pos = (self.cursor_pos - 1) % len(self.menu_items)
                        if self.audio:
                            self.audio.play_sfx('cursor')
                        return 'UP'
                    
                    elif key in [b's', b'S']:  # S키로 아래로 이동
                        self.cursor_pos = (self.cursor_pos + 1) % len(self.menu_items)
                        if self.audio:
                            self.audio.play_sfx('cursor')
                        return 'DOWN'
                    
                    elif key.isdigit() or key.isalpha():
                        # 직접 키 입력
                        char = key.decode('utf-8').upper()
                        for i, (menu_key, _, _) in enumerate(self.menu_items):
                            if menu_key == char:
                                self.cursor_pos = i
                                if self.audio:
                                    self.audio.play_sfx('select')
                                return 'SELECT'
                
                time.sleep(0.05)
        else:
            # Linux/Mac용 간단한 입력
            try:
                choice = input("\n선택하세요: ").strip().upper()
                for i, (menu_key, _, _) in enumerate(self.menu_items):
                    if menu_key == choice:
                        self.cursor_pos = i
                        return 'SELECT'
                return 'EXIT'
            except KeyboardInterrupt:
                return 'EXIT'
    
    def get_selected_key(self):
        """선택된 메뉴 키 반환"""
        if 0 <= self.cursor_pos < len(self.menu_items):
            return self.menu_items[self.cursor_pos][0]
        return None
    
    def run(self):
        """메뉴 실행"""
        while True:
            self.draw_menu()
            action = self.get_input()
            
            if action == 'SELECT':
                return self.get_selected_key()
            elif action == 'EXIT':
                return '0'

def clear_screen():
    """화면 클리어"""
    os.system('cls' if os.name == 'nt' else 'clear')

def set_console_font():
    """콘솔 폰트 설정 (UTF-8 지원)"""
    if os.name == 'nt':
        os.system('chcp 65001 > nul')

def set_gamepad_safe_environment():
    """게임패드 안전 환경 설정"""
    os.environ['DISABLE_GAMEPAD'] = '1'
    os.environ['TERMINAL_MODE'] = '1'
    os.environ['SDL_GAMECONTROLLER_IGNORE_DEVICES'] = '1'
    os.environ['SDL_JOYSTICK_DEVICE'] = ''

def get_python_exe():
    """Python 실행파일 경로 찾기"""
    # 가상환경 확인
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return sys.executable
    
    # .venv 폴더 확인
    venv_python = None
    if os.name == 'nt':
        venv_python = os.path.join('.venv', 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join('.venv', 'bin', 'python')
    
    if os.path.exists(venv_python):
        return venv_python
    
    # 시스템 Python
    return 'python'

def get_pip_exe():
    """pip 실행파일 경로 찾기"""
    python_exe = get_python_exe()
    
    # Python 실행파일에서 pip 경로 유추
    if python_exe.endswith('python.exe') or python_exe.endswith('python'):
        pip_exe = python_exe.replace('python.exe', 'pip.exe').replace('python', 'pip')
        if os.path.exists(pip_exe):
            return pip_exe
    
    # pip를 직접 찾기
    if shutil.which('pip'):
        return 'pip'
    
    # python -m pip 사용
    return [python_exe, '-m', 'pip']

def show_main_menu():
    """메인 메뉴 표시 (커서 메뉴 버전)"""
    audio = LauncherAudio()
    menu = CursorMenu(audio)
    
    # 시작 사운드
    if audio.enabled:
        audio.play_sfx('startup')
        time.sleep(0.5)
        audio.play_bgm(fade_in=True)
    
    # 메뉴 구성 (더 체계적으로 분류)
    menu_items = [
        # 🎮 게임 실행 섹션
        ("1", "⚡ EXE 게임 실행", "빌드된 실행파일로 게임 시작 (최고 성능, 권장)"),
        ("2", "🎮 Python 게임 실행", "소스코드로 직접 게임 실행 (개발자 모드 지원)"),
        ("3", "📱 Flutter 모바일 앱", "Flutter로 개발된 모바일/웹/데스크톱 크로스플랫폼 앱"),
        
        # 🔧 개발 도구 섹션  
        ("4", "📦 게임 빌드", "EXE 파일 생성 및 패키징"),
        ("5", "🔧 폰트 도구", "폰트 주입 및 설정 유틸리티"),
        ("6", "🚀 빠른 설정", "환경 설정 및 패키지 업데이트"),
        
        # 🛠️ 시스템 관리 섹션
        ("7", "🔄 게임 업데이트", "Git을 통한 최신 버전 업데이트"),
        ("8", "🔄 패키지 복구", "손상된 패키지 복구 및 재설치"),
        ("9", "🧹 캐시 정리", "임시 파일 및 캐시 정리"),
        
        # ⚠️ 고급 작업 섹션
        ("A", "⚠️ 완전 재설치", "모든 데이터 삭제 후 재설치"),
        ("B", "📊 시스템 정보", "시스템 및 환경 정보 확인"),
        ("C", "🎵 오디오 테스트", "오디오 시스템 상태 확인"),
        
        # 🚪 종료
        ("0", "❌ 종료", "런처 종료")
    ]
    
    # 구분선 제거한 실제 메뉴 항목만 필터링
    actual_items = [(k, l, d) for k, l, d in menu_items if k != ""]
    
    menu.set_menu(
        "🌟 Dawn of Stellar - 통합 Python 런처 v3.0.0",
        "멋진 모험이 당신을 기다립니다! (W/S로 이동, Enter로 선택)",
        actual_items
    )
    
    return menu, audio

def select_game_mode(audio_system=None):
    """게임 모드 선택 (개발모드/일반모드) - 커서 메뉴 방식"""
    # 모드 선택용 메뉴 구성
    mode_items = [
        ("1", "⚡ 일반 모드", "정상적인 게임 플레이"),
        ("2", "🔧 개발자 모드", "디버그 정보 표시"),
        ("3", "🔙 돌아가기", "메인 메뉴로 돌아가기")
    ]
    
    # 커서 메뉴 생성 (오디오 시스템 전달)
    mode_menu = CursorMenu(audio_system)
    mode_menu.set_menu(
        "🎮 Dawn of Stellar - 게임 모드 선택",
        "W/S로 이동, Enter로 선택, ESC로 취소",
        mode_items
    )
    
    while True:
        choice = mode_menu.run()
        
        if choice == "1":
            return False  # 일반모드
        elif choice == "2":
            return True   # 개발모드
        elif choice == "3" or choice == "0":
            return None   # 취소
        else:
            # 잘못된 선택 시 다시 선택
            continue

def run_game_in_new_process(mode, dev_mode=False, mobile_mode=False):
    """게임을 새 프로세스에서 실행 후 런처 종료"""
    set_console_font()
    
    # 환경 변수 설정
    env = os.environ.copy()
    env['DISABLE_GAMEPAD'] = '1'
    env['TERMINAL_MODE'] = '1'
    env['SDL_GAMECONTROLLER_IGNORE_DEVICES'] = '1'
    env['SDL_JOYSTICK_DEVICE'] = ''
    
    if dev_mode:
        env['DEV_MODE'] = '1'
    if mobile_mode:
        env['MOBILE_MODE'] = '1'
    
    python_exe = get_python_exe()
    
    # 절대 경로로 변환
    if not os.path.isabs(python_exe):
        python_exe = os.path.abspath(python_exe)
    
    try:
        if os.name == 'nt':
            # Windows에서 새 콘솔 창에서 실행 - 간단한 배치파일 방식
            batch_file = "temp_game_launcher.bat"
            batch_content = f"""@echo off
chcp 65001 >nul 2>&1
cd /d "{os.getcwd()}"
"{python_exe}" main.py
pause
del "%~f0"
"""
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            # 배치파일을 새 창에서 실행
            subprocess.Popen(['cmd', '/c', 'start', batch_file], env=env)
        else:
            # Linux/Mac에서 새 터미널에서 실행
            subprocess.run([
                'gnome-terminal', '--', 'bash', '-c',
                f'cd "{os.getcwd()}" && "{python_exe}" main.py; read -p "Press any key to continue..."'
            ], env=env)
        
        # 게임 실행 후 런처 종료
        print("\n🎮 게임이 새 창에서 실행됩니다...")
        print("👋 런처를 종료합니다.")
        time.sleep(2)
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ 게임 실행 실패: {e}")
        print("대신 현재 터미널에서 실행합니다...")
        subprocess.run([python_exe, 'main.py'], env=env)
        # 현재 터미널에서 실행한 경우에도 종료
        sys.exit(0)

def run_exe_game(audio_system=None):
    """빌드된 EXE 파일로 게임 실행"""
    # 모드 선택
    dev_mode = select_game_mode(audio_system)
    if dev_mode is None:
        return  # 취소
    
    clear_screen()
    print()
    print("⚡ Dawn of Stellar EXE 실행")
    print("=" * 50)
    print()
    
    # EXE 파일 존재 확인
    exe_path = os.path.join("dist", "DawnOfStellar.exe")
    if not os.path.exists(exe_path):
        # 이전 이름으로도 시도
        alt_exe_path = os.path.join("dist", "DawnOfStellar_Fixed.exe")
        if os.path.exists(alt_exe_path):
            exe_path = alt_exe_path
        else:
            print("❌ 빌드된 EXE 파일을 찾을 수 없습니다.")
            print(f"   시도한 경로: {exe_path}")
            print(f"   대체 경로: {alt_exe_path}")
            print("\n💡 EXE 파일을 생성하시겠습니까?")
            print("[Y] 네, 지금 빌드하기")
            print("[N] 아니오, 메뉴로 돌아가기")
            
            choice = input("\n선택하세요 (Y/N): ").strip().upper()
            if choice == 'Y':
                print("\n📦 게임을 빌드합니다...")
                time.sleep(1)
                build_game()
                return
            else:
                return
    
    print("✅ EXE 파일을 찾았습니다!")
    print(f"   경로: {exe_path}")
    
    try:
        file_size = os.path.getsize(exe_path)
        print(f"   크기: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
    except:
        pass
    
    print()
    
    try:
        if dev_mode:
            print("🤯 개발자 모드로 실행합니다...")
        else:
            print("🎯 일반 모드로 실행합니다...")
        
        # 환경 변수 설정
        env = os.environ.copy()
        if dev_mode:
            env['DEV_MODE'] = '1'
        
        # 절대 경로로 변환
        exe_path = os.path.abspath(exe_path)
        
        print(f"🚀 게임 시작: {os.path.basename(exe_path)}")
        
        # EXE 파일 직접 실행
        subprocess.Popen([exe_path], env=env, cwd=os.path.dirname(exe_path))
        
        print("✅ 게임이 실행되었습니다!")
        print("창이 보이지 않으면 작업 표시줄을 확인해보세요.")
        print("👋 런처를 종료합니다.")
        print()
        time.sleep(2)
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ EXE 실행 실패: {e}")
        print("\n계속하려면 아무 키나 누르세요...")
        input()

def run_mobile_app():
    """Flutter 모바일 앱 실행"""
    clear_screen()
    print()
    print("📱 Dawn of Stellar v3.0.0 - Flutter 모바일 앱")
    print("=" * 60)
    print()
    
    # Flutter 모바일 폴더 확인
    flutter_path = "flutter_mobile"
    if not os.path.exists(flutter_path):
        print("❌ Flutter 모바일 폴더를 찾을 수 없습니다.")
        print(f"   경로: {os.path.abspath(flutter_path)}")
        print("\n💡 Flutter 모바일 앱을 설치하려면:")
        print("   1. Flutter SDK 설치")
        print("   2. flutter_mobile 폴더 확인")
        print("   3. flutter pub get 실행")
        input("\n아무 키나 누르세요...")
        return
    
    print("� Flutter 환경 확인 중...")
    
    # Flutter 설치 확인
    flutter_check = subprocess.run(["flutter", "--version"], 
                                 capture_output=True, text=True, shell=True)
    
    if flutter_check.returncode != 0:
        print("❌ Flutter SDK가 설치되지 않았습니다.")
        print("\n📥 Flutter 설치가 필요합니다:")
        print("   1. https://flutter.dev/docs/get-started/install")
        print("   2. Flutter SDK 다운로드 및 설치")
        print("   3. PATH 환경변수 설정")
        print("\n� 또는 기존 설치된 Flutter를 사용하시겠습니까?")
        
        choice = input("Y: 계속 진행 / N: 취소 (Y/N): ").strip().upper()
        if choice != 'Y':
            return
    else:
        print("✅ Flutter SDK 설치 확인됨")
        print(f"   버전: {flutter_check.stdout.strip().split()[1] if flutter_check.stdout else 'Unknown'}")
    
    print("\n📦 Flutter 모바일 앱 설정 중...")
    
    # Flutter 프로젝트 디렉토리로 이동
    original_dir = os.getcwd()
    
    try:
        os.chdir(flutter_path)
        
        # pubspec.yaml 확인
        if os.path.exists("pubspec.yaml"):
            print("✅ pubspec.yaml 발견")
            
            # 의존성 설치
            print("📦 Flutter 패키지 설치 중...")
            pub_get = subprocess.run(["flutter", "pub", "get"], 
                                   capture_output=True, text=True, shell=True)
            
            if pub_get.returncode == 0:
                print("✅ Flutter 패키지 설치 완료")
            else:
                print("⚠️ 패키지 설치 중 오류 발생:")
                print(pub_get.stderr)
        
        print("\n🎮 실행 방법을 선택하세요:")
        print()
        print("📱 모바일 옵션:")
        print("   [1] Android 에뮬레이터 (Android Studio)")
        print("   [2] 연결된 Android 기기")
        print("   [3] iOS 시뮬레이터 (macOS 전용)")
        print()
        print("🌐 데스크톱 옵션:")
        print("   [4] 웹 브라우저 (Chrome)")
        print("   [5] Windows 데스크톱 앱")
        print("   [6] Linux 데스크톱 앱")
        print()
        print("🔙 기타:")
        print("   [0] 취소")
        print()
        
        choice = input("선택하세요 (0-6): ").strip()
        
        if choice == "1":
            print("\n📱 Android 에뮬레이터로 실행 중...")
            subprocess.run(["flutter", "run", "-d", "android"], shell=True)
            
        elif choice == "2":
            print("\n� 연결된 Android 기기로 실행 중...")
            # 연결된 기기 확인
            devices = subprocess.run(["flutter", "devices"], 
                                   capture_output=True, text=True, shell=True)
            print("🔍 연결된 기기:")
            print(devices.stdout)
            subprocess.run(["flutter", "run"], shell=True)
            
        elif choice == "3":
            print("\n📱 iOS 시뮬레이터로 실행 중...")
            subprocess.run(["flutter", "run", "-d", "ios"], shell=True)
            
        elif choice == "4":
            print("\n🌐 웹 브라우저로 실행 중...")
            subprocess.run(["flutter", "run", "-d", "chrome"], shell=True)
            
        elif choice == "5":
            print("\n🖥️ Windows 데스크톱 앱으로 실행 중...")
            subprocess.run(["flutter", "run", "-d", "windows"], shell=True)
            
        elif choice == "6":
            print("\n🖥️ Linux 데스크톱 앱으로 실행 중...")
            subprocess.run(["flutter", "run", "-d", "linux"], shell=True)
            
        elif choice == "0":
            print("실행이 취소되었습니다.")
            
        else:
            print("❌ 잘못된 선택입니다.")
            
    except Exception as e:
        print(f"❌ Flutter 앱 실행 중 오류 발생: {e}")
        
    finally:
        # 원래 디렉토리로 복귀
        os.chdir(original_dir)
    
    input("\n아무 키나 누르세요...")

def build_game():
    """게임 빌드 (EXE 생성)"""
    clear_screen()
    print()
    print("📦 Dawn Of Stellar v3.0.0 빌드 시작")
    print("=" * 50)
    print()
    
    # Python 환경 확인
    print("[1/6] Python 환경 확인 중...")
    try:
        result = subprocess.run([get_python_exe(), "--version"], capture_output=True, text=True)
        print(f"✅ Python 버전: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ ERROR: Python 실행 실패: {e}")
        input("아무 키나 누르세요...")
        return
    
    # 빌드 도구 설치
    print("\n[2/6] 빌드 도구 설치 중...")
    pip_exe = get_pip_exe()
    if isinstance(pip_exe, list):
        result = subprocess.run(pip_exe + ["install", "pyinstaller"])
    else:
        result = subprocess.run([pip_exe, "install", "pyinstaller"])
    
    if result.returncode != 0:
        print("❌ ERROR: PyInstaller 설치에 실패했습니다.")
        input("아무 키나 누르세요...")
        return
    
    # 빌드 디렉토리 정리
    print("\n[3/6] 빌드 디렉토리 정리 중...")
    for folder in ["dist", "build"]:
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
    
    # __pycache__ 정리
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
    
    # 게임 실행파일 빌드
    print("\n[4/6] 게임 실행파일 빌드 중...")
    python_exe = get_python_exe()
    
    # PyInstaller용 최적화된 메인 파일 확인
    main_file = "main_pyinstaller_final.py"
    if not os.path.exists(main_file):
        print(f"❌ ERROR: {main_file}을 찾을 수 없습니다.")
        print("PyInstaller용 최적화된 메인 파일이 필요합니다.")
        input("아무 키나 누르세요...")
        return
    
    # 운영체제별 경로 구분자 설정
    sep = ";" if os.name == 'nt' else ":"
    
    # 빌드 모드 선택 (커서 메뉴 방식)
    build_items = [
        ("1", "🔧 개발용 빌드", "콘솔창 표시 - 디버깅 용이"),
        ("2", "🎯 배포용 빌드", "콘솔창 숨김 - 사용자 친화적")
    ]
    
    # 커서 메뉴 생성
    build_menu = CursorMenu(None)  # 빌드 선택에는 오디오 없음
    build_menu.set_menu(
        "📦 빌드 모드 선택",
        "W/S로 이동, Enter로 선택",
        build_items
    )
    
    mode_choice = build_menu.run()
    
    if mode_choice == "1":
        # 개발용 - 콘솔 모드
        build_mode = "--console"
        mode_name = "개발용"
        print("🔧 개발용 빌드 선택 - 콘솔창이 표시됩니다")
    elif mode_choice == "2":
        # 배포용 - 윈도우 모드
        build_mode = "--windowed"
        mode_name = "배포용"
        print("🎯 배포용 빌드 선택 - 콘솔창이 숨겨집니다")
    else:
        # 취소된 경우
        print("빌드가 취소되었습니다.")
        input("아무 키나 누르세요...")
        return
    
    print()
    
    # Assets 폴더 확인 (대소문자 구분)
    assets_folder = "Assets" if os.path.exists("Assets") else "assets"
    
    # 폰트 파일 확인 및 포함
    font_args = []
    if os.path.exists("Galmuri11.ttf"):
        font_args.extend([f"--add-data=Galmuri11.ttf{sep}."])
    if os.path.exists("whitrabt.ttf"):
        font_args.extend([f"--add-data=whitrabt.ttf{sep}."])
    
    build_cmd = [
        python_exe, "-m", "PyInstaller", 
        "--onefile", 
        build_mode,  # 선택된 빌드 모드
        "--name", "DawnOfStellar",  # 전체화면 최종 버전
        f"--add-data=main.py{sep}.",           # main.py 포함
        f"--add-data=config.py{sep}.",         # config.py 포함
        f"--add-data=story_system.py{sep}.",   # story_system.py 포함
        f"--add-data=game{sep}game",           # game 폴더 포함
        f"--add-data={assets_folder}{sep}assets",  # assets 폴더 포함
        *font_args,                            # 폰트 파일들 포함
        "--hidden-import", "pygame",           # pygame 명시적 포함
        "--hidden-import", "tkinter",          # tkinter 명시적 포함
        main_file  # PyInstaller용 최적화된 메인 파일
    ]
    
    print(f"빌드 명령 ({mode_name}): {' '.join(build_cmd)}")
    
    try:
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 빌드 성공!")
            print(f"실행파일 생성됨: dist/DawnOfStellar.exe ({mode_name} 모드)")
        else:
            print("❌ 빌드 실패!")
            print("에러 출력:")
            print(result.stderr)
            print("\n일반 출력:")
            print(result.stdout)
            input("아무 키나 누르세요...")
            return
            
    except Exception as e:
        print(f"❌ 빌드 중 예외 발생: {e}")
        input("아무 키나 누르세요...")
        return
    
    # 추가 리소스 복사 (saves 폴더 등)
    print("\n[5/6] 추가 리소스 복사 중...")
    if os.path.exists("dist"):
        # saves 폴더 복사 (세이브 파일 보존)
        if os.path.exists("saves"):
            shutil.copytree("saves", "dist/saves", dirs_exist_ok=True)
            print("  ✅ 세이브 파일 복사 완료")
    
    # 게임 실행
    print("\n[6/6] 게임 실행 중...")
    exe_path = "dist/DawnOfStellar.exe"
    
    if os.path.exists(exe_path):
        print(f"게임 실행: {exe_path}")
        try:
            subprocess.Popen([exe_path], cwd=os.getcwd())
            print("✅ 게임이 성공적으로 시작되었습니다!")
            print("창이 뜨지 않으면 작업 표시줄을 확인해보세요.")
            print()
            print("📋 빌드 정보:")
            print("✅ 실행파일: dist/DawnOfStellar.exe")
            print("✅ 리소스: 자동 포함됨 (game/, assets/)")
            print("✅ 세이브: dist/saves/ (복사됨)")
            print("✅ 윈도우 모드: 터미널 없이 실행")
        except Exception as e:
            print(f"❌ 게임 실행 실패: {e}")
    else:
        print(f"❌ 실행파일을 찾을 수 없습니다: {exe_path}")
    
    print()
    input("아무 키나 누르세요...")

def run_font_tool():
    """폰트 주입 도구 실행"""
    clear_screen()
    print()
    print("🔧 폰트 주입 도구를 실행합니다...")
    print()
    
    python_exe = get_python_exe()
    if os.path.exists("font_injector.py"):
        subprocess.run([python_exe, "font_injector.py"])
    else:
        print("❌ font_injector.py 파일을 찾을 수 없습니다.")
    
    input("아무 키나 누르세요...")

def show_build_instructions():
    """빌드 안내 표시"""
    clear_screen()
    print("🏗️  빌드 안내")
    print("=" * 50)
    print("현재 사용 가능한 빌드 옵션:")
    print("• PyInstaller EXE: 완료 (DawnOfStellar.exe)")
    print("• Flutter 모바일 앱: 개발 중")
    print("• Electron 웹앱: 계획 중")
    input("\n아무 키나 누르세요...")

def show_audio_status():
    """오디오 상태 표시"""
    clear_screen()
    print("🎵 오디오 시스템 상태")
    print("=" * 50)
    bgm_path = "game/audio/bgm"
    sfx_path = "game/audio/sfx"
    
    if os.path.exists(bgm_path):
        bgm_files = len([f for f in os.listdir(bgm_path) if f.endswith('.mp3')])
        print(f"✅ BGM 파일: {bgm_files}개")
    else:
        print("❌ BGM 폴더 없음")
    
    if os.path.exists(sfx_path):
        sfx_files = len([f for f in os.listdir(sfx_path) if f.endswith('.wav')])
        print(f"✅ SFX 파일: {sfx_files}개")
    else:
        print("❌ SFX 폴더 없음")
    
    print(f"📁 BGM 경로: {os.path.abspath(bgm_path)}")
    print(f"📁 SFX 경로: {os.path.abspath(sfx_path)}")
    input("\n아무 키나 누르세요...")

def setup_development_environment():
    """개발 환경 설정"""
    clear_screen()
    print("🔧 개발 환경 설정")
    print("=" * 50)
    print("이 기능은 개발 중입니다.")
    print("현재는 auto_install.bat를 사용하세요.")
    input("\n아무 키나 누르세요...")

def run_tests():
    """테스트 실행"""
    clear_screen()
    print("🧪 테스트 실행")
    print("=" * 50)
    print("이 기능은 개발 중입니다.")
    input("\n아무 키나 누르세요...")

def system_maintenance():
    """시스템 유지보수"""
    clear_screen()
    print("🔧 시스템 유지보수")
    print("=" * 50)
    print("이 기능은 개발 중입니다.")
    input("\n아무 키나 누르세요...")

def create_backup():
    """백업 생성"""
    clear_screen()
    print("💾 백업 생성")
    print("=" * 50)
    print("이 기능은 개발 중입니다.")
    input("\n아무 키나 누르세요...")

def system_info():
    """시스템 정보 표시"""
    clear_screen()
    print()
    print("📊 Dawn of Stellar - 시스템 정보")
    print("=" * 60)
    print()
    
    # 기본 시스템 정보
    print("🖥️  시스템 정보:")
    print(f"   운영체제: {platform.system()} {platform.release()} ({platform.architecture()[0]})")
    print(f"   컴퓨터명: {platform.node()}")
    print(f"   Python 버전: {sys.version}")
    print(f"   Python 경로: {sys.executable}")
    print()
    
    # 현재 작업 환경
    print("📁 작업 환경:")
    print(f"   현재 디렉토리: {os.getcwd()}")
    python_exe = get_python_exe()
    print(f"   사용 중인 Python: {python_exe}")
    
    # 가상환경 확인
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"   가상환경: 활성화됨 ({sys.prefix})")
    else:
        print("   가상환경: 비활성화됨")
    print()
    
    # 게임 파일 확인
    print("🎮 게임 파일 상태:")
    essential_files = ["main.py", "config.py", "game/", "requirements.txt"]
    for file in essential_files:
        if os.path.exists(file):
            if os.path.isdir(file):
                file_count = len([f for f in os.listdir(file) if f.endswith('.py')])
                print(f"   ✅ {file} (Python 파일: {file_count}개)")
            else:
                file_size = os.path.getsize(file)
                print(f"   ✅ {file} ({file_size:,} bytes)")
        else:
            print(f"   ❌ {file} (없음)")
    print()
    
    # 빌드 파일 확인
    print("📦 빌드 파일:")
    if os.path.exists("dist"):
        exe_files = [f for f in os.listdir("dist") if f.endswith('.exe')]
        if exe_files:
            for exe in exe_files:
                exe_path = os.path.join("dist", exe)
                exe_size = os.path.getsize(exe_path)
                print(f"   ✅ {exe} ({exe_size:,} bytes, {exe_size/(1024*1024):.1f} MB)")
        else:
            print("   📂 dist 폴더 존재하나 EXE 파일 없음")
    else:
        print("   ❌ dist 폴더 없음 (빌드 필요)")
    print()
    
    # 패키지 정보
    print("📦 설치된 주요 패키지:")
    try:
        import pkg_resources
        installed_packages = {d.project_name.lower(): d.version for d in pkg_resources.working_set}
        
        important_packages = ["pygame", "colorama", "requests", "flask", "pyinstaller", "pillow"]
        for package in important_packages:
            if package in installed_packages:
                print(f"   ✅ {package}: v{installed_packages[package]}")
            else:
                print(f"   ❌ {package}: 설치되지 않음")
    except ImportError:
        print("   ⚠️ pkg_resources를 사용할 수 없습니다.")
    print()
    
    # 오디오 시스템 상태
    print("🎵 오디오 시스템:")
    if AUDIO_AVAILABLE:
        try:
            import pygame
            pygame.mixer.init()
            print(f"   ✅ pygame 오디오 지원: v{pygame.version.ver}")
            
            # 오디오 파일 확인
            bgm_count = 0
            sfx_count = 0
            
            if os.path.exists("game/audio/bgm"):
                bgm_count = len([f for f in os.listdir("game/audio/bgm") if f.endswith(('.mp3', '.wav', '.ogg'))])
            
            if os.path.exists("game/audio/sfx"):
                sfx_count = len([f for f in os.listdir("game/audio/sfx") if f.endswith(('.mp3', '.wav', '.ogg'))])
            
            print(f"   🎵 BGM 파일: {bgm_count}개")
            print(f"   🔊 SFX 파일: {sfx_count}개")
        except Exception as e:
            print(f"   ⚠️ pygame 초기화 실패: {e}")
    else:
        print("   ❌ pygame 설치되지 않음 (오디오 비활성화)")
    
    print()
    input("📋 아무 키나 누르면 메뉴로 돌아갑니다...")

def audio_test():
    """오디오 테스트"""
    clear_screen()
    print()
    print("🎵 Dawn of Stellar - 오디오 테스트")
    print("=" * 50)
    print()
    
    if not AUDIO_AVAILABLE:
        print("❌ pygame이 설치되지 않아 오디오 테스트를 할 수 없습니다.")
        print("   pip install pygame 명령으로 설치해주세요.")
        input("\n아무 키나 누르세요...")
        return
    
    # 오디오 시스템 초기화
    try:
        test_audio = LauncherAudio()
        if not test_audio.enabled:
            print("❌ 오디오 시스템 초기화에 실패했습니다.")
            input("\n아무 키나 누르세요...")
            return
        
        print("✅ 오디오 시스템이 성공적으로 초기화되었습니다.")
        print()
        
        # BGM 테스트
        print("🎵 BGM 테스트:")
        if test_audio.launcher_bgm:
            print("   ✅ BGM 파일 로드됨")
            print("   🎵 BGM 재생 중... (3초)")
            test_audio.play_bgm(fade_in=False)
            time.sleep(3)
            test_audio.stop_bgm()
            print("   ⏹️ BGM 정지")
        else:
            print("   ❌ BGM 파일을 찾을 수 없습니다.")
        print()
        
        # SFX 테스트
        print("🔊 SFX 테스트:")
        sfx_tests = [
            ('cursor', '커서 이동음'),
            ('select', '선택음'),
            ('confirm', '확인음'),
            ('cancel', '취소음')
        ]
        
        for sfx_name, description in sfx_tests:
            if test_audio.sfx.get(sfx_name):
                print(f"   🔊 {description} 재생...")
                test_audio.play_sfx(sfx_name)
                time.sleep(0.5)
            else:
                print(f"   ❌ {description} 파일 없음")
        
        print("\n✅ 오디오 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 오디오 테스트 중 오류 발생: {e}")
    
    input("\n아무 키나 누르세요...")

def quick_setup():
    """빠른 설정 및 업데이트"""
    clear_screen()
    print()
    print("🚀 빠른 설정 및 업데이트를 실행합니다...")
    print()
    
    python_exe = get_python_exe()
    pip_exe = get_pip_exe()
    
    print("🔧 빠른 설정 실행 중...")
    if os.path.exists("quick_font_setup.py"):
        subprocess.run([python_exe, "quick_font_setup.py"])
    
    print("\n📦 패키지 업데이트 확인 중...")
    if isinstance(pip_exe, list):
        subprocess.run(pip_exe + ["install", "--upgrade", "pip"])
        if os.path.exists("requirements.txt"):
            subprocess.run(pip_exe + ["install", "-r", "requirements.txt"])
    else:
        subprocess.run([pip_exe, "install", "--upgrade", "pip"])
        if os.path.exists("requirements.txt"):
            subprocess.run([pip_exe, "install", "-r", "requirements.txt"])
    
    print("\n✅ 설정 완료!")
    input("아무 키나 누르세요...")

def complete_reinstall():
    """완전 재설치 (세이브 파일 포함 모든 데이터 삭제)"""
    clear_screen()
    print()
    print("� Dawn of Stellar 완전 재설치")
    print("=" * 50)
    print()
    print("⚠️  경고: 이 작업은 다음을 수행합니다:")
    print("   - 모든 세이브 파일 삭제")
    print("   - 게임 설정 초기화") 
    print("   - 가상환경 재생성")
    print("   - 모든 패키지 재설치")
    print("   - 캐시 및 임시파일 정리")
    print()
    print("🗑️  삭제될 데이터:")
    print("   - saves/ 폴더 (모든 세이브 파일)")
    print("   - .venv/ 폴더 (가상환경)")
    print("   - __pycache__/ 폴더들 (캐시)")
    print("   - *.pyc 파일들")
    print("   - config 파일들")
    print()
    
    # 첫 번째 확인
    confirm1 = input("⚠️  정말로 모든 데이터를 삭제하고 재설치하시겠습니까? (Y/N): ").lower()
    if confirm1 != 'y':
        print("재설치가 취소되었습니다.")
        input("아무 키나 누르세요...")
        return
    
    # 두 번째 확인 (더 강력한 확인)
    print("\n🔥 마지막 경고!")
    print("모든 게임 진행도와 세이브 파일이 영구적으로 삭제됩니다!")
    confirm2 = input("계속하려면 'DELETE ALL'을 정확히 입력하세요: ")
    if confirm2 != 'DELETE ALL':
        print("재설치가 취소되었습니다.")
        input("아무 키나 누르세요...")
        return
    
    print("\n🚀 완전 재설치를 시작합니다...")
    
    # 1단계: 세이브 파일 삭제
    print("\n[1/7] 세이브 파일 삭제 중...")
    if os.path.exists("saves"):
        shutil.rmtree("saves", ignore_errors=True)
        print("  ✅ saves/ 폴더 삭제 완료")
    else:
        print("  ℹ️  saves/ 폴더가 없습니다.")
    
    # 2단계: 가상환경 삭제
    print("\n[2/7] 가상환경 삭제 중...")
    if os.path.exists(".venv"):
        shutil.rmtree(".venv", ignore_errors=True)
        print("  ✅ .venv/ 폴더 삭제 완료")
    else:
        print("  ℹ️  .venv/ 폴더가 없습니다.")
    
    # 3단계: 캐시 정리
    print("\n[3/7] 캐시 및 임시파일 정리 중...")
    for root, dirs, files in os.walk("."):
        # __pycache__ 폴더 삭제
        for d in dirs[:]:
            if d == "__pycache__":
                full_path = os.path.join(root, d)
                shutil.rmtree(full_path, ignore_errors=True)
                dirs.remove(d)
        
        # .pyc 파일 삭제
        for f in files:
            if f.endswith(".pyc"):
                full_path = os.path.join(root, f)
                try:
                    os.remove(full_path)
                except:
                    pass
    print("  ✅ 캐시 정리 완료")
    
    # 4단계: 새 가상환경 생성
    print("\n[4/7] 새 가상환경 생성 중...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("  ✅ 가상환경 생성 완료")
    except Exception as e:
        print(f"  ❌ 가상환경 생성 실패: {e}")
        input("아무 키나 누르세요...")
        return
    
    # 5단계: pip 업그레이드
    print("\n[5/7] pip 업그레이드 중...")
    pip_exe = get_pip_exe()
    try:
        if isinstance(pip_exe, list):
            subprocess.run(pip_exe + ["install", "--upgrade", "pip"], check=True)
        else:
            subprocess.run([pip_exe, "install", "--upgrade", "pip"], check=True)
        print("  ✅ pip 업그레이드 완료")
    except Exception as e:
        print(f"  ⚠️  pip 업그레이드 실패: {e}")
    
    # 6단계: 필수 패키지 재설치
    print("\n[6/7] 필수 패키지 재설치 중...")
    packages = [
        "pygame", "colorama", "requests", 
        "flask", "flask-cors", "pyyaml", 
        "cryptography", "pillow", "pyinstaller"
    ]
    
    for package in packages:
        print(f"  - {package} 설치 중...")
        try:
            if isinstance(pip_exe, list):
                subprocess.run(pip_exe + ["install", package], check=True, capture_output=True)
            else:
                subprocess.run([pip_exe, "install", package], check=True, capture_output=True)
        except Exception as e:
            print(f"    ⚠️ {package} 설치 실패: {e}")
    
    # requirements.txt 재설치
    if os.path.exists("requirements.txt"):
        print("  - requirements.txt 재설치 중...")
        try:
            if isinstance(pip_exe, list):
                subprocess.run(pip_exe + ["install", "-r", "requirements.txt"], check=True)
            else:
                subprocess.run([pip_exe, "install", "-r", "requirements.txt"], check=True)
        except Exception as e:
            print(f"    ⚠️ requirements.txt 설치 실패: {e}")
    
    print("  ✅ 패키지 재설치 완료")
    
    # 7단계: 게임 환경 초기화
    print("\n[7/7] 게임 환경 초기화 중...")
    if os.path.exists("initial_setup.py"):
        try:
            subprocess.run([get_python_exe(), "initial_setup.py"])
            print("  ✅ 초기 설정 완료")
        except Exception as e:
            print(f"  ⚠️ 초기 설정 실패: {e}")
    else:
        print("  ℹ️  initial_setup.py가 없습니다.")
    
    # 새로운 saves 폴더 생성
    os.makedirs("saves", exist_ok=True)
    print("  ✅ 새 saves/ 폴더 생성")
    
    print("\n🎉 완전 재설치가 완료되었습니다!")
    print()
    print("✅ 재설치된 구성 요소:")
    print("   - 새로운 가상환경")
    print("   - 모든 필수 패키지")
    print("   - 초기화된 게임 설정")
    print("   - 빈 세이브 폴더")
    print()
    print("🎮 이제 새 게임으로 시작할 수 있습니다!")
    print()
    input("아무 키나 누르세요...")

def update_game():
    """게임 업데이트 - 안전장치 포함"""
    clear_screen()
    print()
    print("🔄 게임 업데이트")
    print("=" * 60)
    print()
    
    print("⚠️  경고: Git 업데이트는 로컬 변경사항을 덮어쓸 수 있습니다!")
    print("=" * 60)
    print()
    
    # Git 상태 확인
    if shutil.which("git"):
        print("🔍 현재 Git 상태 확인 중...")
        
        # 변경사항 확인
        status_result = subprocess.run(["git", "status", "--porcelain"], 
                                     capture_output=True, text=True)
        
        if status_result.stdout.strip():
            print("❌ 커밋되지 않은 로컬 변경사항이 있습니다:")
            print("─" * 50)
            print(status_result.stdout)
            print("─" * 50)
            print()
            print("🛡️  안전한 업데이트 옵션:")
            print("   1. 변경사항 백업 후 업데이트")
            print("   2. 변경사항 무시하고 강제 업데이트")
            print("   3. 업데이트 취소")
            print()
            
            choice = input("선택하세요 (1/2/3): ").strip()
            
            if choice == "1":
                print("\n💾 변경사항 백업 중...")
                backup_dir = f"backup_{int(time.time())}"
                os.makedirs(backup_dir, exist_ok=True)
                
                # 변경된 파일들 백업
                changed_files = status_result.stdout.strip().split('\n')
                for line in changed_files:
                    if len(line) > 3:
                        file_path = line[3:]  # 상태 코드 제거
                        try:
                            if os.path.exists(file_path):
                                backup_path = os.path.join(backup_dir, file_path)
                                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                                shutil.copy2(file_path, backup_path)
                                print(f"   ✅ {file_path} 백업 완료")
                        except Exception as e:
                            print(f"   ⚠️ {file_path} 백업 실패: {e}")
                
                print(f"\n✅ 백업 완료: {backup_dir} 폴더")
                
                # 변경사항 초기화 후 업데이트
                print("\n🔄 로컬 변경사항 초기화 중...")
                subprocess.run(["git", "reset", "--hard", "HEAD"])
                subprocess.run(["git", "clean", "-fd"])
                
            elif choice == "2":
                print("\n⚠️ 강제 업데이트를 진행합니다...")
                print("📝 모든 로컬 변경사항이 사라집니다!")
                
                final_confirm = input("정말로 계속하시겠습니까? (yes/no): ").strip().lower()
                if final_confirm != "yes":
                    print("업데이트가 취소되었습니다.")
                    input("아무 키나 누르세요...")
                    return
                
                subprocess.run(["git", "reset", "--hard", "HEAD"])
                subprocess.run(["git", "clean", "-fd"])
                
            else:
                print("업데이트가 취소되었습니다.")
                input("아무 키나 누르세요...")
                return
        
        print("\n📥 Git을 통한 업데이트 시도 중...")
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Git 업데이트 완료!")
            if "Already up to date" in result.stdout:
                print("💡 이미 최신 버전입니다.")
            else:
                print("🆕 새로운 업데이트가 적용되었습니다.")
        else:
            print("⚠️ Git 업데이트 실패:")
            print(result.stderr)
            print("\n수동 업데이트가 필요할 수 있습니다.")
    else:
        print("⚠️ Git이 설치되지 않았습니다.")
        print("   수동 다운로드만 가능합니다.")
    
    print("\n📦 패키지 업데이트 중...")
    pip_exe = get_pip_exe()
    if isinstance(pip_exe, list):
        subprocess.run(pip_exe + ["install", "--upgrade", "pip"])
        if os.path.exists("requirements.txt"):
            subprocess.run(pip_exe + ["install", "--upgrade", "-r", "requirements.txt"])
    else:
        subprocess.run([pip_exe, "install", "--upgrade", "pip"])
        if os.path.exists("requirements.txt"):
            subprocess.run([pip_exe, "install", "--upgrade", "-r", "requirements.txt"])
    
    print("\n✅ 업데이트 완료!")
    input("아무 키나 누르세요...")

def reinstall_packages():
    """패키지 재설치 및 복구"""
    clear_screen()
    print()
    print("🔄 패키지 재설치 및 복구")
    print("=" * 50)
    print()
    print("모든 Python 패키지를 재설치합니다...")
    print("이는 패키지 충돌이나 손상된 설치를 복구합니다.")
    print()
    
    confirm = input("계속하시겠습니까? (Y/N): ").lower()
    if confirm != 'y':
        return
    
    pip_exe = get_pip_exe()
    
    print("\n[1/4] pip 업그레이드...")
    if isinstance(pip_exe, list):
        subprocess.run(pip_exe + ["install", "--upgrade", "pip"])
    else:
        subprocess.run([pip_exe, "install", "--upgrade", "pip"])
    
    print("\n[2/4] 캐시 정리...")
    if isinstance(pip_exe, list):
        subprocess.run(pip_exe + ["cache", "purge"], capture_output=True)
    else:
        subprocess.run([pip_exe, "cache", "purge"], capture_output=True)
    
    print("\n[3/4] 필수 패키지 재설치...")
    packages = ["pygame", "colorama", "requests", "flask", "flask-cors"]
    if isinstance(pip_exe, list):
        subprocess.run(pip_exe + ["install", "--force-reinstall"] + packages)
    else:
        subprocess.run([pip_exe, "install", "--force-reinstall"] + packages)
    
    print("\n[4/4] requirements.txt 재설치...")
    if os.path.exists("requirements.txt"):
        if isinstance(pip_exe, list):
            subprocess.run(pip_exe + ["install", "--force-reinstall", "-r", "requirements.txt"])
        else:
            subprocess.run([pip_exe, "install", "--force-reinstall", "-r", "requirements.txt"])
    
    print("\n✅ 패키지 재설치가 완료되었습니다!")
    input("아무 키나 누르세요...")

def clean_cache():
    """캐시 정리"""
    clear_screen()
    print()
    print("🧹 캐시 정리")
    print("=" * 50)
    print()
    
    print("🗑️ Python 캐시 정리 중...")
    for root, dirs, files in os.walk("."):
        # __pycache__ 폴더 삭제
        for d in dirs[:]:
            if d == "__pycache__":
                full_path = os.path.join(root, d)
                print(f"  - {full_path}")
                shutil.rmtree(full_path, ignore_errors=True)
                dirs.remove(d)
        
        # .pyc 파일 삭제
        for f in files:
            if f.endswith(".pyc"):
                full_path = os.path.join(root, f)
                print(f"  - {full_path}")
                os.remove(full_path)
    
    print("\n📦 pip 캐시 정리 중...")
    pip_exe = get_pip_exe()
    if isinstance(pip_exe, list):
        subprocess.run(pip_exe + ["cache", "purge"], capture_output=True)
    else:
        subprocess.run([pip_exe, "cache", "purge"], capture_output=True)
    
    print("\n🗑️ 임시 파일 정리 중...")
    temp_patterns = ["*.tmp", "*.log", "*.bak"]
    for pattern in temp_patterns:
        for file in glob.glob(pattern):
            print(f"  - {file}")
            os.remove(file)
    
    print("\n✅ 캐시 정리가 완료되었습니다!")
    input("아무 키나 누르세요...")

def main():
    """메인 함수 - 커서 메뉴 시스템"""
    # 시작 시 게임패드 안전 환경 설정
    set_gamepad_safe_environment()
    
    # 오디오 및 메뉴 시스템 초기화
    menu, audio = show_main_menu()
    
    try:
        while True:
            choice = menu.run()
            
            # BGM 페이드 아웃 (실제 게임 시작 시에만)
            if choice in ["1", "2", "3"] and audio:
                audio.fade_out_bgm()
                time.sleep(0.5)
            
            if choice == "1":
                # EXE 게임 실행 (권장)
                print("\n⚡ EXE 게임을 시작합니다...")
                if audio:
                    audio.play_sfx('confirm')
                run_exe_game(audio)
                if audio:
                    audio.play_bgm(fade_in=True)
            
            elif choice == "2":
                # Python 게임 시작 - 모드 선택
                dev_mode = select_game_mode(audio)
                if dev_mode is not None:
                    print(f"\n🎮 {'개발자' if dev_mode else '일반'} 모드로 게임을 시작합니다...")
                    if audio:
                        audio.play_sfx('confirm')
                        audio.fade_out_bgm()
                    time.sleep(1)
                    run_game_in_new_process("normal", dev_mode=dev_mode)
                # 게임 종료 후 BGM 재시작
                if audio:
                    audio.play_bgm(fade_in=True)
            
            elif choice == "3":
                if audio:
                    audio.play_sfx('confirm')
                    audio.fade_out_bgm()
                run_mobile_app()
                if audio:
                    audio.play_bgm(fade_in=True)
            
            elif choice == "4":
                if audio:
                    audio.play_sfx('confirm')
                    audio.fade_out_bgm()
                build_game()
                if audio:
                    audio.play_bgm(fade_in=True)
            
            elif choice == "5":
                if audio:
                    audio.play_sfx('confirm')
                run_font_tool()
                input("아무 키나 누르세요...")
            
            elif choice == "6":
                if audio:
                    audio.play_sfx('confirm')
                quick_setup()
            
            elif choice == "7":
                if audio:
                    audio.play_sfx('confirm')
                update_game()
            
            elif choice == "8":
                if audio:
                    audio.play_sfx('confirm')
                reinstall_packages()
            
            elif choice == "9":
                if audio:
                    audio.play_sfx('confirm')
                clean_cache()
            
            elif choice == "A":
                if audio:
                    audio.play_sfx('select')
                complete_reinstall()
            
            elif choice == "B":
                if audio:
                    audio.play_sfx('confirm')
                system_info()
            
            elif choice == "C":
                if audio:
                    audio.play_sfx('confirm')
                audio_test()
            
            elif choice == "0":
                if audio:
                    audio.play_sfx('cancel')
                    audio.fade_out_bgm()
                clear_screen()
                print("\n👋 Dawn of Stellar 런처를 종료합니다.")
                print("🌟 별들이 당신을 기다리고 있습니다!")
                time.sleep(2)
                break
            
            else:
                if audio:
                    audio.play_sfx('cancel')
                print(f"\n❌ 잘못된 선택: {choice}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        if audio:
            audio.stop_bgm()
        clear_screen()
        print("\n👋 런처를 종료합니다.")
    except Exception as e:
        if audio:
            audio.stop_bgm()
        print(f"\n❌ 오류 발생: {e}")
        time.sleep(2)

if __name__ == "__main__":
    main()
