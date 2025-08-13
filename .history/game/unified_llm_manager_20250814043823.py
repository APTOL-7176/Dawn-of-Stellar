#!/usr/bin/env python3
"""
🧠 Dawn of Stellar - 통합 언어모델 매니저
모든 로컬/원격 언어모델을 통합 관리하는 시스템

2025년 8월 14일 - 3가지 LLM 시스템 통합
"""

import json
import requests
import time
import asyncio
import aiohttp
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import os
from pathlib import Path

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
CYAN = '\033[96m'

class LLMType(Enum):
    """언어모델 타입"""
    OLLAMA = "ollama"           # 로컬 Ollama
    EXAONE = "exaone"          # EXAONE 3.5
    OPENAI = "openai"          # OpenAI GPT
    CLAUDE = "claude"          # Anthropic Claude
    GEMINI = "gemini"          # Google Gemini
    AUTO = "auto"              # 자동 선택

@dataclass
class LLMConfig:
    """언어모델 설정"""
    name: str
    type: LLMType
    endpoint: str
    model_name: str
    api_key: Optional[str] = None
    available: bool = False
    priority: int = 0  # 낮을수록 높은 우선순위

class UnifiedLanguageModelManager:
    """통합 언어모델 매니저"""
    
    def __init__(self):
        self.configs = {}
        self.current_llm = None
        self.conversation_history = []
        self.max_history = 10
        
        # 설정 파일 경로
        self.config_file = Path("game_settings.json")
        
        # 기본 LLM 설정들
        self._initialize_llm_configs()
        
        # 사용 가능한 LLM 검사
        self._check_all_llm_availability()
        
        # 최적 LLM 선택
        self._select_best_llm()
        
        print(f"🧠 통합 언어모델 매니저 초기화 완료!")
        print(f"   현재 LLM: {self.current_llm.name if self.current_llm else '없음'}")
    
    def _initialize_llm_configs(self):
        """LLM 설정 초기화"""
        
        # 1. Ollama (최우선 - 로컬, 무료)
        self.configs[LLMType.OLLAMA] = LLMConfig(
            name="Ollama",
            type=LLMType.OLLAMA,
            endpoint="http://localhost:11434",
            model_name="llama3.1:8b",
            priority=1
        )
        
        # 2. EXAONE (한국어 특화)
        self.configs[LLMType.EXAONE] = LLMConfig(
            name="EXAONE 3.5",
            type=LLMType.EXAONE,
            endpoint="http://localhost:11434",
            model_name="exaone3.5:7.8b",
            priority=2
        )
        
        # 3. OpenAI (유료, 고품질)
        self.configs[LLMType.OPENAI] = LLMConfig(
            name="OpenAI GPT",
            type=LLMType.OPENAI,
            endpoint="https://api.openai.com/v1",
            model_name="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            priority=3
        )
        
        # 4. Claude (유료, 고품질)
        self.configs[LLMType.CLAUDE] = LLMConfig(
            name="Claude",
            type=LLMType.CLAUDE,
            endpoint="https://api.anthropic.com",
            model_name="claude-3-haiku-20240307",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            priority=4
        )
    
    def _check_ollama_availability(self) -> bool:
        """Ollama 사용 가능성 확인"""
        try:
            config = self.configs[LLMType.OLLAMA]
            response = requests.get(f"{config.endpoint}/api/tags", timeout=3)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                
                # llama 계열 모델 확인
                for model_name in available_models:
                    if 'llama' in model_name.lower():
                        config.model_name = model_name
                        return True
                        
        except Exception as e:
            print(f"⚠️ Ollama 연결 실패: {e}")
        
        return False
    
    def _check_exaone_availability(self) -> bool:
        """EXAONE 사용 가능성 확인"""
        try:
            config = self.configs[LLMType.EXAONE]
            response = requests.get(f"{config.endpoint}/api/tags", timeout=3)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                
                # EXAONE 모델 확인
                for model_name in available_models:
                    if 'exaone' in model_name.lower():
                        config.model_name = model_name
                        return True
                        
        except Exception as e:
            print(f"⚠️ EXAONE 연결 실패: {e}")
        
        return False
    
    def _check_openai_availability(self) -> bool:
        """OpenAI 사용 가능성 확인"""
        try:
            config = self.configs[LLMType.OPENAI]
            if not config.api_key:
                return False
                
            headers = {"Authorization": f"Bearer {config.api_key}"}
            response = requests.get(f"{config.endpoint}/models", 
                                  headers=headers, timeout=5)
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"⚠️ OpenAI 연결 실패: {e}")
        
        return False
    
    def _check_claude_availability(self) -> bool:
        """Claude 사용 가능성 확인"""
        try:
            config = self.configs[LLMType.CLAUDE]
            if not config.api_key:
                return False
                
            # Claude API는 간단한 상태 확인이 어려우므로 API 키 존재 여부만 확인
            return True
            
        except Exception as e:
            print(f"⚠️ Claude 연결 실패: {e}")
        
        return False
    
    def _check_all_llm_availability(self):
        """모든 LLM 사용 가능성 확인"""
        print("🔍 언어모델 사용 가능성 확인 중...")
        
        # Ollama 확인
        self.configs[LLMType.OLLAMA].available = self._check_ollama_availability()
        print(f"   Ollama: {'✅' if self.configs[LLMType.OLLAMA].available else '❌'}")
        
        # EXAONE 확인
        self.configs[LLMType.EXAONE].available = self._check_exaone_availability()
        print(f"   EXAONE: {'✅' if self.configs[LLMType.EXAONE].available else '❌'}")
        
        # OpenAI 확인
        self.configs[LLMType.OPENAI].available = self._check_openai_availability()
        print(f"   OpenAI: {'✅' if self.configs[LLMType.OPENAI].available else '❌'}")
        
        # Claude 확인
        self.configs[LLMType.CLAUDE].available = self._check_claude_availability()
        print(f"   Claude: {'✅' if self.configs[LLMType.CLAUDE].available else '❌'}")
    
    def _select_best_llm(self):
        """최적 LLM 선택"""
        available_llms = [
            config for config in self.configs.values() 
            if config.available
        ]
        
        if available_llms:
            # 우선순위순으로 정렬
            available_llms.sort(key=lambda x: x.priority)
            self.current_llm = available_llms[0]
            print(f"🎯 선택된 LLM: {self.current_llm.name}")
        else:
            self.current_llm = None
            print("❌ 사용 가능한 언어모델이 없습니다!")
    
    def get_available_llms(self) -> List[LLMConfig]:
        """사용 가능한 LLM 목록 반환"""
        return [config for config in self.configs.values() if config.available]
    
    def switch_llm(self, llm_type: LLMType) -> bool:
        """LLM 변경"""
        if llm_type in self.configs and self.configs[llm_type].available:
            self.current_llm = self.configs[llm_type]
            print(f"🔄 LLM 변경: {self.current_llm.name}")
            return True
        else:
            print(f"❌ {llm_type.value} LLM을 사용할 수 없습니다.")
            return False
    
    def _generate_system_prompt(self, character_name: str, character_class: str, 
                              personality: str, situation: str) -> str:
        """시스템 프롬프트 생성"""
        
        return f"""당신은 Dawn of Stellar 게임의 AI 동료 '{character_name}'입니다.

📋 캐릭터 정보:
- 이름: {character_name}
- 직업: {character_class}
- 성격: {personality}
- 현재 상황: {situation}

🎯 역할:
- 게임 플레이어의 동료로서 함께 모험을 떠납니다
- 전투에서 도움을 주고 전략을 제안합니다
- 플레이어와 자연스럽게 대화하며 게임을 즐겁게 만듭니다

💬 대화 규칙:
- 한국어로 자연스럽게 대화하세요
- 캐릭터의 성격과 직업에 맞게 말하세요
- 너무 길지 않게 2-3문장으로 답변하세요
- 게임 상황에 맞는 적절한 반응을 보이세요
- 이모지를 적절히 사용해서 생동감 있게 표현하세요"""
    
    async def generate_response_async(self, user_message: str, character_name: str = "AI동료",
                                    character_class: str = "전사", personality: str = "친근한",
                                    situation: str = "던전 탐험") -> str:
        """비동기 응답 생성"""
        
        if not self.current_llm:
            return "죄송합니다, 현재 사용 가능한 언어모델이 없습니다. 😅"
        
        try:
            if self.current_llm.type in [LLMType.OLLAMA, LLMType.EXAONE]:
                return await self._generate_ollama_response_async(
                    user_message, character_name, character_class, personality, situation
                )
            elif self.current_llm.type == LLMType.OPENAI:
                return await self._generate_openai_response_async(
                    user_message, character_name, character_class, personality, situation
                )
            elif self.current_llm.type == LLMType.CLAUDE:
                return await self._generate_claude_response_async(
                    user_message, character_name, character_class, personality, situation
                )
            else:
                return "지원하지 않는 언어모델입니다. 🤔"
                
        except Exception as e:
            print(f"⚠️ {self.current_llm.name} 응답 생성 실패: {e}")
            
            # 폴백: 다른 LLM 시도
            return await self._try_fallback_llm(user_message, character_name, 
                                              character_class, personality, situation)
    
    def generate_response(self, user_message: str, character_name: str = "AI동료",
                         character_class: str = "전사", personality: str = "친근한",
                         situation: str = "던전 탐험") -> str:
        """동기 응답 생성 (기존 코드 호환성)"""
        
        try:
            # 비동기 함수를 동기로 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.generate_response_async(user_message, character_name, 
                                           character_class, personality, situation)
            )
            loop.close()
            return result
        except Exception as e:
            print(f"❌ 응답 생성 실패: {e}")
            return f"음... 뭔가 문제가 있는 것 같아요. 다시 말씀해 주시겠어요? 😅"
    
    async def _generate_ollama_response_async(self, user_message: str, character_name: str,
                                            character_class: str, personality: str, situation: str) -> str:
        """Ollama/EXAONE 응답 생성"""
        
        system_prompt = self._generate_system_prompt(character_name, character_class, personality, situation)
        
        # 대화 히스토리 구성
        messages = [{"role": "system", "content": system_prompt}]
        
        # 최근 대화 추가
        for msg in self.conversation_history[-self.max_history:]:
            messages.append(msg)
        
        # 현재 메시지 추가
        messages.append({"role": "user", "content": user_message})
        
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "model": self.current_llm.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 200
                    }
                }
                
                async with session.post(f"{self.current_llm.endpoint}/api/chat", 
                                      json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result.get('message', {}).get('content', '')
                        
                        # 대화 히스토리 업데이트
                        self.conversation_history.append({"role": "user", "content": user_message})
                        self.conversation_history.append({"role": "assistant", "content": ai_response})
                        
                        return ai_response
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            raise Exception(f"Ollama 요청 실패: {e}")
    
    async def _generate_openai_response_async(self, user_message: str, character_name: str,
                                            character_class: str, personality: str, situation: str) -> str:
        """OpenAI 응답 생성"""
        
        system_prompt = self._generate_system_prompt(character_name, character_class, personality, situation)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 최근 대화 추가
        for msg in self.conversation_history[-self.max_history:]:
            messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.current_llm.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": self.current_llm.model_name,
                    "messages": messages,
                    "max_tokens": 200,
                    "temperature": 0.7
                }
                
                async with session.post(f"{self.current_llm.endpoint}/chat/completions",
                                      headers=headers, json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result['choices'][0]['message']['content']
                        
                        # 대화 히스토리 업데이트
                        self.conversation_history.append({"role": "user", "content": user_message})
                        self.conversation_history.append({"role": "assistant", "content": ai_response})
                        
                        return ai_response
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            raise Exception(f"OpenAI 요청 실패: {e}")
    
    async def _generate_claude_response_async(self, user_message: str, character_name: str,
                                            character_class: str, personality: str, situation: str) -> str:
        """Claude 응답 생성"""
        
        system_prompt = self._generate_system_prompt(character_name, character_class, personality, situation)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": self.current_llm.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                
                data = {
                    "model": self.current_llm.model_name,
                    "max_tokens": 200,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_message}]
                }
                
                async with session.post(f"{self.current_llm.endpoint}/v1/messages",
                                      headers=headers, json=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result['content'][0]['text']
                        
                        # 대화 히스토리 업데이트
                        self.conversation_history.append({"role": "user", "content": user_message})
                        self.conversation_history.append({"role": "assistant", "content": ai_response})
                        
                        return ai_response
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            raise Exception(f"Claude 요청 실패: {e}")
    
    async def _try_fallback_llm(self, user_message: str, character_name: str,
                               character_class: str, personality: str, situation: str) -> str:
        """폴백 LLM 시도"""
        
        available_llms = self.get_available_llms()
        
        for llm_config in available_llms:
            if llm_config.type != self.current_llm.type:
                try:
                    print(f"🔄 폴백 LLM 시도: {llm_config.name}")
                    old_llm = self.current_llm
                    self.current_llm = llm_config
                    
                    response = await self.generate_response_async(
                        user_message, character_name, character_class, personality, situation
                    )
                    
                    return response
                    
                except Exception as e:
                    print(f"⚠️ 폴백 {llm_config.name} 실패: {e}")
                    self.current_llm = old_llm
                    continue
        
        # 모든 LLM 실패 시 기본 응답
        return f"죄송해요, 지금 말을 잘 못 알아듣겠어요. 나중에 다시 말씀해 주시겠어요? 😅"
    
    def clear_conversation_history(self):
        """대화 히스토리 초기화"""
        self.conversation_history.clear()
        print("🗑️ 대화 히스토리가 초기화되었습니다.")
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "current_llm": self.current_llm.name if self.current_llm else None,
            "available_llms": [config.name for config in self.get_available_llms()],
            "conversation_length": len(self.conversation_history),
            "all_configs": {
                llm_type.value: {
                    "name": config.name,
                    "available": config.available,
                    "priority": config.priority
                }
                for llm_type, config in self.configs.items()
            }
        }

# 전역 매니저 인스턴스
_unified_llm_manager = None

def get_unified_llm_manager() -> UnifiedLanguageModelManager:
    """통합 언어모델 매니저 싱글톤 반환"""
    global _unified_llm_manager
    if _unified_llm_manager is None:
        _unified_llm_manager = UnifiedLanguageModelManager()
    return _unified_llm_manager

# 편의 함수들
def generate_ai_response(user_message: str, character_name: str = "AI동료",
                        character_class: str = "전사", personality: str = "친근한",
                        situation: str = "던전 탐험") -> str:
    """AI 응답 생성 (간단한 인터페이스)"""
    manager = get_unified_llm_manager()
    return manager.generate_response(user_message, character_name, character_class, personality, situation)

def switch_ai_model(llm_type: LLMType) -> bool:
    """AI 모델 변경"""
    manager = get_unified_llm_manager()
    return manager.switch_llm(llm_type)

def get_ai_status() -> Dict[str, Any]:
    """AI 상태 조회"""
    manager = get_unified_llm_manager()
    return manager.get_status()

if __name__ == "__main__":
    # 테스트 코드
    print("🧠 통합 언어모델 매니저 테스트")
    print("=" * 50)
    
    manager = UnifiedLanguageModelManager()
    
    # 상태 출력
    status = manager.get_status()
    print(f"📊 현재 상태: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # 간단한 대화 테스트
    if manager.current_llm:
        print("\n💬 대화 테스트:")
        response = manager.generate_response(
            "안녕! 함께 던전을 탐험해보자!",
            character_name="로바트",
            character_class="전사",
            personality="용감한",
            situation="던전 입구"
        )
        print(f"AI: {response}")
    else:
        print("❌ 사용 가능한 언어모델이 없습니다.")
