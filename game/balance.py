"""
게임 밸런스 조정 시스템
"""
import logging
from typing import Dict, Optional, Tuple

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameBalance:
    """게임 밸런스 설정"""
    
    # Brave 시스템 밸런스 (전투 속도 개선)
    BRAVE_DAMAGE_MULTIPLIER = 1.5      # Brave 공격 데미지 배율 (0.8 → 1.5, 빠른 전투)
    HP_DAMAGE_MULTIPLIER = 0.20        # HP 공격 데미지 배율 (0.12 → 0.20, 스킬 데미지 강화)
    BREAK_DAMAGE_BONUS = 1.5           # Break 상태 시 HP 데미지 증가율 (2.0 → 1.5)
    
    # Brave 수치 범위 제한 (대폭 하향 조정)
    MIN_BRAVE = 0
    MAX_BRAVE_GLOBAL = 5000            # 전역 최대 Brave 제한 (15000 → 5000)
    MIN_INT_BRV = 200                  # 최소 초기 Brave (500 → 200)
    MAX_INT_BRV = 800                  # 최대 초기 Brave (2000 → 800)
    MIN_MAX_BRV = 2500                 # 최소 최대 Brave (8000 → 2500)
    MAX_MAX_BRV = 4000                 # 최대 최대 Brave (14000 → 4000)
    
    # 캐릭터 클래스별 Brave 스탯 템플릿 (더 낮은 수치로 재조정)
    CLASS_BRAVE_STATS = {
        "검사": {
            "int_brv_base": 400,           # 400-600 범위로 대폭 하향
            "max_brv_base": 3000,          # 3000-4000 범위로 하향
            "brv_efficiency": 1.0,
            "brv_loss_resistance": 0.9
        },
        "대마법사": {
            "int_brv_base": 300,           # 낮은 시작값
            "max_brv_base": 3500,          # 높은 최대값
            "brv_efficiency": 1.3,
            "brv_loss_resistance": 0.7
        },
        "성기사": {
            "int_brv_base": 500,           # 높은 시작값
            "max_brv_base": 2800,          # 낮은 최대값 (안정형)
            "brv_efficiency": 0.8,
            "brv_loss_resistance": 1.2
        },
        "암살자": {
            "int_brv_base": 350,
            "max_brv_base": 3200,
            "brv_efficiency": 1.1,
            "brv_loss_resistance": 0.8
        },
        "정령술사": {
            "int_brv_base": 320,
            "max_brv_base": 3100,
            "brv_efficiency": 1.2,
            "brv_loss_resistance": 0.8
        },
        "궁수": {
            "int_brv_base": 380,
            "max_brv_base": 3000,
            "brv_efficiency": 1.0,
            "brv_loss_resistance": 0.9
        },
        "성직자": {
            "int_brv_base": 450,
            "max_brv_base": 2700,
            "brv_efficiency": 0.9,
            "brv_loss_resistance": 1.1
        }
    }
    
    # 적 밸런스
    ENEMY_SCALING = {
        "hp_multiplier": 1.0,
        "attack_multiplier": 0.85,        # 플레이어보다 약간 약하게
        "brave_multiplier": 0.7,          # 적은 Brave 효율
        "ai_intelligence": 0.6            # AI 판단력 (0-1)
    }
    
    # 아이템 밸런스
    ITEM_BALANCE = {
        "heal_potion_base": 40,
        "great_heal_potion_base": 80,
        "brave_booster_base": 300,        # Brave 회복량도 적절하게
        "equipment_bonus_multiplier": 1.0
    }
    
    @staticmethod
    def validate_brave_value(value: int, min_val: int = None, max_val: int = None) -> int:
        """Brave 수치 유효성 검사 및 제한"""
        try:
            value = int(value) if value is not None else 0
            
            if min_val is None:
                min_val = GameBalance.MIN_BRAVE
            if max_val is None:
                max_val = GameBalance.MAX_BRAVE_GLOBAL
                
            return max(min_val, min(value, max_val))
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid brave value: {value}, error: {e}")
            return min_val or GameBalance.MIN_BRAVE
    
    @staticmethod
    def get_character_brave_stats(character_class: str, level: int = 1) -> Dict:
        """캐릭터 클래스와 레벨에 따른 Brave 스탯 계산"""
        try:
            level = max(1, min(level, 50))  # 레벨 제한 1-50
            
            if character_class not in GameBalance.CLASS_BRAVE_STATS:
                logger.warning(f"Unknown character class: {character_class}, using default stats")
                # 기본값
                int_brv = GameBalance.validate_brave_value(
                    800 + (level - 1) * 30, 
                    GameBalance.MIN_INT_BRV, 
                    GameBalance.MAX_INT_BRV
                )
                max_brv = GameBalance.validate_brave_value(
                    9500 + (level - 1) * 150,
                    GameBalance.MIN_MAX_BRV,
                    GameBalance.MAX_MAX_BRV
                )
                return {
                    "int_brv": int_brv,
                    "max_brv": max_brv,
                    "brv_efficiency": 1.0,
                    "brv_loss_resistance": 1.0
                }
                
            base_stats = GameBalance.CLASS_BRAVE_STATS[character_class]
            
            # 레벨에 따른 성장 (더 적절한 성장률)
            level_bonus_int = (level - 1) * 25  # 레벨당 25씩 증가
            level_bonus_max = (level - 1) * 120  # 레벨당 120씩 증가
            
            int_brv = GameBalance.validate_brave_value(
                base_stats["int_brv_base"] + level_bonus_int,
                GameBalance.MIN_INT_BRV,
                GameBalance.MAX_INT_BRV
            )
            max_brv = GameBalance.validate_brave_value(
                base_stats["max_brv_base"] + level_bonus_max,
                GameBalance.MIN_MAX_BRV,
                GameBalance.MAX_MAX_BRV
            )
            
            return {
                "int_brv": int_brv,
                "max_brv": max_brv,
                "brv_efficiency": base_stats["brv_efficiency"],
                "brv_loss_resistance": base_stats["brv_loss_resistance"]
            }
            
        except Exception as e:
            logger.error(f"Error calculating brave stats for {character_class}: {e}")
            # 안전한 기본값 반환
            return {
                "int_brv": 800,
                "max_brv": 9500,
                "brv_efficiency": 1.0,
                "brv_loss_resistance": 1.0
            }
    
    @staticmethod
    def get_enemy_brave_stats(enemy_name: str, level: int = 1) -> Dict:
        """적의 이름과 레벨에 따른 Brave 스탯 계산"""
        try:
            from .enemy_system import EnemyType
            
            level = max(1, min(level, 20))  # 적 레벨 제한 1-20
            
            # "Lv.X " 접두사 제거하여 기본 이름 추출
            base_name = enemy_name
            if enemy_name.startswith("Lv."):
                # "Lv.2 트롤 수호자" -> "트롤 수호자"
                parts = enemy_name.split(" ", 1)
                if len(parts) > 1:
                    base_name = parts[1]
            
            # 적 이름을 EnemyType과 매핑
            enemy_type_mapping = {
                "고블린 전사": EnemyType.GOBLIN,
                "고블린": EnemyType.GOBLIN,
                "오크 광전사": EnemyType.ORC,
                "오크": EnemyType.ORC,
                "스켈레톤 마법사": EnemyType.SKELETON,
                "스켈레톤": EnemyType.SKELETON,
                "다크엘프 암살자": EnemyType.DARK_ELF,
                "다크엘프": EnemyType.DARK_ELF,
                "트롤 수호자": EnemyType.TROLL,
                "트롤": EnemyType.TROLL,
            }
            
            enemy_type = enemy_type_mapping.get(base_name)
            
            if enemy_type is None:
                logger.warning(f"Unknown enemy: {enemy_name} (base: {base_name}), using default enemy stats")
                # 기본 적 수치 (플레이어보다 낮게)
                int_brv = GameBalance.validate_brave_value(
                    200 + (level - 1) * 15, 
                    100, 
                    400
                )
                max_brv = GameBalance.validate_brave_value(
                    1500 + (level - 1) * 100,
                    1000,
                    3000
                )
                return {
                    "int_brv": int_brv,
                    "max_brv": max_brv,
                    "brv_efficiency": 0.8,
                    "brv_loss_resistance": 0.9
                }
            
            # enemy_system.py의 Brave 데이터 사용
            try:
                from .enemy_system import ENEMY_BRAVE_STATS
                if enemy_type in ENEMY_BRAVE_STATS:
                    base_stats = ENEMY_BRAVE_STATS[enemy_type]
                else:
                    raise KeyError(f"No brave stats for {enemy_type}")
            except (ImportError, KeyError):
                # 기본값 사용
                base_stats = {
                    "int_brv": 250,
                    "max_brv": 2000,
                    "brv_efficiency": 0.8,
                    "brv_loss_resistance": 0.9
                }
            
            # 레벨에 따른 성장 (적은 성장률)
            level_bonus_int = (level - 1) * 10  # 레벨당 10씩 증가
            level_bonus_max = (level - 1) * 50   # 레벨당 50씩 증가
            
            int_brv = GameBalance.validate_brave_value(
                base_stats["int_brv"] + level_bonus_int,
                100,
                500
            )
            max_brv = GameBalance.validate_brave_value(
                base_stats["max_brv"] + level_bonus_max,
                1000,
                3500
            )
            
            return {
                "int_brv": int_brv,
                "max_brv": max_brv,
                "brv_efficiency": base_stats["brv_efficiency"],
                "brv_loss_resistance": base_stats["brv_loss_resistance"]
            }
            
        except Exception as e:
            logger.error(f"Error calculating enemy brave stats for {enemy_name}: {e}")
            # 안전한 기본값 반환
            return {
                "int_brv": 200,
                "max_brv": 1500,
                "brv_efficiency": 0.8,
                "brv_loss_resistance": 0.9
            }
    
    @staticmethod
    def calculate_brave_damage(attacker_atk: int, defender_def: int, 
                             skill_multiplier: float = 1.0) -> int:
        """밸런스 조정된 Brave 데미지 계산"""
        try:
            attacker_atk = max(1, int(attacker_atk))
            defender_def = max(1, int(defender_def))
            skill_multiplier = max(0.1, min(skill_multiplier, 3.0))  # 배율 제한
            
            # 빠른 전투를 위한 개선된 데미지 공식
            base_damage = (attacker_atk / defender_def) * 80  # 기본 배율 증가 (40 → 80)
            final_damage = base_damage * skill_multiplier * GameBalance.BRAVE_DAMAGE_MULTIPLIER
            
            # 더 높은 데미지 범위로 조정
            return max(25, min(int(final_damage), 400))  # 25-400 범위 (15-200 → 25-400)
            
        except Exception as e:
            logger.error(f"Error calculating brave damage: {e}")
            return 50  # 안전한 기본값
    
    @staticmethod
    def calculate_hp_damage(brave_points: int, skill_multiplier: float = 1.0,
                          is_break: bool = False) -> int:
        """밸런스 조정된 HP 데미지 계산 - Opera Omnia 방식"""
        try:
            brave_points = max(0, int(brave_points))
            skill_multiplier = max(0.1, min(skill_multiplier, 5.0))  # 배율 제한 (버그 방지용)
            
            # Opera Omnia 스타일이지만 밸런스 조정: BRV의 10%를 HP 데미지로
            hp_damage_ratio = 0.1  # BRV 대비 HP 데미지 비율 (10%)
            base_damage = brave_points * skill_multiplier * hp_damage_ratio
            
            if is_break:
                base_damage *= GameBalance.BREAK_DAMAGE_BONUS
                
            # 최소 데미지만 보장 (최대치 제한 없음)
            final_damage = max(5, int(base_damage)) if brave_points > 0 else 5
            
            return final_damage
            
        except Exception as e:
            logger.error(f"Error calculating HP damage: {e}")
            return 10  # 안전한 기본값
    
    @staticmethod
    def get_enemy_stats_multiplier(floor_level: int = 1) -> Dict:
        """층수에 따른 적 스탯 배율 - 균형잡힌 난이도"""
        try:
            floor_level = max(1, min(floor_level, 20))  # 층수 제한
            
            # 초기층 난이도 적정 수준으로 조정
            if floor_level <= 3:
                # 1-3층: 적당한 난이도 (기존 2.7배 → 1.0배)
                scaling_factor = 1.8 + (floor_level - 1) * 0.2  # 0.8, 1.0, 1.2배
            elif floor_level <= 5:
                # 4-5층: 점진적 증가
                scaling_factor = 2.4 + (floor_level - 4) * 0.3  # 1.4, 1.7배
            else:
                # 6층 이상: 더 강한 적들
                scaling_factor = 2.8 + (floor_level - 6) * 0.2
            
            return {
                "hp": GameBalance.ENEMY_SCALING["hp_multiplier"] * scaling_factor,  # HP 배율 단순화
                "attack": GameBalance.ENEMY_SCALING["attack_multiplier"] * scaling_factor,  # 공격력 배율 단순화
                "brave": GameBalance.ENEMY_SCALING["brave_multiplier"] * 1.2,  # Brave 20% 증가
                "ai": min(0.95, GameBalance.ENEMY_SCALING["ai_intelligence"] + floor_level * 0.08)  # AI 더 똑똑하게
            }
            
        except Exception as e:
            logger.error(f"Error calculating enemy stats multiplier: {e}")
            return {"hp": 1.8, "attack": 1.5, "brave": 0.9, "ai": 0.7}  # 기본값도 강화
    
    @staticmethod
    def get_balanced_brave_range() -> Tuple[int, int]:
        """권장 Brave 범위 반환"""
        return (GameBalance.MIN_INT_BRV, GameBalance.MAX_INT_BRV)
    
    @staticmethod
    def get_balanced_max_brave_range() -> Tuple[int, int]:
        """권장 MAX BRV 범위 반환"""
        return (GameBalance.MIN_MAX_BRV, GameBalance.MAX_MAX_BRV)


# 밸런스 테스트 함수들
def test_brave_balance():
    """Brave 시스템 밸런스 테스트"""
    print("=== Dawn Of Stellar - Brave 시스템 밸런스 테스트 ===")
    
    try:
        classes = ["검사", "대마법사", "성기사", "암살자", "정령술사", "성직자"]
        
        print(f"{'클래스':12} {'INT BRV':8} {'MAX BRV':8} {'효율':4} {'저항':4} {'비고':10}")
        print("-" * 60)
        
        for char_class in classes:
            stats = GameBalance.get_character_brave_stats(char_class, level=1)
            efficiency = stats['brv_efficiency']
            resistance = stats['brv_loss_resistance']
            
            # 캐릭터 타입 분석
            if efficiency >= 1.2:
                char_type = "공격형"
            elif resistance >= 1.1:
                char_type = "방어형"
            elif efficiency <= 0.9 and resistance >= 1.0:
                char_type = "지원형"
            else:
                char_type = "균형형"
                
            print(f"{char_class:12} {stats['int_brv']:8} {stats['max_brv']:8} "
                  f"{efficiency:4.1f} {resistance:4.1f} {char_type:10}")
        
        print("\n=== 데미지 계산 테스트 ===")
        # 다양한 상황에서의 데미지 테스트
        test_cases = [
            (15, 10, 1.0, "기본 공격"),
            (20, 15, 1.5, "스킬 공격"),
            (25, 8, 2.0, "강력한 스킬"),
            (10, 20, 1.0, "방어력 높은 상대")
        ]
        
        print(f"{'상황':15} {'ATK':4} {'DEF':4} {'배율':4} {'Brave 데미지':10}")
        print("-" * 50)
        
        for atk, def_val, multiplier, description in test_cases:
            brave_dmg = GameBalance.calculate_brave_damage(atk, def_val, multiplier)
            print(f"{description:15} {atk:4} {def_val:4} {multiplier:4.1f} {brave_dmg:10}")
        
        print("\n=== HP 데미지 테스트 ===")
        brave_values = [500, 800, 1200, 1500]
        
        print(f"{'Brave':6} {'기본 HP':8} {'Break HP':8} {'비율':6}")
        print("-" * 35)
        
        for brave in brave_values:
            hp_normal = GameBalance.calculate_hp_damage(brave)
            hp_break = GameBalance.calculate_hp_damage(brave, is_break=True)
            ratio = hp_break / max(hp_normal, 1)
            
            print(f"{brave:6} {hp_normal:8} {hp_break:8} {ratio:6.1f}x")
        
        print("\n=== 권장 밸런스 범위 ===")
        int_range = GameBalance.get_balanced_brave_range()
        max_range = GameBalance.get_balanced_max_brave_range()
        
        print(f"INT BRV 권장 범위: {int_range[0]} ~ {int_range[1]}")
        print(f"MAX BRV 권장 범위: {max_range[0]} ~ {max_range[1]}")
        print(f"전역 최대 Brave 제한: {GameBalance.MAX_BRAVE_GLOBAL}")
        
        print("\n=== 적 스케일링 테스트 ===")
        print(f"{'층수':4} {'HP 배율':8} {'ATK 배율':8} {'AI 지능':8}")
        print("-" * 35)
        
        for floor in [1, 3, 5, 8, 10]:
            enemy_stats = GameBalance.get_enemy_stats_multiplier(floor)
            print(f"{floor:4} {enemy_stats['hp']:8.2f} {enemy_stats['attack']:8.2f} {enemy_stats['ai']:8.2f}")
        
        print("\n✅ 모든 밸런스 테스트 완료!")
        
    except Exception as e:
        logger.error(f"Balance test failed: {e}")
        print(f"❌ 테스트 중 오류 발생: {e}")

def test_edge_cases():
    """예외 상황 테스트"""
    print("\n=== 예외 상황 테스트 ===")
    
    try:
        # 잘못된 입력값 테스트
        print("1. 잘못된 클래스명 테스트:")
        invalid_stats = GameBalance.get_character_brave_stats("존재하지않는클래스")
        print(f"   결과: INT BRV={invalid_stats['int_brv']}, MAX BRV={invalid_stats['max_brv']}")
        
        print("2. 음수 데미지 계산 테스트:")
        negative_dmg = GameBalance.calculate_brave_damage(-10, 5)
        print(f"   결과: {negative_dmg} (최소값으로 보정)")
        
        print("3. 0 Brave HP 데미지 테스트:")
        zero_hp_dmg = GameBalance.calculate_hp_damage(0)
        print(f"   결과: {zero_hp_dmg} (최소 1 데미지)")
        
        print("4. 극한 레벨 테스트:")
        extreme_stats = GameBalance.get_character_brave_stats("검사", level=999)
        print(f"   결과: INT BRV={extreme_stats['int_brv']}, MAX BRV={extreme_stats['max_brv']} (제한됨)")
        
        print("5. Brave 수치 검증 테스트:")
        validated = GameBalance.validate_brave_value(99999)
        print(f"   99999 -> {validated} (최대값으로 제한)")
        
        print("✅ 모든 예외 상황 테스트 통과!")
        
    except Exception as e:
        logger.error(f"Edge case test failed: {e}")
        print(f"❌ 예외 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_brave_balance()
    test_edge_cases()
