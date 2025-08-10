#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dawn of Stellar v4.1.0 - Setup Script
🎮 완전체 로그라이크 RPG + AI 채팅 시스템
"""

from setuptools import setup, find_packages
import os
import sys

# 버전 정보
VERSION = "4.1.0"
DESCRIPTION = "완전체 로그라이크 RPG + AI 채팅 시스템"
LONG_DESCRIPTION = """
🌟 Dawn of Stellar v4.1.0 🌟

완전체 한국어 로그라이크 RPG 게임 + AI 채팅 시스템

🔥 주요 기능:
- 🇰🇷 27개 직업별 한국어 AI 성격 (로바트)
- 🤖 Ollama EEVE-Korean 모델 연동
- ⚔️ 브레이브 전투 시스템 (FF 스타일)
- 🎭 28개 고유 직업 클래스
- 📱 Flutter 모바일 클라이언트
- 🎵 실시간 BGM/SFX 시스템
- 💾 클라우드 저장 시스템

🎯 지원 플랫폼:
- Windows 10/11 (64-bit)
- macOS 10.15+
- Linux (Ubuntu 20.04+)
- Android 7.0+ (Flutter)
- iOS 12.0+ (Flutter)

📦 설치:
    pip install dawn-of-stellar

🚀 실행:
    python -m dawn_of_stellar
    또는
    dawn-stellar

📖 문서: https://github.com/username/dawn-of-stellar
"""

# README 파일 읽기
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return LONG_DESCRIPTION

# 요구사항 파일 읽기
def read_requirements():
    requirements = []
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    # 조건부 의존성 제거
                    if ";" in line:
                        line = line.split(";")[0].strip()
                    if "extra ==" in line:
                        continue
                    requirements.append(line)
    except FileNotFoundError:
        requirements = [
            "pygame>=2.5.0",
            "colorama>=0.4.6",
            "numpy>=1.24.0",
            "aiohttp>=3.8.0",
            "requests>=2.31.0",
            "pydantic>=2.0.0"
        ]
    return requirements

# 개발용 의존성
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.7.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0"
]

# AI 확장 의존성
ai_requirements = [
    "openai>=1.0.0",
    "anthropic>=0.25.0",
    "google-generativeai>=0.4.0",
    "ollama>=0.1.7"
]

# GUI 의존성
gui_requirements = [
    "tkinter; platform_system=='Linux'",
    "rich>=13.0.0",
    "textual>=0.35.0"
]

setup(
    name="dawn-of-stellar",
    version=VERSION,
    author="Dawn of Stellar Team",
    author_email="contact@dawnofstellar.com",
    description=DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/dawn-of-stellar",
    project_urls={
        "Homepage": "https://dawnofstellar.com",
        "Documentation": "https://docs.dawnofstellar.com",
        "Repository": "https://github.com/username/dawn-of-stellar",
        "Issue Tracker": "https://github.com/username/dawn-of-stellar/issues",
        "Discord": "https://discord.gg/dawnofstellar"
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "dawn_of_stellar": [
            "assets/audio/*.ogg",
            "assets/audio/*.wav",
            "assets/fonts/*.ttf",
            "assets/data/*.json",
            "game/data/*.json",
            "saves/*.json",
            "config/*.json"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Topic :: Games/Entertainment :: Turn Based Strategy",
        "Topic :: Software Development :: Libraries :: pygame",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Natural Language :: Korean",
        "Environment :: Console",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Environment :: X11 Applications"
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": dev_requirements,
        "ai": ai_requirements,
        "gui": gui_requirements,
        "all": dev_requirements + ai_requirements + gui_requirements
    },
    entry_points={
        "console_scripts": [
            "dawn-stellar=main:main",
            "dawn-stellar-ai=simple_robat_chat:main",
            "dawn-stellar-launcher=launcher:main",
            "dawn-stellar-performance=performance_launcher:main"
        ]
    },
    keywords=[
        "game", "roguelike", "rpg", "korean", "ai", "chatbot",
        "terminal", "ascii", "fantasy", "adventure", "strategy",
        "brave", "combat", "multiplayer", "flutter", "mobile"
    ],
    zip_safe=False,
    platforms=["Windows", "macOS", "Linux", "Android", "iOS"],
    
    # 메타데이터
    license="MIT",
    maintainer="Dawn of Stellar Team",
    maintainer_email="maintainer@dawnofstellar.com",
    
    # 추가 옵션
    options={
        "bdist_wheel": {
            "universal": False
        }
    }
)

# 설치 후 메시지
def print_install_message():
    print(f"""
🌟 Dawn of Stellar v{VERSION} 설치 완료! 🌟

🚀 게임 실행:
    dawn-stellar

🤖 AI 채팅 테스트:
    dawn-stellar-ai

⚡ 성능 최적화 런처:
    dawn-stellar-performance

📖 도움말:
    dawn-stellar --help

🎮 즐거운 게임 되세요! 🎮
""")

if __name__ == "__main__":
    # 직접 실행 시 설치 진행
    import subprocess
    subprocess.run([sys.executable, "setup.py", "install"])
    print_install_message()
