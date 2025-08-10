# 🌟 Dawn of Stellar - 기여 가이드

Dawn of Stellar 프로젝트에 기여해주셔서 감사합니다! 
이 문서는 프로젝트에 효과적으로 기여하는 방법을 안내합니다.

## 🎯 프로젝트 개요

Dawn of Stellar은 완전체 Python 기반 로그라이크 RPG 게임입니다.
- **장르**: 클래식 로그라이크 + 현대적 JRPG 요소
- **플랫폼**: Windows/Linux/Mac + Flutter 모바일
- **특징**: 28개 직업, FF 브레이브 시스템, 자동화된 전투

## 🚀 빠른 시작

### 개발 환경 설정
```bash
# 1. 저장소 클론
git clone https://github.com/APTOL-7176/Dawn-of-Stellar.git
cd Dawn-of-Stellar

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 게임 실행
python main.py
```

### 코드 품질 도구 설정
```bash
# 코드 포매팅
pip install black isort

# 타입 체크
pip install mypy

# 린팅
pip install flake8 pylint

# 테스트
pip install pytest pytest-cov
```

## 📋 기여 방법

### 1. 이슈 확인
- [Issues](https://github.com/APTOL-7176/Dawn-of-Stellar/issues)에서 해결할 문제 찾기
- `good first issue` 라벨이 있는 이슈부터 시작하기
- 새로운 기능 제안은 먼저 이슈로 토론하기

### 2. 브랜치 생성
```bash
# 새 기능
git checkout -b feature/새기능명

# 버그 수정  
git checkout -b bugfix/버그설명

# 문서 업데이트
git checkout -b docs/문서내용
```

### 3. 코드 작성
- 기존 코드 스타일 따르기
- 한글 주석으로 코드 설명하기
- 함수/클래스에 독스트링 작성하기

### 4. 테스트 작성
```bash
# 테스트 실행
python -m pytest tests/ -v

# 커버리지 확인
python -m pytest tests/ --cov=game --cov-report=html
```

### 5. 코드 검사
```bash
# 포매팅 적용
black game/ main.py config.py version.py
isort game/ main.py config.py version.py

# 타입 체크
mypy game/ --ignore-missing-imports

# 린팅
flake8 game/ main.py config.py version.py
```

### 6. 커밋 및 풀 리퀘스트
```bash
# 커밋 (한글 메시지 권장)
git add .
git commit -m "✨ 새로운 직업 시스템 추가"

# 푸시
git push origin feature/새기능명

# GitHub에서 Pull Request 생성
```

## 🏗️ 프로젝트 구조

```
Dawn-of-Stellar/
├── game/                   # 게임 핵심 모듈
│   ├── character.py       # 캐릭터 시스템
│   ├── brave_combat.py    # 전투 시스템
│   ├── world.py           # 월드/던전 관리
│   ├── skill_system.py    # 스킬 시스템
│   └── ...
├── mobile/                 # Flutter 모바일 클라이언트
├── tests/                  # 테스트 코드
├── docs/                   # 문서
├── main.py                # 게임 진입점
├── config.py              # 설정 관리
├── version.py             # 버전 정보
└── requirements.txt       # 의존성
```

## 🎨 코딩 컨벤션

### 네이밍
- **변수/함수**: `snake_case`
- **클래스**: `PascalCase`
- **상수**: `UPPER_SNAKE_CASE`
- **파일**: `snake_case.py`

### 주석 스타일
```python
def calculate_damage(attacker, defender):
    """데미지 계산 함수
    
    Args:
        attacker: 공격자 캐릭터
        defender: 방어자 캐릭터
    
    Returns:
        int: 계산된 데미지 양
    """
    # 기본 데미지 계산
    base_damage = attacker.attack - defender.defense
    
    # 크리티컬 확률 체크
    if random.randint(1, 100) <= attacker.critical_chance:
        base_damage *= 1.5  # 크리티컬 1.5배
    
    return max(1, int(base_damage))
```

### 커밋 메시지 컨벤션
```
✨ 새로운 기능 추가
🐛 버그 수정
📝 문서 업데이트
🎨 코드 포매팅/구조 개선
⚡ 성능 개선
🔧 설정 파일 수정
🧪 테스트 추가/수정
🚀 배포 관련
```

## 🎮 게임 기능별 기여 가이드

### 새로운 직업 추가
1. `game/character.py`에 직업 클래스 추가
2. `game/skill_system.py`에 직업별 스킬 정의
3. 테스트 코드 작성
4. 문서 업데이트

### 전투 시스템 개선
1. `game/brave_combat.py` 수정
2. ATB/BRV 시스템 균형 조정
3. 전투 로그 시스템 활용
4. 성능 테스트 실행

### UI/UX 개선
1. 색상 시스템 (`game/display_utils.py`)
2. 애니메이션 시스템 추가
3. 접근성 기능 개선
4. 사용자 테스트 진행

### 모바일 기능
1. Flutter 클라이언트 (`mobile/` 폴더)
2. API 서버 연동
3. 터치 인터페이스 최적화
4. 크로스 플랫폼 테스트

## 🧪 테스트 작성 가이드

### 단위 테스트
```python
import pytest
from game.character import Character

def test_character_creation():
    """캐릭터 생성 테스트"""
    char = Character("테스트", "전사")
    
    assert char.name == "테스트"
    assert char.job_class == "전사"
    assert char.level == 1
    assert char.current_hp > 0

def test_level_up():
    """레벨업 테스트"""
    char = Character("테스트", "전사")
    old_hp = char.max_hp
    
    char.gain_experience(1000)
    
    assert char.level > 1
    assert char.max_hp > old_hp
```

### 통합 테스트
```python
def test_combat_system():
    """전투 시스템 통합 테스트"""
    player = Character("플레이어", "전사")
    enemy = Character("적", "도적")
    
    combat = BraveCombatSystem([player], [enemy])
    result = combat.start_combat()
    
    assert result in ['victory', 'defeat']
    assert player.current_hp >= 0
    assert enemy.current_hp >= 0
```

## 📚 문서화

### 코드 문서화
- 모든 공개 함수/클래스에 독스트링 작성
- 복잡한 로직에는 인라인 주석 추가
- README.md 업데이트

### API 문서화
- 모바일 API 엔드포인트 문서화
- 요청/응답 예시 포함
- 에러 코드 정의

## 🔧 디버깅 가이드

### 로그 시스템 활용
```python
from game.error_logger import log_debug, log_error

def complex_function():
    log_debug("함수시작", "복잡한 함수 실행 시작")
    
    try:
        # 복잡한 로직
        result = perform_calculation()
        log_debug("계산완료", f"결과: {result}")
        return result
    except Exception as e:
        log_error("계산오류", f"계산 중 오류 발생: {str(e)}")
        raise
```

### 성능 프로파일링
```python
import cProfile

def profile_function():
    """함수 성능 측정"""
    pr = cProfile.Profile()
    pr.enable()
    
    # 측정할 코드
    run_game_loop()
    
    pr.disable()
    pr.print_stats()
```

## 🎁 기여자 인정

기여해주신 모든 분들의 이름이 게임 크레딧에 표시됩니다!
- 코드 기여
- 버그 리포트
- 문서 개선
- 번역 작업
- 아이디어 제안

## 💬 커뮤니티

- **GitHub Issues**: 버그 리포트, 기능 요청
- **GitHub Discussions**: 일반적인 토론, 질문
- **Discord**: 실시간 채팅 (추후 개설 예정)

## 📞 연락처

- **프로젝트 관리자**: APTOL-7176
- **GitHub**: https://github.com/APTOL-7176/Dawn-of-Stellar
- **이메일**: (추후 공개)

---

🌟 **함께 만들어가는 Dawn of Stellar!**

여러분의 기여가 이 게임을 더욱 멋지게 만듭니다.
작은 기여부터 큰 기능까지, 모든 참여를 환영합니다!
