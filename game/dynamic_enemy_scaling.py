#!/usr/bin/env python3
"""
동적 적 스케일링 시스템
파티 강화에 맞춰 적도 동적으로 강화되는 시스템
"""

from typing import List, Dict, Any, Optional, Tuple
import random
import math
from game.character import Character

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BRIGHT_YELLOW = '\033[93m\033[1m'
BRIGHT_RED = '\033[91m\033[1m'
BRIGHT_CYAN = '\033[96m\033[1m'

class PartyPowerAnalyzer:
    """파티 전력 분석 시스템"""
    
    def __init__(self):
        self.base_power = 1000  # 기준 전력값
    
    def analyze_party_power(self, party: List[Character]) -> Dict[str, Any]:
        """파티의 전체적인 전력을 분석"""
        if not party:
            return {"total_power": self.base_power, "scaling_factor": 1.0}
        
        total_power = 0
        analysis = {
            "stat_power": 0,
            "trait_power": 0,
            "synergy_power": 0,
            "balance_power": 0,
            "level_power": 0
        }
        
        # 1. 기본 스탯 전력 계산
        for char in party:
            stat_power = (
                char.max_hp * 0.5 +
                char.physical_attack * 1.5 +
                char.magic_attack * 1.5 +
                char.physical_defense * 1.0 +
                char.magic_defense * 1.0 +
                char.speed * 2.0 +
                char.level * 10
            )
            analysis["stat_power"] += stat_power
        
        # 2. 특성 전력 계산
        trait_count = 0
        for char in party:
            if hasattr(char, 'traits') and char.traits:
                trait_count += len(char.traits)
            elif hasattr(char, 'selected_traits') and char.selected_traits:
                trait_count += len(char.selected_traits)
        
        analysis["trait_power"] = trait_count * 150  # 특성당 150 전력
        
        # 3. 레벨 전력 계산
        total_level = sum(char.level for char in party)
        analysis["level_power"] = total_level * 25
        
        # 4. 파티 밸런스 보너스
        balance_bonus = self._calculate_balance_bonus(party)
        analysis["balance_power"] = balance_bonus
        
        # 5. 시너지 보너스 (직업 조합)
        synergy_bonus = self._calculate_synergy_bonus(party)
        analysis["synergy_power"] = synergy_bonus
        
        # 총 전력 계산
        total_power = sum(analysis.values())
        scaling_factor = max(1.0, total_power / self.base_power)
        
        return {
            "total_power": total_power,
            "scaling_factor": scaling_factor,
            "analysis": analysis,
            "difficulty_level": self._get_difficulty_level(scaling_factor)
        }
    
    def _calculate_balance_bonus(self, party: List[Character]) -> float:
        """파티 밸런스에 따른 보너스 계산"""
        if len(party) < 2:
            return 0
        
        roles = {"tank": 0, "dps": 0, "mage": 0, "support": 0}
        
        tank_jobs = ["전사", "성기사", "기사"]
        dps_jobs = ["궁수", "도적", "암살자", "검성", "검투사", "광전사", "사무라이"]
        mage_jobs = ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사", "마검사"]
        support_jobs = ["바드", "신관", "드루이드", "무당", "철학자"]
        
        for char in party:
            job = char.character_class
            if job in tank_jobs:
                roles["tank"] += 1
            elif job in dps_jobs:
                roles["dps"] += 1
            elif job in mage_jobs:
                roles["mage"] += 1
            elif job in support_jobs:
                roles["support"] += 1
        
        # 역할 다양성에 따른 보너스
        unique_roles = sum(1 for count in roles.values() if count > 0)
        balance_bonus = unique_roles * 100  # 역할당 100 보너스
        
        # 완벽한 밸런스 보너스 (4가지 역할 모두 있으면)
        if unique_roles == 4:
            balance_bonus += 200
        
        return balance_bonus
    
    def _calculate_synergy_bonus(self, party: List[Character]) -> float:
        """직업 시너지에 따른 보너스 계산"""
        synergy_combinations = {
            ("성기사", "신관"): 150,
            ("암흑기사", "네크로맨서"): 150,
            ("궁수", "사무라이"): 120,
            ("바드", "아크메이지"): 130,
            ("드루이드", "정령술사"): 140,
            ("검성", "검투사"): 160,
            ("광전사", "암흑기사"): 170,
            ("기사", "성기사"): 140,
            ("용기사", "아크메이지"): 150,
        }
        
        jobs = [char.character_class for char in party]
        synergy_bonus = 0
        
        for (job1, job2), bonus in synergy_combinations.items():
            if job1 in jobs and job2 in jobs:
                synergy_bonus += bonus
        
        return synergy_bonus
    
    def _get_difficulty_level(self, scaling_factor: float) -> str:
        """스케일링 팩터에 따른 난이도 레벨"""
        if scaling_factor < 1.2:
            return "쉬움"
        elif scaling_factor < 1.5:
            return "보통"
        elif scaling_factor < 2.0:
            return "어려움"
        elif scaling_factor < 2.5:
            return "매우 어려움"
        elif scaling_factor < 3.0:
            return "지옥"
        else:
            return "불가능"

class DynamicEnemyScaler:
    """동적 적 스케일링 시스템"""
    
    def __init__(self):
        self.power_analyzer = PartyPowerAnalyzer()
        self.last_analysis = None
    
    def scale_enemy(self, enemy: Character, party: List[Character], floor: int) -> Character:
        """파티 전력에 맞춰 적을 스케일링"""
        
        # 파티 전력 분석
        if not self.last_analysis:
            self.last_analysis = self.power_analyzer.analyze_party_power(party)
        
        scaling_factor = self.last_analysis["scaling_factor"]
        
        # 게임의 기본 난이도 설정 고려
        difficulty_modifier = self._get_game_difficulty_modifier()
        
        # 기본 스케일링 (층수 기반)
        floor_scaling = 1.0 + (floor - 1) * 0.1
        
        # 최종 스케일링 팩터 (게임 난이도 포함)
        final_scaling = scaling_factor * floor_scaling * difficulty_modifier
        
        # 적 스탯 강화
        scaled_enemy = self._apply_scaling(enemy, final_scaling, floor)
        
        # 특수 강화 적용
        scaled_enemy = self._apply_special_enhancements(scaled_enemy, self.last_analysis, floor)
        
        return scaled_enemy
    
    def _get_game_difficulty_modifier(self) -> float:
        """게임의 기본 난이도 설정에 따른 수정자"""
        try:
            from config import game_config
            if hasattr(game_config, 'current_difficulty'):
                difficulty = game_config.current_difficulty
            else:
                return 1.0
        except:
            return 1.0
        
        # 난이도별 수정자
        difficulty_modifiers = {
            "쉬움": 0.8,
            "보통": 1.0, 
            "어려움": 1.3,
            "지옥": 1.6
        }
        
        return difficulty_modifiers.get(difficulty, 1.0)
    
    def _apply_scaling(self, enemy: Character, scaling_factor: float, floor: int) -> Character:
        """기본 스케일링 적용"""
        # 스탯 스케일링
        enemy.max_hp = int(enemy.max_hp * scaling_factor)
        enemy.hp = enemy.max_hp
        enemy.physical_attack = int(enemy.physical_attack * scaling_factor)
        enemy.magic_attack = int(enemy.magic_attack * scaling_factor)
        enemy.physical_defense = int(enemy.physical_defense * scaling_factor * 0.8)  # 방어력은 조금 덜 올림
        enemy.magic_defense = int(enemy.magic_defense * scaling_factor * 0.8)
        enemy.speed = int(enemy.speed * min(scaling_factor, 1.5))  # 속도는 최대 1.5배까지만
        
        # 레벨 조정
        enemy.level = max(1, int(floor + scaling_factor - 1))
        
        return enemy
    
    def _apply_special_enhancements(self, enemy: Character, analysis: Dict[str, Any], floor: int) -> Character:
        """특수 강화 효과 적용"""
        scaling_factor = analysis["scaling_factor"]
        
        # 1. 고전력 파티에 대한 특수 대응
        if scaling_factor > 2.0:
            enemy = self._apply_elite_enhancements(enemy)
        
        # 2. 특성 대응 강화
        if analysis["analysis"]["trait_power"] > 300:
            enemy = self._apply_trait_counter_enhancements(enemy)
        
        # 3. 밸런스 대응 강화
        if analysis["analysis"]["balance_power"] > 400:
            enemy = self._apply_balance_counter_enhancements(enemy)
        
        # 4. 층수별 특수 강화
        if floor % 5 == 0:  # 5층마다 보스급 강화
            enemy = self._apply_boss_enhancements(enemy, floor)
        
        return enemy
    
    def _apply_elite_enhancements(self, enemy: Character) -> Character:
        """엘리트 강화 적용"""
        enemy.name = f"🔥 정예 {enemy.name}"
        
        # 추가 스탯 보너스
        enemy.max_hp = int(enemy.max_hp * 1.3)
        enemy.hp = enemy.max_hp
        enemy.physical_attack = int(enemy.physical_attack * 1.2)
        enemy.magic_attack = int(enemy.magic_attack * 1.2)
        
        # 특수 능력 부여 (실제 구현 시 스킬 시스템과 연동)
        if not hasattr(enemy, 'special_abilities'):
            enemy.special_abilities = []
        
        enemy.special_abilities.extend([
            "재생능력",  # 턴마다 HP 회복
            "반격",      # 공격받을 때 반격
            "강화갑주"   # 물리 데미지 감소
        ])
        
        return enemy
    
    def _apply_trait_counter_enhancements(self, enemy: Character) -> Character:
        """특성 대응 강화"""
        enemy.name = f"🎯 특성파괴자 {enemy.name}"
        
        if not hasattr(enemy, 'special_abilities'):
            enemy.special_abilities = []
        
        enemy.special_abilities.extend([
            "특성무효화",  # 특성 효과 50% 감소
            "적응진화",    # 받은 피해 타입에 저항 증가
            "분석능력"     # 아군 특성 정보 습득
        ])
        
        return enemy
    
    def _apply_balance_counter_enhancements(self, enemy: Character) -> Character:
        """밸런스 대응 강화"""
        enemy.name = f"⚖️ 균형파괴자 {enemy.name}"
        
        # 다양한 공격 패턴 부여
        if not hasattr(enemy, 'attack_patterns'):
            enemy.attack_patterns = []
        
        enemy.attack_patterns.extend([
            "탱커킬러",    # 방어 무시 공격
            "딜러헌터",    # 딜러 우선 타겟팅
            "메이지베인",  # 마법 저항 및 침묵
            "서포터스나이퍼"  # 지원 캐릭터 집중 공격
        ])
        
        return enemy
    
    def _apply_boss_enhancements(self, enemy: Character, floor: int) -> Character:
        """보스급 강화"""
        boss_tier = floor // 5
        enemy.name = f"👑 {boss_tier}급 보스 {enemy.name}"
        
        # 보스급 스탯 보너스
        boss_multiplier = 1.0 + (boss_tier * 0.5)
        enemy.max_hp = int(enemy.max_hp * boss_multiplier)
        enemy.hp = enemy.max_hp
        enemy.physical_attack = int(enemy.physical_attack * boss_multiplier)
        enemy.magic_attack = int(enemy.magic_attack * boss_multiplier)
        
        # 보스 전용 능력
        if not hasattr(enemy, 'boss_abilities'):
            enemy.boss_abilities = []
        
        boss_abilities = [
            "광역공격",
            "즉사공격",
            "상태이상무효",
            "패턴변화",
            "분노모드"
        ]
        
        # 보스 티어에 따라 능력 추가
        enemy.boss_abilities = boss_abilities[:min(boss_tier + 1, len(boss_abilities))]
        
        return enemy
    
    def update_party_analysis(self, party: List[Character]):
        """파티 분석 업데이트"""
        self.last_analysis = self.power_analyzer.analyze_party_power(party)
    
    def get_current_difficulty_info(self) -> Dict[str, Any]:
        """현재 난이도 정보 반환"""
        if not self.last_analysis:
            return {"difficulty": "알 수 없음", "scaling_factor": 1.0}
        
        return {
            "difficulty": self.last_analysis["difficulty_level"],
            "scaling_factor": self.last_analysis["scaling_factor"],
            "analysis": self.last_analysis["analysis"]
        }
    
    def display_difficulty_info(self):
        """현재 난이도 정보 표시"""
        if not self.last_analysis:
            print(f"{YELLOW}⚠️ 파티 분석이 필요합니다.{RESET}")
            return
        
        info = self.last_analysis
        difficulty = info["difficulty_level"]
        scaling = info["scaling_factor"]
        
        # 게임 기본 난이도 가져오기
        game_difficulty = self._get_game_difficulty_name()
        difficulty_modifier = self._get_game_difficulty_modifier()
        
        # 난이도별 색상
        difficulty_colors = {
            "쉬움": GREEN,
            "보통": YELLOW,
            "어려움": YELLOW,
            "매우 어려움": RED,
            "지옥": BRIGHT_RED,
            "불가능": BRIGHT_RED + BOLD
        }
        
        color = difficulty_colors.get(difficulty, WHITE)
        
        print(f"\n{CYAN}═══════════════════════════════════════════════════════════{RESET}")
        print(f"{BRIGHT_YELLOW}🎯 현재 게임 난이도 정보{RESET}")
        print(f"{CYAN}═══════════════════════════════════════════════════════════{RESET}")
        print(f"{WHITE}� 게임 기본 난이도: {BRIGHT_CYAN}{game_difficulty}{RESET} (×{difficulty_modifier:.1f})")
        print(f"{WHITE}�🏆 파티 전력: {int(info['total_power'])}{RESET}")
        print(f"{WHITE}📊 스케일링: {scaling:.2f}배{RESET}")
        print(f"{WHITE}⚡ 최종 난이도: {color}{difficulty}{RESET}")
        
        analysis = info["analysis"]
        print(f"\n{MAGENTA}📋 상세 분석:{RESET}")
        print(f"  {CYAN}• 스탯 전력: {int(analysis['stat_power'])}{RESET}")
        print(f"  {CYAN}• 특성 전력: {int(analysis['trait_power'])}{RESET}")
        print(f"  {CYAN}• 레벨 전력: {int(analysis['level_power'])}{RESET}")
        print(f"  {CYAN}• 밸런스 보너스: {int(analysis['balance_power'])}{RESET}")
        print(f"  {CYAN}• 시너지 보너스: {int(analysis['synergy_power'])}{RESET}")
        
        final_multiplier = scaling * difficulty_modifier
        print(f"\n{YELLOW}💡 적들이 {final_multiplier:.1f}배 강화됩니다! (파티 {scaling:.1f}x × 게임난이도 {difficulty_modifier:.1f}x){RESET}")
        print(f"{CYAN}═══════════════════════════════════════════════════════════{RESET}")
    
    def _get_game_difficulty_name(self) -> str:
        """게임의 기본 난이도 이름 반환"""
        try:
            from config import game_config
            if hasattr(game_config, 'current_difficulty'):
                return game_config.current_difficulty
            else:
                return "보통"
        except:
            return "보통"

# 전역 스케일러 인스턴스
dynamic_scaler = DynamicEnemyScaler()

def get_dynamic_scaler() -> DynamicEnemyScaler:
    """동적 스케일러 반환"""
    return dynamic_scaler

def scale_enemy_for_party(enemy: Character, party: List[Character], floor: int) -> Character:
    """파티에 맞춰 적 스케일링 (편의 함수)"""
    return dynamic_scaler.scale_enemy(enemy, party, floor)

def update_difficulty_for_party(party: List[Character]):
    """파티 변경 시 난이도 업데이트"""
    dynamic_scaler.update_party_analysis(party)

def show_current_difficulty():
    """현재 난이도 정보 표시"""
    dynamic_scaler.display_difficulty_info()
