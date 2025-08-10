"""
🚀 Dawn of Stellar - 고성능 최적화 런처 v4.0.1
초고속 반응속도 + 최소 메모리 사용량

2025년 8월 10일 - 성능 최적화 버전
"""

import os
import sys
import subprocess
import platform
from datetime import datetime

# 성능 최적화: 필요할 때만 import
def lazy_import():
    """지연 로딩으로 시작 속도 향상"""
    global json, time
    import json
    import time

class FastLauncher:
    """초고속 런처 클래스"""
    
    def __init__(self):
        self.version = "v4.0.1 Fast"
        self.python_exe = self.get_python_exe()
        self.clear_cmd = "cls" if platform.system() == "Windows" else "clear"
        
    def get_python_exe(self):
        """Python 실행파일 경로 빠른 검색"""
        candidates = [
            "D:/로그라이크_2/.venv/Scripts/python.exe",
            ".venv/Scripts/python.exe",
            "python.exe",
            "python"
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return "python"
    
    def clear_screen(self):
        """빠른 화면 클리어"""
        os.system(self.clear_cmd)
    
    def show_fast_menu(self):
        """최적화된 빠른 메뉴"""
        self.clear_screen()
        
        print(f"""
    ╔══════════════════════════════════════════════════════════════╗
               🚀 Dawn of Stellar - 고속 런처 {self.version}             
                        별들의 새벽 - 로그라이크 RPG                    
    ╚══════════════════════════════════════════════════════════════╝

📋 빠른 실행 메뉴 (숫자키로 즉시 선택)
══════════════════════════════════════
⚡ 빠른 실행:
  [1] 🎮 게임 실행 (EXE)
  [2] 🐍 Python 게임 실행  
  [3] 📱 Flutter 모바일
  [4] 🌐 멀티플레이어

🤖 AI 시스템:
  [A] 🤖 AI 학습 메뉴
  [B] 🌙 밤새 AI 학습
  [C] ⚡ AI 빠른 테스트
  [D] 📊 AI 상태 확인
  [L] 💬 로바트와 대화 (GPT-5!)
  [P] 🎭 27개 직업별 성격 보기

🔧 도구:
  [5] 📦 게임 빌드
  [6] 🔄 업데이트/복구
  [7] 🧹 캐시 정리
  [8] 📊 시스템 정보
  [S] 🔑 LLM API 키 설정

  [0] ❌ 종료

────────────────────────────────────────────────────────────────
🎮 즉시 선택: 숫자/문자키 입력 │ ESC: 종료
📊 시스템: {platform.system()} │ {datetime.now().strftime('%H:%M:%S')}
""")

    def run_fast_command(self, choice):
        """선택에 따른 빠른 실행"""
        choice = choice.upper()
        
        commands = {
            "1": ("🎮 EXE 게임 실행", "game.exe"),
            "2": ("🐍 Python 게임", f"{self.python_exe} main.py"),
            "3": ("📱 Flutter 모바일", f"{self.python_exe} mobile_backend_server.py"),
            "4": ("🌐 멀티플레이어", f"{self.python_exe} mobile_server.py"),
            "A": ("🤖 AI 학습 메뉴", f"{self.python_exe} -c \"from python_launcher import show_ai_learning_menu; show_ai_learning_menu()\""),
            "B": ("🌙 밤새 AI 학습", f"{self.python_exe} -c \"from python_launcher import run_night_learning; run_night_learning()\""),
            "C": ("⚡ AI 빠른 테스트", f"{self.python_exe} -c \"from game.permanent_ai_learning_system import demo_permanent_learning_system; demo_permanent_learning_system()\""),
            "D": ("📊 AI 상태 확인", f"{self.python_exe} -c \"from python_launcher import check_ai_status; check_ai_status()\""),
            "L": ("💬 로바트와 대화", f"{self.python_exe} ai_language_model_integration.py chat"),
            "P": ("🎭 성격 시스템", f"{self.python_exe} game/robat_personality_system.py"),
            "5": ("📦 게임 빌드", f"{self.python_exe} -c \"from python_launcher import build_menu; build_menu()\""),
            "6": ("🔄 업데이트/복구", f"{self.python_exe} -c \"from python_launcher import update_menu; update_menu()\""),
            "7": ("🧹 캐시 정리", f"{self.python_exe} -c \"from python_launcher import cleanup_cache; cleanup_cache()\""),
            "8": ("📊 시스템 정보", f"{self.python_exe} -c \"from python_launcher import show_system_info; show_system_info()\""),
            "S": ("🔑 API 키 설정", f"{self.python_exe} ai_language_model_integration.py setup")
        }
        
        if choice in commands:
            name, cmd = commands[choice]
            print(f"\n🚀 {name} 실행 중...")
            try:
                if choice == "1" and os.path.exists("game.exe"):
                    subprocess.run("game.exe", shell=True)
                else:
                    subprocess.run(cmd, shell=True)
            except Exception as e:
                print(f"❌ 실행 실패: {e}")
                input("아무 키나 누르세요...")
        elif choice == "0":
            print("👋 고속 런처를 종료합니다.")
            return False
        else:
            print("❌ 잘못된 선택입니다.")
            input("아무 키나 누르세요...")
        
        return True

    def run(self):
        """메인 실행 루프"""
        while True:
            self.show_fast_menu()
            try:
                choice = input("선택: ").strip()
                if not choice:
                    continue
                    
                if not self.run_fast_command(choice):
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 고속 런처를 종료합니다.")
                break
            except Exception as e:
                print(f"❌ 오류: {e}")
                input("아무 키나 누르세요...")

def main():
    """고성능 런처 시작"""
    print("🚀 고속 런처 초기화 중...")
    
    # 지연 로딩
    lazy_import()
    
    # 런처 실행
    launcher = FastLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
