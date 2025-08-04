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
        """행동 선택 - BRV/HP 전략 적용"""
        self.turn_count += 1
        
        # 상황 분석
        situation = self._analyze_situation(character, allies, enemies, battlefield_state)
        
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
        """스킬 옵션 생성 - BRV/HP 공격 시스템과 상태이상 통합"""
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
                'description': '🌙 그림자 습격 - 순간이동 후 치명타 + 공포'
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


# 전역 파티 AI
party_ai_assistant = create_party_ai()
