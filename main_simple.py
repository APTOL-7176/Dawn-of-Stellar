#!/usr/bin/env python3
"""
Dawn Of Stellar - 간단한 메인 파일
PyInstaller 호환성을 위한 최소화 버전
"""

import sys
import os

def main():
    """간단한 메인 함수"""
    try:
        print("게임 시작...")
        
        # 기본적인 게임 시스템 import
        from game.character import Character
        from game.brave_combat import BraveCombatSystem
        
        print("모듈 로딩 완료")
        
        # 캐릭터 생성 테스트
        test_char = Character("테스트", "전사")
        print(f"캐릭터 생성: {test_char.name} ({test_char.character_class})")
        
        # 전투 시스템 테스트  
        combat_system = BraveCombatSystem()
        print("전투 시스템 초기화 완료")
        
        print("게임이 정상적으로 초기화되었습니다.")
        input("엔터를 누르면 종료합니다...")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        input("엔터를 누르면 종료합니다...")

if __name__ == "__main__":
    main()
