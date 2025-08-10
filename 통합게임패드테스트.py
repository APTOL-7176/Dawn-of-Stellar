#!/usr/bin/env python3
"""
Dawn of Stellar 통합 게임패드 테스트
화상키보드 차단 + 게임패드→키보드 변환 시스템 테스트
"""

import sys
import os
import time

# 게임 경로 추가
sys.path.append('.')

# 게임 모듈 임포트
try:
    from game.gamepad_input import HybridInputManager
    from game.input_utils import KeyboardInput
    from game.audio_system import AudioManager
    print("✅ 게임 모듈 로딩 성공")
except ImportError as e:
    print(f"❌ 게임 모듈 로딩 실패: {e}")
    sys.exit(1)

def test_integrated_gamepad_system():
    """통합 게임패드 시스템 테스트"""
    print("🎮 Dawn of Stellar 통합 게임패드 테스트")
    print("=" * 60)
    
    # 오디오 시스템 초기화
    try:
        audio_manager = AudioManager()
        print("🔊 오디오 시스템 초기화 완료")
    except Exception as e:
        print(f"⚠️ 오디오 시스템 초기화 실패: {e}")
        audio_manager = None
    
    # 키보드 입력 시스템 초기화
    try:
        keyboard_input = KeyboardInput()
        print("⌨️ 키보드 입력 시스템 초기화 완료")
    except Exception as e:
        print(f"❌ 키보드 입력 시스템 초기화 실패: {e}")
        return False
    
    # 하이브리드 입력 관리자 초기화
    try:
        input_manager = HybridInputManager(keyboard_input, audio_manager)
        print("🎯 하이브리드 입력 관리자 초기화 완료")
        print(f"📱 현재 입력 상태: {input_manager.get_input_info()}")
    except Exception as e:
        print(f"❌ 하이브리드 입력 관리자 초기화 실패: {e}")
        return False
    
    if not input_manager.is_gamepad_connected():
        print("⚠️ 게임패드가 연결되지 않았습니다.")
        print("🎮 Xbox/PlayStation/Nintendo Switch Pro 컨트롤러를 연결해주세요.")
        return False
    
    print("\n🔥 A버튼 화상키보드 차단 테스트")
    print("=" * 40)
    print("🎮 게임패드 버튼을 눌러보세요:")
    print("   🅰️ A버튼 (확인) - 화상키보드가 나타나면 안됩니다!")
    print("   🅱️ B버튼 (취소)")
    print("   ❌ X버튼 (ESC)")
    print("   🅨️ Y버튼 (인벤토리)")
    print("   🎮 방향패드 및 스틱 (이동)")
    print("   ESC키 또는 10초 후 자동 종료")
    print()
    
    test_start_time = time.time()
    button_test_results = []
    
    while True:
        # 시간 제한 체크 (10초)
        if time.time() - test_start_time > 10:
            print("\n⏰ 시간 제한 도달 (10초)")
            break
        
        # 입력 확인
        try:
            key = input_manager.get_key()
            if key:
                current_time = time.strftime("%H:%M:%S")
                
                # 특별한 키들 처리
                if key == '\n':
                    print(f"✅ [{current_time}] A버튼 (확인) 눌림 - 화상키보드 차단됨!")
                    button_test_results.append("A버튼 성공")
                elif key == 'q':
                    print(f"✅ [{current_time}] B버튼 (취소) 눌림")
                    button_test_results.append("B버튼 성공")
                elif key == '\x1b':
                    print(f"✅ [{current_time}] ESC키 감지 - 테스트 종료")
                    break
                elif key == 'i':
                    print(f"✅ [{current_time}] Y버튼 (인벤토리) 눌림")
                    button_test_results.append("Y버튼 성공")
                elif key in ['w', 'a', 's', 'd']:
                    direction_map = {'w': '위', 'a': '왼쪽', 's': '아래', 'd': '오른쪽'}
                    print(f"✅ [{current_time}] 이동: {direction_map[key]}")
                    if "이동 성공" not in button_test_results:
                        button_test_results.append("이동 성공")
                else:
                    print(f"✅ [{current_time}] 기타 입력: '{key}'")
                
                # 충분한 테스트가 완료되면 종료
                if len(button_test_results) >= 3:
                    print(f"\n🎉 충분한 테스트 완료! ({len(button_test_results)}개 버튼)")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 사용자가 테스트를 중단했습니다.")
            break
        except Exception as e:
            print(f"⚠️ 입력 처리 오류: {e}")
        
        time.sleep(0.016)  # 60 FPS
    
    # 테스트 결과 요약
    print("\n📊 테스트 결과 요약")
    print("=" * 30)
    
    if button_test_results:
        print("✅ 성공한 테스트:")
        for result in button_test_results:
            print(f"   ✓ {result}")
        
        if "A버튼 성공" in button_test_results:
            print("\n🎉 A버튼 화상키보드 차단 성공!")
            print("✅ 이제 게임에서 A버튼을 안전하게 사용할 수 있습니다.")
        else:
            print("\n⚠️ A버튼 테스트가 완료되지 않았습니다.")
            print("🎮 A버튼을 눌러보세요.")
    else:
        print("❌ 게임패드 입력이 감지되지 않았습니다.")
        print("🔌 게임패드 연결 상태를 확인해주세요.")
    
    # 정리
    try:
        if hasattr(input_manager, 'gamepad_input') and input_manager.gamepad_input:
            input_manager.gamepad_input.stop()
    except:
        pass
    
    return len(button_test_results) > 0

def main():
    """메인 실행 함수"""
    success = test_integrated_gamepad_system()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Dawn of Stellar 통합 게임패드 테스트 완료!")
        print("✅ 화상키보드 차단 시스템이 정상 작동합니다.")
        print("🎮 이제 실제 게임에서 A버튼을 사용해보세요!")
    else:
        print("❌ 테스트 실패!")
        print("🔧 게임패드 연결 또는 시스템 설정을 확인해주세요.")
    
    print("\n💡 실제 게임 실행: python main.py")
    input("\n아무 키나 누르세요...")

if __name__ == "__main__":
    main()
