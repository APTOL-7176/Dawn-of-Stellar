#!/usr/bin/env python3
"""
스킬 시스템 개선 스크립트 - Phase 2
SFX 추가 및 특수 효과 구현
"""

import json
import re

def add_comprehensive_sfx():
    """모든 스킬에 적절한 SFX 추가"""
    
    # FFVII 기반 SFX 매핑
    sfx_patterns = {
        # 물리 공격 계열
        ("베기", "칼", "검", "일섬", "무쌍"): "sword_hit",
        ("강타", "파괴", "격", "타격", "스매시"): "critical_hit",
        ("난타", "연타", "연속", "콤보"): "punch",
        ("찌르기", "돌진", "창", "스피어"): "spear_hit",
        ("화살", "궁술", "사격", "관통"): "bow_shot",
        ("암살", "어쌔신", "그림자"): "slash",
        
        # 마법 계열
        ("화염", "불꽃", "파이어", "점화", "연소"): "fire",
        ("냉기", "얼음", "아이스", "냉동", "빙결"): "ice",
        ("번개", "전기", "썬더", "낙뢰", "전격"): "thunder",
        ("바람", "윈드", "돌풍", "질풍"): "aero",
        ("대지", "어스", "지진", "암석"): "earth",
        ("독", "포이즌", "중독", "산성"): "bio",
        ("어둠", "다크", "암흑", "저주"): "dark",
        ("빛", "성스러운", "홀리", "축복"): "holy",
        ("시간", "타임", "헤이스트", "슬로우"): "time",
        ("공간", "차원", "텔레포트", "워프"): "warp",
        ("중력", "그래비", "블랙홀"): "gravity",
        ("메테오", "운석", "혜성"): "comet",
        ("죽음", "데스", "즉사", "영혼"): "death",
        
        # 마법 일반
        ("마력", "매직", "마법", "주문", "원소"): "magic_cast",
        ("폭발", "버스트", "익스플로전"): "explosion",
        ("레이저", "빔", "광선"): "laser",
        
        # 치유 계열
        ("치유", "회복", "힐", "케어", "리제네"): "heal",
        ("부활", "라이즈", "리바이브"): "revive",
        ("회복마법", "치료"): "cure",
        ("명상", "휴식", "안식"): "rest",
        
        # 버프/디버프
        ("강화", "부스트", "엔챈트", "인핸스"): "enhance",
        ("보호", "프로텍트", "실드", "방어"): "protect",
        ("가속", "헤이스트", "스피드"): "haste",
        ("감속", "슬로우", "지연"): "slow",
        ("독저항", "해독", "디톡스"): "esuna",
        ("침묵", "사일런스", "봉인"): "silence",
        ("마비", "스턴", "기절"): "stop",
        ("수면", "슬립", "최면"): "sleep",
        ("혼란", "컨퓨즈", "광란"): "confuse",
        ("매혹", "참", "베서크"): "berserk",
        
        # 궁극기/특수
        ("궁극", "오의", "비검", "필살", "피니시"): "limit_break",
        ("각성", "변신", "트랜스폼"): "transform",
        ("소환", "서몬", "콜"): "summon",
        ("흡수", "드레인", "흡혈"): "drain",
        ("반사", "리플렉트", "미러"): "reflect",
        ("순간이동", "텔레포트", "워프"): "teleport",
        
        # 직업별 특수
        ("바드", "노래", "음파", "멜로디"): "song",
        ("연금술", "폭탄", "화학"): "alchemy",
        ("기계", "로봇", "사이보그"): "machine",
        ("해적", "보물", "약탈"): "treasure",
        ("무당", "영혼", "스피릿"): "spirit",
        ("철학", "논리", "진리"): "wisdom",
        ("드루이드", "자연", "야생"): "nature",
    }
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🎵 상세 SFX 매핑 진행 중...")
    
    # 스킬별로 매칭
    def get_best_sfx(skill_name):
        skill_lower = skill_name.lower()
        
        # 패턴 매칭으로 가장 적절한 SFX 찾기
        for patterns, sfx in sfx_patterns.items():
            for pattern in patterns:
                if pattern in skill_name:
                    return sfx
        
        # 기본값
        return "magic_cast"
    
    # 각 스킬 블록을 찾아서 SFX 추가/수정
    skill_pattern = r'(\{"name": "([^"]+)"[^}]*\})'
    
    def add_sfx_to_skill(match):
        skill_block = match.group(0)
        skill_name = match.group(2)
        
        # 최적 SFX 결정
        best_sfx = get_best_sfx(skill_name)
        
        # 이미 SFX가 있으면 교체, 없으면 추가
        if '"sfx":' in skill_block:
            skill_block = re.sub(
                r'"sfx": "[^"]*"',
                f'"sfx": "{best_sfx}"',
                skill_block
            )
        else:
            # mp_cost 뒤에 추가
            skill_block = re.sub(
                r'("mp_cost": [^,]+)',
                rf'\1, "sfx": "{best_sfx}"',
                skill_block
            )
        
        return skill_block
    
    content = re.sub(skill_pattern, add_sfx_to_skill, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 상세 SFX 매핑 완료!")

def add_missing_descriptions():
    """누락된 설명 추가"""
    
    descriptions = {
        "방패강타": "방패로 적을 가격하여 BRV 피해를 입힙니다",
        "연속베기": "연속으로 베어 BRV 피해를 누적시킵니다",
        "파괴의일격": "강력한 일격으로 큰 HP 피해를 입힙니다",
        "전사의격노": "분노한 전사의 전력 공격입니다",
        "마력파동": "마력의 파동으로 적을 공격합니다",
        "마력폭발": "마력을 폭발시켜 광범위 피해를 입힙니다",
        "아르카나": "최고급 마법으로 엄청난 피해를 입힙니다",
        "삼연사": "화살 세 발을 연속으로 발사합니다",
        "관통사격": "적을 관통하는 강력한 화살을 발사합니다",
        "독침": "독이 발린 침으로 적을 공격합니다",
        "암살": "그림자에서 나타나 치명적 공격을 가합니다",
        "성스러운타격": "성스러운 힘으로 적을 정화합니다",
        "심판의빛": "신의 심판으로 적을 벌합니다",
        "흡혈베기": "적의 생명력을 흡수하는 공격입니다",
        "흡혈강타": "강력한 흡혈 공격으로 체력을 회복합니다",
        "연환타격": "연속된 타격으로 적을 압도합니다",
        "폭렬권": "폭발하는 주먹으로 적을 공격합니다",
        "음파공격": "음파로 적의 정신을 혼란시킵니다",
        "영혼의노래": "영혼을 울리는 노래로 적을 약화시킵니다",
    }
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📝 스킬 설명 추가 중...")
    
    for skill_name, description in descriptions.items():
        # 해당 스킬 찾기
        pattern = rf'("name": "{skill_name}"[^}}]*)"description": "[^"]*"'
        replacement = rf'\1"description": "{description}"'
        content = re.sub(pattern, replacement, content)
        
        # description이 아예 없는 경우
        pattern = rf'("name": "{skill_name}"[^}}]*)"mp_cost"'
        replacement = rf'\1"description": "{description}", "mp_cost"'
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 스킬 설명 추가 완료!")

def implement_missing_effects():
    """미구현된 특수 효과들 구현"""
    
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔮 특수 효과 구현 중...")
    
    # TIME_MARKED 상태이상 추가 (이미 있다면 스킵)
    if 'TIME_MARKED' not in content:
        # 상태이상 리스트에 추가
        content = content.replace(
            '"BLESSED"',
            '"BLESSED", "TIME_MARKED"'
        )
    
    # ANY_SINGLE 타겟 타입 추가 (이미 있다면 스킵)
    if 'ANY_SINGLE' not in content:
        content = content.replace(
            '"SINGLE"',
            '"SINGLE", "ANY_SINGLE"'
        )
    
    # 흡수 효과가 있는 스킬들에 DRAIN 효과 추가
    drain_skills = [
        "흡혈베기", "흡혈강타", "생명력흡수", "영혼흡수",
        "마나드레인", "에너지흡수"
    ]
    
    for skill in drain_skills:
        # 해당 스킬에 drain_ratio 추가
        pattern = rf'("name": "{skill}"[^}}]*)"damage"'
        replacement = rf'\1"drain_ratio": 0.3, "damage"'
        content = re.sub(pattern, replacement, content)
    
    # 연금술 폭발 스킬들에 EXPLOSION 효과 추가
    explosion_skills = [
        "화학폭발", "대폭발반응", "연금술폭탄", "마법폭탄"
    ]
    
    for skill in explosion_skills:
        pattern = rf'("name": "{skill}"[^}}]*)"damage"'
        replacement = rf'\1"explosion_radius": 2, "damage"'
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 특수 효과 구현 완료!")

if __name__ == "__main__":
    print("🚀 스킬 시스템 개선 Phase 2 시작!\n")
    
    add_comprehensive_sfx()
    print()
    
    add_missing_descriptions()
    print()
    
    implement_missing_effects()
    print()
    
    print("🎉 모든 개선 작업 완료!")
    print("   • 모든 스킬에 적절한 SFX 매핑")
    print("   • 누락된 스킬 설명 추가") 
    print("   • 특수 효과 구현")
    print("   • TIME_MARKED, ANY_SINGLE 타입 추가")
    print("   • 흡수/폭발 효과 구현")
