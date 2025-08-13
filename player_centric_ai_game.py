#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Dawn of Stellar - 플레이어 중심 AI 멀티플레이어 시스템
플레이어가 주도하고 AI가 지원하는 실용적인 게임 시스템 + 안전 종료
"""

import os
import sys
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

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
                                
                                # 추가 바이트 수집 (최대 3바이트까지)
                                for _ in range(2):  # UTF-8 한글은 최대 3바이트
                                    if msvcrt.kbhit():
                                        next_char = msvcrt.getch()
                                        if ord(next_char) > 127:
                                            extended_chars.append(next_char)
                                        else:
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
    """한글 안전 입력 (이름 등에 사용)"""
    print(f"\n{prompt}")
    print("💡 입력 팁:")
    print("  • 한글 입력 후 Enter를 눌러주세요")
    print("  • 입력이 안 되면 ESC를 누르고 영어로 입력하세요")
    print("  • Ctrl+C를 누르면 취소됩니다")
    
    result = safe_input("👤 입력: ", max_length)
    
    if result == "EXIT_COMMAND":
        return ""
    
    return result

# 기존 시스템들 간단 import python3
"""
🎮 Dawn of Stellar - 플레이어 중심 AI 멀티플레이어 시스템
플레이어가 주도하고 AI가 지원하는 실용적인 게임 시스템
"""

import os
import sys
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

# 기존 시스템들 import
try:
    from complete_27_job_system import job_system
    from ai_training_system import training_system
    from ai_27job_character_creator import character_creator
    from game.easy_character_creator import EasyCharacterCreator
    SYSTEMS_AVAILABLE = True
    CHARACTER_CREATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 일부 모듈을 찾을 수 없습니다: {e}")
    SYSTEMS_AVAILABLE = False
    CHARACTER_CREATOR_AVAILABLE = False

class PlayerCentricAISystem:
    """플레이어 중심 AI 멀티플레이어 시스템"""
    
    def __init__(self):
        self.player_character = None
        self.ai_companions = []
        self.party_size = 4
        
        # 안전 종료 시스템 설정
        if SAFE_EXIT_AVAILABLE:
            setup_safe_exit(self, 'safe_cleanup')
            print("🛡️ 안전 종료 시스템 연동 완료")
        
        self.available_jobs = [
            "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사",
            "몽크", "바드", "네크로맨서", "용기사", "검성", "정령술사",
            "시간술사", "연금술사", "차원술사", "마검사", "기계공학자", "무당",
            "암살자", "해적", "사무라이", "드루이드", "철학자", "검투사",
            "기사", "신관", "광전사"
        ]
        self.job_descriptions = {
            # 전투 직업군
            "전사": "높은 방어력과 HP를 가진 전선 탱커. 초보자에게 추천!",
            "아크메이지": "강력한 마법 공격을 담당하는 마법사. 원소 마법의 달인",
            "궁수": "원거리에서 정확한 공격을 하는 사수. 관통사격과 지원사격",
            "도적": "빠른 속도와 크리티컬로 승부하는 암살자. 독과 은신술",
            "성기사": "신성한 힘으로 아군을 보호하는 성전사. 치유와 축복",
            "암흑기사": "흡혈과 저주로 적을 압도하는 다크 워리어",
            "몽크": "맨손 격투의 달인. 연속 공격과 표식 시스템",
            "바드": "음악으로 전장을 지배하는 음유시인. 사기와 디버프",
            
            # 마법 직업군
            "네크로맨서": "죽음의 마법을 다루는 흑마법사. 생명력 흡수",
            "용기사": "드래곤의 힘을 빌린 전사. 화염 공격과 브레스",
            "검성": "검기를 다루는 검술의 달인. 일섬과 검기 베기",
            "정령술사": "4원소를 조합하는 마법사. 원소 융합술",
            "시간술사": "시간을 조작하는 신비한 마법사. 시간 정지",
            "연금술사": "화학 반응으로 폭발을 일으키는 과학자",
            "차원술사": "차원을 조작하는 마법사. 차원 균열",
            "마검사": "마법과 검술을 결합한 하이브리드 전사",
            "기계공학자": "첨단 기술을 활용하는 엔지니어. 레이저와 장비",
            "무당": "영혼을 다루는 신비한 술사. 영혼 공격",
            
            # 특수 직업군
            "암살자": "그림자를 조작하는 어둠의 암살자. 그림자 처형",
            "해적": "이도류와 보물을 다루는 바다의 영웅",
            "사무라이": "무사도 정신의 검사. 거합 베기",
            "드루이드": "자연의 힘을 빌린 현자. 자연 친화",
            "철학자": "논리와 지혜로 승부하는 현자. 진리 탐구",
            "검투사": "콜로세움의 왕. 투기장 기술",
            "기사": "창과 기마술의 달인. 성스러운 돌격",
            "신관": "신의 가호를 받은 성직자. 축복과 심판",
            "광전사": "광기로 싸우는 전사. 최후의 광기"
        }
        
        print("🎮 플레이어 중심 AI 멀티플레이어 시스템 초기화 완료")
    
    def safe_cleanup(self):
        """안전 종료 시 정리 작업"""
        print("🧹 플레이어 중심 시스템 안전 정리 시작...")
        
        try:
            # 1. 현재 상태 응급 백업
            if SAFE_EXIT_AVAILABLE and (self.player_character or self.ai_companions):
                backup_data = {
                    "player_character": self.player_character,
                    "ai_companions": self.ai_companions,
                    "system_type": "player_centric"
                }
                emergency_backup(backup_data, "player_centric_system")
            
            # 2. 파티 데이터 자동 저장
            if self.player_character or self.ai_companions:
                self.save_party_data()
            
            print("✅ 플레이어 중심 시스템 안전 정리 완료")
            
        except Exception as e:
            print(f"❌ 플레이어 중심 시스템 정리 중 오류: {e}")
    
    def emergency_save_all(self):
        """응급 상황에서 모든 데이터 저장"""
        try:
            print("🆘 응급 데이터 저장 중...")
            
            # 파티 데이터 저장
            if self.player_character or self.ai_companions:
                self.save_party_data()
            
            print("✅ 응급 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ 응급 데이터 저장 실패: {e}")
    
    def create_player_character(self):
        """플레이어 캐릭터 생성 - 기존 27개 직업 시스템 활용"""
        print("\n" + "="*60)
        print("👤 플레이어 캐릭터 생성")
        print("="*60)
        
        if CHARACTER_CREATOR_AVAILABLE:
            print("🎭 27개 직업 시스템으로 캐릭터를 생성합니다...")
            print("💡 캐릭터 생성이 완료되면 자동으로 여기로 돌아옵니다.")
            print("\n🔄 캐릭터 생성 시스템 시작...")
            
            try:
                # ai_27job_character_creator 사용
                created_characters = character_creator.show_character_creation_menu()
                
                if created_characters and len(created_characters) > 0:
                    # 첫 번째 캐릭터를 플레이어로 설정
                    player_char = created_characters[0]
                    
                    # 플레이어 캐릭터 변환
                    self.player_character = {
                        "name": player_char.name,
                        "job": player_char.character_class,
                        "level": player_char.level,
                        "hp": player_char.current_hp,
                        "max_hp": player_char.max_hp,
                        "mp": player_char.current_mp,
                        "max_mp": player_char.max_mp,
                        "brv": getattr(player_char, 'brv', 100),
                        "max_brv": getattr(player_char, 'max_brv', 100),
                        "stats": {
                            "strength": player_char.strength,
                            "intelligence": player_char.intelligence,
                            "agility": player_char.agility,
                            "luck": player_char.luck,
                            "defense": getattr(player_char, 'defense', 10),
                            "resistance": getattr(player_char, 'resistance', 10),
                            "physical_attack": getattr(player_char, 'physical_attack', 15),
                            "magic_attack": getattr(player_char, 'magic_attack', 15),
                            "speed": getattr(player_char, 'speed', 10)
                        },
                        "skills": [skill.name for skill in player_char.skills] if hasattr(player_char, 'skills') else [],
                        "traits": [trait.name for trait in player_char.traits] if hasattr(player_char, 'traits') else [],
                        "is_player": True,
                        "original_character": player_char  # 원본 객체 저장
                    }
                    
                    print(f"\n🎉 {self.player_character['name']} ({self.player_character['job']}) 캐릭터가 생성되었습니다!")
                    self._display_character_info(self.player_character)
                    return self.player_character
                else:
                    print("❌ 캐릭터 생성이 취소되었습니다.")
                    return None
                    
            except Exception as e:
                print(f"❌ 캐릭터 생성 오류: {e}")
                print("📋 간단한 캐릭터 생성 모드로 전환합니다...")
                return self._create_simple_character()
        else:
            print("⚠️ 고급 캐릭터 생성 시스템을 사용할 수 없습니다.")
            print("📋 간단한 캐릭터 생성 모드를 사용합니다.")
            return self._create_simple_character()
    
    def _create_simple_character(self):
        """간단한 캐릭터 생성 (백업용)"""
        print("\n📋 간단한 캐릭터 생성")
        print("-" * 40)
        
        # 플레이어 이름 입력
        name = get_korean_safe_input("캐릭터 이름을 입력하세요 (또는 엔터로 기본값)", 20)
        if not name:
            name = f"용사_{random.randint(1000, 9999)}"
        
        # 간단한 6개 직업 선택
        simple_jobs = ["전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사"]
        
        print(f"\n직업을 선택하세요:")
        for i, job in enumerate(simple_jobs, 1):
            desc = self.job_descriptions.get(job, "특별한 능력을 가진 직업")
            print(f"{i}. {job} - {desc}")
        print("0. 🔙 메인 메뉴로 돌아가기")
        
        while True:
            try:
                choice = input(f"\n직업 선택 (0-{len(simple_jobs)}): ").strip()
                
                if choice == "0":
                    print("🔙 메인 메뉴로 돌아갑니다.")
                    return None
                
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(simple_jobs):
                    selected_job = simple_jobs[choice_num]
                    break
                else:
                    print(f"❌ 0-{len(simple_jobs)} 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
        
        # 간단한 캐릭터 생성
        self.player_character = {
            "name": name,
            "job": selected_job,
            "level": 1,
            "hp": 100,
            "max_hp": 100,
            "mp": 50,
            "max_mp": 50,
            "brv": 100,
            "max_brv": 100,
            "stats": {
                "strength": random.randint(10, 15),
                "intelligence": random.randint(10, 15),
                "agility": random.randint(10, 15),
                "luck": random.randint(10, 15),
                "defense": random.randint(8, 12),
                "resistance": random.randint(8, 12),
                "physical_attack": random.randint(12, 18),
                "magic_attack": random.randint(12, 18),
                "speed": random.randint(8, 12)
            },
            "skills": self._get_job_skills(selected_job),
            "traits": [],
            "is_player": True
        }
        
        print(f"\n✅ {name} ({selected_job}) 캐릭터가 생성되었습니다!")
        self._display_character_info(self.player_character)
        
        return self.player_character
    
    def _create_simple_character(self):
        """간단한 캐릭터 생성 (폴백)"""
        print("\n📝 간단한 캐릭터 생성 모드")
        
        # 플레이어 이름 입력
        name = get_korean_safe_input("캐릭터 이름을 입력하세요", 20)
        if not name:
            name = "용사"
        
        # 6개 기본 직업
        simple_jobs = ["전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사"]
        
        print(f"\n직업을 선택하세요:")
        for i, job in enumerate(simple_jobs, 1):
            print(f"{i}. {job}")
        
        while True:
            try:
                choice = int(input(f"\n직업 선택 (1-{len(simple_jobs)}): ")) - 1
                if 0 <= choice < len(simple_jobs):
                    selected_job = simple_jobs[choice]
                    break
                else:
                    print(f"❌ 1-{len(simple_jobs)} 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
        
        # 간단한 캐릭터 생성
        self.player_character = {
            "name": name,
            "job": selected_job,
            "level": 1,
            "hp": 100,
            "max_hp": 100,
            "mp": 50,
            "max_mp": 50,
            "stats": {
                "strength": random.randint(10, 15),
                "intelligence": random.randint(10, 15),
                "agility": random.randint(10, 15),
                "luck": random.randint(10, 15),
                "defense": random.randint(8, 12),
                "resistance": random.randint(8, 12)
            },
            "skills": ["기본공격", "방어", "회복"],
            "traits": [],
            "is_player": True
        }
        
        print(f"\n✅ {name} ({selected_job}) 캐릭터가 생성되었습니다!")
        self._display_character_info(self.player_character)
        
        return self.player_character
    
    def _get_job_description(self, job: str) -> str:
        """직업 설명 반환"""
        return self.job_descriptions.get(job, "특별한 능력을 가진 직업")
    
    def _get_job_skills(self, job: str) -> List[str]:
        """직업별 기본 스킬 반환 (new_skill_system.py 기반)"""
        skill_map = {
            # 전투 직업군
            "전사": ["적응형 강타", "방패 강타", "연속 베기", "전투 각성"],
            "아크메이지": ["화염구", "빙결탄", "마력 파동", "마력 폭발"],
            "궁수": ["정확한 사격", "삼연사", "관통사격", "정밀 관통사격"],
            "도적": ["독침", "독혈촉진", "암살", "맹독 강화"],
            "성기사": ["성스러운 타격", "축복", "심판의 빛", "성역 확장"],
            "암흑기사": ["흡혈 베기", "흡혈 강타", "생명력 흡수", "암흑 파동"],
            "몽크": ["연환 타격", "표식 강타", "폭렬권", "천공파"],
            "바드": ["음파 공격", "힐링 송", "전투가", "영혼의 노래"],
            
            # 마법 직업군
            "네크로맨서": ["생명력 흡수", "언데드 소환", "영혼 흡수", "죽음의 선고"],
            "용기사": ["화염 강타", "드래곤 브레스", "용린 방어", "드래곤 각성"],
            "검성": ["검기 베기", "일섬", "검기 파동", "무한검"],
            "정령술사": ["원소 탄환", "원소 융합", "정령 소환", "원소 폭풍"],
            "시간술사": ["시간 조작", "시간 정지", "시간 가속", "시간 역행"],
            "연금술사": ["화학 폭발", "산성 공격", "대폭발 반응", "원소 변환"],
            "차원술사": ["차원 균열", "차원 붕괴", "차원 이동", "차원 폭풍"],
            "마검사": ["마법검기", "마검 오의", "마력 강화", "검마 융합"],
            "기계공학자": ["레이저 사격", "메가 레이저", "장비 조작", "자기장 조작"],
            "무당": ["영혼 타격", "영혼 분리", "영혼 치유", "영혼 폭발"],
            
            # 특수 직업군
            "암살자": ["그림자 강타", "그림자 처형", "은신", "그림자 분신"],
            "해적": ["이도류 난타", "해적의 보물", "선상 전투", "보물 탐지"],
            "사무라이": ["거합 베기", "무사도 비의", "집중", "검혼"],
            "드루이드": ["자연의 분노", "자연의 심판", "치유", "자연 친화"],
            "철학자": ["논리적 반박", "진리의 깨달음", "지혜", "철학적 사고"],
            "검투사": ["투기장 기술", "패링", "명예의 일격", "콜로세움의 왕"],
            "기사": ["창 돌격", "수호의 맹세", "기사도", "성스러운 돌격"],
            "신관": ["축복의 빛", "신의 심판", "성스러운 치유", "신성 마법"],
            "광전사": ["분노의 폭발", "피의 방패", "흡혈 강타", "최후의 광기"]
        }
        return skill_map.get(job, ["기본 공격", "방어", "회복"])
    
    def create_ai_companions(self):
        """AI 동료들 자동 생성 - 기존 시스템 활용"""
        print(f"\n🤖 AI 동료 {self.party_size - 1}명을 자동 생성합니다...")
        
        if CHARACTER_CREATOR_AVAILABLE:
            try:
                # 기존 캐릭터 생성 시스템으로 AI 동료들 생성
                print("🎭 27개 직업 시스템으로 AI 동료를 생성합니다...")
                
                # 플레이어 직업 제외
                player_job = self.player_character["job"] if self.player_character else None
                
                self.ai_companions = []
                
                for i in range(self.party_size - 1):
                    print(f"\n🤖 AI 동료 {i+1}번 생성 중...")
                    
                    # AI 자동 생성 모드로 캐릭터 생성
                    ai_characters = character_creator.create_ai_characters(1, exclude_jobs=[player_job] if player_job else [])
                    
                    if ai_characters and len(ai_characters) > 0:
                        ai_char = ai_characters[0]
                        
                        # AI 동료 변환
                        ai_companion = {
                            "name": ai_char.name,
                            "job": ai_char.character_class,
                            "level": ai_char.level,
                            "hp": ai_char.current_hp,
                            "max_hp": ai_char.max_hp,
                            "mp": ai_char.current_mp,
                            "max_mp": ai_char.max_mp,
                            "stats": {
                                "strength": ai_char.strength,
                                "intelligence": ai_char.intelligence,
                                "agility": ai_char.agility,
                                "luck": ai_char.luck,
                                "defense": ai_char.defense,
                                "resistance": ai_char.resistance
                            },
                            "skills": [skill.name for skill in ai_char.skills] if hasattr(ai_char, 'skills') else [],
                            "traits": [trait.name for trait in ai_char.traits] if hasattr(ai_char, 'traits') else [],
                            "is_player": False,
                            "ai_personality": random.choice(["용감한", "신중한", "지혜로운", "활발한", "냉정한"]),
                            "original_character": ai_char  # 원본 객체 저장
                        }
                        
                        self.ai_companions.append(ai_companion)
                        print(f"   ✅ {ai_companion['name']} ({ai_companion['job']}) - {ai_companion['ai_personality']} 성격")
                    else:
                        # 폴백: 간단한 AI 생성
                        self._create_simple_ai_companion(i)
                
                print(f"\n🎉 고급 파티 구성 완료! 총 {len(self.ai_companions) + 1}명")
                if self.ai_companions:
                    jobs = [comp['job'] for comp in self.ai_companions]
                    print(f"   파티 구성: {player_job} (플레이어) + {', '.join(jobs)}")
                    
            except Exception as e:
                print(f"⚠️ 고급 AI 생성 실패: {e}")
                self._create_simple_ai_companions()
        else:
            self._create_simple_ai_companions()
    
    def _create_simple_ai_companions(self):
        """간단한 AI 동료 생성 (폴백)"""
        print("\n📝 간단한 AI 생성 모드")
        
        player_job = self.player_character["job"] if self.player_character else None
        available_for_ai = [job for job in self.available_jobs if job != player_job]
        
        self.ai_companions = []
        
        for i in range(self.party_size - 1):
            self._create_simple_ai_companion(i, available_for_ai)
        
        print(f"\n🎉 간단한 파티 구성 완료! 총 {len(self.ai_companions) + 1}명")
    
    def _create_simple_ai_companion(self, index: int, available_jobs: List[str] = None):
        """단일 간단 AI 동료 생성"""
        if available_jobs is None:
            available_jobs = self.available_jobs
        
        if not available_jobs:
            available_jobs = ["전사", "아크메이지", "궁수"]
        
        job = random.choice(available_jobs)
        if job in available_jobs:
            available_jobs.remove(job)  # 중복 방지
        
        # AI 이름 생성
        ai_names = ["루나", "아스트라", "제피르", "오리온", "셀레스트", "아테나", "헤르메스"]
        name = f"AI_{random.choice(ai_names)}"
        
        # 간단한 AI 캐릭터 생성
        ai_companion = {
            "name": name,
            "job": job,
            "level": 1,
            "hp": random.randint(80, 120),
            "max_hp": random.randint(80, 120),
            "mp": random.randint(40, 60),
            "max_mp": random.randint(40, 60),
            "stats": {
                "strength": random.randint(8, 18),
                "intelligence": random.randint(8, 18),
                "agility": random.randint(8, 18),
                "luck": random.randint(8, 18),
                "defense": random.randint(6, 14),
                "resistance": random.randint(6, 14)
            },
            "skills": ["기본공격", "방어", "회복"],
            "traits": [],
            "is_player": False,
            "ai_personality": random.choice(["용감한", "신중한", "활발한", "냉정한", "따뜻한"])
        }
        
        self.ai_companions.append(ai_companion)
        print(f"   ✅ {name} ({job}) - {ai_companion['ai_personality']} 성격")
    
    def _get_job_base_stats(self, job: str) -> Dict[str, int]:
        """직업별 기본 스탯 반환"""
        stat_templates = {
            # 전투 직업군 - 물리 중심
            "전사": {"strength": 15, "intelligence": 8, "agility": 10, "luck": 10},
            "궁수": {"strength": 12, "intelligence": 10, "agility": 15, "luck": 12},
            "도적": {"strength": 10, "intelligence": 12, "agility": 15, "luck": 15},
            "성기사": {"strength": 14, "intelligence": 12, "agility": 8, "luck": 10},
            "암흑기사": {"strength": 14, "intelligence": 11, "agility": 10, "luck": 8},
            "몽크": {"strength": 13, "intelligence": 10, "agility": 14, "luck": 11},
            "바드": {"strength": 8, "intelligence": 12, "agility": 12, "luck": 15},
            
            # 마법 직업군 - 지능 중심
            "아크메이지": {"strength": 8, "intelligence": 15, "agility": 10, "luck": 12},
            "네크로맨서": {"strength": 9, "intelligence": 15, "agility": 10, "luck": 8},
            "용기사": {"strength": 13, "intelligence": 13, "agility": 10, "luck": 10},
            "검성": {"strength": 12, "intelligence": 12, "agility": 13, "luck": 11},
            "정령술사": {"strength": 8, "intelligence": 14, "agility": 11, "luck": 13},
            "시간술사": {"strength": 7, "intelligence": 15, "agility": 12, "luck": 14},
            "연금술사": {"strength": 9, "intelligence": 14, "agility": 11, "luck": 12},
            "차원술사": {"strength": 8, "intelligence": 15, "agility": 11, "luck": 13},
            "마검사": {"strength": 11, "intelligence": 13, "agility": 12, "luck": 11},
            "기계공학자": {"strength": 10, "intelligence": 14, "agility": 12, "luck": 11},
            "무당": {"strength": 9, "intelligence": 13, "agility": 11, "luck": 14},
            
            # 특수 직업군 - 균형 또는 특화
            "암살자": {"strength": 11, "intelligence": 12, "agility": 15, "luck": 14},
            "해적": {"strength": 12, "intelligence": 10, "agility": 13, "luck": 15},
            "사무라이": {"strength": 13, "intelligence": 11, "agility": 13, "luck": 12},
            "드루이드": {"strength": 10, "intelligence": 13, "agility": 11, "luck": 13},
            "철학자": {"strength": 8, "intelligence": 15, "agility": 10, "luck": 14},
            "검투사": {"strength": 14, "intelligence": 9, "agility": 12, "luck": 12},
            "기사": {"strength": 14, "intelligence": 10, "agility": 11, "luck": 10},
            "신관": {"strength": 9, "intelligence": 13, "agility": 10, "luck": 15},
            "광전사": {"strength": 15, "intelligence": 8, "agility": 12, "luck": 10}
        }
        
        return stat_templates.get(job, {"strength": 10, "intelligence": 10, "agility": 10, "luck": 10})
    
    def _display_character_info(self, character: Dict[str, Any]):
        """캐릭터 정보 표시"""
        print(f"\n📋 {character['name']} 정보:")
        print(f"   직업: {character['job']}")
        print(f"   레벨: {character['level']}")
        print(f"   HP: {character['hp']}/{character.get('max_hp', character['hp'])}")
        print(f"   MP: {character['mp']}/{character.get('max_mp', character['mp'])}")
        
        stats = character['stats']
        print(f"   스탯:")
        print(f"     💪 힘: {stats['strength']} | 🧠 지능: {stats['intelligence']}")
        print(f"     🏃 민첩: {stats['agility']} | 🍀 운: {stats['luck']}")
        if 'defense' in stats:
            print(f"     🛡️ 방어: {stats['defense']} | 🔮 저항: {stats.get('resistance', 0)}")
        
        skills = character.get('skills', [])
        if skills:
            if len(skills) > 6:
                print(f"   스킬: {', '.join(skills[:6])}... (총 {len(skills)}개)")
            else:
                print(f"   스킬: {', '.join(skills)}")
        
        traits = character.get('traits', [])
        if traits:
            print(f"   특성: {', '.join(traits)}")
        
        if not character['is_player']:
            print(f"   AI 성격: {character.get('ai_personality', '보통')}")
    
    def show_party_status(self):
        """파티 상태 표시"""
        print(f"\n👥 현재 파티 상태:")
        print("-" * 50)
        
        if self.player_character:
            print("👤 플레이어:")
            self._display_character_info(self.player_character)
        
        if self.ai_companions:
            print(f"\n🤖 AI 동료들:")
            for companion in self.ai_companions:
                self._display_character_info(companion)
    
    def start_training_mode(self):
        """훈련 모드 시작"""
        if not self.player_character:
            print("❌ 먼저 플레이어 캐릭터를 생성해주세요.")
            return
        
        print(f"\n🎯 {self.player_character['name']}의 훈련 모드")
        print("="*50)
        
        training_options = [
            "개인 스킬 훈련",
            "파티 협력 훈련", 
            "전투 시뮬레이션",
            "AI 동료와 소통 훈련"
        ]
        
        for i, option in enumerate(training_options, 1):
            print(f"{i}. {option}")
        print("0. 🔙 메인 메뉴로 돌아가기")
        
        while True:
            try:
                choice = safe_input("\n훈련 모드 선택 (0-4): ", 2).strip()
                
                if choice == "0":
                    print("🔙 메인 메뉴로 돌아갑니다.")
                    return
                
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(training_options):
                    selected_training = training_options[choice_num]
                    self._execute_training(selected_training)
                    break
                else:
                    print("❌ 0-4 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
    
    def _execute_training(self, training_type: str):
        """훈련 실행"""
        print(f"\n🏃‍♂️ {training_type} 시작!")
        
        if training_type == "개인 스킬 훈련":
            print("💪 개인 스킬을 연마하고 있습니다...")
            # 스킬 포인트 증가 시뮬레이션
            skill_gain = random.randint(1, 3)
            print(f"✅ 스킬 숙련도가 {skill_gain} 포인트 증가했습니다!")
            
        elif training_type == "파티 협력 훈련":
            print("🤝 AI 동료들과 협력 훈련을 하고 있습니다...")
            # 팀워크 향상 시뮬레이션
            for companion in self.ai_companions:
                print(f"   {companion['name']}: 좋은 협력이었습니다!")
            print("✅ 파티 협력도가 향상되었습니다!")
            
        elif training_type == "전투 시뮬레이션":
            print("⚔️ 가상 적과 전투 훈련 중...")
            # 전투 경험치 증가 시뮬레이션
            exp_gain = random.randint(10, 30)
            print(f"✅ 전투 경험치 {exp_gain} 획득!")
            
        elif training_type == "AI 동료와 소통 훈련":
            print("💬 AI 동료들과 의사소통 훈련 중...")
            # AI와의 친밀도 증가 시뮬레이션
            for companion in self.ai_companions:
                print(f"   {companion['name']}: 더 잘 이해하게 되었어요!")
            print("✅ AI 동료들과의 친밀도가 증가했습니다!")
        
        print(f"\n🎉 {training_type} 완료!")
    
    def start_simple_adventure(self):
        """간단한 모험 시작"""
        if not self.player_character or not self.ai_companions:
            print("❌ 먼저 파티를 구성해주세요.")
            return
        
        print(f"\n🗺️ {self.player_character['name']}의 모험 시작!")
        print("="*50)
        
        adventure_scenarios = [
            {
                "name": "숲속의 고블린 소굴",
                "description": "고블린들이 마을을 위협하고 있습니다",
                "difficulty": "쉬움",
                "enemies": ["고블린 전사", "고블린 궁수", "고블린 우두머리"],
                "rewards": ["경험치 +50", "골드 +100", "장비 획득 가능"]
            },
            {
                "name": "폐허가 된 마법탑",
                "description": "고대 마법사의 탑에 위험한 마법 생물들이 살고 있습니다",
                "difficulty": "보통",
                "enemies": ["스켈레톤 마법사", "가고일", "리치"],
                "rewards": ["경험치 +100", "골드 +200", "마법 아이템"]
            },
            {
                "name": "용의 둥지",
                "description": "전설의 드래곤이 잠들어 있는 둥지입니다",
                "difficulty": "어려움",
                "enemies": ["드래곤 새끼", "드래곤 가디언", "고대 드래곤"],
                "rewards": ["경험치 +300", "골드 +1000", "전설 장비"]
            }
        ]
        
        print("모험지를 선택하세요:")
        for i, scenario in enumerate(adventure_scenarios, 1):
            print(f"{i}. {scenario['name']} ({scenario['difficulty']})")
            print(f"   {scenario['description']}")
            print(f"   예상 보상: {', '.join(scenario['rewards'])}")
            print()
        print("0. 🔙 메인 메뉴로 돌아가기")
        
        while True:
            try:
                choice = safe_input("\n모험지 선택 (0-3): ", 2).strip()
                
                if choice == "0":
                    print("🔙 메인 메뉴로 돌아갑니다.")
                    return
                
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(adventure_scenarios):
                    selected_scenario = adventure_scenarios[choice_num]
                    self._execute_adventure(selected_scenario)
                    break
                else:
                    print("❌ 0-3 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
    
    def _execute_adventure(self, scenario: Dict[str, Any]):
        """모험 실행"""
        print(f"\n🗺️ {scenario['name']} 진입!")
        print(f"📖 {scenario['description']}")
        print("-" * 50)
        
        # 파티원들의 반응
        for companion in self.ai_companions:
            reactions = [
                f"{companion['name']}: 준비됐습니다!",
                f"{companion['name']}: 함께 가요!",
                f"{companion['name']}: 조심스럽게 진행합시다.",
                f"{companion['name']}: 제가 도울게요!"
            ]
            print(random.choice(reactions))
        
        print("\n⚔️ 전투 시뮬레이션 중...")
        
        # 간단한 전투 결과 시뮬레이션
        success_rate = {
            "쉬움": 0.9,
            "보통": 0.7,
            "어려움": 0.5
        }
        
        is_success = random.random() < success_rate[scenario['difficulty']]
        
        if is_success:
            print("🎉 승리!")
            print(f"✅ 보상 획득: {', '.join(scenario['rewards'])}")
            
            # AI 동료들의 승리 반응
            victory_reactions = [
                "훌륭한 전술이었어요!",
                "팀워크가 완벽했습니다!",
                "다음 모험도 함께해요!",
                "역시 믿을 만한 리더네요!"
            ]
            
            for companion in self.ai_companions:
                print(f"   {companion['name']}: {random.choice(victory_reactions)}")
                
        else:
            print("💀 패배...")
            print("다시 도전해보세요. AI 동료들이 더 나은 전략을 제안할 것입니다.")
            
            # AI 동료들의 격려
            encourage_reactions = [
                "다음엔 더 잘할 수 있어요!",
                "실패는 성공의 어머니입니다!",
                "함께 더 훈련해봐요!",
                "포기하지 마세요!"
            ]
            
            for companion in self.ai_companions:
                print(f"   {companion['name']}: {random.choice(encourage_reactions)}")
    
    def save_party_data(self):
        """파티 데이터 저장"""
        party_data = {
            "player_character": self.player_character,
            "ai_companions": self.ai_companions,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            with open("player_party_data.json", 'w', encoding='utf-8') as f:
                json.dump(party_data, f, ensure_ascii=False, indent=2)
            print("💾 파티 데이터가 저장되었습니다.")
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
    
    def load_party_data(self):
        """파티 데이터 로드"""
        try:
            with open("player_party_data.json", 'r', encoding='utf-8') as f:
                party_data = json.load(f)
            
            self.player_character = party_data.get("player_character")
            self.ai_companions = party_data.get("ai_companions", [])
            
            print("📂 파티 데이터가 로드되었습니다.")
            return True
        except FileNotFoundError:
            print("💡 저장된 파티 데이터가 없습니다.")
            return False
        except Exception as e:
            print(f"❌ 로드 실패: {e}")
            return False
    
    def main_menu(self):
        """메인 메뉴"""
        # 기존 데이터 로드 시도
        self.load_party_data()
        
        while True:
            print("\n" + "="*60)
            print("🎮 Dawn of Stellar - 플레이어 중심 AI 멀티플레이어")
            print("="*60)
            
            if self.player_character:
                print(f"👤 현재 플레이어: {self.player_character['name']} ({self.player_character['job']})")
                print(f"🤖 AI 동료: {len(self.ai_companions)}명")
            else:
                print("👤 플레이어: 미생성")
            
            print("\n🎮 메인 메뉴:")
            print("1. 👤 플레이어 캐릭터 생성 (27개 직업)")
            print("2. 🤖 AI 동료 자동 생성")
            print("3. 👥 파티 상태 보기")
            print("4. 🎯 훈련 모드")
            print("5. 🗺️ 간단한 모험")
            print("6. 💾 데이터 저장")
            print("7. 📂 데이터 로드")
            if SYSTEMS_AVAILABLE:
                print("8. 🎯 고급 AI 훈련 시스템")
            print("9. 🔧 스마트 AI 멀티플레이어 (고급)")
            if SAFE_EXIT_AVAILABLE:
                print("99. 🛡️ 안전 종료")
            print("0. 🚪 종료")
            print("\n💡 팁: 대부분의 메뉴에서 0을 누르면 뒤로가기가 됩니다!")
            
            choice = safe_input("\n선택하세요: ", 3).strip()
            
            if choice == "1":
                result = self.create_player_character()
                if result is None:
                    print("🔙 캐릭터 생성이 취소되어 메인 메뉴로 돌아갑니다.")
            elif choice == "2":
                if self.player_character:
                    self.create_ai_companions()
                else:
                    print("❌ 먼저 플레이어 캐릭터를 생성해주세요.")
            elif choice == "3":
                self.show_party_status()
            elif choice == "4":
                self.start_training_mode()
            elif choice == "5":
                self.start_simple_adventure()
            elif choice == "6":
                self.save_party_data()
            elif choice == "7":
                self.load_party_data()
            elif choice == "8" and SYSTEMS_AVAILABLE:
                try:
                    training_system.show_training_menu()
                except Exception as e:
                    print(f"❌ 고급 훈련 시스템 오류: {e}")
            elif choice == "9":
                print("🔄 스마트 AI 멀티플레이어 시스템으로 전환합니다...")
                try:
                    import subprocess
                    subprocess.run(["python", "smart_ai_multiplayer.py"])
                except Exception as e:
                    print(f"❌ 스마트 AI 시스템 실행 실패: {e}")
                    print("💡 직접 'python smart_ai_multiplayer.py'를 실행해보세요.")
                self.save_party_data()
            elif choice == "7":
                self.load_party_data()
            elif choice == "8" and SYSTEMS_AVAILABLE:
                try:
                    training_system.show_training_menu()
                except Exception as e:
                    print(f"❌ 고급 훈련 시스템 오류: {e}")
            elif choice == "99" and SAFE_EXIT_AVAILABLE:
                print("🛡️ 안전 종료를 시작합니다...")
                self.emergency_save_all()
                safe_exit(0)
            elif choice == "0":
                if SAFE_EXIT_AVAILABLE:
                    print("🛡️ 안전 종료 프로세스를 실행합니다...")
                    self.emergency_save_all()
                    safe_exit(0)
                else:
                    print("👋 게임을 종료합니다.")
                    break
            else:
                print("❌ 잘못된 선택입니다.")
            
            if choice != "0":
                input("\nEnter를 눌러 계속...")

def main():
    """메인 실행 함수"""
    system = PlayerCentricAISystem()
    system.main_menu()

if __name__ == "__main__":
    main()
