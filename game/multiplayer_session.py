"""
🎮 Dawn of Stellar - 멀티플레이어 게임 세션 매니저
Phase 1: 기존 게임 시스템과 멀티플레이어 네트워킹 연결

이 모듈은 기존의 단일 플레이어 게임 로직을 멀티플레이어 환경에서
동작하도록 조정하는 핵심 브리지 역할을 합니다.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time
import uuid
import json

from .multiplayer_network import P2PNetworkManager, get_network_manager, PlayerRole, MessageType
from .multiplayer_protocol import (
    GameMessage, GameMessageType, GameStateProtocol, GameStateConverter,
    MessageValidator, MessageQueue, get_message_queue,
    PlayerPosition, CharacterState, CombatState
)
from .character import Character
from .error_logger import log_debug, log_error, log_system

class SessionState(Enum):
    """세션 상태"""
    LOBBY = "lobby"           # 대기실 (플레이어 모집 중)
    PLAYING = "playing"       # 게임 진행 중
    PAUSED = "paused"         # 일시 정지
    ENDED = "ended"           # 게임 종료

class TurnMode(Enum):
    """턴 진행 모드"""
    REALTIME = "realtime"     # 실시간 (ATB 시스템)
    TURN_BASED = "turn_based" # 턴제 (For The King 스타일)

class MultiplayerGameSession:
    """멀티플레이어 게임 세션 매니저"""
    
    def __init__(self, session_name: str = "Dawn of Stellar Session"):
        # 기본 세션 정보
        self.session_id = f"game_{int(time.time())}"
        self.session_name = session_name
        self.state = SessionState.LOBBY
        self.turn_mode = TurnMode.REALTIME
        
        # 네트워킹
        self.network = get_network_manager()
        self.message_queue = get_message_queue()
        
        # 게임 상태
        self.current_turn = 0
        self.turn_owner_id: Optional[str] = None
        self.player_characters: Dict[str, Character] = {}  # player_id -> Character
        self.player_positions: Dict[str, PlayerPosition] = {}
        
        # 동기화 상태
        self.last_sync_time = time.time()
        self.sync_interval = 1.0  # 초
        self.pending_actions: List[GameMessage] = []
        
        # 콜백 함수들
        self.on_player_join: Optional[Callable] = None
        self.on_player_leave: Optional[Callable] = None
        self.on_game_state_update: Optional[Callable] = None
        self.on_combat_action: Optional[Callable] = None
        
        # 턴 관리
        self.turn_order: List[str] = []
        self.turn_timeout = 30.0  # 초
        self.turn_start_time = 0.0
        
        log_system("멀티플레이어세션", f"게임 세션 생성", {
            "세션ID": self.session_id,
            "세션명": self.session_name,
            "턴모드": self.turn_mode.value
        })
        
        # 네트워크 메시지 핸들러 등록
        self._setup_message_handlers()
    
    def _setup_message_handlers(self):
        """네트워크 메시지 핸들러 설정"""
        # 기존 네트워크 매니저에 게임 메시지 핸들러 추가
        if hasattr(self.network, 'message_handlers'):
            self.network.message_handlers[MessageType.GAME_STATE] = self._handle_game_state_message
            self.network.message_handlers[MessageType.PLAYER_ACTION] = self._handle_player_action_message
            self.network.message_handlers[MessageType.COMBAT_ACTION] = self._handle_combat_action_message
    
    async def start_session_as_host(self, port: int = 7176) -> bool:
        """호스트로 세션 시작"""
        try:
            # 네트워크 호스트 시작
            success = await self.network.start_as_host(port)
            if not success:
                return False
            
            self.state = SessionState.LOBBY
            
            # 호스트를 첫 번째 플레이어로 등록
            host_id = self.network.my_id
            self.turn_order.append(host_id)
            
            # 동기화 태스크 시작
            asyncio.create_task(self._sync_loop())
            
            log_system("멀티플레이어세션", f"✅ 호스트 세션 시작", {
                "포트": port,
                "세션ID": self.session_id
            })
            
            return True
            
        except Exception as e:
            log_error("멀티플레이어세션", f"호스트 시작 실패: {e}")
            return False
    
    async def join_session_as_peer(self, host_address: str, port: int = 7176) -> bool:
        """피어로 세션 참가"""
        try:
            # 네트워크 피어 연결
            success = await self.network.connect_as_peer(host_address, port)
            if not success:
                return False
            
            self.state = SessionState.LOBBY
            
            # 세션 정보 요청
            await self._request_session_info()
            
            log_system("멀티플레이어세션", f"✅ 피어 세션 참가", {
                "호스트": f"{host_address}:{port}",
                "세션ID": self.session_id
            })
            
            return True
            
        except Exception as e:
            log_error("멀티플레이어세션", f"피어 참가 실패: {e}")
            return False
    
    async def add_player_character(self, player_id: str, character: Character, position: PlayerPosition):
        """플레이어 캐릭터 추가"""
        self.player_characters[player_id] = character
        self.player_positions[player_id] = position
        
        # 턴 순서에 추가 (호스트만)
        if self.network.is_host() and player_id not in self.turn_order:
            self.turn_order.append(player_id)
        
        log_system("멀티플레이어세션", f"플레이어 캐릭터 추가", {
            "플레이어ID": player_id,
            "캐릭터명": character.name,
            "위치": f"({position.x}, {position.y})"
        })
        
        # 다른 플레이어들에게 알림
        if self.network.is_host():
            await self._broadcast_party_state()
    
    async def handle_player_move(self, player_id: str, old_pos: PlayerPosition, new_pos: PlayerPosition):
        """플레이어 이동 처리"""
        # 위치 업데이트
        self.player_positions[player_id] = new_pos
        
        # 이동 메시지 생성 및 전송
        move_msg = GameStateProtocol.create_player_move_message(
            sender_id=self.network.my_id,
            session_id=self.session_id,
            old_pos=old_pos,
            new_pos=new_pos,
            turn_number=self.current_turn
        )
        
        await self._send_game_message(move_msg)
        
        log_debug("멀티플레이어세션", f"플레이어 이동", {
            "플레이어ID": player_id,
            "이전위치": f"({old_pos.x}, {old_pos.y})",
            "새위치": f"({new_pos.x}, {new_pos.y})"
        })
    
    async def handle_combat_action(self, player_id: str, action_type: str, 
                                 target_id: str, skill_name: Optional[str] = None):
        """전투 액션 처리"""
        # 전투 액션 메시지 생성
        action_msg = GameStateProtocol.create_combat_action_message(
            sender_id=self.network.my_id,
            session_id=self.session_id,
            action_type=action_type,
            target_id=target_id,
            skill_name=skill_name,
            turn_number=self.current_turn
        )
        
        # 유효성 검증
        if not MessageValidator.validate_combat_action(action_msg):
            log_error("멀티플레이어세션", f"잘못된 전투 액션: {action_type}")
            return False
        
        # 메시지 전송
        await self._send_game_message(action_msg)
        
        log_debug("멀티플레이어세션", f"전투 액션", {
            "플레이어ID": player_id,
            "액션": action_type,
            "타겟": target_id,
            "스킬": skill_name
        })
        
        return True
    
    async def start_combat(self, party: List[Character], enemies: List[Character]):
        """전투 시작"""
        if not self.network.is_host():
            return  # 호스트만 전투 시작 가능
        
        self.state = SessionState.PLAYING
        
        # 전투 상태 생성
        combat_state = CombatState(
            is_in_combat=True,
            combat_id=str(uuid.uuid4()),
            turn_number=self.current_turn,
            current_turn_character=None,
            party_states=[GameStateConverter.character_to_state(char) for char in party],
            enemy_states=[GameStateConverter.character_to_state(enemy) for enemy in enemies],
            turn_order=[]
        )
        
        # 전투 시작 메시지 전송
        combat_msg = GameMessage(
            type=GameMessageType.COMBAT_START,
            sender_id=self.network.my_id,
            session_id=self.session_id,
            turn_number=self.current_turn,
            data={'combat_state': combat_state.__dict__},
            timestamp=time.time()
        )
        
        await self._send_game_message(combat_msg)
        
        log_system("멀티플레이어세션", f"전투 시작", {
            "전투ID": combat_state.combat_id,
            "아군수": len(party),
            "적수": len(enemies)
        })
    
    async def update_atb_gauge(self, character_id: str, atb_value: int):
        """ATB 게이지 업데이트"""
        atb_msg = GameStateProtocol.create_atb_update_message(
            sender_id=self.network.my_id,
            session_id=self.session_id,
            character_id=character_id,
            atb_value=atb_value,
            turn_number=self.current_turn
        )
        
        await self._send_game_message(atb_msg)
    
    async def deal_damage(self, attacker_id: str, target_id: str, 
                         damage_amount: int, damage_type: str):
        """데미지 처리"""
        damage_msg = GameStateProtocol.create_damage_message(
            sender_id=self.network.my_id,
            session_id=self.session_id,
            attacker_id=attacker_id,
            target_id=target_id,
            damage_amount=damage_amount,
            damage_type=damage_type,
            turn_number=self.current_turn
        )
        
        await self._send_game_message(damage_msg)
    
    async def next_turn(self):
        """다음 턴으로 진행 (호스트만)"""
        if not self.network.is_host():
            return
        
        self.current_turn += 1
        
        # 턴 순서 결정
        if self.turn_order:
            current_index = (self.current_turn - 1) % len(self.turn_order)
            self.turn_owner_id = self.turn_order[current_index]
            self.turn_start_time = time.time()
        
        # 턴 시작 메시지 전송
        turn_msg = GameStateProtocol.create_turn_order_message(
            sender_id=self.network.my_id,
            session_id=self.session_id,
            turn_order=self.turn_order,
            current_turn=self.turn_owner_id or "",
            turn_number=self.current_turn
        )
        
        await self._send_game_message(turn_msg)
        
        log_debug("멀티플레이어세션", f"턴 진행", {
            "턴번호": self.current_turn,
            "턴소유자": self.turn_owner_id
        })
    
    def is_my_turn(self) -> bool:
        """내 턴인지 확인"""
        return self.turn_owner_id == self.network.my_id
    
    def get_current_player_count(self) -> int:
        """현재 플레이어 수"""
        return len(self.player_characters)
    
    def get_session_info(self) -> Dict[str, Any]:
        """세션 정보 반환"""
        return {
            'session_id': self.session_id,
            'session_name': self.session_name,
            'state': self.state.value,
            'turn_mode': self.turn_mode.value,
            'current_turn': self.current_turn,
            'turn_owner': self.turn_owner_id,
            'player_count': len(self.player_characters),
            'turn_order': self.turn_order,
            'is_host': self.network.is_host()
        }
    
    # ========== 내부 메서드들 ==========
    
    async def _send_game_message(self, message: GameMessage):
        """게임 메시지 전송"""
        # 메시지 큐에 추가
        self.message_queue.add_message(message)
        
        # 네트워크로 전송
        await self.network.send_message(
            MessageType.GAME_STATE,  # 네트워크 레벨 메시지 타입
            message.to_dict()
        )
    
    async def _broadcast_party_state(self):
        """파티 상태 브로드캐스트 (호스트만)"""
        if not self.network.is_host():
            return
        
        party_data = {
            'players': {
                pid: {
                    'character': GameStateConverter.character_to_state(char).__dict__,
                    'position': self.player_positions[pid].__dict__
                } for pid, char in self.player_characters.items()
            },
            'turn_order': self.turn_order
        }
        
        party_msg = GameMessage(
            type=GameMessageType.PARTY_STATE,
            sender_id=self.network.my_id,
            session_id=self.session_id,
            turn_number=self.current_turn,
            data=party_data,
            timestamp=time.time()
        )
        
        await self._send_game_message(party_msg)
    
    async def _request_session_info(self):
        """세션 정보 요청 (피어용)"""
        request_msg = GameMessage(
            type=GameMessageType.GAME_STATE_SYNC,
            sender_id=self.network.my_id,
            session_id=self.session_id,
            turn_number=0,
            data={'request_type': 'session_info'},
            timestamp=time.time()
        )
        
        await self._send_game_message(request_msg)
    
    async def _sync_loop(self):
        """동기화 루프 (호스트용)"""
        while self.network.is_running:
            try:
                await asyncio.sleep(self.sync_interval)
                
                if self.network.is_host():
                    # 주기적으로 게임 상태 동기화
                    await self._broadcast_party_state()
                
                # 턴 타임아웃 체크
                if (self.turn_owner_id and 
                    time.time() - self.turn_start_time > self.turn_timeout):
                    log_debug("멀티플레이어세션", f"턴 타임아웃: {self.turn_owner_id}")
                    await self.next_turn()
                
            except Exception as e:
                log_error("멀티플레이어세션", f"동기화 루프 오류: {e}")
    
    # ========== 네트워크 메시지 핸들러들 ==========
    
    async def _handle_game_state_message(self, message, sender_id=None):
        """게임 상태 메시지 처리"""
        try:
            # 네트워크 메시지에서 게임 메시지 추출
            game_msg_data = message.data
            game_msg = GameMessage.from_json(json.dumps(game_msg_data))
            
            # 메시지 타입별 처리
            if game_msg.type == GameMessageType.PLAYER_MOVE:
                await self._handle_player_move(game_msg)
            elif game_msg.type == GameMessageType.COMBAT_ACTION:
                await self._handle_combat_action_received(game_msg)
            elif game_msg.type == GameMessageType.PARTY_STATE:
                await self._handle_party_state_update(game_msg)
            elif game_msg.type == GameMessageType.TURN_ORDER:
                await self._handle_turn_order_update(game_msg)
            
        except Exception as e:
            log_error("멀티플레이어세션", f"게임 상태 메시지 처리 오류: {e}")
    
    async def _handle_player_move(self, message: GameMessage):
        """플레이어 이동 메시지 처리"""
        if not MessageValidator.validate_player_move(message):
            return
        
        player_id = message.sender_id
        new_pos_data = message.data['new_position']
        new_pos = PlayerPosition(**new_pos_data)
        
        # 위치 업데이트
        self.player_positions[player_id] = new_pos
        
        log_debug("멀티플레이어세션", f"플레이어 이동 수신", {
            "플레이어": player_id,
            "새위치": f"({new_pos.x}, {new_pos.y})"
        })
        
        # UI 업데이트 콜백
        if self.on_game_state_update:
            self.on_game_state_update('player_move', {
                'player_id': player_id,
                'position': new_pos
            })
    
    async def _handle_combat_action_received(self, message: GameMessage):
        """전투 액션 메시지 처리"""
        if not MessageValidator.validate_combat_action(message):
            return
        
        action_data = message.data
        
        log_debug("멀티플레이어세션", f"전투 액션 수신", {
            "플레이어": message.sender_id,
            "액션": action_data['action_type'],
            "타겟": action_data['target_id']
        })
        
        # 전투 액션 콜백
        if self.on_combat_action:
            self.on_combat_action(message.sender_id, action_data)
    
    async def _handle_party_state_update(self, message: GameMessage):
        """파티 상태 업데이트 처리"""
        party_data = message.data
        
        # 플레이어 데이터 업데이트
        if 'players' in party_data:
            for player_id, player_info in party_data['players'].items():
                if player_id != self.network.my_id:  # 자신은 제외
                    # 캐릭터 상태 업데이트 (실제 구현에서는 Character 객체 업데이트)
                    log_debug("멀티플레이어세션", f"플레이어 상태 업데이트", {
                        "플레이어": player_id,
                        "캐릭터": player_info['character']['name']
                    })
        
        # 턴 순서 업데이트
        if 'turn_order' in party_data:
            self.turn_order = party_data['turn_order']
    
    async def _handle_turn_order_update(self, message: GameMessage):
        """턴 순서 업데이트 처리"""
        turn_data = message.data
        
        self.turn_order = turn_data['turn_order']
        self.turn_owner_id = turn_data['current_turn']
        self.current_turn = message.turn_number
        self.turn_start_time = time.time()
        
        log_debug("멀티플레이어세션", f"턴 업데이트", {
            "턴번호": self.current_turn,
            "턴소유자": self.turn_owner_id,
            "내턴": self.is_my_turn()
        })
    
    async def shutdown(self):
        """세션 종료"""
        log_system("멀티플레이어세션", "게임 세션 종료 시작")
        
        self.state = SessionState.ENDED
        
        # 네트워크 매니저 종료
        await self.network.shutdown()
        
        # 데이터 정리
        self.player_characters.clear()
        self.player_positions.clear()
        self.turn_order.clear()
        
        log_system("멀티플레이어세션", "✅ 게임 세션 종료 완료")

# 전역 게임 세션 인스턴스
_game_session = None

def get_multiplayer_session() -> MultiplayerGameSession:
    """전역 멀티플레이어 세션 인스턴스 반환"""
    global _game_session
    if _game_session is None:
        _game_session = MultiplayerGameSession()
    return _game_session

def reset_multiplayer_session():
    """멀티플레이어 세션 리셋 (테스트용)"""
    global _game_session
    _game_session = None
