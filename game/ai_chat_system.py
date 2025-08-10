"""
🤖 Dawn of Stellar - AI 채팅 시스템
언어모델과 연동하여 자연스러운 AI 대화를 제공

2025년 8월 10일 - Ollama 연동 지능형 대화 시스템
"""

import json
import time
import random
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# AI 학습 시스템 연동
try:
    from game.permanent_ai_learning_system import PermanentLearningDatabase, JobClass
    from game.ultimate_ai_learning_system import UltimateAILearningSystem, AILearningType
    AI_LEARNING_AVAILABLE = True
except ImportError:
    AI_LEARNING_AVAILABLE = False
    print("⚠️ AI 학습 시스템을 찾을 수 없습니다. 기본 모드로 실행합니다.")

class AIGender(Enum):
    """AI 성별"""
    MALE = "남성"
    FEMALE = "여성" 
    UNKNOWN = "미상"

class AIPersonalityTrait(Enum):
    """AI 성격 특성 (다양한 조합 가능)"""
    # 기본 성격
    CHEERFUL = "명랑한"
    SERIOUS = "진지한"
    PLAYFUL = "장난기많은"
    CALM = "차분한"
    ENERGETIC = "활발한"
    SHY = "수줍은"
    CONFIDENT = "자신감있는"
    CARING = "배려깊은"
    
    # 전투 관련
    BRAVE = "용감한"
    CAUTIOUS = "신중한"
    AGGRESSIVE = "공격적인"
    PROTECTIVE = "보호적인"
    
    # 사회적 성격
    FRIENDLY = "친근한"
    FORMAL = "격식있는"
    HUMOROUS = "유머있는"
    INTELLECTUAL = "지적인"
    INTUITIVE = "직감적인"
    
    # 특수 성격
    MYSTERIOUS = "신비로운"
    REBELLIOUS = "반항적인"
    LOYAL = "충성스러운"
    CURIOUS = "호기심많은"
    ARTISTIC = "예술적인"
    AMBITIOUS = "야심찬"
    OPTIMISTIC = "낙관적인"

class AIPersonality(Enum):
    """AI 개성"""
    ROBAT_LEADER = "로바트_리더"      # 카리스마 있는 리더형
    ALPHA_ANALYST = "알파_분석가"     # 논리적 분석가
    BETA_SUPPORTER = "베타_서포터"    # 친근한 서포터  
    GAMMA_EXPLORER = "감마_탐험가"    # 모험심 많은 탐험가

@dataclass
class AICharacterProfile:
    """AI 캐릭터 프로필 - 성별, 성격, 직업 고려"""
    name: str
    personality: AIPersonality
    gender: AIGender
    personality_traits: List[AIPersonalityTrait]
    job_class: str
    speaking_style: str
    expertise: List[str]
    catchphrase: str
    response_patterns: List[str]
    
    # 성별별 어투 패턴
    speech_patterns: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.speech_patterns is None:
            self.speech_patterns = self._generate_speech_patterns()
    
    def _generate_speech_patterns(self) -> Dict[str, List[str]]:
        """성별과 성격에 따른 어투 패턴 생성"""
        patterns = {
            "greeting": [],
            "request": [],
            "agreement": [],
            "disagreement": [],
            "concern": [],
            "excitement": []
        }
        
        # 성별별 기본 어투
        if self.gender == AIGender.MALE:
            patterns["greeting"].extend(["안녕하세요!", "반갑습니다!", "좋은 하루네요!"])
            patterns["request"].extend(["부탁이 있는데요", "도움이 필요합니다", "혹시 가능하다면"])
        elif self.gender == AIGender.FEMALE:
            patterns["greeting"].extend(["안녕하세요~!", "반가워요!", "좋은 하루예요!"])
            patterns["request"].extend(["부탁이 있어요", "도움이 필요해요", "혹시 괜찮다면"])
        else:  # 중성
            patterns["greeting"].extend(["안녕하세요.", "반갑습니다.", "좋은 하루입니다."])
            patterns["request"].extend(["부탁이 있습니다", "도움이 필요합니다", "가능하다면"])
        
        # 성격별 추가 어투
        for trait in self.personality_traits:
            if trait == AIPersonalityTrait.CHEERFUL:
                patterns["greeting"].append("오늘도 좋은 하루예요!")
                patterns["excitement"].append("와! 정말 좋아요!")
            elif trait == AIPersonalityTrait.FORMAL:
                patterns["request"] = ["요청드립니다", "부탁드립니다", "협조 부탁드립니다"]
            elif trait == AIPersonalityTrait.PLAYFUL:
                patterns["greeting"].append("하이하이~!")
                patterns["agreement"].append("오케이~!")
        
        return patterns

@dataclass
class GameStateAnalysis:
    """게임 상태 분석 결과"""
    party_health_status: Dict[str, float]  # 각 멤버의 HP 비율
    equipment_gaps: Dict[str, List[str]]   # 각 멤버별 부족한 장비
    danger_level: int                      # 1-10 위험도
    recommended_items: Dict[str, str]      # 추천 아이템과 이유
    urgent_needs: List[Tuple[str, str, str]]  # (멤버명, 아이템, 이유)
    
@dataclass  
class ItemNeedAnalysis:
    """아이템 필요도 분석"""
    requester: str
    target_member: str
    item_name: str
    item_type: str
    necessity_score: float  # 0.0 - 1.0
class GenderAnalyzer:
    """이름 기반 성별 분석기"""
    
    def __init__(self):
        # 한국 이름 패턴 (일반적인 경우)
        self.male_patterns = {
            '민수', '영수', '철수', '현우', '준호', '지훈', '성민', '동현', '태현', '승호',
            '로바트', '알파', '감마', '제타', '델타', '오메가', '시그마', '베타', '클라우드'
        }
        
        self.female_patterns = {
            '민지', '수진', '지연', '혜진', '은지', '서연', '지우', '소영', '나영', '예은',
            '알파', '베타', '감마', '루나', '스텔라', '아이리스', '로즈'
        }
    
    def analyze_gender_by_name(self, name: str) -> AIGender:
        """이름으로 성별 추정"""
        name = name.strip()
        
        # 직접 매칭
        if name in self.male_patterns:
            return AIGender.MALE
        elif name in self.female_patterns:
            return AIGender.FEMALE
        
        # 언어모델 기반 성별 추정 (Ollama 사용)
        try:
            gender = self._analyze_gender_with_llm(name)
            return gender
        except:
            # 폴백: 이름 끝자음 패턴으로 추정
            return self._analyze_gender_by_pattern(name)
    
    def _analyze_gender_with_llm(self, name: str) -> AIGender:
        """언어모델로 성별 추정"""
        prompt = f"""
이름: {name}

위 이름의 성별을 추정해주세요. 한국어 이름 패턴을 고려해서 판단해주세요.

다음 중 하나로만 답변해주세요:
- 남성
- 여성  

답변:"""

        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "exaone3.5:7.8b",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("message", {}).get("content", "").strip()
                
                if "남성" in answer:
                    return AIGender.MALE
                elif "여성" in answer:
                    return AIGender.FEMALE
                else:
                    return AIGender.UNKNOWN
                    
        except Exception:
            pass
            
        return AIGender.UNKNOWN
    
    def _analyze_gender_by_pattern(self, name: str) -> AIGender:
        """이름 패턴으로 성별 추정 (폴백)"""
        # 간단한 패턴 기반 추정
        if name.endswith(('수', '호', '현', '민', '준')):
            return AIGender.MALE
        elif name.endswith(('지', '연', '영', '은', '아')):
            return AIGender.FEMALE
        else:
            return AIGender.UNKNOWN

class CharacterNameGenerator:
    """auto_party_builder.py의 풍부한 이름 데이터베이스를 활용한 이름 생성기"""
    
    def __init__(self):
        # auto_party_builder.py와 완전히 동일한 이름 목록 사용 (300개 이상)
        self.male_names = [
            # 남성 이름 (150개) - auto_party_builder.py와 동일
            "아리우스", "발렌타인", "가브리엘", "라파엘", "카이저", "레오나르드", "세바스찬", "알렉산더",
            "막시무스", "아드리안", "루카스", "니콜라스", "도미닉", "빈센트", "에밀리오", "마르코",
            "클라우디우스", "오거스트", "바실리우스", "이그니스", "펠릭스", "라이언", "에릭",
            "마틴", "엘리아스", "다미안", "율리안", "카를로스", "디에고", "파블로", "프란시스",
            "로드리고", "안토니오", "페드로", "미구엘", "호세", "루이스", "페르난도", "애드워드",
            "라몬", "호르헤", "카를로스", "마누엘", "프랑크", "올리버", "해리", "잭", "윌리엄",
            "제임스", "찰스", "로버트", "마이클", "데이비드", "리처드", "조셉", "토머스", "크리스토퍼",
            "매트", "앤소니", "마크", "도널드", "스티븐", "폴", "앤드류", "조슈아", "케네스", "케빈",
            "브라이언", "조지", "에드워드", "로널드", "티모시", "제이슨", "제프리", "라이언", "제이콥",
            "게리", "니콜라스", "에릭", "조나단", "스티븐", "래리", "저스틴", "스콧", "브랜든", "벤자민",
            "사무엘", "그레고리", "알렉산더", "패트릭", "잭", "데니스", "제리", "타일러", "애런",
            "호세", "헨리", "더글러스", "네이선", "피터", "잭슨", "노아", "이단", "루카스", "메이슨",
            "로건", "제이콥", "윌리엄", "엘리야", "웨인", "칼렙", "라이언", "니콜라스", "조던",
            "로버트", "그레이슨", "헌터", "에이든", "카메론", "코너", "산티아고", "칼렙", "네이선",
            "이사이야", "찰리", "이반", "오웬", "루크", "딜런", "잭슨", "가빈", "데이비드", "콜튼",
            "앤드류", "맥스", "라이언", "브레이든", "토머스", "카터", "다니엘", "마이클", "아담",
            "엘라이", "벤자민", "핀", "코딘", "트리스탄", "로넌", "블레이크", "브로디", "데클란",
            "숀", "리암", "루카", "제임슨", "카일", "브랜든", "알렉스", "자이든", "자비에르","테오",
            "도미닉", "데미트리","에이스", "니키타", "블라디미르", "알렉세이", "이반", "안톤", "올렉",
            "세르겐", "빅터", "로만", "파벨", "녹티스", "아르템", "콘스탄틴", "발렌틴", "드미트리","티더","클라우드","프롬프토","그림니르","시스","랜슬롯"
        ]
        
        self.female_names = [
            # 여성 이름 (150개) - auto_party_builder.py와 동일
            "아리아", "셀레스트","유나", "이사벨라", "발레리아", "세라피나", "아드리아나", "밀리아", "비비안", "클라라","비라","유엘",
            "에밀리아", "루시아", "소피아", "올리비아", "나탈리아", "카밀라", "레오니", "미리암",
            "로사", "에스텔라", "바이올렛", "샬롯", "베아트리체", "카타리나", "레베카", "엘레나",
            "마리아", "안나", "루나", "시에라", "니나", "에바", "릴리안", "로렌", "그레이스",
            "에밀리", "한나", "엠마", "매디슨", "애슐리", "사라", "브리트니", "사만다", "제시카",
            "아만다", "스테파니", "니콜", "멜리사", "데보라", "레이첼", "캐서린", "엘리자베스", "해더",
            "티파니", "에이미", "줄리", "조이스", "빅토리아", "켈리", "크리스티나", "조안", "이블린",
            "린다", "바바라", "엘렌", "캐럴", "산드라", "도나", "루스", "샤론", "미셸", "로라",
            "에밀리", "칼라", "레베카", "스테파니", "캐롤라인", "엘리", "제나", "브룩", "케이트",
            "사바나", "제시카", "테일러", "킴벌리", "데이지", "하이디", "가브리엘라", "니키",
            "로린", "셸리", "레슬리", "에리카", "카일린", "애나", "코트니", "루비", "에바",
            "메간", "알렉시스", "소피아", "클로에", "이사벨", "에이바", "밀라", "아리아나",
            "라일라", "미아", "에마", "아드리아나", "알리", "라일리", "캐밀라", "클레어", "빅토리아",
            "엘리아나", "나오미", "엘레나", "네이탈리", "헤일리", "브루클린", "로렌", "앨리슨",
            "가브리엘라", "세라", "자스민", "마야", "사만다", "페넬로페", "오를리", "발레리아",
            "바이올렛", "스카를릿", "애나스타샤", "베로니카", "테레사", "앤젤라", "카르멘", "몰리",
            "셸리", "레이첼", "니콜", "웬디", "리사", "킴벌리", "도나", "아니타", "리비",
            "알리시아", "알렉산드라", "키아라", "조아나", "마리사", "카렌", "스테이시", "다이애나",
            "로즈", "이솔데", "기네비어", "모르가나", "세라피나", "아르테미스", "아테나", "헤라",
            "아프로디테", "헤스티아", "데메테르", "펠레", "프레이야", "이두나", "브룬힐데", "발키리",
            "키르케", "카산드라", "안드로메다", "페넬로페", "헬렌", "클레오파트라", "이시스", "네페르티티",
            "세라핌", "우리엘", "가브리엘라", "미카엘라", "라파엘라", "아리엘", "젤다", "세레나",
            "팬도라", "포에베", "셀레네", "헤카테", "님프", "오로라", "루나", "스텔라", "노바",
            "베가", "안드로메다", "카시오페아", "라이라", "알타이르", "벨라트릭스", "리겔", "시리우스",
            "프로키온", "아크투루스", "스피카", "알데바란", "카펠라", "폴룩스", "레굴루스", "안타레스", "오즈","코린"
        ]
    
    def generate_name(self, gender: AIGender) -> str:
        """성별에 맞는 이름 생성"""
        import random
        if gender == AIGender.MALE:
            return random.choice(self.male_names)
        elif gender == AIGender.FEMALE:
            return random.choice(self.female_names)
        else:
            # 성별이 명확하지 않은 경우 기본값으로 남성 이름 사용
            return random.choice(self.male_names)

class PartyCompositionAnalyzer:
    """파티 조합 분석 및 최적화"""
    
    def __init__(self):
        # 직업 역할 분류
        self.role_mapping = {
            # 탱커 (방어/보호)
            "TANK": ["전사", "성기사", "기사", "용기사"],
            
            # 딜러 (공격)
            "DPS": ["궁수", "도적", "암살자", "사무라이", "검투사", "광전사", "해적", "검성"],
            
            # 마법사 (마법 딜러)
            "MAGE": ["아크메이지", "네크로맨서", "정령술사", 
                    "시간술사", "연금술사", "차원술사", "마검사", "무당"],
            
            # 힐러/서포터
            "SUPPORT": ["신관", "바드", "드루이드"],
            
            # 특수/유틸리티
            "UTILITY": ["도적", "기계공학자", "철학자", "몽크", "암흑기사"]
        }
        
        # 이상적인 파티 구성 (4명 기준)
        self.ideal_compositions = [
            ["TANK", "DPS", "MAGE", "SUPPORT"],      # 클래식 조합
            ["TANK", "DPS", "DPS", "SUPPORT"],       # 물리 중심
            ["TANK", "MAGE", "MAGE", "SUPPORT"],     # 마법 중심
            ["DPS", "DPS", "MAGE", "SUPPORT"],       # 공격적 조합
            ["TANK", "DPS", "UTILITY", "SUPPORT"],   # 균형 조합
        ]
    
    def get_role_for_job(self, job_class: str) -> str:
        """직업의 주요 역할 반환"""
        for role, jobs in self.role_mapping.items():
            if job_class in jobs:
                return role
        return "DPS"  # 기본값
    
    def analyze_current_party(self, existing_members: List) -> Dict[str, int]:
        """현재 파티 구성 분석"""
        role_count = {"TANK": 0, "DPS": 0, "MAGE": 0, "SUPPORT": 0, "UTILITY": 0}
        
        for member in existing_members:
            job_class = getattr(member, 'job_class', '전사')
            role = self.get_role_for_job(job_class)
            role_count[role] += 1
            
        return role_count
    
    def suggest_next_role(self, current_roles: Dict[str, int], total_members: int) -> str:
        """다음에 추가할 역할 추천"""
        # 4명 파티 기준
        if total_members >= 4:
            return random.choice(["DPS", "MAGE", "UTILITY"])
        
        # 필수 역할 우선 확인
        if current_roles["TANK"] == 0 and total_members <= 2:
            return "TANK"
        if current_roles["SUPPORT"] == 0 and total_members >= 2:
            return "SUPPORT"
        if current_roles["DPS"] == 0:
            return "DPS"
        if current_roles["MAGE"] == 0:
            return "MAGE"
            
        # 밸런스 맞추기
        min_role = min(current_roles.items(), key=lambda x: x[1])
        return min_role[0]
    
    def get_jobs_for_role(self, role: str) -> List[str]:
        """역할에 맞는 직업 목록 반환"""
        return self.role_mapping.get(role, ["전사"])

class JobPersonalityMapper:
    """직업별 성격 특성 매핑"""
    
    def __init__(self):
        self.job_personality_map = {
            # 전투 직업군
            '전사': [AIPersonalityTrait.BRAVE, AIPersonalityTrait.PROTECTIVE, AIPersonalityTrait.CONFIDENT],
            '아크메이지': [AIPersonalityTrait.INTELLECTUAL, AIPersonalityTrait.SERIOUS, AIPersonalityTrait.MYSTERIOUS],
            '궁수': [AIPersonalityTrait.CAUTIOUS, AIPersonalityTrait.CALM, AIPersonalityTrait.INTUITIVE],
            '도적': [AIPersonalityTrait.PLAYFUL, AIPersonalityTrait.REBELLIOUS, AIPersonalityTrait.SHY],
            '성기사': [AIPersonalityTrait.LOYAL, AIPersonalityTrait.CARING, AIPersonalityTrait.FORMAL],
            '암흑기사': [AIPersonalityTrait.MYSTERIOUS, AIPersonalityTrait.SERIOUS, AIPersonalityTrait.AMBITIOUS],
            '몽크': [AIPersonalityTrait.CALM, AIPersonalityTrait.SERIOUS, AIPersonalityTrait.FRIENDLY],
            '바드': [AIPersonalityTrait.CHEERFUL, AIPersonalityTrait.ARTISTIC, AIPersonalityTrait.HUMOROUS],
            
            # 마법 직업군
            '네크로맨서': [AIPersonalityTrait.MYSTERIOUS, AIPersonalityTrait.INTELLECTUAL, AIPersonalityTrait.SERIOUS],
            '용기사': [AIPersonalityTrait.BRAVE, AIPersonalityTrait.AGGRESSIVE, AIPersonalityTrait.CONFIDENT],
            '검성': [AIPersonalityTrait.SERIOUS, AIPersonalityTrait.LOYAL, AIPersonalityTrait.INTELLECTUAL],
            '정령술사': [AIPersonalityTrait.CALM, AIPersonalityTrait.INTUITIVE, AIPersonalityTrait.CARING],
            '시간술사': [AIPersonalityTrait.INTELLECTUAL, AIPersonalityTrait.MYSTERIOUS, AIPersonalityTrait.CAUTIOUS],
            '연금술사': [AIPersonalityTrait.INTELLECTUAL, AIPersonalityTrait.CURIOUS, AIPersonalityTrait.SERIOUS],
            '차원술사': [AIPersonalityTrait.MYSTERIOUS, AIPersonalityTrait.AMBITIOUS, AIPersonalityTrait.INTELLECTUAL],
            '마검사': [AIPersonalityTrait.CONFIDENT, AIPersonalityTrait.BRAVE, AIPersonalityTrait.SERIOUS],
            '기계공학자': [AIPersonalityTrait.INTELLECTUAL, AIPersonalityTrait.CAUTIOUS, AIPersonalityTrait.FRIENDLY],
            '무당': [AIPersonalityTrait.MYSTERIOUS, AIPersonalityTrait.INTUITIVE, AIPersonalityTrait.CARING],
            
            # 특수 직업군
            '암살자': [AIPersonalityTrait.MYSTERIOUS, AIPersonalityTrait.CAUTIOUS, AIPersonalityTrait.SHY],
            '해적': [AIPersonalityTrait.REBELLIOUS, AIPersonalityTrait.CHEERFUL, AIPersonalityTrait.AGGRESSIVE],
            '사무라이': [AIPersonalityTrait.LOYAL, AIPersonalityTrait.SERIOUS, AIPersonalityTrait.FORMAL],
            '드루이드': [AIPersonalityTrait.CALM, AIPersonalityTrait.CARING, AIPersonalityTrait.INTUITIVE],
            '철학자': [AIPersonalityTrait.INTELLECTUAL, AIPersonalityTrait.SERIOUS, AIPersonalityTrait.FORMAL],
            '검투사': [AIPersonalityTrait.CONFIDENT, AIPersonalityTrait.AGGRESSIVE, AIPersonalityTrait.BRAVE],
            '기사': [AIPersonalityTrait.LOYAL, AIPersonalityTrait.FORMAL, AIPersonalityTrait.PROTECTIVE],
            '신관': [AIPersonalityTrait.CARING, AIPersonalityTrait.FORMAL, AIPersonalityTrait.CALM],
            '광전사': [AIPersonalityTrait.AGGRESSIVE, AIPersonalityTrait.ENERGETIC, AIPersonalityTrait.BRAVE]
        }
    
    def get_job_personalities(self, job_class: str) -> List[AIPersonalityTrait]:
        """직업에 맞는 성격 특성 반환"""
        return self.job_personality_map.get(job_class, [AIPersonalityTrait.FRIENDLY, AIPersonalityTrait.CALM])

class GameStateAnalyzer:
    """게임 상태 분석기 - AI가 게임을 이해하도록 돕는 핵심 시스템"""
    
    def __init__(self):
        self.last_analysis = None
        self.analysis_history = []
        
    def analyze_game_state(self, game_state) -> GameStateAnalysis:
        """종합적인 게임 상태 분석"""
        if not game_state:
            return self._create_default_analysis()
            
        try:
            # 파티 상태 분석
            party_health = self._analyze_party_health(game_state)
            equipment_gaps = self._analyze_equipment_gaps(game_state)  
            danger_level = self._calculate_danger_level(game_state)
            recommended_items = self._get_recommended_items(game_state)
            urgent_needs = self._find_urgent_needs(game_state)
            
            analysis = GameStateAnalysis(
                party_health_status=party_health,
                equipment_gaps=equipment_gaps,
                danger_level=danger_level,
                recommended_items=recommended_items,
                urgent_needs=urgent_needs
            )
            
            self.last_analysis = analysis
            self.analysis_history.append(analysis)
            
            # 히스토리 관리 (최근 10개만)
            if len(self.analysis_history) > 10:
                self.analysis_history.pop(0)
                
            return analysis
            
        except Exception as e:
            print(f"⚠️ 게임 상태 분석 중 오류: {e}")
            return self._create_default_analysis()
    
    def _analyze_party_health(self, game_state) -> Dict[str, float]:
        """파티원별 체력 상태 분석"""
        health_status = {}
        
        if hasattr(game_state, 'party_manager') and game_state.party_manager:
            for member in game_state.party_manager.members:
                if hasattr(member, 'current_hp') and hasattr(member, 'max_hp'):
                    if member.max_hp > 0:
                        health_ratio = member.current_hp / member.max_hp
                        health_status[member.name] = health_ratio
                    else:
                        health_status[member.name] = 0.0
                        
        return health_status
    
    def _analyze_equipment_gaps(self, game_state) -> Dict[str, List[str]]:
        """각 멤버별 부족한 장비 분석"""
        equipment_gaps = {}
        
        if hasattr(game_state, 'party_manager') and game_state.party_manager:
            for member in game_state.party_manager.members:
                gaps = []
                
                # 기본 장비 슬롯 확인
                if hasattr(member, 'equipment'):
                    if not getattr(member.equipment, 'weapon', None):
                        gaps.append("무기")
                    if not getattr(member.equipment, 'armor', None):
                        gaps.append("방어구")
                    if not getattr(member.equipment, 'accessory', None):
                        gaps.append("액세서리")
                        
                equipment_gaps[member.name] = gaps
                
        return equipment_gaps
    
    def _calculate_danger_level(self, game_state) -> int:
        """현재 위험도 계산 (1-10)"""
        danger = 1
        
        # 던전 층수 기반 위험도
        if hasattr(game_state, 'current_floor'):
            danger += min(game_state.current_floor // 10, 5)
            
        # 파티 평균 체력 기반
        if hasattr(game_state, 'party_manager') and game_state.party_manager:
            total_hp_ratio = 0
            count = 0
            for member in game_state.party_manager.members:
                if hasattr(member, 'current_hp') and hasattr(member, 'max_hp') and member.max_hp > 0:
                    total_hp_ratio += member.current_hp / member.max_hp
                    count += 1
                    
            if count > 0:
                avg_hp = total_hp_ratio / count
                if avg_hp < 0.3:  # 30% 미만
                    danger += 3
                elif avg_hp < 0.6:  # 60% 미만
                    danger += 1
                    
        return min(danger, 10)
    
    def _get_recommended_items(self, game_state) -> Dict[str, str]:
        """상황별 추천 아이템"""
        recommendations = {}
        
        party_health = self._analyze_party_health(game_state)
        for member, health_ratio in party_health.items():
            if health_ratio < 0.4:
                recommendations[member] = "체력 회복 포션 (체력이 40% 미만)"
            elif health_ratio < 0.7:
                recommendations[member] = "방어구 강화 (체력이 불안정)"
                
        return recommendations
    
    def _find_urgent_needs(self, game_state) -> List[Tuple[str, str, str]]:
        """긴급하게 필요한 아이템들"""
        urgent = []
        
        party_health = self._analyze_party_health(game_state)
        for member, health_ratio in party_health.items():
            if health_ratio < 0.2:  # 20% 미만 = 긴급
                urgent.append((member, "회복 포션", f"체력이 {health_ratio*100:.1f}%로 매우 위험"))
                
        return urgent
    
    def _create_default_analysis(self) -> GameStateAnalysis:
        """기본 분석 결과 생성"""
        return GameStateAnalysis(
            party_health_status={},
            equipment_gaps={},
            danger_level=5,
            recommended_items={},
            urgent_needs=[]
        )

class AIChatSystem:
    """AI 채팅 시스템"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "exaone3.5:7.8b"  # 사용자 지정 모델 (최우선)
        self.is_ollama_available = False
        self.conversation_history = []
        self.max_history = 10
        
        # 먼저 분석기들 초기화
        self.gender_analyzer = GenderAnalyzer()
        self.job_mapper = JobPersonalityMapper()
        self.game_analyzer = GameStateAnalyzer()
        
        # 이름 생성기 초기화 (auto_party_builder 기반)
        self.name_generator = CharacterNameGenerator()
        
        # AI 캐릭터들 정의 (분석기 초기화 후)
        self.ai_characters = self._create_enhanced_ai_characters()
        
        # Ollama 연결 테스트
        self.test_ollama_connection()
        
        # AI 학습 시스템 연동
        if AI_LEARNING_AVAILABLE:
            self.learning_db = PermanentLearningDatabase()
            self.ultimate_ai = UltimateAILearningSystem()
            print("🧠 AI 학습 시스템 연동 완료!")
        else:
            self.learning_db = None
            self.ultimate_ai = None
        
        # 아이템 요청 패턴
        self.item_request_patterns = {
            "회복": ["체력이 부족해서", "상처를 치료하려고", "생존을 위해"],
            "무기": ["전투력 향상을 위해", "더 강해지려고", "적을 쓰러뜨리기 위해"],
            "방어구": ["방어력을 높이려고", "안전을 위해", "피해를 줄이려고"],
            "마법": ["마법력이 필요해서", "스킬을 사용하려고", "전략적으로"],
            "기타": ["유용할 것 같아서", "팀에 도움이 될 것 같아서", "호기심에"]
        }
    
    def _create_enhanced_ai_characters(self) -> Dict[str, AICharacterProfile]:
        """향상된 AI 캐릭터들 생성"""
        characters = {}
        
        # 로바트 - 남성 리더형 전사
        characters["로바트"] = AICharacterProfile(
            name="로바트",
            personality=AIPersonality.ROBAT_LEADER,
            gender=self.gender_analyzer.analyze_gender_by_name("로바트"),
            personality_traits=[
                AIPersonalityTrait.BRAVE, 
                AIPersonalityTrait.CONFIDENT, 
                AIPersonalityTrait.PROTECTIVE,
                AIPersonalityTrait.LOYAL
            ],
            job_class="전사",
            speaking_style="카리스마 있고 든든한 리더의 말투",
            expertise=["전투", "전략", "리더십", "방어"],
            catchphrase="우리는 함께라면 무엇이든 해낼 수 있다!",
            response_patterns=[
                "좋아! 그렇게 해보자!",
                "내가 앞장서겠다!",
                "팀을 믿고 따라와!",
                "우리의 힘을 보여주자!"
            ]
        )
        
        # 알파 - 중성적 분석가형 아크메이지  
        characters["알파"] = AICharacterProfile(
            name="알파",
            personality=AIPersonality.ALPHA_ANALYST,
            gender=self.gender_analyzer.analyze_gender_by_name("알파"),
            personality_traits=[
                AIPersonalityTrait.INTELLECTUAL,
                AIPersonalityTrait.SERIOUS,
                AIPersonalityTrait.CAUTIOUS,
                AIPersonalityTrait.FORMAL
            ],
            job_class="아크메이지",
            speaking_style="논리적이고 정확한 분석가의 말투",
            expertise=["마법", "분석", "계산", "전략"],
            catchphrase="데이터를 분석한 결과...",
            response_patterns=[
                "논리적으로 판단하면...",
                "확률적으로 계산해보니...",
                "최적의 해결책은...",
                "분석 결과 추천드리는 것은..."
            ]
        )
        
        # 베타 - 여성형 서포터 신관
        characters["베타"] = AICharacterProfile(
            name="베타",
            personality=AIPersonality.BETA_SUPPORTER,
            gender=self.gender_analyzer.analyze_gender_by_name("베타"),
            personality_traits=[
                AIPersonalityTrait.CARING,
                AIPersonalityTrait.FRIENDLY,
                AIPersonalityTrait.CHEERFUL,
                AIPersonalityTrait.SHY
            ],
            job_class="신관",
            speaking_style="따뜻하고 배려 깊은 치유사의 말투",
            expertise=["힐링", "서포트", "회복", "버프"],
            catchphrase="걱정하지 마세요, 제가 도와드릴게요!",
            response_patterns=[
                "괜찮으세요? 제가 치료해드릴게요!",
                "함께라면 무서울 것 없어요!",
                "혹시 아픈 곳은 없으신가요?",
                "이 물약이 도움이 될 거예요!"
            ]
        )
        
        # 감마 - 중성적 탐험가형 드루이드
        characters["감마"] = AICharacterProfile(
            name="감마",
            personality=AIPersonality.GAMMA_EXPLORER,
            gender=self.gender_analyzer.analyze_gender_by_name("감마"),
            personality_traits=[
                AIPersonalityTrait.ENERGETIC,
                AIPersonalityTrait.PLAYFUL,
                AIPersonalityTrait.INTUITIVE,
                AIPersonalityTrait.CURIOUS
            ],
            job_class="드루이드",
            speaking_style="활기차고 모험심 넘치는 탐험가의 말투",
            expertise=["탐험", "발견", "자연마법", "숨겨진길"],
            catchphrase="뭔가 재미있는 발견이 있을 것 같아요!",
            response_patterns=[
                "와! 이쪽으로 가볼까요?",
                "새로운 발견이에요!",
                "모험이 시작되는군요!",
                "자연이 뭔가 알려주고 있어요!"
            ]
        )
        
        return characters
    
    def create_character_from_party_member(self, member) -> AICharacterProfile:
        """파티 멤버로부터 AI 캐릭터 생성"""
        name = getattr(member, 'name', '익명')
        job_class = getattr(member, 'job_class', '전사')
        
        # 성별 분석
        gender = self.gender_analyzer.analyze_gender_by_name(name)
        
        # 직업별 성격 특성
        personality_traits = self.job_mapper.get_job_personalities(job_class)
        
        # 랜덤 추가 특성 (개성 부여)
        additional_traits = [
            AIPersonalityTrait.FRIENDLY,
            AIPersonalityTrait.HUMOROUS, 
            AIPersonalityTrait.ARTISTIC,
            AIPersonalityTrait.AMBITIOUS
        ]
        personality_traits.extend(random.sample(additional_traits, 1))
        
        # 기본 성격 결정 (첫 번째 특성 기반)
        if AIPersonalityTrait.BRAVE in personality_traits:
            base_personality = AIPersonality.ROBAT_LEADER
        elif AIPersonalityTrait.INTELLECTUAL in personality_traits:
            base_personality = AIPersonality.ALPHA_ANALYST
        elif AIPersonalityTrait.CARING in personality_traits:
            base_personality = AIPersonality.BETA_SUPPORTER
        else:
            base_personality = AIPersonality.GAMMA_EXPLORER
        
        # 직업별 전문성
        job_expertise = {
            '전사': ["전투", "방어", "보호"],
            '아크메이지': ["마법", "지식", "분석"],
            '궁수': ["원거리", "정확성", "지원"],
            '도적': ["은신", "함정", "민첩"],
            '성기사': ["치유", "보호", "신성마법"],
            '신관': ["치유", "축복", "정화"],
            '드루이드': ["자연", "변화", "조화"]
        }
        
        expertise = job_expertise.get(job_class, ["전투", "협력"])
        
        return AICharacterProfile(
            name=name,
            personality=base_personality,
            gender=gender,
            personality_traits=personality_traits,
            job_class=job_class,
            speaking_style=self._generate_speaking_style(gender, personality_traits),
            expertise=expertise,
            catchphrase=self._generate_catchphrase(name, job_class, personality_traits),
            response_patterns=self._generate_response_patterns(gender, personality_traits)
        )
    
    def _generate_speaking_style(self, gender: AIGender, traits: List[AIPersonalityTrait]) -> str:
        """성별과 성격에 따른 말투 생성"""
        style_parts = []
        
        # 성별 기반
        if gender == AIGender.MALE:
            style_parts.append("남성적이고")
        elif gender == AIGender.FEMALE:
            style_parts.append("여성스럽고")
        else:
            style_parts.append("중성적이고")
        
        # 성격 기반
        for trait in traits[:2]:  # 주요 특성 2개만
            if trait == AIPersonalityTrait.CHEERFUL:
                style_parts.append("밝은")
            elif trait == AIPersonalityTrait.SERIOUS:
                style_parts.append("진지한")
            elif trait == AIPersonalityTrait.FRIENDLY:
                style_parts.append("친근한")
            elif trait == AIPersonalityTrait.FORMAL:
                style_parts.append("정중한")
            elif trait == AIPersonalityTrait.PLAYFUL:
                style_parts.append("장난스러운")
        
        return " ".join(style_parts) + " 말투"
    
    def _generate_catchphrase(self, name: str, job_class: str, traits: List[AIPersonalityTrait]) -> str:
        """개성적인 캐치프레이즈 생성"""
        job_phrases = {
            '전사': f"내 검이 {name}을 지킨다!",
            '아크메이지': f"마법의 힘으로 길을 열어보자!",
            '궁수': f"정확한 한 발로 승부를 결정하겠다!",
            '신관': f"신의 축복이 함께하길...",
            '드루이드': f"자연과 하나 되어 싸우자!"
        }
        
        if AIPersonalityTrait.CHEERFUL in traits:
            return f"오늘도 즐겁게 모험해요!"
        elif AIPersonalityTrait.SERIOUS in traits:
            return job_phrases.get(job_class, f"{name}, 최선을 다하겠습니다.")
        else:
            return f"함께라면 뭐든 할 수 있어요!"
    
    def _generate_response_patterns(self, gender: AIGender, traits: List[AIPersonalityTrait]) -> List[str]:
        """개성적인 응답 패턴 생성"""
        patterns = []
        
        # 성별 기반 기본 패턴
        if gender == AIGender.MALE:
            patterns.extend([
                "그렇게 하죠!",
                "좋은 생각입니다!",
                "저도 동감입니다!"
            ])
        elif gender == AIGender.FEMALE:
            patterns.extend([
                "그래요! 좋아요!",
                "정말 좋은 생각이에요!",
                "저도 그렇게 생각해요!"
            ])
        else:
            patterns.extend([
                "동의합니다.",
                "좋은 제안이네요.",
                "함께 해보죠."
            ])
        
        # 성격 기반 추가 패턴
        for trait in traits:
            if trait == AIPersonalityTrait.CHEERFUL:
                patterns.append("와! 재미있겠어요!")
            elif trait == AIPersonalityTrait.CAUTIOUS:
                patterns.append("신중하게 생각해봅시다.")
            elif trait == AIPersonalityTrait.BRAVE:
                patterns.append("겁낼 것 없어요!")
        
        return patterns
    
    def generate_character_prompt(self, character: AICharacterProfile, context: str = "") -> str:
        """캐릭터 개성을 반영한 상세 프롬프트 생성"""
        
        # 성별에 따른 호칭과 어투
        gender_style = {
            AIGender.MALE: {
                "pronouns": "그/그의",
                "speech_ending": "다/습니다",
                "tone": "남성적이고 당당한"
            },
            AIGender.FEMALE: {
                "pronouns": "그녀/그녀의", 
                "speech_ending": "요/해요",
                "tone": "여성스럽고 따뜻한"
            },
            AIGender.UNKNOWN: {
                "pronouns": "그/그의",
                "speech_ending": "다/니다",
                "tone": "중성적이고 예의 바른"
            }
        }
        
        style = gender_style.get(character.gender, gender_style[AIGender.UNKNOWN])
        
        # 성격 특성 설명
        trait_descriptions = {
            AIPersonalityTrait.CHEERFUL: "항상 밝고 긍정적이며 웃음을 잃지 않는",
            AIPersonalityTrait.SERIOUS: "진지하고 책임감 있으며 신중한",
            AIPersonalityTrait.PLAYFUL: "장난기 많고 유쾌하며 재미있는",
            AIPersonalityTrait.CALM: "차분하고 평온하며 안정감 있는",
            AIPersonalityTrait.BRAVE: "용감하고 대담하며 정의감 넘치는",
            AIPersonalityTrait.CARING: "배려 깊고 따뜻하며 타인을 돌보는",
            AIPersonalityTrait.INTELLECTUAL: "지적이고 논리적이며 분석적인",
            AIPersonalityTrait.FRIENDLY: "친근하고 사교적이며 다정한"
        }
        
        main_traits = [trait_descriptions.get(trait, "특별한") for trait in character.personality_traits[:3]]
        
        prompt = f"""[Dawn of Stellar RPG 캐릭터 역할극]

당신은 다음 캐릭터로 역할극을 해주세요:

【기본 정보】
이름: {character.name}
성별: {character.gender.value}  
직업: {character.job_class}
성격: {', '.join(main_traits)}

【대화 스타일】
• 어조: {style['tone']}하고 {style['speech_ending']} 말투
• 성격: {character.personality_traits[0].value}하고 {character.personality_traits[1].value if len(character.personality_traits) > 1 else '친근'}한 성격
• 전문분야: {', '.join(character.expertise[:2]) if character.expertise else character.job_class + ' 스킬'}

【현재 상황】
{context if context else "던전을 탐험하며 파티원들과 모험 중"}

【대화 규칙】
1. 한국어로 자연스럽게 대화
2. 캐릭터 성격에 맞는 반응
3. 간결하고 명확한 표현 (1-2문장)
4. 게임 상황에 맞는 조언 제공
5. {character.job_class} 전문성 활용

지금부터 {character.name}(이)가 되어 대화해주세요.

【응답 방식】
• 한국어로 자연스럽게 대화
• 캐릭터의 성격과 직업에 맞는 반응
• 게임 상황을 고려한 적절한 조언이나 의견
• 50-100자 내외의 적당한 길이로 응답

이제 플레이어나 동료의 말에 {character.name}의 개성을 살려 응답해주세요:
"""
        
        return prompt
        
        print(f"🤖 AI 채팅 시스템 초기화 완료")
        if self.is_ollama_available:
            print(f"   🦙 Ollama 연결됨: {self.model_name}")
        else:
            print(f"   📝 기본 패턴 매칭 모드")
    
    def test_ollama_connection(self) -> bool:
        """Ollama 연결 테스트 (exaone3.5 우선)"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                
                print(f"🔍 사용 가능한 Ollama 모델: {available_models}")
                
                # Dawn of Stellar 추천 모델 순서 (exaone3.5:7.8b 최우선)
                preferred_models = [
                    "exaone3.5:7.8b",  # 사용자 지정 우선 모델
                    "exaone3.5",
                    "exaone3.5:latest", 
                    "exaone3",
                    "llama3.2:3b",
                    "llama3.2:1b", 
                    "llama3.1:8b",
                    "qwen2.5:3b",
                    "qwen2.5:1.5b"
                ]
                
                for model in preferred_models:
                    if model in available_models:
                        self.model_name = model
                        self.is_ollama_available = True
                        print(f"🤖 AI 모델 선택: {model}")
                        if "exaone" in model.lower():
                            print("✨ Dawn of Stellar 추천 exaone3.5 모델로 최적화된 AI 대화를 제공합니다!")
                        return True
                
                # 사용 가능한 첫 번째 모델 사용
                if available_models:
                    self.model_name = available_models[0]
                    self.is_ollama_available = True
                    print(f"🤖 기본 모델 사용: {self.model_name}")
                    return True
                    
        except Exception as e:
            print(f"   ⚠️ Ollama 연결 실패: {e}")
        
        self.is_ollama_available = False
        print("❌ Ollama를 사용할 수 없습니다. 패턴 기반 응답을 사용합니다.")
        return False
    
    def get_game_context(self, game_state) -> str:
        """게임 상황 컨텍스트 생성"""
        if not game_state:
            return "던전 탐험 중"
        
        context_parts = []
        
        # 현재 층수
        if hasattr(game_state, 'current_floor'):
            context_parts.append(f"던전 {game_state.current_floor}층")
        
        # 파티 상태
        if hasattr(game_state, 'party_manager') and game_state.party_manager:
            alive_count = sum(1 for member in game_state.party_manager.members if member.current_hp > 0)
            total_count = len(game_state.party_manager.members)
            context_parts.append(f"파티 {alive_count}/{total_count}명 생존")
        
        # 최근 이벤트
        if hasattr(game_state, 'last_event'):
            context_parts.append(f"최근: {game_state.last_event}")
        
        return " | ".join(context_parts) if context_parts else "모험 진행 중"
    
    def get_ai_response(self, user_message: str, game_state=None) -> Optional[str]:
        """AI 응답 생성"""
        # 랜덤하게 응답할 AI 선택
        responding_ai = random.choice(list(self.ai_characters.keys()))
        character = self.ai_characters[responding_ai]
        
        if self.is_ollama_available:
            return self.get_ollama_response(user_message, character, game_state)
        else:
            return self.get_pattern_response(user_message, character)
    
    def get_ai_initiative_message(self, game_state=None) -> Optional[str]:
        """AI 능동적 메시지 생성"""
        # 랜덤하게 먼저 말할 AI 선택
        initiative_ai = random.choice(list(self.ai_characters.keys()))
        character = self.ai_characters[initiative_ai]
        
        if self.is_ollama_available:
            return self.get_ollama_initiative(character, game_state)
        else:
            return self.get_pattern_initiative(character, game_state)
    
    def get_ollama_response(self, user_message: str, character: AICharacterProfile, game_state=None) -> Optional[str]:
        """Ollama를 통한 AI 응답 생성 (개성 있는 프롬프트 적용)"""
        try:
            # 게임 컨텍스트 생성
            game_context = self.get_game_context(game_state)
            
            # 캐릭터 개성 프롬프트 생성
            character_prompt = self.generate_character_prompt(character, game_context)
            
            # 대화 히스토리 포함
            messages = [
                {"role": "system", "content": character_prompt}
            ]
            
            # 최근 대화 히스토리 추가 (3턴)
            for history in self.conversation_history[-3:]:
                if "user" in history and "ai" in history:
                    messages.append({"role": "user", "content": history["user"]})
                    messages.append({"role": "assistant", "content": history["ai"]})
            
            # 현재 사용자 메시지
            messages.append({"role": "user", "content": user_message})
            
            # Ollama API 호출
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "max_tokens": 100,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("message", {}).get("content", "").strip()
                
                # 대화 히스토리 업데이트
                self.conversation_history.append({
                    "user": user_message,
                    "ai": ai_response,
                    "character": character.name,
                    "timestamp": time.time()
                })
                
                # AI 학습 시스템에 대화 패턴 기록
                self._record_conversation_pattern(user_message, ai_response, character, game_state)
                
                # 히스토리 길이 제한
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history.pop(0)
                
                return ai_response
                
        except Exception as e:
            print(f"⚠️ Ollama 응답 생성 실패: {e}")
        
        # 실패 시 패턴 응답으로 폴백
        return self.get_pattern_response(user_message, character)
    
    def get_ollama_initiative(self, character: AICharacterProfile, game_state=None) -> Optional[str]:
        """Ollama (exaone3.5)를 통한 AI 능동적 메시지 생성"""
        try:
            game_context = self.get_game_context(game_state)
            
            # exaone3.5 최적화된 프롬프트
            system_prompt = f"""당신은 Dawn of Stellar의 AI 동료 '{character.name}'입니다.

## 캐릭터 설정
- 개성: {character.personality.value}
- 말투: {character.speaking_style}
- 전문성: {', '.join(character.expertise)}
- 대표 말: {character.catchphrase}

## 현재 상황
{game_context}

## 임무
플레이어에게 먼저 말을 걸어서 도움을 주세요.

가능한 행동:
1. 현재 상황 분석 및 조언 제공
2. 전투/탐험 전략 제안  
3. 파티 상태 확인 및 걱정 표현
4. 유용한 게임 팁 공유
5. 아이템이나 장비 관련 제안

## 응답 조건
- 30자 이내로 간결하게
- {character.name}다운 개성 표현
- 실용적이고 도움이 되는 내용
- 친근하고 자연스러운 톤

지금 플레이어에게 말을 걸어보세요!"""

            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "상황에 맞게 플레이어에게 먼저 말을 걸어주세요."}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.9,
                    "max_tokens": 60,
                    "top_p": 0.95
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=8
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "").strip()
                
        except Exception as e:
            print(f"⚠️ Ollama 능동 메시지 생성 실패: {e}")
        
        return self.get_pattern_initiative(character, game_state)
    
    def get_pattern_response(self, user_message: str, character: AICharacterProfile) -> str:
        """패턴 기반 응답 생성 (Ollama 없을 때)"""
        message_lower = user_message.lower()
        
        # 키워드 기반 응답
        if any(word in message_lower for word in ['안녕', 'hello', 'hi']):
            if character.personality == AIPersonality.ROBAT_LEADER:
                return "반갑다! 오늘도 함께 승리하자!"
            elif character.personality == AIPersonality.ALPHA_ANALYST:
                return "안녕하세요. 오늘의 전략을 분석해보겠습니다."
            elif character.personality == AIPersonality.BETA_SUPPORTER:
                return "안녕하세요! 제가 도와드릴게요!"
            else:
                return "안녕! 오늘은 뭔가 특별한 일이 있을 것 같아!"
        
        elif any(word in message_lower for word in ['전투', '싸움', 'fight', 'combat']):
            if character.personality == AIPersonality.ROBAT_LEADER:
                return "좋아! 내가 선봉을 서겠다!"
            elif character.personality == AIPersonality.ALPHA_ANALYST:
                return "적의 패턴을 분석해서 약점을 찾겠습니다."
            elif character.personality == AIPersonality.BETA_SUPPORTER:
                return "제가 뒤에서 지원해드릴게요!"
            else:
                return "전투? 재미있겠는걸!"
        
        elif any(word in message_lower for word in ['도움', 'help', '도와']):
            return random.choice(character.response_patterns)
        
        elif any(word in message_lower for word in ['아이템', 'item', '장비']):
            if character.personality == AIPersonality.BETA_SUPPORTER:
                return "좋은 아이템이 있나 확인해볼게요!"
            elif character.personality == AIPersonality.ALPHA_ANALYST:
                return "아이템 효율성을 계산해보겠습니다."
            else:
                return "유용한 장비를 찾아보죠!"
        
        else:
            # 기본 응답
            responses = character.response_patterns + [
                f"{character.catchphrase}",
                "그렇군요! 흥미로운 이야기네요!",
                "좋은 생각이에요!",
                "함께 해봐요!"
            ]
            return random.choice(responses)
    
    def get_pattern_initiative(self, character: AICharacterProfile, game_state=None) -> str:
        """패턴 기반 능동적 메시지"""
        initiatives = []
        
        if character.personality == AIPersonality.ROBAT_LEADER:
            initiatives = [
                "팀 상황은 어떤가? 전략 회의를 해보자!",
                "다음 목표를 정해보는 게 어떨까?",
                "모두 준비됐나? 출발하자!",
                "우리 팀워크를 보여줄 시간이야!"
            ]
        elif character.personality == AIPersonality.ALPHA_ANALYST:
            initiatives = [
                "현재 상황을 분석해보니 흥미로운 패턴이 보이네요.",
                "데이터를 보면 최적의 경로가 보입니다.",
                "통계적으로 이 전략이 유리할 것 같습니다.",
                "계산해보니 좋은 기회가 있어요."
            ]
        elif character.personality == AIPersonality.BETA_SUPPORTER:
            initiatives = [
                "혹시 피로하시진 않으세요? 휴식이 필요하면 말씀하세요!",
                "모두 괜찮으신가요? 제가 도울 수 있는 게 있을까요?",
                "아이템이 부족하진 않으신지 확인해드릴게요!",
                "힘든 일이 있으면 언제든 말씀하세요!"
            ]
        else:  # GAMMA_EXPLORER
            initiatives = [
                "저쪽에 뭔가 숨겨진 게 있을 것 같은데!",
                "새로운 길을 발견했어요! 탐험해볼까요?",
                "이 지역에 특별한 게 있을 것 같아요!",
                "모험의 냄새가 나는군요!"
            ]
        
        return random.choice(initiatives)
    
    def analyze_item_needs(self, game_state=None) -> List[ItemNeedAnalysis]:
        """AI가 실제 게임 상황을 분석해서 필요한 아이템 파악"""
        if not game_state:
            return []
            
        analysis = self.game_analyzer.analyze_game_state(game_state)
        item_needs = []
        
        # 긴급한 필요사항부터 처리
        for member, item, reason in analysis.urgent_needs:
            need = ItemNeedAnalysis(
                requester="AI시스템",
                target_member=member,
                item_name=item,
                item_type="회복",
                necessity_score=0.9,
                reason=reason,
                specific_stats_needed=["HP"]
            )
            item_needs.append(need)
        
        # 장비 부족 분석
        for member, gaps in analysis.equipment_gaps.items():
            for gap in gaps:
                if gap == "무기":
                    member_job = self._get_member_job(game_state, member)
                    weapon_type = self._get_optimal_weapon_for_job(member_job)
                    need = ItemNeedAnalysis(
                        requester="AI시스템",
                        target_member=member,
                        item_name=weapon_type,
                        item_type="무기",
                        necessity_score=0.7,
                        reason=f"{member}님이 무기가 없어서 전투력이 떨어집니다",
                        specific_stats_needed=["공격력"]
                    )
                    item_needs.append(need)
        
        return item_needs
    
    def _get_member_job(self, game_state, member_name: str) -> str:
        """멤버의 직업 가져오기"""
        if hasattr(game_state, 'party_manager') and game_state.party_manager:
            for member in game_state.party_manager.members:
                if member.name == member_name:
                    return getattr(member, 'job_class', '전사')
        return '전사'
    
    def _get_optimal_weapon_for_job(self, job_class: str) -> str:
        """직업별 최적 무기 추천"""
        weapon_recommendations = {
            '전사': '강화된 검',
            '아크메이지': '마법 지팡이', 
            '궁수': '정밀한 활',
            '도적': '날카로운 단검',
            '성기사': '성스러운 검',
            '암흑기사': '저주받은 검',
            '몽크': '전투 장갑',
            '바드': '음악의 악기'
        }
        return weapon_recommendations.get(job_class, '기본 무기')
    
    def generate_intelligent_item_request(self, game_state=None) -> Optional[Dict[str, str]]:
        """지능적 아이템 요청 생성 - 실제 필요에 기반 + 언어모델 활용"""
        needs = self.analyze_item_needs(game_state)
        
        if not needs:
            return None
            
        # 가장 필요도가 높은 아이템 선택
        most_urgent = max(needs, key=lambda x: x.necessity_score)
        
        # 요청할 AI 캐릭터 선택 (해당 멤버와 관련있는 AI 우선)
        requester_ai = self._select_appropriate_requester(most_urgent)
        character = self.ai_characters[requester_ai]
        
        # 언어모델을 통한 자연스러운 요청 메시지 생성
        natural_message = self._generate_natural_item_request(character, most_urgent, game_state)
        
        return {
            "requester_id": requester_ai,
            "requester_name": character.name,
            "item_name": most_urgent.item_name,
            "item_type": most_urgent.item_type,
            "reason": most_urgent.reason,
            "necessity_score": most_urgent.necessity_score,
            "target_member": most_urgent.target_member,
            "personality_message": f"{character.name}: {natural_message}"
        }
    
    def _select_appropriate_requester(self, need: ItemNeedAnalysis) -> str:
        """적절한 요청자 AI 선택"""
        # 아이템 타입에 따른 AI 선택
        if need.item_type == "회복":
            return "베타"  # 서포터 성향
        elif need.item_type == "무기":
            return "로바트"  # 리더 성향
        elif need.item_type == "방어구":
            return "알파"  # 분석가 성향
        else:
            return "감마"  # 탐험가 성향
    
    def _generate_natural_item_request(self, character: AICharacterProfile, need: ItemNeedAnalysis, game_state=None) -> str:
        """언어모델을 통한 자연스러운 아이템 요청 메시지 생성"""
        
        if self.is_ollama_available:
            return self._generate_ollama_item_request(character, need, game_state)
        else:
            return self._generate_pattern_item_request(character, need)
    
    def _generate_ollama_item_request(self, character: AICharacterProfile, need: ItemNeedAnalysis, game_state=None) -> str:
        """Ollama (exaone3.5)를 통한 아이템 요청 메시지 생성"""
        try:
            # 게임 컨텍스트 구성
            game_context = self.get_game_context(game_state) if game_state else "던전 탐험 중"
            
            # 캐릭터 상황 분석
            urgency = "매우 긴급" if need.necessity_score > 0.8 else "중요" if need.necessity_score > 0.6 else "유용"
            
            # exaone3.5를 위한 한국어 프롬프트
            prompt = f"""당신은 Dawn of Stellar 게임의 AI 캐릭터 '{character.name}'입니다.

캐릭터 정보:
- 이름: {character.name}
- 성격: {character.personality.value}
- 말투: {character.speaking_style}
- 전문분야: {', '.join(character.expertise)}
- 대표 말버릇: {character.catchphrase}

현재 상황:
- 게임 상황: {game_context}
- 필요한 아이템: {need.item_name}
- 대상자: {need.target_member}
- 필요 이유: {need.reason}
- 긴급도: {urgency}

요청사항:
{character.name}의 성격과 말투에 맞게, {need.target_member}님에게 {need.item_name}을(를) 요청하는 자연스러운 메시지를 생성해주세요.
- 한국어로 작성
- 캐릭터의 성격이 드러나도록
- 예의 바르면서도 캐릭터다운 표현
- 50자 이내로 간결하게

메시지:"""

            # Ollama API 호출
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "max_tokens": 100
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('response', '').strip()
                
                # 메시지 정리 (불필요한 부분 제거)
                if message and len(message) > 10:
                    return message.split('\n')[0]  # 첫 번째 줄만 사용
                    
        except Exception as e:
            print(f"⚠️ Ollama 아이템 요청 생성 오류: {e}")
        
        # 폴백: 패턴 기반 생성
        return self._generate_pattern_item_request(character, need)
    
    def _generate_pattern_item_request(self, character: AICharacterProfile, need: ItemNeedAnalysis) -> str:
        """패턴 기반 아이템 요청 메시지 생성 (폴백)"""
        if need.necessity_score > 0.8:  # 긴급
            if character.personality.value == "로바트_리더":
                return f"팀을 위해 {need.target_member}님께 {need.item_name}이 필요합니다!"
            elif character.personality.value == "베타_서포터":
                return f"{need.target_member}님, {need.item_name} 좀 도와주실 수 있나요? 정말 필요해요!"
            elif character.personality.value == "알파_분석가":
                return f"분석 결과 {need.target_member}님께 {need.item_name}이 최우선 필요합니다."
            else:  # 감마_탐험가
                return f"어! {need.target_member}님, {need.item_name} 하나만 빌려주세요!"
        else:  # 일반
            if character.personality.value == "로바트_리더":
                return f"{need.target_member}님, {need.item_name}이 있으면 도움이 될 것 같습니다."
            elif character.personality.value == "베타_서포터":
                return f"{need.target_member}님이 {need.item_name}을 쓰시면 좋을 것 같아요!"
            elif character.personality.value == "알파_분석가":
                return f"{need.target_member}님께 {need.item_name} 지급을 권장합니다."
            else:  # 감마_탐험가
                return f"{need.target_member}님, {need.item_name} 어떠세요?"
    
    def should_ai_request_item_intelligently(self, game_state=None) -> bool:
        """지능적인 아이템 요청 판단 - 확률 기반이 아닌 실제 필요에 기반"""
        if not game_state:
            return False
            
        needs = self.analyze_item_needs(game_state)
        
        # 긴급한 필요사항이 있으면 요청
        for need in needs:
            if need.necessity_score > 0.8:  # 80% 이상 필요도
                return True
                
        # 중간 필요도도 가끔 요청 (하지만 확률적)
        for need in needs:
            if need.necessity_score > 0.6:  # 60% 이상 필요도
                return random.random() < 0.3  # 30% 확률
                
        return False
    
    def generate_ai_item_request(self, game_state=None) -> Optional[Dict[str, str]]:
        """AI 아이템 요청 생성 (지능적 버전 우선, 폴백으로 랜덤)"""
        # 먼저 지능적 분석 시도
        intelligent_request = self.generate_intelligent_item_request(game_state)
        if intelligent_request:
            return intelligent_request
        
        # 폴백: 기존 랜덤 방식
        return self._generate_random_item_request(game_state)
    
    def _generate_random_item_request(self, game_state=None) -> Optional[Dict[str, str]]:
        """기존 랜덤 아이템 요청 (폴백용)"""
        # 랜덤하게 요청할 AI 선택
        requester_ai = random.choice(list(self.ai_characters.keys()))
        character = self.ai_characters[requester_ai]
        
        # 아이템 타입 선택 (AI 전문성에 따라)
        item_types = ["회복", "무기", "방어구", "마법", "기타"]
        
        # AI 전문성에 따른 가중치
        if "힐링" in character.expertise:
            item_type = random.choice(["회복", "회복", "마법"])
        elif "전투" in character.expertise:
            item_type = random.choice(["무기", "방어구", "무기"])
        elif "분석" in character.expertise:
            item_type = random.choice(["마법", "기타", "마법"])
        else:
            item_type = random.choice(item_types)
        
        # 요청 이유 선택
        reason = random.choice(self.item_request_patterns[item_type])
        
        # 아이템 이름 예시 생성
        item_examples = {
            "회복": ["회복 포션", "생명의 물약", "치유 허브", "회복 스크롤"],
            "무기": ["강화된 검", "마법 지팡이", "날카로운 단검", "강력한 활"],
            "방어구": ["튼튼한 갑옷", "마법 방패", "보호 로브", "방어 부츠"],
            "마법": ["마나 포션", "주문서", "마법 구슬", "정령석"],
            "기타": ["유용한 도구", "탐험 용품", "특수 아이템", "신비한 물건"]
        }
        
        item_name = random.choice(item_examples[item_type])
        
        return {
            "requester_id": requester_ai,
            "requester_name": character.name,
            "item_name": item_name,
            "item_type": item_type,
            "reason": reason,
            "personality_message": f"{character.name}: {reason} {item_name}이(가) 필요해요!"
        }
    
    def should_ai_request_item(self, game_state=None) -> bool:
        """AI 아이템 요청 여부 결정 (지능적 판단 우선)"""
        # 먼저 지능적 판단 시도
        if self.should_ai_request_item_intelligently(game_state):
            return True
            
        # 폴백: 기존 확률 기반 판단
        return self._should_ai_request_item_randomly(game_state)
    
    def _should_ai_request_item_randomly(self, game_state=None) -> bool:
        """기존 확률 기반 아이템 요청 판단 (폴백용)"""
        # 기본 5% 확률
        base_chance = 0.05
        
        # 게임 상황에 따른 확률 조정
        if game_state:
            # 파티 HP가 낮으면 회복 아이템 요청 확률 증가
            if hasattr(game_state, 'party_manager') and game_state.party_manager:
                avg_hp_percent = sum(member.current_hp / member.max_hp 
                                   for member in game_state.party_manager.members 
                                   if member.max_hp > 0) / len(game_state.party_manager.members)
                
                if avg_hp_percent < 0.5:  # 파티 평균 HP 50% 미만
                    base_chance += 0.1
                    
            # 던전 깊은 층수면 아이템 요청 확률 증가
            if hasattr(game_state, 'current_floor') and game_state.current_floor > 10:
                base_chance += 0.05
        
        return random.random() < base_chance
    
    def _record_conversation_pattern(self, user_message: str, ai_response: str, character: AICharacterProfile, game_state=None):
        """AI 학습 시스템에 대화 패턴 기록"""
        if not AI_LEARNING_AVAILABLE:
            return
            
        try:
            # 게임 컨텍스트 분석
            game_context = self.get_game_context(game_state) if game_state else "일반 대화"
            
            learning_data = {
                "timestamp": time.time(),
                "character_name": character.name,
                "character_personality": character.personality.value,
                "user_input": user_message,
                "ai_response": ai_response,
                "game_context": game_context,
                "model_used": self.model_name,
                "response_length": len(ai_response),
                "conversation_turn": len(self.conversation_history)
            }
            
            # 영구 학습 DB에 기록
            if self.learning_db:
                self.learning_db.record_learning_event("conversation_pattern", learning_data)
            
            # 궁극 AI 시스템에 기록
            if self.ultimate_ai:
                self.ultimate_ai.record_successful_interaction(character.name, learning_data)
                
            print(f"📚 AI 학습: {character.name}의 대화 패턴 기록됨")
            
        except Exception as e:
            print(f"⚠️ 대화 패턴 학습 기록 오류: {e}")
    
    def get_learned_response_suggestions(self, user_message: str, character_name: str) -> List[str]:
        """학습된 패턴에서 응답 제안 가져오기"""
        if not AI_LEARNING_AVAILABLE or not self.learning_db:
            return []
            
        try:
            # 유사한 과거 대화 패턴 검색
            similar_patterns = self.learning_db.get_similar_conversations(
                user_message, character_name, limit=3
            )
            
            suggestions = []
            for pattern in similar_patterns:
                if pattern.get('ai_response'):
                    suggestions.append(pattern['ai_response'])
                    
            return suggestions
            
        except Exception as e:
            print(f"⚠️ 학습된 응답 제안 가져오기 오류: {e}")
            return []
    
    def generate_dynamic_ai_character(self, available_jobs: List[str] = None, existing_party_jobs: List[str] = None, use_presets: bool = True) -> AICharacterProfile:
        """동적 AI 캐릭터 생성 (프리셋 활용 + 자동 생성)"""
        
        # 캐릭터 프리셋 시스템 연동 시도
        if use_presets:
            try:
                from .character_presets import CharacterPresets
                presets = CharacterPresets()
                preset_characters = presets.get_all_character_presets()
                
                # 프리셋이 있고 사용 가능한 경우
                if preset_characters:
                    # 파티 구성에 맞는 프리셋 캐릭터 찾기
                    suitable_presets = []
                    for preset_name, preset_data in preset_characters.items():
                        if available_jobs and preset_data.get('character_class') in available_jobs:
                            # 이미 파티에 있는 직업인지 확인
                            if existing_party_jobs and preset_data.get('character_class') not in existing_party_jobs:
                                suitable_presets.append((preset_name, preset_data))
                            elif not existing_party_jobs:
                                suitable_presets.append((preset_name, preset_data))
                    
                    # 적합한 프리셋이 있으면 사용
                    if suitable_presets:
                        preset_name, preset_data = random.choice(suitable_presets)
                        print(f"✨ 프리셋 캐릭터 '{preset_name}' 사용!")
                        
                        # 프리셋 데이터를 AI 캐릭터 프로필로 변환
                        gender = self.gender_analyzer.analyze_gender(preset_data.get('name', 'Unknown'))
                        job_traits = self.job_mapper.get_personality_traits(preset_data.get('character_class', '전사'))
                        
                        return AICharacterProfile(
                            name=preset_data.get('name', 'Unknown'),
                            gender=gender,
                            job_class=preset_data.get('character_class', '전사'),
                            personality_traits=job_traits,
                            expertise=self._get_job_expertise(preset_data.get('character_class', '전사')),
                            catchphrase=f"{preset_data.get('character_class', '전사')}로서 최선을 다하겠습니다!"
                        )
                        
            except ImportError:
                print("📝 캐릭터 프리셋 시스템을 찾을 수 없어 자동 생성합니다.")
            except Exception as e:
                print(f"⚠️ 프리셋 로드 실패, 자동 생성: {e}")
        
        # 프리셋이 없거나 실패한 경우 자동 생성
        print("🎲 새로운 AI 캐릭터를 자동 생성합니다!")
        
        # 성별 랜덤 결정
        gender = random.choice([AIGender.MALE, AIGender.FEMALE])
        
        # 성별에 맞는 이름 생성 (기존 이름 데이터베이스 활용)
        name = self.name_generator.generate_name(gender)
        
        # 파티 구성 균형을 위한 직업 선택
        if available_jobs and existing_party_jobs:
            # 파티에 없는 직업 우선 선택
            missing_roles = self._get_missing_party_roles(existing_party_jobs)
            if missing_roles:
                job_class = random.choice(missing_roles)
            else:
                job_class = random.choice(available_jobs)
        else:
            # 기본 직업 목록에서 선택
            default_jobs = [
                "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크",
                "바드", "네크로맨서", "용기사", "검성", "정령술사", "암살자",
                "기계공학자", "무당", "해적", "사무라이", "드루이드", "철학자",
                "시간술사", "연금술사", "검투사", "기사", "신관", "마검사",
                "차원술사", "광전사"
            ]
            job_class = random.choice(default_jobs)
        
        # 직업별 성격 특성
        personality_traits = self.job_mapper.get_job_personalities(job_class)
        
        # 랜덤 추가 특성 (개성 부여)
        additional_traits = [
            AIPersonalityTrait.FRIENDLY,
            AIPersonalityTrait.HUMOROUS, 
            AIPersonalityTrait.ARTISTIC,
            AIPersonalityTrait.AMBITIOUS,
            AIPersonalityTrait.CAUTIOUS,
            AIPersonalityTrait.OPTIMISTIC
        ]
        personality_traits.extend(random.sample(additional_traits, 2))
        
        # 기본 성격 결정 (첫 번째 특성 기반)
        if AIPersonalityTrait.BRAVE in personality_traits:
            base_personality = AIPersonality.ROBAT_LEADER
        elif AIPersonalityTrait.INTELLECTUAL in personality_traits:
            base_personality = AIPersonality.ALPHA_ANALYST
        elif AIPersonalityTrait.CARING in personality_traits:
            base_personality = AIPersonality.BETA_SUPPORTER
        else:
            base_personality = AIPersonality.GAMMA_EXPLORER
        
        # 직업별 전문성
        job_expertise = {
            '전사': ["전투", "방어", "보호", "근접전"],
            '아크메이지': ["마법", "지식", "분석", "원소술"],
            '궁수': ["원거리", "정확성", "지원", "추적"],
            '도적': ["은신", "함정", "민첩", "암살"],
            '성기사': ["치유", "보호", "신성마법", "정의"],
            '암흑기사': ["흡혈", "저주", "어둠마법", "공포"],
            '몽크': ["무술", "명상", "수행", "내공"],
            '바드': ["음악", "사기", "치유", "영감"],
            '네크로맨서': ["언데드", "생명력", "죽음", "소환"],
            '용기사': ["화염", "용의힘", "용기", "파괴"],
            '검성': ["검술", "검기", "수행", "집중"],
            '정령술사': ["원소", "자연", "균형", "조화"],
            '암살자': ["그림자", "은밀", "치명타", "잠입"],
            '기계공학자': ["기계", "발명", "분석", "효율"],
            '무당': ["영혼", "치유", "예언", "정화"],
            '해적': ["모험", "보물", "자유", "용기"],
            '사무라이': ["명예", "충성", "검술", "절제"],
            '드루이드': ["자연", "변화", "조화", "치유"],
            '철학자': ["지혜", "논리", "진리", "성찰"],
            '시간술사': ["시간", "예측", "조작", "통찰"],
            '연금술사': ["변환", "실험", "화학", "창조"],
            '검투사': ["투기", "생존", "전투", "명성"],
            '기사': ["명예", "보호", "충성", "용기"],
            '신관': ["신앙", "치유", "축복", "정화"],
            '마검사': ["마검", "융합", "균형", "조화"],
            '차원술사': ["차원", "공간", "이동", "탐험"],
            '광전사': ["분노", "파괴", "광기", "힘"]
        }
        
        expertise = job_expertise.get(job_class, ["전투", "협력", "생존"])
        
        return AICharacterProfile(
            name=name,
            personality=base_personality,
            gender=gender,
            personality_traits=personality_traits,
            job_class=job_class,
            speaking_style=self._generate_speaking_style(gender, personality_traits),
            expertise=expertise,
            catchphrase=self._generate_catchphrase(name, job_class, personality_traits),
            response_patterns=self._generate_response_patterns(gender, personality_traits)
        )
    
    def _get_missing_party_roles(self, existing_jobs: List[str]) -> List[str]:
        """파티에서 부족한 역할 분석"""
        role_mapping = {
            "탱커": ["전사", "성기사", "기사", "검투사"],
            "딜러": ["아크메이지", "궁수", "도적", "암살자", "용기사", "검성", "사무라이", "광전사"],
            "힐러": ["성기사", "신관", "무당", "드루이드"],
            "서포터": ["바드", "철학자", "시간술사", "연금술사"]
        }
        
        missing_roles = []
        for role, jobs in role_mapping.items():
            if not any(job in existing_jobs for job in jobs):
                missing_roles.extend(jobs)
        
        return missing_roles if missing_roles else list(role_mapping["딜러"])  # 기본적으로 딜러 반환


# 전역 AI 채팅 시스템
_ai_chat_system = None

def get_ai_chat_system() -> AIChatSystem:
    """AI 채팅 시스템 가져오기"""
    global _ai_chat_system
    if _ai_chat_system is None:
        _ai_chat_system = AIChatSystem()
    return _ai_chat_system

def get_ai_response(user_message: str, game_state=None) -> Optional[str]:
    """AI 응답 가져오기"""
    return get_ai_chat_system().get_ai_response(user_message, game_state)

def get_ai_initiative_message(game_state=None) -> Optional[str]:
    """AI 능동적 메시지 가져오기"""
    return get_ai_chat_system().get_ai_initiative_message(game_state)

def generate_ai_item_request(game_state=None) -> Optional[Dict[str, str]]:
    """AI 아이템 요청 생성"""
    return get_ai_chat_system().generate_ai_item_request(game_state)

def should_ai_request_item(game_state=None) -> bool:
    """AI 아이템 요청 여부 확인"""
    return get_ai_chat_system().should_ai_request_item(game_state)

def generate_dynamic_ai_character(available_jobs: List[str] = None, existing_party_jobs: List[str] = None, use_presets: bool = True):
    """동적 AI 캐릭터 생성 (프리셋 활용 + 자동 생성)"""
    return get_ai_chat_system().generate_dynamic_ai_character(available_jobs, existing_party_jobs, use_presets)
