#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Dawn of Stellar - 스마트 AI 멀티플레이어 시스템
기존 캐릭터 생성 JSON을 활용하여 AI 속성을 추가하는 시스템
멀티플레이어 전용 세이브 시스템 + 캐릭터 중복 방지 + 안전 종료
"""

import os
import sys
import json
import random
import hashlib
import uuid
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 안전 종료 핸들러 import
try:
    from safe_exit_handler import setup_safe_exit, safe_exit, emergency_backup
    SAFE_EXIT_AVAILABLE = True
    print("🛡️ 안전 종료 시스템 로드 완료")
except ImportError:
    print("⚠️ 안전 종료 시스템을 찾을 수 없습니다.")
    SAFE_EXIT_AVAILABLE = False

# 한글 입력 지원을 위한 인코딩 설정
if sys.platform.startswith('win'):
    import codecs
    import locale
    import msvcrt
    
    # 콘솔 인코딩 설정
    try:
        # Windows 콘솔 인코딩을 UTF-8으로 설정
        os.system('chcp 65001 > nul')
        
        # 시스템 로케일 설정
        locale.setlocale(locale.LC_ALL, '')
        
        # stdout/stdin 인코딩 설정
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stdin = codecs.getreader('utf-8')(sys.stdin.buffer)
        
        print("✅ 한글 입력 시스템 초기화 완료")
    except Exception as e:
        print(f"⚠️ 한글 입력 시스템 초기화 실패: {e}")
        print("💡 영어로 입력하거나 관리자 권한으로 실행해보세요.")

# ========================================
# 🔤 스마트 한글 입력 시스템 (고급 버전)
# ========================================

def english_to_korean(text: str) -> str:
    """영어 입력을 한글로 변환"""
    # 영어 키보드를 한글로 매핑
    eng_to_kor = {
        'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
        'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
        'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
        # 대문자도 포함
        'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'Y': 'ㅛ', 'U': 'ㅕ', 'I': 'ㅑ', 'O': 'ㅒ', 'P': 'ㅖ',
    }
    
    # 먼저 자모로 변환
    jamo_result = ""
    for char in text:
        if char in eng_to_kor:
            jamo_result += eng_to_kor[char]
        else:
            jamo_result += char
    
    # 자모를 한글로 조합
    return combine_jamo_to_hangul(jamo_result)

def combine_jamo_to_hangul(jamo_text: str) -> str:
    """자모를 조합하여 완성된 한글로 만들기"""
    # 초성, 중성, 종성 정의
    CHOSUNG = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    JUNGSUNG = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    JONGSUNG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    
    # 자모가 너무 적으면 그대로 반환
    if len(jamo_text) < 2:
        return jamo_text
    
    result = ""
    i = 0
    
    while i < len(jamo_text):
        char = jamo_text[i]
        
        # 초성으로 사용할 수 있는지 확인
        if char in CHOSUNG:
            cho_idx = CHOSUNG.index(char)
            
            # 다음 글자가 중성인지 확인
            if i + 1 < len(jamo_text):
                next_char = jamo_text[i + 1]
                
                # 중성인지 확인
                if next_char in JUNGSUNG:
                    jung_idx = JUNGSUNG.index(next_char)
                    jong_idx = 0  # 종성 없음
                    advance = 2
                    
                    # 그 다음 글자가 종성으로 사용 가능한지 확인
                    if i + 2 < len(jamo_text):
                        third_char = jamo_text[i + 2]
                        # 종성으로 사용할 수 있는 자음인지 확인
                        if third_char in JONGSUNG[1:]:  # 빈 종성 제외
                            # 하지만 그 다음에 중성이 오면 새 글자 시작
                            if i + 3 < len(jamo_text) and jamo_text[i + 3] in JUNGSUNG:
                                # 종성을 사용하지 말고 다음 글자 시작
                                pass
                            else:
                                jong_idx = JONGSUNG.index(third_char)
                                advance = 3
                    
                    # 유니코드로 조합
                    unicode_val = 0xAC00 + (cho_idx * 21 * 28) + (jung_idx * 28) + jong_idx
                    result += chr(unicode_val)
                    i += advance
                    continue
        
        # 조합하지 못한 경우 그대로 추가
        result += char
        i += 1
    
    return result

def safe_korean_input(prompt: str = "", allow_back: bool = True) -> str:
    """한글 입력을 안전하게 처리하는 함수 - 스마트 변환 시스템"""
    try:
        if allow_back:
            full_prompt = f"{prompt} (뒤로가기: q) "
        else:
            full_prompt = prompt
            
        while True:
            # 기본 input() 사용하되 한글 입력 상태 처리 개선
            if full_prompt:
                print(full_prompt, end='', flush=True)
            
            # 한글 입력 상태에서 안전한 처리
            try:
                result = input().strip()
                
                # 뒤로가기 처리 (영어/한글 모두 지원)
                if allow_back and result.lower() in ['q', 'ㅂ', 'back']:
                    return "BACK"
                
                # 빈 입력이면 다시 입력 요청
                if not result:
                    print("입력이 비어있습니다. 다시 입력해주세요.")
                    continue
                
                # 🚀 스마트 한글 변환 시스템
                if all(ord(c) < 128 for c in result):  # 모든 문자가 ASCII (영어)
                    # 1. 일반적인 영어 응답은 변환하지 않음
                    common_english = {'y', 'n', 'yes', 'no', 'ok', 'cancel', 'back', 'q', 'exit'}
                    if result.lower() in common_english:
                        return result
                    
                    # 2. 숫자나 특수문자만 있으면 변환하지 않음  
                    if result.isdigit() or not result.isalpha():
                        return result
                    
                    # 3. 길이가 1글자이고 의미있는 영어가 아니면 자동 변환
                    if len(result) == 1 and result.lower() not in common_english:
                        korean_converted = english_to_korean(result)
                        if korean_converted != result:
                            print(f"🔄 자동 변환: '{result}' → '{korean_converted}'")
                            return korean_converted
                    
                    # 4. 길이가 2글자 이상이면 사용자에게 선택권 제공
                    if len(result) >= 2:
                        korean_converted = english_to_korean(result)
                        if korean_converted != result:
                            print(f"\n💡 영어 입력을 한글로 변환: '{result}' → '{korean_converted}'")
                            print("🎯 팁: F9키로 변환 모드를 끄거나 켤 수 있습니다")
                            choice = input("변환된 한글을 사용하시겠습니까? (y/n, 엔터=예): ").strip().lower()
                            if choice in ['', 'y', 'yes', 'ㅛ']:
                                result = korean_converted
                    
                # 키보드 버퍼 정리 (Windows에서 한글 입력 후 문제 해결)
                if sys.platform.startswith('win'):
                    try:
                        import msvcrt
                        # 남은 키 입력 모두 제거
                        while msvcrt.kbhit():
                            msvcrt.getch()
                    except:
                        pass
                
                return result
                
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                sys.exit(0)
            except EOFError:
                if allow_back:
                    return "BACK"
                return ""
                
    except UnicodeDecodeError:
        # 인코딩 문제 발생 시 재시도
        print("한글 입력에 문제가 있습니다. 한영키를 눌러 입력 모드를 확인해주세요.")
        return safe_korean_input(prompt, allow_back)
            
    except Exception as e:
        print(f"입력 오류: {e}")
        if allow_back:
            return "BACK"
        return ""

# ========================================
# 🔧 기존 호환성 유지를 위한 래퍼 함수들  
# ========================================

def safe_input(prompt: str, max_length: int = 100, allow_empty: bool = False) -> str:
    """안전한 한글 입력 함수"""
    while True:
        try:
            print(prompt, end='', flush=True)
            
            if sys.platform.startswith('win'):
                # Windows에서 한글 입력을 위한 특별 처리
                input_chars = []
                
                while True:
                    if msvcrt.kbhit():
                        char = msvcrt.getch()
                        
                        # Enter 키 (CR)
                        if char == b'\r':
                            print()  # 줄바꿈
                            break
                        
                        # Backspace 키
                        elif char == b'\x08':
                            if input_chars:
                                input_chars.pop()
                                # 백스페이스 처리 (커서 이동 + 공백 + 커서 이동)
                                print('\b \b', end='', flush=True)
                        
                        # ESC 키 (종료)
                        elif char == b'\x1b':
                            print()
                            return "EXIT_COMMAND"
                        
                        # 일반 문자
                        elif len(char) == 1 and ord(char) >= 32:  # 출력 가능한 ASCII
                            if len(input_chars) < max_length:
                                input_chars.append(char.decode('utf-8', errors='ignore'))
                                print(char.decode('utf-8', errors='ignore'), end='', flush=True)
                        
                        # 멀티바이트 문자 (한글 등)
                        elif len(char) == 1 and ord(char) > 127:
                            try:
                                # 한글 입력 처리
                                extended_chars = [char]
                                
                                # 추가 바이트 수집
                                while msvcrt.kbhit():
                                    next_char = msvcrt.getch()
                                    if ord(next_char) > 127:
                                        extended_chars.append(next_char)
                                    else:
                                        # 다음 문자가 ASCII면 다시 처리 대기열에 넣어야 하지만
                                        # 단순하게 처리하기 위해 그냥 무시
                                        break
                                
                                # 멀티바이트 문자 디코딩 시도
                                multi_byte = b''.join(extended_chars)
                                decoded_char = multi_byte.decode('utf-8', errors='ignore')
                                
                                if decoded_char and len(input_chars) < max_length:
                                    input_chars.append(decoded_char)
                                    print(decoded_char, end='', flush=True)
                                    
                            except Exception:
                                pass  # 디코딩 실패 시 무시
                
                result = ''.join(input_chars).strip()
                
            else:
                # Linux/Mac에서는 기본 input() 사용
                result = input().strip()
            
            # 입력 검증
            if result == "EXIT_COMMAND":
                return result
            
            if not result and not allow_empty:
                print("❌ 입력이 비어있습니다. 다시 입력해주세요.")
                continue
            
            if len(result) > max_length:
                print(f"❌ 입력이 너무 깁니다. (최대 {max_length}자)")
                continue
            
            return result
            
        except UnicodeDecodeError:
            print("❌ 입력 인코딩 오류. 다시 시도해주세요.")
            continue
        except KeyboardInterrupt:
            print("\n🛑 사용자가 입력을 취소했습니다.")
            return "EXIT_COMMAND"
        except Exception as e:
            print(f"❌ 입력 오류: {e}")
            print("💡 다시 시도하거나 영어로 입력해주세요.")
            continue

def get_korean_safe_input(prompt: str, max_length: int = 20) -> str:
    """한글 안전 입력 (이름 등에 사용) - 스마트 한글 입력 시스템 사용"""
    print(f"\n{prompt}")
    print("💡 스마트 입력 시스템:")
    print("  • 한글로 직접 입력하거나 영어로 입력하면 자동 변환됩니다")
    print("  • 영어 키보드로도 자연스러운 한글 입력 가능")
    print("  • 'q' 또는 'back'을 입력하면 뒤로가기")
    
    while True:
        result = safe_korean_input("👤 입력", allow_back=True)
        
        if result == "BACK":
            return ""
        
        if result == "EXIT_COMMAND":
            return ""
        
        # 길이 검증
        if len(result) > max_length:
            print(f"❌ 입력이 너무 깁니다. (최대 {max_length}자)")
            continue
            
        return result

# 기존 시스템들 import
try:
    from complete_27_job_system import job_system
    from ai_training_system import training_system
    from advanced_ai_companion import AdvancedAICompanion, AIPersonalityType
    SYSTEMS_AVAILABLE = True
    ADVANCED_AI_AVAILABLE = True
    print("✅ 고급 AI 시스템 로드 완료")
except ImportError as e:
    print(f"⚠️ 일부 모듈을 찾을 수 없습니다: {e}")
    SYSTEMS_AVAILABLE = False
    ADVANCED_AI_AVAILABLE = False
try:
    from complete_27_job_system import Complete27JobSystem
    from ai_training_system import training_system
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 일부 모듈을 찾을 수 없습니다: {e}")
    SYSTEMS_AVAILABLE = False

class PlayerCentricAISystem:
    """플레이어 중심 AI 멀티플레이어 시스템"""
    
    def __init__(self):
        self.player_character = None
        self.ai_companions = []
        self.party_size = 4
        self.character_presets = {}
        self.party_presets = {}
        
        # 멀티플레이어 전용 세이브 시스템
        self.multiplayer_saves_dir = Path("multiplayer_saves")
        self.character_locks_file = Path("character_locks.json")
        self.adventure_backups_dir = Path("adventure_backups")
        self.current_adventure_id = None
        self.character_locks = {}
        
        # 디렉토리 생성
        self.multiplayer_saves_dir.mkdir(exist_ok=True)
        self.adventure_backups_dir.mkdir(exist_ok=True)
        
        # 캐릭터 잠금 상태 로드
        self.load_character_locks()
        
        # 5단계: 백그라운드 학습 시스템 초기화
        self.learning_active = False
        self.learning_thread = None
        self.learning_data = {}
        self.ai_improvement_records = {}
        
        # 안전 종료 시스템 설정
        if SAFE_EXIT_AVAILABLE:
            setup_safe_exit(self, 'safe_cleanup')
            print("🛡️ 안전 종료 시스템 연동 완료")
        
        # 기존 캐릭터 프리셋 로드
        self.load_character_presets()
        
        # 백그라운드 학습 시스템 초기화
        self._init_background_learning()
        
        # AI 성격 타입 정의
        self.ai_personalities = {
            "용감한": {
                "description": "적극적으로 전투에 참여하며 위험을 두려워하지 않음",
                "combat_style": "aggressive",
                "help_tendency": 0.8,
                "risk_taking": 0.9
            },
            "신중한": {
                "description": "상황을 잘 판단하고 계획적으로 행동함",
                "combat_style": "tactical",
                "help_tendency": 0.9,
                "risk_taking": 0.3
            },
            "지원형": {
                "description": "동료를 돕는 것을 최우선으로 생각함",
                "combat_style": "support",
                "help_tendency": 1.0,
                "risk_taking": 0.4
            },
            "독립적": {
                "description": "자신만의 방식으로 전투를 수행함",
                "combat_style": "independent",
                "help_tendency": 0.5,
                "risk_taking": 0.7
            },
            "적응형": {
                "description": "상황에 따라 유연하게 대응함",
                "combat_style": "adaptive",
                "help_tendency": 0.7,
                "risk_taking": 0.6
            }
        }
        
        print("🎮 플레이어 중심 AI 멀티플레이어 시스템 초기화 완료")
    
    def safe_cleanup(self):
        """안전 종료 시 정리 작업"""
        print("🧹 멀티플레이어 시스템 안전 정리 시작...")
        
        try:
            # 1. 현재 상태 응급 백업
            if SAFE_EXIT_AVAILABLE and (self.player_character or self.ai_companions):
                backup_data = {
                    "player_character": self.player_character,
                    "ai_companions": self.ai_companions,
                    "current_adventure_id": self.current_adventure_id,
                    "character_locks": self.character_locks.copy()
                }
                emergency_backup(backup_data, "multiplayer_system")
            
            # 2. 모험 세션 종료
            if self.current_adventure_id:
                self.end_adventure_session()
            
            # 3. 모든 캐릭터 잠금 해제
            self.unlock_all_characters()
            
            # 4. 파티 데이터 자동 저장
            if self.player_character or self.ai_companions:
                self.save_party_data()
            
            print("✅ 멀티플레이어 시스템 안전 정리 완료")
            
        except Exception as e:
            print(f"❌ 멀티플레이어 시스템 정리 중 오류: {e}")
    
    def unlock_all_characters(self):
        """모든 캐릭터 잠금 강제 해제"""
        try:
            if self.character_locks:
                print(f"🔓 {len(self.character_locks)}개 캐릭터 잠금 해제 중...")
                
                for char_hash, lock_info in self.character_locks.items():
                    char_name = lock_info.get("character_name", "알 수 없음")
                    print(f"  🔓 {char_name} 잠금 해제")
                
                self.character_locks.clear()
                self.save_character_locks()
                print("✅ 모든 캐릭터 잠금 해제 완료")
            else:
                print("ℹ️ 잠긴 캐릭터 없음")
                
        except Exception as e:
            print(f"❌ 캐릭터 잠금 해제 실패: {e}")
    
    def emergency_save_all(self):
        """응급 상황에서 모든 데이터 저장"""
        try:
            print("🆘 응급 데이터 저장 중...")
            
            # 파티 데이터 저장
            if self.player_character or self.ai_companions:
                self.save_party_data()
            
            # 현재 상태 백업
            if hasattr(self, 'backup_adventure_state'):
                self.backup_adventure_state()
            
            # 잠금 상태 저장
            self.save_character_locks()
            
            print("✅ 응급 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ 응급 데이터 저장 실패: {e}")
    
    def load_character_locks(self):
        """캐릭터 잠금 상태 로드"""
        try:
            if self.character_locks_file.exists():
                with open(self.character_locks_file, 'r', encoding='utf-8') as f:
                    self.character_locks = json.load(f)
                    
                # 만료된 잠금 제거 (24시간 초과)
                current_time = datetime.now().timestamp()
                expired_locks = []
                
                for char_hash, lock_info in self.character_locks.items():
                    if current_time - lock_info.get("lock_time", 0) > 86400:  # 24시간
                        expired_locks.append(char_hash)
                
                for char_hash in expired_locks:
                    del self.character_locks[char_hash]
                
                if expired_locks:
                    self.save_character_locks()
                    print(f"🗑️ 만료된 캐릭터 잠금 {len(expired_locks)}개 제거")
                    
            print(f"🔒 캐릭터 잠금 상태 로드 완료 (활성 잠금: {len(self.character_locks)}개)")
        except Exception as e:
            print(f"⚠️ 캐릭터 잠금 상태 로드 실패: {e}")
            self.character_locks = {}
    
    def save_character_locks(self):
        """캐릭터 잠금 상태 저장"""
        try:
            with open(self.character_locks_file, 'w', encoding='utf-8') as f:
                json.dump(self.character_locks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 캐릭터 잠금 상태 저장 실패: {e}")
    
    def get_character_hash(self, character_data: Dict) -> str:
        """캐릭터의 고유 해시 생성 (이름 + 직업 + 생성시간)"""
        unique_string = f"{character_data['name']}_{character_data['character_class']}_{character_data.get('creation_time', '')}"
        return hashlib.md5(unique_string.encode('utf-8')).hexdigest()
    
    def is_character_locked(self, character_data: Dict) -> tuple[bool, str]:
        """캐릭터가 다른 세이브에서 사용 중인지 확인"""
        char_hash = self.get_character_hash(character_data)
        
        if char_hash in self.character_locks:
            lock_info = self.character_locks[char_hash]
            return True, lock_info.get("adventure_id", "알 수 없는 모험")
        
        return False, ""
    
    def lock_character(self, character_data: Dict, adventure_id: str):
        """캐릭터를 특정 모험에 잠금"""
        char_hash = self.get_character_hash(character_data)
        
        self.character_locks[char_hash] = {
            "adventure_id": adventure_id,
            "character_name": character_data["name"],
            "character_class": character_data["character_class"],
            "lock_time": datetime.now().timestamp()
        }
        
        self.save_character_locks()
        print(f"🔒 캐릭터 '{character_data['name']}' 잠금 설정")
    
    def unlock_character(self, character_data: Dict):
        """캐릭터 잠금 해제"""
        char_hash = self.get_character_hash(character_data)
        
        if char_hash in self.character_locks:
            del self.character_locks[char_hash]
            self.save_character_locks()
            print(f"🔓 캐릭터 '{character_data['name']}' 잠금 해제")
    
    def create_adventure_session(self) -> str:
        """새로운 모험 세션 생성"""
        self.current_adventure_id = f"adventure_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        return self.current_adventure_id
    
    def create_exclusive_save(self, save_data: Dict) -> str:
        """멀티플레이어 전용 세이브 생성 (복사 방지)"""
        if not self.current_adventure_id:
            self.current_adventure_id = self.create_adventure_session()
        
        # 보안 정보 추가
        save_data["multiplayer_meta"] = {
            "adventure_id": self.current_adventure_id,
            "save_type": "EXCLUSIVE_MULTIPLAYER",
            "creation_time": datetime.now().isoformat(),
            "checksum": self._calculate_save_checksum(save_data),
            "locked_characters": list(self.character_locks.keys()),
            "version": "1.0.0"
        }
        
        # 파일명 생성 (복사 감지 가능)
        save_filename = f"mp_exclusive_{self.current_adventure_id}.json"
        save_path = self.multiplayer_saves_dir / save_filename
        
        # 저장
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 전용 멀티플레이어 세이브 생성: {save_filename}")
        return str(save_path)
    
    def _calculate_save_checksum(self, save_data: Dict) -> str:
        """세이브 데이터의 체크섬 계산 (무결성 검증용)"""
        # 메타데이터 제외하고 체크섬 계산
        save_copy = save_data.copy()
        save_copy.pop("multiplayer_meta", None)
        
        save_string = json.dumps(save_copy, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(save_string.encode('utf-8')).hexdigest()
    
    def validate_save_integrity(self, save_path: str) -> tuple[bool, str]:
        """세이브 파일 무결성 검증"""
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            if "multiplayer_meta" not in save_data:
                return False, "멀티플레이어 세이브가 아닙니다"
            
            meta = save_data["multiplayer_meta"]
            
            # 체크섬 검증
            current_checksum = self._calculate_save_checksum(save_data)
            original_checksum = meta.get("checksum", "")
            
            if current_checksum != original_checksum:
                return False, "세이브 파일이 변조되었습니다"
            
            # 파일명 검증
            expected_filename = f"mp_exclusive_{meta['adventure_id']}.json"
            actual_filename = Path(save_path).name
            
            if actual_filename != expected_filename:
                return False, "세이브 파일이 복사되었습니다"
            
            return True, "무결성 검증 통과"
            
        except Exception as e:
            return False, f"검증 중 오류: {e}"
    
    def backup_adventure_state(self) -> str:
        """현재 모험 상태 응급 백업 (최대 3개 유지)"""
        if not self.current_adventure_id:
            return ""
        
        # 백업 데이터 생성
        backup_data = {
            "adventure_id": self.current_adventure_id,
            "backup_time": datetime.now().isoformat(),
            "player_character": self.player_character,
            "ai_companions": self.ai_companions,
            "character_locks": self.character_locks.copy()
        }
        
        # 백업 파일명
        timestamp = int(datetime.now().timestamp())
        backup_filename = f"emergency_backup_{self.current_adventure_id}_{timestamp}.json"
        backup_path = self.adventure_backups_dir / backup_filename
        
        # 백업 저장
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # 오래된 백업 정리 (3개 초과시)
        self._cleanup_old_backups()
        
        print(f"🆘 응급 백업 생성: {backup_filename}")
        return str(backup_path)
    
    def _cleanup_old_backups(self):
        """오래된 백업 파일 정리 (최대 3개 유지)"""
        if not self.current_adventure_id:
            return
        
        # 현재 모험의 백업 파일들 찾기
        backup_pattern = f"emergency_backup_{self.current_adventure_id}_*.json"
        backup_files = list(self.adventure_backups_dir.glob(backup_pattern))
        
        # 생성 시간순 정렬 (최신순)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # 3개 초과시 오래된 것 삭제
        for old_backup in backup_files[3:]:
            try:
                old_backup.unlink()
                print(f"🗑️ 오래된 백업 삭제: {old_backup.name}")
            except Exception as e:
                print(f"⚠️ 백업 삭제 실패: {e}")
    
    def restore_from_backup(self, backup_path: str = None) -> bool:
        """백업에서 모험 상태 복원"""
        try:
            if not backup_path:
                # 가장 최근 백업 찾기
                if self.current_adventure_id:
                    backup_pattern = f"emergency_backup_{self.current_adventure_id}_*.json"
                    backup_files = list(self.adventure_backups_dir.glob(backup_pattern))
                    
                    if not backup_files:
                        print("❌ 복원할 백업이 없습니다.")
                        return False
                    
                    # 가장 최신 백업 선택
                    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    backup_path = str(backup_files[0])
                else:
                    print("❌ 활성 모험이 없습니다.")
                    return False
            
            # 백업 로드
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # 상태 복원
            self.current_adventure_id = backup_data["adventure_id"]
            self.player_character = backup_data["player_character"]
            self.ai_companions = backup_data["ai_companions"]
            self.character_locks = backup_data["character_locks"]
            
            self.save_character_locks()
            
            print(f"✅ 백업에서 복원 완료: {Path(backup_path).name}")
            return True
            
        except Exception as e:
            print(f"❌ 백업 복원 실패: {e}")
            return False
    
    def end_adventure_session(self):
        """모험 세션 종료 및 캐릭터 잠금 해제"""
        if self.player_character:
            self.unlock_character(self.player_character)
        
        for companion in self.ai_companions:
            if companion.get("original_data"):
                self.unlock_character(companion["original_data"])
        
        # 백업 정리는 유지 (응급상황 대비)
        print(f"🏁 모험 세션 '{self.current_adventure_id}' 종료")
        self.current_adventure_id = None
    
    def load_character_presets(self):
        """기존 캐릭터 프리셋 로드"""
        try:
            with open("character_presets.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.character_presets = data.get("character_presets", {})
            self.party_presets = data.get("party_presets", {})
            
            print(f"📂 캐릭터 프리셋 {len(self.character_presets)}개 로드 완료")
            print(f"📂 파티 프리셋 {len(self.party_presets)}개 로드 완료")
            
        except FileNotFoundError:
            print("⚠️ character_presets.json 파일을 찾을 수 없습니다.")
            print("💡 게임을 실행하여 캐릭터를 생성한 후 다시 시도하세요.")
        except Exception as e:
            print(f"❌ 캐릭터 프리셋 로드 실패: {e}")
    
    def create_player_character(self):
        """플레이어 캐릭터 생성 또는 선택"""
        print("\n" + "="*60)
        print("👤 플레이어 캐릭터 설정")
        print("="*60)
        
        print("1. 📁 기존 캐릭터에서 선택")
        print("2. 🆕 새 캐릭터 생성 안내")
        print("3. 🤖 AI가 추천하는 캐릭터 (랜덤)")
        print("0. 🔙 메인 메뉴로 돌아가기")
        
        while True:
            choice = safe_input("\n선택하세요 (0-3): ", 2).strip()
            
            if choice == "0":
                print("🔙 메인 메뉴로 돌아갑니다.")
                return None
            elif choice == "1":
                result = self._select_existing_character()
                if result:
                    return result
                # None이면 다시 메뉴로
            elif choice == "2":
                self._create_new_character()
                return None  # 메뉴로 돌아가기
            elif choice == "3":
                result = self._ai_recommend_character()
                if result:
                    return result
            else:
                print("❌ 0-3 사이의 숫자를 입력해주세요.")
    
    def _ai_recommend_character(self):
        """AI가 추천하는 캐릭터 (랜덤 선택, 중복 사용 방지)"""
        if not self.character_presets:
            print("❌ 저장된 캐릭터가 없습니다.")
            print("💡 먼저 캐릭터를 생성해주세요.")
            return None
        
        print("\n🤖 AI가 당신에게 어울리는 캐릭터를 추천합니다...")
        print("🎲 분석 중...")
        
        import time
        time.sleep(1)  # 연출용 딜레이
        
        # 사용 가능한 캐릭터들만 필터링
        available_characters = []
        for key, char in self.character_presets.items():
            is_locked, _ = self.is_character_locked(char)
            if not is_locked:
                available_characters.append((key, char))
        
        if not available_characters:
            print("\n❌ 사용 가능한 캐릭터가 없습니다.")
            print("💡 모든 캐릭터가 다른 모험에서 사용 중입니다.")
            print("⏰ 다른 모험을 종료하거나 새 캐릭터를 생성해주세요.")
            input("\nEnter를 눌러 계속...")
            return None
        
        # 사용 가능한 캐릭터 중에서 랜덤 선택
        selected_key, selected_char = random.choice(available_characters)
        
        print(f"\n✨ AI 추천 결과:")
        print(f"🎭 {selected_char['name']} ({selected_char['character_class']}) Lv.{selected_char['level']}")
        
        # 스탯 정보 표시 (우리 게임 스탯 시스템에 맞게)
        stats = selected_char['stats']
        hp = f"{stats.get('current_hp', stats.get('max_hp', '?'))}/{stats.get('max_hp', '?')}"
        mp = f"{stats.get('current_mp', stats.get('max_mp', '?'))}/{stats.get('max_mp', '?')}"
        print(f"📊 HP:{hp} | MP:{mp}")
        print(f"⚔️ 물공:{stats.get('p_atk', stats.get('physical_attack', '?'))} | 🔮 마공:{stats.get('m_atk', stats.get('magic_attack', '?'))} | ⚡ 속도:{stats.get('speed', '?')}")
        print(f"🛡️ 물방:{stats.get('p_def', stats.get('physical_defense', '?'))} | 🔮 마방:{stats.get('m_def', stats.get('magic_defense', '?'))}")
        
        # 추천 이유 생성
        reasons = [
            "균형 잡힌 능력치로 초보자에게 적합합니다",
            "강력한 공격력으로 빠른 전투가 가능합니다", 
            "다양한 스킬로 여러 상황에 대응할 수 있습니다",
            "높은 생존력으로 안정적인 플레이가 가능합니다",
            "독특한 특성으로 재미있는 게임 경험을 제공합니다"
        ]
        
        print(f"\n💡 추천 이유: {random.choice(reasons)}")
        print("⚠️ 이 캐릭터는 모험 종료까지 다른 세이브에서 사용할 수 없습니다.")
        
        # 선택 확인
        choice = safe_input("\n이 캐릭터를 사용하시겠습니까? (Y/N): ", 5).strip().lower()
        
        if choice in ['y', 'yes', '예', 'ㅇ']:
            # 모험 세션 생성 (없는 경우)
            if not self.current_adventure_id:
                self.create_adventure_session()
            
            # 캐릭터 잠금
            self.lock_character(selected_char, self.current_adventure_id)
            
            # AI 형식으로 변환
            self.player_character = self._convert_to_ai_format(selected_char, is_player=True)
            
            print(f"\n✅ {selected_char['name']} 선택 완료!")
            print(f"🔒 캐릭터가 모험 '{self.current_adventure_id}'에 잠금 설정되었습니다.")
            self._display_character_info(self.player_character)
            
            # 응급 백업 생성
            self.backup_adventure_state()
            
            return self.player_character
        else:
            print("❌ AI 추천을 거부했습니다.")
            return None
    
    def _select_existing_character(self):
        """기존 캐릭터에서 선택 (중복 사용 방지)"""
        if not self.character_presets:
            print("❌ 저장된 캐릭터가 없습니다.")
            print("💡 먼저 python main.py를 실행하여 캐릭터를 생성해주세요.")
            input("\nEnter를 눌러 계속...")
            return None
        
        print("\n� 저장된 캐릭터 목록:")
        print("="*60)
        
        characters = list(self.character_presets.items())
        available_characters = []
        locked_characters = []
        
        # 캐릭터 상태 분류
        for i, (key, char) in enumerate(characters, 1):
            is_locked, adventure_id = self.is_character_locked(char)
            
            if is_locked:
                locked_characters.append((i, key, char, adventure_id))
            else:
                available_characters.append((i, key, char))
        
        # 사용 가능한 캐릭터 표시
        if available_characters:
            print("✅ 사용 가능한 캐릭터:")
            for i, key, char in available_characters:
                name = char['name']
                level = char['level']
                job = char['character_class']
                
                print(f"{i}. 🎭 {name} (Lv.{level} {job})")
                
                # 스탯 정보 (우리 게임 스탯 시스템에 맞게)
                stats = char['stats']
                hp = f"{stats.get('current_hp', stats.get('max_hp', '?'))}/{stats.get('max_hp', '?')}"
                mp = f"{stats.get('current_mp', stats.get('max_mp', '?'))}/{stats.get('max_mp', '?')}"
                
                print(f"   📊 HP:{hp} | MP:{mp}")
                print(f"   ⚔️ 물공:{stats.get('p_atk', stats.get('physical_attack', '?'))} | 🔮 마공:{stats.get('m_atk', stats.get('magic_attack', '?'))} | ⚡ 속도:{stats.get('speed', '?')}")
                print(f"   🛡️ 물방:{stats.get('p_def', stats.get('physical_defense', '?'))} | 🔮 마방:{stats.get('m_def', stats.get('magic_defense', '?'))}")
                
                # 특성 정보 (있는 경우)
                if char.get('traits'):
                    trait_names = [trait.get('name', str(trait)) for trait in char['traits'][:3]]  # 처음 3개만
                    print(f"   ✨ 특성: {', '.join(trait_names)}")
                
                print()
        
        # 잠긴 캐릭터 표시
        if locked_characters:
            print("🔒 다른 모험에서 사용 중인 캐릭터:")
            for i, key, char, adventure_id in locked_characters:
                print(f"{i}. ❌ {char['name']} (Lv.{char['level']} {char['character_class']}) - 모험 '{adventure_id}'에서 사용 중")
            print()
        
        if not available_characters:
            print("❌ 사용 가능한 캐릭터가 없습니다.")
            print("💡 모든 캐릭터가 다른 모험에서 사용 중입니다.")
            print("⏰ 다른 모험을 종료하거나 새 캐릭터를 생성해주세요.")
            input("\nEnter를 눌러 계속...")
            return None
        
        print("0. 🔙 뒤로가기")
        
        while True:
            try:
                choice = input(f"\n캐릭터 선택 (0 또는 사용 가능한 번호): ").strip()
                
                if choice == "0":
                    print("🔙 캐릭터 선택을 취소합니다.")
                    return None
                
                choice_num = int(choice)
                
                # 사용 가능한 캐릭터에서 찾기
                selected_char = None
                for i, key, char in available_characters:
                    if i == choice_num:
                        selected_char = (key, char)
                        break
                
                if selected_char:
                    selected_key, selected_char_data = selected_char
                    
                    # 선택 확인
                    print(f"\n🎯 '{selected_char_data['name']}' ({selected_char_data['character_class']})을(를) 선택하시겠습니까?")
                    print("⚠️ 이 캐릭터는 모험 종료까지 다른 세이브에서 사용할 수 없습니다.")
                    confirm = safe_input("Y/N: ", 5).strip().lower()
                    
                    if confirm in ['y', 'yes', '예', 'ㅇ']:
                        # 모험 세션 생성 (없는 경우)
                        if not self.current_adventure_id:
                            self.create_adventure_session()
                        
                        # 캐릭터 잠금
                        self.lock_character(selected_char_data, self.current_adventure_id)
                        
                        # AI 형식으로 변환
                        self.player_character = self._convert_to_ai_format(selected_char_data, is_player=True)
                        
                        print(f"\n✅ {selected_char_data['name']} ({selected_char_data['character_class']}) 선택 완료!")
                        print(f"🔒 캐릭터가 모험 '{self.current_adventure_id}'에 잠금 설정되었습니다.")
                        self._display_character_info(self.player_character)
                        
                        # 응급 백업 생성
                        self.backup_adventure_state()
                        
                        return self.player_character
                    else:
                        print("❌ 선택을 취소했습니다.")
                        continue
                else:
                    # 잠긴 캐릭터 선택 시 경고
                    for i, key, char, adventure_id in locked_characters:
                        if i == choice_num:
                            print(f"❌ '{char['name']}'은(는) 모험 '{adventure_id}'에서 사용 중입니다.")
                            print("💡 해당 모험을 먼저 종료해주세요.")
                            break
                    else:
                        print(f"❌ 잘못된 선택입니다. 사용 가능한 번호를 입력해주세요.")
                        
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
    
    def _create_new_character(self):
        """새 캐릭터 생성 안내"""
        print("\n💡 새 캐릭터 생성을 위해 게임 런처를 사용하세요:")
        print("1. python main.py 실행")
        print("2. 캐릭터 생성 메뉴에서 캐릭터 생성")
        print("3. 생성 후 이 프로그램으로 돌아와서 다시 시도")
        
        input("\nEnter를 눌러 계속...")
    
    def _convert_to_ai_format(self, character_data: Dict, is_player: bool = False) -> Dict:
        """기존 캐릭터 데이터를 AI 시스템 형식으로 변환"""
        ai_character = {
            "name": character_data["name"],
            "character_class": character_data["character_class"],
            "level": character_data["level"],
            "stats": character_data["stats"].copy(),
            "current_status": character_data["current_status"].copy(),
            "traits": character_data.get("traits", []).copy(),
            "equipment": character_data.get("equipment", {}).copy(),
            "is_player": is_player,
            "original_data": character_data.copy()
        }
        
        # AI 전용 속성 추가 (플레이어가 아닌 경우)
        if not is_player:
            personality = random.choice(list(self.ai_personalities.keys()))
            ai_character.update({
                "ai_personality": personality,
                "ai_traits": self.ai_personalities[personality].copy(),
                "ai_combat_preferences": self._generate_combat_preferences(character_data["character_class"], personality),
                "ai_relationship": {
                    "loyalty": random.randint(70, 95),
                    "trust": random.randint(60, 90),
                    "friendship": random.randint(50, 80)
                }
            })
        
        return ai_character
    
    def _generate_combat_preferences(self, job_class: str, personality: str) -> Dict:
        """직업과 성격에 따른 AI 전투 선호도 생성"""
        base_preferences = {
            "prefer_offensive": 0.5,
            "prefer_defensive": 0.5,
            "prefer_support": 0.5,
            "prefer_items": 0.3,
            "prefer_skills": 0.7,
            "team_coordination": 0.6
        }
        
        # 직업별 조정 (27개 직업 완전체)
        job_modifiers = {
            # 전투 직업군 (8개)
            "전사": {"prefer_defensive": 0.3, "team_coordination": 0.2},
            "아크메이지": {"prefer_offensive": 0.4, "prefer_skills": 0.3},
            "궁수": {"prefer_offensive": 0.2, "team_coordination": 0.2},
            "도적": {"prefer_offensive": 0.3, "team_coordination": -0.2},
            "성기사": {"prefer_support": 0.3, "team_coordination": 0.3, "prefer_defensive": 0.2},
            "암흑기사": {"prefer_offensive": 0.4, "prefer_support": -0.2, "team_coordination": -0.1},
            "몽크": {"prefer_offensive": 0.3, "team_coordination": 0.1, "prefer_skills": 0.2},
            "바드": {"prefer_support": 0.4, "team_coordination": 0.4, "prefer_skills": 0.2},
            
            # 마법 직업군 (10개)
            "네크로맨서": {"prefer_offensive": 0.3, "prefer_support": 0.2, "team_coordination": -0.2},
            "용기사": {"prefer_offensive": 0.4, "prefer_defensive": 0.2, "team_coordination": 0.1},
            "검성": {"prefer_offensive": 0.5, "prefer_skills": 0.3, "team_coordination": 0.0},
            "정령술사": {"prefer_offensive": 0.3, "prefer_skills": 0.4, "team_coordination": 0.1},
            "시간술사": {"prefer_skills": 0.5, "prefer_support": 0.3, "team_coordination": 0.2},
            "연금술사": {"prefer_items": 0.4, "prefer_support": 0.3, "team_coordination": 0.1},
            "차원술사": {"prefer_offensive": 0.4, "prefer_skills": 0.4, "team_coordination": -0.1},
            "마검사": {"prefer_offensive": 0.4, "prefer_skills": 0.3, "team_coordination": 0.0},
            "기계공학자": {"prefer_skills": 0.3, "prefer_items": 0.2, "team_coordination": 0.1},
            "무당": {"prefer_support": 0.3, "prefer_skills": 0.3, "team_coordination": 0.2},
            
            # 특수 직업군 (10개)
            "암살자": {"prefer_offensive": 0.5, "team_coordination": -0.3, "prefer_skills": 0.2},
            "해적": {"prefer_offensive": 0.3, "team_coordination": -0.1, "prefer_items": 0.2},
            "사무라이": {"prefer_offensive": 0.4, "prefer_defensive": 0.2, "team_coordination": 0.1},
            "드루이드": {"prefer_support": 0.4, "prefer_skills": 0.3, "team_coordination": 0.2},
            "철학자": {"prefer_skills": 0.5, "prefer_support": 0.2, "team_coordination": 0.3},
            "검투사": {"prefer_offensive": 0.5, "prefer_defensive": 0.1, "team_coordination": -0.2},
            "기사": {"prefer_defensive": 0.4, "team_coordination": 0.3, "prefer_support": 0.2},
            "신관": {"prefer_support": 0.5, "prefer_defensive": 0.3, "team_coordination": 0.4},
            "광전사": {"prefer_offensive": 0.6, "prefer_defensive": -0.3, "team_coordination": -0.2}
        }
        
        # 성격별 조정
        personality_modifiers = {
            "용감한": {"prefer_offensive": 0.3, "prefer_defensive": -0.2},
            "신중한": {"prefer_defensive": 0.2, "prefer_offensive": -0.1},
            "지원형": {"prefer_support": 0.4, "team_coordination": 0.3},
            "독립적": {"team_coordination": -0.3, "prefer_items": 0.2},
            "적응형": {"prefer_skills": 0.2}
        }
        
        # 조정값 적용
        for key, value in base_preferences.items():
            if job_class in job_modifiers:
                value += job_modifiers[job_class].get(key, 0)
            if personality in personality_modifiers:
                value += personality_modifiers[personality].get(key, 0)
            
            # 0~1 범위로 제한
            base_preferences[key] = max(0.0, min(1.0, value))
        
        return base_preferences
    
    def create_ai_companions(self):
        """AI 동료들 자동 생성"""
        if not self.player_character:
            print("❌ 먼저 플레이어 캐릭터를 설정해주세요.")
            return
        
        print(f"\n🤖 AI 동료 {self.party_size - 1}명을 생성합니다...")
        
        # 플레이어를 제외한 캐릭터들에서 선택
        available_characters = []
        player_name = self.player_character["name"]
        
        for key, char in self.character_presets.items():
            if char["name"] != player_name:
                available_characters.append(char)
        
        if len(available_characters) < self.party_size - 1:
            print(f"⚠️ 사용 가능한 캐릭터가 {len(available_characters)}명뿐입니다.")
            print(f"💡 더 많은 캐릭터를 생성하려면 게임에서 캐릭터를 생성해주세요.")
            self.party_size = len(available_characters) + 1
        
        # 랜덤으로 AI 동료 선택
        selected_companions = random.sample(available_characters, min(self.party_size - 1, len(available_characters)))
        
        self.ai_companions = []
        for i, char in enumerate(selected_companions):
            if ADVANCED_AI_AVAILABLE:
                try:
                    # 고급 AI 시스템 적용
                    advanced_ai = AdvancedAICompanion(
                        character_name=char["name"],
                        character_class=char["character_class"],
                        gender=random.choice(['남성', '여성', '중성'])
                    )
                    
                    # 기존 캐릭터 데이터에 고급 AI 속성 추가
                    ai_companion = self._convert_to_ai_format(char, is_player=False)
                    ai_companion.update({
                        "advanced_ai": advanced_ai,
                        "personality_type": advanced_ai.personality_type,
                        "personality_traits": advanced_ai.personality_traits,
                        "class_personality": advanced_ai.class_personality,
                        "game_intelligence": advanced_ai.game_intelligence
                    })
                    
                    self.ai_companions.append(ai_companion)
                    
                    print(f"🧠 {char['name']} ({char['character_class']}) - {advanced_ai.personality_type.value}")
                    print(f"   지능: 전투 {advanced_ai.game_intelligence['combat_iq']:.2f} | 전략 {advanced_ai.game_intelligence['strategic_thinking']:.2f}")
                    print(f"   특성: 적응력 {advanced_ai.game_intelligence['adaptability']:.2f} | 학습속도 {advanced_ai.game_intelligence['learning_speed']:.2f}")
                    
                except Exception as e:
                    print(f"⚠️ 고급 AI 생성 실패, 기본 AI 사용: {e}")
                    ai_companion = self._convert_to_ai_format(char, is_player=False)
                    self.ai_companions.append(ai_companion)
                    print(f"🤖 {char['name']} ({char['character_class']}) - {ai_companion['ai_personality']} 성격")
            else:
                ai_companion = self._convert_to_ai_format(char, is_player=False)
                self.ai_companions.append(ai_companion)
                
                personality = ai_companion["ai_personality"]
                print(f"🤖 {char['name']} ({char['character_class']}) - {personality} 성격")
                print(f"   {self.ai_personalities[personality]['description']}")
        
        print(f"\n🎉 AI 파티 구성 완료! 총 {len(self.ai_companions) + 1}명")
        if ADVANCED_AI_AVAILABLE:
            print("🧠 고급 AI 시스템 활성화 - 지능적 대화와 고급 전투 AI")
    
    def create_preset_party(self):
        """기존 파티 프리셋 사용"""
        if not self.party_presets:
            print("❌ 저장된 파티 프리셋이 없습니다.")
            return
        
        print(f"\n파티 프리셋 목록:")
        print("-" * 50)
        
        presets = list(self.party_presets.items())
        for i, (key, party) in enumerate(presets, 1):
            print(f"{i}. {key} ({party['party_size']}명)")
            print(f"   {party.get('description', '설명 없음')}")
            print()
        
        while True:
            try:
                choice = int(input(f"파티 선택 (1-{len(presets)}): ")) - 1
                if 0 <= choice < len(presets):
                    selected_key, selected_party = presets[choice]
                    self._load_preset_party(selected_party)
                    break
                else:
                    print(f"❌ 1-{len(presets)} 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
    
    def _load_preset_party(self, party_preset: Dict):
        """파티 프리셋 로드"""
        character_keys = party_preset["characters"]
        
        # 첫 번째 캐릭터를 플레이어로 설정
        if character_keys:
            first_char_key = character_keys[0]
            if first_char_key in self.character_presets:
                first_char = self.character_presets[first_char_key]
                self.player_character = self._convert_to_ai_format(first_char, is_player=True)
                print(f"👤 플레이어: {first_char['name']} ({first_char['character_class']})")
        
        # 나머지를 AI 동료로 설정
        self.ai_companions = []
        for char_key in character_keys[1:]:
            if char_key in self.character_presets:
                char = self.character_presets[char_key]
                ai_companion = self._convert_to_ai_format(char, is_player=False)
                self.ai_companions.append(ai_companion)
                
                personality = ai_companion["ai_personality"]
                print(f"🤖 AI 동료: {char['name']} ({char['character_class']}) - {personality}")
        
        print(f"\n✅ 파티 프리셋 '{party_preset.get('description', '불명')}' 로드 완료!")
    
    def show_party_status(self):
        """파티 상태 표시"""
        print(f"\n👥 현재 파티 상태:")
        print("=" * 60)
        
        if self.player_character:
            print("\n👤 플레이어:")
            self._display_character_info(self.player_character)
        
        if self.ai_companions:
            print(f"\n🤖 AI 동료들:")
            for companion in self.ai_companions:
                self._display_character_info(companion)
        
        if not self.player_character and not self.ai_companions:
            print("❌ 파티가 구성되지 않았습니다.")
    
    def _display_character_info(self, character: Dict[str, Any]):
        """캐릭터 정보 표시"""
        print(f"\n📋 {character['name']} ({character['character_class']}) - Lv.{character['level']}")
        
        stats = character['stats']
        status = character['current_status']
        
        print(f"   ❤️  HP: {status['hp']}/{stats['max_hp']}")
        print(f"   💙 MP: {status['mp']}/{stats['max_mp']}")
        print(f"   ⚡ BRV: {status['brave_points']}")
        print(f"   🗡️  물공: {stats['physical_attack']} | 🔮 마공: {stats['magic_attack']}")
        print(f"   🛡️  물방: {stats['physical_defense']} | 🔰 마방: {stats['magic_defense']}")
        print(f"   💨 속도: {stats['speed']}")
        
        if not character['is_player']:
            if 'advanced_ai' in character and ADVANCED_AI_AVAILABLE:
                # 고급 AI 정보 표시
                ai = character['advanced_ai']
                print(f"   🧠 성격 유형: {ai.personality_type.value}")
                print(f"   ⚔️ 전투 지능: {ai.game_intelligence['combat_iq']:.2f}")
                print(f"   🗺️  길찾기: {ai.game_intelligence['pathfinding_skill']:.2f}")
                print(f"   📚 학습 속도: {ai.game_intelligence['learning_speed']:.2f}")
                
                # 주요 성격 특성 3개 표시
                if 'personality_traits' in character:
                    top_traits = sorted(character['personality_traits'].items(), 
                                      key=lambda x: x[1], reverse=True)[:3]
                    trait_names = [f"{trait}({value:.1f})" for trait, value in top_traits]
                    print(f"   🎭 주요 특성: {', '.join(trait_names)}")
                    
                # 관계도 표시
                if 'relationships' in character:
                    rel = character['relationships']
                    print(f"   💕 관계도: 충성{rel['loyalty']:.1f} | 신뢰{rel['trust']:.1f} | 친밀{rel['friendship']:.1f}")
            else:
                # 기본 AI 정보 표시
                print(f"   🎭 성격: {character['ai_personality']}")
                if 'ai_relationship' in character:
                    rel = character['ai_relationship']
                    print(f"   💕 관계도: 충성{rel['loyalty']} | 신뢰{rel['trust']} | 친밀{rel['friendship']}")
            print(f"      {self.ai_personalities[character['ai_personality']]['description']}")
            
            relationship = character['ai_relationship']
            print(f"   💝 관계도: 충성도 {relationship['loyalty']}% | 신뢰도 {relationship['trust']}% | 친밀도 {relationship['friendship']}%")
    
    def start_training_mode(self):
        """훈련 모드 시작"""
        if not self.player_character:
            print("❌ 먼저 플레이어 캐릭터를 설정해주세요.")
            return
        
        print(f"\n🎯 {self.player_character['name']}의 훈련 모드")
        print("="*50)
        
        training_options = [
            "개인 스킬 훈련",
            "파티 협력 훈련", 
            "전투 시뮬레이션",
            "AI 동료와 소통 훈련",
            "AI 성격 조정"
        ]
        
        for i, option in enumerate(training_options, 1):
            print(f"{i}. {option}")
        
        try:
            choice = int(input("\n훈련 모드 선택 (1-5): ")) - 1
            if 0 <= choice < len(training_options):
                selected_training = training_options[choice]
                self._execute_training(selected_training)
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _execute_training(self, training_type: str):
        """훈련 실행"""
        print(f"\n🏃‍♂️ {training_type} 시작!")
        
        if training_type == "개인 스킬 훈련":
            self._personal_skill_training()
        elif training_type == "파티 협력 훈련":
            self._party_cooperation_training()
        elif training_type == "전투 시뮬레이션":
            self._combat_simulation()
        elif training_type == "AI 동료와 소통 훈련":
            self._ai_communication_training()
        elif training_type == "AI 성격 조정":
            self._ai_personality_adjustment()
    
    def _personal_skill_training(self):
        """개인 스킬 훈련"""
        print("💪 개인 스킬을 연마하고 있습니다...")
        
        # 스탯 증가 시뮬레이션
        stat_names = ["physical_attack", "magic_attack", "physical_defense", "magic_defense", "speed"]
        improved_stat = random.choice(stat_names)
        improvement = random.randint(1, 3)
        
        self.player_character['stats'][improved_stat] += improvement
        
        stat_display = {
            "physical_attack": "물리 공격력",
            "magic_attack": "마법 공격력", 
            "physical_defense": "물리 방어력",
            "magic_defense": "마법 방어력",
            "speed": "속도"
        }
        
        print(f"✅ {stat_display[improved_stat]}이 {improvement} 포인트 증가했습니다!")
    
    def _party_cooperation_training(self):
        """파티 협력 훈련"""
        if not self.ai_companions:
            print("❌ AI 동료가 없습니다.")
            return
        
        print("🤝 AI 동료들과 협력 훈련을 하고 있습니다...")
        
        # AI 동료들의 관계도 향상
        for companion in self.ai_companions:
            relationship = companion['ai_relationship']
            
            # 관계도 증가
            relationship['trust'] = min(100, relationship['trust'] + random.randint(2, 5))
            relationship['friendship'] = min(100, relationship['friendship'] + random.randint(1, 4))
            
            responses = [
                f"{companion['name']}: 좋은 협력이었습니다!",
                f"{companion['name']}: 더 잘 이해하게 되었어요!",
                f"{companion['name']}: 팀워크가 향상된 것 같네요!",
                f"{companion['name']}: 함께 훈련하니 더 강해진 느낌입니다!"
            ]
            print(f"   {random.choice(responses)}")
        
        print("✅ 파티 협력도가 향상되었습니다!")
    
    def _combat_simulation(self):
        """전투 시뮬레이션"""
        print("⚔️ 가상 적과 전투 훈련 중...")
        
        # 경험치 및 BRV 포인트 증가
        exp_gain = random.randint(10, 30)
        brv_gain = random.randint(20, 50)
        
        self.player_character['current_status']['experience'] += exp_gain
        self.player_character['current_status']['brave_points'] += brv_gain
        
        print(f"✅ 전투 경험치 {exp_gain} 획득!")
        print(f"✅ BRV 포인트 {brv_gain} 획득!")
        
        # AI 동료들도 경험치 획득
        for companion in self.ai_companions:
            companion['current_status']['experience'] += exp_gain // 2
            companion['current_status']['brave_points'] += brv_gain // 2
            print(f"   {companion['name']}: 경험치 {exp_gain // 2} 획득!")
    
    def _ai_communication_training(self):
        """AI 동료와 소통 훈련"""
        if not self.ai_companions:
            print("❌ AI 동료가 없습니다.")
            return
        
        print("💬 AI 동료들과 의사소통 훈련 중...")
        
        for companion in self.ai_companions:
            personality = companion['ai_personality']
            relationship = companion['ai_relationship']
            
            # 성격에 따른 대화
            personality_responses = {
                "용감한": [
                    "전투에서 더 적극적으로 나서겠습니다!",
                    "위험한 상황이 오면 제가 앞장서겠어요!",
                    "용기를 내서 함께 싸워봐요!"
                ],
                "신중한": [
                    "상황을 더 꼼꼼히 분석해보겠습니다.",
                    "신중하게 계획을 세워서 행동하죠.",
                    "위험 요소를 미리 파악해두겠어요."
                ],
                "지원형": [
                    "언제든 도움이 필요하면 말씀하세요!",
                    "팀원들을 더 잘 보살피겠습니다.",
                    "모두가 안전할 수 있도록 지원하겠어요."
                ],
                "독립적": [
                    "제 방식대로 전투하겠습니다.",
                    "각자 맡은 역할에 집중하죠.",
                    "독립적으로 행동하되 협력은 하겠어요."
                ],
                "적응형": [
                    "상황에 맞춰 유연하게 대응하겠습니다!",
                    "필요에 따라 역할을 바꿔가며 도와드릴게요.",
                    "어떤 상황이든 적응해서 최선을 다하겠어요!"
                ]
            }
            
            response = random.choice(personality_responses[personality])
            print(f"   {companion['name']} ({personality}): {response}")
            
            # 친밀도 증가
            relationship['friendship'] = min(100, relationship['friendship'] + random.randint(3, 7))
        
        print("✅ AI 동료들과의 친밀도가 증가했습니다!")
    
    def _ai_personality_adjustment(self):
        """AI 성격 조정"""
        if not self.ai_companions:
            print("❌ AI 동료가 없습니다.")
            return
        
        print("\n🎭 AI 동료의 성격을 조정할 수 있습니다:")
        
        for i, companion in enumerate(self.ai_companions, 1):
            current_personality = companion['ai_personality']
            print(f"{i}. {companion['name']} (현재: {current_personality})")
        
        try:
            choice = int(input(f"\n조정할 AI 선택 (1-{len(self.ai_companions)}): ")) - 1
            if 0 <= choice < len(self.ai_companions):
                selected_companion = self.ai_companions[choice]
                self._adjust_companion_personality(selected_companion)
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _adjust_companion_personality(self, companion: Dict):
        """동료의 성격 조정"""
        print(f"\n{companion['name']}의 성격 조정:")
        
        personalities = list(self.ai_personalities.keys())
        for i, personality in enumerate(personalities, 1):
            desc = self.ai_personalities[personality]['description']
            current = " (현재)" if personality == companion['ai_personality'] else ""
            print(f"{i}. {personality}{current}")
            print(f"   {desc}")
            print()
        
        try:
            choice = int(input(f"새로운 성격 선택 (1-{len(personalities)}): ")) - 1
            if 0 <= choice < len(personalities):
                new_personality = personalities[choice]
                old_personality = companion['ai_personality']
                
                # 성격 변경
                companion['ai_personality'] = new_personality
                companion['ai_traits'] = self.ai_personalities[new_personality].copy()
                companion['ai_combat_preferences'] = self._generate_combat_preferences(
                    companion['character_class'], new_personality
                )
                
                print(f"\n✅ {companion['name']}의 성격이 '{old_personality}'에서 '{new_personality}'로 변경되었습니다!")
                print(f"💭 {companion['name']}: {self.ai_personalities[new_personality]['description']}")
                
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def start_simple_adventure(self):
        """간단한 모험 시작"""
        if not self.player_character or not self.ai_companions:
            print("❌ 먼저 파티를 구성해주세요.")
            return
        
        print(f"\n🗺️ {self.player_character['name']}의 모험 시작!")
        print("="*60)
        
        adventure_scenarios = [
            {
                "name": "숲속의 고블린 소굴",
                "description": "고블린들이 마을을 위협하고 있습니다",
                "difficulty": "쉬움",
                "enemies": ["고블린 전사", "고블린 궁수", "고블린 우두머리"],
                "rewards": {"experience": 50, "brave_points": 100, "items": ["회복 포션", "마나 포션"]}
            },
            {
                "name": "폐허가 된 마법탑",
                "description": "고대 마법사의 탑에 위험한 마법 생물들이 살고 있습니다",
                "difficulty": "보통",
                "enemies": ["스켈레톤 마법사", "가고일", "리치"],
                "rewards": {"experience": 100, "brave_points": 200, "items": ["마법 반지", "지혜의 물약"]}
            },
            {
                "name": "용의 둥지",
                "description": "전설의 드래곤이 잠들어 있는 둥지입니다",
                "difficulty": "어려움",
                "enemies": ["드래곤 새끼", "드래곤 가디언", "고대 드래곤"],
                "rewards": {"experience": 300, "brave_points": 500, "items": ["용의 비늘", "전설의 무기"]}
            }
        ]
        
        print("모험지를 선택하세요:")
        for i, scenario in enumerate(adventure_scenarios, 1):
            print(f"{i}. {scenario['name']} ({scenario['difficulty']})")
            print(f"   {scenario['description']}")
            print(f"   예상 적: {', '.join(scenario['enemies'])}")
            print()
        
        try:
            choice = int(input("모험지 선택 (1-3): ")) - 1
            if 0 <= choice < len(adventure_scenarios):
                selected_scenario = adventure_scenarios[choice]
                self._execute_adventure(selected_scenario)
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _execute_adventure(self, scenario: Dict[str, Any]):
        """모험 실행 (전용 세이브 시스템 연동)"""
        print(f"\n🗺️ {scenario['name']} 진입!")
        print(f"📖 {scenario['description']}")
        print("-" * 60)
        
        # 모험 세션 생성 (없는 경우)
        if not self.current_adventure_id:
            self.create_adventure_session()
            print(f"🎮 새 모험 세션 생성: {self.current_adventure_id}")
        
        # 3단계: 모험 전 특성/패시브 선택 시스템 실행
        try:
            print(f"\n🌟 모험 시작 전 파티 준비 단계")
            print("-" * 60)
            
            # 게임 캐릭터 객체로 변환
            game_characters = []
            
            # 플레이어 캐릭터 변환
            if self.player_character:
                try:
                    if SYSTEMS_AVAILABLE:
                        from game.character import Character
                        player_char = Character(
                            name=self.player_character['name'],
                            character_class=self.player_character['character_class']
                        )
                        player_char.is_player = True
                        game_characters.append(player_char)
                    else:
                        # 시스템 비활성화 시 간단한 객체
                        class SimpleCharacter:
                            def __init__(self, name, character_class):
                                self.name = name
                                self.character_class = character_class
                                self.is_player = True
                        
                        player_char = SimpleCharacter(
                            self.player_character['name'],
                            self.player_character['character_class']
                        )
                        game_characters.append(player_char)
                        
                except Exception as e:
                    print(f"⚠️ 플레이어 캐릭터 변환 오류: {e}")
            
            # AI 동료 캐릭터 변환
            for companion_data in self.ai_companions:
                try:
                    if SYSTEMS_AVAILABLE:
                        from game.character import Character
                        ai_char = Character(
                            name=companion_data['name'],
                            character_class=companion_data['character_class']
                        )
                        ai_char.is_player = False
                        ai_char.ai_personality = companion_data['ai_personality']
                        game_characters.append(ai_char)
                    else:
                        # 시스템 비활성화 시 간단한 객체
                        class SimpleCharacter:
                            def __init__(self, name, character_class, personality):
                                self.name = name
                                self.character_class = character_class
                                self.is_player = False
                                self.ai_personality = personality
                        
                        ai_char = SimpleCharacter(
                            companion_data['name'],
                            companion_data['character_class'],
                            companion_data['ai_personality']
                        )
                        game_characters.append(ai_char)
                        
                except Exception as e:
                    print(f"⚠️ AI 동료 {companion_data['name']} 변환 오류: {e}")
            
            # 특성 선택 시스템 실행
            print(f"📝 총 {len(game_characters)}명의 캐릭터가 모험에 참여합니다.")
            self.setup_traits_and_passives(game_characters)
            
        except Exception as e:
            print(f"❌ 특성 선택 시스템 오류: {e}")
            print("⚠️ 기본 설정으로 모험을 시작합니다.")
        
        # 모험 시작 전 전용 세이브 생성
        print("\n💾 전용 멀티플레이어 세이브 생성 중...")
        
        save_data = {
            "scenario": scenario,
            "player_character": self.player_character,
            "ai_companions": self.ai_companions,
            "start_time": datetime.now().isoformat(),
            "adventure_phase": "starting"
        }
        
        try:
            save_path = self.create_exclusive_save(save_data)
            print(f"✅ 전용 세이브 생성 완료: {Path(save_path).name}")
        except Exception as e:
            print(f"⚠️ 전용 세이브 생성 실패: {e}")
            print("❓ 계속 진행하시겠습니까? (Y/N): ")
            if input().strip().lower() not in ['y', 'yes', '예', 'ㅇ']:
                print("🔙 모험을 취소합니다.")
                return
        
        # 모험 시작 전 응급 백업
        print("🆘 응급 백업 생성 중...")
        self.backup_adventure_state()
        
        # AI 동료들의 반응 (성격에 따라)
        for companion in self.ai_companions:
            personality = companion['ai_personality']
            
            personality_reactions = {
                "용감한": [
                    f"{companion['name']}: 좋아! 정면승부다!",
                    f"{companion['name']}: 무서울 게 없어요!",
                    f"{companion['name']}: 앞장서겠습니다!"
                ],
                "신중한": [
                    f"{companion['name']}: 조심스럽게 진행합시다.",
                    f"{companion['name']}: 계획을 세워야겠어요.",
                    f"{companion['name']}: 위험 요소를 체크해봅시다."
                ],
                "지원형": [
                    f"{companion['name']}: 제가 도울게요!",
                    f"{companion['name']}: 모두 안전하게 가요!",
                    f"{companion['name']}: 언제든 지원하겠습니다!"
                ],
                "독립적": [
                    f"{companion['name']}: 각자 맡은 일을 하죠.",
                    f"{companion['name']}: 제 방식대로 하겠어요.",
                    f"{companion['name']}: 준비됐습니다."
                ],
                "적응형": [
                    f"{companion['name']}: 상황에 맞춰 행동하겠어요!",
                    f"{companion['name']}: 유연하게 대응해봅시다!",
                    f"{companion['name']}: 어떤 상황이든 괜찮아요!"
                ]
            }
            
            reaction = random.choice(personality_reactions[personality])
            print(reaction)
        
        print("\n⚔️ 전투 시뮬레이션 중...")
        
        # 성공률 계산 (파티 구성과 AI 성격 고려)
        base_success_rate = {
            "쉬움": 0.8,
            "보통": 0.6,
            "어려움": 0.4
        }
        
        success_rate = base_success_rate[scenario['difficulty']]
        
        # AI 동료들의 성격에 따른 보너스
        for companion in self.ai_companions:
            personality = companion['ai_personality']
            relationship = companion['ai_relationship']
            
            # 성격별 보너스
            personality_bonus = {
                "용감한": 0.1,
                "신중한": 0.05,
                "지원형": 0.08,
                "독립적": 0.03,
                "적응형": 0.06
            }
            
            success_rate += personality_bonus[personality]
            
            # 관계도에 따른 보너스
            avg_relationship = (relationship['loyalty'] + relationship['trust'] + relationship['friendship']) / 300
            success_rate += avg_relationship * 0.1
        
        # 최대 0.95로 제한
        success_rate = min(0.95, success_rate)
        
        is_success = random.random() < success_rate
        
        if is_success:
            print("🎉 승리!")
            
            # 보상 지급
            rewards = scenario['rewards']
            
            # 플레이어 보상
            self.player_character['current_status']['experience'] += rewards['experience']
            self.player_character['current_status']['brave_points'] += rewards['brave_points']
            
            print(f"✅ 보상 획득:")
            print(f"   경험치: +{rewards['experience']}")
            print(f"   BRV 포인트: +{rewards['brave_points']}")
            print(f"   아이템: {', '.join(rewards['items'])}")
            
            # AI 동료들 보상
            for companion in self.ai_companions:
                companion['current_status']['experience'] += rewards['experience'] // 2
                companion['current_status']['brave_points'] += rewards['brave_points'] // 2
                
                # 성격에 따른 승리 반응
                personality = companion['ai_personality']
                victory_reactions = {
                    "용감한": ["훌륭한 전투였어요!", "역시 정면승부가 최고죠!", "다음엔 더 강한 적과 싸워봐요!"],
                    "신중한": ["계획대로 되었네요.", "신중한 접근이 효과적이었어요.", "위험을 잘 관리했습니다."],
                    "지원형": ["모두 무사해서 다행이에요!", "팀워크가 완벽했습니다!", "서로 도와서 이겼네요!"],
                    "독립적": ["각자 역할을 잘했네요.", "효율적인 전투였어요.", "만족스러운 결과입니다."],
                    "적응형": ["상황에 잘 적응했어요!", "유연한 대응이 성공의 열쇠였네요!", "다양한 전술이 효과적이었어요!"]
                }
                
                reaction = random.choice(victory_reactions[personality])
                print(f"   {companion['name']}: {reaction}")
            
            # 승리 후 전용 세이브 업데이트
            print("\n💾 승리 상태를 전용 세이브에 기록 중...")
            
            victory_save_data = {
                "scenario": scenario,
                "player_character": self.player_character,
                "ai_companions": self.ai_companions,
                "completion_time": datetime.now().isoformat(),
                "adventure_phase": "completed_victory",
                "rewards": rewards
            }
            
            try:
                save_path = self.create_exclusive_save(victory_save_data)
                print(f"✅ 승리 세이브 업데이트 완료: {Path(save_path).name}")
            except Exception as e:
                print(f"⚠️ 승리 세이브 업데이트 실패: {e}")
                
        else:
            print("💀 패배...")
            print("다시 도전해보세요. AI 동료들이 더 나은 전략을 제안할 것입니다.")
            
            # AI 동료들의 격려 (성격에 따라)
            for companion in self.ai_companions:
                personality = companion['ai_personality']
                encourage_reactions = {
                    "용감한": ["다음엔 더 강하게 싸워봐요!", "포기하지 마세요!", "용기를 내서 다시 도전해요!"],
                    "신중한": ["전략을 다시 검토해봅시다.", "실패에서 배울 점이 있어요.", "더 신중하게 접근해봐요."],
                    "지원형": ["괜찮아요, 함께 다시 해봐요!", "실패는 성공의 어머니입니다!", "제가 더 도울게요!"],
                    "독립적": ["각자 부족한 점을 보완해봅시다.", "다음엔 더 잘할 수 있어요.", "개인 실력을 더 키워봐요."],
                    "적응형": ["다른 방법을 시도해봅시다!", "실패도 경험이에요!", "유연하게 접근 방식을 바꿔봐요!"]
                }
                
                reaction = random.choice(encourage_reactions[personality])
                print(f"   {companion['name']}: {reaction}")
            
            # 패배 상태도 전용 세이브에 기록
            print("\n💾 패배 상태를 전용 세이브에 기록 중...")
            
            defeat_save_data = {
                "scenario": scenario,
                "player_character": self.player_character,
                "ai_companions": self.ai_companions,
                "completion_time": datetime.now().isoformat(),
                "adventure_phase": "completed_defeat"
            }
            
            try:
                save_path = self.create_exclusive_save(defeat_save_data)
                print(f"✅ 패배 세이브 업데이트 완료: {Path(save_path).name}")
            except Exception as e:
                print(f"⚠️ 패배 세이브 업데이트 실패: {e}")
            
            # 게임 오버 옵션 제공
            print("\n💀 게임 오버 옵션:")
            print("1. 🔄 즉시 리셋하고 다시 시도 (초기 상태로)")
            print("2. 📂 백업에서 복원 (모험 시작 전 상태로)")
            print("3. 💪 현재 상태로 계속 진행")
            
            while True:
                game_over_choice = safe_input("\n선택하세요 (1-3): ", 2).strip()
                
                if game_over_choice == "1":
                    print("🔄 캐릭터들을 초기 상태로 리셋합니다...")
                    self.reset_characters_on_game_over()
                    break
                elif game_over_choice == "2":
                    print("📂 백업에서 복원을 시도합니다...")
                    if self.restore_from_backup():
                        print("✅ 백업에서 성공적으로 복원했습니다!")
                    else:
                        print("❌ 백업 복원에 실패했습니다. 현재 상태로 계속합니다.")
                    break
                elif game_over_choice == "3":
                    print("💪 현재 상태로 계속 진행합니다!")
                    break
                else:
                    print("❌ 1-3 사이의 숫자를 입력해주세요.")
    
    def adjust_ai_personality(self):
        """AI 동료 성격 조정"""
        if not self.ai_companions:
            print("❌ AI 동료가 없습니다.")
            return
        
        print(f"\n🎭 AI 성격 조정")
        print("=" * 50)
        
        # AI 동료 선택
        print("조정할 AI 동료를 선택하세요:")
        for i, companion in enumerate(self.ai_companions, 1):
            if 'advanced_ai' in companion and ADVANCED_AI_AVAILABLE:
                current_personality = companion['advanced_ai'].personality_type.value
                print(f"{i}. {companion['name']} ({companion['character_class']}) - {current_personality}")
            else:
                current_personality = companion['ai_personality']
                print(f"{i}. {companion['name']} ({companion['character_class']}) - {current_personality}")
        
        try:
            choice = int(input(f"\n선택 (1-{len(self.ai_companions)}): ")) - 1
            if 0 <= choice < len(self.ai_companions):
                selected_companion = self.ai_companions[choice]
                
                if 'advanced_ai' in selected_companion and ADVANCED_AI_AVAILABLE:
                    self._adjust_advanced_ai_personality(selected_companion)
                else:
                    self._adjust_basic_ai_personality(selected_companion)
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _adjust_advanced_ai_personality(self, companion: Dict):
        """고급 AI 성격 조정"""
        print(f"\n🧠 {companion['name']}의 고급 AI 성격 조정")
        print("-" * 40)
        
        ai = companion['advanced_ai']
        
        print(f"현재 성격 유형: {ai.personality_type.value}")
        print("\n새로운 성격 유형을 선택하세요:")
        
        personality_types = list(AIPersonalityType)
        for i, ptype in enumerate(personality_types, 1):
            print(f"{i:2d}. {ptype.value}")
        
        try:
            choice = int(input(f"\n선택 (1-{len(personality_types)}): ")) - 1
            if 0 <= choice < len(personality_types):
                new_personality = personality_types[choice]
                
                # 성격 유형 변경
                ai.personality_type = new_personality
                # 새 성격에 맞는 특성 재생성
                ai.personality_traits = ai._generate_detailed_personality()
                companion['personality_traits'] = ai.personality_traits
                
                print(f"\n✅ {companion['name']}의 성격이 '{new_personality.value}'로 변경되었습니다!")
                
                # 새로운 특성 표시
                top_traits = sorted(ai.personality_traits.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"새로운 주요 특성: {', '.join([f'{trait}({value:.2f})' for trait, value in top_traits])}")
                
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
        except Exception as e:
            print(f"❌ 성격 조정 실패: {e}")
    
    def _adjust_basic_ai_personality(self, companion: Dict):
        """기본 AI 성격 조정"""
        print(f"\n🤖 {companion['name']}의 기본 AI 성격 조정")
        print("-" * 40)
        
        print(f"현재 성격: {companion['ai_personality']}")
        print("\n새로운 성격을 선택하세요:")
        
        personalities = list(self.ai_personalities.keys())
        for i, personality in enumerate(personalities, 1):
            print(f"{i}. {personality} - {self.ai_personalities[personality]['description']}")
        
        try:
            choice = int(input(f"\n선택 (1-{len(personalities)}): ")) - 1
            if 0 <= choice < len(personalities):
                new_personality = personalities[choice]
                companion['ai_personality'] = new_personality
                companion['ai_traits'] = self.ai_personalities[new_personality].copy()
                
                # 전투 선호도도 재생성
                companion['ai_combat_preferences'] = self._generate_combat_preferences(
                    companion['character_class'], new_personality
                )
                
                print(f"\n✅ {companion['name']}의 성격이 '{new_personality}'로 변경되었습니다!")
                print(f"새로운 특성: {self.ai_personalities[new_personality]['description']}")
                
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def reset_characters_on_game_over(self):
        """게임 오버 시 캐릭터들을 초기 상태로 리셋"""
        print("\n💀 게임 오버 감지!")
        print("🔄 캐릭터들을 초기 상태로 리셋합니다...")
        
        # 플레이어 캐릭터 리셋
        if self.player_character and "original_data" in self.player_character:
            original_data = self.player_character["original_data"]
            print(f"   🔄 {self.player_character['name']} 리셋 중...")
            
            # 기본 스탯과 레벨만 초기화 (AI 관련 기억은 유지)
            self.player_character.update({
                "level": original_data["level"],
                "stats": original_data["stats"].copy(),
                "current_status": original_data["current_status"].copy(),
                "equipment": original_data.get("equipment", {}).copy(),
            })
            
            print(f"   ✅ {self.player_character['name']} Lv.{original_data['level']}로 리셋 완료")
        
        # AI 동료들 리셋
        for companion in self.ai_companions:
            if "original_data" in companion:
                original_data = companion["original_data"]
                print(f"   🔄 {companion['name']} 리셋 중...")
                
                # 기본 데이터만 리셋 (AI 성격, 관계도, 학습 내용은 유지)
                companion.update({
                    "level": original_data["level"],
                    "stats": original_data["stats"].copy(),
                    "current_status": original_data["current_status"].copy(),
                    "equipment": original_data.get("equipment", {}).copy(),
                })
                
                # AI 관계도는 약간만 감소 (완전 리셋 X)
                if "ai_relationship" in companion:
                    relationship = companion["ai_relationship"]
                    relationship["loyalty"] = max(50, relationship["loyalty"] - 10)
                    relationship["trust"] = max(40, relationship["trust"] - 15)
                    # 친밀도는 유지 (추억은 남음)
                
                print(f"   ✅ {companion['name']} Lv.{original_data['level']}로 리셋 완료")
        
        print("\n🎯 리셋 완료! 게임을 다시 시작할 수 있습니다.")
        print("💡 AI들의 성격과 기억은 유지되어 이전 경험을 기억합니다.")
        
        return True
    
    def backup_current_state(self):
        """현재 게임 상태 백업 (게임 오버 전 호출)"""
        if not self.player_character:
            return False
            
        backup_data = {
            "player_character": self.player_character.copy(),
            "ai_companions": [comp.copy() for comp in self.ai_companions],
            "backup_time": datetime.now().isoformat(),
            "backup_reason": "게임 진행 중 백업"
        }
        
        try:
            with open("game_state_backup.json", 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            print("💾 게임 상태가 백업되었습니다.")
            return True
        except Exception as e:
            print(f"❌ 백업 실패: {e}")
            return False
    
    def restore_from_backup(self):
        """백업된 상태에서 복원"""
        try:
            with open("game_state_backup.json", 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            self.player_character = backup_data.get("player_character")
            self.ai_companions = backup_data.get("ai_companions", [])
            
            print("📂 백업된 게임 상태를 복원했습니다.")
            print(f"   백업 시간: {backup_data.get('backup_time', 'Unknown')}")
            return True
            
        except FileNotFoundError:
            print("💡 백업 파일이 없습니다.")
            return False
        except Exception as e:
            print(f"❌ 복원 실패: {e}")
            return False
    
    def save_party_data(self):
        """파티 데이터 저장"""
        party_data = {
            "player_character": self.player_character,
            "ai_companions": self.ai_companions,
            "created_at": datetime.now().isoformat(),
            "party_size": len(self.ai_companions) + (1 if self.player_character else 0)
        }
        
        try:
            with open("ai_party_data.json", 'w', encoding='utf-8') as f:
                json.dump(party_data, f, ensure_ascii=False, indent=2)
            print("💾 AI 파티 데이터가 저장되었습니다.")
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
    
    def load_party_data(self):
        """파티 데이터 로드"""
        try:
            with open("ai_party_data.json", 'r', encoding='utf-8') as f:
                party_data = json.load(f)
            
            self.player_character = party_data.get("player_character")
            self.ai_companions = party_data.get("ai_companions", [])
            
            print("📂 AI 파티 데이터가 로드되었습니다.")
            print(f"   플레이어: {self.player_character['name'] if self.player_character else '없음'}")
            print(f"   AI 동료: {len(self.ai_companions)}명")
            return True
        except FileNotFoundError:
            print("💡 저장된 AI 파티 데이터가 없습니다.")
            return False
        except Exception as e:
            print(f"❌ 로드 실패: {e}")
            return False

    # ========================================
    # ⚡ 특성/패시브 선택 시스템 (3단계 통합)
    # ========================================
    
    def setup_traits_and_passives(self, game_characters):
        """게임 투입 전 특성과 패시브 선택"""
        try:
            print(f"\n{'='*60}")
            print(f"🌟 특성 및 패시브 효과 선택")
            print(f"{'='*60}")
            
            # 디버그: 캐릭터 목록 확인
            print(f"📋 총 {len(game_characters)}명의 캐릭터")
            for i, char in enumerate(game_characters):
                # Character 객체의 is_player 속성 확인
                is_player = getattr(char, 'is_player', False)
                print(f"  {i+1}. {char.name} ({char.character_class}) - 플레이어: {is_player}")
            
            # 1. 플레이어 특성 선택 (수동)
            player_characters = [char for char in game_characters if getattr(char, 'is_player', False)]
            print(f"\n👤 {len(player_characters)}명의 플레이어 캐릭터 발견")
            
            for i, character in enumerate(player_characters, 1):
                print(f"\n🎯 플레이어 {i}: {character.name} - 특성 선택")
                # 플레이어는 직접 선택
                self._select_character_traits(character, is_player=True, allow_manual=True)
            
            # 2. AI 동료 특성 자동 선택
            ai_companions = [char for char in game_characters if not getattr(char, 'is_player', False)]
            print(f"\n🤖 {len(ai_companions)}명의 AI 동료 발견")
            
            for i, character in enumerate(ai_companions, 1):
                print(f"\n🔧 AI 동료 {i}: {character.name} - 자동 특성 선택 중...")
                # AI는 자동 선택
                try:
                    if hasattr(character, 'available_traits'):
                        character.passive_traits = []
                    print(f"✅ {character.name} 기본 설정 완료")
                except:
                    print(f"⚠️ {character.name} 기본 설정 적용")
            
            # 3. 패시브 효과는 게임 내에서 선택
            print(f"\n💡 패시브 효과는 게임 시작 후 선택할 수 있습니다.")
            
            print(f"\n✅ 모든 설정이 완료되었습니다! 게임을 시작합니다.")
            
        except Exception as e:
            print(f"❌ 특성/패시브 선택 중 오류: {e}")
            print(f"⚠️ 기본 설정으로 게임을 시작합니다.")
            import traceback
            traceback.print_exc()
    
    def _select_character_traits(self, character, is_player=False, allow_manual=False):
        """개별 캐릭터 특성 선택"""
        try:
            # 특성 시스템이 있는지 확인
            if not SYSTEMS_AVAILABLE:
                print(f"⚠️ 특성 시스템을 사용할 수 없습니다. 기본 설정을 사용합니다.")
                return
            
            try:
                from game.character import CharacterClassManager
                
                # 직업별 추천 특성 가져오기
                available_traits = CharacterClassManager.get_class_traits(character.character_class)
                
                if not available_traits:
                    print(f"💡 {character.name}에게 사용 가능한 특성이 없습니다.")
                    return
                
                # 캐릭터에 특성 정보 설정
                character.available_traits = available_traits
                
                if is_player:
                    # 플레이어는 항상 직접 선택
                    print(f"\n📋 {character.name}의 특성을 선택해주세요:")
                    self._manual_trait_selection_cursor(character)
                elif allow_manual:
                    # AI 동료도 수동/자동 선택 가능
                    selection_mode = self._ask_trait_selection_mode(character)
                    if selection_mode == 'manual':
                        print(f"\n📋 {character.name}의 특성을 직접 선택해주세요:")
                        self._manual_trait_selection_cursor(character)
                    else:
                        print(f"🤖 AI가 {character.name}의 특성을 자동 선택합니다...")
                        self._auto_trait_selection(character, available_traits)
                else:
                    # 자동 선택만
                    print(f"🤖 AI가 {character.name}의 특성을 자동 선택합니다...")
                    self._auto_trait_selection(character, available_traits)
                    
            except ImportError:
                print(f"⚠️ 특성 시스템 모듈을 찾을 수 없습니다.")
                return
                
        except Exception as e:
            print(f"❌ {character.name} 특성 선택 오류: {e}")
    
    def _ask_trait_selection_mode(self, character):
        """AI 동료의 특성 선택 방식을 묻기"""
        try:
            print(f"\n🎯 {character.name}의 특성 선택 방식을 정해주세요:")
            print("1. 🎯 직접 선택 - 플레이어가 직접 특성을 고르기")
            print("2. 🤖 AI 자동 선택 - AI가 성격에 맞게 자동 선택")
            
            while True:
                choice = safe_korean_input("선택 (1-2)", allow_back=True)
                
                if choice == "BACK":
                    return 'auto'
                elif choice == "1":
                    return 'manual'
                elif choice == "2":
                    return 'auto'
                else:
                    print("❌ 1 또는 2를 입력해주세요.")
                    
        except Exception as e:
            print(f"❌ 특성 선택 방식 선택 오류: {e}")
            return 'auto'
    
    def _manual_trait_selection_cursor(self, character):
        """스마트 한글 입력 기반 특성 선택"""
        try:
            if not hasattr(character, 'available_traits') or not character.available_traits:
                print(f"⚠️ {character.name}에게 사용 가능한 특성이 없습니다.")
                return False
            
            selected_indices = []
            max_traits = 2
            
            print(f"\n🎯 {character.name}의 특성 선택 ({max_traits}개까지)")
            print("="*50)
            
            while len(selected_indices) < max_traits:
                remaining = max_traits - len(selected_indices)
                
                # 사용 가능한 특성 표시
                print(f"\n📋 사용 가능한 특성 (남은 선택: {remaining}개):")
                for i, trait in enumerate(character.available_traits):
                    # 선택 상태 표시
                    status = " ✅" if i in selected_indices else ""
                    # 특성 효과에 따른 아이콘
                    trait_icon = "⚔️"
                    if "공격" in trait.description or "데미지" in trait.description:
                        trait_icon = "⚔️"
                    elif "방어" in trait.description or "HP" in trait.description:
                        trait_icon = "🛡️"
                    elif "속도" in trait.description or "회피" in trait.description:
                        trait_icon = "💨"
                    elif "마법" in trait.description or "MP" in trait.description:
                        trait_icon = "🔮"
                    elif "회복" in trait.description or "치유" in trait.description:
                        trait_icon = "💚"
                    elif "크리티컬" in trait.description or "치명타" in trait.description:
                        trait_icon = "💥"
                    
                    print(f"  {i+1}. {trait_icon} {trait.name}{status}")
                    print(f"      {trait.description}")
                
                # 특별 옵션들
                if selected_indices:
                    print(f"\n📌 특별 옵션:")
                    print(f"  c. ✅ 선택 완료 ({len(selected_indices)}개 특성)")
                    print(f"  r. 🔄 선택 초기화")
                
                print(f"  q. 🔙 취소")
                
                # 현재 선택된 특성 표시
                if selected_indices:
                    selected_names = [character.available_traits[i].name for i in selected_indices]
                    print(f"\n현재 선택됨: {', '.join(selected_names)}")
                
                choice = safe_korean_input(f"\n선택하세요 (1-{len(character.available_traits)}, c, r, q)", allow_back=True)
                
                if choice == "BACK" or choice.lower() == "q":
                    print(f"🚫 특성 선택이 취소되었습니다.")
                    return False
                elif choice.lower() == "c" and selected_indices:
                    # 선택 완료
                    break
                elif choice.lower() == "r":
                    # 선택 초기화
                    selected_indices = []
                    print(f"🔄 선택이 초기화되었습니다.")
                    continue
                elif choice.isdigit():
                    trait_index = int(choice) - 1
                    if 0 <= trait_index < len(character.available_traits):
                        if trait_index in selected_indices:
                            # 선택 해제
                            selected_indices.remove(trait_index)
                            trait_name = character.available_traits[trait_index].name
                            print(f"❌ {trait_name} 선택 해제됨")
                        else:
                            # 선택 추가
                            selected_indices.append(trait_index)
                            trait_name = character.available_traits[trait_index].name
                            print(f"✅ {trait_name} 선택됨!")
                            
                            # 최대 개수 도달하면 자동 완료
                            if len(selected_indices) >= max_traits:
                                break
                    else:
                        print(f"❌ 1~{len(character.available_traits)} 사이의 숫자를 입력해주세요.")
                else:
                    print(f"❌ 올바른 옵션을 선택해주세요.")
            
            # 특성 적용
            if selected_indices:
                # 캐릭터에 특성 적용 (실제 게임 연동시 활성화)
                if hasattr(character, 'select_passive_traits'):
                    character.select_passive_traits(selected_indices)
                else:
                    # 임시로 속성에 저장
                    character.selected_trait_indices = selected_indices
                
                selected_traits = [character.available_traits[i].name for i in selected_indices]
                print(f"\n{'='*50}")
                print(f"🎉 특성 선택 완료!")
                print(f"선택된 특성: {', '.join(selected_traits)}")
                print(f"{'='*50}")
                return True
            else:
                print(f"\n🔄 특성 없이 진행합니다.")
                if hasattr(character, 'select_passive_traits'):
                    character.select_passive_traits([])
                return True
                
        except Exception as e:
            print(f"❌ 특성 선택 오류: {e}")
            # 폴백으로 자동 선택
            print(f"⚠️ 자동 선택으로 대체합니다.")
            if hasattr(character, 'available_traits'):
                self._auto_trait_selection(character, character.available_traits)
            return True
    
    def _auto_trait_selection(self, character, available_traits):
        """AI용 자동 특성 선택 (성격 기반)"""
        import random
        
        # AI 성격에 따른 특성 선호도
        personality = getattr(character, 'ai_personality', 'balanced')
        
        # 성격별 특성 우선순위 (실제 특성 이름에 맞게 조정 필요)
        personality_preferences = {
            'aggressive': ['전투 광', '공격적 성향', '용맹', '공격력', '데미지'],
            'defensive': ['방어 전문가', '보호 본능', '인내', '방어력', 'HP'],
            'supportive': ['치유술사', '지원 전문가', '협력', '회복', '지원'],
            'balanced': ['다재다능', '균형감각', '적응력', '전체적', '균형'],
            'cunning': ['교활함', '전술가', '기회주의자', '크리티컬', '회피']
        }
        
        # 성격에 맞는 특성 우선 선택
        preferred_traits = []
        if personality in personality_preferences:
            for keyword in personality_preferences[personality]:
                for trait in available_traits:
                    if keyword.lower() in trait.name.lower() or keyword.lower() in trait.description.lower():
                        if trait not in preferred_traits:
                            preferred_traits.append(trait)
        
        # 우선 특성이 없으면 랜덤 선택
        if not preferred_traits:
            preferred_traits = available_traits
        
        # 최대 2개 특성 선택
        selected_count = min(2, len(preferred_traits))
        selected_traits = random.sample(preferred_traits, selected_count) if preferred_traits else []
        
        # 인덱스로 변환해서 적용
        selected_indices = []
        for trait in selected_traits:
            if trait in available_traits:
                selected_indices.append(available_traits.index(trait))
        
        # 캐릭터에 적용
        if hasattr(character, 'select_passive_traits'):
            character.select_passive_traits(selected_indices)
        else:
            # 임시로 속성에 저장
            character.selected_trait_indices = selected_indices
        
        # 선택 결과 표시
        for trait in selected_traits:
            print(f"  ✓ {trait.name}: {trait.description}")
        
        print(f"✅ AI가 {character.name}을 위해 {len(selected_traits)}개 특성을 선택했습니다.")
    
    def main_menu(self):
        """메인 메뉴"""
        # 기존 데이터 로드 시도
        self.load_party_data()
        
        while True:
            print("\n" + "="*60)
            print("🎮 Dawn of Stellar - 플레이어 중심 AI 멀티플레이어")
            print("="*60)
            
            if self.player_character:
                print(f"👤 현재 플레이어: {self.player_character['name']} ({self.player_character['character_class']})")
                print(f"🤖 AI 동료: {len(self.ai_companions)}명")
            else:
                print("👤 플레이어: 미설정")
            
            print(f"📂 사용 가능한 캐릭터: {len(self.character_presets)}명")
            print(f"📋 사용 가능한 파티 프리셋: {len(self.party_presets)}개")
            
            print("\n1. 👤 플레이어 캐릭터 설정")
            print("2. 🤖 AI 동료 자동 생성")
            print("3. 📋 기존 파티 프리셋 사용")
            print("4. 👥 파티 상태 보기")
            print("5. 🎯 훈련 모드")
            print("6. 🗺️ 간단한 모험")
            if SYSTEMS_AVAILABLE:
                print("7. � 실제 게임 시작 (게임 모듈 직접 실행)")
            print("8. �🎭 AI 성격 조정")
            print("9. 💾 AI 파티 데이터 저장")
            print("10. 📂 AI 파티 데이터 로드")
            print("11. 🔄 캐릭터 프리셋 새로고침")
            print("12. 💀 게임 오버 리셋 (초기 상태로)")
            print("13. 🔄 백업에서 복원")
            print("14. 🔒 멀티플레이어 세이브 관리")
            if SYSTEMS_AVAILABLE:
                print("15. 🎯 고급 AI 훈련 시스템")
            if SAFE_EXIT_AVAILABLE:
                print("99. 🛡️ 안전 종료")
            print("0. 🚪 종료")
            
            choice = safe_input("\n선택하세요: ", 3).strip()
            
            if choice == "1":
                self.create_player_character()
            elif choice == "2":
                self.create_ai_companions()
            elif choice == "3":
                self.create_preset_party()
            elif choice == "4":
                self.show_party_status()
            elif choice == "5":
                self.start_training_mode()
            elif choice == "6":
                self.start_simple_adventure()
            elif choice == "7" and SYSTEMS_AVAILABLE:
                self.start_real_game()
            elif choice == "8":
                self.show_learning_management_menu()
            elif choice == "9":
                self.adjust_ai_personality()
            elif choice == "10":
                self.save_party_data()
            elif choice == "11":
                self.load_party_data()
            elif choice == "12":
                self.load_character_presets()
            elif choice == "13":
                if self.player_character:
                    confirm = input("\n⚠️ 정말로 모든 캐릭터를 초기 상태로 리셋하시겠습니까? (Y/N): ").strip().lower()
                    if confirm in ['y', 'yes', '예', 'ㅇ']:
                        self.reset_characters_on_game_over()
                    else:
                        print("❌ 리셋을 취소했습니다.")
                else:
                    print("❌ 파티가 구성되어 있지 않습니다.")
            elif choice == "14":
                self.restore_from_backup()
            elif choice == "15":
                self.manage_multiplayer_saves()
            elif choice == "16" and SYSTEMS_AVAILABLE:
                try:
                    training_system.show_training_menu()
                except Exception as e:
                    print(f"❌ 고급 훈련 시스템 오류: {e}")
            elif choice == "17":
                self.show_system_status()
            elif choice == "18":
                self.show_quick_start_guide()
            elif choice == "99" and SAFE_EXIT_AVAILABLE:
                print("🛡️ 안전 종료를 시작합니다...")
                self.stop_background_learning()  # 학습 시스템 정리
                self.emergency_save_all()
                safe_exit(0)
            elif choice == "0":
                # 종료 시 모험 세션 정리
                if self.current_adventure_id:
                    print("\n🏁 모험 세션을 종료하고 캐릭터 잠금을 해제합니다...")
                    self.end_adventure_session()
                
                if SAFE_EXIT_AVAILABLE:
                    print("�️ 안전 종료 프로세스를 실행합니다...")
                    self.emergency_save_all()
                    safe_exit(0)
                else:
                    print("�👋 게임을 종료합니다.")
                    break
            else:
                print("❌ 잘못된 선택입니다.")
            
            if choice != "0":
                input("\nEnter를 눌러 계속...")
    
    # ========================================
    # 🎮 게임 통합 시스템 (4단계 통합)
    # ========================================
    
    def start_real_game(self):
        """실제 게임 모듈과 연동하여 게임 시작"""
        try:
            if not self.player_character or not self.ai_companions:
                print("❌ 먼저 파티를 구성해주세요.")
                return False
            
            print(f"\n{'='*60}")
            print(f"🎮 실제 게임 모듈 연동 시작")
            print(f"{'='*60}")
            
            # 게임 시스템 모듈 import
            try:
                from game.character import Character, CharacterClassManager, PartyManager
                from game.world import GameWorld
                from game.brave_combat import BraveCombatSystem
                from game.display import GameDisplay
                print("✅ 게임 시스템 모듈 로딩 완료")
            except ImportError as e:
                print(f"❌ 게임 시스템 모듈 로딩 실패: {e}")
                print("💡 대신 간단한 모험 모드를 이용해보세요.")
                return False
            
            # 캐릭터 변환
            game_characters = []
            party_manager = PartyManager()
            
            # 플레이어 캐릭터 생성
            try:
                player_char = Character(
                    name=self.player_character['name'],
                    character_class=self.player_character['character_class']
                )
                player_char.is_player = True
                
                # 저장된 능력치 적용
                if 'current_status' in self.player_character:
                    status = self.player_character['current_status']
                    player_char.level = status.get('level', 1)
                    player_char.experience = status.get('experience', 0)
                    if 'brave_points' in status:
                        player_char.brave_points = status['brave_points']
                
                game_characters.append(player_char)
                party_manager.add_party_member(player_char)
                print(f"✅ 플레이어 캐릭터 '{player_char.name}' 생성 완료")
                
            except Exception as e:
                print(f"❌ 플레이어 캐릭터 생성 실패: {e}")
                return False
            
            # AI 동료 캐릭터 생성
            for i, companion_data in enumerate(self.ai_companions):
                try:
                    ai_char = Character(
                        name=companion_data['name'],
                        character_class=companion_data['character_class']
                    )
                    ai_char.is_player = False
                    ai_char.ai_personality = companion_data['ai_personality']
                    
                    # 저장된 능력치 적용
                    if 'current_status' in companion_data:
                        status = companion_data['current_status']
                        ai_char.level = status.get('level', 1)
                        ai_char.experience = status.get('experience', 0)
                        if 'brave_points' in status:
                            ai_char.brave_points = status['brave_points']
                    
                    game_characters.append(ai_char)
                    party_manager.add_party_member(ai_char)
                    print(f"✅ AI 동료 '{ai_char.name}' 생성 완료")
                    
                except Exception as e:
                    print(f"❌ AI 동료 {companion_data['name']} 생성 실패: {e}")
                    continue
            
            print(f"\n📋 총 {len(game_characters)}명의 캐릭터가 게임에 참여합니다.")
            
            # 특성 선택 시스템 실행
            print(f"\n🌟 게임 시작 전 특성 및 패시브 선택")
            print("-" * 60)
            self.setup_traits_and_passives(game_characters)
            
            # 게임 월드 생성
            try:
                game_world = GameWorld()
                print("✅ 게임 월드 생성 완료")
            except Exception as e:
                print(f"❌ 게임 월드 생성 실패: {e}")
                return False
            
            # 전투 시스템 초기화
            try:
                combat_system = BraveCombatSystem()
                # AI 모드 명시적 비활성화
                combat_system.set_ai_game_mode(False)
                print("✅ 전투 시스템 초기화 완료")
            except Exception as e:
                print(f"❌ 전투 시스템 초기화 실패: {e}")
                return False
            
            # 디스플레이 시스템 초기화
            try:
                display = GameDisplay()
                print("✅ 디스플레이 시스템 초기화 완료")
            except Exception as e:
                print(f"❌ 디스플레이 시스템 초기화 실패: {e}")
                return False
            
            # 게임 루프 전 최종 확인
            print(f"\n{'='*60}")
            print(f"🚀 게임 시작 준비 완료!")
            print(f"👤 플레이어: {player_char.name} ({player_char.character_class})")
            for i, char in enumerate(game_characters[1:], 1):
                print(f"🤖 AI 동료 {i}: {char.name} ({char.character_class})")
            print(f"{'='*60}")
            
            # 게임 시작 확인
            start_confirm = safe_korean_input("\n게임을 시작하시겠습니까? (Y/N)", allow_back=True)
            if start_confirm == "BACK" or start_confirm.lower() not in ['y', 'yes', '예', 'ㅇ']:
                print("🔙 게임 시작을 취소했습니다.")
                return False
            
            # 실제 게임 루프 시작
            print(f"\n🎮 Dawn of Stellar 게임 시작!")
            print("="*60)
            
            # 게임 메인 루프 시뮬레이션 (실제 게임 엔진 연동)
            return self._run_integrated_game_loop(
                party_manager=party_manager,
                game_world=game_world,
                combat_system=combat_system,
                display=display,
                game_characters=game_characters
            )
            
        except Exception as e:
            print(f"❌ 게임 시작 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_integrated_game_loop(self, party_manager, game_world, combat_system, display, game_characters):
        """통합 게임 루프 실행"""
        try:
            print("🎯 통합 게임 루프를 시작합니다...")
            
            # 실제 main.py의 게임 루프를 모방
            # 현재는 간단한 시뮬레이션으로 구현
            
            current_floor = 1
            max_floors = 5  # 테스트를 위해 5층만
            
            while current_floor <= max_floors:
                print(f"\n{'='*50}")
                print(f"🏰 던전 {current_floor}층 진입")
                print(f"{'='*50}")
                
                # 층별 이벤트 생성
                import random
                event_type = random.choice(['battle', 'treasure', 'event', 'rest'])
                
                if event_type == 'battle':
                    # 전투 시뮬레이션
                    print(f"⚔️ 적과 조우했습니다!")
                    
                    # 간단한 전투 결과 시뮬레이션
                    battle_success = self._simulate_battle(game_characters, current_floor)
                    
                    if battle_success:
                        print(f"🎉 전투 승리!")
                        # 경험치 및 보상 지급
                        exp_gain = current_floor * 20
                        brave_gain = current_floor * 50
                        
                        for char in game_characters:
                            char.experience += exp_gain
                            if hasattr(char, 'brave_points'):
                                char.brave_points += brave_gain
                        
                        print(f"📈 모든 파티원이 경험치 {exp_gain}, BRV {brave_gain} 획득!")
                    else:
                        print(f"💀 전투 패배... 이전 층으로 후퇴합니다.")
                        if current_floor > 1:
                            current_floor -= 1
                        continue
                
                elif event_type == 'treasure':
                    print(f"💰 보물상자를 발견했습니다!")
                    treasures = ['회복 포션', '마나 포션', '마법 반지', '강화석']
                    found_treasure = random.choice(treasures)
                    print(f"🎁 {found_treasure}을(를) 획득했습니다!")
                
                elif event_type == 'event':
                    print(f"❓ 특별한 이벤트가 발생했습니다!")
                    events = [
                        '신비한 치유의 샘을 발견했습니다. 모든 파티원의 HP가 회복됩니다.',
                        '고대 마법진을 발견했습니다. 모든 파티원의 MP가 회복됩니다.',
                        '현명한 현자를 만났습니다. 파티원들이 지혜를 얻습니다.',
                        '상인을 만났습니다. 아이템을 거래할 수 있습니다.'
                    ]
                    event_desc = random.choice(events)
                    print(f"✨ {event_desc}")
                
                elif event_type == 'rest':
                    print(f"🛡️ 안전한 휴식처를 발견했습니다.")
                    print(f"💤 파티원들이 휴식을 취하며 체력을 회복합니다.")
                
                # 다음 층 진행 여부 확인
                if current_floor < max_floors:
                    continue_choice = safe_korean_input(f"\n다음 층({current_floor + 1}층)으로 진행하시겠습니까? (Y/N)", allow_back=True)
                    if continue_choice == "BACK" or continue_choice.lower() not in ['y', 'yes', '예', 'ㅇ']:
                        print("🏃 던전에서 퇴각합니다.")
                        break
                
                current_floor += 1
            
            # 게임 완료
            if current_floor > max_floors:
                print(f"\n🎊 축하합니다! 던전을 완전히 정복했습니다!")
                print(f"🏆 최종 층수: {max_floors}층")
                
                # 최종 보상
                final_exp = max_floors * 100
                final_brave = max_floors * 200
                
                for char in game_characters:
                    char.experience += final_exp
                    if hasattr(char, 'brave_points'):
                        char.brave_points += final_brave
                
                print(f"🎁 완주 보너스: 경험치 {final_exp}, BRV {final_brave}")
            
            # 게임 종료 후 데이터 저장
            print(f"\n💾 게임 진행 상황을 저장합니다...")
            self._save_game_progress(game_characters)
            
            print(f"\n✅ 게임이 정상적으로 종료되었습니다!")
            return True
            
        except Exception as e:
            print(f"❌ 게임 루프 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _simulate_battle(self, game_characters, floor_level):
        """간단한 전투 시뮬레이션"""
        try:
            print(f"⚔️ 전투 시뮬레이션 시작! (층수: {floor_level})")
            
            # 파티 능력치 계산
            total_party_power = 0
            for char in game_characters:
                # 기본 능력치 + 레벨 보너스
                char_power = (char.level * 10) + getattr(char, 'experience', 0) // 10
                total_party_power += char_power
            
            # 적 능력치 (층수에 비례)
            enemy_power = floor_level * 100 + (floor_level * 50)
            
            print(f"👥 파티 전력: {total_party_power}")
            print(f"👹 적 전력: {enemy_power}")
            
            # 성공률 계산
            power_ratio = total_party_power / enemy_power
            base_success_rate = min(0.9, max(0.1, power_ratio * 0.6))
            
            # AI 동료 성격 보너스
            personality_bonus = 0
            for char in game_characters:
                if hasattr(char, 'ai_personality') and not getattr(char, 'is_player', True):
                    personality = char.ai_personality
                    if personality == '용감한':
                        personality_bonus += 0.1
                    elif personality == '신중한':
                        personality_bonus += 0.05
                    elif personality == '지원형':
                        personality_bonus += 0.08
                    elif personality == '적응형':
                        personality_bonus += 0.06
            
            final_success_rate = min(0.95, base_success_rate + personality_bonus)
            
            print(f"🎯 승리 확률: {final_success_rate:.1%}")
            
            # 전투 결과
            import random
            battle_result = random.random() < final_success_rate
            
            # AI 동료들의 전투 중 대사
            for char in game_characters:
                if hasattr(char, 'ai_personality') and not getattr(char, 'is_player', True):
                    personality = char.ai_personality
                    
                    if battle_result:
                        # 승리 대사
                        victory_lines = {
                            '용감한': ["정면승부 승리!", "이런 게 진짜 전투지!", "더 강한 적은 없나요?"],
                            '신중한': ["계획대로군요.", "신중한 접근이 효과적이었습니다.", "위험을 잘 관리했네요."],
                            '지원형': ["모두 안전해서 다행이에요!", "팀워크 승리입니다!", "함께 해냈네요!"],
                            '독립적': ["각자 역할을 했군요.", "효율적인 전투였습니다.", "만족스럽네요."],
                            '적응형': ["상황 대응 완벽!", "유연한 전술이 통했어요!", "적응력이 승부를 갈랐네요!"]
                        }
                    else:
                        # 패배 대사
                        defeat_lines = {
                            '용감한': ["다시 도전하자!", "이런 건 인정 못해!", "더 열심히 싸워야겠어!"],
                            '신중한': ["전략을 재검토해야겠어요.", "더 신중하게 접근합시다.", "분석이 부족했나봐요."],
                            '지원형': ["괜찮아요, 다시 해봐요!", "포기하지 말아요!", "함께 극복해요!"],
                            '독립적': ["개인 역량을 더 키워야겠네요.", "다음엔 더 잘하겠습니다.", "부족한 점을 보완하죠."],
                            '적응형': ["다른 방법을 시도해봅시다!", "적응이 부족했어요.", "유연성을 더 발휘해봐요!"]
                        }
                    
                    lines = victory_lines[personality] if battle_result else defeat_lines[personality]
                    selected_line = random.choice(lines)
                    print(f"💬 {char.name}: {selected_line}")
            
            return battle_result
            
        except Exception as e:
            print(f"❌ 전투 시뮬레이션 오류: {e}")
            return False
    
    def _save_game_progress(self, game_characters):
        """게임 진행 상황을 AI 멀티플레이어 데이터에 저장"""
        try:
            # 플레이어 캐릭터 업데이트
            player_char = next((char for char in game_characters if getattr(char, 'is_player', False)), None)
            if player_char and self.player_character:
                self.player_character['current_status']['level'] = player_char.level
                self.player_character['current_status']['experience'] = player_char.experience
                if hasattr(player_char, 'brave_points'):
                    self.player_character['current_status']['brave_points'] = player_char.brave_points
                
                print(f"✅ 플레이어 '{player_char.name}' 진행 상황 저장 완료")
            
            # AI 동료 업데이트
            ai_chars = [char for char in game_characters if not getattr(char, 'is_player', False)]
            for i, ai_char in enumerate(ai_chars):
                if i < len(self.ai_companions):
                    companion_data = self.ai_companions[i]
                    companion_data['current_status']['level'] = ai_char.level
                    companion_data['current_status']['experience'] = ai_char.experience
                    if hasattr(ai_char, 'brave_points'):
                        companion_data['current_status']['brave_points'] = ai_char.brave_points
                    
                    print(f"✅ AI 동료 '{ai_char.name}' 진행 상황 저장 완료")
            
            # 파티 데이터 자동 저장
            self.save_party_data()
            
        except Exception as e:
            print(f"❌ 게임 진행 상황 저장 실패: {e}")
    
    # ========================================
    # 🧠 백그라운드 학습 시스템 (5단계 통합)
    # ========================================
    
    def _init_background_learning(self):
        """백그라운드 학습 시스템 초기화"""
        try:
            print("🧠 AI 백그라운드 학습 시스템 초기화 중...")
            
            # 학습 데이터 구조 초기화
            self.learning_data = {
                'battle_experiences': [],
                'personality_adjustments': {},
                'success_patterns': {},
                'failure_analysis': {},
                'interaction_logs': []
            }
            
            # AI 개선 기록 초기화
            self.ai_improvement_records = {}
            
            # 학습 데이터 로드 시도
            self._load_learning_progress()
            
            print("✅ 백그라운드 학습 시스템 초기화 완료")
            
        except Exception as e:
            print(f"⚠️ 백그라운드 학습 시스템 초기화 실패: {e}")
    
    def start_background_learning(self):
        """백그라운드 학습 프로세스 시작"""
        try:
            if self.learning_active:
                print("⚠️ 백그라운드 학습이 이미 실행 중입니다.")
                return
            
            self.learning_active = True
            import threading
            self.learning_thread = threading.Thread(target=self._background_learning_process, daemon=True)
            self.learning_thread.start()
            print("✅ AI 백그라운드 학습 시작")
            
        except Exception as e:
            print(f"❌ 백그라운드 학습 시작 실패: {e}")
    
    def stop_background_learning(self):
        """백그라운드 학습 프로세스 중지"""
        try:
            if not self.learning_active:
                return
            
            self.learning_active = False
            if self.learning_thread and self.learning_thread.is_alive():
                print("🛑 AI 백그라운드 학습을 중지합니다...")
                # 스레드가 자연스럽게 종료될 때까지 대기
                import time
                time.sleep(1)
            
            print("✅ 백그라운드 학습 중지 완료")
            
        except Exception as e:
            print(f"❌ 백그라운드 학습 중지 실패: {e}")
    
    def _background_learning_process(self):
        """백그라운드 학습 프로세스 (메인 루프)"""
        import time
        
        while self.learning_active:
            try:
                # AI 동료들의 학습 진행
                self._process_ai_learning()
                
                # 학습 데이터 분석
                self._analyze_learning_patterns()
                
                # 성격 자동 조정
                self._auto_adjust_personalities()
                
                # 학습 진행도 저장
                self._save_learning_progress()
                
                # 15초마다 학습 프로세스 실행
                time.sleep(15)
                
            except Exception as e:
                print(f"❌ 백그라운드 학습 오류: {e}")
                time.sleep(5)
    
    def _process_ai_learning(self):
        """AI 동료들의 학습 처리"""
        try:
            if not self.ai_companions:
                return
            
            import time
            current_time = time.time()
            
            for companion in self.ai_companions:
                companion_name = companion['name']
                
                # 개별 AI 학습 기록 추적
                if companion_name not in self.ai_improvement_records:
                    self.ai_improvement_records[companion_name] = {
                        'learning_sessions': 0,
                        'battle_experience': 0,
                        'personality_evolution': [],
                        'success_rate': 0.5,
                        'last_improvement': current_time
                    }
                
                record = self.ai_improvement_records[companion_name]
                
                # 학습 세션 증가
                record['learning_sessions'] += 1
                
                # 최근 활동 기반 학습
                if 'current_status' in companion:
                    experience = companion['current_status'].get('experience', 0)
                    brave_points = companion['current_status'].get('brave_points', 0)
                    
                    # 경험치 증가 기반 학습
                    if experience > record['battle_experience']:
                        exp_gain = experience - record['battle_experience']
                        record['battle_experience'] = experience
                        
                        # 성공률 조정
                        if exp_gain > 50:  # 큰 경험치 획득 = 성공적인 전투
                            record['success_rate'] = min(0.95, record['success_rate'] + 0.05)
                        
                        self._log_learning_event(companion_name, 'experience_gain', {
                            'gained_exp': exp_gain,
                            'total_exp': experience,
                            'success_rate': record['success_rate']
                        })
                
                # 성격 발전 분석
                personality = companion['ai_personality']
                record['personality_evolution'].append({
                    'timestamp': current_time,
                    'personality': personality,
                    'success_rate': record['success_rate']
                })
                
                # 최근 10개 기록만 유지
                if len(record['personality_evolution']) > 10:
                    record['personality_evolution'] = record['personality_evolution'][-10:]
                
        except Exception as e:
            print(f"❌ AI 학습 처리 오류: {e}")
    
    def _analyze_learning_patterns(self):
        """학습 패턴 분석"""
        try:
            if not self.ai_improvement_records:
                return
            
            for companion_name, record in self.ai_improvement_records.items():
                # 성공률 기반 분석
                success_rate = record['success_rate']
                learning_sessions = record['learning_sessions']
                
                # 5세션마다 성과 분석
                if learning_sessions % 5 == 0:
                    if success_rate > 0.8:
                        print(f"🌟 {companion_name}의 학습 성과가 우수합니다! (성공률: {success_rate:.1%})")
                        self._reward_ai_improvement(companion_name)
                    elif success_rate < 0.3:
                        print(f"📚 {companion_name}이(가) 더 많은 학습이 필요합니다. (성공률: {success_rate:.1%})")
                        self._provide_ai_guidance(companion_name)
                
                # 성격 진화 패턴 분석
                evolution = record['personality_evolution']
                if len(evolution) >= 3:
                    # 최근 3회 기록 분석
                    recent = evolution[-3:]
                    avg_success = sum(entry['success_rate'] for entry in recent) / len(recent)
                    
                    if avg_success > 0.7:
                        print(f"📈 {companion_name}의 성격 '{recent[-1]['personality']}'이 잘 맞고 있습니다.")
                    elif avg_success < 0.4:
                        print(f"🔄 {companion_name}의 성격 조정이 필요할 수 있습니다.")
                
        except Exception as e:
            print(f"❌ 학습 패턴 분석 오류: {e}")
    
    def _auto_adjust_personalities(self):
        """성격 자동 조정 (학습 기반)"""
        try:
            if not self.ai_improvement_records:
                return
            
            for companion in self.ai_companions:
                companion_name = companion['name']
                record = self.ai_improvement_records.get(companion_name)
                
                if not record:
                    continue
                
                # 성공률이 계속 낮으면 성격 조정 제안
                if record['success_rate'] < 0.3 and record['learning_sessions'] > 10:
                    current_personality = companion['ai_personality']
                    
                    # 성격 변경 제안 로직
                    personality_improvements = {
                        '용감한': ['신중한', '적응형'],
                        '신중한': ['용감한', '지원형'],
                        '지원형': ['적응형', '신중한'],
                        '독립적': ['지원형', '적응형'],
                        '적응형': ['용감한', '신중한']
                    }
                    
                    if current_personality in personality_improvements:
                        suggested = personality_improvements[current_personality][0]
                        
                        print(f"\n💡 AI 학습 제안: {companion_name}의 성격을 '{current_personality}'에서 '{suggested}'로 조정하는 것이 좋을 것 같습니다.")
                        print(f"   (현재 성공률: {record['success_rate']:.1%}, 학습 세션: {record['learning_sessions']}회)")
                        
                        # 자동 조정 여부 묻기 (백그라운드이므로 로그만 남김)
                        self._log_learning_event(companion_name, 'personality_suggestion', {
                            'current': current_personality,
                            'suggested': suggested,
                            'reason': 'low_success_rate',
                            'success_rate': record['success_rate']
                        })
                
                # 성공률이 높으면 긍정 강화
                elif record['success_rate'] > 0.8:
                    self._log_learning_event(companion_name, 'personality_reinforcement', {
                        'personality': companion['ai_personality'],
                        'success_rate': record['success_rate'],
                        'message': 'personality_working_well'
                    })
                
        except Exception as e:
            print(f"❌ 성격 자동 조정 오류: {e}")
    
    def _reward_ai_improvement(self, companion_name):
        """AI 개선 보상"""
        try:
            # 해당 동료 찾기
            companion = next((c for c in self.ai_companions if c['name'] == companion_name), None)
            if not companion:
                return
            
            # 보상 적용
            if 'current_status' in companion:
                status = companion['current_status']
                
                # 경험치 보너스
                bonus_exp = 25
                status['experience'] = status.get('experience', 0) + bonus_exp
                
                # BRV 포인트 보너스
                bonus_brv = 50
                status['brave_points'] = status.get('brave_points', 0) + bonus_brv
                
                print(f"🎁 {companion_name}에게 학습 보상 지급: 경험치 +{bonus_exp}, BRV +{bonus_brv}")
                
                self._log_learning_event(companion_name, 'learning_reward', {
                    'bonus_exp': bonus_exp,
                    'bonus_brv': bonus_brv,
                    'reason': 'excellent_performance'
                })
                
        except Exception as e:
            print(f"❌ AI 개선 보상 오류: {e}")
    
    def _provide_ai_guidance(self, companion_name):
        """AI 지도 제공"""
        try:
            companion = next((c for c in self.ai_companions if c['name'] == companion_name), None)
            if not companion:
                return
            
            personality = companion['ai_personality']
            
            # 성격별 개선 가이드
            guidance_tips = {
                '용감한': "전투에서 너무 무모하게 돌진하지 말고 상황을 파악해보세요.",
                '신중한': "때로는 과감한 행동도 필요합니다. 기회를 놓치지 마세요.",
                '지원형': "동료를 도우면서도 자신의 안전도 챙기세요.",
                '독립적': "팀워크도 중요합니다. 동료와의 협력을 고려해보세요.",
                '적응형': "상황 적응은 좋지만, 일관성 있는 전략도 필요합니다."
            }
            
            tip = guidance_tips.get(personality, "균형 잡힌 접근을 시도해보세요.")
            print(f"💭 {companion_name}에게 조언: {tip}")
            
            self._log_learning_event(companion_name, 'guidance_provided', {
                'personality': personality,
                'tip': tip,
                'reason': 'performance_improvement_needed'
            })
            
        except Exception as e:
            print(f"❌ AI 지도 제공 오류: {e}")
    
    def _log_learning_event(self, character_name, event_type, data):
        """학습 이벤트 로깅"""
        try:
            import time
            
            event = {
                'timestamp': time.time(),
                'character': character_name,
                'event_type': event_type,
                'data': data
            }
            
            self.learning_data['interaction_logs'].append(event)
            
            # 로그 크기 관리 (최근 100개만 유지)
            if len(self.learning_data['interaction_logs']) > 100:
                self.learning_data['interaction_logs'] = self.learning_data['interaction_logs'][-100:]
                
        except Exception as e:
            print(f"❌ 학습 이벤트 로깅 오류: {e}")
    
    def _save_learning_progress(self):
        """학습 진행도 저장"""
        try:
            learning_save_data = {
                'learning_data': self.learning_data,
                'ai_improvement_records': self.ai_improvement_records,
                'save_timestamp': time.time()
            }
            
            import json
            learning_file = "ai_learning_progress.json"
            
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(learning_save_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 디버그 출력 (너무 빈번하지 않게)
            if hasattr(self, '_last_save_log'):
                import time
                if time.time() - self._last_save_log > 60:  # 1분마다만 출력
                    print("💾 AI 학습 진행도 자동 저장 완료")
                    self._last_save_log = time.time()
            else:
                import time
                self._last_save_log = time.time()
                
        except Exception as e:
            print(f"❌ 학습 진행도 저장 실패: {e}")
    
    def _load_learning_progress(self):
        """학습 진행도 로드"""
        try:
            import json
            learning_file = "ai_learning_progress.json"
            
            with open(learning_file, 'r', encoding='utf-8') as f:
                learning_save_data = json.load(f)
            
            self.learning_data = learning_save_data.get('learning_data', {})
            self.ai_improvement_records = learning_save_data.get('ai_improvement_records', {})
            
            print("📖 AI 학습 진행도 로드 완료")
            
            # 로드된 데이터 확인
            total_logs = len(self.learning_data.get('interaction_logs', []))
            total_ais = len(self.ai_improvement_records)
            
            if total_logs > 0 or total_ais > 0:
                print(f"   로드된 학습 로그: {total_logs}개, 추적 중인 AI: {total_ais}명")
                
        except FileNotFoundError:
            print("💡 이전 학습 데이터가 없습니다. 새로 시작합니다.")
        except Exception as e:
            print(f"⚠️ 학습 진행도 로드 실패: {e}")
    
    def show_learning_status(self):
        """AI 학습 상태 보기"""
        try:
            print(f"\n{'='*60}")
            print(f"🧠 AI 백그라운드 학습 상태")
            print(f"{'='*60}")
            
            # 학습 시스템 상태
            learning_status = "활성화" if self.learning_active else "비활성화"
            print(f"📊 학습 시스템: {learning_status}")
            
            if not self.ai_improvement_records:
                print("💤 아직 학습 기록이 없습니다.")
                return
            
            # AI별 학습 현황
            print(f"\n👥 AI 동료 학습 현황:")
            for companion_name, record in self.ai_improvement_records.items():
                print(f"\n🤖 {companion_name}:")
                print(f"   📚 학습 세션: {record['learning_sessions']}회")
                print(f"   ⚔️ 전투 경험: {record['battle_experience']} EXP")
                print(f"   📈 성공률: {record['success_rate']:.1%}")
                
                # 최근 성격 진화
                if record['personality_evolution']:
                    recent = record['personality_evolution'][-1]
                    print(f"   🎭 현재 성격: {recent['personality']}")
            
            # 최근 학습 이벤트
            print(f"\n📋 최근 학습 이벤트 (최근 5개):")
            recent_logs = self.learning_data.get('interaction_logs', [])[-5:]
            
            if recent_logs:
                for log in recent_logs:
                    import datetime
                    timestamp = datetime.datetime.fromtimestamp(log['timestamp'])
                    print(f"   {timestamp.strftime('%H:%M:%S')} - {log['character']}: {log['event_type']}")
            else:
                print("   📝 아직 이벤트가 없습니다.")
            
            print(f"\n{'='*60}")
            
        except Exception as e:
            print(f"❌ 학습 상태 조회 오류: {e}")
    
    def show_learning_management_menu(self):
        """AI 학습 관리 메뉴"""
        while True:
            print(f"\n{'='*60}")
            print(f"🧠 AI 백그라운드 학습 관리")
            print(f"{'='*60}")
            
            # 현재 학습 상태 표시
            learning_status = "활성화 중" if self.learning_active else "비활성화"
            print(f"📊 학습 시스템 상태: {learning_status}")
            
            if self.ai_companions:
                ai_count = len(self.ai_companions)
                record_count = len(self.ai_improvement_records)
                print(f"🤖 학습 대상 AI: {ai_count}명 (기록된 AI: {record_count}명)")
            
            print(f"\n1. 📊 학습 상태 상세 보기")
            print(f"2. ▶️ 백그라운드 학습 시작")
            print(f"3. ⏸️ 백그라운드 학습 중지")
            print(f"4. 🔄 학습 데이터 초기화")
            print(f"5. 💾 학습 진행도 수동 저장")
            print(f"6. 📂 학습 데이터 백업")
            print(f"0. 🔙 메인 메뉴로 돌아가기")
            
            choice = safe_input("\n선택하세요: ", 2).strip()
            
            if choice == "1":
                self.show_learning_status()
            elif choice == "2":
                if not self.learning_active:
                    self.start_background_learning()
                    print("✅ 백그라운드 학습이 시작되었습니다.")
                else:
                    print("⚠️ 백그라운드 학습이 이미 실행 중입니다.")
            elif choice == "3":
                if self.learning_active:
                    self.stop_background_learning()
                    print("✅ 백그라운드 학습을 중지했습니다.")
                else:
                    print("💤 백그라운드 학습이 실행 중이 아닙니다.")
            elif choice == "4":
                confirm = input("\n⚠️ 모든 학습 데이터를 초기화하시겠습니까? (Y/N): ").strip().lower()
                if confirm in ['y', 'yes', '예', 'ㅇ']:
                    self._reset_learning_data()
                    print("🔄 학습 데이터가 초기화되었습니다.")
                else:
                    print("❌ 초기화를 취소했습니다.")
            elif choice == "5":
                self._save_learning_progress()
                print("💾 학습 진행도를 수동으로 저장했습니다.")
            elif choice == "6":
                self._backup_learning_data()
            elif choice == "0":
                break
            else:
                print("❌ 잘못된 선택입니다.")
            
            if choice != "0":
                input("\nEnter를 눌러 계속...")
    
    def _reset_learning_data(self):
        """학습 데이터 초기화"""
        try:
            self.learning_data = {
                'battle_experiences': [],
                'personality_adjustments': {},
                'success_patterns': {},
                'failure_analysis': {},
                'interaction_logs': []
            }
            self.ai_improvement_records = {}
            
            # 파일도 삭제
            import os
            if os.path.exists("ai_learning_progress.json"):
                os.remove("ai_learning_progress.json")
            
            print("✅ 학습 데이터 초기화 완료")
            
        except Exception as e:
            print(f"❌ 학습 데이터 초기화 실패: {e}")
    
    def _backup_learning_data(self):
        """학습 데이터 백업"""
        try:
            import json
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"ai_learning_backup_{timestamp}.json"
            
            backup_data = {
                'backup_timestamp': timestamp,
                'learning_data': self.learning_data,
                'ai_improvement_records': self.ai_improvement_records,
                'ai_companions_count': len(self.ai_companions)
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ 학습 데이터 백업 완료: {backup_file}")
            
        except Exception as e:
            print(f"❌ 학습 데이터 백업 실패: {e}")
    
    # ========================================
    # 🎯 최종 시스템 통합 및 개선 (6단계 완성)
    # ========================================
    
    def show_system_status(self):
        """전체 시스템 상태 표시"""
        try:
            print(f"\n{'='*70}")
            print(f"🎮 Dawn of Stellar - 하이브리드 AI 멀티플레이어 시스템 상태")
            print(f"{'='*70}")
            
            # 1단계: 27직업 시스템 상태
            job_count = len(self.job_modifiers) if hasattr(self, 'job_modifiers') else 27
            print(f"✅ 1단계 - 27직업 시스템: {job_count}개 직업 지원")
            
            # 2단계: 한글 입력 시스템 상태
            korean_available = "한글 입력 시스템" in str(self.__class__.__dict__)
            korean_status = "활성화" if korean_available else "기본 입력"
            print(f"✅ 2단계 - 스마트 한글 입력: {korean_status}")
            
            # 3단계: 특성 선택 시스템 상태
            trait_available = hasattr(self, 'setup_traits_and_passives')
            trait_status = "사용 가능" if trait_available else "미지원"
            print(f"✅ 3단계 - 특성 선택 시스템: {trait_status}")
            
            # 4단계: 게임 통합 시스템 상태
            game_integration = SYSTEMS_AVAILABLE
            game_status = "게임 모듈 연동 가능" if game_integration else "독립 모드"
            print(f"✅ 4단계 - 게임 통합 시스템: {game_status}")
            
            # 5단계: 백그라운드 학습 시스템 상태
            learning_status = "실행 중" if self.learning_active else "대기 중"
            learning_records = len(self.ai_improvement_records)
            print(f"✅ 5단계 - 백그라운드 학습: {learning_status} (AI 기록: {learning_records}개)")
            
            # 6단계: 최종 시스템 상태
            print(f"✅ 6단계 - 하이브리드 시스템: 완전 통합 완료")
            
            # 파티 현황
            print(f"\n📊 현재 파티 현황:")
            if self.player_character:
                print(f"   👤 플레이어: {self.player_character['name']} ({self.player_character['character_class']})")
            else:
                print(f"   👤 플레이어: 미설정")
            
            print(f"   🤖 AI 동료: {len(self.ai_companions)}명")
            for i, companion in enumerate(self.ai_companions, 1):
                personality = companion.get('ai_personality', '알 수 없음')
                print(f"      {i}. {companion['name']} ({companion['character_class']}) - {personality}")
            
            # 고급 기능 상태
            print(f"\n🔧 고급 기능 상태:")
            print(f"   🔒 멀티플레이어 세이브: {len(self.character_locks)}개 캐릭터 잠금")
            print(f"   🆘 모험 백업: {len(self.adventure_backups) if hasattr(self, 'adventure_backups') else 0}개 백업")
            print(f"   🛡️ 안전 종료: {'활성화' if SAFE_EXIT_AVAILABLE else '비활성화'}")
            
            # 시스템 권장사항
            print(f"\n💡 시스템 권장사항:")
            if not self.player_character:
                print(f"   1. 플레이어 캐릭터를 생성하세요")
            if not self.ai_companions:
                print(f"   2. AI 동료를 추가하세요")
            if not self.learning_active and self.ai_companions:
                print(f"   3. 백그라운드 학습을 시작하세요")
            if self.player_character and self.ai_companions:
                print(f"   ✨ 모든 준비가 완료되었습니다! 게임을 시작할 수 있습니다.")
            
            print(f"\n{'='*70}")
            
        except Exception as e:
            print(f"❌ 시스템 상태 조회 오류: {e}")
    
    def show_quick_start_guide(self):
        """빠른 시작 가이드"""
        try:
            print(f"\n{'='*70}")
            print(f"🚀 Dawn of Stellar 하이브리드 AI 멀티플레이어 - 빠른 시작 가이드")
            print(f"{'='*70}")
            
            print(f"\n📋 기본 설정 (필수):")
            print(f"   1️⃣ 플레이어 캐릭터 생성 → 메뉴 '1번'")
            print(f"   2️⃣ AI 동료 추가 → 메뉴 '2번' (자동 생성) 또는 '3번' (프리셋)")
            print(f"   3️⃣ 파티 확인 → 메뉴 '4번'")
            
            print(f"\n🎮 게임 플레이:")
            print(f"   🗺️ 간단한 모험 → 메뉴 '6번' (시뮬레이션 모드)")
            if SYSTEMS_AVAILABLE:
                print(f"   🎯 실제 게임 → 메뉴 '7번' (게임 모듈 연동)")
            
            print(f"\n🧠 AI 학습 관리:")
            print(f"   📊 학습 상태 확인 → 메뉴 '8번'")
            print(f"   ▶️ 백그라운드 학습 시작 → 메뉴 '8번' → '2번'")
            print(f"   🎭 AI 성격 조정 → 메뉴 '9번'")
            
            print(f"\n💾 데이터 관리:")
            print(f"   💾 파티 데이터 저장 → 메뉴 '10번'")
            print(f"   📂 파티 데이터 로드 → 메뉴 '11번'")
            print(f"   🔒 세이브 관리 → 메뉴 '15번'")
            
            print(f"\n🌟 특별 기능:")
            print(f"   ✨ 특성 선택: 게임 시작 시 자동으로 제공")
            print(f"   🌐 한글 입력: 모든 입력창에서 영어→한글 자동 변환")
            print(f"   🤖 27개 직업: 각 직업마다 고유한 AI 성격")
            print(f"   📈 학습 성장: AI가 플레이하면서 자동으로 개선")
            
            print(f"\n⚡ 추천 시작 순서:")
            print(f"   1. 메뉴 '1번' → 플레이어 캐릭터 생성")
            print(f"   2. 메뉴 '2번' → AI 동료 자동 생성")
            print(f"   3. 메뉴 '8번' → '2번' → 백그라운드 학습 시작")
            print(f"   4. 메뉴 '6번' 또는 '7번' → 게임 시작")
            print(f"   5. 게임 플레이하면서 AI가 자동으로 학습 및 성장!")
            
            print(f"\n{'='*70}")
            
        except Exception as e:
            print(f"❌ 빠른 시작 가이드 오류: {e}")
    
    def emergency_save_all(self):
        """응급 전체 저장 (종료 시 호출)"""
        try:
            print("🆘 응급 전체 저장을 실행합니다...")
            
            # 파티 데이터 저장
            self.save_party_data()
            
            # 학습 진행도 저장
            if hasattr(self, '_save_learning_progress'):
                self._save_learning_progress()
            
            # 백그라운드 학습 중지
            if self.learning_active:
                self.stop_background_learning()
            
            # 모험 세션 정리
            if self.current_adventure_id:
                self.end_adventure_session()
            
            print("✅ 응급 저장 완료")
            
        except Exception as e:
            print(f"❌ 응급 저장 실패: {e}")
    
    def safe_cleanup(self):
        """안전한 정리 작업 (안전 종료 시스템용)"""
        try:
            print("🧹 시스템 정리를 시작합니다...")
            
            # 모든 데이터 저장
            self.emergency_save_all()
            
            print("✅ 시스템 정리 완료")
            
        except Exception as e:
            print(f"❌ 시스템 정리 실패: {e}")

    def manage_multiplayer_saves(self):
        """멀티플레이어 세이브 관리 메뉴"""
        while True:
            print("\n" + "="*60)
            print("🔒 멀티플레이어 세이브 시스템 관리")
            print("="*60)
            
            # 현재 상태 표시
            if self.current_adventure_id:
                print(f"🎮 활성 모험: {self.current_adventure_id}")
                locked_count = len(self.character_locks)
                print(f"🔒 잠긴 캐릭터: {locked_count}개")
            else:
                print("💤 활성 모험 없음")
            
            # 백업 파일 수 표시
            backup_files = list(self.adventure_backups_dir.glob("emergency_backup_*.json"))
            print(f"🆘 응급 백업: {len(backup_files)}개")
            
            # 전용 세이브 파일 수 표시
            exclusive_saves = list(self.multiplayer_saves_dir.glob("mp_exclusive_*.json"))
            print(f"💾 전용 세이브: {len(exclusive_saves)}개")
            
            print("\n1. 📋 잠긴 캐릭터 목록 보기")
            print("2. 🔓 특정 캐릭터 잠금 해제")
            print("3. 🔒 만료된 잠금 정리")
            print("4. 🆘 응급 백업 관리")
            print("5. 💾 전용 세이브 검증")
            print("6. 🗑️ 오래된 파일 정리")
            print("7. 📊 세이브 시스템 통계")
            print("0. 🔙 메인 메뉴로 돌아가기")
            
            choice = safe_input("\n선택하세요 (0-7): ", 2).strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self._show_locked_characters()
            elif choice == "2":
                self._manual_unlock_character()
            elif choice == "3":
                self._cleanup_expired_locks()
            elif choice == "4":
                self._manage_emergency_backups()
            elif choice == "5":
                self._verify_exclusive_saves()
            elif choice == "6":
                self._cleanup_old_files()
            elif choice == "7":
                self._show_save_system_stats()
            else:
                print("❌ 0-7 사이의 숫자를 입력해주세요.")
            
            if choice != "0":
                input("\nEnter를 눌러 계속...")
    
    def _show_locked_characters(self):
        """잠긴 캐릭터 목록 표시"""
        if not self.character_locks:
            print("✅ 잠긴 캐릭터가 없습니다.")
            return
        
        print(f"\n🔒 잠긴 캐릭터 목록 ({len(self.character_locks)}개):")
        print("-" * 60)
        
        for char_hash, lock_info in self.character_locks.items():
            char_name = lock_info.get("character_name", "알 수 없음")
            char_class = lock_info.get("character_class", "알 수 없음")
            adventure_id = lock_info.get("adventure_id", "알 수 없음")
            lock_time = lock_info.get("lock_time", 0)
            
            # 잠금 시간 계산
            lock_datetime = datetime.fromtimestamp(lock_time)
            elapsed = datetime.now() - lock_datetime
            
            print(f"• {char_name} ({char_class})")
            print(f"  📅 모험: {adventure_id}")
            print(f"  ⏰ 잠금 시간: {lock_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  ⌛ 경과 시간: {elapsed}")
            print()
    
    def _manual_unlock_character(self):
        """특정 캐릭터 수동 잠금 해제"""
        if not self.character_locks:
            print("✅ 잠긴 캐릭터가 없습니다.")
            return
        
        print("\n🔓 잠금 해제할 캐릭터 선택:")
        
        lock_items = list(self.character_locks.items())
        for i, (char_hash, lock_info) in enumerate(lock_items, 1):
            char_name = lock_info.get("character_name", "알 수 없음")
            char_class = lock_info.get("character_class", "알 수 없음")
            adventure_id = lock_info.get("adventure_id", "알 수 없음")
            
            print(f"{i}. {char_name} ({char_class}) - {adventure_id}")
        
        try:
            choice = int(input(f"\n선택 (1-{len(lock_items)}): ")) - 1
            
            if 0 <= choice < len(lock_items):
                char_hash, lock_info = lock_items[choice]
                char_name = lock_info.get("character_name", "알 수 없음")
                
                confirm = input(f"\n'{char_name}' 잠금을 해제하시겠습니까? (Y/N): ").strip().lower()
                
                if confirm in ['y', 'yes', '예', 'ㅇ']:
                    del self.character_locks[char_hash]
                    self.save_character_locks()
                    print(f"✅ '{char_name}' 잠금이 해제되었습니다.")
                else:
                    print("❌ 해제를 취소했습니다.")
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _cleanup_expired_locks(self):
        """만료된 잠금 정리"""
        current_time = datetime.now().timestamp()
        expired_locks = []
        
        for char_hash, lock_info in self.character_locks.items():
            if current_time - lock_info.get("lock_time", 0) > 86400:  # 24시간
                expired_locks.append(char_hash)
        
        if not expired_locks:
            print("✅ 만료된 잠금이 없습니다.")
            return
        
        print(f"\n🗑️ 만료된 잠금 {len(expired_locks)}개 발견")
        
        for char_hash in expired_locks:
            lock_info = self.character_locks[char_hash]
            char_name = lock_info.get("character_name", "알 수 없음")
            print(f"• {char_name}")
        
        confirm = input(f"\n이 잠금들을 모두 해제하시겠습니까? (Y/N): ").strip().lower()
        
        if confirm in ['y', 'yes', '예', 'ㅇ']:
            for char_hash in expired_locks:
                del self.character_locks[char_hash]
            
            self.save_character_locks()
            print(f"✅ {len(expired_locks)}개의 만료된 잠금을 해제했습니다.")
        else:
            print("❌ 정리를 취소했습니다.")
    
    def _manage_emergency_backups(self):
        """응급 백업 관리"""
        backup_files = list(self.adventure_backups_dir.glob("emergency_backup_*.json"))
        
        if not backup_files:
            print("📂 응급 백업이 없습니다.")
            return
        
        print(f"\n🆘 응급 백업 파일 ({len(backup_files)}개):")
        print("-" * 60)
        
        # 최신순 정렬
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for i, backup_file in enumerate(backup_files[:10], 1):  # 최신 10개만 표시
            stat = backup_file.stat()
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"{i}. {backup_file.name}")
            print(f"   📅 생성: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   📦 크기: {size:,} bytes")
            print()
        
        if len(backup_files) > 10:
            print(f"... 외 {len(backup_files) - 10}개")
        
        print("\n1. 🔄 특정 백업에서 복원")
        print("2. 🗑️ 오래된 백업 삭제")
        print("0. 🔙 돌아가기")
        
        choice = input("\n선택하세요: ").strip()
        
        if choice == "1":
            try:
                backup_choice = int(input(f"복원할 백업 번호 (1-{min(len(backup_files), 10)}): ")) - 1
                
                if 0 <= backup_choice < min(len(backup_files), 10):
                    backup_path = str(backup_files[backup_choice])
                    
                    if self.restore_from_backup(backup_path):
                        print("✅ 백업 복원이 완료되었습니다.")
                else:
                    print("❌ 잘못된 선택입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
        
        elif choice == "2":
            old_backups = backup_files[5:]  # 최신 5개 제외
            
            if old_backups:
                print(f"\n🗑️ 오래된 백업 {len(old_backups)}개를 삭제하시겠습니까?")
                confirm = input("Y/N: ").strip().lower()
                
                if confirm in ['y', 'yes', '예', 'ㅇ']:
                    deleted_count = 0
                    for backup_file in old_backups:
                        try:
                            backup_file.unlink()
                            deleted_count += 1
                        except Exception as e:
                            print(f"⚠️ {backup_file.name} 삭제 실패: {e}")
                    
                    print(f"✅ {deleted_count}개의 오래된 백업을 삭제했습니다.")
            else:
                print("✅ 삭제할 오래된 백업이 없습니다.")
    
    def _verify_exclusive_saves(self):
        """전용 세이브 파일 검증"""
        exclusive_saves = list(self.multiplayer_saves_dir.glob("mp_exclusive_*.json"))
        
        if not exclusive_saves:
            print("📂 전용 세이브 파일이 없습니다.")
            return
        
        print(f"\n💾 전용 세이브 파일 검증 ({len(exclusive_saves)}개):")
        print("-" * 60)
        
        valid_count = 0
        invalid_count = 0
        
        for save_file in exclusive_saves:
            is_valid, message = self.validate_save_integrity(str(save_file))
            
            if is_valid:
                print(f"✅ {save_file.name}")
                valid_count += 1
            else:
                print(f"❌ {save_file.name} - {message}")
                invalid_count += 1
        
        print(f"\n📊 검증 결과:")
        print(f"✅ 유효: {valid_count}개")
        print(f"❌ 무효: {invalid_count}개")
        
        if invalid_count > 0:
            print("\n⚠️ 무효한 파일들을 삭제하시겠습니까?")
            confirm = input("Y/N: ").strip().lower()
            
            if confirm in ['y', 'yes', '예', 'ㅇ']:
                deleted_count = 0
                for save_file in exclusive_saves:
                    is_valid, _ = self.validate_save_integrity(str(save_file))
                    if not is_valid:
                        try:
                            save_file.unlink()
                            deleted_count += 1
                            print(f"🗑️ {save_file.name} 삭제됨")
                        except Exception as e:
                            print(f"⚠️ {save_file.name} 삭제 실패: {e}")
                
                print(f"✅ {deleted_count}개의 무효한 파일을 삭제했습니다.")
    
    def _cleanup_old_files(self):
        """오래된 파일 정리"""
        print("\n🗑️ 시스템 파일 정리:")
        print("-" * 40)
        
        # 30일 이상 된 백업 파일 찾기
        cutoff_time = datetime.now().timestamp() - (30 * 24 * 3600)  # 30일
        old_backups = []
        
        for backup_file in self.adventure_backups_dir.glob("emergency_backup_*.json"):
            if backup_file.stat().st_mtime < cutoff_time:
                old_backups.append(backup_file)
        
        # 오래된 세이브 파일 찾기 (60일)
        cutoff_time_saves = datetime.now().timestamp() - (60 * 24 * 3600)  # 60일
        old_saves = []
        
        for save_file in self.multiplayer_saves_dir.glob("mp_exclusive_*.json"):
            if save_file.stat().st_mtime < cutoff_time_saves:
                old_saves.append(save_file)
        
        print(f"📦 30일 이상 된 백업: {len(old_backups)}개")
        print(f"💾 60일 이상 된 세이브: {len(old_saves)}개")
        
        total_old = len(old_backups) + len(old_saves)
        
        if total_old == 0:
            print("✅ 정리할 오래된 파일이 없습니다.")
            return
        
        confirm = input(f"\n{total_old}개의 오래된 파일을 삭제하시겠습니까? (Y/N): ").strip().lower()
        
        if confirm in ['y', 'yes', '예', 'ㅇ']:
            deleted_count = 0
            
            for old_file in old_backups + old_saves:
                try:
                    old_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️ {old_file.name} 삭제 실패: {e}")
            
            print(f"✅ {deleted_count}개의 오래된 파일을 삭제했습니다.")
        else:
            print("❌ 정리를 취소했습니다.")
    
    def _show_save_system_stats(self):
        """세이브 시스템 통계 표시"""
        print("\n📊 멀티플레이어 세이브 시스템 통계:")
        print("="*60)
        
        # 캐릭터 잠금 통계
        print(f"🔒 잠긴 캐릭터: {len(self.character_locks)}개")
        
        if self.character_locks:
            adventures = set()
            for lock_info in self.character_locks.values():
                adventures.add(lock_info.get("adventure_id", "알 수 없음"))
            print(f"🎮 활성 모험: {len(adventures)}개")
        
        # 백업 파일 통계
        backup_files = list(self.adventure_backups_dir.glob("emergency_backup_*.json"))
        print(f"🆘 응급 백업: {len(backup_files)}개")
        
        if backup_files:
            total_backup_size = sum(f.stat().st_size for f in backup_files)
            print(f"💾 백업 총 크기: {total_backup_size:,} bytes ({total_backup_size / 1024 / 1024:.2f} MB)")
        
        # 전용 세이브 통계
        exclusive_saves = list(self.multiplayer_saves_dir.glob("mp_exclusive_*.json"))
        print(f"💾 전용 세이브: {len(exclusive_saves)}개")
        
        if exclusive_saves:
            total_save_size = sum(f.stat().st_size for f in exclusive_saves)
            print(f"💾 세이브 총 크기: {total_save_size:,} bytes ({total_save_size / 1024 / 1024:.2f} MB)")
            
            # 유효성 검사
            valid_saves = 0
            for save_file in exclusive_saves:
                is_valid, _ = self.validate_save_integrity(str(save_file))
                if is_valid:
                    valid_saves += 1
            
            print(f"✅ 유효한 세이브: {valid_saves}개")
            print(f"❌ 무효한 세이브: {len(exclusive_saves) - valid_saves}개")
        
        # 현재 상태
        print(f"\n🎯 현재 상태:")
        if self.current_adventure_id:
            print(f"🎮 활성 모험: {self.current_adventure_id}")
        else:
            print("💤 활성 모험 없음")
        
        print(f"📁 캐릭터 프리셋: {len(self.character_presets)}개")
        print(f"🤖 로드된 AI 동료: {len(self.ai_companions)}개")

def main():
    """메인 실행 함수"""
    system = PlayerCentricAISystem()
    system.main_menu()

if __name__ == "__main__":
    main()
