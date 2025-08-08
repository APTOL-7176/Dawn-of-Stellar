"""
아이템 시스템 (스테이지별 드롭률 포함)
내구도 시스템과 특수 효과 통합
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import random


class ItemType(Enum):
    """아이템 타입"""
    CONSUMABLE = "소모품"
    WEAPON = "무기"
    ARMOR = "방어구"
    ACCESSORY = "장신구"
    MATERIAL = "재료"


class ItemRarity(Enum):
    """아이템 희귀도"""
    COMMON = "일반"
    UNCOMMON = "고급"
    RARE = "희귀"
    EPIC = "영웅"
    LEGENDARY = "전설"


class ElementalAffinity(Enum):
    """원소 친화도"""
    NEUTRAL = "무속성"
    FIRE = "화염"
    ICE = "냉기"
    LIGHTNING = "번개"
    EARTH = "대지"
    WIND = "바람"
    WATER = "물"
    LIGHT = "빛"
    DARK = "어둠"
    POISON = "독"


class ItemEffect:
    """아이템 효과 클래스"""
    def __init__(self, name: str, description: str, effect_type: str, 
                 effect_value: Any, condition: str = "always", boss_immune: bool = False):
        self.name = name
        self.description = description
        self.effect_type = effect_type  # stat_boost, combat_effect, special_ability 등
        self.effect_value = effect_value
        self.condition = condition  # always, combat, low_hp, high_brave 등
        self.boss_immune = boss_immune  # 보스에게 면역인 효과
        
    def can_apply_to_target(self, target) -> bool:
        """대상에게 효과 적용 가능한지 확인 (보스 면역 체크)"""
        if self.boss_immune and hasattr(target, 'is_boss') and target.is_boss:
            return False
        return True


class DropRateManager:
    """스테이지별 드롭률 관리자"""
    
    @staticmethod
    def get_rarity_weights(stage: int) -> Dict[ItemRarity, float]:
        """스테이지별 희귀도 가중치 반환"""
        # 기본 가중치
        base_weights = {
            ItemRarity.COMMON: 60.0,
            ItemRarity.UNCOMMON: 25.0,
            ItemRarity.RARE: 10.0,
            ItemRarity.EPIC: 4.0,
            ItemRarity.LEGENDARY: 1.0
        }
        
        # 스테이지가 올라갈수록 좋은 아이템 확률 증가
        stage_multiplier = min(stage / 10.0, 3.0)  # 최대 3배까지
        
        # 스테이지별 조정
        if stage >= 5:  # 5층부터 고급 아이템 확률 증가
            base_weights[ItemRarity.UNCOMMON] += 10.0 * stage_multiplier
            base_weights[ItemRarity.RARE] += 5.0 * stage_multiplier
            base_weights[ItemRarity.COMMON] -= 10.0 * stage_multiplier
            
        if stage >= 10:  # 10층부터 희귀 아이템 확률 증가
            base_weights[ItemRarity.RARE] += 8.0 * stage_multiplier
            base_weights[ItemRarity.EPIC] += 3.0 * stage_multiplier
            base_weights[ItemRarity.UNCOMMON] -= 5.0 * stage_multiplier
            base_weights[ItemRarity.COMMON] -= 5.0 * stage_multiplier
            
        if stage >= 15:  # 15층부터 영웅 아이템 확률 증가
            base_weights[ItemRarity.EPIC] += 5.0 * stage_multiplier
            base_weights[ItemRarity.LEGENDARY] += 2.0 * stage_multiplier
            base_weights[ItemRarity.RARE] -= 3.0 * stage_multiplier
            base_weights[ItemRarity.UNCOMMON] -= 3.0 * stage_multiplier
            
        if stage >= 20:  # 20층부터 전설 아이템 확률 대폭 증가
            base_weights[ItemRarity.LEGENDARY] += 5.0 * stage_multiplier
            base_weights[ItemRarity.EPIC] -= 2.0 * stage_multiplier
            
        # 음수 방지
        for rarity in base_weights:
            base_weights[rarity] = max(1.0, base_weights[rarity])
            
        return base_weights
    
    @staticmethod
    def get_drop_chance(stage: int) -> float:
        """스테이지별 아이템 드롭 확률"""
        base_chance = 0.3  # 기본 30%
        stage_bonus = min(stage * 0.02, 0.4)  # 스테이지당 2%, 최대 40% 추가
        return min(base_chance + stage_bonus, 0.8)  # 최대 80%
    
    @staticmethod
    def select_rarity_by_stage(stage: int) -> ItemRarity:
        """스테이지를 고려한 희귀도 선택"""
        weights = DropRateManager.get_rarity_weights(stage)
        
        # 가중치 기반 랜덤 선택
        total_weight = sum(weights.values())
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        for rarity, weight in weights.items():
            current_weight += weight
            if random_value <= current_weight:
                return rarity
                
        return ItemRarity.COMMON  # 기본값
    
    @staticmethod
    def get_bonus_drop_chance(stage: int) -> float:
        """보너스 드롭 확률 (추가 아이템)"""
        if stage < 5:
            return 0.0
        elif stage < 10:
            return 0.1  # 10%
        elif stage < 15:
            return 0.2  # 20%
        elif stage < 20:
            return 0.3  # 30%
        else:
            return 0.4  # 40%


class Item:
    """
    아이템 클래스 - 내구도 시스템 통합
    
    주요 속성 설명:
    - vision_range: 무기/장비의 가시거리 증가 효과 (매우 중요!)
        * 기본 시야가 3칸으로 축소되어 시야 증가 아이템이 필수적임
        * +1: 기본 가시거리에서 1칸 추가 (망원경, 정찰용 무기)
        * +2: 기본 가시거리에서 2칸 추가 (마법 망원경, 독수리 눈)
        * +3: 기본 가시거리에서 3칸 추가 (예언자의 수정구)
        * +4+: 매우 넓은 가시거리 (드래곤의 눈, 신의 시야)
        * 파티 전체의 vision_range 효과가 누적되어 최종 시야 결정
    - max_durability: 최대 내구도
    - current_durability: 현재 내구도
    - is_broken: 파괴 상태 여부
    """
    
    def __init__(self, name: str, item_type: ItemType, rarity: ItemRarity, 
                 description: str, value: int = 0, weight: float = 1.0, min_level: int = 1,
                 max_durability: int = None, special_effects: List[ItemEffect] = None,
                 elemental_affinity: ElementalAffinity = ElementalAffinity.NEUTRAL):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.description = description
        self.value = value  # 판매 가격
        self.weight = weight  # 무게
        self.min_level = min_level  # 최소 레벨 제한
        self.stats = {}  # 능력치 보너스 (vision_range 포함)
        self.effects = []  # 특수 효과 (구버전 호환)
        self.special_effects = special_effects or []  # 새로운 특수 효과 시스템
        self.elemental_affinity = elemental_affinity  # 원소 친화도
        self.elemental_resistances = {}  # 원소 저항 (ElementType: float)
        self.elemental_weaknesses = {}   # 원소 약점 (ElementType: float)
        self.special_properties = []     # 특수 속성들
        self.stage_scaling = self._calculate_stage_scaling()  # 스테이지별 스케일링
        self.field_usable = False  # 필드에서 사용 가능 여부
        self.combat_usable = True  # 전투에서 사용 가능 여부 (기본값 True)
        
        # 내구도 시스템
        self.max_durability = max_durability or self._get_default_durability()
        self.current_durability = self.max_durability
        self.repair_cost_multiplier = self._get_repair_cost_multiplier()
        self.upgrade_level = 0  # 강화 수준
        self.is_broken = False  # 파괴 상태
        self.protection_turns = 0  # 보호 효과 남은 턴 수
        
    def _get_default_durability(self) -> int:
        """희귀도별 기본 내구도 반환"""
        # 소모품은 내구도가 없음
        if self.item_type == ItemType.CONSUMABLE or self.item_type == ItemType.MATERIAL:
            return 0
            
        # 희귀도별 기본 내구도 설정
        rarity_durability = {
            ItemRarity.COMMON: 80,
            ItemRarity.UNCOMMON: 100,
            ItemRarity.RARE: 120,
            ItemRarity.EPIC: 150,
            ItemRarity.LEGENDARY: 200
        }
        
        return rarity_durability.get(self.rarity, 100)
    
    def _get_repair_cost_multiplier(self) -> float:
        """희귀도별 수리 비용 배수 반환"""
        rarity_multiplier = {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 1.2,
            ItemRarity.RARE: 1.5,
            ItemRarity.EPIC: 2.0,
            ItemRarity.LEGENDARY: 3.0
        }
        
        return rarity_multiplier.get(self.rarity, 1.0)
    
    def get_durability_percentage(self) -> float:
        """내구도 퍼센트 반환"""
        if self.max_durability == 0:
            return 100.0  # 소모품은 항상 100%
        return (self.current_durability / self.max_durability) * 100
    
    def get_durability_status(self) -> str:
        """내구도 상태 문자열"""
        if self.max_durability == 0:
            return ""  # 소모품은 내구도 표시 안함
            
        percentage = self.get_durability_percentage()
        if percentage >= 80:
            return "🔵"  # 최상
        elif percentage >= 50:
            return "🟢"  # 양호
        elif percentage >= 20:
            return "🟡"  # 보통
        elif percentage > 0:
            return "🔴"  # 나쁨
        else:
            return "🤯"  # 파괴됨
    
    def damage_durability(self, amount: int = 1) -> bool:
        """내구도 감소 - 파괴 여부 반환"""
        if self.max_durability == 0 or self.is_broken:
            return False
        
        # 보호 효과가 있으면 내구도 감소 방지
        if self.protection_turns > 0:
            self.protection_turns = max(0, self.protection_turns - 1)
            return False
        
        self.current_durability = max(0, self.current_durability - amount)
        
        if self.current_durability <= 0:
            self.is_broken = True
            return True
        
        return False
    
    def repair(self, amount: int = None) -> int:
        """수리 - 수리 비용 반환"""
        if self.max_durability == 0:
            return 0  # 소모품은 수리 불가
            
        if amount is None:
            amount = self.max_durability - self.current_durability
        
        actual_repair = min(amount, self.max_durability - self.current_durability)
        self.current_durability += actual_repair
        
        if self.current_durability >= self.max_durability:
            self.is_broken = False
        
        # 수리 비용 계산
        base_cost = actual_repair * self.repair_cost_multiplier
        total_cost = int(base_cost * (1.0 + self.upgrade_level * 0.2))  # 강화 수준에 따라 비용 증가
        
        return total_cost
    
    def get_effective_stats(self) -> Dict[str, int]:
        """내구도에 따른 실제 능력치 반환"""
        if self.max_durability == 0:
            return self.stats.copy()  # 소모품은 내구도 영향 없음
            
        if self.is_broken:
            return {stat: 0 for stat in self.stats if isinstance(self.stats[stat], (int, float))}
        
        # 내구도가 낮을수록 능력치 감소
        durability_factor = self.get_durability_percentage() / 100
        
        # 내구도 50% 이하부터 능력치 감소 시작
        if durability_factor < 0.5:
            effectiveness = 0.3 + (durability_factor * 1.4)  # 30%~100% 범위
        else:
            effectiveness = 1.0
        
        effective_stats = {}
        for stat, value in self.stats.items():
            if isinstance(value, (int, float)):
                effective_stats[stat] = int(value * effectiveness)
            else:
                effective_stats[stat] = value  # 숫자가 아닌 값은 그대로
                
        return effective_stats
    
    def get_display_name(self) -> str:
        """표시용 이름 (등급, 강화, 내구도 포함)"""
        rarity_colors = {
            ItemRarity.COMMON: "⚪",
            ItemRarity.UNCOMMON: "🟢",
            ItemRarity.RARE: "🔵",
            ItemRarity.EPIC: "🟣",
            ItemRarity.LEGENDARY: "🟠"
        }
        
        element_icons = {
            ElementalAffinity.FIRE: "🔥",
            ElementalAffinity.ICE: "❄️",
            ElementalAffinity.LIGHTNING: "⚡",
            ElementalAffinity.EARTH: "🌍",
            ElementalAffinity.WIND: "💨",
            ElementalAffinity.WATER: "💧",
            ElementalAffinity.LIGHT: "✨",
            ElementalAffinity.DARK: "🌑",
            ElementalAffinity.POISON: "☠️",
            ElementalAffinity.NEUTRAL: ""
        }
        
        color = rarity_colors.get(self.rarity, "⚪")
        element = element_icons.get(self.elemental_affinity, "")
        upgrade_text = f"+{self.upgrade_level}" if self.upgrade_level > 0 else ""
        durability_icon = self.get_durability_status()
        
        return f"{color}{element}{self.name}{upgrade_text}{durability_icon}"
        
    def _calculate_stage_scaling(self) -> Dict[str, float]:
        """희귀도별 스테이지 스케일링 계수"""
        scaling_factors = {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 1.2,
            ItemRarity.RARE: 1.5,
            ItemRarity.EPIC: 2.0,
            ItemRarity.LEGENDARY: 3.0
        }
        
        return {
            "stat_multiplier": scaling_factors[self.rarity],
            "value_multiplier": scaling_factors[self.rarity]
        }
    
    def apply_stage_scaling(self, stage: int):
        """스테이지에 따른 아이템 스케일링 적용"""
        if stage <= 1:
            return
            
        # 스테이지 보너스 계산
        stage_bonus = 1.0 + (stage - 1) * 0.1 * self.stage_scaling["stat_multiplier"]
        
        # 스탯 스케일링 (숫자 값만)
        for stat_name in self.stats:
            stat_value = self.stats[stat_name]
            if isinstance(stat_value, (int, float)):
                self.stats[stat_name] = int(stat_value * stage_bonus)
            
        # 가격 스케일링
        self.value = int(self.value * stage_bonus * self.stage_scaling["value_multiplier"])
        
    def get_display_char(self) -> str:
        """표시용 문자 반환 (맵용 기호)"""
        if self.item_type == ItemType.CONSUMABLE:
            return "!"
        elif self.item_type == ItemType.WEAPON:
            return "L"  # 맵에서 무기 표시
        elif self.item_type == ItemType.ARMOR:
            return "]"
        elif self.item_type == ItemType.ACCESSORY:
            return "Q"  # 맵에서 액세서리 표시
        else:
            return "?"
            
    def get_colored_name(self) -> str:
        """희귀도에 따른 컬러 이름"""
        color_prefix = {
            ItemRarity.COMMON: "",
            ItemRarity.UNCOMMON: "★",
            ItemRarity.RARE: "★★",
            ItemRarity.EPIC: "★★★",
            ItemRarity.LEGENDARY: "★★★★"
        }
        level_text = f" (Lv.{self.min_level}+)" if hasattr(self, 'min_level') and self.min_level > 1 else ""
        return f"{color_prefix[self.rarity]}{self.name}{level_text}"
    
    def can_be_obtained_at_level(self, level: int) -> bool:
        """특정 레벨에서 얻을 수 있는지 확인"""
        return not hasattr(self, 'min_level') or self.min_level <= level
        
    def get_effect_description(self) -> str:
        """아이템 효과를 한국어로 표시"""
        if not self.effects:
            return "효과 없음"
        
        effect_descriptions = []
        for effect in self.effects:
            if effect == "heal":
                heal_amount = self.stats.get("heal_amount", 50)
                effect_descriptions.append(f"HP {heal_amount} 회복")
            elif effect == "field_rest":
                heal_amount = self.stats.get("heal_amount", 50)
                mp_amount = self.stats.get("mp_amount", 20)
                effect_descriptions.append(f"필드 휴식 (HP {heal_amount}, MP {mp_amount} 회복)")
            elif effect == "full_rest":
                effect_descriptions.append("완전 휴식 (HP/MP 완전 회복)")
            elif effect == "cure_all":
                effect_descriptions.append("모든 상태이상 치료")
            elif effect == "brave_boost":
                brave_amount = self.stats.get("brave_amount", 500)
                effect_descriptions.append(f"Brave +{brave_amount}")
            elif effect == "revive":
                revive_percent = self.stats.get("revive_hp_percent", 50)
                effect_descriptions.append(f"부활 (HP {revive_percent}%)")
            elif effect == "temp_strength":
                boost = self.stats.get("strength_boost", 10)
                duration = self.stats.get("duration", 3)
                effect_descriptions.append(f"물리공격력 +{boost} ({duration}턴)")
            elif effect == "temp_magic":
                boost = self.stats.get("magic_boost", 15)
                duration = self.stats.get("duration", 5)
                effect_descriptions.append(f"마법공격력 +{boost} ({duration}턴)")
            elif effect == "temp_haste":
                boost = self.stats.get("speed_boost", 10)
                duration = self.stats.get("duration", 4)
                effect_descriptions.append(f"속도 +{boost} ({duration}턴)")
            elif effect == "party_barrier":
                reduction = self.stats.get("damage_reduction", 50)
                duration = self.stats.get("duration", 3)
                effect_descriptions.append(f"파티 방어막 ({reduction}% 피해감소, {duration}턴)")
            elif effect == "berserk":
                atk_boost = self.stats.get("attack_boost", 25)
                def_penalty = self.stats.get("defense_penalty", 10)
                duration = self.stats.get("duration", 3)
                effect_descriptions.append(f"광폭화 (공격+{atk_boost}, 방어-{def_penalty}, {duration}턴)")
            else:
                effect_descriptions.append(effect)  # 기본값으로 영어 표시
        
        return ", ".join(effect_descriptions)
    
    def use_item(self, character):
        """아이템 사용"""
        if self.item_type == ItemType.CONSUMABLE:
            return self._use_consumable(character)
        return False
        
    def _use_consumable(self, character) -> bool:
        """소모품 사용 - 완전 구현"""
        used = False
        
        # 1. 기본 회복 효과
        if "heal" in self.effects:
            heal_amount = self.stats.get("heal_amount", 50)
            actual_heal = character.heal(heal_amount)
            print(f"💊 {character.name}이(가) {self.name}을(를) 사용하여 {actual_heal} HP 회복했습니다!")
            used = True
            
        if "mana_restore" in self.effects:
            mp_amount = self.stats.get("mp_amount", 30)
            old_mp = character.current_mp
            character.current_mp = min(character.max_mp, character.current_mp + mp_amount)
            actual_mp = character.current_mp - old_mp
            if actual_mp > 0:
                print(f"🔵 {character.name}이(가) {actual_mp} MP 회복했습니다!")
                used = True
        
        # 2. 완전 회복 효과
        if "full_heal" in self.effects:
            old_hp = character.current_hp
            character.current_hp = character.max_hp
            heal_amount = character.current_hp - old_hp
            print(f"✨ {character.name}의 HP가 완전히 회복되었습니다! (+{heal_amount})")
            used = True
            
        if "full_mana" in self.effects:
            old_mp = character.current_mp
            character.current_mp = character.max_mp
            mp_amount = character.current_mp - old_mp
            print(f"💎 {character.name}의 MP가 완전히 회복되었습니다! (+{mp_amount})")
            used = True
        
        # 3. 상태이상 치료
        if "cure_poison" in self.effects:
            if hasattr(character, 'status_manager') and character.status_manager:
                removed = character.status_manager.remove_status("독")
                if removed:
                    print(f"💚 {character.name}의 독이 치료되었습니다!")
                    used = True
                    
        if "cure_burn" in self.effects:
            if hasattr(character, 'status_manager') and character.status_manager:
                removed = character.status_manager.remove_status("화상")
                if removed:
                    print(f"❄️ {character.name}의 화상이 치료되었습니다!")
                    used = True
        
        if "cure_all" in self.effects:
            if hasattr(character, 'status_manager') and character.status_manager:
                character.status_manager.clear_all_negative_effects()
                print(f"✨ {character.name}의 모든 상태이상이 치료되었습니다!")
                used = True
        
        # 4. 임시 버프 효과
        if "buff_strength" in self.effects:
            bonus = self.stats.get("strength_bonus", 10)
            duration = self.stats.get("buff_duration", 10)
            character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + bonus
            character.temp_buff_duration = getattr(character, 'temp_buff_duration', 0) + duration
            print(f"💪 {character.name}의 공격력이 {bonus} 증가했습니다! ({duration}턴)")
            used = True
            
        if "buff_defense" in self.effects:
            bonus = self.stats.get("defense_bonus", 10)
            duration = self.stats.get("buff_duration", 10)
            character.temp_defense_bonus = getattr(character, 'temp_defense_bonus', 0) + bonus
            character.temp_defense_duration = getattr(character, 'temp_defense_duration', 0) + duration
            print(f"🛡️ {character.name}의 방어력이 {bonus} 증가했습니다! ({duration}턴)")
            used = True
            
        if "buff_speed" in self.effects:
            bonus = self.stats.get("speed_bonus", 5)
            duration = self.stats.get("buff_duration", 10)
            character.temp_speed_bonus = getattr(character, 'temp_speed_bonus', 0) + bonus
            character.temp_speed_duration = getattr(character, 'temp_speed_duration', 0) + duration
            print(f"🏃 {character.name}의 속도가 {bonus} 증가했습니다! ({duration}턴)")
            used = True
            
        if "buff_magic" in self.effects:
            bonus = self.stats.get("magic_bonus", 10)
            duration = self.stats.get("buff_duration", 10)
            character.temp_magic_bonus = getattr(character, 'temp_magic_bonus', 0) + bonus
            character.temp_magic_duration = getattr(character, 'temp_magic_duration', 0) + duration
            print(f"🔮 {character.name}의 마법력이 {bonus} 증가했습니다! ({duration}턴)")
            used = True
        
        # 5. 영구 스탯 증가
        if "permanent_hp" in self.effects:
            bonus = self.stats.get("hp_bonus", 10)
            character.max_hp += bonus
            character.current_hp += bonus  # 현재 HP도 같이 증가
            print(f"❤️ {character.name}의 최대 HP가 영구히 {bonus} 증가했습니다!")
            used = True
            
        if "permanent_mp" in self.effects:
            bonus = self.stats.get("mp_bonus", 5)
            character.max_mp += bonus
            character.current_mp += bonus  # 현재 MP도 같이 증가
            print(f"💙 {character.name}의 최대 MP가 영구히 {bonus} 증가했습니다!")
            used = True
            
        if "permanent_attack" in self.effects:
            bonus = self.stats.get("attack_bonus", 2)
            character.physical_attack += bonus
            print(f"⚔️ {character.name}의 물리공격력이 영구히 {bonus} 증가했습니다!")
            used = True
            
        if "permanent_magic" in self.effects:
            bonus = self.stats.get("magic_bonus", 2)
            character.magic_attack += bonus
            print(f"🌟 {character.name}의 마법공격력이 영구히 {bonus} 증가했습니다!")
            used = True
            
        if "permanent_defense" in self.effects:
            bonus = self.stats.get("defense_bonus", 2)
            character.physical_defense += bonus
            print(f"🛡️ {character.name}의 물리방어력이 영구히 {bonus} 증가했습니다!")
            used = True
            
        if "permanent_speed" in self.effects:
            bonus = self.stats.get("speed_bonus", 1)
            character.speed += bonus
            print(f"💨 {character.name}의 속도가 영구히 {bonus} 증가했습니다!")
            used = True
        
        # 6. 공격 아이템 효과 (폭탄 등)
        if "damage_enemy" in self.effects:
            damage_amount = self.stats.get("damage_amount", 50)
            print(f"💥 {self.name} 폭발! 적에게 {damage_amount}의 피해를 가합니다!")
            # 전투 시스템에서 적 선택은 별도로 처리
            used = True
            
        if "damage_all_enemies" in self.effects:
            damage_amount = self.stats.get("damage_amount", 40)
            print(f"💥💥 {self.name} 대폭발! 모든 적에게 {damage_amount}의 피해를 가합니다!")
            used = True
            
        if "blind_enemies" in self.effects:
            duration = self.stats.get("duration", 3)
            print(f"💨 {self.name} 사용! 적들을 {duration}턴 동안 실명 상태로 만듭니다!")
            used = True
            
        # 7. 특수 효과
        if "revive" in self.effects:
            if character.current_hp <= 0:
                revive_hp = self.stats.get("revive_hp", character.max_hp // 2)
                character.current_hp = min(character.max_hp, revive_hp)
                character.is_dead = False
                if hasattr(character, 'status_manager'):
                    character.status_manager.clear_all_negative_effects()
                print(f"🕊️ {character.name}이(가) 부활했습니다! (HP: {character.current_hp})")
                used = True
            else:
                print(f"❌ {character.name}은(는) 이미 살아있습니다!")
                return False
        
        if "berserk" in self.effects:
            attack_boost = self.stats.get("attack_boost", 25)
            defense_penalty = self.stats.get("defense_penalty", 10)
            duration = self.stats.get("duration", 3)
            character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + attack_boost
            character.temp_defense_bonus = getattr(character, 'temp_defense_bonus', 0) - defense_penalty
            character.temp_berserk_duration = duration
            print(f"😤 {character.name}이(가) 광폭화 상태에 돌입! 공격+{attack_boost}, 방어-{defense_penalty} ({duration}턴)")
            used = True
            
        if "invisibility" in self.effects:
            duration = self.stats.get("duration", 5)
            character.stealth_turns = duration
            character.temp_invisibility = True
            print(f"👻 {character.name}이(가) 투명해졌습니다! ({duration}턴)")
            used = True
            
        if "time_stop" in self.effects:
            character.temp_extra_turn = True
            print(f"⏰ {character.name}이(가) 시간을 정지시켰습니다! 다음 턴에 2번 행동 가능!")
            used = True
            
        if "teleport" in self.effects:
            character.temp_dodge_bonus = getattr(character, 'temp_dodge_bonus', 0) + 100  # 100% 회피
            character.temp_teleport_duration = 1
            print(f"🌀 {character.name}이(가) 순간이동으로 다음 공격을 회피합니다!")
            used = True
            
        if "explosion" in self.effects:
            damage = self.stats.get("explosion_damage", 100)
            character.temp_explosion_damage = damage
            character.temp_explosion_ready = True
            print(f"💥 {character.name}이(가) 폭발 공격을 준비했습니다! (피해: {damage})")
            used = True
            
        if "summon_ally" in self.effects:
            ally_type = self.stats.get("ally_type", "골렘")
            ally_duration = self.stats.get("ally_duration", 10)
            character.temp_summoned_ally = ally_type
            character.temp_ally_duration = ally_duration
            print(f"🤖 {character.name}이(가) {ally_type}을(를) 소환했습니다! ({ally_duration}턴)")
            used = True
        
        # 7. 휴식 관련 효과
        if "field_rest" in self.effects:
            heal_amount = self.stats.get("heal_amount", 50)
            mp_amount = self.stats.get("mp_amount", 20)
            actual_heal = character.heal(heal_amount)
            character.recover_mp(mp_amount)
            print(f"🏕️ {character.name}이(가) {self.name}을(를) 설치하여 휴식을 취했습니다!")
            print(f"HP {actual_heal} 회복, MP {mp_amount} 회복!")
            used = True
            
        if "full_rest" in self.effects:
            heal_amount = self.stats.get("heal_amount", 9999)
            mp_amount = self.stats.get("mp_amount", 9999)
            actual_heal = character.heal(heal_amount)
            character.recover_mp(mp_amount)
            if "cure_all" in self.effects:
                if hasattr(character, 'cure_all_status_effects'):
                    character.cure_all_status_effects()
                print(f"🏰 {character.name}이(가) {self.name}에서 완전한 휴식을 취했습니다!")
                print(f"HP 완전 회복, MP 완전 회복, 모든 상태이상 치료!")
            else:
                print(f"🏰 {character.name}이(가) {self.name}에서 완전한 휴식을 취했습니다!")
                print(f"HP 완전 회복, MP 완전 회복!")
            used = True
            
        if "teleport_town" in self.effects:
            # 마을로 귀환
            print(f"{character.name}이(가) {self.name}을(를) 사용하여 마을로 돌아갑니다!")
            return True
        elif "escape_floor" in self.effects:
            # 현재 층 탈출
            print(f"{character.name}이(가) {self.name}을(를) 사용하여 이 층을 벗어납니다!")
            return True
        elif "unlock" in self.effects:
            # 자물쇠 해제
            print(f"{character.name}이(가) {self.name}을(를) 사용하여 자물쇠를 해제했습니다!")
            return True
        elif "detect_treasure" in self.effects:
            # 보물 탐지
            print(f"{character.name}이(가) {self.name}을(를) 사용하여 주변을 탐지합니다!")
            print("숨겨진 보물과 비밀통로의 위치가 밝혀졌습니다!")
            return True
        elif "brave_boost" in self.effects:
            # Brave 포인트 증가
            brave_amount = self.stats.get("brave_amount", 500)
            if hasattr(character, 'add_brave_points'):
                character.add_brave_points(brave_amount)
                print(f"{character.name}이(가) {self.name}을(를) 사용하여 Brave +{brave_amount}!")
                return True
            else:
                print(f"{character.name}은(는) Brave 시스템을 사용하지 않습니다.")
                return False
        elif "revive" in self.effects:
            # 부활
            if not character.is_alive:
                character.is_alive = True
                revive_percent = self.stats.get("revive_hp_percent", 50)
                revive_hp = int(character.max_hp * (revive_percent / 100))
                character.current_hp = revive_hp
                print(f"{character.name}이(가) 부활했습니다! HP: {revive_hp}")
                return True
            else:
                print(f"{character.name}은(는) 이미 살아있습니다!")
                return False
        elif "cure" in self.effects:
            # 상태이상 치료
            if hasattr(character, 'cure_all_status_effects'):
                character.cure_all_status_effects()
            print(f"{character.name}의 모든 상태이상이 치료되었습니다!")
            return True
        
        # 추가 효과들
        elif "weapon_blessing" in self.effects:
            # 무기 축복 - 일정 턴간 크리티컬 확률 증가
            duration = self.stats.get("duration", 10)
            crit_bonus = self.stats.get("crit_bonus", 20)
            character.temp_crit_bonus = getattr(character, 'temp_crit_bonus', 0) + crit_bonus
            character.temp_weapon_blessing_duration = duration
            print(f"⚔️✨ {character.name}의 무기가 축복받았습니다! 크리티컬 +{crit_bonus}% ({duration}턴)")
            return True
            
        elif "armor_blessing" in self.effects:
            # 방어구 축복 - 일정 턴간 방어력 증가
            duration = self.stats.get("duration", 10)
            def_bonus = self.stats.get("defense_bonus", 20)
            character.temp_defense_bonus = getattr(character, 'temp_defense_bonus', 0) + def_bonus
            character.temp_armor_blessing_duration = duration
            print(f"🛡️✨ {character.name}의 방어구가 축복받았습니다! 방어력 +{def_bonus} ({duration}턴)")
            return True
            
        elif "transformation" in self.effects:
            # 변신 효과
            transform_type = self.stats.get("transform_type", "드래곤")
            duration = self.stats.get("duration", 8)
            stat_bonus = self.stats.get("stat_bonus", 30)
            
            character.temp_transformation = transform_type
            character.temp_transform_duration = duration
            character.temp_attack_bonus = getattr(character, 'temp_attack_bonus', 0) + stat_bonus
            character.temp_defense_bonus = getattr(character, 'temp_defense_bonus', 0) + stat_bonus
            character.temp_magic_bonus = getattr(character, 'temp_magic_bonus', 0) + stat_bonus
            character.temp_speed_bonus = getattr(character, 'temp_speed_bonus', 0) + stat_bonus
            
            print(f"🐉 {character.name}이(가) {transform_type}으로 변신했습니다!")
            print(f"   모든 능력치 +{stat_bonus} ({duration}턴)")
            return True
        
        return used if 'used' in locals() else False


class ItemDatabase:
    """아이템 데이터베이스"""
    
    @staticmethod
    def get_all_items() -> List[Item]:
        """모든 아이템 데이터"""
        items = []
        
        # === 소모품 ===
        heal_potion = Item("치료 포션", ItemType.CONSUMABLE, ItemRarity.COMMON, 
                          "HP를 50 회복한다")
        heal_potion.stats = {"heal_amount": 50}
        heal_potion.effects = ["heal"]
        heal_potion.value = 20
        heal_potion.field_usable = True  # 필드에서 사용 가능
        items.append(heal_potion)
        
        great_heal_potion = Item("상급 치료 포션", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                                "HP를 100 회복한다")
        great_heal_potion.stats = {"heal_amount": 100}
        great_heal_potion.effects = ["heal"]
        great_heal_potion.value = 50
        great_heal_potion.field_usable = True
        items.append(great_heal_potion)
        
        super_heal_potion = Item("최상급 치료 포션", ItemType.CONSUMABLE, ItemRarity.RARE,
                                "HP를 200 회복한다", min_level=5)
        super_heal_potion.stats = {"heal_amount": 200}
        super_heal_potion.effects = ["heal"]
        super_heal_potion.value = 100
        super_heal_potion.field_usable = True
        items.append(super_heal_potion)
        
        # === MP 회복 아이템 ===
        mana_potion = Item("마나 포션", ItemType.CONSUMABLE, ItemRarity.COMMON,
                          "MP를 30 회복한다")
        mana_potion.stats = {"mp_amount": 30}
        mana_potion.effects = ["mana_restore"]
        mana_potion.value = 25
        mana_potion.field_usable = True
        items.append(mana_potion)
        
        great_mana_potion = Item("상급 마나 포션", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                                "MP를 60 회복한다")
        great_mana_potion.stats = {"mp_amount": 60}
        great_mana_potion.effects = ["mana_restore"]
        great_mana_potion.value = 50
        great_mana_potion.field_usable = True
        items.append(great_mana_potion)
        
        # === 필드 전용 아이템 ===
        camping_tent = Item("야영 텐트", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                           "필드에서 휴식을 취해 HP/MP를 회복한다")
        camping_tent.stats = {"heal_amount": 80, "mp_amount": 40}
        camping_tent.effects = ["field_rest"]
        camping_tent.value = 100
        camping_tent.field_usable = True
        camping_tent.combat_usable = False  # 전투 중 사용 불가
        items.append(camping_tent)
        
        luxury_tent = Item("고급 텐트", ItemType.CONSUMABLE, ItemRarity.RARE,
                          "필드에서 완전한 휴식으로 HP/MP 완전 회복")
        luxury_tent.stats = {"heal_amount": 9999, "mp_amount": 9999}
        luxury_tent.effects = ["full_rest", "cure_all"]
        luxury_tent.value = 300
        luxury_tent.field_usable = True
        luxury_tent.combat_usable = False
        items.append(luxury_tent)
        
        teleport_scroll = Item("귀환 두루마리", ItemType.CONSUMABLE, ItemRarity.RARE,
                              "즉시 마을로 돌아간다")
        teleport_scroll.effects = ["teleport_town"]
        teleport_scroll.value = 150
        teleport_scroll.field_usable = True
        teleport_scroll.combat_usable = False
        items.append(teleport_scroll)
        
        escape_rope = Item("탈출 로프", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "현재 층을 벗어난다")
        escape_rope.effects = ["escape_floor"]
        escape_rope.value = 80
        escape_rope.field_usable = True
        escape_rope.combat_usable = False
        items.append(escape_rope)
        
        lockpick_set = Item("자물쇠 도구", ItemType.CONSUMABLE, ItemRarity.COMMON,
                           "잠긴 문이나 상자를 열 수 있다")
        lockpick_set.effects = ["unlock"]
        lockpick_set.value = 40
        lockpick_set.field_usable = True
        lockpick_set.combat_usable = False
        items.append(lockpick_set)
        
        treasure_detector = Item("보물 탐지기", ItemType.CONSUMABLE, ItemRarity.RARE,
                                "숨겨진 보물과 비밀통로를 찾는다")
        treasure_detector.effects = ["detect_treasure"]
        treasure_detector.value = 120
        treasure_detector.field_usable = True
        treasure_detector.combat_usable = False
        items.append(treasure_detector)
        
        # === 상태이상 치료 ===
        antidote = Item("해독제", ItemType.CONSUMABLE, ItemRarity.COMMON,
                       "모든 상태이상을 치료한다")
        antidote.effects = ["cure"]
        antidote.value = 30
        antidote.field_usable = True
        items.append(antidote)
        
        energy_drink = Item("에너지 드링크", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                           "ATB 게이지를 50 증가시킨다")
        energy_drink.effects = ["atb_boost"]
        energy_drink.stats = {"atb_amount": 50}
        energy_drink.value = 40
        items.append(energy_drink)
        
        # === 전투용 소모품 ===
        bomb = Item("폭탄", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                   "적에게 큰 피해를 준다")
        bomb.effects = ["damage_enemy"]
        bomb.stats = {"damage_amount": 80, "target": "enemy"}
        bomb.value = 60
        items.append(bomb)
        
        poison_dart = Item("독침", ItemType.CONSUMABLE, ItemRarity.COMMON,
                          "적에게 독 상태이상을 건다")
        poison_dart.effects = ["poison_enemy"]
        poison_dart.stats = {"damage_amount": 30, "poison_turns": 3}
        poison_dart.value = 35
        items.append(poison_dart)
        
        smoke_bomb = Item("연막탄", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                         "모든 적의 명중률을 크게 감소시킨다")
        smoke_bomb.effects = ["blind_enemies"]
        smoke_bomb.stats = {"duration": 3}
        smoke_bomb.value = 45
        items.append(smoke_bomb)
        
        holy_water = Item("성수", ItemType.CONSUMABLE, ItemRarity.RARE,
                         "언데드 적에게 특효! 아군은 축복 효과")
        holy_water.effects = ["holy_damage", "bless_party"]
        holy_water.stats = {"damage_amount": 120, "bless_turns": 2}
        holy_water.value = 80
        items.append(holy_water)
        
        fire_bottle = Item("화염병", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "적들에게 화상 피해를 입힌다")
        fire_bottle.effects = ["fire_damage_all"]
        fire_bottle.stats = {"damage_amount": 60, "burn_turns": 2}
        fire_bottle.value = 55
        items.append(fire_bottle)
        
        ice_crystal = Item("얼음 수정", ItemType.CONSUMABLE, ItemRarity.RARE,
                          "적의 행동을 지연시킨다")
        ice_crystal.effects = ["slow_enemy"]
        ice_crystal.stats = {"atb_reduction": 30, "slow_turns": 2}
        ice_crystal.value = 70
        items.append(ice_crystal)
        
        lightning_orb = Item("번개 구슬", ItemType.CONSUMABLE, ItemRarity.RARE,
                            "모든 적에게 전격 피해")
        lightning_orb.effects = ["lightning_all"]
        lightning_orb.stats = {"damage_amount": 75}
        lightning_orb.value = 85
        items.append(lightning_orb)
        
        strength_potion = Item("힘의 물약", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                              "일시적으로 공격력을 크게 증가시킨다")
        strength_potion.effects = ["temp_strength"]
        strength_potion.stats = {"attack_boost": 15, "duration": 5}
        strength_potion.value = 50
        items.append(strength_potion)
        
        magic_potion = Item("마력의 물약", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                           "일시적으로 마법 공격력을 증가시킨다")
        magic_potion.effects = ["temp_magic"]
        magic_potion.stats = {"magic_boost": 15, "duration": 5}
        magic_potion.value = 50
        items.append(magic_potion)
        
        barrier_scroll = Item("방어막 두루마리", ItemType.CONSUMABLE, ItemRarity.RARE,
                             "파티 전체에 피해 감소 방어막을 친다")
        barrier_scroll.effects = ["party_barrier"]
        barrier_scroll.stats = {"damage_reduction": 50, "duration": 3}
        barrier_scroll.value = 90
        items.append(barrier_scroll)
        
        haste_potion = Item("신속의 물약", ItemType.CONSUMABLE, ItemRarity.RARE,
                           "일시적으로 속도를 크게 증가시킨다")
        haste_potion.effects = ["temp_haste"]
        haste_potion.stats = {"speed_boost": 10, "duration": 4}
        haste_potion.value = 75
        items.append(haste_potion)
        
        revival_feather = Item("부활의 깃털", ItemType.CONSUMABLE, ItemRarity.EPIC,
                              "쓰러진 동료를 50% HP로 부활시킨다", min_level=10)
        revival_feather.effects = ["revive"]
        revival_feather.stats = {"revive_hp_percent": 50}
        revival_feather.value = 200
        items.append(revival_feather)
        
        berserk_potion = Item("광폭화 물약", ItemType.CONSUMABLE, ItemRarity.EPIC,
                             "공격력 대폭 증가, 방어력 감소", min_level=8)
        berserk_potion.effects = ["berserk"]
        berserk_potion.stats = {"attack_boost": 25, "defense_penalty": 10, "duration": 3}
        berserk_potion.value = 120
        items.append(berserk_potion)
        
        # === 무기 (50개) ===
        
        # 기본 검류
        rusty_sword = Item("녹슨 검", ItemType.WEAPON, ItemRarity.COMMON,
                          "낡고 녹슨 검", 10, 2.0)
        rusty_sword.stats = {"physical_attack": 5}
        rusty_sword.effects = ["durability_low"]
        items.append(rusty_sword)
        
        iron_sword = Item("철검", ItemType.WEAPON, ItemRarity.COMMON,
                         "평범한 철로 만든 검", 50, 3.0)
        iron_sword.stats = {"physical_attack": 12}
        items.append(iron_sword)
        
        silver_sword = Item("은 검", ItemType.WEAPON, ItemRarity.UNCOMMON,
                           "언데드에게 효과적인 은 검", 120, 2.5)
        silver_sword.stats = {"physical_attack": 15}
        silver_sword.effects = ["undead_bane"]
        items.append(silver_sword)
        
        flame_sword = Item("화염 검", ItemType.WEAPON, ItemRarity.RARE,
                          "불꽃이 타오르는 마법 검", 300, 3.5)
        flame_sword.stats = {"physical_attack": 20, "magic_attack": 8}
        flame_sword.effects = ["burn_chance_25"]
        items.append(flame_sword)
        
        ice_sword = Item("얼음 검", ItemType.WEAPON, ItemRarity.RARE,
                        "얼음 기운이 감도는 검", 300, 3.5)
        ice_sword.stats = {"physical_attack": 18, "magic_attack": 10}
        ice_sword.effects = ["freeze_chance_30"]
        items.append(ice_sword)
        
        vampire_sword = Item("뱀파이어 검", ItemType.WEAPON, ItemRarity.EPIC,
                            "피를 흡수하는 저주받은 검", 600, 4.0, min_level=12)
        vampire_sword.stats = {"physical_attack": 25}
        vampire_sword.effects = ["life_steal_15", "hp_drain_1"]
        items.append(vampire_sword)
        
        holy_sword = Item("신성한 검", ItemType.WEAPON, ItemRarity.EPIC,
                         "성스러운 힘이 깃든 검", 650, 3.0, min_level=12)
        holy_sword.stats = {"physical_attack": 22, "magic_attack": 15}
        holy_sword.effects = ["demon_slayer", "hp_regen"]
        items.append(holy_sword)
        
        dragonslayer = Item("용살자의 검", ItemType.WEAPON, ItemRarity.LEGENDARY,
                           "드래곤을 베어낸 전설의 검", 1500, 5.0, min_level=20)
        dragonslayer.stats = {"physical_attack": 40, "magic_attack": 20}
        dragonslayer.effects = ["crit_chance_25", "dragon_slayer"]
        items.append(dragonslayer)
        
        # 단검류
        dagger = Item("단검", ItemType.WEAPON, ItemRarity.COMMON,
                     "빠른 공격이 가능한 단검", 20, 1.0)
        dagger.stats = {"physical_attack": 8, "speed": 3}
        items.append(dagger)
        
        poison_dagger = Item("독침 단검", ItemType.WEAPON, ItemRarity.UNCOMMON,
                            "독이 발린 암살자의 단검", 80, 1.2)
        poison_dagger.stats = {"physical_attack": 10}
        poison_dagger.effects = ["poison_chance_50"]
        items.append(poison_dagger)
        
        shadow_dagger = Item("그림자 단검", ItemType.WEAPON, ItemRarity.RARE,
                            "그림자에서 나타나는 신비한 단검", 250, 1.5)
        shadow_dagger.stats = {"physical_attack": 15, "speed": 8}
        shadow_dagger.effects = ["first_strike_crit", "stealth"]
        items.append(shadow_dagger)
        
        time_dagger = Item("시간의 단검", ItemType.WEAPON, ItemRarity.EPIC,
                          "시간을 조작하는 마법 단검", 800, 2.0)
        time_dagger.stats = {"physical_attack": 18, "speed": 15}
        time_dagger.effects = ["atb_drain", "double_attack"]
        items.append(time_dagger)
        
        # 둔기류
        wooden_club = Item("나무 곤봉", ItemType.WEAPON, ItemRarity.COMMON,
                          "단단한 나무로 만든 곤봉", 15, 4.0)
        wooden_club.stats = {"physical_attack": 10, "physical_defense": 2}
        items.append(wooden_club)
        
        iron_mace = Item("철퇴", ItemType.WEAPON, ItemRarity.UNCOMMON,
                        "무거운 철로 만든 둔기", 100, 6.0)
        iron_mace.stats = {"physical_attack": 18}
        iron_mace.effects = ["stun_chance_20"]
        items.append(iron_mace)
        
        thunder_hammer = Item("뇌전 망치", ItemType.WEAPON, ItemRarity.RARE,
                             "번개가 깃든 거대한 망치", 400, 8.0)
        thunder_hammer.stats = {"physical_attack": 25, "magic_attack": 10}
        thunder_hammer.effects = ["chain_lightning"]
        items.append(thunder_hammer)
        
        earthquake_hammer = Item("지진 망치", ItemType.WEAPON, ItemRarity.EPIC,
                                "대지를 뒤흔드는 전설의 망치", 900, 10.0)
        earthquake_hammer.stats = {"physical_attack": 35}
        earthquake_hammer.effects = ["area_knockdown", "armor_pierce_10"]
        items.append(earthquake_hammer)
        
        # 원거리 무기
        short_bow = Item("단궁", ItemType.WEAPON, ItemRarity.COMMON,
                        "간단한 나무 활", 30, 2.0)
        short_bow.stats = {"physical_attack": 12, "speed": 5}
        items.append(short_bow)
        
        long_bow = Item("장궁", ItemType.WEAPON, ItemRarity.UNCOMMON,
                       "사거리가 긴 강화된 활", 90, 3.0)
        long_bow.stats = {"physical_attack": 16, "speed": 3}
        long_bow.effects = ["no_counter"]
        items.append(long_bow)
        
        elf_bow = Item("엘프의 활", ItemType.WEAPON, ItemRarity.RARE,
                      "정밀도가 높은 엘프 제작 활", 280, 2.5)
        elf_bow.stats = {"physical_attack": 20, "speed": 8}
        elf_bow.effects = ["crit_chance_20", "pierce"]
        items.append(elf_bow)
        
        wind_bow = Item("바람의 활", ItemType.WEAPON, ItemRarity.EPIC,
                       "바람 정령이 깃든 신비한 활", 600, 2.0)
        wind_bow.stats = {"physical_attack": 22, "speed": 12}
        wind_bow.effects = ["wind_magic", "multi_shot"]
        items.append(wind_bow)
        
        starlight_bow = Item("별빛 활", ItemType.WEAPON, ItemRarity.LEGENDARY,
                            "별의 힘을 담은 신화의 활", 1200, 3.0)
        starlight_bow.stats = {"physical_attack": 30, "magic_attack": 25}
        starlight_bow.effects = ["infinite_arrows", "global_range"]
        items.append(starlight_bow)
        
        # 마법 무기
        basic_staff = Item("마법사 지팡이", ItemType.WEAPON, ItemRarity.COMMON,
                          "기본적인 마법 지팡이", 40, 1.5)
        basic_staff.stats = {"magic_attack": 15, "max_mp": 10}
        items.append(basic_staff)
        
        crystal_staff = Item("수정 지팡이", ItemType.WEAPON, ItemRarity.UNCOMMON,
                            "마나 수정이 박힌 지팡이", 110, 2.0)
        crystal_staff.stats = {"magic_attack": 20, "max_mp": 20}
        crystal_staff.effects = ["mp_regen_boost"]
        items.append(crystal_staff)
        
        fire_staff = Item("화염 지팡이", ItemType.WEAPON, ItemRarity.RARE,
                         "화염 마법에 특화된 지팡이", 320, 2.5)
        fire_staff.stats = {"magic_attack": 25, "max_mp": 15}
        fire_staff.effects = ["fire_mastery", "fire_resist"]
        items.append(fire_staff)
        
        ice_staff = Item("얼음 지팡이", ItemType.WEAPON, ItemRarity.RARE,
                        "얼음 마법에 특화된 지팡이", 320, 2.5)
        ice_staff.stats = {"magic_attack": 25, "max_mp": 15}
        ice_staff.effects = ["ice_mastery", "ice_resist"]
        items.append(ice_staff)
        
        lightning_staff = Item("번개 지팡이", ItemType.WEAPON, ItemRarity.RARE,
                              "번개 마법에 특화된 지팡이", 320, 2.5)
        lightning_staff.stats = {"magic_attack": 25, "max_mp": 15}
        lightning_staff.effects = ["lightning_mastery", "shock_resist"]
        items.append(lightning_staff)
        
        sage_staff = Item("현자의 지팡이", ItemType.WEAPON, ItemRarity.EPIC,
                         "고대 현자가 사용한 지팡이", 700, 3.0)
        sage_staff.stats = {"magic_attack": 30, "max_mp": 40}
        sage_staff.effects = ["all_magic_boost", "mana_efficiency"]
        items.append(sage_staff)
        
        creation_staff = Item("창조의 지팡이", ItemType.WEAPON, ItemRarity.LEGENDARY,
                             "세상을 창조한 신의 지팡이", 1800, 4.0)
        creation_staff.stats = {"magic_attack": 50, "max_mp": 80}
        creation_staff.effects = ["infinite_mana", "reality_magic"]
        items.append(creation_staff)
        
        # 특수 무기
        twin_blades = Item("쌍검", ItemType.WEAPON, ItemRarity.UNCOMMON,
                          "양손에 들 수 있는 쌍검", 150, 4.0)
        twin_blades.stats = {"physical_attack": 14, "speed": 6}
        twin_blades.effects = ["double_strike"]
        items.append(twin_blades)
        
        chain_sword = Item("체인 소드", ItemType.WEAPON, ItemRarity.RARE,
                          "사슬이 달린 검", 350, 3.5)
        chain_sword.stats = {"physical_attack": 18, "speed": 4}
        chain_sword.effects = ["ranged_melee", "pull_enemy"]
        items.append(chain_sword)
        
        bio_weapon = Item("생체 무기", ItemType.WEAPON, ItemRarity.EPIC,
                         "살아있는 생체 무기", 1000, 5.0)
        bio_weapon.stats = {"physical_attack": 28}
        bio_weapon.effects = ["evolving", "self_repair", "symbiosis"]
        items.append(bio_weapon)
        
        dimension_blade = Item("시공간 칼날", ItemType.WEAPON, ItemRarity.LEGENDARY,
                              "차원을 베는 신비한 칼날", 2000, 2.0)
        dimension_blade.stats = {"physical_attack": 45, "magic_attack": 30}
        dimension_blade.effects = ["ignore_all_defense", "dimension_strike", "time_stop"]
        items.append(dimension_blade)
        
        # === 방어구 (40개) ===
        
        # 갑옷류
        cloth_robe = Item("천 로브", ItemType.ARMOR, ItemRarity.COMMON,
                         "기본적인 천으로 만든 로브", 15, 2.0)
        cloth_robe.stats = {"physical_defense": 3, "magic_defense": 5}
        items.append(cloth_robe)
        
        leather_armor = Item("가죽 갑옷", ItemType.ARMOR, ItemRarity.COMMON,
                           "유연한 가죽으로 만든 갑옷", 40, 5.0)
        leather_armor.stats = {"physical_defense": 8, "speed": 2}
        items.append(leather_armor)
        
        chain_mail = Item("사슬 갑옷", ItemType.ARMOR, ItemRarity.UNCOMMON,
                         "금속 고리를 엮어 만든 갑옷", 100, 8.0)
        chain_mail.stats = {"physical_defense": 15, "magic_defense": 5}
        items.append(chain_mail)
        
        plate_armor = Item("판금 갑옷", ItemType.ARMOR, ItemRarity.UNCOMMON,
                          "두꺼운 강철판으로 만든 갑옷", 200, 15.0)
        plate_armor.stats = {"physical_defense": 25, "physical_defense": 3}
        plate_armor.effects = ["movement_penalty"]
        items.append(plate_armor)
        
        mithril_mail = Item("미스릴 사슬갑옷", ItemType.ARMOR, ItemRarity.RARE,
                           "전설의 금속 미스릴로 만든 갑옷", 500, 6.0)
        mithril_mail.stats = {"physical_defense": 20, "magic_defense": 20, "speed": 5}
        items.append(mithril_mail)
        
        dragon_scale = Item("용비늘 갑옷", ItemType.ARMOR, ItemRarity.RARE,
                           "드래곤의 비늘로 만든 갑옷", 800, 10.0)
        dragon_scale.stats = {"physical_defense": 30, "magic_defense": 25}
        dragon_scale.effects = ["fire_immunity", "intimidation"]
        items.append(dragon_scale)
        
        shadow_cloak = Item("그림자 망토", ItemType.ARMOR, ItemRarity.EPIC,
                           "그림자로 짜여진 신비한 망토", 1000, 1.0)
        shadow_cloak.stats = {"magic_defense": 35, "speed": 15}
        shadow_cloak.effects = ["stealth_boost", "dodge_chance_25"]
        items.append(shadow_cloak)
        
        holy_vestment = Item("성스러운 법의", ItemType.ARMOR, ItemRarity.EPIC,
                            "신의 축복이 깃든 신성한 의복", 1200, 3.0)
        holy_vestment.stats = {"magic_defense": 40, "max_mp": 30}
        holy_vestment.effects = ["curse_immunity", "undead_fear", "blessing_aura"]
        items.append(holy_vestment)
        
        phoenix_armor = Item("불사조 갑옷", ItemType.ARMOR, ItemRarity.LEGENDARY,
                            "불사조의 깃털로 만든 전설의 갑옷", 2500, 4.0)
        phoenix_armor.stats = {"physical_defense": 45, "magic_defense": 45}
        phoenix_armor.effects = ["auto_revive", "fire_immunity", "hp_regen_high"]
        items.append(phoenix_armor)
        
        # 방패류
        wooden_shield = Item("나무 방패", ItemType.ARMOR, ItemRarity.COMMON,
                           "단단한 나무로 만든 방패", 20, 3.0)
        wooden_shield.stats = {"physical_defense": 5}
        wooden_shield.effects = ["block_chance_10"]
        items.append(wooden_shield)
        
        iron_shield = Item("철 방패", ItemType.ARMOR, ItemRarity.UNCOMMON,
                          "견고한 철로 만든 방패", 80, 5.0)
        iron_shield.stats = {"physical_defense": 12}
        iron_shield.effects = ["block_chance_20"]
        items.append(iron_shield)
        
        tower_shield = Item("탑 방패", ItemType.ARMOR, ItemRarity.RARE,
                           "거대한 크기의 방패", 300, 12.0)
        tower_shield.stats = {"physical_defense": 25, "speed": -5}
        tower_shield.effects = ["block_chance_40", "knockback_resist"]
        items.append(tower_shield)
        
        magic_shield = Item("마법 방패", ItemType.ARMOR, ItemRarity.RARE,
                           "마법으로 강화된 방패", 400, 4.0)
        magic_shield.stats = {"physical_defense": 15, "magic_defense": 20}
        magic_shield.effects = ["spell_reflect_30"]
        items.append(magic_shield)
        
        aegis_shield = Item("이지스의 방패", ItemType.ARMOR, ItemRarity.LEGENDARY,
                           "모든 것을 막아내는 신화의 방패", 3000, 8.0)
        aegis_shield.stats = {"physical_defense": 50, "magic_defense": 50}
        aegis_shield.effects = ["perfect_block_chance", "status_immunity", "fear_aura"]
        items.append(aegis_shield)
        
        # 특수 방어구
        ninja_suit = Item("닌자 의상", ItemType.ARMOR, ItemRarity.RARE,
                         "은밀함을 위한 특수 의상", 350, 2.0)
        ninja_suit.stats = {"speed": 10, "physical_defense": 8}
        ninja_suit.effects = ["stealth", "critical_resist", "poison_resist"]
        items.append(ninja_suit)
        
        berserker_armor = Item("광전사 갑옷", ItemType.ARMOR, ItemRarity.EPIC,
                              "광폭한 전사를 위한 갑옷", 800, 12.0)
        berserker_armor.stats = {"physical_defense": 20, "physical_attack": 10}
        berserker_armor.effects = ["rage_mode", "pain_immunity", "fear_immunity"]
        items.append(berserker_armor)
        
        arcane_robe = Item("비전 로브", ItemType.ARMOR, ItemRarity.EPIC,
                          "고대 마법이 깃든 로브", 900, 2.5)
        arcane_robe.stats = {"magic_defense": 35, "magic_attack": 15, "max_mp": 40}
        arcane_robe.effects = ["mana_efficiency", "spell_power_boost", "magic_resist"]
        items.append(arcane_robe)
        
        living_armor = Item("생체 갑옷", ItemType.ARMOR, ItemRarity.LEGENDARY,
                           "살아있는 생명체로 만든 갑옷", 2000, 6.0)
        living_armor.stats = {"physical_defense": 35, "magic_defense": 35}
        living_armor.effects = ["adaptive_defense", "self_repair", "symbiotic_bond"]
        items.append(living_armor)
        
        # === 장신구 (30개) ===
        
        # 반지류
        strength_ring = Item("힘의 반지", ItemType.ACCESSORY, ItemRarity.COMMON,
                           "착용자의 힘을 증가시키는 반지", 50, 0.1)
        strength_ring.stats = {"physical_attack": 3}
        items.append(strength_ring)
        
        magic_ring = Item("마법의 반지", ItemType.ACCESSORY, ItemRarity.COMMON,
                         "마법력을 증가시키는 반지", 50, 0.1)
        magic_ring.stats = {"magic_attack": 3}
        items.append(magic_ring)
        
        speed_ring = Item("민첩의 반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                         "착용자를 빠르게 만드는 반지", 100, 0.1)
        speed_ring.stats = {"speed": 5}
        items.append(speed_ring)
        
        health_ring = Item("생명의 반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                          "최대 체력을 증가시키는 반지", 150, 0.1)
        health_ring.stats = {"max_hp": 20}
        items.append(health_ring)
        
        mana_ring = Item("마나의 반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                        "마나를 증가시키는 반지", 150, 0.1)
        mana_ring.stats = {"max_mp": 15}
        items.append(mana_ring)
        
        regeneration_ring = Item("재생의 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                               "시간이 지나면서 체력을 회복하는 반지", 400, 0.1)
        regeneration_ring.effects = ["hp_regen", "wound_healing_boost"]
        items.append(regeneration_ring)
        
        vampiric_ring = Item("흡혈의 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                           "적에게 준 피해의 일부를 체력으로 흡수", 500, 0.1)
        vampiric_ring.effects = ["life_steal_10"]
        items.append(vampiric_ring)
        
        time_ring = Item("시간의 반지", ItemType.ACCESSORY, ItemRarity.EPIC,
                        "시간을 조작하는 신비한 반지", 1000, 0.1)
        time_ring.effects = ["time_acceleration", "atb_boost"]
        items.append(time_ring)
        
        dragon_ring = Item("용의 반지", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                          "고대 용의 힘이 깃든 반지", 2000, 0.1)
        dragon_ring.stats = {"physical_attack": 15, "magic_attack": 15}
        dragon_ring.effects = ["dragon_breath", "fire_immunity", "intimidation"]
        items.append(dragon_ring)
        
        # 목걸이류
        protection_amulet = Item("보호의 목걸이", ItemType.ACCESSORY, ItemRarity.COMMON,
                               "물리 피해를 감소시키는 목걸이", 60, 0.2)
        protection_amulet.stats = {"physical_defense": 5}
        items.append(protection_amulet)
        
        ward_amulet = Item("마법 보호의 목걸이", ItemType.ACCESSORY, ItemRarity.COMMON,
                          "마법 피해를 감소시키는 목걸이", 60, 0.2)
        ward_amulet.stats = {"magic_defense": 5}
        items.append(ward_amulet)
        
        lucky_pendant = Item("행운의 펜던트", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                           "크리티컬 확률을 증가시키는 펜던트", 200, 0.2)
        lucky_pendant.effects = ["crit_chance_15"]
        items.append(lucky_pendant)
        
        scholars_pendant = Item("학자의 펜던트", ItemType.ACCESSORY, ItemRarity.RARE,
                              "경험치 획득량을 증가시키는 펜던트", 600, 0.2)
        scholars_pendant.effects = ["exp_boost_25", "skill_cooldown_reduce"]
        items.append(scholars_pendant)
        
        phoenix_pendant = Item("불사조의 펜던트", ItemType.ACCESSORY, ItemRarity.EPIC,
                             "죽음에서 부활시켜주는 펜던트", 1500, 0.2)
        phoenix_pendant.effects = ["auto_revive_once", "fire_resist"]
        items.append(phoenix_pendant)
        
        # 귀걸이류
        focus_earring = Item("집중의 귀걸이", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                           "정신력을 집중시켜주는 귀걸이", 120, 0.1)
        focus_earring.stats = {"magic_attack": 5}
        focus_earring.effects = ["mana_efficiency"]
        items.append(focus_earring)
        
        silence_earring = Item("침묵의 귀걸이", ItemType.ACCESSORY, ItemRarity.RARE,
                             "은밀함을 제공하는 귀걸이", 300, 0.1)
        silence_earring.effects = ["stealth_boost", "backstab_damage"]
        items.append(silence_earring)
        
        # 팔찌류
        warrior_bracelet = Item("전사의 팔찌", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                              "전투력을 향상시키는 팔찌", 150, 0.3)
        warrior_bracelet.stats = {"physical_attack": 7, "physical_defense": 3}
        items.append(warrior_bracelet)
        
        mage_bracelet = Item("마법사의 팔찌", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                           "마법력을 강화하는 팔찌", 150, 0.3)
        mage_bracelet.stats = {"magic_attack": 7, "max_mp": 10}
        items.append(mage_bracelet)
        
        thief_bracelet = Item("도적의 팔찌", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                            "민첩성을 극대화하는 팔찌", 150, 0.3)
        thief_bracelet.stats = {"speed": 8}
        thief_bracelet.effects = ["dodge_chance_15"]
        items.append(thief_bracelet)
        
        # 특수 장신구
        soul_gem = Item("영혼석", ItemType.ACCESSORY, ItemRarity.RARE,
                       "영혼의 힘을 담은 신비한 보석", 800, 0.5)
        soul_gem.stats = {"max_hp": 30, "max_mp": 30}
        soul_gem.effects = ["soul_bond", "death_protection"]
        items.append(soul_gem)
        
        chaos_orb = Item("혼돈의 구슬", ItemType.ACCESSORY, ItemRarity.EPIC,
                        "예측불가능한 힘을 지닌 구슬", 1200, 0.3)
        chaos_orb.effects = ["random_effect", "chaos_strike", "reality_warp"]
        items.append(chaos_orb)
        
        infinity_stone = Item("무한석", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                            "무한한 힘을 담은 전설의 보석", 5000, 0.1)
        infinity_stone.stats = {"physical_attack": 20, "magic_attack": 20, "max_hp": 50, "max_mp": 50}
        infinity_stone.effects = ["power_unlimited", "time_control", "space_manipulation"]
        items.append(infinity_stone)
        
        # 기타 특수 장신구
        berserk_totem = Item("광전사 토템", ItemType.ACCESSORY, ItemRarity.RARE,
                           "전투 광기를 불러일으키는 토템", 400, 0.4)
        berserk_totem.effects = ["rage_on_low_hp", "damage_boost_wounded"]
        items.append(berserk_totem)
        
        healing_crystal = Item("치유의 수정", ItemType.ACCESSORY, ItemRarity.RARE,
                             "지속적으로 상처를 치유하는 수정", 500, 0.3)
        healing_crystal.effects = ["constant_healing", "wound_immunity"]
        items.append(healing_crystal)
        
        shadow_cloak_pin = Item("그림자 망토핀", ItemType.ACCESSORY, ItemRarity.EPIC,
                              "그림자 속으로 숨게 해주는 핀", 800, 0.1)
        shadow_cloak_pin.effects = ["invisibility_chance", "shadow_step"]
        items.append(shadow_cloak_pin)
        
        divine_blessing = Item("신의 축복", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                             "신이 내린 축복이 깃든 성유물", 3000, 0.2)
        divine_blessing.stats = {"max_hp": 40, "max_mp": 40}
        divine_blessing.effects = ["divine_protection", "miracle_heal", "curse_immunity"]
        items.append(divine_blessing)
        
        void_fragment = Item("공허의 파편", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                           "무(無)의 힘을 담은 파편", 4000, 0.1)
        void_fragment.effects = ["void_strike", "existence_drain", "reality_tear"]
        items.append(void_fragment)
        
        eternal_hourglass = Item("영원의 모래시계", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                               "시간을 자유자재로 조작하는 모래시계", 6000, 0.3)
        eternal_hourglass.effects = ["time_stop", "time_rewind", "temporal_shield"]
        items.append(eternal_hourglass)
        
        cosmic_eye = Item("우주의 눈", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                         "모든 것을 꿰뚫어보는 우주의 눈", 7000, 0.2)
        cosmic_eye.effects = ["true_sight", "future_vision", "cosmic_knowledge"]
        items.append(cosmic_eye)
        
        # === 소모품 (20개) ===
        
        # 치유 아이템
        small_potion = Item("작은 치유 물약", ItemType.CONSUMABLE, ItemRarity.COMMON,
                          "체력을 조금 회복하는 물약", 20, 0.3)
        small_potion.use_effect = {"heal": 30}
        items.append(small_potion)
        
        health_potion = Item("치유 물약", ItemType.CONSUMABLE, ItemRarity.COMMON,
                           "체력을 회복하는 물약", 50, 0.3)
        health_potion.use_effect = {"heal": 60}
        items.append(health_potion)
        
        great_potion = Item("큰 치유 물약", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "체력을 크게 회복하는 물약", 100, 0.3)
        great_potion.use_effect = {"heal": 120}
        items.append(great_potion)
        
        mana_potion = Item("마나 물약", ItemType.CONSUMABLE, ItemRarity.COMMON,
                         "마나를 회복하는 물약", 40, 0.3)
        mana_potion.use_effect = {"mana": 40}
        items.append(mana_potion)
        
        elixir = Item("엘릭서", ItemType.CONSUMABLE, ItemRarity.RARE,
                     "체력과 마나를 모두 완전 회복하는 신비한 물약", 500, 0.2)
        elixir.use_effect = {"heal": "full", "mana": "full"}
        items.append(elixir)
        
        # 강화 아이템
        strength_elixir = Item("힘의 영약", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                             "일시적으로 공격력을 증가시키는 영약", 80, 0.2)
        strength_elixir.use_effect = {"buff": "strength", "duration": 10}
        items.append(strength_elixir)
        
        speed_elixir = Item("신속의 영약", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "일시적으로 속도를 증가시키는 영약", 80, 0.2)
        speed_elixir.use_effect = {"buff": "speed", "duration": 10}
        items.append(speed_elixir)
        
        defense_elixir = Item("방어의 영약", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                            "일시적으로 방어력을 증가시키는 영약", 80, 0.2)
        defense_elixir.use_effect = {"buff": "defense", "duration": 10}
        items.append(defense_elixir)
        
        # 특수 아이템
        antidote = Item("해독제", ItemType.CONSUMABLE, ItemRarity.COMMON,
                       "독을 중화시키는 약", 30, 0.2)
        antidote.use_effect = {"cure": "poison"}
        items.append(antidote)
        
        holy_water = Item("성수", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                         "언데드에게 큰 피해를 주는 성스러운 물", 60, 0.3)
        holy_water.use_effect = {"damage_undead": 100, "blessing": 5}
        items.append(holy_water)
        
        smoke_bomb = Item("연막탄", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                         "연막을 생성하여 도망칠 기회를 만드는 폭탄", 40, 0.2)
        smoke_bomb.use_effect = {"escape": True, "blind_enemies": 3}
        items.append(smoke_bomb)
        
        fire_bomb = Item("화염탄", ItemType.CONSUMABLE, ItemRarity.RARE,
                        "강력한 화염 폭발을 일으키는 폭탄", 120, 0.3)
        fire_bomb.use_effect = {"area_damage": 80, "burn": 3}
        items.append(fire_bomb)
        
        # 영구 강화 아이템
        stat_book_str = Item("힘의 비전서", ItemType.CONSUMABLE, ItemRarity.RARE,
                           "영구적으로 힘을 증가시키는 고대 비전서", 1000, 1.0)
        stat_book_str.use_effect = {"permanent_stat": "physical_attack", "value": 5}
        items.append(stat_book_str)
        
        stat_book_mag = Item("마법의 비전서", ItemType.CONSUMABLE, ItemRarity.RARE,
                           "영구적으로 마법력을 증가시키는 고대 비전서", 1000, 1.0)
        stat_book_mag.use_effect = {"permanent_stat": "magic_attack", "value": 5}
        items.append(stat_book_mag)
        
        stat_book_hp = Item("생명의 비전서", ItemType.CONSUMABLE, ItemRarity.RARE,
                          "영구적으로 최대 체력을 증가시키는 고대 비전서", 1200, 1.0)
        stat_book_hp.use_effect = {"permanent_stat": "max_hp", "value": 20}
        items.append(stat_book_hp)
        
        # 전설급 소모품
        phoenix_feather = Item("불사조의 깃털", ItemType.CONSUMABLE, ItemRarity.LEGENDARY,
                             "죽은 자를 되살리는 전설의 깃털", 5000, 0.1)
        phoenix_feather.use_effect = {"revive": True, "heal": "full"}
        items.append(phoenix_feather)
        
        time_crystal = Item("시간 수정", ItemType.CONSUMABLE, ItemRarity.LEGENDARY,
                          "시간을 되돌려 최근 행동을 취소하는 수정", 3000, 0.2)
        time_crystal.use_effect = {"time_rewind": True}
        items.append(time_crystal)
        
        dragon_heart = Item("용의 심장", ItemType.CONSUMABLE, ItemRarity.LEGENDARY,
                          "용의 힘을 일시적으로 부여하는 심장", 8000, 0.5)
        dragon_heart.use_effect = {"dragon_form": 20, "all_stats": 50}
        items.append(dragon_heart)
        
        god_tear = Item("신의 눈물", ItemType.CONSUMABLE, ItemRarity.LEGENDARY,
                       "모든 저주와 상태이상을 정화하고 완전히 치유하는 신의 눈물", 10000, 0.1)
        god_tear.use_effect = {"heal": "full", "mana": "full", "cure_all": True, "blessing": 30}
        items.append(god_tear)
        
        reality_fragment = Item("현실 파편", ItemType.CONSUMABLE, ItemRarity.LEGENDARY,
                              "현실을 조작하여 원하는 결과를 얻는 파편", 15000, 0.1)
        reality_fragment.use_effect = {"reality_alter": True, "any_effect": True}
        items.append(reality_fragment)
        iron_sword.stats = {"physical_attack": 5}
        iron_sword.value = 100
        items.append(iron_sword)
        
        steel_sword = Item("강철검", ItemType.WEAPON, ItemRarity.UNCOMMON,
                          "강화된 강철로 만든 검")
        steel_sword.stats = {"physical_attack": 8, "speed": 1}
        steel_sword.value = 200
        items.append(steel_sword)
        
        mithril_sword = Item("미스릴 검", ItemType.WEAPON, ItemRarity.RARE,
                            "전설의 금속 미스릴로 만든 검")
        mithril_sword.stats = {"physical_attack": 12, "speed": 2}
        mithril_sword.value = 500
        items.append(mithril_sword)
        
        flame_sword = Item("화염검", ItemType.WEAPON, ItemRarity.EPIC,
                          "불의 정령이 깃든 검")
        flame_sword.stats = {"physical_attack": 15, "magic_attack": 5}
        flame_sword.effects = ["fire_damage"]
        flame_sword.value = 800
        items.append(flame_sword)
        
        # 지팡이류
        magic_staff = Item("마법 지팡이", ItemType.WEAPON, ItemRarity.COMMON,
                          "마법력을 증폭시키는 지팡이")
        magic_staff.stats = {"magic_attack": 6}
        magic_staff.value = 120
        items.append(magic_staff)
        
        crystal_staff = Item("수정 지팡이", ItemType.WEAPON, ItemRarity.UNCOMMON,
                            "수정으로 장식된 고급 지팡이")
        crystal_staff.stats = {"magic_attack": 10, "magic_defense": 2}
        crystal_staff.value = 250
        items.append(crystal_staff)
        
        archmage_staff = Item("대마법사의 지팡이", ItemType.WEAPON, ItemRarity.RARE,
                             "전설적인 마법사가 사용했던 지팡이")
        archmage_staff.stats = {"magic_attack": 15, "magic_defense": 4}
        archmage_staff.effects = ["mana_boost"]
        archmage_staff.value = 600
        items.append(archmage_staff)
        
        # 활류
        wooden_bow = Item("나무 활", ItemType.WEAPON, ItemRarity.COMMON,
                         "단순한 나무로 만든 활")
        wooden_bow.stats = {"physical_attack": 4, "speed": 2}
        wooden_bow.value = 80
        items.append(wooden_bow)
        
        composite_bow = Item("복합 활", ItemType.WEAPON, ItemRarity.UNCOMMON,
                            "여러 재료를 조합한 강력한 활")
        composite_bow.stats = {"physical_attack": 7, "speed": 3}
        composite_bow.value = 180
        items.append(composite_bow)
        
        elven_bow = Item("엘프의 활", ItemType.WEAPON, ItemRarity.RARE,
                        "엘프 장인이 만든 정교한 활")
        elven_bow.stats = {"physical_attack": 11, "speed": 4}
        elven_bow.effects = ["precision"]
        elven_bow.value = 450
        items.append(elven_bow)
        
        # === 방어구 ===
        leather_armor = Item("가죽 갑옷", ItemType.ARMOR, ItemRarity.COMMON,
                            "간단한 가죽으로 만든 방어구")
        leather_armor.stats = {"physical_defense": 3, "magic_defense": 1}
        leather_armor.value = 60
        items.append(leather_armor)
        
        chain_mail = Item("사슬 갑옷", ItemType.ARMOR, ItemRarity.UNCOMMON,
                         "철 고리로 엮은 견고한 갑옷")
        chain_mail.stats = {"physical_defense": 6, "magic_defense": 2}
        chain_mail.value = 150
        items.append(chain_mail)
        
        plate_armor = Item("판금 갑옷", ItemType.ARMOR, ItemRarity.RARE,
                          "두꺼운 철판으로 만든 중갑")
        plate_armor.stats = {"physical_defense": 10, "magic_defense": 3, "speed": -1}
        plate_armor.value = 400
        items.append(plate_armor)
        
        mage_robe = Item("마법사 로브", ItemType.ARMOR, ItemRarity.UNCOMMON,
                        "마법 저항력이 높은 로브")
        mage_robe.stats = {"physical_defense": 2, "magic_defense": 8}
        mage_robe.value = 180
        items.append(mage_robe)
        
        dragon_scale = Item("용린 갑옷", ItemType.ARMOR, ItemRarity.EPIC,
                           "고대 용의 비늘로 만든 갑옷")
        dragon_scale.stats = {"physical_defense": 12, "magic_defense": 12}
        dragon_scale.effects = ["fire_resist"]
        dragon_scale.value = 1000
        items.append(dragon_scale)
        
        # === 장신구 ===
        power_ring = Item("힘의 반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                         "착용자의 힘을 증가시키는 반지")
        power_ring.stats = {"physical_attack": 3}
        power_ring.value = 120
        items.append(power_ring)
        
        defense_amulet = Item("수호 목걸이", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                             "착용자를 보호하는 목걸이")
        defense_amulet.stats = {"physical_defense": 2, "magic_defense": 2}
        defense_amulet.value = 140
        items.append(defense_amulet)
        
        speed_boots = Item("신속의 장화", ItemType.ACCESSORY, ItemRarity.RARE,
                          "착용자의 속도를 크게 증가시킨다")
        speed_boots.stats = {"speed": 5}
        speed_boots.value = 300
        items.append(speed_boots)
        
        health_pendant = Item("생명력 펜던트", ItemType.ACCESSORY, ItemRarity.RARE,
                             "착용자의 최대 HP를 증가시킨다")
        health_pendant.stats = {"max_hp": 30}
        health_pendant.value = 250
        items.append(health_pendant)
        
        hero_badge = Item("영웅의 휘장", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                         "전설적인 영웅만이 가질 수 있는 휘장")
        hero_badge.stats = {"physical_attack": 5, "magic_attack": 5, "speed": 3}
        hero_badge.effects = ["legendary_power"]
        hero_badge.value = 2000
        items.append(hero_badge)
        
        # === 재료 ===
        iron_ore = Item("철광석", ItemType.MATERIAL, ItemRarity.COMMON,
                       "무기 제작에 사용되는 기본 재료")
        iron_ore.value = 10
        items.append(iron_ore)
        
        magic_crystal = Item("마법 수정", ItemType.MATERIAL, ItemRarity.UNCOMMON,
                            "마법 아이템 제작에 필요한 수정")
        magic_crystal.value = 25
        items.append(magic_crystal)
        
        # === 추가 소모품 (40개) ===
        # 회복 아이템
        elixir = Item("엘릭서", ItemType.CONSUMABLE, ItemRarity.RARE,
                     "모든 상태이상을 치료하고 HP/MP 완전 회복")
        elixir.stats = {"heal_amount": 9999, "mp_amount": 9999}
        elixir.effects = ["full_heal", "cure_all"]
        elixir.value = 500
        items.append(elixir)
        
        phoenix_down = Item("불사조의 깃털", ItemType.CONSUMABLE, ItemRarity.EPIC,
                           "전투불능 상태를 완전히 회복시킨다")
        phoenix_down.effects = ["full_revive"]
        phoenix_down.value = 1000
        items.append(phoenix_down)
        
        mega_potion = Item("메가 포션", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "HP를 150 회복한다")
        mega_potion.stats = {"heal_amount": 150}
        mega_potion.effects = ["heal"]
        mega_potion.value = 75
        items.append(mega_potion)
        
        x_potion = Item("X-포션", ItemType.CONSUMABLE, ItemRarity.RARE,
                       "HP를 완전히 회복한다")
        x_potion.stats = {"heal_amount": 9999}
        x_potion.effects = ["heal"]
        x_potion.value = 200
        items.append(x_potion)
        
        ether = Item("에테르", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                    "MP를 30 회복한다")
        ether.stats = {"mp_amount": 30}
        ether.effects = ["mp_restore"]
        ether.value = 50
        items.append(ether)
        
        turbo_ether = Item("터보 에테르", ItemType.CONSUMABLE, ItemRarity.RARE,
                          "MP를 완전히 회복한다")
        turbo_ether.stats = {"mp_amount": 9999}
        turbo_ether.effects = ["mp_restore"]
        turbo_ether.value = 150
        items.append(turbo_ether)
        
        # 상태 효과 아이템
        power_drink = Item("파워 드링크", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "일시적으로 공격력을 크게 증가시킨다")
        power_drink.stats = {"attack_boost": 20, "duration": 5}
        power_drink.effects = ["power_boost"]
        power_drink.value = 80
        items.append(power_drink)
        
        guard_drink = Item("가드 드링크", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "일시적으로 방어력을 크게 증가시킨다")
        guard_drink.stats = {"defense_boost": 20, "duration": 5}
        guard_drink.effects = ["guard_boost"]
        guard_drink.value = 80
        items.append(guard_drink)
        
        speed_drink = Item("스피드 드링크", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "일시적으로 속도를 크게 증가시킨다")
        speed_drink.stats = {"speed_boost": 10, "duration": 5}
        speed_drink.effects = ["speed_boost"]
        speed_drink.value = 80
        items.append(speed_drink)
        
        mind_drink = Item("마인드 드링크", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                         "일시적으로 마법력을 크게 증가시킨다")
        mind_drink.stats = {"magic_boost": 20, "duration": 5}
        mind_drink.effects = ["mind_boost"]
        mind_drink.value = 80
        items.append(mind_drink)
        
        # 공격 아이템
        fire_bomb = Item("화염탄", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                        "적에게 화염 데미지를 준다")
        fire_bomb.stats = {"damage_amount": 100, "element": "fire"}
        fire_bomb.effects = ["fire_damage"]
        fire_bomb.value = 60
        items.append(fire_bomb)
        
        ice_bomb = Item("얼음탄", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                       "적에게 얼음 데미지를 주고 동결시킨다")
        ice_bomb.stats = {"damage_amount": 80, "element": "ice"}
        ice_bomb.effects = ["ice_damage", "freeze"]
        ice_bomb.value = 70
        items.append(ice_bomb)
        
        thunder_bomb = Item("번개탄", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                           "적에게 번개 데미지를 주고 마비시킨다")
        thunder_bomb.stats = {"damage_amount": 90, "element": "thunder"}
        thunder_bomb.effects = ["thunder_damage", "paralyze"]
        thunder_bomb.value = 75
        items.append(thunder_bomb)
        
        gravity_bomb = Item("중력탄", ItemType.CONSUMABLE, ItemRarity.RARE,
                           "모든 적에게 현재 HP의 25% 데미지")
        gravity_bomb.stats = {"damage_percent": 25}
        gravity_bomb.effects = ["gravity_damage"]
        gravity_bomb.value = 120
        items.append(gravity_bomb)
        
        # 특수 아이템
        tent = Item("텐트", ItemType.CONSUMABLE, ItemRarity.COMMON,
                   "필드에서 휴식을 취해 HP/MP를 회복한다")
        tent.stats = {"heal_amount": 50, "mp_amount": 20}
        tent.effects = ["field_rest"]
        tent.value = 100
        items.append(tent)
        
        cottage = Item("별장", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                      "필드에서 완전한 휴식을 취한다")
        cottage.stats = {"heal_amount": 9999, "mp_amount": 9999}
        cottage.effects = ["full_rest", "cure_all"]
        cottage.value = 300
        items.append(cottage)
        
        alarm_clock = Item("알람시계", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                          "수면 상태를 치료한다")
        alarm_clock.effects = ["cure_sleep"]
        alarm_clock.value = 30
        items.append(alarm_clock)
        
        eye_drops = Item("안약", ItemType.CONSUMABLE, ItemRarity.COMMON,
                        "실명 상태를 치료한다")
        eye_drops.effects = ["cure_blind"]
        eye_drops.value = 25
        items.append(eye_drops)
        
        echo_herbs = Item("메아리풀", ItemType.CONSUMABLE, ItemRarity.COMMON,
                         "침묵 상태를 치료한다")
        echo_herbs.effects = ["cure_silence"]
        echo_herbs.value = 30
        items.append(echo_herbs)
        
        soft_potion = Item("연화제", ItemType.CONSUMABLE, ItemRarity.COMMON,
                          "석화 상태를 치료한다")
        soft_potion.effects = ["cure_stone"]
        soft_potion.value = 50
        items.append(soft_potion)
        
        # 전략 아이템
        smoke_screen = Item("연막", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                           "모든 적의 명중률을 감소시킨다")
        smoke_screen.stats = {"accuracy_debuff": 30, "duration": 3}
        smoke_screen.effects = ["smoke_screen"]
        smoke_screen.value = 60
        items.append(smoke_screen)
        
        flash_powder = Item("섬광가루", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                           "모든 적을 실명 상태로 만든다")
        flash_powder.effects = ["mass_blind"]
        flash_powder.value = 80
        items.append(flash_powder)
        
        sleep_powder = Item("수면가루", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                           "모든 적을 수면 상태로 만든다")
        sleep_powder.effects = ["mass_sleep"]
        sleep_powder.value = 90
        items.append(sleep_powder)
        
        silence_powder = Item("침묵가루", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                             "모든 적을 침묵 상태로 만든다")
        silence_powder.effects = ["mass_silence"]
        silence_powder.value = 85
        items.append(silence_powder)
        
        # 희귀 특수 아이템
        time_crystal = Item("시간 수정", ItemType.CONSUMABLE, ItemRarity.EPIC,
                           "시간을 조작하여 한 턴 더 행동할 수 있다")
        time_crystal.effects = ["extra_turn"]
        time_crystal.value = 500
        items.append(time_crystal)
        
        warp_stone = Item("워프 스톤", ItemType.CONSUMABLE, ItemRarity.RARE,
                         "즉시 던전에서 탈출한다")
        warp_stone.effects = ["emergency_escape"]
        warp_stone.value = 200
        items.append(warp_stone)
        
        luck_coin = Item("행운의 동전", ItemType.CONSUMABLE, ItemRarity.RARE,
                        "일시적으로 운을 크게 증가시킨다")
        luck_coin.stats = {"luck_boost": 50, "duration": 10}
        luck_coin.effects = ["luck_boost"]
        luck_coin.value = 300
        items.append(luck_coin)
        
        exp_orb = Item("경험치 구슬", ItemType.CONSUMABLE, ItemRarity.RARE,
                      "사용하면 즉시 경험치를 획득한다")
        exp_orb.stats = {"exp_amount": 1000}
        exp_orb.effects = ["exp_boost"]
        exp_orb.value = 400
        items.append(exp_orb)
        
        # 음식 아이템
        bread = Item("빵", ItemType.CONSUMABLE, ItemRarity.COMMON,
                    "HP를 약간 회복한다")
        bread.stats = {"heal_amount": 20}
        bread.effects = ["heal"]
        bread.value = 5
        items.append(bread)
        
        cheese = Item("치즈", ItemType.CONSUMABLE, ItemRarity.COMMON,
                     "MP를 약간 회복한다")
        cheese.stats = {"mp_amount": 10}
        cheese.effects = ["mp_restore"]
        cheese.value = 8
        items.append(cheese)
        
        apple = Item("사과", ItemType.CONSUMABLE, ItemRarity.COMMON,
                    "HP를 조금 회복하고 독을 치료한다")
        apple.stats = {"heal_amount": 15}
        apple.effects = ["heal", "cure_poison"]
        apple.value = 12
        items.append(apple)
        
        wine = Item("포도주", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                   "일시적으로 용기를 증가시킨다")
        wine.stats = {"brave_boost": 200, "duration": 3}
        wine.effects = ["brave_boost"]
        wine.value = 50
        items.append(wine)
        
        dragon_steak = Item("드래곤 스테이크", ItemType.CONSUMABLE, ItemRarity.EPIC,
                           "최고급 요리로 모든 능력치를 일시 증가")
        dragon_steak.stats = {"all_stats_boost": 15, "duration": 10}
        dragon_steak.effects = ["all_boost"]
        dragon_steak.value = 800
        items.append(dragon_steak)
        
        # === 추가 무기 (50개) ===
        # 검류 확장
        bronze_sword = Item("청동검", ItemType.WEAPON, ItemRarity.COMMON,
                           "청동으로 만든 기본적인 검", 25, 2.5)
        bronze_sword.stats = {"physical_attack": 6}
        items.append(bronze_sword)
        
        silver_sword = Item("은검", ItemType.WEAPON, ItemRarity.UNCOMMON,
                           "은으로 만든 아름다운 검", 80, 2.0)
        silver_sword.stats = {"physical_attack": 12}
        silver_sword.effects = ["undead_slayer"]
        items.append(silver_sword)
        
        gold_sword = Item("황금검", ItemType.WEAPON, ItemRarity.RARE,
                         "황금으로 만든 화려한 검", 300, 1.8)
        gold_sword.stats = {"physical_attack": 18, "luck": 5}
        items.append(gold_sword)
        
        crystal_sword = Item("수정검", ItemType.WEAPON, ItemRarity.EPIC,
                            "마법 수정으로 만든 투명한 검", 800, 1.5)
        crystal_sword.stats = {"physical_attack": 25, "magic_attack": 15}
        crystal_sword.effects = ["magic_enhance"]
        items.append(crystal_sword)
        
        demon_blade = Item("마검", ItemType.WEAPON, ItemRarity.LEGENDARY,
                          "악마의 힘이 깃든 저주받은 검", 1200, 3.0)
        demon_blade.stats = {"physical_attack": 35, "magic_attack": 20}
        demon_blade.effects = ["life_steal_20", "curse_weapon"]
        items.append(demon_blade)
        
        # 도끼류
        hand_axe = Item("손도끼", ItemType.WEAPON, ItemRarity.COMMON,
                       "한 손으로 사용하는 작은 도끼", 30, 2.0)
        hand_axe.stats = {"physical_attack": 8}
        items.append(hand_axe)
        
        battle_axe = Item("전투도끼", ItemType.WEAPON, ItemRarity.UNCOMMON,
                         "전장에서 사용하는 큰 도끼", 120, 5.0)
        battle_axe.stats = {"physical_attack": 16, "crit_chance": 10}
        items.append(battle_axe)
        
        berserker_axe = Item("광전사의 도끼", ItemType.WEAPON, ItemRarity.RARE,
                            "광전사가 사용하던 피에 젖은 도끼", 400, 6.0)
        berserker_axe.stats = {"physical_attack": 22}
        berserker_axe.effects = ["rage_boost", "hp_sacrifice"]
        items.append(berserker_axe)
        
        # 창류 - 시야 증가 효과
        spear = Item("창", ItemType.WEAPON, ItemRarity.COMMON,
                    "기본적인 장창, 넓은 시야 확보", 35, 3.0)
        spear.stats = {"physical_attack": 7, "vision_range": 1}
        items.append(spear)
        
        halberd = Item("할버드", ItemType.WEAPON, ItemRarity.UNCOMMON,
                      "창과 도끼가 결합된 무기, 전장 감시용", 150, 4.5)
        halberd.stats = {"physical_attack": 17, "vision_range": 1}
        halberd.effects = ["armor_pierce"]
        items.append(halberd)
        
        lance = Item("랜스", ItemType.WEAPON, ItemRarity.RARE,
                    "기사의 기마용 창, 매우 넓은 시야", 350, 4.0)
        lance.stats = {"physical_attack": 20, "vision_range": 2}
        lance.effects = ["charge_attack"]
        items.append(lance)
        
        # 둔기류
        club = Item("곤봉", ItemType.WEAPON, ItemRarity.COMMON,
                   "원시적인 나무 곤봉", 15, 3.0)
        club.stats = {"physical_attack": 5}
        items.append(club)
        
        mace = Item("메이스", ItemType.WEAPON, ItemRarity.UNCOMMON,
                   "철로 만든 타격무기", 100, 4.0)
        mace.stats = {"physical_attack": 14}
        mace.effects = ["armor_break"]
        items.append(mace)
        
        morning_star = Item("모닝스타", ItemType.WEAPON, ItemRarity.RARE,
                           "가시가 달린 철구", 280, 4.5)
        morning_star.stats = {"physical_attack": 19}
        morning_star.effects = ["bleed_chance"]
        items.append(morning_star)
        
        # 활류 확장
        hunting_bow = Item("사냥활", ItemType.WEAPON, ItemRarity.COMMON,
                          "사냥용 기본 활", 40, 1.5)
        hunting_bow.stats = {"physical_attack": 6, "speed": 2}
        items.append(hunting_bow)
        
        elven_bow = Item("엘프의 활", ItemType.WEAPON, ItemRarity.RARE,
                        "엘프가 만든 정교한 활", 400, 1.0)
        elven_bow.stats = {"physical_attack": 20, "speed": 8, "accuracy": 15}
        items.append(elven_bow)
        
        composite_bow = Item("복합활", ItemType.WEAPON, ItemRarity.UNCOMMON,
                            "여러 재료로 만든 강력한 활", 180, 2.0)
        composite_bow.stats = {"physical_attack": 15, "speed": 4}
        items.append(composite_bow)
        
        # 지팡이류 확장
        wooden_staff = Item("나무 지팡이", ItemType.WEAPON, ItemRarity.COMMON,
                           "기본적인 나무 지팡이", 20, 1.0)
        wooden_staff.stats = {"magic_attack": 5, "max_mp": 10}
        items.append(wooden_staff)
        
        iron_staff = Item("철 지팡이", ItemType.WEAPON, ItemRarity.UNCOMMON,
                         "철로 만든 튼튼한 지팡이", 90, 2.0)
        iron_staff.stats = {"magic_attack": 12, "physical_defense": 5}
        items.append(iron_staff)
        
        enchanted_staff = Item("마법 지팡이", ItemType.WEAPON, ItemRarity.RARE,
                              "마법이 깃든 신비한 지팡이", 350, 1.5)
        enchanted_staff.stats = {"magic_attack": 20, "max_mp": 30}
        enchanted_staff.effects = ["spell_power"]
        items.append(enchanted_staff)
        
        # 특수 무기
        whip = Item("채찍", ItemType.WEAPON, ItemRarity.UNCOMMON,
                   "가죽으로 만든 긴 채찍, 넓은 시야 확보", 120, 1.5)
        whip.stats = {"physical_attack": 10, "speed": 6, "vision_range": 2}
        whip.effects = ["disarm_chance"]
        items.append(whip)
        
        flail = Item("플레일", ItemType.WEAPON, ItemRarity.RARE,
                    "사슬로 연결된 특수무기", 300, 3.5)
        flail.stats = {"physical_attack": 18}
        flail.effects = ["ignore_shield", "stun_chance"]
        items.append(flail)
        
        scythe = Item("낫", ItemType.WEAPON, ItemRarity.EPIC,
                     "죽음의 신이 사용하는 낫", 900, 3.0)
        scythe.stats = {"physical_attack": 28}
        scythe.effects = ["death_chance", "soul_harvest"]
        items.append(scythe)
        
        # 쌍수 무기
        dual_daggers = Item("쌍단검", ItemType.WEAPON, ItemRarity.UNCOMMON,
                           "양손에 든 두 개의 단검", 140, 2.0)
        dual_daggers.stats = {"physical_attack": 12, "speed": 8}
        dual_daggers.effects = ["dual_strike"]
        items.append(dual_daggers)
        
        twin_swords = Item("쌍검", ItemType.WEAPON, ItemRarity.RARE,
                          "완벽하게 균형잡힌 한 쌍의 검", 500, 3.0)
        twin_swords.stats = {"physical_attack": 16, "speed": 6}
        twin_swords.effects = ["twin_strike", "combo_master"]
        items.append(twin_swords)
        
        # === 추가 방어구 (60개) ===
        # 경갑 시리즈
        studded_leather = Item("징박힌 가죽갑옷", ItemType.ARMOR, ItemRarity.UNCOMMON,
                              "금속 징이 박힌 강화 가죽갑옷", 80, 6.0)
        studded_leather.stats = {"physical_defense": 12, "speed": 1}
        items.append(studded_leather)
        
        reinforced_leather = Item("강화 가죽갑옷", ItemType.ARMOR, ItemRarity.RARE,
                                 "마법으로 강화된 특수 가죽갑옷", 250, 5.0)
        reinforced_leather.stats = {"physical_defense": 18, "magic_defense": 10, "speed": 3}
        items.append(reinforced_leather)
        
        dragon_leather = Item("드래곤 가죽갑옷", ItemType.ARMOR, ItemRarity.EPIC,
                             "드래곤 가죽으로 만든 최고급 경갑", 800, 4.0)
        dragon_leather.stats = {"physical_defense": 25, "magic_defense": 20, "speed": 5}
        dragon_leather.effects = ["fire_resist_50", "intimidation"]
        items.append(dragon_leather)
        
        # 중갑 시리즈
        scale_mail = Item("비늘갑옷", ItemType.ARMOR, ItemRarity.UNCOMMON,
                         "금속 비늘을 엮어 만든 갑옷", 120, 10.0)
        scale_mail.stats = {"physical_defense": 16, "magic_defense": 8}
        items.append(scale_mail)
        
        splint_mail = Item("판금사슬갑옷", ItemType.ARMOR, ItemRarity.RARE,
                          "사슬에 금속판을 덧댄 갑옷", 300, 12.0)
        splint_mail.stats = {"physical_defense": 22, "magic_defense": 6}
        splint_mail.effects = ["arrow_resist"]
        items.append(splint_mail)
        
        full_plate = Item("풀 플레이트", ItemType.ARMOR, ItemRarity.EPIC,
                         "전신을 보호하는 최고급 판금갑옷", 1000, 20.0)
        full_plate.stats = {"physical_defense": 35, "max_hp": 20}
        full_plate.effects = ["damage_reduction_20", "movement_penalty"]
        items.append(full_plate)
        
        # 로브 시리즈
        apprentice_robe = Item("견습생 로브", ItemType.ARMOR, ItemRarity.COMMON,
                              "마법 견습생이 입는 기본 로브", 25, 1.0)
        apprentice_robe.stats = {"magic_defense": 8, "max_mp": 10}
        items.append(apprentice_robe)
        
        mage_robe = Item("마법사 로브", ItemType.ARMOR, ItemRarity.UNCOMMON,
                        "정식 마법사의 로브", 100, 1.5)
        mage_robe.stats = {"magic_defense": 15, "max_mp": 25, "magic_attack": 5}
        items.append(mage_robe)
        
        wizard_robe = Item("위저드 로브", ItemType.ARMOR, ItemRarity.RARE,
                          "고위 마법사의 화려한 로브", 400, 2.0)
        wizard_robe.stats = {"magic_defense": 25, "max_mp": 40, "magic_attack": 10}
        wizard_robe.effects = ["spell_cost_reduction"]
        items.append(wizard_robe)
        
        archmage_robe = Item("대마법사 로브", ItemType.ARMOR, ItemRarity.EPIC,
                            "대마법사만이 입을 수 있는 전설의 로브", 1200, 2.5)
        archmage_robe.stats = {"magic_defense": 40, "max_mp": 60, "magic_attack": 20}
        archmage_robe.effects = ["spell_power_boost", "mana_regen"]
        items.append(archmage_robe)
        
        # 특수 갑옷
        ninja_suit = Item("닌자복", ItemType.ARMOR, ItemRarity.RARE,
                         "은밀함을 위한 검은 복장", 350, 2.0)
        ninja_suit.stats = {"physical_defense": 15, "speed": 10}
        ninja_suit.effects = ["stealth", "critical_boost"]
        items.append(ninja_suit)
        
        monk_robe = Item("수도승 의복", ItemType.ARMOR, ItemRarity.UNCOMMON,
                        "수도승이 입는 간소한 의복", 80, 1.5)
        monk_robe.stats = {"physical_defense": 10, "magic_defense": 15}
        monk_robe.effects = ["inner_peace", "meditation"]
        items.append(monk_robe)
        
        paladin_armor = Item("성기사 갑옷", ItemType.ARMOR, ItemRarity.EPIC,
                           "신의 축복이 깃든 성스러운 갑옷", 900, 15.0)
        paladin_armor.stats = {"physical_defense": 28, "magic_defense": 25}
        paladin_armor.effects = ["holy_blessing", "undead_protection"]
        items.append(paladin_armor)
        
        # 헬멧
        leather_cap = Item("가죽 모자", ItemType.ARMOR, ItemRarity.COMMON,
                          "기본적인 가죽 모자", 15, 0.5)
        leather_cap.stats = {"physical_defense": 3}
        items.append(leather_cap)
        
        iron_helmet = Item("철 투구", ItemType.ARMOR, ItemRarity.UNCOMMON,
                          "철로 만든 튼튼한 투구", 60, 2.0)
        iron_helmet.stats = {"physical_defense": 8}
        items.append(iron_helmet)
        
        great_helm = Item("그레이트 헬름", ItemType.ARMOR, ItemRarity.RARE,
                         "전신을 덮는 대형 투구", 200, 4.0)
        great_helm.stats = {"physical_defense": 15}
        great_helm.effects = ["headshot_immunity"]
        items.append(great_helm)
        
        crown_helm = Item("왕관 투구", ItemType.ARMOR, ItemRarity.LEGENDARY,
                         "왕의 위엄이 담긴 황금 투구", 2000, 3.0)
        crown_helm.stats = {"physical_defense": 20, "magic_defense": 20, "charisma": 10}
        crown_helm.effects = ["royal_presence", "fear_immunity"]
        items.append(crown_helm)
        
        # 부츠
        leather_boots = Item("가죽 부츠", ItemType.ARMOR, ItemRarity.COMMON,
                           "기본적인 가죽 부츠", 20, 1.0)
        leather_boots.stats = {"physical_defense": 2, "speed": 1}
        items.append(leather_boots)
        
        iron_boots = Item("철 부츠", ItemType.ARMOR, ItemRarity.UNCOMMON,
                         "철로 만든 무거운 부츠", 80, 3.0)
        iron_boots.stats = {"physical_defense": 6}
        iron_boots.effects = ["knockdown_resist"]
        items.append(iron_boots)
        
        winged_boots = Item("날개 부츠", ItemType.ARMOR, ItemRarity.EPIC,
                           "하늘을 날 수 있는 마법의 부츠", 1500, 0.5)
        winged_boots.stats = {"speed": 15}
        winged_boots.effects = ["flight", "fall_immunity"]
        items.append(winged_boots)
        
        # 장갑
        leather_gloves = Item("가죽 장갑", ItemType.ARMOR, ItemRarity.COMMON,
                             "기본적인 가죽 장갑", 10, 0.2)
        leather_gloves.stats = {"physical_defense": 1, "dexterity": 1}
        items.append(leather_gloves)
        
        gauntlets = Item("건틀릿", ItemType.ARMOR, ItemRarity.UNCOMMON,
                        "철로 만든 전투용 장갑", 70, 1.5)
        gauntlets.stats = {"physical_defense": 5, "physical_attack": 2}
        items.append(gauntlets)
        
        power_gloves = Item("파워 글러브", ItemType.ARMOR, ItemRarity.RARE,
                           "힘을 증폭시키는 마법 장갑", 300, 1.0)
        power_gloves.stats = {"physical_attack": 8, "grip_strength": 5}
        power_gloves.effects = ["strength_boost"]
        items.append(power_gloves)
        
        # === 추가 장신구 (80개) ===
        # 반지류
        brass_ring = Item("황동 반지", ItemType.ACCESSORY, ItemRarity.COMMON,
                         "값싼 황동으로 만든 반지")
        brass_ring.stats = {"charisma": 1}
        brass_ring.value = 5
        items.append(brass_ring)
        
        silver_ring = Item("은반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                          "은으로 만든 아름다운 반지")
        silver_ring.stats = {"magic_defense": 3, "luck": 2}
        silver_ring.value = 50
        items.append(silver_ring)
        
        gold_ring = Item("금반지", ItemType.ACCESSORY, ItemRarity.RARE,
                        "순금으로 만든 화려한 반지")
        gold_ring.stats = {"charisma": 5, "luck": 5}
        gold_ring.value = 200
        items.append(gold_ring)
        
        platinum_ring = Item("플래티넘 반지", ItemType.ACCESSORY, ItemRarity.EPIC,
                            "최고급 플래티넘 반지")
        platinum_ring.stats = {"all_stats": 3}
        platinum_ring.value = 800
        items.append(platinum_ring)
        
        # === 내구도 시스템이 적용된 강력한 장비들 (mega_equipment에서 이전) ===
        
        # 🗡️ 특수 검류 - 내구도 시스템과 특수 효과 완전 연동
        flame_sword = Item("화염의 검", ItemType.WEAPON, ItemRarity.RARE,
                          "불꽃이 깃든 마법검", 500, 2.5, 10, 120,
                          [ItemEffect("화염 부여", "공격 시 15% 확률로 화상", "burn_chance", 0.15),
                           ItemEffect("열정", "HP 50% 이하시 공격력 +30%", "passion", 1.3)],
                          ElementalAffinity.FIRE)
        flame_sword.stats = {"physical_attack": 25, "magic_attack": 10}
        items.append(flame_sword)
        
        frost_blade = Item("빙결의 검", ItemType.WEAPON, ItemRarity.RARE,
                          "차가운 기운이 도는 얼음 검", 480, 2.3, 10, 120,
                          [ItemEffect("한기", "공격 시 20% 확률로 속도 감소", "chill_strike", 0.2),
                           ItemEffect("절대영도", "크리티컬 시 적 1턴 행동불가 (보스 면역)", "absolute_zero", True, "always", True)],
                          ElementalAffinity.ICE)
        frost_blade.stats = {"physical_attack": 23, "magic_defense": 8}
        items.append(frost_blade)
        
        storm_blade = Item("번개의 검", ItemType.WEAPON, ItemRarity.RARE,
                          "전기가 흐르는 마법검", 520, 2.4, 12, 125,
                          [ItemEffect("전기 충격", "30% 확률로 마비 부여", "paralysis_chance", 0.3),
                           ItemEffect("연쇄 번개", "크리티컬 시 인근 적에게 연쇄 피해", "chain_lightning", True)],
                          ElementalAffinity.LIGHTNING)
        storm_blade.stats = {"physical_attack": 22, "speed": 8}
        items.append(storm_blade)
        
        earth_breaker = Item("대지의 검", ItemType.WEAPON, ItemRarity.RARE,
                            "대지의 힘이 깃든 거대한 검", 550, 3.5, 11, 140,
                            [ItemEffect("지진", "공격 시 25% 확률로 모든 적 기절 (보스 면역)", "earthquake", 0.25, "always", True),
                             ItemEffect("견고함", "받는 피해 -15%", "earth_shield", 0.85)],
                            ElementalAffinity.EARTH)
        earth_breaker.stats = {"physical_attack": 28, "physical_defense": 12}
        items.append(earth_breaker)
        
        wind_cutter = Item("바람의 검", ItemType.WEAPON, ItemRarity.RARE,
                          "바람처럼 빠른 검", 450, 1.8, 9, 110,
                          [ItemEffect("바람 베기", "회피 불가능한 공격", "wind_slash", True),
                           ItemEffect("순풍", "매 턴 속도 +2", "tailwind", 2)],
                          ElementalAffinity.WIND)
        wind_cutter.stats = {"physical_attack": 20, "speed": 15}
        items.append(wind_cutter)
        
        # ⚔️ 전설급 무기들
        dragon_slayer = Item("드래곤 슬레이어", ItemType.WEAPON, ItemRarity.LEGENDARY,
                            "용을 잡기 위해 만들어진 전설의 검", 2000, 4.0, 20, 250,
                            [ItemEffect("용 특효", "드래곤족에게 3배 피해", "dragon_bane", 3.0),
                             ItemEffect("용의 심장", "크리티컬 시 브레이브 +10", "dragon_heart", 10),
                             ItemEffect("용린 갑옷", "물리 피해 -25%", "dragon_scale", 0.75)],
                            ElementalAffinity.FIRE)
        dragon_slayer.stats = {"physical_attack": 45, "magic_attack": 20, "brave": 15}
        items.append(dragon_slayer)
        
        void_blade = Item("공허의 검", ItemType.WEAPON, ItemRarity.LEGENDARY,
                         "모든 것을 무로 돌리는 검", 2200, 3.0, 22, 300,
                         [ItemEffect("공허 베기", "방어력 무시 피해", "void_cut", True),
                          ItemEffect("무효화", "50% 확률로 적의 스킬 무효화", "nullify", 0.5),
                          ItemEffect("존재 소거", "치명타 시 적 즉사 (보스 면역)", "existence_erase", True, "critical", True)],
                         ElementalAffinity.DARK)
        void_blade.stats = {"physical_attack": 40, "magic_attack": 25, "speed": 10}
        items.append(void_blade)
        
        # 🛡️ 강력한 방어구들
        dragon_mail = Item("드래곤 메일", ItemType.ARMOR, ItemRarity.EPIC,
                          "용의 비늘로 만든 갑옷", 1200, 8.0, 15, 180,
                          [ItemEffect("용의 보호", "화염 피해 -50%", "fire_resistance", 0.5),
                           ItemEffect("위압", "적 명중률 -20%", "intimidation", 0.8)],
                          ElementalAffinity.FIRE)
        dragon_mail.stats = {"physical_defense": 25, "magic_defense": 15, "hp": 50}
        items.append(dragon_mail)
        
        phoenix_robe = Item("불사조 로브", ItemType.ARMOR, ItemRarity.LEGENDARY,
                           "불사조의 깃털로 만든 마법 로브", 1800, 3.0, 18, 200,
                           [ItemEffect("부활", "사망 시 50% HP로 부활 (1회)", "phoenix_revival", 0.5),
                            ItemEffect("재생의 불꽃", "매 턴 HP 5% 회복", "flame_regeneration", 0.05),
                            ItemEffect("화염 면역", "화염 피해 완전 무효", "fire_immunity", True)],
                           ElementalAffinity.FIRE)
        phoenix_robe.stats = {"magic_defense": 30, "hp": 80, "mp": 40}
        items.append(phoenix_robe)
        
        # 🔮 신비한 장신구들
        time_ring = Item("시간의 반지", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                        "시간을 조작하는 신비한 반지", 3000, 0.1, 25, 100,
                        [ItemEffect("시간 정지", "5% 확률로 적 행동 스킵", "time_stop", 0.05),
                         ItemEffect("가속", "매 턴 시작 시 추가 행동", "haste", True)],
                        ElementalAffinity.NEUTRAL)
        time_ring.stats = {"speed": 20, "luck": 10}
        items.append(time_ring)
        
        soul_amulet = Item("영혼의 목걸이", ItemType.ACCESSORY, ItemRarity.EPIC,
                          "영혼의 힘을 담은 목걸이", 800, 0.3, 12, 120,
                          [ItemEffect("영혼 흡수", "적 처치 시 MP 전체 회복", "soul_drain", True),
                           ItemEffect("정신력", "정신 상태이상 면역", "mental_immunity", True)],
                          ElementalAffinity.DARK)
        soul_amulet.stats = {"mp": 30, "magic_attack": 10}
        items.append(soul_amulet)
        
        # 🌟 시야 확장 장비들 (중요!)
        eagle_eye = Item("독수리의 눈", ItemType.ACCESSORY, ItemRarity.RARE,
                        "독수리의 예리한 시야를 가진 보석", 600, 0.2, 8, 80,
                        [ItemEffect("정밀 조준", "크리티컬 확률 +15%", "precision", 15)],
                        ElementalAffinity.NEUTRAL)
        eagle_eye.stats = {"vision_range": 2, "dexterity": 8}
        items.append(eagle_eye)
        
        oracle_crystal = Item("예언자의 수정구", ItemType.ACCESSORY, ItemRarity.EPIC,
                             "미래를 보는 마법 수정구", 1500, 0.5, 15, 150,
                             [ItemEffect("예지력", "회피율 +25%", "foresight", 25),
                              ItemEffect("위험 감지", "함정 탐지 확률 +50%", "danger_sense", 0.5)],
                             ElementalAffinity.LIGHT)
        oracle_crystal.stats = {"vision_range": 3, "wisdom": 15, "luck": 10}
        items.append(oracle_crystal)
        
        gods_sight = Item("신의 시야", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                         "신의 전지적 시야를 가진 유물", 5000, 0.1, 30, 300,
                         [ItemEffect("전지", "맵 전체 공개", "omniscience", True),
                          ItemEffect("신성", "모든 능력치 +20%", "divine_blessing", 1.2)],
                         ElementalAffinity.LIGHT)
        gods_sight.stats = {"vision_range": 10, "all_stats": 20}
        items.append(gods_sight)
        
        power_ring = Item("힘의 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                         "착용자의 힘을 증가시키는 반지")
        power_ring.stats = {"physical_attack": 8}
        power_ring.value = 300
        items.append(power_ring)
        
        wisdom_ring = Item("지혜의 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                          "착용자의 지혜를 증가시키는 반지")
        wisdom_ring.stats = {"magic_attack": 8}
        wisdom_ring.value = 300
        items.append(wisdom_ring)
        
        agility_ring = Item("민첩의 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                           "착용자의 민첩성을 증가시키는 반지")
        agility_ring.stats = {"speed": 5}
        agility_ring.value = 300
        items.append(agility_ring)
        
        vitality_ring = Item("활력의 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                            "착용자의 생명력을 증가시키는 반지")
        vitality_ring.stats = {"max_hp": 25}
        vitality_ring.value = 300
        items.append(vitality_ring)
        
        # 목걸이류
        copper_necklace = Item("구리 목걸이", ItemType.ACCESSORY, ItemRarity.COMMON,
                              "구리로 만든 간단한 목걸이")
        copper_necklace.stats = {"physical_defense": 2}
        copper_necklace.value = 15
        items.append(copper_necklace)
        
        silver_necklace = Item("은목걸이", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                              "은으로 만든 우아한 목걸이")
        silver_necklace.stats = {"magic_defense": 5}
        silver_necklace.value = 80
        items.append(silver_necklace)
        
        pearl_necklace = Item("진주 목걸이", ItemType.ACCESSORY, ItemRarity.RARE,
                             "아름다운 진주로 만든 목걸이")
        pearl_necklace.stats = {"charisma": 8, "max_mp": 15}
        pearl_necklace.value = 400
        items.append(pearl_necklace)
        
        dragon_pendant = Item("드래곤 펜던트", ItemType.ACCESSORY, ItemRarity.EPIC,
                             "드래곤의 힘이 깃든 펜던트")
        dragon_pendant.stats = {"physical_attack": 10, "magic_attack": 10}
        dragon_pendant.effects = ["dragon_power"]
        dragon_pendant.value = 1000
        items.append(dragon_pendant)
        
        # 귀걸이류
        simple_earring = Item("간단한 귀걸이", ItemType.ACCESSORY, ItemRarity.COMMON,
                             "기본적인 귀걸이")
        simple_earring.stats = {"luck": 1}
        simple_earring.value = 10
        items.append(simple_earring)
        
        magic_earring = Item("마법 귀걸이", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                            "마법이 깃든 귀걸이")
        magic_earring.stats = {"max_mp": 10}
        magic_earring.value = 60
        items.append(magic_earring)
        
        diamond_earring = Item("다이아몬드 귀걸이", ItemType.ACCESSORY, ItemRarity.EPIC,
                              "다이아몬드로 만든 최고급 귀걸이")
        diamond_earring.stats = {"all_stats": 5}
        diamond_earring.value = 1500
        items.append(diamond_earring)
        
        # 팔찌류
        leather_bracelet = Item("가죽 팔찌", ItemType.ACCESSORY, ItemRarity.COMMON,
                               "가죽으로 만든 간단한 팔찌")
        leather_bracelet.stats = {"physical_defense": 1}
        leather_bracelet.value = 8
        items.append(leather_bracelet)
        
        iron_bracelet = Item("철 팔찌", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                            "철로 만든 튼튼한 팔찌")
        iron_bracelet.stats = {"physical_defense": 4}
        iron_bracelet.value = 40
        items.append(iron_bracelet)
        
        power_bracelet = Item("파워 팔찌", ItemType.ACCESSORY, ItemRarity.RARE,
                             "힘을 증폭시키는 마법 팔찌")
        power_bracelet.stats = {"physical_attack": 6}
        power_bracelet.value = 250
        items.append(power_bracelet)
        
        # 특수 장신구
        lucky_charm = Item("행운의 부적", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                          "행운을 가져다주는 부적")
        lucky_charm.stats = {"luck": 8}
        lucky_charm.effects = ["luck_boost"]
        lucky_charm.value = 100
        items.append(lucky_charm)
        
        evil_eye = Item("사악한 눈", ItemType.ACCESSORY, ItemRarity.RARE,
                       "적을 위축시키는 저주받은 보석")
        evil_eye.stats = {"intimidation": 10}
        evil_eye.effects = ["fear_aura"]
        evil_eye.value = 300
        items.append(evil_eye)
        
        angel_feather = Item("천사의 깃털", ItemType.ACCESSORY, ItemRarity.EPIC,
                            "순수한 천사의 깃털")
        angel_feather.stats = {"magic_defense": 15}
        angel_feather.effects = ["holy_protection", "status_immunity"]
        angel_feather.value = 800
        items.append(angel_feather)
        
        demon_horn = Item("악마의 뿔", ItemType.ACCESSORY, ItemRarity.EPIC,
                         "강력한 악마의 뿔")
        demon_horn.stats = {"magic_attack": 15}
        demon_horn.effects = ["dark_magic", "fear_immunity"]
        demon_horn.value = 800
        items.append(demon_horn)
        
        # 원소 장신구
        fire_amulet = Item("화염 부적", ItemType.ACCESSORY, ItemRarity.RARE,
                          "화염의 힘이 깃든 부적")
        fire_amulet.stats = {"fire_attack": 10}
        fire_amulet.effects = ["fire_boost", "fire_resist"]
        fire_amulet.value = 350
        items.append(fire_amulet)
        
        ice_amulet = Item("얼음 부적", ItemType.ACCESSORY, ItemRarity.RARE,
                         "얼음의 힘이 깃든 부적")
        ice_amulet.stats = {"ice_attack": 10}
        ice_amulet.effects = ["ice_boost", "ice_resist"]
        ice_amulet.value = 350
        items.append(ice_amulet)
        
        thunder_amulet = Item("번개 부적", ItemType.ACCESSORY, ItemRarity.RARE,
                             "번개의 힘이 깃든 부적")
        thunder_amulet.stats = {"thunder_attack": 10}
        thunder_amulet.effects = ["thunder_boost", "thunder_resist"]
        thunder_amulet.value = 350
        items.append(thunder_amulet)
        
        earth_amulet = Item("대지 부적", ItemType.ACCESSORY, ItemRarity.RARE,
                           "대지의 힘이 깃든 부적")
        earth_amulet.stats = {"earth_attack": 10}
        earth_amulet.effects = ["earth_boost", "earth_resist"]
        earth_amulet.value = 350
        items.append(earth_amulet)
        
        # 상태이상 저항 장신구
        poison_resist_ring = Item("독 저항 반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                                 "독에 대한 저항력을 제공하는 반지")
        poison_resist_ring.effects = ["poison_immunity"]
        poison_resist_ring.value = 150
        items.append(poison_resist_ring)
        
        sleep_resist_ring = Item("수면 저항 반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                                "수면에 대한 저항력을 제공하는 반지")
        sleep_resist_ring.effects = ["sleep_immunity"]
        sleep_resist_ring.value = 150
        items.append(sleep_resist_ring)
        
        silence_resist_ring = Item("침묵 저항 반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                                  "침묵에 대한 저항력을 제공하는 반지")
        silence_resist_ring.effects = ["silence_immunity"]
        silence_resist_ring.value = 150
        items.append(silence_resist_ring)
        
        # 특수 능력 장신구
        regeneration_ring = Item("재생 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                                "착용자를 천천히 치유하는 반지")
        regeneration_ring.effects = ["hp_regen"]
        regeneration_ring.value = 400
        items.append(regeneration_ring)
        
        mana_regen_ring = Item("마나 재생 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                              "마나를 천천히 회복시키는 반지")
        mana_regen_ring.effects = ["mp_regen"]
        mana_regen_ring.value = 400
        items.append(mana_regen_ring)
        
        critical_ring = Item("크리티컬 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                            "치명타 확률을 증가시키는 반지")
        critical_ring.stats = {"crit_chance": 15}
        critical_ring.value = 500
        items.append(critical_ring)
        
        double_strike_ring = Item("연속타격 반지", ItemType.ACCESSORY, ItemRarity.EPIC,
                                 "공격이 두 번 발동될 확률을 제공")
        double_strike_ring.effects = ["double_attack_chance"]
        double_strike_ring.value = 1000
        items.append(double_strike_ring)
        
        # === 추가 재료 (30개) ===
        mithril_ore = Item("미스릴 광석", ItemType.MATERIAL, ItemRarity.RARE,
                          "전설의 금속 미스릴의 원석")
        mithril_ore.value = 100
        items.append(mithril_ore)
        
        adamantite_ore = Item("아다만타이트 광석", ItemType.MATERIAL, ItemRarity.EPIC,
                             "최고급 금속 아다만타이트의 원석")
        adamantite_ore.value = 500
        items.append(adamantite_ore)
        
        dragon_scale_material = Item("드래곤 비늘", ItemType.MATERIAL, ItemRarity.EPIC,
                                    "드래곤의 강인한 비늘")
        dragon_scale_material.value = 800
        items.append(dragon_scale_material)
        
        phoenix_feather_material = Item("불사조 깃털", ItemType.MATERIAL, ItemRarity.LEGENDARY,
                                       "불사조의 신비한 깃털")
        phoenix_feather_material.value = 2000
        items.append(phoenix_feather_material)
        
        unicorn_horn = Item("유니콘 뿔", ItemType.MATERIAL, ItemRarity.LEGENDARY,
                           "순수한 유니콘의 뿔")
        unicorn_horn.value = 1500
        items.append(unicorn_horn)
        
        demon_blood = Item("악마의 피", ItemType.MATERIAL, ItemRarity.EPIC,
                          "강력한 악마의 피")
        demon_blood.value = 600
        items.append(demon_blood)
        
        angel_tear = Item("천사의 눈물", ItemType.MATERIAL, ItemRarity.EPIC,
                         "순수한 천사의 눈물")
        angel_tear.value = 700
        items.append(angel_tear)
        
        moonstone = Item("문스톤", ItemType.MATERIAL, ItemRarity.RARE,
                        "달빛이 깃든 신비한 돌")
        moonstone.value = 200
        items.append(moonstone)
        
        sunstone = Item("선스톤", ItemType.MATERIAL, ItemRarity.RARE,
                       "태양빛이 깃든 따뜻한 돌")
        sunstone.value = 200
        items.append(sunstone)
        
        void_crystal = Item("공허 수정", ItemType.MATERIAL, ItemRarity.LEGENDARY,
                           "공허의 힘이 담긴 어둠의 수정")
        void_crystal.value = 3000
        items.append(void_crystal)
        
        dragon_tooth = Item("용의 이빨", ItemType.MATERIAL, ItemRarity.EPIC,
                           "전설급 무기 제작에 사용되는 희귀 재료")
        dragon_tooth.value = 500
        items.append(dragon_tooth)
        
        # === 시야 증가 특수 아이템들 ===
        
        # 망원경류
        spyglass = Item("망원경", ItemType.ACCESSORY, ItemRarity.COMMON,
                       "간단한 단안 망원경, 시야를 조금 넓혀준다", 200, 0.8)
        spyglass.stats = {"vision_range": 1}
        spyglass.effects = ["scout_vision"]
        items.append(spyglass)
        
        magic_scope = Item("마법 망원경", ItemType.ACCESSORY, ItemRarity.RARE,
                          "마법으로 강화된 망원경, 시야를 크게 넓혀준다", 800, 1.0)
        magic_scope.stats = {"vision_range": 2, "magic_defense": 5}
        magic_scope.effects = ["detect_secret", "scout_vision"]
        items.append(magic_scope)
        
        eagle_eye_lens = Item("독수리의 눈", ItemType.ACCESSORY, ItemRarity.EPIC,
                             "전설의 독수리 눈으로 만든 렌즈, 매우 넓은 시야", 2000, 0.5)
        eagle_eye_lens.stats = {"vision_range": 3, "accuracy": 15}
        eagle_eye_lens.effects = ["true_sight", "detect_hidden", "scout_vision"]
        items.append(eagle_eye_lens)
        
        prophets_orb = Item("예언자의 수정구", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                           "미래를 보는 수정구, 극도로 넓은 시야", 5000, 2.0)
        prophets_orb.stats = {"vision_range": 4, "magic_attack": 20, "mp": 30}
        prophets_orb.effects = ["future_sight", "detect_all", "mana_regen"]
        items.append(prophets_orb)
        
        dragons_gaze = Item("드래곤의 시선", ItemType.ACCESSORY, ItemRarity.LEGENDARY,
                           "고대 드래곤의 눈, 신적인 시야를 제공", 8000, 1.5)
        dragons_gaze.stats = {"vision_range": 5, "all_resistance": 10}
        dragons_gaze.effects = ["dragon_sight", "see_through_walls", "intimidate"]
        items.append(dragons_gaze)
        
        # 시야 증가 투구들
        scouts_helm = Item("정찰병의 투구", ItemType.ARMOR, ItemRarity.UNCOMMON,
                          "정찰에 특화된 가벼운 투구", 300, 2.0)
        scouts_helm.stats = {"physical_defense": 8, "vision_range": 1, "speed": 3}
        scouts_helm.effects = ["stealth_bonus"]
        items.append(scouts_helm)
        
        watchtower_crown = Item("감시탑의 왕관", ItemType.ARMOR, ItemRarity.RARE,
                               "감시병들이 착용하던 특별한 왕관", 1200, 1.8)
        watchtower_crown.stats = {"physical_defense": 12, "vision_range": 2, "wisdom": 8}
        watchtower_crown.effects = ["alert_boost", "detect_ambush"]
        items.append(watchtower_crown)
        
        # 시야 증가 무기들
        ranger_bow = Item("레인저 활", ItemType.WEAPON, ItemRarity.RARE,
                         "숙련된 레인저가 사용하는 특별한 활", 600, 2.5)
        ranger_bow.stats = {"physical_attack": 18, "vision_range": 2, "accuracy": 10}
        ranger_bow.effects = ["long_shot", "track_target"]
        items.append(ranger_bow)
        
        sniper_crossbow = Item("저격 석궁", ItemType.WEAPON, ItemRarity.EPIC,
                              "정밀 사격을 위한 고급 석궁", 1500, 4.0)
        sniper_crossbow.stats = {"physical_attack": 25, "vision_range": 3, "accuracy": 20}
        sniper_crossbow.effects = ["pierce_shot", "critical_boost"]
        items.append(sniper_crossbow)
        
        return items
    
    @staticmethod
    def get_random_item(level: int = 1) -> Item:
        """레벨에 맞는 랜덤 아이템 생성 (레벨 제한 포함)"""
        all_items = ItemDatabase.get_all_items()
        
        # 레벨 제한을 만족하는 아이템들만 필터링
        available_items = [item for item in all_items if item.min_level <= level]
        
        if not available_items:
            # 레벨 제한으로 사용 가능한 아이템이 없으면 기본 아이템 반환
            return next((item for item in all_items if item.min_level == 1), all_items[0])
        
        # 레벨에 따른 희귀도 확률 조정
        rarity_weights = {
            ItemRarity.COMMON: max(60 - level * 2, 20),
            ItemRarity.UNCOMMON: min(25 + level, 35),
            ItemRarity.RARE: min(10 + level // 2, 25),
            ItemRarity.EPIC: min(4 + level // 5, 15),
            ItemRarity.LEGENDARY: min(1 + level // 10, 5)
        }
        
        # 가중치에 따라 희귀도 선택
        rarity_list = list(rarity_weights.keys())
        weight_list = list(rarity_weights.values())
        chosen_rarity = random.choices(rarity_list, weights=weight_list)[0]
        
        # 해당 희귀도의 아이템들 필터링 (레벨 제한 고려)
        filtered_items = [item for item in available_items if item.rarity == chosen_rarity]
        
        # 해당 희귀도가 없으면 사용 가능한 아이템 중 랜덤 선택
        if filtered_items:
            return random.choice(filtered_items)
        else:
            return random.choice(available_items)
    
    @staticmethod
    def get_random_loot(level: int = 1, count: int = 1) -> List[Item]:
        """랜덤 전리품 생성"""
        loot = []
        for _ in range(count):
            # 80% 확률로 아이템 드롭
            if random.random() < 0.8:
                loot.append(ItemDatabase.get_random_item(level))
        return loot
    
    @staticmethod
    def get_items_by_type(item_type: ItemType) -> List[Item]:
        """타입별 아이템 필터링"""
        all_items = ItemDatabase.get_all_items()
        return [item for item in all_items if item.item_type == item_type]
    
    @staticmethod
    def get_items_by_rarity(rarity: ItemRarity) -> List[Item]:
        """희귀도별 아이템 필터링"""
        all_items = ItemDatabase.get_all_items()
        return [item for item in all_items if item.rarity == rarity]
    
    @staticmethod
    def get_item(item_name: str) -> Optional[Item]:
        """이름으로 아이템 검색"""
        all_items = ItemDatabase.get_all_items()
        for item in all_items:
            if item.name == item_name:
                return item
        return None
        items.append(magic_staff)
        
        # 방어구
        leather_armor = Item("가죽 갑옷", ItemType.ARMOR, ItemRarity.COMMON,
                           "가벼운 가죽으로 만든 갑옷")
        leather_armor.stats = {"physical_defense": 3}
        leather_armor.value = 80
        items.append(leather_armor)
        
        # 장신구
        speed_ring = Item("신속의 반지", ItemType.ACCESSORY, ItemRarity.RARE,
                         "착용자의 속도를 증가시킨다")
        speed_ring.stats = {"speed": 3}
        speed_ring.value = 200
        items.append(speed_ring)
        
        # FFOO 스타일 특수 아이템들
        brave_booster = Item("용기의 오브", ItemType.CONSUMABLE, ItemRarity.UNCOMMON,
                           "Brave 포인트를 500 증가시킨다")
        brave_booster.effects = ["brave_boost"]
        brave_booster.stats = {"brave_amount": 500}
        brave_booster.value = 100
        items.append(brave_booster)
        
        phoenix_down = Item("불사조의 깃털", ItemType.CONSUMABLE, ItemRarity.RARE,
                           "전투불능 상태를 해제하고 HP를 50% 회복한다")
        phoenix_down.effects = ["revive"]
        phoenix_down.stats = {"revive_hp_percent": 50}
        phoenix_down.value = 300
        items.append(phoenix_down)
        
        brave_crystal = Item("용기의 크리스탈", ItemType.MATERIAL, ItemRarity.EPIC,
                           "캐릭터 업그레이드에 사용되는 특별한 재료")
        brave_crystal.value = 500
        items.append(brave_crystal)
        
        # 전설 무기
        excalibur = Item("엑스칼리버", ItemType.WEAPON, ItemRarity.LEGENDARY,
                        "전설의 성검, 모든 능력치를 향상시킨다")
        excalibur.stats = {"physical_attack": 15, "magic_attack": 10, "speed": 2, 
                          "int_brv": 300, "max_brv": 2000}  # Brave 스탯 보너스
        excalibur.effects = ["brave_regen"]
        excalibur.value = 1000
        items.append(excalibur)
        
        # 추가 Brave 관련 아이템들
        brave_sword = Item("용기의 검", ItemType.WEAPON, ItemRarity.RARE,
                          "Brave 능력을 향상시키는 마검")
        brave_sword.stats = {"physical_attack": 10, "int_brv": 200, "max_brv": 1500}
        brave_sword.value = 600
        items.append(brave_sword)
        
        courage_ring = Item("용맹의 반지", ItemType.ACCESSORY, ItemRarity.EPIC,
                           "착용자의 용기를 극대화시킨다")
        courage_ring.stats = {"int_brv": 400, "max_brv": 1000, "speed": 1}
        courage_ring.value = 800
        items.append(courage_ring)
        
        # 희귀도별 자동 레벨 제한 설정
        ItemDatabase._apply_auto_level_restrictions(items)
        
        return items
    
    @staticmethod
    def _apply_auto_level_restrictions(items: List[Item]):
        """희귀도에 따른 자동 레벨 제한 적용"""
        for item in items:
            # 희귀도별 기본 레벨 제한 설정
            if item.rarity == ItemRarity.COMMON:
                item.min_level = 1
            elif item.rarity == ItemRarity.UNCOMMON:
                item.min_level = 3
            elif item.rarity == ItemRarity.RARE:
                item.min_level = 6
            elif item.rarity == ItemRarity.EPIC:
                item.min_level = 10
            elif item.rarity == ItemRarity.LEGENDARY:
                item.min_level = 15
                
            # 특별히 강력한 아이템들은 더 높은 레벨 제한
            if ("dragon" in item.name.lower() or "창조" in item.name or "시공간" in item.name or 
                "드래곤" in item.name or "용" in item.name):
                item.min_level = max(item.min_level, 20)
            elif ("전설" in item.name or "신화" in item.name or "고대" in item.name or 
                  "현실" in item.name or "무한" in item.name or "영원" in item.name):
                item.min_level = max(item.min_level, 18)
            elif ("마왕" in item.name or "악마" in item.name or "공허" in item.name):
                item.min_level = max(item.min_level, 16)
    
    @staticmethod
    def get_random_item_by_stage(stage: int) -> Optional[Item]:
        """스테이지를 고려한 랜덤 아이템 생성 (레벨 제한 포함)"""
        # 층수별 아이템 등급 제한
        if stage <= 5:
            # 1~5층: UNCOMMON 이하만 허용
            max_allowed_rarity = ItemRarity.UNCOMMON
        elif stage <= 12:
            # 6~12층: RARE까지 허용
            max_allowed_rarity = ItemRarity.RARE
        else:
            # 13층 이상: 모든 등급 허용
            max_allowed_rarity = None
        
        # 드롭 확률 체크
        drop_chance = DropRateManager.get_drop_chance(stage)
        if random.random() > drop_chance:
            return None
            
        # 희귀도 선택
        target_rarity = DropRateManager.select_rarity_by_stage(stage)
        
        # 층수별 제한 적용
        if max_allowed_rarity and target_rarity.value > max_allowed_rarity.value:
            target_rarity = max_allowed_rarity
        
        # 해당 희귀도의 아이템들 필터링 (레벨 제한 고려)
        all_items = ItemDatabase.get_all_items()
        items_by_rarity = [item for item in all_items 
                          if item.rarity == target_rarity and item.min_level <= stage]
        
        # 레벨 제한으로 인해 해당 희귀도 아이템이 없으면 낮은 희귀도로 대체
        if not items_by_rarity:
            # 단계적으로 낮은 희귀도로 시도
            fallback_rarities = [ItemRarity.RARE, ItemRarity.UNCOMMON, ItemRarity.COMMON]
            for fallback_rarity in fallback_rarities:
                if fallback_rarity.value <= max_allowed_rarity.value:
                    items_by_rarity = [item for item in all_items 
                                      if item.rarity == fallback_rarity and item.min_level <= stage]
                    if items_by_rarity:
                        break
            
        if not items_by_rarity:
            return None
            
        # 랜덤 선택
        selected_item = random.choice(items_by_rarity)
        
        # 아이템 복사본 생성 (원본 보호)
        new_item = Item(
            selected_item.name,
            selected_item.item_type,
            selected_item.rarity,
            selected_item.description,
            selected_item.value,
            selected_item.weight,
            selected_item.min_level
        )
        
        # 스탯과 효과 복사
        new_item.stats = selected_item.stats.copy()
        new_item.effects = selected_item.effects.copy()
        
        # 스테이지 스케일링 적용
        new_item.apply_stage_scaling(stage)
        
        return new_item
    
    @staticmethod
    def generate_stage_loot(stage: int, enemy_count: int = 1) -> List[Item]:
        """스테이지 완료 시 전리품 생성"""
        loot = []
        
        # 기본 드롭
        for _ in range(enemy_count):
            item = ItemDatabase.get_random_item_by_stage(stage)
            if item:
                loot.append(item)
                
        # 보너스 드롭 체크
        bonus_chance = DropRateManager.get_bonus_drop_chance(stage)
        if random.random() < bonus_chance:
            bonus_item = ItemDatabase.get_random_item_by_stage(stage + 2)  # 보너스는 2스테이지 높은 아이템
            if bonus_item:
                loot.append(bonus_item)
                
        # 스테이지 클리어 보상 (5스테이지마다)
        if stage % 5 == 0:
            special_item = ItemDatabase.get_special_reward(stage)
            if special_item:
                loot.append(special_item)
                
        return loot
    
    @staticmethod
    def get_special_reward(stage: int) -> Optional[Item]:
        """특수 보상 아이템 (5, 10, 15, 20층 등)"""
        if stage % 20 == 0:  # 20층마다 전설 아이템
            legendary_items = [item for item in ItemDatabase.get_all_items() 
                             if item.rarity == ItemRarity.LEGENDARY]
            if legendary_items:
                selected = random.choice(legendary_items)
                # 복사본 생성 및 스케일링
                reward = Item(selected.name, selected.item_type, selected.rarity,
                            selected.description, selected.value, selected.weight)
                reward.stats = selected.stats.copy()
                reward.effects = selected.effects.copy()
                reward.apply_stage_scaling(stage)
                return reward
                
        elif stage % 10 == 0:  # 10층마다 영웅 아이템
            epic_items = [item for item in ItemDatabase.get_all_items() 
                         if item.rarity == ItemRarity.EPIC]
            if epic_items:
                selected = random.choice(epic_items)
                reward = Item(selected.name, selected.item_type, selected.rarity,
                            selected.description, selected.value, selected.weight)
                reward.stats = selected.stats.copy()
                reward.effects = selected.effects.copy()
                reward.apply_stage_scaling(stage)
                return reward
                
        elif stage % 5 == 0:  # 5층마다 희귀 아이템
            rare_items = [item for item in ItemDatabase.get_all_items() 
                         if item.rarity == ItemRarity.RARE]
            if rare_items:
                selected = random.choice(rare_items)
                reward = Item(selected.name, selected.item_type, selected.rarity,
                            selected.description, selected.value, selected.weight)
                reward.stats = selected.stats.copy()
                reward.effects = selected.effects.copy()
                reward.apply_stage_scaling(stage)
                return reward
                
        return None
    
    @staticmethod
    def get_items_by_rarity(rarity: ItemRarity) -> List[Item]:
        """희귀도별 아이템 목록 반환"""
        all_items = ItemDatabase.get_all_items()
        return [item for item in all_items if item.rarity == rarity]
    
    @staticmethod
    def get_items_by_type(item_type: ItemType) -> List[Item]:
        """타입별 아이템 목록 반환"""
        all_items = ItemDatabase.get_all_items()
        return [item for item in all_items if item.item_type == item_type]
        items.append(courage_ring)
        
        mystic_orb = Item("신비의 오브", ItemType.ACCESSORY, ItemRarity.UNCOMMON,
                         "마법사를 위한 Brave 증폭 장치")
        mystic_orb.stats = {"magic_attack": 5, "int_brv": 150, "max_brv": 2500}
        mystic_orb.value = 400
        items.append(mystic_orb)
        
        return items
    
    @staticmethod
    def get_random_item(rarity_weights: Dict[ItemRarity, float] = None) -> Item:
        """랜덤 아이템 생성"""
        if rarity_weights is None:
            rarity_weights = {
                ItemRarity.COMMON: 0.5,
                ItemRarity.UNCOMMON: 0.3,
                ItemRarity.RARE: 0.15,
                ItemRarity.EPIC: 0.04,
                ItemRarity.LEGENDARY: 0.01
            }
            
        # 희귀도 결정
        rarity_list = list(rarity_weights.keys())
        weights = list(rarity_weights.values())
        selected_rarity = random.choices(rarity_list, weights=weights)[0]
        
        # 해당 희귀도의 아이템 중 선택
        all_items = ItemDatabase.get_all_items()
        items_of_rarity = [item for item in all_items if item.rarity == selected_rarity]
        
        if items_of_rarity:
            return random.choice(items_of_rarity)
        else:
            return ItemDatabase.get_all_items()[0]  # 기본 아이템


class Inventory:
    """인벤토리 클래스 (무게 제한 포함)"""
    
    def __init__(self, max_size: int = 30, max_weight: float = 50.0):
        self.items: Dict[str, int] = {}  # 아이템명: 개수
        self.max_size = max_size
        self.max_weight = max_weight
        
    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """아이템 추가 (무게 제한 확인)"""
        # 슬롯 수 확인
        if len(self.items) >= self.max_size and item.name not in self.items:
            return False
        
        # 무게 제한 확인
        total_weight = self.get_total_weight() + (item.weight * quantity)
        if total_weight > self.max_weight:
            return False
            
        if item.name in self.items:
            self.items[item.name] += quantity
        else:
            self.items[item.name] = quantity
        return True
        
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """아이템 제거"""
        if item_name not in self.items:
            return False
            
        if self.items[item_name] <= quantity:
            del self.items[item_name]
        else:
            self.items[item_name] -= quantity
        return True
        
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """아이템 보유 확인"""
        return self.items.get(item_name, 0) >= quantity
        
    def get_items_list(self) -> List[tuple]:
        """아이템 목록 반환 (이름, 개수)"""
        return list(self.items.items())
        
    def is_full(self) -> bool:
        """인벤토리가 가득 찬지 확인 (슬롯 기준)"""
        return len(self.items) >= self.max_size
    
    def is_weight_full(self) -> bool:
        """무게 제한에 도달했는지 확인"""
        return self.get_total_weight() >= self.max_weight
    
    def get_total_weight(self) -> float:
        """전체 무게 계산"""
        total_weight = 0.0
        db = ItemDatabase()
        for item_name, quantity in self.items.items():
            item = db.get_item(item_name)
            if item:
                total_weight += item.weight * quantity
        return total_weight
    
    def get_weight_ratio(self) -> float:
        """무게 비율 반환 (0.0 ~ 1.0)"""
        return min(self.get_total_weight() / self.max_weight, 1.0)
    
    def can_add_item(self, item: Item, quantity: int = 1) -> tuple:
        """아이템 추가 가능 여부와 이유 반환"""
        # 슬롯 확인
        if len(self.items) >= self.max_size and item.name not in self.items:
            return False, "인벤토리 슬롯이 가득 참"
        
        # 무게 확인
        total_weight = self.get_total_weight() + (item.weight * quantity)
        if total_weight > self.max_weight:
            return False, f"무게 제한 초과 ({total_weight:.1f}/{self.max_weight:.1f})"
        
        return True, "추가 가능"


# durability_system.py의 기능을 사용하므로 여기서는 import만
try:
    from game.durability_system import DurabilitySystem, GoldBalanceSystem, get_durability_system, get_gold_balance_system
except ImportError:
    try:
        from durability_system import DurabilitySystem, GoldBalanceSystem, get_durability_system, get_gold_balance_system
    except ImportError:
        # 폴백: 기본 시스템
        print("⚠️ durability_system.py를 불러올 수 없습니다. 기본 시스템을 사용합니다.")
        DurabilitySystem = None
        GoldBalanceSystem = None
