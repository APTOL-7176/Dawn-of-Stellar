#!/usr/bin/env python3
"""
ATB (Active Time Battle) 시스템
- 속도 기반 턴 순서
- 실시간 전투 시스템
- 캐스팅 시간과 쿨다운 관리
"""

import time
import heapq
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass

class ActionType(Enum):
    """행동 타입"""
    ATTACK = "attack"
    SKILL = "skill"
    MAGIC = "magic"
    ITEM = "item"
    DEFEND = "defend"
    MOVE = "move"
    WAIT = "wait"

class ActionStatus(Enum):
    """행동 상태"""
    READY = "ready"           # 준비됨
    CASTING = "casting"       # 캐스팅 중
    COOLDOWN = "cooldown"     # 쿨다운 중
    DISABLED = "disabled"     # 비활성화

@dataclass
class ATBAction:
    """ATB 행동"""
    character_id: str
    action_type: ActionType
    target_id: Optional[str]
    skill_id: Optional[str]
    cast_time: float
    execute_time: float
    priority: int = 0
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

class ATBCharacter:
    """ATB 캐릭터"""
    
    def __init__(self, character_id: str, character_data: Dict):
        self.character_id = character_id
        self.character_data = character_data
        
        # ATB 관련 속성
        self.atb_gauge = 0.0
        self.atb_max = 100.0
        self.speed = character_data.get("speed", 50)
        self.haste_multiplier = 1.0
        self.slow_multiplier = 1.0
        
        # 행동 상태
        self.current_action: Optional[ATBAction] = None
        self.action_queue: List[ATBAction] = []
        self.cast_start_time: Optional[float] = None
        
        # 쿨다운 관리
        self.skill_cooldowns: Dict[str, float] = {}
        self.global_cooldown = 0.0
        
        # 상태 이상
        self.is_stunned = False
        self.is_paralyzed = False
        self.is_confused = False
        self.is_sleeping = False
        
    def get_effective_speed(self) -> float:
        """실제 속도 계산 (버프/디버프 포함)"""
        base_speed = self.speed
        
        # 상태 이상으로 인한 속도 변화
        if self.is_stunned or self.is_paralyzed or self.is_sleeping:
            return 0
        
        # 헤이스트/슬로우 효과
        speed_modifier = self.haste_multiplier / self.slow_multiplier
        
        # 혼란 상태에서는 속도 감소
        if self.is_confused:
            speed_modifier *= 0.7
        
        return base_speed * speed_modifier
    
    def update_atb_gauge(self, delta_time: float):
        """ATB 게이지 업데이트"""
        if self.current_action is None:
            effective_speed = self.get_effective_speed()
            self.atb_gauge += effective_speed * delta_time
            self.atb_gauge = min(self.atb_gauge, self.atb_max)
    
    def is_ready_to_act(self) -> bool:
        """행동 준비 완료 여부"""
        return (self.atb_gauge >= self.atb_max and 
                self.current_action is None and 
                self.global_cooldown <= 0 and
                not self.is_stunned and 
                not self.is_sleeping)
    
    def can_use_skill(self, skill_id: str) -> bool:
        """스킬 사용 가능 여부"""
        if skill_id in self.skill_cooldowns and self.skill_cooldowns[skill_id] > 0:
            return False
        
        # MP, 스태미나 등 자원 체크 (실제 캐릭터 데이터 참조)
        return True
    
    def start_action(self, action: ATBAction) -> bool:
        """행동 시작"""
        if not self.is_ready_to_act():
            return False
        
        self.current_action = action
        self.cast_start_time = time.time()
        self.atb_gauge = 0.0  # 행동 시작 시 게이지 리셋
        
        return True
    
    def complete_action(self):
        """행동 완료"""
        if self.current_action:
            # 스킬 쿨다운 설정
            if self.current_action.skill_id:
                skill_data = self._get_skill_data(self.current_action.skill_id)
                if skill_data:
                    cooldown = skill_data.get("cooldown", 0)
                    self.skill_cooldowns[self.current_action.skill_id] = cooldown
            
            # 글로벌 쿨다운 설정
            self.global_cooldown = 1.0  # 기본 1초
            
            self.current_action = None
            self.cast_start_time = None
    
    def cancel_action(self):
        """행동 취소"""
        self.current_action = None
        self.cast_start_time = None
        # ATB 게이지는 부분적으로 회복
        self.atb_gauge = min(self.atb_max * 0.3, self.atb_gauge)
    
    def update_cooldowns(self, delta_time: float):
        """쿨다운 업데이트"""
        # 글로벌 쿨다운
        if self.global_cooldown > 0:
            self.global_cooldown -= delta_time
            self.global_cooldown = max(0, self.global_cooldown)
        
        # 스킬 쿨다운
        for skill_id in list(self.skill_cooldowns.keys()):
            self.skill_cooldowns[skill_id] -= delta_time
            if self.skill_cooldowns[skill_id] <= 0:
                del self.skill_cooldowns[skill_id]
    
    def _get_skill_data(self, skill_id: str) -> Optional[Dict]:
        """스킬 데이터 조회"""
        # skill_system에서 스킬 데이터 조회
        try:
            from skill_system import get_skill_by_id
            return get_skill_by_id(skill_id)
        except ImportError:
            return None

class ATBSystem:
    """ATB 시스템 관리자"""
    
    def __init__(self):
        self.characters: Dict[str, ATBCharacter] = {}
        self.action_queue: List[Tuple[float, ATBAction]] = []  # (execute_time, action)
        self.battle_time = 0.0
        self.is_battle_active = False
        self.time_scale = 1.0  # 시간 스케일 (빠르게/느리게)
        
        # 콜백 함수들
        self.on_action_ready: Optional[Callable[[str], None]] = None
        self.on_action_executed: Optional[Callable[[ATBAction, Any], None]] = None
        self.on_battle_end: Optional[Callable[[], None]] = None
    
    def add_character(self, character_id: str, character_data: Dict):
        """캐릭터 추가"""
        self.characters[character_id] = ATBCharacter(character_id, character_data)
    
    def remove_character(self, character_id: str):
        """캐릭터 제거"""
        if character_id in self.characters:
            del self.characters[character_id]
    
    def start_battle(self):
        """전투 시작"""
        self.is_battle_active = True
        self.battle_time = 0.0
        
        # 모든 캐릭터 ATB 게이지 초기화
        for character in self.characters.values():
            character.atb_gauge = 0.0
            character.current_action = None
            character.skill_cooldowns.clear()
            character.global_cooldown = 0.0
    
    def end_battle(self):
        """전투 종료"""
        self.is_battle_active = False
        self.action_queue.clear()
        
        if self.on_battle_end:
            self.on_battle_end()
    
    def update(self, delta_time: float):
        """ATB 시스템 업데이트"""
        if not self.is_battle_active:
            return
        
        scaled_delta = delta_time * self.time_scale
        self.battle_time += scaled_delta
        
        # 캐릭터 업데이트
        for character in self.characters.values():
            character.update_atb_gauge(scaled_delta)
            character.update_cooldowns(scaled_delta)
            
            # 캐스팅 중인 행동 체크
            if character.current_action and character.cast_start_time:
                cast_elapsed = time.time() - character.cast_start_time
                if cast_elapsed >= character.current_action.cast_time:
                    self._execute_action(character.current_action)
                    character.complete_action()
            
            # 행동 준비 완료 알림
            if character.is_ready_to_act() and self.on_action_ready:
                self.on_action_ready(character.character_id)
        
        # 예약된 행동 실행
        self._process_action_queue()
    
    def queue_action(self, character_id: str, action_type: ActionType, 
                    target_id: Optional[str] = None, skill_id: Optional[str] = None,
                    cast_time: float = 0.0, priority: int = 0) -> bool:
        """행동 예약"""
        character = self.characters.get(character_id)
        if not character or not character.is_ready_to_act():
            return False
        
        # 스킬 사용 가능성 체크
        if skill_id and not character.can_use_skill(skill_id):
            return False
        
        execute_time = self.battle_time + cast_time
        action = ATBAction(
            character_id=character_id,
            action_type=action_type,
            target_id=target_id,
            skill_id=skill_id,
            cast_time=cast_time,
            execute_time=execute_time,
            priority=priority
        )
        
        # 즉시 실행 (캐스팅 시간 0) 또는 큐에 추가
        if cast_time <= 0:
            self._execute_action(action)
            character.complete_action()
        else:
            character.start_action(action)
        
        return True
    
    def _process_action_queue(self):
        """행동 큐 처리"""
        current_time = self.battle_time
        
        while self.action_queue and self.action_queue[0][0] <= current_time:
            execute_time, action = heapq.heappop(self.action_queue)
            self._execute_action(action)
            
            # 캐릭터 행동 완료 처리
            character = self.characters.get(action.character_id)
            if character:
                character.complete_action()
    
    def _execute_action(self, action: ATBAction):
        """행동 실행"""
        character = self.characters.get(action.character_id)
        if not character:
            return
        
        result = None
        
        if action.action_type == ActionType.ATTACK:
            result = self._execute_attack(action)
        elif action.action_type == ActionType.SKILL:
            result = self._execute_skill(action)
        elif action.action_type == ActionType.MAGIC:
            result = self._execute_magic(action)
        elif action.action_type == ActionType.ITEM:
            result = self._execute_item(action)
        elif action.action_type == ActionType.DEFEND:
            result = self._execute_defend(action)
        
        # 행동 실행 콜백
        if self.on_action_executed:
            self.on_action_executed(action, result)
    
    def _execute_attack(self, action: ATBAction) -> Dict[str, Any]:
        """기본 공격 실행"""
        attacker = self.characters.get(action.character_id)
        target = self.characters.get(action.target_id) if action.target_id else None
        
        if not attacker or not target:
            return {"success": False, "message": "공격 대상을 찾을 수 없습니다."}
        
        # 실제 데미지 계산은 전투 시스템과 연동
        damage = attacker.character_data.get("attack", 10)
        
        return {
            "success": True,
            "action": "attack",
            "attacker": action.character_id,
            "target": action.target_id,
            "damage": damage
        }
    
    def _execute_skill(self, action: ATBAction) -> Dict[str, Any]:
        """스킬 실행"""
        character = self.characters.get(action.character_id)
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다."}
        
        # 스킬 데이터 가져오기
        skill_data = character._get_skill_data(action.skill_id)
        if not skill_data:
            return {"success": False, "message": "스킬 데이터를 찾을 수 없습니다."}
        
        # 실제 스킬 효과 계산
        damage = skill_data.get("damage", 0)
        healing = skill_data.get("healing", 0)
        element = skill_data.get("element", "neutral")
        
        return {
            "success": True,
            "action": "skill",
            "character": action.character_id,
            "skill": action.skill_id,
            "target": action.target_id,
            "damage": damage,
            "healing": healing,
            "element": element,
            "cast_time": skill_data.get("cast_time", 0.0)
        }
    
    def _execute_magic(self, action: ATBAction) -> Dict[str, Any]:
        """마법 실행"""
        return self._execute_skill(action)  # 마법도 스킬로 처리
    
    def _execute_item(self, action: ATBAction) -> Dict[str, Any]:
        """아이템 사용"""
        character = self.characters.get(action.character_id)
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다."}
        
        return {
            "success": True,
            "action": "item",
            "character": action.character_id,
            "item": action.data.get("item_id")
        }
    
    def _execute_defend(self, action: ATBAction) -> Dict[str, Any]:
        """방어 실행"""
        character = self.characters.get(action.character_id)
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다."}
        
        # 방어 효과 적용 (실제 시스템과 연동)
        return {
            "success": True,
            "action": "defend",
            "character": action.character_id
        }
    
    def apply_status_effect(self, character_id: str, effect_type: str, duration: float):
        """상태 이상 적용"""
        character = self.characters.get(character_id)
        if not character:
            return
        
        if effect_type == "stun":
            character.is_stunned = True
        elif effect_type == "paralyze":
            character.is_paralyzed = True
        elif effect_type == "confuse":
            character.is_confused = True
        elif effect_type == "sleep":
            character.is_sleeping = True
        elif effect_type == "haste":
            character.haste_multiplier = 1.5
        elif effect_type == "slow":
            character.slow_multiplier = 2.0
        
        # 지속 시간 후 효과 제거 스케줄링 (실제 구현 시 타이머 시스템 필요)
    
    def get_turn_order(self) -> List[Tuple[str, float]]:
        """현재 턴 순서 조회 (캐릭터 ID, 예상 행동 시간)"""
        turn_order = []
        
        for character in self.characters.values():
            if character.is_ready_to_act():
                turn_order.append((character.character_id, 0.0))
            else:
                # ATB 게이지가 가득 찰 때까지의 시간 계산
                remaining_gauge = character.atb_max - character.atb_gauge
                effective_speed = character.get_effective_speed()
                
                if effective_speed > 0:
                    time_to_ready = remaining_gauge / effective_speed
                    turn_order.append((character.character_id, time_to_ready))
        
        # 예상 시간 순으로 정렬
        turn_order.sort(key=lambda x: x[1])
        return turn_order
    
    def get_character_status(self, character_id: str) -> Dict[str, Any]:
        """캐릭터 ATB 상태 조회"""
        character = self.characters.get(character_id)
        if not character:
            return {}
        
        return {
            "atb_gauge": character.atb_gauge,
            "atb_max": character.atb_max,
            "atb_percentage": (character.atb_gauge / character.atb_max) * 100,
            "is_ready": character.is_ready_to_act(),
            "current_action": character.current_action.action_type.value if character.current_action else None,
            "casting_progress": self._get_casting_progress(character),
            "cooldowns": dict(character.skill_cooldowns),
            "global_cooldown": character.global_cooldown,
            "speed": character.get_effective_speed(),
            "status_effects": self._get_status_effects(character)
        }
    
    def _get_casting_progress(self, character: ATBCharacter) -> float:
        """캐스팅 진행도 (0.0 ~ 1.0)"""
        if not character.current_action or not character.cast_start_time:
            return 0.0
        
        elapsed = time.time() - character.cast_start_time
        total_time = character.current_action.cast_time
        
        if total_time <= 0:
            return 1.0
        
        return min(1.0, elapsed / total_time)
    
    def _get_status_effects(self, character: ATBCharacter) -> List[str]:
        """활성 상태 이상 목록"""
        effects = []
        
        if character.is_stunned:
            effects.append("기절")
        if character.is_paralyzed:
            effects.append("마비")
        if character.is_confused:
            effects.append("혼란")
        if character.is_sleeping:
            effects.append("수면")
        if character.haste_multiplier > 1.0:
            effects.append("헤이스트")
        if character.slow_multiplier > 1.0:
            effects.append("슬로우")
        
        return effects
    
    def set_time_scale(self, scale: float):
        """시간 스케일 설정 (전투 속도 조절)"""
        self.time_scale = max(0.1, min(5.0, scale))  # 0.1배 ~ 5배
    
    def pause_battle(self):
        """전투 일시정지"""
        self.time_scale = 0.0
    
    def resume_battle(self):
        """전투 재개"""
        self.time_scale = 1.0

# 전역 ATB 시스템
atb_system = ATBSystem()

def get_atb_system() -> ATBSystem:
    """ATB 시스템 반환"""
    return atb_system

def start_atb_battle(characters: List[Dict]) -> ATBSystem:
    """ATB 전투 시작"""
    system = get_atb_system()
    
    # 캐릭터들 추가
    for char_data in characters:
        char_id = char_data.get("id") or char_data.get("name")
        system.add_character(char_id, char_data)
    
    system.start_battle()
    return system

def queue_atb_action(character_id: str, action_type: str, **kwargs) -> bool:
    """ATB 행동 예약"""
    system = get_atb_system()
    action_enum = ActionType(action_type)
    
    return system.queue_action(
        character_id=character_id,
        action_type=action_enum,
        target_id=kwargs.get("target_id"),
        skill_id=kwargs.get("skill_id"),
        cast_time=kwargs.get("cast_time", 0.0),
        priority=kwargs.get("priority", 0)
    )
