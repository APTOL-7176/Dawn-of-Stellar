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
from enum import Enum


class GameStateEncoder(json.JSONEncoder):
    """게임 상태를 JSON으로 직렬화하기 위한 커스텀 인코더"""
    def default(self, obj):
        # 🔥 ULTIMATE ItemRarity 처리 (모든 케이스 커버)
        try:
            obj_repr = repr(obj)
            obj_str = str(obj)
            obj_type = str(type(obj))
            
            # ItemRarity 감지 (5가지 방법)
            if any(keyword in text for keyword in ['ItemRarity', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'COMMON'] 
                   for text in [obj_repr, obj_str, obj_type]):
                
                # 값 추출 시도 (10가지 방법)
                value = None
                
                # 방법 1: .value 속성
                if hasattr(obj, 'value'):
                    value = obj.value
                # 방법 2: .name 속성  
                elif hasattr(obj, 'name'):
                    value = obj.name
                # 방법 3: 문자열 파싱 (ItemRarity.UNCOMMON)
                elif '.' in obj_str:
                    value = obj_str.split('.')[-1]
                # 방법 4: 직접 문자열 값
                elif obj_str in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY']:
                    value = obj_str
                # 방법 5: repr 파싱
                elif '.' in obj_repr:
                    value = obj_repr.split('.')[-1].replace('>', '').replace("'", "")
                # 방법 6: 숫자 값 (enum 정수값)
                elif isinstance(obj, int) and 0 <= obj <= 4:
                    rarity_map = {0: 'COMMON', 1: 'UNCOMMON', 2: 'RARE', 3: 'EPIC', 4: 'LEGENDARY'}
                    value = rarity_map.get(obj, 'COMMON')
                # 방법 7: 강제 변환
                else:
                    value = 'UNCOMMON'  # 기본값
                
                return {"__enum__": "ItemRarity", "value": value}
        except:
            # ItemRarity 처리 실패 시 기본값 반환
            if 'ItemRarity' in str(obj) or 'UNCOMMON' in str(obj):
                return {"__enum__": "ItemRarity", "value": "UNCOMMON"}
        
        # 모든 Enum 타입 처리 (표준)
        if isinstance(obj, Enum):
            return {
                "__enum__": obj.__class__.__name__, 
                "__module__": getattr(obj.__class__, '__module__', 'unknown'),
                "value": obj.value
            }
        
        # 특별히 ItemRarity 처리 (다중 폴백)
        try:
            # 방법 1: 클래스 이름 직접 확인
            if hasattr(obj, '__class__') and 'ItemRarity' in str(obj.__class__):
                if hasattr(obj, 'value'):
                    return {"__enum__": "ItemRarity", "value": obj.value}
                elif hasattr(obj, 'name'):
                    return {"__enum__": "ItemRarity", "value": obj.name}
            
            # 방법 2: 문자열 표현 파싱
            obj_str = str(obj)
            if 'ItemRarity.' in obj_str:
                # ItemRarity.UNCOMMON -> UNCOMMON
                parts = obj_str.split('.')
                if len(parts) >= 2:
                    return {"__enum__": "ItemRarity", "value": parts[-1]}
            
            # 방법 3: 타입 이름 확인
            type_name = type(obj).__name__
            if 'ItemRarity' in type_name:
                # 값 추출 시도
                for attr in ['value', 'name', '_value_', '_name_']:
                    if hasattr(obj, attr):
                        return {"__enum__": "ItemRarity", "value": getattr(obj, attr)}
                        
        except Exception as e:
            # 마지막 폴백: 문자열로 저장
            return {"__fallback__": "ItemRarity", "string_value": str(obj)}
        
        # Inventory 객체 처리
        if hasattr(obj, '__class__') and obj.__class__.__name__ == 'Inventory':
            return {
                "__class__": "Inventory",
                "items": getattr(obj, 'items', {}),
                "max_size": getattr(obj, 'max_size', 15),
                "max_weight": getattr(obj, 'max_weight', 100.0)
            }
        
        # 일반 객체 처리
        if hasattr(obj, '__dict__'):
            # 객체의 속성을 딕셔너리로 변환
            return {
                "__class__": obj.__class__.__name__,
                **{k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
            }
        
        # 최종 fallback - 문자열로 변환
        try:
            return str(obj)
        except:
            return None


def decode_game_state(dct):
    """JSON에서 게임 상태를 복원하기 위한 디코더"""
    if "__enum__" in dct:
        # Enum 복원
        enum_name = dct["__enum__"]
        enum_value = dct["value"]
        
        # ItemRarity 복원
        if enum_name == "ItemRarity":
            try:
                from game.items import ItemRarity
                return ItemRarity(enum_value)
            except:
                try:
                    from game.item_system import ItemRarity
                    return ItemRarity(enum_value)
                except:
                    # 복원 실패시 문자열로 대체
                    return enum_value
                    
        # 다른 Enum들도 복원 가능하도록 일반화
        try:
            # 동적으로 Enum 클래스 찾기
            import importlib
            for module_name in ['game.items', 'game.item_system', 'game.character', 'game.combat']:
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, enum_name):
                        enum_class = getattr(module, enum_name)
                        return enum_class(enum_value)
                except:
                    continue
        except:
            pass
            
        # 복원 실패시 원래 값 반환
        return enum_value
    
    # Inventory 객체 복원
    if "__class__" in dct and dct["__class__"] == "Inventory":
        try:
            from game.items import Inventory
            inventory = Inventory(
                max_size=dct.get("max_size", 15),
                max_weight=dct.get("max_weight", 100.0)
            )
            inventory.items = dct.get("items", {})
            return inventory
        except Exception as e:
            print(f"⚠️ 인벤토리 복원 오류: {e}")
            # 기본 인벤토리 반환
            try:
                from game.items import Inventory
                return Inventory()
            except:
                return dct  # 복원 실패시 원본 딕셔너리 반환
        
    return dct


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
            "version": "2.2.0",  # 새로운 스킬 시스템 반영
            "timestamp": datetime.now().isoformat(),
            "checksum": "",
            "game_state": game_state,
            "skill_system_version": "new_skill_system",  # 스킬 시스템 버전 표시
            "organic_effects_enabled": True  # Organic Effects 활성화 표시
        }
        
        # 체크섬 계산 (game_state만)
        state_json = json.dumps(game_state, sort_keys=True, default=str)
        save_data["checksum"] = hashlib.sha256(state_json.encode()).hexdigest()
        
        return save_data
    
    def get_save_files(self):
        """저장 파일 목록 반환"""
        save_files = []
        
        # JSON 파일 검색
        for json_file in self.save_dir.glob(f"*{self.json_ext}"):
            try:
                # 파일 정보 읽기
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                save_info = {
                    'filename': json_file.name,
                    'path': str(json_file),
                    'timestamp': data.get('timestamp', 'Unknown'),
                    'version': data.get('version', 'Unknown'),
                    'type': 'json'
                }
                save_files.append(save_info)
            except Exception:
                # 파일 읽기 실패 시 기본 정보만 추가
                save_info = {
                    'filename': json_file.name,
                    'path': str(json_file),
                    'timestamp': 'Unknown',
                    'version': 'Unknown',
                    'type': 'json'
                }
                save_files.append(save_info)
        
        # 바이너리 파일 검색
        for bin_file in self.save_dir.glob(f"*{self.binary_ext}"):
            save_info = {
                'filename': bin_file.name,
                'path': str(bin_file),
                'timestamp': 'Binary file',
                'version': 'Binary',
                'type': 'binary'
            }
            save_files.append(save_info)
        
        # 압축 파일 검색
        for gz_file in self.save_dir.glob(f"*{self.compressed_ext}"):
            save_info = {
                'filename': gz_file.name,
                'path': str(gz_file),
                'timestamp': 'Compressed file',
                'version': 'Compressed',
                'type': 'compressed'
            }
            save_files.append(save_info)
        
        # 타임스탬프 기준으로 정렬 (최신순)
        save_files.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return save_files

    def get_save_info(self, save_path: str):
        """저장 파일 정보 반환"""
        try:
            # 파일 경로 처리
            if isinstance(save_path, str):
                save_file_path = Path(save_path)
            else:
                save_file_path = save_path
            
            # 상대 경로인 경우 save_dir 기준으로 처리
            if not save_file_path.is_absolute():
                save_file_path = self.save_dir / save_file_path
            
            # 파일 존재 확인
            if not save_file_path.exists():
                return {
                    'exists': False,
                    'error': f'파일을 찾을 수 없습니다: {save_file_path}'
                }
            
            # 파일 확장자에 따른 처리
            if save_file_path.suffix == self.json_ext:
                # JSON 파일
                try:
                    with open(save_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    return {
                        'exists': True,
                        'filename': save_file_path.name,
                        'path': str(save_file_path),
                        'type': 'json',
                        'timestamp': data.get('timestamp', 'Unknown'),
                        'version': data.get('version', 'Unknown'),
                        'checksum': data.get('checksum', 'None'),
                        'size': save_file_path.stat().st_size,
                        'game_state': data.get('game_state', {})
                    }
                except json.JSONDecodeError as e:
                    return {
                        'exists': True,
                        'filename': save_file_path.name,
                        'path': str(save_file_path),
                        'type': 'json',
                        'error': f'JSON 파싱 오류: {e}',
                        'size': save_file_path.stat().st_size
                    }
            else:
                # 바이너리 또는 압축 파일
                file_type = 'binary' if save_file_path.suffix == self.binary_ext else 'compressed'
                return {
                    'exists': True,
                    'filename': save_file_path.name,
                    'path': str(save_file_path),
                    'type': file_type,
                    'timestamp': 'Binary/Compressed file',
                    'version': 'Binary/Compressed',
                    'size': save_file_path.stat().st_size
                }
                
        except Exception as e:
            return {
                'exists': False,
                'error': f'파일 정보 읽기 오류: {e}'
            }

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
    
    def _migrate_save_data(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """구 버전 저장 데이터를 새 버전으로 마이그레이션"""
        version = save_data.get("version", "1.0")
        
        if version == "1.0":
            print("🔄 v1.0 저장 파일을 v2.2.0으로 마이그레이션 중...")
            
            # 새로운 스킬 시스템 속성들을 기본값으로 추가
            game_state = save_data.get("game_state", {})
            
            # 파티 캐릭터들에 새로운 속성 추가
            if "party_data" in game_state:
                for char_data in game_state["party_data"]:
                    if isinstance(char_data, dict):
                        # 새로운 스킬 시스템 속성들 추가
                        if "brave_skills" not in char_data:
                            char_data["brave_skills"] = {}
                        if "casting_data" not in char_data:
                            char_data["casting_data"] = {
                                'casting_skill': None,
                                'casting_targets': None,
                                'casting_start_time': None,
                                'casting_duration': None,
                                'is_casting': False
                            }
                        if "status_effects" not in char_data:
                            char_data["status_effects"] = {
                                'stunned': False, 'silenced': False, 'paralyzed': False,
                                'sleeping': False, 'frozen': False, 'blinded': False,
                                'charmed': False, 'feared': False, 'cursed': False,
                                'blessed': False, 'weakened': False, 'strengthened': False,
                                'hasted': False, 'slowed': False, 'shielded': False, 'poisoned': False
                            }
                        if "element_data" not in char_data:
                            char_data["element_data"] = {
                                'element_affinity': 'neutral',
                                'element_weaknesses': [],
                                'element_resistances': []
                            }
                        if "atb_gauge" not in char_data:
                            char_data["atb_gauge"] = 0
                        if "atb_speed" not in char_data:
                            char_data["atb_speed"] = char_data.get("speed", 10)
                        if "steps_taken" not in char_data:
                            char_data["steps_taken"] = 0
            
            # 버전 업데이트
            save_data["version"] = "2.2.0"
            save_data["skill_system_version"] = "new_skill_system"
            save_data["organic_effects_enabled"] = True
            
            print("✅ 마이그레이션 완료!")
        
        return save_data
    
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
                try:
                    json.dump(game_state, f, indent=2, ensure_ascii=False, cls=GameStateEncoder)
                except TypeError as e:
                    # JSON 직렬화 실패 시 fallback
                    print(f"⚠️ JSON 직렬화 오류, fallback 사용: {e}")
                    json.dump(game_state, f, indent=2, ensure_ascii=False, default=str)
            
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
                save_data = json.load(f, object_hook=decode_game_state)
            
            # 구 버전 저장 파일 마이그레이션
            if isinstance(save_data, dict) and "version" in save_data:
                save_data = self._migrate_save_data(save_data)
                game_state = save_data.get("game_state", save_data)
            else:
                # 구 형식 저장 파일 (game_state가 최상위에 있는 경우)
                print("🔄 구 형식 저장 파일 감지 - 마이그레이션 적용")
                legacy_save = {
                    "version": "1.0",
                    "game_state": save_data,
                    "checksum": ""
                }
                migrated_save = self._migrate_save_data(legacy_save)
                game_state = migrated_save["game_state"]
            
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
        
        # 인벤토리 정보 직렬화 (강화된 안전성)
        inventory_data = {}
        if hasattr(character, 'inventory') and character.inventory:
            try:
                # 인벤토리 items 딕셔너리 안전하게 복사
                items_dict = {}
                if hasattr(character.inventory, 'items') and character.inventory.items:
                    items_dict = character.inventory.items.copy()
                
                inventory_data = {
                    'items': items_dict,
                    'max_size': getattr(character.inventory, 'max_size', 15),
                    'max_weight': getattr(character.inventory, 'max_weight', 100.0)
                }
                
                # 저장 로그 출력
                item_count = len(items_dict)
                total_quantity = sum(items_dict.values()) if items_dict else 0
                print(f"💾 [SAVE] {character.name} 인벤토리: {item_count}종류, {total_quantity}개 아이템 저장")
                
            except Exception as e:
                print(f"⚠️ {character.name} 인벤토리 직렬화 오류: {e}")
                inventory_data = {'items': {}, 'max_size': 15, 'max_weight': 100.0}
        
        # 장비 정보 직렬화
        def serialize_equipment(equipment):
            """장비 아이템을 직렬화"""
            if equipment is None:
                return None
            try:
                return {
                    'name': equipment.name,
                    'item_type': equipment.item_type.value if hasattr(equipment.item_type, 'value') else str(equipment.item_type),
                    'stats': equipment.stats if hasattr(equipment, 'stats') else {},
                    # Enum을 안전하게 문자열로 저장
                    'rarity': (getattr(equipment, 'rarity').name.lower() if hasattr(getattr(equipment, 'rarity', None), 'name') else str(getattr(equipment, 'rarity', 'common'))),
                    'description': getattr(equipment, 'description', ''),
                    'effects': getattr(equipment, 'effects', {}),
                    'durability': getattr(equipment, 'durability', 100),
                    'max_durability': getattr(equipment, 'max_durability', 100)
                }
            except Exception as e:
                print(f"⚠️ 장비 {equipment} 직렬화 오류: {e}")
                return None
        
        equipment_data = {
            'equipped_weapon': serialize_equipment(getattr(character, 'equipped_weapon', None)),
            'equipped_armor': serialize_equipment(getattr(character, 'equipped_armor', None)),
            'equipped_accessory': serialize_equipment(getattr(character, 'equipped_accessory', None))
        }
        
        # 장비 저장 로그
        print(f"🎒 [SAVE LOG] {character.name} 장비 저장:")
        print(f"🎒 [SAVE LOG] - Weapon: {getattr(character, 'equipped_weapon', None)}")
        print(f"🎒 [SAVE LOG] - Armor: {getattr(character, 'equipped_armor', None)}")
        print(f"🎒 [SAVE LOG] - Accessory: {getattr(character, 'equipped_accessory', None)}")
        
        # 골드 정보
        gold = getattr(character, 'gold', 0)
        
        # 새로운 스킬 시스템 관련 속성들
        brave_skills_data = []
        if hasattr(character, 'brave_skills') and character.brave_skills:
            try:
                # brave_skills는 딕셔너리 형태로 저장되어 있음
                brave_skills_data = character.brave_skills.copy() if isinstance(character.brave_skills, dict) else {}
            except Exception as e:
                print(f"⚠️ {character.name} brave_skills 직렬화 오류: {e}")
                brave_skills_data = {}
        
        # 캐스팅 시스템 관련 속성들 (현재 상태는 저장하지 않고 기본값으로 복원)
        casting_data = {
            'casting_skill': None,  # 현재 캐스팅은 저장하지 않음
            'casting_targets': None,
            'casting_start_time': None,
            'casting_duration': None,
            'is_casting': False
        }
        
        # 새로운 상태이상 관련 속성들
        status_effects_data = {}
        status_attributes = [
            'stunned', 'silenced', 'paralyzed', 'sleeping', 'frozen', 'blinded',
            'charmed', 'feared', 'cursed', 'blessed', 'weakened', 'strengthened',
            'hasted', 'slowed', 'shielded', 'poisoned'
        ]
        for attr in status_attributes:
            status_effects_data[attr] = getattr(character, attr, False)
        
        # 상태 효과 딕셔너리 저장 (독 등의 복잡한 상태 효과용)
        if hasattr(character, 'status_effects') and character.status_effects:
            status_effects_data['complex_effects'] = character.status_effects.copy()
        
        # 베놈 파워 (도적 전용)
        venom_data = {
            'venom_power': getattr(character, 'venom_power', 0),
            'venom_power_max': getattr(character, 'venom_power_max', 100)
        }
        
        # 직업별 특수 시스템 데이터
        class_specific_data = {}
        
        # 전사 스탠스 시스템
        if getattr(character, 'character_class', '') == "전사":
            class_specific_data['current_stance'] = getattr(character, 'current_stance', 'balanced')
        
        # 암살자 그림자 시스템
        if getattr(character, 'character_class', '') == "암살자":
            class_specific_data['shadow_count'] = getattr(character, 'shadow_count', 0)
            class_specific_data['shadow_max'] = getattr(character, 'shadow_max', 5)
        
        # 몽크 기 에너지 시스템
        if getattr(character, 'character_class', '') == "몽크":
            class_specific_data['ki_energy'] = getattr(character, 'ki_energy', 0)
            class_specific_data['ki_max'] = getattr(character, 'ki_max', 100)
        
        # 바드 영감 시스템
        if getattr(character, 'character_class', '') == "바드":
            class_specific_data['inspiration_stacks'] = getattr(character, 'inspiration_stacks', 0)
            class_specific_data['inspiration_max'] = getattr(character, 'inspiration_max', 10)
        
        # 검성 검기 시스템
        if getattr(character, 'character_class', '') == "검성":
            class_specific_data['sword_spirit'] = getattr(character, 'sword_spirit', 0)
            class_specific_data['sword_spirit_max'] = getattr(character, 'sword_spirit_max', 100)
        
        # 용기사 드래곤 파워 시스템
        if getattr(character, 'character_class', '') == "용기사":
            class_specific_data['dragon_power'] = getattr(character, 'dragon_power', 0)
            class_specific_data['dragon_power_max'] = getattr(character, 'dragon_power_max', 100)
        
        # 철학자 지혜 스택 시스템
        if getattr(character, 'character_class', '') == "철학자":
            class_specific_data['wisdom_stacks'] = getattr(character, 'wisdom_stacks', 0)
            class_specific_data['wisdom_max'] = getattr(character, 'wisdom_max', 10)
        
        # 속성 시스템 관련
        element_data = {
            'element_affinity': getattr(character, 'element_affinity', 'neutral'),
            'element_weaknesses': getattr(character, 'element_weaknesses', []),
            'element_resistances': getattr(character, 'element_resistances', [])
        }
        
        # safe guard for max_hp access
        try:
            max_hp_value = character.max_hp
        except AttributeError:
            max_hp_value = getattr(character, '_max_hp', getattr(character, '_base_max_hp', 150))
        
        # safe guard for current_hp access 
        try:
            current_hp_value = character.current_hp
        except AttributeError:
            current_hp_value = getattr(character, '_current_hp', max_hp_value)
        
        return {
            'name': character.name,
            'character_class': getattr(character, 'character_class', 'Warrior'),
            'max_hp': max_hp_value,
            'current_hp': current_hp_value,
            'wounds': getattr(character, 'wounds', 0),
            'physical_attack': getattr(character, 'physical_attack', 10),
            'magic_attack': getattr(character, 'magic_attack', 10),
            'physical_defense': getattr(character, 'physical_defense', 10),
            'magic_defense': getattr(character, 'magic_defense', 10),
            'speed': character.speed,
            # 새로운 Brave 시스템 속성들
            'int_brv': getattr(character, 'int_brv', 400),
            'max_brv': getattr(character, 'max_brv', 500),
            'current_brv': getattr(character, 'current_brv', 400),
            # 구 버전 호환성을 위한 속성들 (사용되지 않음)
            'current_brave': getattr(character, 'current_brave', getattr(character, 'current_brv', 400)),
            'max_brave': getattr(character, 'max_brave', getattr(character, 'max_brv', 500)),
            'initial_brave': getattr(character, 'initial_brave', getattr(character, 'int_brv', 400)),
            'is_broken': getattr(character, 'is_broken', False),
            'active_traits': active_traits_data,
            'available_traits': available_traits_data,
            'preferred_damage_type': getattr(character, 'preferred_damage_type', 'physical'),
            'experience': getattr(character, 'experience', 0),
            'level': getattr(character, 'level', 1),
            'max_mp': getattr(character, 'max_mp', 20),
            'current_mp': getattr(character, 'current_mp', getattr(character, 'max_mp', 20)),
            'critical_rate': getattr(character, 'critical_rate', 5),
            'accuracy': getattr(character, 'accuracy', 85),
            'evasion': getattr(character, 'evasion', 10),
            # 인벤토리와 장비 정보 추가
            'inventory': inventory_data,
            'equipment': equipment_data,
            'gold': gold,
            # 추가 스탯들
            'brave_points': getattr(character, 'brave_points', 400),
            'element': getattr(character, 'element', 'none'),
            'max_carry_weight': getattr(character, 'max_carry_weight', 50.0),
            # 새로운 스킬 시스템 관련
            'brave_skills': brave_skills_data,
            'casting_data': casting_data,
            'status_effects': status_effects_data,
            'element_data': element_data,
            'venom_data': venom_data,  # 베놈 파워 데이터 추가
            'class_specific_data': class_specific_data,  # 직업별 특수 데이터 추가
            # ATB 시스템 관련
            'atb_gauge': getattr(character, 'atb_gauge', 0),
            'atb_speed': getattr(character, 'atb_speed', character.speed),
            'steps_taken': getattr(character, 'steps_taken', 0)
        }
    
    @staticmethod
    def deserialize_character(char_data: Dict[str, Any]):
        """딕셔너리에서 캐릭터 객체 생성"""
        # Character 클래스 동적 임포트
        try:
            from .character import Character
            
            # 🔧 모든 스탯 중복 적용 방지: 클래스 보정을 건너뛰고 저장된 값 사용
            character = Character(
                name=char_data['name'],
                character_class=char_data.get('character_class', 'Warrior'),
                max_hp=char_data['max_hp'],  # 저장된 실제값 사용
                physical_attack=char_data.get('physical_attack', 10),  # 저장된 실제값 사용
                magic_attack=char_data.get('magic_attack', 10),         # 저장된 실제값 사용
                physical_defense=char_data.get('physical_defense', 10), # 저장된 실제값 사용
                magic_defense=char_data.get('magic_defense', 10),       # 저장된 실제값 사용
                speed=char_data['speed'],                               # 저장된 실제값 사용
                skip_class_modifiers=True  # 🎯 클래스 보정 건너뛰기
            )
            
            # � 저장된 정확한 값들로 덮어쓰기 (이중 보정 방지)
            character.max_hp = char_data['max_hp']
            character._current_hp = char_data['current_hp']
            character.max_mp = char_data.get('max_mp', 20)
            character._current_mp = char_data.get('current_mp', character.max_mp)
            
            # ATB 속도는 장비 복원 후에 재계산 (장비 보너스 포함하기 위해)
            
        except ImportError:
            # 임시 캐릭터 딕셔너리로 반환
            character = type('Character', (), char_data)()
        
        # 기본 상태 복원 (중복 설정 방지)
        # character.current_hp는 이미 위에서 _current_hp로 설정됨
        character.wounds = char_data.get('wounds', 0)
        
        # 🎯 새로운 Brave 시스템 속성들 복원
        character.int_brv = char_data.get('int_brv', char_data.get('initial_brave', 400))
        character.max_brv = char_data.get('max_brv', char_data.get('max_brave', 500))
        character.current_brv = char_data.get('current_brv', char_data.get('current_brave', 400))
        
        # 구 버전 호환성을 위한 속성들 (새 속성이 없는 경우에만)
        if not hasattr(character, 'current_brave'):
            character.current_brave = character.current_brv
        if not hasattr(character, 'max_brave'):
            character.max_brave = character.max_brv
        if not hasattr(character, 'initial_brave'):
            character.initial_brave = character.int_brv
            
        character.is_broken = char_data.get('is_broken', False)
        character.brave_points = char_data.get('brave_points', character.current_brv)
        character.element = char_data.get('element', 'none')
        character.max_carry_weight = char_data.get('max_carry_weight', 50.0)
        
        # 특성 데이터 복원 (간단한 딕셔너리 형태로 저장)
        character.active_traits = char_data.get('active_traits', [])
        character.available_traits = char_data.get('available_traits', [])
        
        character.preferred_damage_type = char_data.get('preferred_damage_type', 'physical')
        character.experience = char_data.get('experience', 0)
        character.level = char_data.get('level', 1)
        # current_mp, max_mp는 이미 위에서 설정됨 (중복 제거)
        character.critical_rate = char_data.get('critical_rate', 5)
        character.accuracy = char_data.get('accuracy', 85)
        character.evasion = char_data.get('evasion', 10)
        character.gold = char_data.get('gold', 0)
        
        # 새로운 스킬 시스템 관련 속성들 복원
        if 'brave_skills' in char_data:
            character.brave_skills = char_data['brave_skills']
        
        # 캐스팅 시스템 관련 속성들 복원 (기본값으로 초기화)
        casting_data = char_data.get('casting_data', {})
        character.casting_skill = None  # 저장된 캐스팅 상태는 무시
        character.casting_targets = None
        character.casting_start_time = None
        character.casting_duration = None
        character.is_casting = False
        
        # 상태이상 관련 속성들 복원
        status_effects = char_data.get('status_effects', {})
        status_attributes = [
            'stunned', 'silenced', 'paralyzed', 'sleeping', 'frozen', 'blinded',
            'charmed', 'feared', 'cursed', 'blessed', 'weakened', 'strengthened',
            'hasted', 'slowed', 'shielded', 'poisoned'
        ]
        for attr in status_attributes:
            setattr(character, attr, status_effects.get(attr, False))
        
        # 복잡한 상태 효과 딕셔너리 복원 (독 등)
        if 'complex_effects' in status_effects:
            character.status_effects = status_effects['complex_effects'].copy()
        elif not hasattr(character, 'status_effects'):
            character.status_effects = {}
        
        # 베놈 파워 복원 (도적 전용)
        venom_data = char_data.get('venom_data', {})
        character.venom_power = venom_data.get('venom_power', 0)
        character.venom_power_max = venom_data.get('venom_power_max', 100)
        
        # 직업별 특수 시스템 복원
        class_specific_data = char_data.get('class_specific_data', {})
        
        # 전사 스탠스 복원
        if getattr(character, 'character_class', '') == "전사":
            character.current_stance = class_specific_data.get('current_stance', 'balanced')
        
        # 암살자 그림자 복원
        if getattr(character, 'character_class', '') == "암살자":
            character.shadow_count = class_specific_data.get('shadow_count', 0)
            character.shadow_max = class_specific_data.get('shadow_max', 5)
        
        # 몽크 기 에너지 복원
        if getattr(character, 'character_class', '') == "몽크":
            character.ki_energy = class_specific_data.get('ki_energy', 0)
            character.ki_max = class_specific_data.get('ki_max', 100)
        
        # 바드 영감 복원
        if getattr(character, 'character_class', '') == "바드":
            character.inspiration_stacks = class_specific_data.get('inspiration_stacks', 0)
            character.inspiration_max = class_specific_data.get('inspiration_max', 10)
        
        # 검성 검기 복원
        if getattr(character, 'character_class', '') == "검성":
            character.sword_spirit = class_specific_data.get('sword_spirit', 0)
            character.sword_spirit_max = class_specific_data.get('sword_spirit_max', 100)
        
        # 용기사 드래곤 파워 복원
        if getattr(character, 'character_class', '') == "용기사":
            character.dragon_power = class_specific_data.get('dragon_power', 0)
            character.dragon_power_max = class_specific_data.get('dragon_power_max', 100)
        
        # 철학자 지혜 스택 복원
        if getattr(character, 'character_class', '') == "철학자":
            character.wisdom_stacks = class_specific_data.get('wisdom_stacks', 0)
            character.wisdom_max = class_specific_data.get('wisdom_max', 10)
        
        # 속성 시스템 관련 복원
        element_data = char_data.get('element_data', {})
        character.element_affinity = element_data.get('element_affinity', 'neutral')
        character.element_weaknesses = element_data.get('element_weaknesses', [])
        character.element_resistances = element_data.get('element_resistances', [])
        
        # ATB 시스템 관련 복원
        character.atb_gauge = char_data.get('atb_gauge', 0)
        character.atb_speed = char_data.get('atb_speed', character.speed)
        character.steps_taken = char_data.get('steps_taken', 0)
        
        # 인벤토리 복원 (강화된 안전성)
        if 'inventory' in char_data and char_data['inventory']:
            try:
                from .items import Inventory
                inventory_data = char_data['inventory']
                
                # 새 인벤토리 객체 생성
                character.inventory = Inventory(
                    max_size=inventory_data.get('max_size', 15),
                    max_weight=inventory_data.get('max_weight', 100.0)
                )
                
                # 아이템들 복원 - 안전한 복사
                if 'items' in inventory_data and inventory_data['items']:
                    restored_items = {}
                    for item_name, quantity in inventory_data['items'].items():
                        if isinstance(quantity, (int, float)) and quantity > 0:
                            restored_items[str(item_name)] = int(quantity)
                    
                    character.inventory.items = restored_items
                    
                    # 복원 로그 출력
                    item_count = len(restored_items)
                    total_quantity = sum(restored_items.values())
                    print(f"📥 [LOAD] {character.name} 인벤토리: {item_count}종류, {total_quantity}개 아이템 복원")
                else:
                    character.inventory.items = {}
                    print(f"📥 [LOAD] {character.name} 인벤토리: 빈 인벤토리로 복원")
                    
            except Exception as e:
                print(f"⚠️ {character.name} 인벤토리 복원 실패: {e}")
                import traceback
                traceback.print_exc()
                # 기본 인벤토리 생성
                try:
                    from .items import Inventory
                    character.inventory = Inventory(max_size=15, max_weight=100.0)
                    character.inventory.items = {}
                    print(f"🔧 {character.name} 기본 인벤토리 생성")
                except ImportError:
                    pass
        else:
            # 인벤토리 데이터가 없는 경우 기본 인벤토리 생성
            try:
                from .items import Inventory
                character.inventory = Inventory(max_size=15, max_weight=100.0)
                character.inventory.items = {}
                print(f"🆕 {character.name} 새 인벤토리 생성 (저장 데이터 없음)")
            except ImportError:
                pass
        
        # 장비 복원
        def deserialize_equipment(equipment_data):
            """장비 데이터를 아이템 객체로 복원"""
            if equipment_data is None:
                return None
            try:
                from .items import Item, ItemType, ItemRarity
                # ItemType 변환
                item_type_str = equipment_data.get('item_type', 'WEAPON')
                if hasattr(ItemType, item_type_str):
                    item_type = getattr(ItemType, item_type_str)
                else:
                    item_type = ItemType.WEAPON  # 기본값
                
                # ItemRarity 변환
                rarity_str = equipment_data.get('rarity', 'common')
                if hasattr(ItemRarity, rarity_str.upper()):
                    rarity = getattr(ItemRarity, rarity_str.upper())
                else:
                    rarity = ItemRarity.COMMON  # 기본값
                
                equipment = Item(
                    name=equipment_data['name'],
                    item_type=item_type,
                    rarity=rarity,
                    description=equipment_data.get('description', ''),
                    value=equipment_data.get('value', 0),
                    weight=equipment_data.get('weight', 1.0),
                    min_level=equipment_data.get('min_level', 1),
                    max_durability=equipment_data.get('max_durability', 100)
                )
                
                # stats와 effects는 객체 생성 후 별도 설정
                equipment.stats = equipment_data.get('stats', {})
                equipment.effects = equipment_data.get('effects', {})
                equipment.durability = equipment_data.get('durability', equipment.max_durability)
                
                return equipment
            except Exception as e:
                print(f"⚠️ 장비 복원 실패: {e}")
                return None
        
        if 'equipment' in char_data and char_data['equipment']:
            equipment_data = char_data['equipment']
            character.equipped_weapon = deserialize_equipment(equipment_data.get('equipped_weapon'))
            character.equipped_armor = deserialize_equipment(equipment_data.get('equipped_armor'))
            character.equipped_accessory = deserialize_equipment(equipment_data.get('equipped_accessory'))
            
            # 🎯 장비 복원 후 인벤토리에 장비 아이템 자동 추가 (중요!)
            equipped_items = []
            if character.equipped_weapon:
                equipped_items.append(character.equipped_weapon)
                character.inventory.add_item(character.equipped_weapon.name, 1)
                print(f"🔧 {character.equipped_weapon.name} 인벤토리에 자동 추가 (장착됨)")
            
            if character.equipped_armor:
                equipped_items.append(character.equipped_armor)
                character.inventory.add_item(character.equipped_armor.name, 1)
                print(f"🔧 {character.equipped_armor.name} 인벤토리에 자동 추가 (장착됨)")
            
            if character.equipped_accessory:
                equipped_items.append(character.equipped_accessory)
                character.inventory.add_item(character.equipped_accessory.name, 1)
                print(f"🔧 {character.equipped_accessory.name} 인벤토리에 자동 추가 (장착됨)")
            
            # 장비 복원 로그
            print(f"🎒 [LOAD LOG] {character.name} 장비 복원:")
            print(f"🎒 [LOAD LOG] - Weapon: {character.equipped_weapon}")
            print(f"🎒 [LOAD LOG] - Armor: {character.equipped_armor}")
            print(f"🎒 [LOAD LOG] - Accessory: {character.equipped_accessory}")
            
            equipped_count = sum(1 for eq in [character.equipped_weapon, character.equipped_armor, character.equipped_accessory] if eq is not None)
            print(f"✅ {character.name} 장비 복원 완료: {equipped_count}개 장비 + 인벤토리 동기화")
        
        # 🎯 장비 복원 후 ATB 속도 재계산 (장비 보너스 포함)
        try:
            if hasattr(character, 'get_total_speed'):
                character.atb_speed = character.get_total_speed()
                print(f"🏃 {character.name} ATB 속도 재계산: {character.atb_speed}")
            else:
                character.atb_speed = character.speed
                print(f"🏃 {character.name} ATB 속도 기본값: {character.atb_speed}")
        except Exception as e:
            print(f"⚠️ {character.name} ATB 속도 재계산 실패: {e}")
            character.atb_speed = character.speed
        
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
            
            # 파티 공용 인벤토리 직렬화
            shared_inventory_data = {}
            if hasattr(game.party_manager, 'shared_inventory') and game.party_manager.shared_inventory:
                try:
                    shared_inventory_data = {
                        'items': game.party_manager.shared_inventory.items.copy() if hasattr(game.party_manager.shared_inventory, 'items') else {},
                        'max_size': getattr(game.party_manager.shared_inventory, 'max_size', 100),
                        'max_weight': getattr(game.party_manager.shared_inventory, 'max_weight', 500.0)
                    }
                    print(f"📦 공용 인벤토리 직렬화: {len(shared_inventory_data['items'])}개 아이템")
                except Exception as e:
                    print(f"⚠️ 공용 인벤토리 직렬화 오류: {e}")
                    shared_inventory_data = {'items': {}, 'max_size': 100, 'max_weight': 500.0}
            
            # 게임 설정에서 난이도 정보 가져오기
            difficulty_info = "normal"  # 기본값
            try:
                from .settings import GameSettings
                settings = GameSettings()
                difficulty_info = settings.get('gameplay', 'difficulty')
                print(f"🎯 난이도 정보 저장: {difficulty_info}")
            except Exception as e:
                print(f"⚠️ 난이도 정보 가져오기 오류: {e}")
            
            return {
                'version': '2.2.0',  # 새로운 스킬 시스템 반영
                'current_level': game.world.current_level,
                'difficulty': difficulty_info,  # 난이도 정보 추가
                'score': getattr(game, 'score', 0),
                'enemies_defeated': getattr(game, 'enemies_defeated', 0),
                'items_collected': getattr(game, 'items_collected', 0),
                'floors_cleared': getattr(game, 'floors_cleared', 0),
                'steps_since_last_encounter': getattr(game, 'steps_since_last_encounter', 0),
                'gathering_cooldown': getattr(game, 'gathering_cooldown', 0),
                'steps_since_last_gather': getattr(game, 'steps_since_last_gather', 0),
                'random_encounters_this_floor': getattr(game, 'random_encounters_this_floor', 0),
                'player_position': game.world.player_pos,
                'party_characters': [
                    GameStateSerializer.serialize_character(char) 
                    for char in game.party_manager.members
                ],
                'party_character_names': [char.name for char in game.party_manager.members],
                # 파티 관련 정보 추가
                'party_gold': getattr(game.party_manager, 'party_gold', 0),
                'party_shared_inventory': shared_inventory_data,
                'party_total_steps': getattr(game.party_manager, 'total_steps', 0),
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
            
            if file_result is None or file_result == -1 or file_result >= len(saves):
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
    """불러오기 메뉴 표시 - 페이지 방식"""
    saves = save_manager.list_saves()
    
    if not saves:
        print("\n저장된 게임이 없습니다.")
        from .input_utils import KeyboardInput
        KeyboardInput().wait_for_key("아무 키나 눌러 계속...")
        return None
    
    try:
        from .cursor_menu_system import create_simple_menu
        
        # 페이지당 항목 수 (화면에 맞게 조정)
        items_per_page = 10
        total_pages = (len(saves) + items_per_page - 1) // items_per_page
        current_page = 0
        
        while True:
            # 현재 페이지의 저장 파일들
            start_idx = current_page * items_per_page
            end_idx = min(start_idx + items_per_page, len(saves))
            page_saves = saves[start_idx:end_idx]
            
            # 메뉴 옵션 생성
            options = []
            descriptions = []
            
            for i, save_info in enumerate(page_saves):
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
                
                file_number = start_idx + i + 1
                options.append(f"📁 [{file_number:2d}] {save_info['filename']}")
                descriptions.append(f"레벨 {save_info['level']}, 점수 {save_info['score']} | 파티: {party_str} | {save_time}")
            
            # 페이지 네비게이션 옵션 추가
            if total_pages > 1:
                if current_page > 0:
                    options.append("◀️ 이전 페이지")
                    descriptions.append(f"페이지 {current_page}/{total_pages}로 이동")
                
                if current_page < total_pages - 1:
                    options.append("▶️ 다음 페이지")
                    descriptions.append(f"페이지 {current_page + 2}/{total_pages}로 이동")
            
            options.append("❌ 취소")
            descriptions.append("불러오기를 취소하고 돌아갑니다")
            
            # 페이지 정보가 포함된 제목
            title = f"📁 게임 불러오기 (페이지 {current_page + 1}/{total_pages}) - 총 {len(saves)}개 파일"
            
            menu = create_simple_menu(title, options, descriptions)
            result = menu.run()
            
            if result is None or result == -1:  # ESC 또는 잘못된 입력
                return None
            
            # 선택 처리
            if result < len(page_saves):
                # 세이브 파일 선택
                selected_save = page_saves[result]
                return selected_save['filename']
            else:
                # 네비게이션 옵션 처리
                nav_start = len(page_saves)
                nav_option = result - nav_start
                
                if total_pages > 1:
                    if current_page > 0 and nav_option == 0:  # 이전 페이지
                        current_page -= 1
                        continue
                    elif current_page < total_pages - 1:
                        if (current_page > 0 and nav_option == 1) or (current_page == 0 and nav_option == 0):  # 다음 페이지
                            current_page += 1
                            continue
                
                # 취소 선택
                return None
            
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


# 호환성을 위한 alias
SaveSystem = SaveManager
