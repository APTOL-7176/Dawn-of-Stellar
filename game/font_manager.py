#!/usr/bin/env python3
"""
Dawn of Stellar - 폰트 매니저
게임 전체에서 일관된 폰트 사용을 위한 매니저
whitrabt 폰트(영어), Galmuri11 폰트(한글) 강제 적용 시스템
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

class FontManager:
    """게임 폰트 통합 관리 클래스 (강화된 버전)"""
    
    def __init__(self):
        self.current_font = None
        self.font_paths = self._get_system_fonts()
        self.selected_font_path = None
        
        # 게임 전용 폰트 경로
        self.game_dir = Path(__file__).parent.parent
        self.game_fonts = {
            'english': self.game_dir / 'whitrabt.ttf',
            'korean': self.game_dir / 'Galmuri11.ttf'
        }
        
        self.system = platform.system()
        self._initialize_font()
        self._check_game_fonts()
    
    def _get_system_fonts(self) -> Dict[str, str]:
        """시스템 폰트 경로 목록 반환"""
        font_paths = {}
        
        # Windows 폰트
        if sys.platform == "win32":
            windows_fonts = {
                "Arial": "C:/Windows/Fonts/arial.ttf",
                "Calibri": "C:/Windows/Fonts/calibri.ttf",
                "Segoe UI": "C:/Windows/Fonts/segoeui.ttf",
                "Consolas": "C:/Windows/Fonts/consola.ttf",
                "Microsoft YaHei": "C:/Windows/Fonts/msyh.ttf",
                "Malgun Gothic": "C:/Windows/Fonts/malgun.ttf",
            }
            font_paths.update(windows_fonts)
        
        # macOS 폰트
        elif sys.platform == "darwin":
            macos_fonts = {
                "Arial": "/System/Library/Fonts/Arial.ttf",
                "Helvetica": "/System/Library/Fonts/Helvetica.ttc",
                "SF Pro Display": "/System/Library/Fonts/SFNS.ttf",
                "Menlo": "/System/Library/Fonts/Menlo.ttc",
            }
            font_paths.update(macos_fonts)
        
        # Linux 폰트
        else:
            linux_fonts = {
                "DejaVu Sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "Liberation Sans": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "Ubuntu": "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                "Noto Sans": "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            }
            font_paths.update(linux_fonts)
        
        # 실제 존재하는 폰트만 반환
        existing_fonts = {}
        for name, path in font_paths.items():
            if Path(path).exists():
                existing_fonts[name] = path
        
        return existing_fonts
    
    def _check_game_fonts(self):
        """게임 전용 폰트 파일 확인 및 설정"""
        print("Dawn of Stellar 폰트 시스템 초기화...")
        
        # 폰트 파일 존재 확인
        fonts_found = []
        fonts_missing = []
        
        for name, path in self.game_fonts.items():
            if path.exists():
                fonts_found.append(f"OK {name}: {path.name}")
            else:
                fonts_missing.append(f"MISSING {name}: {path.name}")
        
        if fonts_found:
            print("발견된 게임 폰트:")
            for font in fonts_found:
                print(f"   {font}")
        
        if fonts_missing:
            print("누락된 게임 폰트:")
            for font in fonts_missing:
                print(f"   {font}")
        
        # 터미널 폰트 설정 가이드 표시
        if fonts_found:
            self._show_terminal_font_guide()
    
    def _show_terminal_font_guide(self):
        """터미널 폰트 설정 가이드"""
        print("\n최적의 게임 경험을 위한 터미널 폰트 설정:")
        print("=" * 60)
        
        if self.system == "Windows":
            print("Windows Terminal 설정:")
            print("   1. Windows Terminal 열기")
            print("   2. Ctrl + , (설정)")
            print("   3. 프로필 → 기본값 → 모양")
            print("   4. 글꼴 면에 다음 입력:")
            print("      'whitrabt', 'Galmuri11', 'Consolas', 'Courier New', monospace")
            print("   5. 글꼴 크기: 12~14 권장")
            
            print("\nVS Code 터미널 설정:")
            print("   1. VS Code에서 Ctrl + , (설정)")
            print("   2. 'terminal.integrated.fontFamily' 검색")
            print("   3. 다음 값 입력:")
            print("      'whitrabt', 'Galmuri11', 'Consolas', monospace")
            print("   4. 'terminal.integrated.fontSize': 12~14")
            
            print("\nPowerShell 설정:")
            print("   1. PowerShell 우클릭 → 속성")
            print("   2. 글꼴 탭에서 whitrabt 또는 Galmuri11 선택")
            
        elif self.system == "Linux":
            print("Gnome Terminal:")
            print("   1. 터미널 → 환경설정")
            print("   2. 프로필 → 텍스트")
            print("   3. 사용자 정의 글꼴 체크")
            print("   4. 'whitrabt 12' 또는 'Galmuri11 12' 선택")
            
            print("\nVS Code Terminal:")
            print("   터미널 → 설정에서 fontFamily를")
            print("   'whitrabt', 'Galmuri11', 'monospace'로 설정")
            
        elif self.system == "Darwin":  # macOS
            print("Terminal.app:")
            print("   1. Terminal → 환경설정")
            print("   2. 프로필 → 텍스트")
            print("   3. 글꼴에서 whitrabt 또는 Galmuri11 선택")
            
        print(f"\n폰트 강제 설치: python game/font_manager.py")
        print("=" * 60)

    def install_game_fonts(self):
        """게임 폰트를 시스템에 설치"""
        if not all(path.exists() for path in self.game_fonts.values()):
            print("폰트 파일을 찾을 수 없습니다!")
            return False
            
        try:
            if self.system == "Windows":
                return self._install_fonts_windows()
            elif self.system == "Linux":
                return self._install_fonts_linux()
            elif self.system == "Darwin":  # macOS
                return self._install_fonts_macos()
            else:
                print(f"지원하지 않는 운영체제: {self.system}")
                return False
        except Exception as e:
            print(f"폰트 설치 실패: {e}")
            return False
    
    def _install_fonts_windows(self):
        """Windows에 폰트 설치"""
        try:
            import winreg
            import shutil
        except ImportError:
            print("Windows 폰트 설치에 필요한 모듈을 가져올 수 없습니다.")
            return False
        
        fonts_dir = Path(os.environ.get('WINDIR', 'C:\\Windows')) / 'Fonts'
        
        for name, font_path in self.game_fonts.items():
            try:
                # 폰트 파일을 시스템 폰트 디렉토리에 복사
                dest_path = fonts_dir / font_path.name
                if not dest_path.exists():
                    shutil.copy2(font_path, dest_path)
                    print(f"{name} 폰트 복사됨: {dest_path}")
                else:
                    print(f"{name} 폰트 이미 설치됨")
                
                # 레지스트리에 폰트 등록 시도
                try:
                    font_name = self._get_font_display_name(font_path)
                    reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                    
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, font_name, 0, winreg.REG_SZ, font_path.name)
                        print(f"{name} 폰트 등록됨: {font_name}")
                except PermissionError:
                    print(f"{name} 폰트 레지스트리 등록 권한 부족")
                except Exception as reg_e:
                    print(f"{name} 폰트 레지스트리 등록 실패: {reg_e}")
                    
            except PermissionError:
                print(f"{name} 폰트 설치 권한 부족 (관리자 권한으로 실행 필요)")
                return False
            except Exception as e:
                print(f"{name} 폰트 설치 실패: {e}")
                
        print("Windows 폰트 설치 완료! 터미널을 다시 시작해주세요.")
        return True
    
    def _install_fonts_linux(self):
        """Linux에 폰트 설치"""
        # 사용자 폰트 디렉토리 생성
        font_dir = Path.home() / '.local' / 'share' / 'fonts'
        font_dir.mkdir(parents=True, exist_ok=True)
        
        for name, font_path in self.game_fonts.items():
            try:
                dest_path = font_dir / font_path.name
                if not dest_path.exists():
                    import shutil
                    shutil.copy2(font_path, dest_path)
                    print(f"{name} 폰트 설치됨: {dest_path}")
                else:
                    print(f"{name} 폰트 이미 설치됨")
            except Exception as e:
                print(f"{name} 폰트 설치 실패: {e}")
        
        # 폰트 캐시 갱신
        try:
            subprocess.run(['fc-cache', '-f'], check=True, capture_output=True)
            print("폰트 캐시 갱신 완료")
        except subprocess.CalledProcessError:
            print("폰트 캐시 갱신 실패")
        except FileNotFoundError:
            print("fc-cache를 찾을 수 없습니다")
            
        print("Linux 폰트 설치 완료!")
        return True
    
    def _install_fonts_macos(self):
        """macOS에 폰트 설치"""
        font_dir = Path.home() / 'Library' / 'Fonts'
        font_dir.mkdir(parents=True, exist_ok=True)
        
        for name, font_path in self.game_fonts.items():
            try:
                dest_path = font_dir / font_path.name
                if not dest_path.exists():
                    import shutil
                    shutil.copy2(font_path, dest_path)
                    print(f"{name} 폰트 설치됨: {dest_path}")
                else:
                    print(f"{name} 폰트 이미 설치됨")
            except Exception as e:
                print(f"{name} 폰트 설치 실패: {e}")
                
        print("macOS 폰트 설치 완료!")
        return True
    
    def _get_font_display_name(self, font_path):
        """폰트 파일에서 표시 이름 추출"""
        name = font_path.stem.lower()
        if 'whitrabt' in name:
            return "Whitrabt (TrueType)"
        elif 'galmuri' in name:
            return "Galmuri11 (TrueType)"
        else:
            return f"{font_path.stem} (TrueType)"

    def _initialize_font(self):
        """기본 폰트 초기화"""
        # 게임 폰트 우선 확인
        if self.game_fonts['english'].exists():
            print("게임 폰트 발견: whitrabt.ttf")
            return
        
        # 시스템 폰트 대체
        priority_fonts = ["Arial", "Calibri", "Segoe UI", "DejaVu Sans", "Liberation Sans"]
        
        for font_name in priority_fonts:
            if font_name in self.font_paths:
                self.selected_font_path = self.font_paths[font_name]
                print(f"시스템 폰트 설정: {font_name}")
                return
        
        # 사용 가능한 첫 번째 폰트 사용
        if self.font_paths:
            font_name = list(self.font_paths.keys())[0]
            self.selected_font_path = self.font_paths[font_name]
            print(f"대체 폰트 설정: {font_name}")
        else:
            print("경고: 시스템 폰트를 찾을 수 없습니다.")
    
    def get_font_path(self) -> Optional[str]:
        """현재 설정된 폰트 경로 반환"""
        return self.selected_font_path
    
    def get_available_fonts(self) -> Dict[str, str]:
        """사용 가능한 폰트 목록 반환"""
        return self.font_paths.copy()
    
    def set_font(self, font_name: str) -> bool:
        """특정 폰트로 변경"""
        if font_name in self.font_paths:
            self.selected_font_path = self.font_paths[font_name]
            print(f"폰트 변경: {font_name}")
            return True
        else:
            print(f"폰트를 찾을 수 없습니다: {font_name}")
            return False
    
    def get_terminal_font_config(self) -> Dict[str, Any]:
        """터미널/콘솔 출력용 폰트 설정"""
        config = {
            "font_path": self.selected_font_path,
            "encoding": "utf-8",
            "fallback_fonts": ["Arial", "Calibri", "DejaVu Sans"],
        }
        
        # Windows에서는 cp949 인코딩 고려
        if sys.platform == "win32":
            config["encoding_fallback"] = "cp949"
        
        return config
    
    def apply_terminal_font(self):
        """터미널에 폰트 설정 적용 (가능한 경우)"""
        try:
            # Windows 터미널 폰트 설정
            if sys.platform == "win32":
                import ctypes
                from ctypes import wintypes
                
                # 콘솔 폰트 설정 시도
                STD_OUTPUT_HANDLE = -11
                handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                
                # 유니코드 출력 활성화
                ctypes.windll.kernel32.SetConsoleOutputCP(65001)  # UTF-8
                
                # print("✓ Windows 터미널 유니코드 출력 활성화")  # 메시지 제거
        
        except Exception as e:
            print(f"터미널 폰트 설정 실패: {e}")
    
    def get_font_info(self) -> Dict[str, Any]:
        """현재 폰트 정보 반환"""
        info = {
            "selected_font": self.selected_font_path,
            "available_fonts": len(self.font_paths),
            "platform": sys.platform,
            "encoding": "utf-8",
        }
        
        if self.selected_font_path:
            font_file = Path(self.selected_font_path)
            info["font_name"] = font_file.stem
            info["font_exists"] = font_file.exists()
            info["font_size"] = font_file.stat().st_size if font_file.exists() else 0
        
        return info

# 전역 폰트 매니저 인스턴스
_font_manager = None

def get_font_manager() -> FontManager:
    """폰트 매니저 싱글톤 인스턴스 반환"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager

def get_game_font_path() -> Optional[str]:
    """게임용 폰트 경로 반환 (간편 함수)"""
    return get_font_manager().get_font_path()

def apply_game_font():
    """게임 폰트 설정 적용 (간편 함수)"""
    manager = get_font_manager()
    manager.apply_terminal_font()
    return manager.get_font_path()

def show_font_info():
    """현재 폰트 정보 출력"""
    manager = get_font_manager()
    info = manager.get_font_info()
    
    print("\n=== 게임 폰트 정보 ===")
    print(f"선택된 폰트: {info.get('font_name', '없음')}")
    print(f"폰트 경로: {info.get('selected_font', '없음')}")
    print(f"사용 가능한 폰트: {info['available_fonts']}개")
    print(f"플랫폼: {info['platform']}")
    print(f"인코딩: {info['encoding']}")
    
    if info.get('selected_font'):
        exists = "✓" if info.get('font_exists') else "✗"
        size = info.get('font_size', 0)
        print(f"폰트 상태: {exists} ({size:,} bytes)")

def install_game_fonts():
    """게임 폰트 설치 실행 함수"""
    manager = get_font_manager()
    return manager.install_game_fonts()

def show_setup_guide():
    """폰트 설정 가이드 표시"""
    manager = get_font_manager()
    manager._show_terminal_font_guide()

if __name__ == "__main__":
    print("Dawn of Stellar - 폰트 관리 시스템")
    print("=" * 50)
    
    # 폰트 매니저 초기화 (자동으로 게임 폰트 체크)
    manager = get_font_manager()
    
    print("\n📋 사용 가능한 옵션:")
    print("1. 게임 폰트 시스템 설치")
    print("2. 터미널 폰트 설정 가이드 보기")
    print("3. 현재 폰트 정보 확인")
    print("4. 종료")
    
    while True:
        try:
            choice = input("\n선택하세요 (1-4): ").strip()
            
            if choice == "1":
                print("\n게임 폰트 설치 중...")
                if manager.install_game_fonts():
                    print("설치 완료! 터미널을 재시작하고 폰트를 변경해주세요.")
                else:
                    print("설치 실패. 관리자 권한으로 다시 시도해보세요.")
            
            elif choice == "2":
                manager._show_terminal_font_guide()
            
            elif choice == "3":
                show_font_info()
            
            elif choice == "4":
                print("👋 폰트 관리 시스템을 종료합니다.")
                break
            
            else:
                print("잘못된 선택입니다. 1-4 중에서 선택해주세요.")
                
        except KeyboardInterrupt:
            print("\n\n👋 사용자가 종료했습니다.")
            break
        except Exception as e:
            print(f"오류 발생: {e}")
