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
    
    print(f"\n{Color.BRIGHT.value_BLUE.value}{'─'*70}{Color.RESET.value}")
    print(f"{Color.BRIGHT.value_WHITE.value}🛡️  아군 파티 상태{Color.RESET.value}")
    print(f"{Color.BRIGHT.value_BLUE.value}{'─'*70}{Color.RESET.value}")
    
    # 현재 턴 캐릭터 (화살표 있음)
    print(f"  ▶🏹 Lv.15 {Color.BRIGHT.value_CYAN.value}코딘{Color.RESET.value} 🔮")
    print(f"  💚 HP: {Color.BRIGHT.value_GREEN.value}850{Color.RESET.value} / {Color.WHITE.value}850{Color.RESET.value} {Color.WHITE.value}[{Color.BRIGHT.value_GREEN.value}▰▰▰▰▰▰▰▰▰▰{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} | 💙 MP: {Color.BRIGHT_GREEN.value}320{Color.RESET.value} / {Color.WHITE.value}320{Color.RESET.value} {Color.WHITE.value}[{Color.BRIGHT_GREEN.value}▰▰▰▰▰▰▰▰▰▰{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} | {Color.BRIGHT_YELLOW.value}⚡ BRV: 1250{Color.RESET.value}")
    print(f"  ⌛ TIME: {Color.WHITE.value}[{Color.BRIGHT.value_YELLOW.value}▰▰▰▰▰▰▰▰▰▰{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} READY | SPD: {Color.BRIGHT.value_GREEN.value}85{Color.RESET.value}")
    print()
    
    # 일반 아군 (화살표 없음)
    print(f"   🛡️ Lv.12 {Color.WHITE.value}레이나{Color.RESET.value}")
    print(f"  💛 HP: {Color.YELLOW.value}420{Color.RESET.value} / {Color.WHITE.value}680{Color.RESET.value} {Color.WHITE.value}[{Color.YELLOW.value}▰▰▰▰▰▰▱▱▱▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} | 💙 MP: {Color.BLUE.value}180{Color.RESET.value} / {Color.WHITE.value}280{Color.RESET.value} {Color.WHITE.value}[{Color.BLUE.value}▰▰▰▰▰▰▱▱▱▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} | {Color.BRIGHT.value_YELLOW.value}⚡ BRV: 800{Color.RESET.value}")
    print(f"  ⌛ TIME: {Color.WHITE.value}[{Color.BRIGHT.value_CYAN.value}▰▰▰▰▰▰▰▱▱▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} {Color.BRIGHT.value_CYAN.value}75%{Color.RESET.value} | SPD: {Color.WHITE.value}65{Color.RESET.value}")
    print()
    
    # 캐스팅 중인 아군
    print(f"   ⚔️ Lv.14 {Color.WHITE.value}마르쿠스{Color.RESET.value} 🔮")
    print(f"  🧡 HP: {Color.BRIGHT.value_RED.value}280{Color.RESET.value} / {Color.WHITE.value}750{Color.RESET.value} {Color.WHITE.value}[{Color.BRIGHT.value_RED.value}▰▰▰▱▱▱▱▱▱▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} | 💙 MP: {Color.BRIGHT_GREEN.value}420{Color.RESET.value} / {Color.WHITE.value}450{Color.RESET.value} {Color.WHITE.value}[{Color.BRIGHT_GREEN.value}▰▰▰▰▰▰▰▰▰▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} | {Color.BRIGHT_YELLOW.value}⚡ BRV: 950{Color.RESET.value}")
    print(f"  ⌛ TIME: {Color.WHITE.value}[{Color.BRIGHT.value_MAGENTA.value}▰▰▰▰▰▰▱▱▱▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} {Color.BRIGHT.value_MAGENTA.value}🔮65%{Color.RESET.value} | SPD: {Color.GREEN.value}72{Color.RESET.value} {Color.BRIGHT_MAGENTA.value}[CASTING: 파이어볼]{Color.RESET.value}")
    print()
    
    print(f"\n{Color.BRIGHT.value_RED.value}{'─'*70}{Color.RESET.value}")
    print(f"{Color.BRIGHT.value_WHITE.value}⚔️  적군 상태{Color.RESET.value}")
    print(f"{Color.BRIGHT.value_RED.value}{'─'*70}{Color.RESET.value}")
    
    # 일반 적 (화살표 없음)
    print(f"   ⚔️ {Color.WHITE.value}오크 전사{Color.RESET.value}")
    print(f"  💚 HP: {Color.BRIGHT.value_GREEN.value}450{Color.RESET.value} / {Color.WHITE.value}450{Color.RESET.value} {Color.WHITE.value}[{Color.BRIGHT.value_GREEN.value}▰▰▰▰▰▰▰▰▰▰{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} | {Color.BRIGHT_YELLOW.value}⚡ BRV: 600{Color.RESET.value}")
    print(f"  ⌛ TIME: {Color.WHITE.value}[{Color.BRIGHT.value_RED.value}▰▰▰▰▰▰▱▱▱▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} {Color.BRIGHT.value_RED.value}62%{Color.RESET.value} | SPD: {Color.YELLOW.value}45{Color.RESET.value}")
    print()
    
    # 적의 턴 (화살표 있음)
    print(f"  ▶⚔️ {Color.BRIGHT.value_RED.value}다크 메이지{Color.RESET.value} 🔮")
    print(f"  🧡 HP: {Color.BRIGHT.value_RED.value}320{Color.RESET.value} / {Color.WHITE.value}520{Color.RESET.value} {Color.WHITE.value}[{Color.BRIGHT.value_RED.value}▰▰▰▰▰▰▱▱▱▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} | {Color.BRIGHT_RED.value}⚡ BRV: 250{Color.RESET.value}")
    print(f"  ⌛ TIME: {Color.WHITE.value}[{Color.BRIGHT.value_MAGENTA.value}▰▰▰▰▰▰▰▰▱▱{Color.RESET.value} {Color.WHITE.value}]{Color.RESET.value} {Color.BRIGHT.value_MAGENTA.value}🔮85%{Color.RESET.value} | SPD: {Color.WHITE.value}58{Color.RESET.value} {Color.BRIGHT_MAGENTA.value}[CASTING: 다크 볼트]{Color.RESET.value}")
    print()
    
    print(f"\n{Color.BRIGHT.value_YELLOW.value}⏳ ATB 업데이트: ⚔️ 다크 메이지 - 87%{Color.RESET.value}")
    print(f"⏳ ATB 업데이트: ⚔️ 다크 메이지 - 89%")
    print(f"⏳ ATB 업데이트: ⚔️ 다크 메이지 - 92%")
    print(f"⏳ ATB 업데이트: ⚔️ 다크 메이지 - 95%")
    print(f"⏳ ATB 업데이트: ⚔️ 다크 메이지 - 98%")
    print(f"{Color.BRIGHT.value_YELLOW.value}⏳ ATB 업데이트: ⚔️ 다크 메이지 - READY{Color.RESET.value}")
    print(f"\n🎮 ⚔️ 다크 메이지의 차례")

if __name__ == "__main__":
    show_ui_example()
