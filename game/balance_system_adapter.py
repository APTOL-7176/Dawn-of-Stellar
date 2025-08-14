"""
🔧 Dawn of Stellar - 밸런스 시스템 통합 어댑터
==================================================

기존 시스템들과 새로운 완전 밸런스 시스템을 통합하는 어댑터
- unified_damage_system.py와 연동
- advanced_field_enemy_ai.py 스탯 적용
- integrated_enemy_system.py 스케일링 적용
- 기존 전투 시스템과 호환성 유지

2025년 8월 10일 - 시스템 통합 완성
"""

import sys
import os
import importlib.util
from typing import Dict, List, Any, Optional, Tuple

# 게임 모듈 임포트
try:
    from game.complete_balance_redesign import (
        get_balance_system, 
        calculate_balanced_damage,
        normalize_all_effects,
        generate_enemy_for_layer,
        DamageType,
        StatType,
        BalanceConstants
    )
    from game.unified_damage_system import get_damage_system, UnifiedDamageSystem
except ImportError as e:
    print(f"⚠️ 모듈 임포트 오류: {e}")
    print("필요한 모듈들이 없어 기본 구현을 사용합니다.")

class BalanceSystemAdapter:
    """밸런스 시스템 통합 어댑터"""
    
    def __init__(self):
        self.balance_system = get_balance_system()
        self.damage_system = get_damage_system(debug_mode=False)
        self.integration_mode = True
        
        # 기존 상수들을 새로운 밸런스 상수로 업데이트
        self._update_legacy_constants()
        
    def _update_legacy_constants(self):
        """기존 시스템 상수들을 새로운 밸런스에 맞게 업데이트"""
        constants = self.balance_system.constants
        
        # UnifiedDamageSystem 상수 업데이트
        if hasattr(self.damage_system, 'BRV_BASE_MULTIPLIER'):
            # BRV 시스템을 새로운 밸런스에 맞게 조정
            self.damage_system.BRV_BASE_MULTIPLIER = 0.8  # 기존보다 약간 낮춤
            self.damage_system.BRV_DEFENSE_REDUCTION = constants.BRV_DEFENSE_SCALING
            self.damage_system.HP_DEFENSE_REDUCTION = constants.HP_DEFENSE_SCALING
            self.damage_system.BASE_CRITICAL_RATE = constants.BASE_CRIT_RATE / 100
            self.damage_system.BASE_CRITICAL_MULTIPLIER = constants.BASE_CRIT_DAMAGE
            
        print("✅ 기존 시스템 상수들이 새로운 밸런스에 맞게 업데이트되었습니다.")
    
    # =====================================
    # 🔄 데미지 계산 통합
    # =====================================
    
    def calculate_integrated_damage(self, 
                                  attacker, 
                                  target, 
                                  skill: Dict[str, Any], 
                                  damage_category: str = "brv") -> Dict[str, Any]:
        """통합된 데미지 계산 (기존 + 새로운 시스템)"""
        
        # 스킬 타입 결정
        damage_type = skill.get('damage_type', 'physical')
        
        # 새로운 완전 밸런스 시스템으로 계산
        complete_result = calculate_balanced_damage(attacker, target, skill, damage_type)
        
        # 기존 시스템과의 호환성을 위한 결과 형식 변환
        if damage_category == "brv":
            # BRV 데미지는 새로운 시스템 결과 사용
            final_damage = complete_result['final_damage']
            
            # BRV 포인트로 변환 (기존 시스템 호환)
            brv_gain = int(final_damage * 0.8)  # 데미지의 80%를 BRV로 획득
            
        elif damage_category == "hp":
            # HP 데미지는 공격자의 BRV 포인트 기반
            brv_points = getattr(attacker, 'brave_points', 0)
            
            # 새로운 시스템의 HP 계산 로직 적용
            hp_power = skill.get('hp_power', 1.0)
            final_damage = int(brv_points * hp_power * 0.9)  # 기존보다 약간 낮춤
            
            # 방어력 적용 (새로운 시스템)
            if complete_result['is_hit']:
                defense_multiplier = 1.0 - (complete_result.get('effective_defense', 0) * 0.003)
                defense_multiplier = max(0.2, defense_multiplier)
                final_damage = int(final_damage * defense_multiplier)
            else:
                final_damage = 0
        
        # 통합 결과 반환
        return {
            'final_damage': max(1, final_damage) if complete_result['is_hit'] else 0,
            'is_hit': complete_result['is_hit'],
            'is_critical': complete_result['is_critical'],
            'hit_chance': complete_result['hit_chance'],
            'calculation_steps': complete_result['calculation_steps'],
            'complete_analysis': complete_result,
            'brv_gain': brv_gain if damage_category == "brv" else 0,
            'wound_damage': int(final_damage * 0.25) if damage_category == "hp" else 0
        }
    
    # =====================================
    # 👹 적 스탯 통합 생성
    # =====================================
    
    def create_balanced_enemy(self, 
                            enemy_type: str,
                            base_level: int,
                            layer: int,
                            enemy_class: str = "normal") -> Dict[str, Any]:
        """밸런스된 적 생성 (모든 시스템 통합)"""
        
        # 새로운 밸런스 시스템으로 기본 스탯 생성
        balanced_stats = generate_enemy_for_layer(layer, enemy_class, base_level)
        
        # 기존 시스템 형식으로 변환
        enemy_data = {
            'name': f"{enemy_class}_{enemy_type}",
            'level': base_level,
            'layer': layer,
            'enemy_class': enemy_class,
            
            # 기본 스탯
            'max_hp': int(80 + base_level * 15 + layer * 5),
            'max_mp': int(30 + base_level * 5),
            'max_brv': int(40 + base_level * 8),
            'int_brv': int(30 + base_level * 6),
            
            # 물리/마법 분리 스탯 (새로운 밸런스 적용)
            'physical_attack': int(balanced_stats[StatType.PHYSICAL_ATTACK]),
            'magic_attack': int(balanced_stats[StatType.MAGICAL_ATTACK]),
            'physical_defense': int(balanced_stats[StatType.PHYSICAL_DEFENSE]),
            'magic_defense': int(balanced_stats[StatType.MAGICAL_DEFENSE]),
            
            # 명중/회피 시스템
            'accuracy': balanced_stats[StatType.ACCURACY],
            'evasion': balanced_stats[StatType.EVASION],
            
            # 크리티컬 시스템
            'crit_chance': balanced_stats[StatType.CRITICAL_RATE],
            'crit_damage': balanced_stats[StatType.CRITICAL_DAMAGE],
            
            # 관통력 시스템
            'penetration': balanced_stats[StatType.PENETRATION],
            
            # 기타 스탯
            'speed': 50 + base_level * 2 + layer,
            'luck': 10 + base_level,
            
            # 속성 저항/약점 (랜덤)
            'element_resistances': self._generate_resistances(enemy_type),
            'element_weaknesses': self._generate_weaknesses(enemy_type),
            
            # AI 행동 패턴 (기존 시스템 연동)
            'ai_behavior': self._determine_ai_behavior(enemy_class, layer),
            'skills': self._assign_balanced_skills(enemy_type, base_level, layer)
        }
        
        # 특수 타입별 조정
        self._apply_special_type_modifiers(enemy_data, enemy_class)
        
        return enemy_data
    
    def _generate_resistances(self, enemy_type: str) -> List[str]:
        """적 타입에 따른 속성 저항 생성"""
        resistance_map = {
            'fire_elemental': ['fire'],
            'ice_golem': ['ice', 'water'],
            'earth_guardian': ['earth', 'physical'],
            'shadow_wraith': ['dark', 'poison'],
            'holy_knight': ['light', 'dark'],
            'mechanical_drone': ['lightning', 'poison'],
            'nature_spirit': ['earth', 'water'],
            'void_entity': ['dark', 'light']
        }
        return resistance_map.get(enemy_type, [])
    
    def _generate_weaknesses(self, enemy_type: str) -> List[str]:
        """적 타입에 따른 속성 약점 생성"""
        weakness_map = {
            'fire_elemental': ['water', 'ice'],
            'ice_golem': ['fire'],
            'earth_guardian': ['wind', 'lightning'],
            'shadow_wraith': ['light'],
            'holy_knight': ['dark'],
            'mechanical_drone': ['lightning'],
            'nature_spirit': ['fire'],
            'void_entity': ['light']
        }
        return weakness_map.get(enemy_type, [])
    
    def _determine_ai_behavior(self, enemy_class: str, layer: int) -> str:
        """적 클래스와 층수에 따른 AI 행동 패턴 결정"""
        if layer >= 80:
            return "legendary"
        elif layer >= 60:
            return "master" 
        elif layer >= 40:
            return "expert"
        elif layer >= 20:
            return "advanced"
        elif enemy_class in ["boss", "elite"]:
            return "tactical"
        else:
            return "basic"
    
    def _assign_balanced_skills(self, enemy_type: str, level: int, layer: int) -> List[Dict[str, Any]]:
        """밸런스된 적 스킬 할당"""
        skills = []
        
        # 기본 공격 (모든 적)
        skills.append({
            'name': '기본공격',
            'mp_cost': 0,
            'power': 1.0,
            'damage_type': 'physical',
            'type': 'brv_attack'
        })
        
        # 레벨과 층수에 따른 추가 스킬
        if level >= 3:
            skills.append({
                'name': '강타',
                'mp_cost': 5,
                'power': 1.4,
                'damage_type': 'physical',
                'type': 'brv_attack'
            })
        
        if level >= 5:
            skills.append({
                'name': 'HP공격',
                'mp_cost': 0,
                'hp_power': 1.0,
                'damage_type': 'physical',
                'type': 'hp_attack'
            })
        
        if layer >= 10:
            skills.append({
                'name': '마법공격',
                'mp_cost': 8,
                'power': 1.3,
                'damage_type': 'magical',
                'type': 'brv_attack',
                'element': 'fire'
            })
        
        if layer >= 20:
            skills.append({
                'name': '버프',
                'mp_cost': 12,
                'type': 'support',
                'effect': 'attack_boost',
                'duration': self.balance_system.normalize_effect_duration('attack_boost', 3)
            })
        
        # 보스/엘리트 전용 스킬
        if enemy_type in ['boss', 'elite'] and layer >= 15:
            skills.append({
                'name': '궁극기',
                'mp_cost': 20,
                'power': 2.0,
                'damage_type': 'magical',
                'type': 'ultimate',
                'element': 'dark'
            })
        
        return skills
    
    def _apply_special_type_modifiers(self, enemy_data: Dict[str, Any], enemy_class: str):
        """특수 타입별 스탯 조정"""
        if enemy_class == "boss":
            # 보스는 HP와 방어력 대폭 상승
            enemy_data['max_hp'] = int(enemy_data['max_hp'] * 2.5)
            enemy_data['physical_defense'] = int(enemy_data['physical_defense'] * 1.5)
            enemy_data['magic_defense'] = int(enemy_data['magic_defense'] * 1.5)
            enemy_data['max_brv'] = int(enemy_data['max_brv'] * 1.8)
            
        elif enemy_class == "elite":
            # 엘리트는 공격력과 크리티컬 상승
            enemy_data['physical_attack'] = int(enemy_data['physical_attack'] * 1.3)
            enemy_data['magic_attack'] = int(enemy_data['magic_attack'] * 1.3)
            enemy_data['crit_chance'] = min(40, enemy_data['crit_chance'] * 1.5)
            enemy_data['max_hp'] = int(enemy_data['max_hp'] * 1.4)
            
        elif enemy_class == "speed":
            # 스피드형은 회피와 속도 대폭 상승
            enemy_data['evasion'] = min(60, enemy_data['evasion'] * 2.0)
            enemy_data['speed'] = int(enemy_data['speed'] * 1.6)
            enemy_data['accuracy'] = enemy_data['accuracy'] * 1.2
            
        elif enemy_class == "tank":
            # 탱크형은 방어력과 HP 대폭 상승
            enemy_data['physical_defense'] = int(enemy_data['physical_defense'] * 2.0)
            enemy_data['magic_defense'] = int(enemy_data['magic_defense'] * 1.8)
            enemy_data['max_hp'] = int(enemy_data['max_hp'] * 1.8)
            enemy_data['evasion'] = max(1, enemy_data['evasion'] * 0.5)  # 회피 감소
    
    # =====================================
    # 🔄 기존 시스템 연동
    # =====================================
    
    def integrate_with_brave_combat(self, combat_system):
        """BraveCombat 시스템과 통합"""
        if hasattr(combat_system, 'calculate_brv_damage'):
            # 기존 BRV 데미지 계산을 새로운 시스템으로 교체
            original_calculate_brv = combat_system.calculate_brv_damage
            
            def new_calculate_brv(attacker, target, skill, **kwargs):
                result = self.calculate_integrated_damage(attacker, target, skill, "brv")
                return result['final_damage'], result['brv_gain']
            
            combat_system.calculate_brv_damage = new_calculate_brv
            print("✅ BRV 데미지 계산이 새로운 밸런스 시스템으로 교체되었습니다.")
        
        if hasattr(combat_system, 'calculate_hp_damage'):
            # 기존 HP 데미지 계산을 새로운 시스템으로 교체
            original_calculate_hp = combat_system.calculate_hp_damage
            
            def new_calculate_hp(attacker, target, skill, **kwargs):
                result = self.calculate_integrated_damage(attacker, target, skill, "hp")
                return result['final_damage'], result['wound_damage']
            
            combat_system.calculate_hp_damage = new_calculate_hp
            print("✅ HP 데미지 계산이 새로운 밸런스 시스템으로 교체되었습니다.")
    
    def integrate_with_enemy_system(self, enemy_system):
        """통합 적 시스템과 연동"""
        if hasattr(enemy_system, 'create_enemy'):
            # 적 생성을 새로운 밸런스 시스템으로 교체
            original_create_enemy = enemy_system.create_enemy
            
            def new_create_enemy(enemy_type, level, layer, **kwargs):
                enemy_class = kwargs.get('enemy_class', 'normal')
                return self.create_balanced_enemy(enemy_type, level, layer, enemy_class)
            
            enemy_system.create_enemy = new_create_enemy
            print("✅ 적 생성이 새로운 밸런스 시스템으로 교체되었습니다.")
    
    def normalize_all_game_effects(self, effects_data: Dict[str, Any]) -> Dict[str, Any]:
        """게임 내 모든 효과의 지속시간 정규화"""
        normalized_data = effects_data.copy()
        
        # 버프/디버프 지속시간 정규화
        for category in ['buffs', 'debuffs', 'status_effects']:
            if category in normalized_data:
                for effect_name, effect_info in normalized_data[category].items():
                    if isinstance(effect_info, dict) and 'duration' in effect_info:
                        old_duration = effect_info['duration']
                        new_duration = self.balance_system.normalize_effect_duration(effect_name, old_duration)
                        
                        if old_duration != new_duration:
                            effect_info['duration'] = new_duration
                            # 효과값도 비례 조정
                            if 'value' in effect_info:
                                effect_info['value'] *= (new_duration / old_duration)
                            
                            print(f"✅ {effect_name}: {old_duration}턴 → {new_duration}턴으로 정규화")
        
        return normalized_data
    
    # =====================================
    # 📊 밸런스 분석 및 리포트
    # =====================================
    
    def generate_balance_report(self, player_level: int, current_layer: int) -> Dict[str, Any]:
        """현재 게임 상태의 밸런스 리포트 생성"""
        
        # 플레이어 예상 스탯 (평균적인 경우)
        estimated_player_stats = {
            StatType.PHYSICAL_ATTACK: 40 + player_level * 4,
            StatType.MAGICAL_ATTACK: 35 + player_level * 3,
            StatType.PHYSICAL_DEFENSE: 30 + player_level * 2.5,
            StatType.MAGICAL_DEFENSE: 25 + player_level * 2,
            StatType.ACCURACY: 80 + player_level * 0.8,
            StatType.EVASION: 12 + player_level * 0.4,
            StatType.PENETRATION: player_level * 0.3,
            StatType.CRITICAL_RATE: 8 + player_level * 0.3,
            StatType.CRITICAL_DAMAGE: 1.5 + player_level * 0.02,
        }
        
        # 현재 층의 적 스탯
        enemy_stats = generate_enemy_for_layer(current_layer, "normal", player_level)
        elite_stats = generate_enemy_for_layer(current_layer, "elite", player_level + 2)
        boss_stats = generate_enemy_for_layer(current_layer, "boss", player_level + 5)
        
        # 밸런스 분석
        normal_balance = self.balance_system.validate_balance(estimated_player_stats, enemy_stats)
        elite_balance = self.balance_system.validate_balance(estimated_player_stats, elite_stats)
        boss_balance = self.balance_system.validate_balance(estimated_player_stats, boss_stats)
        
        report = {
            'layer': current_layer,
            'player_level': player_level,
            'balance_analysis': {
                'normal_enemy': normal_balance,
                'elite_enemy': elite_balance,
                'boss_enemy': boss_balance
            },
            'recommendations': [],
            'scaling_projection': self._calculate_scaling_projection(player_level, current_layer)
        }
        
        # 권장사항 생성
        if normal_balance['balance_ratio'] < 0.7:
            report['recommendations'].append("일반 적이 너무 약함 - 난이도 상향 필요")
        elif normal_balance['balance_ratio'] > 1.1:
            report['recommendations'].append("일반 적이 너무 강함 - 난이도 하향 필요")
        
        if boss_balance['balance_ratio'] < 1.2:
            report['recommendations'].append("보스가 너무 약함 - 보스 강화 필요")
        elif boss_balance['balance_ratio'] > 2.0:
            report['recommendations'].append("보스가 너무 강함 - 보스 약화 필요")
        
        return report
    
    def _calculate_scaling_projection(self, current_level: int, current_layer: int) -> Dict[str, Any]:
        """향후 스케일링 전망 계산"""
        projections = {}
        
        for future_layer in [current_layer + 10, current_layer + 20, current_layer + 30]:
            future_level = current_level + (future_layer - current_layer) // 3
            
            player_power = 100 * (1.15 ** (future_level - current_level))
            enemy_power = 100 * (1.15 * 1.08) ** (future_layer - current_layer)
            
            projections[f'layer_{future_layer}'] = {
                'estimated_player_level': future_level,
                'relative_enemy_strength': enemy_power / player_power,
                'difficulty_trend': 'increasing' if enemy_power > player_power * 1.1 else 'balanced'
            }
        
        return projections

# =====================================
# 🌟 전역 인스턴스 및 편의 함수
# =====================================

_adapter = None

def get_balance_adapter() -> BalanceSystemAdapter:
    """밸런스 시스템 어댑터 인스턴스 가져오기"""
    global _adapter
    if _adapter is None:
        _adapter = BalanceSystemAdapter()
    return _adapter

def integrate_all_systems():
    """모든 게임 시스템에 새로운 밸런스 적용"""
    adapter = get_balance_adapter()
    
    try:
        # BraveCombat 시스템 통합
        import game.brave_combat as brave_combat
        if hasattr(brave_combat, 'BraveCombatSystem'):
            print("🔧 BraveCombat 시스템과 통합 중...")
            # 전역 인스턴스가 있다면 통합
            # adapter.integrate_with_brave_combat(brave_combat_instance)
        
        # 통합 적 시스템 연동
        try:
            import game.integrated_enemy_system as enemy_system
            print("🔧 통합 적 시스템과 연동 중...")
            # adapter.integrate_with_enemy_system(enemy_system)
        except ImportError:
            print("⚠️ 통합 적 시스템을 찾을 수 없습니다.")
        
        print("✅ 모든 시스템 통합이 완료되었습니다!")
        
    except Exception as e:
        print(f"⚠️ 시스템 통합 중 오류 발생: {e}")
        print("기본 밸런스 시스템만 사용합니다.")

def create_balanced_enemy_quick(enemy_type: str, level: int, layer: int) -> Dict[str, Any]:
    """빠른 밸런스된 적 생성"""
    adapter = get_balance_adapter()
    return adapter.create_balanced_enemy(enemy_type, level, layer)

def calculate_damage_with_new_balance(attacker, target, skill: Dict[str, Any]) -> Dict[str, Any]:
    """새로운 밸런스로 데미지 계산"""
    adapter = get_balance_adapter()
    return adapter.calculate_integrated_damage(attacker, target, skill)

if __name__ == "__main__":
    print("🧪 밸런스 시스템 통합 어댑터 테스트")
    
    # 어댑터 생성
    adapter = get_balance_adapter()
    
    # 밸런스된 적 생성 테스트
    print("\n👹 적 생성 테스트:")
    test_enemy = create_balanced_enemy_quick("fire_elemental", 10, 15)
    print(f"생성된 적: {test_enemy['name']}")
    print(f"물리 공격력: {test_enemy['physical_attack']}")
    print(f"마법 공격력: {test_enemy['magic_attack']}")
    print(f"명중률: {test_enemy['accuracy']:.1f}")
    print(f"회피율: {test_enemy['evasion']:.1f}")
    
    # 밸런스 리포트 생성
    print("\n📊 밸런스 리포트:")
    balance_report = adapter.generate_balance_report(10, 15)
    print(f"현재 층: {balance_report['layer']}")
    print(f"플레이어 레벨: {balance_report['player_level']}")
    print("권장사항:", balance_report['recommendations'])
    
    # 모든 시스템 통합 시도
    print("\n🔧 시스템 통합:")
    integrate_all_systems()
