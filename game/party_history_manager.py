"""
파티 히스토리 관리 시스템
최근 탐험한 파티들을 자동으로 저장하고 관리합니다.
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from game.character import Character

class PartyHistoryManager:
    """최근 탐험한 파티들을 관리하는 시스템"""
    
    def __init__(self, history_file: str = "party_history.json"):
        self.history_file = history_file
        self.max_history_count = 50  # 최대 저장할 파티 수
        self.history_data = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """파티 히스토리 데이터 로드"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"⚠️ 파티 히스토리 로드 실패: {e}")
            return []
    
    def _save_history(self):
        """파티 히스토리 데이터 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 파티 히스토리 저장 실패: {e}")
    
    def add_party_to_history(self, party: List[Character], exploration_info: Dict = None):
        """파티를 히스토리에 추가"""
        try:
            # 파티 정보 직렬화
            party_data = {
                "id": f"party_{int(time.time())}_{len(self.history_data)}",
                "timestamp": datetime.now().isoformat(),
                "date_display": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "party_size": len(party),
                "members": [],
                "exploration_summary": exploration_info or {},
                "avg_level": 0,
                "total_experience": 0,
                "party_composition": []
            }
            
            total_exp = 0
            total_level = 0
            class_counts = {}
            
            for member in party:
                member_data = {
                    "name": getattr(member, 'name', 'Unknown'),
                    "class": getattr(member, 'character_class', 'Unknown'),
                    "level": getattr(member, 'level', 1),
                    "experience": getattr(member, 'experience', 0),
                    "hp": getattr(member, 'current_hp', 0),
                    "max_hp": getattr(member, 'max_hp', 0),
                    "mp": getattr(member, 'current_mp', 0),
                    "max_mp": getattr(member, 'max_mp', 0),
                    "brave_points": getattr(member, 'brave_points', 0),
                    "physical_attack": getattr(member, 'physical_attack', 0),
                    "physical_defense": getattr(member, 'physical_defense', 0),
                    "magic_attack": getattr(member, 'magic_attack', 0),
                    "magic_defense": getattr(member, 'magic_defense', 0),
                    "speed": getattr(member, 'speed', 0),
                    "traits": [],
                    "equipment": []
                }
                
                # 특성 정보
                if hasattr(member, 'active_traits') and member.active_traits:
                    for trait in member.active_traits:
                        if hasattr(trait, 'name'):
                            member_data["traits"].append(trait.name)
                        elif isinstance(trait, dict) and 'name' in trait:
                            member_data["traits"].append(trait['name'])
                
                # 장비 정보
                if hasattr(member, 'equipped_items') and member.equipped_items:
                    for slot, item in member.equipped_items.items():
                        if item:
                            item_info = {
                                "slot": slot,
                                "name": getattr(item, 'name', 'Unknown Item'),
                                "durability": getattr(item, 'current_durability', 100)
                            }
                            member_data["equipment"].append(item_info)
                
                party_data["members"].append(member_data)
                
                # 통계 계산
                total_exp += member_data["experience"]
                total_level += member_data["level"]
                
                char_class = member_data["class"]
                class_counts[char_class] = class_counts.get(char_class, 0) + 1
            
            party_data["avg_level"] = total_level // len(party) if party else 0
            party_data["total_experience"] = total_exp
            party_data["party_composition"] = [f"{cls}×{cnt}" for cls, cnt in class_counts.items()]
            
            # 히스토리에 추가 (최신이 앞에 오도록)
            self.history_data.insert(0, party_data)
            
            # 최대 개수 제한
            if len(self.history_data) > self.max_history_count:
                self.history_data = self.history_data[:self.max_history_count]
            
            self._save_history()
            print(f"✅ 파티가 히스토리에 저장되었습니다 (ID: {party_data['id']})")
            
        except Exception as e:
            print(f"⚠️ 파티 히스토리 추가 실패: {e}")
    
    def get_history_list(self) -> List[Dict]:
        """파티 히스토리 목록 반환"""
        return self.history_data.copy()
    
    def get_party_by_id(self, party_id: str) -> Optional[Dict]:
        """ID로 특정 파티 데이터 반환"""
        for party in self.history_data:
            if party.get("id") == party_id:
                return party
        return None
    
    def delete_party_from_history(self, party_id: str) -> bool:
        """파티를 히스토리에서 삭제"""
        try:
            original_count = len(self.history_data)
            self.history_data = [p for p in self.history_data if p.get("id") != party_id]
            
            if len(self.history_data) < original_count:
                self._save_history()
                print(f"✅ 파티 {party_id}가 히스토리에서 삭제되었습니다.")
                return True
            else:
                print(f"⚠️ 파티 {party_id}를 찾을 수 없습니다.")
                return False
        except Exception as e:
            print(f"⚠️ 파티 삭제 실패: {e}")
            return False
    
    def clear_all_history(self) -> bool:
        """모든 파티 히스토리 삭제"""
        try:
            self.history_data.clear()
            self._save_history()
            print("✅ 모든 파티 히스토리가 삭제되었습니다.")
            return True
        except Exception as e:
            print(f"⚠️ 히스토리 전체 삭제 실패: {e}")
            return False
    
    def recreate_party_from_history(self, party_id: str) -> Optional[List[Character]]:
        """히스토리에서 파티를 재생성"""
        try:
            party_data = self.get_party_by_id(party_id)
            if not party_data:
                return None
            
            recreated_party = []
            for member_data in party_data["members"]:
                # 캐릭터 재생성
                character = Character(
                    name=member_data["name"],
                    character_class=member_data["class"]
                )
                
                # 기본 속성 복원
                character.level = member_data["level"]
                character.experience = member_data["experience"]
                character.current_hp = member_data["hp"]
                character.max_hp = member_data["max_hp"]
                character.current_mp = member_data["mp"]
                character.max_mp = member_data["max_mp"]
                character.brave_points = member_data["brave_points"]
                character.physical_attack = member_data["physical_attack"]
                character.physical_defense = member_data["physical_defense"]
                character.magic_attack = member_data["magic_attack"]
                character.magic_defense = member_data["magic_defense"]
                character.speed = member_data["speed"]
                
                # 특성 복원 (간단한 형태로)
                if member_data["traits"]:
                    # 실제 특성 객체는 복원하지 않고 이름만 기록
                    character.trait_names = member_data["traits"]
                
                recreated_party.append(character)
            
            print(f"✅ 파티 '{party_id}'가 성공적으로 재생성되었습니다.")
            return recreated_party
            
        except Exception as e:
            print(f"⚠️ 파티 재생성 실패: {e}")
            return None
    
    def get_party_summary_stats(self) -> Dict:
        """파티 히스토리 요약 통계"""
        if not self.history_data:
            return {"total_parties": 0}
        
        stats = {
            "total_parties": len(self.history_data),
            "avg_party_level": 0,
            "total_exploration_time": 0,
            "most_used_classes": {},
            "level_distribution": {"1-10": 0, "11-20": 0, "21-30": 0, "31+": 0}
        }
        
        total_avg_level = 0
        class_usage = {}
        
        for party in self.history_data:
            # 평균 레벨 계산
            avg_level = party.get("avg_level", 0)
            total_avg_level += avg_level
            
            # 레벨 분포
            if avg_level <= 10:
                stats["level_distribution"]["1-10"] += 1
            elif avg_level <= 20:
                stats["level_distribution"]["11-20"] += 1
            elif avg_level <= 30:
                stats["level_distribution"]["21-30"] += 1
            else:
                stats["level_distribution"]["31+"] += 1
            
            # 직업 사용 빈도
            for comp in party.get("party_composition", []):
                if "×" in comp:
                    class_name, count = comp.split("×")
                    class_usage[class_name] = class_usage.get(class_name, 0) + int(count)
        
        stats["avg_party_level"] = total_avg_level // len(self.history_data)
        stats["most_used_classes"] = dict(sorted(class_usage.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return stats

# 전역 인스턴스
party_history_manager = PartyHistoryManager()
