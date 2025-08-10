#!/usr/bin/env python3
"""
Dawn of Stellar - AI 간 상호작용 시스템
다중 AI 캐릭터 간의 협력, 경쟁, 그룹 다이나믹스 구현
"""

import json
import random
import time
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

# 기존 시스템 import
try:
    from ai_character_database import AICharacterDatabase
    from exaone_ai_engine import ExaoneAIEngine
    from game.cursor_menu_system import CursorMenu
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

class InteractionType(Enum):
    """AI 간 상호작용 타입"""
    COOPERATION = "cooperation"      # 협력
    COMPETITION = "competition"      # 경쟁
    NEGOTIATION = "negotiation"      # 협상
    DEBATE = "debate"               # 토론
    FRIENDSHIP = "friendship"       # 우정
    RIVALRY = "rivalry"             # 라이벌
    MENTORSHIP = "mentorship"       # 멘토링
    ROMANCE = "romance"             # 로맨스
    CONFLICT = "conflict"           # 갈등
    ALLIANCE = "alliance"           # 동맹

class EmotionState(Enum):
    """26가지 감정 상태"""
    # 긍정적 감정
    JOY = "기쁨"
    HAPPINESS = "행복"
    EXCITEMENT = "흥분"
    ENTHUSIASM = "열정"
    CONFIDENCE = "자신감"
    PRIDE = "자부심"
    SATISFACTION = "만족"
    RELIEF = "안도"
    GRATITUDE = "감사"
    LOVE = "사랑"
    AFFECTION = "애정"
    ADMIRATION = "존경"
    HOPE = "희망"
    
    # 부정적 감정
    SADNESS = "슬픔"
    ANGER = "분노"
    FEAR = "두려움"
    ANXIETY = "불안"
    FRUSTRATION = "좌절"
    DISAPPOINTMENT = "실망"
    JEALOUSY = "질투"
    GUILT = "죄책감"
    SHAME = "수치심"
    LONELINESS = "외로움"
    
    # 중성적 감정
    CURIOSITY = "호기심"
    SURPRISE = "놀람"
    CONFUSION = "혼란"

@dataclass
class AIInteraction:
    """AI 간 상호작용 데이터"""
    timestamp: float
    initiator: str                    # 상호작용 시작자
    target: str                       # 상호작용 대상
    interaction_type: InteractionType
    context: str                      # 상호작용 맥락
    emotion_before: EmotionState      # 이전 감정 상태
    emotion_after: EmotionState       # 이후 감정 상태
    success: bool                     # 상호작용 성공 여부
    outcome: str                      # 결과 설명
    relationship_change: float        # 관계도 변화 (-1.0 ~ +1.0)

@dataclass
class GroupDynamics:
    """그룹 내 역학 관계"""
    group_id: str
    members: List[str]                # 그룹 멤버 AI 이름들
    group_mood: EmotionState          # 그룹 전체 분위기
    leadership_score: Dict[str, float] # 각 멤버의 리더십 점수
    cooperation_level: float          # 협력 정도 (0.0 ~ 1.0)
    conflict_level: float             # 갈등 정도 (0.0 ~ 1.0)
    formed_time: float                # 그룹 형성 시간
    last_activity: float              # 마지막 활동 시간
    shared_goals: List[str]           # 공동 목표들
    group_achievements: List[str]     # 그룹 성과들

class AIInteractionSystem:
    """AI 간 상호작용 시스템 매니저"""
    
    def __init__(self, database_path: str = "ai_interactions.db"):
        self.database_path = database_path
        self.ai_engine = None
        self.active_groups: Dict[str, GroupDynamics] = {}
        self.relationship_matrix: Dict[Tuple[str, str], float] = {}
        self.emotion_states: Dict[str, EmotionState] = {}
        self.interaction_history: List[AIInteraction] = []
        self.interaction_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
        
        # 커서 메뉴 시스템
        self.cursor_menu = None
        try:
            self.cursor_menu = CursorMenu()
        except:
            pass
        
        # AI 엔진 초기화
        if DATABASE_AVAILABLE:
            try:
                self.ai_engine = ExaoneAIEngine()
                print("🤖 AI 상호작용 시스템 초기화 완료")
            except Exception as e:
                print(f"⚠️ AI 엔진 초기화 실패: {e}")
        
        self._init_database()
        self._start_processing_thread()
    
    def _init_database(self):
        """상호작용 데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # 상호작용 히스토리 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        initiator TEXT,
                        target TEXT,
                        interaction_type TEXT,
                        context TEXT,
                        emotion_before TEXT,
                        emotion_after TEXT,
                        success BOOLEAN,
                        outcome TEXT,
                        relationship_change REAL
                    )
                ''')
                
                # 관계도 매트릭스 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS relationships (
                        ai1 TEXT,
                        ai2 TEXT,
                        relationship_score REAL,
                        last_updated REAL,
                        PRIMARY KEY (ai1, ai2)
                    )
                ''')
                
                # 그룹 다이나믹스 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS group_dynamics (
                        group_id TEXT PRIMARY KEY,
                        members TEXT,
                        group_mood TEXT,
                        leadership_scores TEXT,
                        cooperation_level REAL,
                        conflict_level REAL,
                        formed_time REAL,
                        last_activity REAL,
                        shared_goals TEXT,
                        group_achievements TEXT
                    )
                ''')
                
                conn.commit()
                print("✅ AI 상호작용 데이터베이스 초기화 완료")
                
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 실패: {e}")
    
    def _start_processing_thread(self):
        """백그라운드 상호작용 처리 스레드 시작"""
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_interactions, daemon=True)
        self.processing_thread.start()
        print("🔄 AI 상호작용 처리 스레드 시작")
    
    def _process_interactions(self):
        """백그라운드에서 상호작용 처리"""
        while self.running:
            try:
                # 대기 중인 상호작용 처리
                interaction = self.interaction_queue.get(timeout=1.0)
                self._execute_interaction(interaction)
                
                # 주기적 그룹 다이나믹스 업데이트
                if random.random() < 0.1:  # 10% 확률
                    self._update_group_dynamics()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ 상호작용 처리 오류: {e}")
    
    def initiate_interaction(self, initiator: str, target: str, 
                           interaction_type: InteractionType, context: str) -> bool:
        """AI 간 상호작용 시작"""
        try:
            # 현재 감정 상태 확인
            emotion_before = self.emotion_states.get(initiator, EmotionState.CURIOSITY)
            
            # 상호작용 객체 생성
            interaction = AIInteraction(
                timestamp=time.time(),
                initiator=initiator,
                target=target,
                interaction_type=interaction_type,
                context=context,
                emotion_before=emotion_before,
                emotion_after=emotion_before,  # 일단 같게 설정, 나중에 업데이트
                success=False,
                outcome="",
                relationship_change=0.0
            )
            
            # 큐에 추가하여 백그라운드에서 처리
            self.interaction_queue.put(interaction)
            print(f"🤝 {initiator} → {target}: {interaction_type.value} 상호작용 시작")
            return True
            
        except Exception as e:
            print(f"❌ 상호작용 시작 실패: {e}")
            return False
    
    def _execute_interaction(self, interaction: AIInteraction):
        """실제 상호작용 실행"""
        try:
            # AI 엔진을 통한 상호작용 시뮬레이션
            if self.ai_engine:
                prompt = self._create_interaction_prompt(interaction)
                response = self.ai_engine.generate_response(prompt)
                
                # 응답 분석하여 결과 도출
                result = self._analyze_interaction_result(response, interaction)
                
                # 상호작용 결과 적용
                interaction.success = result['success']
                interaction.outcome = result['outcome']
                interaction.emotion_after = result['emotion_after']
                interaction.relationship_change = result['relationship_change']
                
                # 관계도 업데이트
                self._update_relationship(interaction.initiator, interaction.target, 
                                       interaction.relationship_change)
                
                # 감정 상태 업데이트
                self.emotion_states[interaction.initiator] = interaction.emotion_after
                self._propagate_emotion(interaction)
                
                # 히스토리에 저장
                self.interaction_history.append(interaction)
                self._save_interaction_to_db(interaction)
                
                print(f"✅ 상호작용 완료: {interaction.initiator} → {interaction.target}")
                print(f"   결과: {interaction.outcome}")
                
        except Exception as e:
            print(f"❌ 상호작용 실행 실패: {e}")
    
    def _create_interaction_prompt(self, interaction: AIInteraction) -> str:
        """상호작용을 위한 AI 프롬프트 생성"""
        # 스토리 설정 반영
        story_context = """
        세계관: 2157년 시공교란으로 모든 시대가 뒤섞인 혼돈의 세계
        당신은 차원 항해사의 동료 AI로서 다른 AI와 상호작용합니다.
        시대적 특징: 과거의 지혜와 미래의 기술이 공존하는 융합 문명
        """
        
        # 현재 관계도 확인
        current_relationship = self.get_relationship_score(interaction.initiator, interaction.target)
        
        prompt = f"""
        {story_context}
        
        상황: {interaction.context}
        상호작용 유형: {interaction.interaction_type.value}
        시작자: {interaction.initiator} (현재 감정: {interaction.emotion_before.value})
        대상: {interaction.target}
        현재 관계도: {current_relationship:.2f} (-1.0: 적대적, 0.0: 중립, +1.0: 우호적)
        
        이 상호작용의 결과를 다음 형식으로 예측해주세요:
        성공여부: [성공/실패]
        결과설명: [상세한 설명]
        감정변화: [새로운 감정]
        관계변화: [관계도 변화량, -0.5 ~ +0.5]
        """
        
        return prompt
    
    def _analyze_interaction_result(self, response: str, interaction: AIInteraction) -> Dict[str, Any]:
        """AI 응답을 분석하여 상호작용 결과 도출"""
        try:
            # 기본값 설정
            result = {
                'success': True,
                'outcome': "상호작용이 진행되었습니다.",
                'emotion_after': interaction.emotion_before,
                'relationship_change': 0.0
            }
            
            # 응답 파싱 (간단한 키워드 기반)
            if "실패" in response:
                result['success'] = False
            
            # 감정 변화 분석
            for emotion in EmotionState:
                if emotion.value in response:
                    result['emotion_after'] = emotion
                    break
            
            # 관계 변화 분석
            if "우호적" in response or "좋아" in response:
                result['relationship_change'] = random.uniform(0.1, 0.3)
            elif "적대적" in response or "싫어" in response:
                result['relationship_change'] = random.uniform(-0.3, -0.1)
            else:
                result['relationship_change'] = random.uniform(-0.1, 0.1)
            
            # 결과 설명 추출
            lines = response.split('\n')
            for line in lines:
                if "결과설명" in line:
                    result['outcome'] = line.split(':')[-1].strip()
                    break
            
            return result
            
        except Exception as e:
            print(f"⚠️ 응답 분석 실패: {e}")
            # 기본값 반환
            return {
                'success': True,
                'outcome': "상호작용이 진행되었습니다.",
                'emotion_after': interaction.emotion_before,
                'relationship_change': random.uniform(-0.1, 0.1)
            }
    
    def _update_relationship(self, ai1: str, ai2: str, change: float):
        """관계도 업데이트"""
        # 양방향 관계
        key1 = (ai1, ai2)
        key2 = (ai2, ai1)
        
        # 현재 관계도 가져오기
        current_score = self.relationship_matrix.get(key1, 0.0)
        new_score = max(-1.0, min(1.0, current_score + change))
        
        # 업데이트
        self.relationship_matrix[key1] = new_score
        self.relationship_matrix[key2] = new_score
        
        # 데이터베이스에 저장
        self._save_relationship_to_db(ai1, ai2, new_score)
    
    def _propagate_emotion(self, interaction: AIInteraction):
        """감정 전파 시스템"""
        # 강한 감정은 주변 AI들에게 영향을 줌
        strong_emotions = [EmotionState.JOY, EmotionState.ANGER, EmotionState.FEAR, EmotionState.EXCITEMENT]
        
        if interaction.emotion_after in strong_emotions:
            # 같은 그룹의 다른 AI들에게 감정 전파
            for group in self.active_groups.values():
                if interaction.initiator in group.members:
                    for member in group.members:
                        if member != interaction.initiator and random.random() < 0.3:  # 30% 확률
                            # 감정 전파 (약화된 형태로)
                            if interaction.emotion_after == EmotionState.JOY:
                                self.emotion_states[member] = EmotionState.HAPPINESS
                            elif interaction.emotion_after == EmotionState.ANGER:
                                self.emotion_states[member] = EmotionState.FRUSTRATION
                            elif interaction.emotion_after == EmotionState.FEAR:
                                self.emotion_states[member] = EmotionState.ANXIETY
                            elif interaction.emotion_after == EmotionState.EXCITEMENT:
                                self.emotion_states[member] = EmotionState.ENTHUSIASM
    
    def create_group(self, group_id: str, members: List[str], shared_goals: List[str] = None) -> bool:
        """새 그룹 생성"""
        try:
            if shared_goals is None:
                shared_goals = []
            
            group = GroupDynamics(
                group_id=group_id,
                members=members,
                group_mood=EmotionState.CURIOSITY,
                leadership_score={member: 0.0 for member in members},
                cooperation_level=0.5,
                conflict_level=0.0,
                formed_time=time.time(),
                last_activity=time.time(),
                shared_goals=shared_goals,
                group_achievements=[]
            )
            
            self.active_groups[group_id] = group
            self._save_group_to_db(group)
            
            print(f"👥 새 그룹 생성: {group_id} (멤버: {len(members)}명)")
            return True
            
        except Exception as e:
            print(f"❌ 그룹 생성 실패: {e}")
            return False
    
    def _update_group_dynamics(self):
        """그룹 다이나믹스 업데이트"""
        for group in self.active_groups.values():
            try:
                # 그룹 분위기 계산
                member_emotions = [self.emotion_states.get(member, EmotionState.CURIOSITY) 
                                 for member in group.members]
                group.group_mood = self._calculate_group_mood(member_emotions)
                
                # 협력 수준 계산
                cooperation_total = 0
                cooperation_count = 0
                
                for i, member1 in enumerate(group.members):
                    for member2 in group.members[i+1:]:
                        rel_score = self.get_relationship_score(member1, member2)
                        cooperation_total += max(0, rel_score)  # 긍정적 관계만
                        cooperation_count += 1
                
                if cooperation_count > 0:
                    group.cooperation_level = cooperation_total / cooperation_count
                
                # 갈등 수준 계산
                conflict_total = 0
                conflict_count = 0
                
                for i, member1 in enumerate(group.members):
                    for member2 in group.members[i+1:]:
                        rel_score = self.get_relationship_score(member1, member2)
                        conflict_total += max(0, -rel_score)  # 부정적 관계만
                        conflict_count += 1
                
                if conflict_count > 0:
                    group.conflict_level = conflict_total / conflict_count
                
                # 리더십 점수 업데이트 (상호작용 빈도 기반)
                for member in group.members:
                    interaction_count = sum(1 for interaction in self.interaction_history
                                          if interaction.initiator == member and 
                                          interaction.target in group.members)
                    group.leadership_score[member] = interaction_count * 0.1
                
                group.last_activity = time.time()
                self._save_group_to_db(group)
                
            except Exception as e:
                print(f"⚠️ 그룹 다이나믹스 업데이트 실패: {e}")
    
    def _calculate_group_mood(self, emotions: List[EmotionState]) -> EmotionState:
        """그룹 전체 분위기 계산"""
        if not emotions:
            return EmotionState.CURIOSITY
        
        # 감정별 가중치
        positive_emotions = [EmotionState.JOY, EmotionState.HAPPINESS, EmotionState.EXCITEMENT, 
                           EmotionState.ENTHUSIASM, EmotionState.CONFIDENCE]
        negative_emotions = [EmotionState.SADNESS, EmotionState.ANGER, EmotionState.FEAR, 
                           EmotionState.FRUSTRATION, EmotionState.ANXIETY]
        
        positive_count = sum(1 for emotion in emotions if emotion in positive_emotions)
        negative_count = sum(1 for emotion in emotions if emotion in negative_emotions)
        
        if positive_count > negative_count:
            return EmotionState.JOY
        elif negative_count > positive_count:
            return EmotionState.ANXIETY
        else:
            return EmotionState.CURIOSITY
    
    def get_relationship_score(self, ai1: str, ai2: str) -> float:
        """두 AI 간 관계도 조회"""
        key = (ai1, ai2)
        return self.relationship_matrix.get(key, 0.0)
    
    def get_group_status(self, group_id: str) -> Optional[GroupDynamics]:
        """그룹 상태 조회"""
        return self.active_groups.get(group_id)
    
    def _save_interaction_to_db(self, interaction: AIInteraction):
        """상호작용을 데이터베이스에 저장"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO interactions (
                        timestamp, initiator, target, interaction_type, context,
                        emotion_before, emotion_after, success, outcome, relationship_change
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.timestamp, interaction.initiator, interaction.target,
                    interaction.interaction_type.value, interaction.context,
                    interaction.emotion_before.value, interaction.emotion_after.value,
                    interaction.success, interaction.outcome, interaction.relationship_change
                ))
                conn.commit()
                
        except Exception as e:
            print(f"❌ 상호작용 저장 실패: {e}")
    
    def _save_relationship_to_db(self, ai1: str, ai2: str, score: float):
        """관계도를 데이터베이스에 저장"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO relationships (ai1, ai2, relationship_score, last_updated)
                    VALUES (?, ?, ?, ?)
                ''', (ai1, ai2, score, time.time()))
                conn.commit()
                
        except Exception as e:
            print(f"❌ 관계도 저장 실패: {e}")
    
    def _save_group_to_db(self, group: GroupDynamics):
        """그룹 정보를 데이터베이스에 저장"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO group_dynamics (
                        group_id, members, group_mood, leadership_scores,
                        cooperation_level, conflict_level, formed_time, last_activity,
                        shared_goals, group_achievements
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    group.group_id, json.dumps(group.members), group.group_mood.value,
                    json.dumps(group.leadership_score), group.cooperation_level,
                    group.conflict_level, group.formed_time, group.last_activity,
                    json.dumps(group.shared_goals), json.dumps(group.group_achievements)
                ))
                conn.commit()
                
        except Exception as e:
            print(f"❌ 그룹 정보 저장 실패: {e}")
    
    def display_interaction_menu(self):
        """상호작용 관리 메뉴 표시"""
        if not self.cursor_menu:
            print("⚠️ 커서 메뉴 시스템을 사용할 수 없습니다.")
            return
        
        try:
            menu_items = [
                ("1. 💫 AI 간 상호작용 시작", "두 AI 캐릭터 간의 상호작용을 시작합니다"),
                ("2. 👥 그룹 생성", "새로운 AI 그룹을 생성합니다"),
                ("3. 📊 관계도 확인", "AI들 간의 관계도를 확인합니다"),
                ("4. 🎭 감정 상태 확인", "모든 AI의 현재 감정 상태를 확인합니다"),
                ("5. 📈 그룹 다이나믹스", "활성 그룹들의 상태를 확인합니다"),
                ("6. 📜 상호작용 히스토리", "최근 상호작용 기록을 확인합니다"),
                ("7. 🔄 자동 상호작용 시작", "AI들이 자동으로 상호작용하도록 설정합니다"),
                ("0. 🚪 돌아가기", "이전 메뉴로 돌아갑니다")
            ]
            
            selected = self.cursor_menu.display_menu(
                title="🤖 AI 상호작용 시스템",
                items=menu_items,
                description="AI 캐릭터들 간의 상호작용을 관리하고 모니터링합니다."
            )
            
            if selected == 0:  # 1번 선택 (인덱스 0)
                self._start_ai_interaction()
            elif selected == 1:  # 2번 선택
                self._create_new_group()
            elif selected == 2:  # 3번 선택
                self._display_relationships()
            elif selected == 3:  # 4번 선택
                self._display_emotion_states()
            elif selected == 4:  # 5번 선택
                self._display_group_dynamics()
            elif selected == 5:  # 6번 선택
                self._display_interaction_history()
            elif selected == 6:  # 7번 선택
                self._start_auto_interactions()
            elif selected == 7:  # 0번 선택
                return
                
        except Exception as e:
            print(f"❌ 메뉴 표시 실패: {e}")
            input("\nEnter를 눌러 계속...")
    
    def _start_ai_interaction(self):
        """AI 간 상호작용 시작"""
        print("\n🤝 AI 간 상호작용 시작")
        print("=" * 50)
        
        try:
            # AI 캐릭터 목록 가져오기 (더미 데이터)
            available_ais = ["레이나", "세라핌", "쉐도우", "아르카나", "실버", "엠마"]
            
            # 시작자 선택
            print("상호작용을 시작할 AI를 선택하세요:")
            for i, ai in enumerate(available_ais, 1):
                print(f"{i}. {ai}")
            
            try:
                choice = int(input("선택 (1-6): "))
                if 1 <= choice <= len(available_ais):
                    initiator = available_ais[choice - 1]
                else:
                    print("❌ 잘못된 선택입니다.")
                    return
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return
            
            # 대상 선택
            targets = [ai for ai in available_ais if ai != initiator]
            print(f"\n{initiator}이(가) 상호작용할 대상을 선택하세요:")
            for i, ai in enumerate(targets, 1):
                print(f"{i}. {ai}")
            
            try:
                choice = int(input("선택: "))
                if 1 <= choice <= len(targets):
                    target = targets[choice - 1]
                else:
                    print("❌ 잘못된 선택입니다.")
                    return
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return
            
            # 상호작용 타입 선택
            interaction_types = list(InteractionType)
            print(f"\n상호작용 타입을 선택하세요:")
            for i, itype in enumerate(interaction_types, 1):
                print(f"{i}. {itype.value}")
            
            try:
                choice = int(input("선택: "))
                if 1 <= choice <= len(interaction_types):
                    interaction_type = interaction_types[choice - 1]
                else:
                    print("❌ 잘못된 선택입니다.")
                    return
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return
            
            # 상황 입력
            context = input("\n상호작용 상황을 입력하세요: ").strip()
            if not context:
                context = f"{interaction_type.value} 상호작용"
            
            # 상호작용 시작
            success = self.initiate_interaction(initiator, target, interaction_type, context)
            
            if success:
                print(f"\n✅ {initiator} → {target} 상호작용이 시작되었습니다!")
                print("💭 백그라운드에서 처리 중...")
                time.sleep(2)  # 처리 시간 시뮬레이션
                print("🎉 상호작용이 완료되었습니다!")
            else:
                print("❌ 상호작용 시작에 실패했습니다.")
            
        except Exception as e:
            print(f"❌ 상호작용 시작 실패: {e}")
        
        input("\nEnter를 눌러 계속...")
    
    def _create_new_group(self):
        """새 그룹 생성"""
        print("\n👥 새 그룹 생성")
        print("=" * 50)
        
        try:
            group_id = input("그룹 이름을 입력하세요: ").strip()
            if not group_id:
                print("❌ 그룹 이름을 입력해주세요.")
                return
            
            # AI 선택
            available_ais = ["레이나", "세라핌", "쉐도우", "아르카나", "실버", "엠마"]
            print("\n그룹 멤버를 선택하세요 (최소 2명):")
            selected_members = []
            
            for ai in available_ais:
                choice = input(f"{ai}을(를) 추가하시겠습니까? (y/n): ").strip().lower()
                if choice in ['y', 'yes', 'ㅇ']:
                    selected_members.append(ai)
            
            if len(selected_members) < 2:
                print("❌ 최소 2명의 멤버가 필요합니다.")
                return
            
            # 공동 목표 입력
            goals = []
            print("\n공동 목표를 입력하세요 (빈 줄 입력시 종료):")
            while True:
                goal = input("목표: ").strip()
                if not goal:
                    break
                goals.append(goal)
            
            # 그룹 생성
            success = self.create_group(group_id, selected_members, goals)
            
            if success:
                print(f"\n✅ 그룹 '{group_id}' 생성 완료!")
                print(f"멤버: {', '.join(selected_members)}")
                if goals:
                    print(f"목표: {', '.join(goals)}")
            else:
                print("❌ 그룹 생성에 실패했습니다.")
            
        except Exception as e:
            print(f"❌ 그룹 생성 실패: {e}")
        
        input("\nEnter를 눌러 계속...")
    
    def _display_relationships(self):
        """관계도 표시"""
        print("\n📊 AI 간 관계도")
        print("=" * 50)
        
        if not self.relationship_matrix:
            print("📝 아직 관계 데이터가 없습니다.")
        else:
            for (ai1, ai2), score in self.relationship_matrix.items():
                if ai1 < ai2:  # 중복 방지
                    status = "😍 우호적" if score > 0.3 else "😠 적대적" if score < -0.3 else "😐 중립적"
                    print(f"{ai1} ↔ {ai2}: {score:+.2f} {status}")
        
        input("\nEnter를 눌러 계속...")
    
    def _display_emotion_states(self):
        """감정 상태 표시"""
        print("\n🎭 AI 감정 상태")
        print("=" * 50)
        
        if not self.emotion_states:
            print("📝 아직 감정 데이터가 없습니다.")
        else:
            for ai, emotion in self.emotion_states.items():
                emotion_icon = self._get_emotion_icon(emotion)
                print(f"{ai}: {emotion_icon} {emotion.value}")
        
        input("\nEnter를 눌러 계속...")
    
    def _get_emotion_icon(self, emotion: EmotionState) -> str:
        """감정에 맞는 아이콘 반환"""
        emotion_icons = {
            EmotionState.JOY: "😄", EmotionState.HAPPINESS: "😊", EmotionState.EXCITEMENT: "🤩",
            EmotionState.SADNESS: "😢", EmotionState.ANGER: "😠", EmotionState.FEAR: "😨",
            EmotionState.LOVE: "🥰", EmotionState.CURIOSITY: "🤔", EmotionState.SURPRISE: "😲"
        }
        return emotion_icons.get(emotion, "😐")
    
    def _display_group_dynamics(self):
        """그룹 다이나믹스 표시"""
        print("\n📈 그룹 다이나믹스")
        print("=" * 50)
        
        if not self.active_groups:
            print("📝 활성 그룹이 없습니다.")
        else:
            for group_id, group in self.active_groups.items():
                print(f"\n🏷️ 그룹: {group_id}")
                print(f"👥 멤버: {', '.join(group.members)}")
                print(f"🎭 분위기: {group.group_mood.value}")
                print(f"🤝 협력도: {group.cooperation_level:.2f}")
                print(f"⚔️ 갈등도: {group.conflict_level:.2f}")
                
                # 리더십 점수
                leader = max(group.leadership_score, key=group.leadership_score.get)
                print(f"👑 리더: {leader} ({group.leadership_score[leader]:.1f}점)")
                
                if group.shared_goals:
                    print(f"🎯 목표: {', '.join(group.shared_goals)}")
        
        input("\nEnter를 눌러 계속...")
    
    def _display_interaction_history(self):
        """상호작용 히스토리 표시"""
        print("\n📜 상호작용 히스토리")
        print("=" * 50)
        
        if not self.interaction_history:
            print("📝 상호작용 기록이 없습니다.")
        else:
            # 최근 10개만 표시
            recent_interactions = self.interaction_history[-10:]
            for interaction in recent_interactions:
                timestamp = time.strftime("%H:%M:%S", time.localtime(interaction.timestamp))
                status = "✅" if interaction.success else "❌"
                print(f"{timestamp} {status} {interaction.initiator} → {interaction.target}")
                print(f"   타입: {interaction.interaction_type.value}")
                print(f"   결과: {interaction.outcome}")
                print(f"   관계변화: {interaction.relationship_change:+.2f}")
                print()
        
        input("\nEnter를 눌러 계속...")
    
    def _start_auto_interactions(self):
        """자동 상호작용 시작"""
        print("\n🔄 자동 상호작용 모드")
        print("=" * 50)
        print("AI들이 자동으로 상호작용을 시작합니다...")
        print("(Ctrl+C로 중단 가능)")
        
        try:
            available_ais = ["레이나", "세라핌", "쉐도우", "아르카나", "실버", "엠마"]
            interaction_types = list(InteractionType)
            
            for i in range(10):  # 10번의 자동 상호작용
                # 랜덤 AI 선택
                initiator = random.choice(available_ais)
                target = random.choice([ai for ai in available_ais if ai != initiator])
                interaction_type = random.choice(interaction_types)
                
                contexts = [
                    "우연한 만남에서",
                    "전투 중에",
                    "휴식 시간에",
                    "어려운 상황에서",
                    "축하하는 자리에서"
                ]
                context = random.choice(contexts)
                
                print(f"{i+1}/10: {initiator} → {target} ({interaction_type.value})")
                
                self.initiate_interaction(initiator, target, interaction_type, context)
                time.sleep(1)  # 1초 간격
            
            print("\n🎉 자동 상호작용 완료!")
            
        except KeyboardInterrupt:
            print("\n⏹️ 자동 상호작용이 중단되었습니다.")
        except Exception as e:
            print(f"❌ 자동 상호작용 실패: {e}")
        
        input("\nEnter를 눌러 계속...")
    
    def test_emotion_interactions(self):
        """감정 상호작용 테스트"""
        print("\n💭 감정 상호작용 테스트")
        print("=" * 50)
        
        # 테스트 AI들
        test_ais = ["Alice", "Bob", "Charlie"]
        
        # 다양한 감정 상태 설정
        emotions = [EmotionState.HAPPINESS, EmotionState.ANGER, EmotionState.CURIOSITY]
        
        for i, ai in enumerate(test_ais):
            self.emotion_states[ai] = emotions[i]
            print(f"🎭 {ai}: {emotions[i].value}")
        
        print("\n상호작용 시뮬레이션:")
        
        # 각 AI 간 상호작용 테스트
        for i in range(len(test_ais)):
            for j in range(i + 1, len(test_ais)):
                ai1, ai2 = test_ais[i], test_ais[j]
                
                # 상호작용 실행
                result = self.initiate_interaction(
                    ai1, ai2, InteractionType.CONVERSATION, "감정 테스트"
                )
                
                if result and result.get('success'):
                    relationship = self.get_relationship_score(ai1, ai2)
                    print(f"✅ {ai1} ↔ {ai2}: 관계도 {relationship:.2f}")
                else:
                    print(f"❌ {ai1} ↔ {ai2}: 상호작용 실패")
        
        print(f"\n📊 총 상호작용 횟수: {len(self.interaction_history)}")
    
    def test_group_dynamics(self):
        """그룹 다이나믹스 테스트"""
        print("\n👥 그룹 다이나믹스 테스트")
        print("=" * 50)
        
        # 테스트 그룹 생성
        group_members = ["Alpha", "Beta", "Gamma", "Delta"]
        group_goals = ["던전 클리어", "보물 획득", "팀워크 향상"]
        
        print(f"그룹 생성: {', '.join(group_members)}")
        
        group_id = self.create_group("TestGroup", group_members, group_goals)
        
        if group_id in self.active_groups:
            group = self.active_groups[group_id]
            
            print(f"✅ 그룹 '{group_id}' 생성 완료")
            print(f"   멤버: {', '.join(group.members)}")
            print(f"   그룹 분위기: {group.group_mood.value}")
            print(f"   협력 수준: {group.cooperation_level:.2f}")
            print(f"   갈등 수준: {group.conflict_level:.2f}")
            print(f"   목표: {', '.join(group.shared_goals)}")
            
            # 리더십 스코어 표시
            print("\n리더십 스코어:")
            for member, score in group.leadership_scores.items():
                print(f"   {member}: {score:.2f}")
            
            # 그룹 내 상호작용 시뮬레이션
            print("\n그룹 내 상호작용 시뮬레이션:")
            for _ in range(3):
                member1 = random.choice(group_members)
                member2 = random.choice([m for m in group_members if m != member1])
                
                result = self.initiate_interaction(
                    member1, member2, InteractionType.COOPERATION, "그룹 활동"
                )
                
                if result and result.get('success'):
                    print(f"   ✅ {member1} → {member2}: 협력 성공")
                else:
                    print(f"   ❌ {member1} → {member2}: 협력 실패")
            
            # 업데이트된 그룹 상태
            self.update_group_dynamics(group_id)
            updated_group = self.active_groups[group_id]
            
            print(f"\n업데이트된 그룹 상태:")
            print(f"   협력 수준: {updated_group.cooperation_level:.2f}")
            print(f"   갈등 수준: {updated_group.conflict_level:.2f}")
            
        else:
            print("❌ 그룹 생성 실패")
    
    def show_interaction_menu(self):
        """상호작용 메뉴 표시"""
        while True:
            print("\n💬 AI 상호작용 시스템 메뉴")
            print("=" * 50)
            print("1. 감정 상호작용 테스트")
            print("2. 그룹 다이나믹스 테스트")
            print("3. 관계도 매트릭스 보기")
            print("4. 상호작용 히스토리")
            print("5. 활성 그룹 정보")
            print("6. 실시간 상호작용 시작")
            print("0. 돌아가기")
            
            choice = input("\n선택하세요: ").strip()
            
            if choice == "1":
                self.test_emotion_interactions()
            elif choice == "2":
                self.test_group_dynamics()
            elif choice == "3":
                self._show_relationship_matrix()
            elif choice == "4":
                self._show_interaction_history()
            elif choice == "5":
                self._show_active_groups()
            elif choice == "6":
                self.start_auto_interactions()
            elif choice == "0":
                break
            else:
                print("❌ 잘못된 선택입니다.")
            
            input("\n계속하려면 Enter를 누르세요...")
    
    def _show_relationship_matrix(self):
        """관계도 매트릭스 표시"""
        print("\n💕 관계도 매트릭스")
        print("=" * 50)
        
        if not self.relationship_matrix:
            print("📭 관계 데이터가 없습니다.")
            return
        
        for (ai1, ai2), score in self.relationship_matrix.items():
            status = "❤️ 친밀" if score >= 0.7 else "👍 좋음" if score >= 0.3 else "😐 보통" if score >= -0.3 else "👎 나쁨" if score >= -0.7 else "💔 적대"
            print(f"{ai1} ↔ {ai2}: {score:+.2f} {status}")
    
    def _show_interaction_history(self):
        """상호작용 히스토리 표시"""
        print("\n📜 상호작용 히스토리")
        print("=" * 50)
        
        if not self.interaction_history:
            print("📭 상호작용 기록이 없습니다.")
            return
        
        for interaction in self.interaction_history[-10:]:  # 최근 10개
            timestamp = time.strftime("%H:%M:%S", time.localtime(interaction.timestamp))
            status = "✅" if interaction.success else "❌"
            print(f"{timestamp} {status} {interaction.initiator} → {interaction.target}")
            print(f"   유형: {interaction.interaction_type.value}")
            print(f"   결과: {interaction.outcome}")
            if interaction.relationship_change != 0:
                change = f"+{interaction.relationship_change:.2f}" if interaction.relationship_change > 0 else f"{interaction.relationship_change:.2f}"
                print(f"   관계 변화: {change}")
            print()
    
    def _show_active_groups(self):
        """활성 그룹 정보 표시"""
        print("\n👥 활성 그룹 정보")
        print("=" * 50)
        
        if not self.active_groups:
            print("📭 활성 그룹이 없습니다.")
            return
        
        for group_id, group in self.active_groups.items():
            print(f"🏠 그룹: {group_id}")
            print(f"   멤버: {', '.join(group.members)}")
            print(f"   분위기: {group.group_mood.value}")
            print(f"   협력/갈등: {group.cooperation_level:.2f}/{group.conflict_level:.2f}")
            print(f"   목표: {', '.join(group.shared_goals)}")
            
            # 최고 리더십
            if group.leadership_scores:
                leader = max(group.leadership_scores.items(), key=lambda x: x[1])
                print(f"   리더: {leader[0]} ({leader[1]:.2f})")
            
            print()

    def shutdown(self):
        """시스템 종료"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        print("🔄 AI 상호작용 시스템 종료")

# 전역 인스턴스
interaction_system = AIInteractionSystem()

def test_ai_interaction_system():
    """AI 상호작용 시스템 테스트"""
    print("🧪 AI 상호작용 시스템 테스트")
    
    # 테스트 AI들
    test_ais = ["테스트A", "테스트B", "테스트C"]
    
    # 초기 감정 설정
    for ai in test_ais:
        interaction_system.emotion_states[ai] = EmotionState.CURIOSITY
    
    # 그룹 생성 테스트
    interaction_system.create_group("테스트그룹", test_ais, ["협력하기", "문제해결"])
    
    # 상호작용 테스트
    interaction_system.initiate_interaction(
        "테스트A", "테스트B", InteractionType.COOPERATION, "테스트 상황"
    )
    
    # 잠시 대기
    time.sleep(2)
    
    # 결과 확인
    print("\n📊 테스트 결과:")
    print(f"관계도: {interaction_system.get_relationship_score('테스트A', '테스트B'):.2f}")
    print(f"상호작용 수: {len(interaction_system.interaction_history)}")
    
    print("✅ 테스트 완료!")

if __name__ == "__main__":
    test_ai_interaction_system()
