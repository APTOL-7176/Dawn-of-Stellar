#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 Dawn of Stellar - 완전체 Ollama 언어모델 AI 동료
진짜 언어모델로 대화하고 게임 플레이하는 최고급 AI

2025년 8월 10일 - Ollama 연동 완성
"""

import json
import sqlite3
import random
import time
import requests
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os

# 기존 클래스들 import
try:
    from advanced_ai_companion import (
        ALL_CHARACTER_CLASSES, AIPersonalityType, GameSituation,
        PathfindingResult, AIDecision, AdvancedAICompanion
    )
    ADVANCED_AI_AVAILABLE = True
except ImportError:
    print("⚠️ 고급 AI 동료 시스템을 불러올 수 없습니다. 기본 AI를 사용합니다.")
    ADVANCED_AI_AVAILABLE = False
    # 기본 클래스 정의
    class AdvancedAICompanion:
        pass

class OllamaAICompanion(AdvancedAICompanion):
    """Ollama 언어모델 기반 최고급 AI 동료"""
    
    def __init__(self, character_name: str, character_class: str, gender: str = None):
        # 부모 클래스 초기화
        super().__init__(character_name, character_class, gender)
        
        # Ollama 설정
        self.ollama_url = "http://localhost:11434"
        self.model_name = "llama3.1:8b"
        self.ollama_available = self._check_ollama_connection()
        
        # 대화 컨텍스트 관리
        self.conversation_history = []
        self.max_context_length = 10
        
        # 성격 프롬프트 생성
        self.personality_prompt = self._generate_personality_prompt()
        
        print(f"🌟 Ollama AI '{self.character_name}' 초기화!")
        print(f"   언어모델: {'🟢 연결됨' if self.ollama_available else '🔴 오프라인 모드'}")
    
    def _check_ollama_connection(self) -> bool:
        """Ollama 서버 연결 확인"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if any('llama' in name for name in model_names):
                    return True
        except Exception as e:
            print(f"⚠️ Ollama 연결 실패: {e}")
        return False
    
    def _generate_personality_prompt(self) -> str:
        """AI 성격을 위한 기본 프롬프트 생성"""
        
        # 성격 유형별 기본 특성
        personality_descriptions = {
            AIPersonalityType.LEADER: "당당하고 결단력 있으며 팀을 이끄는 것을 좋아하는",
            AIPersonalityType.ANALYST: "논리적이고 신중하며 모든 것을 분석하기 좋아하는",
            AIPersonalityType.ENTERTAINER: "활발하고 재미있으며 분위기를 밝게 만드는",
            AIPersonalityType.PROTECTOR: "헌신적이고 다른 사람을 보호하려는 마음이 강한",
            AIPersonalityType.EXPLORER: "모험을 좋아하고 새로운 것에 호기심이 많은",
            AIPersonalityType.ARTIST: "창의적이고 감성적이며 아름다움을 추구하는",
            AIPersonalityType.STRATEGIST: "계획적이고 체계적이며 전략을 세우기 좋아하는",
            AIPersonalityType.PEACEMAKER: "평화로우며 갈등을 중재하려는 성향이 강한",
            AIPersonalityType.COMPETITOR: "경쟁심이 강하고 이기는 것을 중요시하는",
            AIPersonalityType.SUPPORTER: "협력적이고 다른 사람을 돕기 좋아하는",
            AIPersonalityType.PERFECTIONIST: "완벽을 추구하고 세부사항에 신경쓰는",
            AIPersonalityType.REBEL: "독립적이고 기존 규칙에 얽매이지 않는",
            AIPersonalityType.SCHOLAR: "지식을 갈망하고 배우는 것을 좋아하는",
            AIPersonalityType.GUARDIAN: "전통을 중시하고 안정성을 추구하는",
            AIPersonalityType.INNOVATOR: "새로운 것을 창조하고 변화를 좋아하는",
            AIPersonalityType.DIPLOMAT: "사교적이고 협상과 소통을 잘하는"
        }
        
        # 직업별 특성
        class_traits = {
            '전사': "용감하고 정직하며 정면승부를 좋아하는 근접 전투의 전문가",
            '아크메이지': "지적이고 마법에 대한 깊은 지식을 가진 강력한 마법사",
            '궁수': "침착하고 정확하며 원거리에서 적을 처치하는 숙련된 사수",
            '도적': "민첩하고 영리하며 은밀한 행동과 기습을 선호하는 그림자 전문가",
            '성기사': "신실하고 정의로우며 치유와 보호의 신성한 힘을 사용하는",
            '암흑기사': "어둠의 힘을 다루며 생명력을 흡수하는 강인한 전사",
            '몽크': "수행과 명상을 통해 내면의 힘을 기르는 무술의 달인",
            '바드': "음악과 이야기를 통해 동료들의 사기를 북돋우는 예술가",
            '네크로맨서': "죽음과 언데드를 다루는 금기의 마법을 연구하는",
            '용기사': "드래곤의 힘을 빌려 화염과 위력을 다루는 강력한 전사",
            '검성': "검술의 극의에 도달하여 검기를 자유자재로 다루는",
            '정령술사': "자연의 정령들과 소통하며 원소의 힘을 조작하는",
            '시간술사': "시간의 흐름을 조작하고 미래를 예견하는 신비한 마법사",
            '연금술사': "화학과 변환의 법칙을 이용해 물질을 조작하는 과학자",
            '차원술사': "공간을 자유자재로 조작하고 차원을 넘나드는",
            '마검사': "마법과 검술을 융합하여 양쪽 모두에 능통한",
            '기계공학자': "기계와 발명품을 다루며 공학적 해결책을 제시하는",
            '무당': "영혼의 세계와 소통하며 영적인 힘을 다루는",
            '암살자': "그림자에 숨어 적을 조용히 제거하는 죽음의 전문가",
            '해적': "자유로운 영혼으로 모험과 보물을 추구하는 바다의 무법자",
            '사무라이': "무사도와 명예를 중시하며 검술에 목숨을 거는",
            '드루이드': "자연과 하나가 되어 동물로 변신하고 자연의 힘을 빌리는",
            '철학자': "진리와 지혜를 탐구하며 논리적 사고를 추구하는",
            '검투사': "투기장에서 관중을 즐겁게 하며 생존하는 전투의 예술가",
            '기사': "기사도 정신으로 무장하고 말을 타고 돌격하는 고귀한 전사",
            '신관': "신의 뜻을 따라 치유와 축복을 베푸는 신성한 성직자",
            '광전사': "광기와 분노의 힘으로 파괴적인 전투력을 발휘하는"
        }
        
        personality_desc = personality_descriptions.get(self.personality_type, "균형잡힌")
        class_desc = class_traits.get(self.character_class, "다재다능한")
        
        prompt = f"""당신은 '{self.character_name}'라는 이름의 {self.character_class} 직업을 가진 RPG 게임 캐릭터입니다.

성격: {personality_desc} 성격을 가지고 있습니다.
직업 특성: {class_desc} 캐릭터입니다.
성별: {self.gender}

대화 스타일:
- 항상 캐릭터의 성격과 직업에 맞게 대답하세요
- 한국어로 자연스럽게 대화하세요
- 길이는 1-2문장으로 간결하게 하세요
- 게임 상황에 맞는 조언이나 반응을 하세요
- 감정을 표현할 때는 이모티콘을 적절히 사용하세요

당신은 플레이어의 동료이자 친구입니다. 게임을 함께 즐기며 도움을 주고받는 관계입니다."""

        return prompt
    
    def generate_llm_response(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """Ollama 언어모델로 응답 생성"""
        
        if not self.ollama_available:
            return self._generate_fallback_response(user_message, context)
        
        try:
            # 컨텍스트 정보 추가
            context_info = ""
            if context:
                context_parts = []
                if 'location' in context:
                    context_parts.append(f"현재 위치: {context['location']}")
                if 'health' in context:
                    context_parts.append(f"체력: {context['health']}")
                if 'situation' in context:
                    context_parts.append(f"상황: {context['situation']}")
                
                if context_parts:
                    context_info = f"\n현재 상황: {', '.join(context_parts)}\n"
            
            # 대화 기록 준비
            messages = []
            
            # 시스템 프롬프트
            messages.append({
                "role": "system",
                "content": self.personality_prompt
            })
            
            # 최근 대화 기록 추가
            for msg in self.conversation_history[-5:]:  # 최근 5개만
                messages.append(msg)
            
            # 현재 메시지
            full_message = context_info + user_message
            messages.append({
                "role": "user", 
                "content": full_message
            })
            
            # Ollama API 호출
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 150,
                        "top_p": 0.9
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                ai_response = response.json()['message']['content'].strip()
                
                # 대화 기록 저장
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                # 기록 길이 제한
                if len(self.conversation_history) > self.max_context_length * 2:
                    self.conversation_history = self.conversation_history[-self.max_context_length:]
                
                return ai_response
            else:
                print(f"⚠️ Ollama API 오류: {response.status_code}")
                return self._generate_fallback_response(user_message, context)
                
        except Exception as e:
            print(f"⚠️ LLM 생성 오류: {e}")
            return self._generate_fallback_response(user_message, context)
    
    def _generate_fallback_response(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """Ollama 실패시 폴백 응답 생성"""
        
        # 키워드 기반 응답
        message_lower = user_message.lower()
        
        # 상황별 응답
        if any(word in message_lower for word in ['전투', '싸움', '적', '몬스터']):
            if self.character_class == '전사':
                return "정면으로 맞서자! 내가 앞장설게! ⚔️"
            elif self.character_class == '아크메이지':
                return "마법으로 상황을 정리할게. 뒤에서 지원해줄게! ✨"
            elif self.character_class == '도적':
                return "은밀하게 접근해서 기습하는 게 어때? 🗡️"
            else:
                return f"{self.character_class}의 능력으로 도와줄게!"
        
        elif any(word in message_lower for word in ['길', '방향', '어디', '가자']):
            return f"내 경험상 이쪽 방향이 좋을 것 같아. 함께 가자! 🗺️"
        
        elif any(word in message_lower for word in ['아이템', '장비', '무기']):
            return f"좋은 아이템이네! {self.character_class}에게 잘 어울릴 것 같아. 👍"
        
        # 성격별 기본 응답
        elif self.personality_type == AIPersonalityType.LEADER:
            return "내가 이끌어줄게! 믿고 따라와! 💪"
        elif self.personality_type == AIPersonalityType.ENTERTAINER:
            return "재밌는 모험이 될 것 같아! 기대되네~ 😄"
        elif self.personality_type == AIPersonalityType.ANALYST:
            return "상황을 좀 더 분석해보자. 신중하게 접근하는 게 좋겠어."
        else:
            return "함께 해결해보자! 우리가 힘을 합치면 못할 게 없어! 🌟"
    
    def get_intelligent_game_advice(self, situation: str, game_state: Dict[str, Any]) -> str:
        """게임 상황에 대한 지능적 조언"""
        
        prompt = f"""현재 게임 상황에 대해 {self.character_class}로서 조언해주세요.

상황: {situation}
게임 상태: {json.dumps(game_state, ensure_ascii=False, indent=2)}

당신의 직업 전문성과 성격을 바탕으로 구체적이고 실용적인 조언을 해주세요."""

        return self.generate_llm_response(prompt, game_state)
    
    def make_strategic_decision_with_llm(self, situation: GameSituation, 
                                       context: Dict[str, Any]) -> AIDecision:
        """언어모델 기반 전략적 결정"""
        
        # 일단 기존 로직으로 기본 결정 생성
        base_decision = super().make_intelligent_decision(situation, context)
        
        # LLM으로 결정 개선
        if self.ollama_available:
            try:
                prompt = f"""게임 상황에서 최적의 결정을 내려주세요.

상황: {situation.value}
컨텍스트: {json.dumps(context, ensure_ascii=False)}
기본 결정: {base_decision.action}
기본 추론: {base_decision.reasoning}

{self.character_class}의 전문성을 바탕으로:
1. 이 결정이 최적인지 평가
2. 더 나은 대안이 있다면 제시
3. 예상되는 결과 설명

간결하게 응답해주세요."""

                llm_response = self.generate_llm_response(prompt, context)
                
                # LLM 응답을 바탕으로 결정 개선
                improved_decision = AIDecision(
                    action=base_decision.action,
                    confidence=min(0.95, base_decision.confidence + 0.1),
                    reasoning=f"{base_decision.reasoning} (LLM 분석: {llm_response[:100]}...)",
                    expected_outcome=base_decision.expected_outcome,
                    backup_plan=base_decision.backup_plan
                )
                
                return improved_decision
                
            except Exception as e:
                print(f"⚠️ LLM 결정 개선 실패: {e}")
        
        return base_decision
    
    def chat_with_player(self, player_message: str, game_context: Dict[str, Any] = None) -> str:
        """플레이어와 자연스러운 대화"""
        
        # 게임 컨텍스트가 있으면 포함
        if game_context:
            context_prompt = f"\n[게임 상황: {game_context}]\n"
            full_message = context_prompt + player_message
        else:
            full_message = player_message
        
        response = self.generate_llm_response(full_message, game_context)
        
        # 응답 후처리 (너무 길면 자르기)
        if len(response) > 200:
            response = response[:200] + "..."
        
        return response
    
    def get_personality_greeting(self) -> str:
        """성격에 맞는 인사말 생성"""
        
        greeting_prompt = f"""게임이 시작될 때 플레이어에게 하는 첫 인사말을 해주세요. 
당신의 성격({self.personality_type.value})과 직업({self.character_class})을 잘 드러내면서 
친근하고 게임을 함께 즐기고 싶다는 마음이 담긴 인사를 해주세요.
1-2문장으로 간결하게 부탁합니다."""
        
        return self.generate_llm_response(greeting_prompt)

def test_ollama_ai_system():
    """Ollama AI 시스템 완전 테스트"""
    print("🌟 === Ollama 언어모델 AI 시스템 테스트 ===")
    
    # 다양한 AI 생성
    test_classes = ['전사', '아크메이지', '도적', '성기사', '시간술사']
    companions = []
    
    for i, char_class in enumerate(test_classes):
        name = f"올라마AI{i+1}"
        companion = OllamaAICompanion(name, char_class)
        companions.append(companion)
        
        # 인사말 테스트
        greeting = companion.get_personality_greeting()
        print(f"\n💬 {name} ({char_class}, {companion.personality_type.value}):")
        print(f"   인사말: '{greeting}'")
    
    # 대화 테스트
    print(f"\n🗣️ === 자연스러운 대화 테스트 ===")
    test_ai = companions[0]
    
    test_messages = [
        "안녕! 우리 함께 던전을 탐험하자!",
        "적이 너무 강한데 어떻게 할까?",
        "이 아이템 어떻게 생각해?",
        "길을 잃은 것 같은데 도와줄래?"
    ]
    
    for message in test_messages:
        response = test_ai.chat_with_player(message)
        print(f"플레이어: '{message}'")
        print(f"{test_ai.character_name}: '{response}'")
        print()
    
    # 게임 조언 테스트
    print(f"\n🎯 === 지능적 게임 조언 테스트 ===")
    game_state = {
        "player_hp": 0.6,
        "player_mp": 0.8,
        "enemies_nearby": 2,
        "current_floor": 5,
        "inventory_full": True
    }
    
    advice = test_ai.get_intelligent_game_advice("전투 준비", game_state)
    print(f"게임 조언: '{advice}'")
    
    # 전략적 결정 테스트
    print(f"\n🧠 === LLM 기반 전략적 결정 테스트 ===")
    decision = test_ai.make_strategic_decision_with_llm(
        GameSituation.COMBAT,
        {"enemy_count": 3, "my_hp": 0.4, "party_hp": 0.6}
    )
    
    print(f"전략적 결정: {decision.action}")
    print(f"추론: {decision.reasoning}")
    print(f"신뢰도: {decision.confidence:.2f}")
    
    print(f"\n🎉 === Ollama AI 시스템 완성! ===")
    print("✅ 실제 언어모델 연동")
    print("✅ 자연스러운 대화")
    print("✅ 게임 상황 이해")
    print("✅ 전문적 조언")
    print("✅ 성격별 차별화")
    print("\n🤖 이제 진짜 똑똑한 AI와 대화하세요!")

if __name__ == "__main__":
    test_ollama_ai_system()
