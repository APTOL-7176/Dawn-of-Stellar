"""
고성능 프레임레이트 테스트 - 부드러운 화면 전환
"""

import sys
import time
sys.path.append('.')

from game.clear_screen_utils import soft_clear_screen, set_game_fps, wait_frame, get_frame_controller

def test_high_fps():
    """고성능 FPS 테스트"""
    print("🎮 고성능 프레임레이트 테스트")
    print("="*50)
    
    # FPS 설정 테스트
    for fps in [20, 30, 60]:
        print(f"\n🎯 {fps} FPS로 설정 중...")
        set_game_fps(fps)
        
        print(f"3초간 {fps} FPS로 화면 업데이트 테스트:")
        
        start_time = time.time()
        frame_count = 0
        
        # 3초간 테스트
        while time.time() - start_time < 3.0:
            soft_clear_screen()
            
            print("="*50)
            print(f"  🎮 FPS 테스트: {fps} FPS  ".center(50))
            print("="*50)
            print()
            print(f"현재 프레임: {frame_count}")
            print(f"경과 시간: {time.time() - start_time:.1f}초")
            print(f"실제 FPS: {frame_count / (time.time() - start_time):.1f}")
            print()
            print("🔥 부드러운 화면 전환 테스트 중...")
            print("❄️ 깜빡임 없는 화면 업데이트")
            print("⚡ 고성능 프레임레이트 제어")
            print()
            print("✅ 화면이 부드럽게 업데이트되나요?")
            print("✅ 깜빡임이 없나요?")
            print("✅ 성능이 좋나요?")
            
            wait_frame()  # 프레임레이트 제어
            frame_count += 1
        
        actual_fps = frame_count / 3.0
        print(f"\n📊 {fps} FPS 테스트 결과: {actual_fps:.1f} FPS")
        time.sleep(1)

    print("\n🎊 모든 FPS 테스트 완료!")
    print("✨ 부드러운 화면 전환과 안정적인 프레임레이트를 확인하세요!")

if __name__ == "__main__":
    test_high_fps()
