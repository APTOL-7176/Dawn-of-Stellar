#!/usr/bin/env python3
"""
🌟 게임 AI 멀티플레이 시스템 - 클래식 모드의 완벽한 상위호환!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ 특징:
- AI 동료들과 함께하는 진짜 멀티플레이 경험
- 캐릭터별 독립적인 성격, 기억, 학습 시스템
- 실시간 게임 상호작용과 전략적 AI 플레이
- 언어모델 기반 자연스러운 대화
- 캐릭터 프리셋에 AI 정보 완전 통합
"""

import os
import json
import sqlite3
import random
import asyncio
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import requests
from dataclasses import dataclass, asdict

# 게임 시스템 임포트
try:
    from game.character import Character
    from game.auto_party_builder import AutoPartyBuilder
    from game.input_utils import KeyboardInput
    from config import game_config
except ImportError:
    # 개발 환경에서 테스트용
    import sys
    sys.path.append('.')
    
    # 더미 클래스들 (게임 시스템이 없을 때 사용)
    class Character:
        def __init__(self, name, character_class):
            self.name = name
            self.character_class = character_class
            self.level = 1
            self.current_hp = 100
            self.max_hp = 100
            self.physical_attack = 10
            self.magic_attack = 10
            self.physical_defense = 8
            self.magic_defense = 8
            self.speed = 5
            self.luck = 5
    
    class AutoPartyBuilder:
        def create_balanced_party(self, party_size=4):
            return [
                Character("테스트전사", "전사"),
                Character("테스트마법사", "아크메이지"),
                Character("테스트성기사", "성기사"),
                Character("테스트바드", "바드")
            ][:party_size]
    
    class KeyboardInput:
        def get_key_input(self):
            return input()
    
    game_config = {"ai_enabled": True}

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BRIGHT_RED = '\033[91m\033[1m'
BRIGHT_GREEN = '\033[92m\033[1m'
BRIGHT_YELLOW = '\033[93m\033[1m'
BRIGHT_BLUE = '\033[94m\033[1m'
BRIGHT_MAGENTA = '\033[95m\033[1m'
BRIGHT_CYAN = '\033[96m\033[1m'
BRIGHT_WHITE = '\033[97m\033[1m'

@dataclass
class AIPersonality:
    """AI 캐릭터 성격 데이터"""
    # 기본 정보
    name: str
    job: str
    gender: str
    age: int
    
    # 성격 특성
    personality_type: str  # 친근함, 냉정함, 열정적, 신중함, 장난스러움
    speech_style: str     # 격식있는, 친근한, 귀여운, 쿨한, 열정적인
    hobby: str           # 취미
    fear: str            # 두려워하는 것
    dream: str           # 꿈/목표
    
    # 게임 관련 성향
    combat_preference: str    # 공격적, 방어적, 지원적, 전략적
    risk_tolerance: str      # 신중함, 보통, 모험적, 무모함
    teamwork_style: str      # 리더십, 협력, 독립적, 추종
    learning_style: str      # 빠른학습, 꾸준함, 실험적, 보수적
    
    # AI 특화 정보
    interests: List[str]     # 게임 내 관심사
    memory_weight: float     # 기억 가중치 (0.0~1.0)
    creativity_level: int    # 창의성 수준 (1~10)
    social_level: int        # 사회성 수준 (1~10)

class AICharacterDatabase:
    """캐릭터별 독립적인 AI 데이터베이스"""
    
    def __init__(self, character_name: str):
        self.character_name = character_name
        self.db_path = f"ai_memory_{character_name}.db"
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기본 정보 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_info (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # 성격 정보 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personality_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personality_type TEXT,
                    speech_style TEXT,
                    combat_preference TEXT,
                    risk_tolerance TEXT,
                    teamwork_style TEXT,
                    learning_style TEXT,
                    interests TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 게임 이벤트 학습 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    event_data TEXT,
                    emotional_impact REAL,
                    learned_pattern TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 대화 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context TEXT,
                    user_input TEXT,
                    ai_response TEXT,
                    satisfaction_score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 관계 정보 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_character TEXT,
                    relationship_type TEXT,
                    affection_level REAL,
                    trust_level REAL,
                    shared_experiences INT DEFAULT 0,
                    last_interaction TIMESTAMP
                )
            ''')
            
            # 스킬/전략 학습 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    situation_type TEXT,
                    strategy_used TEXT,
                    success_rate REAL,
                    usage_count INT DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def save_personality(self, personality: AIPersonality):
        """성격 정보 저장"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # JSON으로 직렬화
            personality_json = json.dumps(asdict(personality), ensure_ascii=False)
            
            cursor.execute('''
                INSERT OR REPLACE INTO personality_data 
                (personality_type, speech_style, combat_preference, risk_tolerance, 
                 teamwork_style, learning_style, interests)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                personality.personality_type,
                personality.speech_style,
                personality.combat_preference,
                personality.risk_tolerance,
                personality.teamwork_style,
                personality.learning_style,
                json.dumps(personality.interests, ensure_ascii=False)
            ))
            
            # 기본 정보도 저장
            cursor.execute('INSERT OR REPLACE INTO character_info VALUES (?, ?)', 
                         ('personality_full', personality_json))
            
            conn.commit()
    
    def load_personality(self) -> Optional[AIPersonality]:
        """성격 정보 로드"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM character_info WHERE key = ?', ('personality_full',))
            result = cursor.fetchone()
            
            if result:
                try:
                    personality_data = json.loads(result[0])
                    return AIPersonality(**personality_data)
                except:
                    return None
            return None
    
    def add_game_event(self, event_type: str, event_data: dict, emotional_impact: float = 0.5):
        """게임 이벤트 학습 데이터 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO game_events (event_type, event_data, emotional_impact)
                VALUES (?, ?, ?)
            ''', (event_type, json.dumps(event_data, ensure_ascii=False), emotional_impact))
            conn.commit()
    
    def add_conversation(self, context: str, user_input: str, ai_response: str, satisfaction: float = 0.5):
        """대화 기록 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (context, user_input, ai_response, satisfaction_score)
                VALUES (?, ?, ?, ?)
            ''', (context, user_input, ai_response, satisfaction))
            conn.commit()
    
    def update_relationship(self, target: str, relationship_change: dict):
        """관계 정보 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 관계 확인
            cursor.execute('SELECT * FROM relationships WHERE target_character = ?', (target,))
            existing = cursor.fetchone()
            
            if existing:
                # 업데이트
                cursor.execute('''
                    UPDATE relationships 
                    SET affection_level = ?, trust_level = ?, shared_experiences = shared_experiences + 1,
                        last_interaction = CURRENT_TIMESTAMP
                    WHERE target_character = ?
                ''', (
                    relationship_change.get('affection', existing[3]),
                    relationship_change.get('trust', existing[4]),
                    target
                ))
            else:
                # 새로 생성
                cursor.execute('''
                    INSERT INTO relationships 
                    (target_character, relationship_type, affection_level, trust_level, shared_experiences)
                    VALUES (?, ?, ?, ?, 1)
                ''', (
                    target, 
                    relationship_change.get('type', 'neutral'),
                    relationship_change.get('affection', 0.5),
                    relationship_change.get('trust', 0.5)
                ))
            
            conn.commit()
    
    def learn_strategy(self, situation: str, strategy: str, success: bool):
        """전략 학습"""
        success_value = 1.0 if success else 0.0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 전략 확인
            cursor.execute('''
                SELECT success_rate, usage_count FROM strategy_learning 
                WHERE situation_type = ? AND strategy_used = ?
            ''', (situation, strategy))
            
            existing = cursor.fetchone()
            
            if existing:
                # 성공률 업데이트 (가중 평균)
                old_rate, old_count = existing
                new_count = old_count + 1
                new_rate = (old_rate * old_count + success_value) / new_count
                
                cursor.execute('''
                    UPDATE strategy_learning 
                    SET success_rate = ?, usage_count = ?, last_used = CURRENT_TIMESTAMP
                    WHERE situation_type = ? AND strategy_used = ?
                ''', (new_rate, new_count, situation, strategy))
            else:
                # 새 전략 추가
                cursor.execute('''
                    INSERT INTO strategy_learning (situation_type, strategy_used, success_rate)
                    VALUES (?, ?, ?)
                ''', (situation, strategy, success_value))
            
            conn.commit()
    
    def get_learning_summary(self) -> dict:
        """학습 요약 정보 반환"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 이벤트 수
            cursor.execute('SELECT COUNT(*) FROM game_events')
            event_count = cursor.fetchone()[0]
            
            # 대화 수
            cursor.execute('SELECT COUNT(*) FROM conversations')
            conversation_count = cursor.fetchone()[0]
            
            # 평균 만족도
            cursor.execute('SELECT AVG(satisfaction_score) FROM conversations')
            avg_satisfaction = cursor.fetchone()[0] or 0.0
            
            # 관계 수
            cursor.execute('SELECT COUNT(*) FROM relationships')
            relationship_count = cursor.fetchone()[0]
            
            # 학습된 전략 수
            cursor.execute('SELECT COUNT(*) FROM strategy_learning')
            strategy_count = cursor.fetchone()[0]
            
            return {
                'events': event_count,
                'conversations': conversation_count,
                'avg_satisfaction': avg_satisfaction,
                'relationships': relationship_count,
                'strategies': strategy_count
            }

class GameIntegratedAI:
    """게임에 완전 통합된 AI 동료 시스템"""
    
    def __init__(self):
        self.active_companions = {}  # character_name -> AICompanion
        self.keyboard = KeyboardInput()
        self.auto_builder = AutoPartyBuilder()
        self.ollama_url = "http://localhost:11434"
        
        # 27개 직업별 AI 성향 템플릿
        self.job_ai_templates = {
            # 기본 8개 직업
            "전사": {
                "personality_traits": ["용감함", "직진적", "보호욕"],
                "combat_preference": "공격적",
                "interests": ["무기", "훈련", "명예", "보호"],
                "speech_patterns": ["당당하게", "확신하며", "간결하게"]
            },
            "궁수": {
                "personality_traits": ["정확함", "신중함", "관찰력"],
                "combat_preference": "전략적",
                "interests": ["정밀함", "거리", "타이밍", "분석"],
                "speech_patterns": ["조심스럽게", "정확하게", "계산적으로"]
            },
            "성기사": {
                "personality_traits": ["신성함", "희생정신", "정의감"],
                "combat_preference": "지원적",
                "interests": ["치유", "보호", "신념", "정의"],
                "speech_patterns": ["정중하게", "경건하게", "따뜻하게"]
            },
            "암흑기사": {
                "personality_traits": ["신비함", "복잡함", "깊이"],
                "combat_preference": "공격적",
                "interests": ["어둠", "힘", "비밀", "균형"],
                "speech_patterns": ["신비롭게", "깊게", "직설적으로"]
            },
            "바드": {
                "personality_traits": ["예술적", "사교적", "감정적"],
                "combat_preference": "지원적",
                "interests": ["음악", "이야기", "감정", "조화"],
                "speech_patterns": ["감정적으로", "리듬감있게", "화려하게"]
            },
            "검성": {
                "personality_traits": ["완벽주의", "수련", "절제"],
                "combat_preference": "공격적",
                "interests": ["검술", "수련", "완성", "극한"],
                "speech_patterns": ["절제되게", "명확하게", "강렬하게"]
            },
            "검투사": {
                "personality_traits": ["경쟁적", "불굴", "생존"],
                "combat_preference": "공격적",
                "interests": ["경쟁", "승리", "생존", "명성"],
                "speech_patterns": ["도전적으로", "자신감있게", "거칠게"]
            },
            "광전사": {
                "personality_traits": ["열정적", "충동적", "강인함"],
                "combat_preference": "공격적",
                "interests": ["전투", "아드레날린", "극한", "돌파"],
                "speech_patterns": ["열정적으로", "격렬하게", "직감적으로"]
            },
            
            # 해금 필요한 19개 직업
            "아크메이지": {
                "personality_traits": ["지적", "탐구적", "신비적"],
                "combat_preference": "전략적",
                "interests": ["마법", "지식", "연구", "신비"],
                "speech_patterns": ["학술적으로", "신중하게", "깊이있게"]
            },
            "도적": {
                "personality_traits": ["영리함", "민첩함", "독립적"],
                "combat_preference": "전략적",
                "interests": ["기회", "자유", "기술", "은밀"],
                "speech_patterns": ["재빠르게", "기발하게", "유연하게"]
            },
            "몽크": {
                "personality_traits": ["명상적", "균형", "절제"],
                "combat_preference": "방어적",
                "interests": ["수련", "깨달음", "균형", "내면"],
                "speech_patterns": ["차분하게", "깊게", "현명하게"]
            },
            "네크로맨서": {
                "personality_traits": ["신비적", "금기적", "깊이"],
                "combat_preference": "전략적",
                "interests": ["죽음", "영혼", "금기", "지식"],
                "speech_patterns": ["어둡게", "신비롭게", "철학적으로"]
            },
            "용기사": {
                "personality_traits": ["고귀함", "열정", "용맹"],
                "combat_preference": "공격적",
                "interests": ["용", "불", "영광", "전설"],
                "speech_patterns": ["웅장하게", "열정적으로", "고귀하게"]
            },
            "정령술사": {
                "personality_traits": ["자연적", "조화", "유연함"],
                "combat_preference": "지원적",
                "interests": ["자연", "정령", "조화", "균형"],
                "speech_patterns": ["자연스럽게", "부드럽게", "조화롭게"]
            },
            "암살자": {
                "personality_traits": ["차가움", "정밀함", "은밀"],
                "combat_preference": "전략적",
                "interests": ["정밀함", "은밀", "효율", "완벽"],
                "speech_patterns": ["차갑게", "간결하게", "정밀하게"]
            },
            "기계공학자": {
                "personality_traits": ["논리적", "창의적", "실용적"],
                "combat_preference": "전략적",
                "interests": ["기계", "발명", "효율", "혁신"],
                "speech_patterns": ["논리적으로", "기술적으로", "혁신적으로"]
            },
            "무당": {
                "personality_traits": ["영적", "신비적", "치유"],
                "combat_preference": "지원적",
                "interests": ["영혼", "치유", "균형", "조화"],
                "speech_patterns": ["영적으로", "치유적으로", "조화롭게"]
            },
            "해적": {
                "personality_traits": ["자유로움", "모험적", "무법"],
                "combat_preference": "공격적",
                "interests": ["자유", "모험", "보물", "바다"],
                "speech_patterns": ["자유롭게", "모험적으로", "거칠게"]
            },
            "사무라이": {
                "personality_traits": ["명예", "절제", "완벽"],
                "combat_preference": "방어적",
                "interests": ["명예", "도", "완벽", "절제"],
                "speech_patterns": ["명예롭게", "절제있게", "엄격하게"]
            },
            "드루이드": {
                "personality_traits": ["자연적", "평화적", "보호"],
                "combat_preference": "지원적",
                "interests": ["자연", "생명", "보호", "성장"],
                "speech_patterns": ["자연스럽게", "평화롭게", "보호적으로"]
            },
            "철학자": {
                "personality_traits": ["사색적", "논리적", "깊이"],
                "combat_preference": "전략적",
                "interests": ["진리", "논리", "분석", "사고"],
                "speech_patterns": ["사색적으로", "논리적으로", "깊이있게"]
            },
            "시간술사": {
                "personality_traits": ["신비적", "복잡함", "통찰"],
                "combat_preference": "전략적",
                "interests": ["시간", "운명", "가능성", "미래"],
                "speech_patterns": ["신비롭게", "복잡하게", "통찰적으로"]
            },
            "연금술사": {
                "personality_traits": ["실험적", "호기심", "변화"],
                "combat_preference": "전략적",
                "interests": ["실험", "변화", "발견", "창조"],
                "speech_patterns": ["실험적으로", "호기심으로", "변화적으로"]
            },
            "기사": {
                "personality_traits": ["충성", "희생", "보호"],
                "combat_preference": "방어적",
                "interests": ["충성", "보호", "의무", "명예"],
                "speech_patterns": ["충성스럽게", "보호적으로", "의무감으로"]
            },
            "신관": {
                "personality_traits": ["신성함", "치유", "봉사"],
                "combat_preference": "지원적",
                "interests": ["치유", "봉사", "신성", "희망"],
                "speech_patterns": ["신성하게", "치유적으로", "봉사적으로"]
            },
            "마검사": {
                "personality_traits": ["융합", "이중성", "균형"],
                "combat_preference": "공격적",
                "interests": ["융합", "마법검", "균형", "진화"],
                "speech_patterns": ["균형있게", "융합적으로", "이중적으로"]
            },
            "차원술사": {
                "personality_traits": ["초월적", "복잡함", "신비"],
                "combat_preference": "전략적",
                "interests": ["차원", "공간", "이동", "초월"],
                "speech_patterns": ["초월적으로", "복잡하게", "차원적으로"]
            }
        }
        
        # 성격 유형 템플릿 (더 다양하게 확장)
        self.personality_types = [
            "활발한", "조용한", "친근한", "냉정한", "열정적인", "신중한", 
            "장난스러운", "진지한", "낙천적인", "현실적인", "창의적인", "논리적인",
            "감정적인", "이성적인", "모험적인", "안정적인", "독립적인", "협력적인",
            "완벽주의", "자유로운", "책임감있는", "즉흥적인", "계획적인", "유연한"
        ]
        
        # 말투 스타일 (더 세분화)
        self.speech_styles = [
            "격식있는", "친근한", "귀여운", "쿨한", "열정적인", "차분한",
            "장난스러운", "진지한", "따뜻한", "시크한", "활기찬", "부드러운",
            "당당한", "수줍은", "유머러스한", "철학적인", "실용적인", "감성적인"
        ]
    
    def generate_character_ai_personality(self, character: Character) -> AIPersonality:
        """캐릭터 기반 AI 성격 생성"""
        job = getattr(character, 'character_class', '전사')
        name = getattr(character, 'name', '알 수 없음')
        
        # 직업 템플릿 가져오기
        job_template = self.job_ai_templates.get(job, self.job_ai_templates["전사"])
        
        # 랜덤 성격 요소 추가
        personality_type = random.choice(self.personality_types)
        speech_style = random.choice(self.speech_styles)
        
        # 성별 결정 (랜덤하게)
        gender = random.choice(["남성", "여성", "중성"])
        age = random.randint(18, 45)
        
        # 취미와 두려움 생성
        hobbies = [
            "독서", "음악감상", "요리", "운동", "여행", "그림그리기", "조각", "시쓰기",
            "별보기", "낚시", "정원가꾸기", "수집", "게임", "춤", "명상", "발명"
        ]
        
        fears = [
            "높은 곳", "어둠", "물", "불", "혼자 있는 것", "실패", "배신", "잊혀지는 것",
            "변화", "책임", "과거", "미래", "군중", "침묵", "혼돈", "완벽함"
        ]
        
        dreams = [
            "세계평화", "완벽한 기술 습득", "진정한 친구", "평온한 삶", "모험", "지식탐구",
            "예술 창작", "가족", "명예", "자유", "성장", "발견", "치유", "보호", "창조", "조화"
        ]
        
        # 위험 감수성과 팀워크 스타일
        risk_levels = ["신중함", "보통", "모험적", "무모함"]
        teamwork_styles = ["리더십", "협력적", "독립적", "추종적"]
        learning_styles = ["빠른학습", "꾸준함", "실험적", "보수적"]
        
        # 관심사는 직업 템플릿 + 추가 랜덤
        base_interests = job_template["interests"].copy()
        additional_interests = random.sample([
            "역사", "철학", "과학", "예술", "문학", "전략", "기계", "자연",
            "마법", "영성", "사회", "경제", "정치", "문화", "언어", "심리"
        ], 2)
        
        return AIPersonality(
            name=name,
            job=job,
            gender=gender,
            age=age,
            personality_type=personality_type,
            speech_style=speech_style,
            hobby=random.choice(hobbies),
            fear=random.choice(fears),
            dream=random.choice(dreams),
            combat_preference=job_template["combat_preference"],
            risk_tolerance=random.choice(risk_levels),
            teamwork_style=random.choice(teamwork_styles),
            learning_style=random.choice(learning_styles),
            interests=base_interests + additional_interests,
            memory_weight=random.uniform(0.6, 0.9),
            creativity_level=random.randint(3, 9),
            social_level=random.randint(2, 8)
        )
    
    def save_character_preset_with_ai(self, character: Character, personality: AIPersonality, 
                                    preset_path: str = "character_presets.json"):
        """캐릭터 프리셋에 AI 정보 포함하여 저장"""
        try:
            # 기존 프리셋 로드
            presets = {}
            if os.path.exists(preset_path):
                with open(preset_path, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
            
            # 캐릭터 기본 정보
            character_data = {
                "name": character.name,
                "class": getattr(character, 'character_class', '전사'),
                "level": getattr(character, 'level', 1),
                "hp": getattr(character, 'current_hp', 100),
                "max_hp": getattr(character, 'max_hp', 100),
                
                # 능력치
                "stats": {
                    "physical_attack": getattr(character, 'physical_attack', 10),
                    "magic_attack": getattr(character, 'magic_attack', 10),
                    "physical_defense": getattr(character, 'physical_defense', 8),
                    "magic_defense": getattr(character, 'magic_defense', 8),
                    "speed": getattr(character, 'speed', 5),
                    "luck": getattr(character, 'luck', 5)
                },
                
                # 🌟 AI 성격 정보 추가
                "ai_personality": asdict(personality),
                
                # 학습 데이터 경로
                "ai_database": f"ai_memory_{character.name}.db",
                
                # 생성 일시
                "created_at": datetime.now().isoformat(),
                
                # AI 상태
                "ai_enabled": True,
                "ai_learning_level": 0,
                "ai_conversation_count": 0,
                "ai_satisfaction_avg": 0.5
            }
            
            # 특성 정보 (있다면)
            if hasattr(character, 'active_traits') and character.active_traits:
                character_data["traits"] = character.active_traits
            
            # 프리셋에 추가
            presets[character.name] = character_data
            
            # 파일 저장
            with open(preset_path, 'w', encoding='utf-8') as f:
                json.dump(presets, f, ensure_ascii=False, indent=2)
            
            print(f"{GREEN}✅ {character.name}의 AI 프리셋이 저장되었습니다!{RESET}")
            
        except Exception as e:
            print(f"{RED}❌ 프리셋 저장 실패: {e}{RESET}")
    
    def load_character_from_preset(self, character_name: str, 
                                 preset_path: str = "character_presets.json") -> Optional[Tuple[Character, AIPersonality]]:
        """프리셋에서 캐릭터와 AI 성격 로드"""
        try:
            if not os.path.exists(preset_path):
                return None
            
            with open(preset_path, 'r', encoding='utf-8') as f:
                presets = json.load(f)
            
            if character_name not in presets:
                return None
            
            preset_data = presets[character_name]
            
            # 캐릭터 생성
            character = Character(preset_data["name"], preset_data["class"])
            
            # 능력치 복원
            stats = preset_data.get("stats", {})
            for stat_name, value in stats.items():
                if hasattr(character, stat_name):
                    setattr(character, stat_name, value)
            
            # 레벨 및 HP 복원
            character.level = preset_data.get("level", 1)
            character.current_hp = preset_data.get("hp", 100)
            character.max_hp = preset_data.get("max_hp", 100)
            
            # AI 성격 복원
            ai_data = preset_data.get("ai_personality", {})
            personality = AIPersonality(**ai_data)
            
            return character, personality
            
        except Exception as e:
            print(f"{RED}❌ 프리셋 로드 실패: {e}{RESET}")
            return None
    
    async def create_ai_multiplayer_party(self, party_size: int = 4) -> List[Dict]:
        """AI 멀티플레이용 파티 생성"""
        print(f"\n{BRIGHT_CYAN}🌟 AI 멀티플레이 파티 생성{RESET}")
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        # 자동 파티 빌더로 기본 파티 생성
        party_members = self.auto_builder.create_balanced_party(party_size=party_size)
        
        if not party_members:
            print(f"{RED}❌ 파티 생성에 실패했습니다.{RESET}")
            return []
        
        ai_party = []
        
        for i, character in enumerate(party_members, 1):
            print(f"\n{YELLOW}🎭 {i}번째 AI 동료 설정 중... {character.name} ({character.character_class}){RESET}")
            
            # AI 성격 생성
            personality = self.generate_character_ai_personality(character)
            
            # 데이터베이스 초기화
            ai_db = AICharacterDatabase(character.name)
            ai_db.save_personality(personality)
            
            # 캐릭터 프리셋 저장
            self.save_character_preset_with_ai(character, personality)
            
            # AI 파티 멤버 정보
            ai_member = {
                "character": character,
                "personality": personality,
                "database": ai_db,
                "ai_enabled": True,
                "conversation_ready": True
            }
            
            ai_party.append(ai_member)
            
            # 성격 정보 출력
            print(f"  {GREEN}✨ 성격:{RESET} {personality.personality_type}")
            print(f"  {BLUE}🗣️ 말투:{RESET} {personality.speech_style}")
            print(f"  {MAGENTA}⚔️ 전투:{RESET} {personality.combat_preference}")
            print(f"  {CYAN}🎯 관심사:{RESET} {', '.join(personality.interests[:3])}")
        
        print(f"\n{BRIGHT_GREEN}🎉 AI 멀티플레이 파티가 완성되었습니다!{RESET}")
        print(f"{WHITE}이제 진짜 동료들과 함께 모험을 떠날 수 있습니다! 🚀{RESET}")
        
        return ai_party
    
    async def start_ai_conversation(self, ai_member: dict, context: str, user_input: str) -> str:
        """AI와 대화 시작"""
        character = ai_member["character"]
        personality = ai_member["personality"]
        database = ai_member["database"]
        
        try:
            # Ollama 연결 시도
            response = await self._call_ollama(personality, context, user_input)
            
            if response:
                # 대화 기록
                database.add_conversation(context, user_input, response, 0.8)
                return response
            else:
                # 폴백: 룰 기반 응답
                return self._generate_rule_based_response(personality, context, user_input)
                
        except Exception as e:
            print(f"{YELLOW}⚠️ AI 연결 실패, 오프라인 모드로 전환{RESET}")
            return self._generate_rule_based_response(personality, context, user_input)
    
    async def _call_ollama(self, personality: AIPersonality, context: str, user_input: str) -> Optional[str]:
        """Ollama API 호출"""
        try:
            # 프롬프트 구성
            system_prompt = f"""당신은 {personality.name}입니다.

성격 정보:
- 직업: {personality.job}
- 성별: {personality.gender}
- 나이: {personality.age}
- 성격: {personality.personality_type}
- 말투: {personality.speech_style}
- 취미: {personality.hobby}
- 두려움: {personality.fear}
- 꿈: {personality.dream}
- 전투 성향: {personality.combat_preference}
- 관심사: {', '.join(personality.interests)}

게임 상황: {context}

이 캐릭터의 성격과 말투로 자연스럽게 대화하세요. 한국어로 답변하고, 게임 상황에 맞는 반응을 보여주세요."""

            payload = {
                "model": "llama3.1:8b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "max_tokens": 150
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"].strip()
            
        except Exception as e:
            print(f"{RED}Ollama 호출 실패: {e}{RESET}")
        
        return None
    
    def _generate_rule_based_response(self, personality: AIPersonality, context: str, user_input: str) -> str:
        """룰 기반 응답 생성 (폴백)"""
        
        # 기본 응답 패턴
        responses = []
        
        # 성격에 따른 응답 스타일
        if personality.personality_type in ["활발한", "열정적인", "낙천적인"]:
            responses.extend([
                f"오! 좋은 생각이에요! {personality.job}으로서 열심히 도와드릴게요!",
                f"와! 정말 재미있을 것 같네요! 같이 해봐요!",
                f"그거 좋네요! 제가 {personality.interests[0]}에 관심이 많거든요!"
            ])
        elif personality.personality_type in ["조용한", "신중한", "현실적인"]:
            responses.extend([
                f"음... 신중하게 생각해봐야겠네요. {personality.job}의 입장에서는...",
                f"조심스럽게 접근하는 게 좋겠어요. 제 경험상으론...",
                f"계획을 세워서 진행하면 어떨까요?"
            ])
        elif personality.personality_type in ["친근한", "협력적인", "따뜻한"]:
            responses.extend([
                f"물론이죠! 함께하면 더 잘할 수 있을 거예요!",
                f"도움이 필요하시면 언제든 말씀하세요!",
                f"우리가 힘을 합치면 못할 게 없어요!"
            ])
        
        # 말투에 따른 어미 조정
        if personality.speech_style == "격식있는":
            base_response = random.choice(responses)
            return base_response.replace("요!", "습니다.").replace("네요!", "네요.").replace("해요!", "하겠습니다.")
        elif personality.speech_style == "귀여운":
            base_response = random.choice(responses)
            return base_response.replace("요", "용").replace("네요", "네용") + " ✨"
        elif personality.speech_style == "쿨한":
            return random.choice([
                "알겠어.",
                "그런가.",
                f"{personality.job}으로서는 나쁘지 않네.",
                "좋아, 해보자."
            ])
        
        return random.choice(responses)
    
    def analyze_game_situation(self, ai_party: List[Dict], game_context: dict) -> Dict[str, str]:
        """게임 상황 분석 및 AI 조언"""
        ai_advice = {}
        
        for ai_member in ai_party:
            character = ai_member["character"]
            personality = ai_member["personality"]
            
            # 상황별 조언 생성
            advice = self._generate_situational_advice(personality, game_context)
            ai_advice[character.name] = advice
            
            # 학습 데이터 저장
            database = ai_member["database"]
            database.add_game_event(
                event_type="situation_analysis",
                event_data=game_context,
                emotional_impact=0.6
            )
        
        return ai_advice
    
    def _generate_situational_advice(self, personality: AIPersonality, context: dict) -> str:
        """상황별 AI 조언 생성"""
        situation_type = context.get("type", "general")
        
        if situation_type == "combat":
            if personality.combat_preference == "공격적":
                return f"전투 상황이네요! {personality.job}으로서 앞장서서 공격하겠습니다!"
            elif personality.combat_preference == "방어적":
                return f"조심하세요! 제가 {personality.job}으로서 방어를 담당할게요."
            elif personality.combat_preference == "지원적":
                return f"모두들 힘내세요! {personality.job}으로서 지원하겠습니다!"
            else:  # 전략적
                return f"적을 분석해봅시다. {personality.job}의 전문 지식을 활용해보죠."
        
        elif situation_type == "exploration":
            if personality.personality_type in ["모험적인", "활발한"]:
                return f"새로운 곳을 탐험하는 건 언제나 흥미로워요! {personality.interests[0]}와 관련이 있을까요?"
            else:
                return f"신중하게 살펴봐야겠어요. {personality.job}의 경험을 살려서 도움이 되도록 하겠습니다."
        
        elif situation_type == "puzzle":
            if personality.learning_style == "논리적":
                return f"퍼즐이네요! 논리적으로 접근해봅시다. {personality.job}의 지식이 도움이 될 거예요."
            else:
                return f"함께 생각해봐요! 여러 관점에서 접근하면 답이 보일 거예요."
        
        return f"{personality.job}으로서 최선을 다해 도와드리겠습니다!"
    
    def display_ai_party_status(self, ai_party: List[Dict]):
        """AI 파티 상태 표시"""
        print(f"\n{BRIGHT_CYAN}🤖 AI 멀티플레이 파티 상태{RESET}")
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for i, ai_member in enumerate(ai_party, 1):
            character = ai_member["character"]
            personality = ai_member["personality"]
            database = ai_member["database"]
            
            # 학습 통계
            stats = database.get_learning_summary()
            
            print(f"\n{YELLOW}🎭 {i}. {character.name}{RESET} ({character.character_class})")
            print(f"   {GREEN}성격:{RESET} {personality.personality_type} | {BLUE}말투:{RESET} {personality.speech_style}")
            print(f"   {MAGENTA}관심사:{RESET} {', '.join(personality.interests[:2])}")
            print(f"   {CYAN}학습:{RESET} 대화 {stats['conversations']}회 | 이벤트 {stats['events']}개")
            print(f"   {WHITE}만족도:{RESET} {stats['avg_satisfaction']:.1f}/1.0")

# 🚀 실제 사용 예시
async def main():
    """메인 실행 함수"""
    print(f"{BRIGHT_CYAN}🌟 Dawn of Stellar - AI 멀티플레이 시스템 🌟{RESET}")
    print(f"{CYAN}클래식 모드의 완벽한 상위호환! AI 동료들과 함께하는 진짜 멀티플레이!{RESET}")
    
    # AI 시스템 초기화
    ai_system = GameIntegratedAI()
    
    # AI 파티 생성
    ai_party = await ai_system.create_ai_multiplayer_party(4)
    
    if ai_party:
        # 파티 상태 표시
        ai_system.display_ai_party_status(ai_party)
        
        # 샘플 대화 테스트
        print(f"\n{BRIGHT_GREEN}💬 AI 동료와 대화 테스트{RESET}")
        
        for ai_member in ai_party[:2]:  # 처음 2명과 테스트
            character = ai_member["character"]
            personality = ai_member["personality"]
            
            print(f"\n{YELLOW}👤 {character.name}과 대화:{RESET}")
            
            # 테스트 대화
            context = "던전 입구에서 탐험을 준비하고 있습니다"
            user_input = "이번 던전 탐험에 대해 어떻게 생각해?"
            
            response = await ai_system.start_ai_conversation(ai_member, context, user_input)
            print(f"{GREEN}🤖 {character.name}:{RESET} {response}")
        
        print(f"\n{BRIGHT_CYAN}🎉 AI 멀티플레이 시스템이 성공적으로 초기화되었습니다!{RESET}")
        print(f"{WHITE}이제 게임에 통합하여 실제 플레이가 가능합니다! 🚀{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
