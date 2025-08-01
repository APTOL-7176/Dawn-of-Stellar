"""
메타 진행 시스템 - 게임 오버 후 보상 및 해금 시스템
영구적 성장을 통한 점진적 강화
"""

import json
import os
from typing import Dict, List
from .color_text import bright_cyan, bright_yellow, bright_green, bright_red


class MetaProgression:
    """메타 진행 관리 클래스"""
    
    def __init__(self, save_file: str = "meta_progress.json"):
        self.save_file = save_file
        self.data = self.load_data()
        
    def load_data(self) -> Dict:
        """저장된 진행 데이터 로드"""
        default_data = {
            "total_runs": 0,
            "best_score": 0,
            "total_floors_cleared": 0,
            "total_enemies_defeated": 0,
            "total_items_collected": 0,
            "unlocked_classes": ["전사", "아크메이지", "궁수", "도적"],  # 시작 직업들 (4개)
            "star_fragments": 0,  # 별조각 (메타 재화)
            "star_fragments_spent": 0,  # 사용한 별조각 추적
            
            # 해금된 특성들
            "unlocked_traits": [],
            
            # 직업별 숙련도
            "class_mastery": {},
            
            # 업적
            "achievements": [],
            
            # 통계
            "statistics": {
                "longest_run": 0,
                "total_deaths": 0,
                "favorite_class": "전사",
                "most_killed_enemy": "고블린",
                "total_playtime_minutes": 0,
                "highest_damage_dealt": 0,
                "total_damage_taken": 0,
                "total_healing_done": 0,
                "items_used": 0,
                "spells_cast": 0,
                "critical_hits": 0,
                "perfect_dodges": 0,
                "boss_kills": 0,
                "treasure_chests_opened": 0,
                "gold_spent": 0,
                "levels_gained": 0,
                "fastest_floor_clear": 999999,  # 초 단위
                "consecutive_wins": 0,
                "current_win_streak": 0,
                "best_win_streak": 0,
                "death_causes": {},  # 사망 원인별 통계
                "enemy_kill_counts": {},  # 적별 처치 수
                "item_usage_counts": {},  # 아이템별 사용 횟수
                "class_death_counts": {},  # 클래스별 사망 횟수
                "floor_clear_times": []  # 층별 클리어 시간
            }
        }
        
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # 기본 데이터로 누락된 키들 채우기
                    for key, value in default_data.items():
                        if key not in loaded_data:
                            loaded_data[key] = value
                    return loaded_data
            except:
                return default_data
        return default_data
    def save_data(self):
        """진행 데이터 저장"""
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"저장 실패: {e}")
    
    # 혹시 기존 permanent_upgrades 키가 있다면 제거
    @property
    def star_fragments(self):
        """별조각 현재 보유량"""
        return self.data["star_fragments"]
    
    @property 
    def star_fragments_spent(self):
        """사용한 별조각 총량"""
        return self.data["star_fragments_spent"]
    
    @property
    def unlocked_characters(self):
        """해금된 캐릭터 목록"""
        return self.data["unlocked_classes"]
    
    @property
    def unlocked_traits(self):
        """해금된 특성 목록"""
        return self.data["unlocked_traits"]
    
    @property
    def class_mastery(self):
        """직업 숙련도 데이터"""
        return self.data["class_mastery"]
    
    @property
    def stats(self):
        """통계 데이터"""
        return self.data["stats"]
            
    def record_game_end(self, score: int, enemies_defeated: int, items_collected: int, 
                       floors_cleared: int, victory: bool = False):
        """게임 종료 시 결과 기록"""
        self.data["total_runs"] += 1
        self.data["total_floors_cleared"] = max(self.data["total_floors_cleared"], floors_cleared)
        self.data["total_enemies_defeated"] += enemies_defeated
        self.data["total_items_collected"] += items_collected
        
        if score > self.data["best_score"]:
            self.data["best_score"] = score
            
        # 보상 계산
        rewards = self.calculate_rewards(score, enemies_defeated, items_collected, floors_cleared, victory)
        self.apply_rewards(rewards)
        
        # 업적 체크
        self.check_achievements()
        
        self.save_data()
        return rewards
        
    def calculate_rewards(self, score: int, enemies_defeated: int, items_collected: int,
                         floors_cleared: int, victory: bool, world_performance=None) -> Dict:
        """보상 계산 - 성과 기반 시스템"""
        rewards = {
            "star_fragments": 0,
            "unlocked_classes": [],
            "achievements": []
        }
        
        # 새로운 성과 기반 별조각 계산
        if world_performance and hasattr(world_performance, 'get_star_fragment_reward'):
            # GameWorld의 성과 기반 계산 사용
            base_fragments = world_performance.get_star_fragment_reward()
        else:
            # 폴백: 기존 시스템보다 더 관대한 계산
            base_fragments = floors_cleared * 8 + enemies_defeated * 3 + items_collected * 2
            if victory:
                base_fragments = int(base_fragments * 1.5)  # 승리 보너스 50%
            
        # 연속 실패 보상 (어려움 보정) - 더 관대하게
        if self.data["total_runs"] > 0:
            recent_runs_bonus = min(self.data["total_runs"] * 3, 100)  # 기존 2 -> 3, 최대 50 -> 100
            base_fragments += recent_runs_bonus
            
        rewards["star_fragments"] = base_fragments
        self.data["star_fragments"] += base_fragments
        
        # 직업 해금 조건 체크
        all_classes = [
            "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크",
            "바드", "네크로맨서", "용기사", "검성", "정령술사", "암살자", "기계공학자",
            "무당", "해적", "사무라이", "드루이드", "철학자", "시간술사", "연금술사",
            "검투사", "기사", "신관", "마검사", "차원술사", "광전사"
        ]
        
        for class_name in all_classes:
            if class_name not in self.data["unlocked_classes"]:
                if self.check_class_unlock_condition(class_name):
                    self.data["unlocked_classes"].append(class_name)
                    rewards["unlocked_classes"].append(class_name)
                    
        return rewards
        
    def check_class_unlock_condition(self, class_name: str) -> bool:
        """직업 해금 조건 확인 - 별조각 기반"""
        # 기본 4개 직업은 항상 해금
        if class_name in ["전사", "아크메이지", "궁수", "도적"]:
            return True
            
        unlock_costs = {
            # 기본 확장 직업 (20-60 별조각)
            "성기사": 20,
            "암흑기사": 30,
            "몽크": 40,
            "바드": 45,
            "네크로맨서": 60,
            
            # 중급 직업 (70-150 별조각)
            "용기사": 70,
            "검성": 85,
            "정령술사": 100,
            "암살자": 120,
            "기계공학자": 150,
            
            # 고급 직업 (180-300 별조각)
            "무당": 180,
            "해적": 200,
            "사무라이": 220,
            "드루이드": 250,
            "철학자": 300,
            
            # 마스터 직업 (350-600 별조각)
            "시간술사": 350,
            "연금술사": 400,
            "검투사": 450,
            "기사": 500,
            "신관": 600,
            
            # 전설 직업 (700-1000 별조각)
            "마검사": 700,
            "차원술사": 850,
            "광전사": 1000
        }
        
        unlock_cost = unlock_costs.get(class_name)
        if unlock_cost is None:
            return False
            
        # 별조각으로 이미 해금했는지 확인
        if "unlocked_by_star_fragments" not in self.data:
            self.data["unlocked_by_star_fragments"] = {}
            
        return self.data["unlocked_by_star_fragments"].get(class_name, False)
    
    def get_character_unlock_cost(self, class_name: str) -> int:
        """캐릭터 해금 비용 반환"""
        unlock_costs = {
            # 기본 확장 직업 (20-60 별조각) - 기존 5-15에서 상향
            "성기사": 20, "암흑기사": 30, "몽크": 40, "바드": 45, "네크로맨서": 60,
            
            # 중급 직업 (70-150 별조각) - 기존 20-40에서 상향
            "용기사": 70, "검성": 85, "정령술사": 100, "암살자": 120, "기계공학자": 150,
            
            # 고급 직업 (180-300 별조각) - 기존 50-90에서 상향
            "무당": 180, "해적": 200, "사무라이": 220, "드루이드": 250, "철학자": 300,
            
            # 마스터 직업 (350-600 별조각) - 기존 100-200에서 상향
            "시간술사": 350, "연금술사": 400, "검투사": 450, "기사": 500, "신관": 600,
            
            # 전설 직업 (700-1000 별조각) - 기존 250-500에서 상향
            "마검사": 700, "차원술사": 850, "광전사": 1000
        }
        return unlock_costs.get(class_name, 0)
    
    def can_unlock_character(self, class_name: str) -> bool:
        """캐릭터 해금 가능한지 확인"""
        if self.check_class_unlock_condition(class_name):
            return False  # 이미 해금됨
            
        cost = self.get_character_unlock_cost(class_name)
        return self.data.get("star_fragments", 0) >= cost
    
    def unlock_character(self, class_name: str) -> bool:
        """별조각으로 캐릭터 해금"""
        if self.check_class_unlock_condition(class_name):
            return False  # 이미 해금됨
            
        cost = self.get_character_unlock_cost(class_name)
        if self.data.get("star_fragments", 0) < cost:
            return False  # 별조각 부족
            
        # 별조각 차감 및 해금
        self.data["star_fragments"] -= cost
        if "unlocked_by_star_fragments" not in self.data:
            self.data["unlocked_by_star_fragments"] = {}
        self.data["unlocked_by_star_fragments"][class_name] = True
        
        # 해금된 클래스 목록에도 추가
        if class_name not in self.data["unlocked_classes"]:
            self.data["unlocked_classes"].append(class_name)
            
        self.save_data()
        return True
    
    def show_character_unlock_shop(self):
        """캐릭터 해금 상점 표시 - 커서 기반"""
        try:
            from .cursor_menu_system import CursorMenu
            CURSOR_AVAILABLE = True
        except ImportError:
            CURSOR_AVAILABLE = False
        
        print(f"\n{bright_cyan('🏪 캐릭터 해금 상점')}")
        print("="*60)
        print(f"보유 별조각: {bright_yellow(str(self.data.get('star_fragments', 0)))}개")
        print("="*60)
        
        all_characters = [
            "성기사", "암흑기사", "몽크", "바드", "네크로맨서",
            "용기사", "검성", "정령술사", "암살자", "기계공학자", 
            "무당", "해적", "사무라이", "드루이드", "철학자",
            "시간술사", "연금술사", "검투사", "기사", "신관",
            "마검사", "차원술사", "광전사"
        ]
        
        # 해금 가능한 캐릭터만 필터링
        unlockable = []
        for char_name in all_characters:
            cost = self.get_character_unlock_cost(char_name)
            unlocked = self.check_class_unlock_condition(char_name)
            can_unlock = self.can_unlock_character(char_name)
            
            if unlocked:
                status = bright_green("✅ 해금됨")
            elif can_unlock:
                status = bright_yellow(f"💰 {cost}별조각")
                unlockable.append((char_name, cost))
            else:
                status = bright_red(f"❌ {cost}별조각 필요")
                
            print(f"{char_name:12} - {status}")
        
        if not unlockable:
            print(f"\n{bright_yellow('해금 가능한 캐릭터가 없습니다.')}")
            input("아무 키나 눌러 계속...")
            return
        
        if CURSOR_AVAILABLE:
            # 커서 메뉴 사용
            options = []
            descriptions = []
            
            for char_name, cost in unlockable:
                options.append(f"{char_name} ({cost} 별조각)")
                descriptions.append(f"{char_name}을 {cost} 별조각으로 해금합니다")
            
            options.append("뒤로 가기")
            descriptions.append("캐릭터 해금 상점을 나갑니다")
            
            menu = CursorMenu("🏪 캐릭터 해금", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None or result == len(options) - 1:
                return
            
            # 선택된 캐릭터 해금 처리
            char_name, cost = unlockable[result]
            
            # 확인 메뉴
            confirm_options = ["예, 해금합니다", "아니오, 취소합니다"]
            confirm_descriptions = [
                f"{char_name}을 {cost} 별조각으로 해금합니다",
                "해금을 취소하고 돌아갑니다"
            ]
            
            confirm_menu = CursorMenu(
                f"{char_name} 해금 확인\n현재 보유: {self.data.get('star_fragments', 0)} 별조각",
                confirm_options, confirm_descriptions
            )
            confirm_result = confirm_menu.run()
            
            if confirm_result == 0:  # 예
                if self.unlock_character(char_name):
                    print(f"\n{bright_green('✅')} {char_name}이(가) 해금되었습니다!")
                else:
                    print(f"\n{bright_red('❌')} 해금에 실패했습니다.")
                input("아무 키나 눌러 계속...")
        else:
            # 폴백: 기존 텍스트 방식
            print("\n해금 가능한 캐릭터:")
            for idx, (char_name, cost) in enumerate(unlockable, 1):
                print(f"{idx}. {char_name} ({cost} 별조각)")
                
            print("0. 돌아가기")
            
            try:
                choice = input("\n해금할 캐릭터 번호: ").strip()
                if choice == '0':
                    return
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(unlockable):
                        char_name, cost = unlockable[idx]
                        confirm = input(f"{char_name}을(를) {cost} 별조각으로 해금하시겠습니까? (y/n): ").strip().lower()
                        if confirm in ['y', 'yes', 'ㅇ']:
                            if self.unlock_character(char_name):
                                print(f"✅ {char_name}이(가) 해금되었습니다!")
                            else:
                                print("❌ 해금에 실패했습니다.")
                        else:
                            print("해금이 취소되었습니다.")
                    else:
                        print("❌ 잘못된 선택입니다.")
                else:
                    print("❌ 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 잘못된 입력입니다.")
                
            input("아무 키나 눌러 계속...")
    
    def get_trait_description(self, trait_name: str) -> str:
        """특성 설명 반환"""
        descriptions = {
            # 기본 전투 특성
            "불굴의 의지": "체력이 낮을 때 방어력과 회복력이 증가합니다",
            "피의 갈증": "적을 처치할 때마다 공격력이 일시적으로 증가합니다",
            "전투 광기": "전투 중 받은 피해에 비례하여 공격 속도가 증가합니다",
            "위협적 존재": "적들이 먼저 공격할 확률이 감소합니다",
            "방어 숙련": "모든 방어력이 15% 증가하고 피해 감소 효과가 향상됩니다",
            "빠른 손놀림": "공격 속도와 회피율이 12% 증가합니다",
            "치명적 급소": "크리티컬 확률이 20% 증가하고 크리티컬 데미지가 증가합니다",
            "전투 본능": "전투 시작 시 모든 능력치가 일시적으로 향상됩니다",
            "생존 의지": "체력이 1이 될 상황에서 한 번 버틸 수 있습니다",
            "전투 흥분": "연속 공격 시 데미지가 누적되어 증가합니다",
            "고통 무시": "상처로 인한 최대 체력 제한이 완화됩니다",
            "무모한 돌진": "체력이 낮을수록 이동 속도와 공격력이 증가합니다",
            
            # 기본 마법 특성
            "마력 집중": "마법 공격력이 18% 증가하고 MP 효율이 향상됩니다",
            "마나 순환": "MP 자동 회복 속도가 50% 증가합니다",
            "원소 지배": "모든 속성 마법의 위력이 25% 증가합니다",
            "마법 폭주": "마법 사용 시 일정 확률로 MP 소모 없이 연속 시전 가능합니다",
            "마법 연구자": "마법 스킬 습득 속도가 빨라지고 더 강력한 마법을 익힐 수 있습니다",
            "마나 효율": "모든 마법의 MP 소모량이 20% 감소합니다",
            "시전 가속": "마법 시전 시간이 30% 단축됩니다",
            "원소 이해": "속성 상성 효과가 2배로 증가합니다",
            "실험 정신": "마법 실험을 통해 새로운 효과를 발견할 수 있습니다",
            "마법 저항": "적의 마법 공격에 대한 저항력이 크게 증가합니다",
            "어둠 친화": "어둠 속성 마법의 위력이 40% 증가하고 부작용이 감소합니다",
            "정령 친화": "정령과의 계약을 통해 추가 마법 효과를 얻을 수 있습니다",
            
            # 기본 사격/은신 특성
            "정밀 사격": "원거리 공격의 명중률이 25% 증가하고 크리티컬 확률이 상승합니다",
            "연발 사격": "연속 공격 시 공격 속도가 점진적으로 증가합니다",
            "관통 사격": "원거리 공격이 적을 관통하여 추가 타겟에게도 피해를 줍니다",
            "독수리의 눈": "적의 약점을 간파하여 크리티컬 데미지가 크게 증가합니다",
            "민첩한 몸놀림": "회피율이 20% 증가하고 이동 속도가 향상됩니다",
            "원거리 숙련": "모든 원거리 공격의 데미지가 22% 증가합니다",
            "바람의 가호": "바람의 힘으로 공격 속도와 이동 속도가 증가합니다",
            "사냥꾼의 직감": "적의 위치와 상태를 미리 감지할 수 있습니다",
            "그림자 이동": "그림자를 통해 순간이동하여 기습 공격이 가능합니다",
            "독 마스터": "독 공격의 위력이 증가하고 독 저항력을 얻습니다",
            "일격필살": "낮은 확률로 즉사 공격이 발동할 수 있습니다",
            "은신 숙련": "은신 상태에서의 공격력이 크게 증가하고 발각 확률이 감소합니다",
            "그림자 은신": "그림자에 숨어 적의 시야에서 완전히 사라질 수 있습니다",
            "독 숙련": "독 데미지가 증가하고 독에 면역이 됩니다",
            "도적의 직감": "함정과 비밀을 감지하고 보물을 찾을 확률이 증가합니다",
            "치명타 특화": "크리티컬 공격 시 추가 효과가 발동할 수 있습니다",
            
            # 중급 특성들
            "성스러운 가호": "신성한 보호막이 마법 공격을 막아줍니다",
            "신의 축복": "모든 능력치가 성스러운 힘으로 강화됩니다",
            "치유의 빛": "치유 효과가 50% 증가하고 상처 회복 속도가 빨라집니다",
            "정화의 힘": "상태이상을 치료하고 예방하는 능력이 생깁니다",
            "신성한 가호": "언데드와 악마에게 주는 피해가 2배 증가합니다",
            "축복받은 무기": "무기에 성스러운 힘이 깃들어 추가 피해를 줍니다",
            "수호의 맹세": "파티원을 보호할 때 방어력이 크게 증가합니다",
            "정의의 분노": "악한 적을 상대할 때 공격력이 크게 증가합니다",
            "생명 흡수": "공격 시 일정량의 체력을 회복합니다",
            "어둠의 계약": "어둠의 힘을 빌려 강력한 능력을 얻습니다",
            "불사의 의지": "한 번 죽어도 부활할 수 있는 기회를 얻습니다",
            "어둠 조작": "그림자를 조작하여 다양한 공격과 방어가 가능합니다",
            "공포 오라": "주변 적들이 공포에 떨어 능력이 감소합니다",
            "광폭화": "체력이 낮을 때 공격력과 공격 속도가 크게 증가합니다",
            "베르세르크": "이성을 잃고 엄청난 전투력을 발휘합니다",
            "분노의 일격": "분노가 쌓일수록 더 강력한 공격을 가할 수 있습니다",
            
            # 고급 특성들
            "전투 마스터": "모든 전투 기술이 마스터 수준에 도달합니다",
            "무기 마스터": "모든 무기를 완벽하게 다룰 수 있습니다",
            "완벽한 공격": "공격이 절대 빗나가지 않고 항상 최대 데미지를 냅니다",
            "최고의 방어": "모든 공격을 완벽하게 방어할 수 있습니다",
            "마법 마스터": "모든 마법 계열의 최고 단계에 도달합니다",
            "원소 조화": "모든 원소를 자유자재로 조합하여 사용할 수 있습니다",
            "마나 무한": "MP가 무한히 재생되어 마법을 제한 없이 사용합니다",
            "시전 가속": "마법을 즉시 시전할 수 있고 연속 시전이 가능합니다",
            
            # 전설 특성들
            "시간 조작": "시간의 흐름을 조작하여 전투를 유리하게 이끕니다",
            "공간 지배": "공간을 조작하여 순간이동과 차원 공격이 가능합니다",
            "차원 이동": "다른 차원으로 이동하여 공격을 피하고 기습할 수 있습니다",
            "현실 조작": "현실 자체를 조작하여 불가능을 가능하게 만듭니다",
            "불멸의 혼": "영혼이 불멸하여 어떤 공격으로도 완전히 죽지 않습니다",
            "절대 재생": "어떤 상처도 즉시 재생되어 불사의 몸을 얻습니다",
            "무적의 몸": "모든 물리적 공격에 완전 면역이 됩니다",
            "영원한 생명": "시간의 영향을 받지 않는 영원한 존재가 됩니다",
            "무한의 힘": "무한한 힘을 얻어 어떤 적도 일격에 쓰러뜨립니다",
            "절대 파괴": "어떤 방어도 무시하는 절대적인 파괴력을 얻습니다",
            "신의 권능": "신과 같은 절대적인 권능을 행사할 수 있습니다",
            "창조와 파괴": "무에서 유를 창조하고 유를 무로 돌릴 수 있습니다",
            "완벽한 예지": "미래를 완벽하게 예견하여 모든 공격을 회피합니다",
            "운명 조작": "운명 자체를 조작하여 결과를 바꿀 수 있습니다",
            "인과 조작": "원인과 결과의 관계를 조작할 수 있습니다",
            "존재 초월": "모든 존재의 한계를 초월한 궁극의 존재가 됩니다",
            
            # 장비/도구 관련 특성 설명 (더욱 상세하고 매력적으로)
            "장비 수호자": "🛡️ 마법적 보호막이 장비를 감싸 내구도 감소 확률을 25% 감소시킵니다 [전사, 성기사 전용]",
            "단조 마스터": "🪡 신화급 대장장이의 솜씨로 장비 최대 내구도를 20% 증가시킵니다 [기계공학자, 드워프 전용]",
            "장비 분석가": "🕶️ 고급 분석술로 필드에서 장비 상태를 정확히 파악하고 MP 소모 50% 감소 [철학자, 연금술사 전용]",
            "장인의 혼": "✨ 전설의 장인 혼이 깃들어 수리 시 추가로 10%의 내구도가 더 회복됩니다 [사무라이, 무당 전용]",
            "완벽주의자": "🎯 장비를 80% 이상 내구도로 유지할 때 완벽함의 힘으로 모든 능력치가 5% 증가합니다 [검성, 철학자 전용]",
            "강철 의지": "⚔️ 불굴의 의지로 장비 손상이 50% 느려지고 수리 비용이 30% 감소합니다 [전사, 기사 전용]",
            "절대 보존": "💎 절대적인 보존술로 장비가 절대 파괴되지 않고 최소 1 내구도를 유지합니다 [시간술사, 차원술사 전용]"
        }
        return descriptions.get(trait_name, "신비로운 힘을 가진 특성입니다")

    def get_trait_unlock_cost(self, trait_name: str) -> int:
        """특성 해금 비용 반환 - 실제 게임에 존재하는 특성만"""
        trait_costs = {
            # 기본 전투 특성 (5-20 별조각) - 게임에 실제 존재하는 특성
            "불굴의 의지": 5, "피의 갈증": 8, "전투 광기": 10, "위협적 존재": 12,
            "방어 숙련": 6, "빠른 손놀림": 7, "치명적 급소": 12, "전투 본능": 8,
            "생존 의지": 10, "전투 흥분": 15, "고통 무시": 18, "무모한 돌진": 20,
            
            # 기본 마법 특성 (5-20 별조각)
            "마력 집중": 8, "마나 순환": 10, "원소 지배": 15, "마법 폭주": 18,
            "마법 연구자": 12, "마나 효율": 9, "원소 이해": 16, "실험 정신": 11,
            "마법 저항": 13, "어둠 친화": 17, "정령 친화": 15,
            
            # 기본 사격/은신 특성 (5-20 별조각)
            "정밀 사격": 5, "민첩한 몸놀림": 7, "원거리 숙련": 10, "바람의 가호": 13,
            "사냥꾼의 직감": 16, "그림자 이동": 10, "독 마스터": 12, "일격필살": 20,
            "은신 숙련": 15, "그림자 은신": 14, "독 숙련": 11, "도적의 직감": 18,
            "치명타 특화": 19,
            
            # 중급 성직자/성기사 특성 (15-50 별조각)
            "치유의 빛": 25, "신성한 가호": 22, "축복받은 무기": 28, "수호의 맹세": 35,
            "정의의 분노": 40, "생명 흡수": 18, "어둠의 계약": 25, "불사의 의지": 32,
            "어둠 조작": 38, "공포 오라": 45,
            
            # 중급 직업 특성 (15-50 별조각)
            "내공 순환": 16, "연타 숙련": 22, "정신 수양": 28, "참선의 깨달음": 34,
            "기절 공격": 40, "영감 부여": 18, "다중 주문": 24, "재생의 노래": 30,
            "카리스마": 36, "언데드 소환": 25, "영혼 조작": 32, "생명력 흡수": 38,
            "공포 유발": 44, "용의 분노": 30, "비늘 방어": 35, "용의 숨결": 42,
            
            # 중급 전문 특성 (20-60 별조각)
            "무한 검기": 25, "카타나 숙련": 20, "검기 방출": 30, "검의 춤": 35,
            "무사도": 40, "정령 소환": 28, "자연과의 대화": 33, "영적 보호": 26,
            "자연 치유": 31, "영혼 시야": 36, "악령 퇴치": 41, "신령 소통": 46,
            "해적 코드": 22, "선상 전투": 27, "보물 탐지": 32, "해상 경험": 37,
            
            # 고급 특성 (40-120 별조각)
            "운명의 바람": 52, "명예의 길": 48, "집중력": 55, "고대의 지혜": 65,
            "자연의 가호": 58, "야생 동조": 63, "동물 친화": 68, "식물 성장": 75,
            "깊은 사고": 60, "지혜의 힘": 70, "논리적 분석": 80, "정신 집중": 85,
            "학자의 직감": 90, "기계 소환": 62, "발명가": 72, "기계 친화": 82,
            "수리 기술": 87, "창의성": 95, "물질 변환": 78, "연금술 숙련": 88,
            
            # 전설 특성 (100-400 별조각)
            "시간 조작": 100, "인과 조작": 200, "시간 정지": 140, "예지력": 160,
            "시공간 이해": 180, "포션 제작": 120, "검투 기술": 125, "관중 어필": 145,
            "명성": 165, "기사도": 130, "충성심": 150, "중무장": 170,
            "기마술": 190, "귀족의 품격": 210, "신성한 힘": 135, "축복": 155,
            "치유 마법": 175, "정화": 195, "신앙": 220, "마검 조화": 140,
            "이중 숙련": 160, "마법 검술": 180, "원소 부여": 200, "균형 감각": 225,
            "차원 이동": 240, "공간 왜곡": 240, "차원 균열": 260, "무한 지식": 280,
            "광기 상태": 160, "분노": 180,
            
            # 장비/도구 관련 특성 (비용 대폭 증가 - 20-150 별조각)
            "장비 수호자": 20, "단조 마스터": 35, "장비 분석가": 50, "장인의 혼": 75,
            "완벽주의자": 100, "강철 의지": 125, "절대 보존": 150
        }
        return trait_costs.get(trait_name, 50)  # 기본값 50
    
    def get_trait_description(self, trait_name: str) -> str:
        """특성 설명 반환"""
        trait_descriptions = {
            # 전사 특성 (실제 구현 기준)
            "불굴의 의지": "HP가 25% 이하일 때 공격력 50% 증가",
            "전투 광기": "적을 처치할 때마다 다음 공격의 피해량 20% 증가",
            "방어 숙련": "방어 시 받는 피해 30% 추가 감소",
            "위협적 존재": "전투 시작 시 적들의 공격력 10% 감소",
            "피의 갈증": "HP가 50% 이상일 때 공격속도 25% 증가",
            
            # 아크메이지 특성
            "마나 순환": "스킬 사용 시 30% 확률로 MP 소모량 절반",
            "원소 지배": "속성 마법 사용 시 해당 속성 저항 20% 증가",
            "마법 연구자": "전투 후 획득 경험치 15% 증가",
            "마법 폭주": "크리티컬 마법 시 주변 적들에게 연쇄 피해",
            "마력 집중": "MP가 75% 이상일 때 마법 피해 40% 증가",
            
            # 궁수 특성
            "정밀 사격": "크리티컬 확률 25% 증가",
            "원거리 숙련": "첫 공격 시 항상 크리티컬",
            "민첩한 몸놀림": "회피 확률 20% 증가",
            "사냥꾼의 직감": "적의 약점을 간파해 방어력 무시 확률 15%",
            "바람의 가호": "이동 시 다음 공격의 명중률과 피해량 15% 증가",
            
            # 장비/도구 관련 특성
            "장비 수호자": "🛡️ 마법적 보호막이 장비를 감싸 내구도 감소 확률을 25% 감소",
            "단조 마스터": "🔨 신화급 대장장이의 솜씨로 장비 최대 내구도를 20% 증가",
            "장비 분석가": "🔍 고급 분석술로 필드에서 장비 상태를 정확히 파악하고 MP 소모 50% 감소",
            "장인의 혼": "✨ 전설의 장인 혼이 깃들어 수리 시 추가로 10%의 내구도가 더 회복",
            "완벽주의자": "🎯 장비를 80% 이상 내구도로 유지할 때 완벽함의 힘으로 모든 능력치가 5% 증가",
            "강철 의지": "⚔️ 불굴의 의지로 장비 손상이 50% 느려지고 수리 비용이 30% 감소",
            "절대 보존": "💎 절대적인 보존술로 장비가 절대 파괴되지 않고 최소 1 내구도를 유지",
            
            # 도적 특성
            "그림자 은신": "전투 시작 시 3턴간 은신 상태",
            "치명적 급소": "크리티컬 시 추가 출혈 효과 부여",
            "빠른 손놀림": "아이템 사용 시 턴 소모하지 않음",
            "도적의 직감": "함정과 보물 발견 확률 50% 증가",
            "독 숙련": "모든 공격에 10% 확률로 독 효과 추가",
            
            # 성기사 특성
            "신성한 가호": "언데드와 악마에게 받는 피해 50% 감소",
            "치유의 빛": "공격 시 30% 확률로 파티원 전체 소량 회복",
            "정의의 분노": "아군이 쓰러질 때 공격력과 마법력 30% 증가",
            "축복받은 무기": "모든 공격에 성속성 추가 피해",
            "수호의 맹세": "파티원 보호 시 받는 피해 50% 감소",
            
            # 암흑기사 특성
            "생명 흡수": "가한 피해의 15%만큼 HP 회복",
            "어둠의 계약": "HP가 낮을수록 공격력 증가 (최대 100%)",
            "공포 오라": "적들이 간헐적으로 행동 불가",
            "불사의 의지": "치명상 시 1회 한정 완전 회복",
            "어둠 조작": "턴 종료 시 20% 확률로 적에게 암속성 피해",
            
            # 다른 특성들도 실제 구현에 맞게 수정 필요
            # (여기서는 주요 클래스만 수정, 나머지는 점진적으로 수정)
            
            # 내구도 관련 특성 (업데이트된 설명)
            "장비 보호": "🛡️ 마법적 보호막이 장비를 감싸 내구도 감소 확률을 25% 감소시킵니다",
            "내구도 강화": "💎 장비의 분자 구조를 강화하여 최대 내구도를 20% 증가시킵니다",
            "수리 전문가": "🔧 숙련된 수리 기술로 필드 수리 효과가 50% 증가하고 MP 소모가 25% 감소합니다",
            "장인의 손길": "✨ 마스터 장인의 솜씨로 수리 시 추가로 10%의 내구도가 더 회복됩니다",
            "완벽주의": "🎯 장비를 80% 이상 내구도로 유지할 때 완벽함의 힘으로 모든 능력치가 5% 증가합니다",
            "내구성 마스터": "👑 내구도의 달인이 되어 장비 손상이 50% 느려지고 수리 비용이 30% 감소합니다",
            "불굴의 장비": "⚡ 불굴의 의지가 깃든 장비는 절대 파괴되지 않고 최소 1 내구도를 유지합니다",
            
            # 도적 특성
            "그림자 이동": "은신 시 이동 속도가 50% 증가",
            "독 마스터": "독 데미지가 40% 증가하고 지속시간 연장",
            "일격필살": "기습 공격 시 치명타 데미지 100% 증가",
            "은신 숙련": "은신 지속시간이 50% 증가",
            "그림자 은신": "은신 중 마나가 지속적으로 회복",
            "독 숙련": "독 상태이상 저항력 50% 증가",
            "도적의 직감": "함정과 비밀 통로를 더 쉽게 발견",
            "치명타 특화": "치명타 발생 시 다음 공격도 치명타",
            
            # 성기사 특성
            "치유의 빛": "치유 스킬의 효과가 30% 증가",
            "신성한 가호": "언데드에게 받는 데미지 50% 감소",
            "축복받은 무기": "무기 공격에 신성 속성 추가",
            "수호의 맹세": "파티원 보호 시 받는 데미지 30% 감소",
            "정의의 분노": "악 속성 적에게 데미지 50% 증가",
            
            # 암흑기사 특성
            "생명 흡수": "공격 시 데미지의 15%만큼 HP 회복",
            "어둠의 계약": "HP를 소모하여 강력한 공격 사용 가능",
            "불사의 의지": "죽음 직전에 한 번 HP 1로 부활",
            "어둠 조작": "어둠 속성 스킬의 데미지 40% 증가",
            "공포 오라": "주변 적들을 공포 상태로 만듦",
            
            # 몽크 특성
            "내공 순환": "스킬 사용 후 마나가 점진적으로 회복",
            "연타 숙련": "연속 공격 시 속도가 점진적으로 증가",
            "정신 수양": "상태이상 저항력이 40% 증가",
            "참선의 깨달음": "경험치 획득량이 25% 증가",
            "기절 공격": "공격 시 20% 확률로 적을 기절시킴",
            
            # 바드 특성
            "영감 부여": "파티원들의 능력치를 15% 상승시킴",
            "다중 주문": "스킬 사용 시 30% 확률로 쿨다운 없음",
            "재생의 노래": "지속적으로 파티원들의 HP와 마나 회복",
            "카리스마": "상인과의 거래에서 더 좋은 조건 획득",
            
            # 네크로맨서 특성
            "언데드 소환": "처치한 적을 일시적으로 아군으로 소환",
            "영혼 조작": "적의 영혼을 조작하여 혼란 상태로 만듦",
            "생명력 흡수": "적에게 데미지를 줄 때 HP 회복",
            "공포 유발": "적들을 공포에 빠뜨려 도망가게 만듦",
            
            # 용기사 특성
            "용의 분노": "HP가 낮을수록 공격력이 증가",
            "비늘 방어": "물리 데미지를 20% 감소",
            "용의 숨결": "화염 속성 공격의 데미지 50% 증가",
            
            # 검성 특성
            "무한 검기": "검 스킬의 사거리와 데미지 증가",
            "카타나 숙련": "검 무기 사용 시 치명타율 25% 증가",
            "검기 방출": "원거리에서도 검 공격 가능",
            "검의 춤": "연속 공격 시 회피율 증가",
            "무사도": "HP가 낮을 때 모든 능력치 상승",
            
            # 정령술사 특성
            "정령 소환": "전투 중 정령을 소환하여 지원",
            "자연과의 대화": "자연 환경에서 능력치 보너스",
            "영적 보호": "마법 데미지를 25% 감소",
            "자연 치유": "자연 환경에서 HP 지속 회복",
            
            # 암살자 특성
            "영혼 시야": "은신한 적과 함정을 감지",
            "악령 퇴치": "언데드와 악령에게 추가 데미지",
            "신령 소통": "정령들로부터 정보와 도움 획득",
            
            # 기계공학자 특성
            "기계 소환": "전투용 기계를 소환하여 지원",
            "발명가": "아이템 제작 시 성공률과 품질 향상",
            "기계 친화": "기계 적들에게 받는 데미지 감소",
            "수리 기술": "장비 내구도 소모량 감소",
            "창의성": "독특한 아이템 조합으로 새로운 효과 창조",
            
            # 무당 특성
            "영혼 시야": "숨겨진 비밀과 적의 약점 파악",
            "악령 퇴치": "악한 존재들에게 강력한 데미지",
            "신령 소통": "신령들의 가호로 특별한 능력 획득",
            
            # 해적 특성
            "해적 코드": "동료와의 협력 시 능력치 보너스",
            "선상 전투": "좁은 공간에서의 전투 능력 향상",
            "보물 탐지": "숨겨진 보물과 비밀 방 발견 확률 증가",
            "해상 경험": "다양한 환경에 빠르게 적응",
            
            # 사무라이 특성
            "운명의 바람": "중요한 순간에 운이 따름",
            "명예의 길": "정직한 전투에서 능력치 보너스",
            
            # 드루이드 특성
            "자연의 가호": "자연 환경에서 모든 능력치 상승",
            "야생 동조": "야생 동물들과 소통하고 도움 받음",
            "동물 친화": "동물형 적들과 평화적 해결 가능",
            "식물 성장": "식물을 성장시켜 길을 만들거나 방어벽 생성",
            
            # 철학자 특성
            "집중력": "스킬 사용 시 실패 확률 감소",
            "고대의 지혜": "고대 문명의 지식으로 비밀 해독",
            "깊은 사고": "복잡한 퍼즐과 수수께끼 해결 능력",
            "지혜의 힘": "지식을 이용해 적의 약점 파악",
            "논리적 분석": "상황을 논리적으로 분석하여 최적해 도출",
            "정신 집중": "정신력 관련 저항 능력 향상",
            "학자의 직감": "학문적 통찰로 숨겨진 진실 발견",
            
            # 시간술사 특성
            "시간 조작": "시간의 흐름을 조작하여 전투 유리하게 만듦",
            "인과 조작": "운명을 조작하여 확률 조정",
            "시간 정지": "짧은 시간 동안 시간을 정지시킴",
            "예지력": "미래를 예견하여 위험 회피",
            "시공간 이해": "시공간의 비밀을 이해하여 특별한 능력 획득",
            
            # 연금술사 특성
            "포션 제작": "더 강력한 포션 제작 가능",
            "물질 변환": "물질을 다른 물질로 변환",
            "연금술 숙련": "연금술 실험 성공률 대폭 향상",
            
            # 검투사 특성
            "검투 기술": "관중이 있을 때 능력치 대폭 상승",
            "관중 어필": "화려한 기술로 적을 압도",
            "명성": "명성이 높아질수록 더 강해짐",
            
            # 기사 특성
            "기사도": "정정당당한 전투에서 모든 능력 향상",
            "충성심": "동료를 위해 싸울 때 추가 보너스",
            "중무장": "무거운 장비 착용 시 방어력 대폭 증가",
            "기마술": "이동 관련 능력 향상",
            "귀족의 품격": "사회적 상호작용에서 유리함",
            
            # 신관 특성
            "신성한 힘": "신성 마법의 위력 대폭 증가",
            "축복": "파티원들에게 강력한 축복 부여",
            "치유 마법": "치유 능력이 극도로 강화됨",
            "정화": "모든 상태이상과 저주 해제 가능",
            "신앙": "신앙심이 깊을수록 더 강한 기적 발현",
            
            # 마검사 특성
            "마검 조화": "마법과 검술의 완벽한 조화",
            "이중 숙련": "마법과 물리 공격 모두 마스터",
            "마법 검술": "검에 마법을 부여하여 공격",
            "원소 부여": "무기에 다양한 원소 속성 부여",
            "균형 감각": "마법과 물리의 균형으로 안정성 증가",
            
            # 차원술사 특성
            "차원 이동": "순간이동으로 전장을 자유자재로 이동",
            "공간 왜곡": "공간을 왜곡하여 적의 공격 무효화",
            "차원 균열": "차원의 균열을 만들어 강력한 공격",
            "무한 지식": "다른 차원의 지식에 접근",
            
            # 광전사 특성
            "광기 상태": "HP가 낮을수록 공격력과 속도 극대화",
            "분노": "데미지를 받을수록 더 강해짐"
        }
        return trait_descriptions.get(trait_name, "특별한 능력을 부여하는 특성입니다.")
    
    def get_trait_class_restrictions(self, trait_name: str) -> List[str]:
        """특성별 직업 제한 반환"""
        class_restrictions = {
            # 장비/도구 관련 특성
            "장비 수호자": ["전사", "성기사"],
            "단조 마스터": ["기계공학자", "드워프"],
            "장비 분석가": ["철학자", "연금술사"],
            "장인의 혼": ["사무라이", "무당"],
            "완벽주의자": ["검성", "철학자"],
            "강철 의지": ["전사", "기사"],
            "절대 보존": ["시간술사", "차원술사"],
            
            # 기본 특성들은 제한 없음
            "불굴의 의지": [],
            "전투 광기": [],
            "방어 숙련": [],
            "마나 순환": [],
            "원소 지배": [],
            "정밀 사격": [],
            "그림자 은신": [],
            # ... 다른 기본 특성들도 제한 없음
        }
        return class_restrictions.get(trait_name, [])
    
    def can_unlock_trait(self, trait_name: str, player_classes: List[str] = None) -> bool:
        """특성 해금 가능한지 확인 (직업 제한 포함)"""
        if "unlocked_traits" not in self.data:
            self.data["unlocked_traits"] = []
            
        if trait_name in self.data["unlocked_traits"]:
            return False  # 이미 해금됨
        
        # 직업 제한 확인
        restricted_classes = self.get_trait_class_restrictions(trait_name)
        if restricted_classes and player_classes:
            # 플레이어가 해당 직업 중 하나라도 해금했는지 확인
            unlocked_classes = self.data.get("unlocked_classes", [])
            has_required_class = any(cls in unlocked_classes for cls in restricted_classes)
            if not has_required_class:
                return False  # 필요한 직업이 해금되지 않음
            
        cost = self.get_trait_unlock_cost(trait_name)
        return self.data.get("star_fragments", 0) >= cost
    
    def unlock_trait(self, trait_name: str) -> bool:
        """별조각으로 특성 해금"""
        if "unlocked_traits" not in self.data:
            self.data["unlocked_traits"] = []
            
        if trait_name in self.data["unlocked_traits"]:
            return False  # 이미 해금됨
            
        cost = self.get_trait_unlock_cost(trait_name)
        if self.data.get("star_fragments", 0) < cost:
            return False  # 별조각 부족
            
        # 별조각 차감 및 해금
        self.data["star_fragments"] -= cost
        self.data["unlocked_traits"].append(trait_name)
        self.save_data()
        return True
    
    def is_trait_unlocked(self, trait_name: str) -> bool:
        """특성이 해금되었는지 확인"""
        if "unlocked_traits" not in self.data:
            self.data["unlocked_traits"] = []
        return trait_name in self.data["unlocked_traits"]
    
    def get_unlocked_traits(self) -> List[str]:
        """해금된 특성 목록 반환"""
        if "unlocked_traits" not in self.data:
            self.data["unlocked_traits"] = []
        return self.data["unlocked_traits"].copy()
    
    def show_trait_unlock_shop(self):
        """특성 해금 상점 표시 - 커서 기반"""
        try:
            from .cursor_menu_system import CursorMenu
            CURSOR_AVAILABLE = True
        except ImportError:
            CURSOR_AVAILABLE = False
        
        print(f"\n{bright_cyan('🎭 특성 해금 상점')}")
        print("="*60)
        print(f"보유 별조각: {bright_yellow(str(self.data.get('star_fragments', 0)))}개")
        print("="*60)
        
        all_traits = [
            # 기본 전투 특성 (24개)
            "불굴의 의지", "피의 갈증", "전투 광기", "위협적 존재",
            "방어 숙련", "빠른 손놀림", "치명적 급소", "전투 본능",
            "생존 의지", "전투 흥분", "고통 무시", "무모한 돌진",
            "마력 집중", "마나 순환", "원소 지배", "마법 폭주",
            "마법 연구자", "마나 효율", "시전 가속", "원소 이해",
            "정밀 사격", "연발 사격", "관통 사격", "독수리의 눈",
            
            # 중급 특성 (32개)
            "성스러운 가호", "신의 축복", "치유의 빛", "정화의 힘",
            "신성한 가호", "축복받은 무기", "수호의 맹세", "정의의 분노",
            "생명 흡수", "어둠의 계약", "불사의 의지", "어둠 조작",
            "공포 오라", "광폭화", "베르세르크", "분노의 일격",
            "내공 순환", "연타 숙련", "정신 수양", "참선의 깨달음",
            "기절 공격", "영감 부여", "다중 주문", "재생의 노래",
            "카리스마", "언데드 소환", "영혼 조작", "생명력 흡수",
            "공포 유발", "용의 분노", "비늘 방어", "용의 숨결",
            
            # 고급 특성 (40개)
            "전투 마스터", "무기 마스터", "완벽한 공격", "최고의 방어",
            "마법 마스터", "원소 조화", "마나 무한", "시전 가속",
            "완벽한 조준", "절대 명중", "다중 사격", "궁극의 화살",
            "암살 마스터", "그림자 지배", "치명적 독", "절대 은신",
            "무한 검기", "카타나 숙련", "검기 방출", "검의 춤",
            "무사도", "정령 소환", "자연과의 대화", "영적 보호",
            "자연 치유", "영혼 시야", "악령 퇴치", "신령 소통",
            "해적 코드", "선상 전투", "보물 탐지", "해상 경험",
            "운명의 바람", "명예의 길", "집중력", "고대의 지혜",
            "자연의 가호", "야생 동조", "동물 친화", "식물 성장",
            
            # 전설 특성 (44개)
            "시간 조작", "공간 지배", "차원 이동", "현실 조작",
            "불멸의 혼", "절대 재생", "무적의 몸", "영원한 생명",
            "무한의 힘", "절대 파괴", "신의 권능", "창조와 파괴",
            "완벽한 예지", "운명 조작", "인과 조작", "존재 초월",
            "깊은 사고", "지혜의 힘", "논리적 분석", "정신 집중",
            "학자의 직감", "기계 소환", "발명가", "기계 친화",
            "수리 기술", "창의성", "물질 변환", "연금술 숙련",
            "포션 제작", "시간 정지", "예지력", "시공간 이해",
            "검투 기술", "관중 어필", "명성", "기사도",
            "충성심", "중무장", "기마술", "귀족의 품격",
            "신성한 힘", "축복", "치유 마법", "정화"
        ]
        
        # 등급별로 분류 (각 등급별로 동일한 수로 나누기)
        basic_traits = all_traits[:24]      # 기본 특성 24개
        intermediate_traits = all_traits[24:56]  # 중급 특성 32개  
        advanced_traits = all_traits[56:96]      # 고급 특성 40개
        legendary_traits = all_traits[96:]       # 전설 특성 44개
        
        categories = [
            ("기본 특성", basic_traits, bright_green),
            ("중급 특성", intermediate_traits, bright_yellow),
            ("고급 특성", advanced_traits, bright_red),
            ("전설 특성", legendary_traits, bright_cyan)
        ]
        
        if CURSOR_AVAILABLE:
            # 커서 메뉴 사용 - 등급별 선택
            category_options = []
            category_descriptions = []
            
            for category_name, traits, color_func in categories:
                unlockable_count = 0
                for trait_name in traits:
                    if self.can_unlock_trait(trait_name):
                        unlockable_count += 1
                
                if unlockable_count > 0:
                    category_options.append(f"{category_name} ({unlockable_count}개 해금 가능)")
                    category_descriptions.append(f"{category_name} 특성들을 확인합니다")
            
            if not category_options:
                print(f"\n{bright_yellow('해금 가능한 특성이 없습니다.')}")
                input("아무 키나 눌러 계속...")
                return
            
            category_options.append("뒤로 가기")
            category_descriptions.append("특성 해금 상점을 나갑니다")
            
            category_menu = CursorMenu("🎭 특성 등급 선택", category_options, category_descriptions, cancellable=True)
            category_result = category_menu.run()
            
            if category_result is None or category_result == len(category_options) - 1:
                return
            
            # 선택된 등급의 특성들 표시
            selected_category = categories[category_result]
            category_name, traits, color_func = selected_category
            
            trait_options = []
            trait_descriptions = []
            unlockable_traits = []
            
            for trait_name in traits:
                cost = self.get_trait_unlock_cost(trait_name)
                unlocked = self.is_trait_unlocked(trait_name)
                can_unlock = self.can_unlock_trait(trait_name)
                restrictions = self.get_trait_class_restrictions(trait_name)
                
                if can_unlock:
                    trait_display = f"{trait_name} ({cost} 별조각)"
                    if restrictions:
                        trait_display += f" [{', '.join(restrictions)} 전용]"
                    trait_options.append(trait_display)
                    
                    description = f"{self.get_trait_description(trait_name)}"
                    if restrictions:
                        description += f"\n직업 제한: {', '.join(restrictions)}"
                    trait_descriptions.append(description)
                    unlockable_traits.append((trait_name, cost))
            
            if not trait_options:
                print(f"\n{bright_yellow(f'{category_name}에서 해금 가능한 특성이 없습니다.')}")
                input("아무 키나 눌러 계속...")
                return
            
            trait_options.append("뒤로 가기")
            trait_descriptions.append("등급 선택으로 돌아갑니다")
            
            trait_menu = CursorMenu(f"🎭 {category_name}", trait_options, trait_descriptions, cancellable=True)
            trait_result = trait_menu.run()
            
            if trait_result is None or trait_result == len(trait_options) - 1:
                return
            
            # 선택된 특성 해금 처리
            trait_name, cost = unlockable_traits[trait_result]
            
            # 확인 메뉴
            confirm_options = ["예, 해금합니다", "아니오, 취소합니다"]
            confirm_descriptions = [
                f"{trait_name}을 {cost} 별조각으로 해금합니다",
                "해금을 취소하고 돌아갑니다"
            ]
            
            confirm_menu = CursorMenu(
                f"{trait_name} 해금 확인\n현재 보유: {self.data.get('star_fragments', 0)} 별조각",
                confirm_options, confirm_descriptions
            )
            confirm_result = confirm_menu.run()
            
            if confirm_result == 0:  # 예
                if self.unlock_trait(trait_name):
                    print(f"\n{bright_green('✅')} {trait_name}이(가) 해금되었습니다!")
                else:
                    print(f"\n{bright_red('❌')} 해금에 실패했습니다.")
                input("아무 키나 눌러 계속...")
        else:
            # 폴백: 기존 텍스트 방식
            unlockable = []
            for category_name, traits, color_func in categories:
                print(f"\n{color_func(category_name)}:")
                for trait_name in traits:
                    cost = self.get_trait_unlock_cost(trait_name)
                    unlocked = self.is_trait_unlocked(trait_name)
                    can_unlock = self.can_unlock_trait(trait_name)
                    
                    status = ""
                    if unlocked:
                        status = bright_green("✓ 해금됨")
                    elif can_unlock:
                        status = bright_yellow(f"💰 {cost}별조각")
                        unlockable.append((len(unlockable) + 1, trait_name, cost))
                    else:
                        status = bright_red(f"❌ {cost}별조각 필요")
                        
                    print(f"  {trait_name:15} - {status}")
                    
            if unlockable:
                print(f"\n{bright_yellow('해금 가능한 특성:')}")
                for idx, trait_name, cost in unlockable:
                    print(f"{idx}. {trait_name} ({cost} 별조각)")
                    
                print("0. 돌아가기")
                
                try:
                    choice = input("\n해금할 특성 번호: ").strip()
                    if choice == '0':
                        return
                    elif choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(unlockable):
                            _, trait_name, cost = unlockable[idx]
                            confirm = input(f"{trait_name}을(를) {cost} 별조각으로 해금하시겠습니까? (y/n): ").strip().lower()
                            if confirm in ['y', 'yes', 'ㅇ']:
                                if self.unlock_trait(trait_name):
                                    print(f"✅ {trait_name}이(가) 해금되었습니다!")
                                else:
                                    print("❌ 해금에 실패했습니다.")
                            else:
                                print("해금이 취소되었습니다.")
                        else:
                            print("❌ 잘못된 선택입니다.")
                    else:
                        print("❌ 숫자를 입력해주세요.")
                except ValueError:
                    print("❌ 잘못된 입력입니다.")
            else:
                print(f"\n{bright_yellow('해금 가능한 특성이 없습니다.')}")
                
            input("아무 키나 눌러 계속...")
    
    def show_permanent_enhancement_menu(self):
        """영구 강화 시스템 연결"""
        print(f"\n{bright_cyan('⚡ 영구 강화 시스템')}")
        print("="*60)
        print(f"별조각을 별의 정수로 교환하여 영구 강화를 구매할 수 있습니다.")
        print(f"교환비율: 별조각 2개 = 별의 정수 1개")
        print(f"현재 별조각: {self.data.get('star_fragments', 0)}개")
        print("="*60)
        
        # 별조각을 별의 정수로 교환할지 물어보기
        try:
            from .cursor_menu_system import CursorMenu
            
            exchange_options = [
                "별의 정수로 교환하고 영구 강화 메뉴 열기",
                "뒤로 가기"
            ]
            exchange_descriptions = [
                "별조각을 별의 정수로 교환하고 영구 강화 시스템을 엽니다",
                "메타 진행 메뉴로 돌아갑니다"
            ]
            
            exchange_menu = CursorMenu("영구 강화 시스템", exchange_options, exchange_descriptions, cancellable=True)
            choice = exchange_menu.run()
            
            if choice == 0:
                # 별조각이 있다면 교환 처리
                star_fragments = self.data.get('star_fragments', 0)
                if star_fragments >= 2:
                    # 교환할 수량 선택
                    max_exchange = star_fragments // 2
                    
                    exchange_amount_options = []
                    for i in [1, 5, 10, 25, 50, max_exchange]:
                        if i <= max_exchange:
                            fragments_needed = i * 2
                            exchange_amount_options.append(f"{i}개 (별조각 {fragments_needed}개 소모)")
                    
                    exchange_amount_options.append("취소")
                    
                    amount_menu = CursorMenu(
                        f"별의 정수 교환량 선택 (최대 {max_exchange}개)",
                        exchange_amount_options,
                        [f"별의 정수 {i}개를 획득합니다" for i in [1, 5, 10, 25, 50, max_exchange] if i <= max_exchange] + ["교환을 취소합니다"],
                        cancellable=True
                    )
                    
                    amount_choice = amount_menu.run()
                    
                    if amount_choice is not None and amount_choice < len(exchange_amount_options) - 1:
                        exchange_amounts = [i for i in [1, 5, 10, 25, 50, max_exchange] if i <= max_exchange]
                        if amount_choice < len(exchange_amounts):
                            exchange_count = exchange_amounts[amount_choice]
                            fragments_cost = exchange_count * 2
                            
                            # 별조각 차감 및 영구 강화 시스템에 별조각 추가
                            self.data['star_fragments'] -= fragments_cost
                            self.data['star_fragments_spent'] = self.data.get('star_fragments_spent', 0) + fragments_cost
                            
                            # 영구 강화 시스템에 별조각 추가
                            try:
                                from .permanent_progression import PermanentProgressionSystem
                                perm_system = PermanentProgressionSystem()
                                perm_system.load_from_file()
                                perm_system.gain_star_fragments(exchange_count)
                                perm_system.save_to_file()
                                
                                self.save_data()
                                
                                print(f"\n{bright_green('전환 완료!')}")
                                print(f"별조각 {fragments_cost}개 → 영구 강화용 별조각 {exchange_count}개")
                                
                                # 영구 강화 메뉴 실행
                                perm_system.show_menu()
                                
                            except ImportError:
                                print(f"\n{bright_red('영구 강화 시스템을 불러올 수 없습니다.')}")
                                input("아무 키나 눌러 계속...")
                else:
                    print(f"\n{bright_yellow('별조각이 부족합니다. (최소 2개 필요)')}")
                    input("아무 키나 눌러 계속...")
            
        except ImportError:
            # 폴백: 텍스트 기반 메뉴
            print("1. 별의 정수로 교환하고 영구 강화 메뉴 열기")
            print("2. 뒤로 가기")
            
            choice = input("선택: ").strip()
            if choice == "1":
                star_fragments = self.data.get('star_fragments', 0)
                if star_fragments >= 2:
                    try:
                        exchange_count = int(input(f"교환할 별의 정수 개수 (최대 {star_fragments // 2}개): ").strip())
                        if 1 <= exchange_count <= star_fragments // 2:
                            fragments_cost = exchange_count * 2
                            
                            # 교환 처리
                            self.data['star_fragments'] -= fragments_cost
                            self.data['star_fragments_spent'] = self.data.get('star_fragments_spent', 0) + fragments_cost
                            
                            # 영구 강화 시스템에 추가
                            try:
                                from .permanent_progression import PermanentProgressionSystem
                                perm_system = PermanentProgressionSystem()
                                perm_system.load_from_file()
                                perm_system.gain_star_fragments(exchange_count)
                                perm_system.save_to_file()
                                
                                self.save_data()
                                
                                print(f"전환 완료! 별조각 {fragments_cost}개 → 영구 강화용 별조각 {exchange_count}개")
                                input("아무 키나 눌러 영구 강화 메뉴로...")
                                
                                # 영구 강화 메뉴 실행
                                perm_system.show_menu()
                                
                            except ImportError:
                                print("영구 강화 시스템을 불러올 수 없습니다.")
                        else:
                            print("잘못된 수량입니다.")
                    except ValueError:
                        print("숫자를 입력해주세요.")
                else:
                    print("별조각이 부족합니다. (최소 2개 필요)")
                    input("아무 키나 눌러 계속...")
    
    def show_achievements_menu(self):
        """업적 보기 메뉴 - 커서 기반"""
        try:
            from .cursor_menu_system import CursorMenu
            CURSOR_AVAILABLE = True
        except ImportError:
            CURSOR_AVAILABLE = False
            
        print(f"\n{bright_cyan('🏆 업적 시스템')}")
        print("="*60)
        
        # 모든 업적 정의
        all_achievement_categories = [
            ("기본 진행 업적", [
                {"name": "첫 모험", "condition": "total_runs", "value": 1, "reward": 50, "desc": "첫 번째 모험을 시작했습니다"},
                {"name": "도전자", "condition": "total_runs", "value": 5, "reward": 75, "desc": "5번의 모험을 완료했습니다"},
                {"name": "베테랑 모험가", "condition": "total_runs", "value": 10, "reward": 100, "desc": "10번의 모험을 완료했습니다"},
                {"name": "숙련된 탐험가", "condition": "total_runs", "value": 25, "reward": 150, "desc": "25번의 모험을 완료했습니다"},
                {"name": "전설의 모험가", "condition": "total_runs", "value": 50, "reward": 250, "desc": "50번의 모험을 완료했습니다"},
                {"name": "불멸의 모험가", "condition": "total_runs", "value": 100, "reward": 500, "desc": "100번의 모험을 완료했습니다"}
            ]),
            ("전투 업적", [
                {"name": "첫 승리", "condition": "total_enemies_defeated", "value": 1, "reward": 25, "desc": "첫 번째 적을 물리쳤습니다"},
                {"name": "몬스터 헌터", "condition": "total_enemies_defeated", "value": 100, "reward": 150, "desc": "100마리의 적을 물리쳤습니다"},
                {"name": "학살자", "condition": "total_enemies_defeated", "value": 500, "reward": 300, "desc": "500마리의 적을 물리쳤습니다"},
                {"name": "대량학살자", "condition": "total_enemies_defeated", "value": 1000, "reward": 500, "desc": "1000마리의 적을 물리쳤습니다"},
                {"name": "악몽", "condition": "total_enemies_defeated", "value": 2000, "reward": 750, "desc": "2000마리의 적을 물리쳤습니다"},
                {"name": "절멸자", "condition": "total_enemies_defeated", "value": 5000, "reward": 1000, "desc": "5000마리의 적을 물리쳤습니다"}
            ]),
            ("탐험 업적", [
                {"name": "첫 걸음", "condition": "total_floors_cleared", "value": 1, "reward": 30, "desc": "첫 번째 층을 클리어했습니다"},
                {"name": "깊은 탐험", "condition": "total_floors_cleared", "value": 10, "reward": 100, "desc": "10층까지 탐험했습니다"},
                {"name": "심연 탐험가", "condition": "total_floors_cleared", "value": 25, "reward": 200, "desc": "25층까지 탐험했습니다"},
                {"name": "어둠의 정복자", "condition": "total_floors_cleared", "value": 50, "reward": 400, "desc": "50층까지 탐험했습니다"},
                {"name": "무한의 탐험가", "condition": "total_floors_cleared", "value": 100, "reward": 800, "desc": "100층까지 탐험했습니다"},
                {"name": "심연의 지배자", "condition": "total_floors_cleared", "value": 200, "reward": 1500, "desc": "200층까지 탐험했습니다"}
            ]),
            ("수집 업적", [
                {"name": "수집가", "condition": "total_items_collected", "value": 10, "reward": 50, "desc": "10개의 아이템을 수집했습니다"},
                {"name": "보물 사냥꾼", "condition": "total_items_collected", "value": 50, "reward": 100, "desc": "50개의 아이템을 수집했습니다"},
                {"name": "전설의 수집가", "condition": "total_items_collected", "value": 200, "reward": 300, "desc": "200개의 아이템을 수집했습니다"},
                {"name": "만물 수집가", "condition": "total_items_collected", "value": 500, "reward": 600, "desc": "500개의 아이템을 수집했습니다"},
                {"name": "욕심쟁이", "condition": "total_items_collected", "value": 1000, "reward": 1000, "desc": "1000개의 아이템을 수집했습니다"}
            ]),
            ("점수 업적", [
                {"name": "점수 획득", "condition": "best_score", "value": 500, "reward": 75, "desc": "500점 이상의 점수를 획득했습니다"},
                {"name": "점수 마스터", "condition": "best_score", "value": 2000, "reward": 200, "desc": "2000점 이상의 점수를 획득했습니다"},
                {"name": "점수 전설", "condition": "best_score", "value": 5000, "reward": 400, "desc": "5000점 이상의 점수를 획득했습니다"},
                {"name": "점수 신화", "condition": "best_score", "value": 10000, "reward": 800, "desc": "10000점 이상의 점수를 획득했습니다"},
                {"name": "점수 불멸", "condition": "best_score", "value": 25000, "reward": 1500, "desc": "25000점 이상의 점수를 획득했습니다"}
            ]),
            ("특수 업적", [
                {"name": "불굴의 의지", "condition": "total_deaths", "value": 10, "reward": 100, "desc": "10번 이상 죽었지만 포기하지 않았습니다"},
                {"name": "고통의 대가", "condition": "total_deaths", "value": 25, "reward": 200, "desc": "25번 이상 죽었지만 계속 도전했습니다"},
                {"name": "영원한 도전자", "condition": "total_deaths", "value": 50, "reward": 350, "desc": "50번 이상 죽었지만 굴복하지 않았습니다"},
                {"name": "불사조", "condition": "total_deaths", "value": 100, "reward": 600, "desc": "100번 이상 죽었지만 다시 일어났습니다"}
            ])
        ]
        
        if CURSOR_AVAILABLE:
            # 카테고리 선택 메뉴
            category_options = []
            category_descriptions = []
            
            for category_name, achievements in all_achievement_categories:
                completed_count = 0
                total_count = len(achievements)
                
                for achievement in achievements:
                    if achievement["name"] in self.data.get("achievements", []):
                        completed_count += 1
                
                category_options.append(f"{category_name} ({completed_count}/{total_count})")
                category_descriptions.append(f"{category_name} 업적들을 확인합니다")
            
            category_options.append("뒤로 가기")
            category_descriptions.append("업적 메뉴를 나갑니다")
            
            category_menu = CursorMenu("🏆 업적 카테고리", category_options, category_descriptions, cancellable=True)
            category_result = category_menu.run()
            
            if category_result is None or category_result == len(category_options) - 1:
                return
            
            # 선택된 카테고리의 업적들 표시
            category_name, achievements = all_achievement_categories[category_result]
            
            print(f"\n{bright_cyan(f'🏆 {category_name}')}")
            print("="*60)
            
            for achievement in achievements:
                name = achievement["name"]
                condition = achievement["condition"]
                value = achievement["value"]
                reward = achievement["reward"]
                desc = achievement["desc"]
                
                current_value = self.data.get(condition, 0)
                is_completed = name in self.data.get("achievements", [])
                
                if is_completed:
                    status = bright_green("✅ 완료")
                    progress = f"({current_value}/{value})"
                else:
                    status = bright_red("❌ 미완료")
                    progress = f"({min(current_value, value)}/{value})"
                
                print(f"{name:20} {status}")
                print(f"  📝 {desc}")
                print(f"  🎁 보상: {reward} 별조각")
                print(f"  📊 진행도: {progress}")
                print()
            
            input("아무 키나 눌러 계속...")
        else:
            # 폴백: 간단한 텍스트 표시
            completed_achievements = self.data.get("achievements", [])
            total_achievements = sum(len(achievements) for _, achievements in all_achievement_categories)
            
            print(f"달성한 업적: {len(completed_achievements)}/{total_achievements}")
            print("\n최근 달성한 업적:")
            for achievement in completed_achievements[-10:]:
                print(f"  ✅ {achievement}")
            
            input("아무 키나 눌러 계속...")

    def check_achievements(self):
        """업적 체크 - 대폭 확장된 업적 시스템"""
        new_achievements = []
        
        # 기본 진행 업적
        basic_achievements = [
            {"name": "첫 모험", "condition": "total_runs", "value": 1, "reward": 50, "desc": "첫 번째 모험을 시작했습니다"},
            {"name": "도전자", "condition": "total_runs", "value": 5, "reward": 75, "desc": "5번의 모험을 완료했습니다"},
            {"name": "베테랑 모험가", "condition": "total_runs", "value": 10, "reward": 100, "desc": "10번의 모험을 완료했습니다"},
            {"name": "숙련된 탐험가", "condition": "total_runs", "value": 25, "reward": 150, "desc": "25번의 모험을 완료했습니다"},
            {"name": "전설의 모험가", "condition": "total_runs", "value": 50, "reward": 250, "desc": "50번의 모험을 완료했습니다"},
        ]
        
        # 전투 업적
        combat_achievements = [
            {"name": "첫 승리", "condition": "total_enemies_defeated", "value": 1, "reward": 25, "desc": "첫 번째 적을 물리쳤습니다"},
            {"name": "몬스터 헌터", "condition": "total_enemies_defeated", "value": 100, "reward": 150, "desc": "100마리의 적을 물리쳤습니다"},
            {"name": "학살자", "condition": "total_enemies_defeated", "value": 500, "reward": 300, "desc": "500마리의 적을 물리쳤습니다"},
            {"name": "대량학살자", "condition": "total_enemies_defeated", "value": 1000, "reward": 500, "desc": "1000마리의 적을 물리쳤습니다"},
            {"name": "악몽", "condition": "total_enemies_defeated", "value": 2000, "reward": 750, "desc": "2000마리의 적을 물리쳤습니다"},
        ]
        
        # 탐험 업적
        exploration_achievements = [
            {"name": "첫 걸음", "condition": "total_floors_cleared", "value": 1, "reward": 30, "desc": "첫 번째 층을 클리어했습니다"},
            {"name": "깊은 탐험", "condition": "total_floors_cleared", "value": 10, "reward": 100, "desc": "10층까지 탐험했습니다"},
            {"name": "심연 탐험가", "condition": "total_floors_cleared", "value": 25, "reward": 200, "desc": "25층까지 탐험했습니다"},
            {"name": "어둠의 정복자", "condition": "total_floors_cleared", "value": 50, "reward": 400, "desc": "50층까지 탐험했습니다"},
            {"name": "무한의 탐험가", "condition": "total_floors_cleared", "value": 100, "reward": 800, "desc": "100층까지 탐험했습니다"},
        ]
        
        # 수집 업적
        collection_achievements = [
            {"name": "수집가", "condition": "total_items_collected", "value": 10, "reward": 50, "desc": "10개의 아이템을 수집했습니다"},
            {"name": "보물 사냥꾼", "condition": "total_items_collected", "value": 50, "reward": 100, "desc": "50개의 아이템을 수집했습니다"},
            {"name": "전설의 수집가", "condition": "total_items_collected", "value": 200, "reward": 300, "desc": "200개의 아이템을 수집했습니다"},
            {"name": "만물 수집가", "condition": "total_items_collected", "value": 500, "reward": 600, "desc": "500개의 아이템을 수집했습니다"},
        ]
        
        # 점수 업적
        score_achievements = [
            {"name": "점수 획득", "condition": "best_score", "value": 500, "reward": 75, "desc": "500점 이상의 점수를 획득했습니다"},
            {"name": "점수 마스터", "condition": "best_score", "value": 2000, "reward": 200, "desc": "2000점 이상의 점수를 획득했습니다"},
            {"name": "점수 전설", "condition": "best_score", "value": 5000, "reward": 400, "desc": "5000점 이상의 점수를 획득했습니다"},
            {"name": "점수 신화", "condition": "best_score", "value": 10000, "reward": 800, "desc": "10000점 이상의 점수를 획득했습니다"},
        ]
        
        # 특수 업적
        special_achievements = [
            {"name": "불굴의 의지", "condition": "total_deaths", "value": 10, "reward": 100, "desc": "10번 이상 죽었지만 포기하지 않았습니다"},
            {"name": "고통의 대가", "condition": "total_deaths", "value": 25, "reward": 200, "desc": "25번 이상 죽었지만 계속 도전했습니다"},
            {"name": "영원한 도전자", "condition": "total_deaths", "value": 50, "reward": 350, "desc": "50번 이상 죽었지만 굴복하지 않았습니다"},
        ]
        
        all_achievements = (basic_achievements + combat_achievements + 
                          exploration_achievements + collection_achievements + 
                          score_achievements + special_achievements)
        
        for achievement in all_achievements:
            if (achievement["name"] not in self.data["achievements"] and
                self.data.get(achievement["condition"], 0) >= achievement["value"]):
                
                self.data["achievements"].append(achievement["name"])
                self.data["star_fragments"] += achievement["reward"]
                new_achievements.append(achievement)
                
        return new_achievements
    
    def get_unlocked_characters(self) -> List[str]:
        """해금된 캐릭터 목록 반환"""
        # 개발모드 확인
        try:
            from config import game_config
            if hasattr(game_config, 'DEVELOPMENT_MODE') and game_config.DEVELOPMENT_MODE:
                # 개발모드에서는 모든 캐릭터 해금
                all_characters = [
                    "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크",
                    "바드", "네크로맨서", "용기사", "검성", "정령술사", "암살자",
                    "기계공학자", "무당", "해적", "사무라이", "드루이드", "철학자",
                    "시간술사", "연금술사", "검투사", "기사", "신관", "마검사",
                    "차원술사", "광전사"
                ]
                return all_characters
        except ImportError:
            pass
        
        return self.data.get("unlocked_classes", ["전사", "아크메이지", "궁수", "도적"])
        
    def get_persistent_items(self) -> List[str]:
        """지속 아이템 목록 반환"""
        return self.data.get("persistent_items", [])
        
    def use_persistent_item(self, item_name: str) -> bool:
        """지속 아이템 사용"""
        items = self.data.get("persistent_items", [])
        if item_name in items:
            items.remove(item_name)
            self.save_data()
            return True
        return False
        
    def upgrade_character(self, char_name: str) -> bool:
        """캐릭터 업그레이드"""
        if "character_upgrades" not in self.data:
            self.data["character_upgrades"] = {}
        
        current_level = self.data["character_upgrades"].get(char_name, 0)
        cost = 100 * (current_level + 1)
        
        if self.data.get("star_fragments", 0) >= cost:
            self.data["star_fragments"] -= cost
            self.data["character_upgrades"][char_name] = current_level + 1
            self.save_data()
            return True
        return False
        
    def update_class_mastery(self, class_name: str, experience_gained: int, enemies_killed: int, floors_cleared: int):
        """직업 숙련도 업데이트"""
        if "class_mastery" not in self.data:
            self.data["class_mastery"] = {}
            
        if class_name not in self.data["class_mastery"]:
            self.data["class_mastery"][class_name] = {
                "total_experience": 0,
                "total_enemies_killed": 0,
                "total_floors_cleared": 0,
                "total_playtime": 0,
                "mastery_level": 0,
                "mastery_points": 0,
                "times_played": 0,
                "best_floor": 0,
                "total_deaths": 0,
                "survival_time": 0
            }
        
        mastery = self.data["class_mastery"][class_name]
        mastery["total_experience"] += experience_gained
        mastery["total_enemies_killed"] += enemies_killed
        mastery["total_floors_cleared"] += floors_cleared
        mastery["times_played"] += 1
        mastery["best_floor"] = max(mastery["best_floor"], floors_cleared)
        
        # 숙련도 포인트 계산 (복합적 계산)
        points_gained = (
            experience_gained // 100 +  # 경험치 100당 1포인트
            enemies_killed * 2 +        # 적 1마리당 2포인트
            floors_cleared * 10 +       # 층 1개당 10포인트
            (50 if floors_cleared >= 10 else 0)  # 10층 이상 보너스
        )
        
        mastery["mastery_points"] += points_gained
        
        # 숙련도 레벨 계산 (포인트 기반)
        old_level = mastery["mastery_level"]
        new_level = self.calculate_mastery_level(mastery["mastery_points"])
        mastery["mastery_level"] = new_level
        
        self.save_data()
        
        # 레벨업 시 보상
        if new_level > old_level:
            level_rewards = self.get_mastery_level_rewards(class_name, new_level)
            return level_rewards
        
        return None
    
    def calculate_mastery_level(self, mastery_points: int) -> int:
        """숙련도 레벨 계산"""
        # 레벨별 필요 포인트: 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500...
        level = 0
        required_points = 0
        
        while mastery_points >= required_points:
            level += 1
            required_points += level * 100
            
        return max(0, level - 1)
    
    def get_mastery_level_rewards(self, class_name: str, level: int) -> Dict:
        """숙련도 레벨 보상"""
        base_reward = level * 25  # 레벨당 25 별조각
        bonus_reward = 0
        
        # 마일스톤 보너스
        if level in [5, 10, 15, 20, 25]:
            bonus_reward = level * 50
            
        total_reward = base_reward + bonus_reward
        self.data["star_fragments"] += total_reward
        
        return {
            "class_name": class_name,
            "new_level": level,
            "star_fragments": total_reward,
            "milestone": level % 5 == 0
        }
    
    def get_class_mastery_info(self, class_name: str) -> Dict:
        """직업 숙련도 정보 반환"""
        if "class_mastery" not in self.data:
            self.data["class_mastery"] = {}
            
        if class_name not in self.data["class_mastery"]:
            return {
                "mastery_level": 0,
                "mastery_points": 0,
                "total_experience": 0,
                "total_enemies_killed": 0,
                "total_floors_cleared": 0,
                "times_played": 0,
                "best_floor": 0,
                "next_level_points": 100
            }
        
        mastery = self.data["class_mastery"][class_name]
        current_level = mastery["mastery_level"]
        current_points = mastery["mastery_points"]
        
        # 다음 레벨까지 필요한 포인트 계산
        next_level_required = 0
        for i in range(1, current_level + 2):
            next_level_required += i * 100
            
        points_for_current = 0
        for i in range(1, current_level + 1):
            points_for_current += i * 100
            
        next_level_points = next_level_required - current_points
        
        return {
            **mastery,
            "next_level_points": max(0, next_level_points)
        }
    
    def show_class_mastery_overview(self):
        """직업 숙련도 개요 표시 - 커서 기반"""
        try:
            from .cursor_menu_system import CursorMenu
            CURSOR_AVAILABLE = True
        except ImportError:
            CURSOR_AVAILABLE = False
        
        print(f"\n{bright_cyan('📊 직업 숙련도 현황')}")
        print("="*80)
        
        if "class_mastery" not in self.data or not self.data["class_mastery"]:
            print("아직 숙련도 데이터가 없습니다.")
            input("아무 키나 눌러 계속...")
            return
        
        # 숙련도 순으로 정렬
        sorted_classes = sorted(
            self.data["class_mastery"].items(),
            key=lambda x: x[1]["mastery_level"],
            reverse=True
        )
        
        if CURSOR_AVAILABLE:
            # 커서 메뉴로 상세 정보 선택
            options = []
            descriptions = []
            
            for class_name, mastery in sorted_classes:
                level = mastery["mastery_level"]
                points = mastery["mastery_points"]
                played = mastery["times_played"]
                best_floor = mastery["best_floor"]
                kills = mastery["total_enemies_killed"]
                
                level_color = "🔥" if level >= 10 else "⭐" if level >= 5 else "📈"
                
                options.append(f"{level_color} {class_name} (Lv.{level})")
                descriptions.append(
                    f"숙련도 {level}레벨 | {points}포인트 | {played}회 플레이 | 최고 {best_floor}층 | {kills}마리 처치"
                )
            
            options.append("📈 전체 통계 보기")
            descriptions.append("모든 직업의 통계를 한 번에 확인합니다")
            
            options.append("뒤로 가기")
            descriptions.append("메인 메뉴로 돌아갑니다")
            
            menu = CursorMenu("📊 직업 숙련도", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None or result == len(options) - 1:
                return
            elif result == len(options) - 2:  # 전체 통계 보기
                self._show_full_mastery_stats(sorted_classes)
            else:  # 특정 직업 상세 정보
                class_name, mastery = sorted_classes[result]
                self._show_detailed_class_mastery(class_name, mastery)
        else:
            # 폴백: 기존 텍스트 방식
            print(f"{'클래스':12} {'레벨':4} {'포인트':8} {'플레이':6} {'최고층':6} {'처치':8}")
            print("-" * 80)
            
            for class_name, mastery in sorted_classes:
                level = mastery["mastery_level"]
                points = mastery["mastery_points"]
                played = mastery["times_played"]
                best_floor = mastery["best_floor"]
                kills = mastery["total_enemies_killed"]
                
                level_color = bright_green if level >= 10 else bright_yellow if level >= 5 else bright_red
                
                print(f"{class_name:12} {level_color(str(level)):4} {points:8} {played:6} {best_floor:6} {kills:8}")
            
            print("-" * 80)
            total_classes_played = len(sorted_classes)
            max_level = max([m["mastery_level"] for m in self.data["class_mastery"].values()]) if sorted_classes else 0
            
            print(f"플레이한 클래스: {total_classes_played}개 | 최고 숙련도: {max_level}레벨")
            
            input("\n아무 키나 눌러 계속...")
    
    def _show_full_mastery_stats(self, sorted_classes):
        """전체 숙련도 통계 표시"""
        print(f"\n{bright_cyan('📊 전체 숙련도 통계')}")
        print("="*80)
        print(f"{'클래스':12} {'레벨':4} {'포인트':8} {'플레이':6} {'최고층':6} {'처치':8}")
        print("-" * 80)
        
        total_levels = 0
        total_points = 0
        total_plays = 0
        total_kills = 0
        
        for class_name, mastery in sorted_classes:
            level = mastery["mastery_level"]
            points = mastery["mastery_points"]
            played = mastery["times_played"]
            best_floor = mastery["best_floor"]
            kills = mastery["total_enemies_killed"]
            
            total_levels += level
            total_points += points
            total_plays += played
            total_kills += kills
            
            level_color = bright_green if level >= 10 else bright_yellow if level >= 5 else bright_red
            print(f"{class_name:12} {level_color(str(level)):4} {points:8} {played:6} {best_floor:6} {kills:8}")
        
        print("-" * 80)
        print(f"{'합계':12} {bright_cyan(str(total_levels)):4} {bright_cyan(str(total_points)):8} {bright_cyan(str(total_plays)):6} {'-':6} {bright_cyan(str(total_kills)):8}")
        print(f"\n📈 전체 통계:")
        print(f"  - 플레이한 직업: {bright_yellow(str(len(sorted_classes)))}개")
        print(f"  - 총 숙련도 레벨: {bright_yellow(str(total_levels))}")
        print(f"  - 총 숙련도 포인트: {bright_yellow(str(total_points))}")
        print(f"  - 총 플레이 횟수: {bright_yellow(str(total_plays))}")
        print(f"  - 총 적 처치: {bright_yellow(str(total_kills))}마리")
        
        if sorted_classes:
            max_level_class = max(sorted_classes, key=lambda x: x[1]["mastery_level"])
            most_played_class = max(sorted_classes, key=lambda x: x[1]["times_played"])
            
            print(f"  - 최고 숙련도: {bright_green(max_level_class[0])} ({max_level_class[1]['mastery_level']}레벨)")
            print(f"  - 가장 많이 플레이: {bright_green(most_played_class[0])} ({most_played_class[1]['times_played']}회)")
        
        input("\n아무 키나 눌러 계속...")
    
    def _show_detailed_class_mastery(self, class_name, mastery):
        """특정 직업의 상세 숙련도 정보"""
        print(f"\n{bright_cyan(f'📊 {class_name} 상세 숙련도')}")
        print("="*60)
        
        level = mastery["mastery_level"]
        points = mastery["mastery_points"]
        
        # 다음 레벨까지 필요한 포인트 계산
        next_level_required = 0
        for i in range(1, level + 2):
            next_level_required += i * 100
            
        points_for_current = 0
        for i in range(1, level + 1):
            points_for_current += i * 100
            
        next_level_points = next_level_required - points
        
        print(f"🏆 현재 레벨: {bright_yellow(str(level))}")
        print(f"⭐ 숙련도 포인트: {bright_yellow(str(points))}")
        print(f"📈 다음 레벨까지: {bright_cyan(str(max(0, next_level_points)))} 포인트")
        print(f"🎮 총 플레이 횟수: {mastery['times_played']}회")
        print(f"🏔️ 최고 도달 층: {mastery['best_floor']}층")
        print(f"⚔️ 총 적 처치: {mastery['total_enemies_killed']}마리")
        print(f"💀 총 사망 횟수: {mastery.get('total_deaths', 0)}회")
        print(f"🧙 총 획득 경험치: {mastery['total_experience']}")
        
        # 레벨별 보상 정보
        if level < 25:  # 최대 레벨을 25로 가정
            next_reward = (level + 1) * 25
            milestone_bonus = ((level + 1) * 50) if (level + 1) % 5 == 0 else 0
            total_next_reward = next_reward + milestone_bonus
            
            print(f"\n🎁 다음 레벨업 보상: {bright_green(str(total_next_reward))} 별조각")
            if milestone_bonus > 0:
                print(f"   (기본 {next_reward} + 마일스톤 보너스 {milestone_bonus})")
        
        input("\n아무 키나 눌러 계속...")
    
    def show_detailed_statistics(self):
        """상세 통계 표시 - 커서 기반"""
        try:
            from .cursor_menu_system import CursorMenu
            CURSOR_AVAILABLE = True
        except ImportError:
            CURSOR_AVAILABLE = False
        
        if CURSOR_AVAILABLE:
            # 커서 메뉴로 통계 카테고리 선택
            options = [
                "📊 기본 통계",
                "💎 보유 자원",
                "🏆 업적 현황",
                "🎓 직업 숙련도",
                "⚡ 영구 강화",
                "📈 전체 통계 한눈에"
            ]
            descriptions = [
                "기본적인 게임 플레이 통계를 확인합니다",
                "현재 보유한 자원과 해금 현황을 확인합니다",
                "달성한 업적과 업적 진행도를 확인합니다",
                "직업별 숙련도와 플레이 통계를 확인합니다",
                "별의 정수로 구매한 영구 강화 현황을 확인합니다",
                "모든 통계를 한 번에 확인합니다"
            ]
            
            options.append("뒤로 가기")
            descriptions.append("메인 메뉴로 돌아갑니다")
            
            menu = CursorMenu("📈 상세 통계", options, descriptions, cancellable=True)
            result = menu.run()
            
            if result is None or result == len(options) - 1:
                return
            elif result == 0:
                self._show_basic_statistics()
            elif result == 1:
                self._show_resource_status()
            elif result == 2:
                self._show_achievement_status()
            elif result == 3:
                self._show_mastery_summary()
            elif result == 4:
                self._show_upgrade_status()
            elif result == 5:
                self._show_all_statistics()
        else:
            # 폴백: 기존 방식
            self._show_all_statistics()
    
    def _show_basic_statistics(self):
        """기본 통계 표시"""
        print(f"\n{bright_cyan('📊 기본 통계')}")
        print("="*60)
        print(f"  총 플레이 횟수: {bright_yellow(str(self.data.get('total_runs', 0)))}회")
        print(f"  최고 점수: {bright_yellow(str(self.data.get('best_score', 0)))}점")
        print(f"  총 클리어 층수: {bright_yellow(str(self.data.get('total_floors_cleared', 0)))}층")
        print(f"  총 적 처치수: {bright_yellow(str(self.data.get('total_enemies_defeated', 0)))}마리")
        print(f"  총 아이템 수집: {bright_yellow(str(self.data.get('total_items_collected', 0)))}개")
        print(f"  총 사망 횟수: {bright_red(str(self.data.get('statistics', {}).get('total_deaths', 0)))}회")
        
        # 평균 통계
        runs = max(1, self.data.get('total_runs', 1))
        avg_score = self.data.get('best_score', 0) // runs
        avg_floors = self.data.get('total_floors_cleared', 0) // runs
        avg_kills = self.data.get('total_enemies_defeated', 0) // runs
        
        print(f"\n📈 평균 통계 (게임당):")
        print(f"  평균 점수: {bright_green(str(avg_score))}점")
        print(f"  평균 클리어 층: {bright_green(str(avg_floors))}층")
        print(f"  평균 적 처치: {bright_green(str(avg_kills))}마리")
        
        input("\n아무 키나 눌러 계속...")
    
    def _show_resource_status(self):
        """보유 자원 현황"""
        print(f"\n{bright_cyan('💎 보유 자원')}")
        print("="*60)
        print(f"  별조각: {bright_yellow(str(self.data.get('star_fragments', 0)))}개")
        print(f"  해금된 캐릭터: {bright_green(str(len(self.data.get('unlocked_classes', []))))}개")
        print(f"  해금된 특성: {bright_green(str(len(self.data.get('unlocked_traits', []))))}개")
        
        # 해금 진행률
        total_characters = 27  # 전체 캐릭터 수
        total_traits = 140     # 전체 특성 수 (확장됨)
        
        char_progress = len(self.data.get('unlocked_classes', [])) / total_characters * 100
        trait_progress = len(self.data.get('unlocked_traits', [])) / total_traits * 100
        
        print(f"\n📊 해금 진행률:")
        print(f"  캐릭터: {bright_cyan(f'{char_progress:.1f}%')} ({len(self.data.get('unlocked_classes', []))}/{total_characters})")
        print(f"  특성: {bright_cyan(f'{trait_progress:.1f}%')} ({len(self.data.get('unlocked_traits', []))}/{total_traits})")
        
        input("\n아무 키나 눌러 계속...")
    
    def _show_achievement_status(self):
        """업적 현황"""
        print(f"\n{bright_cyan('🏆 업적 현황')}")
        print("="*60)
        achievements = self.data.get('achievements', [])
        print(f"  달성한 업적: {bright_yellow(str(len(achievements)))}개")
        
        if achievements:
            print(f"\n최근 달성 업적:")
            for achievement in achievements[-10:]:  # 최근 10개만 표시
                print(f"    🏆 {achievement}")
        else:
            print(f"\n  {bright_red('아직 달성한 업적이 없습니다.')}")
        
        # 업적별 진행도 (예시)
        print(f"\n📈 주요 업적 진행도:")
        runs = self.data.get('total_runs', 0)
        kills = self.data.get('total_enemies_defeated', 0)
        floors = self.data.get('total_floors_cleared', 0)
        
        print(f"  모험가 (플레이 {runs}/50회): {'✅' if runs >= 50 else '🔄'}")
        print(f"  학살자 (처치 {kills}/500마리): {'✅' if kills >= 500 else '🔄'}")
        print(f"  탐험가 (층 {floors}/25층): {'✅' if floors >= 25 else '🔄'}")
        
        input("\n아무 키나 눌러 계속...")
    
    def _show_mastery_summary(self):
        """직업 숙련도 요약"""
        print(f"\n{bright_cyan('🎓 직업 숙련도 요약')}")
        print("="*60)
        class_mastery = self.data.get('class_mastery', {})
        
        if class_mastery:
            total_mastery_levels = sum(m["mastery_level"] for m in class_mastery.values())
            max_mastery = max(m["mastery_level"] for m in class_mastery.values())
            favorite_class = max(class_mastery.items(), key=lambda x: x[1]["times_played"])
            most_skilled = max(class_mastery.items(), key=lambda x: x[1]["mastery_level"])
            
            print(f"  총 숙련도 레벨: {bright_yellow(str(total_mastery_levels))}")
            print(f"  최고 숙련도: {bright_green(str(max_mastery))}레벨")
            print(f"  가장 많이 플레이한 클래스: {bright_cyan(favorite_class[0])} ({favorite_class[1]['times_played']}회)")
            print(f"  가장 숙련된 클래스: {bright_cyan(most_skilled[0])} ({most_skilled[1]['mastery_level']}레벨)")
            
            # 상위 5개 클래스
            sorted_classes = sorted(class_mastery.items(), key=lambda x: x[1]["mastery_level"], reverse=True)
            print(f"\n🏆 상위 숙련도 클래스:")
            for i, (class_name, mastery) in enumerate(sorted_classes[:5], 1):
                level = mastery["mastery_level"]
                print(f"    {i}. {class_name}: {level}레벨")
        else:
            print(f"  {bright_red('아직 숙련도 데이터가 없습니다.')}")
        
        input("\n아무 키나 눌러 계속...")
    
    def _show_upgrade_status(self):
        """영구 업그레이드 현황"""
        print(f"\n{bright_cyan('⬆️ 영구 업그레이드 현황')}")
        print("="*60)
        upgrades = self.data.get('permanent_upgrades', {})
        total_upgrade_levels = sum(upgrades.values())
        print(f"  총 업그레이드 레벨: {bright_yellow(str(total_upgrade_levels))}")
        
        active_upgrades = [(k, v) for k, v in upgrades.items() if v > 0]
        if active_upgrades:
            print(f"\n✅ 활성 업그레이드:")
            for upgrade_name, level in active_upgrades:
                description = self.get_upgrade_description(upgrade_name)
                print(f"    {upgrade_name}: {bright_green(str(level))}레벨")
                print(f"      └─ {description}")
        else:
            print(f"\n  {bright_red('아직 구매한 업그레이드가 없습니다.')}")
        
        input("\n아무 키나 눌러 계속...")
        
    def _show_all_statistics(self):
        """전체 통계 한눈에"""
        print(f"\n{bright_cyan('📈 전체 통계')}")
        print("="*80)
        
        # 기본 통계
        print(f"{bright_yellow('기본 통계:')}")
        print(f"  총 플레이 횟수: {self.data.get('total_runs', 0)}회")
        print(f"  최고 점수: {self.data.get('best_score', 0)}점")
        print(f"  총 클리어 층수: {self.data.get('total_floors_cleared', 0)}층")
        print(f"  총 적 처치수: {self.data.get('total_enemies_defeated', 0)}마리")
        print(f"  총 아이템 수집: {self.data.get('total_items_collected', 0)}개")
        print(f"  총 사망 횟수: {self.data.get('statistics', {}).get('total_deaths', 0)}회")
        
        # 보유 자원
        print(f"\n{bright_yellow('보유 자원:')}")
        print(f"  별조각: {self.data.get('star_fragments', 0)}개")
        print(f"  해금된 캐릭터: {len(self.data.get('unlocked_classes', []))}개")
        print(f"  해금된 특성: {len(self.data.get('unlocked_traits', []))}개")
        
        # 업적 현황
        print(f"\n{bright_yellow('업적 현황:')}")
        achievements = self.data.get('achievements', [])
        print(f"  달성한 업적: {len(achievements)}개")
        if achievements:
            print("  최근 달성 업적:")
            for achievement in achievements[-5:]:  # 최근 5개만 표시
                print(f"    - {achievement}")
        
        # 직업 숙련도 요약
        print(f"\n{bright_yellow('직업 숙련도 요약:')}")
        class_mastery = self.data.get('class_mastery', {})
        if class_mastery:
            total_mastery_levels = sum(m["mastery_level"] for m in class_mastery.values())
            max_mastery = max(m["mastery_level"] for m in class_mastery.values())
            favorite_class = max(class_mastery.items(), key=lambda x: x[1]["times_played"])
            
            print(f"  총 숙련도 레벨: {total_mastery_levels}")
            print(f"  최고 숙련도: {max_mastery}레벨")
            print(f"  가장 많이 플레이한 클래스: {favorite_class[0]} ({favorite_class[1]['times_played']}회)")
        else:
            print("  아직 숙련도 데이터가 없습니다.")
        
        # 영구 업그레이드 현황
        print(f"\n{bright_yellow('영구 업그레이드 현황:')}")
        upgrades = self.data.get('permanent_upgrades', {})
        total_upgrade_levels = sum(upgrades.values())
        print(f"  총 업그레이드 레벨: {total_upgrade_levels}")
        
        active_upgrades = [(k, v) for k, v in upgrades.items() if v > 0]
        if active_upgrades:
            print("  활성 업그레이드:")
            for upgrade_name, level in active_upgrades:
                description = self.get_upgrade_description(upgrade_name)
                print(f"    - {upgrade_name}: {level}레벨 ({description})")
        else:
            print("  아직 업그레이드가 없습니다.")
        
        input("\n아무 키나 눌러 계속...")
        
    def show_unlock_progress(self):
        """해금 진행상황 표시"""
        print("\n=== 캐릭터 해금 진행상황 ===")
        try:
            from .character_database import CharacterDatabase
            all_characters = CharacterDatabase.get_all_characters()
        except ImportError:
            print("캐릭터 데이터베이스를 불러올 수 없습니다.")
            return
            
        for char in all_characters:
            char_name = char["name"]
            if char_name in self.data.get("unlocked_classes", []):
                print(f"✓ {char_name} - 해금됨")
            else:
                print(f"✗ {char_name} - 해금 조건을 만족하지 않음")
                
    def reset_progress(self):
        """진행도 초기화 (개발/테스트용)"""
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        self.data = self.load_data()
    
    def update_floors_cleared(self, floors: int):
        """클리어한 층수 업데이트"""
        if "floors_cleared" not in self.data:
            self.data["floors_cleared"] = 0
        if floors > self.data["floors_cleared"]:
            self.data["floors_cleared"] = floors
        self.save_data()

# 전역 메타 진행 시스템
meta_progression = MetaProgression()

def get_meta_progression() -> MetaProgression:
    """메타 진행 시스템 반환"""
    return meta_progression
