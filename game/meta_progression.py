"""
메타 진행 시스템 - 게임 오버 후 보상 및 해금 시스템
영구적 성장을 통한 점진적 강화
"""

import json
import os
from typing import Dict, List
from .color_text import bright_cyan, bright_yellow, bright_green, bright_red, bright_white


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
            "unlocked_classes": ["전사", "아크메이지", "궁수", "도적", "성기사", "몽크", "바드", "기사", "해적", "광전사"],  # 기본 10개 직업 (스탠다드하고 다루기 쉬운 직업들)
            "star_fragments": 0,  # 별조각 (메타 재화)
            "star_fragments_spent": 0,  # 사용한 별조각 추적
            
            # 🌟 별조각 상점 시스템
            "discovered_items": {},  # 발견한 아이템들 {item_name: {type, rarity, level_req, first_found_floor}}
            "discovered_equipment": {},  # 발견한 장비들
            "discovered_food": {},  # 발견한 음식들
            "shop_purchases": {},  # 상점에서 구매한 아이템 기록
            
            # 🏪 창고 시스템
            "warehouse_unlocked": False,  # 창고 잠금 해제 상태
            "warehouse_upgrade_level": 0,  # 창고 업그레이드 레벨 (무게 제한 증가)
            
            # 💀 게임오버 수집 시스템
            "death_salvage_unlocked": False,  # 게임오버 수집 잠금 해제
            "max_death_salvage": 1,  # 게임오버 시 최대 수집 가능 아이템 수
            "death_salvage_upgrades": 0,  # 수집 업그레이드 횟수
            
            # 해금된 특성들
            "unlocked_traits": [],
            
            # 🌟 새로운 패시브 시스템
            "unlocked_passives": [],  # 해금된 파티 패시브들
            "max_passive_cost_upgrades": 0,  # 최대 패시브 코스트 업그레이드 횟수 (기본 3 → 최대 10)
            "passive_unlock_history": {},  # 패시브 해금 기록
            
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
    
    # 🌟 별조각 상점 시스템
    def discover_item(self, item_name: str, item_type: str, rarity: str = "일반", 
                     level_req: int = 0, current_floor: int = 1):
        """아이템 발견 기록"""
        # ItemRarity enum을 문자열로 변환
        if hasattr(rarity, 'value'):
            rarity_str = rarity.value
        elif hasattr(rarity, 'name'):
            rarity_str = rarity.name
        else:
            rarity_str = str(rarity)
        
        if item_name not in self.data["discovered_items"]:
            self.data["discovered_items"][item_name] = {
                "type": item_type,
                "rarity": rarity_str, 
                "level_req": level_req,
                "first_found_floor": current_floor,
                "times_found": 1
            }
            print(f"✨ 새로운 아이템 발견: {bright_cyan(item_name)} ({rarity_str})")
        else:
            self.data["discovered_items"][item_name]["times_found"] += 1
    
    def discover_equipment(self, equipment_name: str, equipment_type: str, rarity: str = "일반",
                          level_req: int = 0, current_floor: int = 1):
        """장비 발견 기록"""
        # ItemRarity enum을 문자열로 변환
        if hasattr(rarity, 'value'):
            rarity_str = rarity.value
        elif hasattr(rarity, 'name'):
            rarity_str = rarity.name
        else:
            rarity_str = str(rarity)
        
        if equipment_name not in self.data["discovered_equipment"]:
            self.data["discovered_equipment"][equipment_name] = {
                "type": equipment_type,
                "rarity": rarity_str,
                "level_req": level_req, 
                "first_found_floor": current_floor,
                "times_found": 1
            }
            print(f"⚔️ 새로운 장비 발견: {bright_cyan(equipment_name)} ({rarity_str})")
        else:
            self.data["discovered_equipment"][equipment_name]["times_found"] += 1
    
    def discover_food(self, food_name: str, food_type: str = "음식", rarity: str = "일반",
                     current_floor: int = 1):
        """음식 발견 기록"""
        if food_name not in self.data["discovered_food"]:
            self.data["discovered_food"][food_name] = {
                "type": food_type,
                "rarity": rarity,
                "first_found_floor": current_floor,
                "times_found": 1
            }
            print(f"🍖 새로운 음식 발견: {bright_cyan(food_name)} ({rarity})")
        else:
            self.data["discovered_food"][food_name]["times_found"] += 1
    
    def get_star_fragment_price(self, item_name: str, item_data: dict) -> int:
        """아이템의 별조각 가격 계산"""
        base_prices = {
            "일반": 1,
            "고급": 3, 
            "희귀": 8,
            "영웅": 20,
            "전설": 50,
            "신화": 100
        }
        
        rarity = item_data.get("rarity", "일반")
        base_price = base_prices.get(rarity, 1)
        
        # 타입별 가격 조정
        item_type = item_data.get("type", "소모품")
        if item_type in ["무기", "방어구", "액세서리"]:
            base_price *= 2  # 장비는 2배
        elif item_type == "음식":
            base_price = max(1, base_price // 2)  # 음식은 절반
        
        # 발견 빈도에 따른 할인 (자주 발견한 아이템은 저렴)
        times_found = item_data.get("times_found", 1)
        if times_found >= 10:
            base_price = max(1, base_price // 2)
        elif times_found >= 5:
            base_price = max(1, int(base_price * 0.75))
        
        return base_price
    
    def can_purchase_item(self, item_name: str, item_data: dict) -> tuple[bool, str]:
        """아이템 구매 가능 여부 확인"""
        price = self.get_star_fragment_price(item_name, item_data)
        
        if self.star_fragments < price:
            return False, f"별조각 부족 (필요: {price}, 보유: {self.star_fragments})"
        
        return True, f"구매 가능 (가격: {price} 별조각)"
    
    def purchase_item(self, item_name: str, item_data: dict) -> tuple[bool, str]:
        """아이템 구매"""
        can_buy, msg = self.can_purchase_item(item_name, item_data)
        if not can_buy:
            return False, msg
        
        price = self.get_star_fragment_price(item_name, item_data)
        self.data["star_fragments"] -= price
        self.data["star_fragments_spent"] += price
        
        # 구매 기록
        if item_name not in self.data["shop_purchases"]:
            self.data["shop_purchases"][item_name] = 0
        self.data["shop_purchases"][item_name] += 1
        
        self.save_data()
        return True, f"✅ {item_name} 구매 완료! (남은 별조각: {self.star_fragments})"
            
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
        # 기본 10개 직업은 항상 해금
        unlock_cost = self.get_character_unlock_cost(class_name)
        if unlock_cost == 0:
            return True
            
        # 별조각으로 이미 해금했는지 확인
        if "unlocked_by_star_fragments" not in self.data:
            self.data["unlocked_by_star_fragments"] = {}
            
        return self.data["unlocked_by_star_fragments"].get(class_name, False)
    
    def get_character_unlock_cost(self, class_name: str) -> int:
        """캐릭터 해금 비용 반환"""
        unlock_costs = {
            # 🆓 기본 10개 직업은 해금 불필요 (비용 0)
            "전사": 0, "아크메이지": 0, "궁수": 0, "도적": 0, "성기사": 0,
            "몽크": 0, "바드": 0, "기사": 0, "해적": 0, "광전사": 0,
            
            # 💰 구매 필요한 직업들
            # 🌟 초급 확장 직업 (25-50 별조각)
            "검성": 25,      # 검기 시스템
            "검투사": 30,    # 투기장 시스템  
            "암흑기사": 35,  # 흡혈 시스템
            "용기사": 40,    # 용의표식 시스템
            "네크로맨서": 50, # 언데드 소환
            
            # ⭐ 중급 직업 (60-120 별조각)
            "정령술사": 60,  # 원소 정령 시스템
            "암살자": 80,    # 그림자 시스템
            "사무라이": 100, # 무사도 시스템
            "기계공학자": 120, # 오버차지 시스템
            
            # 🌟 고급 직업 (150-300 별조각)
            "무당": 150,     # 영력 시스템
            "드루이드": 180, # 자연 변신 시스템
            "성직자": 200,   # 신성 시스템
            "연금술사": 250, # 연금 반응 시스템
            "철학자": 300,   # 지혜 시스템
            
            # ✨ 마스터 직업 (400-700 별조각)
            "시간술사": 400, # 시간 조작 시스템
            "신관": 500,     # 신성력 시스템
            "마검사": 600,   # 마검 융합 시스템
            
            # 🔥 전설 직업 (800-1000 별조각)
            "차원술사": 800, # 차원 조작 시스템
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
        """특성 설명 반환 - 2025년 8월 완전 개편"""
        descriptions = {
            # === 🏆 기본 전투 특성 (5-20 별조각) ===
            "불굴의 의지": "체력이 25% 이하일 때 받는 피해 30% 감소, 턴당 최대 HP 3% 회복",
            "피의 갈증": "적 처치 시 다음 3턴간 공격력 20% 증가 (중첩 가능)",
            "전투 광기": "받은 피해 100당 공격 속도 5% 증가 (최대 50%)",
            "위협적 존재": "적들의 선제공격 확률 40% 감소, 첫 턴 크리티컬 확률 +15%",
            "방어 숙련": "모든 방어력 25% 증가, 완벽한 방어 확률 10%",
            "빠른 손놀림": "공격 속도 20% 증가, 회피율 15% 증가",
            "치명적 급소": "크리티컬 확률 25% 증가, 크리티컬 피해 40% 증가",
            "전투 본능": "전투 시작 시 모든 능력치 15% 증가 (3턴간)",
            "생존 의지": "치명상 시 1회 한정 HP 1로 생존, 이후 5턴간 모든 저항 +50%",
            "전투 흥분": "연속 공격 시 피해량 누적 증가 (최대 5스택, 각 10% 증가)",
            "고통 무시": "상처로 인한 최대 HP 제한이 50%에서 25%로 완화",
            "무모한 돌진": "체력이 낮을수록 이동 속도와 공격력 증가 (최대 60%)",
            
            # === 🎭 기본 마법 특성 (5-20 별조각) ===
            "마력 집중": "마법 공격력 30% 증가, MP 75% 이상일 때 추가 20% 증가",
            "마나 순환": "MP 자동 회복 속도 100% 증가, 스킬 사용 시 30% 확률로 MP 50% 회복",
            "원소 지배": "모든 속성 마법 위력 35% 증가, 속성 상성 효과 2배",
            "마법 폭주": "크리티컬 마법 시 20% 확률로 MP 소모 없이 같은 마법 재시전",
            "마법 연구자": "마법 스킬 성장 속도 50% 증가, 전투 후 경험치 20% 추가 획득",
            "마나 효율": "모든 마법의 MP 소모량 30% 감소, 저레벨 마법은 MP 소모 없음",
            "시전 가속": "마법 시전 시간 40% 단축, 즉시 시전 확률 15%",
            "원소 이해": "속성 상성 효과 3배 증가, 적의 속성 저항 25% 무시",
            "실험 정신": "마법 실험으로 새로운 조합 마법 개발 가능",
            "마법 저항": "받는 마법 피해 40% 감소, 마법 상태이상 저항 70%",
            "어둠 친화": "어둠 속성 마법 위력 60% 증가, 어둠에서 모든 능력치 +20%",
            "정령 친화": "정령 마법 위력 50% 증가, 정령 소환 지속시간 2배",
            
            # === 🏹 기본 사격/은신 특성 (5-20 별조각) ===
            "정밀 사격": "원거리 공격 명중률 30% 증가, 크리티컬 확률 25% 증가",
            "연발 사격": "연속 공격 시 공격 속도 점진적 증가 (최대 60%)",
            "관통 사격": "원거리 공격이 모든 적을 관통, 피해량 50% 유지",
            "독수리의 눈": "적의 약점 간파, 크리티컬 피해 80% 증가",
            "민첩한 몸놀림": "회피율 30% 증가, 이동 시 다음 공격 피해 +25%",
            "원거리 숙련": "모든 원거리 공격 피해 35% 증가, 최대 사거리 +2칸",
            "바람의 가호": "바람 속성 공격 50% 증가, 이동 속도 40% 증가",
            "사냥꾼의 직감": "적의 위치와 상태 미리 감지, 기습 공격 피해 2배",
            "그림자 이동": "그림자를 통해 3칸 순간이동, 이동 후 첫 공격 크리티컬 확정",
            "독 마스터": "독 공격 위력 100% 증가, 독 면역, 독 반사 피해",
            "일격필살": "5% 확률로 즉사 공격, 보스에게는 최대 HP의 50% 피해",
            "은신 숙련": "은신 상태 공격력 150% 증가, 발각 확률 50% 감소",
            "그림자 은신": "완전 은신 (3턴간 무적), 은신 해제 시 강력한 암살 공격",
            "독 숙련": "독 피해 200% 증가, 독 중첩 시 폭발 효과",
            "도적의 직감": "함정 감지 100%, 보물 발견 확률 3배, 비밀 문 자동 발견",
            "치명타 특화": "크리티컬 시 20% 확률로 적 즉사 또는 강력한 상태이상 부여",
            
            # === ⛪ 중급 성직자/성기사 특성 (15-50 별조각) ===
            "치유의 빛": "치유 효과 100% 증가, 치유 시 상처도 50% 회복",
            "신성한 가호": "언데드·악마 피해 70% 감소, 성속성 공격 2배",
            "축복받은 무기": "모든 공격에 성속성 추가, 언데드에게 3배 피해",
            "수호의 맹세": "파티원 보호 시 받는 피해 60% 감소, 보호막 생성",
            "정의의 분노": "악한 적 상대 시 공격력 100% 증가, 정의의 심판 발동",
            "생명 흡수": "가한 피해의 25%만큼 HP 회복, 오버힐 시 상처 치료",
            "어둠의 계약": "HP 소모로 강력한 공격, HP 낮을수록 위력 증가 (최대 200%)",
            "불사의 의지": "치명상 시 완전 회복 (1회), 이후 언데드 상태로 전투 계속",
            "어둠 조작": "그림자 조작으로 공격과 방어, 암속성 마법 위력 3배",
            "공포 오라": "주변 적들 50% 확률로 행동 불가, 도망 확률 증가",
            
            # === 🥋 중급 직업 특성 (15-50 별조각) ===
            "내공 순환": "스킬 사용 후 MP 지속 회복 (3턴간), MP 회복량 50% 증가",
            "연타 숙련": "연속 공격 시 속도 누적 증가 (최대 100%), 콤보 보너스",
            "정신 수양": "상태이상 저항 60%, 정신계 공격 완전 면역",
            "참선의 깨달음": "경험치 획득 40% 증가, 스킬 숙련도 성장 2배",
            "기절 공격": "공격 시 30% 확률로 적 기절 (2턴), 기절한 적에게 크리티컬 확정",
            "영감 부여": "파티원 모든 능력치 25% 증가, 상태이상 회복 효과",
            "다중 주문": "스킬 사용 시 40% 확률로 쿨다운 없음, 연속 시전 가능",
            "재생의 노래": "매 턴 파티 전체 HP·MP 15% 회복, 상태이상 제거",
            "카리스마": "상인 거래 50% 할인, NPC 호감도 2배 증가",
            "언데드 소환": "처치한 적을 언데드로 소환 (5턴간), 최대 3마리",
            "영혼 조작": "적의 영혼 조작으로 혼란·지배, 정신 지배 확률 40%",
            "생명력 흡수": "적 처치 시 최대 HP 5% 영구 증가 (최대 200%)",
            "공포 유발": "적들을 공포로 도망가게 만듦, 도망간 적은 경험치 그대로 획득",
            "용의 분노": "HP 낮을수록 모든 능력 증가 (최대 150%), 용의 오라 발동",
            "비늘 방어": "물리 피해 50% 감소, 화염 완전 면역",
            "용의 숨결": "화염 속성 공격 200% 증가, 브레스 공격으로 광역 소멸",
            
            # === 🗡️ Phase 1&2 신규 특성 (20-80 별조각) ===
            # 검성
            "검기 집중": "검 스킬 위력 60% 증가, 검기로 원거리 공격 가능",
            "일섬의 달인": "60% 확률로 즉사 공격, 실패 시에도 최대 HP의 70% 피해",
            "검의 이치": "모든 검술이 완벽한 경지에 도달, 검 공격 절대 방어 불가",
            "명경지수": "정신이 맑아져 크리티컬 확률 50% 증가, 상태이상 완전 면역",
            "검신의 축복": "검의 신이 내린 축복으로 모든 능력이 초월적 수준에 도달",
            
            # 검투사
            "투기장의 경험": "관중이 많을수록 강해짐 (최대 100% 증가), 화려한 기술 사용",
            "패링 마스터": "모든 공격을 완벽하게 반격, 반격 피해 2배",
            "생존 본능": "위험 감지 능력으로 치명적 공격 70% 확률로 완전 회피",
            "투사의 긍지": "명예로운 전투에서 모든 능력 50% 증가",
            "콜로세움의 영웅": "전설적 검투사의 기량으로 적들이 압도당해 전투 의지 상실",
            
            # 광전사
            "피의 갈증": "적 처치 시 분노 게이지 증가, 분노 상태에서 무적",
            "광기의 힘": "HP 낮을수록 공격력 기하급수적 증가 (최대 500%)",
            "불굴의 의지": "어떤 공격에도 죽지 않고 최소 HP 1 유지",
            "피의 복수": "아군이 쓰러질 때마다 영구적으로 모든 능력 30% 증가",
            "광전사의 최후": "죽음 직전 최후의 광기 발동, 모든 적에게 절멸적 피해",
            
            # 기사
            "의무의 수호자": "아군 보호 시 자신도 같은 효과 획득, 수호 범위 확장",
            "기사도 정신": "정정당당한 전투에서 모든 능력 40% 증가",
            "불굴의 방어": "방어 시 피해 80% 감소, 방어 성공 시 강력한 반격",
            "수호 본능": "아군이 위험할 때 자동으로 보호, 순간이동으로 막아서기",
            "기사의 맹세": "맹세의 힘으로 절대 후퇴하지 않고 끝까지 전투",
            
            # 성기사
            "성역의 수호자": "성스러운 결계로 아군 보호, 악한 존재 접근 불가",
            "축복의 빛": "신의 축복으로 파티 전체 능력 50% 증가",
            "신성한 힘": "신성한 힘으로 모든 공격에 성속성 부여",
            "정의의 심판": "악한 적에게 신의 심판 내려 즉사 또는 큰 피해",
            "천사의 가호": "천사의 날개로 비행 가능, 신성한 오라로 주변 정화",
            
            # 암흑기사
            "어둠의 권능": "어둠의 힘으로 금지된 마법 사용, 생명력으로 강력한 공격",
            "생명력 지배": "생명력을 자유자재로 조작, 적의 생명력 흡수",
            "어둠의 오라": "어둠의 오라로 적들 약화, 암속성 피해 300% 증가",
            "불사의 계약": "죽음과의 계약으로 불사 상태, 죽어도 계속 전투",
            "어둠의 군주": "어둠을 지배하는 군주로 암흑 차원의 힘 사용",
            
            # === 🏪 창고 & 게임오버 수집 특성 (30-100 별조각) ===
            "창고 마스터": "창고 무게 제한 50% 증가, 자동 정리 기능",
            "수집가의 직감": "희귀 아이템 발견 확률 3배, 숨겨진 보물 자동 감지",
            "생존 본능": "게임오버 시 수집 가능 아이템 +2개, 최고 등급 아이템 우선 선택",
            "마지막 의지": "게임오버 시 장착 장비도 수집 가능, 인챈트 효과 유지",
            
            # === 🎯 장비/도구 관련 특성 (20-150 별조각) ===
            "장비 수호자": "🛡️ 마법적 보호막이 장비를 감싸 내구도 감소 확률 40% 감소",
            "단조 마스터": "🔨 신화급 대장장이의 솜씨로 장비 최대 내구도 30% 증가",
            "장비 분석가": "� 고급 분석술로 장비 상태를 완벽히 파악, 수리 효율 100% 증가",
            "장인의 혼": "✨ 전설의 장인 혼이 깃들어 수리 시 내구도 20% 추가 회복",
            "완벽주의자": "🎯 장비를 90% 이상 유지 시 모든 능력치 15% 증가",
            "강철 의지": "⚔️ 불굴의 의지로 장비 손상 70% 감소, 수리 비용 50% 절약",
            "절대 보존": "💎 절대적 보존술로 장비 절대 파괴 불가, 자동 수리 기능"
        }
        return descriptions.get(trait_name, "신비로운 힘을 가진 특성입니다")

    def get_trait_unlock_cost(self, trait_name: str) -> int:
        """특성 해금 비용 반환 - 2025년 8월 완전 개편"""
        trait_costs = {
            # === 🏆 기본 전투 특성 (5-20 별조각) ===
            "불굴의 의지": 8, "피의 갈증": 12, "전투 광기": 15, "위협적 존재": 18,
            "방어 숙련": 10, "빠른 손놀림": 9, "치명적 급소": 16, "전투 본능": 11,
            "생존 의지": 14, "전투 흥분": 20, "고통 무시": 22, "무모한 돌진": 25,
            
            # === 🎭 기본 마법 특성 (5-20 별조각) ===
            "마력 집중": 12, "마나 순환": 15, "원소 지배": 20, "마법 폭주": 23,
            "마법 연구자": 18, "마나 효율": 13, "시전 가속": 16, "원소 이해": 21,
            "실험 정신": 14, "마법 저항": 17, "어둠 친화": 22, "정령 친화": 19,
            
            # === 🏹 기본 사격/은신 특성 (5-20 별조각) ===
            "정밀 사격": 8, "연발 사격": 11, "관통 사격": 14, "독수리의 눈": 17,
            "민첩한 몸놀림": 10, "원거리 숙련": 13, "바람의 가호": 16, "사냥꾼의 직감": 20,
            "그림자 이동": 15, "독 마스터": 18, "일격필살": 25, "은신 숙련": 19,
            "그림자 은신": 21, "독 숙련": 16, "도적의 직감": 23, "치명타 특화": 24,
            
            # === ⛪ 중급 성직자/성기사 특성 (15-50 별조각) ===
            "치유의 빛": 30, "신성한 가호": 28, "축복받은 무기": 35, "수호의 맹세": 42,
            "정의의 분노": 48, "생명 흡수": 22, "어둠의 계약": 30, "불사의 의지": 40,
            "어둠 조작": 45, "공포 오라": 50,
            
            # === 🥋 중급 직업 특성 (15-50 별조각) ===
            "내공 순환": 20, "연타 숙련": 28, "정신 수양": 35, "참선의 깨달음": 42,
            "기절 공격": 48, "영감 부여": 22, "다중 주문": 30, "재생의 노래": 38,
            "카리스마": 45, "언데드 소환": 32, "영혼 조작": 40, "생명력 흡수": 46,
            "공포 유발": 50, "용의 분노": 38, "비늘 방어": 42, "용의 숨결": 48,
            
            # === 🗡️ Phase 1&2 신규 특성 (20-90 별조각) ===
            # 검성
            "검기 집중": 30, "일섬의 달인": 45, "검의 이치": 60, "명경지수": 75, "검신의 축복": 90,
            
            # 검투사  
            "투기장의 경험": 35, "패링 마스터": 50, "생존 본능": 65, "투사의 긍지": 80, "콜로세움의 영웅": 95,
            
            # 광전사
            "피의 갈증": 40, "광기의 힘": 55, "불굴의 의지": 70, "피의 복수": 85, "광전사의 최후": 100,
            
            # 기사
            "의무의 수호자": 30, "기사도 정신": 42, "불굴의 방어": 55, "수호 본능": 70, "기사의 맹세": 85,
            
            # 성기사
            "성역의 수호자": 38, "축복의 빛": 50, "신성한 힘": 65, "정의의 심판": 80, "천사의 가호": 95,
            
            # 암흑기사
            "어둠의 권능": 42, "생명력 지배": 58, "어둠의 오라": 75, "불사의 계약": 90, "어둠의 군주": 110,
            
            # 용기사
            "표식 달인": 32, "도약의 숙련자": 45, "용의 혈통": 60, "드래곤 하트": 78, "용왕의 권능": 95,
            
            # 아크메이지
            "원소 순환 마스터": 48, "마법 연구자": 60, "원소 친화": 75, "대마법사": 90, "원소의 현자": 110,
            
            # 정령술사
            "정령 친화": 35, "자연의 축복": 48, "원소 조화": 62, "마나 순환": 78, "원소 폭발": 95,
            
            # 암살자
            "그림자 조작": 42, "그림자 강화": 55, "그림자 분신": 70, "그림자 은신": 85, "그림자 폭발": 105,
            
            # 기계공학자
            "자동 포탑": 48, "기계 정비": 62, "폭탄 제작": 78, "강화 장비": 95, "오버클럭": 115,
            
            # 무당
            "시야 확장": 38, "정령 가호": 50, "악령 퇴치": 65, "무당의 직감": 82, "영적 보호": 100,
            
            # 해적
            "보물 사냥꾼": 32, "이도류 전투": 45, "바다의 분노": 58, "럭키 스트라이크": 75, "해적의 경험": 90,
            
            # 사무라이
            "일격필살": 45, "카타나 숙련": 58, "참선": 72, "무사도": 88, "명예의 맹세": 105,
            
            # 드루이드
            "자연의 가호": 38, "자연 치유": 52, "식물 조종": 68, "동물 변신": 85, "계절의 힘": 100,
            
            # 철학자
            "현자의 지혜": 50, "논리적 사고": 65, "깨달음": 80, "사색의 힘": 95, "철학적 논증": 115,
            
            # 시간술사
            "시간 파동": 75, "시간 지연": 90, "시간 가속": 105, "시간의 달인": 125, "시공 왜곡": 150,
            
            # 연금술사
            "폭발 연구": 55, "플라스크 폭발": 70, "완전 변환": 85, "연금 숙련": 100, "생명 연성": 120,
            
            # 신관
            "신의 가호": 45, "성스러운 빛": 58, "치유 특화": 72, "축복의 기도": 88, "신탁": 105,
            
            # 마검사
            "마검 일체": 85, "마력 충전": 100, "검기 폭발": 118, "이중 속성": 135, "마검 오의": 155,
            
            # 차원술사
            "차원 보관": 95, "공간 이동": 115, "차원 균열": 135, "평행우주": 155, "공간 왜곡": 180,
            
            # === 🏪 창고 & 게임오버 수집 특성 (30-100 별조각) ===
            "창고 마스터": 50, "수집가의 직감": 70, "생존 본능": 85, "마지막 의지": 100,
            
            # === 🎯 장비/도구 관련 특성 (20-150 별조각) ===
            "장비 수호자": 25, "단조 마스터": 45, "장비 분석가": 65, "장인의 혼": 90,
            "완벽주의자": 120, "강철 의지": 140, "절대 보존": 180
        }
        return trait_costs.get(trait_name, 60)  # 기본값 60
    
    def get_trait_description(self, trait_name: str) -> str:
        """특성 설명 반환"""
        trait_descriptions = {
            # 전사 특성 (적응형 시스템 연계)
            "적응형 무술": "전투 중 자세 변경 시 다음 공격 위력 30% 증가",
            "전장의 지배자": "적응형 자세에서 얻는 보너스 효과 50% 증가",
            "불굴의 의지": "방어형 자세에서 체력 회복량 2배, 다른 자세에서도 턴당 체력 3% 회복",
            "전투 본능": "공격형/광전사 자세에서 크리티컬 확률 20% 증가",
            "균형감각": "균형 자세에서 모든 능력치 15% 증가, 수호자 자세에서 아군 보호 효과",
            
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
            
            # 도적 특성 (리메이크)
            "독술 지배": "모든 공격에 독 효과 부여, 독 피해량 50% 증가",
            "침묵 술": "공격 시 30% 확률로 적의 스킬 봉인 2턴",
            "독 촉진": "독에 걸린 적 공격 시 남은 독 피해의 25%를 즉시 피해",
            "맹독 면역": "모든 독과 상태이상에 완전 면역, 독 공격 받을 때 반사",
            "독왕의 권능": "적이 독으로 죽을 때 주변 적들에게 독 전파",
            
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
            
            # 도적 특성 (리메이크)
            "독혈 지배": "독 데미지가 100% 증가하고 독 누적 시 폭발적 피해",
            "침묵의 왕": "모든 공격에 침묵 효과 부여, 침묵당한 적은 속도 50% 감소",
            "독의 촉진자": "독 촉진 효과가 50%로 증가하고 범위 공격으로 변화",
            "맹독 군주": "독 면역 + 독 공격 받을 때 MP 회복 + 독 반사 데미지 2배",
            "독 전파술": "독으로 적 처치 시 3칸 범위 내 모든 적에게 강력한 독 전파",
            "베놈 익스플로전": "독 폭발 범위가 전체 적으로 확장되고 피해량 2배",
            "침묵의 암살자": "침묵 상태의 적에게 공격 시 즉사 확률 30%",
            "독왕의 권좌": "독에 걸린 적 수만큼 자신의 모든 능력치 10% 증가",
            
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
    
    def show_star_fragment_item_shop(self):
        """별조각 아이템 상점 표시 - 발견한 아이템들 구매"""
        try:
            from game.cursor_menu_system import CursorMenu
            use_cursor_menu = True
        except ImportError:
            use_cursor_menu = False
        
        while True:
            print(f"\n{bright_cyan('⭐ 별조각 아이템 상점')}")
            print("=" * 60)
            print(f"{bright_yellow(f'보유 별조각: {self.star_fragments}개')}")
            print(f"{bright_white('발견한 아이템으로만 구매 가능 (레벨/희귀도 제한 없음)')}")
            print("=" * 60)
            
            # 카테고리별 분류
            categories = [
                ("🧪 소모품", self.data["discovered_items"], "아이템"),
                ("⚔️ 장비", self.data["discovered_equipment"], "장비"), 
                ("🍖 음식", self.data["discovered_food"], "음식")
            ]
            
            if use_cursor_menu:
                # 커서 메뉴 사용
                category_options = []
                category_descriptions = []
                
                for category_name, items_dict, item_type in categories:
                    if items_dict:  # 발견한 아이템이 있는 카테고리만
                        count = len(items_dict)
                        category_options.append(f"{category_name} ({count}개)")
                        category_descriptions.append(f"{item_type} 카테고리를 선택합니다")
                
                if not category_options:
                    print(f"\n{bright_red('아직 발견한 아이템이 없습니다!')}")
                    print(f"{bright_yellow('던전을 탐험하여 새로운 아이템을 발견해보세요.')}")
                    input("아무 키나 눌러 계속...")
                    return
                
                category_options.append("🚪 돌아가기")
                category_descriptions.append("별조각 아이템 상점을 나갑니다")
                
                category_menu = CursorMenu(
                    title="카테고리 선택",
                    options=category_options,
                    descriptions=category_descriptions
                )
                
                category_result = category_menu.show()
                
                if category_result == len(category_options) - 1:  # 돌아가기
                    break
                elif 0 <= category_result < len(categories):
                    # 선택된 카테고리의 아이템 목록 표시
                    selected_category = categories[category_result]
                    self._show_category_items(selected_category[0], selected_category[1], selected_category[2])
            
            else:
                # 폴백: 텍스트 기반 메뉴
                print(f"\n{bright_yellow('카테고리 선택:')}")
                valid_categories = []
                for i, (category_name, items_dict, item_type) in enumerate(categories):
                    if items_dict:
                        count = len(items_dict)
                        print(f"{len(valid_categories) + 1}. {category_name} ({count}개)")
                        valid_categories.append((category_name, items_dict, item_type))
                
                if not valid_categories:
                    print(f"\n{bright_red('아직 발견한 아이템이 없습니다!')}")
                    print(f"{bright_yellow('던전을 탐험하여 새로운 아이템을 발견해보세요.')}")
                    input("아무 키나 눌러 계속...")
                    return
                
                print("0. 돌아가기")
                
                try:
                    choice = input("\n카테고리 선택: ").strip()
                    if choice == '0':
                        break
                    elif choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(valid_categories):
                            category = valid_categories[idx]
                            self._show_category_items(category[0], category[1], category[2])
                        else:
                            print("잘못된 번호입니다.")
                except ValueError:
                    print("올바른 번호를 입력해주세요.")
    
    def _show_category_items(self, category_name: str, items_dict: dict, item_type: str):
        """카테고리별 아이템 목록 표시 및 구매"""
        try:
            from game.cursor_menu_system import CursorMenu
            use_cursor_menu = True
        except ImportError:
            use_cursor_menu = False
        
        while True:
            print(f"\n{bright_cyan(category_name)} - 아이템 목록")
            print("=" * 50)
            print(f"{bright_yellow(f'보유 별조각: {self.star_fragments}개')}")
            print("=" * 50)
            
            if not items_dict:
                print(f"\n{bright_red('이 카테고리에는 발견한 아이템이 없습니다.')}")
                input("아무 키나 눌러 계속...")
                return
            
            # 희귀도별 정렬
            rarity_order = {"일반": 0, "고급": 1, "희귀": 2, "영웅": 3, "전설": 4, "신화": 5}
            sorted_items = sorted(items_dict.items(), 
                                key=lambda x: (rarity_order.get(x[1].get("rarity", "일반"), 0), x[0]))
            
            if use_cursor_menu:
                # 커서 메뉴 사용
                item_options = []
                item_descriptions = []
                
                for item_name, item_data in sorted_items:
                    price = self.get_star_fragment_price(item_name, item_data)
                    rarity = item_data.get("rarity", "일반")
                    times_found = item_data.get("times_found", 1)
                    
                    # 희귀도별 색상
                    rarity_colors = {
                        "일반": bright_white,
                        "고급": bright_green, 
                        "희귀": bright_cyan,
                        "영웅": bright_yellow,
                        "전설": bright_red,
                        "신화": lambda x: f"\033[95m{x}\033[0m"  # 보라색
                    }
                    
                    color_func = rarity_colors.get(rarity, bright_white)
                    can_buy = self.star_fragments >= price
                    
                    if can_buy:
                        option_text = f"{color_func(item_name)} - {price}⭐"
                    else:
                        option_text = f"{item_name} - {price}⭐ (부족)"
                    
                    item_options.append(option_text)
                    item_descriptions.append(f"{rarity} {item_type} | 발견 횟수: {times_found}회 | 가격: {price} 별조각")
                
                item_options.append("🔙 돌아가기")
                item_descriptions.append("카테고리 선택으로 돌아갑니다")
                
                item_menu = CursorMenu(
                    title=f"{category_name} 구매",
                    options=item_options,
                    descriptions=item_descriptions
                )
                
                item_result = item_menu.show()
                
                if item_result == len(item_options) - 1:  # 돌아가기
                    break
                elif 0 <= item_result < len(sorted_items):
                    # 선택된 아이템 구매 확인
                    item_name, item_data = sorted_items[item_result]
                    self._confirm_purchase(item_name, item_data)
            
            else:
                # 폴백: 텍스트 기반 메뉴
                print(f"\n{bright_yellow('구매 가능한 아이템:')}")
                buyable_items = []
                
                for i, (item_name, item_data) in enumerate(sorted_items):
                    price = self.get_star_fragment_price(item_name, item_data)
                    rarity = item_data.get("rarity", "일반")
                    times_found = item_data.get("times_found", 1)
                    can_buy = self.star_fragments >= price
                    
                    status = bright_green("✓ 구매가능") if can_buy else bright_red("❌ 별조각부족")
                    
                    print(f"{i+1:2}. {item_name:20} [{rarity:4}] {price:3}⭐ {status} (발견: {times_found}회)")
                    buyable_items.append((item_name, item_data, can_buy))
                
                print("0. 돌아가기")
                
                try:
                    choice = input(f"\n구매할 아이템 번호 (보유: {self.star_fragments}⭐): ").strip()
                    if choice == '0':
                        break
                    elif choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(buyable_items):
                            item_name, item_data, can_buy = buyable_items[idx]
                            if can_buy:
                                self._confirm_purchase(item_name, item_data)
                            else:
                                print(f"\n{bright_red('별조각이 부족합니다!')}")
                                input("아무 키나 눌러 계속...")
                        else:
                            print("잘못된 번호입니다.")
                except ValueError:
                    print("올바른 번호를 입력해주세요.")
    
    def _confirm_purchase(self, item_name: str, item_data: dict):
        """아이템 구매 확인"""
        try:
            from game.cursor_menu_system import CursorMenu
            use_cursor_menu = True
        except ImportError:
            use_cursor_menu = False
        
        price = self.get_star_fragment_price(item_name, item_data)
        rarity = item_data.get("rarity", "일반")
        
        print(f"\n{bright_cyan('구매 확인')}")
        print("=" * 30)
        print(f"아이템: {bright_yellow(item_name)}")
        print(f"희귀도: {rarity}")
        print(f"가격: {bright_yellow(f'{price} 별조각')}")
        print(f"구매 후 보유: {bright_white(f'{self.star_fragments - price} 별조각')}")
        print("=" * 30)
        
        if use_cursor_menu:
            confirm_menu = CursorMenu(
                title="구매하시겠습니까?",
                options=["✅ 예, 구매합니다", "❌ 아니오, 취소합니다"],
                descriptions=["아이템을 구매합니다", "구매를 취소합니다"]
            )
            
            confirm_result = confirm_menu.show()
            
            if confirm_result == 0:  # 예
                success, msg = self.purchase_item(item_name, item_data)
                if success:
                    print(f"\n{bright_green(msg)}")
                    
                    # 구매한 아이템을 게임에 추가하는 로직은 여기서 처리
                    # (실제 게임 인벤토리에 추가하는 부분은 게임 메인 루프에서 처리)
                    print(f"{bright_cyan('💡 힌트: 다음 게임 시작 시 인벤토리에서 확인하세요!')}")
                else:
                    print(f"\n{bright_red(msg)}")
                input("아무 키나 눌러 계속...")
        else:
            # 폴백: 텍스트 기반
            confirm = input("구매하시겠습니까? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', 'ㅇ']:
                success, msg = self.purchase_item(item_name, item_data)
                if success:
                    print(f"\n{bright_green(msg)}")
                    print(f"{bright_cyan('💡 힌트: 다음 게임 시작 시 인벤토리에서 확인하세요!')}")
                else:
                    print(f"\n{bright_red(msg)}")
            else:
                print("구매가 취소되었습니다.")
            input("아무 키나 눌러 계속...")
    
    def get_purchased_items(self) -> dict:
        """구매한 아이템 목록 반환 (게임 시작 시 인벤토리에 추가용)"""
        return self.data.get("shop_purchases", {})
    
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
        
        return self.data.get("unlocked_classes", ["전사", "아크메이지", "궁수", "도적", "성기사", "몽크", "바드", "기사", "해적", "광전사"])
        
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
    
    # 🌟 새로운 패시브 시스템 메서드들
    def unlock_passive(self, passive_name: str, cost: int) -> bool:
        """패시브 해금 (별조각 소모)"""
        if self.data["star_fragments"] >= cost:
            self.data["star_fragments"] -= cost
            self.data["star_fragments_spent"] += cost
            
            if "unlocked_passives" not in self.data:
                self.data["unlocked_passives"] = []
            
            if passive_name not in self.data["unlocked_passives"]:
                self.data["unlocked_passives"].append(passive_name)
            
            # 해금 기록 저장
            if "passive_unlock_history" not in self.data:
                self.data["passive_unlock_history"] = {}
            self.data["passive_unlock_history"][passive_name] = cost
            
            self.save_data()
            return True
        return False
    
    def is_passive_unlocked(self, passive_name: str) -> bool:
        """패시브가 해금되었는지 확인"""
        return passive_name in self.data.get("unlocked_passives", [])
    
    def get_unlocked_passives(self) -> List[str]:
        """해금된 패시브 목록 반환"""
        return self.data.get("unlocked_passives", [])
    
    def upgrade_max_passive_cost(self, upgrade_cost: int) -> bool:
        """최대 패시브 코스트 업그레이드 (3 → 4 → 5 → ... → 10)"""
        current_upgrades = self.data.get("max_passive_cost_upgrades", 0)
        if current_upgrades >= 7:  # 최대 7단계 (3 + 7 = 10)
            return False
        
        if self.data["star_fragments"] >= upgrade_cost:
            self.data["star_fragments"] -= upgrade_cost
            self.data["star_fragments_spent"] += upgrade_cost
            self.data["max_passive_cost_upgrades"] = current_upgrades + 1
            self.save_data()
            return True
        return False
    
    def get_max_passive_cost(self) -> int:
        """현재 최대 패시브 코스트 반환"""
        base_cost = 3
        upgrades = self.data.get("max_passive_cost_upgrades", 0)
        return min(base_cost + upgrades, 10)
    
    def show_passive_unlock_menu(self):
        """패시브 해금 메뉴 표시"""
        print(f"\n{bright_cyan('=== 🌟 패시브 해금 메뉴 ===')}")
        fragments = self.data["star_fragments"]
        unlocked_count = len(self.get_unlocked_passives())
        max_cost = self.get_max_passive_cost()
        print(f"{bright_yellow(f'보유 별조각: {fragments}')}")
        print(f"{bright_green(f'해금된 패시브: {unlocked_count}개')}")
        print(f"{bright_green(f'최대 패시브 코스트: {max_cost}')}")
        
        # 해금 가능한 패시브들 (main.py의 패시브 목록과 동기화 필요)
        unlockable_passives = [
            {"name": "일사천리", "cost": 30},
            {"name": "위기 대응", "cost": 40},
            {"name": "완벽주의자", "cost": 50},
            {"name": "도박꾼의 심리", "cost": 60},
            {"name": "시너지 마스터", "cost": 70},
            {"name": "변화의 달인", "cost": 80},
            {"name": "역학 관계", "cost": 90},
            # 더 많은 패시브들...
        ]
        
        print(f"\n{bright_white('해금 가능한 패시브:')}")
        for i, passive in enumerate(unlockable_passives, 1):
            status = "✅ 해금됨" if self.is_passive_unlocked(passive["name"]) else f"🔒 별조각 {passive['cost']}개 필요"
            print(f"  {i}. {passive['name']} - {status}")
        
        print(f"\n{bright_white('코스트 업그레이드:')}")
        current_upgrades = self.data.get("max_passive_cost_upgrades", 0)
        if current_upgrades < 7:
            next_cost = (current_upgrades + 1) * 50
            print(f"  최대 코스트 {self.get_max_passive_cost()} → {self.get_max_passive_cost() + 1} (별조각 {next_cost}개)")
        else:
            print(f"  최대 업그레이드 완료! (코스트 10)")
    
    def unlock_warehouse(self):
        """창고 해금"""
        cost = 100
        if self.data["star_fragments"] >= cost:
            self.data["star_fragments"] -= cost
            self.data["warehouse_unlocked"] = True
            self.save_data()
            print(f"✅ 창고가 해금되었습니다! (별조각 {cost}개 소모)")
            input("엔터를 눌러 계속...")
        else:
            print(f"❌ 별조각이 부족합니다. (필요: {cost}, 보유: {self.data['star_fragments']})")
            input("엔터를 눌러 계속...")
    
    def show_warehouse_menu(self):
        """창고 메뉴 표시"""
        from .warehouse_system import get_warehouse
        from .cursor_menu_system import CursorMenu
        
        warehouse = get_warehouse()
        
        while True:
            print("\n" + "="*50)
            print("🏪 창고 관리")
            print("="*50)
            
            stats = warehouse.get_warehouse_stats()
            upgrade_level = self.data.get("warehouse_upgrade_level", 0)
            
            print(f"📦 보관 아이템: {stats['total_items']}")
            print(f"⚖️ 무게: {stats['total_weight']:.1f}/{stats['max_weight']}")
            print(f"⭐ 업그레이드 레벨: {upgrade_level}")
            
            options = [
                "📦 창고 열기",
                "⭐ 창고 업그레이드 (무게 +50)",
                "🔄 창고 정리",
                "⬅️ 돌아가기"
            ]
            
            menu = CursorMenu(options, "창고 메뉴")
            choice = menu.get_choice()
            
            if choice == 0:  # 창고 열기
                warehouse.show_warehouse_ui()
            elif choice == 1:  # 업그레이드
                self.upgrade_warehouse()
            elif choice == 2:  # 정리
                self.organize_warehouse()
            elif choice == 3:  # 돌아가기
                break
    
    def upgrade_warehouse(self):
        """창고 업그레이드"""
        current_level = self.data.get("warehouse_upgrade_level", 0)
        cost = (current_level + 1) * 75  # 75, 150, 225, ...
        
        if current_level >= 10:
            print("❌ 창고가 이미 최대 레벨입니다!")
            input("엔터를 눌러 계속...")
            return
        
        if self.data["star_fragments"] >= cost:
            self.data["star_fragments"] -= cost
            self.data["warehouse_upgrade_level"] = current_level + 1
            
            # 창고 최대 무게 증가
            from .warehouse_system import get_warehouse
            warehouse = get_warehouse()
            warehouse.max_weight += 50
            
            self.save_data()
            print(f"✅ 창고가 업그레이드되었습니다! (레벨 {current_level + 1})")
            print(f"⚖️ 최대 무게가 50 증가했습니다!")
            print(f"💫 별조각 {cost}개 소모")
            input("엔터를 눌러 계속...")
        else:
            print(f"❌ 별조각이 부족합니다. (필요: {cost}, 보유: {self.data['star_fragments']})")
            input("엔터를 눌러 계속...")
    
    def organize_warehouse(self):
        """창고 정리 (빈 슬롯 제거)"""
        print("🔄 창고를 정리하고 있습니다...")
        # 여기에 창고 정리 로직 구현 가능
        print("✅ 창고 정리가 완료되었습니다!")
        input("엔터를 눌러 계속...")
    
    def unlock_death_salvage(self):
        """게임오버 수집 기능 해금"""
        cost = 50
        if self.data["star_fragments"] >= cost:
            self.data["star_fragments"] -= cost
            self.data["death_salvage_unlocked"] = True
            self.data["max_death_salvage"] = 1
            self.save_data()
            print(f"✅ 게임오버 수집 기능이 해금되었습니다! (별조각 {cost}개 소모)")
            print("💀 이제 게임오버 시 아이템 1개를 가져올 수 있습니다!")
            input("엔터를 눌러 계속...")
        else:
            print(f"❌ 별조각이 부족합니다. (필요: {cost}, 보유: {self.data['star_fragments']})")
            input("엔터를 눌러 계속...")
    
    def upgrade_death_salvage(self):
        """게임오버 수집 업그레이드"""
        current_count = self.data.get("max_death_salvage", 1)
        upgrades = self.data.get("death_salvage_upgrades", 0)
        
        if upgrades >= 5:  # 최대 6개까지
            print("❌ 게임오버 수집이 이미 최대 레벨입니다! (6개)")
            input("엔터를 눌러 계속...")
            return
        
        cost = (upgrades + 1) * 30  # 30, 60, 90, 120, 150
        
        if self.data["star_fragments"] >= cost:
            self.data["star_fragments"] -= cost
            self.data["death_salvage_upgrades"] = upgrades + 1
            self.data["max_death_salvage"] = current_count + 1
            self.save_data()
            
            print(f"✅ 게임오버 수집이 업그레이드되었습니다!")
            print(f"💀 이제 게임오버 시 아이템 {current_count + 1}개를 가져올 수 있습니다!")
            print(f"💫 별조각 {cost}개 소모")
            input("엔터를 눌러 계속...")
        else:
            print(f"❌ 별조각이 부족합니다. (필요: {cost}, 보유: {self.data['star_fragments']})")
            input("엔터를 눌러 계속...")
    
    def handle_game_over_salvage(self, player_inventory):
        """게임오버 시 아이템 수집 처리"""
        if not self.data.get("death_salvage_unlocked", False):
            return []
        
        max_salvage = self.data.get("max_death_salvage", 1)
        available_items = []
        
        # 인벤토리에서 수집 가능한 아이템 찾기
        if hasattr(player_inventory, 'items'):
            for item in player_inventory.items:
                if item:  # None이 아닌 아이템만
                    available_items.append(item)
        
        if not available_items:
            print("💀 수집할 수 있는 아이템이 없습니다.")
            return []
        
        print(f"\n💀 게임오버 수집 시스템")
        print(f"🎒 최대 {max_salvage}개의 아이템을 가져올 수 있습니다.")
        print("="*50)
        
        salvaged_items = []
        from .cursor_menu_system import CursorMenu
        
        for i in range(max_salvage):
            if not available_items:
                break
            
            print(f"\n🔍 수집할 아이템 {i+1}/{max_salvage} 선택:")
            
            # 아이템 선택 메뉴
            item_options = []
            for item in available_items:
                item_name = getattr(item, 'name', str(item))
                item_options.append(f"📦 {item_name}")
            item_options.append("❌ 수집 중단")
            
            menu = CursorMenu(item_options, f"아이템 선택 ({i+1}/{max_salvage})")
            choice = menu.get_choice()
            
            if choice == len(item_options) - 1:  # 수집 중단
                break
            
            # 선택된 아이템 수집
            selected_item = available_items[choice]
            salvaged_items.append(selected_item)
            available_items.remove(selected_item)
            
            item_name = getattr(selected_item, 'name', str(selected_item))
            print(f"✅ {item_name}을(를) 수집했습니다!")
        
        if salvaged_items:
            print(f"\n🎒 총 {len(salvaged_items)}개의 아이템을 수집했습니다!")
            
            # 창고에 자동 저장 (창고가 해금된 경우)
            if self.data.get("warehouse_unlocked", False):
                from .warehouse_system import get_warehouse, WarehouseTab
                warehouse = get_warehouse()
                
                for item in salvaged_items:
                    item_name = getattr(item, 'name', str(item))
                    # 아이템 타입에 따라 적절한 탭에 저장
                    tab = WarehouseTab.CONSUMABLES  # 기본값
                    if hasattr(item, 'item_type'):
                        if 'weapon' in item.item_type.lower() or 'armor' in item.item_type.lower():
                            tab = WarehouseTab.EQUIPMENT
                        elif 'food' in item.item_type.lower():
                            tab = WarehouseTab.FOOD
                    
                    warehouse.store_item(
                        item_id=getattr(item, 'id', item_name),
                        item_name=item_name,
                        quantity=1,
                        weight=getattr(item, 'weight', 1.0),
                        tab=tab
                    )
                
                print("📦 수집한 아이템들이 창고에 저장되었습니다!")
        
        input("엔터를 눌러 계속...")
        return salvaged_items

# 전역 메타 진행 시스템
meta_progression = MetaProgression()

def get_meta_progression() -> MetaProgression:
    """메타 진행 시스템 반환"""
    return meta_progression
