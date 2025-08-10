#!/usr/bin/env python3
"""
Dawn of Stellar - AI 캐릭터 자동 생성기 (27개 직업 연동)
직업별 특성을 반영한 AI 캐릭터 자동 생성
"""

import random
import json
import sys
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# 한글 입력 지원을 위한 인코딩 설정
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stdin = codecs.getreader('utf-8')(sys.stdin.buffer)

def safe_korean_input(prompt: str = "") -> str:
    """한글 입력을 안전하게 처리하는 함수"""
    try:
        if prompt:
            print(prompt, end="", flush=True)
        
        # 간단한 방법: 여러 번 시도
        for attempt in range(3):
            try:
                result = input().strip()
                if result or attempt == 2:  # 결과가 있거나 마지막 시도
                    return result
                print("다시 입력해주세요: ", end="", flush=True)
            except UnicodeDecodeError:
                print(f"[입력 오류 {attempt+1}/3] 다시 시도: ", end="", flush=True)
                continue
            except Exception as e:
                if attempt == 2:
                    print(f"\n[입력 오류: {e}] 기본값 사용")
                    return ""
        return ""
            
    except Exception as e:
        print(f"\n[입력 시스템 오류: {e}]")
        return ""

# 기존 시스템들 import
try:
    from complete_27_job_system import job_system, JobProfile
    from ai_character_database import AICharacterPresetManager
    from ai_interaction_system import EmotionState, InteractionType
    from ai_cooperation_system import CooperationType
    from ai_tactical_system import TacticalRole
    JOB_SYSTEM_AVAILABLE = True
    print("✅ 직업 시스템 모듈들 import 성공")
except ImportError as e:
    JOB_SYSTEM_AVAILABLE = False
    print(f"⚠️ 일부 모듈을 찾을 수 없습니다: {e}")
    print("기본 모드로 실행합니다.")

@dataclass
class AICharacterTemplate:
    """AI 캐릭터 템플릿"""
    name: str
    job_id: str
    personality_base: List[str]          # 기본 성격
    emotional_tendencies: List[str]      # 감정 성향
    cooperation_style: str              # 협력 스타일
    combat_preferences: List[str]       # 전투 선호도
    dialogue_patterns: List[str]        # 대화 패턴
    story_motivation: str               # 스토리 동기
    relationship_defaults: Dict[str, int] # 기본 관계도

class AI27JobCharacterCreator:
    """27개 직업 기반 AI 캐릭터 자동 생성기"""
    
    def __init__(self):
        if not JOB_SYSTEM_AVAILABLE:
            print("❌ 직업 시스템을 찾을 수 없습니다.")
            return
            
        self.job_system = job_system
        self.character_db = AICharacterPresetManager()
        
        # 이름 풀 (직업별 맞춤형)
        self.name_pools = self._init_name_pools()
        
        # 성격 특성 매핑
        self.personality_mappings = self._init_personality_mappings()
        
        # 감정 성향 매핑
        self.emotion_mappings = self._init_emotion_mappings()
        
        print("🤖 27개 직업 AI 캐릭터 생성기 초기화 완료")
    
    def _init_name_pools(self) -> Dict[str, List[str]]:
        """직업별 이름 풀 초기화"""
        return {
            # 전투 직업군
            "warrior": ["아르투스", "레오니드", "발키리", "브룬힐드", "시그프리드"],
            "archmage": ["메를린", "갈라드리엘", "간달프", "헤르메스", "아르카나"],
            "archer": ["레골라스", "로빈후드", "아르테미스", "카트니스", "호크아이"],
            "rogue": ["아사신", "쉐도우", "실버", "나이트메어", "팬텀"],
            "paladin": ["세라핌", "가브리엘", "미카엘", "우리엘", "라파엘"],
            "dark_knight": ["아르토리아스", "다크니스", "레이븐", "오르페우스", "데모고르곤"],
            "monk": ["젠마스터", "부다", "샤오린", "달라이", "카르마"],
            "bard": ["오르페우스", "아폴론", "리라", "하모니", "멜로디"],
            
            # 마법 직업군  
            "necromancer": ["리치킹", "모르데카이", "네크로스", "레이스", "소울리버"],
            "dragon_knight": ["드래곤로드", "와이번", "바하무트", "파이어브레스", "스카이림"],
            "sword_saint": ["무사시", "켄세이", "소드마스터", "블레이드", "검신"],
            "elementalist": ["엘레멘탈", "스톰", "블리자드", "인페르노", "어스퀘이크"],
            "time_mage": ["크로노스", "타임워프", "프로피셔", "오라클", "포시어"],
            "alchemist": ["니콜라스", "파라셀수스", "호문클루스", "엘릭서", "트랜스뮤터"],
            "dimension_mage": ["디멘션", "포털", "보이드워커", "리프트", "네더"],
            "magic_swordsman": ["스펠소드", "마검사", "엔챈터", "배틀메이지", "워스펠"],
            "engineer": ["스팀펑크", "기어헤드", "테슬라", "사이보그", "메카닉"],
            "shaman": ["토템", "스피릿", "와이즈맨", "드림워커", "소울가이드"],
            
            # 특수 직업군
            "assassin": ["이지오", "파이버", "해시신", "그림리퍼", "실런트"],
            "pirate": ["잭스패로우", "블랙비어드", "붉은수염", "바다늑대", "크라켄"],
            "samurai": ["무사시", "요시츠네", "하치로", "사카모토", "코지로"],
            "druid": ["래디언트", "네이처", "그린맨", "숲지기", "생명수"],
            "philosopher": ["소크라테스", "플라톤", "아리스토텔레스", "데카르트", "니체"],
            "gladiator": ["스파르타쿠스", "막시무스", "루셀", "챔피언", "아레나킹"],
            "knight": ["랜슬롯", "가웨인", "퍼시발", "갈라하드", "트리스탄"],
            "priest": ["베네딕트", "프란시스", "요한", "마리아", "가브리엘라"],
            "berserker": ["바바리안", "광전사", "레이지", "버서커", "와일드맨"]
        }
    
    def _init_personality_mappings(self) -> Dict[str, List[str]]:
        """성격 특성 매핑"""
        return {
            "용감한": ["대담한", "무모한", "결단력있는", "모험적인"],
            "지적인": ["논리적", "분석적", "학구적", "현명한"],
            "신비로운": ["수수께끼같은", "예언적", "직관적", "영적인"],
            "자유로운": ["독립적", "반항적", "창의적", "모험적"],
            "성스러운": ["순수한", "자비로운", "희생적", "신실한"],
            "어둠의": ["신비로운", "복수심있는", "고독한", "냉정한"],
            "평화로운": ["차분한", "명상적", "균형잡힌", "조화로운"],
            "예술적": ["창의적", "감성적", "표현적", "아름다운"],
            "교활한": ["영리한", "기회주의적", "적응적", "생존본능"],
            "명예로운": ["정직한", "충성스러운", "도덕적", "고결한"]
        }
    
    def _init_emotion_mappings(self) -> Dict[str, List[str]]:
        """감정 성향 매핑"""
        return {
            "전투직": ["결정적", "열정적", "도전적", "승부욕"],
            "마법직": ["신중한", "집중적", "탐구적", "신비적"],
            "특수직": ["독특한", "창의적", "자유로운", "특별한"]
        }
    
    def create_character_from_job(self, job_id: str, custom_name: str = None) -> Dict[str, Any]:
        """직업 기반 AI 캐릭터 생성"""
        if not JOB_SYSTEM_AVAILABLE:
            return {}
            
        job_profile = self.job_system.get_job_profile(job_id)
        if not job_profile:
            print(f"❌ 직업 '{job_id}'를 찾을 수 없습니다.")
            return {}
        
        # 이름 생성
        if custom_name:
            name = custom_name
        else:
            name_pool = self.name_pools.get(job_id, ["Unknown"])
            name = random.choice(name_pool)
        
        # 성격 생성
        personality = self._generate_personality(job_profile)
        
        # 감정 성향 생성
        emotions = self._generate_emotional_tendencies(job_profile)
        
        # 협력 스타일 생성
        cooperation_style = self._generate_cooperation_style(job_profile)
        
        # 전투 선호도 생성
        combat_prefs = self._generate_combat_preferences(job_profile)
        
        # 대화 패턴 생성
        dialogue_patterns = self._generate_dialogue_patterns(job_profile)
        
        # 스토리 동기 생성
        story_motivation = self._generate_story_motivation(job_profile)
        
        # 관계도 기본값 생성
        relationships = self._generate_default_relationships(job_profile)
        
        # AI 캐릭터 데이터 구성
        character_data = {
            "name": name,
            "job_id": job_id,
            "job_name": job_profile.name,
            "personality": {
                "base_traits": personality,
                "emotional_tendencies": emotions,
                "cooperation_style": cooperation_style
            },
            "combat": {
                "tactical_role": job_profile.tactical_role.value,
                "combat_style": job_profile.combat_style,
                "preferences": combat_prefs,
                "signature_skills": job_profile.signature_skills
            },
            "social": {
                "dialogue_patterns": dialogue_patterns,
                "cooperation_preference": job_profile.cooperation_preference,
                "default_relationships": relationships
            },
            "story": {
                "background": job_profile.story_background,
                "motivation": story_motivation,
                "category": job_profile.category
            },
            "stats": {
                "primary_stats": job_profile.primary_stats,
                "secondary_stats": job_profile.secondary_stats
            }
        }
        
        print(f"✅ '{name}' ({job_profile.name}) 캐릭터 생성 완료")
        return character_data
    
    def _generate_personality(self, job_profile: JobProfile) -> List[str]:
        """성격 생성"""
        personality = []
        
        # 직업 기본 특성에서 선택
        for trait in job_profile.ai_personality_traits:
            if trait in self.personality_mappings:
                extra_traits = random.sample(self.personality_mappings[trait], 2)
                personality.extend(extra_traits)
            personality.append(trait)
        
        # 중복 제거 및 최대 5개로 제한
        unique_personality = list(set(personality))
        return unique_personality[:5]
    
    def _generate_emotional_tendencies(self, job_profile: JobProfile) -> List[str]:
        """감정 성향 생성"""
        emotions = []
        
        # 직업 카테고리 기반
        if "전투" in job_profile.category:
            emotions.extend(random.sample(self.emotion_mappings["전투직"], 2))
        elif "마법" in job_profile.category:
            emotions.extend(random.sample(self.emotion_mappings["마법직"], 2))
        else:
            emotions.extend(random.sample(self.emotion_mappings["특수직"], 2))
        
        # 역할 기반 추가
        role_emotions = {
            TacticalRole.TANK: ["보호적", "책임감"],
            TacticalRole.DPS: ["공격적", "경쟁적"],
            TacticalRole.HEALER: ["돌봄", "평화적"],
            TacticalRole.SUPPORT: ["협력적", "배려적"],
            TacticalRole.CONTROLLER: ["전략적", "통제적"],
            TacticalRole.SCOUT: ["경계심", "탐구적"]
        }
        
        if job_profile.tactical_role in role_emotions:
            emotions.extend(role_emotions[job_profile.tactical_role])
        
        return emotions[:4]
    
    def _generate_cooperation_style(self, job_profile: JobProfile) -> str:
        """협력 스타일 생성"""
        styles = {
            TacticalRole.TANK: "선도형",
            TacticalRole.DPS: "공격형", 
            TacticalRole.HEALER: "지원형",
            TacticalRole.SUPPORT: "조화형",
            TacticalRole.CONTROLLER: "전략형",
            TacticalRole.SCOUT: "정보형"
        }
        return styles.get(job_profile.tactical_role, "균형형")
    
    def _generate_combat_preferences(self, job_profile: JobProfile) -> List[str]:
        """전투 선호도 생성"""
        prefs = []
        
        # 전투 스타일 기반
        style = job_profile.combat_style
        if "근접" in style:
            prefs.extend(["근거리_전투", "직접_공격"])
        elif "원거리" in style:
            prefs.extend(["원거리_전투", "안전_거리"])
        
        # 특수 스타일 추가
        if "방어" in style:
            prefs.append("방어_우선")
        elif "공격" in style:
            prefs.append("공격_우선")
        elif "지원" in style:
            prefs.append("팀플레이")
        elif "치유" in style:
            prefs.append("회복_우선")
        
        return prefs[:3]
    
    def _generate_dialogue_patterns(self, job_profile: JobProfile) -> List[str]:
        """대화 패턴 생성"""
        patterns = []
        
        # 성격 기반 대화 패턴
        trait_patterns = {
            "용감한": ["당당한_어조", "직설적_표현"],
            "지적인": ["논리적_설명", "학술적_용어"],
            "신비로운": ["은유적_표현", "암시적_언어"],
            "자유로운": ["활동적_어조", "창의적_표현"],
            "성스러운": ["정중한_어조", "축복_표현"],
            "평화로운": ["차분한_어조", "명상적_표현"]
        }
        
        for trait in job_profile.ai_personality_traits:
            if trait in trait_patterns:
                patterns.extend(trait_patterns[trait])
        
        # 직업별 고유 패턴 추가
        job_patterns = {
            "warrior": ["전투_용어", "명령형_어조"],
            "archmage": ["마법_용어", "학술적_설명"],
            "priest": ["종교적_표현", "축복_언어"],
            "philosopher": ["철학적_질문", "깊은_사고"]
        }
        
        if job_profile.job_id in job_patterns:
            patterns.extend(job_patterns[job_profile.job_id])
        
        return patterns[:4]
    
    def _generate_story_motivation(self, job_profile: JobProfile) -> str:
        """스토리 동기 생성"""
        motivations = {
            "전투직업군": "시공교란 속에서 질서를 회복하고자 한다",
            "마법직업군": "시공교란의 원인을 마법적으로 해결하려 한다", 
            "특수직업군": "시공교란을 자신만의 방식으로 극복하려 한다"
        }
        
        base_motivation = motivations.get(job_profile.category, "시공교란의 혼돈을 수습하려 한다")
        
        # 직업별 특수 동기 추가
        if "시간" in job_profile.name:
            return "시공교란의 근본 원인을 찾아 시간 흐름을 복원하려 한다"
        elif "차원" in job_profile.name:
            return "차원 균열을 봉인하여 현실을 안정시키려 한다"
        elif "성기사" in job_profile.name or "신관" in job_profile.name:
            return "신의 뜻에 따라 시공교란을 정화하려 한다"
        
        return base_motivation
    
    def _generate_default_relationships(self, job_profile: JobProfile) -> Dict[str, int]:
        """기본 관계도 생성"""
        relationships = {}
        
        # 협력 선호 직업들과는 +관계
        for partner in job_profile.cooperation_preference:
            relationships[partner] = random.randint(60, 80)
        
        # 같은 역할 직업들과는 중립~우호
        same_role_jobs = self.job_system.get_jobs_by_role(job_profile.tactical_role)
        for job in same_role_jobs:
            if job.name != job_profile.name:
                relationships[job.name] = random.randint(40, 60)
        
        # 대립 관계 설정 (일부)
        opposites = {
            "성기사": ["암흑기사", "네크로맨서"],
            "암흑기사": ["성기사", "신관"],
            "네크로맨서": ["성기사", "신관"],
            "드루이드": ["기계공학자", "연금술사"],
            "철학자": ["광전사", "해적"]
        }
        
        if job_profile.name in opposites:
            for opponent in opposites[job_profile.name]:
                relationships[opponent] = random.randint(20, 40)
        
        return relationships
    
    def create_full_party_set(self, party_size: int = 4) -> List[Dict[str, Any]]:
        """균형잡힌 파티 구성 생성"""
        if not JOB_SYSTEM_AVAILABLE:
            return []
        
        party_jobs = []
        
        # 역할별 최소 1명씩 보장
        essential_roles = [TacticalRole.TANK, TacticalRole.DPS, TacticalRole.HEALER, TacticalRole.SUPPORT]
        
        for role in essential_roles[:party_size]:
            role_jobs = self.job_system.get_jobs_by_role(role)
            if role_jobs:
                selected_job = random.choice(role_jobs)
                party_jobs.append(selected_job.job_id)
        
        # 나머지 자리는 랜덤 충원
        while len(party_jobs) < party_size:
            all_jobs = list(self.job_system.jobs.keys())
            remaining_jobs = [job for job in all_jobs if job not in party_jobs]
            if remaining_jobs:
                party_jobs.append(random.choice(remaining_jobs))
            else:
                break
        
        # 각 직업에 대해 캐릭터 생성
        party_characters = []
        for job_id in party_jobs:
            character = self.create_character_from_job(job_id)
            if character:
                party_characters.append(character)
        
        print(f"✅ {len(party_characters)}명 파티 생성 완료")
        return party_characters
    
    def save_character_to_database(self, character_data: Dict[str, Any]) -> bool:
        """캐릭터를 데이터베이스에 저장"""
        try:
            # AI 캐릭터 데이터베이스 형식으로 변환
            db_format = {
                "name": character_data["name"],
                "personality": character_data["personality"]["base_traits"],
                "background": character_data["story"]["background"],
                "relationships": character_data["social"]["default_relationships"],
                "conversation_history": [],
                "learning_data": {
                    "job_info": {
                        "job_id": character_data["job_id"],
                        "job_name": character_data["job_name"],
                        "tactical_role": character_data["combat"]["tactical_role"]
                    }
                }
            }
            
            # 데이터베이스에 저장
            self.character_db.add_character(
                character_data["name"],
                db_format["personality"],
                db_format["background"],
                db_format["relationships"]
            )
            
            print(f"💾 '{character_data['name']}' 데이터베이스 저장 완료")
            return True
            
        except Exception as e:
            print(f"❌ 데이터베이스 저장 실패: {e}")
            return False
    
    def batch_create_all_jobs(self) -> List[Dict[str, Any]]:
        """모든 27개 직업의 대표 캐릭터 생성"""
        if not JOB_SYSTEM_AVAILABLE:
            return []
        
        all_characters = []
        
        print("🚀 모든 직업의 대표 캐릭터 생성 시작...")
        
        for job_id in self.job_system.jobs.keys():
            try:
                character = self.create_character_from_job(job_id)
                if character:
                    all_characters.append(character)
                    # 데이터베이스에도 저장
                    self.save_character_to_database(character)
            except Exception as e:
                print(f"❌ '{job_id}' 캐릭터 생성 실패: {e}")
        
        print(f"✅ 총 {len(all_characters)}개 캐릭터 생성 완료")
        return all_characters
    
    def export_characters_to_json(self, characters: List[Dict[str, Any]], filename: str = "ai_characters_27jobs.json"):
        """캐릭터들을 JSON으로 내보내기"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(characters, f, ensure_ascii=False, indent=2)
            print(f"📁 '{filename}'로 캐릭터 데이터 내보내기 완료")
        except Exception as e:
            print(f"❌ JSON 내보내기 실패: {e}")
    
    def show_creator_menu(self):
        """캐릭터 생성기 메뉴 (커서 기반)"""
        try:
            from game.cursor_menu_system import CursorMenu
            
            while True:
                options = [
                    "개별 직업 캐릭터 생성",
                    "균형잡힌 파티 생성", 
                    "모든 직업 대표 캐릭터 생성",
                    "생성된 캐릭터 목록 보기",
                    "JSON으로 내보내기"
                ]
                
                descriptions = [
                    "원하는 직업을 선택해서 캐릭터를 개별 생성합니다",
                    "탱커, 딜러, 힐러, 서포터가 균형잡힌 4인 파티를 생성합니다",
                    "27개 직업 모두의 대표 캐릭터를 한 번에 생성합니다",
                    "현재까지 생성된 모든 캐릭터의 목록을 확인합니다",
                    "생성된 캐릭터 데이터를 JSON 파일로 내보냅니다"
                ]
                
                # 현재 생성된 캐릭터 수 표시
                all_chars = self.character_db.get_all_characters()
                extra_content = f"현재 등록된 캐릭터: {len(all_chars)}명"
                
                cursor_menu = CursorMenu(
                    title="🤖 AI 캐릭터 자동 생성기 (27개 직업)",
                    extra_content=extra_content,
                    options=options,
                    descriptions=descriptions,
                    cancellable=True
                )
                
                result = cursor_menu.run()
                
                if result is None or result == -1:
                    break
                
                if result == 0:
                    self._menu_create_individual()
                elif result == 1:
                    self._menu_create_party()
                elif result == 2:
                    self._menu_create_all_jobs()
                elif result == 3:
                    self._menu_show_characters()
                elif result == 4:
                    self._menu_export_json()
                    
                input("\nEnter를 눌러 계속...")
                    
        except ImportError:
            # 폴백: 기본 메뉴 시스템
            self._show_creator_menu_fallback()
        except Exception as e:
            print(f"❌ 메뉴 처리 오류: {e}")
            input("\nEnter를 눌러 계속...")
    
    def _show_creator_menu_fallback(self):
        """폴백: 기본 메뉴 시스템"""
        while True:
            print("\n🤖 AI 캐릭터 자동 생성기 (27개 직업)")
            print("=" * 50)
            print("1. 개별 직업 캐릭터 생성")
            print("2. 균형잡힌 파티 생성")
            print("3. 모든 직업 대표 캐릭터 생성")
            print("4. 생성된 캐릭터 목록 보기")
            print("5. JSON으로 내보내기")
            print("0. 돌아가기")
            
            try:
                choice = input("\n선택하세요: ").strip()
                
                if choice == "1":
                    self._menu_create_individual()
                elif choice == "2":
                    self._menu_create_party()
                elif choice == "3":
                    self._menu_create_all_jobs()
                elif choice == "4":
                    self._menu_show_characters()
                elif choice == "5":
                    self._menu_export_json()
                elif choice == "0":
                    break
                else:
                    print("❌ 잘못된 선택입니다.")
                    
            except Exception as e:
                print(f"❌ 메뉴 처리 오류: {e}")
            
            input("\nEnter를 눌러 계속...")
    
    def _menu_create_individual(self):
        """개별 캐릭터 생성 메뉴 (커서 기반)"""
        if not JOB_SYSTEM_AVAILABLE:
            print("❌ 직업 시스템을 사용할 수 없습니다.")
            return
        
        try:
            from game.cursor_menu_system import CursorMenu
            
            # 27개 직업을 카테고리별로 정리
            job_list = list(self.job_system.jobs.keys())
            job_options = []
            job_descriptions = []
            
            for job_id in job_list:
                job_profile = self.job_system.get_job_profile(job_id)
                job_options.append(f"{job_profile.name} ({job_profile.category})")
                
                # 직업 설명 생성
                role_name = job_profile.tactical_role.value if hasattr(job_profile.tactical_role, 'value') else str(job_profile.tactical_role)
                desc = f"{role_name} | 스킬: {', '.join(job_profile.signature_skills[:2])}"
                job_descriptions.append(desc)
            
            cursor_menu = CursorMenu(
                title="📋 직업 선택 (27개 직업)",
                extra_content="원하는 직업을 선택하여 캐릭터를 생성합니다",
                options=job_options,
                descriptions=job_descriptions,
                cancellable=True
            )
            
            result = cursor_menu.run()
            
            if result is not None and result != -1:
                job_id = job_list[result]
                
                # 이름 입력
                custom_name = safe_korean_input("\n사용자 정의 이름 (Enter=자동생성): ")
                if not custom_name:
                    custom_name = None
                
                character = self.create_character_from_job(job_id, custom_name)
                if character:
                    self.save_character_to_database(character)
                    print(f"\n🎉 '{character['name']}' 캐릭터 생성 및 저장 완료!")
                    
                    # 생성된 캐릭터 정보 표시
                    print(f"   직업: {character.get('job_name', job_id)}")
                    print(f"   성격: {', '.join(character.get('personality_traits', [])[:3])}")
                    print(f"   전투 스타일: {character.get('combat_style', '일반')}")
                    
        except ImportError:
            # 폴백: 기본 메뉴
            self._menu_create_individual_fallback()
        except Exception as e:
            print(f"❌ 캐릭터 생성 오류: {e}")
    
    def _menu_create_individual_fallback(self):
        """폴백: 기본 개별 생성 메뉴"""
        print("\n📋 사용 가능한 직업:")
        job_list = list(self.job_system.jobs.keys())
        for i, job_id in enumerate(job_list[:10], 1):  # 처음 10개만 표시
            job_profile = self.job_system.get_job_profile(job_id)
            print(f"{i}. {job_profile.name} ({job_id})")
        
        try:
            choice = int(safe_korean_input("직업 선택 (1-10): ")) - 1
            if 0 <= choice < len(job_list):
                job_id = job_list[choice]
                custom_name = safe_korean_input("사용자 정의 이름 (Enter=자동생성): ")
                if not custom_name:
                    custom_name = None
                
                character = self.create_character_from_job(job_id, custom_name)
                if character:
                    self.save_character_to_database(character)
                    print(f"\n🎉 '{character['name']}' 캐릭터 생성 및 저장 완료!")
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _menu_create_party(self):
        """파티 생성 메뉴"""
        try:
            party_size = int(safe_korean_input("파티 크기 (2-6): "))
            if 2 <= party_size <= 6:
                party = self.create_full_party_set(party_size)
                for character in party:
                    self.save_character_to_database(character)
                print(f"\n🎉 {party_size}명 파티 생성 완료!")
            else:
                print("❌ 파티 크기는 2-6명이어야 합니다.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _menu_create_all_jobs(self):
        """모든 직업 생성 메뉴"""
        confirm = safe_korean_input("모든 27개 직업의 캐릭터를 생성하시겠습니까? (y/N): ").lower()
        if confirm == 'y':
            characters = self.batch_create_all_jobs()
            print(f"\n🎉 {len(characters)}개 캐릭터 일괄 생성 완료!")
        else:
            print("❌ 취소되었습니다.")
    
    def _menu_show_characters(self):
        """캐릭터 목록 보기"""
        try:
            characters = self.character_db.get_all_characters()
            if characters:
                print(f"\n👥 저장된 캐릭터 ({len(characters)}명):")
                for name, data in characters.items():
                    job_info = data.get('learning_data', {}).get('job_info', {})
                    job_name = job_info.get('job_name', '알 수 없음')
                    role = job_info.get('tactical_role', '알 수 없음')
                    print(f"   • {name} ({job_name} - {role})")
            else:
                print("📭 저장된 캐릭터가 없습니다.")
        except Exception as e:
            print(f"❌ 캐릭터 목록 조회 실패: {e}")
    
    def _menu_export_json(self):
        """JSON 내보내기 메뉴"""
        try:
            characters = self.character_db.get_all_characters()
            if characters:
                filename = safe_korean_input("파일명 (기본: ai_characters_export.json): ").strip()
                if not filename:
                    filename = "ai_characters_export.json"
                
                # 리스트 형태로 변환
                character_list = []
                for name, data in characters.items():
                    character_list.append({"name": name, **data})
                
                self.export_characters_to_json(character_list, filename)
                print(f"✅ {filename}으로 내보내기 완료!")
            else:
                print("📭 내보낼 캐릭터가 없습니다.")
        except Exception as e:
            print(f"❌ 내보내기 실패: {e}")

# 전역 인스턴스
character_creator = AI27JobCharacterCreator()

def test_character_creator():
    """캐릭터 생성기 테스트"""
    if not JOB_SYSTEM_AVAILABLE:
        print("❌ 테스트를 위한 시스템이 준비되지 않았습니다.")
        return
    
    print("🧪 AI 캐릭터 생성기 테스트")
    
    # 개별 캐릭터 생성 테스트
    warrior_char = character_creator.create_character_from_job("warrior", "테스트전사")
    print(f"테스트 결과: {warrior_char['name'] if warrior_char else 'None'}")
    
    # 파티 생성 테스트
    party = character_creator.create_full_party_set(3)
    print(f"파티 생성 결과: {len(party)}명")
    
    print("✅ 캐릭터 생성기 테스트 완료")

if __name__ == "__main__":
    test_character_creator()
