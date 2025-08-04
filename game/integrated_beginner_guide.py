"""
통합 초보자 가이드 시스템
Dawn Of Stellar 입문자를 위한 친화적인 안내 + 기존 튜토리얼 통합
"""

from typing import Dict, List, Optional
from game.cursor_menu_system import CursorMenu
from game.ascii_effects import play_ascii_sound
import time
import sys


def typewriter_effect(text: str, delay: float = 0.03, pause_on_punctuation: bool = True):
    """타이핑 효과로 텍스트를 한 글자씩 출력"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
        
        # 문장 부호에서 잠시 멈춤
        if pause_on_punctuation and char in '.!?:':
            time.sleep(0.3)
        elif char in ',;':
            time.sleep(0.1)
    print()  # 줄바꿈


def wait_for_user_input(message: str = "📖 계속 읽으려면 Enter를 누르세요..."):
    """사용자 입력을 기다림"""
    print(f"\n{message}")
    try:
        input()
    except KeyboardInterrupt:
        print("\n⚠️ 가이드를 중단합니다.")
        return False
    return True


class IntegratedBeginnerGuide:
    """통합된 초보자 가이드 시스템"""
    
    def __init__(self):
        self.guide_sections = self._create_guide_sections()
        self.current_progress = 0
        
    def _create_guide_sections(self) -> Dict[str, Dict]:
        """초보자 가이드 섹션 생성"""
        return {
            "게임_소개": {
                "title": "🌟 Dawn Of Stellar 처음 시작하기",
                "description": "게임이 처음이신가요? 걱정 마세요!",
                "content": [
                    "👋 안녕하세요! Dawn Of Stellar에 오신 것을 환영합니다!",
                    "",
                    "🎮 이 게임이 처음이시라면:",
                    "  • 천천히 따라오시면 됩니다",
                    "  • 실수해도 괜찮아요! 다시 시도할 수 있습니다", 
                    "  • 언제든지 도움말(H키)을 확인하세요",
                    "",
                    "🎯 게임의 목표:",
                    "  1. 4명의 캐릭터로 파티를 구성하세요",
                    "  2. 던전을 탐험하며 적을 물리치세요",
                    "  3. 경험치와 아이템을 얻어 더 강해지세요",
                    "",
                    "💡 궁금한 것이 있으면 언제든지 물어보세요!"
                ],
                "difficulty": "초급",
                "estimated_time": "2분",
                "category": "basic"
            },
            
            "Brave_쉽게_이해하기": {
                "title": "⚡ Brave 시스템, 쉽게 배우기",
                "description": "게임의 핵심! 하지만 어렵지 않아요",
                "content": [
                    "🤔 Brave가 뭔가요?",
                    "  → 공격력을 쌓는 포인트라고 생각하세요!",
                    "",
                    "📊 간단한 비유로 설명:",
                    "  • Brave = 화살을 당기는 힘",
                    "  • 많이 당길수록 더 강한 화살 발사 가능",
                    "  • HP 공격 = 화살 발사하기",
                    "",
                    "🎯 실전에서는:",
                    "  1. Brave 공격으로 힘을 모으기 (화살 당기기)",
                    "  2. 충분히 모았다면 HP 공격 (화살 발사)",
                    "  3. 상대방 HP가 0이 되면 승리!",
                    "",
                    "✨ 팁: 처음엔 300 이상 모으고 HP 공격해보세요!",
                    "",
                    "⚠️ Break 시스템:",
                    "  • 상대방의 Brave가 0이 되면 Break 상태",
                    "  • Break 상태에서는 받는 HP 데미지가 증가!"
                ],
                "difficulty": "초급",
                "estimated_time": "3분",
                "category": "combat"
            },
            
            "첫_전투_가이드": {
                "title": "⚔️ 첫 전투, 무서워하지 마세요!",
                "description": "단계별로 천천히 따라해보기",
                "content": [
                    "😰 전투가 무서우시나요? 괜찮습니다!",
                    "",
                    "🎮 전투 화면에서 할 수 있는 것들:",
                    "  1️⃣ Brave 공격 - 안전하게 힘 모으기",
                    "  2️⃣ HP 공격 - 실제 데미지 주기",
                    "  3️⃣ 스킬 - 특별한 능력 사용",
                    "  4️⃣ 아이템 - 치유나 도움 아이템",
                    "  5️⃣ 방어 - 안전하게 턴 넘기기",
                    "",
                    "🔰 초보자 추천 패턴:",
                    "  → Brave 공격 → Brave 공격 → HP 공격 → 반복!",
                    "",
                    "⚠️ 주의사항:",
                    "  • HP가 빨간색이면 치유 아이템 사용",
                    "  • 적이 강해 보이면 방어도 좋은 선택",
                    "",
                    "💪 자신감을 가지세요! 연습하면 늘어요!",
                    "",
                    "🩸 상처 시스템도 알아두세요:",
                    "  • 받은 데미지의 25%가 상처로 누적됩니다",
                    "  • 상처는 최대 HP를 제한해요",
                    "  • 초과 치유량의 25%로 상처가 치유됩니다"
                ],
                "difficulty": "초급", 
                "estimated_time": "5분",
                "category": "combat"
            },
            
            "캐릭터_고르기_도움": {
                "title": "👥 어떤 캐릭터를 골라야 할까요?",
                "description": "초보자를 위한 캐릭터 선택 가이드",
                "content": [
                    "🤔 27명 중에 어떻게 고르죠?",
                    "  → 걱정 마세요! 좋은 조합을 알려드릴게요",
                    "",
                    "🌟 초보자 추천 파티 구성:",
                    "  1. 전사 (탱커) - 체력이 많아서 안전",
                    "  2. 궁수 (딜러) - 빠르고 정확한 공격수",
                    "  3. 성기사 (힐러) - 치유와 방어 담당",
                    "  4. 아크메이지 (마법딜러) - 강력한 마법 공격",
                    "",
                    "✨ 각 역할 설명:",
                    "  • 탱커: 적의 공격을 버텨주는 든든한 방패",
                    "  • 딜러: 적을 빠르게 처치하는 공격수",
                    "  • 힐러: 동료를 치유하는 생명의 은인",
                    "  • 마법딜러: 특별한 마법으로 상황 해결사",
                    "",
                    "🏷️ 전체 27개 직업 분류:",
                    "  💪 탱커: 전사, 성기사, 기사, 검투사, 용기사, 광전사",
                    "  ⚔️ 딜러: 궁수, 도적, 암살자, 검성, 해적, 사무라이, 마검사",
                    "  🔮 마법사: 아크메이지, 네크로맨서, 정령술사, 시간술사, 연금술사, 차원술사",
                    "  🎵 서포터: 바드, 신관, 드루이드, 무당, 철학자",
                    "  🔧 하이브리드: 암흑기사, 몽크, 기계공학자",
                    "",
                    "🎯 고급 조합 팁:",
                    "  • 성기사 + 신관 = 신성 시너지 (언데드에게 강함)",
                    "  • 드루이드 + 정령술사 = 자연 조화 (MP 회복 증가)",
                    "  • 바드 + 아크메이지 = 마법 증폭 (마법 데미지 업)",
                    "",
                    "💡 나중에 다른 캐릭터도 사용해보세요!",
                    "   게임을 여러 번 플레이하면서 취향을 찾아가세요!"
                ],
                "difficulty": "초급",
                "estimated_time": "4분",
                "category": "advanced"
            },
            
            "던전_탐험_기초": {
                "title": "🗺️ 던전 탐험, 이것만 알면 OK!",
                "description": "맵을 돌아다니는 기본 방법",
                "content": [
                    "🚶‍♂️ 던전에서 움직이기:",
                    "  • WASD 키로 이동",
                    "  • 벽(#)은 지나갈 수 없어요",
                    "  • 바닥(.)은 자유롭게 이동 가능",
                    "",
                    "🔍 던전에서 만날 수 있는 것들:",
                    "  • E: 적 - 전투가 시작됩니다",
                    "  • T: 보물상자 - 좋은 아이템!",
                    "  • >: 계단 - 다음 층으로",
                    "  • S: 상점 - 아이템 구매/판매", 
                    "",
                    "🎒 아이템 관리:",
                    "  • I키로 인벤토리 확인",
                    "  • 체력이 낮으면 포션 사용",
                    "  • 가방이 가득 차면 필요없는 것 버리기",
                    "",
                    "⚡ 유용한 단축키:",
                    "  • H: 도움말",
                    "  • P: 파티 상태 확인",
                    "  • F: 필드 활동 (스킬/요리)",
                    "  • C: 요리 메뉴",
                    "  • ESC: 일시정지 메뉴",
                    "",
                    "🔮 필드 스킬도 활용하세요:",
                    "  • 탐지: 숨겨진 함정이나 보물 발견",
                    "  • 순간이동: 빠른 이동 (MP 소모)",
                    "  • 축복: 파티원 능력치 향상"
                ],
                "difficulty": "초급",
                "estimated_time": "4분",
                "category": "basic"
            },
            
            "레벨업_성장_시스템": {
                "title": "📈 캐릭터 키우기 & 성장",
                "description": "더 강해지는 방법들",
                "content": [
                    "💪 캐릭터가 강해지는 방법:",
                    "",
                    "🎯 1. 레벨 업:",
                    "  • 적을 물리치면 경험치 획득",
                    "  • 레벨이 오르면 모든 스탯 증가",
                    "  • 새로운 스킬 해금 가능",
                    "",
                    "⚔️ 2. 장비 강화:",
                    "  • 더 좋은 무기와 방어구 착용",
                    "  • 던전에서 발견하거나 상점에서 구매",
                    "  • 희귀한 장비일수록 강력한 효과",
                    "",
                    "✨ 3. 메타 진행:",
                    "  • 게임을 클리어하면 영구적인 보너스",
                    "  • 다음 플레이 때 더 강한 상태로 시작",
                    "  • 새로운 컨텐츠 해금",
                    "",
                    "🏆 4. 특성 시스템:",
                    "  • 각 클래스마다 고유한 특별 능력",
                    "  • 패시브 특성은 자동으로 발동",
                    "  • 액티브 특성은 직접 사용 가능",
                    "",
                    "🌟 5. 별조각 시스템:",
                    "  • 게임 플레이로 별조각 획득",
                    "  • 별조각으로 새 캐릭터 해금",
                    "  • 영구 업그레이드 구매 가능"
                ],
                "difficulty": "중급",
                "estimated_time": "5분",
                "category": "meta"
            },
            
            "고급_전투_팁": {
                "title": "🎯 전투 고수가 되는 비법",
                "description": "더 전략적으로 싸우는 방법",
                "content": [
                    "🔥 고급 전투 전략을 알려드릴게요!",
                    "",
                    "⚡ Brave 관리의 달인되기:",
                    "  • Break 타이밍을 노려서 큰 데미지 노리기",
                    "  • 적의 턴 순서를 고려한 Brave 조절",
                    "  • 방어로 안전하게 Brave 축적",
                    "",
                    "🔄 스킬 연계 마스터:",
                    "  • 캐릭터 특성을 활용한 연계 공격",
                    "  • 상태이상을 활용한 전략",
                    "  • 버프/디버프 타이밍 조절",
                    "",
                    "📊 파티 역할 분담:",
                    "  • 탱커: 적의 어그로 끌기, 파티 보호",
                    "  • 딜러: 효율적인 Brave/HP 공격",
                    "  • 힐러: 상처 관리, 버프 제공",
                    "  • 서포터: 상황에 맞는 유틸리티 제공",
                    "",
                    "💡 프로 팁:",
                    "  • 적의 패턴을 파악하세요",
                    "  • 상황에 맞는 장비 교체",
                    "  • 아이템 타이밍이 승부를 결정해요"
                ],
                "difficulty": "고급",
                "estimated_time": "6분",
                "category": "advanced"
            }
        }
    
    def show_main_menu(self) -> Optional[str]:
        """초보자 가이드 메인 메뉴"""
        print("\n" + "="*60)
        print("🔰 초보자 가이드 - Dawn Of Stellar 입문서")
        print("="*60)
        
        menu_options = []
        
        # 난이도별로 섹션 정리
        beginner_sections = []
        intermediate_sections = []
        advanced_sections = []
        
        for key, section in self.guide_sections.items():
            if section["difficulty"] == "초급":
                beginner_sections.append((key, section))
            elif section["difficulty"] == "중급":
                intermediate_sections.append((key, section))
            else:
                advanced_sections.append((key, section))
        
        # 초급 섹션들
        if beginner_sections:
            for key, section in beginner_sections:
                difficulty_icon = "🔰"
                option_text = f"{difficulty_icon} {section['title']}"
                detail_text = f"{section['description']}\n예상 시간: {section['estimated_time']} | 난이도: {section['difficulty']}"
                menu_options.append({'text': option_text, 'detail': detail_text, 'value': key})
        
        # 중급 섹션들  
        if intermediate_sections:
            for key, section in intermediate_sections:
                difficulty_icon = "⭐"
                option_text = f"{difficulty_icon} {section['title']}"
                detail_text = f"{section['description']}\n예상 시간: {section['estimated_time']} | 난이도: {section['difficulty']}"
                menu_options.append({'text': option_text, 'detail': detail_text, 'value': key})
        
        # 고급 섹션들
        if advanced_sections:
            for key, section in advanced_sections:
                difficulty_icon = "🏆"
                option_text = f"{difficulty_icon} {section['title']}"
                detail_text = f"{section['description']}\n예상 시간: {section['estimated_time']} | 난이도: {section['difficulty']}"
                menu_options.append({'text': option_text, 'detail': detail_text, 'value': key})
        
        # 추가 옵션들
        menu_options.extend([
            {
                'text': "📖 전체 가이드 보기",
                'detail': "모든 가이드를 순서대로 봅니다",
                'value': "show_all"
            },
            {
                'text': "⚡ 빠른 시작 가이드",
                'detail': "꼭 필요한 내용만 빠르게 확인합니다",
                'value': "quick_start"
            },
            {
                'text': "🎮 실제 게임 시작하기",
                'detail': "가이드를 마치고 본격적으로 게임을 시작합니다",
                'value': "start_game"
            },
            {
                'text': "❓ 자주 묻는 질문 (FAQ)",
                'detail': "초보자들이 자주 궁금해하는 내용들",
                'value': "faq"
            },
            {
                'text': "🚪 나가기",
                'detail': "가이드를 종료하고 메인 메뉴로 돌아갑니다",
                'value': "exit"
            }
        ])
        
        menu = CursorMenu(
            title="초보자 가이드 선택",
            options=[opt['text'] for opt in menu_options],
            descriptions=[opt['detail'] for opt in menu_options]
        )
        
        choice_index = menu.run()
        if choice_index is not None and 0 <= choice_index < len(menu_options):
            return menu_options[choice_index]['value']
        return None
    
    def show_section(self, section_key: str):
        """특정 섹션 표시"""
        if section_key not in self.guide_sections:
            print("❌ 해당 가이드를 찾을 수 없습니다.")
            return
            
        section = self.guide_sections[section_key]
        
        print("\n" + "="*60)
        print(f"📖 {section['title']}")
        print("="*60)
        print(f"💡 {section['description']}")
        print(f"⏱️ 예상 시간: {section['estimated_time']} | 📊 난이도: {section['difficulty']}")
        print("-"*60)
        
        # 타이핑 효과로 내용 표시 - 한 글자씩 천천히
        line_count = 0
        for line in section['content']:
            if line.strip() == "":  # 빈 줄은 그냥 출력
                print()
            else:
                typewriter_effect(line, delay=0.04)  # 한 글자당 0.04초
            
            line_count += 1
            
            # 3-4줄마다 사용자 입력 대기
            if line_count % 4 == 0 and line.strip() != "":
                if not wait_for_user_input("📖 계속 읽으려면 Enter를 누르세요... (Ctrl+C로 건너뛰기)"):
                    break
                    
        print("\n" + "-"*60)
        
        # 진행 옵션
        menu_options = [
            {'text': "✅ 이해했습니다", 'detail': "다음 단계로 진행합니다", 'value': "understood"},
            {'text': "🔄 다시 읽기", 'detail': "이 가이드를 다시 봅니다", 'value': "reread"},
            {'text': "🏠 가이드 메뉴로", 'detail': "가이드 메인 메뉴로 돌아갑니다", 'value': "menu"}
        ]
        
        menu = CursorMenu(
            title="다음 단계 선택",
            options=[opt['text'] for opt in menu_options],
            descriptions=[opt['detail'] for opt in menu_options]
        )
        
        choice_index = menu.run()
        if choice_index is not None and 0 <= choice_index < len(menu_options):
            choice = menu_options[choice_index]['value']
        else:
            choice = None
        
        if choice == "reread":
            self.show_section(section_key)
        elif choice == "understood":
            self.mark_completed(section_key)
            print(f"✅ '{section['title']}' 완료!")
            input("계속하려면 Enter를 누르세요...")
        
        return choice
    
    def show_all_guides(self):
        """전체 가이드 순서대로 보기"""
        typewriter_effect("\n🌟 전체 가이드를 시작합니다!")
        typewriter_effect("필요하면 언제든지 건너뛸 수 있어요.")
        
        wait_for_user_input()
        
        # 초급 → 중급 → 고급 순서로 정렬
        ordered_sections = []
        for key, section in self.guide_sections.items():
            if section["difficulty"] == "초급":
                ordered_sections.append((key, section, 1))
            elif section["difficulty"] == "중급":
                ordered_sections.append((key, section, 2))
            else:
                ordered_sections.append((key, section, 3))
        
        ordered_sections.sort(key=lambda x: x[2])
        
        for i, (key, section, _) in enumerate(ordered_sections, 1):
            typewriter_effect(f"\n📍 가이드 {i}/{len(ordered_sections)}: {section['title']}")
            result = self.show_section(key)
            if result == "menu":
                break
    
    def show_quick_start(self):
        """빠른 시작 가이드"""
        quick_sections = ["게임_소개", "Brave_쉽게_이해하기", "첫_전투_가이드", "던전_탐험_기초"]
        
        typewriter_effect("\n⚡ 빠른 시작 가이드")
        typewriter_effect("게임 시작에 꼭 필요한 내용만 보여드릴게요!")
        
        wait_for_user_input()
        
        for i, key in enumerate(quick_sections, 1):
            if key in self.guide_sections:
                section = self.guide_sections[key]
                typewriter_effect(f"\n📍 필수 가이드 {i}/{len(quick_sections)}: {section['title']}")
                result = self.show_section(key)
                if result == "menu":
                    break
        
        typewriter_effect("\n🎉 빠른 시작 가이드 완료!")
        typewriter_effect("이제 게임을 시작할 준비가 되었어요!")
        input("Enter를 눌러 계속하세요...")
    
    def show_faq(self):
        """자주 묻는 질문"""
        faq_data = [
            {
                "question": "❓ 게임이 너무 어려워요!",
                "answer": [
                    "😊 괜찮습니다! 처음엔 모두 어려워해요.",
                    "",
                    "🎯 쉽게 시작하는 방법:",
                    "  • 쉬운 난이도로 시작하기",
                    "  • 추천 파티 구성 사용하기",
                    "  • Brave 공격 위주로 안전하게 플레이",
                    "  • 체력이 낮으면 주저 없이 아이템 사용",
                    "",
                    "💡 기억하세요: 실패해도 다시 시작할 수 있어요!"
                ]
            },
            {
                "question": "❓ 어떤 캐릭터를 선택해야 하나요?",
                "answer": [
                    "🌟 초보자 추천 조합:",
                    "  1. 전사 (앞에서 버티기)",
                    "  2. 검사 (안정적인 딜링)",
                    "  3. 성기사 (회복 담당)",
                    "  4. 마법사 (마법 공격)",
                    "",
                    "💫 고급자 추천:",
                    "  • 자신만의 조합을 실험해보세요!",
                    "  • 각 직업의 특성을 활용한 전략",
                    "  • 상황에 맞는 캐릭터 교체"
                ]
            },
            {
                "question": "❓ Brave 시스템이 헷갈려요!",
                "answer": [
                    "🎯 간단하게 생각해보세요:",
                    "",
                    "1️⃣ Brave 공격 = 데미지 충전",
                    "2️⃣ HP 공격 = 실제 데미지",
                    "",
                    "🔄 기본 패턴:",
                    "  Brave → Brave → HP → 반복",
                    "",
                    "⚡ 중요한 숫자: 300",
                    "  → 300 이상에서 HP 공격하면 효과적!"
                ]
            },
            {
                "question": "❓ 전투에서 계속 져요!",
                "answer": [
                    "💪 승리를 위한 팁:",
                    "",
                    "🛡️ 방어적 플레이:",
                    "  • 체력이 절반 이하면 치유",
                    "  • 확실하지 않으면 방어 선택",
                    "  • 무리하지 말고 안전하게",
                    "",
                    "⚔️ 공격적 플레이:",
                    "  • 상대방을 Break 상태로 만들기",
                    "  • Break 후 HP 공격으로 큰 데미지",
                    "  • 스킬을 적절히 활용"
                ]
            },
            {
                "question": "❓ 게임 조작이 어려워요!",
                "answer": [
                    "🎮 기본 조작법:",
                    "",
                    "🗺️ 이동: WASD 키",
                    "📋 인벤토리: I 키",
                    "👥 파티 상태: P 키",
                    "🔧 필드 활동: F 키",
                    "❓ 도움말: H 키",
                    "",
                    "💡 팁: 모르겠으면 H키를 눌러보세요!",
                    "언제든지 도움말을 볼 수 있어요."
                ]
            }
        ]
        
        print("\n" + "="*60)
        print("❓ 자주 묻는 질문 (FAQ)")
        print("="*60)
        
        for i, faq in enumerate(faq_data, 1):
            typewriter_effect(f"\n{i}. {faq['question']}")
            print("-" * 40)
            
            line_count = 0
            for line in faq['answer']:
                if line.strip() == "":  # 빈 줄은 그냥 출력
                    print()
                else:
                    typewriter_effect(line, delay=0.03)
                
                line_count += 1
                
                # 3줄마다 잠시 멈춤
                if line_count % 3 == 0 and line.strip() != "":
                    time.sleep(0.5)
                    
            wait_for_user_input("📖 다음 질문을 보려면 Enter를 누르세요...")
                
        wait_for_user_input("\n📖 FAQ를 모두 읽으셨으면 Enter를 누르세요...")
    
    def mark_completed(self, section_key: str):
        """섹션 완료 표시"""
        self.current_progress += 1
        # 여기에 진행 상황 저장 로직 추가 가능
    
    def run(self):
        """초보자 가이드 실행"""
        typewriter_effect("\n🌟 Dawn Of Stellar 초보자 가이드를 시작합니다!")
        typewriter_effect("💡 천천히 따라오시면 게임을 쉽게 배울 수 있어요!")
        
        wait_for_user_input()
        
        while True:
            choice = self.show_main_menu()
            
            if choice == "exit":
                typewriter_effect("\n👋 초보자 가이드를 종료합니다. 즐거운 게임 되세요!")
                break
            elif choice == "start_game":
                typewriter_effect("\n🎮 게임을 시작합니다! 화이팅!")
                return "start_game"
            elif choice == "faq":
                self.show_faq()
            elif choice == "show_all":
                self.show_all_guides()
            elif choice == "quick_start":
                self.show_quick_start()
            elif choice in self.guide_sections:
                result = self.show_section(choice)
                if result == "menu":
                    continue
            elif choice is None:
                typewriter_effect("\n👋 초보자 가이드를 종료합니다.")
                break


# 전역 인스턴스
integrated_beginner_guide = IntegratedBeginnerGuide()
