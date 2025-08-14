"""
🏟️ 배틀그라운드 트레이닝 센터
- 세이브 불가능한 실험 전용 공간
- 사각형 방들이 연결된 맵 구조
- 무제한 리소스로 자유로운 테스트
- 오토 파티 빌더, 기존 파티 복사, 수동 캐릭터 생성 기능 제거
"""
import os
import time
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from game.character import Character
from game.cursor_menu_system import create_simple_menu
from game.color_text import *
from copy import deepcopy

def clear_screen():
    """화면 클리어"""
    os.system('cls' if os.name == 'nt' else 'clear')

class BattlegroundTrainingCenter:
    """배틀그라운드 연습장 - 실험과 테스트를 위한 특별한 공간"""
    
    def __init__(self, audio_system=None, keyboard=None):
        self.audio_system = audio_system
        self.keyboard = keyboard
        self.training_party = []
        self.current_room = "central_hub"
        self.experiment_log = []
        self.is_training_space = True
        
        # 맵 구조 초기화
        self.room_map = self._create_room_map()
        
    def _create_room_map(self) -> Dict:
        """사각형 방들이 연결된 맵 구조 생성"""
        return {
            # 중앙 허브 (3x3 그리드의 중심)
            "central_hub": {
                "name": "🏛️ 중앙 허브",
                "description": "모든 훈련 시설의 중심지입니다.",
                "connections": ["north_wing", "east_wing", "south_wing", "west_wing"],
                "features": ["💺 휴식 공간", "🗺️ 안내판", "📊 실험 로그"],
                "npcs": ["📋 훈련 가이드"]
            },
            
            # 북쪽 구역 (전투 관련)
            "north_wing": {
                "name": "⚔️ 전투 훈련 구역",
                "description": "실전 전투 연습을 위한 공간입니다.",
                "connections": ["central_hub", "combat_simulator", "skill_practice"],
                "features": ["🎯 타겟 연습장", "🛡️ 방어 훈련기"],
                "npcs": ["⚔️ 전투 교관"]
            },
            
            "combat_simulator": {
                "name": "🤖 전투 시뮬레이터",
                "description": "다양한 적과 안전하게 전투할 수 있습니다.",
                "connections": ["north_wing"],
                "features": ["💻 시뮬레이터", "📈 전투 분석기"],
                "npcs": ["🤖 시뮬레이터 조작사"]
            },
            
            "skill_practice": {
                "name": "🎯 스킬 연습장",
                "description": "무제한 MP로 스킬을 테스트할 수 있습니다.",
                "connections": ["north_wing"],
                "features": ["⚡ MP 충전소", "📚 스킬 라이브러리"],
                "npcs": ["🧙‍♂️ 스킬 마스터"]
            },
            
            # 동쪽 구역 (능력치 관련)
            "east_wing": {
                "name": "📊 능력치 연구소",
                "description": "캐릭터 능력치를 자유롭게 조정할 수 있습니다.",
                "connections": ["central_hub", "stat_lab", "level_booster"],
                "features": ["🔬 분석 장비", "📈 그래프 모니터"],
                "npcs": ["🧬 연구원"]
            },
            
            "stat_lab": {
                "name": "🔬 스탯 실험실",
                "description": "실시간으로 능력치를 변경하고 테스트할 수 있습니다.",
                "connections": ["east_wing"],
                "features": ["⚙️ 스탯 조정기", "🧮 계산기"],
                "npcs": ["👨‍🔬 스탯 박사"]
            },
            
            "level_booster": {
                "name": "⭐ 레벨 조정실",
                "description": "캐릭터 레벨을 자유롭게 설정할 수 있습니다.",
                "connections": ["east_wing"],
                "features": ["🌟 경험치 증폭기", "⏰ 시간 조절기"],
                "npcs": ["✨ 레벨 마법사"]
            },
            
            # 남쪽 구역 (아이템 관련)
            "south_wing": {
                "name": "🎒 장비 테스트 구역",
                "description": "모든 장비와 아이템을 자유롭게 테스트할 수 있습니다.",
                "connections": ["central_hub", "item_warehouse", "equipment_forge"],
                "features": ["🏺 진열대", "⚖️ 성능 측정기"],
                "npcs": ["🔨 장비 기술자"]
            },
            
            "item_warehouse": {
                "name": "📦 무제한 창고",
                "description": "게임 내 모든 아이템을 무제한으로 사용할 수 있습니다.",
                "connections": ["south_wing"],
                "features": ["📚 아이템 카탈로그", "🎁 무제한 상자"],
                "npcs": ["📦 창고 관리인"]
            },
            
            "equipment_forge": {
                "name": "⚒️ 장비 실험실",
                "description": "다양한 장비 조합을 테스트할 수 있습니다.",
                "connections": ["south_wing"],
                "features": ["🔥 실험용 용광로", "🛠️ 조합 테이블"],
                "npcs": ["👨‍🔧 장비 연구원"]
            },
            
            # 서쪽 구역 (특수 기능)
            "west_wing": {
                "name": "🔮 특수 실험 구역",
                "description": "특별한 기능들을 테스트할 수 있습니다.",
                "connections": ["central_hub", "brv_lab", "scenario_room"],
                "features": ["🎪 실험 장치", "🎭 시나리오 생성기"],
                "npcs": ["🔮 실험 마법사"]
            },
            
            "brv_lab": {
                "name": "💎 BRV 연구소",
                "description": "BRV 시스템을 깊이 있게 연구할 수 있습니다.",
                "connections": ["west_wing"],
                "features": ["🧪 BRV 실험기", "📋 연구 노트"],
                "npcs": ["👨‍🔬 BRV 박사"]
            },
            
            "scenario_room": {
                "name": "🎭 시나리오 테스트실",
                "description": "다양한 전투 상황을 시뮬레이션할 수 있습니다.",
                "connections": ["west_wing"],
                "features": ["🎬 시나리오 생성기", "🏆 챌린지 보드"],
                "npcs": ["🎪 시나리오 디렉터"]
            }
        }
    
    def start_training(self):
        """트레이닝 센터 시작"""
        clear_screen()
        self._show_welcome_message()
        
        # 세이브 파일 로드
        if not self._load_from_save():
            return
        
        # 메인 루프
        while True:
            try:
                self._show_current_room()
                action = self._get_room_actions()
                
                if action == "exit":
                    break
                elif action == "move":
                    self._move_to_room()
                elif action == "interact":
                    self._interact_with_room()
                elif action == "party":
                    self._show_party_status()
                elif action == "map":
                    self._show_full_map()
                elif action == "log":
                    self._show_experiment_log()
                    
            except KeyboardInterrupt:
                print(f"\n{bright_yellow('트레이닝 센터를 나갑니다...')}")
                break
        
        self._show_exit_message()
    
    def _show_welcome_message(self):
        """환영 메시지"""
        print(f"{bright_cyan('🏟️ 배틀그라운드 트레이닝 센터에 오신 것을 환영합니다!')}")
        print("="*70)
        print(f"{bright_yellow('📍 특별한 공간 안내:')}")
        print("   🚫 세이브 불가능 - 모든 변경사항은 임시적입니다")
        print("   ♾️  무제한 리소스 - 자유로운 실험이 가능합니다")
        print("   🔄 안전한 환경 - 실패해도 페널티가 없습니다")
        print("   🗺️ 연결된 방들 - 사각형 구조로 이동 가능합니다")
        print()
        print(f"{bright_green('🎯 이곳에서 할 수 있는 것:')}")
        print("   ⚔️ 무제한 전투 연습")
        print("   📊 실시간 능력치 조정")
        print("   🎒 모든 장비 테스트")
        print("   💎 BRV 시스템 연구")
        print("   🎭 다양한 시나리오 실험")
        print()
        input("계속하려면 Enter를 누르세요...")
    
    def _load_from_save(self) -> bool:
        """세이브 파일에서 파티 로드"""
        clear_screen()
        print(f"{bright_cyan('💾 세이브 파일 로드')}")
        print("="*40)
        print("트레이닝에 사용할 파티를 세이브 파일에서 불러옵니다.")
        print(f"{bright_yellow('⚠️ 원본 세이브 파일은 변경되지 않습니다.')}")
        print()
        
        try:
            from game.save_system import SaveSystem
            save_system = SaveSystem()
            
            # 세이브 파일 목록 (개선된 list_saves 사용)
            save_list = save_system.list_saves()
            if not save_list:
                print(f"{bright_red('❌ 세이브 파일이 없습니다.')}")
                print("메인 게임에서 먼저 플레이해주세요.")
                input("계속하려면 Enter를 누르세요...")
                return False
            
            # 세이브 파일 선택 메뉴
            save_options = []
            save_descriptions = []
            
            for save_info in save_list:
                filename = save_info.get('filename', '알 수 없음')
                save_name = save_info.get('save_name', filename)
                save_time = save_info.get('save_time', '알 수 없음')
                level = save_info.get('level', '?')
                party_names = save_info.get('party_names', [])
                
                # 시간 형식 개선
                if save_time != '알 수 없음' and isinstance(save_time, str):
                    try:
                        # ISO 형식을 사용자 친화적으로 변환
                        if 'T' in save_time:
                            dt = datetime.fromisoformat(save_time.replace('Z', '+00:00'))
                            save_time = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                # 파티 정보 구성
                if party_names:
                    party_info = f"{party_names[0]} Lv.{level} (파티 {len(party_names)}명)"
                else:
                    party_info = f"Lv.{level} (파티 정보 불완전)"
                
                save_options.append(f"💾 {save_name}")
                save_descriptions.append(f"{party_info} - {save_time}")
            
            save_menu = create_simple_menu(
                "로드할 세이브 파일 선택",
                save_options,
                save_descriptions,
                clear_screen=True
            )
            
            choice = save_menu.run()
            if choice is None or choice < 0:
                return False
            
            # 세이브 파일 로드
            selected_save = save_list[choice]['filename']
            print(f"\n{bright_cyan(f'💾 {selected_save} 로딩 중...')}")
            
            loaded_data = save_system.load_game(selected_save)
            if not loaded_data:
                print(f"{bright_red('❌ 세이브 파일 로드 실패')}")
                input("계속하려면 Enter를 누르세요...")
                return False
            
            # 파티 데이터 복사 - 두 가지 키 모두 확인
            party_data = loaded_data.get('party_characters', loaded_data.get('party', []))
            if not party_data:
                print(f"{bright_red('❌ 파티 데이터가 없습니다.')}")
                input("계속하려면 Enter를 누르세요...")
                return False
            self.training_party = []
            
            if isinstance(party_data, list):
                for char_data in party_data:
                    if isinstance(char_data, dict):
                        # Character.from_dict 안전하게 사용
                        try:
                            if hasattr(Character, 'from_dict'):
                                char = Character.from_dict(char_data)
                            else:
                                # from_dict 메서드가 없는 경우 수동 생성
                                char = Character(
                                    name=char_data.get('name', '알 수 없는 캐릭터'),
                                    character_class=char_data.get('character_class', '전사'),
                                    max_hp=char_data.get('max_hp', 100),
                                    physical_attack=char_data.get('physical_attack', 10),
                                    magic_attack=char_data.get('magic_attack', 10),
                                    physical_defense=char_data.get('physical_defense', 10),
                                    magic_defense=char_data.get('magic_defense', 10),
                                    speed=char_data.get('speed', 10)
                                )
                                char.current_hp = char_data.get('current_hp', char.max_hp)
                                char.current_mp = char_data.get('current_mp', char.max_mp)
                                char.level = char_data.get('level', 1)
                                char.experience = char_data.get('experience', 0)
                        except Exception as e:
                            print(f"{bright_red('⚠️ 캐릭터 복원 실패:')} {e}")
                            continue
                    else:
                        char = deepcopy(char_data)
                    
                    # 트레이닝 모드 설정
                    char.is_training_mode = True
                    char.current_hp = char.max_hp
                    char.current_mp = char.max_mp
                    
                    if hasattr(char, 'int_brv'):
                        char.brave_points = char.int_brv
                    
                    self.training_party.append(char)
            
            if not self.training_party:
                print(f"{bright_red('❌ 유효한 캐릭터가 없습니다.')}")
                input("계속하려면 Enter를 누르세요...")
                return False
            
            print(f"{bright_green('✅ 파티 로드 완료!')}")
            print(f"로드된 멤버: {len(self.training_party)}명")
            for char in self.training_party:
                print(f"  - {char.name} (Lv.{char.level} {char.character_class})")
            
            input("\n계속하려면 Enter를 누르세요...")
            return True
            
        except Exception as e:
            print(f"{bright_red(f'❌ 로드 중 오류: {e}')}")
            input("계속하려면 Enter를 누르세요...")
            return False
    
    def _show_current_room(self):
        """현재 방 정보 표시"""
        clear_screen()
        room = self.room_map[self.current_room]
        
        print(f"{room['name']}")
        print("="*60)
        print(f"{room['description']}")
        print()
        
        # 연결된 방들
        if room['connections']:
            print(f"{bright_yellow('🚪 연결된 곳:')}")
            for connection in room['connections']:
                connected_room = self.room_map[connection]
                print(f"  → {connected_room['name']}")
            print()
        
        # 특수 기능들
        if room['features']:
            print(f"{bright_blue('🎯 이용 가능한 기능:')}")
            for feature in room['features']:
                print(f"  {feature}")
            print()
        
        # NPC들
        if room['npcs']:
            print(f"{bright_green('👥 등장인물:')}")
            for npc in room['npcs']:
                print(f"  {npc}")
            print()
    
    def _get_room_actions(self) -> str:
        """방에서 할 수 있는 행동들"""
        actions = [
            "🚶 다른 방으로 이동",
            "🎯 방 기능 사용",
            "👥 파티 상태 확인",
            "🗺️ 전체 맵 보기",
            "📊 실험 로그 확인",
            "🚪 센터 나가기"
        ]
        
        descriptions = [
            "연결된 다른 방으로 이동합니다",
            "현재 방의 특별한 기능을 사용합니다",
            "트레이닝 파티의 상태를 확인합니다",
            "트레이닝 센터의 전체 맵을 확인합니다",
            "지금까지의 실험 기록을 확인합니다",
            "트레이닝 센터를 나가고 메인 게임으로 돌아갑니다"
        ]
        
        action_menu = create_simple_menu(
            f"{self.room_map[self.current_room]['name']} - 행동 선택",
            actions,
            descriptions,
            clear_screen=False
        )
        
        choice = action_menu.run()
        if choice is None or choice < 0:
            return "exit"
        elif choice == 0:
            return "move"
        elif choice == 1:
            return "interact"
        elif choice == 2:
            return "party"
        elif choice == 3:
            return "map"
        elif choice == 4:
            return "log"
        else:
            return "exit"
    
    def _move_to_room(self):
        """다른 방으로 이동"""
        room = self.room_map[self.current_room]
        
        if not room['connections']:
            print(f"{bright_yellow('이동할 수 있는 곳이 없습니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        # 이동 가능한 방들
        move_options = []
        move_descriptions = []
        
        for connection in room['connections']:
            connected_room = self.room_map[connection]
            move_options.append(connected_room['name'])
            move_descriptions.append(connected_room['description'])
        
        move_menu = create_simple_menu(
            "이동할 곳 선택",
            move_options,
            move_descriptions,
            clear_screen=True
        )
        
        choice = move_menu.run()
        if choice is not None and choice >= 0:
            old_room = self.current_room
            self.current_room = room['connections'][choice]
            new_room = self.room_map[self.current_room]
            
            print(f"{bright_cyan(new_room['name'] + '(으)로 이동했습니다!')}")
            self.experiment_log.append(f"방 이동: {self.room_map[old_room]['name']} → {new_room['name']}")
            time.sleep(1)
    
    def _interact_with_room(self):
        """현재 방의 기능 사용"""
        room_functions = {
            "central_hub": self._central_hub_functions,
            "north_wing": self._north_wing_functions,
            "combat_simulator": self._combat_simulator_functions,
            "skill_practice": self._skill_practice_functions,
            "east_wing": self._east_wing_functions,
            "stat_lab": self._stat_lab_functions,
            "level_booster": self._level_booster_functions,
            "south_wing": self._south_wing_functions,
            "item_warehouse": self._item_warehouse_functions,
            "equipment_forge": self._equipment_forge_functions,
            "west_wing": self._west_wing_functions,
            "brv_lab": self._brv_lab_functions,
            "scenario_room": self._scenario_room_functions
        }
        
        if self.current_room in room_functions:
            room_functions[self.current_room]()
        else:
            print(f"{bright_yellow('이 방의 기능은 아직 개발 중입니다.')}")
            input("계속하려면 Enter를 누르세요...")
    
    def _show_party_status(self):
        """파티 상태 확인"""
        clear_screen()
        print(f"{bright_cyan('👥 트레이닝 파티 상태')}")
        print("="*50)
        
        if not self.training_party:
            print(f"{bright_yellow('파티에 멤버가 없습니다.')}")
        else:
            for i, char in enumerate(self.training_party, 1):
                print(f"\n{i}. {bright_green(char.name)} (Lv.{char.level} {char.character_class})")
                print(f"   💚 체력: {char.current_hp}/{char.max_hp}")
                print(f"   💙 마나: {char.current_mp}/{char.max_mp}")
                
                if hasattr(char, 'brave_points'):
                    print(f"   💎 BRV: {char.brave_points}")
                
                if hasattr(char, 'is_training_mode') and char.is_training_mode:
                    print(f"   🏟️ {bright_cyan('트레이닝 모드 활성')}")
        
        input("\n계속하려면 Enter를 누르세요...")
    
    def _show_full_map(self):
        """전체 맵 보기"""
        clear_screen()
        print(f"{bright_cyan('🗺️ 배틀그라운드 트레이닝 센터 맵')}")
        print("="*60)
        print()
        print("   🎯 스킬 연습장    ⚔️ 전투 훈련 구역    🤖 전투 시뮬레이터")
        print("        │                  │                  │")
        print("   📊 능력치 연구소  ──  🏛️ 중앙 허브  ──  🔬 스탯 실험실")
        print("        │                  │                  │")
        print("   🎒 장비 테스트 구역    🔮 특수 실험 구역    ⭐ 레벨 조정실")
        print()
        print("   📦 창고    ⚒️ 실험실    💎 BRV 연구소    🎭 시나리오실")
        print()
        print(f"현재 위치: {bright_yellow(self.room_map[self.current_room]['name'])}")
        print()
        
        # 각 구역 설명
        print(f"{bright_green('구역별 기능:')}")
        for room_id, room_info in self.room_map.items():
            if room_id == self.current_room:
                print(f"  👉 {bright_yellow(room_info['name'])}: {room_info['description']}")
            else:
                print(f"     {room_info['name']}: {room_info['description']}")
        
        input("\n계속하려면 Enter를 누르세요...")
    
    def _show_experiment_log(self):
        """실험 로그 확인"""
        clear_screen()
        print(f"{bright_cyan('📊 실험 로그')}")
        print("="*40)
        
        if not self.experiment_log:
            print(f"{bright_yellow('아직 기록된 실험이 없습니다.')}")
        else:
            for i, log in enumerate(self.experiment_log, 1):
                print(f"{i:2d}. {log}")
        
        input("\n계속하려면 Enter를 누르세요...")
    
    def _show_exit_message(self):
        """나가기 메시지"""
        clear_screen()
        print(f"{bright_cyan('🏟️ 배틀그라운드 트레이닝 센터를 나갑니다')}")
        print("="*50)
        print(f"{bright_yellow('📝 실험 요약:')}")
        print(f"   총 실험 횟수: {len(self.experiment_log)}회")
        print(f"   방문한 방: {len(set(log.split(' → ')[0] for log in self.experiment_log if ' → ' in log))}개")
        print()
        print(f"{bright_green('✨ 모든 실험 데이터는 초기화됩니다.')}")
        print("   트레이닝에서의 모든 변경사항은 저장되지 않았습니다.")
        print("   실제 게임에는 영향을 주지 않습니다.")
        print()
        print(f"{bright_cyan('🎯 실험해보신 내용들이 실제 게임에 도움이 되길 바랍니다!')}")
        input("\n계속하려면 Enter를 누르세요...")
    
    # ================ 각 방별 기능들 (개발 중) ================
    
    def _central_hub_functions(self):
        """중앙 허브 기능들"""
        functions = [
            "💺 전체 휴식 (완전 회복)",
            "🗺️ 안내판 보기",
            "📊 실험 통계 확인"
        ]
        
        descriptions = [
            "모든 파티원의 HP/MP/BRV를 완전히 회복합니다",
            "트레이닝 센터의 모든 시설 정보를 확인합니다",
            "지금까지의 실험 진행상황을 확인합니다"
        ]
        
        function_menu = create_simple_menu(
            "🏛️ 중앙 허브 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._full_recovery()
        elif choice == 1:
            self._show_full_map()
        elif choice == 2:
            self._show_experiment_log()
    
    def _full_recovery(self):
        """전체 회복"""
        if not self.training_party:
            print(f"{bright_yellow('회복할 파티원이 없습니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        print(f"{bright_green('✨ 휴식을 취합니다...')}")
        for char in self.training_party:
            char.current_hp = char.max_hp
            char.current_mp = char.max_mp
            if hasattr(char, 'int_brv'):
                char.brave_points = char.int_brv
        
        print(f"{bright_cyan('🌟 모든 파티원이 완전히 회복되었습니다!')}")
        self.experiment_log.append("전체 회복 사용")
        input("계속하려면 Enter를 누르세요...")
    
    # 북쪽 구역 기능들
    def _north_wing_functions(self):
        """⚔️ 전투 훈련 구역 기능들"""
        functions = [
            "🎯 타겟 연습",
            "🛡️ 방어 훈련",
            "⚔️ 기본 공격 연습",
            "🏃 민첩성 훈련"
        ]
        
        descriptions = [
            "정확도를 높이는 타겟 연습을 합니다",
            "방어력과 회피율을 향상시킵니다",
            "기본 공격의 위력을 증가시킵니다",
            "행동 속도를 향상시킵니다"
        ]
        
        function_menu = create_simple_menu(
            "⚔️ 전투 훈련 구역 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._target_practice()
        elif choice == 1:
            self._defense_training()
        elif choice == 2:
            self._attack_training()
        elif choice == 3:
            self._agility_training()
    
    def _target_practice(self):
        """타겟 연습"""
        char = self._select_character()
        if not char:
            return
        
        print(f"{bright_cyan('🎯 타겟 연습을 시작합니다...')}")
        print(f"{char.name}이(가) 집중해서 타겟을 조준합니다.")
        
        # 정확도 일시적 증가 효과
        accuracy_boost = 20
        print(f"{bright_green(f'✅ 정확도가 일시적으로 +{accuracy_boost} 증가했습니다!')}")
        print("실전에서 명중률이 향상될 것입니다.")
        
        self.experiment_log.append(f"{char.name} 타겟 연습 완료 (정확도 +{accuracy_boost})")
        input("계속하려면 Enter를 누르세요...")
    
    def _defense_training(self):
        """방어 훈련"""
        char = self._select_character()
        if not char:
            return
        
        print(f"{bright_cyan('🛡️ 방어 훈련을 시작합니다...')}")
        print(f"{char.name}이(가) 방어 자세를 연습합니다.")
        
        # 방어력 일시적 증가 효과
        defense_boost = 15
        print(f"{bright_green(f'✅ 방어력이 일시적으로 +{defense_boost} 증가했습니다!')}")
        print("적의 공격을 더 잘 막아낼 수 있습니다.")
        
        self.experiment_log.append(f"{char.name} 방어 훈련 완료 (방어력 +{defense_boost})")
        input("계속하려면 Enter를 누르세요...")
    
    def _attack_training(self):
        """공격 훈련"""
        char = self._select_character()
        if not char:
            return
        
        print(f"{bright_cyan('⚔️ 기본 공격 연습을 시작합니다...')}")
        print(f"{char.name}이(가) 공격 기술을 연마합니다.")
        
        # 공격력 일시적 증가 효과
        attack_boost = 25
        print(f"{bright_green(f'✅ 공격력이 일시적으로 +{attack_boost} 증가했습니다!')}")
        print("더 강력한 공격을 할 수 있습니다.")
        
        self.experiment_log.append(f"{char.name} 공격 훈련 완료 (공격력 +{attack_boost})")
        input("계속하려면 Enter를 누르세요...")
    
    def _agility_training(self):
        """민첩성 훈련"""
        char = self._select_character()
        if not char:
            return
        
        print(f"{bright_cyan('🏃 민첩성 훈련을 시작합니다...')}")
        print(f"{char.name}이(가) 빠른 움직임을 연습합니다.")
        
        # 속도 일시적 증가 효과
        speed_boost = 30
        print(f"{bright_green(f'✅ 속도가 일시적으로 +{speed_boost} 증가했습니다!')}")
        print("전투에서 더 빨리 행동할 수 있습니다.")
        
        self.experiment_log.append(f"{char.name} 민첩성 훈련 완료 (속도 +{speed_boost})")
        input("계속하려면 Enter를 누르세요...")
    
    def _combat_simulator_functions(self):
        """🤖 전투 시뮬레이터 기능들"""
        functions = [
            "🤖 AI 적과 전투",
            "👹 보스 전투 시뮬레이션",
            "👥 파티 전투 연습",
            "📊 전투 통계 분석"
        ]
        
        descriptions = [
            "다양한 AI 적과 안전한 전투를 진행합니다",
            "강력한 보스와의 전투를 시뮬레이션합니다",
            "파티원들과 협동 전투를 연습합니다",
            "전투 패턴과 성과를 분석합니다"
        ]
        
        function_menu = create_simple_menu(
            "🤖 전투 시뮬레이터 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._ai_battle_simulation()
        elif choice == 1:
            self._boss_battle_simulation()
        elif choice == 2:
            self._party_battle_practice()
        elif choice == 3:
            self._battle_statistics()
    
    def _ai_battle_simulation(self):
        """AI 적과 전투 시뮬레이션"""
        enemies = ["슬라임", "고블린", "오크", "스켈레톤", "드래곤"]
        enemy_menu = create_simple_menu(
            "상대할 적 선택",
            enemies,
            [f"{enemy}와 안전한 모의 전투를 진행합니다" for enemy in enemies],
            clear_screen=True
        )
        
        choice = enemy_menu.run()
        if choice is None or choice < 0:
            return
        
        enemy = enemies[choice]
        print(f"{bright_cyan(f'🤖 {enemy}와의 모의 전투를 시작합니다!')}")
        print("=== 전투 시뮬레이션 ===")
        
        for i in range(3):
            print(f"라운드 {i+1}: {enemy}이(가) 공격합니다!")
            time.sleep(0.5)
            print(f"라운드 {i+1}: 반격합니다!")
            time.sleep(0.5)
        
        print(f"{bright_green('✅ 모의 전투 완료! 실제 피해는 없습니다.')}")
        self.experiment_log.append(f"AI 전투 시뮬레이션: {enemy} 상대")
        input("계속하려면 Enter를 누르세요...")
    
    def _boss_battle_simulation(self):
        """보스 전투 시뮬레이션"""
        bosses = ["고블린 킹", "드래곤 로드", "리치", "발록", "최종 보스"]
        boss_menu = create_simple_menu(
            "도전할 보스 선택",
            bosses,
            [f"{boss}와의 고난도 모의 전투입니다" for boss in bosses],
            clear_screen=True
        )
        
        choice = boss_menu.run()
        if choice is None or choice < 0:
            return
        
        boss = bosses[choice]
        print(f"{bright_red(f'👹 {boss}와의 보스 전투 시뮬레이션!')}")
        print("=== 보스 전투 시뮬레이션 ===")
        
        for i in range(5):
            print(f"페이즈 {i+1}: {boss}의 강력한 공격!")
            time.sleep(0.7)
            print(f"페이즈 {i+1}: 파티 전체 공격!")
            time.sleep(0.7)
        
        print(f"{bright_cyan('🏆 보스 전투 시뮬레이션 완료!')}")
        print("실제 보스전에서 도움이 될 전략을 얻었습니다.")
        
        self.experiment_log.append(f"보스 전투 시뮬레이션: {boss}")
        input("계속하려면 Enter를 누르세요...")
    
    def _party_battle_practice(self):
        """파티 전투 연습"""
        if len(self.training_party) < 2:
            print(f"{bright_yellow('파티 전투 연습은 최소 2명의 멤버가 필요합니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        print(f"{bright_cyan('👥 파티 협동 전투 연습을 시작합니다!')}")
        print(f"참여 멤버: {len(self.training_party)}명")
        
        for char in self.training_party:
            print(f"  - {char.name} (Lv.{char.level} {char.character_class})")
        
        print("\n=== 협동 전투 시뮬레이션 ===")
        for i, char in enumerate(self.training_party):
            print(f"{char.name}이(가) 스킬을 사용합니다!")
            time.sleep(0.5)
        
        print(f"{bright_green('✅ 파티 협동 전투 연습 완료!')}")
        print("팀워크가 향상되었습니다.")
        
        self.experiment_log.append(f"파티 전투 연습 ({len(self.training_party)}명 참여)")
        input("계속하려면 Enter를 누르세요...")
    
    def _battle_statistics(self):
        """전투 통계 분석"""
        print(f"{bright_cyan('📊 전투 통계 분석')}")
        print("="*40)
        
        battle_logs = [log for log in self.experiment_log if '전투' in log or '시뮬레이션' in log]
        
        if not battle_logs:
            print(f"{bright_yellow('아직 전투 기록이 없습니다.')}")
        else:
            print(f"총 전투 횟수: {len(battle_logs)}회")
            print("\n전투 기록:")
            for i, log in enumerate(battle_logs, 1):
                print(f"{i:2d}. {log}")
        
        # 파티 전투력 분석
        if self.training_party:
            print(f"\n{bright_green('파티 전투력 분석:')}")
            total_level = sum(char.level for char in self.training_party)
            avg_level = total_level / len(self.training_party)
            print(f"평균 레벨: {avg_level:.1f}")
            print(f"총 HP: {sum(char.max_hp for char in self.training_party)}")
            print(f"총 MP: {sum(char.max_mp for char in self.training_party)}")
        
        input("계속하려면 Enter를 누르세요...")
    
    def _skill_practice_functions(self):
        """🎯 스킬 연습장 기능들"""
        functions = [
            "⚡ MP 무제한 모드",
            "🎯 스킬 데미지 테스트",
            "🔄 쿨다운 무시 모드",
            "📚 새로운 스킬 배우기"
        ]
        
        descriptions = [
            "MP 소모 없이 자유롭게 스킬을 사용합니다",
            "다양한 스킬의 데미지를 측정합니다",
            "쿨다운 없이 연속으로 스킬을 사용합니다",
            "다른 직업의 스킬을 임시로 배웁니다"
        ]
        
        function_menu = create_simple_menu(
            "🎯 스킬 연습장 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._unlimited_mp_mode()
        elif choice == 1:
            self._skill_damage_test()
        elif choice == 2:
            self._no_cooldown_mode()
        elif choice == 3:
            self._learn_new_skills()
    
    def _unlimited_mp_mode(self):
        """무제한 MP 모드"""
        char = self._select_character()
        if not char:
            return
        
        print(f"{bright_cyan('⚡ 무제한 MP 모드 활성화!')}")
        print(f"{char.name}의 MP가 무제한이 됩니다.")
        
        # MP를 최대치로 고정
        char.current_mp = char.max_mp * 10  # 매우 높은 값으로 설정
        
        print(f"{bright_green('✨ MP 무제한 상태가 되었습니다!')}")
        print("이제 MP 걱정 없이 모든 스킬을 사용할 수 있습니다.")
        
        self.experiment_log.append(f"{char.name} 무제한 MP 모드 활성화")
        input("계속하려면 Enter를 누르세요...")
    
    def _skill_damage_test(self):
        """스킬 데미지 테스트"""
        char = self._select_character()
        if not char:
            return
        
        print(f"{bright_cyan('🎯 스킬 데미지 테스트 시작!')}")
        print(f"{char.name}의 스킬들을 테스트합니다.")
        
        # 가상의 스킬 데미지 계산
        skills = ["기본 공격", "특수 스킬", "궁극기"]
        for skill in skills:
            damage = 100 + char.level * 20
            print(f"{skill}: 예상 데미지 {damage}")
            time.sleep(0.3)
        
        print(f"{bright_green('✅ 스킬 데미지 테스트 완료!')}")
        print("최적의 스킬 조합을 확인했습니다.")
        
        self.experiment_log.append(f"{char.name} 스킬 데미지 테스트")
        input("계속하려면 Enter를 누르세요...")
    
    def _no_cooldown_mode(self):
        """쿨다운 무시 모드"""
        char = self._select_character()
        if not char:
            return
        
        print(f"{bright_cyan('🔄 쿨다운 무시 모드 활성화!')}")
        print(f"{char.name}이(가) 연속으로 스킬을 사용할 수 있습니다.")
        
        print(f"{bright_green('⚡ 모든 스킬의 쿨다운이 제거되었습니다!')}")
        print("원하는 만큼 스킬을 연속 사용해보세요.")
        
        self.experiment_log.append(f"{char.name} 쿨다운 무시 모드 활성화")
        input("계속하려면 Enter를 누르세요...")
    
    def _learn_new_skills(self):
        """새로운 스킬 배우기"""
        char = self._select_character()
        if not char:
            return
        
        new_skills = ["화염구", "치유의 빛", "번개 창", "방어막", "순간이동"]
        skill_menu = create_simple_menu(
            "배울 스킬 선택",
            new_skills,
            [f"임시로 {skill} 스킬을 배웁니다" for skill in new_skills],
            clear_screen=True
        )
        
        choice = skill_menu.run()
        if choice is None or choice < 0:
            return
        
        learned_skill = new_skills[choice]
        print(f"{bright_cyan(f'📚 {char.name}이(가) {learned_skill}을(를) 배웠습니다!')}")
        print("트레이닝 센터에서만 사용 가능한 임시 스킬입니다.")
        
        self.experiment_log.append(f"{char.name} 새 스킬 학습: {learned_skill}")
        input("계속하려면 Enter를 누르세요...")
    
    def _east_wing_functions(self):
        """📊 능력치 연구소 기능들"""
        functions = [
            "📈 스탯 분석",
            "⚖️ 능력치 비교",
            "🔍 약점 진단",
            "💪 강화 시뮬레이션"
        ]
        
        descriptions = [
            "현재 파티의 모든 능력치를 분석합니다",
            "파티원들의 능력치를 비교합니다",
            "캐릭터의 약점과 강점을 찾습니다",
            "장비나 레벨업 효과를 시뮬레이션합니다"
        ]
        
        function_menu = create_simple_menu(
            "📊 능력치 연구소 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._stat_analysis()
        elif choice == 1:
            self._stat_comparison()
        elif choice == 2:
            self._weakness_diagnosis()
    
    def _stat_analysis(self):
        """스탯 분석"""
        clear_screen()
        print(f"{bright_cyan('📈 파티 능력치 분석')}")
        print("="*50)
        
        if not self.training_party:
            print(f"{bright_yellow('분석할 파티원이 없습니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        for char in self.training_party:
            print(f"\n{bright_green(char.name)} (Lv.{char.level} {char.character_class})")
            print(f"  💚 체력: {char.current_hp}/{char.max_hp}")
            print(f"  💙 마나: {char.current_mp}/{char.max_mp}")
            print(f"  ⚔️ 물리 공격: {char.physical_attack}")
            print(f"  🔮 마법 공격: {char.magic_attack}")
            print(f"  🛡️ 물리 방어: {char.physical_defense}")
            print(f"  ✨ 마법 방어: {char.magic_defense}")
            print(f"  ⚡ 속도: {char.speed}")
            
            # 능력치 평가
            total_stats = char.physical_attack + char.magic_attack + char.physical_defense + char.magic_defense + char.speed
            avg_stat = total_stats / 5
            
            if avg_stat >= 100:
                rating = "S급"
            elif avg_stat >= 80:
                rating = "A급"
            elif avg_stat >= 60:
                rating = "B급"
            elif avg_stat >= 40:
                rating = "C급"
            else:
                rating = "D급"
            
            print(f"  🏆 종합 평가: {rating} (평균 {avg_stat:.1f})")
        
        self.experiment_log.append("파티 능력치 분석 실시")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _stat_comparison(self):
        """능력치 비교"""
        if len(self.training_party) < 2:
            print(f"{bright_yellow('비교하려면 최소 2명의 파티원이 필요합니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        clear_screen()
        print(f"{bright_cyan('⚖️ 파티원 능력치 비교')}")
        print("="*60)
        
        # 각 스탯별 최고/최저 찾기
        stats = ['physical_attack', 'magic_attack', 'physical_defense', 'magic_defense', 'speed']
        stat_names = ['물리 공격', '마법 공격', '물리 방어', '마법 방어', '속도']
        
        for stat, name in zip(stats, stat_names):
            values = [(getattr(char, stat), char.name) for char in self.training_party]
            values.sort(reverse=True)
            
            print(f"\n{bright_blue(name)} 순위:")
            for i, (value, char_name) in enumerate(values, 1):
                if i == 1:
                    print(f"  🥇 {i}위: {char_name} ({value})")
                elif i == 2:
                    print(f"  🥈 {i}위: {char_name} ({value})")
                elif i == 3:
                    print(f"  🥉 {i}위: {char_name} ({value})")
                else:
                    print(f"     {i}위: {char_name} ({value})")
        
        self.experiment_log.append("파티원 능력치 비교 완료")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _weakness_diagnosis(self):
        """약점 진단"""
        char = self._select_character()
        if not char:
            return
        
        clear_screen()
        print(f"{bright_cyan(f'🔍 {char.name}의 약점 진단')}")
        print("="*40)
        
        # 능력치 분석
        stats = {
            '물리 공격': char.physical_attack,
            '마법 공격': char.magic_attack,
            '물리 방어': char.physical_defense,
            '마법 방어': char.magic_defense,
            '속도': char.speed
        }
        
        avg_stat = sum(stats.values()) / len(stats)
        
        print(f"평균 능력치: {avg_stat:.1f}")
        print("\n📊 능력치 분석:")
        
        strengths = []
        weaknesses = []
        
        for stat_name, value in stats.items():
            if value >= avg_stat * 1.2:
                strengths.append(f"{stat_name} ({value})")
                print(f"  💪 {bright_green(stat_name)}: {value} (강점)")
            elif value <= avg_stat * 0.8:
                weaknesses.append(f"{stat_name} ({value})")
                print(f"  ⚠️ {bright_red(stat_name)}: {value} (약점)")
            else:
                print(f"  ⚖️ {stat_name}: {value} (평균)")
        
        print(f"\n{bright_green('🎯 개선 제안:')}")
        if weaknesses:
            print("약점 보완이 필요한 능력치:")
            for weakness in weaknesses:
                print(f"  - {weakness}")
        else:
            print("균형 잡힌 능력치를 가지고 있습니다!")
        
        if strengths:
            print("\n활용 가능한 강점:")
            for strength in strengths:
                print(f"  + {strength}")
        
        self.experiment_log.append(f"{char.name} 약점 진단 완료")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _enhancement_simulation(self):
        """강화 시뮬레이션"""
        char = self._select_character()
        if not char:
            return
        
        enhancement_types = [
            "레벨업 시뮬레이션",
            "장비 강화 시뮬레이션",
            "스킬 강화 시뮬레이션",
            "종합 강화 시뮬레이션"
        ]
        
        enhancement_menu = create_simple_menu(
            f"{char.name}의 강화 시뮬레이션",
            enhancement_types,
            [
                "레벨업 시 능력치 변화를 예측합니다",
                "장비 착용 시 능력치 변화를 시뮬레이션합니다",
                "스킬 레벨업 효과를 확인합니다",
                "모든 강화 요소를 종합적으로 시뮬레이션합니다"
            ],
            clear_screen=True
        )
        
        choice = enhancement_menu.run()
        if choice is None or choice < 0:
            return
        
        clear_screen()
        print(f"{bright_cyan(f'💪 {char.name}의 {enhancement_types[choice]}')}")
        print("="*50)
        
        if choice == 0:  # 레벨업 시뮬레이션
            print("현재 능력치:")
            print(f"  레벨: {char.level}")
            print(f"  체력: {char.max_hp}")
            print(f"  마나: {char.max_mp}")
            
            print(f"\n레벨 {char.level + 5} 예상 능력치:")
            future_hp = char.max_hp + (5 * 20)
            future_mp = char.max_mp + (5 * 15)
            print(f"  레벨: {char.level + 5}")
            print(f"  체력: {future_hp} (+{future_hp - char.max_hp})")
            print(f"  마나: {future_mp} (+{future_mp - char.max_mp})")
            
        elif choice == 1:  # 장비 강화 시뮬레이션
            print("가상 장비 착용 시뮬레이션:")
            bonus_attack = 50
            bonus_defense = 30
            print(f"  물리 공격: {char.physical_attack} → {char.physical_attack + bonus_attack} (+{bonus_attack})")
            print(f"  물리 방어: {char.physical_defense} → {char.physical_defense + bonus_defense} (+{bonus_defense})")
            
        elif choice == 2:  # 스킬 강화 시뮬레이션
            print("스킬 레벨업 효과 시뮬레이션:")
            print("  기본 스킬 데미지: 100 → 150 (+50%)")
            print("  스킬 효과 지속시간: 3턴 → 5턴 (+2턴)")
            print("  MP 소모량: 20 → 18 (-2)")
            
        else:  # 종합 강화 시뮬레이션
            print("종합 강화 후 예상 능력치:")
            total_bonus = 100
            print(f"  전체 전투력: 현재 → +{total_bonus}% 증가 예상")
            print("  추천 강화 순서:")
            print("    1. 레벨업 우선")
            print("    2. 주력 장비 강화")
            print("    3. 스킬 특화")
        
        self.experiment_log.append(f"{char.name} {enhancement_types[choice]} 완료")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _stat_lab_functions(self):
        """🔬 스탯 실험실 기능들"""
        functions = [
            "⚙️ 능력치 조정",
            "🔄 능력치 재분배",
            "🎯 특화 빌드 테스트",
            "📊 최적화 분석"
        ]
        
        descriptions = [
            "특정 능력치를 직접 조정해봅니다",
            "능력치 포인트를 재분배합니다",
            "특정 역할에 특화된 빌드를 테스트합니다",
            "현재 빌드의 최적화 방안을 분석합니다"
        ]
        
        function_menu = create_simple_menu(
            "🔬 스탯 실험실 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._adjust_stats()
        elif choice == 1:
            self._redistribute_stats()
        elif choice == 2:
            self._test_specialized_build()
        elif choice == 3:
            self._optimization_analysis()
    
    def _adjust_stats(self):
        """능력치 조정"""
        char = self._select_character()
        if not char:
            return
        
        stats = [
            ("물리 공격", "physical_attack"),
            ("마법 공격", "magic_attack"),
            ("물리 방어", "physical_defense"),
            ("마법 방어", "magic_defense"),
            ("속도", "speed")
        ]
        
        stat_menu = create_simple_menu(
            f"{char.name}의 조정할 능력치 선택",
            [f"{name}: {getattr(char, attr)}" for name, attr in stats],
            [f"{name}을(를) 조정합니다" for name, _ in stats],
            clear_screen=True
        )
        
        choice = stat_menu.run()
        if choice is None or choice < 0:
            return
        
        stat_name, stat_attr = stats[choice]
        current_value = getattr(char, stat_attr)
        
        try:
            new_value = int(input(f"{stat_name} 새로운 값 입력 (현재: {current_value}): "))
            new_value = max(1, min(new_value, 999))  # 1-999 범위
            
            setattr(char, stat_attr, new_value)
            
            print(f"{bright_green(f'✅ {stat_name}이(가) {current_value} → {new_value}로 변경되었습니다!')}")
            self.experiment_log.append(f"{char.name} {stat_name} 조정: {current_value} → {new_value}")
            
        except ValueError:
            print(f"{bright_red('❌ 올바른 숫자를 입력해주세요.')}")
        
        input("계속하려면 Enter를 누르세요...")
    
    def _redistribute_stats(self):
        """능력치 재분배"""
        char = self._select_character()
        if not char:
            return
        
        # 현재 총 능력치 포인트 계산
        total_points = (char.physical_attack + char.magic_attack + 
                       char.physical_defense + char.magic_defense + char.speed)
        
        print(f"{bright_cyan(f'{char.name}의 능력치 재분배')}")
        print(f"사용 가능한 총 포인트: {total_points}")
        print("\n현재 능력치:")
        print(f"  물리 공격: {char.physical_attack}")
        print(f"  마법 공격: {char.magic_attack}")
        print(f"  물리 방어: {char.physical_defense}")
        print(f"  마법 방어: {char.magic_defense}")
        print(f"  속도: {char.speed}")
        
        # 간단한 재분배 옵션 제공
        redistribution_options = [
            "밸런스형 (모든 능력치 균등)",
            "물리 딜러형 (물리 공격 특화)",
            "마법 딜러형 (마법 공격 특화)",
            "탱커형 (방어력 특화)",
            "스피드형 (속도 특화)"
        ]
        
        option_menu = create_simple_menu(
            "재분배 타입 선택",
            redistribution_options,
            [f"{option}으로 능력치를 재분배합니다" for option in redistribution_options],
            clear_screen=True
        )
        
        choice = option_menu.run()
        if choice is None or choice < 0:
            return
        
        base_stat = total_points // 5
        
        if choice == 0:  # 밸런스형
            char.physical_attack = base_stat
            char.magic_attack = base_stat
            char.physical_defense = base_stat
            char.magic_defense = base_stat
            char.speed = base_stat
        elif choice == 1:  # 물리 딜러형
            char.physical_attack = int(base_stat * 1.8)
            char.magic_attack = int(base_stat * 0.6)
            char.physical_defense = base_stat
            char.magic_defense = int(base_stat * 0.8)
            char.speed = int(base_stat * 1.0)
        elif choice == 2:  # 마법 딜러형
            char.physical_attack = int(base_stat * 0.6)
            char.magic_attack = int(base_stat * 1.8)
            char.physical_defense = int(base_stat * 0.8)
            char.magic_defense = base_stat
            char.speed = int(base_stat * 1.0)
        elif choice == 3:  # 탱커형
            char.physical_attack = int(base_stat * 0.8)
            char.magic_attack = int(base_stat * 0.6)
            char.physical_defense = int(base_stat * 1.6)
            char.magic_defense = int(base_stat * 1.4)
            char.speed = int(base_stat * 0.8)
        elif choice == 4:  # 스피드형
            char.physical_attack = int(base_stat * 1.2)
            char.magic_attack = int(base_stat * 1.0)
            char.physical_defense = int(base_stat * 0.8)
            char.magic_defense = int(base_stat * 0.8)
            char.speed = int(base_stat * 1.6)
        
        print(f"{bright_green(f'✅ {redistribution_options[choice]}로 능력치가 재분배되었습니다!')}")
        print("\n새로운 능력치:")
        print(f"  물리 공격: {char.physical_attack}")
        print(f"  마법 공격: {char.magic_attack}")
        print(f"  물리 방어: {char.physical_defense}")
        print(f"  마법 방어: {char.magic_defense}")
        print(f"  속도: {char.speed}")
        
        self.experiment_log.append(f"{char.name} 능력치 재분배: {redistribution_options[choice]}")
        input("계속하려면 Enter를 누르세요...")
    
    def _test_specialized_build(self):
        """특화 빌드 테스트"""
        char = self._select_character()
        if not char:
            return
        
        builds = [
            ("글래스 캐논", "극한 공격력, 최소 방어력"),
            ("요새", "극한 방어력, 최소 공격력"),
            ("번개", "극한 속도, 밸런스 공격력"),
            ("만능형", "모든 능력치 최적화"),
            ("원소술사", "마법 공격 극대화")
        ]
        
        build_menu = create_simple_menu(
            "테스트할 특화 빌드 선택",
            [name for name, _ in builds],
            [desc for _, desc in builds],
            clear_screen=True
        )
        
        choice = build_menu.run()
        if choice is None or choice < 0:
            return
        
        build_name, build_desc = builds[choice]
        
        print(f"{bright_cyan(f'{build_name} 빌드 테스트')}")
        print(f"설명: {build_desc}")
        print("\n빌드 적용 시뮬레이션...")
        
        # 원래 스탯 백업
        original_stats = {
            'physical_attack': char.physical_attack,
            'magic_attack': char.magic_attack,
            'physical_defense': char.physical_defense,
            'magic_defense': char.magic_defense,
            'speed': char.speed
        }
        
        # 빌드별 스탯 조정
        if choice == 0:  # 글래스 캐논
            char.physical_attack *= 2
            char.magic_attack *= 2
            char.physical_defense //= 2
            char.magic_defense //= 2
        elif choice == 1:  # 요새
            char.physical_attack //= 2
            char.magic_attack //= 2
            char.physical_defense *= 2
            char.magic_defense *= 2
        elif choice == 2:  # 번개
            char.speed *= 2
            char.physical_attack = int(char.physical_attack * 1.2)
        elif choice == 3:  # 만능형
            bonus = 20
            char.physical_attack += bonus
            char.magic_attack += bonus
            char.physical_defense += bonus
            char.magic_defense += bonus
            char.speed += bonus
        elif choice == 4:  # 원소술사
            char.magic_attack *= 3
            char.physical_attack //= 2
        
        print(f"\n{bright_green('빌드 적용 완료!')}")
        print("새로운 능력치:")
        print(f"  물리 공격: {char.physical_attack}")
        print(f"  마법 공격: {char.magic_attack}")
        print(f"  물리 방어: {char.physical_defense}")
        print(f"  마법 방어: {char.magic_defense}")
        print(f"  속도: {char.speed}")
        
        restore = input(f"\n원래 능력치로 복구하시겠습니까? (y/N): ").strip().lower()
        if restore == 'y':
            char.physical_attack = original_stats['physical_attack']
            char.magic_attack = original_stats['magic_attack']
            char.physical_defense = original_stats['physical_defense']
            char.magic_defense = original_stats['magic_defense']
            char.speed = original_stats['speed']
            print(f"{bright_blue('능력치가 원래대로 복구되었습니다.')}")
        
        self.experiment_log.append(f"{char.name} {build_name} 빌드 테스트")
        input("계속하려면 Enter를 누르세요...")
    
    def _optimization_analysis(self):
        """최적화 분석"""
        char = self._select_character()
        if not char:
            return
        
        clear_screen()
        print(f"{bright_cyan(f'📊 {char.name}의 최적화 분석')}")
        print("="*50)
        
        # 현재 빌드 분석
        stats = {
            '물리 공격': char.physical_attack,
            '마법 공격': char.magic_attack,
            '물리 방어': char.physical_defense,
            '마법 방어': char.magic_defense,
            '속도': char.speed
        }
        
        # 가장 높은/낮은 스탯 찾기
        max_stat = max(stats.items(), key=lambda x: x[1])
        min_stat = min(stats.items(), key=lambda x: x[1])
        
        print(f"주특기: {max_stat[0]} ({max_stat[1]})")
        print(f"약점: {min_stat[0]} ({min_stat[1]})")
        
        # 클래스별 권장 스탯 제안
        class_recommendations = {
            '전사': ['물리 공격', '물리 방어'],
            '마법사': ['마법 공격', '마법 방어'],
            '아크메이지': ['마법 공격', '마법 방어'],
            '궁수': ['물리 공격', '속도'],
            '도적': ['물리 공격', '속도'],
            '성기사': ['물리 공격', '물리 방어'],
            '힐러': ['마법 공격', '마법 방어']
        }
        
        recommended_stats = class_recommendations.get(char.character_class, ['물리 공격', '속도'])
        
        print(f"\n{char.character_class} 클래스 권장 특성:")
        for stat in recommended_stats:
            current_value = stats[stat]
            print(f"  - {stat}: {current_value} (권장)")
        
        print(f"\n{bright_green('최적화 제안:')}")
        
        # 개선 제안
        improvements = []
        avg_stat = sum(stats.values()) / len(stats)
        
        for stat_name, value in stats.items():
            if stat_name in recommended_stats and value < avg_stat:
                improvements.append(f"{stat_name} 강화 필요 (현재 {value})")
        
        if improvements:
            print("개선 우선순위:")
            for i, improvement in enumerate(improvements, 1):
                print(f"  {i}. {improvement}")
        else:
            print("현재 빌드가 클래스에 잘 맞습니다!")
        
        # 효율성 점수 계산
        efficiency_score = 0
        for stat in recommended_stats:
            if stat in stats:
                efficiency_score += stats[stat]
        
        efficiency_score = min(100, efficiency_score // 10)
        print(f"\n빌드 효율성: {efficiency_score}%")
        
        if efficiency_score >= 80:
            print("🏆 매우 효율적인 빌드입니다!")
        elif efficiency_score >= 60:
            print("👍 양호한 빌드입니다.")
        else:
            print("🔧 개선의 여지가 있습니다.")
        
        self.experiment_log.append(f"{char.name} 최적화 분석 (효율성 {efficiency_score}%)")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _level_booster_functions(self):
        """레벨 조정실 - 간단한 레벨 조정 기능 구현"""
        if not self.training_party:
            print(f"{bright_yellow('조정할 파티원이 없습니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        functions = [
            "⬆️ 레벨 +1",
            "⬇️ 레벨 -1",
            "🎯 특정 레벨로 설정",
            "⭐ 최대 레벨(50)로 설정"
        ]
        
        descriptions = [
            "선택한 캐릭터의 레벨을 1 올립니다",
            "선택한 캐릭터의 레벨을 1 내립니다",
            "선택한 캐릭터를 원하는 레벨로 설정합니다",
            "선택한 캐릭터를 최대 레벨로 설정합니다"
        ]
        
        function_menu = create_simple_menu(
            "⭐ 레벨 조정실 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._level_up_character()
        elif choice == 1:
            self._level_down_character()
        elif choice == 2:
            self._set_specific_level()
        elif choice == 3:
            self._set_max_level()
    
    def _level_up_character(self):
        """캐릭터 레벨업"""
        char = self._select_character()
        if not char:
            return
        
        if char.level >= 50:
            print(f"{bright_yellow(f'{char.name}은(는) 이미 최대 레벨입니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        old_level = char.level
        char.level += 1
        char.max_hp += 20
        char.max_mp += 15
        char.current_hp = char.max_hp
        char.current_mp = char.max_mp
        
        print(f"{bright_green(f'✅ {char.name}의 레벨이 {old_level} → {char.level}로 올랐습니다!')}")
        self.experiment_log.append(f"{char.name} 레벨업: {old_level} → {char.level}")
        input("계속하려면 Enter를 누르세요...")
    
    def _level_down_character(self):
        """캐릭터 레벨다운"""
        char = self._select_character()
        if not char:
            return
        
        if char.level <= 1:
            print(f"{bright_yellow(f'{char.name}은(는) 이미 최소 레벨입니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        old_level = char.level
        char.level -= 1
        char.max_hp = max(char.max_hp - 20, 50)
        char.max_mp = max(char.max_mp - 15, 30)
        char.current_hp = min(char.current_hp, char.max_hp)
        char.current_mp = min(char.current_mp, char.max_mp)
        
        print(f"{bright_blue(f'📉 {char.name}의 레벨이 {old_level} → {char.level}로 내려갔습니다.')}")
        self.experiment_log.append(f"{char.name} 레벨다운: {old_level} → {char.level}")
        input("계속하려면 Enter를 누르세요...")
    
    def _set_specific_level(self):
        """특정 레벨로 설정"""
        char = self._select_character()
        if not char:
            return
        
        try:
            target_level = int(input("설정할 레벨을 입력하세요 (1-50): "))
            target_level = max(1, min(target_level, 50))
        except ValueError:
            print(f"{bright_red('❌ 올바른 숫자를 입력해주세요.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        old_level = char.level
        char.level = target_level
        char.max_hp = 100 + (target_level - 1) * 20
        char.max_mp = 50 + (target_level - 1) * 15
        char.current_hp = char.max_hp
        char.current_mp = char.max_mp
        
        print(f"{bright_cyan(f'🎯 {char.name}의 레벨이 {old_level} → {char.level}로 설정되었습니다!')}")
        self.experiment_log.append(f"{char.name} 레벨 설정: {old_level} → {char.level}")
        input("계속하려면 Enter를 누르세요...")
    
    def _set_max_level(self):
        """최대 레벨로 설정"""
        char = self._select_character()
        if not char:
            return
        
        old_level = char.level
        char.level = 50
        char.max_hp = 1080
        char.max_mp = 785
        char.current_hp = char.max_hp
        char.current_mp = char.max_mp
        
        print(f"{bright_cyan(f'⭐ {char.name}이(가) 최대 레벨 50에 도달했습니다!')}")
        self.experiment_log.append(f"{char.name} 최대 레벨 설정: {old_level} → 50")
        input("계속하려면 Enter를 누르세요...")
    
    def _select_character(self) -> Optional[Character]:
        """캐릭터 선택"""
        if not self.training_party:
            return None
        
        char_options = []
        char_descriptions = []
        
        for char in self.training_party:
            char_options.append(f"{char.name} (Lv.{char.level})")
            char_descriptions.append(f"{char.character_class} - HP:{char.current_hp}/{char.max_hp}")
        
        char_menu = create_simple_menu(
            "대상 캐릭터 선택",
            char_options,
            char_descriptions,
            clear_screen=True
        )
        
        choice = char_menu.run()
        if choice is None or choice < 0:
            return None
        
        return self.training_party[choice]
    
    def _south_wing_functions(self):
        self._show_under_development("🎒 장비 테스트 구역")
    
    def _item_warehouse_functions(self):
        """📦 아이템 창고 기능들"""
        functions = [
            "🎒 인벤토리 관리",
            "⚗️ 아이템 생성",
            "🔄 아이템 교환",
            "🗑️ 아이템 삭제"
        ]
        
        descriptions = [
            "현재 인벤토리를 확인하고 관리합니다",
            "테스트용 아이템을 생성합니다",
            "파티원 간 아이템을 교환합니다",
            "불필요한 아이템을 삭제합니다"
        ]
        
        function_menu = create_simple_menu(
            "📦 아이템 창고 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._manage_inventory()
        elif choice == 1:
            self._create_test_items()
        elif choice == 2:
            self._exchange_items()
        elif choice == 3:
            self._delete_items()
    
    def _manage_inventory(self):
        """인벤토리 관리"""
        char = self._select_character()
        if not char:
            return
        
        clear_screen()
        print(f"{bright_cyan(f'🎒 {char.name}의 인벤토리')}")
        print("="*40)
        
        if hasattr(char, 'inventory') and char.inventory:
            print("보유 아이템:")
            if hasattr(char.inventory, 'items') and char.inventory.items:
                for i, (item_key, item_data) in enumerate(char.inventory.items.items(), 1):
                    # item_data는 갯수를 나타내므로 명확하게 표시
                    if isinstance(item_data, int):
                        print(f"  {i}. {item_key} x{item_data}개")
                    else:
                        print(f"  {i}. {item_key}: {item_data}")
            else:
                print("  (인벤토리가 비어있습니다)")
        else:
            print("인벤토리가 비어있습니다.")
        
        print(f"\n소지금: {getattr(char, 'gold', 0)} Gold")
        
        self.experiment_log.append(f"{char.name} 인벤토리 확인")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _create_test_items(self):
        """테스트 아이템 생성"""
        char = self._select_character()
        if not char:
            return
        
        test_items = [
            "체력 포션 (대)",
            "마나 포션 (대)", 
            "전설의 검",
            "마법의 방패",
            "신속의 부츠",
            "지혜의 반지",
            "용의 비늘",
            "엘릭서"
        ]
        
        item_menu = create_simple_menu(
            "생성할 테스트 아이템 선택",
            test_items,
            [f"{item}을(를) 생성합니다" for item in test_items],
            clear_screen=True
        )
        
        choice = item_menu.run()
        if choice is None or choice < 0:
            return
        
        selected_item = test_items[choice]
        
        # 인벤토리가 없으면 생성
        if not hasattr(char, 'inventory'):
            char.inventory = []
        
        char.inventory.append(selected_item)
        
        print(f"{bright_green(f'✅ {selected_item}이(가) {char.name}의 인벤토리에 추가되었습니다!')}")
        self.experiment_log.append(f"{char.name}에게 {selected_item} 지급")
        input("계속하려면 Enter를 누르세요...")
    
    def _exchange_items(self):
        """아이템 교환"""
        if len(self.training_party) < 2:
            print(f"{bright_yellow('아이템 교환하려면 최소 2명의 파티원이 필요합니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        print(f"{bright_cyan('🔄 아이템 교환')}")
        print("교환할 두 캐릭터를 선택하세요.")
        
        # 첫 번째 캐릭터 선택
        print("\n첫 번째 캐릭터:")
        char1 = self._select_character()
        if not char1:
            return
        
        # 두 번째 캐릭터 선택
        remaining_chars = [c for c in self.training_party if c != char1]
        if not remaining_chars:
            print("교환할 다른 캐릭터가 없습니다.")
            return
        
        char2_menu = create_simple_menu(
            "두 번째 캐릭터 선택",
            [f"{char.name} (Lv.{char.level} {char.character_class})" for char in remaining_chars],
            ["이 캐릭터와 아이템을 교환합니다" for _ in remaining_chars],
            clear_screen=True
        )
        
        char2_choice = char2_menu.run()
        if char2_choice is None or char2_choice < 0:
            return
        
        char2 = remaining_chars[char2_choice]
        
        # 간단한 골드 교환 시뮬레이션
        gold1 = getattr(char1, 'gold', 100)
        gold2 = getattr(char2, 'gold', 100)
        
        try:
            amount = int(input(f"{char1.name}이 {char2.name}에게 줄 골드 (보유: {gold1}): "))
            if 0 <= amount <= gold1:
                char1.gold = gold1 - amount
                char2.gold = gold2 + amount
                
                print(f"{bright_green(f'✅ {char1.name}이 {char2.name}에게 {amount} 골드를 전달했습니다!')}")
                self.experiment_log.append(f"아이템 교환: {char1.name} → {char2.name} ({amount} 골드)")
            else:
                print(f"{bright_red('❌ 보유 골드를 초과했습니다.')}")
        except ValueError:
            print(f"{bright_red('❌ 올바른 숫자를 입력해주세요.')}")
        
        input("계속하려면 Enter를 누르세요...")
    
    def _delete_items(self):
        """아이템 삭제"""
        char = self._select_character()
        if not char:
            return
        
        if not hasattr(char, 'inventory') or not char.inventory:
            print(f"{bright_yellow(f'{char.name}의 인벤토리가 비어있습니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        # 인벤토리 아이템 목록 생성
        inventory_items = []
        inventory_descriptions = []
        
        if hasattr(char.inventory, 'items') and char.inventory.items:
            for item_key, item_data in char.inventory.items.items():
                inventory_items.append(item_key)
                # 갯수 정보 포함하여 표시
                if isinstance(item_data, int):
                    inventory_descriptions.append(f"{item_key} x{item_data}개를 삭제합니다")
                else:
                    inventory_descriptions.append(f"{item_key}을(를) 삭제합니다")
        
        if not inventory_items:
            print("삭제할 아이템이 없습니다.")
            return
        
        item_menu = create_simple_menu(
            f"{char.name}의 삭제할 아이템 선택",
            inventory_items,
            inventory_descriptions,
            clear_screen=True
        )
        
        choice = item_menu.run()
        if choice is None or choice < 0:
            return
        
        deleted_item = char.inventory.pop(choice)
        print(f"{bright_green(f'✅ {deleted_item}이(가) 삭제되었습니다!')}")
        self.experiment_log.append(f"{char.name} {deleted_item} 삭제")
        input("계속하려면 Enter를 누르세요...")
    
    def _equipment_forge_functions(self):
        """⚒️ 장비 대장간 기능들"""
        functions = [
            "🛡️ 장비 확인",
            "⚡ 장비 강화",
            "🔮 장비 인챈트",
            "🔄 장비 교체"
        ]
        
        descriptions = [
            "현재 착용 중인 장비를 확인합니다",
            "장비의 성능을 강화합니다",
            "장비에 마법 효과를 부여합니다",
            "다른 장비로 교체합니다"
        ]
        
        function_menu = create_simple_menu(
            "⚒️ 장비 대장간 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._check_equipment()
        elif choice == 1:
            self._enhance_equipment()
        elif choice == 2:
            self._enchant_equipment()
        elif choice == 3:
            self._change_equipment()
    
    def _check_equipment(self):
        """장비 확인"""
        char = self._select_character()
        if not char:
            return
        
        clear_screen()
        print(f"{bright_cyan(f'🛡️ {char.name}의 장비 현황')}")
        print("="*40)
        
        # 기본 장비 정보 (시뮬레이션)
        equipment_slots = {
            '무기': '기본 무기',
            '방어구': '기본 갑옷', 
            '장신구': '기본 반지',
            '신발': '기본 신발'
        }
        
        print("착용 중인 장비:")
        for slot, item in equipment_slots.items():
            print(f"  {slot}: {item}")
        
        print(f"\n장비 효과:")
        print(f"  공격력 보너스: +{char.physical_attack // 10}")
        print(f"  방어력 보너스: +{char.physical_defense // 10}")
        print(f"  속도 보너스: +{char.speed // 20}")
        
        self.experiment_log.append(f"{char.name} 장비 현황 확인")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _enhance_equipment(self):
        """장비 강화"""
        char = self._select_character()
        if not char:
            return
        
        equipment_types = ["무기", "방어구", "장신구", "신발"]
        
        equipment_menu = create_simple_menu(
            "강화할 장비 선택",
            equipment_types,
            [f"{eq}를 강화하여 능력치를 올립니다" for eq in equipment_types],
            clear_screen=True
        )
        
        choice = equipment_menu.run()
        if choice is None or choice < 0:
            return
        
        equipment_type = equipment_types[choice]
        
        print(f"{bright_cyan(f'⚡ {equipment_type} 강화')}")
        print(f"{equipment_type} 강화를 진행합니다...")
        
        # 강화 시뮬레이션
        if equipment_type == "무기":
            bonus = 15
            char.physical_attack += bonus
            char.magic_attack += bonus
            print(f"✅ 공격력이 +{bonus} 증가했습니다!")
        elif equipment_type == "방어구":
            bonus = 12
            char.physical_defense += bonus
            char.magic_defense += bonus
            print(f"✅ 방어력이 +{bonus} 증가했습니다!")
        elif equipment_type == "장신구":
            bonus = 8
            char.physical_attack += bonus
            char.magic_attack += bonus
            char.speed += bonus
            print(f"✅ 모든 능력치가 +{bonus} 증가했습니다!")
        elif equipment_type == "신발":
            bonus = 20
            char.speed += bonus
            print(f"✅ 속도가 +{bonus} 증가했습니다!")
        
        self.experiment_log.append(f"{char.name} {equipment_type} 강화")
        input("계속하려면 Enter를 누르세요...")
    
    def _enchant_equipment(self):
        """장비 인챈트"""
        char = self._select_character()
        if not char:
            return
        
        enchant_types = [
            ("화염 인챈트", "공격 시 화상 효과"),
            ("냉기 인챈트", "공격 시 빙결 효과"),
            ("독 인챈트", "공격 시 중독 효과"),
            ("신성 인챈트", "공격 시 회복 효과"),
            ("흡혈 인챈트", "공격 시 체력 흡수")
        ]
        
        enchant_menu = create_simple_menu(
            "인챈트 타입 선택",
            [name for name, _ in enchant_types],
            [desc for _, desc in enchant_types],
            clear_screen=True
        )
        
        choice = enchant_menu.run()
        if choice is None or choice < 0:
            return
        
        enchant_name, enchant_desc = enchant_types[choice]
        
        print(f"{bright_cyan(f'🔮 {enchant_name} 적용')}")
        print(f"효과: {enchant_desc}")
        print("인챈트가 성공적으로 적용되었습니다!")
        
        # 인챈트에 따른 능력치 보너스
        if "화염" in enchant_name:
            char.magic_attack += 10
        elif "냉기" in enchant_name:
            char.magic_attack += 8
            char.speed += 5
        elif "독" in enchant_name:
            char.physical_attack += 8
        elif "신성" in enchant_name:
            char.magic_defense += 15
        elif "흡혈" in enchant_name:
            char.physical_attack += 12
        
        self.experiment_log.append(f"{char.name} {enchant_name} 적용")
        input("계속하려면 Enter를 누르세요...")
    
    def _change_equipment(self):
        """장비 교체"""
        char = self._select_character()
        if not char:
            return
        
        new_equipment = [
            ("전설의 검", "공격력 +50"),
            ("드래곤 갑옷", "방어력 +40"),
            ("신속의 부츠", "속도 +30"),
            ("지혜의 반지", "마법력 +25"),
            ("용사의 방패", "모든 방어 +20")
        ]
        
        equipment_menu = create_simple_menu(
            "착용할 장비 선택",
            [name for name, _ in new_equipment],
            [desc for _, desc in new_equipment],
            clear_screen=True
        )
        
        choice = equipment_menu.run()
        if choice is None or choice < 0:
            return
        
        equipment_name, equipment_desc = new_equipment[choice]
        
        print(f"{bright_cyan(f'🔄 {equipment_name} 착용')}")
        print(f"효과: {equipment_desc}")
        
        # 장비 효과 적용
        if "검" in equipment_name:
            char.physical_attack += 50
        elif "갑옷" in equipment_name:
            char.physical_defense += 40
            char.magic_defense += 40
        elif "부츠" in equipment_name:
            char.speed += 30
        elif "반지" in equipment_name:
            char.magic_attack += 25
        elif "방패" in equipment_name:
            char.physical_defense += 20
            char.magic_defense += 20
        
        print(f"✅ {equipment_name}을(를) 착용했습니다!")
        self.experiment_log.append(f"{char.name} {equipment_name} 착용")
        input("계속하려면 Enter를 누르세요...")
    
    def _west_wing_functions(self):
        """🔮 서쪽 전용 구역 (BRV 연구소 + 시나리오 룸)"""
        rooms = [
            "⚡ BRV 연구소",
            "🎭 시나리오 룸"
        ]
        
        descriptions = [
            "BRV 시스템을 연구하고 실험합니다",
            "다양한 게임 시나리오를 체험합니다"
        ]
        
        room_menu = create_simple_menu(
            "🔮 서쪽 구역 - 방 선택",
            rooms,
            descriptions,
            clear_screen=True
        )
        
        choice = room_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._brv_lab_functions()
        elif choice == 1:
            self._scenario_room_functions()
    
    def _brv_lab_functions(self):
        """⚡ BRV 연구소 기능들"""
        functions = [
            "📊 BRV 분석",
            "🔬 BRV 실험",
            "⚡ BRV 조정",
            "🎯 BRV 시뮬레이션"
        ]
        
        descriptions = [
            "현재 BRV 상태를 분석합니다",
            "BRV 시스템 실험을 진행합니다",
            "BRV 값을 직접 조정합니다",
            "BRV 전투 시뮬레이션을 실행합니다"
        ]
        
        function_menu = create_simple_menu(
            "⚡ BRV 연구소 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._analyze_brv()
        elif choice == 1:
            self._experiment_brv()
        elif choice == 2:
            self._adjust_brv()
        elif choice == 3:
            self._simulate_brv_combat()
    
    def _analyze_brv(self):
        """BRV 분석"""
        clear_screen()
        print(f"{bright_cyan('📊 파티 BRV 분석')}")
        print("="*40)
        
        if not self.training_party:
            print(f"{bright_yellow('분석할 파티원이 없습니다.')}")
            input("계속하려면 Enter를 누르세요...")
            return
        
        for char in self.training_party:
            current_brv = getattr(char, 'current_brv', 0)
            max_brv = getattr(char, 'max_brv', 9999)
            int_brv = getattr(char, 'int_brv', 100)
            
            print(f"\n{bright_green(char.name)}:")
            print(f"  현재 BRV: {current_brv}")
            print(f"  최대 BRV: {max_brv}")
            print(f"  기본 BRV: {int_brv}")
            
            # BRV 상태 평가
            brv_ratio = current_brv / max_brv if max_brv > 0 else 0
            if brv_ratio >= 0.8:
                status = "우수"
            elif brv_ratio >= 0.5:
                status = "양호"
            elif brv_ratio >= 0.2:
                status = "주의"
            else:
                status = "위험"
            
            print(f"  BRV 상태: {status} ({brv_ratio*100:.1f}%)")
        
        self.experiment_log.append("파티 BRV 분석 완료")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _experiment_brv(self):
        """BRV 실험"""
        char = self._select_character()
        if not char:
            return
        
        experiments = [
            "BRV BREAK 체험",
            "BRV 회복 테스트", 
            "최대 BRV 도달",
            "BRV 0 상태 체험"
        ]
        
        experiment_menu = create_simple_menu(
            "BRV 실험 선택",
            experiments,
            [f"{exp}를 진행합니다" for exp in experiments],
            clear_screen=True
        )
        
        choice = experiment_menu.run()
        if choice is None or choice < 0:
            return
        
        experiment = experiments[choice]
        
        print(f"{bright_cyan(f'🔬 {experiment} 진행')}")
        
        # 실험 시뮬레이션
        if choice == 0:  # BRV BREAK
            char.current_brv = 0
            print("BRV가 0이 되었습니다! BREAK 상태입니다.")
            print("다음 턴까지 행동할 수 없습니다.")
        elif choice == 1:  # BRV 회복
            char.current_brv = getattr(char, 'int_brv', 100)
            print(f"BRV가 기본값({char.current_brv})으로 회복되었습니다.")
        elif choice == 2:  # 최대 BRV
            char.current_brv = getattr(char, 'max_brv', 9999)
            print(f"BRV가 최대값({char.current_brv})에 도달했습니다!")
        elif choice == 3:  # BRV 0
            char.current_brv = 0
            print("BRV가 0이 되었습니다.")
        
        print(f"현재 {char.name}의 BRV: {char.current_brv}")
        self.experiment_log.append(f"{char.name} {experiment} 완료")
        input("계속하려면 Enter를 누르세요...")
    
    def _adjust_brv(self):
        """BRV 조정"""
        char = self._select_character()
        if not char:
            return
        
        brv_options = [
            "현재 BRV 조정",
            "최대 BRV 조정",
            "기본 BRV 조정"
        ]
        
        brv_menu = create_simple_menu(
            f"{char.name}의 BRV 조정 항목",
            brv_options,
            ["현재 BRV 값을 직접 설정합니다", "최대 BRV 한계를 조정합니다", "턴 시작 시 회복되는 기본 BRV를 조정합니다"],
            clear_screen=True
        )
        
        choice = brv_menu.run()
        if choice is None or choice < 0:
            return
        
        try:
            if choice == 0:  # 현재 BRV
                current = getattr(char, 'current_brv', 0)
                new_value = int(input(f"새로운 현재 BRV (현재: {current}): "))
                new_value = max(0, min(new_value, 99999))
                char.current_brv = new_value
                print(f"✅ 현재 BRV가 {new_value}로 설정되었습니다.")
                
            elif choice == 1:  # 최대 BRV
                current = getattr(char, 'max_brv', 9999)
                new_value = int(input(f"새로운 최대 BRV (현재: {current}): "))
                new_value = max(1, min(new_value, 99999))
                char.max_brv = new_value
                print(f"✅ 최대 BRV가 {new_value}로 설정되었습니다.")
                
            elif choice == 2:  # 기본 BRV
                current = getattr(char, 'int_brv', 100)
                new_value = int(input(f"새로운 기본 BRV (현재: {current}): "))
                new_value = max(1, min(new_value, 9999))
                char.int_brv = new_value
                print(f"✅ 기본 BRV가 {new_value}로 설정되었습니다.")
            
            self.experiment_log.append(f"{char.name} BRV 조정: {brv_options[choice]}")
            
        except ValueError:
            print(f"{bright_red('❌ 올바른 숫자를 입력해주세요.')}")
        
        input("계속하려면 Enter를 누르세요...")
    
    def _simulate_brv_combat(self):
        """BRV 전투 시뮬레이션"""
        char = self._select_character()
        if not char:
            return
        
        print(f"{bright_cyan(f'🎯 {char.name}의 BRV 전투 시뮬레이션')}")
        print("="*50)
        
        # 가상의 적 설정
        enemy_brv = 500
        enemy_hp = 1000
        
        print(f"적 정보:")
        print(f"  BRV: {enemy_brv}")
        print(f"  HP: {enemy_hp}")
        
        print(f"\n{char.name} 정보:")
        char_brv = getattr(char, 'current_brv', 100)
        print(f"  BRV: {char_brv}")
        print(f"  HP: {char.current_hp}")
        
        # 간단한 BRV 전투 시뮬레이션
        print(f"\n전투 시뮬레이션:")
        
        # BRV 공격 시뮬레이션
        brv_damage = char.physical_attack
        enemy_brv -= brv_damage
        char_brv += brv_damage // 2
        
        print(f"1. {char.name}의 BRV 공격!")
        print(f"   → 적 BRV: {enemy_brv} (데미지: {brv_damage})")
        print(f"   → {char.name} BRV: {char_brv} (증가: {brv_damage // 2})")
        
        if enemy_brv <= 0:
            print(f"   💥 적이 BREAK 상태가 되었습니다!")
            enemy_brv = 0
        
        # HP 공격 시뮬레이션
        if char_brv > 0:
            hp_damage = char_brv
            enemy_hp -= hp_damage
            char_brv = 0
            
            print(f"2. {char.name}의 HP 공격!")
            print(f"   → 적 HP: {enemy_hp} (데미지: {hp_damage})")
            print(f"   → {char.name} BRV: {char_brv} (소모)")
            
            if enemy_hp <= 0:
                print(f"   🎉 적을 쓰러뜨렸습니다!")
        
        self.experiment_log.append(f"{char.name} BRV 전투 시뮬레이션")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _scenario_room_functions(self):
        """🎭 시나리오 룸 기능들"""
        functions = [
            "🏰 던전 시나리오",
            "👑 보스 시나리오",
            "🎪 이벤트 시나리오",
            "🎲 랜덤 시나리오"
        ]
        
        descriptions = [
            "다양한 던전 상황을 체험합니다",
            "강력한 보스와의 전투를 시뮬레이션합니다",
            "특별한 이벤트 상황을 체험합니다",
            "무작위 시나리오에 도전합니다"
        ]
        
        function_menu = create_simple_menu(
            "🎭 시나리오 룸 - 기능 선택",
            functions,
            descriptions,
            clear_screen=True
        )
        
        choice = function_menu.run()
        if choice is None or choice < 0:
            return
        elif choice == 0:
            self._dungeon_scenario()
        elif choice == 1:
            self._boss_scenario()
        elif choice == 2:
            self._event_scenario()
        elif choice == 3:
            self._random_scenario()
    
    def _dungeon_scenario(self):
        """던전 시나리오"""
        scenarios = [
            ("어둠의 미궁", "복잡한 미로에서 탈출하세요"),
            ("함정의 방", "숨겨진 함정을 피해 보물을 획득하세요"),
            ("고블린 소굴", "고블린 무리와 전투하세요"),
            ("잃어버린 보물", "전설의 보물을 찾아보세요")
        ]
        
        scenario_menu = create_simple_menu(
            "던전 시나리오 선택",
            [name for name, _ in scenarios],
            [desc for _, desc in scenarios],
            clear_screen=True
        )
        
        choice = scenario_menu.run()
        if choice is None or choice < 0:
            return
        
        scenario_name, scenario_desc = scenarios[choice]
        
        print(f"{bright_cyan(f'🏰 {scenario_name}')}")
        print(f"상황: {scenario_desc}")
        print("="*50)
        
        # 시나리오별 시뮬레이션
        if choice == 0:  # 어둠의 미궁
            print("깊은 어둠 속에서 길을 잃었습니다...")
            print("여러 갈래길이 보입니다.")
            options = ["왼쪽 길", "오른쪽 길", "직진"]
            result = random.choice(options)
            print(f"파티가 {result}를 선택했습니다.")
            if result == "직진":
                print("🎉 올바른 길을 찾았습니다!")
                # 경험치 보너스
                for char in self.training_party:
                    char.experience_points = getattr(char, 'experience_points', 0) + 100
            else:
                print("⚠️ 막다른 길입니다. 다시 돌아가야 합니다.")
                
        elif choice == 1:  # 함정의 방
            print("바닥에 압력판이 보입니다...")
            success = random.choice([True, False])
            if success:
                print("🎉 함정을 성공적으로 해제했습니다!")
                print("보물상자를 발견했습니다!")
            else:
                print("💥 함정이 발동했습니다!")
                print("파티가 피해를 입었습니다.")
                
        elif choice == 2:  # 고블린 소굴
            print("고블린 3마리가 나타났습니다!")
            print("전투가 시작됩니다...")
            total_damage = sum(char.physical_attack for char in self.training_party)
            print(f"파티 총 공격력: {total_damage}")
            if total_damage >= 300:
                print("🎉 고블린들을 물리쳤습니다!")
            else:
                print("⚔️ 치열한 전투가 계속됩니다...")
                
        elif choice == 3:  # 잃어버린 보물
            print("고대 문자가 새겨진 석판을 발견했습니다...")
            print("해독을 시도합니다...")
            magic_power = sum(char.magic_attack for char in self.training_party)
            if magic_power >= 200:
                print("🎉 석판을 해독했습니다!")
                print("전설의 보물 위치를 알아냈습니다!")
            else:
                print("🤔 문자가 너무 복잡합니다...")
        
        self.experiment_log.append(f"던전 시나리오: {scenario_name} 완료")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _boss_scenario(self):
        """보스 시나리오"""
        bosses = [
            ("화염 드래곤", "강력한 화염 브레스를 사용합니다"),
            ("얼음 거인", "빙결 공격으로 적을 얼립니다"),
            ("어둠의 마법사", "강력한 흑마법을 구사합니다"),
            ("기계 골렘", "높은 방어력을 가진 기계 몬스터입니다")
        ]
        
        boss_menu = create_simple_menu(
            "도전할 보스 선택",
            [name for name, _ in bosses],
            [desc for _, desc in bosses],
            clear_screen=True
        )
        
        choice = boss_menu.run()
        if choice is None or choice < 0:
            return
        
        boss_name, boss_desc = bosses[choice]
        
        print(f"{bright_cyan(f'👑 {boss_name} 전투')}")
        print(f"특징: {boss_desc}")
        print("="*50)
        
        # 보스별 특수 능력 시뮬레이션
        boss_hp = 5000
        party_power = sum(char.physical_attack + char.magic_attack for char in self.training_party)
        
        print(f"보스 HP: {boss_hp}")
        print(f"파티 전투력: {party_power}")
        print("\n전투 시뮬레이션:")
        
        rounds = 1
        while boss_hp > 0 and rounds <= 5:
            print(f"\n라운드 {rounds}:")
            
            # 파티 공격
            damage = party_power + random.randint(-50, 50)
            boss_hp -= damage
            print(f"파티 공격! 데미지: {damage}")
            print(f"보스 HP: {max(0, boss_hp)}")
            
            if boss_hp <= 0:
                print(f"🎉 {boss_name}을(를) 쓰러뜨렸습니다!")
                # 승리 보상
                for char in self.training_party:
                    char.experience_points = getattr(char, 'experience_points', 0) + 500
                break
            
            # 보스 공격
            boss_damage = 200 + random.randint(-50, 50)
            print(f"보스 공격! 예상 피해: {boss_damage}")
            
            if choice == 0:  # 화염 드래곤
                print("🔥 화염 브레스 공격!")
            elif choice == 1:  # 얼음 거인
                print("❄️ 빙결 공격!")
            elif choice == 2:  # 어둠의 마법사
                print("🌑 흑마법 공격!")
            elif choice == 3:  # 기계 골렘
                print("⚙️ 미사일 공격!")
            
            rounds += 1
        
        if boss_hp > 0:
            print("⏰ 시간 초과! 전투가 무승부로 끝났습니다.")
        
        self.experiment_log.append(f"보스 시나리오: {boss_name} 도전")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _event_scenario(self):
        """이벤트 시나리오"""
        events = [
            ("마법의 샘", "신비한 샘물을 마실 기회입니다"),
            ("떠돌이 상인", "희귀한 물건을 파는 상인을 만났습니다"),
            ("운명의 선택", "중요한 선택을 해야 합니다"),
            ("고대 유적", "신비한 유적을 발견했습니다")
        ]
        
        event_menu = create_simple_menu(
            "체험할 이벤트 선택",
            [name for name, _ in events],
            [desc for _, desc in events],
            clear_screen=True
        )
        
        choice = event_menu.run()
        if choice is None or choice < 0:
            return
        
        event_name, event_desc = events[choice]
        
        print(f"{bright_cyan(f'🎪 {event_name}')}")
        print(f"상황: {event_desc}")
        print("="*50)
        
        if choice == 0:  # 마법의 샘
            print("신비한 샘물이 반짝입니다...")
            print("샘물을 마시겠습니까?")
            decision = random.choice(["마신다", "마시지 않는다"])
            print(f"파티의 선택: {decision}")
            
            if decision == "마신다":
                effect = random.choice(["능력치 증가", "체력 회복", "마나 회복"])
                print(f"🎉 {effect} 효과를 받았습니다!")
                if effect == "능력치 증가":
                    for char in self.training_party:
                        char.physical_attack += 5
                        char.magic_attack += 5
            else:
                print("조심스럽게 지나갔습니다.")
                
        elif choice == 1:  # 떠돌이 상인
            print("수수께끼의 상인이 물건을 팔고 있습니다...")
            items = ["신비한 포션", "마법 두루마리", "행운의 부적"]
            item = random.choice(items)
            print(f"상인이 {item}을(를) 제안합니다.")
            print(f"🎁 {item}을(를) 획득했습니다!")
            
        elif choice == 2:  # 운명의 선택
            print("갈래길에서 두 개의 문을 발견했습니다...")
            doors = ["금문", "은문"]
            chosen_door = random.choice(doors)
            print(f"파티가 {chosen_door}을 선택했습니다.")
            
            if chosen_door == "금문":
                print("🎉 보물을 발견했습니다!")
            else:
                print("🎭 특별한 경험을 했습니다!")
                
        elif choice == 3:  # 고대 유적
            print("고대 문명의 유적이 나타났습니다...")
            print("유적을 조사합니다...")
            knowledge = sum(char.magic_attack for char in self.training_party)
            
            if knowledge >= 300:
                print("🎉 고대의 지식을 획득했습니다!")
                print("파티 전체의 지혜가 증가했습니다!")
            else:
                print("🤔 유적의 비밀을 완전히 해독하지 못했습니다...")
        
        self.experiment_log.append(f"이벤트 시나리오: {event_name} 완료")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _random_scenario(self):
        """랜덤 시나리오"""
        random_events = [
            "갑작스런 몬스터 습격",
            "신비한 보물 발견",
            "마법 진법 해제",
            "동료 구출 작전",
            "시간 제한 퍼즐",
            "정체불명 NPC와의 만남"
        ]
        
        selected_event = random.choice(random_events)
        
        print(f"{bright_cyan(f'🎲 랜덤 시나리오: {selected_event}')}")
        print("="*50)
        
        # 랜덤 이벤트 시뮬레이션
        print(f"예상치 못한 상황이 발생했습니다!")
        print(f"상황: {selected_event}")
        
        # 간단한 성공/실패 판정
        party_total_power = sum(
            char.physical_attack + char.magic_attack + char.speed 
            for char in self.training_party
        )
        
        success_chance = min(90, max(10, party_total_power // 20))
        is_success = random.randint(1, 100) <= success_chance
        
        print(f"\n파티 대응력: {party_total_power}")
        print(f"성공 확률: {success_chance}%")
        
        if is_success:
            print(f"🎉 성공! 상황을 잘 해결했습니다!")
            reward_type = random.choice(["경험치", "능력치", "특별 아이템"])
            print(f"보상: {reward_type} 획득!")
            
            if reward_type == "경험치":
                bonus_exp = random.randint(100, 300)
                for char in self.training_party:
                    char.experience_points = getattr(char, 'experience_points', 0) + bonus_exp
            elif reward_type == "능력치":
                bonus_stat = random.randint(3, 8)
                for char in self.training_party:
                    char.physical_attack += bonus_stat
        else:
            print(f"😅 실패... 하지만 경험을 쌓았습니다!")
            print("다음에는 더 잘할 수 있을 것입니다.")
        
        self.experiment_log.append(f"랜덤 시나리오: {selected_event} ({'성공' if is_success else '실패'})")
        input("\n계속하려면 Enter를 누르세요...")
    
    def _show_under_development(self, room_name: str):
        """개발 중 메시지"""
        print(f"{bright_yellow(f'⚠️ {room_name} 기능은 현재 개발 중입니다.')}")
        print("추후 업데이트에서 다양한 기능을 사용할 수 있게 됩니다!")
        self.experiment_log.append(f"{room_name} 방문 (개발 중)")
        input("계속하려면 Enter를 누르세요...")

# 호환성을 위해 기존 이름으로도 사용 가능
TrainingRoom = BattlegroundTrainingCenter
