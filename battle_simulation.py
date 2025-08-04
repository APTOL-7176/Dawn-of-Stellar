#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 전투 상황 시뮬레이션 - ATB 애니메이션 포함
"""
import time
import os
import random

class Color:
    RESET = '\033[0m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_WHITE = '\033[97m'
    BRIGHT_CYAN = '\033[96m'
    WHITE = '\033[37m'
    BRIGHT_GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED = '\033[91m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'  # 누락된 색상 추가
    BRIGHT_MAGENTA = '\033[95m'
    GREEN = '\033[32m'
    BRIGHT_BLACK = '\033[90m'

class Character:
    def __init__(self, name, hp, max_hp, mp, max_mp, brv, max_brv, speed, char_class, icon):
        self.name = name
        self.current_hp = hp
        self.max_hp = max_hp
        self.current_mp = mp
        self.max_mp = max_mp
        self.brave_points = brv
        self.max_brv = max_brv
        self.speed = speed
        self.character_class = char_class
        self.icon = icon
        self.atb_gauge = random.randint(3000, 7000)  # 30-70% 시작
        self.is_casting = False
        self.casting_skill_name = ""
        self.is_alive = True
        self.level = random.randint(12, 16)

class BattleSimulator:
    def __init__(self):
        self.ATB_READY_THRESHOLD = 10000
        self.ATB_DISPLAY_SCALE = 100
        
        # 아군 파티
        self.party = [
            Character("코딘", 850, 850, 320, 320, 1250, 1250, 85, "Archer", "🏹"),
            Character("레이나", 420, 680, 180, 280, 800, 1200, 65, "Guardian", "🛡️"),
            Character("마르쿠스", 280, 750, 420, 450, 950, 1100, 72, "Warrior", "⚔️")
        ]
        
        # 적군
        self.enemies = [
            Character("오크 전사", 450, 450, 0, 0, 600, 800, 45, "Enemy", "⚔️"),
            Character("다크 메이지", 320, 520, 0, 0, 250, 600, 58, "Enemy", "⚔️")
        ]
        
        # 마르쿠스 캐스팅 상태로 설정
        self.party[2].is_casting = True
        self.party[2].casting_skill_name = "파이어볼"
        
        # 다크 메이지도 캐스팅 상태로 설정
        self.enemies[1].is_casting = True
        self.enemies[1].casting_skill_name = "다크 볼트"
        
        # 코딘을 MAX BRV 상태로 설정 (마젠타 색상 테스트)
        self.party[0].brave_points = self.party[0].max_brv
        
        self.current_turn_char = None
    
    def create_atb_bar(self, atb_gauge: int, character=None) -> tuple:
        """ATB 게이지 바와 표시 텍스트 생성"""
        display_atb = atb_gauge // self.ATB_DISPLAY_SCALE
        filled = int(min(10, max(0, display_atb // 10)))
        empty = int(10 - filled)
        
        # 캐릭터 상태에 따른 색상 결정
        if character and character.is_casting:
            bar_color = Color.BRIGHT_MAGENTA
            display_text = f"{Color.BRIGHT_MAGENTA}🔮{display_atb}%{Color.RESET}"
        elif atb_gauge >= self.ATB_READY_THRESHOLD:
            bar_color = Color.BRIGHT_YELLOW
            display_text = f"{Color.BRIGHT_YELLOW}READY{Color.RESET}"
        else:
            # 진행도에 따른 색상
            if display_atb >= 80:
                bar_color = Color.BRIGHT_CYAN
            elif display_atb >= 60:
                bar_color = Color.CYAN
            elif display_atb >= 40:
                bar_color = Color.BLUE
            else:
                bar_color = Color.BRIGHT_BLUE
            display_text = f"{bar_color}{display_atb}%{Color.RESET}"
        
        # 바 생성
        filled_part = f"{bar_color}{'▰'*filled}{Color.RESET}"
        empty_part = f"{Color.BRIGHT_BLACK}{'▱'*empty}{Color.RESET}"
        bar = f"{filled_part}{empty_part} "
        
        return bar, display_text
    
    def get_hp_color_and_icon(self, character):
        """HP 비율에 따른 색상과 아이콘 반환"""
        hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
        if hp_ratio > 0.7:
            return Color.BRIGHT_GREEN, "💚"
        elif hp_ratio > 0.4:
            return Color.YELLOW, "💛"
        elif hp_ratio > 0.15:
            return Color.BRIGHT_RED, "🧡"
        else:
            return Color.RED, "❤️"
    
    def get_mp_color_and_icon(self, character):
        """MP 비율에 따른 색상과 아이콘 반환"""
        mp_ratio = character.current_mp / character.max_mp if character.max_mp > 0 else 0
        if mp_ratio > 0.5:
            return Color.BRIGHT_GREEN, "💙"  # MP가 충분하면 파란색으로 표시
        elif mp_ratio > 0.2:
            return Color.BLUE, "💙"
        else:
            return Color.BRIGHT_BLACK, "💙"
    
    def get_brv_color(self, character):
        """BRV 상태에 따른 색상 반환"""
        if character.brave_points <= 299:
            return Color.BRIGHT_RED
        elif character.brave_points >= character.max_brv:  # MAX BRV = 현재 BRV일 때 마젠타
            return Color.BRIGHT_MAGENTA
        else:
            return Color.BRIGHT_YELLOW
    
    def is_ally(self, character):
        """캐릭터가 아군인지 확인"""
        return character in self.party
    
    def is_enemy(self, character):
        """캐릭터가 적군인지 확인"""
        return character in self.enemies
    def is_ally(self, character):
        """캐릭터가 아군인지 확인"""
        return character in self.party
    
    def is_enemy(self, character):
        """캐릭터가 적군인지 확인"""
        return character in self.enemies
    
    def get_speed_color(self, speed, avg_speed):
        """속도에 따른 색상 반환"""
        speed_ratio = (speed / avg_speed) if avg_speed > 0 else 1.0
        speed_percent_diff = (speed_ratio - 1.0) * 100
        
        if speed_percent_diff >= 30:
            return Color.BRIGHT_GREEN
        elif speed_percent_diff >= 15:
            return Color.GREEN
        elif speed_percent_diff >= -15:
            return Color.WHITE
        elif speed_percent_diff >= -30:
            return Color.YELLOW
        else:
            return Color.BRIGHT_RED
    
    def display_battle_status(self, clear_screen=True):
        """전투 상태 표시 - 깜빡임 최소화"""
        if clear_screen:
            # 화면 클리어 대신 커서를 맨 위로 이동
            print("\033[H", end="")  # 커서를 (1,1)로 이동
            print("\033[2J", end="")  # 화면 클리어
        else:
            # 커서만 위로 이동 (깜빡임 방지)
            print("\033[H", end="")
        
        # 버퍼에 모든 출력을 저장한 후 한 번에 출력
        output_buffer = []
        
        # 평균 속도 계산
        all_chars = self.party + self.enemies
        alive_chars = [char for char in all_chars if char.is_alive]
        avg_speed = sum(char.speed for char in alive_chars) / len(alive_chars) if alive_chars else 50
        
        # 아군 파티 상태
        output_buffer.append(f"\n{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        output_buffer.append(f"{Color.BRIGHT_WHITE}🛡️  아군 파티 상태{Color.RESET}")
        output_buffer.append(f"{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        
        for member in self.party:
            if member.is_alive:
                # 현재 턴 표시
                if member == self.current_turn_char:
                    name_color = Color.BRIGHT_CYAN
                    status_icon = "▶"
                else:
                    name_color = Color.WHITE
                    status_icon = " "
                
                # 상태 아이콘
                status_icons = ""
                if member.is_casting:
                    status_icons += " 🔮"
                
                # HP/MP 색상과 게이지
                hp_color, hp_icon = self.get_hp_color_and_icon(member)
                mp_color, mp_icon = self.get_mp_color_and_icon(member)
                brv_color = self.get_brv_color(member)
                speed_color = self.get_speed_color(member.speed, avg_speed)
                
                # HP/MP 게이지 생성
                hp_ratio = member.current_hp / member.max_hp
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                
                hp_filled = int(hp_ratio * 10)
                mp_filled = int(mp_ratio * 10)
                
                hp_bar = f"{hp_color}{'▰'*hp_filled}{'▱'*(10-hp_filled)}{Color.RESET}"
                mp_bar = f"{mp_color}{'▰'*mp_filled}{'▱'*(10-mp_filled)}{Color.RESET}"
                
                # ATB 게이지
                atb_bar, atb_display = self.create_atb_bar(member.atb_gauge, member)
                
                # 캐스팅 상태 표시
                casting_status = ""
                if member.is_casting:
                    casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {member.casting_skill_name}]{Color.RESET}"
                
                # 버퍼에 추가
                output_buffer.append(f"  {status_icon}{member.icon} Lv.{member.level} {name_color}{member.name}{Color.RESET}{status_icons}")
                output_buffer.append(f"  {hp_icon} HP: {hp_color}{member.current_hp}{Color.RESET} / {Color.WHITE}{member.max_hp}{Color.RESET} {Color.WHITE}[{hp_bar} {Color.WHITE}]{Color.RESET} | {mp_icon} MP: {mp_color}{member.current_mp}{Color.RESET} / {Color.WHITE}{member.max_mp}{Color.RESET} {Color.WHITE}[{mp_bar} {Color.WHITE}]{Color.RESET} | {brv_color}⚡ BRV: {member.brave_points}{Color.RESET}")
                output_buffer.append(f"  ⌛ TIME: {Color.WHITE}[{atb_bar}{Color.WHITE}]{Color.RESET} {atb_display} | SPD: {speed_color}{member.speed}{Color.RESET}{casting_status}")
        
        # 적군 상태
        output_buffer.append(f"\n{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
        output_buffer.append(f"{Color.BRIGHT_WHITE}⚔️  적군 상태{Color.RESET}")
        output_buffer.append(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
        
        for enemy in self.enemies:
            if enemy.is_alive:
                # 현재 턴 표시
                if enemy == self.current_turn_char:
                    name_color = Color.BRIGHT_RED
                    status_icon = "▶"
                else:
                    name_color = Color.WHITE
                    status_icon = " "
                
                # 상태 아이콘
                status_icons = ""
                if enemy.is_casting:
                    status_icons += " 🔮"
                
                # HP/BRV 색상
                hp_color, hp_icon = self.get_hp_color_and_icon(enemy)
                brv_color = self.get_brv_color(enemy)
                speed_color = self.get_speed_color(enemy.speed, avg_speed)
                
                # HP 게이지 생성
                hp_ratio = enemy.current_hp / enemy.max_hp
                hp_filled = int(hp_ratio * 10)
                hp_bar = f"{hp_color}{'▰'*hp_filled}{'▱'*(10-hp_filled)}{Color.RESET}"
                
                # ATB 게이지
                atb_bar, atb_display = self.create_atb_bar(enemy.atb_gauge, enemy)
                
                # 캐스팅 상태 표시
                casting_status = ""
                if enemy.is_casting:
                    casting_status = f" {Color.BRIGHT_MAGENTA}[CASTING: {enemy.casting_skill_name}]{Color.RESET}"
                
                # 버퍼에 추가
                output_buffer.append(f"  {status_icon}{enemy.icon} {name_color}{enemy.name}{Color.RESET}{status_icons}")
                output_buffer.append(f"  {hp_icon} HP: {hp_color}{enemy.current_hp}{Color.RESET} / {Color.WHITE}{enemy.max_hp}{Color.RESET} {Color.WHITE}[{hp_bar} {Color.WHITE}]{Color.RESET} | {brv_color}⚡ BRV: {enemy.brave_points}{Color.RESET}")
                output_buffer.append(f"  ⌛ TIME: {Color.WHITE}[{atb_bar}{Color.WHITE}]{Color.RESET} {atb_display} | SPD: {speed_color}{enemy.speed}{Color.RESET}{casting_status}")
        
        # 버퍼의 모든 내용을 한 번에 출력 (깜빡임 최소화)
        print("\n".join(output_buffer), end="", flush=True)
    
    def update_atb_gauges(self):
        """ATB 게이지 업데이트 (10 FPS) - 평균 속도 기준으로 정규화"""
        all_chars = self.party + self.enemies
        alive_chars = [char for char in all_chars if char.is_alive]
        
        if not alive_chars:
            return
        
        # 평균 속도 계산
        avg_speed = sum(char.speed for char in alive_chars) / len(alive_chars)
        
        # 기본 ATB 증가율 (평균 속도 기준)
        base_atb_rate = 150  # 평균 속도일 때의 기본 증가량
        
        for char in alive_chars:
            if char.atb_gauge < self.ATB_READY_THRESHOLD:
                # 속도 비율 계산 (평균 대비)
                speed_ratio = char.speed / avg_speed
                
                # ATB 증가량 = 기본 증가율 × 속도 비율
                # 이렇게 하면 모든 캐릭터가 비슷한 시간에 READY 상태가 됨
                atb_increase = int(base_atb_rate * speed_ratio)
                
                char.atb_gauge = min(self.ATB_READY_THRESHOLD, char.atb_gauge + atb_increase)
    
    def get_next_turn_character(self):
        """다음 턴 캐릭터 찾기"""
        all_chars = self.party + self.enemies
        ready_chars = [char for char in all_chars if char.is_alive and char.atb_gauge >= self.ATB_READY_THRESHOLD]
        
        if ready_chars:
            # 가장 먼저 READY가 된 캐릭터 (속도가 높은 순)
            return max(ready_chars, key=lambda x: x.speed)
        return None
    
    def simulate_battle(self):
        """전투 시뮬레이션 실행"""
        print(f"{Color.BRIGHT_YELLOW}=== 전투 시뮬레이션 시작 ==={Color.RESET}")
        print("ATB 게이지가 실시간으로 증가합니다 (10 FPS)")
        print("평균 속도 기준으로 정규화된 ATB 시스템")
        print("누군가의 턴이 되면 멈춥니다...")
        
        # 평균 속도 정보 표시
        all_chars = self.party + self.enemies
        alive_chars = [char for char in all_chars if char.is_alive]
        avg_speed = sum(char.speed for char in alive_chars) / len(alive_chars) if alive_chars else 50
        print(f"{Color.BRIGHT_CYAN}현재 평균 속도: {avg_speed:.1f}{Color.RESET}")
        
        print(f"{Color.BRIGHT_CYAN}엔터를 눌러 시작하세요{Color.RESET}")
        input()
        
        # 첫 화면만 클리어
        os.system('cls' if os.name == 'nt' else 'clear')
        
        frame_count = 0
        while True:
            # ATB 게이지 업데이트
            self.update_atb_gauges()
            
            # 화면 표시 (깜빡임 없이)
            self.display_battle_status(clear_screen=False)
            
            # 평균 속도와 프레임 카운터 표시
            alive_chars = [char for char in all_chars if char.is_alive]
            current_avg_speed = sum(char.speed for char in alive_chars) / len(alive_chars) if alive_chars else 50
            
            frame_count += 1
            
            # 상태 정보를 화면 하단에 고정 표시
            print(f"\n{Color.BRIGHT_BLACK}───────────────────────────────────────────────────────────────────────{Color.RESET}")
            print(f"{Color.BRIGHT_BLACK}프레임: {frame_count:4d} | 10 FPS | 평균 속도: {current_avg_speed:5.1f} | ESC + Enter로 종료{Color.RESET}")
            
            # 턴이 된 캐릭터 확인
            next_char = self.get_next_turn_character()
            if next_char:
                self.current_turn_char = next_char
                # 턴 시작 시에만 화면 클리어
                os.system('cls' if os.name == 'nt' else 'clear')
                self.display_battle_status(clear_screen=False)
                
                user_input = input(f"{Color.BRIGHT_CYAN}[{next_char.name} 턴] 계속하려면 엔터...{Color.RESET}")
                if user_input.lower() == 'esc':
                    break
                
                # 턴 종료 후 ATB 리셋
                next_char.atb_gauge = 0
                self.current_turn_char = None
                
                # 턴 종료 후 화면 클리어
                os.system('cls' if os.name == 'nt' else 'clear')
            
            # 10 FPS (0.1초 대기)
            time.sleep(0.1)

def main():
    simulator = BattleSimulator()
    simulator.simulate_battle()

if __name__ == "__main__":
    main()
