#!/usr/bin/env python3
"""
색상 코드 정리 스크립트 v2.0
잘못 변환된 Color.BRIGHT.value_XXX.value → Color.BRIGHT_XXX.value 형태로 수정
"""

import os
import re
import sys
from pathlib import Path

def fix_broken_color_codes(file_path):
    """망가진 색상 코드를 수정합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 수정 패턴들 (망가진 색상 코드들)
        patterns = [
            # Pattern 1: Color.BRIGHT.value_RED.value → Color.BRIGHT_RED.value
            (r'Color\.BRIGHT\.value_([A-Z_]+)\.value', r'Color.BRIGHT_\1.value'),
            
            # Pattern 2: Color.value_XXXX.value → Color.XXXX.value
            (r'Color\.value_([A-Z_]+)\.value', r'Color.\1.value'),
            
            # Pattern 3: Color.XXXX.value.value → Color.XXXX.value (중복 .value 제거)
            (r'Color\.([A-Z_]+)\.value\.value', r'Color.\1.value'),
            
            # Pattern 4: {Color.XXXX.value.value} → {Color.XXXX.value}
            (r'\{Color\.([A-Z_]+)\.value\.value\}', r'{Color.\1.value}'),
        ]
        
        # 수정 적용
        changes_made = 0
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes_made += len(re.findall(pattern, content))
                content = new_content
        
        # 변경사항이 있으면 파일 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        
        return 0
    
    except Exception as e:
        print(f"❌ 오류 발생 ({file_path}): {e}")
        return 0

def main():
    """메인 함수"""
    print("🔧 색상 코드 정리 스크립트 v2.0")
    print("=" * 50)
    
    # 주요 파일들만 수정 (게임 핵심 파일들)
    key_files = [
        'game/brave_combat.py',
        'game/stable_display.py', 
        'game/optimized_gauge_system.py',
        'game/combat_visual.py',
        'game/buffered_display.py'
    ]
    
    print(f"📁 {len(key_files)}개 핵심 파일 정리 중...")
    print("")
    
    # 수정 실행
    total_changes = 0
    files_modified = 0
    
    for file_path in key_files:
        if os.path.exists(file_path):
            changes = fix_broken_color_codes(file_path)
            if changes > 0:
                files_modified += 1
                total_changes += changes
                print(f"✅ {file_path}: {changes}개 정리")
    
    print("")
    print("=" * 50)
    print(f"🎯 정리 완료!")
    print(f"📝 {files_modified}개 파일 정리")
    print(f"🔧 총 {total_changes}개 색상 코드 정리")
    
    if total_changes > 0:
        print("")
        print("🎮 색상 코드가 정리되었습니다!")
        print("🌈 이제 게임에서 색상이 정상적으로 표시됩니다!")
    else:
        print("")
        print("ℹ️  정리할 색상 코드가 없습니다.")

if __name__ == "__main__":
    main()
