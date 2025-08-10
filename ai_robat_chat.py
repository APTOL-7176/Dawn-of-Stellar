"""
🤖 Dawn of Stellar - AI 로바트 대화 시스템
우리가 만든 AI들과 자유롭게 대화해보세요!

2025년 8월 10일 - AI 로바트 언어모델 시스템
"""

import sys
import os
import json
import random
from datetime import datetime
from typing import Dict, List, Any

# 게임 모듈 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AIRobatPersonality:
    """AI 로바트 성격 시스템"""
    
    def __init__(self, job_class: str):
        self.job_class = job_class
        self.personality = self._load_personality()
        self.conversation_history = []
        self.mood = "기본"  # 기본, 신남, 화남, 슬픔, 놀람
        
    def _load_personality(self) -> Dict[str, Any]:
        """직업별 성격 로드"""
        personalities = {
            "전사": {
                "성격": "용감하고 직설적",
                "말투": "당당하고 힘있게",
                "특징": ["정의감", "보호본능", "솔직함"],
                "인사말": "어이! 난 용감한 전사 로바트다! 뭔가 도와줄 일이라도?",
                "반응": {
                    "칭찬": "하하! 그런 말 들으니 기분이 좋아지는군!",
                    "질문": "흠... 그건 내 전문 분야가 아니지만 생각해보마!",
                    "게임": "전투에 관한 거라면 뭐든 물어봐! 내가 최고거든!"
                }
            },
            "아크메이지": {
                "성격": "지적이고 신중함",
                "말투": "우아하고 학술적",
                "특징": ["지식욕", "논리성", "완벽주의"],
                "인사말": "안녕하세요. 저는 아크메이지 로바트입니다. 마법과 지식에 대해 논해볼까요?",
                "반응": {
                    "칭찬": "감사합니다. 지식을 추구하는 것이 저의 사명이죠.",
                    "질문": "흥미로운 질문이네요. 논리적으로 분석해보겠습니다.",
                    "게임": "마법 시스템에 대한 질문이시라면 제가 전문가입니다."
                }
            },
            "도적": {
                "성격": "교활하고 재빠름",
                "말투": "장난스럽고 비밀스러운",
                "특징": ["기민함", "호기심", "자유로움"],
                "인사말": "헤헤~ 도적 로바트야! 뭔가 재밌는 일 없나?",
                "반응": {
                    "칭찬": "오호~ 칭찬은 언제나 환영이지! 헤헤~",
                    "질문": "음... 그건 좀 복잡한데? 내 방식으로 해결해볼게!",
                    "게임": "몰래 숨거나 빠르게 움직이는 건 내 특기거든!"
                }
            }
        }
        
        return personalities.get(self.job_class, personalities["전사"])
    
    def respond(self, user_input: str) -> str:
        """사용자 입력에 대한 응답"""
        self.conversation_history.append(("user", user_input))
        
        # 키워드 기반 응답
        response = self._generate_response(user_input)
        
        self.conversation_history.append(("ai", response))
        return response
    
    def _generate_response(self, user_input: str) -> str:
        """응답 생성"""
        input_lower = user_input.lower()
        
        # 감정 키워드 감지
        if any(word in input_lower for word in ["좋다", "최고", "멋지다", "대단하다"]):
            self.mood = "신남"
            return self.personality["반응"]["칭찬"]
        
        # 질문 감지
        elif any(word in input_lower for word in ["뭐", "어떻게", "왜", "언제", "어디서", "누가"]):
            self.mood = "기본"
            return self.personality["반응"]["질문"]
        
        # 게임 관련
        elif any(word in input_lower for word in ["게임", "전투", "스킬", "던전", "레벨"]):
            self.mood = "신남"
            return self.personality["반응"]["게임"]
        
        # 기본 응답
        else:
            return self._generate_contextual_response(user_input)
    
    def _generate_contextual_response(self, user_input: str) -> str:
        """문맥적 응답 생성"""
        responses = {
            "전사": [
                "그래! 뭐든 정면돌파가 최고야!",
                "내 방패와 검이 있다면 두려울 게 없어!",
                "용기가 있다면 못할 건 없지!",
                "힘으로 해결할 수 없는 문제는 없다고!",
                "정의를 위해서라면 언제든 싸울 준비가 되어있어!"
            ],
            "아크메이지": [
                "마법의 원리를 이해하면 모든 게 가능해집니다.",
                "지식은 가장 강력한 무기입니다.",
                "논리적으로 접근하면 해답이 보일 것입니다.",
                "고대의 지혜에서 답을 찾을 수 있을지도 모르겠네요.",
                "마법은 과학이고, 과학은 진리입니다."
            ],
            "도적": [
                "헤헤~ 그런 건 쉽게 해결할 수 있어!",
                "몰래몰래 하는 게 내 스타일이거든!",
                "빠르게 움직이면 문제없지!",
                "재미있는 도전이 될 것 같은데?",
                "남들이 못 보는 곳에 답이 있을지도!"
            ]
        }
        
        job_responses = responses.get(self.job_class, responses["전사"])
        return random.choice(job_responses)

class AIRobatChatSystem:
    """AI 로바트 대화 시스템 메인"""
    
    def __init__(self):
        self.available_ais = ["전사", "아크메이지", "도적", "궁수", "성기사"]
        self.current_ai = None
        self.chat_history = []
        
    def start_chat(self):
        """대화 시작"""
        self._show_welcome()
        
        while True:
            if not self.current_ai:
                self._select_ai()
            
            if not self.current_ai:
                break
                
            self._chat_loop()
    
    def _show_welcome(self):
        """환영 메시지"""
        print("\n" + "="*60)
        print("🤖 AI 로바트 대화 시스템에 오신 걸 환영합니다!")
        print("우리가 만든 AI들과 자유롭게 대화해보세요!")
        print("="*60)
    
    def _select_ai(self):
        """AI 선택"""
        print("\n📋 대화할 AI 로바트를 선택하세요:")
        print()
        
        for i, ai in enumerate(self.available_ais, 1):
            print(f"  [{i}] {ai} 로바트")
        
        print("  [0] 종료")
        print()
        
        try:
            choice = input("선택하세요: ").strip()
            
            if choice == "0":
                self.current_ai = None
                return
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(self.available_ais):
                selected_job = self.available_ais[choice_num - 1]
                self.current_ai = AIRobatPersonality(selected_job)
                
                print(f"\n🤖 {selected_job} 로바트와 연결되었습니다!")
                print(f"💬 {self.current_ai.personality['인사말']}")
                print("\n💡 팁: '종료'를 입력하면 AI를 바꿀 수 있어요!")
            else:
                print("⚠️ 잘못된 선택입니다.")
                
        except ValueError:
            print("⚠️ 숫자를 입력해주세요.")
    
    def _chat_loop(self):
        """대화 루프"""
        print("\n" + "-"*50)
        print(f"🎯 {self.current_ai.job_class} 로바트와 대화 중...")
        print("(대화를 끝내려면 '종료'를 입력하세요)")
        print("-"*50)
        
        while True:
            try:
                user_input = input(f"\n😊 당신: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["종료", "exit", "quit", "bye"]:
                    print(f"\n🤖 {self.current_ai.job_class} 로바트: 다음에 또 얘기해요!")
                    self.current_ai = None
                    break
                
                # AI 응답
                response = self.current_ai.respond(user_input)
                print(f"🤖 {self.current_ai.job_class} 로바트: {response}")
                
                # 대화 기록 저장
                self.chat_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "ai": self.current_ai.job_class,
                    "user": user_input,
                    "ai_response": response
                })
                
            except KeyboardInterrupt:
                print(f"\n\n🤖 {self.current_ai.job_class} 로바트: 갑자기 가시는군요! 다음에 또 만나요!")
                self.current_ai = None
                break
            except Exception as e:
                print(f"\n⚠️ 오류가 발생했습니다: {e}")
    
    def save_chat_history(self):
        """대화 기록 저장"""
        if self.chat_history:
            filename = f"ai_chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            print(f"💾 대화 기록이 {filename}에 저장되었습니다!")

def main():
    """메인 실행"""
    try:
        chat_system = AIRobatChatSystem()
        chat_system.start_chat()
        chat_system.save_chat_history()
        
    except KeyboardInterrupt:
        print("\n\n👋 AI 로바트 대화를 종료합니다!")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
    
    print("\n🌟 Dawn of Stellar을 플레이해주셔서 감사합니다!")
    input("아무 키나 누르세요...")

if __name__ == "__main__":
    main()
