#!/usr/bin/env python3
"""
Dawn of Stellar - 완전 재설계된 밸런스 시스템
물리/마법 분리, 회피/명중, 브레이브 시스템 통합
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

class StatType(Enum):
    """스탯 타입 정의"""
    # 공격 관련
    PHYSICAL_ATTACK = "물리공격력"
    MAGIC_ATTACK = "마법공격력"
    # 방어 관련
    PHYSICAL_DEFENSE = "물리방어력"
    MAGIC_DEFENSE = "마법방어력"
    # 명중/회피
    ACCURACY = "명중률"
    EVASION = "회피력"
    # 브레이브 관련
    BRV_ATTACK = "BRV공격력"
    BRV_DEFENSE = "BRV방어력"
    INT_BRV = "초기BRV"

class EffectType(Enum):
    """효과 타입"""
    BUFF = "버프"
    DEBUFF = "디버프"
    DOT = "지속피해"  # Damage over Time
    HOT = "지속회복"  # Heal over Time

@dataclass
class BalancedEffect:
    """밸런스 조정된 효과"""
    name: str
    effect_type: EffectType
    stat_type: StatType
    base_value: float  # 기본 수치 (%)
    max_value: float   # 최대 수치 (%)
    duration: int      # 지속시간 (턴)
    scaling_factor: float = 1.0  # 레벨/층수 스케일링

class BalancedEnemySystem:
    """완전 재설계된 적 밸런스 시스템"""
    
    def __init__(self):
        self.initialize_balanced_system()
    
    def initialize_balanced_system(self):
        """밸런스 시스템 초기화"""
        
        # 🎯 정규화된 레벨 스케일링 (부드러운 곡선)
        self.level_scaling_curve = {
            1: 1.0,     # 1층 기준
            5: 1.4,     # 5층 40% 증가
            10: 1.8,    # 10층 80% 증가  
            15: 2.3,    # 15층 130% 증가
            20: 2.8,    # 20층 180% 증가
            30: 3.8,    # 30층 280% 증가
            40: 5.0,    # 40층 400% 증가
            50: 6.5,    # 50층 550% 증가
            60: 8.5,    # 60층 750% 증가
            70: 11.0,   # 70층 1000% 증가
            80: 14.5,   # 80층 1350% 증가
            90: 19.0,   # 90층 1800% 증가
            100: 25.0   # 100층 2400% 증가 (최종 보스)
        }
        
        # 🏷️ 정규화된 접두사 효과 (밸런스 붕괴 방지)
        self.balanced_prefix_effects = {
            "정예": {
                StatType.PHYSICAL_ATTACK: 0.25,    # +25%
                StatType.MAGIC_ATTACK: 0.25,
                StatType.PHYSICAL_DEFENSE: 0.15,   # +15%
                StatType.MAGIC_DEFENSE: 0.15,
                StatType.BRV_ATTACK: 0.20,         # +20%
                "hp_bonus": 0.30,                  # +30% HP
                "exp_bonus": 1.5                   # 1.5배 경험치
            },
            "고대": {
                StatType.PHYSICAL_ATTACK: 0.20,
                StatType.MAGIC_ATTACK: 0.30,       # 마법 특화
                StatType.PHYSICAL_DEFENSE: 0.20,
                StatType.MAGIC_DEFENSE: 0.25,
                StatType.BRV_DEFENSE: 0.30,        # 브레이브 방어 특화
                "hp_bonus": 0.50,                  # +50% HP
                "mp_bonus": 0.40,                  # +40% MP
                "exp_bonus": 2.0
            },
            "야만적인": {
                StatType.PHYSICAL_ATTACK: 0.60,    # +60% 물리공격
                StatType.PHYSICAL_DEFENSE: -0.30,  # -30% 물리방어
                StatType.MAGIC_DEFENSE: -0.20,     # -20% 마법방어
                StatType.ACCURACY: 0.15,           # +15% 명중
                "speed_bonus": 0.20                # +20% 속도
            },
            "중장갑": {
                StatType.PHYSICAL_DEFENSE: 0.80,   # +80% 물리방어
                StatType.MAGIC_DEFENSE: 0.40,      # +40% 마법방어
                StatType.BRV_DEFENSE: 0.50,        # +50% BRV방어
                StatType.EVASION: -0.40,           # -40% 회피
                "speed_penalty": -0.30             # -30% 속도
            },
            "민첩한": {
                StatType.EVASION: 0.50,            # +50% 회피
                StatType.ACCURACY: 0.30,           # +30% 명중
                "speed_bonus": 0.60,               # +60% 속도
                StatType.PHYSICAL_DEFENSE: -0.20,  # -20% 물리방어
                "hp_penalty": -0.15                # -15% HP
            },
            "마법적인": {
                StatType.MAGIC_ATTACK: 0.70,       # +70% 마법공격
                StatType.MAGIC_DEFENSE: 0.30,      # +30% 마법방어
                StatType.PHYSICAL_DEFENSE: -0.25,  # -25% 물리방어
                "mp_bonus": 0.80,                  # +80% MP
                "magic_skills": True               # 마법 스킬 추가
            },
            "독성": {
                StatType.PHYSICAL_ATTACK: 0.20,    # +20% 물리공격
                "poison_immunity": True,           # 독 면역
                "poison_attack": 0.40,             # 공격 시 40% 독 피해
                "poison_aura": True                # 독 오라
            },
            "재생": {
                StatType.PHYSICAL_DEFENSE: 0.15,   # +15% 물리방어
                StatType.MAGIC_DEFENSE: 0.15,      # +15% 마법방어
                "regeneration": 0.08,              # 턴당 8% 회복
                "healing_bonus": 0.50              # +50% 회복 효과
            },
            "폭발성": {
                StatType.PHYSICAL_ATTACK: 0.30,    # +30% 물리공격
                "death_explosion": 0.80,           # 사망 시 80% 폭발 피해
                "hp_penalty": -0.20,               # -20% HP
                "unstable": True                   # 불안정 (크리티컬 받으면 즉시 폭발)
            },
            "투명한": {
                StatType.EVASION: 0.40,            # +40% 회피
                StatType.PHYSICAL_ATTACK: 0.25,    # +25% 물리공격 (기습)
                StatType.ACCURACY: 0.20,           # +20% 명중
                "stealth": True,                   # 은신 능력
                "first_strike": True               # 선제공격
            },
            "광폭한": {
                "berserker_rage": True,            # 체력 낮을수록 강해짐
                StatType.PHYSICAL_ATTACK: 0.40,    # +40% 물리공격
                StatType.MAGIC_DEFENSE: -0.30,     # -30% 마법방어
                "rage_scaling": 1.5                # 체력 비례 공격력 증가
            },
            "얼음": {
                StatType.MAGIC_ATTACK: 0.35,       # +35% 마법공격
                "ice_immunity": True,              # 얼음 면역
                "ice_attack": 0.30,               # 30% 확률 빙결
                "cold_aura": True                  # 냉기 오라 (속도 감소)
            },
            "화염": {
                StatType.MAGIC_ATTACK: 0.40,       # +40% 마법공격
                "fire_immunity": True,             # 화염 면역
                "fire_attack": 0.35,              # 35% 확률 화상
                "burn_aura": True                  # 화상 오라
            },
            "전기": {
                StatType.MAGIC_ATTACK: 0.30,       # +30% 마법공격
                StatType.ACCURACY: 0.25,           # +25% 명중 (유도)
                "electric_immunity": True,         # 전기 면역
                "electric_attack": 0.25,          # 25% 확률 마비
                "shock_aura": True                 # 전기 오라
            },
            "축복받은": {
                StatType.MAGIC_DEFENSE: 0.40,      # +40% 마법방어
                StatType.BRV_DEFENSE: 0.35,        # +35% BRV방어
                "holy_immunity": True,             # 언데드 특효 면역
                "healing": 0.05,                   # 턴당 5% 회복
                "blessed_attacks": True            # 축복된 공격
            },
            "타락한": {
                StatType.PHYSICAL_ATTACK: 0.35,    # +35% 물리공격
                StatType.MAGIC_ATTACK: 0.25,       # +25% 마법공격
                "corruption_aura": True,           # 타락 오라 (디버프)
                "dark_immunity": True,             # 어둠 면역
                "life_steal": 0.15                 # 15% 생명력 흡수
            }
        }
        
        # 🎭 정규화된 버프/디버프 지속시간
        self.balanced_durations = {
            # 짧은 효과 (2턴)
            "순간_버프": 2,      # 공격력 증가, 명중률 증가 등
            "순간_디버프": 2,    # 방어력 감소, 회피력 감소 등
            
            # 보통 효과 (3턴)  
            "일반_버프": 3,      # 방어력 증가, 속도 증가 등
            "일반_디버프": 3,    # 공격력 감소, 속도 감소 등
            
            # 긴 효과 (4턴)
            "지속_효과": 4,      # 독, 화상, 재생 등
            "강화_버프": 4,      # 강력한 버프 효과
            
            # 특수 효과 (1턴)
            "즉시_효과": 1,      # 기절, 빙결 등
        }
        
        # 🧮 정규화된 효과 수치
        self.balanced_effect_values = {
            # 공격 관련 (%)
            "물리공격증가_소": 15,    "물리공격증가_중": 25,    "물리공격증가_대": 40,
            "마법공격증가_소": 15,    "마법공격증가_중": 25,    "마법공격증가_대": 40,
            "물리공격감소_소": -10,   "물리공격감소_중": -20,   "물리공격감소_대": -30,
            "마법공격감소_소": -10,   "마법공격감소_중": -20,   "마법공격감소_대": -30,
            
            # 방어 관련 (%)
            "물리방어증가_소": 20,    "물리방어증가_중": 35,    "물리방어증가_대": 50,
            "마법방어증가_소": 20,    "마법방어증가_중": 35,    "마법방어증가_대": 50,
            "물리방어감소_소": -15,   "물리방어감소_중": -25,   "물리방어감소_대": -40,
            "마법방어감소_소": -15,   "마법방어감소_중": -25,   "마법방어감소_대": -40,
            
            # 명중/회피 (%)
            "명중률증가_소": 20,      "명중률증가_중": 35,      "명중률증가_대": 50,
            "회피력증가_소": 25,      "회피력증가_중": 40,      "회피력증가_대": 60,
            "명중률감소_소": -15,     "명중률감소_중": -25,     "명중률감소_대": -40,
            "회피력감소_소": -20,     "회피력감소_중": -35,     "회피력감소_대": -50,
            
            # 브레이브 관련 (%)
            "BRV공격증가_소": 20,     "BRV공격증가_중": 35,     "BRV공격증가_대": 50,
            "BRV방어증가_소": 25,     "BRV방어증가_중": 40,     "BRV방어증가_대": 60,
            "BRV공격감소_소": -15,    "BRV공격감소_중": -25,    "BRV공격감소_대": -40,
            "BRV방어감소_소": -20,    "BRV방어감소_중": -30,    "BRV방어감소_대": -45,
            
            # 지속 피해/회복 (% of max HP/MP)
            "독피해_소": 5,          "독피해_중": 8,           "독피해_대": 12,
            "화상피해_소": 6,        "화상피해_중": 10,        "화상피해_대": 15,
            "회복_소": 8,            "회복_중": 12,            "회복_대": 18,
            "마나회복_소": 10,       "마나회복_중": 15,        "마나회복_대": 20,
        }
        
        # 📊 재설계된 기본 적 스탯 (물리/마법 분리)
        self.base_enemy_stats = {
            # (이름, 타입, HP, 물리공격, 마법공격, 물리방어, 마법방어, 속도, 명중, 회피, BRV공격, BRV방어, INT_BRV)
            "늑대": (45, 18, 5, 8, 6, 15, 75, 15, 20, 8, 15),
            "거미": (30, 12, 8, 5, 4, 20, 80, 25, 15, 6, 10),
            "스켈레톤": (35, 20, 3, 12, 15, 10, 70, 5, 18, 12, 12),
            "곰": (80, 25, 2, 15, 8, 8, 65, 10, 25, 10, 20),
            "좀비": (60, 16, 1, 6, 3, 6, 60, 5, 12, 4, 8),
            "임프": (25, 8, 18, 8, 12, 16, 75, 20, 12, 15, 8),
            "오크": (55, 22, 6, 12, 9, 11, 70, 12, 20, 11, 16),
            "골렘": (100, 15, 8, 25, 20, 5, 50, 8, 18, 18, 25),
            "도적": (40, 15, 5, 8, 6, 18, 85, 30, 16, 7, 12),
            "기계병": (65, 12, 20, 18, 22, 12, 75, 15, 15, 20, 15),
            "화염정령": (45, 8, 28, 10, 25, 14, 70, 18, 20, 22, 18),
            "얼음정령": (50, 6, 25, 15, 28, 10, 65, 12, 18, 25, 20),
            "마법사": (35, 5, 30, 6, 30, 12, 80, 15, 15, 28, 12),
            "전사": (70, 24, 8, 16, 12, 10, 75, 10, 22, 14, 18),
            "유령": (40, 10, 25, 20, 35, 18, 60, 40, 15, 30, 15),
            "와이번": (150, 30, 35, 20, 18, 16, 70, 20, 35, 20, 30),
            "촉수괴물": (85, 26, 15, 12, 8, 8, 65, 15, 28, 10, 22)
        }
        
        # 🎯 브레이브 시스템 통합 설정
        self.brave_system_settings = {
            "brv_to_hp_ratio": 0.8,        # BRV → HP 변환 비율
            "break_bonus_damage": 1.5,     # BREAK 상태 추가 피해
            "int_brv_recovery_rate": 0.3,  # INT BRV 회복 비율
            "brv_attack_variance": 0.2,    # BRV 공격 변동성 (±20%)
            "critical_brv_bonus": 0.5,     # 크리티컬 시 BRV 보너스
        }
    
    def get_level_scaling(self, floor: int) -> float:
        """층수에 따른 스케일링 계수 계산"""
        # 구간별 선형 보간
        floors = sorted(self.level_scaling_curve.keys())
        
        if floor <= floors[0]:
            return self.level_scaling_curve[floors[0]]
        if floor >= floors[-1]:
            return self.level_scaling_curve[floors[-1]]
        
        # 선형 보간
        for i in range(len(floors) - 1):
            if floors[i] <= floor <= floors[i + 1]:
                lower_floor, upper_floor = floors[i], floors[i + 1]
                lower_scale, upper_scale = self.level_scaling_curve[lower_floor], self.level_scaling_curve[upper_floor]
                
                ratio = (floor - lower_floor) / (upper_floor - lower_floor)
                return lower_scale + (upper_scale - lower_scale) * ratio
        
        return 1.0
    
    def generate_balanced_enemy(self, enemy_name: str, floor: int, prefix: str = None) -> Dict[str, Any]:
        """완전히 밸런스 조정된 적 생성"""
        if enemy_name not in self.base_enemy_stats:
            enemy_name = "늑대"  # 기본값
        
        # 기본 스탯 가져오기
        stats = self.base_enemy_stats[enemy_name]
        base_hp, base_phys_atk, base_mag_atk, base_phys_def, base_mag_def, base_speed, base_acc, base_eva, base_brv_atk, base_brv_def, base_int_brv = stats
        
        # 레벨 스케일링 적용
        scale = self.get_level_scaling(floor)
        level = max(1, floor)
        
        # 기본 능력치 계산
        enemy_data = {
            "name": enemy_name,
            "display_name": f"{prefix + ' ' if prefix else ''}{enemy_name}",
            "level": level,
            "floor": floor,
            
            # 체력/마나
            "max_hp": int(base_hp * scale),
            "current_hp": int(base_hp * scale),
            "max_mp": int(10 * math.sqrt(scale)),  # MP는 천천히 증가
            "current_mp": int(10 * math.sqrt(scale)),
            
            # 공격 능력치
            "physical_attack": int(base_phys_atk * scale),
            "magic_attack": int(base_mag_atk * scale),
            
            # 방어 능력치  
            "physical_defense": int(base_phys_def * scale),
            "magic_defense": int(base_mag_def * scale),
            
            # 명중/회피
            "accuracy": int(base_acc + scale * 2),      # 명중률은 천천히 증가
            "evasion": int(base_eva + scale * 1.5),     # 회피력도 천천히 증가
            
            # 브레이브 시스템
            "brv_attack": int(base_brv_atk * scale),
            "brv_defense": int(base_brv_def * scale),  
            "int_brv": int(base_int_brv * scale * 0.8), # INT BRV는 조금 느리게 증가
            "current_brv": int(base_int_brv * scale * 0.8),
            "max_brv": int(base_int_brv * scale * 3),   # 최대 BRV는 INT BRV의 3배
            
            # 기타
            "speed": int(base_speed + scale * 0.5),     # 속도는 매우 천천히 증가
            "experience_reward": int(10 * scale),
            "gold_reward": int(5 * scale),
            
            # 상태 관리
            "status_effects": {},
            "is_broken": False,
            "prefix": prefix,
            "scaling_applied": scale
        }
        
        # 접두사 효과 적용
        if prefix and prefix in self.balanced_prefix_effects:
            enemy_data = self._apply_balanced_prefix(enemy_data, prefix)
        
        return enemy_data
    
    def _apply_balanced_prefix(self, enemy_data: Dict[str, Any], prefix: str) -> Dict[str, Any]:
        """밸런스 조정된 접두사 효과 적용"""
        effects = self.balanced_prefix_effects[prefix]
        
        for stat_type, modifier in effects.items():
            if isinstance(stat_type, StatType):
                stat_name = self._get_stat_name(stat_type)
                if stat_name in enemy_data:
                    if modifier > 0:
                        enemy_data[stat_name] = int(enemy_data[stat_name] * (1 + modifier))
                    else:
                        enemy_data[stat_name] = int(enemy_data[stat_name] * (1 + modifier))
            
            elif stat_type == "hp_bonus":
                enemy_data["max_hp"] = int(enemy_data["max_hp"] * (1 + modifier))
                enemy_data["current_hp"] = enemy_data["max_hp"]
            elif stat_type == "mp_bonus":
                enemy_data["max_mp"] = int(enemy_data["max_mp"] * (1 + modifier))
                enemy_data["current_mp"] = enemy_data["max_mp"]
            elif stat_type == "speed_bonus":
                enemy_data["speed"] = int(enemy_data["speed"] * (1 + modifier))
            elif stat_type == "speed_penalty":
                enemy_data["speed"] = int(enemy_data["speed"] * (1 + modifier))
            elif stat_type == "exp_bonus":
                enemy_data["experience_reward"] = int(enemy_data["experience_reward"] * modifier)
                enemy_data["gold_reward"] = int(enemy_data["gold_reward"] * modifier)
        
        return enemy_data
    
    def _get_stat_name(self, stat_type: StatType) -> str:
        """StatType을 실제 스탯 이름으로 변환"""
        stat_mapping = {
            StatType.PHYSICAL_ATTACK: "physical_attack",
            StatType.MAGIC_ATTACK: "magic_attack", 
            StatType.PHYSICAL_DEFENSE: "physical_defense",
            StatType.MAGIC_DEFENSE: "magic_defense",
            StatType.ACCURACY: "accuracy",
            StatType.EVASION: "evasion",
            StatType.BRV_ATTACK: "brv_attack",
            StatType.BRV_DEFENSE: "brv_defense",
            StatType.INT_BRV: "int_brv"
        }
        return stat_mapping.get(stat_type, "")
    
    def calculate_damage(self, attacker: Dict, defender: Dict, attack_type: str = "physical") -> Tuple[int, bool, str]:
        """정확한 데미지 계산 (물리/마법 분리, 브레이브 시스템)"""
        # 명중 판정
        hit_chance = attacker.get("accuracy", 70) - defender.get("evasion", 10)
        hit_chance = max(10, min(95, hit_chance))  # 10%~95% 제한
        
        if random.randint(1, 100) > hit_chance:
            return 0, False, "회피"
        
        # 기본 공격력/방어력
        if attack_type == "physical":
            base_attack = attacker.get("physical_attack", 10)
            base_defense = defender.get("physical_defense", 5)
        elif attack_type == "magic":
            base_attack = attacker.get("magic_attack", 10) 
            base_defense = defender.get("magic_defense", 5)
        elif attack_type == "brv":
            base_attack = attacker.get("brv_attack", 10)
            base_defense = defender.get("brv_defense", 5)
        else:
            base_attack = attacker.get("physical_attack", 10)
            base_defense = defender.get("physical_defense", 5)
        
        # 기본 데미지 계산
        attack_ratio = base_attack / max(1, base_defense)
        base_damage = base_attack * (0.5 + attack_ratio * 0.3)
        
        # 변동성 추가 (±15%)
        variance = random.uniform(0.85, 1.15)
        final_damage = int(base_damage * variance)
        
        # 크리티컬 판정 (5% 기본 + 운 보정)
        critical_chance = 5 + (attacker.get("luck", 0) * 0.5)
        is_critical = random.randint(1, 100) <= critical_chance
        
        if is_critical:
            final_damage = int(final_damage * 1.5)
            
        return max(1, final_damage), is_critical, attack_type
    
    def apply_status_effect(self, target: Dict, effect_name: str, duration: int, value: float) -> bool:
        """상태 효과 적용"""
        if "status_effects" not in target:
            target["status_effects"] = {}
        
        # 중복 효과는 더 강한 것으로 덮어쓰기
        if effect_name in target["status_effects"]:
            existing_value = target["status_effects"][effect_name]["value"]
            if abs(value) <= abs(existing_value):
                return False  # 더 약한 효과는 적용 안함
        
        target["status_effects"][effect_name] = {
            "value": value,
            "duration": duration,
            "remaining": duration
        }
        return True
    
    def process_turn_effects(self, character: Dict) -> List[str]:
        """턴 시작/종료 시 상태 효과 처리"""
        messages = []
        effects_to_remove = []
        
        if "status_effects" not in character:
            return messages
        
        for effect_name, effect_data in character["status_effects"].items():
            remaining = effect_data["remaining"]
            value = effect_data["value"]
            
            # 효과 적용
            if "독" in effect_name or "화상" in effect_name:
                damage = int(character["max_hp"] * abs(value) / 100)
                character["current_hp"] = max(0, character["current_hp"] - damage)
                messages.append(f"{character.get('display_name', '대상')}이(가) {effect_name}으로 {damage} 피해!")
                
            elif "회복" in effect_name:
                heal = int(character["max_hp"] * value / 100)
                character["current_hp"] = min(character["max_hp"], character["current_hp"] + heal)
                messages.append(f"{character.get('display_name', '대상')}이(가) {heal} 회복!")
            
            # 지속시간 감소
            effect_data["remaining"] -= 1
            if effect_data["remaining"] <= 0:
                effects_to_remove.append(effect_name)
                messages.append(f"{character.get('display_name', '대상')}의 {effect_name} 효과가 종료됨")
        
        # 만료된 효과 제거
        for effect_name in effects_to_remove:
            del character["status_effects"][effect_name]
        
        return messages

# 전역 인스턴스
balanced_enemy_system = BalancedEnemySystem()

def test_balanced_system():
    """밸런스 시스템 테스트"""
    print("🎯 완전 재설계된 밸런스 시스템 테스트")
    print("=" * 60)
    
    # 층별 적 테스트
    test_floors = [1, 10, 20, 50, 100]
    test_enemies = ["늑대", "스켈레톤", "임프", "화염정령", "와이번"]
    test_prefixes = [None, "정예", "고대", "야만적인", "중장갑"]
    
    for floor in test_floors:
        print(f"\n🏢 {floor}층 테스트:")
        scale = balanced_enemy_system.get_level_scaling(floor)
        print(f"   스케일링: {scale:.2f}x")
        
        for i, enemy_name in enumerate(test_enemies[:3]):
            prefix = test_prefixes[i] if i < len(test_prefixes) else None
            enemy = balanced_enemy_system.generate_balanced_enemy(enemy_name, floor, prefix)
            
            print(f"\n   👹 {enemy['display_name']} (Lv.{enemy['level']}):")
            print(f"      💔 HP: {enemy['current_hp']}/{enemy['max_hp']}")
            print(f"      ⚔️ 물리공격: {enemy['physical_attack']}, 🔮 마법공격: {enemy['magic_attack']}")
            print(f"      🛡️ 물리방어: {enemy['physical_defense']}, 🌟 마법방어: {enemy['magic_defense']}")
            print(f"      🎯 명중: {enemy['accuracy']}, 💨 회피: {enemy['evasion']}")
            print(f"      💪 BRV공격: {enemy['brv_attack']}, 🛡️ BRV방어: {enemy['brv_defense']}")
            print(f"      ⭐ INT_BRV: {enemy['int_brv']}, 💰 경험치: {enemy['experience_reward']}")
    
    # 데미지 계산 테스트
    print(f"\n🔥 데미지 계산 테스트:")
    attacker = balanced_enemy_system.generate_balanced_enemy("전사", 10, "정예")
    defender = balanced_enemy_system.generate_balanced_enemy("골렘", 10, "중장갑")
    
    print(f"   공격자: {attacker['display_name']} (물리: {attacker['physical_attack']}, 마법: {attacker['magic_attack']})")
    print(f"   방어자: {defender['display_name']} (물리방어: {defender['physical_defense']}, 마법방어: {defender['magic_defense']})")
    
    for attack_type in ["physical", "magic", "brv"]:
        damage, critical, _ = balanced_enemy_system.calculate_damage(attacker, defender, attack_type)
        crit_text = " (크리티컬!)" if critical else ""
        print(f"   {attack_type} 공격: {damage} 피해{crit_text}")
    
    print(f"\n✅ 밸런스 시스템 테스트 완료!")

if __name__ == "__main__":
    test_balanced_system()
