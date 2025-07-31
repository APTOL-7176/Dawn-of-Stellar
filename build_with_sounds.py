#!/usr/bin/env python3
"""
사운드 파일을 포함한 PyInstaller 빌드 스크립트
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def get_all_sound_files():
    """모든 사운드 파일 목록을 생성합니다"""
    sounds_dir = Path("sounds")
    if not sounds_dir.exists():
        print("⚠️ sounds 폴더를 찾을 수 없습니다!")
        return []
    
    sound_files = []
    
    # BGM 파일들
    bgm_dir = sounds_dir / "bgm"
    if bgm_dir.exists():
        for bgm_file in bgm_dir.glob("*.mp3"):
            sound_files.append((str(bgm_file), "sounds/bgm"))
    
    # SFX 파일들
    sfx_dir = sounds_dir / "sfx"
    if sfx_dir.exists():
        for sfx_file in sfx_dir.glob("*.wav"):
            sound_files.append((str(sfx_file), "sounds/sfx"))
    
    print(f"📁 발견된 사운드 파일: {len(sound_files)}개")
    return sound_files

def create_pyinstaller_spec():
    """PyInstaller spec 파일을 생성합니다"""
    sound_files = get_all_sound_files()
    
    # 데이터 파일 목록 생성
    data_files_str = "[\n"
    for src, dst in sound_files:
        data_files_str += f"    ('{src}', '{dst}'),\n"
    data_files_str += "]"
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 사운드 파일들을 포함하는 데이터 목록
sound_files = {data_files_str}

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=sound_files,
    hiddenimports=[
        'pygame',
        'numpy',
        'game.audio_system',
        'game.*',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Dawn_of_Stellar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    with open("dawn_of_stellar.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ PyInstaller spec 파일이 생성되었습니다: dawn_of_stellar.spec")

def build_executable():
    """실행 파일을 빌드합니다"""
    print("🔨 실행 파일 빌드를 시작합니다...")
    
    # spec 파일 생성
    create_pyinstaller_spec()
    
    # 가상환경의 Python 경로 찾기
    venv_python = r"D:/로그라이크_2/.venv/Scripts/python.exe"
    if not os.path.exists(venv_python):
        venv_python = sys.executable  # 기본 Python 사용
    
    # PyInstaller로 빌드
    try:
        result = subprocess.run([
            venv_python, "-m", "PyInstaller",
            "--clean",
            "dawn_of_stellar.spec"
        ], check=True, capture_output=True, text=True)
        
        print("✅ 빌드 성공!")
        print(f"실행 파일 위치: dist/Dawn_of_Stellar.exe")
        
        # 빌드 로그 출력
        if result.stdout:
            print("\n📋 빌드 로그:")
            print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
        if e.stderr:
            print(f"오류 메시지: {e.stderr}")
        return False
    
    return True

def copy_additional_files():
    """추가 파일들을 dist 폴더에 복사합니다"""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("⚠️ dist 폴더를 찾을 수 없습니다!")
        return
    
    # 필요한 파일들을 dist 폴더에 복사
    files_to_copy = [
        "README.md",
        "game_settings.json",
        "permanent_progress.json",
    ]
    
    for file_name in files_to_copy:
        src = Path(file_name)
        if src.exists():
            dst = dist_dir / file_name
            shutil.copy2(src, dst)
            print(f"📄 복사됨: {file_name}")

def main():
    """메인 함수"""
    print("🎵 Dawn of Stellar - 사운드 포함 빌드 스크립트")
    print("=" * 60)
    
    # 현재 디렉토리 확인
    if not Path("main.py").exists():
        print("❌ main.py 파일을 찾을 수 없습니다!")
        print("이 스크립트를 프로젝트 루트 디렉토리에서 실행해주세요.")
        return
    
    # 사운드 파일 확인
    sound_files = get_all_sound_files()
    if not sound_files:
        print("⚠️ 사운드 파일이 없습니다. 사운드 없이 빌드됩니다.")
    
    # 빌드 실행
    if build_executable():
        copy_additional_files()
        print("\n🎉 빌드 완료!")
        print("dist/Dawn_of_Stellar.exe 파일을 실행해보세요.")
    else:
        print("\n❌ 빌드 실패")

if __name__ == "__main__":
    main()
