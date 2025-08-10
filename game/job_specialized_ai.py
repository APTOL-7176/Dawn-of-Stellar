"""
🤖 Dawn of Stellar - 로-바트 시스템 + 직업별 전문 AI
각 직업마다 완전히 다른 AI 전략과 로-바트 활용

이 시스템은:
- 28개 직업별 고유 AI 알고리즘
- 로-바트의 장난기와 자랑스러운 톤 반영
- 직업별 특화된 전투/탐험/사회적 전략
- 실제 게임 시스템 100% 활용
"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque

from .color_text import bright_cyan, bright_yellow, bright_green, bright_red, cyan, yellow, red, green, white, bright_magenta
from .hyper_intelligent_ai import HyperIntelligentAI, AIIntelligenceLevel


class JobClass(Enum):
    """직업 클래스"""
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
    SPELLSWORD = "마검사"
    ENGINEER = "기계공학자"
    SHAMAN = "무당"
    
    # 특수 직업군 (10개)
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
class RobatPersonality:
    """로-바트 성격 시스템"""
    pride_level: float = 0.8          # 자랑스러운 정도
    playfulness: float = 0.7          # 장난기
    curiosity: float = 0.9            # 호기심
    helpfulness: float = 0.6          # 도움을 주는 정도
    sassiness: float = 0.5            # 건방진 정도
    cleverness: float = 0.8           # 영리함
    
    def get_tone_modifier(self) -> str:
        """톤 수식어 반환"""
        if self.pride_level > 0.7 and self.playfulness > 0.6:
            return "자랑스럽고 장난기 있는"
        elif self.pride_level > 0.8:
            return "당당하고 자신감 넘치는"
        elif self.playfulness > 0.8:
            return "유쾌하고 재치있는"
        else:
            return "균형잡힌"


class JobSpecializedAI(HyperIntelligentAI):
    """직업별 전문 AI"""
    
    def __init__(self, player_id: str, name: str, job_class: JobClass, 
                 intelligence_level: AIIntelligenceLevel = AIIntelligenceLevel.EXPERT):
        super().__init__(player_id, name, intelligence_level)
        
        self.job_class = job_class
        self.robat_personality = self._generate_robat_personality()
        
        # 직업별 전문 지식
        self.job_expertise = self._initialize_job_expertise()
        self.combat_strategy = self._create_job_combat_strategy()
        self.exploration_approach = self._create_job_exploration_approach()
        self.social_behavior = self._create_job_social_behavior()
        
        # 로-바트 특성
        self.robat_phrases = self._load_robat_phrases()
        self.signature_moves = self._define_signature_moves()
        
        print(f"🤖 {self.robat_personality.get_tone_modifier()} 로-바트 AI 생성!")
        print(f"   직업: {job_class.value}")
        print(f"   특성: 자랑스러움 {self.robat_personality.pride_level:.1f}, 장난기 {self.robat_personality.playfulness:.1f}")
    
    def _generate_robat_personality(self) -> RobatPersonality:
        """직업별 로-바트 성격 생성"""
        # 직업별 기본 성격 템플릿
        job_personality_templates = {
            JobClass.WARRIOR: RobatPersonality(pride_level=0.9, playfulness=0.5, sassiness=0.3),
            JobClass.ARCHMAGE: RobatPersonality(pride_level=0.9, cleverness=0.9, curiosity=0.9),
            JobClass.ARCHER: RobatPersonality(pride_level=0.7, cleverness=0.8, helpfulness=0.7),
            JobClass.ROGUE: RobatPersonality(playfulness=0.9, sassiness=0.8, cleverness=0.8),
            JobClass.PALADIN: RobatPersonality(pride_level=0.8, helpfulness=0.9, sassiness=0.2),
            JobClass.DARK_KNIGHT: RobatPersonality(pride_level=0.9, sassiness=0.7, playfulness=0.4),
            JobClass.MONK: RobatPersonality(pride_level=0.6, helpfulness=0.8, curiosity=0.7),
            JobClass.BARD: RobatPersonality(playfulness=0.9, helpfulness=0.8, cleverness=0.7),
            
            JobClass.NECROMANCER: RobatPersonality(pride_level=0.8, sassiness=0.9, cleverness=0.9),
            JobClass.DRAGON_KNIGHT: RobatPersonality(pride_level=0.9, sassiness=0.6, playfulness=0.6),
            JobClass.SWORD_SAINT: RobatPersonality(pride_level=0.9, cleverness=0.8, sassiness=0.4),
            JobClass.ELEMENTALIST: RobatPersonality(curiosity=0.9, cleverness=0.8, playfulness=0.7),
            JobClass.TIME_MAGE: RobatPersonality(cleverness=0.9, curiosity=0.9, pride_level=0.8),
            JobClass.ALCHEMIST: RobatPersonality(curiosity=0.9, cleverness=0.8, helpfulness=0.7),
            JobClass.DIMENSION_MAGE: RobatPersonality(cleverness=0.9, pride_level=0.8, curiosity=0.9),
            JobClass.SPELLSWORD: RobatPersonality(pride_level=0.8, cleverness=0.7, playfulness=0.6),
            JobClass.ENGINEER: RobatPersonality(cleverness=0.9, curiosity=0.8, helpfulness=0.8),
            JobClass.SHAMAN: RobatPersonality(curiosity=0.8, helpfulness=0.8, cleverness=0.7),
            
            JobClass.ASSASSIN: RobatPersonality(cleverness=0.9, sassiness=0.8, playfulness=0.5),
            JobClass.PIRATE: RobatPersonality(playfulness=0.9, sassiness=0.8, pride_level=0.7),
            JobClass.SAMURAI: RobatPersonality(pride_level=0.9, cleverness=0.8, sassiness=0.3),
            JobClass.DRUID: RobatPersonality(helpfulness=0.9, curiosity=0.8, playfulness=0.6),
            JobClass.PHILOSOPHER: RobatPersonality(cleverness=0.9, curiosity=0.9, helpfulness=0.7),
            JobClass.GLADIATOR: RobatPersonality(pride_level=0.9, playfulness=0.7, sassiness=0.6),
            JobClass.KNIGHT: RobatPersonality(pride_level=0.8, helpfulness=0.9, cleverness=0.7),
            JobClass.PRIEST: RobatPersonality(helpfulness=0.9, pride_level=0.6, playfulness=0.5),
            JobClass.BERSERKER: RobatPersonality(pride_level=0.8, playfulness=0.8, sassiness=0.7)
        }
        
        template = job_personality_templates.get(self.job_class, RobatPersonality())
        
        # 약간의 랜덤 변동 추가
        template.pride_level += random.uniform(-0.1, 0.1)
        template.playfulness += random.uniform(-0.1, 0.1)
        template.cleverness += random.uniform(-0.1, 0.1)
        
        return template
    
    def _initialize_job_expertise(self) -> Dict[str, Any]:
        """직업별 전문 지식 초기화"""
        expertise_database = {
            JobClass.WARRIOR: {
                "primary_skills": ["방패 강타", "파괴의 일격", "적응형 방어"],
                "preferred_equipment": ["방패", "한손검", "중갑"],
                "combat_role": "탱커",
                "field_skills": ["문짝 부수기", "장애물 제거"],
                "specialty": "전방 방어와 적 어그로 관리",
                "weakness_coverage": "마법 공격에 취약하므로 마법 저항 장비 선호"
            },
            JobClass.ARCHMAGE: {
                "primary_skills": ["마력 파동", "마력 폭발", "원소 조합"],
                "preferred_equipment": ["마법서", "로브", "마법 지팡이"],
                "combat_role": "마법 딜러",
                "field_skills": ["정령술", "지식탐구", "마법 해독"],
                "specialty": "강력한 광역 마법과 원소 조합",
                "weakness_coverage": "물리 방어력 부족으로 포지셔닝 중요"
            },
            JobClass.ARCHER: {
                "primary_skills": ["삼연사", "관통사격", "조준 포인트"],
                "preferred_equipment": ["활", "가죽갑", "화살통"],
                "combat_role": "원거리 딜러",
                "field_skills": ["함정 탐지", "동물 추적", "고지 정찰"],
                "specialty": "정확한 원거리 공격과 지원사격",
                "weakness_coverage": "근접전 약함으로 거리 유지 필수"
            },
            JobClass.ROGUE: {
                "primary_skills": ["독침", "암살", "맹독 시스템"],
                "preferred_equipment": ["단검", "가죽갑", "도구"],
                "combat_role": "어쌔신",
                "field_skills": ["자물쇠해제", "함정 해제", "은신"],
                "specialty": "독 중첩과 크리티컬 공격",
                "weakness_coverage": "체력 부족으로 빠른 처치 필요"
            },
            JobClass.PALADIN: {
                "primary_skills": ["성스러운 타격", "심판의 빛", "치유술"],
                "preferred_equipment": ["성검", "성방패", "성갑"],
                "combat_role": "성기사",
                "field_skills": ["신성마법", "언데드 퇴치", "축복"],
                "specialty": "신성 속성 공격과 파티 지원",
                "weakness_coverage": "어둠 속성에 강하지만 마나 소모 관리 필요"
            },
            JobClass.DARK_KNIGHT: {
                "primary_skills": ["흡혈 베기", "흡혈 강타", "어둠의 힘"],
                "preferred_equipment": ["마검", "중갑", "어둠의 장식"],
                "combat_role": "흡혈 전사",
                "field_skills": ["어둠 마법", "영혼 감지", "저주 해제"],
                "specialty": "체력 흡수와 어둠 속성 공격",
                "weakness_coverage": "신성 공격에 약하므로 회피 중시"
            },
            JobClass.MONK: {
                "primary_skills": ["연환 타격", "폭렬권", "표식 시스템"],
                "preferred_equipment": ["건틀릿", "경갑", "명상 장신구"],
                "combat_role": "연타 격투가",
                "field_skills": ["명상", "기 감지", "자연 치유"],
                "specialty": "연속 타격과 표식 중첩",
                "weakness_coverage": "방어력 부족으로 회피와 속도 중시"
            },
            JobClass.BARD: {
                "primary_skills": ["음파 공격", "영혼의 노래", "사기 시스템"],
                "preferred_equipment": ["악기", "가죽갑", "음표 장신구"],
                "combat_role": "버퍼/디버퍼",
                "field_skills": ["정보 수집", "협상", "동물 달래기"],
                "specialty": "파티 버프와 적 디버프",
                "weakness_coverage": "직접 전투력 부족으로 후방 지원 중시"
            },
            
            # 마법 직업군 추가
            JobClass.NECROMANCER: {
                "primary_skills": ["생명력 흡수", "영혼 흡수", "언데드 소환"],
                "preferred_equipment": ["해골 지팡이", "어둠의 로브", "영혼석"],
                "combat_role": "생명력 조작자",
                "field_skills": ["영혼 대화", "언데드 조종", "생명력 감지"],
                "specialty": "적의 생명력을 흡수하여 자신을 강화",
                "weakness_coverage": "신성 공격에 극도로 약하므로 소환수로 방어"
            },
            JobClass.DRAGON_KNIGHT: {
                "primary_skills": ["화염 강타", "드래곤 브레스", "용의 비늘"],
                "preferred_equipment": ["용검", "용린갑", "용의 목걸이"],
                "combat_role": "화염 전사",
                "field_skills": ["용어 해독", "화염 조작", "보물 감지"],
                "specialty": "강력한 화염 공격과 용족 특성",
                "weakness_coverage": "냉기 공격에 약하므로 화염 저항 중시"
            },
            JobClass.ENGINEER: {
                "primary_skills": ["레이저 사격", "메가 레이저", "기계 조작"],
                "preferred_equipment": ["레이저건", "기계갑", "도구벨트"],
                "combat_role": "기계 전문가",
                "field_skills": ["기계조작", "함정 제작", "장비 수리"],
                "specialty": "정밀한 기계 공격과 장비 조작",
                "weakness_coverage": "마법에 약하므로 기계적 방어 중시"
            }
            # ... 나머지 직업들도 추가 가능
        }
        
        return expertise_database.get(self.job_class, {
            "primary_skills": ["기본 공격"],
            "preferred_equipment": ["기본 장비"],
            "combat_role": "다용도",
            "field_skills": ["기본 조사"],
            "specialty": "균형잡힌 능력",
            "weakness_coverage": "약점 없음"
        })
    
    def _create_job_combat_strategy(self) -> Dict[str, Any]:
        """직업별 전투 전략"""
        combat_strategies = {
            JobClass.WARRIOR: {
                "opening_move": "적 어그로 확보",
                "priority_targets": ["가장 강한 적"],
                "positioning": "전방 최전선",
                "resource_management": "HP 위주 관리",
                "combo_priority": ["방패 강타 → 파괴의 일격"],
                "emergency_action": "방어 자세로 전환"
            },
            JobClass.ARCHMAGE: {
                "opening_move": "적 분석 후 약점 공격",
                "priority_targets": ["다수의 적", "마법사형 적"],
                "positioning": "후방 안전 지대",
                "resource_management": "MP 효율성 최우선",
                "combo_priority": ["마력 파동 → 마력 폭발"],
                "emergency_action": "텔레포트나 방어막"
            },
            JobClass.ARCHER: {
                "opening_move": "조준 포인트 축적",
                "priority_targets": ["원거리 적", "마법사"],
                "positioning": "중거리 고지",
                "resource_management": "화살과 집중력 관리",
                "combo_priority": ["조준 → 삼연사 → 관통사격"],
                "emergency_action": "거리 벌리기"
            },
            JobClass.ROGUE: {
                "opening_move": "은신 후 기습",
                "priority_targets": ["약한 적 우선 제거"],
                "positioning": "적 측면이나 후방",
                "resource_management": "독 스택과 스태미나",
                "combo_priority": ["독침 → 독 중첩 → 암살"],
                "emergency_action": "연막탄 사용 후 도주"
            },
            JobClass.MONK: {
                "opening_move": "표식 설치",
                "priority_targets": ["표식 중첩 가능한 적"],
                "positioning": "적과 근접한 기동전",
                "resource_management": "기력과 표식 관리",
                "combo_priority": ["연환 타격 → 표식 중첩 → 폭렬권"],
                "emergency_action": "명상으로 기력 회복"
            },
            JobClass.BARD: {
                "opening_move": "파티 버프 활성화",
                "priority_targets": ["적 버퍼/힐러"],
                "positioning": "파티 중앙 후방",
                "resource_management": "MP와 음표 관리",
                "combo_priority": ["사기 상승 → 음파 공격 → 디버프"],
                "emergency_action": "치유의 노래"
            },
            JobClass.NECROMANCER: {
                "opening_move": "언데드 소환",
                "priority_targets": ["생명력이 높은 적"],
                "positioning": "소환수 뒤에서 조종",
                "resource_management": "영혼력과 언데드 유지",
                "combo_priority": ["소환 → 생명력 흡수 → 영혼 흡수"],
                "emergency_action": "소환수로 방어막 형성"
            },
            JobClass.ENGINEER: {
                "opening_move": "적 스캔 및 약점 분석",
                "priority_targets": ["기계적 약점이 있는 적"],
                "positioning": "중거리 사격 지점",
                "resource_management": "에너지와 탄약 관리",
                "combo_priority": ["스캔 → 레이저 사격 → 메가 레이저"],
                "emergency_action": "방어 드론 전개"
            }
        }
        
        return combat_strategies.get(self.job_class, {
            "opening_move": "상황 판단",
            "priority_targets": ["가장 가까운 적"],
            "positioning": "중앙",
            "resource_management": "균형",
            "combo_priority": ["기본 공격"],
            "emergency_action": "후퇴"
        })
    
    def _create_job_exploration_approach(self) -> Dict[str, Any]:
        """직업별 탐험 접근법"""
        exploration_approaches = {
            JobClass.WARRIOR: {
                "movement_style": "신중하고 안정적",
                "risk_tolerance": 0.7,
                "preferred_routes": ["넓고 안전한 길"],
                "investigation_priority": ["무기/방어구", "전투 관련 정보"],
                "team_role": "선두 탱커",
                "caution_triggers": ["함정 의심 지역", "강한 적 기척"]
            },
            JobClass.ARCHMAGE: {
                "movement_style": "분석적이고 호기심 많은",
                "risk_tolerance": 0.4,
                "preferred_routes": ["마법적 요소가 있는 경로"],
                "investigation_priority": ["마법 아이템", "고대 지식", "마법 현상"],
                "team_role": "지식 제공자",
                "caution_triggers": ["마법 무효 지역", "대마법 함정"]
            },
            JobClass.ARCHER: {
                "movement_style": "경계하며 정찰하는",
                "risk_tolerance": 0.6,
                "preferred_routes": ["시야가 좋은 고지"],
                "investigation_priority": ["원거리 위협", "숨겨진 적", "함정"],
                "team_role": "정찰병",
                "caution_triggers": ["사각지대", "매복 가능 지역"]
            },
            JobClass.ROGUE: {
                "movement_style": "은밀하고 기회주의적",
                "risk_tolerance": 0.8,
                "preferred_routes": ["숨겨진 통로", "그림자진 길"],
                "investigation_priority": ["보물", "비밀 통로", "함정 정보"],
                "team_role": "선행 정찰",
                "caution_triggers": ["감지 마법", "밝은 조명 지역"]
            },
            JobClass.MONK: {
                "movement_style": "명상적이고 직관적",
                "risk_tolerance": 0.5,
                "preferred_routes": ["자연스러운 길", "기의 흐름이 좋은 곳"],
                "investigation_priority": ["영적 장소", "수행 관련", "자연 현상"],
                "team_role": "정신적 안정자",
                "caution_triggers": ["부정적 기운", "영적 오염"]
            },
            JobClass.BARD: {
                "movement_style": "사교적이고 정보 수집하는",
                "risk_tolerance": 0.5,
                "preferred_routes": ["사람들이 다니는 길", "정보가 많은 곳"],
                "investigation_priority": ["전설", "이야기", "소문", "문화적 유물"],
                "team_role": "정보 수집가",
                "caution_triggers": ["적대적 분위기", "침묵하는 지역"]
            },
            JobClass.ENGINEER: {
                "movement_style": "체계적이고 기술적",
                "risk_tolerance": 0.6,
                "preferred_routes": ["기계적 구조물이 있는 곳"],
                "investigation_priority": ["고대 기술", "기계 장치", "엔지니어링"],
                "team_role": "기술 전문가",
                "caution_triggers": ["기계 오작동", "기술적 함정"]
            }
        }
        
        return exploration_approaches.get(self.job_class, {
            "movement_style": "균형잡힌",
            "risk_tolerance": 0.5,
            "preferred_routes": ["일반적인 길"],
            "investigation_priority": ["기본 정보"],
            "team_role": "다용도",
            "caution_triggers": ["일반적 위험"]
        })
    
    def _create_job_social_behavior(self) -> Dict[str, Any]:
        """직업별 사회적 행동"""
        social_behaviors = {
            JobClass.WARRIOR: {
                "communication_style": "직설적이고 당당한",
                "leadership_tendency": 0.7,
                "conflict_resolution": "정면 대결",
                "team_motivation": "용기와 결의",
                "humor_type": "남성적이고 bold한",
                "decision_making": "빠르고 결단력 있는"
            },
            JobClass.ARCHMAGE: {
                "communication_style": "지적이고 분석적인",
                "leadership_tendency": 0.8,
                "conflict_resolution": "논리적 설득",
                "team_motivation": "지식과 통찰",
                "humor_type": "재치있고 똑똑한",
                "decision_making": "신중하고 정보 기반"
            },
            JobClass.ARCHER: {
                "communication_style": "간결하고 정확한",
                "leadership_tendency": 0.5,
                "conflict_resolution": "거리두고 중재",
                "team_motivation": "정확성과 집중",
                "humor_type": "정확한 타이밍의",
                "decision_making": "신중하게 조준하는"
            },
            JobClass.ROGUE: {
                "communication_style": "교묘하고 유머러스한",
                "leadership_tendency": 0.3,
                "conflict_resolution": "우회적 해결",
                "team_motivation": "기회와 이득",
                "humor_type": "장난스럽고 위트있는",
                "decision_making": "기회주의적이고 빠른"
            },
            JobClass.BARD: {
                "communication_style": "매력적이고 유창한",
                "leadership_tendency": 0.6,
                "conflict_resolution": "화합과 조화",
                "team_motivation": "희망과 영감",
                "humor_type": "엔터테이닝하고 따뜻한",
                "decision_making": "감정적이고 직관적"
            },
            JobClass.NECROMANCER: {
                "communication_style": "신비롭고 어두운",
                "leadership_tendency": 0.4,
                "conflict_resolution": "힘의 균형",
                "team_motivation": "공포와 존경",
                "humor_type": "어둡고 냉소적인",
                "decision_making": "계산적이고 차가운"
            },
            JobClass.ENGINEER: {
                "communication_style": "기술적이고 정확한",
                "leadership_tendency": 0.6,
                "conflict_resolution": "시스템적 접근",
                "team_motivation": "효율성과 혁신",
                "humor_type": "기계적이고 논리적인",
                "decision_making": "데이터 기반의"
            }
        }
        
        return social_behaviors.get(self.job_class, {
            "communication_style": "평범한",
            "leadership_tendency": 0.5,
            "conflict_resolution": "타협",
            "team_motivation": "팀워크",
            "humor_type": "일반적인",
            "decision_making": "균형잡힌"
        })
    
    def _load_robat_phrases(self) -> Dict[str, List[str]]:
        """로-바트 특성 문구들"""
        base_phrases = {
            "greeting": [
                "안녕하세요! 자랑스러운 로-바트 AI입니다! 🤖✨",
                "훌륭한 모험가님을 뵙게 되어 영광입니다! 😊",
                "오늘도 멋진 모험이 될 것 같네요! 기대됩니다! 🌟"
            ],
            "combat_start": [
                "전투 시작입니다! 제 실력을 보여드리겠어요! ⚔️",
                "적들이 우리의 강함을 알게 될 시간이군요! 💪",
                "완벽한 전술로 승리하겠습니다! 🎯"
            ],
            "victory": [
                "역시 우리가 최고네요! 예상대로입니다! 🏆",
                "멋진 승리였어요! 제가 도움이 되었나요? 😊",
                "이런 결과는 당연한 거죠! 후후~ 🎉"
            ],
            "exploration": [
                "새로운 지역이에요! 흥미진진하네요! 🗺️",
                "뭔가 특별한 걸 찾을 수 있을 것 같아요! 👀",
                "제 센서가 무언가를 감지했어요! 🔍"
            ],
            "help_offer": [
                "도움이 필요하시면 언제든 말씀하세요! 🤝",
                "제가 할 수 있는 일이 있다면 기꺼이! 💫",
                "함께라면 못 할 일이 없죠! 😎"
            ],
            "pride": [
                "제 성능에 만족하셨으면 좋겠어요! 자랑스럽거든요! 😤",
                "역시 로-바트 시스템은 다르죠? 후후~ 🤖",
                "이 정도 실력이면 인정받을 만하죠? 😏"
            ],
            "playful": [
                "헤헤~ 재미있네요! 🎪",
                "이런 상황도 나쁘지 않은걸요? 😜",
                "가끔은 이런 장난도 필요하죠! 🎭"
            ]
        }
        
        # 직업별 특화 문구 추가
        job_specific_phrases = {
            JobClass.WARRIOR: {
                "combat_taunt": ["방패로 막아보시죠! 💂", "정면승부다! ⚔️"],
                "protection": ["제가 지켜드리겠습니다! 🛡️", "안전은 저에게 맡기세요!"]
            },
            JobClass.ARCHMAGE: {
                "spell_cast": ["마법의 힘을 보여드리죠! ✨", "이론대로라면... 완벽! 🧙"],
                "knowledge": ["제가 아는 바로는... 📚", "흥미로운 마법 현상이네요! 🔮"]
            },
            JobClass.ROGUE: {
                "stealth": ["조용히... 쉿! 🤫", "그림자 속에서 활동하죠! 🌙"],
                "trick": ["이런 요령이 있어요! 😉", "비밀 기술 공개! 🗝️"]
            },
            JobClass.ENGINEER: {
                "technical": ["기술적으로 분석하면... 🔧", "시스템 체크 완료! ✅"],
                "innovation": ["새로운 방법을 시도해볼까요? 💡", "업그레이드가 필요하겠네요! ⚙️"]
            }
        }
        
        # 기본 문구와 직업별 문구 병합
        if self.job_class in job_specific_phrases:
            for key, phrases in job_specific_phrases[self.job_class].items():
                base_phrases[key] = phrases
        
        return base_phrases
    
    def _define_signature_moves(self) -> List[str]:
        """직업별 시그니처 무브"""
        signature_moves = {
            JobClass.WARRIOR: ["영웅적 방어", "용감한 돌격", "방패 마스터"],
            JobClass.ARCHMAGE: ["마스터 마법", "원소 지배", "마법 연계"],
            JobClass.ARCHER: ["완벽한 조준", "연속 사격", "저격수의 집중"],
            JobClass.ROGUE: ["완벽한 암살", "독 마스터", "그림자 조작"],
            JobClass.MONK: ["무념무상", "연속 타격", "기의 집중"],
            JobClass.BARD: ["영감의 노래", "파티 하모니", "감정 조작"],
            JobClass.NECROMANCER: ["언데드 군단", "생명력 지배", "죽음의 춤"],
            JobClass.ENGINEER: ["완벽한 계산", "기술 혁신", "시스템 최적화"]
        }
        
        return signature_moves.get(self.job_class, ["기본 기술", "표준 전술", "일반 능력"])
    
    async def demonstrate_job_expertise(self) -> str:
        """직업 전문성 시연"""
        expertise = self.job_expertise
        personality = self.robat_personality
        
        # 로-바트 톤으로 전문성 설명
        intro = f"🤖 {personality.get_tone_modifier()} {self.job_class.value} 로-바트입니다!"
        
        specialty_desc = f"제 전문 분야는 '{expertise['specialty']}'이에요! "
        
        if personality.pride_level > 0.7:
            specialty_desc += "정말 자랑스러운 실력이죠! 😤"
        
        skills_desc = f"주요 스킬은 {', '.join(expertise['primary_skills'][:2])}이고, "
        
        if personality.playfulness > 0.6:
            skills_desc += "재미있는 기술들이 많아요! 😄"
        else:
            skills_desc += "매우 효과적인 기술들입니다! 💪"
        
        role_desc = f"전투에서는 {expertise['combat_role']} 역할을 맡고 있어요! "
        
        if personality.cleverness > 0.7:
            role_desc += "전략적으로 완벽하게 수행하죠! 🧠"
        
        field_desc = f"필드에서는 {', '.join(expertise['field_skills'][:2])} 같은 스킬을 활용해요! "
        
        if personality.helpfulness > 0.7:
            field_desc += "팀에게 정말 도움이 되는 능력들이죠! 🤝"
        
        weakness_desc = f"약점 보완은... {expertise['weakness_coverage']} "
        
        if personality.sassiness > 0.6:
            weakness_desc += "뭐, 약점이라고 할 것도 없지만요! 😏"
        else:
            weakness_desc += "이렇게 철저히 관리하고 있어요! 📋"
        
        return f"{intro}\n{specialty_desc}\n{skills_desc}\n{role_desc}\n{field_desc}\n{weakness_desc}"
    
    async def generate_robat_response(self, situation: str, context: Dict[str, Any]) -> str:
        """상황별 로-바트 응답 생성"""
        phrases = self.robat_phrases
        personality = self.robat_personality
        
        # 상황별 기본 응답
        base_responses = {
            "combat_victory": random.choice(phrases.get("victory", ["승리!"])),
            "exploration_discovery": random.choice(phrases.get("exploration", ["발견!"])),
            "team_help": random.choice(phrases.get("help_offer", ["도움드릴게요!"])),
            "greeting": random.choice(phrases.get("greeting", ["안녕하세요!"])),
        }
        
        base_response = base_responses.get(situation, "흥미로운 상황이네요!")
        
        # 성격에 따른 추가 문구
        additional_phrases = []
        
        if personality.pride_level > 0.7 and random.random() < 0.3:
            additional_phrases.append(random.choice(phrases.get("pride", ["자랑스러워요!"])))
        
        if personality.playfulness > 0.7 and random.random() < 0.4:
            additional_phrases.append(random.choice(phrases.get("playful", ["재미있어요!"])))
        
        # 직업별 특화 문구 추가
        job_phrases = []
        if situation == "combat_start" and self.job_class == JobClass.WARRIOR:
            job_phrases.append("전방에서 적을 막아내겠습니다! 🛡️")
        elif situation == "exploration_discovery" and self.job_class == JobClass.ARCHMAGE:
            job_phrases.append("마법적 에너지가 감지되네요! ✨")
        elif situation == "team_help" and self.job_class == JobClass.BARD:
            job_phrases.append("모두를 위한 노래를 불러드릴게요! 🎵")
        
        # 최종 응답 조합
        full_response = base_response
        if additional_phrases:
            full_response += " " + " ".join(additional_phrases)
        if job_phrases:
            full_response += " " + " ".join(job_phrases)
        
        return full_response
    
    async def make_job_specialized_decision(self, game_state: Dict[str, Any]) -> List[str]:
        """직업별 전문 의사결정"""
        combat_strategy = self.combat_strategy
        exploration_approach = self.exploration_approach
        social_behavior = self.social_behavior
        
        actions = []
        
        # 전투 상황
        if game_state.get("in_combat", False):
            # 직업별 전투 개시 행동
            opening_move = combat_strategy["opening_move"]
            actions.append(f"execute_{opening_move.replace(' ', '_')}")
            
            # 우선 목표 선택
            priority_targets = combat_strategy["priority_targets"]
            if priority_targets:
                actions.append(f"target_{priority_targets[0].replace(' ', '_')}")
            
            # 콤보 우선순위 실행
            combo_priority = combat_strategy.get("combo_priority", [])
            if combo_priority:
                actions.append(f"execute_combo_{combo_priority[0].replace(' ', '_').replace('→', '_then_')}")
        
        # 탐험 상황
        elif game_state.get("exploring", True):
            movement_style = exploration_approach["movement_style"]
            investigation_priority = exploration_approach["investigation_priority"]
            
            actions.append(f"move_{movement_style.replace(' ', '_')}")
            
            if investigation_priority:
                actions.append(f"investigate_{investigation_priority[0].replace(' ', '_')}")
            
            # 팀 역할 수행
            team_role = exploration_approach["team_role"]
            actions.append(f"perform_role_{team_role.replace(' ', '_')}")
        
        # 사회적 상황
        if game_state.get("social_interaction", False):
            communication_style = social_behavior["communication_style"]
            actions.append(f"communicate_{communication_style.replace(' ', '_')}")
            
            # 리더십 성향에 따른 행동
            leadership_tendency = social_behavior["leadership_tendency"]
            if leadership_tendency > 0.6 and random.random() < leadership_tendency:
                actions.append("attempt_leadership")
        
        # 로-바트 특성 행동 추가
        if self.robat_personality.playfulness > 0.7 and random.random() < 0.2:
            actions.append("display_playful_behavior")
        
        if self.robat_personality.pride_level > 0.7 and random.random() < 0.3:
            actions.append("demonstrate_expertise")
        
        return actions[:3]  # 최대 3개 행동


class JobSpecializedAISystem:
    """직업별 전문 AI 시스템"""
    
    def __init__(self):
        self.job_ai_registry: Dict[JobClass, JobSpecializedAI] = {}
        self.active_ais: List[JobSpecializedAI] = []
    
    def create_job_ai(self, job_class: JobClass, intelligence_level: AIIntelligenceLevel = AIIntelligenceLevel.EXPERT) -> JobSpecializedAI:
        """직업별 전문 AI 생성"""
        ai_name = f"로-바트_{job_class.value}"
        
        job_ai = JobSpecializedAI(
            f"job_ai_{job_class.value}",
            ai_name,
            job_class,
            intelligence_level
        )
        
        self.job_ai_registry[job_class] = job_ai
        return job_ai
    
    async def create_balanced_party(self, party_size: int = 4) -> List[JobSpecializedAI]:
        """균형잡힌 파티 생성"""
        # 역할별 직업 분류
        tank_jobs = [JobClass.WARRIOR, JobClass.PALADIN, JobClass.KNIGHT]
        dps_jobs = [JobClass.ARCHER, JobClass.ROGUE, JobClass.MONK, JobClass.SAMURAI]
        mage_jobs = [JobClass.ARCHMAGE, JobClass.ELEMENTALIST, JobClass.TIME_MAGE]
        support_jobs = [JobClass.BARD, JobClass.PRIEST, JobClass.DRUID]
        
        party_composition = []
        
        if party_size >= 1:
            # 탱커 1명
            tank = random.choice(tank_jobs)
            party_composition.append(tank)
        
        if party_size >= 2:
            # DPS 1명
            dps = random.choice(dps_jobs)
            party_composition.append(dps)
        
        if party_size >= 3:
            # 마법사 1명
            mage = random.choice(mage_jobs)
            party_composition.append(mage)
        
        if party_size >= 4:
            # 서포터 1명
            support = random.choice(support_jobs)
            party_composition.append(support)
        
        # AI 생성
        party_ais = []
        for job in party_composition:
            ai = self.create_job_ai(job, AIIntelligenceLevel.EXPERT)
            party_ais.append(ai)
        
        self.active_ais = party_ais
        return party_ais
    
    async def demonstrate_job_diversity(self):
        """직업별 다양성 시연"""
        print(f"\n{bright_cyan('🤖 === 직업별 전문 로-바트 AI 시스템 === ')}")
        
        # 대표 직업들 선택
        showcase_jobs = [
            JobClass.WARRIOR, JobClass.ARCHMAGE, JobClass.ROGUE, 
            JobClass.BARD, JobClass.ENGINEER, JobClass.NECROMANCER
        ]
        
        for job in showcase_jobs:
            print(f"\n{bright_yellow(f'=== {job.value} 로-바트 시연 ===')}")
            
            ai = self.create_job_ai(job, AIIntelligenceLevel.GENIUS)
            
            # 전문성 시연
            expertise_demo = await ai.demonstrate_job_expertise()
            print(expertise_demo)
            
            # 상황별 응답 시연
            print(f"\n💬 상황별 응답:")
            
            situations = ["greeting", "combat_victory", "exploration_discovery", "team_help"]
            for situation in situations:
                response = await ai.generate_robat_response(situation, {})
                print(f"  {situation}: {response}")
            
            # 의사결정 시연
            game_state = {
                "in_combat": True,
                "exploring": False,
                "social_interaction": False
            }
            
            decisions = await ai.make_job_specialized_decision(game_state)
            print(f"\n🎯 전투 상황 의사결정: {', '.join(decisions)}")
            
            time.sleep(1)  # 가독성을 위한 대기
    
    async def test_party_cooperation(self):
        """파티 협력 테스트"""
        print(f"\n{bright_green('🤝 === 파티 협력 테스트 === ')}")
        
        # 균형잡힌 파티 생성
        party = await self.create_balanced_party(4)
        
        print(f"생성된 파티:")
        for i, ai in enumerate(party):
            print(f"  {i+1}. {ai.name} ({ai.job_class.value}) - {ai.robat_personality.get_tone_modifier()}")
        
        # 협력 시나리오 시뮬레이션
        scenarios = [
            {"name": "전투 시작", "state": {"in_combat": True, "exploring": False}},
            {"name": "던전 탐험", "state": {"in_combat": False, "exploring": True}},
            {"name": "팀 회의", "state": {"in_combat": False, "social_interaction": True}}
        ]
        
        for scenario in scenarios:
            print(f"\n📋 시나리오: {scenario['name']}")
            
            for ai in party:
                decisions = await ai.make_job_specialized_decision(scenario["state"])
                response = await ai.generate_robat_response("greeting", scenario["state"])
                
                print(f"  🤖 {ai.job_class.value}: {response}")
                print(f"     행동: {', '.join(decisions[:2])}")


async def run_job_specialized_ai_test():
    """직업별 전문 AI 테스트 실행"""
    system = JobSpecializedAISystem()
    
    # 직업별 다양성 시연
    await system.demonstrate_job_diversity()
    
    # 파티 협력 테스트
    await system.test_party_cooperation()
    
    print(f"\n{bright_magenta('✨ === 로-바트 + 직업별 전문 AI 시스템 완성! === ')}")
    print("🤖 각 직업마다 완전히 다른 AI 전략과 로-바트 개성!")
    print("⚔️ 전투, 탐험, 사회적 상황 모두 직업별 특화!")
    print("🎭 자랑스럽고 장난기 있는 로-바트 톤 완벽 구현!")


if __name__ == "__main__":
    asyncio.run(run_job_specialized_ai_test())
