#!/usr/bin/env python3
"""
진보된 UI/UX 시스템
애니메이션, 파티클, 고급 메뉴, 시각 효과
"""

import pygame
import math
import random
import time
from typing import List, Dict, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass
from collections import deque


class AnimationType(Enum):
    """애니메이션 타입"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    SCALE = "scale"
    BOUNCE = "bounce"
    SHAKE = "shake"
    PULSE = "pulse"
    ROTATE = "rotate"


class ParticleType(Enum):
    """파티클 타입"""
    SPARK = "spark"
    SMOKE = "smoke"
    MAGIC = "magic"
    BLOOD = "blood"
    HEAL = "heal"
    DAMAGE = "damage"
    COIN = "coin"
    STAR = "star"


@dataclass
class Animation:
    """애니메이션 데이터"""
    target: Any
    anim_type: AnimationType
    duration: float
    start_time: float
    start_value: Any
    end_value: Any
    easing_func: Optional[Callable] = None
    on_complete: Optional[Callable] = None
    
    def __post_init__(self):
        if self.easing_func is None:
            self.easing_func = self.ease_out_quad
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quad easing out"""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic easing in-out"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - math.pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_bounce(t: float) -> float:
        """Bounce easing"""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375


@dataclass
class Particle:
    """파티클 데이터"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    particle_type: ParticleType
    
    def update(self, dt: float):
        """파티클 업데이트"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        
        # 중력 효과
        if self.particle_type in [ParticleType.SPARK, ParticleType.BLOOD]:
            self.vy += 200 * dt
        
        # 마법 파티클은 원형으로 움직임
        if self.particle_type == ParticleType.MAGIC:
            self.vx += math.sin(time.time() * 5) * 50 * dt
            self.vy += math.cos(time.time() * 5) * 50 * dt
    
    def is_alive(self) -> bool:
        """파티클이 살아있는지 확인"""
        return self.life > 0
    
    def get_alpha(self) -> int:
        """현재 알파값 계산"""
        return int(255 * (self.life / self.max_life))


class UITheme:
    """UI 테마"""
    
    def __init__(self, theme_name: str = "default"):
        self.theme_name = theme_name
        self.colors = self._load_theme_colors(theme_name)
        self.fonts = {}
        
    def _load_theme_colors(self, theme_name: str) -> Dict[str, Tuple[int, int, int]]:
        """테마별 색상 로드"""
        themes = {
            "default": {
                "primary": (70, 130, 180),
                "secondary": (100, 149, 237),
                "accent": (255, 215, 0),
                "background": (20, 25, 40),
                "surface": (40, 45, 60),
                "text": (255, 255, 255),
                "text_secondary": (200, 200, 200),
                "success": (34, 197, 94),
                "warning": (251, 191, 36),
                "error": (239, 68, 68),
                "border": (100, 116, 139)
            },
            "dark": {
                "primary": (139, 69, 19),
                "secondary": (160, 82, 45),
                "accent": (255, 140, 0),
                "background": (10, 10, 10),
                "surface": (25, 25, 25),
                "text": (255, 255, 255),
                "text_secondary": (170, 170, 170),
                "success": (0, 128, 0),
                "warning": (255, 165, 0),
                "error": (178, 34, 34),
                "border": (64, 64, 64)
            },
            "fantasy": {
                "primary": (147, 51, 234),
                "secondary": (168, 85, 247),
                "accent": (34, 197, 94),
                "background": (15, 23, 42),
                "surface": (30, 41, 59),
                "text": (248, 250, 252),
                "text_secondary": (203, 213, 225),
                "success": (16, 185, 129),
                "warning": (245, 158, 11),
                "error": (244, 63, 94),
                "border": (71, 85, 105)
            }
        }
        return themes.get(theme_name, themes["default"])


class AdvancedUI:
    """고급 UI 시스템"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.animations: List[Animation] = []
        self.particles: List[Particle] = []
        self.ui_elements: Dict[str, Any] = {}
        self.theme = UITheme("fantasy")
        
        # 폰트 초기화
        pygame.font.init()
        self.fonts = {
            "small": pygame.font.Font(None, 16),
            "medium": pygame.font.Font(None, 24),
            "large": pygame.font.Font(None, 32),
            "title": pygame.font.Font(None, 48)
        }
        
        # UI 상태
        self.modal_stack: List[Dict] = []
        self.tooltip = None
        self.notification_queue: deque = deque(maxlen=5)
        
    def update(self, dt: float):
        """UI 시스템 업데이트"""
        self._update_animations(dt)
        self._update_particles(dt)
        self._update_notifications(dt)
    
    def _update_animations(self, dt: float):
        """애니메이션 업데이트"""
        current_time = time.time()
        completed_animations = []
        
        for anim in self.animations:
            progress = (current_time - anim.start_time) / anim.duration
            progress = max(0, min(1, progress))
            
            if progress >= 1.0:
                completed_animations.append(anim)
                if anim.on_complete:
                    anim.on_complete()
                continue
            
            # 이징 적용
            eased_progress = anim.easing_func(progress)
            
            # 애니메이션 타입별 처리
            self._apply_animation(anim, eased_progress)
        
        # 완료된 애니메이션 제거
        for anim in completed_animations:
            self.animations.remove(anim)
    
    def _apply_animation(self, anim: Animation, progress: float):
        """애니메이션 적용"""
        if anim.anim_type == AnimationType.FADE_IN:
            alpha = int(anim.start_value + (anim.end_value - anim.start_value) * progress)
            if hasattr(anim.target, 'set_alpha'):
                anim.target.set_alpha(alpha)
        
        elif anim.anim_type == AnimationType.SLIDE_LEFT:
            x = anim.start_value + (anim.end_value - anim.start_value) * progress
            if hasattr(anim.target, 'rect'):
                anim.target.rect.x = x
        
        elif anim.anim_type == AnimationType.PULSE:
            scale = 1.0 + 0.1 * math.sin(progress * math.pi * 4)
            if hasattr(anim.target, 'scale'):
                anim.target.scale = scale
        
        elif anim.anim_type == AnimationType.SHAKE:
            offset_x = random.randint(-5, 5) * (1 - progress)
            offset_y = random.randint(-5, 5) * (1 - progress)
            if hasattr(anim.target, 'shake_offset'):
                anim.target.shake_offset = (offset_x, offset_y)
    
    def _update_particles(self, dt: float):
        """파티클 업데이트"""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def _update_notifications(self, dt: float):
        """알림 업데이트"""
        for notification in list(self.notification_queue):
            notification['life'] -= dt
            if notification['life'] <= 0:
                self.notification_queue.remove(notification)
    
    def add_animation(self, target: Any, anim_type: AnimationType, duration: float, 
                     start_value: Any, end_value: Any, easing_func: Optional[Callable] = None,
                     on_complete: Optional[Callable] = None):
        """애니메이션 추가"""
        animation = Animation(
            target=target,
            anim_type=anim_type,
            duration=duration,
            start_time=time.time(),
            start_value=start_value,
            end_value=end_value,
            easing_func=easing_func,
            on_complete=on_complete
        )
        self.animations.append(animation)
    
    def create_particle_burst(self, x: float, y: float, particle_type: ParticleType, 
                            count: int = 10, color: Optional[Tuple[int, int, int]] = None):
        """파티클 버스트 생성"""
        if color is None:
            color_map = {
                ParticleType.SPARK: (255, 255, 100),
                ParticleType.MAGIC: (147, 51, 234),
                ParticleType.HEAL: (34, 197, 94),
                ParticleType.DAMAGE: (239, 68, 68),
                ParticleType.COIN: (255, 215, 0)
            }
            color = color_map.get(particle_type, (255, 255, 255))
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            if particle_type == ParticleType.HEAL:
                vy = -abs(vy)  # 치료 파티클은 위로
            
            particle = Particle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-10, 10),
                vx=vx,
                vy=vy,
                life=random.uniform(0.5, 1.5),
                max_life=1.0,
                color=color,
                size=random.uniform(2, 6),
                particle_type=particle_type
            )
            self.particles.append(particle)
    
    def show_notification(self, message: str, type_: str = "info", duration: float = 3.0):
        """알림 표시"""
        notification = {
            'message': message,
            'type': type_,
            'life': duration,
            'max_life': duration,
            'created_time': time.time()
        }
        self.notification_queue.append(notification)
    
    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str, 
                   style: str = "primary", hover: bool = False, pressed: bool = False) -> bool:
        """고급 버튼 그리기"""
        # 색상 선택
        if style == "primary":
            bg_color = self.theme.colors["primary"]
        elif style == "secondary":
            bg_color = self.theme.colors["secondary"]
        elif style == "success":
            bg_color = self.theme.colors["success"]
        elif style == "warning":
            bg_color = self.theme.colors["warning"]
        elif style == "error":
            bg_color = self.theme.colors["error"]
        else:
            bg_color = self.theme.colors["surface"]
        
        # 상태별 색상 조정
        if pressed:
            bg_color = tuple(max(0, c - 30) for c in bg_color)
        elif hover:
            bg_color = tuple(min(255, c + 20) for c in bg_color)
        
        # 그라데이션 배경
        self._draw_gradient_rect(surface, rect, bg_color, 
                                tuple(max(0, c - 20) for c in bg_color))
        
        # 테두리
        pygame.draw.rect(surface, self.theme.colors["border"], rect, 2)
        
        # 텍스트
        text_surface = self.fonts["medium"].render(text, True, self.theme.colors["text"])
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
        
        return True
    
    def _draw_gradient_rect(self, surface: pygame.Surface, rect: pygame.Rect, 
                          color1: Tuple[int, int, int], color2: Tuple[int, int, int]):
        """그라데이션 사각형 그리기"""
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))
    
    def draw_progress_bar(self, surface: pygame.Surface, rect: pygame.Rect, 
                         progress: float, color: Optional[Tuple[int, int, int]] = None,
                         animated: bool = True):
        """애니메이션 진행 바"""
        if color is None:
            color = self.theme.colors["primary"]
        
        # 배경
        pygame.draw.rect(surface, self.theme.colors["surface"], rect)
        pygame.draw.rect(surface, self.theme.colors["border"], rect, 2)
        
        # 진행 바
        fill_width = int(rect.width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x + 2, rect.y + 2, 
                                   fill_width - 4, rect.height - 4)
            
            if animated:
                # 애니메이션 효과
                glow_alpha = int(128 + 127 * math.sin(time.time() * 3))
                glow_color = tuple(min(255, c + 50) for c in color)
                # 실제로는 알파 블렌딩을 위한 더 복잡한 구현이 필요
                pygame.draw.rect(surface, color, fill_rect)
            else:
                pygame.draw.rect(surface, color, fill_rect)
    
    def draw_modal(self, surface: pygame.Surface, title: str, content: List[str], 
                  buttons: List[Dict]):
        """모달 창 그리기"""
        # 배경 어둡게
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # 모달 크기 계산
        modal_width = 400
        modal_height = 200 + len(content) * 30 + len(buttons) * 50
        modal_x = (self.screen_width - modal_width) // 2
        modal_y = (self.screen_height - modal_height) // 2
        
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        
        # 모달 배경
        self._draw_gradient_rect(surface, modal_rect, 
                                self.theme.colors["surface"], 
                                self.theme.colors["background"])
        pygame.draw.rect(surface, self.theme.colors["border"], modal_rect, 3)
        
        # 제목
        title_surface = self.fonts["large"].render(title, True, self.theme.colors["text"])
        title_rect = title_surface.get_rect(centerx=modal_rect.centerx, 
                                           y=modal_rect.y + 20)
        surface.blit(title_surface, title_rect)
        
        # 내용
        y_offset = modal_rect.y + 80
        for line in content:
            text_surface = self.fonts["medium"].render(line, True, 
                                                      self.theme.colors["text_secondary"])
            text_rect = text_surface.get_rect(centerx=modal_rect.centerx, y=y_offset)
            surface.blit(text_surface, text_rect)
            y_offset += 30
        
        # 버튼들
        button_y = modal_rect.bottom - 80
        button_width = 100
        button_spacing = 20
        total_button_width = len(buttons) * button_width + (len(buttons) - 1) * button_spacing
        start_x = modal_rect.centerx - total_button_width // 2
        
        for i, button in enumerate(buttons):
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, 40)
            
            self.draw_button(surface, button_rect, button['text'], 
                           button.get('style', 'primary'))
    
    def draw_particles(self, surface: pygame.Surface):
        """파티클 그리기"""
        for particle in self.particles:
            alpha = particle.get_alpha()
            color = (*particle.color, alpha)
            
            # 파티클 타입별 그리기
            if particle.particle_type == ParticleType.SPARK:
                pygame.draw.circle(surface, particle.color, 
                                 (int(particle.x), int(particle.y)), 
                                 int(particle.size))
            
            elif particle.particle_type == ParticleType.MAGIC:
                # 별 모양
                self._draw_star(surface, particle.x, particle.y, 
                               particle.size, particle.color)
            
            elif particle.particle_type == ParticleType.HEAL:
                # 십자가 모양
                self._draw_cross(surface, particle.x, particle.y, 
                                particle.size, particle.color)
    
    def _draw_star(self, surface: pygame.Surface, x: float, y: float, 
                  size: float, color: Tuple[int, int, int]):
        """별 모양 그리기"""
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                radius = size
            else:
                radius = size * 0.5
            
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
        
        pygame.draw.polygon(surface, color, points)
    
    def _draw_cross(self, surface: pygame.Surface, x: float, y: float, 
                   size: float, color: Tuple[int, int, int]):
        """십자가 그리기"""
        thickness = max(1, int(size / 3))
        # 세로선
        pygame.draw.line(surface, color, 
                        (x, y - size), (x, y + size), thickness)
        # 가로선
        pygame.draw.line(surface, color, 
                        (x - size, y), (x + size, y), thickness)
    
    def draw_notifications(self, surface: pygame.Surface):
        """알림 그리기"""
        y_offset = 10
        for notification in self.notification_queue:
            alpha = int(255 * (notification['life'] / notification['max_life']))
            
            # 배경
            text_surface = self.fonts["medium"].render(notification['message'], True, 
                                                      self.theme.colors["text"])
            rect = text_surface.get_rect()
            rect.x = self.screen_width - rect.width - 20
            rect.y = y_offset
            rect = rect.inflate(20, 10)
            
            # 타입별 색상
            bg_color = {
                'info': self.theme.colors["primary"],
                'success': self.theme.colors["success"],
                'warning': self.theme.colors["warning"],
                'error': self.theme.colors["error"]
            }.get(notification['type'], self.theme.colors["surface"])
            
            # 반투명 배경
            overlay = pygame.Surface((rect.width, rect.height))
            overlay.set_alpha(alpha // 2)
            overlay.fill(bg_color)
            surface.blit(overlay, rect)
            
            # 텍스트
            text_surface.set_alpha(alpha)
            surface.blit(text_surface, (rect.x + 10, rect.y + 5))
            
            y_offset += rect.height + 5


# 전역 UI 인스턴스
def create_advanced_ui(screen_width: int, screen_height: int) -> AdvancedUI:
    """고급 UI 생성"""
    return AdvancedUI(screen_width, screen_height)


# UI 유틸리티 함수들
def interpolate(start: float, end: float, t: float) -> float:
    """선형 보간"""
    return start + (end - start) * t


def color_lerp(color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    """색상 보간"""
    return (
        int(interpolate(color1[0], color2[0], t)),
        int(interpolate(color1[1], color2[1], t)),
        int(interpolate(color1[2], color2[2], t))
    )
