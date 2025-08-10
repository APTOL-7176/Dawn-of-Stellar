"""
🤖 Dawn of Stellar - 실제 언어모델 연동 시스템
OpenAI GPT, Claude, Ollama 등 실제 LLM과 연동

2025년 8월 10일 - 실제 AI와 대화하는 로바트들!
"""

import os
import json
import asyncio
import aiohttp
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class LLMProvider(Enum):
    """지원하는 언어모델 제공자"""
    OPENAI = "openai"
    CLAUDE = "claude"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"
    LOCAL = "local"

@dataclass
class LLMConfig:
    """언어모델 설정"""
    provider: LLMProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 150
    temperature: float = 0.7
    enabled: bool = False

class RealLanguageModelSystem:
    """실제 언어모델 연동 시스템"""
    
    def __init__(self):
        self.configs: Dict[LLMProvider, LLMConfig] = {}
        self.active_provider: Optional[LLMProvider] = None
        self.conversation_history: List[Dict[str, str]] = []
        
        # 설정 로드
        self._load_configs()
        
        print("🔗 실제 언어모델 연동 시스템 초기화!")
        self._check_available_providers()
    
    def _load_configs(self):
        """설정 파일 로드"""
        config_file = "llm_config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for provider_name, config_data in data.items():
                    try:
                        provider = LLMProvider(provider_name)
                        self.configs[provider] = LLMConfig(
                            provider=provider,
                            api_key=config_data.get('api_key'),
                            base_url=config_data.get('base_url'),
                            model_name=config_data.get('model_name', 'gpt-3.5-turbo'),
                            max_tokens=config_data.get('max_tokens', 150),
                            temperature=config_data.get('temperature', 0.7),
                            enabled=config_data.get('enabled', False)
                        )
                    except ValueError:
                        continue
            except Exception as e:
                print(f"⚠️ 설정 로드 실패: {e}")
        
        # 기본 설정 생성
        self._create_default_configs()
    
    def _create_default_configs(self):
        """기본 설정 생성"""
        default_configs = {
            LLMProvider.OPENAI: LLMConfig(
                provider=LLMProvider.OPENAI,
                model_name="gpt-5",  # 🔥 GPT-5 기본값으로!
                max_tokens=150,
                temperature=0.7
            ),
            LLMProvider.CLAUDE: LLMConfig(
                provider=LLMProvider.CLAUDE,
                model_name="claude-3-haiku-20240307",
                max_tokens=150,
                temperature=0.7
            ),
            LLMProvider.OLLAMA: LLMConfig(
                provider=LLMProvider.OLLAMA,
                base_url="http://localhost:11434",
                model_name="exaone3.5:7.8b",  # 🇰🇷 확실히 존재하는 LG AI 한국어 모델!
                max_tokens=150,
                temperature=0.7
            ),
            LLMProvider.GEMINI: LLMConfig(
                provider=LLMProvider.GEMINI,
                model_name="gemini-pro",
                max_tokens=150,
                temperature=0.7
            )
        }
        
        for provider, config in default_configs.items():
            if provider not in self.configs:
                self.configs[provider] = config
    
    def _check_available_providers(self):
        """사용 가능한 제공자 확인"""
        print("\n🔍 언어모델 제공자 확인:")
        
        # OpenAI API 키 확인
        openai_key = os.getenv('OPENAI_API_KEY') or self.configs.get(LLMProvider.OPENAI, LLMConfig(LLMProvider.OPENAI)).api_key
        if openai_key:
            self.configs[LLMProvider.OPENAI].api_key = openai_key
            self.configs[LLMProvider.OPENAI].enabled = True
            print("  ✅ OpenAI GPT: 사용 가능")
            if not self.active_provider:
                self.active_provider = LLMProvider.OPENAI
        else:
            print("  ⚠️ OpenAI GPT: API 키 필요")
        
        # Claude API 키 확인
        claude_key = os.getenv('ANTHROPIC_API_KEY') or self.configs.get(LLMProvider.CLAUDE, LLMConfig(LLMProvider.CLAUDE)).api_key
        if claude_key:
            self.configs[LLMProvider.CLAUDE].api_key = claude_key
            self.configs[LLMProvider.CLAUDE].enabled = True
            print("  ✅ Claude: 사용 가능")
            if not self.active_provider:
                self.active_provider = LLMProvider.CLAUDE
        else:
            print("  ⚠️ Claude: API 키 필요")
        
        # Gemini API 키 확인
        gemini_key = os.getenv('GOOGLE_API_KEY') or self.configs.get(LLMProvider.GEMINI, LLMConfig(LLMProvider.GEMINI)).api_key
        if gemini_key:
            self.configs[LLMProvider.GEMINI].api_key = gemini_key
            self.configs[LLMProvider.GEMINI].enabled = True
            print("  ✅ Gemini: 사용 가능")
            if not self.active_provider:
                self.active_provider = LLMProvider.GEMINI
        else:
            print("  ⚠️ Gemini: API 키 필요")
        
        # Ollama 로컬 서버 확인
        if self._check_ollama_server():
            self.configs[LLMProvider.OLLAMA].enabled = True
            print("  ✅ Ollama: 로컬 서버 활성화")
            if not self.active_provider:
                self.active_provider = LLMProvider.OLLAMA
        else:
            print("  ⚠️ Ollama: 로컬 서버 미실행")
        
        if self.active_provider:
            print(f"\n🎯 활성 제공자: {self.active_provider.value}")
        else:
            print("\n❌ 사용 가능한 언어모델 없음")
            print("💡 API 키를 설정하거나 Ollama를 설치하세요!")
    
    def _check_ollama_server(self) -> bool:
        """Ollama 서버 확인"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def generate_response(self, prompt: str, character_context: str = "", job_class: str = "로바트") -> str:
        """실제 언어모델로 응답 생성"""
        if not self.active_provider:
            return self._fallback_response(prompt, job_class)
        
        try:
            config = self.configs[self.active_provider]
            
            # 캐릭터 맥락 포함 프롬프트 구성
            full_prompt = self._build_character_prompt(prompt, character_context, job_class)
            
            if self.active_provider == LLMProvider.OPENAI:
                return await self._call_openai(full_prompt, config)
            elif self.active_provider == LLMProvider.CLAUDE:
                return await self._call_claude(full_prompt, config)
            elif self.active_provider == LLMProvider.OLLAMA:
                return await self._call_ollama(full_prompt, config)
            elif self.active_provider == LLMProvider.GEMINI:
                return await self._call_gemini(full_prompt, config)
            else:
                return self._fallback_response(prompt, job_class)
                
        except Exception as e:
            print(f"⚠️ 언어모델 호출 실패: {e}")
            return self._fallback_response(prompt, job_class)
    
    def _build_character_prompt(self, prompt: str, context: str, job_class: str) -> str:
        """캐릭터 맥락이 포함된 프롬프트 구성"""
        character_prompt = f"""당신은 Dawn of Stellar 게임의 {job_class} 직업 AI 캐릭터입니다.

캐릭터 설정:
- 직업: {job_class}
- 성격: 자랑스럽고 장난기 있는 로바트
- 말투: 친근하고 유머러스, 때로는 건방진 톤
- 특징: 게임에 대한 깊은 지식과 자신감

{context}

플레이어의 말: "{prompt}"

위 설정에 맞게 {job_class} 로바트로서 응답해주세요. 
응답은 100자 이내로 간결하게, 캐릭터의 개성이 드러나도록 작성하세요.

응답:"""
        
        return character_prompt
    
    async def _call_openai(self, prompt: str, config: LLMConfig) -> str:
        """OpenAI API 호출"""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"OpenAI API 오류: {response.status}")
    
    async def _call_claude(self, prompt: str, config: LLMConfig) -> str:
        """Claude API 호출"""
        headers = {
            "x-api-key": config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["content"][0]["text"].strip()
                else:
                    raise Exception(f"Claude API 오류: {response.status}")
    
    async def _call_ollama(self, prompt: str, config: LLMConfig) -> str:
        """Ollama API 호출"""
        data = {
            "model": config.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.base_url}/api/generate",
                json=data,
                timeout=60
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["response"].strip()
                else:
                    raise Exception(f"Ollama API 오류: {response.status}")
    
    async def _call_gemini(self, prompt: str, config: LLMConfig) -> str:
        """Gemini API 호출"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.model_name}:generateContent?key={config.api_key}"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": config.temperature,
                "maxOutputTokens": config.max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
                    raise Exception(f"Gemini API 오류: {response.status}")
    
    def _fallback_response(self, prompt: str, job_class: str) -> str:
        """대체 응답 (API 실패 시)"""
        fallback_responses = [
            f"흠... {job_class}인 내가 그런 건 잘 모르겠네! 🤔",
            f"오늘은 말이 안 나오는구만! {job_class}답지 않게... 😅",
            f"이런, 네트워크가 문제인가? {job_class}도 가끔은 말문이 막히지! 🌐",
            f"{job_class}인 나도 가끔은 생각할 시간이 필요해! ⏰",
            f"언어모델 연결이 불안정하네... {job_class}의 힘으로도 어쩔 수 없어! 🔌"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def save_config(self):
        """설정 저장"""
        config_data = {}
        
        for provider, config in self.configs.items():
            config_data[provider.value] = {
                "api_key": config.api_key,
                "base_url": config.base_url,
                "model_name": config.model_name,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "enabled": config.enabled
            }
        
        with open("llm_config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print("💾 언어모델 설정 저장 완료!")
    
    def set_api_key(self, provider: LLMProvider, api_key: str):
        """API 키 설정"""
        if provider in self.configs:
            self.configs[provider].api_key = api_key
            self.configs[provider].enabled = True
            
            if not self.active_provider:
                self.active_provider = provider
            
            print(f"🔑 {provider.value} API 키 설정 완료!")
        else:
            print(f"❌ 지원하지 않는 제공자: {provider.value}")
    
    def switch_provider(self, provider: LLMProvider):
        """언어모델 제공자 변경"""
        if provider in self.configs and self.configs[provider].enabled:
            self.active_provider = provider
            print(f"🔄 언어모델 변경: {provider.value}")
        else:
            print(f"❌ 사용 불가능한 제공자: {provider.value}")
    
    def get_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        status = {
            "active_provider": self.active_provider.value if self.active_provider else None,
            "available_providers": [],
            "total_conversations": len(self.conversation_history)
        }
        
        for provider, config in self.configs.items():
            if config.enabled:
                status["available_providers"].append({
                    "name": provider.value,
                    "model": config.model_name,
                    "active": provider == self.active_provider
                })
        
        return status

class InteractiveRobatChat:
    """상호작용하는 로바트 채팅 시스템"""
    
    def __init__(self):
        self.llm_system = RealLanguageModelSystem()
        self.active_character = "전사"
        self.character_contexts = self._load_character_contexts()
        
        print("\n💬 상호작용하는 로바트 채팅 시스템 시작!")
    
    def _load_character_contexts(self) -> Dict[str, str]:
        """캐릭터별 맥락 로드"""
        contexts = {
            "전사": "당신은 용감하고 강인한 전사입니다. 전투에 대한 자신감이 넘치고, 정의감이 강합니다.",
            "아크메이지": "당신은 지혜롭고 신비로운 대마법사입니다. 마법에 대한 깊은 지식을 가지고 있습니다.",
            "궁수": "당신은 정확하고 침착한 궁수입니다. 원거리 전투의 달인이며 관찰력이 뛰어납니다.",
            "도적": "당신은 영리하고 재빠른 도적입니다. 은밀한 행동과 기회주의적 성격을 가졌습니다.",
            "성기사": "당신은 고결하고 신성한 기사입니다. 정의와 신앙심이 깊으며 동료를 보호합니다.",
            "로바트": "당신은 게임의 마스코트 로바트입니다. 자랑스럽고 장난기 있으며 게임을 사랑합니다."
        }
        
        return contexts
    
    async def chat_with_robat(self, message: str, character: str = None) -> str:
        """로바트와 채팅"""
        if character:
            self.active_character = character
        
        context = self.character_contexts.get(self.active_character, self.character_contexts["로바트"])
        
        response = await self.llm_system.generate_response(
            message, 
            context, 
            self.active_character
        )
        
        # 대화 기록 저장
        self.llm_system.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "character": self.active_character,
            "user_message": message,
            "robat_response": response
        })
        
        return response
    
    def run_interactive_session(self):
        """대화형 세션 실행"""
        print(f"\n🤖 {self.active_character} 로바트와 대화를 시작합니다!")
        print("(종료하려면 'quit' 입력)")
        print("-" * 50)
        
        while True:
            try:
                user_input = input(f"\n💬 당신: ")
                
                if user_input.lower() in ['quit', 'exit', '종료', 'q']:
                    print(f"\n👋 {self.active_character} 로바트: 안녕! 또 만나자!")
                    break
                
                if user_input.lower().startswith('switch '):
                    new_char = user_input[7:].strip()
                    if new_char in self.character_contexts:
                        self.active_character = new_char
                        print(f"🔄 {new_char} 로바트로 변경!")
                        continue
                
                print(f"🤖 {self.active_character} 로바트가 생각 중...")
                
                response = asyncio.run(self.chat_with_robat(user_input))
                print(f"🤖 {self.active_character} 로바트: {response}")
                
            except KeyboardInterrupt:
                print(f"\n👋 {self.active_character} 로바트: 갑자기 왜 그래? 아무튼 안녕!")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")

def setup_api_keys():
    """API 키 설정 도우미"""
    print("🔑 언어모델 API 키 설정")
    print("-" * 30)
    
    llm_system = RealLanguageModelSystem()
    
    print("사용 가능한 언어모델:")
    print("1. OpenAI GPT (ChatGPT)")
    print("2. Claude (Anthropic)")
    print("3. Gemini (Google)")
    print("4. Ollama (로컬)")
    print()
    
    choice = input("설정할 언어모델 번호 (1-4): ").strip()
    
    if choice == "1":
        api_key = input("OpenAI API 키 입력: ").strip()
        if api_key:
            llm_system.set_api_key(LLMProvider.OPENAI, api_key)
    elif choice == "2":
        api_key = input("Anthropic API 키 입력: ").strip()
        if api_key:
            llm_system.set_api_key(LLMProvider.CLAUDE, api_key)
    elif choice == "3":
        api_key = input("Google API 키 입력: ").strip()
        if api_key:
            llm_system.set_api_key(LLMProvider.GEMINI, api_key)
    elif choice == "4":
        print("Ollama 설치 가이드:")
        print("1. https://ollama.ai 에서 다운로드")
        print("2. 설치 후 'ollama pull llama2' 실행")
        print("3. 'ollama serve' 로 서버 시작")
    
    llm_system.save_config()

async def demo_real_llm_integration():
    """실제 언어모델 연동 데모"""
    print("🎮 === Dawn of Stellar 실제 언어모델 연동 데모! ===")
    print()
    
    # 언어모델 시스템 초기화
    llm_system = RealLanguageModelSystem()
    
    if not llm_system.active_provider:
        print("⚠️ 사용 가능한 언어모델이 없습니다!")
        print("API 키를 설정하시겠습니까? (y/n): ", end="")
        if input().lower().startswith('y'):
            setup_api_keys()
            return
        else:
            print("💡 나중에 API 키를 설정하고 다시 시도하세요!")
            return
    
    # 상태 출력
    status = llm_system.get_status()
    print(f"🎯 활성 모델: {status['active_provider']}")
    print(f"📊 사용 가능한 모델 수: {len(status['available_providers'])}")
    print()
    
    # 대화형 세션
    chat_system = InteractiveRobatChat()
    chat_system.run_interactive_session()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_api_keys()
        elif sys.argv[1] == "chat":
            asyncio.run(demo_real_llm_integration())
        else:
            print("사용법: python ai_language_model_integration.py [setup|chat]")
    else:
        print("🤖 Dawn of Stellar 언어모델 연동 시스템")
        print("사용법:")
        print("  python ai_language_model_integration.py setup  # API 키 설정")
        print("  python ai_language_model_integration.py chat   # 로바트와 대화")
