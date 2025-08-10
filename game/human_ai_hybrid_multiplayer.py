"""
👥 Dawn of Stellar - 인간 + 로-바트 혼합 멀티플레이어 시스템
인간의 창의성 + AI의 효율성 = 최강의 조합!

2025년 8월 10일 - 혁신적 혼합 플레이 시스템
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
import random

# 기존 시스템들 import
try:
    from game.robat_multiplayer import PlayerType, MultiplayerRole, RobatMultiplayerSession
    from game.ultimate_ai_learning_system import UltimateAILearningSystem, AILearningType
except ImportError:
    # Mock classes for demo
    class PlayerType(Enum):
        HUMAN = "human"
        ROBAT_AI = "robat_ai"
        ADVANCED_AI = "advanced_ai"
    
    class MultiplayerRole(Enum):
        HOST = "host"
        LEADER = "leader"
        MEMBER = "member"

class HybridPlayMode(Enum):
    """혼합 플레이 모드"""
    COOPERATIVE = "협력모드"        # 인간이 지휘, AI가 실행
    COMPETITIVE = "경쟁모드"       # 인간 vs AI 팀 대결
    TEACHING = "교육모드"          # 인간이 AI에게 가르치기
    LEARNING = "학습모드"          # AI가 인간을 관찰하고 학습
    FUSION = "융합모드"            # 인간과 AI가 완전히 협력

class CommunicationStyle(Enum):
    """의사소통 스타일"""
    FORMAL = "정중한말투"          # "말씀하신 대로 하겠습니다"
    CASUAL = "친근한말투"          # "오케이! 바로 할게!"
    PROFESSIONAL = "전문가말투"    # "전술적으로 분석하면..."
    CUTE = "귀여운말투"            # "네네~ 알겠어요!"
    ROBOTIC = "로봇말투"           # "명령을 수행합니다"

@dataclass
class HumanPlayerProfile:
    """인간 플레이어 프로필"""
    name: str
    preferred_play_style: str
    skill_level: float  # 0.0 ~ 1.0
    favorite_strategies: List[str]
    ai_trust_level: float  # AI를 얼마나 신뢰하는가
    teaching_preference: str
    communication_style: CommunicationStyle

@dataclass
class AIPersonality:
    """AI 개성"""
    name: str
    communication_style: CommunicationStyle
    learning_enthusiasm: float  # 학습 열정도
    independence_level: float   # 독립성 수준
    creativity_factor: float    # 창의성 계수
    loyalty_to_human: float     # 인간에 대한 충성도
    specialization: str         # 전문 분야

class HumanAIHybridSession:
    """인간-AI 혼합 세션"""
    
    def __init__(self):
        self.session_id = f"hybrid_{int(time.time())}"
        self.humans: Dict[str, HumanPlayerProfile] = {}
        self.ais: Dict[str, AIPersonality] = {}
        self.play_mode = HybridPlayMode.COOPERATIVE
        self.communication_log: List[Dict] = []
        self.learning_system = UltimateAILearningSystem()
        
        print("👥 인간-AI 혼합 세션 생성!")
        print(f"   세션 ID: {self.session_id}")
    
    def add_human_player(self, name: str, skill_level: float = 0.5, 
                        communication_style: CommunicationStyle = CommunicationStyle.CASUAL):
        """인간 플레이어 추가"""
        profile = HumanPlayerProfile(
            name=name,
            preferred_play_style="균형잡힌",
            skill_level=skill_level,
            favorite_strategies=["신중한 탐험", "팀워크 중시"],
            ai_trust_level=0.7,
            teaching_preference="실전 위주",
            communication_style=communication_style
        )
        
        self.humans[name] = profile
        print(f"👤 인간 플레이어 '{name}' 참가!")
        print(f"   실력 수준: {skill_level * 100:.0f}%")
        print(f"   의사소통: {communication_style.value}")
    
    def add_ai_partner(self, name: str, job_class: str, 
                      communication_style: CommunicationStyle = CommunicationStyle.PROFESSIONAL):
        """AI 파트너 추가"""
        personality = AIPersonality(
            name=name,
            communication_style=communication_style,
            learning_enthusiasm=random.uniform(0.7, 1.0),
            independence_level=random.uniform(0.4, 0.8),
            creativity_factor=random.uniform(0.5, 0.9),
            loyalty_to_human=random.uniform(0.8, 1.0),
            specialization=job_class
        )
        
        self.ais[name] = personality
        
        # 학습 AI도 생성
        self.learning_system.create_learning_ai(
            name, job_class, 
            [AILearningType.OBSERVATION, AILearningType.EXPERIENCE]
        )
        
        print(f"🤖 AI 파트너 '{name}' 참가!")
        print(f"   전문분야: {job_class}")
        print(f"   의사소통: {communication_style.value}")
        print(f"   학습열정: {personality.learning_enthusiasm:.0%}")
    
    def set_play_mode(self, mode: HybridPlayMode):
        """플레이 모드 설정"""
        self.play_mode = mode
        print(f"🎮 플레이 모드: {mode.value}")
        
        if mode == HybridPlayMode.COOPERATIVE:
            print("   👥 협력 모드: 인간이 전략을 세우고 AI가 실행합니다")
        elif mode == HybridPlayMode.TEACHING:
            print("   📚 교육 모드: 인간이 AI에게 플레이 방법을 가르칩니다")
        elif mode == HybridPlayMode.LEARNING:
            print("   🧠 학습 모드: AI가 인간의 플레이를 관찰하고 학습합니다")
        elif mode == HybridPlayMode.FUSION:
            print("   ✨ 융합 모드: 인간과 AI가 완전히 하나가 되어 플레이합니다")
    
    def simulate_hybrid_gameplay(self, duration_minutes: int = 5):
        """혼합 플레이 시뮬레이션"""
        print(f"🎮 === {self.play_mode.value} 시뮬레이션 시작! ===")
        print(f"   ⏰ 시간: {duration_minutes}분")
        print()
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        action_count = 0
        while time.time() < end_time:
            action_count += 1
            
            # 다양한 상호작용 시뮬레이션
            self._simulate_interaction(action_count)
            
            time.sleep(2)  # 2초마다 한 번의 상호작용
        
        print(f"✅ 시뮬레이션 완료! 총 {action_count}번의 상호작용")
        self._generate_session_summary()
    
    def _simulate_interaction(self, action_id: int):
        """상호작용 시뮬레이션"""
        # 랜덤하게 인간이나 AI가 행동
        if random.random() < 0.6:  # 60% 확률로 인간이 행동
            self._simulate_human_action(action_id)
        else:  # 40% 확률로 AI가 행동
            self._simulate_ai_action(action_id)
    
    def _simulate_human_action(self, action_id: int):
        """인간 행동 시뮬레이션"""
        if not self.humans:
            return
        
        human_name = random.choice(list(self.humans.keys()))
        human = self.humans[human_name]
        
        actions = [
            "새로운 지역 탐험 제안",
            "전투 전략 수정",
            "아이템 사용 지시",
            "팀 포지션 변경",
            "위험 지역 회피 명령"
        ]
        
        action = random.choice(actions)
        
        print(f"👤 {human_name}: \"{action}\"")
        
        # AI들의 반응
        self._ai_respond_to_human(human_name, action)
        
        # 학습 데이터로 기록
        self._record_interaction("human_action", {
            "player": human_name,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
    
    def _simulate_ai_action(self, action_id: int):
        """AI 행동 시뮬레이션"""
        if not self.ais:
            return
        
        ai_name = random.choice(list(self.ais.keys()))
        ai = self.ais[ai_name]
        
        # AI 개성에 따른 행동
        if ai.communication_style == CommunicationStyle.PROFESSIONAL:
            messages = [
                "전술적 분석 결과, 북쪽 경로가 최적입니다",
                "현재 파티 구성으로는 마법 공격이 유리합니다",
                "적의 패턴을 분석한 결과 약점을 발견했습니다"
            ]
        elif ai.communication_style == CommunicationStyle.CUTE:
            messages = [
                "여기 숨겨진 보물이 있는 것 같아요~!",
                "조심해요! 함정이 있을지도 몰라요!",
                "우와~ 이 스킬 조합 정말 멋져요!"
            ]
        elif ai.communication_style == CommunicationStyle.CASUAL:
            messages = [
                "오케이! 바로 실행할게!",
                "이쪽으로 가면 어떨까?",
                "좋은 아이디어네! 해보자!"
            ]
        else:
            messages = [
                "명령을 수행하겠습니다",
                "최적의 경로를 계산했습니다",
                "데이터 분석 완료했습니다"
            ]
        
        message = random.choice(messages)
        print(f"🤖 {ai_name}: \"{message}\"")
        
        # 학습 시뮬레이션
        if random.random() < 0.3:  # 30% 확률로 새로운 것 학습
            learning_discovery = [
                "새로운 전투 패턴 발견",
                "효율적인 아이템 조합 학습",
                "최적화된 이동 경로 개발"
            ]
            discovery = random.choice(learning_discovery)
            print(f"   💡 {ai_name}이 {discovery}!")
        
        self._record_interaction("ai_action", {
            "ai": ai_name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _ai_respond_to_human(self, human_name: str, human_action: str):
        """AI가 인간 행동에 반응"""
        for ai_name, ai in self.ais.items():
            if random.random() < 0.4:  # 40% 확률로 반응
                if ai.communication_style == CommunicationStyle.FORMAL:
                    response = f"말씀하신 '{human_action}' 즉시 수행하겠습니다!"
                elif ai.communication_style == CommunicationStyle.CUTE:
                    response = f"네네~ '{human_action}' 할게요!"
                else:
                    response = f"알겠습니다. '{human_action}' 진행하겠습니다."
                
                print(f"   🤖 {ai_name}: \"{response}\"")
    
    def _record_interaction(self, interaction_type: str, data: Dict):
        """상호작용 기록"""
        self.communication_log.append({
            "type": interaction_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_session_summary(self):
        """세션 요약 생성"""
        print()
        print("📊 === 세션 요약 ===")
        
        human_actions = len([log for log in self.communication_log if log["type"] == "human_action"])
        ai_actions = len([log for log in self.communication_log if log["type"] == "ai_action"])
        
        print(f"👤 인간 행동: {human_actions}회")
        print(f"🤖 AI 행동: {ai_actions}회")
        print(f"💬 총 상호작용: {len(self.communication_log)}회")
        
        # 협력 점수 계산
        cooperation_score = min((human_actions + ai_actions) / 20.0, 1.0)
        print(f"🤝 협력 점수: {cooperation_score:.0%}")
        
        # AI 학습 효과
        learning_effect = random.uniform(0.1, 0.3)
        print(f"🧠 AI 학습 효과: +{learning_effect:.0%}")
        
        print()
        print("✨ 세션 완료! 인간과 AI의 완벽한 협력이었습니다!")

class AdvancedMixedMultiplayer:
    """고급 혼합 멀티플레이어 시스템"""
    
    def __init__(self):
        self.sessions: Dict[str, HumanAIHybridSession] = {}
        self.global_learning_data = {}
        
    def create_mixed_session(self, session_name: str) -> HumanAIHybridSession:
        """혼합 세션 생성"""
        session = HumanAIHybridSession()
        self.sessions[session_name] = session
        return session
    
    def create_balanced_party(self, human_count: int = 1, ai_count: int = 3):
        """균형잡힌 파티 생성"""
        session = HumanAIHybridSession()
        
        # 인간 플레이어 추가
        for i in range(human_count):
            human_name = f"플레이어{i+1}"
            session.add_human_player(
                human_name, 
                skill_level=random.uniform(0.4, 0.9),
                communication_style=random.choice(list(CommunicationStyle))
            )
        
        # AI 파트너 추가
        ai_jobs = ["전사", "아크메이지", "도적", "바드", "기계공학자"]
        for i in range(ai_count):
            job = ai_jobs[i % len(ai_jobs)]
            ai_name = f"{job}로바트"
            session.add_ai_partner(
                ai_name, 
                job,
                communication_style=random.choice(list(CommunicationStyle))
            )
        
        return session
    
    def start_learning_tournament(self, rounds: int = 5):
        """학습 토너먼트 시작"""
        print("🏆 === AI 학습 토너먼트 시작! ===")
        print(f"   라운드 수: {rounds}")
        print()
        
        for round_num in range(1, rounds + 1):
            print(f"🔥 라운드 {round_num}/{rounds}")
            
            # 새로운 혼합 세션 생성
            session = self.create_balanced_party(
                human_count=random.randint(1, 2),
                ai_count=random.randint(2, 4)
            )
            
            # 랜덤 플레이 모드 설정
            session.set_play_mode(random.choice(list(HybridPlayMode)))
            
            # 짧은 시뮬레이션 실행
            session.simulate_hybrid_gameplay(duration_minutes=1)
            
            print()
        
        print("🎉 토너먼트 완료! AI들이 많이 성장했습니다!")

def demo_hybrid_system():
    """혼합 시스템 데모"""
    print("🚀 === 인간-AI 혼합 멀티플레이어 시스템 데모 ===")
    print()
    
    # 고급 혼합 시스템 생성
    mixed_system = AdvancedMixedMultiplayer()
    
    # 균형잡힌 파티 생성 (인간 1명 + AI 3명)
    session = mixed_system.create_balanced_party(human_count=1, ai_count=3)
    
    # 다양한 플레이 모드 테스트
    modes = [HybridPlayMode.COOPERATIVE, HybridPlayMode.TEACHING, HybridPlayMode.FUSION]
    
    for mode in modes:
        print(f"\n--- {mode.value} 테스트 ---")
        session.set_play_mode(mode)
        session.simulate_hybrid_gameplay(duration_minutes=1)
    
    print("\n🏆 학습 토너먼트 시작!")
    mixed_system.start_learning_tournament(rounds=3)
    
    print("\n✨ 혼합 시스템 데모 완료!")
    print("   인간과 AI가 완벽하게 협력하는 미래의 게임입니다!")

if __name__ == "__main__":
    demo_hybrid_system()
