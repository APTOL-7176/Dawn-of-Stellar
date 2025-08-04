#!/usr/bin/env python3
"""
🔥 강화된 조우 시스템 - 커서 기반 인터페이스 및 다양한 상호작용
- 직관적인 커서 메뉴 시스템
- 특성 기반 선택지 추가
- 위험도와 보상의 균형
- 파티원별 특화 상호작용
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

try:
    from .cursor_menu_system import CursorMenu
    from .color_text import *
    from .random_encounters import EncounterType, RandomEncounter
    from .character import Character
except ImportError:
    # 폴백 처리
    pass

class InteractionType(Enum):
    """상호작용 타입"""
    INVESTIGATE = "조사하기"
    NEGOTIATE = "협상하기"
    FIGHT = "전투하기"
    FLEE = "도주하기"
    USE_SKILL = "스킬 사용"
    TRADE = "거래하기"
    HELP = "도움주기"
    IGNORE = "무시하기"
    STEAL = "훔치기"
    INTIMIDATE = "위협하기"
    CHARM = "매혹하기"
    TRICK = "속이기"

class EnhancedEncounter:
    """강화된 조우 클래스"""
    
    def __init__(self, encounter_type: EncounterType, title: str, description: str, 
                 min_floor: int = 1, max_floor: int = 30):
        self.encounter_type = encounter_type
        self.title = title
        self.description = description
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.base_interactions = []
        self.special_interactions = []
        
    def get_available_interactions(self, party: List[Character], floor: int) -> List[Dict]:
        """파티 구성과 특성에 따른 가능한 상호작용 목록"""
        interactions = []
        
        # 기본 상호작용
        interactions.extend(self._get_base_interactions())
        
        # 특성 기반 특수 상호작용
        interactions.extend(self._get_trait_based_interactions(party))
        
        # 직업 기반 특수 상호작용
        interactions.extend(self._get_class_based_interactions(party))
        
        # 층수 기반 고급 상호작용
        if floor >= 10:
            interactions.extend(self._get_advanced_interactions())
            
        return interactions
    
    def _get_base_interactions(self) -> List[Dict]:
        """기본 상호작용 목록"""
        return [
            {
                "type": InteractionType.INVESTIGATE,
                "name": "🔍 자세히 조사하기",
                "description": "신중하게 접근하여 상황을 파악합니다",
                "risk": "낮음",
                "success_rate": 0.75,
                "requirements": []
            },
            {
                "type": InteractionType.FLEE,
                "name": "🚪 조용히 떠나기",
                "description": "아무 일 없었던 것처럼 그냥 지나갑니다",
                "risk": "없음",
                "success_rate": 0.95,
                "requirements": []
            }
        ]
    
    def _get_trait_based_interactions(self, party: List[Character]) -> List[Dict]:
        """특성 기반 특수 상호작용"""
        interactions = []
        party_traits = self._get_party_traits(party)
        
        # 도적 특성 기반
        if any("stealth" in trait.lower() or "sneak" in trait.lower() for trait in party_traits):
            interactions.append({
                "type": InteractionType.STEAL,
                "name": "🥷 은밀하게 접근",
                "description": "들키지 않고 가치있는 것을 훔쳐봅니다",
                "risk": "중간",
                "success_rate": 0.6,
                "requirements": ["도적 특성"]
            })
        
        # 바드/사교 특성 기반
        if any("charm" in trait.lower() or "social" in trait.lower() for trait in party_traits):
            interactions.append({
                "type": InteractionType.CHARM,
                "name": "💫 매혹하기",
                "description": "상대방을 매혹하여 우호적으로 만듭니다",
                "risk": "낮음",
                "success_rate": 0.7,
                "requirements": ["매혹 특성"]
            })
        
        # 전사/위협 특성 기반
        if any("intimidate" in trait.lower() or "rage" in trait.lower() for trait in party_traits):
            interactions.append({
                "type": InteractionType.INTIMIDATE,
                "name": "⚔️ 위협하기",
                "description": "강력한 위압감으로 상대를 제압합니다",
                "risk": "높음",
                "success_rate": 0.65,
                "requirements": ["위협 특성"]
            })
        
        return interactions
    
    def _get_class_based_interactions(self, party: List[Character]) -> List[Dict]:
        """직업 기반 특수 상호작용"""
        interactions = []
        party_classes = [member.character_class for member in party]
        
        # 성직자/신관 - 치유/축복
        if any(cls in ["성직자", "신관", "성기사"] for cls in party_classes):
            interactions.append({
                "type": InteractionType.HELP,
                "name": "✨ 신성한 힘으로 도움",
                "description": "신의 힘을 빌려 상황을 해결합니다",
                "risk": "낮음",
                "success_rate": 0.8,
                "requirements": ["신성 계열 직업"]
            })
        
        # 연금술사/기계공학자 - 분석
        if any(cls in ["연금술사", "기계공학자", "철학자"] for cls in party_classes):
            interactions.append({
                "type": InteractionType.USE_SKILL,
                "name": "🔬 전문 지식 활용",
                "description": "전문적 지식으로 상황을 분석합니다",
                "risk": "낮음",
                "success_rate": 0.85,
                "requirements": ["학자 계열 직업"]
            })
        
        # 드루이드 - 자연과의 소통
        if "드루이드" in party_classes:
            interactions.append({
                "type": InteractionType.USE_SKILL,
                "name": "🌿 자연과의 교감",
                "description": "자연의 힘을 빌려 해결책을 찾습니다",
                "risk": "낮음",
                "success_rate": 0.75,
                "requirements": ["드루이드"]
            })
        
        return interactions
    
    def _get_advanced_interactions(self) -> List[Dict]:
        """고급 상호작용 (높은 층에서만 사용 가능)"""
        return [
            {
                "type": InteractionType.TRICK,
                "name": "🎭 교묘한 속임수",
                "description": "복잡한 계략으로 상황을 유리하게 만듭니다",
                "risk": "높음",
                "success_rate": 0.5,
                "requirements": ["10층 이상"]
            }
        ]
    
    def _get_party_traits(self, party: List[Character]) -> List[str]:
        """파티의 모든 특성 수집"""
        all_traits = []
        for member in party:
            if hasattr(member, 'active_traits'):
                all_traits.extend([trait.name if hasattr(trait, 'name') else str(trait) 
                                 for trait in member.active_traits])
        return all_traits
    
    def execute_interaction(self, interaction: Dict, party: List[Character], floor: int) -> Dict[str, Any]:
        """상호작용 실행"""
        interaction_type = interaction["type"]
        success_rate = interaction["success_rate"]
        
        # 특성/직업 보너스 적용
        success_rate = self._apply_party_bonuses(success_rate, party, interaction_type)
        
        # 성공/실패 판정
        success = random.random() < success_rate
        
        if success:
            return self._handle_success(interaction_type, party, floor)
        else:
            return self._handle_failure(interaction_type, party, floor)
    
    def _apply_party_bonuses(self, base_rate: float, party: List[Character], 
                           interaction_type: InteractionType) -> float:
        """파티 특성/직업에 따른 성공률 보너스"""
        bonus = 0.0
        
        # 레벨 보너스
        avg_level = sum(member.level for member in party) / len(party)
        bonus += min(avg_level * 0.02, 0.2)  # 최대 20% 보너스
        
        # 특성 보너스 (더 구체적으로 구현 필요)
        for member in party:
            if hasattr(member, 'temp_treasure_bonus') and member.temp_treasure_bonus > 0:
                bonus += 0.1
            if hasattr(member, 'temp_exp_bonus') and member.temp_exp_bonus > 0:
                bonus += 0.05
        
        return min(base_rate + bonus, 0.95)  # 최대 95%로 제한
    
    def _handle_success(self, interaction_type: InteractionType, party: List[Character], 
                       floor: int) -> Dict[str, Any]:
        """성공 시 처리"""
        results = {
            "success": True,
            "message": "",
            "effects": {},
            "rewards": {}
        }
        
        if interaction_type == InteractionType.INVESTIGATE:
            results.update(self._investigate_success(party, floor))
        elif interaction_type == InteractionType.STEAL:
            results.update(self._steal_success(party, floor))
        elif interaction_type == InteractionType.CHARM:
            results.update(self._charm_success(party, floor))
        elif interaction_type == InteractionType.INTIMIDATE:
            results.update(self._intimidate_success(party, floor))
        elif interaction_type == InteractionType.HELP:
            results.update(self._help_success(party, floor))
        elif interaction_type == InteractionType.USE_SKILL:
            results.update(self._skill_success(party, floor))
        elif interaction_type == InteractionType.FLEE:
            results.update(self._flee_success(party, floor))
        
        return results
    
    def _handle_failure(self, interaction_type: InteractionType, party: List[Character], 
                       floor: int) -> Dict[str, Any]:
        """실패 시 처리"""
        results = {
            "success": False,
            "message": "",
            "effects": {},
            "penalties": {}
        }
        
        # 실패 시 공통 패널티
        if interaction_type in [InteractionType.STEAL, InteractionType.INTIMIDATE]:
            results["penalties"]["combat"] = True
            results["message"] = "상황이 악화되어 전투가 불가피해졌습니다!"
        elif interaction_type == InteractionType.INVESTIGATE:
            damage = random.randint(5 * floor, 15 * floor)
            results["penalties"]["damage"] = damage
            results["message"] = f"조사 중 함정에 걸려 {damage} 피해를 받았습니다!"
        else:
            results["message"] = "시도가 실패했지만 특별한 문제는 없었습니다."
        
        return results
    
    def _investigate_success(self, party: List[Character], floor: int) -> Dict[str, Any]:
        """조사 성공"""
        rewards = {}
        message_parts = ["🔍 조사 결과: "]
        
        # 골드 발견
        if random.random() < 0.6:
            gold = random.randint(20 * floor, 50 * floor)
            rewards["gold"] = gold
            message_parts.append(f"💰 {gold} 골드 발견")
        
        # 아이템 발견
        if random.random() < 0.4:
            rewards["item"] = f"층 {floor} 보물"
            message_parts.append("🎁 유용한 아이템 발견")
        
        # 정보 획득
        if random.random() < 0.5:
            rewards["info"] = True
            message_parts.append("📜 유용한 정보 획득")
        
        return {
            "message": " | ".join(message_parts),
            "rewards": rewards
        }
    
    def _steal_success(self, party: List[Character], floor: int) -> Dict[str, Any]:
        """도둑질 성공"""
        gold = random.randint(30 * floor, 70 * floor)
        return {
            "message": f"🥷 성공적으로 {gold} 골드를 훔쳤습니다!",
            "rewards": {"gold": gold}
        }
    
    def _charm_success(self, party: List[Character], floor: int) -> Dict[str, Any]:
        """매혹 성공"""
        return {
            "message": "💫 상대방이 우호적이 되어 선물을 주었습니다!",
            "rewards": {"blessing": True, "gold": random.randint(10 * floor, 30 * floor)}
        }
    
    def _intimidate_success(self, party: List[Character], floor: int) -> Dict[str, Any]:
        """위협 성공"""
        return {
            "message": "⚔️ 강력한 위압감으로 상대방이 물러났습니다!",
            "rewards": {"reputation": 1, "item": f"층 {floor} 전리품"}
        }
    
    def _help_success(self, party: List[Character], floor: int) -> Dict[str, Any]:
        """도움 성공"""
        return {
            "message": "✨ 신성한 힘으로 상황을 해결했습니다!",
            "effects": {"blessing": 3, "heal": 0.3},
            "rewards": {"karma": 1}
        }
    
    def _skill_success(self, party: List[Character], floor: int) -> Dict[str, Any]:
        """스킬 사용 성공"""
        return {
            "message": "🔬 전문 지식으로 최적의 해결책을 찾았습니다!",
            "rewards": {"exp": floor * 50, "info": True}
        }
    
    def _flee_success(self, party: List[Character], floor: int) -> Dict[str, Any]:
        """도주 성공"""
        return {
            "message": "🚪 조용히 그 장소를 떠났습니다.",
            "effects": {}
        }

class EnhancedEncounterManager:
    """강화된 조우 관리자"""
    
    def __init__(self):
        self.encounters = self._initialize_enhanced_encounters()
    
    def _initialize_enhanced_encounters(self) -> List[EnhancedEncounter]:
        """강화된 조우들 초기화"""
        encounters = []
        
        # 기존 조우들을 강화된 버전으로 업그레이드
        encounters.extend([
            EnhancedEncounter(
                EncounterType.TREASURE_CHEST,
                "📦 의심스러운 보물상자",
                "오래된 보물상자가 놓여있습니다. 함정이 있을 수도 있지만 가치있는 보물이 들어있을지도 모릅니다.",
                1, 30
            ),
            EnhancedEncounter(
                EncounterType.WANDERING_SPIRIT,
                "👻 떠도는 영혼",
                "슬픈 영혼이 길을 막고 있습니다. 도움을 구하는 것 같지만 위험할 수도 있습니다.",
                5, 30
            ),
            EnhancedEncounter(
                EncounterType.MERCHANT,
                "🛍️ 수상한 상인",
                "후드를 쓴 상인이 기다리고 있습니다. 좋은 물건을 가지고 있다고 하지만 과연 믿을 수 있을까요?",
                1, 30
            ),
            EnhancedEncounter(
                EncounterType.ABANDONED_CAMP,
                "🏕️ 버려진 야영지",
                "최근까지 사용된 듯한 야영지입니다. 유용한 물건이 남아있을 수도 있습니다.",
                3, 30
            ),
            EnhancedEncounter(
                EncounterType.MYSTERIOUS_STATUE,
                "🗿 고대의 석상",
                "신비한 기운이 감도는 고대 석상입니다. 건드리면 축복을 받을 수도, 저주를 받을 수도 있습니다.",
                7, 30
            )
        ])
        
        return encounters
    
    def trigger_enhanced_encounter(self, party: List[Character], floor: int) -> Optional[Dict[str, Any]]:
        """강화된 조우 시스템 실행"""
        # 현재 층에서 가능한 조우들 필터링
        available_encounters = [
            encounter for encounter in self.encounters
            if encounter.min_floor <= floor <= encounter.max_floor
        ]
        
        if not available_encounters:
            return None
        
        # 랜덤하게 조우 선택
        selected_encounter = random.choice(available_encounters)
        return self._run_encounter_interface(selected_encounter, party, floor)
    
    def _run_encounter_interface(self, encounter: EnhancedEncounter, party: List[Character], 
                               floor: int) -> Dict[str, Any]:
        """커서 기반 조우 인터페이스 실행"""
        try:
            from .cursor_menu_system import CursorMenu
            
            # 상황 설명
            print(f"\n{bright_cyan('='*60)}")
            print(f"{bright_yellow(encounter.title)}")
            print(f"{bright_cyan('='*60)}")
            print(f"{white(encounter.description)}")
            print()
            
            # 가능한 상호작용 목록 생성
            interactions = encounter.get_available_interactions(party, floor)
            
            # 메뉴 옵션 생성
            options = []
            descriptions = []
            
            for interaction in interactions:
                risk_colors = {
                    "없음": green("안전"),
                    "낮음": yellow("낮은 위험"),
                    "중간": bright_yellow("중간 위험"),
                    "높음": red("높은 위험")
                }
                
                risk_text = risk_colors.get(interaction["risk"], interaction["risk"])
                success_rate = int(interaction["success_rate"] * 100)
                
                option_text = f"{interaction['name']} [{risk_text}] ({success_rate}%)"
                options.append(option_text)
                
                desc_parts = [interaction["description"]]
                if interaction["requirements"]:
                    req_text = ", ".join(interaction["requirements"])
                    desc_parts.append(f"{cyan('필요 조건:')} {req_text}")
                
                descriptions.append("\n".join(desc_parts))
            
            # 커서 메뉴 실행
            menu = CursorMenu(
                f"🎯 {encounter.title} - 어떻게 하시겠습니까?",
                options,
                descriptions,
                cancellable=False
            )
            
            choice = menu.run()
            if choice is not None and 0 <= choice < len(interactions):
                selected_interaction = interactions[choice]
                result = encounter.execute_interaction(selected_interaction, party, floor)
                
                # 결과 표시
                print(f"\n{bright_cyan('='*40)}")
                if result["success"]:
                    print(f"{bright_green('✅ 성공!')}")
                else:
                    print(f"{bright_red('❌ 실패!')}")
                print(f"{white(result['message'])}")
                print(f"{bright_cyan('='*40)}")
                
                return result
            
            return {"success": False, "message": "조우를 피했습니다."}
            
        except ImportError:
            # 폴백: 기본 시스템 사용
            return {"success": True, "message": "기본 조우 시스템으로 처리되었습니다."}

# 전역 인스턴스
enhanced_encounter_manager = EnhancedEncounterManager()

def get_enhanced_encounter_manager() -> EnhancedEncounterManager:
    """강화된 조우 관리자 반환"""
    return enhanced_encounter_manager
