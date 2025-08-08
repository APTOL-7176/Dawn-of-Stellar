# 📱 Dawn of Stellar - Mobile Desktop App

이 프로젝트는 웹 기술과 Python을 결합한 세로형 모바일 스타일 데스크톱 애플리케이션입니다.

## ✨ 특징

- **� 모바일 UI**: 세로형 스마트폰 레이아웃 최적화
- **🌐 웹 기술**: HTML5, CSS3, JavaScript (Electron)
- **🐍 Python 백엔드**: 실제 게임 로직 처리
- **👆 터치 최적화**: 터치 친화적 인터페이스
- **🎨 모바일 디자인**: 세로 화면 + 레트로 감성
- **⚡ 실시간 통신**: IPC를 통한 즉시 응답

## 🏗️ 프로젝트 구조

```
electron_app/
├── main.js              # Electron 메인 프로세스
├── package.json         # NPM 설정
├── renderer/
│   ├── index.html      # 메인 UI
│   └── renderer.js     # 렌더러 프로세스
└── assets/             # 이미지, 아이콘

python_backend.py        # Python 게임 백엔드
install_electron_app.bat # 설치 스크립트
start_electron_app.bat   # 실행 스크립트
```

## 🚀 설치 및 실행

### 1단계: 의존성 설치
```bash
# 자동 설치 (Windows)
install_electron_app.bat

# 수동 설치
cd electron_app
npm install
```

### 2단계: 앱 실행
```bash
# 자동 실행 (Windows)
start_electron_app.bat

# 수동 실행
cd electron_app
npm start
```

## 🎮 사용법

### 모바일 스타일 컨트롤
- **십자키**: W, A, S, D 이동 (화면 왼쪽 상단)
- **액션**: OK, NO, BAG, PTY (화면 오른쪽 상단)
- **시스템**: 시작, 저장, 로드, 설정 등 (화면 왼쪽 하단)
- **빠른메뉴**: 자동, 상태, 맵, 퀘스트 등 (화면 오른쪽 하단)

### 터치 인터페이스
- **탭**: 버튼 선택/실행
- **홀드**: 버튼 누름 효과
- **스크롤**: 게임 화면 내 스크롤
- **크기**: 44x44px 터치 최적화 크기

## 🔧 기술 스택

### 프론트엔드 (Electron)
- **Electron**: 크로스 플랫폼 데스크톱 앱
- **HTML5/CSS3**: 모던 웹 기술
- **JavaScript**: 인터랙션 처리
- **IPC**: 프로세스 간 통신

### 백엔드 (Python)
- **Python 3.10+**: 게임 로직
- **Threading**: 비동기 처리
- **JSON**: 데이터 교환
- **UTF-8**: 유니코드 지원

## 📦 빌드 및 배포

### 개발용 빌드
```bash
npm start
```

### 배포용 빌드
```bash
npm run build
```

### 실행파일 생성
```bash
npm run dist
```

## 🎨 UI 특징

### 모바일 최적화 테마
- **세로형 레이아웃**: 414x896px (iPhone 12 Pro 비율)
- **2x2 그리드**: 4개 섹션으로 나눈 컨트롤 영역
- **터치 친화적**: 44px 최소 터치 영역
- **네온 색상**: 보라/파랑 계열 + 우주 테마

### 반응형 디자인
- **세로 우선**: 세로형 스마트폰 최적화
- **스케일링**: 다양한 화면 크기 대응
- **최소 크기**: 320x568px (iPhone SE)
- **최대 크기**: 500px 너비 제한

## 🔗 통신 구조

```
┌─────────────────┐    IPC    ┌─────────────────┐
│   Electron UI   │ ◄────────► │  Main Process   │
│   (Renderer)    │           │                 │
└─────────────────┘           └─────────────────┘
                                        │
                                   Child Process
                                        ▼
                              ┌─────────────────┐
                              │ Python Backend  │
                              │   (Game Logic)  │
                              └─────────────────┘
```

## 🛠️ 개발 가이드

### 새 기능 추가
1. **UI 변경**: `renderer/index.html` + `renderer/renderer.js`
2. **게임 로직**: `python_backend.py`
3. **통신**: `main.js`의 IPC 핸들러

### 디버깅
- **Electron**: F12로 개발자 도구 열기
- **Python**: 콘솔 출력 확인
- **IPC**: `console.log`로 메시지 추적

## 📄 라이선스

MIT License - 자유롭게 사용 및 수정 가능

## 🤝 기여

1. Fork 생성
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 커밋 (`git commit -m 'Add amazing feature'`)
4. 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📞 지원

- **이슈**: GitHub Issues
- **문서**: 이 README.md
- **예제**: `examples/` 폴더

---

🌟 **Dawn of Stellar**과 함께 우주 모험을 떠나보세요! 🚀
