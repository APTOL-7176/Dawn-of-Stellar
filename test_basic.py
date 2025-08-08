#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dawn of Stellar - 간단한 테스트 파일
GitHub Actions에서 사용할 기본 테스트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """기본 모듈들이 정상적으로 임포트되는지 테스트"""
    print("📝 기본 임포트 테스트 시작...")
    
    try:
        import config
        print("✅ config 모듈 임포트 성공")
    except ImportError as e:
        print(f"❌ config 모듈 임포트 실패: {e}")
        return False
    
    try:
        from game.character import Character
        print("✅ Character 클래스 임포트 성공")
    except ImportError as e:
        print(f"❌ Character 클래스 임포트 실패: {e}")
        return False
    
    try:
        import main
        print("✅ main 모듈 임포트 성공")
    except ImportError as e:
        print(f"❌ main 모듈 임포트 실패: {e}")
        return False
    
    return True

def test_directories():
    """필요한 디렉토리들이 존재하는지 테스트"""
    print("📁 디렉토리 존재 테스트 시작...")
    
    required_dirs = ['game', 'sounds', 'sounds/bgm', 'sounds/sfx']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name} 디렉토리 존재")
        else:
            print(f"❌ {dir_name} 디렉토리 누락")
            return False
    
    return True

def test_sound_files():
    """사운드 파일들이 존재하는지 테스트"""
    print("🎵 사운드 파일 테스트 시작...")
    
    bgm_count = len([f for f in os.listdir('sounds/bgm') if f.endswith('.mp3')])
    sfx_count = len([f for f in os.listdir('sounds/sfx') if f.endswith('.wav')])
    
    print(f"🎵 BGM 파일 수: {bgm_count}")
    print(f"🔊 SFX 파일 수: {sfx_count}")
    
    if bgm_count > 0 and sfx_count > 0:
        print("✅ 사운드 파일들이 정상적으로 존재")
        return True
    else:
        print("❌ 사운드 파일이 부족함")
        return False

def main():
    """메인 테스트 함수"""
    print("🎮 Dawn of Stellar - 기본 테스트 시작")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_directories,
        test_sound_files
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ 테스트 통과\n")
            else:
                failed += 1
                print("❌ 테스트 실패\n")
        except Exception as e:
            failed += 1
            print(f"❌ 테스트 에러: {e}\n")
    
    print("=" * 50)
    print(f"📊 테스트 결과: {passed}개 통과, {failed}개 실패")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 모든 테스트 통과!")
        sys.exit(0)

if __name__ == "__main__":
    main()
