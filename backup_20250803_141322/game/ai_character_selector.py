"""
AI 모드용 개선된 캐릭터 선택 시스템
커서 메뉴를 사용한 직관적인 캐릭터 선택
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character

def select_player_characters_with_cursor_menu(party_members: List['Character'], count: int) -> List['Character']:
    """커서 메뉴를 사용한 플레이어 캐릭터 선택"""
    print(f"\n🎮 직접 조작할 캐릭터를 {count}명 선택해주세요!")
    print("="*60)
    
    selected = []
    available = party_members[:]
    
    for i in range(count):
        if not available:
            break
            
        print(f"\n▶️ {i+1}번째 캐릭터 선택 ({i+1}/{count})")
        print("─"*40)
        
        # 캐릭터 선택지 준비
        menu_options = []
        for char in available:
            # HP/MP 비율 계산
            hp_ratio = char.current_hp / char.max_hp if char.max_hp > 0 else 0
            mp_ratio = char.current_mp / char.max_mp if char.max_mp > 0 else 0
            
            # 상태 표시
            status_display = ""
            if hasattr(char, 'status_effects') and char.status_effects:
                status_list = [effect.name for effect in char.status_effects.values()]
                status_display = f" [상태: {', '.join(status_list)}]"
            
            option_text = f"{char.name} (Lv.{char.level} {char.character_class})"
            detail_text = f"💚 HP: {char.current_hp}/{char.max_hp} ({hp_ratio:.0%}) | 💙 MP: {char.current_mp}/{char.max_mp} ({mp_ratio:.0%})\n⚔️ 공격력: {char.physical_attack} | 🛡️ 방어력: {char.physical_defense}{status_display}"
            
            menu_options.append({
                'text': option_text,
                'detail': detail_text,
                'value': char
            })
        
        # 커서 메뉴로 캐릭터 선택
        try:
            from .cursor_menu_system import CursorMenu
            
            menu = CursorMenu(
                title=f"캐릭터 선택 ({i+1}/{count})",
                options=[opt['text'] for opt in menu_options],
                descriptions=[opt['detail'] for opt in menu_options]
            )
            
            choice_index = menu.run()
            if choice_index is not None and 0 <= choice_index < len(menu_options):
                chosen_char = menu_options[choice_index]['value']
                selected.append(chosen_char)
                available.remove(chosen_char)
                print(f"✅ {chosen_char.name}을(를) 선택했습니다!")
            else:
                # 취소한 경우
                if selected:
                    print("⚠️ 이미 선택한 캐릭터가 있어 계속 진행합니다.")
                    break
                else:
                    print("⚠️ 첫 번째 캐릭터를 자동으로 선택합니다.")
                    selected.append(available[0])
                    available.remove(available[0])
                    
        except ImportError:
            # 커서 메뉴를 사용할 수 없는 경우 기존 방식 사용
            print("커서 메뉴를 사용할 수 없어 텍스트 입력 방식으로 진행합니다.")
            
            for j, char in enumerate(available, 1):
                hp_ratio = int((char.current_hp / char.max_hp) * 100) if char.max_hp > 0 else 0
                mp_ratio = int((char.current_mp / char.max_mp) * 100) if char.max_mp > 0 else 0
                print(f"{j}. {char.name} (Lv.{char.level}, {char.character_class})")
                print(f"   HP: {hp_ratio}% | MP: {mp_ratio}% | 공격: {char.physical_attack} | 방어: {char.physical_defense}")
            
            try:
                choice_input = input(f"캐릭터 번호를 입력하세요 (1-{len(available)}): ").strip()
                choice_idx = int(choice_input) - 1
                
                if 0 <= choice_idx < len(available):
                    selected_char = available[choice_idx]
                    selected.append(selected_char)
                    available.remove(selected_char)
                    print(f"✅ {selected_char.name}을(를) 선택했습니다!")
                else:
                    print("⚠️ 첫 번째 캐릭터를 자동으로 선택합니다.")
                    selected.append(available[0])
                    available.remove(available[0])
            except (ValueError, IndexError):
                print("⚠️ 첫 번째 캐릭터를 자동으로 선택합니다.")
                selected.append(available[0])
                available.remove(available[0])
    
    # 선택이 부족한 경우 자동으로 첫 번째 캐릭터들 선택
    while len(selected) < count and party_members:
        for char in party_members:
            if char not in selected:
                selected.append(char)
                print(f"🤖 {char.name}이(가) 자동으로 선택되었습니다.")
                break
        if len(selected) >= count:
            break
    
    print(f"\n🎉 선택 완료! 플레이어가 조작할 캐릭터:")
    for i, char in enumerate(selected, 1):
        print(f"  {i}. {char.name} ({char.character_class})")
    
    input("계속하려면 Enter를 누르세요...")
    return selected
