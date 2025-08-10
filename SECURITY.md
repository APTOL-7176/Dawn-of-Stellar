# Security Policy

## Supported Versions

현재 지원되는 Dawn of Stellar 버전은 다음과 같습니다:

| Version | Supported          |
| ------- | ------------------ |
| 3.1.x   | :white_check_mark: |
| 3.0.x   | :white_check_mark: |
| 2.x.x   | :x:                |
| < 2.0   | :x:                |

## Reporting a Vulnerability

보안 취약점을 발견하셨다면 다음 절차를 따라주세요:

### 🚨 즉시 보고가 필요한 경우
- 사용자 데이터 유출 가능성
- 원격 코드 실행 취약점
- 권한 상승 취약점
- 세이브 파일 조작 가능성

### 📧 보고 방법

**GitHub Security Advisory (권장)**
1. 저장소의 Security 탭으로 이동
2. "Report a vulnerability" 클릭
3. 상세한 취약점 정보 작성

**이메일 보고**
- 보안 관련 이메일 주소 (추후 공개 예정)
- 제목: [SECURITY] Dawn of Stellar 보안 취약점

### 📝 보고 시 포함할 정보

```
- 취약점 설명
- 영향 범위 (어떤 기능이 영향받는지)
- 재현 단계
- 예상 위험도 (Low/Medium/High/Critical)
- 게임 버전
- 운영체제 및 Python 버전
- 첨부 파일 (PoC 코드, 스크린샷 등)
```

### ⏱️ 응답 시간

- **초기 확인**: 48시간 내
- **심각도 평가**: 1주일 내
- **수정 계획**: 2주일 내
- **패치 배포**: 심각도에 따라 1-4주

### 🔒 보안 정책

#### 데이터 보호
- 세이브 파일은 로컬에만 저장
- 네트워크 통신 시 HTTPS 사용
- 민감한 정보는 암호화 저장

#### 코드 실행 보안
- 사용자 입력 검증
- 파일 시스템 접근 제한
- 외부 라이브러리 정기 업데이트

#### 모바일 보안
- API 엔드포인트 인증
- 요청 크기 제한
- CORS 정책 적용

### 🛡️ 보안 모범 사례

**개발자용**
- 정기적인 의존성 보안 검사
- 코드 리뷰 시 보안 체크리스트 사용
- 테스트 시 경계값 검증

**사용자용**
- 공식 소스에서만 게임 다운로드
- 세이브 파일 백업
- 업데이트 정기 확인

### 🏆 보안 기여자

보안 취약점을 제보해주신 분들:
- (향후 기여자 목록 업데이트)

### 📚 추가 보안 리소스

- [Python Security Best Practices](https://python.org/dev/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Advisory](https://docs.github.com/en/code-security/security-advisories)

---

🔐 **보안은 모두의 책임입니다**

Dawn of Stellar을 더 안전하게 만들기 위한 여러분의 기여를 환영합니다!
