"""
개선된 캐릭터 생성 시스템
- 직업 선택
- 특성 선택 (최대 2개)
- 스탯 분배
- 이름 설정
"""

from typing import List, Dict, Optional, Tuple
from .character import Character
from .input_utils import KeyboardInput
from .trait_system import get_trait_system
from .new_skill_system import skill_system

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BRIGHT_WHITE = '\033[97m\033[1m'

class CharacterCreator:
    """캐릭터 생성 시스템"""
    
    def __init__(self):
        self.keyboard = KeyboardInput()
        self.trait_system = get_trait_system()
        
        # 직업별 설명
        self.class_descriptions = {
            "전사": "⚔️ 균형잡힌 근접 전투의 달인 | 높은 HP와 방어력",
            "마법사": "🔮 강력한 마법 공격의 전문가 | 높은 마법력, 낮은 HP",
            "성직자": "✨ 치유와 지원의 성자 | 회복 마법과 버프 전문",
            "도적": "🗡️ 빠르고 치명적인 암살자 | 높은 크리티컬과 속도",
            "궁수": "🏹 원거리 정밀 사격수 | 정확한 공격과 특수 화살",
            "기사": "🛡️ 파티를 지키는 수호자 | 최고의 방어력과 도발",
            "무당": "🌿 자연과 정령의 힘 | 치유와 저주의 균형",
            "용기사": "🐉 용의 힘을 다루는 전사 | 강력한 화염 공격",
            "사무라이": "⚡ 일섬의 달인 | 빠른 연속 공격과 집중력",
            "네크로맨서": "💀 죽음을 다루는 마법사 | 언데드 소환과 흡수"
        }
        
        # 직업별 기본 스탯 (레벨 1 기준)
        self.class_base_stats = {
            "전사": {"hp": 120, "mp": 40, "atk": 18, "def": 16, "mag": 8, "spd": 12},
            "마법사": {"hp": 80, "mp": 80, "atk": 10, "def": 8, "mag": 22, "spd": 10},
            "성직자": {"hp": 100, "mp": 60, "atk": 12, "def": 12, "mag": 18, "spd": 11},
            "도적": {"hp": 90, "mp": 30, "atk": 20, "def": 10, "mag": 6, "spd": 18},
            "궁수": {"hp": 95, "mp": 40, "atk": 17, "def": 11, "mag": 8, "spd": 15},
            "기사": {"hp": 140, "mp": 35, "atk": 15, "def": 20, "mag": 6, "spd": 8},
            "무당": {"hp": 110, "mp": 70, "atk": 13, "def": 13, "mag": 19, "spd": 12},
            "용기사": {"hp": 130, "mp": 50, "atk": 19, "def": 17, "mag": 14, "spd": 10},
            "사무라이": {"hp": 105, "mp": 45, "atk": 21, "def": 14, "mag": 9, "spd": 16},
            "네크로맨서": {"hp": 85, "mp": 75, "atk": 11, "def": 9, "mag": 20, "spd": 11}
        }
    
    def create_character(self) -> Optional[Character]:
        """캐릭터 생성 메인 플로우"""
        print(f"\n{BRIGHT_WHITE}{'='*70}")
        print(f"🎭 캐릭터 생성 시스템")
        print(f"{'='*70}{RESET}")
        
        # 1단계: 직업 선택
        character_class = self._select_class()
        if not character_class:
            return None
        
        # 2단계: 이름 입력
        name = self._input_name()
        if not name:
            return None
        
        # 3단계: 특성 선택 (최대 2개)
        selected_traits = self._select_traits()
        
        # 4단계: 스탯 분배 (추가 포인트 10점)
        final_stats = self._allocate_stats(character_class)
        
        # 5단계: 캐릭터 생성 확인
        character = self._create_final_character(name, character_class, selected_traits, final_stats)
        
        if character:
            self._show_character_summary(character)
        
        return character
    
    def _select_class(self) -> Optional[str]:
        """직업 선택"""
        classes = list(self.class_descriptions.keys())
        
        while True:
            print(f"\n{CYAN}🎯 직업을 선택하세요:{RESET}")
            print("-" * 50)
            
            for i, (class_name, description) in enumerate(self.class_descriptions.items(), 1):
                stats = self.class_base_stats[class_name]
                print(f"{i:2}. {class_name:8} | {description}")
                print(f"    📊 HP:{stats['hp']:3} MP:{stats['mp']:2} ATK:{stats['atk']:2} DEF:{stats['def']:2} MAG:{stats['mag']:2} SPD:{stats['spd']:2}")
                print()
            
            print(f"{len(classes)+1:2}. 취소")
            
            try:
                print(f"\n{YELLOW}선택 (1-{len(classes)}): {RESET}", end="", flush=True)
                choice = int(self.keyboard.get_key())
                
                if choice == len(classes) + 1:
                    return None
                elif 1 <= choice <= len(classes):
                    selected_class = classes[choice - 1]
                    print(f"\n{GREEN}✅ {selected_class}를 선택했습니다!{RESET}")
                    return selected_class
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
            except ValueError:
                print(f"{RED}숫자를 입력하세요.{RESET}")
            
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
    
    def _input_name(self) -> Optional[str]:
        """이름 입력"""
        print(f"\n{CYAN}📝 캐릭터 이름을 입력하세요:{RESET}")
        print("(한글/영문 2-10자, 취소하려면 'cancel' 입력)")
        
        while True:
            print(f"{YELLOW}이름: {RESET}", end="", flush=True)
            name = self.keyboard.get_string_input()
            
            if name.lower() == 'cancel':
                return None
            elif 2 <= len(name) <= 10:
                print(f"\n{GREEN}✅ '{name}' 으로 설정했습니다!{RESET}")
                return name
            else:
                print(f"{RED}이름은 2-10자여야 합니다.{RESET}")
    
    def _select_traits(self) -> List:
        """특성 선택 (최대 2개)"""
        print(f"\n{CYAN}🌟 특성을 선택하세요 (최대 2개, 선택 안해도 됨):{RESET}")
        
        # 사용 가능한 특성 목록 가져오기
        available_traits = self.trait_system.get_available_traits()
        
        if not available_traits:
            print(f"{YELLOW}선택 가능한 특성이 없습니다.{RESET}")
            self.keyboard.wait_for_key("아무 키나 눌러 계속...")
            return []
        
        selected_traits = []
        
        while len(selected_traits) < 2:
            print(f"\n{WHITE}현재 선택된 특성: {len(selected_traits)}/2{RESET}")
            if selected_traits:
                for trait in selected_traits:
                    print(f"  ✓ {GREEN}{trait.name}{RESET} - {trait.description}")
            
            print(f"\n{CYAN}사용 가능한 특성:{RESET}")
            print("-" * 50)
            
            for i, trait in enumerate(available_traits, 1):
                if trait not in selected_traits:
                    print(f"{i:2}. {trait.name}")
                    print(f"    📝 {trait.description}")
                    if hasattr(trait, 'effect_description'):
                        print(f"    ⚡ {trait.effect_description}")
                    print()
            
            print(f"{len(available_traits)+1:2}. 선택 완료")
            print(f"{len(available_traits)+2:2}. 취소")
            
            try:
                print(f"\n{YELLOW}선택 (1-{len(available_traits)+2}): {RESET}", end="", flush=True)
                choice = int(self.keyboard.get_key())
                
                if choice == len(available_traits) + 1:  # 선택 완료
                    break
                elif choice == len(available_traits) + 2:  # 취소
                    return []
                elif 1 <= choice <= len(available_traits):
                    trait = available_traits[choice - 1]
                    if trait not in selected_traits:
                        selected_traits.append(trait)
                        print(f"\n{GREEN}✅ '{trait.name}' 특성을 선택했습니다!{RESET}")
                    else:
                        print(f"{YELLOW}이미 선택된 특성입니다.{RESET}")
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
            except ValueError:
                print(f"{RED}숫자를 입력하세요.{RESET}")
            
            if len(selected_traits) < 2:
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        
        print(f"\n{GREEN}🌟 특성 선택 완료! {len(selected_traits)}개 선택됨{RESET}")
        return selected_traits
    
    def _allocate_stats(self, character_class: str) -> Dict[str, int]:
        """스탯 분배 (추가 포인트 10점)"""
        base_stats = self.class_base_stats[character_class].copy()
        bonus_points = 10
        allocated_stats = base_stats.copy()
        
        print(f"\n{CYAN}📊 스탯 분배 (추가 포인트: {bonus_points}점){RESET}")
        print("스탯을 올리고 싶으면 해당 번호를 입력하세요.")
        
        while bonus_points > 0:
            print(f"\n{WHITE}현재 스탯:{RESET}")
            print(f"1. HP  : {allocated_stats['hp']:3} (+{allocated_stats['hp'] - base_stats['hp']:2})")
            print(f"2. MP  : {allocated_stats['mp']:3} (+{allocated_stats['mp'] - base_stats['mp']:2})")
            print(f"3. ATK : {allocated_stats['atk']:3} (+{allocated_stats['atk'] - base_stats['atk']:2})")
            print(f"4. DEF : {allocated_stats['def']:3} (+{allocated_stats['def'] - base_stats['def']:2})")
            print(f"5. MAG : {allocated_stats['mag']:3} (+{allocated_stats['mag'] - base_stats['mag']:2})")
            print(f"6. SPD : {allocated_stats['spd']:3} (+{allocated_stats['spd'] - base_stats['spd']:2})")
            print(f"\n{YELLOW}남은 포인트: {bonus_points}점{RESET}")
            print("7. 완료")
            
            try:
                print(f"\n{YELLOW}선택 (1-7): {RESET}", end="", flush=True)
                choice = int(self.keyboard.get_key())
                
                if choice == 7:  # 완료
                    break
                elif 1 <= choice <= 6:
                    stat_names = ['hp', 'mp', 'atk', 'def', 'mag', 'spd']
                    stat_name = stat_names[choice - 1]
                    
                    # 스탯 증가
                    if stat_name in ['hp', 'mp']:
                        increase = 5  # HP, MP는 5씩 증가
                    else:
                        increase = 1  # 나머지는 1씩 증가
                    
                    if bonus_points >= increase:
                        allocated_stats[stat_name] += increase
                        bonus_points -= increase
                        print(f"\n{GREEN}✅ {stat_name.upper()} +{increase}!{RESET}")
                    else:
                        print(f"{RED}포인트가 부족합니다! (필요: {increase}점){RESET}")
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
            except ValueError:
                print(f"{RED}숫자를 입력하세요.{RESET}")
            
            if bonus_points > 0:
                self.keyboard.wait_for_key("아무 키나 눌러 계속...")
        
        print(f"\n{GREEN}📊 스탯 분배 완료!{RESET}")
        return allocated_stats
    
    def _create_final_character(self, name: str, character_class: str, traits: List, stats: Dict[str, int]) -> Character:
        """최종 캐릭터 생성"""
        try:
            # Character 객체 생성
            character = Character(name, character_class)
            
            # 스탯 적용
            character.max_hp = stats['hp']
            character.current_hp = stats['hp']
            character.max_mp = stats['mp']
            character.current_mp = stats['mp']
            character.physical_attack = stats['atk']
            character.physical_defense = stats['def']
            character.magic_attack = stats['mag']
            character.magic_defense = stats['def']  # 물리 방어력과 동일
            character.speed = stats['spd']
            
            # 특성 적용
            if traits and hasattr(character, 'active_traits'):
                character.active_traits = traits
                # 특성 효과 적용
                for trait in traits:
                    if hasattr(trait, 'apply_effects'):
                        trait.apply_effects(character)
            
            # 레벨 1로 설정
            character.level = 1
            character.experience = 0
            
            print(f"\n{GREEN}✅ {name} 캐릭터가 생성되었습니다!{RESET}")
            return character
            
        except Exception as e:
            print(f"{RED}❌ 캐릭터 생성 중 오류: {e}{RESET}")
            return None
    
    def _show_character_summary(self, character: Character):
        """캐릭터 요약 정보 표시"""
        print(f"\n{BRIGHT_WHITE}{'='*50}")
        print(f"🎭 {character.name} 캐릭터 정보")
        print(f"{'='*50}{RESET}")
        
        print(f"{CYAN}직업:{RESET} {character.character_class}")
        print(f"{CYAN}레벨:{RESET} {character.level}")
        
        print(f"\n{YELLOW}📊 스탯:{RESET}")
        print(f"HP: {character.max_hp}  MP: {character.max_mp}")
        print(f"ATK: {character.physical_attack}  DEF: {character.physical_defense}")
        print(f"MAG: {character.magic_attack}  SPD: {character.speed}")
        
        if hasattr(character, 'active_traits') and character.active_traits:
            print(f"\n{MAGENTA}🌟 특성:{RESET}")
            for trait in character.active_traits:
                print(f"  • {trait.name} - {trait.description}")
        
        print(f"\n{GREEN}🎉 캐릭터 생성이 완료되었습니다!{RESET}")
        self.keyboard.wait_for_key("아무 키나 눌러 계속...")


# 전역 인스턴스
character_creator = CharacterCreator()

def get_character_creator():
    """캐릭터 생성기 인스턴스 반환"""
    return character_creator
