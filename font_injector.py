#!/usr/bin/env python3
"""
Dawn of Stellar - 폰트 주입 시스템
터미널에서 실행되지만 폰트를 강제로 변경하는 독립 프로그램
"""

import os
import sys
import ctypes
import platform
import subprocess
from pathlib import Path
import time

class FontInjector:
    """터미널 폰트를 강제로 변경하는 클래스"""
    
    def __init__(self):
        self.game_dir = Path(__file__).parent
        self.system = platform.system()
        
        # 게임 폰트 파일들
        self.fonts = {
            'whitrabt': self.game_dir / 'whitrabt.ttf',
            'galmuri': self.game_dir / 'Galmuri11.ttf'
        }
        
        print("🎮 Dawn of Stellar - 폰트 주입 시스템")
        print("=" * 50)
        
    def check_fonts(self):
        """폰트 파일 존재 확인"""
        missing = []
        found = []
        
        for name, path in self.fonts.items():
            if path.exists():
                found.append(f"✅ {name}: {path.name}")
            else:
                missing.append(f"❌ {name}: {path.name}")
        
        if found:
            print("발견된 폰트:")
            for font in found:
                print(f"  {font}")
        
        if missing:
            print("누락된 폰트:")
            for font in missing:
                print(f"  {font}")
            return False
        
        return True
    
    def inject_windows_console_font(self):
        """Windows 콘솔 폰트 직접 변경"""
        if self.system != "Windows":
            print("❌ Windows에서만 지원됩니다.")
            return False
        
        try:
            # Windows API를 통한 콘솔 폰트 변경
            import ctypes
            from ctypes import wintypes, Structure, byref
            
            # 콘솔 핸들 가져오기
            STD_OUTPUT_HANDLE = -11
            handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            
            # CONSOLE_FONT_INFOEX 구조체 정의
            class COORD(Structure):
                _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
            
            class CONSOLE_FONT_INFOEX(Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("nFont", ctypes.c_ulong),
                    ("dwFontSize", COORD),
                    ("FontFamily", ctypes.c_uint),
                    ("FontWeight", ctypes.c_uint),
                    ("FaceName", ctypes.c_wchar * 32)
                ]
            
            # 현재 폰트 정보 가져오기
            font_info = CONSOLE_FONT_INFOEX()
            font_info.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
            
            GetCurrentConsoleFontEx = ctypes.windll.kernel32.GetCurrentConsoleFontEx
            GetCurrentConsoleFontEx.argtypes = [wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(CONSOLE_FONT_INFOEX)]
            GetCurrentConsoleFontEx.restype = wintypes.BOOL
            
            if GetCurrentConsoleFontEx(handle, False, byref(font_info)):
                print(f"현재 콘솔 폰트: {font_info.FaceName}")
                
                # 새 폰트로 변경
                font_info.FaceName = "whitrabt"  # 또는 "Galmuri11"
                font_info.dwFontSize.X = 0
                font_info.dwFontSize.Y = 14
                font_info.FontWeight = 400
                
                SetCurrentConsoleFontEx = ctypes.windll.kernel32.SetCurrentConsoleFontEx
                SetCurrentConsoleFontEx.argtypes = [wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(CONSOLE_FONT_INFOEX)]
                SetCurrentConsoleFontEx.restype = wintypes.BOOL
                
                if SetCurrentConsoleFontEx(handle, False, byref(font_info)):
                    print("✅ 콘솔 폰트 변경 성공!")
                    return True
                else:
                    print("❌ 콘솔 폰트 변경 실패")
            
            return False
            
        except Exception as e:
            print(f"❌ 폰트 주입 실패: {e}")
            return False
    
    def create_font_config_file(self):
        """폰트 설정 파일 생성"""
        config_content = f"""
# Dawn of Stellar - 터미널 폰트 설정
# 이 파일을 터미널 설정에 복사하세요

## Windows Terminal
{{
    "profiles": {{
        "defaults": {{
            "fontFace": "whitrabt, Galmuri11, Consolas",
            "fontSize": 12
        }}
    }}
}}

## VS Code settings.json
{{
    "terminal.integrated.fontFamily": "whitrabt, Galmuri11, Consolas, monospace",
    "terminal.integrated.fontSize": 12
}}

## PowerShell Profile
# $Host.UI.RawUI.WindowTitle = "Dawn of Stellar"
# [console]::InputEncoding = [System.Text.Encoding]::UTF8
# [console]::OutputEncoding = [System.Text.Encoding]::UTF8
"""
        
        config_file = self.game_dir / 'font_config.txt'
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ 폰트 설정 파일 생성: {config_file}")
        return config_file
    
    def launch_with_custom_font(self):
        """사용자 정의 폰트로 새 터미널 실행"""
        if self.system == "Windows":
            return self._launch_windows_terminal()
        else:
            print("❌ Windows에서만 지원됩니다.")
            return False
    
    def _launch_windows_terminal(self):
        """Windows Terminal을 사용자 정의 폰트로 실행"""
        try:
            # Windows Terminal 설정 파일 생성
            wt_config = {
                "profiles": {
                    "list": [
                        {
                            "name": "Dawn of Stellar",
                            "commandline": "cmd.exe",
                            "fontFace": "whitrabt, Galmuri11, Consolas",
                            "fontSize": 12,
                            "colorScheme": "Campbell",
                            "startingDirectory": str(self.game_dir)
                        }
                    ]
                }
            }
            
            import json
            config_file = self.game_dir / 'wt_profile.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(wt_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Windows Terminal 프로필 생성: {config_file}")
            
            # Windows Terminal 실행
            cmd = [
                "wt.exe",
                "--profile", "Dawn of Stellar",
                "--title", "Dawn of Stellar",
                "cmd", "/k", f"cd /d {self.game_dir} && python main.py"
            ]
            
            subprocess.Popen(cmd, shell=True)
            print("🚀 게임 전용 터미널 실행!")
            return True
            
        except Exception as e:
            print(f"❌ 터미널 실행 실패: {e}")
            return False
    
    def create_powershell_launcher(self):
        """PowerShell 런처 스크립트 생성"""
        ps_script = f'''
# Dawn of Stellar - PowerShell 런처
$Host.UI.RawUI.WindowTitle = "Dawn of Stellar"
[console]::InputEncoding = [System.Text.Encoding]::UTF8
[console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 폰트 정보 표시
Write-Host "🎮 Dawn of Stellar 게임 런처" -ForegroundColor Green
Write-Host "=" * 50
Write-Host "💡 최적 폰트: whitrabt, Galmuri11" -ForegroundColor Yellow
Write-Host "📂 게임 디렉토리: {self.game_dir}" -ForegroundColor Cyan
Write-Host ""

# 게임 실행
Set-Location "{self.game_dir}"
python main.py

# 게임 종료 후 대기
Write-Host ""
Write-Host "게임이 종료되었습니다. 아무 키나 누르세요..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
'''
        
        launcher_file = self.game_dir / 'launch_game.ps1'
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        print(f"✅ PowerShell 런처 생성: {launcher_file}")
        return launcher_file
    
    def create_batch_launcher(self):
        """배치 파일 런처 생성"""
        bat_script = f'''@echo off
chcp 65001 > nul
title Dawn of Stellar
cd /d "{self.game_dir}"

echo 🎮 Dawn of Stellar 게임 런처
echo ================================
echo 💡 최적 폰트: whitrabt, Galmuri11
echo 📂 게임 디렉토리: {self.game_dir}
echo.

python main.py

echo.
echo 게임이 종료되었습니다. 아무 키나 누르세요...
pause > nul
'''
        
        launcher_file = self.game_dir / 'launch_game.bat'
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(bat_script)
        
        print(f"✅ 배치 런처 생성: {launcher_file}")
        return launcher_file
    
    def install_font_temporarily(self):
        """임시로 폰트 설치 (현재 세션용)"""
        if self.system != "Windows":
            print("❌ Windows에서만 지원됩니다.")
            return False
        
        try:
            # Windows API를 통한 임시 폰트 로드
            import ctypes
            from ctypes import wintypes
            
            gdi32 = ctypes.windll.gdi32
            AddFontResourceW = gdi32.AddFontResourceW
            AddFontResourceW.argtypes = [wintypes.LPCWSTR]
            AddFontResourceW.restype = ctypes.c_int
            
            success_count = 0
            for name, font_path in self.fonts.items():
                if font_path.exists():
                    result = AddFontResourceW(str(font_path))
                    if result > 0:
                        print(f"✅ {name} 임시 로드 성공")
                        success_count += 1
                    else:
                        print(f"❌ {name} 임시 로드 실패")
            
            if success_count > 0:
                # 폰트 캐시 갱신
                HWND_BROADCAST = 0xFFFF
                WM_FONTCHANGE = 0x001D
                user32 = ctypes.windll.user32
                user32.SendMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)
                print("✅ 폰트 캐시 갱신 완료")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 임시 폰트 설치 실패: {e}")
            return False
    
    def run_font_injection(self):
        """폰트 주입 실행"""
        print("🔍 폰트 파일 확인 중...")
        if not self.check_fonts():
            print("❌ 필요한 폰트 파일을 찾을 수 없습니다.")
            return False
        
        print("\n📋 폰트 주입 옵션:")
        print("1. 콘솔 폰트 직접 변경 (현재 터미널)")
        print("2. 임시 폰트 설치 (현재 세션)")
        print("3. 게임 전용 터미널 실행")
        print("4. 런처 스크립트 생성")
        print("5. 설정 파일 생성")
        print("6. 모든 옵션 실행")
        print("7. 종료")
        
        while True:
            try:
                choice = input("\n선택하세요 (1-7): ").strip()
                
                if choice == "1":
                    print("\n🔧 콘솔 폰트 변경 중...")
                    self.inject_windows_console_font()
                
                elif choice == "2":
                    print("\n🔧 임시 폰트 설치 중...")
                    self.install_font_temporarily()
                
                elif choice == "3":
                    print("\n🚀 게임 전용 터미널 실행 중...")
                    self.launch_with_custom_font()
                
                elif choice == "4":
                    print("\n📝 런처 스크립트 생성 중...")
                    self.create_powershell_launcher()
                    self.create_batch_launcher()
                
                elif choice == "5":
                    print("\n📄 설정 파일 생성 중...")
                    self.create_font_config_file()
                
                elif choice == "6":
                    print("\n🔧 모든 옵션 실행 중...")
                    self.install_font_temporarily()
                    self.inject_windows_console_font()
                    self.create_font_config_file()
                    self.create_powershell_launcher()
                    self.create_batch_launcher()
                    print("✅ 모든 설정 완료!")
                
                elif choice == "7":
                    print("👋 폰트 주입 시스템을 종료합니다.")
                    break
                
                else:
                    print("⚠️ 잘못된 선택입니다. 1-7 중에서 선택해주세요.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 사용자가 종료했습니다.")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")

def main():
    """메인 실행 함수"""
    injector = FontInjector()
    injector.run_font_injection()

if __name__ == "__main__":
    main()
