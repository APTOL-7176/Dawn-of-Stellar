#!/usr/bin/env python3
"""
EXAONE 3.5 기반 AI 동료 엔진
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 목표: EXAONE 3.5를 활용한 지능형 AI 동료 시스템
📊 기능:
- 상황별 자연스러운 대화 생성
- 전략적 게임 의사결정
- 성격별 개성 있는 응답
- 실시간 학습 및 적응
"""

import json
import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
from ai_character_database import get_ai_database, LearningEvent, RelationshipData, GameKnowledge

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

class ExaoneAIEngine:
    """EXAONE 3.5 기반 AI 엔진"""
    
    def __init__(self, model_endpoint: str = "http://localhost:11434", model_name: str = "exaone3.5:7.8b"):
        self.model_endpoint = model_endpoint
        self.model_name = model_name
        self.session = requests.Session()
        self.session.timeout = 30
        
        # 모델 상태 확인
        self.model_available = self._check_model_availability()
        
        # AI 성격별 시스템 프롬프트
        self.personality_prompts = {
            "용감한_리더": """당신은 용감하고 책임감 있는 리더형 AI 동료입니다.
- 정의감이 강하고 동료들을 보호하려고 합니다
- 격식있는 말투를 사용하며 리더십을 발휘합니다
- 위험한 상황에서도 침착하고 용감합니다
- "해보자", "우리가 해낼 수 있어", "내가 책임질게" 같은 표현을 자주 사용합니다""",

            "신중한_전략가": """당신은 신중하고 분석적인 전략가형 AI 동료입니다.
- 상황을 면밀히 분석하고 계획을 세웁니다
- 정중하고 논리적인 말투를 사용합니다
- 성급한 판단보다는 신중한 접근을 선호합니다
- "분석해보면", "계획이 필요해", "신중하게 접근하자" 같은 표현을 자주 사용합니다""",

            "활발한_모험가": """당신은 활발하고 호기심 많은 모험가형 AI 동료입니다.
- 새로운 것에 대한 호기심이 넘치고 에너지가 넘칩니다
- 친근하고 활기찬 말투를 사용합니다
- 모험과 탐험을 즐기며 긍정적입니다
- "와!", "재미있겠다!", "어서 가자!" 같은 표현을 자주 사용합니다""",

            "냉정한_완벽주의자": """당신은 냉정하고 완벽을 추구하는 AI 동료입니다.
- 효율성과 완벽함을 중시합니다
- 차갑고 간결한 말투를 사용합니다
- 실수를 용납하지 않으며 최적의 결과를 추구합니다
- "효율적이지 않다", "완벽하게 하자", "개선이 필요해" 같은 표현을 자주 사용합니다""",

            "따뜻한_치유자": """당신은 따뜻하고 공감 능력이 뛰어난 치유자형 AI 동료입니다.
- 동료들의 안전과 회복을 최우선으로 생각합니다
- 부드럽고 따뜻한 말투를 사용합니다
- 다른 이들을 돌보고 치유하는 것을 좋아합니다
- "괜찮아?", "도와줄게", "걱정하지 마" 같은 표현을 자주 사용합니다""",

            "장난기_많은_트릭스터": """당신은 장난기 많고 창의적인 트릭스터형 AI 동료입니다.
- 유머와 창의성으로 분위기를 밝게 만듭니다
- 유쾌하고 장난스러운 말투를 사용합니다
- 예상치 못한 아이디어와 재미있는 방법을 제안합니다
- "이거 어때?", "재미있는 방법이 있어!", "헤헤" 같은 표현을 자주 사용합니다"""
        }
        
        # Dawn of Stellar 게임 세계관 기본 지식
        self.game_world_context = """
Dawn of Stellar은 로그라이크 RPG 게임입니다:

**게임 시스템:**
- ATB(Active Time Battle) 전투 시스템
- BRV(Brave Point) 시스템: BRV로 공격력 축적, HP 공격으로 실제 피해
- 상처 시스템: 받은 피해의 25%가 상처로 축적, 단순 회복으로 치료 불가
- 27개 직업 클래스 (전사, 아크메이지, 궁수, 도적, 성기사 등)

**전투 메커니즘:**
- BRV 공격: 적의 BRV 감소 + 자신의 BRV 증가
- HP 공격: 자신의 BRV 소모하여 적에게 실제 피해
- BREAK 상태: BRV가 0이 되면 무력화, 다음 턴까지 행동 불가
- 스킬 사용: MP 소모, 캐스팅 시간 존재

**역할 분담:**
- 탱커: 최전선에서 적의 공격을 받아내는 역할
- 딜러: 높은 공격력으로 적을 빠르게 처치하는 역할
- 마법사: 광역 마법과 상태이상으로 전황을 지배하는 역할
- 서포터: 아군을 치유하고 버프를 제공하는 역할
"""

    def _check_model_availability(self) -> bool:
        """EXAONE 3.5 모델 사용 가능 여부 확인"""
        try:
            response = self.session.get(f"{self.model_endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if self.model_name in model.get('name', ''):
                        print(f"{GREEN}✅ EXAONE 3.5 모델 사용 가능{RESET}")
                        return True
            
            print(f"{YELLOW}⚠️ EXAONE 3.5 모델 미확인, 폴백 모드로 동작{RESET}")
            return False
        except Exception as e:
            print(f"{YELLOW}⚠️ 모델 연결 실패: {e}, 폴백 모드로 동작{RESET}")
            return False

    def generate_ai_response(self, character_name: str, personality_type: str, 
                           context: str, situation_type: str = "general") -> str:
        """AI 응답 생성 (EXAONE 3.5 기반)"""
        
        if self.model_available:
            return self._generate_with_exaone(character_name, personality_type, context, situation_type)
        else:
            return self._generate_fallback_response(character_name, personality_type, context, situation_type)

    def _generate_with_exaone(self, character_name: str, personality_type: str, 
                             context: str, situation_type: str) -> str:
        """EXAONE 3.5를 사용한 응답 생성"""
        try:
            # 캐릭터 데이터베이스에서 이전 경험 가져오기
            db = get_ai_database(character_name)
            recent_events = db.get_recent_learning_events(5)
            relationship = db.get_relationship("플레이어")
            
            # 프롬프트 구성
            system_prompt = self.personality_prompts.get(personality_type, "")
            
            # 상황별 추가 컨텍스트
            situation_context = ""
            if situation_type == "combat":
                situation_context = "현재 전투 중입니다. 전략적이고 신속한 판단이 필요합니다."
            elif situation_type == "exploration":
                situation_context = "던전을 탐험 중입니다. 주변 환경을 주의 깊게 살펴보세요."
            elif situation_type == "dialogue":
                situation_context = "동료들과 대화 중입니다. 자연스럽고 개성 있게 대화하세요."
            
            # 관계 정보 추가
            relationship_context = ""
            if relationship:
                trust = relationship.get('trust_level', 0.5)
                friendship = relationship.get('friendship_points', 0)
                relationship_context = f"플레이어와의 신뢰도: {trust:.1f}, 우정도: {friendship}"
            
            # 최종 프롬프트 생성
            full_prompt = f"""
{system_prompt}

게임 배경: {self.game_world_context}

캐릭터 정보:
- 이름: {character_name}
- 성격: {personality_type}
- {relationship_context}

현재 상황: {situation_context}
구체적 상황: {context}

위 정보를 바탕으로 {character_name}의 성격에 맞는 자연스러운 응답을 생성하세요.
응답은 한국어로, 50자 이내로 간단명료하게 작성하세요.
"""

            # EXAONE 3.5 API 호출
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "max_tokens": 100
                }
            }
            
            response = self.session.post(
                f"{self.model_endpoint}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                
                # 학습 데이터 저장
                self._save_learning_event(character_name, context, ai_response, situation_type)
                
                return ai_response
            else:
                print(f"{RED}EXAONE API 오류: {response.status_code}{RESET}")
                return self._generate_fallback_response(character_name, personality_type, context, situation_type)
                
        except Exception as e:
            print(f"{RED}EXAONE 생성 오류: {e}{RESET}")
            return self._generate_fallback_response(character_name, personality_type, context, situation_type)

    def _generate_fallback_response(self, character_name: str, personality_type: str, 
                                  context: str, situation_type: str) -> str:
        """폴백 응답 생성 (EXAONE 사용 불가시)"""
        
        # 성격별 기본 응답 패턴
        fallback_responses = {
            "용감한_리더": {
                "combat": ["정면으로 맞서자!", "내가 앞장설게!", "모두 함께 힘내자!"],
                "exploration": ["신중하게 탐색하자", "위험할 수 있으니 주의해", "내가 먼저 확인할게"],
                "dialogue": ["모두의 의견을 들어보자", "함께 결정하는 게 좋겠어", "책임을 지겠다"],
                "general": ["해보자!", "우리가 해낼 수 있어!", "함께라면 가능해!"]
            },
            "신중한_전략가": {
                "combat": ["전략이 필요해", "상황을 분석해보자", "계획적으로 접근하자"],
                "exploration": ["주의 깊게 살펴보자", "함정이 있을 수 있어", "정보 수집이 우선이야"],
                "dialogue": ["신중하게 생각해보자", "더 알아볼 필요가 있어", "분석이 필요해"],
                "general": ["생각해보자", "계획을 세우는 게 좋겠어", "신중하게 접근하자"]
            },
            "활발한_모험가": {
                "combat": ["신나는데!", "어서 시작하자!", "재미있을 것 같아!"],
                "exploration": ["뭔가 있을 것 같아!", "탐험이 재미있어!", "새로운 발견이 기대돼!"],
                "dialogue": ["좋은 생각이야!", "재미있겠다!", "빨리 해보자!"],
                "general": ["와! 좋아!", "정말 흥미로워!", "기대돼!"]
            },
            "냉정한_완벽주의자": {
                "combat": ["효율적으로 처리하자", "최적의 전략이 필요해", "완벽하게 실행하자"],
                "exploration": ["체계적으로 탐색하자", "놓치는 것이 없도록", "정확하게 조사해야 해"],
                "dialogue": ["논리적으로 생각하자", "효율성을 고려해야 해", "개선점이 보여"],
                "general": ["더 나은 방법이 있을 거야", "완벽하게 하자", "효율적이지 않아"]
            },
            "따뜻한_치유자": {
                "combat": ["모두 다치지 않게 조심해", "내가 치유해줄게", "안전이 우선이야"],
                "exploration": ["위험하지 않나 걱정돼", "다들 괜찮아?", "조심스럽게 가자"],
                "dialogue": ["모두의 마음이 중요해", "서로 배려하자", "걱정하지 마"],
                "general": ["괜찮아?", "도와줄게", "무리하지 마"]
            },
            "장난기_많은_트릭스터": {
                "combat": ["재미있는 방법이 있어!", "이거 어때?", "깜짝 놀랄 전술로!"],
                "exploration": ["숨겨진 것이 있을까?", "재미있는 비밀이 있을 거야!", "헤헤, 뭔가 있어!"],
                "dialogue": ["재미있는 아이디어가 있어!", "이런 건 어때?", "깜짝 놀랄 만한 걸로!"],
                "general": ["헤헤, 재미있겠다!", "창의적으로 해보자!", "예상치 못한 방법으로!"]
            }
        }
        
        # 해당 성격과 상황에 맞는 응답 선택
        personality_responses = fallback_responses.get(personality_type, fallback_responses["용감한_리더"])
        situation_responses = personality_responses.get(situation_type, personality_responses["general"])
        
        import random
        response = random.choice(situation_responses)
        
        # 학습 데이터 저장
        self._save_learning_event(character_name, context, response, situation_type, is_fallback=True)
        
        return response

    def _save_learning_event(self, character_name: str, context: str, response: str, 
                           situation_type: str, is_fallback: bool = False):
        """학습 이벤트 저장"""
        try:
            db = get_ai_database(character_name)
            
            event = LearningEvent(
                timestamp=datetime.now().isoformat(),
                event_type=f"ai_response_{situation_type}",
                context=context,
                action_taken=response,
                outcome="response_generated",
                feedback_score=0.7 if not is_fallback else 0.4,  # EXAONE 응답이 더 높은 점수
                emotional_weight=0.5
            )
            
            db.add_learning_event(event)
            
        except Exception as e:
            print(f"{RED}학습 이벤트 저장 실패: {e}{RESET}")

    def make_strategic_decision(self, character_name: str, personality_type: str, 
                              game_state: Dict, available_actions: List[str]) -> str:
        """전략적 의사결정 (전투/탐험 등)"""
        
        # 게임 상태 분석
        context = self._analyze_game_state(game_state)
        context += f"\n사용 가능한 행동: {', '.join(available_actions)}"
        
        if self.model_available:
            return self._make_decision_with_exaone(character_name, personality_type, context, available_actions)
        else:
            return self._make_fallback_decision(character_name, personality_type, game_state, available_actions)

    def _analyze_game_state(self, game_state: Dict) -> str:
        """게임 상태 분석"""
        analysis = []
        
        # HP/MP 상태
        if 'hp' in game_state and 'max_hp' in game_state:
            hp_percent = (game_state['hp'] / game_state['max_hp']) * 100
            analysis.append(f"HP: {hp_percent:.0f}%")
        
        if 'mp' in game_state and 'max_mp' in game_state:
            mp_percent = (game_state['mp'] / game_state['max_mp']) * 100
            analysis.append(f"MP: {mp_percent:.0f}%")
        
        # BRV 상태
        if 'brv' in game_state:
            analysis.append(f"BRV: {game_state['brv']}")
        
        # 적 정보
        if 'enemies' in game_state:
            enemy_count = len(game_state['enemies'])
            analysis.append(f"적 {enemy_count}명")
        
        # 파티 상태
        if 'party_hp' in game_state:
            party_status = []
            for member, hp_percent in game_state['party_hp'].items():
                if hp_percent < 30:
                    party_status.append(f"{member} 위험")
                elif hp_percent < 60:
                    party_status.append(f"{member} 주의")
            if party_status:
                analysis.append(f"파티: {', '.join(party_status)}")
        
        return " | ".join(analysis)

    def _make_decision_with_exaone(self, character_name: str, personality_type: str, 
                                  context: str, available_actions: List[str]) -> str:
        """EXAONE을 사용한 의사결정"""
        try:
            system_prompt = f"""
당신은 {personality_type} 성격의 {character_name}입니다.
게임 상황을 분석하고 최적의 행동을 선택하세요.

현재 상황: {context}
선택 가능한 행동: {', '.join(available_actions)}

위 상황에서 {character_name}의 성격에 맞는 최적의 행동 하나만 선택하세요.
선택 가능한 행동 중에서만 선택하고, 행동명만 답하세요.
"""

            payload = {
                "model": self.model_name,
                "prompt": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.6,  # 의사결정은 좀 더 일관되게
                    "top_p": 0.8,
                    "max_tokens": 50
                }
            }
            
            response = self.session.post(
                f"{self.model_endpoint}/api/generate",
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                decision = result.get('response', '').strip()
                
                # 유효한 행동인지 확인
                for action in available_actions:
                    if action in decision or decision in action:
                        return action
                
                # 유효하지 않으면 폴백
                return self._make_fallback_decision(character_name, personality_type, {}, available_actions)
                
        except Exception as e:
            print(f"{RED}EXAONE 의사결정 오류: {e}{RESET}")
        
        return self._make_fallback_decision(character_name, personality_type, {}, available_actions)

    def _make_fallback_decision(self, character_name: str, personality_type: str, 
                               game_state: Dict, available_actions: List[str]) -> str:
        """폴백 의사결정"""
        
        # 성격별 행동 우선순위
        decision_priorities = {
            "용감한_리더": ["공격", "방어", "도발", "수호"],
            "신중한_전략가": ["분석", "준비", "버프", "계획"],
            "활발한_모험가": ["탐험", "이동", "발견", "실험"],
            "냉정한_완벽주의자": ["최적화", "효율", "완벽", "개선"],
            "따뜻한_치유자": ["치유", "회복", "보호", "도움"],
            "장난기_많은_트릭스터": ["트릭", "변칙", "창의", "놀라움"]
        }
        
        priorities = decision_priorities.get(personality_type, ["공격", "방어", "이동"])
        
        # 우선순위에 따라 행동 선택
        for priority in priorities:
            for action in available_actions:
                if priority in action or action in priority:
                    return action
        
        # 모든 우선순위 매칭 실패시 첫 번째 행동 선택
        import random
        return random.choice(available_actions) if available_actions else "대기"

    def update_character_relationship(self, character_name: str, interaction_type: str, 
                                    interaction_result: str, feedback_score: float):
        """캐릭터 관계 업데이트"""
        try:
            db = get_ai_database(character_name)
            
            # 기존 관계 데이터 가져오기
            relationship = db.get_relationship("플레이어")
            
            if relationship:
                # 신뢰도 업데이트 (피드백 점수 기반)
                current_trust = relationship.get('trust_level', 0.5)
                trust_change = feedback_score * 0.1  # 최대 ±0.1 변화
                new_trust = max(0.0, min(1.0, current_trust + trust_change))
                
                # 우정 포인트 업데이트
                current_friendship = relationship.get('friendship_points', 0)
                friendship_change = max(0, int(feedback_score * 10))
                new_friendship = current_friendship + friendship_change
                
                # 기억에 남을 만한 이벤트 추가
                memorable_events = relationship.get('memorable_events', [])
                if feedback_score > 0.7 or feedback_score < -0.3:
                    memorable_events.append(f"{interaction_type}: {interaction_result}")
                    if len(memorable_events) > 10:  # 최대 10개까지만 기억
                        memorable_events = memorable_events[-10:]
                
                # 관계 데이터 업데이트
                updated_relationship = RelationshipData(
                    target_name="플레이어",
                    relationship_type="player",
                    trust_level=new_trust,
                    friendship_points=new_friendship,
                    last_interaction=datetime.now().isoformat(),
                    memorable_events=memorable_events
                )
                
                db.update_relationship(updated_relationship)
                
        except Exception as e:
            print(f"{RED}관계 업데이트 실패: {e}{RESET}")

# 글로벌 AI 엔진 인스턴스
ai_engine = ExaoneAIEngine()

def get_ai_engine() -> ExaoneAIEngine:
    """AI 엔진 인스턴스 반환"""
    return ai_engine

def test_exaone_ai_engine():
    """EXAONE AI 엔진 테스트"""
    print(f"{BRIGHT_CYAN}🧪 EXAONE AI 엔진 테스트{RESET}")
    
    engine = ExaoneAIEngine()
    
    # 테스트 시나리오들
    test_scenarios = [
        {
            "character": "레이나",
            "personality": "용감한_리더",
            "context": "던전에서 강력한 적을 만났습니다",
            "situation": "combat"
        },
        {
            "character": "아르카나", 
            "personality": "신중한_전략가",
            "context": "복잡한 함정이 있는 방을 발견했습니다",
            "situation": "exploration"
        },
        {
            "character": "실버",
            "personality": "냉정한_완벽주의자", 
            "context": "파티원들이 의견이 갈라졌습니다",
            "situation": "dialogue"
        }
    ]
    
    print(f"\n{YELLOW}=== AI 응답 생성 테스트 ==={RESET}")
    for scenario in test_scenarios:
        print(f"\n{WHITE}시나리오: {scenario['context']}{RESET}")
        print(f"{WHITE}캐릭터: {scenario['character']} ({scenario['personality']}){RESET}")
        
        response = engine.generate_ai_response(
            scenario['character'], 
            scenario['personality'],
            scenario['context'],
            scenario['situation']
        )
        
        print(f"{GREEN}응답: {response}{RESET}")
    
    # 의사결정 테스트
    print(f"\n{YELLOW}=== AI 의사결정 테스트 ==={RESET}")
    game_state = {
        'hp': 75,
        'max_hp': 100,
        'mp': 30,
        'max_mp': 50,
        'brv': 250,
        'enemies': ['고블린', '오크'],
        'party_hp': {'아르카나': 85, '실버': 40, '쉐도우': 60}
    }
    
    available_actions = ['공격', '방어', '치유 마법', '버프', '도망']
    
    decision = engine.make_strategic_decision(
        "레이나", "용감한_리더", game_state, available_actions
    )
    
    print(f"{GREEN}의사결정: {decision}{RESET}")
    
    print(f"\n{GREEN}✅ EXAONE AI 엔진 테스트 완료!{RESET}")

if __name__ == "__main__":
    test_exaone_ai_engine()
