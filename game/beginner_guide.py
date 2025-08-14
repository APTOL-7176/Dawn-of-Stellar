"""
초보자를 위한 친화적인 가이드 시스템
Dawn Of Stellar 입문자를 위한 단계별 안내
"""

from typing import Dict, List, Optional
from game.cursor_menu_system import CursorMenu
from game.ascii_effects import play_ascii_sound


class BeginnerGuide:
    """초보자 가이드 시스템"""
    
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
                "estimated_time": "2분"
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
                    "✨ 팁: 처음엔 300 이상 모으고 HP 공격해보세요!"
                ],
                "difficulty": "초급",
                "estimated_time": "3분"
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
                    "💪 자신감을 가지세요! 연습하면 늘어요!"
                ],
                "difficulty": "초급", 
                "estimated_time": "5분"
            },
            
            "캐릭터_고르기_도움": {
                "title": "👥 어떤 캐릭터를 골라야 할까요?",
                "description": "초보자를 위한 캐릭터 선택 가이드",
                "content": [
                    "🤔 20명 중에 어떻게 고르죠?",
                    "  → 걱정 마세요! 좋은 조합을 알려드릴게요",
                    "",
                    "🌟 초보자 추천 파티 구성:",
                    "  1. 전사 (탱크) - 체력이 많아서 안전",
                    "  2. 검사 (딜러) - 균형 잡힌 공격수",
                    "  3. 성기사 (힐러) - 회복 담당",
                    "  4. 마법사 (마법딜러) - 다양한 공격",
                    "",
                    "✨ 각 역할 설명:",
                    "  • 탱크: 적의 공격을 버텨주는 든든한 방패",
                    "  • 딜러: 적을 빠르게 처치하는 공격수",
                    "  • 힐러: 동료를 치유하는 생명의 은인",
                    "  • 마법딜러: 특별한 마법으로 상황 해결사",
                    "",
                    "💡 나중에 다른 캐릭터도 사용해보세요!",
                    "   게임을 여러 번 플레이하면서 취향을 찾아가세요!"
                ],
                "difficulty": "초급",
                "estimated_time": "3분"
            },
            
            "던전_탐험_기초": {
                "title": "🗺️ 던전 탐험, 이것만 알면 OK!",
                "description": "맵을 돌아다니는 기본 방법",
                "content": [
                    "🚶‍♂️ 던전에서 움직이기:",
                    "  • 화살표 키나 WASD로 이동",
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
                    "  • C: 캐릭터 정보",
                    "  • ESC: 메뉴"
                ],
                "difficulty": "초급",
                "estimated_time": "4분"
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
                    "  • 액티브 특성은 직접 사용 가능"
                ],
                "difficulty": "중급",
                "estimated_time": "5분"
            }
        }
    
    def show_main_menu(self) -> Optional[str]:
        """초보자 가이드 메인 메뉴"""
        print("\n" + "="*60)
        print("🔰 초보자 가이드 - Dawn Of Stellar 입문서")
        print("="*60)
        
        menu_options = []
        for key, section in self.guide_sections.items():
            difficulty_icon = "🔰" if section["difficulty"] == "초급" else "⭐" if section["difficulty"] == "중급" else "🏆"
            option_text = f"{difficulty_icon} {section['title']}"
            detail_text = f"{section['description']}\n예상 시간: {section['estimated_time']} | 난이도: {section['difficulty']}"
            
            menu_options.append({
                'text': option_text,
                'detail': detail_text,
                'value': key
            })
        
        # 추가 옵션들
        menu_options.extend([
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
        
        for line in section['content']:
            print(line)
            
        print("\n" + "-"*60)
        
        # 진행 옵션
        menu_options = [
            {
                'text': "✅ 이해했습니다",
                'detail': "다음 단계로 진행합니다",
                'value': "understood"
            },
            {
                'text': "🔄 다시 읽기",
                'detail': "이 가이드를 다시 봅니다",
                'value': "reread"
            },
            {
                'text': "🏠 가이드 메뉴로",
                'detail': "가이드 메인 메뉴로 돌아갑니다",
                'value': "menu"
            }
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
            }
        ]
        
        print("\n" + "="*60)
        print("❓ 자주 묻는 질문 (FAQ)")
        print("="*60)
        
        for i, faq in enumerate(faq_data, 1):
            print(f"\n{i}. {faq['question']}")
            print("-" * 40)
            for line in faq['answer']:
                print(line)
                
        input("\n📖 FAQ를 모두 읽으셨으면 Enter를 누르세요...")
    
    def mark_completed(self, section_key: str):
        """섹션 완료 표시"""
        self.current_progress += 1
        # 여기에 진행 상황 저장 로직 추가 가능
    
    def run(self):
        """초보자 가이드 실행"""
        print("\n🌟 Dawn Of Stellar 초보자 가이드를 시작합니다!")
        print("💡 천천히 따라오시면 게임을 쉽게 배울 수 있어요!")
        
        while True:
            choice = self.show_main_menu()
            
            if choice == "exit":
                print("\n👋 초보자 가이드를 종료합니다. 즐거운 게임 되세요!")
                break
            elif choice == "start_game":
                print("\n🎮 게임을 시작합니다! 화이팅!")
                return "start_game"
            elif choice == "faq":
                self.show_faq()
            elif choice in self.guide_sections:
                result = self.show_section(choice)
                if result == "menu":
                    continue
            elif choice is None:
                print("\n👋 초보자 가이드를 종료합니다.")
                break


# 전역 인스턴스
beginner_guide = BeginnerGuide()
