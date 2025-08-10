"""
🔥 Brave 시스템이 통합된 전투 시스템 - 특성 효과 및 밸런스 시스템 통합
"""

from typing import List, Optional, Tuple
import random
import time
from .character import Character, StatusEffect
from .new_skill_system import StatusType
from .error_logger import log_debug, log_error, log_combat  # 로깅 함수 추가

from .brave_system import BraveManager, BraveAttackType, BattleEffects, BraveSkill
from .ffvii_sound_system import get_ffvii_sound_system
from .new_skill_system import get_status_icon, skill_system
from .ascii_effects import enhanced_battle_effect, combat_animator
from .input_utils import KeyboardInput, UnifiedInputManager
from .trait_combat_integration import trait_integrator  # 특성 연동 모듈
from .optimized_gauge_system import OptimizedGaugeSystem
from .color_text import Color
from .ui_animations import get_gauge_animator  # 게이지 애니메이션
from .aggro_system import get_aggro_system, create_damage_aggro, create_healing_aggro, create_taunt_aggro, create_debuff_aggro, AggroType  # 어그로 시스템

# 안전한 색상 상수 정의 - 직접 ANSI 코드 사용
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'DIM': '\033[2m',
    'UNDERLINE': '\033[4m',
    # 기본 색상
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    # 밝은 색상
    'BRIGHT_BLACK': '\033[90m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_YELLOW': '\033[93m',
    'BRIGHT_BLUE': '\033[94m',
    'BRIGHT_MAGENTA': '\033[95m',
    'BRIGHT_CYAN': '\033[96m',
    'BRIGHT_WHITE': '\033[97m',
    # 배경색
    'BG_BLACK': '\033[40m',
    'BG_RED': '\033[41m',
    'BG_GREEN': '\033[42m',
    'BG_YELLOW': '\033[43m',
    'BG_BLUE': '\033[44m',
    'BG_MAGENTA': '\033[45m',
    'BG_CYAN': '\033[46m',
    'BG_WHITE': '\033[47m'
}

def get_color(color_name):
    """안전한 색상 코드 반환"""
    return COLORS.get(color_name, '')
from .error_logger import log_menu_error, log_effect_error, log_combat_error, log_critical_error  # 오류 로그 시스템
# from .buffered_display import BufferedDisplay  # 사용 중단 - 직접 출력으로 대체

# 선택적 애니메이션 시스템 import
try:
    from .ui_animations import show_animated_healing, show_status_change_animation
    from .ui_animations import get_gauge_animator
    UI_ANIMATIONS_AVAILABLE = True
except ImportError:
    UI_ANIMATIONS_AVAILABLE = False
    def show_animated_healing(name, amount): pass  # 더미 함수
    def get_gauge_animator(): return None  # 더미 함수

# 선택적 display 시스템들 import (댓글로 보존)
try:
    from .combat_visual import get_combat_visualizer, EffectType  # 전투 시각 효과 담당 (EffectType 포함)
    COMBAT_VISUAL_AVAILABLE = True
except ImportError:
    COMBAT_VISUAL_AVAILABLE = False
    def get_combat_visualizer(): return None
    # EffectType 더미 클래스
    class EffectType:
        SKILL = "skill"
        PHYSICAL_ATTACK = "physical"
        CRITICAL = "critical"
        HEAL = "heal"
        DEFEND = "defend"
        SPECIAL = "special"  # 추가됨

try:
    from .stable_display import get_stable_display  # 안정적인 출력 담당
    STABLE_DISPLAY_AVAILABLE = True
except ImportError:
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from stable_display import stable_display
        STABLE_DISPLAY_AVAILABLE = True
    except ImportError:
        STABLE_DISPLAY_AVAILABLE = False
        stable_display = None

try:
    from .ui_system import GameDisplay  # 추가 UI 시스템
    GAME_DISPLAY_AVAILABLE = True
except ImportError:
    GAME_DISPLAY_AVAILABLE = False
    class GameDisplay: 
        def __init__(self): pass
        def __getattr__(self, name): return lambda *args, **kwargs: None

# time 모듈을 time_module로 별칭 설정 (전역에서 일관되게 사용)
time_module = time

# 🔥 강화된 시스템들 import
try:
    from .trait_integration_system import get_trait_processor, apply_trait_effects_to_damage, apply_trait_effects_to_defense
    from .relative_balance_system import get_balance_system, calculate_balanced_damage
    from .cursor_menu_system import create_simple_menu  # 커서 메뉴 시스템 전역 import
    from .unified_damage_system import get_damage_system, set_debug_mode
    ENHANCED_SYSTEMS_AVAILABLE = True
    CURSOR_MENU_AVAILABLE = True
except ImportError:
    ENHANCED_SYSTEMS_AVAILABLE = False
    CURSOR_MENU_AVAILABLE = False
    # 더미 함수 제공
    def create_simple_menu(*args, **kwargs):
        class DummyMenu:
            def run(self): return None
        return DummyMenu()

# BGM 타입 import 시도
try:
    from .audio_system import BGMType, get_audio_manager
except ImportError:
    BGMType = None
    get_audio_manager = None

# 🌑 그림자 시스템 import
try:
    from .shadow_system import get_shadow_system
    SHADOW_SYSTEM_AVAILABLE = True
except ImportError:
    SHADOW_SYSTEM_AVAILABLE = False

# 🛡️ 전사 적응형 시스템 import
try:
    from .warrior_system import get_warrior_system
    WARRIOR_SYSTEM_AVAILABLE = True
except ImportError:
    WARRIOR_SYSTEM_AVAILABLE = False


class BraveCombatSystem:
    """Brave 기반 전투 시스템"""
    
    # ATB 시스템 상수 (10배 확장)
    ATB_MAX = 2000  # 100 → 2000 (20배, 오버차지 허용)
    ATB_READY_THRESHOLD = 1000  # 100% → 1000
    ATB_DISPLAY_SCALE = 10  # 표시용 스케일 (1000 → 100으로 변환)
    BASE_ATB_INCREASE = 15  # ⚡ 원래대로 복원 (60 → 15)
    
    def __init__(self, audio_system=None, sound_manager=None):
        self.brave_manager = BraveManager()
        self.visualizer = get_combat_visualizer()
        self.stable_display = get_stable_display()  # 안정적인 출력 시스템 추가
        self.display = GameDisplay()  # GameDisplay 객체 추가
        # self.buffered_display = BufferedDisplay()  # 사용 중단 - 직접 출력으로 대체
        self.turn_order = []
        self.keyboard = KeyboardInput()  # 키보드 입력 처리
        self.current_turn = 0
        
        # 특성 통합 시스템 초기화
        from .trait_combat_integration import TraitCombatIntegrator
        self.trait_integrator = TraitCombatIntegrator()
        
        # 🔥 강화된 시스템들 초기화
        if ENHANCED_SYSTEMS_AVAILABLE:
            self.trait_processor = get_trait_processor()
            self.balance_system = get_balance_system()
            print("🔥 전투 시스템: 강화된 특성 및 밸런스 시스템 활성화!")
        else:
            self.trait_processor = None
            self.balance_system = None
            print("⚠️ 전투 시스템: 기본 모드로 실행 (강화 기능 비활성화)")
        
        # 오디오 시스템
        self.audio_system = audio_system
        self.sound_manager = sound_manager
        
        # 스킬 시스템 초기화 (skill_db 오류 수정)
        self.skill_db = skill_system
        
        # 애니메이션 시스템 - 더 부드럽고 빠르게
        self.animation_duration = 0.8  # 0.8초 애니메이션 (1.5→0.8초로 단축)
        self.animation_fps = 120  # 120 FPS로 매우 부드럽게 (60→120 FPS)
        
        # 게이지 애니메이터 설정
        from .ui_animations import get_gauge_animator
        self.gauge_animator = get_gauge_animator()
        self.gauge_animator.set_combat_mode(True)  # 전투 시작 시 전투 모드 활성화
        
        # 전투 로그 시스템 초기화
        self._recent_combat_logs = []
        self._turn_count = 0
        self._last_action_completed = False
        
        # 진동 시스템 초기화
        self.input_manager = UnifiedInputManager()
        self.vibration_enabled = True  # 진동 기본 활성화
        
        # 트레이닝 모드 설정
        self.training_mode = False  # 트레이닝 모드 플래그
        self.auto_battle_enabled = False  # 자동전투 비활성화
        self.log_delay = 0.3  # 기본 로그 대기 시간 단축 (1.0→0.3초)
        self.animation_active = False
        
        # 자동 전투 모드
        self.auto_battle = False
        self.auto_battle_delay = 1.0  # 자동 전투 시 1.0초 딜레이 (로그 확인 시간 확보)
        
        # AI 게임 모드 플래그 추가
        self.ai_game_mode = False  # AI 게임 모드 여부
        
        # 플레이어 턴 중 플래그 추가 (ATB 시스템용)
        self.is_player_turn_active = False  # 플레이어 턴이 진행 중인지
        self.is_action_executing = False    # 행동(스킬, 공격 등)이 실행 중인지
        
        # ATB 시간 정지 시스템 (파티 상태창용)
        self.atb_paused = False             # ATB 시간 정지 상태
        self.pause_reason = ""              # 정지 이유 (디버그용)
        
        # 🌑 그림자 시스템 초기화 (__init__에서 초기화)
        if SHADOW_SYSTEM_AVAILABLE:
            self.shadow_system = get_shadow_system()
            print("🌑 그림자 시스템 활성화! (암살자 전용)")
        else:
            self.shadow_system = None
            
        # 🎯 동적 어그로 시스템 초기화
        self.aggro_system = get_aggro_system()
        print("🎯 동적 어그로 시스템 활성화! (현실적인 AI 타겟팅)")
        
        # 🧠 AI 개성 시스템 초기화
        self._initialize_ai_personalities()
            
        # 취소 스팸 완화: 캐릭터별 취소 카운터/타임스탬프 초기화
        self._cancel_counters = {}
        self._cancel_last_time = {}
        self._cancel_cooldown_until = {}
        
        # 디버그 모드 설정 (환경변수나 설정으로 제어 가능)
        self.debug_mode = False  # 기본값: False (조용한 모드)
        
    def _debug_print(self, message: str):
        """디버그 모드에서만 출력"""
        if getattr(self, 'debug_mode', False):
            print(message)
        
    def is_ai_game_mode_enabled(self) -> bool:
        """클래식 게임모드 활성화 여부 확인 (안전한 체크)"""
        try:
            # 1. 클래스 내부 플래그 확인 (최우선)
            if hasattr(self, 'ai_game_mode'):
                # 명시적으로 False인 경우 확실히 비활성화
                if self.ai_game_mode is False:
                    return False
                return bool(self.ai_game_mode)
            
            # 2. AI 매니저 확인 (신뢰할 수 있는 소스) - 제한적으로만 사용
            try:
                from game.ai_game_mode import ai_game_mode_manager
                if hasattr(ai_game_mode_manager, 'is_enabled'):
                    # AI 매니저가 명시적으로 비활성화된 경우만 체크
                    if hasattr(ai_game_mode_manager, '_enabled') and ai_game_mode_manager._enabled is False:
                        return False
            except ImportError:
                pass
            
            # 3. 메인 모듈 확인 비활성화 (false positive 방지)
            # try:
            #     import sys
            #     main_module = sys.modules.get('__main__')
            #     if main_module and hasattr(main_module, 'ai_game_mode_enabled'):
            #         return bool(main_module.ai_game_mode_enabled)
            # except Exception:
            #     pass
                
            # 기본값: AI 모드 비활성화 (보수적 접근)
            return False
        except Exception:
            # 오류 발생 시 안전하게 수동 모드
            return False
    
    def set_ai_game_mode(self, enabled: bool):
        """클래식 게임모드 활성화/비활성화 설정"""
        self.ai_game_mode = enabled
        from .error_logger import get_error_logger
        logger = get_error_logger()
        logger.log_debug("AI모드설정", f"클래식 게임모드: {'활성화' if enabled else '비활성화'}")
        
        # 🌑 그림자 시스템 초기화
        if SHADOW_SYSTEM_AVAILABLE:
            self.shadow_system = get_shadow_system()
            print("🌑 그림자 시스템 활성화! (암살자 전용)")
        else:
            self.shadow_system = None
            
        # 전투 로그 시스템 초기화
        self._recent_combat_logs = []
        self._max_log_entries = 10  # 최대 로그 저장 개수
        self._turn_count = 0  # 턴 카운터
        self._last_action_completed = False  # 액션 완료 플래그
        
        # 취소 스팸 완화: 캐릭터별 취소 카운터/타임스탬프
        self._cancel_counters = {}
        self._cancel_last_time = {}
        
        # 취소 후 즉시 재선택을 막는 쿨다운 타이머 (character id -> timestamp)
        self._cancel_cooldown_until = {}    # 🎯 적 아이콘 시스템 초기화
        self.enemy_icons = {
            # 동물 몬스터
            "쥐": "🐭", "고양이": "🐱", "개": "🐕", "늑대": "🐺", "곰": "🐻", 
            "토끼": "🐰", "여우": "🦊", "사자": "🦁", "호랑이": "🐯", "표범": "🐆",
            "원숭이": "🐵", "고릴라": "🦍", "코끼리": "🐘", "코뿔소": "🦏",
            
            # 환상 생물
            "드래곤": "🐉", "용": "🐲", "유니콘": "🦄", "피닉스": "🔥", "그리핀": "🦅",
            "히드라": "🐍", "크라켄": "🐙", "밴시": "👻", "리치": "💀", "바실리스크": "🐍",
            
            # 언데드
            "해골": "💀", "좀비": "🧟", "뱀파이어": "🧛", "스펙터": "👻", "망령": "🌫️",
            "그림 리퍼": "⚰️", "데스나이트": "⚔️", "리치": "🔮", "밴시": "😱",
            
            # 정령/원소
            "화염정령": "🔥", "물정령": "💧", "바람정령": "💨", "땅정령": "🌍",
            "얼음정령": "❄️", "번개정령": "⚡", "빛정령": "✨", "어둠정령": "🌑",
            
            # 악마/데몬
            "임프": "👿", "데몬": "😈", "마왕": "👹", "발록": "🔥", "서큐버스": "💋",
            "인큐버스": "😏", "데빌": "😈", "사탄": "👺", "루시퍼": "😠",
            
            # 거인족
            "오크": "🗡️", "트롤": "🔨", "오거": "💪", "사이클롭스": "👁️", "타이탄": "⛰️",
            "거인": "👨‍🦲", "골렘": "🗿", "미노타우르스": "🐂", "센타우르": "🏹",
            
            # 곤충/거미
            "거미": "🕷️", "전갈": "🦂", "벌": "🐝", "개미": "🐜", "메뚜기": "🦗",
            "나비": "🦋", "잠자리": "🪲", "딱정벌레": "🪲", "바퀴벌레": "🪳",
            
            # 바다 생물
            "상어": "🦈", "문어": "🐙", "오징어": "🦑", "가오리": "🪼", "고래": "🐋",
            "돌고래": "🐬", "바다뱀": "🐍", "크랩": "🦀", "바닷가재": "🦞",
            
            # 파충류
            "뱀": "🐍", "도마뱀": "🦎", "이구아나": "🦎", "카멜레온": "🦎", "게코": "🦎",
            "악어": "🐊", "거북이": "🐢", "바실리스크": "🐲", "와이번": "🐉",
            
            # 조류
            "독수리": "🦅", "매": "🪶", "올빼미": "🦉", "까마귀": "🐦‍⬛", "펭귄": "🐧",
            "타조": "🪶", "플라밍고": "🦩", "공작": "🦚", "펠리컨": "🪿",
            
            # 기타
            "슬라임": "🟢", "미믹": "📦", "보물상자": "💎", "수정": "💎",
            "기계": "🤖", "로봇": "🦾", "사이보그": "🔧", "AI": "💻"
        }
    
    def set_ai_game_mode(self, enabled: bool):
        """AI 게임 모드 설정"""
        self.ai_game_mode = enabled
        if enabled:
            from .error_logger import get_error_logger
            logger = get_error_logger()
            logger.log_debug("AI 게임 모드 활성화 - 자동 진행")
        else:
            from .error_logger import get_error_logger
            logger = get_error_logger()
            logger.log_debug("수동 모드 활성화 - 키 입력 필요")
    
    def pause_atb(self, reason: str = "파티 상태창"):
        """ATB 시간 정지 (불릿타임 무시)"""
        self.atb_paused = True
        self.pause_reason = reason
        log_debug("ATB 정지", f"ATB 시간 정지됨: {reason}")
    
    def resume_atb(self):
        """ATB 시간 재개"""
        if self.atb_paused:
            log_debug("ATB 재개", f"ATB 시간 재개됨 (이전 정지 이유: {self.pause_reason})")
            self.atb_paused = False
            self.pause_reason = ""
    
    def is_atb_paused(self) -> bool:
        """ATB 정지 상태 확인"""
        return self.atb_paused
    
    def add_combat_log(self, message: str):
        """전투 로그 추가"""
        self._recent_combat_logs.append(message)
        if len(self._recent_combat_logs) > self._max_log_entries:
            self._recent_combat_logs.pop(0)  # 오래된 로그 제거
    
    def _wait_for_user_input_or_timeout(self, seconds: float, message: str = None):
        """사용자 입력 대기 또는 타임아웃 - 개선된 버전"""
        import sys
        import select
        import time as time_module
        
        # 입력 버퍼 클리어
        try:
            self.keyboard.clear_input_buffer()
        except:
            pass
        
        if message:
            print(f"\n{message}")
        else:
            print(f"\n⏳ {seconds}초 후 자동으로 계속되거나 Enter를 눌러 즉시 계속...")
        
        # Windows에서는 간단한 방법 사용
        if sys.platform == 'win32':
            import msvcrt
            start_time = time_module.time()
            while time_module.time() - start_time < seconds:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key in [b'\r', b'\n']:  # Enter 키
                        # 남은 입력 제거
                        while msvcrt.kbhit():
                            msvcrt.getch()
                        return
                time_module.sleep(0.1)
        else:
            # Unix 계열에서는 select 사용
            start_time = time_module.time()
            while time_module.time() - start_time < seconds:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    # 키 버퍼 클리어 후 키 대기
                    self.keyboard.clear_input_buffer()
                    self.keyboard.wait_for_key()  # Enter 입력 소비
                    return
                time_module.sleep(0.1)
        
    def _play_menu_sfx(self, sfx_name: str):
        """메뉴 SFX 재생 함수"""
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx(sfx_name)
            elif hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.play_sfx(sfx_name)
            else:
                # audio_manager 가져오기 시도
                try:
                    from .audio_system import get_audio_manager
                    audio_manager = get_audio_manager()
                    if audio_manager:
                        audio_manager.play_sfx(sfx_name)
                except:
                    pass  # SFX 재생 실패 시 무시
        except Exception as e:
            pass  # SFX 재생 실패 시 무시
        
    def add_action_pause(self, message="", pause_duration=0.5):
        """액션 후 일시 정지 - 액션 결과를 읽을 시간 제공 (자동화)"""
        if message:
            print(f"\n{message}")
        # 액션 결과를 읽을 수 있도록 0.5초 대기 (2초에서 단축)
        import time
        time.sleep(pause_duration)
        
    def animate_value_change(self, character: Character, stat_type: str, old_value: int, new_value: int, party: List[Character], enemies: List[Character]):
        """수치 변화 애니메이션 (HP/MP/BRV) - 새로운 애니메이션 시스템 사용"""
        if old_value == new_value:
            return
            
        self.animation_active = True
        
        # 새로운 애니메이션 시스템 사용
        if stat_type.lower() == 'hp':
            # HP 값 설정 (자동 애니메이션 트리거)
            character.current_hp = new_value
            
            # 🔥 광전사 분노 시스템: 피해를 받으면 분노 증가
            if new_value < old_value and hasattr(character, 'character_class') and character.character_class == "광전사":
                damage_taken = old_value - new_value
                # 피해 추적 함수 사용 (외부 피해)
                try:
                    from .new_skill_system import track_berserker_damage
                    track_berserker_damage(character, damage_taken, is_self_damage=False)
                except ImportError:
                    # 기존 방식으로 폴백
                    if not hasattr(character, 'recent_damage_taken'):
                        character.recent_damage_taken = 0
                    character.recent_damage_taken += damage_taken
                    print(f"💢 {character.name}이(가) 피해를 받아 분노가 축적되고 있습니다... ({damage_taken} 피해)")
            
            # 데미지/회복에 따른 효과 표시 - unified_damage_system이 처리함
            if new_value < old_value:
                # 구버전 로그 제거 - unified_damage_system이 신버전 로그 출력
                pass
            elif new_value > old_value:
                healing = new_value - old_value
                show_animated_healing(character.name, healing)
                
                # 🔥 광전사 분노 감소 시스템: 회복받으면 회복량에 비례해서 분노 감소
                if hasattr(character, 'character_class') and character.character_class == "광전사":
                    if hasattr(character, 'rage_stacks') and character.rage_stacks > 0:
                        # 회복량의 15%만큼 분노 감소 (최소 1, 최대 현재 분노)
                        rage_decrease = max(1, min(character.rage_stacks, int(healing * 0.15)))
                        character.rage_stacks = max(0, character.rage_stacks - rage_decrease)
                        print(f"😌 {character.name}의 분노가 회복으로 인해 {rage_decrease}만큼 가라앉았습니다... (현재: {character.rage_stacks})")
                        
                        # 하위 호환성을 위한 기존 변수들도 업데이트
                        if hasattr(character, 'rage_meter'):
                            character.rage_meter = character.rage_stacks * 10
                        if hasattr(character, 'rage_count'):
                            character.rage_count = character.rage_stacks
                
        elif stat_type.lower() == 'mp':
            # MP 값 설정 (자동 애니메이션 트리거)
            character.current_mp = new_value
            
        elif stat_type.lower() == 'brv':
            # BRV 값 설정 (자동 애니메이션 트리거)
            character.brave_points = new_value
        
        # 애니메이션 완료 대기 (게이지 애니메이션이 끝날 때까지)
        time_module.sleep(0.5)
        self.animation_active = False
        
        # 게이지 애니메이션 완료 후 화면 업데이트
        self.show_battle_status(character, party, enemies)

    def create_precise_gauge(self, current: int, maximum: int, length: int = 20, empty_char: str = "▱", fill_char: str = "▰") -> str:
        """정밀한 게이지 생성 (픽셀 단위 정확도)"""
        if maximum <= 0:
            return empty_char * length
            
        # 정확한 비율 계산
        ratio = current / maximum
        
        # 채워진 블록 수 계산
        filled_blocks = ratio * length
        full_blocks = int(filled_blocks)
        
        # 부분적으로 채워진 블록 처리
        partial_block = filled_blocks - full_blocks
        
        # 게이지 생성
        gauge = ""
        
        # 완전히 채워진 블록들
        gauge += fill_char * full_blocks
        
        # 부분적으로 채워진 블록 (7단계 그라데이션)
        if full_blocks < length and partial_block > 0:
            if partial_block >= 0.875:    # 87.5% 이상
                gauge += "▉"
            elif partial_block >= 0.75:   # 75% 이상
                gauge += "▊"  
            elif partial_block >= 0.625:  # 62.5% 이상
                gauge += "▋"
            elif partial_block >= 0.5:    # 50% 이상
                gauge += "▌"
            elif partial_block >= 0.375:  # 37.5% 이상
                gauge += "▍"
            elif partial_block >= 0.25:   # 25% 이상
                gauge += "▎"
            elif partial_block >= 0.125:  # 12.5% 이상
                gauge += "▏"
            else:
                gauge += empty_char
            
            # 나머지는 빈 블록으로 채움
            gauge += empty_char * (length - full_blocks - 1)
        else:
            # 나머지는 빈 블록으로 채움
            gauge += empty_char * (length - full_blocks)
            
        return gauge

    def create_beautiful_hp_gauge(self, current: int, maximum: int, length: int = 18) -> str:
        """단순한 HP 게이지 생성 (그라데이션 제거)"""
        if maximum <= 0:
            return " " * length
            
        # 정확한 비율 계산
        ratio = current / maximum
        filled_blocks = int(ratio * length)
        
        # HP 비율에 따른 단일 색상 결정
        if ratio >= 0.6:
            color = get_color('BRIGHT_GREEN')
        elif ratio >= 0.3:
            color = get_color('YELLOW')
        else:
            color = get_color('BRIGHT_RED')
        
        # 게이지 생성 (단순한 형태)
        gauge = f"{color}{'█' * filled_blocks}{get_color('RESET')}"
        gauge += " " * (length - filled_blocks)
        
        return gauge

    def create_beautiful_mp_gauge(self, current: int, maximum: int, length: int = 18) -> str:
        """단순한 MP 게이지 생성 (그라데이션 제거)"""
        if maximum <= 0:
            return " " * length
            
        # 정확한 비율 계산
        ratio = current / maximum
        filled_blocks = int(ratio * length)
        
        # MP는 파란색으로 고정
        color = get_color('BRIGHT_CYAN')
        
        # 게이지 생성 (단순한 형태)
        gauge = f"{color}{'█' * filled_blocks}{get_color('RESET')}"
        gauge += " " * (length - filled_blocks)
        
        return gauge


    def create_beautiful_brv_gauge(self, current: int, maximum: int, length: int = 18) -> str:
        """단순한 BRV 게이지 생성 (그라데이션 제거)"""
        if maximum <= 0:
            return " " * length
            
        # 정확한 비율 계산
        ratio = current / maximum
        filled_blocks = int(ratio * length)
        
        # BRV는 노란색으로 고정
        color = get_color('BRIGHT_YELLOW')
        
        # 게이지 생성 (단순한 형태)
        gauge = f"{color}{'█' * filled_blocks}{get_color('RESET')}"
        gauge += " " * (length - filled_blocks)
        
        return gauge

    def create_beautiful_atb_gauge(self, current: int, maximum: int, length: int = 18, is_casting: bool = False) -> str:
        """초고해상도 픽셀 ATB 게이지 생성 (8단계 픽셀 세분화)"""
        if maximum <= 0:
            return " " * length
            
        # 정확한 비율 계산 (0.0 ~ 1.0)
        ratio = max(0.0, min(1.0, current / maximum))
        
        # 전체 픽셀 수 계산 (길이 * 8 픽셀)
        total_pixels = length * 8
        filled_pixels = int(ratio * total_pixels)
        
        # 완전히 채워진 블록 수와 나머지 픽셀
        full_blocks = filled_pixels // 8
        remaining_pixels = filled_pixels % 8
        
        # 픽셀 문자들 (0픽셀부터 8픽셀까지)
        pixel_chars = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
        
        # 색상 설정
        if is_casting:
            # 캐스팅 중일 때는 마젠타 색상
            fill_color = get_color('BRIGHT_MAGENTA')
        else:
            # ATB는 시안색으로 고정
            fill_color = get_color('BRIGHT_CYAN')
        
        empty_color = get_color('BRIGHT_BLACK')  # 빈 부분은 어두운 회색
        
        # 게이지 구성
        gauge = ""
        
        # 완전히 채워진 블록들
        if full_blocks > 0:
            gauge += fill_color + '█' * full_blocks + get_color('RESET')
        
        # 부분적으로 채워진 블록
        if full_blocks < length and remaining_pixels > 0:
            gauge += fill_color + pixel_chars[remaining_pixels] + get_color('RESET')
            # 나머지 빈 블록들
            empty_blocks = length - full_blocks - 1
            if empty_blocks > 0:
                gauge += empty_color + '░' * empty_blocks + get_color('RESET')
        elif full_blocks < length:
            # 완전히 빈 블록들
            empty_blocks = length - full_blocks
            gauge += empty_color + '░' * empty_blocks + get_color('RESET')
        
        return gauge
        
    def __init_audio_diagnostic(self):
        """오디오 시스템 진단"""
        print(f"🎵 오디오 시스템 진단:")
        print(f"  - audio_system: {type(self.audio_system).__name__ if self.audio_system else 'None'}")
        print(f"  - sound_manager: {type(self.sound_manager).__name__ if self.sound_manager else 'None'}")
        
        # 스킬 시스템 이미 __init__에서 초기화됨
    
    def get_optimized_display(self):
        """최적화된 디스플레이 시스템 반환 (BufferedDisplay 대체)"""
        return None  # 직접 출력 사용
    
    def get_brave_color_emoji(self, brave_points: int) -> str:
        """Brave 포인트에 따른 통일된 이모지 반환"""
        return "⚡"  # 모든 Brave 포인트에 동일 이모지 사용
    
    def get_enemy_icon(self, enemy_name: str) -> str:
        """적 이름에 따른 고유 아이콘 반환"""
        # 적 이름에서 키워드 추출하여 매칭
        name_lower = enemy_name.lower()
        
        # 정확한 이름 매칭 우선
        for enemy_type, icon in self.enemy_icons.items():
            if enemy_type in enemy_name:
                return icon
        
        # 키워드 기반 매칭
        if any(keyword in name_lower for keyword in ["쥐", "rat", "mouse"]):
            return "🐭"
        elif any(keyword in name_lower for keyword in ["늑대", "wolf", "울프"]):
            return "🐺"
        elif any(keyword in name_lower for keyword in ["드래곤", "dragon", "용"]):
            return "🐉"
        elif any(keyword in name_lower for keyword in ["오크", "orc"]):
            return "🗡️"
        elif any(keyword in name_lower for keyword in ["해골", "skeleton", "스켈레톤"]):
            return "💀"
        elif any(keyword in name_lower for keyword in ["좀비", "zombie"]):
            return "🧟"
        elif any(keyword in name_lower for keyword in ["슬라임", "slime"]):
            return "🟢"
        elif any(keyword in name_lower for keyword in ["거미", "spider"]):
            return "🕷️"
        elif any(keyword in name_lower for keyword in ["고블린", "goblin"]):
            return "👹"
        elif any(keyword in name_lower for keyword in ["트롤", "troll"]):
            return "🔨"
        elif any(keyword in name_lower for keyword in ["마법사", "wizard", "mage"]):
            return "🧙"
        elif any(keyword in name_lower for keyword in ["기사", "knight"]):
            return "⚔️"
        elif any(keyword in name_lower for keyword in ["도적", "thief", "rogue"]):
            return "🗡️"
        elif any(keyword in name_lower for keyword in ["보스", "boss", "왕", "king", "마왕"]):
            return "👑"
        else:
            return "⚔️"  # 기본 아이콘
    
    def calculate_casting_progress_method4(self, character: Character) -> float:
        """캐스팅 진행률 계산 - 방법 4 (ATB 리셋 대응)"""
        if not hasattr(character, 'is_casting') or not character.is_casting:
            return 0.0
        
        if not hasattr(character, 'casting_duration') or character.casting_duration <= 0:
            return 0.0
            
        atb_gauge = getattr(character, 'atb_gauge', 0)
        casting_start_atb = getattr(character, 'casting_start_atb', 0)
        casting_duration = character.casting_duration
        
        # 방법 4: ATB 리셋 대응 계산
        if casting_start_atb > atb_gauge:
            # ATB가 리셋된 경우: 0부터 시작으로 가정
            progress = (atb_gauge / casting_duration)
        else:
            # 정상적인 ATB 증가: 시작점부터 계산
            atb_progress = atb_gauge - casting_start_atb
            progress = (atb_progress / casting_duration)
        
        # 0.0 ~ 1.0 범위로 제한
        return max(0.0, min(1.0, progress))
        
    def start_battle(self, party: List[Character], enemies: List[Character]):
        """전투 시작"""
        # 전투 상태 활성화
        from .character import set_combat_active
        set_combat_active(True)
        
        # 클래식 게임모드 상태 확인 및 표시
        ai_mode_enabled = self.is_ai_game_mode_enabled()
        from .error_logger import get_error_logger
        logger = get_error_logger()
        
        if ai_mode_enabled:
            logger.log_debug("클래식AI", "클래식 게임모드 활성화 - 일부 파티원이 클래식 AI로 제어될 수 있습니다")
        else:
            logger.log_debug("AI모드", "플레이어 제어 모드 - 모든 파티원을 직접 제어합니다")

        # ✅ 간단 렌더링 모드 감지 (Electron/비 TTY 환경에서 커서 제어 실패 시)
        try:
            import os, sys
            self.simple_battle_render_mode = False
            # SUBPROCESS_MODE나 비 TTY, 또는 사용자 지정 환경변수 존재 시 단순 모드
            if os.getenv('SUBPROCESS_MODE') == '1' or not getattr(sys.stdout, 'isatty', lambda: True)():
                self.simple_battle_render_mode = True
            # 추가 힌트 환경변수
            if os.getenv('ELECTRON_RUN') == '1':
                self.simple_battle_render_mode = True
        except Exception:
            self.simple_battle_render_mode = True

        # 화면 초기화 & 기본 전투 헤더 (Electron 검은 화면 대비)
        try:
            print("\x1b[2J\x1b[H", end="")  # 전체 클리어
        except Exception:
            pass
        
        # 🎮 전투 시작 진동 (인카운터 패턴)
        if self.vibration_enabled:
            self.input_manager.vibrate_encounter()
        
        print("⚔️ ================= 전투 시작 ================")
        if party:
            print("👥 파티: " + ", ".join(getattr(c, 'name', '???') for c in party))
        if enemies:
            print("🛑 적: " + ", ".join(getattr(e, 'name', '???') for e in enemies))
        print("============================================")
        # 첫 상태 즉시 표시 (고급 버퍼 실패 환경 대비)
        try:
            first_alive = next((c for c in party if getattr(c, 'is_alive', True)), None)
            if first_alive:
                # 고급 모드에서도 한 번 즉시 출력하여 초기 공백 방지
                self.show_battle_status(first_alive, party, enemies)
        except Exception:
            pass
        
        # 현재 파티와 적군 정보 저장 (스킬 승리 체크용)
        self._current_party = party
        self._current_enemies = enemies
        
        # 캐릭터들에게 BraveCombatSystem 참조 설정 (Method 4용)
        for character in party + enemies:
            character.combat_system_ref = self
        
        # 전투 초기화
        self._turn_count = 0
        self._last_action_completed = False
        self._recent_combat_logs.clear()  # 로그 초기화
        
        # 🎯 어그로 시스템 초기화 (모든 적군에 대해)
        for enemy in enemies:
            enemy_name = getattr(enemy, 'name', str(enemy))
            self.aggro_system.initialize_enemy(enemy_name, party)
            print(f"🎯 {enemy_name}의 어그로 시스템 초기화 완료")
        
        # 입력 버퍼 클리어 (전투 시작 전)
        if hasattr(self, 'keyboard') and self.keyboard:
            self.keyboard.clear_input_buffer()
        
        # 🔊 전투 진입 SFX 재생
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("battle_start")  # 전투 진입 효과음
                print("🔊 전투 진입!")
            elif hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.play_sfx("battle_start")
                print("🔊 전투 진입!")
        except Exception as e:
            print(f"⚠️ 전투 진입 SFX 재생 실패: {e}")
        
        # 🎵 전투 BGM 재생 (BGMType 사용)
        try:
            # 보스 체크
            is_boss_battle = any(
                ("보스" in enemy.name or "Boss" in enemy.name or "왕" in enemy.name or 
                 "용" in enemy.name or "드래곤" in enemy.name or "마왕" in enemy.name or
                 hasattr(enemy, 'is_boss') and enemy.is_boss or
                 hasattr(enemy, 'enemy_type') and 'boss' in str(enemy.enemy_type).lower() or
                 enemy.level >= 10 or enemy.max_hp > 2000)  # 보스 판정 조건들
                for enemy in enemies
            )
            
            print(f"🎵 BGM 시스템 체크...")
            print(f"   보스 전투 여부: {is_boss_battle}")
            
            if BGMType and get_audio_manager:
                audio_manager = get_audio_manager()
                if audio_manager:
                    if is_boss_battle:
                        audio_manager.play_bgm(BGMType.BOSS)
                        print("🎵 보스 전투 BGM 시작! (BGMType.BOSS)")
                    else:
                        audio_manager.play_bgm(BGMType.BATTLE)
                        print("🎵 일반 전투 BGM 시작! (BGMType.BATTLE)")
                else:
                    print("⚠️ 오디오 매니저를 찾을 수 없습니다.")
            else:
                print("⚠️ BGM 시스템을 사용할 수 없습니다.")
        except Exception as e:
            print(f"⚠️ 전투 BGM 재생 실패: {e}")
            import traceback
            print(f"   상세 오류: {traceback.format_exc()}")
        
        # 전투 시작 시간 기록
        self.battle_start_time = time.time()  # 전투 시작 시간 기록
        
        # 💻 버퍼링 디스플레이 시스템 초기화
        try:
            # self.buffered_display.clear_buffer()  # 사용 중단
            # self.buffered_display.hide_cursor()  # 사용 중단
            print("💻 버퍼링 디스플레이 시스템을 초기화했습니다.")
        except Exception as e:
            print(f"⚠️ 버퍼링 디스플레이 초기화 실패: {e}")
        
        print("\n" + "="*80)
        print("🌟 D A W N   O F   S T E L L A R - Brave Battle! 🌟")
        print("="*80)
        
        # 모든 참전자의 ATB 게이지 초기화 및 검증
        all_combatants = party + enemies
        valid_combatants = []
        
        # 완전체 로깅 시스템 사용
        from .error_logger import get_comprehensive_logger, log_atb_initialization
        logger = get_comprehensive_logger()
        
        logger.log_system_info("ATB", "전투 ATB 시스템 초기화 시작")
        print("📊 ATB 시스템 초기화 중...")
        
        for i, combatant in enumerate(all_combatants):
            # dict 객체인 경우 Character 객체로 변환 필요
            if isinstance(combatant, dict):
                print(f"⚠️ 경고: {combatant}는 dict 객체입니다. Character 객체가 아닙니다.")
                logger.log_error("ATB초기화", f"dict 객체 발견: {combatant}")
                continue
            
            # 이전 ATB 상태 로그
            old_atb = getattr(combatant, 'atb_gauge', 'None')
            character_speed = getattr(combatant, 'speed', 100)
            
            # ATB 게이지 속성 확인 및 초기화
            if not hasattr(combatant, 'atb_gauge'):
                combatant.atb_gauge = 0
                print(f"✨ {combatant.name}에 ATB 게이지를 추가했습니다.")
                log_atb_initialization(combatant.name, 0, character_speed)
            else:
                # 🔄 전투 시작 시 ATB 게이지 적절한 초기화
                # ATB_READY_THRESHOLD = 1000이므로 0-300 범위로 시작 (0-30%)
                import random
                random_start_atb = random.randint(0, 300)  # 0-30% 랜덤 시작
                combatant.atb_gauge = random_start_atb
                print(f"🔄 {combatant.name} ATB 초기화: {old_atb} → {random_start_atb} ({random_start_atb*100//self.ATB_READY_THRESHOLD}%)")
                log_atb_initialization(combatant.name, random_start_atb, character_speed)
            
            # 기본 속도 속성 확인
            if not hasattr(combatant, 'speed'):
                combatant.speed = 100
                print(f"✨ {combatant.name}에 기본 속도(100)를 설정했습니다.")
                logger.log_system_info("ATB", f"{combatant.name} 기본 속도 설정", {"속도": 100})
            
            valid_combatants.append(combatant)
        
        if len(valid_combatants) != len(all_combatants):
            print(f"⚠️ 주의: {len(all_combatants) - len(valid_combatants)}개의 무효한 캐릭터가 감지되었습니다.")
            logger.log_system_warning("ATB", f"무효한 캐릭터 감지", {
                "총캐릭터수": len(all_combatants),
                "유효캐릭터수": len(valid_combatants),
                "무효캐릭터수": len(all_combatants) - len(valid_combatants)
            })
        
        # ATB 초기화 결과 요약
        logger.log_system_info("ATB", "ATB 초기화 완료", {"참여자수": len(valid_combatants)})
        for combatant in valid_combatants:
            final_atb = combatant.atb_gauge
            speed = getattr(combatant, 'speed', 100)
            logger.log_debug("ATB상세", f"최종 상태", {
                "이름": combatant.name,
                "ATB": final_atb,
                "ATB비율": f"{final_atb/20:.1f}%",
                "속도": speed
            })
        
        print(f"✅ ATB 초기화 완료: {len(valid_combatants)}명의 전투 참여자")
        
        # 참조 저장 (action_order 계산용)
        self._current_party = [c for c in party if c in valid_combatants]
        self._current_enemies = [c for c in enemies if c in valid_combatants]
        
        # 파티 멤버들의 특성 효과 적용
        for member in party:
            if hasattr(member, 'apply_trait_effects'):
                member.apply_trait_effects("combat_start")
            if hasattr(member, 'trigger_trait_effects'):
                trait_messages = member.trigger_trait_effects("combat_start")
                for msg in trait_messages:
                    print(f"✨ {member.name}: {msg}")
            
            # 🆓 전투 시작 시 무료 궁극기 초기화
            try:
                from .new_skill_system import reset_free_ultimate
                reset_free_ultimate(member)
            except ImportError:
                # 기존 방식으로 폴백
                member.free_ultimate_used = False
            
            # 🗡️ [MECHANIC INIT] - 직업별 기믹 시스템 초기화
            if hasattr(member, 'character_class'):
                character_class = member.character_class
                
                if character_class == "도적":
                    # 독 스택 초기화
                    if not hasattr(member, 'poison_stacks'):
                        setattr(member, 'poison_stacks', 0)
                    if not hasattr(member, 'max_poison_stacks'):
                        attack_stat = getattr(member, 'attack', 100)
                        max_stacks = int(attack_stat * 1.5)  # 공격력의 150%
                        setattr(member, 'max_poison_stacks', max_stacks)
                    print(f"🗡️ [MECHANIC INIT] - {member.name}: poison_stacks: {member.poison_stacks}/{member.max_poison_stacks}")
                
                elif character_class == "궁수":
                    # 조준 포인트 초기화
                    if not hasattr(member, 'aim_points'):
                        setattr(member, 'aim_points', 0)
                    if not hasattr(member, 'max_aim_points'):
                        setattr(member, 'max_aim_points', 10)
                    print(f"🏹 [MECHANIC INIT] - {member.name}: aim_points: {member.aim_points}/{member.max_aim_points}")
                
                elif character_class == "암살자":
                    # 그림자 카운트 초기화
                    if not hasattr(member, 'shadow_count'):
                        setattr(member, 'shadow_count', 0)
                    if not hasattr(member, 'max_shadow_count'):
                        setattr(member, 'max_shadow_count', 10)
                    print(f"🌑 [MECHANIC INIT] - {member.name}: shadow_count: {member.shadow_count}/{member.max_shadow_count}")
                
                elif character_class == "검성":
                    # 검기 초기화
                    if not hasattr(member, 'sword_aura'):
                        setattr(member, 'sword_aura', 0)
                    if not hasattr(member, 'max_sword_aura'):
                        setattr(member, 'max_sword_aura', 10)
                    print(f"⚡ [MECHANIC INIT] - {member.name}: sword_aura: {member.sword_aura}/{member.max_sword_aura}")
                
                elif character_class == "바드":
                    # 멜로디 스택 초기화 (최대치 7)
                    if not hasattr(member, 'melody_stacks'):
                        setattr(member, 'melody_stacks', 0)
                    if not hasattr(member, 'max_melody_stacks'):
                        setattr(member, 'max_melody_stacks', 7)  # 바드 최대치는 7
                    print(f"🎵 [MECHANIC INIT] - {member.name}: melody_stacks: {member.melody_stacks}/{member.max_melody_stacks}")
                
                elif character_class == "광전사":
                    # 🔥 분노 스택 초기화 (공격력 기반 최대치, 1~99999 범위)
                    if not hasattr(member, 'rage_stacks'):
                        setattr(member, 'rage_stacks', 0)
                    if not hasattr(member, 'max_rage_stacks'):
                        # 공격력 기반 최대 분노 계산 (1~99999 범위)
                        base_attack = getattr(member, 'physical_attack', getattr(member, 'attack', 100))
                        max_rage_stacks = max(1, min(99999, base_attack * 50))  # 공격력 * 50, 범위 1~99999
                        setattr(member, 'max_rage_stacks', max_rage_stacks)
                    
                    # 🩸 피해 추적 변수 초기화
                    if not hasattr(member, 'recent_damage_taken'):
                        setattr(member, 'recent_damage_taken', 0)
                    
                    print(f"🔥 [MECHANIC INIT] - {member.name}: rage_stacks: {member.rage_stacks}/{member.max_rage_stacks} (공격력 기반, 범위 1~99999)")
                
                elif character_class == "아크메이지":
                    # 원소 카운트 초기화
                    if not hasattr(member, 'fire_count'):
                        setattr(member, 'fire_count', 0)
                    if not hasattr(member, 'ice_count'):
                        setattr(member, 'ice_count', 0)
                    if not hasattr(member, 'lightning_count'):
                        setattr(member, 'lightning_count', 0)
                    if not hasattr(member, 'max_element_count'):
                        setattr(member, 'max_element_count', 10)
                    print(f"🔮 [MECHANIC INIT] - {member.name}: elements: 🔥{member.fire_count} ❄️{member.ice_count} ⚡{member.lightning_count}")
                
                elif character_class == "용기사":
                    # 드래곤 파워 초기화
                    if not hasattr(member, 'dragon_marks'):
                        setattr(member, 'dragon_marks', 0)
                    if not hasattr(member, 'max_dragon_marks'):
                        setattr(member, 'max_dragon_marks', 10)
                    print(f"🐉 [MECHANIC INIT] - {member.name}: dragon_marks: {member.dragon_marks}/{member.max_dragon_marks}")
                
                elif character_class == "몽크":
                    # 기 에너지 & 타격 표식 초기화
                    if not hasattr(member, 'chi_points'):
                        setattr(member, 'chi_points', 0)
                    if not hasattr(member, 'max_chi_points'):
                        setattr(member, 'max_chi_points', 100)
                    if not hasattr(member, 'strike_marks'):
                        setattr(member, 'strike_marks', 0)
                    print(f"👊 [MECHANIC INIT] - {member.name}: chi_points: {member.chi_points}/{member.max_chi_points}, combo: {member.strike_marks}")
                
                elif character_class == "전사":
                    # 전사 자세 초기화
                    if not hasattr(member, 'warrior_stance'):
                        setattr(member, 'warrior_stance', 'balanced')
                    if not hasattr(member, 'warrior_focus'):
                        setattr(member, 'warrior_focus', 0)
                    print(f"⚔️ [MECHANIC INIT] - {member.name}: stance: {member.warrior_stance}, focus: {member.warrior_focus}")
                
                else:
                    # 기타 직업들 기본 초기화
                    print(f"🎭 [MECHANIC INIT] - {member.name}: {character_class} (기본 설정)")
        
        # 🛡️ 전사 적응형 시스템 적용
        if WARRIOR_SYSTEM_AVAILABLE:
            try:
                warrior_system = get_warrior_system()
                for member in party:
                    if member.character_class == "전사" or "전사" in member.character_class:
                        # 상황 분석 후 최적 자세로 적응
                        other_allies = [ally for ally in party if ally != member]
                        if warrior_system.analyze_situation_and_adapt(member, other_allies, enemies):
                            print(f"🛡️ {member.name}이(가) 전투 상황에 적응했습니다!")
            except Exception as e:
                self._debug_print(f"⚠️ 전사 적응형 시스템 오류: {e}")
            
        # 전투 루프
        print("🎮 전투 루프 시작!")
        battle_result = self.battle_loop(party, enemies)
        
        # 승리 시에는 BGM이 이미 재생되고 있으므로 바로 복구하지 않음
        # 패배 시에만 즉시 BGM 복구
        if not battle_result:  # 패배 시에만
            # 🎵 전투 종료 후 BGM 복구 (안전 함수 사용)
            try:
                # 메인 게임의 안전 BGM 함수 사용
                if hasattr(self, 'game_instance') and self.game_instance:
                    if hasattr(self.game_instance, 'safe_play_bgm'):
                        self.game_instance.safe_play_bgm("dungeon", loop=True)
                        print("🎵 차원 공간 BGM으로 복귀! (안전 모드)")
                    else:
                        # 폴백: 직접 호출
                        if hasattr(self, 'audio_system') and self.audio_system:
                            self.audio_system.play_bgm("dungeon", loop=True)
                        elif hasattr(self, 'sound_manager') and self.sound_manager:
                            self.sound_manager.play_bgm("dungeon")
                        print("🎵 차원 공간 BGM으로 복귀!")
                else:
                    # 기존 방식
                    if hasattr(self, 'audio_system') and self.audio_system:
                        self.audio_system.play_bgm("dungeon", loop=True)
                        print("🎵 차원 공간 BGM으로 복귀!")
                    elif hasattr(self, 'sound_manager') and self.sound_manager:
                        self.sound_manager.play_bgm("dungeon")
                        print("🎵 차원 공간 BGM으로 복귀!")
            except Exception as e:
                print(f"⚠️ 차원 공간 BGM 복구 실패: {e}")
        else:
            # 🎵 승리 시에도 3초 후 필드 BGM으로 전환
            import threading
            def delayed_bgm_restore():
                import time
                time.sleep(3.0)  # 승리 팡파레 재생 시간 확보
                try:
                    if hasattr(self, 'game_instance') and self.game_instance:
                        if hasattr(self.game_instance, 'safe_play_bgm'):
                            self.game_instance.safe_play_bgm("dungeon", loop=True)
                            print("🎵 승리 후 차원 공간 BGM으로 복귀! (3초 지연)")
                        else:
                            if hasattr(self, 'audio_system') and self.audio_system:
                                self.audio_system.play_bgm("dungeon", loop=True)
                            elif hasattr(self, 'sound_manager') and self.sound_manager:
                                self.sound_manager.play_bgm("dungeon")
                            print("🎵 승리 후 차원 공간 BGM으로 복귀!")
                    else:
                        if hasattr(self, 'audio_system') and self.audio_system:
                            self.audio_system.play_bgm("dungeon", loop=True)
                            print("🎵 승리 후 차원 공간 BGM으로 복귀!")
                        elif hasattr(self, 'sound_manager') and self.sound_manager:
                            self.sound_manager.play_bgm("dungeon")
                            print("🎵 승리 후 차원 공간 BGM으로 복귀!")
                except Exception as e:
                    print(f"⚠️ 승리 후 차원 공간 BGM 복구 실패: {e}")
            
            # 백그라운드에서 지연된 BGM 복구 실행
            bgm_thread = threading.Thread(target=delayed_bgm_restore, daemon=True)
            bgm_thread.start()
        
        # 전투 종료 후 디스플레이 정리
        try:
            # self.buffered_display.show_cursor()  # 사용 중단
            # self.buffered_display.clear_buffer()  # 사용 중단
            print("\n💻 화면 버퍼를 정리했습니다.")
        except Exception as e:
            print(f"⚠️ 디스플레이 정리 실패: {e}")
        
        return battle_result
        
    def battle_loop(self, party: List[Character], enemies: List[Character]) -> bool:
        """전투 루프 - 개선된 ATB 시스템"""
        turn_count = 0
        
        print("🔄 전투 루프 시작!")
        log_debug("전투루프", "전투 루프 시작", {
            "파티": [f"{p.name}(HP:{getattr(p, 'current_hp', 0)}/{getattr(p, 'max_hp', 0)}, 생존:{getattr(p, 'is_alive', False)})" for p in party],
            "적": [f"{e.name}(HP:{getattr(e, 'current_hp', 0)}/{getattr(e, 'max_hp', 0)}, 생존:{getattr(e, 'is_alive', False)})" for e in enemies]
        })
        
        # 유효한 캐릭터 객체만 필터링
        valid_party = []
        for c in party:
            if hasattr(c, 'name') and hasattr(c, 'is_alive'):
                valid_party.append(c)
            else:
                print(f"⚠️ 경고: 파티에 잘못된 객체 감지: {type(c).__name__}")
                log_debug("전투루프", f"잘못된 파티 객체", {"타입": type(c).__name__})
        
        valid_enemies = []
        for c in enemies:
            if hasattr(c, 'name') and hasattr(c, 'is_alive'):
                valid_enemies.append(c)
            else:
                print(f"⚠️ 경고: 적군에 잘못된 객체 감지: {type(c).__name__}")
                log_debug("전투루프", f"잘못된 적 객체", {"타입": type(c).__name__})
        
        print(f"📊 유효한 파티: {len(valid_party)}명, 유효한 적: {len(valid_enemies)}마리")
        log_debug("전투루프", "유효한 참가자 확인", {
            "유효파티": len(valid_party),
            "유효적": len(valid_enemies),
            "유효파티명": [p.name for p in valid_party],
            "유효적명": [e.name for e in valid_enemies]
        })
        
        # 🚨 즉시 전투 종료 조건 체크 (시작 직후)
        if self.check_battle_end(valid_party, valid_enemies):
            log_debug("전투루프", "전투 시작 직후 종료 조건 만족", {})
            result = self.determine_winner(valid_party, valid_enemies)
            return result
        
        # 파티 정보를 클래스 변수로 저장
        self._current_party = valid_party
        self._current_enemies = valid_enemies
        
        # 전투 루프 메인 처리
        try:
            while True:
                turn_count += 1
                print(f"🔄 턴 {turn_count} 시작!")
                
                # ATB 게이지가 100%에 도달할 때까지 점진적 업데이트
                max_attempts = 10  # 시도 횟수 대폭 줄임 (50 → 10)
                attempts = 0
                
                while attempts < max_attempts:
                    try:
                        # ATB 애니메이션과 함께 업데이트 (첫 번째 시도에서만 애니메이션 표시)
                        show_animation = (attempts == 0)
                        self.update_atb_gauges(valid_party + valid_enemies, show_animation)
                        
                        action_order = self.get_action_order(valid_party + valid_enemies)
                        if action_order:
                            break
                        attempts += 1
                        time_module.sleep(0.02)  # 더 빠른 업데이트 (50ms → 20ms)
                    except Exception as atb_error:
                        log_error("ATB업데이트", f"ATB 업데이트 중 오류 (시도 {attempts+1})", {"오류": str(atb_error)})
                        print(f"⚠️ ATB 업데이트 오류: {atb_error}")
                        break  # ATB 업데이트에 실패하면 루프 종료
                
                if not action_order:
                    # ATB 소폭 증가로 교착 상태 해결 (100% 강제 설정 방지)
                    for combatant in valid_party + valid_enemies:
                        if combatant.is_alive and hasattr(combatant, 'atb_gauge'):
                            # 강제로 100%로 설정하지 않고 점진적 증가
                            increase_amount = min(200, self.ATB_READY_THRESHOLD - combatant.atb_gauge + 1)
                            combatant.atb_gauge = min(self.ATB_MAX, combatant.atb_gauge + increase_amount)
                    action_order = self.get_action_order(valid_party + valid_enemies)
                    if not action_order:
                        # 그래도 실패하면 추가 소폭 증가
                        for combatant in valid_party + valid_enemies:
                            if combatant.is_alive and hasattr(combatant, 'atb_gauge'):
                                combatant.atb_gauge = min(self.ATB_MAX, combatant.atb_gauge + 1)
                        while True:
                            self.update_atb_gauges(valid_party + valid_enemies)  # ATB 먼저 업데이트
                            action_order = self.get_action_order(valid_party + valid_enemies)
                            if action_order:
                                break  # 행동 가능한 캐릭터가 생기면 진행
                # 선택된 캐릭터의 턴 처리
                character = action_order[0]
                action_taken = False  # 🎯 행동 완료 여부 플래그 초기화
                
                # 현재 행동 중인 캐릭터 추적
                self._current_actor = character
                
                if not character.is_alive:
                    continue
                    
                # 상태이상 처리
                if hasattr(character, 'status_manager'):
                    character.status_manager.process_turn_effects(character)
                
                # 아군 판별 변수 초기화 (블록 밖에서 사용되므로 미리 정의)
                is_ally = False
                    
                if character in valid_party:
                    print(f"🎮 {character.name}의 턴이 시작됩니다!")
                    
                    # 아군 판별 안정성 강화 - 더 확실한 검증
                    try:
                        # 1차: 파티 리스트에 직접 포함되는지 확인
                        is_ally = character in valid_party
                        
                        # 2차: 원본 파티에도 포함되는지 확인 (백업)
                        if not is_ally:
                            is_ally = character in party
                        
                        # 3차: 플레이어 캐릭터인지 확인
                        if not is_ally and hasattr(character, 'is_player_character'):
                            is_ally = character.is_player_character
                        
                        # 4차: 적군 속성이 없으면 아군으로 처리
                        if not is_ally and not hasattr(character, 'is_enemy'):
                            is_ally = True
                        
                        # 5차: 이름 기반 매칭 (최종 백업)
                        if not is_ally:
                            party_names = [p.name for p in valid_party]
                            is_ally = character.name in party_names
                            
                    except Exception as e:
                        self._debug_print(f"⚠️ 아군 판별 오류: {e}")
                        is_ally = True  # 안전을 위해 아군으로 처리
                
                # 강제 아군 전환 로그 (필요시에만)
                if not is_ally:
                    print(f"⚠️ {character.name}을 아군으로 강제 변경합니다.")
                    is_ally = True
                
                # 클래식 모드 확인 - 조건부 처리 (안정화된 클래식 게임모드 판별)
                ai_controlled = False
                
                try:
                    ai_game_mode_enabled = self.is_ai_game_mode_enabled()
                    from .error_logger import get_error_logger
                    logger = get_error_logger()
                    logger.log_debug("AI모드체크", f"클래식 게임모드 상태: {ai_game_mode_enabled}")
                    
                    # 클래식 게임모드가 활성화된 경우에만 클래식 제어 체크
                    if ai_game_mode_enabled:
                        try:
                            from game.ai_game_mode import ai_game_mode_manager
                            if hasattr(ai_game_mode_manager, 'is_ai_controlled'):
                                ai_controlled = ai_game_mode_manager.is_ai_controlled(character)
                                if ai_controlled:
                                    logger.log_debug("AI제어", f"{character.name}은(는) AI가 제어합니다.")
                                    result = self.ai_turn(character, valid_party, valid_enemies)
                                else:
                                    logger.log_debug("플레이어제어", f"{character.name}은(는) 플레이어가 직접 제어합니다.")
                                    result = self.player_turn(character, valid_party, valid_enemies)
                            else:
                                logger.log_debug("플레이어제어", f"{character.name} 플레이어 턴으로 처리 (AI 매니저 기능 없음)")
                                result = self.player_turn(character, valid_party, valid_enemies)
                        except ImportError:
                            logger.log_debug("플레이어제어", f"{character.name} 플레이어 턴으로 처리 (AI 모듈 없음)")
                            result = self.player_turn(character, valid_party, valid_enemies)
                    else:
                        # 클래식 게임모드가 비활성화된 경우 모든 파티원을 플레이어가 직접 제어
                        logger.log_debug("플레이어제어", f"{character.name}은(는) 플레이어가 직접 제어합니다. (클래식 모드 OFF)")
                        result = self.player_turn(character, valid_party, valid_enemies)
                        
                except Exception as e:
                    # 오류 발생 시 안전하게 플레이어 제어로 폴백
                    print(f"⚠️ 클래식 모드 판별 오류 ({e}), {character.name} 플레이어 턴으로 처리")
                    result = self.player_turn(character, valid_party, valid_enemies)
                    
                # 도망 성공 처리
                if result == "flee_success":
                    print(f"\n{get_color('BRIGHT_YELLOW')}🏃💨 전투에서 성공적으로 도망쳤습니다!{get_color('RESET')}")
                    self._wait_for_user_input_or_timeout(3.0)
                    return "fled"  # 도망 성공으로 전투 종료
                elif result == "action_completed":  # 🎯 실제 행동을 완료한 경우에만 ATB 차감
                    action_taken = True
                elif result is not None:  # 다른 전투 종료 신호
                    print(f"\n{get_color('BRIGHT_CYAN')}전투가 종료되었습니다!{get_color('RESET')}")
                    self._wait_for_user_input_or_timeout(5.0)
                    return result
                else:
                    # result가 None인 경우 (취소, 캐스팅 중 등) ATB 차감하지 않음
                    action_taken = False
            else:
                result = self.enemy_turn(character, valid_party, valid_enemies)
                if result is not None:  # 전투 종료 신호
                    print(f"\n{get_color('BRIGHT_CYAN')}전투가 종료되었습니다!{get_color('RESET')}")
                    self._wait_for_user_input_or_timeout(5.0)
                    return result
                else:
                    # 적군은 항상 행동을 수행
                    action_taken = True
            
            # 🎯 중요: 실제 행동을 수행한 경우에만 ATB 차감
            if action_taken and hasattr(character, 'atb_gauge'):
                # 완전 리셋 대신 행동 비용만 차감 (기본 행동 비용: 1000)
                action_cost = 1000  # 기본 행동 비용
                old_atb = character.atb_gauge
                character.atb_gauge = max(0, character.atb_gauge - action_cost)
                print(f"🔄 {character.name} ATB: {old_atb} → {character.atb_gauge} (행동 비용: {action_cost})")
                # 행동 완료 시 취소 카운터와 쿨다운 리셋
                cid = id(character)
                self._cancel_counters[cid] = 0
                if cid in self._cancel_last_time:
                    del self._cancel_last_time[cid]
                if cid in self._cancel_cooldown_until:
                    del self._cancel_cooldown_until[cid]
            elif not action_taken:
                # 취소 스팸 완화: 같은 캐릭터의 반복 취소 출력은 2초에 1회로 제한, 3회 이상 연속 시 조용히 유지
                cid = id(character)
                now = time_module.time()
                cnt = self._cancel_counters.get(cid, 0) + 1
                last = self._cancel_last_time.get(cid, 0)
                if (now - last) > 2.0 and cnt <= 3:
                    print(f"⏸️ {character.name}의 턴이 취소되어 ATB를 유지합니다 (ATB: {getattr(character, 'atb_gauge', 0)})")
                    self._cancel_last_time[cid] = now
                self._cancel_counters[cid] = cnt
                # 즉시 재선택 방지: 짧은 쿨다운과 ATB 살짝 하향(임계치-1)
                # 2회 이상 연속 취소 시 0.5초 쿨다운 부여
                if cnt >= 2:
                    self._cancel_cooldown_until[cid] = now + 0.5
                    if hasattr(character, 'atb_gauge') and character.atb_gauge >= getattr(self, 'ATB_READY_THRESHOLD', 1000):
                        character.atb_gauge = getattr(self, 'ATB_READY_THRESHOLD', 1000) - 1
            
            # 턴 종료 시 플레이어 턴 플래그 해제
            if hasattr(self, 'is_player_turn_active'):
                self.is_player_turn_active = False
            
            # 현재 행동자 초기화
            if hasattr(self, '_current_actor'):
                self._current_actor = None
                
            # 상태이상 턴 종료 처리
            if hasattr(character, 'status_manager'):
                character.status_manager.process_turn_effects(character)
            
            # 🏹 궁수 지원사격 지속시간 감소
            self._process_support_fire_duration(character)
                
            # 행동 처리 후 전투 종료 조건 확인
            if self.check_battle_end(valid_party, valid_enemies):
                result = self.determine_winner(valid_party, valid_enemies)
                print(f"\n{get_color('BRIGHT_CYAN')}전투가 종료되었습니다!{get_color('RESET')}")
                self._wait_for_user_input_or_timeout(5.0)
                return result
            
            # 짧은 대기 후 다음 턴으로 - 더 빠르게
            time_module.sleep(0.03)  # 30ms로 단축 (100ms→30ms)
        
        except Exception as battle_error:
            # 전투 루프에서 치명적 오류 발생
            log_error("전투루프", f"전투 루프 중 치명적 오류", {"오류": str(battle_error)})
            print(f"❌ 전투 중 치명적 오류 발생: {battle_error}")
            print("전투를 안전하게 종료합니다...")
            import traceback
            traceback.print_exc()
            
            # 안전한 종료 처리
            try:
                from .character import set_combat_active
                set_combat_active(False)
                if hasattr(self, 'gauge_animator'):
                    self.gauge_animator.set_combat_mode(False)
            except:
                pass
            return "error"
    
    def ai_turn(self, character: Character, party: List[Character], enemies: List[Character]):
        """AI 턴 처리"""
        try:
            from game.ai_game_mode import ai_game_mode_manager
            
            # AI 동료 찾기
            ai_companion = None
            for companion in ai_game_mode_manager.ai_companions:
                if companion.character == character:
                    ai_companion = companion
                    break
            
            if not ai_companion:
                # AI 동료가 없으면 기본 플레이어 턴으로 처리
                return self.player_turn(character, party, enemies)
            
            # AI 행동 결정
            action_type, action_data = ai_companion.decide_action(party, enemies)
            
            # AI 행동 실행
            print(f"\n💭 {character.name}이(가) 행동을 결정하고 있습니다...")
            time_module.sleep(0.5)
            
            if action_type == "attack":
                target = action_data.get("target")
                if target and target.is_alive:
                    print(f"⚔️ {character.name}이(가) {target.name}을(를) 공격합니다!")
                    return self._execute_attack(character, target, party, enemies)
            
            elif action_type == "skill":
                skill = action_data.get("skill")
                target = action_data.get("target")
                if skill and target:
                    print(f"✨ {character.name}이(가) {skill.name}을(를) 사용합니다!")
                    return self._execute_skill(character, skill, target, party, enemies)
            
            elif action_type == "defend":
                print(f"🛡️ {character.name}이(가) 방어 자세를 취합니다!")
                character.is_defending = True
                return None
            
            elif action_type == "heal":
                target = action_data.get("target") or character
                print(f"💚 {character.name}이(가) {target.name}을(를) 치료합니다!")
                # 간단한 자가 치료
                heal_amount = character.max_hp * 0.2
                target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                print(f"   {target.name}이(가) {heal_amount:.0f} HP 회복했습니다!")
                return None
            
            elif action_type == "use_item":
                item_type = action_data.get("item_type", "healing")
                print(f"🧪 {character.name}이(가) {item_type} 아이템을 사용합니다!")
                # 간단한 아이템 효과
                if item_type == "healing":
                    heal_amount = character.max_hp * 0.3
                    character.current_hp = min(character.max_hp, character.current_hp + heal_amount)
                    print(f"   {character.name}이(가) {heal_amount:.0f} HP 회복했습니다!")
                return None
            
            elif action_type == "request":
                request_type = action_data.get("type")
                message = ai_companion.make_request_to_player(request_type)
                print(f"\n💬 {message}")
                from .error_logger import get_error_logger
                logger = get_error_logger()
                logger.log_error("AI_TURN", "(AI 요청은 전투 후 처리됩니다)")
                # 기본 공격으로 대체
                alive_enemies = [e for e in enemies if e.is_alive]
                if alive_enemies:
                    target = alive_enemies[0]
                    print(f"⚔️ {character.name}이(가) {target.name}을(를) 공격합니다!")
                    return self._execute_attack(character, target, party, enemies)
            
            return None
            
        except Exception as e:
            from .error_logger import get_error_logger
            logger = get_error_logger()
            logger.log_ai_mode_error(f"AI 턴 처리 오류: {type(e).__name__}")
            print(f"📋 상세: {str(e)}")
            print("🔄 기본 플레이어 턴으로 전환합니다...")
            # 오류 발생시 기본 플레이어 턴으로 대체
            return self.player_turn(character, party, enemies)
                
    def player_turn(self, character: Character, party: List[Character], enemies: List[Character]):
        """플레이어 턴 - 클래식 게임모드 지원"""        
        # 플레이어 턴 시작 플래그 설정
        self.is_player_turn_active = True
        
        # 플레이어 턴 시작 효과음 재생
        if hasattr(self, 'sound_manager') and self.sound_manager:
            self.sound_manager.play_sfx("select")  # 선택 효과음으로 턴 알림
        
        try:
            # 전투 종료 체크 - 턴 시작 시 다시 확인
            if self.check_battle_end(party, enemies):
                return self.determine_winner(party, enemies)
            
            # 🛡️ 전사 적응형 시스템 - 턴 시작 시 재평가
            if WARRIOR_SYSTEM_AVAILABLE and (character.character_class == "전사" or "전사" in character.character_class):
                try:
                    warrior_system = get_warrior_system()
                    other_allies = [ally for ally in party if ally != character and ally.current_hp > 0]
                    if warrior_system.analyze_situation_and_adapt(character, other_allies, enemies):
                        pass  # 메시지는 이미 출력됨
                except Exception as e:
                    print(f"⚠️ 전사 적응형 시스템 오류: {e}")
                
            # 🎯 캐스팅 완료 체크 - 캐스팅 중인 캐릭터는 자동으로 스킬 실행 (강화된 처리)
        finally:
            # 플레이어 턴 종료 시 항상 플래그 해제
            if hasattr(self, 'is_player_turn_active'):
                self.is_player_turn_active = False
                
        # 🎯 캐스팅 완료 체크 - 캐스팅 중인 캐릭터는 자동으로 스킬 실행 (강화된 처리)
        if hasattr(character, 'is_casting') and character.is_casting:
            try:
                # 캐스팅 진행도 표시
                if hasattr(character, 'casting_start_atb') and hasattr(character, 'casting_duration'):
                    progress = ((character.atb_gauge - character.casting_start_atb) / character.casting_duration) * 100
                    progress = max(0, min(100, progress))
                    print(f"🔮 {character.name} 캐스팅 진행도: {progress:.1f}% (ATB: {character.atb_gauge}/{character.casting_start_atb + character.casting_duration})")
                    import sys
                    sys.stdout.flush()  # 즉시 출력
                
                # ATB 기반 캐스팅 완료 체크
                if hasattr(character, 'is_casting_ready_atb') and character.is_casting_ready_atb():
                    print(f"✨ {character.name}의 캐스팅이 완료되어 자동으로 스킬을 시전합니다!")
                    self.complete_casting(character)
                    # 캐스팅 완료 후 효과 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)  # 2초에서 0.5초로 단축
                    # 캐스팅 완료 후 턴 종료
                    self._last_action_completed = True  # 액션 완료 플래그 설정
                    return "action_completed"
                elif hasattr(character, 'atb_gauge') and character.atb_gauge >= 1000:
                    # 강제 캐스팅 완료 (ATB가 1000에 도달했을 때)
                    print(f"🔮 {character.name}의 ATB가 충전되어 강제로 캐스팅을 완료합니다!")
                    self.complete_casting(character)
                    import time
                    time.sleep(0.5)  # 2초에서 0.5초로 단축
                    self._last_action_completed = True  # 액션 완료 플래그 설정
                    return "action_completed"
                else:
                    # 캐스팅 진행률 표시
                    if hasattr(character, 'get_casting_progress'):
                        progress = character.get_casting_progress()
                        print(f"⏳ {character.name} 캐스팅 진행 중... {progress*100:.1f}%")
                    elif hasattr(character, 'atb_gauge'):
                        progress = character.atb_gauge / 1000.0
                        print(f"⏳ {character.name} 캐스팅 진행 중... {progress*100:.1f}% (ATB: {character.atb_gauge}/1000)")
                    else:
                        print(f"🔮 {character.name}은(는) 스킬을 캐스팅 중입니다...")
                    import time
                    time.sleep(0.2)  # 1초에서 0.2초로 단축
                    # 캐스팅 중이므로 턴 종료
                    return None
            except Exception as casting_error:
                print(f"⚠️ 캐스팅 처리 중 오류: {casting_error}")
                print(f"🔄 캐스팅 상태를 초기화하고 일반 턴으로 진행합니다.")
                self._clear_casting_state(character)
                return None
            
        # 턴 시작 시 특성 효과 적용
        self.trait_integrator.apply_turn_start_trait_effects(character)
        
        # 🛡️ 턴 시작 시 특수 상태 업데이트
        self._update_special_status_turn_start(character)
        
        # 캐릭터별 턴 시작 처리 (불굴의 의지 회복 등)
        if hasattr(character, 'start_turn'):
            character.start_turn()
            
        # 턴 시작 시 INT BRV 회복 처리
        if hasattr(character, 'recover_int_brv_on_turn_start'):
            old_brv = character.brave_points
            recovered = character.recover_int_brv_on_turn_start()
            if recovered > 0:
                print(f"🔄 {character.name}의 BRV가 INT BRV {recovered}로 회복되었습니다!")
                
                # BRV 회복 (자동 애니메이션 트리거)
                # character.brave_points는 이미 recover_int_brv_on_turn_start()에서 설정됨
                
                # BREAK 상태 해제 체크
                if getattr(character, 'is_broken', False) and character.brave_points > 0:
                    character.is_broken = False
                    print(f"✨ {character.name}의 BREAK 상태가 해제되었습니다!")
            
        # self.show_battle_status(character, party, enemies)  # 메뉴에서 중복 표시되므로 제거
        
        # 캐릭터 특성 쿨다운과 지속효과 업데이트
        if hasattr(character, 'traits'):
            for trait in character.traits:
                trait.update_cooldown()
                if hasattr(trait, 'update_duration_effects'):
                    effects = trait.update_duration_effects(character)
                    for effect in effects:
                        print(f"✨ {effect}")
        
        # 자동 전투 모드 체크
        if self.auto_battle:
            return self._auto_battle_action(character, party, enemies)
        
        # 클래식 게임모드 체크 - 조건부 처리 (안정화된 버전)
        try:
            ai_mode_enabled = self.is_ai_game_mode_enabled()
            
            if ai_mode_enabled:
                # AI 모드에서 플레이어가 조작하는 캐릭터인지 확인
                try:
                    from .ai_game_mode import ai_game_mode_manager
                    from .error_logger import get_error_logger
                    logger = get_error_logger()
                    
                    logger.log_debug("AI제어확인", f"AI 모드 활성화 - {character.name} 제어 권한 확인 중...")
                    
                    if hasattr(ai_game_mode_manager, 'player_controlled_characters'):
                        player_chars = [char.name for char in ai_game_mode_manager.player_controlled_characters]
                        logger.log_debug("플레이어캐릭터", f"플레이어 조작 캐릭터: {player_chars}")
                        
                        if character in ai_game_mode_manager.player_controlled_characters:
                            logger.log_debug("플레이어제어", f"{character.name} - 플레이어 직접 조작 모드")
                            # 플레이어가 조작하는 캐릭터는 일반 플레이어 턴으로 진행
                            pass  # 아래의 일반 플레이어 턴 로직 실행
                        else:
                            logger.log_debug("AI자동제어", f"{character.name} - AI 자동 조작 모드")
                            try:
                                from .ai_game_mode import process_character_turn
                                action_type, action_data = process_character_turn(character, party, enemies)
                                return self._execute_ai_action(character, action_type, action_data, party, enemies)
                            except ImportError:
                                logger.log_error("AI_MODE_ERROR", f"AI 모듈 로드 실패, {character.name} 플레이어 제어로 전환")
                            except Exception as ai_error:
                                logger.log_error("AI_MODE_ERROR", f"AI 처리 오류, {character.name} 플레이어 제어로 전환", ai_error)
                    else:
                        logger.log_error("AI_MODE_ERROR", f"AI 모드 매니저에 player_controlled_characters 속성이 없음")
                except Exception as e:
                    from .error_logger import get_error_logger
                    logger = get_error_logger()
                    logger.log_error("AI_MODE_ERROR", f"AI 모드 상태 확인 실패: {e}", e)
                    logger.log_debug("AI모드", f"{character.name} 플레이어 제어로 폴백")
            else:
                from .error_logger import get_error_logger
                logger = get_error_logger()
                logger.log_debug("AI모드", f"AI 모드 비활성화 - {character.name} 플레이어 제어 모드")
        except Exception as e:
            from .error_logger import get_error_logger
            logger = get_error_logger()
            logger.log_error("AI_MODE_ERROR", f"AI 모드 체크 오류: {e}", e)
            # 오류 시 플레이어 제어로 폴백
            logger.log_debug("플레이어폴백", f"{character.name} 플레이어 제어로 폴백")
        
        while True:
            # 전투 상태 표시
            print(f"\n🎮 {character.name}의 턴")
            print("="*50)
            
            # 현재 상태 간단 요약
            hp_percentage = int((character.current_hp / character.max_hp) * 100)
            brv_status = f"BRV: {character.brave_points}" if hasattr(character, 'brave_points') else "BRV: 0"
            mp_status = f"MP: {character.current_mp}/{character.max_mp}" if hasattr(character, 'current_mp') else "MP: N/A"
            
            print(f"상태: HP {hp_percentage}% | {brv_status} | {mp_status}")
            
            # 적 수 표시
            alive_enemies = [e for e in enemies if e.is_alive]
            print(f"적: {len(alive_enemies)}마리 생존")
            print("="*50)
            
            from .cursor_menu_system import create_simple_menu
            
            # 직업별 Brave 공격 설명 생성
            character_class = getattr(character, 'character_class', '전사')
            class_brave_descriptions = {
                    "전사": "⚡ 적응형 강타: 현재 자세에 따라 다른 효과",
                    "아크메이지": "⚡ 마력 파동: 적의 마법방어력 10% 감소",
                    "궁수": "⚡ 삼연사: 조준 포인트 생성하는 연속 공격",
                    "도적": "⚡ 맹독침: 맹독 누적 + 기존 독 강화",
                    "성기사": "⚡ 성스러운타격: 공격하며 아군 회복",
                    "암흑기사": "⚡ 흡혈 베기: 피해의 10% HP 회복 (너프됨)",
                    "몽크": "⚡ 연환 타격: 타격 표식 중첩",
                    "바드": "⚡ 음파 공격: 아군 사기 증진",
                    "네크로맨서": "⚡ 생명력 흡수: 피해의 5% MP 회복 (최대 MP 15%까지)",
                    "용기사": "⚡ 화염 강타: 화상 상태이상 부여",
                    "검성": "⚡ 검기 베기: 뒤의 적들에게도 피해",
                    "정령술사": "⚡ 원소 탄환: 랜덤 원소 약점 적용",
                    "암살자": "⚡ 그림자 강타: 그림자 생성 + 메아리 추가피해",
                    "기계공학자": "⚡ 기계타격: 기계 에너지 충전",
                    "무당": "⚡ 영혼 타격: 방어력 무시 피해",
                    "해적": "⚡ 이도류 난타: 30% 확률로 2회 공격",
                    "사무라이": "⚡ 거합 베기: HP 낮을수록 강화",
                    "드루이드": "⚡ 자연의 분노: 공격 후 HP 회복",
                    "철학자": "⚡ 논리적 반박: 다음 턴 회피율 증가",
                    "시간술사": "⚡ 시간 조작: 적의 행동 지연",
                    "연금술사": "⚡ 화학 폭발: 주변 적에게 연쇄 피해",
                    "검투사": "⚡ 투기장 기술: 반격 확률 증가",
                    "기사": "⚡ 창 돌격: 관통 피해",
                    "신관": "⚡ 축복의 빛: 아군에게 축복 버프",
                    "마검사": "⚡ 마법검기: 물리+마법 피해",
                    "차원술사": "⚡ 차원 균열: 적의 정확도 감소",
                    "광전사": "⚡ 분노의 폭발: HP 낮을수록 강화"
                }
                
            # 직업별 HP 공격 설명 생성 - 전사는 new_skill_system.py에서 관리
            class_hp_descriptions = {
                "아크메이지": "💀 마력 폭발: 주변 적들에게도 피해",
                "궁수": "💀 정밀 관통사격: 뒤의 적들에게 관통 피해",
                "도적": "💀 독혈촉진: 남은 독 피해의 60%를 즉시 피해",
                "성기사": "💀 심판의 빛: 아군 전체 상태이상 해제",
                "암흑기사": "💀 흡혈 강타: 피해의 60% HP 대량 회복",
                "몽크": "💀 폭렬권: 표식 폭발로 추가 피해",
                "바드": "💀 영혼의 노래: 아군 전체 회복+버프",
                "네크로맨서": "💀 영혼 흡수: MP 탈취 및 회복",
                "용기사": "💀 드래곤 브레스: 광역 화염 피해",
                "검성": "💀 일섬: 방어력 무시 고정 피해",
                "정령술사": "💀 원소 융합: 모든 원소 효과 적용",
                "암살자": "🌑 그림자 처형: 모든 그림자 소모 괴멸적 일격",
                "기계공학자": "💀 에너지방출: 축적된 기계 에너지 폭발",
                "무당": "💀 영혼 분리: 방어력 완전 무시",
                "해적": "💀 해적의 보물: 4가지 무기 연속 공격",
                "사무라이": "💀 무사도 비의: 필사의 일격",
                "드루이드": "💀 자연의 심판: 아군 회복+자연 축복",
                "철학자": "💀 진리의 깨달음: 약점 공격+버프 해제",
                "시간술사": "💀 시간 정지: 4연속 공격",
                "연금술사": "💀 대폭발 반응: 광역 폭발 피해",
                "검투사": "💀 검투장의 피날레: 4연속 콤보",
                "기사": "💀 성스러운 돌격: 성스러운 관통 공격",
                "신관": "💀 신의 심판: 아군 전체 대량 회복",
                "마검사": "💀 마검 오의: 물리+마법 융합 공격",
                "차원술사": "💀 차원 붕괴: 공간 자체로 공격",
                "광전사": "💀 최후의 광기: 광폭화로 최강 일격"
            }
            
            brave_desc = class_brave_descriptions.get(character_class, "⚡ 기본 공격: Brave 포인트 획득")
            hp_desc = class_hp_descriptions.get(character_class, "💀 기본 HP 공격: 적에게 HP 피해")
            
            # 자동 전투 모드 상태 표시
            auto_battle_status = "🟢 ON" if self.auto_battle else "🔴 OFF"
            
            action_options = ["⚔️ Brave 공격", "💀 HP 공격", "✨ 스킬 사용", "🧪 아이템 사용", "🛡️ 방어", "🏃 도망", f"⚡ 자동전투 ({auto_battle_status})", "📊 실시간 상태", "❓ 전투 도움말"]
            action_descriptions = [
                f"Brave를 높여 강력한 공격을 준비합니다\n{brave_desc}",
                f"축적된 Brave로 적에게 데미지를 줍니다 (최소 300 BRV 필요)\n{hp_desc}",
                "캐릭터의 특수 스킬을 사용합니다 (MP 소모)",
                "회복 아이템이나 버프 아이템을 사용합니다",
                "방어 태세로 받는 피해를 줄입니다",
                "전투에서 도망칩니다 (스피드 비교 + 시도횟수 보정, 5%-80%)",
                f"자동 전투 모드를 {'끄기' if self.auto_battle else '켜기'} (현재: {auto_battle_status})",
                "현재 전투 상황을 자세히 확인합니다",
                "전투 시스템에 대한 도움말을 봅니다"
            ]
            
            # choice 변수 초기화
            choice = None
            
            # 🚀 실시간 ATB 전투 메뉴 시스템
            try:
                # 실시간 메뉴 처리를 위한 논블로킹 메뉴 시스템
                choice = self._real_time_combat_menu(character, party, enemies, action_options, action_descriptions)
                
                if choice is None or choice == -1:  # 취소 또는 ATB 인터럽트
                    return None
                    
            except Exception as realtime_error:
                print(f"⚠️ 실시간 메뉴 오류: {realtime_error}")
                print("📝 기본 메뉴 시스템으로 전환합니다...")
                
                # 폴백: 기존 메뉴 시스템 사용
                try:
                    from .cursor_menu_system import create_simple_menu
                    
                    # 간단한 상태 정보 구성
                    status_lines = []
                    status_lines.append(f"🛡️ 아군 파티:")
                    for member in party:
                        if member.is_alive:
                            hp_pct = int((member.current_hp / member.max_hp) * 100)
                            status_lines.append(f"  🔮 {member.name}: HP {hp_pct}%")
                    
                    status_lines.append(f"\n⚔️ 적군:")
                    for enemy in enemies:
                        if enemy.is_alive:
                            hp_pct = int((enemy.current_hp / enemy.max_hp) * 100)
                            status_lines.append(f"  👹 {enemy.name}: HP {hp_pct}%")
                    
                    # 기본 메뉴 생성
                    menu = create_simple_menu(
                        title="⚔️ 전투 - 행동 선택 (기본 모드)",
                        options=action_options,
                        extra_content=status_lines,
                        clear_screen=False
                    )
                    choice = menu.run()
                    
                    if choice is None or choice == -1:
                        return None
                        
                except ImportError:
                    # 최종 폴백: 직접 입력
                    print("⚔️ 전투 메뉴 (텍스트 모드)")
                    print("─" * 50)
                    for i, option in enumerate(action_options):
                        print(f"[{i+1}] {option}")
                    print("─" * 50)
                    
                    try:
                        choice_input = input("선택하세요 (1-9): ")
                        choice = int(choice_input) - 1
                        if choice < 0 or choice >= len(action_options):
                            return None
                    except (ValueError, KeyboardInterrupt):
                        return None
                from .cursor_menu_system import create_simple_menu
                
                # 전투 상태 정보 구성 (최적화된 이쁜 버전)
                status_lines = []
                
                try:
                    # 최적화된 게이지 시스템 사용 - 강화된 import
                    try:
                        from .optimized_gauge_system import OptimizedGaugeSystem
                        gauge_system = OptimizedGaugeSystem()
                        gauge_system_available = True
                    except ImportError as e:
                        gauge_system_available = False
                    
                    if gauge_system_available:
                        # 최적화된 파티와 적 상태 표시 사용
                        party_display = gauge_system.show_optimized_party_status(party, character)
                        enemy_display = gauge_system.show_optimized_enemy_status(enemies)
                        
                        # 상태 정보를 줄 단위로 분할
                        status_lines.extend(party_display.split('\n'))
                        status_lines.extend(enemy_display.split('\n'))
                        
                    else:
                        print("📝 기본 파티 상태 표시 사용 (폴백)")
                        # 기본 파티 상태 표시 (폴백)
                        alive_party = [c for c in party if c.is_alive]
                        status_lines.append(f"🛡️ 아군 파티 ({len(alive_party)}명)")
                        status_lines.append("─" * 50)
                        
                        for member in alive_party:
                            status_line = f"🔮 {member.name}({member.character_class}) - HP: {member.current_hp}/{member.max_hp} MP: {member.current_mp}/{member.max_mp} BRV: {member.brave_points}"
                            status_lines.append(status_line)
                        
                        # 적 상태 표시 (폴백)
                        alive_enemies = [e for e in enemies if e.is_alive]
                        status_lines.append(f"⚔️ 적군 ({len(alive_enemies)}명)")
                        status_lines.append("─" * 50)
                        
                        for enemy in alive_enemies:
                            status_line = f"👹 {enemy.name} - HP: {enemy.current_hp}/{enemy.max_hp} BRV: {enemy.brave_points}"
                            status_lines.append(status_line)
                    
                    # 메뉴 생성 (컬러풀한 상태 정보 포함)
                    menu = create_simple_menu(
                        title="⚔️ 전투 - 행동 선택",
                        options=action_options,
                        extra_content=status_lines,
                        clear_screen=False
                    )
                    choice = menu.run()  # 메뉴 실행하여 선택값 받기
                        
                except Exception as e:
                    gauge_system_available = False
                
                # 게이지 시스템이 정상적으로 로드되고 실행되었는지 확인 후 메뉴 생성
                if not gauge_system_available:
                    # 기본 파티 상태 표시 (폴백)
                    status_lines = []
                    alive_party = [c for c in party if c.is_alive]
                    status_lines.append(f"🛡️ 아군 파티 ({len(alive_party)}명)")
                    status_lines.append("─" * 50)
                    
                    for member in alive_party:
                        status_line = f"🔮 {member.name}({member.character_class}) - HP: {member.current_hp}/{member.max_hp} MP: {member.current_mp}/{member.max_mp} BRV: {member.brave_points}"
                        status_lines.append(status_line)
                    
                    # 적 상태 표시 (폴백)
                    alive_enemies = [e for e in enemies if e.is_alive]
                    status_lines.append(f"⚔️ 적군 ({len(alive_enemies)}명)")
                    status_lines.append("─" * 50)
                    
                    for enemy in alive_enemies:
                        status_line = f"👹 {enemy.name} - HP: {enemy.current_hp}/{enemy.max_hp} BRV: {enemy.brave_points}"
                        status_lines.append(status_line)
                    
                    # 메뉴 생성 (기본 상태 정보 포함)
                    menu = create_simple_menu(
                        title="⚔️ 전투 - 행동 선택 (기본 모드)",
                        options=action_options,
                        extra_content=status_lines,
                        clear_screen=False
                    )
                    choice = menu.run()  # 메뉴 실행하여 선택값 받기
                
                if choice is None or choice == -1:  # 취소
                    return None
                    
            except ImportError:
                # 폴백: 커서 메뉴 없이 직접 키보드 입력
                print("⚔️ 전투 메뉴 (폴백 모드)")
                print("─" * 50)
                for i, (option, desc) in enumerate(zip(action_options, action_descriptions)):
                    print(f"[{i+1}] {option}")
                print("─" * 50)
                print("선택 (1-9, 0=취소): ", end="", flush=True)
                
                # 키보드 시스템 사용
                try:
                    if hasattr(self, 'keyboard') and self.keyboard:
                        key = self.keyboard.get_blocking_key()
                        if key == '0':
                            return None  # 취소
                        choice = int(key) - 1
                        if 0 <= choice < len(action_options):
                            print(f"선택: {action_options[choice]}")
                        else:
                            print("❌ 잘못된 선택입니다.")
                            print("⚠️ Brave 공격(첫 번째 옵션)으로 설정됩니다.")
                            choice = 0  # 기본값으로 설정
                    else:
                        print("🚨 키보드 시스템 오류가 발생했습니다.")
                        print("⚠️ 안전을 위해 Brave 공격(첫 번째 옵션)을 선택합니다.")
                        choice = 0
                except (ValueError, AttributeError):
                    print("❌ 입력 형식 오류가 발생했습니다.")
                    print("⚠️ Brave 공격(첫 번째 옵션)으로 설정됩니다.")
                    choice = 0
            except Exception as e:
                # 메뉴 시스템 오류를 로그에 기록
                log_menu_error(f"플레이어 액션 메뉴 선택 중 오류", e)
                
                # 🚨 안전한 오류 처리: 사용자에게 명확히 알리기
                print(f"\n🚨 메뉴 시스템 오류가 발생했습니다!")
                print(f"오류 내용: {str(e)}")
                print(f"\n📋 사용 가능한 옵션:")
                for i, option in enumerate(action_options):
                    print(f"  {i}: {option}")
                
                # 사용자에게 선택권 제공
                print(f"\n⚠️ 안전을 위해 다음 중 선택해주세요:")
                print(f"  1) Enter 키를 눌러 Brave 공격 (기본값) 실행")
                print(f"  2) 다른 숫자를 입력해서 원하는 행동 선택")
                print(f"  3) 게임을 종료하고 오류를 신고")
                
                try:
                    # 안전한 입력 받기
                    user_input = input("\n선택하세요 (Enter=Brave공격, 숫자=해당행동, q=종료): ").strip().lower()
                    
                    if user_input == 'q':
                        print("게임을 종료합니다. 오류를 개발자에게 신고해주세요.")
                        return None
                    elif user_input == '' or user_input == '1':
                        print("✅ Brave 공격을 선택했습니다.")
                        choice = 0
                    else:
                        try:
                            choice = int(user_input)
                            if 0 <= choice < len(action_options):
                                print(f"✅ {action_options[choice]}을(를) 선택했습니다.")
                            else:
                                print("❌ 잘못된 번호입니다. Brave 공격으로 설정됩니다.")
                                choice = 0
                        except ValueError:
                            print("❌ 잘못된 입력입니다. Brave 공격으로 설정됩니다.")
                            choice = 0
                except Exception as inner_e:
                    print(f"🚨 입력 처리 중 추가 오류 발생: {inner_e}")
                    print("⚠️ 안전을 위해 Brave 공격을 자동 선택합니다.")
                    choice = 0
            
            if choice == 0:  # Brave 공격
                if self.brave_attack_menu(character, enemies):
                    self._last_action_completed = True  # 액션 완료 플래그
                    break
            elif choice == 1:  # HP 공격
                if self.hp_attack_menu(character, enemies):
                    self._last_action_completed = True  # 액션 완료 플래그
                    break
            elif choice == 2:  # 스킬 사용
                if self.skill_menu(character, party, enemies):
                    self._last_action_completed = True  # 액션 완료 플래그
                    break
            elif choice == 3:  # 아이템 사용
                try:
                    result = self.item_menu(character, party)
                    if result:
                        self._last_action_completed = True  # 액션 완료 플래그
                        break
                except Exception as e:
                    print(f"{get_color('RED')}❌ 아이템 사용 중 오류: {e}{get_color('RESET')}")
                    continue
            elif choice == 4:  # 방어
                self.defend_action(character)
                self._last_action_completed = True  # 액션 완료 플래그
                break
            elif choice == 5:  # 도망
                if self.flee_action(character, party, enemies):
                    return "flee_success"  # 도망 성공 신호
                self._last_action_completed = True  # 도망 실패해도 턴 소모
                break
            elif choice == 6:  # 자동 전투 토글
                self.auto_battle = not self.auto_battle
                status = "켜졌습니다" if self.auto_battle else "꺼졌습니다"
                print(f"\n⚡ 자동 전투 모드가 {status}!")
                if self.auto_battle:
                    print("🔸 이제 모든 플레이어 캐릭터가 자동으로 행동합니다")
                    print("🔸 자동 전투 중에도 메뉴에서 다시 끌 수 있습니다")
                    time_module.sleep(0.5)  # 자동 전투 안내 시간 단축 (1.5→0.5초)
                    return self._auto_battle_action(character, party, enemies)
                time_module.sleep(0.3)  # 기본 대기 시간 단축 (1.0→0.3초)
            elif choice == 7:  # 실시간 상태
                # 📊 전투 로그를 먼저 표시
                print("\n" + "="*70)
                print(f"📋 최근 전투 로그 (턴 {getattr(self, '_turn_count', 0)})")
                print("="*70)
                if hasattr(self, '_recent_combat_logs') and self._recent_combat_logs:
                    for i, log in enumerate(self._recent_combat_logs[-10:], 1):  # 최근 10개 로그 표시
                        print(f"{i:2d}. {log}")
                else:
                    print("• 아직 전투 로그가 없습니다.")
                print("="*70)
                
                # 캐스팅 중인 캐릭터 표시
                casting_chars = []
                for char in party + enemies:
                    if hasattr(char, 'casting_skill') and char.casting_skill:
                        casting_chars.append(char)
                
                if casting_chars:
                    print("\n🔮 [CASTING DEBUG] 캐스팅 중인 캐릭터:")
                    print("=" * 60)
                    for char in casting_chars:
                        casting_skill = getattr(char, 'casting_skill', None)
                        cast_progress = getattr(char, 'cast_progress', 0)
                        cast_time = getattr(char, 'cast_time', 100)
                        atb_gauge = getattr(char, 'atb_gauge', 0)
                        casting_start_atb = getattr(char, 'casting_start_atb', 0)
                        casting_duration = getattr(char, 'casting_duration', 0)
                        is_casting = getattr(char, 'is_casting', False)
                        
                        # 스킬 이름 추출
                        if isinstance(casting_skill, dict):
                            skill_name = casting_skill.get('name', '알 수 없는 스킬')
                            skill_cast_time = casting_skill.get('cast_time', cast_time)
                        elif hasattr(casting_skill, 'name'):
                            skill_name = casting_skill.name
                            skill_cast_time = getattr(casting_skill, 'cast_time', cast_time)
                        elif isinstance(casting_skill, str):
                            skill_name = casting_skill
                            skill_cast_time = cast_time
                        else:
                            skill_name = '알 수 없는 스킬'
                            skill_cast_time = cast_time
                        
                        # 캐스팅 진행률 계산 - 여러 방법 시도 (수정된 로직)
                        progress_percent_1 = 0  # 방법 1
                        progress_percent_2 = 0  # 방법 2  
                        progress_percent_3 = 0  # 방법 3
                        progress_percent_4 = 0  # 방법 4 (수정된 ATB 계산)
                        
                        # 방법 1: cast_progress 기반
                        if cast_progress > 0 and skill_cast_time > 0:
                            progress_percent_1 = (cast_progress / skill_cast_time) * 100
                        
                        # 방법 2: ATB 기반 (casting_start_atb 속성이 있는 경우) - 원래 로직
                        if casting_duration > 0:
                            atb_progress = atb_gauge - casting_start_atb
                            progress_percent_2 = (atb_progress / casting_duration) * 100
                        
                        # 방법 3: ATB 게이지 직접 계산 (0-1000 범위)
                        if atb_gauge > 0:
                            progress_percent_3 = (atb_gauge / 1000) * 100
                        
                        # 방법 4: 수정된 ATB 계산 (캐스팅 시작 후 경과 시간 기반)
                        if casting_duration > 0:
                            if casting_start_atb > atb_gauge:
                                # ATB가 리셋된 경우: 0부터 시작으로 가정
                                progress_percent_4 = (atb_gauge / casting_duration) * 100
                            else:
                                # 정상적인 ATB 증가: 시작점부터 계산
                                atb_progress = atb_gauge - casting_start_atb
                                progress_percent_4 = (atb_progress / casting_duration) * 100
                        
                        # 디버그 출력 (방법 4 추가)
                        print(f"🔮 [CASTING DEBUG] {char.name}: ATB={atb_gauge}, Start={casting_start_atb}, Duration={casting_duration}, Progress={cast_progress:.2f} ({progress_percent_1:.0f}%)")
                        print(f"🔮 CASTING INFO: {char.name} (ATB:{atb_gauge}-{casting_start_atb}={atb_gauge-casting_start_atb}/{casting_duration})")
                        print(f"🔍 [FULL DEBUG] {char.name}:")
                        print(f"   is_casting: {is_casting}")
                        print(f"   atb_gauge: {atb_gauge}")
                        print(f"   casting_start_atb: {casting_start_atb}")
                        print(f"   casting_duration: {casting_duration}")
                        print(f"   cast_progress: {cast_progress}")
                        print(f"   cast_time: {cast_time}")
                        print(f"   skill_cast_time: {skill_cast_time}")
                        print(f"   skill_name: {skill_name}")
                        print(f"   진행률 방법1 (cast_progress/skill_cast_time): {progress_percent_1:.2f}%")
                        print(f"   진행률 방법2 (ATB-Start/Duration): {progress_percent_2:.2f}%")
                        print(f"   진행률 방법3 (ATB/1000): {progress_percent_3:.2f}%")
                        print(f"   진행률 방법4 (수정된ATB계산): {progress_percent_4:.2f}%")
                        print(f"   캐스팅 스킬 객체: {type(casting_skill).__name__} - {casting_skill}")
                        print(f"   🎯 ATB 상태 분석: {'ATB리셋됨' if casting_start_atb > atb_gauge else 'ATB정상증가'}")
                        print("-" * 60)
                
                # ATB 실시간 업데이트 표시
                print(f"\n⏰ ATB 게이지 상태:")
                print("-" * 40)
                for char in party + enemies:
                    if char.is_alive:
                        atb_gauge = getattr(char, 'atb_gauge', 0)
                        max_atb = getattr(char, 'max_atb', 1000)
                        atb_percent = int((atb_gauge / max_atb) * 100)
                        gauge_bar = "█" * (atb_percent // 10) + "▌" * (1 if atb_percent % 10 >= 5 else 0)
                        gauge_bar = gauge_bar.ljust(10, " ")
                        print(f"  {char.name}: [{gauge_bar}] {atb_percent}%")
                
                # 키 버퍼 클리어 후 키 대기
                self.keyboard.clear_input_buffer()
                self.keyboard.wait_for_key(f"\n{get_color('YELLOW')}엔터를 눌러 계속...{get_color('RESET')}")
                # 전투 후 키 버퍼 클리어 (키 홀드 방지)
                self.keyboard.clear_input_buffer()
                
                # 그 다음에 상세 메뉴 표시
                self.show_detailed_combat_status(character, party, enemies)
            elif choice == 8:  # 전투 도움말
                from .tutorial import show_combat_help
                show_combat_help()
                # 도움말도 버퍼를 완전히 클리어
                self.buffered_display.clear_buffer()
            elif choice is None:  # 취소
                continue
            else:
                print("잘못된 선택입니다.")
                
        # 턴 종료 후 전투 상태 체크
        if self.check_battle_end(party, enemies):
            return self.determine_winner(party, enemies)
        
        # 턴 카운터 증가
        self._turn_count += 1
        
        # 턴 종료 로그 표시
        print("\n" + "="*70)
        print(f"📋 전투 로그 (턴 {self._turn_count})")
        print("="*70)
        # 여기에 최근 전투 로그들이 표시됩니다
        if hasattr(self, '_recent_combat_logs') and self._recent_combat_logs:
            for log in self._recent_combat_logs[-7:]:  # 최근 7개 로그 표시 (더 많이)
                print(f"• {log}")
        else:
            print("• 턴이 완료되었습니다.")
        print("="*70)
        
        # 전투 로그 확인 시간 제공 (자동화)
        import time
        print("\n⏰ 전투 로그 확인 중... (0.2초)")
        time.sleep(0.2)  # 0.5초에서 0.2초로 더 단축
        
        # 🎯 중요: 실제 행동 완료 여부 확인 후 반환 (취소 카운터 리셋/출력 제한 포함)
        action_completed_flag = getattr(self, '_last_action_completed', False)
        
        if action_completed_flag:
            self._last_action_completed = False  # 플래그 리셋
            # 취소 카운터 리셋
            try:
                cid = id(character)
                if cid in self._cancel_counters:
                    del self._cancel_counters[cid]
                if cid in self._cancel_last_time:
                    del self._cancel_last_time[cid]
            except Exception:
                pass
            print(f"✅ {character.name}의 행동이 완료되었습니다!")
            return "action_completed"  # 행동 완료 신호
        else:
            # 출력 빈도 제한: 2초 내 반복 취소는 메시지 생략
            cid = id(character)
            now = time_module.time()
            last = self._cancel_last_time.get(cid, 0)
            if (now - last) > 2.0:
                print(f"❌ {character.name}의 행동이 취소되었습니다.")
                self._cancel_last_time[cid] = now
            # 취소 카운터 증가
            self._cancel_counters[cid] = self._cancel_counters.get(cid, 0) + 1
            return None  # 행동 취소 신호
    
    def _auto_battle_action(self, character: Character, party: List[Character], enemies: List[Character]):
        """자동 전투 행동 로직"""
        import time
        
        from .error_logger import get_error_logger, log_debug
        logger = get_error_logger()
        log_debug("자동전투", f"{character.name} 자동 행동 중...")
        time_module.sleep(self.auto_battle_delay)
        
        # 생존한 적들
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return None
        
        # 전략적 상황 분석
        party_hp_avg = sum(ally.current_hp / ally.max_hp for ally in party if ally.is_alive) / len([ally for ally in party if ally.is_alive])
        character_hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
        character_class = getattr(character, 'character_class', '전사')
        
        # 전투 역할별 우선순위 결정
        action_priority = self._analyze_tactical_situation(character, party, enemies)
        
        for action_type in action_priority:
            if action_type == "emergency_heal" and character_hp_ratio < 0.2:
                print(f"💚 응급 치료: HP가 {character_hp_ratio*100:.1f}%로 위험")
                if self._try_auto_healing(character, party):
                    # 게이지 변화 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)
                    return None
                    
            elif action_type == "support_heal" and character_class in ["신관", "바드"] and party_hp_avg < 0.6:
                print(f"💚 지원 치료: 파티 평균 HP {party_hp_avg*100:.1f}%")
                if self._try_auto_support_skills(character, party, enemies):
                    # 게이지 변화 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)
                    return None
                    
            elif action_type == "ultimate_attack" and character.current_mp >= 20:
                target = self._select_smart_target(alive_enemies, "ultimate", character)
                print(f"💫 궁극기 사용: {target.name if target else '대상 없음'}")
                if self._try_auto_ultimate_skill(character, party, enemies):
                    # 게이지 변화 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)
                    return None
                
                if self._try_auto_ultimate_skill(character, party, enemies):
                    # 게이지 변화 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)
                    return None
                    
            elif action_type == "tactical_skill":
                print(f"⚡ 전술 스킬 사용: MP {character.current_mp} 활용 (MP 0 기본 공격 포함)")
                if self._try_auto_tactical_skill(character, party, enemies):
                    # 게이지 변화 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)
                    return None
                    
            elif action_type == "hp_attack" and character.brave_points >= 400:
                target = self._select_smart_target(alive_enemies, "hp_attack", character)
                if target:
                    print(f"💀 HP 공격: {target.name} (BRV: {character.brave_points})")
                    self.execute_hp_attack(character, target)
                    # 게이지 변화 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)
                    return None
                    
            elif action_type == "brv_attack":
                target = self._select_smart_target(alive_enemies, "brv_attack", character)
                if target:
                    print(f"⚔️ BRV 공격: {target.name}")
                    self.execute_brave_attack(character, target)
                    # 게이지 변화 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)
                    return None
        
        # 기본 행동 (모든 우선순위가 실패한 경우)
        target = self._select_smart_target(alive_enemies, "brv_attack", character)
        if target:
            print(f"⚔️ 기본 Brave 공격: {target.name}")
            self.execute_brave_attack(character, target)
        
        # 게이지 변화 확인 시간 제공 (단축)
        import time
        time.sleep(0.5)
        return None
    
    def _analyze_tactical_situation(self, character: Character, party: List[Character], enemies: List[Character]) -> list:
        """전술적 상황 분석하여 행동 우선순위 결정"""
        character_class = getattr(character, 'character_class', '전사')
        character_hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
        party_critical = len([ally for ally in party if ally.is_alive and (ally.current_hp / ally.max_hp) < 0.3])
        enemy_count = len([e for e in enemies if e.is_alive])
        
        # 직업별 역할 기반 우선순위
        if character_class in ["신관", "바드"]:  # 지원형
            if party_critical >= 2:
                return ["emergency_heal", "support_heal", "tactical_skill", "brv_attack", "hp_attack"]
            else:
                return ["support_heal", "tactical_skill", "ultimate_attack", "hp_attack", "brv_attack"]
                
        elif character_class in ["아크메이지", "정령술사", "네크로맨서"]:  # 마법사형
            if enemy_count >= 3:
                return ["ultimate_attack", "tactical_skill", "hp_attack", "emergency_heal", "brv_attack"]
            else:
                return ["tactical_skill", "ultimate_attack", "hp_attack", "emergency_heal", "brv_attack"]
        
        elif character_class == "도적":  # 도적 - 독 중심 전략
            # 독 상태인 적이 있는지 확인
            poisoned_enemies = [e for e in enemies if getattr(e, 'is_poisoned', False)]
            
            if len(poisoned_enemies) >= 2:  # 독에 걸린 적이 2명 이상
                # 독 촉진 전략 - HP 공격으로 독 터뜨리기
                return ["hp_attack", "ultimate_attack", "tactical_skill", "emergency_heal", "brv_attack"]
            elif len(poisoned_enemies) == 1:  # 독에 걸린 적이 1명
                # 독 확산 전략 - 더 많은 적에게 독 부여
                return ["tactical_skill", "brv_attack", "hp_attack", "ultimate_attack", "emergency_heal"]
            else:  # 독에 걸린 적이 없음
                # 독 부여 우선 전략
                return ["brv_attack", "tactical_skill", "ultimate_attack", "hp_attack", "emergency_heal"]
                
        elif character_class in ["전사", "성기사", "용기사"]:  # 탱커형
            if character_hp_ratio < 0.4:
                return ["emergency_heal", "tactical_skill", "hp_attack", "brv_attack", "ultimate_attack"]
            else:
                return ["hp_attack", "tactical_skill", "brv_attack", "ultimate_attack", "emergency_heal"]
                
        else:  # 딜러형 (궁수, 암살자 등)
            return ["ultimate_attack", "hp_attack", "tactical_skill", "emergency_heal", "brv_attack"]
    
    def _try_auto_support_skills(self, character: Character, party: List[Character], enemies: List[Character]) -> bool:
        """지원 스킬 자동 사용 (회복, 버프 스킬)"""
        character_class = getattr(character, 'character_class', '전사')
        skills = self.skill_db.get_skills(character_class)
        
        if not skills:
            return False
            
        # 지원형 스킬 우선 선택
        support_skills = [skill for skill in skills 
                         if skill.get("mp_cost", 0) <= character.current_mp
                         and skill.get("name") in ["치유", "신의 심판", "영혼의 노래", "회복", "축복"]]
        
        if support_skills:
            best_skill = support_skills[0]  # 첫 번째 사용 가능한 지원 스킬
            targets = self._select_skill_targets(best_skill, character, party, enemies)
            if targets:
                print(f"✨ 지원 스킬: {best_skill.get('name', '스킬')}")
                self._execute_skill_immediately(best_skill, character, targets)
                return True
        
        return False
    
    def _try_auto_ultimate_skill(self, character: Character, party: List[Character], enemies: List[Character]) -> bool:
        """궁극기 자동 사용"""
        character_class = getattr(character, 'character_class', '전사')
        skills = self.skill_db.get_skills(character_class)
        
        if not skills:
            return False
            
        # 궁극기 우선 선택 - enum과 문자열 모두 지원
        ultimate_skills = []
        for skill in skills:
            if skill.get("mp_cost", 0) <= character.current_mp:
                skill_type = skill.get("type")
                # enum과 문자열 모두 처리
                if hasattr(skill_type, 'value'):
                    type_str = skill_type.value
                else:
                    type_str = str(skill_type)
                
                if type_str == "ULTIMATE" or "ULTIMATE" in type_str:
                    ultimate_skills.append(skill)
        
        if ultimate_skills:
            best_skill = max(ultimate_skills, key=lambda s: s.get("hp_power", 0) + s.get("brv_power", 0))
            
            targets = self._select_skill_targets(best_skill, character, party, enemies)
            if targets:
                print(f"💫 궁극기: {best_skill.get('name', '궁극기')}")
                self._execute_skill_immediately(best_skill, character, targets)
                return True
        
        return False
    
    def _try_auto_tactical_skill(self, character: Character, party: List[Character], enemies: List[Character]) -> bool:
        """전술적 스킬 자동 사용 - 새로운 특성 시스템 대응"""
        character_class = getattr(character, 'character_class', '전사')
        skills = self.skill_db.get_skills(character_class)
        
        if not skills:
            return False
            
        # 캐릭터의 현재 상태 분석
        hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
        mp_ratio = character.current_mp / character.max_mp if character.max_mp > 0 else 0
        party_hp_avg = sum(c.current_hp / c.max_hp for c in party if c.is_alive) / len([c for c in party if c.is_alive])
        
        # 사용 가능한 스킬 필터링 (우선순위 체계 적용)
        tactical_skills = []
        for skill in skills:
            mp_cost = skill.get("mp_cost", 0)
            if mp_cost <= character.current_mp:
                skill_type = skill.get("type")
                skill_name = skill.get("name", "")
                
                # enum과 문자열 모두 처리
                if hasattr(skill_type, 'value'):
                    type_str = skill_type.value
                else:
                    type_str = str(skill_type)
                
                # 새로운 우선순위 체계 (2025년 8월 6일 업데이트):
                # 1. 응급 회복 (HP 20% 이하)
                # 2. 지원 회복 (파티 HP 60% 이하)  
                # 3. 궁극기 (MP 20 이상)
                # 4. 전술 스킬 (MP 12 이상)
                # 5. HP 공격 (BRV 400 이상)
                # 6. BRV 공격 (기본 행동)
                
                priority_score = 0
                
                # 응급 치료 최우선 (생존이 우선)
                if hp_ratio <= 0.2 and ("회복" in skill_name or "치유" in skill_name or "힐" in skill_name):
                    priority_score = 100
                    
                # 파티 지원 치료 (팀 생존성)
                elif party_hp_avg <= 0.6 and ("치유" in skill_name or "회복" in skill_name or "보호" in skill_name):
                    priority_score = 90
                    
                # 궁극기 (충분한 MP가 있을 때만)
                elif type_str == "ULTIMATE" and mp_ratio >= 0.4:
                    priority_score = 80
                    
                # 전술 스킬 (MP 12 이상) - 특성별 조정
                elif mp_cost >= 12 and type_str in ["SPECIAL", "BRV_HP_ATTACK", "DEBUFF"]:
                    priority_score = 70
                    
                    # 광전사: HP 낮을수록 공격 스킬 우선도 증가
                    if character_class == "광전사" and hp_ratio <= 0.15:
                        if "공격" in skill_name or "타격" in skill_name:
                            priority_score = 85  # 궁극기 직전 우선순위
                    
                    # 차원술사: 회피/방어 스킬 우선도 증가  
                    elif character_class == "차원술사" and party_hp_avg <= 0.7:
                        if "차원" in skill_name or "도약" in skill_name or "방어" in skill_name:
                            priority_score = 85
                    
                # HP 공격 (충분한 BRV가 있을 때)
                elif type_str == "HP_ATTACK" and getattr(character, 'brave_points', 0) >= 400:
                    priority_score = 60
                    
                    # 광전사: HP 낮을 때 HP 공격 우선도 증가
                    if character_class == "광전사" and hp_ratio <= 0.15:
                        priority_score = 75
                    
                # BRV 공격 및 기본 공격 (항상 사용 가능)
                elif type_str in ["BRV_ATTACK", "HP_ATTACK", "BRV_HP_ATTACK"] or mp_cost == 0:
                    priority_score = 50
                    
                    # 기본 공격들도 특성에 따라 조정
                    if character_class == "차원술사" and mp_cost == 0:
                        priority_score = 55  # 차원술사는 기본 공격도 조금 더 우선
                
                # 우선순위가 있는 스킬만 추가
                if priority_score > 0:
                    skill['priority_score'] = priority_score
                    tactical_skills.append(skill)
        
        if tactical_skills:
            # 우선순위 순으로 정렬
            tactical_skills.sort(key=lambda s: s.get('priority_score', 0), reverse=True)
            best_skill = tactical_skills[0]
            
            # 상황별 추가 최적화
            enemy_count = len([e for e in enemies if e.is_alive])
            if enemy_count >= 3:
                # 다수 적 상대: 광역 스킬 우선
                area_skills = [s for s in tactical_skills if "전체" in s.get("name", "") or "광역" in s.get("name", "")]
                if area_skills:
                    best_skill = area_skills[0]
                    
            # 특성별 특수 행동 처리 (2025년 8월 6일 업데이트)
            character_traits = getattr(character, 'active_traits', [])
            for trait in character_traits:
                trait_name = getattr(trait, 'name', '') if hasattr(trait, 'name') else trait.get('name', '')
                
                # === 광전사 특성별 AI 전술 ===
                if trait_name == "혈투의 광기":
                    # HP 15% 이하일 때 극도로 공격적
                    if hp_ratio <= 0.15:
                        attack_skills = [s for s in tactical_skills if "공격" in s.get("name", "") or "타격" in s.get("name", "")]
                        if attack_skills:
                            attack_skills[0]['priority_score'] = 95  # 최고 우선순위
                            best_skill = attack_skills[0]
                            
                elif trait_name == "불굴의 의지":
                    # HP 낮을 때 방어적 스킬보다 공격 우선
                    if hp_ratio <= 0.3:
                        hp_attack_skills = [s for s in tactical_skills if s.get("type") == "HP_ATTACK"]
                        if hp_attack_skills:
                            best_skill = hp_attack_skills[0]
                            
                elif trait_name == "광전사의 분노":
                    # 적이 많을 때 광역 공격 우선
                    if enemy_count >= 2:
                        area_skills = [s for s in tactical_skills if "전체" in s.get("name", "") or "광역" in s.get("name", "")]
                        if area_skills:
                            best_skill = area_skills[0]
                
                # === 차원술사 특성별 AI 전술 ===
                elif trait_name == "차원 도약":
                    # 회피 중심: 방어적 스킬과 이동 우선
                    if party_hp_avg < 0.7:
                        evasion_skills = [s for s in tactical_skills if "차원" in s.get("name", "") or "도약" in s.get("name", "")]
                        if evasion_skills:
                            best_skill = evasion_skills[0]
                            
                elif trait_name == "공간 왜곡":
                    # 적 무력화 스킬 우선
                    debuff_skills = [s for s in tactical_skills if s.get("type") == "DEBUFF" or "무력화" in s.get("name", "")]
                    if debuff_skills:
                        best_skill = debuff_skills[0]
                        
                elif trait_name == "차원의 방패":
                    # 파티 보호 중심
                    if party_hp_avg < 0.6:
                        support_skills = [s for s in tactical_skills if "보호" in s.get("name", "") or "방어" in s.get("name", "")]
                        if support_skills:
                            best_skill = support_skills[0]
                            
                elif trait_name == "시공간 조작":
                    # 전장 컨트롤 스킬 우선
                    control_skills = [s for s in tactical_skills if "조작" in s.get("name", "") or "시간" in s.get("name", "")]
                    if control_skills:
                        best_skill = control_skills[0]
                        
                elif trait_name == "차원술사의 직감":
                    # 상황 판단 후 최적 스킬 선택
                    if hp_ratio < 0.3:
                        # 위험 상황: 회복/방어 우선
                        defensive_skills = [s for s in tactical_skills if "회복" in s.get("name", "") or "치유" in s.get("name", "")]
                        if defensive_skills:
                            best_skill = defensive_skills[0]
                    elif enemy_count >= 3:
                        # 다수 적: 광역 공격
                        area_skills = [s for s in tactical_skills if "전체" in s.get("name", "") or "광역" in s.get("name", "")]
                        if area_skills:
                            best_skill = area_skills[0]
                
            targets = self._select_skill_targets(best_skill, character, party, enemies)
            if targets:
                skill_type = best_skill.get("type")
                type_str = skill_type.value if hasattr(skill_type, 'value') else str(skill_type)
                priority = best_skill.get('priority_score', 0)
                
                from .error_logger import get_error_logger
                logger = get_error_logger()
                logger.log_debug("AI전술", f"AI 전술 (우선순위 {priority}): {best_skill.get('name', '스킬')} ({type_str})")
                self._execute_skill_immediately(best_skill, character, targets)
                return True
        
        return False
    
    def _select_smart_target(self, enemies: List[Character], attack_type: str, attacker: Character = None) -> Character:
        """지능적 타겟 선택 (특성별 최적화)"""
        if not enemies:
            return None
        
        selected_target = None
        
        # 공격자의 특성 확인
        attacker_traits = []
        if attacker:
            attacker_traits = getattr(attacker, 'active_traits', [])
            attacker_class = getattr(attacker, 'character_class', '')
        
        if attack_type == "hp_attack":
            # 광전사: 가장 약한 적을 처치 우선
            if any(getattr(trait, 'name', trait.get('name', '')) == "혈투의 광기" for trait in attacker_traits):
                # HP가 가장 낮은 적 우선 (처치 확률 극대화)
                selected_target = min(enemies, key=lambda e: e.current_hp)
            else:
                # 기본: 체력이 낮은 적을 우선 (처치 가능성 높임)
                selected_target = min(enemies, key=lambda e: e.current_hp)
            
        elif attack_type == "brv_attack":
            # 차원술사: 가장 위험한 적(BRV 높은 적) 우선
            if any(getattr(trait, 'name', trait.get('name', '')) == "차원술사의 직감" for trait in attacker_traits):
                # BRV가 높은 적을 우선 타겟 (위험도 감소)
                selected_target = max(enemies, key=lambda e: getattr(e, 'brave_points', 0))
            else:
                # 기본: Brave가 높은 적을 우선 (위험도 감소)
                selected_target = max(enemies, key=lambda e: getattr(e, 'brave_points', 0))
            
        elif attack_type == "debuff":
            # 차원술사: 가장 강한 적을 무력화
            if any(getattr(trait, 'name', trait.get('name', '')) == "공간 왜곡" for trait in attacker_traits):
                # 공격력이 가장 높은 적 우선
                selected_target = max(enemies, key=lambda e: getattr(e, 'physical_attack', 0) + getattr(e, 'magic_attack', 0))
            else:
                # 기본: 체력 비율이 높은 적
                selected_target = max(enemies, key=lambda e: e.current_hp / e.max_hp if e.max_hp > 0 else 0)
                
        else:
            # 기본: 체력 비율이 가장 낮은 적
            selected_target = min(enemies, key=lambda e: e.current_hp / e.max_hp if e.max_hp > 0 else 0)
        
        return selected_target
        
        # 모든 적의 상태 정보 수집
        for enemy in enemies:
            hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
            selection_info["target_scores"][enemy.name] = {
                "HP": f"{enemy.current_hp}/{enemy.max_hp}",
                "HP_비율": f"{hp_ratio*100:.1f}%",
                "BRV": getattr(enemy, 'brave_points', 0),
                "선택됨": enemy == selected_target
            }
            selection_info["threat_assessment"][enemy.name] = {
                "상태": "위험" if hp_ratio < 0.3 else "보통" if hp_ratio < 0.7 else "건강",
                "위험도": "높음" if getattr(enemy, 'brave_points', 0) > 300 else "보통"
            }
        return selected_target
    
    def _try_auto_healing(self, character: Character, party: List[Character]) -> bool:
        """개선된 자동 회복 시도"""
        from .items import ItemDatabase, ItemType
        
        # 1. 회복 스킬 우선 시도
        character_class = getattr(character, 'character_class', '전사')
        if character_class in ["신관", "바드"] and character.current_mp >= 8:
            skills = self.skill_db.get_skills(character_class)
            heal_skills = [skill for skill in skills 
                          if skill.get("mp_cost", 0) <= character.current_mp
                          and "치유" in skill.get("name", "")]
            if heal_skills:
                targets = self._select_skill_targets(heal_skills[0], character, party, [])
                if targets:
                    print(f"✨ 자동 치유 스킬: {heal_skills[0].get('name')}")
                    self._execute_skill_immediately(heal_skills[0], character, targets)
                    return True
        
        # 2. 회복 아이템 사용
        item_db = ItemDatabase()
        heal_items = []
        for item_name, quantity in character.inventory.get_items_list():
            item = item_db.get_item(item_name)
            if item and item.item_type == ItemType.CONSUMABLE and "heal" in item.effects:
                heal_items.append((item, quantity))
        
        # 가장 효과적인 회복 아이템 선택
        if heal_items:
            best_item = max(heal_items, key=lambda x: x[0].stats.get("healing_power", 0))
            if self.use_item_on_target(character, best_item[0], character):
                print(f"🧪 자동 회복: {best_item[0].name} 사용")
                
                # 🎯 힐링 어그로 이벤트 생성
                if hasattr(self, 'aggro_system'):
                    healer_name = getattr(character, 'name', str(character))
                    heal_amount = best_item[0].stats.get("healing_power", 50)
                    
                    # 모든 적에게 힐러의 어그로 추가
                    if hasattr(self, '_current_enemies'):
                        for enemy in self._current_enemies:
                            if getattr(enemy, 'is_alive', True):
                                enemy_name = getattr(enemy, 'name', str(enemy))
                                aggro_event = create_healing_aggro(healer_name, heal_amount)
                                self.aggro_system.add_aggro_event(enemy_name, aggro_event)
                
                return True
        return False
    
    def _try_auto_skill(self, character: Character, party: List[Character], enemies: List[Character]) -> bool:
        """개선된 자동 스킬 사용 시도"""
        character_class = getattr(character, 'character_class', '전사')
        skills = self.skill_db.get_skills(character_class)
        
        if not skills:
            return False
            
        # 상황별 스킬 우선순위
        enemy_count = len([e for e in enemies if e.is_alive])
        party_low_hp = len([ally for ally in party if ally.is_alive and (ally.current_hp / ally.max_hp) < 0.5])
        
        # 지원이 필요한 상황
        if party_low_hp >= 2 and character_class in ["신관", "바드"]:
            support_skills = [skill for skill in skills 
                             if skill.get("mp_cost", 0) <= character.current_mp
                             and any(word in skill.get("name", "") for word in ["치유", "회복", "축복", "노래"])]
            if support_skills:
                best_skill = support_skills[0]
                targets = self._select_skill_targets(best_skill, character, party, enemies)
                if targets:
                    print(f"🚑 긴급 지원: {best_skill.get('name', '스킬')}")
                    self._execute_skill_immediately(best_skill, character, targets)
                    return True
        
        # 공격 스킬 선택
        attack_skills = [skill for skill in skills 
                        if skill.get("mp_cost", 0) <= character.current_mp
                        and skill.get("type") in ["HP_ATTACK", "BRV_HP_ATTACK", "BRV_ATTACK", "ULTIMATE"]]
        
        if attack_skills:
            if enemy_count >= 3:
                # 다수 적: 광역 스킬 우선
                area_skills = [s for s in attack_skills if "전체" in s.get("description", "")]
                best_skill = area_skills[0] if area_skills else max(attack_skills, key=lambda s: s.get("hp_power", 0))
            else:
                # 소수 적: 최고 화력 스킬
                best_skill = max(attack_skills, key=lambda s: s.get("hp_power", 0) + s.get("brv_power", 0))
                
            targets = self._select_skill_targets(best_skill, character, party, enemies)
            if targets:
                print(f"⚔️ 전략적 스킬: {best_skill.get('name', '스킬')}")
                self._execute_skill_immediately(best_skill, character, targets)
                return True
        
        return False
    
    def _select_auto_target(self, enemies: List[Character], character: Character = None, attack_type: str = "normal") -> Character:
        """개선된 자동 타겟 선택 (직업별 전략 포함)"""
        if not enemies:
            return None
        
        character_class = getattr(character, 'character_class', '') if character else ''
        
        # 도적 전용 타겟 선택 로직
        if character_class == "도적":
            if attack_type == "hp_attack":
                # HP 공격: 독에 걸린 적 우선 (독 촉진 효과)
                poisoned_enemies = [e for e in enemies if getattr(e, 'is_poisoned', False)]
                if poisoned_enemies:
                    # 독에 걸린 적 중 독 턴이 많이 남은 적 우선
                    return max(poisoned_enemies, key=lambda e: getattr(e, 'poison_turns', 0))
                else:
                    # 독에 걸린 적이 없으면 체력이 낮은 적
                    return min(enemies, key=lambda e: e.current_hp)
                    
            elif attack_type == "brv_attack":
                # BRV 공격: 독에 걸리지 않은 적 우선 (독 확산)
                non_poisoned = [e for e in enemies if not getattr(e, 'is_poisoned', False)]
                if non_poisoned:
                    # 독에 안 걸린 적 중 체력이 높은 적 우선
                    return max(non_poisoned, key=lambda e: e.current_hp)
                else:
                    # 모두 독에 걸렸으면 브레이브가 높은 적
                    return max(enemies, key=lambda e: getattr(e, 'brave_points', 0))
                    
            elif attack_type == "ultimate_attack":
                # 궁극기: 적이 많이 모인 곳 또는 독에 걸린 적들
                poisoned_enemies = [e for e in enemies if getattr(e, 'is_poisoned', False)]
                if len(poisoned_enemies) >= 2:
                    # 독에 걸린 적이 많으면 그 중 하나 (전체 공격으로 독 폭발)
                    return poisoned_enemies[0]
                else:
                    # 체력이 높은 적 (궁극기로 큰 피해)
                    return max(enemies, key=lambda e: e.current_hp)
            
        # 기존 일반 타겟 선택 로직
        target_scores = []
        for enemy in enemies:
            score = 0
            hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
            brave_points = getattr(enemy, 'brave_points', 0)
            
            # 체력이 낮을수록 높은 점수 (처치 가능성)
            score += (1 - hp_ratio) * 100
            
            # Brave가 높을수록 높은 점수 (위험도)
            score += min(brave_points / 1000, 50)
            
            # 특수 적 타입 보너스
            if hasattr(enemy, 'character_class'):
                if enemy.character_class in ["아크메이지", "신관"]:  # 지원형 우선 처치
                    score += 30
                elif enemy.character_class in ["궁수", "암살자"]:  # 원거리 딜러 우선
                    score += 20
            
            target_scores.append((enemy, score))
        
        # 가장 높은 점수의 적 선택
        return max(target_scores, key=lambda x: x[1])[0]
    
    def _select_enemy_target(self, party: List[Character], enemy: Character = None) -> Character:
        """적 AI의 타겟 선택 (동적 어그로 시스템 전용)"""
        if not party:
            return None
        
        # 🎯 어그로 시스템 기반 타겟 선정 우선
        if enemy and hasattr(self, 'aggro_system'):
            enemy_name = getattr(enemy, 'name', str(enemy))
            
            # 어그로 기반 주요 타겟 선정
            aggro_target_name = self.aggro_system.get_primary_target(enemy_name, party)
            
            if aggro_target_name:
                # 어그로 타겟 찾기
                for member in party:
                    if getattr(member, 'name', '') == aggro_target_name:
                        # 어그로 분포 표시 (개발 모드에서만)
                        if self.aggro_system.show_aggro_messages:
                            aggro_dist = self.aggro_system.get_aggro_distribution(enemy_name)
                            top_3 = sorted(aggro_dist.items(), key=lambda x: x[1], reverse=True)[:3]
                            print(f"   📊 현재 어그로 상위 3명: {', '.join([f'{name}({aggro:.0f})' for name, aggro in top_3])}")
                        
                        return member
        
        # 어그로 시스템 실패 시 첫 번째 아군 선택 (백업)
        print(f"⚠️ 어그로 시스템 사용 불가, 첫 번째 아군 타겟팅")
        return party[0]
        print(f"⚠️ 적이 독술사 {selected_target.name}을(를) 집중 공격합니다!")
        
        return selected_target
                
    def trait_activation_menu(self, character: Character) -> bool:
        """특성 활성화 메뉴 - 수정된 버전"""
        if not hasattr(character, 'active_traits') or not character.active_traits:
            print(f"\n❌ {character.name}은(는) 활성화할 수 있는 특성이 없습니다.")
            # 🎯 특성 메뉴 중 애니메이션 일시정지
            gauge_animator = get_gauge_animator()
            gauge_animator.pause_animations()
            if not self.ai_game_mode:  # 클래식 모드가 아닐 때만 입력 대기
                # 키 버퍼 클리어 후 키 대기
                self.keyboard.clear_input_buffer()
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            else:
                time.sleep(0.3)  # 클래식 모드에서는 짧은 대기
            gauge_animator.resume_animations()
            return False
        
        # 액티브 타입 특성만 필터링 - 더 관대한 검사
        active_traits = []
        for trait in character.active_traits:
            trait_type = None
            if hasattr(trait, 'trait_type'):
                trait_type = trait.trait_type
            elif hasattr(trait, 'effect_type'):
                trait_type = trait.effect_type
            elif isinstance(trait, dict):
                trait_type = trait.get('trait_type') or trait.get('effect_type')
            
            # active 타입이거나 특성 타입이 정의되지 않은 경우 포함
            if trait_type == "active" or trait_type is None:
                active_traits.append(trait)
        
        if not active_traits:
            print(f"\n❌ {character.name}은(는) 활성화할 수 있는 액티브 특성이 없습니다.")
            print(f"💡 패시브 특성은 항상 활성화되어 있습니다.")
            print(f"🔍 현재 특성 목록:")
            for i, trait in enumerate(character.active_traits):
                trait_name = getattr(trait, 'name', trait.get('name', f'특성 {i+1}') if isinstance(trait, dict) else f'특성 {i+1}')
                trait_type = getattr(trait, 'trait_type', getattr(trait, 'effect_type', trait.get('trait_type', trait.get('effect_type', '알 수 없음')) if isinstance(trait, dict) else '알 수 없음'))
                print(f"   - {trait_name} ({trait_type})")
            # 🎯 특성 메뉴 중 애니메이션 일시정지
            gauge_animator = get_gauge_animator()
            gauge_animator.pause_animations()
            if not self.ai_game_mode:  # 클래식 모드가 아닐 때만 입력 대기
                self.keyboard.clear_input_buffer()  # 키 홀드 방지
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            else:
                time.sleep(0.3)  # 클래식 모드에서는 짧은 대기
            gauge_animator.resume_animations()
            return False
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            trait_options = []
            trait_descriptions = []
            
            for trait in active_traits:
                if hasattr(trait, 'name'):
                    trait_name = trait.name
                    trait_desc = getattr(trait, 'description', '특수 효과')
                else:
                    trait_name = trait.get('name', '알 수 없는 특성')
                    trait_desc = trait.get('description', '특수 효과')
                
                # 특성이 이미 활성화되어 있는지 체크
                is_active = False
                if hasattr(trait, 'is_active'):
                    is_active = trait.is_active
                elif isinstance(trait, dict):
                    is_active = trait.get('is_active', False)
                
                if is_active:
                    trait_options.append(f"🟢 {trait_name} (활성화됨)")
                    trait_descriptions.append(f"{trait_desc} - 이미 활성화된 상태")
                else:
                    trait_options.append(f"⚪ {trait_name}")
                    trait_descriptions.append(f"{trait_desc} - 클릭하여 활성화")
            
            menu = create_simple_menu(f"🌟 {character.name}의 특성 활성화", trait_options, trait_descriptions, clear_screen=False)
            choice = menu.run()
            
            if choice is None or choice == -1:  # 취소
                return False
            elif 0 <= choice < len(active_traits):
                selected_trait = active_traits[choice]
                
                # 특성이 이미 활성화되어 있는지 체크
                is_active = False
                if hasattr(selected_trait, 'is_active'):
                    is_active = selected_trait.is_active
                elif isinstance(selected_trait, dict):
                    is_active = selected_trait.get('is_active', False)
                
                if is_active:
                    print(f"💡 {selected_trait.get('name', selected_trait.name)}은(는) 이미 활성화되어 있습니다.")
                    return False
                else:
                    # 특성 활성화
                    if hasattr(selected_trait, 'is_active'):
                        selected_trait.is_active = True
                    elif isinstance(selected_trait, dict):
                        selected_trait['is_active'] = True
                    
                    trait_name = selected_trait.get('name', selected_trait.name) if isinstance(selected_trait, dict) else selected_trait.name
                    print(f"✨ {character.name}이(가) '{trait_name}' 특성을 활성화했습니다!")
                    
                    # 특성별 특수 효과 적용
                    self._apply_trait_activation_effect(character, selected_trait)
                    
                    return True
            else:
                print("잘못된 선택입니다.")
                return False
                
        except Exception as e:
            print(f"❌ 특성 활성화 오류: {e}")
            return False
    
    def _apply_trait_activation_effect(self, character: Character, trait):
        """특성 활성화 효과 적용"""
        trait_name = trait.get('name') if isinstance(trait, dict) else trait.name
        
        if trait_name == "동물 변신":
            # 동물 변신 특성 - 형태 선택
            forms = ["🐺 늑대 (공격+30%)", "🐻 곰 (방어+30%)", "🦅 독수리 (회피+25%)"]
            form_descriptions = [
                "공격력이 30% 증가합니다",
                "방어력이 30% 증가합니다", 
                "회피율이 25% 증가합니다"
            ]
            
            try:
                from .cursor_menu_system import create_simple_menu
                form_menu = create_simple_menu(f"🌟 {character.name}의 변신 형태 선택", forms, form_descriptions, clear_screen=False)
                form_choice = form_menu.run()
                
                if form_choice == 0:  # 늑대
                    character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + int(character.physical_attack * 0.3)
                    print(f"🐺 {character.name}이(가) 늑대로 변신했습니다! 공격력이 증가합니다!")
                elif form_choice == 1:  # 곰
                    character.temp_defense_bonus = getattr(character, 'temp_defense_bonus', 0) + int(character.physical_defense * 0.3)
                    print(f"🐻 {character.name}이(가) 곰으로 변신했습니다! 방어력이 증가합니다!")
                elif form_choice == 2:  # 독수리
                    character.temp_dodge_bonus = getattr(character, 'temp_dodge_bonus', 0) + 25
                    print(f"🦅 {character.name}이(가) 독수리로 변신했습니다! 회피율이 증가합니다!")
                    
            except ImportError:
                # 폴백: 자동으로 늑대 형태
                character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + int(character.physical_attack * 0.3)
                print(f"🐺 {character.name}이(가) 늑대로 변신했습니다! 공격력이 증가합니다!")
        
        else:
            # 다른 특성들의 기본 효과
            print(f"✨ {trait_name} 특성 효과가 적용되었습니다!")
    
    def skill_menu(self, character: Character, party: List[Character], enemies: List[Character]) -> bool:
        """스킬 메뉴 - 실제 스킬 시스템"""
        # 캐릭터 클래스 가져오기
        character_class = getattr(character, 'character_class', '전사')
        all_skills = self.skill_db.get_skills(character_class)
        
        # 기본공격 제외 (mp_cost가 0인 스킬들 필터링)
        skills = [skill for skill in all_skills if skill.get("mp_cost", 0) > 0]
        
        if not skills:
            print(f"{character.name}은(는) 사용할 수 있는 스킬이 없습니다.")
            print("방어를 선택합니다.")
            self.defend_action(character)
            return True
        
        print(f"\n{character.name}의 스킬 (MP: {character.current_mp}/{character.max_mp}):")
        print("─" * 50)

        try:
            from .cursor_menu_system import create_simple_menu
            
            # 스킬 옵션과 설명 준비
            skill_options = []
            skill_descriptions = []
            available_skills = []
            
            for skill in skills:
                base_mp_cost = skill.get("mp_cost", 0)
                actual_mp_cost = self.trait_integrator.apply_skill_cost_reduction(character, base_mp_cost, skill)
                cast_time = skill.get("cast_time", 0)
                cast_info = f" [캐스트:{cast_time}%]" if cast_time > 0 else ""
                skill_name = skill.get('name', '스킬')
                skill_type = skill.get('type', '')
                
                # MP 비용 표시 (실제 비용과 원래 비용이 다르면 할인 표시)
                if actual_mp_cost < base_mp_cost:
                    mp_display = f"MP:{actual_mp_cost} (원래:{base_mp_cost})"
                else:
                    mp_display = f"MP:{actual_mp_cost}"
                
                # 궁극기 조건 체크
                is_ultimate = (skill_type == "ULTIMATE" or "궁극기" in str(skill_type) or 
                             "궁극" in skill_name or actual_mp_cost >= 20)
                
                can_use_skill = character.current_mp >= actual_mp_cost
                ultimate_condition_met = True
                ultimate_message = ""
                free_ultimate_available = False
                
                if is_ultimate:
                    # 궁극기 조건 체크 (수정됨 - 무료 사용 버그 수정)
                    try:
                        from .new_skill_system import check_ultimate_conditions
                        ultimate_condition_met, ultimate_message = check_ultimate_conditions(character, skill_name)
                        
                        # 🚫 무료 궁극기 사용 비활성화 (조건 충족 시에만 사용 가능)
                        free_ultimate_available = False  # 무료 궁극기 완전 비활성화
                        
                    except ImportError:
                        # 함수가 없으면 기본 MP 조건만 체크
                        ultimate_condition_met = True
                
                # 스킬 사용 가능 여부 판단 (수정됨)
                if is_ultimate:
                    # 궁극기의 경우: 조건 충족 AND MP 충분해야 사용 가능
                    if ultimate_condition_met and can_use_skill:
                        skill_options.append(f"✨ {skill_name} ({mp_display}){cast_info}")
                        skill_descriptions.append(skill.get('description', ''))
                        available_skills.append(skill)
                    elif not ultimate_condition_met:
                        skill_options.append(f"❌ {skill_name} ({mp_display}){cast_info} [조건 미달성]")
                        skill_descriptions.append(f"{skill.get('description', '')} - {ultimate_message}")
                        available_skills.append(None)
                    elif not can_use_skill:
                        skill_options.append(f"🚫 {skill_name} ({mp_display}){cast_info} [MP 부족]")
                        skill_descriptions.append(f"{skill.get('description', '')} - MP 부족")
                        available_skills.append(None)
                    else:
                        # 예상치 못한 상황
                        skill_options.append(f"⚠️ {skill_name} ({mp_display}){cast_info} [사용 불가]")
                        skill_descriptions.append(f"{skill.get('description', '')} - 사용 조건 미충족")
                        available_skills.append(None)
                else:
                    # 일반 스킬의 경우: MP만 충분하면 사용 가능
                    if can_use_skill:
                        skill_options.append(f"✨ {skill_name} ({mp_display}){cast_info}")
                        skill_descriptions.append(skill.get('description', ''))
                        available_skills.append(skill)
                    else:
                        skill_options.append(f"🚫 {skill_name} ({mp_display}){cast_info} [MP 부족]")
                        skill_descriptions.append(f"{skill.get('description', '')} - MP 부족")
                        available_skills.append(None)
            
            if not any(skill for skill in available_skills if skill is not None):
                print("사용 가능한 스킬이 없습니다. 방어를 선택합니다.")
                self.defend_action(character)
                return True
            
            menu = create_simple_menu(
                f"✨ {character.name}의 스킬 선택", 
                skill_options, 
                skill_descriptions, 
                clear_screen=True  # 🖥️ 스킬 메뉴 클리어로 중첩 방지
            )
            choice = menu.run()
            
            if choice is None or choice == -1:  # 취소
                return False
            elif 0 <= choice < len(available_skills):
                selected_skill = available_skills[choice]
                
                if selected_skill is None:  # MP 부족한 스킬 선택
                    print(f"MP가 부족합니다!")
                    return False
                
                # 대상 선택
                targets = self._select_skill_targets(selected_skill, character, party, enemies)
                if targets is None:
                    return False  # 취소된 경우
                
                # 빈 리스트가 반환된 경우 (유효한 대상이 없음)
                if isinstance(targets, list) and len(targets) == 0:
                    target_type = selected_skill.get("target", "single_enemy")
                    if hasattr(target_type, 'value'):
                        target_type_str = target_type.value
                    else:
                        target_type_str = str(target_type).lower()
                    
                    if target_type_str in ["죽은아군1명", "dead_ally"]:
                        print("❌ 부활시킬 대상이 없어 스킬을 취소합니다.")
                    else:
                        print("❌ 유효한 대상이 없어 스킬을 취소합니다.")
                    return False
                
                # 스킬 실행 - 캐스트 타임 적용
                cast_time = selected_skill.get("cast_time", 0)
                
                if cast_time > 0:
                    # 캐스트 타임이 있는 스킬 - ATB 시스템 사용
                    print(f"✨ {character.name}이(가) {selected_skill.get('name', '스킬')} 캐스팅을 시작합니다! [캐스트:{cast_time}%]")
                    
                    # MP 소모는 캐스팅 시작 시 (애니메이션 적용)
                    old_mp = character.current_mp
                    base_mp_cost = selected_skill.get("mp_cost", 0)
                    actual_mp_cost = self.trait_integrator.apply_skill_cost_reduction(character, base_mp_cost, selected_skill)
                    character.current_mp -= actual_mp_cost
                    if hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
                        self.animate_value_change(character, 'MP', old_mp, character.current_mp, self._current_party, self._current_enemies)
                    
                    # 캐스팅 시작
                    import time
                    current_time = getattr(self, 'battle_time', time.time())
                    
                    # 캐스팅 관련 속성이 없으면 초기화
                    if not hasattr(character, 'casting_skill'):
                        character.casting_skill = None
                        character.casting_targets = None
                        character.casting_start_time = None
                        character.casting_duration = None
                        character.is_casting = False
                    
                    # cast_time을 ATB 스케일로 변환 
                    # cast_time이 퍼센트라면 (예: 20% = 20), ATB 단위로 변환
                    # 🎯 올바른 스케일링: 20% = 2000 ATB units (ATB_READY_THRESHOLD의 20%)
                    if cast_time <= 100:  # 퍼센트 값으로 가정
                        atb_cast_time = int(cast_time * self.ATB_READY_THRESHOLD / 100)  # 20% → 2000 ATB units
                    else:  # 이미 ATB 단위라면
                        atb_cast_time = cast_time
                    
                    if hasattr(character, 'start_casting'):
                        character.start_casting(selected_skill, targets, current_time, atb_cast_time)
                    else:
                        # 폴백: 직접 속성 설정
                        character.casting_skill = selected_skill
                        character.casting_targets = targets
                        character.casting_start_time = current_time
                        character.casting_duration = atb_cast_time
                        character.casting_cast_time = atb_cast_time  # ATB 기반 캐스팅용 (호환성)
                        character.is_casting = True
                        character.casting_start_atb = character.atb_gauge  # 🎯 현재 ATB에서 시작
                        character.casting_progress = 0  # 초기 진행도 0
                        # 캐스팅 시작 시 ATB는 그대로 유지 (0으로 리셋하지 않음)
                else:
                    # 즉시 시전 스킬
                    self._execute_skill_immediately(selected_skill, character, targets)
                
                return True
            else:
                print("잘못된 선택입니다.")
                return False
                
        except Exception as e:
            print(f"❌ 스킬 메뉴 오류: {e}")
            # 폴백: 방어 선택
            self.defend_action(character)
            return True
    
    def _execute_skill_immediately(self, skill, character, targets):
        """스킬 즉시 실행 (캐스트 타임 없는 스킬용)"""
        # 액션 실행 플래그 설정
        self.is_action_executing = True
        
        # MP 소모 애니메이션 적용
        old_mp = character.current_mp
        base_mp_cost = skill.get("mp_cost", 0)
        actual_mp_cost = self.trait_integrator.apply_skill_cost_reduction(character, base_mp_cost, skill)
        
        # MP 감소 처리
        character.current_mp = max(0, character.current_mp - actual_mp_cost)
        new_mp = character.current_mp
        
        # MP 감소 (자동 애니메이션 트리거)
        if actual_mp_cost > 0:
            print(f"🔮 {character.name}이(가) {actual_mp_cost} MP 소모!")
            # character.current_mp는 이미 위에서 설정됨
        
        # 실제 스킬 효과 적용
        print(f"✨ {character.name}이(가) {skill.get('name', '스킬')}을(를) 사용했습니다!")
        
        # 🎮 스킬 사용 진동 (강한 진동 - MP 소모 스킬)
        if self.vibration_enabled and actual_mp_cost > 0:
            self.input_manager.vibrate_heavy()
        elif self.vibration_enabled:  # MP 0 기본 공격도 중간 진동
            self.input_manager.vibrate_medium()
        
        # 🔊 스킬 사용 SFX 재생
        self._play_skill_sfx(skill)
        
        # 시각 효과
        if hasattr(self, 'visualizer') and self.visualizer:
            self.visualizer.show_skill_effect(character, skill.get('name', '스킬'), EffectType.SKILL)
        
        # 실제 스킬 효과 적용
        self._apply_skill_effects(skill, character, targets)
        
        # 🎯 스킬 사용 완료 - ATB는 자연스럽게 유지됨 (다음 턴을 위해)
        
        # 스킬 사용 후 전투 종료 체크 (팡파레 재생 포함)
        if hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
            # 🎯 승리 체크 전 애니메이션 완료 대기
            gauge_animator = get_gauge_animator()
            if gauge_animator.is_processing:
                print(f"\n{get_color('CYAN')}⏳ 스킬 효과 적용 중...{get_color('RESET')}")
                while gauge_animator.is_processing:
                    time_module.sleep(0.1)
                time_module.sleep(0.5)  # 추가 확인 시간
            
            if self.check_battle_end(self._current_party, self._current_enemies):
                winner = self.determine_winner(self._current_party, self._current_enemies)
                if winner:  # 승리 시 팡파레 재생
                    try:
                        print(f"\n{get_color('BRIGHT_CYAN')}전투가 종료되었습니다!{get_color('RESET')}")
                        
                        # 🎮 승리 진동 패턴
                        if self.vibration_enabled:
                            self.input_manager.vibrate_victory()
                        
                        victory_played = False
                        
                        # 1순위: audio_system 사용
                        if hasattr(self, 'audio_system') and self.audio_system:
                            try:
                                self.audio_system.play_sfx("victory")
                                print("🎵 승리 팡파레 재생! (audio_system)")
                                victory_played = True
                            except Exception as e:
                                print(f"⚠️ audio_system 팡파레 실패: {e}")
                        
                        # 2순위: sound_manager 사용
                        if not victory_played and hasattr(self, 'sound_manager') and self.sound_manager:
                            try:
                                self.sound_manager.play_sfx("victory")
                                print("🎵 승리 팡파레 재생! (sound_manager)")
                                victory_played = True
                            except Exception as e:
                                print(f"⚠️ sound_manager 팡파레 실패: {e}")
                        
                        # 3순위: 직접 오디오 시스템 접근
                        if not victory_played:
                            try:
                                from .ffvii_sound_system import get_ffvii_sound_system
                                audio_mgr = get_ffvii_sound_system()
                                if audio_mgr:
                                    audio_mgr.play_sfx("victory")
                                    print("🎵 승리 팡파레 재생! (direct)")
                                    victory_played = True
                            except Exception as e:
                                print(f"⚠️ 직접 오디오 접근 실패: {e}")
                        
                        if not victory_played:
                            print("⚠️ 승리 팡파레를 재생할 수 없습니다.")
                    except Exception as e:
                        print(f"⚠️ 승리 팡파레 재생 실패: {e}")
                return winner  # 전투 종료 신호 반환
        
        # 스킬 사용 후 딜레이 추가
        self.add_action_pause(f"🎯 스킬 '{skill.get('name', '스킬')}' 효과 적용 완료!")
        
        # 액션 실행 완료, 플래그 해제
        self.is_action_executing = False
    
    def complete_casting(self, character):
        """캐스팅 완료 처리 - 게임 종료 시 예외처리 포함"""
        try:
            if not hasattr(character, 'casting_skill') or not character.casting_skill:
                return
            
            # 캐릭터가 전투불능 상태인지 체크
            if not character.is_alive:
                print(f"⚠️ {character.name}이(가) 전투불능 상태로 캐스팅이 중단되었습니다.")
                self._clear_casting_state(character)
                return
            
            skill = character.casting_skill
            targets = getattr(character, 'casting_targets', [])
            
            # 대상들이 여전히 유효한지 체크
            valid_targets = []
            for target in targets:
                if hasattr(target, 'is_alive') and target.is_alive:
                    valid_targets.append(target)
                else:
                    print(f"⚠️ 대상 {getattr(target, 'name', '알 수 없음')}이(가) 유효하지 않아 제외됩니다.")
            
            # 유효한 대상이 없으면 캐스팅 취소
            if not valid_targets and skill.get('target') not in ['self', '자신']:
                print(f"⚠️ 유효한 대상이 없어 {character.name}의 {skill.get('name', '스킬')} 캐스팅이 취소되었습니다.")
                self._clear_casting_state(character)
                return
            
            print(f"✨ {character.name}의 {skill.get('name', '스킬')} 캐스팅이 완료되었습니다!")
            
            # 🎮 캐스팅 완료 진동 (강한 진동)
            if self.vibration_enabled:
                self.input_manager.vibrate_heavy()
            
            # MP 소모 처리 및 애니메이션
            old_mp = character.current_mp
            base_mp_cost = skill.get("mp_cost", 0)
            actual_mp_cost = self.trait_integrator.apply_skill_cost_reduction(character, base_mp_cost, skill)
            
            # MP 감소 처리
            character.current_mp = max(0, character.current_mp - actual_mp_cost)
            new_mp = character.current_mp
            
            # MP 감소 (자동 애니메이션 트리거)
            if actual_mp_cost > 0:
                print(f"🔮 {character.name}이(가) {actual_mp_cost} MP 소모!")
                # character.current_mp는 이미 위에서 설정됨
            
            # 🔊 스킬 사용 SFX 재생
            self._play_skill_sfx(skill)
            
            # 시각 효과
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.show_skill_effect(character, skill.get('name', '스킬'), EffectType.SKILL)
            
            # 실제 스킬 효과 적용
            self._apply_skill_effects(skill, character, valid_targets if valid_targets else targets)
            
            # 🎯 캐스팅 완료 - ATB는 자연스럽게 유지됨 (다음 턴을 위해)
            
            # 캐스팅 완료 후 전투 종료 체크 (중복 방지)
            if hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
                # 🎯 승리 체크 전 애니메이션 완료 대기
                gauge_animator = get_gauge_animator()
                if gauge_animator.is_processing:
                    print(f"\n{get_color('CYAN')}⏳ 스킬 효과 적용 중...{get_color('RESET')}")
                    while gauge_animator.is_processing:
                        time_module.sleep(0.1)
                    time_module.sleep(0.5)  # 추가 확인 시간
                
                if self.check_battle_end(self._current_party, self._current_enemies):
                    # 스킬 효과 결과 확인 시간 제공 (단축)
                    import time
                    time.sleep(0.5)
                    # 전투 종료만 체크하고 승리 처리는 다른 곳에서 담당
                    return True  # 전투 종료 신호만 반환
            
            # 캐스팅 완료 후 스킬 효과 확인 시간 제공 (단축)
            import time
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ 캐스팅 완료 중 오류 발생: {e}")
        finally:
            # 캐스팅 상태 초기화 (항상 실행)
            self._clear_casting_state(character)
        
        # 정상 완료 시 None 반환 (턴 종료)
        return None
    
    def _clear_casting_state(self, character):
        """캐스팅 상태 완전 초기화"""
        try:
            character.casting_skill = None
            character.casting_targets = None
            character.casting_start_time = None
            character.casting_duration = None
            character.is_casting = False
        except Exception as e:
            print(f"⚠️ 캐스팅 상태 초기화 중 오류: {e}")
    
    def _clear_all_casting(self, all_characters):
        """모든 캐릭터의 캐스팅 상태 중단"""
        for character in all_characters:
            if getattr(character, 'is_casting', False):
                print(f"⚠️ 전투 종료로 인해 {character.name}의 캐스팅이 중단되었습니다.")
                self._clear_casting_state(character)
    
    def _select_skill_targets(self, skill, caster, party: List[Character], enemies: List[Character]):
        """스킬 대상 선택"""
        target_type = skill.get("target", "single_enemy")
        
        # TargetType enum을 문자열로 변환
        if hasattr(target_type, 'value'):
            target_type_str = target_type.value
        else:
            target_type_str = str(target_type).lower()
        
        # 타겟 타입별 처리
        if target_type_str in ["자신", "self"]:
            return [caster]
        elif target_type_str in ["아군전체", "all_allies"]:
            return [char for char in party if char.is_alive]
        elif target_type_str in ["적전체", "all_enemies"]:
            return [enemy for enemy in enemies if enemy.is_alive]
        elif target_type_str in ["아군1명", "single_ally"]:
            alive_allies = [char for char in party if char.is_alive]
            if not alive_allies:
                return []
            
            try:
                # 🔄 화면 버퍼링 해결을 위한 강제 새로고침 - PowerShell 스택 현상 방지
                import sys
                import os
                if hasattr(sys.stdout, 'flush'):
                    sys.stdout.flush()
                # PowerShell에서 화면 클리어로 인한 스택 현상 방지
                # if os.name == 'nt':  # Windows
                #     os.system('cls')
                # else:
                #     os.system('clear')
                
                # cursor_menu_system을 여기서 import (오류 발생 가능)
                cursor_menu_available = False
                try:
                    from .cursor_menu_system import create_simple_menu
                    cursor_menu_available = True
                except Exception as import_error:
                    print(f"🔄 커서 메뉴 시스템 로드 실패: {import_error}")
                    cursor_menu_available = False
                
                if cursor_menu_available:
                    # 커서 메뉴 사용
                    options = []
                    descriptions = []
                    
                    for ally in alive_allies:
                        status = ""
                        if ally.current_hp < ally.max_hp:
                            status += f" (HP: {ally.current_hp}/{ally.max_hp})"
                        if hasattr(ally, 'wounds') and ally.wounds > 0:
                            status += f" [WOUND: {ally.wounds}]"
                        
                        option_text = f"{ally.name}{status}"
                        desc = f"레벨: {ally.level} | 클래스: {ally.character_class}"
                        
                        options.append(option_text)
                        descriptions.append(desc)
                    
                    try:
                        menu = create_simple_menu("🎯 스킬 대상 선택", options, descriptions, clear_screen=False)
                        result = menu.run()
                        
                        if result is None:  # Q키로 취소
                            return None
                        
                        if 0 <= result < len(alive_allies):
                            return [alive_allies[result]]
                        
                        return None
                    except Exception as menu_error:
                        print(f"🔄 메뉴 실행 오류: {menu_error}")
                        cursor_menu_available = False
                
                # 폴백: 키보드 입력 방식 (커서 메뉴 실패 시)
                if not cursor_menu_available:
                    print(f"🔄 기본 입력 모드로 전환합니다.")
                    
                    # 아군이 1명인 경우 자동 선택
                    if len(alive_allies) == 1:
                        print(f"🎯 자동 선택: {alive_allies[0].name}")
                        return [alive_allies[0]]
                    
                    # 아군이 여러 명인 경우 번호 선택
                    print("\n🎯 스킬 대상을 선택하세요:")
                    for i, ally in enumerate(alive_allies, 1):
                        status = ""
                        if ally.current_hp < ally.max_hp:
                            status += f" (HP: {ally.current_hp}/{ally.max_hp})"
                        if hasattr(ally, 'wounds') and ally.wounds > 0:
                            status += f" [WOUND: {ally.wounds}]"
                        print(f"  {i}. {ally.name}{status}")
                    print(f"  0. 취소")
                    
                    try:
                        print("\n번호를 입력하세요:", end=" ")
                        # 키 버퍼 클리어 후 키 대기
                        self.keyboard.clear_input_buffer()
                        choice_str = self.keyboard.get_input().strip()
                        choice = int(choice_str)
                        
                        if choice == 0:
                            return None
                        elif 1 <= choice <= len(alive_allies):
                            return [alive_allies[choice - 1]]
                        else:
                            print("❌ 잘못된 선택입니다.")
                            return None
                    except ValueError:
                        print("❌ 숫자를 입력하세요.")
                        return None
                
            except Exception as general_error:
                print(f"🚨 아군 대상 선택 중 전체 오류가 발생했습니다: {general_error}")
                
                # 안전한 최종 폴백: 사용자 확인 후 첫 번째 아군 선택
                if alive_allies:
                    print(f"⚠️ 오류 복구를 위해 첫 번째 아군 '{alive_allies[0].name}'을(를) 자동 선택하려고 합니다.")
                    try:
                        confirm = input("계속하시겠습니까? (Enter=예, q=아니오): ").strip().lower()
                        if confirm == 'q':
                            print("❌ 대상 선택이 취소되었습니다.")
                            return None
                        else:
                            print(f"✅ {alive_allies[0].name}을(를) 선택했습니다.")
                            return [alive_allies[0]]
                    except Exception:
                        print(f"🚨 입력 처리 실패. 강제로 {alive_allies[0].name}을(를) 선택합니다.")
                        return [alive_allies[0]]
                else:
                    print("❌ 사용 가능한 아군이 없습니다.")
                    return None
                # 폴백: 기존 방식
                print("\n대상을 선택하세요:")
                for i, ally in enumerate(alive_allies, 1):
                    status = ""
                    if ally.current_hp < ally.max_hp:
                        status += f" (HP: {ally.current_hp}/{ally.max_hp})"
                    if hasattr(ally, 'wounds') and ally.wounds > 0:
                        status += f" [WOUND: {ally.wounds}]"
                    print(f"{i}. {ally.name}{status}")
                print("0. 취소")
                
                try:
                    choice_str = self.keyboard.get_key()
                    choice = int(choice_str) - 1
                    if choice == -1:
                        return None
                    elif 0 <= choice < len(alive_allies):
                        return [alive_allies[choice]]
                    else:
                        print("잘못된 선택입니다.")
                        return None
                except ValueError:
                    print("숫자를 입력하세요.")
                    return None
                
        elif target_type_str in ["적1명", "single_enemy"]:
            alive_enemies = [enemy for enemy in enemies if enemy.is_alive]
            if not alive_enemies:
                return []
            
            try:
                # 🔄 화면 버퍼링 해결을 위한 강제 새로고침 - PowerShell 스택 현상 방지
                import sys
                import os
                if hasattr(sys.stdout, 'flush'):
                    sys.stdout.flush()
                # PowerShell에서 화면 클리어로 인한 스택 현상 방지
                # if os.name == 'nt':  # Windows
                #     os.system('cls')
                # else:
                #     os.system('clear')
                
                # cursor_menu_system을 여기서 import (오류 발생 가능)
                cursor_menu_available = False
                try:
                    from .cursor_menu_system import create_simple_menu
                    cursor_menu_available = True
                except Exception as import_error:
                    print(f"🔄 커서 메뉴 시스템 로드 실패: {import_error}")
                    cursor_menu_available = False
                
                if cursor_menu_available:
                    # 커서 메뉴 사용
                    options = []
                    descriptions = []
                    
                    for enemy in alive_enemies:
                        status = f" (HP: {enemy.current_hp}/{enemy.max_hp}"
                        if hasattr(enemy, 'is_broken') and enemy.is_broken:
                            status += ", BREAK"
                        status += ")"
                        
                        option_text = f"{enemy.name}{status}"
                        desc = f"상태: {'브레이크' if hasattr(enemy, 'is_broken') and enemy.is_broken else '정상'}"
                        
                        options.append(option_text)
                        descriptions.append(desc)
                    
                    try:
                        menu = create_simple_menu("⚔️ 공격 대상 선택", options, descriptions, clear_screen=False)
                        result = menu.run()
                        
                        if result is None:  # Q키로 취소
                            return None
                        
                        if 0 <= result < len(alive_enemies):
                            return [alive_enemies[result]]
                        
                        return None
                    except Exception as menu_error:
                        print(f"🔄 메뉴 실행 오류: {menu_error}")
                        cursor_menu_available = False
                
                # 폴백: 키보드 입력 방식 (커서 메뉴 실패 시)
                if not cursor_menu_available:
                    print(f"🔄 기본 입력 모드로 전환합니다.")
                    
                    # 적이 1명인 경우 자동 선택
                    if len(alive_enemies) == 1:
                        print(f"⚔️ 자동 선택: {alive_enemies[0].name}")
                        return [alive_enemies[0]]
                    
                    # 적이 여러 명인 경우 번호 선택
                    print("\n⚔️ 공격할 대상을 선택하세요:")
                    for i, enemy in enumerate(alive_enemies, 1):
                        status = f" (HP: {enemy.current_hp}/{enemy.max_hp}"
                        if hasattr(enemy, 'is_broken') and enemy.is_broken:
                            status += ", BREAK"
                        status += ")"
                        print(f"  {i}. {enemy.name}{status}")
                    print(f"  0. 취소")
                    
                    try:
                        print("\n번호를 입력하세요:", end=" ")
                        # 키 버퍼 클리어 후 키 대기
                        self.keyboard.clear_input_buffer()
                        choice_str = self.keyboard.get_input().strip()
                        choice = int(choice_str)
                        
                        if choice == 0:
                            return None
                        elif 1 <= choice <= len(alive_enemies):
                            return [alive_enemies[choice - 1]]
                        else:
                            print("❌ 잘못된 선택입니다.")
                            return None
                    except ValueError:
                        print("❌ 숫자를 입력하세요.")
                        return None
                
            except Exception as general_error:
                print(f"🚨 적 대상 선택 중 전체 오류가 발생했습니다: {general_error}")
                
                # 안전한 최종 폴백: 사용자 확인 후 첫 번째 적 선택
                if alive_enemies:
                    print(f"⚠️ 오류 복구를 위해 첫 번째 적 '{alive_enemies[0].name}'을(를) 자동 선택하려고 합니다.")
                    try:
                        confirm = input("계속하시겠습니까? (Enter=예, q=아니오): ").strip().lower()
                        if confirm == 'q':
                            print("❌ 대상 선택이 취소되었습니다.")
                            return None
                        else:
                            print(f"✅ {alive_enemies[0].name}을(를) 선택했습니다.")
                            return [alive_enemies[0]]
                    except Exception:
                        print(f"🚨 입력 처리 실패. 강제로 {alive_enemies[0].name}을(를) 선택합니다.")
                        return [alive_enemies[0]]
                else:
                    print("❌ 사용 가능한 적이 없습니다.")
                    return None
                
        elif target_type_str in ["죽은아군1명", "dead_ally"]:
            dead_allies = [char for char in party if not char.is_alive]
            if not dead_allies:
                print("부활시킬 대상이 없습니다.")
                return []
            
            print("\n부활시킬 대상을 선택하세요:")
            for i, ally in enumerate(dead_allies, 1):
                print(f"{i}. {ally.name} (사망)")
            print("0. 취소")
            
            try:
                choice_str = self.keyboard.get_key()
                choice = int(choice_str) - 1
                if choice == -1:
                    return None
                elif 0 <= choice < len(dead_allies):
                    return [dead_allies[choice]]
                else:
                    print("잘못된 선택입니다.")
                    return None
            except ValueError:
                print("숫자를 입력하세요.")
                return None
        
        return []
        
    def item_menu(self, character: Character, party: List[Character]) -> bool:
        """아이템 메뉴 - 실제 인벤토리 시스템 연동"""
        try:
            from .items import ItemDatabase, ItemType
            
            print(f"\n💼 {character.name}의 아이템:")
            print("="*50)
            
            # 인벤토리 아이템 목록 표시
            available_items = []
            item_db = ItemDatabase()
            
            try:
                items_list = character.inventory.get_items_list()
                
                for item_name, quantity in items_list:
                    item = item_db.get_item(item_name)
                    
                    if item and item.item_type == ItemType.CONSUMABLE:
                        available_items.append((item, quantity))
                        
            except Exception as e:
                print(f"❌ 인벤토리 접근 오류: {e}")
                return False
            
            if not available_items:
                print("❌ 사용할 수 있는 소모품이 없습니다.")
                print("💡 힌트: 상점에서 회복 포션이나 얼음탄을 구매해보세요!")
                return False
            
            print("사용할 아이템을 선택하세요:")
            print("-" * 50)
            
            try:
                from .cursor_menu_system import create_simple_menu
                
                options = []
                descriptions = []
                
                for item, quantity in available_items:
                    effect_desc = item.get_effect_description() if hasattr(item, 'get_effect_description') else item.description
                    option_text = f"{item.name} ({quantity}개)"
                    desc_text = f"{effect_desc}"
                    if hasattr(item, 'value') and item.value > 0:
                        desc_text += f" | 가치: {item.value}골드"
                    
                    options.append(option_text)
                    descriptions.append(desc_text)
                
                menu = create_simple_menu("⚔️ 전투 아이템 사용", options, descriptions, clear_screen=True)  # 🖥️ 아이템 메뉴 클리어
                choice = menu.run()
                
                if choice == -1:  # 취소
                    return False
                
                if 0 <= choice < len(available_items):
                    selected_item, quantity = available_items[choice]
                    
                    # 대상 선택 (회복 아이템인 경우)
                    if any(effect in selected_item.effects for effect in ["heal", "field_rest", "full_rest", "mana_restore", "full_mana"]):
                        target = self.select_heal_target(party)
                        if target:
                            return self.use_item_on_target(character, selected_item, target)
                    elif "revive" in selected_item.effects:
                        # 부활 아이템 - 죽은 캐릭터 선택
                        target = self.select_dead_target(party)
                        if target:
                            return self.use_item_on_target(character, selected_item, target)
                    elif any(effect in selected_item.effects for effect in ["damage_enemy", "damage_all_enemies", "blind_enemies"]):
                        # 공격 아이템 - 적 선택 또는 전체 공격
                        if not hasattr(self, '_current_enemies') or not self._current_enemies:
                            print("❌ 현재 적 정보가 없습니다!")
                            return False
                        return self.use_attack_item(character, selected_item, party, self._current_enemies)
                    else:
                        # 즉시 사용 아이템 (버프, 강화 등)
                        return self.use_item_on_target(character, selected_item, character)
                
                return False
                
            except ImportError:
                # 폴백: 기존 방식
                for i, (item, quantity) in enumerate(available_items, 1):
                    effect_desc = item.get_effect_description() if hasattr(item, 'get_effect_description') else item.description
                    print(f"{i}. {item.name} ({quantity}개)")
                    print(f"   📝 {effect_desc}")
                    if hasattr(item, 'value') and item.value > 0:
                        print(f"   💰 가치: {item.value}골드")
                    print()
                    
                print(f"{len(available_items)+1}. 취소")
                
                try:
                    choice_input = input("선택하세요: ").strip()
                    choice = int(choice_input) - 1
                    
                    if 0 <= choice < len(available_items):
                        selected_item, quantity = available_items[choice]
                        
                        # 대상 선택 로직 (동일)
                        if any(effect in selected_item.effects for effect in ["heal", "field_rest", "full_rest", "mana_restore", "full_mana"]):
                            target = self.select_heal_target(party)
                            if target:
                                return self.use_item_on_target(character, selected_item, target)
                        elif "revive" in selected_item.effects:
                            target = self.select_dead_target(party)
                            if target:
                                return self.use_item_on_target(character, selected_item, target)
                        elif any(effect in selected_item.effects for effect in ["damage_enemy", "damage_all_enemies", "blind_enemies"]):
                            if not hasattr(self, '_current_enemies') or not self._current_enemies:
                                print("❌ 현재 적 정보가 없습니다!")
                                return False
                            return self.use_attack_item(character, selected_item, party, self._current_enemies)
                        else:
                            return self.use_item_on_target(character, selected_item, character)
                    elif choice == len(available_items):
                        return False
                except ValueError:
                    pass
                    
                print("잘못된 선택입니다.")
                return False
                
        except Exception as e:
            print(f"❌ 아이템 메뉴 오류: {e}")
            return False
    
    def select_dead_target(self, party: List[Character]) -> Character:
        """부활 대상 선택 - 커서 방식"""
        dead_party = [p for p in party if not p.is_alive]
        if not dead_party:
            print("부활시킬 수 있는 캐릭터가 없습니다.")
            return None
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            options = []
            descriptions = []
            
            for member in dead_party:
                option_text = f"{member.name} (사망 상태)"
                desc = f"레벨: {member.level} | 클래스: {member.character_class}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("💀 부활 대상 선택", options, descriptions, clear_screen=False)
            result = menu.run()
            
            if result is None:  # Q키로 취소
                return None
            
            if 0 <= result < len(dead_party):
                return dead_party[result]
            
            return None
            
        except ImportError:
            # 폴백: 기존 방식
            print("\n부활시킬 대상을 선택하세요:")
            for i, member in enumerate(dead_party, 1):
                print(f"{i}. {member.name} (사망 상태)")
            
            try:
                choice_str = self.keyboard.get_key()
                choice = int(choice_str) - 1
                if 0 <= choice < len(dead_party):
                    return dead_party[choice]
            except ValueError:
                pass
            
            return None
    
    def select_heal_target(self, party: List[Character]) -> Character:
        """치료 대상 선택 - 커서 방식"""
        alive_party = [p for p in party if p.is_alive]
        if not alive_party:
            return None
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            options = []
            descriptions = []
            
            for member in alive_party:
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                status = "양호" if hp_ratio > 0.7 else "부상" if hp_ratio > 0.3 else "위험"
                
                option_text = f"{member.name} (HP: {member.current_hp}/{member.max_hp})"
                desc = f"상태: {status} | HP: {hp_ratio:.1%}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("🎯 치료 대상 선택", options, descriptions, clear_screen=False)
            result = menu.run()
            
            if result is None:  # Q키로 취소
                return None
            
            if 0 <= result < len(alive_party):
                return alive_party[result]
            
            return None
            
        except ImportError:
            # 폴백: 기존 방식
            print("\n대상을 선택하세요:")
            for i, member in enumerate(alive_party, 1):
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                status = "양호" if hp_ratio > 0.7 else "부상" if hp_ratio > 0.3 else "위험"
                print(f"{i}. {member.name} (HP: {member.current_hp}/{member.max_hp} - {status})")
            
            try:
                choice_str = self.keyboard.get_key()
                choice = int(choice_str) - 1
                if 0 <= choice < len(alive_party):
                    return alive_party[choice]
            except ValueError:
                pass
            
            return None
    
    def use_attack_item(self, user: Character, item, party: List[Character], enemies: List[Character]) -> bool:
        """공격 아이템 사용 (폭탄 등)"""
        # 액션 실행 플래그 설정
        self.is_action_executing = True
        
        print(f"\n💥 {user.name}이(가) {item.name}을(를) 사용합니다!")
        
        # 살아있는 적들만 대상으로
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            print("❌ 공격할 적이 없습니다!")
            self.is_action_executing = False
            return False
        
        damage_amount = item.stats.get("damage_amount", 50)
        
        if "damage_all_enemies" in item.effects:
            # 전체 공격
            print(f"💥💥 {item.name} 대폭발!")
            for enemy in alive_enemies:
                actual_damage = max(1, damage_amount)
                enemy.current_hp = max(0, enemy.current_hp - actual_damage)
                print(f"💀 {enemy.name}이(가) {actual_damage} 피해를 받았습니다!")
                
                if enemy.current_hp <= 0:
                    enemy.is_alive = False
                    print(f"💀 {enemy.name}이(가) 쓰러졌습니다!")
            
        elif "damage_enemy" in item.effects:
            # 단일 대상 공격 - 적 선택
            target = self.select_enemy_target(alive_enemies)
            if target:
                actual_damage = max(1, damage_amount)
                target.current_hp = max(0, target.current_hp - actual_damage)
                print(f"💥 {target.name}이(가) {actual_damage} 피해를 받았습니다!")
                
                if target.current_hp <= 0:
                    target.is_alive = False
                    print(f"💀 {target.name}이(가) 쓰러졌습니다!")
            else:
                self.is_action_executing = False
                return False
        
        elif "blind_enemies" in item.effects:
            # 실명 효과
            duration = item.stats.get("duration", 3)
            for enemy in alive_enemies:
                if hasattr(enemy, 'status_manager') and enemy.status_manager:
                    enemy.status_manager.apply_status("blind", duration)
                    print(f"👁️ {enemy.name}이(가) {duration}턴 동안 실명 상태가 되었습니다!")
        
        # 아이템 소모
        user.inventory.remove_item(item.name, 1)
        print(f"✨ {item.name}을(를) 사용했습니다.")
        
        # 액션 실행 완료, 플래그 해제
        self.is_action_executing = False
        return True
    
    def select_enemy_target(self, enemies: List[Character]) -> Character:
        """적 대상 선택"""
        if not enemies:
            return None
            
        if len(enemies) == 1:
            return enemies[0]
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            options = []
            descriptions = []
            
            for enemy in enemies:
                hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
                status = "건강" if hp_ratio > 0.7 else "부상" if hp_ratio > 0.3 else "위험"
                
                option_text = f"{enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp})"
                desc = f"상태: {status} | HP: {hp_ratio:.1%}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("🎯 공격 대상 선택", options, descriptions, clear_screen=False)
            result = menu.run()
            
            if result is None:  # Q키로 취소
                return None
            
            if 0 <= result < len(enemies):
                return enemies[result]
                
        except ImportError:
            # 폴백: 숫자 입력 방식
            print("\n🎯 공격 대상을 선택하세요:")
            for i, enemy in enumerate(enemies, 1):
                hp_ratio = enemy.current_hp / enemy.max_hp if enemy.max_hp > 0 else 0
                print(f"{i}. {enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp} - {hp_ratio:.1%})")
            
            try:
                choice = int(input("선택 (0=취소): "))
                if 1 <= choice <= len(enemies):
                    return enemies[choice - 1]
            except ValueError:
                pass
        
        return None

    def use_item_on_target(self, user: Character, item, target: Character) -> bool:
        """아이템을 대상에게 사용 - 실제 아이템 효과 시스템 연동"""
        # 액션 실행 플래그 설정
        self.is_action_executing = True
        
        # 아이템 사용 이펙트
        self.visualizer.show_skill_effect(user, f"{item.name} 사용", EffectType.HEAL)
        
        # 사용 전 HP/MP 저장
        old_hp = target.current_hp
        old_mp = target.current_mp
        
        # 실제 아이템 효과 적용
        success = item.use_item(target)
        
        if success:
            # 아이템 소모
            user.inventory.remove_item(item.name, 1)
            print(f"✨ {item.name}을(를) 사용했습니다.")
            
            # HP/MP 변화 애니메이션 적용
            if target.current_hp != old_hp and hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
                self.animate_value_change(target, 'HP', old_hp, target.current_hp, self._current_party, self._current_enemies)
            
            if target.current_mp != old_mp and hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
                self.animate_value_change(target, 'MP', old_mp, target.current_mp, self._current_party, self._current_enemies)
            
            # 추가 효과들 처리
            for effect in item.effects:
                if effect == "fire_damage":
                    # 화염 데미지
                    damage = item.stats.get("damage_amount", 50)
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"🔥 {target.name}이(가) 화염 데미지 {damage}를 받았습니다!")
                    # 화상 상태 추가
                    if hasattr(self, 'status_manager'):
                        self.status_manager.add_status(target, "화상", 3)
                
                elif effect == "ice_damage":
                    # 얼음 데미지
                    damage = item.stats.get("damage_amount", 60)
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"❄️ {target.name}이(가) 얼음 데미지 {damage}를 받았습니다!")
                
                elif effect == "freeze":
                    # 동결 상태
                    if hasattr(self, 'status_manager'):
                        self.status_manager.add_status(target, "빙결", 2)
                        print(f"🧊 {target.name}이(가) 동결되었습니다!")
                
                elif effect == "thunder_damage":
                    # 번개 데미지
                    damage = item.stats.get("damage_amount", 70)
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"⚡ {target.name}이(가) 번개 데미지 {damage}를 받았습니다!")
                
                elif effect == "paralyze":
                    # 마비 상태
                    if hasattr(self, 'status_manager'):
                        self.status_manager.add_status(target, "마비", 2)
                        print(f"💫 {target.name}이(가) 마비되었습니다!")
                
                elif effect == "gravity_damage":
                    # 중력 데미지 (현재 HP의 일정 비율)
                    damage_percent = item.stats.get("damage_percent", 25)
                    damage = int(target.current_hp * damage_percent / 100)
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"🌌 {target.name}이(가) 중력 데미지 {damage}를 받았습니다!")
                
                elif effect == "temp_strength":
                    boost = item.stats.get("strength_boost", 10)
                    duration = item.stats.get("duration", 3)
                    # 임시 공격력 증가 (상태 효과 시스템과 연동)
                    if hasattr(target, 'temp_attack_bonus'):
                        target.temp_attack_bonus += boost
                    print(f"💪 {target.name}의 공격력이 {boost} 증가했습니다! ({duration}턴)")
                    
                elif effect == "temp_magic":
                    boost = item.stats.get("magic_boost", 15)
                    duration = item.stats.get("duration", 5)
                    # 임시 마법력 증가
                    if hasattr(target, 'temp_magic_bonus'):
                        target.temp_magic_bonus += boost
                    print(f"🔮 {target.name}의 마법력이 {boost} 증가했습니다! ({duration}턴)")
                    
                elif effect == "temp_haste":
                    boost = item.stats.get("speed_boost", 10)
                    duration = item.stats.get("duration", 4)
                    # 임시 속도 증가
                    if hasattr(target, 'temp_speed_bonus'):
                        target.temp_speed_bonus += boost
                    print(f"⚡ {target.name}의 속도가 {boost} 증가했습니다! ({duration}턴)")
                    
                elif effect == "party_barrier":
                    reduction = item.stats.get("damage_reduction", 50)
                    duration = item.stats.get("duration", 3)
                    # 파티 전체 방어막 (간단 구현)
                    print(f"🛡️ 파티 전체에 방어막이 생성되었습니다! ({reduction}% 피해감소, {duration}턴)")
                    
                elif effect == "berserk":
                    atk_boost = item.stats.get("attack_boost", 25)
                    def_penalty = item.stats.get("defense_penalty", 10)
                    duration = item.stats.get("duration", 3)
                    # 광폭화 효과
                    if hasattr(target, 'temp_attack_bonus'):
                        target.temp_attack_bonus += atk_boost
                    if hasattr(target, 'temp_defense_penalty'):
                        target.temp_defense_penalty += def_penalty
                    print(f"😡 {target.name}이(가) 광폭화 상태가 되었습니다! (공격+{atk_boost}, 방어-{def_penalty}, {duration}턴)")
                
                elif effect == "damage_enemy":
                    # 일반 폭탄 효과
                    damage = item.stats.get("damage_amount", 80)
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"💥 {target.name}이(가) 폭발 데미지 {damage}를 받았습니다!")
                
                elif effect == "poison_enemy":
                    # 독침 효과
                    damage = item.stats.get("damage_amount", 30)
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"☠️ {target.name}이(가) 독 데미지 {damage}를 받았습니다!")
                    if hasattr(self, 'status_manager'):
                        poison_turns = item.stats.get("poison_turns", 3)
                        self.status_manager.add_status(target, "독", poison_turns)
                        print(f"☠️ {target.name}이(가) 독에 중독되었습니다! ({poison_turns}턴)")
                
                elif effect == "blind_enemies":
                    # 연막탄 효과 (명중률 감소)
                    if hasattr(self, 'status_manager'):
                        duration = item.stats.get("duration", 3)
                        self.status_manager.add_status(target, "실명", duration)
                        print(f"👁️ {target.name}이(가) 실명 상태가 되었습니다! ({duration}턴)")
                
                elif effect == "holy_damage":
                    # 성수 효과 (언데드에게 특효)
                    damage = item.stats.get("damage_amount", 120)
                    # 언데드 타입 체크 (간단 구현)
                    if hasattr(target, 'character_class') and any(undead in target.character_class.lower() 
                                                                  for undead in ['언데드', 'undead', '스켈레톤', '좀비']):
                        damage = int(damage * 1.5)  # 언데드에게 1.5배 데미지
                        print(f"✨ 언데드에게 특효! ")
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"🌟 {target.name}이(가) 성스러운 데미지 {damage}를 받았습니다!")
                
                elif effect == "bless_party":
                    # 파티 축복 효과
                    bless_turns = item.stats.get("bless_turns", 2)
                    print(f"✨ 파티 전체에 축복 효과가 적용되었습니다! ({bless_turns}턴)")
                    # 파티 전체 축복 (간단 구현)
                    if hasattr(self, '_current_party'):
                        for member in self._current_party:
                            if member.is_alive and hasattr(self, 'status_manager'):
                                self.status_manager.add_status(member, "축복", bless_turns)
                
                elif effect == "fire_damage_all":
                    # 화염병 - 모든 적에게 화상 피해
                    damage = item.stats.get("damage_amount", 60)
                    burn_turns = item.stats.get("burn_turns", 2)
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"🔥 {target.name}이(가) 화염 데미지 {damage}를 받았습니다!")
                    if hasattr(self, 'status_manager'):
                        self.status_manager.add_status(target, "화상", burn_turns)
                        print(f"🔥 {target.name}이(가) 화상 상태가 되었습니다! ({burn_turns}턴)")
                
                elif effect == "slow_enemy":
                    # 얼음 수정 - ATB 감소 및 둔화
                    atb_reduction = item.stats.get("atb_reduction", 30)
                    slow_turns = item.stats.get("slow_turns", 2)
                    # ATB 감소
                    target.atb_gauge = max(0, target.atb_gauge - (atb_reduction * 10))  # 30% → 300 ATB units
                    print(f"🧊 {target.name}의 ATB가 {atb_reduction}% 감소했습니다!")
                    # 둔화 상태
                    if hasattr(self, 'status_manager'):
                        self.status_manager.add_status(target, "둔화", slow_turns)
                        print(f"🐌 {target.name}이(가) 둔화 상태가 되었습니다! ({slow_turns}턴)")
                
                elif effect == "lightning_all":
                    # 번개 구슬 - 모든 적에게 전격
                    damage = item.stats.get("damage_amount", 75)
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"⚡ {target.name}이(가) 전격 데미지 {damage}를 받았습니다!")
                    # 확률적 마비
                    import random
                    if random.random() < 0.3:  # 30% 확률
                        if hasattr(self, 'status_manager'):
                            self.status_manager.add_status(target, "마비", 1)
                            print(f"💫 {target.name}이(가) 감전되어 마비되었습니다!")
                
                elif effect == "revive":
                    # 부활의 깃털 효과
                    if not target.is_alive:
                        revive_hp_percent = item.stats.get("revive_hp_percent", 50)
                        revival_hp = int(target.max_hp * revive_hp_percent / 100)
                        target.current_hp = revival_hp
                        target.is_alive = True
                        # 상태 초기화
                        if hasattr(target, 'status_manager'):
                            target.status_manager.clear_all_effects()
                        print(f"✨ {target.name}이(가) {revive_hp_percent}% HP로 부활했습니다!")
                        print(f"💚 {target.name}: {target.current_hp}/{target.max_hp} HP")
                    else:
                        print(f"⚠️ {target.name}은(는) 이미 살아있습니다!")
                        self.is_action_executing = False
                        return False  # 아이템 소모하지 않음
                
                elif effect == "cure":
                    # 해독제 - 모든 상태이상 치료
                    if hasattr(target, 'status_manager'):
                        target.status_manager.clear_all_effects()
                        print(f"✨ {target.name}의 모든 상태이상이 치료되었습니다!")
                    else:
                        print(f"💚 {target.name}은(는) 상태이상이 없습니다.")
                
                elif effect == "atb_boost":
                    # 에너지 드링크 - ATB 증가
                    atb_amount = item.stats.get("atb_amount", 50)
                    old_atb = target.atb_gauge
                    target.atb_gauge = min(1000, target.atb_gauge + (atb_amount * 10))  # 50% → 500 ATB units
                    print(f"⚡ {target.name}의 ATB가 {atb_amount}% 증가했습니다!")
                    print(f"⏰ ATB: {old_atb//10}% → {target.atb_gauge//10}%")
                
                elif effect == "detect_treasure":
                    # 보물 탐지기 (전투 중에는 사용 불가)
                    print(f"💎 보물 탐지기는 전투 중에 사용할 수 없습니다!")
                    return False  # 아이템 소모하지 않음
                
                elif effect == "cure_sleep":
                    # 수면 치료
                    if hasattr(target, 'status_manager'):
                        target.status_manager.remove_status("수면")
                        print(f"😴 {target.name}의 수면 상태가 치료되었습니다!")
                
                elif effect == "cure_blind":
                    # 실명 치료
                    if hasattr(target, 'status_manager'):
                        target.status_manager.remove_status("실명")
                        print(f"👁️ {target.name}의 실명 상태가 치료되었습니다!")
                
                elif effect == "cure_silence":
                    # 침묵 치료
                    if hasattr(target, 'status_manager'):
                        target.status_manager.remove_status("침묵")
                        print(f"🤐 {target.name}의 침묵 상태가 치료되었습니다!")
                
                elif effect == "cure_stone":
                    # 석화 치료
                    if hasattr(target, 'status_manager'):
                        target.status_manager.remove_status("석화")
                        print(f"🗿 {target.name}의 석화 상태가 치료되었습니다!")
                
                elif effect == "smoke_screen":
                    # 연막 - 적 명중률 감소
                    accuracy_debuff = item.stats.get("accuracy_debuff", 30)
                    duration = item.stats.get("duration", 3)
                    if hasattr(self, 'status_manager'):
                        self.status_manager.add_status(target, "명중률저하", duration)
                        print(f"💨 {target.name}의 명중률이 {accuracy_debuff}% 감소했습니다! ({duration}턴)")
                
                elif effect == "mass_blind":
                    # 섬광가루 - 모든 적 실명
                    if hasattr(self, 'status_manager') and hasattr(self, '_current_enemies'):
                        for enemy in self._current_enemies:
                            if enemy.is_alive:
                                self.status_manager.add_status(enemy, "실명", 2)
                        print(f"✨ 모든 적이 실명 상태가 되었습니다!")
                
                elif effect == "mass_sleep":
                    # 수면가루 - 모든 적 수면
                    if hasattr(self, 'status_manager') and hasattr(self, '_current_enemies'):
                        for enemy in self._current_enemies:
                            if enemy.is_alive:
                                self.status_manager.add_status(enemy, "수면", 3)
                        print(f"😴 모든 적이 수면 상태가 되었습니다!")
                
                elif effect == "mass_silence":
                    # 침묵가루 - 모든 적 침묵
                    if hasattr(self, 'status_manager') and hasattr(self, '_current_enemies'):
                        for enemy in self._current_enemies:
                            if enemy.is_alive:
                                self.status_manager.add_status(enemy, "침묵", 2)
                        print(f"🤐 모든 적이 침묵 상태가 되었습니다!")
            
            # 🎯 아이템 사용 완료 - ATB는 자연스럽게 유지됨 (다음 턴을 위해)
        else:
            print(f"❌ {item.name}을(를) 사용할 수 없습니다.")
        
        # 액션 실행 완료, 플래그 해제
        self.is_action_executing = False
        return success
                
    def brave_attack_menu(self, attacker: Character, enemies: List[Character]) -> bool:
        """Brave 공격 메뉴 - 강화된 폴백 시스템"""
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return False
        
        # 적이 1명인 경우 자동 선택
        if len(alive_enemies) == 1:
            target = alive_enemies[0]
            print(f"⚔️ 자동 선택: {target.name}")
            self.execute_brave_attack(attacker, target)
            return True
            
        # 1차 시도: 커서 메뉴 시스템
        if CURSOR_MENU_AVAILABLE:
            options = []
            descriptions = []
            
            for enemy in alive_enemies:
                option_text = f"{enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp}, Brave: {enemy.brave_points})"
                desc = f"대상: {enemy.name} | 상태: {'브레이크' if hasattr(enemy, 'is_broken') and enemy.is_broken else '정상'}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("⚔️ Brave 공격 대상 선택", options, descriptions, clear_screen=True)  # 🖥️ 대상 선택 클리어
            result = menu.run()
            
            if result is not None and 0 <= result < len(alive_enemies):
                target = alive_enemies[result]
                self.execute_brave_attack(attacker, target)
                return True
            elif result is None:  # Q키로 취소
                return False
        
        # 2차 시도: 강화된 번호 입력 시스템
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                print(f"\n🔄 번호 입력 방식으로 선택하세요 (시도 {attempt + 1}/{max_attempts}):")
                print("⚔️ 공격할 대상을 선택하세요:")
                
                for i, enemy in enumerate(alive_enemies, 1):
                    status_str = "브레이크" if hasattr(enemy, 'is_broken') and enemy.is_broken else "정상"
                    print(f"  {i}. {enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp}, Brave: {enemy.brave_points}) - {status_str}")
                print(f"  0. 취소")
                
                print("\n번호를 입력하세요:", end=" ")
                choice_str = input().strip()
                
                if not choice_str:  # 빈 입력
                    print("❌ 입력이 없습니다. 다시 시도하세요.")
                    continue
                    
                choice = int(choice_str)
                
                if choice == 0:
                    return False
                elif 1 <= choice <= len(alive_enemies):
                    target = alive_enemies[choice - 1]
                    print(f"✅ {target.name} 선택됨!")
                    self.execute_brave_attack(attacker, target)
                    return True
                else:
                    print(f"❌ 잘못된 선택입니다. 1~{len(alive_enemies)} 또는 0을 입력하세요.")
                    continue
                    
            except ValueError:
                print("❌ 숫자를 입력하세요.")
                continue
            except Exception as e:
                print(f"❌ 입력 처리 중 오류: {e}")
                continue
        
        # 3차 폴백: 사용자에게 마지막 확인 후 첫 번째 적 선택
        print(f"\n🚨 {max_attempts}번의 입력 시도가 모두 실패했습니다.")
        print(f"⚠️ 안전을 위해 첫 번째 적 '{alive_enemies[0].name}'을(를) 자동 선택하려고 합니다.")
        print(f"\n📋 마지막 확인:")
        print(f"  Enter 키: '{alive_enemies[0].name}' 공격")
        print(f"  q 입력: 공격 취소")
        
        try:
            final_input = input("선택하세요 (Enter=공격, q=취소): ").strip().lower()
            if final_input == 'q':
                print("❌ 공격이 취소되었습니다.")
                return False
            else:
                print(f"✅ {alive_enemies[0].name}을(를) 공격합니다!")
                self.execute_brave_attack(attacker, alive_enemies[0])
                return True
        except Exception as e:
            print(f"🚨 최종 입력 처리 중 오류: {e}")
            print(f"⚠️ 강제로 {alive_enemies[0].name}을(를) 공격합니다.")
            self.execute_brave_attack(attacker, alive_enemies[0])
            return True
    
    def _create_colored_hp_gauge(self, current_hp: int, max_hp: int, gauge_length: int = 10) -> str:
        """색깔이 있는 HP 게이지 생성"""
        if max_hp <= 0:
            return "[__________]"
        
        hp_ratio = current_hp / max_hp
        filled_length = int(hp_ratio * gauge_length)
        empty_length = gauge_length - filled_length
        
        # HP 비율에 따른 색깔 결정
        if hp_ratio > 0.7:
            color = get_color('BRIGHT_GREEN')  # 70% 이상: 초록색
        elif hp_ratio > 0.3:
            color = get_color('BRIGHT_YELLOW')  # 30-70%: 노란색
        else:
            color = get_color('BRIGHT_RED')  # 30% 미만: 빨간색
        
        # 게이지 생성
        filled_bar = "█" * filled_length
        empty_bar = "░" * empty_length
        
        return f"[{color}{filled_bar}{get_color('RESET')}{empty_bar}]"
        
    def hp_attack_menu(self, attacker: Character, enemies: List[Character]) -> bool:
        """HP 공격 메뉴"""
        if attacker.brave_points <= 300:  # 500 → 300으로 감소
            print("Brave 포인트가 부족합니다! (최소 300 필요)")
            return False
            
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return False
            
        if CURSOR_MENU_AVAILABLE:
            options = []
            descriptions = []
            
            for enemy in alive_enemies:
                # HP 게이지 색깔 생성
                hp_gauge = self._create_colored_hp_gauge(enemy.current_hp, enemy.max_hp)
                # BREAK 상태는 상태 이펙트에서만 표시 (중복 제거)
                break_status = ""  # 이름에는 BREAK 표시 안함
                option_text = f"{enemy.name} {hp_gauge}{break_status}"
                desc = f"대상: {enemy.name} | HP: {enemy.current_hp}/{enemy.max_hp} | 상태: {'브레이크' if hasattr(enemy, 'is_broken') and enemy.is_broken else '정상'}"
                
                options.append(option_text)
                descriptions.append(desc)
            
            menu = create_simple_menu("💀 HP 공격 대상 선택", options, descriptions, clear_screen=True)  # 🖥️ HP 공격 대상 클리어
            result = menu.run()
            
            if result is not None and 0 <= result < len(alive_enemies):
                target = alive_enemies[result]
                self.execute_hp_attack(attacker, target)
                return True
            elif result is None:  # Q키로 취소
                return False
            return False
        else:
            # 폴백: 기존 방식
            print("\n대상을 선택하세요:")
            for i, enemy in enumerate(alive_enemies, 1):
                hp_gauge = self._create_colored_hp_gauge(enemy.current_hp, enemy.max_hp)
                # BREAK 상태는 상태 이펙트에서만 표시 (중복 제거)
                break_status = ""  # 이름에는 BREAK 표시 안함
                print(f"{i}. {enemy.name} {hp_gauge}{break_status}")
                
            try:
                choice_str = self.keyboard.get_key()
                choice = int(choice_str) - 1
                if 0 <= choice < len(alive_enemies):
                    target = alive_enemies[choice]
                    self.execute_hp_attack(attacker, target)
                    return True
            except ValueError:
                pass
                
            print("잘못된 선택입니다.")
            return False
        
    def execute_brave_attack(self, attacker: Character, target: Character):
        """Brave 공격 실행 + 그림자 시스템 통합"""
        from game.error_logger import log_combat
        
        # 🔧 로그 카테고리 수정: 아군/적군 구분
        if hasattr(self, 'current_party') and attacker in self.current_party:
            log_combat("아군행동", f"{attacker.name}이 {target.name}에게 Brave 공격 실행 시작")
        else:
            log_combat("적행동", f"{attacker.name}이 {target.name}에게 Brave 공격 실행 시작")
        
        # 액션 실행 플래그 설정
        self.is_action_executing = True
        
        # 🌑 암살자인지 확인
        is_assassin = getattr(attacker, 'character_class', '') == '암살자'
        
        # 특성 트리거 효과 발동 (공격 시)
        if hasattr(attacker, 'trigger_trait_effects'):
            trait_messages = attacker.trigger_trait_effects("attack")
            for msg in trait_messages:
                print(f"✨ {attacker.name}: {msg}")
            
            # ⏳ 특성 효과 확인 위해 2초 대기 (엔터로 스킵 가능)
            if trait_messages and hasattr(self, 'gauge_animator'):
                self.gauge_animator._wait_with_skip_option(2.0, "특성 효과 확인")
        
        # 기본 Brave 공격 스킬 사용
        brave_skills = [skill for skill in attacker.brave_skills if skill.attack_type == BraveAttackType.BRAVE]
        if brave_skills:
            skill = brave_skills[0]  # 첫 번째 Brave 스킬 사용
        else:
            # 직업별 기본 공격
            from .brave_system import BraveSkill
            skill = self._get_class_specific_basic_attack(attacker)
        
        # 🎯 새로운 스킬 시스템에서 기본 공격 스킬 데이터 가져오기
        try:
            from .new_skill_system import NewSkillSystem
            skill_system = NewSkillSystem()
            character_class = getattr(attacker, 'character_class', '')
            class_skills = skill_system.get_class_skills(character_class)
            
            # 첫 번째 BRV_ATTACK 타입 스킬 찾기 (기본 공격)
            basic_brv_skill = None
            for s in class_skills:
                if s.get('type') and str(s['type']) == 'SkillType.BRV_ATTACK' and s.get('mp_cost', 0) == 0:
                    basic_brv_skill = s
                    break
            
            if basic_brv_skill:
                # 특수 효과 실행
                special_effects = basic_brv_skill.get('special_effects', [])
                if special_effects:
                    self._execute_special_effects(special_effects, attacker, basic_brv_skill, [target])
        except Exception as e:
            pass  # 기본 공격은 실패해도 정상 진행
        
        # 🌑 암살자 기본공격에 그림자 생성 효과 추가
        if is_assassin and self.shadow_system:
            # 기본공격에도 그림자 1개 생성
            self.shadow_system.add_shadows(attacker, 1)
        
        # 🗡️ 도적 기본공격에 독 효과 추가
        character_class = getattr(attacker, 'character_class', '')
        if character_class == "도적":
            # 도적의 독 스택 시스템 초기화 (필요시)
            if not hasattr(attacker, 'poison_stacks'):
                setattr(attacker, 'poison_stacks', 0)
            if not hasattr(attacker, 'max_poison_stacks'):
                max_stacks = int(getattr(attacker, 'attack', 100) * 1.5)
                setattr(attacker, 'max_poison_stacks', max_stacks)
            
            # 기본공격 시 100% 확률로 독 부여
            if random.random() < 1.0:
                # 독 부여 효과는 BRV 공격 후 처리
                setattr(attacker, '_apply_poison_after_attack', target)
            
        # 스킬 사용 비주얼 이펙트
        if hasattr(self, 'visualizer') and self.visualizer:
            self.visualizer.show_skill_effect(attacker, skill.name, EffectType.SKILL)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("skill", skill_name=skill.name, character_name=attacker.name)
        
        # HP 희생 처리
        if hasattr(skill, 'hp_sacrifice_rate') and skill.hp_sacrifice_rate > 0:
            sacrifice_hp = max(1, int(attacker.current_hp * skill.hp_sacrifice_rate))
            attacker.current_hp = max(1, attacker.current_hp - sacrifice_hp)
            print(f"💔 {attacker.name}이(가) {sacrifice_hp} HP를 희생하여 위력을 극대화!")
            
            # 희생한 HP만큼 추가 데미지 보너스 (스킬 데미지 계산에 반영)
            attacker.temp_sacrifice_power = getattr(attacker, 'temp_sacrifice_power', 0) + sacrifice_hp * 2
        
        # 회피 체크 먼저 수행
        if self._check_dodge(attacker, target):
            # 회피 SFX 재생
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("dodge")
            elif hasattr(self, 'sound_manager'):
                self.sound_manager.play_sfx("dodge")
            
            # 회피 비주얼 이펙트 (이곳에서만 메시지 출력)
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.show_miss_effect(attacker, target)
            enhanced_battle_effect("dodge", character_name=target.name)
            return
        
        # 🎯 새로운 스킬 배율 시스템 (기본공격 100%, 스킬 170%)
        is_skill = False
        if hasattr(skill, '__dict__') and skill.__dict__.get('name') != '기본 공격':
            is_skill = True
        elif hasattr(skill, 'name') and skill.name != '기본 공격':
            is_skill = True
        
        if is_skill:
            # 스킬의 경우: 기본공격의 1.7배 효과
            brv_power = 170  # 170%
        else:
            # 기본 공격의 경우: 100% 기준
            brv_power = 100  # 100%
            
        brave_damage = self._calculate_brv_damage(skill.__dict__ if hasattr(skill, '__dict__') else {"name": skill.name, "brv_power": brv_power}, attacker, target, brv_power)
        
        # BRV 데미지는 통합 시스템에서 이미 적절히 계산됨 (추가 배율 제거)
        # brave_damage = int(brave_damage * 2.5)  # 제거: 중복 배율 적용 방지
        
        # BRV 데미지 최소/최댓값 제한 (1 ~ 999999)
        brave_damage = max(1, min(999999, brave_damage))
        
        # 특성 효과 적용
        if hasattr(attacker, 'get_effective_stats'):
            effective_stats = attacker.get_effective_stats()
            # 공격력 보너스 적용
            total_attack = attacker.get_total_attack() if hasattr(attacker, 'get_total_attack') else attacker.physical_attack
            damage_multiplier = 1.0 + (attacker.temp_attack_bonus / max(1, attacker.physical_attack))
            brave_damage = int(brave_damage * damage_multiplier)
        
        # 크리티컬 체크 (특성 보너스 적용)
        crit_chance = 0.1  # 기본 10%
        if hasattr(attacker, 'temp_crit_bonus'):
            crit_chance += attacker.temp_crit_bonus
        
        # 궁수 첫 공격 크리티컬 특성 (안전하게 수정) - 궁수만 적용
        if (hasattr(attacker, 'character_class') and attacker.character_class == "궁수" and
            hasattr(attacker, 'temp_first_strike') and getattr(attacker, 'temp_first_strike', False)):
            # 이미 공격했는지 확인 (안전한 체크)
            if not getattr(attacker, '_has_attacked_in_battle', False):
                setattr(attacker, '_has_attacked_in_battle', True)
                setattr(attacker, 'temp_first_strike', False)  # 첫 공격 보너스 소모
                crit_chance = 1.0  # 100% 크리티컬
                print(f"🎯 {attacker.name}의 첫 공격 크리티컬 확정!")
                # 🎮 첫 공격 크리티컬 진동
                if self.vibration_enabled:
                    self.input_manager.vibrate_heavy()
        
        # 다른 직업에서 잘못된 temp_first_strike 속성 제거
        elif (hasattr(attacker, 'temp_first_strike') and 
              hasattr(attacker, 'character_class') and 
              attacker.character_class != "궁수"):
            delattr(attacker, 'temp_first_strike')  # 궁수가 아니면 제거
        
        critical = random.random() < crit_chance
        if critical:
            brave_damage = int(brave_damage * 1.5)
            print(f"💥 치명타! {attacker.name}")
            
        # 공격 비주얼 이펙트
        effect_type = EffectType.CRITICAL if critical else EffectType.PHYSICAL_ATTACK
        self.visualizer.show_attack_effect(attacker, target, brave_damage, effect_type, skill.name)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("damage", damage=brave_damage, critical=critical)
        
        # 새로운 스킬 시스템 특수 효과 처리 (먼저 정의)
        special_effects = []
        
        # BraveSkill 객체에서 special_effects 가져오기
        if hasattr(skill, 'special_effects') and skill.special_effects:
            special_effects = skill.special_effects
        elif hasattr(skill, '__dict__'):
            skill_dict = skill.__dict__
            special_effects = skill_dict.get('special_effects', [])

        # Brave 포인트 적용 (아군/적군 구분)
        if attacker and hasattr(attacker, 'character_class') and attacker.character_class != "Enemy":
            # 아군 → 적: 33% 획득 (1/3)
            gained_brave = int(brave_damage * 1)
        else:
            # 적 → 아군: 300% 획득 (3배)
            gained_brave = int(brave_damage * 1)
        
        # BRV 데미지 적용 (연타 공격이 아닌 경우만)
        if not ("combo_attack" in special_effects):
            # 🎯 올바른 BREAK 조건: BRV가 이미 0인 상태에서 BRV 공격을 받으면 BREAK
            was_already_zero = (target.brave_points <= 0)
            
            target.brave_points -= brave_damage
            
            # 공격자 Brave 증가
            attacker.add_brave_points(gained_brave)
            
            print(f"💥 {target.name}에게 {brave_damage} BRV 피해!")
            # 🎮 BRV 공격 성공 진동 (가벼운 진동)
            if self.vibration_enabled:
                self.input_manager.vibrate_light()
            
            # BRV 획득 메시지 제거 - 애니메이션에서 표시됨
            
            # BREAK 체크 - 이미 BRV가 0이었는데 추가로 BRV 공격을 받으면 BREAK 발생
            if target.brave_points <= 0:
                target.brave_points = 0
                
                # BREAK 조건: 이미 0이었던 상태에서 BRV 공격을 받았을 때만
                if was_already_zero and not getattr(target, 'is_broken', False):
                    target.is_broken = True
                    
                    # ATB 게이지 초기화 (BREAK 시)
                    target.atb_gauge = 0
                    # print(f"🔄 {target.name}의 ATB 게이지가 초기화되었습니다!")  # 로그 제거
                    
                    # 캐스팅 중단 (BREAK 시에만 중단됨)
                    if hasattr(target, 'is_casting') and target.is_casting:
                        skill_name = getattr(target, 'casting_skill', {}).get('name', '스킬')
                        print(f"❌ {target.name}의 {skill_name} 캐스팅이 BREAK로 인해 중단되었습니다!")
                        self._clear_casting_state(target)
                    
                    self.visualizer.show_status_change(target, "BREAK!", False)
                    print(f"\n{get_color('BRIGHT_RED')}{'='*50}")
                    print(f"💥 {target.name}이(가) BREAK 상태가 되었습니다! 💥")
                    print(f"   (BRV 0 상태에서 추가 BRV 공격을 받아 무력화!)")
                    print(f"{'='*50}{get_color('RESET')}\n")
                    
                    # Break 전용 효과음 재생
                    if hasattr(self, 'sound_system'):
                        self.sound_system.play_sfx("break_sound")
                    enhanced_battle_effect("break")
                    
                    # BREAK 발생 메시지만 표시
        
        # 직업별 특수 효과 적용
        if hasattr(skill, 'name'):
            self._apply_class_specific_brv_effects(attacker, target, skill, brave_damage)
        
        # 🗡️ 도적 기본공격 독 효과 후처리
        if hasattr(attacker, '_apply_poison_after_attack'):
            poison_target = getattr(attacker, '_apply_poison_after_attack')
            if poison_target == target:  # 같은 타겟에게만 적용
                # 기존 독 상태 확인
                current_poison_turns = getattr(target, 'poison_turns', 0)
                current_poison_damage = getattr(target, 'poison_damage', 0)
                
                if current_poison_turns > 0:
                    # 독 누적
                    setattr(target, 'poison_turns', current_poison_turns + 2)
                    new_poison_damage = int(current_poison_damage * 1.2)
                    setattr(target, 'poison_damage', new_poison_damage)
                    print(f"🐍 {target.name}에게 기본공격 독이 누적되었습니다! ({current_poison_damage} → {new_poison_damage}, {current_poison_turns + 2}턴)")
                else:
                    # 새로운 독 부여
                    setattr(target, 'poison_turns', 3)
                    base_poison = int(target.max_hp * 0.03)  # 기본공격은 약한 독
                    setattr(target, 'poison_damage', base_poison)
                    print(f"🐍 {target.name}에게 독이 적용되었습니다! (3턴간 턴마다 {base_poison} 피해)")
                
                # 독 상태 표시를 위한 플래그 설정 - 강제 적용
                setattr(target, 'is_poisoned', True)
                if hasattr(target, 'status_manager') and target.status_manager:
                    target.status_manager.apply_status('독', getattr(target, 'poison_turns', 3))
                    print(f"🔍 {target.name}의 독 상태가 상태창에 표시됩니다.")
                else:
                    print(f"🔍 {target.name}에게 독 상태 플래그를 설정했습니다.")
                
                # 도적 독 스택 증가
                if hasattr(attacker, 'poison_stacks'):
                    current_stacks = getattr(attacker, 'poison_stacks', 0)
                    max_stacks = getattr(attacker, 'max_poison_stacks', 100)
                    new_stacks = min(current_stacks + 1, max_stacks)
                    setattr(attacker, 'poison_stacks', new_stacks)
                    print(f"💚 {attacker.name}의 독 스택: {current_stacks} → {new_stacks}")
                
                # 후처리 플래그 제거
                delattr(attacker, '_apply_poison_after_attack')
        
        # 특수효과 실행 (연타 공격 포함)
        if special_effects:
            print(f"🎯 {skill.name if hasattr(skill, 'name') else '기본공격'}의 특수 효과 발동! ({len(special_effects)}개)")
            # 🥊 연타 공격 특수 처리
            if "combo_attack" in special_effects:
                self._execute_combo_attack(attacker, target, skill, brave_damage, gained_brave)
            else:
                self._execute_special_effects(special_effects, attacker, skill, [target])
        
        # 스킬의 상태효과 적용 (독화살 등)
        if hasattr(skill, 'status_effects') and skill.status_effects:
            for status_effect in skill.status_effects:
                if hasattr(target, 'status_manager') and target.status_manager:
                    effect_type = status_effect.get('type', "poison")
                    duration = status_effect.get('duration', 3)
                    intensity = status_effect.get('intensity', 1.0)
                    target.status_manager.add_status(effect_type, duration, intensity)
                    print(f"✨ {target.name}에게 {effect_type} 효과 적용! ({duration}턴)")
        
        # 스킬 dict 형태일 때도 처리
        elif hasattr(skill, '__dict__') and skill.__dict__.get('status_effects'):
            for status_effect in skill.__dict__['status_effects']:
                if hasattr(target, 'status_manager') and target.status_manager:
                    effect_type = status_effect.get('type', 'poison')
                    duration = status_effect.get('duration', 3)
                    intensity = status_effect.get('intensity', 1.0)
                    target.status_manager.add_status(effect_type, duration, intensity)
                    print(f"✨ {target.name}에게 {effect_type} 효과 적용! ({duration}턴)")
        
        # 🔮🏹 궁수 지원사격 트리거 (아군이 공격을 받을 때)
        self._trigger_support_fire(attacker, target, "ally_attacked")
        
        # 🎯 어그로 이벤트 생성 (아군이 적을 공격했을 때)
        if hasattr(self, 'aggro_system') and hasattr(attacker, 'character_class'):
            # 아군 → 적 공격 시에만 어그로 생성
            is_attacker_ally = not getattr(attacker, 'is_enemy', False)
            is_target_enemy = getattr(target, 'is_enemy', False)
            
            if is_attacker_ally and is_target_enemy:
                # 모든 적에게 공격자의 어그로 추가
                attacker_name = getattr(attacker, 'name', str(attacker))
                target_name = getattr(target, 'name', str(target))
                target_max_hp = getattr(target, 'max_hp', 1000)  # 타겟의 최대 HP
                
                # 피해량 기반 어그로 생성
                aggro_event = create_damage_aggro(attacker_name, brave_damage, target_max_hp)
                
                # 타겟된 적에게 어그로 추가
                self.aggro_system.add_aggro_event(target_name, aggro_event)
                
                # 다른 적들에게도 절반의 어그로 추가 (관심 끌기)
                if hasattr(self, '_current_enemies'):
                    for enemy in self._current_enemies:
                        enemy_name = getattr(enemy, 'name', str(enemy))
                        if enemy_name != target_name and getattr(enemy, 'is_alive', True):
                            indirect_aggro = create_damage_aggro(attacker_name, brave_damage * 0.3)
                            self.aggro_system.add_aggro_event(enemy_name, indirect_aggro)
        
        # BRV 공격 결과 확인 - 대기 시간 제거 (어차피 턴 정산에서 대기)
        
        # 액션 실행 완료, 플래그 해제
        self.is_action_executing = False
    
    def _get_class_specific_basic_attack(self, character: Character):
        """직업별 특화된 기본공격 반환 (new_skill_system.py 완전 통합)"""
        from .brave_system import BraveSkill
        from .new_skill_system import get_basic_attacks_for_class
        
        character_class = getattr(character, 'character_class', '전사')
        
        # 세피로스 전용 다중 BRV 공격 시스템
        if character_class == "최종보스" and hasattr(character, 'boss_abilities'):
            import random
            boss_brv_attacks = [
                {"name": "마사무네 베기", "power": 0.8, "desc": "전설의 검 마사무네로 강력한 일격"},
                {"name": "옥타슬래시", "power": 0.9, "desc": "세피로스의 8연속 검격으로 강력한 연타 공격"}
            ]
            selected_attack = random.choice(boss_brv_attacks)
            return BraveSkill(
                selected_attack["name"], 
                BraveAttackType.BRAVE, 
                selected_attack["power"], 
                description=selected_attack["desc"]
            )
        
        # new_skill_system.py에서 기본공격 가져오기
        try:
            basic_attacks = get_basic_attacks_for_class(character_class)
            if basic_attacks and 'brv' in basic_attacks:
                brv_attack = basic_attacks['brv']
                
                # 새로운 8개 직업 시스템과 연동
                return BraveSkill(
                    brv_attack['name'], 
                    BraveAttackType.BRAVE, 
                    brv_attack.get('brv_power', 95) / 280,  # 파워를 적절한 배율로 변환
                    description=brv_attack.get('description', '기본 BRV 공격'),
                    special_effects=brv_attack.get('special_effects', [])
                )
        except Exception as e:
            print(f"⚠️ new_skill_system 연동 실패: {e}")
        
        # 폴백 시스템 (Phase 1&2 완성 직업들)
        phase_completed_attacks = {
            "검성": BraveSkill("검기 베기", BraveAttackType.BRAVE, 0.34, 
                             description="검기 스택 1개 획득, 스택으로 강화 가능"),
            "검투사": BraveSkill("투기장 기술", BraveAttackType.BRAVE, 0.35, 
                               description="적 처치 시 능력치 상승, 패링 가능"),
            "광전사": BraveSkill("분노의 폭발", BraveAttackType.BRAVE, 0.36, 
                               description="HP 소모하여 위력 증가, 흡혈 효과"),
            "기사": BraveSkill("창 돌격", BraveAttackType.BRAVE, 0.33, 
                             description="의무 스택 생성, 아군 보호 시 강화"),
            "성기사": BraveSkill("성스러운 타격", BraveAttackType.BRAVE, 0.35, 
                               description="성역 생성 조건 활성화"),
            "암흑기사": BraveSkill("흡혈 베기", BraveAttackType.BRAVE, 0.37, 
                                 description="피해 흡수 스택 생성"),
            "용기사": BraveSkill("용의표식", BraveAttackType.BRAVE, 0.34, 
                               description="용의 표식 부여, 표식 기반 강화"),
            "아크메이지": BraveSkill("라이트닝볼트", BraveAttackType.BRAVE, 0.32, 
                                   description="번개 카운트 +1, 원소 순환 시스템")
        }
        
        return phase_completed_attacks.get(character_class, 
                                         BraveSkill("기본 공격", BraveAttackType.BRAVE, 0.33))
        
        # 폴백 기본공격 정의 (new_skill_system.py 실패 시)
        class_attacks = {
            "전사": BraveSkill("적응형 강타", BraveAttackType.BRAVE, 0.4, description="현재 자세에 따라 효과가 변하는 기본 공격"),
            "아크메이지": BraveSkill("마력 파동", BraveAttackType.BRAVE, 0.25, description="마력을 파동으로 방출하여 적의 마법방어력 감소"),
            "궁수": BraveSkill("삼연사", BraveAttackType.BRAVE, 0.15, description="조준 포인트를 생성하며 연속 사격"),
            "도적": BraveSkill("맹독침", BraveAttackType.BRAVE, 0.3, description="맹독이 발린 침으로 공격하여 강력한 독 상태이상과 독 누적 부여"),
            "성기사": BraveSkill("성스러운타격", BraveAttackType.BRAVE, 0.35, description="성스러운 힘이 깃든 공격으로 아군 회복 효과"),
            "암흑기사": BraveSkill("흡혈 베기", BraveAttackType.BRAVE, 0.45, description="적의 생명력을 흡수하여 자신의 HP 회복"),
            "몽크": BraveSkill("연환 타격", BraveAttackType.BRAVE, 0.28, description="연속 타격으로 적에게 '표식' 중첩"),
            "바드": BraveSkill("음파 공격", BraveAttackType.BRAVE, 0.2, description="음파로 공격하며 아군들의 사기 증진"),
            "네크로맨서": BraveSkill("생명력 흡수", BraveAttackType.BRAVE, 0.35, description="적의 생명력을 흡수하여 MP 회복"),
            "용기사": BraveSkill("화염 강타", BraveAttackType.BRAVE, 0.42, description="용의 숨결을 실은 공격으로 화상 부여"),
            "검성": BraveSkill("검기 베기", BraveAttackType.BRAVE, 0.38, description="검기를 날려 원거리에서도 공격 가능"),
            "정령술사": BraveSkill("원소 탄환", BraveAttackType.BRAVE, 0.3, description="랜덤 원소로 공격하며 속성 약점 적용"),
            "암살자": BraveSkill("그림자 강타", BraveAttackType.BRAVE, 0.5, description="그림자를 생성하고 그림자 메아리로 추가 피해를 가하는 BRV 공격"),
            "기계공학자": BraveSkill("기계타격", BraveAttackType.BRAVE, 0.32, description="정밀한 기계 도구로 적을 타격하며 기계 에너지를 충전"),
            "무당": BraveSkill("영혼 타격", BraveAttackType.BRAVE, 0.25, description="영혼을 직접 타격하여 방어력 무시"),
            "해적": BraveSkill("이도류 난타", BraveAttackType.BRAVE, 0.2, description="양손 무기로 연속 공격"),
            "사무라이": BraveSkill("거합 베기", BraveAttackType.BRAVE, 0.55, description="단숨에 베는 강력한 일격, 낮은 HP일수록 강화"),
            "드루이드": BraveSkill("자연의 분노", BraveAttackType.BRAVE, 0.3, description="자연의 힘으로 공격하며 턴마다 HP 회복"),
            "철학자": BraveSkill("논리적 반박", BraveAttackType.BRAVE, 0.15, description="적의 행동을 예측하여 반격, 높은 회피율"),
            "시간술사": BraveSkill("시간 조작", BraveAttackType.BRAVE, 0.25, description="시간을 조작하여 적의 행동 지연"),
            "연금술사": BraveSkill("화학 폭발", BraveAttackType.BRAVE, 0.35, description="화학 반응으로 폭발 피해, 주변 적에게도 영향"),
            "검투사": BraveSkill("투기장 기술", BraveAttackType.BRAVE, 0.4, description="검투장에서 익힌 기술로 반격 확률 증가"),
            "기사": BraveSkill("창 돌격", BraveAttackType.BRAVE, 0.45, description="창으로 돌격하여 관통 피해"),
            "신관": BraveSkill("축복의 빛", BraveAttackType.BRAVE, 0.2, description="적을 공격하면서 아군에게 축복 버프 부여"),
            "마검사": BraveSkill("마법검기", BraveAttackType.BRAVE, 0.4, description="물리와 마법이 결합된 공격"),
            "차원술사": BraveSkill("차원 균열", BraveAttackType.BRAVE, 0.35, description="차원을 찢어 공간 피해"),
            "광전사": BraveSkill("분노의 폭발", BraveAttackType.BRAVE, 0.6, description="이성을 잃고 폭주하는 공격, HP가 낮을수록 강화"),
            "최종보스": BraveSkill("옥타슬래시", BraveAttackType.BRAVE, 0.9, description="세피로스의 8연속 검격으로 강력한 연타 공격"),
        }
        
        return class_attacks.get(character_class, BraveSkill("기본 공격", BraveAttackType.BRAVE, 0.33))
        
    def _apply_class_specific_brv_effects(self, attacker: Character, target: Character, skill, damage: int):
        """직업별 BRV 공격 특수 효과 적용 (28개 직업 완전 지원)"""
        character_class = getattr(attacker, 'character_class', '전사')
        
        if character_class == "전사" and skill.name == "적응형 강타":
            # 적응형 강타: 현재 자세에 따라 다른 효과
            try:
                from .warrior_system import WarriorStanceSystem
                warrior_system = WarriorStanceSystem()
                current_stance = warrior_system.get_current_stance(attacker)
                
                if current_stance == "방어형":
                    # 방어형: 20% 확률로 적 기절
                    is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
                    stun_chance = 0.05 if is_boss else 0.2
                    if random.random() < stun_chance:
                        setattr(target, 'is_stunned', True)
                        print(f"🛡️ 적응형 강타 (방어형): {target.name}이(가) 기절했습니다!")
                elif current_stance == "공격형":
                    # 공격형: 추가 BRV 피해
                    bonus_damage = int(damage * 0.3)
                    target.brave_points -= bonus_damage
                    attacker.add_brave_points(int(bonus_damage * 0.33))
                    print(f"⚡ 적응형 강타 (공격형): 추가 {bonus_damage} BRV 피해!")
                elif current_stance == "광전사":
                    # 광전사: HP 비례 추가 피해
                    hp_ratio = attacker.current_hp / attacker.max_hp
                    rage_bonus = max(1.0, 2.0 - hp_ratio)
                    bonus_damage = int(damage * (rage_bonus - 1.0))
                    target.brave_points -= bonus_damage
                    print(f"💀 적응형 강타 (광전사): 분노 추가 {bonus_damage} BRV 피해!")
                else:
                    print(f"⚖️ 적응형 강타 ({current_stance}): 균형 잡힌 공격!")
            except ImportError:
                # warrior_system이 없으면 기본 효과
                print(f"⚔️ 적응형 강타: 기본 공격!")
                
        elif character_class == "아크메이지" and skill.name == "마력 파동":
            # 적의 마법방어력 곱적용 감소 (보스는 저항) + 원거리
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss and random.random() < 0.7:  # 보스는 70% 저항
                print(f"🛡️ {target.name}이(가) 마력 파동에 저항했습니다!")
            else:
                reduction_multiplier = 0.9 if is_boss else 0.85  # 보스 10% 감소, 일반 15% 감소
                current_mdef_mult = getattr(target, 'temp_mdef_multiplier', 1.0)
                setattr(target, 'temp_mdef_multiplier', current_mdef_mult * reduction_multiplier)
                setattr(target, 'mdef_reduction_turns', 3)
                reduction_percent = int((1 - reduction_multiplier) * 100)
                print(f"🔮 {target.name}의 마법방어력이 {reduction_percent}% 감소했습니다!")
            
            # 마법 원거리 공격 - ATB 소모량 감소
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(attacker.atb_gauge * 0.25)  # 25% 절약
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"🌟 마법 원거리 공격으로 ATB {atb_save * 100 // self.ATB_READY_THRESHOLD}% 절약!")
            
        elif character_class == "궁수" and skill.name == "삼연사":
            # 3연타 추가 공격 (원거리 - ATB 30% 절약)
            for i in range(2):  # 이미 1번 공격했으므로 2번 더
                additional_damage = int(damage * 0.7)  # 후속 공격은 70% 위력
                target.brave_points -= additional_damage
                gained_brave = int(additional_damage * 0.33)
                attacker.add_brave_points(gained_brave)
                print(f"🏹 연속 공격 {i+2}번째: {additional_damage} BRV 피해!")
            
            # 원거리 공격 - ATB 소모량 감소
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(attacker.atb_gauge * 0.3)  # 30% 절약
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"🎯 원거리 공격으로 ATB {atb_save * 100 // self.ATB_READY_THRESHOLD}% 절약!")
                
        elif character_class == "도적" and skill.name == "맹독침":
            # 🧪 도적 전용: BRV 공격 시 venom_power 증가
            if hasattr(attacker, 'venom_power') and hasattr(attacker, 'venom_power_max'):
                # 공격력의 일부(3%)만큼 venom 증가 (최소 2, 최대 12)
                attacker_attack = getattr(attacker, 'physical_attack', 100)
                venom_gain = max(2, min(12, int(attacker_attack * 0.03)))
                old_venom = attacker.venom_power
                attacker.venom_power = min(attacker.venom_power + venom_gain, attacker.venom_power_max)
                
                # venom 증가 메시지 표시
                if attacker.venom_power > old_venom:
                    new_venom = attacker.venom_power
                    gain_amount = new_venom - old_venom
                    print(f"🧪 맹독침 공격! Venom Power: {old_venom} → {new_venom} (+{gain_amount})")
                    
                    # venom이 최대치에 도달했을 때 특별 메시지
                    if attacker.venom_power >= attacker.venom_power_max:
                        print(f"💀 [VENOM MAX] 도적의 독액이 최고조에 달했습니다! ({attacker.venom_power}/{attacker.venom_power_max})")
            
            # 맹독 누적 시스템 - 기존 독이 있으면 강화
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            resistance_chance = 0.6 if is_boss else 0.1  # 보스 60%, 일반 10% 저항
            
            if random.random() < resistance_chance:
                print(f"🛡️ {target.name}이(가) 독에 저항했습니다!")
            else:
                # 기존 독 상태 확인
                current_poison_turns = getattr(target, 'poison_turns', 0)
                current_poison_damage = getattr(target, 'poison_damage', 0)
                
                # 도적의 독 스택 시스템 초기화
                if not hasattr(attacker, 'poison_stacks'):
                    setattr(attacker, 'poison_stacks', 0)
                if not hasattr(attacker, 'max_poison_stacks'):
                    # 최대 독 스택 = 공격력의 150%
                    max_stacks = int(getattr(attacker, 'attack', 100) * 1.5)
                    setattr(attacker, 'max_poison_stacks', max_stacks)
                
                if current_poison_turns > 0:
                    # 독 누적 - 지속시간 연장 + 피해량 증가
                    setattr(target, 'poison_turns', current_poison_turns + 4)
                    new_poison_damage = int(current_poison_damage * 1.5)
                    setattr(target, 'poison_damage', min(new_poison_damage, int(target.max_hp * 0.15)))  # 최대 15% 제한
                    
                    # 독 스택 축적 - 누적된 독 피해의 25%
                    poison_stack_gain = int(new_poison_damage * 0.25)
                    current_stacks = getattr(attacker, 'poison_stacks', 0)
                    max_stacks = getattr(attacker, 'max_poison_stacks', 100)
                    new_stacks = min(current_stacks + poison_stack_gain, max_stacks)
                    setattr(attacker, 'poison_stacks', new_stacks)
                    
                    print(f"🔥 독이 누적되어 더욱 치명적이 되었습니다! ({current_poison_damage} → {new_poison_damage})")
                    print(f"💚 독 스택 축적: {current_stacks} → {new_stacks} (+{poison_stack_gain})")
                else:
                    # 새로운 독 부여
                    setattr(target, 'poison_turns', 6)
                    base_poison = int(target.max_hp * 0.04) if is_boss else int(target.max_hp * 0.06)
                    setattr(target, 'poison_damage', base_poison)
                    
                    # 독 스택 축적 - 기본 독 피해의 20%
                    poison_stack_gain = int(base_poison * 0.2)
                    current_stacks = getattr(attacker, 'poison_stacks', 0)
                    max_stacks = getattr(attacker, 'max_poison_stacks', 100)
                    new_stacks = min(current_stacks + poison_stack_gain, max_stacks)
                    setattr(attacker, 'poison_stacks', new_stacks)
                    
                    print(f"💚 {target.name}이(가) 맹독에 중독되었습니다! (6턴, {base_poison} 피해)")
                    print(f"💚 독 스택 축적: {current_stacks} → {new_stacks} (+{poison_stack_gain})")
                
                setattr(target, 'is_poisoned', True)
            
        elif character_class == "성기사" and skill.name == "성스러운타격":
            # 공격하면서 아군 중 HP가 가장 낮은 대상 회복
            if hasattr(self, '_current_party') and self._current_party:
                lowest_hp_ally = min([ally for ally in self._current_party if ally.current_hp > 0], 
                                   key=lambda x: x.current_hp / x.max_hp, default=None)
                if lowest_hp_ally:
                    heal_amount = int(damage * 0.3)
                    lowest_hp_ally.heal(heal_amount)
                    print(f"✨ {lowest_hp_ally.name}이(가) {heal_amount} HP 회복!")
                    
        elif character_class == "암흑기사" and skill.name == "흡혈 베기":
            # 가한 피해의 10% HP 회복 (너프됨)
            heal_amount = int(damage * 0.1)
            attacker.heal(heal_amount)
            print(f"🩸 {attacker.name}이(가) {heal_amount} HP 회복!")
            
        elif character_class == "몽크" and skill.name == "연환 타격":
            # 적에게 '타격 표식' 중첩 (최대 5중첩, 받는 물리피해 곱적용 증가)
            current_marks = getattr(target, 'strike_marks', 0)
            new_marks = min(current_marks + 1, 5)
            setattr(target, 'strike_marks', new_marks)
            
            # 곱적용 피해 증가
            current_damage_mult = getattr(target, 'temp_damage_taken_multiplier', 1.0)
            mark_multiplier = 1.0 + (new_marks * 0.06)  # 중첩당 6% 증가
            setattr(target, 'temp_damage_taken_multiplier', mark_multiplier)
            
            damage_increase = int(new_marks * 6)
            print(f"👊 {target.name}에게 타격 표식 {new_marks}중첩! (받는 물리피해 +{damage_increase}%)")
            
        elif character_class == "바드" and skill.name == "음파 공격":
            # 아군 전체 사기 증진 (곱적용 버프)
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally.current_hp > 0:
                        current_attack_mult = getattr(ally, 'temp_attack_multiplier', 1.0)
                        setattr(ally, 'temp_attack_multiplier', current_attack_mult * 1.08)  # 8% 증가
                        setattr(ally, 'morale_boost_turns', 3)
                print(f"🎵 아군 전체의 사기가 높아졌습니다! (공격력 8% 증가)")
                
        elif character_class == "네크로맨서" and skill.name == "생명력 흡수":
            # 가한 피해의 5% MP 회복 (제한적)
            mp_recover = int(damage * 0.05)  # 30% → 5%로 감소
            old_mp = attacker.current_mp
            max_recover = int(attacker.max_mp * 0.15)  # 최대 MP의 15%까지만 회복 가능
            actual_recover = min(mp_recover, max_recover, attacker.max_mp - attacker.current_mp)
            attacker.current_mp = min(attacker.max_mp, attacker.current_mp + actual_recover)
            if actual_recover > 0:
                print(f"💀 {attacker.name}이(가) {actual_recover} MP 회복! (제한적 흡수)")
                
                # MP 회복 (자동 애니메이션 트리거)
                # attacker.current_mp는 이미 위에서 설정됨
                
        elif character_class == "용기사" and skill.name == "화염 강타":
            # 화상 상태이상 부여 (보스는 저항)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss and random.random() < 0.75:  # 보스는 75% 저항
                print(f"🛡️ {target.name}이(가) 화상에 저항했습니다!")
            else:
                setattr(target, 'is_burning', True)
                setattr(target, 'burn_turns', 3)
                burn_damage = int(target.max_hp * 0.02) if is_boss else int(target.max_hp * 0.04)  # 보스 2%, 일반 4%
                setattr(target, 'burn_damage', burn_damage)
                print(f"🔥 {target.name}이(가) 화상에 걸렸습니다!")
            
        elif character_class == "검성" and skill.name == "검기 베기":
            # 검기가 뒤의 적들에게도 피해 (50% 위력)
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                if other_enemies:
                    splash_damage = int(damage * 0.5)
                    for enemy in other_enemies[:2]:  # 최대 2명까지
                        enemy.brave_points -= splash_damage
                        print(f"⚔️ 검기가 {enemy.name}에게도 {splash_damage} BRV 피해!")
                        
        elif character_class == "정령술사" and skill.name == "원소 탄환":
            # 랜덤 원소 속성 약점 적용
            elements = ["화염", "냉기", "번개", "독"]
            element = random.choice(elements)
            bonus_damage = int(damage * 0.2)
            target.brave_points -= bonus_damage
            print(f"🌟 {element} 속성 약점! 추가 {bonus_damage} BRV 피해!")
            
        elif character_class == "암살자" and skill.name == "그림자 강타":
            # 1. 즉사 조건 체크 (적 HP가 50% 이하일 때, 보스 제외)
            try:
                is_boss = hasattr(target, 'is_boss') and target.is_boss
                current_hp_ratio = target.current_hp / target.max_hp if target.max_hp > 0 else 1.0
                
                if not is_boss and current_hp_ratio <= 0.5:
                    # 즉사 확률 계산 (HP가 낮을수록 확률 증가)
                    instant_kill_chance = (0.5 - current_hp_ratio) * 0.8  # 최대 40% 확률
                    if random.random() < instant_kill_chance:
                        target.current_hp = 0
                        print(f"💀 [즉사] 그림자 암살! {target.name}을(를) 즉시 처치했습니다!")
                        return damage
                
                # 2. 높은 크리티컬 확률로 추가 공격 (안전한 처리)
                if random.random() < 0.4:  # 40% 확률
                    crit_damage = int(damage * 0.8)
                    # 안전한 BRV 감소 처리
                    if hasattr(target, 'brave_points'):
                        target.brave_points = max(0, target.brave_points - crit_damage)
                        gained_brave = int(crit_damage * 0.33)
                        if hasattr(attacker, 'add_brave_points'):
                            attacker.add_brave_points(gained_brave)
                        elif hasattr(attacker, 'brave_points'):
                            attacker.brave_points = min(getattr(attacker, 'max_brave_points', 9999), 
                                                      attacker.brave_points + gained_brave)
                        print(f"🗡️ 그림자 크리티컬! 추가 {crit_damage} BRV 피해!")
                    else:
                        print(f"🗡️ 그림자 크리티컬 시도! (타겟 BRV 시스템 없음)")
            except Exception as e:
                print(f"⚠️ 암살자 그림자 강타 처리 중 오류: {e}")
                # 오류가 발생해도 기본 공격은 정상 처리되도록 함
                
        elif character_class == "기계공학자" and skill.name == "기계타격":
            # 기계 에너지 충전 효과
            if hasattr(attacker, 'machine_energy'):
                attacker.machine_energy = min(100, getattr(attacker, 'machine_energy', 0) + 10)
            else:
                attacker.machine_energy = 10
            print(f"🔧 {attacker.name}의 기계 에너지가 충전됨! (현재: {getattr(attacker, 'machine_energy', 0)})")
            
            # 정밀 타격으로 명중률 증가
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(attacker.atb_gauge * 0.15)  # 15% 절약
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"⚡ 레이저 원거리 공격으로 ATB {atb_save * 100 // self.ATB_READY_THRESHOLD}% 절약!")
                    
        elif character_class == "무당" and skill.name == "영혼 타격":
            # 방어력 무시 피해
            spirit_damage = int(damage * 0.5)
            target.brave_points -= spirit_damage
            print(f"👻 영혼 직격! 방어력 무시 {spirit_damage} 추가 BRV 피해!")
            
        elif character_class == "해적" and skill.name == "이도류 난타":
            # 30% 확률로 2회 공격
            if random.random() < 0.3:
                second_damage = int(damage * 0.8)
                target.brave_points -= second_damage
                gained_brave = int(second_damage * 0.33)
                attacker.add_brave_points(gained_brave)
                print(f"⚔️ 이도류 연속 공격! 추가 {second_damage} BRV 피해!")
                
        elif character_class == "사무라이" and skill.name == "거합 베기":
            # HP가 낮을수록 피해 증가
            hp_ratio = attacker.current_hp / attacker.max_hp
            if hp_ratio < 0.5:
                bonus_damage = int(damage * (1 - hp_ratio))
                target.brave_points -= bonus_damage
                print(f"⚔️ 각오의 일격! HP가 낮아 추가 {bonus_damage} BRV 피해!")
                
        elif character_class == "드루이드" and skill.name == "자연의 분노":
            # 공격 후 자신 HP 회복
            heal_amount = int(damage * 0.2)
            attacker.heal(heal_amount)
            print(f"🌿 자연의 가호로 {attacker.name}이(가) {heal_amount} HP 회복!")
            
        elif character_class == "철학자" and skill.name == "논리적 반박":
            # 다음 턴 회피율 증가
            setattr(attacker, 'temp_dodge_bonus', getattr(attacker, 'temp_dodge_bonus', 0) + 0.3)
            setattr(attacker, 'dodge_bonus_turns', 2)
            print(f"🧠 논리적 분석으로 {attacker.name}의 회피율이 증가!")
            
        elif character_class == "시간술사" and skill.name == "시간 조작":
            # 적의 다음 턴 지연 (ATB 곱적용 감소)
            if hasattr(target, 'atb_gauge'):
                current_atb_mult = getattr(target, 'temp_atb_multiplier', 1.0)
                is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
                reduction = 0.85 if is_boss else 0.7  # 보스 15% 감소, 일반 30% 감소
                setattr(target, 'temp_atb_multiplier', current_atb_mult * reduction)
                setattr(target, 'time_slow_turns', 3)
                reduction_percent = int((1 - reduction) * 100)
                print(f"⏱️ {target.name}의 시간이 {reduction_percent}% 지연되었습니다!")
                
        elif character_class == "연금술사" and skill.name == "화학 폭발":
            # 주변 적들에게 연쇄 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                if other_enemies:
                    chain_damage = int(damage * 0.3)
                    for enemy in other_enemies:
                        enemy.brave_points -= chain_damage
                        print(f"💥 화학 폭발이 {enemy.name}에게 {chain_damage} BRV 피해!")
                        
        elif character_class == "검투사" and skill.name == "투기장 기술":
            # 반격 준비 상태
            setattr(attacker, 'counter_ready', True)
            setattr(attacker, 'counter_turns', 2)
            print(f"🏛️ {attacker.name}이(가) 반격 태세를 갖췄습니다!")
            
        elif character_class == "기사" and skill.name == "창 돌격":
            # 관통 피해로 뒤의 적에게도 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                enemy_index = self._current_enemies.index(target)
                if enemy_index < len(self._current_enemies) - 1:
                    next_enemy = self._current_enemies[enemy_index + 1]
                    if next_enemy.current_hp > 0:
                        pierce_damage = int(damage * 0.6)
                        next_enemy.brave_points -= pierce_damage
                        print(f"🏇 창이 관통하여 {next_enemy.name}에게 {pierce_damage} BRV 피해!")
                        
        elif character_class == "신관" and skill.name == "축복의 빛":
            # 아군 전체에게 축복 버프 부여
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally.current_hp > 0:
                        setattr(ally, 'blessed', True)
                        setattr(ally, 'blessed_turns', 3)
                print(f"🌟 아군 전체가 축복을 받았습니다!")
                
        elif character_class == "마검사" and skill.name == "마법검기":
            # 물리와 마법 피해 동시 적용
            magic_damage = int(damage * 0.5)
            target.brave_points -= magic_damage
            print(f"⚡ 마법검기 추가 피해! {magic_damage} BRV 마법 피해!")
            
        elif character_class == "차원술사" and skill.name == "차원 균열":
            # 공간 왜곡으로 적의 정확도 감소
            setattr(target, 'accuracy_debuff', getattr(target, 'accuracy_debuff', 0) + 0.2)
            setattr(target, 'accuracy_debuff_turns', 3)
            print(f"🌀 {target.name}의 공간이 왜곡되어 정확도가 감소!")
            
        elif character_class == "광전사" and skill.name == "분노의 폭발":
            # HP가 낮을수록 추가 공격
            hp_ratio = attacker.current_hp / attacker.max_hp
            if hp_ratio < 0.3:  # 30% 이하일 때
                bonus_attacks = 2
                for i in range(bonus_attacks):
                    bonus_damage = int(damage * 0.4)
                    target.brave_points -= bonus_damage
                    print(f"😤 광폭화 연타 {i+1}! {bonus_damage} BRV 피해!")
                print(f"💀 광전사의 광기가 폭발했습니다!")
                
        elif character_class == "최종보스" and skill.name == "마사무네 베기":
            # 세피로스의 마사무네 베기 - 전설적인 위력
            print("⚔️💀 마사무네 베기! 전설의 검이 빛납니다!")
            
            # 추가 BRV 피해 (크리티컬 확률 증가)
            import random
            if random.random() < 0.7:  # 70% 크리티컬 확률
                critical_damage = int(damage * 0.5)
                target.brave_points -= critical_damage
                print(f"💥 마사무네 크리티컬! 추가 {critical_damage} BRV 피해!")
            
            # 적의 BRV 회복 저해 (3턴)
            setattr(target, 'brv_regen_blocked', True)
            setattr(target, 'brv_regen_block_turns', 3)
            print(f"🗡️ {target.name}의 용기가 꺾였습니다! (BRV 회복 불가 3턴)")
            
            # 세피로스 자신의 BRV 대폭 증가
            masamune_bonus = int(attacker.max_brv * 0.3)
            attacker.brave_points = min(attacker.max_brv, attacker.brave_points + masamune_bonus)
            print(f"✨ 마사무네의 힘! 세피로스 BRV +{masamune_bonus}!")
            
        elif character_class == "최종보스" and skill.name == "옥타슬래시":
            # 세피로스의 옥타슬래시 - 8연속 타격
            print("⚔️⚔️⚔️ 옥타슬래시! 세피로스의 8연속 검격!")
            
            # 8번 연속 공격 (각 타격은 기본 위력의 30%)
            total_octa_damage = 0
            for hit in range(8):
                hit_damage = int(damage * 0.3)
                target.brave_points -= hit_damage
                total_octa_damage += hit_damage
                print(f"🗡️ {hit + 1}타격: {hit_damage} BRV 피해!")
                
                # 타격마다 10% 확률로 추가 효과
                import random
                if random.random() < 0.1:  # 10% 확률
                    bonus_damage = int(hit_damage * 0.5)
                    target.brave_points -= bonus_damage
                    total_octa_damage += bonus_damage
                    print(f"💥 {hit + 1}타격 크리티컬! +{bonus_damage} BRV 피해!")
            
            print(f"⚔️💫 옥타슬래시 총 피해: {total_octa_damage} BRV!")
            
            # 연속 타격으로 인한 속도 감소 디버프 (대상)
            setattr(target, 'speed_debuff', getattr(target, 'speed_debuff', 0) + 0.3)
            setattr(target, 'speed_debuff_turns', 4)
            print(f"🌀 {target.name}이(가) 연속 타격에 압도되어 속도가 감소!")
        
        # 🧪 도적 전용: 모든 BRV 공격 시 venom_power 증가 (기본 효과)
        if character_class == "도적" and skill.name not in ["맹독침"]:  # 맹독침은 이미 위에서 처리됨
            if hasattr(attacker, 'venom_power') and hasattr(attacker, 'venom_power_max'):
                # 공격력의 일부(2%)만큼 venom 증가 (최소 1, 최대 8) - 일반 공격은 약간 적게
                attacker_attack = getattr(attacker, 'physical_attack', 100)
                venom_gain = max(1, min(8, int(attacker_attack * 0.02)))
                old_venom = attacker.venom_power
                attacker.venom_power = min(attacker.venom_power + venom_gain, attacker.venom_power_max)
                
                # venom 증가 메시지 표시 (간소화)
                if attacker.venom_power > old_venom:
                    new_venom = attacker.venom_power
                    gain_amount = new_venom - old_venom
                    print(f"🧪 도적의 독액 축적: Venom +{gain_amount} ({new_venom}/{attacker.venom_power_max})")
                    
                    # venom이 최대치에 도달했을 때 특별 메시지
                    if attacker.venom_power >= attacker.venom_power_max:
                        print(f"💀 [VENOM MAX] 도적의 독액이 최고조에 달했습니다!")
        
        # 🎯 중요: Brave 공격 완료 시 행동 완료 플래그 설정
        self._last_action_completed = True
        print(f"✅ {attacker.name}의 Brave 공격이 완료되었습니다!")
        
    def _get_class_specific_hp_attack(self, character: Character):
        """직업별 특화된 HP 공격 반환 (28개 직업 완전 지원)"""
        from .brave_system import BraveSkill
        
        character_class = getattr(character, 'character_class', '전사')
        
        # 세피로스 전용 다중 HP 공격 시스템
        if character_class == "최종보스" and hasattr(character, 'boss_abilities'):
            import random
            boss_hp_attacks = [
                {"name": "슈퍼노바", "power": 2.5, "desc": "항성을 파괴하는 세피로스의 궁극기, 모든 적에게 절대적인 피해"},
                {"name": "절망의 날개", "power": 2.0, "desc": "절망의 검은 날개로 적의 희망을 산산조각내는 공격"},
                {"name": "차원 붕괴", "power": 1.8, "desc": "차원 자체를 붕괴시켜 존재를 말소하는 금기의 마법"},
                {"name": "메테오", "power": 2.2, "desc": "거대한 운석을 소환하여 파멸적인 충격을 가하는 마법"}
            ]
            selected_attack = random.choice(boss_hp_attacks)
            return BraveSkill(
                selected_attack["name"], 
                BraveAttackType.HP, 
                0.0, 
                selected_attack["power"], 
                description=selected_attack["desc"]
            )
        
        # 직업별 HP 공격 정의 (28개 직업) - 전사는 new_skill_system.py에서 관리
        class_hp_attacks = {
            "아크메이지": BraveSkill("마력 폭발", BraveAttackType.HP, 0.0, 1.2, description="마력을 폭발시켜 주변 적들에게도 피해"),
            "궁수": BraveSkill("정밀 관통사격", BraveAttackType.HP, 0.0, 1.0, description="강력한 화살로 적을 관통, 뒤의 적들에게도 피해"),
            "도적": BraveSkill("독혈촉진", BraveAttackType.HP, 0.0, 1.2, description="적의 독을 촉진시켜 남은 독 피해의 일부를 즉시 가하는 공격"),
            "성기사": BraveSkill("심판의 빛", BraveAttackType.HP, 0.0, 1.1, description="성스러운 빛으로 공격하며 아군 전체 상태이상 해제"),
            "암흑기사": BraveSkill("흡혈 강타", BraveAttackType.HP, 0.0, 1.15, description="강력한 흡혈 공격으로 대량 HP 회복"),
            "몽크": BraveSkill("폭렬권", BraveAttackType.HP, 0.0, 1.0, description="표식이 붙은 적 공격 시 표식 폭발로 추가 피해"),
            "바드": BraveSkill("영혼의 노래", BraveAttackType.HP, 0.0, 0.9, description="적의 영혼을 뒤흔들며 아군 전체 회복"),
            "네크로맨서": BraveSkill("영혼 흡수", BraveAttackType.HP, 0.0, 1.1, description="적의 영혼을 흡수하여 강력한 피해와 함께 MP 대량 회복"),
            "용기사": BraveSkill("드래곤 브레스", BraveAttackType.HP, 0.0, 1.3, description="용의 숨결로 광역 화염 피해"),
            "검성": BraveSkill("일섬", BraveAttackType.HP, 0.0, 1.25, description="완벽한 검기로 일격에 베어넘기는 기술"),
            "정령술사": BraveSkill("원소 융합", BraveAttackType.HP, 0.0, 1.15, description="모든 원소를 융합한 파괴적인 공격"),
            "암살자": BraveSkill("그림자 처형", BraveAttackType.HP, 0.0, 1.8, description="모든 그림자를 소모하여 그림자 수만큼 위력이 증폭되는 궁극 암살술"),
            "기계공학자": BraveSkill("에너지방출", BraveAttackType.HP, 0.0, 1.2, description="축적된 에너지를 방출하여 적에게 기계적 피해를 가함"),
            "무당": BraveSkill("영혼 분리", BraveAttackType.HP, 0.0, 1.0, description="적의 영혼을 직접 공격하여 방어력 완전 무시"),
            "해적": BraveSkill("해적의 보물", BraveAttackType.HP, 0.0, 1.1, description="숨겨진 보물 무기로 연속 공격"),
            "사무라이": BraveSkill("무사도 비의", BraveAttackType.HP, 0.0, 1.5, description="HP가 낮을수록 강해지는 필사의 일격"),
            "드루이드": BraveSkill("자연의 심판", BraveAttackType.HP, 0.0, 1.0, description="자연의 힘으로 적을 심판하며 아군 전체 회복"),
            "철학자": BraveSkill("진리의 깨달음", BraveAttackType.HP, 0.0, 0.8, description="논리적 공격으로 적의 약점을 정확히 타격"),
            "시간술사": BraveSkill("시간 정지", BraveAttackType.HP, 0.0, 1.1, description="시간을 정지시켜 연속 공격"),
            "연금술사": BraveSkill("대폭발 반응", BraveAttackType.HP, 0.0, 1.3, description="화학 반응으로 거대한 폭발 생성"),
            "검투사": BraveSkill("검투장의 피날레", BraveAttackType.HP, 0.0, 1.2, description="관중들의 환호 속에서 화려한 마무리"),
            "기사": BraveSkill("성스러운 돌격", BraveAttackType.HP, 0.0, 1.15, description="신성한 힘이 깃든 창으로 돌격"),
            "신관": BraveSkill("신의 심판", BraveAttackType.HP, 0.0, 0.9, description="적을 심판하면서 아군 전체 HP 회복"),
            "마검사": BraveSkill("마검 오의", BraveAttackType.HP, 0.0, 1.25, description="물리와 마법의 완벽한 융합 기술"),
            "차원술사": BraveSkill("차원 붕괴", BraveAttackType.HP, 0.0, 1.2, description="차원을 붕괴시켜 공간 자체로 공격"),
            "광전사": BraveSkill("최후의 광기", BraveAttackType.HP, 0.0, 1.6, description="모든 것을 내던진 광폭한 최후의 일격"),
            "최종보스": BraveSkill("슈퍼노바", BraveAttackType.HP, 0.0, 2.5, description="항성을 파괴하는 세피로스의 궁극기, 모든 적에게 절대적인 피해"),
        }
        
        return class_hp_attacks.get(character_class, BraveSkill("기본 HP 공격", BraveAttackType.HP, 0.0, 0.8))
        
    def _apply_class_specific_hp_effects(self, attacker: Character, target: Character, skill, hp_damage: int):
        """직업별 HP 공격 특수 효과 적용 (28개 직업 완전 지원)"""
        character_class = getattr(attacker, 'character_class', '전사')
        
        if character_class == "전사" and skill.name == "파괴의 일격":
            # 방어구 내구도 대폭 감소
            if hasattr(target, 'equipped_armor') and target.equipped_armor:
                if hasattr(target.equipped_armor, 'durability'):
                    durability_loss = 15
                    target.equipped_armor.durability = max(0, target.equipped_armor.durability - durability_loss)
                    print(f"🛡️ {target.name}의 방어구 내구도가 {durability_loss} 감소!")
                    
        elif character_class == "아크메이지" and skill.name == "마력 폭발":
            # 주변 적들에게도 피해 (원본의 50%)
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for other_enemy in other_enemies[:2]:  # 최대 2명까지
                    splash_damage = int(hp_damage * 0.5)
                    other_enemy.take_damage(splash_damage)
                    print(f"💥 마력 폭발 연쇄 피해! {other_enemy.name}이(가) {splash_damage} 피해!")
                    
        elif character_class == "궁수" and skill.name == "정밀 관통사격":
            # 뒤의 적들에게 관통 피해 (원본의 70%) + 원거리 ATB 절약
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for other_enemy in other_enemies:
                    pierce_damage = int(hp_damage * 0.7)
                    other_enemy.take_damage(pierce_damage)
                    print(f"🏹 관통 피해! {other_enemy.name}이(가) {pierce_damage} 피해!")
            
            # 원거리 HP 공격 - ATB 소모량 감소
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(self.ATB_MAX * 0.25)  # 25% 절약 (HP 공격이므로 고정값)
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"🎯 원거리 HP 공격으로 ATB {atb_save * 100 // self.ATB_READY_THRESHOLD}% 절약!")
                
        elif character_class == "도적" and skill.name == "독혈촉진":
            # 독혈촉진 - 적의 독을 촉진시켜 남은 독 피해의 60%를 즉시 가함 + 독 스택 소모
            current_poison_turns = getattr(target, 'poison_turns', 0)
            current_poison_damage = getattr(target, 'poison_damage', 0)
            
            # 도적의 독 스택으로 위력 증가
            poison_stacks = getattr(attacker, 'poison_stacks', 0)
            stack_multiplier = 1.0 + (poison_stacks * 0.01)  # 스택당 1% 증가
            
            if current_poison_turns > 0 and current_poison_damage > 0:
                # 남은 독 피해 계산 후 촉진
                remaining_poison = current_poison_turns * current_poison_damage
                triggered_damage = int(remaining_poison * 0.6 * stack_multiplier)
                
                target.take_damage(triggered_damage)
                print(f"🩸 독혈촉진! 남은 독 {remaining_poison} 중 {triggered_damage} 피해를 즉시 가했습니다!")
                
                # 독 스택 소모하여 추가 효과
                if poison_stacks >= 50:
                    stack_consume = min(poison_stacks, 50)
                    setattr(attacker, 'poison_stacks', poison_stacks - stack_consume)
                    bonus_damage = int(stack_consume * 2)  # 스택당 2 추가 피해
                    target.take_damage(bonus_damage)
                    print(f"💀 독 스택 {stack_consume} 소모하여 추가 {bonus_damage} 피해!")
                
                # 독 지속시간을 절반으로 줄이고 약화된 독 유지
                setattr(target, 'poison_turns', max(1, current_poison_turns // 2))
                setattr(target, 'poison_damage', max(1, int(current_poison_damage * 0.7)))
                print(f"💚 독이 약화되었습니다. (턴: {current_poison_turns} → {getattr(target, 'poison_turns')}, 피해: {current_poison_damage} → {getattr(target, 'poison_damage')})")
            else:
                print(f"💀 {target.name}에게 촉진할 독이 없습니다!")
                # 독이 없으면 새로운 독 부여
                setattr(target, 'is_poisoned', True)
                setattr(target, 'poison_turns', 3)
                base_poison = int(target.max_hp * 0.05)
                setattr(target, 'poison_damage', base_poison)
                print(f"☠️ 새로운 독을 주입했습니다! (3턴, {base_poison} 피해)")
                
                # 독 스택 축적
                poison_stack_gain = int(base_poison * 0.15)
                current_stacks = getattr(attacker, 'poison_stacks', 0)
                max_stacks = getattr(attacker, 'max_poison_stacks', 100)
                new_stacks = min(current_stacks + poison_stack_gain, max_stacks)
                setattr(attacker, 'poison_stacks', new_stacks)
                print(f"💚 독 스택 축적: {current_stacks} → {new_stacks} (+{poison_stack_gain})")
                
        elif character_class == "성기사" and skill.name == "심판의 빛":
            # 아군 전체 상태이상 해제 및 회복
            # 공격자가 플레이어 파티에 속해있는지 정확히 확인
            is_player_party_member = False
            if hasattr(self, '_current_party') and self._current_party:
                is_player_party_member = attacker in self._current_party
            
            if is_player_party_member:
                # 플레이어 성기사 - 플레이어 파티만 회복
                target_party = self._current_party
            else:
                # 적군 성기사 - 회복 효과 없음 (적은 이 기술 사용 불가)
                target_party = None
                
            if target_party:
                for ally in target_party:
                    if ally.current_hp > 0:
                        # 상태이상 해제
                        setattr(ally, 'is_poisoned', False)
                        setattr(ally, 'is_burning', False)
                        setattr(ally, 'is_stunned', False)
                        # 소량 회복
                        heal_amount = int(ally.max_hp * 0.1)
                        ally.heal(heal_amount)
                print(f"✨ 성스러운 빛으로 아군 전체 정화 및 회복!")
                        
        elif character_class == "암흑기사" and skill.name == "흡혈 강타":
            # 가한 피해의 60% HP 회복
            heal_amount = int(hp_damage * 0.6)
            attacker.heal(heal_amount)
            print(f"🩸 강력한 흡혈로 {attacker.name}이(가) {heal_amount} HP 회복!")
            
        elif character_class == "몽크" and skill.name == "폭렬권":
            # 타격 표식 폭발 추가 피해 (현재 HP 비율 기반)
            marks = getattr(target, 'strike_marks', 0)
            if marks > 0:
                is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
                if is_boss:
                    explosion_damage = int(target.current_hp * 0.04 * marks)  # 보스는 중첩당 현재 HP의 4%
                else:
                    explosion_damage = int(target.current_hp * 0.08 * marks)  # 일반은 중첩당 현재 HP의 8%
                target.take_damage(explosion_damage)
                setattr(target, 'strike_marks', 0)  # 표식 소모
                print(f"💥 표식 폭발! {marks}개 표식으로 {explosion_damage} 추가 피해!")
                
        elif character_class == "바드" and skill.name == "영혼의 노래":
            # 적에게 피해 + 아군 전체 회복 및 버프
            # ⚠️ 중요: 공격받은 적은 회복에서 제외!
            
            # 파티 멤버 확인을 통해 정확한 아군 구분
            is_player_party_member = False
            if hasattr(self, '_current_party') and self._current_party:
                is_player_party_member = attacker in self._current_party
            
            if is_player_party_member:
                # 플레이어 파티의 바드 - 플레이어 파티만 회복 (적과 공격받은 대상 완전 제외)
                target_party = []
                for ally in self._current_party:
                    if ally and ally.current_hp > 0 and ally != target and ally != attacker:  # 자기 자신도 제외
                        # 추가 안전 체크: 적군이 아닌지 확인
                        if not hasattr(ally, 'character_class') or ally.character_class != 'Enemy':
                            target_party.append(ally)
                party_name = "아군"
            else:
                # 적군 바드 - 아무도 회복 안됨 (적군끼리 회복 금지)
                target_party = []
                party_name = "적군"
                print(f"🎵 적군 바드의 영혼의 노래 - 회복 효과 없음")
                
            if target_party:
                healed_count = 0
                for ally in target_party:
                    if ally and ally.current_hp > 0:
                        heal_amount = int(ally.max_hp * 0.12)  # 12% 회복
                        ally.heal(heal_amount)
                        setattr(ally, 'temp_attack_bonus', getattr(ally, 'temp_attack_bonus', 0) + 10)
                        healed_count += 1
                if healed_count > 0:
                    print(f"🎵 영혼의 노래로 {party_name} {healed_count}명 회복 및 공격력 증가!")
            # 적에게는 정상적으로 피해를 줌 (회복 안됨)
                
        elif character_class == "네크로맨서" and skill.name == "영혼 흡수":
            # MP 제한적 회복 및 적의 MP 흡수
            mp_drain = int(hp_damage * 0.2)  # 30% → 20%로 감소
            if hasattr(target, 'current_mp'):
                # 대상의 MP 감소
                old_target_mp = target.current_mp
                drained_mp = min(target.current_mp, mp_drain)
                target.current_mp -= drained_mp
                
                # MP 탈취 (자동 애니메이션 트리거)
                # target.current_mp는 이미 위에서 설정됨
                
                # 회복량 제한 및 회복
                old_attacker_mp = attacker.current_mp
                max_recover = int(attacker.max_mp * 0.2)  # 최대 MP의 20%까지만
                actual_recover = min(drained_mp, max_recover, attacker.max_mp - attacker.current_mp)
                attacker.current_mp = min(attacker.max_mp, attacker.current_mp + actual_recover)
                print(f"💀 영혼 흡수로 {actual_recover} MP 탈취! (제한적 흡수)")
                
                # MP 회복 (자동 애니메이션 트리거)
                # attacker.current_mp는 이미 위에서 설정됨
                
        elif character_class == "용기사" and skill.name == "드래곤 브레스":
            # 광역 화염 피해 및 화상 (보스는 상태이상 저항)
            if hasattr(self, '_current_enemies') and self._current_enemies:
                for enemy in self._current_enemies:
                    if enemy != target and enemy.current_hp > 0:
                        fire_damage = int(hp_damage * 0.4)
                        enemy.take_damage(fire_damage)
                        
                        # 화상 효과 (보스는 저항)
                        is_boss = getattr(enemy, 'is_boss', False) or enemy.max_hp > 2000
                        if not is_boss or random.random() > 0.8:  # 보스 80% 저항
                            setattr(enemy, 'is_burning', True)
                            setattr(enemy, 'burn_turns', 4)
                            burn_damage = int(enemy.max_hp * 0.02) if is_boss else int(enemy.max_hp * 0.04)
                            setattr(enemy, 'burn_damage', burn_damage)
                            print(f"🔥 드래곤 브레스! {enemy.name}이(가) {fire_damage} 화염 피해 및 화상!")
                        else:
                            print(f"🔥 드래곤 브레스! {enemy.name}이(가) {fire_damage} 화염 피해! (화상 저항)")
                        
        elif character_class == "검성" and skill.name == "일섬":
            # 완벽한 베기로 방어력 무시 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss:
                ignore_damage = int(target.current_hp * 0.15)  # 보스는 현재 HP의 15%
            else:
                ignore_damage = int(target.current_hp * 0.35)  # 일반 적은 현재 HP의 35%
            target.take_damage(ignore_damage)
            print(f"⚔️ 완벽한 일섬! 방어력 무시 {ignore_damage} 고정 피해!")
            
        elif character_class == "정령술사" and skill.name == "원소 융합":
            # 모든 원소 효과 동시 적용 (보스는 저항)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            
            # 화염 효과
            if not is_boss or random.random() > 0.75:  # 보스 75% 저항
                setattr(target, 'is_burning', True)
                setattr(target, 'burn_turns', 3)
                print(f"🔥 화염 효과 적용!")
            elif is_boss:
                print(f"🛡️ {target.name}이(가) 화염에 저항!")
                
            # 냉기 효과 (속도 감소) - 디버프이므로 보스에게도 적용
            current_speed_mult = getattr(target, 'temp_speed_multiplier', 1.0)
            reduction = 0.85 if is_boss else 0.7  # 보스 15% 감소, 일반 30% 감소
            setattr(target, 'temp_speed_multiplier', current_speed_mult * reduction)
            setattr(target, 'speed_debuff_turns', 3)
            
            # 번개 효과 (기절 확률)
            stun_chance = 0.1 if is_boss else 0.3  # 보스 10%, 일반 30%
            if random.random() < stun_chance:
                setattr(target, 'is_stunned', True)
                print(f"⚡ 번개로 기절!")
            elif is_boss:
                print(f"🛡️ {target.name}이(가) 기절에 저항!")
                
            print(f"🌟 원소 융합! {target.name}에게 다중 원소 효과 적용!")
            
        elif character_class == "암살자" and skill.name == "그림자 처형":
            # 그림자에서 연속 공격
            for i in range(3):  # 3연속 공격
                shadow_damage = int(hp_damage * 0.4)
                target.take_damage(shadow_damage)
                print(f"🗡️ 그림자 연격 {i+1}: {shadow_damage} 피해!")
                
        elif character_class == "기계공학자" and skill.name == "에너지방출":
            # 축적된 기계 에너지를 소모하여 강력한 폭발 + 범위 피해
            machine_energy = getattr(attacker, 'machine_energy', 0)
            if machine_energy > 0:
                # 에너지량에 따른 추가 피해
                energy_bonus = int(hp_damage * (machine_energy / 100))
                target.take_damage(energy_bonus)
                print(f"🔧 기계 에너지 방출! 추가 피해 {energy_bonus}!")
                
                # 에너지 방출 시 주변 적들에게도 피해
                if hasattr(self, '_current_enemies') and self._current_enemies:
                    for enemy in self._current_enemies:
                        if enemy != target and enemy.current_hp > 0:
                            splash_damage = int(energy_bonus * 0.5)
                            enemy.take_damage(splash_damage)
                            print(f"⚡ 에너지 폭발! {enemy.name}이(가) {splash_damage} 피해!")
                
                # 기계 에너지 소모
                attacker.machine_energy = 0
                print(f"🔧 기계 에너지가 모두 소모되었습니다!")
            
            # 에너지 방출 후 ATB 보너스
            if hasattr(attacker, 'atb_gauge'):
                atb_save = int(self.ATB_MAX * 0.15)  # 15% 절약
                attacker.atb_gauge = min(self.ATB_MAX, attacker.atb_gauge + atb_save)
                print(f"⚡ 에너지방출로 ATB {atb_save * 100 // self.ATB_READY_THRESHOLD}% 절약!")
                            
        elif character_class == "무당" and skill.name == "영혼 분리":
            # 방어력 완전 무시 및 영혼 디버프 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss:
                soul_damage = int(target.current_hp * 0.12)  # 보스는 현재 HP의 12%
            else:
                soul_damage = int(target.current_hp * 0.28)  # 일반 적은 현재 HP의 28%
            target.take_damage(soul_damage)
            setattr(target, 'soul_weakness', True)  # 영혼 약화 (모든 저항 감소)
            setattr(target, 'soul_weakness_turns', 5)
            print(f"👻 영혼 분리! {soul_damage} 고정 피해 및 영혼 약화!")
            
        elif character_class == "해적" and skill.name == "해적의 보물":
            # 숨겨진 보물 무기들로 연속 공격
            weapons = ["구식 대포", "저주받은 검", "크라켄의 촉수", "바다뱀의 독침"]
            for weapon in weapons:
                weapon_damage = int(hp_damage * 0.3)
                target.take_damage(weapon_damage)
                print(f"🏴‍☠️ {weapon} 공격! {weapon_damage} 피해!")
                
        elif character_class == "사무라이" and skill.name == "무사도 비의":
            # HP가 낮을수록 강해지는 필사의 일격
            hp_ratio = attacker.current_hp / attacker.max_hp
            desperation_multiplier = 2.0 - hp_ratio  # HP가 낮을수록 최대 2배
            bonus_damage = int(hp_damage * (desperation_multiplier - 1))
            target.take_damage(bonus_damage)
            print(f"⚔️ 무사도 비의! 필사의 각오로 {bonus_damage} 추가 피해!")
            # 반격 확률 증가
            setattr(attacker, 'temp_counter_rate', 0.5)
            
        elif character_class == "드루이드" and skill.name == "자연의 심판":
            # 자연의 힘으로 심판하며 아군 회복
            # ⚠️ 중요: 공격받은 적은 회복에서 제외!
            is_player_party_member = False
            if hasattr(self, '_current_party') and self._current_party:
                is_player_party_member = attacker in self._current_party
            
            if is_player_party_member:
                # 플레이어 드루이드 - 플레이어 파티만 회복 (공격받은 적 제외)
                target_party = [ally for ally in self._current_party if ally != target]
            else:
                # 적군 드루이드 - 회복 효과 없음 (적은 이 기술 사용 불가)
                target_party = None
                
            if target_party:
                healed_count = 0
                for ally in target_party:
                    if ally.current_hp > 0 and ally != target:  # 공격받은 대상은 확실히 제외
                        nature_heal = int(ally.max_hp * 0.2)
                        ally.heal(nature_heal)
                        # 자연의 축복 (독/화상 저항)
                        setattr(ally, 'nature_blessing', True)
                        setattr(ally, 'nature_blessing_turns', 3)
                        healed_count += 1
                print(f"🌿 자연의 심판! 아군 {healed_count}명 회복 및 자연의 축복! (공격받은 {target.name} 제외)")
                
        elif character_class == "철학자" and skill.name == "진리의 깨달음":
            # 논리적 약점 공격으로 정확한 피해 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss:
                weakness_damage = int(target.current_hp * 0.08)  # 보스는 현재 HP의 8%
            else:
                weakness_damage = int(target.current_hp * 0.22)  # 일반 적은 현재 HP의 22%
            target.take_damage(weakness_damage)
            # 적의 모든 버프 해제 (디버프는 보스에게도 적용)
            if hasattr(target, 'temp_attack_bonus'):
                setattr(target, 'temp_attack_bonus', 0)
            if hasattr(target, 'temp_defense_bonus'):
                setattr(target, 'temp_defense_bonus', 0)
            print(f"🧠 진리의 깨달음! 약점 {weakness_damage} 피해 및 모든 버프 해제!")
            
        elif character_class == "시간술사" and skill.name == "시간 정지":
            # 시간 정지 중 연속 공격
            for i in range(4):  # 4회 연속 공격
                time_damage = int(hp_damage * 0.25)
                target.take_damage(time_damage)
                print(f"⏰ 시간 정지 공격 {i+1}: {time_damage} 피해!")
            # 적의 ATB 게이지 곱적용 감소
            if hasattr(target, 'atb_gauge'):
                current_atb_mult = getattr(target, 'temp_atb_multiplier', 1.0)
                is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
                time_reduction = 0.7 if is_boss else 0.5  # 보스 30% 감소, 일반 50% 감소
                setattr(target, 'temp_atb_multiplier', current_atb_mult * time_reduction)
                setattr(target, 'time_stop_turns', 2)
                reduction_percent = int((1 - time_reduction) * 100)
                print(f"⏱️ {target.name}의 시간이 {reduction_percent}% 크게 지연되었습니다!")
                
        elif character_class == "연금술사" and skill.name == "대폭발 반응":
            # 거대한 폭발로 광역 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                for enemy in self._current_enemies:
                    if enemy.current_hp > 0:
                        explosion_damage = int(hp_damage * 0.8) if enemy == target else int(hp_damage * 0.5)
                        enemy.take_damage(explosion_damage)
                        # 폭발 후유증 (방어력 곱적용 감소)
                        setattr(enemy, 'explosion_weakness', True)
                        setattr(enemy, 'explosion_weakness_turns', 3)
                        current_def_mult = getattr(enemy, 'temp_defense_multiplier', 1.0)
                        is_boss = getattr(enemy, 'is_boss', False) or enemy.max_hp > 2000
                        def_reduction = 0.9 if is_boss else 0.8  # 보스 10% 감소, 일반 20% 감소
                        setattr(enemy, 'temp_defense_multiplier', current_def_mult * def_reduction)
                        if enemy != target:
                            print(f"💥 대폭발 연쇄! {enemy.name}이(가) {explosion_damage} 피해!")
                reduction_percent = int((1 - (0.9 if any(getattr(e, 'is_boss', False) or e.max_hp > 2000 for e in self._current_enemies) else 0.8)) * 100)
                print(f"💥 연금술 대폭발! 모든 적이 방어력 {reduction_percent}% 감소!")
                
        elif character_class == "검투사" and skill.name == "검투장의 피날레":
            # 화려한 연속 기술
            combo_attacks = ["검 휘두르기", "방패 돌격", "회전 베기", "마무리 찌르기"]
            for attack in combo_attacks:
                combo_damage = int(hp_damage * 0.3)
                target.take_damage(combo_damage)
                print(f"🏛️ {attack}! {combo_damage} 피해!")
            # 관중의 환호로 아군 사기 증진
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    setattr(ally, 'crowd_cheer_bonus', True)
                    setattr(ally, 'temp_attack_bonus', getattr(ally, 'temp_attack_bonus', 0) + 15)
                print(f"👏 관중의 환호로 아군 전체 공격력 증가!")
                
        elif character_class == "기사" and skill.name == "성스러운 돌격":
            # 신성한 힘의 창 돌격
            holy_damage = int(hp_damage * 0.5)  # 추가 성스러운 피해
            target.take_damage(holy_damage)
            print(f"✨ 성스러운 힘 추가 피해: {holy_damage}!")
            # 관통으로 뒤의 적들에게도 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for other_enemy in other_enemies:
                    pierce_damage = int(hp_damage * 0.4)
                    other_enemy.take_damage(pierce_damage)
                    print(f"🛡️ 성스러운 돌격 관통! {other_enemy.name}이(가) {pierce_damage} 피해!")
                    
        elif character_class == "신관" and skill.name == "신의 심판":
            # 신의 심판: 적에게 피해 + 아군 전체 회복 (회복량 감소)
            # ⚠️ 중요: 공격받은 적은 회복에서 제외!
            is_player_party_member = False
            if hasattr(self, '_current_party') and self._current_party:
                is_player_party_member = attacker in self._current_party
            
            if is_player_party_member:
                # 플레이어 신관 - 플레이어 파티만 회복 (공격받은 적 제외)
                target_party = [ally for ally in self._current_party if ally != target]
            else:
                # 적군 신관 - 회복 효과 없음 (적은 이 기술 사용 불가)
                target_party = None
                
            if target_party:
                healed_allies = []
                healed_count = 0
                for ally in target_party:
                    if ally.current_hp > 0 and ally != target:  # 공격받은 대상은 확실히 제외
                        divine_heal = int(ally.max_hp * 0.15)  # 30% -> 15%로 감소
                        ally.heal(divine_heal)
                        healed_allies.append(f"{ally.name}({divine_heal})")
                        # 신의 가호 (모든 저항 증가)
                        setattr(ally, 'divine_protection', True)
                        setattr(ally, 'divine_protection_turns', 4)
                        healed_count += 1
                if healed_allies:
                    print(f"✨ 신의 심판! 아군 {healed_count}명 회복: {', '.join(healed_allies)} (공격받은 {target.name} 제외)")
                    print(f"🛡️ 아군 전체에게 신의 가호 부여!")
            # 적에게는 정상적으로 피해를 줌 (회복 안됨)
                
        elif character_class == "마검사" and skill.name == "마검 오의":
            # 물리와 마법의 완벽한 융합
            magic_damage = int(hp_damage * 0.7)  # 마법 추가 피해
            target.take_damage(magic_damage)
            print(f"⚡ 마법검기 융합! 마법 추가 피해: {magic_damage}!")
            # 검기 파동으로 주변 적들에게도 피해
            if hasattr(self, '_current_enemies') and self._current_enemies:
                other_enemies = [enemy for enemy in self._current_enemies if enemy != target and enemy.current_hp > 0]
                for other_enemy in other_enemies:
                    wave_damage = int(hp_damage * 0.4)
                    other_enemy.take_damage(wave_damage)
                    print(f"⚔️ 마검 파동! {other_enemy.name}이(가) {wave_damage} 피해!")
                    
        elif character_class == "차원술사" and skill.name == "차원 붕괴":
            # 차원 붕괴로 공간 자체가 공격 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            
        elif character_class == "최종보스" and skill.name == "슈퍼노바":
            # 세피로스의 궁극기 - 슈퍼노바
            print("💀🌟 슈퍼노바! 항성을 파괴하는 세피로스의 궁극 마법!")
            
            # 전체 공격 (모든 적에게 피해)
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally != target and ally.current_hp > 0:
                        supernova_damage = int(hp_damage * 0.8)  # 주 대상 외 80% 피해
                        ally.take_damage(supernova_damage)
                        print(f"🌟💥 슈퍼노바 충격파! {ally.name}이(가) {supernova_damage} 피해!")
            
            # 추가 상태이상 부여
            import random
            if random.random() < 0.8:  # 80% 확률
                setattr(target, 'is_burning', True)
                setattr(target, 'burn_turns', 5)
                setattr(target, 'burn_damage', int(target.max_hp * 0.1))
                print(f"🔥 {target.name}이(가) 항성의 불꽃에 화상을 입었습니다!")
                
            # 치명적인 디버프 (절망)
            if hasattr(target, 'physical_attack'):
                despair_debuff = int(target.physical_attack * 0.3)
                target.physical_attack = max(1, target.physical_attack - despair_debuff)
                target.magic_attack = max(1, target.magic_attack - despair_debuff)
                print(f"😱 절망의 힘! {target.name}의 공격력이 {despair_debuff} 감소!")
                
        elif character_class == "최종보스" and skill.name == "절망의 날개":
            # 세피로스의 절망의 날개 - 희망을 분쇄하는 공격
            print("🖤👹 절망의 날개! 검은 날개가 희망을 파괴합니다!")
            
            # 전체 공격 (모든 적에게 피해)
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally != target and ally.current_hp > 0:
                        despair_damage = int(hp_damage * 0.6)  # 주 대상 외 60% 피해
                        ally.take_damage(despair_damage)
                        print(f"🖤💥 절망의 날개 충격! {ally.name}이(가) {despair_damage} 피해!")
            
            # 절망 상태이상 (공격력/방어력 대폭 감소)
            import random
            if random.random() < 0.9:  # 90% 확률
                despair_debuff = int(target.physical_attack * 0.4)
                target.physical_attack = max(1, target.physical_attack - despair_debuff)
                target.physical_defense = max(1, target.physical_defense - int(despair_debuff * 0.7))
                setattr(target, 'despair_turns', 6)
                print(f"😱💔 절망에 빠진 {target.name}! 공격력 -{despair_debuff}, 방어력 감소!")
                
        elif character_class == "최종보스" and skill.name == "메테오":
            # 세피로스의 메테오 - 거대한 운석 낙하
            print("☄️🌟 메테오! 거대한 운석이 낙하합니다!")
            
            # 광역 공격 (모든 적에게 피해)
            if hasattr(self, '_current_party') and self._current_party:
                for ally in self._current_party:
                    if ally != target and ally.current_hp > 0:
                        meteor_damage = int(hp_damage * 0.7)  # 주 대상 외 70% 피해
                        ally.take_damage(meteor_damage)
                        print(f"☄️💥 메테오 충격! {ally.name}이(가) {meteor_damage} 피해!")
            
            # 운석 파편으로 지속 피해
            import random
            if random.random() < 0.8:  # 80% 확률
                setattr(target, 'meteor_fragment', True)
                setattr(target, 'meteor_fragment_turns', 4)
                setattr(target, 'meteor_fragment_damage', int(target.max_hp * 0.08))
                print(f"☄️🔥 {target.name}에게 운석 파편이 박혔습니다! (4턴간 지속 피해)")
                
        elif character_class == "최종보스" and skill.name == "차원 붕괴":
            # 세피로스의 차원 붕괴 - 존재 자체를 말소
            print("🌌💀 차원 붕괴! 존재가 무로 돌아갑니다!")
            
            # 현재 HP 비율 기반 고정 피해 (보스 특화)
            current_hp_ratio = target.current_hp / target.max_hp
            dimension_damage = int(target.max_hp * 0.25 * current_hp_ratio)  # 최대 HP의 25%
            target.take_damage(dimension_damage)
            print(f"🌀💥 차원 붕괴 추가 피해: {dimension_damage}!")
            
            # 공간 왜곡으로 모든 능력치 감소
            stat_reduction = int(target.physical_attack * 0.2)
            target.physical_attack = max(1, target.physical_attack - stat_reduction)
            target.magic_attack = max(1, target.magic_attack - stat_reduction)
            target.speed = max(1, target.speed - int(stat_reduction * 0.5))
            print(f"🌌 공간 왜곡! {target.name}의 모든 능력치 감소!")
                
        elif character_class == "차원술사" and skill.name == "차원 붕괴":
            # 차원 붕괴로 공간 자체가 공격 (현재 HP 비율 기반)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if is_boss:
                space_damage = int(target.current_hp * 0.10)  # 보스는 현재 HP의 10%
            else:
                space_damage = int(target.current_hp * 0.25)  # 일반 적은 현재 HP의 25%
            target.take_damage(space_damage)
            print(f"🌀 차원 붕괴! 공간 자체의 {space_damage} 고정 피해!")
            # 차원 왜곡으로 모든 적의 능력치 감소 (디버프는 보스에게도 적용)
            if hasattr(self, '_current_enemies') and self._current_enemies:
                for enemy in self._current_enemies:
                    if enemy.current_hp > 0:
                        setattr(enemy, 'dimension_distortion', True)
                        setattr(enemy, 'dimension_distortion_turns', 4)
                        # 곱적용 디버프
                        current_reduction = getattr(enemy, 'temp_all_stats_multiplier', 1.0)
                        setattr(enemy, 'temp_all_stats_multiplier', current_reduction * 0.8)  # 20% 감소
                print(f"🌀 차원 왜곡! 모든 적의 능력치 20% 감소!")
                
        elif character_class == "광전사" and skill.name == "최후의 광기":
            # 모든 것을 내던진 광폭한 공격
            hp_ratio = attacker.current_hp / attacker.max_hp
            madness_multiplier = 3.0 - (hp_ratio * 2)  # HP가 낮을수록 최대 3배
            madness_damage = int(hp_damage * (madness_multiplier - 1))
            target.take_damage(madness_damage)
            print(f"😡 최후의 광기! 광폭화로 {madness_damage} 추가 피해!")
            # 자신도 피해를 입지만 공격력 대폭 증가
            self_damage = int(attacker.max_hp * 0.1)
            attacker.current_hp = max(1, attacker.current_hp - self_damage)
            setattr(attacker, 'berserk_mode', True)
            setattr(attacker, 'temp_attack_bonus', getattr(attacker, 'temp_attack_bonus', 0) + 50)
            print(f"😡 광전사 모드! 공격력 대폭 증가하지만 {self_damage} 자해 피해!")
            # 30% 확률로 즉사 효과 (보스급 제외)
            is_boss = getattr(target, 'is_boss', False) or target.max_hp > 2000
            if not is_boss and random.random() < 0.3:
                target.current_hp = 0
                print(f"💀 치명적인 암살! {target.name}이(가) 즉사했습니다!")
            else:
                # 즉사하지 않으면 크리티컬 피해
                crit_bonus = int(hp_damage * 0.5)
                target.take_damage(crit_bonus, 0)
                print(f"🗡️ 치명타 추가 피해: {crit_bonus} HP!")
                
        elif character_class == "성기사" and skill.name == "심판의 빛":
            # 아군 전체 상태이상 해제 및 소량 회복
            # 공격자가 플레이어 파티에 속해있는지 정확히 확인
            is_player_party_member = False
            if hasattr(self, '_current_party') and self._current_party:
                is_player_party_member = attacker in self._current_party
            
            if is_player_party_member:
                # 플레이어 성기사 - 플레이어 파티만 회복
                target_party = self._current_party
            else:
                # 적군 성기사 - 회복 효과 없음
                target_party = None
                
            if target_party:
                for ally in target_party:
                    if ally.current_hp > 0:
                        # 상태이상 해제
                        debuffs = ['is_poisoned', 'is_burning', 'is_frozen', 'is_stunned']
                        for debuff in debuffs:
                            if hasattr(ally, debuff):
                                setattr(ally, debuff, False)
                        # 소량 회복
                        heal_amount = int(hp_damage * 0.15)
                        ally.heal(heal_amount)
                        print(f"✨ {ally.name} 상태이상 해제 & {heal_amount} HP 회복!")
                        
        elif character_class == "검사" and skill.name == "일섬":
            # 완벽한 베기로 방어력 무시 + 출혈 효과
            print(f"⚔️ 완벽한 일섬! 방어력을 무시하고 베어냅니다!")
            setattr(target, 'is_bleeding', True)
            setattr(target, 'bleeding_turns', 3)
            setattr(target, 'bleeding_damage', int(hp_damage * 0.1))
            
        elif character_class == "성직자" and skill.name == "신성한 심판":
            # 아군 전체 HP 회복
            # 공격자가 플레이어 파티에 속해있는지 정확히 확인
            is_player_party_member = False
            if hasattr(self, '_current_party') and self._current_party:
                is_player_party_member = attacker in self._current_party
            
            if is_player_party_member:
                # 플레이어 성직자 - 플레이어 파티만 회복
                target_party = self._current_party
            else:
                # 적군 성직자 - 회복 효과 없음
                target_party = None
                
            if target_party:
                heal_amount = int(hp_damage * 0.4)
                for ally in target_party:
                    if ally.current_hp > 0:
                        ally.heal(heal_amount)
                        print(f"🌟 신성한 빛이 {ally.name}을(를) {heal_amount} HP 회복!")
                        
        elif character_class == "암흑기사" and skill.name == "흡혈 강타":
            # 가한 피해의 60% HP 회복
            heal_amount = int(hp_damage * 0.6)
            attacker.heal(heal_amount)
            print(f"🩸 강력한 흡혈로 {attacker.name}이(가) {heal_amount} HP 회복!")
            
        elif character_class == "몽크" and skill.name == "폭렬권":
            # 타격 표식 폭발 효과
            strike_marks = getattr(target, 'strike_marks', 0)
            if strike_marks > 0:
                explosion_damage = strike_marks * int(hp_damage * 0.2)  # 중첩당 20% 추가 피해
                target.take_damage(explosion_damage, 0)
                setattr(target, 'strike_marks', 0)  # 표식 제거
                print(f"💥 타격 표식 {strike_marks}중첩 폭발! 추가 {explosion_damage} HP 피해!")
                
                # 표식 폭발로 아군 회복
                # 공격자가 플레이어 파티에 속해있는지 정확히 확인
                is_player_party_member = False
                if hasattr(self, '_current_party') and self._current_party:
                    is_player_party_member = attacker in self._current_party
                
                if is_player_party_member:
                    # 플레이어 몽크 - 플레이어 파티만 회복
                    target_party = self._current_party
                else:
                    # 적군 몽크 - 회복 효과 없음
                    target_party = None
                    
                if target_party:
                    heal_amount = int(explosion_damage * 0.3)
                    for ally in target_party:
                        if ally.current_hp > 0:
                            ally.heal(heal_amount)
                    print(f"✨ 표식 폭발 에너지가 아군들을 {heal_amount} HP 회복!")
        
        # 기본 공격 후 딜레이 추가
        attack_name = getattr(skill, 'name', '기본 공격') if skill else '기본 공격'
        self.add_action_pause(f"⚔️ '{attack_name}' 공격 완료!")
        
    def execute_hp_attack(self, attacker: Character, target: Character):
        """HP 공격 실행 - Brave 시스템 우선"""
        from game.error_logger import log_combat
        
        # 🔧 로그 카테고리 수정: 아군/적군 구분  
        if hasattr(self, 'current_party') and attacker in self.current_party:
            log_combat("아군행동", f"{attacker.name}이 {target.name}에게 HP 공격 실행 시작")
        else:
            log_combat("적행동", f"{attacker.name}이 {target.name}에게 HP 공격 실행 시작")
        
        # 액션 실행 플래그 설정
        self.is_action_executing = True
        
        # 직업별 기본 Brave HP 공격을 우선 사용
        skill = self._get_class_specific_hp_attack(attacker)
        
        # 스킬 이름과 정보 출력 (디버깅용)
        print(f"🔍 {attacker.name}({attacker.character_class})의 HP 공격: {skill.name}")
        
        result = self._execute_hp_attack_on_target(attacker, target, skill, True)  # BRV 소모 포함
        
        # 🏹 궁수 지원사격 트리거 (아군이 공격할 때)
        self._trigger_support_fire(attacker, target, "ally_attacking")
        
        # 🎯 중요: HP 공격 완료 시 행동 완료 플래그 설정
        self._last_action_completed = True
        print(f"✅ {attacker.name}의 HP 공격이 완료되었습니다!")
        
        # 액션 실행 완료, 플래그 해제
        self.is_action_executing = False
        
        return result
            
    def execute_area_hp_attack(self, attacker: Character, targets: List[Character], skill=None):
        """광역 HP 공격 실행 - BRV 한 번만 소모하고 모든 대상에게 동일한 파워로 공격"""
        if not targets:
            return
            
        if skill is None:
            # 직업별 기본 Brave HP 공격을 우선 사용 (광역용)
            skill = self._get_class_specific_hp_attack(attacker)
            # 광역 공격시 위력 조정
            skill.hp_multiplier *= 0.8  # 80%로 감소
        
        # BRV 소모를 미리 저장 (모든 대상에게 같은 파워로 공격하기 위해)
        stored_brave = attacker.brave_points
        
        print(f"💥 {attacker.name}의 {skill.name}으로 {len(targets)}명을 동시에 공격!")
        
        total_damage = 0
        for i, target in enumerate(targets):
            if not target.is_alive:
                continue
                
            # 첫 번째 대상이 아닌 경우 저장된 BRV 값으로 복원
            if i > 0:
                attacker.brave_points = stored_brave
            
            # 마지막 대상인지 확인 (BRV 소모는 마지막에만)
            is_last_target = (i == len(targets) - 1)
            damage = self._execute_hp_attack_on_target(attacker, target, skill, is_last_target)
            total_damage += damage
            
            # 연속공격 간 짧은 딜레이 - 더 빠르게
            time_module.sleep(0.05)  # 50ms로 단축 (200ms→50ms)
            
        print(f"💀 총 {total_damage} 데미지를 가했습니다!")
    
    def _execute_hp_attack_on_target(self, attacker: Character, target: Character, skill, consume_brave: bool = True):
        """단일 대상에게 HP 공격 실행 (내부 메서드)"""
    def _execute_hp_attack_on_target(self, attacker: Character, target: Character, skill, consume_brave: bool = True):
        """단일 대상에게 HP 공격 실행 (내부 메서드)"""
        # 스킬 사용 비주얼 이펙트
        if hasattr(self, 'visualizer') and self.visualizer:
            self.visualizer.show_skill_effect(attacker, skill.name, EffectType.SKILL)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("skill", skill_name=skill.name, character_name=attacker.name)
        
        # HP 희생 처리 (최초 1회만)
        if consume_brave and hasattr(skill, 'hp_sacrifice_rate') and skill.hp_sacrifice_rate > 0:
            sacrifice_hp = max(1, int(attacker.current_hp * skill.hp_sacrifice_rate))
            attacker.current_hp = max(1, attacker.current_hp - sacrifice_hp)
            print(f"💔 {attacker.name}이(가) {sacrifice_hp} HP를 희생하여 위력을 극대화!")
            
            # 희생한 HP만큼 추가 데미지 보너스
            attacker.temp_sacrifice_power = getattr(attacker, 'temp_sacrifice_power', 0) + sacrifice_hp * 2
        
        # 회피 체크 먼저 수행
        if self._check_dodge(attacker, target):
            # 회피 SFX 재생
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("dodge")
            elif hasattr(self, 'sound_manager'):
                self.sound_manager.play_sfx("dodge")
            
            # 회피 비주얼 이펙트 (이곳에서만 메시지 출력)
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.show_miss_effect(attacker, target)
            enhanced_battle_effect("dodge", character_name=target.name)
            return 0
        
        # 데미지 계산
        hp_damage, wound_damage = self.brave_manager.calculate_hp_damage(attacker, target, skill)
        
        # 🔥 HP 공격 데미지 배율은 damage_calculator.py에서 통합 처리됨
        # (적군 HP 공격은 이미 0.01125 배율 적용)
        
        # 특성 효과로 공격력 증가 적용
        hp_damage = trait_integrator.apply_attack_trait_effects(attacker, target, hp_damage)
        
        # 무기 숙련도 효과 적용
        if hasattr(attacker, 'equipped_weapon') and attacker.equipped_weapon:
            weapon_type = getattr(attacker.equipped_weapon, 'weapon_type', 'sword')
            hp_damage = trait_integrator.apply_weapon_mastery_effects(attacker, weapon_type, hp_damage)
        
        # 대상 방어 특성 효과 적용
        hp_damage = trait_integrator.apply_defense_trait_effects(target, hp_damage)
        
        # 특성 효과 적용
        if hasattr(attacker, 'temp_attack_bonus'):
            hp_damage = int(hp_damage * (1 + attacker.temp_attack_bonus))
            
        # 요리 효과 적용 (플레이어만)
        if hasattr(attacker, 'character_class') and attacker.character_class != "Enemy":
            try:
                multiplier, status_msg = self._get_cooking_multiplier(attacker)
                hp_damage = int(hp_damage * multiplier)
                
                # 상태 메시지 출력
                if status_msg:
                    print(status_msg)
            except Exception:
                # 요리 시스템 오류 시 무시
                pass
        
        # 생명 흡수 효과
        life_steal_rate = getattr(attacker, 'life_steal_rate', 0.0)
        life_steal_amount = int(hp_damage * life_steal_rate) if life_steal_rate > 0 else 0
        
        # Break 상태면 데미지 증가
        if hasattr(target, 'is_broken') and target.is_broken:
            hp_damage = int(hp_damage * 1.5)
            wound_damage = int(wound_damage * 1.5)
            print("💥 치명타! Break 상태로 데미지 증가!")
            
        # 공격 비주얼 이펙트
        effect_type = EffectType.CRITICAL if (hasattr(target, 'is_broken') and target.is_broken) else EffectType.PHYSICAL_ATTACK
        self.visualizer.show_attack_effect(attacker, target, hp_damage, effect_type, skill.name)
        
        # 기존 이펙트도 유지
        enhanced_battle_effect("damage", damage=hp_damage, critical=(hasattr(target, 'is_broken') and target.is_broken))
        
        # BRV 소모 먼저 처리 (HP 공격 시작 표시)
        if consume_brave:
            consumed_brave = attacker.consume_brave_points()
        
        # 데미지 적용
        actual_hp_damage = target.take_damage(hp_damage)
        print(f"💥 {target.name}에게 {actual_hp_damage} HP 데미지!")
        
        # 🎮 HP 공격 성공 진동 (중간 진동)
        if self.vibration_enabled and actual_hp_damage > 0:
            self.input_manager.vibrate_medium()
        
        target.add_wounds(wound_damage)
        
        # 생명 흡수 적용
        if life_steal_amount > 0:
            healed = attacker.heal(life_steal_amount)
            if healed > 0:
                print(f"💚 {attacker.name}이(가) {healed} HP 회복 (생명 흡수)")
        
        # 특성 트리거 효과 발동
        if hasattr(attacker, 'trigger_trait_effects'):
            if actual_hp_damage > 0:
                trait_messages = attacker.trigger_trait_effects("kill" if target.current_hp <= 0 else "attack")
                for msg in trait_messages:
                    print(f"✨ {attacker.name}: {msg}")
                
                # ⏳ 특성 효과 확인 위해 2초 대기 (엔터로 스킵 가능)
                if trait_messages and hasattr(self, 'gauge_animator'):
                    self.gauge_animator._wait_with_skip_option(2.0, "HP 공격 특성 효과 확인")
        
        # 직업별 HP 공격 특수 효과 적용
        if hasattr(skill, 'name'):
            self._apply_class_specific_hp_effects(attacker, target, skill, actual_hp_damage)
        
        # 대상이 죽었는지 확인
        if target.current_hp <= 0:
            self.visualizer.show_death_effect(target)
            enhanced_battle_effect("death", character_name=target.name)
        
        # HP 공격 결과 확인 - 대기 시간 제거 (어차피 턴 정산에서 대기)
            
        return actual_hp_damage
        
        # 특성 트리거 효과 발동 (중복 제거된 버전)
        if hasattr(attacker, 'trigger_trait_effects'):
            if actual_hp_damage > 0:
                trait_messages = attacker.trigger_trait_effects("kill" if target.current_hp <= 0 else "attack")
                for msg in trait_messages:
                    print(f"✨ {attacker.name}: {msg}")
                
                # ⏳ 특성 효과 확인 위해 2초 대기 (엔터로 스킵 가능)
                if trait_messages and hasattr(self, 'gauge_animator'):
                    self.gauge_animator._wait_with_skip_option(2.0, "마지막 특성 효과 확인")
        
        # 공격자 Brave 소모 (HP 공격 후)
        old_brave = attacker.brave_points
        consumed_brave = attacker.consume_brave_points()
        
        print(f"💫 {attacker.name}의 Brave 포인트: {old_brave} → 0 (HP 공격으로 소모)")
        
        # Brave 변화 비주얼 이펙트 표시
        self.visualizer.show_brave_change(attacker, old_brave, attacker.brave_points)
        
        # 대상이 죽었는지 확인
        if target.current_hp <= 0:
            target.is_alive = False
            self.visualizer.show_status_change(target, "KO!", False)
            print(f"💀 {target.name}이(가) 쓰러졌습니다!")
            
            # 🔊 적 처치 SFX 재생
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system.play_sfx("enemy_defeat")
            elif hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.play_sfx("enemy_defeat")
            
    def enemy_turn(self, enemy: Character, party: List[Character], enemies: List[Character]):
        """적 턴 (AI)"""
        
        # 전투 종료 체크 - 턴 시작 시 다시 확인
        if self.check_battle_end(party, enemies):
            return self.determine_winner(party, enemies)
            
        # 턴 시작 시 특성 효과 적용
        self.trait_integrator.apply_turn_start_trait_effects(enemy)
            
        # 턴 시작 시 INT BRV 회복 처리
        if hasattr(enemy, 'recover_int_brv_on_turn_start'):
            old_brv = enemy.brave_points
            recovered = enemy.recover_int_brv_on_turn_start()
            if recovered > 0:
                print(f"🔄 {enemy.name}의 BRV가 INT BRV {recovered}로 회복되었습니다!")
                
                # BRV 회복 (자동 애니메이션 트리거)
                # enemy.brave_points는 이미 recover_int_brv_on_turn_start()에서 설정됨
                
                # BREAK 상태 해제 체크
                if getattr(enemy, 'is_broken', False) and enemy.brave_points > 0:
                    enemy.is_broken = False
                    print(f"✨ {enemy.name}의 BREAK 상태가 해제되었습니다!")
            
        alive_party = [p for p in party if p.is_alive]
        if not alive_party:
            return self.determine_winner(party, enemies)
            
        print(f"\n{get_color('BRIGHT_RED')}[{enemy.name} 턴]{get_color('RESET')}")
        
        # 🎯 어그로 기반 타겟 선정 (동적 AI)
        target = self._select_enemy_target(alive_party, enemy)
        
        # 매 턴마다 어그로 자연 감소 적용
        if hasattr(self, 'aggro_system'):
            enemy_name = getattr(enemy, 'name', str(enemy))
            self.aggro_system.decay_aggro(enemy_name)
        
        if enemy.brave_points >= 400 and random.random() < 0.5:  # 1000 → 400, 40% → 50%
            # HP 공격 사용
            print(f"💀 {enemy.name}이(가) {target.name}에게 HP 공격을 시도합니다!")
            self.execute_hp_attack(enemy, target)
        else:
            # Brave 공격 사용
            print(f"⚔️ {enemy.name}이(가) {target.name}에게 Brave 공격을 시도합니다!")
            self.execute_brave_attack(enemy, target)
        
        # 턴 종료 후 전투 상태 체크
        if self.check_battle_end(party, enemies):
            return self.determine_winner(party, enemies)
        
        return None  # 전투 계속
            
    def defend_action(self, character: Character):
        """방어 행동 - 비주얼 이펙트 포함"""
        # 방어 애니메이션 (매개변수 순서 수정)
        self.visualizer.show_attack_effect(character, character, 0, EffectType.DEFEND, "방어")
        
        print(f"{character.name}이(가) 방어 태세를 취합니다!")
        # 방어 효과: 다음 받는 데미지 50% 감소
        defense_effect = StatusEffect("방어_태세", StatusType.BUFF, 1, 2)
        character.status_manager.add_effect(defense_effect)
        
        # Brave 포인트 회복 - INT BRV의 85%
        old_brave = character.brave_points
        int_brave = getattr(character, 'initial_brave', 40)  # 기본값 40
        recovery_amount = int(int_brave * 0.85)  # INT BRV의 85%
        character.add_brave_points(recovery_amount)
        
        print(f"🛡️ 방어로 BRV {recovery_amount} 회복! (INT BRV의 85%)")
        
        # 방어 상태 변화 표시
        self.visualizer.show_status_change(character, "방어 태세")
        
        # BRV 회복 애니메이션
        if hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
            self.animate_value_change(character, 'BRV', old_brave, character.brave_points, self._current_party, self._current_enemies)
        else:
            self.visualizer.show_brave_change(character, old_brave, character.brave_points)
        
        # 방어 액션 후 딜레이 추가
        self.add_action_pause(f"🛡️ {character.name} 방어 완료!")
        
        # 🎯 방어 행동 완료 - ATB는 자연스럽게 유지됨 (다음 턴을 위해)
    
    def flee_action(self, character: Character, party: List[Character], enemies: List[Character]) -> bool:
        """개선된 도망 행동 - 스피드 비교 + 시도 횟수 보정"""
        import random
        
        # 도망 시도 횟수 추적 (전투당)
        if not hasattr(self, '_flee_attempts'):
            self._flee_attempts = 0
        
        self._flee_attempts += 1
        
        print(f"{character.name}이(가) 도망을 시도합니다... ({self._flee_attempts}회차)")
        
        # 아군과 적군의 평균 스피드 계산
        alive_party = [c for c in party if c.is_alive]
        alive_enemies = [e for e in enemies if e.is_alive]
        
        party_speed = sum(c.speed for c in alive_party) / len(alive_party) if alive_party else 1
        enemy_speed = sum(e.speed for e in alive_enemies) / len(alive_enemies) if alive_enemies else 1
        
        # 스피드 비율에 따른 기본 확률 계산 (5% ~ 80%)
        speed_ratio = party_speed / enemy_speed
        
        if speed_ratio >= 2.0:
            base_chance = 80  # 압도적으로 빠름
        elif speed_ratio >= 1.5:
            base_chance = 65  # 상당히 빠름
        elif speed_ratio >= 1.2:
            base_chance = 50  # 약간 빠름
        elif speed_ratio >= 0.8:
            base_chance = 35  # 비슷함
        elif speed_ratio >= 0.5:
            base_chance = 20  # 약간 느림
        else:
            base_chance = 5   # 상당히 느림
        
        # 시도 횟수에 따른 가중치 (최대 5회까지 5%씩 증가)
        attempt_bonus = min((self._flee_attempts - 1) * 5, 20)  # 최대 4회 추가시도로 20% 보너스
        
        # 개인 스피드 보정
        personal_bonus = min(character.speed // 20, 10)  # 속도 20당 1%, 최대 10%
        
        # 최종 확률 계산
        final_chance = min(base_chance + attempt_bonus + personal_bonus, 80)  # 최대 80%
        
        # 상세 정보 표시
        print(f"🏃 도망 성공률 분석:")
        print(f"  • 스피드 비교: 아군 {party_speed:.1f} vs 적군 {enemy_speed:.1f} (기본 {base_chance}%)")
        print(f"  • 시도 보정: +{attempt_bonus}% ({self._flee_attempts}회차)")
        print(f"  • 개인 보정: +{personal_bonus}% ({character.name}의 속도)")
        print(f"  • 최종 확률: {final_chance}%")
        
        # 도망 시도 애니메이션 (안전한 방식)
        try:
            self.visualizer.show_attack_effect(character, character, 0, EffectType.SPECIAL, "도망 시도")
        except (AttributeError, NameError):
            # EffectType을 사용할 수 없는 경우 문자열로 대체
            try:
                self.visualizer.show_attack_effect(character, character, 0, "special", "도망 시도")
            except:
                # 시각 효과를 사용할 수 없는 경우 무시
                pass
        
        if random.randint(1, 100) <= final_chance:
            # 도망 성공
            print(f"💨 {character.name}이(가) 성공적으로 도망쳤습니다!")
            print(f"🏃 전투에서 탈출했습니다!")
            
            # 도망 성공 SFX
            self._play_menu_sfx("escape_success")
            
            # 도망 성공 애니메이션
            self.visualizer.show_status_change(character, "도망 성공")
            
            # 잠시 대기
            self.add_action_pause("🏃💨 전투에서 탈출!", 1.5)
            
            # 도망 시도 횟수 리셋
            self._flee_attempts = 0
            
            return True
        else:
            # 도망 실패
            print(f"💔 {character.name}이(가) 도망에 실패했습니다!")
            print(f"😰 적들이 가로막았습니다...")
            
            if self._flee_attempts >= 5:
                print(f"⚠️ 너무 많이 시도했습니다! 다음 시도는 확률이 리셋됩니다.")
                self._flee_attempts = 0  # 5회 초과 시 리셋
            
            # 도망 실패 패널티: BRV 감소
            old_brave = character.brave_points
            penalty = min(character.brave_points // 4, 200)  # BRV의 1/4 또는 최대 200
            character.brave_points = max(0, character.brave_points - penalty)
            
            # 도망 실패 SFX
            self._play_menu_sfx("escape_fail")
            
            # 도망 실패 애니메이션
            self.visualizer.show_status_change(character, "도망 실패")
            
            if penalty > 0:
                print(f"😱 당황하여 BRV가 {penalty} 감소했습니다!")
                # BRV 감소 애니메이션
                if hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
                    self.animate_value_change(character, 'BRV', old_brave, character.brave_points, 
                                            self._current_party, self._current_enemies)
                else:
                    self.visualizer.show_brave_change(character, old_brave, character.brave_points)
            
            # 도망 실패 후 딜레이
            self.add_action_pause("💔 도망 실패...", 1.0)
            
            return False
    
    def show_battle_status(self, current_char: Character, party: List[Character], enemies: List[Character]):
        """전투 상황 표시 - 버퍼링 기반 깜빡임 방지 버전"""
        from .buffered_display import get_buffered_display
        from .ui_animations import get_gauge_animator
        import time as time_module

        # 🔄 간단 렌더링 모드: 전체 클리어 후 한 번에 재출력 (커서 이동 미지원 환경용)
        if getattr(self, 'simple_battle_render_mode', False):
            try:
                import os
                # 전체 화면 클리어 (쌓임 방지)
                print("\x1b[2J\x1b[H", end="")
                # 맨 위에 빈 줄 3줄 추가
                print("\n\n\n")
                print("⚔️ [전투 진행중] 단순 표시 모드")
                # 파티 상태
                try:
                    gauge_system = OptimizedGaugeSystem()
                    party_status = gauge_system.show_optimized_party_status(party, current_char)
                    enemy_status = gauge_system.show_optimized_enemy_status(enemies)
                except Exception:
                    # 실패 시 아주 단순 출력
                    party_status = "\n".join([f"👥 {getattr(c,'name','?')} HP {getattr(c,'current_hp',0)}/{getattr(c,'max_hp',0)} BRV {getattr(c,'brave_points',0)}" for c in party])
                    enemy_status = "\n".join([f"🛑 {getattr(e,'name','?')} HP {getattr(e,'current_hp',0)}/{getattr(e,'max_hp',0)} BRV {getattr(e,'brave_points',0)}" for e in enemies])
                print(party_status)
                print('-'*70)
                print(enemy_status)
                print('-'*70)
                print(f"🎯 현재 턴 캐릭터: {getattr(current_char,'name','?')}")
                return
            except Exception:
                # 단순 모드 실패 시 기존 경로로 폴백
                pass
        
        # 🎯 게이지 애니메이션이 진행 중일 때 대기
        gauge_animator = get_gauge_animator()
        if gauge_animator.is_processing:
            # 게이지 애니메이션이 끝날 때까지 최대 3초 대기
            wait_count = 0
            while gauge_animator.is_processing and wait_count < 30:
                time_module.sleep(0.1)
                wait_count += 1
        
        # 버퍼링 디스플레이 사용
        display = get_buffered_display()
        display.clear_buffer()
        
        # 맨 위에 빈 줄 3줄 추가
        display.add_line("")
        display.add_line("")
        display.add_line("")
        
        # 최적화된 게이지 시스템으로 파티와 적군 상태 표시
        gauge_system = OptimizedGaugeSystem()
        
        # 파티 상태를 버퍼에 추가
        party_status = gauge_system.show_optimized_party_status(party, current_char)
        for line in party_status.split('\n'):
            if line.strip():  # 빈 라인이 아닌 경우만 추가
                display.add_line(line)
        
        # 🌑 그림자 정보 추가 (암살자만)
        if self.shadow_system:
            for char in party:
                if getattr(char, 'character_class', '') == '암살자':
                    shadow_display = self.shadow_system.get_shadow_status_display(char)
                    if shadow_display:
                        display.add_line(f"   {char.name} {shadow_display}")
        
        # 🎯 새로운 직업 스택 시스템 표시
        self._add_job_stack_display(display, party)
        
        # 적군 상태를 버퍼에 추가
        enemy_status = gauge_system.show_optimized_enemy_status(enemies)
        for line in enemy_status.split('\n'):
            if line.strip():  # 빈 라인이 아닌 경우만 추가
                display.add_line(line)
        
        # 최적화된 렌더링으로 출력 (변경된 부분만 업데이트)
        display.render_optimized()

    def _get_party_status_string(self, current_char: Character, party: List[Character], enemies: List[Character]) -> str:
        """파티 상태를 문자열로 반환 - OptimizedGaugeSystem 사용"""
        from .optimized_gauge_system import OptimizedGaugeSystem
        
        status_lines = []
        
        # 아군 파티 상태
        status_lines.append(f"{get_color('BRIGHT_BLUE')}{'─'*70}{get_color('RESET')}")
        status_lines.append(f"{get_color('BRIGHT_WHITE')}🛡️  아군 파티 상태{get_color('RESET')}")
        status_lines.append(f"{get_color('BRIGHT_BLUE')}{'─'*70}{get_color('RESET')}")
        
        for member in party:
            if member.is_alive:
                # OptimizedGaugeSystem 사용
                status_display = OptimizedGaugeSystem.create_compact_character_status(member)
                status_lines.append(status_display)
        
        # 적 상태 (간단하게)
        if enemies:
            status_lines.append(f"\n{get_color('BRIGHT_RED')}{'─'*70}{get_color('RESET')}")
            status_lines.append(f"{get_color('BRIGHT_RED')}⚔️  적 상태{get_color('RESET')}")
            status_lines.append(f"{get_color('BRIGHT_RED')}{'─'*70}{get_color('RESET')}")
            
            for enemy in enemies:
                if enemy.is_alive:
                    enemy_status = OptimizedGaugeSystem.create_compact_character_status(enemy)
                    status_lines.append(enemy_status)
        
        return "\n".join(status_lines)
        
        for member in party:
            # 적군 필터링
            if hasattr(member, 'character_class') and member.character_class == 'Enemy':
                continue
            if member in enemies:
                continue
                
            if member.is_alive:
                # 현재 턴 캐릭터 강조
                if member == current_char:
                    name_color = get_color('BRIGHT_CYAN')
                    status_icon = "▶"
                else:
                    name_color = get_color('WHITE')
                    status_icon = " "
                
                # 클래스 아이콘
                character_class = getattr(member, 'character_class', '모험가')
                class_icons = {
                    '전사': '⚔️', '아크메이지': '🔮', '궁수': '🏹', '도적': '🗡️',
                    '성기사': '🛡️', '암흑기사': '🌑', '몽크': '👊', '바드': '🎵', 
                    '네크로맨서': '💀', '용기사': '🐉', '검성': '⚡', '정령술사': '🌟', 
                    '암살자': '🥷', '기계공학자': '🔧', '무당': '🔯', '해적': '🏴‍☠️', 
                    '사무라이': '🗾', '드루이드': '🌿', '철학자': '🧠', '시간술사': '⏰', 
                    '연금술사': '⚗️', '검투사': '🏛️', '기사': '🐎', '신관': '✨',
                    '마검사': '🗡️', '차원술사': '🌌', '광전사': '💥'
                }
                
                # 전사의 자세 아이콘 추가
                stance_icon = ""
                if character_class == '전사' and WARRIOR_SYSTEM_AVAILABLE:
                    try:
                        warrior_system = get_warrior_system()
                        current_stance = warrior_system.get_current_stance(member)
                        stance_icons = {
                            "defensive": "🛡️",
                            "aggressive": "⚔️", 
                            "balanced": "⚖️",
                            "berserker": "💀",
                            "guardian": "🛠️"
                        }
                        if hasattr(current_stance, 'value'):
                            stance_icon = stance_icons.get(current_stance.value, "⚖️")
                        else:
                            stance_icon = "⚖️"  # 기본값
                    except:
                        stance_icon = "⚖️"  # 오류 시 기본값
                class_icon = class_icons.get(character_class, '🎭')
                
                # HP 상태 색상과 아이콘
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                if hp_ratio > 0.7:
                    hp_color = get_color('BRIGHT_GREEN')
                    hp_icon = "💚"
                elif hp_ratio > 0.4:
                    hp_color = get_color('YELLOW')
                    hp_icon = "💛"
                elif hp_ratio > 0.15:
                    hp_color = get_color('BRIGHT_RED')
                    hp_icon = "🧡"
                else:
                    hp_color = get_color('RED')
                    hp_icon = "❤️"
                
                # MP 상태 색상과 아이콘
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                if mp_ratio > 0.5:
                    mp_color = get_color('BRIGHT_GREEN')
                    mp_icon = "💙"
                elif mp_ratio > 0.2:
                    mp_color = get_color('BLUE')
                    mp_icon = "💙"
                else:
                    mp_color = get_color('BRIGHT_BLACK')
                    mp_icon = "💙"
                
                # ATB 게이지 - 아름다운 게이지 사용
                atb_gauge = getattr(member, 'atb_gauge', 0)
                
                # 캐스팅 상태 체크
                if hasattr(member, 'is_casting') and member.is_casting:
                    # 캐스팅 시간 정보 가져오기 (여러 변수명 지원)
                    cast_time = getattr(member, 'casting_duration', 
                               getattr(member, 'casting_cast_time', 
                               getattr(member, 'cast_time', 250)))  # ATB 스케일 기본값
                    
                    # 캐스팅 시작 게이지 (실제 캐스팅을 시작한 ATB 값)
                    casting_start_gauge = getattr(member, 'casting_start_atb', self.ATB_READY_THRESHOLD)
                    
                    # 캐스팅 진행률 계산 - 방법 4 (ATB 리셋 대응) 사용
                    casting_progress = self.calculate_casting_progress_method4(member)
                    casting_percent = max(0, min(100, int(casting_progress * 100)))
                    
                    # 캐스팅 스킬 이름 가져오기 (더 안전하게)
                    casting_skill_name = "스킬"
                    if hasattr(member, 'casting_skill') and member.casting_skill:
                        if isinstance(member.casting_skill, dict):
                            casting_skill_name = member.casting_skill.get('name', '스킬')
                        else:
                            casting_skill_name = getattr(member.casting_skill, 'name', '스킬')
                    
                    # 캐스팅 표시 개선 (스킬명을 더 길게)
                    skill_display = casting_skill_name[:6] if len(casting_skill_name) > 6 else casting_skill_name
                    atb_display = f"{get_color('BRIGHT_MAGENTA')}🔮{skill_display} {casting_percent:2}%{get_color('RESET')}"
                    
                    # 캐스팅 게이지는 0%에서 100%까지 채워지는 진행률 표시
                    atb_bar = self.create_beautiful_atb_gauge(casting_percent, 100, 15, True)
                elif atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display = f"{get_color('BRIGHT_YELLOW')}READY{get_color('RESET')}"
                    atb_bar = self.create_beautiful_atb_gauge(100, 100, 15, False)
                else:
                    atb_percent = min(100, int(atb_gauge / self.ATB_READY_THRESHOLD * 100))
                    atb_display = f"{get_color('BRIGHT_CYAN')}{atb_percent}%{get_color('RESET')}"
                    atb_bar = self.create_beautiful_atb_gauge(atb_percent, 100, 15, False)
                
                # HP/MP 게이지 바 생성 (아름다운 게이지 사용)
                hp_bar = self.create_beautiful_hp_gauge(member.current_hp, member.max_hp, 15)
                mp_bar = self.create_beautiful_mp_gauge(member.current_mp, member.max_mp, 15)
                
                # Brave 포인트
                brave_points = getattr(member, 'brave_points', 0)
                max_brv = member.brave_manager.get_max_brave(member) if hasattr(member, 'brave_manager') else 9999
                
                # Brave 포인트 색상
                if brave_points <= 299:
                    brv_color = get_color('BRIGHT_RED')
                elif brave_points >= max_brv:
                    brv_color = get_color('BRIGHT_MAGENTA')
                else:
                    brv_color = get_color('BRIGHT_YELLOW')
                
                # SPD 색상 (평균 대비)
                member_speed = getattr(member, 'speed', 50)
                speed_ratio = (member_speed / avg_speed) if avg_speed > 0 else 1.0
                speed_percent_diff = (speed_ratio - 1.0) * 100
                
                if speed_percent_diff >= 30:
                    spd_color = get_color('BRIGHT_GREEN')
                elif speed_percent_diff >= 15:
                    spd_color = get_color('GREEN')
                elif speed_percent_diff >= -15:
                    spd_color = get_color('WHITE')
                elif speed_percent_diff >= -30:
                    spd_color = get_color('YELLOW')
                else:
                    spd_color = get_color('BRIGHT_RED')
                
                # 상태이상 아이콘들
                status_icons = ""
                if hasattr(member, 'is_casting') and member.is_casting:
                    status_icons += " 🔮"
                if hasattr(member, 'is_broken_state') and member.is_broken_state:
                    status_icons += " 💥"
                
                # 캐스팅 상태 표시
                casting_status = ""
                if hasattr(member, 'is_casting') and member.is_casting:
                    skill_name = getattr(member, 'casting_skill_name', '알 수 없는 스킬')
                    casting_status = f" {get_color('BRIGHT_MAGENTA')}[CASTING: {skill_name}]{get_color('RESET')}"
                
                # BREAK 상태 표시 추가
                break_status = ""
                if hasattr(member, 'is_broken') and member.is_broken:
                    break_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                
                # 컴팩트 1줄 형식으로 출력 (빈 줄 없음) - 전사 자세 아이콘 추가
                display_name = member.name
                if stance_icon:  # 전사인 경우 자세 아이콘 추가
                    display_name = f"{member.name} {stance_icon}"
                
                # 🛡️ 특수 상태 표시 추가 (보호막, 스택 등)
                special_status = ""
                
                # 피의 방패 (광전사)
                if hasattr(member, 'blood_shield') and member.blood_shield > 0:
                    shield_turns = getattr(member, 'blood_shield_turns', 0)
                    special_status += f" 🛡️{member.blood_shield}"
                    if shield_turns > 0:
                        special_status += f"({shield_turns}T)"
                
                # 조준 포인트 (궁수) - 영어 대문자 표시
                if hasattr(member, 'precision_points') and member.precision_points > 0:
                    special_status += f" {get_color('BRIGHT_CYAN')}🎯 AIM:{member.precision_points}{get_color('RESET')}"
                elif hasattr(member, 'aim_points') and member.aim_points > 0:
                    special_status += f" {get_color('BRIGHT_CYAN')}🎯 AIM:{member.aim_points}{get_color('RESET')}"

                # 그림자 스택 (암살자) - 숨김 처리 (사용자 요청)
                if hasattr(member, 'shadow_count') and member.shadow_count > 0:
                    special_status += f" {get_color('BRIGHT_BLUE')}👤 SHADOW:{member.shadow_count}{get_color('RESET')}"
                elif hasattr(member, 'shadows') and member.shadows > 0:
                    special_status += f" {get_color('BRIGHT_BLUE')}👤 SHADOW:{member.shadows}{get_color('RESET')}"
                
                # 독 스택 (도적) - 영어 대문자 표시
                if hasattr(member, 'poison_stacks') and member.poison_stacks > 0:
                    special_status += f" {get_color('BRIGHT_MAGENTA')}☠️ VENOM:{member.poison_stacks}{get_color('RESET')}"
                elif hasattr(member, 'venom_power') and member.venom_power > 0:
                    special_status += f" {get_color('BRIGHT_MAGENTA')}☠️ VENOM:{member.venom_power}%{get_color('RESET')}"
                
                # 원소 카운트 (아크메이지) - 화려한 색상 표시
                if hasattr(member, 'fire_count') and member.fire_count > 0:
                    special_status += f" {get_color('BRIGHT_RED')}🔥 FIRE: {get_color('BRIGHT_YELLOW')}{member.fire_count}{get_color('RESET')}"
                if hasattr(member, 'ice_count') and member.ice_count > 0:
                    special_status += f" {get_color('BRIGHT_CYAN')}❄️ ICE: {get_color('BRIGHT_WHITE')}{member.ice_count}{get_color('RESET')}"
                if hasattr(member, 'lightning_count') and member.lightning_count > 0:
                    special_status += f" {get_color('BRIGHT_YELLOW')}⚡ THUNDER: {get_color('BRIGHT_MAGENTA')}{member.lightning_count}{get_color('RESET')}"
                if hasattr(member, 'earth_count') and member.earth_count > 0:
                    special_status += f" {get_color('YELLOW')}🌍 EARTH: {get_color('BRIGHT_GREEN')}{member.earth_count}{get_color('RESET')}"
                if hasattr(member, 'wind_count') and member.wind_count > 0:
                    special_status += f" {get_color('BRIGHT_GREEN')}💨 WIND: {get_color('BRIGHT_CYAN')}{member.wind_count}{get_color('RESET')}"
                if hasattr(member, 'water_count') and member.water_count > 0:
                    special_status += f" {get_color('BLUE')}💧 WATER: {get_color('BRIGHT_BLUE')}{member.water_count}{get_color('RESET')}"
                
                # 검기 스택 (검성) - 화려한 색상 표시
                if hasattr(member, 'sword_aura') and member.sword_aura > 0:
                    special_status += f" {get_color('BRIGHT_WHITE')}⚔️ AURA: {get_color('BRIGHT_YELLOW')}{member.sword_aura}{get_color('RESET')}"
                elif hasattr(member, 'sword_aura_stacks') and member.sword_aura_stacks > 0:
                    special_status += f" {get_color('BRIGHT_WHITE')}⚔️ AURA: {get_color('BRIGHT_YELLOW')}{member.sword_aura_stacks}{get_color('RESET')}"
                
                # 투기 포인트 (검투사) - 화려한 색상 표시
                if hasattr(member, 'arena_points') and member.arena_points > 0:
                    special_status += f" {get_color('YELLOW')}🏛️ ARENA: {get_color('BRIGHT_RED')}{member.arena_points}{get_color('RESET')}"
                elif hasattr(member, 'gladiator_experience') and member.gladiator_experience > 0:
                    special_status += f" {get_color('YELLOW')}🏛️ ARENA: {get_color('BRIGHT_RED')}{member.gladiator_experience}{get_color('RESET')}"
                
                # 광폭화 스택 (광전사) - 화려한 색상 표시
                if hasattr(member, 'rage_stacks') and member.rage_stacks > 0:
                    special_status += f" {get_color('BRIGHT_RED')}💢 RAGE: {get_color('BRIGHT_MAGENTA')}{member.rage_stacks}{get_color('RESET')}"
                elif hasattr(member, 'berserk_level') and member.berserk_level > 0:
                    special_status += f" {get_color('BRIGHT_RED')}💢 RAGE: {get_color('BRIGHT_MAGENTA')}{member.berserk_level}{get_color('RESET')}"
                
                # 정령 친화도 (정령술사) - 화려한 색상 표시
                if hasattr(member, 'spirit_bond') and member.spirit_bond > 0:
                    special_status += f" {get_color('BRIGHT_CYAN')}🌟 SPIRIT: {get_color('BRIGHT_WHITE')}{member.spirit_bond}{get_color('RESET')}"
                elif hasattr(member, 'elemental_affinity') and member.elemental_affinity > 0:
                    special_status += f" {get_color('BRIGHT_CYAN')}🌟 SPIRIT: {get_color('BRIGHT_WHITE')}{member.elemental_affinity}{get_color('RESET')}"
                
                # 시간 기록점 (시간술사) - 화려한 색상 표시
                if hasattr(member, 'time_marks') and member.time_marks > 0:
                    special_status += f" {get_color('BRIGHT_BLUE')}⏰ TIME: {get_color('BRIGHT_YELLOW')}{member.time_marks}{get_color('RESET')}"
                elif hasattr(member, 'time_manipulation_stacks') and member.time_manipulation_stacks > 0:
                    special_status += f" {get_color('BRIGHT_BLUE')}⏰ TIME: {get_color('BRIGHT_YELLOW')}{member.time_manipulation_stacks}{get_color('RESET')}"
                elif hasattr(member, 'temporal_energy') and member.temporal_energy > 0:
                    special_status += f" {get_color('BRIGHT_BLUE')}⏰ TIME: {get_color('BRIGHT_YELLOW')}{member.temporal_energy}{get_color('RESET')}"
                
                # 용의 표식 (용기사) - 화려한 색상 표시
                if hasattr(member, 'dragon_marks') and member.dragon_marks > 0:
                    special_status += f" {get_color('BRIGHT_RED')}🐉 DRAGON: {get_color('BRIGHT_YELLOW')}{member.dragon_marks}{get_color('RESET')}"
                elif hasattr(member, 'dragon_power') and member.dragon_power > 0:
                    special_status += f" {get_color('BRIGHT_RED')}🐉 DRAGON: {get_color('BRIGHT_YELLOW')}{member.dragon_power}{get_color('RESET')}"
                
                # 타격 표식 (몽크) - 화려한 색상 표시
                if hasattr(member, 'strike_marks') and member.strike_marks > 0:
                    special_status += f" {get_color('YELLOW')}👊 COMBO: {get_color('BRIGHT_WHITE')}{member.strike_marks}{get_color('RESET')}"
                elif hasattr(member, 'ki_energy') and member.ki_energy > 0:
                    special_status += f" {get_color('YELLOW')}👊 KI: {get_color('BRIGHT_WHITE')}{member.ki_energy}{get_color('RESET')}"
                elif hasattr(member, 'combo_count') and member.combo_count > 0:
                    special_status += f" {get_color('YELLOW')}👊 COMBO: {get_color('BRIGHT_WHITE')}{member.combo_count}{get_color('RESET')}"
                
                # 음표 스택 (바드) - 화려한 색상 표시
                if hasattr(member, 'melody_stacks') and member.melody_stacks > 0:
                    special_status += f" {get_color('BRIGHT_MAGENTA')}🎵 MELODY: {get_color('BRIGHT_CYAN')}{member.melody_stacks}{get_color('RESET')}"
                elif hasattr(member, 'song_power') and member.song_power > 0:
                    special_status += f" {get_color('BRIGHT_MAGENTA')}🎵 SONG: {get_color('BRIGHT_CYAN')}{member.song_power}{get_color('RESET')}"
                
                # 네크로 에너지 (네크로맨서) - 화려한 색상 표시
                if hasattr(member, 'necro_energy') and member.necro_energy > 0:
                    special_status += f" {get_color('BRIGHT_BLACK')}💀 NECRO: {get_color('BRIGHT_RED')}{member.necro_energy}{get_color('RESET')}"
                elif hasattr(member, 'soul_power') and member.soul_power > 0:
                    special_status += f" {get_color('BRIGHT_BLACK')}💀 SOUL: {get_color('BRIGHT_RED')}{member.soul_power}{get_color('RESET')}"
                elif hasattr(member, 'undead_count') and member.undead_count > 0:
                    special_status += f" 💀 {member.undead_count}"
                
                # 기계 오버드라이브 (기계공학자)
                if hasattr(member, 'overdrive_stacks') and member.overdrive_stacks > 0:
                    special_status += f" 🔧 {member.overdrive_stacks}"
                elif hasattr(member, 'machine_energy') and member.machine_energy > 0:
                    special_status += f" 🔧 {member.machine_energy}"
                elif hasattr(member, 'turret_count') and member.turret_count > 0:
                    special_status += f" 🔧 {member.turret_count}"
                
                # 영혼 에너지 (무당)
                if hasattr(member, 'soul_energy') and member.soul_energy > 0:
                    special_status += f" 🔯 {member.soul_energy}"
                elif hasattr(member, 'spirit_power') and member.spirit_power > 0:
                    special_status += f" 🔯 {member.spirit_power}"
                
                # 해적 보물 (해적)
                if hasattr(member, 'treasure_count') and member.treasure_count > 0:
                    special_status += f" 🏴‍☠️ {member.treasure_count}"
                elif hasattr(member, 'plunder_stacks') and member.plunder_stacks > 0:
                    special_status += f" 🏴‍☠️ {member.plunder_stacks}"
                
                # 무사도 정신 (사무라이)
                if hasattr(member, 'bushido_spirit') and member.bushido_spirit > 0:
                    special_status += f" 🗾 {member.bushido_spirit}"
                elif hasattr(member, 'honor_points') and member.honor_points > 0:
                    special_status += f" 🗾 {member.honor_points}"
                
                # 자연의 힘 (드루이드)
                if hasattr(member, 'nature_power') and member.nature_power > 0:
                    special_status += f" 🌿 {member.nature_power}"
                elif hasattr(member, 'transformation_stacks') and member.transformation_stacks > 0:
                    special_status += f" 🌿 {member.transformation_stacks}"
                
                # 지혜 스택 (철학자)
                if hasattr(member, 'wisdom_stacks') and member.wisdom_stacks > 0:
                    special_status += f" 📘 {member.wisdom_stacks}"
                elif hasattr(member, 'insight_points') and member.insight_points > 0:
                    special_status += f" 📘 {member.insight_points}"
                
                # 연금술 재료 (연금술사)
                if hasattr(member, 'alchemy_materials') and member.alchemy_materials > 0:
                    special_status += f" ⚗️ {member.alchemy_materials}"
                elif hasattr(member, 'transmutation_points') and member.transmutation_points > 0:
                    special_status += f" ⚗️ {member.transmutation_points}"
                
                # 성스러운 힘 (성기사, 신관)
                if hasattr(member, 'holy_power') and member.holy_power > 0:
                    special_status += f" ✨ {member.holy_power}"
                elif hasattr(member, 'divine_energy') and member.divine_energy > 0:
                    special_status += f" ✨ {member.divine_energy}"
                elif hasattr(member, 'blessing_stacks') and member.blessing_stacks > 0:
                    special_status += f" ✨ {member.blessing_stacks}"
                
                # 어둠의 힘 (암흑기사)
                if hasattr(member, 'dark_power') and member.dark_power > 0:
                    special_status += f" 🌑 {member.dark_power}"
                elif hasattr(member, 'shadow_energy') and member.shadow_energy > 0:
                    special_status += f" 🌑 {member.shadow_energy}"
                
                # 기사도 정신 (기사)
                if hasattr(member, 'chivalry_points') and member.chivalry_points > 0:
                    special_status += f" 🐎 {member.chivalry_points}"
                elif hasattr(member, 'nobility_stacks') and member.nobility_stacks > 0:
                    special_status += f" 🐎 {member.nobility_stacks}"
                
                # 마검 융합 (마검사)
                if hasattr(member, 'magic_sword_fusion') and member.magic_sword_fusion > 0:
                    special_status += f" ⚡ {member.magic_sword_fusion}"
                elif hasattr(member, 'spellblade_energy') and member.spellblade_energy > 0:
                    special_status += f" ⚡ {member.spellblade_energy}"
                
                # 차원 에너지 (차원술사)
                if hasattr(member, 'dimension_energy') and member.dimension_energy > 0:
                    special_status += f" 🌌 {member.dimension_energy}"
                elif hasattr(member, 'dimensional_stacks') and member.dimensional_stacks > 0:
                    special_status += f" 🌌 {member.dimensional_stacks}"
                
                # 🆕 추가 특수 상태들
                
                # 전사 스탠스 표시
                if hasattr(member, 'current_stance'):
                    stance_icons = {
                        'defensive': '🛡️',
                        'aggressive': '⚔️', 
                        'balanced': '⚖️',
                        'berserker': '💀',
                        'guardian': '🛠️'
                    }
                    if member.current_stance in stance_icons:
                        special_status += f" {stance_icons[member.current_stance]}"
                
                # 보호막 효과들
                if hasattr(member, 'shield_hp') and member.shield_hp > 0:
                    special_status += f" 🛡️ {member.shield_hp}"
                if hasattr(member, 'barrier_points') and member.barrier_points > 0:
                    special_status += f" 🛡️ {member.barrier_points}"
                
                # 특수 버프/디버프 카운터
                if hasattr(member, 'buff_stacks') and member.buff_stacks > 0:
                    special_status += f" ⬆️ {member.buff_stacks}"
                if hasattr(member, 'debuff_resistance') and member.debuff_resistance > 0:
                    special_status += f" 🛡️ {member.debuff_resistance}%"
                
                # 연계 공격 카운터
                if hasattr(member, 'combo_multiplier') and member.combo_multiplier > 1.0:
                    special_status += f" 🔗 {member.combo_multiplier:.1f}x"
                
                # 치명타 확률 증가
                if hasattr(member, 'crit_bonus') and member.crit_bonus > 0:
                    special_status += f" 💥 {member.crit_bonus}%"
                
                # 회피 확률 증가
                if hasattr(member, 'dodge_bonus') and member.dodge_bonus > 0:
                    special_status += f" 💨 {member.dodge_bonus}%"
                
                # 회복 증폭
                if hasattr(member, 'heal_amplify') and member.heal_amplify > 1.0:
                    special_status += f" 💚 {member.heal_amplify:.1f}x"
                
                # 🆕 추가 직업별 특수 상태들
                
                # 용의 표식 (용기사)
                if hasattr(member, 'dragon_marks') and member.dragon_marks > 0:
                    special_status += f" 🐉 {member.dragon_marks}"
                
                # 타격 표식 (몽크)
                if hasattr(member, 'strike_marks') and member.strike_marks > 0:
                    special_status += f" 👊 {member.strike_marks}"
                
                # 음표 스택 (바드)
                if hasattr(member, 'melody_stacks') and member.melody_stacks > 0:
                    special_status += f" 🎵 {member.melody_stacks}"
                
                # 네크로 에너지 (네크로맨서)
                if hasattr(member, 'necro_energy') and member.necro_energy > 0:
                    special_status += f" 💀 {member.necro_energy}"
                
                # 기계 오버드라이브 (기계공학자)
                if hasattr(member, 'overdrive_stacks') and member.overdrive_stacks > 0:
                    special_status += f" 🔧 {member.overdrive_stacks}"
                
                # 영혼 에너지 (무당)
                if hasattr(member, 'soul_energy') and member.soul_energy > 0:
                    special_status += f" 🔯 {member.soul_energy}"
                
                # 해적 보물 (해적)
                if hasattr(member, 'treasure_count') and member.treasure_count > 0:
                    special_status += f" 🏴‍☠️ {member.treasure_count}"
                
                # 무사도 정신 (사무라이)
                if hasattr(member, 'bushido_spirit') and member.bushido_spirit > 0:
                    special_status += f" 🗾 {member.bushido_spirit}"
                
                # 자연의 힘 (드루이드)
                if hasattr(member, 'nature_power') and member.nature_power > 0:
                    special_status += f" 🌿 {member.nature_power}"
                
                # 지혜 스택 (철학자)
                if hasattr(member, 'wisdom_stacks') and member.wisdom_stacks > 0:
                    special_status += f" 📘 {member.wisdom_stacks}"
                
                # 연금술 재료 (연금술사)
                if hasattr(member, 'alchemy_materials') and member.alchemy_materials > 0:
                    special_status += f" ⚗️ {member.alchemy_materials}"
                
                # 성스러운 힘 (성기사, 신관)
                if hasattr(member, 'holy_power') and member.holy_power > 0:
                    special_status += f" ✨ {member.holy_power}"
                
                # 어둠의 힘 (암흑기사)
                if hasattr(member, 'dark_power') and member.dark_power > 0:
                    special_status += f" 🌑 {member.dark_power}"
                
                # 기사도 정신 (기사)
                if hasattr(member, 'chivalry_points') and member.chivalry_points > 0:
                    special_status += f" 🐎 {member.chivalry_points}"
                
                # 마검 융합 (마검사)
                if hasattr(member, 'magic_sword_fusion') and member.magic_sword_fusion > 0:
                    special_status += f" ⚡ {member.magic_sword_fusion}"
                
                # 차원 에너지 (차원술사)
                if hasattr(member, 'dimension_energy') and member.dimension_energy > 0:
                    special_status += f" 🌌 {member.dimension_energy}"
                
                # 전사 스탠스 표시
                if hasattr(member, 'current_stance') and member.current_stance:
                    stance_icons = {
                        'defensive': '🛡️',
                        'aggressive': '⚔️', 
                        'balanced': '⚖️',
                        'berserker': '💀',
                        'guardian': '🛠️'
                    }
                    stance_icon = stance_icons.get(member.current_stance, '⚖️')
                    special_status += f" {stance_icon}"
                
                # 암살자 그림자 표시
                if hasattr(member, 'shadow_count') and member.shadow_count > 0:
                    special_status += f" 👤 {member.shadow_count}"
                
                # 철학자 지혜 스택
                if hasattr(member, 'wisdom_stacks') and member.wisdom_stacks > 0:
                    special_status += f" 📘 {member.wisdom_stacks}"
                
                # 무사도 정신 (사무라이) - 이미 구현됨
                if hasattr(member, 'bushido_spirit') and member.bushido_spirit > 0:
                    special_status += f" 🗾{member.bushido_spirit}"
                
                # 자연의 힘 (드루이드) - 이미 구현됨
                if hasattr(member, 'nature_power') and member.nature_power > 0:
                    special_status += f" 🌿{member.nature_power}"
                
                # 연금술 재료 (연금술사) - 이미 구현됨
                if hasattr(member, 'alchemy_materials') and member.alchemy_materials > 0:
                    special_status += f" ⚗️{member.alchemy_materials}"
                
                # 성스러운 힘 (성기사, 신관) - 이미 구현됨
                if hasattr(member, 'holy_power') and member.holy_power > 0:
                    special_status += f" ✨{member.holy_power}"
                
                # 어둠의 힘 (암흑기사) - 이미 구현됨
                if hasattr(member, 'dark_power') and member.dark_power > 0:
                    special_status += f" 🌑{member.dark_power}"
                
                # 기사도 정신 (기사) - 이미 구현됨
                if hasattr(member, 'chivalry_points') and member.chivalry_points > 0:
                    special_status += f" 🐎{member.chivalry_points}"
                
                # 마검 융합 (마검사) - 이미 구현됨
                if hasattr(member, 'magic_sword_fusion') and member.magic_sword_fusion > 0:
                    special_status += f" ⚡{member.magic_sword_fusion}"
                
                # 차원 에너지 (차원술사) - 이미 구현됨
                if hasattr(member, 'dimension_energy') and member.dimension_energy > 0:
                    special_status += f" 🌌{member.dimension_energy}"
                
                # 🌟 캐릭터별 특수 기믹 표시 (이름과 같은 줄에!)
                special_mechanics = ""
                
                # 궁수 조준 포인트
                if hasattr(member, 'aim_points') and member.aim_points > 0:
                    special_mechanics += f" 🎯 {member.aim_points}"
                
                # 도적 독 스택
                if hasattr(member, 'poison_stacks') and member.poison_stacks > 0:
                    special_mechanics += f" ☠️ {member.poison_stacks}"
                
                # 암살자 그림자 수
                if hasattr(member, 'shadow_count') and member.shadow_count > 0:
                    special_mechanics += f" 👤 {member.shadow_count}"
                
                # 철학자 지혜 스택
                if hasattr(member, 'wisdom_stacks') and member.wisdom_stacks > 0:
                    special_mechanics += f" 🧠 {member.wisdom_stacks}"
                
                # 전사 스탠스 표시
                if hasattr(member, 'current_stance') and member.current_stance:
                    stance_icons = {
                        'defensive': '🛡️',
                        'aggressive': '⚔️', 
                        'balanced': '⚖️',
                        'berserker': '💀',
                        'guardian': '🛠️'
                    }
                    stance_icon = stance_icons.get(member.current_stance, '⚖️')
                    special_mechanics += f" {stance_icon}"
                
                # 바드 멜로디 스택
                if hasattr(member, 'melody_stacks') and member.melody_stacks > 0:
                    special_mechanics += f" 🎵 {member.melody_stacks}"
                
                # 몽크 기 포인트
                if hasattr(member, 'chi_points') and member.chi_points > 0:
                    special_mechanics += f" 🙏 {member.chi_points}"
                
                # 아크메이지 마력 축적
                if hasattr(member, 'mana_stacks') and member.mana_stacks > 0:
                    special_mechanics += f" 🔮 {member.mana_stacks}"
                
                # 성기사 성스러운 힘
                if hasattr(member, 'character_class') and member.character_class == "성기사":
                    holy_power = getattr(member, 'holy_power', 0)
                    divine_energy = getattr(member, 'divine_energy', 0)
                    blessing_stacks = getattr(member, 'blessing_stacks', 0)
                    protection_stacks = getattr(member, 'protection_stacks', 0)
                    
                    if holy_power > 0:
                        special_mechanics += f" ✨ {holy_power}"
                    elif divine_energy > 0:
                        special_mechanics += f" ✨ {divine_energy}"
                    elif blessing_stacks > 0:
                        special_mechanics += f" ✨ {blessing_stacks}"
                    elif protection_stacks > 0:
                        special_mechanics += f" ✨ {protection_stacks}"
                    else:
                        # 성기사인데 성스러운 힘이 없으면 기본값 설정
                        member.holy_power = 1
                        special_mechanics += f" ✨ 1"
                elif hasattr(member, 'holy_power') and member.holy_power > 0:
                    special_mechanics += f" ✨ {member.holy_power}"
                
                # 암흑기사 어둠의 힘
                if hasattr(member, 'dark_power') and member.dark_power > 0:
                    special_mechanics += f" 🌑 {member.dark_power}"
                
                # 네크로맨서 영혼 수집
                if hasattr(member, 'soul_count') and member.soul_count > 0:
                    special_mechanics += f" 👻 {member.soul_count}"
                
                # 용기사 드래곤 파워
                if hasattr(member, 'dragon_power') and member.dragon_power > 0:
                    special_mechanics += f" 🐉 {member.dragon_power}"
                
                # 검성 검기 충전
                if hasattr(member, 'sword_energy') and member.sword_energy > 0:
                    special_mechanics += f" ⚡ {member.sword_energy}"
                
                # 정령술사 원소 친화
                if hasattr(member, 'character_class') and member.character_class == "정령술사":
                    elemental_affinity = getattr(member, 'elemental_affinity', 0)
                    spirit_bond = getattr(member, 'spirit_bond', 0)
                    spirit_power = getattr(member, 'spirit_power', 0)
                    spirit_energy = getattr(member, 'spirit_energy', 0)
                    elemental_power = getattr(member, 'elemental_power', 0)
                    
                    print(f"🌟 [SPIRIT DEBUG] {member.name} - ALL ATTRS:")
                    print(f"   elemental_affinity: {elemental_affinity}")
                    print(f"   spirit_bond: {spirit_bond}")
                    print(f"   spirit_power: {spirit_power}")
                    print(f"   spirit_energy: {spirit_energy}")
                    print(f"   elemental_power: {elemental_power}")
                    
                    print(f"🌟 [SPIRIT DEBUG] {member.name} - ALL ATTRS:")
                    print(f"   elemental_affinity: {elemental_affinity}")
                    print(f"   spirit_bond: {spirit_bond}")
                    print(f"   spirit_power: {spirit_power}")
                    print(f"   spirit_energy: {spirit_energy}")
                    print(f"   elemental_power: {elemental_power}")
                    
                    # 우선순위에 따라 표시 (있는 것 중 가장 높은 값)
                    spirit_value = max(elemental_affinity, spirit_bond, spirit_power, spirit_energy, elemental_power)
                    
                    if spirit_value > 0:
                        special_mechanics += f" 🌟 {spirit_value}"
                        print(f"🌟 [SPIRIT] {member.name} - Using value: {spirit_value}")
                        print(f"🌟 [SPIRIT] {member.name} - Using value: {spirit_value}")
                    else:
                        # 정령술사인데 아무 수치도 없으면 기본값 설정
                        print(f"🌟 [SPIRIT] {member.name} - No spirit values found, setting default")
                        print(f"🌟 [SPIRIT] {member.name} - No spirit values found, setting default")
                        member.elemental_affinity = 1  # 기본 정령 친화도
                        special_mechanics += f" 🌟 1"
                elif hasattr(member, 'elemental_affinity') and member.elemental_affinity > 0:
                    special_mechanics += f" 🌟 {member.elemental_affinity}"
                
                # 기계공학자 로봇 수
                if hasattr(member, 'robot_count') and member.robot_count > 0:
                    special_mechanics += f" 🤖 {member.robot_count}"
                
                # 무당 영력
                if hasattr(member, 'spirit_power') and member.spirit_power > 0:
                    special_mechanics += f" 🔯 {member.spirit_power}"
                
                # 해적 보물
                if hasattr(member, 'character_class') and member.character_class == "해적":
                    treasure_count = getattr(member, 'treasure_count', 0)
                    plunder_stacks = getattr(member, 'plunder_stacks', 0)
                    
                    if treasure_count > 0:
                        special_mechanics += f" 💰 {treasure_count}"
                    elif plunder_stacks > 0:
                        special_mechanics += f" 💰 {plunder_stacks}"
                    else:
                        # 해적인데 보물이 없으면 기본값 설정
                        print(f"💰 [TREASURE] {member.name} - No treasure found, setting default")
                        member.treasure_count = 1
                        special_mechanics += f" 💰 1"
                elif hasattr(member, 'treasure_count') and member.treasure_count > 0:
                    special_mechanics += f" 💰 {member.treasure_count}"
                
                # 사무라이 무사도 정신
                if hasattr(member, 'bushido_spirit') and member.bushido_spirit > 0:
                    special_mechanics += f" 🗾 {member.bushido_spirit}"
                
                # 드루이드 자연의 힘
                if hasattr(member, 'nature_power') and member.nature_power > 0:
                    special_mechanics += f" 🌿 {member.nature_power}"
                
                # 시간술사 시간 에너지
                if hasattr(member, 'time_energy') and member.time_energy > 0:
                    special_mechanics += f" ⏰ {member.time_energy}"
                
                # 연금술사 연금술 재료
                if hasattr(member, 'alchemy_materials') and member.alchemy_materials > 0:
                    special_mechanics += f" ⚗️ {member.alchemy_materials}"
                
                # 검투사 투기장 포인트
                if hasattr(member, 'arena_points') and member.arena_points > 0:
                    special_mechanics += f" 🏛️ {member.arena_points}"
                
                # 기사 기사도 정신
                if hasattr(member, 'chivalry_points') and member.chivalry_points > 0:
                    special_mechanics += f" 🐎 {member.chivalry_points}"
                
                # 신관 신앙 포인트
                if hasattr(member, 'character_class') and member.character_class == "신관":
                    faith_points = getattr(member, 'faith_points', 0)
                    divine_energy = getattr(member, 'divine_energy', 0)
                    blessing_stacks = getattr(member, 'blessing_stacks', 0)
                    
                    if faith_points > 0:
                        special_mechanics += f" ⛪ {faith_points}"
                    elif divine_energy > 0:
                        special_mechanics += f" ⛪ {divine_energy}"
                    elif blessing_stacks > 0:
                        special_mechanics += f" ⛪ {blessing_stacks}"
                    else:
                        # 신관인데 신앙이 없으면 기본값 설정
                        print(f"⛪ [FAITH] {member.name} - No faith found, setting default")
                        member.faith_points = 1
                        special_mechanics += f" ⛪ 1"
                elif hasattr(member, 'faith_points') and member.faith_points > 0:
                    special_mechanics += f" ⛪ {member.faith_points}"
                
                # 마검사 마검 융합
                if hasattr(member, 'magic_sword_fusion') and member.magic_sword_fusion > 0:
                    special_mechanics += f" ⚡ {member.magic_sword_fusion}"
                
                # 차원술사 차원 에너지
                if hasattr(member, 'dimension_energy') and member.dimension_energy > 0:
                    special_mechanics += f" 🌌 {member.dimension_energy}"
                
                # 광전사 분노 포인트
                if hasattr(member, 'rage_points') and member.rage_points > 0:
                    special_mechanics += f" 💥 {member.rage_points}"
                
                # 🌟 기존 특수 상태들도 유지
                special_status = ""
                
                # 독액 흡수력 (도적)
                if hasattr(member, 'venom_power') and member.venom_power > 0:
                    special_status += f" ☠️ {member.venom_power}%"
                
                # 🌟 상태 효과 표시 (직접 속성 체크 및 status_manager 모두 지원)
                # 독 상태 표시 (우선순위: 직접 속성 → status_manager)
                if hasattr(member, 'is_poisoned') and member.is_poisoned:
                    poison_turns = getattr(member, 'poison_turns', 0)
                    poison_damage = getattr(member, 'poison_damage', 0)
                    if poison_turns > 0:
                        special_status += f" {get_color('BRIGHT_GREEN')}POISON:{poison_turns}{get_color('RESET')}"
                        print(f"🗡️ [DISPLAY LOG] {member.name} 독 표시: {poison_turns}턴 남음, {poison_damage} 피해")
                elif hasattr(member, 'status_manager') and member.status_manager and member.status_manager.has_status("poison"):
                    poison_stacks = member.status_manager.get_status_value("poison")
                    if poison_stacks > 0:
                        special_status += f" {get_color('BRIGHT_GREEN')}POISON:{poison_stacks}{get_color('RESET')}"
                
                # 화상 상태 표시
                if hasattr(member, 'is_burning') and member.is_burning:
                    burn_turns = getattr(member, 'burn_turns', 0)
                    if burn_turns > 0:
                        special_status += f" {get_color('BRIGHT_RED')}BURN:{burn_turns}{get_color('RESET')}"
                elif hasattr(member, 'status_manager') and member.status_manager and member.status_manager.has_status("burn"):
                    burn_stacks = member.status_manager.get_status_value("burn")
                    if burn_stacks > 0:
                        special_status += f" {get_color('BRIGHT_RED')}BURN:{burn_stacks}{get_color('RESET')}"
                
                # 빙결 상태 표시
                if hasattr(member, 'is_frozen') and member.is_frozen:
                    freeze_turns = getattr(member, 'freeze_turns', 0)
                    if freeze_turns > 0:
                        special_status += f" {get_color('BRIGHT_CYAN')}FREEZE:{freeze_turns}{get_color('RESET')}"
                elif hasattr(member, 'status_manager') and member.status_manager and member.status_manager.has_status("freeze"):
                    freeze_turns = member.status_manager.get_status_turns("freeze")
                    if freeze_turns > 0:
                        special_status += f" {get_color('BRIGHT_CYAN')}FREEZE:{freeze_turns}{get_color('RESET')}"
                
                # 마비 상태 표시
                if hasattr(member, 'is_paralyzed') and member.is_paralyzed:
                    paralysis_turns = getattr(member, 'paralysis_turns', 0)
                    if paralysis_turns > 0:
                        special_status += f" {get_color('BRIGHT_YELLOW')}PARALYSIS:{paralysis_turns}{get_color('RESET')}"
                elif hasattr(member, 'status_manager') and member.status_manager and member.status_manager.has_status("paralysis"):
                    paralysis_turns = member.status_manager.get_status_turns("paralysis")
                    if paralysis_turns > 0:
                        special_status += f" {get_color('BRIGHT_YELLOW')}PARALYSIS:{paralysis_turns}{get_color('RESET')}"
                    
                    # 공격력 버프
                    if member.status_manager.has_status("attack_boost"):
                        attack_boost = member.status_manager.get_status_value("attack_boost")
                        attack_turns = member.status_manager.get_status_turns("attack_boost")
                        if attack_boost > 0:
                            special_status += f" ⚔️+{attack_boost}({attack_turns}T)"
                    
                    # 방어력 버프
                    if member.status_manager.has_status("defense_boost"):
                        defense_boost = member.status_manager.get_status_value("defense_boost")
                        defense_turns = member.status_manager.get_status_turns("defense_boost")
                        if defense_boost > 0:
                            special_status += f" 🛡️+{defense_boost}({defense_turns}T)"
                    
                    # 속도 버프
                    if member.status_manager.has_status("speed_boost"):
                        speed_boost = member.status_manager.get_status_value("speed_boost")
                        speed_turns = member.status_manager.get_status_turns("speed_boost")
                        if speed_boost > 0:
                            special_status += f" 💨+{speed_boost}({speed_turns}T)"
                    
                    # 마법 공격력 버프
                    if member.status_manager.has_status("magic_boost"):
                        magic_boost = member.status_manager.get_status_value("magic_boost")
                        magic_turns = member.status_manager.get_status_turns("magic_boost")
                        if magic_boost > 0:
                            special_status += f" 🔮+{magic_boost}({magic_turns}T)"
                    
                    # 회복력 증가
                    if member.status_manager.has_status("heal_boost"):
                        heal_boost = member.status_manager.get_status_value("heal_boost")
                        heal_turns = member.status_manager.get_status_turns("heal_boost")
                        if heal_boost > 0:
                            special_status += f" 💚+{heal_boost}({heal_turns}T)"
                    
                    # 공격력 디버프
                    if member.status_manager.has_status("attack_debuff"):
                        attack_debuff = member.status_manager.get_status_value("attack_debuff")
                        debuff_turns = member.status_manager.get_status_turns("attack_debuff")
                        if attack_debuff > 0:
                            special_status += f" ⚔️-{attack_debuff}({debuff_turns}T)"
                    
                    # 방어력 디버프
                    if member.status_manager.has_status("defense_debuff"):
                        defense_debuff = member.status_manager.get_status_value("defense_debuff")
                        debuff_turns = member.status_manager.get_status_turns("defense_debuff")
                        if defense_debuff > 0:
                            special_status += f" 🛡️-{defense_debuff}({debuff_turns}T)"
                    
                    # 속도 디버프
                    if member.status_manager.has_status("speed_debuff"):
                        speed_debuff = member.status_manager.get_status_value("speed_debuff")
                        debuff_turns = member.status_manager.get_status_turns("speed_debuff")
                        if speed_debuff > 0:
                            special_status += f" 💨-{speed_debuff}({debuff_turns}T)"
                    
                    # 보호막
                    if member.status_manager.has_status("shield"):
                        shield_value = member.status_manager.get_status_value("shield")
                        shield_turns = member.status_manager.get_status_turns("shield")
                        if shield_value > 0:
                            special_status += f" 🛡️{shield_value}({shield_turns}T)"
                    
                    # 재생
                    if member.status_manager.has_status("regeneration"):
                        regen_value = member.status_manager.get_status_value("regeneration")
                        regen_turns = member.status_manager.get_status_turns("regeneration")
                        if regen_value > 0:
                            special_status += f" 💚+{regen_value}/T({regen_turns}T)"
                    
                    # 출혈
                    if member.status_manager.has_status("bleeding"):
                        bleed_value = member.status_manager.get_status_value("bleeding")
                        bleed_turns = member.status_manager.get_status_turns("bleeding")
                        if bleed_value > 0:
                            special_status += f" 🩸{bleed_value}({bleed_turns}T)"
                    
                    # 축복
                    if member.status_manager.has_status("blessing"):
                        blessing_turns = member.status_manager.get_status_turns("blessing")
                        if blessing_turns > 0:
                            special_status += f" ✨({blessing_turns}T)"
                    
                    # 저주
                    if member.status_manager.has_status("curse"):
                        curse_turns = member.status_manager.get_status_turns("curse")
                        if curse_turns > 0:
                            special_status += f" 🌑({curse_turns}T)"
                    
                    # 침묵 (마법 사용 불가)
                    if member.status_manager.has_status("silence"):
                        silence_turns = member.status_manager.get_status_turns("silence")
                        if silence_turns > 0:
                            special_status += f" 🤐({silence_turns}T)"
                    
                    # 기절
                    if member.status_manager.has_status("stun"):
                        stun_turns = member.status_manager.get_status_turns("stun")
                        if stun_turns > 0:
                            special_status += f" 😵({stun_turns}T)"
                
                # 안전한 이름 표시 처리 (Unicode 문제 방지)
                try:
                    safe_name = display_name.encode('utf-8').decode('utf-8')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    safe_name = '알 수 없는 캐릭터'
                
                # 이름과 특수 상태를 함께 표시 (레벨과 기믹 포함!)
                compact_line = f"   {status_icon} {class_icon} Lv.{getattr(member, 'level', 1)} {name_color}{safe_name}{special_mechanics}{special_status}{get_color('RESET')}"
                compact_line += f" | 💚 HP: {member.current_hp}/{member.max_hp} {get_color('WHITE')}{{{hp_bar}}}{get_color('RESET')}"
                compact_line += f" | 💙 MP: {member.current_mp}/{member.max_mp} {get_color('WHITE')}{{{mp_bar}}}{get_color('RESET')}"
                compact_line += f" | {brv_color}⚡ BRV: {brave_points}{get_color('RESET')}"
                compact_line += f" | ⏳ TIME: {get_color('WHITE')}{{{atb_bar}}}{get_color('RESET')} {atb_display} | SPD: {spd_color}{member_speed}{get_color('RESET')}{casting_status}{break_status}"
                status_lines.append(compact_line)
            else:
                # 전투불능 상태 표시
                status_lines.append(f"   💀 {get_color('RED')}{member.name} - 전투불능{get_color('RESET')}")
                
                # ATB 게이지 표시
                atb_gauge = getattr(member, 'atb_gauge', 0)
                if hasattr(member, 'is_casting') and member.is_casting:
                    cast_time = getattr(member, 'casting_duration', 250)  # ATB 스케일 기본값
                    # 캐스팅 시작 게이지 (실제 캐스팅을 시작한 ATB 값)
                    casting_start_gauge = getattr(member, 'casting_start_atb', self.ATB_READY_THRESHOLD)
                    
                    # 캐스팅 진행률 계산 - 시작 게이지부터 현재까지의 진행률
                    if cast_time > 0:
                        casting_progress_atb = member.atb_gauge - casting_start_gauge
                        casting_progress = min(1.0, max(0.0, casting_progress_atb / cast_time))
                    else:
                        casting_progress = 0.0
                    
                    casting_percent = int(casting_progress * 100)
                    atb_display = f"{get_color('BRIGHT_MAGENTA')}🔮{casting_percent:3}%{get_color('RESET')}"
                    atb_icon = "🔮"
                elif atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display = f"{get_color('BRIGHT_YELLOW')}READY{get_color('RESET')}"  # 색상 적용
                    atb_icon = "⏳"
                else:
                    atb_percent = min(100, int(atb_gauge / self.ATB_READY_THRESHOLD * 100))
                    # 진행도에 따른 그라데이션 색상 (푸른색 → 하늘색)
                    if atb_percent >= 80:
                        atb_color = get_color('BRIGHT_CYAN')  # 80% 이상: 밝은 하늘색
                    elif atb_percent >= 60:
                        atb_color = get_color('CYAN')  # 60-80%: 하늘색
                    elif atb_percent >= 40:
                        atb_color = get_color('BLUE')  # 40-60%: 푸른색
                    else:
                        atb_color = get_color('BRIGHT_BLUE')  # 40% 미만: 어두운 파랑
                    
                    atb_display = f"{atb_color}{atb_percent:3}%{get_color('RESET')}"
                    atb_icon = "⏳"
                
                # ATB 바 생성
                atb_bar = self._create_atb_bar(atb_gauge, True, True, member)
                
                # Brave 포인트와 색상
                brave_points = getattr(member, 'brave_points', 0)
                max_brv = member.brave_manager.get_max_brave(member) if hasattr(member, 'brave_manager') else 9999
                
                # BRV 색상 결정: 최대치일 때 마젠타, 낮을 때 빨강, 그 외 노랑
                if brave_points <= 299:
                    brv_color = get_color('BRIGHT_RED')
                elif brave_points >= max_brv:  # MAX BRV = 현재 BRV일 때 마젠타
                    brv_color = get_color('BRIGHT_MAGENTA')
                else:
                    brv_color = get_color('BRIGHT_YELLOW')
                
                # SPD 색상 (상대적 속도 - 실제 평균 대비 퍼센트)
                member_speed = getattr(member, 'speed', 50)
                speed_ratio = (member_speed / avg_speed) if avg_speed > 0 else 1.0
                speed_percent_diff = (speed_ratio - 1.0) * 100  # 평균 대비 퍼센트 차이
                
                if speed_percent_diff >= 30:  # +30% 이상
                    spd_color = get_color('BRIGHT_GREEN')  # 매우 빠름
                elif speed_percent_diff >= 15:  # +15% 이상
                    spd_color = get_color('GREEN')  # 빠름
                elif speed_percent_diff >= -15:  # ±15% 이내
                    spd_color = get_color('WHITE')  # 보통
                elif speed_percent_diff >= -30:  # -15% ~ -30%
                    spd_color = get_color('YELLOW')  # 느림
                else:  # -30% 미만
                    spd_color = get_color('BRIGHT_RED')  # 매우 느림
                
                # 캐스팅/브레이크 상태 확인
                casting_status = ""
                if hasattr(member, 'is_casting') and member.is_casting:
                    skill_name = getattr(member, 'casting_skill_name', '알 수 없는 스킬')
                    casting_status = f" {get_color('BRIGHT_MAGENTA')}[CASTING: {skill_name}]{get_color('RESET')}"
                
                break_status = ""
                if hasattr(member, 'is_broken_state') and member.is_broken_state:
                    break_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                elif hasattr(member, 'is_broken') and member.is_broken:
                    break_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                
                # 상태이상 아이콘들
                status_icons = ""
                if hasattr(member, 'is_casting') and member.is_casting:
                    status_icons += " 🔮"
                if hasattr(member, 'is_broken_state') and member.is_broken_state:
                    status_icons += " 💥"
                elif hasattr(member, 'is_broken') and member.is_broken:
                    status_icons += " 💥"
                if hasattr(member, 'status_effects') and member.status_effects:
                    try:
                        from .new_skill_system import get_status_icon
                        
                        status_types_found = []
                        for effect in member.status_effects:
                            if effect.status_type not in status_types_found:
                                status_types_found.append(effect.status_type)
                                icon = get_status_icon(effect.status_type)
                                status_icons += f" {icon}"
                    except ImportError:
                        pass
                if hasattr(member, 'temp_speed_penalty') and getattr(member, 'temp_speed_penalty', 0) > 0:
                    status_icons += " 🟦"
                
                # HP/MP 게이지 바 생성 (아름다운 게이지 사용)
                hp_bar = self.create_beautiful_hp_gauge(member.current_hp, member.max_hp, 12)
                mp_bar = self.create_beautiful_mp_gauge(member.current_mp, member.max_mp, 12)
                
                # ATB 바 생성 - 아름다운 ATB 게이지 사용
                atb_percent = min(100, int(atb_gauge / self.ATB_READY_THRESHOLD * 100)) if atb_gauge < self.ATB_READY_THRESHOLD else 100
                is_casting = hasattr(member, 'is_casting') and member.is_casting
                atb_bar = self.create_beautiful_atb_gauge(atb_percent, 100, 12, is_casting)
                
                # 캐릭터별 특수 기믹 표시 수집
                special_status = ""
                
                # 🏹 궁수 조준 포인트
                if hasattr(member, 'character_class') and member.character_class == "궁수":
                    aim_points = getattr(member, 'aim_points', 0)
                    if aim_points > 0:
                        special_status += f" 🎯{aim_points}"
                
                # ⚔️ 검성 검기
                if hasattr(member, 'character_class') and member.character_class == "검성":
                    sword_aura = getattr(member, 'sword_aura_stacks', 0)
                    if sword_aura > 0:
                        special_status += f" ⚔️{sword_aura}"
                
                # 🌑 암살자 그림자
                if hasattr(member, 'character_class') and member.character_class == "암살자":
                    shadows = getattr(member, 'shadow_count', 0)
                    if shadows > 0:
                        special_status += f" 🌑{shadows}"
                
                # 💥 광전사 분노
                if hasattr(member, 'character_class') and member.character_class == "광전사":
                    rage = getattr(member, 'rage_stacks', 0)
                    if rage > 0:
                        special_status += f" 💥{rage}"
                
                # 🔮 시간술사 시간 조작
                if hasattr(member, 'character_class') and member.character_class == "시간술사":
                    time_stacks = getattr(member, 'time_manipulation_stacks', 0)
                    if time_stacks > 0:
                        special_status += f" ⏰{time_stacks}"
                
                # 🗡️ 도적 독 스택
                if hasattr(member, 'character_class') and member.character_class == "도적":
                    poison = getattr(member, 'poison_stacks', 0)
                    if poison > 0:
                        special_status += f" POISON:{poison}"
                
                # 🔮 아크메이지 원소 스택
                if hasattr(member, 'character_class') and member.character_class == "아크메이지":
                    fire = getattr(member, 'fire_count', 0)
                    ice = getattr(member, 'ice_count', 0)
                    lightning = getattr(member, 'lightning_count', 0)
                    if fire > 0:
                        special_status += f" FIRE:{fire}"
                    if ice > 0:
                        special_status += f" ICE:{ice}"
                    if lightning > 0:
                        special_status += f" THUNDER:{lightning}"
                
                # 👊 몽크 기 포인트
                if hasattr(member, 'character_class') and member.character_class == "몽크":
                    ki = getattr(member, 'ki_energy', 0)
                    combo = getattr(member, 'combo_count', 0)
                    if ki > 0:
                        special_status += f" KI:{ki}"
                    if combo > 0:
                        special_status += f" COMBO:{combo}"
                
                # 🎵 바드 멜로디 스택 (특별한 음계 표시)
                if hasattr(member, 'character_class') and member.character_class == "바드":
                    melody = getattr(member, 'melody_stacks', 0)
                    if melody > 0:
                        # 음계 배열: DO RE MI FA SOL LA SI
                        notes = ["DO", "RE", "MI", "FA", "SOL", "LA", "SI"]
                        colors = [
                            get_color('RED'),      # 도 - 빨강
                            get_color('YELLOW'),   # 레 - 주황(노랑)
                            get_color('BRIGHT_YELLOW'), # 미 - 노랑
                            get_color('GREEN'),    # 파 - 초록
                            get_color('BLUE'),     # 솔 - 파랑
                            get_color('BRIGHT_BLUE'), # 라 - 남색(밝은파랑)
                            get_color('MAGENTA')   # 시 - 보라
                        ]
                        
                        melody_display = " MELODY:"
                        for i in range(7):
                            if i < melody:
                                # 활성화된 음계는 무지개색으로
                                melody_display += f"{colors[i]}{notes[i]}{get_color('RESET')}"
                            else:
                                # 비활성화된 음계는 회색으로
                                melody_display += f"{get_color('BRIGHT_BLACK')}{notes[i]}{get_color('RESET')}"
                        
                        special_status += melody_display
                
                # 💀 네크로맨서 영혼 수집
                if hasattr(member, 'character_class') and member.character_class == "네크로맨서":
                    souls = getattr(member, 'soul_count', 0)
                    necro_energy = getattr(member, 'necro_energy', 0)
                    if souls > 0:
                        special_status += f" SOULS:{souls}"
                    if necro_energy > 0:
                        special_status += f" NECRO:{necro_energy}"
                
                # 🐉 용기사 드래곤 파워
                if hasattr(member, 'character_class') and member.character_class == "용기사":
                    dragon_power = getattr(member, 'dragon_power', 0)
                    dragon_marks = getattr(member, 'dragon_marks', 0)
                    if dragon_power > 0:
                        special_status += f" DRAGON:{dragon_power}"
                    if dragon_marks > 0:
                        special_status += f" MARKS:{dragon_marks}"
                
                # 🌟 정령술사 원소 친화
                if hasattr(member, 'character_class') and member.character_class == "정령술사":
                    elemental = getattr(member, 'elemental_affinity', 0)
                    spirit_bond = getattr(member, 'spirit_bond', 0)
                    if elemental > 0:
                        special_status += f" 🌟 ELEMENTAL:{elemental}"
                    if spirit_bond > 0:
                        special_status += f" 🌟 SPIRIT:{spirit_bond}"
                
                # 🔧 기계공학자 로봇/터렛
                if hasattr(member, 'character_class') and member.character_class == "기계공학자":
                    robots = getattr(member, 'robot_count', 0)
                    turrets = getattr(member, 'turret_count', 0)
                    overdrive = getattr(member, 'overdrive_stacks', 0)
                    if robots > 0:
                        special_status += f" 🤖 ROBOTS:{robots}"
                    if turrets > 0:
                        special_status += f" 🔧 TURRETS:{turrets}"
                    if overdrive > 0:
                        special_status += f" ⚡ OVERDRIVE:{overdrive}"
                
                # 🔯 무당 영력
                if hasattr(member, 'character_class') and member.character_class == "무당":
                    spirit_power = getattr(member, 'spirit_power', 0)
                    soul_energy = getattr(member, 'soul_energy', 0)
                    if spirit_power > 0:
                        special_status += f" 🔯 SPIRIT:{spirit_power}"
                    if soul_energy > 0:
                        special_status += f" 👻 SOULS:{soul_energy}"
                
                # 🏴‍☠️ 해적 보물
                if hasattr(member, 'character_class') and member.character_class == "해적":
                    treasure = getattr(member, 'treasure_count', 0)
                    plunder = getattr(member, 'plunder_stacks', 0)
                    if treasure > 0:
                        special_status += f" 💰 TREASURE:{treasure}"
                    if plunder > 0:
                        special_status += f" 🏴‍☠️ PLUNDER:{plunder}"
                
                # 🗾 사무라이 무사도 정신
                if hasattr(member, 'character_class') and member.character_class == "사무라이":
                    bushido = getattr(member, 'bushido_spirit', 0)
                    honor = getattr(member, 'honor_points', 0)
                    if bushido > 0:
                        special_status += f" 🗾 BUSHIDO:{bushido}"
                    if honor > 0:
                        special_status += f" ⚔️ HONOR:{honor}"
                
                # 🌿 드루이드 자연의 힘
                if hasattr(member, 'character_class') and member.character_class == "드루이드":
                    nature = getattr(member, 'nature_power', 0)
                    transform = getattr(member, 'transformation_stacks', 0)
                    if nature > 0:
                        special_status += f" 🌿 NATURE:{nature}"
                    if transform > 0:
                        special_status += f" 🐺 TRANSFORM:{transform}"
                
                # 🧠 철학자 지혜 스택
                if hasattr(member, 'character_class') and member.character_class == "철학자":
                    wisdom = getattr(member, 'wisdom_stacks', 0)
                    insight = getattr(member, 'insight_points', 0)
                    if wisdom > 0:
                        special_status += f" 🧠 WISDOM:{wisdom}"
                    if insight > 0:
                        special_status += f" 💡 INSIGHT:{insight}"
                
                # ⚗️ 연금술사 연금술 재료
                if hasattr(member, 'character_class') and member.character_class == "연금술사":
                    materials = getattr(member, 'alchemy_materials', 0)
                    transmutation = getattr(member, 'transmutation_points', 0)
                    if materials > 0:
                        special_status += f" ⚗️ MATERIALS:{materials}"
                    if transmutation > 0:
                        special_status += f" 🔄 TRANSMUTE:{transmutation}"
                
                # 🏛️ 검투사 투기장 포인트
                if hasattr(member, 'character_class') and member.character_class == "검투사":
                    arena = getattr(member, 'arena_points', 0)
                    gladiator_exp = getattr(member, 'gladiator_experience', 0)
                    if arena > 0:
                        special_status += f" 🏛️ ARENA:{arena}"
                    if gladiator_exp > 0:
                        special_status += f" ⚔️ GLADIATOR:{gladiator_exp}"
                
                # 🐎 기사 기사도 정신
                if hasattr(member, 'character_class') and member.character_class == "기사":
                    chivalry = getattr(member, 'chivalry_points', 0)
                    nobility = getattr(member, 'nobility_stacks', 0)
                    if chivalry > 0:
                        special_status += f" 🐎 CHIVALRY:{chivalry}"
                    if nobility > 0:
                        special_status += f" 👑 NOBILITY:{nobility}"
                
                # ✨ 신관 신앙 포인트
                if hasattr(member, 'character_class') and member.character_class == "신관":
                    faith = getattr(member, 'faith_points', 0)
                    divine = getattr(member, 'divine_energy', 0)
                    blessing = getattr(member, 'blessing_stacks', 0)
                    if faith > 0:
                        special_status += f" ⛪ FAITH:{faith}"
                    if divine > 0:
                        special_status += f" ✨ DIVINE:{divine}"
                    if blessing > 0:
                        special_status += f" 🙏 BLESSING:{blessing}"
                
                # 🛡️ 성기사 성스러운 힘
                if hasattr(member, 'character_class') and member.character_class == "성기사":
                    holy = getattr(member, 'holy_power', 0)
                    protection = getattr(member, 'protection_stacks', 0)
                    if holy > 0:
                        special_status += f" ✨ HOLY:{holy}"
                    if protection > 0:
                        special_status += f" 🛡️ PROTECT:{protection}"
                
                # 🌑 암흑기사 어둠의 힘
                if hasattr(member, 'character_class') and member.character_class == "암흑기사":
                    dark = getattr(member, 'dark_power', 0)
                    shadow_energy = getattr(member, 'shadow_energy', 0)
                    if dark > 0:
                        special_status += f" DARK:{dark}"
                    if shadow_energy > 0:
                        special_status += f" SHADOW:{shadow_energy}"
                
                # ⚡ 마검사 마검 융합
                if hasattr(member, 'character_class') and member.character_class == "마검사":
                    fusion = getattr(member, 'magic_sword_fusion', 0)
                    spellblade = getattr(member, 'spellblade_energy', 0)
                    if fusion > 0:
                        special_status += f" FUSION:{fusion}"
                    if spellblade > 0:
                        special_status += f" SPELL:{spellblade}"
                
                # 🌌 차원술사 차원 에너지
                if hasattr(member, 'character_class') and member.character_class == "차원술사":
                    dimension = getattr(member, 'dimension_energy', 0)
                    dimensional = getattr(member, 'dimensional_stacks', 0)
                    if dimension > 0:
                        special_status += f" DIMENSION:{dimension}"
                    if dimensional > 0:
                        special_status += f" PORTAL:{dimensional}"
                
                # ⚖️ 전사 스탠스 표시
                if hasattr(member, 'character_class') and member.character_class == "전사":
                    stance = getattr(member, 'current_stance', None)
                    if stance:
                        stance_names = {
                            'defensive': 'DEFEND',
                            'aggressive': 'ATTACK', 
                            'balanced': 'BALANCE',
                            'berserker': 'BERSERK',
                            'guardian': 'GUARD',
                            'speed': 'SPEED',
                        }
                        stance_name = stance_names.get(stance, 'BALANCE')
                        special_status += f" STANCE:{stance_name}"
                
                # 2줄 형식 (로딩 중일 때) - 간격 조정
                status_lines.append(f"  {class_icon} {member.name}{special_status}{status_icons}")
                
                # HP/MP 게이지와 ATB 진행률 표시 (하얀 껍데기 추가)
                hp_bar_colored = f"{get_color('WHITE')}[{hp_bar}]{get_color('RESET')}"
                mp_bar_colored = f"{get_color('WHITE')}[{mp_bar}]{get_color('RESET')}"
                
                # BREAK 상태 확인 및 표시 (실제 BREAK 상태일 때만)
                brv_status = ""
                if hasattr(member, 'is_broken') and member.is_broken:
                    brv_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                elif brave_points <= 0 and hasattr(member, 'was_brv_attacked'):
                    # BRV 공격을 받아서 0이 된 경우만 BREAK 표시
                    if getattr(member, 'was_brv_attacked', False):
                        brv_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                
                status_lines.append(f"   {hp_icon} HP: {hp_color}{member.current_hp}{get_color('RESET')} / {get_color('WHITE')}{member.max_hp}{get_color('RESET')}  {hp_bar_colored} | {mp_icon} MP: {mp_color}{member.current_mp}{get_color('RESET')} / {get_color('WHITE')}{member.max_mp}{get_color('RESET')}  {mp_bar_colored} | {brv_color}⚡ BRV: {brave_points}{get_color('RESET')}{brv_status}  |")
                
                # ATB 진행률 표시 (대괄호는 흰색)
                atb_bar_simple = f"{get_color('WHITE')}[{atb_bar}]{get_color('RESET')}"
                if hasattr(member, 'is_casting') and member.is_casting:
                    cast_time = getattr(member, 'casting_duration', 250)  # ATB 스케일 기본값
                    # 캐스팅 시작 게이지 (실제 캐스팅을 시작한 ATB 값)
                    casting_start_gauge = getattr(member, 'casting_start_atb', self.ATB_READY_THRESHOLD)
                    
                    # 캐스팅 진행률 계산 - 시작 게이지부터 현재까지의 진행률
                    if cast_time > 0:
                        casting_progress_atb = member.atb_gauge - casting_start_gauge
                        casting_progress = min(1.0, max(0.0, casting_progress_atb / cast_time))
                    else:
                        casting_progress = 0.0
                    
                    casting_percent = int(casting_progress * 100)
                    atb_display_simple = f"{get_color('BRIGHT_MAGENTA')}{casting_percent}%{get_color('RESET')}"
                elif atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display_simple = f"{get_color('BRIGHT_YELLOW')}READY{get_color('RESET')}"
                else:
                    atb_percent = min(100, int(atb_gauge / self.ATB_READY_THRESHOLD * 100))
                    # 진행도에 따른 그라데이션 색상
                    if atb_percent >= 80:
                        atb_color = get_color('BRIGHT_CYAN')  
                    elif atb_percent >= 60:
                        atb_color = get_color('CYAN')  
                    elif atb_percent >= 40:
                        atb_color = get_color('BLUE')  
                    else:
                        atb_color = get_color('BRIGHT_BLUE') 
                    atb_display_simple = f"{atb_color}{atb_percent}%{get_color('RESET')}"
        
        # 적군 상태
        alive_enemies = [e for e in enemies if e.is_alive]
        if alive_enemies:
            status_lines.append(f"{get_color('BRIGHT_RED')}{'─'*70}{get_color('RESET')}")
            status_lines.append(f"{get_color('BRIGHT_WHITE')}⚔️  적군 상태{get_color('RESET')}")
            status_lines.append(f"{get_color('BRIGHT_RED')}{'─'*70}{get_color('RESET')}")
            
            for enemy in alive_enemies:
                if enemy == current_char:
                    name_color = get_color('BRIGHT_RED')
                    status_icon = "▶"
                else:
                    name_color = get_color('WHITE')
                    status_icon = " "
                
                # 🎯 적 타입별 이모지 결정
                enemy_name = enemy.name.lower()
                enemy_icon = "⚔️"  # 기본 아이콘
                
                if '고블린' in enemy_name or 'goblin' in enemy_name:
                    enemy_icon = "👹"
                elif '오크' in enemy_name or 'orc' in enemy_name:
                    enemy_icon = "👿"
                elif '스켈레톤' in enemy_name or 'skeleton' in enemy_name:
                    enemy_icon = "💀"
                elif '드래곤' in enemy_name or 'dragon' in enemy_name:
                    enemy_icon = "🐲"
                elif '슬라임' in enemy_name or 'slime' in enemy_name:
                    enemy_icon = "🟢"
                elif '좀비' in enemy_name or 'zombie' in enemy_name:
                    enemy_icon = "🧟"
                elif '거미' in enemy_name or 'spider' in enemy_name:
                    enemy_icon = "🕷️"
                elif '늑대' in enemy_name or 'wolf' in enemy_name:
                    enemy_icon = "🐺"
                elif '트롤' in enemy_name or 'troll' in enemy_name:
                    enemy_icon = "🔨"
                elif '마법사' in enemy_name or 'mage' in enemy_name:
                    enemy_icon = "🧙"
                elif '다크엘프' in enemy_name or 'darkelf' in enemy_name:
                    enemy_icon = "🧝"
                
                # ATB 게이지
                atb_gauge = getattr(enemy, 'atb_gauge', 0)
                if atb_gauge >= self.ATB_READY_THRESHOLD:
                    atb_display = f"{get_color('BRIGHT_YELLOW')}READY{get_color('RESET')}"
                    atb_bar = self.create_beautiful_atb_gauge(100, 100, 10, False)
                    atb_icon = "⚡"
                else:
                    atb_percent = min(100, int(atb_gauge / self.ATB_READY_THRESHOLD * 100))
                    atb_display = f"{get_color('BRIGHT_CYAN')}{atb_percent}%{get_color('RESET')}"
                    atb_bar = self.create_beautiful_atb_gauge(atb_percent, 100, 10, False)
                    atb_icon = "⏳"
                
                # HP 게이지
                hp_bar = self.create_beautiful_hp_gauge(enemy.current_hp, enemy.max_hp, 10)
                
                # BREAK 상태 표시 추가
                break_status = ""
                if hasattr(enemy, 'is_broken') and enemy.is_broken:
                    break_status = f"  {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                
                # 🌟 적군 상태 효과 표시 (직접 속성 체크 및 status_manager 모두 지원)
                enemy_status_effects = ""
                
                # 독 상태 표시 (우선순위: 직접 속성 → status_manager)
                if hasattr(enemy, 'is_poisoned') and enemy.is_poisoned:
                    poison_turns = getattr(enemy, 'poison_turns', 0)
                    poison_damage = getattr(enemy, 'poison_damage', 0)
                    if poison_turns > 0:
                        enemy_status_effects += f" {get_color('BRIGHT_GREEN')}POISON:{poison_turns}{get_color('RESET')}"
                        print(f"⚔️ [DISPLAY LOG] 적 {enemy.name} 독 표시: {poison_turns}턴 남음, {poison_damage} 피해")
                elif hasattr(enemy, 'status_manager') and enemy.status_manager and enemy.status_manager.has_status("poison"):
                    poison_stacks = enemy.status_manager.get_status_value("poison")
                    if poison_stacks > 0:
                        enemy_status_effects += f" {get_color('BRIGHT_GREEN')}POISON:{poison_stacks}{get_color('RESET')}"
                
                # 화상 상태 표시
                if hasattr(enemy, 'is_burning') and enemy.is_burning:
                    burn_turns = getattr(enemy, 'burn_turns', 0)
                    if burn_turns > 0:
                        enemy_status_effects += f" {get_color('BRIGHT_RED')}BURN:{burn_turns}{get_color('RESET')}"
                elif hasattr(enemy, 'status_manager') and enemy.status_manager and enemy.status_manager.has_status("burn"):
                    burn_stacks = enemy.status_manager.get_status_value("burn")
                    if burn_stacks > 0:
                        enemy_status_effects += f" {get_color('BRIGHT_RED')}BURN:{burn_stacks}{get_color('RESET')}"
                
                # 빙결 상태 표시
                if hasattr(enemy, 'is_frozen') and enemy.is_frozen:
                    freeze_turns = getattr(enemy, 'freeze_turns', 0)
                    if freeze_turns > 0:
                        enemy_status_effects += f" {get_color('BRIGHT_CYAN')}FREEZE:{freeze_turns}{get_color('RESET')}"
                elif hasattr(enemy, 'status_manager') and enemy.status_manager and enemy.status_manager.has_status("freeze"):
                    freeze_turns = enemy.status_manager.get_status_turns("freeze")
                    if freeze_turns > 0:
                        enemy_status_effects += f" {get_color('BRIGHT_CYAN')}FREEZE:{freeze_turns}{get_color('RESET')}"
                
                # 마비 상태 표시
                if hasattr(enemy, 'is_paralyzed') and enemy.is_paralyzed:
                    paralysis_turns = getattr(enemy, 'paralysis_turns', 0)
                    if paralysis_turns > 0:
                        enemy_status_effects += f" {get_color('BRIGHT_YELLOW')}PARALYSIS:{paralysis_turns}{get_color('RESET')}"
                elif hasattr(enemy, 'status_manager') and enemy.status_manager and enemy.status_manager.has_status("paralysis"):
                    paralysis_turns = enemy.status_manager.get_status_turns("paralysis")
                    if paralysis_turns > 0:
                        enemy_status_effects += f" {get_color('BRIGHT_YELLOW')}PARALYSIS:{paralysis_turns}{get_color('RESET')}"
                
                # status_manager 기반 추가 상태들
                if hasattr(enemy, 'status_manager') and enemy.status_manager:
                    
                    # 공격력 디버프
                    if enemy.status_manager.has_status("attack_debuff"):
                        attack_debuff = enemy.status_manager.get_status_value("attack_debuff")
                        debuff_turns = enemy.status_manager.get_status_turns("attack_debuff")
                        if attack_debuff > 0:
                            enemy_status_effects += f" ATK_DOWN:{attack_debuff}({debuff_turns}T)"
                    
                    # 방어력 디버프
                    if enemy.status_manager.has_status("defense_debuff"):
                        defense_debuff = enemy.status_manager.get_status_value("defense_debuff")
                        debuff_turns = enemy.status_manager.get_status_turns("defense_debuff")
                        if defense_debuff > 0:
                            enemy_status_effects += f" DEF_DOWN:{defense_debuff}({debuff_turns}T)"
                    
                    # 속도 디버프
                    if enemy.status_manager.has_status("speed_debuff"):
                        speed_debuff = enemy.status_manager.get_status_value("speed_debuff")
                        debuff_turns = enemy.status_manager.get_status_turns("speed_debuff")
                        if speed_debuff > 0:
                            enemy_status_effects += f" SPD_DOWN:{speed_debuff}({debuff_turns}T)"
                    
                    # 출혈
                    if enemy.status_manager.has_status("bleeding"):
                        bleed_value = enemy.status_manager.get_status_value("bleeding")
                        bleed_turns = enemy.status_manager.get_status_turns("bleeding")
                        if bleed_value > 0:
                            enemy_status_effects += f" BLEED:{bleed_value}({bleed_turns}T)"
                    
                    # 저주
                    if enemy.status_manager.has_status("curse"):
                        curse_turns = enemy.status_manager.get_status_turns("curse")
                        if curse_turns > 0:
                            enemy_status_effects += f" CURSE:{curse_turns}T"
                    
                    # 침묵
                    if enemy.status_manager.has_status("silence"):
                        silence_turns = enemy.status_manager.get_status_turns("silence")
                        if silence_turns > 0:
                            enemy_status_effects += f" SILENCE:{silence_turns}T"
                    
                    # 기절
                    if enemy.status_manager.has_status("stun"):
                        stun_turns = enemy.status_manager.get_status_turns("stun")
                        if stun_turns > 0:
                            enemy_status_effects += f" STUN:{stun_turns}T"
                
                # 🎯 적군 특별 기믹 표시 (직업별 특수 상태)
                enemy_special_mechanic = ""
                if hasattr(enemy, 'character_class'):
                    enemy_class = enemy.character_class
                    print(f"🎯 [DEBUG] 적 기믹 확인: {enemy.name} - {enemy_class}")
                    
                    # 바드 적의 특별 기믹
                    if enemy_class == "바드":
                        # 바드는 특별한 음표 표시 (적이므로 붉은 색조)
                        notes = ["도", "레", "미", "파", "솔", "라", "시"]
                        if hasattr(enemy, 'bardic_notes') and enemy.bardic_notes:
                            current_note = notes[enemy.bardic_notes % len(notes)]
                            enemy_special_mechanic = f" BARDIC:{current_note}"
                        
                    # 네크로맨서 적의 특별 기믹
                    elif enemy_class == "네크로맨서":
                        if hasattr(enemy, 'soul_energy') and enemy.soul_energy > 0:
                            enemy_special_mechanic = f" SOULS:{enemy.soul_energy}"
                        
                    # 시간술사 적의 특별 기믹
                    elif enemy_class == "시간술사":
                        if hasattr(enemy, 'time_charges') and enemy.time_charges > 0:
                            enemy_special_mechanic = f" TIME:{enemy.time_charges}"
                        
                    # 연금술사 적의 특별 기믹
                    elif enemy_class == "연금술사":
                        if hasattr(enemy, 'explosive_stacks') and enemy.explosive_stacks > 0:
                            enemy_special_mechanic = f" EXPLOSIVE:{enemy.explosive_stacks}"
                        
                    # 차원술사 적의 특별 기믹
                    elif enemy_class == "차원술사":
                        if hasattr(enemy, 'dimensional_energy') and enemy.dimensional_energy > 0:
                            enemy_special_mechanic = f" DIMENSION:{enemy.dimensional_energy}"
                        
                    # 드루이드 적의 특별 기믹
                    elif enemy_class == "드루이드":
                        if hasattr(enemy, 'nature_form'):
                            forms = {"wolf": "WOLF", "bear": "BEAR", "eagle": "EAGLE"}
                            if enemy.nature_form in forms:
                                enemy_special_mechanic = f" FORM:{forms[enemy.nature_form]}"
                        
                    # 광전사 적의 특별 기믹 - 0일 때도 표시
                    elif enemy_class == "광전사":
                        rage_stacks = getattr(enemy, 'rage_stacks', 0)
                        enemy_special_mechanic = f" 💥RAGE:{rage_stacks}"
                        
                    # 철학자 적의 특별 기믹
                    elif enemy_class == "철학자":
                        if hasattr(enemy, 'wisdom_points') and enemy.wisdom_points > 0:
                            enemy_special_mechanic = f" WISDOM:{enemy.wisdom_points}"
                        
                    # 마검사 적의 특별 기믹
                    elif enemy_class == "마검사":
                        if hasattr(enemy, 'magic_sword_charge') and enemy.magic_sword_charge > 0:
                            enemy_special_mechanic = f" MAGSWORD:{enemy.magic_sword_charge}"
                
                status_lines.append(f"{status_icon} {enemy_icon} {name_color}{enemy.name}{get_color('RESET')}{enemy_status_effects}{enemy_special_mechanic}")
                status_lines.append(f"   💚 HP: {enemy.current_hp} / {enemy.max_hp} {get_color('WHITE')}{{{hp_bar}}}{get_color('RESET')} | ⚡ BRV: {getattr(enemy, 'brave_points', 0)}")
                status_lines.append(f"  {atb_icon} {get_color('WHITE')}{{{atb_bar}}}{get_color('RESET')} {atb_display} | SPD: {getattr(enemy, 'speed', 50)}{break_status}")

        return "\n".join(status_lines)

    def _play_skill_sfx(self, skill):
        """스킬 사용 SFX 재생 - 실제 존재하는 스킬 기반"""
        try:
            from .new_skill_system import SkillType
            
            skill_type = skill.get("type", SkillType.BRV_ATTACK)
            skill_name = skill.get("name", "").lower()
            
            # 🔊 우선순위 1: 스킬에 직접 정의된 SFX (가장 높은 우선순위)
            direct_sfx = skill.get("sfx")
            if direct_sfx:
                sfx_name = direct_sfx
            else:
                # 실제 존재하는 스킬명 기반 특별 SFX 매핑
                special_skill_sfx = {
                # === 전사 계열 ===
                "분노 축적": "berserk",
                "방패 들기": "protect", 
                "강타": "sword_hit",
                "전사의 외침": "protect",
                "돌진 베기": "critical_hit",
                "광전사의 각성": "limit_break",
                
                # === 검성 계열 ===
                "검심 집중": "protect",
                "일섬": "sword_hit",
                "검기 방출": "sword_hit",
                "반격 태세": "protect",
                "연속 베기": "sword_hit",
                "무념무상": "limit_break",
                
                # === 검투사 계열 ===
                "투기장의 기술": "sword_hit",
                "군중의 함성": "berserk",
                "네트 던지기": "item_use",
                "트라이던트 찌르기": "critical_hit",
                "결투자의 명예": "protect",
                "콜로세움의 왕": "limit_break",
                
                # === 광전사 계열 ===
                "광기의 씨앗": "berserk",
                "무모한 돌격": "critical_hit",
                "피의 갈증": "heal",
                "파괴의 일격": "critical_hit",
                "분노 폭발": "limit_break",
                "버서커의 최후": "limit_break",
                
                # === 기사 계열 ===
                "방패 방어": "protect",
                "창 돌격": "sword_hit",
                "아군 보호": "protect",
                "기사도 정신": "protect",
                "성스러운 돌격": "critical_hit",
                "수호기사의 맹세": "limit_break",
                
                # === 성기사 계열 ===
                "신앙의 힘": "protect",
                "성스러운타격": "sword_hit",
                "축복": "heal",
                "치유의 빛": "heal2",
                "부활": "phoenix_down",
                "천사의 강림": "limit_break",
                
                # === 암흑기사 계열 ===
                "어둠의 계약": "poison",
                "생명 흡수": "heal",
                "저주의 검": "poison",
                "어둠의 보호": "protect",
                "흡혈": "heal",
                "어둠의 지배자": "limit_break",
                
                # === 용기사 계열 ===
                "용의 비늘": "protect",
                "드래곤 클로": "critical_hit",
                "화염 숨결": "fire",
                "용의 위엄": "berserk",
                "드래곤 스피어": "critical_hit",
                "드래곤 로드": "limit_break",
                
                # === 아크메이지 계열 ===
                "마나 집중": "magic_cast",
                "매직 미사일": "magic_cast",
                "파이어볼": "fire",
                "마법 방어막": "barrier",
                "라이트닝 볼트": "thunder",
                "메테오": "fire3",
                
                # === 정령술사 계열 ===
                "정령과의 교감": "summon",
                "화염 정령": "fire",
                "물 정령의 치유": "heal2",
                "바람 정령의 축복": "haste",
                "대지 정령의 분노": "fire2",
                "사대 정령 소환": "limit_break",
                
                # === 시간술사 계열 ===
                "시간 가속": "haste",
                "시간 왜곡": "slow",
                "시간 되돌리기": "heal3",
                "미래 예지": "protect",
                "시간 정지": "stop",
                "시공간 붕괴": "limit_break",
                
                # === 차원술사 계열 ===
                "차원 균열": "magic_cast",
                "순간이동": "teleport",
                "공간 왜곡": "slow",
                "차원 방패": "barrier",
                "공간 절단": "critical_hit",
                "차원 폭풍": "limit_break",
                
                # === 철학자 계열 ===
                "진리 탐구": "magic_cast",
                "진실 간파": "magic_cast",
                "지혜의 빛": "heal",
                "존재 부정": "critical_hit",
                "철학적 사고": "protect",
                "절대 진리": "limit_break",
                
                # === 궁수 계열 ===
                "조준": "protect",
                "정밀 사격": "gun_hit",
                "관통 화살": "gun_critical",
                "정찰 화살": "gun_hit",
                "삼연사": "gun_critical",
                "천공의 화살": "limit_break",
                
                # === 암살자 계열 ===
                "그림자 숨기": "silence",
                "기습": "critical_hit",
                "독 바르기": "poison",
                "그림자 연막": "silence",
                "암살술": "critical_hit",
                "그림자 분신": "limit_break",
                
                # === 도적 계열 ===
                "재빠른 손놀림": "haste",
                "기습 공격": "critical_hit",
                "아이템 훔치기": "item_pickup",
                "연속 베기": "sword_hit",
                "숨겨둔 아이템": "item_use",
                "완벽한 도둑질": "limit_break",
                
                # === 해적 계열 ===
                "이도류": "sword_hit",
                "칼부림": "sword_hit",
                "바다의 저주": "poison",
                "해적의 함성": "berserk",
                "해상 치료술": "heal2",
                }
                
                # 우선순위 2: 특별한 스킬명 매핑
                if skill_name in special_skill_sfx:
                    sfx_name = special_skill_sfx[skill_name]
                
                # 우선순위 3: 스킬 타입별 기본 SFX
                elif skill_type == SkillType.BRV_ATTACK:
                    # BRV 공격을 무기/공격 스타일별로 세분화
                    if any(keyword in skill_name for keyword in ["검", "베기", "검기", "검술", "일섬", "칼", "클로"]):
                        sfx_name = "sword_hit"
                    elif any(keyword in skill_name for keyword in ["사격", "화살", "총", "활", "정밀"]):
                        sfx_name = "gun_hit"
                    elif any(keyword in skill_name for keyword in ["주먹", "펀치", "타격", "몽크", "기습"]):
                        sfx_name = "punch_hit"
                    elif any(keyword in skill_name for keyword in ["돌격", "충격", "강타", "미사일"]):
                        sfx_name = "critical_hit"
                    elif any(keyword in skill_name for keyword in ["마법", "정령", "차원", "매직"]):
                        sfx_name = "magic_cast"
                    else:
                        sfx_name = "sword_hit"  # 기본 물리 공격
                        
                elif skill_type == SkillType.HP_ATTACK:
                    # HP 공격을 강도별로 분류
                    if any(keyword in skill_name for keyword in ["필살", "궁극", "죽음", "파괴", "스피어", "절단"]):
                        sfx_name = "limit_break"
                    elif any(keyword in skill_name for keyword in ["크리티컬", "치명", "강타", "일격", "흡혈", "암살"]):
                        sfx_name = "critical_hit"
                    elif any(keyword in skill_name for keyword in ["볼트", "번개", "전기"]):
                        sfx_name = "thunder"
                    else:
                        sfx_name = "critical_hit"  # 기본 HP 공격
                        
                elif skill_type == SkillType.BRV_HP_ATTACK:
                    # 복합 공격
                    if any(keyword in skill_name for keyword in ["폭발", "삼연사", "분신"]):
                        sfx_name = "limit_break"
                    else:
                        sfx_name = "sword_hit"
                    
                elif skill_type == SkillType.HEAL:
                    # 치유를 강도별로 분류
                    if any(keyword in skill_name for keyword in ["되돌리기", "부활", "완전"]):
                        sfx_name = "heal3"
                    elif any(keyword in skill_name for keyword in ["정령", "빛", "치료술"]):
                        sfx_name = "heal2"
                    else:
                        sfx_name = "heal"
                        
                elif skill_type == SkillType.BUFF:
                    # 버프를 종류별로 분류
                    if any(keyword in skill_name for keyword in ["방어", "보호", "방패", "방벽", "집중", "태세"]):
                        sfx_name = "protect"
                    elif any(keyword in skill_name for keyword in ["속도", "민첩", "가속", "손놀림"]):
                        sfx_name = "haste"
                    elif any(keyword in skill_name for keyword in ["축복", "정신", "힘", "교감"]):
                        sfx_name = "heal"
                    elif any(keyword in skill_name for keyword in ["배리어", "방어막"]):
                        sfx_name = "barrier"
                    elif any(keyword in skill_name for keyword in ["함성", "외침", "분노", "축적"]):
                        sfx_name = "berserk"
                    else:
                        sfx_name = "protect"
                        
                elif skill_type == SkillType.DEBUFF:
                    # 디버프를 종류별로 분류
                    if any(keyword in skill_name for keyword in ["독", "바르기", "저주", "맹독"]):
                        sfx_name = "poison"
                    elif any(keyword in skill_name for keyword in ["침묵", "봉인", "연막"]):
                        sfx_name = "silence"
                    elif any(keyword in skill_name for keyword in ["수면", "잠", "자장가"]):
                        sfx_name = "sleep"
                    elif any(keyword in skill_name for keyword in ["정지", "스톱", "왜곡"]):
                        sfx_name = "stop"
                    elif any(keyword in skill_name for keyword in ["둔화", "감속", "왜곡"]):
                        sfx_name = "slow"
                    elif any(keyword in skill_name for keyword in ["위엄", "공포"]):
                        sfx_name = "berserk"
                    else:
                        sfx_name = "poison"
                        
                elif skill_type == SkillType.SPECIAL:
                    # 특수 스킬
                    if any(keyword in skill_name for keyword in ["훔치기", "도둑질"]):
                        sfx_name = "item_pickup"
                    elif any(keyword in skill_name for keyword in ["계약", "간파", "예지"]):
                        sfx_name = "magic_cast"
                    elif any(keyword in skill_name for keyword in ["부활", "되살리기"]):
                        sfx_name = "phoenix_down"
                    elif any(keyword in skill_name for keyword in ["사고", "명예"]):
                        sfx_name = "protect"
                    else:
                        sfx_name = "magic_cast"
                        
                elif skill_type == SkillType.ULTIMATE:
                    # 궁극기를 속성별로 분류
                    if any(keyword in skill_name for keyword in ["화염", "불", "파이어", "메테오", "로드"]):
                        sfx_name = "fire3"
                    elif any(keyword in skill_name for keyword in ["냉기", "얼음", "블리자드"]):
                        sfx_name = "ice3"
                    elif any(keyword in skill_name for keyword in ["번개", "전기", "썬더", "볼트"]):
                        sfx_name = "thunder3"
                    elif any(keyword in skill_name for keyword in ["소환", "정령", "강림"]):
                        sfx_name = "summon"
                    elif any(keyword in skill_name for keyword in ["붕괴", "폭풍", "진리"]):
                        sfx_name = "ultima"
                    else:
                        sfx_name = "limit_break"
                        
                elif skill_type == SkillType.FIELD:
                    # 필드 스킬
                    if any(keyword in skill_name for keyword in ["연막", "숨기기"]):
                        sfx_name = "silence"
                    elif any(keyword in skill_name for keyword in ["치료", "회복"]):
                        sfx_name = "heal2"
                    elif any(keyword in skill_name for keyword in ["정지", "시간"]):
                        sfx_name = "stop"
                    else:
                        sfx_name = "magic_cast"
                        
                elif skill_type == SkillType.SUPPORT:
                    # 서포트 스킬 - 전술 분석 등
                    if any(keyword in skill_name for keyword in ["전술", "분석", "자세", "태세"]):
                        sfx_name = "magic_cast"
                    elif any(keyword in skill_name for keyword in ["방어", "보호", "방패"]):
                        sfx_name = "protect"
                    elif any(keyword in skill_name for keyword in ["버프", "강화", "축복"]):
                        sfx_name = "heal"
                    else:
                        sfx_name = "magic_cast"
                    
                elif skill_type == SkillType.COUNTER:
                    # 반격 스킬
                    sfx_name = "protect"
                else:
                    # 기본 SFX
                    sfx_name = "menu_confirm"
            
            # SFX 재생 (폴백 지원)
            if sfx_name:
                success = False
                if self.audio_system:
                    success = self.audio_system.play_sfx(sfx_name)
                    if not success:
                        # 폴백 SFX 시도
                        fallback_sfx = self._get_fallback_sfx(skill_type)
                        success = self.audio_system.play_sfx(fallback_sfx)
                elif self.sound_manager:
                    success = self.sound_manager.play_sfx(sfx_name)
                    if not success:
                        fallback_sfx = self._get_fallback_sfx(skill_type)
                        success = self.sound_manager.play_sfx(fallback_sfx)
                    
        except Exception as e:
            print(f"⚠️ SFX 재생 오류: {e}")
            
    def _get_cooking_multiplier(self, character):
        """요리 효과에 따른 데미지 배율 및 상태 메시지 반환"""
        try:
            from game.field_cooking import get_brv_cooking_modifiers
            cooking_modifiers = get_brv_cooking_modifiers()
            
            multiplier = 1.0
            status_msg = ""
            
            # BRV 데미지 보너스 적용
            if "brv_damage_multiplier" in cooking_modifiers:
                multiplier *= cooking_modifiers["brv_damage_multiplier"]
                if cooking_modifiers["brv_damage_multiplier"] > 1.0:
                    bonus_percent = int((cooking_modifiers["brv_damage_multiplier"] - 1.0) * 100)
                    status_msg = f"🍳 요리 효과로 데미지 {bonus_percent}% 증가!"
            
            return multiplier, status_msg
            
        except ImportError:
            # 요리 시스템이 없으면 기본값 반환
            return 1.0, ""
        except Exception as e:
            # 오류 발생 시 기본값 반환
            return 1.0, ""
            
    def _check_dodge(self, attacker: Character, target: Character) -> bool:
        """회피 체크 - 명중률 vs 회피율 계산"""
        try:
            # 공격자 명중률 계산
            attacker_accuracy = getattr(attacker, 'accuracy', 85)
            
            # 적의 명중률 감소 효과 적용 (연막탄 등)
            if hasattr(target, 'temp_enemy_accuracy_down') and target.temp_enemy_accuracy_down > 0:
                attacker_accuracy -= target.temp_enemy_accuracy_down
            
            # 수비자 회피율 계산
            target_evasion = getattr(target, 'evasion', 10)
            
            # 임시 회피 보너스 적용
            if hasattr(target, 'temp_dodge_bonus'):
                target_evasion += target.temp_dodge_bonus
                
            # 차원술사 공간 이동 - 100% 회피
            if hasattr(target, 'temp_dimension_dodge') and target.temp_dimension_dodge:
                return True
                
            # 생존 본능 특성 - HP 30% 이하에서 회피율 50% 증가
            if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
                if target.current_hp <= target.max_hp * 0.3:
                    if hasattr(target, 'temp_dodge_bonus'):
                        # 생존 본능이 있는 캐릭터인지 확인
                        for trait in getattr(target, 'traits', []):
                            if "생존 본능" in trait.name:
                                target_evasion += 50
                                break
            
            # 명중률 계산 공식: (공격자 명중률 / 수비자 회피율) * 100
            # 최소 5%, 최대 95% 명중률 보장
            if target_evasion <= 0:
                target_evasion = 1  # 0 나누기 방지
            hit_chance = min(95, max(5, (attacker_accuracy / target_evasion) * 100))
            
            # 회피 판정
            import random
            dodge_roll = random.randint(1, 100)
            is_dodged = dodge_roll > hit_chance
            
            return is_dodged
            
        except Exception as e:
            print(f"⚠️ 회피 체크 오류: {e}")
            return False  # 오류 시 회피하지 않음
            
    def _get_fallback_sfx(self, skill_type):
        """스킬 타입별 폴백 SFX 반환"""
        try:
            from .new_skill_system import SkillType
            fallback_map = {
                SkillType.BRV_ATTACK: "sword_hit",
                SkillType.HP_ATTACK: "critical_hit", 
                SkillType.BRV_HP_ATTACK: "limit_break",
                SkillType.HEAL: "heal",
                SkillType.BUFF: "protect",
                SkillType.DEBUFF: "poison",
                SkillType.SPECIAL: "magic_cast",
                SkillType.ULTIMATE: "limit_break",
                SkillType.FIELD: "magic_cast",
                SkillType.COUNTER: "protect"
            }
            return fallback_map.get(skill_type, "menu_confirm")
        except:
            return "menu_confirm"
            
    def _show_hit_evasion_test(self, party: List[Character], enemies: List[Character]):
        """명중률/회피율 테스트 화면"""
        while True:
            print(f"\n{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
            print(f"{get_color('BRIGHT_YELLOW')}🎯 명중률/회피율 테스트{get_color('RESET')}")
            print(f"{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
            
            try:
                from .cursor_menu_system import create_simple_menu
                
                # 모든 살아있는 캐릭터 목록
                all_chars = [c for c in party + enemies if c.is_alive]
                
                # 공격자 선택 메뉴
                attacker_options = []
                attacker_descriptions = []
                
                for char in all_chars:
                    accuracy = getattr(char, 'accuracy', 85)
                    temp_dodge = getattr(char, 'temp_dodge_bonus', 0)
                    char_type = "🛡️" if char in party else "⚔️"
                    
                    attacker_options.append(f"{char_type} {char.name}")
                    attacker_descriptions.append(f"명중률: {accuracy}% | 임시 회피: +{temp_dodge}%")
                
                attacker_options.append("🔙 돌아가기")
                attacker_descriptions.append("상세 상태 메뉴로 돌아갑니다")
                
                attacker_menu = create_simple_menu("🎯 공격자 선택", attacker_options, attacker_descriptions, clear_screen=False)
                attacker_choice = attacker_menu.run()
                
                if attacker_choice is None or attacker_choice == len(attacker_options) - 1:
                    break
                    
                attacker = all_chars[attacker_choice]
                
                # 대상 선택 메뉴
                target_options = []
                target_descriptions = []
                
                for char in all_chars:
                    if char != attacker:  # 자기 자신 제외
                        evasion = getattr(char, 'evasion', 10)
                        temp_dodge = getattr(char, 'temp_dodge_bonus', 0)
                        temp_dimension = getattr(char, 'temp_dimension_dodge', False)
                        char_type = "🛡️" if char in party else "⚔️"
                        
                        target_options.append(f"{char_type} {char.name}")
                        special_status = " [차원이동]" if temp_dimension else ""
                        target_descriptions.append(f"회피율: {evasion}% | 회피보너스: +{temp_dodge}%{special_status}")
                
                target_options.append("🔙 돌아가기")
                target_descriptions.append("공격자 선택으로 돌아갑니다")
                
                target_menu = create_simple_menu("🛡️ 대상 선택", target_options, target_descriptions, clear_screen=False)
                target_choice = target_menu.run()
                
                if target_choice is None or target_choice == len(target_options) - 1:
                    continue
                    
                # 자기 자신이 아닌 캐릭터 중에서 선택
                available_targets = [c for c in all_chars if c != attacker]
                target = available_targets[target_choice]
                
                # 명중률 계산 및 테스트 실행
                self._run_hit_evasion_simulation(attacker, target)
                
            except ImportError:
                # 폴백: 간단한 텍스트 메뉴
                print("\n🎯 간단 명중률 테스트:")
                print("1. 모든 캐릭터 상호 명중률 표시")
                print("2. 돌아가기")
                
                try:
                    choice = int(input("선택: "))
                    if choice == 1:
                        self._show_all_hit_rates(party, enemies)
                    elif choice == 2:
                        break
                except:
                    continue
    
    def _run_hit_evasion_simulation(self, attacker: Character, target: Character):
        """명중률/회피율 시뮬레이션 실행"""
        print(f"\n{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        print(f"{get_color('BRIGHT_YELLOW')}🎯 {attacker.name} → {target.name} 명중률 테스트{get_color('RESET')}")
        print(f"{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        
        # 스탯 정보 표시
        attacker_accuracy = getattr(attacker, 'accuracy', 85)
        target_evasion = getattr(target, 'evasion', 10)
        target_dodge_bonus = getattr(target, 'temp_dodge_bonus', 0)
        target_dimension_dodge = getattr(target, 'temp_dimension_dodge', False)
        enemy_accuracy_down = getattr(target, 'temp_enemy_accuracy_down', 0)
        
        print(f"\n📊 기본 스탯:")
        print(f"  🏹 {attacker.name} 명중률: {attacker_accuracy}%")
        if enemy_accuracy_down > 0:
            print(f"    - 적 명중률 감소: -{enemy_accuracy_down}% (연막탄 등)")
        print(f"  🏃 {target.name} 회피율: {target_evasion}%")
        if target_dodge_bonus > 0:
            print(f"    + 임시 회피 보너스: +{target_dodge_bonus}%")
        if target_dimension_dodge:
            print(f"    + 차원 이동: 100% 회피!")
        
        # 생존 본능 특성 체크
        survival_bonus = 0
        if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
            if target.current_hp <= target.max_hp * 0.3:
                for trait in getattr(target, 'traits', []):
                    if "생존 본능" in trait.name:
                        survival_bonus = 50
                        print(f"    + 생존 본능 (HP 30% 이하): +{survival_bonus}%")
                        break
        
        # 최종 명중률 계산
        if target_dimension_dodge:
            hit_chance = 0
            print(f"\n💫 차원 이동으로 인한 100% 회피!")
        else:
            final_accuracy = attacker_accuracy - enemy_accuracy_down
            final_evasion = target_evasion + target_dodge_bonus + survival_bonus
            hit_chance = min(95, max(25, (final_accuracy / max(final_evasion, 1)) * 100))
            
            print(f"\n🎲 최종 계산:")
            print(f"  명중률 공식: min(95, max(25, (공격자명중률 / 수비자회피율) * 100))")
            print(f"  실제 계산: min(95, max(25, ({final_accuracy} / {final_evasion}) * 100))")
            print(f"  💥 최종 명중률: {hit_chance:.1f}%")
            print(f"  💨 회피 확률: {100-hit_chance:.1f}%")
        
        # 시뮬레이션 실행
        print(f"\n🎮 100회 시뮬레이션 실행 중...")
        import random
        hits = 0
        dodges = 0
        
        for i in range(100):
            if target_dimension_dodge:
                dodges += 1
            else:
                roll = random.randint(1, 100)
                if roll <= hit_chance:
                    hits += 1
                else:
                    dodges += 1
        
        print(f"\n📈 시뮬레이션 결과:")
        print(f"  💥 명중: {hits}회 ({hits}%)")
        print(f"  💨 회피: {dodges}회 ({dodges}%)")
        print(f"  📊 이론치: 명중 {hit_chance:.1f}% / 회피 {100-hit_chance:.1f}%")
        
        if abs(hits - hit_chance) <= 10:
            print(f"  ✅ 시뮬레이션 결과가 이론치와 거의 일치합니다!")
        else:
            print(f"  ⚠️ 시뮬레이션 결과와 이론치에 차이가 있습니다 (확률의 오차)")
        
        # 키 버퍼 클리어 후 키 대기
        self.keyboard.clear_input_buffer()
        self.keyboard.wait_for_key(f"\n{get_color('BRIGHT_GREEN')}⏎ 계속하려면 Enter를 누르세요...{get_color('RESET')}")
    
    def _show_all_hit_rates(self, party: List[Character], enemies: List[Character]):
        """모든 캐릭터 간 명중률 매트릭스 표시"""
        print(f"\n{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        print(f"{get_color('BRIGHT_YELLOW')}🎯 전체 명중률 매트릭스{get_color('RESET')}")
        print(f"{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        
        all_chars = [c for c in party + enemies if c.is_alive]
        
        print(f"\n📊 공격자 → 대상 명중률:")
        print(f"{'공격자':<12} {'→':<3} {'대상':<12} {'명중률':<8} {'회피율':<8}")
        print("-" * 50)
        
        for attacker in all_chars:
            attacker_accuracy = getattr(attacker, 'accuracy', 85)
            attacker_type = "🛡️" if attacker in party else "⚔️"
            
            for target in all_chars:
                if target != attacker:
                    target_evasion = getattr(target, 'evasion', 10)
                    target_dodge = getattr(target, 'temp_dodge_bonus', 0)
                    target_dimension = getattr(target, 'temp_dimension_dodge', False)
                    target_type = "🛡️" if target in party else "⚔️"
                    
                    if target_dimension:
                        hit_chance = 0
                    else:
                        final_evasion = target_evasion + target_dodge
                        hit_chance = min(95, max(25, (attacker_accuracy / max(final_evasion, 1)) * 100))
                    
                    attacker_name = f"{attacker_type}{attacker.name[:8]}"
                    target_name = f"{target_type}{target.name[:8]}"
                    
                    print(f"{attacker_name:<12} {'→':<3} {target_name:<12} {hit_chance:>6.1f}% {100-hit_chance:>6.1f}%")
        
        # 키 버퍼 클리어 후 키 대기
        self.keyboard.clear_input_buffer()
        self.keyboard.wait_for_key(f"\n{get_color('BRIGHT_GREEN')}⏎ 계속하려면 Enter를 누르세요...{get_color('RESET')}")
    
    def _get_fallback_sfx(self, skill_type):
        """SFX 폴백 매핑"""
        from .new_skill_system import SkillType
        
        fallback_map = {
            SkillType.BRV_ATTACK: "sword_hit",
            SkillType.HP_ATTACK: "critical_hit", 
            SkillType.BRV_HP_ATTACK: "sword_hit",
            SkillType.HEAL: "heal",
            SkillType.BUFF: "protect",
            SkillType.DEBUFF: "poison",
            SkillType.SPECIAL: "magic_cast",
            SkillType.ULTIMATE: "limit_break"
        }
        
        return fallback_map.get(skill_type, "menu_confirm")

    def show_detailed_combat_status(self, current_char: Character, party: List[Character], enemies: List[Character]):
        """상세한 전투 상태 표시 - 개별 캐릭터 상세 조회 가능 (ATB 시간 정지)"""
        # ATB 시간 정지 (불릿타임 무시)
        self.pause_atb("상세 파티 상태창")
        
        try:
            while True:
                print(f"\n{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
                print(f"{get_color('BRIGHT_CYAN')}📊 실시간 상태 - 상세 조회 (ATB 정지 중){get_color('RESET')}")
                print(f"{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
                
                try:
                    from .cursor_menu_system import create_simple_menu
                    
                    # 메뉴 옵션 구성
                    menu_options = []
                    menu_descriptions = []
                    
                    # 아군 파티 멤버들
                    for i, member in enumerate(party, 1):
                        if member.is_alive:
                            hp_ratio = member.current_hp / member.max_hp
                            mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                            brave = getattr(member, 'brave_points', 0)
                            
                            hp_status = "🟢" if hp_ratio > 0.7 else "🟡" if hp_ratio > 0.4 else "🔴"
                            mp_status = "🔵" if mp_ratio > 0.5 else "🟣"
                            brave_status = "⚡"
                            
                            # BREAK 상태 확인
                            break_status = ""
                            if hasattr(member, 'is_broken_state') and member.is_broken_state:
                                break_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                            
                            menu_options.append(f"{hp_status} {member.name} ({member.character_class}){break_status}")
                            menu_descriptions.append(f"HP: {member.current_hp}/{member.max_hp} | MP: {member.current_mp}/{member.max_mp} | BRV: {brave}{break_status}")
                        else:
                            menu_options.append(f"💀 {member.name} (전투불능)")
                            menu_descriptions.append("상태: 사망 - 상세 정보 없음")
                
                    # 구분선
                    menu_options.append("─── 적군 정보 ───")
                    menu_descriptions.append("적군들의 상태를 확인할 수 있습니다")
                    
                    # 적군들
                    alive_enemies = [e for e in enemies if e.is_alive]
                    for enemy in alive_enemies:
                        hp_ratio = enemy.current_hp / enemy.max_hp
                        brave = getattr(enemy, 'brave_points', 0)
                        
                        hp_status = "🟢" if hp_ratio > 0.7 else "🟡" if hp_ratio > 0.4 else "🔴"
                        brave_status = "⚡"
                        break_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}" if hasattr(enemy, 'is_broken') and enemy.is_broken else ""
                        
                        menu_options.append(f"{hp_status} {enemy.name}{break_status}")
                        menu_descriptions.append(f"HP: {enemy.current_hp}/{enemy.max_hp} | BRV: {brave}")
                    
                    # 전투 정보
                    menu_options.append("─── 전투 정보 ───")
                    menu_descriptions.append("전체 전투 상황과 턴 순서를 확인합니다")
                    
                    menu_options.append("📊 전투 현황 요약")
                    menu_descriptions.append("현재 전투의 전체적인 상황을 요약해서 봅니다")
                    
                    menu_options.append("⏰ 턴 순서 예측")
                    menu_descriptions.append("ATB 게이지를 기반으로 다음 턴 순서를 예측합니다")
                    
                    menu_options.append("🎯 명중률/회피율 테스트")
                    menu_descriptions.append("캐릭터들 간의 명중률과 회피율을 테스트해봅니다")
                    
                    menu_options.append("🔙 돌아가기")
                    menu_descriptions.append("전투 화면으로 돌아갑니다")
                    
                    menu = create_simple_menu("📊 실시간 상태 조회", menu_options, menu_descriptions, clear_screen=False)
                    choice = menu.run()
                    
                    if choice is None or choice == len(menu_options) - 1:  # 돌아가기
                        break
                    elif choice < len(party):  # 파티 멤버 선택
                        selected_member = party[choice]
                        self._show_character_detail(selected_member, True)
                    elif choice == len(party):  # 구분선 (적군)
                        continue
                    elif choice < len(party) + 1 + len(alive_enemies):  # 적군 선택
                        enemy_index = choice - len(party) - 1
                        selected_enemy = alive_enemies[enemy_index]
                        self._show_character_detail(selected_enemy, False)
                    elif choice == len(party) + 1 + len(alive_enemies):  # 구분선 (전투 정보)
                        continue
                    elif choice == len(party) + 2 + len(alive_enemies):  # 전투 현황 요약
                        self._show_battle_summary(current_char, party, enemies)
                    elif choice == len(party) + 3 + len(alive_enemies):  # 턴 순서 예측
                        self._show_turn_order_prediction(party + enemies)
                    elif choice == len(party) + 4 + len(alive_enemies):  # 명중률/회피율 테스트
                        self._show_hit_evasion_test(party, enemies)
                    
                except ImportError:
                    # 폴백: 간단한 정보만 표시
                    print(f"\n{get_color('BRIGHT_BLUE')}🛡️ 아군 파티:{get_color('RESET')}")
                    for i, member in enumerate(party, 1):
                        if member.is_alive:
                            hp_ratio = int(member.current_hp/member.max_hp*100)
                            mp_ratio = int(member.current_mp/max(1,member.max_mp)*100)
                            brave = getattr(member, 'brave_points', 0)
                            print(f"  {i}. {member.name}: HP {hp_ratio}% | MP {mp_ratio}% | BRV {brave}")
                        else:
                            print(f"  {i}. {member.name}: 💀 사망")
                    
                    print(f"\n{get_color('BRIGHT_RED')}⚔️ 적군:{get_color('RESET')}")
                    for i, enemy in enumerate(alive_enemies, 1):
                        hp_ratio = int(enemy.current_hp/enemy.max_hp*100)
                        brave = getattr(enemy, 'brave_points', 0)
                        break_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}" if hasattr(enemy, 'is_broken') and enemy.is_broken else ""
                        print(f"  {i}. {enemy.name}: HP {hp_ratio}% | BRV {brave}{break_status}")
                    
                    break
        finally:
            # ATB 시간 재개
            self.resume_atb()
    
    def _show_character_detail(self, character: Character, is_ally: bool):
        """개별 캐릭터의 매우 상세한 정보 표시"""
        print(f"\n{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        if is_ally:
            print(f"{get_color('BRIGHT_BLUE')}🛡️ {character.name} 상세 정보{get_color('RESET')}")
        else:
            print(f"{get_color('BRIGHT_RED')}⚔️ {character.name} 상세 정보{get_color('RESET')}")
        print(f"{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        
        # 기본 정보
        print(f"\n📋 기본 정보:")
        print(f"  이름: {character.name}")
        if hasattr(character, 'character_class'):
            print(f"  클래스: {character.character_class}")
        if hasattr(character, 'level'):
            print(f"  레벨: {character.level}")
        
        # 생명력 상태
        print(f"\n💚 생명력 상태:")
        hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
        hp_bar = "█" * int(hp_ratio * 20) + "░" * (20 - int(hp_ratio * 20))
        hp_color = get_color('BRIGHT_GREEN') if hp_ratio > 0.7 else get_color('YELLOW') if hp_ratio > 0.4 else get_color('BRIGHT_RED')
        print(f"  HP: {get_color('WHITE')}[{hp_color}{hp_bar}{get_color('WHITE')}] {character.current_hp}{get_color('WHITE')}/{character.max_hp} ({int(hp_ratio*100)}%){get_color('RESET')}")
        
        # 상처 시스템 (아군만)
        if is_ally and hasattr(character, 'wounds'):
            if character.wounds > 0:
                wound_ratio = character.wounds / character.max_hp if character.max_hp > 0 else 0
                wound_severity = "경상" if wound_ratio < 0.1 else "중상" if wound_ratio < 0.3 else "중태"
                print(f"  WOUND: {character.wounds} ({wound_severity})")
                print(f"  🏥 치료 가능 HP: {character.max_hp - character.wounds}")
            # WOUND가 0일 때는 아무것도 표시하지 않음
        
        # 마나 상태 (아군만)
        if is_ally and hasattr(character, 'current_mp'):
            mp_ratio = character.current_mp / character.max_mp if character.max_mp > 0 else 0
            mp_bar = "█" * int(mp_ratio * 20) + "░" * (20 - int(mp_ratio * 20))
            mp_color = get_color('BRIGHT_CYAN') if mp_ratio > 0.7 else get_color('BLUE') if mp_ratio > 0.3 else get_color('BRIGHT_BLACK')
            print(f"\n💙 마나 상태:")
            print(f"  MP: {get_color('WHITE')}[{mp_color}{mp_bar}{get_color('WHITE')}] {character.current_mp}{get_color('WHITE')}/{character.max_mp} ({int(mp_ratio*100)}%){get_color('RESET')}")
        
        # Brave 시스템
        brave_points = getattr(character, 'brave_points', 0)
        print(f"\n⚡ Brave 시스템:")
        # 통일된 이모지와 색상 사용
        brave_status = "전투력" if brave_points >= 300 else "축적중"
        brave_color = get_color('BRIGHT_YELLOW')
        
        # 적군인지 확인하여 표시량 조정
        brave_display = brave_points
        print(f"  BRV: {brave_color}{brave_display}{get_color('RESET')} ({brave_status})")
        
        # BREAK 상태
        if hasattr(character, 'is_broken') and character.is_broken:
            print(f"  💥 상태: {get_color('BRIGHT_MAGENTA')}BREAK - 받는 HP 데미지 1.5배{get_color('RESET')}")
        
        # ATB 게이지
        atb_gauge = getattr(character, 'atb_gauge', 0)
        # 디스플레이용으로 정확한 백분율 계산
        display_atb = min(100, int(atb_gauge / self.ATB_READY_THRESHOLD * 100))
        atb_bar = "█" * int(display_atb/5) + "░" * (20-int(display_atb/5))
        atb_color = get_color('BRIGHT_CYAN') if atb_gauge >= self.ATB_READY_THRESHOLD else get_color('CYAN') if display_atb >= 75 else get_color('BLUE')
        print(f"\n⏱️ ATB (액션 타임 배틀):")
        print(f"  게이지: {get_color('WHITE')}[{atb_color}{atb_bar}{get_color('WHITE')}] {int(display_atb)}%{get_color('RESET')}")
        if atb_gauge >= self.ATB_READY_THRESHOLD:
            print(f"  상태: ⚡ 행동 준비 완료!")
        else:
            turns_to_ready = int((self.ATB_READY_THRESHOLD - atb_gauge) / 800)  # ATB 스케일에 맞춰 계산 조정
            print(f"  예상: {turns_to_ready}턴 후 행동 가능")
        
        # 능력치 (아군만)
        if is_ally:
            print(f"\n{get_color('BRIGHT_CYAN')}⚔️ 전투 능력치{get_color('RESET')}")
            print(f"{get_color('CYAN')}{'─'*50}{get_color('RESET')}")
            
            if hasattr(character, 'physical_attack'):
                # 공격력 색상 계산
                atk_color = get_color('BRIGHT_RED') if character.physical_attack >= 100 else get_color('RED') if character.physical_attack >= 80 else get_color('YELLOW') if character.physical_attack >= 60 else get_color('WHITE')
                print(f"  {get_color('BRIGHT_RED')}⚔️  물리 공격력:{get_color('RESET')} {atk_color}{character.physical_attack:3}{get_color('RESET')}")
                
            if hasattr(character, 'magic_attack'):
                # 마법력 색상 계산
                mag_color = get_color('BRIGHT_MAGENTA') if character.magic_attack >= 100 else get_color('MAGENTA') if character.magic_attack >= 80 else get_color('BLUE') if character.magic_attack >= 60 else get_color('WHITE')
                print(f"  {get_color('BRIGHT_MAGENTA')}🔮  마법 공격력:{get_color('RESET')} {mag_color}{character.magic_attack:3}{get_color('RESET')}")
                
            if hasattr(character, 'physical_defense'):
                # 물리 방어력 색상 계산
                pdef_color = get_color('BRIGHT_BLUE') if character.physical_defense >= 100 else get_color('BLUE') if character.physical_defense >= 80 else get_color('CYAN') if character.physical_defense >= 60 else get_color('WHITE')
                print(f"  {get_color('BRIGHT_BLUE')}🛡️  물리 방어력:{get_color('RESET')} {pdef_color}{character.physical_defense:3}{get_color('RESET')}")
                
            if hasattr(character, 'magic_defense'):
                # 마법 방어력 색상 계산
                mdef_color = get_color('BRIGHT_CYAN') if character.magic_defense >= 100 else get_color('CYAN') if character.magic_defense >= 80 else get_color('BLUE') if character.magic_defense >= 60 else get_color('WHITE')
                print(f"  {get_color('BRIGHT_CYAN')}✨  마법 방어력:{get_color('RESET')} {mdef_color}{character.magic_defense:3}{get_color('RESET')}")
                
            if hasattr(character, 'speed'):
                # 속도 색상 계산
                spd_color = get_color('BRIGHT_YELLOW') if character.speed >= 100 else get_color('YELLOW') if character.speed >= 80 else get_color('GREEN') if character.speed >= 60 else get_color('WHITE')
                print(f"  {get_color('BRIGHT_YELLOW')}⚡  속도:{get_color('RESET')}         {spd_color}{character.speed:3}{get_color('RESET')}")
            
            print(f"{get_color('CYAN')}{'─'*50}{get_color('RESET')}")
        
        # 특성 정보 (아군만)
        if is_ally and hasattr(character, 'traits') and character.traits:
            print(f"\n🌟 특성:")
            for trait in character.traits:
                trait_name = trait.name if hasattr(trait, 'name') else str(trait)
                if hasattr(trait, 'effect_type'):
                    if trait.effect_type == "active":
                        if hasattr(trait, 'cooldown') and trait.cooldown > 0:
                            print(f"  {trait_name} (액티브) - 쿨다운: {trait.cooldown}턴")
                        else:
                            print(f"  {trait_name} (액티브) - 사용 가능")
                    else:
                        print(f"  {trait_name} (패시브) - 항상 활성")
                else:
                    print(f"  {trait_name}")
        
        # 직업별 기믹 상태 (아군만)
        if is_ally and hasattr(character, 'character_class'):
            self._show_class_mechanics(character)
        
        # 상태 효과
        if hasattr(character, 'status_effects') and character.status_effects:
            print(f"\n🎭 상태 효과:")
            for effect in character.status_effects:
                effect_name = effect.name if hasattr(effect, 'name') else str(effect)
                duration = effect.duration if hasattr(effect, 'duration') else "?"
                print(f"  {effect_name} ({duration}턴 남음)")
            
            # ⏳ 상태 효과 확인 위해 2초 대기 (엔터로 스킵 가능)
            if hasattr(self, 'gauge_animator'):
                self.gauge_animator._wait_with_skip_option(2.0, "상태 효과 확인")
        
        # 자동 계속 (입력 대기 제거)
        print(f"\n{get_color('YELLOW')}💫 자동으로 계속됩니다... (0.5초){get_color('RESET')}")
        import time
        time.sleep(0.5)
    
    def _show_class_mechanics(self, character: Character):
        """직업별 기믹 상태 표시"""
        class_name = character.character_class
        print(f"\n🎯 {class_name} 기믹 상태:")
        
        # 바드 멜로디 시스템
        if class_name == "바드":
            melody_stacks = getattr(character, 'melody_stacks', 0)
            melody_count = getattr(character, 'melody_count', 0)
            if melody_stacks > 0 or melody_count > 0:
                notes = ["DO", "RE", "MI", "FA", "SOL", "LA", "SI"]
                current_note = notes[min(melody_count - 1, 6)] if melody_count > 0 else "없음"
                print(f"  🎵 멜로디: {current_note} ({melody_count}/7) | 스택: {melody_stacks}")
            else:
                print(f"  🎵 멜로디: 없음 (0/7)")
        
        # 성기사 성스러운 힘
        elif class_name == "성기사":
            holy_count = getattr(character, 'holy_count', 0)
            sanctuary_count = getattr(character, 'sanctuary_count', 0)
            if holy_count > 0 or sanctuary_count > 0:
                print(f"  ✨ HOLY: {holy_count} | 성역: {sanctuary_count}")
            else:
                print(f"  ✨ 성스러운 힘: 비활성")
        
        # 궁수 조준 시스템
        elif class_name == "궁수":
            aim_points = getattr(character, 'aim_points', 0)
            support_fire = getattr(character, 'support_fire_active', False)
            print(f"  🎯 조준: {aim_points}/5")
            if support_fire:
                print(f"  🏹 지원사격: 활성")
        
        # 암살자 그림자 시스템
        elif class_name == "암살자":
            shadow_count = getattr(character, 'shadow_count', 0)
            stealth_mode = getattr(character, 'stealth_mode', False)
            assassination_ready = getattr(character, 'assassination_ready', False)
            print(f"  🌑 그림자: {shadow_count}/5")
            if stealth_mode:
                print(f"  👤 은신: 활성")
            if assassination_ready:
                print(f"  ⚡ 암살 준비: 완료")
        
        # 도적 독 시스템
        elif class_name == "도적":
            poison_stacks = getattr(character, 'poison_stacks', 0)
            venom_power = getattr(character, 'venom_power', 0)
            poison_immunity = getattr(character, 'poison_immunity', False)
            print(f"  ☠️ 독 스택: {poison_stacks}/96 ({venom_power}% 효력)")
            if poison_immunity:
                print(f"  🛡️ 독 면역: 활성")
        
        # 몽크 기(氣) 에너지
        elif class_name == "몽크":
            ki_energy = getattr(character, 'ki_energy', 0)
            combo_count = getattr(character, 'combo_count', 0)
            print(f"  🔥 기 에너지: {ki_energy}/100")
            if combo_count > 0:
                print(f"  👊 콤보: {combo_count}연타")
        
        # 아크메이지 원소 카운트
        elif class_name == "아크메이지":
            fire_count = getattr(character, 'fire_count', 0)
            ice_count = getattr(character, 'ice_count', 0)
            lightning_count = getattr(character, 'lightning_count', 0)
            earth_count = getattr(character, 'earth_count', 0)
            elements = []
            if fire_count > 0:
                elements.append(f"🔥화염:{fire_count}")
            if ice_count > 0:
                elements.append(f"❄️빙결:{ice_count}")
            if lightning_count > 0:
                elements.append(f"⚡번개:{lightning_count}")
            if earth_count > 0:
                elements.append(f"🌍대지:{earth_count}")
            
            if elements:
                print(f"  🔮 원소: {' | '.join(elements)}")
            else:
                print(f"  🔮 원소: 없음")
        
        # 용기사 용의 표식
        elif class_name == "용기사":
            dragon_marks = getattr(character, 'dragon_marks', 0)
            print(f"  🐉 용의 표식: {dragon_marks}/5")
        
        # 네크로맨서 영혼 에너지
        elif class_name == "네크로맨서":
            necro_energy = getattr(character, 'necro_energy', 0)
            soul_power = getattr(character, 'soul_power', 0)
            print(f"  💀 죽음의 힘: {necro_energy}/100")
            if soul_power > 0:
                print(f"  👻 영혼력: {soul_power}")
        
        # 정령술사 정령 유대
        elif class_name == "정령술사":
            spirit_bond = getattr(character, 'spirit_bond', 0)
            print(f"  🌟 정령 유대: {spirit_bond}/100")
        
        # 검성 검기
        elif class_name == "검성":
            sword_aura = getattr(character, 'sword_aura', 0)
            print(f"  ⚔️ 검기: {sword_aura}/2.0")
        
        # 검투사 투기장 경험
        elif class_name == "검투사":
            arena_points = getattr(character, 'arena_points', 0)
            print(f"  🏛️ 투기장 포인트: {arena_points}/100")
        
        # 광전사 분노
        elif class_name == "광전사":
            rage_stacks = getattr(character, 'rage_stacks', 0)
            berserk_mode = getattr(character, 'berserk_mode', False)
            print(f"  💢 분노: {rage_stacks}/100")
            if berserk_mode:
                print(f"  🔴 광폭화: 활성")
        
        # 기계공학자 기계 에너지
        elif class_name == "기계공학자":
            machine_energy = getattr(character, 'machine_energy', 0)
            overcharge = getattr(character, 'overcharge', False)
            print(f"  ⚙️ 기계 에너지: {machine_energy}/100")
            if overcharge:
                print(f"  ⚡ 과충전: 활성")
        
        # 기타 직업들은 기본 메시지
        else:
            print(f"  💫 {class_name}의 특별한 능력이 잠재되어 있습니다...")
    
    def _show_battle_summary(self, current_char: Character, party: List[Character], enemies: List[Character]):
        """전투 현황 요약"""
        print(f"\n{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        print(f"{get_color('BRIGHT_CYAN')}📊 전투 현황 요약{get_color('RESET')}")
        print(f"{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        
        # 아군 요약
        alive_allies = [p for p in party if p.is_alive]
        total_ally_hp = sum(p.current_hp for p in alive_allies)
        total_ally_max_hp = sum(p.max_hp for p in alive_allies)
        total_ally_brave = sum(getattr(p, 'brave_points', 0) for p in alive_allies)
        
        print(f"\n{get_color('BRIGHT_BLUE')}🛡️ 아군 현황:{get_color('RESET')}")
        print(f"  생존자: {len(alive_allies)}/{len(party)}명")
        print(f"  총 HP: {total_ally_hp}/{total_ally_max_hp} ({int(total_ally_hp/total_ally_max_hp*100) if total_ally_max_hp > 0 else 0}%)")
        print(f"  총 BRV: {total_ally_brave}")
        print(f"  HP 공격 가능: {len([p for p in alive_allies if getattr(p, 'brave_points', 0) >= 300])}명")
        
        # 적군 요약
        alive_enemies = [e for e in enemies if e.is_alive]
        total_enemy_hp = sum(e.current_hp for e in alive_enemies)
        total_enemy_max_hp = sum(e.max_hp for e in alive_enemies)
        total_enemy_brave = sum(getattr(e, 'brave_points', 0) for e in alive_enemies)
        
        print(f"\n{get_color('BRIGHT_RED')}⚔️ 적군 현황:{get_color('RESET')}")
        print(f"  생존자: {len(alive_enemies)}명")
        print(f"  총 HP: {total_enemy_hp}/{total_enemy_max_hp} ({int(total_enemy_hp/total_enemy_max_hp*100) if total_enemy_max_hp > 0 else 0}%)")
        print(f"  총 BRV: {total_enemy_brave}")
        print(f"  BREAK 상태: {len([e for e in alive_enemies if hasattr(e, 'is_broken') and e.is_broken])}명")
        
        # 전투 분석
        print(f"\n{get_color('BRIGHT_YELLOW')}📈 전투 분석:{get_color('RESET')}")
        
        ally_advantage = total_ally_hp / max(1, total_enemy_hp)
        if ally_advantage > 1.5:
            print(f"  • 🟢 아군 우세 (HP 비율: {ally_advantage:.1f}:1)")
        elif ally_advantage > 0.8:
            print(f"  • 🟡 균등한 상황 (HP 비율: {ally_advantage:.1f}:1)")
        else:
            print(f"  • 🔴 아군 열세 (HP 비율: {ally_advantage:.1f}:1)")
        
        brave_advantage = total_ally_brave / max(1, total_enemy_brave)
        if brave_advantage > 1.5:
            print(f"  • ⚡ BRV 우세 - 적극적인 HP 공격 추천")
        elif brave_advantage < 0.7:
            print(f"  • 💧 BRV 열세 - 방어적인 플레이 추천")
        else:
            print(f"  • ✨ BRV 균등")
        
        # 어그로 분석 추가
        if self.aggro_system and self.aggro_system.aggro_table:
            print(f"\n{get_color('BRIGHT_MAGENTA')}🎯 어그로 분석:{get_color('RESET')}")
            aggro_status = self.aggro_system.get_all_aggro_status()
            print(aggro_status)
        
        # 자동 계속 (입력 대기 제거)
        print(f"\n{get_color('YELLOW')}💫 자동으로 계속됩니다... (0.5초){get_color('RESET')}")
        import time
        time.sleep(0.5)
    
    def _show_turn_order_prediction(self, all_combatants: List[Character]):
        """턴 순서 예측"""
        print(f"\n{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        print(f"{get_color('BRIGHT_CYAN')}⏰ 턴 순서 예측{get_color('RESET')}")
        print(f"{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}")
        
        # 유효한 전투원만 필터링
        valid_combatants = [c for c in all_combatants if hasattr(c, 'atb_gauge') and c.is_alive]
        
        # ATB 게이지 순으로 정렬
        sorted_by_atb = sorted(valid_combatants, key=lambda x: getattr(x, 'atb_gauge', 0), reverse=True)
        
        print(f"\n🎯 현재 ATB 순서:")
        for i, combatant in enumerate(sorted_by_atb[:8], 1):  # 상위 8명만
            atb_gauge = getattr(combatant, 'atb_gauge', 0)
            is_ally = combatant in [c for c in all_combatants if hasattr(c, 'character_class') and c.character_class != 'Enemy']
            
            # ATB 백분율 계산 (정상적인 0-100% 범위로)
            atb_percent = min(100, int((atb_gauge / self.ATB_READY_THRESHOLD) * 100))
            
            if atb_gauge >= self.ATB_READY_THRESHOLD:
                status = f"{get_color('BRIGHT_YELLOW')}⚡준비완료{get_color('RESET')}"
            elif atb_percent >= 75:
                status = f"{get_color('CYAN')}🔶거의 준비{get_color('RESET')}"
            else:
                status = f"{get_color('BLUE')}⏳대기중{get_color('RESET')}"
            
            # 직업별 아이콘 또는 적 아이콘
            if is_ally:
                character_class = getattr(combatant, 'character_class', '모험가')
                class_icons = {
                    '전사': '⚔️', '아크메이지': '🔮', '궁수': '🏹', '도적': '🗡️',
                    '성기사': '🛡️', '암흑기사': '🌑', '몽크': '👊', '바드': '🎵', 
                    '네크로맨서': '💀', '용기사': '🐉', '검성': '⚡', '정령술사': '🌟', 
                    '암살자': '🥷', '기계공학자': '🔧', '무당': '🔯', '해적': '🏴‍☠️', 
                    '사무라이': '🗾', '드루이드': '🌿', '철학자': '🧠', '시간술사': '⏰', 
                    '연금술사': '⚗️', '검투사': '🏛️', '기사': '🐎', '신관': '✨',
                    '마검사': '🗡️', '차원술사': '🌌', '광전사': '💥'
                }
                side_icon = class_icons.get(character_class, '🎭')
            else:
                # 적 아이콘 (적 종류별로 다르게)
                enemy_name = combatant.name.lower()
                if '고블린' in enemy_name:
                    side_icon = '👹'
                elif '슬라임' in enemy_name:
                    side_icon = '🟢'
                elif '쥐' in enemy_name:
                    side_icon = '🐭'
                elif '오크' in enemy_name:
                    side_icon = '👺'
                elif '스켈레톤' in enemy_name:
                    side_icon = '💀'
                elif '드래곤' in enemy_name:
                    side_icon = '🐲'
                else:
                    side_icon = '👾'
            
            print(f"  {i}. {side_icon} {combatant.name}: {status} ({atb_percent}%)")
        
        # 다음 턴 예측
        print(f"\n🔮 다음 5턴 예측:")
        prediction_combatants = [(c, getattr(c, 'atb_gauge', 0)) for c in valid_combatants]
        
        for turn in range(1, 6):
            # ATB 시뮬레이션
            for i, (combatant, atb) in enumerate(prediction_combatants):
                speed = getattr(combatant, 'speed', 50)
                atb_increment = (speed / 50.0) * 8
                prediction_combatants[i] = (combatant, min(self.ATB_READY_THRESHOLD, atb + atb_increment))
            
            # ATB_READY_THRESHOLD 도달한 캐릭터 찾기
            ready_combatants = [(c, atb) for c, atb in prediction_combatants if atb >= self.ATB_READY_THRESHOLD]
            if ready_combatants:
                # 가장 높은 ATB의 캐릭터
                next_combatant = max(ready_combatants, key=lambda x: x[1])[0]
                is_ally = next_combatant in [c for c in all_combatants if hasattr(c, 'character_class') and c.character_class != 'Enemy']
                
                # 아이콘 설정
                if is_ally:
                    character_class = getattr(next_combatant, 'character_class', '모험가')
                    class_icons = {
                        '전사': '⚔️', '아크메이지': '🔮', '궁수': '🏹', '도적': '🗡️',
                        '성기사': '🛡️', '암흑기사': '🌑', '몽크': '👊', '바드': '🎵', 
                        '네크로맨서': '💀', '용기사': '🐉', '검성': '⚡', '정령술사': '🌟', 
                        '암살자': '🥷', '기계공학자': '🔧', '무당': '🔯', '해적': '🏴‍☠️', 
                        '사무라이': '🗾', '드루이드': '🌿', '철학자': '🧠', '시간술사': '⏰', 
                        '연금술사': '⚗️', '검투사': '🏛️', '기사': '🐎', '신관': '✨',
                        '마검사': '🗡️', '차원술사': '🌌', '광전사': '💥'
                    }
                    side_icon = class_icons.get(character_class, '🎭')
                else:
                    enemy_name = next_combatant.name.lower()
                    if '고블린' in enemy_name:
                        side_icon = '👹'
                    elif '슬라임' in enemy_name:
                        side_icon = '🟢'
                    elif '쥐' in enemy_name:
                        side_icon = '🐭'
                    elif '오크' in enemy_name:
                        side_icon = '👺'
                    elif '스켈레톤' in enemy_name:
                        side_icon = '💀'
                    elif '드래곤' in enemy_name:
                        side_icon = '🐲'
                    else:
                        side_icon = '👾'
                
                print(f"  턴 {turn}: {side_icon} {next_combatant.name}")
                
                # 해당 캐릭터의 ATB를 0으로 리셋
                for i, (c, atb) in enumerate(prediction_combatants):
                    if c == next_combatant:
                        prediction_combatants[i] = (c, 0)
                        break
        
        # 자동 계속 (입력 대기 제거)
        print(f"\n{get_color('YELLOW')}💫 자동으로 계속됩니다... (0.5초){get_color('RESET')}")
        import time
        time.sleep(0.5)
            
    def update_atb_gauges(self, all_combatants: List[Character], show_animation: bool = False):
        """ATB 게이지 업데이트 - 상대적 속도 기반 차등 업데이트 및 캐스팅 체크 (애니메이션 지원)"""
        # ATB 정지 상태 체크
        if self.is_atb_paused():
            return
        
        # 유효한 캐릭터 객체만 필터링
        valid_combatants = []
        for c in all_combatants:
            if hasattr(c, 'name') and hasattr(c, 'is_alive') and hasattr(c, 'atb_gauge'):
                valid_combatants.append(c)
        
        # 파티 정보 저장 (애니메이션에서 사용)
        party = [c for c in valid_combatants if hasattr(c, 'character_class')]  # 아군 구분 (임시)
        self._current_party = party
        
        # 설정 로드
        try:
            from ..config import GameConfig
            config = GameConfig()
            atb_settings = config.ATB_SETTINGS
        except ImportError:
            # 기본 설정
            atb_settings = {
                "animation_enabled": True,
                "animation_fps": 60,  # 60 FPS로 부드럽게
                "update_speed": 1.0,
                "show_percentage": True,
                "smooth_animation": True,
                "frame_delay": 1.0/60  # 60 FPS = 1/60초 간격
            }
        
        current_time = getattr(self, 'battle_time', 0)
        self.battle_time = current_time + 1  # 시간 증가
        
        # 애니메이션이 활성화되고 요청된 경우
        if show_animation and atb_settings.get("animation_enabled", True):
            self._update_atb_with_animation(valid_combatants, atb_settings)
        else:
            self._update_atb_instant(valid_combatants, atb_settings)
    
    def _update_atb_instant(self, all_combatants: List[Character], atb_settings: dict):
        """ATB 즉시 업데이트 (애니메이션 없음) - 상대적 속도 기반 동시 업데이트"""
        
        # ATB 정지 상태 체크
        if self.is_atb_paused():
            return
        
        # 유효한 전투 참여자만 필터링
        alive_combatants = [c for c in all_combatants if not isinstance(c, dict) and c.is_alive and hasattr(c, 'atb_gauge')]
        if not alive_combatants:
            return
        
        # 📊 전투 참여자 전체의 평균 속도 계산
        total_speed = sum(getattr(c, 'speed', 50) for c in alive_combatants)
        avg_speed = total_speed / len(alive_combatants)
        
        # 🏃‍♂️ 상대적 속도 기반 ATB 증가 - 평균 속도 대비 비율로 계산
        base_atb_increase = 30  # ⚡ 원래대로 복원 (40 → 30)

        # 모든 캐릭터의 ATB를 동시에 계산 후 동시에 업데이트
        atb_updates = {}
        casting_completions = []
        
        for combatant in all_combatants:
            # dict 객체 체크
            if isinstance(combatant, dict):
                print(f"⚠️ 경고: ATB 업데이트 중 dict 객체 발견: {combatant}")
                continue
                
            if combatant.is_alive and hasattr(combatant, 'atb_gauge'):
                # 🎯 개별 캐릭터의 속도와 평균 속도 비교로 상대적 ATB 증가 계산
                character_speed = getattr(combatant, 'speed', 50)
                
                # 평균 속도 대비 상대적 비율 계산 (0.5 ~ 2.0 범위로 제한)
                if avg_speed > 0:
                    speed_ratio = character_speed / avg_speed
                    speed_ratio = max(0.5, min(2.0, speed_ratio))  # 너무 극단적이지 않게 제한
                else:
                    speed_ratio = 1.0
                
                # 상대적 속도 기반 ATB 증가량 계산
                atb_increase = int(base_atb_increase * speed_ratio)
                
                # 난이도 기반 ATB 속도 조절 (적과 아군 모두 공평하게)
                if hasattr(self, 'is_player_turn_active') and self.is_player_turn_active:
                    # 플레이어 턴 중에는 난이도 설정에 따른 속도 조절
                    speed_modifier = self._get_turn_speed_modifier()
                    atb_increase = int(atb_increase * speed_modifier)
                    
                    # 첫 번째 호출 시에만 로깅 (너무 많은 로그 방지)
                    if not hasattr(self, '_speed_modifier_logged'):
                        from game.error_logger import log_system
                        log_system("ATB시스템", f"난이도 기반 ATB 속도 조절 적용", {
                            "속도배수": speed_modifier,
                            "기본증가량": base_atb_increase,
                            "조절후증가량": atb_increase
                        })
                        self._speed_modifier_logged = True
                
                # 캐스팅 중인 경우 특별 처리
                if hasattr(combatant, 'is_casting') and combatant.is_casting:
                    cast_time = getattr(combatant, 'casting_cast_time', 250)
                    required_atb = cast_time
                    new_atb = combatant.atb_gauge + atb_increase
                    
                    # 캐스팅 완료 체크
                    if new_atb >= required_atb:
                        casting_completions.append(combatant)
                        new_atb = new_atb - required_atb  # 필요한 ATB만 소모
                else:
                    # 일반 ATB 증가
                    new_atb = combatant.atb_gauge + atb_increase
                
                # ATB 값 범위 보정
                new_atb = max(0, min(self.ATB_MAX, int(round(new_atb))))
                atb_updates[combatant] = new_atb
        
        # 모든 ATB 값을 동시에 업데이트
        for combatant, new_atb in atb_updates.items():
            combatant.atb_gauge = new_atb
            
            # 🎭 강력한 캐스팅 진행도 강제 계산
            if hasattr(combatant, 'is_casting') and combatant.is_casting:
                if hasattr(combatant, 'casting_start_atb') and hasattr(combatant, 'casting_duration'):
                    # 캐스팅 시작점에서 현재까지의 진행도 계산
                    casting_elapsed_atb = new_atb - combatant.casting_start_atb
                    if combatant.casting_duration > 0:
                        casting_progress_ratio = casting_elapsed_atb / combatant.casting_duration
                        combatant.casting_progress = max(0, min(1000, int(casting_progress_ratio * 1000)))
                    else:
                        combatant.casting_progress = 1000  # 즉시 완료
                else:
                    # 폴백: 기본 진행도 설정
                    combatant.casting_progress = 500  # 50% 진행도
        
        # ATB 업데이트 후 화면 상태 갱신 (즉시 업데이트 모드에서도)
        # 화면 갱신은 모든 ATB 업데이트가 완료된 후에만 실행
        # 빈번한 갱신을 방지하기 위해 조건을 더 엄격하게 설정
        if atb_updates and hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
            # 2% 이상의 ATB 변화가 있을 때만 화면 갱신
            significant_changes = False
            for combatant, new_atb in atb_updates.items():
                old_atb = getattr(combatant, '_last_display_atb', 0)
                atb_change_percent = abs(new_atb - old_atb) / self.ATB_MAX * 100
                if atb_change_percent >= 2:  # 2% 이상 변화시에만 갱신
                    significant_changes = True
                    combatant._last_display_atb = new_atb
                    break
            
            if significant_changes:
                # ATB 변화가 있을 때만 필요시 화면 갱신
                pass  # 빠른 갱신을 위해 화면 갱신은 생략
    
    def _get_turn_speed_modifier(self):
        """난이도 설정에 따른 턴 속도 배수 반환"""
        try:
            # config에서 현재 난이도 설정 가져오기
            import config
            game_config = config.GameConfig()
            current_difficulty = getattr(game_config, 'current_difficulty', '보통')
            difficulty_settings = getattr(game_config, 'DIFFICULTY_SETTINGS', {})
            
            if current_difficulty in difficulty_settings:
                return difficulty_settings[current_difficulty].get('player_turn_speed', 0.2)
            else:
                return 0.2  # 기본값 (보통 난이도)
        except Exception as e:
            from game.error_logger import log_error
            log_error("ATB시스템", "난이도 설정 로드 실패", {"오류": str(e)})
            return 0.2  # 기본값
    
    def _update_atb_with_animation(self, all_combatants: List[Character], atb_settings: dict):
        """ATB 애니메이션과 함께 업데이트 - 20FPS로 안정적이고 부드럽게"""
        import time
        import os
        
        speed_multiplier = atb_settings.get("update_speed", 1.0)
        frame_delay = 1.0/20  # 20 FPS로 안정적 업데이트 (240fps → 20fps)
        show_percentage = atb_settings.get("show_percentage", True)
        
        # 상대적 속도 계산을 위한 평균 속도
        alive_combatants = [c for c in all_combatants if not isinstance(c, dict) and c.is_alive and hasattr(c, 'atb_gauge')]
        if not alive_combatants:
            return
        
        total_speed = sum(getattr(c, 'speed', 100) for c in alive_combatants)
        avg_speed = total_speed / len(alive_combatants)
        
        # ATB 게이지 충전 속도 - 속도에 완전 정비례 (단순하고 명확하게) - 4배 적절히!
        base_increase = 1.0  # ⚡ 메인 ATB 증가량만 4배! (0.25 → 1.0)
        
        # 이전 ATB 값들 저장
        previous_atb = {}
        for combatant in alive_combatants:
            if hasattr(combatant, 'atb_gauge'):
                previous_atb[id(combatant)] = combatant.atb_gauge
        
        # ATB 업데이트 계산
        for combatant in all_combatants:
            if isinstance(combatant, dict):
                continue
                
            if combatant.is_alive and hasattr(combatant, 'atb_gauge'):
                # 개별 속도 기반 ATB 증가 계산 (속도에 완전 정비례)
                speed = getattr(combatant, 'speed', 50)
                # 속도가 50인 캐릭터를 기준으로 완전 정비례 (speed 50 = 1.0배, speed 100 = 2.0배)
                speed_multiplier = speed / 50.0
                
                # 기본 required_atb 값 설정
                required_atb = self.ATB_MAX  # 기본값: 최대 ATB (캐스팅 아닐 때)
                
                # 캐스팅 중인 경우 ATB 기반 캐스팅 처리
                if hasattr(combatant, 'is_casting') and combatant.is_casting:
                    cast_time = getattr(combatant, 'casting_cast_time', 250)  # 기본 25% → 250 ATB units
                    
                    # 캐스팅에 필요한 ATB = cast_time (예: 15% 스킬이면 150 ATB)
                    required_atb = cast_time
                    
                    # 캐스팅 속도는 일반 ATB와 동일하게 처리
                    atb_increase = int(base_increase * speed_multiplier)
                    new_atb = min(self.ATB_MAX, combatant.atb_gauge + atb_increase)
                    
                    # ATB 값 즉시 업데이트 (애니메이션 제거)
                    combatant.atb_gauge = new_atb
                    
                    # 캐스팅 완료 체크: required_atb에 도달하면 완료
                    if combatant.atb_gauge >= required_atb:
                        display_atb = min(100, int(combatant.atb_gauge / self.ATB_READY_THRESHOLD * 100))
                        print(f"✨ {combatant.name}의 캐스팅이 완료되었습니다!")
                        self.complete_casting(combatant)
                        # 캐스팅 완료 시 ATB는 required_atb만큼 소모하고 나머지는 유지
                        combatant.atb_gauge = combatant.atb_gauge - required_atb
                    continue
                
                # 일반적인 ATB 게이지 증가 (속도 기반)
                atb_increase = int(base_increase * speed_multiplier)
                
                # 플레이어 턴 중일 때 ATB 증가 속도 조절
                if hasattr(self, 'is_action_executing') and self.is_action_executing:
                    # 행동 실행 중일 때는 ATB 완전 정지
                    atb_increase = 0
                elif hasattr(self, 'is_player_turn_active') and self.is_player_turn_active:
                    # 난이도 설정에서 플레이어 턴 중 속도 배율 가져오기
                    try:
                        from ..config import GameConfig
                        config = GameConfig()
                        current_difficulty = getattr(config, 'current_difficulty', '보통')
                        difficulty_settings = config.DIFFICULTY_SETTINGS.get(current_difficulty, {})
                        player_turn_speed = difficulty_settings.get("player_turn_speed", 0.3)
                        atb_increase = int(atb_increase * player_turn_speed)
                    except:
                        atb_increase = int(atb_increase * 0.3)  # 기본 0.3배 속도
                
                new_atb = min(self.ATB_MAX, combatant.atb_gauge + atb_increase)
                
                # ATB 값 즉시 업데이트 (애니메이션 제거)
                combatant.atb_gauge = new_atb
    
    def _animate_atb_change(self, character: Character, old_atb: int, new_atb: int, frame_delay: float, show_percentage: bool, is_ally: bool = None):
        """ATB 변화를 즉시 표시 - 딜레이 완전 제거"""
        from .buffered_display import get_buffered_display
        
        if old_atb == new_atb:
            return
        
        # 애니메이션 완전 제거 - 즉시 최종 값으로 업데이트
        current_atb = new_atb
        
        display = get_buffered_display()
        
        # 캐릭터 ATB 값 즉시 업데이트
        character.atb_gauge = int(current_atb)
        
        # 전체 전투 상태를 버퍼링 시스템으로 즉시 업데이트
        if hasattr(self, '_current_party') and hasattr(self, '_current_enemies'):
            current_char = getattr(self, '_current_character', character)
            
            # 버퍼 기반 업데이트 (깜빡임 방지)
            display.clear_buffer()
            
            # 파티와 적군 상태를 버퍼에 추가
            from .optimized_gauge_system import OptimizedGaugeSystem
            gauge_system = OptimizedGaugeSystem()
            party_status = gauge_system.show_optimized_party_status(self._current_party, current_char)
            enemy_status = gauge_system.show_optimized_enemy_status(self._current_enemies)
            
            for line in party_status.split('\n'):
                if line.strip():
                    display.add_line(line)
            
            for line in enemy_status.split('\n'):
                if line.strip():
                    display.add_line(line)
            
            # 즉시 렌더링 (딜레이 없음)
            display.render_optimized()
        
        # 딜레이 완전 제거 - 즉시 완료
    def _create_atb_bar(self, atb_gauge: int, show_percentage: bool = True, is_ally: bool = None, character: Character = None) -> str:
        """ATB 게이지 바 생성 (아군/적군 구분 지원) - 아름다운 게이지 사용"""
        
        # 정확한 백분율 계산
        display_atb = min(100, int(atb_gauge / self.ATB_READY_THRESHOLD * 100))
        
        # 캐릭터 상태에 따른 캐스팅 여부 확인
        is_casting = False
        if character and hasattr(character, 'is_casting') and character.is_casting:
            is_casting = True
        
        # 아름다운 ATB 게이지 생성 (길이 15로 조정)
        atb_bar = self.create_beautiful_atb_gauge(display_atb, 100, 15, is_casting)
        
        return atb_bar
    
    def _show_realtime_atb_status(self, party: List[Character], enemies: List[Character]):
        """실시간 ATB 상태 표시 (3초간) - 화면 겹침 방지 및 깜빡임 개선"""
        import time
        import os
        
        all_combatants = party + enemies
        start_time = time.time()
        last_update_time = 0
        update_interval = 0.2  # 200ms마다 업데이트 (깜빡임 줄이기)
        
        try:
            # 설정 로드
            from ..config import GameConfig
            config = GameConfig()
            atb_settings = config.ATB_SETTINGS
        except ImportError:
            atb_settings = {
                "animation_enabled": True,
                "show_percentage": True,
                "frame_delay": 0.2  # 더 긴 딜레이로 깜빡임 줄이기
            }
        
        # 파워셸 최적화 초기 화면 클리어 (한 번만)
        try:
            if os.name == 'nt':  # Windows/파워셸
                print("\033[2J\033[H", end="", flush=True)  # ANSI 클리어가 더 부드러움
            else:
                os.system('clear')
        except Exception:
            print("\n" * 3)  # 폴백
        
        # 안정적인 디스플레이 시스템 사용
        frame_content = ""
        
        while time.time() - start_time < 3.0:  # 3초간 실행
            current_time = time.time()
            
            # 업데이트 간격 체크 (깜빡임 줄이기) - 더 느린 업데이트
            if current_time - last_update_time < 0.1:  # 100ms로 늘림 (깜빡임 방지)
                time_module.sleep(0.05)  # 50ms 대기
                continue
                
            last_update_time = current_time
            
            # 새 프레임 내용 생성
            new_frame_content = ""
            
            # 헤더 생성
            new_frame_content += f"\n{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}\n"
            new_frame_content += f"{get_color('BRIGHT_WHITE')}⏳ 실시간 ATB 상태 - Dawn of Stellar{get_color('RESET')}\n"
            new_frame_content += f"{get_color('BRIGHT_CYAN')}{'='*80}{get_color('RESET')}\n"
            
            # 아군 표시
            new_frame_content += f"{get_color('BRIGHT_BLUE')}👥 아군{get_color('RESET')}\n"
            new_frame_content += f"{get_color('BLUE')}{'─'*80}{get_color('RESET')}\n"
            for combatant in party:
                if not combatant.is_alive:
                    continue
                    
                atb_gauge = getattr(combatant, 'atb_gauge', 0)
                atb_bar = self._create_atb_bar(atb_gauge, atb_settings.get("show_percentage", True), is_ally=True, character=combatant)
                
                # HP/MP/BRV 정보
                hp_ratio = combatant.current_hp / combatant.max_hp if combatant.max_hp > 0 else 0
                mp_ratio = combatant.current_mp / max(1, combatant.max_mp) if combatant.max_mp > 0 else 0
                brave = getattr(combatant, 'brave_points', 0)
                
                # HP 색상
                if hp_ratio > 0.7:
                    hp_color = get_color('BRIGHT_GREEN')
                elif hp_ratio > 0.4:
                    hp_color = get_color('YELLOW')
                elif hp_ratio > 0.15:
                    hp_color = get_color('BRIGHT_RED')
                else:
                    hp_color = get_color('RED')
                
                # MP 색상
                if mp_ratio > 0.7:
                    mp_color = get_color('BRIGHT_CYAN')
                elif mp_ratio > 0.3:
                    mp_color = get_color('CYAN')
                else:
                    mp_color = get_color('BLUE')
                
                # 상태 정보
                casting_status = ""
                if hasattr(combatant, 'is_casting') and combatant.is_casting:
                    skill_name = getattr(combatant, 'casting_skill_name', '알 수 없는 스킬')
                    casting_status = f" {get_color('BRIGHT_MAGENTA')}[CASTING: {skill_name}]{get_color('RESET')}"
                
                break_status = ""
                if hasattr(combatant, 'is_broken_state') and combatant.is_broken_state:
                    break_status = f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                
                # 새로운 컴팩트 캐릭터 상태 표시
                from .optimized_gauge_system import OptimizedGaugeSystem
                from .shadow_system import get_shadow_system
                
                shadow_system = get_shadow_system()
                compact_status = OptimizedGaugeSystem.create_compact_character_status(combatant, shadow_system)
                new_frame_content += compact_status + "\n"
                
                # 상태이상 표시
                status_effects = ""
                if hasattr(combatant, 'is_stunned') and combatant.is_stunned:
                    status_effects += f" {get_color('BRIGHT_BLACK')}[기절]{get_color('RESET')}"
                if hasattr(combatant, 'temp_speed_penalty') and getattr(combatant, 'temp_speed_penalty', 0) > 0:
                    status_effects += f" {get_color('BLUE')}[둔화]{get_color('RESET')}"
                
                # 독 상태 표시 (누적 정보 포함)
                if hasattr(combatant, 'status_effects') and combatant.status_effects:
                    poison_info = None
                    for effect in combatant.status_effects:
                        if hasattr(effect, 'type') and effect.type == "poison":
                            poison_info = effect
                            break
                    if poison_info:
                        poison_dmg = int(poison_info.intensity * 10)  # 예상 독 피해
                        status_effects += f" {get_color('GREEN')}[독:{poison_dmg} x{poison_info.duration}턴]{get_color('RESET')}"
                
                if status_effects:
                    new_frame_content += f"    상태: {status_effects}\n"
                new_frame_content += "\n"
            
            new_frame_content += f"{get_color('GREEN')}{'─'*80}{get_color('RESET')}\n"
            
            # 적군 표시
            new_frame_content += f"{get_color('BRIGHT_RED')}⚔️ 적군{get_color('RESET')}\n"
            new_frame_content += f"{get_color('RED')}{'─'*80}{get_color('RESET')}\n"
            for combatant in enemies:
                if not combatant.is_alive:
                    continue
                
                # 새로운 컴팩트 적군 상태 표시
                compact_status = OptimizedGaugeSystem.create_compact_character_status(combatant, shadow_system)
                new_frame_content += compact_status + "\n"
                
                # 상태이상 표시
                status_effects = ""
                if hasattr(combatant, 'is_stunned') and combatant.is_stunned:
                    status_effects += f" {get_color('BRIGHT_BLACK')}[기절]{get_color('RESET')}"
                if hasattr(combatant, 'temp_speed_penalty') and getattr(combatant, 'temp_speed_penalty', 0) > 0:
                    status_effects += f" {get_color('BLUE')}[둔화]{get_color('RESET')}"
                if hasattr(combatant, 'is_broken') and combatant.is_broken:
                    status_effects += f" {get_color('BRIGHT_RED')}[BREAK]{get_color('RESET')}"
                if hasattr(combatant, 'is_casting') and combatant.is_casting:
                    skill_name = getattr(combatant, 'casting_skill_name', '알 수 없는 스킬')
                    status_effects += f" {get_color('BRIGHT_MAGENTA')}[CASTING: {skill_name}]{get_color('RESET')}"
                
                # 독 상태 표시 (누적 정보 포함) - 적군용
                if hasattr(combatant, 'status_effects') and combatant.status_effects:
                    poison_info = None
                    for effect in combatant.status_effects:
                        if hasattr(effect, 'type') and effect.type == "poison":
                            poison_info = effect
                            break
                    if poison_info:
                        poison_dmg = int(poison_info.intensity * 10)  # 예상 독 피해
                        total_poison_dmg = poison_dmg * poison_info.duration  # 총 피해
                        status_effects += f" {get_color('GREEN')}[☠️독:{poison_dmg} x{poison_info.duration}턴 (총:{total_poison_dmg})]{get_color('RESET')}"
                
                if status_effects:
                    new_frame_content += f"    상태: {status_effects}\n"
                new_frame_content += "\n"
                
            new_frame_content += f"{get_color('BRIGHT_CYAN')}{'═'*80}{get_color('RESET')}\n"
            new_frame_content += f"{get_color('YELLOW')}ESC를 눌러 종료...{get_color('RESET')}\n"
            
            # 프레임이 변경되었을 때만 화면 업데이트
            if new_frame_content != frame_content:
                frame_content = new_frame_content
                # 커서를 맨 위로 이동 (화면 클리어 대신 사용)
                print('\033[H', end='', flush=True)
                print(frame_content, end='', flush=True)
            
            # 키 입력 체크 (논블로킹)
            try:
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\x1b':  # ESC 키
                        break
            except ImportError:
                # Unix 시스템에서는 select 사용
                import select
                import sys
                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1)
                    if key == '\x1b':  # ESC 키
                        break
            
            # ATB 업데이트 제거 (실시간 상태에서는 현재 상태만 표시)
            # self.update_atb_gauges(all_combatants, show_animation=False)  # 제거됨
            
            time_module.sleep(atb_settings.get("frame_delay", 0.2))  # 200ms 딜레이로 변경
        
        print(f"\n{get_color('BRIGHT_GREEN')}실시간 ATB 상태 표시 종료{get_color('RESET')}")
        # 자동 계속 (입력 대기 제거)
        print(f"{get_color('YELLOW')}💫 자동으로 계속됩니다... (0.5초){get_color('RESET')}")
        import time
        time.sleep(0.5)
        
        # 파워셸 최적화 화면 클리어 (부드러운 전환)
        try:
            if os.name == 'nt':  # Windows/파워셸
                print("\033[2J\033[H", end="", flush=True)  # 부드러운 ANSI 클리어
            else:
                os.system('clear')
        except Exception:
            print("\n" * 5)  # 폴백: 스크롤
        
        # 출력 버퍼 플러시
        import sys
        sys.stdout.flush()
                
    def show_atb_status(self, all_combatants: List[Character]):
        """현재 ATB 상태 표시"""
        print(f"\n{get_color('CYAN')}⏱️ ATB 상태:{get_color('RESET')}")
        
        # dict 객체 필터링 및 유효한 combatant만 선택
        valid_combatants = []
        for c in all_combatants:
            if isinstance(c, dict):
                print(f"⚠️ 경고: dict 객체 발견, 건너뜀: {c}")
                continue
            if c.is_alive and hasattr(c, 'atb_gauge'):
                valid_combatants.append(c)
        
        # ATB 순서대로 정렬
        sorted_combatants = sorted(
            valid_combatants, 
            key=lambda x: getattr(x, 'atb_gauge', 0), 
            reverse=True
        )
        
        for i, combatant in enumerate(sorted_combatants[:5]):  # 상위 5명만 표시
            is_enemy = hasattr(combatant, 'is_enemy')
            name_color = get_color('BRIGHT_RED') if is_enemy else get_color('BRIGHT_BLUE')
            
            # 캐스팅 상태 체크
            casting_info = ""
            if hasattr(combatant, 'is_casting') and combatant.is_casting:
                if hasattr(combatant, 'get_casting_progress'):
                    progress = combatant.get_casting_progress(getattr(self, 'battle_time', 0))
                else:
                    progress = 0.5  # 기본값
                skill_name = getattr(combatant, 'casting_skill', {}).get('name', '스킬')
                casting_info = f" 🔮 {skill_name}: [{progress*100:.0f}%]"
                
            atb_gauge = int(getattr(combatant, 'atb_gauge', 0))
            # 디스플레이용으로 100 스케일로 변환 (정확한 백분율 계산)
            display_atb = min(100, int(atb_gauge / self.ATB_READY_THRESHOLD * 100))
            if atb_gauge >= self.ATB_READY_THRESHOLD:
                bar = f"{get_color('BRIGHT_CYAN')}{'█'*10}{get_color('RESET')}"
                status = f"{get_color('BRIGHT_CYAN')}⚡READY{get_color('RESET')}"
            else:
                filled = int(min(10, max(0, display_atb / 10)))  # 0-10 범위로 제한
                bar = f"{get_color('CYAN')}{'█'*filled}{get_color('BRIGHT_BLACK')}{'░'*(10-filled)}{get_color('RESET')}"
                status = f"{get_color('CYAN')}{display_atb:3}%{get_color('RESET')}"  # 정확한 디스플레이 ATB 값 사용
            
            rank = f"{i+1}."
            print(f"  {rank:3} {name_color}{combatant.name:12}{get_color('RESET')} [{bar}]   {status}{casting_info}")
        
        print()
                
    def get_action_order(self, all_combatants: List[Character]) -> List[Character]:
        """행동 순서 결정 - 공정한 우선순위 기반 단일 선택"""
        # 유효한 캐릭터 객체만 필터링
        valid_combatants = []
        for c in all_combatants:
            # 캐릭터 객체 검증: name 속성과 is_alive 속성이 있어야 함
            if hasattr(c, 'name') and hasattr(c, 'is_alive') and hasattr(c, 'atb_gauge'):
                valid_combatants.append(c)
            else:
                # StatusManager 같은 잘못된 객체 감지
                print(f"⚠️ 경고: 잘못된 객체가 전투 리스트에 포함됨: {type(c).__name__}")
        
        # 취소 직후의 짧은 쿨다운 동안은 선택 대상에서 제외
        now_ts = time_module.time()
        def not_in_cooldown(c):
            cid = id(c)
            # 안전한 속성 접근
            cancel_cooldown_dict = getattr(self, '_cancel_cooldown_until', {})
            until = cancel_cooldown_dict.get(cid, 0)
            return now_ts >= until
        ready_combatants = [c for c in valid_combatants if c.is_alive and c.atb_gauge >= self.ATB_READY_THRESHOLD and not_in_cooldown(c)]
        
        if not ready_combatants:
            return []
        
        # ATB가 100% 이상인 캐릭터 중 우선순위 결정 (10000 스케일)
        # 1. ATB 게이지가 더 높은 캐릭터 (더 중요한 가중치)
        # 2. 속도가 더 빠른 캐릭터
        # 3. 무작위 (동점인 경우 - 아군/적군 편향 방지)
        def priority_key(combatant):
            # ATB 게이지를 1000배로 가중치를 높여서 주요 우선순위로 만듦
            atb_weight = combatant.atb_gauge * 1000
            speed_weight = getattr(combatant, 'speed', 50)
            # 완전한 무작위로 아군/적군 편향 제거
            random_tiebreaker = random.random() * 100
            return (atb_weight, speed_weight, random_tiebreaker)
        
        # 가장 높은 우선순위 캐릭터 선택
        fastest = max(ready_combatants, key=priority_key)
        
        # 선택된 캐릭터 반환 (디버그 출력 제거로 화면 안정성 향상)
        return [fastest]
        
    def check_battle_end(self, party: List[Character], enemies: List[Character]) -> bool:
        """전투 종료 조건 확인"""
        party_alive = any(p.is_alive for p in party)
        enemies_alive = any(e.is_alive for e in enemies)
        
        battle_ended = not party_alive or not enemies_alive
        
        # 디버깅 로그 추가
        log_debug("전투종료체크", f"전투 종료 조건 체크", {
            "파티생존": party_alive,
            "적생존": enemies_alive,
            "전투종료": battle_ended,
            "파티수": len(party),
            "적수": len(enemies),
            "파티상태": [f"{p.name}({p.is_alive})" for p in party],
            "적상태": [f"{e.name}({e.is_alive})" for e in enemies]
        })
        
        # 전투가 종료되면 모든 캐릭터의 캐스팅 중단
        if battle_ended:
            log_debug("전투종료", "전투 종료로 인한 캐스팅 중단", {})
            self._clear_all_casting(party + enemies)
        
        return battle_ended
        
    def determine_winner(self, party: List[Character], enemies: List[Character]) -> bool:
        """승부 결정 - 비주얼 이펙트 포함"""
        party_alive = any(p.is_alive for p in party)
        
        # 전투 종료 처리 - 전투 상태 비활성화
        from .character import set_combat_active
        set_combat_active(False)
        
        # 게이지 애니메이터 전투 모드 해제
        if hasattr(self, 'gauge_animator'):
            self.gauge_animator.set_combat_mode(False)
        
        if party_alive:
            # 🎵 승리 BGM 재생 (조용히)
            try:
                if BGMType and get_audio_manager:
                    audio_mgr = get_audio_manager()
                    if audio_mgr:
                        audio_mgr.play_bgm(BGMType.VICTORY)
                        # 승리 BGM 재생 메시지 제거 (깔끔한 출력을 위해)
                    # else: 조용히 실패 처리
            except Exception as e:
                # 오디오 오류는 조용히 처리
                pass
            
            # 🎯 승리 처리 전 모든 애니메이션 완료 대기
            gauge_animator = get_gauge_animator()
            print(f"\n{get_color('CYAN')}⏳ 전투 결과 정산 중...{get_color('RESET')}")
            
            # 진행 중인 애니메이션이 있다면 완료까지 대기
            while gauge_animator.is_processing:
                time_module.sleep(0.1)
            
            # 추가 대기 시간 (사용자가 최종 결과를 확인할 수 있도록)
            time_module.sleep(1.0)
            
            # 승리 이펙트
            print(f"\n{get_color('BRIGHT_GREEN')}{'='*50}")
            print(f"🎉 승리! 🎉")
            print(f"{'='*50}{get_color('RESET')}")
            
            # 승리 후 일시정지 - 사용자가 결과를 확인할 시간
            print(f"\n{get_color('BRIGHT_YELLOW')}전투에서 승리했습니다!{get_color('RESET')}")
            
            # 식재료 드롭 처리
            try:
                from game.cooking_system import get_cooking_system
                cooking = get_cooking_system()
                
                # 적들로부터 식재료 드롭
                for enemy in enemies:
                    if hasattr(enemy, 'hp') and enemy.hp <= 0:  # 죽은 적만
                        enemy_level = getattr(enemy, 'level', 1)
                        dropped_ingredients = cooking.process_enemy_defeat_drops(enemy.name, enemy_level)
                        if dropped_ingredients:
                            cooking.show_ingredient_drops(dropped_ingredients, enemy.name)
                            
            except ImportError:
                pass  # 요리 시스템이 없으면 무시
            
            # 입력 버퍼 클리어
            import sys
            if hasattr(sys.stdin, 'flush'):
                sys.stdin.flush()
            
            # Windows에서 입력 버퍼 클리어
            try:
                import msvcrt
                while msvcrt.kbhit():
                    msvcrt.getch()
            except ImportError:
                pass
            
            # 승리 후 자동 계속 (입력 대기 제거)
            print(f"{get_color('YELLOW')}💫 자동으로 계속됩니다... (1초){get_color('RESET')}")
            time_module.sleep(1.0)  # 1초 대기 후 자동 계속
            
            # 승리 후 입력 버퍼 클리어
            if hasattr(self, 'keyboard') and self.keyboard:
                self.keyboard.clear_input_buffer()
            
        else:
            # 🎯 패배 처리 전 모든 애니메이션 완료 대기
            gauge_animator = get_gauge_animator()
            print(f"\n{get_color('CYAN')}⏳ 전투 결과 정산 중...{get_color('RESET')}")
            
            # 진행 중인 애니메이션이 있다면 완료까지 대기
            while gauge_animator.is_processing:
                time_module.sleep(0.1)
            
            # 추가 대기 시간 (사용자가 최종 결과를 확인할 수 있도록)
            time_module.sleep(1.0)
            
            # 패배 이펙트  
            print(f"\n{get_color('BRIGHT_RED')}{'='*50}")
            print(f"💀 패배... 💀")
            print(f"{'='*50}{get_color('RESET')}")
            
            # 패배 후 일시정지 - 사용자가 결과를 확인할 시간
            print(f"\n{get_color('BRIGHT_RED')}전투에서 패배했습니다...{get_color('RESET')}")
            
            # 입력 버퍼 클리어
            import sys
            if hasattr(sys.stdin, 'flush'):
                sys.stdin.flush()
            
            # Windows에서 입력 버퍼 클리어
            try:
                import msvcrt
                while msvcrt.kbhit():
                    msvcrt.getch()
            except ImportError:
                pass
            
            # 패배 후 자동 계속 (입력 대기 제거)
            print(f"{get_color('RED')}💀 자동으로 계속됩니다... (2초){get_color('RESET')}")
            time_module.sleep(2.0)  # 2초 대기 후 자동 계속
            
            # 패배 후 입력 버퍼 클리어
            if hasattr(self, 'keyboard') and self.keyboard:
                self.keyboard.clear_input_buffer()
            
        return party_alive
    
    def _is_ally(self, caster, target):
        """시전자와 대상이 같은 편인지 확인"""
        # 둘 다 파티원인지 확인
        if (hasattr(self, '_current_party') and 
            caster in self._current_party and target in self._current_party):
            return True
        
        # 둘 다 적인지 확인
        if (hasattr(self, '_current_enemies') and 
            caster in self._current_enemies and target in self._current_enemies):
            return True
        
        # 기본적으로 적이라고 가정
        return False
    
    def _apply_skill_effects(self, skill, caster, targets):
        """스킬 효과 적용 - New Skill System 호환 + 그림자 시스템 통합"""
        from .new_skill_system import SkillType
        
        skill_type = skill.get("type", SkillType.BRV_ATTACK)
        skill_name = skill.get("name", "알 수 없는 스킬")
        
        print(f"🎯 스킬 '{skill_name}' 효과 적용 중...")
        
        # 🌑 암살자인지 확인하고 그림자 시스템 적용
        is_assassin = getattr(caster, 'character_class', '') == '암살자'
        shadow_results = None
        
        for target in targets:
            base_damage = 0  # 기본 피해량 저장용
            is_magic_skill = skill.get("sfx") == "magic_cast"  # 마법 스킬 여부 판단
            
            if skill_type == SkillType.BRV_ATTACK:
                # Brave 공격 - BRV 데미지
                brv_power = skill.get("brv_power", 100)
                damage = self._calculate_brv_damage(skill, caster, target, brv_power)
                base_damage = damage
                
                # 🛡️ 전사 자세 보너스 적용
                if WARRIOR_SYSTEM_AVAILABLE and (caster.character_class == "전사" or "전사" in caster.character_class):
                    try:
                        warrior_system = get_warrior_system()
                        skill_type_for_bonus = "skill" if is_magic_skill else "physical"
                        damage = warrior_system.apply_stance_bonuses(caster, damage, skill_type_for_bonus)
                    except Exception as e:
                        print(f"⚠️ 전사 자세 보너스 적용 실패: {e}")
                
                # 🌑 그림자 시스템 적용 (암살자만)
                if is_assassin and self.shadow_system:
                    final_damage, shadow_results = self.shadow_system.process_skill_shadow_effects(
                        caster, skill, damage
                    )
                    damage = final_damage
                
                # BRV 데미지 적용
                old_brv = target.brave_points
                target.brave_points -= damage
                target.brave_points = max(0, target.brave_points)

                # 적군인지 확인하여 표시량 조정
                target_is_enemy = hasattr(target, 'character_class') and target.character_class == 'Enemy'
                target_brv_display = target.brave_points
                old_brv_display = old_brv
                damage_display = damage
                
                print(f"⚡ {target.name}의 BRV: {old_brv_display} → {target_brv_display} (-{damage_display})")
                
                # 무모한 돌격의 특수 효과: 시전자 BRV 증가
                if "무모한 돌격" in skill_name:
                    brv_gain = int(damage * 0.5)  # 가한 데미지의 50%만큼 BRV 증가
                    old_caster_brv = caster.brave_points
                    caster.brave_points += brv_gain
                    
                    # 시전자가 적군인지 확인하여 표시량 조정
                    caster_is_enemy = hasattr(caster, 'character_class') and caster.character_class == 'Enemy'
                    caster_brv_display = caster.brave_points
                    old_caster_brv_display = old_caster_brv
                    brv_gain_display = brv_gain // 90 if caster_is_enemy else brv_gain // 10
                    
                    print(f"💪 {caster.name}의 BRV: {old_caster_brv_display} → {caster_brv_display} (+{brv_gain_display}) [무모한 돌격 효과]")
                            
                # BREAK 체크
                if target.brave_points <= 0 and hasattr(target, 'apply_break_if_needed'):
                    if target.apply_break_if_needed():
                        print(f"💥 {target.name}이(가) BREAK 상태가 되었습니다!")
                
            elif skill_type == SkillType.HP_ATTACK:
                # HP 공격 - HP 데미지
                hp_power = skill.get("hp_power", 120)
                damage = self._calculate_hp_damage_from_skill(skill, caster, target, hp_power)
                base_damage = damage
                
                # 🛡️ 전사 자세 보너스 적용
                if WARRIOR_SYSTEM_AVAILABLE and (caster.character_class == "전사" or "전사" in caster.character_class):
                    try:
                        warrior_system = get_warrior_system()
                        skill_type_for_bonus = "skill" if is_magic_skill else "physical"
                        damage = warrior_system.apply_stance_bonuses(caster, damage, skill_type_for_bonus)
                    except Exception as e:
                        print(f"⚠️ 전사 자세 보너스 적용 실패: {e}")
                
                # 🌑 그림자 시스템 적용 (암살자만)
                if is_assassin and self.shadow_system:
                    final_damage, shadow_results = self.shadow_system.process_skill_shadow_effects(
                        caster, skill, damage
                    )
                    damage = final_damage
                
                actual_damage = target.take_damage(damage)
                
            elif skill_type == SkillType.BRV_HP_ATTACK:
                # BRV + HP 복합 공격
                brv_power = skill.get("brv_power", 80)
                hp_power = skill.get("hp_power", 80)
                
                # BRV 데미지
                brv_damage = self._calculate_brv_damage(skill, caster, target, brv_power)
                
                # 🛡️ 전사 자세 보너스 적용 (BRV 데미지)
                if WARRIOR_SYSTEM_AVAILABLE and (caster.character_class == "전사" or "전사" in caster.character_class):
                    try:
                        warrior_system = get_warrior_system()
                        skill_type_for_bonus = "skill" if is_magic_skill else "physical"
                        brv_damage = warrior_system.apply_stance_bonuses(caster, brv_damage, skill_type_for_bonus)
                    except Exception as e:
                        print(f"⚠️ 전사 자세 보너스 적용 실패: {e}")
                
                old_brv = target.brave_points
                target.brave_points -= brv_damage
                target.brave_points = max(0, target.brave_points)
                print(f"⚡ {target.name}의 BRV: {old_brv} → {target.brave_points} (-{brv_damage})")
                
                # HP 데미지
                hp_damage = self._calculate_hp_damage_from_skill(skill, caster, target, hp_power)
                
                # 🛡️ 전사 자세 보너스 적용 (HP 데미지)
                if WARRIOR_SYSTEM_AVAILABLE and (caster.character_class == "전사" or "전사" in caster.character_class):
                    try:
                        warrior_system = get_warrior_system()
                        skill_type_for_bonus = "skill" if is_magic_skill else "physical"
                        hp_damage = warrior_system.apply_stance_bonuses(caster, hp_damage, skill_type_for_bonus)
                    except Exception as e:
                        print(f"⚠️ 전사 자세 보너스 적용 실패: {e}")
                
                actual_damage = target.take_damage(hp_damage)
                
            elif skill_type == SkillType.HEAL:
                # 치유 - 아군만 대상으로 함
                if self._is_ally(caster, target):
                    heal_amount = self._calculate_heal_amount(skill, caster)
                    actual_heal = target.heal(heal_amount)
                    print(f"💚 {target.name}이(가) {actual_heal} HP 회복!")
                else:
                    # 적에게는 치유 효과 적용하지 않음
                    print(f"🚫 {target.name}은(는) 적이므로 치유되지 않습니다.")
                
            elif skill_type == SkillType.BUFF:
                # 버프 적용
                self._apply_skill_buff(skill, target)
                print(f"✨ {target.name}에게 버프 적용!")
                
                # ⏳ 버프 효과 확인 위해 2초 대기 (엔터로 스킵 가능)
                if hasattr(self, 'gauge_animator'):
                    self.gauge_animator._wait_with_skip_option(2.0, "버프 효과 확인")
                
            elif skill_type == SkillType.DEBUFF:
                # 디버프 적용
                self._apply_skill_debuff(skill, target)
                print(f"💀 {target.name}에게 디버프 적용!")
                
                # ⏳ 디버프 효과 확인 위해 2초 대기 (엔터로 스킵 가능)
                if hasattr(self, 'gauge_animator'):
                    self.gauge_animator._wait_with_skip_option(2.0, "디버프 효과 확인")
            
            elif skill_type == SkillType.SPECIAL or skill_type == SkillType.ULTIMATE:
                # 특수/궁극기 스킬
                self._apply_special_skill(skill, caster, target)
        
        # 💫 Special Effects 처리 (모든 스킬 타입에 대해)
        special_effects = skill.get("special_effects", [])
        if special_effects:
            # print(f"🌟 스킬 '{skill_name}' 특수 효과 실행 중...")
            try:
                # New Skill System의 special effects 실행
                from .new_skill_system import skill_system
                if hasattr(skill_system, 'execute_special_effects'):
                    skill_system.execute_special_effects(special_effects, caster, skill, targets)
                else:
                    # 폴백: 직접 특수 효과 실행
                    self._execute_special_effects(special_effects, caster, skill, targets)
            except Exception as e:
                # 특수 효과 실행 오류를 로그에 기록
                log_effect_error("특수효과 실행", f"스킬 '{skill.get('name', 'Unknown')}' 특수효과 실행 중 오류", e)
                # 조용하게 폴백: 직접 특수 효과 실행
                self._execute_special_effects(special_effects, caster, skill, targets)
                
    def _calculate_brv_damage(self, skill, caster, target, brv_power):
        """🔥 BRV 데미지 계산 - 통합 데미지 시스템 사용"""
        
        # 회피 체크 먼저 수행
        dodge_result = self._check_dodge_attempt(caster, target)
        if dodge_result.get("is_dodged", False):
            return 0
        
        try:
            # 🎯 통합 데미지 시스템 우선 사용 (기존 시스템보다 우선)
            from .unified_damage_system import calculate_brv_damage
            
            # 스킬 정보 변환 (CharacterTrait 객체 처리)
            if hasattr(skill, '__dict__'):
                # CharacterTrait 등의 객체인 경우
                skill_name = getattr(skill, 'name', "기본 공격")
                damage_type = getattr(skill, 'damage_type', "physical")
                element = getattr(skill, 'element', "none")
            elif isinstance(skill, dict):
                # 딕셔너리인 경우
                skill_name = skill.get("name", "기본 공격")
                damage_type = skill.get("damage_type", "physical")
                element = skill.get("element", "none")
            else:
                # 기타 경우
                skill_name = "기본 공격"
                damage_type = "physical"
                element = "none"
            
            unified_skill = {
                "name": skill_name,
                "brv_power": brv_power,
                "damage_type": damage_type,
                "element": element
            }
            
            # 통합 시스템으로 데미지 계산 (우선 사용)
            result = calculate_brv_damage(caster, target, unified_skill)
            final_damage = result.final_damage
            
            # 구버전 로그 제거 - 통합 데미지 시스템에서 이쁜 로그 출력
            return final_damage
            
        except Exception as e:
            print(f"⚠️ 통합 데미지 시스템 오류, 기존 시스템 사용: {e}")
            # 폴백: 기존 계산 시스템
            caster_attack = getattr(caster, 'physical_attack', 50)
            target_defense = getattr(target, 'physical_defense', 50)
            simple_damage = max(1, int((caster_attack - target_defense * 0.5) * (brv_power / 100.0) * 0.1))
            print(f"⚠️ 폴백 계산 사용: {simple_damage}")
            return simple_damage
    
    def _check_dodge_attempt(self, attacker, target):
        """회피 시도 체크 및 결과 반환"""
        attacker_speed = getattr(attacker, 'speed', 100)
        target_speed = getattr(target, 'speed', 100)
        
        # 회피 확률 계산
        dodge_chance = max(0, min(0.3, (target_speed - attacker_speed) / attacker_speed * 0.2))
        
        import random
        is_dodged = random.random() < dodge_chance
        
        return {
            "is_dodged": is_dodged,
            "dodge_chance": dodge_chance,
            "attacker_speed": attacker_speed,
            "target_speed": target_speed
        }
    
    def _calculate_hp_damage_from_skill(self, skill, caster, target, hp_power):
        """🔥 스킬의 HP 데미지 계산 - 통합 데미지 시스템 사용"""
        
        try:
            # 통합 데미지 시스템 사용
            from .unified_damage_system import calculate_hp_damage
            
            # 스킬 정보 변환 (CharacterTrait 객체 처리)
            if hasattr(skill, '__dict__'):
                # CharacterTrait 등의 객체인 경우
                skill_name = getattr(skill, 'name', "HP 공격")
                damage_type = getattr(skill, 'damage_type', "physical")
                element = getattr(skill, 'element', "none")
            elif isinstance(skill, dict):
                # 딕셔너리인 경우
                skill_name = skill.get("name", "HP 공격")
                damage_type = skill.get("damage_type", "physical")
                element = skill.get("element", "none")
            else:
                # 기타 경우
                skill_name = "HP 공격"
                damage_type = "physical"
                element = "none"
            
            unified_skill = {
                "name": skill_name,
                "hp_power": hp_power / 100.0,  # 100 기준을 1.0 기준으로 변환
                "damage_type": damage_type,
                "element": element
            }
            
            # 통합 시스템으로 HP 데미지 계산 (hp_power 인수 제거)
            result, wound_damage = calculate_hp_damage(caster, target, unified_skill)
            
            return result.final_damage
            
        except Exception as e:
            print(f"❌ HP 데미지 계산 오류: {e}")
            # 폴백: 간단한 계산
            brv_points = getattr(caster, 'brave_points', 0)
            hp_power_normalized = hp_power / 100.0
            return max(1, int(brv_points * hp_power_normalized * 0.115))
        
        # 아군/적군 구분하여 배율 적용
        is_enemy = hasattr(caster, 'character_class') and caster.character_class == "Enemy"
        if is_enemy:
            # 적군: 원래 배율 유지
            base_damage = int(caster_attack * hp_power_normalized * 0.8 * (100 / (100 + target_defense)))
        else:
            # 아군: 1.75배 증가 (0.8 → 1.4)
            base_damage = int(caster_attack * hp_power_normalized * 1.4 * (100 / (100 + target_defense)))
        
        # 🔥 강화된 시스템 사용 가능한 경우
        if ENHANCED_SYSTEMS_AVAILABLE and self.trait_processor:
            # 스킬 타입에 따른 데미지 타입 결정
            skill_name = skill.get("name", "") if isinstance(skill, dict) else getattr(skill, 'name', "")
            damage_type = "magic" if any(word in skill_name.lower() for word in ["마법", "magic", "spell"]) else "physical"
            
            # 특성 효과로 데미지 증폭
            enhanced_damage = apply_trait_effects_to_damage(caster, target, base_damage, damage_type)
            
            # 방어 특성 효과 적용
            final_damage = apply_trait_effects_to_defense(target, enhanced_damage, damage_type)
            
            # 상대적 밸런스 적용
            if self.balance_system:
                attacker_stat = caster.magic_attack if damage_type == "magic" else caster.physical_attack
                defender_stat = target.magic_defense if damage_type == "magic" else target.physical_defense
                
                balanced_damage = calculate_balanced_damage(
                    attacker_stat,
                    defender_stat,
                    final_damage / base_damage if base_damage > 0 else 1.0
                )
                final_damage = balanced_damage
            
            # 특수 능력 발동
            from .trait_integration_system import trigger_special_abilities
            special_effects = trigger_special_abilities(caster, target)
            if special_effects:
                for effect_msg in special_effects[:1]:  # HP 공격에서는 1개만
                    print(f"  {effect_msg}")
        else:
            # 기존 시스템 (폴백)
            final_damage = base_damage
        
        # HP 공격 후 BRV 소모 (오페라 옴니아 방식)
        if hasattr(caster, 'consume_brave_points'):
            consumed_brv = caster.consume_brave_points()
            print(f"  {caster.name}의 BRV {consumed_brv} 소모됨")
        else:
            # 폴백: 직접 BRV를 0으로
            caster.brave_points = 0
            print(f"  {caster.name}의 BRV가 0이 되었습니다")
        
        return max(1, int(final_damage))  # 최소 1 데미지
    
    def _apply_skill_buff(self, skill, target):
        """스킬 버프 적용"""
        # 간단한 버프 시스템
        buff_type = skill.get("buff_type", "attack")
        buff_value = skill.get("buff_value", 10)
        
        if buff_type == "attack" and hasattr(target, 'temp_attack_bonus'):
            target.temp_attack_bonus = getattr(target, 'temp_attack_bonus', 0) + buff_value
            
    def _apply_skill_debuff(self, skill, target):
        """스킬 디버프 적용"""
        # 간단한 디버프 시스템
        debuff_type = skill.get("debuff_type", "defense")
        debuff_value = skill.get("debuff_value", 10)
        
        if debuff_type == "defense" and hasattr(target, 'temp_defense_penalty'):
            target.temp_defense_penalty = getattr(target, 'temp_defense_penalty', 0) + debuff_value
    
    def _execute_combo_attack(self, attacker: Character, target: Character, skill, base_damage: int, base_brave_gain: int):
        """연타 공격 실행 - 각 타격마다 브레이크 체크"""
        print(f"🥊 {attacker.name}의 연타 공격 시작!")
        
        # 연타 횟수 결정 (2~4회)
        combo_hits = 3  # 기본 3연타
        
        # 직업별 연타 횟수 조정
        character_class = getattr(attacker, 'character_class', '')
        if character_class == '몽크':
            combo_hits = 4  # 몽크는 4연타
        elif character_class == '해적':
            combo_hits = 2  # 해적은 2연타 (강한 타격)
        
        total_damage = 0
        total_brave_gain = 0
        
        for hit_num in range(combo_hits):
            # 각 타격의 데미지 (점점 강해지도록)
            hit_damage = int(base_damage * (0.7 + hit_num * 0.15))  # 70%, 85%, 100%, 115%
            hit_brave_gain = int(base_brave_gain * (0.7 + hit_num * 0.15))
            
            # 🎯 각 타격마다 브레이크 체크
            was_already_zero_before_hit = (target.brave_points <= 0)
            
            # BRV 데미지 적용
            target.brave_points -= hit_damage
            attacker.add_brave_points(hit_brave_gain)
            
            total_damage += hit_damage
            total_brave_gain += hit_brave_gain
            
            print(f"  💥 {hit_num + 1}타: {target.name}에게 {hit_damage} BRV 피해!")
            
            # 🔥 브레이크 체크 - 이전에 0이었는데 추가 타격을 받으면 브레이크
            if target.brave_points <= 0:
                target.brave_points = 0
                
                # 브레이크 조건: 이미 0이었던 상태에서 추가 BRV 공격을 받았을 때
                if was_already_zero_before_hit and not getattr(target, 'is_broken', False):
                    target.is_broken = True
                    
                    # ATB 게이지 초기화 (BREAK 시)
                    target.atb_gauge = 0
                    
                    # 캐스팅 중단 (BREAK 시)
                    if hasattr(target, 'is_casting') and target.is_casting:
                        skill_name = getattr(target, 'casting_skill', {}).get('name', '스킬')
                        self._clear_casting_state(target)
                    
                    self.visualizer.show_status_change(target, "BREAK!", False)
                    print(f"\n{get_color('BRIGHT_RED')}{'='*50}")
                    print(f"💥 {target.name}이(가) {hit_num + 1}타에서 BREAK 상태가 되었습니다! 💥")
                    print(f"   (BRV 0 상태에서 연타 공격을 받아 무력화!)")
                    print(f"{'='*50}{get_color('RESET')}\n")
                    
                    # Break 전용 효과음 재생
                    if hasattr(self, 'sound_system'):
                        self.sound_system.play_sfx("break_sound")
                    enhanced_battle_effect("break")
                    
                    # 브레이크 발생 시 연타 중단 (옵션)
                    # break  # 주석 해제하면 브레이크 시 연타 중단
            
            # 타격 간 짧은 대기
            if hasattr(self, 'gauge_animator'):
                self.gauge_animator._wait_with_skip_option(0.3, f"{hit_num + 1}타 완료")
        
        print(f"🥊 연타 완료! 총 {total_damage} BRV 피해, {total_brave_gain} BRV 획득!")
        
        # 연타 공격 완료 후 다른 특수 효과들 실행
        other_effects = [effect for effect in skill.special_effects if effect != "combo_attack"]
        if other_effects:
            self._execute_special_effects(other_effects, attacker, skill, [target])

    def _execute_special_effects(self, special_effects, caster, skill, targets):
        """특수 효과 직접 실행 (폴백 메서드)"""
        try:
            from .new_skill_system import get_special_effect_handlers
            effect_handlers = get_special_effect_handlers()
            
            for effect_name in special_effects:
                if effect_name in effect_handlers:
                    try:
                        # 효과 핸들러에 적절한 인자 전달 - 유연한 호출 방식
                        handler = effect_handlers[effect_name]
                        
                        # 함수 시그니처에 따라 적절한 인자 전달
                        import inspect
                        sig = inspect.signature(handler)
                        params = list(sig.parameters.keys())
                        
                        if len(params) == 1:
                            # caster만 받는 경우 (예: _elemental_mastery(caster))
                            handler(caster)
                        elif len(params) == 2:
                            # caster, target 받는 경우
                            target = targets[0] if targets else None
                            handler(caster, target)
                        elif len(params) == 3:
                            # caster, target, skill_data 받는 경우
                            target = targets[0] if targets else None
                            handler(caster, target, skill)
                        else:
                            # 기본적으로 모든 인자 전달 시도
                            try:
                                handler(caster, targets, skill)
                            except:
                                # 실패하면 caster만 전달
                                handler(caster)
                    except Exception as e:
                        # 특수 효과 실행 오류를 로그에 기록
                        log_effect_error(effect_name, f"특수 효과 실행 중 오류", e)
                else:
                    # 알 수 없는 특수 효과를 로그에 기록
                    log_effect_error(effect_name, "알 수 없는 특수 효과")
        except ImportError as e:
            # Import 오류를 로그에 기록
            log_effect_error("ImportError", "New Skill System을 불러올 수 없음", e)
        except Exception as e:
            # 일반 오류를 로그에 기록
            log_effect_error("General", "특수 효과 실행 중 예상치 못한 오류", e)
    
    def _calculate_heal_amount(self, skill, caster):
        """힐량 계산"""
        base_heal = skill.get("base_value", skill.get("heal_power", 100))
        magic_attack = getattr(caster, 'magic_attack', 100)
        
        # 힐량 = 기본량 + (마법공격력 * 0.5)
        heal_amount = int(base_heal + (magic_attack * 0.5))
        return max(heal_amount, 1)
    
    def _apply_buff(self, skill, target):
        """버프 적용"""
        # 간단한 버프 시스템
        buff_type = skill.get("buff_type", "attack")
        buff_value = skill.get("buff_value", 10)
        duration = skill.get("duration", 3)
        
        if buff_type == "attack":
            if hasattr(target, 'temp_attack_bonus'):
                target.temp_attack_bonus += buff_value
            else:
                target.temp_attack_bonus = buff_value
    
    def _apply_debuff(self, skill, target):
        """디버프 적용"""
        # 간단한 디버프 시스템
        debuff_type = skill.get("debuff_type", "defense")
        debuff_value = skill.get("debuff_value", 10)
        duration = skill.get("duration", 3)
        
        if debuff_type == "defense":
            if hasattr(target, 'temp_defense_penalty'):
                target.temp_defense_penalty += debuff_value
            else:
                target.temp_defense_penalty = debuff_value
    
    def _apply_special_skill(self, skill, caster, target):
        """특수 스킬 효과 적용"""
        skill_name = skill.get("name", "")
        
        # 연속공격 효과
        if "연속" in skill_name or skill.get("consecutive_attacks", 0) > 0:
            attacks = skill.get("consecutive_attacks", 2)
            print(f"⚔️ {skill_name}: {attacks}연속 공격!")
            
            total_damage = 0
            for i in range(attacks):
                print(f"  🗡️ {i+1}번째 공격:")
                
                # 각 공격별 BRV/HP 데미지 적용
                if skill.get("brv_power", 0) > 0:
                    brv_damage = self._calculate_brv_damage(skill, caster, target, skill.get("brv_power"))
                    old_brv = target.brave_points
                    target.brave_points -= brv_damage
                    target.brave_points = max(0, target.brave_points)
                    print(f"    ⚡ BRV: {old_brv} → {target.brave_points} (-{brv_damage})")
                    total_damage += brv_damage
                
                if skill.get("hp_power", 0) > 0:
                    hp_damage = self._calculate_hp_damage_from_skill(skill, caster, target, skill.get("hp_power"))
                    actual_damage = target.take_damage(hp_damage)
                    print(f"    💥 HP: -{actual_damage}")
                    total_damage += actual_damage
                
                # BREAK 체크
                if target.brave_points <= 0 and hasattr(target, 'apply_break_if_needed'):
                    if target.apply_break_if_needed():
                        print(f"    💥 {target.name}이(가) BREAK 상태가 되었습니다!")
                
                # 대상이 죽으면 연속공격 중단
                if not target.is_alive:
                    print(f"    ⚰️ {target.name}이(가) 쓰러졌습니다! 연속공격 중단.")
                    
                    # 🔊 적 처치 SFX 재생
                    if hasattr(self, 'audio_system') and self.audio_system:
                        self.audio_system.play_sfx("enemy_defeat")
                    elif hasattr(self, 'sound_manager') and self.sound_manager:
                        self.sound_manager.play_sfx("enemy_defeat")
                    
                    break
                    
                # 연속공격 간 짧은 딜레이 - 더 빠르게
                time_module.sleep(0.08)  # 80ms로 단축 (300ms→80ms)
            
            print(f"💀 총 {total_damage} 데미지 가함!")
            
        # 전체공격 효과
        elif "전체" in skill_name or skill.get("area_attack", False):
            print(f"💥 {skill_name}: 전체 공격!")
            # 이미 targets에 전체가 포함되어 있으므로 개별 처리는 상위에서 수행됨
            
        # 흡혈 효과
        elif "흡혈" in skill_name or skill.get("drain_hp", False):
            if skill.get("hp_power", 0) > 0:
                hp_damage = self._calculate_hp_damage_from_skill(skill, caster, target, skill.get("hp_power"))
                actual_damage = target.take_damage(hp_damage)
                
                # 가한 데미지의 일정 비율만큼 회복
                drain_rate = skill.get("drain_rate", 0.3)  # 30% 기본
                heal_amount = int(actual_damage * drain_rate)
                actual_heal = caster.heal(heal_amount)
                
                print(f" {caster.name}이(가) {actual_heal} HP 흡혈 회복!")
        
        # 무모한 돌격 효과
        elif "무모한 돌격" in skill_name:
            # 무모한 돌격: 강력한 HP 공격 + 자신도 데미지
            damage_to_target = self._calculate_hp_damage_from_skill(skill, caster, target, 150)
            actual_damage = target.take_damage(damage_to_target)
            
            # 자신에게도 반동 데미지
            self_damage = int(damage_to_target * 0.3)
            caster.take_damage(self_damage)
            print(f"💢 {caster.name}도 반동으로 {self_damage} 데미지를 받았습니다!")
        
        # 영혼 파악 효과
        elif "영혼 파악" in skill_name:
            # 영혼 파악: 적의 정보 표시 + 정신 데미지
            print(f"👁️ {caster.name}이(가) {target.name}의 영혼을 들여다봅니다...")
            
            # 적 정보 분석 표시
            print(f"📊 === {target.name}의 상태 분석 ===")
            print(f"  ❤️ HP: {target.current_hp}/{target.max_hp} ({target.current_hp/target.max_hp*100:.1f}%)")
            if hasattr(target, 'brave_points'):
                print(f"  ⚡ BRV: {target.brave_points}")
            if hasattr(target, 'physical_attack'):
                print(f"  ⚔️ 물리공격: {target.physical_attack}")
            if hasattr(target, 'physical_defense'):
                print(f"  🛡️ 물리방어: {target.physical_defense}")
            # WOUND는 0이 아닐 때만 표시, 이모지 제거
            if hasattr(target, 'wounds') and target.wounds > 0:
                print(f"  WOUND: {target.wounds}")
            
            # 특수 상태 확인
            if hasattr(target, 'is_broken') and target.is_broken:
                print(f"  💥 상태: BREAK")
            
            # 정신 데미지 (작은 HP 데미지)
            soul_damage = int(getattr(caster, 'magic_attack', 100) * 0.5)  # 마법공격력의 50%
            actual_damage = target.take_damage(soul_damage)
        
        # 진실 간파 효과
        elif "진실 간파" in skill_name:
            # 진실 간파: 철학자의 스킬 - 적의 약점과 진실 노출
            print(f"🔍 {caster.name}이(가) 철학의 힘으로 {target.name}의 진실을 간파합니다...")
            
            # 적의 상세 정보 표시 (철학자의 지혜)
            print("=" * 50)
            print(f"📖 【{target.name}의 진실】")
            print("=" * 50)
            
            # 기본 스탯 분석
            defense_ratio = target.defense / caster.attack if hasattr(caster, 'attack') and caster.attack > 0 else 1.0
            threat_level = "낮음" if defense_ratio < 0.7 else "보통" if defense_ratio < 1.3 else "높음"
            
            print(f"🛡️ 방어력: {getattr(target, 'defense', getattr(target, 'physical_defense', 0))} (위협도: {threat_level})")
            print(f"⚔️ 공격력: {getattr(target, 'attack', getattr(target, 'physical_attack', 0))}")
            
            # BRV 정보가 있다면 표시
            if hasattr(target, 'current_brave'):
                print(f"💎 현재 BRV: {target.current_brave}")
                if hasattr(target, 'max_brave'):
                    print(f"💎 최대 BRV: {target.max_brave}")
            elif hasattr(target, 'brave_points'):
                print(f"💎 현재 BRV: {target.brave_points}")
            
            # 약점 노출 효과
            vulnerability_bonus = 0.35  # 35% 추가 데미지
            duration = 3  # 3턴 지속
            
            if hasattr(target, 'temp_vulnerability'):
                target.temp_vulnerability = max(target.temp_vulnerability, vulnerability_bonus)
            else:
                target.temp_vulnerability = vulnerability_bonus
                
            if hasattr(target, 'vulnerability_turns'):
                target.vulnerability_turns = max(target.vulnerability_turns, duration)
            else:
                target.vulnerability_turns = duration
            
            print("=" * 50)
            print(f"⚠️ 【약점 노출】")
            print(f"   📈 받는 데미지 +{vulnerability_bonus*100:.0f}% ({duration}턴)")
            print(f"   🎯 철학자의 지혜가 적의 약점을 드러냈습니다!")
            print("=" * 50)
            
            # 정신적 충격 데미지 (진실을 마주한 충격)
            psychic_damage = int(getattr(caster, 'magic_attack', 100) * 0.8)  # 철학자의 정신력 기반
            actual_damage = target.take_damage(psychic_damage)
        
        # 기본적인 단일 공격 (특수 효과 없음)
        else:
            # 특수 효과만 있는 스킬 (BRV나 HP 데미지가 없는 유틸리티 스킬)
            special_effects = skill.get("special_effects", [])
            if special_effects:
                print(f"✨ {skill_name}: 특수 효과 발동!")
                # special_effects는 별도로 처리되므로 여기서는 알림만
            else:
                # 기본 BRV/HP 데미지 처리
                if skill.get("brv_power", 0) > 0:
                    brv_damage = self._calculate_brv_damage(skill, caster, target, skill.get("brv_power"))
                    old_brv = target.brave_points
                    target.brave_points -= brv_damage
                    target.brave_points = max(0, target.brave_points)
                    print(f"⚡ {target.name}의 BRV: {old_brv} → {target.brave_points} (-{brv_damage})")
                    
                    # BREAK 체크
                    if target.brave_points <= 0 and hasattr(target, 'apply_break_if_needed'):
                        if target.apply_break_if_needed():
                            print(f"💥 {target.name}이(가) BREAK 상태가 되었습니다!")
                
                if skill.get("hp_power", 0) > 0:
                    hp_damage = self._calculate_hp_damage_from_skill(skill, caster, target, skill.get("hp_power"))
                    actual_damage = target.take_damage(hp_damage)
    
    # ==================== AI 게임모드 지원 메서드들 ====================
    
    def _initialize_ai_personalities(self):
        """🧠 AI 개성 시스템 초기화"""
        # AI 개성별 사고 시간과 정확도 설정
        self.ai_personalities = {
            # 전투 직업군 - 빠른 판단
            '전사': {'thinking_time': (0.3, 0.8), 'accuracy_modifier': 1.1, 'type': '성급함'},
            '아크메이지': {'thinking_time': (1.5, 3.0), 'accuracy_modifier': 1.2, 'type': '신중함'},
            '궁수': {'thinking_time': (0.8, 1.5), 'accuracy_modifier': 1.15, 'type': '냉정함'},
            '도적': {'thinking_time': (0.3, 0.7), 'accuracy_modifier': 1.0, 'type': '성급함'},
            '성기사': {'thinking_time': (1.0, 2.0), 'accuracy_modifier': 1.1, 'type': '균형'},
            '암흑기사': {'thinking_time': (0.5, 1.2), 'accuracy_modifier': 1.05, 'type': '균형'},
            '몽크': {'thinking_time': (0.2, 0.6), 'accuracy_modifier': 0.95, 'type': '성급함'},
            '바드': {'thinking_time': (1.2, 2.5), 'accuracy_modifier': 1.15, 'type': '신중함'},
            
            # 마법 직업군 - 신중한 판단
            '네크로맨서': {'thinking_time': (2.0, 4.0), 'accuracy_modifier': 1.25, 'type': '신중함'},
            '용기사': {'thinking_time': (0.8, 1.5), 'accuracy_modifier': 1.1, 'type': '냉정함'},
            '검성': {'thinking_time': (1.5, 2.5), 'accuracy_modifier': 1.2, 'type': '신중함'},
            '정령술사': {'thinking_time': (1.8, 3.2), 'accuracy_modifier': 1.3, 'type': '신중함'},
            '시간술사': {'thinking_time': (2.5, 4.0), 'accuracy_modifier': 1.4, 'type': '신중함'},
            '연금술사': {'thinking_time': (1.5, 2.8), 'accuracy_modifier': 1.25, 'type': '신중함'},
            '차원술사': {'thinking_time': (2.0, 3.5), 'accuracy_modifier': 1.35, 'type': '신중함'},
            '마검사': {'thinking_time': (1.0, 1.8), 'accuracy_modifier': 1.15, 'type': '균형'},
            '기계공학자': {'thinking_time': (1.2, 2.2), 'accuracy_modifier': 1.2, 'type': '신중함'},
            '무당': {'thinking_time': (1.8, 3.0), 'accuracy_modifier': 1.25, 'type': '신중함'},
            
            # 특수 직업군 - 다양한 성향
            '암살자': {'thinking_time': (0.1, 0.4), 'accuracy_modifier': 1.3, 'type': '성급함'},
            '해적': {'thinking_time': (0.4, 0.9), 'accuracy_modifier': 0.9, 'type': '성급함'},
            '사무라이': {'thinking_time': (1.5, 2.8), 'accuracy_modifier': 1.3, 'type': '신중함'},
            '드루이드': {'thinking_time': (2.0, 3.5), 'accuracy_modifier': 1.2, 'type': '신중함'},
            '철학자': {'thinking_time': (3.0, 4.0), 'accuracy_modifier': 1.5, 'type': '신중함'},
            '검투사': {'thinking_time': (0.3, 0.8), 'accuracy_modifier': 1.0, 'type': '성급함'},
            '기사': {'thinking_time': (1.0, 2.0), 'accuracy_modifier': 1.15, 'type': '균형'},
            '신관': {'thinking_time': (1.5, 2.5), 'accuracy_modifier': 1.2, 'type': '신중함'},
            '광전사': {'thinking_time': (0.1, 0.3), 'accuracy_modifier': 0.8, 'type': '성급함'},
        }
        
        # 자동 배틀 모드용 고정 설정
        self.auto_battle_thinking_time = (0.5, 1.2)
        
        print("🧠 AI 개성 시스템 활성화! (직업별 사고 패턴)")
    
    def _execute_ai_action(self, character: Character, action_type: str, action_data: dict, party: List[Character], enemies: List[Character]):
        """AI가 결정한 액션 실행 (개성별 사고 시간 포함)"""
        try:
            # 🧠 AI 개성별 사고 시간 적용
            import random
            import time
            
            character_class = getattr(character, 'character_class', '')
            personality = self.ai_personalities.get(character_class, {
                'thinking_time': (0.5, 1.0), 
                'accuracy_modifier': 1.0, 
                'type': '균형'
            })
            
            # 자동 배틀 모드가 아닌 경우에만 사고 시간 적용
            if not getattr(self, 'auto_battle_mode', False):
                thinking_min, thinking_max = personality['thinking_time']
                thinking_time = random.uniform(thinking_min, thinking_max)
                personality_type = personality['type']
                
                print(f"🧠 {character.name}({character_class}) {personality_type} 사고 중... ({thinking_time:.1f}초)")
                time.sleep(thinking_time)
            
            if action_type == "attack":
                # 기본 공격
                target = action_data.get("target")
                if not target:
                    # 대상이 없으면 적절한 타겟 선택
                    if character in enemies or getattr(character, 'character_class', '') == 'Enemy':
                        # 적이면 아군을 공격
                        alive_targets = [p for p in party if p.is_alive]
                    else:
                        # 아군이면 적을 공격
                        alive_targets = [e for e in enemies if e.is_alive]
                    
                    target = alive_targets[0] if alive_targets else None
                
                if target:
                    print(f"🤖 {character.name}이(가) {target.name}을(를) 공격합니다!")
                    return self.execute_brave_attack(character, target)
                else:
                    return self.defend_action(character)
            
            elif action_type == "brv_attack":
                # BRV 공격 (BRV 축적)
                target = action_data.get("target")
                if not target:
                    if character in enemies or getattr(character, 'character_class', '') == 'Enemy':
                        alive_targets = [p for p in party if p.is_alive]
                    else:
                        alive_targets = [e for e in enemies if e.is_alive]
                    target = alive_targets[0] if alive_targets else None
                
                if target:
                    print(f"🤖 {character.name}이(가) {target.name}에게 BRV 공격!")
                    return self.execute_brave_attack(character, target)
                else:
                    return self.defend_action(character)
            
            elif action_type == "hp_attack":
                # HP 공격 (BRV 소모하여 실제 피해)
                target = action_data.get("target")
                if not target:
                    if character in enemies or getattr(character, 'character_class', '') == 'Enemy':
                        alive_targets = [p for p in party if p.is_alive]
                    else:
                        alive_targets = [e for e in enemies if e.is_alive]
                    target = alive_targets[0] if alive_targets else None
                
                if target:
                    print(f"🤖 {character.name}이(가) {target.name}에게 HP 공격!")
                    return self.execute_hp_attack(character, target)
                else:
                    return self.defend_action(character)
            
            elif action_type == "skill":
                # 스킬 사용
                skill = action_data.get("skill")
                target = action_data.get("target")
                
                if skill and target:
                    print(f"🤖 {character.name}이(가) {skill.get('name', '스킬')}을(를) 사용합니다!")
                    return self._apply_skill_effect(character, skill, target, party, enemies)
                else:
                    # 스킬이나 대상이 없으면 기본 공격
                    return self._execute_ai_action(character, "attack", {}, party, enemies)
            
            elif action_type == "heal":
                # 치료
                target = action_data.get("target", character)
                heal_amount = int(target.max_hp * 0.2)
                target.heal(heal_amount)
                print(f"🤖 {character.name}이(가) {target.name}을(를) {heal_amount} HP 치료!")
                return None
            
            elif action_type == "use_item":
                # 아이템 사용
                item = action_data.get("item")
                target = action_data.get("target", character)
                
                if item:
                    print(f"🤖 {character.name}이(가) {item.name}을(를) 사용합니다!")
                    return self._apply_item_effect(character, item, target)
                else:
                    return self.defend_action(character)
            
            elif action_type == "defend":
                # 방어
                print(f"🤖 {character.name}이(가) 방어 자세를 취합니다!")
                return self.defend_action(character)
            
            elif action_type == "coordinated_attack":
                # 협동 공격
                partner = action_data.get("partner")
                target = action_data.get("target")
                
                if not target:
                    alive_enemies = [e for e in enemies if e.is_alive]
                    target = alive_enemies[0] if alive_enemies else None
                
                if target and partner:
                    print(f"🤖 {character.name}과(와) {partner.name}의 협동 공격!")
                    # 협동 공격은 일반 공격보다 1.5배 강함
                    result = self.brave_attack(character, target)
                    if result and hasattr(result, 'damage'):
                        result.damage = int(result.damage * 1.5)
                    
                    # AI 게임 모드에서 협동공격 성공 대사 출력
                    if hasattr(self, 'ai_game_mode') and self.ai_game_mode:
                        self.ai_game_mode.show_coordination_success_dialogue(character, partner)
                    
                    return result
                else:
                    return self._execute_ai_action(character, "attack", {}, party, enemies)
            
            else:
                # 기본 행동: 방어
                return self.defend_action(character)
                
        except Exception as e:
            print(f"❌ AI 액션 실행 오류: {e}")
            # 오류 발생시 방어로 대체
            return self.defend_action(character)
    
    def _apply_skill_effect(self, character: Character, skill, target: Character, party: List[Character], enemies: List[Character]):
        """스킬 효과 적용 - 실제 스킬 시스템 사용"""
        try:
            # 실제 스킬 시스템과 연동
            if hasattr(skill, 'type'):
                # 실제 스킬 객체인 경우
                skill_type = skill.type
                skill_name = skill.name
            else:
                # 딕셔너리 형태인 경우
                skill_type = skill.get('type', 'BRV_ATTACK')
                skill_name = skill.get('name', '스킬')
            
            # MP 소모
            mp_cost = getattr(skill, 'mp_cost', skill.get('mp_cost', 0)) if hasattr(skill, 'mp_cost') or isinstance(skill, dict) else 0
            if mp_cost > 0 and character.current_mp >= mp_cost:
                character.current_mp -= mp_cost
                print(f"   💙 MP {mp_cost} 소모")
            
            # 스킬 타입에 따른 처리
            if skill_type in ['BRV_ATTACK', 'brv_attack']:
                # BRV 공격 스킬
                damage = self._calculate_skill_damage(character, skill, target)
                brv_gain = int(damage * 1.2)  # BRV 축적량
                character.brv = min(character.brv + brv_gain, character.max_brv)
                print(f"   ⚡ {character.name}의 BRV {brv_gain} 상승! (현재: {character.brv})")
                return None
                
            elif skill_type in ['HP_ATTACK', 'hp_attack']:
                # HP 공격 스킬
                damage = self._calculate_skill_damage(character, skill, target)
                brv_damage = min(character.brv, target.max_hp)  # BRV만큼 HP 피해
                target.take_damage(brv_damage)
                character.brv = 0  # BRV 소모
                print(f"   💥 {target.name}에게 {brv_damage} HP 피해!")
                return None
                
            elif skill_type in ['HEAL', 'heal', 'SUPPORT', 'support']:
                # 치료/지원 스킬
                heal_power = getattr(skill, 'hp_power', skill.get('power', 1.0)) if hasattr(skill, 'hp_power') or isinstance(skill, dict) else 1.0
                heal_amount = int(character.magic_attack * heal_power)
                
                # 대상 결정
                if skill.get('target', 'ally') == 'ally' or skill_type in ['HEAL', 'heal']:
                    # 아군 치료
                    if character in enemies:
                        # 적이 사용하는 경우 - 자신 치료
                        target = character
                    else:
                        # 아군이 사용하는 경우 - 가장 HP가 낮은 아군 치료
                        alive_allies = [p for p in party if p.is_alive and p.current_hp < p.max_hp]
                        if alive_allies:
                            target = min(alive_allies, key=lambda x: x.current_hp / x.max_hp)
                        else:
                            target = character
                
                target.heal(heal_amount)
                print(f"   💚 {target.name}의 HP {heal_amount} 회복!")
                return None
                
            elif skill_type in ['DEBUFF', 'debuff']:
                # 디버프 스킬
                debuff_name = skill.get('debuff', '약화')
                duration = skill.get('duration', 3)
                print(f"   🔻 {target.name}에게 {debuff_name} 효과!")
                # 실제 디버프 시스템이 있다면 여기서 적용
                return None
                
            else:
                # 기본 공격형 스킬
                damage = self._calculate_skill_damage(character, skill, target)
                target.take_damage(damage)
                print(f"   💥 {target.name}에게 {damage} 피해!")
                return None
                
        except Exception as e:
            print(f"❌ 스킬 적용 오류: {e}")
            # 오류 발생시 기본 공격으로 대체
            return self.brave_attack(character, target)
    
    def _calculate_skill_damage(self, character: Character, skill, target: Character) -> int:
        """스킬 데미지 계산"""
        try:
            # 스킬 파워 가져오기
            if hasattr(skill, 'hp_power'):
                power = skill.hp_power
            elif isinstance(skill, dict):
                power = skill.get('power', 1.0)
            else:
                power = 1.0
            
            # 기본 공격력 계산
            if hasattr(skill, 'type'):
                skill_type = skill.type
            else:
                skill_type = skill.get('type', 'BRV_ATTACK')
            
            if skill_type in ['HP_ATTACK', 'hp_attack', 'BRV_ATTACK', 'brv_attack']:
                base_damage = character.physical_attack
            else:
                base_damage = character.magic_attack
            
            # 스킬 데미지 계산
            damage = int(base_damage * power)
            
            # 크리티컬 확률 (5%)
            import random
            if random.random() < 0.05:
                damage = int(damage * 1.5)
                print(f"   ✨ 크리티컬 히트!")
                # 🎮 크리티컬 진동
                if self.vibration_enabled:
                    self.input_manager.vibrate_heavy()
            
            return max(damage, 1)
        
        except Exception as e:
            print(f"❌ 스킬 데미지 계산 오류: {e}")
            return character.physical_attack
    
    def _add_job_stack_display(self, display, party):
        """Phase 1&2 완성 직업들의 스택 시스템 표시 + 다양한 직업 상태"""
        
        stack_displays = []
        
        for char in party:
            character_class = getattr(char, 'character_class', '')
            
            # Phase 1 직업들
            if character_class == "검성" and hasattr(char, 'sword_aura_stacks'):
                if char.sword_aura_stacks > 0:
                    stack_displays.append(f"\033[96m⚔️ {char.name}: SWORD AURA {char.sword_aura_stacks}/2\033[0m")
            
            elif character_class == "검투사" and hasattr(char, 'kill_stacks'):
                if char.kill_stacks > 0:
                    stack_displays.append(f"\033[93m🏆 {char.name}: KILL STACKS {char.kill_stacks}\033[0m")
            
            elif character_class == "광전사" and hasattr(char, 'absorption_stacks'):
                if char.absorption_stacks > 0:
                    absorption_hp = getattr(char, 'absorption_hp', 0)
                    stack_displays.append(f"\033[91m🩸 {char.name}: ABSORPTION {absorption_hp}HP\033[0m")
            
            elif character_class == "기사" and hasattr(char, 'duty_stacks'):
                if char.duty_stacks > 0:
                    stack_displays.append(f"\033[94m🛡️ {char.name}: DUTY STACKS {char.duty_stacks}/5\033[0m")
            
            # Phase 2 직업들
            elif character_class == "성기사":
                if hasattr(char, 'sanctuary_hits') and char.sanctuary_hits > 0:
                    stack_displays.append(f"\033[97m✨ {char.name}: SANCTUARY {char.sanctuary_hits}/3\033[0m")
            
            elif character_class == "암흑기사" and hasattr(char, 'dark_aura_stacks'):
                if char.dark_aura_stacks > 0:
                    stack_displays.append(f"\033[95m🌑 {char.name}: DARK AURA {char.dark_aura_stacks}\033[0m")
            
            elif character_class == "용기사" and hasattr(char, 'dragon_mark_stacks'):
                if char.dragon_mark_stacks > 0:
                    stack_displays.append(f"\033[91m🐉 {char.name}: DRAGON MARK {char.dragon_mark_stacks}\033[0m")
            
            # 🏹 궁수 조준 시스템
            elif character_class == "궁수":
                if hasattr(char, 'aim_points') and char.aim_points > 0:
                    stack_displays.append(f"\033[93m🎯 {char.name}: AIM POINTS {char.aim_points}/5\033[0m")
                if hasattr(char, 'support_fire_active') and char.support_fire_active:
                    turns_left = getattr(char, 'support_fire_turns', 0)
                    stack_displays.append(f"\033[96m🏹 {char.name}: SUPPORT FIRE ({turns_left} turns)\033[0m")
            
            elif character_class == "아크메이지":
                if hasattr(char, 'lightning_counter') and char.lightning_counter > 0:
                    stack_displays.append(f"\033[96m⚡ {char.name}: LIGHTNING {char.lightning_counter}\033[0m")
                if hasattr(char, 'elemental_combo') and char.elemental_combo > 0:
                    combo_element = getattr(char, 'last_element', '?')
                    stack_displays.append(f"\033[97m🔮 {char.name}: ELEMENTAL COMBO {combo_element}×{char.elemental_combo}\033[0m")
            
            # 기본 직업들
            elif character_class == "전사":
                # 전사의 자세 시스템 - 숨김 처리
                pass  # STANCE 표시 제거
            
            elif character_class == "암살자":
                # 암살자의 그림자 시스템 - 숨김 처리 (사용자 요청)
                # if hasattr(char, 'shadow_count') and char.shadow_count > 0:
                #     stack_displays.append(f"\033[90m👤 {char.name}: SHADOWS {char.shadow_count}\033[0m")
                if hasattr(char, 'stealth_turns') and char.stealth_turns > 0:
                    stack_displays.append(f"\033[90m🕶️ {char.name}: STEALTH {char.stealth_turns}T\033[0m")
            
            elif character_class == "도적":
                # 도적의 독 시스템 - 적들의 독 수치 총합
                total_venom = 0
                if hasattr(self, '_current_enemies'):
                    for enemy in self._current_enemies:
                        if hasattr(enemy, 'poison_stacks'):
                            total_venom += enemy.poison_stacks
                        elif hasattr(enemy, 'venom_stacks'):
                            total_venom += enemy.venom_stacks
                
                if total_venom > 0:
                    stack_displays.append(f"\033[92m☠️ {char.name}: TOTAL VENOM {total_venom}\033[0m")
                
                # 도적의 개인 독 관련 상태
                if hasattr(char, 'poison_mastery_stacks') and char.poison_mastery_stacks > 0:
                    stack_displays.append(f"\033[92m🧪 {char.name}: POISON MASTERY {char.poison_mastery_stacks}\033[0m")
            
            elif character_class == "바드":
                # 바드의 음표 시스템
                if hasattr(char, 'melody_stacks') and char.melody_stacks > 0:
                    stack_displays.append(f"\033[93m🎵 {char.name}: MELODY {char.melody_stacks}\033[0m")
                if hasattr(char, 'inspiration_duration') and char.inspiration_duration > 0:
                    stack_displays.append(f"\033[93m🎶 {char.name}: INSPIRATION {char.inspiration_duration}T\033[0m")
            
            elif character_class == "몽크":
                # 몽크의 내공 시스템
                if hasattr(char, 'chi_stacks') and char.chi_stacks > 0:
                    stack_displays.append(f"\033[95m☯️ {char.name}: CHI {char.chi_stacks}\033[0m")
                if hasattr(char, 'meditation_bonus') and char.meditation_bonus > 0:
                    stack_displays.append(f"\033[95m🧘 {char.name}: MEDITATION {char.meditation_bonus}%\033[0m")
            
            elif character_class == "네크로맨서":
                # 네크로맨서의 언데드 시스템
                if hasattr(char, 'undead_minions') and char.undead_minions > 0:
                    stack_displays.append(f"\033[90m💀 {char.name}: UNDEAD MINIONS {char.undead_minions}\033[0m")
                if hasattr(char, 'soul_energy') and char.soul_energy > 0:
                    stack_displays.append(f"\033[90m👻 {char.name}: SOUL ENERGY {char.soul_energy}\033[0m")
            
            # 🌟 Phase 3 신규 직업들 (시간/공간/철학/연금술)
            elif character_class == "시간술사":
                # 시간술사의 시간 조작 시스템
                if hasattr(char, 'time_rewind_stacks') and char.time_rewind_stacks > 0:
                    stack_displays.append(f"\033[96m⏰ {char.name}: TIME REWIND {char.time_rewind_stacks}/3\033[0m")
                if hasattr(char, 'temp_time_sense') and char.temp_time_sense:
                    stack_displays.append(f"\033[96m🔮 {char.name}: TIME SENSE ACTIVE\033[0m")
                if hasattr(char, 'temp_atb_boost') and char.temp_atb_boost > 0:
                    stack_displays.append(f"\033[96m⚡ {char.name}: TIME ACCELERATION\033[0m")
            
            elif character_class == "차원술사":
                # 차원술사의 공간 조작 시스템
                if hasattr(char, 'dimension_shield_stacks') and char.dimension_shield_stacks > 0:
                    stack_displays.append(f"\033[95m🛡️ {char.name}: DIMENSION SHIELD {char.dimension_shield_stacks}/5\033[0m")
                if hasattr(char, 'afterimage_stacks') and char.afterimage_stacks > 0:
                    stack_displays.append(f"\033[95m👥 {char.name}: AFTERIMAGE {char.afterimage_stacks}/10\033[0m")
                if hasattr(char, 'temp_enemy_accuracy_down') and char.temp_enemy_accuracy_down > 0:
                    stack_displays.append(f"\033[95m🌀 {char.name}: SPACE DISTORTION\033[0m")
            
            elif character_class == "철학자":
                # 철학자의 지혜 시스템
                if hasattr(char, 'wisdom_stacks') and char.wisdom_stacks > 0:
                    stack_displays.append(f"\033[97m📚 {char.name}: WISDOM {char.wisdom_stacks}/10\033[0m")
                if hasattr(char, 'temp_confusion_immunity') and char.temp_confusion_immunity:
                    stack_displays.append(f"\033[97m🧠 {char.name}: CONTEMPLATION\033[0m")
            
            elif character_class == "연금술사":
                # 연금술사의 포션 제작 시스템
                if hasattr(char, 'potion_craft_stacks') and char.potion_craft_stacks > 0:
                    stack_displays.append(f"\033[92m🧪 {char.name}: POTION CRAFT {char.potion_craft_stacks}/5\033[0m")
                if hasattr(char, 'temp_fire_resistance') and char.temp_fire_resistance > 0:
                    stack_displays.append(f"\033[91m🔥 {char.name}: FIRE RESISTANCE\033[0m")
                if hasattr(char, 'temp_water_resistance') and char.temp_water_resistance > 0:
                    stack_displays.append(f"\033[94m💧 {char.name}: WATER RESISTANCE\033[0m")
                if hasattr(char, 'temp_earth_resistance') and char.temp_earth_resistance > 0:
                    stack_displays.append(f"\033[93m🌍 {char.name}: EARTH RESISTANCE\033[0m")
                if hasattr(char, 'temp_air_resistance') and char.temp_air_resistance > 0:
                    stack_displays.append(f"\033[96m💨 {char.name}: AIR RESISTANCE\033[0m")
        
        # 스택 정보가 있으면 표시
        if stack_displays:
            display.add_line("\033[97m📊 STACK STATUS\033[0m")
            for stack_info in stack_displays:
                display.add_line(f"   {stack_info}")
            display.add_line("")  # 빈 줄 추가
    
    def _trigger_support_fire(self, acting_character: Character, target: Character, trigger_type: str):
        """🏹 궁수 지원사격 트리거 시스템"""
        # 파티 멤버 중 궁수 찾기
        party_members = []
        if hasattr(self, 'party') and self.party:
            party_members = self.party
        elif hasattr(self, 'players') and self.players:
            party_members = self.players
        
        for archer in party_members:
            if (hasattr(archer, 'character_class') and archer.character_class == "궁수" and
                getattr(archer, 'support_fire_active', False) and 
                getattr(archer, 'aim_points', 0) > 0 and
                archer != acting_character and archer.current_hp > 0):
                
                # 지원사격 실행
                self._execute_support_fire(archer, target)
    
    def _update_special_status_turn_start(self, character: Character):
        """턴 시작 시 특수 상태 업데이트 (보호막, 스택 등)"""
        updates = []
        
        # 🛡️ 피의 방패 지속시간 감소 (광전사)
        if hasattr(character, 'blood_shield_turns') and character.blood_shield_turns > 0:
            character.blood_shield_turns -= 1
            if character.blood_shield_turns <= 0:
                if hasattr(character, 'blood_shield'):
                    lost_shield = character.blood_shield
                    character.blood_shield = 0
                    updates.append(f"🛡️ 피의 방패가 소멸했습니다! (보호막 {lost_shield} 상실)")
                character.blood_shield_turns = 0
            else:
                updates.append(f"🛡️ 피의 방패 {character.blood_shield_turns}턴 남음")
        
        # 🎯 조준 포인트 자연 감소 (궁수)
        if hasattr(character, 'precision_points') and character.precision_points > 0:
            character.precision_points = max(0, character.precision_points - 1)
            if character.precision_points > 0:
                updates.append(f"🎯 조준 포인트 자연 감소: {character.precision_points}")
        
        # 🌙 그림자 스택은 스킬 사용 시에만 소모됩니다 (자연 감소 제거)
        
        # ☠️ 독 스택 자연 감소 (도적) - 최대치에 따른 비율 감소
        if hasattr(character, 'poison_stacks') and character.poison_stacks > 0:
            max_stacks = getattr(character, 'max_poison_stacks', 100)
            # 최대치가 높을수록 감소량도 증가 (관리의 필요성)
            decay_rate = max(1, int(max_stacks * 0.02))  # 최대치의 2%씩 감소
            character.poison_stacks = max(0, character.poison_stacks - decay_rate)
            if character.poison_stacks > 0:
                updates.append(f"☠️ 독 스택 감소: {character.poison_stacks}/{max_stacks} (-{decay_rate})")
        
        # 🔥❄️⚡ 원소 카운트 자연 감소 (아크메이지)
        if hasattr(character, 'fire_count') and character.fire_count > 0:
            character.fire_count = max(0, character.fire_count - 1)
        if hasattr(character, 'ice_count') and character.ice_count > 0:
            character.ice_count = max(0, character.ice_count - 1)
        if hasattr(character, 'lightning_count') and character.lightning_count > 0:
            character.lightning_count = max(0, character.lightning_count - 1)
        
        # ⚔️ 검기 스택 자연 감소 (검성)
        if hasattr(character, 'sword_aura') and character.sword_aura > 0:
            character.sword_aura = max(0, character.sword_aura - 1)
            if character.sword_aura > 0:
                updates.append(f"⚔️ 검기 감소: {character.sword_aura}")
        
        # 🏛️ 투기 포인트 자연 감소 (검투사)
        if hasattr(character, 'arena_points') and character.arena_points > 0:
            character.arena_points = max(0, character.arena_points - 1)
            if character.arena_points > 0:
                updates.append(f"🏛️ 투기 포인트 감소: {character.arena_points}")
        
        # 💢 광폭화 스택 지속 (광전사 - 감소하지 않음)
        if hasattr(character, 'rage_stacks') and character.rage_stacks > 0:
            updates.append(f"💢 광폭화 지속: {character.rage_stacks}")
        
        # 🌟 정령 친화도 자연 감소 (정령술사)
        if hasattr(character, 'spirit_bond') and character.spirit_bond > 0:
            character.spirit_bond = max(0, character.spirit_bond - 1)
            if character.spirit_bond > 0:
                updates.append(f"🌟 정령 친화도 감소: {character.spirit_bond}")
        
        # ⏰ 시간 기록점 지속 (시간술사 - 감소하지 않음)
        if hasattr(character, 'time_marks') and character.time_marks > 0:
            updates.append(f"⏰ 시간 기록점 유지: {character.time_marks}")
        
        # 🆕 추가 직업별 특수 상태 업데이트
        
        # 🐉 용의 표식 감소 (용기사)
        if hasattr(character, 'dragon_marks') and character.dragon_marks > 0:
            character.dragon_marks = max(0, character.dragon_marks - 1)
            if character.dragon_marks > 0:
                updates.append(f"🐉 용의 표식 감소: {character.dragon_marks}")
        
        # 👊 타격 표식 감소 (몽크)
        if hasattr(character, 'strike_marks') and character.strike_marks > 0:
            character.strike_marks = max(0, character.strike_marks - 1)
            if character.strike_marks > 0:
                updates.append(f"👊 타격 표식 감소: {character.strike_marks}")
        
        # 🎵 음표 스택 감소 (바드)
        if hasattr(character, 'melody_stacks') and character.melody_stacks > 0:
            character.melody_stacks = max(0, character.melody_stacks - 1)
            if character.melody_stacks > 0:
                updates.append(f"🎵 음표 스택 감소: {character.melody_stacks}")
        
        # 💀 네크로 에너지 감소 (네크로맨서)
        if hasattr(character, 'necro_energy') and character.necro_energy > 0:
            character.necro_energy = max(0, character.necro_energy - 1)
            if character.necro_energy > 0:
                updates.append(f"💀 네크로 에너지 감소: {character.necro_energy}")
        
        # 🔧 기계 오버드라이브 감소 (기계공학자)
        if hasattr(character, 'overdrive_stacks') and character.overdrive_stacks > 0:
            character.overdrive_stacks = max(0, character.overdrive_stacks - 1)
            if character.overdrive_stacks > 0:
                updates.append(f"🔧 오버드라이브 감소: {character.overdrive_stacks}")
        
        # 🔯 영혼 에너지 감소 (무당)
        if hasattr(character, 'soul_energy') and character.soul_energy > 0:
            character.soul_energy = max(0, character.soul_energy - 1)
            if character.soul_energy > 0:
                updates.append(f"🔯 영혼 에너지 감소: {character.soul_energy}")
        
        # 🏴‍☠️ 해적 보물 감소 (해적)
        if hasattr(character, 'treasure_count') and character.treasure_count > 0:
            character.treasure_count = max(0, character.treasure_count - 1)
            if character.treasure_count > 0:
                updates.append(f"🏴‍☠️ 보물 감소: {character.treasure_count}")
        
        # 🗾 무사도 정신 지속 (사무라이 - 감소하지 않음)
        if hasattr(character, 'bushido_spirit') and character.bushido_spirit > 0:
            updates.append(f"🗾 무사도 정신 유지: {character.bushido_spirit}")
        
        # 🌿 자연의 힘 감소 (드루이드)
        if hasattr(character, 'nature_power') and character.nature_power > 0:
            character.nature_power = max(0, character.nature_power - 1)
            if character.nature_power > 0:
                updates.append(f"🌿 자연의 힘 감소: {character.nature_power}")
        
        # 📘 지혜 스택 감소 (철학자)
        if hasattr(character, 'wisdom_stacks') and character.wisdom_stacks > 0:
            character.wisdom_stacks = max(0, character.wisdom_stacks - 1)
            if character.wisdom_stacks > 0:
                updates.append(f"📘 지혜 스택 감소: {character.wisdom_stacks}")
        
        # ⚗️ 연금술 재료 감소 (연금술사)
        if hasattr(character, 'alchemy_materials') and character.alchemy_materials > 0:
            character.alchemy_materials = max(0, character.alchemy_materials - 1)
            if character.alchemy_materials > 0:
                updates.append(f"⚗️ 연금술 재료 감소: {character.alchemy_materials}")
        
        # ✨ 성스러운 힘 감소 (성기사, 신관)
        if hasattr(character, 'holy_power') and character.holy_power > 0:
            character.holy_power = max(0, character.holy_power - 1)
            if character.holy_power > 0:
                updates.append(f"✨ 성스러운 힘 감소: {character.holy_power}")
        
        # 🌑 어둠의 힘 감소 (암흑기사)
        if hasattr(character, 'dark_power') and character.dark_power > 0:
            character.dark_power = max(0, character.dark_power - 1)
            if character.dark_power > 0:
                updates.append(f"🌑 어둠의 힘 감소: {character.dark_power}")
        
        # 🐎 기사도 정신 감소 (기사)
        if hasattr(character, 'chivalry_points') and character.chivalry_points > 0:
            character.chivalry_points = max(0, character.chivalry_points - 1)
            if character.chivalry_points > 0:
                updates.append(f"🐎 기사도 감소: {character.chivalry_points}")
        
        # ⚡ 마검 융합 감소 (마검사)
        if hasattr(character, 'magic_sword_fusion') and character.magic_sword_fusion > 0:
            character.magic_sword_fusion = max(0, character.magic_sword_fusion - 1)
            if character.magic_sword_fusion > 0:
                updates.append(f"⚡ 마검 융합 감소: {character.magic_sword_fusion}")
        
        # 🌌 차원 에너지 감소 (차원술사)
        if hasattr(character, 'dimension_energy') and character.dimension_energy > 0:
            character.dimension_energy = max(0, character.dimension_energy - 1)
            if character.dimension_energy > 0:
                updates.append(f"🌌 차원 에너지 감소: {character.dimension_energy}")
        
        # 업데이트 메시지 출력
        if updates:
            print(f"📋 {character.name}의 특수 상태 업데이트:")
            for update in updates:
                print(f"   {update}")
    
    def _execute_support_fire(self, archer: Character, target: Character):
        """지원사격 실행"""
        # 조준 포인트 소모 (최대 3포인트)
        points_to_use = min(3, getattr(archer, 'aim_points', 0))
        if points_to_use <= 0:
            return
        
        archer.aim_points = max(0, archer.aim_points - points_to_use)
        
        # 지원사격 위력 계산 (포인트당 증가)
        base_damage = archer.physical_attack * 0.8
        support_damage = int(base_damage * (1 + points_to_use * 0.3))
        
        # 회피 체크
        if self._check_dodge(archer, target):
            print(f"🏹 {archer.name}의 지원사격이 빗나갔습니다!")
            return
        
        # 데미지 적용
        target.current_hp = max(0, target.current_hp - support_damage)
        
        print(f"🎯 {archer.name}의 지원사격! (조준 포인트 {points_to_use}개 소모)")
        print(f"   💥 {target.name}에게 {support_damage} 피해!")
        
        # 지원사격 턴 감소
        if hasattr(archer, 'support_fire_turns'):
            archer.support_fire_turns -= 1
            if archer.support_fire_turns <= 0:
                archer.support_fire_active = False
                print(f"   🔚 {archer.name}의 지원사격 모드가 종료되었습니다.")
        
        # 사운드 효과
        if hasattr(self, 'sound_system'):
            self.sound_system.play_sfx("bow_shot")
    
    def _process_support_fire_duration(self, character: Character):
        """지원사격 지속시간 감소 처리"""
        if (hasattr(character, 'character_class') and character.character_class == "궁수" and
            getattr(character, 'support_fire_active', False)):
            
            if hasattr(character, 'support_fire_turns'):
                character.support_fire_turns -= 1
                if character.support_fire_turns <= 0:
                    character.support_fire_active = False
                    print(f"🔚 {character.name}의 지원사격 모드가 종료되었습니다.")

    def _real_time_combat_menu(self, character, party, enemies, action_options, action_descriptions):
        """
        실시간 ATB 시스템이 적용된 전투 메뉴
        플레이어가 선택하는 동안에도 ATB가 업데이트되며, 적의 ATB가 100%에 도달하면 인터럽트
        """
        import time
        import sys
        
        print(f"\n🎮 {character.name}의 턴 - 실시간 ATB 활성")
        print("="*60)
        
        # 현재 선택된 옵션 인덱스
        selected_index = 0
        max_index = len(action_options) - 1
        
        # ATB 업데이트 타이머 (파워쉘 최적화)
        last_atb_update = time.time()
        last_display_update = time.time()
        atb_update_interval = 0.05  # 50ms마다 ATB 업데이트 (20fps)
        display_update_interval = 0.05  # 50ms마다 화면 업데이트 (20fps 고정)
        
        # 난이도별 불릿 타임 배율 가져오기
        bullet_time_multiplier = self._get_bullet_time_multiplier()
        
        # 초기 화면 표시
        self._display_realtime_combat_status(character, party, enemies, action_options, selected_index)
        
        # 타임아웃 방지 (2분 후 자동으로 첫 번째 옵션 선택) - 적절한 시간 설정
        start_time = time.time()
        timeout = 120.0  # 2분으로 설정 (충분히 길지만 무한대기 방지)
        warning_shown = False  # 경고 메시지 표시 여부
        
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # 1분 30초 후 경고 메시지 (한 번만)
            if elapsed_time > 90.0 and not warning_shown:
                print(f"\n⚠️ 30초 후 자동으로 '{action_options[0]}'이(가) 선택됩니다. 원하는 행동을 선택해주세요!")
                warning_shown = True
            
            # 타임아웃 체크 (2분 후)
            if elapsed_time > timeout:
                print(f"\n⏰ {timeout/60:.0f}분 시간 초과! 자동으로 '{action_options[0]}'을(를) 선택합니다.")
                print("📝 참고: 이 기능은 게임이 멈추는 것을 방지하기 위한 안전장치입니다.")
                return 0
            
            # 🔄 실시간 ATB 업데이트 (적절한 주기)
            if current_time - last_atb_update >= atb_update_interval:
                enemy_interrupted = False
                
                # 🛡️ 아군 ATB 업데이트 (누락된 부분 추가!)
                for ally in party:
                    if ally.is_alive and hasattr(ally, 'atb_gauge'):
                        if ally.atb_gauge < self.ATB_READY_THRESHOLD:
                            speed_multiplier = getattr(ally, 'speed', 50) / 100.0
                            base_increase = int(self.BASE_ATB_INCREASE * speed_multiplier)
                            # config.py의 난이도별 player_turn_speed 사용
                            atb_increase = int(base_increase * bullet_time_multiplier)
                            
                            ally.atb_gauge = min(self.ATB_MAX, ally.atb_gauge + atb_increase)
                
                # ⚔️ 적군 ATB 업데이트 (기존 로직 유지)
                for enemy in enemies:
                    if enemy.is_alive and hasattr(enemy, 'atb_gauge'):
                        # ATB가 이미 100%가 아닌 경우에만 증가
                        if enemy.atb_gauge < self.ATB_READY_THRESHOLD:
                            # 난이도별 불릿 타임 적용
                            speed_multiplier = getattr(enemy, 'speed', 50) / 100.0
                            base_increase = int(self.BASE_ATB_INCREASE * speed_multiplier)
                            # config.py의 난이도별 player_turn_speed 사용
                            atb_increase = int(base_increase * bullet_time_multiplier)
                            
                            old_atb = enemy.atb_gauge
                            enemy.atb_gauge = min(self.ATB_MAX, enemy.atb_gauge + atb_increase)
                            
                            # 적의 ATB가 행동 가능 상태에 도달하면 조용히 인터럽트
                            if enemy.atb_gauge >= self.ATB_READY_THRESHOLD and old_atb < self.ATB_READY_THRESHOLD:
                                print(f"\n⚡ {enemy.name}이(가) 행동할 차례입니다!")

                                # 🔥 적 인터럽트 페널티: 아군 전체 ATB 10% 감소
                                print(f"💨 적의 기습으로 아군 전체가 약간 흔들렸습니다! (ATB -10%)")
                                for ally in party:
                                    if ally.is_alive and hasattr(ally, 'atb_gauge'):
                                        old_ally_atb = ally.atb_gauge
                                        ally.atb_gauge = max(0, ally.atb_gauge - 100)
                                        print(f"   📉 {ally.name}: ATB {old_ally_atb} → {ally.atb_gauge}")
                                
                                time.sleep(1)
                                return None  # 적 턴으로 전환
                
                last_atb_update = current_time
            
            # 🖥️ 화면 업데이트 (깜빡임 방지)
            if current_time - last_display_update >= display_update_interval:
                self._display_realtime_combat_status(character, party, enemies, action_options, selected_index)
                last_display_update = current_time
            
            # 키 입력 확인 (논블로킹, 강화된 버전)
            key_pressed = False
            try:
                if sys.platform == "win32":
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch()
                        key_pressed = True
                        
                        if key == b'\r' or key == b'\n':  # Enter
                            print(f"\n✅ '{action_options[selected_index]}' 선택됨!")
                            return selected_index
                        elif key == b'q' or key == b'Q':  # 취소
                            print(f"\n❌ 취소됨!")
                            return -1
                        elif key == b'w' or key == b'W' or key == b'\x00H':  # 위 (W 또는 방향키)
                            selected_index = max(0, selected_index - 1)
                            self._display_realtime_combat_status(character, party, enemies, action_options, selected_index)
                        elif key == b's' or key == b'S' or key == b'\x00P':  # 아래 (S 또는 방향키)
                            selected_index = min(max_index, selected_index + 1)
                            self._display_realtime_combat_status(character, party, enemies, action_options, selected_index)
                        elif key.isdigit():  # 숫자 직접 선택
                            num = int(key.decode()) - 1
                            if 0 <= num <= max_index:
                                print(f"\n✅ '{action_options[num]}' 선택됨!")
                                return num
                else:
                    # Linux/Mac 논블로킹 입력 (개선된 버전)
                    import select
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        key = sys.stdin.read(1)
                        key_pressed = True
                        
                        if key == '\n':
                            print(f"\n✅ '{action_options[selected_index]}' 선택됨!")
                            return selected_index
                        elif key == 'q' or key == 'Q':
                            print(f"\n❌ 취소됨!")
                            return -1
                        elif key == 'w' or key == 'W':
                            selected_index = max(0, selected_index - 1)
                            self._display_realtime_combat_status(character, party, enemies, action_options, selected_index)
                        elif key == 's' or key == 'S':
                            selected_index = min(max_index, selected_index + 1)
                            self._display_realtime_combat_status(character, party, enemies, action_options, selected_index)
                        elif key.isdigit():
                            num = int(key) - 1
                            if 0 <= num <= max_index:
                                print(f"\n✅ '{action_options[num]}' 선택됨!")
                                return num
            except Exception as input_error:
                # 입력 오류 시 폴백
                pass
            
            # CPU 사용량 절약 (파워쉘 최적화)
            if not key_pressed:
                time.sleep(0.05)  # 50ms 대기 (파워쉘에서 안정적)
    
    def _display_realtime_menu(self, character, party, enemies, action_options, selected_index):
        """부드러운 실시간 메뉴 화면 표시 (깜빡임 최소화)"""
        # ANSI 이스케이프 시퀀스로 부드러운 화면 업데이트
        import sys
        import os
        
        try:
            # Windows에서 ANSI 지원 활성화
            if os.name == 'nt':
                os.system('color')  # Windows ANSI 활성화
            
            # 커서를 맨 위로 이동하고 화면 지우기 (깜빡임 방지)
            sys.stdout.write('\033[H\033[J')  # 커서 홈 이동 + 화면 클리어
            sys.stdout.flush()
        except:
            # 폴백: 최소한의 화면 클리어
            print('\n' * 2)
        
        print(f"🎮 {character.name}의 턴 - 실시간 ATB 시스템")
        print("="*70)
        
        # 🛡️ 간단한 파티 상태 표시 (ATB_READY_THRESHOLD 기준)
        print("🛡️ 아군 파티:")
        for member in party:
            if member.is_alive:
                hp_pct = int((member.current_hp / member.max_hp) * 100)
                
                # ATB 계산 수정: ATB_READY_THRESHOLD 기준
                atb_gauge = getattr(member, 'atb_gauge', 0)
                atb_pct = int((atb_gauge / self.ATB_READY_THRESHOLD) * 100)
                atb_status = "⚡READY" if atb_pct >= 100 else f"{atb_pct}%"
                
                print(f"  🔮 {member.name}: HP {hp_pct}% | ATB {atb_status} [RAW: {atb_gauge}/{self.ATB_READY_THRESHOLD}]")
        
        print("\n⚔️ 적군:")
        for enemy in enemies:
            if enemy.is_alive:
                hp_pct = int((enemy.current_hp / enemy.max_hp) * 100)
                
                # ATB 계산 수정: ATB_READY_THRESHOLD 기준
                atb_gauge = getattr(enemy, 'atb_gauge', 0)
                atb_pct = int((atb_gauge / self.ATB_READY_THRESHOLD) * 100)
                atb_status = "⚡READY" if atb_pct >= 100 else f"{atb_pct}%"
                
                # ATB 위험도에 따른 색상 표시
                if atb_pct >= 90:
                    status_color = "🔴⚠️"  # 매우 위험
                elif atb_pct >= 75:
                    status_color = "🟠⚡"  # 위험
                elif atb_pct >= 50:
                    status_color = "🟡📈"  # 주의
                else:
                    status_color = "⚪💤"  # 안전
                
                print(f"  {status_color} {enemy.name}: HP {hp_pct}% | ATB {atb_status} [RAW: {atb_gauge}/{self.ATB_READY_THRESHOLD}]")
        
        print("\n" + "="*70)
        print("📝 행동 선택:")
        
        # 메뉴 옵션 표시
        for i, option in enumerate(action_options):
            if i == selected_index:
                print(f"👉 [{i+1}] {option} 👈")
            else:
                print(f"   [{i+1}] {option}")
        
        print("\n" + "="*70)
        print("🔼🔽 W/S: 위/아래 | ⚡ Enter: 선택 | ❌ Q: 취소 | 🔢 1-9: 직접선택")
        print("⏰ 실시간 ATB: 적의 ATB가 100%가 되면 자동으로 턴이 넘어갑니다!")
        print("💡 빨간색 적은 곧 행동합니다! 서둘러 선택하세요!")
        print("="*70)

    def _get_bullet_time_multiplier(self):
        """config 파일의 난이도별 불릿 타임 배율 반환"""
        try:
            # config 파일에서 난이도와 player_turn_speed 가져오기
            import config
            game_config = config.GameConfig()
            
            # 현재 난이도 확인 (기본값: "보통")
            current_difficulty = getattr(self, 'difficulty', '보통')
            
            # 설정 파일에서 난이도 정보 가져오기 시도
            try:
                settings = game_config.load_settings()
                if 'difficulty' in settings:
                    current_difficulty = settings['difficulty']
            except:
                pass
            
            # config 파일의 DIFFICULTY_SETTINGS에서 player_turn_speed 가져오기
            difficulty_settings = game_config.DIFFICULTY_SETTINGS
            if current_difficulty in difficulty_settings:
                multiplier = difficulty_settings[current_difficulty]['player_turn_speed']
                return multiplier
            else:
                # 기본값: 보통 난이도의 player_turn_speed
                return difficulty_settings['보통']['player_turn_speed']
                
        except Exception as e:
            # 오류 시 기본값 반환
            return 0.2  # 보통 난이도 기본값

    def _display_realtime_combat_status(self, character, party, enemies, action_options, selected_index):
        """optimized_gauge_system을 사용한 실시간 전투 상태 표시 (화면 스택 방지)"""
        
        # 🖥️ 강력한 화면 클리어로 중첩 완전 방지
        try:
            from .clear_screen_utils import force_clear_screen
            force_clear_screen()
        except ImportError:
            # 폴백: 기본 화면 클리어
            os.system('cls' if os.name == 'nt' else 'clear')
            print('\033[2J\033[H', end='', flush=True)
        
        # 🖥️ 상단 정렬 전투 화면 출력 (화면 잘림 방지)
        try:
            from .clear_screen_utils import minimal_clear, wait_frame
            from .optimized_gauge_system import OptimizedGaugeSystem
            
            # 최소한의 화면 클리어 (화면 잘림 방지)
            minimal_clear()
            
            # 프레임레이트 제어 (20-60 FPS)
            wait_frame()
            
            gauge_system = OptimizedGaugeSystem()
            
            # 🛡️ 파티 정보 표시 (헤더 완전 제거)
            party_display = gauge_system.show_optimized_party_status(party, character)
            if party_display:
                print(party_display)
            print("")
            
            # ⚔️ 적군 정보 표시 (헤더 완전 제거)
            enemy_display = gauge_system.show_optimized_enemy_status(enemies)
            if enemy_display:
                print(enemy_display)
            print("")
            
            # 📝 메뉴 표시 (구분선 최소화)
            print("📝 행동 선택:")
            for i, option in enumerate(action_options):
                if i == selected_index:
                    print(f"👉 [{i+1}] {option} 👈")
                else:
                    print(f"   [{i+1}] {option}")
            print("")
            print("🔼🔽 W/S: 위/아래 | ⚡ Enter: 선택 | ❌ Q: 취소")
            
        except ImportError:
            # 폴백: 기본 상단 정렬 화면 출력
            from .clear_screen_utils import minimal_clear
            minimal_clear()
            
            # 🎮 간단한 헤더 표시
            print(f"{get_color('BRIGHT_YELLOW')}⚔️ {character.name}의 턴{get_color('RESET')}")
            print("")
            
            # 기본 파티/적군 표시 시도
            try:
                from .optimized_gauge_system import OptimizedGaugeSystem
                gauge_system = OptimizedGaugeSystem()
                
                party_display = gauge_system.show_optimized_party_status(party, character)
                print(party_display)
                
                enemy_display = gauge_system.show_optimized_enemy_status(enemies)
                print(enemy_display)
                
            except ImportError:
                # 최종 폴백: 간단한 상태 표시
                print(f"🛡️ 파티: {len([m for m in party if m.is_alive])}명 생존")
                print(f"⚔️ 적군: {len([e for e in enemies if e.is_alive])}마리 생존")
            
            # 📝 메뉴 표시
            print("📝 행동 선택:")
            for i, option in enumerate(action_options):
                if i == selected_index:
                    print(f"👉 [{i+1}] {option} 👈")
                else:
                    print(f"   [{i+1}] {option}")
            print("🔼🔽 W/S: 위/아래 | ⚡ Enter: 선택 | ❌ Q: 취소")

        # 키 입력 처리