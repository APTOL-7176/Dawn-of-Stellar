#!/usr/bin/env python3
"""
전투창 시뮬레이션 스크립트
실제 전투 화면과 동일한 UI를 미리 볼 수 있습니다.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

from game.brave_combat import BraveCombatSystem
from game.combat_visual import Color
from game.character import Character

# 임시 Character 클래스 (시뮬레이션용)
class MockCharacter:
    def __init__(self, name, character_class, level=15):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.is_alive = True
        
        # HP/MP 설정
        self.max_hp = 850
        self.current_hp = 640  # 75% 상태
        self.max_mp = 320
        self.current_mp = 240  # 75% 상태
        
        # BRV 설정
        self.brave_points = 1250
        
        # ATB 설정
        self.atb_gauge = 7500  # 75% 상태
        
        # 속도
        self.speed = 95
        
        # 상태이상 플래그들
        self.is_casting = False
        self.is_broken_state = False
        self.is_stunned = False
        self.temp_speed_penalty = 0
        self.is_poisoned = False
        self.is_burning = False
        self.is_frozen = False
        
        # Brave 매니저 모킹
        class MockBraveManager:
            def get_max_brave(self, character):
                return 9999
        
        self.brave_manager = MockBraveManager()

def create_mock_party():
    """모의 파티 생성"""
    party = [
        MockCharacter("코딘", "궁수", 15),
        MockCharacter("아리아", "아크메이지", 14),
        MockCharacter("발키리", "성기사", 16),
        MockCharacter("쉐도우", "암살자", 13)
    ]
    
    # 다양한 상태 설정
    party[0].current_hp = 640  # 건강
    party[1].current_hp = 200  # 부상
    party[1].is_casting = True
    party[2].current_hp = 50   # 위험
    party[2].is_burning = True
    party[3].current_hp = 850  # 풀피
    party[3].atb_gauge = 9800  # 거의 준비됨
    
    return party

def create_mock_enemies():
    """모의 적 생성"""
    enemies = [
        MockCharacter("고블린 전사", "전사", 12),
        MockCharacter("오크 샤먼", "네크로맨서", 14),
        MockCharacter("트롤 우두머리", "광전사", 18)
    ]
    
    # 적 상태 설정
    enemies[0].current_hp = 300
    enemies[0].max_hp = 600
    enemies[0].is_poisoned = True
    
    enemies[1].current_hp = 450
    enemies[1].max_hp = 500
    enemies[1].is_casting = True
    
    enemies[2].current_hp = 1200
    enemies[2].max_hp = 1500
    enemies[2].is_stunned = True
    
    return enemies

def simulate_combat_screen():
    """전투 화면 시뮬레이션"""
    combat = BraveCombatSystem()
    party = create_mock_party()
    enemies = create_mock_enemies()
    
    print(f"{Color.BRIGHT_CYAN}🎯 전투창 시뮬레이션{Color.RESET}")
    print("=" * 80)
    print(f"{Color.BRIGHT_YELLOW}실제 전투에서 보이는 화면과 동일합니다{Color.RESET}")
    print("=" * 80)
    
    # 현재 턴 캐릭터 (첫 번째 파티원)
    current_character = party[0]
    
    # 실제 전투 화면 표시
    combat.show_battle_status(current_character, party, enemies)
    
    print(f"\n{Color.BRIGHT_GREEN}💡 게이지 설명:{Color.RESET}")
    print(f"  💚 HP 게이지: {Color.BRIGHT_GREEN}녹색{Color.RESET} → {Color.YELLOW}노란색{Color.RESET} → {Color.BRIGHT_RED}빨간색{Color.RESET}")
    print(f"  💙 MP 게이지: {Color.BRIGHT_CYAN}밝은 시안색{Color.RESET} 고정")
    print(f"  ⌛ ATB 게이지: {Color.BRIGHT_CYAN}시안색{Color.RESET} (일반) / {Color.BRIGHT_MAGENTA}마젠타{Color.RESET} (캐스팅)")
    print(f"  ⚡ BRV: 숫자만 표시 (게이지 바 제거됨)")
    
    print(f"\n{Color.BRIGHT_BLUE}🎮 애니메이션 효과:{Color.RESET}")
    print(f"  • HP/MP/BRV 변화 시 1.5초 애니메이션")
    print(f"  • 8프레임으로 부드러운 변화")
    print(f"  • 깜빡임 최소화")

if __name__ == "__main__":
    simulate_combat_screen()
