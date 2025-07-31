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
    STAIRS_UP = "<"
    STAIRS_DOWN = ">"
    PLAYER = "@"
    ENEMY = "E"
    ITEM = "!"
    TREASURE = "$"


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
        
    def get_display_char(self) -> str:
        """표시할 문자 반환"""
        if not self.explored:
            return " "
        elif not self.visible:
            return "·"  # 어둠 속에서 탐험한 곳
        else:
            return self.type.value
            
    def is_walkable(self) -> bool:
        """이동 가능한지 확인"""
        return self.type in [TileType.FLOOR, TileType.DOOR, 
                           TileType.STAIRS_UP, TileType.STAIRS_DOWN,
                           TileType.ITEM, TileType.TREASURE]


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
    
    def __init__(self, width: int = 80, height: int = 25, party_manager=None):
        self.width = width
        self.height = height
        self.party_manager = party_manager  # 파티 매니저 참조 추가
        self.tiles: List[List[Tile]] = []
        self.rooms: List[Room] = []
        self.player_pos = (0, 0)
        self.current_level = 1
        self.current_floor = 1  # current_level의 별칭
        self.enemies_positions: List[Tuple[int, int]] = []
        self.items_positions: List[Tuple[int, int]] = []
        self.floor_items: Dict[Tuple[int, int], Item] = {}  # 위치별 아이템 매핑
        self.floor_enemies: Dict[Tuple[int, int], Dict] = {}  # 위치별 적 정보 매핑 (레벨 등)
        
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
            
    def generate_level(self):
        """레벨 생성 (던전 생성) - 고정 씨드 사용"""
        # 층수 기반 고정 씨드 설정 (같은 층은 항상 같은 결과)
        level_seed = hash(f"level_{self.current_level}") % (2**32)
        random.seed(level_seed)
        print(f"레벨 {self.current_level} 던전 생성 (씨드: {level_seed})")
        
        self.rooms = []
        self.enemies_positions = []
        self.items_positions = []
        self.floor_items = {}
        self.floor_enemies = {}  # 적 정보도 초기화
        
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
        
        # 계단 배치 (다음 층으로 가는 계단)
        self.place_stairs()
        
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
        """적 배치 - 플레이어 스폰 지점 근처 안전 반지름 적용"""
        num_enemies = random.randint(3, 8)
        safe_radius = 7  # 플레이어 스폰 지점 반지름 7블록 내 적 생성 금지
        
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
                    
                    if (self.tiles[y][x].type == TileType.FLOOR and 
                        (x, y) != self.player_pos and
                        (x, y) not in self.enemies_positions and
                        (x, y) not in self.items_positions):
                        
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
            print(f"다음 층으로 가는 계단이 ({stair_x}, {stair_y})에 배치되었습니다.")
                
    def can_move(self, dx: int, dy: int) -> bool:
        """이동 가능한지 확인"""
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        return self.is_valid_pos(new_x, new_y) and self.tiles[new_y][new_x].is_walkable()
        
    def move_player(self, dx: int, dy: int):
        """플레이어 이동"""
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        if self.can_move(dx, dy):
            # 이동하려는 위치에 적이 있는지 먼저 확인
            if (new_x, new_y) in self.enemies_positions:
                # 적과 충돌 - 전투 시작
                return "combat"
            
            self.player_pos = (new_x, new_y)
            self.update_visibility()
            
            # 아이템 획득 체크
            if (new_x, new_y) in self.items_positions:
                item = self.floor_items.get((new_x, new_y))
                if item:
                    self.items_positions.remove((new_x, new_y))
                    del self.floor_items[(new_x, new_y)]
                    self.tiles[new_y][new_x].has_item = False
                    print(f"{item.get_colored_name()}을(를) 발견했습니다!")
                    return item  # 아이템 반환하여 인벤토리에 추가할 수 있도록
            
            # 계단 체크 (다음 층으로 이동)
            if self.tiles[new_y][new_x].type == TileType.STAIRS_DOWN:
                return "next_floor"
                
        return None
                
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
                        char = "·"  # 어둠
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
                        char = bright_black("·")  # 어둠
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
                            char = bright_white(tile_char)
                        elif tile_char == "+":  # 문
                            char = yellow(tile_char)
                        elif tile_char in ["<", ">"]:  # 계단
                            char = magenta(tile_char, True)
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
