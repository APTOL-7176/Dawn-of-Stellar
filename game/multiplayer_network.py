"""
🌐 Dawn of Stellar - P2P 네트워크 매니저
Phase 1: P2P 네트워크 인프라 구현

이 모듈은 멀티플레이어 게임의 P2P 네트워크 연결을 관리합니다.
호스트/피어 역할 관리, 메시지 라우팅, 연결 상태 추적을 담당합니다.
"""

import asyncio
import websockets
import json
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import time
import logging

from .error_logger import log_debug, log_error, log_system

class PlayerRole(Enum):
    """플레이어 역할 정의"""
    HOST = "host"           # 호스트 (게임 상태 권한)
    PEER = "peer"           # 일반 피어 (참가자)
    SPECTATOR = "spectator" # 관전자

class MessageType(Enum):
    """네트워크 메시지 타입"""
    # 연결 관련
    HANDSHAKE = "handshake"
    PEER_JOIN = "peer_join"
    PEER_LEAVE = "peer_leave"
    
    # 게임 상태
    GAME_STATE = "game_state"
    PLAYER_ACTION = "player_action"
    COMBAT_ACTION = "combat_action"
    
    # 채팅
    CHAT_MESSAGE = "chat_message"
    
    # 시스템
    PING = "ping"
    PONG = "pong"
    ERROR = "error"

@dataclass
class NetworkMessage:
    """네트워크 메시지 구조"""
    type: MessageType
    sender_id: str
    session_id: str
    data: Dict[str, Any]
    timestamp: float
    
    def to_json(self) -> str:
        """JSON 직렬화"""
        return json.dumps({
            'type': self.type.value,
            'sender_id': self.sender_id,
            'session_id': self.session_id,
            'data': self.data,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'NetworkMessage':
        """JSON 역직렬화"""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data['type']),
            sender_id=data['sender_id'],
            session_id=data['session_id'],
            data=data['data'],
            timestamp=data['timestamp']
        )

@dataclass
class PeerInfo:
    """피어 정보"""
    id: str
    role: PlayerRole
    websocket: Optional[Any]
    character_name: str
    last_ping: float
    is_connected: bool = True

class P2PNetworkManager:
    """P2P 네트워크 매니저 - 멀티플레이어 네트워크 핵심"""
    
    def __init__(self):
        self.session_id = f"session_{int(time.time())}"
        self.my_id = str(uuid.uuid4())
        self.role = PlayerRole.HOST  # 기본값은 호스트
        
        # 네트워크 상태
        self.peers: Dict[str, PeerInfo] = {}
        self.websocket = None
        self.server = None
        self.is_running = False
        
        # 메시지 핸들러
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.setup_default_handlers()
        
        # 설정
        self.host_port = 7176
        self.max_peers = 4
        self.ping_interval = 30.0  # 초
        
        log_system("P2P네트워크", f"네트워크 매니저 초기화 완료", {
            "세션ID": self.session_id,
            "내ID": self.my_id,
            "역할": self.role.value
        })
    
    def setup_default_handlers(self):
        """기본 메시지 핸들러 설정"""
        self.message_handlers[MessageType.HANDSHAKE] = self._handle_handshake
        self.message_handlers[MessageType.PEER_JOIN] = self._handle_peer_join
        self.message_handlers[MessageType.PEER_LEAVE] = self._handle_peer_leave
        self.message_handlers[MessageType.PING] = self._handle_ping
        self.message_handlers[MessageType.PONG] = self._handle_pong
        self.message_handlers[MessageType.CHAT_MESSAGE] = self._handle_chat
    
    async def start_as_host(self, port: int = None) -> bool:
        """호스트로 서버 시작"""
        try:
            if port:
                self.host_port = port
            
            self.role = PlayerRole.HOST
            log_system("P2P네트워크", f"호스트 서버 시작 시도", {
                "포트": self.host_port,
                "세션ID": self.session_id
            })
            
            # WebSocket 서버 시작
            self.server = await websockets.serve(
                self._handle_peer_connection,
                "localhost",
                self.host_port
            )
            
            self.is_running = True
            
            # 자기 자신을 호스트로 등록
            self.peers[self.my_id] = PeerInfo(
                id=self.my_id,
                role=PlayerRole.HOST,
                websocket=None,
                character_name="Host",
                last_ping=time.time()
            )
            
            log_system("P2P네트워크", f"✅ 호스트 서버 시작 성공", {
                "포트": self.host_port,
                "세션ID": self.session_id,
                "최대접속": self.max_peers
            })
            
            # Ping 태스크 시작
            asyncio.create_task(self._ping_loop())
            
            return True
            
        except Exception as e:
            log_error("P2P네트워크", f"호스트 시작 실패: {e}")
            return False
    
    async def connect_as_peer(self, host_address: str, port: int = None) -> bool:
        """피어로 호스트에 연결"""
        try:
            if port is None:
                port = self.host_port
            
            self.role = PlayerRole.PEER
            uri = f"ws://{host_address}:{port}"
            
            log_system("P2P네트워크", f"피어 연결 시도", {
                "호스트": uri,
                "내ID": self.my_id
            })
            
            # WebSocket 연결
            self.websocket = await websockets.connect(uri)
            self.is_running = True
            
            # 핸드셰이크 메시지 전송
            handshake_msg = NetworkMessage(
                type=MessageType.HANDSHAKE,
                sender_id=self.my_id,
                session_id=self.session_id,
                data={
                    'role': self.role.value,
                    'character_name': 'Player'  # 나중에 실제 캐릭터명으로 교체
                },
                timestamp=time.time()
            )
            
            await self.websocket.send(handshake_msg.to_json())
            
            # 메시지 수신 태스크 시작
            asyncio.create_task(self._message_receiver())
            
            log_system("P2P네트워크", f"✅ 피어 연결 성공", {
                "호스트": uri,
                "내ID": self.my_id
            })
            
            return True
            
        except Exception as e:
            log_error("P2P네트워크", f"피어 연결 실패: {e}")
            return False
    
    async def _handle_peer_connection(self, websocket):
        """새 피어 연결 처리 (호스트용)"""
        peer_id = None
        try:
            # 핸드셰이크 대기
            handshake_data = await websocket.recv()
            handshake_msg = NetworkMessage.from_json(handshake_data)
            
            if handshake_msg.type != MessageType.HANDSHAKE:
                await websocket.close(code=1003, reason="Invalid handshake")
                return
            
            peer_id = handshake_msg.sender_id
            
            # 최대 접속자 수 확인
            active_peers = len([p for p in self.peers.values() if p.is_connected and p.role != PlayerRole.HOST])
            if active_peers >= self.max_peers - 1:  # 호스트 제외
                await websocket.close(code=1013, reason="Server full")
                return
            
            # 피어 정보 등록
            peer_info = PeerInfo(
                id=peer_id,
                role=PlayerRole(handshake_msg.data.get('role', 'peer')),
                websocket=websocket,
                character_name=handshake_msg.data.get('character_name', 'Unknown'),
                last_ping=time.time()
            )
            
            self.peers[peer_id] = peer_info
            
            log_system("P2P네트워크", f"✅ 새 피어 접속", {
                "피어ID": peer_id,
                "캐릭터명": peer_info.character_name,
                "총접속자": len(self.peers)
            })
            
            # 다른 피어들에게 새 참가자 알림
            await self._broadcast_message(
                MessageType.PEER_JOIN,
                {
                    'peer_id': peer_id,
                    'character_name': peer_info.character_name,
                    'peer_count': len(self.peers)
                },
                exclude=[peer_id]
            )
            
            # 새 피어에게 현재 세션 정보 전송
            session_info_msg = NetworkMessage(
                type=MessageType.GAME_STATE,
                sender_id=self.my_id,
                session_id=self.session_id,
                data={
                    'type': 'session_info',
                    'peers': {
                        pid: {
                            'character_name': p.character_name,
                            'role': p.role.value
                        } for pid, p in self.peers.items()
                    }
                },
                timestamp=time.time()
            )
            await websocket.send(session_info_msg.to_json())
            
            # 메시지 수신 루프
            async for message in websocket:
                await self._process_message(message, peer_id)
                
        except websockets.exceptions.ConnectionClosed:
            log_system("P2P네트워크", f"피어 연결 종료", {"피어ID": peer_id})
        except Exception as e:
            log_error("P2P네트워크", f"피어 연결 처리 오류: {e}", {"피어ID": peer_id})
        finally:
            # 연결 정리
            if peer_id and peer_id in self.peers:
                self.peers[peer_id].is_connected = False
                await self._broadcast_message(
                    MessageType.PEER_LEAVE,
                    {
                        'peer_id': peer_id,
                        'peer_count': len([p for p in self.peers.values() if p.is_connected])
                    }
                )
    
    async def _message_receiver(self):
        """메시지 수신 태스크 (피어용)"""
        try:
            async for message in self.websocket:
                await self._process_message(message)
        except websockets.exceptions.ConnectionClosed:
            log_system("P2P네트워크", "호스트 연결 종료됨")
        except Exception as e:
            log_error("P2P네트워크", f"메시지 수신 오류: {e}")
    
    async def _process_message(self, message_data: str, sender_websocket_id: str = None):
        """수신된 메시지 처리"""
        try:
            msg = NetworkMessage.from_json(message_data)
            
            # 메시지 핸들러 호출
            handler = self.message_handlers.get(msg.type)
            if handler:
                await handler(msg, sender_websocket_id)
            else:
                log_debug("P2P네트워크", f"처리되지 않은 메시지 타입: {msg.type.value}")
                
        except Exception as e:
            log_error("P2P네트워크", f"메시지 처리 오류: {e}")
    
    async def send_message(self, msg_type: MessageType, data: Dict[str, Any], target_id: str = None):
        """메시지 전송"""
        message = NetworkMessage(
            type=msg_type,
            sender_id=self.my_id,
            session_id=self.session_id,
            data=data,
            timestamp=time.time()
        )
        
        if target_id:
            # 특정 피어에게 전송
            peer = self.peers.get(target_id)
            if peer and peer.websocket and peer.is_connected:
                await peer.websocket.send(message.to_json())
        else:
            # 브로드캐스트
            await self._broadcast_message(msg_type, data)
    
    async def _broadcast_message(self, msg_type: MessageType, data: Dict[str, Any], exclude: List[str] = None):
        """모든 피어에게 메시지 브로드캐스트"""
        if exclude is None:
            exclude = []
        
        message = NetworkMessage(
            type=msg_type,
            sender_id=self.my_id,
            session_id=self.session_id,
            data=data,
            timestamp=time.time()
        )
        
        # 연결된 모든 피어에게 전송
        for peer_id, peer in self.peers.items():
            if (peer_id not in exclude and 
                peer.websocket and 
                peer.is_connected and 
                peer_id != self.my_id):
                try:
                    await peer.websocket.send(message.to_json())
                except Exception as e:
                    log_error("P2P네트워크", f"브로드캐스트 실패: {peer_id}", {"오류": str(e)})
                    peer.is_connected = False
    
    async def _ping_loop(self):
        """주기적 핑 전송"""
        while self.is_running:
            try:
                await asyncio.sleep(self.ping_interval)
                
                if self.role == PlayerRole.HOST:
                    # 호스트: 모든 피어에게 핑 전송
                    await self._broadcast_message(MessageType.PING, {'timestamp': time.time()})
                else:
                    # 피어: 호스트에게 핑 전송
                    if self.websocket:
                        await self.send_message(MessageType.PING, {'timestamp': time.time()})
                        
            except Exception as e:
                log_error("P2P네트워크", f"핑 루프 오류: {e}")
    
    # ========== 메시지 핸들러들 ==========
    
    async def _handle_handshake(self, msg: NetworkMessage, sender_id: str = None):
        """핸드셰이크 처리"""
        log_debug("P2P네트워크", f"핸드셰이크 수신: {msg.sender_id}")
    
    async def _handle_peer_join(self, msg: NetworkMessage, sender_id: str = None):
        """피어 참가 알림 처리"""
        peer_id = msg.data.get('peer_id')
        character_name = msg.data.get('character_name')
        peer_count = msg.data.get('peer_count')
        
        log_system("P2P네트워크", f"✅ 새 참가자", {
            "피어ID": peer_id,
            "캐릭터명": character_name,
            "총인원": peer_count
        })
        
        # UI에 알림 (나중에 구현)
        # self._show_peer_join_notification(character_name)
    
    async def _handle_peer_leave(self, msg: NetworkMessage, sender_id: str = None):
        """피어 퇴장 알림 처리"""
        peer_id = msg.data.get('peer_id')
        peer_count = msg.data.get('peer_count')
        
        if peer_id in self.peers:
            character_name = self.peers[peer_id].character_name
            del self.peers[peer_id]
            
            log_system("P2P네트워크", f"❌ 참가자 퇴장", {
                "피어ID": peer_id,
                "캐릭터명": character_name,
                "남은인원": peer_count
            })
    
    async def _handle_ping(self, msg: NetworkMessage, sender_id: str = None):
        """핑 처리"""
        # 퐁으로 응답
        await self.send_message(
            MessageType.PONG, 
            {'timestamp': msg.data.get('timestamp')},
            msg.sender_id
        )
    
    async def _handle_pong(self, msg: NetworkMessage, sender_id: str = None):
        """퐁 처리"""
        if msg.sender_id in self.peers:
            self.peers[msg.sender_id].last_ping = time.time()
    
    async def _handle_chat(self, msg: NetworkMessage, sender_id: str = None):
        """채팅 메시지 처리"""
        sender_name = "Unknown"
        if msg.sender_id in self.peers:
            sender_name = self.peers[msg.sender_id].character_name
        
        chat_text = msg.data.get('message', '')
        
        log_debug("P2P네트워크", f"💬 채팅: {sender_name}: {chat_text}")
        
        # UI에 채팅 표시 (나중에 구현)
        # self._show_chat_message(sender_name, chat_text)
    
    # ========== 유틸리티 메서드들 ==========
    
    def get_connected_peers(self) -> List[PeerInfo]:
        """연결된 피어 목록 반환"""
        return [peer for peer in self.peers.values() if peer.is_connected]
    
    def get_peer_count(self) -> int:
        """연결된 피어 수 반환"""
        return len(self.get_connected_peers())
    
    def is_host(self) -> bool:
        """호스트 여부 확인"""
        return self.role == PlayerRole.HOST
    
    def get_session_info(self) -> Dict[str, Any]:
        """세션 정보 반환"""
        return {
            'session_id': self.session_id,
            'my_id': self.my_id,
            'role': self.role.value,
            'peer_count': self.get_peer_count(),
            'max_peers': self.max_peers,
            'is_running': self.is_running
        }
    
    async def shutdown(self):
        """네트워크 매니저 종료"""
        log_system("P2P네트워크", "네트워크 매니저 종료 시작")
        
        self.is_running = False
        
        # 모든 연결 정리
        if self.websocket:
            await self.websocket.close()
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # 피어 정보 정리
        for peer in self.peers.values():
            if peer.websocket:
                await peer.websocket.close()
        
        self.peers.clear()
        
        log_system("P2P네트워크", "✅ 네트워크 매니저 종료 완료")

# 전역 네트워크 매니저 인스턴스
_network_manager = None

def get_network_manager() -> P2PNetworkManager:
    """전역 네트워크 매니저 인스턴스 반환"""
    global _network_manager
    if _network_manager is None:
        _network_manager = P2PNetworkManager()
    return _network_manager

def reset_network_manager():
    """네트워크 매니저 리셋 (테스트용)"""
    global _network_manager
    _network_manager = None
