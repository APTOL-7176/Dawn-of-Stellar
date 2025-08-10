#!/usr/bin/env python3
"""
AI 캐릭터 데이터베이스 관리 시스템
각 AI 캐릭터별로 독립적인 SQLite 데이터베이스를 관리
"""

import sqlite3
import json
import os
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import time

# 데이터베이스 디렉토리 (새로운 폴더 구조)
DB_DIR = "ai_character_data/memories"
PRESETS_DIR = "character_presets"
SHARED_DATA_DIR = "ai_character_data/interactions"
PARTY_SAVE_DIR = "ai_character_data/party_saves"

# 디렉토리 생성
for directory in [DB_DIR, PRESETS_DIR, SHARED_DATA_DIR]:
    os.makedirs(directory, exist_ok=True)

@dataclass
class LearningEvent:
    """학습 이벤트 데이터 클래스"""
    timestamp: str
    event_type: str  # 'combat', 'dialogue', 'exploration', 'decision'
    context: str
    action_taken: str
    outcome: str
    feedback_score: float  # -1.0 ~ 1.0
    emotional_weight: float  # 0.0 ~ 1.0

@dataclass
class RelationshipData:
    """관계 데이터 클래스"""
    target_name: str
    relationship_type: str  # 'player', 'ai_companion', 'npc'
    trust_level: float  # 0.0 ~ 1.0
    friendship_points: int
    last_interaction: str
    memorable_events: List[str]

@dataclass
class GameKnowledge:
    """게임 지식 데이터 클래스"""
    category: str  # 'monster', 'item', 'strategy', 'location'
    subject: str
    knowledge: str
    confidence_level: float  # 0.0 ~ 1.0
    last_updated: str

@dataclass
class BehavioralPattern:
    """행동 패턴 데이터 클래스"""
    situation_type: str
    action_pattern: str
    success_rate: float
    usage_count: int
    last_used: str

@dataclass
class EmotionalState:
    """감정 상태 데이터 클래스"""
    timestamp: str
    emotion_type: str  # 'happy', 'excited', 'worried', 'angry', 'sad'
    intensity: float  # 0.0 ~ 1.0
    trigger_event: str
    duration: int  # 분 단위

class AICharacterDatabase:
    """AI 캐릭터별 데이터베이스 관리"""
    
    def __init__(self, character_name: str):
        self.character_name = character_name
        self.db_path = os.path.join(DB_DIR, f"ai_memory_{character_name}.db")
        self.lock = threading.Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 학습 이벤트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    context TEXT,
                    action_taken TEXT,
                    outcome TEXT,
                    feedback_score REAL,
                    emotional_weight REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 관계 데이터 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_name TEXT UNIQUE NOT NULL,
                    relationship_type TEXT NOT NULL,
                    trust_level REAL DEFAULT 0.5,
                    friendship_points INTEGER DEFAULT 0,
                    last_interaction TEXT,
                    memorable_events TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 게임 지식 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    knowledge TEXT,
                    confidence_level REAL DEFAULT 0.5,
                    last_updated TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 행동 패턴 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS behavioral_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    situation_type TEXT NOT NULL,
                    action_pattern TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.5,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 감정 상태 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotional_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    emotion_type TEXT NOT NULL,
                    intensity REAL NOT NULL,
                    trigger_event TEXT,
                    duration INTEGER DEFAULT 60,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON learning_events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON learning_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_category ON game_knowledge(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_situation ON behavioral_patterns(situation_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_emotions_type ON emotional_states(emotion_type)')
            
            conn.commit()
    
    def add_learning_event(self, event: LearningEvent):
        """학습 이벤트 추가"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO learning_events 
                    (timestamp, event_type, context, action_taken, outcome, feedback_score, emotional_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.timestamp, event.event_type, event.context,
                    event.action_taken, event.outcome, event.feedback_score, event.emotional_weight
                ))
                conn.commit()
    
    def update_relationship(self, relationship: RelationshipData):
        """관계 데이터 업데이트"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                memorable_events_json = json.dumps(relationship.memorable_events, ensure_ascii=False)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO relationships 
                    (target_name, relationship_type, trust_level, friendship_points, 
                     last_interaction, memorable_events, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    relationship.target_name, relationship.relationship_type,
                    relationship.trust_level, relationship.friendship_points,
                    relationship.last_interaction, memorable_events_json,
                    datetime.datetime.now().isoformat()
                ))
                conn.commit()
    
    def add_game_knowledge(self, knowledge: GameKnowledge):
        """게임 지식 추가"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO game_knowledge 
                    (category, subject, knowledge, confidence_level, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    knowledge.category, knowledge.subject, knowledge.knowledge,
                    knowledge.confidence_level, knowledge.last_updated
                ))
                conn.commit()
    
    def update_behavioral_pattern(self, pattern: BehavioralPattern):
        """행동 패턴 업데이트"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO behavioral_patterns 
                    (situation_type, action_pattern, success_rate, usage_count, last_used, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    pattern.situation_type, pattern.action_pattern,
                    pattern.success_rate, pattern.usage_count, pattern.last_used,
                    datetime.datetime.now().isoformat()
                ))
                conn.commit()
    
    def add_emotional_state(self, emotion: EmotionalState):
        """감정 상태 추가"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO emotional_states 
                    (timestamp, emotion_type, intensity, trigger_event, duration)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    emotion.timestamp, emotion.emotion_type, emotion.intensity,
                    emotion.trigger_event, emotion.duration
                ))
                conn.commit()
    
    def get_recent_learning_events(self, limit: int = 20) -> List[Dict]:
        """최근 학습 이벤트 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM learning_events 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_relationship(self, target_name: str) -> Optional[Dict]:
        """특정 대상과의 관계 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM relationships WHERE target_name = ?
            ''', (target_name,))
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                relationship = dict(zip(columns, row))
                # JSON 문자열을 리스트로 변환
                if relationship['memorable_events']:
                    relationship['memorable_events'] = json.loads(relationship['memorable_events'])
                else:
                    relationship['memorable_events'] = []
                return relationship
            return None
    
    def get_knowledge_by_category(self, category: str) -> List[Dict]:
        """카테고리별 지식 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM game_knowledge 
                WHERE category = ? 
                ORDER BY confidence_level DESC
            ''', (category,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_behavioral_patterns(self, situation_type: str = None) -> List[Dict]:
        """행동 패턴 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if situation_type:
                cursor.execute('''
                    SELECT * FROM behavioral_patterns 
                    WHERE situation_type = ? 
                    ORDER BY success_rate DESC
                ''', (situation_type,))
            else:
                cursor.execute('''
                    SELECT * FROM behavioral_patterns 
                    ORDER BY success_rate DESC
                ''')
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_current_emotional_state(self) -> Optional[Dict]:
        """현재 감정 상태 조회 (가장 최근)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM emotional_states 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """데이터베이스 통계 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # 학습 이벤트 수
            cursor.execute('SELECT COUNT(*) FROM learning_events')
            stats['total_learning_events'] = cursor.fetchone()[0]
            
            # 관계 수
            cursor.execute('SELECT COUNT(*) FROM relationships')
            stats['total_relationships'] = cursor.fetchone()[0]
            
            # 지식 수
            cursor.execute('SELECT COUNT(*) FROM game_knowledge')
            stats['total_knowledge_items'] = cursor.fetchone()[0]
            
            # 행동 패턴 수
            cursor.execute('SELECT COUNT(*) FROM behavioral_patterns')
            stats['total_behavioral_patterns'] = cursor.fetchone()[0]
            
            # 감정 기록 수
            cursor.execute('SELECT COUNT(*) FROM emotional_states')
            stats['total_emotional_records'] = cursor.fetchone()[0]
            
            # 평균 신뢰도
            cursor.execute('SELECT AVG(trust_level) FROM relationships')
            avg_trust = cursor.fetchone()[0]
            stats['average_trust_level'] = avg_trust if avg_trust else 0.0
            
            return stats

class AICharacterPresetManager:
    """AI 캐릭터 프리셋 관리"""
    
    def __init__(self):
        self.presets_dir = PRESETS_DIR
    
    def save_character_preset(self, character_data: Dict[str, Any]):
        """캐릭터 프리셋 저장"""
        character_name = character_data['basic_info']['name']
        preset_file = os.path.join(self.presets_dir, f"preset_{character_name}.json")
        
        # AI 프로필에 데이터베이스 경로 추가
        if 'ai_profile' not in character_data:
            character_data['ai_profile'] = {}
        
        character_data['ai_profile']['database_file'] = f"ai_memory_{character_name}.db"
        
        with open(preset_file, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
    
    def load_character_preset(self, character_name: str) -> Optional[Dict[str, Any]]:
        """캐릭터 프리셋 로드"""
        preset_file = os.path.join(self.presets_dir, f"preset_{character_name}.json")
        
        if os.path.exists(preset_file):
            with open(preset_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_available_presets(self) -> List[str]:
        """사용 가능한 프리셋 목록"""
        presets = []
        for file in os.listdir(self.presets_dir):
            if file.startswith("preset_") and file.endswith(".json"):
                name = file[7:-5]  # "preset_" 제거하고 ".json" 제거
                presets.append(name)
        return presets
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """모든 캐릭터 프리셋을 로드해서 반환"""
        characters = []
        for preset_name in self.list_available_presets():
            character_data = self.load_character_preset(preset_name)
            if character_data:
                characters.append(character_data)
        return characters
    
    def create_default_ai_profile(self, name: str, class_name: str, gender: str, personality_type: str) -> Dict[str, Any]:
        """기본 AI 프로필 생성"""
        # 성격 타입별 기본 설정
        personality_configs = {
            "용감한_리더": {
                "traits": ["용감함", "책임감", "정의감"],
                "interests": ["전술", "무기_연구", "파티_보호"],
                "fears": ["동료_손실", "책임_회피", "불의"],
                "motivations": ["모두를_지키고_싶음", "강해지고_싶음"],
                "speech_style": "격식있는_말투"
            },
            "신중한_전략가": {
                "traits": ["신중함", "지혜", "분석력"],
                "interests": ["전략_연구", "상황_분석", "효율성"],
                "fears": ["실수", "성급한_판단", "예측_실패"],
                "motivations": ["완벽한_계획", "모든_상황_대비"],
                "speech_style": "정중한_말투"
            },
            "활발한_모험가": {
                "traits": ["호기심", "활발함", "모험심"],
                "interests": ["새로운_발견", "탐험", "재미있는_경험"],
                "fears": ["지루함", "제약", "단조로움"],
                "motivations": ["새로운_경험", "즐거운_모험"],
                "speech_style": "친근한_말투"
            },
            "냉정한_완벽주의자": {
                "traits": ["완벽함", "냉정함", "효율성"],
                "interests": ["최적화", "완벽한_실행", "효율_개선"],
                "fears": ["실패", "비효율", "완벽하지_못함"],
                "motivations": ["완벽한_결과", "최고_효율"],
                "speech_style": "차가운_말투"
            },
            "따뜻한_치유자": {
                "traits": ["공감", "따뜻함", "치유"],
                "interests": ["아군_돌봄", "치유술", "평화"],
                "fears": ["아군_고통", "치유_실패", "갈등"],
                "motivations": ["모두의_행복", "평화로운_여행"],
                "speech_style": "부드러운_말투"
            },
            "장난기_많은_트릭스터": {
                "traits": ["장난기", "창의성", "유머"],
                "interests": ["재미있는_전술", "놀라운_아이디어", "유머"],
                "fears": ["지루함", "뻔한_상황", "진부함"],
                "motivations": ["재미있는_경험", "창의적_해결"],
                "speech_style": "유쾌한_말투"
            }
        }
        
        config = personality_configs.get(personality_type, personality_configs["용감한_리더"])
        
        return {
            "basic_info": {
                "name": name,
                "class": class_name,
                "gender": gender,
                "age": 20 + hash(name) % 15,  # 20-34 랜덤 나이
                "personality_type": personality_type,
                "speech_style": config["speech_style"]
            },
            "ai_profile": {
                "core_personality": {
                    "traits": config["traits"],
                    "interests": config["interests"],
                    "fears": config["fears"],
                    "motivations": config["motivations"]
                },
                "professional_knowledge": {
                    "expertise": [f"{class_name}_전술", f"{class_name}_기술"],
                    "preferred_skills": [],  # 게임에서 동적으로 학습
                    "combat_style": f"{class_name}_스타일",
                    "weakness_analysis": []  # 게임에서 동적으로 학습
                },
                "relationship_data": {
                    "trust_level": 0.5,
                    "friendship_points": 0,
                    "memorable_events": [],
                    "communication_history": []
                },
                "database_file": f"ai_memory_{name}.db"
            },
            "learning_data": {
                "learning_sessions": 0,
                "experience_points": 0,
                "skill_development": {},
                "behavioral_patterns": {}
            }
        }

# 글로벌 매니저 인스턴스
ai_database_manager = {}
preset_manager = AICharacterPresetManager()

def get_ai_database(character_name: str) -> AICharacterDatabase:
    """AI 캐릭터 데이터베이스 반환 (싱글톤 패턴)"""
    if character_name not in ai_database_manager:
        ai_database_manager[character_name] = AICharacterDatabase(character_name)
    return ai_database_manager[character_name]

def create_ai_character_with_database(name: str, class_name: str, gender: str, personality_type: str):
    """AI 캐릭터와 데이터베이스를 함께 생성"""
    # 1. 데이터베이스 생성
    db = get_ai_database(name)
    
    # 2. 프리셋 생성
    character_data = preset_manager.create_default_ai_profile(name, class_name, gender, personality_type)
    preset_manager.save_character_preset(character_data)
    
    # 3. 초기 학습 데이터 추가
    initial_event = LearningEvent(
        timestamp=datetime.datetime.now().isoformat(),
        event_type="creation",
        context=f"{name}이(가) {class_name}로 창조되었습니다",
        action_taken="캐릭터_생성",
        outcome="성공",
        feedback_score=1.0,
        emotional_weight=0.8
    )
    db.add_learning_event(initial_event)
    
    # 4. 플레이어와의 초기 관계 설정
    initial_relationship = RelationshipData(
        target_name="플레이어",
        relationship_type="player",
        trust_level=0.5,
        friendship_points=0,
        last_interaction=datetime.datetime.now().isoformat(),
        memorable_events=[f"{name}과 플레이어의 첫 만남"]
    )
    db.update_relationship(initial_relationship)
    
    print(f"✅ {name} ({class_name}, {gender}, {personality_type}) AI 캐릭터와 데이터베이스가 생성되었습니다!")
    return character_data, db

# 테스트 함수
def test_ai_database_system():
    """AI 데이터베이스 시스템 테스트"""
    print("🧪 AI 데이터베이스 시스템 테스트 시작!")
    
    # 테스트 캐릭터 생성
    test_characters = [
        ("레이나", "전사", "female", "용감한_리더"),
        ("아르카나", "아크메이지", "female", "신중한_전략가"),
        ("실버", "궁수", "male", "냉정한_완벽주의자")
    ]
    
    for name, class_name, gender, personality in test_characters:
        character_data, db = create_ai_character_with_database(name, class_name, gender, personality)
        
        # 테스트 데이터 추가
        db.add_learning_event(LearningEvent(
            timestamp=datetime.datetime.now().isoformat(),
            event_type="combat",
            context="첫 번째 전투 경험",
            action_taken="기본_공격_사용",
            outcome="승리",
            feedback_score=0.8,
            emotional_weight=0.6
        ))
        
        # 통계 출력
        stats = db.get_statistics()
        print(f"📊 {name} 통계: {stats}")
    
    print("✅ 테스트 완료!")

if __name__ == "__main__":
    test_ai_database_system()
