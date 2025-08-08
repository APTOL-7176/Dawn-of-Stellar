"""
UI 애니메이션 시스템
HP/MP 게이지 부드러운 변화 효과
"""

import time
import threading
from typing import List, Dict, Optional, Callable
from queue import Queue

class SequentialGaugeAnimator:
    """순차적 게이지 애니메이션 관리자"""
    
    def __init__(self):
        self.animation_queue = Queue()  # 애니메이션 대기열
        self.is_processing = False  # 현재 처리 중인지 여부
        self.processing_thread = None
        self.active_character = None  # 현재 애니메이션 중인 캐릭터
        self.should_pause = False  # 애니메이션 일시정지 플래그
        self.should_skip = False   # 애니메이션 즉시 완료 플래그
        self.combat_mode = False   # 전투 모드 플래그 추가
        self.silent_mode = False   # 조용한 모드 플래그 추가
        
    def pause_animations(self):
        """애니메이션 일시정지 (메뉴 표시 시 사용)"""
        self.should_pause = True
        
    def resume_animations(self):
        """애니메이션 재개"""
        self.should_pause = False
        
    def skip_current_animations(self):
        """현재 애니메이션 즉시 완료"""
        self.should_skip = True
        
    def clear_all_animations(self):
        """모든 애니메이션 대기열 클리어"""
        while not self.animation_queue.empty():
            self.animation_queue.get()
        self.should_skip = True
    
    def set_combat_mode(self, enabled: bool):
        """전투 모드 설정 - 전투 중에도 애니메이션 유지하되 2초 대기 추가"""
        self.combat_mode = enabled
        # 전투 모드에서도 silent_mode는 False로 유지 (애니메이션 계속 실행)
    
    def set_silent_mode(self, enabled: bool):
        """조용한 모드 설정 - 애니메이션 없이 값만 업데이트"""
        self.silent_mode = enabled
        
    def add_animation_request(self, character, gauge_type: str, old_value: int, new_value: int):
        """애니메이션 요청 추가"""
        # 조용한 모드일 때만 간소화된 처리
        if self.silent_mode:
            # 값 즉시 업데이트
            if gauge_type == 'hp':
                character._hp = new_value
            elif gauge_type == 'mp':
                character._mp = new_value
            elif gauge_type == 'brv':
                character._brv = new_value
            
            # 간단한 게이지 변화 표시 및 2초 대기
            self._show_combat_gauge_change(character, gauge_type, new_value)
            return
        
        request = {
            'character': character,
            'gauge_type': gauge_type,  # 'hp', 'mp', 'brv'
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': time.time()
        }
        
        # 같은 캐릭터의 같은 게이지 타입이 이미 대기 중이면 업데이트
        temp_queue = []
        found = False
        
        while not self.animation_queue.empty():
            existing_request = self.animation_queue.get()
            if (existing_request['character'] == character and 
                existing_request['gauge_type'] == gauge_type):
                # 기존 요청을 새 값으로 업데이트
                existing_request['new_value'] = new_value
                temp_queue.append(existing_request)
                found = True
            else:
                temp_queue.append(existing_request)
        
        # 큐에 다시 넣기
        for req in temp_queue:
            self.animation_queue.put(req)
            
        # 새 요청이 아니면 추가
        if not found:
            self.animation_queue.put(request)
        
        # 처리 시작
        self._start_processing()
    
    def _start_processing(self):
        """애니메이션 처리 시작"""
        if self.is_processing:
            return
            
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._process_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def _process_queue(self):
        """대기열 처리"""
        try:
            while not self.animation_queue.empty():
                request = self.animation_queue.get()
                character = request['character']
                gauge_type = request['gauge_type']
                old_value = request['old_value']
                new_value = request['new_value']
                
                # 동일한 캐릭터의 다른 게이지들을 함께 처리
                same_character_requests = [request]
                
                # 같은 캐릭터의 다른 요청들 찾기
                temp_queue = []
                while not self.animation_queue.empty():
                    next_request = self.animation_queue.get()
                    if next_request['character'] == character:
                        same_character_requests.append(next_request)
                    else:
                        temp_queue.append(next_request)
                
                # 처리하지 않은 요청들 다시 큐에 넣기
                for req in temp_queue:
                    self.animation_queue.put(req)
                
                # 같은 캐릭터의 요청들을 순차적으로 처리
                self._process_character_animations(same_character_requests)
                
                # 캐릭터 간 간격
                time.sleep(0.3)
                
        finally:
            self.is_processing = False
            self.active_character = None
    
    def _process_character_animations(self, requests: List[Dict]):
        """같은 캐릭터의 애니메이션들을 순차 처리"""
        if not requests:
            return
        
        character = requests[0]['character']
        self.active_character = character
        
        # 게이지 타입별로 정렬 (HP -> BRV -> MP 순서로 변경)
        type_order = {'hp': 0, 'brv': 1, 'mp': 2}
        requests.sort(key=lambda x: type_order.get(x['gauge_type'], 999))
        
        for i, request in enumerate(requests):
            # 애니메이션 일시정지/스킵 체크
            if self.should_skip:
                # 즉시 완료 - 모든 게이지 값을 최종값으로 설정
                for req in requests:
                    char = req['character']
                    gauge_type = req['gauge_type']
                    new_value = req['new_value']
                    
                    # 값 직접 설정 (애니메이션 없이)
                    if gauge_type == 'hp':
                        char._hp = new_value
                    elif gauge_type == 'mp':
                        char._mp = new_value
                    elif gauge_type == 'brv':
                        char._brv = new_value
                
                self.should_skip = False
                break
            
            # 일시정지 대기
            while self.should_pause:
                time.sleep(0.1)
                if self.should_skip:
                    break
            
            gauge_type = request['gauge_type']
            old_value = request['old_value']
            new_value = request['new_value']
            
            if old_value == new_value:
                continue  # 변화가 없으면 건너뛰기
            
            # 각 게이지 애니메이션 실행
            if gauge_type == 'hp':
                self._animate_hp_sequential(character, old_value, new_value)
            elif gauge_type == 'mp':
                self._animate_mp_sequential(character, old_value, new_value)
            elif gauge_type == 'brv':
                self._animate_brv_sequential(character, old_value, new_value)
            
            # 전투 모드에서 각 게이지 변화 후 0.5초 대기
            if self.combat_mode:
                time.sleep(0.5)
            
            # 게이지 간 간격 (마지막이 아닌 경우에만)
            if i < len(requests) - 1:
                time.sleep(0.4)
        
        # 🎯 애니메이션 완료 - 즉시 다음 처리로 진행
        pass
    
    def _show_combat_gauge_change(self, character, gauge_type: str, new_value: int):
        """전투 중 게이지 변화 간단 표시 + 2초 대기"""
        # 게이지 타입별 이모지와 색상
        if gauge_type == 'hp':
            max_val = character.max_hp
            gauge_emoji = "💚"
            gauge_name = "HP"
            if new_value / max_val >= 0.67:
                color = "\033[92m"  # 초록
            elif new_value / max_val >= 0.33:
                color = "\033[93m"  # 노랑
            else:
                color = "\033[91m"  # 빨강
        elif gauge_type == 'mp':
            max_val = character.max_mp
            gauge_emoji = "💙"
            gauge_name = "MP"
            color = "\033[96m"  # 시안
        elif gauge_type == 'brv':
            if hasattr(character, 'brave_manager') and character.brave_manager:
                max_val = character.brave_manager.get_max_brave(character)
            else:
                max_val = getattr(character, 'max_brv', 999)
            gauge_emoji = "⚡"
            gauge_name = "BRV"
            color = "\033[93m"  # 노랑
        else:
            return
        
        # 간단한 게이지 표시 (애니메이션 없이)
        percentage = min(1.0, new_value / max_val) if max_val > 0 else 0
        bar_length = 20
        filled_length = int(percentage * bar_length)
        bar = "█" * filled_length + "▒" * (bar_length - filled_length)
        
        # 한 줄로 게이지 변화 표시
        print(f"{gauge_emoji} {character.name}: {color}{gauge_name} {new_value}/{max_val} {{{bar}}}\033[0m")
        
        # 2초 대기 (엔터로 스킵 가능)
        self._wait_with_skip_option(0.3, f"{gauge_name} 변화 확인")
    
    def _wait_with_skip_option(self, wait_time: float, description: str):
        """지정된 시간 대기 (엔터로 스킵 가능) - 간단한 구현"""
        print(f"\n⏰ {wait_time}초 후 자동 진행... (Enter로 스킵)")
        
        # 간단한 대기 방식으로 변경
        time.sleep(wait_time)
    
    def _animate_hp_sequential(self, character, old_hp: int, new_hp: int):
        """HP 순차 애니메이션"""
        # 기존 HP 애니메이션 로직을 동기식으로 실행
        if character.max_hp > 0:
            percentage = new_hp / character.max_hp
            bar_width = 20
            
            # HP 상태에 따른 단일 색상 결정
            if percentage >= 0.67:
                gauge_color = "\033[92m"  # 밝은 초록
            elif percentage >= 0.33:
                gauge_color = "\033[93m"  # 밝은 노랑
            else:
                gauge_color = "\033[91m"  # 밝은 빨강
            
            # 애니메이션 실행
            for step in range(16):  # 16단계 애니메이션
                # 스킵 체크
                if self.should_skip:
                    # 즉시 최종값으로 설정
                    character._hp = new_hp
                    print(f"\r💖 {character.name}: ❤️ HP {new_hp}/{character.max_hp}")
                    return
                
                # 일시정지 체크
                while self.should_pause:
                    time.sleep(0.1)
                    if self.should_skip:
                        character._hp = new_hp
                        print(f"\r💖 {character.name}: ❤️ HP {new_hp}/{character.max_hp}")
                        return
                
                progress = step / 15.0
                if progress < 0.5:
                    smooth_progress = 2 * progress * progress
                else:
                    smooth_progress = 1 - 2 * (1 - progress) * (1 - progress)
                
                current_value = old_hp + int((new_hp - old_hp) * smooth_progress)
                
                # 게이지 생성
                filled_blocks = (current_value / character.max_hp) * bar_width
                full_blocks = int(filled_blocks)
                partial_block = filled_blocks - full_blocks
                
                gauge = f"{gauge_color}{'█' * full_blocks}\033[0m"
                
                # 부분 블록 처리
                if full_blocks < bar_width and partial_block > 0:
                    if partial_block >= 0.875:
                        gauge += f"{gauge_color}▉\033[0m"
                    elif partial_block >= 0.75:
                        gauge += f"{gauge_color}▊\033[0m"
                    elif partial_block >= 0.625:
                        gauge += f"{gauge_color}▋\033[0m"
                    elif partial_block >= 0.5:
                        gauge += f"{gauge_color}▌\033[0m"
                    elif partial_block >= 0.375:
                        gauge += f"{gauge_color}▍\033[0m"
                    elif partial_block >= 0.25:
                        gauge += f"{gauge_color}▎\033[0m"
                    elif partial_block >= 0.125:
                        gauge += f"{gauge_color}▏\033[0m"
                    
                    gauge += " " * (bar_width - full_blocks - 1)
                else:
                    gauge += " " * (bar_width - full_blocks)
                
                # 변화량 표시
                change = new_hp - old_hp
                if change > 0:
                    change_text = f" (+{change})"
                elif change < 0:
                    change_text = f" ({change})"
                else:
                    change_text = ""
                
                bar = f"❤️ \033[97m{{\033[0m{gauge}\033[97m}}\033[0m {current_value}/{character.max_hp}"
                print(f"\r💖 {character.name}: {bar}{change_text}", end="", flush=True)
                
                time.sleep(0.025)  # 부드러운 애니메이션을 위한 짧은 딜레이 (2배 빠르게: 0.05 → 0.025)
            
            print()  # 줄바꿈
            time.sleep(0.4)  # 게이지 표시 유지 시간 (2배 빠르게: 0.8 → 0.4)
    
    def _animate_mp_sequential(self, character, old_mp: int, new_mp: int):
        """MP 순차 애니메이션"""
        if character.max_mp > 0:
            percentage = new_mp / character.max_mp
            bar_width = 20
            
            # MP 상태에 따른 단일 색상 결정
            if percentage >= 0.67:
                gauge_color = "\033[96m"  # 밝은 시안
            elif percentage >= 0.33:
                gauge_color = "\033[94m"  # 파랑
            else:
                gauge_color = "\033[34m"  # 어두운 파랑
            
            # 애니메이션 실행
            for step in range(16):
                # 스킵 체크
                if self.should_skip:
                    # 즉시 최종값으로 설정
                    character._mp = new_mp
                    print(f"\r🔮 {character.name}: 🌟 MP {new_mp}/{character.max_mp}")
                    return
                
                # 일시정지 체크
                while self.should_pause:
                    time.sleep(0.1)
                    if self.should_skip:
                        character._mp = new_mp
                        print(f"\r🔮 {character.name}: 🌟 MP {new_mp}/{character.max_mp}")
                        return
                
                progress = step / 15.0
                if progress < 0.5:
                    smooth_progress = 2 * progress * progress
                else:
                    smooth_progress = 1 - 2 * (1 - progress) * (1 - progress)
                
                current_value = old_mp + int((new_mp - old_mp) * smooth_progress)
                
                # 게이지 생성
                filled_blocks = (current_value / character.max_mp) * bar_width
                full_blocks = int(filled_blocks)
                partial_block = filled_blocks - full_blocks
                
                gauge = f"{gauge_color}{'█' * full_blocks}\033[0m"
                
                # 부분 블록 처리
                if full_blocks < bar_width and partial_block > 0:
                    if partial_block >= 0.875:
                        gauge += f"{gauge_color}▉\033[0m"
                    elif partial_block >= 0.75:
                        gauge += f"{gauge_color}▊\033[0m"
                    elif partial_block >= 0.625:
                        gauge += f"{gauge_color}▋\033[0m"
                    elif partial_block >= 0.5:
                        gauge += f"{gauge_color}▌\033[0m"
                    elif partial_block >= 0.375:
                        gauge += f"{gauge_color}▍\033[0m"
                    elif partial_block >= 0.25:
                        gauge += f"{gauge_color}▎\033[0m"
                    elif partial_block >= 0.125:
                        gauge += f"{gauge_color}▏\033[0m"
                    
                    gauge += " " * (bar_width - full_blocks - 1)
                else:
                    gauge += " " * (bar_width - full_blocks)
                
                # 변화량 표시
                change = new_mp - old_mp
                if change > 0:
                    change_text = f" (+{change}) ⬆️"
                elif change < 0:
                    change_text = f" ({change}) ⬇️"
                else:
                    change_text = ""
                
                bar = f"💙 \033[97m{{\033[0m{gauge}\033[97m}}\033[0m {current_value}/{character.max_mp}"
                print(f"\r🔮 {character.name}: {bar}{change_text}", end="", flush=True)
                
                time.sleep(0.025)  # 2배 빠르게: 0.05 → 0.025
            
            print()  # 줄바꿈
            time.sleep(0.4)  # 게이지 표시 유지 시간 (2배 빠르게: 0.8 → 0.4)
    
    def _animate_brv_sequential(self, character, old_brv: int, new_brv: int):
        """BRV 순차 애니메이션"""
        # BraveManager에서 정확한 최댓값 가져오기
        if hasattr(character, 'brave_manager') and character.brave_manager:
            max_brv = character.brave_manager.get_max_brave(character)
        else:
            max_brv = getattr(character, 'max_brv', getattr(character, 'max_brave', 999))
        max_brv = max(max_brv, new_brv, 1000)
        
        bar_width = 20
        
        # 애니메이션 실행
        for step in range(20):  # BRV는 조금 더 긴 애니메이션
            # 스킵 체크
            if self.should_skip:
                # 즉시 최종값으로 설정
                character._brv = new_brv
                print(f"\r⚡ {character.name}: 💪 BRV {new_brv}")
                return
            
            # 일시정지 체크
            while self.should_pause:
                time.sleep(0.1)
                if self.should_skip:
                    character._brv = new_brv
                    print(f"\r⚡ {character.name}: 💪 BRV {new_brv}")
                    return
            
            progress = step / 19.0
            if progress < 0.5:
                smooth_progress = 2 * progress * progress
            else:
                smooth_progress = 1 - 2 * (1 - progress) * (1 - progress)
            
            current_value = old_brv + int((new_brv - old_brv) * smooth_progress)
            
            # BRV 상태에 따른 색상 결정
            if current_value < 300:
                gauge_color = "\033[91m"  # 빨강
            elif current_value >= max_brv:
                gauge_color = "\033[95m"  # 마젠타
            else:
                gauge_color = "\033[93m"  # 노랑
            
            # 게이지 생성
            filled_blocks = (current_value / max_brv) * bar_width
            full_blocks = int(filled_blocks)
            partial_block = filled_blocks - full_blocks
            
            gauge = f"{gauge_color}{'█' * full_blocks}\033[0m"
            
            # 부분 블록 처리
            if full_blocks < bar_width and partial_block > 0:
                if partial_block >= 0.875:
                    gauge += f"{gauge_color}▉\033[0m"
                elif partial_block >= 0.75:
                    gauge += f"{gauge_color}▊\033[0m"
                elif partial_block >= 0.625:
                    gauge += f"{gauge_color}▋\033[0m"
                elif partial_block >= 0.5:
                    gauge += f"{gauge_color}▌\033[0m"
                elif partial_block >= 0.375:
                    gauge += f"{gauge_color}▍\033[0m"
                elif partial_block >= 0.25:
                    gauge += f"{gauge_color}▎\033[0m"
                elif partial_block >= 0.125:
                    gauge += f"{gauge_color}▏\033[0m"
                
                gauge += " " * (bar_width - full_blocks - 1)
            else:
                gauge += " " * (bar_width - full_blocks)
            
            # 변화량 표시
            change = new_brv - old_brv
            if change > 0:
                change_text = f" (+{change}) ⬆️"
            elif change < 0:
                change_text = f" ({change}) ⬇️"
            else:
                change_text = ""
            
            bar = f"⚡ \033[97m{{\033[0m{gauge}\033[97m}}\033[0m {current_value}/{max_brv}"
            print(f"\r💫 {character.name}: {bar}{change_text}", end="", flush=True)
            
            time.sleep(0.03)  # 2배 빠르게: 0.06 → 0.03
        
        print()  # 줄바꿈
        time.sleep(0.5)  # BRV 표시 시간 (2배 빠르게: 1.0 → 0.5)

# 전역 순차 애니메이터 인스턴스
sequential_animator = SequentialGaugeAnimator()

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
    """HP 변화 애니메이션 (순차 처리)"""
    if old_hp == new_hp:
        return
    
    # 순차 애니메이터에 요청 추가
    sequential_animator.add_animation_request(character, 'hp', old_hp, new_hp)

def animate_mp_change(character, old_mp: int, new_mp: int):
    """MP 변화 애니메이션 (순차 처리)"""
    if old_mp == new_mp:
        return
    
    # 순차 애니메이터에 요청 추가
    sequential_animator.add_animation_request(character, 'mp', old_mp, new_mp)

def animate_brv_change(character, old_brv: int, new_brv: int):
    """BRV 변화 애니메이션 (순차 처리)"""
    if old_brv == new_brv:
        return
    
    # 순차 애니메이터에 요청 추가
    sequential_animator.add_animation_request(character, 'brv', old_brv, new_brv)

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

# 전역 게이지 애니메이터 인스턴스 (단일 통합 인스턴스)
def get_gauge_animator():
    """게이지 애니메이터 인스턴스 반환 - sequential_animator와 통합"""
    return sequential_animator

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
