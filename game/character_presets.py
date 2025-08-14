"""
캐릭터 프리셋 시스템
미리 생성한 캐릭터들을 저장하고 불러오는 기능
"""

import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from game.character import Character
from game.auto_party_builder import AutoPartyBuilder

class CharacterPresets:
    """캐릭터 프리셋 관리 클래스"""
    
    def __init__(self):
        self.presets_file = "character_presets.json"
        self.auto_builder = AutoPartyBuilder()
        self.presets_data = self.load_presets()
    
    def load_presets(self) -> Dict[str, Any]:
        """프리셋 데이터 로드"""
        try:
            if os.path.exists(self.presets_file):
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"character_presets": {}, "party_presets": {}}
        except Exception as e:
            print(f"⚠️ 프리셋 로드 실패: {e}")
            return {"character_presets": {}, "party_presets": {}}
    
    def save_presets(self) -> bool:
        """프리셋 데이터 저장"""
        try:
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ 프리셋 저장 실패: {e}")
            return False
    
    def save_character_preset(self, character: Character, preset_name: str, description: str = "") -> bool:
        """캐릭터 프리셋 저장"""
        try:
            # 캐릭터 데이터를 딕셔너리로 변환
            character_data = {
                "name": character.name,
                "character_class": character.character_class,
                "level": character.level,
                "stats": {
                    "physical_attack": character.physical_attack,
                    "magic_attack": character.magic_attack,
                    "physical_defense": character.physical_defense,
                    "magic_defense": character.magic_defense,
                    "speed": character.speed,
                    "max_hp": character.max_hp,
                    "max_mp": character.max_mp
                },
                "current_status": {
                    "hp": getattr(character, 'hp', character.max_hp),
                    "mp": getattr(character, 'mp', character.max_mp),
                    "brave_points": getattr(character, 'brave_points', 1000),
                    "wounds": getattr(character, 'wounds', 0),
                    "experience": getattr(character, 'experience', 0)
                },
                "traits": [],
                "equipment": {},
                "created_at": datetime.now().isoformat(),
                "description": description
            }
            
            # 특성 정보 저장
            if hasattr(character, 'passive_traits') and character.passive_traits:
                character_data["traits"] = [trait.name for trait in character.passive_traits]
            
            # 장비 정보 저장 (기본 정보만)
            if hasattr(character, 'equipment') and character.equipment:
                for slot, item in character.equipment.items():
                    if item:
                        character_data["equipment"][slot] = {
                            "name": item.name,
                            "type": item.item_type,
                            "rarity": getattr(item, 'rarity', 'common')
                        }
            
            # 프리셋 저장
            self.presets_data["character_presets"][preset_name] = character_data
            return self.save_presets()
            
        except Exception as e:
            print(f"⚠️ 캐릭터 프리셋 저장 실패: {e}")
            return False
    
    def save_party_preset(self, party: List[Character], preset_name: str, description: str = "") -> bool:
        """파티 프리셋 저장"""
        try:
            party_data = {
                "characters": [],
                "party_size": len(party),
                "created_at": datetime.now().isoformat(),
                "description": description
            }
            
            # 각 캐릭터 정보 저장
            for char in party:
                char_preset_name = f"{preset_name}_{char.character_class}_{char.name}"
                self.save_character_preset(char, char_preset_name, f"{preset_name} 파티의 {char.character_class}")
                party_data["characters"].append(char_preset_name)
            
            self.presets_data["party_presets"][preset_name] = party_data
            return self.save_presets()
            
        except Exception as e:
            print(f"⚠️ 파티 프리셋 저장 실패: {e}")
            return False
    
    def load_character_preset(self, preset_name: str) -> Optional[Character]:
        """캐릭터 프리셋 로드 - 새 모험용 초기화"""
    def load_character_preset(self, preset_name: str) -> Optional[Character]:
        """캐릭터 프리셋 로드 - 새 모험용 초기화"""
        try:
            if preset_name not in self.presets_data["character_presets"]:
                return None
            
            char_data = self.presets_data["character_presets"][preset_name]
            
            # 🆕 새로운 모험을 위해 레벨 1로 새 캐릭터 생성
            character = self.auto_builder._create_character(char_data["character_class"], 1)
            
            # 📝 저장된 정보에서 이름만 복원
            character.name = char_data["name"]
            
            # 🎯 특성만 복원 (캐릭터의 정체성 유지)
            if char_data.get("traits") and hasattr(character, 'available_traits'):
                try:
                    trait_indices = []
                    for trait_name in char_data["traits"]:
                        for i, trait in enumerate(character.available_traits):
                            if hasattr(trait, 'name') and trait.name == trait_name:
                                trait_indices.append(i)
                                break
                    if trait_indices:
                        character.select_passive_traits(trait_indices)
                except Exception:
                    # 특성 복원 실패 시 자동 선택
                    if hasattr(self.auto_builder, '_auto_select_passives'):
                        self.auto_builder._auto_select_passives(character)
            
            # ✅ 나머지는 모두 초기화됨:
            # - 레벨: 1
            # - 경험치: 0
            # - 장비: 없음
            # - HP/MP: 레벨 1 기본값
            # - 스탯: 레벨 1 + 직업 기본값
            
            return character
            
        except Exception as e:
            print(f"⚠️ 캐릭터 프리셋 로드 실패: {e}")
            return None
    
    def load_party_preset(self, preset_name: str) -> Optional[List[Character]]:
        """파티 프리셋 로드"""
        try:
            if preset_name not in self.presets_data["party_presets"]:
                return None
            
            party_data = self.presets_data["party_presets"][preset_name]
            party = []
            
            for char_preset_name in party_data["characters"]:
                character = self.load_character_preset(char_preset_name)
                if character:
                    party.append(character)
            
            return party if party else None
            
        except Exception as e:
            print(f"⚠️ 파티 프리셋 로드 실패: {e}")
            return None
    
    def list_character_presets(self) -> List[Dict[str, str]]:
        """캐릭터 프리셋 목록 반환"""
        presets = []
        for name, data in self.presets_data["character_presets"].items():
            presets.append({
                "name": name,
                "character_class": data["character_class"],
                "level": data["level"],
                "description": data.get("description", ""),
                "created_at": data.get("created_at", "")
            })
        return presets
    
    def list_party_presets(self) -> List[Dict[str, str]]:
        """파티 프리셋 목록 반환"""
        presets = []
        for name, data in self.presets_data["party_presets"].items():
            # 파티 구성 정보 가져오기
            party_composition = []
            for char_preset_name in data["characters"]:
                if char_preset_name in self.presets_data["character_presets"]:
                    char_data = self.presets_data["character_presets"][char_preset_name]
                    party_composition.append(char_data["character_class"])
            
            presets.append({
                "name": name,
                "party_size": data["party_size"],
                "composition": " + ".join(party_composition),
                "description": data.get("description", ""),
                "created_at": data.get("created_at", "")
            })
        return presets
    
    def delete_character_preset(self, preset_name: str) -> bool:
        """캐릭터 프리셋 삭제"""
        try:
            if preset_name in self.presets_data["character_presets"]:
                del self.presets_data["character_presets"][preset_name]
                return self.save_presets()
            return False
        except Exception as e:
            print(f"⚠️ 캐릭터 프리셋 삭제 실패: {e}")
            return False
    
    def delete_party_preset(self, preset_name: str) -> bool:
        """파티 프리셋 삭제"""
        try:
            if preset_name in self.presets_data["party_presets"]:
                # 연관된 캐릭터 프리셋들도 삭제
                party_data = self.presets_data["party_presets"][preset_name]
                for char_preset_name in party_data["characters"]:
                    self.delete_character_preset(char_preset_name)
                
                del self.presets_data["party_presets"][preset_name]
                return self.save_presets()
            return False
        except Exception as e:
            print(f"⚠️ 파티 프리셋 삭제 실패: {e}")
            return False
    
    def get_preset_info(self, preset_name: str, preset_type: str = "character") -> Optional[Dict]:
        """프리셋 상세 정보 반환"""
        try:
            if preset_type == "character":
                return self.presets_data["character_presets"].get(preset_name)
            else:
                return self.presets_data["party_presets"].get(preset_name)
        except Exception:
            return None
