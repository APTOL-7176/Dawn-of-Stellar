#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
핫 리로드 헬퍼 - 게임 중 쉬운 리로드 기능
게임 실행 중 'r' 키를 눌러 주요 모듈들을 리로드할 수 있습니다.
"""

from hot_reload_manager import reload_module, HOT_RELOAD_AVAILABLE
from game.error_logger import logger

def handle_hot_reload_key(key: str, game_instance=None) -> bool:
    """
    핫 리로드 키 처리
    
    Args:
        key: 입력된 키
        game_instance: 게임 인스턴스 (선택사항)
    
    Returns:
        bool: 핫 리로드 키가 처리되었는지 여부
    """
    if not HOT_RELOAD_AVAILABLE:
        return False
        
    if key.lower() == 'r':
        print("\n🔥 핫 리로드 메뉴")
        print("=" * 40)
        print("1. 전투 시스템 (brave_combat)")
        print("2. 월드 시스템 (world)")  
        print("3. 캐릭터 시스템 (character)")
        print("4. 아이템 시스템 (item_system)")
        print("5. 스킬 시스템 (skill_system)")
        print("6. 모든 시스템 (all)")
        print("0. 취소")
        print("=" * 40)
        
        try:
            choice = input("리로드할 시스템을 선택하세요: ").strip()
            
            reload_map = {
                '1': 'game.brave_combat',
                '2': 'game.world',
                '3': 'game.character', 
                '4': 'game.item_system',
                '5': 'game.skill_system'
            }
            
            if choice == '0':
                print("❌ 리로드 취소")
                return True
            elif choice == '6':
                print("🔄 모든 시스템 리로드 중...")
                success_count = 0
                for module_name in reload_map.values():
                    if reload_module(module_name):
                        success_count += 1
                        
                print(f"✅ {success_count}/{len(reload_map)} 시스템 리로드 완료!")
                logger.log_system_info("핫리로드", f"전체 시스템 리로드", {
                    "성공수": success_count,
                    "총수": len(reload_map)
                })
                
            elif choice in reload_map:
                module_name = reload_map[choice]
                print(f"🔄 {module_name} 리로드 중...")
                
                if reload_module(module_name):
                    print(f"✅ {module_name} 리로드 완료!")
                    logger.log_system_info("핫리로드", f"모듈 리로드 성공", {
                        "모듈": module_name
                    })
                else:
                    print(f"❌ {module_name} 리로드 실패!")
                    logger.log_system_warning("핫리로드", f"모듈 리로드 실패", {
                        "모듈": module_name
                    })
            else:
                print("❌ 잘못된 선택입니다.")
                
        except KeyboardInterrupt:
            print("\n❌ 리로드 취소")
        except Exception as e:
            print(f"❌ 리로드 중 오류: {e}")
            logger.log_error("핫리로드", f"리로드 오류: {e}", {})
            
        print("\n계속하려면 Enter를 누르세요...")
        input()
        return True
        
    return False

def show_hot_reload_help():
    """핫 리로드 도움말 표시"""
    if HOT_RELOAD_AVAILABLE:
        print("\n🔥 핫 리로드 기능 활성화됨!")
        print("📝 게임 중 언제든지 'r' 키를 눌러 모듈을 리로드할 수 있습니다.")
        print("💡 파일을 수정하면 자동으로 감지되어 리로드됩니다.")
        print("⚡ 게임을 재시작하지 않고도 코드 변경사항을 즉시 적용!")
    else:
        print("\n⚠️ 핫 리로드 기능이 비활성화되어 있습니다.")

if __name__ == "__main__":
    # 테스트 코드
    show_hot_reload_help()
    print("\n테스트: 'r' 키 입력을 시뮬레이션...")
    handle_hot_reload_key('r')
