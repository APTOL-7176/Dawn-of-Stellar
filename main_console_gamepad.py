#!/usr/bin/env python3
"""
Dawn Of Stellar - 콘솔 유지 버전
게임패드 지원 + 콘솔 출력 정상화
"""

import sys
import os
import pygame
import time
import subprocess

# PyInstaller 환경 확인
if getattr(sys, 'frozen', False):
    # PyInstaller로 실행된 경우
    application_path = sys._MEIPASS
    os.environ['SDL_VIDEODRIVER'] = 'windib'
else:
    # 일반 Python으로 실행된 경우
    application_path = os.path.dirname(os.path.abspath(__file__))

def main():
    """메인 함수 - 콘솔에서 직접 게임 실행"""
    try:
        print("=== Dawn of Stellar - 게임패드 지원 버전 ===")
        print("게임을 시작합니다...")
        
        # 로그 파일 생성
        with open("gamepad_log.txt", "w", encoding="utf-8") as f:
            f.write("Dawn of Stellar - Console Mode Started\n")
            f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
        
        # 게임패드 초기화 확인
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"게임패드 감지됨: {joystick.get_name()}")
            with open("gamepad_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Gamepad detected: {joystick.get_name()}\n")
        else:
            print("게임패드가 감지되지 않았습니다. 키보드로 플레이하세요.")
        
        pygame.quit()
        
        # 실제 게임 모듈 로드
        import importlib.util
        
        # PyInstaller 환경에서 main.py 경로 찾기
        if getattr(sys, 'frozen', False):
            main_py_path = os.path.join(sys._MEIPASS, "main.py")
        else:
            main_py_path = "main.py"
        
        print(f"게임 모듈 로드 중: {main_py_path}")
        
        with open("gamepad_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Loading main.py from: {main_py_path}\n")
        
        spec = importlib.util.spec_from_file_location("game_main", main_py_path)
        game_main_module = importlib.util.module_from_spec(spec)
        
        spec.loader.exec_module(game_main_module)
        
        # 게임 실행
        print("Dawn of Stellar 시작!")
        print("=" * 50)
        
        with open("gamepad_log.txt", "a", encoding="utf-8") as f:
            f.write("Starting game main...\n")
        
        # 게임 실행
        game_main_module.main()
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        with open("gamepad_error.txt", "w", encoding="utf-8") as f:
            f.write(f"Game start error: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        input("오류가 발생했습니다. Enter를 눌러 종료하세요...")

if __name__ == "__main__":
    main()
