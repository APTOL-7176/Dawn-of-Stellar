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
        """표시용 이름 (재고 및 내구도 포함)"""
        # 내구도 정보 추가
        durability_info = ""
        if hasattr(self.item, 'get_durability_percentage'):
            durability_pct = self.item.get_durability_percentage()
            if durability_pct < 100:
                durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
                durability_info = f" {durability_color}{durability_pct:.0f}%"
        elif hasattr(self.item, 'current_durability') and hasattr(self.item, 'max_durability'):
            durability_pct = (self.item.current_durability / self.item.max_durability * 100) if self.item.max_durability > 0 else 0
            durability_color = "🟢" if durability_pct > 80 else "🟡" if durability_pct > 50 else "🟠" if durability_pct > 20 else "🔴"
            durability_info = f" {durability_color}{durability_pct:.0f}%"
        
        return f"{self.item.name} (x{self.stock}){durability_info} - {self.price}G"


class Merchant:
    """상인 클래스"""
    
    def __init__(self, name: str, merchant_type: str = "일반", floor: int = 1):
        self.name = name
        self.merchant_type = merchant_type
        self.floor = floor  # 현재 층 정보 추가
        self.shop_items: List[ShopItem] = []
        self.gold = 1000  # 상인의 보유 골드
        self.last_refresh_floor = floor  # 마지막으로 상품을 갱신한 층
        self.generate_inventory()
        
    def generate_inventory(self):
        """상인 인벤토리 생성 - 층수에 따라 다른 상품"""
        self.shop_items.clear()  # 기존 상품 제거
        db = ItemDatabase()
        
        # 기본 상품 추가 (항상 판매)
        self.add_basic_items(db)
        
        # 층수에 따른 추가 아이템 개수 및 품질 조정
        base_item_count = 3 + (self.floor // 3)  # 3층마다 아이템 1개씩 추가
        additional_item_count = random.randint(base_item_count, base_item_count + 3)
        
        # 상인 타입과 층수에 따른 추가 아이템 생성
        for _ in range(additional_item_count):
            # 층수에 따른 희귀도 확률 조정
            if self.floor >= 20:  # 깊은 층
                if self.merchant_type == "전문":
                    rarity_weights = [10, 20, 30, 25, 15]  # 전설급도 15%
                elif self.merchant_type == "고급":
                    rarity_weights = [20, 25, 30, 20, 5]
                else:
                    rarity_weights = [40, 30, 20, 8, 2]
            elif self.floor >= 10:  # 중간 층
                if self.merchant_type == "전문":
                    rarity_weights = [15, 30, 35, 18, 2]
                elif self.merchant_type == "고급":
                    rarity_weights = [25, 35, 25, 12, 3]
                else:
                    rarity_weights = [50, 30, 15, 4, 1]
            else:  # 초반 층
                if self.merchant_type == "고급":
                    rarity_weights = [40, 35, 20, 4, 1]
                else:
                    rarity_weights = [70, 20, 8, 2, 0]
            
            # 랜덤 아이템 생성
            item = db.get_random_item()
            if item:
                # 층수에 따른 가격 조정 (깊을수록 비싸짐)
                floor_multiplier = 1.0 + (self.floor * 0.1)
                price_multiplier = random.uniform(1.2, 1.8) * floor_multiplier
                price = int(item.value * price_multiplier)
                
                # 재고 설정 (깊은 층일수록 희귀 아이템은 재고 적음)
                if item.item_type == ItemType.CONSUMABLE:
                    if self.floor >= 15:
                        stock = random.randint(1, 3)  # 깊은 층에서는 재고 적음
                    else:
                        stock = random.randint(2, 5)
                else:
                    stock = 1 if self.floor >= 10 else random.randint(1, 2)
                
                shop_item = ShopItem(item, price, stock)
                self.shop_items.append(shop_item)
        
        # 최소 6종 상품 보장
        while len(self.shop_items) < 6:
            item = db.get_random_item()
            if item:
                price = int(item.value * random.uniform(1.2, 1.8))
                stock = random.randint(1, 3)
                shop_item = ShopItem(item, price, stock)
                self.shop_items.append(shop_item)
        
        # 층수에 따른 상인 골드 조정
        self.gold = 500 + (self.floor * 100) + random.randint(0, 500)
        self.last_refresh_floor = self.floor
    
    def add_basic_items(self, db: ItemDatabase):
        """기본 상품 추가 - 항상 판매하는 필수 아이템들"""
        basic_items = [
            # 포션류
            ("치료 포션", 30, random.randint(3, 6)),
            ("마나 포션", 25, random.randint(2, 4)),
            # 장비류  
            ("가죽 모자", 26, 1),
            ("가죽 갑옷", 45, 1),
            # 특수 아이템
            ("안약", 45, random.randint(2, 5)),
            ("해독제", 35, random.randint(2, 4)),
        ]
        
        for item_name, base_price, stock in basic_items:
            # 해당 이름의 아이템을 DB에서 찾기
            item = db.get_item(item_name)
            if item:
                # 층수에 따른 가격 조정
                floor_multiplier = 1.0 + (self.floor * 0.05)  # 기본 상품은 가격 상승 완만
                price = int(base_price * floor_multiplier)
                shop_item = ShopItem(item, price, stock)
                self.shop_items.append(shop_item)
            else:
                # 아이템이 DB에 없으면 기본 아이템 생성
                from .items import Item, ItemType, ItemRarity
                
                if item_name == "치료 포션":
                    basic_item = Item("치료 포션", ItemType.CONSUMABLE, ItemRarity.COMMON, 
                                    "HP를 50 회복한다", 25, 0.2)
                elif item_name == "마나 포션":
                    basic_item = Item("마나 포션", ItemType.CONSUMABLE, ItemRarity.COMMON,
                                    "MP를 30 회복한다", 20, 0.2)
                elif item_name == "가죽 모자":
                    basic_item = Item("가죽 모자", ItemType.ARMOR, ItemRarity.COMMON,
                                    "기본적인 가죽 모자", 20, 0.5)
                elif item_name == "가죽 갑옷":
                    basic_item = Item("가죽 갑옷", ItemType.ARMOR, ItemRarity.COMMON,
                                    "기본적인 가죽 갑옷", 40, 2.0)
                elif item_name == "안약":
                    basic_item = Item("안약", ItemType.CONSUMABLE, ItemRarity.COMMON,
                                    "실명 상태를 치료한다", 40, 0.1)
                elif item_name == "해독제":
                    basic_item = Item("해독제", ItemType.CONSUMABLE, ItemRarity.COMMON,
                                    "독 상태를 치료한다", 30, 0.1)
                else:
                    continue  # 알 수 없는 아이템은 건너뛰기
                
                floor_multiplier = 1.0 + (self.floor * 0.05)
                price = int(base_price * floor_multiplier)
                shop_item = ShopItem(basic_item, price, stock)
                self.shop_items.append(shop_item)
    
    def refresh_inventory_if_needed(self, current_floor: int):
        """필요시 인벤토리 갱신"""
        if current_floor != self.last_refresh_floor:
            self.floor = current_floor
            self.generate_inventory()
            print(f"🔄 {self.name}이(가) {current_floor}층에 맞는 새로운 상품을 준비했습니다!")
    
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
    
    def show_shop_menu(self, party_manager=None):
        """상점 메뉴 표시 - 커서 시스템"""
        try:
            from .cursor_menu_system import create_simple_menu
            from .color_text import bright_cyan, bright_white, bright_yellow, bright_green
            
            while True:
                print(f"\n{bright_cyan('='*60)}")
                print(f"{bright_white(f'🏪 {self.name}의 상점 ({self.merchant_type})')}")
                print(f"{bright_cyan('='*60)}")
                print(f"상인 보유 골드: {bright_yellow(f'{self.gold}G')}")
                
                if party_manager:
                    print(f"파티 골드: {bright_green(f'{party_manager.get_total_gold()}G')}")
                
                options = [
                    "🛒 아이템 구매",
                    "💰 아이템 판매",
                    "📋 상점 목록 보기",
                    "❌ 나가기"
                ]
                
                descriptions = [
                    "상인에게서 아이템을 구매합니다",
                    "상인에게 아이템을 판매합니다",
                    "상점에서 판매하는 모든 아이템을 확인합니다",
                    "상점을 나갑니다"
                ]
                
                menu = create_simple_menu(f"🏪 {self.name}의 상점", options, descriptions)
                result = menu.run()
                
                if result == 0:  # 구매
                    self._show_buy_menu(party_manager)
                elif result == 1:  # 판매
                    self._show_sell_menu(party_manager)
                elif result == 2:  # 목록 보기
                    self._show_shop_items()
                else:  # 나가기
                    print(f"{bright_cyan('상점을 나갑니다. 또 오세요!')}")
                    break
                    
        except ImportError:
            # 폴백: 기존 텍스트 메뉴
            self._show_shop_menu_fallback(party_manager)
    
    def _show_buy_menu(self, party_manager=None):
        """구매 메뉴"""
        try:
            from .cursor_menu_system import create_simple_menu
            from .color_text import bright_cyan, bright_white, bright_yellow, bright_green, bright_red
            
            if not self.shop_items:
                print(f"{bright_red('판매할 아이템이 없습니다.')}")
                input("Enter를 눌러 계속...")
                return
            
            # 아이템 목록 생성
            options = []
            descriptions = []
            
            for i, shop_item in enumerate(self.shop_items):
                price_color = bright_green if (party_manager and party_manager.get_total_gold() >= shop_item.price) else bright_red
                options.append(f"{shop_item.item.name} - {price_color(f'{shop_item.price}G')} (x{shop_item.stock})")
                descriptions.append(f"{shop_item.item.description}")
            
            options.append("❌ 취소")
            descriptions.append("구매를 취소합니다")
            
            menu = create_simple_menu("🛒 아이템 구매", options, descriptions)
            result = menu.run()
            
            if result != -1 and result < len(self.shop_items):
                # 구매 시도
                if party_manager:
                    # 파티 멤버 선택
                    party_members = party_manager.get_alive_members()
                    if party_members:
                        member_options = [f"{member.name} ({member.character_class})" for member in party_members]
                        member_options.append("❌ 취소")
                        member_descriptions = [f"{member.name}에게 아이템을 줍니다" for member in party_members]
                        member_descriptions.append("구매를 취소합니다")
                        
                        member_menu = create_simple_menu("👥 아이템을 받을 파티원 선택", member_options, member_descriptions)
                        member_result = member_menu.run()
                        
                        if member_result != -1 and member_result < len(party_members):
                            selected_member = party_members[member_result]
                            success, message = self.buy_item_with_party_gold(party_manager, selected_member, result)
                            if success:
                                print(f"{bright_green(message)}")
                            else:
                                print(f"{bright_red(message)}")
                            input("Enter를 눌러 계속...")
                        
        except ImportError:
            print("구매 메뉴를 표시할 수 없습니다.")
    
    def _show_sell_menu(self, party_manager=None):
        """판매 메뉴"""
        try:
            from .cursor_menu_system import create_simple_menu
            from .color_text import bright_cyan, bright_white, bright_yellow, bright_green, bright_red
            
            if not party_manager:
                print(f"{bright_red('파티 정보가 없어 판매할 수 없습니다.')}")
                input("Enter를 눌러 계속...")
                return
            
            # 파티 멤버들의 아이템 수집
            sellable_items = []
            item_owners = []
            
            for member in party_manager.get_alive_members():
                if hasattr(member, 'inventory') and hasattr(member.inventory, 'items'):
                    for item in member.inventory.items:
                        if hasattr(item, 'name'):
                            sellable_items.append(f"{item.name} ({member.name})")
                            item_owners.append((member, item.name))
            
            if not sellable_items:
                print(f"{bright_red('판매할 아이템이 없습니다.')}")
                input("Enter를 눌러 계속...")
                return
            
            sellable_items.append("❌ 취소")
            descriptions = ["선택한 아이템을 판매합니다"] * len(item_owners)
            descriptions.append("판매를 취소합니다")
            
            menu = create_simple_menu("💰 아이템 판매", sellable_items, descriptions)
            result = menu.run()
            
            if result != -1 and result < len(item_owners):
                owner, item_name = item_owners[result]
                success, message = self.sell_item_to_party(party_manager, owner, item_name)
                if success:
                    print(f"{bright_green(message)}")
                else:
                    print(f"{bright_red(message)}")
                input("Enter를 눌러 계속...")
                
        except ImportError:
            print("판매 메뉴를 표시할 수 없습니다.")
    
    def _show_shop_items(self):
        """상점 아이템 목록 표시"""
        from .color_text import bright_cyan, bright_white, bright_yellow
        
        print(f"\n{bright_cyan('='*60)}")
        print(f"{bright_white(f'📋 {self.name}의 상품 목록')}")
        print(f"{bright_cyan('='*60)}")
        
        if not self.shop_items:
            print("판매할 아이템이 없습니다.")
        else:
            for i, shop_item in enumerate(self.shop_items, 1):
                print(f"{i}. {shop_item.item.name}")
                print(f"   💰 가격: {bright_yellow(f'{shop_item.price}G')}")
                print(f"   📦 재고: {shop_item.stock}개")
                print(f"   📝 설명: {shop_item.item.description}")
                print()
        
        input("Enter를 눌러 계속...")
    
    def _show_shop_menu_fallback(self, party_manager=None):
        """상점 메뉴 폴백 (기존 방식)"""
        while True:
            print(f"\n=== {self.name}의 상점 ({self.merchant_type}) ===")
            print(f"상인 보유 골드: {self.gold}G")
            if party_manager:
                print(f"파티 골드: {party_manager.get_total_gold()}G")
            
            print("\n1. 아이템 구매")
            print("2. 아이템 판매")
            print("3. 상점 목록 보기")
            print("0. 나가기")
            
            try:
                choice = input("선택: ").strip()
                if choice == "1":
                    print("구매 기능은 커서 시스템에서만 지원됩니다.")
                elif choice == "2":
                    print("판매 기능은 커서 시스템에서만 지원됩니다.")
                elif choice == "3":
                    for line in self.get_shop_display():
                        print(line)
                    input("Enter를 눌러 계속...")
                elif choice == "0":
                    print("상점을 나갑니다. 또 오세요!")
                    break
                else:
                    print("잘못된 선택입니다.")
            except KeyboardInterrupt:
                print("\n상점을 나갑니다.")
                break


class MerchantManager:
    """상인 관리자"""
    
    def __init__(self):
        self.merchants: Dict[int, Optional[Merchant]] = {}  # 층별 상인 관리
        self.base_spawn_chance = 0.25  # 25% 기본 확률
        self.last_merchant_floor = -1  # 마지막 상인이 나타난 층
        
    def get_spawn_chance(self, floor: int) -> float:
        """층수에 따른 상인 생성 확률 계산"""
        # 안전한 타입 체크
        if floor is None or not isinstance(floor, int):
            floor = 1
        if self.last_merchant_floor is None:
            self.last_merchant_floor = -1
            
        # 연속으로 상인이 없었다면 확률 증가
        floors_without_merchant = floor - self.last_merchant_floor - 1
        bonus_chance = min(0.3, floors_without_merchant * 0.1)  # 최대 30% 보너스
        
        # 특정 층에서는 상인 확률 증가 (5의 배수 층)
        if floor % 5 == 0:
            bonus_chance += 0.2
        
        # 깊은 층에서는 상인이 더 희귀해짐
        depth_penalty = max(0, (floor - 15) * 0.02)
        
        final_chance = self.base_spawn_chance + bonus_chance - depth_penalty
        return max(0.05, min(0.8, final_chance))  # 5%~80% 사이로 제한
    
    def try_spawn_merchant(self, floor: int) -> Optional[Merchant]:
        """상인 생성 시도 - 층별 관리"""
        # 안전한 타입 체크
        if floor is None or not isinstance(floor, int):
            floor = 1
            
        # 이미 이 층에 상인 정보가 있다면 그대로 반환
        if floor in self.merchants:
            return self.merchants[floor]
        
        spawn_chance = self.get_spawn_chance(floor)
        
        if random.random() < spawn_chance:
            merchant = self.create_random_merchant(floor)
            self.merchants[floor] = merchant
            self.last_merchant_floor = floor
            return merchant
        else:
            self.merchants[floor] = None  # 이 층에는 상인이 없음을 기록
            return None
    
    def create_random_merchant(self, floor: int) -> Merchant:
        """랜덤 상인 생성 - 층수 고려"""
        merchant_names = [
            "바르간", "로사", "델피", "카엘", "미르",
            "토란", "세라", "주노", "레이나", "케인",
            "아리스", "볼간", "엘라", "드레이크", "루나",
            "가렌", "시엘", "오리온", "베라", "자이언"
        ]
        
        # 층수에 따른 상인 타입 결정
        if floor >= 20:
            merchant_types = ["일반", "고급", "전문", "전설"]
            weights = [20, 30, 35, 15]
        elif floor >= 15:
            merchant_types = ["일반", "고급", "전문"]
            weights = [25, 40, 35]
        elif floor >= 10:
            merchant_types = ["일반", "고급", "전문"]
            weights = [35, 40, 25]
        elif floor >= 5:
            merchant_types = ["일반", "고급"]
            weights = [55, 45]
        else:
            merchant_types = ["일반", "고급"]
            weights = [75, 25]
        
        name = random.choice(merchant_names)
        merchant_type = random.choices(merchant_types, weights=weights)[0]
        
        merchant = Merchant(name, merchant_type, floor)
        
        return merchant
    
    def get_merchant_at_floor(self, floor: int) -> Optional[Merchant]:
        """특정 층의 상인 반환"""
        return self.merchants.get(floor, None)
    
    def refresh_merchant_inventory(self, floor: int):
        """특정 층 상인의 인벤토리 갱신"""
        if floor in self.merchants and self.merchants[floor]:
            self.merchants[floor].refresh_inventory_if_needed(floor)
    
    def get_merchant_info(self, floor: int) -> str:
        """상인 정보 문자열 반환"""
        merchant = self.get_merchant_at_floor(floor)
        if merchant:
            return f"🏪 {merchant.name} ({merchant.merchant_type} 상인) - {len(merchant.shop_items)}개 상품"
        else:
            spawn_chance = self.get_spawn_chance(floor)
            return f"🚫 이 층에는 상인이 없습니다 (다음 층 상인 확률: {spawn_chance:.1%})"
