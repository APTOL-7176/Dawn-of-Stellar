"""
ASCII 기반 효과음 및 시각 효과 시스템
"""

import time
import random
from typing import List


class ASCIISoundEffects:
    """ASCII 기반 효과음 표현"""
    
    @staticmethod
    def play_brave_attack_sound():
        """Brave 공격 효과음"""
        # Brave 공격 효과음 재생 (의성어 제거)
        time.sleep(0.2)
        
    @staticmethod
    def play_hp_attack_sound():
        """HP 공격 효과음"""
        # HP 공격 효과음 재생 (의성어 제거)
        time.sleep(0.3)
        
    @staticmethod
    def play_break_sound():
        """Break 효과음"""
        # 효과음 재생 (의성어 제거)
        time.sleep(0.5)
        
    @staticmethod
    def play_critical_sound():
        """크리티컬 효과음"""
        # 크리티컬 효과음 재생 (의성어 제거)
        time.sleep(0.4)
        
    @staticmethod
    def play_heal_sound():
        """치유 효과음"""
        effects = [
            "♪ 킹~ ✨",
            "♪ 포와~ 💚",
            "♪ 샤라랑~ 🌟"
        ]
        print(random.choice(effects))
        time.sleep(0.2)
        
    @staticmethod
    def play_menu_sound():
        """메뉴 효과음"""
        # 메뉴 효과음 재생 (의성어 제거)
        pass
        
    @staticmethod
    def play_level_up_sound():
        """레벨업 효과음"""
        # 레벨업 효과음 재생 (의성어 제거)
        time.sleep(0.5)
        
    @staticmethod
    def play_item_get_sound():
        """아이템 획득 효과음"""
        # 아이템 획득 효과음 재생 (의성어 제거)
        time.sleep(0.2)
        
    @staticmethod
    def play_magic_sound():
        """마법 효과음"""
        # 마법 효과음 재생 (의성어 제거)
        time.sleep(0.3)


class ASCIIVisualEffects:
    """ASCII 기반 시각 효과"""
    
    @staticmethod
    def show_damage_numbers(damage: int, is_critical: bool = False):
        """데미지 수치 표시 - 제거됨"""
        pass  # 더 이상 출력하지 않음
            
    @staticmethod
    def show_heal_numbers(heal: int):
        """회복 수치 표시"""
        print(f"    💚 +{heal:,} 💚")
        
    @staticmethod
    def show_brave_gain(amount: int, total: int):
        """Brave 획득 표시"""
        print(f"    ⚡ Brave {amount:,} (총 {total:,}) ⚡")
        
    @staticmethod
    def show_break_effect():
        """Break 이펙트"""
        # Break 이펙트 표시 (의성어/의태어 제거)
        pass
        
    @staticmethod
    def show_skill_activation(skill_name: str, character_name: str):
        """스킬 발동 이펙트"""
        print(f"\n✨ {character_name}의 『{skill_name}』! ✨")
        
    @staticmethod
    def animate_battle_transition():
        """전투 진입 애니메이션"""
        frames = [
            "⚔️ ════════════════ ⚔️",
            "⚔️ ═══ BATTLE! ═══ ⚔️", 
            "⚔️ ════════════════ ⚔️"
        ]
        
        for frame in frames:
            print(f"\n{frame}")
            time.sleep(0.3)
            
    @staticmethod
    def show_status_effect_icon(effect_name: str) -> str:
        """상태이상 아이콘 반환"""
        icons = {
            "독": "🟢",
            "화상": "🔥", 
            "빙결": "❄️",
            "기절": "😵",
            "방어": "🛡️",
            "가속": "💨",
            "강화": "⬆️",
            "약화": "⬇️",
            "회복": "💚"
        }
        return icons.get(effect_name, "❓")


class CombatTextAnimator:
    """전투 텍스트 애니메이션"""
    
    @staticmethod
    def typewriter_effect(text: str, delay: float = 0.03):
        """타이핑 효과"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
        
    @staticmethod
    def show_turn_indicator(character_name: str):
        """턴 표시 애니메이션"""
        border = "═" * (len(character_name) + 10)
        print(f"\n{border}")
        print(f"     {character_name}의 턴!")
        print(f"{border}")
        time.sleep(0.5)
        
    @staticmethod
    def show_victory_animation():
        """승리 애니메이션"""
        victory_frames = [
            "🎉 VICTORY! 🎉",
            "✨ 승리! ✨",
            "🏆 WIN! 🏆"
        ]
        
        for frame in victory_frames:
            print(f"\n{'=' * 20}")
            print(f"     {frame}")
            print(f"{'=' * 20}")
            time.sleep(0.5)
            
    @staticmethod
    def show_defeat_animation():
        """패배 애니메이션"""
        print(f"\n{'💀' * 20}")
        print("       GAME OVER...")
        print(f"{'💀' * 20}")
        time.sleep(1.0)


# 전역 효과음 관리자
ascii_sound = ASCIISoundEffects()
ascii_visual = ASCIIVisualEffects()
combat_animator = CombatTextAnimator()

def play_ascii_sound(effect_name: str):
    """ASCII 효과음 재생"""
    sound_map = {
        "brave_attack": ascii_sound.play_brave_attack_sound,
        "hp_attack": ascii_sound.play_hp_attack_sound,
        "break": ascii_sound.play_break_sound,
        "critical": ascii_sound.play_critical_sound,
        "heal": ascii_sound.play_heal_sound,
        "menu": ascii_sound.play_menu_sound,
        "level_up": ascii_sound.play_level_up_sound,
        "item_get": ascii_sound.play_item_get_sound,
        "magic": ascii_sound.play_magic_sound,
    }
    
    if effect_name in sound_map:
        sound_map[effect_name]()
    else:
        print(f"♪ {effect_name}")


def enhanced_battle_effect(effect_type: str, **kwargs):
    """강화된 전투 이펙트"""
    if effect_type == "damage":
        damage = kwargs.get("damage", 0)
        is_critical = kwargs.get("critical", False)
        if is_critical:
            play_ascii_sound("critical")
        ascii_visual.show_damage_numbers(damage, is_critical)
        
    elif effect_type == "heal":
        heal_amount = kwargs.get("amount", 0)
        play_ascii_sound("heal")
        ascii_visual.show_heal_numbers(heal_amount)
        
    elif effect_type == "brave_gain":
        amount = kwargs.get("amount", 0)
        total = kwargs.get("total", 0)
        ascii_visual.show_brave_gain(amount, total)
        
    elif effect_type == "break":
        play_ascii_sound("break")
        ascii_visual.show_break_effect()
        
    elif effect_type == "skill":
        skill_name = kwargs.get("skill_name", "")
        character_name = kwargs.get("character_name", "")
        ascii_visual.show_skill_activation(skill_name, character_name)
