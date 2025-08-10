#!/usr/bin/env python3
"""
전투 하단 정렬 확인 테스트
"""

import sys
import os
sys.path.append('.')

print("🎯 전투 하단 정렬 확인 테스트")
print("=" * 50)

try:
    # 하단 정렬 함수 테스트
    from game.clear_screen_utils import show_combat_bottom_aligned
    from game.color_text import Color
    
    print("✅ 하단 정렬 모듈 임포트 성공!")
    
    # 실제 전투 화면과 동일한 데이터 구조로 테스트
    party_lines = [
        f"▶ 🌑 Lv.1 핀: {Color.BRIGHT_GREEN.value}HP 107/107{Color.RESET.value} | {Color.BRIGHT_BLUE.value}MP 35/35{Color.RESET.value} | {Color.BRIGHT_YELLOW.value}BRV 423{Color.RESET.value} | ⏳ READY",
        f"  ⚔️ Lv.1 그림니르: {Color.BRIGHT_GREEN.value}HP 259/259{Color.RESET.value} | {Color.BRIGHT_BLUE.value}MP 32/32{Color.RESET.value} | {Color.BRIGHT_YELLOW.value}BRV 531{Color.RESET.value} | ⏳ 73%",
        f"  🌌 Lv.1 오를리: {Color.BRIGHT_GREEN.value}HP 63/63{Color.RESET.value} | {Color.BRIGHT_BLUE.value}MP 91/91{Color.RESET.value} | {Color.BRIGHT_YELLOW.value}BRV 318{Color.RESET.value} | ⏳ 70%",
        f"  ⛪ Lv.1 율리안: {Color.BRIGHT_GREEN.value}HP 143/143{Color.RESET.value} | {Color.BRIGHT_BLUE.value}MP 81/81{Color.RESET.value} | {Color.BRIGHT_YELLOW.value}BRV 498{Color.RESET.value} | ⏳ 79%"
    ]
    
    enemy_lines = [
        f"▶ ⚔️ 스켈레톤: {Color.BRIGHT_RED.value}HP 201/201{Color.RESET.value} | {Color.BRIGHT_YELLOW.value}BRV 552{Color.RESET.value} | ⏳ 69%"
    ]
    
    menu_lines = [
        "👉 [1] ⚔️ Brave 공격 👈",
        "   [2] 💀 HP 공격", 
        "   [3] ✨ 스킬 사용",
        "   [4] 🧪 아이템 사용",
        "   [5] 🛡️ 방어",
        "   [6] 🏃 도망",
        "   [7] ⚡ 자동전투 (🔴 OFF)",
        "   [8] 📊 실시간 상태",
        "   [9] ❓ 전투 도움말",
        "",
        "🔼🔽 W/S: 위/아래 | ⚡ Enter: 선택 | ❌ Q: 취소"
    ]
    
    print("📺 전투 화면 하단 정렬 테스트 시작...")
    import time
    time.sleep(2)
    
    # 실제 전투와 동일한 하단 정렬 호출
    show_combat_bottom_aligned(party_lines, enemy_lines, menu_lines, "핀의 턴")
    
    print(f"\n{Color.BRIGHT_GREEN.value}✅ 전투 하단 정렬 테스트 완료!{Color.RESET.value}")
    print(f"{Color.BRIGHT_CYAN.value}전투 화면이 터미널 아래쪽에 고정되어 표시되었나요?{Color.RESET.value}")
    
except ImportError as e:
    print(f"❌ 임포트 오류: {e}")
    print("⚠️ 하단 정렬이 적용되지 않을 수 있습니다!")
except Exception as e:
    print(f"❌ 테스트 오류: {e}")

print("\n🎮 실제 게임에서도 이렇게 하단 정렬됩니다!")
