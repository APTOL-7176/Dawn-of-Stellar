"""
튜토리얼 시스템
"""

import time
from typing import Dict, List, Optional
from .ascii_effects import combat_animator, play_ascii_sound
from .settings import game_settings


class Tutorial:
    """튜토리얼 단계"""
    
    def __init__(self, title: str, content: List[str], interactive: bool = False, 
                 category: str = "basic", importance: int = 1):
        self.title = title
        self.content = content
        self.interactive = interactive
        self.category = category  # basic, advanced, combat, meta
        self.importance = importance  # 1=필수, 2=권장, 3=선택
        self.completed = False
        self.skippable = importance > 1


class TutorialManager:
    """튜토리얼 관리자"""
    
    def __init__(self):
        self.tutorials = self._create_tutorials()
        self.current_tutorial = 0
        self.tutorial_enabled = True
        self.completed_tutorials = set()
        
    def _create_tutorials(self) -> List[Tutorial]:
        """튜토리얼 생성"""
        tutorials = []
        
        # 1. 게임 소개 (필수)
        intro = Tutorial(
            "Dawn Of Stellar에 오신 것을 환영합니다!",
            [
                "🌟 Dawn Of Stellar는 파이널 판타지 오페라 옴니아 스타일의 전술 RPG입니다.",
                "",
                "📖 이 게임의 특징:",
                "  • Brave 시스템: 전투의 핵심 메커니즘",
                "  • 28개 직업: 각각 고유한 Organic Effects와 6개 스킬",
                "  • 상처 시스템: 체력 제한과 전략적 치유",
                "  • 메타 진행: 게임을 플레이할수록 강해지는 시스템",
                "  • Organic Effects: 직업의 본질을 반영하는 자연적 특성",
                "",
                "🔮 새로운 스킬 시스템:",
                "  • 각 직업마다 6개의 고유 스킬",
                "  • BRV, HP, 복합, 궁극기, 지원 스킬 타입",
                "  • 캐스팅 시스템과 특수 효과 92개 완전 구현",
                "",
                "💡 팁: 언제든지 'h' 키를 눌러 도움말을 볼 수 있습니다!",
                "",
                "지금부터 기본 조작법을 배워보겠습니다!"
            ],
            category="basic",
            importance=1
        )
        tutorials.append(intro)
        
        # 2. Brave 시스템 설명 (필수)
        brave_system = Tutorial(
            "Brave 시스템 이해하기",
            [
                "⚡ Brave 시스템은 이 게임의 핵심입니다!",
                "",
                "📊 주요 Brave 스탯:",
                "  • INT BRV: 전투 시작 시와 HP 공격 후 Brave 값",
                "  • MAX BRV: 가질 수 있는 최대 Brave 값", 
                "  • 현재 Brave: 실시간으로 변하는 Brave 포인트",
                "",
                "🔄 Brave 공격 vs HP 공격:",
                "  • Brave 공격: 상대방의 Brave를 깎고 자신의 Brave를 올림",
                "  • HP 공격: 자신의 Brave를 소모해서 실제 데미지 입힘",
                "",
                "💔 Break 시스템:",
                "  • 상대방의 Brave가 0이 되면 Break 상태",
                "  • Break 상태에서는 받는 HP 데미지가 증가!",
                "",
                "🔮 새로운 스킬 시스템:",
                "  • BRV_ATTACK: Brave 포인트 축적 공격",
                "  • HP_ATTACK: 직접 HP 피해 공격", 
                "  • BRV_HP_ATTACK: 복합 공격 (BRV 획득 + HP 피해)",
                "  • ULTIMATE: 강력한 궁극기 (높은 MP 소모)",
                "  • SUPPORT: 치유 및 버프 스킬",
                "",
                "⚠️ 중요: 각 직업의 Organic Effects가 자동으로 발동되어 전투를 도와줍니다!"
            ],
            category="basic",
            importance=1
        )
        tutorials.append(brave_system)
        
        # 3. 전투 기본 (필수)
        combat_basics = Tutorial(
            "전투 시스템 기초",
            [
                "⚔️ 전투는 ATB(Active Time Battle) 방식입니다.",
                "",
                "🎯 전투 중 선택 가능한 행동:",
                "  1. Brave 공격: 상대방 Brave 깎기 + 자신 Brave 증가",
                "  2. HP 공격: Brave 포인트로 실제 데미지 (최소 300 Brave 필요)",
                "  3. 스킬 사용: 캐릭터별 고유 스킬",
                "  4. 아이템 사용: 치유나 버프 아이템",
                "  5. 방어: 데미지 감소 + 약간의 Brave 회복",
                "",
                "💡 전략 팁:",
                "  • Brave를 충분히 쌓은 후 HP 공격하기",
                "  • 상대방을 Break 시킨 후 HP 공격하면 더 큰 데미지!",
                "  • 방어도 때로는 좋은 선택입니다",
                "",
                "🎮 조작법:",
                "  • WASD (또는 방향키): 맵 이동",
                "  • I: 인벤토리 (소모품과 장비)",
                "  • P: 파티 상태 (캐릭터 정보)",
                "  • F: 필드 활동 (스킬 & 요리 & 상인)",
                "  • Enter: 상호작용/확인",
                "  • Q: 게임 종료",
                "  • B: 게임 저장",
                "  • H: 도움말",
                "  • T: 자동전투 토글",
                "  • Z: 긴급 텔레포트 (갇혔을 때)",
                "",
                "🤖 AI 모드 (활성화시):",
                "  • M: AI 모드 설정",
                "  • R: AI 요청 처리",
                "  • Y: AI 상태 확인",
                "  • 1-9: 선택지/행동",
                "  • 1-9: 선택지/행동 (메뉴에서 숫자로 선택)",
                "  • Enter: 상호작용/확인",
            ],
            category="basic",
            importance=1
        )
        tutorials.append(combat_basics)
        
        # 4. 상처 시스템 (권장)
        wound_system = Tutorial(
            "상처 시스템 알아보기",
            [
                "🩸 이 게임만의 독특한 상처 시스템입니다!",
                "",
                "📝 상처 시스템 규칙:",
                "  • 받은 데미지의 25%가 상처로 누적",
                "  • 상처는 최대 HP의 75%까지 쌓임",
                "  • 상처가 있으면 최대 HP가 제한됨",
                "",
                "💚 상처 치유 방법:",
                "  • 제한된 최대 HP를 넘는 치유량의 25%가 상처 치유",
                "  • 예: 최대 HP가 80으로 제한된 상태에서 100 치유하면",
                "    실제 HP는 80까지만 차고, 20의 25%인 5만큼 상처 치유",
                "",
                "🚶‍♂️ 자연 치유:",
                "  • 3걸음마다 상처 1씩 회복",
                "  • 2걸음마다 MP 1씩 회복",
                "",
                "🎯 전략적 요소:",
                "  • 장기전에서는 상처 관리가 중요",
                "  • 치유 아이템을 전략적으로 사용하세요"
            ],
            category="advanced",
            importance=2
        )
        tutorials.append(wound_system)
        
        # 5. 캐릭터 선택 (권장)
        character_selection = Tutorial(
            "캐릭터 시스템",
            [
                "👥 28개 직업의 개성 있는 캐릭터 중 4명을 선택하세요!",
                "",
                "🏷️ 주요 직업별 특징:",
                "  • 전사: 불굴의 의지로 위기에서 더 강해지는 용맹한 전투자",
                "  • 아크메이지: 마력 파동으로 전장을 지배하는 최고위 마법사",
                "  • 궁수: 정밀 사격과 관통 공격의 원거리 전문가",
                "  • 도적: 독침과 암살 기술로 적을 제거하는 그림자 전사",
                "  • 성기사: 성스러운 빛으로 아군을 치유하고 악을 심판",
                "  • 암흑기사: 생명력 흡수로 자신을 강화하는 어둠의 기사",
                "  • 몽크: 연환 타격과 내공으로 적을 압도하는 무술가",
                "  • 바드: 음파와 영혼의 노래로 전장의 분위기를 조작",
                "",
                "🔮 Organic Effects 시스템:",
                "  • 각 직업은 고유한 자연적 특성 효과 보유",
                "  • 전투 중 확률적으로 발동되는 직업 본질 반영",
                "  • 예: 전사의 '불굴의_의지', 마법사의 '마력_순환'",
                "",
                "⭐ 특성 시스템:",
                "  • 각 클래스는 고유한 패시브/액티브 특성 보유",
                "  • 특성은 전투에서 자동으로 발동",
                "",
                "💡 파티 구성 팁:",
                "  • 물리/마법 딜러, 탱커, 힐러 조합 추천",
                "  • 각 직업의 고유 Organic Effects를 활용하세요"
            ],
            category="advanced",
            importance=2
        )
        tutorials.append(character_selection)
        
        # 6. 고급 전투 팁 (선택)
        advanced_combat = Tutorial(
            "고급 전투 전략",
            [
                "🎯 숙련된 플레이어를 위한 고급 팁들입니다!",
                "",
                "⚡ Brave 관리 전략:",
                "  • Break 타이밍을 노려서 큰 데미지 노리기",
                "  • 적의 턴 순서를 고려한 Brave 조절",
                "  • 방어로 안전하게 Brave 축적",
                "",
                "🔄 스킬 연계:",
                "  • 캐릭터 특성을 활용한 연계 공격",
                "  • 상태이상을 활용한 전략",
                "  • 버프/디버프 타이밍 조절",
                "",
                "📊 파티 역할 분담:",
                "  • 탱커: 적의 어그로 끌기, 파티 보호",
                "  • 딜러: 효율적인 Brave/HP 공격",
                "  • 힐러: 상처 관리, 버프 제공",
                "  • 서포터: 상황에 맞는 유틸리티 제공"
            ],
            category="advanced",
            importance=3
        )
        tutorials.append(advanced_combat)
        
        # 7. 아이템과 장비 (권장)
        items_equipment = Tutorial(
            "아이템과 장비 시스템",
            [
                "🎒 아이템과 장비를 활용해 더 강해지세요!",
                "",
                "⚔️ 장비 종류:",
                "  • 무기: 공격력 증가, 특수 효과",
                "  • 방어구: 방어력 증가, HP 보너스",
                "  • 장신구: 다양한 특수 효과",
                "",
                "💊 소모품:",
                "  • 포션: HP 회복",
                "  • 엘릭서: MP 회복",
                "  • 버프 아이템: 일시적 능력치 증가",
                "  • 상태이상 치료제: 디버프 제거",
                "",
                "💰 상점과 거래:",
                "  • 던전에서 골드와 아이템 획득",
                "  • 상점에서 장비 구매",
                "  • 희귀 아이템은 특별한 방법으로만 획득",
                "",
                "🔧 장비 관리 팁:",
                "  • 캐릭터 특성에 맞는 장비 선택",
                "  • 상황에 따른 장비 교체 고려"
            ],
            category="advanced",
            importance=2
        )
        tutorials.append(items_equipment)
        
        # 8. 메타 진행 (선택)
        meta_progression = Tutorial(
            "메타 진행 시스템",
            [
                "🌟 게임을 플레이할수록 영구적으로 강해집니다!",
                "",
                "💎 별조각 시스템:",
                "  • 게임 플레이로 별조각 획득",
                "  • 별조각으로 캐릭터 업그레이드",
                "  • 새로운 캐릭터 해금",
                "",
                "🏆 도전과제:",
                "  • 다양한 도전과제 달성",
                "  • 도전과제 완료 시 보상 획득",
                "",
                "📈 영구 강화:",
                "  • 캐릭터별 업그레이드 레벨",
                "  • 능력치 영구 증가",
                "  • 새로운 스킬 해금",
                "",
                "🔄 뉴 게임 플러스:",
                "  • 클리어 후에도 계속 플레이 가능",
                "  • 더 어려운 도전과 더 좋은 보상"
            ],
            category="meta",
            importance=3
        )
        tutorials.append(meta_progression)
        
        # 9. 조작법 (필수)
        controls = Tutorial(
            "게임 조작법",
            [
                "🎮 실제 게임 조작법을 익혀보세요!",
                "",
                "🗺️ 이동 조작:",
                "  • WASD (또는 방향키): 캐릭터 이동",
                "  • 자동으로 시야가 플레이어를 따라감",
                "",
                "📋 메뉴 조작:",
                "  • I: 인벤토리 (소모품과 장비)",
                "  • P: 파티 상태 (캐릭터 정보)",
                "  • F: 필드 활동 (스킬 & 요리 & 상인)",
                "",
                "⚙️ 시스템 조작:",
                "  • H: 도움말 (이 화면)",
                "  • Q: 게임 종료 (뒤로 가기)",
                "  • B: 게임 저장",
                "  • T: 자동전투 토글",
                "  • Z: 긴급 텔레포트 (갇혔을 때)",
                "",
                "🤖 AI 게임모드 (활성화시):",
                "  • M: AI 모드 설정",
                "  • R: AI 요청 처리", 
                "  • Y: AI 상태 확인",
                "",
                "⚔️ 전투 중:",
                "  • 1: Brave 공격",
                "  • 2: HP 공격", 
                "  • 3: 스킬 사용",
                "  • 4: 아이템 사용",
                "  • 5: 방어",
                "  • Enter: 상호작용/확인",
                "",
                "💡 유용한 팁:",
                "  • 언제든지 'h'를 눌러 도움말 확인",
                "  • 실수했다면 대부분 취소 가능",
                "  • 급할 때는 Enter로 빠르게 진행"
            ],
            category="basic",
            importance=1
        )
        tutorials.append(controls)
        
        return tutorials
    
    def get_tutorial_steps(self) -> List[Tutorial]:
        """튜토리얼 단계 목록 반환"""
        return self.tutorials
        
    def get_tutorial_count(self) -> int:
        """총 튜토리얼 개수 반환"""
        return len(self.tutorials)
    
    def should_show_tutorial(self) -> bool:
        """튜토리얼을 표시해야 하는지 확인"""
        return not game_settings.is_tutorial_completed()
    
    def filter_tutorials_by_importance(self, max_importance: int = 2) -> List[Tutorial]:
        """중요도에 따라 튜토리얼 필터링"""
        return [t for t in self.tutorials if t.importance <= max_importance]
    
    def start_tutorial(self):
        """튜토리얼 시작"""
        # 이미 완료했고 스킵 설정이 켜져 있으면 건너뛰기
        if game_settings.is_tutorial_completed() and game_settings.should_skip_intro():
            print("튜토리얼을 건너뜁니다...")
            return
            
        print("\n" + "="*80)
        print("🎓 튜토리얼을 시작합니다!")
        print("="*80)
        
        # 튜토리얼 완료 여부에 따른 옵션 제공
        if game_settings.is_tutorial_completed():
            print("이미 튜토리얼을 완료하셨습니다.")
            print("1. 전체 튜토리얼 다시 보기")
            print("2. 필수 내용만 보기")
            print("3. 건너뛰기")
            choice = input("선택하세요 (1-3): ").strip()
            
            if choice == '3':
                return
            elif choice == '2':
                tutorials_to_show = self.filter_tutorials_by_importance(1)  # 필수만
            else:
                tutorials_to_show = self.tutorials  # 전체
        else:
            # 처음 플레이하는 경우
            print("처음 플레이하시는군요! 튜토리얼을 추천드립니다.")
            print("1. 전체 튜토리얼 보기 (권장)")
            print("2. 필수 내용만 보기")
            print("3. 건너뛰기")
            choice = input("선택하세요 (1-3): ").strip()
            
            if choice == '3':
                self.tutorial_enabled = False
                return
            elif choice == '2':
                tutorials_to_show = self.filter_tutorials_by_importance(1)  # 필수만
            else:
                tutorials_to_show = self.tutorials  # 전체
        
        # 선택된 튜토리얼 진행
        for i, tutorial in enumerate(tutorials_to_show):
            self.show_tutorial_step(tutorial, i + 1, len(tutorials_to_show))
            
        self.show_tutorial_complete()
        
        # 튜토리얼 완료 표시
        game_settings.set_tutorial_completed(True)
        
    def start_quick_tutorial(self):
        """빠른 튜토리얼 (필수 내용만)"""
        essential_tutorials = self.filter_tutorials_by_importance(1)
        
        print("\n" + "="*60)
        print("⚡ 빠른 튜토리얼 (필수 내용)")
        print("="*60)
        
        for i, tutorial in enumerate(essential_tutorials):
            self.show_tutorial_step(tutorial, i + 1, len(essential_tutorials))
        
        game_settings.set_tutorial_completed(True)
        
    def show_tutorial_step(self, tutorial: Tutorial, step: int, total: int):
        """튜토리얼 단계 표시"""
        # 중요도 표시
        importance_icon = "🔴" if tutorial.importance == 1 else "🟡" if tutorial.importance == 2 else "🟢"
        category_icon = {"basic": "📚", "advanced": "🎯", "combat": "⚔️", "meta": "🌟"}.get(tutorial.category, "📖")
        
        print(f"\n{'='*80}")
        print(f"{category_icon} 튜토리얼 {step}/{total}: {tutorial.title} {importance_icon}")
        if tutorial.skippable:
            print("💡 이 튜토리얼은 건너뛸 수 있습니다 (Enter를 길게 누르세요)")
        print(f"{'='*80}")
        
        # 자동 진행 모드 확인
        auto_proceed = game_settings.get("tutorial", "auto_proceed", False)
        
        for line in tutorial.content:
            if line.strip():
                if auto_proceed:
                    print(line)
                    time.sleep(0.1)
                else:
                    combat_animator.typewriter_effect(line, 0.02)
            else:
                print()
            if not auto_proceed:
                time.sleep(0.1)
                
        print(f"\n{'─'*80}")
        
        # 스킵 가능한 튜토리얼의 경우 옵션 제공
        if tutorial.skippable:
            print("Enter: 계속 | s: 남은 선택적 튜토리얼 모두 건너뛰기")
            user_input = input().strip().lower()
            if user_input == 's':
                return 'skip_optional'
        else:
            input("계속하려면 Enter를 누르세요...")
            
        play_ascii_sound("menu")
        return 'continue'
        
    def show_tutorial_complete(self):
        """튜토리얼 완료"""
        print(f"\n{'🎉'*20}")
        print("       튜토리얼 완료!")
        print("     이제 게임을 시작하세요!")
        print(f"{'🎉'*20}")
        
        # 설정 저장 안내
        if not game_settings.is_tutorial_completed():
            print("\n💾 튜토리얼 완료가 저장되었습니다.")
            print("다음에는 게임 설정에서 튜토리얼을 건너뛸 수 있습니다.")
        
        play_ascii_sound("level_up")
        time.sleep(1)
        
    def show_contextual_help(self, context: str = "general"):
        """상황별 도움말"""
        help_content = {
            "general": [
                "� 일반 도움말",
                "h: 도움말 | q: 종료 | Enter: 확인",
                "WASD: 이동 | I: 인벤토리 | P: 파티상태 | F: 필드활동 | C: 요리"
            ],
            "combat": [
                "⚔️ 전투 도움말",
                "1: Brave 공격 | 2: HP 공격 | 3: 스킬",
                "4: 아이템 | 5: 방어 | Space: 대기"
            ],
            "character_select": [
                "👥 캐릭터 선택 도움말", 
                "숫자키: 캐릭터 선택 | Enter: 확정",
                "균형잡힌 파티 구성을 추천합니다"
            ]
        }
        
        content = help_content.get(context, help_content["general"])
        print(f"\n{'─'*50}")
        for line in content:
            print(line)
        print(f"{'─'*50}")
        
        # 키 입력 대기 추가
        try:
            from .input_utils import wait_for_any_key
            wait_for_any_key("\n계속하려면 아무 키나 누르세요...")
        except ImportError:
            input("\n계속하려면 Enter를 누르세요...")
        
    def show_quick_help(self):
        """빠른 도움말"""
        print(f"\n{'='*60}")
        print("🆘 빠른 도움말")
        print(f"{'='*60}")
        
        print("🎮 기본 조작:")
        print("  WASD: 이동 | I: 인벤토리 | F: 스킬 | P: 파티 | U: 필드아이템")
        print("  H: 도움말 | Q: 종료 | B: 저장 | L: 불러오기")
        print()
        
        print("⚔️ 전투 시스템:")
        print("  ⚡ Brave 공격: 상대 Brave ↓, 내 Brave ↑")
        print("  💀 HP 공격: 내 Brave로 실제 데미지 (300+ 권장)")
        print("  💔 Break: 상대 Brave 0 → HP 데미지 크게 증가")
        print("  🩸 상처: 받은 데미지 25% 누적, 최대 HP 제한")
        print("  💚 상처 치유: 초과 회복량의 25%로 상처 치유")
        print()
        
        print("🎯 게임 목표:")
        print("  • 던전을 탐험하며 계단을 찾아 다음 층으로 이동")
        print("  • 5층마다 특수층, 10층마다 보스층 등장")
        print("  • 파티를 강화하며 더 깊은 층을 목표로!")
        print()
        
        print("🌍 필드 활동 (F키):")
        print("  🔍 탐지: 함정탐지, 비밀탐지 (도적/궁수/철학자)")
        print("  🔧 조작: 자물쇠해제, 함정해제, 기계조작")
        print("  ✨ 마법: 신성마법, 정령술, 자연친화, 지식탐구")
        print()
        
        print("✨ 특수 장소:")
        print("  🏛️ 제단/신전: 파티 완전 회복 (신성마법 필요)")
        print("  ⛲ 치유의 샘: 파티 체력 25% 회복")
        print("  📚 고대 서재: 경험치 증가 (지식탐구 필요)")
        print("  🔨 마법 대장간: 장비 강화 (기계공학 필요)")
        print("  🌿 비밀 정원: 상태이상 치유 (자연친화 필요)")
        print("  💎 마력 수정: 마나 완전 충전 (정령술 필요)")
        print("  📦 보물상자: 귀중한 아이템 (잠긴 것은 해제 필요)")
        print()
        
        print("⚠️ 위험 요소:")
        print("  ☠️ 저주받은 제단: 체력 25% 감소")
        print("  ☣️ 독성 구름: 파티 전체 중독")
        print("  🌀 어둠의 포털: 주변 위험도 증가")
        print("  🕳️ 불안정한 바닥: 랜덤 낙하 피해")
        print("  🗃️ 저주받은 상자: 마나 감소 + 아이템")
        print()
        print("✨ 마법 스킬:")
        print("  • 신성마법 (성기사/신관): 제단에서 축복 획득")
        print("  • 정령술 (정령술사/아크메이지): 마법 수정에서 마력 충전")
        print("  • 자연친화 (드루이드): 정원에서 자연의 힘 획득")
        print("  • 지식탐구 (철학자/아크메이지): 고대 서적에서 지혜 습득")
        print("  • 기계공학 (기계공학자): 대장간에서 장비 강화")
        print()
        print("💡 팁:")
        print("  • F키로 필드 활동 메뉴 열기")
        print("  • 필요한 직업이 파티에 있어야 스킬 사용 가능")
        print("  • 부정적 요소도 때로는 피할 수 없는 선택일 수 있음")
        print("  • 신중하게 상호작용할 요소를 선택하세요")
        print()
        print("💼 아이템 사용:")
        print("🍶 필드 아이템: U키 - 텐트, 포션 등 필드 전용")
        print("🧳 인벤토리: I키 - 전체 아이템 관리")
        print("⚔️ 전투 아이템: 전투 중 '4번' 선택")
        print()
        print("🎮 조작:")
        print("이동: WASD | 필드 아이템: U | 스킬: F | 파티: P")
        print("인벤토리: I | 도움말: H | 저장: SAVE | 불러오기: LOAD")
        print(f"{'='*60}")
        
        # 키 입력 대기 추가
        try:
            from .input_utils import wait_for_any_key
            wait_for_any_key("\n계속하려면 아무 키나 누르세요...")
        except ImportError:
            input("\n계속하려면 Enter를 누르세요...")
        
    def show_combat_help(self):
        """전투 중 도움말 (2025년 8월 6일 업데이트)"""
        print(f"\n{'─'*60}")
        print("⚔️ 전투 행동 가이드:")
        print("1️⃣ Brave 공격 - 기본 공격으로 Brave 쌓기")
        print("2️⃣ HP 공격 - Brave로 실제 데미지 (방어력 영향 받음)")
        print("3️⃣ 스킬 - 캐릭터 고유 능력 사용")
        print("4️⃣ 아이템 - 치유/버프 아이템 사용")
        print("5️⃣ 방어 - 데미지 감소 + Brave 회복")
        print(f"{'─'*60}")
        print("🆕 새로운 시스템 (2025.08.06 업데이트):")
        print("🛡️ 통합 방어력 시스템:")
        print("  • BRV 공격: 방어력에 크게 영향 받음")
        print("  • HP 공격: 방어력에 약간 영향 받음 (30% 감소)")
        print("  • 마법 공격: 마법 방어력 기준으로 계산")
        print()
        print("💥 광전사 전투 팁:")
        print("  • HP 15% 이하에서 공격력 300% 증가!")
        print("  • 위험할수록 더 강해지는 고위험 고수익 직업")
        print("  • 생존 본능: HP 낮을 때 회피율+50%, 크리티컬+30%")
        print()
        print("🌌 차원술사 전투 팁:")
        print("  • 탱커 역할로 완전 개편됨")
        print("  • 회피 중심의 방어적 플레이 (20% 기본 회피율)")
        print("  • 파티 보호: 아군 피해를 대신 받아 15% 감소")
        print("  • 위험 감지: 강력한 적의 공격을 미리 차단")
        print(f"{'─'*60}")
        
        # 키 입력 대기 추가
        try:
            from .input_utils import wait_for_any_key
            wait_for_any_key("\n계속하려면 아무 키나 누르세요...")
        except ImportError:
            input("\n계속하려면 Enter를 누르세요...")
        
    def show_trait_help(self):
        """특성 시스템 도움말 (2025년 8월 6일 신규 추가)"""
        print(f"\n{'='*70}")
        print("🌟 특성 시스템 완전 가이드")
        print(f"{'='*70}")
        print("📖 특성 타입 분류:")
        print("  🔄 Passive: 항상 발동되는 지속 효과")
        print("  ⚡ Trigger: 특정 조건에서 자동 발동")
        print("  🎯 Active: 플레이어가 직접 활성화")
        print()
        print("💥 광전사 특성 (극한 생존형):")
        print("  🔥 혈투의 광기 (Trigger):")
        print("    - HP 15% 이하에서 공격력 100% 증가 (너프됨)")
        print("    - 모든 공격이 HP 공격으로 변환")
        print("    - 극한 상황에서 강력한 화력 발휘")
        print()
        print("  🛡️ 불굴의 의지 (Trigger):")
        print("    - HP 15% 이하에서 1턴간 무적 상태")
        print("    - 모든 상태이상 면역")
        print("    - 마지막 한 방을 버티는 생존 기술")
        print()
        print("  ⚔️ 광전사의 분노 (Passive):")
        print("    - 받는 피해의 50%를 다음 공격에 추가")
        print("    - 맞을수록 더 강해지는 역전 메커니즘")
        print()
        print("  💀 최후의 일격 (Trigger):")
        print("    - HP 10% 이하일 때 다음 공격이 치명타 + 200% 추가 피해")
        print("    - 절체절명의 순간에 발동하는 필살기")
        print()
        print("  🦅 생존 본능 (Passive):")
        print("    - HP 15% 이하에서 회피율 +50%, 크리티컬 +30%")
        print("    - 위험할 때 더욱 예리해지는 야생의 감각")
        print()
        print("🌌 차원술사 특성 (탱커 전환):")
        print("  🌀 차원 도약 (Trigger):")
        print("    - 공격받을 때 30% 확률로 완전 회피")
        print("    - 회피 성공 시 반격 데미지")
        print("    - 공간을 이용한 회피 기술")
        print()
        print("  🌊 공간 왜곡 (Passive):")
        print("    - 모든 공격에 20% 회피율")
        print("    - 회피 시 적에게 반사 피해")
        print("    - 공간을 비틀어 공격을 무력화")
        print()
        print("  🛡️ 차원의 방패 (Passive):")
        print("    - 아군이 받는 피해를 15% 확률로 대신 받기")
        print("    - 대신 받는 피해는 30% 감소")
        print("    - 차원 공간으로 아군 보호")
        print()
        print("  ⏰ 시공간 조작 (Trigger):")
        print("    - 적의 강력한 공격을 50% 확률로 무효화")
        print("    - 시간을 조작하여 공격 자체를 없애버림")
        print()
        print("  🔮 차원술사의 직감 (Passive):")
        print("    - 위험한 적의 행동을 미리 감지")
        print("    - 파티에게 위험 경고 및 대응 시간 제공")
        print()
        print("🤖 AI 전술 변화:")
        print("  광전사: HP 낮을수록 극도로 공격적, 빠른 처치 우선")
        print("  차원술사: 방어 중심, 위험한 적 무력화, 파티 보호")
        print(f"{'='*70}")
        
        # 키 입력 대기
        try:
            from .input_utils import wait_for_any_key
            wait_for_any_key("\n계속하려면 아무 키나 누르세요...")
        except ImportError:
            input("\n계속하려면 Enter를 누르세요...")
        
    def show_tutorial_menu(self):
        """튜토리얼 메뉴 - 커서 네비게이션"""
        try:
            from .cursor_menu_system import CursorMenu
            from .input_utils import KeyboardInput
            from .color_text import bright_cyan, bright_yellow, bright_green
            
            keyboard = KeyboardInput()
            
            while True:
                # 메뉴 옵션
                options = [
                    "📖 전체 튜토리얼 보기",
                    "⭐ 필수 내용만 보기", 
                    "🎯 고급 팁만 보기",
                    "🔍 특정 주제 선택",
                    "⚡ 빠른 도움말"
                ]
                
                descriptions = [
                    "모든 튜토리얼을 순서대로 봅니다",
                    "필수 내용만 빠르게 봅니다",
                    "고급 팁과 전략을 봅니다",
                    "원하는 주제를 선택해서 봅니다",
                    "핵심 조작법만 빠르게 확인합니다"
                ]
                
                # 커서 메뉴 생성
                menu = CursorMenu(
                    "📚 튜토리얼 메뉴",
                    options, descriptions, cancellable=True
                )
                
                # 메뉴 실행
                result = menu.run()
                
                if result is None:  # 취소
                    break
                elif result == 0:  # 전체 튜토리얼
                    for i, tutorial in enumerate(self.tutorials):
                        self.show_tutorial_step(tutorial, i + 1, len(self.tutorials))
                elif result == 1:  # 필수 내용만
                    essential = self.filter_tutorials_by_importance(1)
                    for i, tutorial in enumerate(essential):
                        self.show_tutorial_step(tutorial, i + 1, len(essential))
                elif result == 2:  # 고급 팁만
                    advanced = [t for t in self.tutorials if t.category == "advanced"]
                    for i, tutorial in enumerate(advanced):
                        self.show_tutorial_step(tutorial, i + 1, len(advanced))
                elif result == 3:  # 특정 주제 선택
                    self.show_topic_selection()
                elif result == 4:  # 빠른 도움말
                    self.show_quick_help()
                    
        except ImportError:
            # 커서 시스템이 없으면 기존 방식 사용
            self._show_tutorial_menu_legacy()
    
    def _show_tutorial_menu_legacy(self):
        """기존 튜토리얼 메뉴 (fallback)"""
        while True:
            print("\n" + "="*60)
            print("📚 튜토리얼 메뉴")
            print("="*60)
            print("1. 전체 튜토리얼 보기")
            print("2. 필수 내용만 보기") 
            print("3. 고급 팁만 보기")
            print("4. 특정 주제 선택")
            print("5. 빠른 도움말")
            print("0. 돌아가기")
            print()
            
            choice = input("선택하세요: ").strip()
            
            if choice == '1':
                for i, tutorial in enumerate(self.tutorials):
                    self.show_tutorial_step(tutorial, i + 1, len(self.tutorials))
            elif choice == '2':
                essential = self.filter_tutorials_by_importance(1)
                for i, tutorial in enumerate(essential):
                    self.show_tutorial_step(tutorial, i + 1, len(essential))
            elif choice == '3':
                advanced = [t for t in self.tutorials if t.category == "advanced"]
                for i, tutorial in enumerate(advanced):
                    self.show_tutorial_step(tutorial, i + 1, len(advanced))
            elif choice == '4':
                self.show_topic_selection()
            elif choice == '5':
                self.show_quick_help()
            elif choice == '0':
                break
            else:
                print("유효하지 않은 선택입니다.")
    
    def show_topic_selection(self):
        """주제별 튜토리얼 선택"""
        categories = {
            "basic": "기초",
            "advanced": "고급",
            "combat": "전투",
            "meta": "메타게임"
        }
        
        print("\n주제를 선택하세요:")
        for i, (key, name) in enumerate(categories.items(), 1):
            count = len([t for t in self.tutorials if t.category == key])
            print(f"{i}. {name} ({count}개)")
        
        try:
            choice = int(input("선택: ")) - 1
            category = list(categories.keys())[choice]
            topic_tutorials = [t for t in self.tutorials if t.category == category]
            
            for i, tutorial in enumerate(topic_tutorials):
                self.show_tutorial_step(tutorial, i + 1, len(topic_tutorials))
        except (ValueError, IndexError):
            print("유효하지 않은 선택입니다.")


# 전역 튜토리얼 매니저
tutorial_manager = TutorialManager()

def show_tutorial():
    """튜토리얼 표시"""
    tutorial_manager.start_tutorial()

def show_quick_tutorial():
    """빠른 튜토리얼"""
    tutorial_manager.start_quick_tutorial()

def show_tutorial_menu():
    """튜토리얼 메뉴"""
    tutorial_manager.show_tutorial_menu()
    
def show_help():
    """도움말 표시"""
    tutorial_manager.show_quick_help()
    
def show_combat_help():
    """전투 도움말 표시"""
    tutorial_manager.show_combat_help()

def show_contextual_help(context: str = "general"):
    """상황별 도움말"""
    tutorial_manager.show_contextual_help(context)

def is_tutorial_completed():
    """튜토리얼 완료 여부"""
    return game_settings.is_tutorial_completed()

def should_show_tutorial():
    """튜토리얼을 보여줘야 하는지"""
    return tutorial_manager.should_show_tutorial()
