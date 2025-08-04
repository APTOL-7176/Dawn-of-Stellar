#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전투 UI 출력 예시 - 개선 후 모습
"""

class Color:
    RESET = '\033[0m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_WHITE = '\033[97m'
    BRIGHT_CYAN = '\033[96m'
    WHITE = '\033[37m'
    BRIGHT_GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED = '\033[91m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    BRIGHT_MAGENTA = '\033[95m'
    GREEN = '\033[32m'
    BRIGHT_BLACK = '\033[90m'

def show_ui_example():
    """개선된 전투 UI 예시 출력"""
    
    print(f"\n{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}🛡️  아군 파티 상태{Color.RESET}")
    print(f"{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
    
    # 현재 턴 캐릭터 (화살표 있음)
    print(f"  ▶🏹 Lv.15 {Color.BRIGHT_CYAN}코딘{Color.RESET} 🔮")
    print(f"  💚 HP: {Color.BRIGHT_GREEN}850{Color.RESET} / {Color.WHITE}850{Color.RESET} {Color.WHITE}[{Color.BRIGHT_GREEN}▰▰▰▰▰▰▰▰▰▰{Color.RESET} {Color.WHITE}]{Color.RESET} | 💙 MP: {Color.BRIGHT_GREEN}320{Color.RESET} / {Color.WHITE}320{Color.RESET} {Color.WHITE}[{Color.BRIGHT_GREEN}▰▰▰▰▰▰▰▰▰▰{Color.RESET} {Color.WHITE}]{Color.RESET} | {Color.BRIGHT_YELLOW}⚡ BRV: 1250{Color.RESET}")
    print(f"  ⌛ TIME: {Color.WHITE}[{Color.BRIGHT_YELLOW}▰▰▰▰▰▰▰▰▰▰{Color.RESET} {Color.WHITE}]{Color.RESET} READY | SPD: {Color.BRIGHT_GREEN}85{Color.RESET}")
    print()
    
    # 일반 아군 (화살표 없음)
    print(f"   🛡️ Lv.12 {Color.WHITE}레이나{Color.RESET}")
    print(f"  💛 HP: {Color.YELLOW}420{Color.RESET} / {Color.WHITE}680{Color.RESET} {Color.WHITE}[{Color.YELLOW}▰▰▰▰▰▰▱▱▱▱{Color.RESET} {Color.WHITE}]{Color.RESET} | 💙 MP: {Color.BLUE}180{Color.RESET} / {Color.WHITE}280{Color.RESET} {Color.WHITE}[{Color.BLUE}▰▰▰▰▰▰▱▱▱▱{Color.RESET} {Color.WHITE}]{Color.RESET} | {Color.BRIGHT_YELLOW}⚡ BRV: 800{Color.RESET}")
    print(f"  ⌛ TIME: {Color.WHITE}[{Color.BRIGHT_CYAN}▰▰▰▰▰▰▰▱▱▱{Color.RESET} {Color.WHITE}]{Color.RESET} {Color.BRIGHT_CYAN}75%{Color.RESET} | SPD: {Color.WHITE}65{Color.RESET}")
    print()
    
    # 캐스팅 중인 아군
    print(f"   ⚔️ Lv.14 {Color.WHITE}마르쿠스{Color.RESET} 🔮")
    print(f"  🧡 HP: {Color.BRIGHT_RED}280{Color.RESET} / {Color.WHITE}750{Color.RESET} {Color.WHITE}[{Color.BRIGHT_RED}▰▰▰▱▱▱▱▱▱▱{Color.RESET} {Color.WHITE}]{Color.RESET} | 💙 MP: {Color.BRIGHT_GREEN}420{Color.RESET} / {Color.WHITE}450{Color.RESET} {Color.WHITE}[{Color.BRIGHT_GREEN}▰▰▰▰▰▰▰▰▰▱{Color.RESET} {Color.WHITE}]{Color.RESET} | {Color.BRIGHT_YELLOW}⚡ BRV: 950{Color.RESET}")
    print(f"  ⌛ TIME: {Color.WHITE}[{Color.BRIGHT_MAGENTA}▰▰▰▰▰▰▱▱▱▱{Color.RESET} {Color.WHITE}]{Color.RESET} {Color.BRIGHT_MAGENTA}🔮65%{Color.RESET} | SPD: {Color.GREEN}72{Color.RESET} {Color.BRIGHT_MAGENTA}[CASTING: 파이어볼]{Color.RESET}")
    print()
    
    print(f"\n{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}⚔️  적군 상태{Color.RESET}")
    print(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
    
    # 일반 적 (화살표 없음)
    print(f"   ⚔️ {Color.WHITE}오크 전사{Color.RESET}")
    print(f"  💚 HP: {Color.BRIGHT_GREEN}450{Color.RESET} / {Color.WHITE}450{Color.RESET} {Color.WHITE}[{Color.BRIGHT_GREEN}▰▰▰▰▰▰▰▰▰▰{Color.RESET} {Color.WHITE}]{Color.RESET} | {Color.BRIGHT_YELLOW}⚡ BRV: 600{Color.RESET}")
    print(f"  ⌛ TIME: {Color.WHITE}[{Color.BRIGHT_RED}▰▰▰▰▰▰▱▱▱▱{Color.RESET} {Color.WHITE}]{Color.RESET} {Color.BRIGHT_RED}62%{Color.RESET} | SPD: {Color.YELLOW}45{Color.RESET}")
    print()
    
    # 적의 턴 (화살표 있음)
    print(f"  ▶⚔️ {Color.BRIGHT_RED}다크 메이지{Color.RESET} 🔮")
    print(f"  🧡 HP: {Color.BRIGHT_RED}320{Color.RESET} / {Color.WHITE}520{Color.RESET} {Color.WHITE}[{Color.BRIGHT_RED}▰▰▰▰▰▰▱▱▱▱{Color.RESET} {Color.WHITE}]{Color.RESET} | {Color.BRIGHT_RED}⚡ BRV: 250{Color.RESET}")
    print(f"  ⌛ TIME: {Color.WHITE}[{Color.BRIGHT_MAGENTA}▰▰▰▰▰▰▰▰▱▱{Color.RESET} {Color.WHITE}]{Color.RESET} {Color.BRIGHT_MAGENTA}🔮85%{Color.RESET} | SPD: {Color.WHITE}58{Color.RESET} {Color.BRIGHT_MAGENTA}[CASTING: 다크 볼트]{Color.RESET}")
    print()
    
    print(f"\n{Color.BRIGHT_YELLOW}⏳ ATB 업데이트: ⚔️ 다크 메이지 - 87%{Color.RESET}")
    print(f"⏳ ATB 업데이트: ⚔️ 다크 메이지 - 89%")
    print(f"⏳ ATB 업데이트: ⚔️ 다크 메이지 - 92%")
    print(f"⏳ ATB 업데이트: ⚔️ 다크 메이지 - 95%")
    print(f"⏳ ATB 업데이트: ⚔️ 다크 메이지 - 98%")
    print(f"{Color.BRIGHT_YELLOW}⏳ ATB 업데이트: ⚔️ 다크 메이지 - READY{Color.RESET}")
    print(f"\n🎮 ⚔️ 다크 메이지의 차례")

if __name__ == "__main__":
    show_ui_example()
