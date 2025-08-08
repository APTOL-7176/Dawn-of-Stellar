#!/usr/bin/env python3
"""
모바일 게임 어댑터 - Dawn of Stellar을 모바일에서 실행하기 위한 어댑터
실제 게임 로직과 모바일 UI를 연결
"""

import sys
import time
import threading
from io import StringIO
from typing import Optional, List, Callable

class MobileGameAdapter:
    """모바일 게임 어댑터 - 게임과 모바일 UI 연결"""
    
    def __init__(self, mobile_ui=None):
        self.mobile_ui = mobile_ui
        self.game_instance = None
        self.input_queue = []
        self.output_buffer = []
        self.is_running = False
        self.original_stdout = sys.stdout
        self.original_stdin = sys.stdin
        
    def set_mobile_ui(self, mobile_ui):
        """모바일 UI 설정"""
        self.mobile_ui = mobile_ui
        
    def init_game(self):
        """실제 게임 인스턴스 초기화"""
        try:
            # 상위 디렉토리 경로 추가
            import os
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from main import DawnOfStellarGame
            self.game_instance = DawnOfStellarGame()
            
            # 게임에 모바일 어댑터 설정
            self.game_instance.mobile_adapter = self
            
            # 초기화 완료 메시지 제거 (무한 재귀 방지)
            return True
            
        except Exception as e:
            error_msg = f"❌ 웹 어댑터 오류: {e}"
            if hasattr(self, 'add_output'):
                self.add_output(error_msg)
            print(error_msg)
            print("게임을 데모 모드로 시작합니다...")
            return False
            return False
    
    def start_output_capture(self):
        """게임 출력 캡처 시작"""
        sys.stdout = MobileOutputRedirect(self)
        # 캡처 시작 메시지 제거 (무한 재귀 방지)
    
    def stop_output_capture(self):
        """게임 출력 캡처 중지"""
        sys.stdout = self.original_stdout
        # 캡처 중지 메시지 제거 (무한 재귀 방지)
    
    def add_output(self, text: str):
        """게임 출력을 버퍼에 추가"""
        if text and text.strip():  # 빈 텍스트 제외
            # 한글 텍스트 안전 처리
            safe_text = text.strip()
            
            self.output_buffer.append(safe_text)
            # 버퍼 크기 제한
            if len(self.output_buffer) > 100:
                self.output_buffer = self.output_buffer[-50:]
            
            # 모바일 UI 업데이트 (실시간)
            if self.mobile_ui and hasattr(self.mobile_ui, 'add_game_text'):
                self.mobile_ui.add_game_text(safe_text)
            
            # 터미널 출력 제거 (무한 재귀 방지)
    
    def get_recent_output(self, lines: int = 20) -> str:
        """최근 출력 가져오기"""
        return '\n'.join(self.output_buffer[-lines:])
    
    def add_input(self, command: str):
        """모바일 입력을 큐에 추가"""
        self.input_queue.append(command)
        # 입력 큐 추가 메시지 제거 (무한 재귀 방지)
    
    def get_input(self) -> Optional[str]:
        """입력 큐에서 명령 가져오기"""
        if self.input_queue:
            command = self.input_queue.pop(0)
            # 입력 전달 로그 제거 (무한 재귀 방지)
            return command
        return None
    
    def wait_for_input(self, timeout: float = 0.1) -> Optional[str]:
        """입력 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.input_queue:
                return self.get_input()
            time.sleep(0.01)
        return None
    
    def start_game_thread(self):
        """별도 스레드에서 게임 실행"""
        if not self.game_instance:
            if not self.init_game():
                return False
        
        self.is_running = True
        game_thread = threading.Thread(target=self._run_game_loop)
        game_thread.daemon = True
        game_thread.start()
        return True
    
    def _run_game_loop(self):
        """게임 루프 실행 (별도 스레드)"""
        try:
            # 게임 루프 시작 로그 제거 (무한 재귀 방지)
            
            # 게임의 키보드 입력을 모바일 입력으로 대체
            self._patch_game_input()
            
            # 게임 메인 루프 실행
            self.game_instance.main_loop()
            
        except Exception as e:
            # 게임 루프 오류 처리 (무한 재귀 방지)
            error_msg = f"❌ 게임 루프 오류: {e}"
            self.add_output(error_msg)
            import traceback
            # traceback 출력 제거 (무한 재귀 방지)
        finally:
            self.is_running = False
            self.add_output("🏁 모바일 게임 루프 종료")
    
    def _patch_game_input(self):
        """게임의 입력 시스템을 모바일 입력으로 패치"""
        try:
            # 게임 인스턴스에 모바일 입력 메서드 추가
            original_input = input if hasattr(__builtins__, 'input') else None
            
            def mobile_input(prompt=""):
                """모바일 입력 함수"""
                if prompt:
                    self.add_output(prompt)
                
                # 입력 대기
                while self.is_running:
                    command = self.wait_for_input(0.1)
                    if command:
                        return command
                    time.sleep(0.05)
                return ""
            
            # 전역 input 함수 교체
            __builtins__['input'] = mobile_input
            
            # 게임 클래스의 입력 메서드들 패치
            if hasattr(self.game_instance, 'get_user_input'):
                original_get_input = self.game_instance.get_user_input
                
                def mobile_get_input(prompt="", valid_choices=None):
                    """모바일 사용자 입력"""
                    if prompt:
                        self.add_output(prompt)
                    
                    while self.is_running:
                        command = self.wait_for_input(0.1)
                        if command:
                            if valid_choices is None or command in valid_choices:
                                return command
                            else:
                                self.add_output(f"잘못된 입력: {command}. 다시 시도하세요.")
                        time.sleep(0.05)
                    return ""
                
                self.game_instance.get_user_input = mobile_get_input
                
        except Exception as e:
            # 입력 패치 실패 처리 (무한 재귀 방지)
            error_msg = f"⚠️ 입력 패치 실패: {e}"
            if hasattr(self, 'add_output'):
                self.add_output(error_msg)
    
    def stop_game(self):
        """게임 중지"""
        self.is_running = False
        if hasattr(self, 'add_output'):
            self.add_output("🛑 모바일 게임 중지")

class MobileOutputRedirect:
    """모바일 출력 리다이렉터"""
    
    def __init__(self, adapter: MobileGameAdapter):
        self.adapter = adapter
        self.original_stdout = sys.stdout
        
    def write(self, text: str):
        """텍스트 출력"""
        # 모바일 어댑터로만 전달 (무한 재귀 방지)
        if self.adapter:
            self.adapter.add_output(text)
        
        # 원본 출력 제거 (무한 재귀 방지)
    
    def flush(self):
        """플러시"""
        if hasattr(self.original_stdout, 'flush'):
            self.original_stdout.flush()

class MobileInputHandler:
    """모바일 입력 핸들러"""
    
    def __init__(self, adapter: MobileGameAdapter):
        self.adapter = adapter
    
    def readline(self):
        """한 줄 읽기"""
        while True:
            command = self.adapter.get_input()
            if command:
                return command + '\n'
            time.sleep(0.05)
    
    def read(self, size=-1):
        """읽기"""
        command = self.adapter.get_input()
        return command if command else ""

# 키 매핑 - 모바일 버튼을 게임 키로 변환
MOBILE_KEY_MAPPING = {
    # 방향키
    'w': 'w',        # 위
    's': 's',        # 아래  
    'a': 'a',        # 왼쪽
    'd': 'd',        # 오른쪽
    
    # 액션 버튼
    'enter': '\n',   # 확인 (엔터)
    'q': 'q',        # 취소/뒤로가기
    'i': 'i',        # 인벤토리
    'p': 'p',        # 파티
    
    # 메뉴 버튼
    'ctrl+s': 'b',   # 저장 (B키로 수정)
    'm': 'm',        # 설정
    'h': 'h',        # 도움말
    'ctrl+q': 'q',   # 종료 (단축키를 'q'로)
}

def convert_mobile_input(mobile_command: str) -> str:
    """모바일 입력을 게임 입력으로 변환"""
    return MOBILE_KEY_MAPPING.get(mobile_command, mobile_command)

if __name__ == "__main__":
    # 테스트 코드의 출력 제거 (무한 재귀 방지)
    adapter = MobileGameAdapter()
    if adapter.init_game():
        # 초기화 성공 로그 제거
        adapter.start_output_capture()
        # 캡처 시작 로그 제거
    else:
        # 초기화 실패 로그 제거
        pass
