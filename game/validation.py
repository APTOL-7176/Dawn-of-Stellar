"""
게임 데이터 검증 시스템
버그를 최소화하기 위한 데이터 유효성 검사
"""

import traceback
from typing import Any, Dict, List, Tuple, Optional
from .character import Character
from .items import Item, ItemType, ItemRarity


class ValidationError(Exception):
    """검증 오류 예외"""
    pass


class GameValidator:
    """게임 데이터 검증 클래스"""
    
    @staticmethod
    def validate_character_data(char_data: Dict) -> Tuple[bool, List[str]]:
        """캐릭터 데이터 검증"""
        errors = []
        
        # 필수 필드 확인
        required_fields = ["name", "class", "description", "hp", "p_atk", "m_atk", 
                          "p_def", "m_def", "speed", "int_brv", "max_brv", 
                          "traits", "preferred_damage"]
        
        for field in required_fields:
            if field not in char_data:
                errors.append(f"필수 필드 누락: {field}")
            elif char_data[field] is None:
                errors.append(f"필드가 None임: {field}")
                
        if errors:
            return False, errors
            
        # 수치 범위 검증
        if char_data["hp"] <= 0 or char_data["hp"] > 500:
            errors.append(f"HP 범위 오류: {char_data['hp']} (1-500 사이여야 함)")
            
        if char_data["p_atk"] < 0 or char_data["p_atk"] > 50:
            errors.append(f"물리공격력 범위 오류: {char_data['p_atk']} (0-50 사이여야 함)")
            
        if char_data["m_atk"] < 0 or char_data["m_atk"] > 50:
            errors.append(f"마법공격력 범위 오류: {char_data['m_atk']} (0-50 사이여야 함)")
            
        if char_data["speed"] <= 0 or char_data["speed"] > 30:
            errors.append(f"속도 범위 오류: {char_data['speed']} (1-30 사이여야 함)")
            
        if char_data["int_brv"] <= 0 or char_data["int_brv"] > 1000:
            errors.append(f"INT BRV 범위 오류: {char_data['int_brv']} (1-1000 사이여야 함)")
            
        if char_data["max_brv"] <= 0 or char_data["max_brv"] > 10000:
            errors.append(f"MAX BRV 범위 오류: {char_data['max_brv']} (1-10000 사이여야 함)")
            
        # INT BRV가 MAX BRV보다 큰지 확인
        if char_data["int_brv"] > char_data["max_brv"]:
            errors.append(f"INT BRV({char_data['int_brv']})가 MAX BRV({char_data['max_brv']})보다 큼")
            
        # 선호 데미지 타입 검증
        if char_data["preferred_damage"] not in ["physical", "magic"]:
            errors.append(f"잘못된 데미지 타입: {char_data['preferred_damage']}")
            
        # 특성 검증
        if not isinstance(char_data["traits"], list):
            errors.append("traits는 리스트여야 함")
        elif len(char_data["traits"]) == 0:
            errors.append("최소 1개의 특성이 필요함")
            
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_item_data(item: Item) -> Tuple[bool, List[str]]:
        """아이템 데이터 검증"""
        errors = []
        
        # 기본 필드 검증
        if not item.name or item.name.strip() == "":
            errors.append("아이템 이름이 비어있음")
            
        if item.value < 0:
            errors.append(f"아이템 가격이 음수: {item.value}")
            
        if item.weight < 0:
            errors.append(f"아이템 무게가 음수: {item.weight}")
            
        # 타입별 특수 검증
        if item.item_type == ItemType.WEAPON:
            if not hasattr(item, 'stats') or 'physical_attack' not in item.stats:
                errors.append("무기에 공격력 스탯이 없음")
                
        elif item.item_type == ItemType.ARMOR:
            if not hasattr(item, 'stats') or ('physical_defense' not in item.stats and 'magic_defense' not in item.stats):
                errors.append("방어구에 방어력 스탯이 없음")
                
        # 스탯 범위 검증
        if hasattr(item, 'stats'):
            for stat_name, stat_value in item.stats.items():
                if not isinstance(stat_value, (int, float)):
                    errors.append(f"스탯 값이 숫자가 아님: {stat_name} = {stat_value}")
                elif stat_value < 0:
                    errors.append(f"스탯 값이 음수: {stat_name} = {stat_value}")
                elif stat_value > 100:  # 일반적인 스탯 상한
                    errors.append(f"스탯 값이 너무 큼: {stat_name} = {stat_value}")
                    
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_party(party: List[Character]) -> Tuple[bool, List[str]]:
        """파티 구성 검증"""
        errors = []
        
        if len(party) == 0:
            errors.append("파티가 비어있음")
        elif len(party) > 4:
            errors.append(f"파티 인원이 너무 많음: {len(party)}명 (최대 4명)")
            
        # 캐릭터별 검증
        for i, character in enumerate(party):
            if not isinstance(character, Character):
                errors.append(f"파티원 {i+1}이 Character 객체가 아님")
                continue
                
            if character.current_hp <= 0:
                errors.append(f"{character.name}의 HP가 0 이하")
                
            if character.max_hp <= 0:
                errors.append(f"{character.name}의 최대 HP가 0 이하")
                
            if not character.is_alive:
                errors.append(f"{character.name}이 사망 상태")
                
        # 중복 이름 검사
        names = [char.name for char in party]
        if len(names) != len(set(names)):
            errors.append("파티에 동일한 이름의 캐릭터가 있음")
            
        return len(errors) == 0, errors
    
    @staticmethod
    def safe_execute(func, *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """안전한 함수 실행 (예외 처리)"""
        try:
            result = func(*args, **kwargs)
            return True, result, None
        except Exception as e:
            error_msg = f"함수 실행 오류: {func.__name__}\n"
            error_msg += f"오류: {str(e)}\n"
            error_msg += f"Traceback:\n{traceback.format_exc()}"
            return False, None, error_msg
    
    @staticmethod
    def validate_combat_state(attacker: Character, target: Character) -> Tuple[bool, List[str]]:
        """전투 상태 검증"""
        errors = []
        
        if not attacker.is_alive:
            errors.append(f"공격자 {attacker.name}이 사망 상태")
            
        if not target.is_alive:
            errors.append(f"대상 {target.name}이 사망 상태")
            
        if attacker.current_hp <= 0:
            errors.append(f"공격자 {attacker.name}의 HP가 0 이하")
            
        if target.current_hp <= 0:
            errors.append(f"대상 {target.name}의 HP가 0 이하")
            
        if attacker.current_mp < 0:
            errors.append(f"공격자 {attacker.name}의 MP가 음수")
            
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_skill_use(character: Character, skill) -> Tuple[bool, List[str]]:
        """스킬 사용 가능성 검증"""
        errors = []
        
        if not skill.can_use(character):
            errors.append(f"스킬 {skill.name}을 사용할 수 없음")
            
        if character.current_mp < skill.mp_cost:
            errors.append(f"MP 부족: 필요 {skill.mp_cost}, 현재 {character.current_mp}")
            
        if skill.current_uses == 0:
            errors.append(f"스킬 {skill.name}의 사용 횟수 소진")
            
        return len(errors) == 0, errors


class SafetyWrapper:
    """안전한 실행을 위한 래퍼 클래스"""
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.error_log = []
        
    def safe_call(self, func, *args, **kwargs):
        """안전한 함수 호출"""
        success, result, error = GameValidator.safe_execute(func, *args, **kwargs)
        
        if not success and self.enable_logging:
            self.error_log.append(error)
            if len(self.error_log) > 100:  # 로그 크기 제한
                self.error_log.pop(0)
                
        return success, result, error
    
    def get_recent_errors(self, count: int = 10) -> List[str]:
        """최근 오류들 반환"""
        return self.error_log[-count:]
    
    def clear_errors(self):
        """오류 로그 초기화"""
        self.error_log.clear()


# 전역 안전 래퍼 인스턴스
game_safety = SafetyWrapper()
