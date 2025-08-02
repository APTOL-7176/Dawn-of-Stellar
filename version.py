# Dawn Of Stellar - Version Information

__version__ = "2.1.1"
__title__ = "Dawn Of Stellar - 별빛의 여명"
__description__ = "차세대 ASCII 기반 전략 로그라이크 RPG"
__author__ = "APTOL-7176"
__author_email__ = "aptol.7176@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/APTOL-7176/Dawn-of-Stellar"

# Release Information
RELEASE_DATE = "2025-08-03"
MAJOR_VERSION = 2
MINOR_VERSION = 1
PATCH_VERSION = 1

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
