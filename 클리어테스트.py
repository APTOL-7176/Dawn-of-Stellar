"""
화면 클리어 테스트 - 상단 정렬 확인
"""

import sys
import time
sys.path.append('.')

from game.clear_screen_utils import force_clear_screen

def test_clear_screen():
    """화면 클리어 테스트"""
    print("🧪 화면 클리어 테스트 시작...")
    print("기존 텍스트들...")
    print("이 텍스트들이 사라져야 합니다.")
    print("3초 후 화면이 클리어됩니다!")
    
    time.sleep(3)
    
    # 화면 클리어
    force_clear_screen()
    
    # 상단에 새로운 내용 표시
    print("="*70)
    print("  ⚔️  전투 화면 테스트 - 상단 정렬  ⚔️".center(70))
    print("="*70)
    print()
    print("🛡️ 아군 파티 상태")
    print("-"*70)
    print("전사 (Lv.5) HP: ████████████ (120/120) MP: ████████ (50/50)")
    print("궁수 (Lv.4) HP: ████████████ (100/100) MP: ██████ (40/50)")
    print()
    print("⚔️ 적군 상태")
    print("-"*70)
    print("고블린 HP: ████████ (80/100)")
    print()
    print("="*70)
    print("📝 행동 선택:")
    print("👉 [1] BRV 공격 👈")
    print("   [2] HP 공격")
    print("   [3] 스킬 사용")
    print()
    print("✅ 화면이 터미널 상단에 정렬되었나요?")
    print("✅ 화면이 아래로 밀려나지 않았나요?")

if __name__ == "__main__":
    test_clear_screen()
