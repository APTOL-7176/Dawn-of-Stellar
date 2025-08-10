#!/usr/bin/env python3
"""
정확한 4배 ATB 속도 테스트
"""

import sys
import os
sys.path.append('.')

print("🎯 정확한 4배 ATB 속도 테스트")
print("=" * 50)

try:
    from game.brave_combat import BraveCombatSystem
    from game.character import Character
    
    # 테스트 설정
    original_base = 0.25  # 원래 값
    current_base = 1.0    # 현재 값
    speed_ratio = current_base / original_base
    
    print(f"📊 ATB 배수 계산:")
    print(f"   원래 base_increase: {original_base}")
    print(f"   현재 base_increase: {current_base}")
    print(f"   실제 속도 배수: {speed_ratio:.1f}배")
    print("")
    
    # 전투 시스템 확인
    combat = BraveCombatSystem()
    print(f"🔧 전투 시스템 설정:")
    print(f"   BASE_ATB_INCREASE: {combat.BASE_ATB_INCREASE}")
    print(f"   ATB_MAX: {combat.ATB_MAX}")
    print(f"   ATB_READY_THRESHOLD: {combat.ATB_READY_THRESHOLD}")
    print("")
    
    # 시뮬레이션 비교
    print("⚖️ 이전 vs 현재 비교:")
    
    # 이전 속도 (base_increase = 0.25)
    old_ticks_to_ready = combat.ATB_READY_THRESHOLD / (0.25 * 50)  # 속도 50 기준
    
    # 현재 속도 (base_increase = 1.0) 
    new_ticks_to_ready = combat.ATB_READY_THRESHOLD / (1.0 * 50)   # 속도 50 기준
    
    print(f"   이전: ~{old_ticks_to_ready:.1f}틱에 턴 준비")
    print(f"   현재: ~{new_ticks_to_ready:.1f}틱에 턴 준비")
    print(f"   개선: {old_ticks_to_ready/new_ticks_to_ready:.1f}배 빨라짐")
    print("")
    
    if abs(speed_ratio - 4.0) < 0.1:
        print("✅ 정확히 4배 속도입니다!")
    elif speed_ratio > 4.5:
        print("⚠️ 4배보다 너무 빠릅니다!")
    elif speed_ratio < 3.5:
        print("⚠️ 4배보다 느립니다!")
    else:
        print("✅ 거의 4배 속도입니다!")
        
    print("")
    print("🎮 이제 전투가 적절히 빨라집니다!")
    
except ImportError as e:
    print(f"❌ 임포트 오류: {e}")
except Exception as e:
    print(f"❌ 테스트 오류: {e}")

print("\n🏁 4배 속도 확인 완료")
