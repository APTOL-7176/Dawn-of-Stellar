"""
UI 애니메이션 시스템
HP/MP 게이지 부드러운 변화 효과
"""

import time
import threading
from typing import Callable, Optional

class GaugeAnimator:
    """게이지 애니메이션 클래스"""
    
    def __init__(self):
        self.animations = {}  # 진행 중인 애니메이션들
        
    def animate_gauge_change(self, 
                           gauge_id: str,
                           old_value: int,
                           new_value: int,
                           max_value: int,
                           callback: Optional[Callable] = None,
                           duration: float = 0.5,
                           steps: int = 10):
        """
        게이지 값 변화를 부드럽게 애니메이션
        
        Args:
            gauge_id: 게이지 식별자 (예: "player1_hp")
            old_value: 이전 값
            new_value: 새로운 값
            max_value: 최대값
            callback: 각 단계마다 호출될 콜백 함수
            duration: 애니메이션 총 시간 (초)
            steps: 애니메이션 단계 수
        """
        # 기존 애니메이션이 있다면 중단
        if gauge_id in self.animations:
            self.animations[gauge_id]['stop'] = True
        
        # 새 애니메이션 시작
        animation_data = {
            'stop': False,
            'thread': None
        }
        self.animations[gauge_id] = animation_data
        
        def animate():
            try:
                step_duration = duration / steps
                value_diff = new_value - old_value
                
                for i in range(steps + 1):
                    if animation_data['stop']:
                        break
                        
                    # 현재 값 계산 (부드러운 곡선 적용)
                    progress = i / steps
                    # easeInOutQuad 함수 적용
                    if progress < 0.5:
                        smooth_progress = 2 * progress * progress
                    else:
                        smooth_progress = 1 - 2 * (1 - progress) * (1 - progress)
                    
                    current_value = old_value + int(value_diff * smooth_progress)
                    
                    # 콜백 호출
                    if callback:
                        callback(current_value, max_value, progress)
                    
                    if i < steps:
                        time.sleep(step_duration)
                
                # 애니메이션 완료
                if gauge_id in self.animations:
                    del self.animations[gauge_id]
                    
            except Exception as e:
                print(f"애니메이션 오류: {e}")
                if gauge_id in self.animations:
                    del self.animations[gauge_id]
        
        # 별도 스레드에서 애니메이션 실행
        animation_thread = threading.Thread(target=animate)
        animation_data['thread'] = animation_thread
        animation_thread.daemon = True
        animation_thread.start()
    
    def stop_all_animations(self):
        """모든 애니메이션 중단"""
        for animation_data in self.animations.values():
            animation_data['stop'] = True
        self.animations.clear()

class CombatAnimations:
    """전투 애니메이션 시스템"""
    
    @staticmethod
    def combat_entry_animation():
        """간소화된 전투 진입 애니메이션"""
        print("⚔️ 전투 시작!")




    
    @staticmethod
    def damage_animation(damage: int, is_critical: bool = False):
        """데미지 애니메이션"""
        if is_critical:
            return f"💥🔥 {damage} 🔥💥 CRITICAL!"
        else:
            return f"⚡ {damage}"
    
    @staticmethod
    def healing_animation(heal_amount: int):
        """힐링 애니메이션"""
        return f"💚✨ +{heal_amount} HP ✨💚"
    
    @staticmethod
    def level_up_animation(character_name: str, new_level: int):
        """레벨업 애니메이션"""
        print(f"\n🌟✨🎉 {character_name} 레벨 업! Lv.{new_level} 🎉✨🌟")
        time.sleep(0.5)

# 전역 애니메이터 인스턴스
gauge_animator = GaugeAnimator()

def animate_hp_change(character, old_hp: int, new_hp: int):
    """HP 변화 애니메이션 (수치 포함)"""
    if old_hp == new_hp:
        return
    
    def update_callback(current_value):
        # HP 바 생성
        if character.max_hp > 0:
            percentage = current_value / character.max_hp
            bar_width = 20
            filled = int(percentage * bar_width)
            empty = bar_width - filled
            
            # 색상 결정
            if percentage > 0.7:
                color = "🟢"
            elif percentage > 0.3:
                color = "🟡"
            else:
                color = "🔴"
            
            bar = f"{color} [{'■' * filled}{'□' * empty}] {current_value}/{character.max_hp}"
            
            # 변화량 표시
            change = current_value - old_hp
            if change > 0:
                change_text = f" (+{change})"
            elif change < 0:
                change_text = f" ({change})"
            else:
                change_text = ""
            
            # 실시간 출력 (간소화된 버전)
            print(f"\r💖 {character.name}: {bar}{change_text}", end="", flush=True)
    
    gauge_animator.animate_gauge_change(
        f"{character.name}_hp",
        old_hp,
        new_hp,
        character.max_hp,
        update_callback,
        duration=0.8,
        steps=15
    )

def animate_mp_change(character, old_mp: int, new_mp: int):
    """MP 변화 애니메이션 (수치 포함)"""
    if old_mp == new_mp:
        return
    
    def update_callback(current_value):
        # MP 바 생성
        if character.max_mp > 0:
            percentage = current_value / character.max_mp
            bar_width = 20
            filled = int(percentage * bar_width)
            empty = bar_width - filled
            
            # 색상 결정
            if percentage > 0.7:
                color = "🔵"
            elif percentage > 0.3:
                color = "🟦"
            else:
                color = "🔷"
            
            bar = f"{color} [{'■' * filled}{'□' * empty}] {current_value}/{character.max_mp}"
            
            # 변화량 표시
            change = current_value - old_mp
            if change > 0:
                change_text = f" (+{change})"
            elif change < 0:
                change_text = f" ({change})"
            else:
                change_text = ""
            
            # 실시간 출력 (간소화된 버전)
            print(f"\r🔮 {character.name}: {bar}{change_text}", end="", flush=True)
    
    gauge_animator.animate_gauge_change(
        f"{character.name}_mp",
        old_mp,
        new_mp,
        character.max_mp,
        update_callback,
        duration=0.6,
        steps=12
    )

def animate_brv_change(character, old_brv: int, new_brv: int):
    """BRV 변화 애니메이션 (수치 포함)"""
    if old_brv == new_brv:
        return
    
    def update_callback(current_value):
        # BRV 바 생성
        max_brv = getattr(character, 'max_brv', 999)
        if max_brv > 0:
            percentage = current_value / max_brv
            bar_width = 20
            filled = int(percentage * bar_width)
            empty = bar_width - filled
            
            # BRV 비율에 따른 색상 (황금색 계열)
            if percentage > 0.8:
                color = "🟨"  # 밝은 노랑
            elif percentage > 0.5:
                color = "🟡"  # 노랑
            elif percentage > 0.2:
                color = "🟤"  # 갈색
            else:
                color = "⚫"  # 검정 (위험)
            
            bar = f"{color} [{'■' * filled}{'□' * empty}] {current_value}/{max_brv}"
            
            # 변화량 표시
            change = current_value - old_brv
            if change > 0:
                change_text = f" (+{change}) ⬆️"
            elif change < 0:
                change_text = f" ({change}) ⬇️"
            else:
                change_text = ""
            
            # 실시간 출력 (간소화된 버전)
            print(f"\r💫 {character.name}: {bar}{change_text}", end="", flush=True)
    
    gauge_animator.animate_gauge_change(
        f"{character.name}_brv",
        old_brv,
        new_brv,
        getattr(character, 'max_brv', 999),
        update_callback,
        duration=0.4,
        steps=10
    )

def show_animated_damage(target_name: str, damage: int, damage_type: str = "physical", is_critical: bool = False):
    """데미지 애니메이션 표시"""
    if is_critical:
        damage_text = f"💥🔥 {damage} 🔥💥 CRITICAL!"
        print(f"\n🎯 {target_name}에게 {damage_text}")
    else:
        if damage_type == "magic":
            damage_text = f"✨⚡ {damage} ⚡✨"
        elif damage > 100:
            damage_text = f"💢💥 {damage} 💥💢"
        elif damage > 50:
            damage_text = f"⚡💨 {damage} 💨⚡"
        else:
            damage_text = f"💨 {damage}"
        
        print(f"\n🎯 {target_name}에게 {damage_text} 데미지!")

def show_animated_healing(target_name: str, heal_amount: int, heal_type: str = "normal"):
    """회복 애니메이션 표시"""
    if heal_type == "major":
        heal_text = f"✨💚 +{heal_amount} HP 💚✨"
    elif heal_amount > 100:
        heal_text = f"🌟💖 +{heal_amount} HP 💖🌟"
    elif heal_amount > 50:
        heal_text = f"💚🌿 +{heal_amount} HP 🌿💚"
    else:
        heal_text = f"🌿 +{heal_amount} HP"
    
    print(f"\n💖 {target_name}이(가) {heal_text} 회복!")

def show_status_change_animation(character_name: str, status_name: str, is_applied: bool = True):
    """상태 변화 애니메이션"""
    status_icons = {
        'poison': '🤢',
        'burn': '🔥',
        'freeze': '🧊',
        'stun': '💫',
        'regeneration': '💚',
        'shield': '🛡️',
        'haste': '💨',
        'slow': '🐌'
    }
    
    icon = status_icons.get(status_name.lower(), '⭐')
    
    if is_applied:
        print(f"\n{icon} {character_name}에게 {status_name} 효과 적용! {icon}")
    else:
        print(f"\n✨ {character_name}의 {status_name} 효과 해제! ✨")

def show_coordination_attack_animation(attacker_name: str, supporter_name: str):
    """협동 공격 애니메이션"""
    print(f"\n💫✨ 협동 공격! ✨💫")
    print(f"⚔️ {attacker_name} ➕ {supporter_name}")
    print("🔥💥 COMBO ATTACK! 💥🔥")
    time.sleep(0.8)

def show_victory_animation():
    """승리 애니메이션"""
    victory_frames = [
        "🎉🎊🎉 승리! 🎉🎊🎉",
        "👑✨ 적을 물리쳤다! ✨👑", 
        "🏆🌟 경험치 획득! 🌟🏆"
    ]
    
    print("\n" + "="*80)
    for frame in victory_frames:
        print(f"{frame:^80}")
        time.sleep(0.5)
    print("="*80)
