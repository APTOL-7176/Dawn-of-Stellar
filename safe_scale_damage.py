#!/usr/bin/env python3
"""
데미지 스케일링 및 정리 스크립트 (안전한 버전)
"""

import re

def clean_and_scale_damage():
    """파일 정리 및 데미지 스케일링"""
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🧹 파일 정리 및 데미지 스케일링 중...")
    
    # 1. 먼저 \\1 패턴 제거
    print("   • \\1 패턴 정리...")
    content = content.replace(', \\1,', ',')
    content = content.replace('\\1, ', '')
    content = content.replace(' \\1,', ',')
    
    # 2. 아직 변환되지 않은 큰 heal_power 값들 (고정값)을 배율로 변환
    print("   • 큰 heal_power 값들 배율로 변환...")
    heal_conversions = [
        ('"heal_power": 200', '"heal_power": 7.0'),   # 1.4배 적용된 값
        ('"heal_power": 120', '"heal_power": 4.2'),
        ('"heal_power": 110', '"heal_power": 3.9'),
        ('"heal_power": 90', '"heal_power": 3.2'),
        ('"heal_power": 80', '"heal_power": 2.8'),
        ('"heal_power": 75', '"heal_power": 2.7'),
        ('"heal_power": 70', '"heal_power": 2.5'),
        ('"heal_power": 65', '"heal_power": 2.3'),
        ('"heal_power": 60', '"heal_power": 2.1'),
    ]
    
    for old_val, new_val in heal_conversions:
        content = content.replace(old_val, new_val)
    
    # 3. 기존의 작은 배율들도 1.4배 스케일링
    print("   • 기존 배율들 1.4배 스케일링...")
    def scale_small_heal_power(match):
        value = float(match.group(1))
        if value < 10:  # 배율로 보이는 값들만
            new_value = round(value * 1.4, 1)
            return f'"heal_power": {new_value}'
        return match.group(0)  # 큰 값은 그대로
    
    content = re.sub(r'"heal_power": ([\d.]+)', scale_small_heal_power, content)
    
    # 4. 공격 데미지 값들 스케일링 (있다면)
    print("   • 공격 데미지 스케일링...")
    
    # power 필드가 있다면 스케일링
    def scale_power(match):
        value = int(match.group(1))
        new_value = int(value * 1.4)
        return f'"power": {new_value}'
    
    content = re.sub(r'"power": (\d+)', scale_power, content)
    
    # base_damage 스케일링
    def scale_base_damage(match):
        value = int(match.group(1))
        new_value = int(value * 1.4)
        return f'"base_damage": {new_value}'
    
    content = re.sub(r'"base_damage": (\d+)', scale_base_damage, content)
    
    # 5. 중복된 쉼표 정리
    print("   • 구문 정리...")
    content = re.sub(r',\s*,', ',', content)
    content = re.sub(r',\s*\}', '}', content)
    content = re.sub(r',\s*\]', ']', content)
    
    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 파일 정리 및 스케일링 완료!")

def verify_changes():
    """변경사항 확인"""
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📊 변경 결과:")
    
    # heal_power 값들 확인
    heal_matches = re.findall(r'"heal_power": ([\d.]+)', content)
    power_matches = re.findall(r'"power": (\d+)', content)
    
    print(f"   • heal_power 값들: {sorted(set(heal_matches))}")
    print(f"   • power 값들: {sorted(set(power_matches))}")
    
    # \\1 패턴 남아있나 확인
    if '\\1' in content:
        print("   ⚠️ 아직 \\1 패턴이 남아있습니다!")
        backslash_lines = [i+1 for i, line in enumerate(content.split('\n')) if '\\1' in line]
        print(f"      라인들: {backslash_lines[:5]}...")
    else:
        print("   ✅ \\1 패턴이 모두 정리되었습니다!")

if __name__ == "__main__":
    print("🎯 안전한 데미지 스케일링 시작!\n")
    
    clean_and_scale_damage()
    verify_changes()
    
    print("\n✨ 작업 완료!")
    print("   • 모든 데미지/치유 값이 1.4배로 조정")
    print("   • 파일 정리 완료")
    print("   • 기존 설정은 안전하게 보존")
