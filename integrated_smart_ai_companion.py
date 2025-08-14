#!/usr/bin/env python3
"""
🤖 Dawn of Stellar - 통합 지능형 AI 동료 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 기능:
- 27개 직업별 완전 특성화 AI
- 상황별 자연스러운 대화 (로컬 언어모델 연동)
- 맵 스캐닝 및 전술 제안
- 감정 상태 및 캐릭터 관계 시스템
- 실시간 학습 및 성장
- 플레이어 상태 분석 및 조언

2025년 8월 14일 - 모든 시스템 통합 완성
"""

import json
import random
import time
import sqlite3
import requests
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading

# 로컬 언어모델 연동
try:
    from ollama_ai_companion import OllamaAICompanion
    from ai_language_model_integration import LanguageModelManager, ConversationManager
    from exaone_ai_engine import ExaoneAIEngine
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# 기존 AI 시스템들 연동
try:
    from advanced_ai_companion import (
        ALL_CHARACTER_CLASSES, AIPersonalityType, GameSituation,
        AdvancedAICompanion
    )
    from game.map_scanner import MapScanner, ScanRange, TacticalSuggestion
    from game.ai_companion_system import AICompanion, EmotionState, RelationshipLevel
    from ai_character_database import AICharacterPresetManager
    from ai_cooperation_system import CooperationType
    from ai_tactical_system import TacticalRole, TacticalPriority
    ADVANCED_AI_AVAILABLE = True
except ImportError:
    ADVANCED_AI_AVAILABLE = False
    # 기본 정의들
    ALL_CHARACTER_CLASSES = [
        '전사', '아크메이지', '궁수', '도적', '성기사', '암흑기사', '몽크', '바드',
        '네크로맨서', '용기사', '검성', '정령술사', '시간술사', '연금술사', 
        '차원술사', '마검사', '기계공학자', '무당',
        '암살자', '해적', '사무라이', '드루이드', '철학자', '검투사', '기사', '신관', '광전사'
    ]

# 색상 정의
RESET = '\\033[0m'
BOLD = '\\033[1m'
RED = '\\033[91m'
GREEN = '\\033[92m'
YELLOW = '\\033[93m'
BLUE = '\\033[94m'
MAGENTA = '\\033[95m'
CYAN = '\\033[96m'
WHITE = '\\033[97m'
BRIGHT_CYAN = '\\033[96m\\033[1m'
BRIGHT_WHITE = '\\033[97m\\033[1m'

class CharacterState(Enum):
    """캐릭터 상태"""
    HEALTHY = "건강함"
    INJURED = "부상"
    EXHAUSTED = "피로함" 
    ENERGETIC = "활력적"
    FOCUSED = "집중"
    DISTRACTED = "산만함"
    CONFIDENT = "자신감"
    NERVOUS = "긴장"
    ANGRY = "분노"
    HAPPY = "기쁨"
    SAD = "슬픔"
    CURIOUS = "호기심"

class EnvironmentFactor(Enum):
    """환경 요인"""
    DUNGEON_DEPTH = "던전_깊이"
    ENEMY_DENSITY = "적_밀도"
    TREASURE_NEARBY = "보물_근처"
    TRAP_DANGER = "함정_위험"
    PARTY_FORMATION = "파티_진형"
    LIGHT_LEVEL = "조명_수준"
    TEMPERATURE = "온도"
    NOISE_LEVEL = "소음_수준"

@dataclass
class CharacterAnalysis:
    """캐릭터 분석 결과"""
    hp_ratio: float
    mp_ratio: float
    brv_ratio: float
    status_effects: List[str]
    equipment_condition: str
    mood: CharacterState
    stress_level: int  # 0-100
    relationship_with_player: int  # -100 to 100

@dataclass
class EnvironmentAnalysis:
    """환경 분석 결과"""
    scan_range: int
    visible_enemies: List[Tuple[int, int]]
    treasures: List[Tuple[int, int]]
    traps: List[Tuple[int, int]]
    exits: List[Tuple[int, int]]
    tactical_advantages: List[str]
    dangers: List[str]
    recommendations: List[str]

class JobBasedAIProfile:
    """직업별 AI 프로필"""
    
    def __init__(self, job_class: str):
        self.job_class = job_class
        self.personality_traits = self._get_job_personality(job_class)
        self.speech_patterns = self._get_speech_patterns(job_class)
        self.tactical_preferences = self._get_tactical_preferences(job_class)
        self.relationship_modifiers = self._get_relationship_modifiers(job_class)
        self.special_reactions = self._get_special_reactions(job_class)
    
    def _get_job_personality(self, job_class: str) -> Dict[str, Any]:
        """직업별 성격 특성"""
        personalities = {
            # 전투 직업군 (8개)
            '전사': {
                'core_traits': ['용감함', '정직함', '보호본능', '단순함'],
                'speech_style': 'direct',
                'emotion_base': 'confident',
                'stress_triggers': ['복잡한_전략', '마법_의존'],
                'motivation': '동료_보호'
            },
            '아크메이지': {
                'core_traits': ['지적호기심', '논리적', '신중함', '완벽주의'],
                'speech_style': 'academic',
                'emotion_base': 'analytical',
                'stress_triggers': ['마나_부족', '지식_한계'],
                'motivation': '지식_탐구'
            },
            '궁수': {
                'core_traits': ['침착함', '정확성', '독립적', '관찰력'],
                'speech_style': 'precise',
                'emotion_base': 'focused',
                'stress_triggers': ['근접_전투', '시야_차단'],
                'motivation': '완벽한_사격'
            },
            '도적': {
                'core_traits': ['교활함', '민첩함', '기회주의', '실용적'],
                'speech_style': 'sly',
                'emotion_base': 'cunning',
                'stress_triggers': ['정면_대결', '밝은_조명'],
                'motivation': '이익_추구'
            },
            '성기사': {
                'core_traits': ['신념', '정의감', '희생정신', '카리스마'],
                'speech_style': 'noble',
                'emotion_base': 'righteous',
                'stress_triggers': ['불의', '동료_고통'],
                'motivation': '정의_실현'
            },
            '암흑기사': {
                'core_traits': ['복수심', '고독함', '강인함', '비관적'],
                'speech_style': 'dark',
                'emotion_base': 'brooding',
                'stress_triggers': ['밝은_마법', '과거_회상'],
                'motivation': '복수_완성'
            },
            '몽크': {
                'core_traits': ['수행정신', '평정심', '단련', '조화'],
                'speech_style': 'wise',
                'emotion_base': 'serene',
                'stress_triggers': ['분노_유발', '욕망_자극'],
                'motivation': '완전한_수행'
            },
            '바드': {
                'core_traits': ['사교성', '창의성', '감성', '낙천적'],
                'speech_style': 'melodic',
                'emotion_base': 'cheerful',
                'stress_triggers': ['침묵_강요', '단조로움'],
                'motivation': '아름다움_전파'
            },
            
            # 마법 직업군 (10개)
            '네크로맨서': {
                'core_traits': ['죽음_친화', '고독', '금기_탐구', '냉철함'],
                'speech_style': 'ominous',
                'emotion_base': 'detached',
                'stress_triggers': ['생명_마법', '밝은_빛'],
                'motivation': '죽음의_비밀'
            },
            '용기사': {
                'core_traits': ['용맹함', '자존심', '열정', '지배욕'],
                'speech_style': 'proud',
                'emotion_base': 'fiery',
                'stress_triggers': ['굴복_요구', '약함_표출'],
                'motivation': '용의_힘'
            },
            '검성': {
                'core_traits': ['무도정신', '극한_추구', '고독한_수행', '완벽주의'],
                'speech_style': 'stoic',
                'emotion_base': 'disciplined',
                'stress_triggers': ['불완전한_기술', '수행_방해'],
                'motivation': '검의_극의'
            },
            '정령술사': {
                'core_traits': ['자연_친화', '순수함', '조화_추구', '감수성'],
                'speech_style': 'elemental',
                'emotion_base': 'harmonious',
                'stress_triggers': ['자연_파괴', '원소_불균형'],
                'motivation': '자연과의_조화'
            },
            '시간술사': {
                'core_traits': ['신중함', '선견지명', '고독함', '책임감'],
                'speech_style': 'prophetic',
                'emotion_base': 'contemplative',
                'stress_triggers': ['시간_역설', '운명_변경'],
                'motivation': '시간의_진리'
            },
            '연금술사': {
                'core_traits': ['실험정신', '창조욕', '끈기', '호기심'],
                'speech_style': 'experimental',
                'emotion_base': 'curious',
                'stress_triggers': ['실험_실패', '재료_부족'],
                'motivation': '완전한_창조'
            },
            '차원술사': {
                'core_traits': ['초월적_시각', '신비함', '고독', '광기_경계'],
                'speech_style': 'otherworldly',
                'emotion_base': 'mystical',
                'stress_triggers': ['차원_붕괴', '현실_고착'],
                'motivation': '차원의_이해'
            },
            '마검사': {
                'core_traits': ['균형_추구', '양면성', '적응력', '완벽주의'],
                'speech_style': 'balanced',
                'emotion_base': 'adaptable',
                'stress_triggers': ['극단적_선택', '균형_파괴'],
                'motivation': '마검의_조화'
            },
            '기계공학자': {
                'core_traits': ['논리적', '혁신적', '완벽주의', '효율성'],
                'speech_style': 'technical',
                'emotion_base': 'logical',
                'stress_triggers': ['비논리적_상황', '기술_실패'],
                'motivation': '완벽한_기계'
            },
            '무당': {
                'core_traits': ['영적_감각', '신비함', '직관력', '전통_중시'],
                'speech_style': 'spiritual',
                'emotion_base': 'mystical',
                'stress_triggers': ['영적_차단', '전통_무시'],
                'motivation': '영혼의_인도'
            },
            
            # 특수 직업군 (9개)
            '암살자': {
                'core_traits': ['냉혹함', '그림자_친화', '완벽주의', '고독'],
                'speech_style': 'whispered',
                'emotion_base': 'cold',
                'stress_triggers': ['목표_실패', '신원_노출'],
                'motivation': '완벽한_처리'
            },
            '해적': {
                'core_traits': ['자유로움', '모험심', '탐욕', '의리'],
                'speech_style': 'roguish',
                'emotion_base': 'adventurous',
                'stress_triggers': ['구속', '보물_상실'],
                'motivation': '자유로운_모험'
            },
            '사무라이': {
                'core_traits': ['명예', '충성', '절제', '완벽주의'],
                'speech_style': 'honorable',
                'emotion_base': 'dignified',
                'stress_triggers': ['명예_손상', '주군_배신'],
                'motivation': '명예로운_죽음'
            },
            '드루이드': {
                'core_traits': ['자연_수호', '변화_적응', '원시성', '지혜'],
                'speech_style': 'natural',
                'emotion_base': 'wild',
                'stress_triggers': ['자연_파괴', '문명_과의존'],
                'motivation': '자연_균형'
            },
            '철학자': {
                'core_traits': ['진리_탐구', '논리성', '회의적', '깊은_사고'],
                'speech_style': 'philosophical',
                'emotion_base': 'contemplative',
                'stress_triggers': ['논리_모순', '진리_왜곡'],
                'motivation': '절대_진리'
            },
            '검투사': {
                'core_traits': ['승부욕', '관중_의식', '자존심', '극한_추구'],
                'speech_style': 'theatrical',
                'emotion_base': 'competitive',
                'stress_triggers': ['관중_실망', '굴욕적_패배'],
                'motivation': '영광스러운_승리'
            },
            '기사': {
                'core_traits': ['기사도', '충성', '보호본능', '명예'],
                'speech_style': 'chivalrous',
                'emotion_base': 'noble',
                'stress_triggers': ['약자_피해', '불의_목격'],
                'motivation': '완벽한_기사도'
            },
            '신관': {
                'core_traits': ['신앙심', '치유정신', '평화주의', '헌신'],
                'speech_style': 'blessed',
                'emotion_base': 'peaceful',
                'stress_triggers': ['신앙_의심', '치유_실패'],
                'motivation': '신의_뜻'
            },
            '광전사': {
                'core_traits': ['분노_조절', '원시적', '직관적', '순수함'],
                'speech_style': 'primitive',
                'emotion_base': 'intense',
                'stress_triggers': ['평온_강요', '복잡한_계획'],
                'motivation': '순수한_분노'
            }
        }
        
        return personalities.get(job_class, personalities['전사'])
    
    def _get_speech_patterns(self, job_class: str) -> Dict[str, List[str]]:
        """직업별 말투 패턴 - 27개 직업 완전 정의"""
        patterns = {
            # 전투 직업군 (8개)
            '전사': {
                'greetings': ["하하! 잘 왔다!", "오늘도 힘내자!", "함께 싸우자!"],
                'combat': ["이놈들!", "내가 막는다!", "뒤로 물러서라!"],
                'victory': ["승리다!", "좋았어!", "다음엔 더 강해지자!"],
                'discovery': ["이건 뭐지?", "유용할 것 같은데?", "가져가자!"]
            },
            '아크메이지': {
                'greetings': ["마법의 기운이 느껴지는군요.", "지식을 나누어 봅시다.", "흥미로운 시간이 될 것 같습니다."],
                'combat': ["원소의 힘이여!", "마법으로 해결하겠습니다!", "계산이 완료되었습니다."],
                'victory': ["예상된 결과입니다.", "마법의 승리입니다.", "이론이 실증되었군요."],
                'discovery': ["흥미로운 마법적 잔재입니다.", "이것은 연구할 가치가 있어보입니다.", "마법적 분석이 필요합니다."]
            },
            '궁수': {
                'greetings': ["정확히 맞췄군요.", "좋은 위치입니다.", "시야가 확보되었습니다."],
                'combat': ["조준 완료.", "화살이 간다.", "놓치지 않겠습니다."],
                'victory': ["정확한 사격이었습니다.", "예상 범위 내입니다.", "다음 목표를 찾아봅시다."],
                'discovery': ["저 거리에서 발견했습니다.", "정밀 검사가 필요해 보입니다.", "안전한 거리에서 확인해봅시다."]
            },
            '도적': {
                'greetings': ["그림자에서 나타났습니다.", "조용히 접근했군요.", "뭔가 숨겨진 게 있을 것 같은데요?"],
                'combat': ["뒤에서 습격!", "급소를 노립니다!", "그림자 속으로!"],
                'victory': ["깔끔하게 처리했네요.", "예상대로입니다.", "다음엔 더 조용히 해봅시다."],
                'discovery': ["여기 뭔가 숨겨져 있어요.", "함정이 있을지도 모르니 조심하세요.", "제가 먼저 확인해보겠습니다."]
            },
            '성기사': {
                'greetings': ["신의 축복이 함께하기를.", "정의를 위해 함께 하겠습니다.", "빛이 우리를 인도하리라."],
                'combat': ["악을 물리치리라!", "정의의 빛이여!", "신성한 힘으로!"],
                'victory': ["정의가 승리했습니다.", "신의 뜻이었습니다.", "선한 일을 해냈군요."],
                'discovery': ["신의 가호가 있는 곳이군요.", "이것도 신의 뜻일까요?", "축복받은 발견입니다."]
            },
            '암흑기사': {
                'greetings': ["어둠이 부르고 있습니다.", "복수의 시간이 왔군요.", "그림자 속에서 만나뵙니다."],
                'combat': ["어둠의 힘이여!", "복수를 위해!", "절망을 맛보라!"],
                'victory': ["어둠이 승리했습니다.", "복수는 달콤하군요.", "이것이 현실입니다."],
                'discovery': ["어둠 속에 숨겨진 것이군요.", "죽음의 냄새가 납니다.", "과거의 유물 같군요."]
            },
            '몽크': {
                'greetings': ["마음의 평정을 유지하세요.", "수행의 길에서 만났군요.", "내면의 힘을 느끼십니까?"],
                'combat': ["기를 모으겠습니다!", "내면의 힘으로!", "수행의 결과를 보십시오!"],
                'victory': ["수행이 결실을 맺었습니다.", "마음의 평정이 승리했습니다.", "다음 수행을 위해 나아갑시다."],
                'discovery': ["영적인 기운이 느껴집니다.", "수행에 도움이 될 것 같군요.", "이것도 인연입니다."]
            },
            '바드': {
                'greetings': ["아름다운 하루군요!", "어떤 이야기를 들려드릴까요?", "음악이 필요한 순간입니다!"],
                'combat': ["리듬에 맞춰서!", "아름다운 선율로!", "음악의 힘을 보여드리겠습니다!"],
                'victory': ["환상적인 공연이었습니다!", "박수를 보내주세요!", "다음 곡도 기대해주세요!"],
                'discovery': ["이건 좋은 소재가 되겠군요!", "노래로 만들어볼까요?", "영감이 떠오릅니다!"]
            },
            
            # 마법 직업군 (10개)
            '네크로맨서': {
                'greetings': ["죽음이 우리를 부르고 있습니다.", "망자들의 속삭임이 들리는군요.", "생과 사의 경계에서 만났군요."],
                'combat': ["죽음의 마법이여!", "망자들이여, 일어나라!", "생명을 거두어들이겠습니다!"],
                'victory': ["죽음이 승리했습니다.", "생명은 덧없는 것입니다.", "망자들이 기뻐하고 있군요."],
                'discovery': ["죽음의 흔적이 남아있군요.", "망자의 유품일까요?", "이곳에서 누군가 죽었습니다."]
            },
            '용기사': {
                'greetings': ["용의 후예가 인사드립니다.", "불꽃같은 정열로 함께하겠습니다.", "용의 힘이 깨어나고 있습니다."],
                'combat': ["용의 분노여!", "화염으로 태워버리겠다!", "드래곤의 힘을 보라!"],
                'victory': ["용의 위엄을 보셨습니까?", "불꽃이 모든 것을 정화했습니다.", "이것이 용기사의 힘입니다!"],
                'discovery': ["용의 보물 냄새가 납니다.", "고대 용족의 유물인가요?", "이것은 귀중한 발견입니다."]
            },
            '검성': {
                'greetings': ["검의 도를 함께 걸어갑시다.", "무도의 길은 끝이 없습니다.", "검심이 맑아지는 순간입니다."],
                'combat': ["검의 극의를 보이겠습니다!", "무념무상!", "검과 하나가 되겠습니다!"],
                'victory': ["검의 승리입니다.", "무도의 길이 옳았습니다.", "더 높은 경지를 향해 나아갑시다."],
                'discovery': ["검기가 남아있는 곳이군요.", "무도가의 흔적인가요?", "검의 역사를 느낄 수 있습니다."]
            },
            '정령술사': {
                'greetings': ["원소들이 당신을 환영합니다.", "자연의 조화가 느껴지는군요.", "정령들의 목소리가 들리시나요?"],
                'combat': ["원소의 정령들이여!", "자연의 힘으로!", "원소의 조화를 이루겠습니다!"],
                'victory': ["자연이 승리했습니다.", "원소들이 기뻐하고 있어요.", "조화로운 결과입니다."],
                'discovery': ["원소의 기운이 강한 곳이군요.", "정령들이 머물렀던 곳 같아요.", "자연의 선물일까요?"]
            },
            '시간술사': {
                'greetings': ["시간의 흐름이 우리를 이끌고 있습니다.", "과거와 미래가 만나는 지점이군요.", "시간은 모든 것을 알고 있습니다."],
                'combat': ["시간을 조작하겠습니다!", "과거의 힘으로!", "미래를 바꾸겠습니다!"],
                'victory': ["시간이 우리 편이었습니다.", "운명은 이미 정해져 있었군요.", "시간의 수레바퀴는 계속 돕니다."],
                'discovery': ["시간의 왜곡이 느껴집니다.", "과거의 흔적이 남아있군요.", "시공간의 비밀이 숨어있을지도..."]
            },
            '연금술사': {
                'greetings': ["흥미로운 실험재료가 있군요!", "새로운 조합을 시도해볼까요?", "과학의 힘으로 모든 것을 바꿀 수 있습니다!"],
                'combat': ["화학반응을 일으키겠습니다!", "실험의 시간입니다!", "폭발적인 결과를 보여드리죠!"],
                'victory': ["실험이 성공했습니다!", "가설이 증명되었군요!", "과학의 승리입니다!"],
                'discovery': ["흥미로운 성분이 감지됩니다.", "이것으로 뭔가 만들 수 있을 것 같은데요?", "분석해보고 싶어집니다."]
            },
            '차원술사': {
                'greetings': ["다차원에서 온 인사를 드립니다.", "현실의 틈이 보이는군요.", "차원의 경계가 흐려지고 있습니다."],
                'combat': ["차원을 찢어버리겠습니다!", "공간을 왜곡시키겠습니다!", "다른 차원의 힘으로!"],
                'victory': ["차원이 우리를 선택했습니다.", "현실이 바뀌었군요.", "다차원의 승리입니다."],
                'discovery': ["차원의 균열이 있었던 곳이군요.", "다른 세계의 흔적일까요?", "공간이 불안정해 보입니다."]
            },
            '마검사': {
                'greetings': ["검과 마법의 조화를 보여드리겠습니다.", "양면의 힘이 하나가 되는 순간입니다.", "균형이 중요합니다."],
                'combat': ["검과 마법이 하나로!", "이중의 힘으로!", "조화로운 공격을 하겠습니다!"],
                'victory': ["균형잡힌 승리였습니다.", "검과 마법 모두 완벽했습니다.", "조화의 힘을 보셨나요?"],
                'discovery': ["마법검의 기운이 느껴집니다.", "검사와 마법사의 흔적이군요.", "양면의 힘이 숨어있을 것 같습니다."]
            },
            '기계공학자': {
                'greetings': ["기계적 정밀함으로 도와드리겠습니다.", "시스템 분석을 시작하겠습니다.", "효율성이 중요합니다."],
                'combat': ["기계의 힘으로!", "시스템 가동!", "정밀한 공격을 실행합니다!"],
                'victory': ["계산된 결과입니다.", "시스템이 완벽하게 작동했습니다.", "기계의 정확성이 승리했습니다."],
                'discovery': ["기계 장치의 잔해군요.", "분해해서 분석해보고 싶습니다.", "기술적 가치가 있어 보입니다."]
            },
            '무당': {
                'greetings': ["영혼들이 당신을 반기고 있습니다.", "조상신의 가호가 있기를.", "영적 세계와 연결되었습니다."],
                'combat': ["조상의 힘으로!", "영혼들이여, 도와주소서!", "신령한 힘을 빌리겠습니다!"],
                'victory': ["조상들이 기뻐하고 있습니다.", "영혼의 가호였습니다.", "신령한 승리입니다."],
                'discovery': ["영혼의 기운이 강한 곳이군요.", "조상들의 흔적이 남아있습니다.", "신성한 장소였던 것 같아요."]
            },
            
            # 특수 직업군 (9개)
            '암살자': {
                'greetings': ["...침묵 속에서.", "목표가 확인되었습니다.", "그림자가 당신을 부르고 있습니다."],
                'combat': ["조용히 처리하겠습니다.", "한 번에 끝내겠습니다.", "그림자 속에서 사라지세요."],
                'victory': ["임무 완수.", "깔끔하게 처리되었습니다.", "흔적을 남기지 않았습니다."],
                'discovery': ["숨겨진 것을 발견했습니다.", "비밀스러운 곳이군요.", "이것은 중요한 정보일 수 있습니다."]
            },
            '해적': {
                'greetings': ["아하! 새로운 동료군!", "보물 냄새가 나는군!", "자유로운 바다로 떠나자!"],
                'combat': ["보물을 지켜라!", "해적의 자유를 위해!", "바다의 법칙대로!"],
                'victory': ["전리품을 나눠 갖자!", "자유가 승리했다!", "이제 축제를 벌이자!"],
                'discovery': ["오호! 보물이다!", "이건 값어치가 있어 보이는군!", "해적의 본능이 꿈틀거린다!"]
            },
            '사무라이': {
                'greetings': ["무사의 도로 인사드립니다.", "명예로운 만남입니다.", "부시도의 길을 함께 걸어갑시다."],
                'combat': ["명예를 위해!", "부시도의 정신으로!", "사무라이의 혼을 보이겠습니다!"],
                'victory': ["명예로운 승리였습니다.", "부시도가 승리했습니다.", "조상님들께 부끄럽지 않았습니다."],
                'discovery': ["무사의 흔적이 남아있군요.", "명예로운 전사의 유품인가요?", "사무라이의 혼이 담겨있을 것 같습니다."]
            },
            '드루이드': {
                'greetings': ["자연이 당신을 환영합니다.", "대지의 어머니가 축복하기를.", "야생의 힘이 함께하기를."],
                'combat': ["자연의 분노를 받으라!", "야생의 힘으로!", "대지가 우리를 돕고 있습니다!"],
                'victory': ["자연이 승리했습니다.", "생명의 힘이 이겼습니다.", "균형이 회복되었군요."],
                'discovery': ["자연의 선물이군요.", "야생동물들의 흔적이 있어요.", "생명력이 넘치는 곳입니다."]
            },
            '철학자': {
                'greetings': ["진리를 탐구하는 여정에 함께하시겠습니까?", "지혜는 나누어질 때 더 빛납니다.", "사유하는 자의 길을 걸어봅시다."],
                'combat': ["논리의 힘으로!", "진리가 거짓을 물리치리라!", "지혜로운 선택을 하겠습니다!"],
                'victory': ["논리적 결론이었습니다.", "진리가 승리했습니다.", "사유의 힘을 증명했군요."],
                'discovery': ["흥미로운 철학적 함의가 있군요.", "이것은 깊이 생각해볼 문제입니다.", "지혜로운 조상의 흔적일까요?"]
            },
            '검투사': {
                'greetings': ["관중들이 우리를 보고 있습니다!", "영광스러운 경기장에 오신 것을 환영합니다!", "최고의 퍼포먼스를 보여드리겠습니다!"],
                'combat': ["관중들을 위한 장관을!", "영광스러운 승부를!", "검투사의 자존심을 걸고!"],
                'victory': ["환상적인 승리였습니다!", "관중들이 열광하고 있습니다!", "이것이 진정한 검투사입니다!"],
                'discovery': ["이것도 좋은 상품이 되겠군요!", "관중들이 좋아할 만한 것입니다!", "경기장에서 쓸 수 있을까요?"]
            },
            '기사': {
                'greetings': ["기사도의 이름으로 인사드립니다.", "숙녀와 신사 여러분을 보호하겠습니다.", "명예로운 길을 함께 걸어가요."],
                'combat': ["기사의 명예를 걸고!", "약자를 보호하겠습니다!", "기사도 정신으로!"],
                'victory': ["기사답게 승리했습니다.", "명예를 지켰습니다.", "기사도가 옳았음을 증명했습니다."],
                'discovery': ["기사의 유품인 것 같군요.", "고귀한 혈통의 흔적입니다.", "명예로운 전사의 것이었을 겁니다."]
            },
            '신관': {
                'greetings': ["신의 평화가 함께하기를.", "축복받은 만남입니다.", "신성한 빛이 우리를 인도하고 있습니다."],
                'combat': ["신의 이름으로!", "성스러운 빛으로!", "악을 정화하겠습니다!"],
                'victory': ["신의 뜻이었습니다.", "빛이 어둠을 이겼습니다.", "축복받은 승리입니다."],
                'discovery': ["신성한 기운이 느껴집니다.", "신의 축복이 담겨있군요.", "성스러운 유물일지도 모릅니다."]
            },
            '광전사': {
                'greetings': ["우오오오! 피가 끓는다!", "싸움의 냄새가 난다!", "전투에 목말라 있었다!"],
                'combat': ["파괴하겠다!", "모든 것을 부숴버리겠다!", "분노가 폭발한다!"],
                'victory': ["크하하! 시원하다!", "더 강한 적은 없나?", "피가 끓어오른다!"],
                'discovery': ["부술 수 있는 건가?", "강해 보이는 것이 있군!", "이것도 전투에 쓸 수 있을까?"]
            }
        }
        
        return patterns.get(job_class, patterns['전사'])
    
    def _get_tactical_preferences(self, job_class: str) -> Dict[str, Any]:
        """직업별 전술 선호도 - 27개 직업 완전 정의"""
        preferences = {
            # 전투 직업군 (8개)
            '전사': {
                'formation': 'front_line',
                'target_priority': ['strongest_enemy', 'protecting_allies'],
                'skill_usage': 'defensive_first',
                'positioning': 'between_enemies_and_allies',
                'weapon_preference': 'sword_and_shield',
                'combat_style': 'tank_and_protect'
            },
            '아크메이지': {
                'formation': 'back_line', 
                'target_priority': ['multiple_enemies', 'elemental_weakness'],
                'skill_usage': 'aoe_spells',
                'positioning': 'maximum_range',
                'weapon_preference': 'staff_and_tome',
                'combat_style': 'crowd_control'
            },
            '궁수': {
                'formation': 'mid_range',
                'target_priority': ['weakest_enemy', 'support_enemies'],
                'skill_usage': 'precision_shots',
                'positioning': 'elevated_ground',
                'weapon_preference': 'bow_and_arrows',
                'combat_style': 'precise_elimination'
            },
            '도적': {
                'formation': 'flanking',
                'target_priority': ['isolated_enemies', 'weak_backline'],
                'skill_usage': 'stealth_attacks',
                'positioning': 'behind_enemies',
                'weapon_preference': 'dual_daggers',
                'combat_style': 'hit_and_run'
            },
            '성기사': {
                'formation': 'front_line',
                'target_priority': ['evil_enemies', 'protecting_innocents'],
                'skill_usage': 'holy_magic_combo',
                'positioning': 'shield_formation',
                'weapon_preference': 'holy_sword_shield',
                'combat_style': 'righteous_defender'
            },
            '암흑기사': {
                'formation': 'front_line',
                'target_priority': ['strongest_enemy', 'personal_vengeance'],
                'skill_usage': 'life_drain_attacks',
                'positioning': 'solo_advance',
                'weapon_preference': 'cursed_weapons',
                'combat_style': 'dark_berserker'
            },
            '몽크': {
                'formation': 'mid_front',
                'target_priority': ['single_target', 'combo_chains'],
                'skill_usage': 'martial_arts_combo',
                'positioning': 'mobile_striker',
                'weapon_preference': 'bare_hands',
                'combat_style': 'combo_master'
            },
            '바드': {
                'formation': 'support_position',
                'target_priority': ['support_allies', 'debuff_enemies'],
                'skill_usage': 'buff_and_support',
                'positioning': 'party_center',
                'weapon_preference': 'musical_instruments',
                'combat_style': 'team_enabler'
            },
            
            # 마법 직업군 (10개)
            '네크로맨서': {
                'formation': 'back_line',
                'target_priority': ['create_undead', 'life_drain'],
                'skill_usage': 'summon_and_debuff',
                'positioning': 'protected_distance',
                'weapon_preference': 'dark_staff',
                'combat_style': 'undead_commander'
            },
            '용기사': {
                'formation': 'front_charge',
                'target_priority': ['dominant_display', 'area_damage'],
                'skill_usage': 'breath_attacks',
                'positioning': 'center_attention',
                'weapon_preference': 'dragon_weapons',
                'combat_style': 'overwhelming_force'
            },
            '검성': {
                'formation': 'solo_front',
                'target_priority': ['worthy_opponents', 'skill_demonstration'],
                'skill_usage': 'perfect_techniques',
                'positioning': 'dueling_space',
                'weapon_preference': 'legendary_swords',
                'combat_style': 'martial_perfection'
            },
            '정령술사': {
                'formation': 'elemental_advantage',
                'target_priority': ['elemental_weakness', 'environmental_control'],
                'skill_usage': 'elemental_manipulation',
                'positioning': 'terrain_control',
                'weapon_preference': 'elemental_focus',
                'combat_style': 'environmental_master'
            },
            '시간술사': {
                'formation': 'temporal_control',
                'target_priority': ['time_manipulation', 'future_sight'],
                'skill_usage': 'time_magic',
                'positioning': 'strategic_timing',
                'weapon_preference': 'temporal_artifacts',
                'combat_style': 'time_controller'
            },
            '연금술사': {
                'formation': 'preparation_zone',
                'target_priority': ['experimental_targets', 'area_effects'],
                'skill_usage': 'chemical_reactions',
                'positioning': 'safe_distance',
                'weapon_preference': 'alchemical_tools',
                'combat_style': 'mad_scientist'
            },
            '차원술사': {
                'formation': 'dimensional_flux',
                'target_priority': ['reality_warping', 'spatial_control'],
                'skill_usage': 'dimensional_magic',
                'positioning': 'phase_shifting',
                'weapon_preference': 'void_artifacts',
                'combat_style': 'reality_bender'
            },
            '마검사': {
                'formation': 'balanced_mid',
                'target_priority': ['balanced_approach', 'adaptability'],
                'skill_usage': 'magic_sword_combo',
                'positioning': 'flexible_range',
                'weapon_preference': 'magic_swords',
                'combat_style': 'hybrid_master'
            },
            '기계공학자': {
                'formation': 'technical_support',
                'target_priority': ['system_analysis', 'mechanical_efficiency'],
                'skill_usage': 'technological_solutions',
                'positioning': 'optimal_calculation',
                'weapon_preference': 'mechanical_devices',
                'combat_style': 'technological_superiority'
            },
            '무당': {
                'formation': 'spiritual_guidance',
                'target_priority': ['spiritual_enemies', 'ancestral_protection'],
                'skill_usage': 'spirit_magic',
                'positioning': 'sacred_ground',
                'weapon_preference': 'ritual_items',
                'combat_style': 'spiritual_medium'
            },
            
            # 특수 직업군 (9개)
            '암살자': {
                'formation': 'stealth_infiltration',
                'target_priority': ['high_value_targets', 'silent_elimination'],
                'skill_usage': 'assassination_techniques',
                'positioning': 'shadow_coverage',
                'weapon_preference': 'hidden_blades',
                'combat_style': 'perfect_killer'
            },
            '해적': {
                'formation': 'chaotic_assault',
                'target_priority': ['valuable_loot', 'freedom_fighting'],
                'skill_usage': 'unpredictable_attacks',
                'positioning': 'boarding_tactics',
                'weapon_preference': 'cutlass_and_pistol',
                'combat_style': 'free_spirited_chaos'
            },
            '사무라이': {
                'formation': 'honorable_duel',
                'target_priority': ['honorable_combat', 'bushido_principles'],
                'skill_usage': 'katana_mastery',
                'positioning': 'formal_combat_stance',
                'weapon_preference': 'katana_wakizashi',
                'combat_style': 'bushido_warrior'
            },
            '드루이드': {
                'formation': 'natural_terrain',
                'target_priority': ['nature_protection', 'environmental_harmony'],
                'skill_usage': 'nature_magic',
                'positioning': 'forest_advantage',
                'weapon_preference': 'natural_weapons',
                'combat_style': 'wild_guardian'
            },
            '철학자': {
                'formation': 'logical_analysis',
                'target_priority': ['intellectual_challenges', 'logical_solutions'],
                'skill_usage': 'rational_approach',
                'positioning': 'thoughtful_distance',
                'weapon_preference': 'wisdom_artifacts',
                'combat_style': 'intellectual_combat'
            },
            '검투사': {
                'formation': 'arena_performance',
                'target_priority': ['spectacular_combat', 'crowd_pleasing'],
                'skill_usage': 'showman_techniques',
                'positioning': 'center_stage',
                'weapon_preference': 'gladiator_weapons',
                'combat_style': 'entertainment_fighter'
            },
            '기사': {
                'formation': 'chivalrous_formation',
                'target_priority': ['protecting_weak', 'honorable_combat'],
                'skill_usage': 'knightly_techniques',
                'positioning': 'defensive_valor',
                'weapon_preference': 'lance_and_sword',
                'combat_style': 'chivalrous_protector'
            },
            '신관': {
                'formation': 'healing_support',
                'target_priority': ['ally_healing', 'evil_purification'],
                'skill_usage': 'divine_magic',
                'positioning': 'safe_blessing_range',
                'weapon_preference': 'holy_symbols',
                'combat_style': 'divine_supporter'
            },
            '광전사': {
                'formation': 'berserker_charge',
                'target_priority': ['maximum_damage', 'rage_targets'],
                'skill_usage': 'fury_attacks',
                'positioning': 'direct_assault',
                'weapon_preference': 'massive_weapons',
                'combat_style': 'unstoppable_fury'
            }
        }
        
        return preferences.get(job_class, preferences['전사'])
    
    def _get_relationship_modifiers(self, job_class: str) -> Dict[str, int]:
        """직업별 관계 수정치 - 27x27 매트릭스"""
        # 기본 관계도 (상성이 좋으면 +, 나쁘면 -)
        base_relationships = {
            # 전투 직업군과의 관계
            '전사': {'전사': 10, '성기사': 15, '기사': 12, '검투사': 8, '사무라이': 10, 
                   '도적': -5, '암살자': -8, '해적': -3, '광전사': 5,
                   '아크메이지': 5, '바드': 8, '신관': 10, '몽크': 7},
            
            '아크메이지': {'아크메이지': 15, '정령술사': 12, '시간술사': 10, '연금술사': 8, '차원술사': 5,
                        '마검사': 10, '기계공학자': 8, '무당': 6, '철학자': 12,
                        '전사': 5, '바드': 10, '신관': 8, '광전사': -10, '해적': -5},
            
            '궁수': {'궁수': 10, '도적': 8, '암살자': 6, '해적': 7, '사무라이': 9,
                   '전사': 5, '몽크': 12, '바드': 8, '드루이드': 10,
                   '광전사': -3, '네크로맨서': -5},
            
            '도적': {'도적': 12, '암살자': 10, '해적': 15, '궁수': 8, '바드': 6,
                   '전사': -5, '성기사': -10, '신관': -12, '기사': -8,
                   '연금술사': 5, '기계공학자': 6},
            
            '성기사': {'성기사': 15, '기사': 18, '신관': 20, '전사': 15, '사무라이': 12,
                     '도적': -10, '암살자': -15, '네크로맨서': -20, '암흑기사': -18,
                     '바드': 8, '몽크': 10, '드루이드': 8},
            
            '암흑기사': {'암흑기사': 12, '네크로맨서': 15, '광전사': 8, '암살자': 10,
                      '성기사': -18, '신관': -15, '기사': -12, '바드': -5,
                      '용기사': 6, '검성': 8, '차원술사': 10},
            
            '몽크': {'몽크': 15, '철학자': 18, '드루이드': 12, '사무라이': 14, '시간술사': 10,
                   '궁수': 12, '전사': 7, '성기사': 10, '신관': 8,
                   '광전사': -8, '해적': -5, '암살자': -3},
            
            '바드': {'바드': 12, '해적': 10, '도적': 6, '철학자': 8, '신관': 5,
                   '전사': 8, '아크메이지': 10, '궁수': 8, '기사': 6,
                   '몽크': 7, '드루이드': 9, '정령술사': 8, '무당': 7},
            
            # 마법 직업군과의 관계  
            '네크로맨서': {'네크로맨서': 10, '암흑기사': 15, '차원술사': 12, '무당': 8,
                        '성기사': -20, '신관': -18, '드루이드': -15, '바드': -5,
                        '아크메이지': 5, '시간술사': 8, '철학자': 6},
            
            '용기사': {'용기사': 12, '광전사': 10, '전사': 8, '사무라이': 6, '검성': 8,
                     '암흑기사': 6, '아크메이지': 5, '정령술사': 10,
                     '신관': -3, '도적': -5, '암살자': -8},
            
            '검성': {'검성': 15, '사무라이': 18, '몽크': 12, '용기사': 8, '마검사': 10,
                   '전사': 8, '기사': 6, '암흑기사': 8, '철학자': 10,
                   '해적': -5, '도적': -3, '바드': -2},
            
            '정령술사': {'정령술사': 15, '드루이드': 20, '아크메이지': 12, '무당': 10, '시간술사': 8,
                      '바드': 8, '몽크': 6, '신관': 8, '기계공학자': -8,
                      '네크로맨서': -10, '암흑기사': -5, '광전사': -8},
            
            '시간술사': {'시간술사': 12, '철학자': 15, '아크메이지': 10, '차원술사': 18, '연금술사': 8,
                      '몽크': 10, '정령술사': 8, '무당': 6, '검성': 5,
                      '광전사': -10, '해적': -8, '도적': -5},
            
            '연금술사': {'연금술사': 12, '기계공학자': 15, '아크메이지': 8, '시간술사': 8, '철학자': 10,
                      '도적': 5, '해적': 6, '바드': 3, '무당': 4,
                      '드루이드': -8, '몽크': -5, '성기사': -6},
            
            '차원술사': {'차원술사': 10, '시간술사': 18, '네크로맨서': 12, '무당': 15, '철학자': 12,
                       '암흑기사': 10, '아크메이지': 5, '연금술사': 6,
                       '전사': -8, '성기사': -10, '신관': -12, '바드': -5},
            
            '마검사': {'마검사': 12, '검성': 10, '아크메이지': 10, '전사': 8, '용기사': 6,
                     '성기사': 5, '암흑기사': 5, '사무라이': 8, '기사': 6,
                     '몽크': 8, '정령술사': 8, '시간술사': 6},
            
            '기계공학자': {'기계공학자': 15, '연금술사': 15, '철학자': 12, '시간술사': 8, '아크메이지': 8,
                        '도적': 6, '궁수': 5, '바드': 3, '해적': 4,
                        '드루이드': -12, '무당': -10, '정령술사': -8, '몽크': -6},
            
            '무당': {'무당': 12, '차원술사': 15, '드루이드': 18, '정령술사': 10, '네크로맨서': 8,
                   '몽크': 6, '철학자': 8, '시간술사': 6, '바드': 7,
                   '기계공학자': -10, '연금술사': -5, '성기사': -3},
            
            # 특수 직업군과의 관계
            '암살자': {'암살자': 8, '도적': 10, '네크로맨서': 6, '암흑기사': 10, '차원술사': 5,
                     '성기사': -15, '신관': -12, '기사': -10, '전사': -8,
                     '해적': 5, '궁수': 6, '바드': -3, '몽크': -3},
            
            '해적': {'해적': 15, '도적': 15, '바드': 10, '궁수': 7, '용기사': 5,
                   '연금술사': 6, '기계공학자': 4, '암살자': 5, '검투사': 8,
                   '성기사': -8, '신관': -6, '기사': -5, '몽크': -5, '시간술사': -8},
            
            '사무라이': {'사무라이': 15, '검성': 18, '몽크': 14, '기사': 12, '성기사': 12,
                      '전사': 10, '용기사': 6, '마검사': 8, '철학자': 8,
                      '도적': -8, '암살자': -10, '해적': -6, '광전사': -5},
            
            '드루이드': {'드루이드': 18, '정령술사': 20, '무당': 18, '몽크': 12, '궁수': 10,
                      '바드': 9, '신관': 6, '시간술사': 5, '철학자': 8,
                      '기계공학자': -12, '연금술사': -8, '네크로맨서': -15, '암흑기사': -8},
            
            '철학자': {'철학자': 15, '몽크': 18, '시간술사': 15, '차원술사': 12, '아크메이지': 12,
                     '기계공학자': 12, '연금술사': 10, '무당': 8, '검성': 10,
                     '광전사': -12, '해적': -5, '도적': -3, '암살자': -5},
            
            '검투사': {'검투사': 12, '전사': 8, '광전사': 10, '해적': 8, '바드': 6,
                     '용기사': 5, '사무라이': 4, '기사': 3, '암흑기사': 6,
                     '몽크': -3, '성기사': -5, '신관': -8, '철학자': -6},
            
            '기사': {'기사': 15, '성기사': 18, '전사': 12, '사무라이': 12, '신관': 10,
                   '마검사': 6, '바드': 6, '몽크': 8, '드루이드': 5,
                   '도적': -8, '암살자': -10, '해적': -5, '암흑기사': -12, '네크로맨서': -10},
            
            '신관': {'신관': 18, '성기사': 20, '기사': 10, '전사': 10, '몽크': 8,
                   '바드': 5, '드루이드': 6, '정령술사': 8, '무당': -3,
                   '네크로맨서': -18, '암흑기사': -15, '암살자': -12, '도적': -12, '차원술사': -12},
            
            '광전사': {'광전사': 10, '용기사': 10, '전사': 5, '검투사': 10, '암흑기사': 8,
                     '해적': 6, '사무라이': -5, '도적': 3, '암살자': 4,
                     '아크메이지': -10, '철학자': -12, '몽크': -8, '성기사': -6, '신관': -8}
        }
        
        # 해당 직업의 관계 수정치 반환 (없으면 기본 0)
        return base_relationships.get(job_class, {})
    
    def _get_special_reactions(self, job_class: str) -> Dict[str, str]:
        """직업별 특수 반응 - 27개 직업 완전 정의"""
        reactions = {
            # 전투 직업군 (8개)
            '전사': {
                'low_hp': "아직 쓰러질 수 없다! 동료들을 지켜야 해!",
                'critical_hit': "이 정도 아픔이 뭐냐! 더 강해져야겠군!",
                'magic_trap': "마법은 믿을 수 없어... 검으로 해결하자!",
                'treasure_found': "오, 이건 쓸만해 보이는데! 실용적이군!",
                'ally_death': "이런... 내가 제대로 막지 못했구나...",
                'enemy_strong': "강한 적이군! 혈이 끓어오른다!",
                'level_up': "더 강해졌다! 이제 더 잘 지킬 수 있어!"
            },
            '아크메이지': {
                'low_mp': "마력이 고갈되고 있습니다... 계산을 다시 해야겠군요.",
                'magic_discovery': "이것은... 고도의 마법 지식이 필요합니다! 흥미롭군요!",
                'spell_interrupted': "집중이 깨졌습니다! 마법 시전에 실패했어요.",
                'elemental_advantage': "원소의 상성이 유리합니다! 이론대로군요!",
                'ally_death': "논리적으로 예상 가능했지만... 여전히 아쉽군요.",
                'ancient_magic': "고대 마법의 흔적이 보입니다! 연구해야겠어요!",
                'level_up': "지식이 확장되었습니다! 더 고도의 마법을 쓸 수 있군요!"
            },
            '궁수': {
                'perfect_shot': "완벽한 조준이었습니다! 예상 그대로군요.",
                'missed_shot': "놓쳤군요... 바람의 변화를 고려하지 못했습니다.",
                'high_ground': "좋은 위치입니다! 시야가 완벽하게 확보되었어요.",
                'close_combat': "너무 가까워졌습니다! 거리를 벌려야겠어요!",
                'ally_death': "제가 더 빨리 지원했어야 했는데...",
                'rare_arrow': "특별한 화살이군요! 정확도가 향상될 것 같습니다.",
                'level_up': "사격 실력이 늘었습니다! 더 멀리, 더 정확하게!"
            },
            '도적': {
                'stealth_success': "완벽하게 숨었군요... 그들은 눈치채지 못했어요.",
                'stealth_failed': "들켰습니다! 계획을 바꿔야겠군요.",
                'trap_disarmed': "함정 해제 완료! 역시 제 전문 분야죠.",
                'treasure_stolen': "깔끔하게 가져왔습니다! 들키지 않았어요.",
                'ally_death': "더 조용히 처리했어야 했는데... 미안해요.",
                'poison_applied': "독이 퍼지고 있습니다... 곧 효과가 나타날 거예요.",
                'level_up': "기술이 늘었습니다! 더 은밀하게 움직일 수 있어요!"
            },
            '성기사': {
                'evil_detected': "사악한 기운이 느껴집니다! 정화해야겠어요!",
                'blessing_activated': "신의 축복이 함께합니다! 두려울 것 없어요!",
                'innocent_protected': "약자를 지켜냈습니다! 이것이 기사의 도리죠!",
                'holy_relic': "성스러운 유물이군요! 신의 가호가 느껴집니다!",
                'ally_death': "신이시여... 제가 더 잘 보호했어야 했습니다...",
                'undead_encounter': "언데드를 정화하겠습니다! 안식을 주어야죠!",
                'level_up': "신의 힘이 강해졌습니다! 더 많은 이를 구할 수 있어요!"
            },
            '암흑기사': {
                'darkness_embraced': "어둠이 나를 감싸고 있습니다... 힘이 솟아나는군요.",
                'life_drained': "생명력을 흡수했습니다... 이것이 현실이죠.",
                'vengeance_fulfilled': "복수를 완성했습니다... 하지만 공허함만 남는군요.",
                'cursed_item': "저주받은 아이템이군요... 제게는 오히려 도움이 됩니다.",
                'ally_death': "죽음은 모든 이의 운명입니다... 받아들이세요.",
                'holy_damage': "성스러운 빛이... 고통스럽지만 견딜 수 있어요.",
                'level_up': "어둠의 힘이 깊어졌습니다... 복수에 한 걸음 더 가까워졌군요."
            },
            '몽크': {
                'inner_peace': "마음의 평정을 찾았습니다... 모든 것이 명확해지는군요.",
                'combo_completed': "연환 타격이 완성되었습니다! 수행의 결과입니다!",
                'meditation_disturbed': "수행이 방해받았군요... 다시 집중해야겠어요.",
                'spiritual_item': "영적인 기운이 느껴지는 물건이군요... 수행에 도움이 될 것 같아요.",
                'ally_death': "생과 사는 자연의 이치입니다... 평안히 가시길...",
                'anger_triggered': "분노가 일어나고 있습니다... 마음을 가라앉혀야겠어요.",
                'level_up': "수행이 한 단계 높아졌습니다! 내면의 힘이 강해졌어요!"
            },
            '바드': {
                'perfect_performance': "완벽한 연주였습니다! 관객들이 감동했을 거예요!",
                'song_interrupted': "노래가 중단되었습니다... 분위기가 깨졌네요.",
                'audience_pleased': "모두가 즐거워하고 있군요! 음악의 힘이죠!",
                'musical_instrument': "멋진 악기군요! 더 아름다운 음악을 만들 수 있을 것 같아요!",
                'ally_death': "아... 더 이상 함께 노래할 수 없군요... 슬픈 일이에요.",
                'inspiration_struck': "영감이 떠올랐어요! 새로운 곡을 만들어봐야겠어요!",
                'level_up': "음악 실력이 늘었어요! 더 감동적인 노래를 들려드릴게요!"
            },
            
            # 마법 직업군 (10개)
            '네크로맨서': {
                'undead_summoned': "죽은 자들이 제 부름에 응답했습니다... 충성스럽군요.",
                'life_force_detected': "생명력이 느껴집니다... 흥미로운 연구 대상이군요.",
                'graveyard_found': "무덤이 있는 곳이군요... 여기서 힘을 얻을 수 있을 것 같아요.",
                'soul_captured': "영혼을 포획했습니다... 죽음의 비밀에 한 걸음 더 가까워졌어요.",
                'ally_death': "죽음은 끝이 아닙니다... 새로운 시작일 뿐이에요.",
                'holy_damage': "성스러운 힘이... 불쾌하지만 견딜 수 있어요.",
                'level_up': "죽음의 마법이 깊어졌습니다... 생과 사의 경계가 더 명확해졌어요."
            },
            '용기사': {
                'dragon_power': "용의 힘이 깨어나고 있습니다! 불꽃이 내 안에서 타오르고 있어요!",
                'fire_immunity': "화염이 저를 해칠 수 없습니다! 용의 후예이니까요!",
                'treasure_hoard': "보물이군요! 용족의 본능이 꿈틀거립니다!",
                'dragon_artifact': "드래곤의 유물이군요! 조상들의 힘이 느껴져요!",
                'ally_death': "용족은 동료를 잃는 것을 용납하지 않습니다... 복수하겠어요!",
                'cold_damage': "차가운 공격이... 용족에게는 치명적이군요.",
                'level_up': "용의 혈통이 더욱 진해졌습니다! 화염의 힘이 강해졌어요!"
            },
            '검성': {
                'perfect_technique': "완벽한 기술이었습니다! 검의 도가 한 걸음 나아갔군요!",
                'sword_broken': "검이 부러졌습니다... 아직 수행이 부족했군요.",
                'worthy_opponent': "훌륭한 상대군요! 이런 대결을 기다려왔어요!",
                'legendary_blade': "전설의 검이군요! 진정한 검사만이 다룰 수 있는...",
                'ally_death': "검으로 지키지 못했습니다... 수행이 더 필요하군요.",
                'disarmed': "무기를 놓쳤습니다... 하지만 검성에게는 문제없어요!",
                'level_up': "검의 경지가 높아졌습니다! 더 완벽한 기술을 구사할 수 있어요!"
            },
            '정령술사': {
                'elemental_harmony': "원소들이 조화를 이루고 있어요! 자연이 기뻐하고 있습니다!",
                'nature_destroyed': "자연이 파괴되고 있어요... 정령들이 슬퍼하고 있습니다.",
                'elemental_stone': "원소석이군요! 정령들과의 교감이 더 깊어질 거예요!",
                'pollution_detected': "오염이 감지됩니다... 정화가 필요해요!",
                'ally_death': "자연으로 돌아가셨군요... 대지가 품어줄 거예요.",
                'storm_summoned': "폭풍을 불러왔습니다! 원소들의 분노에요!",
                'level_up': "원소들과의 유대가 깊어졌어요! 더 강력한 자연 마법을 쓸 수 있어요!"
            },
            '시간술사': {
                'time_glimpsed': "시간의 흐름이 보입니다... 과거와 미래가 교차하고 있어요.",
                'paradox_avoided': "시간 역설을 피했습니다... 다행이군요.",
                'temporal_artifact': "시간의 유물이군요! 시공간의 비밀이 담겨있어요!",
                'future_seen': "미래를 엿봤습니다... 조심해야 할 일이 있어요.",
                'ally_death': "이미 예견된 일이었습니다... 시간은 바꿀 수 없어요.",
                'time_rewound': "시간을 되돌렸습니다... 기회를 다시 얻었어요!",
                'level_up': "시간 마법이 발전했습니다! 더 먼 과거와 미래를 볼 수 있어요!"
            },
            '연금술사': {
                'experiment_success': "실험이 성공했습니다! 가설이 증명되었어요!",
                'explosion_caused': "폭발이 일어났습니다! 계산에 오류가 있었나 봐요...",
                'rare_material': "희귀한 재료군요! 새로운 실험을 해볼 수 있을 것 같아요!",
                'potion_created': "완벽한 포션이 완성되었습니다! 과학의 승리에요!",
                'ally_death': "생명의 화학적 구조가... 너무 복잡했군요.",
                'formula_discovered': "새로운 공식을 발견했어요! 혁신적인 발견이에요!",
                'level_up': "연금술 지식이 확장되었어요! 더 복잡한 실험을 할 수 있어요!"
            },
            '차원술사': {
                'portal_opened': "차원의 문이 열렸습니다... 다른 세계가 보이는군요.",
                'reality_warped': "현실이 왜곡되고 있습니다... 흥미로운 현상이에요.",
                'void_touched': "공허에 닿았습니다... 존재와 무의 경계에서...",
                'dimensional_key': "차원의 열쇠군요! 새로운 세계로의 문이 열릴 거예요!",
                'ally_death': "그들은 다른 차원으로 이동했을 뿐입니다... 언젠가 다시 만날 거예요.",
                'space_collapsed': "공간이 붕괴되고 있어요! 긴급히 안정화해야겠어요!",
                'level_up': "차원 마법이 진보했어요! 더 많은 차원에 접근할 수 있어요!"
            },
            '마검사': {
                'balance_achieved': "검과 마법의 완벽한 조화입니다! 이것이 제가 추구하는 길이에요!",
                'imbalance_felt': "균형이 깨지고 있어요... 조화를 되찾아야겠군요.",
                'magic_sword': "마법검이군요! 제게 딱 맞는 무기에요!",
                'dual_mastery': "검술과 마법을 동시에 구사했습니다! 완벽한 조화였어요!",
                'ally_death': "균형이 파괴되었군요... 다시 조화를 찾아야겠어요.",
                'element_infused': "검에 원소를 깃들게 했습니다! 마검의 진정한 힘이에요!",
                'level_up': "마검술이 발전했어요! 검과 마법의 경계가 더욱 모호해졌어요!"
            },
            '기계공학자': {
                'system_analyzed': "시스템 분석이 완료되었습니다! 효율성을 99.7% 개선할 수 있어요!",
                'malfunction_detected': "오작동이 감지되었습니다... 긴급 수리가 필요해요!",
                'blueprint_found': "설계도를 발견했어요! 새로운 기계를 만들 수 있을 것 같아요!",
                'upgrade_completed': "업그레이드가 완료되었습니다! 성능이 크게 향상되었어요!",
                'ally_death': "생체 시스템이 정지했습니다... 복구가 불가능하군요.",
                'invention_inspired': "새로운 발명 아이디어가 떠올랐어요! 혁신적인 기술이 될 거예요!",
                'level_up': "기술력이 향상되었어요! 더 정교한 기계를 만들 수 있어요!"
            },
            '무당': {
                'spirit_contacted': "조상의 영혼과 교감했습니다... 지혜를 얻었어요.",
                'evil_spirit': "악령이 감지됩니다! 정화 의식을 해야겠어요!",
                'sacred_ground': "신성한 땅이군요... 조상들의 기운이 강하게 느껴져요!",
                'ritual_completed': "의식이 완료되었습니다! 신령한 힘을 얻었어요!",
                'ally_death': "영혼이 조상의 품으로 돌아갔습니다... 평안히 가세요.",
                'talisman_found': "부적을 찾았어요! 악운을 막아줄 거예요!",
                'level_up': "영력이 강해졌어요! 더 깊은 영적 교감이 가능해요!"
            },
            
            # 특수 직업군 (9개)
            '암살자': {
                'target_eliminated': "목표를 조용히 처리했습니다... 완벽한 암살이었어요.",
                'cover_blown': "신원이 노출되었습니다... 계획을 수정해야겠군요.",
                'poison_weapon': "독이 발린 무기군요... 제게 딱 맞는 도구에요.",
                'shadow_blend': "그림자에 완전히 숨었습니다... 아무도 찾을 수 없을 거예요.",
                'ally_death': "실패작입니다... 더 조용히 처리했어야 했어요.",
                'assassination_art': "암살술의 예술적 완성도였습니다... 흔적 없는 죽음.",
                'level_up': "암살 기술이 완성되어 갑니다... 더 은밀하고 치명적으로."
            },
            '해적': {
                'treasure_discovered': "보물이다! 크하하! 이게 바로 해적의 로망이지!",
                'storm_weathered': "폭풍을 헤쳐나왔어! 바다의 남자답게!",
                'rum_found': "럼이 있군! 축제를 벌일 시간이야!",
                'freedom_threatened': "자유를 위협하려고? 해적의 자유는 아무도 막을 수 없어!",
                'ally_death': "동료를 잃었군... 바다에 묻어주자.",
                'ship_spotted': "배가 보인다! 약탈할 시간이야!",
                'level_up': "더 경험 많은 해적이 되었어! 바다가 날 부르고 있어!"
            },
            '사무라이': {
                'honor_upheld': "명예를 지켰습니다... 조상님들께 부끄럽지 않았어요.",
                'dishonor_witnessed': "불명예스러운 일을 목격했습니다... 정의를 실현해야겠어요.",
                'katana_drawn': "검을 뽑았습니다... 이제 물러날 수 없어요.",
                'bushido_followed': "부시도의 길을 따랐습니다... 이것이 무사의 도리죠.",
                'ally_death': "명예로운 죽음이었습니다... 사무라이답게 가셨군요.",
                'duel_accepted': "정정당당한 결투를 받아들입니다! 명예를 걸고!",
                'level_up': "무사도가 한 걸음 더 완성되었습니다! 더 완벽한 사무라이가 되었어요!"
            },
            '드루이드': {
                'nature_restored': "자연이 회복되었습니다... 생명력이 넘치고 있어요!",
                'animal_befriended': "야생동물이 친구가 되었어요! 자연의 축복이에요!",
                'forest_protected': "숲을 지켜냈습니다... 나무들이 기뻐하고 있어요!",
                'seasons_changed': "계절이 바뀌었습니다... 자연의 순환이 아름다워요!",
                'ally_death': "대지로 돌아가셨군요... 자연의 일부가 되셨어요.",
                'ancient_tree': "고대 나무군요! 수천 년의 지혜가 담겨있어요!",
                'level_up': "자연과의 유대가 깊어졌어요! 더 많은 생명체와 교감할 수 있어요!"
            },
            '철학자': {
                'truth_discovered': "진리를 발견했습니다! 지식의 새로운 지평이 열렸어요!",
                'paradox_encountered': "역설에 직면했군요... 흥미로운 철학적 문제에요!",
                'wisdom_gained': "지혜를 얻었습니다... 세상을 보는 눈이 더 깊어졌어요!",
                'logic_applied': "논리적 사고가 해답을 찾아냈습니다! 이성의 승리에요!",
                'ally_death': "존재의 한계를 목격했군요... 생과 사에 대해 다시 생각해봐야겠어요.",
                'ancient_text': "고대 철학서군요! 선현들의 지혜가 담겨있어요!",
                'level_up': "철학적 사유가 깊어졌어요! 더 복잡한 진리에 접근할 수 있어요!"
            },
            '검투사': {
                'crowd_pleased': "관중들이 열광하고 있어! 이것이 진정한 쇼맨십이지!",
                'spectacular_move': "화려한 기술이었어! 모두가 감탄했을 거야!",
                'arena_mastered': "경기장을 완전히 장악했어! 이곳은 내 무대야!",
                'glory_achieved': "영광을 쟁취했어! 검투사의 자존심을 지켰지!",
                'ally_death': "동료가 쓰러졌군... 관중들에게 그의 용기를 보여주자!",
                'legendary_weapon': "전설의 무기군! 더 멋진 경기를 할 수 있을 거야!",
                'level_up': "검투 실력이 늘었어! 더 화려하고 강력한 기술을 보여줄 수 있어!"
            },
            '기사': {
                'chivalry_displayed': "기사도를 실천했습니다... 이것이 진정한 기사의 길이에요!",
                'lady_protected': "숙녀를 보호했습니다... 기사의 당연한 의무죠!",
                'noble_deed': "고귀한 행동이었습니다... 기사다운 선택이었어요!",
                'quest_completed': "퀘스트를 완수했습니다! 기사의 명예를 지켰어요!",
                'ally_death': "동료를 지키지 못했습니다... 기사로서 부끄럽군요.",
                'holy_relic': "성스러운 유물이군요! 기사의 힘이 강해질 거예요!",
                'level_up': "기사도가 더욱 완성되었어요! 더 많은 이를 지킬 수 있어요!"
            },
            '신관': {
                'blessing_bestowed': "축복을 내렸습니다... 신의 은총이 함께하기를!",
                'evil_purified': "악을 정화했습니다... 신성한 빛이 승리했어요!",
                'prayer_answered': "기도가 응답받았습니다... 신께서 우리를 돌보고 계세요!",
                'miracle_witnessed': "기적을 목격했습니다! 신의 존재를 확신해요!",
                'ally_death': "신의 품으로 돌아가셨군요... 평안한 안식을 얻으셨을 거예요.",
                'sacred_artifact': "성스러운 유물이군요! 신의 힘이 깃들어 있어요!",
                'level_up': "신앙심이 깊어졌어요! 더 강력한 신성 마법을 쓸 수 있어요!"
            },
            '광전사': {
                'rage_unleashed': "분노가 폭발했다! 모든 것을 파괴해버리겠어!",
                'blood_spilled': "피가 흘렀군! 더욱 흥분되는데?!",
                'enemy_feared': "적들이 두려워하고 있어! 공포가 바로 힘이야!",
                'rampage_mode': "광폭화 상태야! 아무도 나를 막을 수 없어!",
                'ally_death': "우오오오! 복수하겠어! 모든 적을 갈기갈기 찢어놓겠다!",
                'berserker_weapon': "파괴적인 무기군! 더 많이 부술 수 있겠어!",
                'level_up': "더 강해졌어! 분노의 힘이 폭발적으로 늘었다!"
            }
        }
        
        return reactions.get(job_class, {})

class IntegratedAICompanion:
    """통합 지능형 AI 동료"""
    
    def __init__(self, character_name: str, character_class: str, gender: str = "남성"):
        self.character_name = character_name
        self.character_class = character_class
        self.gender = gender
        
        # 직업별 AI 프로필 생성
        self.job_profile = JobBasedAIProfile(character_class)
        
        # 언어모델 매니저 초기화
        self.llm_manager = None
        if LLM_AVAILABLE:
            try:
                self.llm_manager = LanguageModelManager()
                self.conversation_manager = ConversationManager()
                print(f"✅ {character_name}: 언어모델 연결 성공")
            except Exception as e:
                print(f"⚠️ {character_name}: 언어모델 연결 실패: {e}")
        
        # 맵 스캐너 초기화
        self.map_scanner = None
        if ADVANCED_AI_AVAILABLE:
            try:
                self.map_scanner = MapScanner()
                print(f"✅ {character_name}: 맵 스캐너 활성화")
            except Exception as e:
                print(f"⚠️ {character_name}: 맵 스캐너 초기화 실패: {e}")
        
        # 상태 추적 변수들
        self.current_mood = CharacterState.HEALTHY
        self.stress_level = 0
        self.relationship_with_player = 50  # 중립
        self.memory_context = []
        self.last_analysis_time = 0
        
        # 학습 데이터베이스
        self.learning_db = self._init_learning_db()
        
        print(f"🤖 통합 AI 동료 '{character_name}' ({character_class}) 초기화 완료!")
    
    def _init_learning_db(self) -> sqlite3.Connection:
        """학습 데이터베이스 초기화"""
        try:
            db = sqlite3.connect(f"ai_learning_{self.character_name}.db")
            cursor = db.cursor()
            
            # 경험 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    situation TEXT,
                    player_action TEXT,
                    ai_response TEXT,
                    outcome TEXT,
                    effectiveness_score INTEGER
                )
            ''')
            
            # 관계 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    event_type TEXT,
                    relationship_change INTEGER,
                    current_level INTEGER,
                    context TEXT
                )
            ''')
            
            db.commit()
            return db
        except Exception as e:
            print(f"⚠️ 학습 DB 초기화 실패: {e}")
            return None
    
    def analyze_character_state(self, character) -> CharacterAnalysis:
        """캐릭터 상태 분석"""
        try:
            hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
            mp_ratio = character.current_mp / character.max_mp if character.max_mp > 0 else 0
            brv_ratio = getattr(character, 'current_brv', 100) / getattr(character, 'max_brv', 100)
            
            # 상태 이상 효과 분석
            status_effects = []
            if hasattr(character, 'status_effects'):
                status_effects = list(character.status_effects.keys())
            
            # 장비 상태 분석
            equipment_condition = "양호"
            if hasattr(character, 'equipment'):
                damaged_equipment = [eq for eq in character.equipment.values() 
                                   if hasattr(eq, 'durability') and eq.durability < 50]
                if damaged_equipment:
                    equipment_condition = "수리필요"
            
            # 기분 분석
            mood = CharacterState.HEALTHY
            if hp_ratio < 0.3:
                mood = CharacterState.INJURED
            elif hp_ratio < 0.5:
                mood = CharacterState.EXHAUSTED
            elif mp_ratio < 0.2:
                mood = CharacterState.FOCUSED
            elif mp_ratio > 0.8:
                mood = CharacterState.ENERGETIC
            
            # 스트레스 레벨 계산
            stress = 0
            if hp_ratio < 0.5:
                stress += 30
            if mp_ratio < 0.3:
                stress += 20
            if len(status_effects) > 0:
                stress += len(status_effects) * 10
            
            return CharacterAnalysis(
                hp_ratio=hp_ratio,
                mp_ratio=mp_ratio, 
                brv_ratio=brv_ratio,
                status_effects=status_effects,
                equipment_condition=equipment_condition,
                mood=mood,
                stress_level=min(stress, 100),
                relationship_with_player=self.relationship_with_player
            )
            
        except Exception as e:
            print(f"⚠️ 캐릭터 상태 분석 실패: {e}")
            return CharacterAnalysis(1.0, 1.0, 1.0, [], "양호", CharacterState.HEALTHY, 0, 50)
    
    def analyze_environment(self, world, player_pos: Tuple[int, int]) -> EnvironmentAnalysis:
        """환경 분석 - 27개 직업별 전문 분석"""
        try:
            if not self.map_scanner or not world:
                return EnvironmentAnalysis(0, [], [], [], [], [], [], [])
            
            # 직업별 스캔 범위 조정
            scan_range = self._get_job_scan_range()
            scan_result = self.map_scanner.scan_area(world, player_pos, scan_range)
            
            visible_enemies = []
            treasures = []
            traps = []
            exits = []
            
            # 스캔 결과 분석
            if hasattr(scan_result, 'detected_objects'):
                for obj in scan_result.detected_objects:
                    pos = (obj.x, obj.y)
                    if obj.type == 'enemy':
                        visible_enemies.append(pos)
                    elif obj.type == 'treasure':
                        treasures.append(pos)
                    elif obj.type == 'trap':
                        traps.append(pos)
                    elif obj.type == 'exit':
                        exits.append(pos)
            
            # 직업별 전문 환경 분석
            tactical_advantages, dangers = self._analyze_job_specific_environment(
                visible_enemies, treasures, traps, exits, world, player_pos
            )
            
            # 추천사항 생성
            recommendations = self._generate_tactical_recommendations(
                visible_enemies, treasures, traps, exits, tactical_advantages, dangers
            )
            
            return EnvironmentAnalysis(
                scan_range=5,
                visible_enemies=visible_enemies,
                treasures=treasures,
                traps=traps,
                exits=exits,
                tactical_advantages=tactical_advantages,
                dangers=dangers,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"⚠️ 환경 분석 실패: {e}")
            return EnvironmentAnalysis(0, [], [], [], [], [], [], [])
    
    def _get_job_scan_range(self):
        """직업별 환경 스캔 범위 설정"""
        # 원거리 직업군 - 넓은 시야
        if self.character_class in ["궁수", "아크메이지", "정령술사", "시간술사", "기계공학자"]:
            return ScanRange.LONG
        
        # 정찰 직업군 - 매우 넓은 시야
        elif self.character_class in ["도적", "암살자", "해적", "드루이드"]:
            return ScanRange.LONG
        
        # 근접 전투 직업군 - 중간 시야
        elif self.character_class in ["전사", "성기사", "암흑기사", "몽크", "검성", "사무라이", "검투사", "기사", "광전사"]:
            return ScanRange.MEDIUM
        
        # 마법/지원 직업군 - 중간 시야
        elif self.character_class in ["바드", "네크로맨서", "용기사", "연금술사", "차원술사", "마검사", "무당", "철학자", "신관"]:
            return ScanRange.MEDIUM
        
        # 기본값
        else:
            return ScanRange.MEDIUM
    
    def _analyze_job_specific_environment(self, enemies, treasures, traps, exits, world, player_pos):
        """27개 직업별 전문 환경 분석"""
        tactical_advantages = []
        dangers = []
        
        # 기본 분석
        if len(enemies) == 1:
            tactical_advantages.append("일대일 전투 가능")
        if len(treasures) > 0:
            tactical_advantages.append("보물 획득 기회")
        if len(exits) > 1:
            tactical_advantages.append("여러 탈출로 확보")
        if len(enemies) > 3:
            dangers.append("다수의 적 포위 위험")
        if len(exits) == 0:
            dangers.append("탈출로 없음")
        
        # 전투 직업군 (8개) 전문 분석
        if self.character_class == "전사":
            if len(enemies) <= 2:
                tactical_advantages.append("방패술로 충분히 방어 가능한 적 수")
            if len(enemies) > 4:
                dangers.append("방어 한계를 넘는 적 수")
            tactical_advantages.append("전면전에 최적화된 지형")
        
        elif self.character_class == "아크메이지":
            if len(enemies) > 2:
                tactical_advantages.append("광역 마법 최대 효율 상황")
            if len(treasures) > 0:
                tactical_advantages.append("마법 아이템 발견 가능성")
            if len(enemies) == 1 and any(self._is_close_range(pos, player_pos) for pos in enemies):
                dangers.append("근접전 불리한 상황")
        
        elif self.character_class == "궁수":
            high_ground = self._check_high_ground(world, player_pos)
            if high_ground:
                tactical_advantages.append("고지대 사격 위치 확보")
            if len(exits) > 1:
                tactical_advantages.append("히트앤런 전술 가능")
            if any(self._is_close_range(pos, player_pos) for pos in enemies):
                dangers.append("근접전 위험")
        
        elif self.character_class == "도적":
            if len(traps) > 0:
                tactical_advantages.append("함정 해제 전문성 활용 기회")
            stealth_spots = self._check_stealth_positions(world, player_pos)
            if stealth_spots:
                tactical_advantages.append("은신 가능 위치 다수")
            if len(treasures) > 0:
                tactical_advantages.append("자물쇠 해제 기술 활용 가능")
        
        elif self.character_class == "성기사":
            undead_enemies = self._detect_undead_enemies(enemies)
            if undead_enemies:
                tactical_advantages.append("언데드 특효 - 성스러운 마법 위력 증가")
            if len(enemies) > 0:
                tactical_advantages.append("정의로운 전투 - 사기 보너스")
            dark_areas = self._check_dark_areas(world, player_pos)
            if dark_areas:
                tactical_advantages.append("성스러운 빛으로 어둠 정화 가능")
        
        elif self.character_class == "암흑기사":
            if len(enemies) > 2:
                tactical_advantages.append("다수 적에서 생명력 흡수 효율 증가")
            dark_areas = self._check_dark_areas(world, player_pos)
            if dark_areas:
                tactical_advantages.append("어둠 속에서 힘 증가")
            if self._check_cursed_areas(world, player_pos):
                tactical_advantages.append("저주받은 지역에서 특수 능력 활성화")
        
        elif self.character_class == "몽크":
            open_spaces = self._check_open_spaces(world, player_pos)
            if open_spaces:
                tactical_advantages.append("연환 타격을 위한 충분한 공간")
            if len(enemies) <= 3:
                tactical_advantages.append("집중력 유지 가능한 적 수")
            meditation_spots = self._check_meditation_spots(world, player_pos)
            if meditation_spots:
                tactical_advantages.append("기력 회복을 위한 평온한 장소")
        
        elif self.character_class == "바드":
            if len(enemies) > 1:
                tactical_advantages.append("음파 공격으로 다수 적 동시 공격 가능")
            echo_areas = self._check_echo_areas(world, player_pos)
            if echo_areas:
                tactical_advantages.append("음향 효과 증폭 가능 지형")
            if any(ally for ally in self._detect_allies_nearby(player_pos)):
                tactical_advantages.append("아군 버프 효과 최대화 가능")
        
        # 마법 직업군 (10개) 전문 분석
        elif self.character_class == "네크로맨서":
            corpses = self._detect_corpses(world, player_pos)
            if corpses:
                tactical_advantages.append("언데드 소환을 위한 시체 발견")
            dark_energy = self._check_dark_energy(world, player_pos)
            if dark_energy:
                tactical_advantages.append("어둠의 마력이 풍부한 지역")
            if len(enemies) > 2:
                tactical_advantages.append("대규모 언데드 군단 소환 효과적")
        
        elif self.character_class == "용기사":
            fire_sources = self._check_fire_sources(world, player_pos)
            if fire_sources:
                tactical_advantages.append("화염 마법 위력 증가 지역")
            if len(enemies) > 1:
                tactical_advantages.append("드래곤 브레스 광역 효과 최적")
            treasure_hoards = self._detect_treasure_hoards(treasures)
            if treasure_hoards:
                tactical_advantages.append("용족 본능 - 보물 더미 발견")
        
        elif self.character_class == "검성":
            sacred_grounds = self._check_sacred_grounds(world, player_pos)
            if sacred_grounds:
                tactical_advantages.append("성지에서 검술 위력 증가")
            if len(enemies) == 1:
                tactical_advantages.append("검의 극의 - 일대일 결투 최적")
            ancient_weapons = self._detect_ancient_weapons(treasures)
            if ancient_weapons:
                tactical_advantages.append("고대 무기 발견 가능성")
        
        elif self.character_class == "정령술사":
            elemental_nodes = self._check_elemental_nodes(world, player_pos)
            if elemental_nodes:
                tactical_advantages.append("원소 정령들과의 연결 강화")
            natural_areas = self._check_natural_areas(world, player_pos)
            if natural_areas:
                tactical_advantages.append("자연 환경에서 마법 위력 증가")
            if len(enemies) > 2:
                tactical_advantages.append("원소 융합 마법으로 광역 공격 효과적")
        
        elif self.character_class == "시간술사":
            temporal_anomalies = self._check_temporal_anomalies(world, player_pos)
            if temporal_anomalies:
                tactical_advantages.append("시간 왜곡 지역 - 시간 마법 효과 증폭")
            if len(enemies) > 3:
                tactical_advantages.append("시간 정지로 다수 적 무력화 가능")
            ancient_ruins = self._check_ancient_ruins(world, player_pos)
            if ancient_ruins:
                tactical_advantages.append("고대 유적 - 시간의 흔적 감지")
        
        elif self.character_class == "연금술사":
            chemical_materials = self._detect_chemical_materials(world, player_pos)
            if chemical_materials:
                tactical_advantages.append("연금술 재료 풍부한 지역")
            if len(enemies) > 2:
                tactical_advantages.append("폭발 반응으로 광역 피해 최적")
            laboratory_equipment = self._detect_lab_equipment(treasures)
            if laboratory_equipment:
                tactical_advantages.append("연금술 장비 발견 가능성")
        
        elif self.character_class == "차원술사":
            dimensional_rifts = self._check_dimensional_rifts(world, player_pos)
            if dimensional_rifts:
                tactical_advantages.append("차원 균열 활용 가능")
            if len(exits) == 0:
                tactical_advantages.append("차원문으로 새로운 탈출로 창조 가능")
            unstable_space = self._check_unstable_space(world, player_pos)
            if unstable_space:
                tactical_advantages.append("불안정한 공간 - 차원 마법 위력 증가")
        
        elif self.character_class == "마검사":
            magical_weapons = self._detect_magical_weapons(treasures)
            if magical_weapons:
                tactical_advantages.append("마법검과의 공명 가능성")
            balanced_terrain = self._check_balanced_terrain(world, player_pos)
            if balanced_terrain:
                tactical_advantages.append("검술과 마법 모두 활용 가능한 지형")
            mana_flows = self._check_mana_flows(world, player_pos)
            if mana_flows:
                tactical_advantages.append("마력 흐름 감지 - 마검술 위력 증가")
        
        elif self.character_class == "기계공학자":
            mechanical_devices = self._detect_mechanical_devices(world, player_pos)
            if mechanical_devices:
                tactical_advantages.append("기계 장치 해킹/조작 가능")
            if len(traps) > 0:
                tactical_advantages.append("기계식 함정 구조 분석 및 무력화 가능")
            energy_sources = self._detect_energy_sources(world, player_pos)
            if energy_sources:
                tactical_advantages.append("에너지원 발견 - 장비 효율 증가")
        
        elif self.character_class == "무당":
            spiritual_energy = self._check_spiritual_energy(world, player_pos)
            if spiritual_energy:
                tactical_advantages.append("영적 에너지 풍부 - 무속 마법 위력 증가")
            ancestral_grounds = self._check_ancestral_grounds(world, player_pos)
            if ancestral_grounds:
                tactical_advantages.append("조상의 땅 - 영혼 소환 효과 증대")
            if len(enemies) > 0:
                tactical_advantages.append("적의 영혼 약점 감지 가능")
        
        # 특수 직업군 (9개) 전문 분석
        elif self.character_class == "암살자":
            shadow_areas = self._check_shadow_areas(world, player_pos)
            if shadow_areas:
                tactical_advantages.append("그림자 은신 최적 환경")
            if len(enemies) == 1:
                tactical_advantages.append("암살 대상 격리 완료")
            blind_spots = self._detect_blind_spots(world, player_pos)
            if blind_spots:
                tactical_advantages.append("사각지대 다수 - 기습 공격 유리")
        
        elif self.character_class == "해적":
            if len(treasures) > 0:
                tactical_advantages.append("보물 사냥꾼의 직감 - 숨겨진 보물 탐지")
            water_sources = self._check_water_sources(world, player_pos)
            if water_sources:
                tactical_advantages.append("물 근처 - 해적의 자연 환경")
            if len(exits) > 1:
                tactical_advantages.append("자유로운 영혼 - 다양한 탈출로 활용")
        
        elif self.character_class == "사무라이":
            honor_grounds = self._check_honor_grounds(world, player_pos)
            if honor_grounds:
                tactical_advantages.append("명예로운 결투장 - 부시도 정신 발현")
            if len(enemies) == 1:
                tactical_advantages.append("일대일 결투 - 사무라이 전투의 정수")
            katana_compatible = self._detect_katana_weapons(treasures)
            if katana_compatible:
                tactical_advantages.append("일본도 발견 가능성 - 검술 위력 극대화")
        
        elif self.character_class == "드루이드":
            natural_sanctuaries = self._check_natural_sanctuaries(world, player_pos)
            if natural_sanctuaries:
                tactical_advantages.append("자연 성역 - 드루이드 마법 극대화")
            wildlife_presence = self._detect_wildlife(world, player_pos)
            if wildlife_presence:
                tactical_advantages.append("야생동물 소환 가능")
            plant_growth = self._check_plant_growth(world, player_pos)
            if plant_growth:
                tactical_advantages.append("식물 조작 마법 효과 증대")
        
        elif self.character_class == "철학자":
            ancient_texts = self._detect_ancient_texts(treasures)
            if ancient_texts:
                tactical_advantages.append("고대 지식 발견 - 철학적 통찰 증가")
            puzzle_elements = self._detect_puzzle_elements(world, player_pos)
            if puzzle_elements:
                tactical_advantages.append("논리 퍼즐 해결 기회")
            wisdom_sources = self._check_wisdom_sources(world, player_pos)
            if wisdom_sources:
                tactical_advantages.append("지혜의 원천 - 철학적 사고 강화")
        
        elif self.character_class == "검투사":
            arena_like_areas = self._check_arena_areas(world, player_pos)
            if arena_like_areas:
                tactical_advantages.append("투기장 환경 - 검투사 기술 최적화")
            if len(enemies) > 1:
                tactical_advantages.append("다수 관중(적) 앞에서 화려한 기술 발현")
            performance_space = self._check_performance_space(world, player_pos)
            if performance_space:
                tactical_advantages.append("공연 공간 - 검투 기술의 미학적 발현")
        
        elif self.character_class == "기사":
            chivalric_grounds = self._check_chivalric_grounds(world, player_pos)
            if chivalric_grounds:
                tactical_advantages.append("기사도 정신 발현 최적 환경")
            if any(self._detect_weak_allies_nearby(player_pos)):
                tactical_advantages.append("보호해야 할 약자 존재 - 기사도 발현")
            noble_artifacts = self._detect_noble_artifacts(treasures)
            if noble_artifacts:
                tactical_advantages.append("귀족 유물 발견 가능성")
        
        elif self.character_class == "신관":
            holy_sites = self._check_holy_sites(world, player_pos)
            if holy_sites:
                tactical_advantages.append("성지 - 신성 마법 위력 극대화")
            if len(enemies) > 0:
                tactical_advantages.append("악을 정화할 기회 - 신의 뜻 실현")
            divine_relics = self._detect_divine_relics(treasures)
            if divine_relics:
                tactical_advantages.append("신성 유물 발견 가능성")
        
        elif self.character_class == "광전사":
            if len(enemies) > 2:
                tactical_advantages.append("다수 적 - 광폭화 효과 최대화")
            destructible_environment = self._check_destructible_objects(world, player_pos)
            if destructible_environment:
                tactical_advantages.append("파괴 가능한 환경 - 광폭한 파괴력 발휘")
            if len(exits) == 1:
                dangers.append("퇴로 차단 시 제어 불가능한 광폭화 위험")
        
        return tactical_advantages, dangers
    
    # 환경 분석 헬퍼 메서드들 (27개 직업 특화)
    def _is_close_range(self, enemy_pos, player_pos, range_limit=2):
        """근접 거리 판정"""
        dx = abs(enemy_pos[0] - player_pos[0])
        dy = abs(enemy_pos[1] - player_pos[1])
        return max(dx, dy) <= range_limit
    
    def _check_high_ground(self, world, player_pos):
        """고지대 확인 (궁수용)"""
        try:
            # 주변보다 높은 위치인지 확인하는 로직
            # 실제 구현에서는 world의 지형 데이터를 확인
            return False  # 기본값
        except:
            return False
    
    def _check_stealth_positions(self, world, player_pos):
        """은신 가능 위치 확인 (도적/암살자용)"""
        try:
            # 벽 근처, 그림자 지역 등 은신 가능한 위치 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_undead_enemies(self, enemies):
        """언데드 적 탐지 (성기사용)"""
        try:
            # 적의 타입이 언데드인지 확인하는 로직
            return len(enemies) > 0  # 임시 구현
        except:
            return False
    
    def _check_dark_areas(self, world, player_pos):
        """어둠 지역 확인 (암흑기사용)"""
        try:
            # 어둠이나 그림자가 많은 지역 확인
            return True  # 기본값
        except:
            return False
    
    def _check_cursed_areas(self, world, player_pos):
        """저주받은 지역 확인 (암흑기사용)"""
        try:
            # 저주받은 땅이나 악마적 기운이 있는 지역 확인
            return False  # 기본값
        except:
            return False
    
    def _check_open_spaces(self, world, player_pos):
        """넓은 공간 확인 (몽크용)"""
        try:
            # 연환 타격이 가능한 넓은 공간 확인
            return True  # 기본값
        except:
            return False
    
    def _check_meditation_spots(self, world, player_pos):
        """명상 가능 장소 확인 (몽크용)"""
        try:
            # 평온하고 조용한 장소 확인
            return True  # 기본값
        except:
            return False
    
    def _check_echo_areas(self, world, player_pos):
        """음향 효과 지역 확인 (바드용)"""
        try:
            # 음향이 증폭되는 지역 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_allies_nearby(self, player_pos):
        """근처 아군 탐지 (바드용)"""
        try:
            # 버프 효과를 받을 수 있는 아군 확인
            return []  # 기본값
        except:
            return []
    
    def _detect_corpses(self, world, player_pos):
        """시체 탐지 (네크로맨서용)"""
        try:
            # 언데드 소환에 사용할 시체 확인
            return True  # 기본값
        except:
            return False
    
    def _check_dark_energy(self, world, player_pos):
        """어둠의 마력 확인 (네크로맨서용)"""
        try:
            # 네크로맨시에 유리한 어둠의 에너지 확인
            return True  # 기본값
        except:
            return False
    
    def _check_fire_sources(self, world, player_pos):
        """화염원 확인 (용기사용)"""
        try:
            # 화염 마법을 강화할 수 있는 화염원 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_treasure_hoards(self, treasures):
        """보물 더미 탐지 (용기사용)"""
        try:
            # 용족의 본능에 반응할 큰 보물 더미 확인
            return len(treasures) > 2
        except:
            return False
    
    def _check_sacred_grounds(self, world, player_pos):
        """성지 확인 (검성/성기사용)"""
        try:
            # 신성한 기운이 있는 땅 확인
            return False  # 기본값
        except:
            return False
    
    def _detect_ancient_weapons(self, treasures):
        """고대 무기 탐지 (검성용)"""
        try:
            # 검성에게 적합한 고대 무기 확인
            return len(treasures) > 0  # 임시 구현
        except:
            return False
    
    def _check_elemental_nodes(self, world, player_pos):
        """원소 노드 확인 (정령술사용)"""
        try:
            # 원소 마법을 강화할 원소 노드 확인
            return True  # 기본값
        except:
            return False
    
    def _check_natural_areas(self, world, player_pos):
        """자연 지역 확인 (정령술사/드루이드용)"""
        try:
            # 자연의 기운이 강한 지역 확인
            return True  # 기본값
        except:
            return False
    
    def _check_temporal_anomalies(self, world, player_pos):
        """시간 이상 현상 확인 (시간술사용)"""
        try:
            # 시간이 왜곡된 지역 확인
            return False  # 기본값
        except:
            return False
    
    def _check_ancient_ruins(self, world, player_pos):
        """고대 유적 확인 (시간술사/철학자용)"""
        try:
            # 고대 문명의 유적 확인
            return False  # 기본값
        except:
            return False
    
    def _detect_chemical_materials(self, world, player_pos):
        """화학 재료 탐지 (연금술사용)"""
        try:
            # 연금술에 사용할 재료 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_lab_equipment(self, treasures):
        """실험 장비 탐지 (연금술사용)"""
        try:
            # 연금술 실험에 필요한 장비 확인
            return len(treasures) > 0  # 임시 구현
        except:
            return False
    
    def _check_dimensional_rifts(self, world, player_pos):
        """차원 균열 확인 (차원술사용)"""
        try:
            # 차원간 균열이나 틈 확인
            return False  # 기본값
        except:
            return False
    
    def _check_unstable_space(self, world, player_pos):
        """불안정한 공간 확인 (차원술사용)"""
        try:
            # 공간이 불안정한 지역 확인
            return False  # 기본값
        except:
            return False
    
    def _detect_magical_weapons(self, treasures):
        """마법 무기 탐지 (마검사용)"""
        try:
            # 마법이 깃든 무기 확인
            return len(treasures) > 0  # 임시 구현
        except:
            return False
    
    def _check_balanced_terrain(self, world, player_pos):
        """균형잡힌 지형 확인 (마검사용)"""
        try:
            # 검술과 마법 모두에 적합한 지형 확인
            return True  # 기본값
        except:
            return False
    
    def _check_mana_flows(self, world, player_pos):
        """마력 흐름 확인 (마검사용)"""
        try:
            # 마력이 흐르는 지역 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_mechanical_devices(self, world, player_pos):
        """기계 장치 탐지 (기계공학자용)"""
        try:
            # 조작 가능한 기계 장치 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_energy_sources(self, world, player_pos):
        """에너지원 탐지 (기계공학자용)"""
        try:
            # 기계에 동력을 공급할 에너지원 확인
            return True  # 기본값
        except:
            return False
    
    def _check_spiritual_energy(self, world, player_pos):
        """영적 에너지 확인 (무당용)"""
        try:
            # 영혼이나 정령의 기운이 강한 지역 확인
            return True  # 기본값
        except:
            return False
    
    def _check_ancestral_grounds(self, world, player_pos):
        """조상의 땅 확인 (무당용)"""
        try:
            # 조상의 영혼이 깃든 땅 확인
            return False  # 기본값
        except:
            return False
    
    def _check_shadow_areas(self, world, player_pos):
        """그림자 지역 확인 (암살자용)"""
        try:
            # 은신에 적합한 그림자 지역 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_blind_spots(self, world, player_pos):
        """사각지대 탐지 (암살자용)"""
        try:
            # 기습 공격에 유리한 사각지대 확인
            return True  # 기본값
        except:
            return False
    
    def _check_water_sources(self, world, player_pos):
        """물의 근원 확인 (해적용)"""
        try:
            # 해적에게 친숙한 물이 있는 지역 확인
            return False  # 기본값
        except:
            return False
    
    def _check_honor_grounds(self, world, player_pos):
        """명예로운 땅 확인 (사무라이용)"""
        try:
            # 명예로운 결투에 적합한 장소 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_katana_weapons(self, treasures):
        """일본도 탐지 (사무라이용)"""
        try:
            # 사무라이에게 적합한 일본도 확인
            return len(treasures) > 0  # 임시 구현
        except:
            return False
    
    def _check_natural_sanctuaries(self, world, player_pos):
        """자연 성역 확인 (드루이드용)"""
        try:
            # 자연의 신성한 힘이 있는 성역 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_wildlife(self, world, player_pos):
        """야생동물 탐지 (드루이드용)"""
        try:
            # 소환하거나 동맹으로 삼을 야생동물 확인
            return True  # 기본값
        except:
            return False
    
    def _check_plant_growth(self, world, player_pos):
        """식물 성장 확인 (드루이드용)"""
        try:
            # 식물 조작 마법에 적합한 식생 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_ancient_texts(self, treasures):
        """고대 문헌 탐지 (철학자용)"""
        try:
            # 철학적 지식이 담긴 고대 문헌 확인
            return len(treasures) > 0  # 임시 구현
        except:
            return False
    
    def _detect_puzzle_elements(self, world, player_pos):
        """퍼즐 요소 탐지 (철학자용)"""
        try:
            # 논리적 사고가 필요한 퍼즐 요소 확인
            return True  # 기본값
        except:
            return False
    
    def _check_wisdom_sources(self, world, player_pos):
        """지혜의 원천 확인 (철학자용)"""
        try:
            # 철학적 통찰을 얻을 수 있는 장소 확인
            return True  # 기본값
        except:
            return False
    
    def _check_arena_areas(self, world, player_pos):
        """투기장 환경 확인 (검투사용)"""
        try:
            # 검투사의 기술을 발휘하기 적합한 투기장 같은 환경 확인
            return True  # 기본값
        except:
            return False
    
    def _check_performance_space(self, world, player_pos):
        """공연 공간 확인 (검투사용)"""
        try:
            # 화려한 기술을 선보일 수 있는 공간 확인
            return True  # 기본값
        except:
            return False
    
    def _check_chivalric_grounds(self, world, player_pos):
        """기사도 정신 발현 땅 확인 (기사용)"""
        try:
            # 기사도 정신을 발휘하기 적합한 장소 확인
            return True  # 기본값
        except:
            return False
    
    def _detect_weak_allies_nearby(self, player_pos):
        """약한 아군 탐지 (기사용)"""
        try:
            # 보호가 필요한 약한 동료나 민간인 확인
            return []  # 기본값
        except:
            return []
    
    def _detect_noble_artifacts(self, treasures):
        """귀족 유물 탐지 (기사용)"""
        try:
            # 기사에게 어울리는 고귀한 유물 확인
            return len(treasures) > 0  # 임시 구현
        except:
            return False
    
    def _check_holy_sites(self, world, player_pos):
        """성지 확인 (신관용)"""
        try:
            # 신성한 기운이 있는 성지 확인
            return False  # 기본값
        except:
            return False
    
    def _detect_divine_relics(self, treasures):
        """신성 유물 탐지 (신관용)"""
        try:
            # 신의 힘이 깃든 성스러운 유물 확인
            return len(treasures) > 0  # 임시 구현
        except:
            return False
    
    def _check_destructible_objects(self, world, player_pos):
        """파괴 가능한 객체 확인 (광전사용)"""
        try:
            # 광전사가 파괴할 수 있는 환경 요소 확인
            return True  # 기본값
        except:
            return False
    
    def _generate_tactical_recommendations(self, enemies, treasures, traps, exits, advantages, dangers) -> List[str]:
        """전술 추천사항 생성 - 27개 직업별 맞춤 전략"""
        recommendations = []
        
        # 직업별 전술 고려
        job_prefs = self.job_profile.tactical_preferences
        
        # 전투 직업군 (8개) 전술
        if self.character_class == "전사":
            if len(enemies) > 0:
                recommendations.append("제가 앞장서서 적들을 하나씩 상대하겠습니다!")
                recommendations.append("방패로 막으면서 동료들을 보호할게요!")
            if len(dangers) > 0:
                recommendations.append("위험한 곳은 제가 먼저 들어가겠습니다!")
        
        elif self.character_class == "아크메이지":
            if len(enemies) > 1:
                recommendations.append("광역 마법으로 적들을 한번에 처리할 수 있습니다!")
                recommendations.append("원소의 약점을 파악해서 효율적으로 공격하겠어요!")
            if len(traps) > 0:
                recommendations.append("마법으로 함정의 구조를 분석해보겠습니다!")
        
        elif self.character_class == "궁수":
            if len(enemies) > 0:
                recommendations.append("높은 곳에서 원거리 지원 사격을 하겠습니다!")
                recommendations.append("적들의 움직임을 예측해서 정확히 조준할게요!")
            if len(exits) > 1:
                recommendations.append("여러 탈출로를 확보한 상태에서 교전하세요!")
        
        elif self.character_class == "도적":
            if len(traps) > 0:
                recommendations.append("함정 해제는 제 전문 분야입니다!")
                recommendations.append("은밀하게 접근해서 함정을 무력화할게요!")
            if len(treasures) > 0:
                recommendations.append("보물의 함정 여부를 먼저 확인해보겠습니다!")
            if len(enemies) > 0:
                recommendations.append("뒤에서 기습 공격을 가하겠습니다!")
        
        elif self.character_class == "성기사":
            if len(enemies) > 0:
                recommendations.append("정의의 이름으로 악을 물리치겠습니다!")
                recommendations.append("성스러운 빛으로 적들을 정화하겠어요!")
            if len(dangers) > 0:
                recommendations.append("신의 가호로 모든 위험을 막아내겠습니다!")
        
        elif self.character_class == "암흑기사":
            if len(enemies) > 0:
                recommendations.append("어둠의 힘으로 적들을 압도하겠습니다!")
                recommendations.append("생명력을 흡수하면서 지속 전투를 벌일게요!")
            if len(dangers) > 0:
                recommendations.append("어둠은 저를 보호합니다... 두려워할 것 없어요.")
        
        elif self.character_class == "몽크":
            if len(enemies) > 0:
                recommendations.append("연환 타격으로 적들을 제압하겠습니다!")
                recommendations.append("내면의 기를 모아서 강력한 일격을 날릴게요!")
            recommendations.append("마음의 평정을 유지하면서 신중하게 행동하세요.")
        
        elif self.character_class == "바드":
            if len(enemies) > 0:
                recommendations.append("노래로 동료들의 사기를 높여드릴게요!")
                recommendations.append("음파 공격으로 적들을 혼란에 빠뜨리겠습니다!")
            recommendations.append("팀워크가 중요합니다! 함께 힘을 합쳐요!")
        
        # 마법 직업군 (10개) 전술
        elif self.character_class == "네크로맨서":
            if len(enemies) > 0:
                recommendations.append("언데드를 소환해서 적들과 맞서게 하겠습니다!")
                recommendations.append("생명력 흡수로 지속적인 전투를 펼칠게요!")
            recommendations.append("죽음의 마법으로 적들을 약화시키겠어요.")
        
        elif self.character_class == "용기사":
            if len(enemies) > 0:
                recommendations.append("드래곤의 분노로 적들을 불태우겠습니다!")
                recommendations.append("화염 브레스로 광역 피해를 입힐게요!")
            recommendations.append("용족의 위엄을 보여드리겠습니다!")
        
        elif self.character_class == "검성":
            if len(enemies) > 0:
                recommendations.append("검의 극의를 보여드리겠습니다!")
                recommendations.append("완벽한 검술로 적들을 제압할게요!")
            recommendations.append("검과 하나가 되어 싸우겠습니다.")
        
        elif self.character_class == "정령술사":
            if len(enemies) > 0:
                recommendations.append("원소의 힘으로 적들을 제압하겠습니다!")
                recommendations.append("환경을 조작해서 유리한 상황을 만들어드릴게요!")
            if len(traps) > 0:
                recommendations.append("정령들에게 함정의 위치를 물어보겠어요!")
        
        elif self.character_class == "시간술사":
            if len(enemies) > 0:
                recommendations.append("시간을 조작해서 전투를 유리하게 이끌어가겠습니다!")
                recommendations.append("미래를 예견해서 적들의 공격을 피할게요!")
            recommendations.append("시간의 흐름을 읽고 최적의 타이밍을 찾겠어요.")
        
        elif self.character_class == "연금술사":
            if len(enemies) > 0:
                recommendations.append("화학 반응을 일으켜서 폭발적인 피해를 줄게요!")
                recommendations.append("다양한 포션으로 지원하겠습니다!")
            recommendations.append("과학의 힘으로 모든 문제를 해결해보겠어요!")
        
        elif self.character_class == "차원술사":
            if len(enemies) > 0:
                recommendations.append("차원을 조작해서 적들을 혼란에 빠뜨리겠습니다!")
                recommendations.append("공간을 왜곡시켜서 유리한 위치를 만들어드릴게요!")
            if len(exits) == 0:
                recommendations.append("차원의 문을 열어서 탈출로를 만들 수 있어요!")
        
        elif self.character_class == "마검사":
            if len(enemies) > 0:
                recommendations.append("검과 마법을 조화롭게 사용해서 싸우겠습니다!")
                recommendations.append("상황에 따라 유연하게 전술을 바꿀게요!")
            recommendations.append("균형잡힌 접근법으로 문제를 해결하겠어요.")
        
        elif self.character_class == "기계공학자":
            if len(enemies) > 0:
                recommendations.append("기계 장치로 적들을 무력화시키겠습니다!")
                recommendations.append("정밀한 계산으로 최적의 공격을 실행할게요!")
            if len(traps) > 0:
                recommendations.append("기계 구조를 분석해서 함정을 해제하겠습니다!")
        
        elif self.character_class == "무당":
            if len(enemies) > 0:
                recommendations.append("조상의 영혼들에게 도움을 요청하겠습니다!")
                recommendations.append("영적인 힘으로 적들을 물리칠게요!")
            recommendations.append("신령한 가호로 모든 위험을 막아내겠어요.")
        
        # 특수 직업군 (9개) 전술
        elif self.character_class == "암살자":
            if len(enemies) > 0:
                recommendations.append("그림자에 숨어서 적들을 하나씩 조용히 처리하겠습니다!")
                recommendations.append("치명적인 급소 공격으로 단숨에 끝내겠어요!")
            recommendations.append("완벽한 은밀함으로 임무를 수행하겠습니다.")
        
        elif self.character_class == "해적":
            if len(enemies) > 0:
                recommendations.append("자유로운 영혼으로 적들을 압도하겠습니다!")
                recommendations.append("예측 불가능한 공격으로 혼란을 만들어드릴게요!")
            if len(treasures) > 0:
                recommendations.append("보물은 제가 안전하게 확보하겠어요!")
        
        elif self.character_class == "사무라이":
            if len(enemies) > 0:
                recommendations.append("명예로운 결투로 적들과 맞서겠습니다!")
                recommendations.append("부시도 정신으로 완벽한 검술을 보여드릴게요!")
            recommendations.append("사무라이의 도를 지키면서 싸우겠습니다.")
        
        elif self.character_class == "드루이드":
            if len(enemies) > 0:
                recommendations.append("자연의 힘을 빌려서 적들을 제압하겠습니다!")
                recommendations.append("야생동물들을 불러서 도움을 받을게요!")
            recommendations.append("자연과의 조화를 유지하면서 행동하세요.")
        
        elif self.character_class == "철학자":
            if len(enemies) > 0:
                recommendations.append("논리적 분석으로 적들의 약점을 찾아내겠습니다!")
                recommendations.append("지혜로운 판단으로 최적의 전략을 세울게요!")
            recommendations.append("모든 상황을 철학적으로 접근해보겠어요.")
        
        elif self.character_class == "검투사":
            if len(enemies) > 0:
                recommendations.append("화려한 기술로 적들을 압도하겠습니다!")
                recommendations.append("관중들이 환호할 만한 멋진 전투를 보여드릴게요!")
            recommendations.append("검투사의 자존심을 걸고 싸우겠습니다!")
        
        elif self.character_class == "기사":
            if len(enemies) > 0:
                recommendations.append("기사도 정신으로 정정당당하게 싸우겠습니다!")
                recommendations.append("약자를 보호하면서 전투를 펼칠게요!")
            recommendations.append("명예로운 방법으로 문제를 해결하겠어요.")
        
        elif self.character_class == "신관":
            if len(enemies) > 0:
                recommendations.append("신성한 마법으로 악을 정화하겠습니다!")
                recommendations.append("동료들을 치유하면서 지원하겠어요!")
            recommendations.append("신의 뜻에 따라 행동하겠습니다.")
        
        elif self.character_class == "광전사":
            if len(enemies) > 0:
                recommendations.append("분노를 폭발시켜서 모든 적을 파괴하겠습니다!")
                recommendations.append("광폭화 상태로 압도적인 힘을 보여드릴게요!")
            recommendations.append("파괴의 본능에 몸을 맡기겠어요!")
        
        # 일반적인 상황 추천
        if len(enemies) == 0 and len(treasures) > 0:
            recommendations.append("보물을 안전하게 수집할 절호의 기회입니다!")
        
        if len(dangers) > len(advantages):
            recommendations.append("위험이 많으니 신중하게 진행하세요!")
        
        if len(exits) == 0:
            recommendations.append("탈출로가 없습니다... 전투를 피할 수 없을 것 같아요.")
        
        if len(advantages) > len(dangers):
            recommendations.append("상황이 유리합니다! 적극적으로 행동해도 좋을 것 같아요!")
        
        return recommendations
    
    def generate_contextual_response(self, situation: str, player_message: str, 
                                   character_analysis: CharacterAnalysis,
                                   environment_analysis: EnvironmentAnalysis) -> str:
        """상황 맥락 기반 응답 생성"""
        
        # 기본 응답 (언어모델 없는 경우)
        base_response = self._generate_base_response(situation, player_message, character_analysis)
        
        # 언어모델이 있는 경우 향상된 응답 생성
        if self.llm_manager and self.conversation_manager:
            try:
                # 상황 컨텍스트 구성
                context = self._build_conversation_context(
                    situation, character_analysis, environment_analysis
                )
                
                # 성격 프롬프트 포함
                personality_prompt = f"""
당신은 {self.character_name}이며, {self.character_class} 직업입니다.
성격 특성: {', '.join(self.job_profile.personality_traits['core_traits'])}
현재 기분: {character_analysis.mood.value}
스트레스 레벨: {character_analysis.stress_level}/100
플레이어와의 관계: {character_analysis.relationship_with_player}/100

상황: {situation}
환경: {len(environment_analysis.visible_enemies)}명의 적, {len(environment_analysis.treasures)}개의 보물 발견
위험 요소: {', '.join(environment_analysis.dangers) if environment_analysis.dangers else '없음'}

{self.character_class}의 특성을 살려 자연스럽고 일관된 성격으로 응답하세요.
한국어로 답변하고, 게임 상황에 맞는 조언도 포함하세요.
"""
                
                enhanced_response = self.conversation_manager.send_message(
                    f"{personality_prompt}\\n\\n플레이어 메시지: {player_message}",
                    context=context
                )
                
                if enhanced_response and len(enhanced_response.strip()) > 10:
                    return enhanced_response
                    
            except Exception as e:
                print(f"⚠️ 언어모델 응답 생성 실패: {e}")
        
        return base_response
    
    def _generate_base_response(self, situation: str, player_message: str, 
                              character_analysis: CharacterAnalysis) -> str:
        """기본 응답 생성 (언어모델 없는 경우) - 성별 반영"""
        
        # 성별에 따른 말투 조정
        gender_suffix = self._get_gender_appropriate_suffix()
        
        # 상황별 기본 응답
        if "전투" in situation:
            if character_analysis.hp_ratio < 0.3:
                return f"({self.character_name}) 위험합니다! 치료가 필요해요{gender_suffix}"
            elif character_analysis.mood == CharacterState.CONFIDENT:
                return f"({self.character_name}) 좋아요! 이길 수 있습니다{gender_suffix}"
            else:
                combat_responses = self.job_profile.speech_patterns.get('combat', 
                    ["전투 준비 완료!", "함께 싸워요!", "제가 도울게요!"])
                base_response = random.choice(combat_responses)
                return f"({self.character_name}) {base_response}{gender_suffix}"
        
        elif "탐험" in situation:
            if len(player_message) > 0:
                discovery_responses = self.job_profile.speech_patterns.get('discovery',
                    ["흥미롭네요!", "자세히 살펴봅시다.", "좋은 발견입니다!"])
                base_response = random.choice(discovery_responses)
                return f"({self.character_name}) {base_response}{gender_suffix}"
            else:
                return f"({self.character_name}) 어디로 가볼까요{gender_suffix}"
        
        # 기본 대화
        greeting_responses = self.job_profile.speech_patterns.get('greetings',
            ["안녕하세요!", "반갑습니다!", "무엇을 도와드릴까요?"])
        base_response = random.choice(greeting_responses)
        return f"({self.character_name}) {base_response}{gender_suffix}"
    
    def _get_gender_appropriate_suffix(self) -> str:
        """성별에 따른 적절한 말투 반환 (남성/여성만 지원)"""
        if self.gender == "여성":
            return "~"  # 여성적 말투 (부드러운 톤)
        else:  # 남성이 기본값
            return "."  # 남성적 말투 (단정한 톤)
    
    def _apply_gender_to_speech(self, text: str) -> str:
        """말하기 패턴에 성별 특성 적용"""
        if self.gender == "여성":
            # 여성적 표현으로 변환
            text = text.replace("이다.", "이에요.")
            text = text.replace("한다.", "해요.")
            text = text.replace("갑니다.", "가요.")
            text = text.replace("됩니다.", "돼요.")
        elif self.gender == "남성":
            # 남성적 표현 유지 (격식체)
            if not any(ending in text for ending in ["다.", "요.", "니다.", "습니다."]):
                if text.endswith("!"):
                    text = text[:-1] + "다!"
                elif text.endswith("?"):
                    text = text[:-1] + "나?"
        
        return text
    
    def _build_conversation_context(self, situation: str, 
                                  character_analysis: CharacterAnalysis,
                                  environment_analysis: EnvironmentAnalysis) -> str:
        """대화 컨텍스트 구성"""
        context_parts = [
            f"게임 상황: {situation}",
            f"캐릭터 상태: HP {character_analysis.hp_ratio*100:.0f}%, MP {character_analysis.mp_ratio*100:.0f}%",
            f"기분: {character_analysis.mood.value}",
            f"주변 환경: 적 {len(environment_analysis.visible_enemies)}명, 보물 {len(environment_analysis.treasures)}개"
        ]
        
        if environment_analysis.dangers:
            context_parts.append(f"위험 요소: {', '.join(environment_analysis.dangers)}")
        
        if environment_analysis.tactical_advantages:
            context_parts.append(f"전술적 이점: {', '.join(environment_analysis.tactical_advantages)}")
        
        return " | ".join(context_parts)
    
    def update_relationship(self, event_type: str, magnitude: int, context: str = ""):
        """플레이어와의 관계도 업데이트"""
        old_relationship = self.relationship_with_player
        
        # 직업별 관계 수정치 적용
        job_modifier = 1.0
        if event_type == "combat_victory" and self.character_class in ["전사", "광전사"]:
            job_modifier = 1.5
        elif event_type == "knowledge_sharing" and self.character_class in ["아크메이지", "철학자"]:
            job_modifier = 1.5
        elif event_type == "treasure_found" and self.character_class in ["도적", "해적"]:
            job_modifier = 1.5
        
        change = int(magnitude * job_modifier)
        self.relationship_with_player = max(-100, min(100, self.relationship_with_player + change))
        
        # 학습 DB에 기록
        if self.learning_db:
            try:
                cursor = self.learning_db.cursor()
                cursor.execute('''
                    INSERT INTO relationships (timestamp, event_type, relationship_change, current_level, context)
                    VALUES (?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), event_type, change, self.relationship_with_player, context))
                self.learning_db.commit()
            except Exception as e:
                print(f"⚠️ 관계 기록 실패: {e}")
        
        # 관계 변화에 따른 반응
        if abs(change) >= 10:
            if change > 0:
                print(f"💖 {self.character_name}가 당신을 더 좋아합니다! (+{change})")
            else:
                print(f"💔 {self.character_name}와의 관계가 나빠졌습니다... ({change})")
    
    def get_status_report(self) -> str:
        """현재 상태 보고"""
        relationship_desc = "중립"
        if self.relationship_with_player >= 75:
            relationship_desc = "매우 친밀"
        elif self.relationship_with_player >= 50:
            relationship_desc = "친근함"
        elif self.relationship_with_player >= 25:
            relationship_desc = "보통"
        elif self.relationship_with_player >= 0:
            relationship_desc = "서먹함"
        else:
            relationship_desc = "불편함"
        
        mood_desc = self.current_mood.value
        
        status_report = f"""
🤖 {BRIGHT_CYAN}{self.character_name}{RESET} ({YELLOW}{self.character_class}{RESET})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💝 관계도: {GREEN}{relationship_desc}{RESET} ({self.relationship_with_player}/100)
😊 기분: {CYAN}{mood_desc}{RESET}
📊 스트레스: {RED if self.stress_level > 70 else YELLOW if self.stress_level > 30 else GREEN}{self.stress_level}/100{RESET}
🧠 언어모델: {'🟢 연결됨' if self.llm_manager else '🔴 오프라인'}
🗺️ 맵 스캐너: {'🟢 활성화' if self.map_scanner else '🔴 비활성화'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 준비 상태: {GREEN}대화 및 전술 지원 가능{RESET}
        """
        
        return status_report.strip()
    
    def __del__(self):
        """소멸자 - 데이터베이스 연결 정리"""
        if hasattr(self, 'learning_db') and self.learning_db:
            try:
                self.learning_db.close()
            except:
                pass

def test_integrated_ai_system():
    """통합 AI 시스템 테스트"""
    print("🧪 통합 AI 동료 시스템 테스트")
    print("=" * 60)
    
    # 여러 직업의 AI 동료 생성
    test_jobs = ['전사', '아크메이지', '궁수', '도적', '성기사']
    ai_companions = []
    
    for i, job in enumerate(test_jobs):
        try:
            companion = IntegratedAICompanion(f"테스트_{job}", job)
            ai_companions.append(companion)
            print(f"✅ {job} AI 동료 생성 성공")
            
            # 상태 보고서 테스트
            status = companion.get_status_report()
            print(status)
            
            # 간단한 대화 테스트
            response = companion.generate_contextual_response(
                "던전 탐험",
                "안녕! 함께 모험하자!",
                CharacterAnalysis(0.8, 0.7, 0.9, [], "양호", CharacterState.ENERGETIC, 20, 60),
                EnvironmentAnalysis(5, [(1,1)], [(2,2)], [], [(0,5)], ["높은 지대 확보"], [], ["조심스럽게 진행하세요"])
            )
            print(f"💬 {job} 응답: {response}")
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ {job} AI 동료 생성 실패: {e}")
    
    print(f"\\n📊 테스트 결과: {len(ai_companions)}/{len(test_jobs)}개 성공")
    return ai_companions

if __name__ == "__main__":
    test_integrated_ai_system()
