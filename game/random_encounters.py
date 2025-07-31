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
    """랜덤 조우 타입"""
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
        if hasattr(character, 'job') and character.job.value not in self.required_job:
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
            EncounterType.MONSTER_AMBUSH: self._monster_ambush
        }
        
        handler = encounter_handlers.get(self.encounter_type)
        if handler:
            return handler(party, current_floor)
        
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
        """몬스터 소굴"""
        return {
            "success": True,
            "message": "🕳️ 몬스터 소굴을 발견했습니다!\n강력한 적이 나타날 수 있지만, 좋은 보상도 기대할 수 있습니다.",
            "effect": "elite_encounter"
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
        character_job = character.job.value if hasattr(character, 'job') else "전사"
        
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
    
    def _initialize_encounters(self) -> List[RandomEncounter]:
        """24가지 랜덤 조우 초기화"""
        encounters = []
        
        # 모든 조우 타입에 대해 인스턴스 생성
        for encounter_type in EncounterType:
            # 층별 제한 설정 (특정 조우들은 높은 층에서만)
            if encounter_type in [EncounterType.TIME_RIFT, EncounterType.MAGICAL_PORTAL]:
                encounter = RandomEncounter(encounter_type, 10, 30)
            elif encounter_type in [EncounterType.ANCIENT_LIBRARY, EncounterType.SPELL_CIRCLE]:
                encounter = RandomEncounter(encounter_type, 15, 30)
            elif encounter_type == EncounterType.MONSTER_AMBUSH:
                encounter = RandomEncounter(encounter_type, 5, 30)
            else:
                encounter = RandomEncounter(encounter_type, 1, 30)
            
            encounters.append(encounter)
        
        return encounters
    
    def trigger_random_encounter(self, party: List, current_floor: int) -> Optional[Dict[str, Any]]:
        """랜덤 조우 발생"""
        # 현재 층에서 가능한 조우들 필터링
        available_encounters = [
            encounter for encounter in self.encounters
            if encounter.min_floor <= current_floor <= encounter.max_floor
        ]
        
        if not available_encounters:
            return None
        
        # 랜덤하게 조우 선택
        selected_encounter = random.choice(available_encounters)
        return selected_encounter.trigger(party, current_floor)
    
    def get_encounter_chance(self, floor: int, steps_taken: int) -> float:
        """층과 이동 거리에 따른 조우 확률"""
        base_chance = 0.05  # 기본 5%
        floor_modifier = min(floor * 0.01, 0.10)  # 층당 1% 증가, 최대 10%
        step_modifier = min(steps_taken * 0.02, 0.15)  # 걸음당 2% 증가, 최대 15%
        
        return min(base_chance + floor_modifier + step_modifier, 0.30)  # 최대 30%
    
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
