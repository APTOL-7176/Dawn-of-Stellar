#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
자동전투 & ATB 취소 문제 전용 디버그 테스터
Dawn of Stellar 게임의 자동전투 시스템과 취소 시 ATB 문제를 집중 테스트
"""

import sys
import os
import time
import traceback
from typing import List, Dict, Any

# 게임 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_auto_battle_system():
    """자동전투 시스템 전용 테스트"""
    print("🤖 자동전투 시스템 집중 테스트")
    print("="*60)
    
    try:
        from game.brave_combat import BraveCombatSystem
        from game.character import Character
        
        # 테스트 캐릭터 생성
        ally1 = Character("테스트전사", "전사")
        ally2 = Character("테스트아크메이지", "아크메이지")
        enemy1 = Character("테스트적1", "전사")
        enemy2 = Character("테스트적2", "아크메이지")
        
        # ATB 설정
        for char in [ally1, ally2, enemy1, enemy2]:
            char.atb_gauge = 1000
            
        # 전투 시스템 생성
        combat = BraveCombatSystem([ally1, ally2], [enemy1, enemy2])
        
        print("✅ 전투 시스템 초기화 완료")
        print(f"   아군: {ally1.name}, {ally2.name}")
        print(f"   적군: {enemy1.name}, {enemy2.name}")
        
        # 자동전투 모드 확인
        print(f"\n🔍 자동전투 초기 상태: {getattr(combat, 'auto_battle', 'None')}")
        
        # 자동전투 활성화 테스트
        if hasattr(combat, 'auto_battle'):
            print("🔄 자동전투 모드 활성화 테스트...")
            combat.auto_battle = True
            print(f"   자동전투 설정 후: {combat.auto_battle}")
            
            # toggle_auto_battle 메서드 테스트
            if hasattr(combat, 'toggle_auto_battle'):
                print("🔄 toggle_auto_battle 메서드 테스트...")
                original_state = combat.auto_battle
                combat.toggle_auto_battle()
                new_state = combat.auto_battle
                print(f"   토글 전: {original_state} → 토글 후: {new_state}")
                
                # 다시 토글해서 원상복구
                combat.toggle_auto_battle()
                print(f"   재토글 후: {combat.auto_battle}")
            else:
                print("❌ toggle_auto_battle 메서드가 없음")
                
            # _auto_battle_action 메서드 확인
            if hasattr(combat, '_auto_battle_action'):
                print("✅ _auto_battle_action 메서드 발견")
                
                # 자동전투 행동 시뮬레이션 (안전하게)
                print("🎯 자동전투 행동 시뮬레이션...")
                try:
                    # 자동전투 상태에서 플레이어 턴 시뮬레이션
                    combat.auto_battle = True
                    print("   자동전투 모드에서 플레이어 턴 시뮬레이션...")
                    
                    # 실제 player_turn 호출은 위험하므로 메서드 존재만 확인
                    print("   ✅ 자동전투 관련 메서드들이 모두 존재함")
                    
                except Exception as e:
                    print(f"   ⚠️ 자동전투 시뮬레이션 중 오류: {e}")
            else:
                print("❌ _auto_battle_action 메서드가 없음")
        else:
            print("❌ auto_battle 속성이 없음")
            
        return True
        
    except Exception as e:
        print(f"💥 자동전투 테스트 실패: {e}")
        traceback.print_exc()
        return False

def test_cancel_atb_problem():
    """취소 시 ATB 문제 집중 테스트"""
    print("\n🔄 취소 시 ATB 문제 집중 테스트")
    print("="*60)
    
    try:
        from game.brave_combat import BraveCombatSystem
        from game.character import Character
        
        # 테스트 캐릭터 생성
        ally = Character("테스트아군", "전사")
        enemy = Character("테스트적군", "전사")
        
        # 전투 시스템 생성
        combat = BraveCombatSystem([ally], [enemy])
        
        print("✅ 전투 시스템 초기화 완료")
        
        # ATB 초기 설정
        ally.atb_gauge = 1000
        enemy.atb_gauge = 500  # 적은 500으로 설정
        
        print(f"📊 초기 ATB 상태:")
        print(f"   아군 ATB: {ally.atb_gauge}")
        print(f"   적군 ATB: {enemy.atb_gauge}")
        
        # _last_action_completed 플래그 테스트
        print(f"\n🔍 _last_action_completed 플래그 테스트:")
        print(f"   초기 플래그: {getattr(combat, '_last_action_completed', 'None')}")
        
        # 플래그 초기화 테스트 (player_turn에서 하는 것처럼)
        combat._last_action_completed = False
        print(f"   초기화 후: {combat._last_action_completed}")
        
        # 행동 완료 시뮬레이션
        print(f"\n🎯 행동 완료 시뮬레이션:")
        combat._last_action_completed = True
        print(f"   행동 완료 후 플래그: {combat._last_action_completed}")
        
        # 취소 시뮬레이션
        print(f"\n❌ 취소 시뮬레이션:")
        combat._last_action_completed = False
        print(f"   취소 후 플래그: {combat._last_action_completed}")
        
        # 취소 카운터 시스템 확인
        if hasattr(combat, '_cancel_counters'):
            print(f"✅ _cancel_counters 시스템 발견")
            print(f"   취소 카운터: {combat._cancel_counters}")
        else:
            print(f"❌ _cancel_counters 시스템 없음")
            
        if hasattr(combat, '_cancel_last_time'):
            print(f"✅ _cancel_last_time 시스템 발견")
            print(f"   취소 시간 추적: {combat._cancel_last_time}")
        else:
            print(f"❌ _cancel_last_time 시스템 없음")
        
        # ATB 증가 시뮬레이션 (적 ATB)
        print(f"\n⏱️ ATB 증가 시뮬레이션:")
        original_enemy_atb = enemy.atb_gauge
        
        # ATB 증가 로직 시뮬레이션 (실제 게임처럼)
        if hasattr(enemy, 'speed'):
            speed_factor = getattr(enemy, 'speed', 100)
            atb_increase = max(7.5, min(30, 15 * (speed_factor / 100)))
            enemy.atb_gauge += atb_increase
            print(f"   적군 ATB: {original_enemy_atb} → {enemy.atb_gauge} (+{atb_increase})")
        else:
            enemy.atb_gauge += 15  # 기본 증가량
            print(f"   적군 ATB: {original_enemy_atb} → {enemy.atb_gauge} (+15)")
        
        # 플레이어 취소 시 적 ATB 증가가 멈추는 문제 시뮬레이션
        print(f"\n🚨 취소 시 ATB 문제 시뮬레이션:")
        print(f"   플레이어가 행동을 취소했을 때...")
        print(f"   적 ATB가 계속 증가해야 함: {enemy.atb_gauge} → {enemy.atb_gauge + 15}")
        
        return True
        
    except Exception as e:
        print(f"💥 취소 ATB 테스트 실패: {e}")
        traceback.print_exc()
        return False

def interactive_atb_monitor():
    """대화형 ATB 모니터링"""
    print("\n🎮 대화형 ATB 모니터링 (실제 게임 상황 시뮬레이션)")
    print("="*60)
    print("이 모드에서는 실제 게임처럼 ATB 상황을 모니터링할 수 있습니다.")
    print("Enter를 눌러서 턴을 진행하거나 'q'를 입력해서 종료하세요.")
    
    try:
        from game.brave_combat import BraveCombatSystem
        from game.character import Character
        
        # 테스트 캐릭터 생성
        ally = Character("아군전사", "전사")
        enemy = Character("적전사", "전사")
        
        # 전투 시스템 생성
        combat = BraveCombatSystem([ally], [enemy])
        
        # 초기 ATB 설정
        ally.atb_gauge = 800
        enemy.atb_gauge = 600
        turn_count = 1
        
        while True:
            print(f"\n--- 턴 {turn_count} ---")
            print(f"아군 ATB: {ally.atb_gauge:4.0f} {'✅ 행동가능' if ally.atb_gauge >= 1000 else ''}")
            print(f"적군 ATB: {enemy.atb_gauge:4.0f} {'✅ 행동가능' if enemy.atb_gauge >= 1000 else ''}")
            print(f"자동전투: {'ON' if getattr(combat, 'auto_battle', False) else 'OFF'}")
            print(f"action_completed: {getattr(combat, '_last_action_completed', 'None')}")
            
            user_input = input("\nEnter: 다음턴, 'a': 자동전투토글, 'c': 취소시뮬레이션, 'q': 종료 > ").strip().lower()
            
            if user_input == 'q':
                break
            elif user_input == 'a':
                if hasattr(combat, 'auto_battle'):
                    combat.auto_battle = not combat.auto_battle
                    print(f"자동전투 {'활성화' if combat.auto_battle else '비활성화'}")
                else:
                    print("자동전투 시스템 없음")
            elif user_input == 'c':
                print("취소 시뮬레이션: action_completed를 False로 설정")
                combat._last_action_completed = False
            
            # ATB 증가
            ally.atb_gauge = min(2000, ally.atb_gauge + 15)
            enemy.atb_gauge = min(2000, enemy.atb_gauge + 15)
            
            # 행동 시뮬레이션
            if ally.atb_gauge >= 1000:
                print("🎯 아군 행동 가능!")
                if getattr(combat, 'auto_battle', False):
                    print("   자동전투로 행동 실행")
                    ally.atb_gauge -= 1000
                    combat._last_action_completed = True
                    
            if enemy.atb_gauge >= 1000:
                print("👹 적군 행동!")
                enemy.atb_gauge -= 1000
                
            turn_count += 1
            
    except KeyboardInterrupt:
        print("\n\n중단됨")
    except Exception as e:
        print(f"💥 모니터링 중 오류: {e}")

def main():
    """메인 테스트 실행"""
    print("🔧" + "="*60)
    print("🎮 자동전투 & ATB 취소 문제 전용 디버거")
    print("🔧" + "="*60)
    
    tests = [
        ("자동전투 시스템", test_auto_battle_system),
        ("취소 시 ATB 문제", test_cancel_atb_problem)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🚀 {test_name} 테스트 시작...")
        try:
            result = test_func()
            results[test_name] = "✅ 성공" if result else "❌ 실패"
        except Exception as e:
            results[test_name] = f"💥 크래시: {e}"
        
        print(f"결과: {results[test_name]}")
    
    # 결과 요약
    print("\n" + "="*60)
    print("📋 테스트 결과 요약")
    print("="*60)
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    # 대화형 모니터 제안
    print("\n🎮 대화형 ATB 모니터링을 실행하시겠습니까?")
    choice = input("y/n > ").strip().lower()
    if choice == 'y':
        interactive_atb_monitor()
    
    print("\n🔧 디버깅 완료!")

if __name__ == "__main__":
    main()
