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
    from game.world import World
    from game.display import GameDisplay
    GAME_MODULES_AVAILABLE = True
except ImportError:
    GAME_MODULES_AVAILABLE = False
    print("⚠️ 게임 모듈 일부 미사용 가능, 독립 실행 모드")

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
        print(f"\\n{BRIGHT_WHITE}🎮 AI 멀티플레이 메뉴{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{WHITE}1. {GREEN}🆕 새로운 AI 모험 시작{RESET}")
        print(f"{WHITE}2. {BLUE}📁 기존 AI 파티 불러오기{RESET}")
        print(f"{WHITE}3. {MAGENTA}🎭 커스텀 AI 파티 생성{RESET}")
        print(f"{WHITE}4. {CYAN}👥 AI 캐릭터 관리{RESET}")
        print(f"{WHITE}5. {YELLOW}🧠 AI 훈련 모드{RESET}")
        print(f"{WHITE}6. {WHITE}⚙️ 설정{RESET}")
        print(f"{WHITE}0. {RED}❌ 종료{RESET}")
        
        choice = input(f"\\n{YELLOW}선택하세요 (0-6): {RESET}").strip()
        
        # 문자열을 숫자로 변환
        try:
            return int(choice) - 1 if choice != '0' else 6
        except:
            return None
    
    def _start_new_ai_adventure(self):
        """새로운 AI 모험 시작"""
        print(f"\\n{BRIGHT_GREEN}🆕 새로운 AI 모험을 시작합니다!{RESET}")
        
        # 플레이어 캐릭터 생성 또는 선택
        player_char = self._create_or_select_player_character()
        if not player_char:
            return
        
        # AI 동료 3명 자동 생성
        print(f"\\n{CYAN}🤖 AI 동료들을 준비 중...{RESET}")
        ai_party = self.ai_creator.create_multiplayer_party(3)  # 플레이어 + AI 3명 = 4명 파티
        
        # 게임 시작
        self._start_game_with_ai_party(player_char, ai_party)
    
    def _create_or_select_player_character(self) -> Optional[Dict]:
        """플레이어 캐릭터 생성 또는 선택 - 커서 메뉴"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "🆕 새 캐릭터 생성",
                "📁 기존 캐릭터 사용", 
                "🤖 AI가 추천하는 캐릭터"
            ]
            
            descriptions = [
                "이름과 직업을 직접 선택하여 새로운 캐릭터를 생성합니다",
                "이전에 생성된 캐릭터를 불러와 사용합니다 (개발 중)",
                "AI가 초보자에게 적합한 직업을 추천하고 캐릭터를 생성합니다"
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
                return self._create_new_player_character()
            elif choice == 1:
                return self._select_existing_character()
            elif choice == 2:
                return self._ai_recommended_character()
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return None
                
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print(f"\\n{YELLOW}👤 플레이어 캐릭터 설정{RESET}")
            print("1. 새 캐릭터 생성")
            print("2. 기존 캐릭터 사용") 
            print("3. AI가 추천하는 캐릭터")
            
            choice = input("선택 (1-3): ").strip()
            
            if choice == "1":
                return self._create_new_player_character()
            elif choice == "2":
                return self._select_existing_character()
            elif choice == "3":
                return self._ai_recommended_character()
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
                return None
    
    def _create_new_player_character(self) -> Dict:
        """새 플레이어 캐릭터 생성 - 커서 메뉴"""
        print(f"\\n{CYAN}새 캐릭터를 생성합니다...{RESET}")
        
        # 이름 입력
        name = input("캐릭터 이름: ").strip() or "플레이어"
        
        # 직업 선택 - 커서 메뉴
        try:
            from game.cursor_menu_system import CursorMenu
            
            basic_classes = ["전사", "아크메이지", "궁수", "도적", "성기사", "바드"]
            
            # 직업별 설명
            job_descriptions = [
                "높은 방어력과 HP를 가진 전선 탱커. 초보자에게 추천!",
                "강력한 마법 공격력을 가진 마법사. 전략적 플레이 필요",
                "원거리 물리 공격 전문. 균형잡힌 성능",
                "빠른 속도와 독 공격이 특징. 테크니컬한 플레이",
                "회복과 방어를 겸하는 성스러운 기사. 파티 지원에 특화",
                "버프와 디버프로 파티를 지원하는 음유시인"
            ]
            
            menu = CursorMenu(
                title=f"{CYAN}직업 선택{RESET}",
                options=basic_classes,
                descriptions=job_descriptions,
                cancellable=False
            )
            
            job_choice = menu.run()
            job = basic_classes[job_choice] if job_choice is not None else "전사"
            
        except ImportError:
            # 폴백: 기본 텍스트 메뉴
            print("\\n직업 선택:")
            basic_classes = ["전사", "아크메이지", "궁수", "도적", "성기사", "바드"]
            for i, job in enumerate(basic_classes, 1):
                print(f"{i}. {job}")
            
            try:
                job_choice = int(input("직업 선택 (1-6): ")) - 1
                job = basic_classes[job_choice] if 0 <= job_choice < len(basic_classes) else "전사"
            except:
                job = "전사"
        
        player_char = {
            'name': name,
            'class': job,
            'level': 1,
            'is_ai': False,
            'is_player': True
        }
        
        print(f"{GREEN}✅ {name} ({job}) 생성 완료!{RESET}")
        return player_char
    
    def _select_existing_character(self) -> Optional[Dict]:
        """기존 캐릭터 선택"""
        # 여기서는 간단히 구현, 실제로는 세이브 파일에서 로드
        print(f"{BLUE}기존 캐릭터 기능은 개발 중입니다.{RESET}")
        return self._create_new_player_character()
    
    def _ai_recommended_character(self) -> Dict:
        """AI 추천 캐릭터"""
        print(f"\\n{MAGENTA}🤖 AI가 당신에게 어울리는 캐릭터를 추천합니다!{RESET}")
        
        import random
        recommended_classes = ["전사", "성기사", "바드", "아크메이지"]
        recommended_job = random.choice(recommended_classes)
        
        print(f"{GREEN}AI 추천: {recommended_job}{RESET}")
        print(f"{WHITE}이 직업은 AI 동료들과 잘 어울리고 초보자에게 적합합니다.{RESET}")
        
        accept = input("추천을 수락하시겠습니까? (y/n): ").strip().lower()
        if accept in ['y', 'yes', '네', '']:
            name = input("캐릭터 이름: ").strip() or "플레이어"
            return {
                'name': name,
                'class': recommended_job,
                'level': 1,
                'is_ai': False,
                'is_player': True
            }
        else:
            return self._create_new_player_character()
    
    def _start_game_with_ai_party(self, player_char: Dict, ai_party: List[Dict]):
        """AI 파티와 함께 게임 시작"""
        print(f"\\n{BRIGHT_GREEN}🎮 게임을 시작합니다!{RESET}")
        
        self.player_character = player_char
        self.ai_companions = ai_party
        
        # 파티 정보 표시
        print(f"\\n{BRIGHT_WHITE}👥 파티 구성:{RESET}")
        print(f"  {GREEN}🎮 플레이어: {player_char['name']} ({player_char['class']}){RESET}")
        
        for i, ai_char in enumerate(ai_party, 1):
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            print(f"  {CYAN}🤖 AI {i}: {basic['name']} ({basic['class']}, {basic['personality_type']}){RESET}")
        
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
        """기존 게임 시스템과 완전 통합"""
        if not self.game_integrated:
            return
        
        try:
            # 기존 게임 클래스와 통합
            from main import DawnOfStellarGame
            
            # 새로운 게임 인스턴스 생성 (AI 멀티플레이 모드)
            self.game_instance = DawnOfStellarGame()
            
            # AI 캐릭터들을 실제 게임 캐릭터로 변환
            self._convert_ai_to_game_characters()
            
            # 파티 매니저에 등록
            if hasattr(self.game_instance, 'party_manager'):
                self.party_manager = self.game_instance.party_manager
                
            # 전투 시스템 연동
            if hasattr(self.game_instance, 'combat_system'):
                self.combat_system = self.game_instance.combat_system
                
            # 월드 시스템 연동
            if hasattr(self.game_instance, 'world'):
                self.world = self.game_instance.world
                
            # 디스플레이 시스템 연동
            if hasattr(self.game_instance, 'display'):
                self.display = self.game_instance.display
            
            print(f"{GREEN}✅ Dawn of Stellar 게임 시스템 완전 통합 완료{RESET}")
            
        except Exception as e:
            print(f"{RED}게임 시스템 통합 실패: {e}{RESET}")
            print(f"{YELLOW}독립 모드로 실행합니다.{RESET}")
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
                character_class=self.player_character['class'],
                level=self.player_character.get('level', 1)
            )
            converted_party.append(player_char)
        
        # AI 동료들 변환
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            
            game_char = Character(
                name=basic['name'],
                character_class=basic['class'],
                level=basic.get('level', 1)
            )
            
            # AI 정보 저장 (게임 캐릭터에 AI 메타데이터 추가)
            game_char._ai_personality = basic['personality_type']
            game_char._ai_database = ai_char['database']
            game_char._is_ai_controlled = True
            
            converted_party.append(game_char)
        
        # 파티 매니저에 등록
        if hasattr(self.game_instance, 'party_manager'):
            self.game_instance.party_manager.members = converted_party
            print(f"{GREEN}✅ {len(converted_party)}명 파티를 게임에 등록했습니다{RESET}")
    
    def _main_game_loop(self):
        """메인 게임 루프 - 실제 Dawn of Stellar 게임 실행"""
        if self.game_integrated and hasattr(self, 'game_instance'):
            print(f"\\n{BRIGHT_GREEN}🎮 Dawn of Stellar AI 멀티플레이어 게임 시작!{RESET}")
            
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
                self.game_instance.start_adventure(
                    skip_passive_selection=True,  # 패시브 선택 건너뛰기
                    skip_ai_mode_selection=True   # AI 모드 선택 건너뛰기 (이미 설정됨)
                )
            except Exception as e:
                print(f"{RED}게임 실행 중 오류: {e}{RESET}")
                self._fallback_game_loop()
        else:
            print(f"\\n{YELLOW}독립 모드로 AI 멀티플레이어 시뮬레이션을 실행합니다.{RESET}")
            self._fallback_game_loop()
    
    def _fallback_game_loop(self):
        """폴백 게임 루프 (독립 모드)"""
        print(f"\\n{BRIGHT_WHITE}🎮 AI 멀티플레이어 시뮬레이션 모드{RESET}")
        print(f"{WHITE}실제 게임과 유사한 경험을 제공합니다.{RESET}")
        print(f"{YELLOW}💡 'help'를 입력하면 도움말을 볼 수 있습니다.{RESET}")
        
        while True:
            command = input(f"\\n{CYAN}명령을 입력하세요: {RESET}").strip().lower()
            
            if command in ['quit', 'exit', '종료', 'q']:
                break
            elif command in ['help', '도움말', 'h']:
                self._show_help()
            elif command in ['status', '상태', 's']:
                self._show_party_status()
            elif command in ['talk', '대화', 't']:
                self._talk_with_ai()
            elif command in ['explore', '탐험', 'e']:
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
        print(f"\\n{BRIGHT_CYAN}🎭 AI 동료들이 자기소개를 합니다!{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            personality = basic['personality_type']
            
            # AI가 자기소개 생성
            intro_context = f"{basic['name']}이(가) 새로운 파티원인 {self.player_character['name']}에게 첫 인사를 합니다."
            
            ai_intro = self.ai_engine.generate_ai_response(
                basic['name'], personality, intro_context, "dialogue"
            )
            
            print(f"\\n{CYAN}🤖 {basic['name']} ({basic['class']}):{RESET}")
            print(f"   {WHITE}\\\"{ai_intro}\\\"{RESET}")
            
            # 잠시 대기 (자연스러운 대화 흐름)
            time.sleep(1)
        
        print(f"\\n{GREEN}환영합니다! 이제 함께 모험을 떠날 준비가 되었습니다.{RESET}")
    
    def _main_game_loop(self):
        """메인 게임 루프"""
        if self.game_integrated and hasattr(self, 'game_instance'):
            print(f"\\n{BRIGHT_GREEN}🎮 Dawn of Stellar AI 멀티플레이어 게임 시작!{RESET}")
            
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
                self.game_instance.start_adventure(
                    skip_passive_selection=True,  # 패시브 선택 건너뛰기
                    skip_ai_mode_selection=True   # AI 모드 선택 건너뛰기 (이미 설정됨)
                )
            except Exception as e:
                print(f"{RED}게임 실행 중 오류: {e}{RESET}")
                self._fallback_game_loop()
        else:
            print(f"\\n{YELLOW}독립 모드로 AI 멀티플레이어 시뮬레이션을 실행합니다.{RESET}")
            self._fallback_game_loop()
    
    def _show_help(self):
        """도움말 표시"""
        print(f"\\n{BRIGHT_WHITE}📖 AI 멀티플레이 도움말{RESET}")
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
        print(f"\\n{BRIGHT_WHITE}👥 파티 상태{RESET}")
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
            
            print(f"\\n{CYAN}🤖 {basic['name']} ({basic['class']}){RESET}")
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
            print(f"\\n{BRIGHT_WHITE}💬 AI 동료와 대화{RESET}")
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
        
        print(f"\\n{CYAN}💬 {basic['name']}과(와)의 대화{RESET}")
        print(f"{WHITE}대화를 끝내려면 'end'를 입력하세요.{RESET}")
        
        while True:
            user_input = input(f"\\n{GREEN}당신: {RESET}").strip()
            
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
        print(f"\\n{BRIGHT_WHITE}🗺️ 던전 탐험{RESET}")
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
        print(f"\\n{CYAN}AI 동료들의 의견:{RESET}")
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
        
        print(f"\\n{GREEN}AI 동료들과 함께 신중하게 탐험을 계속합니다.{RESET}")
    
    def _simulate_combat(self):
        """전투 시뮬레이션"""
        print(f"\\n{BRIGHT_WHITE}⚔️ 전투 시뮬레이션{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        enemies = ["고블린", "오크", "스켈레톤"]
        import random
        enemy = random.choice(enemies)
        
        print(f"{RED}⚠️ {enemy}이(가) 나타났습니다!{RESET}")
        
        # AI들의 전투 전략
        print(f"\\n{CYAN}AI 동료들의 전투 준비:{RESET}")
        
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
        
        print(f"\\n{GREEN}✅ 전투에서 승리했습니다!{RESET}")
        print(f"{CYAN}AI 동료들이 전투 경험을 학습했습니다.{RESET}")
    
    def _ai_training_session(self):
        """AI 훈련 세션"""
        print(f"\\n{BRIGHT_WHITE}🧠 AI 훈련 세션{RESET}")
        print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            db = ai_char['database']
            
            # 학습 통계 표시
            stats = db.get_statistics()
            print(f"\\n{CYAN}{basic['name']} 훈련 결과:{RESET}")
            print(f"  총 학습 이벤트: {stats['total_learning_events']}")
            print(f"  게임 지식: {stats['total_knowledge_items']}")
            print(f"  행동 패턴: {stats['total_behavioral_patterns']}")
            
            relationship = db.get_relationship("플레이어")
            if relationship:
                print(f"  플레이어 신뢰도: {relationship['trust_level']:.2f}")
        
        print(f"\\n{GREEN}✅ AI 훈련 세션 완료!{RESET}")
    
    def _load_existing_ai_party(self):
        """기존 AI 파티 불러오기"""
        print(f"\\n{BLUE}📁 기존 AI 파티 불러오기 (개발 중){RESET}")
        available_characters = preset_manager.list_available_presets()
        
        if not available_characters:
            print(f"{RED}저장된 AI 캐릭터가 없습니다.{RESET}")
            return
        
        print(f"사용 가능한 AI 캐릭터: {len(available_characters)}명")
        for char in available_characters[:5]:  # 최대 5명까지 표시
            print(f"  - {char}")
    
    def _create_custom_ai_party(self):
        """커스텀 AI 파티 생성"""
        print(f"\\n{MAGENTA}🎭 커스텀 AI 파티 생성{RESET}")
        
        # 대화형 AI 캐릭터 생성
        custom_party = []
        for i in range(3):
            print(f"\\n{CYAN}AI 동료 {i+1} 생성:{RESET}")
            ai_char = self.ai_creator.create_ai_character_for_multiplayer()
            custom_party.append(ai_char)
            
            # 간단한 프로필 표시
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            print(f"✅ {basic['name']} ({basic['class']}, {basic['personality_type']}) 생성됨")
        
        # 생성된 파티로 게임 시작 여부 확인
        start_game = input(f"\\n이 파티로 게임을 시작하시겠습니까? (y/n): ").strip().lower()
        if start_game in ['y', 'yes', '네', '']:
            player_char = self._create_or_select_player_character()
            if player_char:
                self._start_game_with_ai_party(player_char, custom_party)
    
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
            print(f"\\n{CYAN}👥 AI 캐릭터 관리{RESET}")
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
        print(f"\\n{WHITE}📋 저장된 AI 캐릭터 ({len(characters)}명):{RESET}")
        
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
                    
                    print(f"\\n{BRIGHT_CYAN}📋 {basic['name']} 상세 프로필{RESET}")
                    print(f"{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
                    print(f"  📛 이름: {basic['name']}")
                    print(f"  ⚔️ 직업: {basic['class']}")
                    print(f"  🎭 성격: {basic['personality_type']}")
                    print(f"  🗣️ 말투: {basic.get('speech_style', '보통')}")
                    print(f"  📊 학습 이벤트: {stats['total_learning_events']}개")
                    print(f"  🧠 게임 지식: {stats['total_knowledge_items']}개")
                    print(f"  🤝 관계 데이터: {stats['total_relationships']}개")
                    print(f"  ⚡ 행동 패턴: {stats['total_behavioral_patterns']}개")
                    
                    input(f"\\n{YELLOW}확인하려면 Enter를 누르세요...{RESET}")
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
                        
                        print(f"\\n{BRIGHT_CYAN}📋 {basic['name']} 상세 프로필{RESET}")
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
            print(f"\\n{YELLOW}🧠 AI 훈련 모드{RESET}")
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
        
        print(f"\\n{WHITE}📊 AI 훈련 통계:{RESET}")
        for ai_char in self.ai_companions:
            char_data = ai_char['character_data']
            basic = char_data['basic_info']
            db = ai_char['database']
            stats = db.get_statistics()
            
            print(f"\\n{CYAN}{basic['name']}:{RESET}")
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
            print(f"\\n{WHITE}⚙️ 설정{RESET}")
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
