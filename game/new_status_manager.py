#!/usr/bin/env python3
"""
새로운 상태이상 관리자 - new_skill_system.py와 호환
"""

from typing import List, Dict, Any, Optional
from game.new_skill_system import StatusType

class StatusEffect:
    """상태이상 효과"""
    
    def __init__(self, status_type: StatusType, duration: int, intensity: float = 1.0, source: str = "Unknown"):
        self.status_type = status_type
        self.duration = duration
        self.max_duration = duration
        self.intensity = intensity
        self.source = source
        self.stack_count = 1
        
    def get_icon(self) -> str:
        """상태이상 아이콘"""
        icons = {
            # 버프
            StatusType.BOOST_ATK: "⚔️",
            StatusType.BOOST_DEF: "🛡️", 
            StatusType.BOOST_SPD: "💨",
            StatusType.BLESSING: "✨",
            StatusType.REGENERATION: "💚",
            StatusType.HASTE: "🏃",
            StatusType.FOCUS: "🎯",
            StatusType.RAGE: "😡",
            StatusType.BARRIER: "🔵",
            StatusType.MAGIC_BARRIER: "🔮",
            
            # 디버프
            StatusType.REDUCE_ATK: "⚔️💔",
            StatusType.REDUCE_DEF: "🛡️💔",
            StatusType.REDUCE_SPD: "🐌",
            StatusType.VULNERABLE: "💀",
            StatusType.WEAKNESS: "😵",
            StatusType.CONFUSION: "💫",
            StatusType.TERROR: "😱",
            
            # 상태이상
            StatusType.POISON: "☠️",
            StatusType.BURN: "🔥",
            StatusType.FREEZE: "🧊", 
            StatusType.SHOCK: "⚡",
            StatusType.BLEED: "🩸",
            StatusType.CORRODE: "💚",
            StatusType.DISEASE: "🤢",
            StatusType.PETRIFY: "🗿",
            
            # 행동 제약
            StatusType.STUN: "💫",
            StatusType.SLEEP: "😴",
            StatusType.SILENCE: "🤐",
            StatusType.BLIND: "🙈",
            StatusType.PARALYZE: "⚡💥",
            StatusType.CHARM: "💖",
            StatusType.ROOT: "🌿",
            StatusType.SLOW: "🐌",
            
            # 특수
            StatusType.CURSE: "💀",
            StatusType.FEAR: "😨",
            StatusType.STEALTH: "👤",
            StatusType.BERSERK: "🔴",
            StatusType.COUNTER: "↩️",
            StatusType.VAMPIRE: "🧛",
        }
        return icons.get(self.status_type, "❓")

class NewStatusManager:
    """새로운 상태이상 관리자"""
    
    def __init__(self):
        self.status_effects: List[StatusEffect] = []
        
    def add_status(self, status_effect: StatusEffect) -> bool:
        """상태이상 추가"""
        existing = self.get_status(status_effect.status_type)
        
        if existing:
            # 같은 상태이상이 있으면 더 강한 것으로 덮어쓰기
            if status_effect.intensity > existing.intensity:
                self.status_effects.remove(existing)
                self.status_effects.append(status_effect)
                return True
            else:
                # 지속시간만 갱신
                existing.duration = max(existing.duration, status_effect.duration)
                return False
        else:
            self.status_effects.append(status_effect)
            return True
    
    def remove_status(self, status_type: StatusType) -> bool:
        """상태이상 제거"""
        for effect in self.status_effects[:]:
            if effect.status_type == status_type:
                self.status_effects.remove(effect)
                return True
        return False
    
    def get_status(self, status_type: StatusType) -> Optional[StatusEffect]:
        """특정 상태이상 반환"""
        for effect in self.status_effects:
            if effect.status_type == status_type:
                return effect
        return None
    
    def has_status(self, status_type: StatusType) -> bool:
        """상태이상 보유 여부"""
        return self.get_status(status_type) is not None
    
    def process_turn_effects(self) -> List[str]:
        """턴 처리 - 메서드 이름 유지 (호환성)"""
        messages = []
        
        if not self.status_effects:
            return messages
        
        # 상태이상 지속시간 감소 및 만료 처리
        for effect in self.status_effects[:]:
            effect.duration -= 1
            
            if effect.duration <= 0:
                self.status_effects.remove(effect)
                messages.append(f"{effect.status_type.value} 효과가 해제되었습니다.")
        
        return messages
    
    def get_stat_modifiers(self) -> Dict[str, float]:
        """상태이상이 스탯에 미치는 영향"""
        modifiers = {
            "attack": 1.0, "defense": 1.0, "speed": 1.0,
            "accuracy": 1.0, "evasion": 1.0, "magic_power": 1.0
        }
        
        for effect in self.status_effects:
            intensity = effect.intensity
            
            # 버프 효과
            if effect.status_type == StatusType.BOOST_ATK:
                modifiers["attack"] *= (1.0 + 0.3 * intensity)
            elif effect.status_type == StatusType.BOOST_DEF:
                modifiers["defense"] *= (1.0 + 0.3 * intensity)
            elif effect.status_type == StatusType.BOOST_SPD:
                modifiers["speed"] *= (1.0 + 0.3 * intensity)
            elif effect.status_type == StatusType.BOOST_ACCURACY:
                modifiers["accuracy"] *= (1.0 + 0.2 * intensity)
            elif effect.status_type == StatusType.BLESSING:
                for key in modifiers:
                    modifiers[key] *= (1.0 + 0.2 * intensity)
            
            # 디버프 효과
            elif effect.status_type == StatusType.REDUCE_ATK:
                modifiers["attack"] *= (1.0 - 0.3 * intensity)
            elif effect.status_type == StatusType.REDUCE_DEF:
                modifiers["defense"] *= (1.0 - 0.3 * intensity)
            elif effect.status_type == StatusType.REDUCE_SPD:
                modifiers["speed"] *= (1.0 - 0.3 * intensity)
            elif effect.status_type == StatusType.VULNERABLE:
                modifiers["defense"] *= (1.0 - 0.5 * intensity)
            elif effect.status_type == StatusType.WEAKNESS:
                modifiers["attack"] *= (1.0 - 0.4 * intensity)
            elif effect.status_type == StatusType.CURSE:
                for key in modifiers:
                    modifiers[key] *= (1.0 - 0.2 * intensity)
            
            # 특수 효과
            elif effect.status_type == StatusType.HASTE:
                modifiers["speed"] *= (1.0 + 0.5 * intensity)
            elif effect.status_type == StatusType.SLOW:
                modifiers["speed"] *= (1.0 - 0.5 * intensity)
            elif effect.status_type == StatusType.BLIND:
                modifiers["accuracy"] *= (1.0 - 0.7 * intensity)
            elif effect.status_type == StatusType.FOCUS:
                modifiers["accuracy"] *= (1.0 + 0.4 * intensity)
        
        return modifiers
    
    def can_act(self) -> bool:
        """행동 가능 여부"""
        blocking_statuses = [
            StatusType.STUN, StatusType.SLEEP, StatusType.PETRIFY,
            StatusType.FREEZE, StatusType.PARALYZE
        ]
        
        for effect in self.status_effects:
            if effect.status_type in blocking_statuses:
                return False
        return True
    
    def can_use_magic(self) -> bool:
        """마법 사용 가능 여부"""
        magic_blocking = [StatusType.SILENCE]
        
        for effect in self.status_effects:
            if effect.status_type in magic_blocking:
                return False
        return True
    
    def get_status_display(self) -> str:
        """상태이상 표시용 문자열"""
        if not self.status_effects:
            return ""
        
        icons = []
        for effect in self.status_effects:
            icon = effect.get_icon()
            if effect.stack_count > 1:
                icon += f"x{effect.stack_count}"
            icons.append(icon)
        
        return " ".join(icons)
    
    def clear_all(self):
        """모든 상태이상 제거"""
        self.status_effects.clear()
    
    def get_status_list(self) -> List[StatusEffect]:
        """상태이상 리스트 반환"""
        return self.status_effects.copy()
    
    def get_active_effects(self) -> List[str]:
        """활성 상태이상 이름 목록 반환"""
        return [effect.status_type.value for effect in self.status_effects]

# 편의 함수들
def create_status_effect(status_type: StatusType, duration: int = 5, intensity: float = 1.0, source: str = "Unknown") -> StatusEffect:
    """상태이상 효과 생성"""
    return StatusEffect(status_type, duration, intensity, source)

# 호환성을 위한 별칭
StatusManager = NewStatusManager
