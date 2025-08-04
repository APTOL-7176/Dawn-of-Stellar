"""
트레이닝 룸 시스템 - 무제한 리소스와 커스텀 적 시스템
전용 고정 맵과 모든 장비/아이템 접근 기능 포함
특별한 공간: 인카운터 없음, 세이브 불가, 불사 모드
"""
import json
import os
import time
from typing import List, Dict, Optional
from .character import Character
from .brave_combat import BraveCombatSystem
from .display import GameDisplay
from .items import Inventory, Item, Equipment  
from .cursor_menu_system import CursorMenu, create_simple_menu
from .color_text import *
from copy import deepcopy

class TrainingRoom:
    """트레이닝 룸 - 무제한 리소스로 연습 가능 (인카운터 없음, 불사 모드, 세이브 불가)"""
    
    def __init__(self, audio_system=None, keyboard=None):
        self.audio_system = audio_system
        self.keyboard = keyboard
        self.training_party = []
        self.custom_enemies = []
        self.unlimited_items = self._init_unlimited_items()
        self.is_training_space = True  # 특별한 공간 플래그
        self.display = GameDisplay()  # GameDisplay 인스턴스 생성
        
    def _init_unlimited_items(self) -> Dict:
        """무제한 아이템 목록 초기화"""
        return {
            # 회복 아이템
            "체력 포션": {"quantity": 999, "type": "healing", "power": 100},
            "마나 포션": {"quantity": 999, "type": "mana", "power": 80},
            "완전 회복 포션": {"quantity": 999, "type": "full_heal", "power": 999},
            "BRV 부스터": {"quantity": 999, "type": "brave", "power": 500},
            
            # 버프 아이템
            "공격력 강화 포션": {"quantity": 999, "type": "attack_buff", "power": 50, "duration": 10},
            "방어력 강화 포션": {"quantity": 999, "type": "defense_buff", "power": 50, "duration": 10},
            "속도 강화 포션": {"quantity": 999, "type": "speed_buff", "power": 30, "duration": 10},
            "만능 강화 포션": {"quantity": 999, "type": "all_buff", "power": 30, "duration": 15},
            
            # 특수 아이템
            "경험치 부스터": {"quantity": 999, "type": "exp_boost", "power": 1000},
            "레벨업 스크롤": {"quantity": 999, "type": "level_up", "power": 1},
            "스킬 포인트 증가": {"quantity": 999, "type": "skill_point", "power": 5},
            "골드 주머니": {"quantity": 999, "type": "gold", "power": 10000},
        }
    
    def enter_training_room(self, party_manager):
        """트레이닝 룸 입장 - 특별한 공간 (인카운터 없음, 불사 모드)"""
        
        print(f"\n{bright_cyan('🏋️‍♂️ 트레이닝 룸에 오신 것을 환영합니다! 🏋️‍♂️')}")
        print("="*60)
        print("💪 무제한 리소스로 전투 실력을 향상시키세요!")
        print("⚔️ 커스텀 적과 전투하여 새로운 전술을 시험해보세요!")
        print("👥 다양한 파티 구성을 실험해보세요!")
        print(f"{bright_yellow('🛡️ 특별한 공간: 인카운터 없음, 죽지 않음, 세이브 불가')}")
        print("="*60)
        
        while True:
            try:
                from .cursor_menu_system import create_simple_menu
                
                menu_options = [
                    "👥 파티 구성하기",
                    "⚔️ 커스텀 적 생성",
                    "🛡️ 전투 시작",
                    "🎒 무제한 아이템 지급",
                    "📊 파티 상태 확인",
                    "💾 트레이닝 세팅 저장",
                    "📁 트레이닝 세팅 로드",
                    "🚪 메인 메뉴로 돌아가기"
                ]
                
                menu_descriptions = [
                    "트레이닝용 파티를 구성합니다 (최대 4명)",
                    "연습할 적을 커스터마이징합니다",
                    "구성된 파티와 적으로 전투를 시작합니다",
                    "파티원들에게 무제한 아이템을 지급합니다",
                    "현재 파티의 상세 정보를 확인합니다",
                    "현재 트레이닝 설정을 파일로 저장합니다",
                    "저장된 트레이닝 설정을 불러옵니다",
                    "트레이닝 룸을 나가고 메인 메뉴로 돌아갑니다"
                ]
                
                menu = create_simple_menu(
                    "🏋️‍♂️ 트레이닝 룸 메뉴", 
                    menu_options, 
                    menu_descriptions,
                    clear_screen=True
                )
                choice = menu.run()
                
                if choice == 0:  # 파티 구성
                    self._setup_training_party(party_manager)
                elif choice == 1:  # 커스텀 적 생성
                    self._create_custom_enemies()
                elif choice == 2:  # 전투 시작
                    if not self.training_party:
                        print(f"\n{bright_red('❌ 먼저 파티를 구성해주세요!')}")
                        input("계속하려면 Enter를 누르세요...")
                        continue
                    if not self.custom_enemies:
                        print(f"\n{bright_red('❌ 먼저 적을 생성해주세요!')}")
                        input("계속하려면 Enter를 누르세요...")
                        continue
                    self._start_training_battle()
                elif choice == 3:  # 무제한 아이템 지급
                    self._distribute_unlimited_items()
                elif choice == 4:  # 파티 상태 확인
                    self._show_party_status()
                elif choice == 5:  # 세팅 저장 (트레이닝 룸에서는 비활성화)
                    print(f"\n{bright_yellow('⚠️ 트레이닝 룸에서는 세이브 기능이 비활성화되어 있습니다.')}")
                    print("이곳은 연습용 특별한 공간입니다.")
                    input("계속하려면 Enter를 누르세요...")
                elif choice == 6:  # 세팅 로드 (트레이닝 룸에서는 비활성화)
                    print(f"\n{bright_yellow('⚠️ 트레이닝 룸에서는 로드 기능이 비활성화되어 있습니다.')}")
                    print("이곳은 연습용 특별한 공간입니다.")
                    input("계속하려면 Enter를 누르세요...")
                elif choice == 7 or choice is None:  # 나가기
                    print(f"\n{bright_green('🏋️‍♂️ 트레이닝 룸을 나갑니다. 수고하셨습니다!')}")
                    break
                    
            except ImportError:
                # 폴백 메뉴
                print("\n🏋️‍♂️ 트레이닝 룸 메뉴:")
                print("1. 파티 구성하기")
                print("2. 커스텀 적 생성")
                print("3. 전투 시작") 
                print("4. 무제한 아이템 지급")
                print("5. 파티 상태 확인")
                print("6. 나가기")
                
                choice = input("선택하세요 (1-6): ").strip()
                
                if choice == "1":
                    self._setup_training_party(party_manager)
                elif choice == "2":
                    self._create_custom_enemies()
                elif choice == "3":
                    if self.training_party and self.custom_enemies:
                        self._start_training_battle()
                    else:
                        print("❌ 파티와 적을 먼저 설정해주세요!")
                elif choice == "4":
                    self._distribute_unlimited_items()
                elif choice == "5":
                    self._show_party_status()
                elif choice == "6":
                    break
    
    def _setup_training_party(self, party_manager):
        """트레이닝 파티 구성 - 오토 파티 빌더 활용"""
        
        print(f"\n{bright_yellow('👥 트레이닝 파티 구성')}")
        print("="*50)
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            party_options = [
                "🤖 오토 파티 빌더 사용",
                "👤 기존 파티원 복사",
                "🆕 수동 캐릭터 생성",
                "✅ 구성 완료"
            ]
            party_descriptions = [
                "자동으로 밸런스 잡힌 파티를 생성합니다",
                "메인 게임의 파티원을 트레이닝용으로 복사합니다",
                "직접 캐릭터를 하나씩 생성합니다",
                "현재 파티 구성을 완료합니다"
            ]
            
            while len(self.training_party) < 4:
                print(f"\n현재 파티: {len(self.training_party)}/4명")
                if self.training_party:
                    for i, member in enumerate(self.training_party):
                        print(f"  {i+1}. {member.name} (Lv.{member.level}) - {member.character_class}")
                
                party_menu = create_simple_menu(
                    f"파티 구성 ({len(self.training_party)}/4명)", 
                    party_options, 
                    party_descriptions,
                    clear_screen=False
                )
                choice = party_menu.run()
                
                if choice == 0:  # 오토 파티 빌더
                    self._use_auto_party_builder()
                elif choice == 1:  # 기존 파티원 복사
                    self._copy_existing_party(party_manager)
                elif choice == 2:  # 수동 생성
                    new_char = self._create_new_training_character()
                    if new_char:
                        self.training_party.append(new_char)
                elif choice == 3 or choice is None:  # 구성 완료
                    break
                    
        except ImportError:
            # 폴백: 기본 메뉴
            print("\n파티 구성 옵션:")
            print("1. 오토 파티 빌더 사용")
            print("2. 기존 파티원 복사")
            print("3. 수동 캐릭터 생성")
            print("4. 구성 완료")
            
            choice = input("선택하세요 (1-4): ").strip()
            
            if choice == "1":
                self._use_auto_party_builder()
            elif choice == "2":
                self._copy_existing_party(party_manager)
            elif choice == "3":
                new_char = self._create_new_training_character()
                if new_char:
                    self.training_party.append(new_char)
            elif choice == "4":
                return
        
        if self.training_party:
            print(f"\n{bright_green('✅ 트레이닝 파티 구성 완료!')}")
            print("파티원:")
            for i, member in enumerate(self.training_party):
                print(f"  {i+1}. {member.name} (Lv.{member.level}) - {member.character_class}")
        else:
            print(f"\n{bright_yellow('⚠️ 파티가 구성되지 않았습니다.')}")
        
        input("계속하려면 Enter를 누르세요...")
    
    def _use_auto_party_builder(self):
        """오토 파티 빌더로 파티 생성"""
        try:
            from .auto_party_builder import AutoPartyBuilder
            
            print(f"\n{bright_cyan('🤖 오토 파티 빌더 시작')}")
            print("자동으로 밸런스 잡힌 파티를 생성합니다...")
            
            builder = AutoPartyBuilder()
            
            # 난이도 선택
            try:
                from .cursor_menu_system import create_simple_menu
                
                difficulty_options = [
                    "🔵 평온한 여행",
                    "🟢 균형잡힌 모험", 
                    "🟠 시련의 여정",
                    "❤️ 악몽 같은 시련",
                    "💀 지옥의 심연"
                ]
                difficulty_descriptions = [
                    "편안한 모험 (레벨 5-10)",
                    "표준 난이도 (레벨 10-15)",
                    "도전적 난이도 (레벨 15-20)",
                    "극한의 도전 (레벨 20-25)",
                    "절망적 난이도 (레벨 25-30)"
                ]
                
                diff_menu = create_simple_menu(
                    "파티 난이도 선택", 
                    difficulty_options, 
                    difficulty_descriptions,
                    clear_screen=False
                )
                diff_choice = diff_menu.run()
                
                # 난이도에 따른 레벨 범위
                level_ranges = [
                    (5, 10),   # 평온
                    (10, 15),  # 보통
                    (15, 20),  # 도전
                    (20, 25),  # 악몽
                    (25, 30)   # 지옥
                ]
                
                if diff_choice is not None and 0 <= diff_choice < len(level_ranges):
                    min_level, max_level = level_ranges[diff_choice]
                else:
                    min_level, max_level = 10, 15  # 기본값
                    
            except ImportError:
                min_level, max_level = 10, 15  # 기본값
            
            # 파티 크기 결정
            remaining_slots = 4 - len(self.training_party)
            if remaining_slots <= 0:
                print("❌ 파티가 이미 가득 찼습니다!")
                return
            
            # 오토 파티 빌더로 파티 생성
            print(f"📊 생성 중... (레벨 {min_level}-{max_level}, {remaining_slots}명)")
            
            # 간단한 파티 생성 (오토 빌더의 일부 기능 활용)
            party_roles = ["탱커", "딜러", "마법사", "서포터"]
            role_classes = {
                "탱커": ["전사", "성기사", "기사", "검투사"],
                "딜러": ["궁수", "도적", "암살자", "검성"],
                "마법사": ["아크메이지", "네크로맨서", "정령술사"],
                "서포터": ["바드", "신관", "드루이드"]
            }
            
            import random
            for i in range(remaining_slots):
                if i < len(party_roles):
                    role = party_roles[i]
                    class_list = role_classes[role]
                    selected_class = random.choice(class_list)
                    
                    # 캐릭터 생성
                    char_name = f"트레이닝 {selected_class}"
                    level = random.randint(min_level, max_level)
                    
                    new_char = Character(char_name, selected_class)
                    new_char.level = level
                    
                    # 레벨에 맞는 스탯 조정
                    stat_bonus = (level - 1) * 5
                    new_char.max_hp += stat_bonus * 10
                    new_char.current_hp = new_char.max_hp
                    new_char.max_mp += stat_bonus * 5
                    new_char.current_mp = new_char.max_mp
                    new_char.physical_attack += stat_bonus
                    new_char.physical_defense += stat_bonus
                    new_char.magical_attack += stat_bonus
                    new_char.magical_defense += stat_bonus
                    new_char.speed += stat_bonus // 2
                    
                    # 트레이닝용 골드 지급
                    new_char.gold = 100000
                    
                    self.training_party.append(new_char)
                    print(f"✅ {new_char.name} (Lv.{level}) 추가!")
            
            print(f"\n{bright_green('🤖 오토 파티 빌더 완료!')}")
            
        except ImportError:
            print(f"{bright_red('❌ 오토 파티 빌더를 불러올 수 없습니다.')}")
            print("수동으로 캐릭터를 생성해주세요.")
        except Exception as e:
            print(f"{bright_red(f'❌ 오토 파티 빌더 오류: {e}')}")
    
    def _copy_existing_party(self, party_manager):
        """기존 파티원 복사"""
        if not hasattr(party_manager, 'members') or not party_manager.members:
            print(f"{bright_red('❌ 복사할 파티원이 없습니다!')}")
            return
        
        print(f"\n{bright_cyan('👤 기존 파티원 복사')}")
        print("사용 가능한 캐릭터:")
        
        available_characters = [char for char in party_manager.members if char not in self.training_party]
        
        if not available_characters:
            print("❌ 복사할 수 있는 캐릭터가 없습니다!")
            return
        
        for i, char in enumerate(available_characters):
            status = "🟢 생존" if char.is_alive else "💀 전투불능"
            print(f"{i+1}. {char.name} (Lv.{char.level}) - {char.character_class} [{status}]")
        
        try:
            choice = int(input("복사할 캐릭터 번호: ")) - 1
            if 0 <= choice < len(available_characters):
                selected_char = available_characters[choice]
                training_char = self._create_training_character(selected_char)
                self.training_party.append(training_char)
                print(f"✅ {training_char.name}이(가) 트레이닝 파티에 추가되었습니다!")
            else:
                print("❌ 잘못된 선택입니다!")
        except ValueError:
            print("❌ 유효한 숫자를 입력해주세요!")
    
    def _create_training_character(self, original_char: Character) -> Character:
        """트레이닝용 캐릭터 복사본 생성 (강화된 버전)"""
        training_char = deepcopy(original_char)
        
        # 트레이닝용 강화
        training_char.current_hp = training_char.max_hp  # 완전 회복
        training_char.current_mp = training_char.max_mp  # 완전 회복
        training_char.brave_points = getattr(training_char, 'int_brv', 500)  # BRV 초기화
        
        # 상태이상 모두 제거
        if hasattr(training_char, 'status_manager'):
            training_char.status_manager.clear_all_effects()
        
        # 추가 골드 지급
        if hasattr(training_char, 'gold'):
            training_char.gold += 50000
        
        return training_char
    
    def _create_new_training_character(self) -> Optional[Character]:
        """새로운 트레이닝 캐릭터 생성"""
        
        print(f"\n{bright_cyan('🆕 새 트레이닝 캐릭터 생성')}")
        
        # 직업 선택을 커서 메뉴로
        available_classes = [
            "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", 
            "몽크", "바드", "네크로맨서", "용기사", "검성", "정령술사",
            "시간술사", "연금술사", "차원술사", "암살자", "기계공학자",
            "무당", "해적", "사무라이", "드루이드", "철학자", "검투사",
            "기사", "신관", "마검사", "광전사"
        ]
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            class_options = []
            class_descriptions = []
            
            for job_class in available_classes:
                class_options.append(f"⚔️ {job_class}")
                class_descriptions.append(f"{job_class} 직업으로 캐릭터를 생성합니다")
            
            class_menu = create_simple_menu(
                "직업 선택", 
                class_options, 
                class_descriptions,
                clear_screen=False
            )
            class_choice = class_menu.run()
            
            if class_choice is None or class_choice < 0 or class_choice >= len(available_classes):
                print("❌ 캐릭터 생성이 취소되었습니다!")
                return None
                
            selected_class = available_classes[class_choice]
            
        except ImportError:
            # 폴백: 기존 텍스트 방식
            print("사용 가능한 직업:")
            for i, job_class in enumerate(available_classes):
                print(f"{i+1:2d}. {job_class}")
            
            try:
                class_choice = int(input("직업을 선택하세요: ")) - 1
                if 0 <= class_choice < len(available_classes):
                    selected_class = available_classes[class_choice]
                else:
                    print("❌ 잘못된 선택입니다!")
                    return None
            except ValueError:
                print("❌ 유효한 숫자를 입력해주세요!")
                return None
        
        # 이름 입력
        name = input("캐릭터 이름을 입력하세요: ").strip()
        if not name:
            name = f"트레이닝 {selected_class}"
        
        # 레벨 선택을 커서 메뉴로
        try:
            from .cursor_menu_system import create_simple_menu
            
            level_options = []
            level_descriptions = []
            
            level_ranges = [
                (1, 5, "초급"),
                (10, 15, "중급"), 
                (20, 25, "고급"),
                (30, 35, "전문가"),
                (40, 45, "마스터"),
                (50, 50, "최고수")
            ]
            
            for min_lv, max_lv, tier in level_ranges:
                if min_lv == max_lv:
                    level_options.append(f"⭐ 레벨 {min_lv} ({tier})")
                    level_descriptions.append(f"최고 레벨 {min_lv}로 캐릭터를 생성합니다")
                else:
                    level_options.append(f"📈 레벨 {min_lv}-{max_lv} ({tier})")
                    level_descriptions.append(f"레벨 {min_lv}~{max_lv} 범위에서 랜덤 생성합니다")
            
            level_options.append("🎯 직접 입력")
            level_descriptions.append("원하는 레벨을 직접 입력합니다 (1-50)")
            
            level_menu = create_simple_menu(
                f"{name}의 레벨 선택", 
                level_options, 
                level_descriptions,
                clear_screen=False
            )
            level_choice = level_menu.run()
            
            if level_choice is None or level_choice < 0:
                print("❌ 캐릭터 생성이 취소되었습니다!")
                return None
            elif level_choice < len(level_ranges):
                # 미리 정의된 레벨 범위 선택
                min_lv, max_lv, _ = level_ranges[level_choice]
                if min_lv == max_lv:
                    level = min_lv
                else:
                    import random
                    level = random.randint(min_lv, max_lv)
            else:
                # 직접 입력
                try:
                    level = int(input("레벨을 입력하세요 (1-50): "))
                    level = max(1, min(level, 50))
                except ValueError:
                    level = 10  # 기본값
                    
        except ImportError:
            # 폴백: 기존 텍스트 입력 방식
            try:
                level = int(input("레벨을 설정하세요 (1-50): "))
                level = max(1, min(level, 50))
            except ValueError:
                level = 10  # 기본값
        
        # 캐릭터 생성
        new_char = Character(name, selected_class)
        
        # 레벨 설정
        new_char.level = level
        
        # 레벨에 맞는 스탯 계산
        stat_per_level = 5
        bonus_stats = (level - 1) * stat_per_level
        
        new_char.max_hp += bonus_stats * 10
        new_char.current_hp = new_char.max_hp
        new_char.max_mp += bonus_stats * 5
        new_char.current_mp = new_char.max_mp
        new_char.physical_attack += bonus_stats
        new_char.physical_defense += bonus_stats
        new_char.magical_attack += bonus_stats
        new_char.magical_defense += bonus_stats
        new_char.speed += bonus_stats // 2
        
        # BRV 스탯 설정
        if hasattr(new_char, 'int_brv'):
            new_char.int_brv += bonus_stats * 2
            new_char.max_brv += bonus_stats * 5
            new_char.brave_points = new_char.int_brv
        
        # 트레이닝용 골드 지급
        new_char.gold = 100000
        
        print(f"\n{bright_green(f'✅ {name} (Lv.{level} {selected_class})이(가) 생성되었습니다!')}")
        return new_char
    
    def _create_custom_enemies(self):
        """커스텀 적 생성"""
        
        print(f"\n{bright_red('⚔️ 커스텀 적 생성')}")
        print("="*50)
        
        self.custom_enemies = []
        
        # 기본 적 템플릿
        enemy_templates = {
            "고블린": {"hp": 800, "attack": 120, "defense": 80, "speed": 90},
            "오크": {"hp": 1200, "attack": 150, "defense": 120, "speed": 70},
            "스켈레톤": {"hp": 600, "attack": 100, "defense": 60, "speed": 110},
            "트롤": {"hp": 2000, "attack": 180, "defense": 150, "speed": 50},
            "다크엘프": {"hp": 900, "attack": 140, "defense": 90, "speed": 130},
            "드래곤": {"hp": 5000, "attack": 300, "defense": 200, "speed": 80},
            "리치": {"hp": 1500, "attack": 250, "defense": 100, "speed": 90},
            "고렘": {"hp": 3000, "attack": 200, "defense": 300, "speed": 30}
        }
        
        while len(self.custom_enemies) < 4:  # 최대 4마리
            print(f"\n현재 적 구성: {len(self.custom_enemies)}/4마리")
            if self.custom_enemies:
                for i, enemy in enumerate(self.custom_enemies):
                    print(f"  {i+1}. {enemy.name} (HP: {enemy.max_hp}, ATK: {enemy.physical_attack})")
            
            # 적 선택을 커서 메뉴로
            try:
                from .cursor_menu_system import create_simple_menu
                
                enemy_options = []
                enemy_descriptions = []
                
                template_names = list(enemy_templates.keys())
                for template in template_names:
                    stats = enemy_templates[template]
                    enemy_options.append(f"👹 {template}")
                    enemy_descriptions.append(f"HP:{stats['hp']}, ATK:{stats['attack']}, DEF:{stats['defense']}, SPD:{stats['speed']}")
                
                enemy_options.append("✅ 적 구성 완료")
                enemy_descriptions.append("현재 적 구성을 완료하고 메뉴로 돌아갑니다")
                
                enemy_menu = create_simple_menu(
                    f"적 선택 ({len(self.custom_enemies)}/4마리)", 
                    enemy_options, 
                    enemy_descriptions,
                    clear_screen=False
                )
                choice = enemy_menu.run()
                
                if choice is None or choice < 0:
                    break
                elif choice < len(template_names):
                    template_name = template_names[choice]
                    custom_enemy = self._create_custom_enemy(template_name, enemy_templates[template_name])
                    self.custom_enemies.append(custom_enemy)
                    print(f"✅ {custom_enemy.name}이(가) 추가되었습니다!")
                else:
                    break
                    
            except ImportError:
                # 폴백: 기존 텍스트 입력 방식
                print("\n사용 가능한 적 템플릿:")
                template_names = list(enemy_templates.keys())
                for i, template in enumerate(template_names):
                    stats = enemy_templates[template]
                    print(f"{i+1}. {template} (HP:{stats['hp']}, ATK:{stats['attack']}, DEF:{stats['defense']}, SPD:{stats['speed']})")
                
                print(f"{len(template_names)+1}. ✅ 적 구성 완료")
                
                try:
                    choice = int(input("적을 선택하세요: "))
                    
                    if 1 <= choice <= len(template_names):
                        template_name = template_names[choice - 1]
                        custom_enemy = self._create_custom_enemy(template_name, enemy_templates[template_name])
                        self.custom_enemies.append(custom_enemy)
                        print(f"✅ {custom_enemy.name}이(가) 추가되었습니다!")
                    elif choice == len(template_names) + 1:
                        break
                    else:
                        print("❌ 잘못된 선택입니다!")
                        
                except ValueError:
                    print("❌ 유효한 숫자를 입력해주세요!")
        
        if self.custom_enemies:
            print(f"\n{bright_green('✅ 커스텀 적 구성 완료!')}")
            print("적 구성:")
            for i, enemy in enumerate(self.custom_enemies):
                print(f"  {i+1}. {enemy.name} (HP: {enemy.max_hp}, ATK: {enemy.physical_attack})")
        else:
            print(f"\n{bright_yellow('⚠️ 적이 구성되지 않았습니다.')}")
        
        input("계속하려면 Enter를 누르세요...")
    
    def _create_custom_enemy(self, template_name: str, base_stats: Dict) -> Character:
        """커스텀 적 생성"""
        print(f"\n📝 {template_name} 커스터마이징:")
        
        # 커스텀 설정으로 바로 진행
        level, multiplier = self._custom_enemy_settings()
        
        # 적 이름 설정
        enemy_name = input(f"적 이름을 설정하세요 (기본값: Lv.{level} {template_name}): ").strip()
        if not enemy_name:
            enemy_name = f"Lv.{level} {template_name}"
        
        print(f"✅ {enemy_name} 생성 완료! (레벨: {level}, 배율: {multiplier}x)")
        
        # 적 캐릭터 생성
        enemy = Character(enemy_name, "Enemy")
        enemy.level = level
        
        # 스탯 적용
        level_bonus = (level - 1) * 0.1  # 레벨당 10% 증가
        final_multiplier = multiplier * (1.0 + level_bonus)
        
        enemy.max_hp = int(base_stats["hp"] * final_multiplier)
        enemy.current_hp = enemy.max_hp
        enemy.physical_attack = int(base_stats["attack"] * final_multiplier)
        enemy.physical_defense = int(base_stats["defense"] * final_multiplier)
        enemy.speed = int(base_stats["speed"] * final_multiplier)
        
        # 기본 MP 설정
        enemy.max_mp = 100 + level * 10
        enemy.current_mp = enemy.max_mp
        
        # BRV 스탯 설정
        try:
            from .balance import GameBalance
            brave_stats = GameBalance.get_enemy_brave_stats(template_name, level)
            enemy.int_brv = brave_stats["int_brv"]
            enemy.max_brv = brave_stats["max_brv"]
            enemy.brave_points = enemy.int_brv
        except ImportError:
            # 기본 BRV 설정
            enemy.int_brv = 200 + level * 20
            enemy.max_brv = 1500 + level * 100
            enemy.brave_points = enemy.int_brv
        
        return enemy
    
    def _custom_enemy_settings(self):
        """커스텀 적 설정 (레벨 + 배율)"""
        # 레벨 설정을 커서 메뉴로
        try:
            from .cursor_menu_system import create_simple_menu
            
            level_options = [
                "🟢 레벨 1-5 (약함)",
                "🟡 레벨 6-10 (보통)", 
                "🟠 레벨 11-15 (강함)",
                "🔴 레벨 16-20 (매우 강함)",
                "🎯 직접 설정"
            ]
            level_descriptions = [
                "레벨 1-5 범위에서 랜덤 설정",
                "레벨 6-10 범위에서 랜덤 설정",
                "레벨 11-15 범위에서 랜덤 설정", 
                "레벨 16-20 범위에서 랜덤 설정",
                "원하는 레벨을 직접 입력 (1-20)"
            ]
            
            level_menu = create_simple_menu(
                "레벨 설정", 
                level_options, 
                level_descriptions,
                clear_screen=False
            )
            level_choice = level_menu.run()
            
            if level_choice == 0:
                import random
                level = random.randint(1, 5)
            elif level_choice == 1:
                import random
                level = random.randint(6, 10)
            elif level_choice == 2:
                import random
                level = random.randint(11, 15)
            elif level_choice == 3:
                import random
                level = random.randint(16, 20)
            elif level_choice == 4:
                try:
                    level = int(input(f"레벨을 설정하세요 (1-20): ") or "5")
                    level = max(1, min(level, 20))
                except ValueError:
                    level = 5
            else:
                level = 5  # 기본값
                
        except ImportError:
            # 폴백: 기존 텍스트 입력 방식
            try:
                level = int(input(f"레벨을 설정하세요 (1-20, 기본값 5): ") or "5")
                level = max(1, min(level, 20))
            except ValueError:
                level = 5
        
        # 배율 설정을 커서 메뉴로
        try:
            from .cursor_menu_system import create_simple_menu  # 다시 import 필요
            
            multiplier_options = [
                "🟢 0.5배 (매우 약함)",
                "🟡 0.7배 (약함)",
                "⚪ 1.0배 (기본)",
                "🟠 1.5배 (강함)",
                "🔴 2.0배 (매우 강함)",
                "💀 3.0배 (극한)",
                "🎯 직접 설정"
            ]
            multiplier_descriptions = [
                "능력치를 50%로 약화시킵니다",
                "능력치를 70%로 약화시킵니다", 
                "기본 능력치를 그대로 사용합니다",
                "능력치를 150%로 강화시킵니다",
                "능력치를 200%로 강화시킵니다",
                "능력치를 300%로 극한 강화시킵니다",
                "원하는 배율을 직접 입력 (0.5-3.0)"
            ]
            
            multiplier_menu = create_simple_menu(
                "능력치 배율", 
                multiplier_options, 
                multiplier_descriptions,
                clear_screen=False
            )
            multiplier_choice = multiplier_menu.run()
            
            multiplier_values = [0.5, 0.7, 1.0, 1.5, 2.0, 3.0]
            if multiplier_choice < len(multiplier_values):
                multiplier = multiplier_values[multiplier_choice]
            elif multiplier_choice == len(multiplier_values):
                try:
                    multiplier = float(input(f"능력치 배율을 설정하세요 (0.5-3.0): ") or "1.0")
                    multiplier = max(0.5, min(multiplier, 3.0))
                except ValueError:
                    multiplier = 1.0
            else:
                multiplier = 1.0  # 기본값
                
        except ImportError:
            # 폴백: 기존 텍스트 입력 방식
            try:
                multiplier = float(input(f"능력치 배율을 설정하세요 (0.5-3.0, 기본값 1.0): ") or "1.0")
                multiplier = max(0.5, min(multiplier, 3.0))
            except ValueError:
                multiplier = 1.0
        
        return level, multiplier
        
        # 적 캐릭터 생성
        enemy = Character(enemy_name, "Enemy")
        enemy.level = level
        
        # 스탯 적용
        level_bonus = (level - 1) * 0.1  # 레벨당 10% 증가
        final_multiplier = multiplier * (1.0 + level_bonus)
        
        enemy.max_hp = int(base_stats["hp"] * final_multiplier)
        enemy.current_hp = enemy.max_hp
        enemy.physical_attack = int(base_stats["attack"] * final_multiplier)
        enemy.physical_defense = int(base_stats["defense"] * final_multiplier)
        enemy.speed = int(base_stats["speed"] * final_multiplier)
        
        # 기본 MP 설정
        enemy.max_mp = 100 + level * 10
        enemy.current_mp = enemy.max_mp
        
        # BRV 스탯 설정
        try:
            from .balance import GameBalance
            brave_stats = GameBalance.get_enemy_brave_stats(template_name, level)
            enemy.int_brv = brave_stats["int_brv"]
            enemy.max_brv = brave_stats["max_brv"]
            enemy.brave_points = enemy.int_brv
        except ImportError:
            # 기본 BRV 설정
            enemy.int_brv = 200 + level * 20
            enemy.max_brv = 1500 + level * 100
            enemy.brave_points = enemy.int_brv
        
        return enemy
    
    def _start_training_battle(self):
        """트레이닝 전투 시작 - 불사 모드"""
        
        print(f"\n{bright_cyan('⚔️ 트레이닝 전투 시작!')}")
        print("="*50)
        
        print("파티:")
        for member in self.training_party:
            print(f"  🟢 {member.name} (Lv.{member.level}) - HP: {member.current_hp}/{member.max_hp}")
        
        print("\n적:")
        for enemy in self.custom_enemies:
            print(f"  🔴 {enemy.name} - HP: {enemy.current_hp}/{enemy.max_hp}")
        
        print(f"\n{bright_yellow('💡 이것은 트레이닝 전투입니다. 패배해도 손실이 없습니다!')}")
        print(f"{bright_green('🛡️ 불사 모드: 전투불능이 되어도 HP 1로 부활합니다!')}")
        
        # 전투 시작 확인을 커서 메뉴로
        try:
            from .cursor_menu_system import create_simple_menu
            
            confirm_options = ["⚔️ 전투 시작", "❌ 취소"]
            confirm_descriptions = [
                "트레이닝 전투를 시작합니다",
                "전투를 취소하고 메뉴로 돌아갑니다"
            ]
            
            confirm_menu = create_simple_menu(
                "전투 시작 확인", 
                confirm_options, 
                confirm_descriptions,
                clear_screen=False
            )
            confirm_choice = confirm_menu.run()
            
            if confirm_choice != 0:  # 취소 선택
                print("전투가 취소되었습니다.")
                return
                
        except ImportError:
            # 폴백: 기존 방식
            confirm = input("전투를 시작하시겠습니까? (y/N): ").strip().lower()
            if confirm != 'y':
                print("전투가 취소되었습니다.")
                return
        
        # 전투 시스템 초기화
        combat_system = BraveCombatSystem(self.audio_system, self.audio_system)
        
        try:
            # 원본 캐릭터 백업 (불사 모드용)
            original_party = []
            for member in self.training_party:
                backup = deepcopy(member)
                original_party.append(backup)
            
            # 전투 실행
            result = combat_system.start_battle(self.training_party, self.custom_enemies)
            
            # 결과 처리
            if result:
                print(f"\n{bright_green('🎉 훌륭합니다! 트레이닝 전투에서 승리했습니다!')}")
                print("💪 실력이 향상되었습니다!")
            else:
                print(f"\n{bright_blue('💙 패배했지만 좋은 경험이었습니다!')}")
                print("🎯 다시 도전해보세요!")
            
            # 트레이닝 전투 후 불사 모드 적용 - 모든 파티원 부활 및 완전 회복
            print(f"\n{bright_cyan('✨ 불사 모드 발동 - 모든 파티원이 완전 회복됩니다!')}")
            for i, member in enumerate(self.training_party):
                if not member.is_alive:
                    member.current_hp = 1  # 전투불능 상태였다면 HP 1로 부활
                    member.is_alive = True
                    print(f"⚡ {member.name}이(가) 부활했습니다!")
                
                # 완전 회복
                member.current_hp = member.max_hp
                member.current_mp = member.max_mp
                member.brave_points = getattr(member, 'int_brv', 500)
                
                # 상태이상 모두 제거
                if hasattr(member, 'status_manager'):
                    member.status_manager.clear_all_effects()
            
            print(f"{bright_green('🌟 모든 파티원이 완전한 상태로 회복되었습니다!')}")
            
        except Exception as e:
            print(f"\n{bright_red(f'❌ 전투 중 오류가 발생했습니다: {e}')}")
            print("트레이닝 룸으로 돌아갑니다.")
            
            # 오류 발생 시에도 불사 모드 적용
            print(f"\n{bright_cyan('✨ 불사 모드 발동 - 모든 파티원 완전 회복!')}")
            for member in self.training_party:
                member.current_hp = member.max_hp
                member.current_mp = member.max_mp
                member.is_alive = True
                if hasattr(member, 'status_manager'):
                    member.status_manager.clear_all_effects()
        
        input("계속하려면 Enter를 누르세요...")
    
    def _distribute_unlimited_items(self):
        """무제한 아이템 지급"""
        
        if not self.training_party:
            print(f"\n{bright_red('❌ 먼저 파티를 구성해주세요!')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        print(f"\n{bright_green('🎒 무제한 아이템 지급')}")
        print("="*50)
        
        for member in self.training_party:
            print(f"\n👤 {member.name}에게 아이템 지급 중...")
            
            # 인벤토리가 없으면 생성
            if not hasattr(member, 'inventory'):
                from .items import Inventory
                member.inventory = Inventory()
            
            # 무제한 아이템 추가
            for item_name, item_data in self.unlimited_items.items():
                try:
                    member.inventory.add_item(item_name, item_data["quantity"])
                    print(f"  ✅ {item_name} x{item_data['quantity']}")
                except Exception as e:
                    print(f"  ❌ {item_name} 지급 실패: {e}")
            
            # 추가 골드 지급
            if hasattr(member, 'gold'):
                member.gold += 100000
                print(f"  💰 골드 +100,000 (총: {member.gold:,})")
        
        print(f"\n{bright_green('✅ 모든 파티원에게 무제한 아이템이 지급되었습니다!')}")
        input("계속하려면 Enter를 누르세요...")
    
    def _show_party_status(self):
        """파티 상태 확인"""
        
        if not self.training_party:
            print(f"\n{bright_red('❌ 구성된 파티가 없습니다!')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        print(f"\n{bright_cyan('📊 트레이닝 파티 상태')}")
        print("="*80)
        
        for i, member in enumerate(self.training_party):
            print(f"\n👤 {i+1}. {member.name} (Lv.{member.level}) - {member.character_class}")
            print(f"   ❤️  HP: {member.current_hp:,}/{member.max_hp:,}")
            print(f"   💙 MP: {member.current_mp:,}/{member.max_mp:,}")
            
            if hasattr(member, 'brave_points'):
                print(f"   ⚡ BRV: {member.brave_points:,}/{getattr(member, 'max_brv', 9999):,}")
            
            print(f"   ⚔️  ATK: {member.physical_attack:,} | 🛡️  DEF: {member.physical_defense:,}")
            print(f"   🔮 M.ATK: {member.magical_attack:,} | 🌟 M.DEF: {member.magical_defense:,}")
            print(f"   💨 SPD: {member.speed:,}")
            
            if hasattr(member, 'gold'):
                print(f"   💰 골드: {member.gold:,}")
            
            # 장비 정보
            if hasattr(member, 'equipment'):
                equipped_items = []
                for slot, item in member.equipment.items():
                    if item:
                        equipped_items.append(f"{slot}: {item.name}")
                if equipped_items:
                    print(f"   🎽 장비: {', '.join(equipped_items)}")
        
        print("="*80)
        input("계속하려면 Enter를 누르세요...")
    
    def _save_training_setup(self):
        """트레이닝 설정 저장 - 비활성화됨"""
        
        print(f"\n{bright_yellow('⚠️ 트레이닝 룸에서는 세이브 기능이 비활성화되어 있습니다.')}")
        print("이곳은 연습용 특별한 공간으로, 별도의 세이브 파일을 생성하지 않습니다.")
        print("트레이닝 중인 내용은 메인 게임에 영향을 주지 않습니다.")
        input("계속하려면 Enter를 누르세요...")
    
    def _load_training_setup(self):
        """트레이닝 설정 로드 - 비활성화됨"""
        
        print(f"\n{bright_yellow('⚠️ 트레이닝 룸에서는 로드 기능이 비활성화되어 있습니다.')}")
        print("이곳은 연습용 특별한 공간으로, 별도의 세이브 파일을 사용하지 않습니다.")
        print("매번 새로운 트레이닝 환경에서 시작하세요!")
        input("계속하려면 Enter를 누르세요...")


# 전역 트레이닝 룸 인스턴스
training_room = None

def get_training_room(audio_system=None, keyboard=None):
    """트레이닝 룸 인스턴스 반환"""
    global training_room
    if training_room is None:
        training_room = TrainingRoom(audio_system, keyboard)
    return training_room
