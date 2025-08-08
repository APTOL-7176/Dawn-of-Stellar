# 🍎 iOS 배포 완벽 가이드 - Dawn of Stellar

## 📱 iOS 배포 준비사항

### 1. 🛠️ 개발 환경 설정
```bash
# Xcode 설치 (Mac 필수)
# App Store에서 Xcode 최신 버전 설치

# Flutter iOS 설정 확인
flutter doctor
```

### 2. 🔑 Apple Developer 계정
- **Apple Developer Program** 등록 ($99/년)
- **Bundle ID** 생성 (예: com.yourcompany.dawnofstellar)
- **App ID** 등록
- **Provisioning Profile** 생성

## 📦 iOS 빌드 과정

### 1. 프로젝트 설정
```bash
cd flutter_mobile

# iOS 설정 확인
flutter config --enable-ios

# iOS 시뮬레이터에서 테스트
flutter run -d ios
```

### 2. 📱 iOS 전용 설정

#### `ios/Runner/Info.plist` 수정:
```xml
<key>CFBundleDisplayName</key>
<string>Dawn of Stellar</string>
<key>CFBundleIdentifier</key>
<string>com.yourcompany.dawnofstellar</string>
<key>CFBundleVersion</key>
<string>1.0.0</string>
```

#### `pubspec.yaml` 설정:
```yaml
name: dawn_of_stellar
description: Epic Roguelike RPG Adventure

flutter:
  assets:
    - assets/
    - assets/sounds/
    - assets/images/

  fonts:
    - family: Galmuri11
      fonts:
        - asset: assets/fonts/Galmuri11.ttf
    - family: whitrabt
      fonts:
        - asset: assets/fonts/whitrabt.ttf
```

### 3. 🏗️ iOS 빌드 명령어

#### 개발 빌드 (테스트용):
```bash
# iOS 시뮬레이터용
flutter build ios --debug

# 실제 기기용 (개발자 서명)
flutter build ios --debug --target-platform ios-arm64
```

#### 배포 빌드 (App Store용):
```bash
# Release 빌드
flutter build ios --release

# App Store용 IPA 생성
flutter build ipa --release
```

### 4. 📋 Xcode에서 설정

1. **Xcode로 프로젝트 열기:**
```bash
open ios/Runner.xcworkspace
```

2. **프로젝트 설정:**
   - **Team**: Apple Developer 계정 선택
   - **Bundle Identifier**: 고유 ID 입력
   - **Deployment Target**: iOS 12.0 이상
   - **Signing**: Automatic 또는 Manual

3. **권한 설정 (필요시):**
   - 네트워크 접근 (게임 서버 통신용)
   - 로컬 저장소 접근 (저장 파일용)

## 🚀 App Store 배포

### 1. 📊 App Store Connect 설정
1. [App Store Connect](https://appstoreconnect.apple.com) 접속
2. **새 앱 생성**
3. **앱 정보 입력:**
   - 앱 이름: Dawn of Stellar
   - 카테고리: 게임 > 롤플레잉
   - 연령 등급: 적절히 설정

### 2. 📝 메타데이터 준비
```
앱 제목: Dawn of Stellar
부제목: Epic Roguelike Adventure
키워드: roguelike, rpg, adventure, fantasy, korean
설명: 
🌟 Dawn of Stellar에서 차원간 모험을 시작하세요!
⚔️ 28개 직업, 브레이브 전투 시스템
🎮 완벽한 한국어 지원
```

### 3. 📱 스크린샷 준비
iOS용 스크린샷 필요 사이즈:
- **iPhone 6.7"**: 1290×2796px
- **iPhone 6.5"**: 1242×2688px  
- **iPhone 5.5"**: 1242×2208px
- **iPad Pro 12.9"**: 2048×2732px

### 4. 🎯 TestFlight 베타 테스트
```bash
# 베타 테스트용 빌드 업로드
flutter build ipa --release
```

Xcode에서 Archive → Upload to App Store

### 5. 📤 최종 배포

1. **App Store Connect**에서 빌드 선택
2. **리뷰 제출**
3. **애플 리뷰 대기** (평균 1-3일)
4. **승인 후 배포**

## 🔧 iOS 전용 최적화

### 1. 성능 최적화
```dart
// main.dart에서 iOS 전용 설정
import 'dart:io' show Platform;

void main() {
  if (Platform.isIOS) {
    // iOS 전용 최적화 설정
  }
  runApp(MyApp());
}
```

### 2. 네이티브 iOS 기능 활용
```dart
// 햅틱 피드백 (iOS 전용)
import 'package:flutter/services.dart';

void triggerHaptic() {
  if (Platform.isIOS) {
    HapticFeedback.mediumImpact();
  }
}
```

### 3. iOS 디자인 가이드라인 준수
- **Human Interface Guidelines** 준수
- **Safe Area** 고려
- **Dynamic Type** 지원
- **Dark Mode** 지원

## 📊 배포 체크리스트

### ✅ 기술적 준비
- [ ] Xcode 최신 버전 설치
- [ ] Apple Developer 계정 활성화
- [ ] Bundle ID 등록
- [ ] Provisioning Profile 생성
- [ ] iOS 시뮬레이터 테스트 완료
- [ ] 실제 기기 테스트 완료

### ✅ 앱 준비
- [ ] 앱 아이콘 준비 (1024x1024px)
- [ ] 스크린샷 촬영 (모든 사이즈)
- [ ] 앱 설명 작성 (한국어/영어)
- [ ] 키워드 최적화
- [ ] 연령 등급 결정

### ✅ 법적 준비
- [ ] 개인정보 처리방침
- [ ] 이용약관
- [ ] 저작권 정보
- [ ] 라이선스 정보

## 💰 비용 및 시간

### 💳 필요 비용
- **Apple Developer Program**: $99/년
- **Mac 장비**: 필수 (Xcode 실행용)
- **iOS 기기**: 테스트용 (선택)

### ⏱️ 소요 시간
- **초기 설정**: 1-2일
- **빌드 및 테스트**: 2-3일
- **App Store 리뷰**: 1-3일
- **총 소요 시간**: 약 1주일

## 🚨 주의사항

### ⚠️ 일반적인 리젝트 사유
1. **크래시 발생**
2. **개인정보 처리방침 누락**
3. **부적절한 콘텐츠**
4. **메타데이터 오류**
5. **성능 문제**

### 🛡️ 리젝트 방지 팁
- 철저한 테스트
- 가이드라인 준수
- 명확한 앱 설명
- 적절한 스크린샷
- 안정적인 성능

## 📞 지원 및 도움

### 🔗 유용한 링크
- [Apple Developer](https://developer.apple.com)
- [App Store Connect](https://appstoreconnect.apple.com)
- [Flutter iOS 배포 가이드](https://docs.flutter.dev/deployment/ios)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

### 💡 추가 팁
1. **베타 테스트 활용**: TestFlight로 사전 테스트
2. **점진적 배포**: 특정 지역부터 시작
3. **업데이트 주기**: 정기적인 업데이트로 사용자 유지
4. **피드백 활용**: 사용자 리뷰 적극 활용

---

🎮 **Dawn of Stellar**을 iOS에서도 만나보세요! 
성공적인 배포를 응원합니다! 🌟
