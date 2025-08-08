#!/usr/bin/env python3
"""
Dawn Of Stellar - 최종 PyInstaller 메인 파일 (완전 간소화)
"""

import sys
import os

# PyInstaller 환경 확인
if getattr(sys, 'frozen', False):
    # PyInstaller로 실행된 경우 - 전체화면 설정
    application_path = sys._MEIPASS
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    # 전체화면 모드 설정
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
    os.environ['SDL_VIDEO_CENTERED'] = '0'
    # 전체화면 강제 설정
    os.environ['SDL_VIDEO_FULLSCREEN_HEAD'] = '0'
else:
    # 일반 Python으로 실행된 경우
    application_path = os.path.dirname(os.path.abspath(__file__))

def main():
    """메인 함수"""
    import sys  # sys import 추가
    debug_log = []
    
    # 즉시 로그 파일 생성
    try:
        with open("startup_log.txt", "w", encoding="utf-8") as f:
            f.write("Dawn of Stellar 시작됨\n")
    except:
        pass
    
    # PyInstaller 환경에서 터미널 강제 활성화
    if getattr(sys, 'frozen', False):
        import subprocess
        # 새 콘솔 창 열기
        try:
            subprocess.call(['cmd', '/c', 'title Dawn of Stellar'])
        except:
            pass
    
    try:
        debug_log.append("Dawn of Stellar 로딩 중...")
        print("Dawn of Stellar 로딩 중...")
        # 안전한 플러시
        try:
            if sys.stdout and hasattr(sys.stdout, 'flush'):
                sys.stdout.flush()
        except:
            pass
        
        # 로그 저장
        try:
            with open("step1_log.txt", "w", encoding="utf-8") as f:
                f.write("Step 1: 시작 완료\n")
        except:
            pass
        
        debug_log.append("게임 모듈 임포트 시작...")
        print("게임 모듈 임포트 시작...")
        
        # sys.path에 현재 디렉토리 추가
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 로그 저장
        try:
            with open("step2_log.txt", "w", encoding="utf-8") as f:
                f.write(f"Step 2: 경로 설정 완료\ncurrent_dir: {current_dir}\n")
        except:
            pass
        
        debug_log.append("main.py 임포트 중...")
        print("main.py 임포트 중...")
        
        # 기본 게임 모듈 임포트 (루트 디렉토리의 main.py)
        import importlib.util
        spec = importlib.util.spec_from_file_location("game_main", os.path.join(current_dir, "main.py"))
        game_main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(game_main_module)
        
        # 로그 저장
        try:
            with open("step3_log.txt", "w", encoding="utf-8") as f:
                f.write("Step 3: main.py 임포트 완료\n")
        except:
            pass
        
        debug_log.append("게임 실행 시작...")
        print("게임 실행 시작...")
        debug_log.append("DEBUG: 게임 메인 함수 호출 전")
        print("DEBUG: 게임 메인 함수 호출 전")
        
        # 게임 실행
        result = game_main_module.main()
        
        debug_log.append("DEBUG: 게임 메인 함수 호출 후")
        print("DEBUG: 게임 메인 함수 호출 후")
        debug_log.append(f"DEBUG: 게임 반환값: {result}")
        print(f"DEBUG: 게임 반환값: {result}")
        debug_log.append("게임이 정상적으로 종료되었습니다.")
        print("게임이 정상적으로 종료되었습니다.")
        
        # 디버그 로그를 파일에 저장
        with open("debug_log.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(debug_log))
        
        # PyInstaller 환경에서는 대기 시간 추가
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                
                # 게임 종료 안내 메시지
                messagebox.showinfo("Dawn of Stellar", 
                    "🎮 게임을 플레이해주셔서 감사합니다!\n\n" +
                    "Dawn of Stellar이 정상적으로 종료되었습니다.\n" +
                    "다시 게임을 즐기시려면 exe 파일을 다시 실행해주세요.")
                
                root.destroy()
                    
            except:
                # tkinter가 없으면 콘솔에서 대기
                try:
                    input("\n🎮 게임이 종료되었습니다. 아무 키나 누르세요...")
                except:
                    import time
                    time.sleep(3)  # 3초 대기
        
    except Exception as e:
        import traceback
        error_msg = f"게임 실행 중 오류 발생:\n{str(e)}\n\n상세 오류:\n{traceback.format_exc()}"
        print(error_msg)
        
        # 오류 로그 저장
        try:
            with open("game_error.log", "w", encoding="utf-8") as f:
                f.write(error_msg)
        except:
            pass
        
        # PyInstaller 환경에서는 오류 대화상자 표시
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Dawn of Stellar 오류", 
                    "게임 실행 중 오류가 발생했습니다.\n\n" +
                    "자세한 내용은 game_error.log 파일을 확인하세요.")
                root.destroy()
            except:
                pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
