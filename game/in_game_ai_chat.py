"""
🎮 Dawn of Stellar - 게임 중 AI 대화 시스템
실제 게임 플레이 중에 AI 로바트들과 대화할 수 있는 시스템!

2025년 8월 10일 - GPT-5 지원 + 27개 직업별 성격!
"""

import sys
import os
import asyncio
from typing import Optional, Dict, Any, TYPE_CHECKING

# 게임 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if TYPE_CHECKING:
    from game.character import Character

try:
    from game.robat_personality_system import RobatPersonalitySystem, JobClass
    from ai_language_model_integration import RealLanguageModelSystem, LLMProvider
except ImportError as e:
    print(f"⚠️ 모듈 import 실패: {e}")
    # 폴백 처리
    RobatPersonalitySystem = None
    RealLanguageModelSystem = None

class InGameAIChat:
    """게임 중 AI 대화 시스템"""
    
    def __init__(self):
        self.personality_system = None
        self.llm_system = None
        self.current_character: Optional[Any] = None
        self.conversation_active = False
        
        try:
            if RobatPersonalitySystem:
                self.personality_system = RobatPersonalitySystem()
            if RealLanguageModelSystem:
                self.llm_system = RealLanguageModelSystem()
        except Exception as e:
            print(f"⚠️ AI 시스템 초기화 실패: {e}")
    
    def start_conversation_with_character(self, character) -> bool:
        """캐릭터와 대화 시작"""
        if not self.personality_system or not character:
            print("❌ AI 대화 시스템을 사용할 수 없습니다.")
            return False
        
        self.current_character = character
        job_class = character.job_class
        
        # 성격 정보 가져오기
        personality = self.personality_system.get_personality(job_class)
        if not personality:
            print(f"❌ {job_class} 직업의 성격 정보를 찾을 수 없습니다.")
            return False
        
        self.conversation_active = True
        
        # 대화 시작 인사
        greeting = self.personality_system.get_random_phrase(job_class, "conversation_starters")
        
        print(f"\n💬 === {personality.name}와의 대화 ===")
        print(f"🎭 성격: {personality.personality_type}")
        print(f"💭 말투: {personality.speaking_style}")
        print(f"\n{personality.name}: \"{greeting}\"")
        print("\n💡 명령어:")
        print("  - 메시지 입력: 직접 대화")
        print("  - '/exit' 또는 '/나가기': 대화 종료")
        print("  - '/help' 또는 '/도움말': 도움말 보기")
        print("  - '/personality' 또는 '/성격': 성격 정보 보기")
        print("  - '/quote' 또는 '/명언': 랜덤 명언 듣기")
        
        return True
    
    async def process_user_message(self, user_input: str) -> str:
        """사용자 메시지 처리"""
        if not self.current_character or not self.conversation_active:
            return "❌ 대화 중이 아닙니다."
        
        # 명령어 처리
        if user_input.startswith('/'):
            return self._handle_command(user_input)
        
        # AI 응답 생성
        return await self._generate_ai_response(user_input)
    
    def _handle_command(self, command: str) -> str:
        """명령어 처리"""
        command = command.lower().strip()
        
        if command in ['/exit', '/나가기']:
            self.conversation_active = False
            personality = self.personality_system.get_personality(self.current_character.job_class)
            farewell = self.personality_system.get_random_phrase(self.current_character.job_class, "favorite_phrases")
            return f"{personality.name}: \"{farewell}\" (대화를 종료합니다.)"
        
        elif command in ['/help', '/도움말']:
            return """
💡 === 대화 명령어 도움말 ===
• 일반 메시지: 그냥 입력하면 AI가 캐릭터 성격으로 응답
• /exit, /나가기: 대화 종료
• /personality, /성격: 현재 캐릭터 성격 정보
• /quote, /명언: 캐릭터의 랜덤 명언
• /battle, /전투: 전투 관련 대사
• /victory, /승리: 승리 대사
• /help, /도움말: 이 메시지
"""
        
        elif command in ['/personality', '/성격']:
            if not self.current_character:
                return "❌ 현재 대화 중인 캐릭터가 없습니다."
            
            personality = self.personality_system.get_personality(self.current_character.job_class)
            if not personality:
                return "❌ 성격 정보를 찾을 수 없습니다."
            
            info = f"""
🎭 === {personality.name} 성격 정보 ===
• 직업: {personality.job_class}
• 성격 유형: {personality.personality_type}
• 말투: {personality.speaking_style}
• 성격 특성: {', '.join(personality.character_traits)}
• 자주 하는 말:
"""
            for phrase in personality.favorite_phrases[:3]:
                info += f"  - \"{phrase}\"\n"
            return info
        
        elif command in ['/quote', '/명언']:
            phrase = self.personality_system.get_random_phrase(self.current_character.job_class)
            personality = self.personality_system.get_personality(self.current_character.job_class)
            return f"{personality.name}: \"{phrase}\""
        
        elif command in ['/battle', '/전투']:
            phrase = self.personality_system.get_random_phrase(self.current_character.job_class, "battle_quotes")
            personality = self.personality_system.get_personality(self.current_character.job_class)
            return f"{personality.name}: \"{phrase}\""
        
        elif command in ['/victory', '/승리']:
            phrase = self.personality_system.get_random_phrase(self.current_character.job_class, "victory_quotes")
            personality = self.personality_system.get_personality(self.current_character.job_class)
            return f"{personality.name}: \"{phrase}\""
        
        else:
            return f"❌ 알 수 없는 명령어: {command}\n'/help' 또는 '/도움말'로 명령어를 확인하세요."
    
    async def _generate_ai_response(self, user_message: str) -> str:
        """AI 응답 생성"""
        if not self.current_character or not self.personality_system:
            return "❌ AI 시스템을 사용할 수 없습니다."
        
        job_class = self.current_character.job_class
        personality = self.personality_system.get_personality(job_class)
        
        if not personality:
            return "❌ 성격 정보를 찾을 수 없습니다."
        
        # 실제 LLM 사용 시도
        if self.llm_system and self.llm_system.active_provider:
            try:
                # GPT-5나 다른 LLM으로 실제 응답 생성
                prompt = self.personality_system.generate_conversation_prompt(job_class, user_message)
                ai_response = await self._call_llm_api(prompt)
                
                if ai_response:
                    return f"{personality.name}: {ai_response}"
            except Exception as e:
                print(f"⚠️ LLM API 호출 실패: {e}")
        
        # 폴백: 패턴 기반 응답
        return self._generate_fallback_response(user_message, personality)
    
    async def _call_llm_api(self, prompt: str) -> Optional[str]:
        """실제 LLM API 호출"""
        if not self.llm_system or not self.llm_system.active_provider:
            return None
        
        try:
            # InteractiveRobatChat의 send_message 메서드 사용
            from ai_language_model_integration import InteractiveRobatChat
            chat = InteractiveRobatChat(self.llm_system)
            
            # 임시로 현재 캐릭터 설정
            chat.current_character = self.current_character.job_class if self.current_character else "전사"
            
            response = await chat.send_message(prompt)
            return response
        
        except Exception as e:
            print(f"⚠️ LLM API 호출 중 오류: {e}")
            return None
    
    def _generate_fallback_response(self, user_message: str, personality) -> str:
        """폴백 응답 생성 (LLM 없을 때)"""
        # 키워드 기반 간단한 응답
        message_lower = user_message.lower()
        
        # 감정 키워드 감지
        positive_keywords = ["좋", "훌륭", "멋지", "최고", "감사", "고마", "사랑", "좋아"]
        negative_keywords = ["싫", "나쁜", "화나", "짜증", "슬프", "우울", "힘들"]
        question_keywords = ["?", "뭐", "어떻", "왜", "언제", "어디", "누구", "어느"]
        
        # 반응 생성
        if any(keyword in message_lower for keyword in positive_keywords):
            reaction = personality.special_reactions.get("칭찬", personality.favorite_phrases)
        elif any(keyword in message_lower for keyword in negative_keywords):
            reaction = personality.special_reactions.get("걱정", personality.favorite_phrases)
        elif any(keyword in message_lower for keyword in question_keywords):
            # 질문에는 conversation_starters로 응답
            reaction = personality.conversation_starters
        else:
            # 기본 응답
            reaction = personality.favorite_phrases
        
        import random
        selected_response = random.choice(reaction)
        return f"{personality.name}: \"{selected_response}\""
    
    def is_conversation_active(self) -> bool:
        """대화 중인지 확인"""
        return self.conversation_active
    
    def get_current_character_info(self) -> Optional[Dict[str, Any]]:
        """현재 대화 중인 캐릭터 정보"""
        if not self.current_character:
            return None
        
        personality = self.personality_system.get_personality(self.current_character.job_class)
        if not personality:
            return None
        
        return {
            "name": self.current_character.name,
            "job_class": self.current_character.job_class,
            "robat_name": personality.name,
            "personality_type": personality.personality_type,
            "speaking_style": personality.speaking_style
        }

# 게임에서 사용할 글로벌 인스턴스
_in_game_chat = None

def get_in_game_chat() -> InGameAIChat:
    """인게임 채팅 시스템 인스턴스 가져오기"""
    global _in_game_chat
    if _in_game_chat is None:
        _in_game_chat = InGameAIChat()
    return _in_game_chat

def start_character_chat(character) -> bool:
    """캐릭터와 대화 시작 (게임에서 호출)"""
    chat_system = get_in_game_chat()
    return chat_system.start_conversation_with_character(character)

async def send_chat_message(message: str) -> str:
    """메시지 전송 (게임에서 호출)"""
    chat_system = get_in_game_chat()
    return await chat_system.process_user_message(message)

def is_chat_active() -> bool:
    """대화 중인지 확인 (게임에서 호출)"""
    chat_system = get_in_game_chat()
    return chat_system.is_conversation_active()

# 테스트용 함수
def demo_in_game_chat():
    """인게임 채팅 데모"""
    print("🎮 === 게임 중 AI 대화 시스템 데모! ===")
    
    # 가상의 캐릭터 생성
    class MockCharacter:
        def __init__(self, name, job_class):
            self.name = name
            self.job_class = job_class
    
    characters = [
        MockCharacter("용감한 전사", "전사"),
        MockCharacter("현명한 마법사", "아크메이지"),
        MockCharacter("자유로운 해적", "해적"),
        MockCharacter("사색하는 철학자", "철학자")
    ]
    
    print("\n💬 테스트할 캐릭터를 선택하세요:")
    for i, char in enumerate(characters, 1):
        print(f"{i}. {char.name} ({char.job_class})")
    
    try:
        choice = int(input("\n선택 (1-4): ")) - 1
        if 0 <= choice < len(characters):
            selected_char = characters[choice]
            
            # 대화 시작
            if start_character_chat(selected_char):
                print("\n💬 대화가 시작되었습니다!")
                print("메시지를 입력하거나 '/exit'로 종료하세요.\n")
                
                # 대화 루프
                import asyncio
                async def chat_loop():
                    while is_chat_active():
                        try:
                            user_input = input(f"{selected_char.name}에게 > ")
                            if user_input.strip():
                                response = await send_chat_message(user_input)
                                print(f"\n{response}\n")
                        except KeyboardInterrupt:
                            print("\n대화를 종료합니다.")
                            break
                        except EOFError:
                            break
                
                # 비동기 실행
                try:
                    asyncio.run(chat_loop())
                except Exception as e:
                    print(f"⚠️ 대화 중 오류: {e}")
            else:
                print("❌ 대화를 시작할 수 없습니다.")
        else:
            print("❌ 잘못된 선택입니다.")
    except (ValueError, EOFError, KeyboardInterrupt):
        print("프로그램을 종료합니다.")

if __name__ == "__main__":
    demo_in_game_chat()
