"""
안정적인 화면 표시 시스템 - 깜빡임 방지
"""
import os
import time
from typing import Dict, Any

class StableDisplay:
    """화면 깜빡임을 방지하는 안정적인 표시 시스템"""
    
    def __init__(self):
        self.last_frame = ""
        self.frame_buffer = []
        self.stable_lines = {}  # 라인별 안정화 버퍼
        self.update_threshold = 0.05  # 50ms 이하의 업데이트는 무시
        self.last_update_time = 0
        
    def should_update(self) -> bool:
        """업데이트가 필요한지 확인"""
        current_time = time.time()
        if current_time - self.last_update_time < self.update_threshold:
            return False
        return True
        
    def add_stable_line(self, line_id: str, content: str):
        """안정화된 라인 추가"""
        self.stable_lines[line_id] = content
        
    def get_stable_frame(self) -> str:
        """안정화된 프레임 생성"""
        if not self.stable_lines:
            return ""
            
        # 라인들을 ID 순으로 정렬하여 표시
        sorted_lines = sorted(self.stable_lines.items())
        frame = "\n".join([content for _, content in sorted_lines])
        return frame
        
    def clear_and_display(self, force_update: bool = False):
        """화면을 지우고 안정화된 내용 표시"""
        if not force_update and not self.should_update():
            return
            
        current_frame = self.get_stable_frame()
        
        # 이전 프레임과 동일하면 스킵
        if current_frame == self.last_frame:
            return
            
        # 화면 지우기 (Windows용)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 내용 출력
        print(current_frame, end='', flush=True)
        
        # 상태 업데이트
        self.last_frame = current_frame
        self.last_update_time = time.time()
        
    def force_refresh(self):
        """강제 새로고침"""
        self.last_frame = ""
        self.clear_and_display(force_update=True)
        
# 전역 인스턴스
stable_display = StableDisplay()
