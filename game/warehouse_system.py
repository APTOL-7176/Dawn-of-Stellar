#!/usr/bin/env python3
"""
Dawn of Stellar - 창고 시스템
아이템 보관 및 관리 시스템
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class WarehouseTab(Enum):
    """창고 탭 종류"""
    CONSUMABLES = "소모품"
    EQUIPMENT = "장비"
    WEAPONS = "무기"
    FOOD = "음식"
    MATERIALS = "재료"
    TREASURES = "보물"

@dataclass
class WarehouseSlot:
    """창고 슬롯"""
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: int = 0
    weight: float = 0.0
    tab: Optional[WarehouseTab] = None

class WarehouseSystem:
    """창고 시스템"""
    
    def __init__(self, save_path: str = "saves/warehouse.json"):
        self.save_path = Path(save_path)
        self.max_weight = 250.0  # 최대 무게 (매우 큼)
        self.current_weight = 0.0
        self.max_slots = 500  # 최대 슬롯 수
        
        # 탭별 슬롯 관리
        self.warehouse_slots: Dict[WarehouseTab, List[WarehouseSlot]] = {
            tab: [WarehouseSlot() for _ in range(100)] for tab in WarehouseTab
        }
        
        self.load_warehouse()
    
    def get_tab_weight(self, tab: WarehouseTab) -> float:
        """특정 탭의 총 무게 계산"""
        total_weight = 0.0
        for slot in self.warehouse_slots[tab]:
            if slot.item_id:
                total_weight += slot.weight * slot.quantity
        return total_weight
    
    def get_total_weight(self) -> float:
        """전체 창고 무게 계산"""
        total_weight = 0.0
        for tab in WarehouseTab:
            total_weight += self.get_tab_weight(tab)
        return total_weight
    
    def can_store_item(self, item_weight: float, quantity: int = 1) -> bool:
        """아이템 저장 가능 여부 확인"""
        new_weight = self.get_total_weight() + (item_weight * quantity)
        return new_weight <= self.max_weight
    
    def find_empty_slot(self, tab: WarehouseTab) -> Optional[int]:
        """빈 슬롯 찾기"""
        for i, slot in enumerate(self.warehouse_slots[tab]):
            if not slot.item_id:
                return i
        return None
    
    def find_item_slot(self, tab: WarehouseTab, item_id: str) -> Optional[int]:
        """같은 아이템이 있는 슬롯 찾기"""
        for i, slot in enumerate(self.warehouse_slots[tab]):
            if slot.item_id == item_id:
                return i
        return None
    
    def store_item(self, item_id: str, item_name: str, quantity: int, 
                   weight: float, tab: WarehouseTab) -> bool:
        """아이템 저장"""
        total_weight = weight * quantity
        
        if not self.can_store_item(weight, quantity):
            print(f"❌ 창고 무게 한계 초과! (현재: {self.get_total_weight():.1f}/{self.max_weight})")
            return False
        
        # 같은 아이템이 있는지 확인 (스택 가능한 경우)
        existing_slot_idx = self.find_item_slot(tab, item_id)
        
        if existing_slot_idx is not None:
            # 기존 슬롯에 추가
            slot = self.warehouse_slots[tab][existing_slot_idx]
            slot.quantity += quantity
            print(f"✅ {item_name} x{quantity} 창고에 추가! (총 {slot.quantity}개)")
        else:
            # 새 슬롯에 저장
            empty_slot_idx = self.find_empty_slot(tab)
            if empty_slot_idx is None:
                print(f"❌ {tab.value} 탭이 가득 참!")
                return False
            
            slot = self.warehouse_slots[tab][empty_slot_idx]
            slot.item_id = item_id
            slot.item_name = item_name
            slot.quantity = quantity
            slot.weight = weight
            slot.tab = tab
            print(f"✅ {item_name} x{quantity} 창고에 저장!")
        
        self.save_warehouse()
        return True
    
    def retrieve_item(self, tab: WarehouseTab, slot_index: int, 
                     quantity: int = 1) -> Optional[Tuple[str, str, int, float]]:
        """아이템 꺼내기"""
        if slot_index >= len(self.warehouse_slots[tab]):
            return None
        
        slot = self.warehouse_slots[tab][slot_index]
        if not slot.item_id or slot.quantity < quantity:
            return None
        
        # 아이템 정보 저장
        item_info = (slot.item_id, slot.item_name, quantity, slot.weight)
        
        # 수량 감소
        slot.quantity -= quantity
        
        # 수량이 0이 되면 슬롯 비우기
        if slot.quantity <= 0:
            slot.item_id = None
            slot.item_name = None
            slot.quantity = 0
            slot.weight = 0.0
            slot.tab = None
        
        print(f"✅ {item_info[1]} x{quantity} 창고에서 꺼냄!")
        self.save_warehouse()
        return item_info
    
    def get_tab_items(self, tab: WarehouseTab) -> List[Dict]:
        """특정 탭의 아이템 목록 반환"""
        items = []
        for i, slot in enumerate(self.warehouse_slots[tab]):
            if slot.item_id:
                items.append({
                    'slot_index': i,
                    'item_id': slot.item_id,
                    'item_name': slot.item_name,
                    'quantity': slot.quantity,
                    'weight': slot.weight,
                    'total_weight': slot.weight * slot.quantity
                })
        return items
    
    def get_warehouse_stats(self) -> Dict:
        """창고 통계 정보"""
        total_weight = self.get_total_weight()
        total_items = sum(
            sum(1 for slot in slots if slot.item_id)
            for slots in self.warehouse_slots.values()
        )
        
        tab_stats = {}
        for tab in WarehouseTab:
            tab_items = len([s for s in self.warehouse_slots[tab] if s.item_id])
            tab_weight = self.get_tab_weight(tab)
            tab_stats[tab.value] = {
                'items': tab_items,
                'weight': tab_weight
            }
        
        return {
            'total_weight': total_weight,
            'max_weight': self.max_weight,
            'weight_percentage': (total_weight / self.max_weight) * 100,
            'total_items': total_items,
            'max_slots': self.max_slots,
            'tab_stats': tab_stats
        }
    
    def show_warehouse_ui(self) -> Optional[str]:
        """창고 UI 표시"""
        from game.cursor_menu_system import CursorMenu
        
        while True:
            print("\n" + "="*60)
            print("🏪 Dawn of Stellar 창고 시스템")
            print("="*60)
            
            stats = self.get_warehouse_stats()
            print(f"📦 총 아이템: {stats['total_items']}")
            print(f"⚖️ 무게: {stats['total_weight']:.1f}/{stats['max_weight']} ({stats['weight_percentage']:.1f}%)")
            
            # 탭 메뉴
            tab_options = [f"{tab.value} ({stats['tab_stats'][tab.value]['items']}개)" 
                          for tab in WarehouseTab]
            tab_options.append("📊 상세 통계")
            tab_options.append("🚪 나가기")
            
            tab_menu = CursorMenu(tab_options, "창고 탭 선택")
            tab_choice = tab_menu.get_choice()
            
            if tab_choice == len(tab_options) - 1:  # 나가기
                break
            elif tab_choice == len(tab_options) - 2:  # 상세 통계
                self.show_detailed_stats()
                continue
            
            # 선택된 탭 표시
            selected_tab = list(WarehouseTab)[tab_choice]
            self.show_tab_items(selected_tab)
        
        return None
    
    def show_tab_items(self, tab: WarehouseTab):
        """탭별 아이템 표시"""
        from game.cursor_menu_system import CursorMenu
        
        while True:
            print(f"\n📦 {tab.value} 창고")
            print("-" * 40)
            
            items = self.get_tab_items(tab)
            if not items:
                print("📭 이 창고는 비어있습니다.")
                input("엔터를 눌러 돌아가기...")
                break
            
            # 아이템 목록 표시
            for item in items:
                weight_info = f"{item['total_weight']:.1f}kg"
                print(f"📦 {item['item_name']} x{item['quantity']} ({weight_info})")
            
            # 메뉴 옵션
            item_options = [f"{item['item_name']} x{item['quantity']}" for item in items]
            item_options.append("⬅️ 뒤로 가기")
            
            item_menu = CursorMenu(item_options, f"{tab.value} 아이템 선택")
            item_choice = item_menu.get_choice()
            
            if item_choice == len(item_options) - 1:  # 뒤로 가기
                break
            
            # 선택된 아이템 처리
            selected_item = items[item_choice]
            self.handle_item_action(tab, selected_item)
    
    def handle_item_action(self, tab: WarehouseTab, item: Dict):
        """아이템 액션 처리"""
        from game.cursor_menu_system import CursorMenu
        
        print(f"\n📦 {item['item_name']} x{item['quantity']}")
        print(f"⚖️ 무게: {item['total_weight']:.1f}kg")
        
        actions = ["📤 꺼내기", "📋 정보 보기", "⬅️ 뒤로 가기"]
        action_menu = CursorMenu(actions, "액션 선택")
        action_choice = action_menu.get_choice()
        
        if action_choice == 0:  # 꺼내기
            self.handle_retrieve_item(tab, item)
        elif action_choice == 1:  # 정보 보기
            self.show_item_info(item)
        # 뒤로 가기는 자동으로 처리됨
    
    def handle_retrieve_item(self, tab: WarehouseTab, item: Dict):
        """아이템 꺼내기 처리"""
        max_quantity = item['quantity']
        
        if max_quantity == 1:
            quantity = 1
        else:
            try:
                quantity = int(input(f"꺼낼 수량 (1-{max_quantity}): ") or "1")
                quantity = max(1, min(quantity, max_quantity))
            except ValueError:
                quantity = 1
        
        result = self.retrieve_item(tab, item['slot_index'], quantity)
        if result:
            print(f"✅ {result[1]} x{quantity}를 꺼냈습니다!")
            # 여기서 실제 인벤토리에 추가하는 로직을 구현할 수 있음
        else:
            print("❌ 아이템을 꺼낼 수 없습니다.")
        
        input("엔터를 눌러 계속...")
    
    def show_item_info(self, item: Dict):
        """아이템 정보 표시"""
        print(f"\n📋 {item['item_name']} 정보")
        print("-" * 30)
        print(f"🆔 ID: {item['item_id']}")
        print(f"📦 수량: {item['quantity']}")
        print(f"⚖️ 개당 무게: {item['weight']:.2f}kg")
        print(f"⚖️ 총 무게: {item['total_weight']:.2f}kg")
        
        input("엔터를 눌러 돌아가기...")
    
    def show_detailed_stats(self):
        """상세 통계 표시"""
        stats = self.get_warehouse_stats()
        
        print("\n📊 창고 상세 통계")
        print("="*40)
        print(f"📦 총 아이템 수: {stats['total_items']}")
        print(f"⚖️ 총 무게: {stats['total_weight']:.1f}/{stats['max_weight']}")
        print(f"📈 무게 사용률: {stats['weight_percentage']:.1f}%")
        
        print("\n📂 탭별 현황:")
        for tab_name, tab_stat in stats['tab_stats'].items():
            print(f"  {tab_name}: {tab_stat['items']}개 ({tab_stat['weight']:.1f}kg)")
        
        input("엔터를 눌러 돌아가기...")
    
    def save_warehouse(self):
        """창고 저장"""
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 데이터 직렬화
            warehouse_data = {}
            for tab, slots in self.warehouse_slots.items():
                warehouse_data[tab.value] = []
                for slot in slots:
                    if slot.item_id:  # 빈 슬롯은 저장하지 않음
                        warehouse_data[tab.value].append({
                            'item_id': slot.item_id,
                            'item_name': slot.item_name,
                            'quantity': slot.quantity,
                            'weight': slot.weight
                        })
            
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(warehouse_data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ 창고 저장 실패: {e}")
    
    def load_warehouse(self):
        """창고 로드"""
        try:
            if not self.save_path.exists():
                return
            
            with open(self.save_path, 'r', encoding='utf-8') as f:
                warehouse_data = json.load(f)
            
            # 데이터 역직렬화
            for tab_name, items in warehouse_data.items():
                tab = None
                for t in WarehouseTab:
                    if t.value == tab_name:
                        tab = t
                        break
                
                if tab is None:
                    continue
                
                # 슬롯 초기화
                self.warehouse_slots[tab] = [WarehouseSlot() for _ in range(100)]
                
                # 아이템 로드
                for i, item_data in enumerate(items):
                    if i >= 100:  # 슬롯 수 제한
                        break
                    
                    slot = self.warehouse_slots[tab][i]
                    slot.item_id = item_data['item_id']
                    slot.item_name = item_data['item_name']
                    slot.quantity = item_data['quantity']
                    slot.weight = item_data['weight']
                    slot.tab = tab
            
            print("✅ 창고 데이터 로드 완료!")
            
        except Exception as e:
            print(f"❌ 창고 로드 실패: {e}")

# 전역 창고 인스턴스
_warehouse_instance = None

def get_warehouse() -> WarehouseSystem:
    """창고 시스템 인스턴스 반환"""
    global _warehouse_instance
    if _warehouse_instance is None:
        _warehouse_instance = WarehouseSystem()
    return _warehouse_instance

if __name__ == "__main__":
    # 테스트
    warehouse = WarehouseSystem()
    
    # 테스트 아이템 추가
    warehouse.store_item("potion_hp", "체력 포션", 5, 0.5, WarehouseTab.CONSUMABLES)
    warehouse.store_item("sword_iron", "철검", 1, 3.0, WarehouseTab.WEAPONS)
    warehouse.store_item("bread", "빵", 10, 0.2, WarehouseTab.FOOD)
    
    # UI 테스트
    warehouse.show_warehouse_ui()
