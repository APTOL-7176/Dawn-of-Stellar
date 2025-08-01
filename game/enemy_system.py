#!/usr/bin/env python3
"""
적 시스템 - 100종 이상의 다양한 적
속성, AI, 스킬 등을 포함한 완전한 적 시스템
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
from .character import Character
try:
    from .new_skill_system import StatusType, StatusEffect
except ImportError:
    # StatusType과 StatusEffect를 간단히 정의 (fallback)
    class StatusType:
        POISON = "poison"
        BURN = "burn"
        FREEZE = "freeze"
        STUN = "stun"
        SLEEP = "sleep"
        
    class StatusEffect:
        def __init__(self, status_type, duration: int, intensity: float = 1.0):
            self.status_type = status_type
            self.duration = duration
            self.intensity = intensity

# 원소 타입
class ElementType(Enum):
    NEUTRAL = "무속성"
    FIRE = "화염"
    WATER = "물"
    EARTH = "대지"
    WIND = "바람"  # AIR을 WIND로 추가
    AIR = "바람"
    LIGHTNING = "번개"
    ICE = "얼음"
    POISON = "독"
    HOLY = "신성"
    DARK = "암흑"

# 추가 필요한 타입들
class SkillType(Enum):
    ATTACK = "attack"
    MAGIC = "magic"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"

class TargetType(Enum):
    SINGLE = "single"
    ALL = "all"
    SELF = "self"

class EnemyType(Enum):
    """적 타입"""
    # 일반 몬스터 (1-10층)
    GOBLIN = "고블린"
    ORC = "오크"
    SKELETON = "스켈레톤"
    ZOMBIE = "좀비"
    SPIDER = "거미"
    RAT = "쥐"
    BAT = "박쥐"
    WOLF = "늑대"
    SLIME = "슬라임"
    IMP = "임프"
    
    # 중급 몬스터 (11-20층)
    DARK_ELF = "다크엘프"
    TROLL = "트롤"
    OGRE = "오거"
    HOBGOBLIN = "홉고블린"
    WIGHT = "와이트"
    WRAITH = "레이스"
    GARGOYLE = "가고일"
    MINOTAUR = "미노타우로스"
    CENTAUR = "켄타우로스"
    HARPY = "하피"
    BASILISK = "바실리스크"
    
    # 고급 몬스터 (21-30층)
    DRAKE = "드레이크"
    CHIMERA = "키메라"
    MANTICORE = "만티코어"
    GRIFFON = "그리폰"
    WYVERN = "와이번"
    LICH = "리치"
    VAMPIRE = "뱀파이어"
    DEMON = "데몬"
    DEVIL = "데빌"
    ELEMENTAL = "엘리멘탈"
    
    # 최고급 몬스터 (31-40층)
    DRAGON = "드래곤"
    ARCHLICH = "아치리치"
    BALROG = "발로그"
    SUCCUBUS = "서큐버스"
    INCUBUS = "인큐버스"
    ANCIENT_GOLEM = "고대골렘"
    KRAKEN = "크라켄"
    BEHEMOTH = "베히모스"
    LEVIATHAN = "리바이어던"
    PHOENIX = "피닉스"
    
    # 전설급 몬스터 (41-50층)
    ELDER_DRAGON = "엘더드래곤"
    TITAN = "타이탄"
    CELESTIAL = "천계인"
    FALLEN_ANGEL = "타락천사"
    VOID_LORD = "공허군주"
    SHADOW_KING = "그림자왕"
    DEATH_LORD = "죽음군주"
    CHAOS_BEAST = "혼돈야수"
    NIGHTMARE = "나이트메어"
    AVATAR = "아바타"
    
    # 추가 몬스터들 (다양한 층)
    FIRE_SALAMANDER = "화염도롱뇽"
    ICE_GOLEM = "얼음골렘"
    STORM_BIRD = "폭풍새"
    EARTH_ELEMENTAL = "대지정령"
    WIND_SPIRIT = "바람정령"
    WATER_NYMPH = "물님프"
    LIGHT_SERAPH = "빛세라핌"
    DARK_SHADE = "어둠그림자"
    POISON_HYDRA = "독히드라"
    CRYSTAL_GOLEM = "수정골렘"
    METAL_KNIGHT = "철기사"
    BONE_DRAGON = "뼈드래곤"
    GHOST_KNIGHT = "유령기사"
    FLAME_DEMON = "화염악마"
    FROST_GIANT = "서리거인"
    THUNDER_EAGLE = "천둥독수리"
    ROCK_GIANT = "바위거인"
    WIND_DJINN = "바람지니"
    WATER_DRAGON = "물드래곤"
    SHADOW_ASSASSIN = "그림자암살자"
    CORRUPTED_ANGEL = "타락천사"
    VOID_STALKER = "공허추적자"
    CHAOS_SPAWN = "혼돈새끼"
    DREAM_EATER = "꿈먹는자"
    SOUL_REAPER = "영혼수확자"
    MIND_FLAYER = "정신지배자"
    TIME_WRAITH = "시간망령"
    SPACE_HORROR = "공간공포"
    REALITY_WARPER = "현실왜곡자"
    DIMENSIONAL_FIEND = "차원마귀"
    ETERNAL_GUARDIAN = "영원수호자"
    COSMIC_HORROR = "우주공포"
    PRIMORDIAL_BEAST = "태고야수"
    ANCIENT_EVIL = "고대악"
    FORGOTTEN_GOD = "잊혀진신"
    ABYSSAL_LORD = "심연군주"
    INFERNAL_DUKE = "지옥공작"
    CELESTIAL_WARDEN = "천계경비병"
    VOID_EMPEROR = "공허황제"
    SHADOW_EMPRESS = "그림자여제"
    CHAOS_OVERLORD = "혼돈대군주"
    DEATH_INCARNATE = "죽음화신"
    DESTROYER = "파괴자"
    CREATOR = "창조자"
    OBSERVER = "관찰자"
    JUDGE = "심판자"
    EXECUTIONER = "처형자"
    HERALD = "전령"
    PROPHET = "예언자"
    ORACLE = "신탁"
    SAGE = "현자"
    FOOL = "광인"
    WANDERER = "방랑자"
    SEEKER = "탐구자"
    GUARDIAN = "수호자"
    DESTROYER_OF_WORLDS = "세계파괴자"

class EnemyRank(Enum):
    """적 등급"""
    MINION = "하급"
    REGULAR = "일반"
    ELITE = "정예"
    CHAMPION = "챔피언"
    BOSS = "보스"
    RAID_BOSS = "레이드보스"
    LEGENDARY = "전설"
    MYTHIC = "신화"

class Enemy(Character):
    """적 캐릭터 클래스"""
    
    def __init__(self, enemy_type: EnemyType, floor: int):
        # 부모 클래스 초기화 (기본 스탯으로)
        super().__init__(
            name=enemy_type.value,
            character_class="Enemy",  # 영어로 변경하여 클래스명과 혼동 방지
            max_hp=100,
            physical_attack=20,
            magic_attack=15,
            physical_defense=15,
            magic_defense=10,
            speed=12
        )
        
        self.enemy_type = enemy_type
        self.floor = floor
        self.rank = self._determine_rank(floor)
        self.level = self._determine_level(floor)  # 레벨 시스템 추가
        
        # 적 전용 스탯 재설정
        self._set_enemy_stats()
        
        # AI 정보
        self.ai_type = self._determine_ai_type()
        self.aggression = random.randint(1, 10)
        self.intelligence = random.randint(1, 10)
        
        # 보상 정보
        self.exp_reward = self._calculate_exp_reward()
        self.gold_reward = self._calculate_gold_reward()
        self.drop_items = self._determine_drops()
        
        # 스킬 리스트
        self.enemy_skills = self._get_enemy_skills()
    
    def _determine_level(self, floor: int) -> int:
        """층수에 따른 레벨 결정"""
        base_level = floor
        
        # 초기 층에서는 레벨 변동을 거의 없앰
        if floor <= 4:
            level_variance = 0  # 1-4층: 변동 없음 (정확히 층수 = 레벨)
        elif floor <= 10:
            level_variance = random.randint(-1, 1)  # 5-10층: -1~+1 변동만
        else:
            level_variance = random.randint(-2, 3)  # 11층+: -2~+3 변동
            
        final_level = max(1, base_level + level_variance)
        
        # 등급별 레벨 보너스
        rank_bonus = {
            EnemyRank.MINION: -3,
            EnemyRank.REGULAR: 0,
            EnemyRank.ELITE: 2,
            EnemyRank.CHAMPION: 4,
            EnemyRank.BOSS: 6,
            EnemyRank.RAID_BOSS: 8,
            EnemyRank.LEGENDARY: 10,
            EnemyRank.MYTHIC: 15
        }.get(self.rank, 0)
        
        return max(1, final_level + rank_bonus)
    
    def _determine_rank(self, floor: int) -> EnemyRank:
        """층수에 따른 등급 결정"""
        if floor <= 10:
            weights = [60, 30, 8, 2, 0, 0, 0, 0]  # 하급~신화 확률
        elif floor <= 20:
            weights = [40, 40, 15, 4, 1, 0, 0, 0]
        elif floor <= 30:
            weights = [20, 40, 25, 10, 4, 1, 0, 0]
        elif floor <= 40:
            weights = [10, 30, 30, 20, 8, 2, 0, 0]
        elif floor <= 50:
            weights = [5, 20, 30, 25, 15, 4, 1, 0]
        else:
            weights = [2, 10, 20, 30, 25, 10, 2, 1]
        
        ranks = list(EnemyRank)
        return random.choices(ranks, weights=weights)[0]
    
    def _set_enemy_stats(self):
        """적 전용 스탯 설정 (적응형 밸런스 적용)"""
        base_stats = self._get_base_stats_by_type()
        
        # 난이도별 multiplier 적용
        from config import game_config
        enemy_hp_multiplier = game_config.get_difficulty_setting('enemy_hp_multiplier')
        enemy_damage_multiplier = game_config.get_difficulty_setting('enemy_damage_multiplier')
        
        # 합리적 난이도 증가
        if self.floor <= 5:
            floor_multiplier = 1.0 + (self.floor - 1) * 0.2  # 1-5층: 20% 증가 (1.0~1.8)
        elif self.floor <= 10:
            floor_multiplier = 1.8 + (self.floor - 6) * 0.15  # 6-10층: 15% 증가 (1.8~2.55)
        elif self.floor <= 20:
            floor_multiplier = 2.55 + (self.floor - 11) * 0.1  # 11-20층: 10% 증가 (2.55~3.45)
        elif self.floor <= 30:
            floor_multiplier = 3.45 + (self.floor - 21) * 0.08  # 21-30층: 8% 증가 (3.45~4.17)
        elif self.floor <= 50:
            floor_multiplier = 4.17 + (self.floor - 31) * 0.05  # 31-50층: 5% 증가 (4.17~5.12)
        else:
            floor_multiplier = 5.12 + (self.floor - 51) * 0.03  # 51층+: 3% 증가
        
        # 적응형 밸런스 시스템 적용
        try:
            from game.adaptive_balance import adaptive_balance
            balance_modifiers = adaptive_balance.get_enemy_modifiers()
            adaptive_hp_multiplier = balance_modifiers.enemy_health_multiplier
            adaptive_damage_multiplier = balance_modifiers.enemy_damage_multiplier
        except ImportError:
            adaptive_hp_multiplier = 1.0
            adaptive_damage_multiplier = 1.0
        
        rank_multiplier = self._get_rank_multiplier()
        level_multiplier = 1 + (self.level - 1) * 0.08  # 레벨당 8% 증가 (15%에서 감소)
        
        # 최종 스탯 계산 (스탯별 다른 배율 적용)
        for stat_name, base_value in base_stats.items():
            # 원소 타입은 곱셈하지 않음
            if stat_name == "element":
                self.element_type = base_value
                continue
            
            # 스탯별 성장률 조정 (플레이어 성장 패턴과 유사하게)
            # 난이도별 적 스탯 배율 적용
            if stat_name in ["max_hp"]:
                # HP는 가장 많이 성장 (플레이어와 유사) + 난이도 배율
                # 플레이어 HP 강화 요소: 장비 +50%, 패시브 +30% 고려
                stat_floor_multiplier = floor_multiplier * 1.4 * enemy_hp_multiplier  # 40% 추가 성장 (1.2→1.4) + 난이도
                stat_level_multiplier = 1 + (self.level - 1) * 0.15  # 레벨당 15% (12%→15%)
            elif stat_name in ["attack", "magic_power"]:
                # 공격력은 중간 성장 + 난이도 배율
                # 플레이어 공격력 강화: 무기 +80%, 패시브 +50%, 버프 +30% 고려
                stat_floor_multiplier = floor_multiplier * 1.3 * enemy_damage_multiplier  # 30% 추가 성장 (1.0→1.3) + 난이도
                stat_level_multiplier = 1 + (self.level - 1) * 0.12  # 레벨당 12% (8%→12%)
            elif stat_name in ["defense", "magic_defense"]:
                # 방어력은 중간 성장
                # 플레이어 방어력 강화: 방어구 +60%, 패시브 +30%, 버프 +20% 고려
                stat_floor_multiplier = floor_multiplier * 1.2  # 20% 추가 성장 (0.95→1.2)
                stat_level_multiplier = 1 + (self.level - 1) * 0.10  # 레벨당 10% (7%→10%)
            elif stat_name == "speed":
                # 속도는 가장 적게 성장
                # 플레이어 속도 강화: 장비 +40%, 패시브 +25%, 버프 +25% 고려
                stat_floor_multiplier = floor_multiplier * 1.0   # 기본 성장 (0.8→1.0)
                stat_level_multiplier = 1 + (self.level - 1) * 0.08  # 레벨당 8% (5%→8%)
            elif stat_name == "max_mp":
                # MP는 적게 성장
                # 플레이어 MP 강화: 장비 +30%, 패시브 +20% 고려
                stat_floor_multiplier = floor_multiplier * 0.8   # 낮은 성장 (0.7→0.8)
                stat_level_multiplier = 1 + (self.level - 1) * 0.05  # 레벨당 5% (3%→5%)
            else:
                # 기타 스탯 (BRV 등)
                stat_floor_multiplier = floor_multiplier
                stat_level_multiplier = level_multiplier
            
            # 스탯별 배율 적용
            adjusted_value = base_value * stat_floor_multiplier * rank_multiplier * stat_level_multiplier
            
            # 적응형 배율 적용 (HP, 물리공격력, 마법공격력에 적용) - 난이도는 이미 적용됨
            if stat_name in ["max_hp"]:
                final_value = int(adjusted_value * adaptive_hp_multiplier)
            elif stat_name in ["attack"]:
                final_value = int(adjusted_value * adaptive_damage_multiplier)
            else:
                final_value = int(adjusted_value)
            
            # Character 클래스의 속성명에 맞게 매핑
            if stat_name == "attack":
                self.physical_attack = final_value
                # 마법공격력에도 스탯별 배율과 적응형 배율 적용
                magic_base = base_stats.get("magic_power", base_value * 0.8)
                magic_stat_floor = floor_multiplier * 1.0  # 공격력과 동일
                magic_stat_level = 1 + (self.level - 1) * 0.08
                self.magic_attack = int(magic_base * magic_stat_floor * rank_multiplier * magic_stat_level * adaptive_damage_multiplier)
            elif stat_name == "defense":
                self.physical_defense = final_value
                # 마법방어력도 스탯별 배율 적용
                magic_def_base = base_stats.get("magic_defense", base_value * 0.8)
                magic_def_floor = floor_multiplier * 0.95  # 방어력과 동일
                magic_def_level = 1 + (self.level - 1) * 0.07
                self.magic_defense = int(magic_def_base * magic_def_floor * rank_multiplier * magic_def_level)
            elif stat_name == "max_hp":
                self.max_hp = final_value
            elif stat_name == "max_mp":
                self.max_mp = final_value
            elif stat_name == "speed":
                self.speed = final_value
            elif stat_name in ["init_brv", "max_brv"]:
                # BRV 값들도 스탯별 성장 적용 (속도와 비슷한 패턴)
                brv_floor_multiplier = floor_multiplier * 1.1  # BRV 성장 (속도보다 약간 높음)
                brv_level_multiplier = 1 + (self.level - 1) * 0.06  # 레벨당 6%
                brv_final_value = int(base_value * brv_floor_multiplier * rank_multiplier * brv_level_multiplier)
                
                if stat_name == "init_brv":
                    self.current_brv = brv_final_value
                elif stat_name == "max_brv":
                    self.max_brv = brv_final_value
        
        # 크리티컬/명중/회피 시스템 적용 (올바른 속성명 사용)
        self.critical_rate = self._get_enemy_critical_rate()  # %로 계산됨 (5.0 = 5%)
        self.accuracy = self._get_enemy_accuracy()           # %로 계산됨 (80.0 = 80%)
        self.evasion = self._get_enemy_evasion()             # %로 계산됨 (12.0 = 12%)
        
        # Character 클래스와 호환성을 위한 속성 설정
        self.dodge = self.evasion  # Character에서 사용하는 속성명
        
        # HP/MP 현재값 설정
        self.current_hp = self.max_hp
        self.current_mp = self.max_mp
        
        # Brave 시스템 (적용되지 않을 수도 있지만 호환성을 위해)
        try:
            # BRV 값이 이미 계산되어 설정되었는지 확인
            if not hasattr(self, 'current_brv'):
                # BRV가 계산되지 않은 경우에만 기본값 적용
                init_brv = base_stats.get("init_brv", 500)
                # 층수와 레벨에 맞게 초기 BRV 조정
                brv_floor_multiplier = floor_multiplier * 1.1
                brv_level_multiplier = 1 + (self.level - 1) * 0.06
                self.current_brv = int(init_brv * brv_floor_multiplier * rank_multiplier * brv_level_multiplier)
            if not hasattr(self, 'max_brv'):
                # max_brv가 계산되지 않은 경우에만 기본값 적용
                max_brv = base_stats.get("max_brv", 2500)
                # 층수와 레벨에 맞게 최대 BRV 조정
                brv_floor_multiplier = floor_multiplier * 1.1
                brv_level_multiplier = 1 + (self.level - 1) * 0.06
                self.max_brv = int(max_brv * brv_floor_multiplier * rank_multiplier * brv_level_multiplier)
            
            # 추가 BRV 관련 속성들 (플레이어와 호환)
            self.int_brv = self.current_brv  # 초기 BRV = 현재 BRV
            self.initial_brave = self.current_brv  # 호환성을 위한 별칭
            self.max_brave = self.max_brv  # 호환성을 위한 별칭
            self.current_brave = self.current_brv  # 호환성을 위한 별칭
            self.brave_points = self.current_brv  # brave_combat.py와 호환
            self.is_broken = False  # Break 상태
            self.brv_regen = max(1, self.speed // 15)  # BRV 자동 회복량 (적은 양)
            self.brave_bonus_rate = 1.0  # BRV 획득 배율
            self.brv_efficiency = 1.0  # BRV 효율성
        except:
            pass
    
    def _get_base_stats_by_type(self) -> Dict[str, int]:
        """적 타입별 기본 스탯 (명확한 원소 속성 포함)"""
        stats_table = {
            # 일반 몬스터 (1-10층) - 1층부터 위협적이게 조정
            EnemyType.GOBLIN: {
                "max_hp": 140, "max_mp": 35, "attack": 30, "defense": 20,
                "magic_power": 18, "magic_defense": 15, "speed": 30,
                "init_brv": 400, "max_brv": 800, "element": ElementType.NEUTRAL
            },
            EnemyType.ORC: {
                "max_hp": 180, "max_mp": 55, "attack": 42, "defense": 32,
                "magic_power": 25, "magic_defense": 28, "speed": 25,
                "init_brv": 720, "max_brv": 1440, "element": ElementType.NEUTRAL
            },
            EnemyType.SKELETON: {
                "max_hp": 150, "max_mp": 65, "attack": 34, "defense": 30,
                "magic_power": 30, "magic_defense": 36, "speed": 30,
                "init_brv": 650, "max_brv": 1320, "element": ElementType.DARK  # 언데드
            },
            EnemyType.ZOMBIE: {
                "max_hp": 200, "max_mp": 35, "attack": 38, "defense": 28,
                "magic_power": 16, "magic_defense": 24, "speed": 15,
                "init_brv": 680, "max_brv": 1350, "element": ElementType.DARK  # 언데드
            },
            EnemyType.SPIDER: {
                "max_hp": 120, "max_mp": 50, "attack": 36, "defense": 22,
                "magic_power": 26, "magic_defense": 24, "speed": 45,
                "init_brv": 540, "max_brv": 1080, "element": ElementType.POISON  # 독거미
            },
            EnemyType.RAT: {
                "max_hp": 100, "max_mp": 40, "attack": 30, "defense": 20,
                "magic_power": 18, "magic_defense": 16, "speed": 50,
                "init_brv": 480, "max_brv": 840, "element": ElementType.NEUTRAL
            },
            EnemyType.BAT: {
                "max_hp": 110, "max_mp": 55, "attack": 32, "defense": 18,
                "magic_power": 22, "magic_defense": 20, "speed": 55,
                "init_brv": 520, "max_brv": 980, "element": ElementType.DARK  # 어둠 속성
            },
            EnemyType.WOLF: {
                "max_hp": 160, "max_mp": 50, "attack": 40, "defense": 26,
                "magic_power": 20, "magic_defense": 22, "speed": 40,
                "init_brv": 640, "max_brv": 1260, "element": ElementType.NEUTRAL
            },
            EnemyType.SLIME: {
                "max_hp": 170, "max_mp": 60, "attack": 28, "defense": 36,
                "magic_power": 32, "magic_defense": 32, "speed": 20,
                "init_brv": 580, "max_brv": 1180, "element": ElementType.POISON  # 독성 슬라임
            },
            EnemyType.IMP: {
                "max_hp": 135, "max_mp": 75, "attack": 34, "defense": 24,
                "magic_power": 38, "magic_defense": 28, "speed": 38,
                "init_brv": 560, "max_brv": 1140, "element": ElementType.FIRE  # 화염 임프
            },
            
            # 중급 몬스터 (11-20층)
            EnemyType.DARK_ELF: {
                "max_hp": 120, "max_mp": 80, "attack": 35, "defense": 20,
                "magic_power": 30, "magic_defense": 25, "speed": 48,
                "init_brv": 680, "max_brv": 1320, "element": ElementType.DARK  # 어둠 암살자
            },
            EnemyType.TROLL: {
                "max_hp": 200, "max_mp": 40, "attack": 40, "defense": 35,
                "magic_power": 15, "magic_defense": 25, "speed": 20,
                "init_brv": 800, "max_brv": 1800, "element": ElementType.EARTH  # 대지 트롤
            },
            EnemyType.OGRE: {
                "max_hp": 250, "max_mp": 35, "attack": 45, "defense": 30,
                "magic_power": 12, "magic_defense": 20, "speed": 18,
                "init_brv": 900, "max_brv": 2100, "element": ElementType.NEUTRAL
            },
            EnemyType.HOBGOBLIN: {
                "max_hp": 140, "max_mp": 80, "attack": 32, "defense": 25,
                "magic_power": 35, "magic_defense": 30, "speed": 35,
                "init_brv": 720, "max_brv": 1500, "element": ElementType.LIGHTNING  # 번개술사
            },
            EnemyType.WIGHT: {
                "max_hp": 160, "max_mp": 90, "attack": 35, "defense": 28,
                "magic_power": 40, "magic_defense": 35, "speed": 25,
                "init_brv": 760, "max_brv": 1680, "element": ElementType.DARK  # 강력한 언데드
            },
            EnemyType.WRAITH: {
                "max_hp": 120, "max_mp": 100, "attack": 30, "defense": 20,
                "magic_power": 45, "magic_defense": 40, "speed": 45,
                "init_brv": 720, "max_brv": 1440, "element": ElementType.DARK  # 영체
            },
            EnemyType.GARGOYLE: {
                "max_hp": 180, "max_mp": 60, "attack": 38, "defense": 40,
                "magic_power": 25, "magic_defense": 35, "speed": 30,
                "init_brv": 780, "max_brv": 1740, "element": ElementType.EARTH  # 석상
            },
            EnemyType.MINOTAUR: {
                "max_hp": 220, "max_mp": 50, "attack": 48, "defense": 35,
                "magic_power": 20, "magic_defense": 25, "speed": 28,
                "init_brv": 840, "max_brv": 1920, "element": ElementType.NEUTRAL
            },
            EnemyType.CENTAUR: {
                "max_hp": 170, "max_mp": 70, "attack": 42, "defense": 32,
                "magic_power": 30, "magic_defense": 28, "speed": 42,
                "init_brv": 760, "max_brv": 1680, "element": ElementType.WIND  # 바람의 궁수
            },
            EnemyType.HARPY: {
                "max_hp": 130, "max_mp": 85, "attack": 36, "defense": 22,
                "magic_power": 38, "magic_defense": 30, "speed": 50,
                "init_brv": 720, "max_brv": 1440, "element": ElementType.WIND  # 바람 하피
            },
            EnemyType.BASILISK: {
                "max_hp": 190, "max_mp": 95, "attack": 40, "defense": 38,
                "magic_power": 42, "magic_defense": 40, "speed": 32,
                "init_brv": 800, "max_brv": 1800, "element": ElementType.POISON  # 독 바실리스크
            },
            EnemyType.FIRE_SALAMANDER: {
                "max_hp": 160, "max_mp": 80, "attack": 38, "defense": 30,
                "magic_power": 45, "magic_defense": 35, "speed": 35,
                "init_brv": 740, "max_brv": 1560, "element": ElementType.FIRE  # 화염 도롱뇽
            },
            EnemyType.ICE_GOLEM: {
                "max_hp": 200, "max_mp": 60, "attack": 35, "defense": 50,
                "magic_power": 30, "magic_defense": 45, "speed": 20,
                "init_brv": 800, "max_brv": 1800, "element": ElementType.ICE  # 얼음 골렘
            },
            
            # 고급 몬스터 (21-30층)
            EnemyType.DRAKE: {
                "max_hp": 350, "max_mp": 120, "attack": 60, "defense": 50,
                "magic_power": 55, "magic_defense": 45, "speed": 40,
                "init_brv": 1200, "max_brv": 3000, "element": ElementType.FIRE  # 화염 드레이크
            },
            EnemyType.CHIMERA: {
                "max_hp": 320, "max_mp": 140, "attack": 58, "defense": 45,
                "magic_power": 60, "magic_defense": 50, "speed": 38,
                "init_brv": 1160, "max_brv": 2880, "element": ElementType.FIRE  # 화염 키메라
            },
            EnemyType.MANTICORE: {
                "max_hp": 280, "max_mp": 110, "attack": 55, "defense": 40,
                "magic_power": 45, "magic_defense": 42, "speed": 45,
                "init_brv": 1100, "max_brv": 2520, "element": ElementType.POISON  # 독침 맨티코어
            },
            EnemyType.GRIFFON: {
                "max_hp": 260, "max_mp": 100, "attack": 52, "defense": 38,
                "magic_power": 40, "magic_defense": 45, "speed": 55,
                "init_brv": 1040, "max_brv": 2400, "element": ElementType.WIND  # 폭풍 그리폰
            },
            EnemyType.WYVERN: {
                "max_hp": 300, "max_mp": 130, "attack": 56, "defense": 42,
                "magic_power": 50, "magic_defense": 48, "speed": 48,
                "init_brv": 1080, "max_brv": 2700, "element": ElementType.LIGHTNING  # 번개 와이번
            },
            EnemyType.LICH: {
                "max_hp": 240, "max_mp": 200, "attack": 45, "defense": 35,
                "magic_power": 80, "magic_defense": 70, "speed": 35,
                "init_brv": 960, "max_brv": 2280, "element": ElementType.DARK  # 어둠 리치
            },
            EnemyType.VAMPIRE: {
                "max_hp": 280, "max_mp": 150, "attack": 54, "defense": 40,
                "magic_power": 65, "magic_defense": 55, "speed": 50,
                "init_brv": 1080, "max_brv": 2520, "element": ElementType.DARK  # 어둠 뱀파이어
            },
            EnemyType.DEMON: {
                "max_hp": 320, "max_mp": 160, "attack": 58, "defense": 45,
                "magic_power": 70, "magic_defense": 60, "speed": 42,
                "init_brv": 1160, "max_brv": 2880, "element": ElementType.DARK  # 지옥 데몬
            },
            EnemyType.DEVIL: {
                "max_hp": 340, "max_mp": 180, "attack": 62, "defense": 48,
                "magic_power": 75, "magic_defense": 65, "speed": 40,
                "init_brv": 1220, "max_brv": 3000, "element": ElementType.DARK  # 지옥 데빌
            },
            EnemyType.ARCHLICH: {
                "max_hp": 280, "max_mp": 250, "attack": 50, "defense": 40,
                "magic_power": 90, "magic_defense": 80, "speed": 38,
                "init_brv": 1120, "max_brv": 2520, "element": ElementType.DARK  # 아치리치
            },
            
            # 최고급 몬스터 (31-40층)
            EnemyType.DRAGON: {
                "max_hp": 500, "max_mp": 200, "attack": 80, "defense": 70,
                "magic_power": 85, "magic_defense": 75, "speed": 50,
                "init_brv": 1500, "max_brv": 4500, "element": ElementType.FIRE  # 고대 화염룡
            },
            EnemyType.BALROG: {
                "max_hp": 480, "max_mp": 180, "attack": 85, "defense": 65,
                "magic_power": 80, "magic_defense": 70, "speed": 45,
                "init_brv": 1440, "max_brv": 4200, "element": ElementType.FIRE  # 화염 발록
            },
            EnemyType.KRAKEN: {
                "max_hp": 450, "max_mp": 220, "attack": 75, "defense": 60,
                "magic_power": 90, "magic_defense": 80, "speed": 40,
                "init_brv": 1350, "max_brv": 3900, "element": ElementType.WATER  # 바다 크라켄
            },
            EnemyType.PHOENIX: {
                "max_hp": 350, "max_mp": 250, "attack": 70, "defense": 55,
                "magic_power": 95, "magic_defense": 85, "speed": 60,
                "init_brv": 1260, "max_brv": 3300, "element": ElementType.FIRE  # 불사조
            },
            EnemyType.STORM_BIRD: {
                "max_hp": 380, "max_mp": 200, "attack": 72, "defense": 50,
                "magic_power": 88, "magic_defense": 75, "speed": 70,
                "init_brv": 1320, "max_brv": 3600, "element": ElementType.LIGHTNING  # 폭풍새
            },
            
            # 전설급 몬스터 (41-50층)
            EnemyType.ELDER_DRAGON: {
                "max_hp": 800, "max_mp": 300, "attack": 120, "defense": 100,
                "magic_power": 130, "magic_defense": 110, "speed": 60,
                "init_brv": 1800, "max_brv": 7500, "element": ElementType.FIRE  # 엘더 드래곤
            },
            EnemyType.TITAN: {
                "max_hp": 900, "max_mp": 250, "attack": 140, "defense": 120,
                "magic_power": 100, "magic_defense": 90, "speed": 40,
                "init_brv": 1980, "max_brv": 8400, "element": ElementType.EARTH  # 대지 타이탄
            },
            EnemyType.VOID_LORD: {
                "max_hp": 700, "max_mp": 400, "attack": 100, "defense": 80,
                "magic_power": 150, "magic_defense": 130, "speed": 55,
                "init_brv": 1680, "max_brv": 6600, "element": ElementType.DARK  # 공허 군주
            },
            EnemyType.VOID_EMPEROR: {
                "max_hp": 1000, "max_mp": 500, "attack": 150, "defense": 120,
                "magic_power": 180, "magic_defense": 150, "speed": 65,
                "init_brv": 2100, "max_brv": 9000, "element": ElementType.DARK  # 공허 황제
            },
            EnemyType.CHAOS_BEAST: {
                "max_hp": 850, "max_mp": 350, "attack": 130, "defense": 90,
                "magic_power": 140, "magic_defense": 100, "speed": 70,
                "init_brv": 1890, "max_brv": 7800, "element": ElementType.NEUTRAL  # 혼돈 야수
            },
            
            # 특수 원소형 몬스터들
            EnemyType.ELEMENTAL: {
                "max_hp": 200, "max_mp": 250, "attack": 35, "defense": 30,
                "magic_power": 85, "magic_defense": 80, "speed": 38,
                "init_brv": 800, "max_brv": 1800, "element": ElementType.FIRE  # 기본 화염, 소환시 변경됨
            }
        }
        
        # 기본값 (정의되지 않은 몬스터용)
        default_stats = {
            "max_hp": 100, "max_mp": 40, "attack": 20, "defense": 15,
            "magic_power": 12, "magic_defense": 10, "speed": 30,
            "init_brv": 400, "max_brv": 900, "element": ElementType.NEUTRAL
        }
        
        return stats_table.get(self.enemy_type, default_stats)
    
    def _get_rank_multiplier(self) -> float:
        """등급별 스탯 배율 (더 합리적으로 조정)"""
        multipliers = {
            EnemyRank.MINION: 0.8,      # 0.7 → 0.8
            EnemyRank.REGULAR: 1.0,
            EnemyRank.ELITE: 1.2,       # 1.3 → 1.2  
            EnemyRank.CHAMPION: 1.4,    # 1.6 → 1.4
            EnemyRank.BOSS: 1.7,        # 2.0 → 1.7
            EnemyRank.RAID_BOSS: 2.0,   # 2.5 → 2.0
            EnemyRank.LEGENDARY: 2.3,   # 3.0 → 2.3
            EnemyRank.MYTHIC: 2.7       # 4.0 → 2.7
        }
        return multipliers.get(self.rank, 1.0)
    
    def _get_enemy_critical_rate(self) -> float:
        """적 타입별 크리티컬 확률"""
        base_critical_by_type = {
            # 일반 몬스터 (낮은 크리티컬)
            EnemyType.GOBLIN: 5.0,
            EnemyType.ORC: 8.0,
            EnemyType.SKELETON: 6.0,
            EnemyType.ZOMBIE: 4.0,
            EnemyType.SPIDER: 12.0,  # 독거미는 크리티컬 높음
            EnemyType.RAT: 7.0,
            EnemyType.BAT: 10.0,     # 빠른 적은 크리티컬 높음
            EnemyType.WOLF: 9.0,
            EnemyType.SLIME: 3.0,    # 슬라임은 크리티컬 낮음
            EnemyType.IMP: 11.0,
            
            # 중급 몬스터
            EnemyType.TROLL: 7.0,
            EnemyType.OGRE: 9.0,
            EnemyType.HOBGOBLIN: 8.0,
            EnemyType.WIGHT: 6.0,
            EnemyType.WRAITH: 13.0,   # 영체는 크리티컬 높음
            EnemyType.GARGOYLE: 5.0,
            EnemyType.MINOTAUR: 11.0,
            EnemyType.CENTAUR: 10.0,
            EnemyType.HARPY: 14.0,    # 하피는 크리티컬 높음
            EnemyType.BASILISK: 12.0,
            
            # 고급 몬스터 (높은 크리티컬)
            EnemyType.DRAKE: 15.0,
            EnemyType.CHIMERA: 13.0,
            EnemyType.MANTICORE: 16.0,
            EnemyType.GRIFFON: 14.0,
            EnemyType.WYVERN: 17.0,
            EnemyType.LICH: 10.0,     # 마법사형은 낮음
            EnemyType.VAMPIRE: 18.0,  # 뱀파이어는 매우 높음
            EnemyType.DEMON: 15.0,
            EnemyType.DEVIL: 16.0,
            EnemyType.ELEMENTAL: 8.0,
        }
        
        base_rate = base_critical_by_type.get(self.enemy_type, 8.0)
        
        # 등급별 크리티컬 보너스
        rank_bonus = {
            EnemyRank.MINION: -2.0,
            EnemyRank.REGULAR: 0.0,
            EnemyRank.ELITE: 2.0,
            EnemyRank.CHAMPION: 4.0,
            EnemyRank.BOSS: 6.0,
            EnemyRank.RAID_BOSS: 8.0,
            EnemyRank.LEGENDARY: 10.0,
            EnemyRank.MYTHIC: 12.0
        }.get(self.rank, 0.0)
        
        return max(0.0, min(30.0, base_rate + rank_bonus))
    
    def _get_enemy_accuracy(self) -> float:
        """적 타입별 명중률"""
        base_accuracy_by_type = {
            # 명중률이 높은 적들
            EnemyType.SPIDER: 90.0,    # 거미는 정확함
            EnemyType.HARPY: 88.0,     # 하피는 정확함
            EnemyType.BASILISK: 92.0,  # 바실리스크는 매우 정확
            EnemyType.VAMPIRE: 90.0,   # 뱀파이어는 정확함
            EnemyType.DEMON: 88.0,     # 데몬은 정확함
            
            # 중간 명중률
            EnemyType.GOBLIN: 75.0,
            EnemyType.ORC: 80.0,
            EnemyType.WOLF: 82.0,
            EnemyType.TROLL: 78.0,
            EnemyType.OGRE: 76.0,
            EnemyType.MINOTAUR: 85.0,
            EnemyType.CENTAUR: 87.0,
            
            # 낮은 명중률
            EnemyType.SKELETON: 70.0,  # 뼈다귀라 부정확
            EnemyType.ZOMBIE: 65.0,    # 좀비는 느리고 부정확
            EnemyType.SLIME: 60.0,     # 슬라임은 부정확
            EnemyType.BAT: 70.0,       # 박쥐는 작아서 부정확
        }
        
        base_accuracy = base_accuracy_by_type.get(self.enemy_type, 80.0)
        
        # 등급별 명중률 보너스
        rank_bonus = {
            EnemyRank.MINION: -10.0,
            EnemyRank.REGULAR: 0.0,
            EnemyRank.ELITE: 5.0,
            EnemyRank.CHAMPION: 8.0,
            EnemyRank.BOSS: 12.0,
            EnemyRank.RAID_BOSS: 15.0,
            EnemyRank.LEGENDARY: 18.0,
            EnemyRank.MYTHIC: 20.0
        }.get(self.rank, 0.0)
        
        return max(50.0, min(95.0, base_accuracy + rank_bonus))
    
    def _get_enemy_evasion(self) -> float:
        """적 타입별 회피율"""
        base_evasion_by_type = {
            # 높은 회피율 (기존의 1/3로 감소)
            EnemyType.BAT: 8.0,       # 박쥐는 빠름 (25 -> 8)
            EnemyType.SPIDER: 7.0,    # 거미는 민첩 (20 -> 7)
            EnemyType.IMP: 7.5,       # 임프는 민첩 (22 -> 7.5)
            EnemyType.WRAITH: 10.0,   # 영체는 회피 높음 (30 -> 10)
            EnemyType.HARPY: 9.0,     # 하피는 날아다님 (28 -> 9)
            EnemyType.VAMPIRE: 8.0,   # 뱀파이어는 민첩 (25 -> 8)
            
            # 중간 회피율 (기존의 1/3로 감소)
            EnemyType.GOBLIN: 5.0,    # (15 -> 5)
            EnemyType.WOLF: 6.0,      # (18 -> 6)
            EnemyType.CENTAUR: 5.5,   # (16 -> 5.5)
            EnemyType.DEMON: 7.0,     # (20 -> 7)
            
            # 낮은 회피율 (기존의 1/3로 감소)
            EnemyType.ORC: 3.0,       # 오크는 둔함 (8 -> 3)
            EnemyType.TROLL: 2.0,     # 트롤은 매우 둔함 (5 -> 2)
            EnemyType.OGRE: 2.5,      # 오거도 둔함 (6 -> 2.5)
            EnemyType.SKELETON: 3.5,  # 스켈레톤은 보통 (10 -> 3.5)
            EnemyType.ZOMBIE: 1.0,    # 좀비는 매우 둔함 (3 -> 1)
            EnemyType.SLIME: 4.0,     # 슬라임은 의외로 회피 (12 -> 4)
            EnemyType.GARGOYLE: 2.5,  # 가고일은 무거움 (7 -> 2.5)
            EnemyType.MINOTAUR: 3.0,  # 미노타우로스는 큼 (9 -> 3)
        }
        
        base_evasion = base_evasion_by_type.get(self.enemy_type, 4.0)  # 기본값도 12 -> 4로 감소
        
        # 등급별 회피율 보너스 (기존의 1/2로 감소)
        rank_bonus = {
            EnemyRank.MINION: -1.0,    # -3 -> -1
            EnemyRank.REGULAR: 0.0,
            EnemyRank.ELITE: 1.0,      # 2 -> 1
            EnemyRank.CHAMPION: 2.0,   # 4 -> 2
            EnemyRank.BOSS: 3.0,       # 6 -> 3
            EnemyRank.RAID_BOSS: 4.0,  # 8 -> 4
            EnemyRank.LEGENDARY: 5.0,  # 10 -> 5
            EnemyRank.MYTHIC: 6.0      # 12 -> 6
        }.get(self.rank, 0.0)
        
        return max(0.0, min(15.0, base_evasion + rank_bonus))  # 최대값도 40 -> 15로 감소
    
    def _determine_ai_type(self) -> str:
        """적 타입별 논리적 AI 타입 결정"""
        # 적 타입별 고정 AI 패턴
        ai_by_type = {
            # 일반 몬스터 - 단순한 AI
            EnemyType.GOBLIN: "aggressive",     # 고블린: 공격적
            EnemyType.ORC: "berserker",         # 오크: 광폭
            EnemyType.SKELETON: "defensive",    # 스켈레톤: 방어적
            EnemyType.ZOMBIE: "aggressive",     # 좀비: 느리지만 공격적
            EnemyType.SPIDER: "assassin",       # 거미: 독 암살형
            EnemyType.RAT: "adaptive",          # 쥐: 적응형 (빠름)
            EnemyType.BAT: "assassin",          # 박쥐: 민첩한 암살형
            EnemyType.WOLF: "tactical",         # 늑대: 무리 전술
            EnemyType.SLIME: "defensive",       # 슬라임: 방어적
            EnemyType.IMP: "caster",            # 임프: 마법사형
            
            # 중급 몬스터 - 복잡한 AI
            EnemyType.TROLL: "berserker",       # 트롤: 광폭
            EnemyType.OGRE: "aggressive",       # 오거: 단순 공격
            EnemyType.HOBGOBLIN: "caster",      # 홉고블린: 마법사
            EnemyType.WIGHT: "caster",          # 와이트: 언데드 마법사
            EnemyType.WRAITH: "assassin",       # 레이스: 영체 암살자
            EnemyType.GARGOYLE: "defensive",    # 가고일: 방어적
            EnemyType.MINOTAUR: "berserker",    # 미노타우로스: 광폭
            EnemyType.CENTAUR: "tactical",      # 켄타우로스: 전술적
            EnemyType.HARPY: "assassin",        # 하피: 빠른 암살
            EnemyType.BASILISK: "caster",       # 바실리스크: 독 마법
            EnemyType.FIRE_SALAMANDER: "caster", # 화염도롱뇽: 화염 마법
            EnemyType.ICE_GOLEM: "defensive",   # 얼음골렘: 방어형
            
            # 고급 몬스터 - 지능적 AI
            EnemyType.DRAKE: "tactical",        # 드레이크: 전술적
            EnemyType.CHIMERA: "adaptive",      # 키메라: 적응형
            EnemyType.MANTICORE: "assassin",    # 맨티코어: 독침 암살
            EnemyType.GRIFFON: "tactical",      # 그리폰: 공중 전술
            EnemyType.WYVERN: "caster",         # 와이번: 번개 마법
            EnemyType.LICH: "caster",           # 리치: 강력한 마법사
            EnemyType.VAMPIRE: "assassin",      # 뱀파이어: 흡혈 암살
            EnemyType.DEMON: "tactical",        # 데몬: 지능적 전술
            EnemyType.DEVIL: "adaptive",        # 데빌: 고도의 적응형
            EnemyType.ARCHLICH: "caster",       # 아치리치: 최고급 마법사
            
            # 최고급 몬스터 - 최고 지능
            EnemyType.DRAGON: "adaptive",       # 드래곤: 최고 지능
            EnemyType.BALROG: "berserker",      # 발록: 악마적 광폭
            EnemyType.KRAKEN: "tactical",       # 크라켄: 바다의 전술가
            EnemyType.PHOENIX: "caster",        # 피닉스: 불사조 마법
            EnemyType.STORM_BIRD: "caster",     # 폭풍새: 번개 마법
            
            # 전설급 몬스터 - 신급 지능
            EnemyType.ELDER_DRAGON: "adaptive", # 엘더드래곤: 완벽한 적응
            EnemyType.TITAN: "tactical",        # 타이탄: 신적 전술
            EnemyType.VOID_LORD: "caster",      # 공허군주: 공허 마법
            EnemyType.VOID_EMPEROR: "adaptive", # 공허황제: 궁극 적응
            EnemyType.CHAOS_BEAST: "berserker", # 혼돈야수: 순수 파괴
            
            # 특수
            EnemyType.ELEMENTAL: "caster",      # 엘리멘탈: 원소 마법
        }
        
        # 기본 AI (없는 경우)
        base_ai = ai_by_type.get(self.enemy_type, "aggressive")
        
        # 등급에 따른 AI 업그레이드 (높은 등급일수록 지능적)
        if self.rank in [EnemyRank.BOSS, EnemyRank.RAID_BOSS, EnemyRank.LEGENDARY, EnemyRank.MYTHIC]:
            if base_ai == "aggressive":
                return "tactical"  # 공격적 → 전술적
            elif base_ai == "defensive":
                return "adaptive"  # 방어적 → 적응형
            elif base_ai == "berserker":
                return "tactical"  # 광폭 → 전술적 (보스는 똑똑함)
        
        return base_ai
    
    def _get_enemy_skills_legacy(self) -> List[Dict]:
        """적 타입별 전용 스킬 (Legacy)"""
        enemy_skills = {
            # 일반 몬스터 스킬
            EnemyType.GOBLIN: [
                {"name": "투석", "type": "attack", "power": 0.8, "mp_cost": 0, "element": ElementType.NEUTRAL},
                {"name": "기습", "type": "attack", "power": 1.2, "mp_cost": 5, "element": ElementType.NEUTRAL, "critical_bonus": 5.0},
            ],
            EnemyType.ORC: [
                {"name": "야만적 일격", "type": "attack", "power": 1.4, "mp_cost": 8, "element": ElementType.NEUTRAL},
                {"name": "포효", "type": "debuff", "power": 0.0, "mp_cost": 10, "status": "fear"},
            ],
            EnemyType.SKELETON: [
                {"name": "뼈 투창", "type": "attack", "power": 0.9, "mp_cost": 3, "element": ElementType.NEUTRAL},
                {"name": "언데드의 저주", "type": "debuff", "power": 0.0, "mp_cost": 12, "status": "curse"},
            ],
            EnemyType.ZOMBIE: [
                {"name": "감염", "type": "attack", "power": 0.7, "mp_cost": 5, "element": ElementType.POISON, "status": "poison"},
                {"name": "재생", "type": "heal", "power": 0.3, "mp_cost": 8, "target": "self"},
            ],
            EnemyType.SPIDER: [
                {"name": "독니 공격", "type": "attack", "power": 0.8, "mp_cost": 4, "element": ElementType.POISON, "status": "poison"},
                {"name": "거미줄", "type": "debuff", "power": 0.0, "mp_cost": 6, "status": "slow"},
            ],
            EnemyType.RAT: [
                {"name": "빠른 물기", "type": "attack", "power": 0.6, "mp_cost": 2, "element": ElementType.NEUTRAL, "accuracy_bonus": 10.0},
                {"name": "질병", "type": "attack", "power": 0.5, "mp_cost": 8, "element": ElementType.POISON, "status": "disease"},
            ],
            EnemyType.BAT: [
                {"name": "음파 공격", "type": "attack", "power": 0.7, "mp_cost": 5, "element": ElementType.NEUTRAL, "target": "all"},
                {"name": "흡혈", "type": "attack", "power": 0.9, "mp_cost": 10, "element": ElementType.DARK, "drain": True},
            ],
            EnemyType.WOLF: [
                {"name": "무리 사냥", "type": "attack", "power": 1.1, "mp_cost": 6, "element": ElementType.NEUTRAL},
                {"name": "늑대의 포효", "type": "buff", "power": 0.0, "mp_cost": 8, "status": "attack_up"},
            ],
            EnemyType.SLIME: [
                {"name": "산성 공격", "type": "attack", "power": 0.8, "mp_cost": 4, "element": ElementType.POISON},
                {"name": "분열", "type": "special", "power": 0.0, "mp_cost": 15, "effect": "summon_minion"},
            ],
            EnemyType.IMP: [
                {"name": "화염구", "type": "attack", "power": 1.0, "mp_cost": 8, "element": ElementType.FIRE},
                {"name": "순간이동", "type": "buff", "power": 0.0, "mp_cost": 12, "status": "evasion_up"},
            ],
            
            # 중급 몬스터 스킬
            EnemyType.TROLL: [
                {"name": "거대한 주먹", "type": "attack", "power": 1.6, "mp_cost": 10, "element": ElementType.EARTH},
                {"name": "재생능력", "type": "heal", "power": 0.5, "mp_cost": 15, "target": "self"},
            ],
            EnemyType.OGRE: [
                {"name": "곤봉 휘두르기", "type": "attack", "power": 1.8, "mp_cost": 12, "element": ElementType.NEUTRAL, "target": "all"},
                {"name": "광란", "type": "buff", "power": 0.0, "mp_cost": 10, "status": "berserk"},
            ],
            EnemyType.HOBGOBLIN: [
                {"name": "마법 화살", "type": "attack", "power": 1.2, "mp_cost": 8, "element": ElementType.LIGHTNING},
                {"name": "전술 지휘", "type": "buff", "power": 0.0, "mp_cost": 15, "status": "all_stats_up", "target": "allies"},
            ],
            EnemyType.WIGHT: [
                {"name": "생명력 흡수", "type": "attack", "power": 1.1, "mp_cost": 12, "element": ElementType.DARK, "drain": True},
                {"name": "공포의 시선", "type": "debuff", "power": 0.0, "mp_cost": 10, "status": "fear"},
            ],
            EnemyType.WRAITH: [
                {"name": "유령 접촉", "type": "attack", "power": 1.3, "mp_cost": 15, "element": ElementType.DARK, "penetration": True},
                {"name": "영체화", "type": "buff", "power": 0.0, "mp_cost": 20, "status": "intangible"},
            ],
            EnemyType.GARGOYLE: [
                {"name": "석화의 시선", "type": "debuff", "power": 0.0, "mp_cost": 18, "status": "petrify"},
                {"name": "날개 공격", "type": "attack", "power": 1.4, "mp_cost": 10, "element": ElementType.WIND},
            ],
            EnemyType.MINOTAUR: [
                {"name": "돌진", "type": "attack", "power": 2.0, "mp_cost": 15, "element": ElementType.NEUTRAL, "critical_bonus": 10.0},
                {"name": "미궁의 주인", "type": "debuff", "power": 0.0, "mp_cost": 20, "status": "confusion", "target": "all"},
            ],
            EnemyType.CENTAUR: [
                {"name": "연속 사격", "type": "attack", "power": 0.8, "mp_cost": 12, "element": ElementType.NEUTRAL, "hits": 3},
                {"name": "말발굽 차기", "type": "attack", "power": 1.5, "mp_cost": 8, "element": ElementType.EARTH},
            ],
            EnemyType.HARPY: [
                {"name": "귀를 찢는 노래", "type": "debuff", "power": 0.0, "mp_cost": 15, "status": "silence", "target": "all"},
                {"name": "회오리바람", "type": "attack", "power": 1.3, "mp_cost": 18, "element": ElementType.WIND, "target": "all"},
            ],
            EnemyType.BASILISK: [
                {"name": "독 브레스", "type": "attack", "power": 1.2, "mp_cost": 20, "element": ElementType.POISON, "target": "all"},
                {"name": "석화의 눈", "type": "debuff", "power": 0.0, "mp_cost": 25, "status": "petrify"},
            ],
            
            # 고급 몬스터 스킬
            EnemyType.DRAKE: [
                {"name": "화염 브레스", "type": "attack", "power": 1.8, "mp_cost": 25, "element": ElementType.FIRE, "target": "all"},
                {"name": "용의 위압", "type": "debuff", "power": 0.0, "mp_cost": 20, "status": "fear", "target": "all"},
                {"name": "비행", "type": "buff", "power": 0.0, "mp_cost": 15, "status": "flying"},
            ],
            EnemyType.CHIMERA: [
                {"name": "삼중 브레스", "type": "attack", "power": 1.5, "mp_cost": 30, "element": ElementType.FIRE, "hits": 3},
                {"name": "독꼬리", "type": "attack", "power": 1.2, "mp_cost": 15, "element": ElementType.POISON},
                {"name": "사자의 포효", "type": "debuff", "power": 0.0, "mp_cost": 18, "status": "fear", "target": "all"},
            ],
            EnemyType.VAMPIRE: [
                {"name": "혈액 흡수", "type": "attack", "power": 1.4, "mp_cost": 20, "element": ElementType.DARK, "drain": True},
                {"name": "매혹", "type": "debuff", "power": 0.0, "mp_cost": 25, "status": "charm"},
                {"name": "박쥐 변신", "type": "buff", "power": 0.0, "mp_cost": 30, "status": "evasion_up"},
                {"name": "재생", "type": "heal", "power": 0.8, "mp_cost": 18, "target": "self"},
            ],
            EnemyType.LICH: [
                {"name": "데스 레이", "type": "attack", "power": 2.2, "mp_cost": 35, "element": ElementType.DARK},
                {"name": "언데드 소환", "type": "special", "power": 0.0, "mp_cost": 40, "effect": "summon_undead"},
                {"name": "시간 정지", "type": "debuff", "power": 0.0, "mp_cost": 50, "status": "stop", "target": "all"},
                {"name": "마나 흡수", "type": "special", "power": 0.0, "mp_cost": 20, "effect": "mana_drain"},
            ],
        }
        
        base_skills = enemy_skills.get(self.enemy_type, [
            {"name": "기본 공격", "type": "attack", "power": 1.0, "mp_cost": 0, "element": ElementType.NEUTRAL}
        ])
        
        # 등급에 따른 스킬 강화
        enhanced_skills = []
        for skill in base_skills:
            enhanced_skill = skill.copy()
            
            # 등급별 파워 보너스
            rank_power_bonus = {
                EnemyRank.MINION: 0.8,
                EnemyRank.REGULAR: 1.0,
                EnemyRank.ELITE: 1.2,
                EnemyRank.CHAMPION: 1.4,
                EnemyRank.BOSS: 1.6,
                EnemyRank.RAID_BOSS: 1.8,
                EnemyRank.LEGENDARY: 2.0,
                EnemyRank.MYTHIC: 2.2
            }.get(self.rank, 1.0)
            
            enhanced_skill["power"] *= rank_power_bonus
            enhanced_skills.append(enhanced_skill)
        
        return enhanced_skills
    
    def _calculate_exp_reward(self) -> int:
        """경험치 보상 계산"""
        base_exp = 10 + self.floor * 2
        rank_bonus = {
            EnemyRank.MINION: 0.5,
            EnemyRank.REGULAR: 1.0,
            EnemyRank.ELITE: 1.5,
            EnemyRank.CHAMPION: 2.0,
            EnemyRank.BOSS: 3.0,
            EnemyRank.RAID_BOSS: 5.0,
            EnemyRank.LEGENDARY: 8.0,
            EnemyRank.MYTHIC: 12.0
        }
        return int(base_exp * rank_bonus.get(self.rank, 1.0))
    
    def _calculate_gold_reward(self) -> int:
        """골드 보상 계산"""
        base_gold = 5 + self.floor
        rank_bonus = {
            EnemyRank.MINION: 0.7,
            EnemyRank.REGULAR: 1.0,
            EnemyRank.ELITE: 1.4,
            EnemyRank.CHAMPION: 2.0,
            EnemyRank.BOSS: 3.5,
            EnemyRank.RAID_BOSS: 6.0,
            EnemyRank.LEGENDARY: 10.0,
            EnemyRank.MYTHIC: 15.0
        }
        return int(base_gold * rank_bonus.get(self.rank, 1.0) * random.uniform(0.8, 1.2))
    
    def _determine_drops(self) -> List[str]:
        """드롭 아이템 결정"""
        drops = []
        
        # 등급별 드롭 확률
        drop_chance = {
            EnemyRank.MINION: 0.1,
            EnemyRank.REGULAR: 0.2,
            EnemyRank.ELITE: 0.4,
            EnemyRank.CHAMPION: 0.6,
            EnemyRank.BOSS: 0.8,
            EnemyRank.RAID_BOSS: 1.0,
            EnemyRank.LEGENDARY: 1.0,
            EnemyRank.MYTHIC: 1.0
        }
        
        if random.random() < drop_chance.get(self.rank, 0.1):
            # 적 타입별 특수 드롭
            type_drops = {
                EnemyType.FIRE_SALAMANDER: ["화염의정수", "불꽃구슬"],
                EnemyType.ICE_GOLEM: ["얼음핵", "서리조각"],
                EnemyType.DRAGON: ["용의비늘", "용심장", "용의보석"],
                EnemyType.LICH: ["사령술서", "언데드의정수"],
            }
            
            specific_drops = type_drops.get(self.enemy_type, ["일반드롭"])
            drops.extend(random.sample(specific_drops, min(len(specific_drops), 2)))
        
        return drops
    
    def get_enemy_skill_power(self, base_power: float) -> float:
        """적 스킬 위력에 배수 적용"""
        try:
            # NewSkillSystem에서 적 스킬 배수 가져오기
            from .new_skill_system import skill_system
            return base_power * skill_system.enemy_skill_power_multiplier
        except ImportError:
            # 폴백: 1.3배 고정 배수
            return base_power * 1.3
    
    def get_modified_skill(self, skill: Dict) -> Dict:
        """적 스킬에 배수를 적용하여 반환"""
        modified_skill = skill.copy()
        if 'power' in modified_skill:
            original_power = modified_skill['power']
            modified_skill['power'] = self.get_enemy_skill_power(original_power)
        return modified_skill
    
    def _get_enemy_skills(self) -> List[Dict]:
        """적 전용 스킬 (모든 적 타입에 스킬 추가)"""
        skills = []
        
        # 기본 공격 (모든 적이 보유) - BRV와 HP 공격 모두
        skills.append({
            "name": "일반공격",
            "type": "brv_attack",
            "power": 100,
            "accuracy": 85,
            "mp_cost": 0
        })
        
        skills.append({
            "name": "직접타격",
            "type": "hp_attack", 
            "power": 80,
            "accuracy": 75,
            "mp_cost": 0,  # 기본 공격은 MP 소모 없음
            "requires_brv": True  # BRV가 일정 이상 있어야 사용 가능
        })
        
        # 적 타입별 특수 스킬
        enemy_skill_sets = {
            # 일반 몬스터 스킬
            EnemyType.GOBLIN: [
                {"name": "투석", "type": "brv_attack", "power": 80, "mp_cost": 3, "element": ElementType.NEUTRAL},
                {"name": "기습", "type": "brv_attack", "power": 120, "mp_cost": 5, "critical_bonus": 15.0},
                {"name": "독침", "type": "hp_attack", "power": 90, "mp_cost": 8, "requires_brv": True},
            ],
            EnemyType.ORC: [
                {"name": "야만적일격", "type": "brv_attack", "power": 140, "mp_cost": 8},
                {"name": "포효", "type": "debuff", "status": "fear", "mp_cost": 10},
                {"name": "전력타격", "type": "hp_attack", "power": 120, "mp_cost": 12, "requires_brv": True},
            ],
            EnemyType.SKELETON: [
                {"name": "뼈투창", "type": "brv_attack", "power": 90, "mp_cost": 4},
                {"name": "언데드저주", "type": "debuff", "status": "curse", "mp_cost": 12},
                {"name": "뼈창찌르기", "type": "hp_attack", "power": 100, "mp_cost": 10, "requires_brv": True},
            ],
            EnemyType.ZOMBIE: [
                {"name": "감염", "type": "brv_attack", "power": 70, "mp_cost": 5, "element": ElementType.POISON, "status": "poison"},
                {"name": "재생", "type": "heal", "power": 30, "mp_cost": 8, "target": "self"},
                {"name": "좀비물기", "type": "hp_attack", "power": 85, "mp_cost": 9, "requires_brv": True, "status": "disease"},
            ],
            EnemyType.SPIDER: [
                {"name": "독니공격", "type": "brv_attack", "power": 80, "mp_cost": 4, "element": ElementType.POISON, "status": "poison"},
                {"name": "거미줄", "type": "debuff", "status": "slow", "mp_cost": 6},
                {"name": "맹독주입", "type": "hp_attack", "power": 95, "mp_cost": 10, "requires_brv": True, "element": ElementType.POISON},
            ],
            EnemyType.RAT: [
                {"name": "빠른물기", "type": "brv_attack", "power": 60, "mp_cost": 2, "accuracy": 95},
                {"name": "질병", "type": "debuff", "power": 50, "mp_cost": 8, "status": "disease"},
                {"name": "급소물기", "type": "hp_attack", "power": 75, "mp_cost": 7, "requires_brv": True, "critical_bonus": 10.0},
            ],
            EnemyType.BAT: [
                {"name": "음파공격", "type": "brv_attack", "power": 70, "mp_cost": 5, "target": "all"},
                {"name": "흡혈", "type": "brv_attack", "power": 90, "mp_cost": 10, "element": ElementType.DARK, "drain": True},
                {"name": "생명흡수", "type": "hp_attack", "power": 100, "mp_cost": 12, "requires_brv": True, "element": ElementType.DARK, "drain": True},
            ],
            EnemyType.WOLF: [
                {"name": "무리사냥", "type": "brv_attack", "power": 110, "mp_cost": 6},
                {"name": "포효", "type": "buff", "status": "attack_up", "mp_cost": 8, "target": "self"},
                {"name": "목물기", "type": "hp_attack", "power": 125, "mp_cost": 10, "requires_brv": True, "critical_bonus": 12.0},
            ],
            EnemyType.SLIME: [
                {"name": "산성공격", "type": "brv_attack", "power": 80, "mp_cost": 4, "element": ElementType.POISON},
                {"name": "분열", "type": "special", "mp_cost": 15, "effect": "summon_minion"},
                {"name": "산성용해", "type": "hp_attack", "power": 105, "mp_cost": 11, "requires_brv": True, "element": ElementType.POISON, "status": "poison"},
            ],
            EnemyType.IMP: [
                {"name": "화염구", "type": "brv_attack", "power": 100, "mp_cost": 8, "element": ElementType.FIRE},
                {"name": "순간이동", "type": "buff", "status": "evasion_up", "mp_cost": 12, "target": "self"},
                {"name": "화염폭발", "type": "hp_attack", "power": 115, "mp_cost": 14, "requires_brv": True, "element": ElementType.FIRE},
            ],
            
            # 중급 몬스터 스킬
            EnemyType.TROLL: [
                {"name": "거대한주먹", "type": "attack", "power": 160, "mp_cost": 12},
                {"name": "땅울림", "type": "attack", "power": 120, "mp_cost": 15, "target": "all"},
            ],
            EnemyType.OGRE: [
                {"name": "야만적분노", "type": "attack", "power": 180, "mp_cost": 15},
                {"name": "위압", "type": "debuff", "status": "fear", "mp_cost": 10, "target": "all"},
            ],
            EnemyType.HOBGOBLIN: [
                {"name": "번개창", "type": "magic_attack", "power": 130, "mp_cost": 18, "element": ElementType.LIGHTNING},
                {"name": "전기장막", "type": "buff", "status": "reflect", "mp_cost": 20, "target": "self"},
            ],
            EnemyType.WIGHT: [
                {"name": "생명흡수", "type": "brv_attack", "power": 120, "mp_cost": 15, "element": ElementType.DARK, "drain": True},
                {"name": "공포의시선", "type": "debuff", "status": "paralysis", "mp_cost": 18},
                {"name": "영혼파괴", "type": "hp_attack", "power": 140, "mp_cost": 20, "requires_brv": True, "element": ElementType.DARK},
            ],
            EnemyType.WRAITH: [
                {"name": "영혼공격", "type": "brv_attack", "power": 110, "mp_cost": 12, "element": ElementType.DARK},
                {"name": "실체화", "type": "buff", "status": "invisible", "mp_cost": 15, "target": "self"},
                {"name": "영혼절단", "type": "hp_attack", "power": 135, "mp_cost": 18, "requires_brv": True, "element": ElementType.DARK, "penetration": True},
            ],
            EnemyType.GARGOYLE: [
                {"name": "돌진", "type": "brv_attack", "power": 140, "mp_cost": 10},
                {"name": "석화시선", "type": "debuff", "status": "petrify", "mp_cost": 20},
                {"name": "돌날개타격", "type": "hp_attack", "power": 160, "mp_cost": 16, "requires_brv": True, "element": ElementType.EARTH},
            ],
            EnemyType.MINOTAUR: [
                {"name": "돌진공격", "type": "brv_attack", "power": 170, "mp_cost": 15},
                {"name": "미궁의포효", "type": "debuff", "status": "confusion", "mp_cost": 12, "target": "all"},
                {"name": "뿔찌르기", "type": "hp_attack", "power": 190, "mp_cost": 20, "requires_brv": True, "critical_bonus": 20.0},
            ],
            EnemyType.CENTAUR: [
                {"name": "바람화살", "type": "brv_attack", "power": 130, "mp_cost": 10, "element": ElementType.WIND},
                {"name": "질풍", "type": "buff", "status": "speed_up", "mp_cost": 12, "target": "self"},
                {"name": "관통화살", "type": "hp_attack", "power": 150, "mp_cost": 16, "requires_brv": True, "element": ElementType.WIND, "penetration": True},
            ],
            EnemyType.HARPY: [
                {"name": "바람날개", "type": "brv_attack", "power": 120, "mp_cost": 12, "element": ElementType.WIND},
                {"name": "유혹의노래", "type": "debuff", "status": "charm", "mp_cost": 15, "target": "all"},
                {"name": "급강하공격", "type": "hp_attack", "power": 145, "mp_cost": 18, "requires_brv": True, "element": ElementType.WIND, "critical_bonus": 15.0},
            ],
            EnemyType.BASILISK: [
                {"name": "독침", "type": "brv_attack", "power": 140, "mp_cost": 15, "element": ElementType.POISON, "status": "poison"},
                {"name": "죽음의시선", "type": "debuff", "status": "instant_death", "mp_cost": 25},
                {"name": "맹독브레스", "type": "hp_attack", "power": 165, "mp_cost": 22, "requires_brv": True, "element": ElementType.POISON, "target": "all"},
            ],
            EnemyType.FIRE_SALAMANDER: [
                {"name": "화염숨결", "type": "brv_attack", "power": 150, "mp_cost": 15, "element": ElementType.FIRE},
                {"name": "열기파동", "type": "debuff", "status": "burn", "mp_cost": 20},
                {"name": "화염폭풍", "type": "hp_attack", "power": 175, "mp_cost": 22, "requires_brv": True, "element": ElementType.FIRE, "target": "all"},
            ],
            EnemyType.ICE_GOLEM: [
                {"name": "냉기폭발", "type": "brv_attack", "power": 140, "mp_cost": 18, "element": ElementType.ICE},
                {"name": "빙결시선", "type": "debuff", "status": "freeze", "mp_cost": 25},
                {"name": "절대영도", "type": "hp_attack", "power": 170, "mp_cost": 25, "requires_brv": True, "element": ElementType.ICE, "target": "all"},
            ],
            
            # 고급 몬스터 스킬
            EnemyType.DRAKE: [
                {"name": "화염숨결", "type": "brv_attack", "power": 200, "mp_cost": 25, "element": ElementType.FIRE},
                {"name": "용린방어", "type": "buff", "status": "defense_up", "mp_cost": 20, "target": "self"},
                {"name": "돌진", "type": "brv_attack", "power": 180, "mp_cost": 15},
                {"name": "용의분노", "type": "hp_attack", "power": 220, "mp_cost": 30, "requires_brv": True, "element": ElementType.FIRE, "critical_bonus": 25.0},
            ],
            EnemyType.CHIMERA: [
                {"name": "삼중공격", "type": "brv_attack", "power": 150, "mp_cost": 20, "hits": 3},
                {"name": "화염숨결", "type": "brv_attack", "power": 190, "mp_cost": 22, "element": ElementType.FIRE},
                {"name": "독꼬리", "type": "brv_attack", "power": 120, "mp_cost": 15, "element": ElementType.POISON, "status": "poison"},
                {"name": "키메라의분노", "type": "hp_attack", "power": 210, "mp_cost": 28, "requires_brv": True, "hits": 2},
            ],
            EnemyType.MANTICORE: [
                {"name": "독침난사", "type": "brv_attack", "power": 160, "mp_cost": 18, "element": ElementType.POISON, "target": "all"},
                {"name": "맹독", "type": "debuff", "status": "deadly_poison", "mp_cost": 20},
                {"name": "독침관통", "type": "hp_attack", "power": 185, "mp_cost": 24, "requires_brv": True, "element": ElementType.POISON, "penetration": True},
            ],
            EnemyType.GRIFFON: [
                {"name": "폭풍날개", "type": "brv_attack", "power": 170, "mp_cost": 20, "element": ElementType.WIND},
                {"name": "급강하", "type": "brv_attack", "power": 190, "mp_cost": 18},
                {"name": "천공강타", "type": "hp_attack", "power": 200, "mp_cost": 26, "requires_brv": True, "element": ElementType.WIND, "critical_bonus": 20.0},
            ],
            EnemyType.WYVERN: [
                {"name": "번개숨결", "type": "brv_attack", "power": 180, "mp_cost": 22, "element": ElementType.LIGHTNING},
                {"name": "전기충격", "type": "debuff", "status": "paralysis", "mp_cost": 15, "target": "all"},
                {"name": "뇌전일섬", "type": "hp_attack", "power": 195, "mp_cost": 28, "requires_brv": True, "element": ElementType.LIGHTNING, "target": "all"},
            ],
            EnemyType.LICH: [
                {"name": "죽음의마법", "type": "brv_attack", "power": 220, "mp_cost": 30, "element": ElementType.DARK},
                {"name": "시체소생", "type": "special", "mp_cost": 40, "effect": "summon_skeleton"},
                {"name": "마나드레인", "type": "debuff", "mp_cost": 25, "effect": "mana_drain"},
                {"name": "죽음의지배", "type": "brv_attack", "power": 320, "mp_cost": 38, "critical_bonus": 25.0, "description": "강력한 단일 죽음 마법"},
                {"name": "데스레이", "type": "hp_attack", "power": 250, "mp_cost": 35, "requires_brv": True, "element": ElementType.DARK, "penetration": True},
            ],
            EnemyType.VAMPIRE: [
                {"name": "흡혈공격", "type": "brv_attack", "power": 160, "mp_cost": 18, "element": ElementType.DARK, "drain": True},
                {"name": "박쥐변신", "type": "buff", "status": "flight", "mp_cost": 20, "target": "self"},
                {"name": "매혹", "type": "debuff", "status": "charm", "mp_cost": 15},
                {"name": "피의지배", "type": "brv_attack", "power": 280, "mp_cost": 32, "critical_bonus": 20.0, "drain": True, "description": "강력한 흡혈 공격"},
                {"name": "혈액갈망", "type": "hp_attack", "power": 180, "mp_cost": 24, "requires_brv": True, "element": ElementType.DARK, "drain": True},
            ],
            EnemyType.DEMON: [
                {"name": "지옥불", "type": "brv_attack", "power": 200, "mp_cost": 25, "element": ElementType.FIRE},
                {"name": "어둠의계약", "type": "debuff", "status": "curse", "mp_cost": 20, "target": "all"},
                {"name": "악마의발톱", "type": "brv_attack", "power": 180, "mp_cost": 15},
                {"name": "지옥의분노", "type": "hp_attack", "power": 230, "mp_cost": 32, "requires_brv": True, "element": ElementType.FIRE, "target": "all"},
            ],
            EnemyType.DEVIL: [
                {"name": "암흑화염", "type": "brv_attack", "power": 220, "mp_cost": 28, "element": ElementType.DARK},
                {"name": "절망의고통", "type": "debuff", "status": "despair", "mp_cost": 25, "target": "all"},
                {"name": "악마왕의위엄", "type": "buff", "status": "all_up", "mp_cost": 35, "target": "self"},
                {"name": "최후의심판", "type": "hp_attack", "power": 280, "mp_cost": 40, "requires_brv": True, "element": ElementType.DARK, "critical_bonus": 30.0},
            ],
            EnemyType.ARCHLICH: [
                {"name": "죽음의마력", "type": "brv_attack", "power": 240, "mp_cost": 32, "element": ElementType.DARK},
                {"name": "시간정지", "type": "debuff", "status": "time_stop", "mp_cost": 40},
                {"name": "죽음의선고", "type": "debuff", "status": "doom", "mp_cost": 30},
                {"name": "대마법진", "type": "hp_attack", "power": 280, "mp_cost": 45, "requires_brv": True, "element": ElementType.DARK, "target": "all"},
            ],
            
            # 최고급 몬스터 스킬
            EnemyType.DRAGON: [
                {"name": "용의발톱", "type": "brv_attack", "power": 280, "mp_cost": 30, "critical_bonus": 25.0},
                {"name": "공포의울음", "type": "debuff", "status": "fear", "mp_cost": 30, "target": "all"},
                {"name": "고대의지혜", "type": "buff", "status": "reflect", "mp_cost": 40, "target": "self"},
                {"name": "드래곤킬러", "type": "brv_attack", "power": 400, "mp_cost": 45, "critical_bonus": 40.0, "description": "단일 대상 강력 일격"},
                {"name": "용의분노연타", "type": "hp_attack", "power": 180, "mp_cost": 38, "requires_brv": True, "hits": 3, "description": "3연속 HP 공격"},
                {"name": "용의숨결", "type": "hp_attack", "power": 350, "mp_cost": 55, "requires_brv": True, "element": ElementType.FIRE, "target": "all"},
            ],
            EnemyType.BALROG: [
                {"name": "화염채찍", "type": "brv_attack", "power": 260, "mp_cost": 28, "element": ElementType.FIRE},
                {"name": "악마의분노", "type": "buff", "status": "berserk", "mp_cost": 35, "target": "self"},
                {"name": "지옥의포효", "type": "brv_attack", "power": 240, "mp_cost": 25},
                {"name": "멸망의일격", "type": "brv_attack", "power": 380, "mp_cost": 42, "critical_bonus": 35.0, "description": "단일 대상 치명타 공격"},
                {"name": "연옥의형벌", "type": "hp_attack", "power": 200, "mp_cost": 45, "requires_brv": True, "element": ElementType.FIRE, "hits": 2, "status": "burn"},
                {"name": "지옥불폭발", "type": "hp_attack", "power": 320, "mp_cost": 50, "requires_brv": True, "element": ElementType.FIRE, "target": "all"},
            ],
            EnemyType.KRAKEN: [
                {"name": "촉수공격", "type": "brv_attack", "power": 200, "mp_cost": 22, "hits": 3},
                {"name": "수압", "type": "debuff", "status": "pressure", "mp_cost": 30},
                {"name": "바다의분노", "type": "brv_attack", "power": 240, "mp_cost": 26, "element": ElementType.WATER},
                {"name": "심해의압박", "type": "brv_attack", "power": 350, "mp_cost": 40, "critical_bonus": 30.0, "description": "단일 대상 강력한 압박"},
                {"name": "촉수연타", "type": "hp_attack", "power": 160, "mp_cost": 35, "requires_brv": True, "hits": 4, "description": "4연속 촉수 공격"},
                {"name": "해일", "type": "hp_attack", "power": 300, "mp_cost": 45, "requires_brv": True, "element": ElementType.WATER, "target": "all"},
            ],
            EnemyType.PHOENIX: [
                {"name": "불사조날개", "type": "brv_attack", "power": 220, "mp_cost": 24, "element": ElementType.FIRE},
                {"name": "부활", "type": "heal", "power": 100, "mp_cost": 50, "target": "self", "effect": "revive"},
                {"name": "정화의빛", "type": "heal", "power": 80, "mp_cost": 30, "target": "all_allies"},
                {"name": "불사조불꽃", "type": "hp_attack", "power": 280, "mp_cost": 40, "requires_brv": True, "element": ElementType.FIRE, "target": "all"},
            ],
            EnemyType.STORM_BIRD: [
                {"name": "폭풍소환", "type": "hp_attack", "power": 310, "mp_cost": 50, "requires_brv": True, "element": ElementType.LIGHTNING, "target": "all"},
                {"name": "천둥의울음", "type": "brv_attack", "power": 190, "mp_cost": 22, "element": ElementType.LIGHTNING},
                {"name": "번개창", "type": "brv_attack", "power": 210, "mp_cost": 26, "element": ElementType.LIGHTNING},
                {"name": "태풍날개", "type": "debuff", "status": "confusion", "mp_cost": 20, "target": "all"},
            ],
            
            # 전설급 몬스터 스킬
            EnemyType.ELDER_DRAGON: [
                {"name": "고대의발톱", "type": "brv_attack", "power": 320, "mp_cost": 35, "critical_bonus": 30.0},
                {"name": "용왕의위엄", "type": "debuff", "status": "terror", "mp_cost": 40, "target": "all"},
                {"name": "고대지혜", "type": "buff", "status": "omniscience", "mp_cost": 45, "target": "self"},
                {"name": "시공간균열", "type": "brv_attack", "power": 350, "mp_cost": 50, "element": ElementType.NEUTRAL},
                {"name": "용왕의분노", "type": "brv_attack", "power": 450, "mp_cost": 55, "critical_bonus": 50.0, "penetration": True, "description": "절대 강력 단일기"},
                {"name": "태초의불꽃", "type": "hp_attack", "power": 250, "mp_cost": 60, "requires_brv": True, "element": ElementType.FIRE, "hits": 3, "description": "3연속 태고의 불꽃"},
                {"name": "고대룡의숨결", "type": "hp_attack", "power": 450, "mp_cost": 65, "requires_brv": True, "element": ElementType.FIRE, "target": "all"},
            ],
            EnemyType.TITAN: [
                {"name": "산맥붕괴", "type": "brv_attack", "power": 300, "mp_cost": 40, "element": ElementType.EARTH},
                {"name": "타이탄의분노", "type": "buff", "status": "giant_strength", "mp_cost": 50, "target": "self"},
                {"name": "거대한주먹", "type": "brv_attack", "power": 280, "mp_cost": 35},
                {"name": "대지분열", "type": "hp_attack", "power": 420, "mp_cost": 60, "requires_brv": True, "element": ElementType.EARTH, "target": "all"},
            ],
            EnemyType.VOID_LORD: [
                {"name": "차원균열", "type": "brv_attack", "power": 280, "mp_cost": 38, "element": ElementType.DARK},
                {"name": "정신지배", "type": "debuff", "status": "void_curse", "mp_cost": 40, "target": "all"},
                {"name": "공허의검", "type": "brv_attack", "power": 300, "mp_cost": 42, "element": ElementType.DARK},
                {"name": "보이드러쉬", "type": "hp_attack", "power": 400, "mp_cost": 60, "requires_brv": True, "element": ElementType.DARK, "target": "all"},
            ],
            EnemyType.VOID_EMPEROR: [
                {"name": "현실왜곡", "type": "brv_attack", "power": 350, "mp_cost": 48, "element": ElementType.DARK},
                {"name": "공허황제의힘", "type": "buff", "status": "void_emperor", "mp_cost": 60, "target": "self"},
                {"name": "존재소거", "type": "debuff", "status": "existence_erase", "mp_cost": 50},
                {"name": "절대공허", "type": "brv_attack", "power": 380, "mp_cost": 55, "element": ElementType.DARK},
                {"name": "무의지배", "type": "brv_attack", "power": 480, "mp_cost": 65, "critical_bonus": 60.0, "penetration": True, "description": "절대 강력 무 지배"},
                {"name": "공허의연쇄", "type": "hp_attack", "power": 220, "mp_cost": 58, "requires_brv": True, "element": ElementType.DARK, "hits": 5, "description": "5연속 공허 공격"},
                {"name": "앱솔루트제로", "type": "hp_attack", "power": 500, "mp_cost": 75, "requires_brv": True, "element": ElementType.DARK, "target": "all"},
            ],
            EnemyType.CHAOS_BEAST: [
                {"name": "무작위변이", "type": "special", "mp_cost": 40, "effect": "random_chaos"},
                {"name": "광기유발", "type": "debuff", "status": "madness", "mp_cost": 35, "target": "all"},
                {"name": "혼돈의발톱", "type": "brv_attack", "power": 360, "mp_cost": 45, "element": ElementType.NEUTRAL},
                {"name": "혼돈폭발", "type": "hp_attack", "power": 450, "mp_cost": 70, "requires_brv": True, "element": ElementType.NEUTRAL, "target": "all"},
            ],
        }
        
        # 해당 적 타입의 스킬 추가
        type_skills = enemy_skill_sets.get(self.enemy_type, [])
        skills.extend(type_skills)
        
        return skills
    
    def choose_action(self, player_party: List[Character], enemy_party: List) -> Dict:
        """AI 행동 선택 (개선된 시스템)"""
        if self.ai_type == "aggressive":
            return self._aggressive_ai(player_party)
        elif self.ai_type == "defensive":
            return self._defensive_ai(player_party, enemy_party)
        elif self.ai_type == "tactical":
            return self._tactical_ai(player_party, enemy_party)
        elif self.ai_type == "caster":
            return self._caster_ai(player_party)
        elif self.ai_type == "assassin":
            return self._assassin_ai(player_party)
        elif self.ai_type == "support":
            return self._support_ai(player_party, enemy_party)
        elif self.ai_type == "berserker":
            return self._berserker_ai(player_party)
        elif self.ai_type == "adaptive":
            return self._adaptive_ai(player_party, enemy_party)
        else:
            return self._basic_ai(player_party)
    
    def _aggressive_ai(self, targets: List[Character]) -> Dict:
        """공격적 AI - 공격 전 버프 사용 고려"""
        if not targets:
            return {"action": "wait"}
        
        alive_targets = [t for t in targets if t.is_alive]
        target = min(alive_targets, key=lambda x: x.current_hp)
        
        # 25% 확률로 공격 버프 사용
        if random.random() < 0.25:
            buff_skills = [s for s in self.enemy_skills 
                          if s.get("type") == "buff" and 
                          ("attack" in s.get("status", "") or "strength" in s.get("status", ""))]
            for skill in buff_skills:
                if self.current_mp >= skill.get("mp_cost", 0):
                    return {
                        "action": "skill",
                        "skill": skill,
                        "target": self
                    }
        
        # 강력한 공격 스킬부터 사용 시도
        attack_skills = [s for s in self.enemy_skills if s.get("type") in ["attack", "magic_attack", "ultimate"]]
        for skill in sorted(attack_skills, key=lambda x: x.get("power", 0), reverse=True):
            if self.current_mp >= skill.get("mp_cost", 0):
                return {
                    "action": "skill",
                    "skill": skill,
                    "target": target
                }
        
        # MP가 부족하면 기본 공격
        return {"action": "attack", "target": target}
    
    def _defensive_ai(self, targets: List[Character], allies: List) -> Dict:
        """방어적 AI - 체력이 낮으면 치유/방어"""
        # 체력이 30% 이하면 치유 시도
        if self.current_hp <= self.max_hp * 0.3:
            heal_skills = [s for s in self.enemy_skills if s.get("type") == "heal"]
            for skill in heal_skills:
                if self.current_mp >= skill.get("mp_cost", 0):
                    return {
                        "action": "skill",
                        "skill": skill,
                        "target": self
                    }
        
        # 체력이 50% 이하면 버프 시도
        if self.current_hp <= self.max_hp * 0.5:
            buff_skills = [s for s in self.enemy_skills if s.get("type") == "buff"]
            for skill in buff_skills:
                if self.current_mp >= skill.get("mp_cost", 0):
                    return {
                        "action": "skill",
                        "skill": skill,
                        "target": self
                    }
        
        # 그 외에는 공격
        return self._basic_ai(targets)
    
    def _tactical_ai(self, targets: List[Character], allies: List) -> Dict:
        """전술적 AI - 상황에 맞는 스킬 사용"""
        alive_targets = [t for t in targets if t.is_alive]
        
        # 적이 많으면 전체 공격
        if len(alive_targets) >= 3:
            aoe_skills = [s for s in self.enemy_skills if s.get("target") == "all"]
            for skill in aoe_skills:
                if self.current_mp >= skill.get("mp_cost", 0):
                    return {
                        "action": "skill",
                        "skill": skill,
                        "target": None  # 전체 공격
                    }
        
        # 60% 확률로 디버프 스킬 우선 사용 (확률 증가)
        debuff_skills = [s for s in self.enemy_skills if s.get("type") == "debuff"]
        if debuff_skills and random.random() < 0.6:
            skill = random.choice(debuff_skills)
            if self.current_mp >= skill.get("mp_cost", 0):
                # 디버프 대상 선택
                if skill.get("target") == "all":
                    target = None
                else:
                    # 가장 위협적인 적 (HP와 공격력 고려)
                    target = max(alive_targets, key=lambda x: x.current_hp + getattr(x, 'attack', 0))
                return {
                    "action": "skill",
                    "skill": skill,
                    "target": target
                }
        
        # 30% 확률로 버프 사용
        if random.random() < 0.3:
            buff_skills = [s for s in self.enemy_skills if s.get("type") == "buff"]
            if buff_skills:
                skill = random.choice(buff_skills)
                if self.current_mp >= skill.get("mp_cost", 0):
                    return {
                        "action": "skill",
                        "skill": skill,
                        "target": self
                    }
        
        # 일반 공격
        return self._aggressive_ai(targets)
    
    def _caster_ai(self, targets: List[Character]) -> Dict:
        """마법사 AI - 마법 스킬 우선 사용"""
        if not targets:
            return {"action": "wait"}
        
        # 마법 스킬 우선
        magic_skills = [s for s in self.enemy_skills if s.get("element") != ElementType.NEUTRAL]
        for skill in sorted(magic_skills, key=lambda x: x.get("power", 0), reverse=True):
            if self.current_mp >= skill.get("mp_cost", 0):
                target = random.choice([t for t in targets if t.is_alive])
                return {
                    "action": "skill",
                    "skill": skill,
                    "target": target
                }
        
        # MP가 부족하면 대기 (MP 회복)
        if self.current_mp < self.max_mp * 0.5:
            return {"action": "wait"}
        
        return self._basic_ai(targets)
    
    def _assassin_ai(self, targets: List[Character]) -> Dict:
        """암살자 AI - 크리티컬 스킬과 약한 적 우선"""
        if not targets:
            return {"action": "wait"}
        
        # 가장 HP가 낮은 적 선택
        target = min([t for t in targets if t.is_alive], key=lambda x: x.current_hp)
        
        # 크리티컬 보너스가 있는 스킬 우선
        crit_skills = [s for s in self.enemy_skills if s.get("critical_bonus", 0) > 0]
        for skill in crit_skills:
            if self.current_mp >= skill.get("mp_cost", 0):
                return {
                    "action": "skill",
                    "skill": skill,
                    "target": target
                }
        
        return {"action": "attack", "target": target}
    
    def _support_ai(self, targets: List[Character], allies: List) -> Dict:
        """지원 AI - 아군 치유/버프 우선"""
        # 아군 중 체력이 낮은 존재 확인
        injured_allies = [a for a in allies if a.is_alive and a.current_hp <= a.max_hp * 0.6]
        
        if injured_allies:
            heal_skills = [s for s in self.enemy_skills if s.get("type") == "heal"]
            for skill in heal_skills:
                if self.current_mp >= skill.get("mp_cost", 0):
                    target = min(injured_allies, key=lambda x: x.current_hp)
                    return {
                        "action": "skill",
                        "skill": skill,
                        "target": target
                    }
        
        # 버프 스킬 사용
        buff_skills = [s for s in self.enemy_skills if s.get("type") == "buff"]
        if buff_skills and random.random() < 0.3:
            skill = random.choice(buff_skills)
            if self.current_mp >= skill.get("mp_cost", 0):
                return {
                    "action": "skill",
                    "skill": skill,
                    "target": random.choice(allies) if allies else self
                }
        
        return self._basic_ai(targets)
    
    def _berserker_ai(self, targets: List[Character]) -> Dict:
        """광전사 AI - 체력이 낮을수록 강한 공격"""
        if not targets:
            return {"action": "wait"}
        
        hp_ratio = self.current_hp / self.max_hp
        
        # 체력이 낮을수록 강한 스킬 사용
        if hp_ratio <= 0.3:  # 30% 이하
            power_threshold = 0.5
        elif hp_ratio <= 0.6:  # 60% 이하
            power_threshold = 1.0
        else:
            power_threshold = 1.5
        
        strong_skills = [s for s in self.enemy_skills 
                        if s.get("type") in ["attack", "magic_attack"] and s.get("power", 0) >= power_threshold]
        
        if strong_skills:
            skill = random.choice(strong_skills)
            if self.current_mp >= skill.get("mp_cost", 0):
                target = random.choice([t for t in targets if t.is_alive])
                return {
                    "action": "skill",
                    "skill": skill,
                    "target": target
                }
        
        return self._aggressive_ai(targets)
    
    def _adaptive_ai(self, targets: List[Character], allies: List) -> Dict:
        """적응형 AI - 상황에 따라 AI 타입 변경"""
        alive_targets = [t for t in targets if t.is_alive]
        hp_ratio = self.current_hp / self.max_hp
        
        # 체력에 따라 AI 전략 변경
        if hp_ratio <= 0.3:
            return self._defensive_ai(targets, allies)
        elif len(alive_targets) >= 3:
            return self._tactical_ai(targets, allies)
        elif any(t.current_hp <= t.max_hp * 0.4 for t in alive_targets):
            return self._assassin_ai(targets)
        else:
            return self._aggressive_ai(targets)
    
    def _basic_ai(self, targets: List[Character]) -> Dict:
        """기본 AI - 다양한 스킬 사용"""
        if not targets:
            return {"action": "wait"}
        
        alive_targets = [t for t in targets if t.is_alive]
        target = random.choice(alive_targets)
        
        # 70% 확률로 스킬 사용 (확률 크게 증가)
        if self.enemy_skills and random.random() < 0.7:
            usable_skills = [s for s in self.enemy_skills if self.current_mp >= s.get("mp_cost", 0)]
            
            if usable_skills:
                # 스킬 타입별 가중치
                skill_weights = []
                for skill in usable_skills:
                    skill_type = skill.get("type", "attack")
                    if skill_type in ["buff", "debuff"]:
                        weight = 3  # 버프/디버프 우선
                    elif skill_type in ["magic_attack", "ultimate"]:
                        weight = 2  # 마법/필살기 차선
                    else:
                        weight = 1  # 일반 공격 최후
                    skill_weights.append(weight)
                
                # 가중치에 따른 스킬 선택
                skill = random.choices(usable_skills, weights=skill_weights)[0]
                
                # 타겟 결정
                skill_target = target
                if skill.get("target") == "all":
                    skill_target = None
                elif skill.get("target") == "self" or skill.get("type") == "buff":
                    skill_target = self
                
                return {
                    "action": "skill",
                    "skill": skill,
                    "target": skill_target
                }
        
        return {"action": "attack", "target": target}
class EnemyManager:
    """적 관리자"""
    
    def __init__(self):
        self.spawn_table = self._create_spawn_table()
    
    def _create_spawn_table(self) -> Dict[int, List[EnemyType]]:
        """층별 스폰 테이블"""
        return {
            # 1-10층
            **{floor: [EnemyType.GOBLIN, EnemyType.ORC, EnemyType.SKELETON, EnemyType.SLIME, EnemyType.RAT] 
               for floor in range(1, 11)},
            
            # 11-20층  
            **{floor: [EnemyType.TROLL, EnemyType.OGRE, EnemyType.WIGHT, EnemyType.GARGOYLE, EnemyType.FIRE_SALAMANDER]
               for floor in range(11, 21)},
            
            # 21-30층
            **{floor: [EnemyType.DRAKE, EnemyType.CHIMERA, EnemyType.LICH, EnemyType.DEMON, EnemyType.ICE_GOLEM]
               for floor in range(21, 31)},
            
            # 31-40층
            **{floor: [EnemyType.DRAGON, EnemyType.BALROG, EnemyType.KRAKEN, EnemyType.PHOENIX, EnemyType.STORM_BIRD]
               for floor in range(31, 41)},
            
            # 41-50층
            **{floor: [EnemyType.ELDER_DRAGON, EnemyType.TITAN, EnemyType.VOID_LORD, EnemyType.CHAOS_BEAST]
               for floor in range(41, 51)},
        }
    
    def spawn_enemy(self, floor: int) -> Enemy:
        """층에 맞는 적 스폰"""
        possible_types = self.spawn_table.get(floor, [EnemyType.GOBLIN])
        enemy_type = random.choice(possible_types)
        return Enemy(enemy_type, floor)
    
    def spawn_encounter(self, floor: int, party_size: int = 4) -> List[Enemy]:
        """조우 그룹 생성 (씨드는 호출자에서 설정)"""
        group_size = random.randint(1, min(4, max(1, party_size)))
        enemies = []
        
        for _ in range(group_size):
            enemy = self.spawn_enemy(floor)
            enemies.append(enemy)
        
        return enemies
    
    def get_boss_enemy(self, floor: int) -> Enemy:
        """보스 적 생성"""
        boss_types = {
            10: EnemyType.MINOTAUR,
            20: EnemyType.DRAGON,
            30: EnemyType.ARCHLICH,
            40: EnemyType.TITAN,
            50: EnemyType.VOID_EMPEROR
        }
        
        boss_type = boss_types.get(floor, EnemyType.DRAGON)
        boss = Enemy(boss_type, floor)
        boss.rank = EnemyRank.BOSS
        boss._set_enemy_stats()  # 보스 스탯으로 재설정
        
        return boss

# 전역 적 매니저
enemy_manager = EnemyManager()

# Brave 스탯을 별도로 export하기 위한 딕셔너리 생성
def get_enemy_brave_stats_dict():
    """Enemy Brave 스탯 딕셔너리 반환"""
    enemy_stats = {}
    for enemy_type in EnemyType:
        try:
            # 임시 적 생성해서 스탯 가져오기
            temp_enemy = Enemy(enemy_type, 1)
            base_stats = temp_enemy._get_base_stats_by_type()
            
            enemy_stats[enemy_type] = {
                "int_brv": base_stats.get("init_brv", 300),
                "max_brv": base_stats.get("max_brv", 1500),
                "brv_efficiency": 0.8,
                "brv_loss_resistance": 0.9
            }
        except:
            # 기본값 사용
            enemy_stats[enemy_type] = {
                "int_brv": 300,
                "max_brv": 1500,
                "brv_efficiency": 0.8,
                "brv_loss_resistance": 0.9
            }
    
    return enemy_stats

# balance.py에서 사용할 ENEMY_BRAVE_STATS
ENEMY_BRAVE_STATS = get_enemy_brave_stats_dict()

def get_enemy_manager() -> EnemyManager:
    """적 매니저 반환"""
    return enemy_manager

def create_random_encounter(floor: int) -> List[Enemy]:
    """랜덤 조우 생성"""
    return enemy_manager.spawn_encounter(floor)

def create_boss_encounter(floor: int) -> Enemy:
    """보스 조우 생성"""
    return enemy_manager.get_boss_enemy(floor)
