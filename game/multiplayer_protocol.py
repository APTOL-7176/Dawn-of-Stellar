"""
📡 Dawn of Stellar - 멀티플레이어 메시지 프로토콜
Phase 1: 게임 상태 동기화를 위한 메시지 프로토콜 정의

이 모듈은 멀티플레이어 게임에서 사용되는 모든 메시지 타입과
데이터 구조를 정의합니다. 게임 상태, 전투 액션, 플레이어 행동 등의
동기화를 위한 표준화된 프로토콜을 제공합니다.
"""

from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
import json
import time
from game.character import Character
from game.error_logger import log_debug

class GameMessageType(Enum):
    """게임 메시지 타입 - 게임 로직 전용"""
    
    # 게임 상태 동기화
    GAME_STATE_SYNC = "game_state_sync"
    DUNGEON_STATE = "dungeon_state"
    PARTY_STATE = "party_state"
    
    # 플레이어 액션
    PLAYER_MOVE = "player_move"
    PLAYER_INTERACT = "player_interact"
    MENU_ACTION = "menu_action"
    
    # 전투 시스템
    COMBAT_START = "combat_start"
    COMBAT_ACTION = "combat_action"
    COMBAT_STATE = "combat_state"
    COMBAT_END = "combat_end"
    ATB_UPDATE = "atb_update"
    SKILL_USE = "skill_use"
    DAMAGE_DEALT = "damage_dealt"
    
    # 인벤토리 & 아이템
    ITEM_USE = "item_use"
    ITEM_PICKUP = "item_pickup"
    INVENTORY_UPDATE = "inventory_update"
    EQUIPMENT_CHANGE = "equipment_change"
    
    # 턴 기반 액션
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    TURN_ORDER = "turn_order"

@dataclass
class GameMessage:
    """게임 메시지 기본 구조"""
    type: GameMessageType
    sender_id: str
    session_id: str
    turn_number: int
    data: Dict[str, Any]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'type': self.type.value,
            'sender_id': self.sender_id,
            'session_id': self.session_id,
            'turn_number': self.turn_number,
            'data': self.data,
            'timestamp': self.timestamp
        }
    
    def to_json(self) -> str:
        """JSON 직렬화"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'GameMessage':
        """JSON 역직렬화"""
        data = json.loads(json_str)
        return cls(
            type=GameMessageType(data['type']),
            sender_id=data['sender_id'],
            session_id=data['session_id'],
            turn_number=data['turn_number'],
            data=data['data'],
            timestamp=data['timestamp']
        )

# ========== 게임 상태 메시지들 ==========

@dataclass
class PlayerPosition:
    """플레이어 위치 정보"""
    x: int
    y: int
    dungeon_level: int
    facing_direction: Optional[str] = None

@dataclass
class CharacterState:
    """캐릭터 상태 정보"""
    name: str
    level: int
    current_hp: int
    max_hp: int
    current_mp: int
    max_mp: int
    brave_points: int
    atb_gauge: int
    is_alive: bool
    is_broken: bool
    status_effects: List[Dict[str, Any]]
    equipped_items: Dict[str, Any]

@dataclass
class CombatState:
    """전투 상태 정보"""
    is_in_combat: bool
    combat_id: str
    turn_number: int
    current_turn_character: Optional[str]
    party_states: List[CharacterState]
    enemy_states: List[CharacterState]
    turn_order: List[str]

class GameStateProtocol:
    """게임 상태 동기화 프로토콜"""
    
    @staticmethod
    def create_player_move_message(sender_id: str, session_id: str, 
                                 old_pos: PlayerPosition, new_pos: PlayerPosition,
                                 turn_number: int) -> GameMessage:
        """플레이어 이동 메시지 생성"""
        return GameMessage(
            type=GameMessageType.PLAYER_MOVE,
            sender_id=sender_id,
            session_id=session_id,
            turn_number=turn_number,
            data={
                'old_position': asdict(old_pos),
                'new_position': asdict(new_pos),
                'movement_type': 'walk'
            },
            timestamp=time.time()
        )
    
    @staticmethod
    def create_combat_action_message(sender_id: str, session_id: str,
                                   action_type: str, target_id: str,
                                   skill_name: Optional[str], turn_number: int) -> GameMessage:
        """전투 액션 메시지 생성"""
        return GameMessage(
            type=GameMessageType.COMBAT_ACTION,
            sender_id=sender_id,
            session_id=session_id,
            turn_number=turn_number,
            data={
                'action_type': action_type,  # 'attack', 'skill', 'item', 'defend'
                'target_id': target_id,
                'skill_name': skill_name,
                'additional_params': {}
            },
            timestamp=time.time()
        )
    
    @staticmethod
    def create_atb_update_message(sender_id: str, session_id: str,
                                character_id: str, atb_value: int,
                                turn_number: int) -> GameMessage:
        """ATB 게이지 업데이트 메시지"""
        return GameMessage(
            type=GameMessageType.ATB_UPDATE,
            sender_id=sender_id,
            session_id=session_id,
            turn_number=turn_number,
            data={
                'character_id': character_id,
                'atb_value': atb_value,
                'is_ready': atb_value >= 1000  # ATB_READY_THRESHOLD
            },
            timestamp=time.time()
        )
    
    @staticmethod
    def create_damage_message(sender_id: str, session_id: str,
                            attacker_id: str, target_id: str,
                            damage_amount: int, damage_type: str,
                            turn_number: int) -> GameMessage:
        """데미지 메시지 생성"""
        return GameMessage(
            type=GameMessageType.DAMAGE_DEALT,
            sender_id=sender_id,
            session_id=session_id,
            turn_number=turn_number,
            data={
                'attacker_id': attacker_id,
                'target_id': target_id,
                'damage_amount': damage_amount,
                'damage_type': damage_type,  # 'physical', 'magical', 'true'
                'is_critical': False,
                'status_effects_applied': []
            },
            timestamp=time.time()
        )
    
    @staticmethod
    def create_combat_state_message(sender_id: str, session_id: str,
                                  combat_state: CombatState,
                                  turn_number: int) -> GameMessage:
        """전투 상태 동기화 메시지"""
        return GameMessage(
            type=GameMessageType.COMBAT_STATE,
            sender_id=sender_id,
            session_id=session_id,
            turn_number=turn_number,
            data={
                'combat_state': asdict(combat_state)
            },
            timestamp=time.time()
        )
    
    @staticmethod
    def create_turn_order_message(sender_id: str, session_id: str,
                                turn_order: List[str], current_turn: str,
                                turn_number: int) -> GameMessage:
        """턴 순서 메시지 생성"""
        return GameMessage(
            type=GameMessageType.TURN_ORDER,
            sender_id=sender_id,
            session_id=session_id,
            turn_number=turn_number,
            data={
                'turn_order': turn_order,
                'current_turn': current_turn,
                'turn_index': turn_order.index(current_turn) if current_turn in turn_order else 0
            },
            timestamp=time.time()
        )

class GameStateConverter:
    """게임 객체를 메시지 데이터로 변환하는 유틸리티"""
    
    @staticmethod
    def character_to_state(character: Character) -> CharacterState:
        """Character 객체를 CharacterState로 변환"""
        return CharacterState(
            name=character.name,
            level=character.level,
            current_hp=character.current_hp,
            max_hp=character.max_hp,
            current_mp=character.current_mp,
            max_mp=character.max_mp,
            brave_points=getattr(character, 'brave_points', 0),
            atb_gauge=getattr(character, 'atb_gauge', 0),
            is_alive=character.is_alive,
            is_broken=getattr(character, 'is_broken', False),
            status_effects=[
                {
                    'type': effect.type.value if hasattr(effect, 'type') else str(effect),
                    'duration': getattr(effect, 'duration', 0),
                    'power': getattr(effect, 'power', 0)
                } for effect in getattr(character, 'status_effects', [])
            ],
            equipped_items={
                'weapon': character.equipped_weapon.name if character.equipped_weapon else None,
                'armor': character.equipped_armor.name if character.equipped_armor else None,
                'accessory': character.equipped_accessory.name if character.equipped_accessory else None
            }
        )
    
    @staticmethod
    def state_to_character_data(state: CharacterState) -> Dict[str, Any]:
        """CharacterState를 캐릭터 데이터 딕셔너리로 변환"""
        return {
            'name': state.name,
            'level': state.level,
            'current_hp': state.current_hp,
            'max_hp': state.max_hp,
            'current_mp': state.current_mp,
            'max_mp': state.max_mp,
            'brave_points': state.brave_points,
            'atb_gauge': state.atb_gauge,
            'is_alive': state.is_alive,
            'is_broken': state.is_broken,
            'status_effects': state.status_effects,
            'equipped_items': state.equipped_items
        }

class MessageValidator:
    """메시지 유효성 검증"""
    
    @staticmethod
    def validate_combat_action(message: GameMessage) -> bool:
        """전투 액션 메시지 유효성 검증"""
        try:
            data = message.data
            required_fields = ['action_type', 'target_id']
            
            for field in required_fields:
                if field not in data:
                    log_debug("메시지검증", f"필수 필드 누락: {field}")
                    return False
            
            valid_actions = ['attack', 'skill', 'item', 'defend', 'escape']
            if data['action_type'] not in valid_actions:
                log_debug("메시지검증", f"잘못된 액션 타입: {data['action_type']}")
                return False
            
            return True
            
        except Exception as e:
            log_debug("메시지검증", f"검증 오류: {e}")
            return False
    
    @staticmethod
    def validate_player_move(message: GameMessage) -> bool:
        """플레이어 이동 메시지 유효성 검증"""
        try:
            data = message.data
            required_fields = ['old_position', 'new_position']
            
            for field in required_fields:
                if field not in data:
                    return False
            
            # 위치 데이터 검증
            for pos_key in required_fields:
                pos = data[pos_key]
                if not all(key in pos for key in ['x', 'y', 'dungeon_level']):
                    return False
                
                if not all(isinstance(pos[key], int) for key in ['x', 'y', 'dungeon_level']):
                    return False
            
            return True
            
        except Exception as e:
            log_debug("메시지검증", f"이동 검증 오류: {e}")
            return False

class MessageQueue:
    """메시지 큐 관리"""
    
    def __init__(self, max_size: int = 1000):
        self.messages: List[GameMessage] = []
        self.max_size = max_size
        self.processed_count = 0
    
    def add_message(self, message: GameMessage):
        """메시지 추가"""
        self.messages.append(message)
        
        # 큐 크기 제한
        if len(self.messages) > self.max_size:
            self.messages = self.messages[-self.max_size:]
    
    def get_messages_by_type(self, msg_type: GameMessageType) -> List[GameMessage]:
        """타입별 메시지 조회"""
        return [msg for msg in self.messages if msg.type == msg_type]
    
    def get_messages_since(self, timestamp: float) -> List[GameMessage]:
        """특정 시간 이후 메시지 조회"""
        return [msg for msg in self.messages if msg.timestamp > timestamp]
    
    def get_unprocessed_messages(self) -> List[GameMessage]:
        """처리되지 않은 메시지 조회"""
        return self.messages[self.processed_count:]
    
    def mark_processed(self, count: int):
        """처리 완료 마킹"""
        self.processed_count = min(self.processed_count + count, len(self.messages))
    
    def clear_old_messages(self, keep_last: int = 100):
        """오래된 메시지 정리"""
        if len(self.messages) > keep_last:
            self.messages = self.messages[-keep_last:]
            self.processed_count = max(0, self.processed_count - (len(self.messages) - keep_last))

# 전역 메시지 큐
_message_queue = MessageQueue()

def get_message_queue() -> MessageQueue:
    """전역 메시지 큐 반환"""
    return _message_queue

def reset_message_queue():
    """메시지 큐 리셋 (테스트용)"""
    global _message_queue
    _message_queue = MessageQueue()
