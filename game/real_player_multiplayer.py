"""
🎮 Dawn of Stellar - 진짜 사람끼리 하는 네트워크 멀티플레이어!
AI 테스트용 + 실제 친구들과 함께 플레이

2025년 8월 10일 - 완전한 네트워크 멀티플레이어 시스템
"""

import asyncio
import websockets
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import socket
import uuid
import qrcode
import io
import base64

class NetworkGameState(Enum):
    """네트워크 게임 상태"""
    LOBBY = "lobby"
    PREPARING = "preparing"
    IN_GAME = "in_game"
    PAUSED = "paused"
    FINISHED = "finished"

class PlayerConnectionState(Enum):
    """플레이어 연결 상태"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    READY = "ready"
    IN_GAME = "in_game"
    DISCONNECTED = "disconnected"

@dataclass
class NetworkPlayer:
    """네트워크 플레이어 정보"""
    player_id: str
    name: str
    connection_state: PlayerConnectionState
    websocket: Optional[Any] = None
    character_data: Optional[Dict] = None
    last_ping: float = 0.0
    is_ai: bool = False
    ai_type: str = "none"  # "robat", "ultimate", "none"

class RealPlayerMultiplayerServer:
    """진짜 사람끼리 하는 멀티플레이어 서버"""
    
    def __init__(self, port: int = 7176):
        self.port = port
        self.server = None
        self.running = False
        
        # 게임 상태
        self.game_state = NetworkGameState.LOBBY
        self.session_id = str(uuid.uuid4())[:8]
        self.session_name = "Dawn of Stellar 게임방"
        self.max_players = 4
        
        # 플레이어 관리
        self.players: Dict[str, NetworkPlayer] = {}
        self.host_player_id: Optional[str] = None
        
        # 게임 데이터
        self.game_data: Dict[str, Any] = {}
        self.turn_order: List[str] = []
        self.current_turn_player: Optional[str] = None
        
        # AI 테스트용
        self.test_ai_enabled = True
        self.ai_players: Dict[str, Any] = {}
        
        print(f"🎮 네트워크 멀티플레이어 서버 초기화")
        print(f"   포트: {self.port}")
        print(f"   세션: {self.session_id}")
    
    async def start_server(self):
        """서버 시작"""
        try:
            self.server = await websockets.serve(
                self.handle_client_connection,
                "0.0.0.0",  # 모든 IP에서 접근 가능
                self.port
            )
            self.running = True
            
            # 서버 정보 출력
            local_ip = self._get_local_ip()
            print(f"🚀 멀티플레이어 서버 시작!")
            print(f"   🌐 로컬 IP: {local_ip}:{self.port}")
            print(f"   🏠 로컬호스트: localhost:{self.port}")
            print(f"   📱 모바일 접속: {local_ip}:{self.port}")
            
            # QR 코드 생성
            self._generate_connection_qr(local_ip)
            
            # AI 테스트 플레이어 추가
            if self.test_ai_enabled:
                await self._add_test_ai_players()
            
            print(f"✅ 서버 준비 완료! 플레이어를 기다리는 중...")
            
            # 서버 유지
            await self.server.wait_closed()
            
        except Exception as e:
            print(f"❌ 서버 시작 실패: {e}")
            self.running = False
    
    async def handle_client_connection(self, websocket, path):
        """클라이언트 연결 처리"""
        player_id = str(uuid.uuid4())[:8]
        print(f"🔗 새 플레이어 연결: {player_id}")
        
        try:
            # 플레이어 등록
            player = NetworkPlayer(
                player_id=player_id,
                name=f"플레이어{len(self.players)+1}",
                connection_state=PlayerConnectionState.CONNECTING,
                websocket=websocket,
                last_ping=time.time()
            )
            
            self.players[player_id] = player
            
            # 첫 번째 플레이어는 호스트
            if self.host_player_id is None:
                self.host_player_id = player_id
                print(f"👑 호스트 설정: {player.name}")
            
            # 환영 메시지 전송
            await self._send_to_player(player_id, {
                "type": "welcome",
                "player_id": player_id,
                "session_name": self.session_name,
                "is_host": player_id == self.host_player_id,
                "max_players": self.max_players
            })
            
            # 게임 상태 동기화
            await self._sync_game_state(player_id)
            
            # 다른 플레이어들에게 알림
            await self._broadcast_player_joined(player)
            
            # 메시지 루프
            async for message in websocket:
                await self._handle_player_message(player_id, json.loads(message))
                
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 플레이어 연결 끊김: {player_id}")
        except Exception as e:
            print(f"❌ 연결 처리 오류: {e}")
        finally:
            await self._handle_player_disconnect(player_id)
    
    async def _handle_player_message(self, player_id: str, message: Dict[str, Any]):
        """플레이어 메시지 처리"""
        msg_type = message.get("type")
        
        if msg_type == "ping":
            await self._handle_ping(player_id)
        elif msg_type == "set_name":
            await self._handle_set_name(player_id, message.get("name"))
        elif msg_type == "ready":
            await self._handle_player_ready(player_id)
        elif msg_type == "chat":
            await self._handle_chat_message(player_id, message.get("message"))
        elif msg_type == "game_action":
            await self._handle_game_action(player_id, message.get("action"))
        elif msg_type == "start_game":
            if player_id == self.host_player_id:
                await self._start_game()
        else:
            print(f"⚠️ 알 수 없는 메시지 타입: {msg_type}")
    
    async def _handle_ping(self, player_id: str):
        """핑 처리"""
        if player_id in self.players:
            self.players[player_id].last_ping = time.time()
            await self._send_to_player(player_id, {"type": "pong"})
    
    async def _handle_set_name(self, player_id: str, name: str):
        """플레이어 이름 설정"""
        if player_id in self.players:
            old_name = self.players[player_id].name
            self.players[player_id].name = name
            
            print(f"📝 이름 변경: {old_name} → {name}")
            
            # 모든 플레이어에게 알림
            await self._broadcast({
                "type": "player_name_changed",
                "player_id": player_id,
                "old_name": old_name,
                "new_name": name
            })
    
    async def _handle_player_ready(self, player_id: str):
        """플레이어 준비 완료"""
        if player_id in self.players:
            self.players[player_id].connection_state = PlayerConnectionState.READY
            
            print(f"✅ 준비 완료: {self.players[player_id].name}")
            
            await self._broadcast({
                "type": "player_ready",
                "player_id": player_id,
                "player_name": self.players[player_id].name
            })
            
            # 모든 플레이어가 준비되었는지 확인
            await self._check_all_ready()
    
    async def _handle_chat_message(self, player_id: str, message: str):
        """채팅 메시지 처리"""
        if player_id in self.players:
            player_name = self.players[player_id].name
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"💬 [{timestamp}] {player_name}: {message}")
            
            await self._broadcast({
                "type": "chat_message",
                "player_id": player_id,
                "player_name": player_name,
                "message": message,
                "timestamp": timestamp
            })
    
    async def _handle_game_action(self, player_id: str, action: Dict[str, Any]):
        """게임 액션 처리"""
        if self.game_state != NetworkGameState.IN_GAME:
            return
        
        if player_id != self.current_turn_player:
            await self._send_to_player(player_id, {
                "type": "error",
                "message": "당신의 턴이 아닙니다"
            })
            return
        
        print(f"🎮 게임 액션: {self.players[player_id].name} - {action.get('action_type')}")
        
        # 게임 액션 처리 (실제 게임 로직과 연동)
        result = await self._process_game_action(player_id, action)
        
        # 결과를 모든 플레이어에게 브로드캐스트
        await self._broadcast({
            "type": "game_action_result",
            "player_id": player_id,
            "action": action,
            "result": result
        })
        
        # 다음 턴으로
        await self._next_turn()
    
    async def _start_game(self):
        """게임 시작"""
        ready_players = [p for p in self.players.values() if p.connection_state == PlayerConnectionState.READY]
        
        if len(ready_players) < 2:
            await self._send_to_player(self.host_player_id, {
                "type": "error",
                "message": "최소 2명의 플레이어가 필요합니다"
            })
            return
        
        print(f"🚀 게임 시작! 참가자: {len(ready_players)}명")
        
        self.game_state = NetworkGameState.IN_GAME
        self.turn_order = [p.player_id for p in ready_players]
        self.current_turn_player = self.turn_order[0]
        
        # 게임 초기화
        await self._initialize_game()
        
        # 게임 시작 알림
        await self._broadcast({
            "type": "game_started",
            "turn_order": [{"player_id": pid, "name": self.players[pid].name} for pid in self.turn_order],
            "current_turn": self.current_turn_player
        })
    
    async def _initialize_game(self):
        """게임 초기화"""
        # 여기서 실제 Dawn of Stellar 게임 초기화
        self.game_data = {
            "dungeon_floor": 1,
            "party_members": {},
            "world_state": {}
        }
        
        # 각 플레이어에게 캐릭터 할당
        for i, player_id in enumerate(self.turn_order):
            character_data = {
                "name": self.players[player_id].name,
                "level": 1,
                "hp": 100,
                "mp": 50,
                "position": [i, 0]  # 시작 위치
            }
            self.players[player_id].character_data = character_data
    
    async def _process_game_action(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """게임 액션 처리"""
        action_type = action.get("action_type")
        
        if action_type == "move":
            return await self._process_move_action(player_id, action)
        elif action_type == "attack":
            return await self._process_attack_action(player_id, action)
        elif action_type == "use_item":
            return await self._process_item_action(player_id, action)
        elif action_type == "skip_turn":
            return {"success": True, "message": "턴을 넘깁니다"}
        else:
            return {"success": False, "message": "알 수 없는 액션입니다"}
    
    async def _process_move_action(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """이동 액션 처리"""
        direction = action.get("direction")
        player = self.players[player_id]
        
        # 현재 위치
        current_pos = player.character_data["position"]
        
        # 새로운 위치 계산
        new_pos = list(current_pos)
        if direction == "north":
            new_pos[1] -= 1
        elif direction == "south":
            new_pos[1] += 1
        elif direction == "east":
            new_pos[0] += 1
        elif direction == "west":
            new_pos[0] -= 1
        
        # 이동 가능 여부 확인 (간단한 예시)
        if new_pos[0] < 0 or new_pos[1] < 0:
            return {"success": False, "message": "그 방향으로는 갈 수 없습니다"}
        
        # 이동 실행
        player.character_data["position"] = new_pos
        
        return {
            "success": True,
            "message": f"{direction} 방향으로 이동했습니다",
            "new_position": new_pos
        }
    
    async def _process_attack_action(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """공격 액션 처리"""
        target_id = action.get("target_id")
        
        if target_id not in self.players:
            return {"success": False, "message": "대상을 찾을 수 없습니다"}
        
        # 간단한 공격 계산
        damage = 20  # 기본 데미지
        target_player = self.players[target_id]
        target_player.character_data["hp"] -= damage
        
        return {
            "success": True,
            "message": f"{self.players[target_id].name}에게 {damage} 데미지를 입혔습니다",
            "damage": damage,
            "target_hp": target_player.character_data["hp"]
        }
    
    async def _process_item_action(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """아이템 사용 액션 처리"""
        item_type = action.get("item_type")
        
        if item_type == "health_potion":
            player = self.players[player_id]
            heal_amount = 30
            player.character_data["hp"] = min(player.character_data["hp"] + heal_amount, 100)
            
            return {
                "success": True,
                "message": f"체력 포션을 사용하여 {heal_amount} 회복했습니다",
                "heal_amount": heal_amount,
                "current_hp": player.character_data["hp"]
            }
        
        return {"success": False, "message": "알 수 없는 아이템입니다"}
    
    async def _next_turn(self):
        """다음 턴으로"""
        if not self.turn_order:
            return
        
        current_index = self.turn_order.index(self.current_turn_player)
        next_index = (current_index + 1) % len(self.turn_order)
        self.current_turn_player = self.turn_order[next_index]
        
        await self._broadcast({
            "type": "turn_change",
            "current_turn": self.current_turn_player,
            "player_name": self.players[self.current_turn_player].name
        })
    
    async def _add_test_ai_players(self):
        """AI 테스트 플레이어 추가"""
        ai_names = ["로바트전사", "로바트마법사", "로바트도적"]
        
        for i, ai_name in enumerate(ai_names):
            ai_id = f"ai_{i+1}"
            
            ai_player = NetworkPlayer(
                player_id=ai_id,
                name=ai_name,
                connection_state=PlayerConnectionState.READY,
                is_ai=True,
                ai_type="robat"
            )
            
            self.players[ai_id] = ai_player
            self.ai_players[ai_id] = ai_player
            
            print(f"🤖 AI 플레이어 추가: {ai_name}")
        
        # AI 자동 행동 스레드 시작
        asyncio.create_task(self._ai_behavior_loop())
    
    async def _ai_behavior_loop(self):
        """AI 자동 행동 루프"""
        while self.running:
            if (self.game_state == NetworkGameState.IN_GAME and 
                self.current_turn_player in self.ai_players):
                
                await asyncio.sleep(2)  # 2초 대기 (사람처럼 생각하는 시간)
                
                # AI 자동 행동
                await self._ai_take_action(self.current_turn_player)
            
            await asyncio.sleep(0.5)
    
    async def _ai_take_action(self, ai_id: str):
        """AI 자동 행동"""
        import random
        
        actions = [
            {"action_type": "move", "direction": random.choice(["north", "south", "east", "west"])},
            {"action_type": "skip_turn"},
        ]
        
        # 다른 플레이어가 있으면 공격도 고려
        human_players = [pid for pid, p in self.players.items() if not p.is_ai and p.connection_state == PlayerConnectionState.READY]
        if human_players:
            actions.append({"action_type": "attack", "target_id": random.choice(human_players)})
        
        action = random.choice(actions)
        
        print(f"🤖 AI 행동: {self.players[ai_id].name} - {action['action_type']}")
        
        # AI 행동 처리
        await self._handle_game_action(ai_id, action)
    
    async def _check_all_ready(self):
        """모든 플레이어 준비 상태 확인"""
        ready_players = [p for p in self.players.values() if p.connection_state == PlayerConnectionState.READY]
        total_players = len([p for p in self.players.values() if not p.is_ai])
        
        if len(ready_players) >= 2 and total_players >= 1:  # 최소 1명의 인간 플레이어
            await self._broadcast({
                "type": "all_ready",
                "message": "모든 플레이어가 준비되었습니다! 호스트가 게임을 시작할 수 있습니다."
            })
    
    async def _handle_player_disconnect(self, player_id: str):
        """플레이어 연결 끊김 처리"""
        if player_id in self.players:
            player_name = self.players[player_id].name
            del self.players[player_id]
            
            print(f"👋 플레이어 나감: {player_name}")
            
            # 호스트가 나간 경우 새 호스트 지정
            if player_id == self.host_player_id:
                remaining_players = [p for p in self.players.values() if not p.is_ai]
                if remaining_players:
                    new_host = remaining_players[0]
                    self.host_player_id = new_host.player_id
                    print(f"👑 새 호스트: {new_host.name}")
                    
                    await self._send_to_player(new_host.player_id, {
                        "type": "host_changed",
                        "is_host": True
                    })
            
            # 다른 플레이어들에게 알림
            await self._broadcast({
                "type": "player_left",
                "player_id": player_id,
                "player_name": player_name
            })
    
    async def _send_to_player(self, player_id: str, message: Dict[str, Any]):
        """특정 플레이어에게 메시지 전송"""
        if player_id in self.players and self.players[player_id].websocket:
            try:
                await self.players[player_id].websocket.send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                print(f"❌ 메시지 전송 실패 ({player_id}): {e}")
    
    async def _broadcast(self, message: Dict[str, Any], exclude_player: Optional[str] = None):
        """모든 플레이어에게 브로드캐스트"""
        for player_id, player in self.players.items():
            if player_id != exclude_player and player.websocket and not player.is_ai:
                await self._send_to_player(player_id, message)
    
    async def _broadcast_player_joined(self, new_player: NetworkPlayer):
        """새 플레이어 참가 알림"""
        await self._broadcast({
            "type": "player_joined",
            "player_id": new_player.player_id,
            "player_name": new_player.name,
            "total_players": len([p for p in self.players.values() if not p.is_ai])
        }, exclude_player=new_player.player_id)
    
    async def _sync_game_state(self, player_id: str):
        """게임 상태 동기화"""
        game_state_data = {
            "type": "game_state_sync",
            "game_state": self.game_state.value,
            "session_name": self.session_name,
            "players": [
                {
                    "player_id": pid,
                    "name": p.name,
                    "connection_state": p.connection_state.value,
                    "is_ai": p.is_ai,
                    "ai_type": p.ai_type
                }
                for pid, p in self.players.items()
            ],
            "max_players": self.max_players,
            "current_turn": self.current_turn_player
        }
        
        await self._send_to_player(player_id, game_state_data)
    
    def _get_local_ip(self) -> str:
        """로컬 IP 주소 가져오기"""
        try:
            # 구글 DNS에 연결 시도해서 로컬 IP 확인
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def _generate_connection_qr(self, ip: str):
        """연결용 QR 코드 생성"""
        try:
            connection_url = f"ws://{ip}:{self.port}"
            
            qr = qrcode.QRCode(version=1, box_size=2, border=2)
            qr.add_data(connection_url)
            qr.make(fit=True)
            
            print(f"\n📱 모바일 접속용 QR 코드:")
            qr.print_ascii(invert=True)
            print(f"📱 직접 입력: {connection_url}\n")
            
        except Exception as e:
            print(f"⚠️ QR 코드 생성 실패: {e}")
    
    async def stop_server(self):
        """서버 중지"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        print("🛑 멀티플레이어 서버 중지")

class NetworkMultiplayerClient:
    """네트워크 멀티플레이어 클라이언트"""
    
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.player_id = None
        self.is_host = False
        self.game_state = {}
        self.chat_messages = []
        
    async def connect_to_server(self, host: str, port: int):
        """서버에 연결"""
        try:
            url = f"ws://{host}:{port}"
            print(f"🔗 서버에 연결 중... {url}")
            
            self.websocket = await websockets.connect(url)
            self.connected = True
            
            print(f"✅ 서버 연결 성공!")
            
            # 메시지 수신 루프 시작
            asyncio.create_task(self._message_loop())
            
            return True
            
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            return False
    
    async def _message_loop(self):
        """메시지 수신 루프"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self._handle_server_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 서버 연결이 끊어졌습니다")
            self.connected = False
        except Exception as e:
            print(f"❌ 메시지 수신 오류: {e}")
    
    async def _handle_server_message(self, data: Dict[str, Any]):
        """서버 메시지 처리"""
        msg_type = data.get("type")
        
        if msg_type == "welcome":
            self.player_id = data.get("player_id")
            self.is_host = data.get("is_host", False)
            print(f"🎉 게임방에 입장했습니다! ID: {self.player_id}")
            if self.is_host:
                print("👑 당신은 호스트입니다!")
        
        elif msg_type == "player_joined":
            player_name = data.get("player_name")
            print(f"➕ {player_name}님이 참가했습니다")
        
        elif msg_type == "player_left":
            player_name = data.get("player_name")
            print(f"➖ {player_name}님이 나갔습니다")
        
        elif msg_type == "chat_message":
            player_name = data.get("player_name")
            message = data.get("message")
            timestamp = data.get("timestamp")
            print(f"💬 [{timestamp}] {player_name}: {message}")
        
        elif msg_type == "game_started":
            print(f"🚀 게임이 시작되었습니다!")
            turn_order = data.get("turn_order", [])
            for i, player_info in enumerate(turn_order):
                print(f"   {i+1}. {player_info['name']}")
        
        elif msg_type == "turn_change":
            current_player = data.get("player_name")
            print(f"🎯 {current_player}님의 턴입니다")
        
        elif msg_type == "game_action_result":
            player_name = self.game_state.get("players", {}).get(data.get("player_id"), {}).get("name", "Unknown")
            result = data.get("result", {})
            print(f"🎮 {player_name}: {result.get('message', '액션 실행')}")
        
        elif msg_type == "error":
            print(f"❌ 오류: {data.get('message')}")
        
        # 게임 상태 업데이트
        if "game_state" in data:
            self.game_state.update(data)
    
    async def send_message(self, message: Dict[str, Any]):
        """서버에 메시지 전송"""
        if self.connected and self.websocket:
            try:
                await self.websocket.send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                print(f"❌ 메시지 전송 실패: {e}")
    
    async def set_name(self, name: str):
        """이름 설정"""
        await self.send_message({"type": "set_name", "name": name})
    
    async def ready(self):
        """준비 완료"""
        await self.send_message({"type": "ready"})
    
    async def start_game(self):
        """게임 시작 (호스트만)"""
        if self.is_host:
            await self.send_message({"type": "start_game"})
    
    async def send_chat(self, message: str):
        """채팅 메시지 전송"""
        await self.send_message({"type": "chat", "message": message})
    
    async def send_game_action(self, action: Dict[str, Any]):
        """게임 액션 전송"""
        await self.send_message({"type": "game_action", "action": action})
    
    async def disconnect(self):
        """연결 끊기"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False

async def demo_real_multiplayer():
    """진짜 멀티플레이어 데모"""
    print("🎮 === 진짜 사람끼리 하는 네트워크 멀티플레이어 데모! ===")
    print()
    
    # 서버 시작
    server = RealPlayerMultiplayerServer(port=7176)
    
    # 백그라운드에서 서버 실행
    server_task = asyncio.create_task(server.start_server())
    
    # 잠시 대기
    await asyncio.sleep(3)
    
    print("🔥 서버가 실행 중입니다!")
    print("💡 친구들에게 IP 주소를 알려주고 접속하게 하세요!")
    print("🤖 AI 플레이어들이 테스트용으로 참가했습니다!")
    print()
    print("📋 테스트 방법:")
    print("   1. 다른 컴퓨터나 모바일에서 WebSocket 클라이언트로 접속")
    print("   2. 브라우저에서 JavaScript로 테스트 가능")
    print("   3. AI들과 함께 실제 게임 플레이!")
    print()
    
    # 10초 후 서버 종료 (데모용)
    await asyncio.sleep(10)
    
    def start_multiplayer_session(self):
        """멀티플레이어 세션 시작 (메인 메뉴에서 호출)"""
        print("🎮 멀티플레이어 세션 시작...")
        try:
            # 이벤트 루프 실행
            asyncio.run(self._run_multiplayer_session())
        except Exception as e:
            print(f"❌ 멀티플레이어 세션 오류: {e}")
    
    async def _run_multiplayer_session(self):
        """실제 멀티플레이어 세션 실행"""
        print("🚀 멀티플레이어 서버 시작 중...")
        await self.start_server()
        
        try:
            print("⏳ 플레이어 접속 대기 중...")
            print("   Ctrl+C로 종료할 수 있습니다.")
            
            # 서버 대기
            await self.server.wait_closed()
            
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중단됨")
        except Exception as e:
            print(f"❌ 서버 오류: {e}")
        finally:
            await self.stop_server()

    print("🛑 데모 종료. 서버를 중지합니다...")
    await server.stop_server()

if __name__ == "__main__":
    asyncio.run(demo_real_multiplayer())
