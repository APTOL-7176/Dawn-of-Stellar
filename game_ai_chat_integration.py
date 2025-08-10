"""
🎮 Dawn of Stellar - 게임 내 AI 채팅 통합 시스템
메인 게임에서 AI와 대화할 수 있도록 통합!

2025년 8월 10일 - 27개 직업별 로바트 + GPT-5!
"""

import asyncio
import sys
import os
from typing import Optional

# 게임 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GameAIChatIntegration:
    """게임 내 AI 채팅 통합 시스템"""
    
    def __init__(self):
        self.chat_system = None
        self.enabled = False
        
        try:
            from game.in_game_ai_chat import get_in_game_chat
            self.chat_system = get_in_game_chat()
            self.enabled = True
            print("🤖 게임 내 AI 채팅 시스템 활성화!")
        except ImportError as e:
            print(f"⚠️ AI 채팅 시스템 로드 실패: {e}")
            self.enabled = False
    
    def add_chat_commands_to_game(self, game_instance):
        """게임에 채팅 명령어 추가"""
        if not self.enabled:
            return
        
        # 기존 게임 명령어에 AI 채팅 추가
        original_handle_input = getattr(game_instance, 'handle_input', None)
        
        def enhanced_handle_input(key):
            # AI 채팅 명령어 처리
            if key.lower() == 'c':  # C키로 캐릭터와 대화
                self.start_party_chat(game_instance)
                return True
            elif key.lower() == 'ctrl+c':  # Ctrl+C로 AI 설정
                self.show_ai_setup_menu()
                return True
            
            # 기존 입력 처리
            if original_handle_input:
                return original_handle_input(key)
            return False
        
        # 메서드 교체
        game_instance.handle_input = enhanced_handle_input
        
        print("✅ AI 채팅 명령어가 게임에 추가되었습니다!")
        print("  • C키: 파티원과 대화")
        print("  • Ctrl+C: AI 설정")
    
    def start_party_chat(self, game_instance):
        """파티원과 대화 시작"""
        if not self.enabled:
            print("❌ AI 채팅 시스템이 비활성화되어 있습니다.")
            return
        
        try:
            # 파티 정보 가져오기
            party_manager = getattr(game_instance, 'party_manager', None)
            if not party_manager:
                print("❌ 파티 정보를 찾을 수 없습니다.")
                return
            
            party_members = getattr(party_manager, 'party_members', [])
            if not party_members:
                print("❌ 파티원이 없습니다.")
                return
            
            # 대화할 파티원 선택
            self.show_party_selection(party_members)
            
        except Exception as e:
            print(f"⚠️ 파티 채팅 시작 실패: {e}")
    
    def show_party_selection(self, party_members):
        """파티원 선택 메뉴"""
        print("\n💬 === 누구와 대화하시겠습니까? ===")
        
        for i, member in enumerate(party_members, 1):
            job_class = getattr(member, 'job_class', '알 수 없음')
            name = getattr(member, 'name', f'파티원 {i}')
            print(f"{i}. {name} ({job_class})")
        
        print("0. 취소")
        
        try:
            choice = input("\n선택 (번호 입력): ").strip()
            
            if choice == '0':
                print("대화를 취소했습니다.")
                return
            
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(party_members):
                selected_member = party_members[choice_num]
                self.start_character_conversation(selected_member)
            else:
                print("❌ 잘못된 선택입니다.")
        
        except (ValueError, EOFError, KeyboardInterrupt):
            print("대화를 취소했습니다.")
    
    def start_character_conversation(self, character):
        """캐릭터와 대화 시작"""
        if not self.chat_system:
            print("❌ 채팅 시스템을 사용할 수 없습니다.")
            return
        
        try:
            from game.in_game_ai_chat import start_character_chat, send_chat_message, is_chat_active
            
            # 대화 시작
            if start_character_chat(character):
                print("\n💡 팁: '/exit'로 대화 종료, '/help'로 명령어 확인")
                
                # 대화 루프
                asyncio.run(self._conversation_loop())
            else:
                print("❌ 대화를 시작할 수 없습니다.")
        
        except Exception as e:
            print(f"⚠️ 대화 시작 실패: {e}")
    
    async def _conversation_loop(self):
        """대화 루프"""
        from game.in_game_ai_chat import send_chat_message, is_chat_active
        
        while is_chat_active():
            try:
                user_input = input("\n💬 입력 > ").strip()
                
                if user_input:
                    response = await send_chat_message(user_input)
                    print(f"\n{response}")
                    
                    # 대화 종료 확인
                    if not is_chat_active():
                        print("\n💫 대화가 종료되었습니다. 게임으로 돌아갑니다.")
                        break
            
            except (EOFError, KeyboardInterrupt):
                print("\n대화를 강제 종료합니다.")
                break
            except Exception as e:
                print(f"⚠️ 대화 중 오류: {e}")
                break
    
    def show_ai_setup_menu(self):
        """AI 설정 메뉴"""
        print("\n🤖 === AI 설정 메뉴 ===")
        print("1. API 키 설정")
        print("2. AI 모델 선택")
        print("3. 채팅 테스트")
        print("4. 성격 시스템 정보")
        print("0. 돌아가기")
        
        try:
            choice = input("\n선택: ").strip()
            
            if choice == '1':
                self.setup_api_keys()
            elif choice == '2':
                self.select_ai_model()
            elif choice == '3':
                self.test_ai_chat()
            elif choice == '4':
                self.show_personality_info()
            elif choice == '0':
                print("설정을 종료합니다.")
            else:
                print("❌ 잘못된 선택입니다.")
        
        except (EOFError, KeyboardInterrupt):
            print("설정을 취소합니다.")
    
    def setup_api_keys(self):
        """API 키 설정"""
        print("\n🔑 === API 키 설정 ===")
        print("사용할 AI 서비스의 API 키를 설정하세요.")
        print("(설정하지 않으면 기본 응답 시스템을 사용합니다)")
        
        providers = {
            '1': ('OpenAI (GPT-5, GPT-4)', 'openai'),
            '2': ('Claude (Anthropic)', 'claude'),
            '3': ('Gemini (Google)', 'gemini'),
            '4': ('Ollama (로컬)', 'ollama')
        }
        
        print("\n서비스 선택:")
        for key, (name, _) in providers.items():
            print(f"{key}. {name}")
        print("0. 돌아가기")
        
        try:
            choice = input("\n선택: ").strip()
            
            if choice == '0':
                return
            
            if choice in providers:
                service_name, provider_id = providers[choice]
                print(f"\n{service_name} API 키 설정")
                
                if provider_id == 'ollama':
                    print("Ollama는 로컬 설치가 필요합니다.")
                    print("설치 방법: https://ollama.ai")
                else:
                    api_key = input("API 키 입력 (취소하려면 엔터): ").strip()
                    if api_key:
                        # API 키 저장 로직
                        print(f"✅ {service_name} API 키가 설정되었습니다!")
                        print("ai_language_model_integration.py에서 설정을 완료하세요.")
            else:
                print("❌ 잘못된 선택입니다.")
        
        except (EOFError, KeyboardInterrupt):
            print("API 키 설정을 취소합니다.")
    
    def select_ai_model(self):
        """AI 모델 선택"""
        print("\n🧠 === AI 모델 선택 ===")
        print("1. GPT-5 (최신!)") 
        print("2. GPT-4o")
        print("3. Claude-3")
        print("4. Gemini Pro")
        print("5. Ollama (로컬)")
        print("0. 돌아가기")
        
        try:
            choice = input("\n선택: ").strip()
            models = {
                '1': 'GPT-5',
                '2': 'GPT-4o', 
                '3': 'Claude-3',
                '4': 'Gemini Pro',
                '5': 'Ollama'
            }
            
            if choice == '0':
                return
            
            if choice in models:
                selected_model = models[choice]
                print(f"✅ {selected_model}가 선택되었습니다!")
                print("실제 적용은 ai_language_model_integration.py에서 설정하세요.")
            else:
                print("❌ 잘못된 선택입니다.")
        
        except (EOFError, KeyboardInterrupt):
            print("모델 선택을 취소합니다.")
    
    def test_ai_chat(self):
        """AI 채팅 테스트"""
        print("\n🧪 === AI 채팅 테스트 ===")
        
        try:
            from game.in_game_ai_chat import demo_in_game_chat
            demo_in_game_chat()
        except ImportError:
            print("❌ 채팅 테스트를 실행할 수 없습니다.")
        except Exception as e:
            print(f"⚠️ 테스트 실행 실패: {e}")
    
    def show_personality_info(self):
        """성격 시스템 정보"""
        print("\n🎭 === 27개 직업별 로바트 성격 시스템 ===")
        
        try:
            from game.robat_personality_system import RobatPersonalitySystem
            system = RobatPersonalitySystem()
            system.list_all_personalities()
        except ImportError:
            print("❌ 성격 시스템을 로드할 수 없습니다.")
        except Exception as e:
            print(f"⚠️ 성격 시스템 오류: {e}")

# 게임에서 사용할 글로벌 인스턴스
_game_ai_integration = None

def get_game_ai_integration() -> GameAIChatIntegration:
    """게임 AI 통합 시스템 인스턴스"""
    global _game_ai_integration
    if _game_ai_integration is None:
        _game_ai_integration = GameAIChatIntegration()
    return _game_ai_integration

def integrate_ai_chat_to_game(game_instance):
    """게임에 AI 채팅 기능 통합"""
    integration = get_game_ai_integration()
    integration.add_chat_commands_to_game(game_instance)
    return integration

# 메인 게임에서 호출할 함수들
def add_ai_chat_to_main_menu(menu_options: list):
    """메인 메뉴에 AI 채팅 옵션 추가"""
    ai_options = [
        "💬 파티원과 대화 (C키)",
        "🤖 AI 설정 (Ctrl+C)",
        "🎭 로바트 성격 정보 보기"
    ]
    
    # 기존 메뉴에 AI 옵션 추가
    if isinstance(menu_options, list):
        menu_options.extend(ai_options)
    
    return menu_options

def show_ai_chat_instructions():
    """AI 채팅 사용법 안내"""
    print("\n🤖 === AI 채팅 시스템 사용법 ===")
    print("• C키: 파티원과 대화 시작")
    print("• 대화 중 명령어:")
    print("  - '/exit': 대화 종료")
    print("  - '/help': 명령어 도움말")
    print("  - '/성격': 캐릭터 성격 정보")
    print("  - '/명언': 랜덤 명언 듣기")
    print("• 27개 직업별 고유 성격!")
    print("• GPT-5 지원!")
    print()

if __name__ == "__main__":
    # 테스트
    integration = get_game_ai_integration()
    integration.show_ai_setup_menu()
