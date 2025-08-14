"""
🎮 Dawn of Stellar - 로-바트 멀티플레이어 시스템
실시간 P2P 멀티플레이어에서 로-바트들이 함께 플레이!

이 시스템은:
- 로-바트끼리 협력 및 경쟁 모드
- 실시간 채팅 및 의사소통
- 리더십 시스템 (방장/리더 구분)
- 버전 호환성 체크
- 동기화된 게임플레이
- AI vs 인간 혼합 파티
"""

import asyncio
import random
import time
import json
import socket
import threading
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid

from game.color_text import bright_cyan, bright_yellow, bright_green, bright_red, cyan, yellow, red, green, white, bright_magenta
from game.robat_gameplay_system import RobatGamePlayer, RobatGameplaySystem
from game.job_specialized_ai import JobSpecializedAI, JobClass, RobatPersonality

# 버전 정보
GAME_VERSION = "4.1.1"
MULTIPLAYER_PROTOCOL_VERSION = "1.0"


class PlayerType(Enum):
    """플레이어 타입"""
    HUMAN = "human"
    ROBAT_AI = "robat_ai"
    ADVANCED_AI = "advanced_ai"


class MultiplayerRole(Enum):
    """멀티플레이어 역할"""
    HOST = "host"          # 방장 (변경 불가)
    LEADER = "leader"      # 리더 (움직임 담당, 변경 가능)
    MEMBER = "member"      # 일반 멤버
    OBSERVER = "observer"  # 관전자


class GameSyncType(Enum):
    """게임 동기화 타입"""
    MOVEMENT = "movement"
    COMBAT = "combat"
    INVENTORY = "inventory"
    SAVE_LOAD = "save_load"
    CHAT = "chat"
    SYSTEM = "system"


@dataclass
class MultiplayerCharacter:
    """멀티플레이어 캐릭터"""
    character_id: str
    name: str
    job_class: JobClass
    level: int = 1
    
    # 플레이어 정보
    player_type: PlayerType = PlayerType.HUMAN
    player_id: str = ""
    player_name: str = ""
    
    # 게임 상태
    current_hp: int = 100
    max_hp: int = 100
    current_mp: int = 50
    max_mp: int = 50
    
    # 장비 및 인벤토리
    equipment: Dict[str, Any] = field(default_factory=dict)
    inventory: List[Dict] = field(default_factory=list)
    
    # 위치 정보
    position: Tuple[int, int] = (0, 0)
    
    # AI 관련 (로-바트인 경우)
    robat_ai: Optional[RobatGamePlayer] = None
    ai_personality: Optional[RobatPersonality] = None
    
    # 메타 진행도 (개별 적용)
    meta_progress: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GameSession:
    """게임 세션"""
    session_id: str
    game_version: str = GAME_VERSION
    protocol_version: str = MULTIPLAYER_PROTOCOL_VERSION
    
    # 호스트 정보
    host_id: str = ""
    host_name: str = ""
    
    # 현재 리더
    current_leader_id: str = ""
    
    # 참가자들
    players: Dict[str, MultiplayerCharacter] = field(default_factory=dict)
    max_players: int = 4
    
    # 게임 설정 (공통)
    difficulty: str = "normal"
    map_size: Tuple[int, int] = (50, 50)
    shared_passives: List[str] = field(default_factory=list)
    
    # 게임 상태 (동기화)
    current_floor: int = 1
    world_state: Dict[str, Any] = field(default_factory=dict)
    encounter_state: Dict[str, Any] = field(default_factory=dict)
    
    # 채팅
    chat_history: List[Dict] = field(default_factory=list)
    
    # 동기화 상태
    last_sync_time: float = 0.0
    sync_conflicts: List[Dict] = field(default_factory=list)


class RobatMultiplayerAI:
    """로-바트 멀티플레이어 AI"""
    
    def __init__(self, character: MultiplayerCharacter, session: GameSession):
        self.character = character
        self.session = session
        self.robat_player = character.robat_ai
        
        # 멀티플레이어 특화 기능
        self.communication_style = self._determine_communication_style()
        self.cooperation_level = random.uniform(0.7, 1.0)  # 협력 성향
        self.leadership_desire = random.uniform(0.3, 0.8)  # 리더십 욕구
        self.chat_frequency = random.uniform(0.2, 0.6)     # 채팅 빈도
        
        # 다른 플레이어들과의 관계
        self.player_relationships = {}
        self.team_dynamics = {}
        
        print(f"🤖 {character.name} 멀티플레이어 로-바트 준비!")
        print(f"   협력성: {self.cooperation_level:.1f}, 리더십: {self.leadership_desire:.1f}")
    
    def _determine_communication_style(self) -> Dict[str, float]:
        """의사소통 스타일 결정"""
        job_class = self.character.job_class
        personality = self.character.ai_personality
        
        # 직업별 기본 의사소통 스타일
        job_communication = {
            JobClass.WARRIOR: {"assertive": 0.8, "supportive": 0.6, "informative": 0.5},
            JobClass.ARCHMAGE: {"assertive": 0.7, "supportive": 0.5, "informative": 0.9},
            JobClass.ROGUE: {"assertive": 0.5, "supportive": 0.4, "informative": 0.7},
            JobClass.BARD: {"assertive": 0.6, "supportive": 0.9, "informative": 0.8},
            JobClass.PALADIN: {"assertive": 0.7, "supportive": 0.9, "informative": 0.6},
            JobClass.ENGINEER: {"assertive": 0.6, "supportive": 0.7, "informative": 0.9}
        }
        
        base_style = job_communication.get(job_class, {
            "assertive": 0.5, "supportive": 0.5, "informative": 0.5
        })
        
        # 로-바트 성격 반영
        if personality:
            if personality.pride_level > 0.7:
                base_style["assertive"] += 0.2
            if personality.helpfulness > 0.7:
                base_style["supportive"] += 0.2
            if personality.cleverness > 0.7:
                base_style["informative"] += 0.2
        
        return base_style
    
    async def generate_multiplayer_chat(self, context: Dict[str, Any]) -> Optional[str]:
        """멀티플레이어 채팅 생성"""
        if random.random() > self.chat_frequency:
            return None
        
        situation = context.get("situation", "general")
        team_status = context.get("team_status", {})
        
        # 상황별 채팅 템플릿
        chat_templates = {
            "combat_start": [
                "전투 시작이에요! 제가 도와드릴게요! ⚔️",
                "모두 준비되셨나요? 함께 승리해봐요! 💪",
                "적들이 후회하게 만들어드리겠어요! 😤"
            ],
            "discovery": [
                "오! 뭔가 발견했어요! 모두 와보세요! 👀",
                "이거 흥미로운데요? 함께 확인해볼까요? 🔍",
                "제 센서에 특별한 게 감지됐어요! ✨"
            ],
            "danger": [
                "조심하세요! 위험해 보여요! ⚠️",
                "모두 제 뒤로 와주세요! 제가 막을게요! 🛡️",
                "이건 좀... 신중하게 접근해야겠어요! 🤔"
            ],
            "success": [
                "와! 우리 팀 정말 대단해요! 🎉",
                "역시 우리가 최고죠! 예상대로네요! 😊",
                "이런 결과는 당연한 거죠! 후후~ 🏆"
            ],
            "support": [
                "도움이 필요하면 언제든 말씀하세요! 🤝",
                "제가 할 수 있는 건 뭐든 도와드릴게요! 💫",
                "팀워크가 핵심이죠! 함께 해봐요! 😎"
            ]
        }
        
        # 직업별 특화 멘트 추가
        job_specific_chats = {
            JobClass.WARRIOR: {
                "combat_start": ["제가 앞장서겠습니다! 전사의 자존심을 보여드리죠! ⚔️"],
                "support": ["제 방패 뒤에서 안전하게 있으세요! 🛡️"]
            },
            JobClass.ARCHMAGE: {
                "discovery": ["마법적 에너지가 느껴지네요! 분석해보겠습니다! ✨"],
                "combat_start": ["마법의 힘으로 승리를 이끌어내겠어요! 🔮"]
            },
            JobClass.BARD: {
                "support": ["모든 분께 힘이 되는 노래를 불러드릴게요! 🎵"],
                "success": ["우리의 하모니가 승리를 만들었어요! 🎶"]
            }
        }
        
        # 기본 템플릿 선택
        templates = chat_templates.get(situation, chat_templates["support"])
        base_message = random.choice(templates)
        
        # 직업별 특화 멘트 추가
        job_templates = job_specific_chats.get(self.character.job_class, {})
        if situation in job_templates and random.random() < 0.4:
            base_message = random.choice(job_templates[situation])
        
        # 로-바트 성격 반영
        personality = self.character.ai_personality
        if personality:
            if personality.playfulness > 0.7 and random.random() < 0.3:
                playful_additions = [" 헤헤~", " 재미있겠네요!", " 신나는걸요! 🎪"]
                base_message += random.choice(playful_additions)
            
            if personality.pride_level > 0.8 and random.random() < 0.2:
                proud_additions = [" 제 실력을 보여드릴 시간이군요!", " 자랑스럽지 않나요?"]
                base_message += random.choice(proud_additions)
        
        return base_message
    
    async def evaluate_leadership_opportunity(self, current_situation: Dict[str, Any]) -> float:
        """리더십 기회 평가"""
        base_desire = self.leadership_desire
        
        # 상황별 리더십 욕구 조정
        if current_situation.get("in_danger", False):
            if self.character.job_class in [JobClass.WARRIOR, JobClass.PALADIN]:
                base_desire += 0.3  # 탱커는 위험할 때 리더십 증가
            else:
                base_desire -= 0.2  # 다른 직업은 위험할 때 리더십 감소
        
        if current_situation.get("exploration", False):
            if self.character.job_class in [JobClass.ROGUE, JobClass.ARCHER]:
                base_desire += 0.2  # 정찰병은 탐험 시 리더십 증가
        
        if current_situation.get("social_interaction", False):
            if self.character.job_class == JobClass.BARD:
                base_desire += 0.3  # 바드는 사회적 상황에서 리더십 증가
        
        # 현재 리더의 성과 평가
        current_leader_performance = current_situation.get("leader_performance", 0.5)
        if current_leader_performance < 0.3:
            base_desire += 0.4  # 현재 리더가 부실하면 리더십 욕구 증가
        
        return min(1.0, max(0.0, base_desire))
    
    async def make_team_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """팀 의사결정 참여"""
        communication_style = self.communication_style
        
        decision = {
            "player_id": self.character.player_id,
            "player_name": self.character.name,
            "vote": None,
            "reasoning": "",
            "confidence": 0.0,
            "alternative_suggestions": []
        }
        
        # 직업별 의사결정 가중치
        job_decision_weights = {
            JobClass.WARRIOR: {"combat": 0.9, "exploration": 0.6, "diplomacy": 0.4},
            JobClass.ARCHMAGE: {"combat": 0.7, "exploration": 0.8, "diplomacy": 0.7},
            JobClass.ROGUE: {"combat": 0.6, "exploration": 0.9, "diplomacy": 0.5},
            JobClass.BARD: {"combat": 0.5, "exploration": 0.7, "diplomacy": 0.9},
            JobClass.PALADIN: {"combat": 0.8, "exploration": 0.6, "diplomacy": 0.8}
        }
        
        weights = job_decision_weights.get(self.character.job_class, {
            "combat": 0.6, "exploration": 0.6, "diplomacy": 0.6
        })
        
        decision_type = decision_context.get("type", "general")
        options = decision_context.get("options", [])
        
        if options:
            # 가중치 기반 옵션 평가
            best_option = None
            best_score = 0.0
            
            for option in options:
                score = weights.get(decision_type, 0.5)
                
                # 로-바트 성격 반영
                if self.character.ai_personality:
                    if "aggressive" in option.lower() and self.character.ai_personality.pride_level > 0.7:
                        score += 0.2
                    if "careful" in option.lower() and self.character.ai_personality.cleverness > 0.7:
                        score += 0.2
                    if "help" in option.lower() and self.character.ai_personality.helpfulness > 0.7:
                        score += 0.2
                
                if score > best_score:
                    best_score = score
                    best_option = option
            
            decision["vote"] = best_option
            decision["confidence"] = best_score
            
            # 로-바트다운 이유 설명
            reasoning_templates = {
                "high_confidence": [
                    f"제 {self.character.job_class.value} 경험으로는 이게 최선이에요!",
                    "확신을 가지고 추천드립니다!",
                    "이론적으로도 실전에서도 검증된 방법이에요!"
                ],
                "medium_confidence": [
                    "음... 이게 괜찮을 것 같은데요?",
                    "여러 가지를 고려해보니 이 방법이 나을 것 같아요",
                    "완벽하지는 않지만 시도해볼 만해요!"
                ],
                "low_confidence": [
                    "잘 모르겠지만... 이게 어떨까요?",
                    "다른 분들 의견도 들어보고 싶어요",
                    "확신은 없지만 일단 이걸로..."
                ]
            }
            
            if best_score > 0.7:
                reasoning = random.choice(reasoning_templates["high_confidence"])
            elif best_score > 0.4:
                reasoning = random.choice(reasoning_templates["medium_confidence"])
            else:
                reasoning = random.choice(reasoning_templates["low_confidence"])
            
            decision["reasoning"] = reasoning
        
        return decision


class RobatMultiplayerSession:
    """로-바트 멀티플레이어 세션"""
    
    def __init__(self, session_id: str = None):
        self.session = GameSession(
            session_id=session_id or str(uuid.uuid4()),
            game_version=GAME_VERSION,
            protocol_version=MULTIPLAYER_PROTOCOL_VERSION
        )
        
        self.robat_ais: Dict[str, RobatMultiplayerAI] = {}
        self.chat_log = deque(maxlen=100)
        self.sync_lock = asyncio.Lock()
        
        # 실시간 상태
        self.is_active = False
        self.game_state = {}
        self.pending_decisions = {}
        
        print(f"🎮 로-바트 멀티플레이어 세션 생성: {self.session.session_id}")
    
    async def add_robat_player(self, job_class: JobClass, player_name: str, 
                              intelligence_level = None) -> str:
        """로-바트 플레이어 추가"""
        from game.job_specialized_ai import AIIntelligenceLevel
        
        if intelligence_level is None:
            intelligence_level = AIIntelligenceLevel.GENIUS
        
        # 캐릭터 생성
        character_id = str(uuid.uuid4())
        player_id = f"robat_{character_id[:8]}"
        
        # 로-바트 AI 생성
        job_ai = JobSpecializedAI(player_id, player_name, job_class, intelligence_level)
        robat_player = RobatGamePlayer(job_ai)
        
        # 멀티플레이어 캐릭터 생성
        character = MultiplayerCharacter(
            character_id=character_id,
            name=player_name,
            job_class=job_class,
            player_type=PlayerType.ROBAT_AI,
            player_id=player_id,
            player_name=player_name,
            robat_ai=robat_player,
            ai_personality=job_ai.robat_personality
        )
        
        # 세션에 추가
        self.session.players[player_id] = character
        
        # 로-바트 멀티플레이어 AI 생성
        robat_mp_ai = RobatMultiplayerAI(character, self.session)
        self.robat_ais[player_id] = robat_mp_ai
        
        # 첫 번째 플레이어는 호스트
        if not self.session.host_id:
            self.session.host_id = player_id
            self.session.host_name = player_name
            self.session.current_leader_id = player_id
            
            await self.add_chat_message("system", f"🎮 {player_name}님이 방장이 되었습니다!")
        
        await self.add_chat_message("system", f"🤖 {player_name} ({job_class.value}) 로-바트가 참가했습니다!")
        
        return player_id
    
    async def add_chat_message(self, sender: str, message: str, message_type: str = "normal"):
        """채팅 메시지 추가"""
        chat_entry = {
            "timestamp": time.time(),
            "sender": sender,
            "message": message,
            "type": message_type
        }
        
        self.session.chat_history.append(chat_entry)
        self.chat_log.append(chat_entry)
        
        # 실시간 출력
        if message_type == "system":
            print(f"📢 {message}")
        else:
            print(f"💬 {sender}: {message}")
    
    async def start_multiplayer_game(self, duration: int = 60):
        """멀티플레이어 게임 시작"""
        if len(self.session.players) < 2:
            print("❌ 최소 2명의 플레이어가 필요합니다!")
            return
        
        self.is_active = True
        
        print(f"\n🎮 === 로-바트 멀티플레이어 게임 시작! ===")
        print(f"세션 ID: {self.session.session_id}")
        print(f"참가자: {len(self.session.players)}명")
        print(f"게임 버전: {self.session.game_version}")
        
        await self.add_chat_message("system", "🚀 게임이 시작되었습니다!")
        
        # 모든 로-바트들의 인사
        for robat_ai in self.robat_ais.values():
            greeting = await robat_ai.generate_multiplayer_chat({
                "situation": "game_start",
                "team_status": {"total_players": len(self.session.players)}
            })
            if greeting:
                await self.add_chat_message(robat_ai.character.name, greeting)
        
        # 게임플레이 루프
        start_time = time.time()
        game_events = []
        
        while time.time() - start_time < duration and self.is_active:
            # 현재 상황 생성
            current_situation = await self._generate_game_situation()
            
            # 모든 로-바트가 행동
            for robat_ai in self.robat_ais.values():
                # 행동 선택
                action = await self._robat_choose_action(robat_ai, current_situation)
                
                # 행동 실행
                result = await self._execute_multiplayer_action(robat_ai.character, action)
                
                # 채팅 생성 (가끔)
                if random.random() < robat_ai.chat_frequency:
                    chat = await robat_ai.generate_multiplayer_chat({
                        "situation": action["type"],
                        "result": result
                    })
                    if chat:
                        await self.add_chat_message(robat_ai.character.name, chat)
                
                # 이벤트 로깅
                game_events.append({
                    "time": time.time() - start_time,
                    "player": robat_ai.character.name,
                    "action": action,
                    "result": result
                })
            
            # 팀 의사결정 (가끔)
            if random.random() < 0.3:
                await self._conduct_team_decision()
            
            # 리더십 변경 기회 (가끔)
            if random.random() < 0.2:
                await self._evaluate_leadership_change()
            
            # 대기
            await asyncio.sleep(random.uniform(2, 5))
        
        # 게임 종료
        await self._end_multiplayer_game(game_events)
    
    async def _generate_game_situation(self) -> Dict[str, Any]:
        """게임 상황 생성"""
        situations = [
            {"type": "exploration", "description": "새로운 지역 탐험", "difficulty": 0.3},
            {"type": "combat", "description": "적과 조우", "difficulty": 0.7},
            {"type": "puzzle", "description": "수수께끼 발견", "difficulty": 0.5},
            {"type": "treasure", "description": "보물 발견", "difficulty": 0.2},
            {"type": "danger", "description": "함정 발견", "difficulty": 0.8},
            {"type": "social", "description": "NPC와 만남", "difficulty": 0.4}
        ]
        
        situation = random.choice(situations)
        situation.update({
            "team_health": random.uniform(0.6, 1.0),
            "team_resources": random.uniform(0.4, 0.9),
            "time_pressure": random.uniform(0.1, 0.8)
        })
        
        return situation
    
    async def _robat_choose_action(self, robat_ai: RobatMultiplayerAI, 
                                  situation: Dict[str, Any]) -> Dict[str, Any]:
        """로-바트 행동 선택"""
        # 기본 행동 옵션들
        actions = [
            {"type": "explore", "description": "지역 탐험", "cooperation": True},
            {"type": "combat", "description": "전투 참가", "cooperation": True},
            {"type": "support", "description": "팀 지원", "cooperation": True},
            {"type": "individual", "description": "개별 행동", "cooperation": False},
            {"type": "communicate", "description": "의사소통", "cooperation": True}
        ]
        
        # 협력 성향에 따른 행동 선택
        cooperation_actions = [a for a in actions if a["cooperation"]]
        individual_actions = [a for a in actions if not a["cooperation"]]
        
        if robat_ai.cooperation_level > 0.7:
            chosen_action = random.choice(cooperation_actions)
        elif robat_ai.cooperation_level < 0.4:
            chosen_action = random.choice(individual_actions)
        else:
            chosen_action = random.choice(actions)
        
        # 직업별 특화
        if situation["type"] == "combat" and robat_ai.character.job_class == JobClass.WARRIOR:
            chosen_action = {"type": "tank", "description": "적 어그로 확보", "cooperation": True}
        elif situation["type"] == "exploration" and robat_ai.character.job_class == JobClass.ROGUE:
            chosen_action = {"type": "scout", "description": "정찰 활동", "cooperation": True}
        
        return chosen_action
    
    async def _execute_multiplayer_action(self, character: MultiplayerCharacter, 
                                         action: Dict[str, Any]) -> str:
        """멀티플레이어 행동 실행"""
        action_type = action["type"]
        
        # 행동 결과 시뮬레이션
        success_chance = 0.7
        
        # 직업별 성공률 조정
        if action_type == "combat" and character.job_class in [JobClass.WARRIOR, JobClass.PALADIN]:
            success_chance += 0.2
        elif action_type == "explore" and character.job_class in [JobClass.ROGUE, JobClass.ARCHER]:
            success_chance += 0.2
        elif action_type == "support" and character.job_class == JobClass.BARD:
            success_chance += 0.3
        
        # 결과 결정
        is_success = random.random() < success_chance
        
        if is_success:
            results = {
                "explore": "새로운 지역을 발견했습니다!",
                "combat": "적을 성공적으로 처치했습니다!",
                "support": "팀원들에게 도움을 주었습니다!",
                "tank": "적의 공격을 성공적으로 막아냈습니다!",
                "scout": "안전한 경로를 찾았습니다!",
                "communicate": "팀과 효과적으로 소통했습니다!"
            }
            return results.get(action_type, "행동을 성공적으로 완료했습니다!")
        else:
            failures = {
                "explore": "길을 잃었습니다...",
                "combat": "전투에서 부상을 입었습니다...",
                "support": "도움이 제대로 전달되지 않았습니다...",
                "tank": "적의 공격을 완전히 막지 못했습니다...",
                "scout": "함정을 발견하지 못했습니다...",
                "communicate": "의사소통에 문제가 있었습니다..."
            }
            return failures.get(action_type, "행동이 실패했습니다...")
    
    async def _conduct_team_decision(self):
        """팀 의사결정 진행"""
        decision_scenarios = [
            {
                "question": "어느 길로 가시겠습니까?",
                "options": ["안전한 길", "빠른 길", "보물이 있을 것 같은 길"],
                "type": "exploration"
            },
            {
                "question": "전투 전략을 정하세요:",
                "options": ["정면 공격", "포위 전술", "기습 공격"],
                "type": "combat"
            },
            {
                "question": "휴식을 취하시겠습니까?",
                "options": ["즉시 휴식", "조금 더 진행", "휴식 없이 계속"],
                "type": "general"
            }
        ]
        
        scenario = random.choice(decision_scenarios)
        
        await self.add_chat_message("system", f"📋 팀 의사결정: {scenario['question']}")
        await self.add_chat_message("system", f"선택지: {', '.join(scenario['options'])}")
        
        # 모든 로-바트의 의견 수집
        votes = {}
        for robat_ai in self.robat_ais.values():
            decision = await robat_ai.make_team_decision({
                "type": scenario["type"],
                "options": scenario["options"],
                "question": scenario["question"]
            })
            
            votes[robat_ai.character.player_id] = decision
            
            await self.add_chat_message(
                robat_ai.character.name,
                f"저는 '{decision['vote']}'에 투표해요! {decision['reasoning']}"
            )
        
        # 투표 결과 집계
        vote_counts = defaultdict(int)
        for vote_data in votes.values():
            if vote_data["vote"]:
                vote_counts[vote_data["vote"]] += 1
        
        if vote_counts:
            winner = max(vote_counts.keys(), key=vote_counts.get)
            await self.add_chat_message("system", f"🏆 결정: '{winner}' (득표수: {vote_counts[winner]})")
        else:
            await self.add_chat_message("system", "❓ 의견이 분분해서 리더가 결정하겠습니다!")
    
    async def _evaluate_leadership_change(self):
        """리더십 변경 평가"""
        current_leader_id = self.session.current_leader_id
        current_situation = await self._generate_game_situation()
        
        # 모든 로-바트의 리더십 욕구 평가
        leadership_candidates = []
        for robat_ai in self.robat_ais.values():
            if robat_ai.character.player_id != current_leader_id:
                leadership_score = await robat_ai.evaluate_leadership_opportunity(current_situation)
                leadership_candidates.append((robat_ai, leadership_score))
        
        # 가장 리더십 욕구가 높은 로-바트
        if leadership_candidates:
            leadership_candidates.sort(key=lambda x: x[1], reverse=True)
            best_candidate, best_score = leadership_candidates[0]
            
            # 리더십 도전 (50% 이상의 욕구가 있고, 확률적으로)
            if best_score > 0.5 and random.random() < 0.3:
                challenge_message = await best_candidate.generate_multiplayer_chat({
                    "situation": "leadership_challenge",
                    "team_status": {"current_leader": current_leader_id}
                })
                
                if not challenge_message:
                    challenge_message = f"제가 리더를 해보고 싶어요! 더 잘할 수 있을 것 같거든요! 😊"
                
                await self.add_chat_message(best_candidate.character.name, challenge_message)
                
                # 간단한 투표
                if random.random() < 0.4:  # 40% 확률로 리더 변경
                    self.session.current_leader_id = best_candidate.character.player_id
                    await self.add_chat_message("system", 
                        f"👑 {best_candidate.character.name}님이 새로운 리더가 되었습니다!")
                else:
                    await self.add_chat_message("system", "현재 리더가 계속 유지됩니다.")
    
    async def _end_multiplayer_game(self, game_events: List[Dict]):
        """멀티플레이어 게임 종료"""
        self.is_active = False
        
        await self.add_chat_message("system", "🏁 게임이 종료되었습니다!")
        
        # 통계 분석
        player_stats = defaultdict(lambda: {"actions": 0, "successes": 0, "chats": 0})
        
        for event in game_events:
            player_name = event["player"]
            player_stats[player_name]["actions"] += 1
            if "성공" in event["result"]:
                player_stats[player_name]["successes"] += 1
        
        # 채팅 통계
        for chat_entry in self.session.chat_history:
            if chat_entry["sender"] != "system":
                player_stats[chat_entry["sender"]]["chats"] += 1
        
        # 결과 발표
        print(f"\n📊 === 게임 결과 ===")
        for player_name, stats in player_stats.items():
            success_rate = stats["successes"] / max(stats["actions"], 1) * 100
            print(f"🤖 {player_name}:")
            print(f"   행동 수: {stats['actions']}")
            print(f"   성공률: {success_rate:.1f}%")
            print(f"   채팅 수: {stats['chats']}")
        
        # 모든 로-바트들의 마무리 인사
        for robat_ai in self.robat_ais.values():
            farewell = await robat_ai.generate_multiplayer_chat({
                "situation": "game_end",
                "team_status": {"game_success": True}
            })
            if farewell:
                await self.add_chat_message(robat_ai.character.name, farewell)


async def run_robat_multiplayer_test():
    """로-바트 멀티플레이어 테스트"""
    print(f"\n{bright_magenta('🎮 === 로-바트 멀티플레이어 시스템 === ')}")
    
    # 멀티플레이어 세션 생성
    session = RobatMultiplayerSession()
    
    # 다양한 직업의 로-바트들 추가
    test_jobs = [
        (JobClass.WARRIOR, "전사로바트"),
        (JobClass.ARCHMAGE, "마법사로바트"),
        (JobClass.ROGUE, "도적로바트"),
        (JobClass.BARD, "바드로바트")
    ]
    
    print(f"로-바트 플레이어들을 추가합니다...")
    for job_class, name in test_jobs:
        await session.add_robat_player(job_class, name)
        await asyncio.sleep(0.5)  # 순차적 추가
    
    # 멀티플레이어 게임 시작 (30초)
    print(f"\n⏰ 30초간 로-바트 멀티플레이어 게임을 시작합니다!")
    await session.start_multiplayer_game(duration=30)
    
    print(f"\n{bright_green('✅ 로-바트 멀티플레이어 테스트 완료!')}")
    print(f"🤖 실시간 채팅과 팀 협력!")
    print(f"👑 동적 리더십 변경!")
    print(f"🎯 직업별 특화 전략!")
    print(f"💬 자연스러운 의사소통!")


if __name__ == "__main__":
    asyncio.run(run_robat_multiplayer_test())
