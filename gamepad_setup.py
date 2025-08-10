#!/usr/bin/env python3
"""
Dawn of Stellar - 게임패드 설정 및 테스트 도구
"""

import pygame
import sys
import time
from typing import Dict, List, Optional

class GamepadTester:
    """게임패드 테스트 및 설정 클래스"""
    
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joysticks = []
        self.running = True
        
    def detect_gamepads(self) -> List[Dict]:
        """연결된 게임패드 감지"""
        gamepad_list = []
        
        print("🎮 게임패드 감지 중...")
        joystick_count = pygame.joystick.get_count()
        
        if joystick_count == 0:
            print("❌ 연결된 게임패드가 없습니다.")
            print("\n지원하는 게임패드:")
            print("  • Xbox One/Series 컨트롤러")
            print("  • PlayStation 4/5 컨트롤러")
            print("  • Nintendo Switch Pro 컨트롤러")
            print("  • Steam 컨트롤러")
            print("  • 기타 DirectInput/XInput 호환 컨트롤러")
            return gamepad_list
            
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            
            gamepad_info = {
                'index': i,
                'name': joystick.get_name(),
                'axes': joystick.get_numaxes(),
                'buttons': joystick.get_numbuttons(),
                'hats': joystick.get_numhats(),
                'instance_id': joystick.get_instance_id(),
                'joystick': joystick
            }
            
            gamepad_list.append(gamepad_info)
            self.joysticks.append(joystick)
            
            print(f"✅ 게임패드 {i + 1}: {joystick.get_name()}")
            print(f"   축: {joystick.get_numaxes()}개, 버튼: {joystick.get_numbuttons()}개")
            
        return gamepad_list
        
    def test_gamepad(self, gamepad_index: int = 0):
        """게임패드 테스트"""
        if not self.joysticks or gamepad_index >= len(self.joysticks):
            print("❌ 테스트할 게임패드가 없습니다.")
            return
            
        joystick = self.joysticks[gamepad_index]
        print(f"\n🎮 {joystick.get_name()} 테스트 시작")
        print("아무 버튼이나 눌러보세요... (ESC 또는 Start 버튼으로 종료)")
        
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                elif event.type == pygame.JOYBUTTONDOWN:
                    print(f"🔴 버튼 {event.button} 눌림")
                    # Start 버튼 (보통 9번 또는 10번)으로 종료
                    if event.button in [9, 10]:
                        print("🚪 Start 버튼으로 테스트 종료")
                        self.running = False
                        
                elif event.type == pygame.JOYBUTTONUP:
                    print(f"🔵 버튼 {event.button} 놓음")
                    
                elif event.type == pygame.JOYAXISMOTION:
                    # 축 움직임이 작으면 무시 (데드존)
                    if abs(event.value) > 0.1:
                        print(f"🕹️ 축 {event.axis}: {event.value:.2f}")
                        
                elif event.type == pygame.JOYHATMOTION:
                    print(f"🎯 D-Pad: {event.value}")
                    
            # ESC 키로도 종료 가능
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                print("🚪 ESC 키로 테스트 종료")
                self.running = False
                
            clock.tick(60)  # 60 FPS
            
    def show_gamepad_mapping(self):
        """Dawn of Stellar 게임패드 매핑 표시"""
        print("\n📋 Dawn of Stellar 게임패드 매핑:")
        print("=" * 50)
        print("🎮 이동:")
        print("   왼쪽 스틱 / D-Pad  → 캐릭터 이동")
        print("   오른쪽 스틱       → 메뉴 탐색")
        print()
        print("🎮 액션:")
        print("   A 버튼 (크로스)   → 확인/선택")
        print("   B 버튼 (서클)    → 취소/뒤로")
        print("   X 버튼 (스퀘어)  → 메뉴 열기")
        print("   Y 버튼 (트라이앵글) → 인벤토리")
        print()
        print("🎮 숄더 버튼:")
        print("   LB/L1            → 페이지 위")
        print("   RB/R1            → 페이지 아래")
        print("   LT/L2            → 빠른 사용")
        print("   RT/R2            → 공격")
        print()
        print("🎮 특수:")
        print("   Start/Menu       → 게임 메뉴")
        print("   Select/Share     → 상태 확인")
        print("   Home/PS/Guide    → 종료")
        print("=" * 50)
        
    def save_gamepad_config(self):
        """게임패드 설정 저장"""
        config = {
            "gamepad_enabled": len(self.joysticks) > 0,
            "detected_gamepads": []
        }
        
        for i, joystick in enumerate(self.joysticks):
            gamepad_config = {
                "name": joystick.get_name(),
                "index": i,
                "axes": joystick.get_numaxes(),
                "buttons": joystick.get_numbuttons()
            }
            config["detected_gamepads"].append(gamepad_config)
            
        # JSON 파일로 저장
        import json
        try:
            with open("gamepad_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ 게임패드 설정이 gamepad_config.json에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")

def main():
    """메인 함수"""
    print("🌟 Dawn of Stellar - 게임패드 설정 도구")
    print("=" * 50)
    
    tester = GamepadTester()
    
    try:
        # 게임패드 감지
        gamepads = tester.detect_gamepads()
        
        if not gamepads:
            print("\n💡 게임패드 연결 방법:")
            print("1. USB로 연결하거나 Bluetooth 페어링")
            print("2. Windows 게임 컨트롤러 설정에서 인식 확인")
            print("3. 이 프로그램을 다시 실행")
            input("\n계속하려면 Enter를 누르세요...")
            return
            
        # 게임패드 매핑 표시
        tester.show_gamepad_mapping()
        
        # 테스트 여부 확인
        while True:
            choice = input("\n🎮 게임패드를 테스트하시겠습니까? (y/n): ").lower()
            if choice in ['y', 'yes', '예']:
                # 여러 게임패드가 있으면 선택
                if len(gamepads) > 1:
                    print("\n📋 연결된 게임패드:")
                    for i, gamepad in enumerate(gamepads):
                        print(f"  {i + 1}. {gamepad['name']}")
                        
                    try:
                        choice = int(input("테스트할 게임패드 번호: ")) - 1
                        if 0 <= choice < len(gamepads):
                            tester.test_gamepad(choice)
                        else:
                            print("❌ 잘못된 번호입니다.")
                    except ValueError:
                        print("❌ 숫자를 입력해주세요.")
                else:
                    tester.test_gamepad(0)
                break
            elif choice in ['n', 'no', '아니오']:
                break
            else:
                print("y 또는 n을 입력해주세요.")
                
        # 설정 저장
        tester.save_gamepad_config()
        
        print("\n🎉 게임패드 설정이 완료되었습니다!")
        print("이제 Dawn of Stellar에서 게임패드를 사용할 수 있습니다.")
        
    except KeyboardInterrupt:
        print("\n\n🚪 사용자가 종료했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        pygame.quit()
        
if __name__ == "__main__":
    main()
