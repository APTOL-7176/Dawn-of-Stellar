#!/usr/bin/env python3
"""
통합 게임 매니저
모든 고급 시스템을 통합하고 관리하는 중앙 매니저
"""

import pygame
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

# 우리가 만든 고급 시스템들 import
from .ffvii_sound_system import get_ffvii_sound_system, AudioCategory
from .meta_progression import MetaProgression

# 선택적 시스템들 (없어도 동작)
try:
    from .adaptive_balance import AdaptiveBalanceSystem, DifficultyLevel
except ImportError:
    print("adaptive_balance 모듈을 찾을 수 없습니다.")
    class AdaptiveBalanceSystem:
        def __init__(self): pass
        def start_session(self): pass
        def record_game_result(self, *args, **kwargs): pass
        def record_combat_event(self, *args, **kwargs): pass
        def update(self, dt): pass

try:
    from .smart_ai import SmartEnemyAI, PartyAI, AIPersonality
except ImportError:
    print("smart_ai 모듈을 찾을 수 없습니다.")
    class SmartEnemyAI:
        def __init__(self, personality): pass
        def learn_from_result(self, *args): pass
    class PartyAI:
        def suggest_party_action(self, *args): return {}
    class AIPersonality:
        AGGRESSIVE = "aggressive"
        BERSERKER = "berserker"
        DEFENSIVE = "defensive"
        TACTICAL = "tactical"
        ADAPTIVE = "adaptive"

try:
    from .advanced_ui import AdvancedUI, AnimationType, ParticleType
except ImportError:
    print("advanced_ui 모듈을 찾을 수 없습니다.")
    class AdvancedUI:
        def __init__(self, width, height): 
            self.fonts = {'title': None, 'large': None, 'medium': None}
        def show_notification(self, *args): pass
        def create_particle_burst(self, *args): pass
        def add_animation(self, *args, **kwargs): pass
        def update(self, dt): pass
        def draw_particles(self, surface): pass
        def draw_notifications(self, surface): pass
    class AnimationType:
        SHAKE = "shake"
    class ParticleType:
        MAGIC = "magic"
        SPARK = "spark"
        DAMAGE = "damage"
        HEAL = "heal"
        COIN = "coin"
        STAR = "star"


class GameState(Enum):
    """게임 상태"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    SETTINGS = "settings"
    ACHIEVEMENTS = "achievements"
    QUESTS = "quests"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class IntegratedGameManager:
    """통합 게임 매니저"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_state = GameState.MENU
        self.previous_state = None
        
        # 시스템 초기화
        self.sound_system = get_ffvii_sound_system()
        self.balance_system = AdaptiveBalanceSystem()
        self.ui_system = AdvancedUI(screen_width, screen_height)
        self.meta_progression = MetaProgression()
        self.party_ai = PartyAI()
        
        # 게임 데이터
        self.game_data = {
            'player_party': [],
            'current_floor': 1,
            'total_gold': 0,
            'play_time': 0,
            'session_start': time.time()
        }
        
        # 설정
        self.settings = {
            'master_volume': 0.7,
            'sfx_volume': 0.8,
            'bgm_volume': 0.6,
            'difficulty_auto_adjust': True,
            'ui_animations': True,
            'particle_effects': True,
            'sound_theme': 'fantasy'
        }
        
        # AI 관리
        self.enemy_ais: Dict[str, SmartEnemyAI] = {}
        
        # 이벤트 시스템
        self.event_handlers = {
            GameState.MENU: self._handle_menu_events,
            GameState.PLAYING: self._handle_game_events,
            GameState.PAUSED: self._handle_pause_events,
            GameState.SETTINGS: self._handle_settings_events,
            GameState.ACHIEVEMENTS: self._handle_achievement_events,
        }
        
        # 초기화 완료
        self._initialize_systems()
        
    def _initialize_systems(self):
        """시스템들 초기화"""
        # 사운드 시스템 설정
        self.sound_system.set_master_volume(self.settings['master_volume'])
        self.sound_system.set_volume(AudioCategory.SFX, self.settings['sfx_volume'])
        self.sound_system.set_volume(AudioCategory.BGM, self.settings['bgm_volume'])
        
        # UI 초기화 애니메이션
        if self.settings['ui_animations']:
            self.ui_system.show_notification("게임이 시작되었습니다!", "success")
        
        # 진행 시스템 로드 시도
        self.meta_progression.load_data()
        
        # 메뉴 BGM 시작 (초기화 완료 후)
        self.sound_system.play_bgm("title", loop=True)
        
        # 시스템 활성화 메시지들 제거
    
    def change_state(self, new_state: GameState, **kwargs):
        """게임 상태 변경"""
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # 상태별 전환 효과
        if new_state == GameState.PLAYING:
            self._enter_game_state(**kwargs)
        elif new_state == GameState.MENU:
            self._enter_menu_state()
        elif new_state == GameState.PAUSED:
            self._enter_pause_state()
        elif new_state == GameState.GAME_OVER:
            self._enter_game_over_state(**kwargs)
        
        # UI 알림
        state_messages = {
            GameState.PLAYING: "게임 시작!",
            GameState.PAUSED: "게임 일시정지",
            GameState.MENU: "메인 메뉴",
            GameState.SETTINGS: "설정",
            GameState.ACHIEVEMENTS: "업적",
            GameState.GAME_OVER: "게임 오버"
        }
        
        if new_state in state_messages:
            self.ui_system.show_notification(state_messages[new_state], "info")
    
    def _enter_game_state(self, **kwargs):
        """게임 상태 진입"""
        # 게임 시작 효과음 먼저 재생
        self.sound_system.play_sfx("game_start")
        
        # 파티클 효과
        if self.settings['particle_effects']:
            self.ui_system.create_particle_burst(
                self.screen_width // 2, self.screen_height // 2,
                ParticleType.MAGIC, 20
            )
        
        # 지연 BGM 플레이어를 사용하여 던전이 완전히 준비된 후 BGM 재생
        # world 객체가 있을 때만 실행 (실제 게임에서는 별도 처리)
        # IntegratedGameManager는 world를 직접 가지지 않으므로 건너뜀
        # 실제 world 객체는 main.py의 DawnOfStellarGame에서 관리됨
        pass
        
                # 통계 업데이트 (메타 진행 시스템 호환)
        # self.meta_progression에는 update_stat 메소드가 없으므로 건너뛰기
        pass
        
        # 난이도 조정 시작
        if self.settings['difficulty_auto_adjust']:
            self.balance_system.start_session()
        
        # 통계 업데이트 (메타 진행 시스템 호환)
        floors_explored = self.game_data.get('floors_explored', 0)
        self.game_data['floors_explored'] = max(floors_explored, 1)
    
    def _enter_menu_state(self):
        """메뉴 상태 진입"""
        # stop_bgm() 제거 - play_bgm에서 자동으로 전환 처리
        self.sound_system.play_bgm("title", loop=True)
        
        # 게임 시간 저장 (메타 진행 시스템 호환)
        if self.previous_state == GameState.PLAYING:
            session_time = time.time() - self.game_data['session_start']
            # meta_progression에는 update_stat 메소드가 없으므로 건너뛰기
            self.game_data['total_play_time'] = session_time
    
    def _enter_pause_state(self):
        """일시정지 상태 진입"""
        self.sound_system.pause_bgm()
        self.sound_system.play_sfx("menu_select")
    
    def _enter_game_over_state(self, **kwargs):
        """게임 오버 상태 진입"""
        # 게임 오버 사운드
        self.sound_system.stop_bgm()
        self.sound_system.play_sfx("game_over")
        
        # 스크린 셰이크 효과
        if self.settings['ui_animations']:
            self.ui_system.add_animation(
                target=None, anim_type=AnimationType.SHAKE,
                duration=1.0, start_value=0, end_value=1
            )
        
        # 통계 업데이트 (메타 진행 시스템 호환)
        # meta_progression에는 update_stat 메소드가 없으므로 건너뛰기
        
        # 최종 성과 평가
        final_stats = kwargs.get('final_stats', {})
        self._process_final_results(final_stats)
    
    def _process_final_results(self, final_stats: Dict):
        """최종 결과 처리"""
        # 생존 시간 기록 (메타 진행 시스템 호환)
        survival_time = final_stats.get('survival_time', 0)
        # meta_progression에는 player_stats가 없으므로 game_data에 저장
        longest_survival = self.game_data.get('longest_survival_time', 0)
        if survival_time > longest_survival:
            self.game_data['longest_survival_time'] = survival_time
            self.ui_system.show_notification("새로운 생존 기록!", "success")
        
        # 밸런스 시스템에 결과 피드백
        self.balance_system.record_game_result(
            success=False,  # 게임 오버이므로 실패
            final_stats=final_stats
        )
    
    def handle_combat_event(self, event_type: str, data: Dict[str, Any]):
        """전투 이벤트 처리"""
        if event_type == "enemy_defeated":
            # 통계 업데이트 (메타 진행 시스템 호환)
            enemies_defeated = self.game_data.get('enemies_defeated', 0)
            self.game_data['enemies_defeated'] = enemies_defeated + 1
            
            # 사운드 효과
            enemy_type = data.get('enemy_type', 'default')
            self.sound_system.play_sfx(f"enemy_death_{enemy_type}", fallback="enemy_death")
            
            # 파티클 효과
            if self.settings['particle_effects']:
                pos = data.get('position', (400, 300))
                self.ui_system.create_particle_burst(
                    pos[0], pos[1], ParticleType.SPARK, 15
                )
            
            # AI 학습
            enemy_id = data.get('enemy_id')
            if enemy_id in self.enemy_ais:
                self.enemy_ais[enemy_id].learn_from_result("defeated", 0.0)
        
        elif event_type == "damage_dealt":
            damage = data.get('damage', 0)
            is_critical = data.get('is_critical', False)
            
            # 통계 업데이트 (메타 진행 시스템 호환)
            total_damage = self.game_data.get('total_damage_dealt', 0)
            self.game_data['total_damage_dealt'] = total_damage + damage
            if is_critical:
                critical_hits = self.game_data.get('critical_hits', 0)
                self.game_data['critical_hits'] = critical_hits + 1
            
            # 사운드 효과
            if is_critical:
                self.sound_system.play_sfx("critical_hit")
            else:
                self.sound_system.play_sfx("normal_hit")
            
            # 파티클 효과
            if self.settings['particle_effects']:
                pos = data.get('position', (400, 300))
                particle_type = ParticleType.DAMAGE if not is_critical else ParticleType.SPARK
                self.ui_system.create_particle_burst(pos[0], pos[1], particle_type, 8)
        
        elif event_type == "healing":
            amount = data.get('amount', 0)
            
            # 사운드 효과
            self.sound_system.play_sfx("heal")
            
            # 파티클 효과
            if self.settings['particle_effects']:
                pos = data.get('position', (400, 300))
                self.ui_system.create_particle_burst(
                    pos[0], pos[1], ParticleType.HEAL, 12
                )
        
        # 밸런스 시스템에 전투 데이터 전달
        self.balance_system.record_combat_event(event_type, data)
    
    def handle_exploration_event(self, event_type: str, data: Dict[str, Any]):
        """탐험 이벤트 처리"""
        if event_type == "floor_changed":
            floor = data.get('floor', 1)
            self.game_data['current_floor'] = floor
            
            # 통계 업데이트 (메타 진행 시스템 호환)
            floors_explored = self.game_data.get('floors_explored', 0)
            self.game_data['floors_explored'] = max(floors_explored, floor)
            
            # 층별 BGM 변경
            if floor % 5 == 0:  # 보스 층
                self.sound_system.play_battle_bgm(is_boss=True, boss_type="major")
            else:
                self.sound_system.play_dungeon_bgm(floor)
            
            # 알림
            self.ui_system.show_notification(f"{floor}층 도달!", "info")
        
        elif event_type == "treasure_found":
            # 통계 업데이트 (메타 진행 시스템 호환)
            treasures = self.game_data.get('treasure_chests_opened', 0)
            self.game_data['treasure_chests_opened'] = treasures + 1
            
            # 사운드 효과
            self.sound_system.play_sfx("treasure_open")
            
            # 파티클 효과
            if self.settings['particle_effects']:
                pos = data.get('position', (400, 300))
                self.ui_system.create_particle_burst(
                    pos[0], pos[1], ParticleType.COIN, 25
                )
        
        elif event_type == "secret_found":
            # 통계 업데이트 (메타 진행 시스템 호환)
            secrets = self.game_data.get('secrets_found', 0)
            self.game_data['secrets_found'] = secrets + 1
            
            # 특별 사운드
            self.sound_system.play_sfx("secret_found")
            
            # 특별 파티클
            if self.settings['particle_effects']:
                pos = data.get('position', (400, 300))
                self.ui_system.create_particle_burst(
                    pos[0], pos[1], ParticleType.STAR, 30
                )
            
            # 특별 알림
            self.ui_system.show_notification("비밀을 발견했습니다!", "success")
    
    def create_enemy_ai(self, enemy_id: str, enemy_type: str) -> SmartEnemyAI:
        """적 AI 생성"""
        ai_personality_map = {
            'goblin': AIPersonality.AGGRESSIVE,
            'orc': AIPersonality.BERSERKER,
            'skeleton': AIPersonality.DEFENSIVE,
            'wizard': AIPersonality.TACTICAL,
            'boss': AIPersonality.ADAPTIVE
        }
        
        personality = ai_personality_map.get(enemy_type, AIPersonality.TACTICAL)
        enemy_ai = SmartEnemyAI(personality)
        self.enemy_ais[enemy_id] = enemy_ai
        
        return enemy_ai
    
    def get_party_ai_suggestion(self, party_members: List, enemies: List, 
                               battle_state: Dict) -> Dict:
        """파티 AI 조언 요청"""
        return self.party_ai.suggest_party_action(party_members, enemies, battle_state)
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """설정 업데이트"""
        self.settings.update(new_settings)
        
        # 사운드 볼륨 적용
        if 'master_volume' in new_settings:
            self.sound_system.set_master_volume(new_settings['master_volume'])
        if 'sfx_volume' in new_settings:
            self.sound_system.set_volume(AudioCategory.SFX, new_settings['sfx_volume'])
        if 'bgm_volume' in new_settings:
            self.sound_system.set_volume(AudioCategory.BGM, new_settings['bgm_volume'])
        
        # 설정 저장
        self.save_settings()
    
    def get_current_stats(self) -> Dict[str, Any]:
        """현재 통계 조회"""
        return {
            'player_stats': self.game_data,  # game_data로 대체
            'game_data': self.game_data,
            'difficulty': getattr(self.balance_system, 'current_difficulty', 'Normal'),
            'achievements_unlocked': len(self.meta_progression.data.get('achievements', [])),
            'unlocked_classes': self.meta_progression.data.get('unlocked_classes', [])
        }
    
    def process_events(self, events: List[pygame.event.Event]):
        """이벤트 처리"""
        handler = self.event_handlers.get(self.current_state)
        if handler:
            handler(events)
    
    def _handle_menu_events(self, events: List[pygame.event.Event]):
        """메뉴 이벤트 처리"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.sound_system.play_sfx("menu_select")
                    self.change_state(GameState.PLAYING)
                elif event.key == pygame.K_a:
                    self.sound_system.play_sfx("menu_navigate")
                    self.change_state(GameState.ACHIEVEMENTS)
                elif event.key == pygame.K_s:
                    self.sound_system.play_sfx("menu_navigate")
                    self.change_state(GameState.SETTINGS)
    
    def _handle_game_events(self, events: List[pygame.event.Event]):
        """게임 이벤트 처리"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.PAUSED)
                elif event.key == pygame.K_i:
                    self.change_state(GameState.INVENTORY)
                elif event.key == pygame.K_q:
                    self.change_state(GameState.QUESTS)
    
    def _handle_pause_events(self, events: List[pygame.event.Event]):
        """일시정지 이벤트 처리"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.sound_system.resume_bgm()
                    self.change_state(GameState.PLAYING)
                elif event.key == pygame.K_m:
                    self.change_state(GameState.MENU)
    
    def _handle_settings_events(self, events: List[pygame.event.Event]):
        """설정 이벤트 처리"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_state(self.previous_state or GameState.MENU)
    
    def _handle_achievement_events(self, events: List[pygame.event.Event]):
        """업적 이벤트 처리"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_state(self.previous_state or GameState.MENU)
    
    def update(self, dt: float):
        """매 프레임 업데이트"""
        # UI 시스템 업데이트
        self.ui_system.update(dt)
        
        # 게임 중일 때만 밸런스 시스템 업데이트
        if self.current_state == GameState.PLAYING:
            self.balance_system.update(dt)
        
        # 세션 시간 업데이트
        if self.current_state == GameState.PLAYING:
            self.game_data['play_time'] = time.time() - self.game_data['session_start']
    
    def draw(self, surface: pygame.Surface):
        """화면 그리기"""
        # 파티클 시스템 그리기
        if self.settings['particle_effects']:
            self.ui_system.draw_particles(surface)
        
        # 알림 그리기
        self.ui_system.draw_notifications(surface)
        
        # 상태별 UI 그리기
        if self.current_state == GameState.MENU:
            self._draw_menu(surface)
        elif self.current_state == GameState.ACHIEVEMENTS:
            self._draw_achievements(surface)
        elif self.current_state == GameState.SETTINGS:
            self._draw_settings(surface)
    
    def _draw_menu(self, surface: pygame.Surface):
        """메인 메뉴 그리기"""
        # 간단한 메뉴 UI
        title_text = "🎮 로그라이크 게임"
        font = self.ui_system.fonts['title']
        text_surface = font.render(title_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width//2, 100))
        surface.blit(text_surface, text_rect)
        
        # 메뉴 옵션들
        menu_options = [
            "엔터: 게임 시작",
            "A: 업적 보기",
            "S: 설정",
            "ESC: 종료"
        ]
        
        y_start = 200
        for i, option in enumerate(menu_options):
            font = self.ui_system.fonts['medium']
            text = font.render(option, True, (200, 200, 200))
            rect = text.get_rect(center=(self.screen_width//2, y_start + i * 40))
            surface.blit(text, rect)
    
    def _draw_achievements(self, surface: pygame.Surface):
        """업적 화면 그리기"""
        title = "🏆 업적"
        font = self.ui_system.fonts['large']
        text_surface = font.render(title, True, (255, 215, 0))
        text_rect = text_surface.get_rect(center=(self.screen_width//2, 50))
        surface.blit(text_surface, text_rect)
        
        # 업적 목록 (간단히) - 메타 진행 시스템 호환
        y_offset = 100
        achievements = self.meta_progression.data.get('achievements', [])
        achievement_names = [
            "첫 번째 적 처치",
            "10층 도달",
            "100마리 처치",
            "보물 상자 10개 개방",
            "비밀 발견"
        ]
        
        for i, achievement_name in enumerate(achievement_names[:5]):
            status = "✅" if achievement_name in achievements else "⏳"
            text = f"{status} {achievement_name}"
            
            font = self.ui_system.fonts['medium']
            color = (0, 255, 0) if achievement_name in achievements else (150, 150, 150)
            if font:  # None 체크
                text_surface = font.render(text, True, color)
                surface.blit(text_surface, (50, y_offset))
            y_offset += 30
    
    def _draw_settings(self, surface: pygame.Surface):
        """설정 화면 그리기"""
        title = "⚙️ 설정"
        font = self.ui_system.fonts['large']
        text_surface = font.render(title, True, (100, 149, 237))
        text_rect = text_surface.get_rect(center=(self.screen_width//2, 50))
        surface.blit(text_surface, text_rect)
        
        # 설정 항목들
        settings_display = [
            f"마스터 볼륨: {int(self.settings['master_volume'] * 100)}%",
            f"효과음 볼륨: {int(self.settings['sfx_volume'] * 100)}%",
            f"배경음 볼륨: {int(self.settings['bgm_volume'] * 100)}%",
            f"자동 난이도: {'켜짐' if self.settings['difficulty_auto_adjust'] else '꺼짐'}",
            f"UI 애니메이션: {'켜짐' if self.settings['ui_animations'] else '꺼짐'}",
            f"파티클 효과: {'켜짐' if self.settings['particle_effects'] else '꺼짐'}"
        ]
        
        y_offset = 120
        for setting in settings_display:
            font = self.ui_system.fonts['medium']
            text_surface = font.render(setting, True, (200, 200, 200))
            surface.blit(text_surface, (100, y_offset))
            y_offset += 35
    
    def save_settings(self, filename: str = "game_settings.json"):
        """설정 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"설정 저장 실패: {e}")
            return False
    
    def load_settings(self, filename: str = "game_settings.json"):
        """설정 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                self.settings.update(loaded_settings)
            return True
        except Exception as e:
            print(f"설정 로드 실패: {e}")
            return False
    
    def shutdown(self):
        """게임 종료 처리"""
        # 진행도 저장 (메타 진행 시스템)
        self.meta_progression.save_data()
        
        # 설정 저장
        self.save_settings()
        
        # 사운드 시스템 정리
        self.sound_system.cleanup()
        
        print("🎮 게임 매니저 종료 완료")


# 전역 게임 매니저 인스턴스
def create_game_manager(screen_width: int = 800, screen_height: int = 600) -> IntegratedGameManager:
    """게임 매니저 생성"""
    return IntegratedGameManager(screen_width, screen_height)
