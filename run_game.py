#!/usr/bin/env python3
"""
Dawn of Stellar - 통합 실행 진입점
데스크톱/모바일 자동 감지 및 실행
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 설정
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def detect_platform():
    """플랫폼 감지"""
    try:
        # Kivy 환경 체크
        from kivy.utils import platform as kivy_platform
        return kivy_platform
    except ImportError:
        # 일반적인 플랫폼 감지
        if sys.platform.startswith('linux'):
            return 'linux'
        elif sys.platform.startswith('win'):
            return 'win'
        elif sys.platform.startswith('darwin'):
            return 'macosx'
        else:
            return 'unknown'

def check_mobile_environment():
    """모바일 환경 체크"""
    platform = detect_platform()
    
    # 모바일 플랫폼 체크
    if platform in ['android', 'ios']:
        return True
    
    # 터치 스크린 체크 (Windows)
    if platform == 'win':
        try:
            import ctypes
            SM_TABLETPC = 86
            return ctypes.windll.user32.GetSystemMetrics(SM_TABLETPC) != 0
        except:
            pass
    
    # 환경 변수 체크
    if os.environ.get('DAWN_OF_STELLAR_MOBILE', '').lower() == 'true':
        return True
    
    # 명령행 인수 체크
    if '--mobile' in sys.argv:
        return True
    
    return False

def show_startup_info():
    """시작 정보 표시"""
    print("🌟 Dawn of Stellar - 통합 게임 런처")
    print("=" * 50)
    
    platform = detect_platform()
    is_mobile = check_mobile_environment()
    
    print(f"🖥️  플랫폼: {platform}")
    print(f"📱 모바일 모드: {'예' if is_mobile else '아니오'}")
    print("=" * 50)
    
    return platform, is_mobile

def run_desktop_mode():
    """데스크톱 모드 실행"""
    print("🖥️  데스크톱 모드로 실행합니다...")
    
    try:
        from main import main as desktop_main
        desktop_main()
    except ImportError as e:
        print(f"❌ 데스크톱 게임 로드 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 데스크톱 게임 실행 실패: {e}")
        return False
    
    return True

def run_mobile_mode():
    """모바일 모드 실행"""
    print("📱 모바일 모드로 실행합니다...")
    
    # 모바일 UI 직접 실행
    try:
        os.environ['KIVY_NO_ARGS'] = '1'  # Kivy 인수 파싱 비활성화
        
        from game.mobile_ui import MobileDawnOfStellarApp
        app = MobileDawnOfStellarApp()
        app.run()
        return True
        
    except ImportError as e:
        print(f"❌ 모바일 UI 로드 실패: {e}")
        print("💡 pip install kivy로 Kivy를 설치해주세요.")
    except Exception as e:
        print(f"❌ 모바일 게임 실행 실패: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def run_with_fallback():
    """폴백을 포함한 실행"""
    platform, is_mobile = show_startup_info()
    
    # 명령행 인수 확인
    if '--mobile' in sys.argv or is_mobile:
        success = run_mobile_mode()
        if success:
            return True
        
        # 모바일 실패 시 데스크톱으로 폴백
        print("🔄 데스크톱 모드로 폴백...")
        return run_desktop_mode()
    else:
        return run_desktop_mode()

def show_manual_selection():
    """수동 모드 선택"""
    print("\n🎯 실행 모드를 선택하세요:")
    print("1. 데스크톱 모드 (키보드/마우스)")
    print("2. 모바일 모드 (터치 인터페이스)")
    print("3. 자동 감지")
    print("0. 종료")
    
    while True:
        try:
            choice = input("\n선택 (0-3): ").strip()
            
            if choice == '0':
                print("👋 게임을 종료합니다.")
                return None
            elif choice == '1':
                return 'desktop'
            elif choice == '2':
                return 'mobile'
            elif choice == '3':
                return 'auto'
            else:
                print("❌ 잘못된 선택입니다. 다시 입력하세요.")
                
        except KeyboardInterrupt:
            print("\n👋 게임을 종료합니다.")
            return None

def main():
    """메인 실행 함수"""
    try:
        # 시작 정보 표시
        platform, is_mobile_env = show_startup_info()
        
        # 명령행 인수에서 모드 확인
        if '--desktop' in sys.argv:
            mode = 'desktop'
        elif '--mobile' in sys.argv:
            mode = 'mobile'
        elif '--select' in sys.argv:
            mode = show_manual_selection()
            if mode is None:
                return
        else:
            # 자동 감지
            mode = 'mobile' if is_mobile_env else 'desktop'
        
        print(f"\n🚀 {mode.upper()} 모드로 실행합니다...\n")
        
        # 모드별 실행
        if mode == 'mobile':
            success = run_mobile_mode()
        elif mode == 'desktop':
            success = run_desktop_mode()
        elif mode == 'auto':
            # 자동 감지 재시도
            if is_mobile_env:
                success = run_mobile_mode()
            else:
                success = run_desktop_mode()
        else:
            print("❌ 알 수 없는 실행 모드입니다.")
            success = False
        
        if success:
            print("\n✅ 게임이 정상적으로 종료되었습니다.")
        else:
            print("\n❌ 게임 실행 중 오류가 발생했습니다.")
            
    except KeyboardInterrupt:
        print("\n🛑 사용자가 게임을 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Dawn of Stellar 종료")

def show_help():
    """도움말 표시"""
    print("═" * 50)
    print("        🌟 D A W N   O F   S T E L L A R 🌟")
    print("                    사용법")
    print("═" * 50)
    print("python run_game.py              # 자동 모드 감지")
    print("python run_game.py --desktop    # 데스크톱 모드 강제 실행")
    print("python run_game.py --mobile     # 모바일 모드 강제 실행")
    print("python run_game.py --select     # 수동 모드 선택")
    print("python run_game.py --help       # 이 도움말 표시")
    print()
    print("🔧 환경 변수:")
    print("DAWN_OF_STELLAR_MOBILE=true     # 모바일 모드 강제 활성화")
    print()
    print("📱 모바일 요구사항:")
    print("pip install kivy kivymd")

if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv:
        show_help()
    else:
        main()
