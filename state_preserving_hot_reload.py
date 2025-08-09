"""
상태 보존 핫 리로드 시스템 v2.0
- 리로드 시 게임 상태 자동 백업 및 복원
- 적 위치, 플레이어 위치, 던전 정보 보존
- 안전한 리로드 프로세스
"""

import importlib
import sys
from typing import Dict, Any, Optional
import copy
import traceback

try:
    from game.error_logger import log_system, log_error, log_debug
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

class GameStateBackup:
    """게임 상태 백업 및 복원 클래스"""
    
    def __init__(self):
        self.backup_data = {}
        
    def backup_game_state(self, game_instance) -> bool:
        """게임 상태를 백업합니다"""
        try:
            self.backup_data = {}
            
            if not game_instance:
                print("⚠️ 게임 인스턴스가 없어서 백업을 건너뜁니다")
                return False
                
            # 월드 상태 백업
            if hasattr(game_instance, 'world') and game_instance.world:
                world = game_instance.world
                world_backup = {}
                
                # 적 정보 백업
                if hasattr(world, 'enemies_positions'):
                    world_backup['enemies_positions'] = copy.deepcopy(world.enemies_positions)
                    
                if hasattr(world, 'floor_enemies'):
                    world_backup['floor_enemies'] = copy.deepcopy(world.floor_enemies)
                    
                # 플레이어 위치
                if hasattr(world, 'player_pos'):
                    world_backup['player_pos'] = world.player_pos
                    
                # 던전 정보
                if hasattr(world, 'current_level'):
                    world_backup['current_level'] = world.current_level
                    
                if hasattr(world, 'dungeon_map'):
                    world_backup['dungeon_map'] = copy.deepcopy(world.dungeon_map)
                    
                if hasattr(world, 'explored_tiles'):
                    world_backup['explored_tiles'] = copy.deepcopy(world.explored_tiles)
                    
                self.backup_data['world'] = world_backup
                
            # 파티 정보 백업
            if hasattr(game_instance, 'party_manager') and game_instance.party_manager:
                party_backup = {}
                party = game_instance.party_manager
                
                if hasattr(party, 'members'):
                    # 캐릭터 상태만 백업 (인스턴스는 제외)
                    party_backup['member_states'] = []
                    for member in party.members:
                        if hasattr(member, '__dict__'):
                            member_state = {
                                'name': getattr(member, 'name', ''),
                                'current_hp': getattr(member, 'current_hp', 0),
                                'current_mp': getattr(member, 'current_mp', 0),
                                'current_brv': getattr(member, 'current_brv', 0),
                                'level': getattr(member, 'level', 1),
                                'experience': getattr(member, 'experience', 0),
                                'class_type': getattr(member, 'class_type', None),
                                'position': getattr(member, 'position', (0, 0))
                            }
                            party_backup['member_states'].append(member_state)
                            
                self.backup_data['party'] = party_backup
                
            # 전투 상태 백업
            if hasattr(game_instance, 'combat_system') and game_instance.combat_system:
                combat_backup = {
                    'in_combat': getattr(game_instance.combat_system, 'in_combat', False),
                    'turn_count': getattr(game_instance.combat_system, 'turn_count', 0)
                }
                self.backup_data['combat'] = combat_backup
                
            enemy_count = len(self.backup_data.get('world', {}).get('enemies_positions', []))
            party_count = len(self.backup_data.get('party', {}).get('member_states', []))
            
            print(f"📦 게임 상태 백업 완료: 적 {enemy_count}마리, 파티원 {party_count}명")
            
            if LOGGING_AVAILABLE:
                log_system("상태보존리로드", "게임 상태 백업 완료", {
                    "적수": enemy_count,
                    "파티원수": party_count,
                    "백업항목": list(self.backup_data.keys())
                })
                
            return True
            
        except Exception as e:
            print(f"❌ 게임 상태 백업 실패: {e}")
            if LOGGING_AVAILABLE:
                log_error("상태보존리로드", f"백업 실패: {e}", {"오류": str(e)})
            return False
            
    def restore_game_state(self, game_instance) -> bool:
        """백업된 게임 상태를 복원합니다"""
        try:
            if not self.backup_data:
                print("⚠️ 백업 데이터가 없어서 복원을 건너뜁니다")
                return False
                
            if not game_instance:
                print("⚠️ 게임 인스턴스가 없어서 복원을 건너뜁니다")
                return False
                
            restored_items = []
            
            # 월드 상태 복원
            if 'world' in self.backup_data and hasattr(game_instance, 'world') and game_instance.world:
                world = game_instance.world
                world_backup = self.backup_data['world']
                
                # 적 정보 복원
                if 'enemies_positions' in world_backup and hasattr(world, 'enemies_positions'):
                    world.enemies_positions = copy.deepcopy(world_backup['enemies_positions'])
                    restored_items.append(f"적 위치 {len(world.enemies_positions)}개")
                    
                if 'floor_enemies' in world_backup and hasattr(world, 'floor_enemies'):
                    world.floor_enemies = copy.deepcopy(world_backup['floor_enemies'])
                    
                # 플레이어 위치 복원
                if 'player_pos' in world_backup and hasattr(world, 'player_pos'):
                    world.player_pos = world_backup['player_pos']
                    restored_items.append(f"플레이어 위치 {world.player_pos}")
                    
                # 던전 정보 복원
                if 'current_level' in world_backup and hasattr(world, 'current_level'):
                    world.current_level = world_backup['current_level']
                    restored_items.append(f"던전 레벨 {world.current_level}")
                    
                if 'dungeon_map' in world_backup and hasattr(world, 'dungeon_map'):
                    world.dungeon_map = copy.deepcopy(world_backup['dungeon_map'])
                    
                if 'explored_tiles' in world_backup and hasattr(world, 'explored_tiles'):
                    world.explored_tiles = copy.deepcopy(world_backup['explored_tiles'])
                    
            # 파티 상태 복원 (기본 정보만)
            if 'party' in self.backup_data and hasattr(game_instance, 'party_manager') and game_instance.party_manager:
                party_backup = self.backup_data['party']
                party = game_instance.party_manager
                
                if 'member_states' in party_backup and hasattr(party, 'members'):
                    # 캐릭터가 있으면 상태 정보만 복원
                    member_states = party_backup['member_states']
                    for i, member in enumerate(party.members):
                        if i < len(member_states):
                            state = member_states[i]
                            if hasattr(member, 'current_hp'):
                                member.current_hp = state.get('current_hp', member.current_hp)
                            if hasattr(member, 'current_mp'):
                                member.current_mp = state.get('current_mp', member.current_mp)
                            if hasattr(member, 'current_brv'):
                                member.current_brv = state.get('current_brv', member.current_brv)
                                
                    restored_items.append(f"파티원 상태 {len(member_states)}명")
                    
            print(f"📦 게임 상태 복원 완료: {', '.join(restored_items)}")
            
            if LOGGING_AVAILABLE:
                log_system("상태보존리로드", "게임 상태 복원 완료", {
                    "복원항목": restored_items
                })
                
            return True
            
        except Exception as e:
            print(f"❌ 게임 상태 복원 실패: {e}")
            if LOGGING_AVAILABLE:
                log_error("상태보존리로드", f"복원 실패: {e}", {"오류": str(e)})
            return False

def reload_module_safe(module_name: str) -> bool:
    """모듈을 안전하게 리로드합니다"""
    try:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            return True
        else:
            # 모듈이 로드되지 않은 경우 먼저 import 시도
            print(f"⚠️ {module_name} 모듈이 로드되지 않았습니다. 먼저 import를 시도합니다...")
            try:
                imported_module = importlib.import_module(module_name)
                sys.modules[module_name] = imported_module
                print(f"✅ {module_name} 모듈을 성공적으로 import했습니다")
                return True
            except Exception as import_error:
                print(f"❌ {module_name} 모듈 import 실패: {import_error}")
                return False
    except Exception as e:
        print(f"❌ {module_name} 리로드 실패: {e}")
        if LOGGING_AVAILABLE:
            log_error("상태보존리로드", f"모듈 리로드 실패: {module_name}", {"오류": str(e)})
        return False

def handle_state_preserving_hot_reload(key: str, game_instance=None) -> bool:
    """
    상태 보존 핫 리로드를 처리합니다
    
    Args:
        key: 입력된 키
        game_instance: 현재 게임 인스턴스
        
    Returns:
        bool: 핫 리로드 키가 처리되었는지 여부
    """
    if key.lower() != 'r':
        return False
        
    print("\n🔥 상태 보존 핫 리로드 메뉴 v2.0")
    print("=" * 50)
    print("1. 전투 시스템 (brave_combat)")
    print("2. 월드 시스템 (world) 🗺️")  
    print("3. 캐릭터 시스템 (character)")
    print("4. 아이템 시스템 (item_system)")
    print("5. 스킬 시스템 (skill_system)")
    print("6. AI 시스템 (ai_game_mode)")
    print("7. 모든 시스템 (상태 보존) 📦")
    print("8. 게임 상태 백업만")
    print("9. 게임 상태 복원만")
    print("0. 취소")
    print("=" * 50)
    
    try:
        choice = input("선택하세요: ").strip()
        
        reload_map = {
            '1': 'game.brave_combat',
            '2': 'game.world',
            '3': 'game.character', 
            '4': 'game.item_system',
            '5': 'game.skill_system',
            '6': 'game.ai_game_mode'
        }
        
        state_backup = GameStateBackup()
        
        if choice == '0':
            print("❌ 리로드 취소")
            return True
            
        elif choice == '8':
            # 백업만
            state_backup.backup_game_state(game_instance)
            
        elif choice == '9':
            # 복원만 (이전 백업 사용)
            # 글로벌 백업 인스턴스가 있다면 사용
            print("⚠️ 이전 백업이 있는 경우에만 복원됩니다")
            state_backup.restore_game_state(game_instance)
            
        elif choice == '7':
            # 모든 시스템 리로드 (상태 보존)
            print("📦 게임 상태 백업 중...")
            backup_success = state_backup.backup_game_state(game_instance)
            
            print("🔄 모든 시스템 리로드 중...")
            success_count = 0
            failed_modules = []
            
            for module_name in reload_map.values():
                if reload_module_safe(module_name):
                    success_count += 1
                    print(f"✅ {module_name}")
                else:
                    failed_modules.append(module_name)
                    print(f"❌ {module_name}")
                    
            print(f"📊 리로드 결과: {success_count}/{len(reload_map)} 성공")
            
            if failed_modules:
                print(f"❌ 실패한 모듈: {', '.join(failed_modules)}")
                
            # 상태 복원
            if backup_success:
                print("📦 게임 상태 복원 중...")
                state_backup.restore_game_state(game_instance)
            else:
                print("⚠️ 백업이 실패했어서 상태 복원을 건너뜁니다")
                
            print("🎉 상태 보존 리로드 완료!")
            
        elif choice in reload_map:
            # 개별 시스템 리로드
            module_name = reload_map[choice]
            print(f"🔄 {module_name} 리로드 중...")
            
            # 월드 시스템의 경우 상태 보존
            if module_name == 'game.world':
                print("📦 월드 상태 백업 중...")
                backup_success = state_backup.backup_game_state(game_instance)
                
                if reload_module_safe(module_name):
                    print(f"✅ {module_name} 리로드 완료!")
                    
                    if backup_success:
                        print("📦 월드 상태 복원 중...")
                        state_backup.restore_game_state(game_instance)
                    
                else:
                    print(f"❌ {module_name} 리로드 실패!")
            else:
                # 일반 리로드
                if reload_module_safe(module_name):
                    print(f"✅ {module_name} 리로드 완료!")
                else:
                    print(f"❌ {module_name} 리로드 실패!")
        else:
            print("❌ 잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n❌ 리로드 취소")
    except Exception as e:
        print(f"❌ 리로드 중 오류: {e}")
        print(f"상세 오류: {traceback.format_exc()}")
        if LOGGING_AVAILABLE:
            log_error("상태보존리로드", f"리로드 오류: {e}", {"상세": traceback.format_exc()})
        
    print("\n계속하려면 Enter를 누르세요...")
    input()
    return True

# 글로벌 백업 인스턴스 (선택적으로 사용)
_global_backup = GameStateBackup()

def backup_current_state(game_instance):
    """현재 게임 상태를 글로벌 백업에 저장"""
    return _global_backup.backup_game_state(game_instance)

def restore_backed_state(game_instance):
    """글로벌 백업에서 게임 상태 복원"""
    return _global_backup.restore_game_state(game_instance)

if __name__ == "__main__":
    print("상태 보존 핫 리로드 시스템 v2.0")
    print("이 모듈은 메인 게임에서 import하여 사용하세요")
    print("사용법: handle_state_preserving_hot_reload('r', game_instance)")
