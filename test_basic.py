#!/usr/bin/env python3
"""
Dawn Of Stellar - 기본 테스트 스위트
"""

import sys
import os
import pytest

# 테스트를 위해 프로젝트 루트를 패스에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_python_version():
    """Python 버전 확인"""
    assert sys.version_info >= (3, 8), "Python 3.8 이상이 필요합니다"

def test_required_modules():
    """필수 모듈 import 테스트"""
    try:
        import pygame
        import numpy
        import colorama
    except ImportError as e:
        pytest.fail(f"필수 모듈을 import할 수 없습니다: {e}")

def test_game_module_structure():
    """게임 모듈 구조 테스트"""
    # game 디렉토리 존재 확인
    assert os.path.exists("game"), "game 디렉토리가 존재하지 않습니다"
    
    # 핵심 모듈 파일 존재 확인
    core_modules = [
        "game/character.py",
        "game/combat.py", 
        "game/world.py",
        "game/brave_combat.py",
        "game/meta_progression.py"
    ]
    
    missing_modules = []
    for module in core_modules:
        if not os.path.exists(module):
            missing_modules.append(module)
    
    assert not missing_modules, f"누락된 핵심 모듈: {missing_modules}"

def test_main_entry_point():
    """main.py 진입점 확인"""
    assert os.path.exists("main.py"), "main.py 파일이 존재하지 않습니다"
    
    # main.py가 실행 가능한지 확인 (구문 오류 체크)
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            code = f.read()
        compile(code, "main.py", "exec")
    except SyntaxError as e:
        pytest.fail(f"main.py에 구문 오류가 있습니다: {e}")

def test_version_file():
    """버전 파일 확인"""
    assert os.path.exists("version.py"), "version.py 파일이 존재하지 않습니다"
    
    try:
        import version
        assert hasattr(version, '__version__'), "version.py에 __version__ 상수가 없습니다"
        assert version.__version__ == "2.0.0", f"예상 버전: 2.0.0, 실제: {version.__version__}"
        assert hasattr(version, 'GAME_TITLE'), "version.py에 GAME_TITLE 상수가 없습니다"
    except ImportError as e:
        pytest.fail(f"version.py를 import할 수 없습니다: {e}")

def test_audio_files():
    """오디오 파일 존재 확인"""
    audio_dir = "game/audio"
    if os.path.exists(audio_dir):
        bgm_dir = os.path.join(audio_dir, "bgm")
        sfx_dir = os.path.join(audio_dir, "sfx")
        
        # BGM 폴더에 최소 1개의 음악 파일이 있는지 확인
        if os.path.exists(bgm_dir):
            bgm_files = [f for f in os.listdir(bgm_dir) if f.endswith(('.mp3', '.wav', '.ogg'))]
            assert len(bgm_files) > 0, "BGM 폴더에 음악 파일이 없습니다"
        
        # SFX 폴더에 최소 1개의 효과음 파일이 있는지 확인  
        if os.path.exists(sfx_dir):
            sfx_files = [f for f in os.listdir(sfx_dir) if f.endswith(('.wav', '.mp3', '.ogg'))]
            assert len(sfx_files) > 0, "SFX 폴더에 효과음 파일이 없습니다"

def test_readme_exists():
    """README 파일 존재 확인"""
    readme_files = ["README.md", "README_NEW.md"]
    exists = any(os.path.exists(f) for f in readme_files)
    assert exists, "README 파일이 존재하지 않습니다"

def test_installation_script():
    """자동설치 스크립트 확인"""
    install_script = "자동설치.bat"
    assert os.path.exists(install_script), "자동설치.bat 파일이 존재하지 않습니다"
    
    # 스크립트 파일이 비어있지 않은지 확인
    with open(install_script, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert len(content) > 100, "자동설치.bat 파일이 너무 짧습니다"

if __name__ == "__main__":
    # 직접 실행 시 pytest 실행
    pytest.main([__file__, "-v"])
