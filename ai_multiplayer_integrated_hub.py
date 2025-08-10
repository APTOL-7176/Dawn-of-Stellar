#!/usr/bin/env python3
"""
Dawn of Stellar - AI 멀티플레이어 통합 시스템
모든 AI 시스템들을 하나로 통합하는 메인 허브
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional

# 모든 AI 시스템들 import
try:
    from complete_27_job_system import job_system, Complete27JobSystem
    from ai_27job_character_creator import character_creator, AI27JobCharacterCreator
    from ai_interaction_system import interaction_system, AIInteractionSystem
    from ai_cooperation_system import cooperation_system, AICooperationSystem
    from ai_tactical_system import tactical_system, AdvancedAITacticalSystem
    from ai_training_system import training_system, AITrainingSystem
    from exaone_ai_engine import ExaoneAIEngine
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 일부 모듈을 찾을 수 없습니다: {e}")
    SYSTEMS_AVAILABLE = False

# 간단한 캐릭터 관리 클래스
class SimpleCharacterManager:
    def __init__(self):
        self.characters = {}
        self.data_dir = "ai_character_data/party_saves"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_all_characters(self):
        return self.characters
    
    def add_character(self, name, data):
        self.characters[name] = data
    
    def save_to_file(self, filename="characters.json"):
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.characters, f, ensure_ascii=False, indent=2)

class AIMultiplayerHub:
    """AI 멀티플레이어 통합 허브"""
    
    def __init__(self):
        if not SYSTEMS_AVAILABLE:
            print("❌ 필수 시스템들을 로드할 수 없습니다.")
            return
        
        # BGM 시스템 초기화
        try:
            from game.audio_system import AudioManager, BGMType
            self.audio_system = AudioManager(debug_mode=False)  # 디버그 모드 비활성화
            self.audio_system.play_bgm("aerith_theme")  # 에어리스 테마 재생
        except Exception as e:
            print(f"⚠️ BGM 시스템 로드 실패: {e}")
            self.audio_system = None
        
        # 시스템 인스턴스들
        self.job_system = job_system
        self.character_creator = character_creator
        self.interaction_system = interaction_system
        self.cooperation_system = cooperation_system
        self.tactical_system = tactical_system
        self.training_system = training_system  # AI 훈련 시스템 추가
        self.character_db = SimpleCharacterManager()  # 간단한 캐릭터 관리자 사용
        self.ai_engine = ExaoneAIEngine()
        
        # 현재 활성 파티
        self.active_party: List[str] = []
        self.party_data: Dict[str, Any] = {}
        
        # 게임 상태
        self.game_state = {
            "current_dungeon_level": 1,
            "active_battle": False,
            "party_formation": None,
            "cooperation_actions": [],
            "tactical_situation": None
        }
        
        print("🌟 AI 멀티플레이어 허브 초기화 완료")
        self._display_welcome_message()
    
    def _display_welcome_message(self):
        """환영 메시지 표시"""
        print("\n" + "="*60)
        print("🌟 Dawn of Stellar - AI 멀티플레이어 시스템")
        print("   시공교란 속에서 27개 직업의 AI들과 함께하는 모험")
        print("="*60)
        print("📊 시스템 상태:")
        print(f"   🎭 직업 시스템: {len(self.job_system.jobs)}개 직업 로드됨")
        print(f"   🤖 AI 캐릭터: {len(self.character_db.get_all_characters())}명 등록됨")
        print(f"   ⚔️ 전술 시스템: 활성화")
        print(f"   🤝 협력 시스템: 활성화")
        print(f"   💬 상호작용 시스템: 활성화")
        print(f"   🎯 훈련 시스템: 활성화")
    
    def main_menu(self):
        """메인 메뉴 (커서 기반)"""
        if not SYSTEMS_AVAILABLE:
            print("❌ 시스템이 준비되지 않았습니다.")
            return
        
        try:
            from game.cursor_menu_system import CursorMenu
            CURSOR_MENU_AVAILABLE = True
        except ImportError:
            print("⚠️ 커서 메뉴를 사용할 수 없습니다. 기본 메뉴로 진행합니다.")
            CURSOR_MENU_AVAILABLE = False
        
        if CURSOR_MENU_AVAILABLE:
            self._cursor_main_menu()
        else:
            self._simple_main_menu()
    
    def _cursor_main_menu(self):
        """커서 기반 메인 메뉴"""
        from game.cursor_menu_system import CursorMenu
        
        while True:
            options = [
                "🎭 직업 시스템 (27개 직업)",
                "🤖 AI 캐릭터 생성기", 
                "👥 파티 관리",
                "⚔️ 전투 시뮬레이션",
                "🤝 협력 시스템 테스트",
                "💬 AI 상호작용 테스트",
                "📊 시스템 상태 확인",
                "🎮 실제 게임 시작"
            ]
            
            descriptions = [
                "27개 직업의 특성과 관계를 탐색합니다",
                "직업별 맞춤형 AI 캐릭터를 자동 생성합니다",
                "파티 구성 및 멤버 관리를 합니다",
                "전투 상황 시뮬레이션과 전술 분석을 합니다",
                "AI 협력 메커니즘을 테스트합니다",
                "AI 감정 상호작용을 테스트합니다", 
                "모든 시스템의 상태를 확인합니다",
                "실제 게임을 시작합니다 (main.py 연동)"
            ]
            
            cursor_menu = CursorMenu(
                title="🌟 AI 멀티플레이어 메인 메뉴",
                extra_content="시공교란 속에서 27개 직업의 AI들과 함께하는 모험",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            try:
                result = cursor_menu.run()
                
                if result is None or result == -1:  # 취소 또는 종료
                    print("👋 AI 멀티플레이어 시스템을 종료합니다.")
                    break
                
                # 선택된 메뉴 실행
                if result == 0:
                    self.job_system.display_all_jobs_menu()
                elif result == 1:
                    self.character_creator.show_creator_menu()
                elif result == 2:
                    self._party_management_menu()
                elif result == 3:
                    self._combat_simulation_menu()
                elif result == 4:
                    self._cooperation_test_menu()
                elif result == 5:
                    self._interaction_test_menu()
                elif result == 6:
                    self._system_status_menu()
                elif result == 7:
                    self._start_actual_game()
                    
            except Exception as e:
                print(f"❌ 메뉴 처리 오류: {e}")
                input("\nEnter를 눌러 계속...")
    
    def _simple_main_menu(self):
        """기본 입력 메뉴 (폴백)"""
    def _simple_main_menu(self):
        """기본 입력 메뉴 (폴백)"""
        while True:
            print(f"\n🌟 AI 멀티플레이어 메인 메뉴")
            print("=" * 40)
            print("1. 🎭 직업 시스템 (27개 직업)")
            print("2. 🤖 AI 캐릭터 생성기")
            print("3. 👥 파티 관리")
            print("4. ⚔️ 전투 시뮬레이션")
            print("5. 🤝 협력 시스템 테스트")
            print("6. 💬 AI 상호작용 테스트")
            print("7. 🎯 AI 훈련 시스템")
            print("8. 📊 시스템 상태 확인")
            print("9. 🎮 실제 게임 시작")
            print("0. 🚪 종료")
            
            try:
                choice = input("\n선택하세요: ").strip()
                
                if choice == "1":
                    self.job_system.display_all_jobs_menu()
                elif choice == "2":
                    self.character_creator.show_creator_menu()
                elif choice == "3":
                    self._party_management_menu()
                elif choice == "4":
                    self._combat_simulation_menu()
                elif choice == "5":
                    self._cooperation_test_menu()
                elif choice == "6":
                    self._interaction_test_menu()
                elif choice == "7":
                    self._training_system_menu()
                elif choice == "8":
                    self._system_status_menu()
                elif choice == "9":
                    self._start_actual_game()
                elif choice == "0":
                    print("👋 AI 멀티플레이어 시스템을 종료합니다.")
                    break
                else:
                    print("❌ 잘못된 선택입니다.")
                    
            except Exception as e:
                print(f"❌ 메뉴 처리 오류: {e}")
            
            input("\nEnter를 눌러 계속...")
    
    def _party_management_menu(self):
        """파티 관리 메뉴 (커서 기반)"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            while True:
                # 현재 파티 상태 표시
                party_info = f"현재 파티: {len(self.active_party)}명"
                if self.active_party:
                    party_members = "\n".join([f"   • {member}" for member in self.active_party])
                    party_info += f"\n{party_members}"
                else:
                    party_info += " (파티 없음)"
                
                options = [
                    "파티 생성 (자동)",
                    "파티원 추가", 
                    "파티원 제거",
                    "파티 정보 보기",
                    "파티 해산"
                ]
                
                descriptions = [
                    "균형잡힌 파티를 자동으로 생성합니다",
                    "기존 캐릭터를 파티에 추가합니다",
                    "파티원을 제거합니다",
                    "파티 구성의 상세 정보를 확인합니다",
                    "현재 파티를 해산합니다"
                ]
                
                cursor_menu = CursorMenu(
                    title="👥 파티 관리",
                    extra_content=party_info,
                    options=options,
                    descriptions=descriptions,
                    cancellable=True
                )
                
                result = cursor_menu.run()
                
                if result is None or result == -1:  # 취소
                    break
                
                if result == 0:
                    self._auto_create_party()
                elif result == 1:
                    self._add_party_member()
                elif result == 2:
                    self._remove_party_member()
                elif result == 3:
                    self._show_party_details()
                elif result == 4:
                    self._disband_party()
                    
        except Exception as e:
            print(f"❌ 파티 관리 오류: {e}")
            self._simple_party_menu()  # 폴백
    
    def _simple_party_menu(self):
        """기본 파티 관리 메뉴 (폴백)"""
    def _simple_party_menu(self):
        """기본 파티 관리 메뉴 (폴백)"""
        while True:
            print(f"\n👥 파티 관리")
            print("=" * 30)
            print(f"현재 파티: {len(self.active_party)}명")
            if self.active_party:
                for i, member in enumerate(self.active_party, 1):
                    print(f"   {i}. {member}")
            
            print("\n1. 파티 생성 (자동)")
            print("2. 파티원 추가")
            print("3. 파티원 제거")
            print("4. 파티 정보 보기")
            print("5. 파티 해산")
            print("0. 돌아가기")
            
            try:
                choice = input("\n선택하세요: ").strip()
                
                if choice == "1":
                    self._auto_create_party()
                elif choice == "2":
                    self._add_party_member()
                elif choice == "3":
                    self._remove_party_member()
                elif choice == "4":
                    self._show_party_details()
                elif choice == "5":
                    self._disband_party()
                elif choice == "0":
                    break
                else:
                    print("❌ 잘못된 선택입니다.")
                    
            except Exception as e:
                print(f"❌ 파티 관리 오류: {e}")
    
    def _auto_create_party(self):
        """자동 파티 생성"""
        try:
            party_size = int(input("파티 크기 (2-6): "))
            if 2 <= party_size <= 6:
                # 캐릭터 생성기로 균형잡힌 파티 생성
                party_characters = self.character_creator.create_full_party_set(party_size)
                
                # 파티 멤버 설정
                self.active_party = []
                self.party_data = {}
                
                for char in party_characters:
                    name = char['name']
                    self.active_party.append(name)
                    self.party_data[name] = char
                    
                    # 데이터베이스에 저장
                    self.character_creator.save_character_to_database(char)
                
                print(f"✅ {party_size}명 파티 자동 생성 완료!")
                self._show_party_summary()
            else:
                print("❌ 파티 크기는 2-6명이어야 합니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _add_party_member(self):
        """파티원 추가"""
        if len(self.active_party) >= 6:
            print("❌ 파티는 최대 6명까지만 가능합니다.")
            return
        
        # 사용 가능한 캐릭터 표시
        all_characters = self.character_db.get_all_characters()
        available_chars = [name for name in all_characters.keys() if name not in self.active_party]
        
        if not available_chars:
            print("❌ 추가할 수 있는 캐릭터가 없습니다.")
            return
        
        print("\n사용 가능한 캐릭터:")
        for i, name in enumerate(available_chars[:10], 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input("선택 (1-10): ")) - 1
            if 0 <= choice < len(available_chars):
                selected_name = available_chars[choice]
                self.active_party.append(selected_name)
                self.party_data[selected_name] = all_characters[selected_name]
                print(f"✅ '{selected_name}'이(가) 파티에 합류했습니다!")
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _remove_party_member(self):
        """파티원 제거"""
        if not self.active_party:
            print("❌ 파티가 비어있습니다.")
            return
        
        print("\n현재 파티원:")
        for i, member in enumerate(self.active_party, 1):
            print(f"{i}. {member}")
        
        try:
            choice = int(input("제거할 멤버 선택: ")) - 1
            if 0 <= choice < len(self.active_party):
                removed_member = self.active_party.pop(choice)
                if removed_member in self.party_data:
                    del self.party_data[removed_member]
                print(f"✅ '{removed_member}'이(가) 파티에서 제거되었습니다.")
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _show_party_details(self):
        """파티 상세 정보"""
        if not self.active_party:
            print("❌ 파티가 비어있습니다.")
            return
        
        print(f"\n👥 파티 상세 정보 ({len(self.active_party)}명)")
        print("=" * 50)
        
        for i, member_name in enumerate(self.active_party, 1):
            char_data = self.party_data.get(member_name, {})
            if not char_data:
                # 데이터베이스에서 로드 시도
                all_chars = self.character_db.get_all_characters()
                char_data = all_chars.get(member_name, {})
            
            print(f"\n{i}. {member_name}")
            if char_data:
                job_info = char_data.get('learning_data', {}).get('job_info', {})
                print(f"   직업: {job_info.get('job_name', '알 수 없음')}")
                print(f"   역할: {job_info.get('tactical_role', '알 수 없음')}")
                print(f"   성격: {', '.join(char_data.get('personality', [])[:3])}")
            else:
                print("   정보 없음")
    
    def _show_party_summary(self):
        """파티 요약 정보"""
        if not self.active_party:
            return
        
        print(f"\n📋 파티 구성 요약:")
        role_count = {}
        for member in self.active_party:
            char_data = self.party_data.get(member, {})
            job_info = char_data.get('learning_data', {}).get('job_info', {})
            role = job_info.get('tactical_role', '알 수 없음')
            role_count[role] = role_count.get(role, 0) + 1
        
        for role, count in role_count.items():
            print(f"   {role}: {count}명")
    
    def _disband_party(self):
        """파티 해산"""
        if not self.active_party:
            print("❌ 해산할 파티가 없습니다.")
            return
        
        confirm = input("정말로 파티를 해산하시겠습니까? (y/N): ").strip().lower()
        if confirm == 'y':
            self.active_party = []
            self.party_data = {}
            print("✅ 파티가 해산되었습니다.")
        else:
            print("❌ 해산이 취소되었습니다.")
    
    def _combat_simulation_menu(self):
        """전투 시뮬레이션 메뉴 (커서 기반)"""
        if not self.active_party:
            print("❌ 먼저 파티를 구성해주세요.")
            input("\nEnter를 눌러 계속...")
            return
        
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "전술 상황 분석",
                "최적 포메이션 추천",
                "협력 공격 시뮬레이션", 
                "AI 전투 행동 예측"
            ]
            
            descriptions = [
                "현재 전투 상황을 분석하고 위험도를 평가합니다",
                "파티 구성에 맞는 최적 포메이션을 추천합니다",
                "파티원 간 협력 공격을 시뮬레이션합니다",
                "각 AI의 전투 행동을 예측하고 분석합니다"
            ]
            
            cursor_menu = CursorMenu(
                title="⚔️ 전투 시뮬레이션",
                extra_content=f"파티: {', '.join(self.active_party[:3])}{'...' if len(self.active_party) > 3 else ''}",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            result = cursor_menu.run()
            
            if result is None or result == -1:
                return
            
            if result == 0:
                self._analyze_tactical_situation()
            elif result == 1:
                self._recommend_formation()
            elif result == 2:
                self._simulate_cooperation_attack()
            elif result == 3:
                self._predict_ai_actions()
                
            input("\nEnter를 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 전투 시뮬레이션 오류: {e}")
            input("\nEnter를 눌러 계속...")
    
    def _analyze_tactical_situation(self):
        """전술 상황 분석"""
        print("\n🔍 전술 상황 분석")
        
        # 가상의 전투 상황 생성
        from ai_tactical_system import BattleSituation
        
        situation = BattleSituation(
            enemy_count=3,
            enemy_types=["오크전사", "고블린궁수", "트롤"],
            terrain="던전복도",
            party_hp_ratio=0.8,
            party_mp_ratio=0.6,
            turn_count=5
        )
        
        analysis = self.tactical_system.analyze_situation(situation)
        
        print(f"상황: {situation.terrain}에서 {situation.enemy_count}명의 적과 교전")
        print(f"파티 상태: HP {situation.party_hp_ratio*100:.0f}%, MP {situation.party_mp_ratio*100:.0f}%")
        print(f"전투 지속: {situation.turn_count}턴")
        print(f"\n분석 결과:")
        print(f"위험도: {analysis['threat_level']}")
        print(f"권장 전술: {analysis['recommended_strategy']}")
        print(f"우선순위: {analysis['priority_targets']}")
    
    def _recommend_formation(self):
        """포메이션 추천"""
        print("\n🎯 최적 포메이션 추천")
        
        # 파티 구성 분석
        party_roles = []
        for member in self.active_party:
            char_data = self.party_data.get(member, {})
            job_info = char_data.get('learning_data', {}).get('job_info', {})
            role = job_info.get('tactical_role', '알 수 없음')
            party_roles.append(role)
        
        print(f"현재 파티 구성: {', '.join(party_roles)}")
        
        # 포메이션 추천 로직
        formation = self.tactical_system.recommend_formation(party_roles)
        
        print(f"추천 포메이션: {formation['name']}")
        print(f"장점: {formation['advantages']}")
        print(f"주의사항: {formation['weaknesses']}")
    
    def _simulate_cooperation_attack(self):
        """협력 공격 시뮬레이션"""
        print("\n🤝 협력 공격 시뮬레이션")
        
        if len(self.active_party) < 2:
            print("❌ 협력 공격은 최소 2명이 필요합니다.")
            return
        
        # 파티 첫 2명으로 협력 공격 시뮬레이션
        member1 = self.active_party[0]
        member2 = self.active_party[1]
        
        char1 = self.party_data.get(member1, {})
        char2 = self.party_data.get(member2, {})
        
        job1 = char1.get('job_id', 'unknown')
        job2 = char2.get('job_id', 'unknown')
        
        # 협력 시너지 계산
        synergy = self.cooperation_system.calculate_synergy(job1, job2)
        
        print(f"협력 참가자: {member1} + {member2}")
        print(f"직업 조합: {job1} + {job2}")
        print(f"시너지 보너스: {synergy['bonus']:.1f}x")
        print(f"협력 타입: {synergy['cooperation_type']}")
        print(f"예상 효과: {synergy['description']}")
    
    def _predict_ai_actions(self):
        """AI 행동 예측"""
        print("\n🧠 AI 전투 행동 예측")
        
        for i, member in enumerate(self.active_party[:3], 1):  # 처음 3명만
            char_data = self.party_data.get(member, {})
            job_info = char_data.get('learning_data', {}).get('job_info', {})
            
            # 가상의 전투 상황에서 AI 행동 예측
            predicted_action = self.tactical_system.predict_ai_action(
                character=member,
                job_id=job_info.get('job_id', 'warrior'),
                situation="적과 근접전"
            )
            
            print(f"{i}. {member}:")
            print(f"   예상 행동: {predicted_action['action']}")
            print(f"   이유: {predicted_action['reasoning']}")
            print(f"   성공률: {predicted_action['success_rate']:.0f}%")
    
    def _cooperation_test_menu(self):
        """협력 시스템 테스트 메뉴 (커서 기반)"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "협력 액션 테스트",
                "시너지 계산 테스트",
                "협력 메뉴 시뮬레이션"
            ]
            
            descriptions = [
                "8가지 협력 액션 유형을 테스트합니다",
                "협력 시 시너지 보너스 계산을 테스트합니다",
                "게임 내 협력 메뉴를 시뮬레이션합니다"
            ]
            
            cursor_menu = CursorMenu(
                title="🤝 협력 시스템 테스트",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            result = cursor_menu.run()
            
            if result is None or result == -1:
                return
            
            if result == 0:
                self.cooperation_system.test_cooperation_actions()
            elif result == 1:
                self.cooperation_system.test_synergy_calculations()
            elif result == 2:
                self.cooperation_system.show_cooperation_menu()
                
            input("\nEnter를 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 협력 시스템 테스트 오류: {e}")
            input("\nEnter를 눌러 계속...")
    
    def _interaction_test_menu(self):
        """상호작용 테스트 메뉴 (커서 기반)"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            options = [
                "감정 상호작용 테스트",
                "그룹 다이나믹스 테스트",
                "상호작용 시뮬레이션"
            ]
            
            descriptions = [
                "26가지 감정 상태에 따른 상호작용을 테스트합니다",
                "그룹 내 역학 관계와 파워 밸런스를 테스트합니다",
                "AI간 자연스러운 상호작용을 시뮬레이션합니다"
            ]
            
            cursor_menu = CursorMenu(
                title="💬 AI 상호작용 테스트",
                options=options,
                descriptions=descriptions,
                cancellable=True
            )
            
            result = cursor_menu.run()
            
            if result is None or result == -1:
                return
            
            if result == 0:
                self.interaction_system.test_emotion_interactions()
            elif result == 1:
                self.interaction_system.test_group_dynamics()
            elif result == 2:
                self.interaction_system.show_interaction_menu()
                
            input("\nEnter를 눌러 계속...")
                
        except Exception as e:
            print(f"❌ 상호작용 테스트 오류: {e}")
            input("\nEnter를 눌러 계속...")
    
    def _system_status_menu(self):
        """시스템 상태 확인"""
        print("\n📊 시스템 상태")
        print("=" * 40)
        
        # 각 시스템 상태 확인
        print("🎭 직업 시스템:")
        print(f"   로드된 직업: {len(self.job_system.jobs)}개")
        for category, jobs in self.job_system.job_categories.items():
            print(f"   {category.value}: {len(jobs)}개")
        
        print("\n🤖 AI 캐릭터:")
        all_chars = self.character_db.get_all_characters()
        print(f"   등록된 캐릭터: {len(all_chars)}명")
        
        print("\n👥 현재 파티:")
        if self.active_party:
            print(f"   파티원: {len(self.active_party)}명")
            for member in self.active_party:
                print(f"     • {member}")
        else:
            print("   파티 없음")
        
        print("\n🔧 시스템 모듈:")
        modules = [
            ("직업 시스템", hasattr(self, 'job_system')),
            ("캐릭터 생성기", hasattr(self, 'character_creator')),
            ("상호작용 시스템", hasattr(self, 'interaction_system')),
            ("협력 시스템", hasattr(self, 'cooperation_system')),
            ("전술 시스템", hasattr(self, 'tactical_system')),
            ("AI 엔진", hasattr(self, 'ai_engine'))
        ]
        
        for module_name, status in modules:
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {module_name}")
    
    def _start_actual_game(self):
        """실제 게임 시작"""
        print("\n🎮 게임 시작")
        print("=" * 30)
        
        if not self.active_party:
            print("❌ 먼저 파티를 구성해주세요.")
            return
        
        print("🚀 AI 멀티플레이어 게임을 시작합니다!")
        print(f"파티: {', '.join(self.active_party)}")
        
        # 실제 게임 로직은 main.py와 연동
        try:
            print("🔗 메인 게임과 연동 중...")
            
            # 게임 상태 설정
            self.game_state.update({
                "active_party": self.active_party,
                "party_data": self.party_data,
                "ai_mode": True
            })
            
            print("✅ AI 멀티플레이어 모드가 활성화되었습니다!")
            print("💡 이제 main.py를 실행하여 게임을 시작하세요.")
            
            # 파티 정보를 파일로 저장 (main.py에서 읽을 수 있도록)
            self._save_party_info()
            
        except Exception as e:
            print(f"❌ 게임 시작 오류: {e}")
    
    def _save_party_info(self):
        """파티 정보를 파일로 저장"""
        try:
            import json
            
            party_info = {
                "active_party": self.active_party,
                "party_data": self.party_data,
                "game_state": self.game_state
            }
            
            with open("ai_party_info.json", 'w', encoding='utf-8') as f:
                json.dump(party_info, f, ensure_ascii=False, indent=2)
            
            print("💾 파티 정보가 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 파티 정보 저장 실패: {e}")
    
    def _training_system_menu(self):
        """AI 훈련 시스템 메뉴"""
        try:
            print("\n🎯 AI 훈련 시스템에 연결 중...")
            
            # 훈련 시스템이 있는지 확인
            if hasattr(self, 'training_system') and self.training_system:
                self.training_system.show_training_menu()
            else:
                # 훈련 시스템 연결 시도
                try:
                    from ai_training_system import training_system
                    self.training_system = training_system
                    self.training_system.show_training_menu()
                except ImportError:
                    print("❌ AI 훈련 시스템을 찾을 수 없습니다.")
                    print("   ai_training_system.py 파일이 있는지 확인해주세요.")
                    
        except Exception as e:
            print(f"❌ 훈련 시스템 오류: {e}")

def main():
    """메인 실행 함수"""
    if not SYSTEMS_AVAILABLE:
        print("❌ 필수 시스템을 로드할 수 없어 종료합니다.")
        return
    
    # AI 멀티플레이어 허브 시작
    hub = AIMultiplayerHub()
    hub.main_menu()

if __name__ == "__main__":
    main()
