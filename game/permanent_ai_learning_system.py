"""
🧠 Dawn of Stellar - 영구적 AI 학습 시스템
평생 학습하는 AI! 꺼져도 기억하고, 다시 켜져도 계속 발전!

2025년 8월 10일 - 영구 학습 + 직업별 전문 데이터셋 시스템
"""

import json
import pickle
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
import random
import hashlib

class JobClass(Enum):
    """27개 전체 직업"""
    # 전투 직업군 (8개)
    WARRIOR = "전사"
    ARCHMAGE = "아크메이지"
    ARCHER = "궁수"
    ROGUE = "도적"
    PALADIN = "성기사"
    DARK_KNIGHT = "암흑기사"
    MONK = "몽크"
    BARD = "바드"
    
    # 마법 직업군 (10개)
    NECROMANCER = "네크로맨서"
    DRAGON_KNIGHT = "용기사"
    SWORD_SAINT = "검성"
    ELEMENTALIST = "정령술사"
    TIME_MAGE = "시간술사"
    ALCHEMIST = "연금술사"
    DIMENSION_MAGE = "차원술사"
    MAGIC_SWORDSMAN = "마검사"
    ENGINEER = "기계공학자"
    SHAMAN = "무당"
    
    # 특수 직업군 (9개)
    ASSASSIN = "암살자"
    PIRATE = "해적"
    SAMURAI = "사무라이"
    DRUID = "드루이드"
    PHILOSOPHER = "철학자"
    GLADIATOR = "검투사"
    KNIGHT = "기사"
    PRIEST = "신관"
    BERSERKER = "광전사"

@dataclass
class PermanentSkillData:
    """영구 저장 스킬 데이터"""
    skill_name: str
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_damage: float = 0.0
    best_situation: str = ""
    worst_situation: str = ""
    synergy_skills: List[str] = None
    counter_skills: List[str] = None
    
    def __post_init__(self):
        if self.synergy_skills is None:
            self.synergy_skills = []
        if self.counter_skills is None:
            self.counter_skills = []

@dataclass
class PermanentCombatData:
    """영구 저장 전투 데이터"""
    enemy_type: str
    encounters: int = 0
    victories: int = 0
    defeats: int = 0
    average_combat_duration: float = 0.0
    effective_strategies: List[str] = None
    failed_strategies: List[str] = None
    optimal_party_composition: List[str] = None
    
    def __post_init__(self):
        if self.effective_strategies is None:
            self.effective_strategies = []
        if self.failed_strategies is None:
            self.failed_strategies = []
        if self.optimal_party_composition is None:
            self.optimal_party_composition = []

@dataclass
class JobSpecificKnowledge:
    """직업별 전문 지식"""
    job_class: JobClass
    mastery_level: float = 0.0  # 0.0 ~ 10.0
    signature_skills: Dict[str, PermanentSkillData] = None
    combat_expertise: Dict[str, PermanentCombatData] = None
    exploration_patterns: Dict[str, int] = None
    item_preferences: Dict[str, float] = None
    team_synergies: Dict[str, float] = None
    unique_strategies: List[str] = None
    
    def __post_init__(self):
        if self.signature_skills is None:
            self.signature_skills = {}
        if self.combat_expertise is None:
            self.combat_expertise = {}
        if self.exploration_patterns is None:
            self.exploration_patterns = {}
        if self.item_preferences is None:
            self.item_preferences = {}
        if self.team_synergies is None:
            self.team_synergies = {}
        if self.unique_strategies is None:
            self.unique_strategies = []

class PermanentLearningDatabase:
    """영구 학습 데이터베이스"""
    
    def __init__(self, db_path: str = "ai_permanent_learning.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self._initialize_database()
        
        print(f"🗄️ 영구 학습 데이터베이스 초기화: {self.db_path}")
    
    def _initialize_database(self):
        """데이터베이스 초기화"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS ai_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ai_name TEXT NOT NULL,
                job_class TEXT NOT NULL,
                knowledge_type TEXT NOT NULL,
                data_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER DEFAULT 1
            )
        """)
        
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ai_name TEXT NOT NULL,
                session_type TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                performance_improvement REAL NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT NOT NULL
            )
        """)
        
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS global_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_name TEXT UNIQUE NOT NULL,
                stat_value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        self.connection.commit()
    
    def save_knowledge(self, ai_name: str, job_class: str, knowledge_type: str, data: Any):
        """지식 저장"""
        data_json = json.dumps(data, ensure_ascii=False, default=str)
        now = datetime.now().isoformat()
        
        # 기존 데이터 확인
        cursor = self.connection.execute("""
            SELECT id, version FROM ai_knowledge 
            WHERE ai_name = ? AND job_class = ? AND knowledge_type = ?
        """, (ai_name, job_class, knowledge_type))
        
        existing = cursor.fetchone()
        
        if existing:
            # 업데이트
            self.connection.execute("""
                UPDATE ai_knowledge 
                SET data_json = ?, updated_at = ?, version = version + 1
                WHERE id = ?
            """, (data_json, now, existing[0]))
        else:
            # 새로 삽입
            self.connection.execute("""
                INSERT INTO ai_knowledge (ai_name, job_class, knowledge_type, data_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ai_name, job_class, knowledge_type, data_json, now, now))
        
        self.connection.commit()
    
    def load_knowledge(self, ai_name: str, job_class: str, knowledge_type: str) -> Optional[Any]:
        """지식 로드"""
        cursor = self.connection.execute("""
            SELECT data_json FROM ai_knowledge 
            WHERE ai_name = ? AND job_class = ? AND knowledge_type = ?
            ORDER BY updated_at DESC LIMIT 1
        """, (ai_name, job_class, knowledge_type))
        
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None
    
    def get_all_ai_knowledge(self, ai_name: str) -> Dict[str, Any]:
        """AI의 모든 지식 가져오기"""
        cursor = self.connection.execute("""
            SELECT knowledge_type, data_json FROM ai_knowledge 
            WHERE ai_name = ?
            ORDER BY updated_at DESC
        """, (ai_name,))
        
        knowledge = {}
        for row in cursor.fetchall():
            knowledge[row[0]] = json.loads(row[1])
        
        return knowledge
    
    def get_job_skills(self, job_name: str) -> List[str]:
        """직업별 스킬 목록 가져오기"""
        try:
            # AI별 지식에서 스킬 정보 추출
            ai_name = f"{job_name}_AI"
            knowledge = self.load_knowledge(ai_name, job_name, "job_specific_knowledge")
            
            if knowledge and "signature_skills" in knowledge:
                # signature_skills가 딕셔너리인 경우 (PermanentSkillData 형태)
                skills = knowledge["signature_skills"]
                if isinstance(skills, dict):
                    return list(skills.keys())
                # 리스트인 경우
                elif isinstance(skills, list):
                    return skills
            
            # 기본 스킬 목록 반환 (더미 데이터)
            return [f"{job_name}_기본공격", f"{job_name}_특수기"]
            
        except Exception as e:
            # 오류 발생 시 빈 목록 반환
            return []
    
    def get_job_strategies(self, job_name: str) -> List[str]:
        """직업별 전략 목록 가져오기"""
        try:
            # AI별 지식에서 전략 정보 추출
            ai_name = f"{job_name}_AI"
            knowledge = self.load_knowledge(ai_name, job_name, "job_specific_knowledge")
            
            if knowledge and "unique_strategies" in knowledge:
                # unique_strategies가 리스트인 경우
                strategies = knowledge["unique_strategies"]
                if isinstance(strategies, list):
                    return strategies
                # 딕셔너리인 경우
                elif isinstance(strategies, dict):
                    return list(strategies.keys())
            
            # 기본 전략 목록 반환 (더미 데이터)
            return [f"{job_name}_공격전략", f"{job_name}_방어전략"]
            
        except Exception as e:
            # 오류 발생 시 빈 목록 반환
            return []
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 통계 가져오기"""
        try:
            cursor = self.connection.execute("""
                SELECT COUNT(*) as total_knowledge,
                       COUNT(DISTINCT ai_name) as unique_ais,
                       COUNT(DISTINCT job_class) as learned_jobs
                FROM ai_knowledge
            """)
            
            stats = cursor.fetchone()
            return {
                "total_knowledge": stats[0] if stats else 0,
                "unique_ais": stats[1] if stats else 0,
                "learned_jobs": stats[2] if stats else 0
            }
        except Exception as e:
            return {
                "total_knowledge": 0,
                "unique_ais": 0, 
                "learned_jobs": 0
            }
    
    def save_backup_data(self):
        """학습 데이터 백업 저장"""
        try:
            # 데이터베이스 백업
            backup_path = f"ai_permanent_learning_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # 통계 정보 저장
            stats = self.get_learning_statistics()
            self.connection.execute("""
                INSERT OR REPLACE INTO global_statistics (stat_name, stat_value, updated_at)
                VALUES ('last_backup', ?, ?)
            """, (datetime.now().isoformat(), datetime.now().isoformat()))
            
            self.connection.commit()
            print(f"💾 학습 데이터 백업 완료: {backup_path}")
            
        except Exception as e:
            print(f"⚠️ 백업 저장 실패: {e}")
    
    def cleanup_old_data(self, days_old: int = 30):
        """오래된 데이터 정리"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            self.connection.execute("""
                DELETE FROM ai_knowledge 
                WHERE updated_at < ? AND knowledge_type = 'temporary_data'
            """, (cutoff_date,))
            self.connection.commit()
        except Exception as e:
            print(f"데이터 정리 실패: {e}")

class JobSpecificDatasetGenerator:
    """직업별 전문 데이터셋 생성기"""
    
    def __init__(self):
        self.job_datasets: Dict[JobClass, JobSpecificKnowledge] = {}
        self.db = PermanentLearningDatabase()
        
        print("📊 직업별 데이터셋 생성기 초기화!")
    
    def generate_all_job_datasets(self):
        """27개 직업 전체 데이터셋 생성"""
        print("🏭 === 27개 직업 데이터셋 대량 생성 시작! ===")
        
        for job_class in JobClass:
            print(f"📊 {job_class.value} 데이터셋 생성 중...")
            dataset = self._generate_job_dataset(job_class)
            self.job_datasets[job_class] = dataset
            
            # 영구 저장
            self.db.save_knowledge(
                f"{job_class.value}_AI", 
                job_class.value, 
                "job_specific_knowledge", 
                asdict(dataset)
            )
        
        print(f"✅ 27개 직업 데이터셋 생성 완료!")
        self._generate_summary_report()
    
    def generate_job_dataset(self, job_class: JobClass) -> JobSpecificKnowledge:
        """외부에서 호출 가능한 단일 직업 데이터셋 생성"""
        print(f"📊 {job_class.value} 데이터셋 생성 중...")
        dataset = self._generate_job_dataset(job_class)
        
        # 영구 저장
        self.db.save_knowledge(
            f"{job_class.value}_AI", 
            job_class.value, 
            "job_specific_knowledge", 
            asdict(dataset)
        )
        
        self.job_datasets[job_class] = dataset
        print(f"✅ {job_class.value} 데이터셋 생성 완료!")
        return dataset
    
    def _generate_job_dataset(self, job_class: JobClass) -> JobSpecificKnowledge:
        """특정 직업 데이터셋 생성"""
        knowledge = JobSpecificKnowledge(job_class=job_class)
        
        # 직업별 시그니처 스킬 데이터
        knowledge.signature_skills = self._generate_signature_skills(job_class)
        
        # 전투 전문성 데이터
        knowledge.combat_expertise = self._generate_combat_expertise(job_class)
        
        # 탐험 패턴 데이터
        knowledge.exploration_patterns = self._generate_exploration_patterns(job_class)
        
        # 아이템 선호도 데이터
        knowledge.item_preferences = self._generate_item_preferences(job_class)
        
        # 팀 시너지 데이터
        knowledge.team_synergies = self._generate_team_synergies(job_class)
        
        # 고유 전략 데이터
        knowledge.unique_strategies = self._generate_unique_strategies(job_class)
        
        # 숙련도 초기값 설정
        knowledge.mastery_level = random.uniform(1.0, 3.0)
        
        return knowledge
    
    def _generate_signature_skills(self, job_class: JobClass) -> Dict[str, PermanentSkillData]:
        """직업별 시그니처 스킬 데이터"""
        skill_datasets = {
            JobClass.WARRIOR: {
                "방패_강타": PermanentSkillData("방패_강타", synergy_skills=["파괴의_일격"], best_situation="근접전투"),
                "파괴의_일격": PermanentSkillData("파괴의_일격", synergy_skills=["방패_강타"], best_situation="마무리타격"),
                "도발": PermanentSkillData("도발", synergy_skills=["방어태세"], best_situation="어그로관리"),
                "방어태세": PermanentSkillData("방어태세", synergy_skills=["도발"], best_situation="생존전략")
            },
            JobClass.ARCHMAGE: {
                "마력_파동": PermanentSkillData("마력_파동", synergy_skills=["마력_폭발"], best_situation="광역공격"),
                "마력_폭발": PermanentSkillData("마력_폭발", synergy_skills=["마력_파동"], best_situation="마무리기"),
                "메테오": PermanentSkillData("메테오", synergy_skills=["플레어"], best_situation="대규모전투"),
                "텔레포트": PermanentSkillData("텔레포트", synergy_skills=["시간정지"], best_situation="위치선점")
            },
            JobClass.ROGUE: {
                "독침": PermanentSkillData("독침", synergy_skills=["암살"], best_situation="지속딜"),
                "암살": PermanentSkillData("암살", synergy_skills=["독침"], best_situation="일격필살"),
                "은신": PermanentSkillData("은신", synergy_skills=["기습"], best_situation="선제공격"),
                "자물쇠해제": PermanentSkillData("자물쇠해제", best_situation="탐험지원")
            },
            JobClass.ARCHER: {
                "삼연사": PermanentSkillData("삼연사", synergy_skills=["관통사격"], best_situation="다중타겟"),
                "관통사격": PermanentSkillData("관통사격", synergy_skills=["삼연사"], best_situation="정렬된적"),
                "지원사격": PermanentSkillData("지원사격", synergy_skills=["조준"], best_situation="팀지원"),
                "조준": PermanentSkillData("조준", synergy_skills=["지원사격"], best_situation="정확도증가")
            },
            JobClass.ENGINEER: {
                "레이저_사격": PermanentSkillData("레이저_사격", synergy_skills=["메가_레이저"], best_situation="원거리공격"),
                "메가_레이저": PermanentSkillData("메가_레이저", synergy_skills=["레이저_사격"], best_situation="강력한일격"),
                "기계조작": PermanentSkillData("기계조작", best_situation="기믹활용"),
                "장비수리": PermanentSkillData("장비수리", best_situation="유지보수")
            }
        }
        
        return skill_datasets.get(job_class, {
            "기본공격": PermanentSkillData("기본공격", best_situation="일반전투"),
            "특수기술": PermanentSkillData("특수기술", best_situation="특수상황")
        })
    
    def _generate_combat_expertise(self, job_class: JobClass) -> Dict[str, PermanentCombatData]:
        """전투 전문성 데이터"""
        combat_patterns = {
            JobClass.WARRIOR: {
                "고블린": PermanentCombatData("고블린", effective_strategies=["정면돌파", "방패방어"]),
                "오크": PermanentCombatData("오크", effective_strategies=["도발후집중공격"]),
                "드래곤": PermanentCombatData("드래곤", effective_strategies=["팀워크중시", "장기전준비"])
            },
            JobClass.ARCHMAGE: {
                "고블린": PermanentCombatData("고블린", effective_strategies=["광역마법", "마력절약"]),
                "언데드": PermanentCombatData("언데드", effective_strategies=["성속성마법", "정화주문"]),
                "악마": PermanentCombatData("악마", effective_strategies=["봉인마법", "신성마법"])
            },
            JobClass.ROGUE: {
                "경비병": PermanentCombatData("경비병", effective_strategies=["은신기습", "독사용"]),
                "마법사": PermanentCombatData("마법사", effective_strategies=["근접전환유도", "신속처리"]),
                "궁수": PermanentCombatData("궁수", effective_strategies=["거리좁히기", "연막탄"])
            }
        }
        
        return combat_patterns.get(job_class, {
            "일반몬스터": PermanentCombatData("일반몬스터", effective_strategies=["기본전술"])
        })
    
    def _generate_exploration_patterns(self, job_class: JobClass) -> Dict[str, int]:
        """탐험 패턴 데이터"""
        patterns = {
            JobClass.WARRIOR: {"정면돌파": 8, "신중탐험": 4, "위험회피": 2},
            JobClass.ARCHMAGE: {"비밀탐색": 9, "마법감지": 8, "안전우선": 6},
            JobClass.ROGUE: {"은밀탐험": 10, "함정탐지": 9, "보물수색": 8},
            JobClass.ARCHER: {"원거리정찰": 9, "고지점령": 7, "경계태세": 8},
            JobClass.ENGINEER: {"기계분석": 10, "시스템해킹": 8, "효율탐험": 7}
        }
        
        return patterns.get(job_class, {"기본탐험": 5, "신중행동": 5})
    
    def _generate_item_preferences(self, job_class: JobClass) -> Dict[str, float]:
        """아이템 선호도 데이터"""
        preferences = {
            JobClass.WARRIOR: {"무기": 0.9, "방어구": 0.8, "체력포션": 0.7, "방패": 0.9},
            JobClass.ARCHMAGE: {"마법서": 0.9, "마나포션": 0.8, "마법재료": 0.7, "지팡이": 0.9},
            JobClass.ROGUE: {"단검": 0.9, "독": 0.8, "은신도구": 0.7, "자물쇠도구": 0.8},
            JobClass.ARCHER: {"활": 0.9, "화살": 0.8, "조준경": 0.7, "가벼운갑옷": 0.6},
            JobClass.ENGINEER: {"도구": 0.9, "기계부품": 0.8, "배터리": 0.7, "설계도": 0.8}
        }
        
        return preferences.get(job_class, {"일반아이템": 0.5})
    
    def _generate_team_synergies(self, job_class: JobClass) -> Dict[str, float]:
        """팀 시너지 데이터"""
        synergies = {
            JobClass.WARRIOR: {"아크메이지": 0.8, "신관": 0.9, "궁수": 0.7, "바드": 0.6},
            JobClass.ARCHMAGE: {"전사": 0.8, "도적": 0.6, "시간술사": 0.9, "연금술사": 0.7},
            JobClass.ROGUE: {"궁수": 0.8, "암살자": 0.9, "바드": 0.7, "전사": 0.5},
            JobClass.ARCHER: {"전사": 0.7, "도적": 0.8, "바드": 0.8, "기계공학자": 0.6},
            JobClass.ENGINEER: {"아크메이지": 0.8, "연금술사": 0.9, "시간술사": 0.7, "차원술사": 0.8}
        }
        
        return synergies.get(job_class, {"기본협력": 0.5})
    
    def _generate_unique_strategies(self, job_class: JobClass) -> List[str]:
        """고유 전략 데이터"""
        strategies = {
            JobClass.WARRIOR: ["방패벽전술", "도발집중전술", "최후의저항", "팀보호우선"],
            JobClass.ARCHMAGE: ["마법콤보연계", "원소상성활용", "마나효율관리", "광역제압전술"],
            JobClass.ROGUE: ["기습암살전술", "독중첩전략", "은신재배치", "약점공략집중"],
            JobClass.ARCHER: ["거리유지전술", "조준포인트축적", "지원사격활용", "고지점령우선"],
            JobClass.ENGINEER: ["기계활용전술", "시스템최적화", "효율성우선", "기술적해결책"]
        }
        
        return strategies.get(job_class, ["기본전략", "상황적응"])
    
    def _generate_summary_report(self):
        """요약 보고서 생성"""
        print("\n📊 === 직업별 데이터셋 생성 완료 보고서 ===")
        
        total_skills = 0
        total_strategies = 0
        
        for job_class, knowledge in self.job_datasets.items():
            skill_count = len(knowledge.signature_skills)
            strategy_count = len(knowledge.unique_strategies)
            
            total_skills += skill_count
            total_strategies += strategy_count
            
            print(f"✅ {job_class.value}:")
            print(f"   스킬 데이터: {skill_count}개")
            print(f"   전투 전문성: {len(knowledge.combat_expertise)}개")
            print(f"   고유 전략: {strategy_count}개")
            print(f"   숙련도: {knowledge.mastery_level:.1f}/10.0")
        
        print(f"\n📈 총계:")
        print(f"   전체 직업: {len(JobClass)}개")
        print(f"   총 스킬 데이터: {total_skills}개")
        print(f"   총 전략 데이터: {total_strategies}개")
        print(f"   데이터베이스 크기: 영구 저장 완료")

class PermanentAIEvolutionSystem:
    """영구적 AI 진화 시스템"""
    
    def __init__(self):
        self.db = PermanentLearningDatabase()
        self.dataset_generator = JobSpecificDatasetGenerator()
        self.evolution_active = False
        self.evolution_thread = None
        
        print("🧬 영구적 AI 진화 시스템 초기화!")
    
    def start_permanent_evolution(self):
        """영구 진화 시작"""
        print("♾️ === 영구적 AI 진화 시작! ===")
        print("   💡 컴퓨터를 꺼도 다시 켜면 이어서 진화합니다!")
        print("   🧠 AI가 평생에 걸쳐 계속 발전합니다!")
        
        self.evolution_active = True
        
        def evolution_loop():
            generation = self._load_generation_count()
            
            while self.evolution_active:
                generation += 1
                print(f"🧬 제{generation}세대 진화 시작...")
                
                # 각 직업별 AI 진화
                for job_class in JobClass:
                    self._evolve_job_ai(job_class, generation)
                
                # 진화 데이터 저장
                self._save_generation_count(generation)
                
                print(f"✅ 제{generation}세대 진화 완료!")
                
                # 1시간마다 진화 (실제로는 더 짧게 설정 가능)
                time.sleep(3600)
        
        self.evolution_thread = threading.Thread(target=evolution_loop, daemon=True)
        self.evolution_thread.start()
    
    def _evolve_job_ai(self, job_class: JobClass, generation: int):
        """특정 직업 AI 진화"""
        ai_name = f"{job_class.value}_AI"
        
        # 기존 지식 로드
        existing_knowledge = self.db.load_knowledge(ai_name, job_class.value, "job_specific_knowledge")
        
        if existing_knowledge:
            # 기존 지식 개선
            knowledge = JobSpecificKnowledge(**existing_knowledge)
            knowledge.mastery_level = min(knowledge.mastery_level + random.uniform(0.1, 0.3), 10.0)
            
            # 새로운 전략 발견 (10% 확률)
            if random.random() < 0.1:
                new_strategy = f"진화전략_G{generation}_{random.randint(1000, 9999)}"
                knowledge.unique_strategies.append(new_strategy)
        else:
            # 새로운 지식 생성
            knowledge = self.dataset_generator._generate_job_dataset(job_class)
        
        # 진화된 지식 저장
        self.db.save_knowledge(ai_name, job_class.value, "job_specific_knowledge", asdict(knowledge))
        
        # 진화 기록
        evolution_record = {
            "generation": generation,
            "job_class": job_class.value,
            "mastery_improvement": 0.2,
            "new_strategies": len(knowledge.unique_strategies),
            "evolution_time": datetime.now().isoformat()
        }
        
        self.db.save_knowledge(ai_name, job_class.value, f"evolution_g{generation}", evolution_record)
    
    def _load_generation_count(self) -> int:
        """세대 수 로드"""
        cursor = self.db.connection.execute("""
            SELECT stat_value FROM global_statistics WHERE stat_name = 'current_generation'
        """)
        result = cursor.fetchone()
        return int(result[0]) if result else 0
    
    def _save_generation_count(self, generation: int):
        """세대 수 저장"""
        self.db.connection.execute("""
            INSERT OR REPLACE INTO global_statistics (stat_name, stat_value, updated_at)
            VALUES ('current_generation', ?, ?)
        """, (str(generation), datetime.now().isoformat()))
        self.db.connection.commit()
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """진화 상태 확인"""
        generation = self._load_generation_count()
        
        status = {
            "current_generation": generation,
            "evolution_active": self.evolution_active,
            "total_jobs": len(JobClass),
            "database_size": self.db.db_path.stat().st_size if self.db.db_path.exists() else 0,
            "last_evolution": "진행중" if self.evolution_active else "중지됨"
        }
        
        return status

def demo_permanent_learning_system():
    """영구 학습 시스템 데모"""
    print("♾️ === 영구적 AI 학습 시스템 데모! ===")
    print()
    
    # 1. 직업별 데이터셋 대량 생성
    dataset_generator = JobSpecificDatasetGenerator()
    dataset_generator.generate_all_job_datasets()
    
    print("\n" + "="*60 + "\n")
    
    # 2. 영구 진화 시스템 시작
    evolution_system = PermanentAIEvolutionSystem()
    evolution_system.start_permanent_evolution()
    
    # 3. 잠시 진화 과정 관찰
    print("🔍 5초간 진화 과정 관찰...")
    time.sleep(5)
    
    # 4. 진화 상태 확인
    status = evolution_system.get_evolution_status()
    print("\n📊 현재 진화 상태:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # 5. 진화 중지 (데모용)
    evolution_system.evolution_active = False
    
    print("\n✨ 영구 학습 시스템 데모 완료!")
    print("💾 모든 학습 데이터가 영구적으로 저장되었습니다!")
    print("🔄 컴퓨터를 껐다 켜도 AI는 계속 발전합니다!")

if __name__ == "__main__":
    demo_permanent_learning_system()
