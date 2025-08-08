#!/usr/bin/env python3
"""
통합 메뉴 시스템 - FFVII 스타일 커서 네비게이션
Dawn of Stellar의 모든 메뉴에 적용되는 통합 메뉴 시스템
"""

import os
import sys
from typing import List, Optional, Callable, Dict, Any
from enum import Enum
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
                 buffered: bool = False):
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
        self._ansi_inplace_supported = self._detect_ansi_support()
        self._menu_displayed = False
        
        # 모바일 환경 감지 (Flutter 클라이언트나 HTTP 모드)
        self.is_mobile = (os.getenv('MOBILE_MODE') == '1' or 
                         os.getenv('HTTP_MODE') == '1' or
                         os.getenv('FLUTTER_MODE') == '1')
        
        # 모바일에서는 인플레이스 업데이트 비활성화 (중복 표시 방지)
        if self.is_mobile:
            self._ansi_inplace_supported = False
            self.compact_mode = True

        # 옵션 -> MenuItem 자동 생성
        if options:
            temp_items: List[MenuItem] = []
            for i, option in enumerate(options):
                desc = descriptions[i] if descriptions and i < len(descriptions) else ""
                temp_items.append(MenuItem(option, description=desc))
            self.set_items(temp_items)

    def _println(self, text: str = "", normalize_multi: bool = False):
        """크로스플랫폼 줄바꿈 출력. Windows에서 CRLF 보장.
        normalize_multi=True일 때는 문자열 내부의 모든 \n을 CRLF로 변환.
        """
        try:
            if os.name == 'nt':
                t = text or ""
                if normalize_multi and t:
                    # 1) 모든 라인 엔딩을 LF로 통일
                    t = t.replace('\r\n', '\n').replace('\r', '\n')
                    # 2) 컴팩트 모드에서는 연속 빈 줄을 1줄로 축소
                    if self.compact_mode:
                        lines = t.split('\n')
                        collapsed = []
                        prev_blank = False
                        for ln in lines:
                            blank = (ln.strip() == '')
                            if blank and prev_blank:
                                continue
                            collapsed.append(ln)
                            prev_blank = blank
                        t = '\n'.join(collapsed)
                    # 3) LF를 CRLF로 변환 후 최종 CRLF 추가
                    t = t.replace('\n', '\r\n')
                    sys.stdout.write(t + "\r\n")
                else:
                    sys.stdout.write(t + "\r\n")
            else:
                print(text)
        except Exception:
            # 문제가 생기면 일반 print로 폴백
            print(text)
        
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
        """화면 클리어 - 개선된 버전 + 디바운싱"""
        import time
        
        # 디바운싱: 0.1초 이내 중복 클리어 방지
        current_time = time.time()
        if hasattr(self, '_last_clear_time'):
            if current_time - self._last_clear_time < 0.1:
                return  # 너무 빈번한 클리어 방지
        self._last_clear_time = current_time
        
        # 버퍼 모드에서는 ANSI 클리어 + 홈 커서 토큰만 보냄
        if self.buffered:
            try:
                # ANSI 시퀀스로 화면 완전 클리어
                print("\x1b[2J\x1b[H", end='', flush=True)
            except Exception:
                pass
            return
        
        # 표준 터미널 클리어
        try:
            # Windows에서 더 강력한 클리어
            if os.name == 'nt':
                # ANSI 시퀀스 시도 (Windows Terminal, ConEmu 등)
                if 'WT_SESSION' in os.environ or 'ANSICON' in os.environ:
                    print("\x1b[2J\x1b[H", end='', flush=True)
                else:
                    # CMD 기본 cls
                    os.system('cls')
                    print("\x1b[H", end='', flush=True)  # 커서 홈으로
            else:
                # Unix/Linux
                print("\x1b[2J\x1b[H", end='', flush=True)
        except:
            # 폴백: 기본 시스템 클리어
            os.system('cls' if os.name == 'nt' else 'clear')

    # ====== 신규: ANSI 지원 감지 & 라인 구성/인플레이스 렌더 ======
    def _detect_ansi_support(self) -> bool:
        """터미널이 기본 ANSI 시퀀스를 지원하는지 간단 감지"""
        if os.name != 'nt':
            return True
        # Windows: WT_SESSION(Windows Terminal) 또는 ANSICON / ConEmu 등
        if 'WT_SESSION' in os.environ or 'ANSICON' in os.environ:
            return True
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
            extra = self.extra_content.replace('\r\n','\n').replace('\r','\n')
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
                if not item.enabled:
                    prefix = "   " if i != self.selected_index else "👉 "
                    line = f"{prefix}🚫 {item.text}"
                elif i == self.selected_index:
                    line = f"👉 [{i+1}] {item.text} 👈" if self.show_index else f"👉 {item.text} 👈"
                else:
                    line = f"   [{i+1}] {item.text}" if self.show_index else f"   {item.text}"
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
        """ANSI 커서 이동을 사용한 인플레이스 갱신 (중복 누적 제거)"""
        if not self._ansi_inplace_supported or not sys.stdout.isatty():
            # 폴백: 전체 재표시
            self._update_menu_only()
            return
        new_lines = self._compose_menu_lines()
        # 커서를 이전 렌더 줄 수 만큼 위로 이동
        if self._last_render_line_count > 0:
            # A: 위로 이동, H: 필요시 홈이지만 여기선 A만
            sys.stdout.write(f"\x1b[{self._last_render_line_count}F")
        # 각 줄 지우고 새 내용 출력
        common = min(self._last_render_line_count, len(new_lines))
        for i in range(common):
            sys.stdout.write("\x1b[2K" + new_lines[i] + ("\r\n" if i < len(new_lines)-1 else ""))
        # 추가 새 줄
        if len(new_lines) > common:
            for i in range(common, len(new_lines)):
                sys.stdout.write("\x1b[2K" + new_lines[i] + ("\r\n" if i < len(new_lines)-1 else ""))
        # 남은 이전 줄 지우기
        if self._last_render_line_count > len(new_lines):
            for _ in range(self._last_render_line_count - len(new_lines)):
                sys.stdout.write("\x1b[2K\r\n")
        sys.stdout.flush()
        self._last_render_line_count = len(new_lines)

        
    def display_menu(self):
        """메뉴 화면 표시"""
        self._clear_screen()
        lines = self._compose_menu_lines()
        self._print_lines(lines)
        self._last_render_line_count = len(lines)
        self._menu_displayed = True
    
    def _update_selection_inline(self):
        """선택 항목만 인라인으로 표시 (아스키 아트 보존용) - 깜빡임 방지"""
        # 인플레이스 ANSI 재렌더 (지원시)
        if self._ansi_inplace_supported:
            self._redraw_in_place()
        else:
            self._update_menu_only()
        
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
        if not self.keyboard:
            return MenuAction.CANCEL
        
        # 통합 입력 관리자에서 입력 받기
        if hasattr(self.keyboard, 'wait_for_input_with_repeat'):
            # UnifiedInputManager 사용 - 블로킹 모드로 입력 대기
            key = self.keyboard.wait_for_input_with_repeat("", timeout=None).lower()
        elif hasattr(self.keyboard, 'get_input'):
            # 논블로킹 모드 - 입력이 있을 때까지 대기
            import time
            key = ""
            while not key:
                key = self.keyboard.get_input().lower()
                if not key:
                    time.sleep(0.05)  # 50ms 대기
        else:
            # 폴백: 기존 키보드 입력
            key = self.keyboard.get_key().lower()
        
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
        elif key == '\r' or key == '\n' or key == ' ':  # 엔터 또는 스페이스 (선택)
            if self.items and self.selected_index < len(self.items):
                current_item = self.items[self.selected_index]
                if current_item.enabled:
                    self.play_confirm_sound()
                    return MenuAction.SELECT
                else:
                    self.play_error_sound()
                    return MenuAction.SPECIAL
            return MenuAction.SELECT
        elif key == 'q' and self.cancellable:  # 취소 (키보드/게임패드 B버튼)
            self.play_cancel_sound()
            return MenuAction.CANCEL
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
                return MenuAction.SELECT
        
        return MenuAction.SPECIAL  # 기타 키
    
    def run(self) -> Optional[int]:
        """메뉴 실행"""
        if not self.items:
            return None
        
        # 첫 번째 표시
        self.display_menu()
        
        while True:
            action = self.handle_input()
            
            if action in [MenuAction.UP, MenuAction.DOWN]:
                # 커서 이동 -> 인플레이스 갱신 시도
                self._update_selection_inline()
                
            elif action == MenuAction.SELECT:
                current_item = self.items[self.selected_index]
                if current_item.enabled:
                    # 액션이 있으면 실행
                    if current_item.action:
                        try:
                            result = current_item.action()
                            if result is not None:
                                return result
                        except Exception as e:
                            print(f"⚠️ 액션 실행 오류: {e}")
                            self.keyboard.get_key() if self.keyboard else None
                    return self.selected_index
                    
            elif action == MenuAction.CANCEL:
                return None  # Q 키로 취소할 때 None 반환
                
            elif action == MenuAction.INFO:
                self.show_item_info()
                # 정보 화면에서 돌아온 후 메뉴 다시 표시
                self._menu_displayed = False
                self.display_menu()
                
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
                      extra_content: str = "") -> CursorMenu:
    """간단한 메뉴 생성"""
    menu = CursorMenu(title, options, descriptions, audio_manager, keyboard, 
                     clear_screen=clear_screen, extra_content=extra_content)
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
