# 🌟 Dawn of Stellar - Mobile Edition

Python 백엔드와 Flutter 프론트엔드로 구성된 모바일 로그라이크 RPG

## 📋 시스템 구성

### 🐍 Python Backend (Flask)
- **파일**: `mobile_backend_server.py`
- **포트**: 8000
- **기능**: 게임 로직, 데이터 관리, API 제공
- **실행**: `start_mobile_backend.bat`

### 📱 Flutter Frontend
- **디렉토리**: `flutter_mobile/`
- **기능**: 세로 최적화 UI, 터치 제스처, 실시간 통신
- **실행**: `run_flutter_app.bat`

## 🚀 시작하기

### 1단계: 백엔드 서버 실행
```bash
# 방법 1: 배치 파일 사용 (권장)
start_mobile_backend.bat

# 방법 2: 직접 실행
python mobile_backend_server.py
```

### 2단계: Flutter 앱 실행
```bash
# 방법 1: 배치 파일 사용 (권장)
run_flutter_app.bat

# 방법 2: 직접 실행
cd flutter_mobile
flutter pub get
flutter run
```

## 🎮 게임 기능

### ⚔️ 전투 시스템
- **실시간 전투**: Python 백엔드에서 데미지 계산
- **스킬 시스템**: 각 직업별 고유 스킬
- **BRV 시스템**: Final Fantasy 스타일 브레이브 시스템

### 🏰 던전 탐험
- **무작위 이벤트**: 적 조우, 아이템 발견, 특수 이벤트
- **층수 진행**: 점진적 난이도 증가
- **위치 추적**: 현재 위치와 이동 경로 기록

### 🎒 인벤토리 관리
- **아이템 사용**: 회복 포션, 마나 포션 등
- **장비 시스템**: 무기와 방어구 장착
- **희귀도 시스템**: Common, Uncommon, Rare, Epic, Legendary

### 👥 파티 관리
- **4명 파티**: 전사, 아크메이지, 성기사, 바드
- **상태 관리**: HP, MP, BRV 실시간 추적
- **스킬 관리**: 각 캐릭터별 고유 스킬셋

## 🛠️ 기술 스택

### Backend (Python)
- **Flask**: 웹 서버 프레임워크
- **Flask-CORS**: 크로스 오리진 요청 허용
- **JSON**: 데이터 직렬화
- **Threading**: 백그라운드 작업 관리

### Frontend (Flutter)
- **GetX**: 상태 관리 및 의존성 주입
- **HTTP**: 백엔드 API 통신
- **Material 3**: UI 디자인 시스템
- **Custom Theme**: 우주/별자리 테마

## 📡 API 엔드포인트

### 게임 관리
- `GET /health` - 서버 상태 확인
- `POST /game/start` - 새 게임 시작
- `POST /game/save` - 게임 저장
- `GET /game/load/<session_id>` - 게임 불러오기
- `GET /game/state` - 현재 게임 상태 조회

### 전투 시스템
- `POST /combat/action` - 전투 액션 수행
  ```json
  {
    "session_id": "uuid",
    "character_id": "1",
    "action_type": "attack|skill|defend",
    "target_id": "enemy_1",
    "skill_id": "파이어볼"
  }
  ```

### 던전 탐험
- `POST /dungeon/move` - 던전 이동
  ```json
  {
    "session_id": "uuid",
    "direction": "north|south|east|west",
    "current_position": {"x": 0, "y": 0}
  }
  ```

### 인벤토리
- `POST /inventory/use_item` - 아이템 사용
  ```json
  {
    "session_id": "uuid",
    "item_id": "healing_potion",
    "target_character_id": "1"
  }
  ```

## 🎨 UI 특징

### 🌌 Cosmic Theme
- **색상**: 우주 테마 (코스믹 블루, 스텔라 퍼플, 스타 골드)
- **그라데이션**: 은하수와 성운 효과
- **글로우 효과**: 버튼과 카드에 빛나는 효과

### 📱 모바일 최적화
- **세로 모드 고정**: 한손 조작 최적화
- **터치 제스처**: 스와이프, 탭, 홀드 지원
- **응답형 UI**: 다양한 화면 크기 지원

### 🎭 애니메이션
- **스플래시 스크린**: 회전하는 별과 타이틀 효과
- **화면 전환**: 부드러운 페이드 인/아웃
- **버튼 효과**: 터치 시 파급 효과

## 🔧 개발자 가이드

### 🐛 디버깅
1. **백엔드 로그**: Flask 콘솔에서 API 요청/응답 확인
2. **Flutter 로그**: `flutter logs` 명령어로 실시간 로그 확인
3. **네트워크 상태**: 앱 내에서 연결 상태 표시

### 🔄 오프라인 모드
- 백엔드 서버가 없어도 로컬 데이터로 게임 플레이 가능
- 더미 데이터와 간단한 게임 로직 포함
- 서버 연결 복구 시 자동 동기화

### 📊 성능 최적화
- **상태 관리**: GetX의 반응형 프로그래밍으로 효율적 UI 업데이트
- **메모리 관리**: 세션 만료 시 자동 정리
- **네트워크**: 필요한 경우에만 API 호출

## 🚨 문제 해결

### 백엔드 연결 실패
```
❌ 오류: Connection refused (OS Error: 연결할 수 없음)
```
**해결책**:
1. `start_mobile_backend.bat` 실행 확인
2. 방화벽에서 포트 8000 허용
3. localhost 대신 실제 IP 주소 사용

### Flutter 빌드 오류
```
❌ 오류: Target of URI doesn't exist
```
**해결책**:
1. `flutter clean` 후 `flutter pub get` 실행
2. 임포트 경로 확인
3. 의존성 버전 충돌 확인

### 게임 데이터 손실
```
❌ 오류: 저장된 게임을 찾을 수 없습니다
```
**해결책**:
1. `saves/` 디렉토리 존재 확인
2. 세션 ID 일치 여부 확인
3. 파일 권한 문제 확인

## 🎯 향후 개발 계획

### 🔮 예정 기능
- [ ] **실시간 멀티플레이**: WebSocket 기반 협력 플레이
- [ ] **길드 시스템**: 플레이어 간 그룹 형성
- [ ] **업적 시스템**: 다양한 도전 과제
- [ ] **일일 퀘스트**: 매일 새로운 미션
- [ ] **PvP 모드**: 플레이어 대 플레이어 전투

### 🛠️ 기술 개선
- [ ] **데이터베이스**: SQLite/PostgreSQL 도입
- [ ] **캐싱**: Redis를 통한 성능 향상
- [ ] **보안**: JWT 토큰 기반 인증
- [ ] **배포**: Docker 컨테이너화
- [ ] **모니터링**: 실시간 서버 상태 추적

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 언제든지 문의하세요!

---

🌟 **Dawn of Stellar** - 별들의 새벽이 당신을 기다립니다!
