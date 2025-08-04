#!/usr/bin/env python3
"""
모든 스킬에 적절한 SFX(효과음) 추가 스크립트
"""

import re

# SFX 매핑 딕셔너리
sfx_mapping = {
    # 공격 스킬
    "방패강타": "shield_bash",
    "철벽방어": "armor_up",
    "연속베기": "sword_combo",
    "전투함성": "war_cry",
    "파괴의일격": "heavy_strike",
    "전사의격노": "berserker_rage_sfx",
    
    # 검술 스킬
    "검기응축": "sword_aura",
    "일섬": "quickdraw",
    "검압베기": "sword_pressure_sfx",
    "검심일체": "sword_unity_sfx",
    "무쌍베기": "flawless_cut",
    "검성비검": "sword_saint_ultimate",
    
    # 마법 스킬
    "마력파동": "mana_wave",
    "마력폭발": "mana_explosion",
    "메타마법": "metamagic",
    "마력흡수": "mana_drain",
    "마법진": "magic_circle",
    "아르카나": "arcana_ultimate",
    
    # 궁수 스킬
    "집중사격": "precise_shot",
    "삼연사": "triple_shot",
    "관통사격": "piercing_shot",
    "독화살": "poison_arrow",
    "화살비": "arrow_rain",
    "절대명중": "absolute_shot",
    
    # 회복/지원 스킬
    "치유": "heal",
    "대치유술": "greater_heal",
    "회복술": "restore",
    "부활술": "resurrection",
    "축복": "blessing",
    "신의심판": "divine_judgment",
    
    # 디버프 스킬
    "독침": "poison_dart",
    "암살": "assassinate",
    "저주": "curse",
    "침묵": "silence_spell",
    "공포": "fear",
    "혼란": "confusion",
    
    # 원소 마법
    "화염": "fire_spell",
    "냉기": "ice_spell",
    "번개": "lightning_spell",
    "대지": "earth_spell",
    "바람": "wind_spell",
    "물": "water_spell",
    
    # 특수 효과
    "폭발": "explosion",
    "충격파": "shockwave",
    "시간": "time_magic",
    "공간": "space_magic",
    "어둠": "dark_magic",
    "빛": "light_magic",
}

def get_sfx_for_skill(skill_name, skill_type, element=None):
    """스킬 이름, 타입, 속성을 기반으로 적절한 SFX 반환"""
    
    # 직접 매핑된 SFX가 있는지 확인
    for key, sfx in sfx_mapping.items():
        if key in skill_name:
            return sfx
    
    # 스킬 타입 기반 SFX
    if "HP_ATTACK" in str(skill_type) or "BRV_HP_ATTACK" in str(skill_type):
        if element:
            if "FIRE" in str(element):
                return "fire_attack"
            elif "ICE" in str(element):
                return "ice_attack"
            elif "LIGHTNING" in str(element):
                return "lightning_attack"
            elif "EARTH" in str(element):
                return "earth_attack"
            elif "LIGHT" in str(element):
                return "light_attack"
            elif "DARK" in str(element):
                return "dark_attack"
        return "physical_attack"
    
    elif "BRV_ATTACK" in str(skill_type):
        return "weapon_hit"
    
    elif "HEAL" in str(skill_type):
        return "heal_spell"
    
    elif "BUFF" in str(skill_type):
        return "buff_spell"
    
    elif "DEBUFF" in str(skill_type):
        return "debuff_spell"
    
    elif "ULTIMATE" in str(skill_type):
        return "ultimate_skill"
    
    elif "SPECIAL" in str(skill_type):
        return "special_effect"
    
    # 기본 SFX
    return "skill_cast"

def add_sfx_to_file():
    """스킬 파일에 SFX 추가"""
    file_path = "game/new_skill_system.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 이미 sfx가 있는 스킬은 건드리지 않기 위해 체크
    if '"sfx"' in content:
        print("일부 스킬에 이미 SFX가 있습니다.")
    
    # 스킬 정의 패턴 찾기
    skill_pattern = r'{"name": "([^"]+)"[^}]+}'
    
    def add_sfx_to_skill(match):
        skill_def = match.group(0)
        skill_name = match.group(1)
        
        # 이미 sfx가 있으면 건드리지 않음
        if '"sfx"' in skill_def:
            return skill_def
        
        # 스킬 타입과 속성 추출
        type_match = re.search(r'"type": SkillType\.([^,]+)', skill_def)
        element_match = re.search(r'"element": ElementType\.([^,]+)', skill_def)
        
        skill_type = type_match.group(1) if type_match else None
        element = element_match.group(1) if element_match else None
        
        # 적절한 SFX 결정
        sfx = get_sfx_for_skill(skill_name, skill_type, element)
        
        # SFX 추가 (description 뒤에 삽입)
        if '"description"' in skill_def:
            new_skill_def = re.sub(
                r'("description": "[^"]+"),',
                r'\1, "sfx": "' + sfx + '",',
                skill_def
            )
            return new_skill_def
        else:
            # description이 없으면 mp_cost 뒤에 추가
            new_skill_def = re.sub(
                r'("mp_cost": \d+),',
                r'\1, "sfx": "' + sfx + '",',
                skill_def
            )
            return new_skill_def
    
    # 모든 스킬에 SFX 추가
    updated_content = re.sub(skill_pattern, add_sfx_to_skill, content, flags=re.DOTALL)
    
    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("모든 스킬에 SFX가 추가되었습니다!")

if __name__ == "__main__":
    add_sfx_to_file()
