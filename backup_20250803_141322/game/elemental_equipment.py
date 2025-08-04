#!/usr/bin/env python3
"""
원소 저항 및 특수 효과 장비 시스템
"""

from game.items import Item, ItemType, ItemRarity
from game.status_effects import ElementType

def create_elemental_equipment():
    """원소 저항 및 특수 효과가 있는 장비들 생성"""
    items = []
    
    # === 원소 저항 방어구 ===
    
    # 화염 저항 갑옷
    fire_cloak = Item("화염의 망토", ItemType.ARMOR, ItemRarity.RARE,
                      "드래곤의 비늘로 만든 화염 저항 망토", 400, 3.0)
    fire_cloak.stats = {"physical_defense": 12, "magic_defense": 15}
    fire_cloak.elemental_resistances = {ElementType.FIRE: 0.5}  # 50% 화염 저항
    fire_cloak.elemental_weaknesses = {ElementType.ICE: 0.25}   # 빙결에 취약
    fire_cloak.special_properties = ["burn_immunity"]
    items.append(fire_cloak)
    
    # 빙결 저항 갑옷
    frost_armor = Item("서리의 갑옷", ItemType.ARMOR, ItemRarity.RARE,
                       "영원한 얼음으로 만든 갑옷", 420, 4.5)
    frost_armor.stats = {"physical_defense": 18, "magic_defense": 8}
    frost_armor.elemental_resistances = {ElementType.ICE: 0.6}  # 60% 빙결 저항
    frost_armor.elemental_weaknesses = {ElementType.FIRE: 0.3}  # 화염에 취약
    frost_armor.special_properties = ["freeze_immunity", "cold_aura"]
    items.append(frost_armor)
    
    # 번개 저항 갑옷
    storm_plate = Item("폭풍의 판금", ItemType.ARMOR, ItemRarity.EPIC,
                       "번개를 흡수하는 신비한 갑옷", 800, 6.0)
    storm_plate.stats = {"physical_defense": 22, "magic_defense": 12, "speed": 5}
    storm_plate.elemental_resistances = {ElementType.LIGHTNING: 0.7}  # 70% 번개 저항
    storm_plate.special_properties = ["lightning_immunity", "shock_reflect"]
    items.append(storm_plate)
    
    # 독 저항 갑옷
    plague_guard = Item("역병 방어구", ItemType.ARMOR, ItemRarity.UNCOMMON,
                        "독과 질병을 막아주는 특수 갑옷", 250, 3.5)
    plague_guard.stats = {"physical_defense": 10, "magic_defense": 18}
    plague_guard.elemental_resistances = {ElementType.POISON: 0.8}  # 80% 독 저항
    plague_guard.special_properties = ["poison_immunity", "disease_immunity"]
    items.append(plague_guard)
    
    # 어둠 저항 갑옷
    light_mail = Item("빛의 사슬갑옷", ItemType.ARMOR, ItemRarity.RARE,
                      "신성한 빛으로 축복받은 갑옷", 500, 4.0)
    light_mail.stats = {"physical_defense": 15, "magic_defense": 20}
    light_mail.elemental_resistances = {ElementType.DARK: 0.6, ElementType.LIGHT: 0.3}
    light_mail.elemental_weaknesses = {ElementType.DARK: -0.2}  # 어둠에 더 강함
    light_mail.special_properties = ["curse_immunity", "undead_ward"]
    items.append(light_mail)
    
    # === 특수 효과 무기 ===
    
    # 원소 무효화 검
    null_blade = Item("무효화의 검", ItemType.WEAPON, ItemRarity.LEGENDARY,
                      "모든 원소를 무효화시키는 전설의 검", 2000, 5.0)
    null_blade.stats = {"physical_attack": 30, "magic_attack": 15}
    null_blade.elemental_resistances = {
        ElementType.FIRE: 0.9, ElementType.ICE: 0.9, ElementType.LIGHTNING: 0.9,
        ElementType.EARTH: 0.9, ElementType.WIND: 0.9, ElementType.WATER: 0.9,
        ElementType.DARK: 0.9, ElementType.LIGHT: 0.9, ElementType.POISON: 0.9
    }
    null_blade.special_properties = ["element_nullify", "status_cleanse_on_hit"]
    items.append(null_blade)
    
    # 변환의 검 (공격할 때마다 원소가 바뀜)
    chaos_blade = Item("혼돈의 검", ItemType.WEAPON, ItemRarity.EPIC,
                       "매번 다른 원소로 공격하는 불안정한 검", 800, 4.0)
    chaos_blade.stats = {"physical_attack": 22, "magic_attack": 12}
    chaos_blade.special_properties = ["random_element", "chaos_strike"]
    items.append(chaos_blade)
    
    # 흡수의 검 (적의 원소 저항을 흡수)
    drain_sword = Item("흡수의 검", ItemType.WEAPON, ItemRarity.EPIC,
                       "적의 힘을 흡수하는 검", 700, 3.5)
    drain_sword.stats = {"physical_attack": 20, "magic_attack": 8}
    drain_sword.special_properties = ["resistance_drain", "power_absorb"]
    items.append(drain_sword)
    
    # === 특수 효과 장신구 ===
    
    # 원소 순환 목걸이
    element_cycle = Item("원소 순환 목걸이", ItemType.ACCESSORY, ItemRarity.RARE,
                         "착용자의 원소 친화도를 순환시키는 목걸이", 600, 0.5)
    element_cycle.stats = {"magic_attack": 10, "magic_defense": 10}
    element_cycle.special_properties = ["element_rotation", "mana_efficiency"]
    items.append(element_cycle)
    
    # 적응의 반지
    adapt_ring = Item("적응의 반지", ItemType.ACCESSORY, ItemRarity.EPIC,
                      "받은 데미지 타입에 점차 저항하게 되는 반지", 900, 0.3)
    adapt_ring.stats = {"magic_defense": 15}
    adapt_ring.special_properties = ["damage_adaptation", "resistance_learning"]
    items.append(adapt_ring)
    
    # 반사의 방패
    mirror_shield = Item("반사의 방패", ItemType.ARMOR, ItemRarity.EPIC,
                         "마법 공격을 반사하는 방패", 1000, 5.0)
    mirror_shield.stats = {"physical_defense": 25, "magic_defense": 30}
    mirror_shield.special_properties = ["spell_reflect", "magic_immunity_chance"]
    items.append(mirror_shield)
    
    # === 특이한 효과 장비 ===
    
    # 시간 정지 건틀릿
    time_gauntlet = Item("시간의 건틀릿", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                         "시간의 흐름을 조작할 수 있는 건틀릿", 3000, 2.0)
    time_gauntlet.stats = {"speed": 20, "magic_attack": 15}
    time_gauntlet.special_properties = ["time_stop", "haste_aura", "slow_immunity"]
    items.append(time_gauntlet)
    
    # 재생의 갑옷
    regen_armor = Item("재생의 갑옷", ItemType.ARMOR, ItemRarity.RARE,
                       "착용자를 지속적으로 치유하는 갑옷", 600, 4.0)
    regen_armor.stats = {"physical_defense": 16, "magic_defense": 12}
    regen_armor.special_properties = ["auto_heal", "wound_recovery", "hp_boost"]
    items.append(regen_armor)
    
    # 마나 흡수 로브
    mana_robe = Item("마나 흡수 로브", ItemType.ARMOR, ItemRarity.EPIC,
                     "주변의 마나를 흡수하는 마법사의 로브", 800, 2.0)
    mana_robe.stats = {"magic_attack": 18, "magic_defense": 22}
    mana_robe.special_properties = ["mana_absorb", "spell_power_boost", "mp_efficiency"]
    items.append(mana_robe)
    
    # 도발의 투구
    taunt_helm = Item("도발의 투구", ItemType.ARMOR, ItemRarity.UNCOMMON,
                      "적의 어그로를 끌어모으는 투구", 300, 3.0)
    taunt_helm.stats = {"physical_defense": 20, "physical_attack": 5}
    taunt_helm.special_properties = ["auto_taunt", "threat_increase", "damage_reduction"]
    items.append(taunt_helm)
    
    return items

def apply_equipment_effects(character, equipped_items):
    """장착된 장비의 효과를 캐릭터에게 적용"""
    total_resistances = {}
    total_weaknesses = {}
    active_properties = []
    
    for item in equipped_items:
        if item is None:
            continue
            
        # 원소 저항 합산
        for element, resistance in item.elemental_resistances.items():
            if element in total_resistances:
                total_resistances[element] = min(0.95, total_resistances[element] + resistance)  # 최대 95% 저항
            else:
                total_resistances[element] = resistance
        
        # 원소 약점 합산
        for element, weakness in item.elemental_weaknesses.items():
            if element in total_weaknesses:
                total_weaknesses[element] += weakness
            else:
                total_weaknesses[element] = weakness
        
        # 특수 속성 수집
        active_properties.extend(item.special_properties)
    
    # 캐릭터에 적용
    character.equipment_resistances = total_resistances
    character.equipment_weaknesses = total_weaknesses
    character.equipment_properties = active_properties
    
    return {
        'resistances': total_resistances,
        'weaknesses': total_weaknesses,
        'properties': active_properties
    }

def get_equipment_description(item):
    """장비의 상세 설명 반환"""
    desc = [item.description]
    
    # 스탯 보너스
    if item.stats:
        stat_desc = "스탯: " + ", ".join([f"{k}+{v}" for k, v in item.stats.items()])
        desc.append(stat_desc)
    
    # 원소 저항
    if item.elemental_resistances:
        resist_desc = "저항: " + ", ".join([f"{elem.value}({int(res*100)}%)" for elem, res in item.elemental_resistances.items()])
        desc.append(resist_desc)
    
    # 원소 약점
    if item.elemental_weaknesses:
        weak_desc = "약점: " + ", ".join([f"{elem.value}({int(abs(weak)*100)}%)" for elem, weak in item.elemental_weaknesses.items()])
        desc.append(weak_desc)
    
    # 특수 속성
    if item.special_properties:
        prop_desc = "특수: " + ", ".join(item.special_properties)
        desc.append(prop_desc)
    
    return " | ".join(desc)

if __name__ == "__main__":
    # 테스트
    items = create_elemental_equipment()
    print(f"생성된 특수 장비 개수: {len(items)}개")
    print("\n=== 원소 저항 장비 목록 ===")
    for item in items:
        print(f"🎯 {item.get_colored_name()}")
        print(f"   {get_equipment_description(item)}")
        print()
