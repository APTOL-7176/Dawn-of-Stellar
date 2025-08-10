#!/usr/bin/env python3
"""
🌟 AI 통합 캐릭터 생성 시스템 확장
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ 특징:
- 기존 캐릭터 생성기에 AI 기능 완전 통합
- 성별, 성격, 관심사를 프리셋에 자동 저장
- 캐릭터별 독립적인 AI 데이터베이스 생성
- 27개 직업 모두 지원
- 멀티플레이용 AI 동료 자동 설정
"""

import os
import json
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# AI 멀티플레이 시스템 임포트
from game_ai_multiplayer import GameIntegratedAI, AIPersonality, AICharacterDatabase

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

class AICharacterCreatorExtension:
    """AI 통합 캐릭터 생성 확장 시스템"""
    
    def __init__(self):
        self.ai_system = GameIntegratedAI()
        self.preset_file = "character_presets_ai.json"
        
        # 확장된 성격 시스템 (더 세분화된 27개 직업별 특성)
        self.extended_personality_traits = {
            # 전사 계열
            "전사": {
                "core_traits": ["용맹함", "충성심", "보호욕"],
                "sub_traits": ["직진적", "단순함", "정의감", "끈기"],
                "quirks": ["무기 손질하기", "훈련 좋아함", "술 못함", "동료 챙기기"]
            },
            "검성": {
                "core_traits": ["완벽주의", "절제", "수련욕"],
                "sub_traits": ["고독함", "엄격함", "집중력", "인내"],
                "quirks": ["검 모으기", "명상하기", "차 마시기", "조용한 곳 선호"]
            },
            "검투사": {
                "core_traits": ["경쟁심", "불굴의지", "생존본능"],
                "sub_traits": ["거침없음", "자신감", "도전정신", "승부욕"],
                "quirks": ["승부 좋아함", "관중 의식", "상처 자랑", "강자 존경"]
            },
            "광전사": {
                "core_traits": ["열정", "충동성", "원시성"],
                "sub_traits": ["감정적", "본능적", "자유로움", "강인함"],
                "quirks": ["큰 소리", "육식 선호", "단순 사고", "감정 표현 직접적"]
            },
            
            # 기사 계열
            "성기사": {
                "core_traits": ["신성함", "희생정신", "치유욕"],
                "sub_traits": ["온화함", "인내심", "자비", "정의감"],
                "quirks": ["기도하기", "약자 돕기", "채식주의", "일찍 자기"]
            },
            "암흑기사": {
                "core_traits": ["신비함", "복잡함", "이중성"],
                "sub_traits": ["깊이있음", "철학적", "고독함", "강인함"],
                "quirks": ["야행성", "독서광", "어둠 선호", "깊은 사색"]
            },
            "기사": {
                "core_traits": ["충성심", "명예", "의무감"],
                "sub_traits": ["예의바름", "규율적", "보호욕", "희생정신"],
                "quirks": ["예의 중시", "약속 지키기", "갑옷 관리", "귀족적 취향"]
            },
            "용기사": {
                "core_traits": ["고귀함", "웅장함", "전설추구"],
                "sub_traits": ["열정적", "모험적", "자부심", "카리스마"],
                "quirks": ["용 이야기", "불꽃 좋아함", "높은 곳 선호", "전설 수집"]
            },
            
            # 원거리 계열
            "궁수": {
                "core_traits": ["정밀함", "인내심", "집중력"],
                "sub_traits": ["조용함", "관찰력", "신중함", "독립적"],
                "quirks": ["활 손질", "정적 선호", "야생동물 좋아함", "멀리서 관찰"]
            },
            "도적": {
                "core_traits": ["영리함", "민첩함", "자유로움"],
                "sub_traits": ["기회주의", "독립적", "실용적", "적응력"],
                "quirks": ["그림자 이용", "보물 찾기", "몰래 움직이기", "정보 수집"]
            },
            "암살자": {
                "core_traits": ["차가움", "정밀함", "은밀함"],
                "sub_traits": ["냉정함", "계산적", "완벽주의", "고독함"],
                "quirks": ["무표정", "조용히 이동", "독 관심", "어둠 활용"]
            },
            "사무라이": {
                "core_traits": ["명예", "절제", "완벽함"],
                "sub_traits": ["엄격함", "예의바름", "충성심", "자기성찰"],
                "quirks": ["도검 관리", "차도 즐김", "명상하기", "전통 중시"]
            },
            
            # 마법 계열
            "아크메이지": {
                "core_traits": ["지적호기심", "탐구정신", "신비추구"],
                "sub_traits": ["분석적", "논리적", "집중력", "창의적"],
                "quirks": ["책 읽기", "실험하기", "별 관찰", "지식 수집"]
            },
            "네크로맨서": {
                "core_traits": ["금기적", "신비적", "깊이있음"],
                "sub_traits": ["철학적", "고독함", "이해심", "복잡함"],
                "quirks": ["야행성", "해골 수집", "고서 연구", "죽음 철학"]
            },
            "정령술사": {
                "core_traits": ["자연친화", "조화추구", "순수함"],
                "sub_traits": ["평화적", "직관적", "유연함", "공감능력"],
                "quirks": ["자연과 대화", "꽃 기르기", "동물 친구", "계절 느끼기"]
            },
            "시간술사": {
                "core_traits": ["신비함", "복잡함", "통찰력"],
                "sub_traits": ["철학적", "예언적", "신중함", "지혜로움"],
                "quirks": ["시계 수집", "과거 회상", "미래 걱정", "운명 사색"]
            },
            "연금술사": {
                "core_traits": ["실험정신", "호기심", "창조욕"],
                "sub_traits": ["창의적", "도전적", "끈기있음", "변화추구"],
                "quirks": ["실험하기", "재료 수집", "조합 시도", "발견 좋아함"]
            },
            "차원술사": {
                "core_traits": ["초월적", "신비적", "복잡함"],
                "sub_traits": ["다차원적", "철학적", "유연함", "창의적"],
                "quirks": ["공간 조작", "차원 연구", "이동 실험", "현실 의문"]
            },
            "마검사": {
                "core_traits": ["균형추구", "융합적", "이중성"],
                "sub_traits": ["적응력", "완벽주의", "진화욕", "조화"],
                "quirks": ["검과 마법", "균형 추구", "완벽 조합", "새 기술 개발"]
            },
            
            # 서포터 계열
            "바드": {
                "core_traits": ["예술적", "사교적", "감정적"],
                "sub_traits": ["표현력", "공감능력", "창의적", "자유로움"],
                "quirks": ["노래하기", "이야기하기", "감정 표현", "파티 좋아함"]
            },
            "신관": {
                "core_traits": ["신성함", "봉사정신", "치유욕"],
                "sub_traits": ["온화함", "인내심", "희생정신", "자비"],
                "quirks": ["기도하기", "병자 돌보기", "성서 읽기", "평화 추구"]
            },
            "드루이드": {
                "core_traits": ["자연사랑", "보호욕", "평화주의"],
                "sub_traits": ["직관적", "포용적", "신비적", "성장지향"],
                "quirks": ["나무와 대화", "동물 보호", "자연 치유", "순환 믿음"]
            },
            "무당": {
                "core_traits": ["영적", "신비적", "치유적"],
                "sub_traits": ["직관적", "공감적", "신비적", "조화추구"],
                "quirks": ["영혼과 소통", "주술 의식", "자연 제물", "영적 상담"]
            },
            "철학자": {
                "core_traits": ["사색적", "논리적", "탐구적"],
                "sub_traits": ["지적", "분석적", "성찰적", "지혜추구"],
                "quirks": ["깊은 사색", "논리 전개", "진리 탐구", "토론 좋아함"]
            },
            
            # 특수 계열
            "몽크": {
                "core_traits": ["균형", "수련", "깨달음"],
                "sub_traits": ["절제", "명상적", "평화적", "조화"],
                "quirks": ["명상하기", "수행하기", "절제 생활", "내면 성찰"]
            },
            "기계공학자": {
                "core_traits": ["논리적", "창의적", "실용적"],
                "sub_traits": ["혁신적", "정밀함", "효율추구", "문제해결"],
                "quirks": ["기계 조작", "발명하기", "효율 추구", "논리적 사고"]
            },
            "해적": {
                "core_traits": ["자유로움", "모험적", "무법"],
                "sub_traits": ["대담함", "즉흥적", "개방적", "독립적"],
                "quirks": ["보물 찾기", "바다 그리워함", "자유 추구", "모험담 좋아함"]
            }
        }
        
        # 확장된 관심사 시스템
        self.extended_interests = {
            "학문": ["역사", "철학", "과학", "문학", "언어학", "심리학", "고고학", "천문학"],
            "예술": ["음악", "그림", "조각", "무용", "시", "소설", "연극", "건축"],
            "자연": ["동물", "식물", "날씨", "계절", "산", "바다", "별", "달"],
            "기술": ["연금술", "마법", "기계", "무기", "방어구", "발명", "실험", "혁신"],
            "사회": ["정치", "경제", "문화", "종교", "전통", "역사", "외교", "정의"],
            "개인": ["수련", "명상", "독서", "요리", "여행", "모험", "수집", "게임"],
            "관계": ["가족", "친구", "동료", "스승", "제자", "연인", "라이벌", "동맹"],
            "가치": ["명예", "자유", "평화", "정의", "지혜", "힘", "아름다움", "진리"]
        }
        
        # 확장된 성별 정보
        self.gender_info = {
            "남성": {
                "pronouns": ["그", "그가", "그의", "그를", "그에게"],
                "titles": ["형", "선배", "대장", "선생", "님", "씨"],
                "speech_tendencies": ["단호하게", "간결하게", "직설적으로"]
            },
            "여성": {
                "pronouns": ["그녀", "그녀가", "그녀의", "그녀를", "그녀에게"],
                "titles": ["언니", "선배", "대장", "선생", "님", "씨"],
                "speech_tendencies": ["부드럽게", "섬세하게", "배려하며"]
            },
            "중성": {
                "pronouns": ["그", "그가", "그의", "그를", "그에게"],
                "titles": ["동료", "파트너", "선생", "님", "씨"],
                "speech_tendencies": ["중립적으로", "균형있게", "합리적으로"]
            }
        }
    
    def create_enhanced_ai_character(self, character_name: str, character_class: str, 
                                   custom_personality: Dict = None) -> Tuple[Dict, AIPersonality]:
        """향상된 AI 캐릭터 생성"""
        
        print(f"\n{BRIGHT_CYAN}🎭 {character_name}의 AI 성격 생성 중...{RESET}")
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        # 기본 정보 설정
        gender = custom_personality.get("gender") if custom_personality else random.choice(["남성", "여성", "중성"])
        age = custom_personality.get("age") if custom_personality else random.randint(18, 45)
        
        # 직업별 특성 가져오기
        job_traits = self.extended_personality_traits.get(character_class, self.extended_personality_traits["전사"])
        
        # 성격 특성 조합
        core_trait = random.choice(job_traits["core_traits"])
        sub_trait = random.choice(job_traits["sub_traits"])
        quirk = random.choice(job_traits["quirks"])
        
        # 복합 성격 타입 생성
        personality_type = f"{core_trait}하며 {sub_trait}"
        
        # 말투 스타일 (성별과 성격 고려)
        gender_tendencies = self.gender_info[gender]["speech_tendencies"]
        speech_style = random.choice([
            "격식있는", "친근한", "귀여운", "쿨한", "열정적인", "차분한",
            "장난스러운", "진지한", "따뜻한", "시크한"
        ])
        
        # 관심사 생성 (직업 + 랜덤)
        job_template = self.ai_system.job_ai_templates.get(character_class, {})
        base_interests = job_template.get("interests", ["모험", "동료"])
        
        # 카테고리별로 관심사 추가
        additional_interests = []
        for category, interests in self.extended_interests.items():
            if random.random() < 0.3:  # 30% 확률로 각 카테고리에서 선택
                additional_interests.append(random.choice(interests))
        
        all_interests = base_interests + additional_interests[:3]  # 최대 6개
        
        # 취미, 두려움, 꿈 생성 (더 다양하게)
        hobbies = [
            "독서", "음악감상", "요리", "운동", "여행", "그림그리기", "조각", "시쓰기",
            "별보기", "낚시", "정원가꾸기", "수집", "게임", "춤", "명상", "발명",
            "무기 손질", "마법 연구", "동물 돌보기", "이야기 만들기", "악기 연주",
            "기계 조립", "약초 재배", "보석 세공", "지도 그리기", "역사 연구"
        ]
        
        fears = [
            "높은 곳", "어둠", "물", "불", "혼자 있는 것", "실패", "배신", "잊혀지는 것",
            "변화", "책임", "과거", "미래", "군중", "침묵", "혼돈", "완벽함",
            "마법 실패", "동료 잃기", "명예 실추", "힘의 부족", "무력함", "고립",
            "의무 방기", "신념 흔들림", "자유 구속", "창의력 고갈", "관계 파탄"
        ]
        
        dreams = [
            "세계평화", "완벽한 기술 습득", "진정한 친구", "평온한 삶", "모험", "지식탐구",
            "예술 창작", "가족", "명예", "자유", "성장", "발견", "치유", "보호", "창조", "조화",
            "전설 되기", "스승 되기", "세상 구하기", "완벽한 작품", "이상향 건설",
            "진리 발견", "혁신 이루기", "평화 실현", "균형 찾기", "극한 돌파"
        ]
        
        # AI 성격 객체 생성
        personality = AIPersonality(
            name=character_name,
            job=character_class,
            gender=gender,
            age=age,
            personality_type=personality_type,
            speech_style=speech_style,
            hobby=random.choice(hobbies),
            fear=random.choice(fears),
            dream=random.choice(dreams),
            combat_preference=job_template.get("combat_preference", "균형적"),
            risk_tolerance=random.choice(["신중함", "보통", "모험적", "무모함"]),
            teamwork_style=random.choice(["리더십", "협력적", "독립적", "추종적"]),
            learning_style=random.choice(["빠른학습", "꾸준함", "실험적", "보수적"]),
            interests=all_interests,
            memory_weight=random.uniform(0.7, 0.95),
            creativity_level=random.randint(4, 9),
            social_level=random.randint(3, 8)
        )
        
        # 캐릭터 기본 정보
        character_data = {
            "name": character_name,
            "class": character_class,
            "level": 1,
            "gender": gender,
            "age": age,
            "quirk": quirk,
            "created_at": datetime.now().isoformat(),
            "ai_enabled": True
        }
        
        # 생성 결과 출력
        print(f"  {GREEN}👤 이름:{RESET} {character_name} ({gender}, {age}세)")
        print(f"  {BLUE}🎭 성격:{RESET} {personality_type}")
        print(f"  {MAGENTA}🗣️ 말투:{RESET} {speech_style}")
        print(f"  {YELLOW}🎯 특징:{RESET} {quirk}")
        print(f"  {CYAN}💭 관심사:{RESET} {', '.join(all_interests[:3])}")
        print(f"  {WHITE}🎈 취미:{RESET} {personality.hobby}")
        print(f"  {RED}😰 두려움:{RESET} {personality.fear}")
        print(f"  {GREEN}🌟 꿈:{RESET} {personality.dream}")
        
        return character_data, personality
    
    def save_enhanced_preset(self, character_data: Dict, personality: AIPersonality, 
                           additional_data: Dict = None):
        """향상된 프리셋 저장"""
        try:
            # 기존 프리셋 로드
            presets = {}
            if os.path.exists(self.preset_file):
                with open(self.preset_file, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
            
            # AI 데이터베이스 생성
            ai_db = AICharacterDatabase(character_data["name"])
            ai_db.save_personality(personality)
            
            # 프리셋 데이터 구성
            preset_data = {
                **character_data,
                "ai_personality": {
                    "basic_info": {
                        "gender": personality.gender,
                        "age": personality.age,
                        "personality_type": personality.personality_type,
                        "speech_style": personality.speech_style
                    },
                    "personal_traits": {
                        "hobby": personality.hobby,
                        "fear": personality.fear,
                        "dream": personality.dream,
                        "quirk": character_data.get("quirk", "")
                    },
                    "game_preferences": {
                        "combat_preference": personality.combat_preference,
                        "risk_tolerance": personality.risk_tolerance,
                        "teamwork_style": personality.teamwork_style,
                        "learning_style": personality.learning_style
                    },
                    "interests_and_memory": {
                        "interests": personality.interests,
                        "memory_weight": personality.memory_weight,
                        "creativity_level": personality.creativity_level,
                        "social_level": personality.social_level
                    }
                },
                "ai_database_path": f"ai_memory_{character_data['name']}.db",
                "learning_stats": {
                    "conversations": 0,
                    "events": 0,
                    "satisfaction": 0.5,
                    "relationships": 0
                }
            }
            
            # 추가 데이터 병합
            if additional_data:
                preset_data.update(additional_data)
            
            # 프리셋 저장
            presets[character_data["name"]] = preset_data
            
            with open(self.preset_file, 'w', encoding='utf-8') as f:
                json.dump(presets, f, ensure_ascii=False, indent=2)
            
            print(f"\n{BRIGHT_GREEN}✅ {character_data['name']}의 AI 프리셋이 저장되었습니다!{RESET}")
            print(f"{WHITE}파일: {self.preset_file}{RESET}")
            
        except Exception as e:
            print(f"{RED}❌ 프리셋 저장 실패: {e}{RESET}")
    
    def create_ai_multiplayer_characters(self, party_size: int = 4) -> List[Dict]:
        """AI 멀티플레이용 캐릭터들 생성"""
        print(f"\n{BRIGHT_CYAN}🚀 AI 멀티플레이 캐릭터 생성 시작!{RESET}")
        print(f"{CYAN}클래식 모드 → AI 멀티플레이로 업그레이드! 🌟{RESET}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        # 자동 파티 빌더로 기본 구성 가져오기
        basic_party = self.ai_system.auto_builder.create_balanced_party(party_size=party_size)
        
        ai_characters = []
        
        for i, character in enumerate(basic_party, 1):
            print(f"\n{BRIGHT_YELLOW}🎭 {i}/{party_size}: {character.name} ({character.character_class}) 설정 중...{RESET}")
            
            # AI 캐릭터 생성
            char_data, personality = self.create_enhanced_ai_character(
                character.name, 
                character.character_class
            )
            
            # 캐릭터 능력치 정보 추가
            char_data.update({
                "stats": {
                    "level": getattr(character, 'level', 1),
                    "hp": getattr(character, 'current_hp', 100),
                    "max_hp": getattr(character, 'max_hp', 100),
                    "physical_attack": getattr(character, 'physical_attack', 10),
                    "magic_attack": getattr(character, 'magic_attack', 10),
                    "physical_defense": getattr(character, 'physical_defense', 8),
                    "magic_defense": getattr(character, 'magic_defense', 8),
                    "speed": getattr(character, 'speed', 5),
                    "luck": getattr(character, 'luck', 5)
                }
            })
            
            # 프리셋 저장
            self.save_enhanced_preset(char_data, personality)
            
            # AI 데이터베이스 생성 및 성격 저장
            ai_db = AICharacterDatabase(char_data["name"])
            ai_db.save_personality(personality)
            
            # AI 캐릭터 정보 구성
            ai_char = {
                "character": character,
                "character_data": char_data,
                "personality": personality,
                "database": ai_db,  # 데이터베이스 추가
                "ai_ready": True,
                "multiplayer_enabled": True
            }
            
            ai_characters.append(ai_char)
        
        print(f"\n{BRIGHT_GREEN}🎉 AI 멀티플레이 캐릭터 생성 완료!{RESET}")
        self._display_party_summary(ai_characters)
        
        return ai_characters
    
    def _display_party_summary(self, ai_characters: List[Dict]):
        """파티 요약 정보 표시"""
        print(f"\n{BRIGHT_CYAN}📋 AI 멀티플레이 파티 요약{RESET}")
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for i, ai_char in enumerate(ai_characters, 1):
            char_data = ai_char["character_data"]
            personality = ai_char["personality"]
            
            # 역할 아이콘
            role_icons = {
                "전사": "🛡️", "검성": "⚔️", "검투사": "🗡️", "광전사": "🔥",
                "성기사": "✨", "암흑기사": "🌙", "기사": "🏰", "용기사": "🐉",
                "궁수": "🏹", "도적": "🗡️", "암살자": "💀", "사무라이": "🎌",
                "아크메이지": "🔮", "네크로맨서": "💀", "정령술사": "🌿", "시간술사": "⏰",
                "연금술사": "⚗️", "차원술사": "🌀", "마검사": "⚔️🔮",
                "바드": "🎵", "신관": "⛪", "드루이드": "🌳", "무당": "🔯", "철학자": "📚",
                "몽크": "🧘", "기계공학자": "⚙️", "해적": "🏴‍☠️"
            }
            
            icon = role_icons.get(char_data["class"], "⭐")
            
            print(f"\n{YELLOW}{icon} {i}. {char_data['name']}{RESET}")
            print(f"    {BLUE}직업:{RESET} {char_data['class']}")
            print(f"    {GREEN}성격:{RESET} {personality.personality_type}")
            print(f"    {MAGENTA}말투:{RESET} {personality.speech_style}")
            print(f"    {CYAN}특징:{RESET} {char_data.get('quirk', '없음')}")
            print(f"    {WHITE}관심사:{RESET} {', '.join(personality.interests[:2])}")
        
        print(f"\n{BRIGHT_WHITE}💡 이제 이 AI 동료들과 함께 진짜 멀티플레이를 즐기세요!{RESET}")
        print(f"{GREEN}   • 각자 고유한 성격과 대화 스타일{RESET}")
        print(f"{BLUE}   • 게임 상황에 맞는 반응과 조언{RESET}")
        print(f"{MAGENTA}   • 플레이하면서 점점 더 똑똑해지는 AI{RESET}")
        print(f"{CYAN}   • 캐릭터가 죽어도 기억은 영원히 보존{RESET}")

def test_ai_character_creation():
    """AI 캐릭터 생성 테스트"""
    print(f"{BRIGHT_CYAN}🧪 AI 캐릭터 생성 시스템 테스트{RESET}")
    
    creator = AICharacterCreatorExtension()
    
    # 테스트용 캐릭터 생성
    test_characters = creator.create_ai_multiplayer_characters(4)
    
    print(f"\n{BRIGHT_GREEN}✅ 테스트 완료! 생성된 캐릭터 수: {len(test_characters)}{RESET}")
    
    return test_characters

if __name__ == "__main__":
    test_ai_character_creation()
