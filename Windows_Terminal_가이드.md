# 🌟 Dawn of Stellar - Windows Terminal 최적화 가이드

## 🖥️ Windows Terminal이란?

Windows Terminal은 Microsoft에서 개발한 최신 터미널 애플리케이션으로, Dawn of Stellar과 같은 텍스트 기반 게임에 최적화되어 있습니다.

### 📊 CMD vs Windows Terminal 비교

| 기능 | CMD (명령 프롬프트) | Windows Terminal |
|------|-------------------|------------------|
| 🎨 색상 지원 | 16색 제한 | 24비트 트루컬러 |
| 🔤 폰트 | 고정폰트만 | 다양한 폰트 + 이모지 |
| 🪟 탭 | 지원 안함 | 멀티탭 지원 |
| ⚡ 성능 | 느림 | GPU 가속 |
| 🎮 게임 호환성 | 낮음 | 최고 |

## 🚀 설치 방법

### 방법 1: Microsoft Store (권장)
1. Microsoft Store 열기
2. "Windows Terminal" 검색
3. 설치 클릭

### 방법 2: winget (명령줄)
```powershell
winget install Microsoft.WindowsTerminal
```

### 방법 3: GitHub 릴리즈
[Windows Terminal GitHub](https://github.com/microsoft/terminal/releases)에서 최신 릴리즈 다운로드

## 🎮 Dawn of Stellar 최적화 설정

### 1. 폰트 설정 (권장)
Windows Terminal에서 최고의 게임 경험을 위한 폰트:

1. **Cascadia Code** (기본, 권장)
   - 프로그래밍 최적화
   - 리가처 지원
   - 크기: 12pt

2. **Consolas** (클래식)
   - Windows 기본 폰트
   - 안정적 표시
   - 크기: 12pt

3. **Fira Code** (개발자용)
   - 오픈소스
   - 아름다운 기호
   - 크기: 11pt

### 2. 색상 테마 설정

#### Dawn of Stellar 전용 테마
Windows Terminal 설정(Ctrl+,)에서 다음 테마를 추가:

```json
{
    "name": "Dawn of Stellar",
    "background": "#0C0C0C",
    "foreground": "#CCCCCC",
    "black": "#0C0C0C",
    "blue": "#0037DA",
    "brightBlue": "#3B78FF",
    "brightCyan": "#61D6D6",
    "brightGreen": "#16C60C",
    "brightPurple": "#B4009E",
    "brightRed": "#E74856",
    "brightWhite": "#F2F2F2",
    "brightYellow": "#F9F1A5",
    "cyan": "#3A96DD",
    "green": "#13A10E",
    "purple": "#881798",
    "red": "#C50F1F",
    "white": "#CCCCCC",
    "yellow": "#C19C00"
}
```

### 3. 프로필 설정

Dawn of Stellar 전용 프로필 추가:

```json
{
    "name": "Dawn of Stellar",
    "commandline": "cmd.exe",
    "startingDirectory": "C:\\경로\\Dawn-of-Stellar",
    "colorScheme": "Dawn of Stellar",
    "fontSize": 12,
    "fontFace": "Cascadia Code",
    "cursorShape": "underscore",
    "backgroundImage": null,
    "backgroundImageOpacity": 0.1
}
```

## 🎮 게임 실행 방법

### 1. 자동 실행 (권장)
```batch
# 더블클릭만 하면 됩니다!
Dawn_of_Stellar_실행.bat
```

### 2. Windows Terminal에서 직접 실행
```cmd
cd Dawn-of-Stellar
.venv\Scripts\activate.bat
python main.py
```

### 3. PowerShell 실행
```powershell
# PowerShell 스크립트 실행
.\Dawn_of_Stellar_PowerShell실행.ps1
```

## 🎯 게임패드 설정

### 지원하는 컨트롤러
- Xbox One/Series X|S 컨트롤러
- PlayStation 4/5 컨트롤러 (DS4Windows 권장)
- Nintendo Switch Pro 컨트롤러
- Steam 컨트롤러
- 기타 DirectInput/XInput 호환 컨트롤러

### 게임패드 테스트
```batch
# 게임패드 설정 도구 실행
python gamepad_setup.py
```

## 📱 모바일 연동

### Flutter 앱 연결
1. 모바일 백엔드 서버 시작:
   ```cmd
   python mobile_backend_server.py
   ```

2. Flutter 앱에서 PC IP 주소로 연결

3. 모바일에서 게임 조작 가능

## 🔧 문제 해결

### Windows Terminal에서 색상이 안 보일 때
1. `설정 > 프로필 > 고급` 에서 VT 처리 활성화
2. `colorScheme`이 올바르게 설정되었는지 확인

### 게임패드가 인식 안 될 때
1. Windows 설정 > 게임 > 컨트롤러에서 인식 확인
2. Steam이 실행 중이면 종료 (컨트롤러 충돌 방지)
3. 게임패드 설정 도구 실행: `python gamepad_setup.py`

### 한글이 깨질 때
1. Windows Terminal 설정에서 폰트가 한글을 지원하는지 확인
2. `chcp 65001` 명령어로 UTF-8 설정

## 🌟 최고의 게임 경험을 위한 팁

1. **전체화면 모드**: F11키로 전체화면 전환
2. **투명도 조절**: Ctrl + Shift + 마우스 휠
3. **탭 관리**: Ctrl + Shift + T (새 탭), Ctrl + W (탭 닫기)
4. **폰트 크기**: Ctrl + Plus/Minus로 조절
5. **테마 전환**: 게임에 맞는 어두운 테마 사용

## 🎊 즐거운 게임 되세요!

Dawn of Stellar은 Windows Terminal에서 최고의 경험을 제공합니다. 
28개 직업, 165개 이상의 상태효과, 그리고 완벽한 색상 지원으로 
진정한 로그라이크 RPG의 재미를 만끽하세요!

---

📞 **문의사항**: GitHub Issues 또는 Discord 커뮤니티
🌐 **공식 사이트**: https://github.com/APTOL-7176/Dawn-of-Stellar
