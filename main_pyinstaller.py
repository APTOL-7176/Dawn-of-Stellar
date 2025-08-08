#!/usr/bin/env python3
"""
Dawn Of Stellar - PyInstaller 호환 메인 파일 (Windowed 모드 대응 + 로깅)
"""

import sys
import os
import traceback
import datetime

# Windowed 모드 대응: stdout/stderr 리다이렉션 + 로깅
def setup_windowed_mode():
    """Windowed 모드에서 입출력 시스템 설정 + 로그                     # 시작 화면 그리기 (간단한 텍스트만 사용)
                    try:
                        title_text = korean_font.render("던 오브 스텔라", True, (255, 255, 255))
                        title_rect = title_text.get_rect(center=(width//2, height//2 - 50))
                        screen.blit(title_text, title_rect)
                        
                        loading_text = korean_font.render("게임 시작 중...", True, (200, 200, 200))
                        loading_rect = loading_text.get_rect(center=(width//2, height//2 + 20))
                        screen.blit(loading_text, loading_rect)
                        
                        auto_text = english_font.render("Starting automatically...", True, (150, 150, 150))
                        auto_rect = auto_text.get_rect(center=(width//2, height//2 + 60))
                        screen.blit(auto_text, auto_rect)
                        
                        # ESC 키 안내
                        esc_text = english_font.render("Press ESC to exit fullscreen", True, (100, 100, 100))
                        esc_rect = esc_text.get_rect(center=(width//2, height - 50))
                        screen.blit(esc_text, esc_rect)
                        
                    except Exception as e:
                        safe_print(f"  - 텍스트 렌더링 실패: {e}")
                        # 폰트 로딩 실패 시 기본 메시지
                        try:
                            default_font = pygame.font.Font(None, 48)
                            fallback_text = default_font.render("Dawn of Stellar", True, (255, 255, 255))
                            fallback_rect = fallback_text.get_rect(center=(width//2, height//2))
                            screen.blit(fallback_text, fallback_rect)
                        except:
                            pass  
    # 로그 파일 설정
    log_file = "game_debug.log"
    error_file = "game_error.log"
    
    try:
        # 기존 로그 파일 백업 (너무 커지면)
        if os.path.exists(log_file) and os.path.getsize(log_file) > 1024*1024:  # 1MB 초과시
            os.rename(log_file, f"game_debug_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # 로그 파일 열기
        log_handle = open(log_file, 'a', encoding='utf-8')
        error_handle = open(error_file, 'a', encoding='utf-8')
        
        # 시작 로그 작성
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_handle.write(f"\n{'='*50}\n")
        log_handle.write(f"Dawn of Stellar 시작: {timestamp}\n")
        log_handle.write(f"PyInstaller 모드: {getattr(sys, 'frozen', False)}\n")
        log_handle.write(f"실행 경로: {os.getcwd()}\n")
        log_handle.write(f"{'='*50}\n")
        log_handle.flush()
        
        if getattr(sys, 'frozen', False):  # PyInstaller로 빌드된 경우
            # Windowed 모드에서 stdout/stderr가 None일 수 있음
            if sys.stdout is None:
                sys.stdout = log_handle
            if sys.stderr is None:
                sys.stderr = error_handle
            if sys.stdin is None:
                # stdin 대체 (키보드 입력용)
                import io
                sys.stdin = io.StringIO()
                
        return log_handle, error_handle
        
    except Exception as e:
        # 로그 설정 실패해도 게임 실행 계속
        return None, None

def safe_input(prompt="", timeout=None):
    """안전한 입력 함수 (windowed 모드 대응)"""
    try:
        if hasattr(sys, 'stdin') and sys.stdin and not getattr(sys, 'frozen', False):
            return input(prompt)
        else:
            # Windowed 모드에서는 파일로 입력 받기
            safe_print(f"{prompt}(자동 진행)")
            return ""
    except:
        return ""

def safe_print(*args, **kwargs):
    """안전한 출력 함수"""
    try:
        print(*args, **kwargs)
        if hasattr(sys.stdout, 'flush'):
            sys.stdout.flush()
    except:
        pass

def log_error(error_msg, exception=None):
    """오류 로깅 함수"""
    try:
        with open("game_error.log", "a", encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n[ERROR {timestamp}] {error_msg}\n")
            if exception:
                f.write(f"Exception: {str(exception)}\n")
                f.write(f"Traceback:\n{traceback.format_exc()}\n")
            f.write("-" * 50 + "\n")
    except:
        pass

def main():
    """메인 함수 - 단계별 디버깅 및 로깅"""
    log_handle = None
    error_handle = None
    
    try:
        # 1. Windowed 모드 설정 및 로깅 시작
        log_handle, error_handle = setup_windowed_mode()
        safe_print("=== Dawn of Stellar 게임 시작 ===")
        
        # 2. 시스템 정보 로깅
        safe_print(f"Python 버전: {sys.version}")
        safe_print(f"PyInstaller 모드: {getattr(sys, 'frozen', False)}")
        safe_print(f"현재 디렉토리: {os.getcwd()}")
        
        # 3. 단계별 모듈 임포트 (각 단계마다 로깅)
        safe_print("\n--- 모듈 임포트 단계 ---")
        
        try:
            safe_print("1/5: main 모듈 임포트 중...")
            from main import DawnOfStellarGame
            safe_print("✓ main.DawnOfStellarGame 임포트 성공")
        except Exception as e:
            error_msg = f"main 모듈 임포트 실패: {e}"
            safe_print(f"✗ {error_msg}")
            log_error(error_msg, e)
            raise
        
        try:
            safe_print("2/5: 게임 인스턴스 생성 중...")
            game = DawnOfStellarGame()
            safe_print("✓ 게임 인스턴스 생성 성공")
        except Exception as e:
            error_msg = f"게임 인스턴스 생성 실패: {e}"
            safe_print(f"✗ {error_msg}")
            log_error(error_msg, e)
            raise
        
        try:
            safe_print("3/5: 게임 속성 검증 중...")
            if not hasattr(game, 'running'):
                game.running = True
                safe_print("  - running 속성 초기화")
            
            # game_manager 속성 초기화 (main.py에서 참조하므로 필수)
            if not hasattr(game, 'game_manager'):
                try:
                    from game.integrated_game_manager import IntegratedGameManager
                    game.game_manager = IntegratedGameManager()
                    safe_print("  - game_manager 속성 초기화 성공")
                except Exception as e:
                    game.game_manager = None
                    safe_print(f"  - game_manager 초기화 실패, None으로 설정: {e}")
            
            # keyboard 속성 초기화 (main.py에서 참조하므로 필수)
            if not hasattr(game, 'keyboard'):
                try:
                    from game.input_utils import UnifiedInputManager
                    game.keyboard = UnifiedInputManager()
                    safe_print("  - keyboard 속성 초기화 성공")
                except Exception as e:
                    # 폴백 keyboard 객체 생성
                    class FallbackKeyboard:
                        def get_key(self): return None
                        def is_key_pressed(self, key): return False
                    game.keyboard = FallbackKeyboard()
                    safe_print(f"  - keyboard 초기화 실패, 폴백 객체로 설정: {e}")
            
            # story_system 속성 초기화
            if not hasattr(game, 'story_system'):
                try:
                    from story_system import StorySystem
                    game.story_system = StorySystem()
                    safe_print("  - story_system 속성 초기화 성공")
                except Exception as e:
                    game.story_system = None
                    safe_print(f"  - story_system 초기화 실패, None으로 설정: {e}")
            
            # PyInstaller 모드에서 "Press ANY KEY" 단계만 건너뛰기 (오프닝은 유지)
            if getattr(sys, 'frozen', False):
                # 게임 준비 상태를 강제로 True로 설정
                if hasattr(game, 'game_ready'):
                    game.game_ready = True
                    safe_print("  - 게임 준비 상태 강제 설정")
                
                # "Press ANY KEY" 단계 건너뛰기 (오프닝 스토리는 유지)
                if hasattr(game, 'skip_press_key'):
                    game.skip_press_key = True
                    safe_print("  - Press ANY KEY 단계 건너뛰기 설정")
            
            if not hasattr(game, 'main_loop'):
                raise AttributeError("main_loop 메서드가 없습니다")
            
            safe_print("✓ 게임 속성 검증 완료")
        except Exception as e:
            error_msg = f"게임 속성 검증 실패: {e}"
            safe_print(f"✗ {error_msg}")
            log_error(error_msg, e)
            raise
        
        try:
            safe_print("4/5: 오디오 시스템 초기화 중...")
            import pygame
            if not pygame.get_init():
                pygame.init()
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            safe_print("✓ 오디오 시스템 초기화 완료")
        except Exception as e:
            error_msg = f"오디오 시스템 초기화 실패: {e}"
            safe_print(f"⚠ {error_msg} (계속 진행)")
            log_error(error_msg, e)
        
        # 4. 게임 실행
        safe_print("\n--- 게임 실행 단계 ---")
        try:
            safe_print("5/5: 게임 메인 루프 시작...")
            
            # Windowed 모드에서 pygame 시스템 완전 초기화
            if getattr(sys, 'frozen', False):  # PyInstaller 빌드된 경우
                try:
                    import pygame
                    
                    # SDL 환경 변수 설정
                    os.environ['SDL_VIDEODRIVER'] = 'windib'
                    os.environ['SDL_AUDIODRIVER'] = 'dsound'
                    
                    # pygame 완전 초기화
                    pygame.init()
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
                    pygame.display.init()
                    pygame.font.init()
                    
                    # 전체화면 모드로 설정
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    pygame.display.set_caption("Dawn of Stellar")
                    width, height = screen.get_size()
                    
                    # 배경 설정
                    screen.fill((0, 0, 0))
                    
                    # 폰트 로딩 (PyInstaller 환경 대응)
                    korean_font = None
                    english_font = None
                    
                    try:
                        # PyInstaller 빌드된 경우 sys._MEIPASS 디렉토리에서 폰트 찾기
                        if getattr(sys, 'frozen', False):
                            # PyInstaller 임시 디렉토리
                            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                            korean_font_path = os.path.join(base_path, "Galmuri11.ttf")
                            english_font_path = os.path.join(base_path, "whitrabt.ttf")
                            safe_print(f"  - PyInstaller 모드: 폰트 경로 = {base_path}")
                        else:
                            # 개발 환경에서는 현재 디렉토리에서 찾기
                            korean_font_path = "Galmuri11.ttf"
                            english_font_path = "whitrabt.ttf"
                        
                        # 한글 폰트 로딩
                        if os.path.exists(korean_font_path):
                            korean_font = pygame.font.Font(korean_font_path, 32)
                            safe_print(f"  - 한글 폰트 로딩 성공: {korean_font_path}")
                        else:
                            korean_font = pygame.font.Font(None, 32)
                            safe_print(f"  - 한글 폰트 파일 없음, 기본 폰트 사용: {korean_font_path}")
                        
                        # 영어 폰트 로딩
                        if os.path.exists(english_font_path):
                            english_font = pygame.font.Font(english_font_path, 24)
                            safe_print(f"  - 영어 폰트 로딩 성공: {english_font_path}")
                        else:
                            english_font = pygame.font.Font(None, 24)
                            safe_print(f"  - 영어 폰트 파일 없음, 기본 폰트 사용: {english_font_path}")
                            
                    except Exception as e:
                        safe_print(f"  - 폰트 로딩 오류: {e}")
                        korean_font = pygame.font.Font(None, 32)
                        english_font = pygame.font.Font(None, 24)
                        safe_print("  - 모든 폰트를 기본 폰트로 대체")
                    
                    # 시작 화면 그리기 (색상 코드 및 특수문자 제거)
                    title_text = korean_font.render("던 오브 스텔라", True, (255, 255, 255))
                    title_rect = title_text.get_rect(center=(width//2, height//2 - 80))
                    screen.blit(title_text, title_rect)
                    
                    loading_text = korean_font.render("게임 시작 중...", True, (200, 200, 200))
                    loading_rect = loading_text.get_rect(center=(width//2, height//2))
                    screen.blit(loading_text, loading_rect)
                    
                    auto_text = english_font.render("Starting automatically...", True, (150, 150, 150))
                    auto_rect = auto_text.get_rect(center=(width//2, height//2 + 80))
                    screen.blit(auto_text, auto_rect)
                    
                    esc_text = english_font.render("Press ESC to exit fullscreen", True, (100, 100, 100))
                    esc_rect = esc_text.get_rect(center=(width//2, height//2 + 120))
                    screen.blit(esc_text, esc_rect)
                    
                    pygame.display.flip()
                    
                    # 이벤트 처리 시스템 활성화
                    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.JOYBUTTONDOWN])
                    
                    # 짧은 대기 후 바로 게임 시작 (키 입력 대기 제거)
                    import time
                    time.sleep(0.5)  # 0.5초만 대기
                    
                    safe_print("  - pygame 시스템 완전 초기화 완료")
                    safe_print("  - 게임 창이 표시되었습니다!")
                    safe_print("  - 자동 게임 시작 중...")
                    
                except Exception as e:
                    safe_print(f"  - pygame 초기화 실패: {e}")
            
            game.main_loop()
            safe_print("✓ 게임 정상 종료")
            
        except KeyboardInterrupt:
            safe_print("사용자에 의한 게임 중단 (Ctrl+C)")
            
        except Exception as e:
            error_msg = f"게임 실행 중 오류: {e}"
            safe_print(f"✗ {error_msg}")
            log_error(error_msg, e)
            raise
            
    except Exception as e:
        error_msg = f"치명적 오류: {e}"
        safe_print(f"\n{error_msg}")
        log_error(error_msg, e)
        
        # 에러 발생 시 창이 바로 닫히지 않도록 처리
        if getattr(sys, 'frozen', False):  # PyInstaller 빌드된 경우
            try:
                import tkinter as tk
                from tkinter import messagebox, simpledialog
                
                # 메인 윈도우 생성 (숨기지 않음)
                root = tk.Tk()
                root.title("Dawn of Stellar - 오류 발생")
                root.geometry("500x300")
                root.resizable(False, False)
                
                # 에러 메시지를 텍스트 위젯에 표시
                import tkinter.scrolledtext as scrolledtext
                text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15)
                text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                
                # 에러 정보 텍스트 작성
                error_text = f"""Dawn of Stellar 실행 중 오류가 발생했습니다.

오류 내용:
{error_msg}

상세 오류 정보:
{traceback.format_exc()}

해결 방법:
1. game_error.log 파일을 확인하세요
2. 게임 파일이 모두 있는지 확인하세요
3. 문제가 지속되면 개발자에게 문의하세요

이 창을 닫으면 게임이 종료됩니다."""
                
                text_widget.insert(tk.END, error_text)
                text_widget.config(state=tk.DISABLED)
                
                # 닫기 버튼
                def close_app():
                    root.destroy()
                
                close_button = tk.Button(root, text="확인 (게임 종료)", command=close_app, 
                                       font=("맑은 고딕", 12), bg="#ff6b6b", fg="white")
                close_button.pack(pady=10)
                
                # 창을 화면 중앙에 배치
                root.update_idletasks()
                x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
                y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
                root.geometry(f"+{x}+{y}")
                
                # 항상 위에 표시
                root.attributes('-topmost', True)
                
                # 메인 루프 실행 (사용자가 창을 닫을 때까지 대기)
                root.mainloop()
                
            except Exception as tk_error:
                # tkinter도 실패한 경우 콘솔에 출력하고 긴 대기
                safe_print(f"GUI 오류 표시 실패: {tk_error}")
                safe_print(f"\n{'='*50}")
                safe_print(f"Dawn of Stellar 실행 오류")
                safe_print(f"{'='*50}")
                safe_print(f"오류 내용: {error_msg}")
                safe_print(f"상세 로그: game_error.log 파일 확인")
                safe_print(f"{'='*50}")
                safe_print("30초 후 자동 종료됩니다...")
                
                import time
                for i in range(30, 0, -1):
                    safe_print(f"남은 시간: {i}초")
                    time.sleep(1)
        else:
            # Console 모드에서는 입력 대기
            safe_print(f"\n{'='*50}")
            safe_print(f"Dawn of Stellar 실행 오류")
            safe_print(f"{'='*50}")
            safe_print(f"오류 내용: {error_msg}")
            safe_print(f"상세 로그: game_error.log 파일 확인")
            safe_print(f"{'='*50}")
            try:
                safe_input("\n엔터를 누르면 종료합니다...")
            except:
                import time
                safe_print("10초 후 자동 종료됩니다...")
                time.sleep(10)
        
        return 1
        
    finally:
        # 정리 작업
        try:
            import pygame
            if pygame.get_init():
                pygame.mixer.quit()
                pygame.quit()
        except:
            pass
            
        try:
            if log_handle and log_handle != sys.stdout:
                log_handle.close()
            if error_handle and error_handle != sys.stderr:
                error_handle.close()
        except:
            pass
    
    return 0

if __name__ == "__main__":
    main()
