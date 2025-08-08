import pygame
import os
import random
import time
from typing import Optional, Dict, List
from pathlib import Path

class UnifiedAudioSystem:
    """통합 오디오 시스템 - BGM과 효과음 통합 관리"""
    
    def __init__(self, debug_mode: bool = False):
        self.initialized = False
        self.debug_mode = debug_mode
        self.current_bgm = None
        self.bgm_volume = 0.6
        self.sfx_volume = 0.8  # 원래대로 복구
        self.master_volume = 0.7
        
        # 사운드 저장소
        self.bgm_tracks = {}
        self.sfx_sounds = {}
        self.sounds = {}  # 통합 사운드 딕셔너리
        
        # 경로 설정 - 새로운 game/audio 구조 사용
        self.base_path = Path("game/audio")
        self.bgm_path = self.base_path / "bgm"
        self.sfx_path = self.base_path / "sfx"
        
        # pygame mixer 초기화 시도
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)  # 여러 사운드 동시 재생
            self.initialized = True
            if self.debug_mode:
                print("🎵 통합 오디오 시스템 초기화 완료!")
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ 오디오 시스템 초기화 실패: {e}")
            self.initialized = False
        
        # 사운드 시스템 초기화
        self._initialize_sound_mappings()
        self._create_audio_directories()
    
    def _create_audio_directories(self):
        """오디오 디렉토리 생성"""
        try:
            os.makedirs(self.bgm_path, exist_ok=True)
            os.makedirs(self.sfx_path, exist_ok=True)
            if self.debug_mode:
                print("📁 오디오 디렉토리 확인 완료")
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ 디렉토리 생성 실패: {e}")
    
    def _initialize_sound_mappings(self):
        """사운드 매핑 초기화"""
        # FFVII BGM 매핑 (게임 상황별)
        self.bgm_mapping = {
            # 메인 테마들
            'title': '01-The Prelude.mp3',
            'main_theme': '25-Main Theme of Final Fantasy VII.mp3',
            'menu_theme': '01-The Prelude.mp3',
            'prelude': '01-The Prelude.mp3',
            
            # 캐릭터/평화로운 테마
            'character_select': '06-Tifa\'s Theme.mp3',
            'tifa_theme': '06-Tifa\'s Theme.mp3',
            'peaceful': '26-Ahead on Our Way.mp3',
            'safe_area': '13-Flowers Blooming in the Church.mp3',
            
            # 던전 테마들 (층별)
            'dungeon': '04-Mako Reactor.mp3',
            'dungeon_theme': '04-Mako Reactor.mp3',
            'dungeon_deep': '09-Lurking in the Darkness.mp3',
            'mysterious': '33-Chasing the Black-Caped Man.mp3',
            'cave': '46-Cosmo Canyon.mp3',
            
            # 전투 테마들
            'battle': '11-Fighting.mp3',
            'boss_battle': '21-Still More Fighting.mp3',
            'boss_theme': '21-Still More Fighting.mp3',
            'final_boss': '38-J-E-N-O-V-A.mp3',
            'epic_battle': '87-One-Winged Angel.mp3',
            
            # 이벤트 테마들
            'victory': '12-Fanfare.mp3',
            'success': '59-A Great Success.mp3',
            'game_over': '39-Continue.mp3',
            'tension': '05-Anxious Heart.mp3',
            'urgent': '08-Hurry!.mp3',
            
            # 기존 호환성을 위한 매핑
            'bombing_mission': '03-Bombing Mission.mp3',
            'mako_reactor': '04-Mako Reactor.mp3',
        }
        
        # FFVII SFX 매핑 (정확한 파일명 기반)
        self.sfx_mapping = {
            # UI 사운드
            'menu_select': '000.wav',      # 커서 이동
            'menu_confirm': '001.wav',     # 세이브 완료/확인
            'menu_cancel': '003.wav',      # 취소
            'menu_error': '002.wav',       # 잘못된 선택
            
            # 전투 사운드 - 물리 공격
            'sword_hit': '017.wav',        # 클라우드 검 타격
            'critical_hit': '026.wav',     # 클라우드 크리티컬
            'gun_hit': '014.wav',          # 바렛 총 타격
            'gun_critical': '045.wav',     # 바렛 크리티컬
            'staff_hit': '049.wav',        # 에어리스 스태프
            'staff_critical': '022.wav',   # 에어리스 크리티컬
            'punch_hit': '027.wav',        # 티파 펀치
            'punch_critical': '289.wav',   # 티파 크리티컬
            'miss': '004.wav',             # 공격 빗나감
            
            # 마법 사운드
            'magic_cast': '012.wav',       # 마법 시전 준비
            'fire': '008.wav',             # 파이어
            'fire2': '009.wav',            # 파이어2
            'fire3': '141.wav',            # 파이어3
            'ice': '023.wav',              # 아이스
            'ice3': '028.wav',             # 아이스3
            'thunder': '010.wav',          # 볼트
            'thunder2': '011.wav',         # 볼트2
            'thunder3': '069.wav',         # 볼트3
            'heal': '005.wav',             # 케알
            'heal2': '007.wav',            # 케알2
            'heal3': '068.wav',            # 케알3
            'ultima': '307.wav',           # 알테마
            
            # 상태 마법
            'haste': '082.wav',            # 헤이스트
            'slow': '064.wav',             # 슬로우
            'protect': '093.wav',          # 프로텍트
            'shell': '066.wav',            # 쉘
            'barrier': '067.wav',          # 배리어
            'reflect': '071.wav',          # 리플렉트
            'sleep': '072.wav',            # 슬립
            'poison': '062.wav',           # 바이오
            'silence': '083.wav',          # 사일런스
            'stop': '086.wav',             # 스톱
            'berserk': '065.wav',          # 버서크
            
            # 아이템 사운드
            'item_use': '020.wav',         # 아이템 사용
            'potion': '005.wav',           # 포션
            'hi_potion': '006.wav',        # 하이포션
            'x_potion': '007.wav',         # 엑스포션
            'elixir': '068.wav',           # 엘릭서
            'phoenix_down': '379.wav',     # 피닉스테일
            'item_pickup': '357.wav',      # 아이템 획득
            'treasure_open': '253.wav',    # 보물상자
            'equip': '444.wav',            # 장비 장착
            
            # 전투 상황
            'battle_start': '042.wav',     # 전투 시작 소용돌이
            'victory': '012.wav',          # 승리 팡파레
            'escape': '025.wav',           # 전투 도망
            'enemy_death': '021.wav',      # 적 사망
            'boss_death': '445.wav',       # 보스 사망
            'level_up': '381.wav',         # 레벨업/4번째 리미트 습득
            
            # 리미트 브레이크
            'limit_break': '035.wav',      # 리미트 브레이크 발동
            'blade_beam': '368.wav',       # 클라우드 블레이드빔
            'big_shot': '039.wav',         # 바렛 빅샷
            'healing_wind': '033.wav',     # 에어리스 치유의바람
            'somersault': '290.wav',       # 티파 공중제비
            
            # 환경 사운드
            'door_open': '121.wav',        # 문 열기
            'door_close': '052.wav',       # 문 닫기
            'elevator': '041.wav',         # 엘리베이터
            'save_point': '356.wav',       # 세이브 포인트
            'save_complete': '206.wav',    # 세이브 완료
            'footsteps': '027.wav',        # 발소리
            'jumping': '054.wav',          # 점프
            'landing': '055.wav',          # 착지
            
            # 시스템 사운드
            'coin': '170.wav',             # 길/돈
            'buy_item': '261.wav',         # 아이템 구매
            'points_earned': '485.wav',    # 포인트/GP 획득
            'winning_prize': '250.wav',    # 특별한 보상 획득
            'applause': '438.wav',         # 박수
            'materia_glow': '190.wav',     # 마테리아 빛남/소환
            
            # 특수 효과
            'summon': '190.wav',           # 소환수 등장
            'vanish': '040.wav',           # 소환을 위한 파티 사라짐
            'transform': '266.wav',        # 변신/기계 반응
            'teleport': '054.wav',         # 순간이동/점프
            'chocobo_happy': '273.wav',    # 초코보 기쁨
            'chocobo_sad': '272.wav',      # 초코보 슬픔
            'moogle': '244.wav',           # 모글리 "쿠포"
            
            # 경고/알림
            'alert': '059.wav',            # 경고음
            'computer_beep': '058.wav',    # 컴퓨터 신호음
            'switch_on': '050.wav',        # 스위치 켜기
            'monitor': '173.wav',          # 모니터 작동
            'announcement': '447.wav',     # 안내방송
            
            # 추가 호환성
            'menu_move': '000.wav',        # 메뉴 이동 (별칭)
            'confirm': '001.wav',          # 확인 (별칭)
            'cancel': '003.wav',           # 취소 (별칭)
            'error': '002.wav',            # 에러 (별칭)
        }
    
    def load_bgm(self, bgm_name: str) -> bool:
        """BGM 파일 로드"""
        if bgm_name in self.bgm_tracks:
            return True
        
        if bgm_name not in self.bgm_mapping:
            if self.debug_mode:
                print(f"⚠️ BGM 매핑을 찾을 수 없음: {bgm_name}")
            return False
        
        filename = self.bgm_mapping[bgm_name]
        file_path = self.bgm_path / filename
        
        if file_path.exists():
            try:
                # pygame.mixer.music은 로드만 하고 실제 Sound 객체는 저장하지 않음
                self.bgm_tracks[bgm_name] = str(file_path)
                if self.debug_mode:
                    print(f"✅ BGM 로드: {bgm_name} -> {filename}")
                return True
            except Exception as e:
                if self.debug_mode:
                    print(f"⚠️ BGM 로드 실패: {bgm_name} - {e}")
                return False
        else:
            if self.debug_mode:
                print(f"⚠️ BGM 파일 없음: {file_path}")
            return False
    
    def load_sfx(self, sfx_name: str) -> bool:
        """SFX 파일 로드"""
        if sfx_name in self.sfx_sounds:
            return True
        
        if sfx_name not in self.sfx_mapping:
            if self.debug_mode:
                print(f"⚠️ SFX 매핑을 찾을 수 없음: {sfx_name}")
            return False
        
        filename = self.sfx_mapping[sfx_name]
        file_path = self.sfx_path / filename
        
        if file_path.exists():
            try:
                sound = pygame.mixer.Sound(str(file_path))
                sound.set_volume(self.sfx_volume * self.master_volume)
                self.sfx_sounds[sfx_name] = sound
                if self.debug_mode:
                    print(f"✅ SFX 로드: {sfx_name} -> {filename}")
                return True
            except Exception as e:
                if self.debug_mode:
                    print(f"⚠️ SFX 로드 실패: {sfx_name} - {e}")
                return False
        else:
            if self.debug_mode:
                print(f"⚠️ SFX 파일 없음: {file_path}")
            return False
    
    def play_bgm(self, bgm_name: str, loop: bool = True, fade_in: float = 1.0, force_restart: bool = False):
        """BGM 재생 - 끊김 방지 개선"""
        if not self.initialized:
            if self.debug_mode:
                print(f"🔇 오디오 시스템 비활성화됨 - BGM: {bgm_name}")
            return False
        
        # 같은 BGM이 이미 재생 중이고 실제로 재생되고 있으면 그냥 둠
        if (not force_restart and 
            self.current_bgm == bgm_name and 
            pygame.mixer.music.get_busy()):
            if self.debug_mode:
                print(f"🎵 이미 재생 중 (끊김 방지): {bgm_name}")
            return True
        
        # 같은 BGM이지만 재생이 중단된 경우 빠르게 재시작
        if (self.current_bgm == bgm_name and 
            not pygame.mixer.music.get_busy()):
            if self.debug_mode:
                print(f"🔄 BGM 재시작 (연속성 보장): {bgm_name}")
            fade_in = 0.3  # 더 빠른 재시작
        
        # BGM 로드
        if not self.load_bgm(bgm_name):
            return False
        
        try:
            # 현재 BGM 중지 (같은 BGM 재시작이면 더 빠르게)
            if pygame.mixer.music.get_busy():
                fadeout_time = int(fade_in * 300) if self.current_bgm == bgm_name else int(fade_in * 500)
                pygame.mixer.music.fadeout(fadeout_time)
                time.sleep(fade_in * 0.3)  # 더 짧은 대기
            
            # 새 BGM 로드 및 재생
            pygame.mixer.music.load(self.bgm_tracks[bgm_name])
            pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
            
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops, fade_ms=int(fade_in * 1000))
            
            self.current_bgm = bgm_name
            if self.debug_mode:
                print(f"🎵 BGM 재생: {bgm_name}")
            return True
            
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ BGM 재생 실패: {bgm_name} - {e}")
            return False
    
    def play_sfx(self, sfx_name: str, volume: float = 1.0, fallback: str = None):
        """SFX 재생"""
        if not self.initialized:
            if self.debug_mode:
                print(f"🔇 오디오 시스템 비활성화됨 - SFX: {sfx_name}")
            return False
        
        # 요청된 사운드가 없으면 fallback 사용
        if sfx_name not in self.sfx_sounds and fallback and fallback in self.sfx_mapping:
            sfx_name = fallback
        
        # SFX 로드
        if not self.load_sfx(sfx_name):
            return False
        
        try:
            sound = self.sfx_sounds[sfx_name]
            sound.set_volume(volume * self.sfx_volume * self.master_volume)
            sound.play()
            if self.debug_mode:
                print(f"🔊 SFX 재생: {sfx_name}")
            return True
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ SFX 재생 실패: {sfx_name} - {e}")
            return False
    
    def get_bgm_for_floor(self, floor: int) -> str:
        """층수에 맞는 FFVII BGM 트랙명 반환"""
        # 최종 보스층 (20층 이상)
        if floor >= 20:
            if floor % 5 == 0:  # 20, 25, 30층... 진짜 보스층
                return "final_boss"  # J-E-N-O-V-A
            else:
                return "epic_battle"  # One-Winged Angel
        
        # 보스층 체크 (5의 배수)
        if floor % 5 == 0:
            if floor >= 15:
                return "boss_battle"  # Still More Fighting
            else:
                return "battle"   # Fighting
        
        # 일반층 - FFVII 스토리 진행에 맞춰 배치
        if floor <= 4:
            return "dungeon"         # Mako Reactor (1-4층)
        elif floor <= 9:
            return "dungeon_deep"    # Lurking in the Darkness (5-9층)
        elif floor <= 14:
            return "cave"            # Cosmo Canyon (10-14층)
        elif floor <= 19:
            return "mysterious"      # Chasing the Black-Caped Man (15-19층)
        else:
            return "dungeon"         # 기본 던전 테마
    
    def set_floor_bgm(self, floor: int):
        """층수에 맞는 BGM 재생"""
        bgm_name = self.get_bgm_for_floor(floor)
        return self.play_bgm(bgm_name)
    
    def stop_bgm(self, fade_out: float = 1.0):
        """BGM 정지"""
        if not self.initialized:
            return
        
        try:
            if pygame.mixer.music.get_busy():
                if fade_out > 0:
                    pygame.mixer.music.fadeout(int(fade_out * 1000))
                else:
                    pygame.mixer.music.stop()
            self.current_bgm = None
            if self.debug_mode:
                print("🔇 BGM 정지")
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ BGM 정지 실패: {e}")
    
    def pause_bgm(self):
        """BGM 일시정지"""
        if not self.initialized:
            return
        
        try:
            pygame.mixer.music.pause()
            if self.debug_mode:
                print("⏸️ BGM 일시정지")
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ BGM 일시정지 실패: {e}")
    
    def resume_bgm(self):
        """BGM 재개"""
        if not self.initialized:
            return
        
        try:
            pygame.mixer.music.unpause()
            if self.debug_mode:
                print("▶️ BGM 재개")
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ BGM 재개 실패: {e}")
    
    def set_master_volume(self, volume: float):
        """마스터 볼륨 설정 (0.0 ~ 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        
        # 현재 재생중인 BGM 볼륨 업데이트
        if self.current_bgm and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
        
        # 로드된 SFX 볼륨 업데이트
        for sound in self.sfx_sounds.values():
            sound.set_volume(self.sfx_volume * self.master_volume)
        
        if self.debug_mode:
            print(f"🔊 마스터 볼륨: {int(self.master_volume * 100)}%")
    
    def set_bgm_volume(self, volume: float):
        """BGM 볼륨 설정 (0.0 ~ 1.0)"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        if self.current_bgm and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
        if self.debug_mode:
            print(f"🎵 BGM 볼륨: {int(self.bgm_volume * 100)}%")
    
    def set_sfx_volume(self, volume: float):
        """SFX 볼륨 설정 (0.0 ~ 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        # 로드된 모든 SFX 볼륨 업데이트
        for sound in self.sfx_sounds.values():
            sound.set_volume(self.sfx_volume * self.master_volume)
        if self.debug_mode:
            print(f"🔊 SFX 볼륨: {int(self.sfx_volume * 100)}%")
    
    def cleanup(self):
        """오디오 시스템 정리"""
        try:
            if self.initialized:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                if self.debug_mode:
                    print("🎵 오디오 시스템 종료")
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ 오디오 시스템 종료 실패: {e}")
    
    # 기존 AudioManager 호환성을 위한 메서드들
    def load_bgm_tracks(self):
        """호환성을 위한 메서드 - 실제로는 아무것도 하지 않음"""
        if self.debug_mode:
            print("🎵 BGM 트랙 정보 로드됨 (호환성 모드)")
    
    def play_bgm_for_floor(self, floor: int):
        """호환성을 위한 메서드"""
        return self.set_floor_bgm(floor)
    
    def play_sound_effect(self, effect_name: str):
        """호환성을 위한 메서드"""
        return self.play_sfx(effect_name)
    
    def play_special_bgm(self, situation: str):
        """특수 상황용 BGM 재생"""
        situation_mapping = {
            "shop": "peaceful",
            "rest": "safe_area", 
            "mystery": "mysterious",
            "ending": "victory"
        }
        
        bgm_name = situation_mapping.get(situation, "peaceful")
        return self.play_bgm(bgm_name)
    
    def is_bgm_playing(self) -> bool:
        """BGM 재생 상태 확인"""
        if not self.initialized:
            return False
        try:
            return pygame.mixer.music.get_busy()
        except:
            return False
    
    def ensure_bgm_continuity(self, bgm_name: str):
        """BGM 연속성 보장 - 창 전환 시 호출"""
        if (self.current_bgm == bgm_name and 
            not self.is_bgm_playing()):
            # 같은 BGM이지만 재생이 중단된 경우 빠르게 재시작
            if self.debug_mode:
                print(f"🔄 BGM 연속성 복구: {bgm_name}")
            self.play_bgm(bgm_name, fade_in=0.2)
    
    def soft_transition_bgm(self, bgm_name: str, **kwargs):
        """부드러운 BGM 전환 - 끊김 최소화"""
        if self.current_bgm != bgm_name:
            kwargs.setdefault('fade_in', 0.3)
            self.play_bgm(bgm_name, **kwargs)
        else:
            self.ensure_bgm_continuity(bgm_name)

# 전역 통합 오디오 시스템 인스턴스
_unified_audio_system = None

def get_unified_audio_system(debug_mode: bool = False):
    """통합 오디오 시스템 인스턴스 반환"""
    global _unified_audio_system
    if _unified_audio_system is None:
        _unified_audio_system = UnifiedAudioSystem(debug_mode=debug_mode)
    return _unified_audio_system

# 기존 호환성을 위한 별칭들
def get_audio_system():
    """기존 호환성을 위한 함수"""
    return get_unified_audio_system()

def get_audio_manager():
    """기존 호환성을 위한 함수"""
    return get_unified_audio_system()

def get_ffvii_sound_system():
    """FFVII 사운드 시스템 호환성을 위한 함수"""
    return get_unified_audio_system()

# 전역 인스턴스 (기존 코드 호환성)
audio_manager = get_unified_audio_system()

# 편의 함수들
def play_bgm(name: str, **kwargs):
    """BGM 재생 편의 함수"""
    return get_unified_audio_system().play_bgm(name, **kwargs)

def play_sfx(name: str, **kwargs):
    """SFX 재생 편의 함수"""
    return get_unified_audio_system().play_sfx(name, **kwargs)

def stop_bgm(**kwargs):
    """BGM 중지 편의 함수"""
    return get_unified_audio_system().stop_bgm(**kwargs)

def set_floor_bgm(floor: int):
    """층별 BGM 설정 편의 함수"""
    return get_unified_audio_system().set_floor_bgm(floor)

# 클래스 별칭 (기존 코드 호환성)
AudioManager = UnifiedAudioSystem
AudioSystem = UnifiedAudioSystem
FFVIISoundSystem = UnifiedAudioSystem

if __name__ == "__main__":
    # 테스트 코드
    print("🎵 통합 오디오 시스템 테스트")
    audio = UnifiedAudioSystem(debug_mode=True)
    
    # BGM 테스트
    print("\n📀 BGM 테스트:")
    audio.play_bgm("title")
    time.sleep(2)
    audio.play_bgm("dungeon")
    time.sleep(2)
    
    # SFX 테스트
    print("\n🔊 SFX 테스트:")
    audio.play_sfx("menu_select")
    time.sleep(0.5)
    audio.play_sfx("sword_hit")
    time.sleep(0.5)
    
    # 층별 BGM 테스트
    print("\n🏢 층별 BGM 테스트:")
    for floor in [1, 5, 10, 15, 20]:
        print(f"  {floor}층: {audio.get_bgm_for_floor(floor)}")
    
    audio.cleanup()
    print("✅ 테스트 완료!")
