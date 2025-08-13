#!/usr/bin/env python3
"""
Dawn of Stellar - AI 캐릭터 자동 생성기 (27개 직업 연동)
직업별 특성을 반영한 AI 캐릭터 자동 생성
"""

import random
import json
import sys
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# 한글 입력 지원을 위한 인코딩 설정
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stdin = codecs.getreader('utf-8')(sys.stdin.buffer)

def safe_korean_input(prompt: str = "") -> str:
    """한글 입력을 안전하게 처리하는 함수"""
    try:
        if prompt:
            print(prompt, end="", flush=True)
        
        # 간단한 방법: 여러 번 시도
        for attempt in range(3):
            try:
                result = input().strip()
                if result or attempt == 2:  # 결과가 있거나 마지막 시도
                    return result
                print("다시 입력해주세요: ", end="", flush=True)
            except UnicodeDecodeError:
                print(f"[입력 오류 {attempt+1}/3] 다시 시도: ", end="", flush=True)
                continue
            except Exception as e:
                if attempt == 2:
                    print(f"\n[입력 오류: {e}] 기본값 사용")
                    return ""
        return ""
            
    except Exception as e:
        print(f"\n[입력 시스템 오류: {e}]")
        return ""

# 기존 시스템들 import
try:
    from complete_27_job_system import job_system, JobProfile
    from ai_character_database import AICharacterPresetManager
    from ai_interaction_system import EmotionState, InteractionType
    from ai_cooperation_system import CooperationType
    from ai_tactical_system import TacticalRole
    JOB_SYSTEM_AVAILABLE = True
    print("✅ 직업 시스템 모듈들 import 성공")
except ImportError as e:
    JOB_SYSTEM_AVAILABLE = False
    print(f"⚠️ 일부 모듈을 찾을 수 없습니다: {e}")
    print("기본 모드로 실행합니다.")

@dataclass
class AICharacterTemplate:
    """AI 캐릭터 템플릿"""
    name: str
    job_id: str
    personality_base: List[str]          # 기본 성격
    emotional_tendencies: List[str]      # 감정 성향
    cooperation_style: str              # 협력 스타일
    combat_preferences: List[str]       # 전투 선호도
    dialogue_patterns: List[str]        # 대화 패턴
    story_motivation: str               # 스토리 동기
    relationship_defaults: Dict[str, int] # 기본 관계도

class AI27JobCharacterCreator:
    """27개 직업 기반 AI 캐릭터 자동 생성기"""
    
    def __init__(self):
        if not JOB_SYSTEM_AVAILABLE:
            print("❌ 직업 시스템을 찾을 수 없습니다.")
            return
            
        self.job_system = job_system
        self.character_db = AICharacterPresetManager()
        
        # 이름 풀 (직업별 맞춤형)
        self.name_pools = self._init_name_pools()
        
        # 성격 특성 매핑
        self.personality_mappings = self._init_personality_mappings()
        
        # 감정 성향 매핑
        self.emotion_mappings = self._init_emotion_mappings()
        
        print("🤖 27개 직업 AI 캐릭터 생성기 초기화 완료")
    
    def _init_name_pools(self) -> Dict[str, List[str]]:
        """성별별 캐릭터 이름 풀 초기화 (300개 이상)"""
        return {
            # 남성 이름 (150개)
            "male": [
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
                "사무엘", "그레고리", "알렉산더", "패트릭", "잭", "데니스", "제리", "타일러", "애런","헤인",
                "호세", "헨리", "더글러스", "네이선", "피터", "잭슨", "노아", "이단", "루카스", "메이슨",
                "로건", "제이콥", "윌리엄", "엘리야", "웨인", "칼렙", "라이언", "니콜라스", "조던","플라튼",
                "로버트", "그레이슨", "헌터", "에이든", "카메론", "코너", "산티아고", "칼렙", "네이선",
                "이사이야", "찰리", "이반", "오웬", "루크", "딜런", "잭슨", "가빈", "데이비드", "콜튼",
                "앤드류", "맥스", "라이언", "브레이든", "토머스", "카터", "다니엘", "마이클", "아담",
                "엘라이", "벤자민", "핀", "코딘", "트리스탄", "로넌", "블레이크", "브로디", "데클란",
                "숀", "리암", "루카", "제임슨", "카일", "브랜든", "알렉스", "자이든", "자비에르","테오",
                "도미닉", "데미트리","에이스", "니키타", "블라디미르", "알렉세이", "이반", "안톤", "올렉",
                "세르겐", "빅터", "로만", "파벨", "녹티스", "아르템", "콘스탄틴", "발렌틴", "드미트리","티더","클라우드","프롬프토","그림니르","시스","랜슬롯","벤티","카이","솔","제노","슈르크","네스"
            ],
            
            # 여성 이름 (150개)
            "female": [
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
                "로린", "셸리", "레슬리", "에리카", "카일린", "애나", "코트니", "루비", "이바",
                "메간", "알렉시스", "소피아", "클로에", "이사벨", "에이바", "밀라", "아리아나",
                "라일라", "미아", "엠마", "아드리아나", "알리", "라일리", "캐밀라", "클레어", "빅토리아",
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
                "베가", "안드로메다", "카시오페아", "라이라", "알타이르", "벨라트릭스", "리겔", "시리우스","플레임",
                "프로키온", "아크투루스", "스피카", "알데바란", "카펠라", "폴룩스", "레굴루스", "안타레스", "오즈","코린","엔비","아이린","플루토"
            ]
        }
    
    def _init_personality_mappings(self) -> Dict[str, List[str]]:
        """성격 특성 매핑"""
        return {
            "용감한": ["대담한", "무모한", "결단력있는", "모험적인"],
            "지적인": ["논리적", "분석적", "학구적", "현명한"],
            "신비로운": ["수수께끼같은", "예언적", "직관적", "영적인"],
            "자유로운": ["독립적", "반항적", "창의적", "모험적"],
            "성스러운": ["순수한", "자비로운", "희생적", "신실한"],
            "어둠의": ["신비로운", "복수심있는", "고독한", "냉정한"],
            "평화로운": ["차분한", "명상적", "균형잡힌", "조화로운"],
            "예술적": ["창의적", "감성적", "표현적", "아름다운"],
            "교활한": ["영리한", "기회주의적", "적응적", "생존본능"],
            "명예로운": ["정직한", "충성스러운", "도덕적", "고결한"]
        }
    
    def _init_emotion_mappings(self) -> Dict[str, List[str]]:
        """감정 성향 매핑"""
        return {
            "전투직": ["결정적", "열정적", "도전적", "승부욕"],
            "마법직": ["신중한", "집중적", "탐구적", "신비적"],
            "특수직": ["독특한", "창의적", "자유로운", "특별한"]
        }
    
    def _detect_gender_from_name(self, name: str) -> str:
        """이름으로부터 성별 감지"""
        if name in self.name_pools["male"]:
            return "male"
        elif name in self.name_pools["female"]:
            return "female"
        else:
            # 알 수 없는 이름이면 랜덤하게
            return random.choice(["male", "female"])
    
    def _generate_name_by_gender(self, preferred_gender: str = None) -> tuple[str, str]:
        """성별별 이름 생성"""
        if preferred_gender and preferred_gender in self.name_pools:
            gender = preferred_gender
        else:
            gender = random.choice(["male", "female"])
        
        name = random.choice(self.name_pools[gender])
        return name, gender
    
    def create_character_from_job(self, job_id: str, custom_name: str = None) -> Dict[str, Any]:
        """직업 기반 AI 캐릭터 생성"""
        if not JOB_SYSTEM_AVAILABLE:
            return {}
            
        job_profile = self.job_system.get_job_profile(job_id)
        if not job_profile:
            print(f"❌ 직업 '{job_id}'를 찾을 수 없습니다.")
            return {}
        
        # 이름과 성별 생성
        if custom_name:
            name = custom_name
            gender = self._detect_gender_from_name(name)
        else:
            name, gender = self._generate_name_by_gender()
        
        # 성격 생성
        personality = self._generate_personality(job_profile)
        
        # 감정 성향 생성
        emotions = self._generate_emotional_tendencies(job_profile)
        
        # 협력 스타일 생성
        cooperation_style = self._generate_cooperation_style(job_profile)
        
        # 전투 선호도 생성
        combat_prefs = self._generate_combat_preferences(job_profile)
        
        # 대화 패턴 생성
        dialogue_patterns = self._generate_dialogue_patterns(job_profile)
        
        # 자기소개 대사 생성
        introduction_dialogue = self._generate_introduction_dialogue(name, gender, job_profile, "플레이어")
        
        # 스토리 동기 생성
        story_motivation = self._generate_story_motivation(job_profile)
        
        # 관계도 기본값 생성
        relationships = self._generate_default_relationships(job_profile)
        
        # AI 캐릭터 데이터 구성
        character_data = {
            "name": name,
            "gender": gender,
            "job_id": job_id,
            "job_name": job_profile.name,
            "personality": {
                "base_traits": personality,
                "emotional_tendencies": emotions,
                "cooperation_style": cooperation_style
            },
            "combat": {
                "tactical_role": job_profile.tactical_role.value,
                "combat_style": job_profile.combat_style,
                "preferences": combat_prefs,
                "signature_skills": job_profile.signature_skills
            },
            "social": {
                "dialogue_patterns": dialogue_patterns,
                "introduction_dialogue": introduction_dialogue,
                "cooperation_preference": job_profile.cooperation_preference,
                "default_relationships": relationships
            },
            "story": {
                "background": job_profile.story_background,
                "motivation": story_motivation,
                "category": job_profile.category
            },
            "stats": {
                "primary_stats": job_profile.primary_stats,
                "secondary_stats": job_profile.secondary_stats
            }
        }
        
        print(f"✅ '{name}' ({job_profile.name}) 캐릭터 생성 완료")
        return character_data
    
    def _generate_personality(self, job_profile: JobProfile) -> List[str]:
        """성격 생성"""
        personality = []
        
        # 직업 기본 특성에서 선택
        for trait in job_profile.ai_personality_traits:
            if trait in self.personality_mappings:
                extra_traits = random.sample(self.personality_mappings[trait], 2)
                personality.extend(extra_traits)
            personality.append(trait)
        
        # 중복 제거 및 최대 5개로 제한
        unique_personality = list(set(personality))
        return unique_personality[:5]
    
    def _generate_emotional_tendencies(self, job_profile: JobProfile) -> List[str]:
        """감정 성향 생성"""
        emotions = []
        
        # 직업 카테고리 기반
        if "전투" in job_profile.category:
            emotions.extend(random.sample(self.emotion_mappings["전투직"], 2))
        elif "마법" in job_profile.category:
            emotions.extend(random.sample(self.emotion_mappings["마법직"], 2))
        else:
            emotions.extend(random.sample(self.emotion_mappings["특수직"], 2))
        
        # 역할 기반 추가
        role_emotions = {
            TacticalRole.TANK: ["보호적", "책임감"],
            TacticalRole.DPS: ["공격적", "경쟁적"],
            TacticalRole.HEALER: ["돌봄", "평화적"],
            TacticalRole.SUPPORT: ["협력적", "배려적"],
            TacticalRole.CONTROLLER: ["전략적", "통제적"],
            TacticalRole.SCOUT: ["경계심", "탐구적"]
        }
        
        if job_profile.tactical_role in role_emotions:
            emotions.extend(role_emotions[job_profile.tactical_role])
        
        return emotions[:4]
    
    def _detect_gender_from_name(self, name: str) -> str:
        """이름으로부터 성별 감지"""
        if name in self.name_pools["male"]:
            return "male"
        elif name in self.name_pools["female"]:
            return "female"
        else:
            # 이름이 풀에 없는 경우 랜덤 선택
            return random.choice(["male", "female"])
    
    def _generate_name_by_gender(self, gender: str = None) -> tuple:
        """성별에 따른 이름 생성"""
        if gender is None:
            gender = random.choice(["male", "female"])
        
        if gender in self.name_pools:
            name = random.choice(self.name_pools[gender])
        else:
            # 기본값으로 모든 이름에서 선택
            all_names = self.name_pools["male"] + self.name_pools["female"]
            name = random.choice(all_names)
            gender = self._detect_gender_from_name(name)
        
        return name, gender
    
    def _generate_cooperation_style(self, job_profile: JobProfile) -> str:
        """협력 스타일 생성"""
        styles = {
            TacticalRole.TANK: "선도형",
            TacticalRole.DPS: "공격형", 
            TacticalRole.HEALER: "지원형",
            TacticalRole.SUPPORT: "조화형",
            TacticalRole.CONTROLLER: "전략형",
            TacticalRole.SCOUT: "정보형"
        }
        return styles.get(job_profile.tactical_role, "균형형")
    
    def _generate_combat_preferences(self, job_profile: JobProfile) -> List[str]:
        """전투 선호도 생성"""
        prefs = []
        
        # 전투 스타일 기반
        style = job_profile.combat_style
        if "근접" in style:
            prefs.extend(["근거리_전투", "직접_공격"])
        elif "원거리" in style:
            prefs.extend(["원거리_전투", "안전_거리"])
        
        # 특수 스타일 추가
        if "방어" in style:
            prefs.append("방어_우선")
        elif "공격" in style:
            prefs.append("공격_우선")
        elif "지원" in style:
            prefs.append("팀플레이")
        elif "치유" in style:
            prefs.append("회복_우선")
        
        return prefs[:3]
    
    def _generate_dialogue_patterns(self, job_profile: JobProfile) -> List[str]:
        """대화 패턴 생성"""
        patterns = []
        
        # 성격 기반 대화 패턴
        trait_patterns = {
            "용감한": ["당당한_어조", "직설적_표현"],
            "지적인": ["논리적_설명", "학술적_용어"],
            "신비로운": ["은유적_표현", "암시적_언어"],
            "자유로운": ["활동적_어조", "창의적_표현"],
            "성스러운": ["정중한_어조", "축복_표현"],
            "평화로운": ["차분한_어조", "명상적_표현"]
        }
        
        for trait in job_profile.ai_personality_traits:
            if trait in trait_patterns:
                patterns.extend(trait_patterns[trait])
        
        # 직업별 고유 패턴 추가
        job_patterns = {
            "warrior": ["전투_용어", "명령형_어조"],
            "archmage": ["마법_용어", "학술적_설명"],
            "priest": ["종교적_표현", "축복_언어"],
            "philosopher": ["철학적_질문", "깊은_사고"]
        }
        
        if job_profile.job_id in job_patterns:
            patterns.extend(job_patterns[job_profile.job_id])
        
        return patterns[:4]
    
    def _generate_introduction_dialogue(self, name: str, gender: str, job_profile: JobProfile, player_name: str = "핀") -> str:
        """성별과 직업에 따른 자기소개 대사 생성"""
        
        # 성별별 기본 어투
        male_endings = ["다", "네", "지", "요"]
        female_endings = ["요", "어요", "에요", "네요"]
        
        # 직업별 특성을 반영한 대사 템플릿
        job_templates = {
            # 전투 직업군
            "warrior": {
                "male": [
                    f"{player_name}아, 강철 같은 의지로 이곳에 서준 것이 고맙다. 함께 싸워나가자.",
                    f"{player_name}, 전장에서 너와 함께할 수 있어 든든하다.",
                    f"용감한 {player_name}이군. 우리의 검이 정의를 관철할 것이다."
                ],
                "female": [
                    f"{player_name}, 당신과 함께라면 어떤 시련도 이겨낼 수 있을 것 같아요.",
                    f"안녕하세요, {player_name}. 저도 전투에서 도움이 되도록 하겠어요.",
                    f"{player_name}님, 함께 승리를 쟁취해보아요!"
                ]
            },
            "knight": {
                "male": [
                    f"{player_name}아, 강철 같은 의지로 이곳에 서준 것이 고맙다. 함께 정의를 지켜나가자.",
                    f"기사 {name}이다. {player_name}, 너의 용기를 보니 마음이 든든하구나.",
                    f"{player_name}, 함께 명예로운 길을 걸어가자."
                ],
                "female": [
                    f"기사 {name}입니다. {player_name}님, 함께 정의를 실현해나가요.",
                    f"{player_name}님, 당신의 용기에 감명받았어요. 함께 싸우겠습니다.",
                    f"안녕하세요 {player_name}. 저와 함께 악을 물리쳐요!"
                ]
            },
            "assassin": {
                "male": [
                    f"{player_name}, 죽음의 길을 함께 걸어갈 동료구나. 기대되네.",
                    f"그림자 속에서 {player_name}을 지켜보고 있었다. 흥미로운 녀석이군.",
                    f"{player_name}... 너도 어둠의 길을 아는 자인가?"
                ],
                "female": [
                    f"{player_name}, 당신도 그림자의 길을 걷는 분이군요. 함께해요.",
                    f"안녕하세요 {player_name}. 저는 조용히 뒤에서 지원하겠어요.",
                    f"{player_name}님, 제 기술이 도움이 될 거예요."
                ]
            },
            "monk": {
                "male": [
                    f"{player_name}이라니... 흥미로운 이름이구나. 싸우는 법 좀 배웠나?",
                    f"수행자 {name}이다. {player_name}, 너의 정신력을 시험해보고 싶군.",
                    f"{player_name}, 내면의 힘을 키우는 것이 중요하다네."
                ],
                "female": [
                    f"안녕하세요 {player_name}. 저는 평화로운 해결을 선호해요.",
                    f"{player_name}님, 함께 수행의 길을 걸어가요.",
                    f"명상과 무술, 둘 다 중요하답니다. {player_name}님도 그렇게 생각하시나요?"
                ]
            },
            "archmage": {
                "male": [
                    f"마법사 {name}이다. {player_name}, 마법의 신비를 함께 탐구해보지 않겠나?",
                    f"{player_name}, 너에게서 특별한 마력을 느낀다.",
                    f"흥미롭군, {player_name}. 함께라면 더 강력한 마법을 쓸 수 있을 것 같다."
                ],
                "female": [
                    f"안녕하세요 {player_name}. 마법으로 도움을 드릴게요.",
                    f"{player_name}님, 함께 마법의 세계를 탐험해보아요.",
                    f"저의 마법이 {player_name}님께 도움이 되길 바라요."
                ]
            }
        }
        
        # 기본 템플릿 (직업별 템플릿이 없는 경우)
        default_templates = {
            "male": [
                f"{player_name}, 함께 모험을 떠나자.",
                f"만나서 반갑다, {player_name}. 잘 부탁한다.",
                f"{player_name}이군. 흥미로운 여행이 될 것 같다."
            ],
            "female": [
                f"안녕하세요 {player_name}. 잘 부탁드려요.",
                f"{player_name}님, 함께 모험을 떠나요!",
                f"만나서 반가워요, {player_name}님."
            ]
        }
        
        # 직업에 맞는 템플릿 선택
        if job_profile.job_id in job_templates:
            templates = job_templates[job_profile.job_id][gender]
        else:
            templates = default_templates[gender]
        
        return random.choice(templates)
    
    def _generate_story_motivation(self, job_profile: JobProfile) -> str:
        """스토리 동기 생성"""
        motivations = {
            "전투직업군": "시공교란 속에서 질서를 회복하고자 한다",
            "마법직업군": "시공교란의 원인을 마법적으로 해결하려 한다", 
            "특수직업군": "시공교란을 자신만의 방식으로 극복하려 한다"
        }
        
        base_motivation = motivations.get(job_profile.category, "시공교란의 혼돈을 수습하려 한다")
        
        # 직업별 특수 동기 추가
        if "시간" in job_profile.name:
            return "시공교란의 근본 원인을 찾아 시간 흐름을 복원하려 한다"
        elif "차원" in job_profile.name:
            return "차원 균열을 봉인하여 현실을 안정시키려 한다"
        elif "성기사" in job_profile.name or "신관" in job_profile.name:
            return "신의 뜻에 따라 시공교란을 정화하려 한다"
        
        return base_motivation
    
    def _generate_default_relationships(self, job_profile: JobProfile) -> Dict[str, int]:
        """기본 관계도 생성"""
        relationships = {}
        
        # 협력 선호 직업들과는 +관계
        for partner in job_profile.cooperation_preference:
            relationships[partner] = random.randint(60, 80)
        
        # 같은 역할 직업들과는 중립~우호
        same_role_jobs = self.job_system.get_jobs_by_role(job_profile.tactical_role)
        for job in same_role_jobs:
            if job.name != job_profile.name:
                relationships[job.name] = random.randint(40, 60)
        
        # 대립 관계 설정 (일부)
        opposites = {
            "성기사": ["암흑기사", "네크로맨서"],
            "암흑기사": ["성기사", "신관"],
            "네크로맨서": ["성기사", "신관"],
            "드루이드": ["기계공학자", "연금술사"],
            "철학자": ["광전사", "해적"]
        }
        
        if job_profile.name in opposites:
            for opponent in opposites[job_profile.name]:
                relationships[opponent] = random.randint(20, 40)
        
        return relationships
    
    def create_full_party_set(self, party_size: int = 4) -> List[Dict[str, Any]]:
        """균형잡힌 파티 구성 생성"""
        if not JOB_SYSTEM_AVAILABLE:
            return []
        
        party_jobs = []
        
        # 역할별 최소 1명씩 보장
        essential_roles = [TacticalRole.TANK, TacticalRole.DPS, TacticalRole.HEALER, TacticalRole.SUPPORT]
        
        for role in essential_roles[:party_size]:
            role_jobs = self.job_system.get_jobs_by_role(role)
            if role_jobs:
                selected_job = random.choice(role_jobs)
                party_jobs.append(selected_job.job_id)
        
        # 나머지 자리는 랜덤 충원
        while len(party_jobs) < party_size:
            all_jobs = list(self.job_system.jobs.keys())
            remaining_jobs = [job for job in all_jobs if job not in party_jobs]
            if remaining_jobs:
                party_jobs.append(random.choice(remaining_jobs))
            else:
                break
        
        # 각 직업에 대해 캐릭터 생성
        party_characters = []
        for job_id in party_jobs:
            character = self.create_character_from_job(job_id)
            if character:
                party_characters.append(character)
        
        print(f"✅ {len(party_characters)}명 파티 생성 완료")
        return party_characters
    
    def save_character_to_database(self, character_data: Dict[str, Any]) -> bool:
        """캐릭터를 데이터베이스에 저장"""
        try:
            # AI 캐릭터 데이터베이스 형식으로 변환
            db_format = {
                "name": character_data["name"],
                "personality": character_data["personality"]["base_traits"],
                "background": character_data["story"]["background"],
                "relationships": character_data["social"]["default_relationships"],
                "conversation_history": [],
                "learning_data": {
                    "job_info": {
                        "job_id": character_data["job_id"],
                        "job_name": character_data["job_name"],
                        "tactical_role": character_data["combat"]["tactical_role"]
                    }
                }
            }
            
            # 데이터베이스에 저장
            self.character_db.add_character(
                character_data["name"],
                db_format["personality"],
                db_format["background"],
                db_format["relationships"]
            )
            
            print(f"💾 '{character_data['name']}' 데이터베이스 저장 완료")
            return True
            
        except Exception as e:
            print(f"❌ 데이터베이스 저장 실패: {e}")
            return False
    
    def batch_create_all_jobs(self) -> List[Dict[str, Any]]:
        """모든 27개 직업의 대표 캐릭터 생성"""
        if not JOB_SYSTEM_AVAILABLE:
            return []
        
        all_characters = []
        
        print("🚀 모든 직업의 대표 캐릭터 생성 시작...")
        
        for job_id in self.job_system.jobs.keys():
            try:
                character = self.create_character_from_job(job_id)
                if character:
                    all_characters.append(character)
                    # 데이터베이스에도 저장
                    self.save_character_to_database(character)
            except Exception as e:
                print(f"❌ '{job_id}' 캐릭터 생성 실패: {e}")
        
        print(f"✅ 총 {len(all_characters)}개 캐릭터 생성 완료")
        return all_characters
    
    def export_characters_to_json(self, characters: List[Dict[str, Any]], filename: str = "ai_characters_27jobs.json"):
        """캐릭터들을 JSON으로 내보내기"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(characters, f, ensure_ascii=False, indent=2)
            print(f"📁 '{filename}'로 캐릭터 데이터 내보내기 완료")
        except Exception as e:
            print(f"❌ JSON 내보내기 실패: {e}")
    
    def show_creator_menu(self):
        """캐릭터 생성기 메뉴 (커서 기반)"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            while True:
                options = [
                    "개별 직업 캐릭터 생성",
                    "균형잡힌 파티 생성", 
                    "모든 직업 대표 캐릭터 생성",
                    "생성된 캐릭터 목록 보기",
                    "JSON으로 내보내기"
                ]
                
                descriptions = [
                    "원하는 직업을 선택해서 캐릭터를 개별 생성합니다",
                    "탱커, 딜러, 힐러, 서포터가 균형잡힌 4인 파티를 생성합니다",
                    "27개 직업 모두의 대표 캐릭터를 한 번에 생성합니다",
                    "현재까지 생성된 모든 캐릭터의 목록을 확인합니다",
                    "생성된 캐릭터 데이터를 JSON 파일로 내보냅니다"
                ]
                
                # 현재 생성된 캐릭터 수 표시
                all_chars = self.character_db.get_all_characters()
                extra_content = f"현재 등록된 캐릭터: {len(all_chars)}명"
                
                cursor_menu = CursorMenu(
                    title="🤖 AI 캐릭터 자동 생성기 (27개 직업)",
                    extra_content=extra_content,
                    options=options,
                    descriptions=descriptions,
                    cancellable=True
                )
                
                result = cursor_menu.run()
                
                if result is None or result == -1:
                    break
                
                if result == 0:
                    self._menu_create_individual()
                elif result == 1:
                    self._menu_create_party()
                elif result == 2:
                    self._menu_create_all_jobs()
                elif result == 3:
                    self._menu_show_characters()
                elif result == 4:
                    self._menu_export_json()
                    
                input("\nEnter를 눌러 계속...")
                    
        except ImportError:
            # 폴백: 기본 메뉴 시스템
            self._show_creator_menu_fallback()
        except Exception as e:
            print(f"❌ 메뉴 처리 오류: {e}")
            input("\nEnter를 눌러 계속...")
    
    def _show_creator_menu_fallback(self):
        """폴백: 기본 메뉴 시스템"""
        while True:
            print("\n🤖 AI 캐릭터 자동 생성기 (27개 직업)")
            print("=" * 50)
            print("1. 개별 직업 캐릭터 생성")
            print("2. 균형잡힌 파티 생성")
            print("3. 모든 직업 대표 캐릭터 생성")
            print("4. 생성된 캐릭터 목록 보기")
            print("5. JSON으로 내보내기")
            print("0. 돌아가기")
            
            try:
                choice = input("\n선택하세요: ").strip()
                
                if choice == "1":
                    self._menu_create_individual()
                elif choice == "2":
                    self._menu_create_party()
                elif choice == "3":
                    self._menu_create_all_jobs()
                elif choice == "4":
                    self._menu_show_characters()
                elif choice == "5":
                    self._menu_export_json()
                elif choice == "0":
                    break
                else:
                    print("❌ 잘못된 선택입니다.")
                    
            except Exception as e:
                print(f"❌ 메뉴 처리 오류: {e}")
            
            input("\nEnter를 눌러 계속...")
    
    def _menu_create_individual(self):
        """개별 캐릭터 생성 메뉴 (커서 기반)"""
        if not JOB_SYSTEM_AVAILABLE:
            print("❌ 직업 시스템을 사용할 수 없습니다.")
            return
        
        try:
            from game.cursor_menu_system import CursorMenu
            
            # 27개 직업을 카테고리별로 정리
            job_list = list(self.job_system.jobs.keys())
            job_options = []
            job_descriptions = []
            
            for job_id in job_list:
                job_profile = self.job_system.get_job_profile(job_id)
                job_options.append(f"{job_profile.name} ({job_profile.category})")
                
                # 직업 설명 생성
                role_name = job_profile.tactical_role.value if hasattr(job_profile.tactical_role, 'value') else str(job_profile.tactical_role)
                desc = f"{role_name} | 스킬: {', '.join(job_profile.signature_skills[:2])}"
                job_descriptions.append(desc)
            
            cursor_menu = CursorMenu(
                title="📋 직업 선택 (27개 직업)",
                extra_content="원하는 직업을 선택하여 캐릭터를 생성합니다",
                options=job_options,
                descriptions=job_descriptions,
                cancellable=True
            )
            
            result = cursor_menu.run()
            
            if result is not None and result != -1:
                job_id = job_list[result]
                
                # 이름 입력
                custom_name = safe_korean_input("\n사용자 정의 이름 (Enter=자동생성): ")
                if not custom_name:
                    custom_name = None
                
                character = self.create_character_from_job(job_id, custom_name)
                if character:
                    self.save_character_to_database(character)
                    print(f"\n🎉 '{character['name']}' 캐릭터 생성 및 저장 완료!")
                    
                    # 생성된 캐릭터 정보 표시
                    print(f"   직업: {character.get('job_name', job_id)}")
                    print(f"   성격: {', '.join(character.get('personality_traits', [])[:3])}")
                    print(f"   전투 스타일: {character.get('combat_style', '일반')}")
                    
        except ImportError:
            # 폴백: 기본 메뉴
            self._menu_create_individual_fallback()
        except Exception as e:
            print(f"❌ 캐릭터 생성 오류: {e}")
    
    def _menu_create_individual_fallback(self):
        """폴백: 기본 개별 생성 메뉴"""
        print("\n📋 사용 가능한 직업:")
        job_list = list(self.job_system.jobs.keys())
        for i, job_id in enumerate(job_list[:10], 1):  # 처음 10개만 표시
            job_profile = self.job_system.get_job_profile(job_id)
            print(f"{i}. {job_profile.name} ({job_id})")
        
        try:
            choice = int(safe_korean_input("직업 선택 (1-10): ")) - 1
            if 0 <= choice < len(job_list):
                job_id = job_list[choice]
                custom_name = safe_korean_input("사용자 정의 이름 (Enter=자동생성): ")
                if not custom_name:
                    custom_name = None
                
                character = self.create_character_from_job(job_id, custom_name)
                if character:
                    self.save_character_to_database(character)
                    print(f"\n🎉 '{character['name']}' 캐릭터 생성 및 저장 완료!")
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _menu_create_party(self):
        """파티 생성 메뉴"""
        try:
            party_size = int(safe_korean_input("파티 크기 (2-6): "))
            if 2 <= party_size <= 6:
                party = self.create_full_party_set(party_size)
                for character in party:
                    self.save_character_to_database(character)
                print(f"\n🎉 {party_size}명 파티 생성 완료!")
            else:
                print("❌ 파티 크기는 2-6명이어야 합니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _menu_create_all_jobs(self):
        """모든 직업 생성 메뉴"""
        confirm = safe_korean_input("모든 27개 직업의 캐릭터를 생성하시겠습니까? (y/N): ").lower()
        if confirm == 'y':
            characters = self.batch_create_all_jobs()
            print(f"\n🎉 {len(characters)}개 캐릭터 일괄 생성 완료!")
        else:
            print("❌ 취소되었습니다.")
    
    def _menu_show_characters(self):
        """캐릭터 목록 보기"""
        try:
            characters = self.character_db.get_all_characters()
            if characters:
                print(f"\n👥 저장된 캐릭터 ({len(characters)}명):")
                for name, data in characters.items():
                    job_info = data.get('learning_data', {}).get('job_info', {})
                    job_name = job_info.get('job_name', '알 수 없음')
                    role = job_info.get('tactical_role', '알 수 없음')
                    print(f"   • {name} ({job_name} - {role})")
            else:
                print("📭 저장된 캐릭터가 없습니다.")
        except Exception as e:
            print(f"❌ 캐릭터 목록 조회 실패: {e}")
    
    def _menu_export_json(self):
        """JSON 내보내기 메뉴"""
        try:
            characters = self.character_db.get_all_characters()
            if characters:
                filename = safe_korean_input("파일명 (기본: ai_characters_export.json): ").strip()
                if not filename:
                    filename = "ai_characters_export.json"
                
                # 리스트 형태로 변환
                character_list = []
                for name, data in characters.items():
                    character_list.append({"name": name, **data})
                
                self.export_characters_to_json(character_list, filename)
                print(f"✅ {filename}으로 내보내기 완료!")
            else:
                print("📭 내보낼 캐릭터가 없습니다.")
        except Exception as e:
            print(f"❌ 내보내기 실패: {e}")

# 전역 인스턴스
character_creator = AI27JobCharacterCreator()

def test_character_creator():
    """캐릭터 생성기 테스트"""
    if not JOB_SYSTEM_AVAILABLE:
        print("❌ 테스트를 위한 시스템이 준비되지 않았습니다.")
        return
    
    print("🧪 AI 캐릭터 생성기 테스트")
    
    # 개별 캐릭터 생성 테스트
    warrior_char = character_creator.create_character_from_job("warrior", "테스트전사")
    print(f"테스트 결과: {warrior_char['name'] if warrior_char else 'None'}")
    
    # 파티 생성 테스트
    party = character_creator.create_full_party_set(3)
    print(f"파티 생성 결과: {len(party)}명")
    
    print("✅ 캐릭터 생성기 테스트 완료")

if __name__ == "__main__":
    test_character_creator()
