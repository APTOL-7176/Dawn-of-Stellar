# Dawn Of Stellar - Version Information

__version__ = "4.3.0"
__title__ = "Dawn Of Stellar - 별빛의 여명"
__description__ = "완전체 로그라이크 RPG - 밸런스 시스템 통합 + 스토리 BGM 수정"
__author__ = "APTOL-7176"
__author_email__ = "iamckck49@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/APTOL-7176/Dawn-of-Stellar"

# Release Information
RELEASE_DATE = "2025-08-14"
MAJOR_VERSION = 4
MINOR_VERSION = 3
PATCH_VERSION = 0

# Game Information
GAME_TITLE = "Dawn Of Stellar"
GAME_SUBTITLE = "별빛의 여명"
GAME_VERSION_DISPLAY = f"v{__version__}"

# Build Information
BUILD_TYPE = "Release"
PYTHON_MIN_VERSION = "3.10"
PYTHON_RECOMMENDED = "3.11"

def get_version_info():
    """버전 정보를 딕셔너리로 반환"""
    return {
        "version": __version__,
        "title": __title__,
        "description": __description__,
        "author": __author__,
        "release_date": RELEASE_DATE,
        "build_type": BUILD_TYPE,
        "python_min": PYTHON_MIN_VERSION,
        "python_recommended": PYTHON_RECOMMENDED
    }

# v5.0.0 메이저 업데이트 내역 (2025-08-13)
VERSION_NOTES_500 = [
    "🎮 완전체 게임 시스템 완성 - 스타팅 장비 4명 균등 분배",
    "⚔️ 28개 직업별 맞춤 장비 시스템 - 부위 겹침 방지",
    "⚡ B키 직접 저장 기능 - 맵에서 바로 저장 가능",
    "🌿 통합 필드 메뉴 - F키로 채집, 요리, 스킬, 상점, 저장 접근",
    "🛒 상점 정보 대폭 강화 - 가격, 재고, 희귀도, 스탯, 내구도 표시",
    "📜 파티 히스토리 시스템 복구 - 저장된 파티 불러오기 기능",
    "📱 Flutter 모바일 클라이언트 완성 - 터미널 스타일 UI",
    "🗂️ 종합 로깅 시스템 - 7종류 한국어 로그 파일 세션별 관리",
    "🔧 장비 슬롯 자동 감지 시스템 - 아이템명 기반 타입 분류",
    "🎯 공정한 아이템 분배 - 첫 번째 파티원 독점 문제 해결",
    "📊 실시간 문제 진단 - 이동, 전투, AI 문제 로그 추적",
    "💫 완성도 극대화 - 모든 시스템 안정화 및 최적화"
]

# v4.3.0 업데이트 내역 (2025-08-14)
VERSION_NOTES_430 = [
    "🎯 완전한 밸런스 시스템 v3.0 통합 - final_integrated_balance_system.py",
    "� 스토리 시스템 BGM import 경로 수정 - game.audio -> game.audio_system",
    "🔧 메뉴 시스템 인덱스 정렬 문제 해결",
    "� 오디오 폴더 구조 자동 생성",
    "� 모든 게임 모드에서 통일된 밸런스 적용",
    "� AI 게임 모드 검증 시스템 강화",
    "� 난이도별 스토리 시스템 완성 (평온/보통/도전/악몽/지옥)",
    "🎭 28개 직업별 고유 스토리 및 특성 시스템",
    "🔒 .gitignore 업데이트로 디버그 파일 제외",
    "🚀 코드 최적화 및 안정성 향상"
]

# v3.1.1 업데이트 내역 (2025-08-10)
VERSION_NOTES_311 = [
    "🔧 모든 Color.value 오류 완전 해결 (915+ 패턴 수정)",
    "🎮 전투 자동화 개선 - Enter 입력 대기 제거",
    "⚡ 전투 로그 확인 시간 단축 (0.5초 → 0.2초)",
    "🏆 승리/패배 시 자동 진행 (1-2초 대기 후 자동 계속)",
    "📊 상세 정보 표시 시 자동 계속 (0.5초)",
    "🎯 공격/스킬 사용 후 대기 시간 단축 (2초 → 0.5초)",
    "🤖 AI 턴 처리 속도 향상 (모든 대기 시간 단축)",
    "🛠️ log_debug 메서드 인수 오류 완전 수정",
    "🎪 전투 화면 상단 빈 줄 3줄 추가 (깔끔한 UI)",
    "🚀 전반적인 게임 진행 속도 대폭 향상"
]

# v3.1.0 업데이트 내역
VERSION_NOTES_310 = [
    "🚀 완전한 로깅 시스템 구현",
    "🐛 이동 시스템 문제 해결 완료", 
    "⚔️ ATB 시스템 속도 밸런스 조정",
    "🛡️ AI 모드 검증 시스템 강화",
    "🎮 화면 깜빡임 문제 해결",
    "🗺️ 맵 장치 상호작용 완전 구현",
    "📊 종합 로깅 시스템 (세션별 한국어 파일명)",
    "🔧 커서 메뉴 시스템 안정화"
]

def get_version_string():
    """게임에서 표시할 버전 문자열 반환"""
    return f"{GAME_TITLE} {GAME_VERSION_DISPLAY} - {GAME_SUBTITLE}"

def print_version_info():
    """버전 정보 출력"""
    print(f"{GAME_TITLE} {GAME_VERSION_DISPLAY}")
    print(f"{GAME_SUBTITLE}")
    print(f"Release Date: {RELEASE_DATE}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    
    if __version__ == "4.3.0":
        print(f"\n📋 v{__version__} 업데이트 내역:")
        for note in VERSION_NOTES_430:
            print(f"   {note}")
    elif __version__ == "3.1.1":
        print(f"\n📋 v{__version__} 업데이트 내역:")
        for note in VERSION_NOTES_311:
            print(f"   {note}")
    elif __version__ == "3.1.0":
        print(f"\n📋 v{__version__} 업데이트 내역:")
        for note in VERSION_NOTES_310:
            print(f"   {note}")
