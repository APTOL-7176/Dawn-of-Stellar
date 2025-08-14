"""
멀티플레이어 리더십 시스템
탐험 모드에서 리더 관리 및 양도 기능
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from game.color_text import GREEN, YELLOW, RED, CYAN, WHITE, RESET
from game.cursor_menu_system import CursorMenu
from game.error_logger import log_system, log_player


class LeadershipStatus(Enum):
    """리더십 상태"""
    LEADER = "leader"           # 현재 리더 (탐험 조작 권한)
    MEMBER = "member"           # 일반 멤버 (관전/채팅)
    HOST = "host"              # 방장 (영구 권한)
    SPECTATOR = "spectator"     # 관전자


@dataclass
class LeadershipRequest:
    """리더십 요청 데이터"""
    requester_id: str
    requester_name: str
    request_time: float
    reason: str = ""
    votes_for: List[str] = None
    votes_against: List[str] = None
    
    def __post_init__(self):
        if self.votes_for is None:
            self.votes_for = []
        if self.votes_against is None:
            self.votes_against = []


class MultiplayerLeadershipSystem:
    """멀티플레이어 리더십 관리 시스템"""
    
    def __init__(self, session):
        self.session = session
        self.current_leader_id: Optional[str] = None
        self.host_id: Optional[str] = None
        self.player_status: Dict[str, LeadershipStatus] = {}
        
        # 리더십 요청 관리
        self.pending_request: Optional[LeadershipRequest] = None
        self.vote_timeout = 30.0  # 30초 투표 시간
        self.leadership_cooldown = 60.0  # 1분 쿨다운
        self.last_leadership_change = 0
        
        # 리더 권한 설정
        self.leader_permissions = {
            "move_party": True,        # 파티 이동
            "interact_objects": True,  # 오브젝트 상호작용
            "enter_dungeon": True,     # 던전 진입
            "use_items": True,         # 아이템 사용 (공용)
            "manage_inventory": True,  # 인벤토리 관리
            "make_decisions": True     # 중요 결정
        }
        
        log_system("리더십시스템", "멀티플레이어 리더십 시스템 초기화 완료")
    
    def initialize_leadership(self, host_id: str, players: List[Dict[str, Any]]):
        """리더십 시스템 초기화"""
        self.host_id = host_id
        self.current_leader_id = host_id  # 방장이 기본 리더
        
        # 플레이어 상태 설정
        for player in players:
            player_id = player.get('player_id', '')
            if player_id == host_id:
                self.player_status[player_id] = LeadershipStatus.HOST
            else:
                self.player_status[player_id] = LeadershipStatus.MEMBER
        
        log_system("리더십시스템", f"리더십 초기화: 호스트={host_id}, 플레이어={len(players)}명")
        self.broadcast_leadership_update()
    
    def is_leader(self, player_id: str) -> bool:
        """플레이어가 현재 리더인지 확인"""
        return player_id == self.current_leader_id
    
    def is_host(self, player_id: str) -> bool:
        """플레이어가 호스트인지 확인"""
        return player_id == self.host_id
    
    def can_request_leadership(self, player_id: str) -> Tuple[bool, str]:
        """리더십 요청 가능 여부 확인"""
        if player_id == self.current_leader_id:
            return False, "이미 리더입니다"
        
        if self.pending_request is not None:
            return False, "다른 리더십 요청이 진행 중입니다"
        
        if time.time() - self.last_leadership_change < self.leadership_cooldown:
            remaining = self.leadership_cooldown - (time.time() - self.last_leadership_change)
            return False, f"리더십 변경 쿨다운 중 (남은 시간: {remaining:.0f}초)"
        
        return True, ""
    
    async def request_leadership(self, player_id: str, player_name: str, reason: str = "") -> bool:
        """리더십 요청"""
        can_request, error_msg = self.can_request_leadership(player_id)
        if not can_request:
            await self.send_error_to_player(player_id, error_msg)
            return False
        
        # 리더십 요청 생성
        self.pending_request = LeadershipRequest(
            requester_id=player_id,
            requester_name=player_name,
            request_time=time.time(),
            reason=reason
        )
        
        log_player("리더십요청", f"{player_name}이 리더십을 요청", {
            "요청자": player_name,
            "이유": reason,
            "현재리더": self.current_leader_id
        })
        
        # 모든 플레이어에게 투표 요청 브로드캐스트
        await self.broadcast_leadership_vote_request()
        
        # 투표 타이머 시작
        asyncio.create_task(self.leadership_vote_timer())
        
        return True
    
    async def cast_leadership_vote(self, voter_id: str, vote: bool) -> bool:
        """리더십 투표"""
        if self.pending_request is None:
            return False
        
        if voter_id == self.pending_request.requester_id:
            return False  # 요청자는 투표 불가
        
        # 중복 투표 방지
        if voter_id in self.pending_request.votes_for or voter_id in self.pending_request.votes_against:
            return False
        
        # 투표 기록
        if vote:
            self.pending_request.votes_for.append(voter_id)
        else:
            self.pending_request.votes_against.append(voter_id)
        
        log_player("리더십투표", f"{voter_id}가 투표", {
            "투표": "찬성" if vote else "반대",
            "요청자": self.pending_request.requester_name
        })
        
        # 투표 현황 브로드캐스트
        await self.broadcast_vote_status()
        
        # 모든 표가 모였는지 확인
        total_voters = len(self.player_status) - 1  # 요청자 제외
        total_votes = len(self.pending_request.votes_for) + len(self.pending_request.votes_against)
        
        if total_votes >= total_voters:
            await self.finalize_leadership_vote()
        
        return True
    
    async def finalize_leadership_vote(self):
        """리더십 투표 최종 처리"""
        if self.pending_request is None:
            return
        
        votes_for = len(self.pending_request.votes_for)
        votes_against = len(self.pending_request.votes_against)
        total_votes = votes_for + votes_against
        
        # 과반수 이상 찬성시 리더 변경
        leadership_changed = votes_for > (total_votes / 2)
        
        if leadership_changed:
            old_leader = self.current_leader_id
            self.current_leader_id = self.pending_request.requester_id
            self.last_leadership_change = time.time()
            
            # 상태 업데이트
            if old_leader in self.player_status:
                self.player_status[old_leader] = LeadershipStatus.MEMBER
            self.player_status[self.current_leader_id] = LeadershipStatus.LEADER
            
            log_system("리더십변경", f"리더십 변경: {old_leader} → {self.current_leader_id}")
            
            # 성공 메시지 브로드캐스트
            await self.broadcast_leadership_change_result(True, self.pending_request.requester_name)
        else:
            log_system("리더십투표", f"리더십 변경 거부: 찬성={votes_for}, 반대={votes_against}")
            
            # 실패 메시지 브로드캐스트
            await self.broadcast_leadership_change_result(False, self.pending_request.requester_name)
        
        # 요청 정리
        self.pending_request = None
        await self.broadcast_leadership_update()
    
    async def leadership_vote_timer(self):
        """리더십 투표 타이머"""
        await asyncio.sleep(self.vote_timeout)
        
        if self.pending_request is not None:
            log_system("리더십투표", "투표 시간 초과")
            
            # 시간 초과로 투표 종료
            await self.broadcast_vote_timeout()
            await self.finalize_leadership_vote()
    
    async def force_leadership_change(self, new_leader_id: str, reason: str = "Host override"):
        """호스트 권한으로 강제 리더 변경"""
        if self.current_leader_id == new_leader_id:
            return
        
        old_leader = self.current_leader_id
        self.current_leader_id = new_leader_id
        self.last_leadership_change = time.time()
        
        # 상태 업데이트
        if old_leader in self.player_status:
            self.player_status[old_leader] = LeadershipStatus.MEMBER
        self.player_status[new_leader_id] = LeadershipStatus.LEADER
        
        log_system("강제리더변경", f"호스트가 리더 변경: {old_leader} → {new_leader_id}, 이유: {reason}")
        
        # 진행 중인 투표 취소
        if self.pending_request is not None:
            self.pending_request = None
        
        await self.broadcast_leadership_update()
        await self.broadcast_force_leadership_change(new_leader_id, reason)
    
    def get_leadership_status(self) -> Dict[str, Any]:
        """현재 리더십 상태 반환"""
        return {
            "current_leader": self.current_leader_id,
            "host": self.host_id,
            "player_status": {pid: status.value for pid, status in self.player_status.items()},
            "pending_request": {
                "requester": self.pending_request.requester_name,
                "reason": self.pending_request.reason,
                "votes_for": len(self.pending_request.votes_for),
                "votes_against": len(self.pending_request.votes_against),
                "time_left": max(0, self.vote_timeout - (time.time() - self.pending_request.request_time))
            } if self.pending_request else None,
            "cooldown_remaining": max(0, self.leadership_cooldown - (time.time() - self.last_leadership_change))
        }
    
    # ===== 브로드캐스트 메서드들 =====
    
    async def broadcast_leadership_update(self):
        """리더십 상태 업데이트 브로드캐스트"""
        message = {
            "type": "leadership_update",
            "data": self.get_leadership_status()
        }
        await self.session.broadcast_to_all(message)
    
    async def broadcast_leadership_vote_request(self):
        """리더십 투표 요청 브로드캐스트"""
        if self.pending_request is None:
            return
        
        message = {
            "type": "leadership_vote_request",
            "data": {
                "requester": self.pending_request.requester_name,
                "reason": self.pending_request.reason,
                "timeout": self.vote_timeout
            }
        }
        await self.session.broadcast_to_all(message)
    
    async def broadcast_vote_status(self):
        """투표 현황 브로드캐스트"""
        if self.pending_request is None:
            return
        
        message = {
            "type": "vote_status_update",
            "data": {
                "votes_for": len(self.pending_request.votes_for),
                "votes_against": len(self.pending_request.votes_against),
                "total_voters": len(self.player_status) - 1
            }
        }
        await self.session.broadcast_to_all(message)
    
    async def broadcast_leadership_change_result(self, success: bool, requester_name: str):
        """리더십 변경 결과 브로드캐스트"""
        message = {
            "type": "leadership_change_result",
            "data": {
                "success": success,
                "new_leader": requester_name if success else None,
                "reason": "투표 통과" if success else "투표 부결"
            }
        }
        await self.session.broadcast_to_all(message)
    
    async def broadcast_vote_timeout(self):
        """투표 시간 초과 브로드캐스트"""
        message = {
            "type": "vote_timeout",
            "data": {"message": "리더십 투표 시간이 초과되었습니다"}
        }
        await self.session.broadcast_to_all(message)
    
    async def broadcast_force_leadership_change(self, new_leader_id: str, reason: str):
        """강제 리더십 변경 브로드캐스트"""
        message = {
            "type": "force_leadership_change",
            "data": {
                "new_leader": new_leader_id,
                "reason": reason
            }
        }
        await self.session.broadcast_to_all(message)
    
    async def send_error_to_player(self, player_id: str, error_msg: str):
        """특정 플레이어에게 오류 메시지 전송"""
        message = {
            "type": "leadership_error",
            "data": {"message": error_msg}
        }
        await self.session.send_to_player(player_id, message)


class LeadershipUI:
    """리더십 관련 UI 처리"""
    
    def __init__(self, leadership_system: MultiplayerLeadershipSystem):
        self.leadership = leadership_system
    
    def show_leadership_menu(self, player_id: str) -> Optional[str]:
        """리더십 메뉴 표시"""
        status = self.leadership.get_leadership_status()
        is_leader = self.leadership.is_leader(player_id)
        is_host = self.leadership.is_host(player_id)
        
        print(f"\n{CYAN}👑 리더십 관리{RESET}")
        print(f"{WHITE}현재 리더: {status['current_leader']}{RESET}")
        
        if status['pending_request']:
            req = status['pending_request']
            print(f"{YELLOW}📊 진행 중인 투표: {req['requester']}님의 리더십 요청{RESET}")
            print(f"   이유: {req['reason']}")
            print(f"   찬성: {req['votes_for']}표, 반대: {req['votes_against']}표")
            print(f"   남은 시간: {req['time_left']:.0f}초")
        
        if status['cooldown_remaining'] > 0:
            print(f"{RED}⏰ 리더십 변경 쿨다운: {status['cooldown_remaining']:.0f}초{RESET}")
        
        options = []
        actions = []
        
        if not is_leader and status['pending_request'] is None and status['cooldown_remaining'] <= 0:
            options.append("👑 리더십 요청")
            actions.append("request_leadership")
        
        if status['pending_request'] and not self.leadership.is_leader(player_id):
            options.append("✅ 찬성 투표")
            options.append("❌ 반대 투표") 
            actions.extend(["vote_yes", "vote_no"])
        
        if is_host:
            options.append("⚡ 강제 리더 변경")
            actions.append("force_change")
        
        options.append("❌ 돌아가기")
        actions.append("back")
        
        if len(options) == 1:  # 돌아가기만 있는 경우
            input(f"{YELLOW}현재 사용 가능한 옵션이 없습니다. Enter를 눌러 돌아가세요...{RESET}")
            return None
        
        menu = CursorMenu("👑 리더십 관리", options, cancellable=True)
        result = menu.run()
        
        if result is None or result == len(actions) - 1:
            return None
        
        return actions[result]
    
    def get_leadership_request_reason(self) -> str:
        """리더십 요청 이유 입력"""
        print(f"\n{CYAN}📝 리더십 요청 이유를 입력하세요 (선택사항):{RESET}")
        print(f"{YELLOW}> {RESET}", end="")
        
        reason = input().strip()
        return reason if reason else "리더 교체 요청"
    
    def show_vote_notification(self, requester_name: str, reason: str):
        """투표 알림 표시"""
        print(f"\n{CYAN}🗳️  리더십 투표 알림{RESET}")
        print(f"{WHITE}{requester_name}님이 리더십을 요청했습니다{RESET}")
        print(f"이유: {reason}")
        print(f"{YELLOW}리더십 메뉴에서 투표해주세요!{RESET}")
    
    def show_leadership_change_result(self, success: bool, new_leader: str):
        """리더십 변경 결과 표시"""
        if success:
            print(f"\n{GREEN}👑 리더십이 {new_leader}님으로 변경되었습니다!{RESET}")
        else:
            print(f"\n{RED}📊 리더십 변경이 거부되었습니다{RESET}")


def get_multiplayer_leadership_system(session):
    """멀티플레이어 리더십 시스템 인스턴스 반환"""
    return MultiplayerLeadershipSystem(session)
