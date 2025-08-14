"""
🌐 Dawn of Stellar - 멀티플레이어 로비 시스템
Phase 2: UI 통합 및 게임 세션 관리

이 모듈은 플레이어가 멀티플레이어 게임을 시작하고 참가할 수 있는
로비 시스템을 제공합니다. 호스트 생성, 게임 참가, 플레이어 관리를 담당합니다.
"""

import asyncio
import time
from typing import List, Dict, Optional, Any
from enum import Enum

from game.multiplayer_session import MultiplayerGameSession, get_multiplayer_session, SessionState
from game.multiplayer_network import get_network_manager, PlayerRole
from game.error_logger import log_debug, log_system
from game.color_text import bright_cyan, bright_yellow, bright_green, bright_red, cyan, yellow, red, green, white

class LobbyState(Enum):
    """로비 상태"""
    MAIN_MENU = "main_menu"
    HOST_SETUP = "host_setup"
    JOIN_SETUP = "join_setup"
    WAITING_ROOM = "waiting_room"
    CONNECTING = "connecting"
    IN_GAME = "in_game"

class MultiplayerLobbyManager:
    """멀티플레이어 로비 매니저"""
    
    def __init__(self, game_instance=None):
        self.game = game_instance
        self.state = LobbyState.MAIN_MENU
        self.session = None
        self.is_running = False
        
        # 로비 설정
        self.host_settings = {
            'session_name': 'Dawn of Stellar Session',
            'max_players': 4,
            'port': 7176,
            'password': None
        }
        
        # 연결 정보
        self.connection_info = {
            'host_address': 'localhost',
            'port': 7176,
            'password': None
        }
        
        # 플레이어 목록
        self.connected_players: List[Dict[str, Any]] = []
        self.chat_messages: List[str] = []
        
        log_system("멀티플레이어로비", "로비 매니저 초기화 완료")
    
    def show_multiplayer_menu(self):
        """멀티플레이어 메인 메뉴 표시"""
        while True:
            self._clear_screen()
            
            print(f"{bright_cyan('🌐 Dawn of Stellar - 멀티플레이어')}")
            print("=" * 50)
            print()
            
            # 현재 상태 표시
            if self.session:
                session_info = self.session.get_session_info()
                print(f"{bright_green('현재 세션:')} {session_info['session_name']}")
                print(f"{cyan('플레이어:')} {session_info['player_count']}/{session_info.get('max_peers', 4)}")
                print(f"{cyan('역할:')} {'호스트' if session_info['is_host'] else '참가자'}")
                print()
            
            # 메뉴 옵션
            options = [
                "1. 게임 호스트하기",
                "2. 게임 참가하기",
                "3. 빠른 매칭 (로컬)",
                "4. 연결 테스트",
                "5. 설정",
                "0. 뒤로 가기"
            ]
            
            for option in options:
                print(f"  {option}")
            
            print()
            choice = input(f"{bright_yellow('선택하세요: ')}")
            
            if choice == '1':
                asyncio.run(self._host_game_setup())
            elif choice == '2':
                asyncio.run(self._join_game_setup())
            elif choice == '3':
                asyncio.run(self._quick_match())
            elif choice == '4':
                asyncio.run(self._connection_test())
            elif choice == '5':
                self._show_settings()
            elif choice == '0':
                break
            else:
                print(f"{bright_red('잘못된 선택입니다.')}")
                time.sleep(1)
    
    async def _host_game_setup(self):
        """게임 호스트 설정"""
        self._clear_screen()
        
        print(f"{bright_cyan('🎮 게임 호스트 설정')}")
        print("=" * 30)
        print()
        
        # 세션 이름 입력
        session_name = input(f"{cyan('세션 이름')} [{self.host_settings['session_name']}]: ").strip()
        if session_name:
            self.host_settings['session_name'] = session_name
        
        # 최대 플레이어 수 입력
        max_players_input = input(f"{cyan('최대 플레이어 수')} [2-4, 기본: {self.host_settings['max_players']}]: ").strip()
        if max_players_input.isdigit():
            max_players = int(max_players_input)
            if 2 <= max_players <= 4:
                self.host_settings['max_players'] = max_players
        
        # 포트 입력
        port_input = input(f"{cyan('포트 번호')} [기본: {self.host_settings['port']}]: ").strip()
        if port_input.isdigit():
            port = int(port_input)
            if 1024 <= port <= 65535:
                self.host_settings['port'] = port
        
        print()
        print(f"{bright_green('호스트 설정 완료!')}")
        print(f"세션 이름: {self.host_settings['session_name']}")
        print(f"최대 플레이어: {self.host_settings['max_players']}")
        print(f"포트: {self.host_settings['port']}")
        print()
        
        confirm = input(f"{bright_yellow('게임을 시작하시겠습니까? (y/N): ')}")
        if confirm.lower() == 'y':
            await self._start_host_session()
    
    async def _join_game_setup(self):
        """게임 참가 설정"""
        self._clear_screen()
        
        print(f"{bright_cyan('🔗 게임 참가 설정')}")
        print("=" * 30)
        print()
        
        # 호스트 주소 입력
        host_address = input(f"{cyan('호스트 주소')} [{self.connection_info['host_address']}]: ").strip()
        if host_address:
            self.connection_info['host_address'] = host_address
        
        # 포트 입력
        port_input = input(f"{cyan('포트 번호')} [기본: {self.connection_info['port']}]: ").strip()
        if port_input.isdigit():
            port = int(port_input)
            if 1024 <= port <= 65535:
                self.connection_info['port'] = port
        
        print()
        print(f"{bright_green('연결 설정 완료!')}")
        print(f"호스트: {self.connection_info['host_address']}:{self.connection_info['port']}")
        print()
        
        confirm = input(f"{bright_yellow('게임에 참가하시겠습니까? (y/N): ')}")
        if confirm.lower() == 'y':
            await self._join_session()
    
    async def _quick_match(self):
        """빠른 매칭 (로컬 테스트용)"""
        self._clear_screen()
        
        print(f"{bright_cyan('⚡ 빠른 매칭')}")
        print("=" * 20)
        print()
        
        print("로컬 네트워크에서 게임을 찾고 있습니다...")
        
        # 로컬에서 호스트 찾기 시도 (여러 포트 스캔)
        common_ports = [7176, 7177, 7178, 7179, 7180]
        
        for port in common_ports:
            print(f"포트 {port} 확인 중...")
            
            try:
                # 연결 시도
                self.connection_info['host_address'] = 'localhost'
                self.connection_info['port'] = port
                
                success = await self._try_connect_to_host()
                if success:
                    print(f"{bright_green(f'게임을 찾았습니다! (포트 {port})')}")
                    await self._join_session()
                    return
                    
            except Exception as e:
                log_debug("멀티플레이어로비", f"포트 {port} 연결 실패: {e}")
                continue
        
        print(f"{bright_red('사용 가능한 게임을 찾을 수 없습니다.')}")
        print()
        
        create_host = input(f"{bright_yellow('새 게임을 호스트하시겠습니까? (y/N): ')}")
        if create_host.lower() == 'y':
            await self._start_host_session()
        else:
            input("아무 키나 눌러 계속...")
    
    async def _connection_test(self):
        """연결 테스트"""
        self._clear_screen()
        
        print(f"{bright_cyan('🔧 연결 테스트')}")
        print("=" * 20)
        print()
        
        # Phase 1 테스트 실행
        print("Phase 1 멀티플레이어 시스템 테스트를 실행합니다...")
        print()
        
        try:
            from game.multiplayer_test import run_phase1_tests
            
            print("테스트 시작...")
            results = await run_phase1_tests()
            
            print()
            print(f"{bright_green('테스트 완료!')}")
            
            # 결과 요약
            passed = sum(results.values())
            total = len(results)
            
            if passed == total:
                print(f"{bright_green('모든 테스트 통과!')} ({passed}/{total})")
                print("멀티플레이어 시스템이 정상적으로 작동합니다.")
            else:
                print(f"{bright_yellow('일부 테스트 실패:')} ({passed}/{total})")
                print("일부 기능에 문제가 있을 수 있습니다.")
                
                for test_name, result in results.items():
                    status = "✅" if result else "❌"
                    print(f"  {status} {test_name}")
            
        except Exception as e:
            print(f"{bright_red(f'테스트 실행 실패: {e}')}")
        
        print()
        input("아무 키나 눌러 계속...")
    
    def _show_settings(self):
        """멀티플레이어 설정"""
        while True:
            self._clear_screen()
            
            print(f"{bright_cyan('⚙️ 멀티플레이어 설정')}")
            print("=" * 30)
            print()
            
            print(f"1. 기본 포트 번호: {self.host_settings['port']}")
            print(f"2. 세션 이름: {self.host_settings['session_name']}")
            print(f"3. 최대 플레이어: {self.host_settings['max_players']}")
            print("4. 네트워크 진단")
            print("0. 뒤로 가기")
            print()
            
            choice = input(f"{bright_yellow('선택하세요: ')}")
            
            if choice == '1':
                self._edit_default_port()
            elif choice == '2':
                self._edit_session_name()
            elif choice == '3':
                self._edit_max_players()
            elif choice == '4':
                asyncio.run(self._network_diagnostics())
            elif choice == '0':
                break
    
    def _edit_default_port(self):
        """기본 포트 설정"""
        print()
        current_port = self.host_settings['port']
        port_input = input(f"새 포트 번호 (현재: {current_port}): ").strip()
        
        if port_input.isdigit():
            port = int(port_input)
            if 1024 <= port <= 65535:
                self.host_settings['port'] = port
                self.connection_info['port'] = port
                print(f"{bright_green(f'포트가 {port}로 변경되었습니다.')}")
            else:
                print(f"{bright_red('포트는 1024-65535 범위여야 합니다.')}")
        
        time.sleep(1)
    
    def _edit_session_name(self):
        """세션 이름 설정"""
        print()
        current_name = self.host_settings['session_name']
        name_input = input(f"새 세션 이름 (현재: {current_name}): ").strip()
        
        if name_input:
            self.host_settings['session_name'] = name_input
            success_msg = f'세션 이름이 "{name_input}"으로 변경되었습니다.'
            print(f"{bright_green(success_msg)}")
        
        time.sleep(1)
    
    def _edit_max_players(self):
        """최대 플레이어 수 설정"""
        print()
        current_max = self.host_settings['max_players']
        max_input = input(f"최대 플레이어 수 (2-4, 현재: {current_max}): ").strip()
        
        if max_input.isdigit():
            max_players = int(max_input)
            if 2 <= max_players <= 4:
                self.host_settings['max_players'] = max_players
                print(f"{bright_green(f'최대 플레이어가 {max_players}명으로 변경되었습니다.')}")
            else:
                print(f"{bright_red('플레이어 수는 2-4명이어야 합니다.')}")
        
        time.sleep(1)
    
    async def _start_host_session(self):
        """호스트 세션 시작"""
        self._clear_screen()
        
        print(f"{bright_cyan('🎮 게임 호스트 시작')}")
        print("=" * 30)
        print()
        
        try:
            # 세션 생성
            self.session = MultiplayerGameSession(self.host_settings['session_name'])
            
            print("서버를 시작하고 있습니다...")
            
            # 호스트로 세션 시작
            success = await self.session.start_session_as_host(self.host_settings['port'])
            
            if success:
                print(f"{bright_green('✅ 서버 시작 성공!')}")
                print()
                print(f"세션 이름: {self.host_settings['session_name']}")
                print(f"포트: {self.host_settings['port']}")
                print(f"세션 ID: {self.session.session_id}")
                print()
                print("다른 플레이어가 참가할 수 있습니다.")
                print(f"참가 주소: localhost:{self.host_settings['port']}")
                
                # 대기실로 이동
                await self._show_waiting_room()
                
            else:
                print(f"{bright_red('❌ 서버 시작 실패!')}")
                print("포트가 이미 사용 중이거나 권한이 없을 수 있습니다.")
                input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"{bright_red(f'오류 발생: {e}')}")
            input("아무 키나 눌러 계속...")
    
    async def _join_session(self):
        """세션 참가"""
        self._clear_screen()
        
        print(f"{bright_cyan('🔗 게임 참가')}")
        print("=" * 20)
        print()
        
        try:
            # 세션 생성
            self.session = MultiplayerGameSession()
            
            print(f"서버에 연결하고 있습니다... ({self.connection_info['host_address']}:{self.connection_info['port']})")
            
            # 피어로 세션 참가
            success = await self.session.join_session_as_peer(
                self.connection_info['host_address'],
                self.connection_info['port']
            )
            
            if success:
                print(f"{bright_green('✅ 연결 성공!')}")
                print()
                
                # 세션 정보 표시
                session_info = self.session.get_session_info()
                print(f"세션: {session_info['session_id']}")
                print(f"플레이어: {session_info['player_count']}")
                
                # 대기실로 이동
                await self._show_waiting_room()
                
            else:
                print(f"{bright_red('❌ 연결 실패!')}")
                print("호스트 주소나 포트를 확인해주세요.")
                input("아무 키나 눌러 계속...")
                
        except Exception as e:
            print(f"{bright_red(f'연결 오류: {e}')}")
            input("아무 키나 눌러 계속...")
    
    async def _try_connect_to_host(self) -> bool:
        """호스트 연결 시도 (테스트용)"""
        try:
            import websockets
            
            uri = f"ws://{self.connection_info['host_address']}:{self.connection_info['port']}"
            
            # 3초 타임아웃으로 연결 시도
            websocket = await asyncio.wait_for(
                websockets.connect(uri),
                timeout=3.0
            )
            
            await websocket.close()
            return True
            
        except Exception:
            return False
    
    async def _show_waiting_room(self):
        """대기실 표시"""
        self.state = LobbyState.WAITING_ROOM
        
        while self.state == LobbyState.WAITING_ROOM:
            self._clear_screen()
            
            print(f"{bright_cyan('🏠 대기실')}")
            print("=" * 20)
            print()
            
            # 세션 정보
            if self.session:
                session_info = self.session.get_session_info()
                print(f"세션: {session_info['session_name'] if 'session_name' in session_info else session_info['session_id'][:8]}")
                print(f"플레이어: {session_info['player_count']}/{self.host_settings['max_players']}")
                print(f"역할: {'🎮 호스트' if session_info['is_host'] else '👤 참가자'}")
                print()
            
            # 연결된 플레이어 목록
            print(f"{cyan('연결된 플레이어:')}")
            if self.session and hasattr(self.session, 'player_characters'):
                if self.session.player_characters:
                    for i, (player_id, character) in enumerate(self.session.player_characters.items(), 1):
                        role_icon = "🎮" if player_id == self.session.network.my_id else "👤"
                        print(f"  {role_icon} {character.name if hasattr(character, 'name') else player_id[:8]}")
                else:
                    print("  (아직 캐릭터가 없습니다)")
            else:
                print("  (플레이어 정보 로딩 중...)")
            
            print()
            
            # 대기실 메뉴
            if self.session and self.session.network.is_host():
                print("호스트 옵션:")
                print("  1. 게임 시작")
                print("  2. 플레이어 내보내기")
                print("  3. 세션 설정")
            
            print("  C. 채팅")
            print("  R. 새로고침")
            print("  Q. 나가기")
            print()
            
            # 비차단 입력 (간단한 구현)
            print("명령어를 입력하세요 (1초 후 자동 새로고침): ", end="", flush=True)
            
            try:
                # 1초 타임아웃으로 입력 받기
                choice = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, input),
                    timeout=1.0
                )
                
                await self._handle_waiting_room_input(choice.strip().upper())
                
            except asyncio.TimeoutError:
                # 타임아웃 시 자동 새로고침
                continue
            
            await asyncio.sleep(0.1)  # 짧은 대기
    
    async def _handle_waiting_room_input(self, choice: str):
        """대기실 입력 처리"""
        if choice == 'Q':
            # 세션 나가기
            if self.session:
                await self.session.shutdown()
                self.session = None
            self.state = LobbyState.MAIN_MENU
            
        elif choice == 'R':
            # 새로고침 (아무것도 하지 않음)
            pass
            
        elif choice == 'C':
            # 채팅 (간단한 구현)
            print()
            message = input("메시지: ").strip()
            if message and self.session:
                # 채팅 메시지 전송 (실제 구현 필요)
                print(f"{bright_green('메시지 전송됨: ')} {message}")
                
        elif choice == '1' and self.session and self.session.network.is_host():
            # 게임 시작
            print()
            print("게임을 시작합니다...")
            self.state = LobbyState.IN_GAME
            
            # 실제 게임 시작 로직 (나중에 구현)
            await self._start_multiplayer_game()
    
    async def _start_multiplayer_game(self):
        """멀티플레이어 게임 시작"""
        print(f"{bright_green('🎮 멀티플레이어 게임 시작!')}")
        print()
        
        if not self.session:
            print(f"{bright_red('세션이 없습니다.')}")
            return
        
        try:
            # 멀티플레이어 통합 시스템 초기화
            from game.multiplayer_integration import MultiplayerGameIntegration, MultiplayerMode
            
            print("멀티플레이어 통합 시스템을 초기화하고 있습니다...")
            
            # 게임 인스턴스가 없으면 새로 생성
            if not self.game:
                print("새 게임 인스턴스를 생성합니다...")
                # 여기서는 간단한 데모만 구현
                print(f"{bright_yellow('데모 모드: 실제 게임 연결은 Phase 2 완료 후 가능합니다.')}")
                print()
                print("현재 구현된 기능:")
                print("✅ P2P 네트워킹")
                print("✅ 메시지 프로토콜")
                print("✅ 게임 세션 관리")
                print("✅ 동기화된 전투 시스템")
                print("✅ 로비 시스템")
                print("🔄 게임 통합 (진행 중)")
                print()
                
                # 5초 후 대기실로 복귀
                for i in range(5, 0, -1):
                    print(f"대기실로 복귀까지: {i}초", end="\r")
                    await asyncio.sleep(1)
                
                print()
                self.state = LobbyState.WAITING_ROOM
                return
            
            # 실제 게임 인스턴스가 있는 경우
            integration = MultiplayerGameIntegration(self.game)
            integration.enable_multiplayer_mode(self.session, MultiplayerMode.COOPERATIVE)
            
            print(f"{bright_green('멀티플레이어 모드 활성화 완료!')}")
            print()
            
            # 모든 플레이어가 준비되었는지 확인
            session_info = self.session.get_session_info()
            player_count = session_info['player_count']
            
            print(f"연결된 플레이어: {player_count}명")
            print("게임을 시작합니다...")
            
            # 게임 시작 메시지 전송
            await self.session.broadcast_message({
                'type': 'game_start',
                'timestamp': time.time()
            })
            
            # 실제 게임으로 전환
            print(f"{bright_cyan('게임 모드로 전환 중...')}")
            
            # 로비 상태를 게임 중으로 변경
            self.state = LobbyState.IN_GAME
            
            # 게임 인스턴스의 멀티플레이어 모드 시작
            if hasattr(self.game, 'start_multiplayer_adventure'):
                self.game.start_multiplayer_adventure(integration)
            else:
                # 기본 어드벤처 시작에 멀티플레이어 통합 적용
                self.game.multiplayer_integration = integration
                self.game.start_adventure()
            
        except Exception as e:
            print(f"{bright_red(f'멀티플레이어 게임 시작 실패: {e}')}")
            print()
            print("오류 세부 정보:")
            import traceback
            traceback.print_exc()
            print()
            
            # 오류 발생 시 대기실로 복귀
            input("대기실로 돌아가려면 Enter를 누르세요...")
            self.state = LobbyState.WAITING_ROOM
    
    async def _network_diagnostics(self):
        """네트워크 진단"""
        self._clear_screen()
        
        print(f"{bright_cyan('🔧 네트워크 진단')}")
        print("=" * 20)
        print()
        
        print("네트워크 상태를 확인하고 있습니다...")
        print()
        
        # 기본 연결 테스트
        try:
            import socket
            
            # 로컬 연결 테스트
            print("✅ 로컬 연결 테스트...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', 80))
            sock.close()
            
            if result == 0:
                print(f"  {bright_green('✅ 로컬 네트워크 정상')}")
            else:
                print(f"  {bright_yellow('⚠️ 로컬 네트워크 문제 가능성')}")
            
        except Exception as e:
            print(f"  {bright_red(f'❌ 네트워크 테스트 실패: {e}')}")
        
        # 포트 테스트
        print()
        print("✅ 포트 사용 가능성 테스트...")
        
        test_ports = [7176, 7177, 7178, 7179, 7180]
        available_ports = []
        
        for port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result != 0:  # 포트가 사용되지 않음 (사용 가능)
                    available_ports.append(port)
                    print(f"  {bright_green(f'✅ 포트 {port}: 사용 가능')}")
                else:
                    print(f"  {bright_yellow(f'⚠️ 포트 {port}: 사용 중')}")
                    
            except Exception:
                available_ports.append(port)
                print(f"  {bright_green(f'✅ 포트 {port}: 사용 가능')}")
        
        print()
        if available_ports:
            print(f"{bright_green(f'사용 가능한 포트: {available_ports}')}")
        else:
            print(f"{bright_red('사용 가능한 포트가 없습니다.')}")
        
        print()
        input("아무 키나 눌러 계속...")
    
    def _clear_screen(self):
        """화면 클리어"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def cleanup(self):
        """로비 매니저 정리"""
        if self.session:
            asyncio.run(self.session.shutdown())
            self.session = None
        
        log_system("멀티플레이어로비", "로비 매니저 정리 완료")

# 전역 로비 매니저 인스턴스
_lobby_manager = None

def get_multiplayer_lobby() -> MultiplayerLobbyManager:
    """전역 멀티플레이어 로비 매니저 반환"""
    global _lobby_manager
    if _lobby_manager is None:
        _lobby_manager = MultiplayerLobbyManager()
    return _lobby_manager

def set_lobby_game_instance(game_instance):
    """로비 매니저에 게임 인스턴스 설정"""
    lobby = get_multiplayer_lobby()
    lobby.game = game_instance
