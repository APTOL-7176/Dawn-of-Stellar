#!/usr/bin/env python3
"""
실제 파워 값들 1.4배 스케일링 스크립트
"""

import re

def scale_power_values():
    """hp_power, brv_power 등 실제 파워 값들을 1.4배로 스케일링"""
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("⚔️ 실제 파워 값들 1.4배 스케일링 중...")
    
    # 변경 사항 추적
    changes = []
    
    # 1. hp_power 값들 스케일링
    def scale_hp_power(match):
        old_value = int(match.group(1))
        new_value = int(old_value * 1.4)
        changes.append(f"hp_power: {old_value} → {new_value}")
        return f'"hp_power": {new_value}'
    
    content = re.sub(r'"hp_power": (\d+)', scale_hp_power, content)
    
    # 2. brv_power 값들 스케일링
    def scale_brv_power(match):
        old_value = int(match.group(1))
        new_value = int(old_value * 1.4)
        changes.append(f"brv_power: {old_value} → {new_value}")
        return f'"brv_power": {new_value}'
    
    content = re.sub(r'"brv_power": (\d+)', scale_brv_power, content)
    
    # 3. 기타 power 관련 값들도 확인
    def scale_other_power(match):
        field = match.group(1)
        old_value = int(match.group(2))
        new_value = int(old_value * 1.4)
        changes.append(f"{field}: {old_value} → {new_value}")
        return f'"{field}": {new_value}'
    
    # attack_power, magic_power 등이 있다면 스케일링
    content = re.sub(r'"(attack_power|magic_power|base_power)": (\d+)', scale_other_power, content)
    
    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 파워 값 스케일링 완료! {len(changes)}개 값 변경")
    
    # 변경 사항 요약 출력
    if changes:
        print("\n📊 변경된 값들 (샘플):")
        for change in changes[:10]:  # 처음 10개만 표시
            print(f"   • {change}")
        
        if len(changes) > 10:
            print(f"   ... 및 {len(changes) - 10}개 더")

def verify_power_scaling():
    """스케일링 결과 확인"""
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📈 스케일링 결과 확인:")
    
    # hp_power 값들 수집
    hp_powers = re.findall(r'"hp_power": (\d+)', content)
    brv_powers = re.findall(r'"brv_power": (\d+)', content)
    
    if hp_powers:
        hp_powers = [int(x) for x in hp_powers]
        print(f"   • hp_power 범위: {min(hp_powers)} ~ {max(hp_powers)}")
        print(f"   • hp_power 평균: {sum(hp_powers) // len(hp_powers)}")
    
    if brv_powers:
        brv_powers = [int(x) for x in brv_powers]
        print(f"   • brv_power 범위: {min(brv_powers)} ~ {max(brv_powers)}")
        print(f"   • brv_power 평균: {sum(brv_powers) // len(brv_powers)}")
    
    print(f"\n   총 hp_power 항목: {len(hp_powers)}개")
    print(f"   총 brv_power 항목: {len(brv_powers)}개")

if __name__ == "__main__":
    print("🎯 실제 파워 값들 1.4배 스케일링 시작!\n")
    
    scale_power_values()
    verify_power_scaling()
    
    print("\n✨ 모든 공격력 값이 1.4배로 강화되었습니다!")
