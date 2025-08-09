#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
핫 리로드 매니저 - 게임 실행 중 파일 변경사항 자동 반영
게임 도중 파일이 업데이트되면 업데이트된 버전으로 계속 플레이 및 디버깅 가능
"""

import os
import sys
import time
import importlib
import threading
from typing import Dict, Set, Any
from pathlib import Path
from game.error_logger import logger

class HotReloadManager:
    """게임 실행 중 모듈 핫 리로드 관리"""
    
    def __init__(self, watch_directories: list = None):
        self.watch_directories = watch_directories or ['game', '.']
        self.file_timestamps: Dict[str, float] = {}
        self.loaded_modules: Set[str] = set()
        self.reload_callbacks: Dict[str, callable] = {}
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 리로드 제외 파일들 (너무 민감한 파일들)
        self.exclude_files = {
            '__pycache__',
            '.pyc',
            '.pyo',
            '.git',
            'save_data',
            'logs',
            '.venv'
        }
        
        logger.log_system_info("핫리로드", "핫 리로드 매니저 초기화", {
            "감시디렉토리": self.watch_directories
        })
    
    def start_monitoring(self):
        """파일 모니터링 시작"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.log_system_info("핫리로드", "파일 모니터링 시작", {})
        print("🔥 핫 리로드 활성화: 파일 변경 시 자동 업데이트!")
    
    def stop_monitoring(self):
        """파일 모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        logger.log_system_info("핫리로드", "파일 모니터링 중지", {})
        print("🔥 핫 리로드 비활성화")
    
    def _monitor_loop(self):
        """파일 변경 모니터링 루프"""
        self._scan_initial_files()
        
        while self.is_monitoring:
            try:
                self._check_file_changes()
                time.sleep(1.0)  # 1초마다 체크
            except Exception as e:
                logger.log_error("핫리로드", f"모니터링 오류: {e}", {})
                time.sleep(5.0)  # 오류 시 5초 대기
    
    def _scan_initial_files(self):
        """초기 파일 스캔"""
        for directory in self.watch_directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    # 제외 디렉토리 건너뛰기
                    dirs[:] = [d for d in dirs if not any(ex in d for ex in self.exclude_files)]
                    
                    for file in files:
                        if file.endswith('.py') and not any(ex in file for ex in self.exclude_files):
                            file_path = os.path.join(root, file)
                            try:
                                self.file_timestamps[file_path] = os.path.getmtime(file_path)
                            except OSError:
                                continue
        
        logger.log_debug("핫리로드", f"초기 파일 스캔 완료", {
            "파일수": len(self.file_timestamps)
        })
    
    def _check_file_changes(self):
        """파일 변경사항 체크"""
        changed_files = []
        
        # 기존 파일들 체크
        for file_path, old_timestamp in list(self.file_timestamps.items()):
            try:
                if os.path.exists(file_path):
                    new_timestamp = os.path.getmtime(file_path)
                    if new_timestamp > old_timestamp:
                        changed_files.append(file_path)
                        self.file_timestamps[file_path] = new_timestamp
                else:
                    # 파일이 삭제됨
                    del self.file_timestamps[file_path]
                    logger.log_debug("핫리로드", f"파일 삭제 감지", {"파일": file_path})
            except OSError:
                continue
        
        # 새 파일들 체크
        for directory in self.watch_directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    dirs[:] = [d for d in dirs if not any(ex in d for ex in self.exclude_files)]
                    
                    for file in files:
                        if file.endswith('.py') and not any(ex in file for ex in self.exclude_files):
                            file_path = os.path.join(root, file)
                            if file_path not in self.file_timestamps:
                                try:
                                    self.file_timestamps[file_path] = os.path.getmtime(file_path)
                                    changed_files.append(file_path)
                                    logger.log_debug("핫리로드", f"새 파일 감지", {"파일": file_path})
                                except OSError:
                                    continue
        
        # 변경된 파일들 리로드
        for file_path in changed_files:
            self._reload_file(file_path)
    
    def _reload_file(self, file_path: str):
        """특정 파일 리로드"""
        try:
            # 파일 경로를 모듈명으로 변환
            relative_path = os.path.relpath(file_path, '.')
            module_path = relative_path.replace(os.sep, '.').replace('.py', '')
            
            logger.log_system_info("핫리로드", f"파일 변경 감지", {
                "파일": file_path,
                "모듈": module_path
            })
            
            # 모듈이 이미 로드되어 있다면 리로드
            if module_path in sys.modules:
                print(f"🔄 리로드: {module_path}")
                
                try:
                    importlib.reload(sys.modules[module_path])
                    logger.log_system_info("핫리로드", f"모듈 리로드 성공", {
                        "모듈": module_path
                    })
                    
                    # 리로드 콜백 실행
                    if module_path in self.reload_callbacks:
                        self.reload_callbacks[module_path]()
                        
                    print(f"✅ {module_path} 업데이트 완료!")
                    
                except Exception as e:
                    logger.log_error("핫리로드", f"모듈 리로드 실패: {e}", {
                        "모듈": module_path,
                        "오류": str(e)
                    })
                    print(f"❌ {module_path} 리로드 실패: {e}")
            else:
                logger.log_debug("핫리로드", f"새 모듈 감지", {"모듈": module_path})
                print(f"📦 새 모듈: {module_path}")
                
        except Exception as e:
            logger.log_error("핫리로드", f"파일 처리 오류: {e}", {
                "파일": file_path,
                "오류": str(e)
            })
    
    def register_reload_callback(self, module_name: str, callback: callable):
        """모듈 리로드 시 실행할 콜백 등록"""
        self.reload_callbacks[module_name] = callback
        logger.log_debug("핫리로드", f"콜백 등록", {
            "모듈": module_name,
            "콜백": callback.__name__
        })
    
    def force_reload_module(self, module_name: str):
        """특정 모듈 강제 리로드"""
        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                logger.log_system_info("핫리로드", f"강제 리로드 성공", {
                    "모듈": module_name
                })
                print(f"🔄 강제 리로드: {module_name}")
                
                if module_name in self.reload_callbacks:
                    self.reload_callbacks[module_name]()
                    
                return True
            else:
                logger.log_system_warning("핫리로드", f"모듈을 찾을 수 없음", {
                    "모듈": module_name
                })
                return False
                
        except Exception as e:
            logger.log_error("핫리로드", f"강제 리로드 실패: {e}", {
                "모듈": module_name,
                "오류": str(e)
            })
            print(f"❌ 강제 리로드 실패: {e}")
            return False

# 전역 핫 리로드 매니저 인스턴스
hot_reload_manager = HotReloadManager()

# 핫 리로드 가용성 플래그
HOT_RELOAD_AVAILABLE = True

def enable_hot_reload():
    """핫 리로드 활성화"""
    hot_reload_manager.start_monitoring()

def disable_hot_reload():
    """핫 리로드 비활성화"""
    hot_reload_manager.stop_monitoring()

def reload_module(module_name: str):
    """특정 모듈 강제 리로드"""
    return hot_reload_manager.force_reload_module(module_name)

def register_reload_callback(module_name: str, callback: callable):
    """리로드 콜백 등록"""
    hot_reload_manager.register_reload_callback(module_name, callback)

if __name__ == "__main__":
    # 테스트 코드
    print("🔥 핫 리로드 매니저 테스트")
    enable_hot_reload()
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🔥 핫 리로드 중지")
        disable_hot_reload()
