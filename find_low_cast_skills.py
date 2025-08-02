#!/usr/bin/env python3
"""1-9% 캐스트 타임을 가진 스킬들을 찾는 스크립트"""

import sys
sys.path.append('.')
from game.new_skill_system import new_skill_system

print("=== 1-9% 캐스트 타임을 가진 스킬들 ===")
found_skills = []

for class_name in new_skill_system.skills_by_class.keys():
    skills = new_skill_system.skills_by_class[class_name]
    for skill in skills:
        if 'cast_time' in skill:
            cast_time = skill['cast_time']
            if 1 <= cast_time <= 9:
                skill_info = f"{class_name}: {skill['name']} - cast_time: {cast_time}"
                print(skill_info)
                found_skills.append((class_name, skill['name'], cast_time))

print(f"\n총 {len(found_skills)}개의 스킬이 발견되었습니다.")
