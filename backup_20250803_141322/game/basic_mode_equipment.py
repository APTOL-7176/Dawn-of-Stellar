#!/usr/bin/env python3
"""
기본 게임모드용 장비 자동 장착 시스템 통합
"""

from typing import List, Dict
from .ai_game_mode import basic_equipment_manager, auto_equip_for_basic_mode, get_equipment_recommendations_for_basic_mode

class BasicModeEquipmentUI:
    """기본 게임모드용 장비 관리 UI"""
    
    def __init__(self):
        self.equipment_manager = basic_equipment_manager
    
    def show_auto_equip_menu(self, character, inventory_items: List = None):
        """자동 장착 메뉴 표시"""
        if not inventory_items:
            print("❌ 인벤토리에 장비할 아이템이 없습니다.")
            return
        
        print(f"\n🎒 {character.name}의 자동 장비 장착")
        print("="*50)
        
        # 현재 장착 장비 표시
        self._show_current_equipment(character)
        
        print("\n📋 옵션:")
        print("1. 🔄 모든 장비 자동 최적화")
        print("2. 📊 장비 추천 보기")
        print("3. 🔧 특정 부위만 자동 장착")
        print("4. ❌ 취소")
        
        choice = input("\n선택하세요 (1-4): ").strip()
        
        if choice == '1':
            self._auto_equip_all(character, inventory_items)
        elif choice == '2':
            self._show_equipment_recommendations(character, inventory_items)
        elif choice == '3':
            self._auto_equip_specific_slot(character, inventory_items)
        elif choice == '4':
            print("❌ 취소되었습니다.")
        else:
            print("❌ 잘못된 선택입니다.")
    
    def _show_current_equipment(self, character):
        """현재 장착 장비 표시"""
        print(f"\n👤 {character.name}의 현재 장비:")
        
        equipment_slots = {
            'weapon': '🗡️ 무기',
            'armor': '🛡️ 갑옷', 
            'helmet': '⛑️ 투구',
            'boots': '👢 신발',
            'gloves': '🧤 장갑',
            'shield': '🛡️ 방패',
            'accessory': '💍 액세서리'
        }
        
        equipped_items = getattr(character, 'equipped_items', {})
        
        for slot, slot_name in equipment_slots.items():
            item = equipped_items.get(slot)
            if item:
                item_name = getattr(item, 'name', str(item))
                enhancement = getattr(item, 'enhancement_level', 0)
                if enhancement > 0:
                    item_name += f" (+{enhancement})"
                print(f"   {slot_name}: {item_name}")
            else:
                print(f"   {slot_name}: (미착용)")
    
    def _auto_equip_all(self, character, inventory_items):
        """모든 장비 자동 최적화"""
        print(f"\n🔄 {character.name}의 장비를 자동으로 최적화합니다...")
        
        equipped_items = auto_equip_for_basic_mode(character, inventory_items)
        
        if equipped_items:
            print("\n✅ 자동 장착 완료!")
            print("📈 스탯 변화:")
            self._show_stat_changes(character)
        else:
            print("❌ 더 나은 장비를 찾을 수 없습니다.")
    
    def _show_equipment_recommendations(self, character, inventory_items):
        """장비 추천 표시"""
        print(f"\n📊 {character.name}에게 추천하는 장비:")
        
        recommendations = get_equipment_recommendations_for_basic_mode(character, inventory_items)
        
        if not recommendations:
            print("❌ 추천할 수 있는 장비가 없습니다.")
            return
        
        # 슬롯별로 정리
        slot_recommendations = {}
        for rec in recommendations:
            slot = rec.get('slot', 'unknown')
            if slot not in slot_recommendations:
                slot_recommendations[slot] = []
            slot_recommendations[slot].append(rec)
        
        slot_names = {
            'weapon': '🗡️ 무기',
            'armor': '🛡️ 갑옷',
            'helmet': '⛑️ 투구', 
            'boots': '👢 신발',
            'gloves': '🧤 장갑',
            'shield': '🛡️ 방패',
            'accessory': '💍 액세서리'
        }
        
        for slot, recs in slot_recommendations.items():
            print(f"\n{slot_names.get(slot, slot)}:")
            for i, rec in enumerate(recs[:3], 1):  # 상위 3개만 표시
                item = rec.get('item')
                reason = rec.get('reason', '스탯 향상')
                if item:
                    print(f"  {i}. {item.name} - {reason}")
    
    def _auto_equip_specific_slot(self, character, inventory_items):
        """특정 부위만 자동 장착"""
        slots = {
            '1': 'weapon',
            '2': 'armor', 
            '3': 'helmet',
            '4': 'boots',
            '5': 'gloves',
            '6': 'shield',
            '7': 'accessory'
        }
        
        slot_names = {
            'weapon': '🗡️ 무기',
            'armor': '🛡️ 갑옷',
            'helmet': '⛑️ 투구',
            'boots': '👢 신발', 
            'gloves': '🧤 장갑',
            'shield': '🛡️ 방패',
            'accessory': '💍 액세서리'
        }
        
        print("\n🔧 자동 장착할 부위를 선택하세요:")
        for key, slot in slots.items():
            print(f"{key}. {slot_names[slot]}")
        print("8. ❌ 취소")
        
        choice = input("\n선택하세요 (1-8): ").strip()
        
        if choice in slots:
            slot = slots[choice]
            slot_name = slot_names[slot]
            print(f"\n🔄 {slot_name} 자동 장착 중...")
            
            # 해당 슬롯의 최적 아이템 찾기
            best_item = self.equipment_manager._find_best_item_for_slot(
                character, slot, inventory_items, None
            )
            
            if best_item:
                success = self.equipment_manager._equip_item_to_character(
                    character, best_item, slot
                )
                if success:
                    print(f"✅ {slot_name}에 {best_item.name} 장착 완료!")
                else:
                    print(f"❌ {slot_name} 장착에 실패했습니다.")
            else:
                print(f"❌ {slot_name}에 적합한 장비를 찾을 수 없습니다.")
        elif choice == '8':
            print("❌ 취소되었습니다.")
        else:
            print("❌ 잘못된 선택입니다.")
    
    def _show_stat_changes(self, character):
        """스탯 변화 표시 (간단 버전)"""
        stats = ['attack_power', 'physical_defense', 'magic_power', 'magic_defense', 'max_hp', 'max_mp']
        
        for stat in stats:
            value = getattr(character, stat, 0)
            if value > 0:
                stat_name = {
                    'attack_power': '⚔️ 공격력',
                    'physical_defense': '🛡️ 물리방어',
                    'magic_power': '🔮 마법력',
                    'magic_defense': '✨ 마법방어', 
                    'max_hp': '❤️ 최대HP',
                    'max_mp': '💙 최대MP'
                }.get(stat, stat)
                print(f"   {stat_name}: {value}")

# 전역 UI 인스턴스
basic_equipment_ui = BasicModeEquipmentUI()

def show_basic_mode_equipment_menu(character, inventory_items: List = None):
    """기본 게임모드 장비 메뉴 진입점"""
    basic_equipment_ui.show_auto_equip_menu(character, inventory_items)
