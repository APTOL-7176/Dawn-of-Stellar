"""
🗣️ Dawn of Stellar - 토글식 채팅 시스템
특정 키로 채팅창을 열고 닫을 수 있는 시스템

2025년 8월 10일 - 몰입형 AI 대화 시스템
"""

import time
import threading
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class ChatMode(Enum):
    """채팅 모드"""
    HIDDEN = "숨김"           # 채팅창 완전히 숨김
    NOTIFICATION = "알림"     # 새 메시지 알림만 표시
    VISIBLE = "표시"          # 채팅창 완전히 표시
    INPUT = "입력"           # 채팅 입력 모드

class MessageType(Enum):
    """메시지 타입"""
    PLAYER = "플레이어"
    AI_CHAT = "AI대화"
    AI_SUGGESTION = "AI제안"
    AI_INITIATIVE = "AI먼저말"
    SYSTEM = "시스템"
    COMBAT = "전투"
    EXPLORATION = "탐험"

@dataclass
class ChatMessage:
    """채팅 메시지"""
    sender: str
    content: str
    message_type: MessageType
    timestamp: float
    character_name: Optional[str] = None
    character_class: Optional[str] = None
    is_ai: bool = False

@dataclass
class ItemRequest:
    """아이템 요청 데이터 클래스"""
    requester_id: str
    requester_name: str
    item_name: str
    item_type: str
    reason: str
    timestamp: float
    is_approved: Optional[bool] = None
    approver_id: Optional[str] = None

class ToggleChatSystem:
    """토글식 채팅 시스템"""
    
    def __init__(self):
        self.mode = ChatMode.HIDDEN
        self.messages: List[ChatMessage] = []
        self.max_messages = 50
        self.unread_count = 0
        
        # AI 모드 체크 플래그
        self.ai_mode_enabled = False
        
        # 아이템 요청 시스템
        self.pending_requests: List[ItemRequest] = []
        self.request_timeout = 30.0  # 30초 타임아웃
        self.last_displayed = 0
        
        # 채팅 설정
        self.toggle_key = 'T'  # T키로 채팅 토글
        self.input_key = 'Enter'
        self.chat_height = 8   # 채팅창 높이 (줄 수)
        
        # AI 모드 감지
        self.ai_mode_enabled = False
        
        # AI 대화 설정
        self.ai_response_chance = 0.7    # AI가 응답할 확률
        self.ai_initiative_chance = 0.1  # AI가 먼저 말할 확률
        self.last_ai_initiative = 0
        self.ai_initiative_cooldown = 30  # 30초 쿨다운
        
        print("🗣️ 토글식 채팅 시스템 초기화 완료")
        print(f"   💡 '{self.toggle_key}' 키를 눌러 채팅창을 열고 닫을 수 있습니다")
        print(f"   ⚠️ AI 모드에서만 활성화됩니다")
    
    def check_ai_mode(self, game_state=None) -> bool:
        """AI 모드 활성화 여부 확인"""
        if not game_state:
            return self.ai_mode_enabled
        
        # AI 멀티플레이어 모드 체크
        if hasattr(game_state, 'multiplayer_integration') and game_state.multiplayer_integration:
            self.ai_mode_enabled = True
            return True
        
        # AI 게임 모드 체크
        if hasattr(game_state, 'ai_multiplayer_mode') and game_state.ai_multiplayer_mode:
            self.ai_mode_enabled = True
            return True
        
        # 클래식 AI 모드 체크
        if hasattr(game_state, 'ai_game_mode_enabled') and game_state.ai_game_mode_enabled:
            self.ai_mode_enabled = True
            return True
        
        self.ai_mode_enabled = False
        return False
    
    def set_ai_mode(self, enabled: bool):
        """AI 모드 수동 설정"""
        self.ai_mode_enabled = enabled
        
    def create_item_request(self, requester_id: str, requester_name: str, 
                          item_name: str, item_type: str, reason: str) -> ItemRequest:
        """아이템 요청 생성"""
        request = ItemRequest(
            requester_id=requester_id,
            requester_name=requester_name,
            item_name=item_name,
            item_type=item_type,
            reason=reason,
            timestamp=time.time()
        )
        
        self.pending_requests.append(request)
        
        # 채팅으로 요청 메시지 추가
        request_message = f"🤝 {requester_name}이(가) {item_name}을(를) 요청합니다: {reason}"
        self.add_message(
            sender="시스템",
            content=request_message,
            message_type=MessageType.SYSTEM,
            is_ai=True
        )
        
        return request
        
    def approve_item_request(self, request_id: int, approver_id: str) -> bool:
        """아이템 요청 승인"""
        if 0 <= request_id < len(self.pending_requests):
            request = self.pending_requests[request_id]
            request.is_approved = True
            request.approver_id = approver_id
            
            # 승인 메시지 추가
            approval_message = f"✅ {request.item_name} 요청이 승인되었습니다!"
            self.add_message(
                sender="시스템",
                content=approval_message,
                message_type=MessageType.SYSTEM,
                is_ai=True
            )
            
            # AI 학습 시스템에 승인 패턴 기록
            self._record_item_decision(request, True, approver_id)
            
            # 요청 목록에서 제거
            self.pending_requests.pop(request_id)
            return True
        return False
        
    def reject_item_request(self, request_id: int, reason: str = "") -> bool:
        """아이템 요청 거절"""
        if 0 <= request_id < len(self.pending_requests):
            request = self.pending_requests[request_id]
            request.is_approved = False
            
            # 거절 메시지 추가
            reject_message = f"❌ {request.item_name} 요청이 거절되었습니다"
            if reason:
                reject_message += f": {reason}"
            
            self.add_message(
                sender="시스템",
                content=reject_message,
                message_type=MessageType.SYSTEM,
                is_ai=True
            )
            
            # AI 학습 시스템에 거절 패턴 기록
            self._record_item_decision(request, False, reason)
            
            # 요청 목록에서 제거
            self.pending_requests.pop(request_id)
            return True
        return False
        
    def clean_expired_requests(self):
        """만료된 요청 제거"""
        current_time = time.time()
        expired_requests = []
        
        for i, request in enumerate(self.pending_requests):
            if current_time - request.timestamp > self.request_timeout:
                expired_requests.append(i)
                
                # 만료 메시지 추가
                expire_message = f"⏰ {request.item_name} 요청이 시간 초과로 만료되었습니다"
                self.add_message(
                    sender="시스템",
                    content=expire_message,
                    message_type=MessageType.SYSTEM,
                    is_ai=True
                )
        
        # 역순으로 제거 (인덱스 변경 방지)
        for i in reversed(expired_requests):
            self.pending_requests.pop(i)
            
    def get_pending_requests(self) -> List[str]:
        """대기 중인 요청 목록 반환"""
        self.clean_expired_requests()
        
        request_list = []
        for i, request in enumerate(self.pending_requests):
            remaining_time = int(self.request_timeout - (time.time() - request.timestamp))
            request_str = f"{i+1}. {request.requester_name}: {request.item_name} ({remaining_time}초 남음)"
            request_list.append(request_str)
            
        return request_list
    
    def check_ai_item_requests(self, game_state=None):
        """AI 아이템 요청 체크 및 처리"""
        if not self.check_ai_mode(game_state):
            return
            
        try:
            from game.ai_chat_system import should_ai_request_item, generate_ai_item_request
            
            # AI가 아이템을 요청할지 확률적으로 결정
            if should_ai_request_item(game_state):
                request_data = generate_ai_item_request(game_state)
                
                if request_data:
                    # 아이템 요청 생성
                    request = self.create_item_request(
                        requester_id=request_data["requester_id"],
                        requester_name=request_data["requester_name"],
                        item_name=request_data["item_name"],
                        item_type=request_data["item_type"],
                        reason=request_data["reason"]
                    )
                    
                    # AI 개성 메시지도 추가
                    self.add_message(
                        sender=request_data["requester_name"],
                        content=request_data["personality_message"],
                        message_type=MessageType.AI_SUGGESTION,
                        is_ai=True,
                        character_name=request_data["requester_name"]
                    )
                    
        except ImportError:
            pass  # AI 시스템이 없으면 무시
            
    def handle_item_request_command(self, command: str) -> Optional[str]:
        """아이템 요청 명령어 처리 (! 또는 / 명령어 모두 지원)"""
        # 슬래시 명령어 또는 느낌표 명령어 처리
        original_command = command.strip()
        
        # 슬래시 명령어를 느낌표 명령어로 변환
        if original_command.startswith('/'):
            command = '!' + original_command[1:]
        
        parts = command.lower().split()
        
        if len(parts) < 2:
            return self._show_item_command_help()
            
        try:
            if parts[0] in ["!요청승인", "!승인"]:
                request_id = int(parts[1]) - 1  # 1-based to 0-based
                if self.approve_item_request(request_id, "플레이어"):
                    return f"✅ 요청 {parts[1]}번이 승인되었습니다."
                else:
                    return f"❌ 요청 {parts[1]}번을 찾을 수 없습니다."
                    
            elif parts[0] in ["!요청거절", "!거절"]:
                request_id = int(parts[1]) - 1  # 1-based to 0-based
                reason = " ".join(parts[2:]) if len(parts) > 2 else ""
                if self.reject_item_request(request_id, reason):
                    return f"❌ 요청 {parts[1]}번이 거절되었습니다."
                else:
                    return f"❌ 요청 {parts[1]}번을 찾을 수 없습니다."
                    
            elif parts[0] in ["!요청목록", "!목록"]:
                requests = self.get_pending_requests()
                if requests:
                    return "📋 대기 중인 요청:\n" + "\n".join(requests)
                else:
                    return "📋 대기 중인 요청이 없습니다."
            
            elif parts[0] in ["!아이템요청", "!요청"]:
                # 플레이어가 직접 아이템 요청
                if len(parts) < 3:
                    return "📝 사용법: /요청 <아이템명> <이유...> 또는 !아이템요청 <아이템명> <이유...>"
                
                item_name = parts[1]
                reason = " ".join(parts[2:])
                
                request = self.create_item_request(
                    requester_id="플레이어",
                    requester_name="플레이어",
                    item_name=item_name,
                    item_type="기타",
                    reason=reason
                )
                
                return f"아이템 요청이 등록되었습니다: {item_name}"
            
            elif parts[0] == "!도움말" or parts[0] == "!help":
                return self._show_item_command_help()
                    
        except (ValueError, IndexError):
            return "올바른 숫자를 입력해주세요."
            
        return None
    
    def _show_item_command_help(self) -> str:
        """아이템 요청 명령어 도움말"""
        return """
🎒 아이템 요청 시스템 명령어:
📝 요청하기:
• /요청 <아이템명> <이유>  또는  !아이템요청 <아이템명> <이유>  - 아이템 요청하기

📋 관리하기:
• /목록  또는  !요청목록                     - 대기 중인 요청 보기  
• /승인 <번호>  또는  !요청승인 <번호>       - 요청 승인하기
• /거절 <번호> [이유]  또는  !요청거절 <번호> [이유]  - 요청 거절하기

💡 도움말:
• /도움말  또는  !도움말                    - 이 도움말 보기

✨ 예시: 
• /요청 회복포션 체력이 부족해서 필요해요
• /승인 1
• /거절 2 지금은 여유가 없어서
"""
    
    def process_user_message(self, message: str, game_state=None) -> Optional[str]:
        """사용자 메시지 처리 (슬래시 명령어 및 느낌표 명령어 지원)"""
        if not message.strip():
            return None
            
        # 아이템 요청 명령어 체크 (슬래시 또는 느낌표)
        if message.startswith("/") or message.startswith("!"):
            # 도움말 명령어 처리
            if message.lower() in ["/도움말", "!도움말", "/help", "!help"]:
                return self._show_item_command_help()
            return self.handle_item_request_command(message)
        
        # 일반 채팅 메시지로 처리
        self.add_message(
            sender="플레이어",
            content=message,
            message_type=MessageType.PLAYER,
            is_ai=False
        )
        
        # AI 응답 생성
        try:
            from game.ai_chat_system import get_ai_response
            ai_response = get_ai_response(message, game_state)
            
            if ai_response:
                # AI 응답을 채팅에 추가
                self.add_message(
                    sender="AI",
                    content=ai_response,
                    message_type=MessageType.AI_CHAT,
                    is_ai=True
                )
                
        except ImportError:
            pass  # AI 시스템이 없으면 무시
            
        return "메시지가 전송되었습니다."
    
    def update(self, game_state=None):
        """주기적 업데이트 (게임 루프에서 호출)"""
        # AI 모드가 아니면 아무것도 하지 않음
        if not self.check_ai_mode(game_state):
            return
            
        # 만료된 요청 정리
        self.clean_expired_requests()
        
        # AI 아이템 요청 체크 (낮은 확률)
        self.check_ai_item_requests(game_state)
    
    def _record_item_decision(self, request: ItemRequest, approved: bool, decision_maker: str):
        """AI 학습 시스템에 아이템 결정 패턴 기록"""
        try:
            # AI 학습 시스템 연동
            from game.permanent_ai_learning_system import PermanentLearningDatabase
            from game.ultimate_ai_learning_system import UltimateAILearningSystem
            
            learning_data = {
                "timestamp": time.time(),
                "requester": request.requester_name,
                "item_name": request.item_name,
                "item_type": request.item_type,
                "reason": request.reason,
                "approved": approved,
                "decision_maker": decision_maker,
                "request_urgency": getattr(request, 'necessity_score', 0.5)
            }
            
            # 영구 학습 DB에 기록
            db = PermanentLearningDatabase()
            db.record_learning_event("item_request_decision", learning_data)
            
            print(f"📚 AI 학습: 아이템 요청 결정 패턴 기록됨 - {request.item_name} {'승인' if approved else '거절'}")
            
        except ImportError:
            pass  # 학습 시스템이 없으면 무지
        except Exception as e:
            print(f"⚠️ AI 학습 기록 오류: {e}")
    
    def add_message(self, sender: str, content: str, message_type: MessageType, 
                   character_name: str = None, character_class: str = None, is_ai: bool = False):
        """메시지 추가"""
        message = ChatMessage(
            sender=sender,
            content=content,
            message_type=message_type,
            timestamp=time.time(),
            character_name=character_name,
            character_class=character_class,
            is_ai=is_ai
        )
        
        self.messages.append(message)
        
        # 메시지 수 제한
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # 읽지 않은 메시지 카운트
        if self.mode == ChatMode.HIDDEN:
            self.unread_count += 1
    
    def toggle_chat(self) -> ChatMode:
        """채팅 모드 토글"""
        if self.mode == ChatMode.HIDDEN:
            self.mode = ChatMode.VISIBLE
            self.unread_count = 0  # 읽음 처리
        elif self.mode == ChatMode.VISIBLE:
            self.mode = ChatMode.HIDDEN
        elif self.mode == ChatMode.INPUT:
            self.mode = ChatMode.VISIBLE
        
        return self.mode
    
    def get_status_line(self) -> str:
        """상태 라인 반환 (항상 표시)"""
        if self.mode == ChatMode.HIDDEN:
            if self.unread_count > 0:
                return f"💬 새 메시지 {self.unread_count}개 (T키로 채팅 열기)"
            else:
                return f"💬 채팅 (T키로 열기)"
        elif self.mode == ChatMode.VISIBLE:
            return f"💬 채팅창 열림 (T키로 닫기, Enter로 입력)"
        elif self.mode == ChatMode.INPUT:
            return f"💬 메시지 입력 중... (ESC로 취소)"
        
        return ""


# 전역 채팅 시스템 인스턴스
_global_chat_system = None

def get_chat_system() -> ToggleChatSystem:
    """전역 채팅 시스템 가져오기"""
    global _global_chat_system
    if _global_chat_system is None:
        _global_chat_system = ToggleChatSystem()
    return _global_chat_system

def initialize_chat_system():
    """채팅 시스템 초기화"""
    global _global_chat_system
    _global_chat_system = ToggleChatSystem()
    return _global_chat_system
    
    def toggle_chat(self) -> ChatMode:
        """채팅 모드 토글"""
        if self.mode == ChatMode.HIDDEN:
            self.mode = ChatMode.VISIBLE
            self.unread_count = 0  # 읽음 처리
        elif self.mode == ChatMode.VISIBLE:
            self.mode = ChatMode.HIDDEN
        elif self.mode == ChatMode.INPUT:
            self.mode = ChatMode.VISIBLE
        
        return self.mode
    
    def enter_input_mode(self) -> bool:
        """채팅 입력 모드로 전환"""
        if self.mode == ChatMode.VISIBLE:
            self.mode = ChatMode.INPUT
            return True
        return False
    
    def exit_input_mode(self):
        """입력 모드 종료"""
        if self.mode == ChatMode.INPUT:
            self.mode = ChatMode.VISIBLE
    
    def add_message(self, sender: str, content: str, message_type: MessageType, 
                   character_name: str = None, character_class: str = None, is_ai: bool = False):
        """메시지 추가"""
        message = ChatMessage(
            sender=sender,
            content=content,
            message_type=message_type,
            timestamp=time.time(),
            character_name=character_name,
            character_class=character_class,
            is_ai=is_ai
        )
        
        self.messages.append(message)
        
        # 메시지 수 제한
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # 읽지 않은 메시지 카운트
        if self.mode == ChatMode.HIDDEN:
            self.unread_count += 1
    
    def get_status_line(self) -> str:
        """상태 라인 반환 (항상 표시)"""
        if self.mode == ChatMode.HIDDEN:
            if self.unread_count > 0:
                return f"💬 새 메시지 {self.unread_count}개 (T키로 채팅 열기)"
            else:
                return f"💬 채팅 (T키로 열기)"
        elif self.mode == ChatMode.VISIBLE:
            return f"💬 채팅창 열림 (T키로 닫기, Enter로 입력)"
        elif self.mode == ChatMode.INPUT:
            return f"💬 메시지 입력 중... (ESC로 취소)"
        
        return ""
    
    def render_chat_window(self) -> List[str]:
        """채팅창 렌더링"""
        if self.mode not in [ChatMode.VISIBLE, ChatMode.INPUT]:
            return []
        
        lines = []
        lines.append("=" * 60)
        lines.append("💬 파티 채팅")
        lines.append("-" * 60)
        
        # 최근 메시지들 표시
        recent_messages = self.messages[-self.chat_height:]
        
        for msg in recent_messages:
            timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M")
            
            # 메시지 타입별 아이콘
            if msg.message_type == MessageType.PLAYER:
                icon = "👤"
            elif msg.message_type == MessageType.AI_CHAT:
                icon = "🤖"
            elif msg.message_type == MessageType.AI_SUGGESTION:
                icon = "💡"
            elif msg.message_type == MessageType.AI_INITIATIVE:
                icon = "🗨️"
            elif msg.message_type == MessageType.SYSTEM:
                icon = "⚙️"
            else:
                icon = "📢"
            
            # 캐릭터 정보
            if msg.character_name:
                sender_info = f"{msg.character_name}"
                if msg.character_class:
                    sender_info += f"({msg.character_class})"
            else:
                sender_info = msg.sender
            
            # 메시지 포맷
            line = f"{timestamp} {icon} {sender_info}: {msg.content}"
            
            # 줄 길이 제한
            if len(line) > 58:
                line = line[:55] + "..."
            
            lines.append(line)
        
        # 빈 줄 채우기
        while len(lines) < self.chat_height + 3:
            lines.append("")
        
        if self.mode == ChatMode.INPUT:
            lines.append("💭 메시지 입력: ")
        else:
            lines.append("Enter키로 메시지 입력, T키로 닫기")
        
        lines.append("=" * 60)
        
        return lines
    
    def handle_input(self, key: str, game_state=None) -> Tuple[bool, Optional[str]]:
        """입력 처리"""
        # AI 모드가 아니면 채팅 시스템 비활성화
        if not self.check_ai_mode(game_state):
            return False, None
        
        if key.upper() == self.toggle_key:
            new_mode = self.toggle_chat()
            if new_mode == ChatMode.VISIBLE:
                # AI 능동적 대화 체크
                self.check_ai_initiative(game_state)
            return True, f"채팅창 {new_mode.value}"
        
        if self.mode == ChatMode.VISIBLE and key == '\n':  # Enter
            return True, "input_mode"
        
        if self.mode == ChatMode.INPUT and key == '\x1b':  # ESC
            self.exit_input_mode()
            return True, "입력 취소"
        
        return False, None
    
    def check_ai_initiative(self, game_state=None):
        """AI 능동적 대화 체크"""
        current_time = time.time()
        
        # 쿨다운 체크
        if current_time - self.last_ai_initiative < self.ai_initiative_cooldown:
            return
        
        # 확률 체크
        import random
        if random.random() > self.ai_initiative_chance:
            return
        
        # AI가 먼저 말하기
        self.trigger_ai_initiative(game_state)
        self.last_ai_initiative = current_time
    
    def trigger_ai_initiative(self, game_state=None):
        """AI 능동적 대화 실행"""
        try:
            from game.ai_chat_system import get_ai_initiative_message
            
            # 게임 상황에 따른 AI 메시지 생성
            ai_message = get_ai_initiative_message(game_state)
            
            if ai_message:
                # 랜덤한 AI 캐릭터가 말하기
                ai_characters = ["로바트", "알파", "베타", "감마"]
                import random
                speaker = random.choice(ai_characters)
                
                self.add_message(
                    sender=speaker,
                    content=ai_message,
                    message_type=MessageType.AI_INITIATIVE,
                    character_name=speaker,
                    character_class="AI 어시스턴트",
                    is_ai=True
                )
                
        except ImportError:
            # AI 시스템이 없으면 기본 메시지
            basic_messages = [
                "혹시 도움이 필요하신가요?",
                "전투 전략을 상의해볼까요?",
                "현재 상황이 어떤 것 같으신지요?",
                "제가 뭔가 도울 수 있을까요?"
            ]
            import random
            message = random.choice(basic_messages)
            
            self.add_message(
                sender="로바트",
                content=message,
                message_type=MessageType.AI_INITIATIVE,
                character_name="로바트",
                character_class="AI 어시스턴트",
                is_ai=True
            )
    
    def process_user_message(self, user_message: str, game_state=None):
        """사용자 메시지 처리 및 AI 응답"""
        # 사용자 메시지 추가
        self.add_message(
            sender="플레이어",
            content=user_message,
            message_type=MessageType.PLAYER,
            character_name="모험가",
            is_ai=False
        )
        
        # AI 응답 생성
        self.generate_ai_response(user_message, game_state)
    
    def generate_ai_response(self, user_message: str, game_state=None):
        """AI 응답 생성"""
        import random
        
        # 응답 확률 체크
        if random.random() > self.ai_response_chance:
            return
        
        try:
            from game.ai_chat_system import get_ai_response
            ai_response = get_ai_response(user_message, game_state)
        except ImportError:
            # 기본 패턴 매칭 응답
            ai_response = self.get_basic_ai_response(user_message)
        
        if ai_response:
            # 응답할 AI 캐릭터 선택
            ai_characters = [
                ("로바트", "전투 전문가"),
                ("알파", "전략 분석가"), 
                ("베타", "아이템 전문가"),
                ("감마", "탐험 가이드")
            ]
            
            speaker, role = random.choice(ai_characters)
            
            self.add_message(
                sender=speaker,
                content=ai_response,
                message_type=MessageType.AI_CHAT,
                character_name=speaker,
                character_class=role,
                is_ai=True
            )
    
    def get_basic_ai_response(self, user_message: str) -> str:
        """기본 AI 응답 (언어모델 없을 때)"""
        import random
        
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['안녕', '안녕하세요', 'hello', 'hi']):
            responses = [
                "안녕하세요! 로바트가 도와드리겠습니다!",
                "반갑습니다! 오늘도 함께 모험해요!",
                "안녕하세요! 좋은 하루네요!"
            ]
        elif any(word in message_lower for word in ['도움', 'help', '도와', '도와줘']):
            responses = [
                "무엇을 도와드릴까요? 전투, 탐험, 아이템 관리 모두 가능해요!",
                "언제든 말씀하세요! 저희가 도와드릴게요!",
                "어떤 도움이 필요하신가요? 구체적으로 말씀해주세요!"
            ]
        elif any(word in message_lower for word in ['전투', '싸움', 'combat', 'fight']):
            responses = [
                "전투 전략을 짜볼까요? 적의 약점을 파악하는 게 중요해요!",
                "저희가 전투에서 도와드릴게요! 팀워크가 승리의 열쇠죠!",
                "전투 준비는 완료! 언제든 명령하세요!"
            ]
        elif any(word in message_lower for word in ['아이템', 'item', '장비', '무기']):
            responses = [
                "아이템 관리를 도와드릴까요? 최적의 장비 조합을 찾아드려요!",
                "좋은 아이템을 발견했다면 공유해주세요!",
                "장비 업그레이드가 필요하시다면 알려주세요!"
            ]
        else:
            responses = [
                "흥미로운 이야기네요! 더 자세히 들려주세요!",
                "그렇군요! 저도 그렇게 생각해요!",
                "좋은 생각이에요! 함께 해봐요!",
                "네, 알겠습니다! 계속 진행해볼까요?",
                "그 방법도 좋을 것 같아요!"
            ]
        
        return random.choice(responses)


# 전역 채팅 시스템 인스턴스
_chat_system = None

def get_chat_system() -> ToggleChatSystem:
    """전역 채팅 시스템 가져오기"""
    global _chat_system
    if _chat_system is None:
        _chat_system = ToggleChatSystem()
    return _chat_system

def reset_chat_system():
    """채팅 시스템 리셋"""
    global _chat_system
    _chat_system = None
