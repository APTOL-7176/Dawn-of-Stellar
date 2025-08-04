# Copilot Instructions for Dawn of Stellar - Complete Game Documentation

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilot-instructions-md-file -->

## 🌟 Project Overview: Dawn of Stellar
**완전체 Python 기반 로그라이크 RPG 게임**

### 🎯 Core Game Vision
- **장르**: 클래식 로그라이크 + 현대적 JRPG 요소 융합
- **스타일**: ASCII/유니코드 문자 기반 그래픽
- **플랫폼**: Windows/Linux/Mac 크로스 플랫폼
- **언어**: Python 3.10+ (완전 한국어 지원)
- **테마**: 모험 + 판타지 세계관

## 🎮 Complete Game Systems

### 1. 🏰 던전 시스템 (Dungeon System)
- **던전 생성**: 절차적 생성 알고리즘
- **던전 타입**: 일반, 특수, 보스, 히든 던전
- **층수 시스템**: 무한 층수 진행 (100층까지 구현)
- **미니맵**: 실시간 탐험 지도
- **함정 시스템**: 독, 폭발, 순간이동 함정
- **보물상자**: 일반, 마법, 전설 등급 상자
- **환경 상호작용**: 문, 레버, 비밀통로

### 2. ⚔️ 전투 시스템 (Brave Combat System)
#### ATB (Active Time Battle) 시스템
- **게이지 시스템**: 0~10000 범위 (100배 정밀도)
- **속도 기반**: 캐릭터 속도에 따른 행동 순서
- **실시간 업데이트**: 부드러운 게이지 애니메이션

#### Brave Point 시스템
- **BRV 축적**: Brave 공격으로 포인트 획득
- **HP 공격**: BRV 소모하여 실제 피해
- **BREAK 시스템**: BRV 0일 때 무력화 상태
- **INT BRV**: 턴 시작 시 기본 BRV 회복

#### 상처 시스템 (Wound System)
- **상처 축적**: 받은 피해의 25%가 상처로 누적
- **최대 상처**: 최대 HP의 75%까지 제한
- **상처 치유**: 초과 회복의 25%로 상처 치료
- **영구 피해**: 상처는 전투 종료 후에도 지속

### 3. 👥 파티 관리 시스템 (Party Management)
- **파티 크기**: 최대 4명 구성
- **직업 시스템**: 27개 고유 직업
- **동료 시스템**: NPC 동료 영입
- **AI 동료**: 자동 전투 AI 탑재
- **파티 밸런스**: 탱커, 딜러, 힐러, 서포터 역할 분담

### 4. 🎓 직업 시스템 (Character Classes)
#### 전투 직업군
- **전사**: 방패 강타, 파괴의 일격
- **아크메이지**: 마력 파동, 마력 폭발
- **궁수**: 삼연사, 관통사격
- **도적**: 독침, 암살
- **성기사**: 성스러운 타격, 심판의 빛
- **암흑기사**: 흡혈 베기, 흡혈 강타
- **몽크**: 연환 타격, 폭렬권
- **바드**: 음파 공격, 영혼의 노래

#### 마법 직업군
- **네크로맨서**: 생명력 흡수, 영혼 흡수
- **용기사**: 화염 강타, 드래곤 브레스
- **검성**: 검기 베기, 일섬
- **정령술사**: 원소 탄환, 원소 융합
- **시간술사**: 시간 조작, 시간 정지
- **연금술사**: 화학 폭발, 대폭발 반응
- **차원술사**: 차원 균열, 차원 붕괴

#### 특수 직업군
- **암살자**: 그림자 습격, 그림자 처형
- **기계공학자**: 레이저 사격, 메가 레이저
- **무당**: 영혼 타격, 영혼 분리
- **해적**: 이도류 난타, 해적의 보물
- **사무라이**: 거합 베기, 무사도 비의
- **드루이드**: 자연의 분노, 자연의 심판
- **철학자**: 논리적 반박, 진리의 깨달음
- **검투사**: 투기장 기술, 검투장의 피날레
- **기사**: 창 돌격, 성스러운 돌격
- **신관**: 축복의 빛, 신의 심판
- **마검사**: 마법검기, 마검 오의
- **광전사**: 광폭화 난타, 최후의 광기

### 5. ✨ 스킬 시스템 (Skill System)
#### 스킬 타입
- **BRV_ATTACK**: Brave 포인트 획득 공격
- **HP_ATTACK**: 직접 HP 피해 공격
- **BRV_HP_ATTACK**: BRV 획득 + HP 피해 복합
- **ULTIMATE**: 궁극기 (높은 MP 소모)
- **SUPPORT**: 지원/회복 스킬
- **DEBUFF**: 적 약화 스킬

#### 캐스팅 시스템
- **캐스트 타임**: 스킬별 시전 시간
- **중단 가능**: 피해 받으면 캐스팅 중단
- **ATB 연동**: 캐스팅 중 ATB 게이지 표시

### 6. 🎒 인벤토리 & 아이템 시스템
#### 아이템 카테고리
- **소모품**: 회복 포션, 버프 아이템
- **장비**: 무기, 방어구, 액세서리
- **재료**: 제작 재료, 강화 석
- **귀중품**: 퀘스트 아이템, 수집품

#### 제작 시스템 (Crafting)
- **요리 시스템**: 음식 제작으로 버프 효과
- **연금술**: 포션 및 특수 아이템 제작
- **강화 시스템**: 장비 강화 및 인챈트

### 7. 🧬 특성 시스템 (Trait System)
#### 특성 타입
- **패시브 특성**: 항상 활성화된 효과
- **액티브 특성**: 수동 발동 특성
- **전투 특성**: 전투 중 자동 발동
- **조건부 특성**: 특정 조건에서 발동

#### 특성 예시
- **동물 변신**: 늑대/곰/독수리 형태 변환
- **원소 친화**: 원소 마법 위력 증가
- **전투 광**: 체력 낮을수록 공격력 증가
- **치유술사**: 회복 효과 2배 증가

### 8. 🤖 AI 시스템 (AI Game Mode)
#### AI 동료 시스템
- **자동 전투**: AI가 최적 행동 선택
- **전략적 판단**: 상황 분석 후 행동 결정
- **협력 플레이**: 플레이어와 협력 전술
- **학습 능력**: 플레이 패턴 학습 및 적응

#### AI 행동 패턴
- **공격**: 최적 타겟 선택
- **스킬**: 상황별 스킬 사용
- **방어**: 위험 상황 시 방어
- **치료**: 아군 체력 관리
- **아이템**: 필요 시 아이템 사용
- **요청**: 플레이어에게 지시 요청

### 9. 🎵 오디오 시스템 (Audio System)
#### BGM 시스템
- **상황별 BGM**: 던전, 전투, 마을, 보스
- **동적 전환**: 상황에 따른 자연스러운 전환
- **루프 재생**: 끊김 없는 배경음악

#### SFX 시스템
- **전투음**: 공격, 스킬, 방어음
- **환경음**: 발걸음, 문 여는 소리
- **UI음**: 메뉴, 선택, 확인음

### 10. 💾 저장 시스템 (Save System)
#### 저장 데이터
- **캐릭터 진행도**: 레벨, 경험치, 스탯
- **인벤토리**: 아이템, 장비, 돈
- **던전 진행**: 탐험한 층수, 맵 정보
- **퀘스트**: 진행 중/완료된 퀘스트
- **설정**: 게임 설정, 키 바인딩

#### 자동 저장
- **던전 진입**: 새 층 진입 시 자동 저장
- **전투 승리**: 중요 전투 후 자동 저장
- **상점 이용**: 거래 완료 후 자동 저장

### 11. 🎯 난이도 시스템 (Difficulty System)
- **쉬움**: 초보자용 (피해 -30%, 경험치 +20%)
- **보통**: 표준 난이도
- **어려움**: 도전적 (피해 +50%, 경험치 +50%)
- **지옥**: 극한 도전 (피해 +100%, 특수 보상)

### 12. 🏆 업적 시스템 (Achievement System)
- **전투 업적**: 연속 승리, 완벽한 승리
- **탐험 업적**: 층수 도달, 비밀 발견
- **수집 업적**: 아이템 수집, 도감 완성
- **특수 업적**: 숨겨진 조건 달성

## 🛠️ Technical Architecture

### Core Modules
```python
main.py                 # 게임 메인 엔트리 포인트
config.py              # 게임 설정 관리
game/
├── brave_combat.py    # 전투 시스템 핵심
├── character.py       # 캐릭터 클래스
├── party_manager.py   # 파티 관리
├── dungeon_system.py  # 던전 생성/관리
├── skill_system.py    # 스킬 데이터베이스
├── item_system.py     # 아이템 관리
├── ai_game_mode.py    # AI 시스템
├── trait_system.py    # 특성 시스템
├── audio_system.py    # 오디오 관리
└── save_system.py     # 저장/로드
```

### 🎨 UI/UX Systems
#### Display Systems
- **BufferedDisplay**: 화면 깜빡임 방지
- **ColorSystem**: 256색 컬러 시스템
- **CursorMenu**: 커서 기반 메뉴
- **GameDisplay**: 게임 화면 렌더링

#### Input Systems
- **KeyboardInput**: 키보드 입력 처리
- **MenuNavigation**: 메뉴 탐색 시스템
- **HotkeySystem**: 단축키 시스템

### 🔧 Utility Systems
- **GameStateEncoder**: JSON 직렬화
- **ErrorHandler**: 예외 처리
- **PerformanceMonitor**: 성능 모니터링
- **DebugSystem**: 디버그 기능

## 📊 Game Balance & Mechanics

### Damage Formula
```python
기본_피해 = (공격력 / 방어력) * 스킬_배율
최종_피해 = 기본_피해 * 특성_배율 * 상태_배율
BRV_피해 = 최종_피해 * BRV_배율
HP_피해 = BRV_포인트 * HP_배율
```

### Status Effects
- **독**: 턴마다 HP 감소
- **화상**: 행동 시 추가 피해
- **빙결**: 행동 불가
- **마비**: 확률적 행동 실패
- **축복**: 모든 능력치 증가
- **저주**: 모든 능력치 감소

### Critical System
- **크리티컬 확률**: 기본 5% + 운 스탯
- **크리티컬 배율**: 1.5배 ~ 2.0배
- **크리티컬 효과**: 추가 상태이상 부여

## 🎮 Code Style Guidelines

### Naming Conventions
- **변수명**: snake_case (한글 주석 포함)
- **클래스명**: PascalCase
- **함수명**: snake_case
- **상수명**: UPPER_SNAKE_CASE

### Design Patterns
- **Singleton**: 게임 매니저 클래스들
- **Factory**: 캐릭터/아이템 생성
- **Observer**: 이벤트 시스템
- **Strategy**: AI 행동 패턴
- **Command**: 액션 시스템

### Error Handling
```python
try:
    # 게임 로직
    result = perform_action()
except GameException as e:
    # 게임 내 예외 처리
    handle_game_error(e)
except Exception as e:
    # 시스템 예외 처리
    log_error(e)
    show_error_dialog()
```

## 🚀 Performance Optimization

### Memory Management
- **객체 풀링**: 자주 생성되는 객체 재사용
- **지연 로딩**: 필요할 때만 리소스 로드
- **가비지 컬렉션**: 수동 메모리 정리

### Display Optimization
- **더블 버퍼링**: 화면 깜빡임 방지
- **부분 업데이트**: 변경된 부분만 다시 그리기
- **프레임 제한**: 60 FPS 제한

## 🐛 Debugging & Testing

### Debug Features
- **치트 모드**: 개발자 전용 치트
- **로그 시스템**: 상세 게임 로그
- **상태 확인**: 실시간 게임 상태 모니터링

### Testing Strategy
- **단위 테스트**: 개별 함수 테스트
- **통합 테스트**: 시스템 간 연동 테스트
- **플레이 테스트**: 실제 게임플레이 테스트

## 🔮 Future Expansion Plans

### Planned Features
- **멀티플레이어**: 온라인 협동/대전
- **모드 시스템**: 사용자 제작 콘텐츠
- **시즌 시스템**: 정기 업데이트 콘텐츠
- **토너먼트**: 경쟁 모드

### Technical Improvements
- **3D 그래픽**: 3D 모델 지원
- **음성 지원**: 캐릭터 음성
- **클라우드 저장**: 온라인 저장 시스템

## 🎯 Game Development Philosophy

### Core Principles
1. **플레이어 경험 우선**: 재미와 몰입감
2. **접근성**: 누구나 쉽게 시작
3. **깊이**: 마스터하기 어려운 깊이
4. **공정성**: 운보다는 실력 중심
5. **창의성**: 다양한 플레이 스타일 지원

### Quality Standards
- **버그 없는 게임**: 철저한 테스트
- **직관적 UI**: 쉬운 조작법
- **빠른 로딩**: 대기시간 최소화
- **안정적 성능**: 모든 환경에서 안정적

## 📝 Important Game Mechanics Notes

### Combat System
- BRV 공격은 적의 BRV를 감소시키고 자신의 BRV 증가
- HP 공격은 자신의 BRV를 소모하여 적의 HP 감소
- BREAK 상태의 적은 다음 턴까지 행동 불가
- 상처 시스템으로 단순 회복만으로는 완전 회복 불가

### Character Progression
- 레벨업 시 스탯 자동 증가 + 보너스 포인트 배분
- 직업별 고유 스킬 트리
- 특성 시스템으로 개성화
- 장비를 통한 추가 스탯 보정

### Resource Management
- HP: 생명력 (0이 되면 전투불능)
- MP: 마법력 (스킬 사용에 소모)
- BRV: 용기 (HP 공격의 위력 결정)
- 스태미나: 던전 탐험 시 소모

### Strategic Depth
- 직업 조합에 따른 시너지 효과
- 적의 약점/저항 시스템
- 전장 위치에 따른 전략 변화
- 시간 관리 (ATB 게이지 활용)

이 게임은 단순한 로그라이크를 넘어서 현대적 JRPG의 모든 요소를 담은 종합 RPG 시스템입니다!
