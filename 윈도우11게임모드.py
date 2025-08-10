#!/usr/bin/env python3
"""
Windows 11 게임 모드 강제 활성화 도구
"""

import os
import sys

def force_game_mode():
    """Windows 11 게임 모드 강제 활성화로 화상키보드 차단"""
    try:
        import winreg
        
        print("🎮 Windows 11 게임 모드 강제 활성화 중...")
        
        # 게임 모드 레지스트리 설정
        try:
            key_path = r"SOFTWARE\Microsoft\GameBar"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            print("✅ 게임 모드 자동 활성화")
        except Exception as e:
            print(f"⚠️ 게임 모드 설정 실패: {e}")
        
        # 전체 화면 최적화 비활성화 (화상키보드 차단)
        try:
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "python.exe", 0, winreg.REG_SZ, "DISABLEDXMAXIMIZEDWINDOWEDMODE")
            winreg.CloseKey(key)
            print("✅ 전체 화면 최적화 비활성화")
        except Exception as e:
            print(f"⚠️ 전체 화면 최적화 설정 실패: {e}")
            
        print("✅ Windows 11 게임 모드 설정 완료!")
        
    except ImportError:
        print("❌ winreg 모듈을 사용할 수 없습니다")
    except Exception as e:
        print(f"❌ 게임 모드 설정 실패: {e}")

if __name__ == "__main__":
    force_game_mode()
    input("아무 키나 누르세요...")
