"""
자동 저장 시스템
게임 진행 중 중요한 이벤트에서 자동으로 저장
"""
import time
import threading
from typing import Optional, List
from enum import Enum

class AutoSaveEventType(Enum):
    """자동 저장 이벤트 타입"""
    FLOOR_CHANGE = "floor_change"      # 층 이동
    LEVEL_UP = "level_up"              # 레벨업
    BOSS_DEFEAT = "boss_defeat"        # 보스 처치
    RARE_ITEM_FOUND = "rare_item"      # 희귀 아이템 획득
    ACHIEVEMENT_UNLOCK = "achievement" # 업적 달성
    COMBAT_VICTORY = "combat_victory"  # 전투 승리
    PARTY_WIPE = "party_wipe"         # 파티 전멸
    MANUAL_REQUEST = "manual"         # 수동 요청

class AutoSaveManager:
    """자동 저장 매니저"""
    
    def __init__(self, game_instance=None):
        self.game_instance = game_instance
        self.enabled = True
        self.save_cooldown = 10.0  # 10초 쿨다운
        self.last_save_time = 0
        self.save_queue = []
        self.is_saving = False
        
        # 이벤트별 자동 저장 설정
        self.auto_save_events = {
            AutoSaveEventType.FLOOR_CHANGE: True,
            AutoSaveEventType.LEVEL_UP: True,
            AutoSaveEventType.BOSS_DEFEAT: True,
            AutoSaveEventType.RARE_ITEM_FOUND: False,  # 너무 자주 발생할 수 있음
            AutoSaveEventType.ACHIEVEMENT_UNLOCK: True,
            AutoSaveEventType.COMBAT_VICTORY: False,   # 너무 자주 발생
            AutoSaveEventType.PARTY_WIPE: True,
            AutoSaveEventType.MANUAL_REQUEST: True
        }
        
        self.save_history = []  # 최근 저장 기록
        
    def set_game_instance(self, game_instance):
        """게임 인스턴스 설정"""
        self.game_instance = game_instance
        
    def is_enabled_for_event(self, event_type: AutoSaveEventType) -> bool:
        """특정 이벤트에 대한 자동 저장 활성화 여부"""
        return self.enabled and self.auto_save_events.get(event_type, False)
        
    def can_save_now(self) -> bool:
        """지금 저장 가능한지 확인 (쿨다운 체크)"""
        current_time = time.time()
        return (current_time - self.last_save_time) >= self.save_cooldown
        
    def auto_save_on_event(self, event_type: AutoSaveEventType, event_data: dict = None):
        """이벤트 기반 자동 저장"""
        if not self.is_enabled_for_event(event_type):
            return False
            
        if self.is_saving:
            print("⏳ 이미 저장 중입니다...")
            return False
            
        if not self.can_save_now():
            remaining_cooldown = self.save_cooldown - (time.time() - self.last_save_time)
            print(f"⏰ 자동 저장 쿨다운 중... ({remaining_cooldown:.1f}초 남음)")
            return False
            
        return self._perform_auto_save(event_type, event_data)
        
    def _perform_auto_save(self, event_type: AutoSaveEventType, event_data: dict = None) -> bool:
        """실제 자동 저장 수행"""
        if not self.game_instance:
            print("❌ 게임 인스턴스가 설정되지 않았습니다.")
            return False
            
        self.is_saving = True
        
        try:
            # 이벤트별 메시지
            event_messages = {
                AutoSaveEventType.FLOOR_CHANGE: "🏢 층 이동으로 인한 자동 저장",
                AutoSaveEventType.LEVEL_UP: "⭐ 레벨업으로 인한 자동 저장",
                AutoSaveEventType.BOSS_DEFEAT: "👑 보스 처치로 인한 자동 저장",
                AutoSaveEventType.RARE_ITEM_FOUND: "💎 희귀 아이템 획득으로 인한 자동 저장",
                AutoSaveEventType.ACHIEVEMENT_UNLOCK: "🏆 업적 달성으로 인한 자동 저장",
                AutoSaveEventType.COMBAT_VICTORY: "⚔️ 전투 승리로 인한 자동 저장",
                AutoSaveEventType.PARTY_WIPE: "💀 파티 전멸로 인한 자동 저장",
                AutoSaveEventType.MANUAL_REQUEST: "🎮 수동 요청으로 인한 자동 저장"
            }
            
            message = event_messages.get(event_type, "💾 자동 저장")
            print(f"\n{message}...")
            
            # 게임 저장 실행
            success = False
            if hasattr(self.game_instance, 'save_game'):
                try:
                    self.game_instance.save_game()
                    success = True
                except Exception as save_error:
                    print(f"❌ 자동 저장 실패: {save_error}")
                    success = False
            else:
                print("❌ 저장 기능을 찾을 수 없습니다.")
                
            if success:
                self.last_save_time = time.time()
                self.save_history.append({
                    'timestamp': time.time(),
                    'event_type': event_type.value,
                    'event_data': event_data or {},
                    'success': True
                })
                print("✅ 자동 저장 완료!")
                return True
            else:
                self.save_history.append({
                    'timestamp': time.time(),
                    'event_type': event_type.value,
                    'event_data': event_data or {},
                    'success': False
                })
                return False
                
        except Exception as e:
            print(f"❌ 자동 저장 중 오류 발생: {e}")
            return False
        finally:
            self.is_saving = False
            
    def force_save(self, reason: str = "강제 저장"):
        """쿨다운 무시하고 강제 저장"""
        print(f"\n🚨 {reason}...")
        old_cooldown = self.save_cooldown
        self.save_cooldown = 0  # 쿨다운 임시 제거
        
        result = self.auto_save_on_event(AutoSaveEventType.MANUAL_REQUEST, {'reason': reason})
        
        self.save_cooldown = old_cooldown  # 쿨다운 복원
        return result
        
    def configure_auto_save(self, event_type: AutoSaveEventType, enabled: bool):
        """특정 이벤트 타입의 자동 저장 설정"""
        self.auto_save_events[event_type] = enabled
        status = "활성화" if enabled else "비활성화"
        print(f"⚙️ {event_type.value} 자동 저장이 {status}되었습니다.")
        
    def get_save_history(self, limit: int = 10) -> List[dict]:
        """최근 저장 기록 조회"""
        return self.save_history[-limit:] if self.save_history else []
        
    def show_auto_save_status(self):
        """자동 저장 상태 표시"""
        print(f"\n💾 자동 저장 상태")
        print(f"  전체 활성화: {'🟢 ON' if self.enabled else '🔴 OFF'}")
        print(f"  저장 쿨다운: {self.save_cooldown}초")
        print(f"  마지막 저장: {time.time() - self.last_save_time:.1f}초 전")
        print(f"\n📋 이벤트별 설정:")
        
        for event_type, enabled in self.auto_save_events.items():
            status = "🟢 ON" if enabled else "🔴 OFF"
            event_name = {
                AutoSaveEventType.FLOOR_CHANGE: "층 이동",
                AutoSaveEventType.LEVEL_UP: "레벨업",
                AutoSaveEventType.BOSS_DEFEAT: "보스 처치",
                AutoSaveEventType.RARE_ITEM_FOUND: "희귀 아이템",
                AutoSaveEventType.ACHIEVEMENT_UNLOCK: "업적 달성",
                AutoSaveEventType.COMBAT_VICTORY: "전투 승리",
                AutoSaveEventType.PARTY_WIPE: "파티 전멸",
                AutoSaveEventType.MANUAL_REQUEST: "수동 요청"
            }.get(event_type, event_type.value)
            
            print(f"    {event_name}: {status}")
            
        # 최근 저장 기록
        recent_saves = self.get_save_history(5)
        if recent_saves:
            print(f"\n📜 최근 저장 기록:")
            for save_record in recent_saves:
                timestamp = save_record['timestamp']
                event_type = save_record['event_type']
                success = save_record['success']
                status_icon = "✅" if success else "❌"
                time_ago = time.time() - timestamp
                print(f"    {status_icon} {event_type} ({time_ago:.1f}초 전)")

# 전역 자동 저장 매니저 인스턴스
auto_save_manager = AutoSaveManager()

# 편의 함수들
def trigger_auto_save(event_type: AutoSaveEventType, event_data: dict = None):
    """자동 저장 트리거"""
    return auto_save_manager.auto_save_on_event(event_type, event_data)

def on_floor_change(floor_number: int):
    """층 변경 시 자동 저장"""
    return trigger_auto_save(AutoSaveEventType.FLOOR_CHANGE, {'floor': floor_number})

# 레벨업 배치 처리를 위한 변수
_levelup_batch_timer = None
_levelup_batch_characters = []

def on_level_up(character_name: str, new_level: int):
    """레벨업 시 자동 저장 (배치 처리)"""
    global _levelup_batch_timer, _levelup_batch_characters
    
    # 캐릭터 정보 추가
    _levelup_batch_characters.append({'character': character_name, 'level': new_level})
    
    # 기존 타이머가 있으면 취소
    if _levelup_batch_timer:
        import threading
        _levelup_batch_timer.cancel()
    
    # 1초 후에 배치 저장 실행
    import threading
    def batch_save():
        global _levelup_batch_characters
        if _levelup_batch_characters:
            # 모든 레벨업 정보를 포함하여 한 번만 저장
            trigger_auto_save(AutoSaveEventType.LEVEL_UP, {
                'characters': _levelup_batch_characters.copy(),
                'count': len(_levelup_batch_characters)
            })
            _levelup_batch_characters.clear()
    
    _levelup_batch_timer = threading.Timer(1.0, batch_save)
    _levelup_batch_timer.start()
    
    return True  # 항상 성공으로 반환 (실제 저장은 배치에서)

def on_boss_defeat(boss_name: str):
    """보스 처치 시 자동 저장"""
    return trigger_auto_save(AutoSaveEventType.BOSS_DEFEAT, {'boss': boss_name})

def on_achievement_unlock(achievement_name: str):
    """업적 달성 시 자동 저장"""
    return trigger_auto_save(AutoSaveEventType.ACHIEVEMENT_UNLOCK, {'achievement': achievement_name})

def on_party_wipe():
    """파티 전멸 시 자동 저장"""
    return trigger_auto_save(AutoSaveEventType.PARTY_WIPE)

def configure_auto_save_system(game_instance):
    """자동 저장 시스템 설정"""
    auto_save_manager.set_game_instance(game_instance)
    return auto_save_manager
