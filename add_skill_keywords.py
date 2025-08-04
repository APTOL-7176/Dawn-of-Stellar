#!/usr/bin/env python3
"""
스킬 설명에 키워드를 자동으로 추가하는 스크립트
"""

import re
import sys
import os

# 스킬 타입별 키워드 매핑
SKILL_TYPE_KEYWORDS = {
    'SkillType.BRV_ATTACK': '[BRV]',
    'SkillType.HP_ATTACK': '[HP]',
    'SkillType.BRV_HP_ATTACK': '[BRV+HP]',
    'SkillType.ULTIMATE': '[ULTIMATE]',
    'SkillType.BUFF': '[BUFF]',
    'SkillType.DEBUFF': '[DEBUFF]',
    'SkillType.HEAL': '[HEAL]',
    'SkillType.SUPPORT': '[SUPPORT]',
    'SkillType.COUNTER': '[COUNTER]',
    'SkillType.SPECIAL': '[SPECIAL]',
    'SkillType.STATUS': '[STATUS]'
}

def add_keywords_to_skill_file(file_path):
    """스킬 파일에 키워드를 추가합니다."""
    
    print(f"스킬 파일 처리 중: {file_path}")
    
    # 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 스킬 패턴 찾기 및 키워드 추가
    skill_pattern = r'(\{"name":[^}]+?"type": (SkillType\.\w+),[^}]+?"description": ")([^"]+)(")'
    
    def replace_description(match):
        skill_start = match.group(1)
        skill_type = match.group(2)
        description = match.group(3)
        skill_end = match.group(4)
        
        # 이미 키워드가 있는지 확인
        if description.startswith('[') and ']' in description:
            return match.group(0)  # 이미 키워드가 있으면 변경하지 않음
        
        # 스킬 타입에 따른 키워드 추가
        keyword = SKILL_TYPE_KEYWORDS.get(skill_type, '[SKILL]')
        new_description = f"{keyword} {description}"
        
        return f"{skill_start}{new_description}{skill_end}"
    
    # 정규식으로 모든 스킬 설명 변경
    updated_content = re.sub(skill_pattern, replace_description, content, flags=re.MULTILINE | re.DOTALL)
    
    # 변경된 내용이 있는지 확인
    if updated_content != content:
        # 파일 백업
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"백업 파일 생성: {backup_path}")
        
        # 업데이트된 내용 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"스킬 키워드 추가 완료!")
        
        # 변경된 개수 계산
        original_skills = len(re.findall(r'"description":', content))
        updated_skills = len(re.findall(r'"description": "\[', updated_content))
        print(f"총 {original_skills}개 스킬 중 {updated_skills}개에 키워드 추가")
        
    else:
        print("변경할 스킬이 없습니다. (이미 모든 스킬에 키워드가 있음)")

def main():
    """메인 함수"""
    
    skill_file = "game/new_skill_system.py"
    
    if not os.path.exists(skill_file):
        print(f"오류: {skill_file} 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    try:
        add_keywords_to_skill_file(skill_file)
        print("\n스킬 키워드 추가 작업이 완료되었습니다!")
        print("\n추가된 키워드 유형:")
        for skill_type, keyword in SKILL_TYPE_KEYWORDS.items():
            print(f"  {skill_type} → {keyword}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
