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
            "atb": {
                "animation_enabled": True,
                "animation_fps": 20,
                "update_speed": 1.0,
                "show_percentage": True,
                "smooth_animation": True,
                "frame_delay": 0.05
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
    
    def get_section(self, category: str):
        """설정 섹션 전체 가져오기"""
        return self.settings.get(category, {})
    
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
                    f"⏳ ATB 시스템 설정",
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
                    "ATB 게이지 애니메이션과 속도를 설정합니다",
                    "사운드와 음악 설정을 변경합니다",
                    "모든 튜토리얼 진행도를 초기화합니다",
                    "설정 메뉴를 나갑니다"
                ]
                
                menu = create_simple_menu("⚙️ 게임 설정", options, descriptions)
                result = menu.run()
                
                if result == -1 or result == 12:  # 돌아가기
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
                elif result == 3:  # 화면 너비
                    self._change_screen_width()
                elif result == 4:  # 맵 크기
                    self._change_map_size()
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
                elif result == 9:  # ATB 시스템 설정
                    self._show_atb_settings()
                elif result == 10:  # 오디오 설정
                    self._show_audio_settings()
                elif result == 11:  # 튜토리얼 초기화
                    self._reset_tutorials()
                    
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
    
    def _show_atb_settings(self):
        """ATB 시스템 설정"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            while True:
                # 현재 ATB 설정 상태로 옵션 텍스트 생성
                options = [
                    f"🎬 ATB 애니메이션: {'✅' if self.get('atb', 'animation_enabled') else '❌'}",
                    f"🎯 애니메이션 FPS: {self.get('atb', 'animation_fps', 20)}",
                    f"⚡ ATB 업데이트 속도: {self.get('atb', 'update_speed', 1.0)}x",
                    f"📊 퍼센트 표시: {'✅' if self.get('atb', 'show_percentage') else '❌'}",
                    f"🌊 부드러운 애니메이션: {'✅' if self.get('atb', 'smooth_animation') else '❌'}",
                    "🔄 ATB 설정 초기화",
                    "❌ 돌아가기"
                ]
                
                descriptions = [
                    "ATB 게이지 애니메이션을 켜거나 끕니다",
                    "ATB 애니메이션의 프레임 속도를 조정합니다",
                    "ATB 게이지 증가 속도를 조정합니다",
                    "ATB 게이지에 퍼센트를 표시합니다",
                    "ATB 게이지 변화를 부드럽게 합니다",
                    "모든 ATB 설정을 기본값으로 되돌립니다",
                    "ATB 설정 메뉴를 나갑니다"
                ]
                
                menu = create_simple_menu("⏳ ATB 시스템 설정", options, descriptions)
                result = menu.run()
                
                if result == -1 or result == 6:  # 돌아가기
                    break
                elif result == 0:  # ATB 애니메이션 토글
                    self.toggle_setting("atb", "animation_enabled")
                    print("✅ ATB 애니메이션 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 1:  # FPS 변경
                    self._change_atb_fps()
                elif result == 2:  # 업데이트 속도 변경
                    self._change_atb_speed()
                elif result == 3:  # 퍼센트 표시 토글
                    self.toggle_setting("atb", "show_percentage")
                    print("✅ 퍼센트 표시 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 4:  # 부드러운 애니메이션 토글
                    self.toggle_setting("atb", "smooth_animation")
                    print("✅ 부드러운 애니메이션 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 5:  # ATB 설정 초기화
                    self._reset_atb_settings()
                    
        except ImportError:
            # 폴백: 텍스트 메뉴
            while True:
                print("\n" + "="*60)
                print("⏳ ATB 시스템 설정")
                print("="*60)
                print(f"1. ATB 애니메이션: {'✅' if self.get('atb', 'animation_enabled') else '❌'}")
                print(f"2. 애니메이션 FPS: {self.get('atb', 'animation_fps', 20)}")
                print(f"3. ATB 업데이트 속도: {self.get('atb', 'update_speed', 1.0)}x")
                print(f"4. 퍼센트 표시: {'✅' if self.get('atb', 'show_percentage') else '❌'}")
                print(f"5. 부드러운 애니메이션: {'✅' if self.get('atb', 'smooth_animation') else '❌'}")
                print("r. ATB 설정 초기화")
                print("0. 돌아가기")
                
                choice = input("선택: ").strip()
                
                if choice == '1':
                    self.toggle_setting("atb", "animation_enabled")
                    print("✅ 설정이 변경되었습니다.")
                elif choice == '2':
                    self._change_atb_fps()
                elif choice == '3':
                    self._change_atb_speed()
                elif choice == '4':
                    self.toggle_setting("atb", "show_percentage")
                    print("✅ 설정이 변경되었습니다.")
                elif choice == '5':
                    self.toggle_setting("atb", "smooth_animation")
                    print("✅ 설정이 변경되었습니다.")
                elif choice == 'r':
                    self._reset_atb_settings()
                elif choice == '0':
                    break
                else:
                    print("❌ 유효하지 않은 선택입니다.")

    def _change_atb_fps(self):
        """ATB 애니메이션 FPS 변경"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            fps_options = ["10 FPS", "15 FPS", "20 FPS (기본)", "30 FPS", "60 FPS", "❌ 취소"]
            fps_descriptions = [
                "낮은 FPS - 부드럽지 않지만 성능 절약",
                "보통 FPS - 적당한 성능과 품질",
                "기본 FPS - 권장 설정",
                "높은 FPS - 부드럽지만 더 많은 자원 사용",
                "최고 FPS - 매우 부드럽지만 높은 자원 사용",
                "FPS 변경을 취소합니다"
            ]
            
            menu = create_simple_menu("ATB 애니메이션 FPS 선택", fps_options, fps_descriptions)
            result = menu.run()
            
            fps_values = [10, 15, 20, 30, 60]
            if result != -1 and result < len(fps_values):
                self.set("atb", "animation_fps", fps_values[result])
                # frame_delay도 자동으로 조정
                frame_delay = 1.0 / fps_values[result]
                self.set("atb", "frame_delay", frame_delay)
                print(f"✅ ATB 애니메이션 FPS가 {fps_values[result]}로 변경되었습니다.")
                self._wait_for_key()
        except ImportError:
            # 폴백
            print("FPS 선택: 1) 10 FPS  2) 15 FPS  3) 20 FPS  4) 30 FPS  5) 60 FPS")
            choice = input("선택 (1-5): ").strip()
            fps_values = [10, 15, 20, 30, 60]
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(fps_values):
                    self.set("atb", "animation_fps", fps_values[idx])
                    frame_delay = 1.0 / fps_values[idx]
                    self.set("atb", "frame_delay", frame_delay)
                    print(f"✅ FPS가 {fps_values[idx]}로 변경되었습니다.")
                else:
                    print("❌ 유효하지 않은 선택입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")

    def _change_atb_speed(self):
        """ATB 업데이트 속도 변경"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            speed_options = [
                "0.5x (매우 느림)", "0.75x (느림)", "1.0x (기본)", 
                "1.25x (조금 빠름)", "1.5x (빠름)", "2.0x (매우 빠름)", "3.0x (극한)", "❌ 취소"
            ]
            speed_descriptions = [
                "ATB가 매우 천천히 증가합니다",
                "ATB가 천천히 증가합니다", 
                "기본 ATB 증가 속도입니다",
                "ATB가 조금 빠르게 증가합니다",
                "ATB가 빠르게 증가합니다",
                "ATB가 매우 빠르게 증가합니다",
                "ATB가 극한으로 빠르게 증가합니다",
                "속도 변경을 취소합니다"
            ]
            
            menu = create_simple_menu("ATB 업데이트 속도 선택", speed_options, speed_descriptions)
            result = menu.run()
            
            speed_values = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
            if result != -1 and result < len(speed_values):
                self.set("atb", "update_speed", speed_values[result])
                print(f"✅ ATB 업데이트 속도가 {speed_values[result]}x로 변경되었습니다.")
                self._wait_for_key()
        except ImportError:
            # 폴백
            print("속도 선택: 1) 0.5x  2) 0.75x  3) 1.0x  4) 1.25x  5) 1.5x  6) 2.0x  7) 3.0x")
            choice = input("선택 (1-7): ").strip()
            speed_values = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(speed_values):
                    self.set("atb", "update_speed", speed_values[idx])
                    print(f"✅ 속도가 {speed_values[idx]}x로 변경되었습니다.")
                else:
                    print("❌ 유효하지 않은 선택입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")

    def _reset_atb_settings(self):
        """ATB 설정 초기화"""
        try:
            from .cursor_menu_system import create_yes_no_menu
            
            confirm_menu = create_yes_no_menu("ATB 설정을 초기화하시겠습니까?")
            confirm_result = confirm_menu.run()
            
            if confirm_result == 0:  # 예
                # 기본 ATB 설정으로 초기화
                self.set("atb", "animation_enabled", True)
                self.set("atb", "animation_fps", 20)
                self.set("atb", "update_speed", 1.0)
                self.set("atb", "show_percentage", True)
                self.set("atb", "smooth_animation", True)
                self.set("atb", "frame_delay", 0.05)
                print("✅ ATB 설정이 초기화되었습니다.")
                self._wait_for_key()
        except ImportError:
            # 폴백
            confirm = input("ATB 설정을 초기화하시겠습니까? (y/n): ").strip().lower()
            if confirm == 'y':
                self.set("atb", "animation_enabled", True)
                self.set("atb", "animation_fps", 20)
                self.set("atb", "update_speed", 1.0)
                self.set("atb", "show_percentage", True)
                self.set("atb", "smooth_animation", True)
                self.set("atb", "frame_delay", 0.05)
                print("✅ ATB 설정이 초기화되었습니다.")

    def _show_audio_settings(self):
        """오디오 설정"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            while True:
                # 현재 오디오 설정 상태로 옵션 텍스트 생성
                options = [
                    f"🔊 사운드 효과: {'✅' if self.get('audio', 'sound_enabled') else '❌'}",
                    f"🎵 배경음악: {'✅' if self.get('audio', 'music_enabled') else '❌'}",
                    f"🔉 볼륨: {self.get('audio', 'volume', 50)}%",
                    "❌ 돌아가기"
                ]
                
                descriptions = [
                    "게임 사운드 효과를 켜거나 끕니다",
                    "배경음악을 켜거나 끕니다",
                    "전체 볼륨을 조정합니다 (0-100%)",
                    "오디오 설정 메뉴를 나갑니다"
                ]
                
                menu = create_simple_menu("🔊 오디오 설정", options, descriptions)
                result = menu.run()
                
                if result == -1 or result == 3:  # 돌아가기
                    break
                elif result == 0:  # 사운드 효과 토글
                    self.toggle_setting("audio", "sound_enabled")
                    print("✅ 사운드 효과 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 1:  # 배경음악 토글
                    self.toggle_setting("audio", "music_enabled")
                    print("✅ 배경음악 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 2:  # 볼륨 조정
                    self._change_volume()
                    
        except ImportError:
            # 폴백: 텍스트 메뉴
            while True:
                print("\n" + "="*60)
                print("🔊 오디오 설정")
                print("="*60)
                print(f"1. 사운드 효과: {'✅' if self.get('audio', 'sound_enabled') else '❌'}")
                print(f"2. 배경음악: {'✅' if self.get('audio', 'music_enabled') else '❌'}")
                print(f"3. 볼륨: {self.get('audio', 'volume', 50)}%")
                print("0. 돌아가기")
                
                choice = input("선택: ").strip()
                
                if choice == '1':
                    self.toggle_setting("audio", "sound_enabled")
                    print("✅ 설정이 변경되었습니다.")
                elif choice == '2':
                    self.toggle_setting("audio", "music_enabled")
                    print("✅ 설정이 변경되었습니다.")
                elif choice == '3':
                    self._change_volume()
                elif choice == '0':
                    break
                else:
                    print("❌ 유효하지 않은 선택입니다.")

    def _change_volume(self):
        """볼륨 변경"""
        try:
            from .input_utils import KeyboardInput
            keyboard = KeyboardInput()
            
            print("새 볼륨 (0-100): ", end='', flush=True)
            volume_str = keyboard.get_string_input()
            
            if volume_str:
                volume = int(volume_str)
                if 0 <= volume <= 100:
                    self.set("audio", "volume", volume)
                    print("✅ 볼륨이 변경되었습니다.")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
                else:
                    print("❌ 유효한 범위가 아닙니다.")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
            else:
                print("❌ 입력이 취소되었습니다.")
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
    
    def _show_atb_settings(self):
        """ATB 시스템 설정 메뉴"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            while True:
                atb_settings = self.get_section("atb")
                
                options = [
                    f"🎬 애니메이션 활성화: {'✅' if atb_settings.get('animation_enabled', True) else '❌'}",
                    f"⚡ 애니메이션 FPS: {atb_settings.get('animation_fps', 20)}",
                    f"🚀 업데이트 속도: {atb_settings.get('update_speed', 1.0):.1f}x",
                    f"📊 퍼센트 표시: {'✅' if atb_settings.get('show_percentage', True) else '❌'}",
                    f"🌊 부드러운 애니메이션: {'✅' if atb_settings.get('smooth_animation', True) else '❌'}",
                    "🔄 기본값으로 초기화",
                    "❌ 돌아가기"
                ]
                
                descriptions = [
                    "ATB 게이지 애니메이션을 활성화/비활성화합니다",
                    "ATB 애니메이션의 초당 프레임 수를 설정합니다 (10-60)",
                    "ATB 게이지 증가 속도를 조정합니다 (0.5x-3.0x)",
                    "ATB 게이지에 퍼센트 숫자를 표시할지 설정합니다",
                    "ATB 게이지 변화를 부드럽게 애니메이션으로 표시합니다",
                    "모든 ATB 설정을 기본값으로 재설정합니다",
                    "이전 메뉴로 돌아갑니다"
                ]
                
                menu = create_simple_menu("⏳ ATB 시스템 설정", options, descriptions)
                result = menu.run()
                
                if result == -1 or result == 6:  # 돌아가기
                    break
                elif result == 0:  # 애니메이션 활성화
                    self.toggle_setting("atb", "animation_enabled")
                    print("✅ ATB 애니메이션 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 1:  # 애니메이션 FPS
                    self._change_atb_fps()
                elif result == 2:  # 업데이트 속도
                    self._change_atb_speed()
                elif result == 3:  # 퍼센트 표시
                    self.toggle_setting("atb", "show_percentage")
                    print("✅ ATB 퍼센트 표시 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 4:  # 부드러운 애니메이션
                    self.toggle_setting("atb", "smooth_animation")
                    print("✅ ATB 부드러운 애니메이션 설정이 변경되었습니다.")
                    self._wait_for_key()
                elif result == 5:  # 기본값으로 초기화
                    self._reset_atb_settings()
                    
        except ImportError:
            # 폴백: 간단한 텍스트 메뉴
            self._show_atb_settings_fallback()
    
    def _change_atb_fps(self):
        """ATB FPS 설정 변경"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            fps_options = ["10 FPS (매우 느림)", "15 FPS (느림)", "20 FPS (기본)", "30 FPS (빠름)", "60 FPS (매우 빠름)"]
            fps_values = [10, 15, 20, 30, 60]
            
            menu = create_simple_menu("🎬 ATB 애니메이션 FPS", fps_options, 
                                    ["매우 느린 애니메이션", "느린 애니메이션", "기본 속도 (권장)", "빠른 애니메이션", "매우 빠른 애니메이션"])
            result = menu.run()
            
            if result is not None and 0 <= result < len(fps_values):
                new_fps = fps_values[result]
                self.set("atb", "animation_fps", new_fps)
                self.set("atb", "frame_delay", 1.0 / new_fps)
                print(f"✅ ATB FPS가 {new_fps}로 설정되었습니다.")
                self._wait_for_key()
                
        except ImportError:
            # 폴백
            print("FPS 설정 (10-60): ", end='', flush=True)
            try:
                new_fps = int(input())
                if 10 <= new_fps <= 60:
                    self.set("atb", "animation_fps", new_fps)
                    self.set("atb", "frame_delay", 1.0 / new_fps)
                    print(f"✅ ATB FPS가 {new_fps}로 설정되었습니다.")
                else:
                    print("❌ 10-60 사이의 값을 입력하세요.")
            except ValueError:
                print("❌ 올바른 숫자를 입력하세요.")
    
    def _change_atb_speed(self):
        """ATB 속도 설정 변경"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            speed_options = ["0.5x (매우 느림)", "0.75x (느림)", "1.0x (기본)", "1.25x (조금 빠름)", "1.5x (빠름)", "2.0x (매우 빠름)", "3.0x (초고속)"]
            speed_values = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
            
            menu = create_simple_menu("🚀 ATB 업데이트 속도", speed_options,
                                    ["매우 느린 전투", "느린 전투", "기본 속도", "조금 빠른 전투", "빠른 전투", "매우 빠른 전투", "초고속 전투"])
            result = menu.run()
            
            if result is not None and 0 <= result < len(speed_values):
                new_speed = speed_values[result]
                self.set("atb", "update_speed", new_speed)
                print(f"✅ ATB 속도가 {new_speed}x로 설정되었습니다.")
                self._wait_for_key()
                
        except ImportError:
            # 폴백
            print("속도 배율 (0.5-3.0): ", end='', flush=True)
            try:
                new_speed = float(input())
                if 0.5 <= new_speed <= 3.0:
                    self.set("atb", "update_speed", new_speed)
                    print(f"✅ ATB 속도가 {new_speed}x로 설정되었습니다.")
                else:
                    print("❌ 0.5-3.0 사이의 값을 입력하세요.")
            except ValueError:
                print("❌ 올바른 숫자를 입력하세요.")
    
    def _reset_atb_settings(self):
        """ATB 설정 초기화"""
        default_atb = {
            "animation_enabled": True,
            "animation_fps": 20,
            "update_speed": 1.0,
            "show_percentage": True,
            "smooth_animation": True,
            "frame_delay": 0.05
        }
        
        for key, value in default_atb.items():
            self.set("atb", key, value)
        
        print("✅ ATB 설정이 기본값으로 초기화되었습니다.")
        self._wait_for_key()
    
    def _show_atb_settings_fallback(self):
        """ATB 설정 폴백 메뉴"""
        while True:
            atb_settings = self.get_section("atb")
            
            print("\n" + "="*50)
            print("⏳ ATB 시스템 설정")
            print("="*50)
            print(f"1. 애니메이션: {'ON' if atb_settings.get('animation_enabled', True) else 'OFF'}")
            print(f"2. FPS: {atb_settings.get('animation_fps', 20)}")
            print(f"3. 속도: {atb_settings.get('update_speed', 1.0):.1f}x")
            print(f"4. 퍼센트 표시: {'ON' if atb_settings.get('show_percentage', True) else 'OFF'}")
            print("5. 기본값 초기화")
            print("0. 돌아가기")
            
            choice = input("\n선택하세요: ")
            
            if choice == '1':
                self.toggle_setting("atb", "animation_enabled")
                print("✅ 설정이 변경되었습니다.")
            elif choice == '2':
                self._change_atb_fps()
            elif choice == '3':
                self._change_atb_speed()
            elif choice == '4':
                self.toggle_setting("atb", "show_percentage")
                print("✅ 설정이 변경되었습니다.")
            elif choice == '5':
                self._reset_atb_settings()
            elif choice == '0':
                break
            else:
                print("❌ 유효하지 않은 선택입니다.")


# 전역 설정 객체
game_settings = GameSettings()

def show_settings_menu():
    """전역 설정 메뉴 함수"""
    game_settings.show_settings_menu()
