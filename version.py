# Dawn Of Stellar - Version Information

__version__ = "3.1.0"
__title__ = "Dawn Of Stellar - 별빛의 여명"
__description__ = "차세대 ASCII 기반 전략 로그라이크 RPG"
__author__ = "APTOL-7176"
__author_email__ = "iamckck49@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/APTOL-7176/Dawn-of-Stellar"

# Release Information
RELEASE_DATE = "2025-08-10"
MAJOR_VERSION = 3
MINOR_VERSION = 1
PATCH_VERSION = 0

# Game Information
GAME_TITLE = "Dawn Of Stellar"
GAME_SUBTITLE = "별빛의 여명"
GAME_VERSION_DISPLAY = f"v{__version__}"

# Build Information
BUILD_TYPE = "Release"
PYTHON_MIN_VERSION = "3.8"
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
    
    if __version__ == "3.1.0":
        print(f"\n📋 v{__version__} 업데이트 내역:")
        for note in VERSION_NOTES_310:
            print(f"   {note}")
