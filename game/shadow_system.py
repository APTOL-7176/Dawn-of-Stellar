"""
🌑 그림자 시스템 - 암살자 전용 특수 메커니즘
그림자를 생성, 소모, 활용하는 전투 시스템
"""

from typing import List, Dict, Optional, Tuple
from .character import Character
from .new_skill_system import StatusType

class ShadowSystem:
    """그림자 시스템 관리자"""
    
    def __init__(self):
        self.max_shadows = 5  # 최대 그림자 개수
        self.shadow_echo_damage = 0.1  # 그림자 메아리 추가 피해 (10%)
        self.shadow_empowerment = 1.5  # 그림자 강화 배율 (1.5배)
        self.ultimate_shadow_multiplier = 0.3  # 궁극기 그림자당 피해 증가 (30%)
    
    def get_shadow_count(self, character: Character) -> int:
        """캐릭터의 현재 그림자 개수 조회"""
        if not hasattr(character, 'status_effects'):
            return 0
        
        for effect in character.status_effects:
            if hasattr(effect, 'status_type') and effect.status_type == StatusType.SHADOW_STACK:
                return int(getattr(effect, 'intensity', 0))
        
        return 0
    
    def add_shadows(self, character: Character, count: int) -> int:
        """그림자 추가 (최대 개수 제한)"""
        current_shadows = self.get_shadow_count(character)
        new_count = min(current_shadows + count, self.max_shadows)
        
        self._set_shadow_count(character, new_count)
        
        added = new_count - current_shadows
        if added > 0:
            print(f"🌑 {character.name}의 그림자 +{added}개 생성! (현재: {new_count}/{self.max_shadows})")
        
        return added
    
    def consume_shadows(self, character: Character, count: int) -> int:
        """그림자 소모 (실제로 소모된 개수 반환)"""
        current_shadows = self.get_shadow_count(character)
        consumed = min(current_shadows, count)
        new_count = current_shadows - consumed
        
        self._set_shadow_count(character, new_count)
        
        if consumed > 0:
            print(f"🌑 {character.name}의 그림자 -{consumed}개 소모! (현재: {new_count}/{self.max_shadows})")
        
        return consumed
    
    def consume_all_shadows(self, character: Character) -> int:
        """모든 그림자 소모 (소모된 개수 반환)"""
        current_shadows = self.get_shadow_count(character)
        if current_shadows > 0:
            self._set_shadow_count(character, 0)
            print(f"🌑 {character.name}의 모든 그림자 소모! ({current_shadows}개)")
        
        return current_shadows
    
    def _set_shadow_count(self, character: Character, count: int):
        """그림자 개수 설정 (내부 메서드)"""
        if not hasattr(character, 'status_effects'):
            character.status_effects = []
        
        # 기존 그림자 상태 제거
        character.status_effects = [
            effect for effect in character.status_effects 
            if not (hasattr(effect, 'status_type') and effect.status_type == StatusType.SHADOW_STACK)
        ]
        
        # 새 그림자 상태 추가 (0개가 아닐 때만)
        if count > 0:
            from .new_skill_system import StatusEffect
            shadow_effect = StatusEffect(
                name=f"shadow_stack_{count}",
                status_type=StatusType.SHADOW_STACK,
                duration=999,
                effect_value=count
            )
            character.status_effects.append(shadow_effect)
    
    def apply_shadow_echo(self, character: Character, base_damage: int) -> List[int]:
        """그림자 메아리 개별 타격 피해 계산 (각 그림자마다 별도 타격)"""
        shadow_count = self.get_shadow_count(character)
        if shadow_count <= 0:
            return []
        
        echo_damages = []
        single_echo_damage = int(base_damage * self.shadow_echo_damage)
        
        for i in range(shadow_count):
            if single_echo_damage > 0:
                echo_damages.append(single_echo_damage)
                print(f"🌑 그림자 메아리 #{i+1}: +{single_echo_damage} 추가 피해!")
        
        if echo_damages:
            total_echo = sum(echo_damages)
            print(f"🌑 총 그림자 메아리: {len(echo_damages)}회 타격으로 +{total_echo} 추가 피해!")
        
        return echo_damages
    
    def calculate_shadow_empowerment(self, character: Character, base_damage: int, can_consume: bool = True) -> Tuple[int, bool]:
        """그림자 강화 피해 계산 (그림자 소모 여부와 함께 반환)"""
        if not can_consume:
            return base_damage, False
        
        shadow_count = self.get_shadow_count(character)
        if shadow_count <= 0:
            return base_damage, False
        
        # 그림자 1개 소모하여 1.5배 피해
        consumed = self.consume_shadows(character, 1)
        if consumed > 0:
            empowered_damage = int(base_damage * self.shadow_empowerment)
            print(f"🌑 그림자 강화! 피해량 {base_damage} → {empowered_damage} (1.5배)")
            return empowered_damage, True
        
        return base_damage, False
    
    def calculate_ultimate_damage(self, character: Character, base_damage: int) -> int:
        """궁극기 그림자 소모 피해 계산"""
        shadow_count = self.get_shadow_count(character)
        if shadow_count <= 0:
            return base_damage
        
        # 모든 그림자 소모
        consumed_shadows = self.consume_all_shadows(character)
        
        # 그림자 1개당 30% 피해 증가
        multiplier = 1.0 + (consumed_shadows * self.ultimate_shadow_multiplier)
        ultimate_damage = int(base_damage * multiplier)
        
        print(f"🌑 그림자 처형! {consumed_shadows}개 그림자로 피해량 {base_damage} → {ultimate_damage} ({multiplier:.1f}배)")
        
        return ultimate_damage
    
    def can_use_skill_with_shadows(self, character: Character, skill: Dict) -> bool:
        """스킬을 그림자로 강화할 수 있는지 확인"""
        if not skill.get('can_consume_shadow', False):
            return False
        
        return self.get_shadow_count(character) > 0
    
    def get_shadow_status_display(self, character: Character) -> str:
        """그림자 상태 표시용 문자열"""
        shadow_count = self.get_shadow_count(character)
        if shadow_count <= 0:
            return ""
        
        # 그림자 아이콘으로 표시
        shadow_icons = "🌑" * min(shadow_count, 5)  # 최대 5개까지 아이콘으로 표시
        return f"{shadow_icons} {shadow_count}"
    
    def process_skill_shadow_effects(self, character: Character, skill: Dict, damage: int) -> Tuple[int, Dict]:
        """스킬 사용 시 그림자 효과 처리"""
        results = {
            'shadows_generated': 0,
            'shadows_consumed': 0,
            'echo_damages': [],
            'empowered': False,
            'final_damage': damage
        }
        
        # 1. 그림자 생성 (기본공격, BRV공격, 특수 스킬)
        if 'generate_shadow' in skill.get('special_effects', []):
            shadow_count = skill.get('shadow_count', 1)
            results['shadows_generated'] = self.add_shadows(character, shadow_count)
        
        # 2. 그림자 메아리 (기본공격, BRV공격 시 개별 추가 타격)
        if skill.get('type') in ['BRV_ATTACK', 'ATTACK'] and 'shadow_echo' in skill.get('special_effects', []):
            results['echo_damages'] = self.apply_shadow_echo(character, damage)
            results['final_damage'] += sum(results['echo_damages'])
        
        # 3. 그림자 강화 (소모 가능한 스킬)
        if skill.get('can_consume_shadow', False):
            empowered_damage, was_empowered = self.calculate_shadow_empowerment(
                character, damage, can_consume=True
            )
            if was_empowered:
                results['empowered'] = True
                results['shadows_consumed'] = 1
                results['final_damage'] = empowered_damage
        
        # 4. 궁극기 그림자 소모
        if 'consume_all_shadows' in skill.get('special_effects', []):
            ultimate_damage = self.calculate_ultimate_damage(character, damage)
            results['final_damage'] = ultimate_damage
            results['shadows_consumed'] = self.get_shadow_count(character)  # 소모 전 개수 기록
        
        return results['final_damage'], results


# 전역 그림자 시스템 인스턴스
_shadow_system = None

def get_shadow_system() -> ShadowSystem:
    """그림자 시스템 인스턴스 반환 (싱글톤)"""
    global _shadow_system
    if _shadow_system is None:
        _shadow_system = ShadowSystem()
    return _shadow_system
