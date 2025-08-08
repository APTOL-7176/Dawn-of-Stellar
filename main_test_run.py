#!/usr/bin/env python3
"""
main() 함수 호출 테스트
"""

import sys
import os
import time

def main():
    """main() 함수 호출 테스트"""
    try:
        print("=== main() 함수 호출 테스트 ===")
        
        # sys.path에 현재 디렉토리 추가
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        print("1. main.py import...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("game_main", os.path.join(current_dir, "main.py"))
        game_main_module = importlib.util.module_from_spec(spec)
        
        # 중요: stdout/stderr 버퍼 문제 해결을 위한 설정
        if getattr(sys, 'frozen', False):
            # PyInstaller 환경에서 버퍼 문제 방지
            try:
                if sys.stdout and hasattr(sys.stdout, 'flush'):
                    sys.stdout.flush()
                if sys.stderr and hasattr(sys.stderr, 'flush'):
                    sys.stderr.flush()
            except:
                pass
        
        print("2. 모듈 실행...")
        spec.loader.exec_module(game_main_module)
        print("✅ import 완료")
        
        print("3. main() 함수 호출 시작...")
        print("   주의: 이 단계에서 게임이 실제로 시작됩니다.")
        print("   스토리가 표시되거나 메뉴가 나타날 수 있습니다.")
        print("   게임을 종료하려면 ESC를 누르거나 메뉴에서 종료를 선택하세요.")
        
        # PyInstaller 환경에서는 알림창 표시
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                result = messagebox.askyesno("게임 시작", 
                    "이제 실제 게임이 시작됩니다.\n\n게임을 시작하시겠습니까?\n\n(아니오를 누르면 테스트를 중단합니다)")
                root.destroy()
                
                if not result:
                    print("게임 시작을 취소했습니다.")
                    return
            except:
                pass
        
        print("4. 📱 Dawn of Stellar 게임 시작!")
        print("-" * 50)
        
        # 실제 게임 실행
        result = game_main_module.main()
        
        print("-" * 50)
        print("5. ✅ 게임이 정상적으로 종료되었습니다!")
        print(f"반환값: {result}")
        
        # 종료 확인 메시지
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("테스트 완료", "게임이 정상적으로 실행되고 종료되었습니다!")
                root.destroy()
            except:
                pass
        
    except KeyboardInterrupt:
        print("\n게임이 사용자에 의해 중단되었습니다.")
        
    except Exception as e:
        error_msg = f"게임 실행 중 오류 발생: {e}"
        print(error_msg)
        
        # 상세 오류 정보
        import traceback
        detailed_error = traceback.format_exc()
        print("\n상세 오류:")
        print(detailed_error)
        
        # 오류 로그 저장
        try:
            with open("game_run_error.log", "w", encoding="utf-8") as f:
                f.write(f"{error_msg}\n\n{detailed_error}")
            print("오류 로그가 game_run_error.log에 저장되었습니다.")
        except:
            pass
        
        if getattr(sys, 'frozen', False):
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("게임 실행 오류", f"게임 실행 중 오류가 발생했습니다:\n\n{str(e)}")
                root.destroy()
            except:
                pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
