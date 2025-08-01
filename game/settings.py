"""
게임 설정 관리 시스템
"""

import json
import os
from typing import Dict, Any
from pathlib import Path


class GameSettings:
    """게임 설정 관리자"""
    
    def __init__(self):
        self.settings_file = Path("game_settings.json")
        self.default_settings = {
            "tutorial": {
                "tutorial_completed": False,
                "skip_intro": False,
                "show_advanced_tips": True,
                "auto_proceed": False
            },
            "display": {
                "screen_width": 120,
                "map_width": 100,
                "map_height": 25,
                "show_coordinates": False,
                "color_enabled": True
            },
            "gameplay": {
                "auto_save": True,
                "save_interval": 5,  # 분
                "difficulty": "normal",  # easy, normal, hard
                "fast_combat": False,
                "skip_animations": False
            },
            "audio": {
                "sound_enabled": True,
                "music_enabled": True,
                "volume": 50
            },
            "debug": {
                "debug_mode": False,
                "show_enemy_hp": False,
                "infinite_mp": False,
                "god_mode": False
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 기본값과 병합 (새로운 설정 항목 추가 대응)
                settings = self.default_settings.copy()
                for category, values in loaded_settings.items():
                    if category in settings:
                        settings[category].update(values)
                    else:
                        settings[category] = values
                
                return settings
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"설정 파일 로드 실패: {e}")
                return self.default_settings.copy()
        else:
            return self.default_settings.copy()
    
    def save_settings(self):
        """설정 파일 저장"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"설정 파일 저장 실패: {e}")
    
    def get(self, category: str, key: str, default=None):
        """설정값 가져오기"""
        return self.settings.get(category, {}).get(key, default)
    
    def set(self, category: str, key: str, value: Any):
        """설정값 변경"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_settings()
    
    def is_tutorial_completed(self) -> bool:
        """튜토리얼 완료 여부"""
        return self.get("tutorial", "tutorial_completed", False)
    
    def set_tutorial_completed(self, completed: bool = True):
        """튜토리얼 완료 설정"""
        self.set("tutorial", "tutorial_completed", completed)
    
    def should_skip_intro(self) -> bool:
        """인트로 스킵 여부"""
        return self.get("tutorial", "skip_intro", False)
    
    def should_show_advanced_tips(self) -> bool:
        """고급 팁 표시 여부"""
        return self.get("tutorial", "show_advanced_tips", True)
    
    def reset_tutorial(self):
        """튜토리얼 설정 초기화"""
        self.set("tutorial", "tutorial_completed", False)
        self.set("tutorial", "skip_intro", False)
    
    def toggle_setting(self, category: str, key: str):
        """불린 설정 토글"""
        current_value = self.get(category, key, False)
        self.set(category, key, not current_value)
        return not current_value
    
    def show_settings_menu(self):
        """설정 메뉴 표시 - 커서 방식"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            while True:
                # 현재 설정 상태로 옵션 텍스트 생성
                options = [
                    f"📚 튜토리얼 완료 상태: {'✅' if self.is_tutorial_completed() else '❌'}",
                    f"⏭️ 인트로 스킵: {'✅' if self.should_skip_intro() else '❌'}",
                    f"💡 고급 팁 표시: {'✅' if self.should_show_advanced_tips() else '❌'}",
                    f"🖥️ 화면 너비: {self.get('display', 'screen_width')}",
                    f"📐 맵 크기: {self.get('display', 'map_width')}x{self.get('display', 'map_height')}",
                    f"🎨 색상 활성화: {'✅' if self.get('display', 'color_enabled') else '❌'}",
                    f"💾 자동 저장: {'✅' if self.get('gameplay', 'auto_save') else '❌'}",
                    f"⚡ 난이도: {self.get('gameplay', 'difficulty')}",
                    f"🚀 빠른 전투: {'✅' if self.get('gameplay', 'fast_combat') else '❌'}",
                    f"🔊 오디오 설정",
                    "🤔 튜토리얼 초기화",
                    "❌ 돌아가기"
                ]
                
                descriptions = [
                    "튜토리얼 완료 여부를 변경합니다",
                    "게임 시작 시 인트로를 건너뜁니다",
                    "고급 팁과 도움말을 표시합니다",
                    "게임 화면의 너비를 조정합니다 (80-200)",
                    "던전 맵의 크기를 조정합니다",
                    "화면 색상 표시를 켜거나 끕니다",
                    "자동 저장 기능을 켜거나 끕니다",
                    "게임 난이도를 조정합니다 (쉬움/보통/어려움)",
                    "전투 애니메이션을 빠르게 합니다",
                    "사운드와 음악 설정을 변경합니다",
                    "모든 튜토리얼 진행도를 초기화합니다",
                    "설정 메뉴를 나갑니다"
                ]
                
                menu = create_simple_menu("⚙️ 게임 설정", options, descriptions)
                result = menu.run()
                
                if result == -1 or result == 11:  # 돌아가기
                    break
                elif result == 0:  # 튜토리얼 완료 상태
                    self.toggle_setting("tutorial", "tutorial_completed")
                    print("✅ 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 1:  # 인트로 스킵
                    self.toggle_setting("tutorial", "skip_intro")
                    print("✅ 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 2:  # 고급 팁 표시
                    self.toggle_setting("tutorial", "show_advanced_tips")
                    print("✅ 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 3:  # 화면 설정
                    self._show_display_settings()
                elif result == 4:  # 오디오 설정
                    self._show_audio_settings()
                elif result == 5:  # 색상 활성화
                    self.toggle_setting("display", "color_enabled")
                    print("✅ 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 6:  # 자동 저장
                    self.toggle_setting("gameplay", "auto_save")
                    print("✅ 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 7:  # 난이도
                    self._change_difficulty()
                elif result == 8:  # 빠른 전투
                    self.toggle_setting("gameplay", "fast_combat")
                    print("✅ 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 9:  # 튜토리얼 초기화
                    self._reset_tutorials()
                elif result == 10:  # 돌아가기
                    break
                    
        except ImportError:
            # 폴백: 기존 텍스트 메뉴
            self._show_settings_menu_fallback()
    
    def _change_screen_width(self):
        """화면 너비 변경"""
        try:
            from .input_utils import KeyboardInput
            keyboard = KeyboardInput()
            
            print("새 화면 너비 (80-200): ", end='', flush=True)
            width_str = keyboard.get_string_input()
            
            if width_str:
                width = int(width_str)
                if 80 <= width <= 200:
                    self.set("display", "screen_width", width)
                    print("✅ 화면 너비가 변경되었습니다.")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
                else:
                    print("❌ 유효한 범위가 아닙니다.")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
            else:
                print("❌ 입력이 취소되었습니다.")
                keyboard.wait_for_key("아무 키나 눌러 계속...")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            keyboard.wait_for_key("아무 키나 눌러 계속...")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            try:
                keyboard.wait_for_key("아무 키나 눌러 계속...")
            except:
                pass
    
    def _change_map_size(self):
        """맵 크기 변경"""
        try:
            from .input_utils import KeyboardInput
            keyboard = KeyboardInput()
            
            print("맵 너비 (60-120): ", end='', flush=True)
            width_str = keyboard.get_string_input()
            
            if not width_str:
                print("❌ 입력이 취소되었습니다.")
                keyboard.wait_for_key("아무 키나 눌러 계속...")
                return
                
            print("맵 높이 (15-30): ", end='', flush=True)
            height_str = keyboard.get_string_input()
            
            if not height_str:
                print("❌ 입력이 취소되었습니다.")
                keyboard.wait_for_key("아무 키나 눌러 계속...")
                return
            
            width = int(width_str)
            height = int(height_str)
            
            if 60 <= width <= 120 and 15 <= height <= 30:
                self.set("display", "map_width", width)
                self.set("display", "map_height", height)
                print("✅ 맵 크기가 변경되었습니다.")
                keyboard.wait_for_key("아무 키나 눌러 계속...")
            else:
                print("❌ 유효한 범위가 아닙니다.")
                keyboard.wait_for_key("아무 키나 눌러 계속...")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            try:
                keyboard.wait_for_key("아무 키나 눌러 계속...")
            except:
                pass
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            try:
                keyboard.wait_for_key("아무 키나 눌러 계속...")
            except:
                pass
    
    def _change_difficulty(self):
        """난이도 변경"""
        from .cursor_menu_system import create_simple_menu
        
        try:
            # config.py에서 난이도 설정 가져오기
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from config import GameConfig
            
            config = GameConfig()
            difficulties = config.get_all_difficulties()
            
            # 난이도별 옵션과 설명 생성
            difficulty_options = []
            difficulty_descriptions = []
            
            for diff_key in difficulties:
                diff_info = config.get_difficulty_info(diff_key)
                difficulty_options.append(f"{diff_info['color']} {diff_info['name']}")
                difficulty_descriptions.append(diff_info['description'])
            
            difficulty_options.append("❌ 취소")
            difficulty_descriptions.append("난이도 변경을 취소합니다")
            
            diff_menu = create_simple_menu("난이도 선택", difficulty_options, difficulty_descriptions)
            diff_result = diff_menu.run()
            
            if diff_result == -1 or diff_result >= len(difficulties):
                return
            
            # 선택된 난이도 저장
            selected_difficulty = list(difficulties)[diff_result]
            self.set("gameplay", "difficulty", selected_difficulty)
            
            print(f"✅ 난이도가 '{difficulty_options[diff_result]}'로 변경되었습니다.")
            self._wait_for_key()
            
        except Exception as e:
            print(f"❌ 난이도 변경 중 오류 발생: {e}")
            # 폴백: 기존 방식
            difficulty_options = ["🟢 쉬움", "🟡 보통", "🔴 어려움", "❌ 취소"]
            difficulty_descriptions = [
                "적 HP와 공격력이 낮습니다",
                "기본 난이도입니다",
                "적 HP와 공격력이 높습니다",
                "난이도 변경을 취소합니다"
            ]
            
            diff_menu = create_simple_menu("난이도 선택", difficulty_options, difficulty_descriptions)
            diff_result = diff_menu.run()
            
            if diff_result == 0:
                self.set("gameplay", "difficulty", "평온")
            elif diff_result == 1:
                self.set("gameplay", "difficulty", "보통")
            elif diff_result == 2:
                self.set("gameplay", "difficulty", "도전")
            else:
                return
                
            print("✅ 난이도가 변경되었습니다.")
            self._wait_for_key()
    
    def _reset_tutorials(self):
        """튜토리얼 초기화"""
        from .cursor_menu_system import create_yes_no_menu
        
        confirm_menu = create_yes_no_menu("튜토리얼을 초기화하시겠습니까?")
        confirm_result = confirm_menu.run()
        
        if confirm_result == 0:  # 예
            self.reset_tutorial()
            print("✅ 튜토리얼이 초기화되었습니다.")
            self._wait_for_key()
    
    def _wait_for_key(self):
        """키 입력 대기"""
        try:
            from .input_utils import KeyboardInput
            keyboard = KeyboardInput()
            keyboard.wait_for_key("아무 키나 눌러 계속...")
        except Exception:
            input("아무 키나 눌러 계속...")  # 폴백

    def _show_settings_menu_fallback(self):
        """설정 메뉴 폴백 (기존 방식)"""
        while True:
            print("\n" + "="*60)
            print("⚙️  게임 설정")
            print("="*60)
            print()
            
            # 튜토리얼 설정
            print("📚 튜토리얼 설정:")
            print(f"  1. 튜토리얼 완료 상태: {'✅' if self.is_tutorial_completed() else '❌'}")
            print(f"  2. 인트로 스킵: {'✅' if self.should_skip_intro() else '❌'}")
            print(f"  3. 고급 팁 표시: {'✅' if self.should_show_advanced_tips() else '❌'}")
            print()
            
            # 화면 설정
            print("🖥️  화면 설정:")
            print(f"  4. 화면 너비: {self.get('display', 'screen_width')}")
            print(f"  5. 맵 크기: {self.get('display', 'map_width')}x{self.get('display', 'map_height')}")
            print(f"  6. 색상 활성화: {'✅' if self.get('display', 'color_enabled') else '❌'}")
            print()
            
            # 게임플레이 설정
            print("🎮 게임플레이 설정:")
            print(f"  7. 자동 저장: {'✅' if self.get('gameplay', 'auto_save') else '❌'}")
            print(f"  8. 난이도: {self.get('gameplay', 'difficulty')}")
            print(f"  9. 빠른 전투: {'✅' if self.get('gameplay', 'fast_combat') else '❌'}")
            print()
            
            print("  r. 튜토리얼 초기화")
            print("  0. 돌아가기")
            print()
            
            choice = input("선택: ").strip().lower()
            
            if choice == '1':
                self.toggle_setting("tutorial", "tutorial_completed")
                print("✅ 설정이 변경되었습니다.")
            elif choice == '2':
                self.toggle_setting("tutorial", "skip_intro")
                print("✅ 설정이 변경되었습니다.")
            elif choice == '3':
                self.toggle_setting("tutorial", "show_advanced_tips")
                print("✅ 설정이 변경되었습니다.")
            elif choice == '4':
                try:
                    width = int(input("새 화면 너비 (80-200): "))
                    if 80 <= width <= 200:
                        self.set("display", "screen_width", width)
                        print("✅ 화면 너비가 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다.")
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
            elif choice == '5':
                try:
                    width = int(input("맵 너비 (60-120): "))
                    height = int(input("맵 높이 (15-30): "))
                    if 60 <= width <= 120 and 15 <= height <= 30:
                        self.set("display", "map_width", width)
                        self.set("display", "map_height", height)
                        print("✅ 맵 크기가 변경되었습니다.")
                    else:
                        print("❌ 유효한 범위가 아닙니다.")
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
            elif choice == '6':
                self.toggle_setting("display", "color_enabled")
                print("✅ 설정이 변경되었습니다.")
            elif choice == '7':
                self.toggle_setting("gameplay", "auto_save")
                print("✅ 설정이 변경되었습니다.")
            elif choice == '8':
                print("난이도 선택:")
                print("  1. 쉬움 (easy)")
                print("  2. 보통 (normal)")
                print("  3. 어려움 (hard)")
                diff_choice = input("선택: ").strip()
                if diff_choice == '1':
                    self.set("gameplay", "difficulty", "easy")
                elif diff_choice == '2':
                    self.set("gameplay", "difficulty", "normal")
                elif diff_choice == '3':
                    self.set("gameplay", "difficulty", "hard")
                else:
                    print("❌ 유효하지 않은 선택입니다.")
                    continue
                print("✅ 난이도가 변경되었습니다.")
            elif choice == '9':
                self.toggle_setting("gameplay", "fast_combat")
                print("✅ 설정이 변경되었습니다.")
            elif choice == 'r':
                confirm = input("튜토리얼을 초기화하시겠습니까? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.reset_tutorial()
                    print("✅ 튜토리얼이 초기화되었습니다.")
            elif choice == '0':
                break
            else:
                print("❌ 유효하지 않은 선택입니다.")


# 전역 설정 객체
game_settings = GameSettings()

def show_settings_menu():
    """전역 설정 메뉴 함수"""
    game_settings.show_settings_menu()
