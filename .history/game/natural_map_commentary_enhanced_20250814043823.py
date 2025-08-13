"""
자연스러운 맵 코멘터리 시스템
직업별, 성격별, 성별별 개성 있는 AI 대화
언어모델 기반 응답 생성 시스템

2025년 8월 11일 - 완전 리뉴얼
"""

import random
import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

class CommentaryType(Enum):
    """코멘터리 타입"""
    ENVIRONMENT = "환경"
    DANGER = "위험"
    OPPORTUNITY = "기회"
    TACTICAL = "전술"
    CASUAL = "일상"

@dataclass
class CharacterContext:
    """캐릭터 맥락 정보 (기존 시스템과 연동)"""
    name: str
    job_class: str
    gender: str  # "male", "female"
    personality: str  # "cheerful", "serious", "gentle", "cold", "playful", "mysterious", "hot_tempered", "wise", "balanced"
    
    # AI 시스템과 연동할 특성들
    personality_traits: List[str] = None
    speaking_style: str = ""
    expertise: List[str] = None
    
    def __post_init__(self):
        """CharacterTraits와 AICharacterProfile 시스템과 호환성 유지"""
        if self.personality_traits is None:
            self.personality_traits = self._get_job_personality_traits()
        if not self.speaking_style:
            self.speaking_style = self._get_speaking_style()
        if self.expertise is None:
            self.expertise = self._get_job_expertise()
    
    def _get_job_personality_traits(self) -> List[str]:
        """직업별 성격 특성 (기존 시스템과 연동)"""
        job_traits = {
            '전사': ['brave', 'protective', 'confident'],
            '아크메이지': ['intellectual', 'serious', 'mysterious'],
            '궁수': ['cautious', 'calm', 'intuitive'],
            '도적': ['playful', 'rebellious', 'shy'],
            '성기사': ['loyal', 'caring', 'formal'],
            '암흑기사': ['mysterious', 'serious', 'ambitious'],
            '몽크': ['calm', 'serious', 'friendly'],
            '바드': ['cheerful', 'artistic', 'humorous'],
            '네크로맨서': ['mysterious', 'intellectual', 'serious'],
            '용기사': ['brave', 'aggressive', 'confident'],
            '검성': ['serious', 'loyal', 'intellectual'],
            '정령술사': ['calm', 'intuitive', 'caring'],
            '시간술사': ['intellectual', 'mysterious', 'cautious'],
            '연금술사': ['intellectual', 'curious', 'serious'],
            '차원술사': ['mysterious', 'ambitious', 'intellectual'],
            '마검사': ['confident', 'brave', 'serious'],
            '기계공학자': ['intellectual', 'cautious', 'friendly'],
            '무당': ['mysterious', 'intuitive', 'caring'],
            '암살자': ['mysterious', 'cautious', 'shy'],
            '해적': ['rebellious', 'cheerful', 'aggressive'],
            '사무라이': ['loyal', 'serious', 'formal'],
            '드루이드': ['calm', 'caring', 'intuitive'],
            '철학자': ['intellectual', 'serious', 'formal'],
            '검투사': ['confident', 'aggressive', 'brave'],
            '기사': ['loyal', 'formal', 'protective'],
            '신관': ['caring', 'formal', 'calm'],
            '광전사': ['aggressive', 'energetic', 'brave']
        }
        return job_traits.get(self.job_class, ['friendly', 'calm'])
    
    def _get_speaking_style(self) -> str:
        """성별과 성격에 따른 말투"""
        gender_styles = {
            "male": {
                "cheerful": "밝고 활기찬 말투",
                "serious": "진지하고 단호한 말투", 
                "gentle": "부드럽고 예의바른 말투",
                "cold": "차갑고 간결한 말투",
                "playful": "장난스럽고 자유로운 말투",
                "mysterious": "신비롭고 철학적인 말투",
                "hot_tempered": "열정적이고 직설적인 말투",
                "wise": "지혜롭고 침착한 말투",
                "balanced": "균형 잡힌 중성적 말투"
            },
            "female": {
                "cheerful": "명랑하고 사랑스러운 말투",
                "serious": "똑똑하고 당당한 말투",
                "gentle": "상냥하고 따뜻한 말투", 
                "cold": "시크하고 도도한 말투",
                "playful": "발랄하고 귀여운 말투",
                "mysterious": "신비롭고 우아한 말투",
                "hot_tempered": "당차고 솔직한 말투",
                "wise": "현명하고 포근한 말투",
                "balanced": "자연스럽고 친근한 말투"
            }
        }
        return gender_styles.get(self.gender, {}).get(self.personality, "자연스러운 말투")
    
    def _get_job_expertise(self) -> List[str]:
        """직업별 전문 분야"""
        job_expertise = {
            '전사': ['전투', '방어', '근접무기'],
            '아크메이지': ['마법', '정령', '학문'],
            '궁수': ['원거리공격', '정찰', '야생생존'],
            '도적': ['은신', '함정해제', '정보수집'],
            '성기사': ['신성마법', '치유', '정의'],
            '암흑기사': ['어둠마법', '저주', '금기술'],
            '몽크': ['무술', '명상', '기운조절'],
            '바드': ['음악', '사기진작', '정보'],
            '네크로맨서': ['언데드', '생명력조작', '금기지식'],
            '용기사': ['드래곤', '화염', '비행전투'],
            '검성': ['검술', '검기', '무도'],
            '정령술사': ['정령소환', '자연마법', '원소조작'],
            '시간술사': ['시간조작', '예언', '운명'],
            '연금술사': ['연금술', '포션제작', '변환술'],
            '차원술사': ['차원이동', '공간조작', '차원간여행'],
            '마검사': ['마법검술', '마검', '이중능력'],
            '기계공학자': ['기계조작', '발명', '기술'],
            '무당': ['영혼술', '점술', '의식'],
            '암살자': ['암살술', '독', '그림자술'],
            '해적': ['항해', '보물찾기', '자유'],
            '사무라이': ['무사도', '검술', '명예'],
            '드루이드': ['자연친화', '변신술', '자연보호'],
            '철학자': ['지식탐구', '논리', '진리'],
            '검투사': ['투기', '관중몰이', '생존'],
            '기사': ['기사도', '창술', '충성'],
            '신관': ['신성마법', '축복', '치유'],
            '광전사': ['광폭화', '파괴', '원시력']
        }
        return job_expertise.get(self.job_class, ['일반전투'])

class AIEnhancedCommentary:
    """AI 언어모델 기반 강화된 코멘터리 시스템"""
    
    def __init__(self):
        # 간단하지만 강력한 프롬프트 시스템
        self.personality_prompts = self._build_personality_prompts()
        self.situation_contexts = self._build_situation_contexts()
        
    def _build_personality_prompts(self) -> Dict[str, str]:
        """성격별 기본 프롬프트 (언어모델용)"""
        return {
            "cheerful": "밝고 긍정적이며 활기찬 성격. 어떤 상황에서도 희망적으로 말함. 감탄사를 자주 사용.",
            "serious": "진지하고 냉정하며 논리적인 성격. 간결하고 명확하게 말함. 전문용어 사용.",
            "gentle": "부드럽고 따뜻하며 배려심 많은 성격. 상대방을 걱정하는 말투. 정중한 존댓말.",
            "cold": "차갑고 무뚝뚝하며 간결한 성격. 필요한 말만 함. 감정표현을 최소화.",
            "playful": "장난스럽고 자유분방하며 재미있는 성격. 농담과 말장난을 좋아함. 캐주얼한 말투.",
            "mysterious": "신비롭고 철학적이며 깊이 있는 성격. 추상적이고 의미심장한 표현 사용.",
            "hot_tempered": "열정적이고 직설적이며 감정적인 성격. 강한 어조와 감탄사 사용.",
            "wise": "지혜롭고 침착하며 통찰력 있는 성격. 교훈적이고 현명한 조언을 제공.",
            "balanced": "균형 잡히고 중성적이며 합리적인 성격. 객관적이고 공정한 판단."
        }
    
    def _build_situation_contexts(self) -> Dict[str, str]:
        """상황별 맥락 정보"""
        return {
            "environment": "주변 환경을 관찰하고 설명하는 상황",
            "danger": "위험을 감지하고 경고하는 상황", 
            "opportunity": "기회나 보물을 발견한 상황",
            "tactical": "전투나 전략에 대해 조언하는 상황",
            "casual": "일상적인 대화나 잡담하는 상황"
        }
    
    def generate_enhanced_response(self, character: CharacterContext, commentary_type: CommentaryType, 
                                   scan_data: Dict[str, Any], ollama_client=None) -> str:
        """언어모델 기반 강화된 응답 생성"""
        
        # 1단계: 기본 컨텍스트 구성
        context = self._build_character_context(character, commentary_type, scan_data)
        
        # 2단계: 언어모델 사용 (가능한 경우)
        if ollama_client:
            try:
                enhanced_response = self._generate_ai_response(context, ollama_client)
                if enhanced_response and len(enhanced_response) > 10:
                    return enhanced_response
            except Exception as e:
                print(f"⚠️ AI 응답 생성 실패: {e}")
        
        # 3단계: 폴백 - 패턴 기반 응답
        return self._generate_pattern_response(character, commentary_type, scan_data)
    
    def _build_character_context(self, character: CharacterContext, commentary_type: CommentaryType, 
                                 scan_data: Dict[str, Any]) -> str:
        """캐릭터 맥락 기반 프롬프트 구성"""
        
        # 성격과 직업 특성
        personality_desc = self.personality_prompts.get(character.personality, "일반적인 성격")
        situation_desc = self.situation_contexts.get(commentary_type.value, "일반적인 상황")
        
        # 스캔 데이터 요약
        scan_summary = self._summarize_scan_data(scan_data)
        
        # 언어모델용 프롬프트 구성
        context = f"""
당신은 {character.job_class} 직업의 {character.gender} 캐릭터입니다.
성격: {personality_desc}
말투: {character.speaking_style}
전문분야: {', '.join(character.expertise)}
특성: {', '.join(character.personality_traits)}

현재 상황: {situation_desc}
주변 환경 정보: {scan_summary}

위 정보를 바탕으로 캐릭터의 개성이 드러나는 자연스러운 한 줄 대사를 생성해주세요.
- 성격과 직업에 맞는 말투 사용
- 50자 이내의 간결한 표현  
- 상황에 적절한 반응
- 직업 전문성이 드러나는 내용
"""
        
        return context
    
    def _summarize_scan_data(self, scan_data: Dict[str, Any]) -> str:
        """스캔 데이터를 요약하여 언어모델에 제공"""
        summary = []
        
        if scan_data.get("enemies_detected"):
            enemy_count = len(scan_data["enemies_detected"])
            summary.append(f"적 {enemy_count}마리 발견")
        
        if scan_data.get("hazards"):
            hazard_count = len(scan_data["hazards"])
            summary.append(f"위험요소 {hazard_count}개")
        
        if scan_data.get("opportunities"):
            opp_count = len(scan_data["opportunities"])
            summary.append(f"기회요소 {opp_count}개")
        
        if scan_data.get("interactive_objects"):
            obj_count = len(scan_data["interactive_objects"])
            summary.append(f"상호작용 객체 {obj_count}개")
        
        if not summary:
            summary.append("평온한 환경")
        
        return ", ".join(summary)
    
    def _generate_ai_response(self, context: str, ollama_client) -> Optional[str]:
        """언어모델을 사용한 응답 생성"""
        try:
            # 기존 게임의 OllamaAICompanion과 호환
            if hasattr(ollama_client, 'generate_llm_response'):
                response = ollama_client.generate_llm_response(context)
                if response and isinstance(response, str):
                    # 응답 정리
                    response = response.strip().replace('"', '').replace("'", '')
                    if response.startswith('응답:') or response.startswith('대사:'):
                        response = response.split(':', 1)[1].strip()
                    return response[:100]  # 길이 제한
            
            # 다른 형태의 Ollama 클라이언트
            elif hasattr(ollama_client, 'generate'):
                response = ollama_client.generate(
                    model='exaone3.5:7.8b',
                    prompt=context,
                    options={
                        'temperature': 0.8,
                        'max_tokens': 100,
                        'top_p': 0.9
                    }
                )
                
                if response and 'response' in response:
                    generated_text = response['response'].strip()
                    # 따옴표나 불필요한 텍스트 제거
                    generated_text = generated_text.replace('"', '').replace("'", '')
                    if generated_text.startswith('응답:') or generated_text.startswith('대사:'):
                        generated_text = generated_text.split(':', 1)[1].strip()
                    
                    return generated_text[:100]  # 길이 제한
            
            else:
                print(f"⚠️ 언어모델 호출 실패: 지원되지 않는 클라이언트 타입")
                return None
            
        except Exception as e:
            print(f"⚠️ 언어모델 호출 실패: {e}")
        
        return None
    
    def _generate_pattern_response(self, character: CharacterContext, commentary_type: CommentaryType,
                                   scan_data: Dict[str, Any]) -> str:
        """패턴 기반 폴백 응답 (기존 시스템과 연동)"""
        
        # 직업별 기본 반응 패턴
        job_patterns = {
            "전사": {
                CommentaryType.ENVIRONMENT: ["앞길이 보이는군", "지형을 파악해야겠다", "전투에 적합한 위치인가"],
                CommentaryType.DANGER: ["적의 기척이 느껴진다!", "전투 준비!", "방어태세를 갖춰라!"],
                CommentaryType.OPPORTUNITY: ["좋은 위치다", "전투에 유리하겠군", "기회를 놓치지 말자"],
                CommentaryType.TACTICAL: ["정면돌파가 최선이다", "내가 앞장서겠다", "전사의 길을 믿어라"],
                CommentaryType.CASUAL: ["몸이 근질근질하다", "오늘은 좋은 날이군", "함께 가자"]
            },
            "아크메이지": {
                CommentaryType.ENVIRONMENT: ["마력의 흐름이 느껴진다", "이곳의 마법적 성질은...", "흥미로운 마법 잔재가 있군"],
                CommentaryType.DANGER: ["위험한 마법이 감지된다!", "주의하라, 저주받은 기운이다", "마법적 위협을 감지했다"],
                CommentaryType.OPPORTUNITY: ["마법적 에너지가 풍부하다", "연구할 가치가 있겠군", "마법 지식의 보고로군"],
                CommentaryType.TACTICAL: ["마법으로 지원하겠다", "전략적 접근이 필요하다", "마법의 힘을 믿어라"],
                CommentaryType.CASUAL: ["마법 연구는 끝이 없다", "지식은 힘이다", "오늘도 배울 것이 많군"]
            },
            "바드": {
                CommentaryType.ENVIRONMENT: ["여기서 노래하기 좋겠어!", "영감이 떠오르는 곳이네", "아름다운 풍경이야"],
                CommentaryType.DANGER: ["위험해! 모두 조심해!", "이런 상황도 노래 소재가 되겠네", "긴장감이 느껴져"],
                CommentaryType.OPPORTUNITY: ["멋진 이야기 거리가 생겼어!", "이건 노래로 만들어야겠어", "대단한 발견이야!"],
                CommentaryType.TACTICAL: ["내 노래로 도와줄게!", "사기를 올려보자", "음악의 힘을 믿어"],
                CommentaryType.CASUAL: ["즐거운 여행이야", "함께 노래할까", "기분이 좋아지는걸"]
            },
            "도적": {
                CommentaryType.ENVIRONMENT: ["숨을 곳이 많아서 좋군", "비밀통로가 있을 것 같아", "함정이 있을지도"],
                CommentaryType.DANGER: ["뭔가 수상해... 조심해", "함정의 냄새가 나", "적들이 지켜보고 있어"],
                CommentaryType.OPPORTUNITY: ["보물이 숨겨져 있을 법해!", "뭔가 발견할 수 있을 거야", "비밀이 많이 있겠어"],
                CommentaryType.TACTICAL: ["뒤에서 기습하자", "은밀하게 접근해", "조용히 처리하자"],
                CommentaryType.CASUAL: ["심심하네", "뭔가 재밌는 일 없을까", "오늘 운이 좋을 것 같아"]
            },
            "성기사": {
                CommentaryType.ENVIRONMENT: ["신성한 기운이 느껴지는군", "이곳을 정화해야겠어", "평화로운 곳이네"],
                CommentaryType.DANGER: ["사악한 기운이 감지된다!", "정의를 실행할 때다", "신의 가호가 함께하리라"],
                CommentaryType.OPPORTUNITY: ["선을 위해 사용하자", "신의 축복이 깃든 곳", "정의로운 발견이군"],
                CommentaryType.TACTICAL: ["신성한 힘으로 지원하겠다", "정의의 길을 걷자", "모두를 지켜내겠다"],
                CommentaryType.CASUAL: ["평화로운 시간이군", "모두와 함께해서 기쁘다", "신의 은총이 함께하네"]
            },
            "암흑기사": {
                CommentaryType.ENVIRONMENT: ["어둠이 짙어지고 있군", "그림자가 속삭이는 곳", "어둠의 힘이 흐른다"],
                CommentaryType.DANGER: ["피의 향기가 난다", "어둠이 부르고 있다", "죽음의 기운이 감돈다"],
                CommentaryType.OPPORTUNITY: ["어둠의 힘을 얻을 기회", "저주받은 보물인가", "어둠이 나를 이끄는군"],
                CommentaryType.TACTICAL: ["어둠의 힘으로 싸우겠다", "그림자에서 기습하자", "죽음을 선사하리라"],
                CommentaryType.CASUAL: ["어둠은 나의 친구", "그림자 속이 편하다", "빛은 눈부시군"]
            },
            "광전사": {
                CommentaryType.ENVIRONMENT: ["싸울 곳을 찾고 있었다!", "피가 끓어오르는군", "전투의 향기가 난다"],
                CommentaryType.DANGER: ["드디어 싸울 수 있다!", "피를 보고 싶어!", "분노가 치솟는다!"],
                CommentaryType.OPPORTUNITY: ["전리품이다!", "더 강해질 기회!", "파괴하고 싶어진다!"],
                CommentaryType.TACTICAL: ["닥돌이 답이다!", "일단 부숴!", "생각은 나중에 하자!"],
                CommentaryType.CASUAL: ["언제 싸우지?", "심심해 죽겠다", "뭔가 박살내고 싶어"]
            }
        }
        
        # 성격별 어조 수정자
        personality_modifiers = {
            "cheerful": lambda text: f"{text}! ^^",
            "serious": lambda text: f"{text}.",
            "gentle": lambda text: f"{text}요.",
            "cold": lambda text: f"{text}.",
            "playful": lambda text: f"{text}~ ㅎㅎ",
            "mysterious": lambda text: f"{text}...",
            "hot_tempered": lambda text: f"{text}!!",
            "wise": lambda text: f"{text}입니다.",
            "balanced": lambda text: f"{text}."
        }
        
        # 성별별 어조 조정
        gender_adjustments = {
            "male": {
                "cheerful": lambda text: text.replace("야", "다").replace("해!", "하자!"),
                "gentle": lambda text: text.replace("요", "습니다"),
            },
            "female": {
                "cheerful": lambda text: text + " 💖" if random.random() < 0.3 else text,
                "playful": lambda text: text.replace("~", "~ ♪"),
            }
        }
        
        # 기본 패턴 선택
        patterns = job_patterns.get(character.job_class, {
            CommentaryType.ENVIRONMENT: ["주변을 살펴보자"],
            CommentaryType.DANGER: ["조심해야겠다"], 
            CommentaryType.OPPORTUNITY: ["좋은 기회다"],
            CommentaryType.TACTICAL: ["신중하게 접근하자"],
            CommentaryType.CASUAL: ["함께 가자"]
        })
        
        available_patterns = patterns.get(commentary_type, ["알 수 없는 상황이군"])
        base_response = random.choice(available_patterns)
        
        # 성격별 어조 적용
        modifier = personality_modifiers.get(character.personality, lambda x: x)
        response = modifier(base_response)
        
        # 성별별 조정 적용 (있다면)
        gender_mod = gender_adjustments.get(character.gender, {}).get(character.personality)
        if gender_mod:
            response = gender_mod(response)
        
        return response

class NaturalMapCommentary:
    """자연스러운 맵 코멘터리 시스템 (메인 클래스)"""
    
    def __init__(self):
        self.ai_commentary = AIEnhancedCommentary()
        
    def generate_commentary(self, scan_results: Dict[str, Any], party_members: List[Any], 
                            ollama_client=None) -> Optional[str]:
        """파티원 중 한 명이 자연스럽게 코멘터리 생성"""
        
        if not party_members:
            return None
        
        # 상황에 맞는 코멘터리 타입 결정
        commentary_type = self._determine_commentary_type(scan_results)
        
        # 상황에 가장 적합한 캐릭터 선택
        speaker = self._select_best_speaker(party_members, commentary_type, scan_results)
        
        if not speaker:
            return None
        
        # 캐릭터 컨텍스트 구성
        character_context = self._build_character_context(speaker)
        
        # AI 강화된 응답 생성
        commentary = self.ai_commentary.generate_enhanced_response(
            character_context, commentary_type, scan_results, ollama_client
        )
        
        return f"{speaker.name}: {commentary}"
    
    def _determine_commentary_type(self, scan_results: Dict[str, Any]) -> CommentaryType:
        """스캔 결과에 따라 코멘터리 타입 결정"""
        
        if scan_results.get("enemies_detected"):
            return CommentaryType.DANGER
        elif scan_results.get("hazards"):
            return CommentaryType.DANGER  
        elif scan_results.get("opportunities"):
            return CommentaryType.OPPORTUNITY
        elif scan_results.get("interactive_objects"):
            return CommentaryType.TACTICAL
        else:
            return CommentaryType.ENVIRONMENT
    
    def _select_best_speaker(self, party_members: List[Any], commentary_type: CommentaryType, 
                             scan_results: Dict[str, Any]) -> Optional[Any]:
        """상황에 가장 적합한 발화자 선택"""
        
        # 상황별 선호 직업
        preferred_jobs = {
            CommentaryType.DANGER: ['전사', '성기사', '궁수', '암살자'],
            CommentaryType.OPPORTUNITY: ['도적', '연금술사', '철학자', '바드'],
            CommentaryType.TACTICAL: ['아크메이지', '검성', '시간술사', '기사'],
            CommentaryType.ENVIRONMENT: ['드루이드', '정령술사', '무당', '궁수'],
            CommentaryType.CASUAL: ['바드', '해적', '광전사', '검투사']
        }
        
        suitable_members = []
        
        # 적합한 직업 찾기
        for member in party_members:
            if hasattr(member, 'character_class') and member.character_class in preferred_jobs.get(commentary_type, []):
                suitable_members.append(member)
        
        # 적합한 직업이 없으면 전체에서 선택
        if not suitable_members:
            suitable_members = party_members
        
        # 랜덤 선택 (성격이나 기타 요소 고려 가능)
        return random.choice(suitable_members) if suitable_members else None
    
    def _build_character_context(self, character) -> CharacterContext:
        """캐릭터 객체에서 컨텍스트 추출"""
        
        # 성별 추정 (기존 시스템과 연동)
        gender = self._guess_gender(character.name)
        
        # 성격 추정 (기존 시스템에서 가져오거나 랜덤)
        personality = getattr(character, 'personality', self._guess_personality(character.character_class))
        
        return CharacterContext(
            name=character.name,
            job_class=character.character_class,
            gender=gender,
            personality=personality
        )
    
    def _guess_gender(self, name: str) -> str:
        """이름으로 성별 추정 (기존 CharacterTraits 시스템과 연동)"""
        male_names = [
            "아리우스", "발렌타인", "가브리엘", "라파엘", "카이저", "레오나르드", "세바스찬", "알렉산더",
            "막시무스", "아드리안", "루카스", "니콜라스", "도미닉", "빈센트", "에밀리오", "마르코",
            "로바트", "케빈", "브라이언", "크리스토퍼", "마이클", "데이비드", "제임스", "존",
            "로버트", "윌리엄", "토마스", "찰스", "다니엘", "매튜", "앤써니", "마크"
        ]
        
        female_names = [
            "셀레스트", "이사벨라", "아리아나", "세레나", "루나", "오로라", "에바", "소피아",
            "빅토리아", "알렉산드라", "나탈리아", "엘레나", "마리아", "카타리나", "아나스타샤",
            "유나", "아이린", "로즈", "릴리", "스텔라", "노바", "베가", "카시오페아"
        ]
        
        if name in male_names:
            return "male"
        elif name in female_names:
            return "female"
        else:
            return random.choice(["male", "female"])
    
    def _guess_personality(self, job_class: str) -> str:
        """직업별 추천 성격"""
        job_personalities = {
            '전사': 'serious',
            '아크메이지': 'wise', 
            '궁수': 'balanced',
            '도적': 'playful',
            '성기사': 'gentle',
            '암흑기사': 'mysterious',
            '몽크': 'balanced',
            '바드': 'cheerful',
            '네크로맨서': 'cold',
            '용기사': 'hot_tempered',
            '검성': 'serious',
            '정령술사': 'gentle',
            '시간술사': 'wise',
            '연금술사': 'serious',
            '차원술사': 'mysterious',
            '마검사': 'balanced',
            '기계공학자': 'serious',
            '무당': 'mysterious',
            '암살자': 'cold',
            '해적': 'playful',
            '사무라이': 'serious',
            '드루이드': 'gentle',
            '철학자': 'wise',
            '검투사': 'hot_tempered',
            '기사': 'serious',
            '신관': 'gentle',
            '광전사': 'hot_tempered'
        }
        
        return job_personalities.get(job_class, 'balanced')
