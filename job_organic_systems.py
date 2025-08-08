#!/usr/bin/env python3
"""
🎯 직업별 유기성 시스템 - 각 직업만의 고유 메커니즘
암살자의 그림자 시스템처럼 직업별 특색 있는 전투 시스템 구현
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

class JobMechanicType(Enum):
    """직업 메커니즘 타입"""
    RESOURCE_STACK = "resource_stack"      # 자원 축적형 (콤보, 기력 등)
    STANCE_CHANGE = "stance_change"        # 자세 변환형 (폼체인지)
    COMBO_CHAIN = "combo_chain"            # 연계 공격형
    AURA_FIELD = "aura_field"             # 오라/필드형
    TRANSFORMATION = "transformation"      # 변신/형태변환형
    ELEMENTAL_CYCLE = "elemental_cycle"    # 원소 순환형
    TIME_MANIPULATION = "time_manipulation" # 시간 조작형
    SUMMON_CONTROL = "summon_control"      # 소환물 조작형

@dataclass
class JobMechanic:
    """직업 메커니즘 정의"""
    name: str
    job_class: str
    mechanic_type: JobMechanicType
    max_stacks: int = 5
    decay_rate: int = 0  # 턴당 감소량
    special_effects: List[str] = None
    
    def __post_init__(self):
        if self.special_effects is None:
            self.special_effects = []

# ================================
# 1. 전사 - 분노 시스템 🔥
# ================================
WARRIOR_RAGE_SYSTEM = JobMechanic(
    name="분노",
    job_class="전사",
    mechanic_type=JobMechanicType.RESOURCE_STACK,
    max_stacks=5,
    special_effects=["damage_boost", "speed_increase", "critical_rate_up"]
)

# ================================
# 2. 궁수 - 집중 시스템 🎯
# ================================
ARCHER_FOCUS_SYSTEM = JobMechanic(
    name="집중",
    job_class="궁수", 
    mechanic_type=JobMechanicType.RESOURCE_STACK,
    max_stacks=3,
    special_effects=["accuracy_boost", "critical_damage_up", "piercing_shot"]
)

# ================================
# 3. 마법사 - 원소 순환 시스템 🌟
# ================================
MAGE_ELEMENT_SYSTEM = JobMechanic(
    name="원소조화",
    job_class="마법사",
    mechanic_type=JobMechanicType.ELEMENTAL_CYCLE,
    max_stacks=4,  # 화염, 얼음, 번개, 어둠
    special_effects=["element_fusion", "spell_amplify", "mana_efficiency"]
)

# ================================
# 4. 성직자 - 신성력 시스템 ✨
# ================================
PRIEST_DIVINE_SYSTEM = JobMechanic(
    name="신성력",
    job_class="성직자",
    mechanic_type=JobMechanicType.AURA_FIELD,
    max_stacks=3,
    special_effects=["healing_boost", "party_blessing", "divine_protection"]
)

# ================================
# 5. 기계공학자 - 오버차지 시스템 🔧
# ================================
ENGINEER_OVERCHARGE_SYSTEM = JobMechanic(
    name="오버차지",
    job_class="기계공학자",
    mechanic_type=JobMechanicType.RESOURCE_STACK,
    max_stacks=10,
    decay_rate=1,  # 매 턴 1씩 감소
    special_effects=["tech_boost", "multi_shot", "explosive_damage"]
)

# ================================
# 6. 바드 - 선율 시스템 🎵
# ================================
BARD_MELODY_SYSTEM = JobMechanic(
    name="선율",
    job_class="바드",
    mechanic_type=JobMechanicType.COMBO_CHAIN,
    max_stacks=7,  # 7음계
    special_effects=["melody_chain", "party_buff", "emotion_control"]
)

# ================================
# 7. 몽크 - 기 시스템 👊
# ================================
MONK_KI_SYSTEM = JobMechanic(
    name="기력",
    job_class="몽크",
    mechanic_type=JobMechanicType.RESOURCE_STACK,
    max_stacks=5,
    special_effects=["combo_multiplier", "inner_power", "perfect_balance"]
)

# ================================
# 8. 용기사 - 용의 힘 시스템 🐉
# ================================
DRAGONKNIGHT_POWER_SYSTEM = JobMechanic(
    name="용의힘",
    job_class="용기사",
    mechanic_type=JobMechanicType.TRANSFORMATION,
    max_stacks=3,  # 용화 단계
    special_effects=["dragon_form", "breath_weapon", "scale_armor"]
)

# ================================
# 9. 시간술사 - 시간 조작 시스템 ⏰
# ================================
TIMEMAGE_TEMPORAL_SYSTEM = JobMechanic(
    name="시간층",
    job_class="시간술사",
    mechanic_type=JobMechanicType.TIME_MANIPULATION,
    max_stacks=5,
    special_effects=["time_slow", "time_acceleration", "temporal_loop"]
)

# ================================
# 10. 네크로맨서 - 영혼 시스템 ☠️
# ================================
NECROMANCER_SOUL_SYSTEM = JobMechanic(
    name="영혼력",
    job_class="네크로맨서",
    mechanic_type=JobMechanicType.SUMMON_CONTROL,
    max_stacks=7,
    special_effects=["soul_harvest", "undead_summon", "life_drain"]
)

def get_job_mechanic_details() -> Dict[str, Dict]:
    """각 직업별 상세 메커니즘 설명"""
    return {
        "전사": {
            "시스템명": "🔥 분노 시스템",
            "설명": "피해를 받거나 적을 처치할 때마다 분노 누적, 분노가 높을수록 공격력과 속도 증가",
            "특징": [
                "분노 1단계: 공격력 +10%, 속도 +5%",
                "분노 2단계: 공격력 +25%, 속도 +10%, 크리티컬 +10%", 
                "분노 3단계: 공격력 +45%, 속도 +20%, 크리티컬 +20%",
                "분노 4단계: 공격력 +70%, 속도 +35%, 크리티컬 +35%",
                "분노 5단계(광폭): 공격력 +100%, 속도 +50%, 모든 공격이 크리티컬"
            ],
            "활용법": "지속적인 전투로 분노를 쌓아 후반에 압도적 화력 발휘"
        },
        
        "궁수": {
            "시스템명": "🎯 집중 시스템", 
            "설명": "움직이지 않고 공격할 때마다 집중도 상승, 집중도에 따라 정확도와 관통력 증가",
            "특징": [
                "집중 1단계: 명중률 +15%, 크리티컬 데미지 +20%",
                "집중 2단계: 명중률 +35%, 크리티컬 데미지 +50%, 관통사격 가능",
                "집중 3단계(완전집중): 모든 공격이 100% 명중, 크리티컬 데미지 +100%, 다중 관통"
            ],
            "활용법": "위치를 고정하여 집중도를 높인 후 강력한 원거리 공격으로 적 섬멸"
        },
        
        "마법사": {
            "시스템명": "🌟 원소 순환 시스템",
            "설명": "화염→얼음→번개→어둠 순서로 원소를 순환, 같은 원소 연속 사용 시 폭발적 위력",
            "특징": [
                "원소 1개: 기본 마법 위력",
                "원소 2개: 융합 마법 발동 가능 (위력 +50%)",
                "원소 3개: 고급 융합 마법 (위력 +100%, 광역 효과)",
                "원소 4개(완전조화): 궁극 원소 마법 (위력 +200%, 특수 효과)"
            ],
            "활용법": "다양한 원소를 조합하여 상황에 맞는 최적의 마법 선택"
        },
        
        "성직자": {
            "시스템명": "✨ 신성력 시스템",
            "설명": "치료나 축복 스킬 사용 시 신성력 축적, 파티 전체에 지속적인 보호막과 회복 효과",
            "특징": [
                "신성력 1단계: 파티 HP 재생 +5/턴",
                "신성력 2단계: 파티 HP 재생 +10/턴, 상태이상 저항 +25%", 
                "신성력 3단계(신의가호): 파티 HP 재생 +20/턴, 상태이상 면역, 피해 감소 20%"
            ],
            "활용법": "지속적인 지원으로 파티의 생존력을 극대화"
        },
        
        "기계공학자": {
            "시스템명": "🔧 오버차지 시스템",
            "설명": "기술 스킬 사용 시 기계에 에너지 축적, 높은 차지일수록 폭발적 공격 가능",
            "특징": [
                "차지 1-3: 일반 기술 공격",
                "차지 4-6: 강화 기술 공격 (위력 +50%, 관통 효과)",
                "차지 7-9: 고출력 기술 공격 (위력 +100%, 광역 효과)",
                "차지 10(임계점): 오버로드 공격 (위력 +300%, 모든 적 대상, 차지 초기화)"
            ],
            "활용법": "차지를 조절하여 상황에 맞는 화력 조절, 임계점에서 대폭발"
        },
        
        "바드": {
            "시스템명": "🎵 선율 시스템",
            "설명": "도-레-미-파-솔-라-시 7음계 순서로 연주, 완성된 선율에 따라 다양한 효과",
            "특징": [
                "3음 완성: 단순 버프 (공격력/방어력 +20%)",
                "5음 완성: 중급 버프 (모든 능력치 +30%, 상태이상 회복)",
                "7음 완성: 완벽한 선율 (모든 능력치 +50%, 특수 효과, 적 디버프)"
            ],
            "활용법": "전략적 선율 조합으로 전투 흐름을 완전히 바꿔놓기"
        },
        
        "몽크": {
            "시스템명": "👊 기력 시스템",
            "설명": "연속 공격과 이동으로 기력 축적, 기력이 높을수록 연계 공격 위력 증가",
            "특징": [
                "기력 1-2: 일반 무술 공격",
                "기력 3-4: 연계 콤보 공격 (2-3연타)",
                "기력 5(완전조화): 무극 연계 (5연타, 마지막 타격이 필살기급 위력)"
            ],
            "활용법": "지속적인 움직임과 공격으로 기력을 쌓아 강력한 연계 공격"
        },
        
        "용기사": {
            "시스템명": "🐉 용의 힘 시스템",
            "설명": "전투 중 용의 힘 각성, 단계별로 용의 특성 획득하여 능력치 대폭 상승",
            "특징": [
                "각성 1단계: 용의 비늘 (방어력 +50%)",
                "각성 2단계: 용의 날개 (속도 +100%, 비행 공격)",
                "각성 3단계(완전용화): 용의 완전체 (모든 능력치 +200%, 브레스 공격)"
            ],
            "활용법": "시간을 들여 각성을 완료하면 압도적인 전투력 확보"
        },
        
        "시간술사": {
            "시스템명": "⏰ 시간 조작 시스템",
            "설명": "시간층을 쌓아 시간 흐름 조작, 적의 시간을 늦추거나 자신의 시간을 가속",
            "특징": [
                "시간층 1-2: 미세한 시간 조작 (속도 ±20%)",
                "시간층 3-4: 중급 시간 조작 (턴 순서 변경, 시간 정지)",
                "시간층 5(시간지배): 완전한 시간 통제 (적 시간 정지, 자신 추가 턴)"
            ],
            "활용법": "시간 조작으로 전투의 템포를 완전히 장악"
        },
        
        "네크로맨서": {
            "시스템명": "☠️ 영혼 시스템",
            "설명": "적 처치나 생명력 흡수로 영혼 수집, 영혼으로 언데드 소환 및 강화",
            "특징": [
                "영혼 1-2: 스켈레톤 소환",
                "영혼 3-4: 좀비, 스펙터 소환",
                "영혼 5-7: 리치, 본 드래곤 등 강력한 언데드 소환"
            ],
            "활용법": "영혼을 모아 강력한 언데드 군단으로 적을 압도"
        }
    }

if __name__ == "__main__":
    details = get_job_mechanic_details()
    for job, info in details.items():
        print(f"\n{'='*50}")
        print(f"직업: {job}")
        print(f"시스템: {info['시스템명']}")
        print(f"설명: {info['설명']}")
        print("특징:")
        for feature in info['특징']:
            print(f"  • {feature}")
        print(f"활용법: {info['활용법']}")
