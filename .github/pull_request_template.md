name: Pull Request
description: Dawn of Stellar에 기여해주셔서 감사합니다!

title: "[PR] "

body:
  - type: markdown
    attributes:
      value: |
        🎉 **풀 리퀘스트를 제출해주셔서 감사합니다!**
        
        코드 리뷰를 원활하게 진행할 수 있도록 아래 정보를 작성해주세요.

  - type: dropdown
    id: pr-type
    attributes:
      label: 🏷️ PR 타입
      description: 이 풀 리퀘스트의 유형을 선택해주세요.
      options:
        - 🐛 버그 수정
        - ✨ 새로운 기능
        - 📝 문서 개선
        - 🎨 코드 스타일/리팩토링
        - ⚡ 성능 개선
        - 🧪 테스트 추가/개선
        - 🔧 빌드/배포 개선
        - 🔒 보안 개선
        - 🌐 번역/다국어
        - 기타
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: 📝 변경사항 설명
      description: 이 PR에서 무엇을 변경했는지 설명해주세요.
      placeholder: |
        - ATB 시스템에서 게이지 속도 조정
        - 전투 자동화 기능 추가
        - UI 색상 시스템 개선
        - 버그 수정: Color.value 오류 해결
    validations:
      required: true

  - type: textarea
    id: related-issues
    attributes:
      label: 🔗 관련 이슈
      description: 이 PR과 관련된 이슈가 있다면 번호를 입력해주세요.
      placeholder: |
        Closes #123
        Fixes #456
        Related to #789

  - type: checkboxes
    id: testing
    attributes:
      label: 🧪 테스트
      description: 변경사항에 대한 테스트를 완료했나요?
      options:
        - label: 로컬에서 게임 실행 테스트 완료
        - label: 변경된 기능의 동작 확인 완료
        - label: 기존 기능들이 정상 동작하는지 확인
        - label: 오류 로그 확인 (게임로그 폴더)
        - label: 다양한 상황에서 테스트 진행
        - label: 성능 영향 검토 (해당하는 경우)

  - type: checkboxes
    id: code-quality
    attributes:
      label: 📋 코드 품질
      description: 코드 품질 기준을 확인해주세요.
      options:
        - label: 기존 코딩 스타일을 따름
        - label: 함수/클래스에 적절한 독스트링 추가
        - label: 복잡한 로직에 주석 추가
        - label: 한글 주석으로 설명 작성
        - label: 변수명과 함수명이 명확함
        - label: 불필요한 코드 제거

  - type: textarea
    id: breaking-changes
    attributes:
      label: ⚠️ 중요한 변경사항
      description: 기존 기능을 변경하거나 제거한 내용이 있나요?
      placeholder: |
        - 세이브 파일 형식 변경 (기존 세이브와 호환되지 않음)
        - API 인터페이스 변경
        - 설정 파일 구조 변경
        - 없음 (기존 기능에 영향 없음)

  - type: textarea
    id: performance-impact
    attributes:
      label: ⚡ 성능 영향
      description: 이 변경사항이 게임 성능에 미치는 영향이 있나요?
      placeholder: |
        - 메모리 사용량 변화
        - 로딩 시간 변화  
        - FPS/응답성 변화
        - 없음 (성능에 영향 없음)

  - type: textarea
    id: visual-changes
    attributes:
      label: 🎨 시각적 변경사항
      description: UI나 게임 화면에 시각적 변화가 있다면 스크린샷을 첨부해주세요.
      placeholder: |
        스크린샷을 드래그 앤 드롭으로 첨부하거나
        Before/After 이미지를 추가해주세요.

  - type: checkboxes
    id: documentation
    attributes:
      label: 📚 문서화
      description: 문서 업데이트가 필요한 변경사항인가요?
      options:
        - label: README.md 업데이트 필요
        - label: 코드 주석 추가/수정
        - label: API 문서 업데이트 필요
        - label: 사용자 가이드 업데이트 필요
        - label: 개발자 문서 업데이트 필요
        - label: 문서 업데이트 불필요

  - type: dropdown
    id: compatibility
    attributes:
      label: 🔄 호환성
      description: 이 변경사항이 호환성에 미치는 영향은?
      options:
        - ✅ 완전 호환 - 기존 기능에 영향 없음
        - 🟡 부분 호환 - 일부 설정 재조정 필요
        - 🟠 제한적 호환 - 기존 데이터 마이그레이션 필요
        - 🔴 비호환 - 기존 데이터/설정 초기화 필요

  - type: textarea
    id: migration-guide
    attributes:
      label: 🔄 마이그레이션 가이드
      description: 기존 사용자가 새 버전으로 업데이트할 때 필요한 작업이 있나요?
      placeholder: |
        - 설정 파일 백업 후 삭제 필요
        - 세이브 파일 변환 도구 사용
        - 특별한 작업 불필요
        - 기타: ...

  - type: checkboxes
    id: checklist
    attributes:
      label: ✅ 최종 체크리스트
      description: PR 제출 전 다음 사항들을 확인해주세요.
      options:
        - label: 코드가 main 브랜치와 충돌 없이 병합 가능합니다
          required: true
        - label: 커밋 메시지가 명확하고 의미가 있습니다
          required: true
        - label: 변경사항이 게임의 전반적인 품질을 향상시킵니다
          required: true
        - label: 코드 리뷰를 받을 준비가 되었습니다
          required: true

  - type: textarea
    id: additional-notes
    attributes:
      label: 📋 추가 노트
      description: 리뷰어가 알아야 할 추가 정보가 있다면 작성해주세요.
      placeholder: |
        - 특별히 주의 깊게 봐야 할 부분
        - 알려진 제한사항이나 임시 해결책
        - 향후 개선 계획
        - 기타 참고사항
