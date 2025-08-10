#!/usr/bin/env python3
"""
Windows Terminal 색상 테스트
"""

import sys
import os
sys.path.append('.')

from game.color_text import ColorText, Color, colored, bright_red, bright_green, bright_yellow, bright_cyan

def test_colors():
    """색상 테스트"""
    print("🎨 Windows Terminal 색상 테스트")
    print("=" * 50)
    
    print(f"Windows Terminal 감지: {'WT_SESSION' in os.environ}")
    print(f"PowerShell 감지: {'PSModulePath' in os.environ}")
    print(f"색상 지원: {ColorText.is_color_supported()}")
    print()
    
    if ColorText.is_color_supported():
        print("✅ 색상이 지원됩니다!")
        print()
        
        # 색상 테스트
        print(bright_red("🔴 빨간색 테스트"))
        print(bright_green("🟢 초록색 테스트"))
        print(bright_yellow("🟡 노란색 테스트"))
        print(bright_cyan("🔵 청록색 테스트"))
        print(colored("🟣 마젠타 테스트", Color.BRIGHT_MAGENTA.value))
        print()
        
        # 게임 스타일 테스트
        print(f"{Color.BRIGHT.value_CYAN.value}🌟 D A W N   O F   S T E L L A R 🌟{Color.RESET.value}")
        print(f"{Color.BRIGHT.value_YELLOW.value}⭐ 별들 사이의 모험이 시작됩니다 ⭐{Color.RESET.value}")
        print(f"{Color.BRIGHT.value_GREEN.value}✨ 용기를 가지고 도전하세요! ✨{Color.RESET.value}")
        
    else:
        print("❌ 색상이 지원되지 않습니다.")
        print("🔧 Windows Terminal에서 실행해보세요!")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_colors()
    input("아무 키나 누르세요...")
