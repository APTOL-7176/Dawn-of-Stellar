#!/usr/bin/env python3
"""
Dawn of Stellar - 하이브리드 입력 매니저
기존 KeyboardInput과 새로운 GamepadInput을 통합
"""

import sys
import os
import time
from typing import Optional

# 현재 디렉터리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from game.input_utils import KeyboardInput
    from game.gamepad_input import GamepadInput, GAMEPAD_GUIDE
except ImportError as e:
    print(f"⚠️ 입력 모듈 로드 실패: {e}")
    # 기본 KeyboardInput만 사용
    from game.input_utils import KeyboardInput
    GamepadInput = None
    GAMEPAD_GUIDE = "게임패드 지원을 사용할 수 없습니다."

class DawnOfStellarInputManager:
    """Dawn of Stellar 전용 하이브리드 입력 관리자"""
    
    def __init__(self, sound_manager=None):
        self.sound_manager = sound_manager
        
        # 키보드 입력 시스템 (항상 사용 가능)
        try:
            self.keyboard_input = KeyboardInput()
            print("⌨️ 키보드 입력 시스템 초기화 완료")
        except Exception as e:
            print(f"❌ 키보드 입력 시스템 초기화 실패: {e}")
            self.keyboard_input = None
        
        # 게임패드 입력 시스템 (선택적)
        self.gamepad_input = None
        self.gamepad_available = False
        
        if GamepadInput:
            try:
                self.gamepad_input = GamepadInput(sound_manager)
                self.gamepad_available = self.gamepad_input.is_connected()
                
                if self.gamepad_available:
                    gamepad_info = self.gamepad_input.get_gamepad_info()
                    print(f"🎮 게임패드 연결됨: {gamepad_info.get('name', '알 수 없는 기기')}")
                    print("💡 도움말을 보려면 게임에서 H 키를 누르세요!")
                else:
                    print("🎮 게임패드가 연결되지 않았습니다")
                    
            except Exception as e:
                print(f"⚠️ 게임패드 초기화 실패: {e}")
                self.gamepad_input = None
                self.gamepad_available = False
        else:
            print("⚠️ 게임패드 지원 모듈이 없습니다 (pygame 설치 필요)")
        
        # 입력 모드 설정
        self.menu_mode = False
        
        # 입력 통계
        self.input_stats = {
            'keyboard_inputs': 0,
            'gamepad_inputs': 0,
            'total_inputs': 0
        }
        
        # 상태 표시
        self._show_input_status()
    
    def _show_input_status(self):
        """입력 시스템 상태 표시"""
        print("\n" + "="*60)
        print("🎮 Dawn of Stellar 입력 시스템 상태")
        print("="*60)
        
        # 키보드 상태
        if self.keyboard_input:
            print("✅ 키보드: 사용 가능")
        else:
            print("❌ 키보드: 사용 불가")
        
        # 게임패드 상태
        if self.gamepad_available:
            gamepad_info = self.gamepad_input.get_gamepad_info()
            print(f"✅ 게임패드: {gamepad_info.get('name', '알 수 없는 기기')}")
            print(f"   버튼: {gamepad_info.get('buttons', 0)}개")
            print(f"   축: {gamepad_info.get('axes', 0)}개")
            print(f"   D-Pad: {gamepad_info.get('hats', 0)}개")
        else:
            print("❌ 게임패드: 연결되지 않음")
        
        print("="*60)
        
        # 조작법 안내
        if self.gamepad_available:
            print("🎯 기본 조작법:")
            print("   이동: W/A/S/D 키 또는 왼쪽 스틱/D-Pad")
            print("   확인: Enter 키 또는 A 버튼")
            print("   메뉴: I/P/F/H 키 또는 X/LB/Y/RB 버튼")
            print("   상세한 게임패드 조작법은 게임에서 H 키를 누르세요!")
        else:
            print("🎯 키보드 조작법:")
            print("   이동: W/A/S/D 키")
            print("   확인: Enter 키")
            print("   메뉴: I(인벤토리), P(파티), F(필드), H(도움말)")
        
        print("="*60 + "\n")
    
    def get_key(self) -> str:
        """키보드 또는 게임패드에서 입력 받기 (논블로킹)"""
        # 게임패드 입력 우선 확인
        if self.gamepad_available and self.gamepad_input.has_input():
            key = self.gamepad_input.get_input()
            if key:
                self.input_stats['gamepad_inputs'] += 1
                self.input_stats['total_inputs'] += 1
                return key
        
        # 키보드 입력 확인
        if self.keyboard_input:
            try:
                key = self.keyboard_input.get_key()
                if key:
                    self.input_stats['keyboard_inputs'] += 1
                    self.input_stats['total_inputs'] += 1
                    return key
            except Exception as e:
                print(f"⚠️ 키보드 입력 오류: {e}")
        
        return ''
    
    def wait_for_key(self, message: str = "아무 키나 누르세요...") -> str:
        """키보드 또는 게임패드 입력을 기다림 (블로킹)"""
        if message:
            print(message, end='', flush=True)
        
        while True:
            # 게임패드 입력 우선 확인
            if self.gamepad_available and self.gamepad_input.has_input():
                key = self.gamepad_input.get_input()
                if key:
                    print()  # 줄바꿈
                    self.input_stats['gamepad_inputs'] += 1
                    self.input_stats['total_inputs'] += 1
                    return key
            
            # 키보드 입력 확인
            if self.keyboard_input:
                try:
                    key = self.keyboard_input.get_key()
                    if key:
                        print()  # 줄바꿈
                        self.input_stats['keyboard_inputs'] += 1
                        self.input_stats['total_inputs'] += 1
                        return key
                except Exception as e:
                    print(f"⚠️ 키보드 입력 오류: {e}")
            
            # CPU 사용량 절약
            time.sleep(0.016)  # 60 FPS
    
    def get_string_input(self, prompt: str = "") -> str:
        """문자열 입력 받기 (키보드만 사용)"""
        if self.keyboard_input and hasattr(self.keyboard_input, 'get_string_input'):
            return self.keyboard_input.get_string_input(prompt)
        else:
            # 기본 input() 사용
            try:
                if prompt:
                    print(prompt, end='', flush=True)
                return input().strip()
            except (EOFError, KeyboardInterrupt):
                return ""
    
    def set_menu_mode(self, enabled: bool):
        """메뉴 모드 설정 (게임패드 D-Pad 매핑 변경)"""
        self.menu_mode = enabled
        if self.gamepad_input:
            self.gamepad_input.set_menu_mode(enabled)
    
    def clear_input_buffer(self):
        """모든 입력 버퍼 클리어"""
        if self.keyboard_input and hasattr(self.keyboard_input, 'clear_input_buffer'):
            self.keyboard_input.clear_input_buffer()
        
        if self.gamepad_input:
            self.gamepad_input.clear_input_queue()
    
    def is_gamepad_connected(self) -> bool:
        """게임패드 연결 상태 확인"""
        return self.gamepad_available
    
    def get_input_info(self) -> str:
        """현재 입력 방법 정보"""
        if self.gamepad_available:
            gamepad_info = self.gamepad_input.get_gamepad_info()
            return f"🎮 {gamepad_info.get('name', '게임패드')} + ⌨️ 키보드"
        else:
            return "⌨️ 키보드 전용"
    
    def get_input_stats(self) -> dict:
        """입력 통계 반환"""
        return self.input_stats.copy()
    
    def show_gamepad_guide(self):
        """게임패드 조작 가이드 표시"""
        if self.gamepad_available:
            print(GAMEPAD_GUIDE)
        else:
            print("🎮 게임패드가 연결되지 않았습니다.")
            print("⌨️ 키보드 조작법:")
            print("   이동: W(위), A(왼쪽), S(아래), D(오른쪽)")
            print("   확인: Enter")
            print("   메뉴: I(인벤토리), P(파티), F(필드), H(도움말)")
            print("   시스템: B(저장), L(로그), T(자동전투), Z(텔레포트)")
            print("   종료: Q")
    
    def vibrate_feedback(self, feedback_type: str = "light"):
        """게임패드 진동 피드백"""
        if not self.gamepad_available:
            return
        
        try:
            if feedback_type == "light":
                # 메뉴 선택, 아이템 획득 등
                pass  # 새로운 GamepadInput에는 진동 기능이 없음
            elif feedback_type == "medium":
                # 공격 성공, 레벨업 등
                pass
            elif feedback_type == "heavy":
                # 피격, 크리티컬 등
                pass
            elif feedback_type == "encounter":
                # 적과 마주침
                pass
            elif feedback_type == "victory":
                # 전투 승리
                pass
        except Exception as e:
            # 진동 실패는 조용히 처리
            pass
    
    def stop(self):
        """입력 시스템 정리"""
        if self.gamepad_input:
            try:
                self.gamepad_input.stop()
            except Exception as e:
                print(f"⚠️ 게임패드 정리 오류: {e}")
        
        # 입력 통계 출력
        if self.input_stats['total_inputs'] > 0:
            print(f"\n📊 입력 통계:")
            print(f"   키보드: {self.input_stats['keyboard_inputs']}회")
            print(f"   게임패드: {self.input_stats['gamepad_inputs']}회")
            print(f"   총 입력: {self.input_stats['total_inputs']}회")
    
    def __del__(self):
        """소멸자"""
        try:
            self.stop()
        except:
            pass

# 편의 함수들
def create_input_manager(sound_manager=None) -> DawnOfStellarInputManager:
    """Dawn of Stellar 입력 매니저 생성"""
    return DawnOfStellarInputManager(sound_manager)

def get_single_key_input(prompt: str = "") -> str:
    """단일 키 입력 받기 (편의 함수)"""
    input_manager = DawnOfStellarInputManager()
    try:
        return input_manager.wait_for_key(prompt)
    finally:
        input_manager.stop()

def wait_for_any_key(message: str = "아무 키나 누르세요...") -> str:
    """아무 키나 눌러서 계속하기"""
    input_manager = DawnOfStellarInputManager()
    try:
        return input_manager.wait_for_key(message)
    finally:
        input_manager.stop()

# 테스트 코드
if __name__ == "__main__":
    print("🎮 Dawn of Stellar 입력 시스템 테스트")
    
    input_manager = DawnOfStellarInputManager()
    
    try:
        print("\n📋 테스트 메뉴:")
        print("1. 단일 키 입력 테스트")
        print("2. 게임패드 가이드 보기")
        print("3. 입력 시스템 정보")
        print("4. 실시간 입력 테스트")
        print("q. 종료")
        
        while True:
            print("\n선택하세요: ", end='', flush=True)
            choice = input_manager.get_key()
            
            if not choice:
                time.sleep(0.1)
                continue
            
            if choice == 'q':
                print("q (종료)")
                break
            elif choice == '1':
                print("1 (단일 키 입력 테스트)")
                key = input_manager.wait_for_key("아무 키나 누르세요: ")
                print(f"입력된 키: '{key}'")
            elif choice == '2':
                print("2 (게임패드 가이드)")
                input_manager.show_gamepad_guide()
            elif choice == '3':
                print("3 (시스템 정보)")
                print(f"입력 방법: {input_manager.get_input_info()}")
                stats = input_manager.get_input_stats()
                print(f"입력 통계: {stats}")
            elif choice == '4':
                print("4 (실시간 입력 테스트)")
                print("실시간 입력 테스트 (q로 종료):")
                while True:
                    key = input_manager.get_key()
                    if key:
                        print(f"입력: '{key}'")
                        if key == 'q':
                            break
                    time.sleep(0.05)
            else:
                print(f"입력: '{choice}' (알 수 없는 선택)")
                
    except KeyboardInterrupt:
        print("\n\n종료합니다...")
    finally:
        input_manager.stop()
