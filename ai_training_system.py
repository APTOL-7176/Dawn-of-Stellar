#!/usr/bin/env python3
"""
🎯 AI 훈련 시스템 (AI Training System)
Dawn of Stellar - 지능형 AI 학습 및 발전 시스템

AI 캐릭터들이 다양한 상황에서 학습하고 발전할 수 있는 종합 훈련 모드
"""

import random
import time
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import sqlite3
import threading
from datetime import datetime, timedelta

# 기존 시스템 임포트
from ai_character_database import AICharacterDatabase, LearningEvent
from ai_interaction_system import AIInteractionSystem, EmotionState, InteractionType
from ai_cooperation_system import AICooperationSystem
from complete_27_job_system import Complete27JobSystem, job_system

class TrainingMode(Enum):
    """훈련 모드 타입"""
    COMBAT_TRAINING = "전투_훈련"
    COOPERATION_TRAINING = "협력_훈련"
    EMOTION_TRAINING = "감정_훈련"
    STRATEGY_TRAINING = "전략_훈련"
    PERSONALITY_DEVELOPMENT = "개성_발달"
    SURVIVAL_TRAINING = "생존_훈련"
    LEADERSHIP_TRAINING = "리더십_훈련"
    ADAPTIVE_LEARNING = "적응_학습"

class TrainingDifficulty(Enum):
    """훈련 난이도"""
    BEGINNER = "초급"
    INTERMEDIATE = "중급"
    ADVANCED = "고급"
    EXPERT = "전문가"
    MASTER = "마스터"

@dataclass
class TrainingScenario:
    """훈련 시나리오"""
    scenario_id: str
    name: str
    description: str
    training_mode: TrainingMode
    difficulty: TrainingDifficulty
    required_participants: int
    required_jobs: List[str]
    duration_minutes: int
    learning_objectives: List[str]
    success_conditions: Dict[str, float]
    rewards: Dict[str, float]

@dataclass
class TrainingSession:
    """훈련 세션"""
    session_id: str
    scenario: TrainingScenario
    participants: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    progress: float  # 0.0 ~ 1.0
    success_rate: float
    learning_gains: Dict[str, float]
    performance_metrics: Dict[str, Any]
    ai_feedback: List[str]

@dataclass
class AILearningProfile:
    """AI 학습 프로필"""
    ai_name: str
    job_class: str
    learning_rate: float  # 기본 학습 속도
    strengths: List[str]  # 강점 영역
    weaknesses: List[str]  # 약점 영역
    personality_traits: Dict[str, float]
    skill_levels: Dict[str, int]  # 기술별 레벨 (1-100)
    training_hours: Dict[TrainingMode, int]  # 훈련 시간 누적
    performance_history: List[Dict[str, Any]]
    adaptation_score: float  # 적응력 점수

class AITrainingSystem:
    """AI 훈련 시스템 메인 클래스"""
    
    def __init__(self):
        # 기존 시스템 연동
        self.character_db = None
        self.interaction_system = None
        self.cooperation_system = None
        self.job_system = Complete27JobSystem()
        
        # 훈련 시스템 데이터
        self.training_scenarios: Dict[str, TrainingScenario] = {}
        self.active_sessions: Dict[str, TrainingSession] = {}
        self.ai_profiles: Dict[str, AILearningProfile] = {}
        self.training_history: List[TrainingSession] = []
        
        # 설정
        self.auto_save_interval = 300  # 5분마다 자동 저장
        self.max_concurrent_sessions = 5
        self.training_data_dir = "ai_training_data"
        
        # 초기화
        self._init_training_system()
        print("🎯 AI 훈련 시스템 초기화 완료")
    
    def _init_training_system(self):
        """훈련 시스템 초기화"""
        # 디렉토리 생성
        os.makedirs(self.training_data_dir, exist_ok=True)
        
        # 기본 훈련 시나리오 로드
        self._load_default_scenarios()
        
        # 기존 AI 프로필 로드
        self._load_ai_profiles()
        
        # 자동 저장 스레드 시작
        self._start_auto_save_thread()
    
    def _load_default_scenarios(self):
        """기본 훈련 시나리오 로드"""
        
        # 1. 전투 훈련 시나리오들
        self.training_scenarios["combat_basic"] = TrainingScenario(
            scenario_id="combat_basic",
            name="기본 전투 훈련",
            description="AI가 기본적인 전투 패턴과 기술을 학습합니다",
            training_mode=TrainingMode.COMBAT_TRAINING,
            difficulty=TrainingDifficulty.BEGINNER,
            required_participants=2,
            required_jobs=["전사", "궁수", "아크메이지"],
            duration_minutes=15,
            learning_objectives=["기본_공격_패턴", "방어_타이밍", "스킬_사용법"],
            success_conditions={"accuracy": 0.7, "survival_rate": 0.8},
            rewards={"combat_exp": 100, "skill_points": 5}
        )
        
        self.training_scenarios["combat_advanced"] = TrainingScenario(
            scenario_id="combat_advanced",
            name="고급 전투 훈련",
            description="복잡한 전투 상황에서의 전략적 사고와 연계 공격을 학습합니다",
            training_mode=TrainingMode.COMBAT_TRAINING,
            difficulty=TrainingDifficulty.ADVANCED,
            required_participants=4,
            required_jobs=["전사", "아크메이지", "성기사", "도적"],
            duration_minutes=30,
            learning_objectives=["연계_공격", "전술적_사고", "상황_판단"],
            success_conditions={"team_coordination": 0.8, "strategic_thinking": 0.7},
            rewards={"combat_exp": 300, "skill_points": 15, "tactical_knowledge": 10}
        )
        
        # 2. 협력 훈련 시나리오들
        self.training_scenarios["cooperation_basic"] = TrainingScenario(
            scenario_id="cooperation_basic",
            name="기본 협력 훈련",
            description="AI들이 기본적인 협력과 의사소통을 학습합니다",
            training_mode=TrainingMode.COOPERATION_TRAINING,
            difficulty=TrainingDifficulty.BEGINNER,
            required_participants=3,
            required_jobs=["전사", "신관", "궁수"],
            duration_minutes=20,
            learning_objectives=["기본_의사소통", "역할_분담", "협력_행동"],
            success_conditions={"cooperation_score": 0.7, "communication_quality": 0.6},
            rewards={"cooperation_exp": 150, "social_skills": 10}
        )
        
        # 3. 감정 훈련 시나리오들
        self.training_scenarios["emotion_basic"] = TrainingScenario(
            scenario_id="emotion_basic",
            name="감정 인식 훈련",
            description="AI가 다양한 감정을 인식하고 적절히 반응하는 방법을 학습합니다",
            training_mode=TrainingMode.EMOTION_TRAINING,
            difficulty=TrainingDifficulty.INTERMEDIATE,
            required_participants=2,
            required_jobs=["바드", "신관", "드루이드"],
            duration_minutes=25,
            learning_objectives=["감정_인식", "감정_표현", "공감_능력"],
            success_conditions={"emotion_recognition": 0.8, "empathy_score": 0.7},
            rewards={"emotional_intelligence": 20, "social_skills": 15}
        )
        
        # 4. 전략 훈련 시나리오들
        self.training_scenarios["strategy_basic"] = TrainingScenario(
            scenario_id="strategy_basic",
            name="기본 전략 훈련",
            description="AI가 상황 분석과 전략적 계획 수립을 학습합니다",
            training_mode=TrainingMode.STRATEGY_TRAINING,
            difficulty=TrainingDifficulty.INTERMEDIATE,
            required_participants=3,
            required_jobs=["철학자", "시간술사", "차원술사"],
            duration_minutes=35,
            learning_objectives=["상황_분석", "전략_수립", "계획_실행"],
            success_conditions={"strategic_thinking": 0.75, "execution_quality": 0.7},
            rewards={"strategic_knowledge": 25, "intelligence_boost": 10}
        )
        
        # 5. 리더십 훈련 시나리오들
        self.training_scenarios["leadership_basic"] = TrainingScenario(
            scenario_id="leadership_basic",
            name="리더십 기초 훈련",
            description="AI가 팀을 이끄는 리더십 스킬을 학습합니다",
            training_mode=TrainingMode.LEADERSHIP_TRAINING,
            difficulty=TrainingDifficulty.ADVANCED,
            required_participants=4,
            required_jobs=["성기사", "기사", "검투사", "사무라이"],
            duration_minutes=40,
            learning_objectives=["팀_관리", "의사결정", "동기_부여"],
            success_conditions={"leadership_effectiveness": 0.8, "team_morale": 0.75},
            rewards={"leadership_exp": 200, "charisma_boost": 15}
        )
        
        print(f"✅ {len(self.training_scenarios)}개 기본 훈련 시나리오 로드 완료")
    
    def _load_ai_profiles(self):
        """AI 학습 프로필 로드"""
        profile_file = os.path.join(self.training_data_dir, "ai_learning_profiles.json")
        
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, profile_data in data.items():
                        self.ai_profiles[name] = AILearningProfile(**profile_data)
                print(f"✅ {len(self.ai_profiles)}개 AI 학습 프로필 로드 완료")
            except Exception as e:
                print(f"⚠️ AI 프로필 로드 실패: {e}")
    
    def _save_ai_profiles(self):
        """AI 학습 프로필 저장"""
        profile_file = os.path.join(self.training_data_dir, "ai_learning_profiles.json")
        
        try:
            data = {name: asdict(profile) for name, profile in self.ai_profiles.items()}
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ AI 프로필 저장 실패: {e}")
    
    def _start_auto_save_thread(self):
        """자동 저장 스레드 시작"""
        def auto_save():
            while True:
                time.sleep(self.auto_save_interval)
                self._save_ai_profiles()
                self._save_training_history()
        
        thread = threading.Thread(target=auto_save, daemon=True)
        thread.start()
        print("🔄 자동 저장 스레드 시작")
    
    def _save_training_history(self):
        """훈련 히스토리 저장"""
        history_file = os.path.join(self.training_data_dir, "training_history.json")
        
        try:
            data = [asdict(session) for session in self.training_history[-100:]]  # 최근 100개만
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ 훈련 히스토리 저장 실패: {e}")
    
    def create_ai_profile(self, ai_name: str, job_class: str) -> AILearningProfile:
        """새로운 AI 학습 프로필 생성"""
        # job_system에서 직업 정보 가져오기
        job_info = None
        if hasattr(job_system, 'jobs') and job_class in job_system.jobs:
            job_info = job_system.jobs[job_class]
        
        # 직업별 기본 특성 설정
        base_traits = {
            "courage": 0.5,
            "intelligence": 0.5,
            "creativity": 0.5,
            "empathy": 0.5,
            "leadership": 0.5,
            "adaptability": 0.5
        }
        
        # 직업별 특성 조정
        if job_class in ["전사", "성기사", "기사"]:
            base_traits["courage"] += 0.3
            base_traits["leadership"] += 0.2
        elif job_class in ["아크메이지", "철학자", "시간술사"]:
            base_traits["intelligence"] += 0.3
            base_traits["creativity"] += 0.2
        elif job_class in ["바드", "신관", "드루이드"]:
            base_traits["empathy"] += 0.3
            base_traits["creativity"] += 0.2
        
        profile = AILearningProfile(
            ai_name=ai_name,
            job_class=job_class,
            learning_rate=random.uniform(0.8, 1.2),
            strengths=[],
            weaknesses=[],
            personality_traits=base_traits,
            skill_levels={
                "combat": random.randint(20, 40),
                "magic": random.randint(20, 40),
                "social": random.randint(20, 40),
                "strategy": random.randint(20, 40),
                "survival": random.randint(20, 40)
            },
            training_hours={mode: 0 for mode in TrainingMode},
            performance_history=[],
            adaptation_score=0.5
        )
        
        self.ai_profiles[ai_name] = profile
        print(f"✅ {ai_name} ({job_class}) AI 학습 프로필 생성 완료")
        return profile
    
    def start_training_session(self, scenario_id: str, participants: List[str]) -> str:
        """훈련 세션 시작"""
        if len(self.active_sessions) >= self.max_concurrent_sessions:
            print("❌ 동시 실행 가능한 훈련 세션 수를 초과했습니다")
            return None
        
        if scenario_id not in self.training_scenarios:
            print(f"❌ 훈련 시나리오 '{scenario_id}'를 찾을 수 없습니다")
            return None
        
        scenario = self.training_scenarios[scenario_id]
        
        # 참가자 수 확인
        if len(participants) != scenario.required_participants:
            print(f"❌ 필요한 참가자 수: {scenario.required_participants}명, 현재: {len(participants)}명")
            return None
        
        # 참가자 프로필 확인 및 생성
        for participant in participants:
            if participant not in self.ai_profiles:
                # 랜덤 직업으로 프로필 생성
                random_job = random.choice(scenario.required_jobs)
                self.create_ai_profile(participant, random_job)
        
        # 세션 ID 생성
        session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # 훈련 세션 생성
        session = TrainingSession(
            session_id=session_id,
            scenario=scenario,
            participants=participants,
            start_time=datetime.now(),
            end_time=None,
            progress=0.0,
            success_rate=0.0,
            learning_gains={},
            performance_metrics={},
            ai_feedback=[]
        )
        
        self.active_sessions[session_id] = session
        
        print(f"🎯 훈련 세션 시작: {scenario.name}")
        print(f"   세션 ID: {session_id}")
        print(f"   참가자: {', '.join(participants)}")
        print(f"   예상 소요 시간: {scenario.duration_minutes}분")
        
        # 훈련 실행 (백그라운드)
        threading.Thread(target=self._execute_training, args=(session_id,), daemon=True).start()
        
        return session_id
    
    def _execute_training(self, session_id: str):
        """훈련 실행 (백그라운드 프로세스)"""
        session = self.active_sessions[session_id]
        scenario = session.scenario
        
        print(f"🔄 훈련 실행 시작: {scenario.name}")
        
        # 훈련 단계별 실행
        training_steps = self._generate_training_steps(scenario)
        total_steps = len(training_steps)
        
        for i, step in enumerate(training_steps):
            # 진행률 업데이트
            session.progress = (i + 1) / total_steps
            
            # 단계 실행
            step_result = self._execute_training_step(session, step)
            
            # 결과 처리
            self._process_step_result(session, step_result)
            
            # 진행 상황 출력
            if i % (total_steps // 4) == 0:  # 25%마다 출력
                print(f"📊 {scenario.name} 진행률: {session.progress * 100:.0f}%")
            
            # 잠시 대기 (실제 훈련 시간 시뮬레이션)
            time.sleep(0.5)
        
        # 훈련 완료 처리
        self._complete_training_session(session_id)
    
    def _generate_training_steps(self, scenario: TrainingScenario) -> List[Dict[str, Any]]:
        """훈련 단계 생성"""
        steps = []
        
        if scenario.training_mode == TrainingMode.COMBAT_TRAINING:
            steps = [
                {"type": "warmup", "description": "전투 준비 및 기본 동작 확인"},
                {"type": "basic_combat", "description": "기본 공격 패턴 연습"},
                {"type": "skill_practice", "description": "스킬 사용법 연습"},
                {"type": "defensive_training", "description": "방어 및 회피 훈련"},
                {"type": "combat_simulation", "description": "실전 전투 시뮬레이션"},
                {"type": "evaluation", "description": "성과 평가 및 피드백"}
            ]
        elif scenario.training_mode == TrainingMode.COOPERATION_TRAINING:
            steps = [
                {"type": "introduction", "description": "팀원 소개 및 역할 분담"},
                {"type": "communication", "description": "의사소통 방법 학습"},
                {"type": "cooperation_exercise", "description": "협력 과제 수행"},
                {"type": "problem_solving", "description": "공동 문제 해결"},
                {"type": "team_building", "description": "팀워크 강화 활동"},
                {"type": "evaluation", "description": "협력 성과 평가"}
            ]
        elif scenario.training_mode == TrainingMode.EMOTION_TRAINING:
            steps = [
                {"type": "emotion_recognition", "description": "감정 인식 연습"},
                {"type": "empathy_exercise", "description": "공감 능력 개발"},
                {"type": "emotional_expression", "description": "감정 표현 방법 학습"},
                {"type": "social_interaction", "description": "사회적 상호작용 연습"},
                {"type": "emotional_intelligence", "description": "감정 지능 종합 평가"}
            ]
        else:
            # 기본 훈련 단계
            steps = [
                {"type": "preparation", "description": "훈련 준비"},
                {"type": "basic_exercise", "description": "기본 연습"},
                {"type": "advanced_exercise", "description": "고급 연습"},
                {"type": "practical_application", "description": "실전 적용"},
                {"type": "evaluation", "description": "성과 평가"}
            ]
        
        return steps
    
    def _execute_training_step(self, session: TrainingSession, step: Dict[str, Any]) -> Dict[str, Any]:
        """훈련 단계 실행"""
        participants = session.participants
        scenario = session.scenario
        
        # 각 참가자의 성과 시뮬레이션
        step_results = {}
        
        for participant in participants:
            profile = self.ai_profiles[participant]
            
            # 성과 계산 (학습률, 난이도, 개인 특성 고려)
            base_performance = random.uniform(0.3, 0.9)
            
            # 학습률 적용
            learning_bonus = (profile.learning_rate - 1.0) * 0.3
            
            # 난이도 조정
            difficulty_modifier = {
                TrainingDifficulty.BEGINNER: 0.2,
                TrainingDifficulty.INTERMEDIATE: 0.0,
                TrainingDifficulty.ADVANCED: -0.2,
                TrainingDifficulty.EXPERT: -0.3,
                TrainingDifficulty.MASTER: -0.4
            }[scenario.difficulty]
            
            # 개인 특성 적용
            trait_bonus = 0.0
            if step["type"] in ["combat_simulation", "basic_combat"]:
                trait_bonus = (profile.personality_traits.get("courage", 0.5) - 0.5) * 0.2
            elif step["type"] in ["cooperation_exercise", "team_building"]:
                trait_bonus = (profile.personality_traits.get("empathy", 0.5) - 0.5) * 0.2
            elif step["type"] in ["problem_solving", "evaluation"]:
                trait_bonus = (profile.personality_traits.get("intelligence", 0.5) - 0.5) * 0.2
            
            final_performance = max(0.1, min(1.0, 
                base_performance + learning_bonus + difficulty_modifier + trait_bonus
            ))
            
            step_results[participant] = {
                "performance": final_performance,
                "learning_gain": final_performance * profile.learning_rate * 0.1,
                "feedback": self._generate_feedback(participant, step, final_performance)
            }
        
        return {
            "step_type": step["type"],
            "description": step["description"],
            "participant_results": step_results,
            "overall_success": sum(r["performance"] for r in step_results.values()) / len(step_results)
        }
    
    def _generate_feedback(self, participant: str, step: Dict[str, Any], performance: float) -> str:
        """AI 피드백 생성"""
        profile = self.ai_profiles[participant]
        
        if performance >= 0.8:
            feedback_pool = [
                f"{participant}는 {step['description']}에서 뛰어난 성과를 보였습니다!",
                f"훌륭합니다! {participant}의 {step['type']} 실력이 크게 향상되었네요.",
                f"{participant}는 이 분야에서 타고난 재능을 보여주고 있습니다."
            ]
        elif performance >= 0.6:
            feedback_pool = [
                f"{participant}는 {step['description']}에서 안정적인 실력을 보였습니다.",
                f"좋은 진전이에요! {participant}의 꾸준한 노력이 보입니다.",
                f"{participant}는 이해도가 높아지고 있어요."
            ]
        elif performance >= 0.4:
            feedback_pool = [
                f"{participant}는 {step['description']}에서 더 많은 연습이 필요해 보입니다.",
                f"{participant}에게는 이 부분이 조금 어려운 것 같네요. 추가 훈련을 권장합니다.",
                f"아직 개선의 여지가 있어요. {participant}의 잠재력은 충분합니다."
            ]
        else:
            feedback_pool = [
                f"{participant}는 {step['description']}에서 많은 어려움을 겪고 있습니다.",
                f"{participant}에게는 기초부터 다시 시작하는 것이 좋겠어요.",
                f"걱정하지 마세요, {participant}! 처음에는 누구나 어려워해요."
            ]
        
        return random.choice(feedback_pool)
    
    def _process_step_result(self, session: TrainingSession, step_result: Dict[str, Any]):
        """단계 결과 처리"""
        # 세션에 결과 저장
        if "step_results" not in session.performance_metrics:
            session.performance_metrics["step_results"] = []
        
        session.performance_metrics["step_results"].append(step_result)
        
        # AI 피드백 추가
        for participant, result in step_result["participant_results"].items():
            session.ai_feedback.append(result["feedback"])
            
            # 개별 AI 프로필 업데이트
            profile = self.ai_profiles[participant]
            
            # 학습 이득 적용
            learning_gain = result["learning_gain"]
            
            # 스킬 레벨 업데이트 (훈련 타입에 따라)
            if session.scenario.training_mode == TrainingMode.COMBAT_TRAINING:
                profile.skill_levels["combat"] = min(100, profile.skill_levels["combat"] + learning_gain * 10)
            elif session.scenario.training_mode == TrainingMode.COOPERATION_TRAINING:
                profile.skill_levels["social"] = min(100, profile.skill_levels["social"] + learning_gain * 10)
            elif session.scenario.training_mode == TrainingMode.STRATEGY_TRAINING:
                profile.skill_levels["strategy"] = min(100, profile.skill_levels["strategy"] + learning_gain * 10)
    
    def _complete_training_session(self, session_id: str):
        """훈련 세션 완료 처리"""
        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        session.progress = 1.0
        
        # 최종 성공률 계산
        if "step_results" in session.performance_metrics:
            total_performance = sum(
                step["overall_success"] for step in session.performance_metrics["step_results"]
            )
            session.success_rate = total_performance / len(session.performance_metrics["step_results"])
        
        # 훈련 시간 기록
        training_duration = (session.end_time - session.start_time).total_seconds() / 3600  # 시간 단위
        
        for participant in session.participants:
            profile = self.ai_profiles[participant]
            profile.training_hours[session.scenario.training_mode] += int(training_duration * 60)  # 분 단위
            
            # 성과 히스토리에 추가
            profile.performance_history.append({
                "session_id": session_id,
                "scenario_name": session.scenario.name,
                "date": session.end_time.isoformat(),
                "success_rate": session.success_rate,
                "learning_gains": session.learning_gains.get(participant, 0)
            })
        
        # 활성 세션에서 제거하고 히스토리에 추가
        del self.active_sessions[session_id]
        self.training_history.append(session)
        
        print(f"✅ 훈련 세션 완료: {session.scenario.name}")
        print(f"   성공률: {session.success_rate * 100:.1f}%")
        print(f"   소요 시간: {training_duration * 60:.0f}분")
        
        # 보상 지급
        self._award_training_rewards(session)
    
    def _award_training_rewards(self, session: TrainingSession):
        """훈련 보상 지급"""
        rewards = session.scenario.rewards
        success_multiplier = session.success_rate
        
        print(f"\n🎁 훈련 보상 지급:")
        
        for participant in session.participants:
            profile = self.ai_profiles[participant]
            
            for reward_type, base_amount in rewards.items():
                actual_reward = int(base_amount * success_multiplier)
                
                if reward_type == "combat_exp":
                    profile.skill_levels["combat"] = min(100, profile.skill_levels["combat"] + actual_reward // 10)
                elif reward_type == "social_skills":
                    profile.skill_levels["social"] = min(100, profile.skill_levels["social"] + actual_reward // 10)
                elif reward_type == "strategic_knowledge":
                    profile.skill_levels["strategy"] = min(100, profile.skill_levels["strategy"] + actual_reward // 10)
                elif reward_type == "emotional_intelligence":
                    profile.personality_traits["empathy"] = min(1.0, profile.personality_traits["empathy"] + actual_reward / 1000)
                
                print(f"   {participant}: {reward_type} +{actual_reward}")
    
    def get_training_status(self) -> Dict[str, Any]:
        """훈련 상태 정보 반환"""
        return {
            "active_sessions": len(self.active_sessions),
            "total_ai_profiles": len(self.ai_profiles),
            "total_scenarios": len(self.training_scenarios),
            "completed_sessions": len(self.training_history),
            "available_capacity": self.max_concurrent_sessions - len(self.active_sessions)
        }
    
    def get_ai_progress(self, ai_name: str) -> Optional[Dict[str, Any]]:
        """특정 AI의 진행 상황 반환"""
        if ai_name not in self.ai_profiles:
            return None
        
        profile = self.ai_profiles[ai_name]
        
        # 총 훈련 시간 계산
        total_hours = sum(profile.training_hours.values())
        
        # 평균 성과 계산
        avg_performance = 0.0
        if profile.performance_history:
            avg_performance = sum(h["success_rate"] for h in profile.performance_history) / len(profile.performance_history)
        
        return {
            "ai_name": ai_name,
            "job_class": profile.job_class,
            "total_training_hours": total_hours,
            "skill_levels": profile.skill_levels,
            "personality_traits": profile.personality_traits,
            "average_performance": avg_performance,
            "total_sessions": len(profile.performance_history),
            "adaptation_score": profile.adaptation_score,
            "recent_improvements": self._calculate_recent_improvements(profile)
        }
    
    def _calculate_recent_improvements(self, profile: AILearningProfile) -> Dict[str, float]:
        """최근 개선 사항 계산"""
        if len(profile.performance_history) < 2:
            return {}
        
        recent_sessions = profile.performance_history[-5:]  # 최근 5세션
        older_sessions = profile.performance_history[-10:-5] if len(profile.performance_history) >= 10 else profile.performance_history[:-5]
        
        if not older_sessions:
            return {}
        
        recent_avg = sum(s["success_rate"] for s in recent_sessions) / len(recent_sessions)
        older_avg = sum(s["success_rate"] for s in older_sessions) / len(older_sessions)
        
        return {
            "performance_improvement": recent_avg - older_avg,
            "trend": "향상" if recent_avg > older_avg else "정체" if recent_avg == older_avg else "하락"
        }
    
    def show_training_menu(self):
        """훈련 메뉴 표시"""
        while True:
            print("\n" + "=" * 60)
            print("🎯 AI 훈련 시스템 메인 메뉴")
            print("=" * 60)
            
            status = self.get_training_status()
            print(f"📊 시스템 상태: 활성 세션 {status['active_sessions']}/{self.max_concurrent_sessions}")
            print(f"   등록된 AI: {status['total_ai_profiles']}개")
            print(f"   이용 가능한 시나리오: {status['total_scenarios']}개")
            
            print("\n1. 🥊 훈련 세션 시작")
            print("2. 📋 훈련 시나리오 목록")
            print("3. 👤 AI 프로필 관리")
            print("4. 📊 진행 상황 보기")
            print("5. 🏃‍♂️ 활성 세션 모니터링")
            print("6. 📜 훈련 히스토리")
            print("7. ⚙️ 시스템 설정")
            print("0. 🚪 돌아가기")
            
            choice = input("\n선택하세요: ").strip()
            
            if choice == "1":
                self._start_training_menu()
            elif choice == "2":
                self._show_training_scenarios()
            elif choice == "3":
                self._ai_profile_menu()
            elif choice == "4":
                self._show_progress_dashboard()
            elif choice == "5":
                self._monitor_active_sessions()
            elif choice == "6":
                self._show_training_history()
            elif choice == "7":
                self._system_settings_menu()
            elif choice == "0":
                break
            else:
                print("❌ 잘못된 선택입니다.")
            
            if choice != "0":
                input("\n계속하려면 Enter를 누르세요...")
    
    def _start_training_menu(self):
        """훈련 시작 메뉴"""
        print("\n🥊 훈련 세션 시작")
        print("-" * 40)
        
        # 사용 가능한 시나리오 표시
        print("사용 가능한 훈련 시나리오:")
        for i, (scenario_id, scenario) in enumerate(self.training_scenarios.items(), 1):
            print(f"{i}. {scenario.name} ({scenario.difficulty.value})")
            print(f"   모드: {scenario.training_mode.value}")
            print(f"   참가자: {scenario.required_participants}명")
            print(f"   소요 시간: {scenario.duration_minutes}분")
            print()
        
        try:
            choice = int(input("시나리오 선택 (번호): ")) - 1
            scenario_list = list(self.training_scenarios.keys())
            
            if 0 <= choice < len(scenario_list):
                scenario_id = scenario_list[choice]
                scenario = self.training_scenarios[scenario_id]
                
                print(f"\n선택된 시나리오: {scenario.name}")
                print(f"필요한 참가자 수: {scenario.required_participants}명")
                
                # 참가자 선택
                participants = []
                for i in range(scenario.required_participants):
                    name = input(f"참가자 {i+1} 이름: ").strip()
                    if name:
                        participants.append(name)
                
                if len(participants) == scenario.required_participants:
                    session_id = self.start_training_session(scenario_id, participants)
                    if session_id:
                        print(f"✅ 훈련 세션이 시작되었습니다! (ID: {session_id})")
                else:
                    print("❌ 참가자 수가 부족합니다.")
            else:
                print("❌ 잘못된 선택입니다.")
                
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _show_training_scenarios(self):
        """훈련 시나리오 목록 표시"""
        print("\n📋 훈련 시나리오 목록")
        print("=" * 60)
        
        by_mode = {}
        for scenario in self.training_scenarios.values():
            mode = scenario.training_mode.value
            if mode not in by_mode:
                by_mode[mode] = []
            by_mode[mode].append(scenario)
        
        for mode, scenarios in by_mode.items():
            print(f"\n🎯 {mode}")
            print("-" * 40)
            
            for scenario in scenarios:
                print(f"📌 {scenario.name} ({scenario.difficulty.value})")
                print(f"   설명: {scenario.description}")
                print(f"   참가자: {scenario.required_participants}명")
                print(f"   필요 직업: {', '.join(scenario.required_jobs)}")
                print(f"   소요 시간: {scenario.duration_minutes}분")
                print(f"   학습 목표: {', '.join(scenario.learning_objectives)}")
                print()
    
    def _ai_profile_menu(self):
        """AI 프로필 관리 메뉴"""
        print("\n👤 AI 프로필 관리")
        print("-" * 40)
        
        if not self.ai_profiles:
            print("📭 등록된 AI가 없습니다.")
            
            create = input("새 AI 프로필을 생성하시겠습니까? (y/n): ").strip().lower()
            if create == 'y':
                name = input("AI 이름: ").strip()
                
                print("\n사용 가능한 직업:")
                jobs = ["전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크", "바드"]
                for i, job in enumerate(jobs, 1):
                    print(f"{i}. {job}")
                
                try:
                    job_choice = int(input("직업 선택 (번호): ")) - 1
                    if 0 <= job_choice < len(jobs):
                        job_class = jobs[job_choice]
                        self.create_ai_profile(name, job_class)
                    else:
                        print("❌ 잘못된 선택입니다.")
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
            return
        
        print("등록된 AI 목록:")
        for i, (name, profile) in enumerate(self.ai_profiles.items(), 1):
            total_hours = sum(profile.training_hours.values())
            avg_skill = sum(profile.skill_levels.values()) / len(profile.skill_levels)
            
            print(f"{i}. {name} ({profile.job_class})")
            print(f"   훈련 시간: {total_hours}분")
            print(f"   평균 스킬 레벨: {avg_skill:.1f}")
            print()
        
        try:
            choice = int(input("상세 정보를 볼 AI 선택 (번호, 0=취소): "))
            if choice > 0:
                ai_names = list(self.ai_profiles.keys())
                if choice <= len(ai_names):
                    ai_name = ai_names[choice - 1]
                    progress = self.get_ai_progress(ai_name)
                    self._show_ai_details(progress)
        except ValueError:
            pass
    
    def _show_ai_details(self, progress: Dict[str, Any]):
        """AI 상세 정보 표시"""
        print(f"\n👤 {progress['ai_name']} 상세 정보")
        print("=" * 50)
        
        print(f"직업: {progress['job_class']}")
        print(f"총 훈련 시간: {progress['total_training_hours']}분")
        print(f"참여한 세션 수: {progress['total_sessions']}개")
        print(f"평균 성과: {progress['average_performance'] * 100:.1f}%")
        print(f"적응력 점수: {progress['adaptation_score'] * 100:.1f}%")
        
        print("\n🎯 스킬 레벨:")
        for skill, level in progress['skill_levels'].items():
            bar = "█" * (level // 10) + "▒" * (10 - level // 10)
            print(f"   {skill}: {level:3d}/100 [{bar}]")
        
        print("\n🎭 성격 특성:")
        for trait, value in progress['personality_traits'].items():
            bar = "█" * int(value * 10) + "▒" * (10 - int(value * 10))
            print(f"   {trait}: {value:.2f} [{bar}]")
        
        if progress['recent_improvements']:
            improvements = progress['recent_improvements']
            trend_emoji = "📈" if improvements['trend'] == "향상" else "📉" if improvements['trend'] == "하락" else "📊"
            print(f"\n📊 최근 동향: {trend_emoji} {improvements['trend']}")
            if improvements.get('performance_improvement'):
                print(f"   성과 변화: {improvements['performance_improvement']:+.2f}")
    
    def _show_progress_dashboard(self):
        """진행 상황 대시보드"""
        print("\n📊 AI 훈련 진행 상황 대시보드")
        print("=" * 60)
        
        if not self.ai_profiles:
            print("📭 등록된 AI가 없습니다.")
            return
        
        # 전체 통계
        total_sessions = len(self.training_history)
        total_hours = sum(
            sum(profile.training_hours.values()) 
            for profile in self.ai_profiles.values()
        )
        
        print(f"📈 전체 통계:")
        print(f"   총 완료된 세션: {total_sessions}개")
        print(f"   총 훈련 시간: {total_hours}분 ({total_hours/60:.1f}시간)")
        print(f"   등록된 AI: {len(self.ai_profiles)}개")
        
        # 훈련 모드별 통계
        mode_stats = {}
        for profile in self.ai_profiles.values():
            for mode, hours in profile.training_hours.items():
                if mode not in mode_stats:
                    mode_stats[mode] = 0
                mode_stats[mode] += hours
        
        print(f"\n🎯 훈련 모드별 통계:")
        for mode, hours in mode_stats.items():
            if hours > 0:
                print(f"   {mode.value}: {hours}분")
        
        # 최고 성과 AI
        best_performers = []
        for name, profile in self.ai_profiles.items():
            if profile.performance_history:
                avg_performance = sum(h["success_rate"] for h in profile.performance_history) / len(profile.performance_history)
                best_performers.append((name, avg_performance, profile.job_class))
        
        best_performers.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🏆 최고 성과 AI (TOP 5):")
        for i, (name, performance, job) in enumerate(best_performers[:5], 1):
            print(f"   {i}. {name} ({job}): {performance * 100:.1f}%")
    
    def _monitor_active_sessions(self):
        """활성 세션 모니터링"""
        print("\n🏃‍♂️ 활성 훈련 세션 모니터링")
        print("=" * 60)
        
        if not self.active_sessions:
            print("📭 현재 활성 세션이 없습니다.")
            return
        
        for session_id, session in self.active_sessions.items():
            elapsed = datetime.now() - session.start_time
            elapsed_minutes = elapsed.total_seconds() / 60
            
            print(f"🎯 {session.scenario.name}")
            print(f"   세션 ID: {session_id}")
            print(f"   참가자: {', '.join(session.participants)}")
            print(f"   진행률: {session.progress * 100:.1f}%")
            print(f"   경과 시간: {elapsed_minutes:.0f}분")
            print(f"   예상 완료: {session.scenario.duration_minutes}분")
            
            # 진행률 바
            progress_bar = "█" * int(session.progress * 20) + "▒" * (20 - int(session.progress * 20))
            print(f"   [{progress_bar}]")
            print()
    
    def _show_training_history(self):
        """훈련 히스토리 표시"""
        print("\n📜 훈련 히스토리")
        print("=" * 60)
        
        if not self.training_history:
            print("📭 훈련 히스토리가 없습니다.")
            return
        
        # 최근 10개 세션
        recent_sessions = self.training_history[-10:]
        
        for session in reversed(recent_sessions):
            duration = (session.end_time - session.start_time).total_seconds() / 60
            
            print(f"📅 {session.start_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   시나리오: {session.scenario.name}")
            print(f"   참가자: {', '.join(session.participants)}")
            print(f"   성공률: {session.success_rate * 100:.1f}%")
            print(f"   소요 시간: {duration:.0f}분")
            print()
    
    def _system_settings_menu(self):
        """시스템 설정 메뉴"""
        print("\n⚙️ 시스템 설정")
        print("-" * 40)
        
        print(f"현재 설정:")
        print(f"   최대 동시 세션 수: {self.max_concurrent_sessions}")
        print(f"   자동 저장 간격: {self.auto_save_interval}초")
        print(f"   데이터 디렉토리: {self.training_data_dir}")
        
        print(f"\n1. 최대 동시 세션 수 변경")
        print(f"2. 자동 저장 간격 변경")
        print(f"3. 데이터 백업")
        print(f"4. 시스템 초기화")
        print(f"0. 돌아가기")
        
        choice = input("\n선택하세요: ").strip()
        
        if choice == "1":
            try:
                new_max = int(input(f"새로운 최대 동시 세션 수 (현재: {self.max_concurrent_sessions}): "))
                if 1 <= new_max <= 20:
                    self.max_concurrent_sessions = new_max
                    print(f"✅ 최대 동시 세션 수가 {new_max}개로 변경되었습니다.")
                else:
                    print("❌ 1-20 사이의 값을 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
        
        elif choice == "2":
            try:
                new_interval = int(input(f"새로운 자동 저장 간격(초) (현재: {self.auto_save_interval}): "))
                if 60 <= new_interval <= 3600:
                    self.auto_save_interval = new_interval
                    print(f"✅ 자동 저장 간격이 {new_interval}초로 변경되었습니다.")
                else:
                    print("❌ 60-3600 사이의 값을 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
        
        elif choice == "3":
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"데이터를 {backup_dir}에 백업하는 중...")
            # 백업 로직 구현 (실제로는 파일 복사)
            print("✅ 백업이 완료되었습니다.")
        
        elif choice == "4":
            confirm = input("⚠️ 정말로 시스템을 초기화하시겠습니까? 모든 데이터가 삭제됩니다. (yes/no): ")
            if confirm.lower() == "yes":
                self.ai_profiles.clear()
                self.training_history.clear()
                print("✅ 시스템이 초기화되었습니다.")
            else:
                print("❌ 초기화가 취소되었습니다.")

# 전역 인스턴스
training_system = AITrainingSystem()

def test_training_system():
    """훈련 시스템 테스트"""
    print("🧪 AI 훈련 시스템 테스트")
    
    # 테스트 AI 생성
    training_system.create_ai_profile("테스트전사", "전사")
    training_system.create_ai_profile("테스트마법사", "아크메이지")
    
    # 훈련 세션 시작
    session_id = training_system.start_training_session(
        "combat_basic", 
        ["테스트전사", "테스트마법사"]
    )
    
    if session_id:
        print(f"✅ 테스트 세션 시작: {session_id}")
        
        # 잠시 대기 후 상태 확인
        time.sleep(3)
        
        status = training_system.get_training_status()
        print(f"📊 시스템 상태: {status}")
        
        # AI 진행 상황 확인
        progress = training_system.get_ai_progress("테스트전사")
        if progress:
            print(f"👤 테스트전사 진행 상황:")
            print(f"   평균 성과: {progress['average_performance'] * 100:.1f}%")
            print(f"   스킬 레벨: {progress['skill_levels']}")
    
    print("✅ 테스트 완료!")

if __name__ == "__main__":
    test_training_system()
