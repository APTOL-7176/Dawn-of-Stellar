"""
게임 패키지 초기화 파일
"""

__version__ = "1.0.0"
__author__ = "Roguelike Game Developer"

# 주요 모듈 import
try:
    from . import story_system
except ImportError:
    pass  # 모듈이 없어도 패키지는 로드됨
