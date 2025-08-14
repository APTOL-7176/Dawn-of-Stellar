import pygame
import os
import random
import time
from typing import Optional, Dict, List
from pathlib import Path
from enum import Enum

class BGMType(Enum):
    """BGM 타입 정의 - FFVII 완전 매핑"""
    MENU = "menu"
    MAIN_MENU_OPENING = "main_menu_opening"
    DIFFICULTY_SELECT = "difficulty_select"
    FLOOR_1_3 = "floor_1_3"
    FLOOR_4_6 = "floor_4_6"
    FLOOR_7_9 = "floor_7_9"
    FLOOR_10_12 = "floor_10_12"
    FLOOR_13_15 = "floor_13_15"
    FLOOR_16_18 = "floor_16_18"
    FLOOR_19_21 = "floor_19_21"
    FLOOR_22_24 = "floor_22_24"
    FLOOR_25_27 = "floor_25_27"
    FLOOR_28_30 = "floor_28_30"
    FLOOR_31_33 = "floor_31_33"
    FLOOR_34_36 = "floor_34_36"
    FLOOR_37_39 = "floor_37_39"
    FLOOR_40_42 = "floor_40_42"
    FLOOR_43_45 = "floor_43_45"
    FLOOR_46_48 = "floor_46_48"
    FLOOR_49_51 = "floor_49_51"
    FLOOR_52_PLUS = "floor_52_plus"
    BATTLE = "battle"
    BOSS = "boss"
    SHOP = "shop"
    AERITH_THEME = "aerith_theme"
    VICTORY = "victory"
    GAME_OVER = "game_over"
    SPECIAL_EVENT = "special_event"

class SFXType(Enum):
    """효과음 타입 정의 - FFVII 완전 매핑"""
    # UI 효과음
    MENU_SELECT = "menu_select"
    MENU_CONFIRM = "menu_confirm"
    MENU_CANCEL = "menu_cancel"
    MENU_ERROR = "menu_error"
    ITEM_GET = "item_get"
    ITEM_USE = "item_use"
    ITEM_PICKUP = "item_pickup"
    LEVEL_UP = "level_up"
    SKILL_LEARN = "skill_learn"
    SAVE_GAME = "save_game"
    SAVE_READY = "save_ready"
    EQUIP = "equip"
    UNEQUIP = "unequip"
    
    # 소모품 효과음
    POTION = "potion"
    HI_POTION = "hi_potion"
    X_POTION = "x_potion"
    ELIXIR = "elixir"
    PHOENIX_DOWN = "phoenix_down"
    
    # 전투 효과음
    SWORD_HIT = "sword_hit"
    CRITICAL_HIT = "critical_hit"
    MAGIC_CAST = "magic_cast"
    MAGIC_HIT = "magic_hit"
    ARROW_SHOT = "arrow_shot"
    GUN_SHOT = "gun_shot"
    EXPLOSION = "explosion"
    MISS = "miss"
    BLOCK = "block"
    DODGE = "dodge"
    
    # 상태 효과음
    HEAL = "heal"
    POISON = "poison"
    BURN = "burn"
    FREEZE = "freeze"
    SHOCK = "shock"
    BUFF_ON = "buff_on"
    DEBUFF_ON = "debuff_on"
    BUFF_OFF = "buff_off"
    DEBUFF_OFF = "debuff_off"
    
    # 환경 효과음
    FOOTSTEP = "footstep"
    DOOR_OPEN = "door_open"
    DOOR_CLOSE = "door_close"
    TREASURE_OPEN = "treasure_open"
    TRAP_ACTIVATE = "trap_activate"
    STAIRS_UP = "stairs_up"
    STAIRS_DOWN = "stairs_down"
    BATTLE_SWIRL = "battle_swirl"
    
    # 특수 효과음
    SUMMON = "summon"
    TELEPORT = "teleport"
    TRANSFORMATION = "transformation"
    ULTIMATE = "ultimate"
    DEATH = "death"
    REVIVE = "revive"

class UnifiedAudioSystem:
    """통합 오디오 시스템 - FFVII 완전 매핑 + 랜덤 재생"""
    
    def __init__(self, debug_mode: bool = False):
        self.initialized = False
        self.debug_mode = debug_mode
        self.current_bgm = None
        self.bgm_volume = 0.6
        self.sfx_volume = 0.8
        self.master_volume = 0.7
        
        # 사운드 저장소
        self.bgm_tracks = {}
        self.sfx_sounds = {}
        
        # 경로 설정
        self.base_path = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.bgm_path = self.base_path / "audio" / "bgm"
        self.sfx_path = self.base_path / "audio" / "sfx"
        
        # 매핑 초기화
        self._initialize_bgm_mapping()
        self._initialize_sfx_mapping()
        
        # 초기화 시도
        self._initialize_pygame()
    
    def _initialize_pygame(self):
        """Pygame 초기화"""
        try:
            if not pygame.get_init():
                pygame.init()
            
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            
            self.initialized = True
            if self.debug_mode:
                print("🎵 UnifiedAudioSystem 초기화 성공")
                
        except Exception as e:
            if self.debug_mode:
                print(f"❌ 오디오 초기화 실패: {e}")
            self.initialized = False

    def _initialize_bgm_mapping(self):
        """FFVII BGM 매핑 초기화"""
        self.bgm_files = {
            BGMType.MENU: [
                "01-The Prelude.mp3",           # FF7 프렐루드 (보조)
                "25-Main Theme of Final Fantasy VII.mp3",     # FF7 메인 테마 (우선)
            ],
            BGMType.MAIN_MENU_OPENING: [
                "02-Opening ~ Bombing Mission.mp3"     # 오프닝 전용 BGM
            ],
            BGMType.DIFFICULTY_SELECT: [
                "15-Underneath the Rotting Pizza.mp3",  # 썩은 피자 아래서 (선택의 긴장감)
                "19-Don of the Slums.mp3",              # 돈 코를레오네 (중후한 선택)
                "23-Tifa's Theme.mp3"                   # 티파의 테마 (부드러운 선택)
            ],
            BGMType.FLOOR_1_3: [
                "03-Bombing Mission.mp3",   # 필드용 폭파 임무 (03번 사용)
                "15-Underneath the Rotting Pizza.mp3",  # 썩은 피자 아래서
                "04-Mako Reactor.mp3"       # 마코로 1호기 (1층에 적합)
            ],
            BGMType.FLOOR_4_6: [
                "26-Ahead on Our Way.mp3",      # 그 길에서
                "27-Good Night, Until Tomorrow!.mp3",   # 그 앞길에서
                "19-Don of the Slums.mp3"       # 돈 코를레오네
            ],
            BGMType.FLOOR_7_9: [
                "40-Costa del Sol.mp3",     # 코스타 델 솔
                "44-Cait Sith's Theme.mp3", # 케이트 시스의 테마
                "13-Flowers Blooming in the Church.mp3"    # 꽃이 피는 교회
            ],
            BGMType.FLOOR_10_12: [
                "22-Red XIII's Theme.mp3",  # 레드 XIII의 테마
                "53-Cid's Theme.mp3",       # 시드의 테마
                "62-Interrupted by Fireworks.mp3"  # 불꽃에 가로막혀서
            ],
            BGMType.FLOOR_13_15: [
                "46-Cosmo Canyon.mp3",      # 코스모 캐년
                "65-Aeris' Theme.mp3",      # 에어리스의 테마
                "60-Tango of Tears.mp3"     # 눈물의 탱고
            ],
            BGMType.FLOOR_16_18: [
                "78-Sending a Dream into the Universe.mp3",     # 약속의 땅
                "72-The Highwind Takes to the Skies.mp3",       # 하이윈드
                "75-Off the Edge of Despair.mp3"                # 절망의 끝에서
            ],
            BGMType.FLOOR_19_21: [
                "10-Shinra Corporation.mp3",    # 신라 컴퍼니
                "39-Continue.mp3",               # 컨티뉴
                "68-Reunion.mp3"                 # 재회
            ],
            BGMType.FLOOR_22_24: [
                "05-Anxious Heart.mp3",         # 불안한 마음
                "24-Holding My Thoughts in My Heart.mp3",  # 마음에 품은 생각
                "28-On That Day, 5 Years Ago.mp3"     # 그날, 5년 전
            ],
            BGMType.FLOOR_25_27: [
                "33-Chasing the Black-Caped Man.mp3",  # 검은 망토의 사나이를 쫓아서
                "41-Mark of the Traitor.mp3",          # 배반자의 표식
                "37-Trail of Blood.mp3"                # 피의 흔적
            ],
            BGMType.FLOOR_28_30: [
                "52-The Nightmare's Beginning.mp3",    # 악몽의 시작
                "64-You Can Hear the Cry of the Planet.mp3",  # 별의 울음소리가 들려
                "67-The Great Northern Cave.mp3"       # 대공동
            ],
            BGMType.FLOOR_31_33: [
                "07-Barret's Theme.mp3",            # 바렛의 테마
                "14-Turks' Theme.mp3",              # 터크스의 테마
                "06-Tifa's Theme.mp3"               # 티파의 테마
            ],
            BGMType.FLOOR_34_36: [
                "16-Oppressed People.mp3",          # 억압받는 사람들
                "17-Honeybee Manor.mp3",            # 벌집 저택
                "18-Who Are You.mp3"                # 너는 누구냐
            ],
            BGMType.FLOOR_37_39: [
                "20-Infiltrating Shinra Tower.mp3", # 신라 빌딩 침입
                "29-Farm Boy.mp3",                  # 농장 소년
                "34-Fortress of the Condor.mp3"     # 콘돌 요새
            ],
            BGMType.FLOOR_40_42: [
                "35-Rufus' Welcoming Ceremony.mp3", # 루퍼스 환영식
                "42-Mining Town.mp3",               # 광산 마을
                "43-Gold Saucer.mp3"                # 골드 소서
            ],
            BGMType.FLOOR_43_45: [
                "45-Sandy Badlands.mp3",            # 모래 황무지
                "47-Life Stream.mp3",               # 라이프 스트림
                "48-Great Warrior.mp3"              # 위대한 전사
            ],
            BGMType.FLOOR_46_48: [
                "49-Descendant of Shinobi.mp3",     # 시노비의 후예
                "50-Those Chosen By the Planet.mp3", # 별에게 선택받은 자
                "55-Wutai.mp3"                      # 우타이
            ],
            BGMType.FLOOR_49_51: [
                "63-Forested Temple.mp3",           # 숲의 신전
                "66-Buried in the Snow.mp3",        # 눈에 묻힌
                "69-Who Am I.mp3"                   # 나는 누구인가
            ],
            BGMType.FLOOR_52_PLUS: [
                "88-World Crisis.mp3",              # 세계의 위기 (최종층)
                "84-Judgement Day.mp3",             # 심판의 날 (최종층)
                "79-The Countdown Begins.mp3"       # 카운트다운 시작 (최종층)
            ],
            BGMType.BATTLE: [
                "11-Fighting.mp3",                  # 전투! (일반 전투)
                "21-Still More Fighting.mp3",       # 더욱 전투를! (일반 전투)
                "85-Jenova Absolute.mp3",           # 제노바 앱솔루트 (일반 전투)
            ],
            BGMType.BOSS: [
                "38-J-E-N-O-V-A.mp3",              # 제노바 (보스급)
                "86-The Birth of God.mp3",          # 신의 탄생 (보스급)
                "23-Crazy Motorcycle Chase.mp3",    # 크레이지 모터사이클
                "70-Full-Scale Attack.mp3",         # 전면 공격
                "71-Weapon Raid.mp3",               # 웨폰 습격
                "82-Attacking Weapon!.mp3",         # 웨폰을 공격하라!
                "87-One-Winged Angel.mp3"           # 외날개 천사 (최종보스 전용)
            ],
            BGMType.SHOP: [
                "44-Cait Sith's Theme.mp3",          # 상인
                "40-Costa del Sol.mp3",              # 코스타 델 솔
                "19-Don of the Slums.mp3",            # 월 마켓
            ],
            BGMType.AERITH_THEME: [
                "47-Life Stream.mp3",                      # 라이프 스트림 (잔잔함)
                "65-Aeris Theme.mp3"                       # 에어리스 테마
            ],
            BGMType.VICTORY: [
                "12-Fanfare.mp3",                    # 승리의 팡파르 (우선 재생)
                "12-Fanfare.mp3",                    # 팡파레 확률 증가
                "12-Fanfare.mp3",                    # 팡파레 확률 더 증가
                "72-The Highwind Takes to the Skies.mp3"           # 하이윈드 (보조)
            ],
            BGMType.GAME_OVER: [
                "39-Continue.mp3",                   # 게임 오버
                "75-Off the Edge of Despair.mp3"    # 슬픈 테마
            ],
            BGMType.SPECIAL_EVENT: [
                "02-Opening ~ Bombing Mission.mp3",       # 오프닝/스토리용 (02번 오프닝)
                "13-Flowers Blooming in the Church.mp3",  # 꽃이 피는 교회
                "62-Interrupted by Fireworks.mp3",        # 불꽃에 가로막혀서
                "60-Tango of Tears.mp3"                   # 데이트 테마
            ]
        }
    
    def _initialize_sfx_mapping(self):
        """FFVII SFX 매핑 초기화 - 랜덤 재생 지원"""
        self.sfx_files = {
            # UI 효과음 (FFVII 정확한 파일명)
            SFXType.MENU_SELECT: ["000.wav"],      # 커서 이동
            SFXType.MENU_CONFIRM: ["001.wav"],     # 세이브 완료/확인
            SFXType.MENU_CANCEL: ["003.wav"],      # 취소
            SFXType.MENU_ERROR: ["003.wav"],       # 에러도 취소음 사용 (더 적절함)
            SFXType.ITEM_GET: ["357.wav"],         # 아이템 획득
            SFXType.ITEM_USE: ["020.wav"],         # 아이템 사용
            SFXType.ITEM_PICKUP: ["357.wav"],      # 아이템 픽업
            SFXType.LEVEL_UP: ["381.wav"],         # 레벨업/4번째 리미트 습득
            SFXType.SKILL_LEARN: ["381.wav"],      # 스킬 습득/새로운 발견
            SFXType.SAVE_GAME: ["001.wav"],        # 저장 (확인음 사용)
            SFXType.SAVE_READY: ["001.wav"],       # 로드 성공 (확인음 사용)
            SFXType.EQUIP: ["444.wav"],            # 장비 장착
            SFXType.UNEQUIP: ["444.wav"],          # 장비 해제
            
            # 소모품 효과음 (FFVII 정확한 파일명)
            SFXType.POTION: ["005.wav"],           # 포션
            SFXType.HI_POTION: ["006.wav"],        # 하이포션  
            SFXType.X_POTION: ["007.wav"],         # 엑스포션
            SFXType.ELIXIR: ["068.wav"],           # 엘릭서
            SFXType.PHOENIX_DOWN: ["379.wav"],     # 피닉스테일
            
            # 전투 효과음 (FFVII 정확한 파일명 + 랜덤 지원)
            SFXType.SWORD_HIT: ["017.wav", "014.wav"],        # 클라우드 검 타격 (랜덤)
            SFXType.CRITICAL_HIT: ["026.wav"],     # 클라우드 크리티컬
            SFXType.MAGIC_CAST: ["012.wav"],       # 마법 시전 준비
            SFXType.MAGIC_HIT: ["008.wav", "023.wav", "010.wav"],  # 파이어, 아이스, 볼트 (랜덤)
            SFXType.ARROW_SHOT: ["017.wav", "014.wav", "019.wav"],  # 물리 공격 (랜덤)
            SFXType.GUN_SHOT: ["014.wav", "017.wav"],         # 바렛 총 타격 (랜덤)
            SFXType.EXPLOSION: ["019.wav", "008.wav"],        # 그레네이드 폭발 (랜덤)
            SFXType.MISS: ["004.wav", "061.wav"],             # 공격 빗나감 (랜덤)
            SFXType.BLOCK: ["061.wav"],            # 공격 회피
            SFXType.DODGE: ["061.wav"],            # 회피
            
            # 상태 효과음 (FFVII 정확한 파일명)
            SFXType.HEAL: ["005.wav"],             # 케알
            SFXType.POISON: ["062.wav"],           # 바이오
            SFXType.BURN: ["008.wav"],             # 파이어
            SFXType.FREEZE: ["023.wav"],           # 아이스
            SFXType.SHOCK: ["010.wav"],            # 볼트
            SFXType.BUFF_ON: ["082.wav"],          # 헤이스트
            SFXType.DEBUFF_ON: ["064.wav"],        # 슬로우
            SFXType.BUFF_OFF: ["148.wav"],         # 상태이상 회복
            SFXType.DEBUFF_OFF: ["148.wav"],       # 상태이상 회복
            
            # 환경 효과음 (FFVII 정확한 파일명)
            SFXType.FOOTSTEP: ["027.wav"],         # 발소리
            SFXType.DOOR_OPEN: ["121.wav"],        # 문 열기
            SFXType.DOOR_CLOSE: ["052.wav"],       # 문 닫기
            SFXType.TREASURE_OPEN: ["253.wav"],    # 보물상자
            SFXType.TRAP_ACTIVATE: ["059.wav"],    # 경고음
            SFXType.STAIRS_UP: ["054.wav"],        # 점프/이동
            SFXType.STAIRS_DOWN: ["055.wav"],      # 착지
            SFXType.BATTLE_SWIRL: ["042.wav"],     # 전투 시작 소용돌이
            
            # 특수 효과음 (FFVII 정확한 파일명)
            SFXType.SUMMON: ["190.wav"],           # 마테리아 빛남/소환
            SFXType.TELEPORT: ["054.wav"],         # 순간이동/점프
            SFXType.TRANSFORMATION: ["266.wav"],   # 변신/기계 반응
            SFXType.ULTIMATE: ["035.wav"],         # 리미트 브레이크
            SFXType.DEATH: ["021.wav"],            # 적 사망
            SFXType.REVIVE: ["379.wav"]            # 피닉스테일
        }
    
    def play_bgm(self, bgm_type, loop: bool = True, force_restart: bool = False):
        """BGM 재생 - 랜덤 선택 지원"""
        if not self.initialized:
            return
        
        try:
            # BGMType 변환
            if isinstance(bgm_type, str):
                # 문자열을 BGMType으로 변환 시도
                for bt in BGMType:
                    if bt.value == bgm_type or bt.name.lower() == bgm_type.lower():
                        bgm_type = bt
                        break
                else:
                    if self.debug_mode:
                        print(f"⚠️ 알 수 없는 BGM 타입: {bgm_type}")
                    return
            
            if bgm_type not in self.bgm_files:
                if self.debug_mode:
                    print(f"⚠️ BGM 타입이 매핑되지 않음: {bgm_type}")
                return
            
            # 랜덤 파일 선택
            file_list = self.bgm_files[bgm_type]
            selected_file = random.choice(file_list)
            
            # 현재 재생 중인 곡과 같으면 스킵 (force_restart가 False일 때)
            if not force_restart and self.current_bgm == selected_file:
                return
            
            # 파일 경로 확인
            file_path = self.bgm_path / selected_file
            if not file_path.exists():
                if self.debug_mode:
                    print(f"⚠️ BGM 파일이 없음: {file_path}")
                return
            
            # BGM 재생
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
            pygame.mixer.music.play(-1 if loop else 1)
            
            self.current_bgm = selected_file
            
            if self.debug_mode:
                print(f"🎵 BGM 재생: {selected_file} (타입: {bgm_type.name})")
                
        except Exception as e:
            if self.debug_mode:
                print(f"❌ BGM 재생 실패: {e}")
    
    def _play_bgm_internal(self, bgm_type, loop: bool = True, fade_in: int = 1000):
        """내부 BGM 재생 로직 (호환성용)"""
        self.play_bgm(bgm_type, loop=loop)
    
    def play_sfx(self, sfx_type, volume_override: Optional[float] = None):
        """SFX 재생 - 랜덤 선택 지원"""
        if not self.initialized:
            return
        
        try:
            # SFXType 변환
            if isinstance(sfx_type, str):
                # 문자열을 SFXType으로 변환 시도
                for st in SFXType:
                    if st.value == sfx_type or st.name.lower() == sfx_type.lower():
                        sfx_type = st
                        break
                else:
                    if self.debug_mode:
                        print(f"⚠️ 알 수 없는 SFX 타입: {sfx_type}")
                    return
            
            if sfx_type not in self.sfx_files:
                if self.debug_mode:
                    print(f"⚠️ SFX 타입이 매핑되지 않음: {sfx_type}")
                return
            
            # 랜덤 파일 선택
            file_list = self.sfx_files[sfx_type]
            selected_file = random.choice(file_list)
            
            # 파일 경로 확인
            file_path = self.sfx_path / selected_file
            if not file_path.exists():
                if self.debug_mode:
                    print(f"⚠️ SFX 파일이 없음: {file_path}")
                return
            
            # SFX 재생
            sound = pygame.mixer.Sound(str(file_path))
            volume = volume_override if volume_override is not None else (self.sfx_volume * self.master_volume)
            sound.set_volume(volume)
            sound.play()
            
            if self.debug_mode:
                print(f"🔊 SFX 재생: {selected_file} (타입: {sfx_type.name})")
                
        except Exception as e:
            if self.debug_mode:
                print(f"❌ SFX 재생 실패: {e}")
    
    def stop_bgm(self):
        """BGM 중지"""
        if self.initialized:
            pygame.mixer.music.stop()
            self.current_bgm = None
            if self.debug_mode:
                print("🛑 BGM 중지")
    
    def set_bgm_volume(self, volume: float):
        """BGM 볼륨 설정 (0.0 ~ 1.0)"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        if self.initialized and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
    
    def set_sfx_volume(self, volume: float):
        """SFX 볼륨 설정 (0.0 ~ 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_master_volume(self, volume: float):
        """마스터 볼륨 설정 (0.0 ~ 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        if self.initialized and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
    
    def get_bgm_for_floor(self, floor: int) -> BGMType:
        """층수에 따른 BGM 타입 반환"""
        if floor <= 3:
            return BGMType.FLOOR_1_3
        elif floor <= 6:
            return BGMType.FLOOR_4_6
        elif floor <= 9:
            return BGMType.FLOOR_7_9
        elif floor <= 12:
            return BGMType.FLOOR_10_12
        elif floor <= 15:
            return BGMType.FLOOR_13_15
        elif floor <= 18:
            return BGMType.FLOOR_16_18
        elif floor <= 21:
            return BGMType.FLOOR_19_21
        elif floor <= 24:
            return BGMType.FLOOR_22_24
        elif floor <= 27:
            return BGMType.FLOOR_25_27
        elif floor <= 30:
            return BGMType.FLOOR_28_30
        elif floor <= 33:
            return BGMType.FLOOR_31_33
        elif floor <= 36:
            return BGMType.FLOOR_34_36
        elif floor <= 39:
            return BGMType.FLOOR_37_39
        elif floor <= 42:
            return BGMType.FLOOR_40_42
        elif floor <= 45:
            return BGMType.FLOOR_43_45
        elif floor <= 48:
            return BGMType.FLOOR_46_48
        elif floor <= 51:
            return BGMType.FLOOR_49_51
        else:
            return BGMType.FLOOR_52_PLUS
    
    def set_floor_bgm(self, floor: int):
        """층수에 따른 BGM 자동 설정"""
        bgm_type = self.get_bgm_for_floor(floor)
        self.play_bgm(bgm_type)
        
        if self.debug_mode:
            print(f"🏢 {floor}층 BGM 설정: {bgm_type.name}")
    
    def cleanup(self):
        """오디오 시스템 정리"""
        if self.initialized:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.initialized = False
            if self.debug_mode:
                print("🧹 오디오 시스템 정리 완료")

# 전역 인스턴스
_unified_audio_system = None

def get_unified_audio_system() -> UnifiedAudioSystem:
    """통합 오디오 시스템 싱글톤 인스턴스 반환"""
    global _unified_audio_system
    if _unified_audio_system is None:
        _unified_audio_system = UnifiedAudioSystem(debug_mode=False)
    return _unified_audio_system

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
    audio.play_bgm(BGMType.MENU)
    time.sleep(2)
    audio.play_bgm(BGMType.FLOOR_1_3)
    time.sleep(2)
    
    # SFX 테스트
    print("\n🔊 SFX 테스트:")
    audio.play_sfx(SFXType.MENU_SELECT)
    time.sleep(0.5)
    audio.play_sfx(SFXType.SWORD_HIT)  # 랜덤으로 017.wav 또는 014.wav 재생
    time.sleep(0.5)
    audio.play_sfx(SFXType.MAGIC_HIT)  # 랜덤으로 008.wav, 023.wav, 010.wav 중 하나 재생
    time.sleep(0.5)
    
    # 층별 BGM 테스트
    print("\n🏢 층별 BGM 테스트:")
    for floor in [1, 5, 10, 15, 20]:
        bgm_type = audio.get_bgm_for_floor(floor)
        print(f"  {floor}층: {bgm_type.name}")
    
    audio.cleanup()
    print("✅ 테스트 완료!")
