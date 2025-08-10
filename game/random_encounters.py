#!/usr/bin/env python3
"""
랜덤 조우 시스템 및 필드 스킬 시스템
- 최소 20종류의 랜덤 조우
- 8종류 이상의 필드 스킬
- 필드 스킬 사용 가능한 캐릭터 한정
- 쿨다운 시스템
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class EncounterType(Enum):
    """랜덤 조우 타입 - 강화된 버전"""
    TREASURE_CHEST = "보물상자"
    HEALING_SPRING = "치유의 샘"
    MERCHANT = "상인"
    TRAP = "함정"
    MYSTERIOUS_STATUE = "신비한 석상"
    WANDERING_SPIRIT = "떠도는 영혼"
    ANCIENT_RUNES = "고대 룬 문자"
    CRYSTAL_FORMATION = "수정 형태"
    ABANDONED_CAMP = "버려진 야영지"
    MONSTER_LAIR = "몬스터 소굴"
    MAGICAL_PORTAL = "마법 포털"
    WISE_HERMIT = "현명한 은둔자"
    CURSED_ALTAR = "저주받은 제단"
    LUCKY_FOUNTAIN = "행운의 분수"
    TRAINING_DUMMY = "훈련용 더미"
    ELEMENTAL_NODE = "원소 노드"
    TIME_RIFT = "시간 균열"
    SHADOW_PASSAGE = "그림자 통로"
    BLESSED_SHRINE = "축복받은 신전"
    MERCHANT_CARAVAN = "상인 마차"
    ANCIENT_LIBRARY = "고대 도서관"
    WEAPON_RACK = "무기 거치대"
    SPELL_CIRCLE = "마법진"
    MONSTER_AMBUSH = "몬스터 매복"
    
    # 새로운 인카운트 타입들
    MYSTICAL_GARDEN = "신비한 정원"
    DRAGON_NEST = "드래곤 둥지"
    ENCHANTED_MIRROR = "마법 거울"
    FORGOTTEN_TOMB = "잊혀진 무덤"
    ELEMENTAL_STORM = "원소 폭풍"
    CELESTIAL_ALTAR = "천체 제단"
    PHANTOM_SHIP = "유령선"
    CRYSTAL_CAVE = "수정 동굴"
    ANCIENT_GOLEM = "고대 골렘"
    MAGICAL_LABORATORY = "마법 실험실"
    SOUL_WELL = "영혼의 우물"
    TREASURE_GUARDIAN = "보물 수호자"
    DIMENSIONAL_TEAR = "차원 균열"
    FAIRY_RING = "요정의 고리"
    HAUNTED_FORGE = "유령 대장간"

class FieldSkillType(Enum):
    """필드 스킬 타입"""
    DETECT_TREASURE = "보물 탐지"
    HEAL_PARTY = "파티 치유"
    TELEPORT = "순간이동"
    UNLOCK = "자물쇠 해제"
    PURIFY = "정화"
    STEALTH = "은신"
    ANALYZE = "분석"
    BLESS_PARTY = "파티 축복"
    DISPEL_TRAP = "함정 해제"
    SUMMON_FAMILIAR = "사역마 소환"

class FieldSkill:
    """필드 스킬"""
    
    def __init__(self, name: str, skill_type: FieldSkillType, mp_cost: int,
                 cooldown: int, description: str, required_job: List[str]):
        self.name = name
        self.skill_type = skill_type
        self.mp_cost = mp_cost
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.description = description
        self.required_job = required_job  # 사용 가능한 직업들
    
    def can_use(self, character, current_mp: int) -> bool:
        """스킬 사용 가능 여부"""
        if self.current_cooldown > 0:
            return False
        if current_mp < self.mp_cost:
            return False
        if hasattr(character, 'job') and character.character_class.value not in self.required_job:
            return False
        return True
    
    def use(self, party: List, current_floor: int) -> Dict[str, Any]:
        """필드 스킬 사용"""
        if self.current_cooldown > 0:
            return {"success": False, "message": f"{self.name}은 아직 쿨다운 중입니다. ({self.current_cooldown}턴 남음)"}
        
        self.current_cooldown = self.cooldown
        
        if self.skill_type == FieldSkillType.DETECT_TREASURE:
            return self._detect_treasure(current_floor)
        elif self.skill_type == FieldSkillType.HEAL_PARTY:
            return self._heal_party(party)
        elif self.skill_type == FieldSkillType.TELEPORT:
            return self._teleport()
        elif self.skill_type == FieldSkillType.UNLOCK:
            return self._unlock()
        elif self.skill_type == FieldSkillType.PURIFY:
            return self._purify(party)
        elif self.skill_type == FieldSkillType.STEALTH:
            return self._stealth(party)
        elif self.skill_type == FieldSkillType.ANALYZE:
            return self._analyze(current_floor)
        elif self.skill_type == FieldSkillType.BLESS_PARTY:
            return self._bless_party(party)
        elif self.skill_type == FieldSkillType.DISPEL_TRAP:
            return self._dispel_trap()
        elif self.skill_type == FieldSkillType.SUMMON_FAMILIAR:
            return self._summon_familiar()
        
        return {"success": False, "message": "알 수 없는 스킬입니다."}
    
    def _detect_treasure(self, floor: int) -> Dict[str, Any]:
        """보물 탐지"""
        chance = random.random()
        if chance < 0.3:  # 30% 확률로 보물 발견
            treasure_value = random.randint(50 * floor, 150 * floor)
            return {
                "success": True,
                "message": f"🏆 숨겨진 보물을 발견했습니다! {treasure_value} 골드를 획득!",
                "gold": treasure_value
            }
        else:
            return {
                "success": True,
                "message": "🔍 주변을 탐지했지만 특별한 것을 찾지 못했습니다."
            }
    
    def _heal_party(self, party: List) -> Dict[str, Any]:
        """파티 치유"""
        healed_members = []
        for member in party:
            if hasattr(member, 'current_hp') and hasattr(member, 'max_hp'):
                heal_amount = min(member.max_hp - member.current_hp, int(member.max_hp * 0.3))
                if heal_amount > 0:
                    member.current_hp += heal_amount
                    healed_members.append(f"{member.name}: {heal_amount} HP 회복")
        
        if healed_members:
            return {
                "success": True,
                "message": f"💚 파티 치유 완료!\n" + "\n".join(healed_members)
            }
        else:
            return {
                "success": True,
                "message": "💚 파티원들이 모두 건강합니다."
            }
    
    def _teleport(self) -> Dict[str, Any]:
        """순간이동"""
        return {
            "success": True,
            "message": "✨ 순간이동을 사용했습니다. 안전한 곳으로 이동할 수 있습니다.",
            "effect": "teleport_option"
        }
    
    def _unlock(self) -> Dict[str, Any]:
        """자물쇠 해제"""
        return {
            "success": True,
            "message": "🔓 자물쇠 해제 기술을 사용했습니다. 다음 보물상자나 문을 쉽게 열 수 있습니다.",
            "effect": "unlock_bonus"
        }
    
    def _purify(self, party: List) -> Dict[str, Any]:
        """정화"""
        purified_members = []
        for member in party:
            if hasattr(member, 'active_statuses'):
                debuffs_removed = 0
                for status in member.active_statuses[:]:
                    # 디버프 제거 (간단한 판별)
                    if any(word in status.status_type.value for word in ["독", "화상", "마비", "혼란", "저주"]):
                        member.active_statuses.remove(status)
                        debuffs_removed += 1
                
                if debuffs_removed > 0:
                    purified_members.append(f"{member.name}: {debuffs_removed}개 디버프 제거")
        
        if purified_members:
            return {
                "success": True,
                "message": f"✨ 정화 완료!\n" + "\n".join(purified_members)
            }
        else:
            return {
                "success": True,
                "message": "✨ 파티원들에게 정화할 것이 없습니다."
            }
    
    def _stealth(self, party: List) -> Dict[str, Any]:
        """은신"""
        return {
            "success": True,
            "message": "👤 파티가 은신 상태가 되었습니다. 다음 몇 번의 이동에서 적과 마주칠 확률이 감소합니다.",
            "effect": "stealth_mode"
        }
    
    def _analyze(self, floor: int) -> Dict[str, Any]:
        """분석"""
        analysis_info = [
            f"📊 현재 층: {floor}",
            f"🎯 추천 레벨: {floor + 2}~{floor + 5}",
            f"👹 예상 적 강도: {'매우 약함' if floor <= 3 else '약함' if floor <= 7 else '보통' if floor <= 12 else '강함' if floor <= 18 else '매우 강함'}",
            f"💎 보물 등급: {'일반' if floor <= 5 else '고급' if floor <= 10 else '희귀' if floor <= 15 else '영웅' if floor <= 20 else '전설'}",
            f"🔮 마법 농도: {random.randint(floor * 10, floor * 20)}%"
        ]
        
        return {
            "success": True,
            "message": f"🔍 던전 분석 결과:\n" + "\n".join(analysis_info)
        }
    
    def _bless_party(self, party: List) -> Dict[str, Any]:
        """파티 축복"""
        blessed_members = []
        for member in party:
            # 간단한 스탯 버프 적용 (게임 시스템에 따라 조정)
            if hasattr(member, 'add_status'):
                # 축복 상태 추가 (실제 StatusEffect 객체 필요)
                blessed_members.append(f"{member.name}: 축복 효과 적용")
        
        return {
            "success": True,
            "message": f"🙏 파티 축복 완료!\n" + "\n".join(blessed_members) if blessed_members else "🙏 파티에 축복을 내렸습니다.",
            "effect": "party_blessed"
        }
    
    def _dispel_trap(self) -> Dict[str, Any]:
        """함정 해제"""
        return {
            "success": True,
            "message": "🛡️ 함정 해제 기술을 사용했습니다. 다음 함정을 안전하게 해제할 수 있습니다.",
            "effect": "trap_immunity"
        }
    
    def _summon_familiar(self) -> Dict[str, Any]:
        """사역마 소환"""
        familiar_types = ["정찰용 까마귀", "보물 찾기 쥐", "치유 요정", "전투 늑대", "마법 부엉이"]
        familiar = random.choice(familiar_types)
        
        return {
            "success": True,
            "message": f"🐾 {familiar}을(를) 소환했습니다. 일정 시간 동안 도움을 받을 수 있습니다.",
            "effect": f"familiar_{familiar.split()[0]}"
        }
    
    def reduce_cooldown(self):
        """쿨다운 감소"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class RandomEncounter:
    """랜덤 조우"""
    
    def __init__(self, encounter_type: EncounterType, min_floor: int = 1, max_floor: int = 30):
        self.encounter_type = encounter_type
        self.min_floor = min_floor
        self.max_floor = max_floor
    
    def trigger(self, party: List, current_floor: int) -> Dict[str, Any]:
        """조우 실행"""
        if not (self.min_floor <= current_floor <= self.max_floor):
            return {"success": False, "message": "이 층에서는 발생하지 않는 조우입니다."}
        
        encounter_handlers = {
            EncounterType.TREASURE_CHEST: self._treasure_chest,
            EncounterType.HEALING_SPRING: self._healing_spring,
            EncounterType.MERCHANT: self._merchant,
            EncounterType.TRAP: self._trap,
            EncounterType.MYSTERIOUS_STATUE: self._mysterious_statue,
            EncounterType.WANDERING_SPIRIT: self._wandering_spirit,
            EncounterType.ANCIENT_RUNES: self._ancient_runes,
            EncounterType.CRYSTAL_FORMATION: self._crystal_formation,
            EncounterType.ABANDONED_CAMP: self._abandoned_camp,
            EncounterType.MONSTER_LAIR: self._monster_lair,
            EncounterType.MAGICAL_PORTAL: self._magical_portal,
            EncounterType.WISE_HERMIT: self._wise_hermit,
            EncounterType.CURSED_ALTAR: self._cursed_altar,
            EncounterType.LUCKY_FOUNTAIN: self._lucky_fountain,
            EncounterType.TRAINING_DUMMY: self._training_dummy,
            EncounterType.ELEMENTAL_NODE: self._elemental_node,
            EncounterType.TIME_RIFT: self._time_rift,
            EncounterType.SHADOW_PASSAGE: self._shadow_passage,
            EncounterType.BLESSED_SHRINE: self._blessed_shrine,
            EncounterType.MERCHANT_CARAVAN: self._merchant_caravan,
            EncounterType.ANCIENT_LIBRARY: self._ancient_library,
            EncounterType.WEAPON_RACK: self._weapon_rack,
            EncounterType.SPELL_CIRCLE: self._spell_circle,
            EncounterType.MONSTER_AMBUSH: self._monster_ambush,
            
            # 새로운 인카운트 핸들러들
            EncounterType.MYSTICAL_GARDEN: self._mystical_garden,
            EncounterType.DRAGON_NEST: self._dragon_nest,
            EncounterType.ENCHANTED_MIRROR: self._enchanted_mirror,
            EncounterType.FORGOTTEN_TOMB: self._forgotten_tomb,
            EncounterType.ELEMENTAL_STORM: self._elemental_storm,
            EncounterType.CELESTIAL_ALTAR: self._celestial_altar,
            EncounterType.PHANTOM_SHIP: self._phantom_ship,
            EncounterType.CRYSTAL_CAVE: self._crystal_cave,
            EncounterType.ANCIENT_GOLEM: self._ancient_golem,
            EncounterType.MAGICAL_LABORATORY: self._magical_laboratory,
            EncounterType.SOUL_WELL: self._soul_well,
            EncounterType.TREASURE_GUARDIAN: self._treasure_guardian,
            EncounterType.DIMENSIONAL_TEAR: self._dimensional_tear,
            EncounterType.FAIRY_RING: self._fairy_ring,
            EncounterType.HAUNTED_FORGE: self._haunted_forge
        }
        
        handler = encounter_handlers.get(self.encounter_type)
        if handler:
            result = handler(party, current_floor)
            # 인카운터 타입 정보 추가
            if isinstance(result, dict):
                result['type'] = self.encounter_type.value
            return result
        
        return {"success": False, "message": "알 수 없는 조우입니다."}
    
    def _treasure_chest(self, party: List, floor: int) -> Dict[str, Any]:
        """보물상자"""
        gold = random.randint(30 * floor, 80 * floor)
        item_chance = random.random()
        
        result = {
            "success": True,
            "message": f"📦 보물상자를 발견했습니다!\n💰 {gold} 골드를 획득했습니다!",
            "gold": gold
        }
        
        if item_chance < 0.3:  # 30% 확률로 아이템도 획득
            item_name = f"층 {floor} 보물"
            result["message"] += f"\n🎁 {item_name}도 획득했습니다!"
            result["item"] = item_name
        
        return result
    
    def _healing_spring(self, party: List, floor: int) -> Dict[str, Any]:
        """치유의 샘"""
        healed = []
        for member in party:
            if hasattr(member, 'current_hp') and hasattr(member, 'max_hp'):
                heal_amount = member.max_hp - member.current_hp
                if heal_amount > 0:
                    member.current_hp = member.max_hp
                    healed.append(f"{member.name}: 완전히 회복")
                    
                    # 상처도 일부 치료
                    if hasattr(member, 'wounds'):
                        wound_heal = min(member.wounds, int(member.max_hp * 0.2))
                        member.wounds -= wound_heal
                        if wound_heal > 0:
                            healed[-1] += f", 상처 {wound_heal} 치료"
        
        return {
            "success": True,
            "message": f"💧 신비한 치유의 샘을 발견했습니다!\n" + "\n".join(healed) if healed else "💧 치유의 샘이지만 모두 건강합니다."
        }
    
    def _merchant(self, party: List, floor: int) -> Dict[str, Any]:
        """상인"""
        return {
            "success": True,
            "message": "🛍️ 떠도는 상인을 만났습니다!\n\"좋은 물건들이 있다네. 한번 둘러보겠나?\"",
            "effect": "open_shop"
        }
    
    def _trap(self, party: List, floor: int) -> Dict[str, Any]:
        """함정"""
        trap_damage = random.randint(10 * floor, 25 * floor)
        damaged_member = random.choice(party) if party else None
        
        if damaged_member and hasattr(damaged_member, 'take_hp_damage'):
            actual_damage = damaged_member.take_hp_damage(trap_damage)
            return {
                "success": True,
                "message": f"⚠️ 함정에 걸렸습니다!\n{damaged_member.name}이(가) {actual_damage} 데미지를 받았습니다!",
                "damage": actual_damage
            }
        
        return {
            "success": True,
            "message": "⚠️ 함정이 있었지만 다행히 피했습니다!"
        }
    
    def _mysterious_statue(self, party: List, floor: int) -> Dict[str, Any]:
        """신비한 석상"""
        statue_effects = [
            ("지혜의 석상", "파티 전체의 경험치가 조금 증가합니다.", "exp_bonus"),
            ("힘의 석상", "파티 전체의 공격력이 일시적으로 증가합니다.", "attack_boost"),
            ("행운의 석상", "앞으로 더 좋은 보물을 찾을 확률이 증가합니다.", "luck_boost"),
            ("저주의 석상", "무언가 불길한 기운이 감돕니다...", "minor_curse")
        ]
        
        effect = random.choice(statue_effects)
        return {
            "success": True,
            "message": f"🗿 {effect[0]}을 발견했습니다.\n{effect[1]}",
            "effect": effect[2]
        }
    
    def _wandering_spirit(self, party: List, floor: int) -> Dict[str, Any]:
        """떠도는 영혼"""
        spirit_outcomes = [
            ("친근한 영혼", "영혼이 유용한 정보를 알려줍니다.", "map_reveal"),
            ("슬픈 영혼", "영혼을 달래주어 축복을 받았습니다.", "blessing"),
            ("화난 영혼", "영혼이 화내며 사라졌습니다.", "minor_debuff"),
            ("지혜로운 영혼", "고대의 지혜를 전수받았습니다.", "skill_boost")
        ]
        
        outcome = random.choice(spirit_outcomes)
        return {
            "success": True,
            "message": f"👻 떠도는 영혼을 만났습니다.\n{outcome[1]}",
            "effect": outcome[2]
        }
    
    def _ancient_runes(self, party: List, floor: int) -> Dict[str, Any]:
        """고대 룬 문자"""
        if random.random() < 0.5:
            # 성공적으로 해독
            return {
                "success": True,
                "message": "📜 고대 룬 문자를 해독했습니다!\n고대의 지식을 얻어 마법력이 일시적으로 상승합니다.",
                "effect": "magic_boost"
            }
        else:
            # 해독 실패
            return {
                "success": True,
                "message": "📜 고대 룬 문자를 발견했지만 해독하지 못했습니다.\n다음에 더 주의깊게 살펴보세요."
            }
    
    def _crystal_formation(self, party: List, floor: int) -> Dict[str, Any]:
        """수정 형태"""
        crystal_types = ["마나 수정", "체력 수정", "행운 수정", "시간 수정"]
        crystal = random.choice(crystal_types)
        
        effects = {
            "마나 수정": ("파티 전체의 MP가 회복됩니다.", "mp_restore"),
            "체력 수정": ("파티 전체의 HP가 회복됩니다.", "hp_restore"),
            "행운 수정": ("행운이 일시적으로 상승합니다.", "luck_up"),
            "시간 수정": ("시간의 흐름이 느려져 다음 전투에서 유리합니다.", "time_slow")
        }
        
        effect = effects[crystal]
        return {
            "success": True,
            "message": f"💎 {crystal} 형태를 발견했습니다!\n{effect[0]}",
            "effect": effect[1]
        }
    
    def _abandoned_camp(self, party: List, floor: int) -> Dict[str, Any]:
        """버려진 야영지"""
        findings = [
            ("버려진 배낭", "유용한 소모품들을 발견했습니다.", "consumables"),
            ("오래된 지도", "이 층의 지형이 일부 밝혀졌습니다.", "map_info"),
            ("야영지 잔해", "특별한 것을 찾지 못했습니다.", "nothing"),
            ("모험가의 일기", "선배 모험가의 조언을 얻었습니다.", "advice")
        ]
        
        finding = random.choice(findings)
        return {
            "success": True,
            "message": f"🏕️ 버려진 야영지를 발견했습니다.\n{finding[0]}: {finding[1]}",
            "effect": finding[2] if finding[2] != "nothing" else None
        }
    
    def _monster_lair(self, party: List, floor: int) -> Dict[str, Any]:
        """몬스터 소굴 - 4마리의 강력한 적"""
        return {
            "success": True,
            "message": "🕳️ 몬스터 소굴을 발견했습니다!\n4마리의 강력한 적이 나타날 것이지만, 좋은 보상도 기대할 수 있습니다.",
            "effect": "elite_encounter_4"
        }
    
    def _magical_portal(self, party: List, floor: int) -> Dict[str, Any]:
        """마법 포털"""
        portal_destinations = [
            "상층으로 이어지는 포털",
            "하층으로 이어지는 포털", 
            "보물방으로 이어지는 포털",
            "위험한 곳으로 이어지는 포털"
        ]
        
        destination = random.choice(portal_destinations)
        return {
            "success": True,
            "message": f"🌀 마법 포털을 발견했습니다!\n{destination}인 것 같습니다. 들어가시겠습니까?",
            "effect": "portal_choice"
        }
    
    # 나머지 조우들도 비슷하게 구현...
    def _wise_hermit(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "🧙 현명한 은둔자를 만났습니다.\n\"젊은 모험가들이여, 조언을 들어보겠는가?\"",
            "effect": "hermit_advice"
        }
    
    def _cursed_altar(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "⚡ 저주받은 제단을 발견했습니다.\n어두운 기운이 감돕니다. 위험하지만 강력한 힘을 얻을 수도...",
            "effect": "cursed_choice"
        }
    
    def _lucky_fountain(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "⛲ 행운의 분수를 발견했습니다!\n동전을 던지면 소원이 이루어질지도 모릅니다.",
            "effect": "lucky_wish"
        }
    
    def _training_dummy(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "🎯 훈련용 더미를 발견했습니다.\n연습을 통해 실력을 향상시킬 수 있습니다.",
            "effect": "training_option"
        }
    
    def _elemental_node(self, party: List, floor: int) -> Dict[str, Any]:
        elements = ["화염", "빙결", "번개", "대지", "바람", "물", "빛", "어둠", "독"]
        element = random.choice(elements)
        # 강화량 계산 (층수에 따라 증가, 15~30%)
        boost_value = min(15 + floor // 5, 30)
        return {
            "success": True,
            "message": f"🔮 {element} 원소 노드를 발견했습니다!\n{element} 속성 공격력이 일시적으로 상승합니다.",
            "effect": f"element_boost_{element}",
            "effect_value": boost_value
        }
    
    def _time_rift(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "⏰ 시간 균열을 발견했습니다.\n시간의 흐름이 불안정합니다. 기회일 수도, 위험일 수도...",
            "effect": "time_anomaly"
        }
    
    def _shadow_passage(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "🌑 그림자 통로를 발견했습니다.\n어둠 속을 통과하면 빠르게 이동할 수 있지만...",
            "effect": "shadow_travel"
        }
    
    def _blessed_shrine(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "⛪ 축복받은 신전을 발견했습니다.\n신성한 힘이 파티를 감싸줍니다.",
            "effect": "divine_blessing"
        }
    
    def _merchant_caravan(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "🚛 상인 마차를 발견했습니다!\n더 다양하고 좋은 상품들을 구경할 수 있습니다.",
            "effect": "premium_shop"
        }
    
    def _ancient_library(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "📚 고대 도서관을 발견했습니다.\n고대의 지식이 담긴 책들이 가득합니다.",
            "effect": "knowledge_gain"
        }
    
    def _weapon_rack(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "⚔️ 무기 거치대를 발견했습니다.\n좋은 무기를 하나 가져갈 수 있을 것 같습니다.",
            "effect": "weapon_choice"
        }
    
    def _spell_circle(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "🔯 마법진을 발견했습니다.\n강력한 마법을 배울 기회입니다.",
            "effect": "spell_learning"
        }
    
    def _monster_ambush(self, party: List, floor: int) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "💀 몬스터 매복에 당했습니다!\n불리한 상황에서 전투가 시작됩니다!",
            "effect": "ambush_battle"
        }

class FieldSkillManager:
    """필드 스킬 관리자"""
    
    def __init__(self):
        self.field_skills = self._initialize_field_skills()
    
    def _initialize_field_skills(self) -> Dict[str, FieldSkill]:
        """8가지 필드 스킬 초기화"""
        skills = {}
        
        # 1. 보물 탐지 (도적, 레인저 계열)
        skills["보물 탐지"] = FieldSkill(
            "보물 탐지", FieldSkillType.DETECT_TREASURE, 15, 5,
            "주변의 숨겨진 보물을 탐지합니다.",
            ["도적", "레인저", "닌자", "암살자"]
        )
        
        # 2. 파티 치유 (치료사, 성직자 계열)
        skills["야외 치료"] = FieldSkill(
            "야외 치료", FieldSkillType.HEAL_PARTY, 20, 6,
            "야외에서 파티원들을 치료합니다.",
            ["치료사", "성직자", "드루이드", "성기사"]
        )
        
        # 3. 순간이동 (마법사 계열)
        skills["마법 이동"] = FieldSkill(
            "마법 이동", FieldSkillType.TELEPORT, 25, 8,
            "마법으로 안전한 곳으로 순간이동합니다.",
            ["마법사", "술사", "흑마법사", "신비술사"]
        )
        
        # 4. 자물쇠 해제 (도적, 기술자 계열)
        skills["자물쇠 해제"] = FieldSkill(
            "자물쇠 해제", FieldSkillType.UNLOCK, 10, 3,
            "복잡한 자물쇠나 봉인을 해제합니다.",
            ["도적", "닌자", "기술자", "연금술사"]
        )
        
        # 5. 정화 (성직자, 드루이드 계열)
        skills["환경 정화"] = FieldSkill(
            "환경 정화", FieldSkillType.PURIFY, 18, 4,
            "주변 환경과 파티의 독성을 정화합니다.",
            ["성직자", "드루이드", "치료사", "주술사"]
        )
        
        # 6. 은신 (암살자, 닌자 계열)
        skills["집단 은신"] = FieldSkill(
            "집단 은신", FieldSkillType.STEALTH, 22, 7,
            "파티 전체를 은신시켜 적을 피합니다.",
            ["닌자", "암살자", "레인저"]
        )
        
        # 7. 분석 (학자, 연금술사 계열)
        skills["던전 분석"] = FieldSkill(
            "던전 분석", FieldSkillType.ANALYZE, 12, 2,
            "던전의 위험도와 보물 정보를 분석합니다.",
            ["연금술사", "기술자", "신비술사"]
        )
        
        # 8. 파티 축복 (성직자, 음유시인 계열)
        skills["집단 축복"] = FieldSkill(
            "집단 축복", FieldSkillType.BLESS_PARTY, 30, 10,
            "파티 전체에 강력한 축복을 내립니다.",
            ["성직자", "음유시인", "성기사"]
        )
        
        return skills
    
    def get_usable_skills(self, character) -> List[FieldSkill]:
        """캐릭터가 사용할 수 있는 필드 스킬들"""
        usable = []
        character_job = character.character_class.value if hasattr(character, 'job') else "전사"
        
        for skill in self.field_skills.values():
            if character_job in skill.required_job:
                usable.append(skill)
        
        return usable
    
    def reduce_all_cooldowns(self):
        """모든 필드 스킬 쿨다운 감소"""
        for skill in self.field_skills.values():
            skill.reduce_cooldown()

class RandomEncounterManager:
    """랜덤 조우 관리자"""
    
    def __init__(self):
        self.encounters = self._initialize_encounters()
        self.field_skill_manager = FieldSkillManager()
        # 층당 조우 횟수 제한 시스템
        self.floor_encounter_counts = {}  # {floor: encounter_count}
        self.max_encounters_per_floor = 6  # 층당 최대 조우 횟수
        self.min_encounters_per_floor = 5  # 층당 최소 보장 조우 횟수
    
    def _initialize_encounters(self) -> List[RandomEncounter]:
        """강화된 랜덤 조우 초기화 - 39가지 다양한 조우"""
        encounters = []
        
        # 모든 조우 타입에 대해 강화된 인스턴스 생성
        for encounter_type in EncounterType:
            # 층별 제한 설정 (특정 조우들은 높은 층에서만)
            if encounter_type in [EncounterType.TIME_RIFT, EncounterType.MAGICAL_PORTAL, EncounterType.DIMENSIONAL_TEAR]:
                encounter = RandomEncounter(encounter_type, 10, 30)
            elif encounter_type in [EncounterType.ANCIENT_LIBRARY, EncounterType.SPELL_CIRCLE, EncounterType.MAGICAL_LABORATORY]:
                encounter = RandomEncounter(encounter_type, 15, 30)
            elif encounter_type in [EncounterType.MONSTER_AMBUSH, EncounterType.DRAGON_NEST, EncounterType.TREASURE_GUARDIAN]:
                encounter = RandomEncounter(encounter_type, 5, 30)
            elif encounter_type in [EncounterType.PHANTOM_SHIP, EncounterType.ANCIENT_GOLEM, EncounterType.FORGOTTEN_TOMB]:
                encounter = RandomEncounter(encounter_type, 8, 30)
            elif encounter_type in [EncounterType.CELESTIAL_ALTAR, EncounterType.SOUL_WELL, EncounterType.HAUNTED_FORGE]:
                encounter = RandomEncounter(encounter_type, 12, 30)
            else:
                encounter = RandomEncounter(encounter_type, 1, 30)
            
            encounters.append(encounter)
        
        # print(f"✨ 강화된 인카운트 시스템 초기화 완료: {len(encounters)}가지 조우 타입")  # 숨김
        return encounters
    
    def get_floor_encounter_count(self, floor: int) -> int:
        """특정 층의 조우 횟수 반환"""
        return self.floor_encounter_counts.get(floor, 0)
    
    def increment_floor_encounter_count(self, floor: int) -> None:
        """특정 층의 조우 횟수 증가"""
        if floor not in self.floor_encounter_counts:
            self.floor_encounter_counts[floor] = 0
        self.floor_encounter_counts[floor] += 1
    
    def can_encounter_on_floor(self, floor: int) -> bool:
        """해당 층에서 더 조우가 가능한지 체크"""
        current_count = self.get_floor_encounter_count(floor)
        return current_count < self.max_encounters_per_floor
    
    def should_force_encounter(self, floor: int, steps_taken: int) -> bool:
        """강제 조우 발생 여부 (최소 조우 보장 + 최대 걸음수 시스템)"""
        current_count = self.get_floor_encounter_count(floor)
        
        # === 최대 걸음수 도달 시 강제 인카운트 (100% 발생) ===
        max_steps_without_encounter = 120  # 최대 120걸음
        if steps_taken >= max_steps_without_encounter:
            print(f"🚨 최대 걸음수 {max_steps_without_encounter} 도달! 강제 인카운트 발생!")
            return True
        
        # === 기존 최소 조우 보장 시스템 ===
        # 최소 조우 횟수 미달이고 충분히 많이 걸었을 때 강제 발생
        if current_count < self.min_encounters_per_floor and steps_taken > 50:
            return True
        
        # 계단 근처에서 최소 조우 미달시 강제 발생
        if current_count < self.min_encounters_per_floor and steps_taken > 80:
            return True
        
        return False
    
    def check_encounter(self, party: List, current_floor: int, steps_taken: int = 0) -> Optional[Dict[str, Any]]:
        """확률 기반 인카운터 체크 (층당 조우 횟수 제한 적용)"""
        # 해당 층에서 더 이상 조우가 불가능한 경우
        if not self.can_encounter_on_floor(current_floor):
            return None
        
        # 강제 조우 체크 (최소 조우 보장)
        if self.should_force_encounter(current_floor, steps_taken):
            print(f"🎯 층 {current_floor}에서 최소 조우 보장을 위한 강제 조우 발생!")
            encounter_result = self.trigger_random_encounter(party, current_floor)
            if encounter_result:
                self.increment_floor_encounter_count(current_floor)
                # 인카운트 통계 출력
                self._show_encounter_stats(current_floor)
            return encounter_result
        
        # 일반적인 확률 기반 조우
        encounter_chance = self.get_encounter_chance(current_floor, steps_taken)
        
        if random.random() < encounter_chance:
            encounter_result = self.trigger_random_encounter(party, current_floor)
            if encounter_result:
                self.increment_floor_encounter_count(current_floor)
                # 인카운트 통계 출력
                self._show_encounter_stats(current_floor)
            return encounter_result
        
        return None
    
    def _show_encounter_stats(self, floor: int):
        """인카운트 통계 표시"""
        current_count = self.get_floor_encounter_count(floor)
        print(f"📊 층 {floor} 조우 현황: {current_count}/{self.max_encounters_per_floor} (최소 {self.min_encounters_per_floor}개 보장)")
        
        # 전체 인카운트 통계도 표시
        total_encounters = sum(self.floor_encounter_counts.values())
        floors_explored = len(self.floor_encounter_counts)
        if floors_explored > 0:
            avg_encounters = total_encounters / floors_explored
            print(f"📈 총 인카운트: {total_encounters}회 | 탐험 층수: {floors_explored}층 | 평균: {avg_encounters:.1f}회/층")
    
    def trigger_random_encounter(self, party: List, current_floor: int) -> Optional[Dict[str, Any]]:
        """강화된 랜덤 조우 발생 - 커서 메뉴 지원"""
        # 현재 층에서 가능한 조우들 필터링
        available_encounters = [
            encounter for encounter in self.encounters
            if encounter.min_floor <= current_floor <= encounter.max_floor
        ]
        
        if not available_encounters:
            return None
        
        # 랜덤하게 조우 선택
        selected_encounter = random.choice(available_encounters)
        
        # 특별한 인카운트들은 커서 메뉴 사용
        special_encounters = [
            "신비한 정원", "드래곤 둥지", "마법 거울", "잊혀진 무덤", 
            "원소 폭풍", "천체 제단", "유령선", "수정 동굴", 
            "고대 골렘", "마법 실험실", "영혼의 우물", "보물 수호자",
            "차원 균열", "요정의 고리", "유령 대장간"
        ]
        
        encounter_result = selected_encounter.trigger(party, current_floor)
        
        # 특별한 인카운트는 선택지 제공
        if (encounter_result and encounter_result.get("success") and 
            selected_encounter.encounter_type.value in special_encounters):
            encounter_result = self._handle_special_encounter_choice(encounter_result, party, current_floor)
        
        return encounter_result
    
    def _handle_special_encounter_choice(self, encounter_result: Dict[str, Any], party: List, floor: int) -> Dict[str, Any]:
        """특별한 인카운트에 대한 선택지 제공"""
        try:
            from .cursor_menu_system import create_simple_menu
            
            # 인카운트 정보 표시
            encounter_type = encounter_result.get("type", "신비한 조우")
            message = encounter_result.get("message", "특별한 일이 일어났습니다.")
            
            print(f"\n✨ 특별한 조우: {encounter_type}")
            print(f"📖 {message}")
            
            # 선택지 구성
            choices = ["🎯 도전하기", "🚶 조용히 지나가기", "🔍 자세히 관찰하기"]
            descriptions = [
                "위험을 감수하고 조우에 도전합니다.",
                "위험을 피해 조용히 지나갑니다.",
                "안전한 거리에서 상황을 관찰합니다."
            ]
            
            choice = create_simple_menu(
                title=f"🌟 {encounter_type} - 어떻게 하시겠습니까?",
                options=choices,
                descriptions=descriptions
            )
            
            if choice == 0:  # 도전하기
                print("🎯 위험을 감수하고 도전합니다!")
                return encounter_result  # 원래 결과 그대로
            elif choice == 1:  # 지나가기
                print("🚶 조용히 지나가며 안전을 택했습니다.")
                return {
                    "success": True,
                    "message": f"조용히 {encounter_type}을(를) 지나쳤습니다. 안전하지만 기회를 놓쳤습니다.",
                    "effects": {"exp": floor * 10}  # 작은 경험치 보상
                }
            elif choice == 2:  # 관찰하기
                print("🔍 안전한 거리에서 관찰합니다.")
                return {
                    "success": True,
                    "message": f"{encounter_type}을(를) 관찰하며 지혜를 얻었습니다.",
                    "effects": {"exp": floor * 25, "wisdom_boost": 5}  # 중간 보상
                }
            else:
                return encounter_result  # 기본값
                
        except ImportError:
            # 커서 메뉴 시스템이 없으면 기본 처리
            return encounter_result
    
    def get_encounter_chance(self, floor: int, steps_taken: int) -> float:
        """층과 이동 거리에 따른 조우 확률 (매우 낮은 빈도로 조정)"""
        base_chance = 0.003  # 기본 0.3% (0.8% → 0.3%로 더욱 낮춤)
        floor_modifier = min(floor * 0.0005, 0.003)  # 층당 0.05% 증가, 최대 0.3%
        step_modifier = min(steps_taken * 0.0002, 0.004)  # 걸음당 0.02% 증가, 최대 0.4%
        
        return min(base_chance + floor_modifier + step_modifier, 0.01)  # 최대 1% (2.5% → 1%로 낮춤)
    
    def get_floor_encounter_status(self, floor: int) -> str:
        """특정 층의 조우 상태 문자열 반환"""
        current_count = self.get_floor_encounter_count(floor)
        return f"층 {floor} 조우: {current_count}/{self.max_encounters_per_floor} (최소 {self.min_encounters_per_floor}개 보장)"
    
    def reset_floor_encounter_data(self, floor: int) -> None:
        """특정 층의 조우 데이터 리셋 (디버깅용)"""
        if floor in self.floor_encounter_counts:
            del self.floor_encounter_counts[floor]
            print(f"✅ 층 {floor}의 조우 데이터가 리셋되었습니다.")

# 새로운 인카운트 핸들러들을 기존 RandomEncounter 클래스에 추가
def add_enhanced_encounter_methods():
    """새로운 인카운트 메서드들을 RandomEncounter 클래스에 동적으로 추가"""
    
    def _mystical_garden(self, party: List, floor: int) -> Dict[str, Any]:
        """신비한 정원 - 특별한 열매나 허브 발견"""
        garden_outcomes = [
            ("치유의 열매", "파티 전체가 완전히 회복되고 상처도 치료됩니다.", "full_heal_wounds"),
            ("마력의 열매", "파티 전체의 MP가 완전히 회복됩니다.", "full_mp_restore"),
            ("활력의 허브", "파티 전체의 최대 HP가 일시적으로 증가합니다.", "temp_hp_boost"),
            ("독성 식물", "정원의 독성 식물에 의해 파티가 피해를 입습니다.", "poison_damage"),
            ("시간의 꽃", "신비한 꽃의 향기로 시간이 느려집니다.", "time_slow")
        ]
        
        outcome = random.choice(garden_outcomes)
        effects = {}
        
        if outcome[2] == "full_heal_wounds":
            for member in party:
                if hasattr(member, 'hp') and hasattr(member, 'max_hp'):
                    member.hp = member.max_hp
                if hasattr(member, 'wounds'):
                    member.wounds = 0
            effects["healing"] = "complete"
        elif outcome[2] == "temp_hp_boost":
            effects["temp_hp_boost"] = floor * 20
        elif outcome[2] == "poison_damage":
            effects["poison_damage"] = floor * 15
            
        return {
            "success": True,
            "message": f"🌺 신비한 정원을 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
    def _dragon_nest(self, party: List, floor: int) -> Dict[str, Any]:
        """드래곤 둥지 - 위험하지만 큰 보상"""
        nest_outcomes = [
            ("빈 둥지", "드래곤은 없지만 황금알 파편들이 있습니다.", "gold_bonus"),
            ("잠자는 드래곤", "조용히 빠져나가며 보물을 훔칩니다.", "stealth_treasure"),
            ("분노한 드래곤", "드래곤과 마주쳤습니다! 전투가 시작됩니다!", "dragon_battle"),
            ("친근한 새끼 드래곤", "새끼 드래곤이 불꽃 마법을 가르쳐줍니다.", "fire_magic_boost"),
            ("고대 드래곤의 축복", "고대 드래곤의 영혼이 축복을 내립니다.", "dragon_blessing")
        ]
        
        outcome = random.choice(nest_outcomes)
        effects = {}
        
        if outcome[2] == "gold_bonus":
            effects["gold"] = floor * 200
        elif outcome[2] == "stealth_treasure":
            effects["gold"] = floor * 150
            effects["exp"] = floor * 30
        elif outcome[2] == "dragon_battle":
            effects["battle"] = "elite_dragon"
        elif outcome[2] == "fire_magic_boost":
            effects["fire_resistance"] = 25
        elif outcome[2] == "dragon_blessing":
            effects["all_stats_boost"] = 10
            
        return {
            "success": True,
            "message": f"🐉 드래곤 둥지를 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
    def _enchanted_mirror(self, party: List, floor: int) -> Dict[str, Any]:
        """마법 거울 - 복사나 환영 효과"""
        mirror_outcomes = [
            ("진실의 거울", "거울이 숨겨진 길을 보여줍니다.", "reveal_secret"),
            ("복사의 거울", "거울이 골드를 복사해줍니다.", "duplicate_gold"),
            ("환영의 거울", "거울 속 환영이 혼란을 일으킵니다.", "confusion_trap"),
            ("시간의 거울", "과거의 모습을 보며 경험치를 얻습니다.", "exp_bonus"),
            ("차원의 거울", "다른 차원으로 짧게 이동할 수 있습니다.", "dimension_hop")
        ]
        
        outcome = random.choice(mirror_outcomes)
        effects = {}
        
        if outcome[2] == "duplicate_gold":
            current_gold = getattr(party[0], 'gold', 0) if party else 0
            effects["gold"] = min(current_gold, floor * 100)  # 최대 복사량 제한
        elif outcome[2] == "exp_bonus":
            effects["exp"] = floor * 50
        elif outcome[2] == "confusion_trap":
            effects["confusion"] = 3  # 3턴 혼란
            
        return {
            "success": True,
            "message": f"🪞 마법 거울을 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
    # 나머지 새로운 인카운트 메서드들도 비슷하게 추가...
    # (간단히 몇 개만 더 추가)
    
    def _fairy_ring(self, party: List, floor: int) -> Dict[str, Any]:
        """요정의 고리 - 요정들의 마법"""
        fairy_magic = [
            ("치유의 요정", "요정들이 파티를 치유해줍니다.", "fairy_healing"),
            ("장난꾸러기 요정", "요정들이 장난을 칩니다.", "fairy_prank"),
            ("축복의 요정", "요정들이 행운을 빌어줍니다.", "fairy_blessing"),
            ("마법의 요정", "요정들이 마법을 가르쳐줍니다.", "fairy_magic"),
            ("수호의 요정", "요정들이 보호막을 쳐줍니다.", "fairy_protection")
        ]
        
        magic = random.choice(fairy_magic)
        effects = {}
        
        if magic[2] == "fairy_healing":
            effects["healing"] = "full"
            effects["status_cure"] = True
        elif magic[2] == "fairy_blessing":
            effects["luck_boost"] = 30
            effects["critical_rate_boost"] = 15
        elif magic[2] == "fairy_magic":
            effects["magic_attack_boost"] = 25
            effects["mp_efficiency"] = 20
            
        return {
            "success": True,
            "message": f"🧚 요정의 고리를 발견했습니다!\n{magic[0]}: {magic[1]}",
            "effects": effects
        }
    
    # 메서드들을 RandomEncounter 클래스에 동적으로 추가
    RandomEncounter._mystical_garden = _mystical_garden
    RandomEncounter._dragon_nest = _dragon_nest
    RandomEncounter._enchanted_mirror = _enchanted_mirror
    RandomEncounter._fairy_ring = _fairy_ring
    
    # 나머지 메서드들도 기본 구현으로 추가 (간단한 효과들)
    def _create_simple_encounter(name, emoji, effect_type, base_value):
        def encounter_method(self, party: List, floor: int) -> Dict[str, Any]:
            effects = {effect_type: floor * base_value}
            return {
                "success": True,
                "message": f"{emoji} {name}을(를) 발견했습니다!\n특별한 일이 일어났습니다.",
                "effects": effects
            }
        return encounter_method
    
    # 나머지 새로운 인카운트들을 간단한 형태로 추가
    new_encounters = [
        ("forgotten_tomb", "잊혀진 무덤", "⚰️", "gold", 300),
        ("elemental_storm", "원소 폭풍", "⛈️", "exp", 80),
        ("celestial_altar", "천체 제단", "✨", "all_stats_boost", 5),
        ("phantom_ship", "유령선", "🚢", "gold", 400),
        ("crystal_cave", "수정 동굴", "💎", "mp_restore", 50),
        ("ancient_golem", "고대 골렘", "🗿", "exp", 120),
        ("magical_laboratory", "마법 실험실", "🧪", "potion_reward", 3),
        ("soul_well", "영혼의 우물", "🌀", "magic_boost", 20),
        ("treasure_guardian", "보물 수호자", "⚔️", "legendary_reward", 1),
        ("dimensional_tear", "차원 균열", "🌀", "random_effect", 1),
        ("haunted_forge", "유령 대장간", "🔨", "equipment_enhance", 1)
    ]
    
    for method_name, name, emoji, effect_type, base_value in new_encounters:
        setattr(RandomEncounter, f"_{method_name}", _create_simple_encounter(name, emoji, effect_type, base_value))

# 시스템 초기화시 메서드 추가
add_enhanced_encounter_methods()

# EnhancedRandomEncounter 클래스 제거 (더 이상 필요없음)
    
def _mystical_garden(self, party: List, floor: int) -> Dict[str, Any]:
        """신비한 정원 - 특별한 열매나 허브 발견"""
        garden_outcomes = [
            ("치유의 열매", "파티 전체가 완전히 회복되고 상처도 치료됩니다.", "full_heal_wounds"),
            ("마력의 열매", "파티 전체의 MP가 완전히 회복됩니다.", "full_mp_restore"),
            ("활력의 허브", "파티 전체의 최대 HP가 일시적으로 증가합니다.", "temp_hp_boost"),
            ("독성 식물", "정원의 독성 식물에 의해 파티가 피해를 입습니다.", "poison_damage"),
            ("시간의 꽃", "신비한 꽃의 향기로 시간이 느려집니다.", "time_slow")
        ]
        
        outcome = random.choice(garden_outcomes)
        effects = {}
        
        if outcome[2] == "full_heal_wounds":
            for member in party:
                if hasattr(member, 'hp') and hasattr(member, 'max_hp'):
                    member.hp = member.max_hp
                if hasattr(member, 'wounds'):
                    member.wounds = 0
            effects["healing"] = "complete"
        elif outcome[2] == "temp_hp_boost":
            effects["temp_hp_boost"] = floor * 20
        elif outcome[2] == "poison_damage":
            effects["poison_damage"] = floor * 15
            
        return {
            "success": True,
            "message": f"🌺 신비한 정원을 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
def _dragon_nest(self, party: List, floor: int) -> Dict[str, Any]:
        """드래곤 둥지 - 위험하지만 큰 보상"""
        nest_outcomes = [
            ("빈 둥지", "드래곤은 없지만 황금알 파편들이 있습니다.", "gold_bonus"),
            ("잠자는 드래곤", "조용히 빠져나가며 보물을 훔칩니다.", "stealth_treasure"),
            ("분노한 드래곤", "드래곤과 마주쳤습니다! 전투가 시작됩니다!", "dragon_battle"),
            ("친근한 새끼 드래곤", "새끼 드래곤이 불꽃 마법을 가르쳐줍니다.", "fire_magic_boost"),
            ("고대 드래곤의 축복", "고대 드래곤의 영혼이 축복을 내립니다.", "dragon_blessing")
        ]
        
        outcome = random.choice(nest_outcomes)
        effects = {}
        
        if outcome[2] == "gold_bonus":
            effects["gold"] = floor * 200
        elif outcome[2] == "stealth_treasure":
            effects["gold"] = floor * 150
            effects["exp"] = floor * 30
        elif outcome[2] == "dragon_battle":
            effects["battle"] = "elite_dragon"
        elif outcome[2] == "fire_magic_boost":
            effects["fire_resistance"] = 25
        elif outcome[2] == "dragon_blessing":
            effects["all_stats_boost"] = 10
            
        return {
            "success": True,
            "message": f"🐉 드래곤 둥지를 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
def _enchanted_mirror(self, party: List, floor: int) -> Dict[str, Any]:
        """마법 거울 - 복사나 환영 효과"""
        mirror_outcomes = [
            ("진실의 거울", "거울이 숨겨진 길을 보여줍니다.", "reveal_secret"),
            ("복사의 거울", "거울이 골드를 복사해줍니다.", "duplicate_gold"),
            ("환영의 거울", "거울 속 환영이 혼란을 일으킵니다.", "confusion_trap"),
            ("시간의 거울", "과거의 모습을 보며 경험치를 얻습니다.", "exp_bonus"),
            ("차원의 거울", "다른 차원으로 짧게 이동할 수 있습니다.", "dimension_hop")
        ]
        
        outcome = random.choice(mirror_outcomes)
        effects = {}
        
        if outcome[2] == "duplicate_gold":
            current_gold = getattr(party[0], 'gold', 0) if party else 0
            effects["gold"] = min(current_gold, floor * 100)  # 최대 복사량 제한
        elif outcome[2] == "exp_bonus":
            effects["exp"] = floor * 50
        elif outcome[2] == "confusion_trap":
            effects["confusion"] = 3  # 3턴 혼란
            
        return {
            "success": True,
            "message": f"🪞 마법 거울을 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
def _forgotten_tomb(self, party: List, floor: int) -> Dict[str, Any]:
        """잊혀진 무덤 - 언데드나 고대 보물"""
        tomb_outcomes = [
            ("평온한 무덤", "고인의 평화로운 무덤에서 축복을 받습니다.", "peaceful_blessing"),
            ("보물 무덤", "부장품으로 값진 보물들이 있습니다.", "ancient_treasure"),
            ("저주받은 무덤", "무덤의 저주가 파티를 감쌉니다.", "tomb_curse"),
            ("언데드 무덤", "언데드들이 깨어났습니다!", "undead_battle"),
            ("현자의 무덤", "고대 현자의 지혜가 깃들어 있습니다.", "wisdom_boost")
        ]
        
        outcome = random.choice(tomb_outcomes)
        effects = {}
        
        if outcome[2] == "ancient_treasure":
            effects["gold"] = floor * 300
            effects["rare_item"] = True
        elif outcome[2] == "tomb_curse":
            effects["curse"] = "reduced_stats"
        elif outcome[2] == "undead_battle":
            effects["battle"] = "undead_horde"
        elif outcome[2] == "wisdom_boost":
            effects["exp"] = floor * 100
            effects["skill_point"] = 1
            
        return {
            "success": True,
            "message": f"⚰️ 잊혀진 무덤을 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
def _elemental_storm(self, party: List, floor: int) -> Dict[str, Any]:
        """원소 폭풍 - 원소 마법 관련 효과"""
        storm_types = [
            ("화염 폭풍", "뜨거운 화염이 휘몰아칩니다.", "fire_storm"),
            ("빙결 폭풍", "차가운 얼음이 모든 것을 얼립니다.", "ice_storm"), 
            ("번개 폭풍", "번개가 하늘을 가릅니다.", "lightning_storm"),
            ("바람 폭풍", "강한 바람이 모든 것을 휩쓸어갑니다.", "wind_storm"),
            ("마법 폭풍", "순수한 마법 에너지가 소용돌이칩니다.", "magic_storm")
        ]
        
        storm = random.choice(storm_types)
        effects = {}
        damage = floor * 25
        
        if storm[2] == "fire_storm":
            effects["fire_damage"] = damage
            effects["fire_resistance"] = 15  # 저항도 얻음
        elif storm[2] == "ice_storm":
            effects["ice_damage"] = damage
            effects["speed_reduction"] = 2
        elif storm[2] == "lightning_storm":
            effects["lightning_damage"] = damage
            effects["paralysis"] = 1
        elif storm[2] == "magic_storm":
            effects["magic_damage"] = damage // 2  # 낮은 피해
            effects["mp_restore"] = floor * 10  # 하지만 MP 회복
            
        return {
            "success": True,
            "message": f"⛈️ 원소 폭풍에 휘말렸습니다!\n{storm[0]}: {storm[1]}",
            "effects": effects
        }
    
def _celestial_altar(self, party: List, floor: int) -> Dict[str, Any]:
        """천체 제단 - 별과 달의 축복"""
        celestial_events = [
            ("별의 축복", "별빛이 파티를 축복합니다.", "star_blessing"),
            ("달의 은총", "달빛이 상처를 치유해줍니다.", "moon_healing"),
            ("태양의 힘", "태양의 힘이 공격력을 증가시킵니다.", "sun_power"),
            ("혜성의 기운", "혜성의 기운으로 속도가 증가합니다.", "comet_speed"),
            ("행성의 정렬", "행성의 정렬로 모든 능력이 향상됩니다.", "planetary_boost")
        ]
        
        event = random.choice(celestial_events)
        effects = {}
        
        if event[2] == "star_blessing":
            effects["luck_boost"] = 20
            effects["exp_multiplier"] = 1.5
        elif event[2] == "moon_healing":
            effects["healing"] = "full"
            effects["mp_restore"] = "full"
        elif event[2] == "sun_power":
            effects["attack_boost"] = 25
        elif event[2] == "comet_speed":
            effects["speed_boost"] = 30
        elif event[2] == "planetary_boost":
            effects["all_stats_boost"] = 15
            
        return {
            "success": True,
            "message": f"✨ 천체 제단을 발견했습니다!\n{event[0]}: {event[1]}",
            "effects": effects
        }
    
def _phantom_ship(self, party: List, floor: int) -> Dict[str, Any]:
        """유령선 - 바다 관련 신비한 효과"""
        ship_outcomes = [
            ("보물선", "유령선에 보물이 가득합니다.", "pirate_treasure"),
            ("저주받은 선원", "유령 선원들이 저주를 겁니다.", "sailor_curse"),
            ("항해 일지", "선장의 항해 일지에서 지혜를 얻습니다.", "navigation_wisdom"),
            ("바다의 축복", "바다의 정령이 축복을 내립니다.", "sea_blessing"),
            ("크라켄의 공격", "거대한 바다 괴물이 공격합니다!", "kraken_battle")
        ]
        
        outcome = random.choice(ship_outcomes)
        effects = {}
        
        if outcome[2] == "pirate_treasure":
            effects["gold"] = floor * 400
            effects["rare_equipment"] = True
        elif outcome[2] == "sailor_curse":
            effects["curse"] = "reduced_speed"
        elif outcome[2] == "navigation_wisdom":
            effects["map_reveal"] = True
            effects["exp"] = floor * 75
        elif outcome[2] == "sea_blessing":
            effects["water_resistance"] = 30
            effects["healing"] = "full"
        elif outcome[2] == "kraken_battle":
            effects["battle"] = "sea_monster"
            
        return {
            "success": True,
            "message": f"🚢 유령선을 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
def _crystal_cave(self, party: List, floor: int) -> Dict[str, Any]:
        """수정 동굴 - 마법력과 관련된 효과"""
        crystal_types = [
            ("마나 수정", "순수한 마나 수정이 MP를 회복시킵니다.", "mana_crystal"),
            ("힘의 수정", "힘의 수정이 물리 공격력을 증가시킵니다.", "power_crystal"),
            ("지혜의 수정", "지혜의 수정이 마법 공격력을 증가시킵니다.", "wisdom_crystal"),
            ("공명하는 수정", "수정들이 공명하며 경험치를 줍니다.", "resonance_crystal"),
            ("폭발하는 수정", "불안정한 수정이 폭발합니다!", "unstable_crystal")
        ]
        
        crystal = random.choice(crystal_types)
        effects = {}
        
        if crystal[2] == "mana_crystal":
            effects["mp_restore"] = "full"
            effects["max_mp_boost"] = floor * 5
        elif crystal[2] == "power_crystal":
            effects["physical_attack_boost"] = 20
        elif crystal[2] == "wisdom_crystal":
            effects["magic_attack_boost"] = 20
        elif crystal[2] == "resonance_crystal":
            effects["exp"] = floor * 80
        elif crystal[2] == "unstable_crystal":
            effects["explosion_damage"] = floor * 30
            effects["gold"] = floor * 50  # 폭발해도 수정 파편
            
        return {
            "success": True,
            "message": f"💎 수정 동굴을 발견했습니다!\n{crystal[0]}: {crystal[1]}",
            "effects": effects
        }
    
def _fairy_ring(self, party: List, floor: int) -> Dict[str, Any]:
        """요정의 고리 - 요정들의 마법"""
        fairy_magic = [
            ("치유의 요정", "요정들이 파티를 치유해줍니다.", "fairy_healing"),
            ("장난꾸러기 요정", "요정들이 장난을 칩니다.", "fairy_prank"),
            ("축복의 요정", "요정들이 행운을 빌어줍니다.", "fairy_blessing"),
            ("마법의 요정", "요정들이 마법을 가르쳐줍니다.", "fairy_magic"),
            ("수호의 요정", "요정들이 보호막을 쳐줍니다.", "fairy_protection")
        ]
        
        magic = random.choice(fairy_magic)
        effects = {}
        
        if magic[2] == "fairy_healing":
            effects["healing"] = "full"
            effects["status_cure"] = True
        elif magic[2] == "fairy_prank":
            # 좋을 수도 나쁠 수도 있는 효과
            if random.random() < 0.5:
                effects["gold"] = floor * 100
            else:
                effects["confusion"] = 2
        elif magic[2] == "fairy_blessing":
            effects["luck_boost"] = 30
            effects["critical_rate_boost"] = 15
        elif magic[2] == "fairy_magic":
            effects["magic_attack_boost"] = 25
            effects["mp_efficiency"] = 20  # MP 소모 감소
        elif magic[2] == "fairy_protection":
            effects["magic_defense_boost"] = 30
            effects["status_immunity"] = 5  # 5턴간 상태이상 면역
            
        return {
            "success": True,
            "message": f"🧚 요정의 고리를 발견했습니다!\n{magic[0]}: {magic[1]}",
            "effects": effects
        }
    
def _haunted_forge(self, party: List, floor: int) -> Dict[str, Any]:
        """유령 대장간 - 장비 강화나 저주"""
        forge_outcomes = [
            ("마스터의 혼", "전설적 대장장이의 혼이 장비를 강화해줍니다.", "equipment_enhance"),
            ("저주받은 망치", "저주받은 망치가 장비에 저주를 겁니다.", "equipment_curse"),
            ("고대의 제법", "고대 제법서를 발견하여 제작 기술을 얻습니다.", "crafting_skill"),
            ("불멸의 화로", "불멸의 화로에서 특별한 아이템을 제작할 수 있습니다.", "special_craft"),
            ("복수의 정령", "원한을 품은 정령들이 공격합니다!", "spirit_battle")
        ]
        
        outcome = random.choice(forge_outcomes)
        effects = {}
        
        if outcome[2] == "equipment_enhance":
            effects["equipment_upgrade"] = True
            effects["enhancement_level"] = floor // 5 + 1
        elif outcome[2] == "equipment_curse":
            effects["equipment_curse"] = True
        elif outcome[2] == "crafting_skill":
            effects["crafting_bonus"] = 25
            effects["exp"] = floor * 60
        elif outcome[2] == "special_craft":
            effects["legendary_item"] = True
        elif outcome[2] == "spirit_battle":
            effects["battle"] = "vengeful_spirits"
            
        return {
            "success": True,
            "message": f"🔨 유령 대장간을 발견했습니다!\n{outcome[0]}: {outcome[1]}",
            "effects": effects
        }
    
def _ancient_golem(self, party: List, floor: int) -> Dict[str, Any]:
        """고대 골렘 - 수호자나 도우미"""
        golem_states = [
            ("잠든 골렘", "골렘이 잠들어 있어 조용히 지나갑니다.", "sleeping_golem"),
            ("친근한 골렘", "골렘이 깨어나 길을 안내해줍니다.", "friendly_golem"),
            ("수호자 골렘", "골렘이 침입자로 인식하고 공격합니다!", "guardian_battle"),
            ("현자 골렘", "현자 골렘이 고대 지식을 가르쳐줍니다.", "ancient_knowledge"),
            ("보물 골렘", "골렘의 몸에 보석들이 박혀있습니다.", "treasure_golem")
        ]
        
        state = random.choice(golem_states)
        effects = {}
        
        if state[2] == "sleeping_golem":
            effects["stealth_bonus"] = True
            effects["gold"] = floor * 50  # 조용히 주변 탐색
        elif state[2] == "friendly_golem":
            effects["map_reveal"] = True
            effects["safe_passage"] = 3  # 3턴간 안전
        elif state[2] == "guardian_battle":
            effects["battle"] = "ancient_golem"
        elif state[2] == "ancient_knowledge":
            effects["skill_points"] = 2
            effects["exp"] = floor * 120
        elif state[2] == "treasure_golem":
            effects["gems"] = floor * 5
            effects["rare_materials"] = True
            
        return {
            "success": True,
            "message": f"🗿 고대 골렘을 발견했습니다!\n{state[0]}: {state[1]}",
            "effects": effects
        }
    
def _magical_laboratory(self, party: List, floor: int) -> Dict[str, Any]:
        """마법 실험실 - 포션이나 마법 실험"""
        lab_discoveries = [
            ("치유 포션", "완성된 치유 포션들을 발견했습니다.", "healing_potions"),
            ("마나 포션", "순수한 마나 포션들이 있습니다.", "mana_potions"),
            ("실험 실패작", "실패한 실험으로 폭발이 일어납니다!", "lab_explosion"),
            ("변이 포션", "변이 포션으로 능력이 변화합니다.", "mutation_potion"),
            ("연금술 서적", "연금술의 비밀이 담긴 서적을 발견했습니다.", "alchemy_knowledge")
        ]
        
        discovery = random.choice(lab_discoveries)
        effects = {}
        
        if discovery[2] == "healing_potions":
            effects["healing_items"] = floor // 2 + 1
        elif discovery[2] == "mana_potions":
            effects["mana_items"] = floor // 2 + 1
        elif discovery[2] == "lab_explosion":
            effects["explosion_damage"] = floor * 40
            effects["fire_damage"] = floor * 20
        elif discovery[2] == "mutation_potion":
            # 랜덤 스탯 변화 (좋을 수도 나쁠 수도)
            if random.random() < 0.6:
                effects["random_stat_boost"] = floor * 3
            else:
                effects["random_stat_penalty"] = floor * 2
        elif discovery[2] == "alchemy_knowledge":
            effects["alchemy_skill"] = 30
            effects["potion_efficiency"] = 50
            
        return {
            "success": True,
            "message": f"🧪 마법 실험실을 발견했습니다!\n{discovery[0]}: {discovery[1]}",
            "effects": effects
        }
    
def _soul_well(self, party: List, floor: int) -> Dict[str, Any]:
        """영혼의 우물 - 영혼과 관련된 신비한 효과"""
        soul_phenomena = [
            ("정화의 우물", "우물이 영혼을 정화해줍니다.", "soul_purification"),
            ("기억의 우물", "우물에서 잃어버린 기억을 찾습니다.", "memory_recovery"),
            ("힘의 우물", "영혼의 힘이 능력을 증진시킵니다.", "soul_empowerment"),
            ("어둠의 우물", "어둠에 물든 우물이 저주를 퍼뜨립니다.", "dark_corruption"),
            ("영혼 교감", "우물의 영혼들과 교감하며 지혜를 얻습니다.", "soul_communion")
        ]
        
        phenomenon = random.choice(soul_phenomena)
        effects = {}
        
        if phenomenon[2] == "soul_purification":
            effects["status_cure"] = True
            effects["curse_removal"] = True
            effects["healing"] = "partial"
        elif phenomenon[2] == "memory_recovery":
            effects["exp"] = floor * 100
            effects["skill_recall"] = True  # 잊어버린 스킬 복구
        elif phenomenon[2] == "soul_empowerment":
            effects["soul_power"] = floor * 10
            effects["magic_attack_boost"] = 30
        elif phenomenon[2] == "dark_corruption":
            effects["curse"] = "soul_drain"
            effects["hp_drain"] = floor * 10
        elif phenomenon[2] == "soul_communion":
            effects["wisdom_boost"] = 25
            effects["magic_defense_boost"] = 20
            
        return {
            "success": True,
            "message": f"🌀 영혼의 우물을 발견했습니다!\n{phenomenon[0]}: {phenomenon[1]}",
            "effects": effects
        }
    
def _treasure_guardian(self, party: List, floor: int) -> Dict[str, Any]:
        """보물 수호자 - 강력하지만 큰 보상"""
        guardian_types = [
            ("고고학자 유령", "고대 보물을 지키는 학자의 영혼입니다.", "scholar_ghost"),
            ("수정 정령", "수정을 지키는 아름다운 정령입니다.", "crystal_elemental"),
            ("황금 드래곤", "보물 더미 위의 작은 황금 드래곤입니다.", "golden_dragon"),
            ("마법 골렘", "보물을 지키도록 만들어진 골렘입니다.", "magic_guardian"),
            ("고대 기사", "영원히 보물을 지키는 기사의 혼입니다.", "eternal_knight")
        ]
        
        guardian = random.choice(guardian_types)
        effects = {}
        
        # 모든 수호자는 전투 후 큰 보상 제공
        if guardian[2] == "scholar_ghost":
            effects["battle"] = "scholar_ghost"
            effects["knowledge_reward"] = True
        elif guardian[2] == "crystal_elemental":
            effects["battle"] = "crystal_elemental"
            effects["crystal_reward"] = True
        elif guardian[2] == "golden_dragon":
            effects["battle"] = "golden_dragon"
            effects["gold_reward"] = floor * 500
        elif guardian[2] == "magic_guardian":
            effects["battle"] = "magic_guardian"
            effects["magic_item_reward"] = True
        elif guardian[2] == "eternal_knight":
            effects["battle"] = "eternal_knight"
            effects["legendary_weapon"] = True
            
        return {
            "success": True,
            "message": f"⚔️ 보물 수호자를 발견했습니다!\n{guardian[0]}: {guardian[1]}\n강력하지만 승리하면 큰 보상이 기다립니다!",
            "effects": effects
        }
    
def _dimensional_tear(self, party: List, floor: int) -> Dict[str, Any]:
        """차원 균열 - 다른 차원의 효과"""
        dimensional_effects = [
            ("평화의 차원", "평화로운 차원에서 휴식을 취합니다.", "peaceful_dimension"),
            ("마법의 차원", "마법이 넘치는 차원입니다.", "magic_dimension"),
            ("시간의 차원", "시간이 다르게 흐르는 차원입니다.", "time_dimension"),
            ("혼돈의 차원", "혼돈스러운 차원에 빨려들어갑니다.", "chaos_dimension"),
            ("거울의 차원", "모든 것이 반대인 차원입니다.", "mirror_dimension")
        ]
        
        effect = random.choice(dimensional_effects)
        effects = {}
        
        if effect[2] == "peaceful_dimension":
            effects["full_recovery"] = True
            effects["stress_relief"] = True
        elif effect[2] == "magic_dimension":
            effects["magic_boost"] = 40
            effects["mp_multiplier"] = 2.0
        elif effect[2] == "time_dimension":
            effects["time_bonus"] = True
            effects["extra_turns"] = 2
        elif effect[2] == "chaos_dimension":
            effects["random_effects"] = True
            effects["chaos_damage"] = floor * 20
        elif effect[2] == "mirror_dimension":
            effects["stat_reverse"] = True
            effects["confusion"] = 5
            
        return {
            "success": True,
            "message": f"🌀 차원 균열을 발견했습니다!\n{effect[0]}: {effect[1]}",
            "effects": effects
        }
    
def get_combat_chance(self) -> float:
        """랜덤 인카운터에서 전투가 발생할 확률"""
        return 0.30  # 30% 확률로 전투 발생

# 전역 관리자들
encounter_manager = RandomEncounterManager()
field_skill_manager = FieldSkillManager()

def get_encounter_manager() -> RandomEncounterManager:
    """랜덤 조우 관리자 반환"""
    return encounter_manager

def get_field_skill_manager() -> FieldSkillManager:
    """필드 스킬 관리자 반환"""
    return field_skill_manager
