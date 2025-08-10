# 🌟 Dawn of Stellar - AI 멀티플레이 시스템 설계 문서
**날짜: 2025년 8월 10일**  
**버전: 2.0 - 구현 완료 업데이트**  
**언어모델: EXAONE 3.5 - 7.8B**

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [🚀 2025.8.10 구현 완료 현황](#구현-완료-현황)
3. [게임 세계관 & AI 통합](#게임-세계관--ai-통합)
4. [AI 캐릭터 시스템](#ai-캐릭터-시스템)
5. [데이터베이스 구조](#데이터베이스-구조)
6. [멀티플레이 메커니즘](#멀티플레이-메커니즘)
7. [학습 시스템](#학습-시스템)
8. [구현 로드맵](#구현-로드맵)

---

## 🚀 **2025년 8월 10일 구현 완료 현황**

### ✅ **Phase 1: 기반 시스템 구축 - 완료**
- [x] **AI 캐릭터 데이터베이스 시스템** (`ai_character_database.py`)
- [x] **멀티플레이어 AI 캐릭터 생성기** (`multiplayer_ai_creator.py`)
- [x] **EXAONE 3.5 AI 엔진 통합** (`exaone_ai_engine.py`)
- [x] **캐릭터 프리셋 JSON 저장 시스템**

### ✅ **Phase 3: 게임 통합 - 완료**
- [x] **AI 멀티플레이어 런처** (`ai_multiplayer_launcher.py`)
- [x] **메인 게임 메뉴 통합** (`main.py` 수정)
- [x] **클래식 모드 완전 대체**
- [x] **기존 게임 시스템 완전 통합**

### 🔄 **Phase 2: AI 상호작용 구현 - 진행중**
- [x] AI-AI 기본 대화 시스템
- [x] 기본 협력 메커니즘
- [x] **커서 메뉴 시스템 완전 통합** ✅
- [ ] 고급 그룹 다이나믹스 시스템
- [ ] 캐릭터 간 관계 발전 시스템

### 🔧 **2025.8.10 오후 추가 작업 완료**

#### ✅ **커서 메뉴 시스템 완전 통합**
모든 AI 멀티플레이어 메뉴를 커서 메뉴 시스템으로 교체 완료:

1. **메인 메뉴** - `_display_main_menu()`
   - 7개 옵션 커서 메뉴 방식
   - 각 옵션별 상세 설명 추가
   - 폴백 시스템 지원

2. **캐릭터 생성 메뉴** - `_create_or_select_player_character()`
   - 3개 옵션 (새 캐릭터, 기존 캐릭터, AI 추천)
   - 직업 선택도 커서 메뉴로 변경
   - 직업별 상세 설명 제공

3. **AI와 대화 메뉴** - `_talk_with_ai()`
   - 동적 AI 목록 생성
   - 각 AI별 성격 정보 표시
   - 취소 옵션 지원

4. **AI 캐릭터 관리** - `_manage_ai_characters()`
   - 4개 관리 옵션 커서 메뉴
   - 상세 정보 선택도 커서 메뉴
   - 캐릭터별 프로필 정보 표시

5. **AI 훈련 모드** - `_ai_training_mode()`
   - 3개 훈련 옵션
   - 훈련 상태 설명 추가

6. **설정 메뉴** - `_settings_menu()`
   - 3개 설정 카테고리
   - 각 설정별 상세 설명

#### ✅ **오류 수정 완료**
1. **Import 오류**: `game.party_manager` 제거
2. **변수 오류**: `white` 함수 import 추가
3. **메뉴 일관성**: 모든 메뉴 커서 메뉴로 통일

#### 🎯 **사용자 경험 개선**
- 일관된 네비게이션 (방향키 + Enter)
- 상세한 옵션 설명 제공
- 취소 기능 모든 메뉴에 추가
- 폴백 시스템으로 안정성 보장

### 📋 **Phase 4-5: 고급 기능 - 계획됨**
- [ ] 동적 난이도 조절
- [ ] AI 전술 진화
- [ ] 플레이어 적응 시스템
- [ ] 성능 최적화 및 완성

---

---

## 🌟 Phase 4: 고급 AI 기능 구현 ✅ (2025.08.10 완료)

### 4.1 AI 상호작용 시스템 ✅
- [x] 26가지 감정 상태 기반 상호작용 (HAPPY, SAD, ANGRY, EXCITED 등)
- [x] 그룹 다이나믹스 시뮬레이션 (파티 내 감정 전파)
- [x] 감정 전파 및 상호 영향 (긍정/부정 영향 계산)
- **구현 파일**: `ai_interaction_system.py`
- **핵심 기능**: 
  - AIInteraction 데이터클래스로 상호작용 추적
  - GroupDynamics를 통한 파티 전체 분위기 관리
  - 10가지 상호작용 타입 (대화, 협력, 갈등, 지원 등)

### 4.2 협력 메커니즘 ✅
- [x] 8가지 협력 유형 (COMBAT_COMBO, HEALING_SUPPORT, BUFF_CHAIN 등)
- [x] 직업 간 시너지 시스템 (6개 시너지 페어: 전사+성기사, 궁수+도적 등)
- [x] 협력 공격 및 지원 시스템 (3개 기본 액션: combo_attack, healing_circle, magic_chain)
- **구현 파일**: `ai_cooperation_system.py`
- **핵심 기능**:
  - CooperationAction 데이터클래스로 협력 행동 정의
  - 직업별 시너지 보너스 계산 (1.2x ~ 1.8x)
  - 메뉴 시스템을 통한 실시간 협력 선택

### 4.3 고급 AI 전술 ✅
- [x] 6가지 전술 역할 (TANK, DPS, HEALER, SUPPORT, CONTROLLER, SCOUT)
- [x] 상황 분석 및 의사결정 엔진 (BattleSituation 기반)
- [x] 포메이션 및 전략 최적화 (6가지 포메이션: DEFENSIVE, OFFENSIVE, BALANCED 등)
- **구현 파일**: `ai_tactical_system.py`
- **핵심 기능**:
  - 실시간 전투 상황 분석 (적 수, 지형, 파티 상태)
  - AI별 맞춤 전술 행동 (6가지 역할별 고유 행동)
  - 논리적 추론 시스템으로 AI 의사결정 설명

### 4.4 27개 직업 확장 ✅
- [x] 모든 직업의 AI 특성 정의 (성격, 감정성향, 협력스타일)
- [x] 직업별 고유 행동 패턴 및 대화 패턴 (JobProfile 체계)
- [x] 직업 간 상성 및 관계 시스템 (협력선호도, 대립관계)
- **구현 파일**: 
  - `complete_27_job_system.py` (직업 체계)
  - `ai_27job_character_creator.py` (캐릭터 자동 생성)
- **핵심 기능**:
  - 3개 카테고리 (전투 8개, 마법 10개, 특수 9개)
  - 각 직업별 시공교란 스토리 배경 설정
  - AI 성격 특성 매핑 (용감한→대담한/무모한 등)

### 4.5 통합 허브 시스템 ✅
- [x] 모든 AI 시스템 통합 관리 (AIMultiplayerHub)
- [x] 파티 관리 및 전투 시뮬레이션 (자동 파티 구성, 균형 체크)
- [x] 실제 게임과의 연동 인터페이스 (JSON 기반 파티 정보 저장)
- **구현 파일**: `ai_multiplayer_integrated_hub.py`
- **핵심 기능**:
  - 통합 메뉴 시스템 (8개 주요 기능)
  - 실시간 시스템 상태 모니터링
  - 파티 정보 저장으로 main.py와 연동

### 4.6 완성된 AI 멀티플레이어 기능
- **자동 캐릭터 생성**: 직업별 맞춤형 AI 캐릭터 자동 생성
- **균형잡힌 파티**: 역할별 최소 1명씩 보장하는 파티 구성
- **실시간 상호작용**: 26가지 감정 기반 AI 간 대화
- **협력 전투**: 8가지 협력 유형으로 전략적 전투
- **전술 AI**: 상황 분석 후 최적 행동 선택
- **성장 시스템**: AI별 독립적 학습 및 성장

---

## 🎯 시스템 개요

### 핵심 비전
- **클래식 모드 → AI 멀티플레이 모드로 완전 대체**
- **EXAONE 3.5 기반 지능형 AI 동료 시스템**
- **캐릭터별 독립적 AI 성격 & 학습 데이터**
- **실시간 AI 상호작용 & 협력 플레이**
- **24시간 백그라운드 학습 시스템**

### 기술 스택
```
언어모델: EXAONE 3.5 - 7.8B (로컬 실행)
데이터베이스: SQLite (캐릭터별 분리)
게임 엔진: Python 기반 Dawn of Stellar
AI 프레임워크: 자체 개발 (언어모델 연동)
학습 데이터: JSON + SQLite 하이브리드
```

---

## 🌍 게임 세계관 & AI 통합

### Dawn of Stellar 세계관
```
🌟 차원간 모험가들의 이야기
- 28개 직업 클래스가 존재하는 판타지 세계
- 로그라이크 던전 탐험 & JRPG 전투 시스템
- ATB(Active Time Battle) + BRV(Brave Point) 시스템
- 상처 시스템으로 현실적인 생존 메커니즘
- 파티 기반 협력 플레이 (최대 4명)
```

### AI 캐릭터의 역할
```
🤖 지능형 동료 시스템
- 각자 고유한 성격과 배경 스토리
- 직업별 전문 지식과 전투 스타일
- 플레이어와의 관계 발전 (신뢰도 시스템)
- 상황별 적응적 대화 & 행동
- 게임 진행에 따른 성장과 학습
```

---

## 🎭 AI 캐릭터 시스템

### 캐릭터 프로필 구조
```json
{
  "basic_info": {
    "name": "레이나",
    "class": "전사",
    "gender": "female",
    "age": 25,
    "personality_type": "용감한_리더",
    "speech_style": "격식있는_말투"
  },
  "ai_profile": {
    "core_personality": {
      "traits": ["용감함", "책임감", "정의감"],
      "interests": ["전술", "무기_연구", "파티_보호"],
      "fears": ["동료_손실", "책임_회피", "불의"],
      "motivations": ["모두를_지키고_싶음", "강해지고_싶음"]
    },
    "professional_knowledge": {
      "expertise": ["방어_전술", "탱킹_기술", "파티_보호"],
      "preferred_skills": ["방패_강타", "수호_의지", "파괴의_일격"],
      "combat_style": "최전선_탱커",
      "weakness_analysis": "속도가_느림, MP가_부족함"
    },
    "relationship_data": {
      "trust_level": 0.5,
      "friendship_points": 0,
      "memorable_events": [],
      "communication_history": []
    }
  },
  "learning_data": {
    "database_file": "ai_memory_레이나.db",
    "learning_sessions": 0,
    "experience_points": 0,
    "skill_development": {},
    "behavioral_patterns": {}
  }
}
```

### 성격 타입 시스템 (확장형)
```python
PERSONALITY_TYPES = {
    "용감한_리더": {
        "speech_patterns": ["정면으로 맞서자!", "내가 앞장설게!", "모두 힘내!"],
        "decision_style": "적극적이고 과감한 선택",
        "combat_preference": "최전선에서 적극적 공격",
        "social_behavior": "리더십 발휘, 동료 격려"
    },
    "신중한_전략가": {
        "speech_patterns": ["좀 더 생각해보자", "전략이 필요해", "신중하게 접근하자"],
        "decision_style": "분석적이고 계획적인 선택",
        "combat_preference": "상황 분석 후 최적 행동",
        "social_behavior": "조언 제공, 계획 수립"
    },
    "활발한_모험가": {
        "speech_patterns": ["와! 재미있겠다!", "빨리 가자!", "새로운 걸 발견했어!"],
        "decision_style": "직감적이고 즉흥적인 선택",
        "combat_preference": "다양한 스킬 실험",
        "social_behavior": "분위기 띄우기, 호기심 표현"
    },
    "냉정한_완벽주의자": {
        "speech_patterns": ["효율적이지 않군", "완벽하게 처리하자", "실수는 용납할 수 없어"],
        "decision_style": "논리적이고 완벽한 선택",
        "combat_preference": "최적화된 스킬 사용",
        "social_behavior": "실력 중시, 완벽 추구"
    },
    "따뜻한_치유자": {
        "speech_patterns": ["괜찮아?", "도와줄게", "모두 무사하길 바라"],
        "decision_style": "공감적이고 배려하는 선택",
        "combat_preference": "아군 지원과 회복 우선",
        "social_behavior": "돌봄, 치유, 공감"
    },
    "장난기_많은_트릭스터": {
        "speech_patterns": ["이거 어때?", "재미있는 방법이 있어!", "헤헤, 속았지?"],
        "decision_style": "창의적이고 예측불가한 선택",
        "combat_preference": "예상치 못한 전술 사용",
        "social_behavior": "유머, 장난, 창의성"
    }
}
```

---

## 💾 데이터베이스 구조

### 파일 구조
```
ai_databases/
├── ai_memory_레이나.db          # 전사 레이나 전용 DB
├── ai_memory_아르카나.db        # 아크메이지 아르카나 전용 DB
├── ai_memory_실버.db            # 궁수 실버 전용 DB
├── ai_memory_쉐도우.db          # 도적 쉐도우 전용 DB
└── ...                          # 캐릭터별 개별 DB

character_presets/
├── preset_레이나.json           # 레이나 캐릭터 설정
├── preset_아르카나.json         # 아르카나 캐릭터 설정
└── ...                          # 캐릭터별 프리셋

shared_data/
├── game_world_knowledge.json    # 게임 세계관 공통 지식
├── class_abilities.json         # 직업별 능력 데이터
└── item_database.json           # 아이템 정보 DB
```

### AI 메모리 DB 스키마
```sql
-- 학습 이벤트 저장
CREATE TABLE learning_events (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    event_type TEXT,  -- 'combat', 'dialogue', 'exploration', 'decision'
    context TEXT,     -- 상황 설명
    action_taken TEXT, -- AI가 취한 행동
    outcome TEXT,     -- 결과
    feedback_score REAL, -- 피드백 점수 (-1.0 ~ 1.0)
    emotional_weight REAL -- 감정적 중요도
);

-- 관계 데이터
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    target_name TEXT,  -- 상대방 이름 (플레이어 또는 다른 AI)
    relationship_type TEXT, -- 'player', 'ai_companion', 'npc'
    trust_level REAL,
    friendship_points INTEGER,
    last_interaction TEXT,
    memorable_events TEXT -- JSON 형태로 저장
);

-- 게임 지식
CREATE TABLE game_knowledge (
    id INTEGER PRIMARY KEY,
    category TEXT,    -- 'monster', 'item', 'strategy', 'location'
    subject TEXT,     -- 구체적 대상
    knowledge TEXT,   -- 학습한 지식 내용
    confidence_level REAL, -- 지식의 확신도
    last_updated TEXT
);

-- 행동 패턴
CREATE TABLE behavioral_patterns (
    id INTEGER PRIMARY KEY,
    situation_type TEXT, -- 상황 유형
    action_pattern TEXT, -- 행동 패턴
    success_rate REAL,   -- 성공률
    usage_count INTEGER, -- 사용 횟수
    last_used TEXT
);

-- 감정 상태 기록
CREATE TABLE emotional_states (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    emotion_type TEXT,   -- 'happy', 'excited', 'worried', 'angry', 'sad'
    intensity REAL,      -- 강도 (0.0 ~ 1.0)
    trigger_event TEXT,  -- 감정을 일으킨 사건
    duration INTEGER     -- 지속 시간 (분)
);
```

---

## 🎮 멀티플레이 메커니즘

### AI 협력 시스템
```python
class AICooperationManager:
    """AI들 간의 협력과 상호작용 관리"""
    
    def __init__(self):
        self.ai_companions = {}  # AI 동료들
        self.group_dynamics = {} # 그룹 역학
        self.communication_log = [] # 대화 기록
    
    def process_ai_interactions(self):
        """AI들 간의 상호작용 처리"""
        # 1. 전투 중 AI 협력
        # 2. 일상 대화 및 관계 발전
        # 3. 의견 충돌 및 해결
        # 4. 그룹 의사결정
        pass
    
    def coordinate_combat_actions(self):
        """전투 중 AI 조율"""
        # ATB 시스템과 연동하여
        # AI들이 서로 협력하는 행동 선택
        pass
```

### 턴제 AI 행동 시스템
```python
class AITurnManager:
    """AI의 턴별 행동 관리"""
    
    def ai_turn_decision(self, ai_character, battle_state):
        """AI 턴에서의 의사결정"""
        # 1. 상황 분석 (EXAONE 3.5 기반)
        # 2. 성격에 따른 행동 선택
        # 3. 다른 AI와의 협력 고려
        # 4. 최종 행동 결정
        
        context = self.analyze_battle_context(battle_state)
        personality_filter = ai_character.get_personality_filter()
        action = self.exaone_decision_engine(context, personality_filter)
        
        return action
```

---

## 🧠 학습 시스템

### 실시간 학습 (게임플레이 중)
```python
class RealTimeLearning:
    """게임플레이 중 실시간 학습"""
    
    def observe_and_learn(self, event_data):
        """게임 이벤트 관찰 및 학습"""
        # 1. 전투 결과 분석
        # 2. 플레이어 행동 패턴 학습
        # 3. 효과적인 전략 기록
        # 4. 실패 사례 분석
        
    def update_knowledge_base(self, new_knowledge):
        """지식 베이스 업데이트"""
        # SQLite DB에 새로운 지식 저장
        # 기존 지식과의 충돌 해결
        # 신뢰도 기반 가중치 적용
```

### 백그라운드 학습 (수면 시간)
```python
class BackgroundLearning:
    """백그라운드 ML 학습 시스템"""
    
    def nightly_training_session(self):
        """야간 집중 학습 세션"""
        # 1. 하루 데이터 정리 및 분석
        # 2. 패턴 인식 및 최적화
        # 3. 성격 모델 미세 조정
        # 4. 대화 모델 개선
        
    def cross_character_learning(self):
        """캐릭터 간 지식 공유"""
        # 일반적인 게임 지식은 공유
        # 개인적 경험은 유지
        # 성격별 해석 차이 보존
```

### 학습 데이터 종류
```yaml
전투 학습:
  - 스킬 효과성 분석
  - 적 약점 파악
  - 파티 조합 최적화
  - 자원 관리 전략

사회적 학습:
  - 플레이어 선호도 파악
  - 대화 패턴 학습
  - 감정 반응 분석
  - 관계 발전 전략

게임 세계 학습:
  - 아이템 가치 평가
  - 던전 구조 기억
  - NPC 정보 축적
  - 퀘스트 패턴 인식
```

---

## 🛠️ 구현 로드맵

### Phase 1: 기반 시스템 구축 (1주차)
- [ ] AI 캐릭터 데이터베이스 설계 및 구현
- [ ] 캐릭터 프리셋 시스템 확장
- [ ] EXAONE 3.5 연동 기본 프레임워크
- [ ] 기본 AI 성격 시스템

### Phase 2: AI 상호작용 구현 (2주차)
- [ ] AI-플레이어 대화 시스템
- [ ] AI-AI 상호작용 메커니즘
- [ ] 감정 시스템 및 관계 발전
- [ ] 기본 학습 데이터 수집

### Phase 3: 멀티플레이 시스템 (3주차)
- [ ] 클래식 모드 → AI 멀티플레이 전환
- [ ] 협력 전투 시스템 구현
- [ ] 그룹 의사결정 시스템
- [ ] AI 행동 조율 메커니즘

### Phase 4: 학습 시스템 고도화 (4주차)
- [ ] 실시간 학습 엔진 구현
- [ ] 백그라운드 학습 시스템
- [ ] 성격 모델 최적화
- [ ] 크로스 캐릭터 지식 공유

### Phase 5: 통합 및 최적화 (5주차)
- [ ] 게임 런처 개조
- [ ] 전체 시스템 통합 테스트
- [ ] 성능 최적화
- [ ] 사용자 경험 개선

---

## 🎯 핵심 기능 명세

### 1. AI 캐릭터 생성기 확장
```python
def create_ai_character_with_full_profile():
    """AI 전용 캐릭터 생성"""
    # 기본 RPG 스탯 + AI 성격 프로필
    # 개별 데이터베이스 생성
    # 초기 학습 데이터 세팅
    # 성격별 대화 패턴 로드
```

### 2. 게임 런처 개조
```python
def launch_ai_multiplayer_mode():
    """AI 멀티플레이 모드 런처"""
    # 클래식 모드 대체
    # AI 동료 3명 자동 로드
    # 백그라운드 학습 프로세스 시작
    # 실시간 AI 상호작용 활성화
```

### 3. EXAONE 3.5 연동
```python
class ExaoneAIEngine:
    """EXAONE 3.5 기반 AI 엔진"""
    
    def generate_contextual_response(self, context, personality):
        """상황별 AI 응답 생성"""
        # 게임 상황 + 성격 특성 → 자연스러운 대화
        
    def make_strategic_decision(self, game_state, character_data):
        """전략적 의사결정"""
        # 전투/탐험 상황에서 최적 행동 선택
```

---

## 📊 성공 지표

### 기술적 지표
- AI 응답 시간: < 2초
- 학습 데이터 축적: 일평균 100+ 이벤트
- 캐릭터별 개성 구분도: 80%+
- 시스템 안정성: 99%+ 업타임

### 사용자 경험 지표
- AI 동료의 자연스러움: 주관적 평가 8/10+
- 게임 몰입도 향상: 기존 대비 30%+
- 플레이 시간 증가: 평균 50%+
- AI 학습 체감도: 일주일 내 변화 감지

---

## � Dawn of Stellar 스토리 시스템 분석 (2025.08.10)

### 🌟 스토리 시스템 핵심 특징
**세계관: 시공교란 컨셉의 SF 판타지 로그라이크**
- **시간적 배경**: 서기 2157년, 차원 실험 실패로 인한 시공간 왜곡
- **핵심 컨셉**: 시간과 공간의 법칙이 무너진 혼돈의 세계
- **주인공 설정**: 차원 항해사로서 시공간 혼돈 속에서 길을 찾는 모험가

### 🎭 주요 스토리 요소
#### 세피로스 시스템 (악역)
- **캐릭터**: 스텔라 연구소의 천재 과학자, 차원 실험의 진정한 흑막
- **글리치 모드**: 세피로스 조우 후 모든 텍스트에 글리치 효과 적용
- **진 엔딩 모드**: 세피로스 처치 후 해금되는 복구된 스토리
- **공포 요소**: 극도로 무서운 변조된 스토리, 글리치 텍스트, 비프음 효과

#### 시공교란 설정
- **과거와 미래 혼재**: 그리스 철학자가 컴퓨터로 작업, 해적이 우주선 조종
- **물리법칙 붕괴**: 중력 변화, 거리 개념 소실, 시간 역행/정지
- **융합 문명**: 서로 다른 시대의 기술과 문화가 충돌하며 새로운 가능성 창조

### 🎮 스토리 시스템 기술 구조
#### StorySegment 클래스
- **타이핑 효과**: 문자별 딜레이와 색상 지정
- **다양한 스토리 타입**: 오프닝, 캐릭터 소개, 전투, 엔딩 등
- **상황별 BGM**: 오디오 시스템과 연동

#### 글리치 효과 시스템
- **8가지 글리치 타입**: 문자 교체, 손상, 공포 문자, 연쇄 손상 등
- **무작위성**: 완전 랜덤한 글리치 위치와 강도
- **세피로스 특화**: 세피로스 관련 텍스트에서 더 강한 글리치

### 🎪 직업별 배경 스토리 (27개 직업)
#### 시공교란 설정에 맞는 직업 혼재
- **고대 직업**: 그리스 철학자, 해적, 기사, 사무라이, 드루이드
- **현대 직업**: 기계공학자, 과학자, 의료진
- **판타지 직업**: 마법사, 성기사, 암흑기사, 네크로맨서
- **미래 직업**: 차원술사, 시간술사, 사이버네틱 전문가

### 🎵 오디오 연동 시스템
#### 스토리별 BGM
- **오프닝**: BOMBING_MISSION (FF7 스타일)
- **글리치 모드**: 공포 음향 효과, 랜덤 비프음
- **진 엔딩**: 평화로운 복구 음악

#### 효과음 시스템
- **글리치 효과음**: 텍스트 타이핑 중 5% 확률 비프음
- **세피로스 전용음**: 긴 불길한 비프음
- **상황별 SFX**: 캐릭터 행동에 맞는 효과음

### 🚀 AI 캐릭터용 스토리 프롬프트 요소
#### 핵심 설정 정보
```
세계관: 2157년 시공교란으로 모든 시대가 뒤섞인 혼돈의 세계
당신의 역할: 차원 항해사의 동료 또는 라이벌
시대적 특징: 과거의 지혜와 미래의 기술이 공존하는 융합 문명
위험 요소: 세피로스라는 악역 과학자의 존재
특수 상황: 글리치 모드에서는 메모리 오류와 데이터 손상 체험
```

---

## �🔮 미래 확장 계획

### 고급 AI 기능
- 창의적 전략 개발 능력
- 복잡한 감정 표현
- 플레이어별 맞춤 적응
- 메타 게임 이해

### 커뮤니티 기능
- AI 캐릭터 공유 시스템
- 커뮤니티 학습 데이터 풀
- AI 캐릭터 토너먼트
- 사용자 생성 AI 성격

---

## 📝 개발 노트

### 중요 고려사항
1. **성능 최적화**: EXAONE 3.5 로컬 실행 최적화
2. **데이터 관리**: 캐릭터별 DB 분리로 개별성 보장
3. **학습 효율**: 실시간 + 백그라운드 하이브리드 학습
4. **사용자 경험**: 자연스러운 AI 상호작용

### 기술적 도전
1. 언어모델 로컬 실행 최적화
2. 실시간 학습과 게임 성능 균형
3. AI 성격의 일관성 유지
4. 대화의 자연스러움 확보

---

**🎉 결론: Dawn of Stellar은 이제 단순한 게임을 넘어서 AI 동료들과 함께 성장하는 살아있는 세계가 됩니다!**
