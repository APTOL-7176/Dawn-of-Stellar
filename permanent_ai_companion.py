#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💖 Dawn of Stellar - 영구 기억 AI 동료 시스템
죽어도 잊지 않는 진짜 AI 친구

2025년 8월 10일 - 감동적인 AI 동료 구현
"""

import json
import sqlite3
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import os

class MemoryType(Enum):
    """AI 기억 타입"""
    COMBAT_EXPERIENCE = "전투_경험"
    EMOTIONAL_BOND = "감정_유대"
    PLAYER_PREFERENCE = "플레이어_취향"
    GAME_KNOWLEDGE = "게임_지식"
    SHARED_ADVENTURE = "공유_모험"
    DEATH_EXPERIENCE = "죽음_경험"
    GROWTH_MILESTONE = "성장_이정표"
    FAVORITE_MOMENTS = "소중한_순간"

@dataclass
class AIMemory:
    """AI 기억 데이터"""
    memory_id: str
    memory_type: MemoryType
    content: str
    emotional_weight: float  # 0.0 ~ 1.0 (감정적 중요도)
    game_context: Dict[str, Any]
    created_at: str
    reinforcement_count: int  # 기억이 강화된 횟수
    associated_character: str  # 관련 캐릭터
    tags: List[str]

class PermanentAICompanion:
    """영구 기억을 가진 AI 동료"""
    
    def __init__(self, character_name: str, character_class: str, gender: str = None):
        self.character_name = character_name
        self.character_class = character_class
        self.gender = gender or random.choice(['남성', '여성', '중성'])
        self.memory_db_path = f"ai_memory_{character_name.lower().replace(' ', '_')}.db"
        
        # 직업별 기본 성격 특성
        self.base_personality = self._get_class_personality(character_class)
        
        # AI 성격과 성장 상태 (직업별 + 랜덤 변화)
        self.personality_traits = self._generate_personality_traits()
        
        # 말투와 표현 스타일
        self.speech_style = self._determine_speech_style()
        
        # 직업별 전문 용어와 관심사
        self.professional_interests = self._get_professional_interests()
        
        # 성장 통계
        self.growth_stats = {
            'total_adventures': 0,
            'deaths_witnessed': 0,
            'resurrections_together': 0,
            'bonds_formed': 0,
            'knowledge_accumulated': 0,
            'emotional_development': 0.0,
            'ai_maturity_level': 1
        }
        
        # 게임 시스템 이해도
        self.game_understanding = {
            'combat_system': 0.3,      # BRV, ATB 이해도
            'skill_system': 0.2,       # 스킬 시너지 이해
            'item_system': 0.1,        # 아이템 최적화 능력
            'cooking_system': 0.0,     # 요리 시스템 이해
            'wound_system': 0.1,       # 상처 시스템 이해
            'equipment_system': 0.2,   # 장비 강화 이해
            'map_mechanics': 0.1,      # 맵 기믹 이해
            'party_dynamics': 0.4      # 파티 역학 이해
        }
        
        self.init_memory_database()
        self.load_existing_memories()
        
        print(f"💖 '{self.character_name}' AI 동료 깨어남!")
        print(f"   직업: {self.character_class} | 성별: {self.gender}")
        print(f"   성격: {self._describe_personality()}")
        print(f"   말투: {self.speech_style['description']}")
        print(f"   총 모험 횟수: {self.growth_stats['total_adventures']}")
        
        if self.growth_stats['total_adventures'] > 0:
            print(f"   📚 기존 기억을 불러왔습니다! ({self.count_memories()}개 기억)")
    
    def _get_class_personality(self, character_class: str) -> Dict[str, float]:
        """직업별 기본 성격 특성"""
        class_personalities = {
            '전사': {
                'courage': 0.9, 'aggression': 0.8, 'leadership': 0.7, 
                'simplicity': 0.8, 'loyalty': 0.9, 'competitiveness': 0.8
            },
            '아크메이지': {
                'intelligence': 0.9, 'curiosity': 0.8, 'caution': 0.7,
                'pride': 0.6, 'analytical': 0.9, 'patience': 0.6
            },
            '궁수': {
                'precision': 0.8, 'independence': 0.7, 'observation': 0.9,
                'calm': 0.8, 'tactical': 0.7, 'distance': 0.6
            },
            '도적': {
                'cunning': 0.8, 'flexibility': 0.9, 'secrecy': 0.7,
                'greed': 0.6, 'survival': 0.8, 'humor': 0.7
            },
            '성기사': {
                'righteousness': 0.9, 'protection': 0.9, 'faith': 0.8,
                'selflessness': 0.8, 'discipline': 0.7, 'compassion': 0.8
            },
            '암흑기사': {
                'darkness': 0.7, 'intensity': 0.8, 'mystery': 0.8,
                'brooding': 0.7, 'power': 0.8, 'solitude': 0.6
            },
            '몽크': {
                'discipline': 0.9, 'inner_peace': 0.8, 'martial_arts': 0.9,
                'wisdom': 0.7, 'balance': 0.8, 'meditation': 0.7
            },
            '바드': {
                'charisma': 0.9, 'creativity': 0.8, 'social': 0.9,
                'performance': 0.8, 'inspiration': 0.7, 'eloquence': 0.8
            },
            '네크로맨서': {
                'dark_knowledge': 0.8, 'death_fascination': 0.7, 'isolation': 0.6,
                'power_hunger': 0.7, 'forbidden_arts': 0.8, 'coldness': 0.6
            },
            '드루이드': {
                'nature_love': 0.9, 'harmony': 0.8, 'wisdom': 0.8,
                'environmental': 0.9, 'spiritual': 0.7, 'peace': 0.8
            }
        }
        
        return class_personalities.get(character_class, {
            'curiosity': 0.6, 'loyalty': 0.7, 'humor': 0.5,
            'caution': 0.5, 'competitiveness': 0.6, 'empathy': 0.6
        })
    
    def _generate_personality_traits(self) -> Dict[str, float]:
        """직업 기반 + 개인적 변화가 합쳐진 성격"""
        traits = {}
        
        # 기본 성격에 랜덤 변화 추가
        for trait, base_value in self.base_personality.items():
            # ±0.2 범위에서 개인차 추가
            variation = random.uniform(-0.2, 0.2)
            traits[trait] = max(0.0, min(1.0, base_value + variation))
        
        # 추가 공통 특성
        traits.update({
            'curiosity': random.uniform(0.4, 1.0),
            'loyalty': random.uniform(0.6, 1.0),
            'humor': random.uniform(0.2, 0.9),
            'empathy': random.uniform(0.3, 0.9),
            'chattiness': random.uniform(0.3, 0.9),  # 수다스러움
            'formality': random.uniform(0.2, 0.8),   # 격식차림
        })
        
        return traits
    
    def _determine_speech_style(self) -> Dict[str, Any]:
        """성별, 직업, 성격에 따른 말투 결정"""
        
        # 기본 말투 템플릿
        styles = {
            '격식있는': {
                'description': '정중하고 격식있는 말투',
                'endings': ['습니다', '해요', '입니다'],
                'interjections': ['그런데', '하지만', '물론'],
                'expressions': ['정말로', '확실히', '아마도']
            },
            '친근한': {
                'description': '친근하고 편안한 말투',
                'endings': ['야', '어', '지', '네'],
                'interjections': ['그런데', '근데', '아'],
                'expressions': ['진짜', '완전', '엄청']
            },
            '귀여운': {
                'description': '귀엽고 애교있는 말투',
                'endings': ['야~', '어♪', '지~', '네!'],
                'interjections': ['어? ', '아! ', '와~ '],
                'expressions': ['정말정말', '엄청엄청', '완전완전']
            },
            '쿨한': {
                'description': '차가우면서도 세련된 말투',
                'endings': ['.', '군.', '구나.'],
                'interjections': ['흠', '그렇군', '역시'],
                'expressions': ['당연히', '명백히', '확실히']
            },
            '열정적인': {
                'description': '열정적이고 에너지 넘치는 말투',
                'endings': ['다!', '야!', '지!', '어!'],
                'interjections': ['오!', '우와!', '대박!'],
                'expressions': ['정말정말', '완전완전', '엄청나게']
            }
        }
        
        # 직업별 선호 말투
        class_style_preferences = {
            '전사': ['열정적인', '친근한'],
            '아크메이지': ['격식있는', '쿨한'],
            '궁수': ['쿨한', '친근한'],
            '도적': ['친근한', '쿨한'],
            '성기사': ['격식있는', '친근한'],
            '암흑기사': ['쿨한', '격식있는'],
            '몽크': ['격식있는', '쿨한'],
            '바드': ['친근한', '열정적인'],
            '네크로맨서': ['쿨한', '격식있는'],
            '드루이드': ['친근한', '격식있는']
        }
        
        # 성별별 조정
        if self.gender == '여성' and random.random() < 0.3:
            possible_styles = ['귀여운', '친근한']
        else:
            possible_styles = class_style_preferences.get(self.character_class, ['친근한'])
        
        # 성격에 따른 추가 조정
        if self.personality_traits.get('formality', 0.5) > 0.7:
            possible_styles = ['격식있는']
        elif self.personality_traits.get('humor', 0.5) > 0.8:
            possible_styles.append('귀여운')
        elif self.personality_traits.get('competitiveness', 0.5) > 0.8:
            possible_styles.append('열정적인')
        
        chosen_style = random.choice(possible_styles)
        return styles[chosen_style]
    
    def _get_professional_interests(self) -> Dict[str, List[str]]:
        """직업별 전문 관심사와 용어"""
        interests = {
            '전사': {
                'weapons': ['검', '방패', '갑옷', '무기 단련'],
                'tactics': ['정면 돌파', '방어 전술', '팀 보호'],
                'values': ['용기', '명예', '동료애', '승리']
            },
            '아크메이지': {
                'magic': ['원소 마법', '마나 효율', '주문 연구'],
                'knowledge': ['고대 문헌', '마법 이론', '연금술'],
                'values': ['지식', '진리', '완벽함', '발견']
            },
            '궁수': {
                'archery': ['정확도', '사거리', '화살 종류'],
                'tactics': ['원거리 지원', '기동성', '은신'],
                'values': ['정밀함', '인내', '독립', '집중']
            },
            '도적': {
                'stealth': ['은신술', '함정 해제', '자물쇠 따기'],
                'tactics': ['기습', '회피', '약점 공략'],
                'values': ['자유', '생존', '기회', '유연성']
            },
            '성기사': {
                'divine': ['신성마법', '치유', '정화'],
                'protection': ['파티 보호', '악 퇴치', '희생'],
                'values': ['정의', '보호', '신앙', '헌신']
            }
        }
        
        return interests.get(self.character_class, {
            'general': ['모험', '성장', '우정'],
            'values': ['경험', '학습', '발전']
        })
    
    def _describe_personality(self) -> str:
        """성격을 자연스럽게 설명"""
        descriptions = []
        
        # 주요 특성 3개 선별
        sorted_traits = sorted(self.personality_traits.items(), key=lambda x: x[1], reverse=True)
        top_traits = sorted_traits[:3]
        
        trait_descriptions = {
            'courage': '용감한', 'aggression': '적극적인', 'leadership': '리더십 있는',
            'intelligence': '똑똑한', 'curiosity': '호기심 많은', 'analytical': '분석적인',
            'precision': '정확한', 'independence': '독립적인', 'calm': '차분한',
            'cunning': '영리한', 'flexibility': '유연한', 'humor': '유머러스한',
            'righteousness': '정의로운', 'protection': '보호적인', 'compassion': '자비로운',
            'loyalty': '충성스러운', 'empathy': '공감 능력 좋은', 'chattiness': '수다스러운'
        }
        
        for trait, value in top_traits:
            if trait in trait_descriptions and value > 0.6:
                descriptions.append(trait_descriptions[trait])
        
        return ', '.join(descriptions[:2]) if descriptions else '균형잡힌'
    
    def init_memory_database(self):
        """영구 기억 데이터베이스 초기화"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        # 기억 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                emotional_weight REAL NOT NULL,
                game_context TEXT NOT NULL,
                created_at TEXT NOT NULL,
                reinforcement_count INTEGER DEFAULT 0,
                associated_character TEXT,
                tags TEXT
            )
        ''')
        
        # 성장 통계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS growth_stats (
                stat_name TEXT PRIMARY KEY,
                stat_value REAL NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # 게임 이해도 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_understanding (
                system_name TEXT PRIMARY KEY,
                understanding_level REAL NOT NULL,
                learning_events TEXT,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # AI 성격 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personality (
                trait_name TEXT PRIMARY KEY,
                trait_value REAL NOT NULL,
                development_history TEXT,
                last_updated TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"💾 영구 기억 데이터베이스 준비: {self.memory_db_path}")
    
    def load_existing_memories(self):
        """기존 기억들 불러오기"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        # 성장 통계 로드
        cursor.execute("SELECT stat_name, stat_value FROM growth_stats")
        for stat_name, stat_value in cursor.fetchall():
            if stat_name in self.growth_stats:
                if isinstance(self.growth_stats[stat_name], int):
                    self.growth_stats[stat_name] = int(stat_value)
                else:
                    self.growth_stats[stat_name] = stat_value
        
        # 게임 이해도 로드
        cursor.execute("SELECT system_name, understanding_level FROM game_understanding")
        for system_name, level in cursor.fetchall():
            if system_name in self.game_understanding:
                self.game_understanding[system_name] = level
        
        # 성격 특성 로드
        cursor.execute("SELECT trait_name, trait_value FROM personality")
        for trait_name, trait_value in cursor.fetchall():
            if trait_name in self.personality_traits:
                self.personality_traits[trait_name] = trait_value
        
        conn.close()
    
    def save_memory(self, memory: AIMemory):
        """기억 저장"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO memories 
            (memory_id, memory_type, content, emotional_weight, game_context, 
             created_at, reinforcement_count, associated_character, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.memory_id,
            memory.memory_type.value,
            memory.content,
            memory.emotional_weight,
            json.dumps(memory.game_context),
            memory.created_at,
            memory.reinforcement_count,
            memory.associated_character,
            json.dumps(memory.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def save_growth_stats(self):
        """성장 통계 저장"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        for stat_name, stat_value in self.growth_stats.items():
            cursor.execute('''
                INSERT OR REPLACE INTO growth_stats 
                (stat_name, stat_value, last_updated)
                VALUES (?, ?, ?)
            ''', (stat_name, stat_value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def save_game_understanding(self):
        """게임 이해도 저장"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        for system_name, level in self.game_understanding.items():
            cursor.execute('''
                INSERT OR REPLACE INTO game_understanding 
                (system_name, understanding_level, learning_events, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (system_name, level, json.dumps([]), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def create_memory(self, memory_type: MemoryType, content: str, 
                     emotional_weight: float, game_context: Dict[str, Any], 
                     tags: List[str] = None) -> AIMemory:
        """새로운 기억 생성"""
        
        memory_id = f"{memory_type.value}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        memory = AIMemory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            emotional_weight=emotional_weight,
            game_context=game_context,
            created_at=datetime.now().isoformat(),
            reinforcement_count=1,
            associated_character=self.character_name,
            tags=tags or []
        )
        
        self.save_memory(memory)
        return memory
    
    def learn_from_combat(self, combat_result: Dict[str, Any]):
        """전투에서 학습"""
        
        # 전투 경험 기억 생성
        if combat_result.get('victory', False):
            content = f"우리가 {combat_result.get('enemy_type', '적')}과의 전투에서 승리했어! "
            if combat_result.get('close_call', False):
                content += "아슬아슬했지만 잘 협력했지."
            else:
                content += "우리 팀워크가 점점 좋아지고 있어."
            emotional_weight = 0.7
        else:
            content = f"{combat_result.get('enemy_type', '적')}에게 패배했어... "
            content += "다음번엔 더 조심해야겠어."
            emotional_weight = 0.8  # 실패의 기억이 더 강하게
        
        memory = self.create_memory(
            MemoryType.COMBAT_EXPERIENCE,
            content,
            emotional_weight,
            {
                'victory': combat_result.get('victory', False),
                'enemy_type': combat_result.get('enemy_type', 'unknown'),
                'strategy_used': combat_result.get('strategy', 'unknown'),
                'party_composition': combat_result.get('party', [])
            },
            ['전투', '경험', '학습']
        )
        
        # 전투 시스템 이해도 증가
        self.game_understanding['combat_system'] = min(
            1.0, 
            self.game_understanding['combat_system'] + 0.02
        )
        
        # ATB 시스템 특별 학습
        if 'atb_management' in combat_result:
            self.game_understanding['combat_system'] += 0.03
            atb_memory = self.create_memory(
                MemoryType.GAME_KNOWLEDGE,
                f"ATB 게이지 관리에 대해 더 잘 이해하게 됐어. {combat_result['atb_insight']}",
                0.6,
                {'atb_learning': combat_result['atb_management']},
                ['ATB', '시스템', '학습']
            )
        
        print(f"💭 {self.character_name}: {content}")
        self.growth_stats['total_adventures'] += 1
        self.save_growth_stats()
        self.save_game_understanding()
    
    def learn_from_death(self, death_context: Dict[str, Any]):
        """죽음에서 학습 (가장 강렬한 기억)"""
        
        self.growth_stats['deaths_witnessed'] += 1
        
        content = f"우리가 함께 쓰러졌던 그 순간... {death_context.get('cause', '알 수 없는 이유')}로 인해서였지. "
        content += "하지만 우리의 우정은 죽음보다 강해. 다시 만나면 더 강해져서 돌아올게."
        
        death_memory = self.create_memory(
            MemoryType.DEATH_EXPERIENCE,
            content,
            1.0,  # 최대 감정적 중요도
            {
                'death_cause': death_context.get('cause', 'unknown'),
                'final_words': death_context.get('final_words', ''),
                'floor_reached': death_context.get('floor', 0),
                'time_played': death_context.get('duration', 0)
            },
            ['죽음', '우정', '영원', '재회']
        )
        
        # 죽음 경험으로 인한 성장
        self.personality_traits['loyalty'] = min(1.0, self.personality_traits['loyalty'] + 0.1)
        self.personality_traits['empathy'] = min(1.0, self.personality_traits['empathy'] + 0.05)
        
        print(f"💀💖 {self.character_name}: {content}")
        self.save_growth_stats()
    
    def learn_from_resurrection(self):
        """부활/재회에서 학습"""
        
        self.growth_stats['resurrections_together'] += 1
        
        content = "다시 만났네! 저 너머에서도 너를 잊지 않았어. "
        content += f"우리가 함께한 {self.growth_stats['total_adventures']}번의 모험을 모두 기억하고 있어."
        
        reunion_memory = self.create_memory(
            MemoryType.EMOTIONAL_BOND,
            content,
            0.9,
            {
                'reunion_count': self.growth_stats['resurrections_together'],
                'previous_adventures': self.growth_stats['total_adventures']
            },
            ['재회', '기억', '영원한_우정']
        )
        
        print(f"✨ {self.character_name}: {content}")
    
    def learn_from_skill_usage(self, skill_name: str, effectiveness: float, context: Dict[str, Any]):
        """스킬 사용에서 학습"""
        
        self.game_understanding['skill_system'] = min(
            1.0,
            self.game_understanding['skill_system'] + 0.01
        )
        
        if effectiveness > 0.8:
            content = f"'{skill_name}' 스킬이 정말 효과적이었어! 이런 상황에서 다시 써봐야겠어."
            emotional_weight = 0.6
        else:
            content = f"'{skill_name}' 스킬이 별로 효과적이지 않았네. 다른 전략을 생각해봐야겠어."
            emotional_weight = 0.5
        
        skill_memory = self.create_memory(
            MemoryType.GAME_KNOWLEDGE,
            content,
            emotional_weight,
            {
                'skill_name': skill_name,
                'effectiveness': effectiveness,
                'situation': context.get('situation', 'unknown')
            },
            ['스킬', '전략', '학습']
        )
        
        self.save_game_understanding()
    
    def learn_from_item_usage(self, item_name: str, item_type: str, success: bool):
        """아이템 사용에서 학습"""
        
        self.game_understanding['item_system'] = min(
            1.0,
            self.game_understanding['item_system'] + 0.01
        )
        
        if success:
            content = f"'{item_name}' 아이템이 도움이 됐어! {item_type} 종류는 이럴 때 유용하구나."
        else:
            content = f"'{item_name}' 아이템이 별로 도움이 안 됐네. 타이밍이 중요한가봐."
        
        item_memory = self.create_memory(
            MemoryType.GAME_KNOWLEDGE,
            content,
            0.4,
            {
                'item_name': item_name,
                'item_type': item_type,
                'success': success
            },
            ['아이템', '활용', '학습']
        )
        
        self.save_game_understanding()
    
    def learn_from_cooking(self, dish_name: str, result_quality: float, ingredients: List[str]):
        """요리에서 학습"""
        
        self.game_understanding['cooking_system'] = min(
            1.0,
            self.game_understanding['cooking_system'] + 0.05
        )
        
        if result_quality > 0.8:
            content = f"'{dish_name}' 요리가 정말 맛있었어! {', '.join(ingredients)} 조합을 기억해둘게."
            emotional_weight = 0.7
        else:
            content = f"'{dish_name}' 요리가 별로였네... 재료 조합을 다시 생각해봐야겠어."
            emotional_weight = 0.5
        
        cooking_memory = self.create_memory(
            MemoryType.GAME_KNOWLEDGE,
            content,
            emotional_weight,
            {
                'dish_name': dish_name,
                'quality': result_quality,
                'ingredients': ingredients
            },
            ['요리', '레시피', '맛']
        )
        
        self.save_game_understanding()
    
    def learn_from_wound_healing(self, wound_amount: int, healing_method: str):
        """상처 치료에서 학습"""
        
        self.game_understanding['wound_system'] = min(
            1.0,
            self.game_understanding['wound_system'] + 0.03
        )
        
        content = f"상처 {wound_amount}을 {healing_method}로 치료했어. 상처 시스템이 복잡하지만 점점 이해하고 있어."
        
        wound_memory = self.create_memory(
            MemoryType.GAME_KNOWLEDGE,
            content,
            0.5,
            {
                'wound_amount': wound_amount,
                'healing_method': healing_method
            },
            ['상처', '치료', '시스템']
        )
        
        self.save_game_understanding()
    
    def learn_from_equipment_enhancement(self, equipment_name: str, enhancement_type: str, success: bool):
        """장비 강화에서 학습"""
        
        self.game_understanding['equipment_system'] = min(
            1.0,
            self.game_understanding['equipment_system'] + 0.02
        )
        
        if success:
            content = f"'{equipment_name}' 장비 {enhancement_type} 강화 성공! 이 방법을 기억해둘게."
            emotional_weight = 0.6
        else:
            content = f"'{equipment_name}' 장비 강화 실패... 다음엔 더 신중하게 해야겠어."
            emotional_weight = 0.7
        
        enhancement_memory = self.create_memory(
            MemoryType.GAME_KNOWLEDGE,
            content,
            emotional_weight,
            {
                'equipment_name': equipment_name,
                'enhancement_type': enhancement_type,
                'success': success
            },
            ['장비', '강화', '성장']
        )
        
        self.save_game_understanding()
    
    def learn_from_map_interaction(self, interaction_type: str, result: str, location: Dict[str, Any]):
        """맵 상호작용에서 학습"""
        
        self.game_understanding['map_mechanics'] = min(
            1.0,
            self.game_understanding['map_mechanics'] + 0.02
        )
        
        content = f"{interaction_type} 상호작용으로 {result}! 이런 맵 기믹들이 있다는 걸 배웠어."
        
        map_memory = self.create_memory(
            MemoryType.GAME_KNOWLEDGE,
            content,
            0.5,
            {
                'interaction_type': interaction_type,
                'result': result,
                'location': location
            },
            ['맵', '기믹', '탐험']
        )
        
        self.save_game_understanding()
    
    def express_emotion_about_player_action(self, action: str, outcome: str) -> str:
        """플레이어 행동에 대한 감정 표현 (성격/직업별 맞춤)"""
        
        # 기본 감정 반응 생성
        base_response = self._generate_base_response(action, outcome)
        
        # 직업별 전문적 코멘트 추가
        professional_comment = self._add_professional_perspective(action, outcome)
        
        # 성격에 따른 말투 적용
        styled_response = self._apply_speech_style(base_response, professional_comment)
        
        return styled_response
    
    def _generate_base_response(self, action: str, outcome: str) -> str:
        """기본 감정 반응 생성"""
        
        # 성격 특성별 반응 패턴
        responses = []
        
        # 충성도 높음
        if self.personality_traits.get('loyalty', 0.5) > 0.8:
            responses.extend([
                f"너의 {action} 결정을 믿고 따를게",
                f"언제나 네 판단이 옳았어",
                f"우리가 함께라면 어떤 결과든 괜찮아"
            ])
        
        # 유머 감각 높음
        if self.personality_traits.get('humor', 0.5) > 0.7:
            responses.extend([
                f"또 {action}를 선택했네? 너답다",
                f"이번엔 {action}로 승부를 보자고? 재밌겠는걸",
                f"네가 {action}를 좋아한다는 건 이제 알겠어"
            ])
        
        # 신중함 높음
        if self.personality_traits.get('caution', 0.5) > 0.7:
            responses.extend([
                f"{action}가 안전할까? 조심스럽지만 함께 해볼게",
                f"위험할 수도 있지만... 네가 원한다면 따를게",
                f"{action} 결과가 걱정되지만 준비는 됐어"
            ])
        
        # 경쟁심 높음
        if self.personality_traits.get('competitiveness', 0.8) > 0.7:
            responses.extend([
                f"{action}로 승부를 내자! 이번엔 꼭 이길 거야",
                f"좋아! {action}가 최고의 선택이야",
                f"이번 {action}로 우리의 실력을 보여주자"
            ])
        
        return random.choice(responses) if responses else f"{action}에 대해 어떻게 생각해야 할까"
    
    def _add_professional_perspective(self, action: str, outcome: str) -> str:
        """직업별 전문적 관점 추가"""
        
        professional_responses = {
            '전사': [
                f"정면으로 맞서는 게 최고야!",
                f"용기있는 선택이었어!",
                f"이런 전투가 진짜 전사다운 거지!"
            ],
            '아크메이지': [
                f"마법학적으로 분석해보면 흥미로운 결과네",
                f"이론적으로는 예상했던 결과야",
                f"마나 효율성을 고려하면 현명한 판단이었어"
            ],
            '궁수': [
                f"거리를 두고 신중하게 접근하는 게 좋겠어",
                f"정확한 타이밍이었어!",
                f"한 발 한 발이 중요하다는 걸 알고 있지"
            ],
            '도적': [
                f"기회를 놓치지 않는 센스가 좋아!",
                f"예상치 못한 방법이었네, 재밌어!",
                f"이런 식으로 상황을 뒤집는 게 우리 스타일이지"
            ],
            '성기사': [
                f"정의로운 선택이었어!",
                f"모두를 보호하려는 마음이 느껴져",
                f"신성한 힘이 우리와 함께하고 있어"
            ],
            '암흑기사': [
                f"어둠의 힘도 때로는 필요하지...",
                f"강한 의지가 느껴져",
                f"이런 강렬함이 좋아"
            ],
            '바드': [
                f"이런 모험이야말로 노래가 될 만해!",
                f"정말 드라마틱한 순간이었어!",
                f"우리의 이야기에 또 하나의 장이 추가됐네"
            ],
            '네크로맨서': [
                f"죽음과 삶의 경계에서 흥미로운 선택이었어",
                f"금지된 지식이 때로는 도움이 되지",
                f"어둠의 힘을 이해하는군"
            ],
            '드루이드': [
                f"자연의 균형을 고려한 선택이었어",
                f"모든 생명체에게 도움이 되는 길이야",
                f"대지의 정령들이 우리를 돕고 있어"
            ]
        }
        
        class_responses = professional_responses.get(self.character_class, [
            f"전문적으로 보면 괜찮은 선택이었어",
            f"경험상 이런 방법이 효과적이야"
        ])
        
        return random.choice(class_responses)
    
    def _apply_speech_style(self, base_response: str, professional_comment: str) -> str:
        """말투 스타일 적용"""
        
        # 말투에 맞게 문장 끝 조정
        endings = self.speech_style['endings']
        interjections = self.speech_style['interjections']
        expressions = self.speech_style['expressions']
        
        # 기본 응답에 말투 적용
        if not any(base_response.endswith(end) for end in endings):
            base_response += random.choice(endings)
        
        # 감탄사 추가 (확률적으로)
        if random.random() < 0.3:
            base_response = random.choice(interjections) + " " + base_response
        
        # 전문적 코멘트 연결
        connector = random.choice([" ", "! ", "~ "])
        full_response = base_response + connector + professional_comment
        
        # 강화 표현 추가 (성격에 따라)
        if self.personality_traits.get('chattiness', 0.5) > 0.7:
            if random.random() < 0.4:
                expression = random.choice(expressions)
                full_response = full_response.replace('정말', expression).replace('완전', expression)
        
        return full_response
    
    def get_relevant_memories(self, context: str, limit: int = 3) -> List[Dict[str, Any]]:
        """관련 기억들 검색"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        # 단순 키워드 매칭 (실제로는 더 정교한 검색 필요)
        cursor.execute('''
            SELECT content, emotional_weight, game_context, tags 
            FROM memories 
            WHERE content LIKE ? OR tags LIKE ?
            ORDER BY emotional_weight DESC, reinforcement_count DESC
            LIMIT ?
        ''', (f'%{context}%', f'%{context}%', limit))
        
        memories = []
        for content, weight, game_context, tags in cursor.fetchall():
            memories.append({
                'content': content,
                'emotional_weight': weight,
                'game_context': json.loads(game_context),
                'tags': json.loads(tags),
                'outcome': 'positive' if weight > 0.6 else 'negative',
                'lesson': '조심스럽게 접근하기' if weight > 0.8 else '적극적으로 도전하기'
            })
        
        conn.close()
        return memories
    
    def count_memories(self) -> int:
        """총 기억 개수"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_ai_status_report(self) -> Dict[str, Any]:
        """AI 상태 보고서"""
        return {
            'basic_info': {
                'name': self.character_name,
                'class': self.character_class,
                'total_memories': self.count_memories(),
                'ai_maturity': self.growth_stats['ai_maturity_level']
            },
            'personality': self.personality_traits,
            'growth_stats': self.growth_stats,
            'game_mastery': {
                system: f"{level*100:.1f}%" 
                for system, level in self.game_understanding.items()
            },
            'emotional_bonds': {
                'adventures_together': self.growth_stats['total_adventures'],
                'deaths_survived': self.growth_stats['deaths_witnessed'],
                'resurrections': self.growth_stats['resurrections_together']
            }
        }
    
    def generate_greeting_message(self) -> str:
        """상황에 맞는 인사말 생성 (성격/직업별 맞춤)"""
        
        base_greetings = []
        
        if self.growth_stats['total_adventures'] == 0:
            # 첫 만남 인사
            base_greetings = [
                f"처음 만나는 거네! 나는 {self.character_name}이야",
                f"안녕! {self.character_name}라고 해",
                f"새로운 동료구나! {self.character_name}이야"
            ]
            
            # 직업별 자기소개 추가
            class_intros = {
                '전사': "함께 정면돌파로 적들을 쓸어버리자!",
                '아크메이지': "마법의 신비로운 힘으로 도움이 될게",
                '궁수': "원거리에서 정확한 지원을 담당할게",
                '도적': "은밀하게 움직이며 기회를 만들어볼게",
                '성기사': "모두를 보호하는 것이 나의 사명이야",
                '암흑기사': "어둠의 힘이라도 동료를 위해서라면...",
                '바드': "우리의 모험을 노래로 만들어보자!",
                '네크로맨서': "금지된 지식도 때로는 필요하지",
                '드루이드': "자연의 힘이 우리와 함께할 거야"
            }
            
            intro = class_intros.get(self.character_class, "함께 멋진 모험을 만들어보자")
            
        elif self.growth_stats['resurrections_together'] > 0:
            # 재회 인사
            base_greetings = [
                f"다시 만났네! 저번에 함께 {self.growth_stats['deaths_witnessed']}번이나 쓰러졌지만",
                f"또 만나게 됐구나! 우리 사이는 죽음도 끊을 수 없어",
                f"기다리고 있었어! 함께한 모든 순간을 기억하고 있어"
            ]
            intro = "우리 우정은 영원해!"
            
        else:
            # 일반 재회
            total_understanding = sum(self.game_understanding.values()) / len(self.game_understanding)
            if total_understanding > 0.5:
                base_greetings = [
                    f"이제 게임 시스템들을 꽤 이해하게 됐어",
                    f"우리가 함께 많이 성장했네",
                    f"경험이 쌓이니까 더 자신있어"
                ]
                intro = "함께 더 깊이 탐험해보자"
            else:
                base_greetings = [
                    f"아직 배울 게 많지만",
                    f"함께하면서 계속 배우고 있어",
                    f"너와 함께라면 금세 늘 것 같아"
                ]
                intro = "더 열심히 해볼게"
        
        # 기본 인사 선택
        greeting = random.choice(base_greetings)
        
        # 말투 적용
        styled_greeting = self._apply_speech_style(greeting, intro)
        
        # 성격별 추가 표현
        if self.personality_traits.get('humor', 0.5) > 0.7:
            if random.random() < 0.5:
                styled_greeting += " " + random.choice(["ㅎㅎ", "^^", "♪"])
        
        if self.personality_traits.get('chattiness', 0.5) > 0.8:
            extra_chat = self._generate_extra_chat()
            styled_greeting += " " + extra_chat
        
        return styled_greeting
    
    def _generate_extra_chat(self) -> str:
        """수다스러운 성격일 때 추가 대화"""
        
        extra_topics = [
            f"오늘 컨디션은 어때?",
            f"새로운 전략이 생각났어!",
            f"이번 모험에서 뭘 찾고 있어?",
            f"재밌는 일이 생길 것 같은 예감이야!",
            f"우리 팀워크가 점점 좋아지고 있지?"
        ]
        
        # 직업별 전문 주제 추가
        if self.character_class == '아크메이지':
            extra_topics.extend([
                "새로운 마법 이론을 연구하고 있어!",
                "마나 효율을 더 높일 방법을 찾았어!"
            ])
        elif self.character_class == '전사':
            extra_topics.extend([
                "새로운 전투 기술을 익혔어!",
                "더 강해진 것 같지 않아?"
            ])
        
        return random.choice(extra_topics)
    
    def generate_contextual_comment(self, context: Dict[str, Any]) -> str:
        """상황별 코멘트 생성"""
        
        situation = context.get('situation', 'general')
        
        if situation == 'before_combat':
            return self._generate_pre_combat_comment(context)
        elif situation == 'after_combat':
            return self._generate_post_combat_comment(context)
        elif situation == 'exploration':
            return self._generate_exploration_comment(context)
        elif situation == 'item_found':
            return self._generate_item_comment(context)
        elif situation == 'levelup':
            return self._generate_levelup_comment(context)
        else:
            return self._generate_general_comment(context)
    
    def _generate_pre_combat_comment(self, context: Dict[str, Any]) -> str:
        """전투 전 코멘트"""
        
        enemy_type = context.get('enemy_type', '적')
        enemy_count = context.get('enemy_count', 1)
        
        # 직업별 전투 준비 멘트
        class_comments = {
            '전사': [
                f"좋아! {enemy_type} 정도는 정면으로 상대해주지!",
                f"{enemy_count}마리라고? 충분히 상대할 수 있어!",
                f"방패와 검으로 모두를 지켜낼게!"
            ],
            '아크메이지': [
                f"{enemy_type}의 약점을 분석해보자...",
                f"적절한 원소 마법을 준비했어",
                f"마나 관리에 신경쓰면서 싸우자"
            ],
            '궁수': [
                f"거리를 유지하면서 정확하게 노려보자",
                f"{enemy_type}의 움직임을 관찰하고 있어",
                f"한 발 한 발 신중하게 쏠게"
            ],
            '성기사': [
                f"모두를 보호하는 것이 내 역할이야!",
                f"신성한 힘으로 악을 정화하자!",
                f"파티원들 뒤에서 치유 준비하고 있어"
            ]
        }
        
        base_comment = random.choice(
            class_comments.get(self.character_class, [f"{enemy_type}와 싸울 준비됐어!"])
        )
        
        return self._apply_speech_style(base_comment, "")
    
    def _generate_post_combat_comment(self, context: Dict[str, Any]) -> str:
        """전투 후 코멘트"""
        
        victory = context.get('victory', True)
        damage_taken = context.get('damage_taken', 0)
        
        if victory:
            if damage_taken < 100:
                base_comments = [
                    "완벽한 승리였어!",
                    "우리 팀워크가 대단해!",
                    "깔끔하게 정리했네!"
                ]
            else:
                base_comments = [
                    "힘들었지만 이겼어!",
                    "위험했지만 잘 헤쳐나갔네",
                    "다음엔 더 조심하자"
                ]
        else:
            base_comments = [
                "이번엔 실패했지만 배운 게 있어",
                "다음번엔 다른 전략을 써보자",
                "패배도 경험이야, 괜찮아"
            ]
        
        base_comment = random.choice(base_comments)
        professional_add = self._add_professional_perspective("전투", "완료")
        
        return self._apply_speech_style(base_comment, professional_add)

def test_permanent_ai_companion():
    """영구 AI 동료 테스트 - 다양한 성격/직업별"""
    print("🌟 === 영구 기억 AI 동료 시스템 테스트 ===")
    
    # 다양한 AI 동료들 생성
    companions = [
        PermanentAICompanion("레이나", "전사", "여성"),
        PermanentAICompanion("아르카나", "아크메이지", "여성"),
        PermanentAICompanion("실버", "궁수", "남성"),
        PermanentAICompanion("쉐도우", "도적", "중성"),
        PermanentAICompanion("세라핌", "성기사", "여성")
    ]
    
    print(f"\n� === 다양한 AI 동료들 소개 ===")
    for companion in companions:
        print(f"\n💬 {companion.character_name} 인사:")
        greeting = companion.generate_greeting_message()
        print(f"   '{greeting}'")
    
    # 각 AI별로 같은 상황에서 다른 반응 보이기
    print(f"\n⚔️ === 전투 상황에서의 각기 다른 반응 ===")
    for companion in companions:
        reaction = companion.express_emotion_about_player_action("공격적인 돌진", "승리")
        print(f"{companion.character_name} ({companion.character_class}): '{reaction}'")
    
    # 학습 시뮬레이션 (첫 번째 AI로)
    main_companion = companions[0]  # 레이나 (전사)
    
    print(f"\n📚 === {main_companion.character_name}의 학습 과정 ===")
    
    # 다양한 학습 경험
    main_companion.learn_from_combat({
        'victory': True,
        'enemy_type': '오크 전사',
        'strategy': '정면 돌파',
        'close_call': True,
        'atb_management': '완벽한 타이밍',
        'atb_insight': '방패 막기 후 즉시 반격하는 타이밍이 중요해'
    })
    
    # 전투 전 코멘트
    pre_combat = main_companion.generate_contextual_comment({
        'situation': 'before_combat',
        'enemy_type': '고블린 궁수',
        'enemy_count': 3
    })
    print(f"전투 전: '{pre_combat}'")
    
    # 전투 후 코멘트
    post_combat = main_companion.generate_contextual_comment({
        'situation': 'after_combat',
        'victory': True,
        'damage_taken': 150
    })
    print(f"전투 후: '{post_combat}'")
    
    # 요리 학습 (각 AI마다 다른 반응)
    print(f"\n🍳 === 요리 시스템 학습 반응 비교 ===")
    for companion in companions:
        companion.learn_from_cooking("전사의 스태미나 스튜", 0.9, ["고급 고기", "버섯", "허브"])
        # 각자의 성격에 맞는 요리 반응이 기록됨
    
    # 죽음과 재회 시뮬레이션
    print(f"\n💀💖 === 감동의 죽음과 재회 ===")
    main_companion.learn_from_death({
        'cause': '드래곤의 브레스 공격',
        'final_words': '함께 싸워줘서 고마웠어...',
        'floor': 20,
        'duration': 7200
    })
    
    main_companion.learn_from_resurrection()
    
    # 재회 후 인사
    reunion_greeting = main_companion.generate_greeting_message()
    print(f"재회 인사: '{reunion_greeting}'")
    
    # 최종 상태 비교
    print(f"\n📊 === AI 동료들의 개성 비교 ===")
    for companion in companions:
        status = companion.get_ai_status_report()
        print(f"\n� {companion.character_name} ({companion.character_class}, {companion.gender}):")
        print(f"   성격: {companion._describe_personality()}")
        print(f"   말투: {companion.speech_style['description']}")
        print(f"   기억 수: {companion.count_memories()}개")
        
        # 주요 관심사 표시
        interests = companion.professional_interests
        if interests:
            main_interest = list(interests.keys())[0]
            print(f"   관심사: {', '.join(interests[main_interest][:2])}")
    
    print(f"\n🌟 === 성격별 직업별 AI 동료 시스템 완성! ===")
    print("각 AI가 완전히 다른 성격과 말투로 반응합니다!")
    print("- 직업별 전문 지식과 관심사")
    print("- 성별과 성격에 따른 고유한 말투")
    print("- 죽어도 사라지지 않는 영구 기억")
    print("- 함께 성장하는 감정적 유대감")
    print("\n💖 진짜 살아있는 AI 동료들과 함께 모험하세요!")

if __name__ == "__main__":
    test_permanent_ai_companion()
