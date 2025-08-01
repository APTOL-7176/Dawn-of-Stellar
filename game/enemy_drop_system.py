#!/usr/bin/env python3
"""
적 드롭 시스템
아이템, 골드, 경험치 드롭을 관리합니다.
"""

import random
from typing import Dict, List, Tuple, Optional
from .items import Item, ItemDatabase, ItemRarity, DropRateManager
from .character import Character


class EnemyDropSystem:
    """적 드롭 시스템"""
    
    def __init__(self):
        self.item_db = ItemDatabase()
        
    def calculate_drops(self, enemy: Character, current_floor: int, party_level: int = 1) -> Dict:
        """적을 처치했을 때의 드롭 계산"""
        drops = {
            'gold': 0,
            'experience': 0,
            'items': []
        }
        
        # 기본 정보
        enemy_level = getattr(enemy, 'level', 1)
        is_elite = getattr(enemy, 'is_elite', False)
        is_boss = getattr(enemy, 'is_boss', False)
        
        # 골드 드롭 계산
        drops['gold'] = self._calculate_gold_drop(enemy_level, current_floor, is_elite, is_boss)
        
        # 경험치 드롭 계산  
        drops['experience'] = self._calculate_exp_drop(enemy_level, current_floor, is_elite, is_boss)
        
        # 아이템 드롭 계산
        drops['items'] = self._calculate_item_drops(enemy_level, current_floor, is_elite, is_boss)
        
        return drops
    
    def _calculate_gold_drop(self, enemy_level: int, floor: int, is_elite: bool, is_boss: bool) -> int:
        """골드 드롭량 계산"""
        # 기본 골드 (50층 이후 고정 배율)
        if floor >= 50:
            base_gold = 15 + (enemy_level * 3) + 100  # 50층 이후 +100 고정 보너스
        else:
            base_gold = 15 + (enemy_level * 3) + (floor * 2)
        
        # 변동폭 (±30%)
        variation = random.uniform(0.7, 1.3)
        gold = int(base_gold * variation)
        
        # 특수 적 보너스
        if is_boss:
            gold = int(gold * 3.0)  # 보스 3배
        elif is_elite:
            gold = int(gold * 1.8)  # 엘리트 1.8배
        
        return max(1, gold)  # 최소 1골드
    
    def _calculate_exp_drop(self, enemy_level: int, floor: int, is_elite: bool, is_boss: bool) -> int:
        """경험치 드롭량 계산"""
        # 기본 경험치 (40층 이후 고정 배율)
        if floor >= 40:
            base_exp = 25 + (enemy_level * 8) + 120  # 40층 이후 +120 고정 보너스
        else:
            base_exp = 25 + (enemy_level * 8) + (floor * 3)
        
        # 변동폭 (±20%)
        variation = random.uniform(0.8, 1.2)
        exp = int(base_exp * variation)
        
        # 특수 적 보너스
        if is_boss:
            exp = int(exp * 4.0)  # 보스 4배
        elif is_elite:
            exp = int(exp * 2.2)  # 엘리트 2.2배
        
        return max(1, exp)  # 최소 1경험치
    
    def _calculate_item_drops(self, enemy_level: int, floor: int, is_elite: bool, is_boss: bool) -> List[Item]:
        """아이템 드롭 계산"""
        items = []
        
        # 기본 아이템 드롭 확률 (30층 이후 고정)
        if floor >= 30:
            base_chance = 0.45  # 30층 이후 45%로 고정
        else:
            base_chance = 0.15 + (floor * 0.01)  # 층수가 올라갈수록 증가
        
        # 특수 적 아이템 드롭 확률 보너스
        if is_boss:
            base_chance = 0.95  # 보스는 95% 확률
            # 보스는 여러 아이템 드롭 가능
            for _ in range(random.randint(2, 4)):
                if random.random() < 0.8:  # 80% 확률로 추가 아이템
                    item = self._get_random_item_by_floor(floor, enemy_level, True)
                    if item:
                        items.append(item)
        elif is_elite:
            base_chance = 0.6  # 엘리트는 60% 확률
            # 엘리트는 1-2개 아이템 드롭 가능
            for _ in range(random.randint(1, 2)):
                if random.random() < 0.7:  # 70% 확률로 추가 아이템
                    item = self._get_random_item_by_floor(floor, enemy_level, False)
                    if item:
                        items.append(item)
        
        # 일반 아이템 드롭
        if random.random() < base_chance:
            item = self._get_random_item_by_floor(floor, enemy_level, False)
            if item:
                items.append(item)
        
        # 매우 낮은 확률로 보너스 아이템 (희귀템) - 50층 이후 고정
        if floor >= 50:
            bonus_chance = 0.13  # 50층 이후 13%로 고정
        else:
            bonus_chance = 0.03 + (floor * 0.002)  # 층수가 올라갈수록 증가
            
        if random.random() < bonus_chance:
            rare_item = self._get_rare_item_by_floor(floor)
            if rare_item:
                items.append(rare_item)
        
        return items
    
    def _get_random_item_by_floor(self, floor: int, enemy_level: int, is_special: bool) -> Optional[Item]:
        """층수에 맞는 랜덤 아이템 생성"""
        try:
            # 층수에 따른 희귀도 가중치 조정
            if floor >= 25:  # 깊은 층
                if is_special:
                    rarity_weights = {
                        ItemRarity.COMMON: 10,
                        ItemRarity.UNCOMMON: 25, 
                        ItemRarity.RARE: 35,
                        ItemRarity.EPIC: 25,
                        ItemRarity.LEGENDARY: 5
                    }
                else:
                    rarity_weights = {
                        ItemRarity.COMMON: 30,
                        ItemRarity.UNCOMMON: 35,
                        ItemRarity.RARE: 25,
                        ItemRarity.EPIC: 8,
                        ItemRarity.LEGENDARY: 2
                    }
            elif floor >= 15:  # 중간 층
                if is_special:
                    rarity_weights = {
                        ItemRarity.COMMON: 20,
                        ItemRarity.UNCOMMON: 35,
                        ItemRarity.RARE: 30,
                        ItemRarity.EPIC: 13,
                        ItemRarity.LEGENDARY: 2
                    }
                else:
                    rarity_weights = {
                        ItemRarity.COMMON: 45,
                        ItemRarity.UNCOMMON: 30,
                        ItemRarity.RARE: 20,
                        ItemRarity.EPIC: 4,
                        ItemRarity.LEGENDARY: 1
                    }
            else:  # 초반 층
                if is_special:
                    rarity_weights = {
                        ItemRarity.COMMON: 40,
                        ItemRarity.UNCOMMON: 35,
                        ItemRarity.RARE: 20,
                        ItemRarity.EPIC: 4,
                        ItemRarity.LEGENDARY: 1
                    }
                else:
                    rarity_weights = {
                        ItemRarity.COMMON: 65,
                        ItemRarity.UNCOMMON: 25,
                        ItemRarity.RARE: 8,
                        ItemRarity.EPIC: 2,
                        ItemRarity.LEGENDARY: 0
                    }
            
            # 가중치 기반 희귀도 선택
            rarities = list(rarity_weights.keys())
            weights = list(rarity_weights.values())
            selected_rarity = random.choices(rarities, weights=weights)[0]
            
            # 해당 희귀도의 아이템 중 랜덤 선택
            items_of_rarity = self.item_db.get_items_by_rarity(selected_rarity)
            if items_of_rarity:
                return random.choice(items_of_rarity)
            else:
                # 폴백: 랜덤 아이템
                return self.item_db.get_random_item(rarity_weights)
                
        except Exception as e:
            print(f"⚠️ 아이템 생성 중 오류: {e}")
            return None
    
    def _get_rare_item_by_floor(self, floor: int) -> Optional[Item]:
        """층수에 맞는 희귀 아이템 생성"""
        try:
            # 희귀 아이템 전용 가중치 (높은 희귀도 위주)
            if floor >= 20:
                rarity_weights = {
                    ItemRarity.RARE: 40,
                    ItemRarity.EPIC: 35,
                    ItemRarity.LEGENDARY: 25
                }
            elif floor >= 10:
                rarity_weights = {
                    ItemRarity.UNCOMMON: 20,
                    ItemRarity.RARE: 50,
                    ItemRarity.EPIC: 25,
                    ItemRarity.LEGENDARY: 5
                }
            else:
                rarity_weights = {
                    ItemRarity.UNCOMMON: 60,
                    ItemRarity.RARE: 35,
                    ItemRarity.EPIC: 5,
                    ItemRarity.LEGENDARY: 0
                }
            
            rarities = list(rarity_weights.keys())
            weights = list(rarity_weights.values())
            selected_rarity = random.choices(rarities, weights=weights)[0]
            
            items_of_rarity = self.item_db.get_items_by_rarity(selected_rarity)
            if items_of_rarity:
                return random.choice(items_of_rarity)
                
        except Exception as e:
            print(f"⚠️ 희귀 아이템 생성 중 오류: {e}")
            
        return None
    
    def apply_drop_bonuses(self, drops: Dict, party_members: List[Character] = None) -> Dict:
        """파티원의 드롭 보너스 적용"""
        if not party_members:
            return drops
        
        gold_bonus = 0.0
        exp_bonus = 0.0
        item_drop_bonus = 0.0
        
        # 파티원들의 드롭 관련 특성 확인
        for member in party_members:
            if not member.is_alive:
                continue
                
            # 골드 관련 특성
            if hasattr(member, 'traits'):
                for trait in member.traits:
                    if hasattr(trait, 'effects'):
                        if 'treasure_hunter' in trait.effects:
                            gold_bonus += trait.effects['treasure_hunter']
                        if 'lucky_strike' in trait.effects:
                            # 크리티컬 시 골드 보너스 (여기서는 일반 보너스로 적용)
                            gold_bonus += trait.effects['lucky_strike'] * 0.5
                        if 'pirate_exp' in trait.effects:
                            exp_bonus += trait.effects['pirate_exp']
                        if 'enlightenment' in trait.effects:
                            exp_bonus += trait.effects['enlightenment']
        
        # 보너스 적용
        drops['gold'] = int(drops['gold'] * (1.0 + gold_bonus))
        drops['experience'] = int(drops['experience'] * (1.0 + exp_bonus))
        
        # 아이템 드롭 보너스 (확률적으로 추가 아이템)
        if item_drop_bonus > 0 and random.random() < item_drop_bonus:
            bonus_item = self._get_random_item_by_floor(1, 1, False)  # 기본 아이템
            if bonus_item:
                drops['items'].append(bonus_item)
        
        return drops


# 전역 드롭 시스템 인스턴스
_drop_system = None

def get_drop_system() -> EnemyDropSystem:
    """드롭 시스템 싱글톤 인스턴스 반환"""
    global _drop_system
    if _drop_system is None:
        _drop_system = EnemyDropSystem()
    return _drop_system
