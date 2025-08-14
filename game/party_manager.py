# party_manager.py
# 파티 관리 시스템

from typing import List
from game.character import Character


class PartyManager:
    """파티 관리자 클래스"""
    
    def __init__(self):
        self.party = []
        
    def add_member(self, character: Character):
        """파티원 추가"""
        if character not in self.party:
            self.party.append(character)
            
    def remove_member(self, character: Character):
        """파티원 제거"""
        if character in self.party:
            self.party.remove(character)
            
    def get_party_info(self) -> dict:
        """파티 정보 반환"""
        return {
            'size': len(self.party),
            'members': [member.name for member in self.party],
            'alive_count': sum(1 for member in self.party if member.is_alive)
        }
        
    def show_party_status(self) -> str:
        """파티 상태 표시 문자열 반환"""
        if not self.party:
            return "파티가 비어있습니다."
            
        status_lines = ["=== 파티 상태 ==="]
        for i, member in enumerate(self.party, 1):
            hp_info = f"{member.current_hp}/{member.max_hp}"
            mp_info = f"{member.current_mp}/{member.max_mp}"
            status = "생존" if member.is_alive else "전투불능"
            status_lines.append(f"{i}. {member.name} [{member.job}] - HP:{hp_info} MP:{mp_info} ({status})")
            
        return "\n".join(status_lines)
        
    def display_party(self):
        """파티 상태 출력"""
        print(self.show_party_status())
