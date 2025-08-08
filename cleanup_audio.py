#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사운드 파일 정리 스크립트
실제 사용되는 파일들만 남기고 나머지는 아카이브로 이동
"""

import os
import shutil
import re

def get_used_audio_files():
    """실제 코드에서 사용되는 오디오 파일 목록 추출"""
    used_files = set()
    
    # 파이썬 파일들에서 오디오 파일 참조 검색
    for root, dirs, files in os.walk('.'):
        # __pycache__, .git 등 제외
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # .mp3, .wav, .ogg 파일 참조 찾기
                        audio_refs = re.findall(r'[\'"]([^\'"\s]+\.(mp3|wav|ogg))[\'"]', content)
                        for ref, ext in audio_refs:
                            # 경로에서 파일명만 추출
                            filename = os.path.basename(ref)
                            used_files.add(filename)
                except Exception as e:
                    print(f"파일 읽기 오류 {file_path}: {e}")
    
    return used_files

def archive_unused_audio():
    """사용하지 않는 오디오 파일들을 아카이브로 이동"""
    
    # 실제 사용되는 파일들
    used_files = get_used_audio_files()
    
    print("=== 사용되는 오디오 파일들 ===")
    for file in sorted(used_files):
        print(f"  ✓ {file}")
    
    # BGM과 SFX 디렉토리 확인
    bgm_dir = "game/audio/bgm"
    sfx_dir = "game/audio/sfx"
    archive_dir = "audio_archive"
    
    # 아카이브 디렉토리 생성
    os.makedirs(f"{archive_dir}/bgm", exist_ok=True)
    os.makedirs(f"{archive_dir}/sfx", exist_ok=True)
    
    moved_count = 0
    kept_count = 0
    
    # BGM 파일들 처리
    if os.path.exists(bgm_dir):
        print(f"\n=== BGM 파일 정리 ({bgm_dir}) ===")
        for file in os.listdir(bgm_dir):
            if file.endswith(('.mp3', '.wav', '.ogg')):
                if file in used_files:
                    print(f"  ✓ 유지: {file}")
                    kept_count += 1
                else:
                    src = os.path.join(bgm_dir, file)
                    dst = os.path.join(archive_dir, "bgm", file)
                    shutil.move(src, dst)
                    print(f"  📦 아카이브: {file}")
                    moved_count += 1
    
    # SFX 파일들 처리
    if os.path.exists(sfx_dir):
        print(f"\n=== SFX 파일 정리 ({sfx_dir}) ===")
        for file in os.listdir(sfx_dir):
            if file.endswith(('.mp3', '.wav', '.ogg')):
                if file in used_files:
                    print(f"  ✓ 유지: {file}")
                    kept_count += 1
                else:
                    src = os.path.join(sfx_dir, file)
                    dst = os.path.join(archive_dir, "sfx", file)
                    shutil.move(src, dst)
                    print(f"  📦 아카이브: {file}")
                    moved_count += 1
    
    print(f"\n=== 정리 완료 ===")
    print(f"유지된 파일: {kept_count}개")
    print(f"아카이브된 파일: {moved_count}개")
    print(f"아카이브 위치: {archive_dir}/")
    
    # 용량 절약 효과 계산
    if moved_count > 0:
        archive_size = 0
        for root, dirs, files in os.walk(archive_dir):
            for file in files:
                file_path = os.path.join(root, file)
                archive_size += os.path.getsize(file_path)
        
        print(f"절약된 용량: {archive_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    archive_unused_audio()
