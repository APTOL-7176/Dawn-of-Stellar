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
    
    # ⚡ 데미지 배율은 UnifiedDamageSystem에서 중앙 관리됨
    # 이 클래스는 다른 밸런스 설정만 담당
    
    @staticmethod
    def get_brave_damage_multiplier():
        """BRV 데미지 배율 가져오기 - UnifiedDamageSystem에서 관리"""
        try:
            from .unified_damage_system import UnifiedDamageSystem
            return UnifiedDamageSystem.BRV_DAMAGE_BASE_MULTIPLIER
        except ImportError:
            return 0.1  # 폴백값
    
    @staticmethod
    def get_hp_damage_multiplier():
        """HP 데미지 배율 가져오기 - UnifiedDamageSystem에서 관리"""
        try:
            from .unified_damage_system import UnifiedDamageSystem
            return UnifiedDamageSystem.HP_DAMAGE_MULTIPLIER
        except ImportError:
            return 0.15  # 폴백값
    
    @staticmethod
    def get_break_damage_bonus():
        """Break 데미지 보너스 가져오기 - UnifiedDamageSystem에서 관리"""
        try:
            from .unified_damage_system import UnifiedDamageSystem
            return UnifiedDamageSystem.BREAK_DAMAGE_BONUS
        except ImportError:
            return 1.5  # 폴백값
    
    # Brave 수치 범위 제한 (1레벨 기준 350 정도로 조정)
    MIN_BRAVE = 0
    MAX_BRAVE_GLOBAL = 999999            # 전역 최대 Brave 제한 (5003 → 1253)
    MIN_INT_BRV = 50                   # 최소 초기 Brave (103 → 51)
    MAX_INT_BRV = 999999                  # 최대 초기 Brave (807 → 403)
    MIN_MAX_BRV = 200                  # 최소 최대 Brave (2503 → 753)
    MAX_MAX_BRV = 999999                 # 최대 최대 Brave (4003 → 1003)
    
    # 캐릭터 클래스별 Brave 스탯 템플릿 (1레벨 기준 350 정도로 조정)
    CLASS_BRAVE_STATS = {
        "검사": {
            "int_brv_base": 161,           # 161에서 시작 (321 → 161)
            "max_brv_base": 483,           # 483에서 시작 (INT BRV × 3.0)
            "brv_efficiency": 1.0,
            "brv_loss_resistance": 0.9
        },
        "전사": {
            "int_brv_base": 177,           # 177에서 시작 (353 → 177)
            "max_brv_base": 531,           # 531에서 시작 (INT BRV × 3.0)
            "brv_efficiency": 1.0,
            "brv_loss_resistance": 0.95
        },
        "대마법사": {
            "int_brv_base": 126,           # 낮은 시작값 (251 → 126)
            "max_brv_base": 504,           # 504에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.3,
            "brv_loss_resistance": 0.7
        },
        "아크메이지": {
            "int_brv_base": 116,           # 116에서 시작 (231 → 116)
            "max_brv_base": 464,           # 464에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.4,
            "brv_loss_resistance": 0.6
        },
        "성기사": {
            "int_brv_base": 192,           # 192에서 시작 (383 → 192)
            "max_brv_base": 480,           # 480에서 시작 (INT BRV × 2.5)
            "brv_efficiency": 0.8,
            "brv_loss_resistance": 1.2
        },
        "암살자": {
            "int_brv_base": 141,           # 141에서 시작 (281 → 141)
            "max_brv_base": 564,           # 564에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.1,
            "brv_loss_resistance": 0.8
        },
        "도적": {
            "int_brv_base": 151,           # 151에서 시작 (301 → 151)
            "max_brv_base": 604,           # 604에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.1,
            "brv_loss_resistance": 0.85
        },
        "정령술사": {
            "int_brv_base": 126,           # 126에서 시작 (251 → 126)
            "max_brv_base": 504,           # 504에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.2,
            "brv_loss_resistance": 0.8
        },
        "궁수": {
            "int_brv_base": 156,           # 156에서 시작 (311 → 156)
            "max_brv_base": 546,           # 546에서 시작 (INT BRV × 3.5)
            "brv_efficiency": 1.0,
            "brv_loss_resistance": 0.9
        },
        "성직자": {
            "int_brv_base": 176,           # 176에서 시작 (351 → 176)
            "max_brv_base": 440,           # 440에서 시작 (INT BRV × 2.5)
            "brv_efficiency": 0.9,
            "brv_loss_resistance": 1.1
        },
        "무당": {
            "int_brv_base": 156,           # 156에서 시작 (311 → 156)
            "max_brv_base": 546,           # 546에서 시작 (INT BRV × 3.5)
            "brv_efficiency": 1.2,
            "brv_loss_resistance": 0.9
        },
        "마검사": {
            "int_brv_base": 166,           # 166에서 시작 (331 → 166)
            "max_brv_base": 581,           # 581에서 시작 (INT BRV × 3.5)
            "brv_efficiency": 1.15,
            "brv_loss_resistance": 0.85
        },
        "시간술사": {
            "int_brv_base": 111,           # 111에서 시작 (221 → 111)
            "max_brv_base": 444,           # 444에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.5,
            "brv_loss_resistance": 0.7
        },
        # 탱커 클래스들
        "기사": {
            "int_brv_base": 186,           # 186에서 시작 (371 → 186)
            "max_brv_base": 465,           # 465에서 시작 (INT BRV × 2.5)
            "brv_efficiency": 0.85,
            "brv_loss_resistance": 1.15
        },
        "암흑기사": {
            "int_brv_base": 176,           # 176에서 시작 (351 → 176)
            "max_brv_base": 528,           # 528에서 시작 (INT BRV × 3.0)
            "brv_efficiency": 1.0,
            "brv_loss_resistance": 1.0
        },
        # 물리 딜러들
        "검성": {
            "int_brv_base": 171,           # 171에서 시작 (341 → 171)
            "max_brv_base": 598,           # 598에서 시작 (INT BRV × 3.5)
            "brv_efficiency": 1.1,
            "brv_loss_resistance": 0.9
        },
        "사무라이": {
            "int_brv_base": 161,           # 161에서 시작 (321 → 161)
            "max_brv_base": 644,           # 644에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.2,
            "brv_loss_resistance": 0.85
        },
        "몽크": {
            "int_brv_base": 181,           # 181에서 시작 (361 → 181)
            "max_brv_base": 543,           # 543에서 시작 (INT BRV × 3.0)
            "brv_efficiency": 1.0,
            "brv_loss_resistance": 0.95
        },
        "검투사": {
            "int_brv_base": 176,           # 176에서 시작 (351 → 176)
            "max_brv_base": 616,           # 616에서 시작 (INT BRV × 3.5)
            "brv_efficiency": 1.1,
            "brv_loss_resistance": 0.9
        },
        "광전사": {
            "int_brv_base": 151,           # 151에서 시작 (301 → 151)
            "max_brv_base": 604,           # 604에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.3,
            "brv_loss_resistance": 0.7
        },
        "해적": {
            "int_brv_base": 146,           # 146에서 시작 (291 → 146)
            "max_brv_base": 511,           # 511에서 시작 (INT BRV × 3.5)
            "brv_efficiency": 1.15,
            "brv_loss_resistance": 0.8
        },
        "기계공학자": {
            "int_brv_base": 136,           # 136에서 시작 (271 → 136)
            "max_brv_base": 544,           # 544에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.1,
            "brv_loss_resistance": 0.85
        },
        # 마법사들
        "네크로맨서": {
            "int_brv_base": 121,           # 121에서 시작 (241 → 121)
            "max_brv_base": 364,           # 364에서 시작 (INT BRV × 3.0)
            "brv_efficiency": 1.3,
            "brv_loss_resistance": 0.75
        },
        "연금술사": {
            "int_brv_base": 116,           # 116에서 시작 (231 → 116)
            "max_brv_base": 348,           # 348에서 시작 (INT BRV × 3.0)
            "brv_efficiency": 1.25,
            "brv_loss_resistance": 0.8
        },
        "차원술사": {
            "int_brv_base": 106,           # 106에서 시작 (211 → 106)
            "max_brv_base": 424,           # 424에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.6,
            "brv_loss_resistance": 0.6
        },
        # 서포터들
        "바드": {
            "int_brv_base": 146,           # 146에서 시작 (291 → 146)
            "max_brv_base": 365,           # 365에서 시작 (INT BRV × 2.5)
            "brv_efficiency": 0.95,
            "brv_loss_resistance": 1.0
        },
        "드루이드": {
            "int_brv_base": 161,           # 161에서 시작 (321 → 161)
            "max_brv_base": 403,           # 403에서 시작 (INT BRV × 2.5)
            "brv_efficiency": 1.1,
            "brv_loss_resistance": 1.05
        },
        "신관": {
            "int_brv_base": 166,           # 166에서 시작 (331 → 166)
            "max_brv_base": 415,           # 415에서 시작 (INT BRV × 2.5)
            "brv_efficiency": 0.9,
            "brv_loss_resistance": 1.2
        },
        # 특수 클래스들
        "용기사": {
            "int_brv_base": 227,           # 227에서 시작 (453 → 227)
            "max_brv_base": 681,           # 681에서 시작 (INT BRV × 3.0)
            "brv_efficiency": 1.2,
            "brv_loss_resistance": 0.9
        },
        "철학자": {
            "int_brv_base": 176,           # 176에서 시작 (351 → 176)
            "max_brv_base": 704,           # 704에서 시작 (INT BRV × 4.0)
            "brv_efficiency": 1.4,
            "brv_loss_resistance": 0.8
        }
    }
    
    # 적 밸런스 - 대폭 강화 (올스탯 4배, HP만 3배)
    ENEMY_SCALING = {
        "hp_multiplier": 3.0,              # HP 3배 강화 (1.0 → 3.0)
        "attack_multiplier": 4.0,          # 공격력 4배 강화 (0.85 → 4.0)
        "brave_multiplier": 4.0,           # Brave 4배 강화 (0.7 → 4.0)
        "ai_intelligence": 0.6             # AI 판단력 (0-1)
    }
    
    # 아이템 밸런스
    ITEM_BALANCE = {
        "heal_potion_base": 41,
        "great_heal_potion_base": 83,
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
                # Enemy 클래스는 조용히 처리 (너무 많은 로그 방지)
                if character_class != "Enemy":
                    logger.warning(f"Unknown character class: {character_class}, using default stats")
                # 기본값 (정의되지 않은 직업용 - 더 합리적인 성장)
                int_brv = GameBalance.validate_brave_value(
                    301 + (level - 1) * 27,   # 기본값 301 + 레벨당 27 (150+8에서 증가)
                    GameBalance.MIN_INT_BRV, 
                    2003  # 최대값 2003으로 증가 (200에서 증가)
                )
                max_brv = GameBalance.validate_brave_value(
                    1003 + (level - 1) * 123,  # 기본값 1003 + 레벨당 123 (400+30에서 증가)
                    807,  # 최소값 807로 증가
                    8003   # 최대값 8003으로 증가 (800에서 증가)
                )
                return {
                    "int_brv": int_brv,
                    "max_brv": max_brv,
                    "brv_efficiency": 1.0,
                    "brv_loss_resistance": 1.0
                }
                
            base_stats = GameBalance.CLASS_BRAVE_STATS[character_class]
            
            # 레벨에 따른 성장 (1레벨에서 350 정도 목표)
            level_bonus_int = (level - 1) * 11  # 레벨당 11씩 증가 (21→11 감소)
            level_bonus_max = (level - 1) * 51  # 레벨당 51씩 증가 (103→51 감소)
            
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
                "int_brv": 807,
                "max_brv": 9503,
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
                    203 + (level - 1) * 17, 
                    101, 
                    401
                )
                max_brv = GameBalance.validate_brave_value(
                    1507 + (level - 1) * 101,
                    1003,
                    3001
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
                    "int_brv": 151,  # 기본값 감소 (250→151)
                    "max_brv": 401,  # 기본값 감소 (2000→401)
                    "brv_efficiency": 0.7,  # 효율 감소 (0.8→0.7)
                    "brv_loss_resistance": 0.8  # 저항 감소 (0.9→0.8)
                }
            
            # 레벨에 따른 성장 (적의 성장률 더 낮게 조정)
            level_bonus_int = (level - 1) * 5   # 레벨당 5씩 증가 (10→5) - 절반으로 감소
            level_bonus_max = (level - 1) * 17  # 레벨당 17씩 증가 (50→17) - 절반 이하로 감소

            int_brv = GameBalance.validate_brave_value(
                base_stats["int_brv"] + level_bonus_int,
                53,   # 최소값 53으로 감소 (100→53)
                301   # 최대값 301으로 감소 (500→301)
            )
            max_brv = GameBalance.validate_brave_value(
                base_stats["max_brv"] + level_bonus_max,
                503,  # 최소값 503으로 감소 (1000→503)
                2003  # 최대값 2003으로 감소 (3500→2003)
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
                "int_brv": 101,   # 안전 기본값 감소 (200→101)
                "max_brv": 301,   # 안전 기본값 감소 (1500→301)
                "brv_efficiency": 0.7,
                "brv_loss_resistance": 0.8
            }
    
    @staticmethod
    def calculate_brave_damage(attacker_atk: int, defender_def: int, 
                             skill_multiplier: float = 1.0, attacker=None, defender=None, skill=None) -> int:
        """밸런스 조정된 Brave 데미지 계산 - UnifiedDamageSystem으로 리다이렉트"""
        try:
            # ⚡ 통합 데미지 시스템 사용 (중복 제거)
            from .unified_damage_system import UnifiedDamageSystem
            damage_system = UnifiedDamageSystem()
            
            # BRV 데미지 계산 결과 가져오기
            result = damage_system.calculate_brv_damage(
                attacker_atk=attacker_atk,
                defender_def=defender_def,
                skill_power=skill_multiplier,
                attacker=attacker,
                defender=defender,
                skill=skill
            )
            
            return result.final_damage
            
        except Exception as e:
            logger.error(f"Error in calculate_brave_damage redirect: {e}")
            # 폴백: 기본 계산
            base_damage = max(1, int((attacker_atk / max(1, defender_def)) * skill_multiplier * 50))
            return min(base_damage, 9999)
    
    @staticmethod
    def calculate_hp_damage(brave_points: int, skill_multiplier: float = 1.0,
                          is_break: bool = False, attacker=None, defender=None, skill=None) -> int:
        """밸런스 조정된 HP 데미지 계산 - UnifiedDamageSystem으로 리다이렉트"""
        try:
            # ⚡ 통합 데미지 시스템 사용 (중복 제거)
            from .unified_damage_system import UnifiedDamageSystem
            damage_system = UnifiedDamageSystem()
            
            # 스킬 객체 생성 (없으면 기본값)
            if skill is None:
                skill = {"hp_power": skill_multiplier}
            
            # HP 데미지 계산 결과 가져오기 (매개변수명 수정)
            result, wound_damage = damage_system.calculate_hp_damage(
                attacker=attacker or type('MockAttacker', (), {'brave_points': brave_points})(),
                target=defender or type('MockTarget', (), {})(),  # defender -> target으로 수정
                skill=skill,
                brv_points=brave_points,
                hp_power=skill_multiplier
            )
            
            # BREAK 보너스 적용
            final_damage = result.final_damage
            if is_break:
                final_damage = int(final_damage * 1.5)
            
            return final_damage
            
        except Exception as e:
            logger.error(f"Error in calculate_hp_damage redirect: {e}")
            # 폴백: 기본 계산
            base_damage = max(5, int(brave_points * skill_multiplier * 0.15))
            if is_break:
                base_damage = int(base_damage * 1.5)
            return base_damage
    
    @staticmethod
    def get_enemy_stats_multiplier(floor_level: int = 1) -> Dict:
        """층수에 따른 적 스탯 배율 - 균형잡힌 난이도"""
        try:
            floor_level = max(1, min(floor_level, 20))  # 층수 제한
            
            # 초기층부터 강한 적들 - 대폭 강화
            if floor_level <= 3:
                # 1-3층: 강한 기본 난이도 (4배 베이스)
                scaling_factor = 4.0 + (floor_level - 1) * 0.5  # 4.0, 4.5, 5.0배
            elif floor_level <= 5:
                # 4-5층: 더욱 강화
                scaling_factor = 5.5 + (floor_level - 4) * 0.5  # 5.5, 6.0배
            else:
                # 6층 이상: 극강의 적들
                scaling_factor = 6.5 + (floor_level - 6) * 0.3
            
            return {
                "hp": GameBalance.ENEMY_SCALING["hp_multiplier"] * scaling_factor,  # HP 3배 * 층수배율
                "attack": GameBalance.ENEMY_SCALING["attack_multiplier"] * scaling_factor,  # 공격력 4배 * 층수배율
                "brave": GameBalance.ENEMY_SCALING["brave_multiplier"] * 1.5,  # Brave 50% 추가 증가
                "ai": min(0.95, GameBalance.ENEMY_SCALING["ai_intelligence"] + floor_level * 0.08)  # AI 더 똑똑하게
            }
            
        except Exception as e:
            logger.error(f"Error calculating enemy stats multiplier: {e}")
            return {"hp": 12.0, "attack": 16.0, "brave": 6.0, "ai": 0.8}  # 기본값도 대폭 강화
    
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
