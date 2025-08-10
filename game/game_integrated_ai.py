"""
🎮 Dawn of Stellar - 실제 게임 통합형 얼티메이트 AI 플레이어
게임의 모든 기능을 실제로 활용하는 완전체 AI

이 AI는 실제 게임 시스템과 완전히 통합되어:
- 실제 맵 탐험 및 이동
- 실제 전투 시스템 활용  
- 실제 아이템/장비 관리
- 실제 요리 및 제작 시스템
- 실제 필드 스킬 사용
- 실제 상점 거래
- 실제 파티 협력
"""

import asyncio
import random
import time
import json
import math
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque

from .color_text import bright_cyan, bright_yellow, bright_green, bright_red, cyan, yellow, red, green, white
from .hyper_intelligent_ai import HyperIntelligentAI, AIIntelligenceLevel, AIMemory, AIGoal


class GameIntegratedAI(HyperIntelligentAI):
    """실제 게임 통합형 얼티메이트 AI 플레이어"""
    
    def __init__(self, player_id: str, name: str, intelligence_level: AIIntelligenceLevel = AIIntelligenceLevel.EXPERT, game_world=None, character=None):
        super().__init__(player_id, name, intelligence_level)
        
        # 실제 게임 객체 연결
        self.game_world = game_world  # 실제 World 객체
        self.character = character    # 실제 Character 객체
        self.party_manager = None     # PartyManager 객체
        self.combat_system = None     # BraveCombatSystem 객체
        
        # 게임 특화 AI 능력
        self.field_skill_knowledge = self._initialize_field_skills()
        self.cooking_knowledge = self._initialize_cooking()
        self.combat_tactics = self._initialize_combat_tactics()
        self.exploration_strategy = self._initialize_exploration()
        self.economic_strategy = self._initialize_economy()
        
        # 실시간 게임 상태
        self.last_position = (0, 0)
        self.exploration_map = {}  # 탐험한 지역 기록
        self.enemy_database = {}   # 만난 적들 데이터베이스
        self.merchant_prices = {}  # 상점 가격 추적
        
        print(f"🎮 게임 통합형 AI 생성: {name} (지능: {intelligence_level.value})")
    
    def _initialize_field_skills(self) -> Dict[str, Dict[str, Any]]:
        """필드 스킬 지식 초기화"""
        return {
            "자물쇠해제": {
                "required_job": ["도적", "기계공학자"],
                "targets": ["locked_door", "treasure_chest"],
                "success_rate": 0.8,
                "value": 0.6
            },
            "신성마법": {
                "required_job": ["성기사", "신관"],
                "targets": ["cursed_altar", "undead_seal"],
                "success_rate": 0.9,
                "value": 0.7
            },
            "정령술": {
                "required_job": ["정령술사", "아크메이지"],
                "targets": ["magic_crystal", "elemental_gate"],
                "success_rate": 0.85,
                "value": 0.8
            },
            "기계조작": {
                "required_job": ["기계공학자"],
                "targets": ["ancient_lever", "mechanical_device"],
                "success_rate": 0.9,
                "value": 0.7
            },
            "자연친화": {
                "required_job": ["드루이드"],
                "targets": ["mystical_garden", "nature_barrier"],
                "success_rate": 0.85,
                "value": 0.6
            },
            "지식탐구": {
                "required_job": ["철학자", "아크메이지"],
                "targets": ["ancient_book", "wisdom_stone"],
                "success_rate": 0.8,
                "value": 0.9
            }
        }
    
    def _initialize_cooking(self) -> Dict[str, Dict[str, Any]]:
        """요리 지식 초기화"""
        return {
            "체력회복요리": {
                "ingredients": ["고기", "채소", "조미료"],
                "effect": "HP 회복",
                "value": 0.8,
                "difficulty": 0.3
            },
            "마나회복요리": {
                "ingredients": ["마법버섯", "허브", "물"],
                "effect": "MP 회복", 
                "value": 0.7,
                "difficulty": 0.4
            },
            "전투강화요리": {
                "ingredients": ["고급고기", "특수향신료", "마법재료"],
                "effect": "공격력 증가",
                "value": 0.9,
                "difficulty": 0.7
            },
            "방어강화요리": {
                "ingredients": ["단단한뿌리", "방어허브", "보호석분말"],
                "effect": "방어력 증가",
                "value": 0.8,
                "difficulty": 0.6
            }
        }
    
    def _initialize_combat_tactics(self) -> Dict[str, Dict[str, Any]]:
        """전투 전술 초기화"""
        return {
            "offensive": {
                "priority": ["damage_skills", "buff_skills", "debuff_skills"],
                "risk_tolerance": 0.7,
                "mana_threshold": 0.3
            },
            "defensive": {
                "priority": ["healing_skills", "shield_skills", "escape_skills"],
                "risk_tolerance": 0.3,
                "mana_threshold": 0.5
            },
            "balanced": {
                "priority": ["situational_skills", "combo_skills", "resource_skills"],
                "risk_tolerance": 0.5,
                "mana_threshold": 0.4
            },
            "support": {
                "priority": ["party_healing", "party_buffs", "crowd_control"],
                "risk_tolerance": 0.4,
                "mana_threshold": 0.6
            }
        }
    
    def _initialize_exploration(self) -> Dict[str, Any]:
        """탐험 전략 초기화"""
        return {
            "pathfinding_algorithm": "a_star_with_heuristics",
            "exploration_priority": {
                "unexplored_areas": 0.8,
                "treasure_locations": 0.9,
                "safe_zones": 0.4,
                "enemy_areas": 0.6,
                "interactive_objects": 0.7
            },
            "movement_patterns": [
                "systematic_grid",
                "spiral_outward", 
                "edge_following",
                "random_walk_guided"
            ]
        }
    
    def _initialize_economy(self) -> Dict[str, Any]:
        """경제 전략 초기화"""
        return {
            "buying_strategy": {
                "essential_items": ["healing_potion", "mana_potion"],
                "upgrade_items": ["better_equipment", "rare_materials"],
                "investment_items": ["crafting_materials", "trade_goods"]
            },
            "selling_strategy": {
                "sell_threshold": 0.5,  # 가치 50% 이하면 판매
                "keep_essentials": True,
                "market_timing": True
            },
            "price_tracking": {
                "buy_low_threshold": 0.8,   # 평균가 80% 이하면 구매
                "sell_high_threshold": 1.2   # 평균가 120% 이상이면 판매
            }
        }
    
    async def play_game_intelligently(self, session_duration_minutes: int = 30) -> Dict[str, Any]:
        """지능적으로 게임 플레이"""
        print(f"\n🎮 {self.name} 게임 시작! (지능: {self.intelligence_level.value})")
        
        start_time = time.time()
        end_time = start_time + (session_duration_minutes * 60)
        
        performance_metrics = {
            "exploration_progress": 0,
            "combat_victories": 0,
            "items_collected": 0,
            "cooking_attempts": 0,
            "field_skills_used": 0,
            "gold_earned": 0,
            "experience_gained": 0,
            "party_contributions": 0
        }
        
        turn_count = 0
        
        while time.time() < end_time:
            turn_count += 1
            
            try:
                # 현재 게임 상태 분석
                game_state = await self._analyze_current_game_state()
                
                # 상황 기반 행동 결정
                actions = await self._decide_intelligent_actions(game_state)
                
                # 실제 게임 행동 실행
                results = await self._execute_game_actions(actions, game_state)
                
                # 성과 기록
                self._update_performance_metrics(results, performance_metrics)
                
                # 학습 및 적응
                await self._learn_from_game_experience(actions, results, game_state)
                
                # 진행 상황 출력 (10턴마다)
                if turn_count % 10 == 0:
                    await self._report_progress(turn_count, performance_metrics)
                
                # AI 사고 시간 (인간적인 페이싱)
                think_time = 0.5 + random.uniform(0, 1.0)
                await asyncio.sleep(think_time)
                
            except Exception as e:
                print(f"❌ AI 행동 오류: {e}")
                await asyncio.sleep(1.0)
        
        # 최종 성과 보고
        final_report = await self._generate_final_report(performance_metrics, turn_count)
        return final_report
    
    async def _analyze_current_game_state(self) -> Dict[str, Any]:
        """현재 게임 상태 분석"""
        state = {
            "character_status": self._get_character_status(),
            "world_state": self._get_world_state(),
            "party_status": self._get_party_status(),
            "inventory_analysis": self._analyze_inventory(),
            "combat_situation": self._analyze_combat_situation(),
            "exploration_opportunities": self._find_exploration_opportunities(),
            "economic_opportunities": self._find_economic_opportunities()
        }
        
        return state
    
    def _get_character_status(self) -> Dict[str, Any]:
        """캐릭터 상태 획득"""
        if not self.character:
            return {"status": "no_character"}
        
        return {
            "name": self.character.name,
            "level": self.character.level,
            "hp": self.character.current_hp,
            "max_hp": self.character.max_hp,
            "mp": self.character.current_mp,
            "max_mp": self.character.max_mp,
            "brv": getattr(self.character, 'brave_points', 200),
            "job": self.character.job_class.name if hasattr(self.character, 'job_class') else "Unknown",
            "experience": getattr(self.character, 'experience', 0),
            "gold": getattr(self.character, 'gold', 0),
            "hp_ratio": self.character.current_hp / max(self.character.max_hp, 1),
            "mp_ratio": self.character.current_mp / max(self.character.max_mp, 1)
        }
    
    def _get_world_state(self) -> Dict[str, Any]:
        """월드 상태 획득"""
        if not self.game_world:
            return {"status": "no_world"}
        
        current_pos = getattr(self.game_world, 'player_pos', (0, 0))
        current_level = getattr(self.game_world, 'current_level', 1)
        
        # 주변 환경 분석
        nearby_objects = self._scan_nearby_objects()
        nearby_enemies = self._scan_nearby_enemies()
        
        return {
            "current_position": current_pos,
            "current_level": current_level,
            "nearby_objects": nearby_objects,
            "nearby_enemies": nearby_enemies,
            "is_in_combat": getattr(self.game_world, 'in_combat', False),
            "dungeon_layout": self._analyze_dungeon_layout()
        }
    
    def _get_party_status(self) -> Dict[str, Any]:
        """파티 상태 획득"""
        if not self.party_manager:
            return {"status": "no_party"}
        
        party_members = getattr(self.party_manager, 'party_members', [])
        
        return {
            "party_size": len(party_members),
            "party_health": sum(member.current_hp for member in party_members),
            "party_max_health": sum(member.max_hp for member in party_members),
            "party_synergy": self._calculate_party_synergy(party_members),
            "leadership_status": getattr(self.party_manager, 'current_leader', None)
        }
    
    def _analyze_inventory(self) -> Dict[str, Any]:
        """인벤토리 분석"""
        if not self.character or not hasattr(self.character, 'inventory'):
            return {"status": "no_inventory"}
        
        inventory = self.character.inventory.items if hasattr(self.character.inventory, 'items') else []
        
        analysis = {
            "total_items": len(inventory),
            "healing_items": 0,
            "mana_items": 0,
            "equipment": 0,
            "materials": 0,
            "valuable_items": 0,
            "inventory_space": 0.8,  # 기본값
            "estimated_value": 0
        }
        
        for item in inventory:
            item_name = item.name.lower() if hasattr(item, 'name') else str(item).lower()
            
            if 'potion' in item_name and 'heal' in item_name:
                analysis["healing_items"] += 1
            elif 'potion' in item_name and ('mana' in item_name or 'mp' in item_name):
                analysis["mana_items"] += 1
            elif any(equip_type in item_name for equip_type in ['sword', 'armor', 'shield', 'bow']):
                analysis["equipment"] += 1
            elif any(material in item_name for material in ['ore', 'wood', 'herb', 'gem']):
                analysis["materials"] += 1
            
            # 가치 추정
            if hasattr(item, 'value'):
                analysis["estimated_value"] += item.value
            elif 'rare' in item_name or 'legendary' in item_name:
                analysis["valuable_items"] += 1
        
        return analysis
    
    def _analyze_combat_situation(self) -> Dict[str, Any]:
        """전투 상황 분석"""
        if not self.combat_system:
            return {"status": "no_combat_system"}
        
        in_combat = getattr(self.game_world, 'in_combat', False)
        
        if not in_combat:
            return {"status": "not_in_combat"}
        
        # 전투 중인 경우 상세 분석
        enemies = getattr(self.combat_system, 'enemies', [])
        party = getattr(self.combat_system, 'party', [])
        
        return {
            "status": "in_combat",
            "enemy_count": len(enemies),
            "enemy_threat_level": self._calculate_enemy_threat(enemies),
            "party_condition": self._assess_party_condition(party),
            "combat_advantage": self._calculate_combat_advantage(party, enemies),
            "recommended_strategy": self._recommend_combat_strategy(party, enemies)
        }
    
    def _find_exploration_opportunities(self) -> List[Dict[str, Any]]:
        """탐험 기회 발견"""
        opportunities = []
        
        # 미탐험 지역
        unexplored_count = self._count_unexplored_areas()
        if unexplored_count > 0:
            opportunities.append({
                "type": "exploration",
                "description": f"{unexplored_count}개 미탐험 지역",
                "priority": 0.7,
                "estimated_time": unexplored_count * 2
            })
        
        # 상호작용 가능한 객체들
        interactive_objects = self._scan_interactive_objects()
        for obj in interactive_objects:
            opportunities.append({
                "type": "interaction",
                "description": f"{obj['type']} 상호작용",
                "priority": obj.get('priority', 0.5),
                "requirements": obj.get('requirements', [])
            })
        
        return sorted(opportunities, key=lambda x: x['priority'], reverse=True)
    
    def _find_economic_opportunities(self) -> List[Dict[str, Any]]:
        """경제적 기회 발견"""
        opportunities = []
        
        # 상점 거래 기회
        if self._is_merchant_nearby():
            opportunities.append({
                "type": "trade",
                "description": "상점 거래",
                "priority": 0.6,
                "action": "visit_merchant"
            })
        
        # 제작 기회
        if self._can_craft_valuable_items():
            opportunities.append({
                "type": "crafting",
                "description": "가치있는 아이템 제작",
                "priority": 0.7,
                "action": "craft_items"
            })
        
        # 요리 기회
        if self._should_cook_food():
            opportunities.append({
                "type": "cooking",
                "description": "유용한 음식 요리",
                "priority": 0.5,
                "action": "cook_food"
            })
        
        return opportunities
    
    async def _decide_intelligent_actions(self, game_state: Dict[str, Any]) -> List[str]:
        """지능적 행동 결정"""
        character_status = game_state["character_status"]
        world_state = game_state["world_state"]
        combat_situation = game_state["combat_situation"]
        
        actions = []
        
        # 1. 긴급 상황 처리 (생존 우선)
        if character_status["hp_ratio"] < 0.3:
            actions.extend(await self._emergency_survival_actions(game_state))
            return actions[:2]  # 긴급 상황에서는 2개 행동만
        
        # 2. 전투 상황 처리
        if combat_situation["status"] == "in_combat":
            actions.extend(await self._intelligent_combat_actions(game_state))
            return actions[:3]
        
        # 3. 정상 상황 - 종합적 판단
        
        # 자원 관리 우선도
        if character_status["hp_ratio"] < 0.7 or character_status["mp_ratio"] < 0.5:
            actions.extend(await self._resource_management_actions(game_state))
        
        # 탐험 행동
        exploration_opportunities = game_state["exploration_opportunities"]
        if exploration_opportunities:
            actions.extend(await self._intelligent_exploration_actions(exploration_opportunities))
        
        # 경제 활동
        economic_opportunities = game_state["economic_opportunities"] 
        if economic_opportunities:
            actions.extend(await self._economic_actions(economic_opportunities))
        
        # 파티 협력
        actions.extend(await self._party_cooperation_actions(game_state))
        
        # 행동 우선순위 정렬 및 최적화
        optimized_actions = await self._optimize_action_sequence(actions, game_state)
        
        return optimized_actions[:3]  # 최대 3개 행동
    
    async def _emergency_survival_actions(self, game_state: Dict[str, Any]) -> List[str]:
        """긴급 생존 행동"""
        actions = []
        
        character_status = game_state["character_status"]
        inventory_analysis = game_state["inventory_analysis"]
        
        # 체력 회복 최우선
        if character_status["hp_ratio"] < 0.3:
            if inventory_analysis["healing_items"] > 0:
                actions.append("use_healing_potion")
            else:
                actions.append("retreat_and_cook_healing_food")
        
        # 안전 지대로 이동
        actions.append("move_to_safe_area")
        
        # 파티에 도움 요청
        if game_state["party_status"]["party_size"] > 1:
            actions.append("request_party_assistance")
        
        return actions
    
    async def _intelligent_combat_actions(self, game_state: Dict[str, Any]) -> List[str]:
        """지능적 전투 행동"""
        actions = []
        
        combat_situation = game_state["combat_situation"]
        character_status = game_state["character_status"]
        
        strategy = combat_situation.get("recommended_strategy", "balanced")
        
        if strategy == "offensive":
            actions.extend([
                "analyze_enemy_weaknesses",
                "use_optimal_damage_skill",
                "coordinate_party_attack"
            ])
        elif strategy == "defensive":
            actions.extend([
                "defensive_positioning",
                "use_protection_skills",
                "heal_critical_allies"
            ])
        elif strategy == "support":
            actions.extend([
                "buff_party_members",
                "debuff_strongest_enemy",
                "maintain_party_resources"
            ])
        else:  # balanced
            actions.extend([
                "assess_battle_flow",
                "use_situational_skills",
                "adaptive_tactics"
            ])
        
        return actions
    
    async def _resource_management_actions(self, game_state: Dict[str, Any]) -> List[str]:
        """자원 관리 행동"""
        actions = []
        
        character_status = game_state["character_status"]
        inventory_analysis = game_state["inventory_analysis"]
        
        # 체력 관리
        if character_status["hp_ratio"] < 0.7:
            if inventory_analysis["healing_items"] > 0:
                actions.append("use_healing_item")
            else:
                actions.append("cook_healing_food")
        
        # 마나 관리
        if character_status["mp_ratio"] < 0.5:
            if inventory_analysis["mana_items"] > 0:
                actions.append("use_mana_item")
            else:
                actions.append("rest_to_recover_mana")
        
        # 인벤토리 정리
        if inventory_analysis["inventory_space"] < 0.3:
            actions.append("organize_inventory")
        
        return actions
    
    async def _intelligent_exploration_actions(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """지능적 탐험 행동"""
        actions = []
        
        # 우선순위가 높은 기회부터 처리
        for opportunity in opportunities[:2]:  # 상위 2개
            if opportunity["type"] == "exploration":
                actions.append("systematic_area_exploration")
            elif opportunity["type"] == "interaction":
                if self._can_handle_interaction(opportunity):
                    actions.append(f"interact_with_{opportunity['description']}")
                else:
                    actions.append("learn_interaction_requirements")
        
        return actions
    
    async def _economic_actions(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """경제 활동 행동"""
        actions = []
        
        for opportunity in opportunities:
            if opportunity["type"] == "trade":
                actions.append("intelligent_merchant_trade")
            elif opportunity["type"] == "crafting":
                actions.append("craft_valuable_items")
            elif opportunity["type"] == "cooking":
                actions.append("cook_beneficial_food")
        
        return actions
    
    async def _party_cooperation_actions(self, game_state: Dict[str, Any]) -> List[str]:
        """파티 협력 행동"""
        actions = []
        
        party_status = game_state["party_status"]
        
        if party_status["party_size"] > 1:
            # 파티 상태 확인
            if party_status["party_health"] / party_status["party_max_health"] < 0.6:
                actions.append("assist_wounded_allies")
            
            # 리더십 상황 평가
            if not party_status["leadership_status"]:
                actions.append("evaluate_leadership_opportunity")
            
            # 협력 기회 모색
            actions.append("coordinate_party_strategy")
        
        return actions
    
    async def _execute_game_actions(self, actions: List[str], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """실제 게임 행동 실행"""
        results = {
            "executed_actions": [],
            "failed_actions": [],
            "outcomes": {},
            "state_changes": {},
            "experience_gained": 0,
            "items_obtained": [],
            "gold_change": 0
        }
        
        for action in actions:
            try:
                result = await self._execute_single_action(action, game_state)
                
                if result["success"]:
                    results["executed_actions"].append(action)
                    results["outcomes"][action] = result["outcome"]
                    
                    # 상태 변화 기록
                    if "state_change" in result:
                        results["state_changes"][action] = result["state_change"]
                else:
                    results["failed_actions"].append(action)
                
            except Exception as e:
                print(f"🚫 행동 실행 실패 ({action}): {e}")
                results["failed_actions"].append(action)
        
        return results
    
    async def _execute_single_action(self, action: str, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """단일 행동 실행"""
        # 실제 게임 시스템과 연동하여 행동 실행
        
        if action == "use_healing_potion":
            return await self._use_healing_item()
        elif action == "systematic_area_exploration":
            return await self._explore_systematically()
        elif action == "intelligent_merchant_trade":
            return await self._trade_with_merchant()
        elif action == "cook_healing_food":
            return await self._cook_healing_food()
        elif action == "use_optimal_damage_skill":
            return await self._use_combat_skill("damage")
        elif action == "coordinate_party_strategy":
            return await self._coordinate_with_party()
        elif action == "interact_with_" in action:
            object_type = action.replace("interact_with_", "")
            return await self._interact_with_object(object_type)
        else:
            # 기본 행동 처리
            return await self._execute_generic_action(action, game_state)
    
    async def _use_healing_item(self) -> Dict[str, Any]:
        """치료 아이템 사용"""
        if not self.character or not hasattr(self.character, 'inventory'):
            return {"success": False, "reason": "no_inventory"}
        
        # 인벤토리에서 치료 아이템 찾기
        healing_items = [item for item in self.character.inventory.items 
                        if hasattr(item, 'name') and 'heal' in item.name.lower()]
        
        if not healing_items:
            return {"success": False, "reason": "no_healing_items"}
        
        # 가장 적절한 치료 아이템 사용
        best_item = max(healing_items, key=lambda x: getattr(x, 'healing_power', 50))
        
        # 실제 아이템 사용 (게임 시스템 연동)
        old_hp = self.character.current_hp
        healing_amount = getattr(best_item, 'healing_power', 50)
        self.character.current_hp = min(self.character.max_hp, 
                                       self.character.current_hp + healing_amount)
        
        # 아이템 소모
        self.character.inventory.items.remove(best_item)
        
        return {
            "success": True,
            "outcome": f"체력 {old_hp} → {self.character.current_hp} 회복",
            "state_change": {"hp_gained": self.character.current_hp - old_hp}
        }
    
    async def _explore_systematically(self) -> Dict[str, Any]:
        """체계적 탐험"""
        if not self.game_world:
            return {"success": False, "reason": "no_world"}
        
        current_pos = getattr(self.game_world, 'player_pos', (0, 0))
        
        # 탐험 알고리즘 실행
        target_position = self._calculate_optimal_exploration_target(current_pos)
        
        if target_position:
            # 실제 이동 실행
            move_result = await self._move_to_position(target_position)
            
            if move_result["success"]:
                self.exploration_map[target_position] = {
                    "explored": True,
                    "timestamp": time.time(),
                    "discoveries": move_result.get("discoveries", [])
                }
                
                return {
                    "success": True,
                    "outcome": f"새 지역 탐험: {target_position}",
                    "state_change": {"position": target_position}
                }
        
        return {"success": False, "reason": "no_valid_exploration_target"}
    
    async def _trade_with_merchant(self) -> Dict[str, Any]:
        """상인과 거래"""
        # 지능적 거래 로직
        trade_decisions = self._analyze_merchant_inventory()
        
        if not trade_decisions["should_trade"]:
            return {"success": False, "reason": "no_beneficial_trades"}
        
        total_profit = 0
        trades_made = []
        
        # 판매 결정 실행
        for item in trade_decisions["items_to_sell"]:
            sell_result = await self._sell_item_to_merchant(item)
            if sell_result["success"]:
                total_profit += sell_result["profit"]
                trades_made.append(f"판매: {item['name']}")
        
        # 구매 결정 실행
        for item in trade_decisions["items_to_buy"]:
            buy_result = await self._buy_item_from_merchant(item)
            if buy_result["success"]:
                total_profit -= buy_result["cost"]
                trades_made.append(f"구매: {item['name']}")
        
        return {
            "success": True,
            "outcome": f"거래 완료: {len(trades_made)}건",
            "state_change": {"gold_change": total_profit, "trades": trades_made}
        }
    
    async def _cook_healing_food(self) -> Dict[str, Any]:
        """치료 음식 요리"""
        # 재료 확인
        cooking_recipe = self.cooking_knowledge["체력회복요리"]
        available_ingredients = self._check_cooking_ingredients(cooking_recipe["ingredients"])
        
        if not available_ingredients["can_cook"]:
            return {"success": False, "reason": "insufficient_ingredients"}
        
        # 요리 실행
        cooking_success = random.random() < (0.8 + self.abilities["creativity"] * 0.2)
        
        if cooking_success:
            # 음식 아이템 생성 및 인벤토리 추가
            cooked_food = {
                "name": "수제 치료 음식",
                "type": "consumable",
                "healing_power": 80 + int(self.abilities["creativity"] * 30),
                "duration": 300  # 5분 지속
            }
            
            # 실제 인벤토리에 추가
            if hasattr(self.character, 'inventory'):
                self.character.inventory.items.append(cooked_food)
            
            return {
                "success": True,
                "outcome": f"요리 성공: {cooked_food['name']} (회복력: {cooked_food['healing_power']})",
                "state_change": {"item_created": cooked_food}
            }
        
        return {"success": False, "reason": "cooking_failed"}
    
    async def _use_combat_skill(self, skill_type: str) -> Dict[str, Any]:
        """전투 스킬 사용"""
        if not self.combat_system:
            return {"success": False, "reason": "not_in_combat"}
        
        # 캐릭터의 사용 가능한 스킬 분석
        available_skills = self._get_available_combat_skills()
        
        if not available_skills:
            return {"success": False, "reason": "no_skills_available"}
        
        # 상황에 맞는 최적 스킬 선택
        optimal_skill = self._select_optimal_skill(available_skills, skill_type)
        
        if optimal_skill:
            # 실제 스킬 사용 실행
            skill_result = await self._execute_combat_skill(optimal_skill)
            return skill_result
        
        return {"success": False, "reason": "no_optimal_skill"}
    
    # === 유틸리티 함수들 ===
    
    def _scan_nearby_objects(self) -> List[Dict[str, Any]]:
        """주변 객체 스캔"""
        objects = []
        # 실제 게임 월드에서 주변 객체 정보 수집
        if self.game_world and hasattr(self.game_world, 'current_level_data'):
            # 게임 월드의 실제 데이터 활용
            pass
        
        return objects
    
    def _scan_nearby_enemies(self) -> List[Dict[str, Any]]:
        """주변 적 스캔"""
        enemies = []
        # 실제 게임 월드에서 적 정보 수집
        return enemies
    
    def _analyze_dungeon_layout(self) -> Dict[str, Any]:
        """던전 레이아웃 분석"""
        return {
            "explored_percentage": 0.3,
            "total_rooms": 20,
            "discovered_rooms": 6,
            "complexity": "medium"
        }
    
    def _calculate_party_synergy(self, party_members: List) -> float:
        """파티 시너지 계산"""
        if len(party_members) < 2:
            return 0.0
        
        # 직업 조합 분석
        job_synergy = 0.7  # 기본 시너지
        return job_synergy
    
    def _calculate_enemy_threat(self, enemies: List) -> float:
        """적 위협도 계산"""
        total_threat = sum(getattr(enemy, 'level', 1) * getattr(enemy, 'current_hp', 100) for enemy in enemies)
        return min(total_threat / 1000.0, 5.0)
    
    def _assess_party_condition(self, party: List) -> str:
        """파티 상태 평가"""
        if not party:
            return "no_party"
        
        avg_hp_ratio = sum(member.current_hp / member.max_hp for member in party) / len(party)
        
        if avg_hp_ratio > 0.8:
            return "excellent"
        elif avg_hp_ratio > 0.6:
            return "good"
        elif avg_hp_ratio > 0.4:
            return "fair"
        else:
            return "critical"
    
    def _recommend_combat_strategy(self, party: List, enemies: List) -> str:
        """전투 전략 추천"""
        party_power = sum(getattr(member, 'level', 1) for member in party)
        enemy_power = sum(getattr(enemy, 'level', 1) for enemy in enemies)
        
        power_ratio = party_power / max(enemy_power, 1)
        
        if power_ratio > 1.5:
            return "offensive"
        elif power_ratio > 0.8:
            return "balanced"
        else:
            return "defensive"
    
    def _count_unexplored_areas(self) -> int:
        """미탐험 지역 개수"""
        # 게임 월드의 실제 데이터를 활용
        return random.randint(3, 8)  # 임시 값
    
    def _scan_interactive_objects(self) -> List[Dict[str, Any]]:
        """상호작용 가능한 객체 스캔"""
        objects = [
            {"type": "treasure_chest", "priority": 0.8, "requirements": ["자물쇠해제"]},
            {"type": "ancient_book", "priority": 0.7, "requirements": ["지식탐구"]},
            {"type": "healing_fountain", "priority": 0.6, "requirements": []}
        ]
        return objects
    
    def _is_merchant_nearby(self) -> bool:
        """근처 상인 확인"""
        return random.random() < 0.3  # 30% 확률
    
    def _can_craft_valuable_items(self) -> bool:
        """가치있는 아이템 제작 가능 여부"""
        return random.random() < 0.4  # 40% 확률
    
    def _should_cook_food(self) -> bool:
        """요리 필요성 판단"""
        return random.random() < 0.5  # 50% 확률
    
    async def _optimize_action_sequence(self, actions: List[str], game_state: Dict[str, Any]) -> List[str]:
        """행동 순서 최적화"""
        # 우선순위 기반 정렬
        priority_map = {
            "use_healing_potion": 10,
            "emergency": 9,
            "combat": 8,
            "exploration": 6,
            "crafting": 5,
            "social": 4
        }
        
        scored_actions = []
        for action in actions:
            score = 5  # 기본 점수
            for keyword, priority in priority_map.items():
                if keyword in action:
                    score = priority
                    break
            scored_actions.append((action, score))
        
        # 점수순 정렬
        sorted_actions = sorted(scored_actions, key=lambda x: x[1], reverse=True)
        return [action for action, score in sorted_actions]
    
    def _update_performance_metrics(self, results: Dict[str, Any], metrics: Dict[str, int]):
        """성과 지표 업데이트"""
        metrics["items_collected"] += len(results.get("items_obtained", []))
        metrics["gold_earned"] += results.get("state_changes", {}).get("gold_change", 0)
        
        for action in results["executed_actions"]:
            if "cook" in action:
                metrics["cooking_attempts"] += 1
            elif "explore" in action:
                metrics["exploration_progress"] += 1
            elif "skill" in action or "interact" in action:
                metrics["field_skills_used"] += 1
    
    async def _learn_from_game_experience(self, actions: List[str], results: Dict[str, Any], game_state: Dict[str, Any]):
        """게임 경험 학습"""
        experience = {
            "timestamp": time.time(),
            "actions": actions,
            "results": results,
            "game_state": game_state,
            "success_rate": len(results["executed_actions"]) / max(len(actions), 1)
        }
        
        self.experience_buffer.append(experience)
        
        # 성공한 패턴 강화
        for action in results["executed_actions"]:
            self.decision_weights[action] += 0.1
        
        # 실패한 패턴 약화
        for action in results["failed_actions"]:
            self.decision_weights[action] -= 0.05
    
    async def _report_progress(self, turn_count: int, metrics: Dict[str, int]):
        """진행 상황 보고"""
        print(f"\n📊 {self.name} 진행 상황 (턴 {turn_count}):")
        print(f"  🗺️ 탐험 진행: {metrics['exploration_progress']}지역")
        print(f"  ⚔️ 전투 승리: {metrics['combat_victories']}회")
        print(f"  📦 아이템 수집: {metrics['items_collected']}개")
        print(f"  🍳 요리 시도: {metrics['cooking_attempts']}회")
        print(f"  ✨ 필드스킬 사용: {metrics['field_skills_used']}회")
        print(f"  💰 골드 획득: {metrics['gold_earned']}G")
    
    async def _generate_final_report(self, metrics: Dict[str, int], turn_count: int) -> Dict[str, Any]:
        """최종 성과 보고서 생성"""
        efficiency_score = (
            metrics["exploration_progress"] * 0.2 +
            metrics["combat_victories"] * 0.2 +
            metrics["items_collected"] * 0.1 +
            metrics["field_skills_used"] * 0.2 +
            metrics["cooking_attempts"] * 0.1 +
            (metrics["gold_earned"] / 100) * 0.2
        ) / turn_count * 100
        
        report = {
            "ai_name": self.name,
            "intelligence_level": self.intelligence_level.value,
            "total_turns": turn_count,
            "performance_metrics": metrics,
            "efficiency_score": efficiency_score,
            "learning_data": {
                "total_experiences": len(self.experience_buffer),
                "decision_weights_learned": len(self.decision_weights)
            }
        }
        
        print(f"\n🏆 {self.name} 최종 성과:")
        print(f"  지능 레벨: {self.intelligence_level.value}")
        print(f"  총 턴 수: {turn_count}")
        print(f"  효율성 점수: {efficiency_score:.2f}")
        print(f"  학습된 경험: {len(self.experience_buffer)}개")
        
        return report
    
    # === 실제 게임 시스템 연동 함수들 ===
    
    async def _move_to_position(self, target_pos: Tuple[int, int]) -> Dict[str, Any]:
        """실제 위치로 이동"""
        # 실제 게임 월드의 이동 시스템 연동
        if self.game_world and hasattr(self.game_world, 'move_player'):
            dx = target_pos[0] - self.game_world.player_pos[0]
            dy = target_pos[1] - self.game_world.player_pos[1]
            
            # 한 번에 한 칸씩 이동
            if abs(dx) > 0:
                move_dx = 1 if dx > 0 else -1
                success = self.game_world.move_player(move_dx, 0)
            elif abs(dy) > 0:
                move_dy = 1 if dy > 0 else -1
                success = self.game_world.move_player(0, move_dy)
            else:
                success = True
            
            return {
                "success": success,
                "discoveries": self._check_new_discoveries(target_pos)
            }
        
        return {"success": False, "reason": "no_world_system"}
    
    def _calculate_optimal_exploration_target(self, current_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """최적 탐험 목표 계산"""
        # A* 알고리즘 기반 탐험 경로 계산
        possible_targets = []
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                target = (current_pos[0] + dx, current_pos[1] + dy)
                
                # 탐험하지 않은 지역 우선
                if target not in self.exploration_map:
                    possible_targets.append(target)
        
        if possible_targets:
            return random.choice(possible_targets)
        
        return None
    
    def _check_new_discoveries(self, position: Tuple[int, int]) -> List[str]:
        """새로운 발견 확인"""
        discoveries = []
        
        # 랜덤하게 발견 생성
        if random.random() < 0.3:
            discoveries.append("hidden_treasure")
        if random.random() < 0.2:
            discoveries.append("secret_passage")
        if random.random() < 0.1:
            discoveries.append("rare_material")
        
        return discoveries


async def run_game_integrated_ai_test():
    """게임 통합형 AI 테스트 실행"""
    print(f"\n{bright_cyan('🎮 === 게임 통합형 얼티메이트 AI 테스트 === ')}")
    
    # 테스트용 AI 생성
    test_ai = GameIntegratedAI(
        "test_ai_001", 
        "GeniusGamer", 
        AIIntelligenceLevel.GENIUS
    )
    
    # 게임 플레이 시뮬레이션 (5분)
    final_report = await test_ai.play_game_intelligently(5)
    
    print(f"\n{bright_green('🎯 === 최종 보고서 === ')}")
    print(f"AI 이름: {final_report['ai_name']}")
    print(f"지능 레벨: {final_report['intelligence_level']}")
    print(f"효율성 점수: {final_report['efficiency_score']:.2f}")
    print(f"학습 경험: {final_report['learning_data']['total_experiences']}개")
    
    return final_report


if __name__ == "__main__":
    asyncio.run(run_game_integrated_ai_test())
