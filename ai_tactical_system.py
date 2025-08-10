#!/usr/bin/env python3
"""
Dawn of Stellar - 고급 AI 전술 시스템
AI 캐릭터들의 전술적 사고와 전투 전략 구현
"""

import random
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TacticalRole(Enum):
    """전술적 역할"""
    TANK = "탱커"           # 최전선 방어
    DPS = "딜러"            # 공격 담당
    HEALER = "힐러"         # 치유 담당
    SUPPORT = "서포터"      # 지원 담당
    CONTROLLER = "컨트롤러"  # 전장 제어
    SCOUT = "정찰병"        # 정보 수집

class TacticalFormation(Enum):
    """전술 진형"""
    DEFENSIVE = "방어진형"
    OFFENSIVE = "공격진형"
    BALANCED = "균형진형"
    AMBUSH = "기습진형"
    RETREAT = "후퇴진형"
    ENCIRCLEMENT = "포위진형"

@dataclass
class TacticalAction:
    """전술 행동"""
    action_id: str
    name: str
    description: str
    required_role: TacticalRole
    priority: int                    # 우선순위 (1-10)
    conditions: Dict[str, Any]       # 실행 조건
    effects: Dict[str, Any]          # 효과
    cooldown: float                  # 재사용 대기시간

@dataclass
class BattleSituation:
    """전투 상황 분석"""
    ally_count: int
    enemy_count: int
    ally_hp_ratio: float             # 아군 평균 HP 비율
    enemy_hp_ratio: float            # 적군 평균 HP 비율
    ally_mp_ratio: float             # 아군 평균 MP 비율
    battlefield_type: str            # 전장 타입
    turn_count: int                  # 현재 턴 수
    threat_level: str                # 위험도 (LOW, MEDIUM, HIGH, CRITICAL)

class AdvancedAITacticalSystem:
    """고급 AI 전술 시스템"""
    
    def __init__(self):
        self.tactical_actions: Dict[str, TacticalAction] = {}
        self.job_roles: Dict[str, TacticalRole] = {}
        self.formation_preferences: Dict[str, TacticalFormation] = {}
        self.decision_history: List[Dict[str, Any]] = []
        self.current_formation: Optional[TacticalFormation] = None
        
        self._init_job_roles()
        self._init_tactical_actions()
        print("🧠 고급 AI 전술 시스템 초기화 완료")
    
    def _init_job_roles(self):
        """직업별 전술적 역할 초기화 (완성된 27개 직업)"""
        self.job_roles = {
            # 전투 직업군 (8개)
            "전사": TacticalRole.TANK,
            "아크메이지": TacticalRole.DPS,
            "궁수": TacticalRole.DPS,
            "도적": TacticalRole.DPS,
            "성기사": TacticalRole.TANK,
            "암흑기사": TacticalRole.TANK,
            "몽크": TacticalRole.DPS,
            "바드": TacticalRole.SUPPORT,
            
            # 마법 직업군 (10개)
            "네크로맨서": TacticalRole.DPS,
            "용기사": TacticalRole.DPS,
            "검성": TacticalRole.DPS,
            "정령술사": TacticalRole.CONTROLLER,
            "시간술사": TacticalRole.CONTROLLER,
            "연금술사": TacticalRole.SUPPORT,
            "차원술사": TacticalRole.CONTROLLER,
            "마검사": TacticalRole.DPS,
            "기계공학자": TacticalRole.SUPPORT,
            "무당": TacticalRole.HEALER,
            
            # 특수 직업군 (9개)
            "암살자": TacticalRole.DPS,
            "해적": TacticalRole.DPS,
            "사무라이": TacticalRole.DPS,
            "드루이드": TacticalRole.HEALER,
            "철학자": TacticalRole.SUPPORT,
            "검투사": TacticalRole.DPS,
            "기사": TacticalRole.TANK,
            "신관": TacticalRole.HEALER,
            "광전사": TacticalRole.DPS
        }
        print(f"✅ 27개 직업 역할 {len(self.job_roles)}개 초기화 완료")
    
    def _init_tactical_actions(self):
        """기본 전술 행동들 초기화"""
        
        # 탱커 행동들
        self.tactical_actions["taunt_enemies"] = TacticalAction(
            action_id="taunt_enemies",
            name="적 도발",
            description="적들의 어그로를 끌어서 아군을 보호합니다",
            required_role=TacticalRole.TANK,
            priority=8,
            conditions={"ally_in_danger": True, "hp_above": 0.3},
            effects={"aggro_increase": 2.0, "damage_reduction": 0.1},
            cooldown=3.0
        )
        
        self.tactical_actions["defensive_stance"] = TacticalAction(
            action_id="defensive_stance",
            name="방어 자세",
            description="방어력을 높여 피해를 줄입니다",
            required_role=TacticalRole.TANK,
            priority=6,
            conditions={"threat_level": "HIGH"},
            effects={"defense_boost": 1.5, "movement_penalty": 0.5},
            cooldown=0.0
        )
        
        # 힐러 행동들
        self.tactical_actions["emergency_heal"] = TacticalAction(
            action_id="emergency_heal",
            name="응급 치료",
            description="위험한 상태의 아군을 즉시 치료합니다",
            required_role=TacticalRole.HEALER,
            priority=10,
            conditions={"ally_hp_below": 0.2, "mp_above": 20},
            effects={"heal_amount": 0.5, "mp_cost": 20},
            cooldown=1.0
        )
        
        self.tactical_actions["group_heal"] = TacticalAction(
            action_id="group_heal",
            name="집단 치료",
            description="여러 아군을 동시에 치료합니다",
            required_role=TacticalRole.HEALER,
            priority=7,
            conditions={"multiple_injured": True, "mp_above": 30},
            effects={"heal_amount": 0.3, "mp_cost": 30, "targets": "multiple"},
            cooldown=2.0
        )
        
        # DPS 행동들
        self.tactical_actions["focus_fire"] = TacticalAction(
            action_id="focus_fire",
            name="집중 공격",
            description="약한 적을 집중적으로 공격하여 빠르게 제거합니다",
            required_role=TacticalRole.DPS,
            priority=8,
            conditions={"enemy_low_hp": True},
            effects={"damage_boost": 1.3, "critical_chance": 0.2},
            cooldown=1.5
        )
        
        # 컨트롤러 행동들
        self.tactical_actions["crowd_control"] = TacticalAction(
            action_id="crowd_control",
            name="군중 제어",
            description="여러 적을 무력화시켜 전장을 통제합니다",
            required_role=TacticalRole.CONTROLLER,
            priority=7,
            conditions={"multiple_enemies": True, "mp_above": 25},
            effects={"stun_duration": 2.0, "mp_cost": 25, "targets": "multiple"},
            cooldown=3.0
        )
        
        print(f"✅ 전술 행동 {len(self.tactical_actions)}개 초기화 완료")
    
    def analyze_battle_situation(self, battle_data: Dict[str, Any]) -> BattleSituation:
        """전투 상황 분석"""
        # 임시 더미 데이터 - 실제로는 게임 상태를 분석
        situation = BattleSituation(
            ally_count=battle_data.get("ally_count", 4),
            enemy_count=battle_data.get("enemy_count", 3),
            ally_hp_ratio=battle_data.get("ally_hp_ratio", 0.7),
            enemy_hp_ratio=battle_data.get("enemy_hp_ratio", 0.8),
            ally_mp_ratio=battle_data.get("ally_mp_ratio", 0.6),
            battlefield_type=battle_data.get("battlefield_type", "normal"),
            turn_count=battle_data.get("turn_count", 5),
            threat_level=self._assess_threat_level(battle_data)
        )
        
        return situation
    
    def _assess_threat_level(self, battle_data: Dict[str, Any]) -> str:
        """위험도 평가"""
        ally_hp = battle_data.get("ally_hp_ratio", 1.0)
        enemy_count = battle_data.get("enemy_count", 1)
        ally_count = battle_data.get("ally_count", 4)
        
        if ally_hp < 0.3:
            return "CRITICAL"
        elif ally_hp < 0.5 or enemy_count > ally_count:
            return "HIGH"
        elif ally_hp < 0.8:
            return "MEDIUM"
        else:
            return "LOW"
    
    def recommend_formation(self, situation: BattleSituation) -> TacticalFormation:
        """상황에 맞는 진형 추천"""
        if situation.threat_level == "CRITICAL":
            return TacticalFormation.DEFENSIVE
        elif situation.enemy_count > situation.ally_count:
            return TacticalFormation.DEFENSIVE
        elif situation.ally_hp_ratio > 0.8 and situation.ally_mp_ratio > 0.7:
            return TacticalFormation.OFFENSIVE
        elif situation.enemy_hp_ratio < 0.3:
            return TacticalFormation.OFFENSIVE
        else:
            return TacticalFormation.BALANCED
    
    def get_best_action_for_ai(self, ai_job: str, situation: BattleSituation, 
                              ai_status: Dict[str, Any]) -> Optional[TacticalAction]:
        """AI의 직업과 상황에 맞는 최적 행동 추천"""
        if ai_job not in self.job_roles:
            return None
        
        ai_role = self.job_roles[ai_job]
        
        # 해당 역할에 맞는 행동들 필터링
        suitable_actions = [
            action for action in self.tactical_actions.values()
            if action.required_role == ai_role
        ]
        
        # 조건을 만족하는 행동들 필터링
        valid_actions = []
        for action in suitable_actions:
            if self._check_action_conditions(action, situation, ai_status):
                valid_actions.append(action)
        
        # 우선순위에 따라 정렬하여 최고 우선순위 행동 반환
        if valid_actions:
            valid_actions.sort(key=lambda x: x.priority, reverse=True)
            return valid_actions[0]
        
        return None
    
    def _check_action_conditions(self, action: TacticalAction, 
                                situation: BattleSituation, 
                                ai_status: Dict[str, Any]) -> bool:
        """행동 실행 조건 체크"""
        conditions = action.conditions
        
        # 위험도 조건
        if "threat_level" in conditions:
            if conditions["threat_level"] != situation.threat_level:
                return False
        
        # HP 조건
        if "hp_above" in conditions:
            current_hp_ratio = ai_status.get("hp_ratio", 1.0)
            if current_hp_ratio < conditions["hp_above"]:
                return False
        
        if "ally_hp_below" in conditions:
            if situation.ally_hp_ratio >= conditions["ally_hp_below"]:
                return False
        
        # MP 조건
        if "mp_above" in conditions:
            current_mp = ai_status.get("current_mp", 100)
            if current_mp < conditions["mp_above"]:
                return False
        
        # 다중 적 조건
        if "multiple_enemies" in conditions:
            if situation.enemy_count < 2:
                return False
        
        # 다중 부상자 조건
        if "multiple_injured" in conditions:
            if situation.ally_hp_ratio > 0.8:  # 대부분 건강하면 집단 치료 불필요
                return False
        
        return True
    
    def make_tactical_decision(self, ai_name: str, ai_job: str, 
                             battle_data: Dict[str, Any], 
                             ai_status: Dict[str, Any]) -> Dict[str, Any]:
        """AI의 전술적 의사결정"""
        
        # 1. 상황 분석
        situation = self.analyze_battle_situation(battle_data)
        
        # 2. 진형 추천
        recommended_formation = self.recommend_formation(situation)
        
        # 3. 최적 행동 선택
        best_action = self.get_best_action_for_ai(ai_job, situation, ai_status)
        
        # 4. 의사결정 결과
        decision = {
            "ai_name": ai_name,
            "ai_job": ai_job,
            "timestamp": time.time(),
            "situation_analysis": {
                "threat_level": situation.threat_level,
                "ally_advantage": situation.ally_count >= situation.enemy_count,
                "resource_status": "good" if situation.ally_mp_ratio > 0.6 else "low"
            },
            "recommended_formation": recommended_formation.value,
            "selected_action": {
                "action_id": best_action.action_id if best_action else None,
                "action_name": best_action.name if best_action else "기본 공격",
                "priority": best_action.priority if best_action else 1,
                "reasoning": self._generate_reasoning(situation, best_action)
            }
        }
        
        # 5. 의사결정 기록
        self.decision_history.append(decision)
        
        print(f"🧠 {ai_name}({ai_job}) 전술 결정: {decision['selected_action']['action_name']}")
        
        return decision
    
    def _generate_reasoning(self, situation: BattleSituation, 
                          action: Optional[TacticalAction]) -> str:
        """의사결정 이유 생성"""
        if not action:
            return "상황에 맞는 특별한 행동이 없어 기본 행동을 선택합니다."
        
        reasoning_parts = []
        
        # 위험도 기반 이유
        if situation.threat_level == "CRITICAL":
            reasoning_parts.append("위험한 상황")
        elif situation.threat_level == "HIGH":
            reasoning_parts.append("높은 위험도")
        
        # HP 상태 기반 이유
        if situation.ally_hp_ratio < 0.5:
            reasoning_parts.append("아군 생존 우선")
        
        # 행동 타입 기반 이유
        if action.required_role == TacticalRole.HEALER:
            reasoning_parts.append("치료 필요")
        elif action.required_role == TacticalRole.TANK:
            reasoning_parts.append("방어 필요")
        elif action.required_role == TacticalRole.DPS:
            reasoning_parts.append("공격 기회")
        
        if reasoning_parts:
            return f"{', '.join(reasoning_parts)}로 인해 {action.name}를 선택"
        else:
            return f"최적의 전술로 {action.name}를 선택"
    
    def display_tactical_menu(self):
        """전술 시스템 메뉴 (간단한 텍스트 버전)"""
        print("\n🧠 고급 AI 전술 시스템")
        print("=" * 50)
        print("1. 전술 행동 보기")
        print("2. 직업별 역할 확인")
        print("3. 전술 시뮬레이션")
        print("4. 의사결정 히스토리")
        print("0. 돌아가기")
        
        try:
            choice = input("\n선택하세요: ").strip()
            
            if choice == "1":
                self._show_tactical_actions()
            elif choice == "2":
                self._show_job_roles()
            elif choice == "3":
                self._run_tactical_simulation()
            elif choice == "4":
                self._show_decision_history()
            elif choice == "0":
                return
            else:
                print("❌ 잘못된 선택입니다.")
                
        except Exception as e:
            print(f"❌ 메뉴 처리 오류: {e}")
        
        input("\nEnter를 눌러 계속...")
    
    def _show_tactical_actions(self):
        """전술 행동들 표시"""
        print("\n⚔️ 전술 행동 목록")
        print("-" * 40)
        
        # 역할별로 그룹화
        actions_by_role = {}
        for action in self.tactical_actions.values():
            role = action.required_role.value
            if role not in actions_by_role:
                actions_by_role[role] = []
            actions_by_role[role].append(action)
        
        for role, actions in actions_by_role.items():
            print(f"\n📋 {role} 전용 행동:")
            for action in actions:
                print(f"  🎯 {action.name} (우선순위: {action.priority})")
                print(f"     {action.description}")
    
    def _show_job_roles(self):
        """직업별 역할 표시"""
        print("\n👥 직업별 전술 역할")
        print("-" * 40)
        
        role_groups = {}
        for job, role in self.job_roles.items():
            role_name = role.value
            if role_name not in role_groups:
                role_groups[role_name] = []
            role_groups[role_name].append(job)
        
        for role, jobs in role_groups.items():
            print(f"\n🛡️ {role}: {', '.join(jobs)}")
    
    def _run_tactical_simulation(self):
        """전술 시뮬레이션 실행"""
        print("\n🎮 전술 시뮬레이션")
        print("-" * 30)
        
        # 가상의 전투 상황 생성
        test_battle_data = {
            "ally_count": 4,
            "enemy_count": random.randint(2, 6),
            "ally_hp_ratio": random.uniform(0.3, 0.9),
            "enemy_hp_ratio": random.uniform(0.5, 1.0),
            "ally_mp_ratio": random.uniform(0.4, 0.8),
            "battlefield_type": "normal",
            "turn_count": random.randint(1, 10)
        }
        
        test_ai_status = {
            "hp_ratio": random.uniform(0.4, 0.9),
            "current_mp": random.randint(20, 80)
        }
        
        print("🎯 시뮬레이션 상황:")
        print(f"   아군: {test_battle_data['ally_count']}명, 적군: {test_battle_data['enemy_count']}명")
        print(f"   아군 HP: {test_battle_data['ally_hp_ratio']:.1%}")
        print(f"   아군 MP: {test_battle_data['ally_mp_ratio']:.1%}")
        
        # 각 직업별로 의사결정 테스트
        print("\n🤖 AI 의사결정 결과:")
        for job in ["전사", "신관", "궁수", "아크메이지"]:
            decision = self.make_tactical_decision(
                f"AI_{job}", job, test_battle_data, test_ai_status
            )
            action_name = decision['selected_action']['action_name']
            reasoning = decision['selected_action']['reasoning']
            print(f"   {job}: {action_name}")
            print(f"      이유: {reasoning}")
    
    def _show_decision_history(self):
        """의사결정 히스토리 표시"""
        print("\n📊 의사결정 히스토리")
        print("-" * 40)
        
        if not self.decision_history:
            print("📝 의사결정 기록이 없습니다.")
            return
        
        for record in self.decision_history[-5:]:  # 최근 5개만
            timestamp = time.strftime("%H:%M:%S", time.localtime(record['timestamp']))
            ai_info = f"{record['ai_name']}({record['ai_job']})"
            action = record['selected_action']['action_name']
            print(f"{timestamp} {ai_info}: {action}")

# 전역 인스턴스
tactical_system = AdvancedAITacticalSystem()

def test_tactical_system():
    """전술 시스템 테스트"""
    print("🧪 전술 시스템 테스트 시작")
    
    # 테스트 전투 데이터
    test_data = {
        "ally_count": 4,
        "enemy_count": 3,
        "ally_hp_ratio": 0.6,
        "enemy_hp_ratio": 0.8,
        "ally_mp_ratio": 0.7,
        "turn_count": 3
    }
    
    test_status = {"hp_ratio": 0.8, "current_mp": 50}
    
    # 의사결정 테스트
    decision = tactical_system.make_tactical_decision(
        "테스트AI", "전사", test_data, test_status
    )
    
    print(f"결정된 행동: {decision['selected_action']['action_name']}")
    print("✅ 전술 시스템 테스트 완료")

if __name__ == "__main__":
    test_tactical_system()
