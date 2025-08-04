"""
한글 인코딩 및 터미널 호환성 유틸리티
"""

import sys
import os
import locale
import codecs


def setup_korean_encoding():
    """한글 인코딩 설정"""
    success_methods = []
    
    # Windows 전용 설정
    if os.name == 'nt':
        try:
            # Windows 콘솔 UTF-8 설정
            os.system('chcp 65001 >nul 2>&1')
            success_methods.append("Windows Console UTF-8")
        except:
            pass
        
        try:
            # Windows 로케일 설정
            locale.setlocale(locale.LC_ALL, 'korean')
            success_methods.append("Korean Locale")
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
                success_methods.append("Korean UTF-8 Locale")
            except:
                pass
    
    # 표준 입출력 인코딩 설정
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            success_methods.append("stdout/stderr UTF-8")
    except:
        pass
    
    try:
        if hasattr(sys.stdin, 'reconfigure'):
            sys.stdin.reconfigure(encoding='utf-8', errors='replace')
            success_methods.append("stdin UTF-8")
    except:
        pass
    
    # 환경 변수 설정
    try:
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        success_methods.append("PYTHONIOENCODING")
    except:
        pass
    
    return success_methods


def print_encoding_info():
    """현재 인코딩 정보 출력"""
    print("="*50)
    print("🔧 인코딩 설정 정보")
    print("="*50)
    
    try:
        print(f"시스템 인코딩: {sys.getdefaultencoding()}")
        print(f"파일시스템 인코딩: {sys.getfilesystemencoding()}")
        print(f"stdout 인코딩: {sys.stdout.encoding}")
        print(f"stderr 인코딩: {sys.stderr.encoding}")
        print(f"stdin 인코딩: {sys.stdin.encoding}")
        
        try:
            current_locale = locale.getlocale()
            print(f"현재 로케일: {current_locale}")
        except:
            print("로케일 정보를 가져올 수 없습니다.")
        
        print(f"운영체제: {os.name}")
        
        if os.name == 'nt':
            try:
                import subprocess
                result = subprocess.run('chcp', capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    print(f"Windows 코드페이지: {result.stdout.strip()}")
            except:
                pass
    
    except Exception as e:
        print(f"인코딩 정보 조회 실패: {e}")


def test_korean_output():
    """한글 출력 테스트"""
    print("\n" + "="*50)
    print("🇰🇷 한글 출력 테스트")
    print("="*50)
    
    test_strings = [
        "안녕하세요! Dawn Of Stellar에 오신 것을 환영합니다!",
        "한글과 영어가 Mixed String 잘 나오나요?",
        "특수문자: ★☆♥♦♣♠◆◇○●◎△▲▽▼",
        "ASCII 박스: +-|+",
        "게임 UI: [체력: 100/100] [마나: 50/50]",
        "캐릭터: 아이린, 카일, 라이언"
    ]
    
    for i, test_str in enumerate(test_strings, 1):
        try:
            print(f"{i}. {test_str}")
        except UnicodeEncodeError as e:
            print(f"{i}. [인코딩 오류] {e}")
        except Exception as e:
            print(f"{i}. [출력 오류] {e}")
    
    print("\n위 텍스트가 모두 정상적으로 표시되면 한글 설정이 완료되었습니다!")


def fix_terminal_encoding():
    """터미널 인코딩 자동 수정"""
    print("🔧 터미널 인코딩을 자동으로 설정합니다...")
    
    methods = setup_korean_encoding()
    
    if methods:
        print("✅ 다음 방법으로 인코딩이 설정되었습니다:")
        for method in methods:
            print(f"  • {method}")
    else:
        print("⚠️  자동 인코딩 설정에 실패했습니다.")
        print("수동으로 터미널 설정을 확인해주세요.")
    
    # 테스트 출력
    test_korean_output()
    
    return len(methods) > 0


def show_encoding_help():
    """인코딩 설정 도움말"""
    help_text = """
🔧 한글 표시 문제 해결 가이드

【Windows Terminal 설정】
1. Windows Terminal 설정 열기
2. 프로필 > 기본값 > 모양
3. 글꼴: Consolas, Courier New, 또는 MS Gothic
4. 크기: 12pt 이상

【CMD/PowerShell 설정】
1. 창 제목 표시줄 우클릭 > 속성
2. 글꼴 탭에서 적절한 폰트 선택
3. 크기 12 이상 설정

【VS Code 터미널 설정】
1. 설정(Ctrl+,) > terminal.integrated.fontFamily
2. "Consolas", "Courier New" 설정

【자주 발생하는 문제】
- 글자가 깨져 보임: 터미널 폰트를 MS Gothic으로 변경
- 박스 문자 오류: ASCII 호환 모드 사용 (게임에서 자동 설정됨)
- 한글 입력 안됨: 터미널 인코딩을 UTF-8로 설정

【추천 실행 방법】
- run_game.ps1 사용 (자동 인코딩 설정)
- 또는 Windows Terminal에서 python main.py

【문제가 계속 발생시】
1. 터미널 재시작
2. 다른 터미널 프로그램 사용
3. 폰트 변경
4. 관리자 권한으로 실행
"""
    print(help_text)


if __name__ == "__main__":
    print("Dawn Of Stellar - 인코딩 설정 도구")
    fix_terminal_encoding()
    print_encoding_info()
    print("\nEnter를 누르면 종료됩니다...")
    input()
