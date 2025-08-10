"""
간단한 화면 클리어 테스트 - 중복 출력 방지
"""

import os
import time

def simple_clear():
    """가장 간단한 화면 클리어"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def test_simple_display():
    """간단한 화면 표시 테스트"""
    print("기존 내용 1")
    print("기존 내용 2") 
    print("기존 내용 3")
    print()
    print("3초 후 화면이 클리어되고 새 내용이 나타납니다...")
    
    time.sleep(3)
    
    # 간단한 클리어
    simple_clear()
    
    # 새 내용 표시
    print("="*50)
    print(" 전투 화면 테스트 ".center(50, "="))
    print("="*50)
    print()
    print("🛡️ 전사 HP: 100/100")
    print("🏹 궁수 HP: 80/80")
    print()
    print("👹 고블린 HP: 60/100")
    print()
    print("="*50)
    print("[1] 공격")
    print("[2] 방어") 
    print("[3] 스킬")
    print("="*50)
    print()
    print("✅ 화면이 깔끔하게 표시되었나요?")
    print("✅ 중복되거나 이상한 내용이 없나요?")

if __name__ == "__main__":
    test_simple_display()
