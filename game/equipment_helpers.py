#!/usr/bin/env python3
"""
게임 전체에서 사용할 수 있는 통합 장비 관리 시스템
"""

from typing import List, Dict, Optional
from .ai_game_mode import basic_equipment_manager, auto_equip_for_basic_mode
from .basic_mode_equipment import show_basic_mode_equipment_menu

def quick_auto_equip(character, inventory_items: List = None, show_results: bool = True) -> bool:
    """빠른 자동 장착 (메뉴 없이 바로 실행)"""
    if not inventory_items:
        if show_results:
            print("❌ 장착할 아이템이 없습니다.")
        return False
    
    equipped_items = auto_equip_for_basic_mode(character, inventory_items)
    
    if equipped_items and show_results:
        print(f"🎒 {character.name} 자동 장착 완료:")
        for item_info in equipped_items:
            print(f"   ✅ {item_info}")
        return True
    elif show_results:
        print(f"❌ {character.name}에게 더 나은 장비를 찾을 수 없습니다.")
    
    return len(equipped_items) > 0

def auto_equip_party(party: List, inventory_items: List = None, show_results: bool = True) -> Dict:
    """파티 전체 자동 장착"""
    if not inventory_items:
        if show_results:
            print("❌ 장착할 아이템이 없습니다.")
        return {}
    
    results = {}
    
    if show_results:
        print("\n🎉 파티 전체 자동 장착 시작!")
        print("="*50)
    
    for character in party:
        if hasattr(character, 'name'):
            equipped_count = len(auto_equip_for_basic_mode(character, inventory_items))
            results[character.name] = equipped_count
            
            if show_results:
                if equipped_count > 0:
                    print(f"✅ {character.name}: {equipped_count}개 장비 교체")
                else:
                    print(f"⚪ {character.name}: 교체할 장비 없음")
    
    return results

def optimize_all_equipment(party: List, inventory_items: List = None, show_results: bool = True) -> Dict:
    """전체 장비 최적화 (내구도 고려)"""
    if not inventory_items:
        if show_results:
            print("❌ 최적화할 아이템이 없습니다.")
        return {}
    
    results = {}
    
    if show_results:
        print("\n🔧 전체 장비 최적화 시작!")
        print("="*50)
        print("📋 현재 장비 상태 점검 중...")
    
    for character in party:
        if not hasattr(character, 'name'):
            continue
            
        character_results = {
            'repaired': 0,
            'upgraded': 0,
            'equipped': 0,
            'durability_issues': []
        }
        
        # 1. 현재 장착된 장비의 내구도 점검
        if hasattr(character, 'equipment'):
            for slot, item in character.equipment.items():
                if item and hasattr(item, 'durability'):
                    current_dur = getattr(item, 'current_durability', item.durability)
                    max_dur = item.durability
                    
                    if current_dur < max_dur * 0.3:  # 30% 이하면 경고
                        character_results['durability_issues'].append({
                            'slot': slot,
                            'item': item.name if hasattr(item, 'name') else str(item),
                            'durability': f"{current_dur}/{max_dur}"
                        })
                        
                        # 더 나은 장비가 있는지 확인
                        better_items = [inv_item for inv_item in inventory_items 
                                      if hasattr(inv_item, 'equipment_type') and 
                                      inv_item.equipment_type.lower() == slot.lower() and
                                      getattr(inv_item, 'current_durability', inv_item.durability) > current_dur]
                        
                        if better_items:
                            # 더 나은 장비로 교체
                            best_item = max(better_items, 
                                          key=lambda x: getattr(x, 'current_durability', x.durability))
                            character.equipment[slot] = best_item
                            inventory_items.remove(best_item)
                            character_results['upgraded'] += 1
                            
                            if show_results:
                                print(f"🔄 {character.name}: {slot} 교체 ({best_item.name if hasattr(best_item, 'name') else '장비'})")
        
        # 2. 자동 장착으로 최적화
        equipped_items = auto_equip_for_basic_mode(character, inventory_items)
        character_results['equipped'] = len(equipped_items)
        
        results[character.name] = character_results
        
        if show_results:
            total_changes = character_results['upgraded'] + character_results['equipped']
            if total_changes > 0:
                print(f"✅ {character.name}: {total_changes}개 최적화 완료")
                if character_results['durability_issues']:
                    print(f"   ⚠️  내구도 문제: {len(character_results['durability_issues'])}개")
            else:
                print(f"⚪ {character.name}: 최적화 불필요")
    
    if show_results:
        print("="*50)
        print("🎯 전체 장비 최적화 완료!")
        
        # 요약 정보
        total_upgrades = sum(r['upgraded'] + r['equipped'] for r in results.values())
        total_issues = sum(len(r['durability_issues']) for r in results.values())
        
        print(f"📊 결과: {total_upgrades}개 장비 최적화, {total_issues}개 내구도 문제 해결")
    
    return results

def get_character_equipment_score(character) -> float:
    """캐릭터의 현재 장비 점수 계산"""
    character_class = getattr(character, 'character_class', '전사')
    equipped_items = getattr(character, 'equipped_items', {})
    
    if not equipped_items:
        return 0.0
    
    total_score = 0.0
    for slot, item in equipped_items.items():
        if item:
            score = basic_equipment_manager._calculate_item_score(character, item, character_class)
            total_score += score
    
    return total_score

def suggest_equipment_upgrades(character, available_items: List = None) -> List[Dict]:
    """캐릭터에게 장비 업그레이드 제안"""
    if not available_items:
        return []
    
    suggestions = []
    current_equipped = getattr(character, 'equipped_items', {})
    character_class = getattr(character, 'character_class', '전사')
    
    # 각 슬롯에 대해 현재 장비보다 좋은 장비가 있는지 확인
    equipment_slots = ['weapon', 'armor', 'helmet', 'boots', 'gloves', 'shield', 'accessory']
    
    for slot in equipment_slots:
        current_item = current_equipped.get(slot)
        current_score = 0.0
        
        if current_item:
            current_score = basic_equipment_manager._calculate_item_score(
                character, current_item, character_class
            )
        
        # 더 나은 아이템 찾기
        best_item = basic_equipment_manager._find_best_item_for_slot(
            character, slot, available_items, None
        )
        
        if best_item:
            new_score = basic_equipment_manager._calculate_item_score(
                character, best_item, character_class
            )
            
            if new_score > current_score * 1.1:  # 10% 이상 향상
                improvement = ((new_score - current_score) / max(current_score, 1)) * 100
                suggestions.append({
                    'slot': slot,
                    'current_item': current_item,
                    'suggested_item': best_item,
                    'improvement': improvement,
                    'slot_name': {
                        'weapon': '🗡️ 무기',
                        'armor': '🛡️ 갑옷',
                        'helmet': '⛑️ 투구', 
                        'boots': '👢 신발',
                        'gloves': '🧤 장갑',
                        'shield': '🛡️ 방패',
                        'accessory': '💍 액세서리'
                    }.get(slot, slot)
                })
    
    # 개선도 순으로 정렬
    suggestions.sort(key=lambda x: x['improvement'], reverse=True)
    return suggestions

def analyze_party_equipment_gaps(party: List, available_items: List = None) -> Dict:
    """파티의 장비 부족 분석"""
    if not available_items:
        return {}
    
    analysis = {
        'weakest_members': [],
        'upgrade_opportunities': {},
        'total_upgrade_potential': 0
    }
    
    # 각 멤버의 장비 점수 계산
    member_scores = []
    for character in party:
        if hasattr(character, 'name'):
            score = get_character_equipment_score(character)
            upgrades = suggest_equipment_upgrades(character, available_items)
            
            member_scores.append({
                'character': character,
                'score': score,
                'upgrade_count': len(upgrades),
                'max_improvement': max([u['improvement'] for u in upgrades]) if upgrades else 0
            })
    
    # 점수 순으로 정렬 (낮은 순)
    member_scores.sort(key=lambda x: x['score'])
    
    # 가장 약한 멤버들 (하위 50%)
    weak_count = max(1, len(member_scores) // 2)
    analysis['weakest_members'] = member_scores[:weak_count]
    
    # 업그레이드 기회 분석
    for member_data in member_scores:
        character = member_data['character']
        if hasattr(character, 'name'):
            upgrades = suggest_equipment_upgrades(character, available_items)
            if upgrades:
                analysis['upgrade_opportunities'][character.name] = upgrades
                analysis['total_upgrade_potential'] += len(upgrades)
    
    return analysis

def show_equipment_analysis_report(party: List, available_items: List = None):
    """파티 장비 분석 리포트 표시"""
    if not available_items:
        print("❌ 분석할 아이템이 없습니다.")
        return
    
    print("\n📊 파티 장비 분석 리포트")
    print("="*60)
    
    analysis = analyze_party_equipment_gaps(party, available_items)
    
    # 전체 업그레이드 기회
    total_opportunities = analysis.get('total_upgrade_potential', 0) 
    print(f"\n🔍 총 {total_opportunities}개의 장비 업그레이드 기회를 발견했습니다!")
    
    # 가장 약한 멤버들
    weakest = analysis.get('weakest_members', [])
    if weakest:
        print(f"\n⚠️ 장비 보강이 필요한 멤버들:")
        for member_data in weakest:
            character = member_data['character']
            score = member_data['score']
            upgrade_count = member_data['upgrade_count']
            if hasattr(character, 'name'):
                print(f"   📉 {character.name}: 점수 {score:.1f}, {upgrade_count}개 업그레이드 가능")
    
    # 주요 업그레이드 추천
    opportunities = analysis.get('upgrade_opportunities', {})
    if opportunities:
        print(f"\n💡 주요 업그레이드 추천:")
        for char_name, upgrades in opportunities.items():
            if upgrades:  # 빈 리스트가 아닌 경우만
                best_upgrade = upgrades[0]  # 가장 좋은 업그레이드
                slot_name = best_upgrade['slot_name']
                improvement = best_upgrade['improvement']
                suggested_item = best_upgrade['suggested_item']
                print(f"   🎯 {char_name}: {slot_name} → {suggested_item.name} (+{improvement:.1f}%)")

# 편의 함수들
def enable_auto_equip_for_character(character, inventory_items: List = None):
    """특정 캐릭터에 대해 자동 장착 활성화"""
    show_basic_mode_equipment_menu(character, inventory_items)

def batch_auto_equip_with_confirmation(party: List, inventory_items: List = None) -> bool:
    """확인 후 파티 전체 자동 장착"""
    if not inventory_items:
        print("❌ 장착할 아이템이 없습니다.")
        return False
    
    # 예상 변경사항 미리 보기
    print("\n🔍 자동 장착 예상 결과:")
    preview_results = {}
    for character in party:
        if hasattr(character, 'name'):
            upgrades = suggest_equipment_upgrades(character, inventory_items)
            preview_results[character.name] = len(upgrades)
            
            if upgrades:
                print(f"   📈 {character.name}: {len(upgrades)}개 업그레이드 예정")
            else:
                print(f"   ⚪ {character.name}: 변경 없음")
    
    total_changes = sum(preview_results.values())
    if total_changes == 0:
        print("\n❌ 변경할 장비가 없습니다.")
        return False
    
    print(f"\n📋 총 {total_changes}개 장비가 변경될 예정입니다.")
    confirm = input("계속하시겠습니까? (y/n): ").lower().strip()
    
    if confirm == 'y':
        results = auto_equip_party(party, inventory_items, show_results=True)
        return True
    else:
        print("❌ 취소되었습니다.")
        return False
