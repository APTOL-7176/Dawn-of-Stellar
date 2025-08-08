#!/usr/bin/env python3
"""
가장 간단한 테스트 - PyInstaller 호환성 확인
"""

import sys
import os
import time

def main():
    """간단한 테스트 메인 함수"""
    try:
        print("=== Dawn of Stellar 초기화 테스트 ===")
        
        # 1. 기본 환경 확인
        print(f"Python 버전: {sys.version}")
        print(f"실행 경로: {os.getcwd()}")
        print(f"PyInstaller 모드: {getattr(sys, 'frozen', False)}")
        
        if getattr(sys, 'frozen', False):
            print(f"임시 폴더: {sys._MEIPASS}")
        
        # 2. 필수 모듈 테스트
        print("\n=== 모듈 import 테스트 ===")
        
        try:
            import pygame
            print("✅ pygame 로드 성공")
        except Exception as e:
            print(f"❌ pygame 로드 실패: {e}")
        
        try:
            import tkinter
            print("✅ tkinter 로드 성공")
        except Exception as e:
            print(f"❌ tkinter 로드 실패: {e}")
        
        # 3. 파일 존재 확인
        print("\n=== 파일 존재 확인 ===")
        files_to_check = ["main.py", "config.py", "story_system.py"]
        for file in files_to_check:
            if os.path.exists(file):
                print(f"✅ {file} 존재")
            else:
                print(f"❌ {file} 없음")
        
        # 4. 게임 폴더 확인
        if os.path.exists("game"):
            print("✅ game 폴더 존재")
            game_files = os.listdir("game")[:5]  # 처음 5개만
            print(f"게임 파일들: {game_files}")
        else:
            print("❌ game 폴더 없음")
        
        print("\n=== 테스트 완료 ===")
        print("5초 후 종료됩니다...")
        
        # PyInstaller 환경에서는 메시지박스로 결과 표시
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("테스트 완료", "초기화 테스트가 완료되었습니다.\n\n콘솔 창을 확인하세요.")
                root.destroy()
            except:
                pass
        
        time.sleep(5)
        
    except Exception as e:
        error_msg = f"테스트 중 오류 발생: {e}"
        print(error_msg)
        
        # 오류 로그 저장
        try:
            with open("test_error.log", "w", encoding="utf-8") as f:
                import traceback
                f.write(f"{error_msg}\n\n{traceback.format_exc()}")
        except:
            pass
        
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("테스트 오류", f"테스트 중 오류가 발생했습니다:\n\n{error_msg}")
                root.destroy()
            except:
                pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
