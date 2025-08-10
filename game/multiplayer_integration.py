"""
🎮 Dawn of Stellar - 멀티플레이어 인게임 통합 시스템
Phase 2: 실제 게임플레이 중 멀티플레이어 기능 통합

이 모듈은 기존 싱글플레이어 게임에 멀티플레이어 기능을 원활하게 통합합니다.
던전 탐험, 전투, 아이템 공유 등의 기능을 동기화합니다.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from .multiplayer_session import MultiplayerGameSession, get_multiplayer_session, SessionState
from .multiplayer_combat import MultiplayerBraveCombatSystem
from .error_logger import log_debug, log_system, log_player
from .color_text import bright_cyan, bright_yellow, bright_green, bright_red, cyan, yellow, red, green, white

class MultiplayerMode(Enum):
    """멀티플레이어 모드"""
    SINGLE_PLAYER = "single_player"
    COOPERATIVE = "cooperative"  # 협력 모드
    COMPETITIVE = "competitive"  # 경쟁 모드 (나중에 구현)

class MultiplayerGameIntegration:
    """멀티플레이어 게임 통합 시스템"""
    
    def __init__(self, game_instance):
        self.game = game_instance
        self.mode = MultiplayerMode.SINGLE_PLAYER
        self.session: Optional[MultiplayerGameSession] = None
        self.multiplayer_combat: Optional[MultiplayerBraveCombatSystem] = None
        
        # 동기화 설정
        self.sync_enabled = False
        self.sync_interval = 0.5  # 0.5초마다 동기화
        self.last_sync_time = 0
        
        # 플레이어 위치 추적
        self.player_positions: Dict[str, Tuple[int, int]] = {}
        self.shared_map_data: Dict = {}
        
        log_system("멀티플레이어통합", "멀티플레이어 게임 통합 시스템 초기화 완료")
    
    def is_multiplayer_active(self) -> bool:
        """멀티플레이어가 활성화되어 있는지 확인"""
        return (
            self.mode != MultiplayerMode.SINGLE_PLAYER and
            self.session is not None and
            self.session.is_connected()
        )
    
    def enable_multiplayer_mode(self, session: MultiplayerGameSession, mode: MultiplayerMode = MultiplayerMode.COOPERATIVE):
        """멀티플레이어 모드 활성화"""
        self.session = session
        self.mode = mode
        self.sync_enabled = True
        
        # 멀티플레이어 전투 시스템 초기화
        if hasattr(self.game, 'brave_combat') and self.game.brave_combat:
            self.multiplayer_combat = MultiplayerBraveCombatSystem(
                self.session,
                self.game.brave_combat.characters
            )
        
        log_system("멀티플레이어통합", f"멀티플레이어 모드 활성화: {mode.value}")
    
    def disable_multiplayer_mode(self):
        """멀티플레이어 모드 비활성화"""
        self.mode = MultiplayerMode.SINGLE_PLAYER
        self.sync_enabled = False
        self.session = None
        self.multiplayer_combat = None
        
        log_system("멀티플레이어통합", "멀티플레이어 모드 비활성화")
    
    async def sync_game_state(self):
        """게임 상태 동기화"""
        if not self.is_multiplayer_active() or not self.sync_enabled:
            return
        
        current_time = time.time()
        if current_time - self.last_sync_time < self.sync_interval:
            return
        
        try:
            # 플레이어 위치 동기화
            if hasattr(self.game, 'world') and self.game.world:
                await self._sync_player_position()
            
            # 던전 맵 데이터 동기화
            if hasattr(self.game, 'world') and self.game.world and hasattr(self.game.world, 'current_floor'):
                await self._sync_map_data()
            
            # 파티 상태 동기화
            if hasattr(self.game, 'party_manager') and self.game.party_manager:
                await self._sync_party_state()
            
            self.last_sync_time = current_time
            
        except Exception as e:
            log_debug("멀티플레이어통합", f"게임 상태 동기화 오류: {e}")
    
    async def _sync_player_position(self):
        """플레이어 위치 동기화"""
        if not self.session or not hasattr(self.game, 'world'):
            return
        
        try:
            # 현재 플레이어 위치 전송
            player_pos = self.game.world.player_pos
            await self.session.broadcast_message({
                'type': 'player_position',
                'player_id': self.session.network.my_id,
                'position': player_pos,
                'floor': getattr(self.game.world, 'current_floor', 1)
            })
            
            # 다른 플레이어 위치 업데이트
            if hasattr(self.session, 'received_messages'):
                for msg in self.session.received_messages:
                    if msg.get('type') == 'player_position':
                        player_id = msg.get('player_id')
                        position = msg.get('position')
                        if player_id and position and player_id != self.session.network.my_id:
                            self.player_positions[player_id] = position
            
        except Exception as e:
            log_debug("멀티플레이어통합", f"위치 동기화 오류: {e}")
    
    async def _sync_map_data(self):
        """맵 데이터 동기화"""
        if not self.session or not hasattr(self.game, 'world'):
            return
        
        try:
            # 호스트만 맵 데이터를 전송
            if self.session.network.is_host():
                world = self.game.world
                map_data = {
                    'type': 'map_data',
                    'floor': getattr(world, 'current_floor', 1),
                    'discovered_tiles': getattr(world, 'discovered', set()),
                    'map_size': (getattr(world, 'width', 50), getattr(world, 'height', 25))
                }
                
                # set을 list로 변환 (JSON 직렬화를 위해)
                if isinstance(map_data['discovered_tiles'], set):
                    map_data['discovered_tiles'] = list(map_data['discovered_tiles'])
                
                await self.session.broadcast_message(map_data)
            
            # 호스트가 아닌 경우 맵 데이터 수신
            else:
                if hasattr(self.session, 'received_messages'):
                    for msg in self.session.received_messages:
                        if msg.get('type') == 'map_data':
                            self.shared_map_data = msg
                            # 수신된 맵 데이터를 게임에 적용
                            await self._apply_shared_map_data()
            
        except Exception as e:
            log_debug("멀티플레이어통합", f"맵 데이터 동기화 오류: {e}")
    
    async def _apply_shared_map_data(self):
        """공유된 맵 데이터 적용"""
        if not self.shared_map_data or not hasattr(self.game, 'world'):
            return
        
        try:
            world = self.game.world
            
            # 발견된 타일 정보 동기화
            if 'discovered_tiles' in self.shared_map_data:
                discovered = self.shared_map_data['discovered_tiles']
                if isinstance(discovered, list):
                    discovered = set(discovered)
                
                if hasattr(world, 'discovered'):
                    world.discovered.update(discovered)
                else:
                    world.discovered = discovered
            
        except Exception as e:
            log_debug("멀티플레이어통합", f"맵 데이터 적용 오류: {e}")
    
    async def _sync_party_state(self):
        """파티 상태 동기화"""
        if not self.session or not hasattr(self.game, 'party_manager'):
            return
        
        try:
            party_manager = self.game.party_manager
            
            # 파티 상태 정보 생성
            party_state = {
                'type': 'party_state',
                'player_id': self.session.network.my_id,
                'members': []
            }
            
            # 파티 멤버 정보 수집
            for member in party_manager.members:
                member_data = {
                    'name': member.name,
                    'job_class': member.job_class,
                    'level': member.level,
                    'current_hp': member.current_hp,
                    'max_hp': member.max_hp,
                    'current_mp': member.current_mp,
                    'max_mp': member.max_mp
                }
                party_state['members'].append(member_data)
            
            # 파티 상태 전송
            await self.session.broadcast_message(party_state)
            
        except Exception as e:
            log_debug("멀티플레이어통합", f"파티 상태 동기화 오류: {e}")
    
    def handle_multiplayer_input(self, command: str) -> bool:
        """멀티플레이어 관련 입력 처리"""
        if not self.is_multiplayer_active():
            return False
        
        # 멀티플레이어 전용 명령어 처리
        if command.lower().startswith('/'):
            return self._handle_multiplayer_command(command)
        
        return False
    
    def _handle_multiplayer_command(self, command: str) -> bool:
        """멀티플레이어 명령어 처리"""
        cmd_parts = command[1:].split(' ', 1)
        cmd = cmd_parts[0].lower()
        args = cmd_parts[1] if len(cmd_parts) > 1 else ""
        
        if cmd == 'say' or cmd == 'chat':
            # 채팅 메시지 전송
            asyncio.run(self._send_chat_message(args))
            return True
            
        elif cmd == 'players' or cmd == 'who':
            # 연결된 플레이어 목록 표시
            self._show_connected_players()
            return True
            
        elif cmd == 'sync':
            # 수동 동기화
            asyncio.run(self.sync_game_state())
            print(f"{bright_green('게임 상태가 동기화되었습니다.')}")
            return True
            
        elif cmd == 'disconnect':
            # 연결 해제
            self._disconnect_from_session()
            return True
        
        return False
    
    async def _send_chat_message(self, message: str):
        """채팅 메시지 전송"""
        if not message.strip():
            print(f"{bright_red('메시지를 입력해주세요.')}")
            return
        
        try:
            chat_msg = {
                'type': 'chat',
                'player_id': self.session.network.my_id,
                'message': message.strip(),
                'timestamp': time.time()
            }
            
            await self.session.broadcast_message(chat_msg)
            print(f"{bright_cyan('[나]')} {message}")
            
        except Exception as e:
            print(f"{bright_red(f'채팅 전송 실패: {e}')}")
    
    def _show_connected_players(self):
        """연결된 플레이어 목록 표시"""
        if not self.session:
            return
        
        print(f"\n{bright_cyan('🌐 연결된 플레이어:')}")
        
        # 내 정보 표시
        my_id = self.session.network.my_id
        role = "🎮 호스트" if self.session.network.is_host() else "👤 참가자"
        print(f"  {role} {my_id[:8]} (나)")
        
        # 다른 플레이어 정보 표시
        if hasattr(self.session, 'player_characters'):
            for player_id, character in self.session.player_characters.items():
                if player_id != my_id:
                    char_name = character.name if hasattr(character, 'name') else "알 수 없음"
                    print(f"  👤 {player_id[:8]} ({char_name})")
        
        print()
    
    def _disconnect_from_session(self):
        """세션에서 연결 해제"""
        if self.session:
            asyncio.run(self.session.shutdown())
            self.disable_multiplayer_mode()
            print(f"{bright_yellow('멀티플레이어 세션에서 연결을 해제했습니다.')}")
    
    def show_multiplayer_status(self):
        """멀티플레이어 상태 표시"""
        if not self.is_multiplayer_active():
            return
        
        try:
            session_info = self.session.get_session_info()
            
            status_text = f"{cyan('🌐 멀티플레이어:')} "
            status_text += f"{session_info['player_count']}명 연결 | "
            status_text += f"{'호스트' if session_info['is_host'] else '참가자'}"
            
            if self.player_positions:
                status_text += f" | 위치 동기화 중"
            
            print(status_text)
            
        except Exception as e:
            log_debug("멀티플레이어통합", f"상태 표시 오류: {e}")
    
    def handle_multiplayer_combat(self, combat_system):
        """멀티플레이어 전투 처리"""
        if not self.is_multiplayer_active():
            return combat_system
        
        # 멀티플레이어 전투 시스템으로 교체
        if self.multiplayer_combat:
            return self.multiplayer_combat
        
        return combat_system
    
    def get_other_players_positions(self) -> Dict[str, Tuple[int, int]]:
        """다른 플레이어들의 위치 반환"""
        return self.player_positions.copy()
    
    def display_other_players_on_map(self, display_func):
        """맵에 다른 플레이어들 표시"""
        if not self.is_multiplayer_active():
            return
        
        try:
            # 다른 플레이어 위치에 표시 추가
            for player_id, position in self.player_positions.items():
                if position and len(position) == 2:
                    x, y = position
                    # 플레이어 아이콘으로 '@'의 다른 색상 버전 사용
                    player_icon = f"{bright_yellow('@')}"  # 다른 플레이어는 노란색
                    
                    # 표시 함수 호출 (구체적인 구현은 게임의 맵 표시 시스템에 따라 달라짐)
                    if callable(display_func):
                        display_func(x, y, player_icon, f"플레이어 {player_id[:4]}")
            
        except Exception as e:
            log_debug("멀티플레이어통합", f"다른 플레이어 표시 오류: {e}")

# 전역 멀티플레이어 통합 인스턴스
_multiplayer_integration = None

def get_multiplayer_integration() -> Optional[MultiplayerGameIntegration]:
    """전역 멀티플레이어 통합 인스턴스 반환"""
    global _multiplayer_integration
    return _multiplayer_integration

def set_multiplayer_integration(integration: MultiplayerGameIntegration):
    """전역 멀티플레이어 통합 인스턴스 설정"""
    global _multiplayer_integration
    _multiplayer_integration = integration

def initialize_multiplayer_integration(game_instance) -> MultiplayerGameIntegration:
    """멀티플레이어 통합 초기화"""
    integration = MultiplayerGameIntegration(game_instance)
    set_multiplayer_integration(integration)
    return integration
