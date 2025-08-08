#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dawn of Stellar - GUI 런처 (tkinter 기반)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

class DawnOfStellarLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dawn of Stellar - 게임 런처")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 아이콘 설정 (있다면)
        try:
            self.root.iconbitmap("dos.ico")
        except:
            pass
        
        # 게임 폰트 확인 및 로드
        self.check_game_fonts()
        
        self.setup_ui()
    
    def check_game_fonts(self):
        """게임 폰트 파일 존재 확인"""
        current_dir = Path(__file__).parent
        self.whitrabt_exists = (current_dir / 'whitrabt.ttf').exists()
        self.galmuri_exists = (current_dir / 'Galmuri11.ttf').exists()
        
        if not (self.whitrabt_exists or self.galmuri_exists):
            # 폰트가 없으면 기본 폰트 사용 안내
            self.game_font_family = ("맑은 고딕", "Consolas", "Arial")
        else:
            # 게임 폰트 사용
            fonts = []
            if self.whitrabt_exists:
                fonts.append("whitrabt")
            if self.galmuri_exists:
                fonts.append("Galmuri11")
            fonts.extend(["맑은 고딕", "Consolas", "Arial"])
            self.game_font_family = tuple(fonts)
        
    def setup_ui(self):
        """UI 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목 - 게임 스타일 폰트
        title_label = ttk.Label(main_frame, text="🌟 Dawn of Stellar 🌟", 
                               font=(self.game_font_family, 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # 부제목 - 게임 스타일 폰트
        subtitle_label = ttk.Label(main_frame, text="로그라이크 RPG 게임", 
                                  font=(self.game_font_family, 10))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # 폰트 상태 표시
        font_status = "게임 폰트 사용" if (self.whitrabt_exists or self.galmuri_exists) else "기본 폰트 사용"
        font_label = ttk.Label(main_frame, text=f"폰트: {font_status}", 
                              font=(self.game_font_family, 8), foreground="blue")
        font_label.grid(row=1, column=0, columnspan=2, pady=(5, 25))
        
        # 버튼들
        buttons = [
            ("🎮 게임 시작", self.start_game),
            ("📱 모바일 앱", self.start_mobile),
            ("🌐 웹 앱", self.start_web),
            ("⚙️ 설정", self.open_settings),
            ("❌ 종료", self.quit_app)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(main_frame, text=text, command=command,
                           width=20, style="Custom.TButton")
            btn.grid(row=3+i, column=0, columnspan=2, pady=5, padx=10, sticky="ew")
        
        # 상태 표시 - 게임 스타일 폰트
        self.status_var = tk.StringVar(value="준비됨")
        status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                font=(self.game_font_family, 9), foreground="gray")
        status_label.grid(row=9, column=0, columnspan=2, pady=20)
        
        # 스타일 설정 - 게임 폰트 적용
        style = ttk.Style()
        style.configure("Custom.TButton", font=(self.game_font_family, 10))
        
    def get_python_exe(self):
        """Python 실행파일 경로 찾기"""
        # 가상환경 확인
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            return sys.executable
        
        # .venv 폴더 확인
        venv_python = os.path.join('.venv', 'Scripts', 'python.exe')
        if os.path.exists(venv_python):
            return os.path.abspath(venv_python)
        
        return 'python'
    
    def start_game(self):
        """게임 시작"""
        self.status_var.set("게임을 시작하는 중...")
        
        def run_game():
            try:
                python_exe = self.get_python_exe()
                
                # 환경 변수 설정
                env = os.environ.copy()
                env['DISABLE_GAMEPAD'] = '1'
                env['TERMINAL_MODE'] = '1'
                
                # 새 콘솔 창에서 게임 실행
                subprocess.Popen([
                    'cmd', '/c', 'start', 'cmd', '/k', 
                    f'cd /d "{os.getcwd()}" && "{python_exe}" main.py'
                ], env=env)
                
                # 런처 종료
                self.root.after(2000, self.quit_app)
                self.status_var.set("게임이 시작되었습니다. 런처를 종료합니다.")
                
            except Exception as e:
                messagebox.showerror("오류", f"게임 시작 실패: {e}")
                self.status_var.set("게임 시작 실패")
        
        threading.Thread(target=run_game, daemon=True).start()
    
    def start_mobile(self):
        """모바일 앱 시작"""
        self.status_var.set("모바일 앱 준비 중...")
        messagebox.showinfo("정보", "모바일 앱 기능은 준비 중입니다.")
        self.status_var.set("준비됨")
    
    def start_web(self):
        """웹 앱 시작"""
        self.status_var.set("웹 앱 준비 중...")
        messagebox.showinfo("정보", "웹 앱 기능은 준비 중입니다.")
        self.status_var.set("준비됨")
    
    def open_settings(self):
        """설정 열기"""
        messagebox.showinfo("설정", "설정 기능은 준비 중입니다.")
    
    def quit_app(self):
        """앱 종료"""
        self.root.quit()
    
    def run(self):
        """런처 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    launcher = DawnOfStellarLauncher()
    launcher.run()
