"""
Dawn of Stellar - 통합 적 시스템
기존 enemy_system.py와 advanced_field_enemy_ai.py를 통합하여 밸런스 맞춤
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

class EnemyIntegrationMode(Enum):
    """적 생성 모드"""
    CLASSIC = "classic"           # 기존 간단한 적 시스템
    ADVANCED = "advanced"         # 고급 AI 적 시스템
    HYBRID = "hybrid"             # 두 시스템을 혼합

class IntegratedEnemyManager:
    """기존 적 시스템과 고급 AI 시스템을 통합하는 매니저"""
    
    def __init__(self):
        self.mode = EnemyIntegrationMode.HYBRID
        self.classic_enemy_ratio = 0.6  # 60% 클래식, 40% 고급
        self.advanced_field_ai = None
        self.classic_enemy_system = None
        
        # 층별 난이도 곡선 통합
        self.integrated_scaling = {
            # 층수: (클래식_비율, 고급_비율, 보스_확률)
            1: (0.9, 0.1, 0.0),     # 초반은 클래식 위주
            5: (0.8, 0.2, 0.05),    # 5층부터 고급 AI 증가
            10: (0.7, 0.3, 0.1),    # 10층부터 밸런스
            15: (0.6, 0.4, 0.15),   # 15층부터 고급 AI 우세
            20: (0.5, 0.5, 0.2),    # 20층부터 동등
            30: (0.4, 0.6, 0.25),   # 30층부터 고급 AI 위주
            50: (0.3, 0.7, 0.3),    # 50층부터 고급 AI 중심
            100: (0.2, 0.8, 0.4),   # 100층 극한 난이도
        }
        
        # 🎯 통합 적 레벨 스케일링 (밸런스 조정)
        self.level_scaling_curve = {
            1: 1.0,    # 1층 기준
            5: 1.8,    # 5층 80% 증가
            10: 2.5,   # 10층 150% 증가
            15: 3.5,   # 15층 250% 증가
            20: 4.8,   # 20층 380% 증가
            30: 7.0,   # 30층 600% 증가
            50: 12.0,  # 50층 1100% 증가
            75: 20.0,  # 75층 1900% 증가
            100: 35.0  # 100층 3400% 증가
        }
        
        self._initialize_systems()
    
    def _initialize_systems(self):
        """두 적 시스템 초기화"""
        try:
            # 고급 필드 AI 시스템 로드
            from game.advanced_field_enemy_ai import AdvancedFieldEnemyAI
            self.advanced_field_ai = AdvancedFieldEnemyAI()
            print("✅ 고급 필드 AI 시스템 로드 완료")
        except Exception as e:
            print(f"⚠️ 고급 필드 AI 시스템 로드 실패: {e}")
            self.advanced_field_ai = None
        
        try:
            # 클래식 적 시스템 로드
            from game.enemy_system import Enemy, EnemyType, EnemyAI
            self.classic_enemy_system = True
            print("✅ 클래식 적 시스템 로드 완료")
        except Exception as e:
            print(f"⚠️ 클래식 적 시스템 로드 실패: {e}")
            self.classic_enemy_system = None
    
    def get_floor_scaling_ratios(self, floor: int) -> Tuple[float, float, float]:
        """층수별 적 비율 계산"""
        # 가장 가까운 층수 찾기
        available_floors = sorted(self.integrated_scaling.keys())
        target_floor = floor
        
        for f in available_floors:
            if floor <= f:
                target_floor = f
                break
        else:
            target_floor = available_floors[-1]  # 최고층 사용
        
        return self.integrated_scaling[target_floor]
    
    def get_level_scale(self, floor: int) -> float:
        """층수별 레벨 스케일링 계산"""
        available_floors = sorted(self.level_scaling_curve.keys())
        
        # 정확한 층수가 있으면 사용
        if floor in self.level_scaling_curve:
            return self.level_scaling_curve[floor]
        
        # 선형 보간으로 중간값 계산
        for i, f in enumerate(available_floors):
            if floor <= f:
                if i == 0:
                    return self.level_scaling_curve[f]
                
                # 이전 층과 현재 층 사이 보간
                prev_floor = available_floors[i-1]
                prev_scale = self.level_scaling_curve[prev_floor]
                curr_scale = self.level_scaling_curve[f]
                
                # 선형 보간
                progress = (floor - prev_floor) / (f - prev_floor)
                return prev_scale + (curr_scale - prev_scale) * progress
        
        # 최고층을 넘으면 최고층 스케일 사용
        return self.level_scaling_curve[available_floors[-1]]
    
    def generate_integrated_enemy(self, floor: int, force_advanced: bool = False) -> Dict[str, Any]:
        """통합된 적 생성 시스템"""
        classic_ratio, advanced_ratio, boss_chance = self.get_floor_scaling_ratios(floor)
        
        # 보스 적 생성 확률 체크
        if random.random() < boss_chance:
            return self._generate_boss_enemy(floor)
        
        # 강제 고급 AI 또는 확률 기반 선택
        if force_advanced or random.random() < advanced_ratio:
            return self._generate_advanced_enemy(floor)
        else:
            return self._generate_classic_enemy(floor)
    
    def _generate_advanced_enemy(self, floor: int) -> Dict[str, Any]:
        """고급 AI 적 생성"""
        if not self.advanced_field_ai:
            return self._generate_classic_enemy(floor)  # fallback
        
        try:
            enemy_data = self.advanced_field_ai.generate_enemy(floor)
            # 통합 스케일링 적용
            scale = self.get_level_scale(floor)
            
            # 스탯 조정
            enemy_data["max_hp"] = int(enemy_data["max_hp"] * scale * 0.85)  # 고급 AI는 15% 감소
            enemy_data["current_hp"] = enemy_data["max_hp"]
            enemy_data["attack"] = int(enemy_data["attack"] * scale * 0.9)   # 공격력 10% 감소
            enemy_data["defense"] = int(enemy_data["defense"] * scale * 0.95) # 방어력 5% 감소
            
            enemy_data["enemy_type"] = "advanced_ai"
            enemy_data["ai_enabled"] = True
            
            return enemy_data
        except Exception as e:
            print(f"고급 AI 적 생성 실패: {e}")
            return self._generate_classic_enemy(floor)
    
    def _generate_classic_enemy(self, floor: int) -> Dict[str, Any]:
        """클래식 적 생성"""
        if not self.classic_enemy_system:
            # 간단한 기본 적 생성
            return self._generate_simple_enemy(floor)
        
        try:
            from game.enemy_system import Enemy, EnemyType, EnemyAI
            
            # 클래식 적 타입 목록
            classic_enemies = [
                ("늑대", EnemyType.BEAST, 45, 18, 8, 15),
                ("거미", EnemyType.BEAST, 30, 15, 5, 20),
                ("스켈레톤", EnemyType.UNDEAD, 35, 20, 12, 10),
                ("곰", EnemyType.BEAST, 80, 25, 15, 8),
                ("좀비", EnemyType.UNDEAD, 60, 16, 6, 6),
                ("임프", EnemyType.DEMON, 25, 14, 8, 16),
                ("오크", EnemyType.HUMANOID, 55, 22, 12, 11),
            ]
            
            name, enemy_type, base_hp, base_attack, base_defense, base_speed = random.choice(classic_enemies)
            
            # 통합 스케일링 적용
            scale = self.get_level_scale(floor)
            level = max(1, floor)
            
            enemy_data = {
                "name": name,
                "display_name": name,
                "type": enemy_type.value if hasattr(enemy_type, 'value') else str(enemy_type),
                "behavior": "classic",
                "level": level,
                "max_hp": int(base_hp * scale),
                "current_hp": int(base_hp * scale),
                "attack": int(base_attack * scale),
                "defense": int(base_defense * scale),
                "speed": int(base_speed * scale),
                "max_mp": int(20 * scale),
                "current_mp": int(20 * scale),
                "ai_aggression": 0.7,
                "ai_intelligence": 0.5,
                "special_abilities": [],
                "skills": ["기본공격"],
                "passives": [],
                "prefix": None,
                "experience_reward": int(max(5, floor * 2 * scale)),
                "gold_reward": int(max(2, floor * 1 * scale)),
                "enemy_type": "classic",
                "ai_enabled": False,
                "status_effects": {},
                "last_skill_use": {}
            }
            
            return enemy_data
            
        except Exception as e:
            print(f"클래식 적 생성 실패: {e}")
            return self._generate_simple_enemy(floor)
    
    def _generate_simple_enemy(self, floor: int) -> Dict[str, Any]:
        """가장 간단한 적 생성 (fallback)"""
        simple_enemies = ["늑대", "거미", "스켈레톤", "곰", "좀비"]
        name = random.choice(simple_enemies)
        
        # 기본 스탯
        base_stats = {
            "늑대": (45, 18, 8, 15),
            "거미": (30, 15, 5, 20),
            "스켈레톤": (35, 20, 12, 10),
            "곰": (80, 25, 15, 8),
            "좀비": (60, 16, 6, 6)
        }
        
        base_hp, base_attack, base_defense, base_speed = base_stats.get(name, (40, 15, 8, 12))
        scale = self.get_level_scale(floor)
        
        return {
            "name": name,
            "display_name": name,
            "type": "beast",
            "behavior": "simple",
            "level": max(1, floor),
            "max_hp": int(base_hp * scale),
            "current_hp": int(base_hp * scale),
            "attack": int(base_attack * scale),
            "defense": int(base_defense * scale),
            "speed": int(base_speed * scale),
            "max_mp": 20,
            "current_mp": 20,
            "ai_aggression": 0.5,
            "ai_intelligence": 0.3,
            "special_abilities": [],
            "skills": ["기본공격"],
            "passives": [],
            "prefix": None,
            "experience_reward": int(max(5, floor * 2)),
            "gold_reward": int(max(2, floor * 1)),
            "enemy_type": "simple",
            "ai_enabled": False,
            "status_effects": {},
            "last_skill_use": {}
        }
    
    def _generate_boss_enemy(self, floor: int) -> Dict[str, Any]:
        """보스 적 생성"""
        boss_names = [
            "거대한 곰", "늑대왕", "고대 골렘", "데스나이트", 
            "화염정령왕", "얼음용", "어둠의군주", "기계왕"
        ]
        
        name = random.choice(boss_names)
        scale = self.get_level_scale(floor) * 2.5  # 보스는 2.5배 강함
        
        # 보스 기본 스탯 (일반 적보다 강함)
        boss_data = {
            "name": f"[보스] {name}",
            "display_name": f"👑 {name}",
            "type": "boss",
            "behavior": "boss",
            "level": max(1, floor + 5),  # 보스는 층수+5 레벨
            "max_hp": int(200 * scale),
            "current_hp": int(200 * scale),
            "attack": int(50 * scale),
            "defense": int(30 * scale),
            "speed": int(20 * scale),
            "max_mp": int(100 * scale),
            "current_mp": int(100 * scale),
            "ai_aggression": 0.9,
            "ai_intelligence": 0.8,
            "special_abilities": ["보스의위압", "연속공격", "광역공격"],
            "skills": ["강타", "연속베기", "광역파괴"],
            "passives": ["보스내성", "죽음의저항"],
            "prefix": "전설의",
            "experience_reward": int(floor * 10 * scale),
            "gold_reward": int(floor * 5 * scale),
            "enemy_type": "boss",
            "ai_enabled": True,
            "status_effects": {},
            "last_skill_use": {},
            "boss_rank": "legendary"
        }
        
        return boss_data
    
    def set_integration_mode(self, mode: EnemyIntegrationMode):
        """통합 모드 설정"""
        self.mode = mode
        print(f"적 통합 모드 변경: {mode.value}")
    
    def set_classic_ratio(self, ratio: float):
        """클래식 적 비율 설정 (0.0 ~ 1.0)"""
        self.classic_enemy_ratio = max(0.0, min(1.0, ratio))
        print(f"클래식 적 비율 설정: {self.classic_enemy_ratio:.1%}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "mode": self.mode.value,
            "classic_ratio": self.classic_enemy_ratio,
            "advanced_ai_available": self.advanced_field_ai is not None,
            "classic_system_available": self.classic_enemy_system is not None,
            "scaling_levels": len(self.level_scaling_curve),
            "integration_floors": len(self.integrated_scaling)
        }

# 🌟 전역 통합 매니저 인스턴스
integrated_enemy_manager = IntegratedEnemyManager()

def create_integrated_enemy(floor: int, force_advanced: bool = False) -> Dict[str, Any]:
    """통합 적 생성 함수 (외부 인터페이스)"""
    return integrated_enemy_manager.generate_integrated_enemy(floor, force_advanced)

def set_enemy_balance(classic_ratio: float = 0.6):
    """적 밸런스 설정"""
    integrated_enemy_manager.set_classic_ratio(classic_ratio)

def get_enemy_system_status() -> Dict[str, Any]:
    """적 시스템 상태 조회"""
    return integrated_enemy_manager.get_system_status()

if __name__ == "__main__":
    # 테스트 코드
    print("=== Dawn of Stellar 통합 적 시스템 테스트 ===")
    
    # 시스템 상태 확인
    status = get_enemy_system_status()
    print(f"시스템 상태: {status}")
    
    # 층별 적 생성 테스트
    test_floors = [1, 5, 10, 20, 50, 100]
    
    for floor in test_floors:
        print(f"\n--- {floor}층 적 생성 테스트 ---")
        
        # 일반 적 생성
        enemy = create_integrated_enemy(floor)
        print(f"적: {enemy['display_name']} (타입: {enemy['enemy_type']})")
        print(f"레벨: {enemy['level']}, HP: {enemy['max_hp']}, 공격: {enemy['attack']}")
        
        # 고급 AI 강제 생성
        if status['advanced_ai_available']:
            advanced_enemy = create_integrated_enemy(floor, force_advanced=True)
            print(f"고급 AI: {advanced_enemy['display_name']}")
            print(f"스킬: {advanced_enemy.get('skills', [])[:3]}...")  # 첫 3개 스킬만
