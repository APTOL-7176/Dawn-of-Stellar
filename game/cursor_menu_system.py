#!/usr/bin/env python3
"""
통합 메뉴 시스템 - FFVII 스타일 커서 네비게이션
Dawn of Stellar의 모든 메뉴에 적용되는 통합 메뉴 시스템
"""

import os
import sys
import time
import platform
import time as _t
try:
    import msvcrt  # Windows에서만 존재
except Exception:
    msvcrt = None

# 메뉴 디버그 토글 (환경변수로 제어)
MENU_DEBUG = os.getenv('MENU_DEBUG') == '1'
from typing import List, Optional, Callable, Any
from enum import Enum

# 안전 로깅(선택): 메뉴 표시/선택 시 시스템 로그 남기기
try:
    from game.error_logger import log_system as _menu_log_system
except Exception:
    _menu_log_system = None

# 전역 메뉴 락: 동시에 두 개 이상의 메뉴 루프가 돌지 않도록 방지
_ACTIVE_MENU = False
class MenuAction(Enum):
    """메뉴 액션 타입"""
    SELECT = "select"
    CANCEL = "cancel"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    INFO = "info"
    SPECIAL = "special"

class MenuItem:
    """메뉴 아이템 클래스"""
    def __init__(self, text: str, action: Callable = None, enabled: bool = True, 
                 description: str = "", value: Any = None):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.description = description
        self.value = value

class CursorMenu:
    """FFVII 스타일 커서 메뉴"""
    
    def __init__(self, title: str = "", options: List[str] = None, descriptions: List[str] = None, 
                 audio_manager=None, keyboard=None, cancellable: bool = True, extra_content: str = "",
                 clear_screen: bool = True,
                 buffered: bool = False, multi_select: bool = False, max_selections: int = 4,
                 ignore_initial_enter_ms: float = 0.2):
        """메뉴 초기화"""
        try:
            if not audio_manager:
                from game.audio_system import get_audio_manager
                self.audio_manager = get_audio_manager()
            else:
                self.audio_manager = audio_manager

            if not keyboard:
                # 게임패드 지원을 위한 통합 입력 관리자 사용
                from game.input_utils import UnifiedInputManager
                self.keyboard = UnifiedInputManager()
            else:
                self.keyboard = keyboard
        except ImportError:
            print("⚠️ 오디오 시스템을 불러올 수 없습니다.")
            self.audio_manager = None
            # 폴백: 기본 키보드 입력
            try:
                from game.input_utils import KeyboardInput
                self.keyboard = KeyboardInput()
            except:
                self.keyboard = None
        except Exception as e:
            # 예상치 못한 초기화 오류
            print(f"⚠️ 초기화 중 오류: {e}")
            self.audio_manager = None
            self.keyboard = None

        # 기본 상태값
        self.selected_index = 0
        self.items: List[MenuItem] = []
        self.title = title
        self.extra_content = extra_content  # 추가 콘텐츠 (파티 정보 등)
        self.show_description = True
        self.show_index = True
        self.show_header = True  # 헤더(==== 장식) 표시 여부
        self.cancellable = cancellable
        self.compact_mode = os.getenv('SUBPROCESS_MODE') == '1'
        self.clear_screen = clear_screen
        self.buffered = buffered or self.compact_mode
        self._last_render_line_count = 0
        self._last_key = None
        try:
            import time as _t
            self._ignore_enter_until = _t.time() + (ignore_initial_enter_ms if ignore_initial_enter_ms else 0)
        except Exception:
            self._ignore_enter_until = 0
        # 초기 Enter/Q 억제를 한 번만 적용하기 위한 플래그
        self._grace_suppressed_once = False
        self._grace_cancel_suppressed_once = False
        
        # 멀티 선택 관련 설정
        self.multi_select = multi_select
        self.max_selections = max_selections
        self.selected_items = set()  # 선택된 아이템 인덱스들
        # PowerShell/Windows Terminal 환경 감지 및 설정
        powershell_env = (
            'PSModulePath' in os.environ or 
            'WT_SESSION' in os.environ or
            'TERM_PROGRAM' in os.environ or
            'powershell' in sys.executable.lower() or
            'pwsh' in sys.executable.lower()
        )
        
        # 런처에서 PowerShell로 실행되었는지 확인
        launcher_powershell = os.getenv('LAUNCHER_POWERSHELL') == '1'
        
        # CMD 전용 모드 감지 (배치 파일에서 설정)
        cmd_only_mode = os.getenv('USE_CMD_ONLY') == '1'
        terminal_type = os.getenv('TERMINAL_TYPE')
        
        if cmd_only_mode or terminal_type == 'CMD':
            self._ansi_inplace_supported = False
            print("[INFO] CMD 전용 모드 감지 - 기본 메뉴 시스템 사용")
        elif powershell_env or launcher_powershell:
            self._ansi_inplace_supported = True
            print("[INFO] PowerShell 환경 감지 - 고급 메뉴 시스템 활성화")
        else:
            self._ansi_inplace_supported = False
            print("[INFO] 명령 프롬프트 환경 감지 - 기본 메뉴 시스템 사용")
            
        self._menu_displayed = False
        
        # 모바일 환경 감지 (Flutter 클라이언트나 HTTP 모드) - 안전한 초기화
        try:
            self.is_mobile = (os.getenv('MOBILE_MODE') == '1' or 
                             os.getenv('HTTP_MODE') == '1' or
                             os.getenv('FLUTTER_MODE') == '1')
        except Exception:
            # 환경변수 접근 실패 시 기본값
            self.is_mobile = False
        
        # 모바일에서는 인플레이스 업데이트 비활성화 (중복 표시 방지)
        if self.is_mobile:
            self._ansi_inplace_supported = False
            self.compact_mode = True
        
        # PowerShell에서 ANSI 지원 강제 활성화
        if not self.is_mobile and not self.compact_mode:
            self._ansi_inplace_supported = True

        # 옵션 -> MenuItem 자동 생성
        if options:
            temp_items: List[MenuItem] = []
            for i, option in enumerate(options):
                desc = descriptions[i] if descriptions and i < len(descriptions) else ""
                temp_items.append(MenuItem(option, description=desc))
            self.set_items(temp_items)

    def _println(self, text: str = "", normalize_multi: bool = False):
        """명령 프롬프트 전용 출력 - 단순하게"""
        try:
            print(text)
        except Exception:
            pass
        
    def set_items(self, items: List[MenuItem]):
        """메뉴 아이템 설정"""
        self.items = items
        self.selected_index = 0
        
    def set_title(self, title: str):
        """메뉴 제목 설정"""
        self.title = title
            
    def play_cursor_sound(self):
        """커서 이동 사운드 재생"""
        # 쿨다운 비활성화 - input_utils.py 중복 제거로 인해 불필요
        if self.audio_manager:
            try:
                self.audio_manager.play_sfx("menu_select")  # 000.wav
            except:
                pass  # 사운드 재생 실패해도 계속 진행
            
    def play_confirm_sound(self):
        """확인 사운드 재생"""
        # 쿨다운 비활성화
        if self.audio_manager:
            try:
                self.audio_manager.play_sfx("menu_confirm")  # 001.wav
            except:
                pass  # 사운드 재생 실패해도 계속 진행
            
    def play_cancel_sound(self):
        """취소 사운드 재생"""
        # 쿨다운 비활성화
        if self.audio_manager:
            try:
                self.audio_manager.play_sfx("menu_cancel")  # 003.wav
            except:
                pass  # 사운드 재생 실패해도 계속 진행
            
    def play_error_sound(self):
        """에러 사운드 재생"""
        # 쿨다운 비활성화
        if self.audio_manager:
            try:
                self.audio_manager.play_sfx("menu_error")  # 003.wav
            except:
                pass  # 사운드 재생 실패해도 계속 진행
    
    def _clear_screen(self):
        """환경에 맞는 화면 클리어"""
        import sys
        import os
        
        if self._ansi_inplace_supported:
            # PowerShell/Windows Terminal - ANSI 시퀀스 사용
            try:
                sys.stdout.write('\033[2J\033[H')  # 화면 클리어 + 커서 홈
                sys.stdout.flush()
                return
            except:
                pass
        
        # 명령 프롬프트 - cls 명령 사용
        try:
            os.system('cls')
        except:
            # 최후 수단: 빈 줄로 밀어내기
            for _ in range(50):
                print()
        
        # 버퍼 플러시
        try:
            sys.stdout.flush()
        except:
            pass

    # ====== 신규: ANSI 지원 감지 & 라인 구성/인플레이스 렌더 ======
    def _detect_ansi_support(self) -> bool:
        """터미널이 기본 ANSI 시퀀스를 지원하는지 정확하게 감지"""
        import os
        import sys
        
        # 모바일/웹 모드는 ANSI 지원 안 함
        if self.is_mobile or self.compact_mode:
            return False
            
        # stdout이 터미널이 아니면 지원 안 함
        if not sys.stdout.isatty():
            return False
            
        if os.name != 'nt':
            # Unix/Linux는 대부분 ANSI 지원
            return True
            
        # Windows에서 ANSI 지원 체크
        # 1. Windows Terminal
        if 'WT_SESSION' in os.environ:
            return True
            
        # 2. ConEmu, Cmder 등
        if 'ANSICON' in os.environ or 'ConEmuANSI' in os.environ:
            return True
            
        # 3. PowerShell 현대 버전
        if 'PSModulePath' in os.environ:
            return True
            
        # 4. Windows 10 이상의 기본 콘솔 (VT 모드)
        try:
            import platform
            version = platform.version()
            if version and len(version.split('.')) >= 2:
                major = int(version.split('.')[0])
                if major >= 10:  # Windows 10 이상
                    return True
        except:
            pass
            
        # 4. VS Code 터미널
        if 'VSCODE_INJECTION' in os.environ or 'TERM_PROGRAM' in os.environ:
            return True
            
        # 기본값: ANSI 미지원
        return False
        # colorama 초기화 여부는 여기서 판단 어렵지만 일단 False
        return False

    def _compose_menu_lines(self) -> List[str]:
        """현재 메뉴 전체를 라인 배열로 구성 (출력 부작용 없음)"""
        lines: List[str] = []
        # 제목
        if self.title:
            if not self.compact_mode and self.show_header:
                lines.append("")
                lines.append("="*60)
                lines.append(f"{self.title:^60}")
                lines.append("="*60)
            else:
                lines.append(self.title)
        # 추가 콘텐츠
        if self.extra_content:
            # extra_content가 리스트인 경우 문자열로 변환
            if isinstance(self.extra_content, list):
                extra = '\n'.join(str(item) for item in self.extra_content)
            else:
                extra = str(self.extra_content)
            
            extra = extra.replace('\r\n','\n').replace('\r','\n')
            extra_lines = extra.split('\n')
            if self.compact_mode:
                # 연속 공백 줄 축소
                filtered=[]; prev_blank=False
                for ln in extra_lines:
                    blank = (ln.strip()=="")
                    if blank and prev_blank:
                        continue
                    filtered.append(ln)
                    prev_blank=blank
                extra_lines = filtered
            lines.extend(extra_lines)
            if not self.compact_mode:
                lines.append("")
        # 아이템
        if not self.items:
            lines.append("⚠️ 메뉴 아이템이 없습니다!")
        else:
            for i,item in enumerate(self.items):
                # 체크박스 표시 (멀티 선택 모드일 때)
                checkbox = ""
                if self.multi_select:
                    if i in self.selected_items:
                        checkbox = "☑️ "
                    else:
                        checkbox = "☐ "
                
                if not item.enabled:
                    prefix = "   " if i != self.selected_index else "👉 "
                    line = f"{prefix}{checkbox}🚫 {item.text}"
                elif i == self.selected_index:
                    if self.show_index:
                        line = f"👉 {checkbox}[{i+1}] {item.text} 👈"
                    else:
                        line = f"👉 {checkbox}{item.text} 👈"
                else:
                    if self.show_index:
                        line = f"   {checkbox}[{i+1}] {item.text}"
                    else:
                        line = f"   {checkbox}{item.text}"
                lines.append(line)
        # 설명
        if self.show_description and self.items and self.selected_index < len(self.items):
            current = self.items[self.selected_index]
            if current.description:
                if not self.compact_mode:
                    lines.append("")
                lines.append(f"💡 {current.description}")
        # 조작법
        if not self.compact_mode:
            lines.append("")
            lines.append("═"*70)
        controls=[]
        if len(self.items)>1:
            controls.append("🔼🔽 W/S: 위/아래")
        if self.multi_select:
            controls.append("☑️ Space: 체크/해제")
        controls.append("⚡ Enter: 선택")
        if self.cancellable:
            controls.append("❌ Q: 취소")
        controls.append("📋 I: 정보")
        control_text = " | ".join(controls)
        if self.compact_mode:
            lines.append("  "+control_text)
        else:
            lines.append(f"{control_text:^70}")
            lines.append("═"*70)
            lines.append(f"{'✦':^14} {'✧':^14} {'✦':^14} {'✧':^14} {'✦':^14}")
        return lines

    def _print_lines(self, lines: List[str]):
        """라인 배열 출력 (플랫폼별 줄바꿈 정규화)"""
        win = (os.name=='nt')
        for ln in lines:
            if win:
                sys.stdout.write(ln + "\r\n")
            else:
                print(ln)
        sys.stdout.flush()

    def _redraw_in_place(self):
        """환경에 맞는 화면 다시 그리기"""
        if self._ansi_inplace_supported:
            # PowerShell - 부드러운 인플레이스 업데이트
            try:
                import sys
                sys.stdout.write('\033[2J\033[H')  # 화면 클리어 + 커서 홈
                sys.stdout.flush()
                
                # 새 메뉴 내용 출력
                lines = self._compose_menu_lines()
                self._print_lines(lines)
                self._last_render_line_count = len(lines)
                return
            except:
                pass
        
        # 명령 프롬프트 - 전체 화면 클리어 후 다시 그리기
        self._clear_screen()
        lines = self._compose_menu_lines()
        self._print_lines(lines)
        self._last_render_line_count = len(lines)

    def _minimal_update(self):
        """ANSI 미지원 환경에서 최소한의 업데이트 (깜빡임 방지)"""
        # 현재 선택된 항목만 다시 표시 (짧은 업데이트)
        if not self.items or self.selected_index >= len(self.items):
            return
        
        print("\n" + "─" * 50)
        current_item = self.items[self.selected_index]
        print(f"👉 현재 선택: {current_item.text}")
        if current_item.description:
            print(f"💡 {current_item.description}")
        print("─" * 50)
        
    def _redraw_in_place_optimized(self):
        """최적화된 인플레이스 리드로우 (커서 이동만)"""
        if not self._ansi_inplace_supported or not self._menu_displayed:
            return False
            
        try:
            # 간단한 ANSI 시퀀스로 메뉴 부분만 업데이트
            lines = self._compose_menu_lines()
            
            # 커서를 메뉴 시작점으로 이동
            if self._last_render_line_count > 0:
                sys.stdout.write(f"\x1b[{self._last_render_line_count}A")
            
            # 각 줄 업데이트 (지우기 + 새 내용)
            for i, line in enumerate(lines):
                sys.stdout.write(f"\x1b[2K{line}")
                if i < len(lines) - 1:
                    sys.stdout.write("\r\n")
            
            sys.stdout.flush()
            self._last_render_line_count = len(lines)
            return True
            
        except Exception:
            return False

        
    def display_menu(self):
        """메뉴 화면 표시 - 명령 프롬프트 최적화"""
        # 안전 가드: 잘못된 인덱스 보정(클램프)
        try:
            if self.items:
                if self.selected_index < 0:
                    self.selected_index = 0
                elif self.selected_index >= len(self.items):
                    self.selected_index = len(self.items) - 1
        except Exception:
            pass
        # 최초 표시 시 시스템 로그 남기기 (가능할 때만)
        try:
            if _menu_log_system and not getattr(self, "_menu_displayed", False):
                _menu_log_system("메뉴표시", "메뉴 표시", {
                    "제목": getattr(self, 'title', ''),
                    "항목수": len(self.items) if self.items else 0,
                    "취소가능": getattr(self, 'cancellable', True)
                })
        except Exception:
            pass
        if self.clear_screen:
            # 빈 줄로 이전 내용 밀어내기 (확실한 방법)
            for _ in range(100):
                print()
            
            # cls 시도
            try:
                import os
                os.system('cls')
            except:
                pass
            
            # 추가로 빈 줄 몇 개 더
            for _ in range(5):
                print()
            
        lines = self._compose_menu_lines()
        if MENU_DEBUG:
            try:
                print(f"[MENU_DEBUG] display_menu() lines={len(lines)} sel={self.selected_index} items={len(self.items)}", flush=True)
            except Exception:
                pass
        self._print_lines(lines)
        self._last_render_line_count = len(lines)
        self._menu_displayed = True
    
    def _update_selection_inline(self):
        """선택 항목 변경 시 전체 메뉴 다시 그리기"""
        # 항상 전체 메뉴 다시 그리기
        self.display_menu()
        
    def _display_menu_footer_inline(self):
        """메뉴 하단 정보를 인라인으로 표시 (화면 스크롤 방지)"""
        # 화려한 구분선과 조작법 표시
        if not self.compact_mode:
            self._println("")
            self._println("═" * 70)
        
        # 조작법 표시 (더 예쁜 버전)
        controls = []
        if len(self.items) > 1:
            controls.append("🔼🔽 W/S: 위/아래")
        controls.append("⚡ Enter: 선택")
        if self.cancellable:
            controls.append("❌ Q: 취소")
        controls.append("📋 I: 정보")
        control_text = f" | ".join(controls)
        if self.compact_mode:
            pad = max(0, (70 - len(control_text)) // 4)
            self._println((" " * pad) + control_text)
        else:
            self._println(f"{control_text:^70}")
            self._println("═" * 70)
            # 멋진 하단 장식 (일반 모드에서만)
            self._println(f"{'✦':^14} {'✧':^14} {'✦':^14} {'✧':^14} {'✦':^14}")
    # 커서를 마지막으로 이동하여 추가 출력 방지 (필요시 확장 가능)
        
    def _display_controls(self):
        """조작법 표시"""
        controls = []
        if len(self.items) > 1:
            controls.append("🔼🔽 W/S: 위/아래")
        controls.append("⚡ Enter: 선택")
        if self.cancellable:
            controls.append("❌ Q: 취소")
        controls.append("📋 I: 정보")
        control_text = f" | ".join(controls)
        self._println(f"{control_text:^70}")
        self._println(f"{'✦':^14} {'✧':^14} {'✦':^14} {'✧':^14} {'✦':^14}")
    
    def _get_current_line(self):
        """현재 커서 위치 라인 반환 (추정)"""
        # 간단한 라인 카운터 (정확하지 않지만 대략적인 위치)
        return 0
        
    def _update_menu_only(self):
        """메뉴 항목만 업데이트 (효율적인 화면 업데이트)"""
        # 인플레이스 업데이트가 가능하면 사용, 아니면 전체 클리어
        if self._ansi_inplace_supported and hasattr(self, '_menu_displayed') and self._menu_displayed:
            self._redraw_in_place()
        else:
            # 전체 화면 클리어
            self._clear_screen()
            
            # 제목 다시 표시
            if self.title:
                if not self.compact_mode:
                    self._println("")
                    self._println("="*60)
                    self._println(f"{self.title:^60}")
                    self._println("="*60)
                else:
                    if not hasattr(self, "_last_title") or self._last_title != self.title:
                        self._println(self.title)
                        self._last_title = self.title
            
            # 추가 콘텐츠 표시 (아스키 아트 등)
            if self.extra_content:
                self._println(self.extra_content, normalize_multi=True)
                if not self.compact_mode:
                    self._println("")
            
            # 메뉴 아이템들 다시 표시
            self._display_menu_items()
            
            # 설명과 조작법 표시
            self._display_menu_footer()
            
            # 메뉴 표시 상태 설정
            self._menu_displayed = True
        
        # 강제 플러시
        import sys
        sys.stdout.flush()
        
    def _display_menu_items(self):
        """메뉴 아이템들만 표시"""
        if not self.items:
            self._println("⚠️ 메뉴 아이템이 없습니다!")
            return
            
        for i, item in enumerate(self.items):
            if not item.enabled:
                # 비활성화된 항목
                prefix = "   " if i != self.selected_index else "👉 "
                self._println(f"{prefix}🚫 {item.text}")
            elif i == self.selected_index:
                # 선택된 항목
                if self.show_index:
                    self._println(f"👉 [{i+1}] {item.text} 👈")
                else:
                    self._println(f"👉 {item.text} 👈")
            else:
                # 일반 항목
                if self.show_index:
                    self._println(f"   [{i+1}] {item.text}")
                else:
                    self._println(f"   {item.text}")
        
    def _display_menu_footer(self):
        """메뉴 하단 정보 표시 - 화려한 버전"""
        # 설명 표시
        if self.show_description and self.items and self.selected_index < len(self.items):
            current_item = self.items[self.selected_index]
            if current_item.description:
                if not self.compact_mode:
                    self._println("")
                self._println(f"💡 {current_item.description}")
        
        # 화려한 구분선과 조작법 표시
        if not self.compact_mode:
            self._println("")
            self._println("═" * 70)
        
        # 조작법 표시 (더 예쁜 버전)
        controls = []
        if len(self.items) > 1:
            controls.append("🔼🔽 W/S: 위/아래")
        controls.append("⚡ Enter: 선택")
        if self.cancellable:
            controls.append("❌ Q: 취소")
        controls.append("📋 I: 정보")
        
        control_text = f" | ".join(controls)
        if self.compact_mode:
            # 컴팩트 모드: 왼쪽 여백을 절반 수준으로만
            # 기존 70컬럼 센터링 대신 좌측 정렬 + 소폭 패딩
            self._println("  " + control_text)
        else:
            self._println(f"{control_text:^70}")
            self._println("═" * 70)
            # 멋진 하단 장식 (일반 모드에서만)
            self._println(f"{'✦':^14} {'✧':^14} {'✦':^14} {'✧':^14} {'✦':^14}")
        
    def move_cursor(self, direction: int, silent: bool = False):
        """커서 이동 (사운드 중복 방지 강화)"""
        old_index = self.selected_index
        
        if direction > 0:  # 아래로
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
        else:  # 위로
            self.selected_index = max(0, self.selected_index - 1)
            
        # 커서가 실제로 움직였고, silent 모드가 아닐 때만 사운드 재생
        if old_index != self.selected_index and not silent:
            self.play_cursor_sound()
            
    def handle_input(self) -> MenuAction:
        """키 입력 처리 (키보드 + 게임패드 지원)"""
        # 키보드 장치가 없을 때 즉시 취소로 빠지지 않도록 안전한 폴백 제공
        if not self.keyboard:
            try:
                # 표준 입력 폴백: 한 줄 입력을 받아 간단히 매핑
                raw = input().strip()
            except Exception:
                # 입력 불가 환경에서는 잠시 대기 후 화면 유지
                import time as _t
                _t.sleep(0.1)
                return MenuAction.SPECIAL
            # 최근 키 저장 (초기 Enter 무시 보조)
            try:
                self._last_key = raw if raw else '\n'
            except Exception:
                self._last_key = None
            key = raw.lower() if raw else '\n'
            # 매핑
            if key == 'w':
                self.move_cursor(-1)
                return MenuAction.UP
            if key == 's':
                self.move_cursor(1)
                return MenuAction.DOWN
            if key == 'a':
                self.move_cursor(-1)
                return MenuAction.LEFT
            if key == 'd':
                self.move_cursor(1)
                return MenuAction.RIGHT
            if key == 'i':
                return MenuAction.INFO
            if key == 'q':
                # 메뉴가 취소 불가면 취소로 처리하지 않음
                return MenuAction.CANCEL if getattr(self, 'cancellable', True) else MenuAction.SPECIAL
            if key.isdigit():
                num = int(key) - 1
                if 0 <= num < len(self.items):
                    self.selected_index = num
                    return MenuAction.SELECT
                return MenuAction.SPECIAL
            # 빈 입력 또는 기타 입력은 Enter로 간주
            return MenuAction.SELECT
        
        # 통합 입력 관리자에서 입력 받기
        if hasattr(self.keyboard, 'wait_for_input_with_repeat'):
            # UnifiedInputManager 사용 - 블로킹 모드로 입력 대기
            key = self.keyboard.wait_for_input_with_repeat("", timeout=None).lower()
        elif hasattr(self.keyboard, 'get_input'):
            # 논블로킹 모드 - 입력이 있을 때까지 대기
            import time
            key = ""
            attempts = 0
            while not key and attempts < 100:  # 최대 2초 대기
                key = self.keyboard.get_input()
                if not key:
                    time.sleep(0.02)  # 20ms 대기
                    attempts += 1
                # Enter 키 특별 처리
                if key == '\r':
                    key = '\r'  # 유지
                    break
            key = key.lower() if key and key != '\r' else key
        else:
            # 폴백: 기존 키보드 입력
            key = self.keyboard.get_key().lower()
        
        # 최근 키 저장 (초기 Enter 무시 보조)
        try:
            self._last_key = key
        except Exception:
            self._last_key = None
        # 디버그: 입력된 키 출력
        if MENU_DEBUG:
            try:
                print(f"[MENU_DEBUG] key={repr(key)}", flush=True)
            except Exception:
                pass
        
        if key == 'w':  # 위로 (키보드/게임패드)
            self.move_cursor(-1)
            return MenuAction.UP
        elif key == 's':  # 아래로 (키보드/게임패드)
            self.move_cursor(1)
            return MenuAction.DOWN
        elif key == 'a':  # 왼쪽 (게임패드 D-패드)
            self.move_cursor(-1)
            return MenuAction.LEFT
        elif key == 'd':  # 오른쪽 (게임패드 D-패드)
            self.move_cursor(1)
            return MenuAction.RIGHT
        elif key in ['\r', '\n'] or (key and ord(key) == 13):  # Enter 키 (선택)
            if self.multi_select:
                # 멀티 선택 모드: 엔터로 체크/언체크 토글
                if self.items and self.selected_index < len(self.items):
                    current_item = self.items[self.selected_index]
                    if current_item.enabled:
                        if self.selected_index in self.selected_items:
                            # 체크 해제
                            self.selected_items.remove(self.selected_index)
                            self.play_cancel_sound()
                        else:
                            # 체크 추가 (최대 선택 수 확인)
                            if len(self.selected_items) < self.max_selections:
                                self.selected_items.add(self.selected_index)
                                self.play_confirm_sound()
                                
                                # 최대 선택 수에 도달하면 자동으로 완료
                                if len(self.selected_items) >= self.max_selections:
                                    return MenuAction.SELECT
                            else:
                                self.play_error_sound()
                        return MenuAction.SPECIAL  # 화면 업데이트 필요
                    else:
                        self.play_error_sound()
                        return MenuAction.SPECIAL
                return MenuAction.SPECIAL
            else:
                # 단일 선택 모드: 현재 아이템 선택
                if self.items and self.selected_index < len(self.items):
                    current_item = self.items[self.selected_index]
                    if current_item.enabled:
                        self.play_confirm_sound()
                        return MenuAction.SELECT
                    else:
                        self.play_error_sound()
                        return MenuAction.SPECIAL
                return MenuAction.SELECT
        elif key == ' ':  # 스페이스바 (체크박스 토글)
            if self.multi_select and self.items and self.selected_index < len(self.items):
                current_item = self.items[self.selected_index]
                if current_item.enabled:
                    if self.selected_index in self.selected_items:
                        # 체크 해제
                        self.selected_items.remove(self.selected_index)
                        self.play_cancel_sound()
                    else:
                        # 체크 추가 (최대 선택 수 확인)
                        if len(self.selected_items) < self.max_selections:
                            self.selected_items.add(self.selected_index)
                            self.play_confirm_sound()
                        else:
                            self.play_error_sound()
                    return MenuAction.SPECIAL  # 화면 업데이트 필요
                else:
                    self.play_error_sound()
                    return MenuAction.SPECIAL
            return MenuAction.SPECIAL
        elif key == 'q' and self.cancellable:  # 취소 (키보드/게임패드 B버튼)
            self.play_cancel_sound()
            return MenuAction.CANCEL
        elif key == 'f' or key == '\t':  # F키 또는 Tab키로 확정 (멀티 선택 모드)
            if self.multi_select and self.selected_items:
                self.play_confirm_sound()
                return MenuAction.SELECT
            elif self.multi_select and not self.selected_items:
                self.play_error_sound()
                return MenuAction.SPECIAL
            return MenuAction.SPECIAL
        elif key == 'i':  # 정보
            return MenuAction.INFO
        elif key.isdigit():  # 숫자 직접 입력
            num = int(key) - 1
            if 0 <= num < len(self.items):
                old_index = self.selected_index
                self.selected_index = num
                # 숫자 키로 직접 선택할 때는 소리 재생하지 않음 (중복 방지)
                # 직접 선택이므로 바로 SELECT 반환하면서 confirm 소리만 재생
                if self.items[self.selected_index].enabled:
                    self.play_confirm_sound()
                    return MenuAction.SELECT
                else:
                    self.play_error_sound()
                    return MenuAction.SPECIAL
            return MenuAction.SPECIAL
        
        return MenuAction.SPECIAL  # 기타 키
    
    def __getattr__(self, name):
        """누락된 속성에 대한 안전한 기본값 제공"""
        if name == 'is_mobile':
            return False
        elif name == 'compact_mode':
            return False
        elif name == '_ansi_inplace_supported':
            return True
        elif name == 'buffered':
            return False
        elif name == 'clear_screen':
            return True
        elif name == '_last_clear_time':
            return None
        elif name == '_last_render_line_count':
            return 0
        elif name == '_menu_displayed':
            return False
        # 기타 누락된 속성들
        return None

    def run(self) -> Optional[int]:
        """메뉴 실행"""
        if not self.items:
            return None
        # 전역 메뉴 락: 중첩 메뉴 즉시 전환 지원 (대기 없이 선점)
        global _ACTIVE_MENU
        _lock_acquired = False
        try:
            if MENU_DEBUG:
                try:
                    print(f"[MENU_DEBUG] run() start: items={len(self.items)}, cancellable={self.cancellable}, clear_screen={self.clear_screen}", flush=True)
                except Exception:
                    pass
            # 진입 시 인덱스 정규화
            try:
                if not self.items or self.selected_index < 0 or self.selected_index >= len(self.items):
                    self.selected_index = 0
            except Exception:
                self.selected_index = 0
            try:
                # 다른 메뉴가 활성화되어 있으면 즉시 해제하고 선점
                if _ACTIVE_MENU:
                    _ACTIVE_MENU = False
                _ACTIVE_MENU = True
                _lock_acquired = True
            except Exception:
                pass
            # 키보드가 없으면 안전 초기화 시도 (런타임 복구)
            if not self.keyboard:
                try:
                    from game.input_utils import UnifiedInputManager
                    self.keyboard = UnifiedInputManager()
                except Exception:
                    try:
                        from game.input_utils import KeyboardInput
                        self.keyboard = KeyboardInput()
                    except Exception:
                        self.keyboard = None
            
            # 키보드 버퍼 정리 (한글 입력 후 문제 해결)
            try:
                if sys.platform.startswith('win') and msvcrt is not None:
                    while msvcrt.kbhit():
                        msvcrt.getch()
            except:
                pass
            
            # 화면 클리어 후 첫 번째 표시
            if self.clear_screen:
                self._clear_screen()
            self.display_menu()
            # 그레이스 억제 플래그 리셋 (실행마다 초기화)
            self._grace_suppressed_once = False
            self._grace_cancel_suppressed_once = False
            
            while True:
                action = self.handle_input()
                if MENU_DEBUG:
                    try:
                        print(f"[MENU_DEBUG] action={action}", flush=True)
                    except Exception:
                        pass
                # 메뉴 진입 직후 잔상 입력으로 인한 즉시 선택/취소 방지
                try:
                    now = _t.time()
                    if now < self._ignore_enter_until:
                        # 초기 Enter만 무시, 숫자 선택은 허용
                        if action == MenuAction.SELECT and (self._last_key in ['\r', '\n']):
                            if not self._grace_suppressed_once:
                                if MENU_DEBUG:
                                    try:
                                        print(f"[MENU_DEBUG] suppressed SELECT due to grace: last_key={repr(self._last_key)} now={now:.3f} until={self._ignore_enter_until:.3f}", flush=True)
                                    except Exception:
                                        pass
                                # 키보드 버퍼 플러시로 자동 반복 입력 제거
                                try:
                                    if sys.platform.startswith('win') and msvcrt is not None:
                                        while msvcrt.kbhit():
                                            msvcrt.getch()
                                except Exception:
                                    pass
                                # 너무 바쁘게 루프 도는 것을 방지하기 위해 짧게 대기
                                try:
                                    remaining = max(0.0, self._ignore_enter_until - now)
                                    _t.sleep(min(0.05, remaining))
                                except Exception:
                                    pass
                                # 억제 직후 메뉴를 다시 그려 시각적 확실성 보장
                                try:
                                    self._menu_displayed = False
                                    self.display_menu()
                                except Exception:
                                    pass
                                self._grace_suppressed_once = True
                                continue
                            # 이미 한 번 억제한 경우에는 허용
                        if action == MenuAction.CANCEL and (self._last_key == 'q'):
                            if not self._grace_cancel_suppressed_once:
                                if MENU_DEBUG:
                                    try:
                                        print(f"[MENU_DEBUG] suppressed CANCEL due to grace: last_key={repr(self._last_key)} now={now:.3f} until={self._ignore_enter_until:.3f}", flush=True)
                                    except Exception:
                                        pass
                                try:
                                    if sys.platform.startswith('win') and msvcrt is not None:
                                        while msvcrt.kbhit():
                                            msvcrt.getch()
                                except Exception:
                                    pass
                                try:
                                    remaining = max(0.0, self._ignore_enter_until - now)
                                    _t.sleep(min(0.05, remaining))
                                except Exception:
                                    pass
                                try:
                                    self._menu_displayed = False
                                    self.display_menu()
                                except Exception:
                                    pass
                                self._grace_cancel_suppressed_once = True
                                continue
                except Exception:
                    pass
                
                if action in [MenuAction.UP, MenuAction.DOWN]:
                    # 커서 이동 -> 간단한 상태 표시만 (메뉴 다시 그리지 않음)
                    self._update_selection_inline()
                    
                elif action == MenuAction.SPECIAL:
                    # 특별 액션 (체크박스 토글 등) -> 전체 메뉴 다시 그리기
                    self._menu_displayed = False
                    self.display_menu()
                    
                elif action == MenuAction.INFO:
                    # 정보 보기 후 메뉴 다시 표시
                    try:
                        self.show_item_info()
                    except Exception:
                        pass
                    self._menu_displayed = False
                    self.display_menu()
                    
                elif action == MenuAction.SELECT:
                    if self.multi_select:
                        # 멀티 선택 모드: 선택된 인덱스들의 리스트 반환
                        if MENU_DEBUG:
                            try:
                                print(f"[MENU_DEBUG] return SELECT multi={list(self.selected_items)}", flush=True)
                            except Exception:
                                pass
                        # 시스템 로그: 멀티 선택 결과
                        try:
                            if _menu_log_system:
                                _menu_log_system("메뉴선택", "멀티 선택 완료", {
                                    "제목": getattr(self, 'title', ''),
                                    "선택목록": list(self.selected_items)
                                })
                        except Exception:
                            pass
                        return list(self.selected_items)
                    else:
                        # 단일 선택 모드: 현재 인덱스 반환
                        current_item = self.items[self.selected_index]
                        if current_item.enabled:
                            # 액션이 있으면 실행
                            if current_item.action:
                                try:
                                    result = current_item.action()
                                    if result is not None:
                                        if MENU_DEBUG:
                                            try:
                                                print(f"[MENU_DEBUG] return action-result={result}", flush=True)
                                            except Exception:
                                                pass
                                        # 시스템 로그: 액션 반환값
                                        try:
                                            if _menu_log_system:
                                                _menu_log_system("메뉴선택", "액션 결과 반환", {
                                                    "제목": getattr(self, 'title', ''),
                                                    "반환값": result
                                                })
                                        except Exception:
                                            pass
                                        return result
                                except Exception as e:
                                    print(f"⚠️ 액션 실행 오류: {e}")
                                    self.keyboard.get_key() if self.keyboard else None
                            # 시스템 로그: 일반 선택
                            try:
                                if _menu_log_system:
                                    _menu_log_system("메뉴선택", "항목 선택", {
                                        "제목": getattr(self, 'title', ''),
                                        "인덱스": self.selected_index,
                                        "텍스트": getattr(current_item, 'text', '')
                                    })
                            except Exception:
                                pass
                            if MENU_DEBUG:
                                try:
                                    print(f"[MENU_DEBUG] return selected_index={self.selected_index}", flush=True)
                                except Exception:
                                    pass
                            return self.selected_index
                        
                elif action == MenuAction.CANCEL:
                    if MENU_DEBUG:
                        try:
                            print(f"[MENU_DEBUG] return CANCEL(None)", flush=True)
                        except Exception:
                            pass
                    # 시스템 로그: 취소
                    try:
                        if _menu_log_system:
                            _menu_log_system("메뉴취소", "사용자가 메뉴를 취소함", {
                                "제목": getattr(self, 'title', ''),
                            })
                    except Exception:
                        pass
                    return None  # Q 키로 취소할 때 None 반환
        finally:
            # 전역 메뉴 락 안전 해제 (예외/빠른 반환 포함)
            try:
                if _lock_acquired:
                    _ACTIVE_MENU = False
            except Exception:
                pass
    # 함수 종료 시 전역 메뉴 락 해제
        
                
    def show_item_info(self):
        """선택된 아이템의 상세 정보 표시"""
        if not self.items or self.selected_index >= len(self.items):
            return
            
        item = self.items[self.selected_index]
        if self.clear_screen:
            self._clear_screen()
        else:
            print("\n" + "─" * 60)
        
        print(f"\n📋 {item.text} - 상세 정보\n")
        print("=" * 40)
        
        if item.description:
            print(f"\n📝 설명: {item.description}")
        
        if item.value is not None:
            print(f"💎 값: {item.value}")
            
        print(f"\n🔧 상태: {'활성화' if item.enabled else '비활성화'}")
        
        print(f"\n{'─' * 40}")
        print("🔙 아무 키나 눌러 돌아가기... (자세히 읽어보세요)")
        
        if self.keyboard:
            self.keyboard.wait_for_key("계속하려면 아무 키나 누르세요...")

# 편의 함수들
def create_simple_menu(title: str, options: List[str], descriptions: List[str] = None,
                      audio_manager=None, keyboard=None, clear_screen: bool = True, 
                      extra_content: str = "", cancellable: bool = True,
                      ignore_initial_enter_ms: float = 0.2) -> CursorMenu:
    """간단한 메뉴 생성"""
    menu = CursorMenu(title, options, descriptions, audio_manager, keyboard, 
                     cancellable=cancellable, clear_screen=clear_screen, extra_content=extra_content,
                     ignore_initial_enter_ms=ignore_initial_enter_ms)
    return menu

def create_character_selection_menu(characters: List[Any], audio_manager=None, keyboard=None) -> CursorMenu:
    """캐릭터 선택 메뉴 생성"""
    menu = CursorMenu(audio_manager, keyboard)
    menu.set_title("캐릭터 선택")
    
    items = []
    for char in characters:
        # 캐릭터 정보를 포함한 텍스트 생성
        char_text = f"{char.name} (Lv.{char.level})"
        char_desc = f"HP: {char.hp}/{char.max_hp} | ATK: {char.attack} | DEF: {char.defense}"
        items.append(MenuItem(char_text, description=char_desc, value=char))
    
    menu.set_items(items)
    return menu

def create_yes_no_menu(question: str, audio_manager=None, keyboard=None) -> CursorMenu:
    """예/아니오 메뉴 생성"""
    menu = CursorMenu(audio_manager, keyboard)
    menu.set_title(question)
    menu.show_index = False
    
    items = [
        MenuItem("✅ 예", description="확인합니다", value=True),
        MenuItem("❌ 아니오", description="취소합니다", value=False)
    ]
    
    menu.set_items(items)
    return menu

def create_character_detail_menu(title: str, characters: List[Any], audio_manager=None, keyboard=None) -> CursorMenu:
    """캐릭터 선택 메뉴 생성 (상세 정보 포함)"""
    menu = CursorMenu(title, audio_manager=audio_manager, keyboard=keyboard, clear_screen=True)
    
    # 캐릭터 옵션과 기본 설명 생성
    options = [f"{char.name} ({char.character_class})" for char in characters]
    options.append("취소")
    
    descriptions = [f"레벨 {char.level}" for char in characters]
    descriptions.append("선택을 취소합니다")
    
    # 기존 메뉴 시스템과 호환되도록 설정
    menu.options = options
    menu.descriptions = descriptions
    menu.characters = characters  # 캐릭터 데이터 저장
    
    # MenuItem 객체로 생성
    items = []
    for i, char in enumerate(characters):
        items.append(MenuItem(options[i], description=descriptions[i], value=char))
    items.append(MenuItem("취소", description="선택을 취소합니다", value=None))
    
    menu.set_items(items)
    
    # 커스텀 디스플레이 메서드 오버라이드
    original_display_footer = menu._display_menu_footer
    
    def custom_display_footer():
        """캐릭터 상세 정보를 포함한 푸터 표시"""
        # 현재 선택된 캐릭터의 상세 정보 표시
        if menu.selected_index < len(characters):
            char = characters[menu.selected_index]
            
            print(f"\n{'─' * 50}")
            print(f"📋 {char.name} 상세 정보")
            print(f"{'─' * 50}")
            print(f"🎭 직업: {char.character_class}")
            print(f"⭐ 레벨: {char.level}")
            print(f"💝 HP: {char.current_hp}/{char.max_hp}")
            print(f"💙 MP: {char.current_mp}/{char.max_mp}")
            print(f"⚔️ 공격력: {char.physical_attack}")
            print(f"🛡️ 방어력: {char.physical_defense}")
            print(f"✨ 마법력: {char.magic_attack}")
            print(f"🔮 마법방어: {char.magic_defense}")
            print(f"🏃 속도: {char.speed}")
            print(f"💰 BRV: {char.brave_points}")
            
            # 장착 장비 정보
            print(f"\n🎒 장착 장비:")
            weapon = getattr(char, 'equipped_weapon', None)
            armor = getattr(char, 'equipped_armor', None)
            accessory = getattr(char, 'equipped_accessory', None)
            
            print(f"  🗡️ 무기: {weapon.name if weapon else '없음'}")
            print(f"  🛡️ 방어구: {armor.name if armor else '없음'}")
            print(f"  💍 장신구: {accessory.name if accessory else '없음'}")
        else:
            # 취소 선택 시
            print(f"\n💡 {descriptions[menu.selected_index]}")
        
        # 조작법 표시
        print(f"\n{'─' * 50}")
        controls = []
        if len(menu.options) > 1:
            controls.append("W/S: 위/아래")
        controls.append("Enter: 선택")
        controls.append("Q: 취소")
        
        print(f"{' | '.join(controls)}")
    
    menu._display_menu_footer = custom_display_footer
    return menu

# 테스트용 함수
def demo_cursor_menu():
    """커서 메뉴 데모"""
    try:
        # 메인 메뉴
        options = [
            "🚀 게임 시작",
            "📊 캐릭터 상태", 
            "🎒 인벤토리",
            "⚙️ 설정",
            "❌ 게임 종료"
        ]
        
        descriptions = [
            "새로운 모험을 시작합니다",
            "캐릭터들의 상태를 확인합니다",
            "아이템과 장비를 관리합니다", 
            "게임 설정을 변경합니다",
            "게임을 종료합니다"
        ]
        
        menu = create_simple_menu("메인 메뉴", options, descriptions)
        result = menu.run()
        
        if result == -1:
            print("메뉴가 취소되었습니다.")
        else:
            print(f"선택됨: {options[result]}")
            
        # 예/아니오 메뉴 테스트
        if result != -1:
            yn_menu = create_yes_no_menu("정말로 실행하시겠습니까?")
            yn_result = yn_menu.run()
            
            if yn_result != -1:
                selected_item = yn_menu.items[yn_result]
                print(f"답변: {'예' if selected_item.value else '아니오'}")
            
    except Exception as e:
        print(f"❌ 데모 실행 오류: {e}")

if __name__ == "__main__":
    demo_cursor_menu()
