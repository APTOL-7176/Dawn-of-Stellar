"""
저장 시스템 - 확실하고 안전한 저장/불러오기
"""

import json
import os
import pickle
import gzip
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class SaveManager:
    """저장 관리자 - 향상된 안전 저장"""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # 저장 파일 확장자
        self.json_ext = ".json"
        self.binary_ext = ".sav"
        self.compressed_ext = ".sav.gz"
        
        # 백업 디렉토리
        self.backup_dir = self.save_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # 최대 백업 수
        self.max_backups = 10
        
        # 레거시 지원
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """저장 디렉토리 생성 (레거시)"""
        if not os.path.exists(str(self.save_dir)):
            os.makedirs(str(self.save_dir))
    
    def _generate_checksum(self, data: bytes) -> str:
        """체크섬 생성"""
        return hashlib.sha256(data).hexdigest()
    
    def _create_save_data(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """저장 데이터 생성"""
        save_data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "checksum": "",
            "game_state": game_state
        }
        
        # 체크섬 계산 (game_state만)
        state_json = json.dumps(game_state, sort_keys=True, default=str)
        save_data["checksum"] = hashlib.sha256(state_json.encode()).hexdigest()
        
        return save_data
    
    def _create_backup(self, save_path: Path):
        """백업 생성"""
        try:
            if not save_path.exists():
                return
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{save_path.stem}_{timestamp}{save_path.suffix}"
            backup_path = self.backup_dir / backup_name
            
            # 파일 복사
            import shutil
            shutil.copy2(save_path, backup_path)
            
            # 오래된 백업 정리
            self._cleanup_old_backups(save_path.stem)
            
        except Exception as e:
            print(f"백업 생성 실패: {e}")
    
    def _cleanup_old_backups(self, save_name: str):
        """오래된 백업 정리"""
        try:
            # 해당 저장 파일의 백업들 찾기
            backups = list(self.backup_dir.glob(f"{save_name}_*"))
            
            # 수정 시간으로 정렬 (최신부터)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 최대 개수를 초과하는 백업 삭제
            for backup in backups[self.max_backups:]:
                backup.unlink()
                print(f"오래된 백업 삭제: {backup.name}")
                
        except Exception as e:
            print(f"백업 정리 실패: {e}")
    
    def _verify_save_data(self, save_data: Dict[str, Any]) -> bool:
        """저장 데이터 무결성 검증"""
        try:
            if "game_state" not in save_data or "checksum" not in save_data:
                return False
            
            # 체크섬 검증
            state_json = json.dumps(save_data["game_state"], sort_keys=True, default=str)
            calculated_checksum = hashlib.sha256(state_json.encode()).hexdigest()
            
            return calculated_checksum == save_data["checksum"]
            
        except Exception:
            return False
    
    def save_game(self, game_state: Dict[str, Any], save_name: str = None) -> bool:
        """게임 저장"""
        try:
            print(f"🔍 저장 시작 - save_name: {save_name}")
            
            if save_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"save_{timestamp}"
                print(f"📅 자동 파일명 생성: {save_name}")
            
            # .json 확장자 추가
            if not save_name.endswith('.json'):
                save_name += '.json'
            
            save_path = os.path.join(self.save_dir, save_name)
            print(f"💾 저장 경로: {save_path}")
            
            # 저장 디렉토리 확인
            if not os.path.exists(self.save_dir):
                print(f"📁 저장 디렉토리 생성: {self.save_dir}")
                os.makedirs(self.save_dir)
            
            # 저장 시간 추가
            game_state['save_time'] = datetime.now().isoformat()
            game_state['save_name'] = save_name
            
            print(f"📝 파일 쓰기 시작...")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 게임이 저장되었습니다: {save_name}")
            return True
            
        except PermissionError as e:
            print(f"❌ 권한 오류: {e}")
            print(f"💡 파일이 다른 프로그램에서 사용 중이거나 관리자 권한이 필요할 수 있습니다.")
            return False
        except OSError as e:
            print(f"❌ 파일 시스템 오류: {e}")
            print(f"💡 디스크 공간이 부족하거나 파일명이 잘못되었을 수 있습니다.")
            return False
        except Exception as e:
            print(f"❌ 예상치 못한 저장 실패: {e}")
            print(f"💡 오류 타입: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """게임 불러오기"""
        try:
            if not save_name.endswith('.json'):
                save_name += '.json'
            
            save_path = os.path.join(self.save_dir, save_name)
            
            if not os.path.exists(save_path):
                print(f"❌ 저장 파일을 찾을 수 없습니다: {save_name}")
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            print(f"✅ 게임을 불러왔습니다: {save_name}")
            return game_state
            
        except Exception as e:
            print(f"❌ 불러오기 실패: {e}")
            return None
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """저장 파일 목록"""
        saves = []
        
        try:
            if not os.path.exists(self.save_dir):
                return saves
            
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    save_path = os.path.join(self.save_dir, filename)
                    try:
                        with open(save_path, 'r', encoding='utf-8') as f:
                            save_data = json.load(f)
                        
                        save_info = {
                            'filename': filename,
                            'save_name': save_data.get('save_name', filename),
                            'save_time': save_data.get('save_time', '알 수 없음'),
                            'level': save_data.get('current_level', 1),
                            'score': save_data.get('score', 0),
                            'party_names': save_data.get('party_character_names', [])
                        }
                        saves.append(save_info)
                        
                    except Exception as e:
                        print(f"저장 파일 읽기 오류: {filename} - {e}")
            
            # 저장 시간 순으로 정렬 (최신 순)
            saves.sort(key=lambda x: x['save_time'], reverse=True)
            
        except Exception as e:
            print(f"저장 파일 목록 오류: {e}")
        
        return saves
    
    def delete_save(self, save_name: str) -> bool:
        """저장 파일 삭제"""
        try:
            if not save_name.endswith('.json'):
                save_name += '.json'
            
            save_path = os.path.join(self.save_dir, save_name)
            
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"✅ 저장 파일이 삭제되었습니다: {save_name}")
                return True
            else:
                print(f"❌ 저장 파일을 찾을 수 없습니다: {save_name}")
                return False
                
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")
            return False


class GameStateSerializer:
    """게임 상태 직렬화/역직렬화"""
    
    @staticmethod
    def serialize_character(character) -> Dict[str, Any]:
        """캐릭터 객체를 딕셔너리로 변환"""
        # active_traits를 직렬화 가능한 형태로 변환
        active_traits_data = []
        if hasattr(character, 'active_traits') and character.active_traits:
            for trait in character.active_traits:
                if hasattr(trait, 'name'):
                    active_traits_data.append({
                        'name': trait.name,
                        'description': getattr(trait, 'description', ''),
                        'effect_type': getattr(trait, 'effect_type', ''),
                        'is_active': getattr(trait, 'is_active', True)
                    })
                elif isinstance(trait, dict):
                    # 이미 dict 형태인 경우
                    active_traits_data.append({
                        'name': trait.get('name', ''),
                        'description': trait.get('description', ''),
                        'effect_type': trait.get('effect_type', ''),
                        'is_active': trait.get('is_active', True)
                    })
        
        # available_traits를 직렬화 가능한 형태로 변환
        available_traits_data = []
        if hasattr(character, 'available_traits') and character.available_traits:
            for trait in character.available_traits:
                if hasattr(trait, 'name'):
                    available_traits_data.append({
                        'name': trait.name,
                        'description': getattr(trait, 'description', ''),
                        'effect_type': getattr(trait, 'effect_type', ''),
                        'is_active': getattr(trait, 'is_active', False)
                    })
                elif isinstance(trait, dict):
                    # 이미 dict 형태인 경우
                    available_traits_data.append({
                        'name': trait.get('name', ''),
                        'description': trait.get('description', ''),
                        'effect_type': trait.get('effect_type', ''),
                        'is_active': trait.get('is_active', False)
                    })
        
        return {
            'name': character.name,
            'character_class': getattr(character, 'character_class', 'Warrior'),
            'max_hp': character.max_hp,
            'current_hp': character.current_hp,
            'wounds': getattr(character, 'wounds', 0),
            'physical_attack': getattr(character, 'physical_attack', 10),
            'magic_attack': getattr(character, 'magic_attack', 10),
            'physical_defense': getattr(character, 'physical_defense', 10),
            'magic_defense': getattr(character, 'magic_defense', 10),
            'speed': character.speed,
            'current_brave': getattr(character, 'current_brave', 400),
            'max_brave': getattr(character, 'max_brave', 500),
            'initial_brave': getattr(character, 'initial_brave', 400),
            'is_broken': getattr(character, 'is_broken', False),
            'active_traits': active_traits_data,
            'available_traits': available_traits_data,
            'preferred_damage_type': getattr(character, 'preferred_damage_type', 'physical'),
            'experience': getattr(character, 'experience', 0),
            'level': getattr(character, 'level', 1),
            'max_mp': getattr(character, 'max_mp', 20),
            'current_mp': getattr(character, 'current_mp', 20),
            'critical_rate': getattr(character, 'critical_rate', 5),
            'accuracy': getattr(character, 'accuracy', 85),
            'evasion': getattr(character, 'evasion', 10)
        }
    
    @staticmethod
    def deserialize_character(char_data: Dict[str, Any]):
        """딕셔너리에서 캐릭터 객체 생성"""
        # Character 클래스 동적 임포트
        try:
            from .character import Character
            character = Character(
                name=char_data['name'],
                character_class=char_data.get('character_class', 'Warrior'),
                max_hp=char_data['max_hp'],
                physical_attack=char_data.get('physical_attack', 10),
                magic_attack=char_data.get('magic_attack', 10),
                physical_defense=char_data.get('physical_defense', 10),
                magic_defense=char_data.get('magic_defense', 10),
                speed=char_data['speed']
            )
        except ImportError:
            # 임시 캐릭터 딕셔너리로 반환
            character = type('Character', (), char_data)()
        
        # 상태 복원
        character.current_hp = char_data['current_hp']
        character.wounds = char_data.get('wounds', 0)
        character.current_brave = char_data.get('current_brave', 400)
        character.max_brave = char_data.get('max_brave', 500)
        character.initial_brave = char_data.get('initial_brave', 400)
        character.is_broken = char_data.get('is_broken', False)
        
        # 특성 데이터 복원 (간단한 딕셔너리 형태로 저장)
        character.active_traits = char_data.get('active_traits', [])
        character.available_traits = char_data.get('available_traits', [])
        
        character.preferred_damage_type = char_data.get('preferred_damage_type', 'physical')
        character.experience = char_data.get('experience', 0)
        character.level = char_data.get('level', 1)
        character.current_mp = char_data.get('current_mp', 20)
        character.max_mp = char_data.get('max_mp', 20)
        character.critical_rate = char_data.get('critical_rate', 5)
        character.accuracy = char_data.get('accuracy', 85)
        character.evasion = char_data.get('evasion', 10)
        
        return character
    
    @staticmethod
    def create_game_state(game) -> Dict[str, Any]:
        """게임 객체에서 저장 가능한 상태 생성"""
        try:
            # 필수 속성 확인
            if not hasattr(game, 'world') or game.world is None:
                raise ValueError("게임 월드가 초기화되지 않았습니다.")
            
            if not hasattr(game, 'party_manager') or game.party_manager is None:
                raise ValueError("파티 매니저가 초기화되지 않았습니다.")
                
            if not game.party_manager.members:
                raise ValueError("파티에 멤버가 없습니다.")
            
            print(f"🔍 게임 상태 검증 완료 - 레벨: {game.world.current_level}, 파티원: {len(game.party_manager.members)}명")
            
            return {
                'version': '1.0',
                'current_level': game.world.current_level,
                'score': getattr(game, 'score', 0),
                'enemies_defeated': getattr(game, 'enemies_defeated', 0),
                'items_collected': getattr(game, 'items_collected', 0),
                'floors_cleared': getattr(game, 'floors_cleared', 0),
                'steps_since_last_encounter': getattr(game, 'steps_since_last_encounter', 0),
                'player_position': game.world.player_pos,
                'party_characters': [
                    GameStateSerializer.serialize_character(char) 
                    for char in game.party_manager.members
                ],
                'party_character_names': [char.name for char in game.party_manager.members],
                'world_state': {
                    'current_level': game.world.current_level,
                    'enemies_positions': getattr(game.world, 'enemies_positions', {}),
                    'items_positions': getattr(game.world, 'items_positions', {}),
                    'explored_tiles': GameStateSerializer.serialize_explored_tiles(game.world)
                }
            }
        except Exception as e:
            print(f"❌ 게임 상태 생성 중 오류: {e}")
            raise
    
    @staticmethod
    def serialize_explored_tiles(world) -> List[List[bool]]:
        """탐험된 타일 정보 직렬화"""
        explored = []
        for y in range(world.height):
            row = []
            for x in range(world.width):
                row.append(world.tiles[y][x].explored)
            explored.append(row)
        return explored
    
    @staticmethod
    def restore_explored_tiles(world, explored_data: List[List[bool]]):
        """탐험된 타일 정보 복원"""
        try:
            for y in range(min(world.height, len(explored_data))):
                for x in range(min(world.width, len(explored_data[y]))):
                    world.tiles[y][x].explored = explored_data[y][x]
        except Exception as e:
            print(f"타일 복원 오류: {e}")


def show_save_menu(save_manager: SaveManager) -> Optional[str]:
    """저장 메뉴 표시 - 커서 방식"""
    try:
        from .cursor_menu_system import create_simple_menu
        
        # 커서 메뉴 생성
        options = [
            "💨 빠른 저장 (자동 이름)",
            "📝 이름 지정해서 저장", 
            "🔄 기존 저장 파일 덮어쓰기",
            "❌ 취소"
        ]
        
        descriptions = [
            "현재 시간으로 자동 이름 생성",
            "사용자가 직접 파일명 입력",
            "기존 저장 파일 목록에서 선택",
            "저장을 취소하고 돌아갑니다"
        ]
        
        menu = create_simple_menu("💾 게임 저장", options, descriptions)
        result = menu.run()
        
        if result == -1 or result == 3:  # 취소
            return "CANCEL"
        elif result == 0:  # 빠른 저장
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"autosave_{timestamp}"
        elif result == 1:  # 이름 지정 저장
            from .input_utils import KeyboardInput
            keyboard = KeyboardInput()
            print("\n저장 파일 이름을 입력하세요: ", end='', flush=True)
            save_name = keyboard.get_string_input()
            if save_name:
                return save_name
            else:
                print("올바른 파일명을 입력하세요.")
                return None
        elif result == 2:  # 기존 파일 덮어쓰기
            saves = save_manager.list_saves()
            if not saves:
                print("\n기존 저장 파일이 없습니다.")
                from .input_utils import KeyboardInput
                KeyboardInput().wait_for_key("아무 키나 눌러 계속...")
                return None
            
            # 기존 파일 선택을 위한 커서 메뉴
            file_options = []
            file_descriptions = []
            for save_info in saves:
                file_options.append(f"📁 {save_info['filename']}")
                file_descriptions.append(f"레벨 {save_info['level']}, 점수 {save_info['score']}")
            
            file_options.append("❌ 취소")
            file_descriptions.append("덮어쓰기를 취소합니다")
            
            file_menu = create_simple_menu("기존 저장 파일 선택", file_options, file_descriptions)
            file_result = file_menu.run()
            
            if file_result == -1 or file_result >= len(saves):
                return None
            else:
                return saves[file_result]['filename']
        
        return None
        
    except ImportError:
        # 폴백: 기존 텍스트 메뉴
        return _show_save_menu_fallback(save_manager)

def _show_save_menu_fallback(save_manager: SaveManager) -> Optional[str]:
    """저장 메뉴 폴백 (기존 방식)"""
    from .input_utils import KeyboardInput
    
    keyboard = KeyboardInput()
    
    print("\n" + "="*50)
    print("💾 게임 저장")
    print("="*50)
    
    print("1. 빠른 저장 (자동 이름)")
    print("2. 이름 지정해서 저장")
    print("3. 기존 저장 파일 덮어쓰기")
    print("0. 취소")
    
    while True:
        print("\n선택하세요 (1-3, 0): ", end='', flush=True)
        try:
            choice = keyboard.get_key().strip()
            
            if choice == '1':
                # 자동 이름 생성
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                return f"autosave_{timestamp}"
            elif choice == '2':
                print("저장 파일 이름을 입력하세요: ", end='', flush=True)
                save_name = keyboard.get_string_input()
                if save_name:
                    return save_name
                else:
                    print("올바른 파일명을 입력하세요.")
                    continue
            elif choice == '3':
                saves = save_manager.list_saves()
                if not saves:
                    print("기존 저장 파일이 없습니다.")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
                    continue
                
                print("\n기존 저장 파일:")
                for i, save_info in enumerate(saves, 1):
                    print(f"{i}. {save_info['filename']} (레벨 {save_info['level']}, 점수 {save_info['score']})")
                
                try:
                    print("덮어쓸 파일 번호: ", end='', flush=True)
                    idx_str = keyboard.get_key()
                    idx = int(idx_str) - 1
                    if 0 <= idx < len(saves):
                        return saves[idx]['filename']
                    else:
                        print("잘못된 번호입니다.")
                        keyboard.wait_for_key("아무 키나 눌러 계속...")
                        continue
                except ValueError:
                    print("숫자를 입력하세요.")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
                    continue
            elif choice == '0':
                return "CANCEL"
            else:
                print("잘못된 선택입니다. 1-3 또는 0을 입력하세요.")
                keyboard.wait_for_key("아무 키나 눌러 계속...")
                continue
        except KeyboardInterrupt:
            return "CANCEL"


def show_load_menu(save_manager: SaveManager) -> Optional[str]:
    """불러오기 메뉴 표시 - 커서 방식"""
    saves = save_manager.list_saves()
    
    if not saves:
        print("\n저장된 게임이 없습니다.")
        from .input_utils import KeyboardInput
        KeyboardInput().wait_for_key("아무 키나 눌러 계속...")
        return None
    
    try:
        from .cursor_menu_system import create_simple_menu
        
        # 저장 파일 목록을 커서 메뉴로 생성
        options = []
        descriptions = []
        
        for save_info in saves:
            save_time = save_info['save_time']
            if save_time != '알 수 없음':
                try:
                    dt = datetime.datetime.fromisoformat(save_time)
                    save_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            party_str = ", ".join(save_info['party_names'][:2])
            if len(save_info['party_names']) > 2:
                party_str += "..."
            
            options.append(f"📁 {save_info['filename']}")
            descriptions.append(f"레벨 {save_info['level']}, 점수 {save_info['score']} | 파티: {party_str} | {save_time}")
        
        options.append("❌ 취소")
        descriptions.append("불러오기를 취소하고 돌아갑니다")
        
        menu = create_simple_menu("📁 게임 불러오기", options, descriptions)
        result = menu.run()
        
        if result == -1 or result >= len(saves):  # 취소
            return None
        else:
            return saves[result]['filename']
            
    except ImportError:
        # 폴백: 기존 텍스트 메뉴
        return _show_load_menu_fallback(save_manager, saves)

def _show_load_menu_fallback(save_manager: SaveManager, saves: List) -> Optional[str]:
    """불러오기 메뉴 폴백 (기존 방식)"""
    from .input_utils import KeyboardInput
    keyboard = KeyboardInput()
    
    print("\n" + "="*50)
    print("📁 게임 불러오기")
    print("="*50)
    
    for i, save_info in enumerate(saves, 1):
        save_time = save_info['save_time']
        if save_time != '알 수 없음':
            try:
                dt = datetime.datetime.fromisoformat(save_time)
                save_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        party_str = ", ".join(save_info['party_names'][:2])
        if len(save_info['party_names']) > 2:
            party_str += "..."
        
        print(f"{i}. {save_info['filename']}")
        print(f"   레벨: {save_info['level']}, 점수: {save_info['score']}")
        print(f"   파티: {party_str}")
        print(f"   저장 시간: {save_time}")
        print()
    
    print("0. 취소")
    
    try:
        print("불러올 저장 파일 번호: ", end="", flush=True)
        choice_str = keyboard.get_key()
        choice = int(choice_str)
        
        if choice == 0:
            return None
        elif 1 <= choice <= len(saves):
            return saves[choice - 1]['filename']
        else:
            print("잘못된 선택입니다.")
            keyboard.wait_for_key("아무 키나 눌러 계속...")
            return None
    except ValueError:
        print("숫자를 입력해주세요.")
        keyboard.wait_for_key("아무 키나 눌러 계속...")
        return None


# 전역 저장 관리자 인스턴스
_global_save_manager = None
_global_auto_save_manager = None


def get_save_manager() -> SaveManager:
    """글로벌 저장 관리자 가져오기"""
    global _global_save_manager
    if _global_save_manager is None:
        _global_save_manager = SaveManager("saves")
    return _global_save_manager


def get_auto_save_manager() -> SaveManager:
    """글로벌 자동 저장 관리자 가져오기"""
    global _global_auto_save_manager
    if _global_auto_save_manager is None:
        _global_auto_save_manager = SaveManager("auto_saves")
    return _global_auto_save_manager
