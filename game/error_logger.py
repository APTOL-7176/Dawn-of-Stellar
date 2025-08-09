"""
🔧 완전체 로그 시스템
게임의 모든 활동을 세션별로 한글 파일명에 저장
"""

import os
import datetime
import traceback
import threading
import json
from typing import Optional, Dict, Any
from pathlib import Path

class ComprehensiveLogger:
    """완전체 로그 관리자 - 모든 게임 활동 기록"""
    
    def __init__(self):
        # 세션 시작 시간
        self.session_start = datetime.datetime.now()
        
        # 로그 폴더 생성
        self.log_dir = Path("게임로그")
        self.log_dir.mkdir(exist_ok=True)
        
        # 세션별 파일명 생성 (한글)
        session_time = self.session_start.strftime("%Y년%m월%d일_%H시%M분%S초")
        self.session_prefix = f"{session_time}_세션"
        
        # 다양한 로그 파일들
        self.log_files = {
            "all": self.log_dir / f"{self.session_prefix}_전체로그.log",
            "error": self.log_dir / f"{self.session_prefix}_오류로그.log", 
            "enemy": self.log_dir / f"{self.session_prefix}_적로그.log",
            "combat": self.log_dir / f"{self.session_prefix}_전투로그.log",
            "player": self.log_dir / f"{self.session_prefix}_플레이어로그.log",
            "world": self.log_dir / f"{self.session_prefix}_월드로그.log",
            "debug": self.log_dir / f"{self.session_prefix}_디버그로그.log",
            "system": self.log_dir / f"{self.session_prefix}_시스템로그.log"
        }
        
        # 스레드 안전을 위한 락
        self.lock = threading.Lock()
        
        # 세션 정보 기록
        self._log_session_start()
    
    def _log_session_start(self):
        """세션 시작 정보 기록"""
        session_info = {
            "세션시작": self.session_start.isoformat(),
            "게임버전": "Dawn of Stellar v2.2.0", 
            "로그폴더": str(self.log_dir),
            "로그파일들": {name: str(path) for name, path in self.log_files.items()}
        }
        
        start_message = f"""
{'='*80}
🌟 게임 세션 시작 - {self.session_start.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}
{'='*80}
세션 ID: {self.session_prefix}
로그 폴더: {self.log_dir}
{'='*80}
"""
        
        # 모든 로그 파일에 세션 시작 기록
        for file_path in self.log_files.values():
            self._write_to_file(file_path, start_message)
        
        # 세션 정보 JSON 파일도 생성
        session_info_file = self.log_dir / f"{self.session_prefix}_세션정보.json"
        with open(session_info_file, "w", encoding="utf-8") as f:
            json.dump(session_info, f, ensure_ascii=False, indent=2)
    
    def _write_to_file(self, file_path: Path, content: str):
        """파일에 안전하게 쓰기"""
        try:
            with self.lock:
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(content)
                    f.flush()  # 즉시 디스크에 쓰기
        except Exception as e:
            # 로그 쓰기 실패해도 게임은 계속 진행
            print(f"⚠️ 로그 쓰기 실패: {e}")
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 가져오기"""
        return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]  # 밀리초까지
    
    def _format_log_entry(self, category: str, level: str, message: str, 
                         exception: Optional[Exception] = None, extra_data: Dict[str, Any] = None) -> str:
        """로그 엔트리 포맷팅"""
        timestamp = self._get_timestamp()
        
        # 기본 로그 엔트리
        entry = f"[{timestamp}] [{level}] [{category}] {message}"
        
        # 예외 정보 추가
        if exception:
            entry += f"\n  └─ 예외: {type(exception).__name__}: {str(exception)}"
            if hasattr(exception, '__traceback__') and exception.__traceback__:
                try:
                    tb_lines = traceback.format_tb(exception.__traceback__)
                    if tb_lines:
                        entry += f"\n  └─ 위치: {''.join(tb_lines[-1:])}"
                except:
                    pass
        
        # 추가 데이터
        if extra_data:
            for key, value in extra_data.items():
                entry += f"\n  └─ {key}: {value}"
        
        entry += "\n"
        return entry
    
    def log(self, category: str, level: str, message: str, 
            exception: Optional[Exception] = None, extra_data: Dict[str, Any] = None,
            file_types: list = ["all"]):
        """통합 로그 기록"""
        entry = self._format_log_entry(category, level, message, exception, extra_data)
        
        # 지정된 파일들에 기록
        for file_type in file_types:
            if file_type in self.log_files:
                self._write_to_file(self.log_files[file_type], entry)
    
    # === 전투 관련 로그 ===
    def log_combat_start(self, party_info: Dict, enemy_info: Dict):
        """전투 시작 로그"""
        extra_data = {
            "파티정보": party_info,
            "적정보": enemy_info
        }
        self.log("전투", "정보", "전투 시작", extra_data=extra_data, 
                file_types=["all", "combat"])
    
    def log_combat_action(self, character_name: str, action: str, target: str = "", result: str = ""):
        """전투 행동 로그"""
        message = f"{character_name}이(가) {action}"
        if target:
            message += f" → {target}"
        if result:
            message += f" (결과: {result})"
        
        self.log("전투행동", "정보", message, file_types=["all", "combat"])
    
    def log_combat_damage(self, attacker: str, target: str, damage: int, damage_type: str):
        """전투 피해 로그"""
        extra_data = {
            "공격자": attacker,
            "대상": target, 
            "피해량": damage,
            "피해타입": damage_type
        }
        self.log("피해", "정보", f"{attacker} → {target}: {damage} {damage_type} 피해", 
                extra_data=extra_data, file_types=["all", "combat"])
    
    def log_combat_end(self, result: str, rewards: Dict = None):
        """전투 종료 로그"""
        extra_data = {"결과": result}
        if rewards:
            extra_data["보상"] = rewards
        self.log("전투", "정보", f"전투 종료: {result}", extra_data=extra_data,
                file_types=["all", "combat"])
    
    # === 적 관련 로그 ===
    def log_enemy_generation(self, position: tuple, enemy_type: str, level: int):
        """적 생성 로그"""
        extra_data = {
            "위치": position,
            "타입": enemy_type,
            "레벨": level
        }
        self.log("적생성", "정보", f"적 생성: {enemy_type} Lv.{level} @ {position}", 
                extra_data=extra_data, file_types=["all", "enemy"])
    
    def log_enemy_movement(self, old_pos: tuple, new_pos: tuple, enemy_type: str, reason: str):
        """적 이동 로그"""
        extra_data = {
            "이전위치": old_pos,
            "새위치": new_pos,
            "적타입": enemy_type,
            "이동이유": reason
        }
        self.log("적이동", "정보", f"{enemy_type} 이동: {old_pos} → {new_pos} ({reason})",
                extra_data=extra_data, file_types=["all", "enemy"])
    
    def log_enemy_ai_decision(self, enemy_name: str, decision: str, reasoning: str):
        """적 AI 결정 로그"""
        extra_data = {
            "적이름": enemy_name,
            "결정": decision,
            "이유": reasoning
        }
        self.log("적AI", "정보", f"{enemy_name} AI 결정: {decision} (이유: {reasoning})",
                extra_data=extra_data, file_types=["all", "enemy", "debug"])
    
    # === 플레이어 관련 로그 ===
    def log_player_action(self, action: str, details: Dict = None):
        """플레이어 행동 로그"""
        self.log("플레이어", "정보", f"플레이어 행동: {action}", extra_data=details,
                file_types=["all", "player"])
    
    def log_player_movement(self, old_pos: tuple, new_pos: tuple, floor: int):
        """플레이어 이동 로그"""
        extra_data = {
            "이전위치": old_pos,
            "새위치": new_pos,
            "층수": floor
        }
        self.log("플레이어이동", "정보", f"플레이어 이동: {old_pos} → {new_pos} (층 {floor})",
                extra_data=extra_data, file_types=["all", "player"])
    
    def log_player_interaction(self, target: str, interaction_type: str, result: str):
        """플레이어 상호작용 로그"""
        extra_data = {
            "대상": target,
            "상호작용타입": interaction_type,
            "결과": result
        }
        self.log("플레이어상호작용", "정보", f"상호작용: {target} ({interaction_type}) → {result}",
                extra_data=extra_data, file_types=["all", "player"])
    
    # === 월드 관련 로그 ===
    def log_world_generation(self, floor: int, size: tuple, room_count: int, enemy_count: int):
        """월드 생성 로그"""
        extra_data = {
            "층수": floor,
            "맵크기": size,
            "방수": room_count,
            "적수": enemy_count
        }
        self.log("월드생성", "정보", f"층 {floor} 생성: {size[0]}x{size[1]}, 방 {room_count}개, 적 {enemy_count}마리",
                extra_data=extra_data, file_types=["all", "world"])
    
    def log_world_event(self, event_type: str, description: str, location: tuple = None):
        """월드 이벤트 로그"""
        extra_data = {"이벤트타입": event_type}
        if location:
            extra_data["위치"] = location
        self.log("월드이벤트", "정보", f"{event_type}: {description}",
                extra_data=extra_data, file_types=["all", "world"])
    
    # === 시스템 관련 로그 ===
    def log_system_info(self, component: str, message: str, data: Dict = None):
        """시스템 정보 로그"""
        self.log(f"시스템/{component}", "정보", message, extra_data=data,
                file_types=["all", "system"])
    
    def log_performance(self, operation: str, duration: float, details: Dict = None):
        """성능 로그"""
        extra_data = {"작업": operation, "소요시간": f"{duration:.3f}초"}
        if details:
            extra_data.update(details)
        self.log("성능", "정보", f"{operation} 완료: {duration:.3f}초",
                extra_data=extra_data, file_types=["all", "system"])
    
    # === 오류 로그 ===
    def log_error(self, category: str, message: str, exception: Optional[Exception] = None, 
                  show_in_game: bool = False, data: Dict = None):
        """오류 로그"""
        self.log(category, "오류", message, exception=exception, extra_data=data,
                file_types=["all", "error"])
        
        if show_in_game:
            print(f"⚠️ {category}: {message}")
    
    def log_warning(self, category: str, message: str, data: Dict = None):
        """경고 로그"""
        self.log(category, "경고", message, extra_data=data,
                file_types=["all", "debug"])
    
    def log_debug(self, category: str, message: str, data: Dict = None):
        """디버그 로그"""
        self.log(category, "디버그", message, extra_data=data,
                file_types=["all", "debug"])
    
    def log_system_warning(self, category: str, message: str, data: Dict = None):
        """시스템 경고 로그"""
        self.log(f"시스템/{category}", "경고", message, extra_data=data,
                file_types=["all", "system", "debug"])
    
    def log_ai_mode_debug(self, message: str, data: Dict = None):
        """AI 모드 디버그 로그"""
        self.log("AI_MODE_DEBUG", "디버그", message, extra_data=data,
                file_types=["all", "debug"])
    
    # === ATB 관련 로그 ===
    def log_atb_update(self, character_name: str, old_atb: int, new_atb: int, reason: str):
        """ATB 업데이트 로그"""
        extra_data = {
            "캐릭터": character_name,
            "이전ATB": old_atb,
            "새ATB": new_atb,
            "이유": reason
        }
        self.log("ATB", "정보", f"{character_name} ATB: {old_atb} → {new_atb} ({reason})",
                extra_data=extra_data, file_types=["all", "combat", "debug"])
    
    def log_atb_initialization(self, character_name: str, initial_atb: int, speed: int):
        """ATB 초기화 로그"""
        extra_data = {
            "캐릭터": character_name,
            "초기ATB": initial_atb,
            "속도": speed
        }
        self.log("ATB초기화", "정보", f"{character_name} ATB 초기화: {initial_atb} (속도: {speed})",
                extra_data=extra_data, file_types=["all", "combat", "debug"])
    
    def close_session(self):
        """세션 종료 로그"""
        session_end = datetime.datetime.now()
        duration = session_end - self.session_start
        
        end_message = f"""
{'='*80}
🌟 게임 세션 종료 - {session_end.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}
세션 지속 시간: {duration}
{'='*80}
"""
        
        # 모든 로그 파일에 세션 종료 기록
        for file_path in self.log_files.values():
            self._write_to_file(file_path, end_message)


# 전역 로거 인스턴스
_comprehensive_logger = None

def get_comprehensive_logger() -> ComprehensiveLogger:
    """완전체 로거 인스턴스 가져오기"""
    global _comprehensive_logger
    if _comprehensive_logger is None:
        _comprehensive_logger = ComprehensiveLogger()
    return _comprehensive_logger

# === 편의 함수들 ===
def log_combat_start(party_info: Dict, enemy_info: Dict):
    get_comprehensive_logger().log_combat_start(party_info, enemy_info)

def log_combat_action(character_name: str, action: str, target: str = "", result: str = ""):
    get_comprehensive_logger().log_combat_action(character_name, action, target, result)

def log_combat_damage(attacker: str, target: str, damage: int, damage_type: str):
    get_comprehensive_logger().log_combat_damage(attacker, target, damage, damage_type)

def log_enemy_generation(position: tuple, enemy_type: str, level: int):
    get_comprehensive_logger().log_enemy_generation(position, enemy_type, level)

def log_enemy_movement(old_pos: tuple, new_pos: tuple, enemy_type: str, reason: str):
    get_comprehensive_logger().log_enemy_movement(old_pos, new_pos, enemy_type, reason)

def log_player_action(action: str, details: Dict = None):
    get_comprehensive_logger().log_player_action(action, details)

def log_player_movement(old_pos: tuple, new_pos: tuple, floor: int):
    get_comprehensive_logger().log_player_movement(old_pos, new_pos, floor)

def log_world_generation(floor: int, size: tuple, room_count: int, enemy_count: int):
    get_comprehensive_logger().log_world_generation(floor, size, room_count, enemy_count)

def log_atb_update(character_name: str, old_atb: int, new_atb: int, reason: str):
    get_comprehensive_logger().log_atb_update(character_name, old_atb, new_atb, reason)

def log_atb_initialization(character_name: str, initial_atb: int, speed: int):
    get_comprehensive_logger().log_atb_initialization(character_name, initial_atb, speed)

def log_error(category: str, message: str, exception: Optional[Exception] = None, 
              show_in_game: bool = False, data: Dict = None):
    get_comprehensive_logger().log_error(category, message, exception, show_in_game, data)

def log_debug(category: str, message: str, data: Dict = None):
    get_comprehensive_logger().log_debug(category, message, data)

# 새로운 카테고리별 로깅 함수들 (2025.08.10 추가)
def log_enemy(category: str, message: str, data: Dict = None):
    """적 관련 로그 기록"""
    logger = get_comprehensive_logger()
    logger.log(category, "정보", message, extra_data=data, file_types=["all", "enemy"])

def log_player(category: str, message: str, data: Dict = None):
    """플레이어 관련 로그 기록"""
    logger = get_comprehensive_logger()
    logger.log(category, "정보", message, extra_data=data, file_types=["all", "player"])

def log_world(category: str, message: str, data: Dict = None):
    """월드 관련 로그 기록"""
    logger = get_comprehensive_logger()
    logger.log(category, "정보", message, extra_data=data, file_types=["all", "world"])

def log_combat(category: str, message: str, data: Dict = None):
    """전투 관련 로그 기록"""
    logger = get_comprehensive_logger()
    logger.log(category, "정보", message, extra_data=data, file_types=["all", "combat"])

def log_system(category: str, message: str, data: Dict = None):
    """시스템 관련 로그 기록"""
    logger = get_comprehensive_logger()
    logger.log(category, "정보", message, extra_data=data, file_types=["all", "system"])

# 하위 호환성을 위한 기존 함수들
def get_error_logger():
    """기존 코드 호환성을 위한 함수 - 완전체 로거 반환"""
    return get_comprehensive_logger()

def log_critical_error(message: str, details: dict = None):
    """치명적 오류 로깅 - 기존 호환성"""
    get_comprehensive_logger().log_error("치명적오류", message, None, True, details or {})

def log_menu_error(message: str, details: dict = None):
    """메뉴 오류 로깅"""
    get_comprehensive_logger().log_error("메뉴오류", message, None, False, details or {})

def log_effect_error(message: str, details: dict = None):
    """효과 오류 로깅"""
    get_comprehensive_logger().log_error("효과오류", message, None, False, details or {})

def log_combat_error(message: str, details: dict = None):
    """전투 오류 로깅"""
    get_comprehensive_logger().log_error("전투오류", message, None, False, details or {})

def setup_error_logging():
    """오류 로깅 설정 - 기존 호환성"""
    pass  # 완전체 로거는 자동으로 설정됨

def get_recent_errors(count: int = 5) -> list:
    """최근 오류들을 가져오기"""
    try:
        import os
        from pathlib import Path
        
        # 최신 오류 로그 파일 찾기
        log_dir = Path("게임로그")
        if not log_dir.exists():
            return []
        
        # 오류 로그 파일들 찾기
        error_files = list(log_dir.glob("*_오류로그.log"))
        if not error_files:
            return []
        
        # 가장 최신 파일 선택
        latest_error_file = max(error_files, key=lambda x: x.stat().st_mtime)
        
        errors = []
        try:
            with open(latest_error_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # 오류 메시지만 추출 (타임스탬프가 있는 라인)
                for line in lines:
                    if "[오류]" in line or "[ERROR]" in line:
                        errors.append(line.strip())
                        if len(errors) >= count:
                            break
        except:
            pass
        
        return errors[-count:] if errors else []
    except:
        return []

def get_session_logs() -> dict:
    """현재 세션의 로그 파일 경로들 반환"""
    try:
        logger = get_comprehensive_logger()
        return {name: str(path) for name, path in logger.log_files.items()}
    except:
        return {}

# 전역 완전체 로거 인스턴스 (호환성)
logger = get_comprehensive_logger()
