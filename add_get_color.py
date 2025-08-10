#!/usr/bin/env python3
"""
모든 게임 파일에 get_color 함수를 추가하는 스크립트
"""

def add_get_color_function():
    """각 파일에 get_color 함수 추가"""
    
    # get_color 함수 정의
    get_color_code = '''
# 안전한 색상 상수 정의
COLORS = {
    'RESET': '\\033[0m',
    'BOLD': '\\033[1m',
    'DIM': '\\033[2m', 
    'UNDERLINE': '\\033[4m',
    'BLACK': '\\033[30m',
    'RED': '\\033[31m',
    'GREEN': '\\033[32m',
    'YELLOW': '\\033[33m',
    'BLUE': '\\033[34m',
    'MAGENTA': '\\033[35m',
    'CYAN': '\\033[36m',
    'WHITE': '\\033[37m',
    'BRIGHT_BLACK': '\\033[90m',
    'BRIGHT_RED': '\\033[91m',
    'BRIGHT_GREEN': '\\033[92m',
    'BRIGHT_YELLOW': '\\033[93m',
    'BRIGHT_BLUE': '\\033[94m',
    'BRIGHT_MAGENTA': '\\033[95m',
    'BRIGHT_CYAN': '\\033[96m',
    'BRIGHT_WHITE': '\\033[97m',
    'BG_BLACK': '\\033[40m',
    'BG_RED': '\\033[41m',
    'BG_GREEN': '\\033[42m',
    'BG_YELLOW': '\\033[43m',
    'BG_BLUE': '\\033[44m',
    'BG_MAGENTA': '\\033[45m',
    'BG_CYAN': '\\033[46m',
    'BG_WHITE': '\\033[47m'
}

def get_color(color_name):
    """안전한 색상 코드 반환"""
    return COLORS.get(color_name, '')
'''

    target_files = [
        'game/buffered_display.py',
        'game/combat_visual.py',
        'game/optimized_gauge_system.py',
        'game/stable_display.py',
        'game/status_effects.py',
        'game/ui_system.py',
        'game/unified_damage_system.py'
    ]

    for file_path in target_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 이미 get_color 함수가 있는지 확인
            if 'def get_color(' in content:
                print(f"ℹ️ {file_path}: get_color 함수가 이미 존재함")
                continue
                
            # import 문 뒤에 get_color 함수 추가
            lines = content.split('\n')
            insert_index = 0
            
            # import 문이 끝나는 위치 찾기
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_index = i + 1
                elif line.strip() == '' and insert_index > 0:
                    insert_index = i + 1
                elif line.strip() != '' and insert_index > 0:
                    break
                    
            # get_color 함수 삽입
            lines.insert(insert_index, get_color_code)
            new_content = '\n'.join(lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"✅ {file_path}: get_color 함수 추가 완료")
            
        except Exception as e:
            print(f"❌ {file_path} 처리 오류: {e}")

if __name__ == "__main__":
    add_get_color_function()
