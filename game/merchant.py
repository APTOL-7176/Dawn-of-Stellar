#!/usr/bin/env python3
"""
상인 및 상점 시스템
"""

import random
from typing import List, Optional, Dict, Tuple
from .items import Item, ItemDatabase, ItemType, ItemRarity
from .character import Character


class ShopItem:
    """상점 아이템 (가격 포함)"""
    
    def __init__(self, item: Item, price: int, stock: int = 1):
        self.item = item
        self.price = price
        self.stock = stock
        
    def get_display_name(self) -> str:
        """표시용 이름 (재고 포함)"""
        return f"{self.item.name} (x{self.stock}) - {self.price}G"


class Merchant:
    """상인 클래스"""
    
    def __init__(self, name: str, merchant_type: str = "일반"):
        self.name = name
        self.merchant_type = merchant_type
        self.shop_items: List[ShopItem] = []
        self.gold = 1000  # 상인의 보유 골드
        self.generate_inventory()
        
    def generate_inventory(self):
        """상인 인벤토리 생성"""
        db = ItemDatabase()
        
        # 상인 타입에 따른 아이템 생성
        item_count = random.randint(5, 10)
        
        for _ in range(item_count):
            # 희귀도별 확률 (상인 타입에 따라 조정)
            if self.merchant_type == "고급":
                rarity_weights = [40, 30, 20, 8, 2]  # 일반~전설
            elif self.merchant_type == "전문":
                rarity_weights = [20, 40, 25, 12, 3]
            else:  # 일반 상인
                rarity_weights = [60, 25, 10, 4, 1]
            
            # 랜덤 아이템 생성
            item = db.get_random_item()
            if item:
                # 가격 계산 (기본 가격의 1.2~1.8배)
                price_multiplier = random.uniform(1.2, 1.8)
                price = int(item.value * price_multiplier)
                
                # 재고 설정
                if item.item_type == ItemType.CONSUMABLE:
                    stock = random.randint(1, 5)
                else:
                    stock = random.randint(1, 2)
                
                shop_item = ShopItem(item, price, stock)
                self.shop_items.append(shop_item)
    
    def buy_item_with_party_gold(self, party_manager, customer, item_index: int) -> Tuple[bool, str]:
        """파티 골드를 사용하여 아이템 구매"""
        if item_index < 0 or item_index >= len(self.shop_items):
            return False, "잘못된 아이템 선택"
        
        shop_item = self.shop_items[item_index]
        
        # 파티 골드 확인
        if not party_manager.has_enough_gold(shop_item.price):
            return False, f"골드가 부족합니다 ({party_manager.get_total_gold()}G/{shop_item.price}G)"
        
        # 인벤토리 확인
        can_add, reason = customer.inventory.can_add_item(shop_item.item)
        if not can_add:
            return False, f"인벤토리 문제: {reason}"
        
        # 거래 실행
        party_manager.spend_gold(shop_item.price)
        self.gold += shop_item.price
        customer.inventory.add_item(shop_item.item)
        
        # 재고 감소
        shop_item.stock -= 1
        if shop_item.stock <= 0:
            self.shop_items.remove(shop_item)
        
        return True, f"{customer.name}이(가) {shop_item.item.name}을(를) 구매했습니다!"
    
    def buy_item(self, customer, item_index: int) -> Tuple[bool, str]:
        """아이템 구매"""
        if item_index < 0 or item_index >= len(self.shop_items):
            return False, "잘못된 아이템 선택"
        
        shop_item = self.shop_items[item_index]
        
        # 골드 확인
        if customer.gold < shop_item.price:
            return False, f"골드가 부족합니다 ({customer.gold}G/{shop_item.price}G)"
        
        # 인벤토리 확인
        can_add, reason = customer.inventory.can_add_item(shop_item.item)
        if not can_add:
            return False, f"인벤토리 문제: {reason}"
        
        # 거래 실행
        customer.gold -= shop_item.price
        self.gold += shop_item.price
        customer.inventory.add_item(shop_item.item)
        
        # 재고 감소
        shop_item.stock -= 1
        if shop_item.stock <= 0:
            self.shop_items.remove(shop_item)
        
        return True, f"{shop_item.item.name}을(를) {shop_item.price}G에 구매했습니다"
    
    def sell_item(self, customer: Character, item_name: str) -> tuple:
        """아이템 판매 (고객이 상인에게)"""
        if not customer.inventory.has_item(item_name):
            return False, "해당 아이템을 보유하고 있지 않습니다"
        
        db = ItemDatabase()
        item = db.get_item(item_name)
        if not item:
            return False, "알 수 없는 아이템입니다"
        
        # 판매 가격 (기본 가격의 50~70%)
        sell_price = int(item.value * random.uniform(0.5, 0.7))
        
        # 상인의 골드 확인
        if self.gold < sell_price:
            return False, "상인의 골드가 부족합니다"
        
        # 거래 실행
        customer.inventory.remove_item(item_name)
        customer.gold += sell_price
        self.gold -= sell_price
        
        return True, f"{item_name}을(를) {sell_price}G에 판매했습니다"
    
    def sell_item_to_party(self, party_manager, customer: Character, item_name: str) -> tuple:
        """아이템 판매 (파티 골드로 수익)"""
        if not customer.inventory.has_item(item_name):
            return False, "해당 아이템을 보유하고 있지 않습니다"
        
        db = ItemDatabase()
        item = db.get_item(item_name)
        if not item:
            return False, "알 수 없는 아이템입니다"
        
        # 판매 가격 (기본 가격의 50~70%)
        sell_price = int(item.value * random.uniform(0.5, 0.7))
        
        # 상인의 골드 확인
        if self.gold < sell_price:
            return False, "상인의 골드가 부족합니다"
        
        # 거래 실행 (파티 골드로)
        customer.inventory.remove_item(item_name)
        party_manager.add_gold(sell_price)
        self.gold -= sell_price
        
        return True, f"{item_name}을(를) {sell_price}G에 판매했습니다 (파티 골드에 추가)"
    
    def sell_party_item(self, party_manager, item_name: str) -> tuple:
        """파티 공용 인벤토리에서 아이템 판매"""
        # 파티 인벤토리에서 아이템 확인
        if not party_manager.shared_inventory.has_item(item_name):
            return False, "파티 인벤토리에 해당 아이템이 없습니다"
        
        db = ItemDatabase()
        item = db.get_item(item_name)
        if not item:
            return False, "알 수 없는 아이템입니다"
        
        # 판매 가격 (기본 가격의 50~70%)
        sell_price = int(item.value * random.uniform(0.5, 0.7))
        
        # 상인의 골드 확인
        if self.gold < sell_price:
            return False, "상인의 골드가 부족합니다"
        
        # 거래 실행
        party_manager.shared_inventory.remove_item(item_name, 1)
        party_manager.add_gold(sell_price)
        self.gold -= sell_price
        
        return True, f"{item_name}을(를) {sell_price}G에 판매했습니다"
    
    def get_shop_display(self) -> List[str]:
        """상점 목록 표시"""
        display = [f"=== {self.name}의 상점 ({self.merchant_type}) ==="]
        display.append(f"상인 보유 골드: {self.gold}G")
        display.append("")
        
        if not self.shop_items:
            display.append("판매할 아이템이 없습니다.")
        else:
            for i, shop_item in enumerate(self.shop_items):
                display.append(f"{i+1}. {shop_item.get_display_name()}")
        
        return display


class MerchantManager:
    """상인 관리자"""
    
    def __init__(self):
        self.merchants: List[Merchant] = []
        self.spawn_chance = 0.15  # 15% 확률로 상인 생성
        
    def try_spawn_merchant(self, floor: int) -> Optional[Merchant]:
        """상인 생성 시도"""
        if random.random() < self.spawn_chance:
            return self.create_random_merchant(floor)
        return None
    
    def create_random_merchant(self, floor: int) -> Merchant:
        """랜덤 상인 생성"""
        merchant_names = [
            "바르간", "로사", "델피", "카엘", "미르",
            "토란", "세라", "주노", "레이나", "케인"
        ]
        
        # 층수에 따른 상인 타입 결정
        if floor >= 10:
            merchant_types = ["일반", "고급", "전문"]
            weights = [40, 35, 25]
        elif floor >= 5:
            merchant_types = ["일반", "고급"]
            weights = [60, 40]
        else:
            merchant_types = ["일반"]
            weights = [100]
        
        name = random.choice(merchant_names)
        merchant_type = random.choices(merchant_types, weights=weights)[0]
        
        merchant = Merchant(name, merchant_type)
        self.merchants.append(merchant)
        
        return merchant
    
    def get_merchant_at_position(self, x: int, y: int) -> Optional[Merchant]:
        """특정 위치의 상인 반환 (향후 확장용)"""
        # 현재는 단순히 첫 번째 상인 반환
        if self.merchants:
            return self.merchants[0]
        return None
