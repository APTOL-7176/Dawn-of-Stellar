#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""첫 번째 _get_enemy_skills_old 메소드를 완전히 제거하는 스크립트"""

def remove_first_method():
    with open('enemy_system.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_lines = False
    
    for i, line in enumerate(lines):
        if '# def _get_enemy_skills_old(self) -> List[Dict]:' in line:
            print(f"Found start of old method at line {i+1}")
            skip_lines = True
            continue
        elif skip_lines and line.strip().startswith('def ') and '_get_enemy_skills_old' not in line:
            print(f"Found end of old method at line {i+1}")
            skip_lines = False
            new_lines.append(line)
        elif not skip_lines:
            new_lines.append(line)
        # skip_lines가 True인 경우 라인을 추가하지 않음 (건너뜀)
    
    # 새 파일로 저장
    with open('enemy_system.py', 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(new_lines)
    
    print(f"Original lines: {len(lines)}, New lines: {len(new_lines)}")
    print("First method completely removed!")

if __name__ == "__main__":
    remove_first_method()
