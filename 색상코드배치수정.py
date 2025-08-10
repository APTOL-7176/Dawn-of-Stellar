#!/usr/bin/env python3
"""
색상 코드 배치 수정 스크립트
모든 Python 파일에서 Color.XXX.value}Color → Color.XXX.value}Color 형태로 수정
"""

import os
import re
import sys
from pathlib import Path

def fix_color_codes_in_file(file_path):
    """파일의 색상 코드를 수정합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 백업용 원본 내용
        original_content = content
        
        # 수정 패턴들
        patterns = [
            # Pattern 1: Color.XXX.value}Color → Color.XXX.value}Color
            (r'Color\.([A-Z_]+)\}Color', r'Color.\1.value}Color'),
            
            # Pattern 2: {Color.XXX.value → {Color.XXX.value
            (r'\{Color\.([A-Z_]+)([^.a-zA-Z])', r'{Color.\1.value\2'),
            
            # Pattern 3: "Color.XXX.value → "Color.XXX.value
            (r'"Color\.([A-Z_]+)([^.a-zA-Z])', r'"Color.\1.value\2'),
            
            # Pattern 4: f-string 내부에서 Color.XXX → Color.XXX.value
            (r'f"([^"]*?)Color\.([A-Z_]+)([^.a-zA-Z][^"]*?)"', r'f"\1Color.\2.value\3"'),
            
            # Pattern 5: print 문에서 Color.XXX → Color.XXX.value
            (r'print\(([^)]*?)Color\.([A-Z_]+)([^.a-zA-Z][^)]*?)\)', r'print(\1Color.\2.value\3)'),
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
    print("🎨 색상 코드 배치 수정 시작...")
    print("=" * 50)
    
    # 수정할 파일 찾기
    python_files = []
    for root, dirs, files in os.walk('.'):
        # 제외할 디렉토리
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
    
    print(f"📁 {len(python_files)}개 Python 파일 발견")
    print("")
    
    # 수정 실행
    total_changes = 0
    files_modified = 0
    
    for file_path in python_files:
        changes = fix_color_codes_in_file(file_path)
        if changes > 0:
            files_modified += 1
            total_changes += changes
            print(f"✅ {file_path}: {changes}개 수정")
    
    print("")
    print("=" * 50)
    print(f"🎯 수정 완료!")
    print(f"📝 {files_modified}개 파일 수정")
    print(f"🔧 총 {total_changes}개 색상 코드 수정")
    
    if total_changes > 0:
        print("")
        print("🎮 이제 게임을 다시 실행해보세요!")
        print("🌈 색상이 정상적으로 표시될 것입니다!")
    else:
        print("")
        print("ℹ️  수정할 색상 코드가 없습니다.")

if __name__ == "__main__":
    main()
