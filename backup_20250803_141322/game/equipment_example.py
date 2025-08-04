#!/usr/bin/env python3
"""
장비 자동 장착 시스템 사용 예제
기본 게임모드에서 28개 직업 모두 지원
"""

# 사용 예제 코드

def example_basic_mode_auto_equip():
    """기본 게임모드 자동 장착 사용 예제"""
    
    # 1. 간단한 자동 장착 (한 명)
    from game.equipment_helpers import quick_auto_equip
    
    # character: 캐릭터 객체, inventory_items: 인벤토리 아이템 리스트
    # success = quick_auto_equip(character, inventory_items)
    
    # 2. 파티 전체 자동 장착  
    from game.equipment_helpers import auto_equip_party
    
    # party: 파티 멤버 리스트, inventory_items: 인벤토리 아이템 리스트
    # results = auto_equip_party(party, inventory_items)
    
    # 3. 메뉴 방식 자동 장착
    from game.basic_mode_equipment import show_basic_mode_equipment_menu
    
    # character: 캐릭터 객체, inventory_items: 인벤토리 아이템 리스트  
    # show_basic_mode_equipment_menu(character, inventory_items)
    
    # 4. 파티 장비 분석 리포트
    from game.equipment_helpers import show_equipment_analysis_report
    
    # party: 파티 멤버 리스트, inventory_items: 인벤토리 아이템 리스트
    # show_equipment_analysis_report(party, inventory_items)
    
    # 5. 확인 후 일괄 자동 장착
    from game.equipment_helpers import batch_auto_equip_with_confirmation
    
    # party: 파티 멤버 리스트, inventory_items: 인벤토리 아이템 리스트
    # success = batch_auto_equip_with_confirmation(party, inventory_items)
    
    print("🎯 장비 자동 장착 시스템 사용 가능!")
    print("📝 지원 직업 (28개):")
    
    supported_classes = [
        # 근접 전투 직업 (10개)
        "전사", "기사", "성기사", "암흑기사", "용기사", 
        "검성", "사무라이", "검투사", "광전사", "몽크",
        
        # 원거리 전투 직업 (4개)  
        "궁수", "도적", "암살자", "해적",
        
        # 마법 직업 (6개)
        "아크메이지", "네크로맨서", "정령술사", 
        "시간술사", "차원술사", "연금술사",
        
        # 하이브리드 직업 (2개)
        "마검사", "기계공학자",
        
        # 지원 직업 (6개)
        "바드", "신관", "클레릭", "드루이드", "무당", "철학자"
    ]
    
    print("   근접 전투:", ", ".join(supported_classes[:10]))
    print("   원거리:", ", ".join(supported_classes[10:14])) 
    print("   마법:", ", ".join(supported_classes[14:20]))
    print("   하이브리드:", ", ".join(supported_classes[20:22]))
    print("   지원:", ", ".join(supported_classes[22:28]))
    
    print(f"\n총 {len(supported_classes)}개 직업 완전 지원! ✅")

if __name__ == "__main__":
    example_basic_mode_auto_equip()
