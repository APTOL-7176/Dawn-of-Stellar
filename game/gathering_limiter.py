"""
채집 제한 시스템 - 균형적인 게임플레이를 위한 제한 추가
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class GatheringLimiter:
    """채집 제한 관리자"""
    step_cooldown: int = 450  # 채집 후 450걸음 대기
    
    # 상태 관리
    last_gathering_step: int = -450  # 마지막 채집한 걸음 수 (처음엔 바로 채집 가능)
    party_manager = None  # 파티 매니저 참조
    cooldown_notified: bool = False  # 쿨다운 완료 알림 여부
    
    def __post_init__(self):
        """초기화"""
        pass
    
    def set_party_manager(self, party_manager):
        """파티 매니저 설정"""
        self.party_manager = party_manager
    
    def get_current_steps(self) -> int:
        """현재 걸음 수 반환"""
        if self.party_manager and hasattr(self.party_manager, 'total_steps'):
            return self.party_manager.total_steps
        return 0
    
    def can_gather(self, location_name: str) -> tuple[bool, str]:
        """채집 가능 여부 확인 (걸음 기반)"""
        current_steps = self.get_current_steps()
        steps_since_last = current_steps - self.last_gathering_step
        
        if steps_since_last < self.step_cooldown:
            remaining_steps = self.step_cooldown - steps_since_last
            return False, f"채집 쿨다운: {remaining_steps}걸음 더 이동해야 합니다"
        
        return True, "채집 가능"
    
    def record_gathering(self, location_name: str):
        """채집 기록"""
        current_steps = self.get_current_steps()
        self.last_gathering_step = current_steps
        self.cooldown_notified = False  # 다음 쿨다운 알림을 위해 리셋
    
    def check_and_notify_cooldown_end(self) -> bool:
        """쿨다운 종료 확인 및 알림 (게임 루프에서 호출)"""
        current_steps = self.get_current_steps()
        steps_since_last = current_steps - self.last_gathering_step
        
        # 쿨다운이 끝났고 아직 알림하지 않았다면
        if (steps_since_last >= self.step_cooldown and 
            not self.cooldown_notified and 
            self.last_gathering_step > -450):  # 실제로 채집한 적이 있다면
            
            self.cooldown_notified = True
            self._show_gathering_available_notification()
            return True
        
        return False
    
    def _show_gathering_available_notification(self):
        """채집 가능 알림 표시"""
        print(f"\n{'='*60}")
        print(f"🌿✨ 채집 가능 알림 ✨🌿")
        print(f"{'='*60}")
        print(f"🎉 걸음을 충분히 걸어서 다시 채집할 수 있습니다!")
        print(f"🌍 숲속, 강가, 동굴, 고원에서 새로운 재료를 찾아보세요.")
        print(f"🍳 필드 메뉴에서 [4. 채집하기]를 선택하세요!")
        print(f"{'='*60}")
        
        try:
            input("📢 아무 키나 눌러서 계속...")
        except:
            pass
    
    def get_status(self) -> Dict[str, any]:
        """현재 상태 반환"""
        current_steps = self.get_current_steps()
        steps_since_last = current_steps - self.last_gathering_step
        
        status = {
            "current_steps": current_steps,
            "last_gathering_step": self.last_gathering_step,
            "steps_since_last": steps_since_last,
            "cooldown_remaining_steps": max(0, self.step_cooldown - steps_since_last)
        }
        
        return status

# 전역 채집 제한 관리자
gathering_limiter = GatheringLimiter()

def get_gathering_limiter() -> GatheringLimiter:
    """채집 제한 관리자 반환"""
    return gathering_limiter

def can_gather_at_location(location_name: str) -> tuple[bool, str]:
    """특정 장소에서 채집 가능한지 확인"""
    return gathering_limiter.can_gather(location_name)

def record_gathering_attempt(location_name: str):
    """채집 시도 기록"""
    gathering_limiter.record_gathering(location_name)

def get_gathering_status() -> Dict[str, any]:
    """채집 상태 정보 반환"""
    return gathering_limiter.get_status()

def reset_gathering_limits():
    """채집 제한 초기화 (치트/테스트용)"""
    gathering_limiter.last_gathering_step = -450

def set_party_manager_for_gathering(party_manager):
    """파티 매니저를 채집 시스템에 연결"""
    gathering_limiter.set_party_manager(party_manager)

def check_gathering_cooldown_notification():
    """채집 쿨다운 알림 확인 (게임 루프에서 호출)"""
    return gathering_limiter.check_and_notify_cooldown_end()
