"""
🎮 Dawn of Stellar - 핫시트 멀티플레이어 시스템
로컬 멀티플레이어: 한 컴퓨터에서 여러 플레이어가 번갈아가며 플레이

이 시스템은 기존 싱글플레이어 게임을 그대로 유지하면서,
파티 멤버들을 여러 플레이어가 조종할 수 있게 합니다.
- 한 명이 탐험을 총괄
- 전투 시 각자 자신의 캐릭터 조종
- 바톤 터치로 조종권 이양
- 기존 세이브파일 100% 호환
"""

import time
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .error_logger import log_system, log_player
from .color_text import bright_cyan, bright_yellow, bright_green, bright_red, cyan, yellow, red, green, white, bright_white

class HotSeatPhase(Enum):
    """핫시트 게임 단계"""
    EXPLORATION = "exploration"    # 탐험 단계 (한 명이 조종)
    COMBAT_SETUP = "combat_setup"  # 전투 준비 (각자 준비)
    COMBAT_TURN = "combat_turn"    # 전투 턴 (개별 조종)
    DECISION = "decision"          # 중요 결정 (투표/합의)
    ITEM_MANAGEMENT = "item_mgmt"  # 아이템 관리 (개별 조종)

class HotSeatMultiplayer:
    """핫시트 멀티플레이어 매니저"""
    
    def __init__(self, game_instance=None):
        self.game = game_instance
        self.enabled = False
        
        # 플레이어 설정
        self.players: Dict[str, Dict] = {}  # player_id: {name, color, assigned_characters}
        self.current_player_id: Optional[str] = None
        self.explorer_player_id: Optional[str] = None  # 탐험 담당 플레이어
        
        # 게임 상태
        self.current_phase = HotSeatPhase.EXPLORATION
        self.character_assignments: Dict[str, str] = {}  # character_name: player_id
        
        # 설정
        self.auto_pass_exploration = False  # 탐험 중 자동으로 다음 플레이어에게 넘김
        self.voting_enabled = True  # 중요 결정 시 투표 시스템
        
        log_system("핫시트멀티", "핫시트 멀티플레이어 시스템 초기화")
    
    def setup_hotseat_mode(self) -> bool:
        """핫시트 모드 설정"""
        try:
            print(f"\n{bright_cyan('🎮 핫시트 멀티플레이어 설정')}")
            print("=" * 40)
            print()
            print(f"{bright_yellow('핫시트 멀티플레이어란?')}")
            print("• 한 컴퓨터에서 여러 플레이어가 번갈아가며 플레이")
            print("• 각자 파티 멤버를 배정받아 조종")
            print("• 탐험은 한 명이 담당, 전투는 각자 조종")
            print("• 기존 세이브파일과 100% 호환")
            print()
            
            # 플레이어 수 입력
            while True:
                try:
                    player_count = input(f"{cyan('플레이어 수 (2-4명): ')}")
                    player_count = int(player_count)
                    if 2 <= player_count <= 4:
                        break
                    else:
                        print(f"{bright_red('2-4명 사이로 입력해주세요.')}")
                except ValueError:
                    print(f"{bright_red('숫자를 입력해주세요.')}")
            
            # 플레이어 정보 입력
            player_colors = ['🔴', '🔵', '🟢', '🟡']
            
            for i in range(player_count):
                print(f"\n{cyan(f'플레이어 {i+1} 설정:')}")
                
                # 플레이어 이름
                while True:
                    name = input(f"  이름: ").strip()
                    if name and name not in [p['name'] for p in self.players.values()]:
                        break
                    elif not name:
                        print(f"  {bright_red('이름을 입력해주세요.')}")
                    else:
                        print(f"  {bright_red('이미 사용 중인 이름입니다.')}")
                
                player_id = f"player_{i+1}"
                self.players[player_id] = {
                    'name': name,
                    'color': player_colors[i],
                    'assigned_characters': []
                }
                
                print(f"  {player_colors[i]} {name} 등록 완료!")
            
            # 탐험 담당자 설정
            print(f"\n{cyan('탐험 담당자 설정:')}")
            print("탐험 담당자는 맵 이동, 아이템 수집, 층 이동을 담당합니다.")
            
            for i, (player_id, player_info) in enumerate(self.players.items(), 1):
                print(f"  {i}. {player_info['color']} {player_info['name']}")
            
            while True:
                try:
                    choice = int(input(f"탐험 담당자 선택 (1-{len(self.players)}): "))
                    if 1 <= choice <= len(self.players):
                        selected_player_id = list(self.players.keys())[choice-1]
                        self.explorer_player_id = selected_player_id
                        explorer_name = self.players[selected_player_id]['name']
                        print(f"{bright_green(f'탐험 담당자: {explorer_name}')}")
                        break
                    else:
                        print(f"{bright_red('올바른 번호를 입력해주세요.')}")
                except ValueError:
                    print(f"{bright_red('숫자를 입력해주세요.')}")
            
            # 캐릭터 배정은 게임 시작 후 진행
            self.enabled = True
            self.current_player_id = self.explorer_player_id
            
            print(f"\n{bright_green('✅ 핫시트 멀티플레이어 설정 완료!')}")
            print(f"등록된 플레이어: {len(self.players)}명")
            
            return True
            
        except Exception as e:
            print(f"{bright_red(f'핫시트 설정 실패: {e}')}")
            return False
    
    def assign_characters(self, party_members: List) -> bool:
        """파티 멤버에게 플레이어 배정"""
        if not self.enabled or not party_members:
            return False
        
        try:
            print(f"\n{bright_cyan('👥 캐릭터 배정')}")
            print("=" * 30)
            print()
            
            # 파티 멤버 표시
            print(f"{cyan('파티 멤버:')}")
            for i, member in enumerate(party_members, 1):
                print(f"  {i}. {member.name} ({member.job_class}) Lv.{member.level}")
            
            print()
            
            # 자동 배정 vs 수동 배정
            auto_assign = input(f"{cyan('자동 배정하시겠습니까? (y/N): ')}").lower() == 'y'
            
            if auto_assign:
                # 자동 배정: 순서대로 배정
                player_ids = list(self.players.keys())
                for i, member in enumerate(party_members):
                    player_id = player_ids[i % len(player_ids)]
                    self.character_assignments[member.name] = player_id
                    self.players[player_id]['assigned_characters'].append(member.name)
                
                print(f"\n{bright_green('자동 배정 완료:')}")
                for member in party_members:
                    player_id = self.character_assignments[member.name]
                    player_info = self.players[player_id]
                    print(f"  {player_info['color']} {member.name} → {player_info['name']}")
            
            else:
                # 수동 배정
                print(f"\n{cyan('수동 배정 모드:')}")
                
                for member in party_members:
                    print(f"\n캐릭터: {member.name} ({member.job_class})")
                    
                    # 플레이어 목록 표시
                    for i, (player_id, player_info) in enumerate(self.players.items(), 1):
                        assigned_count = len(player_info['assigned_characters'])
                        print(f"  {i}. {player_info['color']} {player_info['name']} (현재 {assigned_count}명)")
                    
                    while True:
                        try:
                            choice = int(input(f"플레이어 선택 (1-{len(self.players)}): "))
                            if 1 <= choice <= len(self.players):
                                selected_player_id = list(self.players.keys())[choice-1]
                                self.character_assignments[member.name] = selected_player_id
                                self.players[selected_player_id]['assigned_characters'].append(member.name)
                                
                                player_name = self.players[selected_player_id]['name']
                                print(f"  {bright_green(f'{member.name} → {player_name}')}")
                                break
                            else:
                                print(f"  {bright_red('올바른 번호를 입력해주세요.')}")
                        except ValueError:
                            print(f"  {bright_red('숫자를 입력해주세요.')}")
            
            print(f"\n{bright_green('✅ 캐릭터 배정 완료!')}")
            return True
            
        except Exception as e:
            print(f"{bright_red(f'캐릭터 배정 실패: {e}')}")
            return False
    
    def get_current_player_info(self) -> Optional[Dict]:
        """현재 플레이어 정보 반환"""
        if not self.current_player_id:
            return None
        return self.players.get(self.current_player_id)
    
    def get_character_owner(self, character_name: str) -> Optional[str]:
        """캐릭터의 소유자 플레이어 ID 반환"""
        return self.character_assignments.get(character_name)
    
    def switch_to_character_owner(self, character_name: str) -> bool:
        """캐릭터 소유자로 바톤 터치"""
        owner_id = self.get_character_owner(character_name)
        if not owner_id:
            return False
        
        old_player = self.get_current_player_info()
        self.current_player_id = owner_id
        new_player = self.get_current_player_info()
        
        if old_player and new_player and old_player != new_player:
            print(f"\n{bright_yellow('🎮 바톤 터치!')}")
            print(f"{old_player['color']} {old_player['name']} → {new_player['color']} {new_player['name']}")
            print(f"({character_name}의 턴)")
            
            # 플레이어 교체 확인
            player_name = new_player["name"]
            input(f"{bright_cyan(f'{player_name}님, 준비되면 Enter를 누르세요...')}")
            
        return True
    
    def switch_to_explorer(self) -> bool:
        """탐험 담당자로 바톤 터치"""
        if not self.explorer_player_id:
            return False
        
        old_player = self.get_current_player_info()
        self.current_player_id = self.explorer_player_id
        new_player = self.get_current_player_info()
        
        if old_player and new_player and old_player != new_player:
            print(f"\n{bright_yellow('🗺️ 탐험 모드로 전환!')}")
            print(f"{old_player['color']} {old_player['name']} → {new_player['color']} {new_player['name']}")
            print(f"(탐험 담당)")
            
            player_name = new_player["name"]
            input(f"{bright_cyan(f'{player_name}님, 준비되면 Enter를 누르세요...')}")
        
        return True
    
    def show_current_status(self):
        """현재 핫시트 상태 표시"""
        if not self.enabled:
            return
        
        current_player = self.get_current_player_info()
        if not current_player:
            return
        
        # 현재 플레이어 표시
        phase_names = {
            HotSeatPhase.EXPLORATION: "🗺️ 탐험",
            HotSeatPhase.COMBAT_SETUP: "⚔️ 전투 준비",
            HotSeatPhase.COMBAT_TURN: "⚔️ 전투",
            HotSeatPhase.DECISION: "🤔 결정",
            HotSeatPhase.ITEM_MANAGEMENT: "🎒 아이템 관리"
        }
        
        phase_name = phase_names.get(self.current_phase, "🎮 게임")
        
        status_line = f"{cyan('핫시트:')} {current_player['color']} {current_player['name']} | {phase_name}"
        
        # 담당 캐릭터 표시 (전투 시)
        if self.current_phase in [HotSeatPhase.COMBAT_TURN, HotSeatPhase.ITEM_MANAGEMENT]:
            assigned_chars = current_player.get('assigned_characters', [])
            if assigned_chars:
                status_line += f" | 담당: {', '.join(assigned_chars[:2])}"
                if len(assigned_chars) > 2:
                    status_line += f" 외 {len(assigned_chars)-2}명"
        
        print(status_line)
    
    def handle_combat_turn(self, character_name: str) -> bool:
        """전투 턴 처리"""
        if not self.enabled:
            return True  # 핫시트 비활성화 시 정상 진행
        
        # 해당 캐릭터 소유자로 바톤 터치
        self.current_phase = HotSeatPhase.COMBAT_TURN
        return self.switch_to_character_owner(character_name)
    
    def handle_exploration(self) -> bool:
        """탐험 단계 처리"""
        if not self.enabled:
            return True
        
        self.current_phase = HotSeatPhase.EXPLORATION
        return self.switch_to_explorer()
    
    def handle_decision(self, decision_text: str) -> Optional[bool]:
        """중요 결정 처리 (투표 시스템)"""
        if not self.enabled or not self.voting_enabled:
            return None  # 일반 결정 진행
        
        print(f"\n{bright_cyan('🗳️ 파티 투표')}")
        print("=" * 20)
        print(f"결정 사안: {decision_text}")
        print()
        
        votes = {}
        
        for player_id, player_info in self.players.items():
            print(f"{player_info['color']} {player_info['name']}님의 투표:")
            
            while True:
                vote = input("  찬성(y) / 반대(n) / 기권(s): ").lower()
                if vote in ['y', 'n', 's']:
                    votes[player_id] = vote
                    vote_text = {'y': '찬성', 'n': '반대', 's': '기권'}[vote]
                    print(f"  → {vote_text}")
                    break
                else:
                    print(f"  {bright_red('y, n, s 중 하나를 입력해주세요.')}")
            print()
        
        # 투표 결과 집계
        yes_votes = sum(1 for v in votes.values() if v == 'y')
        no_votes = sum(1 for v in votes.values() if v == 'n')
        abstain_votes = sum(1 for v in votes.values() if v == 's')
        
        print(f"{bright_cyan('투표 결과:')}")
        print(f"  찬성: {yes_votes}표")
        print(f"  반대: {no_votes}표")
        print(f"  기권: {abstain_votes}표")
        print()
        
        if yes_votes > no_votes:
            print(f"{bright_green('✅ 가결 (찬성)')}")
            return True
        elif no_votes > yes_votes:
            print(f"{bright_red('❌ 부결 (반대)')}")
            return False
        else:
            print(f"{bright_yellow('⚖️ 동표 (탐험 담당자 결정권)')}")
            explorer = self.players[self.explorer_player_id]
            final_vote = input(f"{explorer['color']} {explorer['name']}님이 최종 결정해주세요 (y/n): ").lower()
            result = final_vote == 'y'
            result_text = "찬성" if result else "반대"
            print(f"최종 결정: {result_text}")
            return result
    
    def save_hotseat_data(self) -> Dict:
        """핫시트 데이터 저장용 딕셔너리 반환"""
        if not self.enabled:
            return {}
        
        return {
            'enabled': self.enabled,
            'players': self.players,
            'current_player_id': self.current_player_id,
            'explorer_player_id': self.explorer_player_id,
            'character_assignments': self.character_assignments,
            'current_phase': self.current_phase.value,
            'auto_pass_exploration': self.auto_pass_exploration,
            'voting_enabled': self.voting_enabled
        }
    
    def load_hotseat_data(self, data: Dict) -> bool:
        """핫시트 데이터 로드"""
        try:
            if not data or not data.get('enabled', False):
                self.enabled = False
                return True
            
            self.enabled = data['enabled']
            self.players = data['players']
            self.current_player_id = data['current_player_id']
            self.explorer_player_id = data['explorer_player_id']
            self.character_assignments = data['character_assignments']
            self.current_phase = HotSeatPhase(data['current_phase'])
            self.auto_pass_exploration = data.get('auto_pass_exploration', False)
            self.voting_enabled = data.get('voting_enabled', True)
            
            print(f"\n{bright_green('✅ 핫시트 멀티플레이어 데이터 로드 완료!')}")
            print(f"플레이어: {len(self.players)}명")
            
            return True
            
        except Exception as e:
            print(f"{bright_red(f'핫시트 데이터 로드 실패: {e}')}")
            self.enabled = False
            return False
    
    def show_player_assignments(self):
        """플레이어 배정 현황 표시"""
        if not self.enabled:
            return
        
        print(f"\n{bright_cyan('👥 플레이어 배정 현황')}")
        print("=" * 30)
        
        for player_id, player_info in self.players.items():
            role = " (탐험 담당)" if player_id == self.explorer_player_id else ""
            current = " ⬅️ 현재" if player_id == self.current_player_id else ""
            
            print(f"{player_info['color']} {player_info['name']}{role}{current}")
            
            assigned_chars = player_info.get('assigned_characters', [])
            if assigned_chars:
                print(f"  담당 캐릭터: {', '.join(assigned_chars)}")
            else:
                print(f"  담당 캐릭터: 없음")
            print()

# 전역 핫시트 매니저 인스턴스
_hotseat_manager = None

def get_hotseat_manager() -> HotSeatMultiplayer:
    """전역 핫시트 매니저 반환"""
    global _hotseat_manager
    if _hotseat_manager is None:
        _hotseat_manager = HotSeatMultiplayer()
    return _hotseat_manager

def setup_hotseat_multiplayer(game_instance) -> bool:
    """핫시트 멀티플레이어 설정"""
    manager = get_hotseat_manager()
    manager.game = game_instance
    return manager.setup_hotseat_mode()
