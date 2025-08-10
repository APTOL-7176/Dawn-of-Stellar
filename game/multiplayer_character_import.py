"""
멀티플레이어 캐릭터 임포트 시스템
각 플레이어가 자신의 캐릭터를 가져와서 파티 구성
"""

import json
import os
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from .character import Character
from .character_presets import CharacterPresets
from .save_system import SaveSystem
from .items import Item, ItemDatabase
from .cursor_menu_system import CursorMenu
from .color_text import GREEN, YELLOW, RED, CYAN, WHITE, RESET


class MultiplayerCharacterImport:
    """멀티플레이어용 캐릭터 임포트 시스템"""
    
    def __init__(self):
        self.preset_manager = CharacterPresets()
        self.save_system = SaveSystem()
        self.warehouse_file = "player_warehouse.json"
        self.version = "4.0.0"  # 멀티플레이어 버전
        
    def load_warehouse_data(self) -> Dict[str, Any]:
        """창고 데이터 로드"""
        try:
            if os.path.exists(self.warehouse_file):
                with open(self.warehouse_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "items": [],
                    "gold": 0,
                    "version": self.version,
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"⚠️ 창고 데이터 로드 실패: {e}")
            return {"items": [], "gold": 0, "version": self.version}
    
    def save_warehouse_data(self, warehouse_data: Dict[str, Any]) -> bool:
        """창고 데이터 저장"""
        try:
            warehouse_data["last_updated"] = datetime.now().isoformat()
            warehouse_data["version"] = self.version
            with open(self.warehouse_file, 'w', encoding='utf-8') as f:
                json.dump(warehouse_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ 창고 데이터 저장 실패: {e}")
            return False
    
    def get_saved_games_with_characters(self) -> List[Dict[str, Any]]:
        """저장된 게임 파일에서 캐릭터 정보 추출"""
        saved_games = []
        save_dir = "saves"
        
        if not os.path.exists(save_dir):
            return saved_games
        
        for filename in os.listdir(save_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(save_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    # 파티 정보 추출
                    if 'party' in save_data and save_data['party']:
                        game_info = {
                            "filename": filename,
                            "filepath": filepath,
                            "save_name": save_data.get('save_name', filename[:-5]),
                            "party_size": len(save_data['party']),
                            "characters": [],
                            "dungeon_level": save_data.get('current_level', 1),
                            "total_gold": save_data.get('gold', 0),
                            "save_date": save_data.get('save_date', 'Unknown'),
                            "game_version": save_data.get('version', 'Unknown')
                        }
                        
                        # 각 캐릭터 정보 추출
                        for char_data in save_data['party']:
                            char_info = {
                                "name": char_data.get('name', 'Unknown'),
                                "class": char_data.get('character_class', 'Unknown'),
                                "level": char_data.get('level', 1),
                                "hp": char_data.get('current_hp', 0),
                                "max_hp": char_data.get('max_hp', 0),
                                "mp": char_data.get('current_mp', 0),
                                "max_mp": char_data.get('max_mp', 0),
                                "experience": char_data.get('experience', 0),
                                "equipment_count": len(char_data.get('equipment', {})),
                                "traits": char_data.get('passive_traits', [])
                            }
                            game_info["characters"].append(char_info)
                        
                        saved_games.append(game_info)
                
                except Exception as e:
                    print(f"⚠️ 게임 파일 {filename} 분석 실패: {e}")
                    continue
        
        # 저장 날짜 순으로 정렬 (최신순)
        saved_games.sort(key=lambda x: x.get('save_date', ''), reverse=True)
        return saved_games
    
    def select_character_from_saves(self, player_name: str) -> Optional[Tuple[Character, List[Item], int]]:
        """저장된 게임에서 캐릭터 선택 (캐릭터, 아이템, 골드 반환)"""
        print(f"\n{CYAN}🎮 {player_name}님의 캐릭터 선택{RESET}")
        print(f"{YELLOW}저장된 게임 파일에서 캐릭터를 선택하세요{RESET}")
        
        saved_games = self.get_saved_games_with_characters()
        
        if not saved_games:
            print(f"{RED}저장된 게임 파일이 없습니다.{RESET}")
            return None
        
        # 게임 파일 선택
        game_options = []
        game_descriptions = []
        
        for game in saved_games:
            option = f"📁 {game['save_name']} (Lv.{game['dungeon_level']}, {game['party_size']}명)"
            description = f"저장일: {game['save_date'][:10]} | 골드: {game['total_gold']}"
            game_options.append(option)
            game_descriptions.append(description)
        
        game_options.append("❌ 취소")
        game_descriptions.append("캐릭터 선택을 취소합니다")
        
        game_menu = CursorMenu("📂 게임 파일 선택", game_options, game_descriptions, cancellable=True)
        game_result = game_menu.run()
        
        if game_result is None or game_result == len(saved_games):
            return None
        
        selected_game = saved_games[game_result]
        
        # 캐릭터 선택
        char_options = []
        char_descriptions = []
        
        for i, char in enumerate(selected_game['characters']):
            option = f"⚔️ {char['name']} ({char['class']} Lv.{char['level']})"
            description = f"HP: {char['hp']}/{char['max_hp']} | MP: {char['mp']}/{char['max_mp']} | 장비: {char['equipment_count']}개"
            char_options.append(option)
            char_descriptions.append(description)
        
        char_options.append("❌ 다른 게임 파일 선택")
        char_descriptions.append("다른 게임 파일에서 캐릭터를 선택합니다")
        
        char_menu = CursorMenu(f"👤 {selected_game['save_name']}에서 캐릭터 선택", char_options, char_descriptions, cancellable=True)
        char_result = char_menu.run()
        
        if char_result is None or char_result == len(selected_game['characters']):
            return self.select_character_from_saves(player_name)  # 재귀 호출
        
        # 선택된 캐릭터 로드
        try:
            with open(selected_game['filepath'], 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            selected_char_data = save_data['party'][char_result]
            
            # Character 객체 생성
            character = Character(
                selected_char_data.get('character_class', 'warrior'),
                selected_char_data.get('name', 'Unknown')
            )
            
            # 캐릭터 데이터 복원
            self._restore_character_data(character, selected_char_data)
            
            # 인벤토리에서 아이템 추출
            inventory_items = []
            if 'inventory' in save_data and save_data['inventory']:
                for item_data in save_data['inventory']:
                    try:
                        item = ItemDatabase.get_item(item_data['name'])
                        if item:
                            inventory_items.append(item)
                    except Exception as e:
                        print(f"⚠️ 아이템 {item_data.get('name', 'Unknown')} 로드 실패: {e}")
            
            # 골드 정보
            character_gold = save_data.get('gold', 0) // len(selected_game['characters'])  # 파티원 수로 나눔
            
            print(f"{GREEN}✅ {character.name} ({character.character_class}) 선택 완료!{RESET}")
            print(f"   레벨: {character.level} | 아이템: {len(inventory_items)}개 | 골드: {character_gold}")
            
            return character, inventory_items, character_gold
            
        except Exception as e:
            print(f"{RED}캐릭터 로드 실패: {e}{RESET}")
            return None
    
    def _restore_character_data(self, character: Character, char_data: Dict[str, Any]):
        """캐릭터 데이터 복원"""
        # 기본 정보
        character.level = char_data.get('level', 1)
        character.experience = char_data.get('experience', 0)
        
        # 체력/마나
        character.current_hp = char_data.get('current_hp', character.max_hp)
        character.current_mp = char_data.get('current_mp', character.max_mp)
        character.max_hp = char_data.get('max_hp', character.max_hp)
        character.max_mp = char_data.get('max_mp', character.max_mp)
        
        # 스탯
        character.physical_attack = char_data.get('physical_attack', character.physical_attack)
        character.magic_attack = char_data.get('magic_attack', character.magic_attack)
        character.physical_defense = char_data.get('physical_defense', character.physical_defense)
        character.magic_defense = char_data.get('magic_defense', character.magic_defense)
        character.speed = char_data.get('speed', character.speed)
        
        # 전투 관련
        character.brave_points = char_data.get('brave_points', 1000)
        character.wounds = char_data.get('wounds', 0)
        character.atb_gauge = char_data.get('atb_gauge', 0)
        
        # 특성 복원
        if 'passive_traits' in char_data and char_data['passive_traits']:
            try:
                # 특성 이름으로 매칭해서 복원
                restored_traits = []
                for trait_name in char_data['passive_traits']:
                    for trait in character.available_traits:
                        if hasattr(trait, 'name') and trait.name == trait_name:
                            restored_traits.append(trait)
                            break
                character.passive_traits = restored_traits
            except Exception as e:
                print(f"⚠️ 특성 복원 실패: {e}")
        
        # 장비 복원 (기본 정보만)
        if 'equipment' in char_data and char_data['equipment']:
            try:
                for slot, item_data in char_data['equipment'].items():
                    if item_data:
                        item = ItemDatabase.get_item(item_data['name'])
                        if item and hasattr(character, 'equipment'):
                            character.equipment[slot] = item
            except Exception as e:
                print(f"⚠️ 장비 복원 실패: {e}")
    
    def select_character_from_presets(self, player_name: str) -> Optional[Character]:
        """프리셋에서 캐릭터 선택"""
        print(f"\n{CYAN}🎭 {player_name}님의 프리셋 캐릭터 선택{RESET}")
        
        # 개별 캐릭터 프리셋 목록
        char_presets = self.preset_manager.list_character_presets()
        
        if not char_presets:
            print(f"{YELLOW}저장된 캐릭터 프리셋이 없습니다.{RESET}")
            return None
        
        options = []
        descriptions = []
        
        for preset in char_presets:
            option = f"🎭 {preset['name']}"
            description = preset.get('description', '프리셋 캐릭터')
            if preset.get('created_at'):
                description += f" (생성: {preset['created_at'][:10]})"
            options.append(option)
            descriptions.append(description)
        
        options.append("❌ 취소")
        descriptions.append("프리셋 선택을 취소합니다")
        
        menu = CursorMenu("🎭 프리셋 캐릭터 선택", options, descriptions, cancellable=True)
        result = menu.run()
        
        if result is None or result == len(char_presets):
            return None
        
        # 선택된 프리셋 로드
        selected_preset = char_presets[result]
        character = self.preset_manager.load_character_preset(selected_preset['name'])
        
        if character:
            print(f"{GREEN}✅ 프리셋 캐릭터 '{character.name}' 선택 완료!{RESET}")
            return character
        else:
            print(f"{RED}프리셋 로드 실패{RESET}")
            return None
    
    def select_warehouse_items(self, player_name: str, max_items: int = 10) -> Tuple[List[Item], int]:
        """창고에서 아이템 선택"""
        print(f"\n{CYAN}📦 {player_name}님의 창고 아이템 선택{RESET}")
        print(f"{YELLOW}최대 {max_items}개의 아이템을 선택할 수 있습니다{RESET}")
        
        warehouse_data = self.load_warehouse_data()
        available_items = warehouse_data.get('items', [])
        available_gold = warehouse_data.get('gold', 0)
        
        if not available_items and available_gold == 0:
            print(f"{YELLOW}창고가 비어있습니다.{RESET}")
            return [], 0
        
        selected_items = []
        selected_gold = 0
        
        # 골드 선택
        if available_gold > 0:
            print(f"\n{YELLOW}💰 보유 골드: {available_gold}{RESET}")
            while True:
                try:
                    take_gold = input(f"{GREEN}가져갈 골드 (0-{available_gold}): {RESET}").strip()
                    if take_gold == "":
                        take_gold = 0
                    else:
                        take_gold = int(take_gold)
                    
                    if 0 <= take_gold <= available_gold:
                        selected_gold = take_gold
                        break
                    else:
                        print(f"{RED}0부터 {available_gold} 사이의 값을 입력하세요.{RESET}")
                except ValueError:
                    print(f"{RED}숫자를 입력하세요.{RESET}")
        
        # 아이템 선택
        if available_items:
            print(f"\n{CYAN}📦 창고 아이템 목록{RESET}")
            
            while len(selected_items) < max_items and available_items:
                options = []
                descriptions = []
                
                for i, item_data in enumerate(available_items):
                    option = f"📦 {item_data['name']} ({item_data.get('type', 'item')})"
                    description = item_data.get('description', '창고 아이템')
                    options.append(option)
                    descriptions.append(description)
                
                options.append("✅ 선택 완료")
                descriptions.append(f"현재 선택: {len(selected_items)}개")
                
                menu = CursorMenu(f"아이템 선택 ({len(selected_items)}/{max_items})", options, descriptions, cancellable=True)
                result = menu.run()
                
                if result is None or result == len(available_items):
                    break
                
                # 선택된 아이템 처리
                selected_item_data = available_items.pop(result)
                try:
                    item = ItemDatabase.get_item(selected_item_data['name'])
                    if item:
                        selected_items.append(item)
                        print(f"{GREEN}✅ {item.name} 선택됨{RESET}")
                except Exception as e:
                    print(f"{RED}아이템 로드 실패: {e}{RESET}")
        
        print(f"\n{GREEN}창고에서 선택 완료: 아이템 {len(selected_items)}개, 골드 {selected_gold}{RESET}")
        return selected_items, selected_gold
    
    def get_multiplayer_party_setup(self, player_names: List[str]) -> Optional[List[Dict[str, Any]]]:
        """멀티플레이어 파티 설정"""
        print(f"\n{CYAN}🎮 멀티플레이어 파티 설정{RESET}")
        print(f"{WHITE}총 {len(player_names)}명의 플레이어가 각자 캐릭터를 선택합니다{RESET}")
        
        party_setup = []
        
        for i, player_name in enumerate(player_names):
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{WHITE}👤 {i+1}/{len(player_names)}: {player_name}님 차례{RESET}")
            print(f"{CYAN}{'='*60}{RESET}")
            
            # 캐릭터 선택 방법
            options = [
                "💾 저장된 게임에서 캐릭터 선택",
                "🎭 프리셋 캐릭터 선택",
                "❌ 건너뛰기 (AI로 대체)"
            ]
            
            descriptions = [
                "저장된 게임 파일에서 캐릭터와 아이템을 가져옵니다",
                "미리 생성한 프리셋 캐릭터를 선택합니다", 
                "이 슬롯을 AI가 조작하도록 설정합니다"
            ]
            
            menu = CursorMenu(f"👤 {player_name}님의 캐릭터 선택 방법", options, descriptions, cancellable=False)
            choice = menu.run()
            
            player_data = {
                "player_name": player_name,
                "character": None,
                "items": [],
                "gold": 0,
                "is_ai": False
            }
            
            if choice == 0:  # 저장된 게임에서 선택
                result = self.select_character_from_saves(player_name)
                if result:
                    character, items, gold = result
                    player_data["character"] = character
                    player_data["items"] = items
                    player_data["gold"] = gold
                    
                    # 창고 아이템도 추가로 선택 가능
                    if input(f"{GREEN}창고에서 추가 아이템을 가져오시겠습니까? (y/N): {RESET}").strip().lower() == 'y':
                        warehouse_items, warehouse_gold = self.select_warehouse_items(player_name, 5)
                        player_data["items"].extend(warehouse_items)
                        player_data["gold"] += warehouse_gold
                
            elif choice == 1:  # 프리셋에서 선택
                character = self.select_character_from_presets(player_name)
                if character:
                    player_data["character"] = character
                    
                    # 창고 아이템 선택
                    warehouse_items, warehouse_gold = self.select_warehouse_items(player_name, 10)
                    player_data["items"] = warehouse_items
                    player_data["gold"] = warehouse_gold
                
            elif choice == 2:  # AI로 대체
                player_data["is_ai"] = True
                print(f"{YELLOW}⚙️ {player_name} 슬롯이 AI로 설정됩니다{RESET}")
            
            # 캐릭터가 없으면 기본 캐릭터 생성 또는 AI 설정
            if not player_data["character"] and not player_data["is_ai"]:
                print(f"{YELLOW}캐릭터 선택이 취소되었습니다. AI로 대체합니다.{RESET}")
                player_data["is_ai"] = True
            
            party_setup.append(player_data)
        
        # 최종 확인
        print(f"\n{CYAN}🎉 파티 설정 완료!{RESET}")
        for i, player_data in enumerate(party_setup):
            if player_data["is_ai"]:
                print(f"{i+1}. {player_data['player_name']}: {YELLOW}AI 플레이어{RESET}")
            else:
                char = player_data["character"]
                print(f"{i+1}. {player_data['player_name']}: {GREEN}{char.name} ({char.character_class} Lv.{char.level}){RESET}")
                print(f"    아이템: {len(player_data['items'])}개, 골드: {player_data['gold']}")
        
        if input(f"\n{GREEN}이 설정으로 게임을 시작하시겠습니까? (Y/n): {RESET}").strip().lower() != 'n':
            return party_setup
        else:
            return None


def get_multiplayer_character_import():
    """멀티플레이어 캐릭터 임포트 시스템 인스턴스 반환"""
    return MultiplayerCharacterImport()
