#!/usr/bin/env python3
"""
로그라이크 게임 통합 런처
"""

import sys
import os
import subprocess

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'

def clear_screen():
    """화면 클리어"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_launcher_menu():
    """런처 메뉴 표시"""
    clear_screen()
    
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{WHITE}{BOLD}              🗡️  로그라이크 게임 런처  ⚔️{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")
    print()
    
    print(f"{WHITE}🎮 게임 모드를 선택하세요:{RESET}")
    print()
    print(f"{GREEN}1. 🧪 개발자 모드{RESET}")
    print(f"   • 모든 직업 해금 ({get_total_classes()}개)")
    print(f"   • 모든 패시브 해금")
    print(f"   • 디버그 기능 활성화")
    print()
    print(f"{YELLOW}2. 🎯 일반 게임 모드{RESET}")
    print(f"   • 기본 4개 직업만 해금 (전사, 아크메이지, 궁수, 도적)")
    print(f"   • 패시브는 게임 진행으로 해금")
    print(f"   • 정상적인 게임 밸런스")
    print()
    print(f"{BLUE}3. 🔧 파티 구성 테스트{RESET}")
    print(f"   • 자동 파티 생성 테스트")
    print(f"   • 패시브 시스템 테스트")
    print(f"   • 밸런스 확인")
    print()
    print(f"{MAGENTA}4. 📊 시스템 정보{RESET}")
    print(f"   • 게임 시스템 정보 확인")
    print(f"   • 직업/패시브 목록")
    print()
    print(f"{RED}5. ❌ 종료{RESET}")
    print()

def get_total_classes() -> int:
    """전체 직업 수 반환"""
    try:
        # 개발 모드로 임시 설정해서 전체 직업 수 확인
        original_env = os.environ.get('ROGUELIKE_DEV_MODE', 'false')
        os.environ['ROGUELIKE_DEV_MODE'] = 'true'
        
        # config 모듈을 다시 로드해서 새 환경변수 적용
        import importlib
        import sys
        if 'config' in sys.modules:
            importlib.reload(sys.modules['config'])
        
        from config import game_config
        total = len(game_config.get_available_classes())
        
        # 환경변수를 원래대로 복원
        os.environ['ROGUELIKE_DEV_MODE'] = original_env
        
        return total
    except:
        return 27

def run_development_mode():
    """개발자 모드 실행"""
    print(f"\n{GREEN}🧪 개발자 모드로 게임을 시작합니다...{RESET}")
    print(f"{YELLOW}✅ 모든 직업 해금{RESET}")
    print(f"{YELLOW}✅ 모든 패시브 해금{RESET}")
    print(f"{YELLOW}✅ 디버그 기능 활성화{RESET}")
    
    # 환경 변수 설정
    os.environ['ROGUELIKE_DEV_MODE'] = 'true'
    
    try:
        # 메인 게임 실행
        from main import main as game_main
        game_main()
    except ImportError:
        print(f"{RED}❌ 게임 파일을 찾을 수 없습니다.{RESET}")
        input(f"{WHITE}Enter 키를 눌러 계속...{RESET}")
    except Exception as e:
        print(f"{RED}❌ 게임 실행 중 오류 발생: {e}{RESET}")
        input(f"{WHITE}Enter 키를 눌러 계속...{RESET}")

def run_normal_mode():
    """일반 게임 모드 실행"""
    print(f"\n{YELLOW}🎯 일반 게임 모드로 게임을 시작합니다...{RESET}")
    print(f"{BLUE}🔒 기본 4개 직업만 해금{RESET}")
    print(f"{BLUE}🔒 패시브는 플레이로 해금{RESET}")
    print(f"{BLUE}🎯 정상적인 게임 진행{RESET}")
    
    # 환경 변수 설정
    os.environ['ROGUELIKE_DEV_MODE'] = 'false'
    
    try:
        # 메인 게임 실행
        from main import main as game_main
        game_main()
    except ImportError:
        print(f"{RED}❌ 게임 파일을 찾을 수 없습니다.{RESET}")
        input(f"{WHITE}Enter 키를 눌러 계속...{RESET}")
    except Exception as e:
        print(f"{RED}❌ 게임 실행 중 오류 발생: {e}{RESET}")
        input(f"{WHITE}Enter 키를 눌러 계속...{RESET}")

def run_party_test():
    """파티 구성 테스트 실행"""
    print(f"\n{BLUE}🔧 파티 구성 테스트를 시작합니다...{RESET}")
    
    # 개발 모드로 설정 (테스트를 위해)
    os.environ['ROGUELIKE_DEV_MODE'] = 'true'
    
    try:
        from test_party_regeneration import test_party_regeneration
        test_party_regeneration()
    except ImportError:
        print(f"{RED}❌ 테스트 파일을 찾을 수 없습니다.{RESET}")
    except Exception as e:
        print(f"{RED}❌ 테스트 실행 중 오류 발생: {e}{RESET}")
    
    input(f"\n{WHITE}Enter 키를 눌러 런처로 돌아가기...{RESET}")

def show_system_info():
    """시스템 정보 표시"""
    clear_screen()
    
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{WHITE}{BOLD}              📊 시스템 정보{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")
    print()
    
    try:
        # 개발 모드로 임시 설정해서 전체 정보 확인
        original_env = os.environ.get('ROGUELIKE_DEV_MODE', 'false')
        os.environ['ROGUELIKE_DEV_MODE'] = 'true'
        
        # config 모듈을 다시 로드해서 새 환경변수 적용
        import importlib
        import sys
        if 'config' in sys.modules:
            importlib.reload(sys.modules['config'])
        
        from config import game_config
        from game.character import CharacterClassManager
        
        print(f"{WHITE}🎮 게임 모드:{RESET}")
        print(f"   • 개발 모드: 모든 콘텐츠 해금")
        print(f"   • 일반 모드: 단계적 해금 시스템")
        print()
        
        print(f"{WHITE}🗡️ 직업 시스템:{RESET}")
        all_classes = game_config.get_available_classes()
        print(f"   • 총 직업 수: {GREEN}{len(all_classes)}개{RESET}")
        print(f"   • 개발 모드: 모든 직업 해금")
        print(f"   • 일반 모드: 전사, 아크메이지, 궁수, 도적만 해금")
        print()
        
        print(f"{WHITE}⚡ 패시브 시스템:{RESET}")
        print(f"   • 개발 모드: 모든 패시브 해금")
        print(f"   • 일반 모드: 패시브 기본 잠김 (게임 진행으로 해금)")
        print(f"   • 선택 가능: 0-2개 (패시브 없이도 게임 가능)")
        print()
        
        print(f"{WHITE}🔧 주요 기능:{RESET}")
        print(f"   • ATB 전투 시스템")
        print(f"   • 상처/회복 메커니즘")
        print(f"   • BRAVE 시스템")
        print(f"   • 자동 파티 구성")
        print(f"   • 135+ 패시브 능력")
        print(f"   • 27개 직업 클래스")
        print()
        
        print(f"{WHITE}📋 사용 가능한 직업 목록 (개발 모드):{RESET}")
        for i in range(0, len(all_classes), 5):
            row = all_classes[i:i+5]
            print("   " + " | ".join(f"{cls:>10}" for cls in row))
        
        # 환경변수를 원래대로 복원
        os.environ['ROGUELIKE_DEV_MODE'] = original_env
        
    except Exception as e:
        print(f"{RED}❌ 시스템 정보를 불러오는 중 오류 발생: {e}{RESET}")
    
    print()
    input(f"{WHITE}Enter 키를 눌러 런처로 돌아가기...{RESET}")

def cleanup_old_files():
    """기존 배치 파일들 정리 (더 이상 사용하지 않음)"""
    # 새로운 배치 파일들은 유지
    pass

def main():
    """메인 함수"""
    # 시작 시 기존 파일들 정리
    cleanup_old_files()
    
    while True:
        try:
            display_launcher_menu()
            
            choice = input(f"{WHITE}선택 (1-5): {RESET}").strip()
            
            if choice == '1':
                run_development_mode()
                
            elif choice == '2':
                run_normal_mode()
                
            elif choice == '3':
                run_party_test()
                
            elif choice == '4':
                show_system_info()
                
            elif choice == '5':
                print(f"\n{YELLOW}🎮 런처를 종료합니다. 안녕히가세요!{RESET}")
                break
                
            else:
                print(f"{RED}잘못된 선택입니다. 1-5 중에서 선택해주세요.{RESET}")
                input(f"{WHITE}Enter 키를 눌러 계속...{RESET}")
                
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}🎮 런처를 종료합니다. 안녕히가세요!{RESET}")
            break
        except Exception as e:
            print(f"{RED}❌ 런처 오류: {e}{RESET}")
            input(f"{WHITE}Enter 키를 눌러 계속...{RESET}")

if __name__ == "__main__":
    main()
