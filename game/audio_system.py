#!/usr/bin/env python3
"""
BGM 및 SFX 시스템 - FFVII 스타일 (시작 시 완전 차단됨)
층별 다른 BGM, 다양한 효과음
"""

# pygame import - main.py에서 조건부 차단된 pygame 사용
import pygame  # main.py에서 ConditionalPygameModule로 관리됨

import random
import os
import sys
from typing import Dict, List, Optional
from enum import Enum

class BGMType(Enum):
    """BGM 타입"""
    MENU = "메인메뉴"
    MAIN_MENU_OPENING = "메인메뉴_오프닝"  # 02-Opening ~ Bombing Mission.mp3 전용
    DIFFICULTY_SELECT = "난이도선택"  # 난이도 선택 화면용
    AERITH_THEME = "에어리스테마"  # AI 멀티플레이어용 잔잔한 테마
    FLOOR_1_3 = "1-3층"
    FLOOR_4_6 = "4-6층"
    FLOOR_7_9 = "7-9층"
    FLOOR_10_12 = "10-12층"
    FLOOR_13_15 = "13-15층"
    FLOOR_16_18 = "16-18층"
    FLOOR_19_21 = "19-21층"
    FLOOR_22_24 = "22-24층"
    FLOOR_25_27 = "25-27층"
    FLOOR_28_30 = "28-30층"
    FLOOR_31_33 = "31-33층"
    FLOOR_34_36 = "34-36층"
    FLOOR_37_39 = "37-39층"
    FLOOR_40_42 = "40-42층"
    FLOOR_43_45 = "43-45층"
    FLOOR_46_48 = "46-48층"
    FLOOR_49_51 = "49-51층"
    FLOOR_52_PLUS = "52층이상"
    BATTLE = "전투"
    BOSS = "보스전"
    SHOP = "상점"
    VICTORY = "승리"
    GAME_OVER = "게임오버"
    SPECIAL_EVENT = "특별이벤트"

class SFXType(Enum):
    """효과음 타입"""
    # 전투 효과음
    SWORD_HIT = "검격"
    MAGIC_CAST = "마법시전"
    MAGIC_HIT = "마법명중"
    ARROW_SHOT = "화살발사"
    GUN_SHOT = "총격"
    EXPLOSION = "폭발"
    CRITICAL_HIT = "크리티컬"
    MISS = "빗나감"
    BLOCK = "방어"
    DODGE = "회피"
    
    # 상태 효과음
    HEAL = "치유"
    POISON = "독"
    BURN = "화상"
    FREEZE = "빙결"
    SHOCK = "감전"
    BUFF_ON = "버프적용"
    DEBUFF_ON = "디버프적용"
    BUFF_OFF = "버프해제"
    DEBUFF_OFF = "디버프해제"
    
    # UI 효과음
    MENU_SELECT = "메뉴선택"
    MENU_CONFIRM = "메뉴확인"
    MENU_CANCEL = "메뉴취소"
    MENU_ERROR = "메뉴에러"
    ITEM_GET = "아이템획득"
    ITEM_USE = "아이템사용"
    ITEM_PICKUP = "아이템픽업"
    LEVEL_UP = "레벨업"
    SKILL_LEARN = "스킬습득"
    SAVE_GAME = "게임저장"
    SAVE_READY = "저장준비"
    EQUIP = "장비장착"
    UNEQUIP = "장비해제"
    
    # 소모품 효과음
    POTION = "포션"
    HI_POTION = "하이포션"
    X_POTION = "엑스포션"
    ELIXIR = "엘릭서"
    PHOENIX_DOWN = "피닉스테일"
    
    # 환경 효과음
    FOOTSTEP = "발소리"
    DOOR_OPEN = "문열림"
    DOOR_CLOSE = "문닫힘"
    TREASURE_OPEN = "보물상자"
    TRAP_ACTIVATE = "함정발동"
    STAIRS_UP = "계단오르기"
    STAIRS_DOWN = "계단내려가기"
    
    # 글리치 모드 전용 공포 효과음
    GLITCH_STATIC = "글리치_정적음"
    GLITCH_DISTORTION = "글리치_왜곡음"
    GLITCH_CORRUPTION = "글리치_손상음"
    GLITCH_ERROR = "글리치_에러음"
    GLITCH_SCREAM = "글리치_비명"
    GLITCH_WHISPER = "글리치_속삭임"
    GLITCH_HEARTBEAT = "글리치_심장박동"
    GLITCH_BREATH = "글리치_호흡음"
    GLITCH_CRACK = "글리치_균열음"
    GLITCH_VOID = "글리치_공허음"
    SEPHIROTH_LAUGH = "세피로스_웃음"
    SEPHIROTH_WHISPER = "세피로스_속삭임"
    HORROR_AMBIENT = "공포_분위기"
    SYSTEM_CORRUPTION = "시스템_손상"
    REALITY_BREAK = "현실_붕괴"
    BATTLE_SWIRL = "전투시작소용돌이"
    
    # 상호작용 효과음 (FFVII 기반 매핑)
    INTERACT_SUCCESS = "아이템획득"        # 성공적인 상호작용 -> FFVII 아이템 획득음
    INTERACT_FAIL = "메뉴에러"              # 실패한 상호작용 -> FFVII 에러음
    ALTAR_ACTIVATE = "치유"                 # 제단 활성화 -> FFVII 회복마법음
    LEVER_PULL = "장비장착"                 # 레버 작동 -> FFVII 장비 장착음 (기계음)
    BOOKSHELF_READ = "스킬습득"             # 지식 습득 -> FFVII 스킬 학습음
    FORGE_USE = "장비장착"                  # 대장간 사용 -> FFVII 장비 관련음
    FOUNTAIN_DRINK = "포션"                 # 분수 치유 -> FFVII 포션 사용음
    CRYSTAL_TOUCH = "마법시전"              # 수정 터치 -> FFVII 마법 시전음
    SECRET_FOUND = "아이템픽업"             # 비밀 발견 -> FFVII 특별 아이템 발견음
    LOCK_PICK = "문열림"                    # 잠금해제 -> FFVII 문 열림음
    TRAP_DISARM = "버프적용"                # 함정해제 -> FFVII 버프 적용음 (성공음)
    CURSED_ACTIVATE = "디버프적용"          # 저주 발동 -> FFVII 디버프 적용음
    MAGIC_SEAL = "마법시전"                 # 마법 봉인 -> FFVII 마법 시전음
    
    # 특수 효과음
    SUMMON = "소환"
    TELEPORT = "순간이동"
    TRANSFORMATION = "변신"
    ULTIMATE = "궁극기"
    DEATH = "죽음"
    REVIVE = "부활"

class AudioManager:
    """오디오 관리자"""
    
    def __init__(self, debug_mode: bool = False):
        # 디버그 모드 설정
        self.debug_mode = debug_mode
        self.mixer_available = False
        
        # pygame mixer 초기화 (조용하게)
        try:
            # 먼저 기존 mixer 정리
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.quit()
            except:
                pass
            
            # pygame 초기화 (mixer만)
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
                pygame.mixer.init()
                
                # 초기화 확인
                if pygame.mixer.get_init():
                    self.mixer_available = True
                    # 초기화 성공 메시지 조용히 처리
                    
                    # 초기화 직후 즉시 정지
                    pygame.mixer.stop()
                    pygame.mixer.music.stop()
                    pygame.mixer.music.set_volume(0.0)
                else:
                    raise Exception("mixer 초기화 실패")
                    
            except Exception as init_error:
                # 초기화 실패 메시지 조용히 처리
                self.mixer_available = False
                
        except Exception as e:
            # 전체 초기화 실패 메시지 조용히 처리
            self.mixer_available = False
        
        # mixer가 사용 불가능하면 여기서 종료
        if not self.mixer_available:
            # 오디오 비활성화 메시지 조용히 처리
            self._init_fallback_mode()
            return
        
        # 정상 모드 초기화
        self._init_normal_mode()
    
    def _init_normal_mode(self):
        """정상 오디오 모드 초기화"""
        # 기본값들 설정
        self.bgm_volume = 0.7
        self.sfx_volume = 0.8
        self.current_bgm = None
        self.current_bgm_type = None
        self.current_track_index = 0  # 필드 BGM 순환용 인덱스
        
        # BGM 및 SFX 딕셔너리
        self.bgm_tracks = {}
        self.sfx_sounds = {}
        
        # 로드된 파일 추적
        self.loaded_bgm = set()
        self.loaded_sfx = set()
        
        # SFX 쿨다운 시스템 (중복 재생 방지)
        self.last_sfx_time = {}
        self.sfx_cooldown = 0.1  # 100ms 쿨다운
        
        # 🔧 안전한 경로 처리 시스템
        self.sounds_base_path = self._get_sounds_path()
        self.bgm_base_path = os.path.join(self.sounds_base_path, "bgm")
        self.sfx_base_path = os.path.join(self.sounds_base_path, "sfx")
        
        # 디렉토리 생성
        self._ensure_audio_directories()
        
        # BGM/SFX 매핑 초기화
        try:
            self._initialize_bgm_mapping()
            self._initialize_sfx_mapping()
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ 매핑 초기화 실패: {e}")
        
        # 🔇 초기화 중 BGM 자동 재생 완전 차단
        if self.mixer_available:
            try:
                # 모든 mixer 채널 정지
                pygame.mixer.stop()
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                # 볼륨도 0으로 설정
                pygame.mixer.music.set_volume(0.0)
                self.current_bgm = None
                self.current_bgm_type = None
                # 약간의 지연 후 볼륨 복구
                import time
                time.sleep(0.1)
                pygame.mixer.music.set_volume(self.bgm_volume)
                if self.debug_mode:
                    print("🔇 초기화 완료 - BGM 자동 재생 차단됨")
            except Exception as e:
                if self.debug_mode:
                    print(f"⚠️ 초기화 정지 실패: {e}")
    
    def _init_fallback_mode(self):
        """오디오 시스템이 사용 불가능할 때의 fallback 초기화"""
        # 기본값들 설정
        self.bgm_volume = 0.7
        self.sfx_volume = 0.8
        self.current_bgm = None
        self.current_bgm_type = None
        self.current_track_index = 0  # 필드 BGM 순환용 인덱스
        
        # BGM 및 SFX 딕셔너리
        self.bgm_tracks = {}
        self.sfx_sounds = {}
        
        # 로드된 파일 추적
        self.loaded_bgm = set()
        self.loaded_sfx = set()
        
        # SFX 쿨다운 시스템 (중복 재생 방지)
        self.last_sfx_time = {}
        self.sfx_cooldown = 0.1  # 100ms 쿨다운
        
        # 🔧 안전한 경로 처리 시스템
        self.sounds_base_path = self._get_sounds_path()
        self.bgm_base_path = os.path.join(self.sounds_base_path, "bgm")
        self.sfx_base_path = os.path.join(self.sounds_base_path, "sfx")
        
        # 디렉토리 생성
        self._ensure_audio_directories()
        
        # 빈 매핑 초기화 (fallback 모드에서는 실제 파일 로드하지 않음)
        try:
            self._initialize_bgm_mapping()
            self._initialize_sfx_mapping()
        except:
            # 매핑 초기화 실패해도 계속 진행
            pass
    
    def _get_sounds_path(self) -> str:
        """실행 파일 위치에 관계없이 game/audio 폴더 경로를 안전하게 찾기"""
        # 실행 중인 스크립트의 디렉토리 찾기
        if getattr(sys, 'frozen', False):
            # PyInstaller로 패키징된 실행 파일
            base_dir = sys._MEIPASS
        else:
            # 일반 Python 실행
            # 현재 파일(audio_system.py)의 상위 디렉토리로 이동
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)  # game/ 폴더의 상위로
        
        audio_path = os.path.join(base_dir, "game", "audio")
        
        # game/audio 폴더가 없으면 현재 디렉토리에서 찾기
        if not os.path.exists(audio_path):
            # 현재 작업 디렉토리에서 찾기
            current_audio = os.path.join(os.getcwd(), "game", "audio")
            if os.path.exists(current_audio):
                audio_path = current_audio
            else:
                # 스크립트가 있는 디렉토리의 상위에서 찾기
                script_dir = os.path.dirname(os.path.abspath(__file__))
                parent_audio = os.path.join(os.path.dirname(script_dir), "game", "audio")
                if os.path.exists(parent_audio):
                    audio_path = parent_audio
                else:
                    # 마지막 시도: 여러 경로 시도
                    possible_paths = [
                        os.path.join(os.getcwd(), "game", "audio"),
                        os.path.join(os.path.dirname(sys.executable), "game", "audio"),
                        os.path.join(os.path.dirname(sys.argv[0]), "game", "audio"),
                        os.path.join("game", "audio")  # 상대 경로
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            audio_path = path
                            break
        
        # print(f"🎵 사운드 폴더 경로: {sounds_path}")  # 조용히
        return audio_path
    
    def _ensure_audio_directories(self):
        """오디오 디렉토리 생성 및 확인"""
        try:
            os.makedirs(self.bgm_base_path, exist_ok=True)
            os.makedirs(self.sfx_base_path, exist_ok=True)
            
            # 디렉토리 존재 확인
            if not os.path.exists(self.bgm_base_path):
                print(f"⚠️ BGM 폴더를 찾을 수 없습니다: {self.bgm_base_path}")
            if not os.path.exists(self.sfx_base_path):
                print(f"⚠️ SFX 폴더를 찾을 수 없습니다: {self.sfx_base_path}")
                
        except Exception as e:
            print(f"⚠️ 오디오 디렉토리 생성 실패: {e}")
    
    def _safe_file_path(self, filename: str, sound_type: str = "bgm") -> Optional[str]:
        """안전한 파일 경로 생성 및 존재 확인"""
        if sound_type == "bgm":
            file_path = os.path.join(self.bgm_base_path, filename)
        else:
            file_path = os.path.join(self.sfx_base_path, filename)
        
        # 파일 존재 확인
        if os.path.exists(file_path):
            return file_path
        else:
            # 파일이 없으면 None 반환 (오류 대신 조용히 처리)
            return None
    
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
        """FFVII SFX 매핑 초기화 - 정확한 파일명 기반"""
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
            
            # 전투 효과음 (FFVII 정확한 파일명)
            SFXType.SWORD_HIT: ["017.wav"],        # 클라우드 검 타격
            SFXType.CRITICAL_HIT: ["026.wav"],     # 클라우드 크리티컬
            SFXType.MAGIC_CAST: ["012.wav"],       # 마법 시전 준비
            SFXType.MAGIC_HIT: ["008.wav", "023.wav", "010.wav"],  # 파이어, 아이스, 볼트
            SFXType.ARROW_SHOT: ["017.wav"],       # 물리 공격
            SFXType.GUN_SHOT: ["014.wav"],         # 바렛 총 타격
            SFXType.EXPLOSION: ["019.wav"],        # 그레네이드 폭발
            SFXType.MISS: ["004.wav"],             # 공격 빗나감
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
    
    def load_bgm(self, bgm_type: BGMType) -> bool:
        """BGM 로드 - 안전한 경로 처리"""
        if not self.mixer_available:
            return False
            
        if bgm_type in self.loaded_bgm:
            return True
        
        try:
            tracks = []
            for filename in self.bgm_files.get(bgm_type, []):
                # 안전한 파일 경로 생성
                filepath = self._safe_file_path(filename, "bgm")
                if filepath:
                    tracks.append(filepath)
                else:
                    # 파일이 없으면 로그만 출력하고 계속 진행 (조용히)
                    pass  # print(f"🔇 BGM 파일 없음: {filename}")
            
            if tracks:
                self.bgm_tracks[bgm_type] = tracks
                self.loaded_bgm.add(bgm_type)
                # 로드 성공 메시지는 조용히 처리
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    print(f"✅ BGM 로드 성공: {bgm_type.value} ({len(tracks)}개 파일)")
                return True
            else:
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    print(f"⚠️ BGM 타입 {bgm_type.value}에 사용 가능한 파일이 없습니다")
            
        except Exception as e:
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"⚠️ BGM 로드 실패 {bgm_type.value}: {e}")
        
        return False
    
    def load_sfx(self, sfx_type: SFXType) -> bool:
        """SFX 로드 - 안전한 경로 처리"""
        if not self.mixer_available:
            return False
            
        if sfx_type in self.loaded_sfx:
            return True
        
        try:
            sounds = []
            for filename in self.sfx_files.get(sfx_type, []):
                # 안전한 파일 경로 생성
                filepath = self._safe_file_path(filename, "sfx")
                if filepath:
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.sfx_volume)
                    sounds.append(sound)
                else:
                    # 파일이 없으면 로그만 출력하고 계속 진행
                    print(f"🔇 SFX 파일 없음: {filename}")
            
            if sounds:
                self.sfx_sounds[sfx_type] = sounds
                self.loaded_sfx.add(sfx_type)
                # SFX 로드 로그 제거 (너무 많은 출력)
                return True
            else:
                print(f"⚠️ SFX 타입 {sfx_type.value}에 사용 가능한 파일이 없습니다")
                
        except Exception as e:
            print(f"⚠️ SFX 로드 실패 {sfx_type.value}: {e}")
        
        return False
    
    def play_bgm(self, bgm_type_or_name, loop: bool = True, fade_in: int = 1000):
        """BGM 재생"""
        # 문자열이면 BGMType으로 변환
        if isinstance(bgm_type_or_name, str):
            self.play_bgm_by_name(bgm_type_or_name, loop=loop, fade_in=fade_in)
            return
        
        # BGMType으로 처리
        bgm_type = bgm_type_or_name
        self._play_bgm_internal(bgm_type, loop=loop, fade_in=fade_in)
    
    def _is_field_bgm(self, bgm_type: BGMType) -> bool:
        """필드 BGM인지 확인"""
        field_bgm_types = [
            BGMType.FLOOR_1_3, BGMType.FLOOR_4_6, BGMType.FLOOR_7_9,
            BGMType.FLOOR_10_12, BGMType.FLOOR_13_15, BGMType.FLOOR_16_18,
            BGMType.FLOOR_19_21, BGMType.FLOOR_22_24, BGMType.FLOOR_25_27,
            BGMType.FLOOR_28_30, BGMType.FLOOR_31_33, BGMType.FLOOR_34_36,
            BGMType.FLOOR_37_39, BGMType.FLOOR_40_42, BGMType.FLOOR_43_45,
            BGMType.FLOOR_46_48, BGMType.FLOOR_49_51, BGMType.FLOOR_52_PLUS
        ]
        return bgm_type in field_bgm_types
    
    def play_sfx(self, sfx_type_or_name, volume_multiplier: float = 1.0):
        """SFX 재생 - SFXType 또는 문자열 모두 지원 (중복 재생 방지)"""
        import time
        
        # 중복 재생 방지 - 쿨다운 체크
        current_time = time.time()
        sfx_key = str(sfx_type_or_name)
        if sfx_key in self.last_sfx_time:
            time_diff = current_time - self.last_sfx_time[sfx_key]
            if time_diff < self.sfx_cooldown:
                return  # 쿨다운 중이면 재생하지 않음
        
        self.last_sfx_time[sfx_key] = current_time
        
        # 문자열이면 SFXType으로 변환
        if isinstance(sfx_type_or_name, str):
            sfx_mapping = {
                # UI 사운드
                "menu_select": SFXType.MENU_SELECT,
                "menu_confirm": SFXType.MENU_CONFIRM,
                "menu_cancel": SFXType.MENU_CANCEL,
                "menu_error": SFXType.MENU_ERROR,  # 새로운 에러 효과음
                "error": SFXType.MENU_ERROR,
                
                # 아이템 사용음
                "item_pickup": SFXType.ITEM_PICKUP,
                "item_get": SFXType.ITEM_GET,
                "item_use": SFXType.ITEM_USE,  # 020.wav - 아이템 사용
                "potion": SFXType.POTION,  # 005.wav - 포션
                "hi_potion": SFXType.HI_POTION,  # 006.wav - 하이포션
                "x_potion": SFXType.X_POTION,  # 007.wav - 엑스포션
                "elixir": SFXType.ELIXIR,  # 068.wav - 엘릭서
                "phoenix_down": SFXType.PHOENIX_DOWN,  # 379.wav - 피닉스테일
                "treasure_open": SFXType.TREASURE_OPEN,  # 253.wav - 보물상자
                "winning_prize": SFXType.TREASURE_OPEN,  # 특별 아이템은 보물상자음
                "equip": SFXType.EQUIP,  # 444.wav - 장비 장착
                "unequip": SFXType.UNEQUIP,  # 444.wav - 장비 해제
                "save_game": SFXType.SAVE_GAME,  # 001.wav - 저장 (확인음)
                "save_ready": SFXType.SAVE_READY,  # 001.wav - 로드 성공 (확인음)
                "victory": SFXType.LEVEL_UP,  # 승리 효과음은 레벨업음 (381.wav)
                "victory_fanfare": SFXType.LEVEL_UP,  # 승리 팡파르도 레벨업음으로 임시
                "enemy_defeat": SFXType.DEATH,  # 적 처치 효과음 (021.wav)
                "level_up": SFXType.LEVEL_UP,  # 레벨업 효과음
                
                # 전투/마법
                "magic_cast": SFXType.MAGIC_CAST,
                "heal": SFXType.HEAL,
                "sword_hit": SFXType.SWORD_HIT,
                "battle_start": SFXType.BATTLE_SWIRL,  # 042.wav - 전투 시작 소용돌이
                "critical_hit": SFXType.CRITICAL_HIT,  # 크리티컬 히트
                "dodge": SFXType.DODGE,  # 회피
                "protect": SFXType.BUFF_ON,  # 프로텍트 (버프 적용음)
                "silence": SFXType.DEBUFF_ON,  # 사일런스 (디버프 적용음)
                "poison": SFXType.POISON,  # 독
                "haste": SFXType.BUFF_ON,  # 헤이스트
                "slow": SFXType.DEBUFF_ON,  # 슬로우
                "barrier": SFXType.BUFF_ON,  # 배리어
                "berserk": SFXType.BUFF_ON,  # 버서크
                "stop": SFXType.DEBUFF_ON,  # 스톱
                "gun_hit": SFXType.GUN_SHOT,  # 총격
                "gun_critical": SFXType.CRITICAL_HIT,  # 총 크리티컬
                "punch_hit": SFXType.SWORD_HIT,  # 주먹 공격 (검격과 동일)
                "magic_hit": SFXType.MAGIC_HIT,  # 마법 명중
                "limit_break": SFXType.ULTIMATE,  # 리미트 브레이크
                "summon": SFXType.SUMMON,  # 소환
                "fire": SFXType.BURN,  # 화염 마법
                "fire2": SFXType.BURN,  # 화염 마법 2단계
                "fire3": SFXType.ULTIMATE,  # 화염 마법 3단계
                "ice": SFXType.FREEZE,  # 얼음 마법
                "ice2": SFXType.FREEZE,  # 얼음 마법 2단계
                "ice3": SFXType.ULTIMATE,  # 얼음 마법 3단계
                "lightning": SFXType.SHOCK,  # 번개 마법
                "lightning2": SFXType.SHOCK,  # 번개 마법 2단계
                "lightning3": SFXType.ULTIMATE,  # 번개 마법 3단계
                "thunder": SFXType.SHOCK,  # 번개 마법 (별명)
                "thunder2": SFXType.SHOCK,  # 번개 마법 2단계 (별명)
                "thunder3": SFXType.ULTIMATE,  # 번개 마법 3단계 (별명)
                "earth": SFXType.MAGIC_HIT,  # 대지 마법 (마법 명중음 사용)
                "earth2": SFXType.MAGIC_HIT,  # 대지 마법 2단계
                "earth3": SFXType.ULTIMATE,  # 대지 마법 3단계
                "wind": SFXType.MAGIC_HIT,  # 바람 마법 (마법 명중음 사용)
                "wind2": SFXType.MAGIC_HIT,  # 바람 마법 2단계
                "wind3": SFXType.ULTIMATE,  # 바람 마법 3단계
                "water": SFXType.HEAL,  # 물 마법 (치유음 사용, 물=회복)
                "water2": SFXType.HEAL,  # 물 마법 2단계
                "water3": SFXType.ULTIMATE,  # 물 마법 3단계
                "light": SFXType.HEAL,  # 빛 마법 (치유음 사용, 빛=회복)
                "light2": SFXType.HEAL,  # 빛 마법 2단계
                "light3": SFXType.ULTIMATE,  # 빛 마법 3단계
                "dark": SFXType.POISON,  # 어둠 마법 (독음 사용, 어둠=해로움)
                "dark2": SFXType.POISON,  # 어둠 마법 2단계
                "dark3": SFXType.ULTIMATE,  # 어둠 마법 3단계
                "poison": SFXType.POISON,  # 독 마법
                "poison2": SFXType.POISON,  # 독 마법 2단계
                "poison3": SFXType.ULTIMATE,  # 독 마법 3단계
                "heal2": SFXType.HEAL,  # 2단계 치유
                "heal3": SFXType.HEAL,  # 3단계 치유
                "sleep": SFXType.DEBUFF_ON,  # 수면
                "ultima": SFXType.ULTIMATE,  # 알테마
                
                # 기타
                "teleport": SFXType.TELEPORT,
                "level_up": SFXType.LEVEL_UP,
                "skill_learn": SFXType.SKILL_LEARN,
            }
            
            sfx_type = sfx_mapping.get(sfx_type_or_name.lower())
            if not sfx_type:
                # 직접 파일명인 경우 (예: "012.wav") 바로 재생 시도
                if sfx_type_or_name.endswith('.wav'):
                    return self._play_direct_sfx_file(sfx_type_or_name, volume_multiplier)
                # 알 수 없는 SFX는 조용히 무시
                return
        else:
            sfx_type = sfx_type_or_name
        
        # SFXType으로 재생
        if not self.mixer_available:
            # pygame mixer를 사용할 수 없으면 조용히 처리
            return
        
        # mixer 초기화 상태 재확인
        try:
            if not pygame.mixer.get_init():
                if self.debug_mode:
                    print("⚠️ SFX 재생 실패: mixer not initialized")
                return
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ SFX 재생 실패: {e}")
            return
            
        if self.load_sfx(sfx_type):
            sounds = self.sfx_sounds.get(sfx_type, [])
            if sounds:
                # 랜덤하게 사운드 선택
                selected_sound = random.choice(sounds)
                try:
                    # 볼륨 조정
                    volume = min(1.0, self.sfx_volume * volume_multiplier)
                    selected_sound.set_volume(volume)
                    selected_sound.play()
                    
                except Exception as e:
                    if self.debug_mode:
                        print(f"⚠️ SFX 재생 실패: {e}")
            else:
                if self.debug_mode:
                    print(f"🔇 SFX 로드되지 않음: {sfx_type.value}")
        else:
            if self.debug_mode:
                print(f"🔇 SFX 파일 없음으로 {sfx_type.value} 재생을 건너뜁니다")
    
    def _play_direct_sfx_file(self, filename: str, volume_multiplier: float = 1.0):
        """직접 SFX 파일명으로 재생 (예: "012.wav")"""
        if not self.mixer_available:
            return False
            
        try:
            # 파일 경로 구성
            file_path = os.path.join(self.sfx_base_path, filename)
            
            # 파일 존재 확인
            if not os.path.exists(file_path):
                return False
            
            # 사운드 로드 및 재생
            sound = pygame.mixer.Sound(file_path)
            volume = min(1.0, self.sfx_volume * volume_multiplier)
            sound.set_volume(volume)
            sound.play()
            return True
            
        except Exception as e:
            return False
    
    def stop_bgm(self, fade_out: int = 0):
        """BGM 정지 - 상태 보존"""
        if not self.mixer_available:
            return
            
        try:
            if fade_out > 0:
                pygame.mixer.music.fadeout(fade_out)
            else:
                pygame.mixer.music.stop()
            
            # 상태 초기화하지 않음 - 새로운 BGM이 로드될 때 갱신됨
            # self.current_bgm = None
            # self.current_bgm_type = None
            
        except Exception as e:
            print(f"⚠️ BGM 정지 실패: {e}")
    
    def pause_bgm(self):
        """BGM 일시정지 - 안전한 처리"""
        if not self.mixer_available:
            return
            
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"⚠️ BGM 일시정지 실패: {e}")
    
    def resume_bgm(self):
        """BGM 재개 - 안전한 처리"""
        if not self.mixer_available:
            return
            
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"⚠️ BGM 재개 실패: {e}")
    
    def set_bgm_volume(self, volume: float):
        """BGM 볼륨 설정 (0.0 ~ 1.0) - 안전한 처리"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        if not self.mixer_available:
            return
            
        try:
            pygame.mixer.music.set_volume(self.bgm_volume)
        except Exception as e:
            print(f"⚠️ BGM 볼륨 설정 실패: {e}")
    
    def is_bgm_playing(self) -> bool:
        """BGM 재생 상태 확인 - 안전한 처리"""
        if not self.mixer_available:
            return False
            
        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return False
    
    def ensure_bgm_continuity(self, bgm_type: BGMType):
        """BGM 연속성 보장 - 창 전환 시 호출"""
        if (self.current_bgm_type == bgm_type and 
            not self.is_bgm_playing()):
            # 같은 BGM이지만 재생이 중단된 경우 재시작
            self.play_bgm(bgm_type, fade_in=200)
    
    def soft_transition_bgm(self, bgm_type: BGMType):
        """부드러운 BGM 전환 - 끊김 최소화"""
        if self.current_bgm_type != bgm_type:
            self.play_bgm(bgm_type, fade_in=300)
        else:
            self.ensure_bgm_continuity(bgm_type)
    
    def play_bgm_by_name(self, bgm_name: str, loop: bool = True, fade_in: int = 500):
        """문자열 이름으로 BGM 재생"""
        # 문자열을 BGMType으로 매핑
        bgm_mapping = {
            "main theme of ffvii": BGMType.MENU,
            "main_theme": BGMType.MENU,  # ← 누락된 매핑 추가!
            "title": BGMType.MENU,
            "prelude": BGMType.MENU,
            "character_select": BGMType.MENU,
            "dungeon_theme": BGMType.FLOOR_1_3,
            "peaceful": BGMType.FLOOR_1_3,  # 1층 던전 BGM으로 수정!
            "battle": BGMType.BATTLE,
            "victory": BGMType.VICTORY,
            "game_over": BGMType.GAME_OVER,
            # 추가 매핑
            "menu": BGMType.MENU,
            "menu_theme": BGMType.MENU,
            "shop": BGMType.SHOP,
            "boss": BGMType.BOSS,
            "boss_battle": BGMType.BOSS,
            "dungeon": BGMType.FLOOR_1_3,
            "mako_reactor": BGMType.FLOOR_1_3,
            "bombing_mission": BGMType.FLOOR_1_3,
            # 제노바 컴플리트 추가 (보스급 전투 음악으로 매핑)
            "jenova_complete": BGMType.BOSS,
            "jenova_absolute": BGMType.BOSS,
            "aerith_theme": BGMType.AERITH_THEME,  # AI 멀티플레이어용 잔잔한 테마
            "aerith": BGMType.AERITH_THEME
        }
        
        bgm_type = bgm_mapping.get(bgm_name.lower(), BGMType.FLOOR_1_3)
        
        # 디버그: 매핑 정보 조용히
        if self.debug_mode:
            if bgm_name.lower() in bgm_mapping:
                pass  # BGM 매핑 조용히
            else:
                pass  # BGM 매핑 없음 조용히
        
        self._play_bgm_internal(bgm_type, loop=loop, fade_in=fade_in)
    
    def _play_bgm_internal(self, bgm_type: BGMType, loop: bool = True, fade_in: int = 1000):
        """내부 BGM 재생 로직"""
        if not self.mixer_available:
            if self.debug_mode:
                print(f"🔇 pygame mixer를 사용할 수 없어 BGM을 재생하지 않습니다")
            return
        
        # mixer 초기화 상태 재확인
        try:
            if not pygame.mixer.get_init():
                if self.debug_mode:
                    print("⚠️ BGM 재생 실패: mixer not initialized")
                return
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ BGM 재생 실패: {e}")
            return
            
        # 전투 BGM은 항상 새로 선택하도록 (랜덤 재생을 위해)
        if bgm_type in [BGMType.BATTLE, BGMType.BOSS, BGMType.VICTORY]:
            # 전투 관련 BGM은 항상 새로 재생
            pass
        else:
            # 같은 BGM 타입이고 실제로 재생 중인 경우에만 스킵
            try:
                if (self.current_bgm_type == bgm_type and 
                    pygame.mixer.music.get_busy()):
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        print(f"🔄 이미 재생 중인 BGM: {bgm_type.value}")
                    return  # 이미 같은 BGM이 재생 중
            except Exception:
                # pygame.mixer.music.get_busy() 오류 시 재생 진행
                pass
        
        # 🎯 BGM 안전한 전환: 기존 BGM 상태 확인 후 처리
        if self.current_bgm_type != bgm_type:
            # 기존 BGM이 재생 중이면 즉시 정지하고 새 BGM 준비
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()  # 즉시 정지로 충돌 방지
                # 상태 초기화하지 않음 (load_bgm에서 처리)
            except Exception:
                pass
        
        # 새 BGM 로드 및 재생
        if self.load_bgm(bgm_type):
            tracks = self.bgm_tracks.get(bgm_type, [])
            if tracks:
                # BGM 타입에 따른 트랙 선택 방식
                if self._is_field_bgm(bgm_type):
                    # 필드 BGM: 순환 재생
                    if self.current_bgm_type != bgm_type:
                        self.current_track_index = 0  # 새로운 필드면 인덱스 초기화
                    selected_track = tracks[self.current_track_index % len(tracks)]
                    self.current_track_index += 1  # 다음 트랙을 위해 인덱스 증가
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        pass  # 필드 BGM 순환 재생 조용히
                else:
                    # 전투/보스/기타 BGM: 랜덤 선택
                    selected_track = random.choice(tracks)
                    # 승리 BGM은 조용히 재생
                    if bgm_type == BGMType.BATTLE and (hasattr(self, 'debug_mode') and self.debug_mode):
                        pass  # 전투 BGM 조용히 재생
                    elif bgm_type == BGMType.VICTORY:
                        pass  # 승리 BGM은 조용히 재생
                
                try:
                    # 🎵 정상 BGM 재생 모드 - 글리치 모드 체크 비활성화
                    # (BGM 차단 로직 완전 제거)
                    
                    # 🎵 pygame BGM 재생 (정상 모드)
                    pygame.mixer.music.load(selected_track)
                    
                    # BGM 타입별 볼륨 조정 (일부 BGM이 더 큰 음량으로 제작됨)
                    if bgm_type == BGMType.DIFFICULTY_SELECT:
                        # 난이도 선택 BGM을 더 조용히 재생
                        adjusted_volume = self.bgm_volume * 0.6
                    elif bgm_type in [BGMType.MENU, BGMType.MAIN_MENU_OPENING]:
                        # 메인 메뉴 BGM 표준 볼륨
                        adjusted_volume = self.bgm_volume * 0.8
                    else:
                        # 기타 BGM 표준 볼륨
                        adjusted_volume = self.bgm_volume
                    
                    pygame.mixer.music.set_volume(adjusted_volume)
                    loops = -1 if loop else 0
                    pygame.mixer.music.play(loops, fade_ms=fade_in)
                    
                    self.current_bgm = selected_track
                    self.current_bgm_type = bgm_type
                    # BGM 재생 시작 메시지 조용히 처리
                    
                except Exception as e:
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        print(f"⚠️ BGM 재생 실패: {e}")
            else:
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    print(f"🔇 BGM 타입 {bgm_type.value}에 사용 가능한 트랙이 없습니다")
        else:
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"🔇 BGM 로드 실패로 {bgm_type.value} 재생을 건너뜁니다")
    
    def set_sfx_volume(self, volume: float):
        """SFX 볼륨 설정 (0.0 ~ 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        # 로드된 모든 SFX 볼륨 업데이트
        for sounds in self.sfx_sounds.values():
            for sound in sounds:
                sound.set_volume(self.sfx_volume)
    
    def get_bgm_for_floor(self, floor: int) -> BGMType:
        """층수에 따른 BGM 타입 반환 (3층 단위)"""
        if 1 <= floor <= 3:
            return BGMType.FLOOR_1_3
        elif 4 <= floor <= 6:
            return BGMType.FLOOR_4_6
        elif 7 <= floor <= 9:
            return BGMType.FLOOR_7_9
        elif 10 <= floor <= 12:
            return BGMType.FLOOR_10_12
        elif 13 <= floor <= 15:
            return BGMType.FLOOR_13_15
        elif 16 <= floor <= 18:
            return BGMType.FLOOR_16_18
        elif 19 <= floor <= 21:
            return BGMType.FLOOR_19_21
        elif 22 <= floor <= 24:
            return BGMType.FLOOR_22_24
        elif 25 <= floor <= 27:
            return BGMType.FLOOR_25_27
        elif 28 <= floor <= 30:
            return BGMType.FLOOR_28_30
        elif 31 <= floor <= 33:
            return BGMType.FLOOR_31_33
        elif 34 <= floor <= 36:
            return BGMType.FLOOR_34_36
        elif 37 <= floor <= 39:
            return BGMType.FLOOR_37_39
        elif 40 <= floor <= 42:
            return BGMType.FLOOR_40_42
        elif 43 <= floor <= 45:
            return BGMType.FLOOR_43_45
        elif 46 <= floor <= 48:
            return BGMType.FLOOR_46_48
        elif 49 <= floor <= 51:
            return BGMType.FLOOR_49_51
        else:
            return BGMType.FLOOR_52_PLUS
    
    def set_floor_bgm(self, floor: int):
        """층수에 맞는 BGM 재생"""
        bgm_type = self.get_bgm_for_floor(floor)
        self.play_bgm(bgm_type)
    
    def play_skill_sfx(self, skill_name: str, skill_element: str = None):
        """스킬에 따른 적절한 SFX 재생"""
        skill_lower = skill_name.lower()
        
        # 원소 속성 우선 체크 (9가지 원소 모두 지원)
        if skill_element:
            element_lower = skill_element.lower()
            if "fire" in element_lower or "화염" in element_lower:
                self.play_sfx(SFXType.BURN)
                return
            elif "ice" in element_lower or "빙결" in element_lower or "냉기" in element_lower:
                self.play_sfx(SFXType.FREEZE)
                return
            elif "lightning" in element_lower or "번개" in element_lower:
                self.play_sfx(SFXType.SHOCK)
                return
            elif "earth" in element_lower or "대지" in element_lower:
                self.play_sfx(SFXType.MAGIC_HIT)
                return
            elif "wind" in element_lower or "바람" in element_lower:
                self.play_sfx(SFXType.MAGIC_HIT)
                return
            elif "water" in element_lower or "물" in element_lower:
                self.play_sfx(SFXType.HEAL)
                return
            elif "light" in element_lower or "빛" in element_lower:
                self.play_sfx(SFXType.HEAL)
                return
            elif "dark" in element_lower or "어둠" in element_lower:
                self.play_sfx(SFXType.POISON)
                return
            elif "poison" in element_lower or "독" in element_lower:
                self.play_sfx(SFXType.POISON)
                return
        
        # 스킬 이름별 특별 처리 (9가지 원소 키워드)
        if "파이어볼" in skill_name or "화염구" in skill_name or "화염" in skill_lower:
            self.play_sfx(SFXType.BURN)
        elif "아이스" in skill_lower or "빙결" in skill_lower or "냉기" in skill_lower:
            self.play_sfx(SFXType.FREEZE)
        elif "라이트닝" in skill_lower or "번개" in skill_lower:
            self.play_sfx(SFXType.SHOCK)
        elif "대지" in skill_lower or "어스" in skill_lower:
            self.play_sfx(SFXType.MAGIC_HIT)
        elif "바람" in skill_lower or "윈드" in skill_lower:
            self.play_sfx(SFXType.MAGIC_HIT)
        elif "물" in skill_lower or "워터" in skill_lower:
            self.play_sfx(SFXType.HEAL)
        elif "빛" in skill_lower or "라이트" in skill_lower or "홀리" in skill_lower:
            self.play_sfx(SFXType.HEAL)
        elif "어둠" in skill_lower or "다크" in skill_lower or "암흑" in skill_lower:
            self.play_sfx(SFXType.POISON)
        elif "독" in skill_lower or "포이즌" in skill_lower:
            self.play_sfx(SFXType.POISON)
        # 스킬 타입별 SFX 매핑
        elif any(word in skill_lower for word in ["검", "베기", "강타", "일격"]):
            self.play_sfx(SFXType.SWORD_HIT)
        elif any(word in skill_lower for word in ["마법", "매직", "spell"]):
            self.play_sfx(SFXType.MAGIC_CAST)
        elif any(word in skill_lower for word in ["화살", "사격", "저격"]):
            self.play_sfx(SFXType.ARROW_SHOT)
        elif any(word in skill_lower for word in ["총", "미사일", "폭탄"]):
            self.play_sfx(SFXType.GUN_SHOT)
        elif any(word in skill_lower for word in ["폭발", "메테오"]):
            self.play_sfx(SFXType.EXPLOSION)
        elif any(word in skill_lower for word in ["치유", "회복", "힐"]):
            self.play_sfx(SFXType.HEAL)
        elif any(word in skill_lower for word in ["소환", "바하무트"]):
            self.play_sfx(SFXType.SUMMON)
        elif any(word in skill_lower for word in ["궁극", "최후", "아포칼립스"]):
            self.play_sfx(SFXType.ULTIMATE)
        else:
            # 기본 공격음
            self.play_sfx(SFXType.SWORD_HIT)
    
    def play_status_sfx(self, status_name: str, is_applied: bool = True):
        """상태이상에 따른 SFX 재생"""
        status_lower = status_name.lower()
        
        if "독" in status_lower:
            self.play_sfx(SFXType.POISON)
        elif "화상" in status_lower or "번" in status_lower:
            self.play_sfx(SFXType.BURN)
        elif "빙결" in status_lower or "얼음" in status_lower:
            self.play_sfx(SFXType.FREEZE)
        elif "감전" in status_lower or "번개" in status_lower:
            self.play_sfx(SFXType.SHOCK)
        elif any(word in status_lower for word in ["축복", "보호", "힘", "신속"]):
            if is_applied:
                self.play_sfx(SFXType.BUFF_ON)
            else:
                self.play_sfx(SFXType.BUFF_OFF)
        else:
            if is_applied:
                self.play_sfx(SFXType.DEBUFF_ON)
            else:
                self.play_sfx(SFXType.DEBUFF_OFF)
    
    def play_dungeon_bgm(self, floor: int):
        """던전 층수에 맞는 BGM 재생"""
        if self.debug_mode:
            pass  # 던전 BGM 호출 조용히
        
        # 층수에 맞는 BGM 타입 가져오기
        bgm_type = self.get_bgm_for_floor(floor)
        
        if self.debug_mode:
            pass  # 층수별 BGM 타입 조용히
        
        # BGM 재생
        self._play_bgm_internal(bgm_type)
        
        # BGM 재생
        self.play_bgm(bgm_type, loop=True, fade_in=500)
    
    def cleanup(self):
        """오디오 시스템 정리 - 안전한 처리"""
        if not self.mixer_available:
            return
            
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            print("✅ 오디오 시스템 정리 완료")
        except Exception as e:
            print(f"⚠️ 오디오 정리 실패: {e}")

# 전역 오디오 매니저 (안전한 초기화)
audio_manager = None

def get_audio_manager(debug_mode: bool = False) -> AudioManager:
    """오디오 매니저 반환"""
    global audio_manager
    if audio_manager is None:
        try:
            audio_manager = AudioManager(debug_mode=debug_mode)
        except Exception as e:
            print(f"⚠️ 오디오 매니저 초기화 실패: {e}")
            # 더미 오디오 매니저 생성
            audio_manager = DummyAudioManager()
    return audio_manager

class DummyAudioManager:
    """사운드가 없을 때 사용하는 더미 오디오 매니저"""
    
    def __init__(self):
        self.debug_mode = False  # 더미에서는 디버그 모드 비활성화
        self.mixer_available = False
        self.bgm_volume = 0.7
        self.sfx_volume = 0.8
        self.current_bgm = None
        self.current_bgm_type = None
        # 더미 오디오 매니저 메시지 조용히 처리
    
    def play_bgm(self, *args, **kwargs):
        """더미 BGM 재생"""
        pass
    
    def play_sfx(self, *args, **kwargs):
        """더미 SFX 재생"""
        pass
    
    def stop_bgm(self, *args, **kwargs):
        """더미 BGM 정지"""
        pass
    
    def pause_bgm(self):
        """더미 BGM 일시정지"""
        pass
    
    def resume_bgm(self):
        """더미 BGM 재개"""
        pass
    
    def set_bgm_volume(self, volume: float):
        """더미 BGM 볼륨 설정"""
        self.bgm_volume = volume
    
    def set_sfx_volume(self, volume: float):
        """더미 SFX 볼륨 설정"""
        self.sfx_volume = volume
    
    def is_bgm_playing(self) -> bool:
        """더미 BGM 재생 상태 (항상 False)"""
        return False
    
    def set_floor_bgm(self, floor: int):
        """더미 층수 BGM 설정"""
        pass
    
    def cleanup(self):
        """더미 정리"""
        pass

def create_audio_directories():
    """오디오 디렉토리 생성"""
    try:
        os.makedirs("game/audio/bgm", exist_ok=True)
        os.makedirs("game/audio/sfx", exist_ok=True)
        print("오디오 디렉토리 생성 완료")
    except Exception as e:
        print(f"디렉토리 생성 실패: {e}")

# 초기화 시 디렉토리 생성
create_audio_directories()

# FFVII 스타일 확장 기능
def play_skill_audio(skill_name: str, element: str = "무속성"):
    """스킬 사용시 적절한 오디오 재생"""
    # 스킬 이름 기반 SFX 매핑
    audio_mgr = get_audio_manager()
    
    if "검" in skill_name or "베기" in skill_name or "찌르기" in skill_name:
        audio_mgr.play_sfx(SFXType.SWORD_HIT)
    elif "화염" in skill_name or "파이어" in skill_name:
        audio_mgr.play_sfx(SFXType.MAGIC_CAST)  # FIRE_MAGIC 대신 MAGIC_CAST 사용
    elif "빙결" in skill_name or "아이스" in skill_name:
        audio_mgr.play_sfx(SFXType.MAGIC_CAST)  # ICE_MAGIC 대신 MAGIC_CAST 사용
    elif "번개" in skill_name or "썬더" in skill_name:
        audio_mgr.play_sfx(SFXType.MAGIC_CAST)  # LIGHTNING_MAGIC 대신 MAGIC_CAST 사용
    elif "치유" in skill_name or "케어" in skill_name:
        audio_mgr.play_sfx(SFXType.HEAL)
    elif "궁극기" in skill_name or "최후" in skill_name:
        audio_mgr.play_sfx(SFXType.ULTIMATE)
    else:
        audio_mgr.play_sfx(SFXType.MAGIC_CAST)

def set_floor_bgm(floor: int):
    """층수에 따른 BGM 자동 설정"""
    audio_mgr = get_audio_manager()
    
    if 1 <= floor <= 3:
        audio_mgr.play_bgm(BGMType.FLOOR_1_3)
    elif 4 <= floor <= 6:
        audio_mgr.play_bgm(BGMType.FLOOR_4_6)
    elif 7 <= floor <= 9:
        audio_mgr.play_bgm(BGMType.FLOOR_7_9)
    elif 10 <= floor <= 12:
        audio_mgr.play_bgm(BGMType.FLOOR_10_12)
    elif 13 <= floor <= 15:
        audio_mgr.play_bgm(BGMType.FLOOR_13_15)
    elif 16 <= floor <= 18:
        audio_mgr.play_bgm(BGMType.FLOOR_16_18)
    elif 19 <= floor <= 21:
        audio_mgr.play_bgm(BGMType.FLOOR_19_21)
    elif 22 <= floor <= 24:
        audio_mgr.play_bgm(BGMType.FLOOR_22_24)
    elif 25 <= floor <= 27:
        audio_mgr.play_bgm(BGMType.FLOOR_25_27)
    elif 28 <= floor <= 30:
        audio_mgr.play_bgm(BGMType.FLOOR_28_30)
    elif 31 <= floor <= 33:
        audio_mgr.play_bgm(BGMType.FLOOR_31_33)
    elif 34 <= floor <= 36:
        audio_mgr.play_bgm(BGMType.FLOOR_34_36)
    elif 37 <= floor <= 39:
        audio_mgr.play_bgm(BGMType.FLOOR_37_39)
    elif 40 <= floor <= 42:
        audio_mgr.play_bgm(BGMType.FLOOR_40_42)
    elif 43 <= floor <= 45:
        audio_mgr.play_bgm(BGMType.FLOOR_43_45)
    elif 46 <= floor <= 48:
        audio_mgr.play_bgm(BGMType.FLOOR_46_48)
    elif 49 <= floor <= 51:
        audio_mgr.play_bgm(BGMType.FLOOR_49_51)
    else:
        audio_mgr.play_bgm(BGMType.FLOOR_52_PLUS)

def play_status_audio(status_name: str, is_buff: bool):
    """상태이상에 따른 오디오 재생"""
    audio_mgr = get_audio_manager()
    
    if is_buff:
        audio_mgr.play_sfx(SFXType.BUFF_ON)
    else:
        if "독" in status_name:
            audio_mgr.play_sfx(SFXType.POISON)
        elif "화상" in status_name:
            audio_mgr.play_sfx(SFXType.BURN)
        elif "빙결" in status_name:
            audio_mgr.play_sfx(SFXType.FREEZE)
        else:
            audio_mgr.play_sfx(SFXType.DEBUFF_ON)

# 호환성을 위한 별칭
AudioSystem = AudioManager

def get_audio_system(debug_mode: bool = False):
    """오디오 시스템 반환 (호환성을 위한 함수)"""
    return get_audio_manager()

def get_unified_audio_system(debug_mode: bool = False):
    """통합 오디오 시스템 반환 (호환성을 위한 함수)"""
    return get_audio_manager()

# 전투 관련 편의 함수들
def play_battle_bgm():
    """전투 BGM 재생"""
    audio_mgr = get_audio_manager()
    audio_mgr.play_bgm(BGMType.BATTLE)

def play_boss_bgm():
    """보스 BGM 재생"""
    audio_mgr = get_audio_manager()
    audio_mgr.play_bgm(BGMType.BOSS)

def play_battle_start_sfx():
    """전투 시작 효과음 재생"""
    audio_mgr = get_audio_manager()
    audio_mgr.play_sfx(SFXType.BATTLE_SWIRL)  # 전투 시작 소용돌이

def play_victory_bgm():
    """승리 BGM 재생"""
    audio_mgr = get_audio_manager()
    audio_mgr.play_bgm(BGMType.VICTORY)

def stop_all_bgm():
    """모든 BGM 정지"""
    audio_mgr = get_audio_manager()
    audio_mgr.stop_bgm()
