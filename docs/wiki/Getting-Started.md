# 🚀 시작하기 가이드

Dawn of Stellar를 처음 시작하는 분들을 위한 완전한 설치 및 실행 가이드입니다.

## 📋 시스템 요구사항

### 필수 요구사항
- **Python 3.10+**: 최신 Python 버전 (3.10 이상 권장)
- **UTF-8 콘솔**: Windows Terminal, PowerShell, 또는 UTF-8 지원 터미널
- **메모리**: 최소 512MB RAM (게임 실행용)
- **저장공간**: 최소 100MB 여유 공간

### 권장 환경
- **Windows Terminal**: 최적화된 콘솔 환경
- **가상환경**: `.venv` (저장소 내 포함)
- **VS Code**: 개발 및 실행 환경

## 💻 설치 방법

### 방법 1: 간편 실행 (권장)
1. **저장소 클론**:
   ```bash
   git clone https://github.com/APTOL-7176/Dawn-of-Stellar.git
   cd Dawn-of-Stellar
   ```

2. **배치 파일 실행**:
   - `통합런처.bat` 또는 `게임시작.bat` 더블클릭
   - 자동으로 가상환경 활성화 및 게임 실행

### 방법 2: 수동 설정
1. **가상환경 활성화**:
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **의존성 설치** (필요시):
   ```bash
   pip install -r requirements.txt
   ```

3. **게임 실행**:
   ```bash
   python main.py
   ```

### 방법 3: VS Code에서 실행
1. **VS Code로 폴더 열기**
2. **Task 실행**: `Ctrl+Shift+P` → "Run Task" → "Run Roguelike Game"
3. 또는 터미널에서: `.venv/Scripts/python.exe main.py`

## 🎮 첫 게임 플레이

### 1단계: 캐릭터 생성
1. **이름 입력**: 원하는 캐릭터 이름 입력
2. **직업 선택**: 28개 직업 중 하나 선택
   - **전사**: 초보자 추천, 균형 잡힌 능력
   - **아크메이지**: 강력한 마법, 높은 MP 소모
   - **성기사**: 탱커 역할, 높은 방어력
   - **도적**: 빠른 속도, 독 스킬 특화

### 2단계: 기본 조작법
- **이동**: `W` (위), `A` (왼쪽), `S` (아래), `D` (오른쪽) 또는 화살표키
- **인벤토리**: `I` 키
- **파티 상태**: `P` 키 (캐릭터 정보 포함)
- **필드 활동**: `F` 키 (스킬, 요리, 상인)
- **도움말**: `H` 키
- **게임 저장**: `B` 키
- **게임 종료**: `Q` 키

### 3단계: 첫 전투
1. **적 발견**: 빨간색 문자로 표시된 적
2. **전투 진입**: 적과 인접하면 자동 전투 시작
3. **ATB 게이지**: 게이지가 가득 차면 행동 가능
4. **스킬 선택**: 숫자 키 (1-9)로 스킬 선택
5. **기본 공격**: BRV 공격 → HP 공격 순서

### 4단계: 첫 층 클리어
1. **계단 찾기**: `>` 기호로 표시된 계단
2. **아이템 수집**: 바닥의 아이템들 획득
3. **레벨업**: 경험치 획득으로 자동 레벨업
4. **다음 층**: 계단에서 `Enter`로 다음 층 이동

## 🎯 게임 목표

### 단기 목표
- **첫 5층 클리어**: 기본 시스템 익히기
- **장비 교체**: 더 좋은 무기/방어구 찾기
- **스킬 마스터**: 직업별 스킬 활용법 학습
- **파티 구성**: AI 동료 영입하기

### 중기 목표  
- **10층 도달**: 중급 몬스터와 전투
- **특성 획득**: 캐릭터 특성 시스템 활용
- **제작 시스템**: 요리 및 연금술 이용
- **보스 전투**: 특별한 보스 몬스터 도전

### 장기 목표
- **50층 돌파**: 고급 콘텐츠 접근
- **전직업 마스터**: 모든 직업 경험해보기
- **완벽한 장비**: 전설 등급 장비 수집
- **100층 정복**: 최종 목표 달성

## ⚙️ 설정 조정

### 난이도 설정
- **평온**: 초보자용 (피해 -40%, 경험치 +20%)
- **보통**: 표준 난이도
- **어려움**: 도전적 (피해 +50%, 경험치 +50%)
- **지옥**: 극한 도전 (피해 +100%, 특수 보상)

### 게임 설정 (config.py)
```python
# 개발 모드 (치트 기능)
DEVELOPMENT_MODE = False  

# ATB 애니메이션 설정
ATB_SETTINGS = {
    "animation_enabled": True,
    "animation_fps": 60,
    "smooth_animation": True
}

# 오디오 설정
BGM_SETTINGS = {
    "character_select": "prelude"
}
```

## 🔧 문제 해결

### 자주 발생하는 문제

#### 1. 게임이 실행되지 않음
- **Python 버전 확인**: `python --version`
- **가상환경 활성화**: `.venv\Scripts\activate`
- **의존성 재설치**: `pip install -r requirements.txt`

#### 2. 화면이 깨져 보임
- **콘솔 설정**: UTF-8 인코딩 확인
- **Windows Terminal 사용** 권장
- **폰트 설정**: 한글 지원 폰트 사용

#### 3. 키 입력이 안 됨
- **키보드 레이아웃**: 영문 키보드로 변경
- **Caps Lock 확인**: 대소문자 구분 없음
- **NumLock 상태**: 숫자 패드 사용 시 확인

#### 4. 게임이 느림
- **터미널 성능**: Windows Terminal 사용
- **애니메이션 끄기**: config.py에서 설정 변경
- **배경 프로그램**: 다른 프로그램 종료

### 디버그 모드
개발자나 고급 사용자를 위한 디버그 기능:
```python
# config.py에서 설정
DEVELOPMENT_MODE = True
DEBUG_MODE = True
```

## 📱 모바일 클라이언트

### Flutter 앱 (별도 프로젝트)
- **플랫폼**: Android/iOS
- **UI**: 터미널 스타일 모바일 최적화
- **제스처**: 스와이프 기반 이동
- **통신**: HTTP API를 통한 백엔드 연결

## 📁 프로젝트 구조

```
Dawn-of-Stellar/
├── main.py                 # 게임 메인 엔트리
├── config.py              # 설정 파일
├── game/                  # 게임 로직
│   ├── brave_combat.py    # 전투 시스템
│   ├── character.py       # 캐릭터 관리
│   ├── world.py          # 던전/월드
│   └── ...
├── docs/wiki/            # 위키 문서
├── saves/                # 세이브 파일
├── .venv/               # 가상환경
└── flutter_mobile/      # 모바일 클라이언트
```

## 🆘 도움 받기

### 게임 내 도움말
- **도움말**: `H` 또는 `?` 키
- **상태 확인**: `C` 키로 캐릭터 정보
- **전투 가이드**: 전투 중 `H` 키

### 추가 자료
- **[전투 시스템](Combat-System.md)**: 전투 메커니즘 상세 가이드
- **[스킬 시스템](Skills-and-Casting.md)**: 스킬 및 캐스팅 가이드
- **[인벤토리](Inventory-and-Equipment.md)**: 아이템 관리 가이드

### 커뮤니티
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **GitHub Discussions**: 일반적인 질문 및 토론
- **Wiki**: 상세한 게임 정보

## 📸 스크린샷

![게임 시작 화면](media/start_screen_sample.png)
![첫 던전 탐험](media/first_dungeon_sample.png)
![전투 화면](media/combat_ui_sample.png)

이제 Dawn of Stellar의 세계로 모험을 떠나보세요! 🌟
