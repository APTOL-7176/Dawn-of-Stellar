#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dawn of Stellar - 통합 Python 런처 v5.0.0
🎮 완전체 로그라이크 RPG + AI 멀티플레이어
마지막 업데이트: 2025년 8월 10일

🚀 v5.0.0 정리 버전:
- 🎮 메인 게임 (클래식 로그라이크)
- 🤖 AI 멀티플레이어 시스템
- 🎵 BGM/SFX 시스템
- 📱 Flutter 모바일 클라이언트
- 🔧 시스템 유틸리티
"""

import os
import sys
import subprocess
import time
import webbrowser
from datetime import datetime

# 색상 출력을 위한 설정
if os.name == 'nt':  # Windows
    os.system('chcp 65001 > nul')  # UTF-8 설정
    os.system('color')  # ANSI 색상 활성화

class Colors:
    """터미널 색상 코드"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DawnOfStellarLauncher:
    """Dawn of Stellar 통합 런처"""
    
    def __init__(self):
        self.game_dir = os.path.dirname(os.path.abspath(__file__))
        self.title = f"{Colors.CYAN}{Colors.BOLD}🌟 Dawn of Stellar - 통합 런처{Colors.END}"
        self.version = "v5.0.0"
        
    def clear_screen(self):
        """화면 지우기"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """헤더 출력"""
        print("=" * 60)
        print(f"    {self.title}")
        print(f"    {Colors.YELLOW}버전: {self.version} | 업데이트: 2025.08.10{Colors.END}")
        print("=" * 60)
        print()
    
    def check_python_environment(self):
        """Python 환경 확인"""
        python_version = sys.version_info
        print(f"{Colors.BLUE}🔍 Python 환경 확인:{Colors.END}")
        print(f"   버전: Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 가상환경 확인
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print(f"   환경: {Colors.GREEN}가상환경 활성화됨{Colors.END}")
        else:
            print(f"   환경: {Colors.YELLOW}시스템 Python{Colors.END}")
        
        # 필수 모듈 확인
        required_modules = ['pygame', 'colorama']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"   ✅ {module}")
            except ImportError:
                print(f"   ❌ {module} (누락)")
                missing_modules.append(module)
        
        if missing_modules:
            print(f"{Colors.RED}⚠️ 누락된 모듈이 있습니다: {', '.join(missing_modules)}{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✅ 모든 필수 모듈이 설치되어 있습니다.{Colors.END}")
        return True
    
    def run_main_game(self):
        """메인 게임 실행"""
        print(f"{Colors.GREEN}🎮 메인 게임 시작...{Colors.END}")
        print()
        
        try:
            # main.py 실행
            result = subprocess.run([sys.executable, "main.py"], 
                                  cwd=self.game_dir,
                                  capture_output=False)
            
            if result.returncode != 0:
                print(f"{Colors.RED}❌ 게임 실행 중 오류가 발생했습니다. (코드: {result.returncode}){Colors.END}")
            else:
                print(f"{Colors.GREEN}✅ 게임이 정상적으로 종료되었습니다.{Colors.END}")
                
        except FileNotFoundError:
            print(f"{Colors.RED}❌ main.py를 찾을 수 없습니다.{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ 실행 오류: {e}{Colors.END}")
    
    def run_ai_multiplayer(self):
        """AI 멀티플레이어 실행"""
        print(f"{Colors.PURPLE}🤖 AI 멀티플레이어 시작...{Colors.END}")
        print()
        
        try:
            # ai_multiplayer_integrated_hub.py 실행
            result = subprocess.run([sys.executable, "ai_multiplayer_integrated_hub.py"], 
                                  cwd=self.game_dir,
                                  capture_output=False)
            
            if result.returncode != 0:
                print(f"{Colors.RED}❌ AI 멀티플레이어 실행 중 오류가 발생했습니다. (코드: {result.returncode}){Colors.END}")
            else:
                print(f"{Colors.GREEN}✅ AI 멀티플레이어가 정상적으로 종료되었습니다.{Colors.END}")
                
        except FileNotFoundError:
            print(f"{Colors.RED}❌ ai_multiplayer_integrated_hub.py를 찾을 수 없습니다.{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ 실행 오류: {e}{Colors.END}")
    
    def run_mobile_server(self):
        """모바일 백엔드 서버 실행"""
        print(f"{Colors.CYAN}📱 모바일 백엔드 서버 시작...{Colors.END}")
        print()
        
        try:
            # mobile_backend_server.py 실행
            result = subprocess.run([sys.executable, "mobile_backend_server.py"], 
                                  cwd=self.game_dir,
                                  capture_output=False)
            
            if result.returncode != 0:
                print(f"{Colors.RED}❌ 모바일 서버 실행 중 오류가 발생했습니다. (코드: {result.returncode}){Colors.END}")
            else:
                print(f"{Colors.GREEN}✅ 모바일 서버가 정상적으로 종료되었습니다.{Colors.END}")
                
        except FileNotFoundError:
            print(f"{Colors.RED}❌ mobile_backend_server.py를 찾을 수 없습니다.{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ 실행 오류: {e}{Colors.END}")
    
    def open_documentation(self):
        """문서 보기"""
        print(f"{Colors.BLUE}📚 게임 문서 열기...{Colors.END}")
        
        docs = [
            ("README.md", "게임 메인 가이드"),
            ("COMPLETION_STATUS_FINAL.md", "완성 상태 보고서"),
            ("AI_MULTIPLAYER_COMPLETION_REPORT.md", "AI 멀티플레이어 보고서"),
            ("MOBILE_COMPLETE_GUIDE.md", "모바일 가이드")
        ]
        
        print("\n📖 사용 가능한 문서:")
        for i, (filename, description) in enumerate(docs, 1):
            if os.path.exists(filename):
                print(f"   {i}. {description} ({filename})")
        
        print("0. 돌아가기")
        
        try:
            choice = input("\n문서를 선택하세요: ").strip()
            if choice == "0":
                return
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(docs):
                filename = docs[choice_idx][0]
                if os.path.exists(filename):
                    # 기본 텍스트 에디터로 열기
                    if os.name == 'nt':  # Windows
                        os.startfile(filename)
                    else:  # Linux/Mac
                        subprocess.run(['xdg-open' if os.name != 'darwin' else 'open', filename])
                    print(f"✅ {filename} 문서를 열었습니다.")
                else:
                    print(f"❌ {filename} 파일을 찾을 수 없습니다.")
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def system_utilities(self):
        """시스템 유틸리티"""
        while True:
            print(f"\n{Colors.YELLOW}🔧 시스템 유틸리티{Colors.END}")
            print("-" * 30)
            print("1. 캐시 정리")
            print("2. 로그 파일 보기")
            print("3. 게임 설정 확인")
            print("4. 시스템 정보")
            print("0. 돌아가기")
            
            try:
                choice = input("\n선택하세요: ").strip()
                
                if choice == "1":
                    self.clear_cache()
                elif choice == "2":
                    self.view_logs()
                elif choice == "3":
                    self.check_game_settings()
                elif choice == "4":
                    self.show_system_info()
                elif choice == "0":
                    break
                else:
                    print("❌ 잘못된 선택입니다.")
                    
            except KeyboardInterrupt:
                break
    
    def clear_cache(self):
        """캐시 정리"""
        print(f"{Colors.YELLOW}🧹 캐시 정리 중...{Colors.END}")
        
        cache_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".pytest_cache",
            "game_debug.log",
            "game_error.log"
        ]
        
        cleaned_files = 0
        for pattern in cache_patterns:
            if pattern.startswith("*."):
                # 파일 패턴
                import glob
                files = glob.glob(pattern, recursive=True)
                for file in files:
                    try:
                        os.remove(file)
                        cleaned_files += 1
                        print(f"   삭제: {file}")
                    except:
                        pass
            else:
                # 디렉토리 패턴
                import shutil
                for root, dirs, files in os.walk("."):
                    if pattern in dirs:
                        dir_path = os.path.join(root, pattern)
                        try:
                            shutil.rmtree(dir_path)
                            cleaned_files += 1
                            print(f"   삭제: {dir_path}")
                        except:
                            pass
        
        print(f"✅ 캐시 정리 완료! ({cleaned_files}개 항목 정리)")
    
    def view_logs(self):
        """로그 파일 보기"""
        print(f"{Colors.BLUE}📋 로그 파일 확인{Colors.END}")
        
        log_files = [
            "game_debug.log",
            "game_error.log",
            "latest_errors.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                size = os.path.getsize(log_file)
                print(f"   📄 {log_file} ({size} bytes)")
            else:
                print(f"   📄 {log_file} (없음)")
    
    def check_game_settings(self):
        """게임 설정 확인"""
        print(f"{Colors.BLUE}⚙️ 게임 설정 확인{Colors.END}")
        
        settings_files = [
            "game_settings.json",
            "config.py"
        ]
        
        for settings_file in settings_files:
            if os.path.exists(settings_file):
                print(f"   ✅ {settings_file}")
            else:
                print(f"   ❌ {settings_file} (없음)")
    
    def show_system_info(self):
        """시스템 정보 표시"""
        import platform
        
        print(f"{Colors.BLUE}💻 시스템 정보{Colors.END}")
        print(f"   OS: {platform.system()} {platform.release()}")
        print(f"   Python: {platform.python_version()}")
        print(f"   Architecture: {platform.machine()}")
        print(f"   Processor: {platform.processor()}")
    
    def main_menu(self):
        """메인 메뉴"""
        while True:
            self.clear_screen()
            self.print_header()
            
            # 환경 체크 (간단히)
            env_status = "✅" if self.check_python_environment() else "⚠️"
            
            print(f"\n{Colors.BOLD}🎮 게임 메뉴{Colors.END}")
            print("-" * 30)
            print(f"1. {Colors.GREEN}🎮 메인 게임 (클래식 로그라이크){Colors.END}")
            print(f"2. {Colors.PURPLE}🤖 AI 멀티플레이어 시스템{Colors.END}")
            print(f"3. {Colors.CYAN}📱 모바일 백엔드 서버{Colors.END}")
            print(f"4. {Colors.BLUE}📚 게임 문서 보기{Colors.END}")
            print(f"5. {Colors.YELLOW}🔧 시스템 유틸리티{Colors.END}")
            print(f"0. {Colors.RED}❌ 종료{Colors.END}")
            
            print(f"\n{Colors.BOLD}상태:{Colors.END} 환경 {env_status} | 시간: {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                choice = input(f"\n{Colors.BOLD}선택하세요: {Colors.END}").strip()
                
                if choice == "1":
                    self.run_main_game()
                elif choice == "2":
                    self.run_ai_multiplayer()
                elif choice == "3":
                    self.run_mobile_server()
                elif choice == "4":
                    self.open_documentation()
                elif choice == "5":
                    self.system_utilities()
                elif choice == "0":
                    print(f"\n{Colors.GREEN}🌟 Dawn of Stellar을 플레이해주셔서 감사합니다!{Colors.END}")
                    break
                else:
                    print(f"{Colors.RED}❌ 잘못된 선택입니다.{Colors.END}")
                
                if choice in ["1", "2", "3"]:
                    input(f"\n{Colors.YELLOW}Enter를 눌러 계속...{Colors.END}")
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.GREEN}🌟 Dawn of Stellar을 플레이해주셔서 감사합니다!{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ 오류 발생: {e}{Colors.END}")
                input(f"\n{Colors.YELLOW}Enter를 눌러 계속...{Colors.END}")

def main():
    """메인 함수"""
    launcher = DawnOfStellarLauncher()
    launcher.main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GREEN}🌟 Dawn of Stellar을 플레이해주셔서 감사합니다!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ 런처 오류: {e}{Colors.END}")
        input("Enter를 눌러 종료...")
