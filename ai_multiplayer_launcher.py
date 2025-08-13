#!/usr/bin/env python3
"""
AI 멀티플레이 게임 런처
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 목표: 클래식 모드를 AI 멀티플레이로 완전 대체
📊 기능:
- AI 동료 3명 자동 로드
- EXAONE 3.5 기반 실시간 AI 상호작용
- 백그라운드 학습 프로세스
- 게임 상태와 AI 완전 통합
"""

import os
import sys
import json
import threading
import time
from typing import List, Dict, Optional, Any
from datetime import datetime

# 프로젝트 모듈 임포트
from multiplayer_ai_creator import MultiplayerAICharacterCreator
from exaone_ai_engine import get_ai_engine
from ai_character_database import get_ai_database, preset_manager

# 게임 시스템 임포트 (기존 게임과 연동)
try:
    from game.character import Character
    # PartyManager 임포트 제거 - 직접 사용 안함
    from game.brave_combat import BraveCombatSystem
    from game.world import GameWorld
    from game.display import GameDisplay
    GAME_MODULES_AVAILABLE = True
    print("✅ 게임 시스템 통합 모듈 로드 성공")
except ImportError as e:
    GAME_MODULES_AVAILABLE = False
    print(f"⚠️ 게임 모듈 일부 미사용 가능, 독립 실행 모드: {e}")

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BRIGHT_CYAN = '\033[96m\033[1m'
BRIGHT_WHITE = '\033[97m\033[1m'

# 한글 입력 지원 함수
def english_to_korean(text: str) -> str:
    """영어 입력을 한글로 변환"""
    # 영어 키보드를 한글로 매핑
    eng_to_kor = {
        'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
        'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
        'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
        # 대문자도 포함
        'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'Y': 'ㅛ', 'U': 'ㅕ', 'I': 'ㅑ', 'O': 'ㅒ', 'P': 'ㅖ',
    }
    
    # 먼저 자모로 변환
    jamo_result = ""
    for char in text:
        if char in eng_to_kor:
            jamo_result += eng_to_kor[char]
        else:
            jamo_result += char
    
    # 자모를 한글로 조합
    return combine_jamo_to_hangul(jamo_result)

def combine_jamo_to_hangul(jamo_text: str) -> str:
    """자모를 조합하여 완성된 한글로 만들기"""
    # 초성, 중성, 종성 정의
    CHOSUNG = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    JUNGSUNG = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    JONGSUNG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    
    # 자모가 너무 적으면 그대로 반환
    if len(jamo_text) < 2:
        return jamo_text
    
    result = ""
    i = 0
    
    while i < len(jamo_text):
        char = jamo_text[i]
        
        # 초성으로 사용할 수 있는지 확인
        if char in CHOSUNG:
            cho_idx = CHOSUNG.index(char)
            
            # 다음 글자가 중성인지 확인
            if i + 1 < len(jamo_text):
                next_char = jamo_text[i + 1]
                
                # 중성인지 확인
                if next_char in JUNGSUNG:
                    jung_idx = JUNGSUNG.index(next_char)
                    jong_idx = 0  # 종성 없음
                    advance = 2
                    
                    # 그 다음 글자가 종성으로 사용 가능한지 확인
                    if i + 2 < len(jamo_text):
                        third_char = jamo_text[i + 2]
                        # 종성으로 사용할 수 있는 자음인지 확인
                        if third_char in JONGSUNG[1:]:  # 빈 종성 제외
                            # 하지만 그 다음에 중성이 오면 새 글자 시작
                            if i + 3 < len(jamo_text) and jamo_text[i + 3] in JUNGSUNG:
                                # 종성을 사용하지 말고 다음 글자 시작
                                pass
                            else:
                                jong_idx = JONGSUNG.index(third_char)
                                advance = 3
                    
                    # 유니코드로 조합
                    unicode_val = 0xAC00 + (cho_idx * 21 * 28) + (jung_idx * 28) + jong_idx
                    result += chr(unicode_val)
                    i += advance
                    continue
        
        # 조합하지 못한 경우 그대로 추가
        result += char
        i += 1
    
    return result

def safe_korean_input(prompt: str = "", allow_back: bool = True) -> str:
    """한글 입력을 안전하게 처리하는 함수 - 스마트 변환 시스템"""
    try:
        if allow_back:
            full_prompt = f"{prompt} (뒤로가기: q) "
        else:
            full_prompt = prompt
            
        while True:
            # 기본 input() 사용하되 한글 입력 상태 처리 개선
            if full_prompt:
                print(full_prompt, end='', flush=True)
            
            # 한글 입력 상태에서 안전한 처리
            try:
                result = input().strip()
                
                # 뒤로가기 처리 (영어/한글 모두 지원)
                if allow_back and result.lower() in ['q', 'ㅂ', 'back']:
                    return "BACK"
                
                # 빈 입력이면 다시 입력 요청
                if not result:
                    print("입력이 비어있습니다. 다시 입력해주세요.")
                    continue
                
                # 🚀 스마트 한글 변환 시스템
                if all(ord(c) < 128 for c in result):  # 모든 문자가 ASCII (영어)
                    # 1. 일반적인 영어 응답은 변환하지 않음
                    common_english = {'y', 'n', 'yes', 'no', 'ok', 'cancel', 'back', 'q', 'exit'}
                    if result.lower() in common_english:
                        return result
                    
                    # 2. 숫자나 특수문자만 있으면 변환하지 않음  
                    if result.isdigit() or not result.isalpha():
                        return result
                    
                    # 3. 길이가 1글자이고 의미있는 영어가 아니면 자동 변환
                    if len(result) == 1 and result.lower() not in common_english:
                        korean_converted = english_to_korean(result)
                        if korean_converted != result:
                            print(f"🔄 자동 변환: '{result}' → '{korean_converted}'")
                            return korean_converted
                    
                    # 4. 길이가 2글자 이상이면 사용자에게 선택권 제공 (기존 방식)
                    if len(result) >= 2:
                        korean_converted = english_to_korean(result)
                        if korean_converted != result:
                            print(f"\n💡 영어 입력을 한글로 변환: '{result}' → '{korean_converted}'")
                            print("🎯 팁: F9키로 변환 모드를 끄거나 켤 수 있습니다")
                            choice = input("변환된 한글을 사용하시겠습니까? (y/n, 엔터=예): ").strip().lower()
                            if choice in ['', 'y', 'yes', 'ㅛ']:
                                result = korean_converted
                    
                # 키보드 버퍼 정리 (Windows에서 한글 입력 후 문제 해결)
                if sys.platform.startswith('win'):
                    try:
                        import msvcrt
                        # 남은 키 입력 모두 제거
                        while msvcrt.kbhit():
                            msvcrt.getch()
                    except:
                        pass
                
                return result
                
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                sys.exit(0)
            except EOFError:
                if allow_back:
                    return "BACK"
                return ""
                
    except UnicodeDecodeError:
        # 인코딩 문제 발생 시 재시도
        print("한글 입력에 문제가 있습니다. 한영키를 눌러 입력 모드를 확인해주세요.")
        return safe_korean_input(prompt, allow_back)
            
    except Exception as e:
        print(f"입력 오류: {e}")
        if allow_back:
            return "BACK"
        return ""
BRIGHT_GREEN = '\033[92m\033[1m'
BRIGHT_YELLOW = '\033[93m\033[1m'
BRIGHT_RED = '\033[91m\033[1m'

class AIMultiplayerLauncher:
    """AI 멀티플레이 게임 런처"""
    
    def __init__(self):
        self.ai_creator = MultiplayerAICharacterCreator()
        self.ai_engine = get_ai_engine()
        self.ai_companions = []
        self.player_character = None
        self.learning_thread = None
        self.learning_active = False
        
        # 게임 통합 상태
        self.game_integrated = GAME_MODULES_AVAILABLE
        self.party_manager = None
        self.combat_system = None
        self.world = None
        self.display = None
        
        print(f"{BRIGHT_CYAN}🚀 AI 멀티플레이 런처 초기화 완료{RESET}")
        if self.game_integrated:
            print(f"{GREEN}✅ 게임 시스템 통합 활성화{RESET}")
        else:
            print(f"{YELLOW}⚠️ 독립 실행 모드 (게임 시스템 미연동){RESET}")
    
    def run(self):
        """AI 멀티플레이 모드 실행"""
        return self.start_ai_multiplayer_mode()
    
    def start_ai_multiplayer_mode(self):
        """AI 멀티플레이 모드 시작"""
        print(f"\n{BRIGHT_CYAN}🌟 Dawn of Stellar - AI 멀티플레이 모드{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{CYAN}클래식 모드가 AI 멀티플레이로 진화했습니다!{RESET}")
        print(f"{WHITE}이제 3명의 지능형 AI 동료와 함께 모험을 떠나보세요.{RESET}")
        
        # 메뉴 루프
        while True:
            choice = self._display_main_menu()
            
            if choice is None:  # 취소 또는 오류
                print(f"{YELLOW}메뉴 선택이 취소되었습니다.{RESET}")
                continue
            elif choice == 6 or choice == -1:  # 종료
                print(f"{GREEN}게임을 종료합니다. 안녕히 가세요!{RESET}")
                self._cleanup_and_exit()
                break
            elif choice == 0:  # 새로운 AI 모험 시작
                self._start_new_ai_adventure()
            elif choice == 1:  # 기존 AI 파티 불러오기
                self._load_existing_ai_party()
            elif choice == 2:  # 커스텀 AI 파티 생성
                self._create_custom_ai_party()
            elif choice == 3:  # AI 캐릭터 관리
                self._manage_ai_characters()
            elif choice == 4:  # AI 훈련 모드
                self._ai_training_mode()
            elif choice == 5:  # 설정
                self._settings_menu()
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
    
    def _display_main_menu(self):
        """커서 메뉴 기반 메인 메뉴 표시"""
        try:
            # 커서 메뉴 시스템 임포트
            from game.cursor_menu_system import CursorMenu
            
            # 메뉴 옵션
            options = [
                "🆕 새로운 AI 모험 시작",
                "📁 기존 AI 파티 불러오기", 
                "🎭 커스텀 AI 파티 생성",
                "👥 AI 캐릭터 관리",
                "🧠 AI 훈련 모드",
                "⚙️ 설정",
                "❌ 종료"
            ]
            
            # 각 옵션의 설명
            descriptions = [
                "AI 동료 3명과 함께 새로운 모험을 시작합니다",
                "이전에 저장된 AI 파티를 불러와 게임을 계속합니다",
                "원하는 직업과 성격의 AI 동료들로 파티를 직접 구성합니다",
                "생성된 AI 캐릭터들의 정보를 확인하고 관리합니다",
                "AI들의 학습 데이터를 확인하고 훈련 상태를 모니터링합니다",
                "EXAONE 모델 설정, 학습 옵션 등을 조정합니다",
                "AI 멀티플레이어 모드를 종료하고 메인 메뉴로 돌아갑니다"
            ]
            
            # 커서 메뉴 생성
            menu = CursorMenu(
                title=f"{BRIGHT_WHITE}🎮 AI 멀티플레이 메뉴{RESET}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            return menu.run()
            
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            return self._display_fallback_menu()
    
    def _display_fallback_menu(self):
        """폴백 텍스트 메뉴"""
        print(f"\n{BRIGHT_WHITE}🎮 AI 멀티플레이 메뉴{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{WHITE}1. {GREEN}🆕 새로운 AI 모험 시작{RESET}")
        print(f"{WHITE}2. {BLUE}📁 기존 AI 파티 불러오기{RESET}")
        print(f"{WHITE}3. {MAGENTA}🎭 커스텀 AI 파티 생성{RESET}")
        print(f"{WHITE}4. {CYAN}👥 AI 캐릭터 관리{RESET}")
        print(f"{WHITE}5. {YELLOW}🧠 AI 훈련 모드{RESET}")
        print(f"{WHITE}6. {WHITE}⚙️ 설정{RESET}")
        print(f"{WHITE}0. {RED}❌ 종료{RESET}")
        
        choice = input(f"\n{YELLOW}선택하세요 (0-6): {RESET}").strip()
        
        # 문자열을 숫자로 변환
        try:
            return int(choice) - 1 if choice != '0' else 6
        except:
            return None
    
    def _start_new_ai_adventure(self):
        """새로운 AI 모험 시작 - 질문 기반 파티 추천 포함"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            print(f"\n{BRIGHT_GREEN}🆕 새로운 AI 모험을 시작합니다!{RESET}")
            
            # 파티 생성 방식 선택
            options = [
                "🎯 수동 캐릭터 생성 (추천)",
                "⚡ 자동 캐릭터 생성 (빠른 시작)",
                "🧠 AI 추천 시스템 (8개 질문)",
                "🎲 랜덤 파티 생성",
                "⚖️ 균형잡힌 파티 생성",
                "📁 저장된 프리셋 불러오기",
                "📋 파티 히스토리 보기",
                "💾 단일 캐릭터 생성 및 저장"
            ]
            
            descriptions = [
                "캐릭터의 직업, 이름, 성별을 직접 선택합니다\n• 완전한 커스터마이징 가능\n• 원하는 조합으로 파티 구성\n• 각 캐릭터의 특성도 수동 선택",
                "AI가 초보자 친화적인 캐릭터와 파티를 자동으로 구성합니다",
                "8가지 질문에 답하면 플레이 스타일에 맞는 파티를 추천합니다",
                "역할 균형을 고려한 랜덤 파티를 생성합니다",
                "플레이어 캐릭터만 먼저 생성하고 나중에 AI 동료를 추가합니다",
                "이전에 저장한 파티 프리셋을 불러와서 게임을 시작합니다",
                "과거에 플레이했던 파티 구성을 확인하고 재사용합니다",
                "게임 시작 없이 캐릭터만 생성하여 프리셋으로 저장합니다"
            ]
            
            menu = CursorMenu(
                title=f"{YELLOW}🎮 파티 생성 방식 선택{RESET}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            choice = menu.run()
            
            if choice is None or choice == -1:
                print(f"{YELLOW}파티 생성이 취소되었습니다.{RESET}")
                return
            
            if choice == 0:  # 수동 캐릭터 생성 (추천)
                self._manual_character_creation()
            elif choice == 1:  # 자동 캐릭터 생성 (빠른 시작)
                self._quick_start_adventure()
            elif choice == 2:  # AI 추천 시스템 (8개 질문)
                self._question_based_party_adventure()
            elif choice == 3:  # 랜덤 파티 생성
                self._random_balanced_party_adventure()
            elif choice == 4:  # 균형잡힌 파티 생성
                self._player_only_start()
            elif choice == 5:  # 저장된 프리셋 불러오기
                self._load_saved_preset()
            elif choice == 6:  # 파티 히스토리 보기
                self._show_party_history()
            elif choice == 7:  # 단일 캐릭터 생성 및 저장
                self._create_single_character_preset()
                
        except ImportError:
            # 폴백: 기본 자동 생성
            self._quick_start_adventure()
    
    def _quick_start_adventure(self):
        """빠른 시작 - 자동 캐릭터 생성"""
        print(f"\n{CYAN}⚡ 빠른 시작 모드{RESET}")
        print(f"{WHITE}AI가 초보자 친화적인 파티를 자동으로 구성합니다...{RESET}")
        
        # 플레이어 캐릭터 자동 생성
        player_char = self._auto_create_player_character()
        if not player_char:
            print(f"{RED}❌ 플레이어 캐릭터 생성에 실패했습니다.{RESET}")
            return
        
        print(f"{GREEN}✅ 플레이어: {player_char.get('name', 'Unknown')} ({player_char.get('character_class', 'Unknown')}){RESET}")
        
        # AI 동료 3명 자동 생성
        player_job = player_char.get('character_class', '')
        ai_party = self.ai_creator.create_multiplayer_party(3, exclude_jobs=[player_job])
        
        # 게임 시작
        self._start_game_with_ai_party(player_char, ai_party, [])
    
    def _question_based_party_adventure(self):
        """질문 기반 맞춤 파티 추천"""
        try:
            from game.auto_party_builder import AutoPartyBuilder
            
            print(f"\n{CYAN}🎯 질문 기반 맞춤 파티 추천{RESET}")
            print(f"{WHITE}당신의 플레이 스타일에 맞는 파티를 추천해드립니다!{RESET}")
            
            # 파티 빌더 생성
            party_builder = AutoPartyBuilder()
            
            # 질문 기반 파티 생성 (4명 파티)
            recommended_party = party_builder.create_question_based_party(4)
            
            if not recommended_party:
                print(f"{YELLOW}파티 추천이 취소되었습니다. 빠른 시작으로 전환합니다.{RESET}")
                self._quick_start_adventure()
                return
            
            # 첫 번째 캐릭터를 플레이어로, 나머지를 AI로 설정
            player_char = self._convert_character_to_player_format(recommended_party[0])
            ai_companions = [self._convert_character_to_ai_format(char) for char in recommended_party[1:]]
            
            print(f"\n{GREEN}✨ 맞춤형 파티가 완성되었습니다!{RESET}")
            print(f"{CYAN}플레이어: {player_char.get('name')} ({player_char.get('character_class')}){RESET}")
            
            # 게임 시작
            self._start_game_with_ai_party(player_char, ai_companions, [])
            
        except ImportError as e:
            print(f"{RED}❌ 파티 빌더를 불러올 수 없습니다: {e}{RESET}")
            print(f"{YELLOW}빠른 시작으로 전환합니다.{RESET}")
            self._quick_start_adventure()
    
    def _random_balanced_party_adventure(self):
        """랜덤 균형 파티 생성"""
        print(f"\n{CYAN}🎲 랜덤 균형 파티 생성{RESET}")
        print(f"{WHITE}역할 균형을 고려한 랜덤 파티를 생성합니다...{RESET}")
        
        # 균형잡힌 직업 조합 선택
        balanced_combinations = [
            ['전사', '아크메이지', '궁수', '성기사'],
            ['암흑기사', '정령술사', '도적', '바드'],
            ['용기사', '시간술사', '몽크', '신관'],
            ['검성', '차원술사', '연금술사', '드루이드'],
            ['마검사', '네크로맨서', '해적', '무당']
        ]
        
        import random
        selected_combo = random.choice(balanced_combinations)
        
        # 플레이어 캐릭터 생성 (첫 번째 직업)
        player_char = self._create_basic_character(selected_combo[0])
        player_char['name'] = self._get_random_name()
        
        # AI 동료들 생성
        ai_party = []
        for job in selected_combo[1:]:
            ai_char = self.ai_creator.create_ai_character_for_multiplayer(preferred_job=job)
            ai_party.append(ai_char)
        
        print(f"{GREEN}✅ 랜덤 균형 파티 생성 완료!{RESET}")
        print(f"{CYAN}플레이어: {player_char.get('name')} ({player_char.get('character_class')}){RESET}")
        
        # 게임 시작
        self._start_game_with_ai_party(player_char, ai_party, [])
    
    def _player_only_start(self):
        """플레이어만 생성 후 AI 추가"""
        print(f"\n{CYAN}👤 플레이어 캐릭터 생성{RESET}")
        
        # 플레이어 캐릭터 선택/생성
        player_char = self._create_or_select_player_character()
        if not player_char:
            print(f"{YELLOW}플레이어 캐릭터 생성이 취소되었습니다.{RESET}")
            return
        
        print(f"{GREEN}✅ 플레이어: {player_char.get('name')} ({player_char.get('character_class')}){RESET}")
        print(f"{WHITE}나중에 AI 동료를 추가할 수 있습니다.{RESET}")
        
        # 빈 AI 파티로 게임 시작
        self._start_game_with_ai_party(player_char, [], [])
    
    def _convert_character_to_player_format(self, character) -> Dict:
        """Character 객체를 플레이어 형식으로 변환"""
        return {
            'name': character.name,
            'character_class': character.character_class,
            'level': character.level,
            'hp': character.hp,
            'mp': character.mp,
            'attack': character.attack,
            'defense': character.defense,
            'speed': character.speed,
            'luck': character.luck,
            'traits': getattr(character, 'traits', []),
            'passives': getattr(character, 'party_passives', [])
        }
    
    def _convert_character_to_ai_format(self, character) -> Dict:
        """Character 객체를 AI 형식으로 변환"""
        return {
            'character_data': {
                'basic_info': {
                    'name': character.name,
                    'class': character.character_class,
                    'level': character.level
                },
                'stats': {
                    'hp': character.hp,
                    'mp': character.mp,
                    'attack': character.attack,
                    'defense': character.defense,
                    'speed': character.speed,
                    'luck': character.luck
                },
                'traits': getattr(character, 'traits', []),
                'passives': getattr(character, 'party_passives', [])
            },
            'ai_personality': self._generate_ai_personality(character.character_class)
        }
    
    def _generate_ai_personality(self, character_class: str) -> Dict:
        """직업에 따른 AI 성격 생성"""
        personality_templates = {
            '전사': {'aggression': 0.8, 'caution': 0.3, 'teamwork': 0.7},
            '아크메이지': {'aggression': 0.4, 'caution': 0.8, 'teamwork': 0.6},
            '궁수': {'aggression': 0.6, 'caution': 0.7, 'teamwork': 0.5},
            '성기사': {'aggression': 0.5, 'caution': 0.6, 'teamwork': 0.9},
            '도적': {'aggression': 0.7, 'caution': 0.8, 'teamwork': 0.4}
        }
        
        return personality_templates.get(character_class, 
                                       {'aggression': 0.5, 'caution': 0.5, 'teamwork': 0.5})
    
    def _get_random_name(self) -> str:
        """unified_name_pools에서 랜덤 이름 선택"""
        try:
            from game.unified_name_pools import get_random_name
            import random
            
            # 성별 랜덤 선택하여 이름 가져오기
            gender = random.choice(['male', 'female'])
            name, detected_gender = get_random_name(gender)
            
            return name
                
        except ImportError:
            # unified_name_pools를 불러올 수 없는 경우
            fallback_names = ['아리우스', '셀레스트', '발렌타인', '유나', '가브리엘', '이사벨라']
            import random
            return random.choice(fallback_names)
    
    def _auto_create_player_character(self) -> Optional[Dict]:
        """플레이어 캐릭터 자동 생성 (선택 스킵)"""
        try:
            # AI가 추천하는 초보자 친화적 캐릭터 자동 선택
            recommended_jobs = ['전사', '성기사', '아크메이지', '궁수']  # 초보자 친화적 직업들
            
            import random
            selected_job = random.choice(recommended_jobs)
            
            # 기본 캐릭터 생성 후 랜덤 이름 부여
            player_char = self._create_basic_character(selected_job)
            player_char['name'] = self._get_random_name()
            
            print(f"🎯 선택된 직업: {selected_job}")
            print(f"👤 캐릭터: {player_char.get('name', 'Unknown')}")
            return player_char
                
        except Exception as e:
            print(f"{RED}❌ 자동 캐릭터 생성 오류: {e}{RESET}")
            return self._create_basic_character('전사')  # 폴백: 기본 전사
    
    def _create_basic_character(self, job_class: str) -> Dict:
        """기본 캐릭터 생성 (폴백용)"""
        return {
            'name': f'플레이어_{job_class}',
            'character_class': job_class,
            'level': 1,
            'hp': 100,
            'mp': 50,
            'attack': 20,
            'defense': 15,
            'speed': 10,
            'luck': 5,
            'traits': []
        }
    
    def _select_character_traits_for_ai_mode(self, player_char: Dict, ai_party: List[Dict]) -> bool:
        """AI 모드에서 각 캐릭터의 실제 특성 선택"""
        try:
            from game.passive_selection import PassiveSelectionSystem
            from game.character import Character
            
            passive_system = PassiveSelectionSystem()
            
            print(f"\n{BRIGHT_CYAN}🎯 캐릭터 특성 선택{RESET}")
            print(f"{WHITE}각 캐릭터마다 개별 특성을 선택합니다.{RESET}")
            
            # 모든 캐릭터를 Character 객체로 변환
            character_objects = []
            
            # 플레이어 캐릭터 추가
            player_character = Character(
                name=player_char.get('name', 'Player'),
                character_class=player_char.get('character_class', player_char.get('class', '전사')),
                level=player_char.get('level', 1)
            )
            character_objects.append(player_character)
            
            # AI 캐릭터들 추가
            for char in ai_party:
                if hasattr(char, 'character_data') and 'character_data' in char:
                    basic_info = char['character_data']['basic_info']
                    char_obj = Character(
                        name=basic_info['name'],
                        character_class=basic_info['class'],
                        level=basic_info.get('level', 1)
                    )
                    character_objects.append(char_obj)
            
            # 패시브 선택 실행
            return passive_system.select_passives_for_party(character_objects)
            
        except Exception as e:
            print(f"{RED}❌ 특성 선택 오류: {e}{RESET}")
            print(f"{YELLOW}특성 선택을 건너뛰고 게임을 시작합니다.{RESET}")
            return True
    
    def _create_or_select_player_character(self) -> Optional[Dict]:
        """플레이어 캐릭터 선택 - 프리셋만 사용"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "📁 기존 캐릭터 사용",
                "🤖 AI가 추천하는 캐릭터", 
                "🎲 랜덤 프리셋 캐릭터"
            ]
            
            descriptions = [
                "저장된 프리셋 캐릭터 중에서 선택합니다",
                "AI가 초보자에게 적합한 프리셋 캐릭터를 추천합니다",
                "다양한 프리셋 중에서 랜덤으로 선택합니다"
            ]
            
            menu = CursorMenu(
                title=f"{YELLOW}👤 플레이어 캐릭터 설정{RESET}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            choice = menu.run()
            
            if choice is None or choice == -1:
                return None
            elif choice == 0:
                return self._select_existing_character()
            elif choice == 1:
                return self._ai_recommended_character()
            elif choice == 2:
                return self._random_preset_character()
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return None
                
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print(f"\n{YELLOW}👤 플레이어 캐릭터 설정{RESET}")
            print("1. 기존 캐릭터 사용") 
            print("2. AI가 추천하는 캐릭터")
            print("3. 랜덤 프리셋 캐릭터")
            
            choice = input("선택 (1-3): ").strip()
            
            if choice == "1":
                return self._select_existing_character()
            elif choice == "2":
                return self._ai_recommended_character()
            elif choice == "3":
                return self._random_preset_character()
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return None
    
    def _create_new_player_character(self) -> Dict:
        """새 플레이어 캐릭터 생성 - 커서 메뉴"""
        print(f"\n{CYAN}새 캐릭터를 생성합니다...{RESET}")
        
        # 300개 이상의 성별별 이름 목록 (AI 캐릭터 생성기와 동일)
        male_names = [
            "아리우스", "발렌타인", "가브리엘", "라파엘", "카이저", "레오나르드", "세바스찬", "알렉산더",
            "막시무스", "아드리안", "루카스", "니콜라스", "도미닉", "빈센트", "에밀리오", "마르코",
            "클라우디우스", "오거스트", "바실리우스", "이그니스", "펠릭스", "라이언", "에릭",
            "마틴", "엘리아스", "다미안", "율리안", "카를로스", "디에고", "파블로", "프란시스",
            "로드리고", "안토니오", "페드로", "미구엘", "호세", "루이스", "페르난도", "애드워드",
            "핀", "트리스탄", "로넌", "블레이크", "브로디", "데클란", "숀", "리암", "루카", 
            "제임슨", "카일", "브랜든", "알렉스", "자이든", "자비에르","테오", "녹티스", "클라우드"
        ]
        
        female_names = [
            "아리아", "셀레스트","유나", "이사벨라", "발레리아", "세라피나", "아드리아나", "밀리아", 
            "비비안", "클라라","비라","유엘", "에밀리아", "루시아", "소피아", "올리비아", "나탈리아", 
            "카밀라", "레오니", "미리암", "로사", "에스텔라", "바이올렛", "샬롯", "베아트리체", 
            "카타리나", "레베카", "엘레나", "마리아", "안나", "루나", "시에라", "니나", "에바",
            "젤다", "세레나", "루나", "스텔라", "노바", "오즈","코린"
        ]
        
        # 이름 입력 (뒤로가기 지원)
        while True:
            print(f"\n{YELLOW}💡 캐릭터 생성 방법을 선택하세요:{RESET}")
            print(f"{WHITE}1. 👨 남성 캐릭터 (남성 이름 추천){RESET}")
            print(f"{WHITE}2. 👩 여성 캐릭터 (여성 이름 추천){RESET}")
            print(f"{WHITE}3. ✏️ 직접 이름 입력 (성별 자동 감지){RESET}")
            print(f"{WHITE}4. ⚙️ 성별 직접 선택 후 이름 입력{RESET}")
            
            choice = safe_korean_input("선택 (1-4)", allow_back=True)
            
            if choice == "BACK":
                print(f"{YELLOW}캐릭터 생성을 취소합니다.{RESET}")
                return None
            elif choice == "1":
                print("📝 남성 이름 추천:", ", ".join(male_names[:10]))
                print(f"{WHITE}   더 많은 이름: {', '.join(male_names[10:20])}{RESET}")
                name = safe_korean_input("선택하거나 직접 입력", allow_back=True)
                gender = "male"
            elif choice == "2":
                print("📝 여성 이름 추천:", ", ".join(female_names[:10]))
                print(f"{WHITE}   더 많은 이름: {', '.join(female_names[10:20])}{RESET}")
                name = safe_korean_input("선택하거나 직접 입력", allow_back=True)
                gender = "female"
            elif choice == "3":
                name = safe_korean_input("캐릭터 이름", allow_back=True)
                # 이름으로부터 성별 자동 감지
                if name in male_names:
                    gender = "male"
                elif name in female_names:
                    gender = "female"
                else:
                    # 자동 감지 실패 시 성별 선택
                    print(f"{YELLOW}이름 '{name}'의 성별을 자동으로 감지할 수 없습니다.{RESET}")
                    gender_choice = safe_korean_input("성별 선택 (1:남성, 2:여성)", allow_back=True)
                    if gender_choice == "BACK":
                        continue
                    gender = "male" if gender_choice == "1" else "female"
            elif choice == "4":
                # 성별 먼저 선택
                print(f"\n{WHITE}성별을 선택하세요:{RESET}")
                print(f"{WHITE}1. 👨 남성{RESET}")
                print(f"{WHITE}2. 👩 여성{RESET}")
                gender_choice = safe_korean_input("성별 선택 (1-2)", allow_back=True)
                if gender_choice == "BACK":
                    continue
                
                if gender_choice == "1":
                    gender = "male"
                    print("📝 남성 이름 추천:", ", ".join(male_names[:10]))
                    print(f"{WHITE}   더 많은 이름: {', '.join(male_names[10:20])}{RESET}")
                elif gender_choice == "2":
                    gender = "female"
                    print("📝 여성 이름 추천:", ", ".join(female_names[:10]))
                    print(f"{WHITE}   더 많은 이름: {', '.join(female_names[10:20])}{RESET}")
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
                    continue
                
                name = safe_korean_input("이름 선택 또는 직접 입력", allow_back=True)
            else:
                print(f"{RED}1-4 중에서 선택해주세요.{RESET}")
                continue
            
            if name == "BACK":
                continue
            elif name and name.strip():
                name = name.strip()
                break
            else:
                print(f"{RED}이름을 입력해주세요.{RESET}")
        
        # 한글 입력 후 키보드 상태 정리
        print(f"{GREEN}이름: {name}{RESET}")
        print("\n직업을 선택해주세요...")
        
        # 시간 간격 추가하여 입력 안정화
        time.sleep(0.1)
        
        # 직업 선택 - 커서 메뉴
        try:
            from game.cursor_menu_system import CursorMenu
            
            # 먼저 직업군 선택
            category_options = [
                "🛡️ 전투 직업군 (8개)",
                "🔮 마법 직업군 (10개)", 
                "✨ 특수 직업군 (10개)"
            ]
            
            category_descriptions = [
                "탱커와 물리 딜러 중심의 전투 전문 직업들",
                "마법과 원소를 다루는 마법사 계열 직업들",
                "독특한 능력을 가진 특수 역할 직업들"
            ]
            
            category_menu = CursorMenu(
                title=f"{CYAN}직업군 선택{RESET}",
                options=category_options,
                descriptions=category_descriptions,
                cancellable=True
            )
            
            category_choice = category_menu.run()
            if category_choice is None:
                return None
            
            # 선택된 직업군에 따라 직업 목록 표시
            if category_choice == 0:  # 전투 직업군
                job_classes = ["전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크", "바드"]
                job_descriptions = [
                    "높은 방어력과 HP를 가진 전선 탱커. 초보자에게 추천!",
                    "강력한 마법 공격력을 가진 마법사. 전략적 플레이 필요",
                    "원거리 물리 공격 전문. 균형잡힌 성능",
                    "빠른 속도와 독 공격이 특징. 테크니컬한 플레이",
                    "회복과 방어를 겸하는 성스러운 기사. 파티 지원에 특화",
                    "흡혈과 어둠의 힘을 다루는 기사. 공격적인 탱커",
                    "주먹과 기 공격으로 싸우는 무투가. 연타 특화",
                    "버프와 디버프로 파티를 지원하는 음유시인"
                ]
                title = f"{CYAN}🛡️ 전투 직업군 선택{RESET}"
            elif category_choice == 1:  # 마법 직업군
                job_classes = ["네크로맨서", "용기사", "검성", "정령술사", "시간술사", "연금술사", "차원술사", "마검사", "기계공학자", "무당"]
                job_descriptions = [
                    "언데드를 다루고 생명력을 조작하는 흑마법사",
                    "드래곤의 힘을 빌려 화염 공격을 하는 기사",
                    "검과 기를 융합한 검술의 달인",
                    "4원소를 자유자재로 조작하는 마법사",
                    "시간을 조작하여 전장을 지배하는 마법사",
                    "화학과 폭발물을 다루는 과학자",
                    "차원을 넘나드는 고차원 마법사",
                    "마법과 검술을 동시에 구사하는 마검사",
                    "기계와 과학기술을 활용하는 엔지니어",
                    "영혼과 자연의 힘을 다루는 샤먼"
                ]
                title = f"{CYAN}🔮 마법 직업군 선택{RESET}"
            else:  # 특수 직업군
                job_classes = ["암살자", "해적", "사무라이", "드루이드", "철학자", "검투사", "기사", "신관", "광전사"]
                job_descriptions = [
                    "그림자에 숨어 치명타를 노리는 암살자",
                    "바다의 자유로운 전사. 이도류 특화",
                    "무사도 정신으로 무장한 동양의 검사",
                    "자연의 힘을 빌려 싸우는 자연주의자",
                    "논리와 지혜로 적을 압도하는 현자",
                    "투기장에서 단련된 전투의 프로",
                    "기사도 정신으로 무장한 창술사",
                    "신의 가호를 받는 성스러운 치료사",
                    "분노와 광기로 적을 압도하는 전사"
                ]
                title = f"{CYAN}✨ 특수 직업군 선택{RESET}"
            
            # 선택된 직업군의 직업 선택 메뉴
            job_menu = CursorMenu(
                title=title,
                options=job_classes,
                descriptions=job_descriptions,
                cancellable=True
            )
            
            job_choice = job_menu.run()
            if job_choice is None:
                return None
                
            job = job_classes[job_choice]
            
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print("\n직업 선택:")
            # Dawn of Stellar의 28개 전체 직업
            all_classes = [
                # 전투 직업군 (8개)
                "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크", "바드",
                # 마법 직업군 (10개)  
                "네크로맨서", "용기사", "검성", "정령술사", "시간술사", "연금술사", 
                "차원술사", "마검사", "기계공학자", "무당",
                # 특수 직업군 (10개)
                "암살자", "해적", "사무라이", "드루이드", "철학자", "검투사", 
                "기사", "신관", "광전사"
            ]
            
            # 역할군별로 분류해서 표시
            print(f"{CYAN}🛡️ 전투 직업군:{RESET}")
            for i in range(8):
                print(f"{i+1:2}. {all_classes[i]}")
            
            print(f"\n{BLUE}🔮 마법 직업군:{RESET}")
            for i in range(8, 18):
                print(f"{i+1:2}. {all_classes[i]}")
                
            print(f"\n{MAGENTA}✨ 특수 직업군:{RESET}")
            for i in range(18, 28):
                print(f"{i+1:2}. {all_classes[i]}")
            
            print(f"\n{YELLOW}0. 뒤로가기{RESET}")
            
            try:
                job_input = input(f"\n직업 선택 (0-{len(all_classes)}, q: 뒤로가기): ").strip()
                
                # 뒤로가기 처리
                if job_input.lower() in ['0', 'q', 'ㅂ']:
                    print(f"{YELLOW}직업 선택을 취소합니다.{RESET}")
                    return None
                
                job_choice = int(job_input) - 1
                job = all_classes[job_choice] if 0 <= job_choice < len(all_classes) else "전사"
            except ValueError:
                print(f"{RED}잘못된 입력입니다. 기본 직업(전사)을 선택합니다.{RESET}")
                job = "전사"
            except:
                job = "전사"
        
        player_char = {
            'name': name,
            'gender': gender,
            'class': job,
            'level': 1,
            'is_ai': False,
            'is_player': True
        }
        
        print(f"{GREEN}✅ {name} ({job}) 생성 완료!{RESET}")
        return player_char
    
    def _select_existing_character(self) -> Optional[Dict]:
        """기존 캐릭터 선택"""
        try:
            # 캐릭터 프리셋 파일들에서 캐릭터 로드
            characters = self._load_existing_characters()
            
            if not characters:
                print(f"{YELLOW}저장된 캐릭터가 없습니다.{RESET}")
                print(f"{BLUE}새 캐릭터를 생성합니다...{RESET}")
                return self._create_new_player_character()
            
            # 캐릭터 선택 메뉴 생성
            from game.cursor_menu_system import CursorMenu
            
            character_options = []
            character_descriptions = []
            
            for char_data in characters:
                name = char_data.get('name', 'Unknown')
                # character_class와 class 필드 모두 지원
                char_class = char_data.get('character_class') or char_data.get('class', 'Unknown')
                level = char_data.get('level', 1)
                
                # 옵션과 설명 생성
                option = f"{name} ({char_class})"
                description = f"레벨 {level} | HP: {char_data.get('current_status', {}).get('hp', '?')} | MP: {char_data.get('current_status', {}).get('mp', '?')}"
                
                character_options.append(option)
                character_descriptions.append(description)
            
            # 새 캐릭터 생성 옵션 추가
            character_options.append("🆕 새 캐릭터 생성")
            character_descriptions.append("새로운 캐릭터를 처음부터 생성합니다")
            
            # 커서 메뉴 실행
            menu = CursorMenu(
                title="기존 캐릭터 선택",
                options=character_options,
                descriptions=character_descriptions,
                cancellable=True
            )
            
            result = menu.run()
            
            if result is None:  # 취소
                return None
            elif result == len(characters):  # 새 캐릭터 생성
                return self._create_new_player_character()
            else:  # 기존 캐릭터 선택
                selected_char = characters[result]
                
                # AI 멀티플레이어 형식으로 변환
                converted_char = {
                    'name': selected_char.get('name', 'Unknown'),
                    'class': selected_char.get('character_class') or selected_char.get('class', 'Unknown'),
                    'level': selected_char.get('level', 1),
                    'source': 'existing_character'
                }
                
                print(f"\n{GREEN}✅ {converted_char['name']} ({converted_char['class']})를 선택했습니다!{RESET}")
                return converted_char
                
        except Exception as e:
            print(f"{RED}캐릭터 로드 중 오류: {e}{RESET}")
            print(f"{BLUE}새 캐릭터를 생성합니다...{RESET}")
            return self._create_new_player_character()
    
    def _load_existing_characters(self) -> List[Dict]:
        """저장된 캐릭터들 로드"""
        characters = []
        
        try:
            import os
            import json
            
            # 1. character_presets.json에서 로드
            preset_file = "character_presets.json"
            if os.path.exists(preset_file):
                with open(preset_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'character_presets' in data:
                        for char_id, char_data in data['character_presets'].items():
                            characters.append(char_data)
            
            # 2. character_presets 폴더에서 개별 파일들 로드
            preset_dir = "character_presets"
            if os.path.exists(preset_dir) and os.path.isdir(preset_dir):
                for filename in os.listdir(preset_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(preset_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                char_data = json.load(f)
                                # 개별 파일 형식에서 기본 정보 추출
                                if 'basic_info' in char_data:
                                    # AI 캐릭터 형식
                                    converted_char = {
                                        'name': char_data['basic_info']['name'],
                                        'character_class': char_data['basic_info']['class'],
                                        'level': 1,  # 기본 레벨
                                        'current_status': {
                                            'hp': 100,
                                            'mp': 20,
                                            'brave_points': 100
                                        },
                                        'source': 'ai_preset'
                                    }
                                    characters.append(converted_char)
                        except Exception as e:
                            print(f"{YELLOW}파일 {filename} 로드 실패: {e}{RESET}")
                            continue
            
            # 중복 제거 (이름 기준)
            seen_names = set()
            unique_characters = []
            for char in characters:
                name = char.get('name', '')
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_characters.append(char)
            
            return unique_characters
            
        except Exception as e:
            print(f"{RED}캐릭터 데이터 로드 실패: {e}{RESET}")
            return []
    
    def _ai_recommended_character(self) -> Dict:
        """AI 추천 프리셋 캐릭터"""
        print(f"\n{MAGENTA}🤖 AI가 당신에게 어울리는 캐릭터를 추천합니다!{RESET}")
        
        # 프리셋 캐릭터들 로드
        characters = self._load_character_presets()
        
        if not characters:
            print(f"{RED}사용 가능한 프리셋 캐릭터가 없습니다.{RESET}")
            return None
        
        import random
        # 초보자에게 적합한 직업들
        beginner_friendly = [
            "전사", "궁수", "성기사", "아크메이지", "바드", "몽크",
            "검성", "정령술사", "신관", "기사", "드루이드", "검투사"
        ]
        
        # 초보자 친화적인 직업의 프리셋 캐릭터들 필터링
        suitable_chars = [char for char in characters 
                         if char.get('class', '') in beginner_friendly]
        
        if not suitable_chars:
            # 초보자 친화적인 캐릭터가 없으면 전체에서 선택
            suitable_chars = characters
        
        recommended_char = random.choice(suitable_chars)
        
        print(f"\n{GREEN}🎉 AI 추천 캐릭터:{RESET}")
        print(f"  📝 이름: {recommended_char['name']}")
        print(f"  ⚔️  직업: {recommended_char['class']}")
        print(f"  💡 레벨: {recommended_char.get('level', 1)}")
        
        # 프리셋 캐릭터의 완전한 스탯 표시
        if 'character_data' in recommended_char:
            char_data = recommended_char['character_data']
            stats = char_data.get('stats', {})
            print(f"  ❤️  HP: {stats.get('hp', 100)} | 💙 MP: {stats.get('mp', 20)}")
            
        print(f"{WHITE}이 캐릭터는 AI 동료들과 잘 어울리고 초보자에게 적합합니다.{RESET}")
        
        accept = input("\n추천을 수락하시겠습니까? (y/n): ").strip().lower()
        if accept in ['y', 'yes', '네', '']:
            return recommended_char
        else:
            return self._select_existing_character()
    
    def _random_preset_character(self) -> Dict:
        """랜덤 프리셋 캐릭터 선택"""
        print(f"\n{MAGENTA}🎲 랜덤 프리셋 캐릭터를 선택합니다!{RESET}")
        
        # 프리셋 캐릭터들 로드
        characters = self._load_character_presets()
        
        if not characters:
            print(f"{RED}사용 가능한 프리셋 캐릭터가 없습니다.{RESET}")
            return self._select_existing_character()
        
        import random
        selected_char = random.choice(characters)
        
        print(f"\n{GREEN}🎉 선택된 캐릭터:{RESET}")
        print(f"  📝 이름: {selected_char['name']}")
        print(f"  ⚔️  직업: {selected_char['class']}")
        print(f"  💡 레벨: {selected_char.get('level', 1)}")
        
        # 프리셋 캐릭터는 완전한 스탯을 가지고 있음
        if 'character_data' in selected_char:
            char_data = selected_char['character_data']
            basic_info = char_data.get('basic_info', {})
            stats = char_data.get('stats', {})
            print(f"  ❤️  HP: {stats.get('hp', 100)} | 💙 MP: {stats.get('mp', 20)}")
        
        accept = input(f"\n이 캐릭터를 사용하시겠습니까? (y/n): ").strip().lower()
        if accept in ['y', 'yes', '네', '']:
            return selected_char
        else:
            return self._random_preset_character()  # 다시 랜덤 선택
    
    def _start_game_with_ai_party(self, player_char: Dict, ai_party: List[Dict], traits: Optional[List[Dict]] = None):
        """AI 파티와 함께 게임 시작 (특성 및 자동 저장 기능 포함)"""
        print(f"\n{BRIGHT_GREEN}🎮 게임을 시작합니다!{RESET}")
        
        self.player_character = player_char
        self.ai_companions = ai_party
        
        # 특성 시스템 적용
        if traits:
            self.party_traits = traits
            print(f"\n{BRIGHT_CYAN}🌟 파티 특성 적용:{RESET}")
            for trait in traits:
                print(f"  • {trait['name']}: {trait['description']}")
                self._apply_trait_effects(trait)
        else:
            self.party_traits = []
        
        # 파티 정보 표시
        print(f"\n{BRIGHT_WHITE}👥 파티 구성:{RESET}")
        print(f"  {GREEN}🎮 플레이어: {player_char['name']} ({player_char['class']}){RESET}")
        
        party_members = []  # 저장용 파티 데이터
        
        # 플레이어 캐릭터도 파티에 포함
        player_member_data = {
            'name': player_char['name'],
            'job': player_char['class'],
            'gender': player_char.get('gender', '미지정'),
            'personality': 'player',  # 플레이어 표시
            'behavior_style': {},
            'dialogue_style': {},
            'is_player': True,  # 플레이어 구분자
            'traits': [t['name'] for t in (traits or [])]
        }
        party_members.append(player_member_data)
        
        for i, ai_char in enumerate(ai_party, 1):
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            print(f"  {CYAN}🤖 AI {i}: {basic['name']} ({basic['class']}, {basic['personality_type']}){RESET}")
            
            # 저장용 데이터 구성
            member_data = {
                'name': basic['name'],
                'job': basic['class'],
                'gender': basic.get('gender', '미지정'),
                'personality': basic.get('personality_type', ''),
                'behavior_style': char_data.get('behavior_patterns', {}),
                'dialogue_style': char_data.get('dialogue_style', {}),
                'is_player': False,  # AI 동료 구분자
                'traits': [t['name'] for t in (traits or [])]
            }
            party_members.append(member_data)
        
        # AI 멀티플레이어 모드 자동 저장
        print(f"\n{CYAN}💾 AI 멀티플레이어 세션 자동 저장 중...{RESET}")
        auto_save_successful = self._auto_save_ai_session(party_members, traits)
        
        if auto_save_successful:
            print(f"{GREEN}✅ 자동 저장 완료! 언제든 게임을 재개할 수 있습니다.{RESET}")
        else:
            print(f"{YELLOW}⚠️ 자동 저장에 실패했지만 게임을 계속 진행합니다.{RESET}")
        
        # 백그라운드 학습 시작
        self._start_background_learning()
        
        # 게임 시스템과 통합
        if self.game_integrated:
            self._integrate_with_game_systems()
        
        # AI 소개 및 첫 만남
        self._ai_introduction_sequence()
        
        # 메인 게임 루프 시작
        self._main_game_loop()
    
    def _start_background_learning(self):
        """백그라운드 학습 프로세스 시작"""
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._background_learning_process, daemon=True)
        self.learning_thread.start()
        print(f"{GREEN}✅ AI 백그라운드 학습 시작{RESET}")
    
    def _background_learning_process(self):
        """백그라운드 학습 프로세스"""
        while self.learning_active:
            try:
                # 주기적으로 AI 학습 데이터 처리
                for ai_char in self.ai_companions:
                    char_name = ai_char['character_data']['basic_info']['name']
                    db = get_ai_database(char_name)
                    
                    # 최근 이벤트 분석 및 패턴 학습
                    recent_events = db.get_recent_learning_events(10)
                    if len(recent_events) > 5:
                        self._analyze_learning_patterns(char_name, recent_events)
                
                # 10초마다 학습 프로세스 실행
                time.sleep(10)
                
            except Exception as e:
                print(f"{RED}백그라운드 학습 오류: {e}{RESET}")
                time.sleep(5)
    
    def _analyze_learning_patterns(self, character_name: str, events: List[Dict]):
        """학습 패턴 분석"""
        # 여기서 실제 머신러닝 분석을 수행
        # 현재는 간단한 통계 분석만 구현
        success_rate = sum(1 for e in events if e.get('feedback_score', 0) > 0.5) / len(events)
        
        if success_rate > 0.8:
            print(f"{GREEN}🧠 {character_name}의 학습 성과가 우수합니다! (성공률: {success_rate:.1%}){RESET}")
        elif success_rate < 0.3:
            print(f"{YELLOW}📚 {character_name}이(가) 더 많은 학습이 필요합니다. (성공률: {success_rate:.1%}){RESET}")
    
    def _integrate_with_game_systems(self):
        """기존 게임 시스템과 완전 통합 - 안전성 강화"""
        if not self.game_integrated:
            print(f"{YELLOW}⚠️ 게임 시스템 미연동 모드로 실행됩니다.{RESET}")
            return
        
        try:
            # 기존 게임 클래스와 통합
            from main import DawnOfStellarGame
            
            print(f"{CYAN}🔗 게임 시스템과 통합 중...{RESET}")
            
            # 새로운 게임 인스턴스 생성 (AI 멀티플레이 모드)
            print(f"{CYAN}🔧 게임 인스턴스 생성 중...{RESET}")
            self.game_instance = DawnOfStellarGame()
            
            # 게임 인스턴스 완전 초기화
            print(f"{CYAN}⚙️ 게임 시스템 초기화 중...{RESET}")
            
            # 필수 시스템들이 없으면 초기화
            if not hasattr(self.game_instance, 'party_manager') or self.game_instance.party_manager is None:
                print(f"{YELLOW}⚠️ 파티 매니저가 없습니다. 기존 시스템을 사용합니다.{RESET}")
            
            if not hasattr(self.game_instance, 'world') or self.game_instance.world is None:
                print(f"{YELLOW}⚠️ 월드 시스템이 없습니다. 기존 시스템을 사용합니다.{RESET}")
            
            # process_action, show_inventory 등 핵심 메서드 확인
            required_methods = ['process_action', 'show_inventory', 'show_character_info', 'show_help', 'show_main_menu']
            missing_methods = []
            
            for method_name in required_methods:
                if not hasattr(self.game_instance, method_name):
                    missing_methods.append(method_name)
            
            if missing_methods:
                print(f"{RED}⚠️ 누락된 메서드들: {', '.join(missing_methods)}{RESET}")
                print(f"{YELLOW}게임이 정상 작동하지 않을 수 있습니다.{RESET}")
            else:
                print(f"{GREEN}✓ 모든 핵심 메서드 확인 완료{RESET}")
            
            # AI 멀티플레이어 모드 플래그 설정
            if hasattr(self.game_instance, 'ai_multiplayer_mode'):
                self.game_instance.ai_multiplayer_mode = True
                print(f"{GREEN}✓ AI 멀티플레이어 모드 활성화{RESET}")
            
            # 먼저 AI 캐릭터들을 실제 게임 캐릭터로 변환
            print(f"{CYAN}🔄 AI 캐릭터를 게임 캐릭터로 변환 중...{RESET}")
            self._convert_ai_to_game_characters()
            
            # 파티 매니저에 등록
            if hasattr(self.game_instance, 'party_manager'):
                self.party_manager = self.game_instance.party_manager
                print(f"{GREEN}✓ 파티 매니저 연동 완료{RESET}")
                
            # 전투 시스템 연동
            if hasattr(self.game_instance, 'combat_system'):
                self.combat_system = self.game_instance.combat_system
                print(f"{GREEN}✓ 전투 시스템 연동 완료{RESET}")
                
            # 월드 시스템 연동
            if hasattr(self.game_instance, 'world'):
                self.world = self.game_instance.world
                print(f"{GREEN}✓ 월드 시스템 연동 완료{RESET}")
                
            # 디스플레이 시스템 연동
            if hasattr(self.game_instance, 'display'):
                self.display = self.game_instance.display
                print(f"{GREEN}✓ 디스플레이 시스템 연동 완료{RESET}")
            
            print(f"{GREEN}✅ Dawn of Stellar 게임 시스템 완전 통합 완료{RESET}")
            
        except ImportError as e:
            print(f"{RED}❌ 게임 모듈 import 실패: {e}{RESET}")
            print(f"{YELLOW}⚠️ 독립 모드로 실행합니다.{RESET}")
            self.game_integrated = False
        except Exception as e:
            print(f"{RED}❌ 게임 시스템 통합 중 오류: {e}{RESET}")
            print(f"{YELLOW}⚠️ 독립 모드로 실행합니다.{RESET}")
            import traceback
            print(f"{YELLOW}상세 오류 정보:{RESET}")
            traceback.print_exc()
            self.game_integrated = False
    
    def _convert_ai_to_game_characters(self):
        """AI 캐릭터를 실제 게임 캐릭터로 변환"""
        if not GAME_MODULES_AVAILABLE:
            return
            
        converted_party = []
        
        # 플레이어 캐릭터 변환
        if self.player_character:
            player_char = Character(
                name=self.player_character['name'],
                character_class=self.player_character['class']
            )
            # 플레이어 캐릭터 속성 설정
            player_char.is_player = True
            player_char.is_ai_controlled = False
            
            # 기본 HP/MP 확인 및 초기화
            if not hasattr(player_char, 'current_hp') or player_char.current_hp <= 0:
                player_char.current_hp = player_char.max_hp
            if not hasattr(player_char, 'current_mp') or player_char.current_mp <= 0:
                player_char.current_mp = player_char.max_mp
                
            converted_party.append(player_char)
        
        # AI 동료들 변환
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            
            game_char = Character(
                name=basic['name'],
                character_class=basic['class']
            )
            
            # AI 캐릭터 속성 설정
            game_char.is_player = False
            game_char.is_ai_controlled = True
            
            # 기본 HP/MP 확인 및 초기화
            if not hasattr(game_char, 'current_hp') or game_char.current_hp <= 0:
                game_char.current_hp = game_char.max_hp
            if not hasattr(game_char, 'current_mp') or game_char.current_mp <= 0:
                game_char.current_mp = game_char.max_mp
            
            # AI 정보 저장 (게임 캐릭터에 AI 메타데이터 추가)
            game_char._ai_personality = basic['personality_type']
            game_char._ai_database = ai_char['database']
            game_char._is_ai_controlled = True
            
            converted_party.append(game_char)
        
        # 파티 매니저에 등록
        if hasattr(self.game_instance, 'party_manager'):
            self.game_instance.party_manager.members = converted_party
            print(f"{GREEN}✅ {len(converted_party)}명 파티를 게임에 등록했습니다{RESET}")
            
            # 캐릭터 목록도 별도 저장 (메인 게임 호환성)
            if hasattr(self.game_instance, 'characters'):
                self.game_instance.characters = converted_party
                print(f"{GREEN}✓ 캐릭터 목록도 game.characters에 저장했습니다{RESET}")
            
            # 현재 캐릭터 인덱스 설정
            if hasattr(self.game_instance, 'current_character_index'):
                self.game_instance.current_character_index = 0
                print(f"{GREEN}✓ 현재 캐릭터 인덱스 설정 완료{RESET}")
            
            # 스타팅 아이템 지급 + 공정 자동 장착 (클래식 플로우와 동일 보장)
            try:
                give_start = getattr(self.game_instance, "_give_basic_starting_items", None)
                auto_equip = getattr(self.game_instance, "_auto_equip_starting_items", None)
                if callable(give_start):
                    give_start()
                if callable(auto_equip):
                    auto_equip()
                else:
                    # 폴백: 장비 최적화 헬퍼 직접 호출 시도
                    try:
                        from game.equipment_helpers import optimize_all_equipment
                        from game.items import ItemDatabase
                        db = ItemDatabase()
                        pooled = []
                        for m in self.game_instance.party_manager.members:
                            inv = getattr(m, 'inventory', None)
                            if inv and hasattr(inv, 'items') and isinstance(inv.items, dict):
                                for item_name, qty in inv.items.items():
                                    obj = db.get_item(item_name)
                                    if obj:
                                        pooled.extend([obj] * int(max(1, qty)))
                        if pooled:
                            optimize_all_equipment(self.game_instance.party_manager.members, pooled, show_results=False)
                    except Exception:
                        pass
            except Exception as _e:
                print(f"{YELLOW}⚠️ 스타팅 장비 초기화 중 경고: {_e}{RESET}")

            # 파티 상태 확인
            print(f"{CYAN}🔍 파티 상태 확인:{RESET}")
            for i, char in enumerate(converted_party):
                print(f"  {i+1}. {char.name} ({char.character_class}) - HP: {char.current_hp}/{char.max_hp}")
        else:
            print(f"{RED}❌ party_manager를 찾을 수 없습니다!{RESET}")
    
    def _main_game_loop(self):
        """메인 게임 루프 - 실제 Dawn of Stellar 게임 실행"""
        if self.game_integrated and hasattr(self, 'game_instance'):
            print(f"\n{BRIGHT_GREEN}🎮 Dawn of Stellar AI 멀티플레이어 게임 시작!{RESET}")
            
            # 게임 시작 전 AI 모드 설정
            self.game_instance.ai_game_mode_enabled = True
            
            # AI 게임 모드 초기화
            try:
                from game.ai_game_mode import initialize_ai_game_mode
                initialize_ai_game_mode(self.game_instance.party_manager.members)
                print(f"{GREEN}✅ AI 게임 모드 초기화 완료{RESET}")
            except:
                print(f"{YELLOW}⚠️ AI 게임 모드 초기화 실패, 수동 모드로 진행{RESET}")
            
            # 실제 게임 시작 (던전 진입)
            try:
                # AI 멀티플레이어에서는 패시브 선택을 허용하되 AI 모드 선택은 건너뛰기
                print(f"{CYAN}🎯 AI 멀티플레이어 게임 초기화 중...{RESET}")
                print(f"{YELLOW}💡 패시브 효과를 선택하여 파티를 강화하세요!{RESET}")
                
                self.game_instance.start_adventure(
                    skip_passive_selection=False,  # 패시브 선택 허용 (파티 강화용)
                    skip_ai_mode_selection=True    # AI 모드 선택만 건너뛰기 (이미 설정됨)
                )
                
                # start_adventure 완료 후 실제 게임 루프 시작
                print(f"{GREEN}✅ 게임 초기화 완료! 게임 루프를 시작합니다...{RESET}")
                
                # 메서드 존재 여부 확인 및 호출
                main_loop_called = False
                
                if hasattr(self.game_instance, 'main_game_loop'):
                    print(f"{CYAN}🎮 main_game_loop() 메서드를 호출합니다...{RESET}")
                    self.game_instance.main_game_loop()
                    main_loop_called = True
                elif hasattr(self.game_instance, 'main_loop'):
                    print(f"{CYAN}🎮 main_loop() 메서드를 호출합니다...{RESET}")
                    self.game_instance.main_loop()
                    main_loop_called = True
                else:
                    print(f"{RED}❌ 게임 루프 메서드를 찾을 수 없습니다.{RESET}")
                    print(f"{YELLOW}사용 가능한 메서드들: {dir(self.game_instance)}{RESET}")
                
                if main_loop_called:
                    print(f"{GREEN}✅ 게임 루프가 완료되었습니다.{RESET}")
                    print(f"{CYAN}🎮 AI 멀티플레이어 모드로 돌아갑니다...{RESET}")
                    self._fallback_game_loop()  # 게임 종료 후 AI 모드로 복귀
                else:
                    print(f"{YELLOW}기본 게임 모드로 전환합니다.{RESET}")
                    self._fallback_game_loop()
                    
            except Exception as e:
                print(f"{RED}❌ AI 멀티플레이어 모드 오류: {e}{RESET}")
                print(f"{YELLOW}기본 게임 모드로 전환합니다.{RESET}")
                self._fallback_game_loop()
        else:
            print(f"\n{YELLOW}독립 모드로 AI 멀티플레이어 시뮬레이션을 실행합니다.{RESET}")
            self._fallback_game_loop()
    
    def _fallback_game_loop(self):
        """폴백 게임 루프 (독립 모드)"""
        print(f"\n{BRIGHT_WHITE}🎮 AI 멀티플레이어 시뮬레이션 모드{RESET}")
        print(f"{WHITE}실제 게임과 유사한 경험을 제공합니다.{RESET}")
        print(f"{YELLOW}💡 'help'를 입력하면 도움말을 볼 수 있습니다.{RESET}")
        
        while True:
            command = input(f"\n{CYAN}명령을 입력하세요: {RESET}").strip().lower()
            
            if command in ['quit', 'exit', '종료', 'q']:
                break
            elif command in ['help', '도움말', 'h']:
                self._show_help()
            elif command in ['status', '상태', 's']:
                self._show_party_status()
            elif command in ['talk', '대화', 't']:
                self._talk_with_ai()
            elif command in ['explore', '탐험', 'e']:
                if self.game_integrated and hasattr(self, 'game_instance') and self.game_instance:
                    print(f"{BRIGHT_WHITE}🗺️ 실제 게임으로 전환합니다...{RESET}")
                    try:
                        # 게임 인스턴스에 AI 캐릭터들 전달
                        if hasattr(self.game_instance, 'set_ai_companions'):
                            self.game_instance.set_ai_companions(self.ai_companions)
                        
                        # 실제 게임 실행
                        self.game_instance.run()
                        print(f"\n{GREEN}게임에서 돌아왔습니다. AI 멀티플레이어 모드로 복귀합니다.{RESET}")
                    except Exception as e:
                        print(f"{RED}❌ 게임 실행 중 오류: {e}{RESET}")
                        print(f"{YELLOW}독립 모드 탐험으로 대체합니다.{RESET}")
                        self._explore_with_ai()
                else:
                    self._explore_with_ai()
            elif command in ['combat', '전투', 'c']:
                self._simulate_combat()
            elif command in ['train', '훈련']:
                self._ai_training_session()
            elif command in ['game', '게임', 'start']:
                print(f"{CYAN}실제 게임 모드로 전환을 시도합니다...{RESET}")
                self._attempt_game_integration()
                break
            else:
                print(f"{RED}알 수 없는 명령입니다. 'help'를 입력해보세요.{RESET}")
        
        print(f"{GREEN}AI 멀티플레이어 세션을 종료합니다.{RESET}")
    
    def _attempt_game_integration(self):
        """게임 통합 재시도"""
        try:
            self.game_integrated = True
            self._integrate_with_game_systems()
            if self.game_integrated:
                self._main_game_loop()
            else:
                print(f"{RED}게임 통합에 실패했습니다.{RESET}")
        except Exception as e:
            print(f"{RED}게임 통합 시도 중 오류: {e}{RESET}")
    
    def _ai_introduction_sequence(self):
        """AI 소개 시퀀스"""
        print(f"\n{BRIGHT_CYAN}🎭 AI 동료들이 자기소개를 합니다!{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            personality = basic['personality_type']
            
            # 저장된 자기소개 대사가 있다면 사용, 없다면 AI 생성
            if ('social' in char_data and 
                'introduction_dialogue' in char_data['social'] and 
                char_data['social']['introduction_dialogue']):
                ai_intro = char_data['social']['introduction_dialogue']
            else:
                # AI가 자기소개 생성 (폴백)
                intro_context = f"{basic['name']}이(가) 새로운 파티원인 {self.player_character['name']}에게 첫 인사를 합니다."
                ai_intro = self.ai_engine.generate_ai_response(
                    basic['name'], personality, intro_context, "dialogue"
                )
            
            print(f"\n{CYAN}🤖 {basic['name']} ({basic['class']}):{RESET}")
            print(f"   {WHITE}'{ai_intro}'{RESET}")
            
            # 잠시 대기 (자연스러운 대화 흐름)
            time.sleep(1)
        
        print(f"\n{GREEN}환영합니다! 이제 함께 모험을 떠날 준비가 되었습니다.{RESET}")
    
    def _show_help(self):
        """도움말 표시"""
        print(f"\n{BRIGHT_WHITE}📖 AI 멀티플레이 도움말{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{WHITE}status (s)  - 파티 상태 확인{RESET}")
        print(f"{WHITE}talk (t)    - AI 동료와 대화{RESET}")
        print(f"{WHITE}explore (e) - 던전 탐험{RESET}")
        print(f"{WHITE}combat (c)  - 전투 시뮬레이션{RESET}")
        print(f"{WHITE}train       - AI 훈련 세션{RESET}")
        print(f"{WHITE}help (h)    - 이 도움말{RESET}")
        print(f"{WHITE}quit (q)    - 게임 종료{RESET}")
    
    def _show_party_status(self):
        """파티 상태 표시"""
        print(f"\n{BRIGHT_WHITE}👥 파티 상태{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        # 플레이어
        print(f"{GREEN}🎮 {self.player_character['name']} ({self.player_character['class']}){RESET}")
        print(f"   레벨: {self.player_character.get('level', 1)} | 상태: 건강")
        
        # AI 동료들
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            db = ai_char['database']
            stats = db.get_statistics()
            
            relationship = db.get_relationship("플레이어")
            trust = relationship.get('trust_level', 0.5) if relationship else 0.5
            
            print(f"\n{CYAN}🤖 {basic['name']} ({basic['class']}){RESET}")
            print(f"   성격: {basic['personality_type']}")
            print(f"   신뢰도: {trust:.2f}/1.00")
            print(f"   학습 이벤트: {stats['total_learning_events']}개")
            print(f"   게임 지식: {stats['total_knowledge_items']}개")
    
    def _talk_with_ai(self):
        """AI와 대화 - 커서 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            # AI 선택 옵션 생성
            options = []
            descriptions = []
            
            for ai_char in self.ai_companions:
                basic = ai_char['character_data']['basic_info']
                options.append(f"💬 {basic['name']} ({basic['class']})")
                descriptions.append(f"성격: {basic['personality_type']} | AI와 대화를 나눕니다")
            
            if not options:
                print(f"{RED}대화할 AI 동료가 없습니다.{RESET}")
                return
            
            menu = CursorMenu(
                title=f"{BRIGHT_WHITE}💬 AI 동료와 대화{RESET}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            choice = menu.run()
            
            if choice is not None and 0 <= choice < len(self.ai_companions):
                selected_ai = self.ai_companions[choice]
                self._conversation_with_ai(selected_ai)
            elif choice is None:
                print(f"{YELLOW}대화가 취소되었습니다.{RESET}")
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print(f"\n{BRIGHT_WHITE}💬 AI 동료와 대화{RESET}")
            print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            
            # AI 선택
            print("대화할 AI를 선택하세요:")
            for i, ai_char in enumerate(self.ai_companions, 1):
                basic = ai_char['character_data']['basic_info']
                print(f"{i}. {basic['name']} ({basic['personality_type']})")
            
            try:
                choice = int(input("선택 (1-3): ")) - 1
                if 0 <= choice < len(self.ai_companions):
                    selected_ai = self.ai_companions[choice]
                    self._conversation_with_ai(selected_ai)
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
            except:
                print(f"{RED}잘못된 입력입니다.{RESET}")
    
    def _conversation_with_ai(self, ai_char: Dict):
        """특정 AI와 대화"""
        char_data = ai_char['character_data']
        basic = char_data['basic_info']
        
        print(f"\n{CYAN}💬 {basic['name']}과(와)의 대화{RESET}")
        print(f"{WHITE}대화를 끝내려면 'end'를 입력하세요.{RESET}")
        
        while True:
            user_input = input(f"\n{GREEN}당신: {RESET}").strip()
            
            if user_input.lower() in ['end', '끝', '종료']:
                print(f"{CYAN}{basic['name']}: 나중에 또 이야기해요!{RESET}")
                break
            
            if not user_input:
                continue
            
            # AI 응답 생성
            context = f"플레이어가 '{user_input}'라고 말했습니다."
            ai_response = self.ai_engine.generate_ai_response(
                basic['name'], basic['personality_type'], context, "dialogue"
            )
            
            print(f"{CYAN}{basic['name']}: {ai_response}{RESET}")
            
            # 관계 업데이트 (긍정적 상호작용)
            self.ai_engine.update_character_relationship(
                basic['name'], "casual_conversation", user_input, 0.6
            )
    
    def _explore_with_ai(self):
        """AI와 함께 탐험"""
        print(f"\n{BRIGHT_WHITE}🗺️ 던전 탐험{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        # 탐험 시나리오
        scenarios = [
            "앞에 갈래길이 나타났습니다. 어느 길로 갈까요?",
            "수상한 보물상자를 발견했습니다.",
            "멀리서 적의 소리가 들립니다.",
            "신비한 마법진이 바닥에 그려져 있습니다.",
            "좁은 통로에 함정이 있는 것 같습니다."
        ]
        
        import random
        scenario = random.choice(scenarios)
        
        print(f"{WHITE}상황: {scenario}{RESET}")
        
        # AI들의 의견 수집
        print(f"\n{CYAN}AI 동료들의 의견:{RESET}")
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            
            ai_opinion = self.ai_engine.generate_ai_response(
                basic['name'], basic['personality_type'], scenario, "exploration"
            )
            
            print(f"  {basic['name']}: {ai_opinion}")
            
            # 학습 데이터 저장
            self.ai_engine.update_character_relationship(
                basic['name'], "exploration_advice", scenario, 0.5
            )
        
        print(f"\n{GREEN}AI 동료들과 함께 신중하게 탐험을 계속합니다.{RESET}")
    
    def _simulate_combat(self):
        """전투 시뮬레이션"""
        print(f"\n{BRIGHT_WHITE}⚔️ 전투 시뮬레이션{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        enemies = ["고블린", "오크", "스켈레톤"]
        import random
        enemy = random.choice(enemies)
        
        print(f"{RED}⚠️ {enemy}이(가) 나타났습니다!{RESET}")
        
        # AI들의 전투 전략
        print(f"\n{CYAN}AI 동료들의 전투 준비:{RESET}")
        
        combat_actions = ["공격", "방어", "스킬 사용", "마법", "치유"]
        
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            
            # 게임 상태 시뮬레이션
            game_state = {
                'hp': random.randint(60, 100),
                'max_hp': 100,
                'mp': random.randint(20, 50),
                'max_mp': 50,
                'brv': random.randint(100, 300),
                'enemies': [enemy]
            }
            
            # AI 의사결정
            decision = self.ai_engine.make_strategic_decision(
                basic['name'], basic['personality_type'], game_state, combat_actions
            )
            
            print(f"  {basic['name']}: {decision}을(를) 사용합니다!")
            
            # 전투 결과 피드백 (임의)
            success_rate = random.uniform(0.3, 0.9)
            self.ai_engine.update_character_relationship(
                basic['name'], "combat_action", decision, success_rate
            )
        
        print(f"\n{GREEN}✅ 전투에서 승리했습니다!{RESET}")
        print(f"{CYAN}AI 동료들이 전투 경험을 학습했습니다.{RESET}")
    
    def _ai_training_session(self):
        """AI 훈련 세션"""
        print(f"\n{BRIGHT_WHITE}🧠 AI 훈련 세션{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            db = ai_char['database']
            
            # 학습 통계 표시
            stats = db.get_statistics()
            print(f"\n{CYAN}{basic['name']} 훈련 결과:{RESET}")
            print(f"  총 학습 이벤트: {stats['total_learning_events']}")
            print(f"  게임 지식: {stats['total_knowledge_items']}")
            print(f"  행동 패턴: {stats['total_behavioral_patterns']}")
            
            relationship = db.get_relationship("플레이어")
            if relationship:
                print(f"  플레이어 신뢰도: {relationship['trust_level']:.2f}")
        
        print(f"\n{GREEN}✅ AI 훈련 세션 완료!{RESET}")
    
    def get_saved_ai_parties(self):
        """저장된 AI 파티 목록 가져오기"""
        import os
        import json
        from datetime import datetime
        
        parties_dir = "ai_parties"
        if not os.path.exists(parties_dir):
            os.makedirs(parties_dir)
            return []
        
        parties = []
        try:
            for filename in os.listdir(parties_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(parties_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            party_data = json.load(f)
                            parties.append(party_data)
                    except Exception as e:
                        print(f"{YELLOW}⚠️ 파티 파일 로드 실패: {filename} - {str(e)}{RESET}")
                        continue
            
            # 생성일 기준 정렬 (최신순)
            parties.sort(key=lambda x: x.get('created', ''), reverse=True)
            return parties
            
        except Exception as e:
            print(f"{RED}❌ 파티 목록 로드 실패: {str(e)}{RESET}")
            return []
    
    def save_ai_party(self, party_members, party_name=None):
        """AI 파티를 파일로 저장"""
        import os
        import json
        from datetime import datetime
        
        # 파티명이 없으면 자동 생성
        if not party_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            party_name = f"AI파티_{timestamp}"
        
        # 저장 디렉토리 생성
        parties_dir = "ai_parties"
        if not os.path.exists(parties_dir):
            os.makedirs(parties_dir)
        
        # 파티 데이터 구성
        party_data = {
            "name": party_name,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "members": party_members,
            "version": "1.0"
        }
        
        # 파일명 생성 (안전한 파일명)
        safe_name = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in party_name)
        filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = os.path.join(parties_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(party_data, f, ensure_ascii=False, indent=2)
            
            print(f"{GREEN}✅ AI 파티가 저장되었습니다: {party_name}{RESET}")
            return True
            
        except Exception as e:
            print(f"{RED}❌ AI 파티 저장 실패: {str(e)}{RESET}")
            return False
    
    def start_adventure_with_party(self, party_members):
        """저장된 파티로 게임 시작"""
        print(f"\n{CYAN}🎮 게임을 시작합니다...{RESET}")
        
        try:
            # 파티 멤버들을 게임 캐릭터로 변환
            game_characters = []
            for member_data in party_members:
                # 게임 캐릭터 객체 생성
                character = self.convert_to_game_character(member_data)
                game_characters.append(character)
            
            # 게임 시작
            return self.start_adventure_with_characters(game_characters)
            
        except Exception as e:
            print(f"{RED}❌ 게임 시작 실패: {str(e)}{RESET}")
            import traceback
            traceback.print_exc()
            return None
    
    def convert_to_game_character(self, member_data):
        """AI 파티 멤버 데이터를 게임 캐릭터 객체로 변환"""
        from game.character import Character
        
        # 캐릭터 기본 정보
        name = member_data.get('name', '이름 없음')
        job = member_data.get('job', '전사')  # 기본 직업
        
        # 게임 캐릭터 생성
        character = Character(name=name, character_class=job)
        
        # 플레이어/AI 구분 설정
        character.is_player = member_data.get('is_player', False)
        
        # AI 관련 설정
        if 'personality' in member_data:
            character.ai_personality = member_data['personality']
        if 'behavior_style' in member_data:
            character.ai_behavior_style = member_data['behavior_style']
        if 'dialogue_style' in member_data:
            character.ai_dialogue_style = member_data['dialogue_style']
            
        return character
        
    def start_adventure_with_characters(self, game_characters):
        """게임 캐릭터들로 실제 게임 시작"""
        print(f"\n{BRIGHT_GREEN}🎮 실제 게임을 시작합니다!{RESET}")
        
        try:
            # 게임 인스턴스 생성
            if not hasattr(self, 'game_instance') or not self.game_instance:
                from main import DawnOfStellarGame
                self.game_instance = DawnOfStellarGame()
            
            # AI 모드 설정
            self.game_instance.ai_game_mode_enabled = True
            
            # � 색상 시스템 강제 활성화
            try:
                import game.color_text as color_module
                color_module.COLOR_DISABLED = False
                print("")  # 로그 제거
            except Exception as e:
                pass  # 조용히 실패 처리
            
            # 캐릭터 검증 및 초기화
            print(f"\n{CYAN}🔍 캐릭터 상태 검증 중...{RESET}")
            for character in game_characters:
                # 기본 속성 확인 및 설정
                if not hasattr(character, 'current_hp'):
                    character.current_hp = character.max_hp
                if not hasattr(character, 'current_mp'):
                    character.current_mp = character.max_mp
                    
                # 플레이어/AI 구분 설정
                if not hasattr(character, 'is_player'):
                    character.is_player = False
                if not hasattr(character, 'is_ai_controlled'):
                    character.is_ai_controlled = not character.is_player
                    
                # 기본 인벤토리 초기화
                if not hasattr(character, 'inventory'):
                    from game.item_system import Inventory
                    character.inventory = Inventory()
                
                print(f"  ✓ {character.name}: HP {character.current_hp}/{character.max_hp}, MP {character.current_mp}/{character.max_mp}")
            
            # 게임 투입 전 특성/패시브 선택
            print(f"\n{CYAN}🌟 게임 시작 전 특성과 패시브를 선택해주세요!{RESET}")
            self._setup_traits_and_passives(game_characters)
            
            # 파티 설정 및 게임 인스턴스 설정
            self.game_instance.party_manager.members = game_characters
            
            # 플레이어 캐릭터가 있는지 확인하고 첫 번째 플레이어를 주인공으로 설정
            player_character = None
            for character in game_characters:
                if getattr(character, 'is_player', False):
                    player_character = character
                    break
            
            if player_character:
                # 게임의 플레이어 설정
                if hasattr(self.game_instance, 'player'):
                    self.game_instance.player = player_character
                print(f"  ✓ 플레이어 캐릭터: {player_character.name}")
            
            # AI 제어 플래그 설정
            for character in game_characters:
                if not getattr(character, 'is_player', False):
                    character.is_ai_controlled = True
                else:
                    character.is_ai_controlled = False
            
            # AI 게임 모드 초기화
            try:
                from game.ai_game_mode import ai_game_mode_manager
                ai_game_mode_manager.set_enabled(True)
                # AI 게임 모드 로그 제거
            except:
                pass  # 조용히 실패 처리
            
            # 실제 게임 시작 (던전 진입)
            try:
                self.game_instance.start_adventure(
                    skip_passive_selection=True,  # 패시브 선택 건너뛰기
                    skip_ai_mode_selection=True   # AI 모드 선택 건너뛰기 (이미 설정됨)
                )
                
                # start_adventure 완료 후 실제 게임 루프 시작
                print(f"{GREEN}✅ 게임 초기화 완료! 게임 루프를 시작합니다...{RESET}")
                
                # 메서드 존재 여부 확인 및 호출
                main_loop_called = False
                
                if hasattr(self.game_instance, 'main_game_loop'):
                    print(f"{CYAN}🎮 main_game_loop() 메서드를 호출합니다...{RESET}")
                    self.game_instance.main_game_loop()
                    main_loop_called = True
                elif hasattr(self.game_instance, 'main_loop'):
                    print(f"{CYAN}🎮 main_loop() 메서드를 호출합니다...{RESET}")
                    self.game_instance.main_loop()
                    main_loop_called = True
                else:
                    print(f"{RED}❌ 게임 루프 메서드를 찾을 수 없습니다.{RESET}")
                    print(f"{YELLOW}사용 가능한 메서드들: {[method for method in dir(self.game_instance) if 'loop' in method.lower()]}{RESET}")
                
                if main_loop_called:
                    print(f"{GREEN}✅ 게임 루프가 완료되었습니다.{RESET}")
                    
                    # AI 멀티플레이어 모드 저장 처리
                    print(f"\n{CYAN}💾 AI 멀티플레이어 게임 저장 중...{RESET}")
                    self._handle_ai_multiplayer_save()
                    
                else:
                    # 대안: 게임 인스턴스가 실행 가능한 다른 메서드들 찾기
                    print(f"{YELLOW}🔍 게임 실행을 위한 대체 메서드를 찾는 중...{RESET}")
                    if hasattr(self.game_instance, 'run'):
                        print(f"{CYAN}🎮 run() 메서드를 호출합니다...{RESET}")
                        self.game_instance.run()
                    elif hasattr(self.game_instance, 'start'):
                        print(f"{CYAN}🎮 start() 메서드를 호출합니다...{RESET}")
                        self.game_instance.start()
                    else:
                        print(f"{RED}❌ 실행 가능한 게임 메서드를 찾을 수 없습니다.{RESET}")
                        return None
                
            except Exception as e:
                print(f"{RED}❌ 게임 시작 중 오류: {str(e)}{RESET}")
                import traceback
                traceback.print_exc()
                return None
                
        except Exception as e:
            print(f"{RED}❌ 게임 인스턴스 생성 실패: {str(e)}{RESET}")
            import traceback
            traceback.print_exc()
            return None
        
        return True
    
    def _handle_ai_multiplayer_save(self):
        """AI 멀티플레이어 모드 저장 처리"""
        try:
            if not hasattr(self, 'game_instance') or not self.game_instance:
                print(f"{YELLOW}⚠️ 게임 인스턴스가 없어 저장을 건너뜁니다.{RESET}")
                return
            
            # 플레이어 캐릭터 찾기 (한 명만 있어야 함)
            player_character = None
            ai_companions = []
            
            if hasattr(self.game_instance, 'party_manager') and self.game_instance.party_manager.members:
                for character in self.game_instance.party_manager.members:
                    if getattr(character, 'is_player', False):
                        player_character = character
                    else:
                        ai_companions.append(character)
            
            if player_character:
                print(f"{GREEN}🎮 플레이어 캐릭터 '{player_character.name}' 저장 중...{RESET}")
                
                # 메인 게임의 저장 시스템 사용 (플레이어 캐릭터만)
                if hasattr(self.game_instance, 'save_game'):
                    # 임시로 파티를 플레이어만으로 설정
                    original_members = self.game_instance.party_manager.members
                    self.game_instance.party_manager.members = [player_character]
                    
                    try:
                        # 플레이어 캐릭터 세이브 (기존 게임 시스템 사용)
                        self.game_instance.save_game()
                        print(f"  ✓ 플레이어 캐릭터가 메인 세이브파일에 저장되었습니다")
                    finally:
                        # 파티 복구
                        self.game_instance.party_manager.members = original_members
                else:
                    print(f"{YELLOW}⚠️ 게임 저장 메서드를 찾을 수 없습니다{RESET}")
            
            # AI 동료들은 별도 저장하지 않음 (매번 새로 생성)
            if ai_companions:
                print(f"{CYAN}🤖 AI 동료 {len(ai_companions)}명은 다음 게임에서 새로 생성됩니다{RESET}")
                for companion in ai_companions:
                    print(f"  - {companion.name} ({companion.character_class})")
            
            print(f"{GREEN}✅ AI 멀티플레이어 저장 완료!{RESET}")
            print(f"{BRIGHT_YELLOW}💡 다음 게임 시 같은 플레이어 캐릭터로 새로운 AI 동료들과 모험하세요!{RESET}")
            
        except Exception as e:
            print(f"{RED}❌ AI 멀티플레이어 저장 중 오류: {e}{RESET}")
            import traceback
            traceback.print_exc()
    
    def _load_existing_ai_party(self):
        """기존 AI 파티 불러오기"""
        print(f"\n{CYAN}=== 기존 AI 파티 불러오기 ==={RESET}")
        
        # 저장된 AI 파티 목록 확인
        ai_parties = self.get_saved_ai_parties()
        
        if not ai_parties:
            print(f"{YELLOW}💡 저장된 AI 파티가 없습니다.{RESET}")
            print(f"{CYAN}새로운 AI 파티를 생성하세요!{RESET}")
            input(f"\n{YELLOW}엔터를 눌러서 돌아가기...{RESET}")
            return None
        
        print(f"\n{CYAN}📋 저장된 AI 파티 목록:{RESET}")
        for i, party_info in enumerate(ai_parties, 1):
            party_name = party_info['name']
            members = party_info['members']
            
            # 플레이어와 AI 구분
            player_count = sum(1 for member in members if member.get('is_player', False))
            ai_count = len(members) - player_count
            
            member_description = f"플레이어 {player_count}명 + AI {ai_count}명"
            created_date = party_info.get('created', '날짜 미상')
            print(f"{GREEN}{i}.{RESET} {party_name} ({member_description}) - {created_date}")
        
        print(f"{GREEN}0.{RESET} 돌아가기")
        
        try:
            choice = int(safe_korean_input(f"\n{CYAN}불러올 파티를 선택하세요: {RESET}"))
            
            if choice == 0:
                return None
            
            if 1 <= choice <= len(ai_parties):
                selected_party = ai_parties[choice - 1]
                print(f"\n{GREEN}✅ '{selected_party['name']}' 파티를 불러왔습니다!{RESET}")
                
                # 파티 멤버 정보 표시
                print(f"\n{CYAN}📋 파티 구성원:{RESET}")
                for i, member in enumerate(selected_party['members'], 1):
                    name = member.get('name', f'멤버{i}')
                    job = member.get('job', '직업 미지정')
                    gender = member.get('gender', '성별 미지정')
                    
                    # 플레이어와 AI 구분
                    if member.get('is_player', False):
                        member_type = f"{BRIGHT_WHITE}🎮 플레이어{RESET}"
                    else:
                        member_type = f"{CYAN}🤖 AI{RESET}"
                    
                    print(f"  {GREEN}{i}.{RESET} {member_type} {name} ({job}) - {gender}")
                
                # 게임 시작 여부 확인
                print(f"\n{CYAN}🎮 이 파티로 게임을 시작하시겠습니까?{RESET}")
                start_choice = safe_korean_input(f"{GREEN}y{RESET}/n: ").lower()
                
                if start_choice == 'y' or start_choice == 'yes' or start_choice == '예':
                    # 게임 시작
                    return self.start_adventure_with_party(selected_party['members'])
                else:
                    return None
            else:
                print(f"{RED}❌ 잘못된 선택입니다.{RESET}")
                return None
                
        except (ValueError, KeyboardInterrupt):
            print(f"{YELLOW}🚫 취소되었습니다.{RESET}")
            return None
    
    def _create_custom_ai_party(self):
        """커스텀 AI 파티 생성"""
        print(f"\n{MAGENTA}🎭 커스텀 AI 파티 생성{RESET}")
        
        # 대화형 AI 캐릭터 생성
        custom_party = []
        for i in range(3):
            print(f"\n{CYAN}AI 동료 {i+1} 생성:{RESET}")
            ai_char = self.ai_creator.create_ai_character_for_multiplayer()
            custom_party.append(ai_char)
            
            # 간단한 프로필 표시
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            print(f"✅ {basic['name']} ({basic['class']}, {basic['personality_type']}) 생성됨")
        
        # 생성된 파티로 게임 시작 여부 확인
        start_game = input(f"\n이 파티로 게임을 시작하시겠습니까? (y/n): ").strip().lower()
        if start_game in ['y', 'yes', '네', '']:
            player_char = self._create_or_select_player_character()
            if player_char:
                self._start_game_with_ai_party(player_char, custom_party, [])
    
    def _manage_ai_characters(self):
        """AI 캐릭터 관리 - 커서 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "📋 AI 캐릭터 목록 보기",
                "🔍 AI 캐릭터 상세 정보",
                "🗑️ AI 캐릭터 삭제",
                "🔄 AI 학습 데이터 초기화"
            ]
            
            descriptions = [
                "생성된 모든 AI 캐릭터들의 기본 정보를 확인합니다",
                "특정 AI 캐릭터의 상세한 프로필과 학습 정보를 봅니다",
                "선택한 AI 캐릭터를 완전히 삭제합니다 (개발 중)",
                "AI의 학습 데이터를 초기화하여 처음 상태로 되돌립니다 (개발 중)"
            ]
            
            menu = CursorMenu(
                title=f"{CYAN}👥 AI 캐릭터 관리{RESET}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            choice = menu.run()
            
            if choice is None:
                return
            elif choice == 0:
                self._list_ai_characters()
            elif choice == 1:
                self._show_ai_character_details()
            elif choice == 2:
                print(f"{RED}AI 캐릭터 삭제 기능은 개발 중입니다.{RESET}")
            elif choice == 3:
                print(f"{RED}학습 데이터 초기화 기능은 개발 중입니다.{RESET}")
                
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print(f"\n{CYAN}👥 AI 캐릭터 관리{RESET}")
            print("1. AI 캐릭터 목록 보기")
            print("2. AI 캐릭터 상세 정보")
            print("3. AI 캐릭터 삭제")
            print("4. AI 학습 데이터 초기화")
            
            choice = input("선택 (1-4): ").strip()
            
            if choice == "1":
                self._list_ai_characters()
            elif choice == "2":
                self._show_ai_character_details()
            elif choice == "3":
                print(f"{RED}AI 캐릭터 삭제 기능은 개발 중입니다.{RESET}")
            elif choice == "4":
                print(f"{RED}학습 데이터 초기화 기능은 개발 중입니다.{RESET}")
    
    def _list_ai_characters(self):
        """AI 캐릭터 목록"""
        characters = preset_manager.list_available_presets()
        print(f"\n{WHITE}📋 저장된 AI 캐릭터 ({len(characters)}명):{RESET}")
        
        for char_name in characters:
            char_data = preset_manager.load_character_preset(char_name)
            if char_data:
                basic = char_data['basic_info']
                print(f"  {basic['name']} - {basic['class']} ({basic['personality_type']})")
    
    def _show_ai_character_details(self):
        """AI 캐릭터 상세 정보 - 커서 메뉴"""
        characters = preset_manager.list_available_presets()
        if not characters:
            print(f"{RED}저장된 AI 캐릭터가 없습니다.{RESET}")
            return
        
        try:
            from game.cursor_menu_system import CursorMenu
            
            # 캐릭터 옵션과 설명 생성
            options = []
            descriptions = []
            
            for char_name in characters:
                char_data = preset_manager.load_character_preset(char_name)
                if char_data:
                    basic = char_data['basic_info']
                    options.append(f"🎭 {basic['name']} ({basic['class']})")
                    descriptions.append(f"성격: {basic['personality_type']} | 상세 정보를 확인합니다")
                else:
                    options.append(f"❓ {char_name}")
                    descriptions.append("데이터 로드 오류")
            
            menu = CursorMenu(
                title=f"{CYAN}AI 캐릭터 상세 정보{RESET}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            choice = menu.run()
            
            if choice is not None and 0 <= choice < len(characters):
                char_name = characters[choice]
                char_data = preset_manager.load_character_preset(char_name)
                db = get_ai_database(char_name)
                
                # 상세 프로필 표시
                if char_data:
                    basic = char_data['basic_info']
                    stats = db.get_statistics()
                    
                    print(f"\n{BRIGHT_CYAN}📋 {basic['name']} 상세 프로필{RESET}")
                    print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
                    print(f"  📛 이름: {basic['name']}")
                    print(f"  ⚔️ 직업: {basic['class']}")
                    print(f"  🎭 성격: {basic['personality_type']}")
                    print(f"  🗣️ 말투: {basic.get('speech_style', '보통')}")
                    print(f"  📊 학습 이벤트: {stats['total_learning_events']}개")
                    print(f"  🧠 게임 지식: {stats['total_knowledge_items']}개")
                    print(f"  🤝 관계 데이터: {stats['total_relationships']}개")
                    print(f"  ⚡ 행동 패턴: {stats['total_behavioral_patterns']}개")
                    
                    input(f"\n{YELLOW}확인하려면 Enter를 누르세요...{RESET}")
                else:
                    print(f"{RED}캐릭터 데이터를 불러올 수 없습니다.{RESET}")
            elif choice is None:
                pass  # 취소됨
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print("상세 정보를 볼 캐릭터:")
            for i, char_name in enumerate(characters, 1):
                print(f"{i}. {char_name}")
            
            try:
                choice = int(input("선택: ")) - 1
                if 0 <= choice < len(characters):
                    char_name = characters[choice]
                    char_data = preset_manager.load_character_preset(char_name)
                    db = get_ai_database(char_name)
                    
                    # 상세 프로필 표시 (기존 방식)
                    if char_data:
                        basic = char_data['basic_info']
                        stats = db.get_statistics()
                        
                        print(f"\n{BRIGHT_CYAN}📋 {basic['name']} 상세 프로필{RESET}")
                        print(f"  이름: {basic['name']}")
                        print(f"  직업: {basic['class']}")
                        print(f"  성격: {basic['personality_type']}")
                        print(f"  학습 이벤트: {stats['total_learning_events']}개")
                        
            except:
                print(f"{RED}잘못된 선택입니다.{RESET}")
    
    def _ai_training_mode(self):
        """AI 훈련 모드 - 커서 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "⚡ 실시간 훈련 시작",
                "🌙 야간 집중 훈련",
                "📊 훈련 통계 보기"
            ]
            
            descriptions = [
                "현재 실행 중인 백그라운드 실시간 훈련 상태를 확인합니다",
                "고강도 집중 훈련 모드를 시작합니다 (개발 중)",
                "AI들의 학습 진행도와 성과를 상세히 확인합니다"
            ]
            
            menu = CursorMenu(
                title=f"{YELLOW}🧠 AI 훈련 모드{RESET}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            choice = menu.run()
            
            if choice is None:
                return
            elif choice == 0:
                print(f"{GREEN}실시간 훈련이 백그라운드에서 이미 실행 중입니다.{RESET}")
            elif choice == 1:
                print(f"{BLUE}야간 집중 훈련 기능은 개발 중입니다.{RESET}")
            elif choice == 2:
                self._show_training_statistics()
                
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print(f"\n{YELLOW}🧠 AI 훈련 모드{RESET}")
            print("1. 실시간 훈련 시작")
            print("2. 야간 집중 훈련")
            print("3. 훈련 통계 보기")
            
            choice = input("선택 (1-3): ").strip()
            
            if choice == "1":
                print(f"{GREEN}실시간 훈련이 백그라운드에서 이미 실행 중입니다.{RESET}")
            elif choice == "2":
                print(f"{BLUE}야간 집중 훈련 기능은 개발 중입니다.{RESET}")
            elif choice == "3":
                self._show_training_statistics()
    
    def _show_training_statistics(self):
        """훈련 통계 표시"""
        if not self.ai_companions:
            print(f"{RED}활성화된 AI 동료가 없습니다.{RESET}")
            return
        
        print(f"\n{WHITE}📊 AI 훈련 통계:{RESET}")
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            db = ai_char['database']
            stats = db.get_statistics()
            
            print(f"\n{CYAN}{basic['name']}:{RESET}")
            print(f"  학습 이벤트: {stats['total_learning_events']}")
            print(f"  관계 데이터: {stats['total_relationships']}")
            print(f"  게임 지식: {stats['total_knowledge_items']}")
            print(f"  행동 패턴: {stats['total_behavioral_patterns']}")
    
    def _settings_menu(self):
        """설정 메뉴 - 커서 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "🤖 EXAONE 모델 설정",
                "📚 학습 설정",
                "🎨 디스플레이 설정"
            ]
            
            descriptions = [
                "EXAONE 3.5 언어모델의 설정을 조정합니다 (개발 중)",
                "AI 학습 속도, 빈도, 방식 등을 설정합니다 (개발 중)",
                "화면 표시, 색상, 애니메이션 등을 조정합니다 (개발 중)"
            ]
            
            menu = CursorMenu(
                title=f"{WHITE}⚙️ 설정{RESET}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            choice = menu.run()
            
            if choice is None:
                return
            elif choice == 0:
                print(f"{BLUE}EXAONE 모델 설정은 개발 중입니다.{RESET}")
            elif choice == 1:
                print(f"{BLUE}학습 설정은 개발 중입니다.{RESET}")
            elif choice == 2:
                print(f"{BLUE}디스플레이 설정은 개발 중입니다.{RESET}")
                
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print(f"\n{WHITE}⚙️ 설정{RESET}")
            print("1. EXAONE 모델 설정")
            print("2. 학습 설정")  
            print("3. 디스플레이 설정")
            
            choice = input("선택 (1-3): ").strip()
            
            if choice == "1":
                print(f"{BLUE}EXAONE 모델 설정은 개발 중입니다.{RESET}")
            elif choice == "2":
                print(f"{BLUE}학습 설정은 개발 중입니다.{RESET}")
            elif choice == "3":
                print(f"{BLUE}디스플레이 설정은 개발 중입니다.{RESET}")
    
    def _cleanup_and_exit(self):
        """정리 및 종료"""
        self.learning_active = False
        if self.learning_thread and self.learning_thread.is_alive():
            print(f"{YELLOW}백그라운드 학습 중단 중...{RESET}")
            self.learning_thread.join(timeout=2)
        
        print(f"{GREEN}AI 멀티플레이 시스템 정리 완료{RESET}")
    
    def _setup_traits_and_passives(self, game_characters):
        """게임 투입 전 특성과 패시브 선택"""
        try:
            print(f"\n{BRIGHT_WHITE}🌟 특성 및 패시브 효과 선택{RESET}")
            print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            
            # 디버그: 캐릭터 목록 확인
            print(f"디버그: 총 {len(game_characters)}명의 캐릭터")
            for i, char in enumerate(game_characters):
                # Character 객체의 is_player 속성 확인
                is_player = getattr(char, 'is_player', False)
                print(f"  {i+1}. {char.name} ({char.character_class}) - 플레이어: {is_player}")
            
            # 1. 플레이어 특성 선택 (수동)
            player_characters = [char for char in game_characters if getattr(char, 'is_player', False)]
            print(f"디버그: {len(player_characters)}명의 플레이어 캐릭터 발견")
            
            for i, character in enumerate(player_characters, 1):
                print(f"\n{BRIGHT_CYAN}👤 플레이어 {i}: {character.name} - 특성 선택{RESET}")
                # 플레이어는 직접 선택
                self._select_character_traits(character, is_player=True, allow_manual=True)
            
            # 2. AI 동료 특성 자동 선택
            ai_companions = [char for char in game_characters if not getattr(char, 'is_player', False)]
            print(f"디버그: {len(ai_companions)}명의 AI 동료 발견")
            
            for i, character in enumerate(ai_companions, 1):
                print(f"\n{CYAN}🤖 AI 동료 {i}: {character.name} - 자동 특성 선택 중...{RESET}")
                # AI는 자동 선택
                try:
                    if hasattr(character, 'available_traits'):
                        character.passive_traits = []
                    print(f"{GREEN}✅ {character.name} 기본 설정 완료{RESET}")
                except:
                    print(f"{YELLOW}⚠️ {character.name} 기본 설정 적용{RESET}")
            
            # 3. 패시브 효과는 게임 내에서 선택
            print(f"\n{YELLOW}🌟 패시브 효과는 게임 시작 후 선택할 수 있습니다.{RESET}")
            
            print(f"\n{GREEN}✅ 모든 설정이 완료되었습니다! 게임을 시작합니다.{RESET}")
            
        except Exception as e:
            print(f"{RED}❌ 특성/패시브 선택 중 오류: {e}{RESET}")
            print(f"{YELLOW}⚠️ 기본 설정으로 게임을 시작합니다.{RESET}")
            import traceback
            traceback.print_exc()
    
    def _select_character_traits(self, character, is_player=False, allow_manual=False):
        """개별 캐릭터 특성 선택"""
        try:
            # 특성 시스템이 있는지 확인
            if not GAME_MODULES_AVAILABLE:
                print(f"{YELLOW}⚠️ 특성 시스템을 사용할 수 없습니다. 기본 설정을 사용합니다.{RESET}")
                return
            
            from game.character import CharacterClassManager
            
            # 직업별 추천 특성 가져오기
            available_traits = CharacterClassManager.get_class_traits(character.character_class)
            
            if not available_traits:
                print(f"{YELLOW}💡 {character.name}에게 사용 가능한 특성이 없습니다.{RESET}")
                return
            
            # 캐릭터에 특성 정보 설정
            character.available_traits = available_traits
            
            if is_player:
                # 플레이어는 항상 직접 선택
                print(f"\n{CYAN}📋 {character.name}의 특성을 선택해주세요:{RESET}")
                self._manual_trait_selection_cursor(character)
            elif allow_manual:
                # AI 동료도 수동/자동 선택 가능
                selection_mode = self._ask_trait_selection_mode(character)
                if selection_mode == 'manual':
                    print(f"\n{CYAN}📋 {character.name}의 특성을 직접 선택해주세요:{RESET}")
                    self._manual_trait_selection_cursor(character)
                else:
                    print(f"{CYAN}🤖 AI가 {character.name}의 특성을 자동 선택합니다...{RESET}")
                    self._auto_trait_selection(character, available_traits)
            else:
                # 자동 선택만
                print(f"{CYAN}🤖 AI가 {character.name}의 특성을 자동 선택합니다...{RESET}")
                self._auto_trait_selection(character, available_traits)
                
        except Exception as e:
            print(f"{RED}❌ {character.name} 특성 선택 오류: {e}{RESET}")
    
    def _ask_trait_selection_mode(self, character):
        """AI 동료의 특성 선택 방식을 묻기"""
        try:
            if not GAME_MODULES_AVAILABLE:
                return 'auto'
            
            from game.cursor_menu_system import CursorMenu
            
            options = [
                f"🎯 직접 선택 - {character.name}의 특성을 직접 고르기",
                f"🤖 AI 자동 선택 - {character.name}의 성격에 맞게 자동 선택"
            ]
            
            descriptions = [
                f"플레이어가 {character.name}의 특성을 직접 선택합니다",
                f"AI가 {character.name}의 성격({getattr(character, 'ai_personality', 'balanced')})에 맞는 특성을 자동 선택합니다"
            ]
            
            menu = CursorMenu(
                f"🌟 {character.name}의 특성 선택 방식", 
                options, 
                descriptions, 
                cancellable=False
            )
            
            result = menu.run()
            return 'manual' if result == 0 else 'auto'
            
        except Exception as e:
            print(f"{RED}❌ 특성 선택 방식 선택 오류: {e}{RESET}")
            return 'auto'
    
    def _manual_trait_selection_cursor(self, character):
        """커서 기반 특성 선택 (기존 시스템에서 가져옴)"""
        try:
            if not GAME_MODULES_AVAILABLE:
                print(f"{YELLOW}⚠️ 커서 메뉴를 사용할 수 없습니다. 기본 설정을 사용합니다.{RESET}")
                return False
                
            from game.cursor_menu_system import CursorMenu
            from game.color_text import GREEN, YELLOW, RED, WHITE, RESET, BOLD
            
            selected_indices = []
            max_traits = 2
            
            while len(selected_indices) < max_traits:
                remaining = max_traits - len(selected_indices)
                
                # 메뉴 옵션 생성
                options = []
                descriptions = []
                
                for i, trait in enumerate(character.available_traits):
                    # 특성 효과에 따른 아이콘
                    trait_icon = "⚔️"
                    if "공격" in trait.description or "데미지" in trait.description:
                        trait_icon = "⚔️"
                    elif "방어" in trait.description or "HP" in trait.description:
                        trait_icon = "🛡️"
                    elif "속도" in trait.description or "회피" in trait.description:
                        trait_icon = "💨"
                    elif "마법" in trait.description or "MP" in trait.description:
                        trait_icon = "🔮"
                    elif "회복" in trait.description or "치유" in trait.description:
                        trait_icon = "💚"
                    elif "크리티컬" in trait.description or "치명타" in trait.description:
                        trait_icon = "💥"
                    
                    # 선택 상태 표시
                    status = " ✅" if i in selected_indices else ""
                    option_text = f"{trait_icon} {trait.name}{status}"
                    
                    options.append(option_text)
                    descriptions.append(trait.description)
                
                # 특별 옵션들
                if selected_indices:
                    options.extend([
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        "✅ 선택 완료",
                        "🔄 선택 초기화"
                    ])
                    descriptions.extend([
                        "",
                        f"현재 선택된 {len(selected_indices)}개 특성으로 완료합니다",
                        "모든 선택을 취소하고 처음부터 다시 선택합니다"
                    ])
                
                title = f"🎯 특성 선택 ({len(selected_indices)}/{max_traits}) - {character.name}"
                if selected_indices:
                    selected_names = [character.available_traits[i].name for i in selected_indices]
                    title += f"\n선택됨: {', '.join(selected_names)}"
                
                menu = CursorMenu(title, options, descriptions, cancellable=True)
                result = menu.run()
                
                if result is None:  # 취소
                    print(f"{YELLOW}🚫 특성 선택이 취소되었습니다.{RESET}")
                    return False
                elif result < len(character.available_traits):  # 특성 선택/해제
                    trait_index = result
                    if trait_index in selected_indices:
                        # 선택 해제
                        selected_indices.remove(trait_index)
                        trait_name = character.available_traits[trait_index].name
                        print(f"{YELLOW}❌ {trait_name} 선택 해제됨{RESET}")
                    else:
                        # 선택 추가
                        selected_indices.append(trait_index)
                        trait_name = character.available_traits[trait_index].name
                        print(f"{GREEN}✅ {trait_name} 선택됨!{RESET}")
                        
                        # 최대 개수 도달하면 자동 완료
                        if len(selected_indices) >= max_traits:
                            break
                            
                elif result == len(character.available_traits) + 1:  # 선택 완료
                    if selected_indices:
                        break
                    else:
                        print(f"{YELLOW}⚠️ 최소 1개의 특성을 선택해주세요.{RESET}")
                        continue
                        
                elif result == len(character.available_traits) + 2:  # 선택 초기화
                    selected_indices = []
                    print(f"{YELLOW}🔄 선택이 초기화되었습니다.{RESET}")
                    continue
            
            # 특성 적용
            if selected_indices:
                character.select_passive_traits(selected_indices)
                selected_traits = [character.available_traits[i].name for i in selected_indices]
                print(f"\n{GREEN}{'='*50}{RESET}")
                print(f"{GREEN}🎉 특성 선택 완료!{RESET}")
                print(f"{WHITE}선택된 특성: {BOLD}{', '.join(selected_traits)}{RESET}")
                print(f"{GREEN}{'='*50}{RESET}")
                return True
            else:
                print(f"\n{YELLOW}🔄 특성 없이 진행합니다.{RESET}")
                character.select_passive_traits([])
                return True
                
        except Exception as e:
            print(f"{RED}❌ 커서 메뉴 특성 선택 오류: {e}{RESET}")
            # 폴백으로 자동 선택
            print(f"{YELLOW}⚠️ 자동 선택으로 대체합니다.{RESET}")
            self._auto_trait_selection(character, character.available_traits)
            return True
    
    def _auto_trait_selection(self, character, available_traits):
        """AI용 자동 특성 선택 (성격 기반)"""
        import random
        
        # AI 성격에 따른 특성 선호도
        personality = getattr(character, 'ai_personality', 'balanced')
        
        # 성격별 특성 우선순위 (실제 특성 이름에 맞게 조정 필요)
        personality_preferences = {
            'aggressive': ['전투 광', '공격적 성향', '용맹'],
            'defensive': ['방어 전문가', '보호 본능', '인내'],
            'supportive': ['치유술사', '지원 전문가', '협력'],
            'balanced': ['다재다능', '균형감각', '적응력'],
            'cunning': ['교활함', '전술가', '기회주의자']
        }
        
        # 성격에 맞는 특성 우선 선택
        preferred_traits = []
        if personality in personality_preferences:
            for trait_name in personality_preferences[personality]:
                for trait in available_traits:
                    if trait_name.lower() in trait.name.lower():
                        preferred_traits.append(trait)
        
        # 우선 특성이 없으면 랜덤 선택
        if not preferred_traits:
            preferred_traits = available_traits
        
        # 최대 2개 특성 선택
        selected_count = min(2, len(preferred_traits))
        selected_traits = random.sample(preferred_traits, selected_count)
        
        # 인덱스로 변환해서 적용
        selected_indices = []
        for trait in selected_traits:
            if trait in available_traits:
                selected_indices.append(available_traits.index(trait))
        
        # 캐릭터에 적용
        character.select_passive_traits(selected_indices)
        
        # 선택 결과 표시
        for trait in selected_traits:
            print(f"  ✓ {trait.name}: {trait.description}")
        
        print(f"{GREEN}✅ AI가 {character.name}을 위해 {len(selected_traits)}개 특성을 선택했습니다.{RESET}")
    
    # def _select_party_passive_effect(self, player_character, game_characters):
    #     """플레이어가 파티 전체 패시브 효과 3개를 선택"""
    #     # 패시브 효과는 이제 게임 내에서 선택합니다
    #     pass
    
    # def _apply_party_passives_to_characters(self, game_characters, selected_passives):
    #     """선택된 패시브 효과를 모든 파티원에게 적용"""
    #     # 패시브 효과는 이제 게임 내에서 적용됩니다
    #     pass

    def _select_party_passives(self, game_characters):
        """파티 전체 패시브 효과 선택"""
        try:
            # 기존 게임의 패시브 선택 시스템 활용
            if hasattr(self.game_instance, 'party_passive_selection'):
                print(f"{CYAN}🌟 파티 패시브 효과 선택 시스템을 시작합니다...{RESET}")
                
                # 파티 매니저에 캐릭터들 설정
                self.game_instance.party_manager.members = game_characters
                
                # 패시브 선택 실행
                self.game_instance.party_passive_selection()
            else:
                print(f"{YELLOW}⚠️ 패시브 선택 시스템을 찾을 수 없습니다. 기본 설정을 사용합니다.{RESET}")
                
        except Exception as e:
            print(f"{RED}❌ 파티 패시브 선택 오류: {e}{RESET}")
            print(f"{YELLOW}⚠️ 패시브 효과 없이 게임을 진행합니다.{RESET}")
    
    def _apply_trait_effects(self, trait: Dict):
        """특성 효과를 파티에 적용"""
        try:
            effect = trait.get('effect', {})
            print(f"  {GREEN}→ {trait['name']} 효과 적용됨{RESET}")
            
            # 특성 효과를 게임 시스템에 저장 (게임 시작 시 적용됨)
            if not hasattr(self, 'applied_trait_effects'):
                self.applied_trait_effects = {}
            
            for effect_type, value in effect.items():
                if effect_type not in self.applied_trait_effects:
                    self.applied_trait_effects[effect_type] = 0
                self.applied_trait_effects[effect_type] += value
                
        except Exception as e:
            print(f"{RED}❌ 특성 효과 적용 오류: {e}{RESET}")
    
    def _auto_save_ai_session(self, party_members: List[Dict], traits: Optional[List[Dict]] = None) -> bool:
        """AI 멀티플레이어 세션 자동 저장"""
        try:
            from datetime import datetime
            import json
            import os
            
            # 자동 저장 디렉토리 생성
            save_dir = "ai_multiplayer_saves"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 세션 데이터 구성
            session_data = {
                'session_id': f"ai_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'created_at': datetime.now().isoformat(),
                'party_members': party_members,
                'traits': traits or [],
                'trait_effects': getattr(self, 'applied_trait_effects', {}),
                'session_type': 'ai_multiplayer',
                'auto_save': True,
                'player_character': self.player_character,
                'ai_companions': [
                    {
                        'name': ai['character_data']['basic_info']['name'],
                        'class': ai['character_data']['basic_info']['class'],
                        'personality': ai['character_data']['basic_info'].get('personality_type', ''),
                        'data': ai['character_data']
                    } for ai in (self.ai_companions or [])
                ]
            }
            
            # 파일명 생성
            filename = f"auto_save_{session_data['session_id']}.json"
            filepath = os.path.join(save_dir, filename)
            
            # 저장 실행
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # 최신 세션 링크 생성
            latest_path = os.path.join(save_dir, "latest_ai_session.json")
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print(f"  💾 저장 경로: {filepath}")
            return True
            
        except Exception as e:
            print(f"{RED}❌ 자동 저장 실패: {e}{RESET}")
            return False
    
    def load_latest_ai_session(self) -> Optional[Dict]:
        """최신 AI 세션 로드"""
        try:
            import json
            import os
            
            latest_path = os.path.join("ai_multiplayer_saves", "latest_ai_session.json")
            if os.path.exists(latest_path):
                with open(latest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            print(f"{RED}❌ 세션 로드 실패: {e}{RESET}")
            return None
    
    def _create_single_character_preset(self):
        """단일 캐릭터 생성 및 저장 - 게임 시작 없이 프리셋만 생성"""
        try:
            from game.cursor_menu_system import CursorMenu
            from ai_27job_character_creator import AI27JobCharacterCreator
            
            print(f"\n{BRIGHT_CYAN}💾 단일 캐릭터 생성 및 저장{RESET}")
            print(f"{WHITE}게임을 시작하지 않고 캐릭터만 생성하여 프리셋으로 저장합니다.{RESET}")
            
            # 캐릭터 생성 방식 선택
            creation_options = [
                "🎯 수동 캐릭터 생성",
                "🤖 AI 추천 캐릭터",
                "🎲 랜덤 캐릭터 생성"
            ]
            
            creation_descriptions = [
                "직업, 이름, 성별을 직접 선택하여 캐릭터를 생성합니다",
                "AI가 추천하는 균형잡힌 캐릭터를 생성합니다",
                "완전히 랜덤한 캐릭터를 생성합니다"
            ]
            
            creation_menu = CursorMenu(
                title=f"{CYAN}캐릭터 생성 방식 선택{RESET}",
                options=creation_options,
                descriptions=creation_descriptions,
                cancellable=True
            )
            
            creation_choice = creation_menu.run()
            
            if creation_choice is None:
                print(f"{YELLOW}캐릭터 생성이 취소되었습니다.{RESET}")
                return
            
            character_data = None
            
            if creation_choice == 0:  # 수동 생성
                character_data = self._manual_single_character_creation()
            elif creation_choice == 1:  # AI 추천
                character_data = self._ai_recommended_character_creation()
            elif creation_choice == 2:  # 랜덤 생성
                character_data = self._random_character_creation()
            
            if character_data:
                # 캐릭터 프리셋 저장
                success = self._save_character_preset(character_data)
                if success:
                    print(f"\n{GREEN}✅ 캐릭터 프리셋이 성공적으로 저장되었습니다!{RESET}")
                    print(f"{CYAN}이제 게임 시작 시 이 캐릭터를 선택할 수 있습니다.{RESET}")
                else:
                    print(f"{RED}❌ 캐릭터 저장에 실패했습니다.{RESET}")
            
        except ImportError:
            print(f"{RED}❌ 필요한 모듈을 불러올 수 없습니다.{RESET}")
        except Exception as e:
            print(f"{RED}❌ 캐릭터 생성 오류: {e}{RESET}")
    
    def _manual_single_character_creation(self) -> Optional[Dict]:
        """수동 단일 캐릭터 생성"""
        try:
            from ai_27job_character_creator import AI27JobCharacterCreator
            
            creator = AI27JobCharacterCreator()
            
            print(f"\n{CYAN}🎯 수동 캐릭터 생성{RESET}")
            
            # 개별 캐릭터 생성 메뉴 호출
            character = creator._menu_create_individual()
            
            if character:
                # 캐릭터 데이터를 프리셋 형식으로 변환
                character_data = {
                    'name': character.name,
                    'class': character.character_class,
                    'gender': getattr(character, 'gender', '미지정'),
                    'level': character.level,
                    'character_data': {
                        'basic_info': {
                            'name': character.name,
                            'class': character.character_class,
                            'gender': getattr(character, 'gender', '미지정'),
                            'level': character.level
                        },
                        'stats': {
                            'hp': character.hp,
                            'mp': character.mp,
                            'attack': character.attack,
                            'defense': character.defense,
                            'speed': character.speed,
                            'luck': character.luck
                        },
                        'traits': getattr(character, 'traits', []),
                        'equipment': getattr(character, 'equipment', {})
                    },
                    'creation_method': 'manual',
                    'created_at': self._get_current_timestamp()
                }
                
                return character_data
            
            return None
            
        except Exception as e:
            print(f"{RED}❌ 수동 캐릭터 생성 오류: {e}{RESET}")
            return None
    
    def _ai_recommended_character_creation(self) -> Optional[Dict]:
        """AI 추천 캐릭터 생성"""
        try:
            print(f"\n{CYAN}🤖 AI 추천 캐릭터 생성{RESET}")
            
            # 초보자 친화적인 직업들
            beginner_jobs = ['전사', '궁수', '성기사', '아크메이지', '신관']
            
            import random
            selected_job = random.choice(beginner_jobs)
            
            # 기본 캐릭터 생성
            character_data = self._create_basic_character_data(selected_job)
            character_data['name'] = self._get_random_name()
            character_data['creation_method'] = 'ai_recommended'
            character_data['created_at'] = self._get_current_timestamp()
            
            print(f"{GREEN}✅ AI 추천 캐릭터 생성 완료:{RESET}")
            print(f"  📝 이름: {character_data['name']}")
            print(f"  ⚔️  직업: {character_data['class']}")
            print(f"  💡 레벨: {character_data['level']}")
            
            return character_data
            
        except Exception as e:
            print(f"{RED}❌ AI 추천 캐릭터 생성 오류: {e}{RESET}")
            return None
    
    def _random_character_creation(self) -> Optional[Dict]:
        """랜덤 캐릭터 생성"""
        try:
            print(f"\n{CYAN}🎲 랜덤 캐릭터 생성{RESET}")
            
            # 모든 직업 중 랜덤 선택
            all_jobs = [
                '전사', '아크메이지', '궁수', '성기사', '암흑기사', '정령술사', '도적', '바드',
                '용기사', '시간술사', '몽크', '신관', '검성', '차원술사', '연금술사', '드루이드',
                '마검사', '네크로맨서', '해적', '무당', '기계술사', '음유시인', '마법검사', '소환사',
                '마법사', '치유사', '암살자'
            ]
            
            import random
            selected_job = random.choice(all_jobs)
            
            # 기본 캐릭터 생성
            character_data = self._create_basic_character_data(selected_job)
            character_data['name'] = self._get_random_name()
            character_data['creation_method'] = 'random'
            character_data['created_at'] = self._get_current_timestamp()
            
            print(f"{GREEN}✅ 랜덤 캐릭터 생성 완료:{RESET}")
            print(f"  📝 이름: {character_data['name']}")
            print(f"  ⚔️  직업: {character_data['class']}")
            print(f"  💡 레벨: {character_data['level']}")
            
            return character_data
            
        except Exception as e:
            print(f"{RED}❌ 랜덤 캐릭터 생성 오류: {e}{RESET}")
            return None
    
    def _create_basic_character_data(self, job: str) -> Dict:
        """기본 캐릭터 데이터 생성"""
        # 직업별 기본 스탯
        job_stats = {
            '전사': {'hp': 120, 'mp': 20, 'attack': 15, 'defense': 12, 'speed': 8, 'luck': 5},
            '아크메이지': {'hp': 80, 'mp': 50, 'attack': 8, 'defense': 6, 'speed': 10, 'luck': 8},
            '궁수': {'hp': 100, 'mp': 30, 'attack': 12, 'defense': 8, 'speed': 15, 'luck': 10},
            '성기사': {'hp': 110, 'mp': 35, 'attack': 10, 'defense': 15, 'speed': 6, 'luck': 7},
            '도적': {'hp': 90, 'mp': 25, 'attack': 13, 'defense': 7, 'speed': 18, 'luck': 12}
        }
        
        # 기본값 설정
        default_stats = {'hp': 100, 'mp': 30, 'attack': 10, 'defense': 10, 'speed': 10, 'luck': 8}
        stats = job_stats.get(job, default_stats)
        
        return {
            'name': '',  # 나중에 설정
            'class': job,
            'gender': '미지정',
            'level': 1,
            'character_data': {
                'basic_info': {
                    'name': '',
                    'class': job,
                    'gender': '미지정',
                    'level': 1
                },
                'stats': stats,
                'traits': [],
                'equipment': {}
            }
        }
    
    def _save_character_preset(self, character_data: Dict) -> bool:
        """캐릭터 프리셋 저장"""
        try:
            import json
            import os
            from datetime import datetime
            
            # 프리셋 디렉토리 생성
            preset_dir = "character_presets"
            if not os.path.exists(preset_dir):
                os.makedirs(preset_dir)
            
            # 파일명 생성 (이름_직업_타임스탬프)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{character_data['name']}_{character_data['class']}_{timestamp}.json"
            filepath = os.path.join(preset_dir, filename)
            
            # 저장 실행
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
            
            print(f"  💾 저장 경로: {filepath}")
            return True
            
        except Exception as e:
            print(f"{RED}❌ 캐릭터 저장 오류: {e}{RESET}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _manual_character_creation(self):
        """수동 캐릭터 생성 (파티 구성)"""
        print(f"\n{CYAN}🎯 수동 캐릭터 생성 모드{RESET}")
        print(f"{WHITE}완전한 커스터마이징으로 파티를 구성합니다.{RESET}")
        
        # 기존 플레이어만 생성 후 AI 추가 방식 사용
        self._player_only_start()
    
    def _load_saved_preset(self):
        """저장된 프리셋 불러오기"""
        print(f"\n{CYAN}📁 저장된 프리셋 불러오기{RESET}")
        print(f"{YELLOW}이 기능은 개발 중입니다.{RESET}")
    
    def _load_party_preset(self):
        """저장된 파티 프리셋 불러오기"""
        import os
        import json
        from datetime import datetime
        
        preset_dir = os.path.join('presets', 'parties')
        if not os.path.exists(preset_dir):
            print(f"\n{RED}❌ 저장된 프리셋이 없습니다.{RESET}")
            input("\n계속하려면 Enter를 누르세요...")
            return None
        
        presets = sorted([f for f in os.listdir(preset_dir) if f.endswith('.json')],
                       key=lambda x: os.path.getmtime(os.path.join(preset_dir, x)), reverse=True)[:10]
        
        if not presets:
            print(f"\n{RED}❌ 저장된 프리셋이 없습니다.{RESET}")
            input("\n계속하려면 Enter를 누르세요...")
            return None
        
        print(f"\n{CYAN}📂 사용 가능한 프리셋:{RESET}")
        for i, p in enumerate(presets, 1):
            with open(os.path.join(preset_dir, p), 'r', encoding='utf-8') as f:
                data = json.load(f)
                date_str = datetime.fromtimestamp(os.path.getmtime(os.path.join(preset_dir, p))).strftime('%Y-%m-%d %H:%M')
                composition_str = ', '.join([f"{m['job']}({m['name']})" for m in data['party_composition']])
                print(f"  {i}. {p.replace('.json', '')} - {date_str}")
                print(f"     구성: {composition_str}")
        
        try:
            choice = int(input(f"\n{YELLOW}불러올 프리셋 번호 (0=취소): {RESET}"))
            if choice == 0 or choice > len(presets):
                return None
            
            # 선택된 프리셋 데이터 로드
            with open(os.path.join(preset_dir, presets[choice-1]), 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            print(f"\n{GREEN}📂 프리셋을 불러오는 중...{RESET}")
            print(f"✅ 프리셋 '{preset_data['name']}' 불러오기 완료!")
            return preset_data
            
        except (ValueError, IndexError):
            print(f"\n{RED}❌ 잘못된 선택입니다.{RESET}")
            return None
        except Exception as e:
            print(f"\n{RED}❌ 프리셋 불러오기 중 오류: {e}{RESET}")
            return None
    
    def _show_party_history(self):
        """파티 히스토리 보기"""
        print(f"\n{CYAN}📋 파티 히스토리{RESET}")
        print(f"{YELLOW}이 기능은 개발 중입니다.{RESET}")

def main():
    """메인 함수"""
    print(f"{BRIGHT_CYAN}🌟 Dawn of Stellar - AI 멀티플레이 시스템{RESET}")
    print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{CYAN}클래식 모드가 AI 멀티플레이로 진화했습니다!{RESET}")
    print(f"{WHITE}EXAONE 3.5 기반 지능형 AI 동료들과 함께 모험을 떠나보세요.{RESET}")
    
    launcher = AIMultiplayerLauncher()
    launcher.start_ai_multiplayer_mode()

if __name__ == "__main__":
    main()
