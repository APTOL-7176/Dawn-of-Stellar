# enhanced_party_presets.py
# 향상된 파티 프리셋 시스템

import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from game.character import Character
from game.color_text import *

class EnhancedPartyPresets:
    """향상된 파티 프리셋 관리 클래스"""
    
    def __init__(self):
        self.presets_dir = "presets"
        self.parties_dir = os.path.join(self.presets_dir, "parties")
        self.ai_parties_dir = "ai_parties"  # AI 게임모드 호환
        self._ensure_directories()
    
    def _ensure_directories(self):
        """필요한 디렉토리 생성"""
        for directory in [self.presets_dir, self.parties_dir, self.ai_parties_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def save_party_preset(self, party: List[Character], party_name: str, description: str = "") -> Optional[str]:
        """파티 프리셋 저장 (향상된 버전)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{party_name}_{timestamp}.json"
            filepath = os.path.join(self.parties_dir, filename)
            
            # 파티 데이터 구성
            party_data = {
                "meta": {
                    "name": party_name,
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                    "party_size": len(party),
                    "version": "2.0"  # Enhanced 버전
                },
                "characters": []
            }
            
            # 각 캐릭터 정보 저장
            for i, char in enumerate(party):
                char_data = self._serialize_character(char, i)
                party_data["characters"].append(char_data)
            
            # 일반 프리셋 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(party_data, f, ensure_ascii=False, indent=2)
            
            # AI 게임모드 호환 버전 저장
            self._save_ai_compatible_version(party_data, party_name, timestamp)
            
            return filename
            
        except Exception as e:
            print(f"{RED}❌ 파티 프리셋 저장 실패: {e}{RESET}")
            return None
    
    def _serialize_character(self, character: Character, index: int) -> Dict[str, Any]:
        """캐릭터를 직렬화"""
        char_data = {
            "index": index,
            "basic_info": {
                "name": character.name,
                "character_class": character.character_class,
                "level": getattr(character, 'level', 1),
                "gender": getattr(character, 'gender', 'male')
            },
            "stats": {
                "max_hp": getattr(character, 'max_hp', 100),
                "max_mp": getattr(character, 'max_mp', 20),
                "current_hp": getattr(character, 'current_hp', character.max_hp),
                "current_mp": getattr(character, 'current_mp', character.max_mp),
                "brave_points": getattr(character, 'brave_points', 1000),
                "wounds": getattr(character, 'wounds', 0),
                "experience": getattr(character, 'experience', 0)
            },
            "attributes": {
                "strength": getattr(character, 'strength', 10),
                "magic": getattr(character, 'magic', 10),
                "defense": getattr(character, 'defense', 10),
                "magic_defense": getattr(character, 'magic_defense', 10),
                "speed": getattr(character, 'speed', 10),
                "luck": getattr(character, 'luck', 10)
            },
            "traits": [],
            "equipment": {},
            "special_data": {}
        }
        
        # 특성 정보
        if hasattr(character, 'passive_traits') and character.passive_traits:
            char_data["traits"] = [
                {
                    "name": trait.name if hasattr(trait, 'name') else str(trait),
                    "description": getattr(trait, 'description', '')
                }
                for trait in character.passive_traits
            ]
        
        # 장비 정보
        if hasattr(character, 'equipment') and character.equipment:
            for slot, item in character.equipment.items():
                if item:
                    char_data["equipment"][slot] = {
                        "name": item.name,
                        "type": item.item_type,
                        "rarity": getattr(item, 'rarity', 'common'),
                        "stats": getattr(item, 'stats', {})
                    }
        
        # 직업별 특수 데이터
        char_data["special_data"] = self._get_class_special_data(character)
        
        return char_data
    
    def _get_class_special_data(self, character: Character) -> Dict[str, Any]:
        """직업별 특수 데이터 추출"""
        special_data = {}
        
        try:
            # 도적 - 맹독 시스템
            if hasattr(character, 'poison_stacks'):
                special_data["poison_stacks"] = character.poison_stacks
            
            # 궁수 - 조준 시스템  
            if hasattr(character, 'aim_points'):
                special_data["aim_points"] = character.aim_points
            
            # 암살자 - 그림자 시스템
            if hasattr(character, 'shadow_count'):
                special_data["shadow_count"] = character.shadow_count
            
            # 바드 - 사기 시스템
            if hasattr(character, 'morale_effects'):
                special_data["morale_effects"] = character.morale_effects
            
            # 몽크 - 표식 시스템
            if hasattr(character, 'focus_marks'):
                special_data["focus_marks"] = character.focus_marks
                
        except Exception as e:
            print(f"⚠️ 특수 데이터 추출 실패: {e}")
        
        return special_data
    
    def _save_ai_compatible_version(self, party_data: Dict[str, Any], party_name: str, timestamp: str):
        """AI 게임모드 호환 버전 저장"""
        try:
            ai_filename = f"{party_name}_{timestamp}.json"
            ai_filepath = os.path.join(self.ai_parties_dir, ai_filename)
            
            # AI 게임모드용 형식으로 변환
            ai_party_data = {
                "meta": party_data["meta"].copy(),
                "ai_compatible": True,
                "characters": []
            }
            
            for char_data in party_data["characters"]:
                ai_char_data = {
                    "name": char_data["basic_info"]["name"],
                    "character_class": char_data["basic_info"]["character_class"],
                    "level": char_data["basic_info"]["level"],
                    "current_status": {
                        "hp": char_data["stats"]["current_hp"],
                        "mp": char_data["stats"]["current_mp"],
                        "brave_points": char_data["stats"]["brave_points"]
                    },
                    "ai_personality": self._generate_ai_personality(char_data),
                    "source": "enhanced_preset"
                }
                ai_party_data["characters"].append(ai_char_data)
            
            with open(ai_filepath, 'w', encoding='utf-8') as f:
                json.dump(ai_party_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ AI 호환 버전 저장 실패: {e}")
    
    def _generate_ai_personality(self, char_data: Dict[str, Any]) -> Dict[str, Any]:
        """캐릭터 데이터 기반 AI 성격 생성"""
        character_class = char_data["basic_info"]["character_class"]
        
        # 직업별 기본 AI 성격
        class_personalities = {
            "전사": {"archetype": "guardian", "combat_style": "aggressive", "social_style": "protective"},
            "아크메이지": {"archetype": "scholar", "combat_style": "tactical", "social_style": "wise"},
            "궁수": {"archetype": "hunter", "combat_style": "precise", "social_style": "independent"},
            "도적": {"archetype": "trickster", "combat_style": "cunning", "social_style": "sneaky"},
            "성기사": {"archetype": "paladin", "combat_style": "righteous", "social_style": "noble"},
            "암흑기사": {"archetype": "dark_knight", "combat_style": "ruthless", "social_style": "brooding"},
            "몽크": {"archetype": "martial_artist", "combat_style": "balanced", "social_style": "disciplined"},
            "바드": {"archetype": "entertainer", "combat_style": "supportive", "social_style": "charismatic"}
        }
        
        return class_personalities.get(character_class, {
            "archetype": "adventurer",
            "combat_style": "adaptive", 
            "social_style": "friendly"
        })
    
    def load_party_preset(self, filename: str) -> Optional[List[Dict[str, Any]]]:
        """파티 프리셋 로드"""
        try:
            filepath = os.path.join(self.parties_dir, filename)
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                party_data = json.load(f)
            
            return party_data.get("characters", [])
            
        except Exception as e:
            print(f"{RED}❌ 파티 프리셋 로드 실패: {e}{RESET}")
            return None
    
    def list_party_presets(self) -> List[Dict[str, Any]]:
        """저장된 파티 프리셋 목록"""
        presets = []
        
        try:
            if not os.path.exists(self.parties_dir):
                return presets
            
            files = [f for f in os.listdir(self.parties_dir) if f.endswith('.json')]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.parties_dir, x)), reverse=True)
            
            for filename in files:
                filepath = os.path.join(self.parties_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    meta = data.get("meta", {})
                    presets.append({
                        "filename": filename,
                        "name": meta.get("name", filename.replace('.json', '')),
                        "description": meta.get("description", ""),
                        "party_size": meta.get("party_size", 0),
                        "created_at": meta.get("created_at", ""),
                        "version": meta.get("version", "1.0")
                    })
                    
                except Exception as e:
                    print(f"⚠️ 프리셋 파일 읽기 실패 ({filename}): {e}")
                    continue
                    
        except Exception as e:
            print(f"{RED}❌ 프리셋 목록 조회 실패: {e}{RESET}")
        
        return presets
    
    def delete_party_preset(self, filename: str) -> bool:
        """파티 프리셋 삭제"""
        try:
            filepath = os.path.join(self.parties_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                
                # AI 호환 버전도 삭제
                ai_filepath = os.path.join(self.ai_parties_dir, filename)
                if os.path.exists(ai_filepath):
                    os.remove(ai_filepath)
                
                return True
                
        except Exception as e:
            print(f"{RED}❌ 프리셋 삭제 실패: {e}{RESET}")
        
        return False
    
    def get_preset_summary(self, filename: str) -> Optional[str]:
        """프리셋 요약 정보 반환"""
        try:
            party_data = self.load_party_preset(filename)
            if not party_data:
                return None
            
            summary_lines = []
            summary_lines.append(f"📁 {filename}")
            summary_lines.append(f"👥 파티 구성 ({len(party_data)}명):")
            
            for char_data in party_data:
                name = char_data["basic_info"]["name"]
                char_class = char_data["basic_info"]["character_class"]
                level = char_data["basic_info"]["level"]
                summary_lines.append(f"  • {name} ({char_class}) Lv.{level}")
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            print(f"⚠️ 프리셋 요약 생성 실패: {e}")
            return None
