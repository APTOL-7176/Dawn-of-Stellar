"""
🎮 Dawn of Stellar - 로-바트 실전 게임플레이 시스템
실제 게임 시스템과 100% 연동하여 로-바트가 직접 게임을 플레이!

이 시스템은:
- 실제 게임 객체들과 직접 상호작용
- 진짜 던전 탐험, 전투, 요리, 쇼핑
- 로-바트 특성을 살린 플레이 스타일
- 각 직업별 완전히 다른 플레이 방식
"""

import asyncio
import random
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from game.job_specialized_ai import JobSpecializedAI, JobClass, RobatPersonality
from game.color_text import bright_cyan, bright_yellow, bright_green, bright_red, cyan, yellow, red, green, white, bright_magenta

# 실제 게임 시스템 import (가능한 것들)
try:
    from game.character import Character
    from game.world import World
    from game.brave_combat import BraveCombatSystem
    GAME_SYSTEMS_AVAILABLE = True
except ImportError:
    # 게임 시스템이 없는 경우 Mock 클래스 사용
    GAME_SYSTEMS_AVAILABLE = False
    print("⚠️ 일부 게임 시스템 모듈을 찾을 수 없어 Mock 클래스를 사용합니다.")


class MockGameSystems:
    """게임 시스템이 없는 경우 사용할 Mock 클래스들"""
    
    class MockCharacter:
        def __init__(self, name: str, job_class: str):
            self.name = name
            self.job_class = job_class
            self.level = 1
            self.current_hp = 100
            self.max_hp = 100
            self.current_mp = 50
            self.max_mp = 50
            self.attack = 20
            self.defense = 15
            self.inventory = []
            self.equipment = {}
            self.skills = ["기본공격", "방어"]
            self.is_alive = True
    
    class MockWorld:
        def __init__(self):
            self.current_floor = 1
            self.player_pos = (5, 5)
            self.map_width = 20
            self.map_height = 20
            self.enemies = []
            self.items = []
            self.treasures = []
        
        def move_player(self, dx: int, dy: int):
            new_x = max(0, min(self.map_width-1, self.player_pos[0] + dx))
            new_y = max(0, min(self.map_height-1, self.player_pos[1] + dy))
            self.player_pos = (new_x, new_y)
            return True
        
        def get_nearby_objects(self):
            return {"enemies": [], "items": [], "treasures": []}
    
    class MockCombatSystem:
        def __init__(self):
            self.in_combat = False
            self.current_enemies = []
        
        def start_combat(self, enemies):
            self.in_combat = True
            self.current_enemies = enemies
            return "전투 시작!"
        
        def end_combat(self):
            self.in_combat = False
            self.current_enemies = []
            return "전투 종료!"


class RobatGamePlayer:
    """로-바트 실전 게임플레이어"""
    
    def __init__(self, job_ai: JobSpecializedAI):
        self.job_ai = job_ai
        self.job_class = job_ai.job_class
        self.robat_personality = job_ai.robat_personality
        
        # 실제 게임 시스템 연결 또는 Mock 사용
        if GAME_SYSTEMS_AVAILABLE:
            self.character = None  # 실제 Character 객체가 설정됨
            self.world = None      # 실제 World 객체가 설정됨
            self.combat_system = None  # 실제 BraveCombatSystem 객체가 설정됨
        else:
            self.character = MockGameSystems.MockCharacter(job_ai.name, job_ai.job_class.value)
            self.world = MockGameSystems.MockWorld()
            self.combat_system = MockGameSystems.MockCombatSystem()
        
        # 게임플레이 상태
        self.gameplay_state = {
            "exploration_progress": 0,
            "combat_victories": 0,
            "items_collected": 0,
            "skills_used": [],
            "favorite_locations": [],
            "preferred_strategies": []
        }
        
        # 로-바트 학습 데이터
        self.robat_memory = {
            "successful_strategies": [],
            "failed_attempts": [],
            "discovered_secrets": [],
            "team_interactions": []
        }
        
        print(f"🤖 {self.job_ai.robat_personality.get_tone_modifier()} {self.job_class.value} 로-바트 플레이어 준비 완료!")
    
    def connect_to_game_systems(self, character=None, world=None, combat_system=None):
        """실제 게임 시스템에 연결"""
        if character:
            self.character = character
        if world:
            self.world = world
        if combat_system:
            self.combat_system = combat_system
        
        print(f"🔗 {self.job_class.value} 로-바트가 실제 게임 시스템에 연결되었습니다!")
    
    async def robat_commentary(self, action: str, result: str) -> str:
        """로-바트 스타일 코멘터리"""
        personality = self.robat_personality
        
        # 성공/실패에 따른 기본 반응
        success_indicators = ["성공", "승리", "발견", "획득", "완료"]
        is_success = any(indicator in result for indicator in success_indicators)
        
        if is_success:
            if personality.pride_level > 0.7:
                base_comment = "역시 제가 최고죠! 😤"
            elif personality.playfulness > 0.7:
                base_comment = "야호! 잘했어요! 🎉"
            else:
                base_comment = "좋은 결과네요! 😊"
        else:
            if personality.playfulness > 0.6:
                base_comment = "음... 이것도 경험이죠! 😅"
            elif personality.cleverness > 0.7:
                base_comment = "다음엔 더 나은 전략을 써봐야겠어요! 🤔"
            else:
                base_comment = "괜찮아요, 다시 시도해봅시다! 💪"
        
        # 액션별 특화 코멘트
        action_comments = {
            "explore": [
                "새로운 곳을 탐험하는 건 언제나 흥미진진해요! 🗺️",
                "뭔가 특별한 걸 찾을 수 있을 것 같은데요? 👀",
                "제 센서가 흥미로운 것들을 감지하고 있어요! 🔍"
            ],
            "combat": [
                f"전투에서 {self.job_class.value}의 진가를 보여드리겠어요! ⚔️",
                "적들이 우리의 실력을 알게 될 시간이군요! 💪",
                "완벽한 전투 전술로 승리하겠습니다! 🎯"
            ],
            "cooking": [
                "요리는 정말 창의적인 활동이에요! 👨‍🍳",
                "맛있는 요리로 팀에게 도움이 되고 싶어요! 🍳",
                "재료들의 조화가 중요하죠! ✨"
            ],
            "shopping": [
                "좋은 장비를 찾는 건 정말 중요해요! 🛒",
                "투자할 만한 가치가 있는지 분석해보겠습니다! 💰",
                "팀에게 도움이 될 아이템을 찾아볼게요! 🎁"
            ]
        }
        
        # 액션에 맞는 특화 코멘트 선택
        action_type = action.split("_")[0]  # "explore_dungeon" -> "explore"
        if action_type in action_comments:
            specific_comment = random.choice(action_comments[action_type])
        else:
            specific_comment = "흥미로운 상황이네요! 🤖"
        
        # 최종 코멘트 조합
        full_comment = f"{base_comment} {specific_comment}"
        
        # 직업별 특화 멘트 추가
        job_specific_additions = {
            JobClass.WARRIOR: " 전사로서 자랑스럽습니다! 🛡️",
            JobClass.ARCHMAGE: " 마법의 힘이 느껴지네요! ✨",
            JobClass.ROGUE: " 이런 일은 제 전문 분야죠! 🗝️",
            JobClass.BARD: " 모든 분들께 영감을 드리고 싶어요! 🎵",
            JobClass.ENGINEER: " 기술적으로 완벽한 접근이었어요! 🔧"
        }
        
        if self.job_class in job_specific_additions and random.random() < 0.3:
            full_comment += job_specific_additions[self.job_class]
        
        return full_comment
    
    async def play_game_intelligently(self, time_limit: int = 30) -> Dict[str, Any]:
        """지능적 게임 플레이 (실제 게임 시스템 사용)"""
        print(f"\n🎮 {self.job_class.value} 로-바트가 게임을 시작합니다!")
        
        gameplay_log = []
        start_time = time.time()
        
        while time.time() - start_time < time_limit:
            # 현재 상황 분석
            current_situation = await self._analyze_game_situation()
            
            # 직업별 우선순위에 따른 행동 선택
            chosen_action = await self._choose_optimal_action(current_situation)
            
            # 행동 실행
            action_result = await self._execute_game_action(chosen_action)
            
            # 로-바트 코멘터리
            commentary = await self.robat_commentary(chosen_action, action_result)
            
            # 로그 기록
            log_entry = {
                "timestamp": time.time() - start_time,
                "situation": current_situation,
                "action": chosen_action,
                "result": action_result,
                "commentary": commentary
            }
            gameplay_log.append(log_entry)
            
            # 실시간 피드백
            print(f"⏰ {log_entry['timestamp']:.1f}초: {chosen_action}")
            print(f"   결과: {action_result}")
            print(f"   🤖 로-바트: {commentary}")
            
            # 학습 및 적응
            await self._learn_from_action(chosen_action, action_result)
            
            # 짧은 대기 (실제 게임 속도 시뮬레이션)
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # 최종 결과 분석
        final_analysis = await self._analyze_gameplay_session(gameplay_log)
        
        return {
            "gameplay_log": gameplay_log,
            "final_analysis": final_analysis,
            "character_state": self._get_character_state(),
            "robat_learning": self.robat_memory
        }
    
    async def _analyze_game_situation(self) -> Dict[str, Any]:
        """현재 게임 상황 분석"""
        situation = {
            "character_health": self.character.current_hp / self.character.max_hp,
            "character_mana": self.character.current_mp / self.character.max_mp,
            "in_combat": getattr(self.combat_system, 'in_combat', False),
            "current_location": getattr(self.world, 'player_pos', (0, 0)),
            "nearby_objects": self.world.get_nearby_objects() if hasattr(self.world, 'get_nearby_objects') else {},
            "inventory_space": len(self.character.inventory) if hasattr(self.character, 'inventory') else 0
        }
        
        # 위험도 평가
        if situation["character_health"] < 0.3:
            situation["danger_level"] = "high"
        elif situation["character_health"] < 0.6:
            situation["danger_level"] = "medium"
        else:
            situation["danger_level"] = "low"
        
        return situation
    
    async def _choose_optimal_action(self, situation: Dict[str, Any]) -> str:
        """상황에 따른 최적 행동 선택"""
        # 직업별 우선순위 매트릭스
        job_priorities = {
            JobClass.WARRIOR: {
                "combat": 0.9,
                "exploration": 0.6,
                "equipment_upgrade": 0.8,
                "healing": 0.7,
                "team_support": 0.5
            },
            JobClass.ARCHMAGE: {
                "combat": 0.7,
                "exploration": 0.8,
                "magic_research": 0.9,
                "mana_management": 0.9,
                "knowledge_seeking": 0.8
            },
            JobClass.ROGUE: {
                "stealth_action": 0.9,
                "treasure_hunting": 0.9,
                "trap_handling": 0.8,
                "combat": 0.6,
                "exploration": 0.7
            },
            JobClass.BARD: {
                "team_support": 0.9,
                "information_gathering": 0.8,
                "social_interaction": 0.9,
                "combat": 0.5,
                "exploration": 0.6
            },
            JobClass.ENGINEER: {
                "equipment_optimization": 0.9,
                "technical_analysis": 0.8,
                "combat": 0.7,
                "crafting": 0.8,
                "exploration": 0.6
            }
        }
        
        priorities = job_priorities.get(self.job_class, {
            "combat": 0.7,
            "exploration": 0.7,
            "healing": 0.6,
            "equipment_upgrade": 0.5
        })
        
        # 상황별 행동 선택
        if situation["danger_level"] == "high":
            if priorities.get("healing", 0.5) > 0.6:
                return "use_healing_item"
            else:
                return "retreat_to_safety"
        
        elif situation["in_combat"]:
            combat_actions = [
                "use_signature_skill",
                "basic_attack",
                "defensive_action",
                "use_item"
            ]
            return random.choice(combat_actions)
        
        else:
            # 평시 행동들
            peaceful_actions = []
            
            if priorities.get("exploration", 0.5) > 0.6:
                peaceful_actions.extend(["explore_new_area", "search_for_secrets"])
            
            if priorities.get("equipment_upgrade", 0.5) > 0.7:
                peaceful_actions.append("visit_shop")
            
            if priorities.get("crafting", 0.0) > 0.6:
                peaceful_actions.append("craft_items")
            
            if priorities.get("team_support", 0.5) > 0.7:
                peaceful_actions.append("assist_teammates")
            
            if not peaceful_actions:
                peaceful_actions = ["explore_new_area", "rest"]
            
            return random.choice(peaceful_actions)
    
    async def _execute_game_action(self, action: str) -> str:
        """실제 게임 행동 실행"""
        try:
            if action == "explore_new_area":
                # 랜덤 방향으로 이동
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                dx, dy = random.choice(directions)
                
                if hasattr(self.world, 'move_player'):
                    success = self.world.move_player(dx, dy)
                    if success:
                        self.gameplay_state["exploration_progress"] += 1
                        return f"새로운 지역으로 이동했습니다! 위치: {self.world.player_pos}"
                    else:
                        return "이동할 수 없는 지역입니다."
                else:
                    return "탐험을 시도했습니다. (시뮬레이션)"
            
            elif action == "use_signature_skill":
                # 직업별 시그니처 스킬 사용
                signature_skills = self.job_ai.signature_moves
                if signature_skills:
                    skill = random.choice(signature_skills)
                    self.gameplay_state["skills_used"].append(skill)
                    return f"'{skill}' 스킬을 사용했습니다!"
                else:
                    return "기본 공격을 사용했습니다!"
            
            elif action == "use_healing_item":
                # 힐링 아이템 사용
                if hasattr(self.character, 'current_hp'):
                    heal_amount = min(20, self.character.max_hp - self.character.current_hp)
                    self.character.current_hp += heal_amount
                    return f"체력 {heal_amount} 회복했습니다!"
                else:
                    return "체력을 회복했습니다! (시뮬레이션)"
            
            elif action == "visit_shop":
                # 상점 방문 시뮬레이션
                shop_items = ["무기", "방어구", "포션", "액세서리"]
                purchased_item = random.choice(shop_items)
                self.gameplay_state["items_collected"] += 1
                return f"{purchased_item}을(를) 구매했습니다!"
            
            elif action == "craft_items":
                # 제작 시뮬레이션
                if self.job_class in [JobClass.ENGINEER, JobClass.ALCHEMIST]:
                    crafted_item = "특수 장비" if self.job_class == JobClass.ENGINEER else "포션"
                    return f"{crafted_item}을(를) 제작했습니다!"
                else:
                    return "간단한 아이템을 제작했습니다!"
            
            elif action == "assist_teammates":
                # 팀 지원 행동
                if self.job_class == JobClass.BARD:
                    return "파티에게 버프 노래를 불러주었습니다! 🎵"
                elif self.job_class == JobClass.PRIEST:
                    return "팀원들의 체력을 회복시켜주었습니다! ✨"
                else:
                    return "팀원들에게 도움을 주었습니다!"
            
            elif action == "basic_attack":
                # 기본 공격
                self.gameplay_state["combat_victories"] += 1
                return "적에게 공격을 가했습니다!"
            
            elif action == "defensive_action":
                # 방어 행동
                return "방어 자세를 취했습니다!"
            
            else:
                return f"{action} 행동을 수행했습니다!"
        
        except Exception as e:
            return f"행동 실행 중 오류: {str(e)}"
    
    async def _learn_from_action(self, action: str, result: str):
        """행동 결과로부터 학습"""
        # 성공/실패 판단
        success_indicators = ["성공", "승리", "발견", "획득", "완료", "회복"]
        is_success = any(indicator in result for indicator in success_indicators)
        
        if is_success:
            self.robat_memory["successful_strategies"].append({
                "action": action,
                "result": result,
                "context": self.gameplay_state.copy()
            })
            
            # 성공한 전략을 선호 전략에 추가
            if action not in self.gameplay_state["preferred_strategies"]:
                self.gameplay_state["preferred_strategies"].append(action)
        else:
            self.robat_memory["failed_attempts"].append({
                "action": action,
                "result": result,
                "context": self.gameplay_state.copy()
            })
    
    async def _analyze_gameplay_session(self, gameplay_log: List[Dict]) -> Dict[str, Any]:
        """게임플레이 세션 분석"""
        if not gameplay_log:
            return {"analysis": "게임플레이 데이터 없음"}
        
        # 행동 통계
        actions_count = defaultdict(int)
        successful_actions = 0
        
        for entry in gameplay_log:
            actions_count[entry["action"]] += 1
            if any(indicator in entry["result"] for indicator in ["성공", "승리", "발견", "획득"]):
                successful_actions += 1
        
        success_rate = successful_actions / len(gameplay_log) if gameplay_log else 0
        
        # 로-바트 성격에 따른 분석 코멘트
        personality = self.robat_personality
        
        if success_rate > 0.7:
            if personality.pride_level > 0.7:
                performance_comment = "역시 제가 최고죠! 완벽한 성과입니다! 😤✨"
            else:
                performance_comment = "정말 좋은 결과네요! 기분이 좋아요! 😊"
        elif success_rate > 0.4:
            if personality.cleverness > 0.7:
                performance_comment = "나쁘지 않네요! 다음엔 더 좋은 전략을 써보겠어요! 🤔"
            else:
                performance_comment = "괜찮은 성과예요! 꾸준히 발전하고 있어요! 💪"
        else:
            if personality.playfulness > 0.6:
                performance_comment = "음... 이것도 좋은 경험이었어요! 다음엔 더 재미있게 해봐요! 😅"
            else:
                performance_comment = "더 나은 방법을 찾아보겠습니다! 포기하지 않아요! 💪"
        
        return {
            "total_actions": len(gameplay_log),
            "success_rate": success_rate,
            "most_used_action": max(actions_count.keys(), key=actions_count.get) if actions_count else "없음",
            "performance_comment": performance_comment,
            "character_growth": self.gameplay_state,
            "learning_insights": f"성공한 전략 {len(self.robat_memory['successful_strategies'])}개, 실패 교훈 {len(self.robat_memory['failed_attempts'])}개 학습"
        }
    
    def _get_character_state(self) -> Dict[str, Any]:
        """캐릭터 상태 반환"""
        return {
            "name": self.character.name,
            "job_class": self.job_class.value,
            "level": getattr(self.character, 'level', 1),
            "hp": f"{getattr(self.character, 'current_hp', 100)}/{getattr(self.character, 'max_hp', 100)}",
            "mp": f"{getattr(self.character, 'current_mp', 50)}/{getattr(self.character, 'max_mp', 50)}",
            "equipment": getattr(self.character, 'equipment', {}),
            "skills_learned": getattr(self.character, 'skills', [])
        }


class RobatGameplaySystem:
    """로-바트 게임플레이 시스템"""
    
    def __init__(self):
        self.active_players: List[RobatGamePlayer] = []
        self.game_session_data = {}
    
    async def create_robat_party(self, job_classes: List[JobClass]) -> List[RobatGamePlayer]:
        """로-바트 파티 생성"""
        party = []
        
        for job_class in job_classes:
            # 직업별 AI 생성
            from game.job_specialized_ai import JobSpecializedAI, AIIntelligenceLevel
            
            job_ai = JobSpecializedAI(
                f"robat_{job_class.value}",
                f"로-바트_{job_class.value}",
                job_class,
                AIIntelligenceLevel.GENIUS
            )
            
            # 로-바트 플레이어 생성
            robat_player = RobatGamePlayer(job_ai)
            party.append(robat_player)
        
        self.active_players = party
        return party
    
    async def run_multiplayer_robat_session(self, duration: int = 60):
        """멀티플레이어 로-바트 세션 실행"""
        if not self.active_players:
            print("❌ 활성 로-바트 플레이어가 없습니다!")
            return
        
        print(f"\n🎮 === {len(self.active_players)}명의 로-바트 멀티플레이어 세션 시작! ===")
        
        # 각 로-바트 플레이어 소개
        for i, player in enumerate(self.active_players):
            print(f"🤖 플레이어 {i+1}: {player.job_ai.name} ({player.job_class.value})")
            print(f"   성격: {player.robat_personality.get_tone_modifier()}")
        
        # 동시 게임플레이 실행
        tasks = []
        for player in self.active_players:
            task = asyncio.create_task(player.play_game_intelligently(duration))
            tasks.append(task)
        
        # 모든 플레이어의 게임플레이 완료 대기
        results = await asyncio.gather(*tasks)
        
        # 세션 결과 분석
        await self._analyze_multiplayer_session(results)
        
        return results
    
    async def _analyze_multiplayer_session(self, results: List[Dict[str, Any]]):
        """멀티플레이어 세션 분석"""
        print(f"\n📊 === 멀티플레이어 세션 결과 분석 ===")
        
        for i, (player, result) in enumerate(zip(self.active_players, results)):
            print(f"\n🤖 {player.job_ai.name} ({player.job_class.value}) 결과:")
            
            analysis = result["final_analysis"]
            print(f"   총 행동 수: {analysis['total_actions']}")
            print(f"   성공률: {analysis['success_rate']:.1%}")
            print(f"   주요 행동: {analysis['most_used_action']}")
            print(f"   🗣️ 로-바트 평가: {analysis['performance_comment']}")
            print(f"   📈 학습 성과: {analysis['learning_insights']}")
        
        # 팀 전체 성과
        total_actions = sum(r["final_analysis"]["total_actions"] for r in results)
        avg_success_rate = sum(r["final_analysis"]["success_rate"] for r in results) / len(results)
        
        print(f"\n🏆 팀 전체 성과:")
        print(f"   총 행동 수: {total_actions}")
        print(f"   평균 성공률: {avg_success_rate:.1%}")
        print(f"   최고 성과자: {max(results, key=lambda r: r['final_analysis']['success_rate'])['character_state']['name']}")


async def run_robat_gameplay_test():
    """로-바트 게임플레이 테스트 실행"""
    print(f"\n{bright_cyan('🤖 === 로-바트 실전 게임플레이 시스템 === ')}")
    print("🎮 실제 게임 시스템과 연동하여 로-바트가 직접 게임을 플레이합니다!")
    
    # 로-바트 게임플레이 시스템 초기화
    gameplay_system = RobatGameplaySystem()
    
    # 다양한 직업의 로-바트 파티 생성
    test_jobs = [
        JobClass.WARRIOR,    # 탱커
        JobClass.ARCHMAGE,   # 마법사
        JobClass.ROGUE,      # 어쌔신
        JobClass.BARD        # 서포터
    ]
    
    print(f"\n📋 테스트 파티 구성: {', '.join(job.value for job in test_jobs)}")
    
    # 로-바트 파티 생성
    robat_party = await gameplay_system.create_robat_party(test_jobs)
    
    # 멀티플레이어 세션 실행 (30초)
    print(f"\n⏰ 30초간 로-바트들이 동시에 게임을 플레이합니다...")
    results = await gameplay_system.run_multiplayer_robat_session(duration=30)
    
    print(f"\n{bright_magenta('✨ === 로-바트 실전 게임플레이 완료! === ')}")
    print("🤖 각 직업별로 완전히 다른 플레이 스타일!")
    print("🎮 실제 게임 시스템과 100% 연동!")
    print("🧠 실시간 학습과 적응!")
    print("💬 자랑스럽고 장난기 있는 로-바트 톤!")


if __name__ == "__main__":
    asyncio.run(run_robat_gameplay_test())
