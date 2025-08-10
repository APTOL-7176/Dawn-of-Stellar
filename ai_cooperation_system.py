#!/usr/bin/env python3
"""
Dawn of Stellar - AI 협력 메커니즘 시스템
AI 캐릭터들 간의 협력 행동과 전술적 협업 구현
"""

import json
import random
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class CooperationAction:
    """협력 행동 데이터"""
    action_id: str
    action_name: str
    description: str
    required_participants: int           # 필요한 참가자 수
    required_jobs: List[str]            # 필요한 직업들
    cooperation_type: str               # 협력 타입
    success_chance: float               # 성공 확률
    benefits: Dict[str, Any]            # 협력 성공 시 혜택
    cost: Dict[str, Any]                # 협력 비용

class CooperationType(Enum):
    """협력 타입"""
    COMBAT_COMBO = "전투_연계"          # 전투 연계 공격
    HEALING_SUPPORT = "치유_지원"       # 치유 지원
    BUFF_CHAIN = "버프_연쇄"           # 버프 연쇄 효과
    TACTICAL_FORMATION = "전술_진형"    # 전술적 진형
    RESOURCE_SHARING = "자원_공유"      # 자원 공유
    KNOWLEDGE_EXCHANGE = "지식_교환"    # 지식 및 정보 교환
    PROTECTION = "보호_행동"           # 보호 행동
    EXPLORATION = "탐험_협력"          # 탐험 협력

class AICooperationSystem:
    """AI 협력 메커니즘 시스템"""
    
    def __init__(self):
        self.cooperation_actions: Dict[str, CooperationAction] = {}
        self.active_cooperations: List[Dict[str, Any]] = []
        self.cooperation_history: List[Dict[str, Any]] = []
        self.job_synergies: Dict[Tuple[str, str], float] = {}
        
        self._init_basic_cooperation_actions()
        self._init_job_synergies()
        print("🤝 AI 협력 메커니즘 시스템 초기화 완료")
    
    def _init_basic_cooperation_actions(self):
        """기본 협력 행동들 초기화"""
        
        # 1. 전투 연계 행동들
        self.cooperation_actions["combo_attack"] = CooperationAction(
            action_id="combo_attack",
            action_name="연계 공격",
            description="두 명 이상이 협력하여 강력한 연계 공격을 실행합니다",
            required_participants=2,
            required_jobs=["전사", "궁수", "도적"],  # 예시 직업들
            cooperation_type=CooperationType.COMBAT_COMBO.value,
            success_chance=0.8,
            benefits={"damage_multiplier": 1.5, "critical_chance": 0.3},
            cost={"mp_cost": 15, "stamina_cost": 20}
        )
        
        # 2. 치유 지원
        self.cooperation_actions["healing_circle"] = CooperationAction(
            action_id="healing_circle",
            action_name="치유의 원",
            description="치유 능력자들이 협력하여 강력한 회복 효과를 만듭니다",
            required_participants=2,
            required_jobs=["신관", "드루이드"],
            cooperation_type=CooperationType.HEALING_SUPPORT.value,
            success_chance=0.9,
            benefits={"healing_multiplier": 2.0, "status_remove": True},
            cost={"mp_cost": 25}
        )
        
        # 3. 마법 연쇄
        self.cooperation_actions["magic_chain"] = CooperationAction(
            action_id="magic_chain",
            action_name="마법 연쇄",
            description="마법사들이 협력하여 강화된 마법을 시전합니다",
            required_participants=2,
            required_jobs=["아크메이지", "정령술사", "차원술사"],
            cooperation_type=CooperationType.BUFF_CHAIN.value,
            success_chance=0.75,
            benefits={"spell_power": 1.8, "area_effect": True},
            cost={"mp_cost": 30}
        )
        
        print("✅ 기본 협력 행동 3개 초기화 완료")
    
    def _init_job_synergies(self):
        """직업 간 시너지 초기화 (기본 6개 직업으로 시작)"""
        
        # 전투 시너지
        self.job_synergies[("전사", "성기사")] = 1.3  # 전선 유지 시너지
        self.job_synergies[("궁수", "도적")] = 1.2    # 원거리-근거리 연계
        self.job_synergies[("아크메이지", "정령술사")] = 1.4  # 마법 증폭
        
        # 지원 시너지  
        self.job_synergies[("신관", "드루이드")] = 1.5  # 치유 증폭
        self.job_synergies[("전사", "신관")] = 1.2      # 탱커-힐러
        self.job_synergies[("궁수", "아크메이지")] = 1.1  # 원거리 조합
        
        print(f"✅ 직업 시너지 {len(self.job_synergies)}개 초기화 완료")
    
    def can_cooperate(self, participants: List[str], action_id: str) -> Tuple[bool, str]:
        """협력 가능 여부 체크"""
        if action_id not in self.cooperation_actions:
            return False, "존재하지 않는 협력 행동입니다"
        
        action = self.cooperation_actions[action_id]
        
        # 참가자 수 체크
        if len(participants) < action.required_participants:
            return False, f"최소 {action.required_participants}명이 필요합니다"
        
        # 직업 요구사항 체크 (임시로 스킵 - 나중에 실제 직업 데이터 연동)
        # TODO: 실제 캐릭터 직업 정보와 연동
        
        return True, "협력 가능"
    
    def initiate_cooperation(self, participants: List[str], action_id: str, 
                           context: str = "") -> Dict[str, Any]:
        """협력 행동 시작"""
        can_coop, reason = self.can_cooperate(participants, action_id)
        if not can_coop:
            return {
                "success": False,
                "reason": reason,
                "timestamp": time.time()
            }
        
        action = self.cooperation_actions[action_id]
        
        # 성공 여부 판정
        success = random.random() < action.success_chance
        
        cooperation_result = {
            "cooperation_id": f"coop_{int(time.time())}_{random.randint(1000, 9999)}",
            "action_id": action_id,
            "action_name": action.action_name,
            "participants": participants,
            "success": success,
            "timestamp": time.time(),
            "context": context,
            "benefits_applied": action.benefits if success else {},
            "cost_applied": action.cost if success else {},
            "description": action.description
        }
        
        # 기록에 추가
        self.cooperation_history.append(cooperation_result)
        
        # 성공 시 임시로 활성 협력에 추가
        if success:
            self.active_cooperations.append(cooperation_result)
        
        print(f"🤝 협력 행동 {'성공' if success else '실패'}: {action.action_name}")
        print(f"   참가자: {', '.join(participants)}")
        
        return cooperation_result
    
    def get_available_cooperations(self, participants: List[str]) -> List[CooperationAction]:
        """현재 참가자들이 사용 가능한 협력 행동 목록"""
        available = []
        
        for action in self.cooperation_actions.values():
            can_coop, _ = self.can_cooperate(participants, action.action_id)
            if can_coop:
                available.append(action)
        
        return available
    
    def get_job_synergy(self, job1: str, job2: str) -> float:
        """두 직업 간 시너지 계수 반환"""
        key1 = (job1, job2)
        key2 = (job2, job1)
        
        if key1 in self.job_synergies:
            return self.job_synergies[key1]
        elif key2 in self.job_synergies:
            return self.job_synergies[key2]
        else:
            return 1.0  # 기본 시너지 없음
    
    def calculate_group_synergy(self, jobs: List[str]) -> float:
        """그룹 전체의 시너지 계수 계산"""
        if len(jobs) < 2:
            return 1.0
        
        total_synergy = 0.0
        pair_count = 0
        
        for i in range(len(jobs)):
            for j in range(i + 1, len(jobs)):
                synergy = self.get_job_synergy(jobs[i], jobs[j])
                total_synergy += synergy
                pair_count += 1
        
        if pair_count > 0:
            return total_synergy / pair_count
        else:
            return 1.0
    
    def display_cooperation_menu(self):
        """협력 관리 메뉴 (간단한 텍스트 버전)"""
        print("\n🤝 AI 협력 메커니즘")
        print("=" * 50)
        print("1. 사용 가능한 협력 행동 보기")
        print("2. 협력 테스트 실행")
        print("3. 협력 히스토리 보기")
        print("4. 직업 시너지 확인")
        print("0. 돌아가기")
        
        try:
            choice = input("\n선택하세요: ").strip()
            
            if choice == "1":
                self._show_available_actions()
            elif choice == "2":
                self._test_cooperation()
            elif choice == "3":
                self._show_cooperation_history()
            elif choice == "4":
                self._show_job_synergies()
            elif choice == "0":
                return
            else:
                print("❌ 잘못된 선택입니다.")
                
        except Exception as e:
            print(f"❌ 메뉴 처리 오류: {e}")
        
        input("\nEnter를 눌러 계속...")
    
    def _show_available_actions(self):
        """사용 가능한 협력 행동 표시"""
        print("\n📋 사용 가능한 협력 행동")
        print("-" * 40)
        
        for action in self.cooperation_actions.values():
            print(f"\n🎯 {action.action_name}")
            print(f"   설명: {action.description}")
            print(f"   필요 인원: {action.required_participants}명")
            print(f"   필요 직업: {', '.join(action.required_jobs)}")
            print(f"   성공률: {action.success_chance*100:.0f}%")
            print(f"   타입: {action.cooperation_type}")
    
    def _test_cooperation(self):
        """협력 테스트 실행"""
        print("\n🧪 협력 테스트")
        print("-" * 30)
        
        # 테스트용 참가자들
        test_participants = ["AI_알파", "AI_베타"]
        
        print("테스트 참가자:", ", ".join(test_participants))
        
        # 사용 가능한 행동들 표시
        available = self.get_available_cooperations(test_participants)
        
        if not available:
            print("❌ 사용 가능한 협력 행동이 없습니다.")
            return
        
        print("\n사용 가능한 협력 행동:")
        for i, action in enumerate(available, 1):
            print(f"{i}. {action.action_name}")
        
        try:
            choice = int(input("선택하세요: ")) - 1
            if 0 <= choice < len(available):
                selected_action = available[choice]
                result = self.initiate_cooperation(
                    test_participants, 
                    selected_action.action_id, 
                    "테스트 실행"
                )
                print(f"\n결과: {'성공' if result['success'] else '실패'}")
                if result['success']:
                    print(f"혜택: {result['benefits_applied']}")
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _show_cooperation_history(self):
        """협력 히스토리 표시"""
        print("\n📜 협력 히스토리")
        print("-" * 40)
        
        if not self.cooperation_history:
            print("📝 협력 기록이 없습니다.")
            return
        
        for record in self.cooperation_history[-5:]:  # 최근 5개만
            timestamp = time.strftime("%H:%M:%S", time.localtime(record['timestamp']))
            status = "✅" if record['success'] else "❌"
            print(f"{timestamp} {status} {record['action_name']}")
            print(f"   참가자: {', '.join(record['participants'])}")
            if record['context']:
                print(f"   상황: {record['context']}")
            print()
    
    def _show_job_synergies(self):
        """직업 시너지 표시"""
        print("\n⚔️ 직업 간 시너지")
        print("-" * 40)
        
        for (job1, job2), synergy in self.job_synergies.items():
            status = "🔥 강력" if synergy >= 1.4 else "💪 좋음" if synergy >= 1.2 else "👍 보통"
            print(f"{job1} + {job2}: {synergy:.1f}x {status}")
    
    def test_cooperation_actions(self):
        """협력 행동 테스트"""
        print("\n🧪 협력 행동 테스트")
        print("=" * 50)
        
        for action_id, action in self.cooperation_actions.items():
            print(f"📋 {action.action_name} ({action_id})")
            print(f"   설명: {action.description}")
            print(f"   필요 인원: {action.required_participants}명")
            print(f"   필요 직업: {', '.join(action.required_jobs)}")
            print(f"   성공률: {action.success_chance * 100:.0f}%")
            print(f"   혜택: {action.benefits}")
            print(f"   비용: {action.cost}")
            print()
    
    def test_synergy_calculations(self):
        """시너지 계산 테스트"""
        print("\n⚡ 시너지 계산 테스트")
        print("=" * 50)
        
        test_parties = [
            ["전사", "성기사"],
            ["궁수", "도적"],
            ["아크메이지", "정령술사"],
            ["신관", "드루이드"],
            ["전사", "아크메이지", "신관"]  # 3인 파티
        ]
        
        for party in test_parties:
            synergy = self.calculate_party_synergy(party)
            print(f"파티 {' + '.join(party)}: {synergy:.2f}x 시너지")
    
    def show_cooperation_menu(self):
        """협력 메뉴 표시"""
        while True:
            print("\n🤝 협력 시스템 메뉴")
            print("=" * 50)
            print("1. 협력 행동 목록")
            print("2. 직업 시너지 보기")
            print("3. 협력 행동 테스트")
            print("4. 시너지 계산 테스트")
            print("5. 협력 히스토리")
            print("0. 돌아가기")
            
            choice = input("\n선택하세요: ").strip()
            
            if choice == "1":
                self.test_cooperation_actions()
            elif choice == "2":
                self._show_job_synergies()
            elif choice == "3":
                self.test_cooperation_actions()
            elif choice == "4":
                self.test_synergy_calculations()
            elif choice == "5":
                self._show_recent_history()
            elif choice == "0":
                break
            else:
                print("❌ 잘못된 선택입니다.")
            
            input("\n계속하려면 Enter를 누르세요...")

# 전역 인스턴스
cooperation_system = AICooperationSystem()

def test_cooperation_system():
    """협력 시스템 테스트"""
    print("🧪 협력 시스템 테스트 시작")
    
    # 기본 테스트
    participants = ["테스트A", "테스트B"]
    result = cooperation_system.initiate_cooperation(
        participants, "combo_attack", "테스트 상황"
    )
    
    print(f"테스트 결과: {result['success']}")
    print("✅ 협력 시스템 테스트 완료")

if __name__ == "__main__":
    test_cooperation_system()
