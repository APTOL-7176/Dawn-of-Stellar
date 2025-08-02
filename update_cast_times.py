#!/usr/bin/env python3
"""1-9% 캐스트 타임 스킬들을 10배로 늘리는 스크립트"""

import sys
import re

# 변경할 스킬들 목록 (스킬명: 원래 캐스트타임 -> 새 캐스트타임)
skills_to_update = {
    "무모한 돌격": (8, 80),
    "폭풍의 함대": (2, 20),
    "대자연의 심판": (3, 30),
    "부활술": (2, 20),
    "신벌": (1, 10),
    "신의 심판": (3, 30),
    "깨달음의 경지": (2, 20),
    "마력 폭발": (1, 10),
    "마검의 진리": (2, 20),
    "철학자의 돌": (3, 30),
    "폭발 장치": (1, 10),
    "메카닉 아머": (2, 20)
}

# 파일 읽기
with open('game/new_skill_system.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 각 스킬별로 캐스트 타임 수정
for skill_name, (old_time, new_time) in skills_to_update.items():
    # 스킬 이름을 포함한 블록을 찾아서 cast_time을 수정
    pattern = rf'("name": "{skill_name}".*?"cast_time": ){old_time}(.*?)'
    replacement = rf'\g<1>{new_time}\g<2>'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
# 파일 쓰기
with open('game/new_skill_system.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("모든 1-9% 캐스트 타임 스킬들을 10배로 증가시켰습니다!")
for skill_name, (old_time, new_time) in skills_to_update.items():
    print(f"  {skill_name}: {old_time}% → {new_time}%")
