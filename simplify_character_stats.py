#!/usr/bin/env python3
"""
캐릭터 스탯 시스템 단순화 스크립트
- 모든 클래스의 hp_bonus를 1.0으로 통일
- 모든 클래스의 mp_efficiency를 1.0으로 통일  
- BRV 관련 복잡한 배율들을 단순화
"""

import re

def simplify_character_file():
    """character.py 파일의 복잡한 배율들을 단순화"""
    
    # character.py 파일 읽기
    with open('game/character.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 모든 hp_bonus를 1.0으로 통일
    content = re.sub(r'"hp_bonus":\s*[\d.]+', '"hp_bonus": 1.0', content)
    
    # 2. 모든 mp_efficiency를 1.0으로 통일
    content = re.sub(r'"mp_efficiency":\s*[\d.]+', '"mp_efficiency": 1.0', content)
    
    # 3. BRV 관련 기본값들을 단순화
    brv_replacements = [
        # BRV 기본값 통일
        (r'self\.int_brv\s*=.*', 'self.int_brv = 100  # 기본 BRV'),
        (r'self\.max_brv\s*=.*', 'self.max_brv = 200  # 최대 BRV'), 
        (r'self\.current_brv\s*=.*', 'self.current_brv = 100  # 현재 BRV'),
        
        # BRV 계산 공식 단순화
        (r'int\(base_brv \* brv_modifier\)', 'base_brv'),  # 배율 제거
        (r'int\(base_atk \* [\d.]+\)', 'base_atk'),  # 공격력 배율 제거
    ]
    
    for pattern, replacement in brv_replacements:
        content = re.sub(pattern, replacement, content)
    
    # 4. 기본 스탯값들을 더 단순하게 조정 (선택사항)
    # 모든 클래스의 기본 HP를 비슷한 범위로 조정
    simple_hp_values = {
        '"hp": 216': '"hp": 150',  # 전사
        '"hp": 121': '"hp": 120',  # 아크메이지  
        '"hp": 164': '"hp": 140',  # 궁수
        '"hp": 150': '"hp": 130',  # 도적
        '"hp": 194': '"hp": 160',  # 성기사
        '"hp": 183': '"hp": 155',  # 암흑기사
        '"hp": 173': '"hp": 145',  # 몽크
        '"hp": 112': '"hp": 110',  # 바드
        '"hp": 134': '"hp": 125',  # 암살자
        '"hp": 107': '"hp": 115',  # 정령술사
    }
    
    for old_hp, new_hp in simple_hp_values.items():
        content = content.replace(old_hp, new_hp)
    
    # 5. 파일 저장
    with open('game/character.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 캐릭터 스탯 시스템 단순화 완료!")
    print("📝 변경 사항:")
    print("   • 모든 클래스 hp_bonus: 1.0 통일")
    print("   • 모든 클래스 mp_efficiency: 1.0 통일") 
    print("   • BRV 기본값 단순화 (100/200/100)")
    print("   • HP 값들을 비슷한 범위로 조정")

if __name__ == "__main__":
    simplify_character_file()
