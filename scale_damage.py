#!/usr/bin/env python3
"""
데미지 스케일 1.4배 조정 스크립트
"""

import re

def scale_damage_values():
    """모든 데미지 값을 1.4배로 스케일링"""
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("⚔️ 데미지 스케일 1.4배 적용 중...")
    
    # damage 값을 찾아서 1.4배 적용
    def scale_damage(match):
        key = match.group(1)  # "damage" 또는 "base_damage"
        value = int(match.group(2))
        new_value = int(value * 1.4)
        return f'"{key}": {new_value}'
    
    # damage: 숫자 패턴 찾기
    damage_pattern = r'"((?:base_)?damage)": (\d+)'
    content = re.sub(damage_pattern, scale_damage, content)
    
    # brv_damage 값도 스케일링
    def scale_brv_damage(match):
        key = match.group(1)
        value = int(match.group(2))
        new_value = int(value * 1.4)
        return f'"{key}": {new_value}'
    
    brv_pattern = r'"(brv_damage)": (\d+)'
    content = re.sub(brv_pattern, scale_brv_damage, content)
    
    # 배율 값들도 조정 (multiplier)
    def scale_multiplier(match):
        key = match.group(1)
        value = float(match.group(2))
        new_value = round(value * 1.4, 1)
        return f'"{key}": {new_value}'
    
    multiplier_pattern = r'"(damage_multiplier|brv_multiplier)": ([\d.]+)'
    content = re.sub(multiplier_pattern, scale_multiplier, content)
    
    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 데미지 스케일 1.4배 적용 완료!")
    print("   • damage 값들 1.4배 증가")
    print("   • brv_damage 값들 1.4배 증가") 
    print("   • damage_multiplier 값들 1.4배 증가")

def verify_changes():
    """변경사항 확인"""
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📊 변경된 데미지 값 샘플:")
    
    # 몇 가지 예시 출력
    damage_matches = re.findall(r'"damage": (\d+)', content)
    brv_matches = re.findall(r'"brv_damage": (\d+)', content)
    
    if damage_matches:
        print(f"   • damage 값 예시: {damage_matches[:5]}")
    
    if brv_matches:
        print(f"   • brv_damage 값 예시: {brv_matches[:5]}")
    
    print(f"\n   총 damage 항목: {len(damage_matches)}개")
    print(f"   총 brv_damage 항목: {len(brv_matches)}개")

if __name__ == "__main__":
    print("🎯 데미지 스케일링 시작!\n")
    
    scale_damage_values()
    verify_changes()
    
    print("\n✨ 데미지 스케일링 완료!")
    print("   모든 스킬 데미지가 1.4배로 조정되었습니다.")
