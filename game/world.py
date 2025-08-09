"""
게임 월드 및 던전 시스템
"""

import random
from typing import List, Tuple, Dict
from enum import Enum
from .items import ItemDatabase, Item, DropRateManager
from .color_text import *


class TileType(Enum):
    """타일 종류"""
    WALL = "#"
    FLOOR = "."
    DOOR = "+"
    LOCKED_DOOR = "&"   # 잠긴 문 (열쇠 필요)
    SECRET_DOOR = "?"   # 비밀 문 (탐지 스킬 필요)
    STAIRS_UP = "<"
    STAIRS_DOWN = ">"
    PLAYER = "@"
    ENEMY = "E"
    BOSS = "♔"          # 보스 (3층마다 등장) - 왕관 마커
    ITEM = "!"
    TREASURE = "$"
    CHEST = "="         # 보물상자 (열쇠 또는 해제 스킬 필요)
    TRAP = "^"          # 함정 (탐지/해제 스킬 필요)
    LEVER = "/"         # 레버 (조작 스킬)
    ALTAR = "T"         # 제단 (신관 스킬)
    FOUNTAIN = "~"      # 분수 (회복)
    BOOKSHELF = "B"     # 책장 (철학자/아크메이지 스킬)
    FORGE = "F"         # 대장간 (기계공학자 스킬)
    GARDEN = "G"        # 정원 (드루이드 스킬)
    CRYSTAL = "*"       # 마법 수정 (정령술사 스킬)
    # 부정적 요소들
    CURSED_ALTAR = "X"  # 저주받은 제단 (부정적 효과)
    POISON_CLOUD = "P"  # 독구름 (체력 감소)
    DARK_PORTAL = "O"   # 어둠의 포털 (적 소환)
    CURSED_CHEST = "C"  # 저주받은 상자 (나쁜 효과 + 아이템)
    UNSTABLE_FLOOR = "U" # 불안정한 바닥 (낙하 위험)


class Tile:
    """던전 타일 클래스"""
    
    def __init__(self, tile_type: TileType, x: int, y: int):
        self.type = tile_type
        self.x = x
        self.y = y
        self.visible = False
        self.explored = False
        self.has_enemy = False
        self.has_item = False
        
        # 새로운 속성들
        self.is_locked = False      # 잠긴 문/상자 여부
        self.is_trapped = False     # 함정 여부
        self.trap_detected = False  # 함정 탐지됨
        self.is_activated = False   # 레버/제단 활성화됨
        self.required_skill = None  # 필요한 스킬
        self.treasure_quality = "common"  # 보물 품질
        self.secret_revealed = False # 비밀 문/통로 발견됨
        
    def get_display_char(self) -> str:
        """표시할 문자 반환"""
        if not self.explored:
            return " "
        elif not self.visible:
            # 탐험했지만 현재 시야에 없는 경우
            if self.type == TileType.WALL:
                return "#"  # 벽은 항상 표시 (회색으로 표시됨)
            else:
                return "·"  # 다른 지형은 어둠 처리
        else:
            # 비밀 문은 발견되기 전에는 벽으로 보임
            if self.type == TileType.SECRET_DOOR and not self.secret_revealed:
                return "#"
            # 함정은 탐지되기 전에는 바닥으로 보임
            elif self.type == TileType.TRAP and not self.trap_detected:
                return "."
            else:
                return self.type.value
    
    def get_display_info(self) -> Tuple[str, str]:
        """표시할 문자와 색상 정보 반환"""
        char = self.get_display_char()
        
        if not self.explored:
            return " ", "black"
        elif not self.visible:
            # 탐험했지만 현재 시야에 없는 경우 회색으로 표시
            if self.type == TileType.WALL:
                return "#", "dark_gray"  # 벽은 어두운 회색
            else:
                return "·", "gray"
        else:
            # 현재 시야에 있는 경우 정상 색상
            if self.type == TileType.WALL:
                return "#", "white"
            elif self.type == TileType.FLOOR:
                return ".", "gray"
            elif self.type == TileType.DOOR:
                return "+", "brown"
            elif self.type == TileType.STAIRS_DOWN:
                return ">", "yellow"
            elif self.type == TileType.STAIRS_UP:
                return "<", "yellow"
            elif self.type == TileType.TREASURE:
                return "$", "gold"
            elif self.type == TileType.BOSS:
                return "♔", "red"
            else:
                return char, "white"
            
    def is_walkable(self) -> bool:
        """이동 가능한지 확인"""
        # 기본적으로 이동 가능한 타일들
        walkable_types = [
            TileType.FLOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN,
            TileType.ITEM, TileType.TREASURE, TileType.FOUNTAIN,
            TileType.GARDEN, TileType.BOSS, TileType.TRAP  # 함정도 이동 가능 (밟으면 발동)
        ]
        
        # 문은 잠겨있지 않으면 이동 가능
        if self.type == TileType.DOOR:
            return not self.is_locked
        elif self.type == TileType.LOCKED_DOOR:
            return False  # 항상 잠김 (열쇠로 열어야 함)
        elif self.type == TileType.SECRET_DOOR:
            return self.secret_revealed and not self.is_locked
        
        return self.type in walkable_types


class Room:
    """던전 방 클래스"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        
    def intersects(self, other: 'Room') -> bool:
        """다른 방과 겹치는지 확인"""
        return (self.x <= other.x + other.width and
                self.x + self.width >= other.x and
                self.y <= other.y + other.height and
                self.y + self.height >= other.y)


class GameWorld:
    """게임 월드 관리 클래스"""
    
    def __init__(self, width: int = None, height: int = None, party_manager=None):
        # 설정에서 맵 크기 가져오기
        if width is None or height is None:
            try:
                from config import game_config
                if hasattr(game_config, 'get_map_dimensions'):
                    width, height = game_config.get_map_dimensions()
                else:
                    width, height = 35, 35  # 기본값
            except (ImportError, AttributeError):
                width, height = 35, 35  # 기본값 (정사각형)
        
        self.width = width
        self.height = height
        self.party_manager = party_manager  # 파티 매니저 참조 추가
        self.audio_system = None  # 오디오 시스템 참조
        self.tiles: List[List[Tile]] = []
        self.rooms: List[Room] = []
        self.player_pos = (0, 0)
        self.current_level = 1
        self.current_floor = 1  # current_level의 별칭
        self.enemies_positions: List[Tuple[int, int]] = []
        self.items_positions: List[Tuple[int, int]] = []
        self.floor_items: Dict[Tuple[int, int], Item] = {}  # 위치별 아이템 매핑
        self.floor_enemies: Dict[Tuple[int, int], Dict] = {}  # 위치별 적 정보 매핑 (레벨 등)
        
        # 새로운 필드 스킬 요소들
        self.special_tiles: Dict[Tuple[int, int], Dict] = {}  # 특수 타일 정보
        self.locked_doors: List[Tuple[int, int]] = []         # 잠긴 문들
        self.secret_doors: List[Tuple[int, int]] = []         # 비밀 문들
        self.traps: List[Tuple[int, int]] = []                # 함정들
        self.treasure_chests: List[Tuple[int, int]] = []      # 보물상자들
        self.interactive_objects: List[Tuple[int, int]] = []  # 상호작용 객체들 (레버, 제단 등)
        
        # 이동거리 추적 시스템
        self.total_movement_distance = 0  # 총 이동거리 (게임 전체)
        self.current_run_movement = 0     # 현재 런에서의 이동거리
        self.actions_taken = 0            # 총 액션 수 (AFK 방지)
        self.combat_count = 0             # 전투 횟수
        
        # 현재 층의 시드 저장 (세이브 파일에 포함)
        self.current_level_seed = None
        
        # 성과 기반 보상 시스템
        self.performance_metrics = {
            'floors_cleared': 0,           # 클리어한 층수
            'enemies_defeated': 0,         # 처치한 적 수
            'items_collected': 0,          # 수집한 아이템 수
            'perfect_floors': 0,           # 모든 적을 처치한 층수
            'exploration_rate': 0.0,       # 탐험률 (0.0 ~ 1.0)
            'combat_efficiency': 0.0,      # 전투 효율성
            'survival_time': 0,            # 생존 시간 (초)
            'no_damage_combats': 0,        # 무피해 전투 횟수
            'critical_hits': 0,            # 크리티컬 히트 횟수
            'skills_used': 0,              # 사용한 스킬 수
        }
        
        # 현재 층 통계
        self.current_floor_stats = {
            'enemies_on_floor': 0,         # 현재 층의 총 적 수
            'enemies_defeated_on_floor': 0, # 현재 층에서 처치한 적 수
            'tiles_explored': set(),       # 탐험한 타일들
            'total_tiles': 0,              # 총 바닥 타일 수
        }
        
        self.initialize_world()
        
    def initialize_world(self):
        """월드 초기화"""
        # 모든 타일을 벽으로 초기화
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(Tile(TileType.WALL, x, y))
            self.tiles.append(row)
            
    def generate_level(self, saved_seed=None):
        """레벨 생성 (던전 생성) - 고정 씨드 사용"""
        # 층수 기반 고정 씨드 설정 (같은 층은 항상 같은 결과)
        if saved_seed is not None:
            level_seed = saved_seed
            print(f"레벨 {self.current_level} 던전 복원 (저장된 씨드: {level_seed})")
        else:
            level_seed = hash(f"level_{self.current_level}") % (2**32)
            print(f"레벨 {self.current_level} 던전 생성 (새 씨드: {level_seed})")
        
        # 현재 층의 씨드 저장
        self.current_level_seed = level_seed
        random.seed(level_seed)
        
        self.rooms = []
        self.enemies_positions = []
        self.items_positions = []
        self.floor_items = {}
        self.floor_enemies = {}  # 적 정보도 초기화
        
        # 새로운 요소들 초기화
        self.special_tiles = {}
        self.locked_doors = []
        self.secret_doors = []
        self.traps = []
        self.treasure_chests = []
        self.interactive_objects = []
        
        print(f"레벨 {self.current_level} 던전을 생성 중...")
        
        # 방 생성 시도
        max_rooms = random.randint(6, 12)  # 방 개수 증가
        for _ in range(max_rooms):
            self.try_place_room()
            
        # 방들을 복도로 연결
        self.connect_rooms()
        
        # 플레이어 시작 위치 설정
        if self.rooms:
            first_room = self.rooms[0]
            self.player_pos = (first_room.center_x, first_room.center_y)
            
        # 적과 아이템 배치
        self.place_enemies()
        self.place_items()
        
        # 새로운 특수 요소들 배치
        self.place_special_features()
        
        # 계단 배치 (다음 층으로 가는 계단)
        self.place_stairs()
        
        # 성과 추적을 위한 통계 계산
        self._calculate_floor_stats()
        
        # 시야 업데이트
        self.update_visibility()
        
        print("던전 생성 완료!")
        
    def try_place_room(self):
        """방 배치 시도"""
        for _ in range(100):  # 최대 100번 시도
            # 랜덤 크기와 위치
            width = random.randint(4, 12)
            height = random.randint(4, 8)
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
            
            new_room = Room(x, y, width, height)
            
            # 다른 방들과 겹치는지 확인
            can_place = True
            for room in self.rooms:
                if new_room.intersects(room):
                    can_place = False
                    break
                    
            if can_place:
                self.create_room(new_room)
                self.rooms.append(new_room)
                break
                
    def create_room(self, room: Room):
        """방 생성"""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[y][x].type = TileType.FLOOR
                    
    def connect_rooms(self):
        """방들을 복도로 연결"""
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]
            
            # L자 복도 생성
            self.create_h_tunnel(room1.center_x, room2.center_x, room1.center_y)
            self.create_v_tunnel(room1.center_y, room2.center_y, room2.center_x)
            
    def create_h_tunnel(self, x1: int, x2: int, y: int):
        """수평 복도 생성"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x].type = TileType.FLOOR
                
    def create_v_tunnel(self, y1: int, y2: int, x: int):
        """수직 복도 생성"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x].type = TileType.FLOOR
                
    def place_enemies(self):
        """적 배치 - 맵 크기와 난이도에 따른 적 수 조정"""
        # 맵 크기에 따른 기본 적 수 계산
        map_area = self.width * self.height
        base_enemies = max(3, map_area // 120)  # 맵 크기 비례 (120 타일당 1마리)
        
        # 난이도별 적 수 조정
        from config import game_config
        enemy_spawn_rate = game_config.get_difficulty_setting('enemy_spawn_rate')
        num_enemies = int(base_enemies * enemy_spawn_rate)
        
        # 맵 크기별 추가 보정 (큰 맵일수록 더 많은 적)
        if self.width >= 60:  # 큰 맵
            num_enemies = int(num_enemies * 1.5)
        elif self.width >= 45:  # 중간 맵
            num_enemies = int(num_enemies * 1.2)
        
        safe_radius = 7  # 플레이어 스폰 지점 반지름 7블록 내 적 생성 금지
        
        print(f"🎯 맵 크기 {self.width}x{self.height}에 적 {num_enemies}마리 배치 시도")
        
        for _ in range(num_enemies):
            # 빈 바닥 타일에 적 배치
            attempts = 0
            while attempts < 50:
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                
                # 플레이어 스폰 지점과의 거리 계산
                distance_from_player = ((x - self.player_pos[0]) ** 2 + (y - self.player_pos[1]) ** 2) ** 0.5
                
                if (self.tiles[y][x].type == TileType.FLOOR and 
                    (x, y) != self.player_pos and
                    (x, y) not in self.enemies_positions and
                    distance_from_player > safe_radius):  # 안전 반지름 확인
                    
                    # 현재 층수 기반 적 레벨 계산 (더 직관적으로)
                    base_level = max(1, (self.current_level + 1)) 
                    enemy_level = base_level + random.randint(-1, 1)  # ±1 변동
                    enemy_level = max(1, min(enemy_level, 100))  # 레벨 1-100 제한 (더 낮게)
                    
                    self.enemies_positions.append((x, y))
                    self.floor_enemies[(x, y)] = {
                        'level': enemy_level,
                        'type': random.choice(['고블린', '오크', '스켈레톤', '다크엘프', '트롤'])
                    }
                    self.tiles[y][x].has_enemy = True
                    break
                    
                attempts += 1
            
            # 안전 반지름 때문에 적을 배치하지 못한 경우 알림
            if attempts >= 50:
                print(f"⚠️ 적 배치 실패: 플레이어 안전 반지름({safe_radius}블록) 제약으로 인해 적절한 위치를 찾지 못했습니다.")
                
    def place_items(self):
        """아이템 배치 (개선된 시스템) - 위치별 고정 시드"""
        # 방 당 1-3개의 아이템 배치
        for room_idx, room in enumerate(self.rooms):
            # 방별 고정 시드 설정
            room_seed = hash(f"room_items_{self.current_level}_{room_idx}_{room.x}_{room.y}") % (2**32)
            random.seed(room_seed)
            
            num_items = random.randint(1, 3)
            
            for item_idx in range(num_items):
                # 아이템별 고정 시드 설정
                item_seed = hash(f"item_{self.current_level}_{room_idx}_{item_idx}") % (2**32)
                random.seed(item_seed)
                
                attempts = 0
                while attempts < 20:
                    # 방 내부의 랜덤 위치
                    x = random.randint(room.x + 1, room.x + room.width - 2)
                    y = random.randint(room.y + 1, room.y + room.height - 2)
                    
                    if (self.tiles[y][x].type == TileType.FLOOR and 
                        (x, y) != self.player_pos and
                        (x, y) not in self.enemies_positions and
                        (x, y) not in self.items_positions):
                        
                        # 현재 레벨에 맞는 랜덤 아이템 생성 (스테이지 기반)
                        from .items import ItemDatabase
                        item = ItemDatabase.get_random_item_by_stage(self.current_level)
                        if item:  # 아이템이 드롭되었을 때만 배치
                            self.items_positions.append((x, y))
                            self.floor_items[(x, y)] = item
                            self.tiles[y][x].has_item = True
                        break
                        
                    attempts += 1
        
        # 복도에 보너스 아이템 배치 (낮은 확률)
        safe_radius = 7  # 플레이어 스폰 지점 반지름 7블록 내 아이템 생성 금지
        bonus_seed = hash(f"bonus_items_{self.current_level}") % (2**32)
        random.seed(bonus_seed)
        
        bonus_items = random.randint(1, 3)
        for bonus_idx in range(bonus_items):
            bonus_item_seed = hash(f"bonus_{self.current_level}_{bonus_idx}") % (2**32)
            random.seed(bonus_item_seed)
            
            if random.random() < 0.3:  # 30% 확률
                attempts = 0
                while attempts < 30:
                    x = random.randint(1, self.width - 2)
                    y = random.randint(1, self.height - 2)
                    
                    # 플레이어 스폰 지점과의 거리 계산
                    distance_from_player = ((x - self.player_pos[0]) ** 2 + (y - self.player_pos[1]) ** 2) ** 0.5
                    
                    if (self.tiles[y][x].type == TileType.FLOOR and 
                        (x, y) != self.player_pos and
                        (x, y) not in self.enemies_positions and
                        (x, y) not in self.items_positions and
                        distance_from_player >= safe_radius):  # 스폰 지점에서 충분히 멀리
                        
                        from .items import ItemDatabase
                        # 보물상자는 더 좋은 아이템 (스테이지+2 수준)
                        item = ItemDatabase.get_random_item_by_stage(self.current_level + 2)
                        if not item:  # 혹시라도 아이템이 없으면 기본 아이템
                            all_items = ItemDatabase.get_all_items()
                            item = random.choice(all_items) if all_items else None
                        
                        if item:
                            self.items_positions.append((x, y))
                            self.floor_items[(x, y)] = item
                            self.tiles[y][x].has_item = True
                        break
                        
                    attempts += 1
                
    def place_stairs(self):
        """계단 배치 (다음 층으로 가는 계단)"""
        if len(self.rooms) < 2:
            return
            
        # 마지막 방에 계단 배치
        last_room = self.rooms[-1]
        stair_x = last_room.center_x
        stair_y = last_room.center_y
        
        # 계단 위치 조정 (중앙이 아닌 모서리로)
        stair_x = last_room.x + last_room.width - 2
        stair_y = last_room.y + last_room.height - 2
        
        if self.is_valid_pos(stair_x, stair_y):
            self.tiles[stair_y][stair_x].type = TileType.STAIRS_DOWN
            # print(f"다음 층으로 가는 계단이 ({stair_x}, {stair_y})에 배치되었습니다.")  # 숨김
    
    def place_special_features(self):
        """특수 필드 스킬 요소들 배치"""
        # print("🎯 특수 필드 요소들을 배치합니다...")  # 숨김
        
        # 각 방에 특수 요소 배치 확률 (더 많이)
        for room_idx, room in enumerate(self.rooms[1:], 1):  # 첫 번째 방은 시작점이므로 제외
            feature_seed = hash(f"features_{self.current_level}_{room_idx}") % (2**32)
            random.seed(feature_seed)
            
            # 70% 확률로 특수 요소 배치 (기존 30%에서 증가)
            if random.random() < 0.7:
                self._place_room_feature(room, room_idx)
                
            # 30% 확률로 추가 특수 요소 배치
            if random.random() < 0.3:
                self._place_room_feature(room, room_idx)
        
        # 복도에 함정과 비밀 문 배치
        self._place_corridor_features()
        
        # 잠긴 문 생성 (일부 방 입구를)
        self._place_locked_doors()
    
    def _place_room_feature(self, room: Room, room_idx: int):
        """방에 특수 요소 배치"""
        # 방 중앙 근처의 빈 공간 찾기
        center_x, center_y = room.center_x, room.center_y
        
        # 배치할 특수 요소 선택 (확장된 리스트 + 부정적 요소)
        good_features = [
            (TileType.CHEST, "treasure_chest", "보물상자"),
            (TileType.ALTAR, "altar", "신비한 제단"),
            (TileType.FOUNTAIN, "fountain", "치유의 샘"),
            (TileType.BOOKSHELF, "bookshelf", "고대 서재"),
            (TileType.FORGE, "forge", "마법 대장간"),
            (TileType.GARDEN, "garden", "비밀 정원"),
            (TileType.CRYSTAL, "crystal", "마력 수정"),
            (TileType.LEVER, "lever", "수상한 레버"),
            # 추가 다양성
            (TileType.ALTAR, "shrine", "고대 신전"),
            (TileType.FOUNTAIN, "spring", "성스러운 샘"),
            (TileType.BOOKSHELF, "library", "잃어버린 도서관"),
            (TileType.FORGE, "anvil", "전설의 모루"),
            (TileType.GARDEN, "grove", "마법의 숲"),
            (TileType.CRYSTAL, "gem", "신비한 보석"),
            (TileType.LEVER, "mechanism", "고대 기계장치"),
            (TileType.CHEST, "vault", "고대 금고")
        ]
        
        # 부정적 요소들 (20% 확률)
        negative_features = [
            (TileType.CURSED_ALTAR, "cursed_altar", "저주받은 제단"),
            (TileType.POISON_CLOUD, "poison_cloud", "독성 구름"),
            (TileType.DARK_PORTAL, "dark_portal", "어둠의 포털"),
            (TileType.CURSED_CHEST, "cursed_chest", "저주받은 상자"),
            (TileType.UNSTABLE_FLOOR, "unstable_floor", "불안정한 바닥")
        ]
        
        # 20% 확률로 부정적 요소, 80% 확률로 긍정적 요소
        if random.random() < 0.2:
            features = negative_features
        else:
            features = good_features
        
        feature_type, feature_id, feature_name = random.choice(features)
        
        # 배치 가능한 위치 찾기
        safe_radius = 7  # 플레이어 스폰 지점 반지름 7블록 내 기믹 생성 금지
        for offset in range(1, 3):
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    x, y = center_x + dx, center_y + dy
                    
                    # 플레이어 스폰 지점과의 거리 계산
                    distance_from_player = ((x - self.player_pos[0]) ** 2 + (y - self.player_pos[1]) ** 2) ** 0.5
                    
                    if (self.is_valid_pos(x, y) and 
                        self.tiles[y][x].type == TileType.FLOOR and
                        (x, y) not in self.enemies_positions and
                        (x, y) not in self.items_positions and
                        distance_from_player >= safe_radius):  # 스폰 지점에서 충분히 멀리
                        
                        # 특수 요소 배치
                        self.tiles[y][x].type = feature_type
                        
                        # 특수 속성 설정
                        if feature_type == TileType.CHEST:
                            self.tiles[y][x].is_locked = random.choice([True, False])
                            self.tiles[y][x].treasure_quality = random.choice(["common", "rare", "epic"])
                            self.treasure_chests.append((x, y))
                        elif feature_type == TileType.LEVER:
                            self.tiles[y][x].required_skill = "기계조작"
                            self.interactive_objects.append((x, y))
                        elif feature_type == TileType.ALTAR:
                            self.tiles[y][x].required_skill = "신성마법"
                            self.interactive_objects.append((x, y))
                        elif feature_type == TileType.BOOKSHELF:
                            self.tiles[y][x].required_skill = "지식탐구"
                            self.interactive_objects.append((x, y))
                        elif feature_type == TileType.FORGE:
                            self.tiles[y][x].required_skill = "기계공학"
                            self.interactive_objects.append((x, y))
                        elif feature_type == TileType.GARDEN:
                            self.tiles[y][x].required_skill = "자연친화"
                            self.interactive_objects.append((x, y))
                        elif feature_type == TileType.CRYSTAL:
                            self.tiles[y][x].required_skill = "정령술"
                            self.interactive_objects.append((x, y))
                        
                        # 특수 타일 정보 저장
                        self.special_tiles[(x, y)] = {
                            'type': feature_id,
                            'name': feature_name,
                            'level': self.current_level,
                            'used': False
                        }
                        
                        # print(f"   📍 {feature_name}이(가) ({x}, {y})에 배치됨")  # 숨김
                        return
    
    def _place_corridor_features(self):
        """복도에 함정과 비밀 문 배치"""
        corridor_positions = []
        
        # 복도 타일들 찾기 (방이 아닌 바닥 타일들)
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].type == TileType.FLOOR:
                    # 방 안에 있지 않은 바닥 타일인지 확인
                    in_room = False
                    for room in self.rooms:
                        if (room.x < x < room.x + room.width - 1 and 
                            room.y < y < room.y + room.height - 1):
                            in_room = True
                            break
                    
                    if not in_room:
                        corridor_positions.append((x, y))
        
        # 함정 배치 (복도의 5%로 줄임 + 길막 방지 개선)
        safe_radius = 7  # 플레이어 스폰 지점 반지름 7블록 내 함정 생성 금지
        num_traps = max(1, len(corridor_positions) // 20)  # 기존 10에서 20으로 변경
        if len(corridor_positions) > 0:
            # 스폰 지점에서 안전한 거리에 있는 복도 위치만 필터링
            safe_corridor_positions = []
            for x, y in corridor_positions:
                distance_from_player = ((x - self.player_pos[0]) ** 2 + (y - self.player_pos[1]) ** 2) ** 0.5
                if distance_from_player >= safe_radius:
                    safe_corridor_positions.append((x, y))
            
            if safe_corridor_positions:
                # 길막 방지를 위한 함정 배치
                valid_trap_positions = []
                for x, y in safe_corridor_positions:
                    # 함정을 배치했을 때 길이 막히지 않는지 확인
                    if self._can_place_trap_safely(x, y):
                        valid_trap_positions.append((x, y))
                
                if valid_trap_positions:
                    trap_positions = random.sample(valid_trap_positions, min(num_traps, len(valid_trap_positions)))
                    
                    for x, y in trap_positions:
                        self.tiles[y][x].type = TileType.TRAP
                        self.tiles[y][x].is_trapped = True
                        self.tiles[y][x].required_skill = "함정탐지"
                        self.traps.append((x, y))
                        # print(f"   ⚡ 함정이 ({x}, {y})에 숨겨짐")  # 숨김
                    # print(f"   ⚡ 함정이 ({x}, {y})에 숨겨짐")  # 숨김
        
        # 비밀 문 배치 (벽 중에서)
        self._place_secret_doors()
    
    def _place_secret_doors(self):
        """비밀 문 배치"""
        wall_positions = []
        
        # 방과 복도 사이의 벽 찾기
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.tiles[y][x].type == TileType.WALL:
                    # 양쪽에 바닥이 있는 벽인지 확인
                    adjacent_floors = 0
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (self.is_valid_pos(nx, ny) and 
                            self.tiles[ny][nx].type == TileType.FLOOR):
                            adjacent_floors += 1
                    
                    if adjacent_floors >= 2:  # 2개 이상의 바닥과 인접한 벽
                        wall_positions.append((x, y))
        
        # 비밀 문 배치 (최대 2개)
        safe_radius = 7  # 플레이어 스폰 지점 반지름 7블록 내 비밀 문 생성 금지
        num_secret_doors = min(2, len(wall_positions) // 5)
        if num_secret_doors > 0:
            # 스폰 지점에서 안전한 거리에 있는 벽 위치만 필터링
            safe_wall_positions = []
            for x, y in wall_positions:
                distance_from_player = ((x - self.player_pos[0]) ** 2 + (y - self.player_pos[1]) ** 2) ** 0.5
                if distance_from_player >= safe_radius:
                    safe_wall_positions.append((x, y))
            
            if safe_wall_positions:
                secret_positions = random.sample(safe_wall_positions, min(num_secret_doors, len(safe_wall_positions)))
                
                for x, y in secret_positions:
                    self.tiles[y][x].type = TileType.SECRET_DOOR
                    self.tiles[y][x].required_skill = "비밀탐지"
                    self.secret_doors.append((x, y))
                    # print(f"   🔍 비밀 문이 ({x}, {y})에 숨겨짐")  # 숨김
    
    def _place_locked_doors(self):
        """잠긴 문 배치"""
        # 기존 문들 중 일부를 잠긴 문으로 변경
        door_positions = []
        
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].type == TileType.DOOR:
                    door_positions.append((x, y))
        
        # 30% 확률로 문을 잠금 (스폰 지점에서 안전한 거리의 문만)
        safe_radius = 7  # 플레이어 스폰 지점 반지름 7블록 내 잠긴 문 생성 금지
        for x, y in door_positions:
            # 스폰 지점과의 거리 계산
            distance_from_player = ((x - self.player_pos[0]) ** 2 + (y - self.player_pos[1]) ** 2) ** 0.5
            
            if distance_from_player >= safe_radius and random.random() < 0.3:
                self.tiles[y][x].type = TileType.LOCKED_DOOR
                self.tiles[y][x].is_locked = True
                self.tiles[y][x].required_skill = "자물쇠해제"
                self.locked_doors.append((x, y))
                # print(f"   🔒 잠긴 문이 ({x}, {y})에 배치됨")  # 숨김
                
    def can_move(self, dx: int, dy: int) -> bool:
        """이동 가능한지 확인 - 개선된 오류 처리"""
        try:
            new_x = self.player_pos[0] + dx
            new_y = self.player_pos[1] + dy
            
            # 경계 확인
            if not self.is_valid_pos(new_x, new_y):
                return False
                
            # 타일 확인
            if new_y >= len(self.tiles) or new_x >= len(self.tiles[new_y]):
                return False
                
            tile = self.tiles[new_y][new_x]
            return tile.is_walkable()
            
        except Exception as e:
            print(f"can_move 오류: {e}")
            return False
        
    def move_player(self, dx: int, dy: int):
        """플레이어 이동 - 개선된 아이템 처리"""
        try:
            new_x = self.player_pos[0] + dx
            new_y = self.player_pos[1] + dy
            
            # 이동 가능한지 확인
            if not self.can_move(dx, dy):
                return None  # 이동 불가
            
            # 이동하려는 위치에 적이 있는지 먼저 확인
            if (new_x, new_y) in self.enemies_positions:
                print(f"⚔️ 적과 충돌! 위치: ({new_x}, {new_y})")
                # 적과 충돌 - 주변 적들도 함께 전투에 참여
                nearby_enemies = self.get_nearby_enemies_for_combat(new_x, new_y)
                print(f"🎯 전투 대상: {len(nearby_enemies)}개 위치의 적들")
                return {"type": "combat", "enemies": nearby_enemies, "trigger_pos": (new_x, new_y)}
            
            # 플레이어 위치 업데이트 및 이동거리 추적
            old_pos = self.player_pos
            self.player_pos = (new_x, new_y)
            print(f"🚶 플레이어 이동: {old_pos} → {self.player_pos}")
            
            # 이동거리 추가 (맨하탄 거리)
            movement_distance = abs(dx) + abs(dy)
            self.total_movement_distance += movement_distance
            self.current_run_movement += movement_distance
            self.actions_taken += 1  # 액션 수 증가
            
            # 탐험 추적
            self.track_exploration(new_x, new_y)
            
            self.update_visibility()
            
            # 아이템 획득 체크
            if (new_x, new_y) in self.items_positions:
                item = self.floor_items.get((new_x, new_y))
                if item:
                    print(f"💎 아이템 발견: {item.name}")
                    # 아이템 제거
                    self.items_positions.remove((new_x, new_y))
                    del self.floor_items[(new_x, new_y)]
                    self.tiles[new_y][new_x].has_item = False
                    
                    # 아이템 수집 추적
                    self.track_item_collection()
                    
                    return {"type": "item", "item": item}  # 아이템 반환
            
            # 계단 체크 (다음 층으로 이동)
            if self.tiles[new_y][new_x].type == TileType.STAIRS_DOWN:
                print("🪜 계단 발견! 다음 층으로 이동합니다.")
                # 층 완료 시 통계 계산
                self.track_floor_completion()
                return {"type": "stairs", "direction": "down"}
                
            # 일반 이동 성공
            return {"type": "move", "success": True}
            
        except Exception as e:
            print(f"❌ move_player 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_nearby_enemies_for_combat(self, target_x: int, target_y: int) -> List[Tuple[int, int]]:
        """전투 시 주변 적들을 모아서 반환 (최대 3개 위치, 4마리 적)"""
        combat_enemies = []
        
        # 타겟 위치의 적 먼저 추가
        if (target_x, target_y) in self.enemies_positions:
            combat_enemies.append((target_x, target_y))
        
        # 주변 8방향에서 추가 적들 찾기 (최대 2개 추가 위치)
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for dx, dy in directions:
            if len(combat_enemies) >= 3:  # 최대 3개 위치
                break
                
            check_x = target_x + dx
            check_y = target_y + dy
            
            # 유효한 위치이고 적이 있는지 확인
            if (self.is_valid_pos(check_x, check_y) and 
                (check_x, check_y) in self.enemies_positions and
                (check_x, check_y) not in combat_enemies):
                combat_enemies.append((check_x, check_y))
        
        print(f"⚔️ 전투 시작! {len(combat_enemies)}개 위치의 적들과 교전")
        return combat_enemies
    
    def remove_combat_enemies(self, enemy_positions: List[Tuple[int, int]], game_instance=None):
        """전투 승리 후 적들을 맵에서 제거"""
        for pos in enemy_positions:
            if pos in self.enemies_positions:
                self.enemies_positions.remove(pos)
                x, y = pos
                if self.is_valid_pos(x, y):
                    self.tiles[y][x].type = TileType.FLOOR
                    # 메시지 버퍼 시스템 사용
                    if game_instance and hasattr(game_instance, 'add_game_message'):
                        game_instance.add_game_message(f"💀 적 제거됨: ({x}, {y})")
                    else:
                        print(f"💀 적 제거됨: ({x}, {y})")
        
        # 전체 완료 메시지
        if game_instance and hasattr(game_instance, 'add_game_message'):
            game_instance.add_game_message(f"✨ {len(enemy_positions)}개 위치의 모든 적이 소멸되었습니다!")
        else:
            print(f"✨ {len(enemy_positions)}개 위치의 모든 적이 소멸되었습니다!")
                
    def is_valid_pos(self, x: int, y: int) -> bool:
        """유효한 위치인지 확인"""
        return 0 <= x < self.width and 0 <= y < self.height
        
    def update_visibility(self):
        """시야 업데이트 (파티 장비 기반 시야 시스템)"""
        player_x, player_y = self.player_pos
        
        # 파티 매니저가 있으면 장비 효과를 고려한 시야 범위 사용
        if self.party_manager:
            sight_range = self.party_manager.get_total_vision_range()
        else:
            sight_range = 3  # 기본 시야 범위
        
        # 모든 타일을 보이지 않게 설정
        for row in self.tiles:
            for tile in row:
                tile.visible = False
                
        # 플레이어 주변 시야 범위 내 타일들을 보이게 설정
        for dy in range(-sight_range, sight_range + 1):
            for dx in range(-sight_range, sight_range + 1):
                x, y = player_x + dx, player_y + dy
                
                if self.is_valid_pos(x, y):
                    # 거리 계산
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    if distance <= sight_range:
                        self.tiles[y][x].visible = True
                        self.tiles[y][x].explored = True
                        
    def get_map_display(self, display_width: int = 30, display_height: int = 20) -> List[str]:
        """화면에 표시할 맵 반환 (크기 증가, 시야 시스템 적용)"""
        player_x, player_y = self.player_pos
        
        # 플레이어 중심으로 맵 영역 계산
        start_x = max(0, player_x - display_width // 2)
        start_y = max(0, player_y - display_height // 2)
        end_x = min(self.width, start_x + display_width)
        end_y = min(self.height, start_y + display_height)
        
        # 실제 표시 영역 조정
        start_x = max(0, end_x - display_width)
        start_y = max(0, end_y - display_height)
        
        display_lines = []
        
        for y in range(start_y, end_y):
            line = ""
            for x in range(start_x, end_x):
                # 시야 시스템 적용 - 보이는 곳만 표시
                if not self.is_valid_pos(x, y):
                    char = " "
                elif not self.tiles[y][x].visible:
                    # 탐험했지만 시야에 없는 곳
                    if self.tiles[y][x].explored:
                        # 탐험된 지역의 지형정보 표시
                        tile_char = self.tiles[y][x].get_display_char()
                        if tile_char == "#":  # 벽
                            char = "#"  # 탐험된 벽
                        elif tile_char == ".":  # 바닥
                            char = "·"  # 탐험된 바닥 (작은 점)
                        elif tile_char == "+":  # 문
                            char = "+"  # 탐험된 문
                        elif tile_char in ["<", ">"]:  # 계단
                            char = tile_char  # 탐험된 계단
                        else:
                            char = "·"  # 기타 탐험된 지역
                    else:
                        char = " "  # 미탐험 지역
                else:
                    # 시야 안에 있는 곳
                    if x == player_x and y == player_y:
                        char = "@"  # 플레이어
                    elif (x, y) in self.enemies_positions:
                        char = "E"  # 적 (레벨 숨김)
                    elif (x, y) in self.items_positions:
                        # 아이템 타입에 따른 표시
                        item = self.floor_items.get((x, y))
                        if item:
                            char = item.get_display_char()
                        else:
                            char = "!"  # 기본 아이템
                    else:
                        char = self.tiles[y][x].get_display_char()
                
                # 글자 사이에 스페이스 추가하여 원형에 가까운 시야 만들기
                line += char + " "
                    
            display_lines.append(line)
            
        return display_lines
    
    def get_colored_map_display(self, display_width: int = 30, display_height: int = 20) -> List[str]:
        """색상이 적용된 맵 표시 반환 (시야 시스템 적용)"""
        player_x, player_y = self.player_pos
        
        # 플레이어 중심으로 맵 영역 계산
        start_x = max(0, player_x - display_width // 2)
        start_y = max(0, player_y - display_height // 2)
        end_x = min(self.width, start_x + display_width)
        end_y = min(self.height, start_y + display_height)
        
        # 실제 표시 영역 조정
        start_x = max(0, end_x - display_width)
        start_y = max(0, end_y - display_height)
        
        display_lines = []
        
        for y in range(start_y, end_y):
            line = ""
            for x in range(start_x, end_x):
                # 시야 시스템 적용
                if not self.is_valid_pos(x, y):
                    char = " "
                elif not self.tiles[y][x].visible:
                    # 탐험했지만 시야에 없는 곳
                    if self.tiles[y][x].explored:
                        # 탐험된 지역의 지형정보를 회색으로 표시
                        tile_char = self.tiles[y][x].get_display_char()
                        if tile_char == "#":  # 벽을 회색으로
                            char = bright_black("#")  # 회색 벽
                        elif tile_char == ".":  # 바닥을 회색으로
                            char = bright_black("·")  # 회색 바닥 (작은 점)
                        elif tile_char == "+":  # 문을 회색으로
                            char = bright_black("+")  # 회색 문
                        elif tile_char == "&":  # 잠긴 문을 회색으로
                            char = bright_black("&")  # 회색 잠긴 문
                        elif tile_char == "?":  # 비밀 문을 회색으로
                            char = bright_black("?")  # 회색 비밀 문
                        elif tile_char == "=":  # 보물상자를 회색으로
                            char = bright_black("=")  # 회색 보물상자
                        elif tile_char == "^":  # 함정을 회색으로
                            char = bright_black("^")  # 회색 함정
                        elif tile_char == "/":  # 레버를 회색으로
                            char = bright_black("/")  # 회색 레버
                        elif tile_char == "T":  # 제단을 회색으로
                            char = bright_black("T")  # 회색 제단
                        elif tile_char == "~":  # 분수를 회색으로
                            char = bright_black("~")  # 회색 분수
                        elif tile_char == "B":  # 책장을 회색으로
                            char = bright_black("B")  # 회색 책장
                        elif tile_char == "F":  # 대장간을 회색으로
                            char = bright_black("F")  # 회색 대장간
                        elif tile_char == "G":  # 정원을 회색으로
                            char = bright_black("G")  # 회색 정원
                        elif tile_char == "*":  # 마법 수정을 회색으로
                            char = bright_black("*")  # 회색 마법 수정
                        elif tile_char in ["<", ">"]:  # 계단을 회색으로
                            char = bright_black(tile_char)  # 회색 계단
                        # 부정적 요소들도 회색으로 표시
                        elif tile_char == "X":  # 저주받은 제단
                            char = bright_black("X")
                        elif tile_char == "P":  # 독구름
                            char = bright_black("P")
                        elif tile_char == "O":  # 어둠의 포털
                            char = bright_black("O")
                        elif tile_char == "C":  # 저주받은 상자
                            char = bright_black("C")
                        elif tile_char == "U":  # 불안정한 바닥
                            char = bright_black("U")
                        else:
                            char = bright_black("·")  # 기타 탐험된 지역
                    else:
                        char = " "  # 미탐험 지역
                else:
                    # 시야 안에 있는 곳만 표시
                    if x == player_x and y == player_y:
                        char = bright_yellow("@", True)  # 플레이어 (밝은 노랑)
                    elif (x, y) in self.enemies_positions:
                        # 적 - 빨간색으로 통일
                        char = bright_red("E", True)  # 적 (밝은 빨간색)
                    elif (x, y) in self.items_positions:
                        # 아이템 타입에 따른 색상
                        item = self.floor_items.get((x, y))
                        if item:
                            item_char = item.get_display_char()
                            # 희귀도별 색상
                            if hasattr(item, 'rarity'):
                                char = rarity_colored(item_char, item.rarity.value)
                            else:
                                char = bright_green(item_char)  # 기본 아이템 색상
                        else:
                            char = bright_green("!")  # 기본 아이템
                    else:
                        # 타일 타입별 색상
                        tile_char = self.tiles[y][x].get_display_char()
                        if tile_char == "#":  # 벽
                            char = cyan(tile_char)
                        elif tile_char == ".":  # 바닥
                            char = bright_white("·")  # 작은 점으로 통일
                        elif tile_char == "+":  # 문
                            char = yellow(tile_char)
                        elif tile_char == "&":  # 잠긴 문
                            char = bright_red(tile_char)
                        elif tile_char == "?":  # 비밀 문 (발견됨)
                            char = magenta(tile_char)
                        elif tile_char == "=":  # 보물상자
                            char = bright_yellow(tile_char, True)
                        elif tile_char == "^":  # 함정 (탐지됨)
                            char = bright_red(tile_char, True)
                        elif tile_char == "/":  # 레버
                            char = cyan(tile_char, True)
                        elif tile_char == "T":  # 제단
                            char = bright_white(tile_char, True)
                        elif tile_char == "~":  # 분수
                            char = bright_blue(tile_char)
                        elif tile_char == "B":  # 책장
                            char = yellow(tile_char)
                        elif tile_char == "F":  # 대장간
                            char = bright_red(tile_char)
                        elif tile_char == "G":  # 정원
                            char = bright_green(tile_char)
                        elif tile_char == "*":  # 마법 수정
                            char = magenta(tile_char, True)
                        elif tile_char in ["<", ">"]:  # 계단
                            char = magenta(tile_char, True)
                        # 부정적 요소들 색상
                        elif tile_char == "X":  # 저주받은 제단
                            char = bright_red("X", True)
                        elif tile_char == "P":  # 독구름
                            char = bright_green("P", True)
                        elif tile_char == "O":  # 어둠의 포털
                            char = bright_black("O", True)
                        elif tile_char == "C":  # 저주받은 상자
                            char = red("C", True)
                        elif tile_char == "U":  # 불안정한 바닥
                            char = yellow("U", True)
                        else:
                            char = tile_char
                
                # 글자 사이에 스페이스 추가하여 원형에 가까운 시야 만들기
                line += char + " "
                    
            display_lines.append(line)
            
        return display_lines
        
    def get_tile_char(self, x: int, y: int) -> str:
        """특정 위치의 타일 문자 반환"""
        if not self.is_valid_pos(x, y):
            return " "
            
        if (x, y) == self.player_pos:
            return "@"
        elif (x, y) in self.enemies_positions:
            return "E"
        elif (x, y) in self.items_positions:
            return "!"
        else:
            return self.tiles[y][x].get_display_char()
            
    def get_enemies_near_player(self, range_limit: int = 1) -> List[Tuple[int, int]]:
        """플레이어 근처의 적들 반환"""
        player_x, player_y = self.player_pos
        nearby_enemies = []
        
        for enemy_pos in self.enemies_positions:
            enemy_x, enemy_y = enemy_pos
            distance = abs(enemy_x - player_x) + abs(enemy_y - player_y)  # 맨하탄 거리
            
            if distance <= range_limit:
                nearby_enemies.append(enemy_pos)
                
        return nearby_enemies
    
    def check_enemy_collision(self) -> bool:
        """플레이어가 적과 충돌했는지 확인"""
        return self.player_pos in self.enemies_positions
    
    def get_enemy_at_position(self, pos: Tuple[int, int]) -> bool:
        """특정 위치에 적이 있는지 확인"""
        return pos in self.enemies_positions
        
    def remove_enemy(self, pos: Tuple[int, int]):
        """적 제거"""
        if pos in self.enemies_positions:
            self.enemies_positions.remove(pos)
            # 적 정보도 함께 제거
            if pos in self.floor_enemies:
                del self.floor_enemies[pos]
            x, y = pos
            self.tiles[y][x].has_enemy = False
            
    def add_enemy(self, pos: Tuple[int, int]):
        """적 추가"""
        x, y = pos
        if self.is_valid_pos(x, y) and self.tiles[y][x].is_walkable():
            self.enemies_positions.append(pos)
            self.tiles[y][x].has_enemy = True
            return True
        return False
        
    def get_random_floor_position(self) -> Tuple[int, int]:
        """랜덤한 바닥 위치 반환"""
        attempts = 0
        while attempts < 100:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            if (self.tiles[y][x].type == TileType.FLOOR and
                (x, y) != self.player_pos and
                (x, y) not in self.enemies_positions and
                (x, y) not in self.items_positions):
                return (x, y)
                
            attempts += 1
            
        # 실패 시 플레이어 근처 반환
        return (self.player_pos[0] + 1, self.player_pos[1])
        
    def generate_next_level(self):
        """다음 레벨 생성"""
        self.current_level += 1
        self.initialize_world()
        self.generate_level()
        print(f"레벨 {self.current_level}로 이동했습니다!")
        
    def move_enemies(self):
        """적들의 AI 이동 처리"""
        if not self.enemies_positions:
            return
            
        player_x, player_y = self.player_pos
        new_positions = []
        
        for enemy_pos in self.enemies_positions:
            enemy_x, enemy_y = enemy_pos
            
            # 플레이어와의 거리 계산
            distance = abs(enemy_x - player_x) + abs(enemy_y - player_y)
            
            # 시야 범위 안에 있는 적만 이동 (5 타일 이내)
            if distance <= 5 and self.tiles[enemy_y][enemy_x].visible:
                # 플레이어를 향해 이동
                new_x, new_y = enemy_x, enemy_y
                
                if enemy_x < player_x and self._can_move_to(enemy_x + 1, enemy_y):
                    new_x = enemy_x + 1
                elif enemy_x > player_x and self._can_move_to(enemy_x - 1, enemy_y):
                    new_x = enemy_x - 1
                elif enemy_y < player_y and self._can_move_to(enemy_x, enemy_y + 1):
                    new_y = enemy_y + 1
                elif enemy_y > player_y and self._can_move_to(enemy_x, enemy_y - 1):
                    new_y = enemy_y - 1
                
                # 적 정보 업데이트
                if (new_x, new_y) != (enemy_x, enemy_y):
                    # 이전 위치 정리
                    if self.is_valid_pos(enemy_x, enemy_y):
                        self.tiles[enemy_y][enemy_x].has_enemy = False
                    
                    # 새 위치 설정
                    if self.is_valid_pos(new_x, new_y):
                        self.tiles[new_y][new_x].has_enemy = True
                    
                    # 적 데이터 이동
                    if (enemy_x, enemy_y) in self.floor_enemies:
                        enemy_data = self.floor_enemies.pop((enemy_x, enemy_y))
                        self.floor_enemies[(new_x, new_y)] = enemy_data
                    
                    new_positions.append((new_x, new_y))
                else:
                    new_positions.append((enemy_x, enemy_y))
            else:
                # 시야 밖의 적은 랜덤 이동 (25% 확률)
                if random.random() < 0.25:
                    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    random.shuffle(directions)
                    
                    for dx, dy in directions:
                        new_x, new_y = enemy_x + dx, enemy_y + dy
                        if self._can_move_to(new_x, new_y):
                            # 이전 위치 정리
                            if self.is_valid_pos(enemy_x, enemy_y):
                                self.tiles[enemy_y][enemy_x].has_enemy = False
                            
                            # 새 위치 설정
                            if self.is_valid_pos(new_x, new_y):
                                self.tiles[new_y][new_x].has_enemy = True
                            
                            # 적 데이터 이동
                            if (enemy_x, enemy_y) in self.floor_enemies:
                                enemy_data = self.floor_enemies.pop((enemy_x, enemy_y))
                                self.floor_enemies[(new_x, new_y)] = enemy_data
                            
                            new_positions.append((new_x, new_y))
                            break
                    else:
                        new_positions.append((enemy_x, enemy_y))
                else:
                    new_positions.append((enemy_x, enemy_y))
        
        self.enemies_positions = new_positions
    
    def _can_move_to(self, x: int, y: int) -> bool:
        """해당 위치로 이동 가능한지 확인"""
        if not self.is_valid_pos(x, y):
            return False
        if not self.tiles[y][x].is_walkable():
            return False
        if (x, y) == self.player_pos:
            return False
        if (x, y) in self.enemies_positions:
            return False
        return True
        
    def track_enemy_defeat(self, enemy_pos: Tuple[int, int]):
        """적 처치 추적"""
        self.performance_metrics['enemies_defeated'] += 1
        self.current_floor_stats['enemies_defeated_on_floor'] += 1
        self.combat_count += 1
        
    def track_item_collection(self):
        """아이템 수집 추적"""
        self.performance_metrics['items_collected'] += 1
        
    def track_exploration(self, x: int, y: int):
        """탐험 추적"""
        if self.is_valid_pos(x, y) and self.tiles[y][x].type == TileType.FLOOR:
            self.current_floor_stats['tiles_explored'].add((x, y))
            
    def track_floor_completion(self):
        """층 완료 추적"""
        self.performance_metrics['floors_cleared'] += 1
        
        # 완벽한 층 체크 (모든 적 처치)
        if (self.current_floor_stats['enemies_defeated_on_floor'] >= 
            self.current_floor_stats['enemies_on_floor']):
            self.performance_metrics['perfect_floors'] += 1
            
        # 탐험률 계산
        if self.current_floor_stats['total_tiles'] > 0:
            exploration_rate = (len(self.current_floor_stats['tiles_explored']) / 
                              self.current_floor_stats['total_tiles'])
            self.performance_metrics['exploration_rate'] = exploration_rate
            
        # 다음 층을 위한 통계 초기화
        self.current_floor_stats['enemies_defeated_on_floor'] = 0
        self.current_floor_stats['tiles_explored'] = set()
        
    def calculate_performance_score(self) -> int:
        """성과 점수 계산 (AFK 방지 포함)"""
        metrics = self.performance_metrics
        
        # 기본 점수 계산
        base_score = (
            metrics['floors_cleared'] * 100 +         # 층당 100점
            metrics['enemies_defeated'] * 10 +        # 적당 10점
            metrics['items_collected'] * 5 +          # 아이템당 5점
            metrics['perfect_floors'] * 50 +          # 완벽한 층당 50점 보너스
            int(metrics['exploration_rate'] * 100) +  # 탐험률 보너스
            metrics['no_damage_combats'] * 20 +       # 무피해 전투당 20점
            metrics['critical_hits'] * 2 +            # 크리티컬당 2점
            metrics['skills_used'] * 3                # 스킬 사용당 3점
        )
        
        # AFK 방지: 액션 대비 성과 비율 체크
        if self.actions_taken > 0:
            efficiency_ratio = base_score / self.actions_taken
            if efficiency_ratio < 0.5:  # 너무 비효율적인 플레이
                base_score = int(base_score * 0.7)  # 30% 감소
            elif efficiency_ratio > 2.0:  # 매우 효율적인 플레이
                base_score = int(base_score * 1.2)  # 20% 보너스
                
        return max(0, base_score)
        
    def get_star_fragment_reward(self) -> int:
        """별조각 보상 계산 (성과 기반)"""
        performance_score = self.calculate_performance_score()
        metrics = self.performance_metrics
        
        # 기본 보상 (성과 점수 기반)
        base_reward = performance_score // 10  # 10점당 1개
        
        # 특별 보너스
        bonus_reward = 0
        
        # 층수 보너스 (층당 5개)
        bonus_reward += metrics['floors_cleared'] * 5
        
        # 완벽한 층 보너스 (완벽한 층당 추가 10개)
        bonus_reward += metrics['perfect_floors'] * 10
        
        # 탐험 보너스 (90% 이상 탐험시 보너스)
        if metrics['exploration_rate'] >= 0.9:
            bonus_reward += metrics['floors_cleared'] * 5
            
        # 효율성 보너스 (무피해 전투가 많으면)
        if metrics['no_damage_combats'] >= 5:
            bonus_reward += 20
            
        # 연속 성공 보너스 (층수가 높아질수록)
        if metrics['floors_cleared'] >= 10:
            bonus_reward += 30
        elif metrics['floors_cleared'] >= 5:
            bonus_reward += 15
            
        total_reward = base_reward + bonus_reward
        
        # 난이도별 별조각 배율 적용
        try:
            from config import game_config
            difficulty_multiplier = game_config.get_difficulty_setting('star_fragment_multiplier')
            total_reward = int(total_reward * difficulty_multiplier)
        except:
            pass  # 설정 로드 실패시 기본값 유지
        
        # 최소 보상 보장 (어려움 보정)
        min_reward = metrics['floors_cleared'] * 3  # 층당 최소 3개
        
        return max(min_reward, total_reward)
        
    def _calculate_floor_stats(self):
        """현재 층의 통계 계산"""
        # 총 바닥 타일 수 계산
        total_floor_tiles = 0
        for row in self.tiles:
            for tile in row:
                if tile.type == TileType.FLOOR:
                    total_floor_tiles += 1
                    
        self.current_floor_stats['total_tiles'] = total_floor_tiles
        self.current_floor_stats['enemies_on_floor'] = len(self.enemies_positions)
        
        # print(f"층 {self.current_level} 통계: 바닥 타일 {total_floor_tiles}개, 적 {len(self.enemies_positions)}마리")  # 숨김
    
    def get_interactable_nearby(self, player_pos: Tuple[int, int]) -> List[Dict]:
        """플레이어 주변의 상호작용 가능한 객체들 반환"""
        px, py = player_pos
        interactables = []
        
        # 인접한 8방향 + 현재 위치 확인
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x, y = px + dx, py + dy
                if not self.is_valid_pos(x, y):
                    continue
                
                tile = self.tiles[y][x]
                if not tile.visible and not tile.explored:
                    continue
                
                interaction_info = None
                
                # 각 타일 타입별 상호작용 정보
                if tile.type == TileType.LOCKED_DOOR:
                    interaction_info = {
                        'pos': (x, y),
                        'type': 'locked_door',
                        'name': '잠긴 문',
                        'required_skill': '자물쇠해제',
                        'required_classes': ['도적', '궁수'],
                        'description': '열쇠나 자물쇠 해제 기술이 필요합니다.'
                    }
                elif tile.type == TileType.SECRET_DOOR and not tile.secret_revealed:
                    interaction_info = {
                        'pos': (x, y),
                        'type': 'secret_door',
                        'name': '의심스러운 벽',
                        'required_skill': '비밀탐지',
                        'required_classes': ['도적', '궁수', '철학자'],
                        'description': '뭔가 숨겨진 것이 있는 것 같습니다.'
                    }
                elif tile.type == TileType.TRAP and not tile.trap_detected:
                    # 함정은 스킬이 있어야 감지됨
                    if self._party_has_field_skill('함정탐지'):
                        interaction_info = {
                            'pos': (x, y),
                            'type': 'trap',
                            'name': '숨겨진 함정',
                            'required_skill': '함정해제',
                            'required_classes': ['도적', '궁수'],
                            'description': '조심스럽게 해제할 수 있습니다.'
                        }
                elif tile.type == TileType.CHEST:
                    chest_name = f"{'잠긴 ' if tile.is_locked else ''}보물상자"
                    interaction_info = {
                        'pos': (x, y),
                        'type': 'treasure_chest',
                        'name': chest_name,
                        'required_skill': '자물쇠해제' if tile.is_locked else None,
                        'required_classes': ['도적', '궁수'] if tile.is_locked else [],
                        'description': f'{tile.treasure_quality.title()} 등급의 보물이 들어있을 것 같습니다.'
                    }
                elif tile.type in [TileType.ALTAR, TileType.LEVER, TileType.BOOKSHELF, 
                                 TileType.FORGE, TileType.GARDEN, TileType.CRYSTAL,
                                 TileType.CURSED_ALTAR, TileType.POISON_CLOUD, TileType.DARK_PORTAL,
                                 TileType.CURSED_CHEST, TileType.UNSTABLE_FLOOR]:
                    special_info = self.special_tiles.get((x, y), {})
                    skill_map = {
                        TileType.ALTAR: ('신성마법', ['성기사', '신관']),
                        TileType.LEVER: ('기계조작', ['기계공학자', '도적']),
                        TileType.BOOKSHELF: ('지식탐구', ['철학자', '아크메이지']),
                        TileType.FORGE: ('기계공학', ['기계공학자']),
                        TileType.GARDEN: ('자연친화', ['드루이드']),
                        TileType.CRYSTAL: ('정령술', ['정령술사', '아크메이지']),
                        # 부정적 요소들
                        TileType.CURSED_ALTAR: ('신성마법', ['성기사', '신관']),
                        TileType.POISON_CLOUD: ('자연친화', ['드루이드']),
                        TileType.DARK_PORTAL: ('정령술', ['정령술사', '아크메이지']),
                        TileType.CURSED_CHEST: ('자물쇠해제', ['도적', '궁수']),
                        TileType.UNSTABLE_FLOOR: ('기계조작', ['기계공학자', '도적'])
                    }
                    
                    type_map = {
                        TileType.ALTAR: 'altar',
                        TileType.LEVER: 'lever',
                        TileType.BOOKSHELF: 'bookshelf',
                        TileType.FORGE: 'forge',
                        TileType.GARDEN: 'garden',
                        TileType.CRYSTAL: 'crystal',
                        # 부정적 요소들
                        TileType.CURSED_ALTAR: 'cursed_altar',
                        TileType.POISON_CLOUD: 'poison_cloud',
                        TileType.DARK_PORTAL: 'dark_portal',
                        TileType.CURSED_CHEST: 'cursed_chest',
                        TileType.UNSTABLE_FLOOR: 'unstable_floor'
                    }
                    
                    skill, classes = skill_map.get(tile.type, ('알 수 없음', []))
                    interaction_info = {
                        'pos': (x, y),
                        'type': type_map.get(tile.type, 'special_object'),
                        'name': special_info.get('name', '신비한 물체'),
                        'required_skill': skill,
                        'required_classes': classes,
                        'description': f'{"이미 사용됨" if special_info.get("used") else "특별한 효과를 얻을 수 있을 것 같습니다."}',
                        'used': special_info.get('used', False)
                    }
                elif tile.type == TileType.FOUNTAIN:
                    interaction_info = {
                        'pos': (x, y),
                        'type': 'fountain',
                        'name': '치유의 샘',
                        'required_skill': None,
                        'required_classes': [],
                        'description': '깨끗한 물이 흘러나옵니다. 치유 효과가 있을 것 같습니다.'
                    }
                
                if interaction_info:
                    interactables.append(interaction_info)
        
        return interactables
    
    def _party_has_field_skill(self, skill_type: str) -> bool:
        """파티가 특정 필드 스킬을 가지고 있는지 확인 (개선된 필드스킬 시스템 활용)"""
        if not self.party_manager:
            return False
        
        # 필드스킬 시스템 활용
        try:
            from .field_skill_selector import get_field_skill_selector
            field_skill_selector = get_field_skill_selector()
            
            # 직접적으로 스킬 이름 사용
            capable_members = field_skill_selector.get_capable_members(self.party_manager, skill_type)
            return len(capable_members) > 0
            
        except (ImportError, Exception):
            # 필드스킬 시스템 사용 불가 시 폴백
            pass
        
        # 폴백: 기존 직업 기반 체크
        skill_class_map = {
            '함정탐지': ['도적', '궁수', '암살자', '레인저'],
            '함정해제': ['도적', '궁수', '암살자', '기계공학자'],
            '자물쇠해제': ['도적', '궁수', '암살자', '스카웃'],
            '비밀탐지': ['도적', '궁수', '철학자', '스카웃'],
            '신성마법': ['성기사', '신관', '성직자', '클레릭'],
            '기계조작': ['기계공학자', '도적', '궁수'],
            '지식탐구': ['철학자', '아크메이지', '바드'],
            '기계공학': ['기계공학자'],
            '자연친화': ['드루이드', '레인저'],
            '정령술': ['정령술사', '아크메이지', '마법사']
        }
        
        required_classes = skill_class_map.get(skill_type, [])
        for member in self.party_manager.members:
            if member.is_alive and member.character_class in required_classes:
                return True
        
        return False
    
    def interact_with_tile(self, pos: Tuple[int, int], skill_user=None) -> Dict:
        """타일과 상호작용"""
        x, y = pos
        if not self.is_valid_pos(x, y):
            return {'success': False, 'message': '잘못된 위치입니다.'}
        
        tile = self.tiles[y][x]
        result = {'success': False, 'message': '상호작용할 수 없습니다.'}
        
        # 타일 타입별 상호작용 처리
        if tile.type == TileType.LOCKED_DOOR:
            if self._party_has_field_skill('자물쇠해제'):
                tile.type = TileType.DOOR
                tile.is_locked = False
                if (x, y) in self.locked_doors:
                    self.locked_doors.remove((x, y))
                result = {'success': True, 'message': '문을 성공적으로 열었습니다!', 'pause': True}
            else:
                result = {'success': False, 'message': '자물쇠 해제 스킬이 필요합니다.', 'pause': True}
        
        elif tile.type == TileType.SECRET_DOOR:
            if self._party_has_field_skill('비밀탐지'):
                tile.secret_revealed = True
                result = {'success': True, 'message': '비밀 문을 발견했습니다!', 'pause': True}
            else:
                result = {'success': False, 'message': '비밀 탐지 스킬이 필요합니다.', 'pause': True}
        
        elif tile.type == TileType.TRAP:
            if tile.trap_detected:
                if self._party_has_field_skill('함정해제'):
                    tile.type = TileType.FLOOR
                    tile.is_trapped = False
                    if (x, y) in self.traps:
                        self.traps.remove((x, y))
                    result = {'success': True, 'message': '함정을 성공적으로 해제했습니다!', 'pause': True}
                else:
                    result = {'success': False, 'message': '함정 해제 스킬이 필요합니다.', 'pause': True}
            else:
                if self._party_has_field_skill('함정탐지'):
                    tile.trap_detected = True
                    result = {'success': True, 'message': '함정을 발견했습니다!', 'pause': True}
                else:
                    result = {'success': False, 'message': '함정을 감지할 수 없습니다.', 'pause': True}
        
        elif tile.type == TileType.CHEST:
            if tile.is_locked and not self._party_has_field_skill('자물쇠해제'):
                result = {'success': False, 'message': '잠긴 상자입니다. 자물쇠 해제 스킬이 필요합니다.', 'pause': True}
            else:
                # 보물 생성 및 지급
                treasure = self._generate_treasure(tile.treasure_quality)
                tile.type = TileType.FLOOR  # 빈 상자로 변경
                if (x, y) in self.treasure_chests:
                    self.treasure_chests.remove((x, y))
                result = {'success': True, 'message': f'보물상자에서 {treasure}을(를) 발견했습니다!', 'treasure': treasure, 'pause': True}
        
        elif tile.type == TileType.FOUNTAIN:
            # 파티 전체 회복
            healed = 0
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive and member.current_hp < member.max_hp:
                        heal_amount = member.max_hp // 4  # 25% 회복
                        member.current_hp = min(member.max_hp, member.current_hp + heal_amount)
                        healed += 1
            result = {'success': True, 'message': f'치유의 샘에서 {healed}명이 회복되었습니다.', 'pause': True}
        
        elif tile.type == TileType.BOSS:
            # 보스와의 전투 시작
            boss_enemy = None
            if hasattr(self, 'enemies') and self.enemies:
                # 해당 위치의 보스 찾기
                for enemy in self.enemies:
                    if (hasattr(enemy, 'is_boss') and enemy.is_boss and 
                        getattr(enemy, 'x', None) == x and getattr(enemy, 'y', None) == y):
                        boss_enemy = enemy
                        break
                
                # 보스가 없으면 첫 번째 보스 사용
                if not boss_enemy:
                    for enemy in self.enemies:
                        if hasattr(enemy, 'is_boss') and enemy.is_boss:
                            boss_enemy = enemy
                            break
            
            if boss_enemy:
                result = {
                    'success': True, 
                    'message': f'👑 층 보스 {boss_enemy.name}와의 전투가 시작됩니다!',
                    'boss_battle': True,
                    'boss': boss_enemy,
                    'pause': True
                }
            else:
                result = {'success': False, 'message': '보스를 찾을 수 없습니다.', 'pause': True}
        
        elif tile.type in [TileType.ALTAR, TileType.LEVER, TileType.BOOKSHELF, 
                         TileType.FORGE, TileType.GARDEN, TileType.CRYSTAL,
                         TileType.CURSED_ALTAR, TileType.POISON_CLOUD, TileType.DARK_PORTAL,
                         TileType.CURSED_CHEST, TileType.UNSTABLE_FLOOR]:
            special_info = self.special_tiles.get((x, y), {})
            if special_info.get('used'):
                result = {'success': False, 'message': '이미 사용된 물체입니다.', 'pause': True}
            else:
                # 타일 타입별 필요 스킬 결정
                skill_map = {
                    TileType.ALTAR: '신성마법',
                    TileType.LEVER: '기계조작',
                    TileType.BOOKSHELF: '지식탐구',
                    TileType.FORGE: '기계공학',
                    TileType.GARDEN: '자연친화',
                    TileType.CRYSTAL: '정령술',
                    # 부정적 요소들 - 스킬 없이도 상호작용 가능하지만 위험
                    TileType.CURSED_ALTAR: None,
                    TileType.POISON_CLOUD: '자연친화',  # 드루이드가 정화 가능
                    TileType.DARK_PORTAL: '정령술',    # 정령술사가 차단 가능
                    TileType.CURSED_CHEST: None,       # 누구나 열 수 있지만 위험
                    TileType.UNSTABLE_FLOOR: '기계조작'  # 기계공학자가 안전하게 보강 가능
                }
                required_skill = skill_map.get(tile.type, '알 수 없음')
                
                # 부정적 요소들 처리
                if tile.type in [TileType.CURSED_ALTAR, TileType.POISON_CLOUD, TileType.DARK_PORTAL,
                               TileType.CURSED_CHEST, TileType.UNSTABLE_FLOOR]:
                    
                    # 스킬이 있으면 안전하게 처리
                    if required_skill and self._party_has_field_skill(required_skill):
                        effect = self._apply_safe_negative_effect(tile.type, special_info)
                        special_info['used'] = True
                        self.special_tiles[(x, y)] = special_info
                        result = {'success': True, 'message': effect, 'pause': True}
                    else:
                        # 스킬 없이 강제 상호작용 (위험)
                        effect = self._apply_forced_negative_effect(tile.type, special_info)
                        special_info['used'] = True
                        self.special_tiles[(x, y)] = special_info
                        result = {'success': True, 'message': effect, 'pause': True}
                else:
                    # 긍정적 요소들 처리
                    if self._party_has_field_skill(required_skill):
                        # 특수 효과 적용
                        effect = self._apply_special_effect(tile.type, special_info)
                        special_info['used'] = True
                        self.special_tiles[(x, y)] = special_info
                        result = {'success': True, 'message': effect, 'pause': True}
                    else:
                        result = {'success': False, 'message': f'{required_skill} 스킬이 필요합니다.', 'pause': True}
        
        return result
    
    def _generate_treasure(self, quality: str) -> str:
        """보물 품질에 따른 보물 생성"""
        treasures = {
            'common': ['철 동전 주머니', '작은 치유 포션', '낡은 장비'],
            'rare': ['금 동전 주머니', '마법 포션', '마법 장비'],
            'epic': ['보석 주머니', '전설 포션', '고급 마법 장비']
        }
        
        return random.choice(treasures.get(quality, treasures['common']))
    
    def _apply_special_effect(self, tile_type: TileType, special_info: Dict) -> str:
        """특수 객체 효과 적용 (긍정적 효과 강화)"""
        if tile_type == TileType.ALTAR:
            # 신성한 축복 - 완전 회복 + 추가 보너스
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        member.current_hp = member.max_hp  # 완전 회복
                        member.current_mp = member.max_mp  # 마나 완전 회복
                        # 추가 보너스: 상처 치유
                        if hasattr(member, 'wounds'):
                            member.wounds = max(0, member.wounds - member.max_hp // 4)  # 상처 25% 치유
            return "신성한 축복을 받아 파티 전체가 완전히 회복되고 상처까지 치유되었습니다!"
        
        elif tile_type == TileType.LEVER:
            # 레버 조작 - 유용한 효과들
            effects = [
                "숨겨진 보물방이 개방되었습니다!",
                "함정들이 일시적으로 비활성화되었습니다!",
                "비밀 통로가 나타났습니다!",
                "적들이 잠시 혼란에 빠졌습니다!",
                "마법의 보호막이 활성화되었습니다!"
            ]
            return random.choice(effects)
        
        elif tile_type == TileType.BOOKSHELF:
            # 고대 지식 습득 - 경험치 + 스킬 보너스
            if self.party_manager:
                exp_gain = 50 + (self.current_level * 10)  # 층수에 비례한 경험치
                for member in self.party_manager.members:
                    if member.is_alive and hasattr(member, 'experience'):
                        member.experience += exp_gain
                        # 일시적 지혜 보너스 (마법 공격력 증가)
                        if hasattr(member, 'magic_attack'):
                            temp_bonus = member.magic_attack // 10
                            if not hasattr(member, 'wisdom_bonus'):
                                member.wisdom_bonus = temp_bonus
            return f"고대 지식을 습득하여 모든 파티원이 {exp_gain} 경험치를 얻고 지혜가 증가했습니다!"
        
        elif tile_type == TileType.FORGE:
            # 마법 대장간 - 장비 강화 + 무기 효과
            if self.party_manager:
                enhanced_count = 0
                for member in self.party_manager.members:
                    if member.is_alive:
                        # 임시 공격력 증가
                        if hasattr(member, 'physical_attack'):
                            temp_bonus = member.physical_attack // 10
                            if not hasattr(member, 'forge_bonus'):
                                member.forge_bonus = temp_bonus
                                enhanced_count += 1
                return f"마법 대장간에서 {enhanced_count}명의 장비가 강화되어 공격력이 일시적으로 증가했습니다!"
            return "마법 대장간의 힘을 느꼈지만 강화할 장비가 없습니다."
        
        elif tile_type == TileType.GARDEN:
            # 자연의 축복 - 상태이상 치유 + 생명력 증가
            if self.party_manager:
                healed_conditions = 0
                for member in self.party_manager.members:
                    if member.is_alive:
                        # 상태이상 제거 (독, 화상, 저주 등)
                        if hasattr(member, 'status_effects'):
                            negative_effects = ['독', '화상', '저주', '마비', '침묵']
                            for effect in negative_effects:
                                if effect in member.status_effects:
                                    del member.status_effects[effect]
                                    healed_conditions += 1
                        # 생명력 증가 (일시적)
                        if hasattr(member, 'max_hp'):
                            temp_hp_bonus = member.max_hp // 10
                            member.current_hp = min(member.max_hp + temp_hp_bonus, member.current_hp + temp_hp_bonus)
                return f"자연의 축복을 받아 {healed_conditions}개의 부정적 상태가 치유되고 생명력이 증가했습니다!"
            return "자연의 평화로운 기운을 느꼈습니다."
        
        elif tile_type == TileType.CRYSTAL:
            # 마력 수정 - 마나 충전 + 마법 효율 증가
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        member.current_mp = member.max_mp  # 마나 완전 충전
                        # 마법 효율 증가 (일시적)
                        if hasattr(member, 'magic_attack'):
                            temp_bonus = member.magic_attack // 8
                            if not hasattr(member, 'crystal_bonus'):
                                member.crystal_bonus = temp_bonus
                return "마법 수정에서 마력을 충전하고 마법 효율이 일시적으로 증가했습니다!"
            return "마법 수정의 신비한 힘을 느꼈습니다."
        
        # 부정적 요소들
        elif tile_type == TileType.CURSED_ALTAR:
            # 저주받은 제단 - 체력 감소
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        damage = member.max_hp // 4  # 25% 체력 감소
                        member.current_hp = max(1, member.current_hp - damage)
            return "저주받은 제단의 어둠이 파티를 약화시켰습니다..."
        
        elif tile_type == TileType.POISON_CLOUD:
            # 독성 구름 - 지속 체력 감소 (최대 HP 기반)
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        damage = member.max_hp // 10  # 최대 HP의 10%
                        member.current_hp = max(1, member.current_hp - damage)
            return "독성 구름이 파티를 중독시켰습니다!"
        
        elif tile_type == TileType.DARK_PORTAL:
            # 어둠의 포털 - 적 소환 (실제로는 메시지만)
            return "어둠의 포털에서 불길한 기운이 흘러나왔습니다... 주변이 더 위험해진 것 같습니다."
        
        elif tile_type == TileType.CURSED_CHEST:
            # 저주받은 상자 - 나쁜 효과 + 아이템 (최대 MP 기반)
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        # MP 감소 (최대 MP의 20%)
                        mp_cost = member.max_mp // 5
                        member.current_mp = max(0, member.current_mp - mp_cost)
            return "저주받은 상자를 열었습니다! 마력이 흡수되었지만 귀중한 아이템을 얻었습니다."
        
        elif tile_type == TileType.UNSTABLE_FLOOR:
            # 불안정한 바닥 - 랜덤 피해 (최대 HP 기반)
            if self.party_manager:
                affected_member = random.choice([m for m in self.party_manager.members if m.is_alive])
                if affected_member:
                    base_damage = affected_member.max_hp // 8  # 최대 HP의 12.5%
                    damage = base_damage + random.randint(affected_member.max_hp // 20, affected_member.max_hp // 10)  # +2.5~5% 랜덤
                    affected_member.current_hp = max(1, affected_member.current_hp - damage)
                    return f"불안정한 바닥이 무너져 {affected_member.name}이(가) 부상을 입었습니다!"
            return "불안정한 바닥이 무너졌지만 다행히 피해는 없었습니다."
        
        return "신비한 효과를 받았습니다."
    
    def _apply_forced_negative_effect(self, tile_type: TileType, special_info: Dict) -> str:
        """부정적 요소 강제 상호작용 (스킬 없이) - 더 강한 부정적 효과"""
        if tile_type == TileType.CURSED_ALTAR:
            # 강제 상호작용 시 더 큰 피해
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        damage = member.max_hp // 2  # 최대 HP의 50%
                        member.current_hp = max(1, member.current_hp - damage)
            return "저주받은 제단의 어둠이 파티를 크게 약화시켰습니다! 강제 상호작용의 대가입니다..."
        
        elif tile_type == TileType.POISON_CLOUD:
            # 강제 상호작용 시 더 많은 독 피해
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        damage = 25  # 기본보다 2.5배
                        member.current_hp = max(1, member.current_hp - damage)
            return "독성 구름에 무방비로 노출되어 심각한 중독을 입었습니다!"
        
        elif tile_type == TileType.DARK_PORTAL:
            # 강제 상호작용 시 실제 적 소환 (시뮬레이션)
            return "어둠의 포털을 강제로 건드렸습니다! 강력한 적들이 이 층에 추가로 소환되었습니다..."
        
        elif tile_type == TileType.CURSED_CHEST:
            # 강제 상호작용 시 더 큰 MP 손실 (최대 MP 기반)
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        # MP 대폭 감소 (최대 MP의 40%)
                        mp_cost = member.max_mp * 2 // 5
                        member.current_mp = max(0, member.current_mp - mp_cost)
            return "저주받은 상자를 무리하게 열었습니다! 마력이 대량으로 흡수되었지만 특별한 아이템을 얻었습니다."
        
        elif tile_type == TileType.UNSTABLE_FLOOR:
            # 강제 상호작용 시 모든 파티원에게 피해 (최대 HP 기반)
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        base_damage = member.max_hp // 5  # 최대 HP의 20%
                        damage = base_damage + random.randint(member.max_hp // 10, member.max_hp // 5)  # +10-20% 랜덤
                        member.current_hp = max(1, member.current_hp - damage)
                return "불안정한 바닥을 무리하게 밟았습니다! 모든 파티원이 낙하 피해를 입었습니다!"
            return "불안정한 바닥이 완전히 무너졌습니다!"
        
        return "강제 상호작용으로 인한 예상치 못한 결과가 발생했습니다."
    
    def _apply_safe_negative_effect(self, tile_type: TileType, special_info: Dict) -> str:
        """부정적 요소 안전 처리 (적절한 스킬 보유 시)"""
        if tile_type == TileType.CURSED_ALTAR:
            # 신성마법으로 안전하게 정화
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        # 소량의 체력 감소만
                        damage = member.max_hp // 10  # 10% 체력 감소
                        member.current_hp = max(1, member.current_hp - damage)
                        # 대신 경험치 획득
                        if hasattr(member, 'experience'):
                            member.experience += 30
            return "신성마법으로 저주받은 제단을 정화했습니다. 약간의 피해를 입었지만 경험을 얻었습니다."
        
        elif tile_type == TileType.POISON_CLOUD:
            # 자연친화로 독을 중화
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        damage = member.max_hp // 20  # 최대 HP의 5%
                        member.current_hp = max(1, member.current_hp - damage)
                        # 독 저항력 획득 (일시적)
                        if hasattr(member, 'poison_resistance'):
                            member.poison_resistance += 0.2
            return "자연친화 스킬로 독성 구름을 중화시켰습니다. 경미한 피해만 입었습니다."
        
        elif tile_type == TileType.DARK_PORTAL:
            # 정령술로 포털 봉인
            return "정령술로 어둠의 포털을 안전하게 봉인했습니다. 위험한 존재들의 침입을 막았습니다."
        
        elif tile_type == TileType.CURSED_CHEST:
            # 자물쇠해제로 안전하게 열기
            if self.party_manager:
                for member in self.party_manager.members:
                    if member.is_alive:
                        # MP 약간 감소 (최대 MP의 10%)
                        mp_cost = member.max_mp // 10
                        member.current_mp = max(0, member.current_mp - mp_cost)
            return "자물쇠해제 스킬로 저주받은 상자를 안전하게 열었습니다. 약간의 마력만 소모되었습니다."
        
        elif tile_type == TileType.UNSTABLE_FLOOR:
            # 기계조작으로 안정화
            if self.party_manager:
                # 가장 약한 멤버에게만 소량 피해
                weakest_member = min([m for m in self.party_manager.members if m.is_alive], 
                                   key=lambda m: m.current_hp)
                if weakest_member:
                    damage = weakest_member.max_hp // 20  # 최대 HP의 5%
                    weakest_member.current_hp = max(1, weakest_member.current_hp - damage)
                    return f"기계조작으로 바닥을 안정화시켰지만 {weakest_member.name}이(가) 약간 다쳤습니다."
            return "기계조작으로 불안정한 바닥을 완전히 안정화시켰습니다!"
        
        return "스킬을 사용하여 안전하게 처리했습니다."
    
    def show_interaction_message(self, message: str, pause: bool = True, sfx_type: str = None):
        """상호작용 메시지 표시 및 일시정지 (SFX 포함)"""
        import time
        
        # SFX 재생
        if sfx_type:
            try:
                # 오디오 시스템이 있으면 SFX 재생
                from main import DawnOfStellarGame
                if hasattr(DawnOfStellarGame, '_instance') and DawnOfStellarGame._instance:
                    game_instance = DawnOfStellarGame._instance
                    if hasattr(game_instance, 'audio_system') and game_instance.audio_system:
                        game_instance.audio_system.play_sfx(sfx_type)
            except:
                pass  # SFX 재생 실패는 조용히 무시
        
        print(f"\n💬 {message}")
        
        if pause:
            try:
                input("\n🔑 계속하려면 Enter를 누르세요...")
            except:
                # 입력 오류 시 짧은 대기
                time.sleep(1.5)
    

    
    def get_save_data(self) -> Dict:
        """세이브 데이터 생성"""
        # 타일 정보를 직렬화 가능한 형태로 변환
        tiles_data = []
        for y in range(self.height):
            row_data = []
            for x in range(self.width):
                tile = self.tiles[y][x]
                tile_data = {
                    'type': tile.type.value,
                    'visible': tile.visible,
                    'explored': tile.explored,
                    'has_enemy': tile.has_enemy,
                    'has_item': tile.has_item,
                    'is_locked': tile.is_locked,
                    'is_trapped': tile.is_trapped,
                    'trap_detected': tile.trap_detected,
                    'is_activated': tile.is_activated,
                    'required_skill': tile.required_skill,
                    'treasure_quality': tile.treasure_quality,
                    'secret_revealed': tile.secret_revealed
                }
                row_data.append(tile_data)
            tiles_data.append(row_data)
        
        # 방 정보 직렬화
        rooms_data = []
        for room in self.rooms:
            rooms_data.append({
                'x': room.x,
                'y': room.y,
                'width': room.width,
                'height': room.height
            })
        
        # 바닥 아이템 직렬화
        floor_items_data = {}
        for pos, item in self.floor_items.items():
            floor_items_data[f"{pos[0]},{pos[1]}"] = {
                'name': item.name,
                'type': item.type.value,
                'rarity': item.rarity.value,
                'stats': item.stats
            }
        
        return {
            'width': self.width,
            'height': self.height,
            'tiles': tiles_data,
            'rooms': rooms_data,
            'player_pos': list(self.player_pos),
            'current_level': self.current_level,
            'current_floor': self.current_floor,
            'enemies_positions': self.enemies_positions,
            'items_positions': self.items_positions,
            'floor_items': floor_items_data,
            'floor_enemies': self.floor_enemies,
            'special_tiles': self.special_tiles,
            'locked_doors': self.locked_doors,
            'secret_doors': self.secret_doors,
            'traps': self.traps,
            'treasure_chests': self.treasure_chests,
            'interactive_objects': self.interactive_objects,
            'total_movement_distance': self.total_movement_distance,
            'current_run_movement': self.current_run_movement,
            'actions_taken': self.actions_taken,
            'combat_count': self.combat_count,
            'performance_metrics': self.performance_metrics,
            'current_level_seed': self.current_level_seed,  # 현재 층 시드 저장
            'current_floor_stats': {
                'enemies_on_floor': self.current_floor_stats['enemies_on_floor'],
                'enemies_defeated_on_floor': self.current_floor_stats['enemies_defeated_on_floor'],
                'tiles_explored': list(self.current_floor_stats['tiles_explored']),
                'total_tiles': self.current_floor_stats['total_tiles']
            }
        }
    
    def load_from_data(self, data: Dict):
        """세이브 데이터에서 복원"""
        self.width = data['width']
        self.height = data['height']
        self.player_pos = tuple(data['player_pos'])
        self.current_level = data['current_level']
        self.current_floor = data['current_floor']
        self.enemies_positions = data['enemies_positions']
        self.items_positions = data['items_positions']
        self.floor_enemies = data['floor_enemies']
        self.special_tiles = data['special_tiles']
        self.locked_doors = data['locked_doors']
        self.secret_doors = data['secret_doors']
        self.traps = data['traps']
        self.treasure_chests = data['treasure_chests']
        self.interactive_objects = data['interactive_objects']
        self.total_movement_distance = data['total_movement_distance']
        self.current_run_movement = data['current_run_movement']
        self.actions_taken = data['actions_taken']
        self.combat_count = data['combat_count']
        self.performance_metrics = data['performance_metrics']
        
        # 시드 정보 복원 (호환성 확인)
        self.current_level_seed = data.get('current_level_seed', None)
        
        # 타일 복원
        self.tiles = []
        tiles_data = data['tiles']
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile_data = tiles_data[y][x]
                # TileType enum으로 변환
                tile_type = None
                for tile_type_enum in TileType:
                    if tile_type_enum.value == tile_data['type']:
                        tile_type = tile_type_enum
                        break
                
                if tile_type is None:
                    tile_type = TileType.WALL  # 기본값
                
                tile = Tile(tile_type, x, y)
                tile.visible = tile_data['visible']
                tile.explored = tile_data['explored']
                tile.has_enemy = tile_data['has_enemy']
                tile.has_item = tile_data['has_item']
                tile.is_locked = tile_data['is_locked']
                tile.is_trapped = tile_data['is_trapped']
                tile.trap_detected = tile_data['trap_detected']
                tile.is_activated = tile_data['is_activated']
                tile.required_skill = tile_data['required_skill']
                tile.treasure_quality = tile_data['treasure_quality']
                tile.secret_revealed = tile_data['secret_revealed']
                row.append(tile)
            self.tiles.append(row)
        
        # 방 복원
        self.rooms = []
        for room_data in data['rooms']:
            room = Room(room_data['x'], room_data['y'], room_data['width'], room_data['height'])
            self.rooms.append(room)
        
        # 바닥 아이템 복원
        self.floor_items = {}
        floor_items_data = data['floor_items']
        for pos_str, item_data in floor_items_data.items():
            x, y = map(int, pos_str.split(','))
            pos = (x, y)
            
            # Item 객체 재생성
            from .items import ItemDatabase, ItemType, ItemRarity
            item_type = None
            for type_enum in ItemType:
                if type_enum.value == item_data['type']:
                    item_type = type_enum
                    break
            
            item_rarity = None
            for rarity_enum in ItemRarity:
                if rarity_enum.value == item_data['rarity']:
                    item_rarity = rarity_enum
                    break
            
            if item_type and item_rarity:
                from .items import Item
                item = Item(item_data['name'], item_type, item_rarity, item_data['stats'])
                self.floor_items[pos] = item
        
        # 현재 층 통계 복원
        floor_stats_data = data['current_floor_stats']
        self.current_floor_stats = {
            'enemies_on_floor': floor_stats_data['enemies_on_floor'],
            'enemies_defeated_on_floor': floor_stats_data['enemies_defeated_on_floor'],
            'tiles_explored': set(tuple(tile) for tile in floor_stats_data['tiles_explored']),
            'total_tiles': floor_stats_data['total_tiles']
        }

    def show_interaction_message(self, message, wait_for_enter=False, sfx_type=None):
        """상호작용 메시지 표시 (SFX 포함)"""
        # SFX 재생
        if sfx_type and hasattr(self, 'audio_system') and self.audio_system:
            try:
                self.audio_system.play_sfx(sfx_type)
            except Exception as e:
                pass  # SFX 재생 실패 시 무시
        
        print(f"\n💬 {message}")
        
        if wait_for_enter:
            input("\n⏳ Enter를 눌러 계속하세요...")
            print()  # 빈 줄 추가

    def _get_special_element_info(self, element_type):
        """특수 요소 정보 반환"""
        special_elements = {
            'locked_door': {
                'name': '잠긴 문',
                'description': '열쇠나 자물쇠 따기 스킬이 필요한 문',
                'required_skill': '자물쇠 따기'
            },
            'secret_door': {
                'name': '비밀 문',
                'description': '탐지 스킬로 발견할 수 있는 숨겨진 문',
                'required_skill': '탐지'
            },
            'treasure_chest': {
                'name': '보물상자',
                'description': '귀중한 아이템이 들어있는 상자',
                'required_skill': None
            },
            'trap': {
                'name': '함정',
                'description': '해제 스킬로 안전하게 제거할 수 있는 함정',
                'required_skill': '함정 해제'
            },
            'lever': {
                'name': '레버',
                'description': '무언가를 작동시킬 수 있는 기계 장치',
                'required_skill': None
            },
            'altar': {
                'name': '제단',
                'description': '신성한 힘이 깃든 제단 (축복 효과)',
                'required_skill': None
            },
            'fountain': {
                'name': '분수',
                'description': '마법의 물이 흐르는 치유의 분수',
                'required_skill': None
            },
            'bookshelf': {
                'name': '책장',
                'description': '지식이 담긴 고서들이 있는 책장',
                'required_skill': '독서'
            },
            'forge': {
                'name': '대장간',
                'description': '무기와 방어구를 강화할 수 있는 대장간',
                'required_skill': '단조'
            },
            'garden': {
                'name': '정원',
                'description': '약초와 재료를 수집할 수 있는 정원',
                'required_skill': '채집'
            },
            'crystal': {
                'name': '마법 수정',
                'description': '강력한 마법의 힘이 깃든 수정',
                'required_skill': None
            },
            # 부정적 요소들
            'cursed_altar': {
                'name': '저주받은 제단',
                'description': '어둠의 힘이 깃든 위험한 제단',
                'required_skill': None
            },
            'cursed_chest': {
                'name': '저주받은 상자',
                'description': '함정이 있을 수 있는 의심스러운 상자',
                'required_skill': None
            },
            'poison_cloud': {
                'name': '독구름',
                'description': '유독한 가스가 퍼져있는 위험한 지역',
                'required_skill': None
            },
            'dark_portal': {
                'name': '어둠의 포털',
                'description': '미지의 위험으로 연결된 어두운 포털',
                'required_skill': None
            },
            'unstable_floor': {
                'name': '불안정한 바닥',
                'description': '언제 무너질지 모르는 위험한 바닥',
                'required_skill': None
            }
        }
        
        return special_elements.get(element_type, None)

    def _can_place_trap_safely(self, trap_x: int, trap_y: int) -> bool:
        """함정을 안전하게 배치할 수 있는지 확인 (길막 방지)"""
        try:
            # 1. 현재 위치가 이동 가능한지 확인
            if not self.tiles[trap_y][trap_x].is_walkable():
                return False
            
            # 2. 임시로 함정을 배치해보고 길이 막히는지 테스트
            original_type = self.tiles[trap_y][trap_x].type
            original_walkable = self.tiles[trap_y][trap_x].is_walkable
            
            # 임시로 함정 설정
            self.tiles[trap_y][trap_x].type = TileType.TRAP
            self.tiles[trap_y][trap_x].is_trapped = True
            
            # 3. 플레이어에서 계단까지의 경로가 여전히 존재하는지 확인
            can_reach_stairs = self._can_reach_stairs_from_player()
            
            # 4. 원래 상태로 복구
            self.tiles[trap_y][trap_x].type = original_type
            self.tiles[trap_y][trap_x].is_trapped = False
            
            return can_reach_stairs
            
        except Exception as e:
            print(f"함정 배치 안전성 검사 오류: {e}")
            return False
    
    def _can_reach_stairs_from_player(self) -> bool:
        """플레이어 위치에서 계단까지 도달 가능한지 BFS로 확인"""
        try:
            # 계단 위치 찾기
            stairs_pos = None
            for y in range(self.height):
                for x in range(self.width):
                    if self.tiles[y][x].type == TileType.STAIRS_DOWN:
                        stairs_pos = (x, y)
                        break
                if stairs_pos:
                    break
            
            if not stairs_pos:
                return True  # 계단이 없으면 일단 안전하다고 가정
            
            # BFS로 경로 탐색
            from collections import deque
            
            queue = deque([self.player_pos])
            visited = {self.player_pos}
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            
            while queue:
                x, y = queue.popleft()
                
                # 계단에 도달했으면 성공
                if (x, y) == stairs_pos:
                    return True
                
                # 인접한 칸들 탐색
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    
                    # 경계 체크
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        # 방문하지 않은 이동 가능한 칸
                        if (nx, ny) not in visited and self.tiles[ny][nx].is_walkable():
                            # 함정은 이동 가능하지만 스킬이 필요하므로 경로로 인정
                            # (함정탐지 스킬 없어도 피해 받고 지나갈 수 있음)
                            visited.add((nx, ny))
                            queue.append((nx, ny))
            
            # 계단에 도달할 수 없음
            return False
            
        except Exception as e:
            print(f"경로 탐색 오류: {e}")
            return True  # 오류 시 안전하다고 가정
