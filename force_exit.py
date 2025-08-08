#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dawn of Stellar - 강제 종료 유틸리티
게임이 완전히 종료되지 않을 때 사용하는 안전한 종료 처리기
"""

import os
import sys
import signal
import time


def force_exit():
    """강제 종료 처리"""
    try:
        # pygame 정리
        import pygame
        if pygame.get_init():
            pygame.mixer.quit()
            pygame.quit()
    except:
        pass
    
    try:
        # 모든 Python 프로세스 정리
        import psutil
        current_pid = os.getpid()
        parent = psutil.Process(current_pid)
        
        # 자식 프로세스들 종료
        for child in parent.children(recursive=True):
            try:
                child.terminate()
            except:
                pass
        
        # 좀비 프로세스 정리
        try:
            psutil.wait_procs(parent.children(), timeout=3)
        except:
            pass
            
    except ImportError:
        # psutil이 없으면 기본 방법 사용
        pass
    
    # 강제 종료
    try:
        os._exit(0)
    except:
        sys.exit(0)


def safe_cleanup_and_exit():
    """안전한 정리 후 종료"""
    print("\n게임을 정리하고 종료합니다...")
    
    try:
        # 짧은 대기 시간
        time.sleep(1)
    except:
        pass
    
    force_exit()


if __name__ == "__main__":
    # 직접 실행 시 강제 종료
    print("강제 종료 실행...")
    force_exit()
