"""
⚔️ Dawn of Stellar - 멀티플레이어 전투 시스템
Phase 1: 동기화된 ATB 전투 시스템

기존의 BraveCombatSystem을 멀티플레이어 환경에서 동작하도록 확장한 시스템입니다.
ATB 게이지, 턴 순서, 전투 액션이 모든 플레이어 간에 실시간으로 동기화됩니다.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import copy

from .brave_combat import BraveCombatSystem
from .character import Character
from .multiplayer_session import MultiplayerGameSession, get_multiplayer_session
from .multiplayer_protocol import (
    GameMessage, GameMessageType, GameStateProtocol, GameStateConverter,
    CharacterState, CombatState
)
from .error_logger import log_debug, log_error, log_combat

class MultiplayerCombatPhase(Enum):
    """멀티플레이어 전투 단계"""
    WAITING_FOR_PLAYERS = "waiting_for_players"
    COMBAT_SETUP = "combat_setup"
    ATB_PROCESSING = "atb_processing"
    ACTION_SELECTION = "action_selection"
    ACTION_EXECUTION = "action_execution"
    TURN_RESOLUTION = "turn_resolution"
    COMBAT_END = "combat_end"

class MultiplayerBraveCombatSystem(BraveCombatSystem):
    """멀티플레이어 브레이브 전투 시스템"""
    
    def __init__(self, party: List[Character], enemies: List[Character]):
        super().__init__(party, enemies)
        
        # 멀티플레이어 관련
        self.mp_session = get_multiplayer_session()
        self.combat_phase = MultiplayerCombatPhase.WAITING_FOR_PLAYERS
        self.combat_id = f"combat_{int(time.time())}"
        
        # 동기화 상태
        self.is_host = self.mp_session.network.is_host()
        self.sync_pending = False
        self.last_sync_time = time.time()
        self.sync_interval = 0.1  # 100ms 간격으로 빠른 동기화
        
        # 플레이어 액션 대기
        self.pending_actions: Dict[str, Dict[str, Any]] = {}  # player_id -> action_data
        self.action_confirmations: Dict[str, bool] = {}  # player_id -> confirmed
        
        # ATB 동기화
        self.atb_sync_threshold = 50  # ATB 차이가 50 이상일 때만 동기화
        self.last_atb_states: Dict[str, int] = {}  # character_id -> atb_value
        
        # 전투 로그 동기화
        self.combat_events: List[Dict[str, Any]] = []
        self.event_sequence = 0
        
        log_combat("멀티플레이어전투", f"멀티플레이어 전투 시스템 초기화", {
            "전투ID": self.combat_id,
            "호스트여부": self.is_host,
            "아군수": len(party),
            "적수": len(enemies)
        })
        
        # 세션 콜백 등록
        self.mp_session.on_combat_action = self._handle_remote_combat_action
        
        # 동기화 태스크 시작 (호스트만)
        if self.is_host:
            asyncio.create_task(self._combat_sync_loop())
    
    async def start_multiplayer_combat(self) -> bool:
        """멀티플레이어 전투 시작"""
        try:
            self.combat_phase = MultiplayerCombatPhase.COMBAT_SETUP
            
            # 호스트만 전투 시작 처리
            if self.is_host:
                await self.mp_session.start_combat(self.party, self.enemies)
                
                # 초기 전투 상태 동기화
                await self._sync_combat_state()
                
                self.combat_phase = MultiplayerCombatPhase.ATB_PROCESSING
                
                log_combat("멀티플레이어전투", f"✅ 전투 시작 (호스트)", {
                    "전투ID": self.combat_id,
                    "참가자수": self.mp_session.get_current_player_count()
                })
                
                # 전투 루프 시작
                asyncio.create_task(self._multiplayer_battle_loop())
            
            else:
                # 피어는 호스트의 전투 시작을 대기
                self.combat_phase = MultiplayerCombatPhase.WAITING_FOR_PLAYERS
                log_combat("멀티플레이어전투", f"전투 시작 대기 (피어)", {
                    "전투ID": self.combat_id
                })
            
            return True
            
        except Exception as e:
            log_error("멀티플레이어전투", f"전투 시작 실패: {e}")
            return False
    
    async def _multiplayer_battle_loop(self):
        """멀티플레이어 전투 메인 루프 (호스트만)"""
        try:
            while not self.battle_ended:
                # ATB 게이지 업데이트
                self._update_all_atb()
                
                # ATB 상태 동기화
                await self._sync_atb_if_needed()
                
                # 행동 가능한 캐릭터 확인
                ready_characters = self._get_ready_characters()
                
                if ready_characters:
                    # 우선순위가 가장 높은 캐릭터 선택
                    current_character = self._get_highest_priority_character(ready_characters)
                    
                    if current_character in self.party:
                        # 플레이어 캐릭터 - 액션 대기
                        await self._handle_player_turn(current_character)
                    else:
                        # 적 캐릭터 - 즉시 처리
                        await self._handle_enemy_turn(current_character)
                
                # 전투 종료 조건 확인
                if self._check_battle_end():
                    await self._end_multiplayer_combat()
                    break
                
                # 동기화 간격 유지
                await asyncio.sleep(self.sync_interval)
                
        except Exception as e:
            log_error("멀티플레이어전투", f"전투 루프 오류: {e}")
    
    async def _handle_player_turn(self, character: Character):
        """플레이어 턴 처리"""
        self.combat_phase = MultiplayerCombatPhase.ACTION_SELECTION
        
        # 해당 플레이어에게 액션 요청 (실제로는 UI를 통해 처리)
        player_id = self._get_player_id_by_character(character)
        
        if player_id:
            log_combat("멀티플레이어전투", f"플레이어 턴 시작", {
                "플레이어ID": player_id,
                "캐릭터": character.name,
                "ATB": character.atb_gauge
            })
            
            # 액션 대기 상태로 전환
            self.pending_actions[player_id] = None
            self.action_confirmations[player_id] = False
            
            # 턴 타임아웃 설정 (30초)
            asyncio.create_task(self._action_timeout(player_id, 30.0))
    
    async def _handle_enemy_turn(self, enemy: Character):
        """적 턴 처리 (호스트만)"""
        self.combat_phase = MultiplayerCombatPhase.ACTION_EXECUTION
        
        # 기존 AI 로직 사용
        action_result = self._process_enemy_turn(enemy)
        
        if action_result:
            # 적 액션을 모든 플레이어에게 동기화
            await self._broadcast_enemy_action(enemy, action_result)
            
            # ATB 소모
            enemy.atb_gauge = max(0, enemy.atb_gauge - 1000)
            
            log_combat("멀티플레이어전투", f"적 턴 완료", {
                "적": enemy.name,
                "액션": action_result.get('action_type', 'unknown'),
                "남은ATB": enemy.atb_gauge
            })
    
    async def handle_player_action(self, player_id: str, action_data: Dict[str, Any]) -> bool:
        """플레이어 액션 처리"""
        try:
            # 액션 유효성 검증
            if not self._validate_player_action(player_id, action_data):
                return False
            
            # 액션 저장
            self.pending_actions[player_id] = action_data
            
            # 호스트가 아니면 호스트에게 전송
            if not self.is_host:
                await self.mp_session.handle_combat_action(
                    player_id=player_id,
                    action_type=action_data['action_type'],
                    target_id=action_data['target_id'],
                    skill_name=action_data.get('skill_name')
                )
            else:
                # 호스트는 즉시 처리
                await self._execute_player_action(player_id, action_data)
            
            return True
            
        except Exception as e:
            log_error("멀티플레이어전투", f"플레이어 액션 처리 실패: {e}")
            return False
    
    async def _execute_player_action(self, player_id: str, action_data: Dict[str, Any]):
        """플레이어 액션 실행 (호스트만)"""
        character = self._get_character_by_player_id(player_id)
        if not character:
            return
        
        self.combat_phase = MultiplayerCombatPhase.ACTION_EXECUTION
        
        action_type = action_data['action_type']
        target_id = action_data['target_id']
        skill_name = action_data.get('skill_name')
        
        # 기존 전투 시스템 로직 사용
        if action_type == 'attack':
            target = self._get_character_by_id(target_id)
            if target:
                damage_result = self._process_attack(character, target, skill_name)
                await self._broadcast_damage_result(character, target, damage_result)
        
        elif action_type == 'skill':
            result = self._process_skill_use(character, skill_name, target_id)
            await self._broadcast_skill_result(character, result)
        
        elif action_type == 'item':
            result = self._process_item_use(character, action_data['item_name'])
            await self._broadcast_item_result(character, result)
        
        # ATB 소모
        character.atb_gauge = max(0, character.atb_gauge - 1000)
        
        # 액션 완료 처리
        self.action_confirmations[player_id] = True
        
        log_combat("멀티플레이어전투", f"플레이어 액션 실행 완료", {
            "플레이어": player_id,
            "캐릭터": character.name,
            "액션": action_type,
            "타겟": target_id
        })
    
    async def _handle_remote_combat_action(self, sender_id: str, action_data: Dict[str, Any]):
        """원격 플레이어의 전투 액션 처리"""
        if self.is_host:
            # 호스트: 액션 실행
            await self._execute_player_action(sender_id, action_data)
        else:
            # 피어: 액션 결과만 반영 (호스트에서 브로드캐스트될 예정)
            log_combat("멀티플레이어전투", f"원격 액션 수신", {
                "플레이어": sender_id,
                "액션": action_data['action_type']
            })
    
    async def _sync_combat_state(self):
        """전투 상태 동기화 (호스트만)"""
        if not self.is_host:
            return
        
        # 현재 전투 상태 생성
        combat_state = CombatState(
            is_in_combat=True,
            combat_id=self.combat_id,
            turn_number=self.turn_count,
            current_turn_character=None,  # ATB 시스템에서는 없음
            party_states=[GameStateConverter.character_to_state(char) for char in self.party],
            enemy_states=[GameStateConverter.character_to_state(enemy) for enemy in self.enemies],
            turn_order=[]  # ATB 시스템에서는 동적
        )
        
        # 전투 상태 메시지 전송
        state_msg = GameStateProtocol.create_combat_state_message(
            sender_id=self.mp_session.network.my_id,
            session_id=self.mp_session.session_id,
            combat_state=combat_state,
            turn_number=self.turn_count
        )
        
        await self.mp_session._send_game_message(state_msg)
        
        self.last_sync_time = time.time()
    
    async def _sync_atb_if_needed(self):
        """필요시 ATB 상태 동기화"""
        if not self.is_host:
            return
        
        current_time = time.time()
        if current_time - self.last_sync_time < self.sync_interval:
            return
        
        # ATB 변화가 큰 캐릭터들만 동기화
        for character in self.party + self.enemies:
            char_id = character.name  # 실제로는 unique ID 사용
            current_atb = character.atb_gauge
            last_atb = self.last_atb_states.get(char_id, 0)
            
            if abs(current_atb - last_atb) >= self.atb_sync_threshold:
                await self.mp_session.update_atb_gauge(char_id, current_atb)
                self.last_atb_states[char_id] = current_atb
    
    async def _broadcast_damage_result(self, attacker: Character, target: Character, 
                                     damage_result: Dict[str, Any]):
        """데미지 결과 브로드캐스트"""
        if not self.is_host:
            return
        
        await self.mp_session.deal_damage(
            attacker_id=attacker.name,
            target_id=target.name,
            damage_amount=damage_result.get('damage', 0),
            damage_type=damage_result.get('type', 'physical')
        )
        
        # 전투 이벤트 기록
        self._add_combat_event({
            'type': 'damage',
            'attacker': attacker.name,
            'target': target.name,
            'damage': damage_result.get('damage', 0),
            'timestamp': time.time()
        })
    
    async def _broadcast_skill_result(self, character: Character, skill_result: Dict[str, Any]):
        """스킬 결과 브로드캐스트"""
        # 스킬 사용 메시지 생성 및 전송
        skill_msg = GameMessage(
            type=GameMessageType.SKILL_USE,
            sender_id=self.mp_session.network.my_id,
            session_id=self.mp_session.session_id,
            turn_number=self.turn_count,
            data={
                'character': character.name,
                'skill_name': skill_result.get('skill_name'),
                'result': skill_result
            },
            timestamp=time.time()
        )
        
        await self.mp_session._send_game_message(skill_msg)
    
    async def _combat_sync_loop(self):
        """전투 동기화 루프 (호스트만)"""
        while not self.battle_ended and self.is_host:
            try:
                await asyncio.sleep(self.sync_interval * 5)  # 500ms 간격으로 전체 동기화
                
                if self.combat_phase in [MultiplayerCombatPhase.ATB_PROCESSING, 
                                       MultiplayerCombatPhase.ACTION_EXECUTION]:
                    await self._sync_combat_state()
                
            except Exception as e:
                log_error("멀티플레이어전투", f"동기화 루프 오류: {e}")
    
    async def _action_timeout(self, player_id: str, timeout_seconds: float):
        """액션 타임아웃 처리"""
        await asyncio.sleep(timeout_seconds)
        
        if (player_id in self.pending_actions and 
            not self.action_confirmations.get(player_id, False)):
            
            log_combat("멀티플레이어전투", f"플레이어 액션 타임아웃", {
                "플레이어": player_id,
                "타임아웃": timeout_seconds
            })
            
            # 기본 액션 (방어) 실행
            default_action = {
                'action_type': 'defend',
                'target_id': player_id
            }
            
            await self._execute_player_action(player_id, default_action)
    
    def _validate_player_action(self, player_id: str, action_data: Dict[str, Any]) -> bool:
        """플레이어 액션 유효성 검증"""
        try:
            # 기본 필드 확인
            required_fields = ['action_type', 'target_id']
            for field in required_fields:
                if field not in action_data:
                    return False
            
            # 액션 타입 확인
            valid_actions = ['attack', 'skill', 'item', 'defend', 'escape']
            if action_data['action_type'] not in valid_actions:
                return False
            
            # 캐릭터 존재 확인
            character = self._get_character_by_player_id(player_id)
            if not character or not character.is_alive:
                return False
            
            # ATB 게이지 확인
            if character.atb_gauge < 1000:  # ATB_READY_THRESHOLD
                return False
            
            return True
            
        except Exception as e:
            log_error("멀티플레이어전투", f"액션 검증 오류: {e}")
            return False
    
    def _add_combat_event(self, event: Dict[str, Any]):
        """전투 이벤트 추가"""
        event['sequence'] = self.event_sequence
        self.event_sequence += 1
        self.combat_events.append(event)
        
        # 이벤트 로그 크기 제한
        if len(self.combat_events) > 1000:
            self.combat_events = self.combat_events[-500:]
    
    def _get_player_id_by_character(self, character: Character) -> Optional[str]:
        """캐릭터로 플레이어 ID 찾기"""
        # 실제 구현에서는 캐릭터-플레이어 매핑 테이블 사용
        for player_id, player_char in self.mp_session.player_characters.items():
            if player_char.name == character.name:
                return player_id
        return None
    
    def _get_character_by_player_id(self, player_id: str) -> Optional[Character]:
        """플레이어 ID로 캐릭터 찾기"""
        return self.mp_session.player_characters.get(player_id)
    
    def _get_character_by_id(self, character_id: str) -> Optional[Character]:
        """캐릭터 ID로 캐릭터 찾기"""
        for char in self.party + self.enemies:
            if char.name == character_id:  # 실제로는 unique ID 사용
                return char
        return None
    
    async def _end_multiplayer_combat(self):
        """멀티플레이어 전투 종료"""
        self.combat_phase = MultiplayerCombatPhase.COMBAT_END
        self.battle_ended = True
        
        # 전투 종료 메시지 전송 (호스트만)
        if self.is_host:
            end_msg = GameMessage(
                type=GameMessageType.COMBAT_END,
                sender_id=self.mp_session.network.my_id,
                session_id=self.mp_session.session_id,
                turn_number=self.turn_count,
                data={
                    'combat_id': self.combat_id,
                    'victory': self._check_victory(),
                    'combat_events': self.combat_events[-10:]  # 마지막 10개 이벤트만
                },
                timestamp=time.time()
            )
            
            await self.mp_session._send_game_message(end_msg)
        
        log_combat("멀티플레이어전투", f"✅ 전투 종료", {
            "전투ID": self.combat_id,
            "승리": self._check_victory(),
            "턴수": self.turn_count
        })
    
    def get_multiplayer_status(self) -> Dict[str, Any]:
        """멀티플레이어 전투 상태 반환"""
        return {
            'combat_id': self.combat_id,
            'phase': self.combat_phase.value,
            'is_host': self.is_host,
            'pending_actions': len(self.pending_actions),
            'last_sync': self.last_sync_time,
            'event_count': len(self.combat_events),
            'turn_count': self.turn_count
        }

def create_multiplayer_combat_system(party: List[Character], 
                                   enemies: List[Character]) -> MultiplayerBraveCombatSystem:
    """멀티플레이어 전투 시스템 생성"""
    return MultiplayerBraveCombatSystem(party, enemies)
