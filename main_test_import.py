#!/usr/bin/env python3
"""
main.py import 테스트
"""

import sys
import os
import time

def main():
    """main.py import 테스트"""
    try:
        print("=== main.py import 테스트 ===")
        
        # sys.path에 현재 디렉토리 추가
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        print("1. main.py 파일 확인...")
        main_py_path = os.path.join(current_dir, "main.py")
        if os.path.exists(main_py_path):
            print(f"✅ main.py 존재: {main_py_path}")
            
            # 파일 크기 확인
            size = os.path.getsize(main_py_path)
            print(f"파일 크기: {size:,} bytes")
        else:
            print(f"❌ main.py 없음: {main_py_path}")
            return
        
        print("2. main.py import 시도...")
        
        # importlib를 사용한 안전한 import
        import importlib.util
        spec = importlib.util.spec_from_file_location("game_main", main_py_path)
        if spec is None:
            print("❌ spec 생성 실패")
            return
        
        print("3. 모듈 생성...")
        game_main_module = importlib.util.module_from_spec(spec)
        
        print("4. 모듈 실행 시도...")
        # 이 부분에서 문제가 발생할 가능성이 높음
        spec.loader.exec_module(game_main_module)
        
        print("5. ✅ main.py import 성공!")
        
        # main 함수 존재 확인
        if hasattr(game_main_module, 'main'):
            print("✅ main 함수 발견")
        else:
            print("❌ main 함수 없음")
        
        print("\n=== import 테스트 완료 ===")
        
        # PyInstaller 환경에서는 메시지박스로 결과 표시
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("import 테스트 완료", "main.py import가 성공했습니다!")
                root.destroy()
            except:
                pass
        
        time.sleep(3)
        
    except Exception as e:
        error_msg = f"import 테스트 중 오류 발생: {e}"
        print(error_msg)
        
        # 상세 오류 정보
        import traceback
        detailed_error = traceback.format_exc()
        print("\n상세 오류:")
        print(detailed_error)
        
        # 오류 로그 저장
        try:
            with open("import_error.log", "w", encoding="utf-8") as f:
                f.write(f"{error_msg}\n\n{detailed_error}")
            print("오류 로그가 import_error.log에 저장되었습니다.")
        except:
            pass
        
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("import 오류", f"main.py import 중 오류가 발생했습니다:\n\n{str(e)}")
                root.destroy()
            except:
                pass
        
        time.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    main()
