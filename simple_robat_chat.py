"""
🎮 Dawn of Stellar - 27개 직업별 로바트 간단 채팅 데모
API 키 없이도 작동하는 폴백 시스템 테스트!

2025년 8월 10일 - GPT-5 지원!
"""

import asyncio
import sys
import os

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simple_chat_demo():
    """간단한 채팅 데모"""
    
    print("🎮 === Dawn of Stellar - 27개 직업별 로바트 채팅 데모! ===")
    print("🔥 GPT-5 지원! (API 키 설정 시)")
    print()
    
    try:
        from game.robat_personality_system import RobatPersonalitySystem
        system = RobatPersonalitySystem()
    except ImportError:
        print("❌ 성격 시스템을 로드할 수 없습니다.")
        return
    
    # 인기 직업들 선택
    popular_jobs = [
        ("전사", "용감한 전사"),
        ("아크메이지", "현명한 마법사"),
        ("해적", "자유로운 해적"),
        ("암살자", "그림자 암살자"),
        ("드래곤", "용족 전사"),
        ("기계공학자", "기계 박사"),
        ("철학자", "사색가")
    ]
    
    print("💬 대화할 로바트를 선택하세요:")
    available_jobs = []
    for i, (job_class, name) in enumerate(popular_jobs, 1):
        personality = system.get_personality(job_class)
        if personality:
            print(f"{i}. {personality.name} ({job_class}) - {personality.personality_type}")
            available_jobs.append((job_class, personality))
        else:
            print(f"{i}. {name} ({job_class}) - [구현중]")
    
    print("0. 종료")
    
    try:
        choice = input("\n선택 (번호): ").strip()
        
        if choice == '0':
            print("프로그램을 종료합니다!")
            return
        
        choice_num = int(choice) - 1
        if 0 <= choice_num < len(available_jobs):
            job_class, personality = available_jobs[choice_num]
            
            # 간단한 대화 시뮬레이션
            print(f"\n💬 === {personality.name}와의 대화 ===")
            print(f"🎭 성격: {personality.personality_type}")
            print(f"💭 말투: {personality.speaking_style}")
            
            # 인사말
            greeting = system.get_random_phrase(job_class, "conversation_starters")
            print(f"\n{personality.name}: \"{greeting}\"")
            
            print("\n💡 명령어: '/exit' 종료, '/help' 도움말")
            print("📝 메시지를 입력하세요!")
            
            # 간단한 대화 루프
            while True:
                try:
                    user_input = input(f"\n당신 > ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['/exit', '/종료', '/나가기']:
                        farewell = system.get_random_phrase(job_class, "favorite_phrases")
                        print(f"\n{personality.name}: \"{farewell}\"")
                        print("대화를 종료합니다!")
                        break
                    
                    elif user_input.lower() in ['/help', '/도움말']:
                        print("\n💡 === 명령어 도움말 ===")
                        print("• 일반 대화: 메시지 입력")
                        print("• /exit, /종료: 대화 종료")
                        print("• /성격: 성격 정보 보기")
                        print("• /명언: 랜덤 명언")
                        print("• /전투: 전투 대사")
                        print("• /승리: 승리 대사")
                        continue
                    
                    elif user_input.lower() in ['/성격', '/personality']:
                        print(f"\n🎭 === {personality.name} 성격 정보 ===")
                        print(f"• 직업: {personality.job_class}")
                        print(f"• 성격 유형: {personality.personality_type}")
                        print(f"• 말투: {personality.speaking_style}")
                        print(f"• 성격 특성: {', '.join(personality.character_traits)}")
                        continue
                    
                    elif user_input.lower() in ['/명언', '/quote']:
                        quote = system.get_random_phrase(job_class, "favorite_phrases")
                        print(f"\n{personality.name}: \"{quote}\"")
                        continue
                    
                    elif user_input.lower() in ['/전투', '/battle']:
                        battle_quote = system.get_random_phrase(job_class, "battle_quotes")
                        print(f"\n{personality.name}: \"{battle_quote}\"")
                        continue
                    
                    elif user_input.lower() in ['/승리', '/victory']:
                        victory_quote = system.get_random_phrase(job_class, "victory_quotes")
                        print(f"\n{personality.name}: \"{victory_quote}\"")
                        continue
                    
                    # 일반 대화 처리
                    response = generate_smart_response(user_input, personality, system)
                    print(f"\n{personality.name}: \"{response}\"")
                
                except (EOFError, KeyboardInterrupt):
                    print("\n\n대화를 종료합니다!")
                    break
        else:
            print("❌ 잘못된 선택입니다.")
    
    except (ValueError, EOFError, KeyboardInterrupt):
        print("프로그램을 종료합니다!")

def generate_smart_response(user_input, personality, system):
    """스마트한 응답 생성 (폴백 시스템)"""
    import random
    
    message_lower = user_input.lower()
    
    # 감정/키워드 분석
    positive_words = ["좋", "훌륭", "멋지", "최고", "감사", "고마", "사랑", "좋아", "대단", "완벽", "놀라", "멋있"]
    negative_words = ["싫", "나쁜", "화나", "짜증", "슬프", "우울", "힘들", "답답", "짜증나", "최악"]
    question_words = ["?", "뭐", "어떻", "왜", "언제", "어디", "누구", "어느", "무엇", "어떤"]
    greeting_words = ["안녕", "hi", "hello", "반가", "처음", "만나"]
    
    job_class = personality.job_class
    
    # 인사말
    if any(word in message_lower for word in greeting_words):
        greetings = personality.conversation_starters + personality.favorite_phrases[:2]
        return random.choice(greetings)
    
    # 긍정적 반응
    elif any(word in message_lower for word in positive_words):
        if "칭찬" in personality.special_reactions:
            return random.choice(personality.special_reactions["칭찬"])
        return random.choice(personality.favorite_phrases)
    
    # 부정적 반응  
    elif any(word in message_lower for word in negative_words):
        if "걱정" in personality.special_reactions:
            return random.choice(personality.special_reactions["걱정"])
        return random.choice(personality.favorite_phrases)
    
    # 질문
    elif any(word in message_lower for word in question_words):
        return random.choice(personality.conversation_starters)
    
    # 직업별 특수 키워드
    elif job_class == "전사" and any(word in message_lower for word in ["싸움", "전투", "힘", "방패"]):
        return random.choice(personality.battle_quotes + personality.favorite_phrases)
    
    elif job_class == "아크메이지" and any(word in message_lower for word in ["마법", "주문", "원소", "지식"]):
        return random.choice(["마법에 대해 알고 싶으신가요?", "원소의 조화가 중요합니다.", "지식은 힘이죠!"])
    
    elif job_class == "해적" and any(word in message_lower for word in ["바다", "모험", "보물", "자유"]):
        return random.choice(["바다로 나가고 싶어!", "모험이 기다리고 있어!", "자유가 최고야!"])
    
    elif job_class == "기계공학자" and any(word in message_lower for word in ["기계", "발명", "기술", "로봇"]):
        return random.choice(["기계의 정밀함!", "새로운 발명이 필요해!", "기술로 해결하자!"])
    
    elif job_class == "철학자" and any(word in message_lower for word in ["생각", "철학", "진리", "의미"]):
        return random.choice(["깊이 생각해봅시다.", "철학적인 질문이군요.", "진리를 찾는 길이죠."])
    
    # 기본 응답
    else:
        return random.choice(personality.favorite_phrases)

if __name__ == "__main__":
    simple_chat_demo()
