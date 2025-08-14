#!/usr/bin/env python3
"""
레벨업 전용 스킬 시스템
캐릭터가 레벨업할 때만 배울 수 있는 독특하고 강력한 스킬들
"""

from typing import Dict, List, Any
try:
    from game.status_effects import ElementType, StatusEffectType
except ImportError:
    # 직접 실행할 때의 fallback
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from game.status_effects import ElementType, StatusEffectType

class LevelUpSkillSystem:
    """레벨업 전용 스킬 시스템"""
    
    def __init__(self):
        pass
    
    def get_learnable_skills(self, character, new_level: int) -> List[Dict[str, Any]]:
        """해당 레벨에서 배울 수 있는 스킬들 반환"""
        skills = []
        
        # 클래스별 스킬 트리
        if character.character_class == "전사":
            skills.extend(self._get_warrior_levelup_skills(new_level))
        elif character.character_class == "마법사":
            skills.extend(self._get_mage_levelup_skills(new_level))
        elif character.character_class == "궁수":
            skills.extend(self._get_archer_levelup_skills(new_level))
        elif character.character_class == "성직자":
            skills.extend(self._get_priest_levelup_skills(new_level))
        
        return skills
    
    def _get_warrior_levelup_skills(self, level: int) -> List[Dict[str, Any]]:
        """전사 레벨업 스킬"""
        skills = []
        
        if level == 3:
            skills.append({
                'name': '🔥⚔️ 검기 폭발',
                'type': 'special_attack',
                'modifier': 2.2,
                'mp_cost': 25,
                'element': ElementType.FIRE,
                'target_type': 'line_attack',
                'description': '일직선상의 모든 적에게 화염 검기 발사',
                'special_effects': ['armor_penetration', 'knockback'],
                'sfx': 'sword_beam',
                'unlock_level': 3
            })
            
        if level == 5:
            skills.append({
                'name': '⚡🛡️ 번개 반격',
                'type': 'counter_skill',
                'modifier': 1.8,
                'mp_cost': 20,
                'element': ElementType.LIGHTNING,
                'target_type': 'counter',
                'description': '공격받을 때 자동으로 번개로 반격 (패시브)',
                'special_effects': ['auto_counter', 'stun_chance'],
                'sfx': 'thunder_strike',
                'unlock_level': 5
            })
            
        if level == 7:
            skills.append({
                'name': '🌪️⚔️ 검무 토네이도',
                'type': 'area_attack',
                'modifier': 1.5,
                'mp_cost': 35,
                'element': ElementType.WIND,
                'target_type': 'surrounding',
                'description': '주변 모든 적을 휘감는 검의 토네이도',
                'special_effects': ['multi_hit', 'wind_prison'],
                'sfx': 'blade_tornado',
                'unlock_level': 7
            })
            
        if level == 10:
            skills.append({
                'name': '💀⚔️ 처형자의 일격',
                'type': 'execution',
                'modifier': 3.0,
                'mp_cost': 50,
                'target_type': 'single_enemy',
                'description': 'HP가 30% 이하인 적을 즉사시킬 확률 50%',
                'special_effects': ['execution_chance', 'fear_aura'],
                'sfx': 'death_strike',
                'unlock_level': 10
            })
            
        return skills
    
    def _get_mage_levelup_skills(self, level: int) -> List[Dict[str, Any]]:
        """마법사 레벨업 스킬"""
        skills = []
        
        if level == 3:
            skills.append({
                'name': '🔮✨ 마법 연쇄',
                'type': 'spell_combo',
                'modifier': 1.3,
                'mp_cost': 30,
                'target_type': 'smart_target',
                'description': '3개의 다른 원소 마법을 연속으로 시전',
                'special_effects': ['element_combo', 'magic_amplify'],
                'sfx': 'spell_chain',
                'unlock_level': 3
            })
            
        if level == 5:
            skills.append({
                'name': '🌀🔮 원소 융합',
                'type': 'fusion_magic',
                'modifier': 2.5,
                'mp_cost': 40,
                'element': None,  # 랜덤 조합
                'target_type': 'area_blast',
                'description': '두 원소를 융합하여 새로운 효과 창조',
                'special_effects': ['element_fusion', 'chaos_effect'],
                'sfx': 'elemental_fusion',
                'unlock_level': 5
            })
            
        if level == 7:
            skills.append({
                'name': '🕳️🌌 차원 균열',
                'type': 'dimension_magic',
                'modifier': 2.0,
                'mp_cost': 45,
                'element': ElementType.ARCANE,
                'target_type': 'random_teleport',
                'description': '차원의 균열을 열어 적들을 다른 차원으로 추방',
                'special_effects': ['banishment', 'reality_tear'],
                'sfx': 'dimension_rip',
                'unlock_level': 7
            })
            
        if level == 10:
            skills.append({
                'name': '🌟💥 메테오 스웜',
                'type': 'ultimate_magic',
                'modifier': 1.8,
                'mp_cost': 60,
                'element': ElementType.FIRE,
                'target_type': 'battlefield',
                'description': '전체 전장에 운석우를 내려 모든 적 공격',
                'special_effects': ['meteor_rain', 'terrain_change'],
                'sfx': 'meteor_storm',
                'unlock_level': 10
            })
            
        return skills
    
    def _get_archer_levelup_skills(self, level: int) -> List[Dict[str, Any]]:
        """궁수 레벨업 스킬"""
        skills = []
        
        if level == 3:
            skills.append({
                'name': '🏹💎 크리스탈 화살',
                'type': 'special_shot',
                'modifier': 2.0,
                'mp_cost': 20,
                'target_type': 'piercing_shot',
                'description': '모든 적을 관통하며 각 적마다 위력 증가',
                'special_effects': ['armor_pierce', 'damage_stack'],
                'sfx': 'crystal_shot',
                'unlock_level': 3
            })
            
        if level == 5:
            skills.append({
                'name': '🌙🏹 달빛 추적',
                'type': 'tracking_shot',
                'modifier': 2.5,
                'mp_cost': 25,
                'element': ElementType.LIGHT,
                'target_type': 'guided_missile',
                'description': '절대 빗나가지 않는 추적 화살, 은신한 적도 타격',
                'special_effects': ['never_miss', 'stealth_detect'],
                'sfx': 'moonbeam_arrow',
                'unlock_level': 5
            })
            
        if level == 7:
            skills.append({
                'name': '🏹⏰ 시간 화살',
                'type': 'temporal_shot',
                'modifier': 1.5,
                'mp_cost': 35,
                'target_type': 'time_manipulation',
                'description': '시간을 역행하여 과거의 자신도 함께 공격',
                'special_effects': ['time_echo', 'multi_timeline'],
                'sfx': 'time_arrow',
                'unlock_level': 7
            })
            
        if level == 10:
            skills.append({
                'name': '🌟🏹 별자리 사격',
                'type': 'constellation_shot',
                'modifier': 3.5,
                'mp_cost': 50,
                'target_type': 'constellation_pattern',
                'description': '별자리 모양으로 화살을 쏘아 강력한 마법진 생성',
                'special_effects': ['magic_circle', 'star_power'],
                'sfx': 'constellation_rain',
                'unlock_level': 10
            })
            
        return skills
    
    def _get_priest_levelup_skills(self, level: int) -> List[Dict[str, Any]]:
        """성직자 레벨업 스킬"""
        skills = []
        
        if level == 3:
            skills.append({
                'name': '👼✨ 수호천사 소환',
                'type': 'summon_ally',
                'modifier': 0.0,
                'mp_cost': 40,
                'target_type': 'summon',
                'description': '강력한 수호천사를 소환하여 3턴간 아군 지원',
                'special_effects': ['summon_guardian', 'divine_protection'],
                'sfx': 'angel_descend',
                'unlock_level': 3
            })
            
        if level == 5:
            skills.append({
                'name': '💫🔄 시간 역행',
                'type': 'time_magic',
                'modifier': 0.0,
                'mp_cost': 50,
                'target_type': 'party_wide',
                'description': '파티 전체를 3턴 전 상태로 되돌림',
                'special_effects': ['time_rewind', 'hp_mp_restore'],
                'sfx': 'time_reverse',
                'unlock_level': 5
            })
            
        if level == 7:
            skills.append({
                'name': '⚖️✨ 심판의 저울',
                'type': 'justice_magic',
                'modifier': 0.0,
                'mp_cost': 35,
                'target_type': 'moral_judgment',
                'description': '악한 적일수록 더 큰 피해, 선한 존재는 치유',
                'special_effects': ['karma_damage', 'alignment_detect'],
                'sfx': 'divine_judgment',
                'unlock_level': 7
            })
            
        if level == 10:
            skills.append({
                'name': '🌅💫 새벽의 기적',
                'type': 'miracle',
                'modifier': 0.0,
                'mp_cost': 80,
                'target_type': 'battlefield_change',
                'description': '전투를 완전히 리셋하고 모든 아군 완전 회복',
                'special_effects': ['battle_reset', 'full_recovery', 'status_cleanse'],
                'sfx': 'dawn_miracle',
                'unlock_level': 10
            })
            
        return skills
    
    def learn_skill(self, character, skill: Dict[str, Any]) -> bool:
        """스킬 습득"""
        if not hasattr(character, 'learned_skills'):
            character.learned_skills = []
        
        # 이미 배운 스킬인지 확인
        for learned in character.learned_skills:
            if learned['name'] == skill['name']:
                return False
        
        # 레벨 조건 확인
        if character.level >= skill.get('unlock_level', 1):
            character.learned_skills.append(skill)
            return True
        
        return False
    
    def get_learned_skills(self, character) -> List[Dict[str, Any]]:
        """배운 스킬 목록 반환"""
        if not hasattr(character, 'learned_skills'):
            character.learned_skills = []
        return character.learned_skills
    
    def can_use_learned_skill(self, character, skill: Dict[str, Any]) -> bool:
        """배운 스킬 사용 가능 여부"""
        # MP 확인
        mp_cost = skill.get('mp_cost', 0)
        if character.current_mp < mp_cost:
            return False
        
        return True

# 테스트 코드
if __name__ == "__main__":
    from game.character import Character
    
    print("=== 레벨업 전용 스킬 시스템 테스트 ===")
    
    skill_system = LevelUpSkillSystem()
    
    # 테스트 캐릭터 생성
    warrior = Character("테스트 전사", "전사", 100, 20, 5, 15, 10, 12)
    warrior.level = 5
    
    # 레벨 5에서 배울 수 있는 스킬들
    learnable = skill_system.get_learnable_skills(warrior, 5)
    
    print(f"\n⚔️ 전사 레벨 5 스킬:")
    for skill in learnable:
        print(f"  🎯 {skill['name']}: {skill['description']}")
        print(f"     MP: {skill['mp_cost']}, 효과: {', '.join(skill.get('special_effects', []))}")
    
    # 모든 레벨의 스킬 표시
    print(f"\n📚 전체 레벨업 스킬 미리보기:")
    for level in [3, 5, 7, 10]:
        for class_name in ["전사", "마법사", "궁수", "성직자"]:
            test_char = Character(f"테스트 {class_name}", class_name, 100, 20, 20, 15, 15, 15)
            skills = skill_system.get_learnable_skills(test_char, level)
            
            if skills:
                print(f"\n  🏆 {class_name} 레벨 {level}:")
                for skill in skills:
                    print(f"    ✨ {skill['name']}: {skill['description']}")
                    
    print(f"\n🎮 총 구현된 레벨업 스킬: {sum(len(skill_system.get_learnable_skills(Character('test', cls, 100, 20, 20, 15, 15, 15), 10)) for cls in ['전사', '마법사', '궁수', '성직자'])}개")
