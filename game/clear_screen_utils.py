"""
강력한 화면 클리어 시스템
화면 중첩을 완전히 방지하는 유틸리티 함수들 + 하단 정렬 시스템 + 고성능 프레임레이트
"""

import os
import sys
import time

# 🎮 고성능 프레임레이트 설정
MIN_FPS = 20
MAX_FPS = 60
TARGET_FPS = 30  # 기본 타겟
FRAME_TIME = 1.0 / TARGET_FPS  # 프레임 간격

class FrameRateController:
    """프레임레이트 제어 클래스"""
    
    def __init__(self, target_fps=TARGET_FPS):
        self.target_fps = max(MIN_FPS, min(MAX_FPS, target_fps))
        self.frame_time = 1.0 / self.target_fps
        self.last_frame_time = time.time()
    
    def wait_for_next_frame(self):
        """다음 프레임까지 대기"""
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        if elapsed < self.frame_time:
            time.sleep(self.frame_time - elapsed)
        
        self.last_frame_time = time.time()
    
    def set_fps(self, fps):
        """FPS 설정"""
        self.target_fps = max(MIN_FPS, min(MAX_FPS, fps))
        self.frame_time = 1.0 / self.target_fps

# 전역 프레임레이트 컨트롤러
_frame_controller = FrameRateController()

def get_terminal_size():
    """터미널 크기를 안전하게 가져옵니다."""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except:
        # 폴백: 기본 크기
        return 80, 24

def calculate_content_lines(content):
    """내용의 줄 수를 계산합니다."""
    if isinstance(content, str):
        return len(content.split('\n'))
    elif isinstance(content, list):
        return len(content)
    else:
        return 1

def align_to_bottom(content, preserve_top_lines=0):
    """
    내용을 터미널 아래쪽으로 정렬합니다.
    
    Args:
        content: 출력할 내용 (문자열 또는 리스트)
        preserve_top_lines: 상단에 보존할 줄 수 (헤더 등)
    
    Returns:
        str: 하단 정렬된 내용
    """
    try:
        cols, lines = get_terminal_size()
        
        # 내용을 리스트로 변환
        if isinstance(content, str):
            content_lines = content.split('\n')
        elif isinstance(content, list):
            content_lines = list(content)
        else:
            content_lines = [str(content)]
        
        content_height = len(content_lines)
        
        # 하단 정렬을 위한 상단 패딩 계산
        available_lines = lines - preserve_top_lines - 2  # 2줄은 입력/여백을 위해 보존
        
        if content_height > available_lines:
            # 내용이 너무 많으면 하단 부분만 잘라내기
            content_lines = content_lines[-available_lines:]
            padding_lines = 0
        else:
            # 하단 정렬을 위한 패딩 계산
            padding_lines = max(0, available_lines - content_height)
        
        # 상단에 빈 줄 추가
        if padding_lines > 0:
            padded_content = [" "] * padding_lines + content_lines
        else:
            padded_content = content_lines
        
        return '\n'.join(padded_content)
        
    except Exception:
        # 오류 시 원본 반환
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return '\n'.join(content)
        else:
            return str(content)

def force_clear_screen():
    """
    부드럽고 안정적인 화면 클리어 - 화면 잘림 방지
    """
    try:
        # 1단계: 최소한의 스크롤로 이전 내용 분리 (화면 잘림 방지)
        print('\n' * 3)  # 40에서 3으로 대폭 감소
        
        # 2단계: 구분선으로 시각적 분리
        print('=' * 70)
        print()
        
    except Exception:
        # 폴백: 최소한의 빈 줄
        print('\n' * 2)  # 30에서 2로 감소

def soft_clear_screen():
    """
    스마트한 화면 클리어 - 터미널 크기에 따라 적응적 스크롤
    """
    try:
        cols, lines = get_terminal_size()
        
        # 터미널 크기에 따른 스마트 스크롤
        if lines <= 20:
            # 작은 터미널 (20줄 이하): 스크롤 없음
            scroll_amount = 0
        elif lines <= 30:
            # 중간 터미널 (21-30줄): 최소 스크롤
            scroll_amount = 2
        elif lines <= 50:
            # 큰 터미널 (31-50줄): 적당한 스크롤
            scroll_amount = 5
        else:
            # 매우 큰 터미널 (50줄 초과): 많은 스크롤
            scroll_amount = 8
        
        if scroll_amount > 0:
            print('\n' * scroll_amount)
            
    except Exception:
        # 폴백: 스크롤 없음
        pass

def minimal_clear():
    """
    최소 클리어 - 터미널 크기 고려한 스마트 클리어
    """
    try:
        cols, lines = get_terminal_size()
        
        # 게임 콘텐츠에 필요한 최소 줄 수
        min_content_lines = 20
        
        if lines < min_content_lines:
            # 터미널이 너무 작으면 아예 스크롤 안함
            pass
        elif lines < 30:
            # 작은 터미널: 1줄만
            print('\n')
        else:
            # 충분한 크기: 2-3줄
            print('\n' * 2)
            
    except Exception:
        pass

def get_frame_controller():
    """프레임레이트 컨트롤러 반환"""
    return _frame_controller

def set_game_fps(fps):
    """게임 FPS 설정 (20-60 범위)"""
    global _frame_controller
    _frame_controller.set_fps(fps)
    print(f"🎮 게임 FPS 설정: {fps} FPS")

def wait_frame():
    """다음 프레임까지 대기 (고성능 게임용)"""
    _frame_controller.wait_for_next_frame()

def high_performance_clear():
    """
    고성능 화면 클리어 - 화면 잘림 방지, 최소 스크롤
    """
    try:
        # 매우 빠른 클리어 - 최소한의 스크롤 (화면 잘림 방지)
        print('\n' * 2)  # 10에서 2로 감소
        print('\033[H', end='', flush=True)  # 커서만 홈으로
    except:
        print('\n' * 1)  # 5에서 1로 감소

def minimal_clear():
    """
    최소한의 화면 클리어 - 화면 잘림 완전 방지
    """
    try:
        # 단순히 구분선만 출력 (스크롤 없음)
        print('\n' + '=' * 70)
    except:
        print('\n' + '-' * 50)

def clear_with_header(title="DAWN OF STELLAR", separator_char="=", width=70):
    """
    화면을 클리어하고 깔끔한 헤더를 표시합니다.
    """
    force_clear_screen()
    
    # 헤더 표시
    print(f"{separator_char * width}")
    if title:
        title_centered = f" {title} ".center(width, separator_char)
        print(title_centered)
        print(f"{separator_char * width}")
    print()

def soft_clear_screen():
    """
    부드러운 화면 클리어 - 깜빡임 없이 내용만 밀어내기
    """
    # 빈 줄로 부드럽게 밀어내기 (깜빡임 없음, 눈 안아픔)
    print('\n' * 30)

def gentle_clear_screen():
    """
    매우 부드러운 화면 클리어 - 최소한의 빈 줄
    """
    # 최소한의 빈 줄로 구분만 하기
    print('\n' * 10)

def prevent_screen_stacking():
    """
    화면 스택킹 방지를 위한 빠른 클리어
    """
    # 짧은 지연으로 이전 출력이 완료되도록 함
    time.sleep(0.01)
    force_clear_screen()

def smart_clear_screen(always_clear=True):
    """
    간단한 화면 클리어 - 복잡한 로직 제거
    """
    if always_clear:
        force_clear_screen()
    else:
        # 클리어하지 않고 그냥 진행
        pass

def clear_and_align_bottom(content, title=None):
    """
    화면을 클리어하고 내용을 하단에 정렬해서 표시합니다.
    """
    force_clear_screen()
    
    # 타이틀이 있으면 상단에 표시
    title_lines = 0
    if title:
        print(f"{'='*70}")
        print(f" {title} ".center(70, '='))
        print(f"{'='*70}")
        print()
        title_lines = 4
    
    # 내용을 하단 정렬
    aligned_content = align_to_bottom(content, preserve_top_lines=title_lines)
    print(aligned_content, end='', flush=True)

def print_bottom_aligned(content, clear_first=True):
    """
    내용을 터미널 하단에 정렬해서 출력합니다.
    
    Args:
        content: 출력할 내용
        clear_first: 먼저 화면을 클리어할지 여부
    """
    if clear_first:
        force_clear_screen()
    
    aligned_content = align_to_bottom(content)
    print(aligned_content)

def show_combat_bottom_aligned(party_info, enemy_info, menu_info, title="전투 화면"):
    """
    전투 화면을 하단 정렬로 표시합니다.
    """
    force_clear_screen()
    
    try:
        cols, lines = get_terminal_size()
        
        # 전체 내용 구성
        content_lines = []
        
        # 타이틀
        content_lines.extend([
            "="*70,
            f"  ⚔️  {title} - 실시간 ATB 시스템  ⚔️".center(70),
            "="*70,
            ""
        ])
        
        # 파티 정보
        content_lines.extend([
            "🛡️ 아군 파티 상태",
            "-"*70
        ])
        content_lines.extend(party_info)
        content_lines.append("")
        
        # 적군 정보
        content_lines.extend([
            "⚔️ 적군 상태", 
            "-"*70
        ])
        content_lines.extend(enemy_info)
        content_lines.append("")
        
        # 메뉴
        content_lines.extend([
            "="*70,
            "📝 행동 선택:"
        ])
        content_lines.extend(menu_info)
        content_lines.extend([
            "="*50,
            ""
        ])
        
        # 내용이 터미널보다 큰 경우 자동으로 잘라내기
        total_content_lines = len(content_lines)
        max_display_lines = lines - 2  # 입력 공간 확보
        
        if total_content_lines > max_display_lines:
            # 내용이 너무 많으면 하단 부분만 표시 (메뉴 우선)
            content_lines = content_lines[-max_display_lines:]
        
        # 하단 정렬을 위한 패딩 계산
        remaining_lines = max_display_lines - len(content_lines)
        if remaining_lines > 0:
            padding = [" "] * remaining_lines
            content_lines = padding + content_lines
        
        # 출력
        for line in content_lines:
            print(line)
            
    except Exception as e:
        # 오류 시 기본 출력
        print(f"전투 화면 표시 오류: {e}")
        for line in party_info:
            print(line)
        for line in enemy_info:
            print(line)
        for line in menu_info:
            print(line)
