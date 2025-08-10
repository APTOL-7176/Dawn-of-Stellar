# 🌟 Dawn of Stellar v4.0.0 - 멀티플레이어 시스템 설계서

## 📋 프로젝트 개요

**Dawn of Stellar v4.0.0**은 완전한 **P2P 멀티플레이어 로그라이크 RPG**를 목표로 합니다.
기존의 단일 플레이어 경험을 확장하여 최대 4명의 플레이어가 협력하여 던전을 탐험할 수 있습니다.

### 🎯 핵심 목표
- **For The King 스타일**: 각 캐릭터에 플레이어/AI 할당 방식
- **P2P 네트워킹**: 별도 서버 없이 직접 연결
- **완벽한 동기화**: 모든 게임 상태의 실시간 동기화
- **기존 시스템 호환**: 현재 캐릭터/아이템/세이브 시스템과 완전 연동

---

## 🏗️ 시스템 아키텍처

### 1. 네트워크 구조 (P2P with Host Authority)

```
┌─────────────────────────────────────────────────────────────┐
│                    멀티플레이어 세션                          │
├─────────────────────────────────────────────────────────────┤
│  방장(Host) ◄─────────► 플레이어2 (Client)                │
│     │                        │                              │
│     │                        │                              │
│     ▼                        ▼                              │
│  플레이어3 ◄─────────► 플레이어4 (Clients)                │
│                                                             │
│  ✅ 방장 = 권한 보유 (저장, 설정, 동기화 기준점)             │
│  ✅ 리더 = 월드 이동 담당 (변경 가능)                       │
│  ✅ 모든 클라이언트는 서로 직접 통신                        │
└─────────────────────────────────────────────────────────────┘
```

### 2. 역할 분담 시스템

#### 🏛️ 방장 (Host) - 고정 역할
- **게임 세션 생성 및 관리**
- **세이브/로드 권한** (유일한 저장 권한 보유)
- **동기화 기준점** (충돌 시 방장 데이터 우선)
- **플레이어 입장/퇴장 관리**
- **게임 설정** (난이도, 패시브 등)

#### 👑 리더 (Leader) - 변경 가능 역할
- **월드 이동 결정** (던전 층 이동, 마을 방문 등)
- **전역 결정** (휴식, 상점 방문 등)
- **인카운터 발생 시 대응 결정**
- **리더 권한은 투표나 방장 지정으로 변경 가능**

#### 🎮 플레이어 (Player)
- **자신의 캐릭터 완전 제어**
- **전투 중 행동 선택**
- **개별 인벤토리 관리**
- **채팅 참여**

#### 🤖 AI 플레이어
- **빈 슬롯에 AI 자동 배치**
- **플레이어와 동일한 권한으로 동작**
- **방장이 AI 난이도/전략 설정 가능**

---

## 🎮 게임플레이 시스템

### 1. 세션 생성 및 참가

#### 세션 생성 (방장)
```python
class MultiplayerSession:
    def __init__(self):
        self.session_id = generate_unique_id()
        self.host_player = current_player
        self.version = __version__  # 버전 호환성 체크
        self.max_players = 4
        self.current_players = []
        self.leader_id = None  # 리더는 별도 지정
        self.game_settings = {
            'difficulty': 'normal',
            'shared_passives': [],
            'map_size': 'medium',
            'permadeath': False
        }
```

#### 세션 참가 (클라이언트)
```python
def join_session(session_id, player_character):
    # 1. 버전 호환성 체크
    if not check_version_compatibility(session_id):
        raise VersionMismatchError("호스트와 클라이언트 버전이 다릅니다")
    
    # 2. 캐릭터 데이터 전송 (기존 캐릭터 파일 기반)
    character_data = load_character_preset(player_character)
    
    # 3. 세션 입장 요청
    return request_join(session_id, character_data)
```

### 2. 캐릭터 및 인벤토리 시스템

#### 캐릭터 불러오기
- **기존 캐릭터 생성 시스템 활용**
- **캐릭터 프리셋 파일(.json) 불러오기**
- **창고 시스템 연동** (시작 시 아이템 선택 가능)
- **개별 인벤토리** (각 플레이어가 독립적으로 관리)

```python
class MultiplayerCharacter:
    def __init__(self, preset_file, warehouse_items=None):
        self.base_character = load_character_preset(preset_file)
        self.player_id = None  # 할당된 플레이어 ID
        self.is_ai_controlled = False
        self.starting_items = warehouse_items or []
        self.individual_progress = IndividualProgress()
```

#### 창고 시스템 연동
```python
class WarehouseIntegration:
    def select_starting_items(self, warehouse_data, max_items=10):
        """세션 시작 전 창고에서 아이템 선택"""
        selected_items = show_warehouse_selection_ui(warehouse_data, max_items)
        return selected_items
    
    def sync_post_game_items(self, gained_items):
        """게임 종료 후 획득 아이템을 개별 창고에 저장"""
        update_individual_warehouse(self.player_id, gained_items)
```

### 3. 동기화 시스템

#### 실시간 동기화 대상
```python
class SyncData:
    # 전역 동기화 (모든 플레이어 동일)
    world_state = {
        'current_floor': 1,
        'map_layout': None,
        'enemies_positions': {},
        'encounters': [],
        'discovered_areas': set(),
        'global_events': []
    }
    
    # 전투 동기화
    combat_state = {
        'turn_order': [],
        'atb_gauges': {},
        'battlefield_positions': {},
        'active_effects': {}
    }
    
    # 개별 데이터 (동기화하지 않음)
    individual_data = {
        'character_stats': {},  # 메타 진행도
        'personal_inventory': {},
        'individual_progress': {},
        'achievements': {}
    }
```

#### 동기화 메커니즘
```python
class SynchronizationManager:
    def __init__(self):
        self.sync_frequency = 60  # 60 FPS
        self.priority_events = []  # 즉시 동기화 이벤트
        self.batch_events = []     # 배치 동기화 이벤트
    
    def handle_critical_sync(self, event):
        """즉시 동기화가 필요한 이벤트 (전투, 이동 등)"""
        broadcast_to_all_clients(event)
        
    def handle_batch_sync(self, events):
        """배치로 처리 가능한 이벤트 (UI 업데이트 등)"""
        accumulated_events.extend(events)
        if len(accumulated_events) > BATCH_SIZE:
            flush_batch_sync()
```

#### 충돌 해결 (Host Authority)
```python
class ConflictResolution:
    def resolve_state_conflict(self, host_state, client_state):
        """상태 충돌 시 방장 데이터 우선 적용"""
        if host_state != client_state:
            log_conflict(f"State conflict detected. Using host authority.")
            return host_state
        return client_state
    
    def handle_desync(self, player_id):
        """동기화 실패 시 전체 상태 재전송"""
        full_state = get_complete_game_state()
        send_full_resync(player_id, full_state)
```

---

## 💾 세이브/로드 시스템

### 1. 세이브 파일 구조

```python
class MultiplayerSaveData:
    def __init__(self):
        self.version = __version__  # 버전 정보 (필수)
        self.session_info = {
            'session_id': str,
            'host_id': str,
            'creation_time': datetime,
            'last_save_time': datetime,
            'total_playtime': int
        }
        
        # 공통 게임 상태
        self.world_state = WorldState()
        self.shared_progress = SharedProgress()
        self.game_settings = GameSettings()
        
        # 각 플레이어별 데이터
        self.player_data = {
            'player_1': PlayerSaveData(),
            'player_2': PlayerSaveData(),
            'player_3': PlayerSaveData(),
            'player_4': PlayerSaveData()
        }
```

### 2. 저장 권한 및 프로세스

#### 방장 전용 저장
```python
class SaveSystem:
    def save_multiplayer_session(self):
        if not self.is_host:
            raise PermissionError("저장은 방장만 가능합니다")
        
        # 1. 모든 클라이언트에서 현재 상태 수집
        all_player_data = collect_all_player_states()
        
        # 2. 통합 세이브 파일 생성
        save_data = create_multiplayer_save(all_player_data)
        
        # 3. 방장 로컬에 저장
        save_path = save_multiplayer_data(save_data)
        
        # 4. 모든 클라이언트에게 세이브 파일 전송
        distribute_save_file(save_path, all_clients)
        
        # 5. 개별 창고 데이터 업데이트
        update_individual_warehouses()
```

#### 로드 시 버전 체크
```python
def load_multiplayer_session(save_file):
    save_data = load_save_file(save_file)
    
    # 버전 호환성 체크
    if not is_compatible_version(save_data.version, __version__):
        show_version_mismatch_dialog(save_data.version, __version__)
        return False
    
    # 모든 플레이어가 동일한 버전인지 확인
    for player in session.players:
        if player.version != __version__:
            kick_player(player, "버전 불일치")
    
    return restore_game_state(save_data)
```

---

## 🌐 네트워킹 구현

### 1. P2P 연결 관리

```python
import socket
import threading
import json
from typing import Dict, List

class P2PNetworkManager:
    def __init__(self):
        self.host_socket = None
        self.client_sockets: Dict[str, socket.socket] = {}
        self.is_host = False
        self.player_id = generate_player_id()
        
    def create_session(self, port=7176):
        """방장이 세션 생성"""
        self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_socket.bind(('localhost', port))
        self.host_socket.listen(3)  # 최대 3명 추가 접속
        self.is_host = True
        
        # 접속 대기 스레드 시작
        threading.Thread(target=self.accept_connections, daemon=True).start()
        
    def join_session(self, host_ip, port=7176):
        """클라이언트가 세션 참가"""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host_ip, port))
        
        # 버전 정보 전송
        version_info = {
            'type': 'version_check',
            'version': __version__,
            'player_id': self.player_id
        }
        self.send_message(client_socket, version_info)
        
        # 응답 대기
        response = self.receive_message(client_socket)
        if response['status'] != 'version_ok':
            raise ConnectionError(f"버전 불일치: {response['message']}")
            
        return client_socket
```

### 2. 메시지 프로토콜

```python
class MessageProtocol:
    """게임 이벤트 메시지 정의"""
    
    # 게임 상태 동기화
    WORLD_UPDATE = "world_update"
    PLAYER_MOVE = "player_move"
    COMBAT_ACTION = "combat_action"
    INVENTORY_CHANGE = "inventory_change"
    
    # 세션 관리
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    LEADER_CHANGE = "leader_change"
    SAVE_REQUEST = "save_request"
    
    # 채팅
    CHAT_MESSAGE = "chat_message"
    
    # 동기화 제어
    FULL_RESYNC = "full_resync"
    HEARTBEAT = "heartbeat"

class MessageHandler:
    def handle_message(self, message):
        msg_type = message['type']
        
        if msg_type == MessageProtocol.WORLD_UPDATE:
            self.handle_world_update(message['data'])
        elif msg_type == MessageProtocol.COMBAT_ACTION:
            self.handle_combat_action(message['data'])
        elif msg_type == MessageProtocol.CHAT_MESSAGE:
            self.handle_chat_message(message['data'])
        # ... 기타 메시지 처리
```

---

## 💬 채팅 시스템

### 1. 채팅 기능

```python
class ChatSystem:
    def __init__(self):
        self.chat_history = []
        self.max_history = 100
        self.chat_window_visible = True
        
    def send_chat_message(self, message, sender_id):
        chat_data = {
            'type': 'chat_message',
            'sender_id': sender_id,
            'sender_name': get_player_name(sender_id),
            'message': message,
            'timestamp': time.time(),
            'message_type': 'public'  # public, system, whisper
        }
        
        # 모든 플레이어에게 브로드캐스트
        broadcast_message(chat_data)
        
    def handle_system_message(self, message):
        """시스템 메시지 (플레이어 입장/퇴장, 리더 변경 등)"""
        system_msg = {
            'type': 'chat_message',
            'sender_id': 'system',
            'sender_name': 'System',
            'message': message,
            'timestamp': time.time(),
            'message_type': 'system'
        }
        broadcast_message(system_msg)
```

### 2. 채팅 UI 통합

```python
class GameUI:
    def __init__(self):
        self.chat_panel = ChatPanel()
        self.game_panel = GamePanel()
        
    def render_with_chat(self):
        """게임 화면과 채팅창 동시 렌더링"""
        screen_height = get_terminal_height()
        
        # 채팅창 크기 (하단 1/4)
        chat_height = screen_height // 4
        game_height = screen_height - chat_height
        
        # 게임 화면 렌더링
        game_output = self.game_panel.render(height=game_height)
        
        # 채팅창 렌더링
        chat_output = self.chat_panel.render(height=chat_height)
        
        # 통합 출력
        print(game_output + "\n" + "="*50 + "\n" + chat_output)
```

---

## 🎯 동기화 세부 사항

### 1. 우선순위 기반 동기화

```python
class SyncPriority:
    CRITICAL = 0    # 즉시 동기화 (전투 행동, 이동)
    HIGH = 1        # 높은 우선순위 (인벤토리 변경)
    MEDIUM = 2      # 중간 우선순위 (UI 업데이트)
    LOW = 3         # 낮은 우선순위 (통계, 로그)

class EventQueue:
    def __init__(self):
        self.queues = {
            SyncPriority.CRITICAL: [],
            SyncPriority.HIGH: [],
            SyncPriority.MEDIUM: [],
            SyncPriority.LOW: []
        }
        
    def process_events(self):
        # 우선순위 순으로 처리
        for priority in [SyncPriority.CRITICAL, SyncPriority.HIGH, 
                        SyncPriority.MEDIUM, SyncPriority.LOW]:
            while self.queues[priority]:
                event = self.queues[priority].pop(0)
                self.handle_event(event)
```

### 2. 전투 시스템 동기화

```python
class MultiplayerCombat:
    def __init__(self):
        self.turn_manager = MultiplayerTurnManager()
        self.action_queue = []
        
    def handle_player_action(self, player_id, action):
        """플레이어 행동 처리 및 동기화"""
        # 1. 행동 유효성 검사
        if not self.validate_action(player_id, action):
            return False
            
        # 2. 모든 클라이언트에 즉시 브로드캐스트
        action_data = {
            'type': 'combat_action',
            'player_id': player_id,
            'action': action,
            'timestamp': time.time()
        }
        broadcast_critical_event(action_data)
        
        # 3. 로컬에서 실행
        result = self.execute_action(action)
        
        # 4. 결과 동기화
        result_data = {
            'type': 'action_result',
            'action_id': action.id,
            'result': result
        }
        broadcast_critical_event(result_data)
        
        return True
```

---

## 🛡️ 오류 처리 및 복구

### 1. 네트워크 연결 끊김 처리

```python
class ConnectionManager:
    def __init__(self):
        self.heartbeat_interval = 5.0  # 5초마다 확인
        self.timeout_limit = 15.0      # 15초 무응답시 연결 끊김
        
    def handle_player_disconnect(self, player_id):
        """플레이어 연결 끊김 처리"""
        # 1. 해당 플레이어 캐릭터를 AI로 전환
        character = get_player_character(player_id)
        character.set_ai_controlled(True)
        
        # 2. 다른 플레이어들에게 알림
        system_message = f"{character.name}의 연결이 끊어져 AI가 대신 조작합니다."
        send_system_message(system_message)
        
        # 3. 세션에서 플레이어 제거
        self.session.remove_player(player_id)
        
    def handle_reconnection(self, player_id):
        """플레이어 재접속 처리"""
        # 1. 현재 게임 상태 전송
        full_state = get_complete_game_state()
        send_full_resync(player_id, full_state)
        
        # 2. AI를 플레이어 컨트롤로 복구
        character = get_player_character(player_id)
        character.set_ai_controlled(False)
        
        # 3. 재접속 알림
        system_message = f"{character.name}이 다시 접속했습니다."
        send_system_message(system_message)
```

### 2. 상태 불일치 해결

```python
class StateValidator:
    def validate_game_state(self):
        """주기적으로 모든 클라이언트 상태 검증"""
        host_state = get_host_game_state()
        
        for client_id in self.session.clients:
            client_state = request_client_state(client_id)
            
            if not self.states_match(host_state, client_state):
                self.handle_state_mismatch(client_id, host_state, client_state)
                
    def handle_state_mismatch(self, client_id, host_state, client_state):
        """상태 불일치 시 방장 상태로 동기화"""
        log_error(f"State mismatch detected for client {client_id}")
        
        # 방장 상태를 클라이언트에 강제 적용
        send_forced_state_update(client_id, host_state)
        
        # 시스템 메시지로 알림
        send_system_message("게임 상태가 동기화되었습니다.")
```

---

## 📊 구현 우선순위 및 로드맵

### Phase 1: 기본 인프라 (v4.0.0-alpha)
1. **P2P 네트워킹 시스템**
2. **기본 세션 생성/참가**
3. **버전 호환성 체크**
4. **메시지 프로토콜 구현**

### Phase 2: 게임플레이 통합 (v4.0.0-beta)
1. **캐릭터/창고 시스템 연동**
2. **기본 동기화 시스템**
3. **채팅 기능**
4. **리더/방장 권한 시스템**

### Phase 3: 완전한 멀티플레이 (v4.0.0-rc)
1. **전투 시스템 동기화**
2. **세이브/로드 시스템**
3. **오류 처리 및 복구**
4. **성능 최적화**

### Phase 4: 폴리싱 (v4.0.0-stable)
1. **UI/UX 개선**
2. **밸런스 조정**
3. **추가 기능** (관전 모드, 킥 기능 등)
4. **문서화 및 가이드**

---

## 🔧 기술적 고려사항

### 1. 성능 최적화
- **메시지 압축**: JSON 대신 바이너리 프로토콜 고려
- **배치 처리**: 비중요 이벤트는 묶어서 전송
- **예측 시스템**: 네트워크 지연 보상을 위한 클라이언트 예측
- **LOD (Level of Detail)**: 거리에 따른 동기화 세밀도 조정

### 2. 보안 고려사항
- **치팅 방지**: 클라이언트 검증 시스템
- **데이터 검증**: 모든 네트워크 데이터 유효성 검사
- **세이브 파일 보호**: 세이브 파일 해시 체크
- **권한 관리**: 방장/리더 권한 악용 방지

### 3. 사용자 경험
- **직관적인 UI**: 멀티플레이어 상태를 명확히 표시
- **오프라인 모드**: 네트워크 없이도 AI와 플레이 가능
- **관전 모드**: 접속자가 게임을 관전할 수 있는 기능
- **음성 채팅**: 추후 Discord 연동 고려

---

## 🎯 결론

**Dawn of Stellar v4.0.0**의 멀티플레이어 시스템은 기존의 단일 플레이어 경험을 손상시키지 않으면서도 
완전히 새로운 협력 플레이 경험을 제공할 것입니다.

**핵심 설계 원칙**:
1. **기존 시스템과의 완벽한 호환성**
2. **안정적이고 신뢰할 수 있는 동기화**
3. **직관적이고 재미있는 멀티플레이어 경험**
4. **확장 가능한 아키텍처**

이 설계서를 바탕으로 단계별로 구현해나가면 **세계 최고의 로그라이크 멀티플레이어 게임**을 만들 수 있을 것입니다! 🌟

---

**📝 다음 단계**: 각 시스템의 상세 구현 명세서 작성 및 프로토타입 개발 시작
