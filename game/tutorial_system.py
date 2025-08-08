#!/usr/bin/env python3
"""
튜토리얼 시스템 - 빵빵한 선택 가능한 튜토리얼
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import json


class TutorialType(Enum):
    """튜토리얼 종류"""
    BASIC_MOVEMENT = "basic_movement"
    COMBAT_SYSTEM = "combat_system"
    ATB_SYSTEM = "atb_system"
    BRAVE_SYSTEM = "brave_system"
    WOUND_SYSTEM = "wound_system"
    SKILL_SYSTEM = "skill_system"
    TRAIT_SYSTEM = "trait_system"  # 새로운 특성 시스템
    ORGANIC_EFFECTS = "organic_effects"  # 유기적 효과 시스템
    FIELD_SKILLS = "field_skills"  # 필드 스킬 시스템
    STATUS_EFFECTS = "status_effects"
    INVENTORY_SYSTEM = "inventory_system"
    PARTY_MANAGEMENT = "party_management"
    DUNGEON_EXPLORATION = "dungeon_exploration"
    ITEM_USAGE = "item_usage"
    SAVE_LOAD = "save_load"
    ADVANCED_COMBAT = "advanced_combat"
    ELEMENT_SYSTEM = "element_system"
    BOSS_STRATEGY = "boss_strategy"
    AUDIO_SYSTEM = "audio_system"  # 사운드 시스템


class TutorialStep:
    """튜토리얼 단계"""
    
    def __init__(self, title: str, description: str, instruction: str,
                 trigger_condition: str = None, completion_condition: str = None,
                 demo_action: Callable = None):
        self.title = title
        self.description = description
        self.instruction = instruction
        self.trigger_condition = trigger_condition
        self.completion_condition = completion_condition
        self.demo_action = demo_action
        self.completed = False
        self.skipped = False


class Tutorial:
    """개별 튜토리얼"""
    
    def __init__(self, tutorial_type: TutorialType, title: str, description: str,
                 difficulty: str = "초급", estimated_time: str = "3분"):
        self.type = tutorial_type
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.estimated_time = estimated_time
        self.steps: List[TutorialStep] = []
        self.current_step = 0
        self.completed = False
        self.enabled = True
        
    def add_step(self, step: TutorialStep):
        """단계 추가"""
        self.steps.append(step)
    
    def get_current_step(self) -> Optional[TutorialStep]:
        """현재 단계 반환"""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def advance_step(self) -> bool:
        """다음 단계로 진행"""
        if self.current_step < len(self.steps):
            self.steps[self.current_step].completed = True
            self.current_step += 1
            
            if self.current_step >= len(self.steps):
                self.completed = True
                return False  # 튜토리얼 완료
            return True  # 다음 단계 있음
        return False
    
    def skip_current_step(self):
        """현재 단계 건너뛰기"""
        if current_step := self.get_current_step():
            current_step.skipped = True
            self.advance_step()
    
    def reset(self):
        """튜토리얼 재설정"""
        self.current_step = 0
        self.completed = False
        for step in self.steps:
            step.completed = False
            step.skipped = False


class TutorialManager:
    """튜토리얼 관리자"""
    
    def __init__(self):
        self.tutorials: Dict[TutorialType, Tutorial] = {}
        self.current_tutorial: Optional[Tutorial] = None
        self.tutorial_enabled = True
        self.auto_trigger = True
        self.completed_tutorials: List[TutorialType] = []
        self.user_preferences = {
            "show_hints": True,
            "auto_advance": False,
            "demo_mode": True,
            "skip_completed": True
        }
        
        self._initialize_tutorials()
    
    def _initialize_tutorials(self):
        """모든 튜토리얼 초기화"""
        
        # 기본 이동 튜토리얼
        basic_movement = Tutorial(
            TutorialType.BASIC_MOVEMENT,
            "기본 이동",
            "캐릭터 이동과 던전 탐험의 기초를 배워보세요",
            "초급", "2분"
        )
        basic_movement.add_step(TutorialStep(
            "방향키 이동", 
            "방향키나 WASD로 캐릭터를 움직일 수 있습니다.",
            "↑↓←→ 키나 WASD 키를 눌러 캐릭터를 움직여보세요."
        ))
        basic_movement.add_step(TutorialStep(
            "시야 시스템",
            "캐릭터 주변만 볼 수 있으며, 이동하면서 던전을 탐험합니다.",
            "여러 방향으로 이동하여 던전을 탐험해보세요."
        ))
        basic_movement.add_step(TutorialStep(
            "벽과 장애물",
            "# 표시는 벽이며 지나갈 수 없습니다.",
            "벽에 부딪혀보고 지나갈 수 있는 곳을 찾아보세요."
        ))
        self.tutorials[TutorialType.BASIC_MOVEMENT] = basic_movement
        
        # 전투 시스템 튜토리얼
        combat_system = Tutorial(
            TutorialType.COMBAT_SYSTEM,
            "전투 시스템",
            "기본적인 전투 메커니즘을 배워보세요",
            "초급", "5분"
        )
        combat_system.add_step(TutorialStep(
            "전투 진입",
            "적과 만나면 자동으로 전투가 시작됩니다.",
            "적을 만나 전투에 진입해보세요."
        ))
        combat_system.add_step(TutorialStep(
            "공격과 방어",
            "공격력과 방어력의 비율로 데미지가 결정됩니다.",
            "적을 공격해보세요. 데미지 = (공격력 / 방어력) × 보정값"
        ))
        combat_system.add_step(TutorialStep(
            "HP와 상처",
            "데미지를 받으면 HP가 감소하고 상처가 누적됩니다.",
            "적의 공격을 받아보고 HP와 상처 변화를 확인하세요."
        ))
        self.tutorials[TutorialType.COMBAT_SYSTEM] = combat_system
        
        # ATB 시스템 튜토리얼
        atb_system = Tutorial(
            TutorialType.ATB_SYSTEM,
            "ATB 시스템",
            "Active Time Battle 시스템의 작동 방식을 이해하세요",
            "중급", "4분"
        )
        atb_system.add_step(TutorialStep(
            "행동 순서",
            "속도 스탯에 따라 행동 순서가 결정됩니다.",
            "전투에서 행동 순서를 확인해보세요."
        ))
        atb_system.add_step(TutorialStep(
            "시간 흐름",
            "모든 캐릭터와 적의 ATB 게이지가 동시에 차오릅니다.",
            "ATB 게이지가 가득 차면 행동할 수 있습니다."
        ))
        atb_system.add_step(TutorialStep(
            "행동 대기",
            "게이지가 가득 찬 후에도 전략적으로 기다릴 수 있습니다.",
            "적절한 타이밍을 기다려 행동해보세요."
        ))
        self.tutorials[TutorialType.ATB_SYSTEM] = atb_system
        
        # BRV 시스템 튜토리얼
        brave_system = Tutorial(
            TutorialType.BRAVE_SYSTEM,
            "BRV 시스템",
            "브레이브 시스템으로 전략적 전투를 마스터하세요",
            "중급", "6분"
        )
        brave_system.add_step(TutorialStep(
            "BRV 공격",
            "BRV 공격으로 적의 브레이브를 빼앗아 자신의 것으로 만듭니다.",
            "BRV 공격을 사용해보세요."
        ))
        brave_system.add_step(TutorialStep(
            "HP 공격",
            "쌓인 브레이브로 HP 공격을 하여 실제 데미지를 입힙니다.",
            "브레이브를 쌓은 후 HP 공격을 해보세요."
        ))
        brave_system.add_step(TutorialStep(
            "브레이크 상태",
            "브레이브가 0이 되면 브레이크 상태가 되어 위험합니다.",
            "브레이크 상태의 위험성을 체험해보세요."
        ))
        self.tutorials[TutorialType.BRAVE_SYSTEM] = brave_system
        
        # 상처 시스템 튜토리얼
        wound_system = Tutorial(
            TutorialType.WOUND_SYSTEM,
            "상처 시스템",
            "독특한 상처 축적 시스템을 이해하세요",
            "중급", "4분"
        )
        wound_system.add_step(TutorialStep(
            "상처 축적",
            "받은 데미지의 25%가 상처로 축적됩니다.",
            "데미지를 받아 상처가 쌓이는 것을 확인하세요."
        ))
        wound_system.add_step(TutorialStep(
            "최대 HP 제한",
            "상처는 최대 HP의 75%까지만 축적됩니다.",
            "상처 한계를 확인해보세요."
        ))
        wound_system.add_step(TutorialStep(
            "상처 치료",
            "최대 HP를 넘는 회복량의 25%가 상처를 치료합니다.",
            "회복 아이템으로 상처를 치료해보세요."
        ))
        self.tutorials[TutorialType.WOUND_SYSTEM] = wound_system
        
        # 스킬 시스템 튜토리얼
        skill_system = Tutorial(
            TutorialType.SKILL_SYSTEM,
            "스킬 시스템",
            "캐릭터별 고유 스킬을 활용하는 방법을 배우세요",
            "중급", "7분"
        )
        skill_system.add_step(TutorialStep(
            "스킬 메뉴",
            "각 캐릭터는 8개의 스킬을 가지고 있습니다 (기본 BRV/HP 공격 + 고유 스킬 6개).",
            "스킬 메뉴를 열어 스킬 목록을 확인하세요."
        ))
        skill_system.add_step(TutorialStep(
            "기본 공격",
            "모든 캐릭터는 기본 BRV 공격과 기본 HP 공격을 가지고 있습니다.",
            "기본 BRV 공격으로 브레이브를 쌓은 후 기본 HP 공격을 사용해보세요."
        ))
        skill_system.add_step(TutorialStep(
            "고유 스킬",
            "각 직업마다 6개의 고유 스킬을 가지고 있으며, MP를 소모하여 사용합니다.",
            "MP를 소모하여 고유 스킬을 사용해보세요."
        ))
        skill_system.add_step(TutorialStep(
            "스킬 효과",
            "스킬은 데미지, 회복, 상태 효과 등 다양한 효과가 있습니다.",
            "여러 종류의 스킬을 사용해보세요."
        ))
        skill_system.add_step(TutorialStep(
            "도적 특화: 독 시스템",
            "도적은 독을 이용한 특수한 전투 스타일을 가지고 있습니다.",
            "도적으로 적에게 독을 걸어보세요. 독은 매 턴마다 피해를 입힙니다."
        ))
        self.tutorials[TutorialType.SKILL_SYSTEM] = skill_system
        
        # 특성 시스템 튜토리얼 (새로 추가)
        trait_system = Tutorial(
            TutorialType.TRAIT_SYSTEM,
            "특성 시스템",
            "각 직업의 고유 특성으로 전투 스타일을 개성화하세요",
            "중급", "6분"
        )
        trait_system.add_step(TutorialStep(
            "특성 개념",
            "각 직업은 5개의 고유 특성을 가지고 있습니다.",
            "캐릭터 정보에서 특성 목록을 확인해보세요."
        ))
        trait_system.add_step(TutorialStep(
            "특성 해금",
            "스타 조각을 사용하여 새로운 특성을 해금할 수 있습니다.",
            "메타 진행도에서 특성 해금 비용을 확인하세요."
        ))
        trait_system.add_step(TutorialStep(
            "특성 효과",
            "특성은 스킬 위력, 회복량, 상태 저항 등에 영향을 줍니다.",
            "특성 보유 여부에 따른 스킬 효과 차이를 체험해보세요."
        ))
        trait_system.add_step(TutorialStep(
            "AI 특성 인식",
            "아군과 적군 AI는 특성을 고려하여 전략을 결정합니다.",
            "AI의 특성 기반 행동 패턴을 관찰해보세요."
        ))
        self.tutorials[TutorialType.TRAIT_SYSTEM] = trait_system
        
        # 유기적 효과 시스템 튜토리얼
        organic_effects = Tutorial(
            TutorialType.ORGANIC_EFFECTS,
            "유기적 효과",
            "특성과 스킬이 유기적으로 연동되는 시스템을 이해하세요",
            "고급", "5분"
        )
        organic_effects.add_step(TutorialStep(
            "유기적 연동",
            "스킬 사용 시 보유 특성에 따라 추가 효과가 발동합니다.",
            "특성을 보유한 상태에서 스킬을 사용해보세요."
        ))
        organic_effects.add_step(TutorialStep(
            "특성 시너지",
            "여러 특성을 조합하면 더 강력한 시너지 효과를 얻을 수 있습니다.",
            "다양한 특성 조합을 실험해보세요."
        ))
        organic_effects.add_step(TutorialStep(
            "밸런스 시스템",
            "모든 효과는 신중하게 밸런스가 조정되어 있습니다.",
            "다양한 특성 조합의 밸런스를 체험해보세요."
        ))
        self.tutorials[TutorialType.ORGANIC_EFFECTS] = organic_effects
        
        # 상태 효과 튜토리얼
        status_effects = Tutorial(
            TutorialType.STATUS_EFFECTS,
            "상태 효과",
            "165가지가 넘는 상태 효과 시스템을 마스터하세요",
            "고급", "8분"
        )
        status_effects.add_step(TutorialStep(
            "버프와 디버프",
            "버프는 능력치를 향상시키고, 디버프는 약화시킵니다.",
            "버프와 디버프 효과를 확인해보세요."
        ))
        status_effects.add_step(TutorialStep(
            "지속 시간",
            "대부분의 상태 효과는 일정 턴 후 해제됩니다.",
            "상태 효과의 지속 시간을 관찰하세요."
        ))
        status_effects.add_step(TutorialStep(
            "독 효과 (DOT)",
            "독은 특별한 지속 피해 효과입니다. 매 턴마다 남은 독의 20%만큼 피해를 입히고, 피해를 입힌 독은 사라집니다.",
            "독 상태의 적을 관찰하며 독이 어떻게 줄어드는지 확인해보세요."
        ))
        status_effects.add_step(TutorialStep(
            "독 중첩과 병합",
            "여러 독 효과가 적용되면 지속 시간이 더 긴 것을 우선으로 병합됩니다.",
            "같은 적에게 여러 번 독을 걸어 병합 효과를 확인해보세요."
        ))
        status_effects.add_step(TutorialStep(
            "베놈 파워",
            "도적의 베놈 파워는 독 관련 스킬의 위력을 증가시킵니다. 적이 독에 걸릴 때마다 베놈 파워가 상승합니다.",
            "도적으로 플레이하며 베놈 파워 시스템을 체험해보세요."
        ))
        self.tutorials[TutorialType.STATUS_EFFECTS] = status_effects
        
        # 인벤토리 시스템 튜토리얼
        inventory_system = Tutorial(
            TutorialType.INVENTORY_SYSTEM,
            "인벤토리 시스템",
            "아이템 관리와 사용법을 배워보세요",
            "초급", "4분"
        )
        inventory_system.add_step(TutorialStep(
            "인벤토리 열기",
            "I 키를 눌러 인벤토리를 열 수 있습니다.",
            "I 키를 눌러 인벤토리를 열어보세요."
        ))
        inventory_system.add_step(TutorialStep(
            "아이템 사용",
            "아이템을 선택하고 사용하여 효과를 적용할 수 있습니다.",
            "회복 아이템을 사용해보세요."
        ))
        inventory_system.add_step(TutorialStep(
            "장비 착용",
            "무기와 방어구를 착용하여 능력치를 향상시킬 수 있습니다.",
            "장비를 착용해보세요."
        ))
        self.tutorials[TutorialType.INVENTORY_SYSTEM] = inventory_system
        
        # 추가 튜토리얼들...
        self._initialize_advanced_tutorials()
    
    def _initialize_advanced_tutorials(self):
        """고급 튜토리얼 초기화"""
        
        # 파티 관리 튜토리얼
        party_management = Tutorial(
            TutorialType.PARTY_MANAGEMENT,
            "파티 관리",
            "4인 파티 시스템을 효과적으로 운용하는 방법",
            "중급", "6분"
        )
        party_management.add_step(TutorialStep(
            "파티 구성",
            "최대 4명의 캐릭터로 파티를 구성할 수 있습니다.",
            "파티 메뉴에서 멤버를 확인하세요."
        ))
        party_management.add_step(TutorialStep(
            "역할 분담",
            "공격, 방어, 지원, 치료 역할을 적절히 배치하세요.",
            "각 캐릭터의 역할을 파악해보세요."
        ))
        party_management.add_step(TutorialStep(
            "협력 전투",
            "캐릭터들의 스킬을 조합하여 시너지를 만들어보세요.",
            "여러 캐릭터의 스킬을 연계해보세요."
        ))
        self.tutorials[TutorialType.PARTY_MANAGEMENT] = party_management
        
        # 던전 탐험 튜토리얼
        dungeon_exploration = Tutorial(
            TutorialType.DUNGEON_EXPLORATION,
            "던전 탐험",
            "효율적인 던전 탐험 전략을 배워보세요",
            "중급", "5분"
        )
        dungeon_exploration.add_step(TutorialStep(
            "맵 탐험",
            "던전의 모든 구역을 탐험하여 숨겨진 보물을 찾으세요.",
            "던전을 구석구석 탐험해보세요. 특수 지형을 찾아보세요."
        ))
        dungeon_exploration.add_step(TutorialStep(
            "계단 찾기",
            "> 표시가 다음 층으로 가는 계단입니다.",
            "계단을 찾아 다음 층으로 내려가세요."
        ))
        dungeon_exploration.add_step(TutorialStep(
            "특수 지형",
            "= 보물상자, & 잠긴 문, ^ 함정, ? 비밀 문, T 제단, ~ 분수, B 책장, F 대장간, G 정원, * 마법 수정, / 레버",
            "각 특수 지형은 특정 직업 스킬이 필요합니다."
        ))
        dungeon_exploration.add_step(TutorialStep(
            "아이템 표시",
            "! 소모품, L 무기, ] 방어구, Q 액세서리로 표시됩니다.",
            "아이템을 찾아 수집해보세요."
        ))
        self.tutorials[TutorialType.DUNGEON_EXPLORATION] = dungeon_exploration
        
        # 원소 시스템 튜토리얼
        element_system = Tutorial(
            TutorialType.ELEMENT_SYSTEM,
            "원소 시스템",
            "10가지 원소의 상성과 효과를 마스터하세요",
            "고급", "10분"
        )
        element_system.add_step(TutorialStep(
            "원소 상성",
            "화염 > 얼음 > 대지 > 화염의 3원소 순환 상성이 있습니다.",
            "서로 다른 원소 스킬을 사용해보세요."
        ))
        element_system.add_step(TutorialStep(
            "추가 원소",
            "번개, 바람, 물, 빛, 어둠, 독, 무속성까지 총 10가지입니다.",
            "다양한 원소 스킬의 효과를 확인하세요."
        ))
        element_system.add_step(TutorialStep(
            "원소 조합",
            "여러 원소를 조합하여 강력한 연계 공격을 만들 수 있습니다.",
            "원소 스킬을 연계하여 사용해보세요."
        ))
        self.tutorials[TutorialType.ELEMENT_SYSTEM] = element_system
        
        # 보스 전략 튜토리얼
        boss_strategy = Tutorial(
            TutorialType.BOSS_STRATEGY,
            "보스 전략",
            "강력한 보스를 상대하는 고급 전술을 배우세요",
            "고급", "12분"
        )
        boss_strategy.add_step(TutorialStep(
            "보스 패턴",
            "보스는 특별한 공격 패턴과 능력을 가지고 있습니다.",
            "보스의 공격 패턴을 관찰하세요."
        ))
        boss_strategy.add_step(TutorialStep(
            "약점 공략",
            "보스마다 특정 원소나 공격 타입에 약점이 있습니다.",
            "보스의 약점을 찾아 공략해보세요."
        ))
        boss_strategy.add_step(TutorialStep(
            "지구전 준비",
            "장기간 전투를 대비해 MP와 아이템을 관리하세요.",
            "자원을 아껴가며 보스와 싸워보세요."
        ))
        self.tutorials[TutorialType.BOSS_STRATEGY] = boss_strategy
        
        # 오디오 시스템 튜토리얼 (새로 추가)
        audio_system = Tutorial(
            TutorialType.AUDIO_SYSTEM,
            "사운드 시스템",
            "게임의 풍부한 오디오 환경을 체험하세요",
            "초급", "3분"
        )
        audio_system.add_step(TutorialStep(
            "배경음악",
            "각 던전 층마다 다른 BGM이 재생됩니다.",
            "여러 층을 탐험하며 다양한 BGM을 들어보세요."
        ))
        audio_system.add_step(TutorialStep(
            "스킬 효과음",
            "각 스킬마다 고유한 SFX가 재생됩니다.",
            "다양한 스킬을 사용하며 효과음을 들어보세요."
        ))
        audio_system.add_step(TutorialStep(
            "상황별 사운드",
            "전투 시작, 아이템 획득, 레벨업 등 상황마다 적절한 사운드가 재생됩니다.",
            "게임을 플레이하며 다양한 상황 사운드를 체험해보세요."
        ))
        audio_system.add_step(TutorialStep(
            "음량 조절",
            "설정에서 BGM과 SFX 음량을 개별적으로 조절할 수 있습니다.",
            "설정 메뉴에서 음량을 조절해보세요."
        ))
        self.tutorials[TutorialType.AUDIO_SYSTEM] = audio_system
        
        # 필드 스킬 튜토리얼 (새로 추가)
        field_skills = Tutorial(
            TutorialType.FIELD_SKILLS,
            "필드 스킬 시스템",
            "직업별 필드 스킬로 던전의 숨겨진 요소를 활용하세요",
            "중급", "8분"
        )
        field_skills.add_step(TutorialStep(
            "직업별 필드 스킬",
            "각 직업은 고유한 필드 스킬을 가지고 있습니다.",
            "파티 구성을 다양하게 해서 여러 스킬을 활용해보세요."
        ))
        field_skills.add_step(TutorialStep(
            "잠긴 문과 상자",
            "& 잠긴 문과 = 잠긴 보물상자는 도적이나 궁수의 '자물쇠해제' 스킬이 필요합니다.",
            "도적이나 궁수를 파티에 넣고 잠긴 것들을 열어보세요."
        ))
        field_skills.add_step(TutorialStep(
            "비밀 탐지",
            "? 비밀 문이나 숨겨진 함정은 도적, 궁수, 철학자의 '비밀탐지' 스킬로 발견할 수 있습니다.",
            "벽을 자세히 살펴보세요. 숨겨진 통로가 있을지도 모릅니다."
        ))
        field_skills.add_step(TutorialStep(
            "함정 처리",
            "^ 함정은 먼저 '함정탐지'로 발견하고 '함정해제'로 안전하게 제거할 수 있습니다.",
            "도적이나 궁수로 함정을 조심스럽게 처리해보세요."
        ))
        field_skills.add_step(TutorialStep(
            "신성한 힘",
            "T 제단은 성기사나 신관의 '신성마법' 스킬로 축복을 받을 수 있습니다.",
            "성기사나 신관으로 제단을 조사해보세요."
        ))
        field_skills.add_step(TutorialStep(
            "지식과 기술",
            "B 책장(철학자/아크메이지), F 대장간(기계공학자), G 정원(드루이드), * 마법 수정(정령술사/아크메이지), / 레버(기계공학자/도적)",
            "각 직업의 전문 분야를 활용해 특별한 혜택을 얻어보세요."
        ))
        field_skills.add_step(TutorialStep(
            "다양한 파티 구성",
            "모든 필드 스킬을 활용하려면 다양한 직업으로 파티를 구성하세요.",
            "탐험 중심 파티: 도적, 철학자, 기계공학자, 드루이드를 추천합니다."
        ))
        self.tutorials[TutorialType.FIELD_SKILLS] = field_skills
        
        # 모든 튜토리얼 등록
        for tutorial in [party_management, dungeon_exploration, field_skills, element_system, boss_strategy, audio_system]:
            self.tutorials[tutorial.type] = tutorial
    
    def get_available_tutorials(self) -> List[Tutorial]:
        """사용 가능한 튜토리얼 목록"""
        available = []
        for tutorial in self.tutorials.values():
            if tutorial.enabled:
                if not self.user_preferences["skip_completed"] or not tutorial.completed:
                    available.append(tutorial)
        return available
    
    def start_tutorial(self, tutorial_type: TutorialType) -> bool:
        """튜토리얼 시작"""
        if tutorial_type in self.tutorials:
            self.current_tutorial = self.tutorials[tutorial_type]
            self.current_tutorial.reset()
            print(f"📚 튜토리얼 시작: {self.current_tutorial.title}")
            print(f"📖 설명: {self.current_tutorial.description}")
            print(f"⏱️ 예상 시간: {self.current_tutorial.estimated_time}")
            print(f"🎯 난이도: {self.current_tutorial.difficulty}")
            return True
        return False
    
    def get_current_instruction(self) -> Optional[str]:
        """현재 지시사항 반환"""
        if self.current_tutorial:
            if step := self.current_tutorial.get_current_step():
                return f"📝 {step.title}: {step.instruction}"
        return None
    
    def advance_tutorial(self) -> bool:
        """튜토리얼 진행"""
        if self.current_tutorial:
            has_more = self.current_tutorial.advance_step()
            if not has_more:
                self._complete_tutorial()
                return False
            return True
        return False
    
    def skip_current_step(self):
        """현재 단계 건너뛰기"""
        if self.current_tutorial:
            self.current_tutorial.skip_current_step()
            if self.current_tutorial.completed:
                self._complete_tutorial()
    
    def _complete_tutorial(self):
        """튜토리얼 완료 처리"""
        if self.current_tutorial:
            self.completed_tutorials.append(self.current_tutorial.type)
            print(f"🎉 튜토리얼 완료: {self.current_tutorial.title}")
            print("💡 새로운 지식을 습득했습니다!")
            self.current_tutorial = None
    
    def stop_tutorial(self):
        """튜토리얼 중지"""
        if self.current_tutorial:
            print(f"⏹️ 튜토리얼 중지: {self.current_tutorial.title}")
            self.current_tutorial = None
    
    def show_tutorial_menu(self) -> List[Dict[str, Any]]:
        """튜토리얼 메뉴 표시용 데이터"""
        menu_items = []
        
        # 카테고리별 분류
        categories = {
            "기초": [TutorialType.BASIC_MOVEMENT, TutorialType.INVENTORY_SYSTEM],
            "전투": [TutorialType.COMBAT_SYSTEM, TutorialType.ATB_SYSTEM, TutorialType.BRAVE_SYSTEM],
            "시스템": [TutorialType.WOUND_SYSTEM, TutorialType.SKILL_SYSTEM, TutorialType.STATUS_EFFECTS],
            "고급": [TutorialType.PARTY_MANAGEMENT, TutorialType.ELEMENT_SYSTEM, TutorialType.BOSS_STRATEGY],
            "탐험": [TutorialType.DUNGEON_EXPLORATION, TutorialType.FIELD_SKILLS, TutorialType.ITEM_USAGE, TutorialType.SAVE_LOAD]
        }
        
        for category, tutorial_types in categories.items():
            menu_items.append({
                "type": "category",
                "title": category,
                "items": []
            })
            
            for tutorial_type in tutorial_types:
                if tutorial_type in self.tutorials:
                    tutorial = self.tutorials[tutorial_type]
                    status = "✅" if tutorial.completed else "📚"
                    if tutorial_type in self.completed_tutorials:
                        status = "✅ 완료"
                    elif tutorial.current_step > 0:
                        status = f"🔄 진행중 ({tutorial.current_step}/{len(tutorial.steps)})"
                    else:
                        status = "📚 새로움"
                    
                    menu_items[-1]["items"].append({
                        "type": tutorial_type,
                        "title": tutorial.title,
                        "description": tutorial.description,
                        "difficulty": tutorial.difficulty,
                        "time": tutorial.estimated_time,
                        "status": status,
                        "enabled": tutorial.enabled
                    })
        
        return menu_items
    
    def get_tutorial_progress(self) -> Dict[str, Any]:
        """튜토리얼 진행도 정보"""
        total_tutorials = len(self.tutorials)
        completed_count = len(self.completed_tutorials)
        
        progress = {
            "total": total_tutorials,
            "completed": completed_count,
            "percentage": (completed_count / total_tutorials * 100) if total_tutorials > 0 else 0,
            "current_tutorial": None
        }
        
        if self.current_tutorial:
            progress["current_tutorial"] = {
                "title": self.current_tutorial.title,
                "step": self.current_tutorial.current_step + 1,
                "total_steps": len(self.current_tutorial.steps),
                "step_percentage": ((self.current_tutorial.current_step) / len(self.current_tutorial.steps) * 100) if self.current_tutorial.steps else 0
            }
        
        return progress
    
    def save_progress(self) -> Dict[str, Any]:
        """진행도 저장용 데이터"""
        return {
            "completed_tutorials": [t.value for t in self.completed_tutorials],
            "user_preferences": self.user_preferences,
            "tutorial_enabled": self.tutorial_enabled,
            "auto_trigger": self.auto_trigger
        }
    
    def load_progress(self, data: Dict[str, Any]):
        """진행도 불러오기"""
        self.completed_tutorials = [TutorialType(t) for t in data.get("completed_tutorials", [])]
        self.user_preferences.update(data.get("user_preferences", {}))
        self.tutorial_enabled = data.get("tutorial_enabled", True)
        self.auto_trigger = data.get("auto_trigger", True)
        
        # 완료된 튜토리얼 마킹
        for tutorial_type in self.completed_tutorials:
            if tutorial_type in self.tutorials:
                self.tutorials[tutorial_type].completed = True
    
    def toggle_tutorial_system(self):
        """튜토리얼 시스템 켜기/끄기"""
        self.tutorial_enabled = not self.tutorial_enabled
        status = "활성화" if self.tutorial_enabled else "비활성화"
        print(f"📚 튜토리얼 시스템 {status}")
    
    def set_preference(self, key: str, value: Any):
        """사용자 설정 변경"""
        if key in self.user_preferences:
            self.user_preferences[key] = value
            print(f"⚙️ 설정 변경: {key} = {value}")


# 전역 튜토리얼 매니저
tutorial_manager = TutorialManager()

def get_tutorial_manager() -> TutorialManager:
    """튜토리얼 매니저 반환"""
    return tutorial_manager


def show_tutorial_selection_menu():
    """튜토리얼 선택 메뉴 표시 - 커서 방식"""
    try:
        from .cursor_menu_system import create_simple_menu
        
        progress = tutorial_manager.get_tutorial_progress()
        
        while True:
            print("\n" + "="*60)
            print("📚 튜토리얼 메뉴")
            print("="*60)
            print(f"진행도: {progress['completed']}/{progress['total']} ({progress['percentage']:.1f}%)")
            
            if progress['current_tutorial']:
                current = progress['current_tutorial']
                print(f"현재 튜토리얼: {current['title']} ({current['step']}/{current['total_steps']})")
            
            print("\n" + "-"*60)
            
            menu_data = tutorial_manager.show_tutorial_menu()
            
            # 튜토리얼 항목들을 커서 메뉴로 변환
            options = []
            descriptions = []
            choice_map = {}
            choice_num = 0
            
            for category_data in menu_data:
                # 카테고리 헤더는 비활성화된 항목으로 추가
                options.append(f"📂 {category_data['title']}")
                descriptions.append("카테고리")
                choice_map[choice_num] = None  # 선택 불가
                choice_num += 1
                
                # 카테고리 내 항목들 추가
                for item in category_data['items']:
                    choice_map[choice_num] = item['type']
                    status_color = "✅" if "완료" in item['status'] else "📚"
                    options.append(f"  {status_color} {item['title']} ({item['difficulty']}, {item['time']})")
                    descriptions.append(f"{item['description']} | 상태: {item['status']}")
                    choice_num += 1
            
            # 메뉴 하단 옵션들
            options.append("🔧 튜토리얼 설정")
            descriptions.append("튜토리얼 관련 설정을 변경합니다")
            choice_map[choice_num] = "settings"
            choice_num += 1
            
            options.append("🚪 메뉴 나가기")
            descriptions.append("메인 메뉴로 돌아갑니다")
            choice_map[choice_num] = "exit"
            
            menu = create_simple_menu("� 튜토리얼 선택", options, descriptions)
            result = menu.run()
            
            if result == -1:  # 취소
                break
            
            # 선택된 항목 처리
            selected_action = choice_map.get(result)
            if selected_action is None:
                continue  # 카테고리 헤더 선택시 무시
            elif selected_action == "exit":
                break
            elif selected_action == "settings":
                handle_tutorial_settings()
            else:
                # 특정 튜토리얼 실행
                tutorial_manager.start_tutorial(selected_action)
                progress = tutorial_manager.get_tutorial_progress()  # 진행도 업데이트
        
    except ImportError:
        # 폴백: 기존 텍스트 메뉴
        _show_tutorial_selection_menu_fallback()

def _show_tutorial_selection_menu_fallback():
    """튜토리얼 선택 메뉴 폴백 (기존 방식)"""
    print("\n" + "="*60)
    print("📚 튜토리얼 메뉴")
    print("="*60)
    
    progress = tutorial_manager.get_tutorial_progress()
    print(f"진행도: {progress['completed']}/{progress['total']} ({progress['percentage']:.1f}%)")
    
    if progress['current_tutorial']:
        current = progress['current_tutorial']
        print(f"현재 튜토리얼: {current['title']} ({current['step']}/{current['total_steps']})")
    
    print("\n" + "-"*60)
    
    menu_data = tutorial_manager.show_tutorial_menu()
    choice_map = {}
    choice_num = 1
    
    for category_data in menu_data:
        print(f"\n📂 {category_data['title']}")
        print("-" * 30)
        
        for item in category_data['items']:
            choice_map[choice_num] = item['type']
            status_color = "✅" if "완료" in item['status'] else "📚"
            print(f"{choice_num:2d}. {status_color} {item['title']} ({item['difficulty']}, {item['time']})")
            print(f"     {item['description']}")
            print(f"     상태: {item['status']}")
            choice_num += 1
    
    print(f"\n{choice_num}. 🔧 튜토리얼 설정")
    print(f"{choice_num + 1}. 🚪 메뉴 나가기")
    
    return choice_map


def handle_tutorial_settings():
    """튜토리얼 설정 메뉴 - 커서 방식"""
    try:
        from .cursor_menu_system import create_simple_menu
        
        while True:
            prefs = tutorial_manager.user_preferences
            
            # 현재 설정 상태로 옵션 텍스트 생성
            options = [
                f"💡 힌트 표시: {'켜짐' if prefs['show_hints'] else '꺼짐'}",
                f"⏩ 자동 진행: {'켜짐' if prefs['auto_advance'] else '꺼짐'}",
                f"🎭 데모 모드: {'켜짐' if prefs['demo_mode'] else '꺼짐'}",
                f"✅ 완료된 튜토리얼 숨기기: {'켜짐' if prefs['skip_completed'] else '꺼짐'}",
                f"🔄 자동 트리거: {'켜짐' if tutorial_manager.auto_trigger else '꺼짐'}",
                f"📚 튜토리얼 시스템: {'켜짐' if tutorial_manager.tutorial_enabled else '꺼짐'}",
                "🗑️ 모든 진행도 초기화",
                "❌ 돌아가기"
            ]
            
            descriptions = [
                "튜토리얼 중 힌트를 표시합니다",
                "튜토리얼을 자동으로 진행합니다",
                "데모 모드를 활성화합니다",
                "완료된 튜토리얼을 목록에서 숨깁니다",
                "상황에 맞는 튜토리얼을 자동으로 시작합니다",
                "전체 튜토리얼 시스템을 켜거나 끕니다",
                "모든 튜토리얼 진행도를 초기화합니다",
                "설정 메뉴를 나갑니다"
            ]
            
            menu = create_simple_menu("🔧 튜토리얼 설정", options, descriptions)
            result = menu.run()
            
            if result == -1 or result == 7:  # 돌아가기
                break
            elif result == 0:  # 힌트 표시
                tutorial_manager.user_preferences['show_hints'] = not prefs['show_hints']
                print("✅ 설정이 변경되었습니다.")
            elif result == 1:  # 자동 진행
                tutorial_manager.user_preferences['auto_advance'] = not prefs['auto_advance']
                print("✅ 설정이 변경되었습니다.")
            elif result == 2:  # 데모 모드
                tutorial_manager.user_preferences['demo_mode'] = not prefs['demo_mode']
                print("✅ 설정이 변경되었습니다.")
            elif result == 3:  # 완료된 튜토리얼 숨기기
                tutorial_manager.user_preferences['skip_completed'] = not prefs['skip_completed']
                print("✅ 설정이 변경되었습니다.")
            elif result == 4:  # 자동 트리거
                tutorial_manager.auto_trigger = not tutorial_manager.auto_trigger
                print("✅ 설정이 변경되었습니다.")
            elif result == 5:  # 튜토리얼 시스템
                tutorial_manager.tutorial_enabled = not tutorial_manager.tutorial_enabled
                if tutorial_manager.tutorial_enabled:
                    print("✅ 튜토리얼 시스템이 활성화되었습니다.")
                else:
                    print("⚠️ 튜토리얼 시스템이 비활성화되었습니다.")
            elif result == 6:  # 모든 진행도 초기화
                from .cursor_menu_system import create_yes_no_menu
                confirm_menu = create_yes_no_menu("정말로 모든 튜토리얼 진행도를 초기화하시겠습니까?")
                confirm_result = confirm_menu.run()
                
                if confirm_result == 0:  # 예
                    tutorial_manager.reset_all_progress()
                    print("✅ 모든 튜토리얼 진행도가 초기화되었습니다.")
                    
    except ImportError:
        # 폴백: 기존 텍스트 메뉴
        _handle_tutorial_settings_fallback()

def _handle_tutorial_settings_fallback():
    """튜토리얼 설정 메뉴 폴백 (기존 방식)"""
    print("\n" + "="*50)
    print("🔧 튜토리얼 설정")
    print("="*50)
    
    prefs = tutorial_manager.user_preferences
    print(f"1. 힌트 표시: {'켜짐' if prefs['show_hints'] else '꺼짐'}")
    print(f"2. 자동 진행: {'켜짐' if prefs['auto_advance'] else '꺼짐'}")
    print(f"3. 데모 모드: {'켜짐' if prefs['demo_mode'] else '꺼짐'}")
    print(f"4. 완료된 튜토리얼 숨기기: {'켜짐' if prefs['skip_completed'] else '꺼짐'}")
    print(f"5. 자동 트리거: {'켜짐' if tutorial_manager.auto_trigger else '꺼짐'}")
    print(f"6. 튜토리얼 시스템: {'켜짐' if tutorial_manager.tutorial_enabled else '꺼짐'}")
    print("7. 모든 진행도 초기화")
    print("8. 돌아가기")
    
    settings_map = {
        1: ("show_hints", not prefs['show_hints']),
        2: ("auto_advance", not prefs['auto_advance']),
        3: ("demo_mode", not prefs['demo_mode']),
        4: ("skip_completed", not prefs['skip_completed']),
        5: ("auto_trigger", not tutorial_manager.auto_trigger),
        6: ("tutorial_system", None),
        7: ("reset_all", None),
        8: ("back", None)
    }
