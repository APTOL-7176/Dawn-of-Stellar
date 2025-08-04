#!/usr/bin/env python3
"""
모든 스킬에 적절한 SFX 매칭하는 스크립트 - audio.py 기반
"""

import re

def create_skill_sfx_mapping():
    """스킬별 적절한 SFX 매핑 생성 - audio.py의 sfx_mapping 기반"""
    
    skill_sfx_mapping = {
        # 검술/물리 공격
        "방패강타": "sword_hit",
        "연속베기": "sword_hit", 
        "파괴의일격": "critical_hit",
        "전사의격노": "critical_hit",
        "검기응축": "haste",
        "일섬": "critical_hit",
        "검압베기": "sword_hit",
        "검심일체": "haste",
        "무쌍베기": "critical_hit",
        "검성비검": "limit_break",
        
        # 아크메이지 마법
        "마력파동": "magic_cast",
        "마력폭발": "fire3",
        "메타마법": "magic_cast",
        "마력흡수": "magic_cast",
        "마법진": "magic_cast",
        "아르카나": "ultima",
        
        # 궁수/원거리
        "집중사격": "gun_hit",
        "삼연사": "gun_hit",
        "관통사격": "gun_critical",
        "독화살": "poison",
        "화살비": "gun_hit",
        "절대명중": "gun_critical",
        
        # 암살/도적
        "독침": "poison",
        "암살": "critical_hit",
        "그림자습격": "teleport",
        "그림자처형": "limit_break",
        
        # 성기사
        "성스러운타격": "staff_hit",
        "축복": "protect",
        "치유의빛": "heal",
        "부활": "phoenix_down",
        "심판의빛": "thunder3",
        "천사의강림": "limit_break",
        
        # 암흑기사
        "흡혈베기": "sword_hit",
        "흡혈강타": "critical_hit",
        "어둠의힘": "berserk",
        "생명흡수": "magic_cast",
        "어둠의영역": "magic_cast",
        "어둠의심판": "limit_break",
        
        # 치유/지원 (다양한 회복 스킬들)
        "치유": "heal",
        "대치유술": "heal3",
        "축복": "protect",
        "부활": "phoenix_down",
        "신의심판": "thunder3",
        "치유의빛": "heal2",
        "회복술": "heal",
        "물정령치유": "heal",
        "명상": "heal",
        "정령의치유": "heal",
        "바다의치유": "heal",
        "치유의선율": "heal",
        "천상의치유가": "heal3",
        "무당의춤": "heal",
        "자연의치유": "heal2",
        "자동수리": "heal",
        
        # 버프/디버프
        "철벽방어": "protect",
        "전투함성": "haste",
        "시간가속": "haste",
        "시간왜곡": "magic_cast",
        "순간이동": "teleport",
        "차원장막": "shell",
        "잔상분신": "haste",
        "미래예지": "magic_cast",
        
        # 원소 마법
        "화염": "fire",
        "화염구": "fire2",
        "대화염": "fire3",
        "냉기": "ice",
        "얼음창": "ice3",
        "번개": "thunder",
        "번개폭풍": "thunder3",
        "대지진동": "magic_cast",
        "바람칼날": "magic_cast",
        "화염정령": "fire2",
        "얼음정령": "ice",
        "번개정령": "thunder2",
        "대지정령": "magic_cast",
        "바람정령": "magic_cast",
        
        # 시간술사 특수
        "시간왜곡": "stop",
        "시간되돌리기": "magic_cast",
        "시간정지": "stop",
        "시공간붕괴": "ultima",
        
        # 차원술사 (회피 특화)
        "차원장막": "vanish",
        "잔상분신": "teleport",
        "공간도약": "teleport",
        "차원미로": "magic_cast",
        "회피반격": "critical_hit",
        "무적의경지": "limit_break",
        
        # 몽크/격투
        "기수련": "haste",
        "연속주먹": "punch_hit",
        "명상": "heal",
        "기폭발": "punch_critical",
        "철의주먹": "punch_critical",
        "깨달음의경지": "limit_break",
        
        # 바드 음악
        "음파공격": "magic_cast",
        "영혼의노래": "haste",
        "치유의선율": "heal",
        "전쟁의노래": "haste",
        "천상의치유가": "heal3",
        "레퀴엠": "limit_break",
        
        # 기계공학자
        "레이저사격": "gun_hit",
        "메가레이저": "gun_critical",
        "자동포탑": "gun_hit",
        "메카닉수리": "heal",
        "자동수리": "heal",
        "오버드라이브": "limit_break",
        
        # 정령술사/무당
        "정령교감": "haste",
        "정령소환": "summon",
        "무당의춤": "heal",
        "영혼타격": "magic_cast",
        "영혼분리": "limit_break",
        
        # 해적
        "이도류난타": "sword_hit",
        "해적의보물": "treasure_open",
        "바다의분노": "limit_break",
        "바다의치유": "heal",
        
        # 사무라이/무사
        "거합베기": "critical_hit",
        "무사도비의": "limit_break",
        "정신집중": "haste",
        "무사의정신력": "heal",
        
        # 연금술사
        "화학폭발": "fire2",
        "대폭발반응": "fire3", 
        "고급포션제조": "heal2",
        "연성술": "magic_cast",
        
        # 철학자
        "진리탐구": "haste",
        "논리적반박": "slow",
        "진리의깨달음": "limit_break",
        
        # 드루이드
        "동물변신": "transform",
        "늑대변신": "transform",
        "곰변신": "transform",
        "독수리변신": "transform",
        "변신해제": "transform",
        "자연의분노": "thunder3",
        "가이아의분노": "ultima",
        
        # 신관/성직자
        "신의가호": "protect",
        "성스러운빛": "heal",
        "대치유술": "heal3",
        "부활술": "phoenix_down",
        "축복의빛": "heal2",
        "신의심판": "thunder3",
        "평화의기도": "protect",
        "정화의빛": "heal",
        "신성한치유": "heal2",
        "침묵의서약": "silence",
        "순교자의길": "magic_cast",
    }
    
    return skill_sfx_mapping

def apply_sfx_to_skills():
    """스킬 파일에 SFX 정보 추가 - audio.py 호환"""
    
    skill_sfx_mapping = create_skill_sfx_mapping()
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 스킬 정의 패턴 찾기
    skill_pattern = r'({"name": "([^"]+)"[^}]*?)(})'
    
    def add_sfx_to_skill(match):
        skill_def = match.group(1)
        skill_name = match.group(2)
        closing_brace = match.group(3)
        
        # 이미 sfx가 있으면 건드리지 않음
        if '"sfx"' in skill_def:
            return match.group(0)
        
        # 스킬명에 대응하는 SFX 찾기 (정확한 매칭 우선)
        sfx = skill_sfx_mapping.get(skill_name)
        
        # 부분 매칭으로 SFX 결정
        if not sfx:
            for skill_key, sfx_value in skill_sfx_mapping.items():
                if skill_key in skill_name:
                    sfx = sfx_value
                    break
        
        # 패턴 매칭으로 SFX 결정
        if not sfx:
            if any(word in skill_name for word in ["베기", "강타", "일격", "타격", "검"]):
                sfx = "sword_hit"
            elif any(word in skill_name for word in ["주먹", "펀치", "격투"]):
                sfx = "punch_hit"
            elif any(word in skill_name for word in ["치유", "회복", "힐링"]):
                sfx = "heal"
            elif any(word in skill_name for word in ["화염", "불", "파이어"]):
                sfx = "fire"
            elif any(word in skill_name for word in ["냉기", "얼음", "아이스", "빙결"]):
                sfx = "ice"
            elif any(word in skill_name for word in ["번개", "전기", "볼트", "감전"]):
                sfx = "thunder"
            elif any(word in skill_name for word in ["축복", "강화", "버프"]):
                sfx = "protect"
            elif any(word in skill_name for word in ["저주", "약화", "디버프"]):
                sfx = "slow"
            elif any(word in skill_name for word in ["궁극", "비검", "오의", "분노"]):
                sfx = "limit_break"
            elif any(word in skill_name for word in ["이동", "순간", "텔레포트"]):
                sfx = "teleport"
            elif any(word in skill_name for word in ["화살", "사격", "총"]):
                sfx = "gun_hit"
            elif any(word in skill_name for word in ["마법", "술", "진", "파동"]):
                sfx = "magic_cast"
            elif any(word in skill_name for word in ["폭발", "붕괴", "파괴"]):
                sfx = "fire3"
            else:
                sfx = "magic_cast"  # 기본 SFX
        
        # SFX 추가 - organic_effects 앞에 삽입
        if '"organic_effects"' in skill_def:
            updated_def = re.sub(
                r'("organic_effects")',
                r'"sfx": "' + sfx + '", \\1',
                skill_def
            )
        elif '"description"' in skill_def:
            # description 뒤에 추가
            updated_def = re.sub(
                r'("description": "[^"]+"),',
                r'\\1, "sfx": "' + sfx + '",',
                skill_def
            )
        else:
            # 마지막에 추가
            updated_def = skill_def + ', "sfx": "' + sfx + '"'
        
        return updated_def + closing_brace
    
    # 모든 스킬에 SFX 추가
    updated_content = re.sub(skill_pattern, add_sfx_to_skill, content, flags=re.DOTALL)
    
    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ 모든 스킬에 적절한 SFX가 매칭되었습니다!")
    
    # 적용된 SFX 요약 출력
    sfx_types = set(skill_sfx_mapping.values())
    print(f"📊 사용된 SFX 타입: {len(sfx_types)}개")
    for sfx_type in sorted(sfx_types):
        count = list(skill_sfx_mapping.values()).count(sfx_type)
        print(f"   • {sfx_type}: {count}개 스킬")

if __name__ == "__main__":
    apply_sfx_to_skills()
