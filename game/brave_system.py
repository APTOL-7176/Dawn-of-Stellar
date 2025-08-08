"""
Brave 시스템 (파이널 판타지 오페라 옴니아 스타일)
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import time


class BraveAttackType(Enum):
    """Brave 공격 타입"""
    BRAVE = "brave"  # Brave 데미지 (Brave 포인트 증가)
    HP = "hp"        # HP 공격 (실제 HP 데미지, Brave 소모)
    BREAK = "break"  # Break 공격 (상대방 Brave를 0으로)


class BraveSkill:
    """Brave 스킬 클래스 (MP 소모 포함)"""
    
    def __init__(self, name: str, attack_type: BraveAttackType, 
                 brave_multiplier: float = 1.0, hp_multiplier: float = 1.0,
                 uses: int = -1, mp_cost: int = 0, description: str = "", 
                 hp_sacrifice_rate: float = 0.0, special_effects: list = None):
        self.name = name
        self.attack_type = attack_type
        self.brave_multiplier = brave_multiplier  # Brave 데미지 배율
        self.hp_multiplier = hp_multiplier        # HP 데미지 배율
        self.max_uses = uses                      # 최대 사용 횟수 (-1은 무제한)
        self.current_uses = uses
        self.mp_cost = mp_cost                    # MP 소모량
        self.description = description
        self.effects = []                         # 특수 효과들
        self.special_effects = special_effects or []  # 새로운 스킬 시스템 특수 효과
        self.is_healing_skill = self._check_if_healing()  # 회복 스킬 여부
        self.hp_sacrifice_rate = hp_sacrifice_rate  # HP 희생 비율 (0.0 ~ 1.0)
        
    def _check_if_healing(self) -> bool:
        """회복 스킬인지 확인"""
        healing_keywords = ["치유", "회복", "힐", "부활", "대치유"]
        return any(keyword in self.name for keyword in healing_keywords)
    
    def get_description_with_type(self) -> str:
        """공격 타입을 포함한 스킬 설명 반환"""
        type_indicators = {
            BraveAttackType.BRAVE: "🎯BRV",
            BraveAttackType.HP: "💥HP", 
            BraveAttackType.HYBRID: "⚡복합"
        }
        
        type_indicator = type_indicators.get(self.attack_type, "❓")
        return f"[{type_indicator}] {self.description}"
        
    def calculate_healing_amount(self, caster) -> int:
        """시전자의 스탯을 기반으로 회복량 계산"""
        if not self.is_healing_skill:
            return 0
            
        # 기본 회복량은 시전자의 마법력 기반
        base_heal = caster.magic_attack * 2
        
        # 스킬별 회복 계수
        healing_multipliers = {
            "치유술": 1.5,
            "대치유술": 2.5,
            "성스러운 빛": 1.0,
            "치유의빛": 1.2,
            "재생": 0.8  # 지속 회복
        }
        
        multiplier = healing_multipliers.get(self.name, 1.0)
        
        # 최종 회복량 계산
        heal_amount = int(base_heal * multiplier)
        
        # 최소/최대 회복량 제한
        min_heal = max(10, caster.level * 5)  # 최소 회복량
        max_heal = caster.magic_attack * 5    # 최대 회복량
        
        return max(min_heal, min(heal_amount, max_heal))
        
    def can_use(self, character=None) -> bool:
        """사용 가능한지 확인 (MP 포함)"""
        if self.current_uses == 0:
            return False
        if character and hasattr(character, 'current_mp'):
            return character.current_mp >= self.mp_cost
        return True
        
    def use_skill(self, character=None):
        """스킬 사용 (MP 소모 포함)"""
        if self.current_uses > 0:
            self.current_uses -= 1
        if character and hasattr(character, 'use_mp'):
            character.use_mp(self.mp_cost)


class BraveManager:
    """Brave 시스템 관리자"""
    
    def __init__(self):
        self.base_brave = 50   # 기본 Brave 값 (INT BRV) - 500에서 50으로 대폭 감소
        self.max_brave = 999   # 최대 Brave 값 (MAX BRV) - 9999에서 999로 감소
        
    def get_initial_brave(self, character) -> int:
        """캐릭터의 초기 Brave 계산 (INT BRV) - 밸런스 조정됨, 아군 3배 보너스"""
        base_int_brv = getattr(character, 'int_brv', self.base_brave)
        # 레벨과 장비에 따른 보정 (BRV 스케일 조정: 레벨당 2.5 증가)
        level_bonus = (character.level - 1) * 3 if hasattr(character, 'level') else 0  # 25에서 3으로 감소
        equipment_bonus = self._get_equipment_int_brv_bonus(character)
        
        calculated_int_brv = base_int_brv + level_bonus + equipment_bonus
        
        # 🎯 아군은 INT BRV 3배 보너스 적용
        if hasattr(character, 'character_class') and character.character_class != "Enemy":
            calculated_int_brv *= 3
            
        return calculated_int_brv
        
    def get_max_brave(self, character) -> int:
        """캐릭터의 최대 Brave 계산 (MAX BRV) - 아군 3배 보너스, 밸런스 조정됨"""
        base_max_brv = getattr(character, 'max_brv', self.max_brave)
        # 레벨과 장비에 따른 보정 (BRV 스케일 조정: 레벨당 10 증가)
        level_bonus = (character.level - 1) * 10 if hasattr(character, 'level') else 0  # 100에서 10으로 감소
        equipment_bonus = self._get_equipment_max_brv_bonus(character)
        
        calculated_max_brv = base_max_brv + level_bonus + equipment_bonus
        
        # 🎯 아군은 MAX BRV 3배 보너스 적용 (2배에서 3배로 증가)
        if hasattr(character, 'character_class') and character.character_class != "Enemy":
            calculated_max_brv *= 3
            
        return calculated_max_brv
        
    def _get_equipment_int_brv_bonus(self, character) -> int:
        """장비로부터 INT BRV 보너스 계산"""
        bonus = 0
        if hasattr(character, 'equipped_weapon') and character.equipped_weapon:
            bonus += character.equipped_weapon.stats.get('int_brv', 0)
        if hasattr(character, 'equipped_armor') and character.equipped_armor:
            bonus += character.equipped_armor.stats.get('int_brv', 0)
        if hasattr(character, 'equipped_accessory') and character.equipped_accessory:
            bonus += character.equipped_accessory.stats.get('int_brv', 0)
        return bonus
        
    def _get_equipment_max_brv_bonus(self, character) -> int:
        """장비로부터 MAX BRV 보너스 계산"""
        bonus = 0
        if hasattr(character, 'equipped_weapon') and character.equipped_weapon:
            bonus += character.equipped_weapon.stats.get('max_brv', 0)
        if hasattr(character, 'equipped_armor') and character.equipped_armor:
            bonus += character.equipped_armor.stats.get('max_brv', 0)
        if hasattr(character, 'equipped_accessory') and character.equipped_accessory:
            bonus += character.equipped_accessory.stats.get('max_brv', 0)
        return bonus
        
    def calculate_brave_damage(self, attacker, target, skill: BraveSkill) -> int:
        """Brave 데미지 계산 (밸런스 조정 + 요리 효과)"""
        if skill.attack_type != BraveAttackType.BRAVE:
            return 0
            
        # 밸런스 시스템 사용
        from .balance import GameBalance
        
        # 캐릭터 속성명 매핑
        if hasattr(attacker, 'get_effective_stat'):
            base_attack = attacker.get_effective_stat('physical_attack')
        elif hasattr(attacker, 'physical_attack'):
            base_attack = attacker.physical_attack
        else:
            base_attack = getattr(attacker, 'p_atk', 10)  # 기본값
            
        if hasattr(target, 'get_effective_stat'):
            target_defense = target.get_effective_stat('physical_defense')
        elif hasattr(target, 'physical_defense'):
            target_defense = target.physical_defense
        else:
            target_defense = getattr(target, 'p_def', 10)  # 기본값
        
        brave_damage = GameBalance.calculate_brave_damage(
            base_attack, target_defense, skill.brave_multiplier, attacker
        )
        
        # 요리 효과 적용 (BRV 게인 보너스)
        try:
            from game.field_cooking import get_brv_cooking_modifiers
            cooking_modifiers = get_brv_cooking_modifiers()
            
            if "brv_gain_multiplier" in cooking_modifiers:
                brave_damage = int(brave_damage * cooking_modifiers["brv_gain_multiplier"])
                
        except ImportError:
            pass  # 요리 시스템이 없으면 무시
        
        # 요리 효과로 인한 BRV 방어 적용 (대상이 받는 데미지 감소)
        try:
            from game.field_cooking import get_brv_cooking_modifiers
            target_cooking_modifiers = get_brv_cooking_modifiers()
            
            if "brv_defense_multiplier" in target_cooking_modifiers:
                # 방어력 증가 = 받는 데미지 감소
                defense_reduction = 1.0 / target_cooking_modifiers["brv_defense_multiplier"]
                brave_damage = int(brave_damage * defense_reduction)
                
        except ImportError:
            pass  # 요리 시스템이 없으면 무시
        
        # 랜덤 요소 추가 (90-110%)
        variance = random.uniform(0.9, 1.1)
        brave_damage = int(brave_damage * variance)
        
        return max(brave_damage, 1)
        
    def calculate_hp_damage(self, attacker, target, skill: BraveSkill) -> Tuple[int, int]:
        """HP 데미지 계산 (밸런스 조정, 실제 HP 데미지, 상처 데미지 + 요리 효과)"""
        if skill.attack_type != BraveAttackType.HP:
            return 0, 0
            
        # 밸런스 시스템 사용
        from .balance import GameBalance
        
        brave_points = getattr(attacker, 'brave_points', self.base_brave)
        is_break = getattr(target, 'is_broken', False)
        
        hp_damage = GameBalance.calculate_hp_damage(
            brave_points, skill.hp_multiplier, is_break, attacker  # attacker 추가
        )
        
        # 희생 위력 보너스 적용
        sacrifice_bonus = getattr(attacker, 'temp_sacrifice_power', 0)
        if sacrifice_bonus > 0:
            hp_damage += sacrifice_bonus
            # 희생 위력 보너스 사용 후 제거
            attacker.temp_sacrifice_power = 0
        
        # 요리 효과 적용 (BRV 데미지 보너스)
        try:
            from game.field_cooking import get_brv_cooking_modifiers
            cooking_modifiers = get_brv_cooking_modifiers()
            
            if "brv_damage_multiplier" in cooking_modifiers:
                hp_damage = int(hp_damage * cooking_modifiers["brv_damage_multiplier"])
                
        except ImportError:
            pass  # 요리 시스템이 없으면 무시
        
        # 요리 효과로 인한 BRV 방어 적용 (대상이 받는 HP 데미지 감소)
        try:
            from game.field_cooking import get_brv_cooking_modifiers
            target_cooking_modifiers = get_brv_cooking_modifiers()
            
            if "brv_defense_multiplier" in target_cooking_modifiers:
                # 방어력 증가 = 받는 데미지 감소
                defense_reduction = 1.0 / target_cooking_modifiers["brv_defense_multiplier"]
                hp_damage = int(hp_damage * defense_reduction)
                
        except ImportError:
            pass  # 요리 시스템이 없으면 무시
        
        # 상처 시스템과 연동 (데미지의 25%가 상처로)
        wound_damage = int(hp_damage * 0.25)
        
        return hp_damage, wound_damage
        
    def apply_break(self, target) -> bool:
        """Break 적용 - BRV가 0인 상태에서 BRV 공격을 받을 때"""
        if hasattr(target, 'brave_points') and target.brave_points <= 0:
            # 이미 BRV가 0인 상태에서 공격받음 = BREAK 발생
            setattr(target, 'is_broken_state', True)
            # Break 상태 효과 적용 (다음 턴 지연 등)
            return True
        return False
        
    def is_broken(self, character) -> bool:
        """Break 상태인지 확인 - 명시적으로 설정된 상태만"""
        return getattr(character, 'is_broken_state', False)
        
    def clear_break_state(self, character):
        """Break 상태 해제 - 턴 시작 시 호출"""
        if hasattr(character, 'is_broken_state'):
            character.is_broken_state = False


class BattleEffects:
    """배틀 이펙트 시스템"""
    
    @staticmethod
    def show_brave_attack_effect(attacker_name: str, skill_name: str, damage: int):
        """Brave 공격 이펙트"""
        print(f"\n{'='*60}")
        print(f"💫 {attacker_name}의 {skill_name}!")
        print(f"⚔️  Brave 데미지: {damage}")
        BattleEffects._animate_damage(damage, "💥")
        print(f"{'='*60}")
        
    @staticmethod
    def show_hp_attack_effect(attacker_name: str, skill_name: str, hp_damage: int, wound_damage: int):
        """HP 공격 이펙트"""
        print(f"\n{'='*60}")
        print(f"🌟 {attacker_name}의 {skill_name}!")
        print(f"💀 HP 데미지: {hp_damage}")
        print(f"🩸 상처 데미지: {wound_damage}")
        BattleEffects._animate_damage(hp_damage, "💥💥💥")
        print(f"{'='*60}")
        
    @staticmethod
    def show_break_effect(target_name: str):
        """Break 이펙트"""
        print(f"\n{target_name} BREAK!")
        time.sleep(0.5)
        
    @staticmethod
    def show_brave_gain_effect(character_name: str, gained: int, total: int):
        """Brave 획득 이펙트"""
        print(f"✨ {character_name} Brave {gained} (총 {total})")
        
    @staticmethod
    def _animate_damage(damage: int, effect_char: str):
        """데미지 애니메이션"""
        if damage < 500:
            print(f"{effect_char} 약한 타격!")
        elif damage < 1500:
            print(f"{effect_char * 2} 강한 타격!")
        elif damage < 3000:
            print(f"{effect_char * 3} 치명적 타격!")
        else:
            print(f"{effect_char * 4} 극딜!!!")
        time.sleep(0.3)


class BraveSkillDatabase:
    """Brave 스킬 데이터베이스 (대폭 확장)"""
    
    @staticmethod
    def get_character_skills(character_class: str) -> List[BraveSkill]:
        """캐릭터 클래스별 스킬 반환 (MP 비용 포함) - 대폭 확장"""
        skill_sets = {
            "전사": [
                # 기본 공격
                BraveSkill("검 공격", BraveAttackType.BRAVE, 1.0, mp_cost=0, description="[BRV] 기본적인 검 공격"),
                # 기본 스킬
                BraveSkill("강타", BraveAttackType.BRAVE, 1.5, mp_cost=5, description="[BRV] 강력한 일격으로 Brave를 크게 증가 (1.5배 데미지, MP 5 소모)"),
                BraveSkill("분노의 일격", BraveAttackType.HP, 0.0, 1.8, mp_cost=12, description="[HP] 분노로 강화된 HP 공격 (1.8배 데미지, 축적된 BRV로 HP 피해, MP 12 소모)"),
                BraveSkill("방어 태세", BraveAttackType.BRAVE, 0.5, mp_cost=8, description="[BRV] 방어력 향상, 받는 피해 감소 (0.5배 약한 공격, MP 8 소모)"),
                
                # 고급 스킬
                BraveSkill("연속 공격", BraveAttackType.BRAVE, 0.8, mp_cost=15, description="[BRV] 3번 연속 공격으로 Brave 축적 (0.8배×3회, MP 15 소모)"),
                BraveSkill("도발", BraveAttackType.BRAVE, 0.3, mp_cost=6, description="[BRV] 적의 공격을 집중시키고 적 Brave 감소 (0.3배 약한 공격, MP 6 소모)"),
                BraveSkill("광전사의 분노", BraveAttackType.HP, 0.0, 2.5, mp_cost=25, description="[HP공격] 현재 HP의 30%를 소모하여 강력한 피해 (2.5배), 희생한 HP만큼 추가 데미지 보너스", hp_sacrifice_rate=0.30),
                BraveSkill("대지 강타", BraveAttackType.BRAVE, 1.2, mp_cost=10, description="[BRV] 땅을 강타해 광역 Brave 피해 (1.2배 데미지, 광역 공격, MP 10 소모)"),
                BraveSkill("불굴의 의지", BraveAttackType.BRAVE, 0.0, mp_cost=20, description="[특수] Break 상태에서 즉시 회복 (MP 20 소모)"),
                BraveSkill("전사의 외침", BraveAttackType.BRAVE, 0.0, mp_cost=15, description="[버프] 아군 전체의 공격력 증가 (MP 15 소모)"),
                BraveSkill("무쌍난무", BraveAttackType.HP, 0.0, 3.0, 1, mp_cost=40, description="[궁극기] 모든 적을 베는 최강 광역 공격 (3.0배 데미지, 1회 사용, MP 40 소모)")
            ],
            
            "마법사": [
                # 기본 공격
                BraveSkill("마법탄", BraveAttackType.BRAVE, 1.0, mp_cost=0, description="[BRV] 기본적인 마법 공격"),
                # 원소 마법
                BraveSkill("파이어볼", BraveAttackType.BRAVE, 1.3, mp_cost=8, description="화염구로 마법 Brave 피해"),
                BraveSkill("아이스 스파이크", BraveAttackType.BRAVE, 1.1, mp_cost=7, description="얼음 가시로 적을 둔화"),
                BraveSkill("라이트닝 볼트", BraveAttackType.HP, 0.0, 1.5, mp_cost=15, description="번개로 HP 직접 피해"),
                
                # 고급 마법
                BraveSkill("메테오", BraveAttackType.HP, 0.0, 2.2, 2, mp_cost=30, description="거대한 운석 낙하"),
                BraveSkill("블리자드", BraveAttackType.BRAVE, 1.0, mp_cost=20, description="광역 얼음 폭풍"),
                BraveSkill("체인 라이트닝", BraveAttackType.BRAVE, 0.9, mp_cost=18, description="연쇄 번개 공격"),
                BraveSkill("매직 미사일", BraveAttackType.BRAVE, 0.7, mp_cost=5, description="마법 화살 연속 발사"),
                BraveSkill("텔레포트", BraveAttackType.BRAVE, 0.0, mp_cost=12, description="순간이동으로 회피"),
                BraveSkill("마나 드레인", BraveAttackType.BRAVE, 0.8, mp_cost=10, description="적의 MP 흡수"),
                BraveSkill("엘리멘탈 스톰", BraveAttackType.HP, 0.0, 1.8, 3, mp_cost=25, description="모든 속성 융합 폭풍"),
                BraveSkill("아르카눔", BraveAttackType.HP, 0.0, 3.5, 1, mp_cost=50, description="금지된 궁극 마법")
            ],
            
            "궁수": [
                # 기본 공격
                BraveSkill("사격", BraveAttackType.BRAVE, 1.0, mp_cost=0, description="[BRV] 기본적인 활 사격"),
                # 기본 사격
                BraveSkill("정확한 사격", BraveAttackType.BRAVE, 1.4, mp_cost=6, description="정밀한 조준으로 높은 Brave 피해"),
                BraveSkill("연발사격", BraveAttackType.BRAVE, 0.6, mp_cost=12, description="빠른 연속 화살"),
                BraveSkill("관통사격", BraveAttackType.HP, 0.0, 1.6, mp_cost=18, description="적을 관통하는 강력한 화살"),
                
                # 특수 화살
                BraveSkill("독화살", BraveAttackType.BRAVE, 1.0, mp_cost=10, description="독을 바른 화살로 지속 피해"),
                BraveSkill("폭발화살", BraveAttackType.HP, 0.0, 1.4, mp_cost=16, description="폭발하는 화살로 광역 피해"),
                BraveSkill("얼음화살", BraveAttackType.BRAVE, 1.1, mp_cost=8, description="적을 얼려 행동 방해"),
                BraveSkill("추적화살", BraveAttackType.BRAVE, 1.3, mp_cost=14, description="반드시 명중하는 유도 화살"),
                BraveSkill("천공의 화살", BraveAttackType.HP, 0.0, 2.0, 4, mp_cost=22, description="하늘에서 무수한 화살"),
                BraveSkill("바람의 가호", BraveAttackType.BRAVE, 0.0, mp_cost=15, description="회피율과 속도 증가"),
                BraveSkill("신궁의 일격", BraveAttackType.HP, 0.0, 2.8, 2, mp_cost=35, description="절대 명중하는 필살 화살")
            ],
            
            "도적": [
                # 기본 공격
                BraveSkill("단검 공격", BraveAttackType.BRAVE, 1.0, mp_cost=0, description="[BRV] 기본적인 단검 공격"),
                # 암살 기술
                BraveSkill("백스탭", BraveAttackType.BRAVE, 1.8, mp_cost=8, description="뒤에서 기습으로 큰 Brave 피해"),
                BraveSkill("암살", BraveAttackType.HP, 0.0, 2.5, mp_cost=20, description="치명적인 급소 공격"),
                BraveSkill("은신", BraveAttackType.BRAVE, 0.0, mp_cost=12, description="모습을 감춰 다음 공격 강화"),
                
                # 기교 기술
                BraveSkill("독 바르기", BraveAttackType.BRAVE, 0.5, mp_cost=5, description="무기에 독 발라 지속 피해"),
                BraveSkill("연막탄", BraveAttackType.BRAVE, 0.0, mp_cost=10, description="연막으로 적 명중률 감소"),
                BraveSkill("그림자 분신", BraveAttackType.BRAVE, 1.0, mp_cost=18, description="분신으로 동시 공격"),
                BraveSkill("절도", BraveAttackType.BRAVE, 0.3, mp_cost=15, description="적의 아이템이나 버프 훔치기"),
                BraveSkill("치명타", BraveAttackType.HP, 0.0, 3.0, 3, mp_cost=25, description="확률적 엄청난 피해"),
                BraveSkill("그림자 이동", BraveAttackType.BRAVE, 0.0, mp_cost=8, description="그림자 통해 순간이동"),
                BraveSkill("섀도우 킬", BraveAttackType.HP, 0.0, 4.0, 1, mp_cost=45, description="그림자에서 나타나는 일격필살")
            ],
            
            "성기사": [
                # 기본 공격
                BraveSkill("성검 공격", BraveAttackType.BRAVE, 1.0, mp_cost=0, description="[BRV] 기본적인 성검 공격"),
                # 성스러운 공격
                BraveSkill("성스러운 일격", BraveAttackType.BRAVE, 1.3, mp_cost=10, description="신성한 힘이 깃든 공격"),
                BraveSkill("심판의 빛", BraveAttackType.HP, 0.0, 1.7, mp_cost=20, description="악을 심판하는 성스러운 빛"),
                BraveSkill("엑소시즘", BraveAttackType.HP, 0.0, 2.5, mp_cost=22, description="언데드와 악마 특효 퇴마술"),
                
                # 지원 마법 (스탯 기반 회복)
                BraveSkill("치유술", BraveAttackType.BRAVE, 0.0, mp_cost=12, description="마법력 기반으로 아군 HP 회복"),
                BraveSkill("축복", BraveAttackType.BRAVE, 0.0, mp_cost=15, description="아군 전체 능력치 향상"),
                BraveSkill("신의 가호", BraveAttackType.BRAVE, 0.0, mp_cost=18, description="상태이상 치유와 보호막"),
                BraveSkill("성역", BraveAttackType.BRAVE, 0.0, mp_cost=25, description="신성한 결계로 광역 보호"),
                BraveSkill("부활술", BraveAttackType.BRAVE, 0.0, mp_cost=40, description="쓰러진 아군 되살리기"),
                BraveSkill("천벌", BraveAttackType.HP, 0.0, 3.0, 2, mp_cost=35, description="하늘에서 내리는 신의 벌"),
                BraveSkill("신의 심판", BraveAttackType.HP, 0.0, 5.0, 1, mp_cost=60, description="절대적 정의의 심판")
            ],
            
            "검사": [
                BraveSkill("검격", BraveAttackType.BRAVE, 1.2, mp_cost=2, description="기본 검 공격"),
                BraveSkill("연속베기", BraveAttackType.BRAVE, 0.8, mp_cost=5, description="2회 연속 공격"),
                BraveSkill("성검 베기", BraveAttackType.HP, 0.0, 1.5, 3, mp_cost=15, description="강력한 HP 공격"),
                BraveSkill("일섬", BraveAttackType.HP, 0.0, 2.5, 2, mp_cost=25, description="한 번의 베기로 모든 것을 가름"),
            ],
            
            "성직자": [
                BraveSkill("성스러운 빛", BraveAttackType.BRAVE, 1.0, mp_cost=5, description="치유와 공격"),
                BraveSkill("축복", BraveAttackType.BRAVE, 0.8, mp_cost=7, description="버프 효과"),
                BraveSkill("심판", BraveAttackType.HP, 0.0, 1.8, 2, mp_cost=20, description="신성한 심판"),
                BraveSkill("대치유술", BraveAttackType.BRAVE, 0.0, mp_cost=15, description="마법력 기반 강력한 회복 마법"),
            ],
            
            "암흑기사": [
                BraveSkill("암흑 검격", BraveAttackType.BRAVE, 1.4, mp_cost=8, description="어둠의 힘이 깃든 검격"),
                BraveSkill("생명 흡수", BraveAttackType.HP, 0.0, 1.3, mp_cost=15, description="적의 생명력을 흡수"),
                BraveSkill("저주", BraveAttackType.BRAVE, 0.6, mp_cost=10, description="적에게 저주를 걸어 약화"),
                BraveSkill("다크 익스플로전", BraveAttackType.HP, 0.0, 2.2, 3, mp_cost=30, description="어둠의 폭발"),
                BraveSkill("데스 나이트", BraveAttackType.HP, 0.0, 3.5, 1, mp_cost=50, description="죽음의 기사 소환")
            ],
            
            "몽크": [
                BraveSkill("연타", BraveAttackType.BRAVE, 0.7, mp_cost=3, description="빠른 주먹 연타"),
                BraveSkill("기공탄", BraveAttackType.BRAVE, 1.3, mp_cost=8, description="기를 모아 발사"),
                BraveSkill("철권", BraveAttackType.HP, 0.0, 1.8, mp_cost=18, description="철같이 단단한 주먹"),
                BraveSkill("천지권", BraveAttackType.HP, 0.0, 2.8, 2, mp_cost=35, description="천지를 가르는 주먹"),
                BraveSkill("용권 난무", BraveAttackType.HP, 0.0, 4.2, 1, mp_cost=55, description="용의 힘이 깃든 최강 권법")
            ]
        }
        
        return skill_sets.get(character_class, [
            BraveSkill("기본 공격", BraveAttackType.BRAVE, 1.0, mp_cost=0, description="기본 공격")
        ])
        
    @staticmethod
    def get_enemy_skills() -> List[BraveSkill]:
        """적 전용 스킬들"""
        return [
            BraveSkill("할퀴기", BraveAttackType.BRAVE, 0.9, description="기본 공격"),
            BraveSkill("강타", BraveAttackType.BRAVE, 1.3, description="강한 공격"),
            BraveSkill("필살기", BraveAttackType.HP, 0.0, 1.2, 1, "적의 필살기"),
        ]


class BraveMixin:
    """Brave 시스템을 위한 믹스인 클래스"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brave_manager = BraveManager()
        self.brave_skills = []  # 캐릭터별 Brave 스킬 목록
        # brave_points는 캐릭터 초기화 시 int_brv 값으로 설정됨
        
    def initialize_brave_points(self):
        """Brave 포인트를 INT BRV 값으로 초기화"""
        self.brave_points = self.brave_manager.get_initial_brave(self)
        
    def gain_brave(self, amount: int) -> int:
        """Brave 포인트 획득 (효율성 적용) - 아군과 적군 동일한 기본 흡수율"""
        try:
            amount = max(0, int(amount))
            efficiency = getattr(self, 'brave_bonus_rate', 1.0)
            actual_gain = int(amount * efficiency)
            
            # 기본 BRV 흡수율은 아군과 적군 동일 (기존 2.5배 보너스 제거)
            # if hasattr(self, 'character_class') and self.character_class != "Enemy":
            #     actual_gain = int(actual_gain * 2.5)
            
            max_brv = self.brave_manager.get_max_brave(self)
            old_brave = self.brave_points
            self.brave_points = min(self.brave_points + actual_gain, max_brv)
            
            return self.brave_points - old_brave
        except Exception:
            return 0
            
    def lose_brave(self, amount: int) -> int:
        """Brave 포인트 손실 (저항력 적용)"""
        try:
            amount = max(0, int(amount))
            resistance = getattr(self, 'brv_loss_resistance', 1.0)
            actual_loss = int(amount / resistance)
            
            old_brave = self.brave_points
            self.brave_points = max(0, self.brave_points - actual_loss)
            
            return old_brave - self.brave_points
        except Exception:
            return 0
        
    def add_brave_points(self, amount: int):
        """Brave 포인트 추가 (MAX BRV 제한 적용)"""
        self.gain_brave(amount)
        
    def consume_brave_points(self) -> int:
        """Brave 포인트 소모 (HP 공격 시) - 오페라 옴니아 방식"""
        consumed = self.brave_points
        
        # HP 공격 후 BRV는 0이 되고 끝 (INT BRV 회복은 턴 시작 시)
        self.brave_points = 0
        
        return consumed
        
    def recover_int_brv_on_turn_start(self):
        """턴 시작 시 INT BRV 회복 (BREAK 상태는 더 오래 유지)"""
        # BREAK 상태일 때는 BRV 회복을 지연시킴
        if hasattr(self, 'is_broken_state') and self.is_broken_state:
            # BREAK 턴 카운터 증가
            if not hasattr(self, 'break_turn_count'):
                self.break_turn_count = 0
            self.break_turn_count += 1
            
            # BREAK 상태를 1턴 동안만 지속 (BREAK된 본인 기준)
            if self.break_turn_count >= 1:
                # 1턴 후에 BRV 회복 및 BREAK 해제
                int_brv = self.brave_manager.get_initial_brave(self)
                self.brave_points = int_brv
                self.is_broken_state = False
                self.break_turn_count = 0
                print(f"💫 {self.name}의 BREAK 상태가 해제되고 BRV가 회복되었습니다!")
                return int_brv
            else:
                # 아직 BREAK 상태 유지
                print(f"💀 {self.name}은(는) BREAK 상태입니다! (본인 턴에 해제됨)")
                return 0
        
        # 일반적인 경우: BRV가 0일 때만 회복
        if self.brave_points <= 0:
            int_brv = self.brave_manager.get_initial_brave(self)
            self.brave_points = int_brv
            return int_brv
        return 0
        
    def regenerate_brave(self):
        """Brave 자동 회복"""
        if hasattr(self, 'brv_regen'):
            self.gain_brave(self.brv_regen)
        
    def is_broken(self) -> bool:
        """Break 상태 확인 - 명시적으로 설정된 상태만"""
        return getattr(self, 'is_broken_state', False)
        
    def apply_break_if_needed(self) -> bool:
        """BREAK 적용 - BRV가 0이 되었을 때 (연속 BREAK 방지)"""
        # 이미 BREAK 상태면 추가 BREAK 방지
        if hasattr(self, 'is_broken_state') and self.is_broken_state:
            print(f"🛡️ {self.name}은(는) 이미 BREAK 상태이므로 추가 BREAK를 방지합니다!")
            return False
        
        self.is_broken_state = True
        
        # BREAK 시 ATB 게이지 초기화
        if hasattr(self, 'atb_gauge'):
            self.atb_gauge = 0
            print(f"💥 {self.name}의 ATB 게이지가 초기화되었습니다!")
        
        return True
        
    def clear_break_state(self):
        """Break 상태 해제 - 턴 시작 시 호출"""
        self.is_broken_state = False
        
    def get_brave_efficiency(self) -> float:
        """Brave 효율성 계산 (현재 Brave / MAX BRV)"""
        max_brv = self.brave_manager.get_max_brave(self)
        return self.brave_points / max_brv if max_brv > 0 else 0.0
        
    def get_available_brave_skills(self) -> List[BraveSkill]:
        """사용 가능한 Brave 스킬 반환"""
        if not self.brave_skills:
            # 캐릭터 클래스에 따른 스킬 로드
            class_name = getattr(self, 'character_class', '전사')
            self.brave_skills = BraveSkillDatabase.get_character_skills(class_name)
        return [skill for skill in self.brave_skills if skill.can_use()]
        
    def get_brave_skills(self) -> List[BraveSkill]:
        """모든 Brave 스킬 반환 (사용 불가능한 것 포함)"""
        if not self.brave_skills:
            class_name = getattr(self, 'character_class', '전사')
            self.brave_skills = BraveSkillDatabase.get_character_skills(class_name)
        return self.brave_skills
    
    def get_total_speed(self) -> int:
        """장비 보너스가 포함된 총 속도 (안전한 구현)"""
        base_speed = getattr(self, 'speed', 20)  # 기본값 20
        temp_bonus = getattr(self, 'temp_speed_bonus', 0)
        equipment_bonus = getattr(self, 'equipment_speed_bonus', 0)
        return base_speed + temp_bonus + equipment_bonus
