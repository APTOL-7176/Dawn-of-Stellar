#!/usr/bin/env python3
"""
영구 성장 시스템 (메타 프로그레션)
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class PermanentUpgrade:
    """영구 업그레이드"""
    id: str
    name: str
    description: str
    cost: int
    max_level: int
    current_level: int = 0
    effect_type: str = "stat"  # "stat", "ability", "passive"
    effect_value: float = 0.0
    
    def get_total_cost(self, target_level: int) -> int:
        """목표 레벨까지의 총 비용"""
        total = 0
        for level in range(self.current_level, min(target_level, self.max_level)):
            total += self.cost * (level + 1)
        return total
    
    def get_effect_description(self) -> str:
        """효과 설명"""
        if self.current_level == 0:
            return "미보유"
        
        total_effect = self.effect_value * self.current_level
        if self.effect_type == "stat":
            return f"+{total_effect:.1f}"
        elif self.effect_type == "ability":
            return f"레벨 {self.current_level} 능력"
        else:
            return f"{total_effect:.1f}% 향상"


class PermanentProgressionSystem:
    """영구 성장 시스템"""
    
    def __init__(self):
        self.star_fragments = 0   # 별조각 (메타 화폐)
        self.total_runs = 0       # 총 플레이 횟수
        self.best_floor = 0       # 최고 도달 층
        self.total_kills = 0      # 총 처치 수
        self.total_deaths = 0     # 총 사망 횟수
        
        # 영구 업그레이드
        self.upgrades: Dict[str, PermanentUpgrade] = {}
        self.initialize_upgrades()
        
        # 업적
        self.achievements: Dict[str, bool] = {}
        self.initialize_achievements()
    
    def initialize_upgrades(self):
        """영구 업그레이드 초기화 - 패시브 코스트 시스템에 맞춤"""
        upgrade_data = [
            # 패시브 관련 - 최우선 (비용 상향)
            {
                "id": "passive_cost",
                "name": "패시브 확장",
                "description": "패시브 최대 코스트 +1 (5 → 10)",
                "cost": 80,  # 40 → 80
                "max_level": 5,  # 5+5=10 최대 코스트
                "effect_type": "passive",
                "effect_value": 1.0
            },
            {
                "id": "wound_healing",
                "name": "상처 치유술",
                "description": "상처 회복 속도 +25%",
                "cost": 70,  # 35 → 70
                "max_level": 4,
                "effect_type": "passive",
                "effect_value": 25.0
            },
            
            # 기본 스탯 강화 (비용 상향)
            {
                "id": "hp_boost",
                "name": "생명력 강화",
                "description": "시작 시 최대 HP +10%",
                "cost": 30,  # 15 → 30
                "max_level": 8,
                "effect_type": "stat",
                "effect_value": 10.0
            },
            {
                "id": "attack_boost",
                "name": "공격력 강화",
                "description": "시작 시 물리/마법 공격력 +8%",
                "cost": 40,  # 20 → 40
                "max_level": 6,
                "effect_type": "stat",
                "effect_value": 8.0
            },
            {
                "id": "defense_boost",
                "name": "방어력 강화",
                "description": "시작 시 물리/마법 방어력 +6%",
                "cost": 36,  # 18 → 36
                "max_level": 6,
                "effect_type": "stat",
                "effect_value": 6.0
            },
            {
                "id": "speed_boost",
                "name": "민첩성 강화",
                "description": "시작 시 속도 +5%",
                "cost": 50,  # 25 → 50
                "max_level": 5,
                "effect_type": "stat",
                "effect_value": 5.0
            },
            
            # 경제 관련 - 별조각 획득 중심 (비용 상향)
            {
                "id": "star_fragment_finder",
                "name": "별조각 탐지자",
                "description": "별조각 획득량 +25%",
                "cost": 80,  # 40 → 80
                "max_level": 4,
                "effect_type": "passive",
                "effect_value": 25.0
            },
            {
                "id": "gold_finder",
                "name": "황금 탐지자",
                "description": "골드 획득량 +20%",
                "cost": 50,  # 25 → 50
                "max_level": 5,
                "effect_type": "passive",
                "effect_value": 20.0
            },
            {
                "id": "item_luck",
                "name": "행운의 손길",
                "description": "희귀 아이템 발견 확률 +15%",
                "cost": 70,  # 35 → 70
                "max_level": 4,
                "effect_type": "passive",
                "effect_value": 15.0
            },
            
            # 게임플레이 편의성 (비용 상향)
            {
                "id": "inventory_expansion",
                "name": "차원 주머니",
                "description": "인벤토리 무게 한계 +20%",
                "cost": 60,  # 30 → 60
                "max_level": 5,
                "effect_type": "stat",
                "effect_value": 20.0
            },
            {
                "id": "starting_items",
                "name": "모험가의 준비",
                "description": "시작 시 기본 아이템 세트 제공",
                "cost": 90,  # 45 → 90
                "max_level": 3,
                "effect_type": "ability",
                "effect_value": 1.0
            },
            {
                "id": "auto_save",
                "name": "자동 저장",
                "description": "층 이동 시 자동 저장 (진행도 보호)",
                "cost": 120,  # 60 → 120
                "max_level": 1,
                "effect_type": "ability",
                "effect_value": 1.0
            },
            
            # 전투 관련 (비용 상향)
            {
                "id": "brave_mastery",
                "name": "용기의 숙련",
                "description": "Brave 회복량 +30%",
                "cost": 70,  # 35 → 70
                "max_level": 4,
                "effect_type": "passive",
                "effect_value": 30.0
            },
            {
                "id": "exp_boost",
                "name": "빠른 성장",
                "description": "경험치 획득량 +15%",
                "cost": 80,  # 40 → 80
                "max_level": 4,
                "effect_type": "passive",
                "effect_value": 15.0
            },
            {
                "id": "wound_resistance",
                "name": "상처 저항",
                "description": "상처 축적량 -15%",
                "cost": 100,  # 50 → 100
                "max_level": 3,
                "effect_type": "passive",
                "effect_value": 15.0
            },
            
            # 고급 능력 (비용 대폭 상향)
            {
                "id": "second_chance",
                "name": "재기의 기회",
                "description": "죽음 시 20% 확률로 부활 (최대 3회/게임)",
                "cost": 160,  # 80 → 160
                "max_level": 3,  # 최대 3회까지
                "effect_type": "ability",
                "effect_value": 20.0
            },
            {
                "id": "boss_hunter",
                "name": "보스 킬러",
                "description": "보스에게 추가 데미지 +30%",
                "cost": 160,  # 80 → 160
                "max_level": 2,
                "effect_type": "passive",
                "effect_value": 30.0
            }
        ]
        
        for data in upgrade_data:
            upgrade = PermanentUpgrade(**data)
            self.upgrades[upgrade.id] = upgrade
    
    def initialize_achievements(self):
        """업적 초기화 - 패시브 시스템에 맞춤"""
        self.achievements = {
            # 기본 진행 업적
            "first_floor": False,           # 첫 층 클리어
            "deep_dive": False,             # 10층 도달
            "abyss_explorer": False,        # 20층 도달
            
            # 전투 업적
            "monster_slayer": False,        # 몬스터 100마리 처치
            "boss_hunter": False,           # 보스 10마리 처치
            "unstoppable": False,           # 한 번도 죽지 않고 10층 클리어
            
            # 수집 업적
            "collector": False,             # 전설 아이템 5개 획득
            "gold_hoarder": False,          # 골드 5000 보유
            "star_collector": False,        # 별조각 500개 획득
            
            # 패시브 관련 업적
            "passive_master": False,        # 패시브 10코스트 달성
            "passive_collector": False,     # 패시브 15개 해금
            "synergy_master": False,        # 한 게임에서 패시브 5개 이상 사용
            
            # 거래 업적
            "merchant_friend": False,       # 상인과 20회 거래
            "chef_master": False,           # 요리 50개 제작
            
            # 특수 업적
            "brave_master": False,          # Brave 10000 달성
            "speed_runner": False,          # 5층을 30분 내 클리어
            "perfectionist": False          # 모든 패시브 해금
        }
    
    def gain_star_fragments(self, amount: int):
        """별조각 획득"""
        self.star_fragments += amount
    
    def can_upgrade(self, upgrade_id: str) -> tuple:
        """업그레이드 가능 여부 확인"""
        if upgrade_id not in self.upgrades:
            return False, "존재하지 않는 업그레이드"
        
        upgrade = self.upgrades[upgrade_id]
        
        if upgrade.current_level >= upgrade.max_level:
            return False, "최대 레벨 달성"
        
        next_cost = upgrade.cost * (upgrade.current_level + 1)
        if self.star_fragments < next_cost:
            return False, f"별조각 부족 ({self.star_fragments}/{next_cost})"
        
        return True, "업그레이드 가능"
    
    def purchase_upgrade(self, upgrade_id: str) -> tuple:
        """업그레이드 구매"""
        can_upgrade, reason = self.can_upgrade(upgrade_id)
        if not can_upgrade:
            return False, reason
        
        upgrade = self.upgrades[upgrade_id]
        cost = upgrade.cost * (upgrade.current_level + 1)
        
        self.star_fragments -= cost
        upgrade.current_level += 1
        
        return True, f"{upgrade.name} 레벨 {upgrade.current_level}로 업그레이드!"
    
    def get_stat_bonus(self, stat_name: str) -> float:
        """스탯 보너스 계산 - 개선된 매핑"""
        bonus = 0.0
        stat_mapping = {
            "hp": "hp_boost",
            "physical_attack": "attack_boost",
            "magic_attack": "attack_boost", 
            "physical_defense": "defense_boost",
            "magic_defense": "defense_boost",
            "speed": "speed_boost",
            "max_weight": "inventory_expansion"
        }
        
        if stat_name in stat_mapping:
            upgrade_id = stat_mapping[stat_name]
            if upgrade_id in self.upgrades:
                upgrade = self.upgrades[upgrade_id]
                bonus = upgrade.effect_value * upgrade.current_level
        
        return bonus
    
    def get_passive_bonus(self, bonus_type: str) -> float:
        """패시브 보너스 계산 - 개선된 매핑"""
        bonus = 0.0
        passive_mapping = {
            "gold_rate": "gold_finder",
            "item_luck": "item_luck", 
            "brave_regen": "brave_mastery",
            "exp_rate": "exp_boost",
            "star_fragments": "star_fragment_finder",
            "wound_resistance": "wound_resistance",
            "wound_healing": "wound_healing",
            "boss_damage": "boss_hunter",
            "passive_cost_max": "passive_cost"  # 패시브 최대 코스트
        }
        
        if bonus_type in passive_mapping:
            upgrade_id = passive_mapping[bonus_type]
            if upgrade_id in self.upgrades:
                upgrade = self.upgrades[upgrade_id]
                bonus = upgrade.effect_value * upgrade.current_level
        
        return bonus
    
    def has_ability(self, ability_name: str) -> bool:
        """특수 능력 보유 여부 확인"""
        ability_mapping = {
            "second_chance": "second_chance",
            "auto_save": "auto_save"
        }
        
        if ability_name in ability_mapping:
            upgrade_id = ability_mapping[ability_name]
            if upgrade_id in self.upgrades:
                return self.upgrades[upgrade_id].current_level > 0
        
        return False
    
    def check_achievement(self, achievement_id: str, condition_met: bool = True):
        """업적 달성 확인"""
        if achievement_id in self.achievements and not self.achievements[achievement_id]:
            if condition_met:
                self.achievements[achievement_id] = True
                return True  # 새 업적 달성
        return False
    
    def on_run_end(self, floor_reached: int, kills: int, died: bool, star_fragments_earned: int = 0, passives_used: int = 0):
        """게임 종료 시 호출 - 개선된 보상 시스템"""
        self.total_runs += 1
        self.best_floor = max(self.best_floor, floor_reached)
        self.total_kills += kills
        
        if died:
            self.total_deaths += 1
        
        # 별조각 획득 (층수, 처치 수, 생존 보너스)
        base_fragments = floor_reached * 2  # 층당 2조각
        kill_fragments = kills // 3         # 3킬당 1조각
        survival_bonus = (floor_reached * 3) if not died else 0  # 생존 보너스
        
        total_fragments = base_fragments + kill_fragments + survival_bonus
        self.gain_star_fragments(total_fragments)
        
        # 업적 확인
        self.check_achievement("first_floor", floor_reached >= 1)
        self.check_achievement("deep_dive", floor_reached >= 10)
        self.check_achievement("abyss_explorer", floor_reached >= 20)
        self.check_achievement("monster_slayer", self.total_kills >= 100)
        self.check_achievement("unstoppable", floor_reached >= 10 and not died)
        self.check_achievement("synergy_master", passives_used >= 5)
        
        # 별조각 관련 업적
        if star_fragments_earned > 0:
            self.check_achievement("star_collector", star_fragments_earned >= 500)
        
        return total_fragments
    
    def save_to_file(self, filename: str = "permanent_progress.json"):
        """영구 진행상황 저장"""
        data = {
            "star_fragments": self.star_fragments,
            "total_runs": self.total_runs,
            "best_floor": self.best_floor,
            "total_kills": self.total_kills,
            "total_deaths": self.total_deaths,
            "upgrades": {uid: asdict(upgrade) for uid, upgrade in self.upgrades.items()},
            "achievements": self.achievements
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"영구 진행상황 저장 실패: {e}")
            return False
    
    def load_from_file(self, filename: str = "permanent_progress.json"):
        """영구 진행상황 로드"""
        if not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.star_fragments = data.get("star_fragments", data.get("stellar_essence", 0))  # 호환성을 위해 stellar_essence도 확인
            self.total_runs = data.get("total_runs", 0)
            self.best_floor = data.get("best_floor", 0)
            self.total_kills = data.get("total_kills", 0)
            self.total_deaths = data.get("total_deaths", 0)
            self.achievements = data.get("achievements", {})
            
            # 업그레이드 로드
            if "upgrades" in data:
                for uid, upgrade_data in data["upgrades"].items():
                    if uid in self.upgrades:
                        self.upgrades[uid].current_level = upgrade_data.get("current_level", 0)
            
            return True
        except Exception as e:
            print(f"영구 진행상황 로드 실패: {e}")
            return False
    
    def get_upgrade_menu_display(self) -> List[str]:
        """업그레이드 메뉴 표시용 텍스트"""
        lines = [
            f"별조각: {self.star_fragments}",
            f"총 플레이: {self.total_runs}회 | 최고 층: {self.best_floor}층",
            f"총 처치: {self.total_kills}마리 | 사망: {self.total_deaths}회",
            "",
            "=== 영구 업그레이드 ==="
        ]
        
        for i, (uid, upgrade) in enumerate(self.upgrades.items(), 1):
            status = f"({upgrade.current_level}/{upgrade.max_level})"
            cost = upgrade.cost * (upgrade.current_level + 1) if upgrade.current_level < upgrade.max_level else "MAX"
            effect = upgrade.get_effect_description()
            
            lines.append(f"{i:2}. {upgrade.name} {status} - {cost} 정수")
            lines.append(f"    {upgrade.description} [{effect}]")
        
        return lines

    def show_menu(self):
        """영구 성장 메뉴 표시 - 커서 네비게이션"""
        try:
            from game.cursor_menu_system import CursorMenu, MenuAction
            from game.input_utils import KeyboardInput
            from game.color_text import bright_cyan, bright_yellow, bright_green, cyan, yellow, red
            
            keyboard = KeyboardInput()
            
            while True:
                # 업그레이드 옵션 생성
                upgrade_options = []
                upgrade_descriptions = []
                upgrades_list = list(self.upgrades.items())
                
                for uid, upgrade in upgrades_list:
                    status = f"({upgrade.current_level}/{upgrade.max_level})"
                    if upgrade.current_level < upgrade.max_level:
                        cost = upgrade.cost * (upgrade.current_level + 1)
                        cost_str = f"{cost} 조각"
                        can_afford = self.star_fragments >= cost
                        if can_afford:
                            option_text = f"{upgrade.name} {status} - {cost_str}"
                        else:
                            option_text = f"🔒 {upgrade.name} {status} - {cost_str}"
                    else:
                        option_text = f"✅ {upgrade.name} {status} - MAX"
                    
                    upgrade_options.append(option_text)
                    
                    effect = upgrade.get_effect_description()
                    upgrade_descriptions.append(f"{upgrade.description} [{effect}]")
                
                # 상태 정보를 제목에 포함
                title = f"⭐ 영구 성장 시스템 ⭐\n별조각: {self.star_fragments} | 플레이: {self.total_runs}회 | 최고 층: {self.best_floor}층"
                
                # 커서 메뉴 생성
                menu = CursorMenu(title, upgrade_options, upgrade_descriptions, cancellable=True)
                
                # 메뉴 실행
                result = menu.run()
                
                if result is None:  # 취소 (Q)
                    break
                
                # 선택된 업그레이드 처리
                uid, upgrade = upgrades_list[result]
                
                if upgrade.current_level >= upgrade.max_level:
                    print(f"\n{upgrade.name}은(는) 이미 최대 레벨입니다.")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
                    continue
                
                cost = upgrade.cost * (upgrade.current_level + 1)
                
                if self.star_fragments < cost:
                    print(f"\n{red('별조각이 부족합니다.')}")
                    print(f"필요: {cost} | 보유: {self.star_fragments}")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
                    continue
                
                # 구매 확인
                confirm_options = ["✅ 구매", "❌ 취소"]
                confirm_descriptions = [
                    f"비용 {cost} 조각으로 {upgrade.name}을(를) 업그레이드합니다",
                    "업그레이드를 취소합니다"
                ]
                
                confirm_menu = CursorMenu(
                    f"업그레이드 확인\n{upgrade.name} (레벨 {upgrade.current_level} → {upgrade.current_level + 1})",
                    confirm_options, confirm_descriptions, cancellable=True
                )
                
                confirm_result = confirm_menu.run()
                
                if confirm_result == 0:  # 구매 확인
                    self.star_fragments -= cost
                    upgrade.current_level += 1
                    self.save_to_file()
                    print(f"\n{bright_green('업그레이드 완료!')} {upgrade.name} → 레벨 {upgrade.current_level}")
                    keyboard.wait_for_key("아무 키나 눌러 계속...")
                    
        except Exception as e:
            print(f"영구 성장 메뉴 오류: {e}")
            try:
                from game.input_utils import KeyboardInput
                KeyboardInput().wait_for_key("아무 키나 눌러 계속...")
            except:
                input("아무 키나 눌러 계속...")
