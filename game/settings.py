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
        """설정 메뉴 표시"""
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
