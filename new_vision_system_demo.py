#!/usr/bin/env python3
"""
새로운 시야 시스템 데모 - 기본 시야 축소 + 파티 vision_range 기반
"""

def demo_new_vision_system():
    """새로운 시야 시스템 데모"""
    print("=== 새로운 동적 시야 시스템 ===\n")
    
    # 기본 시야 (축소됨)
    base_vision = 3
    print(f"🔍 기본 시야: {base_vision}칸 (이전 5칸에서 축소)")
    print("   - 시야 증가 아이템 없이는 매우 제한적인 시야")
    print("   - 함정, 적, 아이템을 놓치기 쉬움")
    print("   - 시야 증가 아이템의 중요성 대폭 증가\n")
    
    print("📈 파티 vision_range에 따른 최종 시야:")
    
    # 다양한 파티 구성 시뮬레이션
    party_scenarios = [
        ("시작 파티", 0, "시야 아이템 없음"),
        ("망원경 보유", 1, "기본 망원경 1개"),
        ("정찰 특화", 3, "망원경 + 정찰병 투구 + 창"),
        ("중급 탐험가", 5, "마법 망원경 + 레인저 활 + 정찰 장비"),
        ("고급 탐험가", 8, "독수리의 눈 + 저격 석궁 + 감시탑 왕관"),
        ("전설 탐험가", 12, "드래곤의 시선 + 예언자의 수정구 + 고급 장비"),
        ("최고 구성", 15, "모든 전설급 시야 아이템 보유")
    ]
    
    for party_name, vision_bonus, description in party_scenarios:
        final_vision = base_vision + vision_bonus
        print(f"   {party_name}: +{vision_bonus} → 총 {final_vision}칸")
        print(f"      구성: {description}")
        
        # 시야별 게임플레이 설명
        if final_vision <= 3:
            difficulty = "🔴 매우 어려움"
            gameplay = "함정과 적을 발견하기 매우 어려움"
        elif final_vision <= 5:
            difficulty = "🟡 어려움"
            gameplay = "기본적인 탐색 가능, 여전히 위험"
        elif final_vision <= 7:
            difficulty = "🟢 보통"
            gameplay = "안전한 탐색, 함정 미리 발견"
        elif final_vision <= 10:
            difficulty = "🔵 쉬움"
            gameplay = "넓은 시야로 전략적 이동 가능"
        else:
            difficulty = "🟣 매우 쉬움"
            gameplay = "거의 모든 위험 요소 사전 파악"
            
        print(f"      난이도: {difficulty}")
        print(f"      게임플레이: {gameplay}")
        print()
    
    print("🎯 전략적 변화:")
    print("1. 초반 생존: 망원경이나 시야 증가 무기를 우선 획득")
    print("2. 파티 구성: 시야 증가 아이템을 고려한 장비 선택")
    print("3. 진행 단계별:")
    print("   - Lv.1-5: 망원경, 정찰병 투구로 기본 시야 확보")
    print("   - Lv.6-10: 마법 망원경, 레인저 활로 안전한 탐험")
    print("   - Lv.11-15: 독수리의 눈으로 전략적 우위 확보")
    print("   - Lv.16+: 전설급 아이템으로 완전한 시야 지배")
    print()
    
    print("⚖️ 밸런스 효과:")
    print("• 시야 증가 아이템의 가치 대폭 상승")
    print("• 탐험 난이도 증가로 전략적 사고 필요")
    print("• 아이템 선택의 중요성 증대")
    print("• 파티 구성에 새로운 고려사항 추가")
    print("• 게임 진행에 따른 명확한 성장감 제공")
    print()
    
    print("🎮 플레이어 경험:")
    print("• 초반: 제한된 시야로 긴장감 있는 탐험")
    print("• 중반: 시야 증가로 점진적인 안전감 확보")
    print("• 후반: 넓은 시야로 전략적 게임플레이")
    print("• 엔드게임: 완전한 시야 지배로 마스터급 플레이")

def demo_vision_calculation():
    """시야 계산 예시"""
    print("\n" + "="*50)
    print("=== 시야 계산 시뮬레이션 ===\n")
    
    # 가상의 파티원들과 아이템들
    party_examples = [
        {
            "name": "전사",
            "items": {
                "weapon": {"name": "창", "vision_range": 1},
                "helmet": {"name": "정찰병의 투구", "vision_range": 1}
            }
        },
        {
            "name": "궁수",
            "items": {
                "weapon": {"name": "레인저 활", "vision_range": 2},
                "accessory": {"name": "망원경", "vision_range": 1}
            }
        },
        {
            "name": "마법사",
            "items": {
                "accessory": {"name": "마법 망원경", "vision_range": 2}
            }
        },
        {
            "name": "도적",
            "items": {
                "weapon": {"name": "채찍", "vision_range": 2}
            }
        }
    ]
    
    total_vision_bonus = 0
    print("파티원별 시야 기여도:")
    
    for member in party_examples:
        member_vision = 0
        print(f"\n{member['name']}:")
        
        for slot, item in member['items'].items():
            vision_contribution = item['vision_range']
            member_vision += vision_contribution
            print(f"  - {item['name']} ({slot}): +{vision_contribution}")
        
        print(f"  소계: +{member_vision}")
        total_vision_bonus += member_vision
    
    base_vision = 3
    final_vision = base_vision + total_vision_bonus
    
    print(f"\n📊 최종 계산:")
    print(f"기본 시야: {base_vision}칸")
    print(f"파티 보너스: +{total_vision_bonus}칸")
    print(f"최종 시야: {final_vision}칸")
    print(f"\n결과: 매우 넓은 시야로 안전하고 전략적인 탐험 가능! 🎯")

if __name__ == "__main__":
    demo_new_vision_system()
    demo_vision_calculation()
