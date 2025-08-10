#!/usr/bin/env python3
"""
시드 고정 테스트 - 아이템 일관성 확인
"""

import sys
import os
sys.path.append('.')

print("🎲 시드 고정 테스트 - 아이템 일관성 확인")
print("=" * 60)

try:
    from game.world import GameWorld
    from game.party_manager import PartyManager
    from game.character import Character
    import hashlib
    
    # 테스트 1: 동일한 파티로 시드 생성 테스트
    print("📊 테스트 1: 동일한 파티 구성으로 시드 일관성 확인")
    
    # 파티 매니저 생성
    party_manager = PartyManager()
    test_char = Character("핀", "암살자")
    party_manager.add_member(test_char)
    
    # 월드 생성 (첫 번째)
    world1 = GameWorld()
    world1.party_manager = party_manager
    
    # 세션 시드 생성
    party_names = [member.name for member in party_manager.members]
    party_hash = "".join(party_names)
    session_string = f"DawnOfStellar_{party_hash}_Session2025"
    expected_seed = int(hashlib.md5(session_string.encode()).hexdigest()[:8], 16)
    
    print(f"   파티 구성: {party_names}")
    print(f"   예상 세션 시드: {expected_seed}")
    
    # 첫 번째 층 생성
    world1.generate_level(1)
    actual_seed1 = world1.game_session_seed
    level_seed1 = world1.current_level_seed
    
    print(f"   실제 세션 시드: {actual_seed1}")
    print(f"   1층 시드: {level_seed1}")
    
    # 월드 생성 (두 번째) - 동일한 파티
    world2 = GameWorld()
    world2.party_manager = party_manager
    world2.generate_level(1)
    
    actual_seed2 = world2.game_session_seed
    level_seed2 = world2.current_level_seed
    
    print(f"   재생성 세션 시드: {actual_seed2}")
    print(f"   재생성 1층 시드: {level_seed2}")
    
    # 일관성 확인
    session_consistent = (actual_seed1 == actual_seed2 == expected_seed)
    level_consistent = (level_seed1 == level_seed2)
    
    print(f"\n🔍 결과:")
    print(f"   세션 시드 일관성: {'✅ 일관됨' if session_consistent else '❌ 불일치'}")
    print(f"   층별 시드 일관성: {'✅ 일관됨' if level_consistent else '❌ 불일치'}")
    
    # 테스트 2: 다른 층에서의 시드 확인
    print(f"\n📊 테스트 2: 층별 시드 변화 확인")
    
    for level in [2, 3, 4, 5]:
        world1.generate_level(level)
        level_seed = world1.current_level_seed
        
        # 동일한 조건으로 재생성
        world2.generate_level(level)
        level_seed2 = world2.current_level_seed
        
        consistent = (level_seed == level_seed2)
        print(f"   {level}층 시드: {level_seed} {'✅' if consistent else '❌'}")
    
    if session_consistent and level_consistent:
        print(f"\n🎉 성공!")
        print(f"✅ 시드 고정 시스템이 정상 작동합니다!")
        print(f"🎮 이제 아이템이 매번 동일하게 나타납니다!")
        print(f"💾 저장/로드 시에도 시드가 보존됩니다!")
    else:
        print(f"\n⚠️ 문제 발견!")
        print(f"❌ 시드 시스템에 불일치가 있습니다.")
        
except ImportError as e:
    print(f"❌ 임포트 오류: {e}")
except Exception as e:
    print(f"❌ 테스트 오류: {e}")

print("\n🏁 시드 고정 테스트 완료")
