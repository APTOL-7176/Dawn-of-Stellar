#!/usr/bin/env python3
"""
모든 치유 스킬을 공격력/마법력 중 높은 수치 기반으로 변경하는 스크립트
"""

import re

def convert_heal_powers():
    """heal_power 값들을 공격력/마법력 기반 배율로 변경"""
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # heal_power 값 변환 매핑 (기존 값 -> 새로운 배율)
    # 높은 수치의 30-60% 정도로 조정
    heal_power_conversions = {
        '"heal_power": 200': '"heal_power": 5.0',  # 부활술 등 최강 치유
        '"heal_power": 120': '"heal_power": 3.0',  # 궁극기급 치유
        '"heal_power": 110': '"heal_power": 2.8',  # 매우 강력한 치유
        '"heal_power": 90': '"heal_power": 2.3',   # 강력한 치유
        '"heal_power": 80': '"heal_power": 2.0',   # 일반 강력 치유
        '"heal_power": 75': '"heal_power": 1.9',   # 일반 치유
        '"heal_power": 70': '"heal_power": 1.8',   # 기본 치유
        '"heal_power": 65': '"heal_power": 1.6',   # 약한 치유
        '"heal_power": 60': '"heal_power": 1.5',   # 매우 약한 치유
    }
    
    # 이미 변경된 것들은 건드리지 않기 위해 소수점 값들 제외
    already_converted = ['2.2', '1.9', '2.3']
    
    # heal_power 값 변경
    for old_value, new_value in heal_power_conversions.items():
        # 이미 변경된 것들은 건드리지 않음
        skip = False
        for converted in already_converted:
            if converted in new_value:
                # 이미 파일에 해당 값이 있는지 확인
                if new_value in content:
                    continue
        
        content = content.replace(old_value, new_value)
    
    # 설명에 공격력/마법력 기반임을 명시
    heal_descriptions = [
        ('"heal_power": 5.0', ' (공격력/마법력 중 높은 수치 x5.0)'),
        ('"heal_power": 3.0', ' (공격력/마법력 중 높은 수치 x3.0)'),
        ('"heal_power": 2.8', ' (공격력/마법력 중 높은 수치 x2.8)'),
        ('"heal_power": 2.0', ' (공격력/마법력 중 높은 수치 x2.0)'),
        ('"heal_power": 1.8', ' (공격력/마법력 중 높은 수치 x1.8)'),
        ('"heal_power": 1.6', ' (공격력/마법력 중 높은 수치 x1.6)'),
        ('"heal_power": 1.5', ' (공격력/마법력 중 높은 수치 x1.5)'),
    ]
    
    # 설명에 배율 정보 추가
    for heal_power, multiplier_text in heal_descriptions:
        # 해당 heal_power를 가진 스킬 찾기
        pattern = rf'({{[^}}]*{re.escape(heal_power)}[^}}]*"description": "[^"]*?)("[^}}]*}})'
        
        def add_multiplier(match):
            description_part = match.group(1)
            rest_part = match.group(2)
            
            # 이미 공격력/마법력 기반 설명이 있으면 건드리지 않음
            if '공격력/마법력' in description_part or '마법력 x' in description_part:
                return match.group(0)
            
            # 설명 끝에 배율 정보 추가
            return description_part + multiplier_text + rest_part
        
        content = re.sub(pattern, add_multiplier, content, flags=re.DOTALL)
    
    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("모든 치유 스킬이 공격력/마법력 기반으로 변경되었습니다!")

if __name__ == "__main__":
    convert_heal_powers()
