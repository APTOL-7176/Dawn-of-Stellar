#!/usr/bin/env python3
"""
AI 멀티플레이 시스템 - Phase 1: 통합 AI 캐릭터 생성기
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 목표: 클래식 모드를 AI 멀티플레이로 대체
📊 기능: 
- 27개 직업 지원 AI 캐릭터 생성  
- 캐릭터별 독립 데이터베이스
- 성격/성별/관심사 프리셋 저장
- EXAONE 3.5 연동 준비
"""

import os
import json
import random
from typing import List, Dict, Optional, Tuple
from ai_character_database import (
    create_ai_character_with_database, 
    preset_manager,
    get_ai_database,
    AICharacterDatabase
)

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
BRIGHT_CYAN = '\033[96m\033[1m'
BRIGHT_WHITE = '\033[97m\033[1m'
BRIGHT_GREEN = '\033[92m\033[1m'
BRIGHT_YELLOW = '\033[93m\033[1m'

class MultiplayerAICharacterCreator:
    """멀티플레이용 AI 캐릭터 생성기"""
    
    def __init__(self):
        # Dawn of Stellar의 27개 직업 정의
        self.all_classes = [
            # 기본 전투 직업군 (8개)
            "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크", "바드",
            
            # 마법 직업군 (10개)  
            "네크로맨서", "용기사", "검성", "정령술사", "시간술사", "연금술사", 
            "차원술사", "마검사", "기계공학자", "무당",
            
            # 특수 직업군 (9개)
            "암살자", "해적", "사무라이", "드루이드", "철학자", "검투사", 
            "기사", "신관", "광전사"
        ]
        
        # 성별 옵션
        self.genders = ["male", "female"]
        
        # 확장된 성격 시스템 (12가지)
        self.personality_types = [
            "용감한_리더",           # 정의감, 책임감, 리더십
            "신중한_전략가",         # 분석력, 계획성, 신중함
            "활발한_모험가",         # 호기심, 모험심, 활발함
            "냉정한_완벽주의자",     # 완벽주의, 효율성, 냉정함
            "따뜻한_치유자",         # 공감능력, 치유 본능, 따뜻함
            "장난기_많은_트릭스터",  # 유머, 창의성, 장난기
            "고요한_현자",           # 지혜, 침착함, 통찰력
            "열정적인_전사",         # 열정, 투지, 에너지
            "수줍은_학자",           # 내향성, 학구열, 신중함
            "카리스마_넘치는_리더",  # 카리스마, 사교성, 영향력
            "독립적인_탐험가",       # 독립성, 자유로움, 탐험심
            "보호본능_강한_수호자"   # 보호 본능, 헌신, 충성심
        ]
        
        # 이름 풀 (성별별)
        self.name_pools = {
            "male": [
                 "아리우스", "발렌타인", "가브리엘", "라파엘", "카이저", "레오나르드", "세바스찬", "알렉산더",
            "막시무스", "아드리안", "루카스", "니콜라스", "도미닉", "빈센트", "에밀리오", "마르코",
            "크리스", "오거스트", "바실리우스", "이그니스", "펠릭스", "라이언", "에릭",
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
            "세르겐", "빅터", "로만", "파벨", "녹티스", "아르템", "콘스탄틴", "발렌틴", "드미트리","티더","클라우드","프롬프토","그림니르","시스","랜슬롯",
            ],
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
        }
        
        # 직업별 전문 관심사 (AI 학습에 활용)
        self.class_specialties = {
            "전사": {
                "interests": ["방어_전술", "무기_기술", "파티_보호", "전선_유지"],
                "combat_style": "최전선_탱커",
                "preferred_actions": ["방패_강타", "도발", "수호_자세"],
                "personality_fit": ["용감한_리더", "보호본능_강한_수호자"]
            },
            "아크메이지": {
                "interests": ["마법_연구", "원소_조작", "마력_효율", "마법_이론"],
                "combat_style": "후방_광역_딜러",
                "preferred_actions": ["마력_파동", "원소_마법", "마법_폭발"],
                "personality_fit": ["고요한_현자", "수줍은_학자"]
            },
            "궁수": {
                "interests": ["정확성", "거리_조절", "조준_기술", "은밀_이동"],
                "combat_style": "원거리_정밀_딜러",
                "preferred_actions": ["삼연사", "관통사격", "정밀_조준"],
                "personality_fit": ["냉정한_완벽주의자", "독립적인_탐험가"]
            },
            "도적": {
                "interests": ["은신술", "함정_해제", "빠른_공격", "전리품_획득"],
                "combat_style": "기습_딜러",
                "preferred_actions": ["독침", "암살", "은신"],
                "personality_fit": ["장난기_많은_트릭스터", "독립적인_탐험가"]
            },
            "성기사": {
                "interests": ["신성_마법", "치유술", "정의_실현", "악의_척결"],
                "combat_style": "탱커_힐러_하이브리드",
                "preferred_actions": ["성스러운_타격", "치유", "정화"],
                "personality_fit": ["용감한_리더", "따뜻한_치유자"]
            },
            "암흑기사": {
                "interests": ["어둠_마법", "생명력_흡수", "공포_조성", "금기_탐구"],
                "combat_style": "흡혈_탱커",
                "preferred_actions": ["흡혈_베기", "어둠_마법", "공포"],
                "personality_fit": ["냉정한_완벽주의자", "고요한_현자"]
            },
            "몽크": {
                "interests": ["내공_수련", "신체_단련", "정신_집중", "기_조절"],
                "combat_style": "근접_콤보_딜러",
                "preferred_actions": ["연환_타격", "기_집중", "내공_수련"],
                "personality_fit": ["고요한_현자", "신중한_전략가"]
            },
            "바드": {
                "interests": ["음악_이론", "사기_진작", "사교술", "정보_수집"],
                "combat_style": "버프_서포터",
                "preferred_actions": ["음파_공격", "사기_진작", "치유_노래"],
                "personality_fit": ["카리스마_넘치는_리더", "활발한_모험가"]
            },
            # 나머지 직업들도 동일한 패턴으로 정의...
            "네크로맨서": {
                "interests": ["죽음_마법", "언데드_조종", "영혼_연구", "금기_지식"],
                "combat_style": "소환_마법사",
                "preferred_actions": ["생명력_흡수", "언데드_소환", "죽음_마법"],
                "personality_fit": ["고요한_현자", "수줍은_학자"]
            },
            "검성": {
                "interests": ["검술_완성", "검기_조작", "무도_철학", "수련_방법"],
                "combat_style": "검기_딜러",
                "preferred_actions": ["검기_베기", "일섬", "검술_수련"],
                "personality_fit": ["신중한_전략가", "독립적인_탐험가"]
            }
            # ... 더 많은 직업 추가 가능
        }
        
        # 성격별 말투 매핑
        self.speech_styles = {
            "용감한_리더": "격식있는_말투",
            "신중한_전략가": "정중한_말투", 
            "활발한_모험가": "친근한_말투",
            "냉정한_완벽주의자": "차가운_말투",
            "따뜻한_치유자": "부드러운_말투",
            "장난기_많은_트릭스터": "유쾌한_말투",
            "고요한_현자": "지혜로운_말투",
            "열정적인_전사": "열정적인_말투",
            "수줍은_학자": "조심스러운_말투",
            "카리스마_넘치는_리더": "당당한_말투",
            "독립적인_탐험가": "자유로운_말투",
            "보호본능_강한_수호자": "따뜻하고_강한_말투"
        }
    
    def create_ai_character_for_multiplayer(self, name: str = None, class_name: str = None, 
                                          gender: str = None, personality_type: str = None) -> Dict:
        """멀티플레이용 AI 캐릭터 생성"""
        
        # 랜덤 선택 처리
        if not name:
            selected_gender = gender or random.choice(self.genders)
            name = random.choice(self.name_pools[selected_gender])
        
        if not class_name:
            class_name = random.choice(self.all_classes)
        
        if not gender:
            gender = random.choice(self.genders)
        
        if not personality_type:
            # 직업에 맞는 성격 우선 선택
            if class_name in self.class_specialties:
                suitable_personalities = self.class_specialties[class_name]["personality_fit"]
                personality_type = random.choice(suitable_personalities + self.personality_types)
            else:
                personality_type = random.choice(self.personality_types)
        
        print(f"\n{CYAN}🤖 AI 멀티플레이 캐릭터 생성 중...{RESET}")
        print(f"{WHITE}├─ 이름: {name}{RESET}")
        print(f"{WHITE}├─ 직업: {class_name}{RESET}")
        print(f"{WHITE}├─ 성별: {gender}{RESET}")
        print(f"{WHITE}└─ 성격: {personality_type}{RESET}")
        
        # AI 캐릭터와 데이터베이스 생성
        character_data, database = create_ai_character_with_database(
            name, class_name, gender, personality_type
        )
        
        # 직업별 전문성 추가
        if class_name in self.class_specialties:
            specialty = self.class_specialties[class_name]
            
            # 관심사 확장
            character_data['ai_profile']['core_personality']['interests'].extend(
                specialty['interests']
            )
            
            # 전문 지식 업데이트
            character_data['ai_profile']['professional_knowledge'].update({
                'combat_style': specialty['combat_style'],
                'preferred_actions': specialty['preferred_actions'],
                'specialty_knowledge': specialty['interests']
            })
        
        # 말투 스타일 설정
        character_data['basic_info']['speech_style'] = self.speech_styles.get(
            personality_type, "보통_말투"
        )
        
        # 멀티플레이 전용 설정 추가
        character_data['multiplayer_settings'] = {
            'ai_controlled': True,
            'cooperation_level': 0.8,  # 협력성 (0.0 ~ 1.0)
            'independence_level': 0.6,  # 독립성 (0.0 ~ 1.0)
            'communication_frequency': 0.7,  # 대화 빈도 (0.0 ~ 1.0)
            'decision_making_style': self._get_decision_style(personality_type)
        }
        
        # 프리셋 재저장 (완전한 AI 프로필 포함)
        preset_manager.save_character_preset(character_data)
        
        return {
            'character_data': character_data,
            'database': database,
            'ai_ready': True
        }
    
    def _get_decision_style(self, personality_type: str) -> str:
        """성격에 따른 의사결정 스타일 반환"""
        decision_styles = {
            "용감한_리더": "적극적_결단",
            "신중한_전략가": "분석적_계획",
            "활발한_모험가": "직감적_행동",
            "냉정한_완벽주의자": "논리적_최적화",
            "따뜻한_치유자": "공감적_배려",
            "장난기_많은_트릭스터": "창의적_실험",
            "고요한_현자": "통찰적_판단",
            "열정적인_전사": "감정적_돌진",
            "수줍은_학자": "신중한_관찰",
            "카리스마_넘치는_리더": "영향력_활용",
            "독립적인_탐험가": "자율적_판단",
            "보호본능_강한_수호자": "방어적_우선"
        }
        return decision_styles.get(personality_type, "균형적_판단")
    
    def create_multiplayer_party(self, party_size: int = 4, exclude_jobs: List[str] = None) -> List[Dict]:
        """멀티플레이용 AI 파티 생성 (역할 균형 고려 + 직업 중복 방지)"""
        print(f"\n{BRIGHT_CYAN}🎮 AI 멀티플레이 파티 생성 ({party_size}명){RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        if exclude_jobs is None:
            exclude_jobs = []
        
        # 역할별 직업 분류 (밸런스 잡힌 파티 구성)
        role_distribution = {
            "탱커": ["전사", "성기사", "기사", "암흑기사", "검투사"],
            "딜러": ["궁수", "도적", "암살자", "검성", "사무라이", "광전사"],
            "마법사": ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사"],
            "서포터": ["바드", "신관", "드루이드", "무당", "철학자"],
            "하이브리드": ["몽크", "용기사", "마검사", "기계공학자", "해적"]
        }
        
        # 제외할 직업 필터링
        for role, jobs in role_distribution.items():
            role_distribution[role] = [job for job in jobs if job not in exclude_jobs]
        
        party_members = []
        used_names = set()
        used_jobs = set(exclude_jobs)  # 이미 제외할 직업들 추가
        
        # 파티 구성 전략 (4명 기준)
        if party_size >= 4:
            required_roles = ["탱커", "딜러", "마법사", "서포터"]
        else:
            required_roles = ["탱커", "딜러", "서포터"][:party_size-1] + ["하이브리드"]
        
        # 필수 역할 캐릭터 생성
        for i, role in enumerate(required_roles):
            if i >= party_size:
                break
            
            # 사용 가능한 직업들 중에서 선택 (중복 방지)
            available_jobs = [job for job in role_distribution[role] if job not in used_jobs]
            if not available_jobs:
                # 해당 역할에 사용 가능한 직업이 없으면 다른 역할에서 선택
                all_available = []
                for other_role, jobs in role_distribution.items():
                    all_available.extend([job for job in jobs if job not in used_jobs])
                if all_available:
                    class_name = random.choice(all_available)
                else:
                    continue  # 정말 선택할 직업이 없으면 스킵
            else:
                class_name = random.choice(available_jobs)
            
            used_jobs.add(class_name)  # 사용된 직업 추가
            gender = random.choice(self.genders)
            
            # 직업에 맞는 성격 선택 (개선된 매칭)
            personality_type = self._get_suitable_personality(class_name)
            
            # 직업과 성격에 맞는 이름과 성별 선택
            name, gender = self._get_suitable_name(class_name, personality_type)
            
            # 이름 중복 방지
            attempts = 0
            while name in used_names and attempts < 10:
                name, gender = self._get_suitable_name(class_name, personality_type)
                attempts += 1
            
            # 여전히 중복이면 숫자 추가
            if name in used_names:
                name = f"{name}_{i+1}"
            
            used_names.add(name)
            
            character = self.create_ai_character_for_multiplayer(
                name, class_name, gender, personality_type
            )
            party_members.append(character)
            
            print(f"  {GREEN}✅ {role}: {name} ({class_name}, {personality_type}){RESET}")
        
        # 나머지 슬롯 채우기
        for i in range(len(required_roles), party_size):
            role = random.choice(list(role_distribution.keys()))
            class_name = random.choice(role_distribution[role])
            gender = random.choice(self.genders)
            personality_type = random.choice(self.personality_types)
            
            # 이름 중복 방지
            attempts = 0
            while attempts < 30:
                name = random.choice(self.name_pools[gender])
                if name not in used_names:
                    used_names.add(name)
                    break
                attempts += 1
            else:
                name = f"{random.choice(self.name_pools[gender])}_{i+1}"
            
            character = self.create_ai_character_for_multiplayer(
                name, class_name, gender, personality_type
            )
            party_members.append(character)
            
            print(f"  {GREEN}✅ {role}: {name} ({class_name}, {personality_type}){RESET}")
        
        # 파티 시너지 분석
        self._analyze_party_synergy(party_members)
        
        print(f"\n{BRIGHT_GREEN}🎉 AI 멀티플레이 파티 완성! ({len(party_members)}명){RESET}")
        return party_members
    
    def _analyze_party_synergy(self, party_members: List[Dict]):
        """파티 시너지 분석"""
        print(f"\n{YELLOW}📊 파티 시너지 분석:{RESET}")
        
        classes = [member['character_data']['basic_info']['class'] for member in party_members]
        personalities = [member['character_data']['basic_info']['personality_type'] for member in party_members]
        
        # 직업 시너지 체크
        synergies = []
        if "성기사" in classes and "신관" in classes:
            synergies.append("신성 시너지 (성기사 + 신관)")
        if "암흑기사" in classes and "네크로맨서" in classes:
            synergies.append("어둠 시너지 (암흑기사 + 네크로맨서)")
        if "아크메이지" in classes and "정령술사" in classes:
            synergies.append("원소 마스터 (아크메이지 + 정령술사)")
        
        # 성격 조화 분석
        leadership_count = sum(1 for p in personalities if "리더" in p)
        healer_count = sum(1 for p in personalities if "치유자" in p or "수호자" in p)
        
        print(f"  {WHITE}├─ 직업 시너지: {len(synergies)}개{RESET}")
        for synergy in synergies:
            print(f"  {WHITE}│  • {synergy}{RESET}")
        
        print(f"  {WHITE}├─ 리더십: {leadership_count}명{RESET}")
        print(f"  {WHITE}├─ 치유/보호: {healer_count}명{RESET}")
        
        # 전체 평가
        if len(synergies) >= 2:
            rating = "🌟 Excellent"
        elif len(synergies) >= 1:
            rating = "⭐ Good"
        else:
            rating = "✨ Standard"
        
        print(f"  {WHITE}└─ 파티 등급: {rating}{RESET}")
    
    def _get_suitable_personality(self, class_name: str) -> str:
        """직업에 맞는 성격 유형 반환"""
        # 직업별 어울리는 성격 매핑
        class_personality_map = {
            # 전투 직업군 - 강인하고 용감한 성격
            "전사": ["용감한_전사", "충성스런_기사", "단호한_지휘관", "수호하는_방패", "불굴의_투사"],
            "성기사": ["신실한_성자", "정의로운_기사", "수호하는_방패", "자비로운_치유자", "빛의_수호자"],
            "암흑기사": ["냉정한_전술가", "고독한_기사", "어둠의_수호자", "복수의_검", "침묵하는_전사"],
            "몽크": ["평온한_수도승", "단련하는_구도자", "깨달은_현자", "수행하는_무도가", "조화로운_영혼"],
            "아크메이지": ["지혜로운_현자", "탐구하는_학자", "신비로운_술사", "마법의_지배자", "원소의_주인"],
            "궁수": ["냉정한_저격수", "자유로운_유랑자", "정확한_명사수", "숲의_수호자", "바람의_사자"],
            "도적": ["교활한_도둑", "그림자_무용수", "침묵하는_암살자", "민첩한_탐험가", "은밀한_정탐꾼"],
            "바드": ["낭만적_음유시인", "매혹적_예술가", "유쾌한_엔터테이너", "감성적_시인", "카리스마_리더"],
            
            # 마법 직업군 - 지적이고 신비로운 성격
            "네크로맨서": ["어둠의_학자", "죽음의_현자", "고독한_연구자", "금기의_탐구자", "영혼의_지배자"],
            "용기사": ["용맹한_기사", "불의_전사", "드래곤_동반자", "화염의_수호자", "고귀한_전사"],
            "검성": ["초월한_검사", "검의_구도자", "무예의_달인", "고독한_검호", "완벽한_검사"],
            "정령술사": ["자연의_친구", "원소의_현자", "조화로운_술사", "신비로운_드루이드", "정령의_대화자"],
            "시간술사": ["신비로운_예언자", "시간의_수호자", "운명의_조율자", "차원의_여행자", "미래의_관찰자"],
            "연금술사": ["탐구하는_학자", "실험적_발명가", "지적인_연구자", "창조적_과학자", "변화의_대가"],
            "차원술사": ["초월적_현자", "차원의_탐험가", "공간의_지배자", "무한의_탐구자", "현실의_조율자"],
            "마검사": ["균형의_전사", "마법_검사", "이중의_수행자", "조화로운_전사", "완성된_검사"],
            "기계공학자": ["창의적_발명가", "기계의_대가", "논리적_엔지니어", "혁신적_창조자", "완벽주의_기술자"],
            "무당": ["영적인_치유자", "신비로운_무당", "자연의_대변자", "영혼의_안내자", "조상의_대리인"],
            
            # 특수 직업군 - 독특하고 특별한 성격
            "암살자": ["침묵하는_그림자", "냉혹한_암살자", "완벽한_킬러", "그림자_무용수", "죽음의_사자"],
            "해적": ["자유로운_모험가", "바다의_늑대", "모험적_선장", "용감한_해적", "바다의_지배자"],
            "사무라이": ["명예로운_무사", "완벽한_검사", "충의의_전사", "고귀한_사무라이", "무도의_달인"],
            "드루이드": ["자연의_수호자", "야생의_친구", "대지의_현자", "생명의_보호자", "자연의_대변자"],
            "철학자": ["깊이_사색하는_현자", "지혜로운_철학자", "진리의_탐구자", "사색적_학자", "깨달은_현자"],
            "검투사": ["투기의_전사", "불굴의_투사", "경기장_영웅", "전투의_예술가", "승리의_추구자"],
            "기사": ["고귀한_기사", "명예로운_전사", "충성스런_기사", "정의의_수호자", "완벽한_기사"],
            "신관": ["신실한_성직자", "자비로운_치유자", "빛의_사도", "희망의_전령", "평화의_수호자"],
            "광전사": ["광기의_전사", "파괴적_투사", "분노의_화신", "전투광_바이킹", "폭풍의_전사"]
        }
        
        # 직업에 맞는 성격 목록 가져오기
        suitable_personalities = class_personality_map.get(class_name, ["균형잡힌_모험가"])
        return random.choice(suitable_personalities)
    
    def _get_suitable_name(self, class_name: str, personality_type: str) -> tuple[str, str]:
        """직업과 성격에 맞는 이름과 성별 생성 (성별별 이름 풀 사용)"""
        
        # 성별 랜덤 선택 후 해당 성별 이름 풀에서 선택
        gender = random.choice(["male", "female"])
        name_pool = self.name_pools[gender]
        base_name = random.choice(name_pool)
        
        # 성격에 따른 수식어 추가 (선택적)
        if "리더" in personality_type:
            modifiers = ["대장", "캡틴", "리더"]
        elif "현자" in personality_type or "학자" in personality_type:
            modifiers = ["현자", "박사", "마스터"]
        elif "전사" in personality_type or "기사" in personality_type:
            modifiers = ["기사", "전사", "가디언"]
        else:
            modifiers = []
        
        # 20% 확률로 수식어 추가
        if modifiers and random.random() < 0.2:
            final_name = f"{random.choice(modifiers)} {base_name}"
        else:
            final_name = base_name
            
        return final_name, gender

    def display_ai_character_profile(self, character: Dict):
        """AI 캐릭터 상세 프로필 표시"""
        data = character['character_data']
        database = character['database']
        
        print(f"\n{BRIGHT_CYAN}👤 AI 캐릭터 프로필{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        basic = data['basic_info']
        ai_profile = data['ai_profile']
        multiplayer = data.get('multiplayer_settings', {})
        
        print(f"{BRIGHT_WHITE}🎭 기본 정보:{RESET}")
        print(f"   이름: {basic['name']}")
        print(f"   직업: {basic['class']}")
        print(f"   성별: {basic['gender']}")
        print(f"   나이: {basic['age']}")
        print(f"   성격: {basic['personality_type']}")
        print(f"   말투: {basic['speech_style']}")
        
        print(f"\n{BRIGHT_WHITE}🧠 AI 성격:{RESET}")
        core = ai_profile['core_personality']
        print(f"   특성: {', '.join(core['traits'])}")
        print(f"   관심사: {', '.join(core['interests'][:4])}...")
        print(f"   두려움: {', '.join(core['fears'])}")
        print(f"   동기: {', '.join(core['motivations'])}")
        
        print(f"\n{BRIGHT_WHITE}⚔️ 전문성:{RESET}")
        prof = ai_profile['professional_knowledge']
        print(f"   전투 스타일: {prof.get('combat_style', '일반적')}")
        print(f"   선호 행동: {', '.join(prof.get('preferred_actions', [])[:3])}")
        print(f"   전문 분야: {', '.join(prof.get('specialty_knowledge', [])[:3])}")
        
        print(f"\n{BRIGHT_WHITE}🎮 멀티플레이 설정:{RESET}")
        print(f"   AI 제어: {'활성화' if multiplayer.get('ai_controlled', True) else '비활성화'}")
        print(f"   협력성: {multiplayer.get('cooperation_level', 0.8):.1f}/1.0")
        print(f"   독립성: {multiplayer.get('independence_level', 0.6):.1f}/1.0")
        print(f"   소통 빈도: {multiplayer.get('communication_frequency', 0.7):.1f}/1.0")
        print(f"   의사결정: {multiplayer.get('decision_making_style', '균형적_판단')}")
        
        print(f"\n{BRIGHT_WHITE}💾 AI 데이터베이스:{RESET}")
        stats = database.get_statistics()
        print(f"   DB 파일: {ai_profile.get('database_file', 'N/A')}")
        print(f"   학습 이벤트: {stats['total_learning_events']}개")
        print(f"   관계 데이터: {stats['total_relationships']}개")
        print(f"   게임 지식: {stats['total_knowledge_items']}개")
        print(f"   행동 패턴: {stats['total_behavioral_patterns']}개")
        print(f"   평균 신뢰도: {stats['average_trust_level']:.2f}/1.0")

def test_multiplayer_ai_creator():
    """멀티플레이 AI 생성기 테스트"""
    print(f"{BRIGHT_CYAN}🧪 멀티플레이 AI 캐릭터 생성기 테스트{RESET}")
    
    creator = MultiplayerAICharacterCreator()
    
    # 단일 캐릭터 테스트
    print(f"\n{YELLOW}=== 단일 AI 캐릭터 생성 테스트 ==={RESET}")
    character = creator.create_ai_character_for_multiplayer()
    creator.display_ai_character_profile(character)
    
    # AI 파티 테스트
    print(f"\n{YELLOW}=== AI 멀티플레이 파티 생성 테스트 ==={RESET}")
    party = creator.create_multiplayer_party(4)
    
    print(f"\n{BRIGHT_GREEN}📋 완성된 AI 파티 요약:{RESET}")
    for i, member in enumerate(party, 1):
        data = member['character_data']
        basic = data['basic_info']
        mp_settings = data.get('multiplayer_settings', {})
        print(f"  {i}. {basic['name']} - {basic['class']}")
        print(f"     성격: {basic['personality_type']} | 협력성: {mp_settings.get('cooperation_level', 0.8):.1f}")
    
    print(f"\n{GREEN}✅ Phase 1 테스트 완료! 클래식 모드 → AI 멀티플레이 준비됨{RESET}")

if __name__ == "__main__":
    test_multiplayer_ai_creator()
