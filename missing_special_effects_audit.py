#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
특수 효과 누락 검사 도구
"""

# 스킬에서 발견된 모든 특수 효과들
all_special_effects = {
    # 전사 관련
    "adaptive_attack", "armor_break", "stance_adaptation", "enemy_analysis",
    "defensive_bonus", "double_attack", "aggressive_bonus", "guardian_bonus", 
    "balanced_bonus", "adaptive_ultimate",
    
    # 검성 관련
    "basic_sword_aura", "basic_sword_burst", "sword_aura_gain", "sword_aura_consume", 
    "sword_aura_wave", "piercing", "atb_refund", "atb_refund_medium", 
    "infinite_blade", "sword_aura_consume_all",
    
    # 검투사 관련  
    "arena_experience", "decisive_strike", "gladiator_skill", "parry_stance", 
    "honor_strike", "warrior_roar", "survival_spirit", "colosseum_king",
    
    # 광전사 관련
    "rage_build", "basic_vampiric", "berserk_strike", "vampire_attack", 
    "blood_shield", "vampiric_blast", "shield_consume", "madness_amplify", 
    "rage_chain", "area_vampire", "final_madness", "massive_vampire",
    
    # 기사 관련
    "knight_honor", "guardian_will", "spear_charge", "protection_oath", 
    "chivalry_spirit", "duty_counter", "survival_will", "holy_charge",
    
    # 성기사 관련
    "holy_blessing", "purify_touch", "holy_strike_sanctuary", "blessing_sanctuary", 
    "judgment_light", "sanctuary_expand", "divine_protection", "angel_descent",
    
    # 암흑기사 관련
    "darkness_power", "minor_vampiric", "vampire_slash", "dark_aura", 
    "dark_aura_passive", "vampiric_strike", "life_drain_all", "dark_dominion", "dark_lord",
    
    # 용기사 관련
    "dragon_mark", "leap_attack", "dragon_scale", "dragon_breath", 
    "dragon_majesty", "dragon_lord_ultimate", "dragon_awakening",
    
    # 아크메이지 관련
    "lightning_count", "fire_count", "ice_count", "elemental_mastery", 
    "elemental_fusion", "elemental_cycle", "all_elements_burst", "magic_storm",
    
    # 정령술사 관련
    "spirit_bond", "earth_rage", "four_elements",
    
    # 시간술사 관련
    "time_record_savepoint", "future_sight", "time_rewind_to_savepoint", 
    "time_stop", "spacetime_collapse",
    
    # 차원술사 관련
    "afterimage", "dimension_cloak", "space_leap", "dimension_maze", 
    "evasion_counter", "untouchable_state",
    
    # 철학자 관련
    "truth_insight", "philosophical_thought", "existence_denial", "absolute_truth",
    
    # 궁수 관련
    "precision_stack", "arrow_penetration", "triple_shot", "piercing_shot", 
    "support_fire_activation", "hunter_mode",
    
    # 암살자 관련
    "generate_shadow", "shadow_execution", "shadow_echo", "poison_weapon", 
    "smoke_bomb", "assassination", "consume_all_shadows",
    
    # 도적 관련
    "poison_stack", "lethal_strike", "corrosive_poison", "poison_trigger", 
    "poison_fog_enhanced", "plague_spread", "venom_explosion", "toxic_cocktail", 
    "poison_field", "venom_burst", "venom_absorption", "poison_emperor",
    
    # 해적 관련
    "treasure_hunt", "pirate_plunder", "combo_attack", "ghost_fleet",
    
    # 사무라이 관련
    "samurai_focus", "bushido_spirit", "mushin_cut",
    
    # 바드 관련
    "melody_build", "sonic_burst", "divine_song", "heavenly_chorus", "soul_analysis",
    
    # 드루이드 관련
    "nature_bond", "wild_instinct", "animal_form", "lightning_storm", 
    "gaia_wrath", "nature_judgment",
    
    # 신관 관련
    "atonement_stack", "divine_release", "holy_light", "greater_heal", 
    "resurrect", "divine_punishment", "heaven_gate",
    
    # 무당 관련
    "divine_accumulation", "blessing_beam", "purify_light", "martyrdom_path", "divine_judgment",
    
    # 몽크 관련
    "chi_circulation", "combo_chain", "mp_restore_15pct", "ki_explosion", 
    "armor_pierce", "enlightenment",
    
    # 마검사 관련
    "elemental_blade", "elemental_burst", "elemental_weapon", "magic_field", "perfect_fusion",
    
    # 연금술사 관련
    "transmute_item", "instant_potion", "acid_corrosion", "philosophers_stone",
    
    # 기계공학자 관련
    "machine_charge", "energy_discharge", "auto_turret_install", "precision_laser", 
    "multi_missile", "repair_drone", "giga_turret",
    
    # 네크로맨서 관련
    "soul_harvest", "life_drain", "summon_undead", "life_steal"
}

# 현재 핸들러에 등록된 효과들 (get_special_effect_handlers에서 확인됨)
registered_effects = {
    "berserk_strike", "vampire_attack", "blood_shield", "vampiric_blast", 
    "shield_consume", "madness_amplify", "rage_chain", "area_vampire", 
    "final_madness", "massive_vampire", "rage_seed", "blood_thirst", 
    "mad_combo", "rage_explosion", "gladiator_honor", "colosseum_king", 
    "elemental_mastery", "elemental_weakness", "elemental_fusion", 
    "poison_stack", "venom_burst", "deadly_poison", "poison_amplify", 
    "corrosive_poison", "poison_weapon", "dragon_scale", "draconic_might", 
    "dragon_breath", "resurrect", "life_steal", "dispel_all", "analyze_enemy", 
    "adaptive_attack", "armor_break", "stance_adaptation", "enemy_analysis", 
    "guardian_bonus", "accuracy", "accuracy_boost", "brv_boost", "damage_boost", 
    "critical_boost", "never_miss", "perfect_accuracy", "guaranteed_critical", 
    "first_strike", "berserk", "combo_bonus", "double_damage", "piercing", 
    "multi_hit", "stun_chance", "armor_penetration", "basic_sword_aura", 
    "basic_sword_burst", "sword_aura_gain", "sword_aura_consume", 
    "sword_aura_wave", "atb_refund", "atb_refund_medium", "infinite_blade", 
    "sword_aura_consume_all", "arena_experience", "decisive_strike", 
    "gladiator_skill", "parry_stance", "honor_strike", "warrior_roar", 
    "survival_spirit", "rage_build", "basic_vampiric", "double_attack", 
    "aggressive_bonus", "defensive_bonus", "balanced_bonus", "adaptive_ultimate", 
    "magic_wave", "magic_blast", "random_element_effect", "mana_recovery", 
    "mana_explosion", "overload_magic", "chain_magic", "ultimate_magic", 
    "triple_shot", "piercing_shot", "rapid_fire", "precision_shot", 
    "arrow_rain", "explosive_arrow", "wind_shot", "ultimate_shot", 
    "truth_insight", "life_drain", "combo_attack", "summon_undead",
    
    # 추가된 누락 효과들
    "absolute_truth", "acid_corrosion", "afterimage", "all_elements_burst",
    "angel_descent", "animal_form", "armor_pierce", "arrow_penetration",
    "assassination", "atonement_stack", "auto_turret_install", "blessing_beam",
    "blessing_sanctuary", "bushido_spirit", "chi_circulation", "chivalry_spirit",
    "combo_chain", "consume_all_shadows", "dark_aura", "dark_aura_passive",
    "dark_dominion", "dark_lord", "darkness_power", "dimension_cloak",
    "dimension_maze", "divine_accumulation", "divine_judgment", "divine_protection",
    "divine_punishment", "divine_release", "divine_song", "dragon_awakening",
    "dragon_lord_ultimate", "dragon_majesty", "dragon_mark", "duty_counter",
    "earth_rage", "elemental_blade", "elemental_burst", "elemental_cycle",
    "elemental_weapon", "energy_discharge", "enlightenment", "evasion_counter",
    "existence_denial", "fire_count", "four_elements", "future_sight",
    "gaia_wrath", "generate_shadow", "ghost_fleet", "giga_turret",
    "greater_heal", "guardian_will", "heaven_gate", "heavenly_chorus",
    "holy_blessing", "holy_charge", "holy_light", "holy_strike_sanctuary",
    "hunter_mode", "ice_count", "instant_potion", "judgment_light",
    "ki_explosion", "knight_honor", "leap_attack", "lethal_strike",
    "life_drain_all", "lightning_count", "lightning_storm", "machine_charge",
    "magic_field", "magic_storm", "martyrdom_path", "melody_build",
    "minor_vampiric", "mp_restore_15pct", "multi_missile", "mushin_cut",
    "nature_bond", "nature_judgment", "perfect_fusion", "philosophers_stone",
    "philosophical_thought", "pirate_plunder", "plague_spread", "poison_emperor",
    "poison_field", "poison_fog_enhanced", "poison_trigger", "precision_laser",
    "precision_stack", "protection_oath", "purify_light", "purify_touch",
    "repair_drone", "samurai_focus", "sanctuary_expand", "shadow_echo",
    "shadow_execution", "smoke_bomb", "sonic_burst", "soul_analysis",
    "soul_harvest", "space_leap", "spacetime_collapse", "spear_charge",
    "spirit_bond", "support_fire_activation", "survival_will", "time_record_savepoint",
    "time_rewind_to_savepoint", "time_stop", "toxic_cocktail", "transmute_item",
    "treasure_hunt", "untouchable_state", "vampire_slash", "vampiric_strike",
    "venom_absorption", "venom_explosion", "wild_instinct",
    
    # 기존 효과들
    "absolute_defense", "shield_bash", "blood_drain", "dark_blessing",
    "meditation", "fury_blow", "soul_song", "death_touch", "shadow_strike",
    "laser_shot", "mega_laser", "spirit_strike", "soul_separation",
    "dual_wield_combo", "pirate_treasure", "iai_slash", "bushido_secret",
    "nature_wrath", "logical_refutation", "truth_enlightenment", "arena_technique",
    "arena_finale", "lance_charge", "blessing_light", "magic_sword_aura",
    "magic_sword_mastery", "berserker_combo", "flame_burst", "frost_nova",
    "lightning_strike", "earth_shake", "healing_boost", "mana_drain",
    "status_immunity"
}

# 누락된 효과들 찾기
missing_effects = all_special_effects - registered_effects

print("🔍 특수 효과 누락 검사 결과")
print("="*50)
print(f"📊 총 발견된 특수 효과: {len(all_special_effects)}개")
print(f"✅ 등록된 효과: {len(registered_effects)}개")
print(f"❌ 누락된 효과: {len(missing_effects)}개")
print()

if missing_effects:
    print("🚨 누락된 특수 효과들:")
    for effect in sorted(missing_effects):
        print(f"  - {effect}")
    print()
    print("💡 이 효과들은 핸들러가 구현되지 않아서 '알 수 없는 특수 효과' 에러가 발생할 수 있습니다.")
else:
    print("✨ 모든 특수 효과가 등록되어 있습니다!")
