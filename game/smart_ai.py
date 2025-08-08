#!/usr/bin/env python3
"""
고급 AI 시스템
스마트 적 AI, 전술적 파티 AI, 적응형 행동 패턴
"""

import random
import math
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum, IntEnum
from dataclasses import dataclass


class AIPersonality(Enum):
    """AI 성격 유형"""
    AGGRESSIVE = "aggressive"      # 공격적
    DEFENSIVE = "defensive"        # 방어적
    TACTICAL = "tactical"          # 전술적
    BERSERKER = "berserker"       # 광전사
    SUPPORT = "support"           # 지원형
    ADAPTIVE = "adaptive"         # 적응형


class ThreatLevel(IntEnum):
    """위협 수준"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AIMemory:
    """AI 기억 시스템"""
    player_patterns: Dict[str, int] = None
    effective_strategies: List[str] = None
    failed_strategies: List[str] = None
    target_preferences: Dict[str, float] = None
    
    def __post_init__(self):
        if self.player_patterns is None:
            self.player_patterns = {}
        if self.effective_strategies is None:
            self.effective_strategies = []
        if self.failed_strategies is None:
            self.failed_strategies = []
        if self.target_preferences is None:
            self.target_preferences = {}


class AllyAI:
    """아군 AI - 플레이어를 도와주는 파티원 AI"""
    
    def __init__(self, character_class: str = "전사", personality: AIPersonality = AIPersonality.TACTICAL):
        self.character_class = character_class
        self.personality = personality
        self.cooperation_level = 0.8  # 협력도 (0.0~1.0)
        self.initiative = 0.6  # 주도성 (0.0~1.0)
        self.memory = AIMemory()
        
        # 직업별 특성 가중치
        self.role_weights = self._setup_role_weights()
        
        # 성격별 가중치
        self.personality_weights = self._setup_personality_weights()
    
    def _setup_role_weights(self) -> Dict[str, float]:
        """직업별 역할 가중치 설정"""
        role_configs = {
            "전사": {"tank": 0.8, "damage": 0.6, "support": 0.2, "heal": 0.1},
            "궁수": {"damage": 0.9, "tank": 0.2, "support": 0.4, "heal": 0.1},
            "마법사": {"damage": 0.8, "support": 0.7, "tank": 0.1, "heal": 0.3},
            "성직자": {"heal": 0.9, "support": 0.8, "damage": 0.3, "tank": 0.4},
            "암살자": {"damage": 0.9, "support": 0.3, "tank": 0.1, "heal": 0.1},
            "기계공학자": {"damage": 0.7, "support": 0.6, "tank": 0.3, "heal": 0.2},
            "바드": {"support": 0.9, "heal": 0.6, "damage": 0.4, "tank": 0.2},
            "성기사": {"tank": 0.8, "heal": 0.7, "damage": 0.5, "support": 0.6},
            
            # Phase 1 & 2 새로운 직업들
            "검성": {"damage": 0.9, "tank": 0.4, "support": 0.3, "heal": 0.1},      # 검기 스택 기반 딜러
            "검투사": {"damage": 0.8, "tank": 0.6, "support": 0.4, "heal": 0.2},    # 처치 스택 + 패링
            "광전사": {"damage": 0.9, "tank": 0.5, "support": 0.2, "heal": 0.4},    # HP 소모 + 흡혈
            "기사": {"tank": 0.9, "support": 0.7, "damage": 0.4, "heal": 0.3},      # 의무 스택 + 보호
            "암흑기사": {"damage": 0.8, "tank": 0.6, "support": 0.3, "heal": 0.5},  # 흡혈 + 암흑 오라
            "용기사": {"damage": 0.8, "tank": 0.5, "support": 0.4, "heal": 0.2},    # 용의표식 + 화염
            "아크메이지": {"damage": 0.9, "support": 0.6, "tank": 0.2, "heal": 0.3}, # 원소 순환 + 번개
            
            # Phase 2A 추가 직업들
            "드루이드": {"heal": 0.8, "support": 0.7, "damage": 0.5, "tank": 0.4},   # 자연 변신 + 회복
            "신관": {"heal": 0.9, "support": 0.8, "damage": 0.4, "tank": 0.5},      # 속죄 + 신성력
            "마검사": {"damage": 0.8, "support": 0.5, "tank": 0.4, "heal": 0.3},     # 원소 검기 혼합형
            "몽크": {"damage": 0.7, "heal": 0.6, "support": 0.5, "tank": 0.6},      # 기공 + 밸런스
            "네크로맨서": {"damage": 0.8, "support": 0.6, "tank": 0.3, "heal": 0.5}, # 영혼 조작 + 흡수
            "사무라이": {"damage": 0.9, "tank": 0.5, "support": 0.3, "heal": 0.2},   # 의지 게이지 + 거합
        }
        
        return role_configs.get(self.character_class, {
            "damage": 0.5, "tank": 0.5, "support": 0.5, "heal": 0.5
        })
    
    def choose_action(self, character, party_members: List, enemies: List, battlefield_state: Dict) -> Dict:
        """아군이 취할 최적 행동 선택"""
        if not character.is_alive:
            return {"type": "wait", "priority": 0}
        
        # 상황 분석
        situation = self._analyze_party_situation(character, party_members, enemies, battlefield_state)
        
        # 직업별 특수 분석 추가
        if character.character_class == "드루이드":
            druid_analysis = self._analyze_druid_nature_gauge(character, enemies)
            situation.update(druid_analysis)
        elif character.character_class == "신관":
            priest_analysis = self._analyze_priest_atonement_system(character, party_members)
            situation.update(priest_analysis)
        elif character.character_class == "마검사":
            mystic_analysis = self._analyze_mystic_sword_elemental_harmony(character, enemies)
            situation.update(mystic_analysis)
        elif character.character_class == "몽크":
            monk_analysis = self._analyze_monk_chi_balance(character, party_members, enemies)
            situation.update(monk_analysis)
        elif character.character_class == "네크로맨서":
            necro_analysis = self._analyze_necromancer_soul_management(character, enemies)
            situation.update(necro_analysis)
        elif character.character_class == "사무라이":
            samurai_analysis = self._analyze_samurai_willpower_system(character, enemies)
            situation.update(samurai_analysis)
        
        # 행동 옵션 생성
        action_options = []
        
        # 1. 치료 행동 검토
        heal_options = self._generate_heal_options(character, party_members, situation)
        action_options.extend(heal_options)
        
        # 2. 공격 행동 검토
        attack_options = self._generate_attack_options(character, enemies, situation)
        action_options.extend(attack_options)
        
        # 3. 지원 행동 검토
        support_options = self._generate_support_options(character, party_members, situation)
        action_options.extend(support_options)
        
        # 4. 방어 행동 검토
        if situation['threat_level'] >= ThreatLevel.HIGH:
            defend_option = self._generate_defend_option(character, situation)
            if defend_option:
                action_options.append(defend_option)
        
        # 최적 행동 선택
        if action_options:
            best_action = max(action_options, key=lambda x: x['priority'])
            return best_action
        
        # 기본 행동
        return {"type": "basic_attack", "target": enemies[0] if enemies else None, "priority": 10}
    
    def _analyze_party_situation(self, character, party_members: List, enemies: List, battlefield_state: Dict) -> Dict:
        """파티 상황 분석"""
        situation = {
            'self_health_ratio': character.current_hp / character.max_hp,
            'self_mp_ratio': character.current_mp / character.max_mp,
            'party_health_avg': sum(m.current_hp / m.max_hp for m in party_members if m.is_alive) / len([m for m in party_members if m.is_alive]),
            'critical_members': [m for m in party_members if m.is_alive and m.current_hp / m.max_hp < 0.25],
            'injured_members': [m for m in party_members if m.is_alive and m.current_hp / m.max_hp < 0.6],
            'enemies_count': len([e for e in enemies if e.is_alive]),
            'strongest_enemy': max(enemies, key=lambda e: e.physical_attack + e.magic_attack) if enemies else None,
            'threat_level': self._assess_threat_level(character, enemies),
            'player_needs_help': any(m.current_hp / m.max_hp < 0.3 for m in party_members if hasattr(m, 'is_player') and m.is_player)
        }
        
        return situation
    
    def _generate_heal_options(self, character, party_members: List, situation: Dict) -> List[Dict]:
        """치료 옵션 생성"""
        heal_options = []
        
        if self.role_weights.get('heal', 0) < 0.3:
            return heal_options  # 치료 능력이 낮으면 치료 시도 안함
        
        # 위급한 파티원 우선 치료
        for member in situation['critical_members']:
            priority = 90 * self.role_weights['heal'] * self.cooperation_level
            if hasattr(member, 'is_player') and member.is_player:
                priority *= 1.3  # 플레이어 우선 치료
            
            heal_options.append({
                'type': 'heal',
                'target': member,
                'priority': priority,
                'expected_outcome': f"{member.name} 치료"
            })
        
        return heal_options
    
    def _generate_attack_options(self, character, enemies: List, situation: Dict) -> List[Dict]:
        """공격 옵션 생성"""
        attack_options = []
        
        for enemy in enemies:
            if not enemy.is_alive:
                continue
            
            # 기본 공격 우선순위
            base_priority = 60 * self.role_weights.get('damage', 0.5)
            
            # 적 HP가 낮을 때 우선순위 상승
            enemy_hp_ratio = getattr(enemy, 'current_hp', 100) / getattr(enemy, 'max_hp', 100)
            if enemy_hp_ratio < 0.3:
                base_priority *= 1.5  # 마무리 공격
            
            # 가장 위험한 적 우선 공격
            if enemy == situation['strongest_enemy']:
                base_priority *= 1.2
            
            # 암살자는 그림자 시스템 고려
            if self.character_class == "암살자":
                shadow_priority = self._calculate_assassin_priority(character, enemy, situation)
                base_priority *= shadow_priority
            
            attack_options.append({
                'type': 'attack',
                'target': enemy,
                'priority': base_priority,
                'expected_outcome': f"{enemy.name} 공격"
            })
        
        return attack_options
    
    def _calculate_assassin_priority(self, character, enemy, situation: Dict) -> float:
        """암살자 아군의 그림자 시스템 우선순위 계산"""
        from .shadow_system import get_shadow_system
        
        shadow_system = get_shadow_system()
        shadow_count = shadow_system.get_shadow_count(character)
        
        # 그림자가 없으면 생성 우선
        if shadow_count == 0:
            return 1.2  # 그림자 생성 공격 우선
        
        # 그림자가 많으면 소모 공격 고려
        elif shadow_count >= 3:
            enemy_hp_ratio = getattr(enemy, 'current_hp', 100) / getattr(enemy, 'max_hp', 100)
            if enemy_hp_ratio < 0.4:
                return 1.8  # 마무리 궁극기
            else:
                return 1.4  # 강화 공격
        
        # 중간 상태는 상황에 따라
        return 1.1
    
    def _generate_support_options(self, character, party_members: List, situation: Dict) -> List[Dict]:
        """지원 옵션 생성"""
        support_options = []
        
        if self.role_weights.get('support', 0) < 0.4:
            return support_options
        
        # 버프 스킬 사용 고려
        if character.current_mp > character.max_mp * 0.3:
            priority = 40 * self.role_weights['support'] * self.cooperation_level
            
            support_options.append({
                'type': 'buff',
                'target': party_members,
                'priority': priority,
                'expected_outcome': "파티 버프"
            })
        
        return support_options
    
    def _generate_defend_option(self, character, situation: Dict) -> Optional[Dict]:
        """방어 옵션 생성"""
        if self.role_weights.get('tank', 0) < 0.5:
            return None
        
        if situation['threat_level'] >= ThreatLevel.CRITICAL:
            return {
                'type': 'defend',
                'priority': 70 * self.role_weights['tank'],
                'expected_outcome': "방어 태세"
            }
        
        return None


class SmartEnemyAI:
    """스마트 적 AI"""
    
    def __init__(self, personality: AIPersonality = AIPersonality.TACTICAL):
        self.personality = personality
        self.memory = AIMemory()
        self.turn_count = 0
        self.last_action = None
        self.health_threshold = 0.3  # 위험 상황 임계점
        
        # 성격별 가중치
        self.personality_weights = self._get_personality_weights()
        
    def _get_personality_weights(self) -> Dict[str, float]:
        """성격별 행동 가중치"""
        weights = {
            AIPersonality.AGGRESSIVE: {
                'attack': 0.7, 'skill': 0.2, 'defend': 0.05, 'heal': 0.05
            },
            AIPersonality.DEFENSIVE: {
                'attack': 0.3, 'skill': 0.2, 'defend': 0.4, 'heal': 0.1
            },
            AIPersonality.TACTICAL: {
                'attack': 0.4, 'skill': 0.35, 'defend': 0.15, 'heal': 0.1
            },
            AIPersonality.BERSERKER: {
                'attack': 0.8, 'skill': 0.15, 'defend': 0.02, 'heal': 0.03
            },
            AIPersonality.SUPPORT: {
                'attack': 0.2, 'skill': 0.4, 'defend': 0.2, 'heal': 0.2
            },
            AIPersonality.ADAPTIVE: {
                'attack': 0.4, 'skill': 0.3, 'defend': 0.2, 'heal': 0.1
            }
        }
        return weights[self.personality]
    
    def choose_action(self, character, allies: List, enemies: List, battlefield_state: Dict) -> Dict[str, Any]:
        """행동 선택 - BRV/HP 전략 + 그림자 시스템 적용"""
        self.turn_count += 1
        
        # 상황 분석
        situation = self._analyze_situation(character, allies, enemies, battlefield_state)
        
        # 🌑 그림자 시스템 분석 (암살자인 경우)
        if getattr(character, 'character_class', '') == '암살자':
            situation.update(self._analyze_shadow_system(character))
        
        # BRV/HP 전략 평가
        brv_hp_strategy = self._evaluate_brv_hp_strategy(character, enemies, situation)
        situation.update(brv_hp_strategy)
        
        # 행동 옵션 생성
        action_options = self._generate_action_options(character, allies, enemies, situation)
        
        # 성격과 상황에 따른 행동 선택
        chosen_action = self._select_best_action(action_options, situation)
        
        return chosen_action
    
    def _evaluate_brv_hp_strategy(self, character, enemies: List, situation: Dict) -> Dict:
        """BRV/HP 전략 평가"""
        current_brv = getattr(character, 'brv', 0)
        max_brv = getattr(character, 'max_brv', 100)
        brv_ratio = current_brv / max_brv if max_brv > 0 else 0
        
        strategy = {}
        
        # BRV 축적이 필요한 상황
        if brv_ratio < 0.3:
            strategy['priority_action'] = 'build_brv'
            strategy['brv_urgency'] = 'high'
        elif brv_ratio < 0.6:
            strategy['priority_action'] = 'build_brv'
            strategy['brv_urgency'] = 'medium'
        else:
            strategy['priority_action'] = 'hp_attack_ready'
            strategy['brv_urgency'] = 'low'
        
        # 적 HP 상태 확인 (HP 공격 타이밍)
        low_hp_enemies = [e for e in enemies if getattr(e, 'current_hp', 100) / getattr(e, 'max_hp', 100) < 0.4]
        if low_hp_enemies and brv_ratio >= 0.3:
            strategy['hp_attack_opportunity'] = True
            strategy['priority_targets'] = low_hp_enemies
        else:
            strategy['hp_attack_opportunity'] = False
            strategy['priority_targets'] = []
        
        # 위급 상황에서는 즉시 HP 공격
        if situation.get('threat_level') == ThreatLevel.CRITICAL and brv_ratio >= 0.2:
            strategy['emergency_hp_attack'] = True
        else:
            strategy['emergency_hp_attack'] = False
        
        return strategy
        
        # 기억 업데이트
        self._update_memory(chosen_action, situation)
        
        self.last_action = chosen_action
        return chosen_action
    
    def _analyze_situation(self, character, allies: List, enemies: List, battlefield_state: Dict) -> Dict:
        """상황 분석"""
        situation = {
            'self_health_ratio': character.current_hp / character.max_hp,
            'self_mp_ratio': character.current_mp / character.max_mp,
            'allies_count': len([a for a in allies if a.is_alive]),
            'enemies_count': len([e for e in enemies if e.is_alive]),
            'strongest_enemy': max(enemies, key=lambda e: e.physical_attack + e.magic_attack) if enemies else None,
            'weakest_enemy': min(enemies, key=lambda e: e.current_hp) if enemies else None,
            'threat_level': self._assess_threat_level(character, enemies),
            'allies_need_healing': any(a.current_hp / a.max_hp < 0.4 for a in allies if a.is_alive),
            'turn_count': self.turn_count
        }
        
        return situation
    
    def _assess_threat_level(self, character, enemies: List) -> ThreatLevel:
        """위협 수준 평가"""
        if not enemies:
            return ThreatLevel.LOW
        
        total_enemy_power = sum(e.physical_attack + e.magic_attack for e in enemies if e.is_alive)
        character_defense = character.physical_defense + character.magic_defense
        
        threat_ratio = total_enemy_power / max(1, character_defense)
        
        if threat_ratio > 3.0:
            return ThreatLevel.CRITICAL
        elif threat_ratio > 2.0:
            return ThreatLevel.HIGH
        elif threat_ratio > 1.0:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _generate_action_options(self, character, allies: List, enemies: List, situation: Dict) -> List[Dict]:
        """행동 옵션 생성 - BRV/HP 공격 시스템 적용"""
        options = []
        
        # 그림자 상태 분석 (암살자 전용)
        shadow_analysis = self._analyze_shadow_state(character, situation)
        
        # BRV/HP 공격 옵션
        for enemy in enemies:
            if enemy.is_alive:
                damage_potential = self._estimate_damage(character, enemy)
                current_brv = getattr(character, 'brv', 0)
                max_brv = getattr(character, 'max_brv', 100)
                
                # BRV 공격 옵션 (BRV 축적)
                brv_priority = damage_potential * self.personality_weights['attack']
                if current_brv < max_brv * 0.8:  # BRV가 80% 미만일 때 우선순위 상승
                    brv_priority *= 1.3
                
                # 암살자: 그림자 생성 필요 시 BRV 공격 우선순위 상승
                if shadow_analysis.get('should_generate_shadows', False):
                    brv_priority *= 1.4
                
                options.append({
                    'type': 'brv_attack',
                    'target': enemy,
                    'priority': brv_priority,
                    'expected_outcome': 'brv_damage'
                })
                
                # HP 공격 옵션 (BRV가 충분할 때만)
                min_brv_for_hp = max_brv * 0.3  # 최대 BRV의 30% 이상 필요
                if current_brv >= min_brv_for_hp:
                    hp_priority = damage_potential * self.personality_weights['attack'] * 1.5
                    
                    # 적의 HP가 낮을 때 HP 공격 우선순위 상승
                    enemy_hp_ratio = getattr(enemy, 'current_hp', 100) / getattr(enemy, 'max_hp', 100)
                    if enemy_hp_ratio < 0.4:
                        hp_priority *= 1.4
                    
                    options.append({
                        'type': 'hp_attack',
                        'target': enemy,
                        'priority': hp_priority,
                        'expected_outcome': 'hp_damage',
                        'brv_required': min_brv_for_hp
                    })
        
        # 스킬 옵션 (가상의 스킬들)
        if character.current_mp >= 10:
            options.extend(self._generate_skill_options(character, allies, enemies, situation))
        
        # 방어 옵션
        if situation['threat_level'] in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            options.append({
                'type': 'defend',
                'priority': 50 * self.personality_weights['defend'],
                'expected_outcome': 'defense_boost'
            })
        
        # 치료 옵션
        if situation['self_health_ratio'] < self.health_threshold:
            options.append({
                'type': 'heal',
                'target': character,
                'priority': 70 * self.personality_weights['heal'],
                'expected_outcome': 'heal'
            })
        
        return options
    
    def _generate_skill_options(self, character, allies: List, enemies: List, situation: Dict) -> List[Dict]:
        """스킬 옵션 생성 - 실제 게임 스킬 시스템과 연동"""
        skill_options = []
        
        # 그림자 상태 분석 (암살자 전용)
        shadow_analysis = self._analyze_shadow_state(character, situation)
        
        try:
            # 실제 게임의 스킬 시스템 사용
            from .new_skill_system import SkillDatabase
            skill_db = SkillDatabase()
            character_class = getattr(character, 'character_class', '전사')
            available_skills = skill_db.get_skills(character_class)
            
            if available_skills:
                for skill in available_skills:
                    mp_cost = skill.get('mp_cost', 0)
                    if mp_cost <= character.current_mp:
                        skill_priority = self._calculate_skill_priority(skill, character, enemies, situation, shadow_analysis)
                        
                        skill_options.append({
                            'type': 'skill',
                            'skill': skill,
                            'target': self._select_skill_target(skill, enemies),
                            'priority': skill_priority,
                            'expected_outcome': f"스킬: {skill.get('name', '알 수 없음')}",
                            'mp_cost': mp_cost
                        })
        except ImportError:
            # 스킬 시스템을 찾을 수 없으면 가상 스킬 사용
            skill_options = self._generate_virtual_skill_options(character, allies, enemies, situation)
        
        return skill_options
    
    def _calculate_skill_priority(self, skill: Dict, character, enemies: List, situation: Dict, shadow_analysis: Dict = None) -> float:
        """스킬 우선순위 계산 - 특성 시스템 연동 강화"""
        base_priority = 50
        character_class = getattr(character, 'character_class', '전사')
        character_traits = getattr(character, 'traits', [])
        
        # 스킬 타입에 따른 우선순위
        skill_type = skill.get('type', 'unknown')
        if skill_type in ['BRV_ATTACK', 'brv_attack']:
            base_priority = 60 * self.personality_weights['attack']
        elif skill_type in ['HP_ATTACK', 'hp_attack']:
            base_priority = 80 * self.personality_weights['attack']
        elif skill_type in ['HEAL', 'heal', 'SUPPORT', 'support']:
            base_priority = 70 * self.personality_weights['heal']
        elif skill_type in ['DEBUFF', 'debuff']:
            base_priority = 65 * self.personality_weights['skill']
        
        # MP 효율성 고려
        mp_cost = skill.get('mp_cost', 0)
        mp_efficiency = 1.0 - (mp_cost / max(character.current_mp, 1)) * 0.3
        base_priority *= mp_efficiency
        
        # 특성 기반 우선순위 조정
        skill_name = skill.get('name', '')
        
        # 직업별 특성 반영 우선순위
        for trait in character_traits:
            trait_name = getattr(trait, 'name', '')
            trait_effects = getattr(trait, 'effects', {})
            trait_type = getattr(trait, 'trait_type', 'passive')
            
            # 공격력 증가 특성
            if '공격력' in trait_name and skill_type in ['BRV_ATTACK', 'HP_ATTACK', 'BRV_HP_ATTACK']:
                base_priority *= 1.2
            
            # 특정 스킬 타입 특화 특성
            if '마법' in trait_name and 'magic' in skill.get('element', '').lower():
                base_priority *= 1.15
            
            # 크리티컬 특성
            if '크리티컬' in trait_name or '치명타' in trait_name:
                base_priority *= 1.1
            
            # 상태이상 특성
            if '독' in trait_name and 'poison' in skill.get('status_effect', ''):
                base_priority *= 1.3
            
            # 속성 특화 특성
            if '화염' in trait_name and 'fire' in skill.get('element', '').lower():
                base_priority *= 1.2
            elif '빙결' in trait_name and 'ice' in skill.get('element', '').lower():
                base_priority *= 1.2
            elif '번개' in trait_name and 'lightning' in skill.get('element', '').lower():
                base_priority *= 1.2
        
        # 새로운 직업별 스킬 우선순위 조정
        if character_class == "검성":
            # 검기 스택 관련 스킬 우선순위
            sword_stacks = getattr(character, 'sword_aura_stacks', 0)
            if '검기' in skill_name:
                if sword_stacks < 2:
                    base_priority *= 1.3  # 검기 쌓기 우선
                elif sword_stacks == 2 and '검압' in skill_name:
                    base_priority *= 1.8  # 최대 스택에서 소모 스킬 우선
        
        elif character_class == "검투사":
            # 처치 스택이 많을수록 명예의 일격 우선
            kill_stacks = getattr(character, 'kill_stacks', 0)
            if '명예의 일격' in skill_name and kill_stacks > 0:
                base_priority *= (1.0 + kill_stacks * 0.2)
            elif '패링' in skill_name and situation.get('threat_level', 1) >= ThreatLevel.HIGH:
                base_priority *= 1.6  # 위험 상황에서 패링 우선
        
        elif character_class == "광전사":
            # HP가 낮을수록 광기 스킬 우선
            hp_ratio = character.current_hp / character.max_hp
            if '광기' in skill_name and hp_ratio < 0.5:
                base_priority *= (2.0 - hp_ratio)  # HP 낮을수록 우선순위 증가
        
        elif character_class == "기사":
            # 아군이 위험할 때 보호 스킬 우선
            allies_in_danger = sum(1 for ally in [character] if ally.current_hp / ally.max_hp < 0.4)
            if '성스러운 돌격' in skill_name and allies_in_danger > 0:
                base_priority *= (1.0 + allies_in_danger * 0.5)
        
        elif character_class == "성기사":
            # 성역 히트 카운트가 3에 가까울수록 확장 우선
            sanctuary_hits = getattr(character, 'sanctuary_hits', 0)
            if '성역 확장' in skill_name and sanctuary_hits >= 2:
                base_priority *= 1.7
        
        elif character_class == "암흑기사":
            # 흡혈 관련 스킬 우선 (체력이 낮을 때)
            hp_ratio = character.current_hp / character.max_hp
            if ('흡혈' in skill_name or '생명력 흡수' in skill_name) and hp_ratio < 0.6:
                base_priority *= (1.5 - hp_ratio * 0.5)
        
        elif character_class == "용기사":
            # 용의표식이 쌓였을 때 폭발 스킬 우선
            dragon_marks = sum(getattr(enemy, 'dragon_mark_stacks', 0) for enemy in enemies)
            if '용의 분노' in skill_name and dragon_marks >= 2:
                base_priority *= 1.6
        
        elif character_class == "아크메이지":
            # 원소 순환 시스템 고려
            elemental_combo = getattr(character, 'elemental_combo', 0)
            if elemental_combo >= 2 and any(elem in skill_name for elem in ['라이트닝', '파이어', '아이스']):
                base_priority *= 1.4  # 원소 연쇄 기회
        
        # 암살자 스킬: 그림자 시스템 고려
        elif shadow_analysis and character_class == "암살자":
            # 그림자 생성 스킬 (기본 공격류)
            shadow_count = getattr(character, 'shadow_count', 0)
            if '그림자' in skill_name and shadow_count < 3:
                base_priority *= 1.4  # 그림자 부족 시 생성 우선
            elif '폭발' in skill_name and shadow_count >= 2:
                base_priority *= 1.6  # 그림자 충분 시 폭발 우선
        
        # 🌟 새로운 직업들 AI 패턴 추가
        elif character_class == "시간술사":
            # 시간 되돌리기 스택 시스템
            time_rewind_stacks = getattr(character, 'time_rewind_stacks', 0)
            hp_ratio = character.current_hp / character.max_hp
            
            if '시간왜곡' in skill_name and time_rewind_stacks < 3:
                base_priority *= 1.3  # 시간 스택 쌓기 우선
            elif '시간되돌리기' in skill_name and (hp_ratio < 0.4 or time_rewind_stacks >= 2):
                base_priority *= 1.8  # 위험하거나 스택 충분할 때 회복 우선
            elif '시간정지' in skill_name and situation.get('threat_level', 1) >= ThreatLevel.HIGH:
                base_priority *= 1.7  # 위험 상황에서 시간정지 우선
        
        elif character_class == "차원술사":
            # 차원 방패와 잔상 스택 시스템
            dimension_shield = getattr(character, 'dimension_shield_stacks', 0)
            afterimage_stacks = getattr(character, 'afterimage_stacks', 0)
            threat_level = situation.get('threat_level', 1)
            
            if '차원장막' in skill_name and (dimension_shield < 3 or threat_level >= ThreatLevel.HIGH):
                base_priority *= 1.4  # 방어 부족 시 장막 우선
            elif '잔상분신' in skill_name and afterimage_stacks < 5:
                base_priority *= 1.2  # 잔상 부족 시 분신 우선
            elif '공간도약' in skill_name and afterimage_stacks >= 3:
                base_priority *= 1.5  # 잔상 충분할 때 도약 강화
        
        elif character_class == "철학자":
            # 지혜 스택 시스템
            wisdom_stacks = getattr(character, 'wisdom_stacks', 0)
            enemy_analyzed = any(hasattr(enemy, 'analyzed') for enemy in enemies)
            
            if '진실간파' in skill_name and not enemy_analyzed:
                base_priority *= 1.6  # 적 분석 우선
            elif '철학적사고' in skill_name and wisdom_stacks < 5:
                base_priority *= 1.3  # 지혜 스택 부족 시 사고 우선
            elif '존재부정' in skill_name and wisdom_stacks >= 3:
                base_priority *= (1.0 + wisdom_stacks * 0.15)  # 지혜에 비례 강화
        
        elif character_class == "연금술사":
            # 포션 제작 스택 시스템
            potion_stacks = getattr(character, 'potion_craft_stacks', 0)
            team_hp_ratio = sum(ally.current_hp / ally.max_hp for ally in [character]) / max(1, len([character]))
            
            if '물질변환' in skill_name and potion_stacks < 3:
                base_priority *= 1.3  # 포션 스택 부족 시 변환 우선
            elif '회복포션' in skill_name and (team_hp_ratio < 0.6 or potion_stacks >= 2):
                base_priority *= 1.5  # 체력 부족하거나 포션 충분할 때 회복 우선
            elif '산성용해' in skill_name and potion_stacks >= 1:
                base_priority *= 1.2  # 포션으로 공격 강화
            # 그림자 생성 스킬 (기본 공격류)
            if '그림자 강타' in skill_name:
                if shadow_analysis.get('should_generate_shadows', False):
                    base_priority *= 1.5  # 그림자가 필요하면 우선순위 상승
            
            # 그림자 소모 스킬
            elif any(name in skill_name for name in ['그림자 분신', '그림자 칼날', '그림자 폭발', '암영 난무']):
                if shadow_analysis.get('should_consume_shadows', False) and shadow_analysis.get('has_shadows', False):
                    base_priority *= 1.8  # 그림자 소모가 유리하면 높은 우선순위
                elif not shadow_analysis.get('has_shadows', False):
                    base_priority *= 0.3  # 그림자가 없으면 우선순위 하락
            
            # 궁극기 (그림자 전부 소모)
            elif '그림자 처형' in skill_name:
                shadow_count = shadow_analysis.get('shadow_count', 0)
                if shadow_analysis.get('optimal_shadow_use', False) and shadow_count >= 3:
                    base_priority *= 2.0  # 최적 상황에서 궁극기 우선순위 최대
                elif shadow_count == 0:
                    base_priority *= 0.1  # 그림자가 없으면 거의 사용 안함
        
        # 위험 상황에서는 강력한 스킬 우선
        if situation['threat_level'] >= ThreatLevel.HIGH:
            power = skill.get('power', 1.0)
            base_priority *= (1.0 + power * 0.2)
        
        return base_priority
    
    def _select_skill_target(self, skill: Dict, enemies: List):
        """스킬에 적절한 타겟 선택"""
        target_type = skill.get('target', 'single_enemy')
        
        if target_type in ['single_enemy', 'SINGLE_ENEMY', '적1명']:
            # 가장 위험한 적 선택
            alive_enemies = [e for e in enemies if e.is_alive]
            if alive_enemies:
                return max(alive_enemies, key=lambda e: e.physical_attack + e.magic_attack)
        elif target_type in ['all_enemies', 'ALL_ENEMIES', '적전체']:
            return enemies  # 모든 적
        
        # 기본적으로 첫 번째 살아있는 적 반환
        alive_enemies = [e for e in enemies if e.is_alive]
        return alive_enemies[0] if alive_enemies else None
    
    def _generate_virtual_skill_options(self, character, allies: List, enemies: List, situation: Dict) -> List[Dict]:
        """가상 스킬 옵션 생성 (폴백)"""
        skill_options = []
        character_class = getattr(character, 'character_class', '전사')
        
        # 직업별 가상 스킬 정의
        virtual_skills = {
            '전사': [
                {'name': '강공격', 'type': 'BRV_ATTACK', 'power': 1.5, 'mp_cost': 20, 'target': 'single_enemy'},
                {'name': '결정타', 'type': 'HP_ATTACK', 'power': 2.0, 'mp_cost': 40, 'target': 'single_enemy'}
            ],
            '궁수': [
                {'name': '연속사격', 'type': 'BRV_ATTACK', 'power': 1.3, 'mp_cost': 15, 'target': 'single_enemy'},
                {'name': '관통사격', 'type': 'HP_ATTACK', 'power': 1.8, 'mp_cost': 35, 'target': 'single_enemy'}
            ],
            '성기사': [
                {'name': '치유술', 'type': 'HEAL', 'power': 1.5, 'mp_cost': 30, 'target': 'ally'},
                {'name': '신성공격', 'type': 'BRV_ATTACK', 'power': 1.4, 'mp_cost': 25, 'target': 'single_enemy'}
            ]
        }
        
        class_skills = virtual_skills.get(character_class, virtual_skills['전사'])
        
        for skill in class_skills:
            mp_cost = skill.get('mp_cost', 0)
            if mp_cost <= character.current_mp:
                skill_priority = self._calculate_skill_priority(skill, character, enemies, situation)
                
                skill_options.append({
                    'type': 'skill',
                    'skill': skill,
                    'target': self._select_skill_target(skill, enemies),
                    'priority': skill_priority,
                    'expected_outcome': f"가상스킬: {skill.get('name', '알 수 없음')}",
                    'mp_cost': mp_cost
                })
        
        return skill_options
        skill_options = []
        mp_ratio = situation['self_mp_ratio']
        health_ratio = situation['self_health_ratio']
        floor_level = getattr(character, 'floor_level', 1)
        current_brv = getattr(character, 'brv', 0)
        max_brv = getattr(character, 'max_brv', 100)
        
        # 층수별 스킬 파워 제한 (최대 2.5배까지만)
        floor_level = min(floor_level, 8)  # 8층 이후는 동일한 파워
        skill_power_multiplier = 1.0 + min(floor_level * 0.1, 1.5)  # 최대 250% (층당 10%, 최대 제한)
        
        # === BRV 공격 스킬 ===
        if len(enemies) >= 2 and mp_ratio > 0.3:
            skill_options.append({
                'type': 'brv_skill',
                'skill_name': 'flame_burst',
                'targets': enemies[:3],
                'mp_cost': 18,
                'priority': 70 * self.personality_weights['skill'],
                'expected_outcome': 'area_brv_damage',
                'element': 'fire',
                'status_chance': 0.4,
                'status_effect': 'burn',
                'sfx': 'fire_explosion',
                'power_multiplier': skill_power_multiplier,
                'description': '🔥 화염 폭발 - 광역 BRV 데미지 + 화상'
            })
        
        # === HP 공격 스킬 (BRV 요구) ===
        min_brv_for_hp_skill = max_brv * 0.4  # HP 스킬은 더 많은 BRV 필요
        if current_brv >= min_brv_for_hp_skill and floor_level >= 4 and len(enemies) >= 3 and mp_ratio > 0.4:
            skill_options.append({
                'type': 'hp_skill',
                'skill_name': 'lava_eruption',
                'targets': enemies,
                'mp_cost': 25,
                'priority': 85 * self.personality_weights['skill'],
                'expected_outcome': 'massive_hp_damage',
                'element': 'fire',
                'status_chance': 0.6,
                'status_effect': 'burn',
                'requires_brv': True,
                'brv_required': min_brv_for_hp_skill,
                'sfx': 'earthquake_rumble',
                'description': '🌋 용암 분출 - 모든 적에게 강력한 HP 데미지'
            })
            
        # 화염 장벽 (자가 버프)
        if mp_ratio > 0.35 and health_ratio < 0.6:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'fire_shield',
                'target': character,
                'mp_cost': 20,
                'priority': 60 * self.personality_weights['skill'],
                'expected_outcome': 'fire_defense',
                'element': 'fire',
                'status_effect': 'thorns',
                'sfx': 'fire_whoosh',
                'description': '🔥🛡️ 화염 방패 - 공격자에게 반사 데미지'
            })
        
        # === 빙결 원소 스킬 ===
        if mp_ratio > 0.25:
            strongest_enemy = situation.get('strongest_enemy')
            if strongest_enemy:
                skill_options.append({
                    'type': 'skill',
                    'skill_name': 'ice_shard',
                    'target': strongest_enemy,
                    'mp_cost': 15,
                    'priority': 65 * self.personality_weights['skill'],
                    'expected_outcome': 'ice_damage',
                    'element': 'ice',
                    'status_chance': 0.5,
                    'status_effect': 'freeze',
                    'sfx': 'ice_crack',
                    'description': '❄️ 얼음 파편 - 빙결 데미지 + 둔화'
                })
        
        # 눈보라 (광역 빙결)
        if floor_level >= 3 and len(enemies) >= 2 and mp_ratio > 0.4:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'blizzard',
                'targets': enemies[:4],
                'mp_cost': 22,
                'priority': 75 * self.personality_weights['skill'],
                'expected_outcome': 'ice_area_damage',
                'element': 'ice',
                'status_chance': 0.7,
                'status_effect': 'frostbite',
                'sfx': 'wind_howling',
                'description': '🌨️ 눈보라 - 광역 빙결 데미지 + 동상'
            })
            
        # 절대영도 (즉사 위험) - 캐스트 시간 필요
        if floor_level >= 5 and mp_ratio > 0.6:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'absolute_zero',
                'target': enemies[0] if enemies else None,
                'mp_cost': 30,
                'priority': 90 * self.personality_weights['skill'],
                'expected_outcome': 'instant_kill_chance',
                'element': 'ice',
                'status_chance': 0.2,
                'status_effect': 'petrify',
                'sfx': 'ice_shatter',
                'cast_time': 2,  # 2턴 캐스트
                'power_multiplier': skill_power_multiplier * 1.5,  # 강력한 스킬
                'description': '🧊 절대영도 - 즉사 확률이 있는 강력한 빙결 공격 (2턴 캐스트)'
            })
        
        # === 번개 원소 스킬 ===
        if mp_ratio > 0.3:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'lightning_bolt',
                'target': random.choice(enemies) if enemies else None,
                'mp_cost': 16,
                'priority': 70 * self.personality_weights['skill'],
                'expected_outcome': 'lightning_damage',
                'element': 'lightning',
                'status_chance': 0.4,
                'status_effect': 'paralysis',
                'sfx': 'thunder_crack',
                'description': '⚡ 번개 화살 - 전격 데미지 + 마비'
            })
            
        # 연쇄 번개
        if len(enemies) >= 2 and mp_ratio > 0.35:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'chain_lightning',
                'targets': enemies[:3],
                'mp_cost': 20,
                'priority': 80 * self.personality_weights['skill'],
                'expected_outcome': 'chain_lightning_damage',
                'element': 'lightning',
                'status_chance': 0.6,
                'status_effect': 'lightning_shock',
                'sfx': 'electric_zap',
                'description': '⚡🔗 연쇄 번개 - 여러 적에게 점프하는 전격'
            })
        
        # === 독 원소 스킬 ===
        if mp_ratio > 0.2:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'poison_cloud',
                'targets': enemies[:2],
                'mp_cost': 12,
                'priority': 55 * self.personality_weights['skill'],
                'expected_outcome': 'poison_dot',
                'element': 'poison',
                'status_chance': 0.8,
                'status_effect': 'poison',
                'sfx': 'gas_hiss',
                'description': '☠️ 독구름 - 지속 독 데미지'
            })
            
        # 맹독 스파이크
        if floor_level >= 3 and mp_ratio > 0.3:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'toxic_spikes',
                'targets': enemies[:3],
                'mp_cost': 18,
                'priority': 65 * self.personality_weights['skill'],
                'expected_outcome': 'toxic_damage',
                'element': 'poison',
                'status_chance': 0.9,
                'status_effect': 'corrosion',
                'sfx': 'poison_splash',
                'description': '☠️🗡️ 맹독 가시 - 부식 효과가 있는 독 공격'
            })
        
        # === 암흑 원소 스킬 ===
        if mp_ratio > 0.4:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'shadow_strike',
                'target': situation.get('weakest_enemy'),
                'mp_cost': 18,
                'priority': 75 * self.personality_weights['skill'],
                'expected_outcome': 'shadow_damage',
                'element': 'dark',
                'status_chance': 0.3,
                'status_effect': 'fear',
                'sfx': 'shadow_whisper',
                'description': '🌙 그림자 강타 - 기본 공격으로 그림자 생성'
            })
            
        # 생명력 흡수
        if mp_ratio > 0.3 and health_ratio < 0.7:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'life_drain',
                'target': situation.get('strongest_enemy'),
                'mp_cost': 16,
                'priority': 65 * self.personality_weights['skill'],
                'expected_outcome': 'vampire_attack',
                'element': 'dark',
                'status_effect': 'vampire',
                'sfx': 'dark_magic',
                'description': '🩸 생명력 흡수 - 데미지와 동시에 체력 회복'
            })
            
        # 저주의 시선
        if floor_level >= 4 and mp_ratio > 0.5:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'cursed_gaze',
                'target': situation.get('strongest_enemy'),
                'mp_cost': 25,
                'priority': 85 * self.personality_weights['skill'],
                'expected_outcome': 'multiple_debuffs',
                'element': 'dark',
                'status_chance': 0.7,
                'status_effect': 'doom',
                'sfx': 'evil_laugh',
                'description': '👁️ 저주의 시선 - 파멸 카운트다운 시작'
            })
        
        # === 신비 원소 스킬 ===
        if floor_level >= 3 and mp_ratio > 0.4:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'arcane_missile',
                'target': random.choice(enemies) if enemies else None,
                'mp_cost': 20,
                'priority': 70 * self.personality_weights['skill'],
                'expected_outcome': 'arcane_damage',
                'element': 'arcane',
                'status_chance': 0.3,
                'status_effect': 'silence',
                'sfx': 'magic_missile',
                'description': '🔮 신비한 화살 - 마법 데미지 + 침묵'
            })
            
        # 마나 소모
        if mp_ratio > 0.35:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'mana_burn',
                'target': enemies[0] if enemies else None,
                'mp_cost': 15,
                'priority': 60 * self.personality_weights['skill'],
                'expected_outcome': 'mana_damage',
                'element': 'arcane',
                'status_chance': 0.8,
                'status_effect': 'mana_burn',
                'sfx': 'mana_drain',
                'description': '🔥🔮 마나 소모 - MP 제거 + 정신 데미지'
            })
        
        # === 대지 원소 스킬 ===
        if floor_level >= 2 and mp_ratio > 0.3:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'earth_spike',
                'target': random.choice(enemies) if enemies else None,
                'mp_cost': 14,
                'priority': 65 * self.personality_weights['skill'],
                'expected_outcome': 'earth_damage',
                'element': 'earth',
                'status_chance': 0.4,
                'status_effect': 'root',
                'sfx': 'rock_break',
                'description': '🪨 대지 가시 - 물리 데미지 + 속박'
            })
            
        # 지진 - 캐스트 시간 필요
        if floor_level >= 4 and len(enemies) >= 3 and mp_ratio > 0.5:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'earthquake',
                'targets': enemies,
                'mp_cost': 28,
                'priority': 90 * self.personality_weights['skill'],
                'expected_outcome': 'massive_earth_damage',
                'element': 'earth',
                'status_chance': 0.5,
                'status_effect': 'stun',
                'sfx': 'earthquake_rumble',
                'cast_time': 1,  # 1턴 캐스트
                'power_multiplier': skill_power_multiplier * 1.3,
                'description': '🌍 지진 - 모든 적에게 강력한 대지 데미지 + 기절 (1턴 캐스트)'
            })
        
        # === 바람 원소 스킬 ===
        if mp_ratio > 0.25:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'wind_slash',
                'targets': enemies[:2],
                'mp_cost': 13,
                'priority': 60 * self.personality_weights['skill'],
                'expected_outcome': 'wind_damage',
                'element': 'wind',
                'status_chance': 0.3,
                'status_effect': 'blind',
                'sfx': 'wind_cutting',
                'description': '💨 바람 베기 - 관통 데미지 + 실명'
            })
            
        # 회오리바람
        if floor_level >= 3 and len(enemies) >= 2 and mp_ratio > 0.4:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'tornado',
                'targets': enemies[:3],
                'mp_cost': 22,
                'priority': 80 * self.personality_weights['skill'],
                'expected_outcome': 'wind_area_damage',
                'element': 'wind',
                'status_chance': 0.6,
                'status_effect': 'confusion',
                'sfx': 'wind_howling',
                'description': '🌪️ 회오리바람 - 광역 바람 데미지 + 혼란'
            })
        
        # === 물 원소 스킬 ===
        if mp_ratio > 0.3:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'water_wave',
                'targets': enemies[:3],
                'mp_cost': 16,
                'priority': 65 * self.personality_weights['skill'],
                'expected_outcome': 'water_damage',
                'element': 'water',
                'status_chance': 0.4,
                'status_effect': 'slow',
                'sfx': 'water_splash',
                'description': '🌊 물결 공격 - 광역 물 데미지 + 둔화'
            })
            
        # === 빛 원소 스킬 (보스급) ===
        if floor_level >= 5 and mp_ratio > 0.6:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'divine_light',
                'targets': enemies[:2],
                'mp_cost': 30,
                'priority': 95 * self.personality_weights['skill'],
                'expected_outcome': 'holy_damage',
                'element': 'light',
                'status_chance': 0.5,
                'status_effect': 'blind',
                'sfx': 'holy_chime',
                'description': '✨ 신성한 빛 - 강력한 빛 데미지 + 실명'
            })
        
        # === 강화 스킬 ===
        # 광폭화 (광전사 AI 선호)
        if health_ratio > 0.6 and mp_ratio > 0.3:
            berserk_priority = 90 if self.personality == AIPersonality.BERSERKER else 50
            skill_options.append({
                'type': 'skill',
                'skill_name': 'berserk_rage',
                'target': character,
                'mp_cost': 18,
                'priority': berserk_priority * self.personality_weights['skill'],
                'expected_outcome': 'self_buff',
                'status_effect': 'berserk',
                'sfx': 'roar',
                'description': '� 광폭화 - 공격력 대폭 증가, 방어력 감소'
            })
            
        # 강화 마법 (전술형 AI 선호)
        if mp_ratio > 0.4 and self.personality == AIPersonality.TACTICAL:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'empowerment',
                'target': character,
                'mp_cost': 20,
                'priority': 80 * self.personality_weights['skill'],
                'expected_outcome': 'multi_buff',
                'status_effect': 'empowered',
                'sfx': 'power_up',
                'description': '💪 강화술 - 모든 능력치 증가'
            })
            
        # 재생술 (지원형 AI 선호)
        if health_ratio < 0.6 and mp_ratio > 0.25:
            heal_priority = 85 if self.personality == AIPersonality.SUPPORT else 55
            skill_options.append({
                'type': 'skill',
                'skill_name': 'regeneration',
                'target': character,
                'mp_cost': 14,
                'priority': heal_priority * self.personality_weights['heal'],
                'expected_outcome': 'heal_over_time',
                'status_effect': 'regeneration',
                'sfx': 'healing_chime',
                'description': '💚 재생술 - 지속 체력 회복'
            })
            
        # 마법 방벽 (방어형 AI 선호)
        if situation['threat_level'] >= ThreatLevel.HIGH and mp_ratio > 0.3:
            shield_priority = 95 if self.personality == AIPersonality.DEFENSIVE else 40
            skill_options.append({
                'type': 'skill',
                'skill_name': 'magic_barrier',
                'target': character,
                'mp_cost': 20,
                'priority': shield_priority * self.personality_weights['defend'],
                'expected_outcome': 'damage_shield',
                'status_effect': 'magic_shield',
                'sfx': 'shield_activate',
                'description': '🛡️ 마법 방벽 - 마법 데미지 크게 감소'
            })
            
        # 집중 (크리티컬 증가)
        if mp_ratio > 0.3:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'focus_mind',
                'target': character,
                'mp_cost': 15,
                'priority': 65 * self.personality_weights['skill'],
                'expected_outcome': 'crit_buff',
                'status_effect': 'focus',
                'sfx': 'meditation_bell',
                'description': '🎯 정신 집중 - 크리티컬 확률 대폭 증가'
            })
        
        # === 복합 디버프 스킬 ===
        # 약화의 저주
        if situation['threat_level'] >= ThreatLevel.MEDIUM and mp_ratio > 0.25:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'weakness_curse',
                'target': situation.get('strongest_enemy'),
                'mp_cost': 16,
                'priority': 70 * self.personality_weights['skill'],
                'expected_outcome': 'multiple_debuffs',
                'element': 'dark',
                'status_chance': 0.8,
                'status_effect': 'weakened',
                'sfx': 'curse_whisper',
                'description': '🌀 약화 저주 - 공격력/방어력 대폭 감소'
            })
            
        # 갑옷 파괴
        if mp_ratio > 0.3:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'armor_shatter',
                'target': situation.get('strongest_enemy'),
                'mp_cost': 18,
                'priority': 75 * self.personality_weights['skill'],
                'expected_outcome': 'armor_break',
                'status_chance': 0.9,
                'status_effect': 'armor_break',
                'sfx': 'metal_break',
                'description': '🔨 갑옷 파괴 - 방어력 무력화'
            })
            
        # 기절타 (적응형 AI의 전술)
        if mp_ratio > 0.4 and self.personality == AIPersonality.ADAPTIVE:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'stunning_blow',
                'target': situation.get('strongest_enemy'),
                'mp_cost': 22,
                'priority': 80 * self.personality_weights['skill'],
                'expected_outcome': 'stun_attack',
                'status_chance': 0.7,
                'status_effect': 'stun',
                'sfx': 'heavy_impact',
                'description': '⚡ 기절타 - 높은 데미지 + 기절 효과'
            })
        
        # === 특수 스킬 ===
        # 혼란의 마법
        if floor_level >= 3 and mp_ratio > 0.3:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'confusion_spell',
                'targets': enemies[:2],
                'mp_cost': 17,
                'priority': 60 * self.personality_weights['skill'],
                'expected_outcome': 'confusion_debuff',
                'element': 'arcane',
                'status_chance': 0.6,
                'status_effect': 'confusion',
                'sfx': 'mind_magic',
                'description': '🌀 혼란술 - 행동 정확도 크게 감소'
            })
            
        # 매혹의 시선
        if floor_level >= 4 and mp_ratio > 0.4:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'charm_gaze',
                'target': enemies[0] if enemies else None,
                'mp_cost': 24,
                'priority': 85 * self.personality_weights['skill'],
                'expected_outcome': 'mind_control',
                'status_chance': 0.4,
                'status_effect': 'charm',
                'sfx': 'hypnotic_sound',
                'description': '💖 매혹의 시선 - 적을 아군으로 전환'
            })
            
        # 피의 갈증 (스택 버프)
        if health_ratio < 0.5 and mp_ratio > 0.3:
            skill_options.append({
                'type': 'skill',
                'skill_name': 'bloodthirst',
                'target': character,
                'mp_cost': 16,
                'priority': 70 * self.personality_weights['skill'],
                'expected_outcome': 'bloodlust_stack',
                'status_effect': 'bloodlust',
                'sfx': 'vampire_bite',
                'description': '🩸 피의 갈증 - 공격 시마다 공격력 증가 (중첩)'
            })
        
        return skill_options
    
    def _estimate_damage(self, attacker, target) -> float:
        """예상 데미지 계산"""
        base_damage = attacker.physical_attack
        defense = target.physical_defense
        
        # 간단한 데미지 공식
        estimated_damage = max(1, base_damage - defense * 0.5)
        
        # 크리티컬 확률 고려
        crit_chance = 0.1
        avg_damage = estimated_damage * (1 + crit_chance * 0.5)
        
        return avg_damage
    
    def _select_best_action(self, action_options: List[Dict], situation: Dict) -> Dict:
        """최적 행동 선택 - BRV/HP 전략 적용"""
        if not action_options:
            return {'type': 'wait'}
        
        # BRV/HP 전략에 따른 우선순위 조정
        self._adjust_priorities_for_brv_hp_strategy(action_options, situation)
        
        # 적응형 AI의 경우 과거 경험 반영
        if self.personality == AIPersonality.ADAPTIVE:
            self._adjust_priorities_based_on_memory(action_options, situation)
        
        # 상황별 우선순위 조정
        self._adjust_priorities_for_situation(action_options, situation)
        
        # 확률적 선택 (최고 우선순위가 항상 선택되지 않도록)
        sorted_options = sorted(action_options, key=lambda x: x['priority'], reverse=True)
        
        # 상위 3개 중에서 가중 랜덤 선택
        top_options = sorted_options[:min(3, len(sorted_options))]
        weights = [opt['priority'] for opt in top_options]
        
        if sum(weights) == 0:
            return random.choice(top_options)
        
        chosen = random.choices(top_options, weights=weights)[0]
        return chosen
    
    def _adjust_priorities_for_brv_hp_strategy(self, action_options: List[Dict], situation: Dict):
        """BRV/HP 전략에 따른 우선순위 조정"""
        priority_action = situation.get('priority_action', 'build_brv')
        brv_urgency = situation.get('brv_urgency', 'medium')
        hp_attack_opportunity = situation.get('hp_attack_opportunity', False)
        emergency_hp_attack = situation.get('emergency_hp_attack', False)
        
        for option in action_options:
            action_type = option['type']
            
            # 긴급 상황에서 HP 공격 우선
            if emergency_hp_attack and action_type in ['hp_attack', 'hp_skill']:
                option['priority'] *= 2.0
            
            # BRV 축적이 우선인 상황
            elif priority_action == 'build_brv':
                if action_type in ['brv_attack', 'brv_skill']:
                    if brv_urgency == 'high':
                        option['priority'] *= 1.5
                    elif brv_urgency == 'medium':
                        option['priority'] *= 1.2
                elif action_type in ['hp_attack', 'hp_skill']:
                    option['priority'] *= 0.5  # HP 공격 우선순위 감소
            
            # HP 공격 기회가 있는 상황
            elif hp_attack_opportunity and action_type in ['hp_attack', 'hp_skill']:
                option['priority'] *= 1.3
                # 우선 타겟에 대한 추가 보너스
                if option.get('target') in situation.get('priority_targets', []):
                    option['priority'] *= 1.2
    
    def _adjust_priorities_based_on_memory(self, action_options: List[Dict], situation: Dict):
        """기억을 바탕으로 우선순위 조정"""
        for option in action_options:
            action_type = option['type']
            
            # 효과적이었던 전략에 보너스
            if action_type in self.memory.effective_strategies:
                option['priority'] *= 1.2
            
            # 실패했던 전략에 페널티
            if action_type in self.memory.failed_strategies:
                option['priority'] *= 0.8
    
    def _adjust_priorities_for_situation(self, action_options: List[Dict], situation: Dict):
        """상황별 우선순위 조정"""
        # 체력이 낮을 때 생존 우선
        if situation['self_health_ratio'] < 0.3:
            for option in action_options:
                if option['type'] in ['heal', 'defend']:
                    option['priority'] *= 1.5
                elif option['type'] == 'attack':
                    option['priority'] *= 0.7
        
        # 적이 많을 때 광역 공격 선호
        if situation['enemies_count'] >= 3:
            for option in action_options:
                if option.get('expected_outcome') == 'area_damage':
                    option['priority'] *= 1.3
        
        # 위험 상황에서 강력한 스킬 사용
        if situation['threat_level'] >= ThreatLevel.HIGH:
            for option in action_options:
                if option['type'] == 'skill' and option.get('mp_cost', 0) >= 15:
                    option['priority'] *= 1.2
    
    def _update_memory(self, chosen_action: Dict, situation: Dict):
        """기억 업데이트"""
        action_type = chosen_action['type']
        
        # 플레이어 패턴 학습 (가상)
        if 'player_last_action' in situation:
            player_action = situation['player_last_action']
            if player_action in self.memory.player_patterns:
                self.memory.player_patterns[player_action] += 1
            else:
                self.memory.player_patterns[player_action] = 1
    
    def learn_from_result(self, action_result: str, effectiveness: float):
        """결과에서 학습"""
        if self.last_action:
            action_type = self.last_action['type']
            
            if effectiveness > 0.7:  # 효과적이었음
                if action_type not in self.memory.effective_strategies:
                    self.memory.effective_strategies.append(action_type)
                
                # 실패 목록에서 제거
                if action_type in self.memory.failed_strategies:
                    self.memory.failed_strategies.remove(action_type)
            
            elif effectiveness < 0.3:  # 비효과적이었음
                if action_type not in self.memory.failed_strategies:
                    self.memory.failed_strategies.append(action_type)


class PartyAI:
    """파티 AI 시스템"""
    
    def __init__(self):
        self.coordination_bonus = 0.1
        self.formation_preferences = ['balanced', 'defensive', 'aggressive']
        self.current_formation = 'balanced'
        
    def suggest_party_action(self, party_members: List, enemies: List, battle_state: Dict) -> Dict:
        """파티 전체 행동 제안"""
        suggestions = {
            'formation': self._suggest_formation(party_members, enemies),
            'focus_target': self._select_focus_target(enemies),
            'coordination': self._plan_coordination(party_members, enemies),
            'priority_actions': self._get_priority_actions(party_members, battle_state)
        }
        
        return suggestions
    
    def _suggest_formation(self, party_members: List, enemies: List) -> str:
        """대형 제안"""
        total_party_hp = sum(m.current_hp for m in party_members if m.is_alive)
        max_party_hp = sum(m.max_hp for m in party_members if m.is_alive)
        
        health_ratio = total_party_hp / max(1, max_party_hp)
        
        if health_ratio < 0.4:
            return 'defensive'
        elif len(enemies) >= len(party_members) + 2:
            return 'defensive'
        else:
            return 'aggressive'
    
    def _select_focus_target(self, enemies: List):
        """집중 공격 대상 선택"""
        if not enemies:
            return None
        
        # 위협도 계산
        threat_scores = []
        for enemy in enemies:
            if enemy.is_alive:
                threat = (enemy.physical_attack + enemy.magic_attack) / max(1, enemy.current_hp)
                threat_scores.append((enemy, threat))
        
        if threat_scores:
            return max(threat_scores, key=lambda x: x[1])[0]
        return None
    
    def _plan_coordination(self, party_members: List, enemies: List) -> Dict:
        """협력 계획"""
        coordination = {
            'combo_attacks': [],
            'support_chains': [],
            'protective_actions': []
        }
        
        # 콤보 공격 기회 찾기
        attackers = [m for m in party_members if m.is_alive and m.current_mp >= 10]
        if len(attackers) >= 2:
            coordination['combo_attacks'] = attackers[:2]
        
        # 지원 체인 (힐러 -> 탱커 -> 딜러 순)
        healers = [m for m in party_members if m.character_class in ['마법사', '성직자']]
        if healers:
            coordination['support_chains'] = healers
        
        return coordination
    
    def _get_priority_actions(self, party_members: List, battle_state: Dict) -> List[str]:
        """우선순위 행동 목록"""
        priorities = []
        
        # 급한 치료가 필요한 멤버 확인
        critical_members = [m for m in party_members if m.is_alive and m.current_hp / m.max_hp < 0.25]
        if critical_members:
            priorities.append('emergency_heal')
        
        # 강력한 적이 있는 경우
        if any(e.physical_attack + e.magic_attack > 50 for e in battle_state.get('enemies', [])):
            priorities.append('focus_fire')
        
        # MP가 부족한 경우
        low_mp_members = [m for m in party_members if m.is_alive and m.current_mp / m.max_mp < 0.3]
        if len(low_mp_members) >= 2:
            priorities.append('conserve_mp')
        
        return priorities


# AI 인스턴스 생성 함수들
def create_smart_enemy(enemy_type: str = "default") -> SmartEnemyAI:
    """스마트 적 생성"""
    personality_map = {
        "goblin": AIPersonality.AGGRESSIVE,
        "orc": AIPersonality.BERSERKER,
        "skeleton": AIPersonality.DEFENSIVE,
        "wizard": AIPersonality.TACTICAL,
        "boss": AIPersonality.ADAPTIVE,
        "default": AIPersonality.TACTICAL
    }
    
    personality = personality_map.get(enemy_type, AIPersonality.TACTICAL)
    return SmartEnemyAI(personality)


def create_party_ai() -> PartyAI:
    """파티 AI 생성"""
    return PartyAI()


    def _analyze_shadow_state(self, character, situation: Dict) -> Dict:
        """그림자 상태 분석 (암살자 클래스 전용)"""
        from .shadow_system import ShadowSystem
        
        # 암살자가 아닌 경우 빈 딕셔너리 반환
        if character.character_class != "암살자":
            return {}
        
        shadow_system = ShadowSystem.get_instance()
        shadow_count = shadow_system.get_shadow_count(character.name)
        
        analysis = {
            'has_shadows': shadow_count > 0,
            'shadow_count': shadow_count,
            'can_empower': shadow_count >= 1,
            'optimal_shadow_use': False,
            'shadow_priority': 0.0,
            'should_generate_shadows': False,
            'should_consume_shadows': False
        }
        
        # 상황에 따른 그림자 사용 전략
        health_ratio = situation.get('self_health_ratio', 1.0)
        threat_level = situation.get('threat_level', 'LOW')
        enemy_count = situation.get('enemies_count', 0)
        
        # 위급 상황에서는 그림자 소모 공격 우선
        if health_ratio < 0.3 or threat_level == 'CRITICAL':
            if shadow_count >= 3:
                analysis['optimal_shadow_use'] = True
                analysis['should_consume_shadows'] = True
                analysis['shadow_priority'] = 0.9
            elif shadow_count >= 1:
                analysis['should_consume_shadows'] = True
                analysis['shadow_priority'] = 0.7
        
        # 적이 많을 때는 그림자 축적 우선
        elif enemy_count >= 3 and shadow_count < 5:
            analysis['should_generate_shadows'] = True
            analysis['shadow_priority'] = 0.6
        
        # 적이 적고 그림자가 많을 때는 소모 공격
        elif enemy_count <= 2 and shadow_count >= 3:
            analysis['should_consume_shadows'] = True
            analysis['shadow_priority'] = 0.8
        
        # 그림자가 없을 때는 생성 우선
        elif shadow_count == 0:
            analysis['should_generate_shadows'] = True
            analysis['shadow_priority'] = 0.9
        
        return analysis

    def _analyze_druid_nature_gauge(self, character, enemies: List) -> Dict:
        """드루이드 자연 게이지 분석"""
        analysis = {}
        
        # 자연 친화도 스택과 야생 게이지 확인
        nature_stacks = getattr(character, 'nature_stacks', 0)
        wild_gauge = getattr(character, 'wild_gauge', 0)
        hp_ratio = character.current_hp / character.max_hp
        
        # HP가 낮으면 자연 회복 우선
        if hp_ratio < 0.4:
            analysis['prioritize_nature_healing'] = True
            analysis['nature_priority'] = 0.9
        
        # 자연 스택이 높으면 강력한 자연 스킬 사용
        elif nature_stacks >= 7:
            analysis['use_nature_ultimate'] = True
            analysis['nature_priority'] = 0.8
        
        # 야생 게이지가 높으면 변신 스킬 우선
        elif wild_gauge >= 80:
            analysis['should_transform'] = True
            analysis['wild_priority'] = 0.85
        
        # 적이 많을 때는 자연 스택 축적
        enemy_count = len([e for e in enemies if e.is_alive])
        if enemy_count >= 3 and nature_stacks < 5:
            analysis['build_nature_stacks'] = True
            analysis['nature_priority'] = 0.6
        
        return analysis

    def _analyze_priest_atonement_system(self, character, party_members: List) -> Dict:
        """신관 속죄 시스템 분석"""
        analysis = {}
        
        # 속죄 스택과 신성 에너지 확인
        atonement_stacks = getattr(character, 'atonement_stacks', 0)
        divine_energy = getattr(character, 'divine_energy', 0)
        
        # 아군 HP 상태 확인
        injured_allies = [ally for ally in party_members if ally.is_alive and ally.current_hp / ally.max_hp < 0.6]
        critically_injured = [ally for ally in party_members if ally.is_alive and ally.current_hp / ally.max_hp < 0.3]
        
        # 심각한 부상자가 있으면 즉시 치유
        if critically_injured:
            analysis['emergency_heal'] = True
            analysis['heal_priority'] = 1.0
        
        # 속죄 스택이 높고 신성 에너지가 충분하면 대규모 치유
        elif atonement_stacks >= 6 and divine_energy >= 80:
            analysis['mass_divine_heal'] = True
            analysis['divine_priority'] = 0.9
        
        # 부상자가 많으면 속죄 스택 활용한 광역 치유
        elif len(injured_allies) >= 2 and atonement_stacks >= 4:
            analysis['atonement_heal'] = True
            analysis['heal_priority'] = 0.8
        
        # 스택이 부족하면 축적 우선
        elif atonement_stacks < 3:
            analysis['build_atonement'] = True
            analysis['stack_priority'] = 0.7
        
        return analysis

    def _analyze_mystic_sword_elemental_harmony(self, character, enemies: List) -> Dict:
        """마검사 원소 조화 분석"""
        analysis = {}
        
        # 원소 조화 스택과 임시 원소 확인
        harmony_stacks = getattr(character, 'elemental_harmony', 0)
        temp_element = getattr(character, 'temp_element', None)
        
        enemy_count = len([e for e in enemies if e.is_alive])
        
        # 원소 조화 스택이 최대치면 폭발 스킬 사용
        if harmony_stacks >= 6:
            analysis['elemental_explosion'] = True
            analysis['explosion_priority'] = 0.9
        
        # 적이 많고 조화 스택이 충분하면 광역 원소 공격
        elif enemy_count >= 3 and harmony_stacks >= 4:
            analysis['area_elemental_attack'] = True
            analysis['elemental_priority'] = 0.8
        
        # 임시 원소가 있으면 해당 원소 특화 스킬 우선
        elif temp_element:
            analysis['use_elemental_skill'] = True
            analysis['element_type'] = temp_element
            analysis['elemental_priority'] = 0.7
        
        # 조화 스택이 낮으면 축적 우선
        elif harmony_stacks < 3:
            analysis['build_harmony'] = True
            analysis['harmony_priority'] = 0.6
        
        return analysis

    def _analyze_monk_chi_balance(self, character, party_members: List, enemies: List) -> Dict:
        """몽크 기공 밸런스 분석"""
        analysis = {}
        
        # 기공 에너지와 콤보 카운트 확인
        chi_energy = getattr(character, 'chi_energy', 0)
        combo_count = getattr(character, 'combo_count', 0)
        hp_ratio = character.current_hp / character.max_hp
        
        # HP가 낮으면 기공 회복 우선
        if hp_ratio < 0.5:
            analysis['chi_healing'] = True
            analysis['heal_priority'] = 0.8
        
        # 콤보 카운트가 높으면 피니시 기술
        elif combo_count >= 4:
            analysis['combo_finisher'] = True
            analysis['combo_priority'] = 0.9
        
        # 기공 에너지가 충분하면 강화 기술
        elif chi_energy >= 80:
            analysis['chi_enhanced_attack'] = True
            analysis['chi_priority'] = 0.8
        
        # 적이 많으면 연속 공격으로 콤보 축적
        enemy_count = len([e for e in enemies if e.is_alive])
        if enemy_count >= 2 and combo_count < 3:
            analysis['build_combo'] = True
            analysis['combo_priority'] = 0.6
        
        # 기공 에너지가 부족하면 순환 기술
        elif chi_energy < 30:
            analysis['chi_circulation'] = True
            analysis['chi_priority'] = 0.7
        
        return analysis

    def _analyze_necromancer_soul_management(self, character, enemies: List) -> Dict:
        """네크로맨서 영혼 관리 분석"""
        analysis = {}
        
        # 영혼 에너지와 언데드 상태 확인
        soul_energy = getattr(character, 'soul_energy', 0)
        has_undead = getattr(character, 'undead_minions', 0) > 0
        
        enemy_count = len([e for e in enemies if e.is_alive])
        weak_enemies = [e for e in enemies if e.is_alive and e.current_hp / e.max_hp < 0.3]
        
        # 약한 적이 있으면 영혼 수확 우선
        if weak_enemies and soul_energy < 80:
            analysis['soul_harvest_target'] = True
            analysis['harvest_priority'] = 0.9
        
        # 영혼 에너지가 충분하면 언데드 소환
        elif soul_energy >= 70 and not has_undead:
            analysis['summon_undead'] = True
            analysis['summon_priority'] = 0.8
        
        # 적이 많고 언데드가 있으면 강화
        elif enemy_count >= 3 and has_undead:
            analysis['enhance_undead'] = True
            analysis['undead_priority'] = 0.7
        
        # 영혼 에너지가 부족하면 흡수 우선
        elif soul_energy < 30:
            analysis['life_drain_focus'] = True
            analysis['drain_priority'] = 0.8
        
        return analysis

    def _analyze_samurai_willpower_system(self, character, enemies: List) -> Dict:
        """사무라이 의지 시스템 분석"""
        analysis = {}
        
        # 의지 게이지 확인
        willpower = getattr(character, 'willpower_gauge', 0)
        
        enemy_count = len([e for e in enemies if e.is_alive])
        strong_enemies = [e for e in enemies if e.is_alive and e.current_hp / e.max_hp > 0.8]
        
        # 의지 게이지가 최대치면 거합 일격
        if willpower >= 100:
            analysis['iai_strike'] = True
            analysis['iai_priority'] = 1.0
        
        # 강한 적이 있고 의지가 충분하면 무사도 정신
        elif strong_enemies and willpower >= 80:
            analysis['bushido_spirit'] = True
            analysis['bushido_priority'] = 0.9
        
        # 적이 많고 의지가 중간 정도면 연속 베기
        elif enemy_count >= 3 and willpower >= 50:
            analysis['continuous_slash'] = True
            analysis['slash_priority'] = 0.8
        
        # 의지가 부족하면 축적 우선
        elif willpower < 40:
            analysis['build_willpower'] = True
            analysis['willpower_priority'] = 0.7
        
        return analysis


# 전역 파티 AI
party_ai_assistant = create_party_ai()
