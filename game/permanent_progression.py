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
        self.stellar_essence = 0  # 별의 정수 (메타 화폐)
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
        """영구 업그레이드 초기화"""
        upgrade_data = [
            # 스탯 강화
            {
                "id": "hp_boost",
                "name": "생명력 강화",
                "description": "시작 시 최대 HP 증가",
                "cost": 5,
                "max_level": 10,
                "effect_type": "stat",
                "effect_value": 15.0
            },
            {
                "id": "attack_boost",
                "name": "공격력 강화",
                "description": "시작 시 공격력 증가",
                "cost": 8,
                "max_level": 8,
                "effect_type": "stat",
                "effect_value": 3.0
            },
            {
                "id": "defense_boost",
                "name": "방어력 강화",
                "description": "시작 시 방어력 증가",
                "cost": 6,
                "max_level": 8,
                "effect_type": "stat",
                "effect_value": 2.0
            },
            
            # 경제 관련
            {
                "id": "gold_finder",
                "name": "황금 탐지자",
                "description": "골드 획득량 증가",
                "cost": 10,
                "max_level": 5,
                "effect_type": "passive",
                "effect_value": 15.0
            },
            {
                "id": "item_luck",
                "name": "행운의 손길",
                "description": "희귀 아이템 발견 확률 증가",
                "cost": 15,
                "max_level": 5,
                "effect_type": "passive",
                "effect_value": 10.0
            },
            
            # 인벤토리 관련
            {
                "id": "inventory_expansion",
                "name": "차원 주머니",
                "description": "인벤토리 무게 한계 증가",
                "cost": 12,
                "max_level": 6,
                "effect_type": "stat",
                "effect_value": 10.0
            },
            {
                "id": "starting_items",
                "name": "모험가의 준비",
                "description": "시작 시 기본 아이템 제공",
                "cost": 20,
                "max_level": 3,
                "effect_type": "ability",
                "effect_value": 1.0
            },
            
            # 전투 관련
            {
                "id": "brave_mastery",
                "name": "용기의 숙련",
                "description": "Brave 회복량 증가",
                "cost": 15,
                "max_level": 5,
                "effect_type": "passive",
                "effect_value": 20.0
            },
            {
                "id": "exp_boost",
                "name": "빠른 성장",
                "description": "경험치 획득량 증가",
                "cost": 18,
                "max_level": 4,
                "effect_type": "passive",
                "effect_value": 25.0
            },
            
            # 특수 능력
            {
                "id": "second_chance",
                "name": "재기의 기회",
                "description": "죽음 시 일정 확률로 부활",
                "cost": 50,
                "max_level": 1,
                "effect_type": "ability",
                "effect_value": 15.0
            }
        ]
        
        for data in upgrade_data:
            upgrade = PermanentUpgrade(**data)
            self.upgrades[upgrade.id] = upgrade
    
    def initialize_achievements(self):
        """업적 초기화"""
        self.achievements = {
            "first_floor": False,      # 첫 층 클리어
            "deep_dive": False,        # 10층 도달
            "merchant_friend": False,  # 상인과 10회 거래
            "collector": False,        # 전설 아이템 10개 획득
            "survivor": False,         # 한 번도 죽지 않고 5층 클리어
            "brave_master": False,     # Brave 10000 달성
            "gold_hoarder": False,     # 골드 1000 보유
            "monster_slayer": False    # 몬스터 100마리 처치
        }
    
    def gain_stellar_essence(self, amount: int):
        """별의 정수 획득"""
        self.stellar_essence += amount
    
    def can_upgrade(self, upgrade_id: str) -> tuple:
        """업그레이드 가능 여부 확인"""
        if upgrade_id not in self.upgrades:
            return False, "존재하지 않는 업그레이드"
        
        upgrade = self.upgrades[upgrade_id]
        
        if upgrade.current_level >= upgrade.max_level:
            return False, "최대 레벨 달성"
        
        next_cost = upgrade.cost * (upgrade.current_level + 1)
        if self.stellar_essence < next_cost:
            return False, f"별의 정수 부족 ({self.stellar_essence}/{next_cost})"
        
        return True, "업그레이드 가능"
    
    def purchase_upgrade(self, upgrade_id: str) -> tuple:
        """업그레이드 구매"""
        can_upgrade, reason = self.can_upgrade(upgrade_id)
        if not can_upgrade:
            return False, reason
        
        upgrade = self.upgrades[upgrade_id]
        cost = upgrade.cost * (upgrade.current_level + 1)
        
        self.stellar_essence -= cost
        upgrade.current_level += 1
        
        return True, f"{upgrade.name} 레벨 {upgrade.current_level}로 업그레이드!"
    
    def get_stat_bonus(self, stat_name: str) -> float:
        """스탯 보너스 계산"""
        bonus = 0.0
        stat_mapping = {
            "hp": "hp_boost",
            "attack": "attack_boost",
            "defense": "defense_boost",
            "max_weight": "inventory_expansion"
        }
        
        if stat_name in stat_mapping:
            upgrade_id = stat_mapping[stat_name]
            if upgrade_id in self.upgrades:
                upgrade = self.upgrades[upgrade_id]
                bonus = upgrade.effect_value * upgrade.current_level
        
        return bonus
    
    def get_passive_bonus(self, bonus_type: str) -> float:
        """패시브 보너스 계산"""
        bonus = 0.0
        passive_mapping = {
            "gold_rate": "gold_finder",
            "item_luck": "item_luck",
            "brave_regen": "brave_mastery",
            "exp_rate": "exp_boost"
        }
        
        if bonus_type in passive_mapping:
            upgrade_id = passive_mapping[bonus_type]
            if upgrade_id in self.upgrades:
                upgrade = self.upgrades[upgrade_id]
                bonus = upgrade.effect_value * upgrade.current_level
        
        return bonus
    
    def check_achievement(self, achievement_id: str, condition_met: bool = True):
        """업적 달성 확인"""
        if achievement_id in self.achievements and not self.achievements[achievement_id]:
            if condition_met:
                self.achievements[achievement_id] = True
                return True  # 새 업적 달성
        return False
    
    def on_run_end(self, floor_reached: int, kills: int, died: bool):
        """게임 종료 시 호출"""
        self.total_runs += 1
        self.best_floor = max(self.best_floor, floor_reached)
        self.total_kills += kills
        
        if died:
            self.total_deaths += 1
        
        # 별의 정수 획득 (층수와 처치 수 기반)
        essence_gained = floor_reached + (kills // 5)
        self.gain_stellar_essence(essence_gained)
        
        # 업적 확인
        self.check_achievement("first_floor", floor_reached >= 1)
        self.check_achievement("deep_dive", floor_reached >= 10)
        self.check_achievement("monster_slayer", self.total_kills >= 100)
    
    def save_to_file(self, filename: str = "permanent_progress.json"):
        """영구 진행상황 저장"""
        data = {
            "stellar_essence": self.stellar_essence,
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
            
            self.stellar_essence = data.get("stellar_essence", 0)
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
            f"별의 정수: {self.stellar_essence}",
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
