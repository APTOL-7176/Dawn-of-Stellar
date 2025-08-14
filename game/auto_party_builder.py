#!/usr/bin/env python3
"""
자동 파티 구성 시스템 - 밸런스 잡힌 파티 자동 생성
"""

import random
from typing import List, Dict, Any, Optional
from game.character import Character, CharacterClassManager, CharacterTrait  # CharacterTrait 추가
from game.input_utils import KeyboardInput
from game import enhanced_items
from config import game_config

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
BRIGHT_YELLOW = '\033[93m\033[1m'
BRIGHT_CYAN = '\033[96m\033[1m'
BRIGHT_WHITE = '\033[97m\033[1m'

class AutoPartyBuilder:
    """자동 파티 구성 시스템"""
    
    def __init__(self):
        self.keyboard = KeyboardInput()
        self._used_names = set()
    
    # 전체 직업 정의 (기본 8개 + 해금 19개)
    ALL_CLASSES = [
        # 기본 8개 직업 (쓰기 쉬운 직업들)
        "전사", "궁수", "성기사", "암흑기사", "바드", "검성", "검투사", "광전사",
        
        # 해금 필요한 19개 직업
        "아크메이지", "도적", "몽크", "네크로맨서", "용기사", "정령술사", "암살자", 
        "기계공학자", "무당", "해적", "사무라이", "드루이드", "철학자", "시간술사", 
        "연금술사", "기사", "신관", "마검사", "차원술사"
    ]
    
    # 역할별 분류 (Phase 1&2 직업 포함) - 통일된 분류
    ROLE_CLASSES = {
        "탱커": ["전사", "성기사", "기사", "암흑기사", "검투사", "광전사", "용기사"],
        "딜러": ["궁수", "도적", "암살자", "검성", "사무라이"],
        "마법사": ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사", "마검사", "기계공학자"],
        "서포터": ["바드", "신관", "드루이드", "무당", "철학자"],
        "하이브리드": ["몽크", "해적"]
    }
    
    # 시너지 조합 (새로운 직업 시너지 추가)
    SYNERGY_COMBINATIONS = {
        "성기사 + 신관": {"bonus": "신성 시너지", "effect": "언데드에게 추가 피해"},
        "암흑기사 + 네크로맨서": {"bonus": "어둠 시너지", "effect": "생명력 흡수 증가"},
        "궁수 + 사무라이": {"bonus": "원거리 + 근거리", "effect": "속도 보너스"},
        "바드 + 아크메이지": {"bonus": "마법 증폭", "effect": "마법 피해 증가"},
        "드루이드 + 정령술사": {"bonus": "자연 조화", "effect": "MP 회복 증가"},
        "기계공학자 + 연금술사": {"bonus": "과학 조합", "effect": "아이템 효과 증가"},
        
        # 🌟 Phase 1&2 새로운 시너지
        "검성 + 검투사": {"bonus": "검술 대가", "effect": "검기/처치 스택 효율 증가"},
        "광전사 + 암흑기사": {"bonus": "흡혈 전사", "effect": "생명력 흡수 효과 2배"},
        "기사 + 성기사": {"bonus": "기사단", "effect": "보호 및 치유 효과 증가"},
        "용기사 + 아크메이지": {"bonus": "원소 융합", "effect": "화염+번개 복합 공격"},
        "검성 + 광전사": {"bonus": "검의 광기", "effect": "스택 생성 속도 증가"},
        "검투사 + 기사": {"bonus": "투기장 기사", "effect": "패링 성공 시 의무 스택 획득"}
    }
    
    # 직업별 고유 기믹 정보 (상태창 표시용)
    CLASS_MECHANICS = {
        "검성": {"type": "스택", "display": "검기 스택", "max": 2, "description": "BRV 공격 시 획득, HP공격/스킬에 소모하여 위력 증폭"},
        "검투사": {"type": "스택", "display": "처치 스택", "max": 99, "description": "적 처치 시 공격력/MP/HP 증가 (전투 내 무한 중첩)"},
        "광전사": {"type": "보호막", "display": "피의 보호막", "max": 999999, "description": "HP 소모하여 생성, 보호막 소모 시 흡혈 회복"},
        "기사": {"type": "스택", "display": "의무 스택", "max": 5, "description": "아군 대신 피해 시 획득, 3스택 이상 시 죽음 회피"},
        "성기사": {"type": "필드", "display": "성역", "max": 3, "description": "버프 아군 피해 시 생성, 성역 수에 따른 강화"},
        "암흑기사": {"type": "흡수", "display": "어둠 흡수", "max": 999999, "description": "피해 흡수하여 스택화 (최대 HP 75%)"},
        "용기사": {"type": "표식", "display": "용의 표식", "max": 5, "description": "도약 공격 시 부여, 착지 시 표식당 추가 피해"},
        "아크메이지": {"type": "원소", "display": "원소 순환", "max": 3, "description": "동일 속성 3회 사용 시 강화 마법 자동 발동"},
        "정령술사": {"type": "소환", "display": "정령", "max": 2, "description": "상황별 정령 자동 소환 (불/물/바람/땅)"},
        "시간술사": {"type": "저장", "display": "시간 저장", "max": 1, "description": "아군/적 상태를 시점으로 저장하여 복원"},
        "차원술사": {"type": "스택", "display": "잔상 스택", "max": 5, "description": "회피 성공 시 축적, 차원이동 공격에 사용"},
        "네크로맨서": {"type": "시체", "display": "시체 수집", "max": 10, "description": "죽은 자를 시체로 수집, 언데드 소환/폭발에 사용"},
        "암살자": {"type": "스택", "display": "그림자 스택", "max": 3, "description": "은신 성공 시 축적, 암살 공격 위력 증폭"},
        "궁수": {"type": "스택", "display": "조준 포인트", "max": 5, "description": "스킬 사용 시 축적, 명중률/치명타율 증가"},
        "기계공학자": {"type": "소환", "display": "기계 유닛", "max": 3, "description": "포탑/드론 설치, 자동 기능 발동"},
        "철학자": {"type": "스택", "display": "분석 스택", "max": 3, "description": "적 분석하여 적응형 스킬 강화"},
        "해적": {"type": "수집", "display": "약탈품", "max": 99, "description": "적 처치 시 자원/아이템/버프 강탈"},
        "사무라이": {"type": "게이지", "display": "의지 게이지", "max": 100, "description": "회피/반격 성공 시 증가, 강력한 기술 발동"},
        "바드": {"type": "음계", "display": "음계 진행", "max": 7, "description": "도레미파솔라시 진행, 옥타브 완성 시 강력 버프"},
        "무당": {"type": "전환", "display": "디버프 전환", "max": 5, "description": "디버프를 버프로 전환하거나 반사"},
        "드루이드": {"type": "변신", "display": "자연 감응", "max": 100, "description": "감응도 축적하여 야수/식물 형태 변신"},
        "신관": {"type": "스택", "display": "속죄 스택", "max": 99, "description": "피해 받을 때 축적, 치유/방어막에 사용"},
        "몽크": {"type": "콤보", "display": "기 콤보", "max": 5, "description": "연속 공격 콤보, 기 축적으로 강화"},
        "마검사": {"type": "속성", "display": "원소 부여", "max": 4, "description": "무기에 속성 부여, 원소 조합으로 연쇄 반응"}
    }
    
    # 질문 기반 파티 추천을 위한 질문 풀 (30개 질문)
    PARTY_QUESTIONS = [
        {
            "question": "어떤 전투 스타일을 선호하시나요?",
            "answers": [
                {"text": "속전속결! 빠르게 끝내고 싶어요", "tags": ["속도", "딜러", "크리티컬", "공격적", "빠름"]},
                {"text": "안전하게 천천히 진행하고 싶어요", "tags": ["탱커", "생존", "방어", "안정", "신중"]},
                {"text": "화려한 마법으로 싸우고 싶어요", "tags": ["마법", "원소", "AOE", "화려", "마법사"]},
                {"text": "전략적이고 복잡한 전투를 좋아해요", "tags": ["하이브리드", "시너지", "복합", "전략", "깊이"]}
            ]
        },
        {
            "question": "파티에서 가장 중요하게 생각하는 것은?",
            "answers": [
                {"text": "높은 데미지로 적을 빠르게 처치", "tags": ["딜러", "공격", "DPS", "폭딜", "처치"]},
                {"text": "안정적인 생존과 회복", "tags": ["서포터", "힐링", "생존", "회복", "안정"]},
                {"text": "다양한 상황에 대응할 수 있는 유연성", "tags": ["하이브리드", "유틸", "적응", "유연", "대응"]},
                {"text": "독특하고 재미있는 기믹", "tags": ["특수", "유니크", "실험", "기믹", "창의"]}
            ]
        },
        {
            "question": "적과 마주했을 때 첫 번째 행동은?",
            "answers": [
                {"text": "일단 공격! 선제 타격이 최고", "tags": ["공격", "선제", "어그로", "적극", "공격적"]},
                {"text": "방어 태세를 갖추고 신중하게", "tags": ["방어", "탱킹", "신중", "보호", "수비"]},
                {"text": "적의 약점을 파악하고 분석", "tags": ["분석", "전략", "지능", "관찰", "계획"]},
                {"text": "동료들을 지원하고 버프", "tags": ["서포트", "팀플레이", "협력", "지원", "버프"]}
            ]
        },
        {
            "question": "위험한 상황에서 어떻게 대처하나요?",
            "answers": [
                {"text": "더 강하게 공격해서 돌파!", "tags": ["공격적", "돌파", "강함", "용기", "적극"]},
                {"text": "방어하면서 기회를 기다려요", "tags": ["방어", "인내", "기다림", "신중", "수비"]},
                {"text": "기발한 방법으로 해결해요", "tags": ["창의", "기발", "독특", "실험", "유연"]},
                {"text": "팀원들과 협력해서 극복해요", "tags": ["협력", "팀워크", "지원", "조화", "함께"]}
            ]
        },
        {
            "question": "선호하는 자원 관리 방식은?",
            "answers": [
                {"text": "HP를 소모해서라도 강력한 공격!", "tags": ["HP소모", "위험", "공격적", "리스크", "강력함"]},
                {"text": "MP를 아껴서 중요할 때 사용", "tags": ["MP관리", "절약", "신중", "계획", "효율"]},
                {"text": "특수 자원(스택, 게이지)을 활용", "tags": ["스택", "게이지", "특수", "관리", "전략"]},
                {"text": "자원보다는 기본 공격 위주", "tags": ["기본공격", "단순", "직관", "안정", "기본"]}
            ]
        },
        {
            "question": "어떤 역할을 맡고 싶나요?",
            "answers": [
                {"text": "최전선에서 적을 막는 방패", "tags": ["탱커", "방어", "보호", "최전선", "수호"]},
                {"text": "강력한 공격으로 적을 쓰러뜨리는 검", "tags": ["딜러", "공격", "처치", "검", "강력함"]},
                {"text": "마법으로 전장을 지배하는 현자", "tags": ["마법사", "지배", "현자", "마법", "지능"]},
                {"text": "동료를 돕는 든든한 지원군", "tags": ["서포터", "지원", "도움", "든든함", "협력"]}
            ]
        },
        {
            "question": "가장 매력적인 전투 기믹은?",
            "answers": [
                {"text": "스택을 쌓아서 폭발적인 일격!", "tags": ["스택", "폭발", "일격", "축적", "강력함"]},
                {"text": "회피와 반격의 완벽한 타이밍", "tags": ["회피", "반격", "타이밍", "정밀", "기술"]},
                {"text": "원소를 조합한 화려한 마법", "tags": ["원소", "조합", "화려", "마법", "다양함"]},
                {"text": "동료와의 완벽한 연계 플레이", "tags": ["연계", "협력", "완벽", "시너지", "팀워크"]}
            ]
        },
        {
            "question": "전투에서 가장 중요한 능력치는?",
            "answers": [
                {"text": "압도적인 공격력", "tags": ["공격력", "압도적", "강함", "폭딜", "데미지"]},
                {"text": "튼튼한 방어력과 체력", "tags": ["방어력", "체력", "튼튼함", "생존", "안정"]},
                {"text": "빠른 속도와 민첩성", "tags": ["속도", "민첩", "빠름", "기동력", "선제"]},
                {"text": "높은 마법력과 지능", "tags": ["마법력", "지능", "마법", "현명함", "전략"]}
            ]
        },
        {
            "question": "게임에서 가장 짜릿한 순간은?",
            "answers": [
                {"text": "크리티컬이 터져서 엄청난 데미지!", "tags": ["크리티컬", "폭딜", "RNG", "운", "터짐"]},
                {"text": "절체절명의 순간에서 역전!", "tags": ["역전", "스릴", "극한", "드라마", "긴장"]},
                {"text": "완벽한 콤보가 들어갔을 때", "tags": ["콤보", "연계", "정밀", "완벽", "기술"]},
                {"text": "팀원들과 완벽한 호흡으로 승리", "tags": ["팀워크", "협력", "조화", "시너지", "단결"]}
            ]
        },
        {
            "question": "적에게 상태이상을 거는 것에 대해?",
            "answers": [
                {"text": "독, 화상 등으로 서서히 괴롭히기", "tags": ["독", "지속피해", "인내", "서서히", "괴롭힘"]},
                {"text": "침묵, 마비로 행동을 봉쇄하기", "tags": ["침묵", "마비", "봉쇄", "방해", "제어"]},
                {"text": "버프로 아군을 강화하는 게 좋아", "tags": ["버프", "강화", "지원", "아군", "도움"]},
                {"text": "상태이상보다는 직접 공격!", "tags": ["직접공격", "단순", "강력함", "즉시", "명확"]}
            ]
        },
        {
            "question": "파티원이 위험할 때 당신의 선택은?",
            "answers": [
                {"text": "몸을 던져서 대신 맞아주기", "tags": ["희생", "보호", "탱킹", "용기", "수호"]},
                {"text": "즉시 치유해서 회복시키기", "tags": ["치유", "회복", "서포트", "도움", "케어"]},
                {"text": "적을 더 빨리 처치해서 해결", "tags": ["공격", "처치", "빠름", "공격적", "해결"]},
                {"text": "전략적으로 위치를 바꾸기", "tags": ["전략", "위치", "이동", "지능", "계획"]}
            ]
        },
        {
            "question": "선호하는 무기 타입은?",
            "answers": [
                {"text": "검이나 도끼 같은 근접 무기", "tags": ["근접", "검", "물리", "직접", "강함"]},
                {"text": "활이나 총 같은 원거리 무기", "tags": ["원거리", "활", "정밀", "안전", "거리"]},
                {"text": "지팡이나 오브 같은 마법 도구", "tags": ["마법도구", "지팡이", "마법", "신비", "지능"]},
                {"text": "방패나 보호구 같은 방어구", "tags": ["방패", "방어", "보호", "안전", "수비"]}
            ]
        },
        {
            "question": "전투 후 가장 먼저 하고 싶은 일은?",
            "answers": [
                {"text": "전리품을 수집하고 정리하기", "tags": ["수집", "정리", "전리품", "효율", "관리"]},
                {"text": "부상을 치료하고 휴식하기", "tags": ["치료", "휴식", "회복", "안정", "케어"]},
                {"text": "다음 전투를 준비하고 전략 세우기", "tags": ["준비", "전략", "계획", "미래", "지능"]},
                {"text": "동료들과 전투를 되돌아보기", "tags": ["회고", "동료", "소통", "학습", "팀워크"]}
            ]
        },
        {
            "question": "어떤 환경에서 싸우고 싶나요?",
            "answers": [
                {"text": "넓은 평야에서 자유롭게", "tags": ["넓음", "자유", "개방", "기동성", "활동"]},
                {"text": "좁은 통로에서 전략적으로", "tags": ["좁음", "전략", "제한", "집중", "계획"]},
                {"text": "마법이 강화되는 신비한 곳", "tags": ["마법강화", "신비", "특별", "마법", "환경"]},
                {"text": "어디든 상관없어, 적응할 수 있어", "tags": ["적응", "유연", "범용", "안정", "균형"]}
            ]
        },
        {
            "question": "가장 싫어하는 적의 유형은?",
            "answers": [
                {"text": "엄청나게 단단한 적", "tags": ["단단함", "방어", "인내", "지속", "끈기"]},
                {"text": "너무 빠르고 회피하는 적", "tags": ["빠름", "회피", "민첩", "추적", "속도"]},
                {"text": "마법으로 방해하는 적", "tags": ["마법방해", "제어", "대응", "해제", "자유"]},
                {"text": "무리를 지어 몰려오는 적", "tags": ["무리", "다수", "AOE", "광역", "효율"]}
            ]
        },
        {
            "question": "이상적인 전투 시간은?",
            "answers": [
                {"text": "1-2턴 만에 끝내는 초스피드", "tags": ["초스피드", "빠름", "폭딜", "효율", "즉시"]},
                {"text": "5-10턴 정도의 적당한 길이", "tags": ["적당함", "균형", "안정", "여유", "계획"]},
                {"text": "길고 치열한 승부", "tags": ["길게", "치열", "인내", "전략", "깊이"]},
                {"text": "상황에 따라 유연하게", "tags": ["유연", "상황대응", "적응", "변화", "균형"]}
            ]
        },
        {
            "question": "팀 플레이에서 가장 중요한 것은?",
            "answers": [
                {"text": "각자의 역할을 완벽하게 수행", "tags": ["역할수행", "완벽", "전문성", "집중", "숙련"]},
                {"text": "서로를 보완하며 협력", "tags": ["보완", "협력", "시너지", "도움", "조화"]},
                {"text": "리더의 지시에 따라 행동", "tags": ["리더십", "지시", "조직", "체계", "통제"]},
                {"text": "자유롭게 각자 판단해서 행동", "tags": ["자유", "판단", "독립", "창의", "유연"]}
            ]
        },
        {
            "question": "캐릭터 성장에서 중요한 것은?",
            "answers": [
                {"text": "강력한 공격 스킬 습득", "tags": ["공격스킬", "강력함", "딜러", "위력", "파괴"]},
                {"text": "생존을 위한 방어 능력", "tags": ["방어능력", "생존", "안정", "버티기", "지구력"]},
                {"text": "다양한 유틸리티 스킬", "tags": ["유틸리티", "다양함", "유연", "도구", "편의"]},
                {"text": "특별하고 독특한 능력", "tags": ["특별함", "독특함", "유니크", "개성", "특색"]}
            ]
        },
        {
            "question": "게임에서 가장 좋아하는 순간은?",
            "answers": [
                {"text": "새로운 스킬을 배웠을 때", "tags": ["스킬습득", "성장", "새로움", "발전", "학습"]},
                {"text": "어려운 적을 물리쳤을 때", "tags": ["승리", "도전", "성취", "극복", "성공"]},
                {"text": "동료와 완벽한 연계를 했을 때", "tags": ["연계", "팀워크", "완벽", "협력", "조화"]},
                {"text": "예상치 못한 상황에서 기지를 발휘했을 때", "tags": ["기지", "창의", "순발력", "놀라움", "독창"]}
            ]
        },
        {
            "question": "당신의 플레이 철학은?",
            "answers": [
                {"text": "강한 자가 살아남는다", "tags": ["강함", "생존", "경쟁", "실력", "우승"]},
                {"text": "모두가 함께 성장한다", "tags": ["성장", "함께", "공동체", "협력", "발전"]},
                {"text": "재미있으면 그것으로 충분하다", "tags": ["재미", "즐거움", "엔터테인", "행복", "만족"]},
                {"text": "완벽을 추구한다", "tags": ["완벽", "정밀", "완성", "품질", "최고"]}
            ]
        },
        {
            "question": "보스전에서 가장 중요한 전략은?",
            "answers": [
                {"text": "강력한 일격으로 빠르게 끝내기", "tags": ["일격", "빠름", "폭딜", "공격적", "결정적"]},
                {"text": "안전하게 패턴을 파악하며 공략", "tags": ["패턴", "안전", "분석", "신중", "학습"]},
                {"text": "팀원들과 역할 분담해서 협력", "tags": ["협력", "역할분담", "팀워크", "조직", "시너지"]},
                {"text": "창의적인 방법으로 약점 공략", "tags": ["창의", "약점", "기발", "전략", "독특"]}
            ]
        },
        {
            "question": "던전 탐험에서 가장 흥미로운 요소는?",
            "answers": [
                {"text": "숨겨진 보물과 비밀 방", "tags": ["보물", "비밀", "탐험", "발견", "수집"]},
                {"text": "다양한 몬스터와의 전투", "tags": ["몬스터", "전투", "다양함", "도전", "액션"]},
                {"text": "퍼즐과 함정 해결", "tags": ["퍼즐", "함정", "지능", "해결", "사고"]},
                {"text": "동료들과의 모험 이야기", "tags": ["모험", "이야기", "동료", "추억", "여정"]}
            ]
        },
        {
            "question": "적의 약점을 발견했을 때 어떻게 하나요?",
            "answers": [
                {"text": "즉시 약점을 집중 공격", "tags": ["집중공격", "약점", "즉시", "효율", "타겟팅"]},
                {"text": "팀원들에게 알려서 함께 공략", "tags": ["정보공유", "팀워크", "소통", "협력", "조직"]},
                {"text": "약점 공격용 스킬을 준비", "tags": ["준비", "스킬", "계획", "전략", "특화"]},
                {"text": "약점보다는 정면승부", "tags": ["정면승부", "직접", "당당함", "강함", "정직"]}
            ]
        },
        {
            "question": "새로운 장비를 얻었을 때 우선순위는?",
            "answers": [
                {"text": "공격력이 높은 무기", "tags": ["공격력", "무기", "딜러", "강함", "데미지"]},
                {"text": "방어력이 높은 방어구", "tags": ["방어력", "방어구", "탱커", "생존", "안전"]},
                {"text": "특수 효과가 있는 장비", "tags": ["특수효과", "유니크", "기능", "다양함", "특별"]},
                {"text": "세트 효과를 맞출 수 있는 장비", "tags": ["세트효과", "조합", "시너지", "완성", "체계"]}
            ]
        },
        {
            "question": "파티 구성에서 가장 신경쓰는 부분은?",
            "answers": [
                {"text": "각 역할의 균형", "tags": ["균형", "역할", "안정", "체계", "완성"]},
                {"text": "강력한 시너지 효과", "tags": ["시너지", "조합", "상승효과", "협력", "강화"]},
                {"text": "개성 있는 캐릭터들", "tags": ["개성", "다양함", "특색", "유니크", "재미"]},
                {"text": "상황 대응 능력", "tags": ["대응능력", "유연", "적응", "변화", "범용"]}
            ]
        },
        {
            "question": "전투에서 가장 만족스러운 순간은?",
            "answers": [
                {"text": "완벽한 타이밍의 스킬 사용", "tags": ["타이밍", "완벽", "스킬", "정밀", "기술"]},
                {"text": "예상보다 높은 데미지가 나올 때", "tags": ["높은데미지", "예상초과", "놀라움", "강력", "성과"]},
                {"text": "위기를 모면했을 때", "tags": ["위기모면", "생존", "안도", "극복", "회복"]},
                {"text": "팀원을 구해냈을 때", "tags": ["구조", "도움", "희생", "보호", "영웅"]}
            ]
        },
        {
            "question": "마법과 물리 공격 중 선호하는 것은?",
            "answers": [
                {"text": "화려하고 강력한 마법", "tags": ["마법", "화려", "강력", "신비", "원소"]},
                {"text": "확실하고 직접적인 물리 공격", "tags": ["물리", "직접", "확실", "근접", "단순"]},
                {"text": "마법과 물리를 조합", "tags": ["조합", "하이브리드", "다양", "복합", "균형"]},
                {"text": "상황에 따라 선택", "tags": ["상황대응", "선택", "유연", "적응", "전략"]}
            ]
        },
        {
            "question": "게임에서 가장 중요한 재미 요소는?",
            "answers": [
                {"text": "강해지는 성장의 재미", "tags": ["성장", "강화", "발전", "진보", "향상"]},
                {"text": "새로운 것을 발견하는 재미", "tags": ["발견", "새로움", "탐험", "호기심", "모험"]},
                {"text": "친구들과 함께하는 재미", "tags": ["친구", "함께", "소셜", "공유", "유대"]},
                {"text": "도전과 극복의 재미", "tags": ["도전", "극복", "성취", "승리", "만족"]}
            ]
        },
        {
            "question": "이상적인 캐릭터 빌드는?",
            "answers": [
                {"text": "한 분야에 특화된 전문가", "tags": ["전문가", "특화", "집중", "마스터", "깊이"]},
                {"text": "여러 분야를 아우르는 만능형", "tags": ["만능", "다재다능", "균형", "범용", "유연"]},
                {"text": "독특한 컨셉의 개성파", "tags": ["개성", "독특", "컨셉", "특별", "유니크"]},
                {"text": "팀에 꼭 필요한 핵심 역할", "tags": ["핵심", "필수", "중요", "역할", "책임"]}
            ]
        }
    ]
    
    # 태그별 직업 매핑 (확장형)
    TAG_TO_CLASSES = {
        # 스타일 태그
        "속도": ["궁수", "암살자", "도적", "사무라이", "광전사"],
        "딜러": ["검성", "검투사", "궁수", "암살자", "도적", "해적", "사무라이"],
        "크리티컬": ["궁수", "암살자", "사무라이", "해적"],
        "탱커": ["전사", "성기사", "기사", "검투사", "용기사"],
        "생존": ["전사", "성기사", "기사", "신관", "드루이드"],
        "방어": ["전사", "성기사", "기사", "검투사"],
        "마법": ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사"],
        "원소": ["아크메이지", "정령술사", "마검사", "용기사"],
        "AOE": ["아크메이지", "네크로맨서", "연금술사"],
        "하이브리드": ["암흑기사", "몽크", "기계공학자", "마검사"],
        "서포터": ["바드", "신관", "드루이드", "무당", "철학자"],
        "힐링": ["신관", "드루이드", "바드", "성기사"],
        "특수": ["시간술사", "차원술사", "무당", "철학자", "해적"],
        "유니크": ["네크로맨서", "기계공학자", "무당", "철학자"],
        
        # 전투 스타일 태그
        "공격적": ["검성", "검투사", "광전사", "암살자"],
        "신중": ["궁수", "철학자", "시간술사", "성기사"],
        "분석": ["철학자", "시간술사", "연금술사"],
        "전략": ["시간술사", "철학자", "기계공학자", "바드"],
        "지원": ["바드", "신관", "드루이드", "무당"],
        "협력": ["바드", "성기사", "신관", "기사"],
        
        # 자원 관리 태그
        "HP소모": ["광전사", "암흑기사", "무당"],
        "MP관리": ["아크메이지", "네크로맨서", "정령술사"],
        "스택": ["검성", "검투사", "차원술사", "궁수", "기사"],
        "게이지": ["사무라이", "바드", "드루이드"],
        "특수자원": ["네크로맨서", "해적", "기계공학자"],
        
        # 역할 태그
        "수호": ["성기사", "기사", "전사"],
        "처치": ["검성", "검투사", "암살자", "해적"],
        "지배": ["아크메이지", "네크로맨서", "시간술사"],
        "도움": ["바드", "신관", "드루이드", "무당"],
        
        # 기믹 태그
        "폭발": ["연금술사", "아크메이지", "광전사"],
        "회피": ["차원술사", "암살자", "사무라이"],
        "반격": ["검투사", "사무라이", "기사"],
        "조합": ["아크메이지", "정령술사", "마검사", "연금술사"],
        "연계": ["바드", "몽크", "기계공학자"],
        
        # 능력치 태그
        "공격력": ["검성", "검투사", "광전사"],
        "방어력": ["전사", "성기사", "기사"],
        "민첩": ["도적", "암살자", "궁수"],
        "마법력": ["아크메이지", "네크로맨서", "정령술사"]
    }
    
    # 특성 태그 매핑 (질문 기반으로 특성도 추천) - 6단계 완전체 시스템
    TAG_TO_TRAITS = {
        "공격적": ["6단계 완전체", "전장의 지배자", "패링 마스터", "피의 갈증"],
        "방어": ["6단계 완전체", "신성한 보호", "수호 본능", "불굴의 의지"],
        "마법": ["원소 마스터", "마력 조절", "정령 소통", "시간 조작"],
        "지원": ["파티 지원", "치유 전문가", "신성 가호", "음악 재능"],
        "속도": ["6단계 완전체", "정밀함", "집중력", "그림자 조작"],
        "생존": ["생명력 조작", "치유술", "자연 소통", "영적 보호"],
        "스택": ["검기 조작", "투기장의 경험", "공간 조작", "분석 능력"],
        "특수": ["영혼 조작", "시간 조작", "기계 조작", "논리적 사고"],
        "팀워크": ["파티 지원", "기사도 정신", "신성한 보호", "음악 재능"]
    }

    def create_question_based_party(self, party_size: int = 4) -> List[Character]:
        """질문 기반 파티 추천 시스템 - 커서 메뉴 버전"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            print(f"\n{CYAN}🎯 질문 기반 파티 추천 시스템{RESET}")
            print(f"{WHITE}8가지 질문에 답하시면 맞춤형 파티를 추천해드립니다!{RESET}")
            print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            
            # 랜덤으로 8개 질문 선택
            num_questions = min(8, len(self.PARTY_QUESTIONS))
            selected_questions = random.sample(self.PARTY_QUESTIONS, num_questions)
            user_tags = []
            
            for i, question_data in enumerate(selected_questions, 1):
                # 커서 메뉴로 질문과 답변 표시
                options = [answer['text'] for answer in question_data['answers']]
                
                # 질문과 진행상황을 포함한 제목
                title = f"질문 {i}/{num_questions}: {question_data['question']}"
                
                # 커서 메뉴 생성
                menu = CursorMenu(
                    title=title,
                    options=options,
                    cancellable=True
                )
                
                # 선택 받기
                result = menu.run()
                
                if result is None:  # 취소된 경우
                    print(f"\n{RED}❌ 파티 추천 취소{RESET}")
                    return None
                
                # 선택된 답변의 태그 추가
                selected_answer = question_data['answers'][result]
                user_tags.extend(selected_answer['tags'])
                print(f"{MAGENTA}→ 선택: {selected_answer['text']}{RESET}")
            
            # 태그 분석하여 파티 구성
            print(f"\n{CYAN}🤔 답변을 분석중...{RESET}")
            recommended_party = self._analyze_tags_and_build_party(user_tags, party_size)
            
            # 생성된 파티 정보 표시
            if recommended_party:
                self._display_party_summary(recommended_party)
                # 동적 난이도 시스템 업데이트
                self._update_difficulty_scaling(recommended_party)
            
            print(f"\n{GREEN}✨ 맞춤형 파티가 완성되었습니다!{RESET}")
            return recommended_party
            
        except ImportError:
            # 커서 메뉴를 사용할 수 없는 경우 기존 방식 사용
            return self.create_question_based_party_fallback(party_size)
    
    def create_question_based_party_fallback(self, party_size: int = 4) -> List[Character]:
        """질문 기반 파티 추천 시스템 - 기본 버전 (폴백)"""
        print(f"\n{CYAN}🎯 질문 기반 파티 추천 시스템{RESET}")
        print(f"{WHITE}8가지 질문에 답하시면 맞춤형 파티를 추천해드립니다!{RESET}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        # 랜덤으로 8개 질문 선택
        num_questions = min(8, len(self.PARTY_QUESTIONS))
        selected_questions = random.sample(self.PARTY_QUESTIONS, num_questions)
        user_tags = []
        
        for i, question_data in enumerate(selected_questions, 1):
            print(f"\n{GREEN}질문 {i}/{num_questions}: {question_data['question']}{RESET}")
            print()
            
            # 답변 선택지 표시
            for j, answer in enumerate(question_data['answers'], 1):
                print(f"  {j}. {answer['text']}")
            
            print(f"\n{BLUE}선택하세요 (1-{len(question_data['answers'])}): {RESET}", end="")
            
            # 사용자 입력 받기
            while True:
                try:
                    choice = self.keyboard.get_key()
                    if choice.isdigit():
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(question_data['answers']):
                            selected_answer = question_data['answers'][choice_num - 1]
                            user_tags.extend(selected_answer['tags'])
                            print(f"{choice_num}")
                            print(f"{MAGENTA}→ {selected_answer['text']}{RESET}")
                            break
                    print(f"\n{RED}잘못된 입력입니다. 1-{len(question_data['answers'])} 중에서 선택해주세요: {RESET}", end="")
                except KeyboardInterrupt:
                    print(f"\n{RED}❌ 파티 추천 취소{RESET}")
                    return None
        
        # 태그 분석하여 파티 구성
        print(f"\n{CYAN}🤔 답변을 분석중...{RESET}")
        recommended_party = self._analyze_tags_and_build_party(user_tags, party_size)
        
        print(f"\n{GREEN}✨ 맞춤형 파티가 완성되었습니다!{RESET}")
        return recommended_party
    
    def _analyze_tags_and_build_party(self, user_tags: List[str], party_size: int) -> List[Character]:
        """태그 분석하여 파티 구성"""
        # 태그별 점수 계산
        class_scores = {}
        trait_scores = {}
        
        # 모든 직업 초기화
        for class_name in self.ALL_CLASSES:
            class_scores[class_name] = 0
        
        # 태그별 점수 부여
        for tag in user_tags:
            # 직업 점수
            if tag in self.TAG_TO_CLASSES:
                for class_name in self.TAG_TO_CLASSES[tag]:
                    class_scores[class_name] += 1
            
            # 특성 점수
            if tag in self.TAG_TO_TRAITS:
                for trait_name in self.TAG_TO_TRAITS[tag]:
                    trait_scores[trait_name] = trait_scores.get(trait_name, 0) + 1
        
        # 역할 균형 보정
        selected_classes = []
        used_roles = set()
        
        # 점수 순으로 정렬
        sorted_classes = sorted(class_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 역할 다양성을 고려하여 선택
        for class_name, score in sorted_classes:
            if len(selected_classes) >= party_size:
                break
            
            # 현재 직업의 역할 확인
            class_role = self._get_character_role(class_name)
            
            # 같은 역할이 너무 많으면 패스 (최대 2명)
            role_count = sum(1 for selected in selected_classes if self._get_character_role(selected) == class_role)
            if role_count >= 2:
                continue
            
            selected_classes.append(class_name)
            used_roles.add(class_role)
        
        # 역할이 부족하면 보완
        while len(selected_classes) < party_size:
            missing_roles = set(["탱커", "딜러", "마법사", "서포터"]) - used_roles
            if missing_roles:
                missing_role = random.choice(list(missing_roles))
                available_for_role = [c for c in self.ROLE_CLASSES.get(missing_role, []) 
                                    if c not in selected_classes]
                if available_for_role:
                    selected_classes.append(random.choice(available_for_role))
                    used_roles.add(missing_role)
                else:
                    # 사용 가능한 직업이 없으면 아무거나 추가
                    remaining = [c for c in self.ALL_CLASSES if c not in selected_classes]
                    if remaining:
                        selected_classes.append(random.choice(remaining))
            else:
                # 모든 역할이 있으면 아무거나 추가
                remaining = [c for c in self.ALL_CLASSES if c not in selected_classes]
                if remaining:
                    selected_classes.append(random.choice(remaining))
                else:
                    break
        
        # 캐릭터 생성
        party_members = []
        self._used_names = set()  # 이름 중복 방지 초기화
        
        for i, class_name in enumerate(selected_classes):
            character = self._create_character(class_name, i + 1)
            
            # 사용자가 직접 특성 선택 (AI 추천 기반 힌트 제공)
            self._ai_assisted_select_passives(character, user_tags)
            
            # 시작 장비 제공
            self._provide_starting_equipment(character)
            
            party_members.append(character)
        
        # 파티 분석
        self._analyze_question_based_party(party_members, user_tags)
        
        # 🌟 패시브 효과 선택
        selected_passives = self.select_party_passives(party_members, user_tags)
        
        # 파티에 패시브 정보 저장 (게임에서 적용할 수 있도록)
        for member in party_members:
            if not hasattr(member, 'party_passives'):
                member.party_passives = selected_passives
        
        # 🎁 모든 캐릭터에게 스타팅 아이템 지급
        self._give_starting_items_to_party(party_members)
        
        return party_members
    
    def _auto_select_traits_by_tags(self, character: Character, user_tags: List[str], trait_scores: Dict[str, int]):
        """질문 태그 기반 특성 자동 선택 (개발 모드에서는 2개 선택)"""
        print(f"\n{CYAN}🎯 {character.name}의 특성 선택 중...{RESET}")
        
        if not character.available_traits:
            print(f"{YELLOW}  ⚠️ 사용 가능한 특성이 없습니다{RESET}")
            return
        
        # 개발 모드 확인
        try:
            from config import game_config
            is_dev_mode = hasattr(game_config, 'DEVELOPMENT_MODE') and game_config.DEVELOPMENT_MODE
        except:
            is_dev_mode = False
        
        # 개발 모드가 아닌 경우 해금된 특성만 선택 가능
        if not is_dev_mode:
            unlocked_traits = character._get_unlocked_traits()
            available_indices = []
            for i, trait in enumerate(character.available_traits):
                if trait.name in unlocked_traits:
                    available_indices.append(i)
            
            if not available_indices:
                character.select_passive_traits([])
                return
            
            # 해금된 특성 중에서 1개 선택
            self._select_best_trait_combination(character, available_indices, user_tags, trait_scores)
        else:
            # 개발 모드: 질문 태그 + 직업 특성을 모두 고려하여 2개 선택
            trait_priority_scores = {}
            
            # 기본 직업 특성 우선순위
            class_priorities = self._get_trait_priorities(character.character_class)
            
            for i, trait in enumerate(character.available_traits):
                score = 0
                
                # 직업별 기본 우선순위
                if trait.name in class_priorities:
                    score += class_priorities[trait.name]
                
                # 질문 태그 기반 보너스
                if trait.name in trait_scores:
                    score += trait_scores[trait.name] * 3  # 질문 기반 가중치
                
                # 사용자 태그와 특성 연관성 체크
                for tag in user_tags:
                    if tag in self.TAG_TO_TRAITS and trait.name in self.TAG_TO_TRAITS[tag]:
                        score += 2
                
                trait_priority_scores[i] = score
            
            # 개발 모드에서는 2개 선택
            available_indices = list(range(len(character.available_traits)))
            self._select_best_trait_combination_dev_mode(character, available_indices, user_tags, trait_scores, trait_priority_scores)
    
    def _select_best_trait_combination(self, character: Character, available_indices: List[int], 
                                     user_tags: List[str], trait_scores: Dict[str, int], 
                                     priority_scores: Dict[int, int] = None):
        """최적의 특성 선택 (코스트 시스템 제거)"""
        if not available_indices:
            character.select_passive_traits([])
            return
        
        # 우선순위 점수가 없으면 기본 계산
        if priority_scores is None:
            priority_scores = {}
            class_priorities = self._get_trait_priorities(character.character_class)
            
            for i in available_indices:
                trait = character.available_traits[i]
                score = class_priorities.get(trait.name, 0)
                
                # 질문 태그 기반 보너스
                if trait.name in trait_scores:
                    score += trait_scores[trait.name] * 3
                
                for tag in user_tags:
                    if tag in self.TAG_TO_TRAITS and trait.name in self.TAG_TO_TRAITS[tag]:
                        score += 2
                
                priority_scores[i] = score
        
        # 가장 높은 점수의 특성 1개 선택
        if available_indices:
            best_trait = max(available_indices, key=lambda i: priority_scores.get(i, 0))
            character.select_passive_traits([best_trait])
            trait_name = character.available_traits[best_trait].name
            print(f"{GREEN}  ✅ {character.name} - 선택된 특성: {trait_name}{RESET}")
        else:
            character.select_passive_traits([])
            print(f"{YELLOW}  ⚠️ {character.name} - 선택된 특성 없음{RESET}")

    def select_party_passives(self, party: List[Character], user_tags: List[str]):
        """질문 기반 파티에 맞는 패시브 선택"""
        print(f"\n{GREEN}=== 🌟 파티 패시브 효과 선택 ==={RESET}")
        
        # 🌟 완전 리메이크된 창의적 패시브 시스템
        all_passive_effects = [
            # === 1코스트 패시브 (기초 효과) ===
            {
                "name": "첫걸음의 용기", 
                "description": "첫 번째 전투에서 모든 능력치 +50%",
                "effect_type": "first_battle_boost",
                "effect_value": {"all_stats": 0.50},
                "cost": 1,
                "unlock_cost": 0,
                "rarity": "common"
            },
            {
                "name": "미니멀리스트", 
                "description": "인벤토리 50% 이하일 때 SPD +15%, 회피율 +10%",
                "effect_type": "minimalist",
                "effect_value": {"speed_bonus": 0.15, "dodge_bonus": 0.10, "inventory_threshold": 0.50},
                "cost": 1,
                "unlock_cost": 0,
                "rarity": "common"
            },
            {
                "name": "새벽의 집중", 
                "description": "전투 첫 턴에 행동속도 +100%",
                "effect_type": "dawn_focus",
                "effect_value": {"first_turn_speed": 1.00},
                "cost": 1,
                "unlock_cost": 0,
                "rarity": "common"
            },
            {
                "name": "절약 정신", 
                "description": "아이템 사용 시 25% 확률로 소모하지 않음",
                "effect_type": "conservation",
                "effect_value": {"save_chance": 0.25},
                "cost": 1,
                "unlock_cost": 0,
                "rarity": "common"
            },
            {
                "name": "행운의 동전", 
                "description": "골드 습득 시 10% 확률로 2배",
                "effect_type": "lucky_coin",
                "effect_value": {"double_chance": 0.10},
                "cost": 1,
                "unlock_cost": 0,
                "rarity": "common"
            },
            
            # === 2코스트 패시브 (응용 효과) ===
            {
                "name": "역전의 명수", 
                "description": "HP 25% 이하일 때 크리티컬 확률 +30%",
                "effect_type": "comeback_master",
                "effect_value": {"crit_bonus": 0.30, "hp_threshold": 0.25},
                "cost": 2,
                "unlock_cost": 0,
                "rarity": "common"
            },
            {
                "name": "모험가의 직감", 
                "description": "숨겨진 문 발견율 +40%, 함정 감지 +25%",
                "effect_type": "adventurer_instinct",
                "effect_value": {"secret_find": 0.40, "trap_detect": 0.25},
                "cost": 2,
                "unlock_cost": 0,
                "rarity": "common"
            },
            {
                "name": "연쇄 반응", 
                "description": "크리티컬 히트 시 다음 공격 데미지 +20% (3회 중첩)",
                "effect_type": "chain_reaction",
                "effect_value": {"damage_boost": 0.20, "max_stacks": 3},
                "cost": 2,
                "unlock_cost": 0,
                "rarity": "common"
            },
            {
                "name": "수집가의 눈", 
                "description": "레어 아이템 발견율 +20%, 중복 아이템 시 골드 보너스 +50%",
                "effect_type": "collector_eye",
                "effect_value": {"rare_find": 0.20, "duplicate_bonus": 0.50},
                "cost": 2,
                "unlock_cost": 0,
                "rarity": "common"
            },
            {
                "name": "일사천리", 
                "description": "같은 스킬 연속 사용 시 MP 소모 -10% (최대 -50%)",
                "effect_type": "momentum",
                "effect_value": {"mp_reduction": 0.10, "max_reduction": 0.50},
                "cost": 2,
                "unlock_cost": 30,
                "rarity": "uncommon"
            },
            {
                "name": "위기 대응", 
                "description": "상태이상 걸릴 때 즉시 HP 15% 회복",
                "effect_type": "crisis_response",
                "effect_value": {"heal_percent": 0.15},
                "cost": 2,
                "unlock_cost": 40,
                "rarity": "uncommon"
            },
            
            # === 3코스트 패시브 (전략적 효과) ===
            {
                "name": "완벽주의자", 
                "description": "풀 HP/MP일 때 모든 행동 효과 +25%",
                "effect_type": "perfectionist",
                "effect_value": {"effect_boost": 0.25},
                "cost": 3,
                "unlock_cost": 50,
                "rarity": "uncommon"
            },
            {
                "name": "도박꾼의 심리", 
                "description": "공격/스킬 사용 시 10% 확률로 2배 효과, 5% 확률로 실패",
                "effect_type": "gambler_mind",
                "effect_value": {"double_chance": 0.10, "fail_chance": 0.05},
                "cost": 3,
                "unlock_cost": 60,
                "rarity": "uncommon"
            },
            {
                "name": "시너지 마스터", 
                "description": "파티원과 같은 타겟 공격 시 데미지 +35%",
                "effect_type": "synergy_master",
                "effect_value": {"synergy_damage": 0.35},
                "cost": 3,
                "unlock_cost": 70,
                "rarity": "uncommon"
            },
            {
                "name": "변화의 달인", 
                "description": "매 5턴마다 랜덤 능력치 +50% (1턴 지속)",
                "effect_type": "change_master",
                "effect_value": {"stat_boost": 0.50, "interval": 5, "duration": 1},
                "cost": 3,
                "unlock_cost": 80,
                "rarity": "uncommon"
            },
            {
                "name": "역학 관계", 
                "description": "아군이 죽을 때마다 생존 파티원 모든 능력치 +15% (누적)",
                "effect_type": "dynamic_relationship",
                "effect_value": {"stat_per_death": 0.15},
                "cost": 3,
                "unlock_cost": 90,
                "rarity": "uncommon"
            },
            
            # === 4-10코스트 고급 패시브들 (일부만 표시) ===
            {
                "name": "뱀파이어 본능", 
                "description": "적 처치 시 최대 HP의 30% 회복, 상처도 25% 치료",
                "effect_type": "vampire_instinct",
                "effect_value": {"hp_restore": 0.30, "wound_heal": 0.25},
                "cost": 4,
                "unlock_cost": 100,
                "rarity": "rare"
            },
            {
                "name": "분신술", 
                "description": "치명타 시 15% 확률로 즉시 한 번 더 행동",
                "effect_type": "shadow_clone",
                "effect_value": {"extra_action_chance": 0.15},
                "cost": 5,
                "unlock_cost": 150,
                "rarity": "rare"
            },
            {
                "name": "불사조의 심장", 
                "description": "죽음 시 50% HP로 부활 + 3턴간 무적 (1회/층)",
                "effect_type": "phoenix_heart",
                "effect_value": {"revive_hp": 0.50, "invincible_turns": 3, "uses_per_floor": 1},
                "cost": 6,
                "unlock_cost": 200,
                "rarity": "epic"
            },
            {
                "name": "만물 동조", 
                "description": "모든 스킬이 모든 스탯을 사용 (물리/마법/치유 등 모든 효과 혼합)",
                "effect_type": "universal_sync",
                "effect_value": {"all_stat_scaling": True},
                "cost": 7,
                "unlock_cost": 300,
                "rarity": "legendary"
            },
            {
                "name": "현실 편집", 
                "description": "전투 중 1회 모든 상태를 원하는 대로 변경 가능",
                "effect_type": "reality_edit",
                "effect_value": {"edit_per_battle": 1},
                "cost": 8,
                "unlock_cost": 450,
                "rarity": "mythic"
            },
            {
                "name": "절대 법칙", 
                "description": "모든 행동이 절대 실패하지 않음 + 모든 확률이 최대값",
                "effect_type": "absolute_law",
                "effect_value": {"no_failure": True, "max_probability": True},
                "cost": 10,
                "unlock_cost": 600,
                "rarity": "mythic"
            }
        ]
        
        # 🎯 패시브 개수 제한 시스템 (최대 6개)
        MAX_PASSIVE_COUNT = 6
        
        # 태그 기반 패시브 추천
        recommended_passives = self._get_recommended_passives_by_tags(user_tags, all_passive_effects)
        
        # 자동 선택된 패시브들 표시
        print(f"{BLUE}🎯 당신의 플레이 성향에 맞는 추천 패시브:{RESET}")
        
        selected_passives = []
        total_cost = 0
        
        # 코스트가 낮은 것부터 우선 선택
        recommended_passives.sort(key=lambda x: x['cost'])
        
        for passive in recommended_passives:
            if len(selected_passives) >= MAX_PASSIVE_COUNT:
                break
            if total_cost + passive['cost'] <= 15:  # 15코스트 제한
                selected_passives.append(passive)
                total_cost += passive['cost']
                
                rarity_colors = {
                    "common": "⚪", "uncommon": "💚", "rare": "💙", 
                    "epic": "💜", "legendary": "🧡", "mythic": "❤️"
                }
                color = rarity_colors.get(passive['rarity'], '⚪')
                
                print(f"  {color} {passive['name']} [{passive['cost']}코스트] - {passive['description']}")
        
        print(f"\n{GREEN}선택된 패시브: {len(selected_passives)}개, 총 코스트: {total_cost}/15{RESET}")
        
        return selected_passives
    
    def _get_recommended_passives_by_tags(self, user_tags: List[str], all_passives: List[dict]) -> List[dict]:
        """태그에 따른 패시브 추천"""
        recommended = []
        
        # 태그별 선호 패시브 매핑
        tag_to_passives = {
            "공격적": ["역전의 명수", "연쇄 반응", "뱀파이어 본능", "분신술"],
            "방어": ["위기 대응", "불사조의 심장", "완벽주의자"],
            "속도": ["새벽의 집중", "일사천리", "미니멀리스트"],
            "마법": ["만물 동조", "원소 순환", "시공간 왜곡"],
            "생존": ["불사조의 심장", "위기 대응", "뱀파이어 본능"],
            "탐험": ["모험가의 직감", "수집가의 눈", "보물 자석"],
            "팀워크": ["시너지 마스터", "역학 관계", "변화의 달인"],
            "행운": ["행운의 동전", "도박꾼의 심리", "운명 조작"],
            "완벽": ["완벽주의자", "절대 법칙", "현실 편집"]
        }
        
        # 사용자 태그에 맞는 패시브 수집
        for tag in user_tags:
            if tag in tag_to_passives:
                for passive_name in tag_to_passives[tag]:
                    matching_passive = next((p for p in all_passives if p['name'] == passive_name), None)
                    if matching_passive and matching_passive not in recommended:
                        recommended.append(matching_passive)
        
        # 기본 패시브들도 일부 추가 (코스트가 낮은 것들)
        basic_passives = ["첫걸음의 용기", "절약 정신", "모험가의 직감"]
        for name in basic_passives:
            passive = next((p for p in all_passives if p['name'] == name), None)
            if passive and passive not in recommended:
                recommended.append(passive)
        
        return recommended[:10]  # 최대 10개 추천
    
    def _analyze_question_based_party(self, party: List[Character], user_tags: List[str]):
        """질문 기반 파티 분석 및 표시"""
        print(f"\n{GREEN}=== 질문 기반 맞춤 파티 ==={RESET}")
        
        # 사용자 성향 분석 표시
        print(f"{MAGENTA}🎯 당신의 플레이 성향:{RESET}")
        tag_counts = {}
        for tag in user_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 상위 태그들을 한국어로 변환하여 표시
        tag_translations = {
            "속도": "빠른 전투", "딜러": "공격 중심", "방어": "안정 중심", "마법": "마법 선호",
            "서포터": "지원 선호", "특수": "독특한 기믹", "스택": "전략적 관리", "팀워크": "협력 중시",
            "공격적": "적극적 성향", "신중": "신중한 성향", "분석": "분석적 사고", "생존": "생존 중시"
        }
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:4]
        for tag, count in top_tags:
            korean_tag = tag_translations.get(tag, tag)
            print(f"  ✨ {korean_tag} ({count}회 선택)")
        
        print()
        
        # 파티 구성 표시
        for i, character in enumerate(party, 1):
            role = self._get_character_role(character.character_class)
            passives = [trait.name for trait in character.active_traits]
            
            # 직업 기믹 정보 추가
            mechanic_info = ""
            if character.character_class in self.CLASS_MECHANICS:
                mechanic = self.CLASS_MECHANICS[character.character_class]
                mechanic_info = f" [{mechanic['display']}]"
            
            print(f"{WHITE}{i}. {character.name}{RESET}")
            print(f"   직업: {CYAN}{character.character_class}{RESET} ({role}){mechanic_info}")
            print(f"   특성: {YELLOW}{', '.join(passives) if passives else '없음'}{RESET}")
            print()
        
        # 파티 시너지 및 추천 이유
        print(f"{BLUE}🎯 이 파티가 추천된 이유:{RESET}")
        
        # 역할 균형 분석
        roles = self._analyze_roles([c.character_class for c in party])
        balanced_roles = [role for role, count in roles.items() if count > 0]
        if len(balanced_roles) >= 3:
            print(f"  ✅ 균형잡힌 역할 구성: {', '.join(balanced_roles)}")
        
        # 시너지 확인
        synergies = self._check_synergies(party)
        if synergies:
            print(f"  ✨ 파티 시너지 발견:")
            for synergy in synergies[:2]:  # 최대 2개만 표시
                print(f"    • {synergy}")
        
        # 플레이 스타일 매칭
        style_match = []
        if "공격적" in user_tags or "딜러" in user_tags:
            attackers = [c for c in party if self._get_character_role(c.character_class) in ["딜러", "하이브리드"]]
            if len(attackers) >= 2:
                style_match.append("공격적인 플레이 스타일에 적합")
        
        if "방어" in user_tags or "생존" in user_tags:
            defenders = [c for c in party if self._get_character_role(c.character_class) in ["탱커", "서포터"]]
            if len(defenders) >= 2:
                style_match.append("안정적인 플레이 스타일에 적합")
        
        if "마법" in user_tags:
            mages = [c for c in party if self._get_character_role(c.character_class) == "마법사"]
            if mages:
                style_match.append("마법 중심 플레이에 최적화")
        
        for match in style_match:
            print(f"  🎮 {match}")
        
        print(f"\n{GREEN}맞춤형 파티 구성 완료! 🎉{RESET}")
    
    def display_class_mechanics(self, class_name: str):
        """직업별 고유 기믹 표시"""
        if class_name not in self.CLASS_MECHANICS:
            return
        
        mechanic = self.CLASS_MECHANICS[class_name]
        print(f"\n{CYAN}🔧 {class_name} 고유 기믹:{RESET}")
        print(f"  타입: {YELLOW}{mechanic['type']}{RESET}")
        print(f"  표시명: {GREEN}{mechanic['display']}{RESET}")
        print(f"  최대값: {BLUE}{mechanic['max']}{RESET}")
        print(f"  설명: {WHITE}{mechanic['description']}{RESET}")

    def create_balanced_party(self, user_selected: List[str] = None, party_size: int = 4, auto_select_traits: bool = False) -> List[Character]:
        """밸런스 잡힌 파티 생성 (개선된 다양성 알고리즘)"""
        if user_selected is None:
            user_selected = []
        
        # 사용자 선택 저장
        self.last_user_selection = user_selected.copy()
        
        # 이름 중복 방지를 위해 사용된 이름 초기화
        self._used_names = set()
        
        # 사용자 선택 캐릭터 검증
        validated_selected = []
        for class_name in user_selected:
            if class_name in self.ALL_CLASSES:
                validated_selected.append(class_name)
            else:
                print(f"{YELLOW}경고: '{class_name}'는 유효하지 않은 직업입니다.{RESET}")
        
        print(f"\n{CYAN}=== 자동 파티 구성 시작 ==={RESET}")
        if validated_selected:
            print(f"{GREEN}사용자 선택: {', '.join(validated_selected)}{RESET}")
        
        # 다양성 보장을 위한 다중 시도 시스템
        best_party_classes = None
        max_diversity_score = -1
        
        # 최대 5번 시도하여 가장 다양한 조합 선택
        for attempt in range(5):
            try_party_classes = self._select_party_classes(validated_selected, party_size)
            diversity_score = self._calculate_diversity_score(try_party_classes)
            
            if diversity_score > max_diversity_score:
                max_diversity_score = diversity_score
                best_party_classes = try_party_classes
            
            # 완벽한 다양성(모두 다른 직업)이면 즉시 선택
            if len(set(try_party_classes)) == len(try_party_classes):
                best_party_classes = try_party_classes
                break
        
        party_classes = best_party_classes
        print(f"{BLUE}다양성 점수: {max_diversity_score}/100{RESET}")
        
        party_members = []
        
        for i, class_name in enumerate(party_classes):
            character = self._create_character(class_name, i + 1)
            
            # 이름 커스터마이징 (auto_select_traits가 False인 경우)
            if not auto_select_traits:
                self._allow_name_customization(character)
            
            # 특성 선택 처리
            if auto_select_traits:
                self._auto_select_passives(character)
            else:
                # 사용자가 직접 특성 선택
                self._manual_select_passives(character)
                
            # 시작 장비 제공
            self._provide_starting_equipment(character)
            
            party_members.append(character)
        
        # 파티 분석 및 시너지 확인
        self._analyze_party(party_members)
        
        # Easy Character Creator에서 확인을 처리하므로 여기서는 생략
        # self._offer_regeneration_option(party_members)
        
        return party_members
    
    def regenerate_party(self, party_size: int = 4) -> List[Character]:
        """파티 재생성 (마지막 사용자 선택 유지)"""
        print(f"\n{CYAN}🔄 파티 재생성 중...{RESET}")
        return self.create_balanced_party(self.last_user_selection, party_size)
    
    def _offer_regeneration_option(self, current_party: List[Character]):
        """파티 재생성 옵션 제공"""
        print(f"\n{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{WHITE}파티가 마음에 드시나요?{RESET}")
        print(f"{GREEN}✅ Enter: 이 파티로 진행{RESET}")
        print(f"{CYAN}🔄 R: 파티 재생성{RESET}")
        print(f"{RED}❌ Q: 종료{RESET}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        while True:
            try:
                choice = self.keyboard.get_key().lower()
                
                if choice == '' or choice == 'enter' or choice == '\r':
                    print(f"{GREEN}✅ 파티 확정!{RESET}")
                    break
                elif choice == 'r':
                    regenerated_party = self.regenerate_party()
                    return regenerated_party
                elif choice == 'q':
                    print(f"{RED}❌ 파티 생성 취소{RESET}")
                    return None
                else:
                    print(f"{RED}잘못된 입력입니다. Enter, R, 또는 Q를 입력해주세요.{RESET}")
            except KeyboardInterrupt:
                print(f"\n{RED}❌ 파티 생성 취소{RESET}")
                return None
    
    def _select_party_classes(self, user_selected: List[str], party_size: int) -> List[str]:
        """파티 직업 선택 (밸런스 고려 + 다양성 강화)"""
        remaining_slots = party_size - len(user_selected)
        available_classes = [c for c in self.ALL_CLASSES if c not in user_selected]
        
        if remaining_slots <= 0:
            return user_selected[:party_size]
        
        # 🎲 다양성 강화: 자주 선택되는 직업들을 피하기 위한 가중치 조정
        # 고정되는 직업들 (궁수, 암살자, 사무라이, 도적)의 가중치를 줄임
        overused_classes = ["궁수", "암살자", "사무라이", "도적"]
        underused_classes = ["기계공학자", "무당", "철학자", "연금술사", "차원술사", "바드", "몽크", "마검사"]
        
        # 현재 파티 역할 분석
        current_roles = self._analyze_roles(user_selected)
        needed_roles = self._determine_needed_roles(current_roles, remaining_slots)
        
        selected_classes = user_selected.copy()
        
        # 필요한 역할에 따라 캐릭터 선택 (다양성 가중치 적용)
        for role in needed_roles:
            if remaining_slots <= 0:
                break
                
            role_candidates = [c for c in self.ROLE_CLASSES.get(role, []) if c in available_classes]
            
            if role_candidates:
                # 🎯 다양성 기반 선택: 덜 사용되는 직업에 높은 가중치
                weighted_candidates = []
                for candidate in role_candidates:
                    weight = 1.0  # 기본 가중치
                    
                    if candidate in underused_classes:
                        weight *= 3.0  # 덜 사용되는 직업은 3배 가중치
                    elif candidate in overused_classes:
                        weight *= 0.3  # 자주 사용되는 직업은 30% 가중치
                    
                    # 시너지도 고려하되 다양성이 우선
                    synergy_score = self._calculate_synergy_score(candidate, selected_classes)
                    weight *= (1.0 + synergy_score * 0.2)  # 시너지는 20% 보너스만
                    
                    weighted_candidates.extend([candidate] * int(weight * 10))
                
                # 가중치 기반 랜덤 선택
                if weighted_candidates:
                    best_candidate = random.choice(weighted_candidates)
                else:
                    best_candidate = random.choice(role_candidates)
                    
                selected_classes.append(best_candidate)
                available_classes.remove(best_candidate)
                remaining_slots -= 1
        
        # 남은 슬롯은 다양성 우선 랜덤 선택
        while remaining_slots > 0 and available_classes:
            # 다양성 가중치 적용
            weighted_available = []
            for candidate in available_classes:
                weight = 1.0
                if candidate in underused_classes:
                    weight *= 2.5  # 덜 사용되는 직업 우선
                elif candidate in overused_classes:
                    weight *= 0.4  # 자주 사용되는 직업 회피
                weighted_available.extend([candidate] * int(weight * 10))
            
            if weighted_available:
                random_choice = random.choice(weighted_available)
            else:
                random_choice = random.choice(available_classes)
                
            selected_classes.append(random_choice)
            available_classes.remove(random_choice)
            remaining_slots -= 1
        
        return selected_classes
    
    def _calculate_synergy_score(self, candidate: str, current_party: List[str]) -> float:
        """후보 직업과 현재 파티 간의 시너지 점수 계산"""
        synergy_score = 0.0
        
        for member in current_party:
            # 시너지 조합 확인
            synergy_key1 = f"{member} + {candidate}"
            synergy_key2 = f"{candidate} + {member}"
            
            if synergy_key1 in self.SYNERGY_COMBINATIONS:
                synergy_score += 0.5
            elif synergy_key2 in self.SYNERGY_COMBINATIONS:
                synergy_score += 0.5
        
        return synergy_score
    
    def _analyze_roles(self, classes: List[str]) -> Dict[str, int]:
        """현재 파티의 역할 분석"""
        role_count = {"탱커": 0, "딜러": 0, "마법사": 0, "서포터": 0, "하이브리드": 0}
        
        for class_name in classes:
            for role, role_classes in self.ROLE_CLASSES.items():
                if class_name in role_classes:
                    role_count[role] += 1
                    break
        
        return role_count
    
    def _determine_needed_roles(self, current_roles: Dict[str, int], remaining_slots: int) -> List[str]:
        """필요한 역할 결정 (다양한 조합을 위한 개선된 로직)"""
        needed_roles = []
        
        # 파티 구성 패턴들 정의 (4인 파티 기준)
        composition_patterns = [
            # 밸런스형 (클래식)
            ["탱커", "딜러", "마법사", "서포터"],
            ["탱커", "딜러", "서포터", "서포터"],
            
            # 공격형 (딜러 중심)
            ["딜러", "딜러", "마법사", "서포터"],
            ["딜러", "딜러", "딜러", "서포터"],
            ["딜러", "마법사", "마법사", "서포터"],
            
            # 마법형 (마법사 중심)
            ["마법사", "마법사", "마법사", "서포터"],
            ["마법사", "마법사", "딜러", "서포터"],
            ["탱커", "마법사", "마법사", "서포터"],
            
            # 서포터형 (지원 중심)
            ["탱커", "딜러", "서포터", "서포터"],
            ["마법사", "서포터", "서포터", "서포터"],
            
            # 하이브리드형 (특수 조합)
            ["하이브리드", "딜러", "마법사", "서포터"],
            ["탱커", "하이브리드", "마법사", "서포터"],
            ["딜러", "딜러", "하이브리드", "서포터"],
            
            # 극한형 (도전적)
            ["탱커", "탱커", "딜러", "서포터"],
            ["딜러", "딜러", "딜러", "딜러"],  # 극딜파티
            ["마법사", "마법사", "마법사", "마법사"],  # 극마파티
        ]
        
        # 현재 파티 크기에 따라 패턴 선택
        total_party_size = sum(current_roles.values()) + remaining_slots
        
        # 랜덤하게 구성 패턴 선택
        selected_pattern = random.choice(composition_patterns)
        
        # 현재 파티에서 부족한 역할들 계산
        for role in selected_pattern:
            if len(needed_roles) >= remaining_slots:
                break
                
            current_count = current_roles.get(role, 0)
            needed_count = selected_pattern.count(role)
            already_added = needed_roles.count(role)
            
            if current_count + already_added < needed_count:
                needed_roles.append(role)
        
        # 남은 슬롯이 있으면 완전 랜덤 선택 (20% 확률로 예측 불가능한 조합)
        while len(needed_roles) < remaining_slots:
            if random.random() < 0.2:  # 20% 확률로 완전 랜덤
                all_roles = ["탱커", "딜러", "마법사", "서포터", "하이브리드"]
                needed_roles.append(random.choice(all_roles))
            else:
                # 부족한 핵심 역할 우선 추가
                missing_core_roles = []
                if current_roles["탱커"] == 0 and "탱커" not in needed_roles:
                    missing_core_roles.append("탱커")
                if current_roles["서포터"] == 0 and "서포터" not in needed_roles:
                    missing_core_roles.append("서포터")
                if current_roles["딜러"] == 0 and "딜러" not in needed_roles:
                    missing_core_roles.append("딜러")
                
                if missing_core_roles:
                    needed_roles.append(random.choice(missing_core_roles))
                else:
                    # 모든 핵심 역할이 있으면 랜덤 추가
                    preferred_roles = ["딜러", "마법사", "서포터"]  # 하이브리드는 희소성 유지
                    needed_roles.append(random.choice(preferred_roles))
        
        return needed_roles[:remaining_slots]
    
    def _select_best_candidate(self, candidates: List[str], current_party: List[str]) -> str:
        """시너지와 다양성을 고려한 최적 후보 선택 (개선된 알고리즘)"""
        if not candidates:
            return None
            
        # 30% 확률로 완전 랜덤 선택 (예측 불가능성 증가)
        if random.random() < 0.3:
            return random.choice(candidates)
        
        synergy_scores = {}
        
        for candidate in candidates:
            score = 0
            
            # 시너지 확인 (가중치 감소)
            for party_member in current_party:
                synergy_key1 = f"{party_member} + {candidate}"
                synergy_key2 = f"{candidate} + {party_member}"
                
                if synergy_key1 in self.SYNERGY_COMBINATIONS or synergy_key2 in self.SYNERGY_COMBINATIONS:
                    score += 5  # 10에서 5로 감소
            
            # 다양성 보너스 강화 (같은 직업이 없으면 큰 보너스)
            if candidate not in current_party:
                score += 15  # 5에서 15로 증가
            
            # 희소 직업 보너스 (하이브리드 직업들)
            rare_classes = ["암살자", "해적", "사무라이", "드루이드", "철학자", 
                           "검투사", "기사", "신관", "광전사"]
            if candidate in rare_classes:
                score += 10
            
            # 균형 보너스 - 특정 역할이 너무 많으면 페널티
            candidate_role = None
            for role, classes in self.ROLE_CLASSES.items():
                if candidate in classes:
                    candidate_role = role
                    break
            
            if candidate_role:
                role_count = sum(1 for member in current_party 
                               for role, classes in self.ROLE_CLASSES.items()
                               if member in classes and role == candidate_role)
                
                # 같은 역할이 2명 이상이면 페널티
                if role_count >= 2:
                    score -= 8
                elif role_count >= 1:
                    score -= 3
            
            synergy_scores[candidate] = score
        
        # 상위 50% 후보군에서 랜덤 선택 (다양성 증가)
        sorted_candidates = sorted(synergy_scores.items(), key=lambda x: x[1], reverse=True)
        top_half_count = max(1, len(sorted_candidates) // 2)
        top_candidates = [candidate for candidate, score in sorted_candidates[:top_half_count]]
        
        return random.choice(top_candidates)
    
    def _create_character(self, class_name: str, index: int) -> Character:
        """캐릭터 생성"""
        # 대폭 확장된 캐릭터 이름 풀 (300개 이상)
        character_names = [
            # 남성 이름 (150개)
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
            "세르겐", "빅터", "로만", "파벨", "녹티스", "아르템", "콘스탄틴", "발렌틴", "드미트리","티더","클라우드","프롬프토","그림니르","시스","랜슬롯",
            
            # 여성 이름 (150개)
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
        
        # 중복되지 않는 이름 선택
        available_names = [name for name in character_names if name not in self._used_names]
        if not available_names:
            # 모든 이름이 사용되었으면 초기화
            self._used_names.clear()
            available_names = character_names
        
        name = random.choice(available_names)
        self._used_names.add(name)
        
        # 직업별 기본 스탯 (레벨 10 기준)
        base_stats = self._get_class_base_stats(class_name)
        
        character = Character(
            name=name,
            character_class=class_name,
            max_hp=base_stats["hp"],
            physical_attack=base_stats["physical_attack"],
            magic_attack=base_stats["magic_attack"],
            physical_defense=base_stats["physical_defense"],
            magic_defense=base_stats["magic_defense"],
            speed=base_stats["speed"]
        )
        
        # 레벨 1로 설정
        character.level = 1
        
        return character
    
    def _get_class_base_stats(self, class_name: str) -> Dict[str, int]:
        """직업별 기본 스탯 (고정값으로 변경)"""
        # 직업별 고정 스탯 정의 (레벨 10 기준)
        fixed_stats = {
            "전사": {"hp": 216, "physical_attack": 75, "magic_attack": 43, "physical_defense": 63, "magic_defense": 48, "speed": 56},
            "아크메이지": {"hp": 121, "physical_attack": 43, "magic_attack": 78, "physical_defense": 33, "magic_defense": 67, "speed": 58},
            "궁수": {"hp": 164, "physical_attack": 74, "magic_attack": 33, "physical_defense": 44, "magic_defense": 43, "speed": 68},
            "도적": {"hp": 150, "physical_attack": 64, "magic_attack": 38, "physical_defense": 43, "magic_defense": 49, "speed": 93},
            "성기사": {"hp": 197, "physical_attack": 67, "magic_attack": 38, "physical_defense": 76, "magic_defense": 62, "speed": 43},
            "암흑기사": {"hp": 189, "physical_attack": 71, "magic_attack": 54, "physical_defense": 58, "magic_defense": 51, "speed": 52},
            "몽크": {"hp": 172, "physical_attack": 82, "magic_attack": 51, "physical_defense": 59, "magic_defense": 64, "speed": 76},
            "바드": {"hp": 107, "physical_attack": 43, "magic_attack": 66, "physical_defense": 38, "magic_defense": 58, "speed": 69},
            "네크로맨서": {"hp": 134, "physical_attack": 44, "magic_attack": 84, "physical_defense": 39, "magic_defense": 74, "speed": 48},
            "용기사": {"hp": 181, "physical_attack": 78, "magic_attack": 62, "physical_defense": 67, "magic_defense": 58, "speed": 61},
            "검성": {"hp": 164, "physical_attack": 83, "magic_attack": 31, "physical_defense": 51, "magic_defense": 47, "speed": 71},
            "정령술사": {"hp": 107, "physical_attack": 49, "magic_attack": 85, "physical_defense": 42, "magic_defense": 69, "speed": 59},
            "암살자": {"hp": 134, "physical_attack": 81, "magic_attack": 28, "physical_defense": 34, "magic_defense": 39, "speed": 87},
            "기계공학자": {"hp": 156, "physical_attack": 63, "magic_attack": 59, "physical_defense": 54, "magic_defense": 48, "speed": 53},
            "무당": {"hp": 121, "physical_attack": 48, "magic_attack": 86, "physical_defense": 44, "magic_defense": 77, "speed": 64},
            "해적": {"hp": 164, "physical_attack": 74, "magic_attack": 34, "physical_defense": 52, "magic_defense": 41, "speed": 77},
            "사무라이": {"hp": 167, "physical_attack": 74, "magic_attack": 45, "physical_defense": 58, "magic_defense": 53, "speed": 67},
            "드루이드": {"hp": 175, "physical_attack": 53, "magic_attack": 81, "physical_defense": 48, "magic_defense": 69, "speed": 59},
            "철학자": {"hp": 107, "physical_attack": 38, "magic_attack": 76, "physical_defense": 54, "magic_defense": 86, "speed": 49},
            "시간술사": {"hp": 121, "physical_attack": 54, "magic_attack": 77, "physical_defense": 49, "magic_defense": 64, "speed": 57},
            "연금술사": {"hp": 135, "physical_attack": 59, "magic_attack": 72, "physical_defense": 44, "magic_defense": 58, "speed": 54},
            "검투사": {"hp": 172, "physical_attack": 79, "magic_attack": 41, "physical_defense": 56, "magic_defense": 48, "speed": 64},
            "기사": {"hp": 235, "physical_attack": 79, "magic_attack": 46, "physical_defense": 72, "magic_defense": 54, "speed": 48},
            "신관": {"hp": 143, "physical_attack": 42, "magic_attack": 79, "physical_defense": 57, "magic_defense": 89, "speed": 52},
            "마검사": {"hp": 164, "physical_attack": 67, "magic_attack": 70, "physical_defense": 54, "magic_defense": 61, "speed": 58},
            "차원술사": {"hp": 84, "physical_attack": 33, "magic_attack": 88, "physical_defense": 28, "magic_defense": 72, "speed": 47},
            "광전사": {"hp": 327, "physical_attack": 64, "magic_attack": 13, "physical_defense": 22, "magic_defense": 21, "speed": 74}
        }
        
        return fixed_stats.get(class_name, {
            "hp": 150, "physical_attack": 50, "magic_attack": 50, 
            "physical_defense": 50, "magic_defense": 50, "speed": 50
        })
    
    def _auto_select_passives(self, character: Character):
        """자동 패시브 선택 (2개 강제)"""
        if not character.available_traits:
            print(f"  {character.name}: 사용 가능한 특성이 없습니다.")
            return
        
        print(f"  {character.name}: 개발 모드 = {game_config.are_all_passives_unlocked()}")
        print(f"  {character.name}: 사용 가능한 특성 수 = {len(character.available_traits)}")
        
        # 개발 모드가 아닌 경우 해금된 패시브만 선택 가능
        if not game_config.are_all_passives_unlocked():
            unlocked_traits = character._get_unlocked_traits()
            available_indices = []
            for i, trait in enumerate(character.available_traits):
                if trait.name in unlocked_traits:
                    available_indices.append(i)
            
            # 해금된 패시브가 없으면 패시브 없이 진행
            if not available_indices:
                character.select_passive_traits([])
                return
            
            # 해금된 패시브 중에서 2개 선택 (가능한 만큼)
            num_to_select = min(2, len(available_indices))
            if num_to_select > 0:
                selected_indices = random.sample(available_indices, num_to_select)
                character.select_passive_traits(selected_indices)
            else:
                character.select_passive_traits([])
        else:
            # 개발 모드에서는 직업 특성을 고려한 패시브 선택 로직
            trait_priorities = self._get_trait_priorities(character.character_class)
            
            # 우선순위에 따라 정렬
            sorted_traits = []
            for i, trait in enumerate(character.available_traits):
                priority = trait_priorities.get(trait.name, 0)
                sorted_traits.append((i, trait, priority))  # 인덱스도 함께 저장
            
            sorted_traits.sort(key=lambda x: x[2], reverse=True)  # priority로 정렬
            
            # 항상 2개 선택 (사용 가능한 특성이 있다면)
            selected_indices = []
            
            if len(sorted_traits) >= 2:
                # 상위 2개 특성 선택
                selected_indices = [sorted_traits[0][0], sorted_traits[1][0]]
            elif len(sorted_traits) == 1:
                # 1개만 있으면 1개만 선택
                selected_indices = [sorted_traits[0][0]]
            
            # 패시브 적용
            character.select_passive_traits(selected_indices)
    
    def _get_trait_priorities(self, class_name: str) -> Dict[str, int]:
        """직업별 특성 우선순위 (Phase 1&2 신규 직업 포함 - 27개 직업) - 6단계 완전체 시스템"""
        priorities = {
            # 전사계 - 6단계 완전체 시스템 최적화
            "전사": {"6단계 완전체": 10, "전장의 지배자": 9, "균형감각": 8, "전투 본능": 7, "불굴의 의지": 6},
            "성기사": {"신성한 보호": 10, "빛의 축복": 9, "성역 마스터": 8, "신성 가호": 7, "치유술": 6},
            "암흑기사": {"생명력 조작": 10, "흡혈 강화": 9, "어둠의 가호": 8, "흡혈술": 7, "어둠 친화": 6},
            "기사": {"수호 본능": 10, "의무 마스터": 9, "창술 달인": 8, "기사도 정신": 7, "명예 수호": 6},
            "용기사": {"화염 강화": 10, "용의 유산": 9, "드래곤 마크": 8, "용의 혈통": 7, "화염 친화": 6},
            "검성": {"검기 조작": 10, "검기 장인": 9, "완벽한 검술": 8, "일섬 달인": 7, "검의 도": 6},
            "검투사": {"패링 마스터": 10, "투기장의 경험": 9, "생존 본능": 8, "투사의 긍지": 7, "콜로세움의 영웅": 6},
            "광전사": {"피의 갈증": 10, "광기의 힘": 9, "흡혈 강화": 8, "분노 제어": 7, "야생 본능": 6},
            
            # 원거리/물리계 - 정밀함과 기동성 중심 
            "궁수": {"정밀함": 10, "집중력": 9, "연속 사격": 8, "원거리 전문가": 7, "사냥꾼의 직감": 6},
            "도적": {"독왕의 권능": 10, "독술 지배": 9, "독 촉진": 8, "침묵 술": 7, "맹독 면역": 6},
            "암살자": {"그림자 조작": 10, "그림자 방어": 9, "그림자 강화": 8, "즉사술": 7, "치명타 특화": 6},
            "해적": {"이도류 달인": 10, "보물 감각": 9, "항해술": 8, "약탈 전문가": 7, "운명의 바람": 6},
            "사무라이": {"무사도 정신": 10, "거합 달인": 9, "명예 수호": 8, "검의 길": 7, "집중력": 6},
            
            # 마법계 - 원소와 마나 관리 중심
            "아크메이지": {"원소 마스터": 10, "마력 조절": 9, "원소 순환": 8, "번개 친화": 7, "마법 지식": 6},
            "네크로맨서": {"영혼 조작": 10, "죽음 친화": 9, "언데드 지배": 8, "생명 흡수": 7, "공포 유발": 6},
            "정령술사": {"원소 조작": 10, "정령 소통": 9, "원소 융합": 8, "자연 친화": 7, "마나 효율": 6},
            "시간술사": {"시간 조작": 10, "미래 예측": 9, "시공간 인식": 8, "시간 역행": 7, "인과 조작": 6},
            "연금술사": {"화학 지식": 10, "폭발 제어": 9, "물질 변환": 8, "연성술": 7, "실험 정신": 6},
            "차원술사": {"공간 조작": 10, "차원 이동": 9, "공간 인식": 8, "차원 균열": 7, "무한 지식": 6},
            
            # 하이브리드계 - 균형 잡힌 특성
            "몽크": {"내공술": 10, "연타 전문가": 9, "정신 수련": 8, "기 조절": 7, "참선의 깨달음": 6},
            "마검사": {"마검 조화": 10, "원소 검술": 9, "마법 검기": 8, "이중 수련": 7, "균형 감각": 6},
            "기계공학자": {"기계 조작": 10, "에너지 제어": 9, "로봇 공학": 8, "과학 지식": 7, "창의성": 6},
            
            # 서포터계 - 파티 지원과 치유 중심
            "바드": {"파티 지원": 10, "음악 재능": 9, "매혹술": 8, "정신 조작": 7, "카리스마": 6},
            "신관": {"치유 전문가": 10, "신성 가호": 9, "신앙심": 8, "축복술": 7, "정화": 6},
            "드루이드": {"자연 소통": 10, "동물 변신": 9, "자연 마법": 8, "생태 지식": 7, "식물 성장": 6},
            "무당": {"영혼 시야": 10, "정신 지배": 9, "귀신 소통": 8, "주술 지식": 7, "영적 보호": 6},
            "철학자": {"논리적 사고": 10, "진리 추구": 9, "지식 축적": 8, "설득술": 7, "학자의 직감": 6}
        }
        
        return priorities.get(class_name, {})
    
    def _analyze_party(self, party: List[Character]):
        """파티 분석 및 시너지 표시"""
        print(f"\n{GREEN}=== 생성된 파티 ==={RESET}")
        
        # 파티 구성 표시
        for i, character in enumerate(party, 1):
            role = self._get_character_role(character.character_class)
            passives = [trait.name for trait in character.active_traits]
            
            print(f"{WHITE}{i}. {character.name}{RESET}")
            print(f"   직업: {CYAN}{character.character_class}{RESET} ({role})")
            print(f"   레벨: {character.level}")
            print(f"   스탯: HP {character.max_hp}, 물공 {character.physical_attack}, 마공 {character.magic_attack}")
            print(f"   패시브: {YELLOW}{', '.join(passives)}{RESET}")
            print()
        
        # 역할 분석
        roles = self._analyze_roles([c.character_class for c in party])
        print(f"{BLUE}파티 역할 구성:{RESET}")
        for role, count in roles.items():
            if count > 0:
                print(f"  {role}: {count}명")
        
        # 시너지 확인
        synergies = self._check_synergies(party)
        if synergies:
            print(f"\n{MAGENTA}파티 시너지:{RESET}")
            for synergy in synergies:
                print(f"  ✨ {synergy}")
        
        print(f"\n{GREEN}파티 구성 완료! 🎉{RESET}")
    
    def _get_character_role(self, class_name: str) -> str:
        """캐릭터의 역할 반환"""
        for role, classes in self.ROLE_CLASSES.items():
            if class_name in classes:
                return role
        return "기타"
    
    def _check_synergies(self, party: List[Character]) -> List[str]:
        """파티 시너지 확인"""
        synergies = []
        party_classes = [c.character_class for c in party]
        
        for combination, info in self.SYNERGY_COMBINATIONS.items():
            classes = combination.split(" + ")
            if all(cls in party_classes for cls in classes):
                synergies.append(f"{combination}: {info['effect']}")
        
        return synergies
    
    def get_balanced_party_from_list(self, unlocked_names: List[str]) -> List[str]:
        """해금된 캐릭터 목록에서 균형잡힌 파티 구성 (이름만 반환)"""
        if len(unlocked_names) < 4:
            return unlocked_names
        
        # 역할별로 분류
        available_by_role = {role: [] for role in self.ROLE_CLASSES.keys()}
        
        for name in unlocked_names:
            for role, classes in self.ROLE_CLASSES.items():
                if name in classes:
                    available_by_role[role].append(name)
                    break
        
        # 균형잡힌 파티 구성 (각 역할에서 1명씩)
        selected = []
        
        # 탱커 1명
        if available_by_role["탱커"]:
            selected.append(random.choice(available_by_role["탱커"]))
        
        # 딜러 1명
        if available_by_role["딜러"]:
            selected.append(random.choice(available_by_role["딜러"]))
        
        # 마법사 1명
        if available_by_role["마법사"]:
            selected.append(random.choice(available_by_role["마법사"]))
        
        # 서포터 또는 하이브리드 1명
        support_pool = available_by_role["서포터"] + available_by_role["하이브리드"]
        if support_pool:
            selected.append(random.choice(support_pool))
        
        # 4명이 안 되면 나머지 해금된 캐릭터로 채우기
        remaining = [name for name in unlocked_names if name not in selected]
        while len(selected) < 4 and remaining:
            selected.append(remaining.pop(0))
        
        return selected[:4]
    
    def select_party_passive_effects(self):
        """파티 전체 패시브 효과 선택 - main.py와 동일한 시스템"""
        try:
            from game.cursor_menu_system import CursorMenu
            from game.color_text import bright_cyan, bright_yellow, yellow, green, red, bright_white, cyan, white
            
            # 🌟 완전 리메이크된 창의적 패시브 시스템 (1-10 코스트, 최대 3개 제한)
            all_passive_effects = [
                # === 1코스트 패시브 (기초 효과) ===
                {
                    "name": "첫걸음의 용기", 
                    "description": "첫 번째 전투에서 모든 능력치 +50%",
                    "effect_type": "first_battle_boost",
                    "effect_value": {"all_stats": 0.50},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "미니멀리스트", 
                    "description": "인벤토리 50% 이하일 때 SPD +15%, 회피율 +10%",
                    "effect_type": "minimalist",
                    "effect_value": {"speed_bonus": 0.15, "dodge_bonus": 0.10, "inventory_threshold": 0.50},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "새벽의 집중", 
                    "description": "전투 첫 턴에 행동속도 +100%",
                    "effect_type": "dawn_focus",
                    "effect_value": {"first_turn_speed": 1.00},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "절약 정신", 
                    "description": "아이템 사용 시 25% 확률로 소모하지 않음",
                    "effect_type": "conservation",
                    "effect_value": {"save_chance": 0.25},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "행운의 동전", 
                    "description": "골드 습득 시 10% 확률로 2배",
                    "effect_type": "lucky_coin",
                    "effect_value": {"double_chance": 0.10},
                    "cost": 1,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                
                # === 2코스트 패시브 (응용 효과) ===
                {
                    "name": "역전의 명수", 
                    "description": "HP 25% 이하일 때 크리티컬 확률 +30%",
                    "effect_type": "comeback_master",
                    "effect_value": {"crit_bonus": 0.30, "hp_threshold": 0.25},
                    "cost": 2,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "모험가의 직감", 
                    "description": "숨겨진 문 발견율 +40%, 함정 감지 +25%",
                    "effect_type": "adventurer_instinct",
                    "effect_value": {"secret_find": 0.40, "trap_detect": 0.25},
                    "cost": 2,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "연쇄 반응", 
                    "description": "크리티컬 히트 시 다음 공격 데미지 +20% (3회 중첩)",
                    "effect_type": "chain_reaction",
                    "effect_value": {"damage_boost": 0.20, "max_stacks": 3},
                    "cost": 2,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "수집가의 눈", 
                    "description": "레어 아이템 발견율 +20%, 중복 아이템 시 골드 보너스 +50%",
                    "effect_type": "collector_eye",
                    "effect_value": {"rare_find": 0.20, "duplicate_bonus": 0.50},
                    "cost": 2,
                    "unlock_cost": 0,
                    "rarity": "common"
                },
                {
                    "name": "일사천리", 
                    "description": "같은 스킬 연속 사용 시 MP 소모 -10% (최대 -50%)",
                    "effect_type": "momentum",
                    "effect_value": {"mp_reduction": 0.10, "max_reduction": 0.50},
                    "cost": 2,
                    "unlock_cost": 30,
                    "rarity": "uncommon"
                },
                {
                    "name": "위기 대응", 
                    "description": "상태이상 걸릴 때 즉시 HP 15% 회복",
                    "effect_type": "crisis_response",
                    "effect_value": {"heal_percent": 0.15},
                    "cost": 2,
                    "unlock_cost": 40,
                    "rarity": "uncommon"
                },
                
                # === 3코스트 패시브 (전략적 효과) ===
                {
                    "name": "완벽주의자", 
                    "description": "풀 HP/MP일 때 모든 행동 효과 +25%",
                    "effect_type": "perfectionist",
                    "effect_value": {"effect_boost": 0.25},
                    "cost": 3,
                    "unlock_cost": 50,
                    "rarity": "uncommon"
                },
                {
                    "name": "도박꾼의 심리", 
                    "description": "공격/스킬 사용 시 10% 확률로 2배 효과, 5% 확률로 실패",
                    "effect_type": "gambler_mind",
                    "effect_value": {"double_chance": 0.10, "fail_chance": 0.05},
                    "cost": 3,
                    "unlock_cost": 60,
                    "rarity": "uncommon"
                },
                {
                    "name": "시너지 마스터", 
                    "description": "파티원과 같은 타겟 공격 시 데미지 +35%",
                    "effect_type": "synergy_master",
                    "effect_value": {"synergy_damage": 0.35},
                    "cost": 3,
                    "unlock_cost": 70,
                    "rarity": "uncommon"
                }
            ]
            
            # 🎯 패시브 개수 제한 시스템 (최대 3개)
            MAX_PASSIVE_COUNT = 3
            current_max_cost = 3  # 기본 3코스트, 최대 10까지 확장 가능
            
            print(f"\n{bright_cyan('🌟 파티 패시브 효과 선택')}")
            print(f"{yellow('⚠️ 패시브는 최대 3개까지, 총 코스트 3 이내로 선택 가능합니다.')}")
            print(f"{cyan('💡 1-2코스트 패시브 조합으로 전략적인 구성을 해보세요!')}")
            
            selected_passives = []
            used_cost = 0
            
            while len(selected_passives) < MAX_PASSIVE_COUNT and used_cost < current_max_cost:
                # 선택 가능한 패시브들 (기본 3코스트 시스템에서 사용 가능한 것들만)
                available_passives = [p for p in all_passive_effects 
                                    if p not in selected_passives 
                                    and p['cost'] <= (current_max_cost - used_cost)
                                    and p['unlock_cost'] == 0]  # 기본 패시브만
                
                if not available_passives:
                    break
                
                # 커서 메뉴로 패시브 선택 (페이지네이션 적용)
                try:
                    # 페이지당 표시할 패시브 개수
                    PASSIVES_PER_PAGE = 8
                    total_pages = (len(available_passives) + PASSIVES_PER_PAGE - 1) // PASSIVES_PER_PAGE
                    current_page = 0
                    
                    while True:
                        # 현재 페이지의 패시브들
                        start_idx = current_page * PASSIVES_PER_PAGE
                        end_idx = min(start_idx + PASSIVES_PER_PAGE, len(available_passives))
                        page_passives = available_passives[start_idx:end_idx]
                        
                        options = []
                        descriptions = []
                        
                        # 현재 페이지의 패시브들 추가
                        for passive in page_passives:
                            cost = passive['cost']
                            rarity_color = {"common": "🔷", "uncommon": "🔶", "rare": "🔥", "epic": "💜", "legendary": "✨", "mythic": "💫"}
                            rarity_icon = rarity_color.get(passive.get('rarity', 'common'), "🔷")
                            
                            option_text = f"{rarity_icon} {passive['name']} [{cost}코스트]"
                            description = f"{passive['description']}"
                            
                            options.append(option_text)
                            descriptions.append(description)
                        
                        # 네비게이션 옵션들 추가
                        if total_pages > 1:
                            if current_page > 0:
                                options.append("⬅️ 이전 페이지")
                                descriptions.append("이전 페이지로 돌아갑니다")
                            if current_page < total_pages - 1:
                                options.append("➡️ 다음 페이지")
                                descriptions.append("다음 페이지로 이동합니다")
                        
                        # 선택 완료 옵션 추가
                        options.append("✅ 선택 완료 (패시브 없이 진행)")
                        descriptions.append("더 이상 패시브를 선택하지 않고 게임을 시작합니다")
                        
                        # 상태 정보 (페이지 정보 포함)
                        status_info = f"코스트: {used_cost}/{current_max_cost} | 개수: {len(selected_passives)}/{MAX_PASSIVE_COUNT}"
                        if total_pages > 1:
                            status_info += f" | 페이지: {current_page + 1}/{total_pages}"
                        
                        # 현재 선택된 패시브들 정보
                        selected_info = ""
                        if selected_passives:
                            selected_info = "\n선택된 패시브:\n"
                            for p in selected_passives:
                                selected_info += f"• {p['name']} [{p['cost']}코스트]\n"
                        
                        # 커서 메뉴 생성
                        menu = CursorMenu(
                            title=f"🌟 파티 패시브 효과 선택\n{status_info}{selected_info}",
                            options=options,
                            descriptions=descriptions,
                            cancellable=True
                        )
                        
                        result = menu.run()
                        
                        if result is None:  # 취소
                            return []
                        elif result < len(page_passives):  # 패시브 선택
                            selected_passive = page_passives[result]
                            selected_passives.append(selected_passive)
                            used_cost += selected_passive['cost']
                            
                            print(f"\n{GREEN}✅ {selected_passive['name']} 패시브가 선택되었습니다!{RESET}")
                            print(f"{CYAN}💡 {selected_passive['description']}{RESET}")
                            
                            if used_cost >= current_max_cost or len(selected_passives) >= MAX_PASSIVE_COUNT:
                                print(f"\n{YELLOW}🎯 제한에 도달했습니다!{RESET}")
                                break
                            break  # 패시브 선택 후 메인 루프로
                        else:
                            # 네비게이션 또는 완료 처리
                            nav_start = len(page_passives)
                            relative_choice = result - nav_start
                            
                            nav_options = []
                            if total_pages > 1:
                                if current_page > 0:
                                    nav_options.append("prev")
                                if current_page < total_pages - 1:
                                    nav_options.append("next")
                            nav_options.append("complete")
                            
                            if relative_choice < len(nav_options):
                                choice = nav_options[relative_choice]
                                if choice == "prev":
                                    current_page = max(0, current_page - 1)
                                elif choice == "next":
                                    current_page = min(total_pages - 1, current_page + 1)
                                elif choice == "complete":
                                    return selected_passives
                            
                    if used_cost >= current_max_cost or len(selected_passives) >= MAX_PASSIVE_COUNT:
                        break
                
                except ImportError:
                    # 커서 메뉴 없을 때 기존 방식 사용
                    print(f"\n{bright_white('사용 가능한 패시브 목록:')} (코스트: {used_cost}/{current_max_cost}, 개수: {len(selected_passives)}/{MAX_PASSIVE_COUNT})")
                    
                    options = []
                    for i, passive in enumerate(available_passives, 1):
                        cost = passive['cost']
                        print(f"{bright_yellow(f'{i}.')} {white(passive['name'])} [{cost}코스트] - {cyan(passive['description'])}")
                        options.append(str(i))
                    
                    print(f"{bright_yellow(f'{len(available_passives) + 1}.')} {white('선택 완료 (패시브 없이 진행)')}")
                    options.append(str(len(available_passives) + 1))
                    
                    choice = self.keyboard.get_key_input(f"\n{bright_white('선택하세요')}: ", options)
                    choice_idx = int(choice) - 1
                    
                    if choice_idx < len(available_passives):
                        # 패시브 선택
                        selected_passive = available_passives[choice_idx]
                        selected_passives.append(selected_passive)
                        used_cost += selected_passive['cost']
                        
                        print(f"\n{green('✅')} {bright_white(selected_passive['name'])} 패시브가 선택되었습니다!")
                        print(f"{cyan('💡')} {selected_passive['description']}")
                        
                        if used_cost >= current_max_cost or len(selected_passives) >= MAX_PASSIVE_COUNT:
                            print(f"\n{bright_yellow('🎯 제한에 도달했습니다!')}")
                            break
                    else:
                        # 선택 완료
                        break
                else:
                    # 선택 완료
                    break
            
            # 선택 결과 출력
            if selected_passives:
                print(f"\n{bright_cyan('='*50)}")
                print(f"{green('🎉 선택된 파티 패시브 효과:')}")
                for i, passive in enumerate(selected_passives, 1):
                    print(f"  {bright_yellow(f'{i}.')} {white(passive['name'])} - {cyan(passive['description'])}")
                print(f"{bright_cyan('='*50)}")
                
                # 패시브 효과를 파티에 저장 (실제 적용은 게임 내에서)
                return selected_passives
            else:
                print(f"\n{yellow('패시브 효과 없이 게임을 시작합니다.')}")
                return []
            
        except Exception as e:
            print(f"⚠️ 패시브 선택 시스템 오류: {e}")
            return []
    
    def _get_available_traits(self, job: str) -> List[str]:
        """직업별 사용 가능한 특성 목록 반환 - 6단계 완전체 시스템"""
        # 모든 특성 이름 리스트 (게임 시스템과 동기화 필요)
        all_traits = [
            # 전투 특성 - 6단계 완전체 포함
            "6단계 완전체", "전장의 지배자", "패링 마스터", "피의 갈증",
            "신성한 보호", "수호 본능", "불굴의 의지", "기사도 정신",
            "그림자 조작", "암살자의 직감", "독성 특화", "스텔스 마스터",
            
            # 마법 특성
            "원소 마스터", "마력 조절", "정령 소통", "시간 조작",
            "생명력 조작", "언데드 지배", "영혼 흡수", "어둠의 힘",
            "차원 여행", "공간 조작", "현실 왜곡", "차원의 문",
            
            # 지원 특성  
            "파티 지원", "치유 전문가", "신성 가호", "음악 재능",
            "자연 소통", "야생 형태", "동물 친화", "치유술",
            "기계 조작", "연금술 지식", "발명품 제작", "과학적 사고",
            
            # 특수 특성
            "영혼 조작", "정신력", "영적 보호", "무당의 지혜",
            "검기 조작", "투기장의 경험", "콤보 마스터", "격투 기술",
            "용의 혈통", "화염 저항", "드래곤 하트", "용의 비늘",
            "무사도 정신", "정밀함", "집중력", "완벽한 자세",
            "논리적 사고", "분석 능력", "철학적 사고", "진리 탐구",
            "광전사의 분노", "피의 축제", "광기의 힘", "파괴의 충동"
        ]
        
        # 직업별 특화 특성 (우선 순위가 높은 특성들) - 6단계 완전체 포함
        job_specific_traits = {
            "전사": ["6단계 완전체", "전장의 지배자", "패링 마스터", "피의 갈증"],
            "아크메이지": ["원소 마스터", "마력 조절", "정령 소통", "시간 조작"],
            "궁수": ["정밀함", "집중력", "완벽한 자세", "6단계 완전체"],
            "도적": ["그림자 조작", "암살자의 직감", "독성 특화", "스텔스 마스터"],
            "성기사": ["신성한 보호", "수호 본능", "불굴의 의지", "기사도 정신"],
            "암흑기사": ["생명력 조작", "어둠의 힘", "피의 갈증", "영혼 흡수"],
            "몽크": ["콤보 마스터", "격투 기술", "정신력", "완벽한 자세"],
            "바드": ["음악 재능", "파티 지원", "정신력", "영적 보호"],
            "네크로맨서": ["생명력 조작", "언데드 지배", "영혼 흡수", "어둠의 힘"],
            "용기사": ["용의 혈통", "화염 저항", "드래곤 하트", "용의 비늘"],
            "검성": ["검기 조작", "무사도 정신", "정밀함", "집중력"],
            "정령술사": ["정령 소통", "원소 마스터", "자연 소통", "마력 조절"],
            "시간술사": ["시간 조작", "현실 왜곡", "차원 여행", "공간 조작"],
            "연금술사": ["폭발 연구", "플라스크 달인", "원소 변환", "생명 연성"],
            "차원술사": ["차원 여행", "공간 조작", "현실 왜곡", "차원의 문"],
            "암살자": ["그림자 조작", "그림자 강화", "그림자 분신", "그림자 숙련"],
            "기계공학자": ["기계 정밀", "발명품 제작", "기계 숙련", "강화 장비"],
            "무당": ["영혼 조작", "정신력", "영적 보호", "무당의 지혜"],
            "해적": ["6단계 완전체", "투기장의 경험", "파티 지원", "격투 기술"],
            "사무라이": ["무사도 정신", "정밀함", "집중력", "완벽한 자세"],
            "드루이드": ["자연 소통", "야생 본능", "식물 친화", "계절의 힘"],
            "철학자": ["논리적 사고", "철학적 통찰", "철학적 사고", "진리 탐구"],
            "검투사": ["투기장의 경험", "격투 기술", "콤보 마스터", "전장의 지배자"],
            "기사": ["기사도 정신", "수호 본능", "신성한 보호", "불굴의 의지"],
            "신관": ["신성 가호", "축복의 오라", "파티 지원", "영적 보호"],
            "마검사": ["검기 조작", "원소 마스터", "마력 조절", "무사도 정신"],
            "광전사": ["광전사의 분노", "피의 축제", "광기의 힘", "파괴의 충동"]
        }
        
        # 해당 직업의 특화 특성이 있으면 반환, 없으면 모든 특성 반환
        if job in job_specific_traits:
            return job_specific_traits[job]
        else:
            return all_traits[:8]  # 기본적으로 8개만 반환
    
    def _display_party_summary(self, party: List[Character]):
        """파티 정보를 간결하게 표시"""
        if not party:
            return
        
        print(f"\n{CYAN}═══════════════════════════════════════════════════════════{RESET}")
        print(f"{BRIGHT_YELLOW}🎉 질문 기반 맞춤 파티 완성!{RESET}")
        print(f"{CYAN}═══════════════════════════════════════════════════════════{RESET}")
        
        for i, char in enumerate(party, 1):
            # 직업별 색상과 역할 아이콘
            job_color = self._get_job_color(char.character_class)
            role_icon = self._get_role_icon(char.character_class)
            
            # 특성 정보 (최대 2개까지만 표시)
            trait_info = ""
            if hasattr(char, 'traits') and char.traits:
                trait_names = char.traits[:2]  # 최대 2개까지
                if trait_names:
                    trait_info = f" | 특성: {', '.join(trait_names)}"
            elif hasattr(char, 'selected_traits') and char.selected_traits:
                trait_names = [trait.name if hasattr(trait, 'name') else str(trait) 
                             for trait in char.selected_traits[:2]]
                if trait_names:
                    trait_info = f" | 특성: {', '.join(trait_names)}"
            
            print(f"{WHITE}{i}.{RESET} {role_icon} {job_color}{char.name}{RESET} "
                  f"({job_color}{char.character_class}{RESET}) "
                  f"Lv.{char.level}{trait_info}")
        
        # 파티 밸런스 분석
        balance = self._analyze_party_balance(party)
        print(f"\n{MAGENTA}📊 파티 밸런스: {balance}{RESET}")
        print(f"{CYAN}═══════════════════════════════════════════════════════════{RESET}")
    
    def _get_role_icon(self, job: str) -> str:
        """직업별 역할 아이콘 반환 - 통일된 분류"""
        tank_jobs = ["전사", "성기사", "기사", "검투사", "광전사"]
        dps_jobs = ["궁수", "도적", "암살자", "검성", "사무라이"]
        mage_jobs = ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사", "마검사"]
        support_jobs = ["바드", "신관", "드루이드", "무당", "철학자"]
        hybrid_jobs = ["암흑기사", "몽크", "용기사", "기계공학자", "해적"]
        
        if job in tank_jobs:
            return "🛡️"
        elif job in dps_jobs:
            return "⚔️"
        elif job in mage_jobs:
            return "🔮"
        elif job in support_jobs:
            return "💫"
        elif job in hybrid_jobs:
            return "🌟"
        else:
            return "❓"
    
    def _get_job_color(self, job: str) -> str:
        """직업별 색상 반환"""
        tank_jobs = ["전사", "성기사", "기사"]
        dps_jobs = ["궁수", "도적", "암살자", "검성", "검투사", "광전사", "사무라이"]
        mage_jobs = ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사", "마검사"]
        support_jobs = ["바드", "신관", "드루이드", "무당", "철학자"]
        hybrid_jobs = ["암흑기사", "몽크", "용기사", "기계공학자", "해적"]
        
        if job in tank_jobs:
            return CYAN  # 파란색 - 탱커
        elif job in dps_jobs:
            return RED   # 빨간색 - 딜러
        elif job in mage_jobs:
            return MAGENTA  # 자주색 - 마법사
        elif job in support_jobs:
            return GREEN    # 초록색 - 서포터
        elif job in hybrid_jobs:
            return YELLOW   # 노란색 - 하이브리드
        else:
            return WHITE
    
    def _analyze_party_balance(self, party: List[Character]) -> str:
        """파티 밸런스 분석"""
        if not party:
            return "파티 없음"
        
        tank_count = 0
        dps_count = 0
        mage_count = 0
        support_count = 0
        hybrid_count = 0
        
        tank_jobs = ["전사", "성기사", "기사"]
        dps_jobs = ["궁수", "도적", "암살자", "검성", "검투사", "광전사", "사무라이"]
        mage_jobs = ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사", "마검사"]
        support_jobs = ["바드", "신관", "드루이드", "무당", "철학자"]
        hybrid_jobs = ["암흑기사", "몽크", "용기사", "기계공학자", "해적"]
        
        for char in party:
            job = char.character_class
            if job in tank_jobs:
                tank_count += 1
            elif job in dps_jobs:
                dps_count += 1
            elif job in mage_jobs:
                mage_count += 1
            elif job in support_jobs:
                support_count += 1
            elif job in hybrid_jobs:
                hybrid_count += 1
        
        # 밸런스 평가
        balance_parts = []
        if tank_count > 0:
            balance_parts.append(f"🛡️×{tank_count}")
        if dps_count > 0:
            balance_parts.append(f"⚔️×{dps_count}")
        if mage_count > 0:
            balance_parts.append(f"🔮×{mage_count}")
        if support_count > 0:
            balance_parts.append(f"💫×{support_count}")
        if hybrid_count > 0:
            balance_parts.append(f"🌟×{hybrid_count}")
        
        balance_str = " ".join(balance_parts)
        
        # 밸런스 등급 판정
        total_roles = len([x for x in [tank_count, dps_count, mage_count, support_count] if x > 0])
        if total_roles >= 3:
            balance_str += " (균형잡힌 파티 ✨)"
        elif total_roles == 2:
            balance_str += " (양호한 밸런스 ⚖️)"
        else:
            balance_str += " (특화 파티 🎯)"
        
        return balance_str
    
    def _select_best_trait_combination_dev_mode(self, character: Character, available_indices: List[int], 
                                              user_tags: List[str], trait_scores: Dict[str, int], 
                                              priority_scores: Dict[int, int] = None):
        """개발 모드에서 2개 특성 선택"""
        if not available_indices:
            character.select_passive_traits([])
            return
        
        # 점수순으로 정렬
        scored_indices = []
        for i in available_indices:
            score = priority_scores.get(i, 0) if priority_scores else 0
            scored_indices.append((i, score))
        
        # 점수 내림차순 정렬
        scored_indices.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 2개 선택 (가능한 경우)
        selected_indices = []
        for i, score in scored_indices[:2]:
            selected_indices.append(i)
        
        # 특성 적용
        if selected_indices:
            character.select_passive_traits(selected_indices)
            selected_names = [character.available_traits[i].name for i in selected_indices]
            print(f"{GREEN}  ✅ {character.name} - 자동 선택된 특성 ({len(selected_names)}개): {', '.join(selected_names)}{RESET}")
        else:
            character.select_passive_traits([])
            print(f"{YELLOW}  ⚠️ {character.name} - 선택된 특성 없음{RESET}")
    
    def _update_difficulty_scaling(self, party: List[Character]):
        """파티에 맞춰 적 난이도 스케일링 업데이트"""
        try:
            from game.dynamic_enemy_scaling import update_difficulty_for_party, show_current_difficulty
            
            # 파티 분석 업데이트
            update_difficulty_for_party(party)
            
            # 현재 난이도 정보 표시
            show_current_difficulty()
            
        except ImportError:
            print(f"{YELLOW}⚠️ 동적 난이도 시스템을 찾을 수 없습니다.{RESET}")
        except Exception as e:
            print(f"{RED}⚠️ 난이도 분석 중 오류: {e}{RESET}")

    def build_party_from_saved_characters(self) -> Optional[List[Character]]:
        """저장된 캐릭터들에서 최대 4명을 선택하여 파티 구성"""
        import json
        import os
        from glob import glob
        
        try:
            # 저장 파일들 찾기
            save_files = glob("saves/*.json") + glob("*.json")
            save_files = [f for f in save_files if f.startswith(("save_", "saves/save_"))]
            
            if not save_files:
                print(f"{RED}저장된 게임 파일이 없습니다.{RESET}")
                return None
            
            # 모든 저장 파일에서 캐릭터 정보 수집
            all_characters = []
            for save_file in save_files:
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    # 파티 멤버들 추출
                    if 'party' in save_data:
                        for char_data in save_data['party']:
                            character_info = {
                                'name': char_data.get('name', 'Unknown'),
                                'class': char_data.get('character_class', 'Unknown'),
                                'level': char_data.get('level', 1),
                                'hp': char_data.get('max_hp', 100),
                                'mp': char_data.get('max_mp', 20),
                                'save_file': save_file,
                                'original_data': char_data
                            }
                            all_characters.append(character_info)
                except Exception as e:
                    print(f"{YELLOW}저장 파일 {save_file} 로드 실패: {e}{RESET}")
                    continue
            
            if not all_characters:
                print(f"{RED}저장된 캐릭터를 찾을 수 없습니다.{RESET}")
                return None
            
            # 중복 제거 (이름 + 클래스로 구분)
            unique_characters = []
            seen = set()
            for char in all_characters:
                key = (char['name'], char['class'])
                if key not in seen:
                    unique_characters.append(char)
                    seen.add(key)
            
            print(f"\n{CYAN}=== 저장된 캐릭터 선택 ==={RESET}")
            print(f"{YELLOW}발견된 캐릭터: {len(unique_characters)}명{RESET}")
            print(f"{YELLOW}최대 4명까지 선택 가능합니다.{RESET}\n")
            
            # 캐릭터 목록 표시
            for i, char in enumerate(unique_characters):
                print(f"{WHITE}{i+1:2}. {BOLD}{char['name']}{RESET} ({char['class']}) - Lv.{char['level']}")
                print(f"     HP: {char['hp']} | MP: {char['mp']} | 출처: {char['save_file']}")
                print()
            
            # 사용자 선택 받기
            selected_indices = []
            while len(selected_indices) < 4:
                try:
                    if len(selected_indices) == 0:
                        prompt = f"{GREEN}선택할 캐릭터 번호를 입력하세요 (1-{len(unique_characters)}, 'done'으로 완료): {RESET}"
                    else:
                        selected_names = [unique_characters[i]['name'] for i in selected_indices]
                        prompt = f"{GREEN}추가 캐릭터 선택 ({len(selected_indices)}/4) - 현재: {', '.join(selected_names)} (번호 입력 또는 'done'): {RESET}"
                    
                    user_input = input(prompt).strip()
                    
                    if user_input.lower() in ['done', '완료', 'd']:
                        if len(selected_indices) > 0:
                            break
                        else:
                            print(f"{RED}최소 1명은 선택해야 합니다.{RESET}")
                            continue
                    
                    index = int(user_input) - 1
                    if 0 <= index < len(unique_characters):
                        if index not in selected_indices:
                            selected_indices.append(index)
                            print(f"{GREEN}✓ {unique_characters[index]['name']} 선택됨{RESET}")
                        else:
                            print(f"{YELLOW}이미 선택된 캐릭터입니다.{RESET}")
                    else:
                        print(f"{RED}올바른 번호를 입력하세요 (1-{len(unique_characters)}).{RESET}")
                        
                except ValueError:
                    print(f"{RED}숫자를 입력하거나 'done'을 입력하세요.{RESET}")
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}선택이 취소되었습니다.{RESET}")
                    return None
            
            # 선택된 캐릭터들로 파티 생성
            party = []
            for index in selected_indices:
                char_info = unique_characters[index]
                try:
                    # 저장된 데이터에서 캐릭터 복원
                    from game.save_system import GameStateSerializer
                    character = GameStateSerializer.deserialize_character(char_info['original_data'])
                    if character:
                        party.append(character)
                        print(f"{GREEN}✓ {character.name} 로드 완료{RESET}")
                    else:
                        print(f"{RED}✗ {char_info['name']} 로드 실패{RESET}")
                except Exception as e:
                    print(f"{RED}✗ {char_info['name']} 로드 오류: {e}{RESET}")
                    continue
            
            if len(party) == 0:
                print(f"{RED}캐릭터를 로드할 수 없습니다.{RESET}")
                return None
            
            print(f"\n{BRIGHT_CYAN}🎉 저장된 캐릭터 {len(party)}명으로 파티 구성 완료!{RESET}")
            return party
            
        except Exception as e:
            print(f"{RED}저장된 캐릭터 로드 중 오류 발생: {e}{RESET}")
            return None
    
    def _give_starting_items_to_party(self, party_members: List[Character]):
        """파티 전체에게 스타팅 아이템 지급"""
        print(f"\n{CYAN}🎁 스타팅 아이템 지급 중...{RESET}")
        
        for character in party_members:
            try:
                # 각 캐릭터에게 스타팅 아이템 생성
                starting_items = enhanced_items.generate_starting_items(
                    character.character_class, character.level
                )
                
                # 인벤토리가 없으면 생성
                if not hasattr(character, 'inventory'):
                    character.inventory = []
                
                # 장비 아이템 추가 (2개)
                for equipment in starting_items["equipment"]:
                    item = enhanced_items.create_item_for_inventory(equipment)
                    # 인벤토리 타입에 따른 처리
                    if hasattr(character.inventory, 'add_item_by_name'):
                        # Inventory 객체인 경우 - 이름으로 추가
                        success = character.inventory.add_item_by_name(item['name'])
                        if not success:
                            print(f"      ⚠️ {item['name']} 추가 실패 (add_item_by_name)")
                    elif hasattr(character.inventory, 'add_item'):
                        # Inventory 객체인 경우 - 직접 추가 (fallback)
                        try:
                            from game.items import Item, ItemType, ItemRarity
                            inventory_item = Item(item['name'], ItemType.EQUIPMENT, ItemRarity.COMMON, 
                                                item.get('description', '장비 아이템'))
                            character.inventory.add_item(inventory_item)
                        except Exception as e:
                            print(f"      ⚠️ {item['name']} 추가 실패 (add_item): {e}")
                    elif hasattr(character.inventory, 'items'):
                        # Dict 형태 인벤토리인 경우
                        if item['name'] in character.inventory.items:
                            character.inventory.items[item['name']] += item.get('quantity', 1)
                        else:
                            character.inventory.items[item['name']] = item.get('quantity', 1)
                    else:
                        # 리스트인 경우 - 직접 추가
                        character.inventory.append(item)
                
                # 소비 아이템 추가 (2개)
                for consumable in starting_items["consumables"]:
                    item = enhanced_items.create_item_for_inventory(consumable)
                    # 인벤토리 타입에 따른 처리
                    if hasattr(character.inventory, 'add_item_by_name'):
                        # Inventory 객체인 경우 - 이름으로 추가
                        success = character.inventory.add_item_by_name(item['name'])
                        if not success:
                            print(f"      ⚠️ {item['name']} 추가 실패 (add_item_by_name)")
                    elif hasattr(character.inventory, 'add_item'):
                        # Inventory 객체인 경우 - 직접 추가 (fallback)
                        try:
                            from game.items import Item, ItemType, ItemRarity
                            inventory_item = Item(item['name'], ItemType.CONSUMABLE, ItemRarity.COMMON, 
                                                item.get('description', '소비 아이템'))
                            character.inventory.add_item(inventory_item)
                        except Exception as e:
                            print(f"      ⚠️ {item['name']} 추가 실패 (add_item): {e}")
                    elif hasattr(character.inventory, 'items'):
                        # Dict 형태 인벤토리인 경우
                        if item['name'] in character.inventory.items:
                            character.inventory.items[item['name']] += item.get('quantity', 1)
                        else:
                            character.inventory.items[item['name']] = item.get('quantity', 1)
                    else:
                        # 리스트인 경우 - 직접 추가
                        character.inventory.append(item)
                
                # 자동 장착 시도 (장비 아이템만)
                self._auto_equip_starting_items(character, starting_items["equipment"])
                
                print(f"{GREEN}  ✅ {character.name} - 스타팅 아이템 지급 완료{RESET}")
                
            except Exception as e:
                print(f"{RED}  ✗ {character.name} - 아이템 지급 실패: {e}{RESET}")

    def _calculate_diversity_score(self, party_classes: List[str]) -> int:
        """파티 구성의 다양성 점수 계산 (0-100점)"""
        if not party_classes:
            return 0
        
        score = 0
        
        # 1. 중복 없는 직업 비율 (40점)
        unique_classes = len(set(party_classes))
        total_classes = len(party_classes)
        uniqueness_ratio = unique_classes / total_classes
        score += int(uniqueness_ratio * 40)
        
        # 2. 역할 다양성 (30점)
        role_count = {"탱커": 0, "딜러": 0, "마법사": 0, "서포터": 0, "하이브리드": 0}
        for class_name in party_classes:
            for role, classes in self.ROLE_CLASSES.items():
                if class_name in classes:
                    role_count[role] += 1
                    break
        
        # 서로 다른 역할의 수
        different_roles = sum(1 for count in role_count.values() if count > 0)
        role_diversity = (different_roles / 5) * 30  # 최대 5개 역할
        score += int(role_diversity)
        
        # 3. 희소 직업 보너스 (20점)
        rare_classes = ["암살자", "해적", "사무라이", "드루이드", "철학자", 
                       "검투사", "기사", "신관", "광전사"]
        rare_count = sum(1 for class_name in party_classes if class_name in rare_classes)
        rare_bonus = min(20, rare_count * 7)  # 희소 직업 1개당 7점, 최대 20점
        score += rare_bonus
        
        # 4. 밸런스 페널티 (한 역할이 너무 많으면 감점)
        balance_penalty = 0
        for role, count in role_count.items():
            if count > 2:  # 같은 역할이 3명 이상이면 페널티
                balance_penalty += (count - 2) * 5
        
        # 5. 하이브리드 직업 특별 보너스 (10점)
        hybrid_bonus = min(10, role_count["하이브리드"] * 10)
        score += hybrid_bonus
        
        final_score = max(0, min(100, score - balance_penalty))
        
        return final_score
    
    def _auto_equip_starting_items(self, character: Character, equipment_items: List[Dict]):
        """스타팅 장비 자동 장착"""
        for equipment in equipment_items:
            try:
                # 장비 타입 확인
                item_type = self._determine_equipment_type(equipment)
                item_name = equipment.get('name', '알 수 없는 아이템')
                
                # 캐릭터에 장비 속성이 없으면 생성
                if not hasattr(character, 'weapon'):
                    character.weapon = None
                if not hasattr(character, 'armor'):
                    character.armor = None
                if not hasattr(character, 'accessory'):
                    character.accessory = None
                
                # 해당 슬롯이 비어있으면 자동 장착
                if item_type == "무기" and character.weapon is None:
                    character.weapon = equipment
                    print(f"{GREEN}      ✅ {item_name} 무기 슬롯에 자동 장착{RESET}")
                elif item_type == "방어구" and character.armor is None:
                    character.armor = equipment
                    print(f"{GREEN}      ✅ {item_name} 방어구 슬롯에 자동 장착{RESET}")
                elif item_type == "장신구" and character.accessory is None:
                    character.accessory = equipment
                    print(f"{GREEN}      ✅ {item_name} 장신구 슬롯에 자동 장착{RESET}")
                else:
                    print(f"{YELLOW}      ⚠️ {item_name} ({item_type}) - 해당 슬롯이 이미 사용 중{RESET}")
                    
            except Exception as e:
                print(f"{YELLOW}    ⚠️ {equipment.get('name', '알 수 없는 아이템')} 자동 장착 실패: {e}{RESET}")
    
    def _determine_equipment_type(self, equipment: Dict) -> str:
        """장비 타입 판별"""
        name = equipment.get('name', '').lower()
        
        # 무기 키워드
        weapon_keywords = ['검', '도', '활', '지팡이', '창', '도끼', '망치', '단검', '총', '권총', '소총']
        # 방어구 키워드  
        armor_keywords = ['갑옷', '로브', '가죽', '천', '판금', '사슬', '투구', '모자', '방패']
        # 장신구 키워드
        accessory_keywords = ['반지', '목걸이', '팔찌', '부적', '장신구']
        
        for keyword in weapon_keywords:
            if keyword in name:
                return "무기"
        
        for keyword in armor_keywords:
            if keyword in name:
                return "방어구"
                
        for keyword in accessory_keywords:
            if keyword in name:
                return "장신구"
        
        # 기본값은 무기로 처리
        return "무기"
    
    def _manual_select_passives(self, character: Character):
        """사용자가 직접 특성 선택 - 커서 메뉴 방식"""
        print(f"\n{CYAN}=== {character.name}({character.character_class})의 특성 선택 ==={RESET}")
        
        # 특성 시스템이 있는지 확인
        try:
            from game.character import CharacterClassManager
            from game.cursor_menu_system import CursorMenu
            
            available_traits = CharacterClassManager.get_class_traits(character.character_class)
            
            if not available_traits:
                print(f"{YELLOW}사용 가능한 특성이 없습니다.{RESET}")
                return
            
            # 커서 메뉴용 옵션 구성
            options = []
            for trait in available_traits:
                options.append({
                    'text': trait.name,
                    'detail': trait.description
                })
            
            # 건너뛰기 옵션 추가
            options.append({
                'text': '특성 없이 계속',
                'detail': '특성을 선택하지 않고 진행합니다'
            })
            
            # 커서 메뉴 표시
            menu = CursorMenu(
                title=f"{character.name}의 특성 선택",
                options=options,
                descriptions=[opt['detail'] for opt in options],
                screen_width=100,
                screen_height=30
            )
            
            choice = menu.display()
            
            if choice < len(available_traits):
                selected_trait = available_traits[choice]
                character.traits = [selected_trait]
                print(f"\n{GREEN}✅ '{selected_trait.name}' 특성이 선택되었습니다!{RESET}")
            else:
                print(f"\n{CYAN}특성 선택을 건너뛰었습니다.{RESET}")
                    
        except Exception as e:
            print(f"{YELLOW}특성 시스템을 로드할 수 없습니다: {e}{RESET}")
            print(f"{CYAN}특성 없이 계속 진행합니다.{RESET}")
    
    def _provide_starting_equipment(self, character: Character):
        """캐릭터에게 시작 장비 제공"""
        try:
            # 시작 아이템 생성 (랜덤 2개 장비 + 1-3개 소모품)
            starting_items = self._generate_starting_items_for_class(character.character_class)
            
            if starting_items:
                print(f"\n{GREEN}✅ {character.name}에게 시작 장비를 제공합니다:{RESET}")
                
                # 인벤토리 초기화 (없는 경우)
                if not hasattr(character, 'inventory') or character.inventory is None:
                    from game.items import Inventory
                    character.inventory = Inventory()
                
                # 장비 아이템 추가 및 자동 장착
                equipment_for_auto_equip = []
                for item in starting_items.get("equipment", []):
                    # Item 객체로 변환하여 인벤토리에 추가
                    from game.items import Item, ItemType, ItemRarity
                    
                    # 아이템 타입 결정
                    item_type_str = item.get('type', '장비')
                    if item_type_str == '무기':
                        item_type = ItemType.WEAPON
                    elif item_type_str == '방어구':
                        item_type = ItemType.ARMOR
                    elif item_type_str == '장신구':
                        item_type = ItemType.ACCESSORY
                    else:
                        item_type = ItemType.WEAPON  # 기본값
                    
                    item_obj = Item(
                        name=item.get('name', '알 수 없는 장비'),
                        item_type=item_type,
                        rarity=ItemRarity.COMMON,
                        description=f"{character.character_class} 전용 시작 장비",
                        weight=1.0,
                        value=10
                    )
                    
                    # 아이템 스탯 설정
                    if item.get('attack'):
                        item_obj.stats['공격력'] = item['attack']
                    if item.get('defense'):
                        item_obj.stats['방어력'] = item['defense']
                    
                    if character.inventory.add_item(item_obj):
                        print(f"  📦 {item.get('name', '알 수 없는 장비')} 획득!")
                        equipment_for_auto_equip.append(item)
                    else:
                        print(f"  ❌ {item.get('name', '알 수 없는 장비')} 추가 실패 (인벤토리 가득참)")
                
                # 소모품 추가
                for item in starting_items.get("consumables", []):
                    from game.items import Item, ItemType, ItemRarity
                    item_obj = Item(
                        name=item.get('name', '알 수 없는 소모품'),
                        item_type=ItemType.CONSUMABLE,
                        rarity=ItemRarity.COMMON,
                        description=f"유용한 소모품",
                        weight=0.1,
                        value=5
                    )
                    
                    if character.inventory.add_item(item_obj):
                        print(f"  🧪 {item.get('name', '알 수 없는 소모품')} 획득!")
                    else:
                        print(f"  ❌ {item.get('name', '알 수 없는 소모품')} 추가 실패 (인벤토리 가득함)")
                
                # 자동 장착 시도
                if equipment_for_auto_equip:
                    self._auto_equip_starting_items(character, equipment_for_auto_equip)
                
            else:
                print(f"{YELLOW}⚠️ {character.character_class}에 대한 시작 장비가 없습니다.{RESET}")
                
        except Exception as e:
            print(f"{YELLOW}⚠️ 시작 장비 제공 중 오류: {e}{RESET}")
            import traceback
            traceback.print_exc()
    
    def _generate_starting_items_for_class(self, character_class: str) -> Dict[str, List[Dict]]:
        """직업별 시작 아이템 생성 (2개 장비 + 1-3개 소모품)"""
        import random
        
        # 직업별 장비 카테고리 매핑
        class_equipment_map = {
            # 전투 직업군
            "전사": {"weapon": ["검", "도끼", "망치"], "armor": ["판금갑옷", "사슬갑옷"], "accessory": ["전사의 반지"]},
            "아크메이지": {"weapon": ["지팡이", "완드"], "armor": ["마법사 로브"], "accessory": ["마력의 목걸이"]},
            "궁수": {"weapon": ["활", "석궁"], "armor": ["가죽갑옷"], "accessory": ["정확성의 반지"]},
            "도적": {"weapon": ["단검", "단검"], "armor": ["경량갑옷"], "accessory": ["민첩의 반지"]},
            "성기사": {"weapon": ["성검", "성스러운 창"], "armor": ["성기사 갑옷"], "accessory": ["성스러운 목걸이"]},
            "암흑기사": {"weapon": ["암흑검", "저주받은 도끼"], "armor": ["암흑갑옷"], "accessory": ["어둠의 반지"]},
            "몽크": {"weapon": ["권투글러브", "철제 건틀릿"], "armor": ["수도복"], "accessory": ["집중의 팔찌"]},
            "바드": {"weapon": ["하프", "류트"], "armor": ["음유시인 옷"], "accessory": ["음악의 반지"]},
            
            # 마법 직업군
            "네크로맨서": {"weapon": ["해골 지팡이", "부패의 완드"], "armor": ["네크로맨서 로브"], "accessory": ["언데드의 목걸이"]},
            "용기사": {"weapon": ["용검", "드래곤 창"], "armor": ["용비늘 갑옷"], "accessory": ["용의 심장"]},
            "검성": {"weapon": ["영검", "기검"], "armor": ["검성 도복"], "accessory": ["검기의 반지"]},
            "정령술사": {"weapon": ["정령 지팡이", "원소 완드"], "armor": ["정령술사 로브"], "accessory": ["원소의 목걸이"]},
            "시간술사": {"weapon": ["시공 지팡이", "시간의 완드"], "armor": ["시간술사 로브"], "accessory": ["시간의 반지"]},
            "연금술사": {"weapon": ["연금술 지팡이", "실험 도구"], "armor": ["연금술사 코트"], "accessory": ["연금의 반지"]},
            "차원술사": {"weapon": ["차원 지팡이", "공간 완드"], "armor": ["차원술사 로브"], "accessory": ["차원의 목걸이"]},
            "마검사": {"weapon": ["마검", "마도검"], "armor": ["마검사 갑옷"], "accessory": ["마력의 반지"]},
            "기계공학자": {"weapon": ["기계 권총", "레이저 건"], "armor": ["기계 갑옷"], "accessory": ["기계의 팔찌"]},
            "무당": {"weapon": ["영혼 지팡이", "제례용 칼"], "armor": ["무당 의복"], "accessory": ["영혼의 목걸이"]},
            
            # 특수 직업군
            "암살자": {"weapon": ["암살 단검", "독 칼"], "armor": ["암살자 의복"], "accessory": ["그림자의 반지"]},
            "해적": {"weapon": ["해적 도", "곡도"], "armor": ["해적 코트"], "accessory": ["해적의 목걸이"]},
            "사무라이": {"weapon": ["카타나", "와키자시"], "armor": ["사무라이 갑옷"], "accessory": ["명예의 반지"]},
            "드루이드": {"weapon": ["자연 지팡이", "나무 창"], "armor": ["드루이드 로브"], "accessory": ["자연의 목걸이"]},
            "철학자": {"weapon": ["지혜의 지팡이", "논리의 완드"], "armor": ["철학자 로브"], "accessory": ["지혜의 반지"]},
            "검투사": {"weapon": ["글라디우스", "트라이던트"], "armor": ["검투사 갑옷"], "accessory": ["투기의 반지"]},
            "기사": {"weapon": ["기사 창", "롱소드"], "armor": ["기사 갑옷"], "accessory": ["기사의 반지"]},
            "신관": {"weapon": ["성스러운 메이스", "축복의 지팡이"], "armor": ["신관 로브"], "accessory": ["신성의 목걸이"]},
            "광전사": {"weapon": ["광전사 도끼", "파괴의 망치"], "armor": ["광전사 갑옷"], "accessory": ["광기의 반지"]}
        }
        
        # 공통 소모품
        consumables = [
            {"name": "체력 포션", "type": "소모품", "effect": "HP 회복", "value": 50},
            {"name": "마나 포션", "type": "소모품", "effect": "MP 회복", "value": 30},
            {"name": "해독제", "type": "소모품", "effect": "독 치료", "value": 1},
            {"name": "상처 연고", "type": "소모품", "effect": "상처 치료", "value": 25},
            {"name": "힘의 물약", "type": "소모품", "effect": "공격력 증가", "value": 10}
        ]
        
        # 직업에 맞는 장비 선택
        equipment_data = class_equipment_map.get(character_class, class_equipment_map["전사"])
        starting_equipment = []
        
        # 무기 1개 랜덤 선택
        if equipment_data.get("weapon"):
            weapon_name = random.choice(equipment_data["weapon"])
            starting_equipment.append({
                "name": weapon_name,
                "type": "무기",
                "attack": random.randint(8, 15),
                "durability": 100,
                "class_specific": character_class
            })
        
        # 방어구 1개 랜덤 선택
        if equipment_data.get("armor"):
            armor_name = random.choice(equipment_data["armor"])
            starting_equipment.append({
                "name": armor_name,
                "type": "방어구", 
                "defense": random.randint(5, 12),
                "durability": 100,
                "class_specific": character_class
            })
        
        # 소모품 1-3개 랜덤 선택
        starting_consumables = random.sample(consumables, random.randint(1, 3))
        
        return {
            "equipment": starting_equipment,
            "consumables": starting_consumables
        }
    
    def _ai_assisted_select_passives(self, character: Character, user_tags: List[str]):
        """AI 힌트와 함께 특성 선택"""
        print(f"\n{CYAN}=== {character.name}({character.character_class})의 특성 선택 (AI 추천) ==={RESET}")
        
        try:
            from game.character import CharacterClassManager
            available_traits = CharacterClassManager.get_class_traits(character.character_class)
            
            if not available_traits:
                print(f"{YELLOW}사용 가능한 특성이 없습니다.{RESET}")
                return
            
            # AI 추천 점수 계산
            trait_scores = {}
            for trait in available_traits:
                score = self._calculate_trait_ai_score(trait, user_tags)
                trait_scores[trait.name] = score
            
            # 점수 순으로 정렬
            sorted_traits = sorted(available_traits, key=lambda t: trait_scores[t.name], reverse=True)
            
            print(f"{GREEN}AI 추천 특성 (추천도 순):{RESET}")
            for i, trait in enumerate(sorted_traits):
                score = trait_scores[trait.name]
                stars = "★" * min(5, max(1, int(score / 20)))
                print(f"  [{i+1}] {trait.name}: {trait.description}")
                print(f"      {YELLOW}AI 추천도: {stars} ({score:.0f}점){RESET}")
            
            print(f"\n{YELLOW}특성을 선택하세요 (1-{len(sorted_traits)}, 0=AI 자동 선택):{RESET}")
            
            while True:
                try:
                    choice = input("특성 번호: ").strip()
                    if choice == "0" or choice == "":
                        # AI 자동 선택 (가장 높은 점수)
                        selected_trait = sorted_traits[0]
                        character.traits = [selected_trait]
                        print(f"{GREEN}🤖 AI가 '{selected_trait.name}'을(를) 자동 선택했습니다!{RESET}")
                        break
                    
                    trait_index = int(choice) - 1
                    if 0 <= trait_index < len(sorted_traits):
                        selected_trait = sorted_traits[trait_index]
                        character.traits = [selected_trait]
                        print(f"{GREEN}✅ '{selected_trait.name}' 특성이 선택되었습니다!{RESET}")
                        break
                    else:
                        print(f"{RED}잘못된 번호입니다. 1-{len(sorted_traits)} 사이의 숫자를 입력하세요.{RESET}")
                        
                except ValueError:
                    print(f"{RED}숫자를 입력하세요.{RESET}")
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}특성 선택을 취소했습니다.{RESET}")
                    break
                    
        except Exception as e:
            print(f"{YELLOW}특성 시스템을 로드할 수 없습니다: {e}{RESET}")
            print(f"{CYAN}특성 없이 계속 진행합니다.{RESET}")
    
    def _calculate_trait_ai_score(self, trait: 'CharacterTrait', user_tags: List[str]) -> float:
        """특성에 대한 AI 추천 점수 계산"""
        score = 50.0  # 기본 점수
        
        # 사용자 태그에 따른 점수 조정
        trait_name_lower = trait.name.lower()
        trait_desc_lower = trait.description.lower()
        
        for tag in user_tags:
            tag_lower = tag.lower()
            
            # 태그와 특성 이름/설명 매칭
            if tag_lower in trait_name_lower or tag_lower in trait_desc_lower:
                score += 30
            
            # 특정 태그에 따른 추가 점수
            if tag == "공격적" and ("공격" in trait_desc_lower or "피해" in trait_desc_lower):
                score += 25
            elif tag == "방어적" and ("방어" in trait_desc_lower or "보호" in trait_desc_lower):
                score += 25
            elif tag == "전략적" and ("스택" in trait_desc_lower or "효과" in trait_desc_lower):
                score += 20
            elif tag == "협력적" and ("아군" in trait_desc_lower or "파티" in trait_desc_lower):
                score += 20
        
        # 특성 타입에 따른 기본 점수
        if hasattr(trait, 'effect_type'):
            if trait.effect_type == "passive":
                score += 10  # 패시브는 항상 유용
            elif trait.effect_type == "trigger":
                score += 15  # 트리거는 더 강력
        
        return min(100, max(0, score))
    
    def _allow_name_customization(self, character: Character):
        """캐릭터 이름 커스터마이징 - 이름 풀에서 선택"""
        print(f"\n{CYAN}=== 캐릭터 이름 설정 ==={RESET}")
        print(f"현재 이름: {GREEN}{character.name}{RESET} ({character.character_class})")
        
        try:
            from game.unified_name_pools import NAME_POOLS, get_random_name, detect_gender_from_name
            from game.cursor_menu_system import CursorMenu
            import random
            
            # 현재 이름으로 성별 감지
            current_gender = detect_gender_from_name(character.name)
            
            # 같은 성별 이름들만 15개 선택
            same_gender_names = random.sample(NAME_POOLS["western"][current_gender], min(15, len(NAME_POOLS["western"][current_gender])))
            
            # 커서 메뉴 옵션 구성
            options = []
            
            # 현재 이름 유지 옵션
            options.append({
                'text': f'현재 이름 유지: {character.name}',
                'detail': f'{character.character_class}에게 어울리는 현재 이름을 그대로 사용합니다'
            })
            
            # 같은 성별 이름들
            for name in same_gender_names:
                if name != character.name:  # 현재 이름과 다른 것만
                    options.append({
                        'text': f'{name}',
                        'detail': f'{character.character_class}에게 어울리는 {current_gender} 이름입니다'
                    })
            
            # 랜덤 리롤 옵션
            options.append({
                'text': '🎲 다른 이름들 보기',
                'detail': '새로운 랜덤 이름 목록을 다시 생성합니다'
            })
            
            # 직접 입력 옵션
            options.append({
                'text': '✏️ 직접 입력',
                'detail': '원하는 이름을 직접 입력합니다'
            })
            
            while True:
                # 커서 메뉴 표시
                menu = CursorMenu(
                    title=f"{character.name}의 이름 선택",
                    options=options,
                    descriptions=[opt['detail'] for opt in options],
                    screen_width=100,
                    screen_height=25
                )
                
                choice = menu.display()
                
                if choice == 0:  # 현재 이름 유지
                    print(f"{CYAN}기존 이름 '{character.name}'을 유지합니다.{RESET}")
                    break
                elif choice == len(options) - 2:  # 리롤
                    # 새로운 이름 목록 생성
                    same_gender_names = random.sample(NAME_POOLS["western"][current_gender], min(15, len(NAME_POOLS["western"][current_gender])))
                    
                    # 옵션 다시 구성 (첫 번째와 마지막 두 개는 고정)
                    options = options[:1] + options[-2:]  # 첫 번째, 리롤, 직접입력만 유지
                    
                    # 새 이름들 추가
                    new_options = []
                    for name in same_gender_names:
                        if name != character.name:
                            new_options.append({
                                'text': f'{name}',
                                'detail': f'{character.character_class}에게 어울리는 {current_gender} 이름입니다'
                            })
                    
                    # 새 옵션들을 중간에 삽입
                    options = options[:1] + new_options + options[1:]
                    print(f"{GREEN}🎲 새로운 이름 목록을 생성했습니다!{RESET}")
                    continue
                    
                elif choice == len(options) - 1:  # 직접 입력
                    print(f"{YELLOW}새로운 이름을 입력하세요:{RESET}")
                    new_name = input("새 이름: ").strip()
                    if new_name and new_name != character.name:
                        character.name = new_name
                        print(f"{GREEN}✅ 이름이 '{new_name}'으로 변경되었습니다!{RESET}")
                        break
                    else:
                        print(f"{YELLOW}올바른 이름을 입력하지 않았습니다.{RESET}")
                        continue
                        
                else:  # 이름 선택
                    selected_option = options[choice]
                    # 이름 추출
                    new_name = selected_option['text']
                    if new_name != character.name:
                        character.name = new_name
                        print(f"{GREEN}✅ 이름이 '{new_name}'으로 변경되었습니다!{RESET}")
                    else:
                        print(f"{CYAN}기존 이름을 유지합니다.{RESET}")
                    break
            
        except KeyboardInterrupt:
            print(f"\n{CYAN}이름 변경을 취소했습니다.{RESET}")
        except Exception as e:
            print(f"{YELLOW}이름 선택 중 오류 발생: {e}{RESET}")
            print(f"{CYAN}기존 이름을 유지합니다.{RESET}")
    
    def create_random_party(self, party_size: int = 4) -> List[Character]:
        """완전 랜덤 파티 생성"""
        print(f"\n{CYAN}=== 랜덤 파티 생성 시작 ==={RESET}")
        
        # 사용된 이름 초기화
        self._used_names = set()
        
        # 랜덤으로 직업 선택
        import random
        selected_classes = random.sample(self.ALL_CLASSES, min(party_size, len(self.ALL_CLASSES)))
        
        print(f"{GREEN}랜덤 선택된 직업들: {', '.join(selected_classes)}{RESET}")
        
        party_members = []
        
        for i, class_name in enumerate(selected_classes):
            character = self._create_character(class_name, i + 1)
            
            # 랜덤으로 특성 선택 (50% 확률)
            if random.choice([True, False]):
                self._auto_select_passives(character)
            
            # 시작 장비 제공
            self._provide_starting_equipment(character)
            
            party_members.append(character)
        
        print(f"{GREEN}✅ 랜덤 파티 생성 완료!{RESET}")
        return party_members
    
    def _manual_select_passives_with_ai_hints(self, character: Character, user_tags: List[str], trait_scores: Dict[str, int]):
        """AI 힌트와 함께 사용자가 직접 특성 선택 - 커서 메뉴 방식"""
        print(f"\n{CYAN}=== {character.name}({character.character_class})의 특성 선택 ==={RESET}")
        
        try:
            from game.trait_system import get_trait_system
            from game.cursor_menu_system import CursorMenu
            trait_system = get_trait_system()
            available_traits = trait_system.get_available_traits(character.character_class)
            
            if not available_traits:
                print(f"{YELLOW}사용 가능한 특성이 없습니다.{RESET}")
                return
            
            # AI 추천 특성 계산
            recommended_traits = []
            for trait in available_traits:
                trait_name = trait.get('name', '')
                if trait_name in trait_scores:
                    recommended_traits.append((trait, trait_scores[trait_name]))
            
            # 점수 순으로 정렬
            recommended_traits.sort(key=lambda x: x[1], reverse=True)
            recommended_trait_names = [t[0].get('name', '') for t in recommended_traits[:3]]
            
            # 커서 메뉴용 옵션 구성
            options = []
            descriptions = []
            
            for trait in available_traits:
                trait_name = trait.get('name', '')
                trait_desc = trait.get('description', '')
                
                # AI 추천 특성인지 확인
                if trait_name in recommended_trait_names:
                    display_name = f"🤖⭐ {trait_name}"
                    description = f"[AI 추천] {trait_desc}"
                else:
                    display_name = trait_name
                    description = trait_desc
                
                options.append({'text': display_name, 'detail': description})
                descriptions.append(description)
            
            # 건너뛰기 옵션 추가
            options.append({'text': '특성 없이 계속', 'detail': '특성을 선택하지 않고 진행합니다'})
            descriptions.append('특성을 선택하지 않고 진행합니다')
            
            # 커서 메뉴 표시
            menu = CursorMenu(
                title=f"{character.name}의 특성 선택 (🤖 = AI 추천)",
                options=options,
                descriptions=descriptions,
                screen_width=100,
                screen_height=30
            )
            
            choice = menu.display()
            
            if choice < len(available_traits):
                selected_trait = available_traits[choice]
                character.traits = [selected_trait]
                
                trait_name = selected_trait.get('name', '')
                if trait_name in recommended_trait_names:
                    print(f"\n{GREEN}✅ AI 추천 특성 '{trait_name}'을 선택했습니다! 🤖⭐{RESET}")
                else:
                    print(f"\n{GREEN}✅ '{trait_name}' 특성이 선택되었습니다!{RESET}")
            else:
                print(f"\n{CYAN}특성 선택을 건너뛰었습니다.{RESET}")
                    
        except Exception as e:
            print(f"{YELLOW}특성 시스템을 로드할 수 없습니다: {e}{RESET}")
            print(f"{CYAN}특성 없이 계속 진행합니다.{RESET}")

# 전역 자동 파티 빌더 인스턴스
auto_party_builder = AutoPartyBuilder()

def get_auto_party_builder() -> AutoPartyBuilder:
    """자동 파티 빌더 반환"""
    return auto_party_builder
