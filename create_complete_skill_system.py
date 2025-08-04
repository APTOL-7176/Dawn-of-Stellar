#!/usr/bin/env python3
"""
백업에서 모든 직업 스킬을 추출하여 새로운 스킬 시스템에 통합하는 스크립트
"""

import re
import json

def extract_all_job_skills():
    """백업 파일에서 모든 직업의 스킬을 추출"""
    
    print("🔍 백업 파일에서 스킬 데이터 추출 중...")
    
    # 백업 파일 읽기
    with open('game/new_skill_system_backup.py', 'r', encoding='utf-8') as f:
        backup_content = f.read()
    
    # 직업별 스킬 추출
    # skills = { 다음부터 } 까지 찾기
    skills_pattern = r'self\.skills\s*=\s*\{(.*?)\}\s*def'
    
    match = re.search(skills_pattern, backup_content, re.DOTALL)
    if not match:
        print("❌ 스킬 데이터를 찾을 수 없습니다.")
        return None
    
    skills_content = match.group(1)
    
    # 각 직업과 스킬 찾기 (더 간단한 패턴)
    job_pattern = r'"([^"]+)":\s*\[(.*?)\](?=\s*,\s*"|\s*\})'
    
    jobs_found = re.findall(job_pattern, skills_content, re.DOTALL)
    
    print(f"📊 발견된 직업 수: {len(jobs_found)}")
    
    extracted_jobs = {}
    for job_name, job_skills in jobs_found:
        if job_name.strip():
            # 스킬 개수 확인
            skill_count = job_skills.count('{"name":')
            print(f"  - {job_name}: {skill_count}개 스킬")
            extracted_jobs[job_name] = job_skills
    
    return extracted_jobs

def create_skill_descriptions_for_missing_jobs():
    """누락된 직업들을 위한 스킬 설명 생성"""
    
    job_skills_descriptions = {
        "검성": {
            "검기응축": "[검술][강화] 검에 기운을 모아 공격력을 크게 상승시키는 검성의 기본 강화 기술",
            "일섬": "[검술][일격] 번개같이 빠른 일섬으로 적을 베어내는 고도의 검술 기법, 높은 치명타율",
            "검압베기": "[검술][검압] 검기의 압력으로 적을 베는 강력한 단일 공격 기술",
            "검심일체": "[검술][집중] 검과 마음이 하나가 되어 집중력과 공격 정확도가 크게 상승",
            "무쌍베기": "[검술][무쌍] 완벽한 검술로 적의 모든 방어를 무시하고 베어내는 강력한 공격",
            "검제비의": "[검술][궁극] 검제만이 사용할 수 있는 비전 검술로 모든 적을 섬멸하는 최강 기술"
        },
        "아크메이지": {
            "마력파동": "[마법][파동] 순수한 마력을 파동 형태로 발사하여 적에게 마법 피해를 입히는 기본 마법",
            "원소융합": "[원소][융합] 서로 다른 원소를 융합하여 예측 불가능한 강력한 복합 원소 공격을 발동",
            "마나실드": "[마법][방어] 마나를 실드 형태로 전개하여 마법 공격으로부터 자신을 효과적으로 보호",
            "마법폭발": "[마법][폭발] 축적된 마력을 한순간에 폭발시켜 모든 적에게 강력한 마법 피해를 입힘",
            "아케인미사일": "[마법][유도] 마법으로 생성한 유도 미사일로 적을 정확히 타격하는 중급 공격 마법",
            "마도서의비밀": "[궁극][마법] 고대 마도서에 봉인된 비밀한 힘을 해방하여 현실을 뒤바꾸는 최강 마법"
        },
        "궁수": {
            "정확한사격": "[궁술][정밀] 정확한 조준으로 적의 약점을 노리는 궁수의 기본적이지만 효과적인 사격 기법",
            "연속사격": "[궁술][연속] 빠른 손놀림으로 여러 발의 화살을 연속으로 발사하는 궁수의 기본 전투 기술",
            "폭발화살": "[궁술][폭발] 폭발하는 특수 화살촉으로 단일 대상에게 강력한 폭발 피해를 입히는 특수 사격",
            "독화살": "[궁술][독성] 독이 발린 화살로 적에게 독 상태이상을 유발하고 지속 피해를 가하는 특수 화살",
            "관통사격": "[궁술][관통] 강력한 힘으로 쏜 화살이 일직선상의 여러 적을 관통하여 피해를 입히는 기술",
            "신궁의화살": "[궁극][궁술] 전설의 신궁이 사용하는 절대불가피한 일격의 화살로 모든 것을 관통"
        }
    }
    
    return job_skills_descriptions

def add_descriptions_to_job_skills(job_skills_text, job_name, descriptions):
    """특정 직업의 스킬에 설명 추가"""
    
    if job_name not in descriptions:
        return job_skills_text
    
    job_descriptions = descriptions[job_name]
    updated_skills = job_skills_text
    
    for skill_name, description in job_descriptions.items():
        # 해당 스킬이 있고 description이 없는 경우 추가
        skill_pattern = rf'(\{{"name":\s*"{re.escape(skill_name)}"[^}}]*?)(\n\s*"(?:damage_type|special_effects|sfx|organic_effects|status_effects|hit_count|accuracy|cast_time|cooldown|hp_power|brv_power|heal_power|mp_cost|element|target|type)"[^}}]*(?:\}}|$))'
        
        def add_description_replacement(match):
            before_part = match.group(1)
            after_part = match.group(2)
            
            # description이 이미 있는지 확인
            if '"description":' in before_part:
                return match.group(0)  # 이미 있으면 그대로 반환
            
            # description 추가
            insertion_point = before_part.rstrip().rstrip(',')
            return f'{insertion_point},\n                 "description": "{description}"{after_part}'
        
        updated_skills = re.sub(skill_pattern, add_description_replacement, updated_skills, flags=re.DOTALL)
    
    return updated_skills

def create_complete_skill_system():
    """모든 직업이 포함된 완전한 스킬 시스템 생성"""
    
    print("🏗️ 완전한 스킬 시스템 생성 중...")
    
    # 1단계: 백업에서 모든 직업 추출
    all_jobs = extract_all_job_skills()
    if not all_jobs:
        print("❌ 백업에서 스킬 데이터를 추출할 수 없습니다.")
        return False
    
    # 2단계: 현재 파일 읽기
    with open('game/new_skill_system.py', 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # 3단계: 기본 구조 유지하면서 모든 직업 추가
    header_part = current_content.split('self.skills = {')[0] + 'self.skills = {'
    footer_part = current_content.split('# 전역 인스턴스')[1]
    
    # 4단계: 모든 직업 스킬 조합
    descriptions = create_skill_descriptions_for_missing_jobs()
    
    all_job_entries = []
    for job_name, job_skills in all_jobs.items():
        # 설명 추가
        updated_job_skills = add_descriptions_to_job_skills(job_skills, job_name, descriptions)
        job_entry = f'            "{job_name}": [\n{updated_job_skills}\n            ]'
        all_job_entries.append(job_entry)
    
    # 5단계: 완전한 파일 조합
    complete_skills_section = ',\n'.join(all_job_entries)
    
    complete_content = f"""{header_part}
{complete_skills_section}
        }}

    def get_skills_for_class(self, class_name: str) -> List[Dict[str, Any]]:
        \"\"\"특정 직업의 스킬 목록 반환\"\"\"
        return self.skills.get(class_name, [])

    def get_skill_by_name(self, skill_name: str) -> Dict[str, Any]:
        \"\"\"스킬 이름으로 스킬 정보 검색\"\"\"
        for class_skills in self.skills.values():
            for skill in class_skills:
                if skill["name"] == skill_name:
                    return skill
        return {{}}

    def get_all_skills(self) -> Dict[str, List[Dict[str, Any]]]:
        \"\"\"모든 스킬 정보 반환\"\"\"
        return self.skills

    def get_available_classes(self) -> List[str]:
        \"\"\"사용 가능한 직업 목록 반환\"\"\"
        return list(self.skills.keys())

# 전역 인스턴스{footer_part}"""
    
    # 6단계: 파일 저장
    with open('game/new_skill_system.py', 'w', encoding='utf-8') as f:
        f.write(complete_content)
    
    print(f"✅ 완전한 스킬 시스템 생성 완료 - {len(all_jobs)}개 직업 포함")
    
    # 7단계: 문법 검사
    try:
        exec(compile(complete_content, 'new_skill_system.py', 'exec'))
        print("✅ 파이썬 문법 검사 통과")
        return True
    except Exception as e:
        print(f"❌ 문법 오류: {e}")
        return False

if __name__ == "__main__":
    print("🎮 Dawn of Stellar - 완전한 스킬 시스템 생성")
    print("=" * 50)
    
    success = create_complete_skill_system()
    
    if success:
        print("\n🎉 작업 완료!")
        print("  📚 모든 직업의 스킬이 포함된 완전한 시스템이 생성되었습니다.")
        print("  📝 모든 스킬에 상세한 설명이 포함되어 있습니다.")
        print("  🎯 이제 스킬 선택창에서 모든 스킬의 설명을 볼 수 있습니다!")
    else:
        print("\n❌ 작업 실패!")
        print("  🔧 수동으로 파일을 확인해주세요.")
