#!/usr/bin/env python3
"""
고급 게임 밸런스 시스템
동적 난이도 조절, 적응형 리워드, 플레이어 진행도 분석
"""

import json
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DifficultyLevel(Enum):
    """난이도 레벨"""
    VERY_EASY = 0.5
    EASY = 0.7
    NORMAL = 1.0
    HARD = 1.3
    VERY_HARD = 1.6
    NIGHTMARE = 2.0


class PlayerSkillLevel(Enum):
    """플레이어 스킬 레벨"""
    BEGINNER = "beginner"
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class GameMetrics:
    """게임 메트릭스"""
    battles_won: int = 0
    battles_lost: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    healing_used: int = 0
    items_used: int = 0
    time_played: float = 0.0
    deaths: int = 0
    levels_gained: int = 0
    gold_earned: int = 0
    perfect_battles: int = 0  # 무상 승리
    close_calls: int = 0      # 간발의 승리 (HP 20% 이하)


@dataclass
class BalanceModifier:
    """밸런스 수정자"""
    enemy_health_multiplier: float = 1.0
    enemy_damage_multiplier: float = 1.0
    exp_multiplier: float = 1.0
    gold_multiplier: float = 1.0
    item_drop_rate_multiplier: float = 1.0
    healing_effectiveness: float = 1.0
    mp_regeneration_rate: float = 1.0


class AdaptiveBalanceSystem:
    """적응형 밸런스 시스템"""
    
    def __init__(self):
        self.metrics = GameMetrics()
        self.current_difficulty = DifficultyLevel.NORMAL
        self.base_modifiers = BalanceModifier()
        self.dynamic_modifiers = BalanceModifier()
        
        # 분석 데이터
        self.recent_performance = []  # 최근 전투 결과
        self.struggle_points = []     # 어려움을 겪은 지점들
        self.mastery_indicators = []  # 숙련도 지표
        
        # 설정
        self.adaptation_sensitivity = 0.1  # 적응 민감도
        self.max_adjustment = 0.5         # 최대 조정 폭
        self.analysis_window = 10         # 분석 윈도우 (최근 N번의 전투)
        
    def start_session(self, debug_mode=False):
        """새로운 게임 세션 시작 - 세션별 데이터 초기화"""
        if debug_mode:
            print("🎯 적응형 밸런스 시스템 세션 시작")
        
        # 세션별 메트릭 초기화 (전체 데이터는 유지)
        self.recent_performance = []
        self.struggle_points = []
        self.mastery_indicators = []
        
        # 현재 난이도 표시
        if debug_mode:
            print(f"   현재 난이도: {self.current_difficulty.value}")
            print(f"   적응 민감도: {self.adaptation_sensitivity:.1%}")
        
        # 기존 데이터가 있다면 로드
        try:
            self.load_balance_data(debug_mode=debug_mode)
        except:
            pass  # 첫 실행시에는 파일이 없을 수 있음
        
    def update(self, dt: float):
        """프레임마다 호출되는 업데이트 메서드"""
        # 현재는 특별한 프레임별 업데이트가 필요하지 않음
        # 필요시 실시간 분석이나 적응형 조정을 여기서 수행
        pass
        
    def record_battle_result(self, won: bool, player_hp_remaining: float, 
                           battle_duration: float, damage_dealt: int, 
                           damage_taken: int, items_used: int):
        """전투 결과 기록"""
        self.metrics.battles_won += 1 if won else 0
        self.metrics.battles_lost += 0 if won else 1
        self.metrics.total_damage_dealt += damage_dealt
        self.metrics.total_damage_taken += damage_taken
        self.metrics.items_used += items_used
        
        # 성과 분석
        performance_score = self._calculate_performance_score(
            won, player_hp_remaining, battle_duration, damage_dealt, damage_taken
        )
        
        self.recent_performance.append({
            'won': won,
            'score': performance_score,
            'hp_remaining': player_hp_remaining,
            'duration': battle_duration,
            'timestamp': time.time()
        })
        
        # 특별한 상황 기록
        if won and player_hp_remaining > 0.8:
            self.metrics.perfect_battles += 1
        elif won and player_hp_remaining < 0.2:
            self.metrics.close_calls += 1
        
        # 분석 윈도우 크기 유지
        if len(self.recent_performance) > self.analysis_window:
            self.recent_performance.pop(0)
        
        # 동적 조정 수행
        self._adjust_difficulty()
        
    def record_combat_event(self, event_type: str, data: dict):
        """전투 이벤트 기록 (통합 게임 매니저용)"""
        try:
            if event_type == "enemy_defeated":
                # 적 처치 이벤트
                damage_dealt = data.get('damage_dealt', 0)
                battle_duration = data.get('duration', 30.0)
                
                # 메트릭스 업데이트
                self.metrics.total_damage_dealt += damage_dealt
                
            elif event_type == "battle_won":
                # 전투 승리
                hp_remaining = data.get('hp_remaining', 1.0)
                duration = data.get('duration', 30.0)
                damage_dealt = data.get('damage_dealt', 0)
                damage_taken = data.get('damage_taken', 0)
                items_used = data.get('items_used', 0)
                
                self.record_battle_result(True, hp_remaining, duration, 
                                        damage_dealt, damage_taken, items_used)
                
            elif event_type == "battle_lost":
                # 전투 패배
                hp_remaining = data.get('hp_remaining', 0.0)
                duration = data.get('duration', 30.0)
                damage_dealt = data.get('damage_dealt', 0)
                damage_taken = data.get('damage_taken', 0)
                items_used = data.get('items_used', 0)
                
                self.record_battle_result(False, hp_remaining, duration, 
                                        damage_dealt, damage_taken, items_used)
                
            elif event_type == "player_damaged":
                # 플레이어 피해
                damage = data.get('damage', 0)
                self.metrics.total_damage_taken += damage
                
            elif event_type == "item_used":
                # 아이템 사용
                self.metrics.items_used += 1
                
        except Exception as e:
            # 밸런스 시스템 오류가 게임을 중단시키지 않도록
            print(f"밸런스 시스템 이벤트 처리 오류: {e}")
            pass
    
    def _calculate_performance_score(self, won: bool, hp_remaining: float,
                                   duration: float, damage_dealt: int, damage_taken: int) -> float:
        """성과 점수 계산"""
        base_score = 50.0  # 기본 점수
        
        if won:
            base_score += 30.0
            base_score += hp_remaining * 20.0  # HP 잔여량 보너스
            
            # 효율성 보너스 (빠른 승리)
            if duration < 30.0:
                base_score += 10.0
            elif duration > 120.0:
                base_score -= 5.0
                
            # 데미지 효율성
            if damage_taken > 0:
                damage_ratio = damage_dealt / damage_taken
                base_score += min(damage_ratio * 5.0, 15.0)
        else:
            base_score -= 20.0
            # 패배해도 선전했다면 점수 보정
            if hp_remaining > 0:  # 동료가 살아있음
                base_score += hp_remaining * 10.0
        
        return max(0.0, min(100.0, base_score))
    
    def _adjust_difficulty(self):
        """난이도 동적 조정"""
        if len(self.recent_performance) < 3:
            return
        
        # 최근 성과 분석
        recent_scores = [p['score'] for p in self.recent_performance[-5:]]
        recent_wins = [p['won'] for p in self.recent_performance[-5:]]
        
        avg_score = sum(recent_scores) / len(recent_scores)
        win_rate = sum(recent_wins) / len(recent_wins)
        
        # 조정 필요성 판단
        adjustment_needed = 0.0
        
        # 승률 기반 조정 (더 민감하게)
        if win_rate > 0.7:  # 70% 이상 승률이면 어렵게 (80%에서 낮춤)
            adjustment_needed -= 0.15  # 더 강한 조정
        elif win_rate < 0.5:  # 50% 미만 승률이면 쉽게 (40%에서 높임)
            adjustment_needed += 0.12  # 더 강한 조정
        
        # 성과 점수 기반 조정 (더 민감하게)
        if avg_score > 70.0:  # 우수한 성과 (75에서 낮춤)
            adjustment_needed -= 0.08
        elif avg_score < 45.0:  # 저조한 성과 (40에서 높임)
            adjustment_needed += 0.08
        
        # 연속 패배 체크 (더 빨리 반응)
        recent_5 = self.recent_performance[-3:]  # 최근 3전만 체크
        if len(recent_5) >= 2 and not any(p['won'] for p in recent_5[-2:]):  # 2연패
            adjustment_needed += 0.2  # 연속 패배 시 크게 쉽게
        
        # 연속 완승 체크 (더 빨리 반응)
        if len(recent_5) >= 2 and all(p['won'] and p['hp_remaining'] > 0.7 for p in recent_5[-2:]):  # 2연속 완승
            adjustment_needed -= 0.15  # 연속 완승 시 어렵게
        
        # 조정 적용
        if abs(adjustment_needed) > 0.02:  # 최소 임계값
            self._apply_balance_adjustment(adjustment_needed)
    
    def _apply_balance_adjustment(self, adjustment: float):
        """밸런스 조정 적용"""
        # 조정 폭 제한
        adjustment = max(-self.max_adjustment, min(self.max_adjustment, adjustment))
        
        # 현재 수정자에 조정 적용
        if adjustment < 0:  # 쉽게 만들기
            self.dynamic_modifiers.enemy_health_multiplier *= (1 + adjustment)
            self.dynamic_modifiers.enemy_damage_multiplier *= (1 + adjustment)
            self.dynamic_modifiers.exp_multiplier *= (1 - adjustment * 0.5)
            self.dynamic_modifiers.gold_multiplier *= (1 - adjustment * 0.5)
        else:  # 어렵게 만들기
            self.dynamic_modifiers.enemy_health_multiplier *= (1 + adjustment)
            self.dynamic_modifiers.enemy_damage_multiplier *= (1 + adjustment)
            self.dynamic_modifiers.exp_multiplier *= (1 - adjustment * 0.3)
        
        # 범위 제한
        self.dynamic_modifiers.enemy_health_multiplier = max(0.5, min(2.0, self.dynamic_modifiers.enemy_health_multiplier))
        self.dynamic_modifiers.enemy_damage_multiplier = max(0.5, min(2.0, self.dynamic_modifiers.enemy_damage_multiplier))
        self.dynamic_modifiers.exp_multiplier = max(0.7, min(1.5, self.dynamic_modifiers.exp_multiplier))
        
        print(f"🎯 난이도 자동 조정: {'쉬워짐' if adjustment < 0 else '어려워짐'} ({adjustment:.2f})")
    
    def get_player_skill_level(self) -> PlayerSkillLevel:
        """플레이어 스킬 레벨 판정"""
        if len(self.recent_performance) < 5:
            return PlayerSkillLevel.BEGINNER
        
        avg_score = sum(p['score'] for p in self.recent_performance) / len(self.recent_performance)
        win_rate = sum(p['won'] for p in self.recent_performance) / len(self.recent_performance)
        perfect_rate = self.metrics.perfect_battles / max(1, self.metrics.battles_won)
        
        # 복합 지표로 스킬 레벨 판정
        if avg_score >= 80 and win_rate >= 0.9 and perfect_rate >= 0.5:
            return PlayerSkillLevel.EXPERT
        elif avg_score >= 70 and win_rate >= 0.8:
            return PlayerSkillLevel.ADVANCED
        elif avg_score >= 60 and win_rate >= 0.6:
            return PlayerSkillLevel.INTERMEDIATE
        elif avg_score >= 45 and win_rate >= 0.4:
            return PlayerSkillLevel.NOVICE
        else:
            return PlayerSkillLevel.BEGINNER
    
    def get_adaptive_rewards(self, base_exp: int, base_gold: int) -> Tuple[int, int]:
        """적응형 보상 계산"""
        exp_modifier = self.dynamic_modifiers.exp_multiplier
        gold_modifier = self.dynamic_modifiers.gold_multiplier
        
        # 스킬 레벨에 따른 추가 보정
        skill_level = self.get_player_skill_level()
        if skill_level == PlayerSkillLevel.BEGINNER:
            exp_modifier *= 1.2  # 초보자 보너스
            gold_modifier *= 1.1
        elif skill_level == PlayerSkillLevel.EXPERT:
            exp_modifier *= 0.9  # 전문가는 보상 감소
        
        return int(base_exp * exp_modifier), int(base_gold * gold_modifier)
    
    def get_enemy_modifiers(self) -> BalanceModifier:
        """적 수정자 반환"""
        return self.dynamic_modifiers
    
    def get_loot_modifier(self) -> float:
        """전리품 수정자 반환"""
        # 플레이어 스킬 레벨에 따른 전리품 조정
        skill_level = self.get_player_skill_level()
        base_modifier = 1.0
        
        if skill_level == PlayerSkillLevel.BEGINNER:
            return base_modifier * 1.3  # 초보자 보너스
        elif skill_level == PlayerSkillLevel.NOVICE:
            return base_modifier * 1.1
        elif skill_level == PlayerSkillLevel.EXPERT:
            return base_modifier * 0.9  # 전문가는 감소
        else:
            return base_modifier
    
    def get_difficulty_description(self) -> str:
        """현재 난이도 설명"""
        health_mod = self.dynamic_modifiers.enemy_health_multiplier
        damage_mod = self.dynamic_modifiers.enemy_damage_multiplier
        
        if health_mod <= 0.7 and damage_mod <= 0.7:
            return "🟢 매우 쉬움 (적응형 조정)"
        elif health_mod <= 0.85 and damage_mod <= 0.85:
            return "🔵 쉬움 (적응형 조정)"
        elif health_mod <= 1.15 and damage_mod <= 1.15:
            return "🟡 보통"
        elif health_mod <= 1.4 and damage_mod <= 1.4:
            return "🟠 어려움 (적응형 조정)"
        else:
            return "🔴 매우 어려움 (적응형 조정)"
    
    def get_performance_summary(self) -> Dict:
        """성과 요약 반환"""
        total_battles = self.metrics.battles_won + self.metrics.battles_lost
        win_rate = self.metrics.battles_won / max(1, total_battles)
        
        return {
            'total_battles': total_battles,
            'win_rate': win_rate,
            'skill_level': self.get_player_skill_level().value,
            'difficulty': self.get_difficulty_description(),
            'perfect_battles': self.metrics.perfect_battles,
            'close_calls': self.metrics.close_calls,
            'average_recent_score': sum(p['score'] for p in self.recent_performance[-5:]) / max(1, len(self.recent_performance[-5:]))
        }
    
    def save_balance_data(self, filename: str = "balance_data.json"):
        """밸런스 데이터 저장"""
        data = {
            'metrics': self.metrics.__dict__,
            'modifiers': self.dynamic_modifiers.__dict__,
            'recent_performance': self.recent_performance,
            'current_difficulty': self.current_difficulty.value
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"밸런스 데이터 저장 실패: {e}")
    
    def load_balance_data(self, filename: str = "balance_data.json", debug_mode: bool = False):
        """밸런스 데이터 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 메트릭스 복원
            for key, value in data.get('metrics', {}).items():
                if hasattr(self.metrics, key):
                    setattr(self.metrics, key, value)
            
            # 수정자 복원
            for key, value in data.get('modifiers', {}).items():
                if hasattr(self.dynamic_modifiers, key):
                    setattr(self.dynamic_modifiers, key, value)
            
            # 최근 성과 복원
            self.recent_performance = data.get('recent_performance', [])
            
            if debug_mode:
                print("✅ 밸런스 데이터 로드 완료")
            
        except FileNotFoundError:
            if debug_mode:
                print("🔵 새로운 밸런스 데이터 시작")
        except Exception as e:
            if debug_mode:
                print(f"❌ 밸런스 데이터 로드 실패: {e}")


# 전역 적응형 밸런스 시스템
adaptive_balance = AdaptiveBalanceSystem()


def record_combat_result(won: bool, player_hp_remaining: float, battle_duration: float,
                        damage_dealt: int, damage_taken: int, items_used: int = 0):
    """전투 결과 기록 (편의 함수)"""
    adaptive_balance.record_battle_result(
        won, player_hp_remaining, battle_duration, 
        damage_dealt, damage_taken, items_used
    )


def get_balanced_enemy_stats(base_hp: int, base_attack: int) -> Tuple[int, int]:
    """밸런스가 적용된 적 스탯"""
    modifiers = adaptive_balance.get_enemy_modifiers()
    
    balanced_hp = int(base_hp * modifiers.enemy_health_multiplier)
    balanced_attack = int(base_attack * modifiers.enemy_damage_multiplier)
    
    return balanced_hp, balanced_attack


def get_balanced_rewards(base_exp: int, base_gold: int) -> Tuple[int, int]:
    """밸런스가 적용된 보상"""
    return adaptive_balance.get_adaptive_rewards(base_exp, base_gold)
