#!/usr/bin/env python3
"""
게임 설정 관리
"""

import os
import json

class GameConfig:
    """게임 설정 클래스"""
    
    def __init__(self):
        # 설정 파일 경로
        self.settings_file = "game_settings.json"
        
        # 환경 변수에서 개발 모드 확인
        self.DEVELOPMENT_MODE = os.getenv('ROGUELIKE_DEV_MODE', 'false').lower() == 'true'
        
        # 설정 파일에서 개발모드 설정 확인 (배치파일에서 설정)
        try:
            if hasattr(self, 'DEVELOPMENT_MODE') and not self.DEVELOPMENT_MODE:
                # 현재 파일에서 개발모드 설정 확인
                with open(__file__, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'DEVELOPMENT_MODE = True' in content:
                        self.DEVELOPMENT_MODE = True
        except:
            pass
        
        # 개발모드 추가 설정
        self.DEBUG_MODE = getattr(self, 'DEBUG_MODE', self.DEVELOPMENT_MODE)
        self.UNLIMITED_ESSENCE = getattr(self, 'UNLIMITED_ESSENCE', self.DEVELOPMENT_MODE)
        self.ALL_CHARACTERS_UNLOCKED = getattr(self, 'ALL_CHARACTERS_UNLOCKED', self.DEVELOPMENT_MODE)
        
        # 개발자 전용 스토리 설정 (BGM 정상 재생을 위해 비활성화)
        self.FORCE_GLITCH_MODE = getattr(self, 'FORCE_GLITCH_MODE', False)  # 강제 글리치 모드 비활성화
        self.DISABLE_GLITCH_MODE = getattr(self, 'DISABLE_GLITCH_MODE', True)  # 글리치 모드 완전 비활성화
        self.FORCE_TRUE_ENDING = getattr(self, 'FORCE_TRUE_ENDING', False)  # 강제 진 엔딩 모드 비활성화
        
        # BGM 설정 (확장된 버전)
        self.BGM_SETTINGS = {
            "character_select": "prelude",  # 캐릭터 선택창 BGM
          #  "main_menu": "Main theme of FFVII",  # 메인화면 BGM
          #  "combat": "Battle on the Big Bridge",  # 전투 BGM
         #   "exploration": "Roaming Sheep",  # 탐험 BGM
         #   "village": "Hometown Domina",  # 마을 BGM
          #  "victory": "Victory Fanfare",  # 승리 BGM
           # "game_over": "Game Over",  # 게임 오버 BGM
            #"boss": "Dancing Mad"  # 보스 BGM
        }
        
        # 내구도 시스템 설정
        self.DURABILITY_ENABLED = True
        self.DURABILITY_LOSS_RATE_MULTIPLIER = 0.7  # 30% 감소된 내구도 손실률
        
        # ATB 시스템 설정 - 더 부드럽고 빠르게
        self.ATB_SETTINGS = {
            "animation_enabled": True,  # ATB 애니메이션 활성화
            "animation_fps": 60,        # 60FPS로 업데이트 (10→60 FPS)
            "update_speed": 1.0,        # ATB 증가 속도 배율 (1.0 = 기본 속도)
            "show_percentage": True,    # 퍼센트 표시
            "smooth_animation": True,   # 부드러운 애니메이션
            "frame_delay": 0.016        # ~60FPS (0.1→0.016초)
        }
        
        # 메타 진행 시스템 설정
        self.META_PROGRESSION_ENABLED = True
        self.STAR_FRAGMENT_DROP_RATE = 0.3 if self.DEVELOPMENT_MODE else 0.1
        self.MAX_STAR_FRAGMENTS = 9999
        
        # 장비 시스템 설정
        self.EQUIPMENT_VARIETY_ENABLED = True
        self.LEGENDARY_DROP_RATE = 0.05 if self.DEVELOPMENT_MODE else 0.01
        self.ARTIFACT_DROP_RATE = 0.01 if self.DEVELOPMENT_MODE else 0.001
        
        # 난이도 설정 (통합된 버전)
        self.DIFFICULTY_SETTINGS = {
            "평온": {
                "name": "평온한 여행",
                "description": "편안한 모험을 원하는 초보자를 위한 난이도",
                "enemy_hp_multiplier": 0.7,
                "enemy_damage_multiplier": 0.6,
                "player_damage_multiplier": 1.3,
                "exp_multiplier": 1.2,
                "gold_multiplier": 1.3,
                "star_fragment_multiplier": 0.8,  # 쉬운 난이도이므로 보상 감소
                "item_drop_rate": 1.4,
                "healing_effectiveness": 1.5,
                "wound_accumulation": 0.15,  # 받은 피해의 15%만 상처로
                "enemy_spawn_rate": 0.8,
                "boss_hp_multiplier": 0.8,
                "color": "🔵" 
            },
            "보통": {
                "name": "균형잡힌 모험",
                "description": "표준적인 로그라이크 경험을 제공하는 기본 난이도",
                "enemy_hp_multiplier": 1.0,
                "enemy_damage_multiplier": 1.0,
                "player_damage_multiplier": 1.0,
                "exp_multiplier": 1.0,
                "gold_multiplier": 1.0,
                "star_fragment_multiplier": 1.0,  # 기준 보상
                "item_drop_rate": 1.0,
                "healing_effectiveness": 1.0,
                "wound_accumulation": 0.25,  # 기본 25%
                "enemy_spawn_rate": 1.0,
                "boss_hp_multiplier": 1.0,
                "color": "🟢"
            },
            "도전": {
                "name": "시련의 여정",
                "description": "숙련된 플레이어를 위한 어려운 난이도",
                "enemy_hp_multiplier": 1.4,
                "enemy_damage_multiplier": 1.3,
                "player_damage_multiplier": 0.8,
                "exp_multiplier": 1.2,
                "gold_multiplier": 1.1,
                "star_fragment_multiplier": 1.3,  # 어려우므로 보상 증가
                "item_drop_rate": 0.9,
                "healing_effectiveness": 0.8,
                "wound_accumulation": 0.35,  # 받은 피해의 35%가 상처로
                "enemy_spawn_rate": 1.2,
                "boss_hp_multiplier": 1.5,
                "color": "🟠"
            },
            "악몽": {
                "name": "악몽 같은 시련",
                "description": "극한의 도전을 원하는 마스터를 위한 최고 난이도",
                "enemy_hp_multiplier": 1.8,
                "enemy_damage_multiplier": 1.6,
                "player_damage_multiplier": 0.7,
                "exp_multiplier": 1.5,
                "gold_multiplier": 1.2,
                "star_fragment_multiplier": 1.8,  # 매우 어려우므로 높은 보상
                "item_drop_rate": 0.8,
                "healing_effectiveness": 0.6,
                "wound_accumulation": 0.45,  # 받은 피해의 45%가 상처로
                "enemy_spawn_rate": 1.4,
                "boss_hp_multiplier": 2.0,
                "color": "❤️"
            },
            "지옥": {
                "name": "지옥의 심연",
                "description": "오직 전설의 용사만이 도전할 수 있는 절망적인 난이도",
                "enemy_hp_multiplier": 2.5,
                "enemy_damage_multiplier": 2.0,
                "player_damage_multiplier": 0.6,
                "exp_multiplier": 2.0,
                "gold_multiplier": 1.5,
                "star_fragment_multiplier": 2.5,  # 최고 난이도이므로 최고 보상
                "item_drop_rate": 0.7,
                "healing_effectiveness": 0.5,
                "wound_accumulation": 0.6,  # 받은 피해의 60%가 상처로
                "enemy_spawn_rate": 1.6,
                "boss_hp_multiplier": 3.0,
                "color": "💀"
            }
        }
        
        # 맵 크기 설정 (정사각형)
        self.MAP_SIZE_SETTINGS = {
            "작은 맵": {
                "name": "아늑한 던전",
                "color": "🟦",
                "description": "빠른 플레이를 위한 작은 던전",
                "width": 25,
                "height": 25,
                "room_count": 8,
                "corridor_complexity": 0.6
            },
            "보통 맵": {
                "name": "표준 던전",
                "color": "🟩",
                "description": "적당한 크기의 균형잡힌 던전",
                "width": 35,
                "height": 35,
                "room_count": 12,
                "corridor_complexity": 0.8
            },
            "큰 맵": {
                "name": "광활한 던전",
                "color": "🟨",
                "description": "탐험을 좋아하는 플레이어를 위한 큰 던전",
                "width": 50,
                "height": 50,
                "room_count": 18,
                "corridor_complexity": 1.0
            },
            "거대 맵": {
                "name": "미궁의 던전",
                "color": "🟪",
                "description": "장시간 탐험을 위한 거대한 미궁",
                "width": 70,
                "height": 70,
                "room_count": 25,
                "corridor_complexity": 1.2
            }
        }
        
        # 직업 해금 설정
        self.UNLOCKED_CLASSES = {
            "development": [
                "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크",
                "바드", "네크로맨서", "용기사", "검성", "정령술사", "암살자",
                "기계공학자", "무당", "해적", "사무라이", "드루이드", "철학자",
                "시간술사", "연금술사", "검투사", "기사", "신관", "마검사",
                "차원술사", "광전사"
            ],
            "normal": [
                "전사", "아크메이지", "궁수", "도적"  # 기본 4개 직업만 해금
            ]
        }
        
        # 패시브 해금 설정 (개발모드에서는 모든 패시브 해금)
        self.ALL_PASSIVES_UNLOCKED = self.DEVELOPMENT_MODE
        
        # 게임 밸런스 설정
        self.EXPERIENCE_MULTIPLIER = 2.0 if self.DEVELOPMENT_MODE else 1.0
        self.GOLD_MULTIPLIER = 2.0 if self.DEVELOPMENT_MODE else 1.0
        self.WOUND_HEALING_RATE = 0.25  # 상처 치유율 (25%)
        self.MAX_WOUND_PERCENTAGE = 0.75  # 최대 상처 비율 (75%)
        
        # 전투 시스템 설정
        self.ATB_SPEED_MULTIPLIER = 1.5 if self.DEVELOPMENT_MODE else 1.0
        self.CRITICAL_HIT_MULTIPLIER = 2.0
        self.ELEMENTAL_WEAKNESS_MULTIPLIER = 1.5
        
        # AI 시스템 설정 (확장된 버전)
        self.AI_DIFFICULTY = "normal"  # easy, normal, hard
        self.AI_LEARNING_ENABLED = True
        
        # 적 AI 행동 설정
        self.ENEMY_AI_SETTINGS = {
            "aggression_level": 0.7,  # 공격성 (0.0-1.0)
            "tactical_thinking": 0.8,  # 전술적 사고 (0.0-1.0)
            "group_coordination": 0.6,  # 집단 협력 (0.0-1.0)
            "retreat_threshold": 0.3,  # 후퇴 임계점 (HP 비율)
            "skill_usage_intelligence": 0.8,  # 스킬 사용 지능 (0.0-1.0)
            "target_prioritization": 0.9,  # 타겟 우선순위 지능 (0.0-1.0)
            "positioning_awareness": 0.7,  # 위치 인식 능력 (0.0-1.0)
            "reaction_speed": 1.0,  # 반응 속도 배수
            "learning_rate": 0.1 if self.DEVELOPMENT_MODE else 0.05,  # 학습률
            "memory_duration": 10,  # 기억 지속 턴 수
        }
        
        # 난이도별 적 AI 보정
        self.AI_DIFFICULTY_MODIFIERS = {
            "평온": {
                "aggression_multiplier": 0.6,
                "tactical_multiplier": 0.5,
                "skill_intelligence_multiplier": 0.4,
                "reaction_speed_multiplier": 0.7,
            },
            "보통": {
                "aggression_multiplier": 1.0,
                "tactical_multiplier": 1.0,
                "skill_intelligence_multiplier": 1.0,
                "reaction_speed_multiplier": 1.0,
            },
            "도전": {
                "aggression_multiplier": 1.3,
                "tactical_multiplier": 1.4,
                "skill_intelligence_multiplier": 1.5,
                "reaction_speed_multiplier": 1.2,
            },
            "악몽": {
                "aggression_multiplier": 1.6,
                "tactical_multiplier": 1.8,
                "skill_intelligence_multiplier": 2.0,
                "reaction_speed_multiplier": 1.5,
            },
            "지옥": {
                "aggression_multiplier": 2.0,
                "tactical_multiplier": 2.5,
                "skill_intelligence_multiplier": 3.0,
                "reaction_speed_multiplier": 2.0,
            }
        }
        
        # 디스플레이 설정 - 더 높은 FPS
        self.FULLSCREEN_MODE = True  # 터미널 창 최대화 기본 활성화
        self.WINDOW_WIDTH = 1200 if not self.FULLSCREEN_MODE else None
        self.WINDOW_HEIGHT = 800 if not self.FULLSCREEN_MODE else None
        self.FPS_LIMIT = 120  # 120 FPS로 증가 (60→120)
        self.VSYNC_ENABLED = True
        self.UI_SCALE = 1.0  # UI 크기 배율
        
        # 오디오 설정 (확장)
        self.MASTER_VOLUME = 0.8
        self.BGM_VOLUME = 0.7
        self.SFX_VOLUME = 0.9
        self.VOICE_VOLUME = 0.8
        self.AUDIO_QUALITY = "high"  # low, medium, high
        
        # 게임플레이 설정 (확장)
        self.AUTO_SAVE_ENABLED = True
        self.AUTO_SAVE_INTERVAL = 300  # 5분 (초 단위)
        self.PAUSE_ON_LOST_FOCUS = True
        self.CONFIRM_EXIT = True
        self.TUTORIAL_ENABLED = True
        self.TOOLTIPS_ENABLED = True
        self.CAMERA_SMOOTHING = True
        
        # 접근성 설정
        self.COLOR_BLIND_MODE = "none"  # none, protanopia, deuteranopia, tritanopia
        self.HIGH_CONTRAST_MODE = False
        self.LARGE_TEXT_MODE = False
        self.SCREEN_READER_SUPPORT = False
        
        # 컨트롤 설정
        self.MOUSE_SENSITIVITY = 1.0
        self.KEYBOARD_REPEAT_DELAY = 0.5
        self.GAMEPAD_ENABLED = True
        self.VIBRATION_ENABLED = True
        
        # 성능 설정
        self.TEXTURE_QUALITY = "high"  # low, medium, high, ultra
        self.SHADOW_QUALITY = "medium"  # off, low, medium, high
        self.PARTICLE_EFFECTS = True
        self.MOTION_BLUR = False
        self.ANTI_ALIASING = True
        
        # 네트워크 설정 (미래 확장용)
        self.ONLINE_FEATURES = False
        self.AUTO_UPLOAD_SAVES = False
        self.CLOUD_SYNC = False
        
        # 디버그 설정
        self.DEBUG_MODE = self.DEVELOPMENT_MODE
        self.SHOW_DAMAGE_CALCULATIONS = self.DEVELOPMENT_MODE
        self.INFINITE_RESOURCES = self.DEVELOPMENT_MODE
        
        # 현재 게임 설정
        self.current_difficulty = "보통"
        self.current_map_size = "보통 맵"
        
        # 설정 파일에서 설정 로드
        self.load_settings()
        
    def get_available_classes(self):
        """현재 모드에 따른 사용 가능한 직업 반환"""
        if self.DEVELOPMENT_MODE:
            return self.UNLOCKED_CLASSES["development"]
        else:
            return self.UNLOCKED_CLASSES["normal"]
    
    def is_class_unlocked(self, class_name: str) -> bool:
        """특정 직업이 해금되었는지 확인"""
        return class_name in self.get_available_classes()
    
    def are_all_passives_unlocked(self) -> bool:
        """모든 패시브가 해금되었는지 확인"""
        return self.ALL_PASSIVES_UNLOCKED
    
    def get_bgm_track(self, scene: str) -> str:
        """특정 장면의 BGM 트랙 반환"""
        return self.BGM_SETTINGS.get(scene, "default")
    
    def print_mode_info(self):
        """현재 모드 정보 출력"""
        mode = "개발 모드" if self.DEVELOPMENT_MODE else "일반 모드"
        difficulty_display = self.get_difficulty_display_name()
        map_display = self.get_map_display_name()
        ai_display = self.get_ai_difficulty_display()
        print(f"🎮 {mode}로 실행 중")
        print(f"⚔️ 난이도: {difficulty_display}")
        print(f"🗺️ 맵 크기: {map_display}")
        print(f"{ai_display}")
        print(f"📊 해금된 직업 수: {len(self.get_available_classes())}개")
        print(f"🎯 모든 패시브 해금: {'✅ 예' if self.ALL_PASSIVES_UNLOCKED else '❌ 아니오'}")
        print(f"⚔️ 내구도 시스템: {'✅ 활성화' if self.DURABILITY_ENABLED else '❌ 비활성화'}")
        print(f"⭐ 메타 진행: {'✅ 활성화' if self.META_PROGRESSION_ENABLED else '❌ 비활성화'}")
        print(f"🎵 BGM 트랙 수: {len(self.BGM_SETTINGS)}개")
        print(f"🧠 AI 학습: {'✅ 활성화' if self.AI_LEARNING_ENABLED else '❌ 비활성화'}")
        print(f"🖥️ 터미널 창 최대화: {'✅ 활성화' if self.FULLSCREEN_MODE else '❌ 비활성화'}")
        print(f"🔊 마스터 볼륨: {int(self.MASTER_VOLUME * 100)}%")
        print(f"💾 자동 저장: {'✅ 활성화' if self.AUTO_SAVE_ENABLED else '❌ 비활성화'}")
        print(f"🎓 튜토리얼: {'✅ 활성화' if self.TUTORIAL_ENABLED else '❌ 비활성화'}")
        print(f"🎨 접근성: {'고대비 모드' if self.HIGH_CONTRAST_MODE else '일반 모드'}")
    
    def print_all_settings(self):
        """모든 설정 상세 출력"""
        print("=" * 80)
        print("🔧 Dawn of Stellar - 게임 설정")
        print("=" * 80)
        
        print("\n📊 게임플레이 설정:")
        print(f"  ⚔️ 난이도: {self.get_difficulty_display_name()}")
        print(f"  🗺️ 맵 크기: {self.get_map_display_name()}")
        print(f"  💾 자동 저장: {'✅' if self.AUTO_SAVE_ENABLED else '❌'} ({self.AUTO_SAVE_INTERVAL//60}분 간격)")
        print(f"  🎓 튜토리얼: {'✅' if self.TUTORIAL_ENABLED else '❌'}")
        print(f"  💡 툴팁: {'✅' if self.TOOLTIPS_ENABLED else '❌'}")
        
        print("\n🖥️ 디스플레이 설정:")
        print(f"  📺 창 최대화: {'✅' if self.FULLSCREEN_MODE else '❌'}")
        if not self.FULLSCREEN_MODE:
            print(f"  📐 창 크기: {self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        print(f"  🎚️ UI 크기: {int(self.UI_SCALE * 100)}%")
        print(f"  ⚡ FPS 제한: {self.FPS_LIMIT}")
        
        print("\n🔊 오디오 설정:")
        print(f"  🎵 마스터 볼륨: {int(self.MASTER_VOLUME * 100)}%")
        print(f"  🎼 BGM 볼륨: {int(self.BGM_VOLUME * 100)}%")
        print(f"  🔔 효과음 볼륨: {int(self.SFX_VOLUME * 100)}%")
        print(f"  🎤 음성 볼륨: {int(self.VOICE_VOLUME * 100)}%")
        print(f"  🎧 오디오 품질: {self.AUDIO_QUALITY}")
        
        print("\n♿ 접근성 설정:")
        print(f"  🌈 색맹 지원: {self.COLOR_BLIND_MODE}")
        print(f"  🔳 고대비: {'✅' if self.HIGH_CONTRAST_MODE else '❌'}")
        print(f"  🔤 큰 텍스트: {'✅' if self.LARGE_TEXT_MODE else '❌'}")
        
        print("\n⚙️ 성능 설정:")
        print(f"  🖼️ 텍스처 품질: {self.TEXTURE_QUALITY}")
        print(f"  ✨ 파티클 효과: {'✅' if self.PARTICLE_EFFECTS else '❌'}")
        print(f"  🔄 수직 동기화: {'✅' if self.VSYNC_ENABLED else '❌'}")
        
        print("\n🤖 AI 설정:")
        print(f"  {self.get_ai_difficulty_display()}")
        print(f"  🧠 AI 학습: {'✅' if self.AI_LEARNING_ENABLED else '❌'}")
        
        print("=" * 80)
    
    # 난이도 관련 메서드들
    def set_difficulty(self, difficulty: str):
        """난이도 설정"""
        if difficulty in self.DIFFICULTY_SETTINGS:
            self.current_difficulty = difficulty
            self.save_settings()  # 설정 저장
            return True
        return False
    
    def get_difficulty_setting(self, setting_name: str):
        """현재 난이도의 특정 설정값 반환"""
        difficulty_data = self.DIFFICULTY_SETTINGS.get(self.current_difficulty, self.DIFFICULTY_SETTINGS["보통"])
        return difficulty_data.get(setting_name, 1.0)
    
    def get_difficulty_info(self, difficulty: str = None):
        """난이도 정보 반환"""
        if difficulty is None:
            difficulty = self.current_difficulty
        return self.DIFFICULTY_SETTINGS.get(difficulty, self.DIFFICULTY_SETTINGS["보통"])
    
    def get_all_difficulties(self):
        """모든 난이도 목록 반환"""
        return list(self.DIFFICULTY_SETTINGS.keys())
    
    def get_difficulty_display_name(self, difficulty: str = None):
        """난이도 표시 이름 반환"""
        if difficulty is None:
            difficulty = self.current_difficulty
        difficulty_info = self.get_difficulty_info(difficulty)
        return f"{difficulty_info['color']} {difficulty_info['name']}"
    
    # 맵 크기 관련 메서드들
    def set_map_size(self, map_size: str):
        """맵 크기 설정"""
        if map_size in self.MAP_SIZE_SETTINGS:
            self.current_map_size = map_size
            self.save_settings()  # 설정 저장
            return True
        return False
    
    def get_map_setting(self, setting_name: str):
        """현재 맵 크기의 특정 설정값 반환"""
        map_data = self.MAP_SIZE_SETTINGS.get(self.current_map_size, self.MAP_SIZE_SETTINGS["보통 맵"])
        return map_data.get(setting_name, 35)
    
    def get_map_info(self, map_size: str = None):
        """맵 크기 정보 반환"""
        if map_size is None:
            map_size = self.current_map_size
        return self.MAP_SIZE_SETTINGS.get(map_size, self.MAP_SIZE_SETTINGS["보통 맵"])
    
    def get_all_map_sizes(self):
        """모든 맵 크기 목록 반환"""
        return list(self.MAP_SIZE_SETTINGS.keys())
    
    def get_map_dimensions(self):
        """현재 설정된 맵 크기 반환 (width, height)"""
        map_info = self.get_map_info()
        return map_info['width'], map_info['height']
    
    def get_map_display_name(self, map_size: str = None):
        """맵 크기 표시 이름 반환"""
        if map_size is None:
            map_size = self.current_map_size
        map_info = self.get_map_info(map_size)
        return f"{map_info['color']} {map_info['name']}"
    
    def get_map_size_display_name(self, map_size: str = None):
        """맵 크기 표시 이름 반환 (별칭)"""
        return self.get_map_display_name(map_size)
    
    def get_map_size_info(self, map_size: str = None):
        """맵 크기 정보 반환 (별칭)"""
        return self.get_map_info(map_size)
    
    def get_durability_settings(self):
        """내구도 관련 설정 반환"""
        return {
            "enabled": self.DURABILITY_ENABLED,
            "loss_rate_multiplier": self.DURABILITY_LOSS_RATE_MULTIPLIER,
            "repair_cost_multiplier": 1.0
        }
    
    def get_meta_progression_settings(self):
        """메타 진행 관련 설정 반환"""
        return {
            "enabled": self.META_PROGRESSION_ENABLED,
            "star_fragment_drop_rate": self.STAR_FRAGMENT_DROP_RATE,
            "max_star_fragments": self.MAX_STAR_FRAGMENTS
        }
    
    def get_equipment_settings(self):
        """장비 관련 설정 반환"""
        return {
            "variety_enabled": self.EQUIPMENT_VARIETY_ENABLED,
            "legendary_drop_rate": self.LEGENDARY_DROP_RATE,
            "artifact_drop_rate": self.ARTIFACT_DROP_RATE
        }
    
    # AI 관련 메서드들
    def get_enemy_ai_setting(self, setting_name: str, difficulty: str = None):
        """현재 난이도에 맞는 적 AI 설정값 반환"""
        if difficulty is None:
            difficulty = self.current_difficulty
        
        base_value = self.ENEMY_AI_SETTINGS.get(setting_name, 1.0)
        modifier_key = setting_name.replace("_level", "_multiplier").replace("_thinking", "_multiplier").replace("_coordination", "_multiplier").replace("_intelligence", "_multiplier").replace("_awareness", "_multiplier").replace("_speed", "_multiplier")
        
        # 난이도별 보정값 적용
        modifier = self.AI_DIFFICULTY_MODIFIERS.get(difficulty, self.AI_DIFFICULTY_MODIFIERS["보통"]).get(modifier_key, 1.0)
        
        return min(base_value * modifier, 3.0)  # 최대 3.0으로 제한
    
    def get_ai_settings_for_difficulty(self, difficulty: str = None):
        """특정 난이도의 모든 AI 설정 반환"""
        if difficulty is None:
            difficulty = self.current_difficulty
        
        ai_settings = {}
        for setting_name in self.ENEMY_AI_SETTINGS.keys():
            ai_settings[setting_name] = self.get_enemy_ai_setting(setting_name, difficulty)
        
        return ai_settings
    
    def is_ai_learning_enabled(self):
        """AI 학습 기능 활성화 여부"""
        return self.AI_LEARNING_ENABLED
    
    def get_ai_difficulty_display(self):
        """현재 난이도의 AI 난이도 표시"""
        difficulty = self.current_difficulty
        modifiers = self.AI_DIFFICULTY_MODIFIERS.get(difficulty, self.AI_DIFFICULTY_MODIFIERS["보통"])
        
        avg_multiplier = sum(modifiers.values()) / len(modifiers)
        
        if avg_multiplier <= 0.7:
            return "🤖 AI: 초보자 친화적"
        elif avg_multiplier <= 1.0:
            return "🤖 AI: 균형잡힌"
        elif avg_multiplier <= 1.5:
            return "🤖 AI: 도전적"
        elif avg_multiplier <= 2.0:
            return "🤖 AI: 매우 어려움"
        else:
            return "🤖 AI: 극한 난이도"
    
    # 디스플레이 설정 메서드들
    def set_fullscreen(self, enabled: bool):
        """전체화면 모드 설정"""
        self.FULLSCREEN_MODE = enabled
        self.save_settings()
        return enabled
    
    def get_window_size(self):
        """창 크기 반환"""
        if self.FULLSCREEN_MODE:
            return None, None  # 전체화면에서는 None
        return self.WINDOW_WIDTH, self.WINDOW_HEIGHT
    
    def set_window_size(self, width: int, height: int):
        """창 크기 설정"""
        self.WINDOW_WIDTH = max(800, min(width, 2560))  # 800~2560 제한
        self.WINDOW_HEIGHT = max(600, min(height, 1440))  # 600~1440 제한
        self.save_settings()
    
    def set_ui_scale(self, scale: float):
        """UI 크기 배율 설정"""
        self.UI_SCALE = max(0.5, min(scale, 2.0))  # 0.5~2.0 제한
        self.save_settings()
    
    # 오디오 설정 메서드들
    def set_master_volume(self, volume: float):
        """마스터 볼륨 설정"""
        self.MASTER_VOLUME = max(0.0, min(volume, 1.0))
        self.save_settings()
    
    def set_bgm_volume(self, volume: float):
        """BGM 볼륨 설정"""
        self.BGM_VOLUME = max(0.0, min(volume, 1.0))
        self.save_settings()
    
    def set_sfx_volume(self, volume: float):
        """효과음 볼륨 설정"""
        self.SFX_VOLUME = max(0.0, min(volume, 1.0))
        self.save_settings()
    
    def get_audio_settings(self):
        """모든 오디오 설정 반환"""
        return {
            "master_volume": self.MASTER_VOLUME,
            "bgm_volume": self.BGM_VOLUME,
            "sfx_volume": self.SFX_VOLUME,
            "voice_volume": self.VOICE_VOLUME,
            "audio_quality": self.AUDIO_QUALITY
        }
    
    # 게임플레이 설정 메서드들
    def toggle_auto_save(self):
        """자동 저장 토글"""
        self.AUTO_SAVE_ENABLED = not self.AUTO_SAVE_ENABLED
        self.save_settings()
        return self.AUTO_SAVE_ENABLED
    
    def set_auto_save_interval(self, seconds: int):
        """자동 저장 간격 설정 (초)"""
        self.AUTO_SAVE_INTERVAL = max(60, min(seconds, 1800))  # 1분~30분 제한
        self.save_settings()
    
    def toggle_tutorial(self):
        """튜토리얼 토글"""
        self.TUTORIAL_ENABLED = not self.TUTORIAL_ENABLED
        self.save_settings()
        return self.TUTORIAL_ENABLED
    
    def toggle_tooltips(self):
        """툴팁 토글"""
        self.TOOLTIPS_ENABLED = not self.TOOLTIPS_ENABLED
        self.save_settings()
        return self.TOOLTIPS_ENABLED
    
    # 접근성 설정 메서드들
    def set_color_blind_mode(self, mode: str):
        """색맹 지원 모드 설정"""
        valid_modes = ["none", "protanopia", "deuteranopia", "tritanopia"]
        if mode in valid_modes:
            self.COLOR_BLIND_MODE = mode
            self.save_settings()
            return True
        return False
    
    def toggle_high_contrast(self):
        """고대비 모드 토글"""
        self.HIGH_CONTRAST_MODE = not self.HIGH_CONTRAST_MODE
        self.save_settings()
        return self.HIGH_CONTRAST_MODE
    
    def toggle_large_text(self):
        """큰 텍스트 모드 토글"""
        self.LARGE_TEXT_MODE = not self.LARGE_TEXT_MODE
        self.save_settings()
        return self.LARGE_TEXT_MODE
    
    # 성능 설정 메서드들
    def set_texture_quality(self, quality: str):
        """텍스처 품질 설정"""
        valid_qualities = ["low", "medium", "high", "ultra"]
        if quality in valid_qualities:
            self.TEXTURE_QUALITY = quality
            self.save_settings()
            return True
        return False
    
    def toggle_particle_effects(self):
        """파티클 효과 토글"""
        self.PARTICLE_EFFECTS = not self.PARTICLE_EFFECTS
        self.save_settings()
        return self.PARTICLE_EFFECTS
    
    def toggle_development_mode(self):
        """개발자 모드 토글"""
        self.DEVELOPMENT_MODE = not self.DEVELOPMENT_MODE
        self.save_settings()
        return self.DEVELOPMENT_MODE
    
    def toggle_force_glitch_mode(self):
        """강제 글리치 모드 토글 (개발자 전용)"""
        self.FORCE_GLITCH_MODE = not self.FORCE_GLITCH_MODE
        # 강제 글리치 모드가 켜지면 비활성화 모드는 자동으로 꺼짐
        if self.FORCE_GLITCH_MODE:
            self.DISABLE_GLITCH_MODE = False
        self.save_settings()
        return self.FORCE_GLITCH_MODE
    
    def toggle_disable_glitch_mode(self):
        """글리치 모드 비활성화 토글 (개발자 전용)"""
        self.DISABLE_GLITCH_MODE = not self.DISABLE_GLITCH_MODE
        # 비활성화 모드가 켜지면 강제 모드는 자동으로 꺼짐
        if self.DISABLE_GLITCH_MODE:
            self.FORCE_GLITCH_MODE = False
        self.save_settings()
        return self.DISABLE_GLITCH_MODE
    
    def reset_glitch_mode_settings(self):
        """글리치 모드 설정 초기화 (개발자 전용)"""
        self.FORCE_GLITCH_MODE = False
        self.DISABLE_GLITCH_MODE = False
        self.save_settings()
        return True
    
    def toggle_force_true_ending(self):
        """강제 진 엔딩 모드 토글 (개발자 전용)"""
        self.FORCE_TRUE_ENDING = not self.FORCE_TRUE_ENDING
        self.save_settings()
        return self.FORCE_TRUE_ENDING
    
    def reset_story_mode_settings(self):
        """스토리 모드 설정 전체 초기화 (개발자 전용)"""
        self.FORCE_GLITCH_MODE = False
        self.DISABLE_GLITCH_MODE = False
        self.FORCE_TRUE_ENDING = False
        self.save_settings()
        return True
    
    def get_performance_settings(self):
        """성능 설정 반환"""
        return {
            "texture_quality": self.TEXTURE_QUALITY,
            "shadow_quality": self.SHADOW_QUALITY,
            "particle_effects": self.PARTICLE_EFFECTS,
            "motion_blur": self.MOTION_BLUR,
            "anti_aliasing": self.ANTI_ALIASING,
            "fps_limit": self.FPS_LIMIT,
            "vsync": self.VSYNC_ENABLED
        }
    
    def apply_terminal_fullscreen(self):
        """전체화면 모드 조용히 적용"""
        if self.FULLSCREEN_MODE:
            # 전체화면 모드 설정은 터미널 환경에서 자동으로 처리
            # 안내 메시지 제거 - 게임 플레이에 방해되지 않도록
            pass
    
    def restore_window_mode(self):
        """전체화면 해제 안내"""
        print("\n💡 전체화면을 해제하려면:")
        print("   • F11 키를 다시 누르세요")
        print("   • 또는 ESC 키를 누르세요")
        print("   • Alt + Tab으로 다른 창으로 전환할 수도 있습니다")
        return True
    
    def set_terminal_size(self, width: int = None, height: int = None):
        """터미널 크기 설정 안내"""
        print("\n📏 터미널 크기 조정:")
        print("   • 대부분의 터미널에서는 마우스로 창 테두리를 드래그하여 크기 조정")
        print("   • 또는 터미널 설정에서 글꼴 크기 변경")
        print("   • F11으로 전체화면하면 자동으로 최적 크기가 됩니다")
        return True
    
    def get_optimal_settings_for_system(self):
        """시스템에 최적화된 설정 반환"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            return {
                "fullscreen": True,
                "terminal_width": 120,
                "terminal_height": 35,
                "fps_limit": 60,
                "vsync": True
            }
        elif system == "Linux" or system == "Darwin":  # macOS
            return {
                "fullscreen": False,
                "terminal_width": 100,
                "terminal_height": 30,
                "fps_limit": 30,
                "vsync": False
            }
        else:
            return {
                "fullscreen": False,
                "terminal_width": 80,
                "terminal_height": 25,
                "fps_limit": 30,
                "vsync": False
            }
    
    def load_settings(self):
        """설정 파일에서 설정 로드"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # gameplay 설정에서 난이도와 맵 크기 로드
                gameplay = settings.get('gameplay', {})
                
                # 난이도 설정 로드 (한국어 매핑)
                difficulty_mapping = {
                    "easy": "평온",
                    "normal": "보통", 
                    "hard": "도전",
                    "nightmare": "악몽",
                    "hell": "지옥"
                }
                
                saved_difficulty = gameplay.get('difficulty', 'normal')
                if saved_difficulty in difficulty_mapping:
                    self.current_difficulty = difficulty_mapping[saved_difficulty]
                elif saved_difficulty in self.DIFFICULTY_SETTINGS:
                    self.current_difficulty = saved_difficulty
                
                # 맵 크기 설정 로드
                map_size_mapping = {
                    "small": "작은 맵",
                    "normal": "보통 맵",
                    "large": "큰 맵", 
                    "huge": "거대 맵"
                }
                
                saved_map_size = gameplay.get('map_size', 'normal')
                if saved_map_size in map_size_mapping:
                    self.current_map_size = map_size_mapping[saved_map_size]
                elif saved_map_size in self.MAP_SIZE_SETTINGS:
                    self.current_map_size = saved_map_size
                
                # 게임플레이 설정 로드
                self.AUTO_SAVE_ENABLED = gameplay.get('auto_save', self.AUTO_SAVE_ENABLED)
                self.AUTO_SAVE_INTERVAL = gameplay.get('auto_save_interval', self.AUTO_SAVE_INTERVAL)
                self.PAUSE_ON_LOST_FOCUS = gameplay.get('pause_on_lost_focus', self.PAUSE_ON_LOST_FOCUS)
                self.CONFIRM_EXIT = gameplay.get('confirm_exit', self.CONFIRM_EXIT)
                self.TUTORIAL_ENABLED = gameplay.get('tutorial_enabled', self.TUTORIAL_ENABLED)
                self.TOOLTIPS_ENABLED = gameplay.get('tooltips_enabled', self.TOOLTIPS_ENABLED)
                self.CAMERA_SMOOTHING = gameplay.get('camera_smoothing', self.CAMERA_SMOOTHING)
                self.DEVELOPMENT_MODE = gameplay.get('development_mode', self.DEVELOPMENT_MODE)  # 개발자 모드 추가
                
                # 개발자 전용 글리치 모드 설정 로드
                self.FORCE_GLITCH_MODE = gameplay.get('force_glitch_mode', self.FORCE_GLITCH_MODE)
                self.DISABLE_GLITCH_MODE = gameplay.get('disable_glitch_mode', self.DISABLE_GLITCH_MODE)
                self.FORCE_TRUE_ENDING = gameplay.get('force_true_ending', self.FORCE_TRUE_ENDING)
                
                # 디스플레이 설정 로드
                display = settings.get('display', {})
                self.FULLSCREEN_MODE = display.get('fullscreen', self.FULLSCREEN_MODE)
                self.WINDOW_WIDTH = display.get('window_width', self.WINDOW_WIDTH)
                self.WINDOW_HEIGHT = display.get('window_height', self.WINDOW_HEIGHT)
                self.FPS_LIMIT = display.get('fps_limit', self.FPS_LIMIT)
                self.VSYNC_ENABLED = display.get('vsync', self.VSYNC_ENABLED)
                self.UI_SCALE = display.get('ui_scale', self.UI_SCALE)
                
                # 오디오 설정 로드
                audio = settings.get('audio', {})
                self.MASTER_VOLUME = audio.get('master_volume', self.MASTER_VOLUME)
                self.BGM_VOLUME = audio.get('bgm_volume', self.BGM_VOLUME)
                self.SFX_VOLUME = audio.get('sfx_volume', self.SFX_VOLUME)
                self.VOICE_VOLUME = audio.get('voice_volume', self.VOICE_VOLUME)
                self.AUDIO_QUALITY = audio.get('audio_quality', self.AUDIO_QUALITY)
                
                # 접근성 설정 로드
                accessibility = settings.get('accessibility', {})
                self.COLOR_BLIND_MODE = accessibility.get('color_blind_mode', self.COLOR_BLIND_MODE)
                self.HIGH_CONTRAST_MODE = accessibility.get('high_contrast', self.HIGH_CONTRAST_MODE)
                self.LARGE_TEXT_MODE = accessibility.get('large_text', self.LARGE_TEXT_MODE)
                self.SCREEN_READER_SUPPORT = accessibility.get('screen_reader_support', self.SCREEN_READER_SUPPORT)
                
                # 컨트롤 설정 로드
                controls = settings.get('controls', {})
                self.MOUSE_SENSITIVITY = controls.get('mouse_sensitivity', self.MOUSE_SENSITIVITY)
                self.KEYBOARD_REPEAT_DELAY = controls.get('keyboard_repeat_delay', self.KEYBOARD_REPEAT_DELAY)
                self.GAMEPAD_ENABLED = controls.get('gamepad_enabled', self.GAMEPAD_ENABLED)
                self.VIBRATION_ENABLED = controls.get('vibration_enabled', self.VIBRATION_ENABLED)
                
                # 성능 설정 로드
                performance = settings.get('performance', {})
                self.TEXTURE_QUALITY = performance.get('texture_quality', self.TEXTURE_QUALITY)
                self.SHADOW_QUALITY = performance.get('shadow_quality', self.SHADOW_QUALITY)
                self.PARTICLE_EFFECTS = performance.get('particle_effects', self.PARTICLE_EFFECTS)
                self.MOTION_BLUR = performance.get('motion_blur', self.MOTION_BLUR)
                self.ANTI_ALIASING = performance.get('anti_aliasing', self.ANTI_ALIASING)
                
                # 네트워크 설정 로드
                network = settings.get('network', {})
                self.ONLINE_FEATURES = network.get('online_features', self.ONLINE_FEATURES)
                self.AUTO_UPLOAD_SAVES = network.get('auto_upload_saves', self.AUTO_UPLOAD_SAVES)
                self.CLOUD_SYNC = network.get('cloud_sync', self.CLOUD_SYNC)
                
                # ATB 설정 로드 (새로 추가)
                atb = settings.get('atb', {})
                self.ATB_SETTINGS.update({
                    'animation_enabled': atb.get('animation_enabled', self.ATB_SETTINGS.get('animation_enabled', True)),
                    'animation_fps': atb.get('animation_fps', self.ATB_SETTINGS.get('animation_fps', 20)),
                    'update_speed': atb.get('update_speed', self.ATB_SETTINGS.get('update_speed', 1.0)),
                    'show_percentage': atb.get('show_percentage', self.ATB_SETTINGS.get('show_percentage', True)),
                    'smooth_animation': atb.get('smooth_animation', self.ATB_SETTINGS.get('smooth_animation', True)),
                    'frame_delay': atb.get('frame_delay', self.ATB_SETTINGS.get('frame_delay', 0.05))
                })
                    
        except Exception as e:
            print(f"⚠️ 설정 로드 중 오류: {e}")
            # 기본값 유지
            self.current_difficulty = "보통"
            self.current_map_size = "보통 맵"
    
    def save_settings(self):
        """현재 설정을 파일에 저장"""
        try:
            # 기존 설정 파일 로드 (있다면)
            settings = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # 각 섹션이 없다면 생성
            sections = ['gameplay', 'display', 'audio', 'accessibility', 'controls', 'performance', 'network']
            for section in sections:
                if section not in settings:
                    settings[section] = {}
            
            # 난이도를 영어로 변환하여 저장
            difficulty_reverse_mapping = {
                "평온": "easy",
                "보통": "normal",
                "도전": "hard", 
                "악몽": "nightmare",
                "지옥": "hell"
            }
            
            # 맵 크기를 영어로 변환하여 저장
            map_size_reverse_mapping = {
                "작은 맵": "small",
                "보통 맵": "normal",
                "큰 맵": "large",
                "거대 맵": "huge"
            }
            
            # 게임플레이 설정 업데이트
            settings['gameplay'].update({
                'difficulty': difficulty_reverse_mapping.get(self.current_difficulty, 'normal'),
                'map_size': map_size_reverse_mapping.get(self.current_map_size, 'normal'),
                'auto_save': self.AUTO_SAVE_ENABLED,
                'auto_save_interval': self.AUTO_SAVE_INTERVAL,
                'pause_on_lost_focus': self.PAUSE_ON_LOST_FOCUS,
                'confirm_exit': self.CONFIRM_EXIT,
                'tutorial_enabled': self.TUTORIAL_ENABLED,
                'tooltips_enabled': self.TOOLTIPS_ENABLED,
                'camera_smoothing': self.CAMERA_SMOOTHING,
                'development_mode': self.DEVELOPMENT_MODE,  # 개발자 모드 추가
                'force_glitch_mode': self.FORCE_GLITCH_MODE,  # 강제 글리치 모드
                'disable_glitch_mode': self.DISABLE_GLITCH_MODE,  # 글리치 모드 비활성화
                'force_true_ending': self.FORCE_TRUE_ENDING  # 강제 진 엔딩 모드
            })
            
            # 디스플레이 설정 업데이트
            settings['display'].update({
                'fullscreen': self.FULLSCREEN_MODE,
                'window_width': self.WINDOW_WIDTH,
                'window_height': self.WINDOW_HEIGHT,
                'fps_limit': self.FPS_LIMIT,
                'vsync': self.VSYNC_ENABLED,
                'ui_scale': self.UI_SCALE
            })
            
            # 오디오 설정 업데이트
            settings['audio'].update({
                'master_volume': self.MASTER_VOLUME,
                'bgm_volume': self.BGM_VOLUME,
                'sfx_volume': self.SFX_VOLUME,
                'voice_volume': self.VOICE_VOLUME,
                'audio_quality': self.AUDIO_QUALITY
            })
            
            # 접근성 설정 업데이트
            settings['accessibility'].update({
                'color_blind_mode': self.COLOR_BLIND_MODE,
                'high_contrast': self.HIGH_CONTRAST_MODE,
                'large_text': self.LARGE_TEXT_MODE,
                'screen_reader_support': self.SCREEN_READER_SUPPORT
            })
            
            # 컨트롤 설정 업데이트
            settings['controls'].update({
                'mouse_sensitivity': self.MOUSE_SENSITIVITY,
                'keyboard_repeat_delay': self.KEYBOARD_REPEAT_DELAY,
                'gamepad_enabled': self.GAMEPAD_ENABLED,
                'vibration_enabled': self.VIBRATION_ENABLED
            })
            
            # 성능 설정 업데이트
            settings['performance'].update({
                'texture_quality': self.TEXTURE_QUALITY,
                'shadow_quality': self.SHADOW_QUALITY,
                'particle_effects': self.PARTICLE_EFFECTS,
                'motion_blur': self.MOTION_BLUR,
                'anti_aliasing': self.ANTI_ALIASING
            })
            
            # 네트워크 설정 업데이트
            settings['network'].update({
                'online_features': self.ONLINE_FEATURES,
                'auto_upload_saves': self.AUTO_UPLOAD_SAVES,
                'cloud_sync': self.CLOUD_SYNC
            })
            
            # ATB 설정 업데이트 (새로 추가)
            settings['atb'] = {
                'animation_enabled': self.ATB_SETTINGS.get('animation_enabled', True),
                'animation_fps': self.ATB_SETTINGS.get('animation_fps', 20),
                'update_speed': self.ATB_SETTINGS.get('update_speed', 1.0),
                'show_percentage': self.ATB_SETTINGS.get('show_percentage', True),
                'smooth_animation': self.ATB_SETTINGS.get('smooth_animation', True),
                'frame_delay': self.ATB_SETTINGS.get('frame_delay', 0.05)
            }
            
            # 파일에 저장
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"⚠️ 설정 저장 중 오류: {e}")
            return False
    
    def update_atb_setting(self, setting_name: str, value):
        """ATB 설정 업데이트"""
        if setting_name in self.ATB_SETTINGS:
            old_value = self.ATB_SETTINGS[setting_name]
            self.ATB_SETTINGS[setting_name] = value
            self.save_settings()  # 즉시 저장
            print(f"⚙️ ATB 설정 업데이트: {setting_name} {old_value} → {value}")
            return True
        else:
            print(f"⚠️ 알 수 없는 ATB 설정: {setting_name}")
            return False
    
    def get_atb_setting(self, setting_name: str, default=None):
        """ATB 설정 값 가져오기"""
        return self.ATB_SETTINGS.get(setting_name, default)

# 전역 설정 인스턴스
game_config = GameConfig()
