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
                 clear_screen: bool = True):
        """메뉴 초기화"""
        try:
            if not audio_manager:
                from game.audio_system import get_audio_manager
                self.audio_manager = get_audio_manager()
            else:
                self.audio_manager = audio_manager
                
            if not keyboard:
                from game.input_utils import KeyboardInput
                self.keyboard = KeyboardInput()
            else:
                self.keyboard = keyboard
        except ImportError:
            print("⚠️ 오디오 시스템을 불러올 수 없습니다.")
            self.audio_manager = None
            self.keyboard = None
            
        self.selected_index = 0
        self.items = []
        self.title = title
        self.extra_content = extra_content  # 추가 콘텐츠 (파티 정보 등)
        self.show_description = True
        self.show_index = True
        # 쿨다운 시스템 제거 - input_utils.py 중복 제거로 인해 불필요
        self.cancellable = cancellable
        self.clear_screen = clear_screen  # 화면 지우기 옵션
        
        # 옵션들이 제공되면 자동으로 MenuItem 생성
        if options:
            items = []
            for i, option in enumerate(options):
                desc = descriptions[i] if descriptions and i < len(descriptions) else ""
                items.append(MenuItem(option, description=desc))
            self.set_items(items)
        
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
        """화면 클리어"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_menu(self):
        """메뉴 화면 표시 - 아스키 아트 보존 버전"""
        # clear_screen이 False인 경우, 아스키 아트 보존을 위해 업데이트 방식 변경
        if not self.clear_screen:
            # 첫 표시인 경우에만 메뉴 표시
            if not hasattr(self, '_menu_displayed') or not self._menu_displayed:
                # 제목 표시 (간소화)
                if self.title:
                    print(f"\n{self.title}\n")
                
                # 추가 콘텐츠 표시 (파티 정보 등) - 처음 한 번만
                if self.extra_content:
                    print(self.extra_content)
                    print()
                
                # 메뉴 아이템들 표시
                self._display_menu_items()
                
                # 설명과 조작법 표시
                self._display_menu_footer()
                
                # 메뉴가 표시되었음을 표시
                self._menu_displayed = True
            else:
                # 이미 표시된 경우, 현재 선택만 업데이트 (인라인)
                self._update_selection_inline()
            return
        
        # clear_screen이 True인 경우, 기존 방식 유지
        # 첫 표시가 아닌 경우, 메뉴만 업데이트
        if hasattr(self, '_menu_displayed') and self._menu_displayed:
            self._update_menu_only()
            return
            
        # 첫 표시인 경우에만 전체 화면 처리
        if self.clear_screen:
            self._clear_screen()
        
        # 제목 표시
        if self.title:
            print(f"\n{self.title}\n")
            print()
        
        # 추가 콘텐츠 표시 (파티 정보 등) - 처음 한 번만
        if self.extra_content:
            print(self.extra_content)
            print()
        
        # 메뉴 아이템들 표시
        self._display_menu_items()
        
        # 설명과 조작법 표시
        self._display_menu_footer()
        
        # 메뉴가 표시되었음을 표시
        self._menu_displayed = True
    
    def _update_selection_inline(self):
        """선택 항목만 인라인으로 업데이트 (아스키 아트 보존용)"""
        try:
            # 커서를 메뉴 시작 위치로 이동하여 메뉴 부분만 다시 그리기
            print("\033[2K", end='')  # 현재 라인 클리어
            
            # 메뉴 아이템들만 다시 표시
            self._display_menu_items()
            
            # 설명 부분 업데이트
            if self.show_description and self.items and self.selected_index < len(self.items):
                current_item = self.items[self.selected_index]
                if current_item.description:
                    print(f"\n💡 {current_item.description}")
            
            # 조작법 다시 표시
            self._display_menu_footer()
            
        except Exception as e:
            # 인라인 업데이트 실패 시 전체 다시 그리기
            self._display_full_menu()
    
    def _display_full_menu(self):
        """전체 메뉴 다시 표시 (폴백용)"""
        if not self.clear_screen:
            # 아스키 아트 보존 모드에서는 메뉴 부분만 다시 그리기
            print(f"\n{self.title}\n" if self.title else "")
            self._display_menu_items()
            self._display_menu_footer()
        else:
            # 일반 모드에서는 전체 화면 클리어 후 다시 그리기
            self.display_menu()
        
    def _get_current_line(self):
        """현재 커서 위치 라인 반환 (추정)"""
        # 간단한 라인 카운터 (정확하지 않지만 대략적인 위치)
        return 0
        
    def _update_menu_only(self):
        """메뉴 항목만 업데이트 (clear_screen=True인 경우만 사용)"""
        # 전체 화면 클리어
        self._clear_screen()
        
        # 제목 다시 표시
        if self.title:
            print(f"\n{self.title}\n")
            print()
        
        # 추가 콘텐츠 표시 (파티 정보 등)
        if self.extra_content:
            print(self.extra_content)
            print()
        
        # 메뉴 아이템들 다시 표시
        self._display_menu_items()
        
        # 설명과 조작법 표시
        self._display_menu_footer()
        
    def _display_menu_items(self):
        """메뉴 아이템들만 표시"""
        for i, item in enumerate(self.items):
            if not item.enabled:
                # 비활성화된 항목
                prefix = "   " if i != self.selected_index else "👉 "
                print(f"{prefix}🚫 {item.text}")
            elif i == self.selected_index:
                # 선택된 항목
                if self.show_index:
                    print(f"👉 [{i+1}] {item.text} 👈")
                else:
                    print(f"👉 {item.text} 👈")
            else:
                # 일반 항목
                if self.show_index:
                    print(f"   [{i+1}] {item.text}")
                else:
                    print(f"   {item.text}")
        
    def _display_menu_footer(self):
        """메뉴 하단 정보 표시 - 화려한 버전"""
        # 설명 표시
        if self.show_description and self.items and self.selected_index < len(self.items):
            current_item = self.items[self.selected_index]
            if current_item.description:
                print(f"\n💡 {current_item.description}")
        
        # 화려한 구분선과 조작법 표시
        print(f"\n{'═' * 70}")
        
        # 조작법 표시 (더 예쁜 버전)
        controls = []
        if len(self.items) > 1:
            controls.append("🔼🔽 W/S: 위/아래")
        controls.append("⚡ Enter: 선택")
        if self.cancellable:
            controls.append("❌ Q: 취소")
        controls.append("📋 I: 정보")
        
        control_text = f" | ".join(controls)
        print(f"{control_text:^70}")
        print(f"{'═' * 70}")
        
        # 멋진 하단 장식
        print(f"{'✦':^14} {'✧':^14} {'✦':^14} {'✧':^14} {'✦':^14}")
        
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
        """키 입력 처리"""
        if not self.keyboard:
            return MenuAction.CANCEL
            
        key = self.keyboard.get_key().lower()
        
        if key == 'w':  # 위로
            self.move_cursor(-1)
            return MenuAction.UP
        elif key == 's':  # 아래로
            self.move_cursor(1)
            return MenuAction.DOWN
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
        elif key == 'q' and self.cancellable:  # 취소
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
                # 커서가 이동한 경우에만 메뉴 업데이트
                self._update_menu_only()
                
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
