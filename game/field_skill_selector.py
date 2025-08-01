#!/usr/bin/env python3
"""
필드 스킬 사용자 선택 시스템
파티 멤버 중 누가 필드 스킬을 사용할지 선택할 수 있게 함
"""

from typing import List, Dict, Optional, Any
from .character import Character, PartyManager

class FieldSkillSelector:
    """필드 스킬 사용자 선택기"""
    
    def __init__(self, sound_system=None):
        self.sound_system = sound_system
        
        # 필드 스킬 정의
        self.field_skills = {
            "heal": {
                "name": "🍃 파티 치유",
                "description": "파티 전체를 회복시킵니다",
                "mp_cost": 15,  # 8 -> 15로 증가
                "cooldown": 5,
                "required_class": ["성직자", "마법사", "드루이드", "클레릭", "대마법사", "성기사", "정령술사"],
                "effect_type": "healing"
            },
            "teleport": {
                "name": "🌀 공간 도약",
                "description": "벽이나 함정을 뛰어넘어 이동합니다",
                "mp_cost": 20,  # 25 -> 20으로 감소
                "cooldown": 6,
                "required_class": ["마법사", "정령술사", "소서러", "워록", "대마법사"],
                "effect_type": "movement"
            },
            "detect_items": {
                "name": "🔍 아이템 탐지",
                "description": "주변의 숨겨진 아이템을 찾습니다",
                "mp_cost": 10,  # 5 -> 10으로 증가
                "cooldown": 3,
                "required_class": ["도적", "스카웃", "레인저", "궁수", "암살자"],
                "effect_type": "detection"
            },
            "detect_enemies": {
                "name": "👁️ 적 탐지",
                "description": "주변의 적을 탐지합니다",
                "mp_cost": 12,  # 6 -> 12로 증가
                "cooldown": 4,
                "required_class": ["레인저", "스카웃", "궁수", "사냥꾼", "암살자"],
                "effect_type": "detection"
            },
            "escape": {
                "name": "💨 탈출",
                "description": "안전한 장소로 이동합니다",
                "mp_cost": 25,
                "cooldown": 10,
                "required_class": ["도적", "암살자", "닌자", "스카웃"],
                "effect_type": "movement"
            },
            "illuminate": {
                "name": "💡 조명",
                "description": "어둠을 밝혀 시야를 넓힙니다",
                "mp_cost": 12,  # 15 -> 12로 감소
                "cooldown": 2,
                "required_class": ["성직자", "마법사", "클레릭", "대마법사", "성기사"],
                "effect_type": "utility"
            },
            "purify": {
                "name": "✨ 정화",
                "description": "파티의 상태이상을 제거합니다",
                "mp_cost": 25,  # 30 -> 25로 감소
                "cooldown": 6,
                "required_class": ["성직자", "드루이드", "클레릭", "성기사"],
                "effect_type": "cleansing"
            },
            "haste": {
                "name": "⚡ 시간 조작",
                "description": "주변 적들의 시간을 늦춰 상대적으로 빨라집니다",
                "mp_cost": 28,  # 35 -> 28로 감소
                "cooldown": 8,
                "required_class": ["마법사", "정령술사", "바드", "대마법사"],
                "effect_type": "enhancement"
            }
        }
        
        # 최근 사용 기록
        self.last_used = {}
        
    def get_available_skills(self, party: PartyManager) -> List[str]:
        """파티에서 사용 가능한 필드 스킬 목록 반환"""
        available_skills = []
        
        for skill_id, skill_info in self.field_skills.items():
            # 쿨다운 확인
            if self._is_on_cooldown(skill_id):
                continue
                
            # 사용 가능한 멤버가 있는지 확인
            capable_members = self.get_capable_members(party, skill_id)
            if capable_members:
                available_skills.append(skill_id)
                
        return available_skills
    
    def get_capable_members(self, party: PartyManager, skill_id: str) -> List[Character]:
        """특정 필드 스킬을 사용할 수 있는 파티 멤버들 반환"""
        if skill_id not in self.field_skills:
            return []
            
        skill_info = self.field_skills[skill_id]
        required_classes = skill_info["required_class"]
        mp_cost = skill_info["mp_cost"]
        
        capable_members = []
        
        for member in party.get_alive_members():
            # 클래스 조건 확인
            if member.character_class in required_classes:
                # MP 조건 확인
                if member.current_mp >= mp_cost:
                    capable_members.append(member)
        
        return capable_members
    
    def select_skill_user(self, party: PartyManager, skill_id: str) -> Optional[Character]:
        """필드 스킬 사용자 선택 인터페이스 - 커서 방식"""
        if skill_id not in self.field_skills:
            print(f"❌ 알 수 없는 스킬: {skill_id}")
            return None
            
        capable_members = self.get_capable_members(party, skill_id)
        
        if not capable_members:
            skill_info = self.field_skills[skill_id]
            print(f"❌ {skill_info['name']} 스킬을 사용할 수 있는 멤버가 없습니다.")
            print(f"   필요 직업: {', '.join(skill_info['required_class'])}")
            print(f"   필요 MP: {skill_info['mp_cost']}")
            return None
        
        if len(capable_members) == 1:
            # 사용 가능한 멤버가 1명뿐이면 자동 선택
            return capable_members[0]
        
        skill_info = self.field_skills[skill_id]
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            # 커서 메뉴로 사용자 선택
            options = []
            descriptions = []
            
            for member in capable_members:
                mp_status = f"{member.current_mp}/{member.max_mp}"
                hp_status = f"{member.current_hp}/{member.max_hp}"
                
                options.append(f"👤 {member.name} ({member.character_class})")
                
                desc = f"HP: {hp_status} | MP: {mp_status}"
                # 특별한 상태 표시
                if hasattr(member, 'status_manager'):
                    active_effects = member.status_manager.get_active_effects()
                    if active_effects:
                        desc += f" | 상태: {', '.join(active_effects)}"
                        
                descriptions.append(desc)
            
            options.append("❌ 취소")
            descriptions.append("스킬 사용을 취소합니다")
            
            menu_title = f"🎯 {skill_info['name']} 사용자 선택"
            menu = create_simple_menu(menu_title, options, descriptions)
            
            # 스킬 정보를 상단에 표시
            print(f"\n📝 {skill_info['description']}")
            print(f"💙 MP 소모: {skill_info['mp_cost']}")
            print("─" * 50)
            
            result = menu.run()
            
            if result == -1 or result >= len(capable_members):  # 취소
                return None
            else:
                selected_member = capable_members[result]
                
                # 효과음 재생
                if self.sound_system:
                    self.sound_system.play_sfx("menu_confirm")
                
                print(f"✅ {selected_member.name}이(가) {skill_info['name']} 스킬을 사용합니다!")
                return selected_member
                
        except ImportError:
            # 폴백: 기존 텍스트 메뉴
            return self._select_skill_user_fallback(capable_members, skill_info)
    
    def _select_skill_user_fallback(self, capable_members: List[Character], skill_info: Dict) -> Optional[Character]:
        """필드 스킬 사용자 선택 폴백 (기존 방식)"""
        print(f"\n🎯 {skill_info['name']} 스킬 사용자 선택")
        print(f"📝 {skill_info['description']}")
        print(f"💙 MP 소모: {skill_info['mp_cost']}")
        print("─" * 50)
        
        for i, member in enumerate(capable_members, 1):
            mp_status = f"{member.current_mp}/{member.max_mp}"
            hp_status = f"{member.current_hp}/{member.max_hp}"
            print(f"{i}. {member.name} ({member.character_class})")
            print(f"   HP: {hp_status} | MP: {mp_status}")
            
            # 특별한 상태 표시
            if hasattr(member, 'status_manager'):
                active_effects = member.status_manager.get_active_effects()
                if active_effects:
                    print(f"   상태: {', '.join(active_effects)}")
        
        print("0. 취소")
        
        while True:
            try:
                choice = input("\n사용자를 선택하세요: ").strip()
                
                if choice == "0":
                    return None
                    
                choice_num = int(choice)
                if 1 <= choice_num <= len(capable_members):
                    selected_member = capable_members[choice_num - 1]
                    
                    # 효과음 재생
                    if self.sound_system:
                        self.sound_system.play_sfx("menu_confirm")
                    
                    print(f"✅ {selected_member.name}이(가) {skill_info['name']} 스킬을 사용합니다!")
                    return selected_member
                else:
                    print("❌ 잘못된 선택입니다.")
                    
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
            except KeyboardInterrupt:
                print("\n❌ 취소되었습니다.")
                return None
    
    def use_field_skill(self, party: PartyManager, skill_id: str, world=None, target_pos=None) -> Dict[str, Any]:
        """필드 스킬 사용 실행"""
        # 사용자 선택
        user = self.select_skill_user(party, skill_id)
        if not user:
            return {"success": False, "message": "스킬 사용이 취소되었습니다."}
        
        skill_info = self.field_skills[skill_id]
        
        # MP 소모
        user.current_mp -= skill_info["mp_cost"]
        
        # 쿨다운 설정
        self.last_used[skill_id] = 0  # 턴 카운터와 연동 필요
        
        # 스킬 효과 실행
        result = self._execute_skill_effect(skill_id, user, party, world, target_pos)
        
        # 효과음 재생
        if self.sound_system:
            effect_sounds = {
                "healing": "heal",
                "movement": "teleport",
                "detection": "magic_cast",
                "utility": "magic_cast",
                "cleansing": "cure2",
                "enhancement": "haste"
            }
            sound_name = effect_sounds.get(skill_info["effect_type"], "magic_cast")
            self.sound_system.play_sfx(sound_name)
        
        return result
    
    def _execute_skill_effect(self, skill_id: str, user: Character, party: PartyManager, 
                            world=None, target_pos=None) -> Dict[str, Any]:
        """필드 스킬 효과 실행"""
        skill_info = self.field_skills[skill_id]
        
        if skill_id == "heal":
            return self._execute_heal(user, party)
        elif skill_id == "teleport":
            return self._execute_teleport(user, world, target_pos)
        elif skill_id == "detect_items":
            return self._execute_detect_items(user, world)
        elif skill_id == "detect_enemies":
            return self._execute_detect_enemies(user, world)
        elif skill_id == "escape":
            return self._execute_escape(user, world)
        elif skill_id == "illuminate":
            return self._execute_illuminate(user, world)
        elif skill_id == "purify":
            return self._execute_purify(user, party)
        elif skill_id == "haste":
            return self._execute_haste(user, party)
        else:
            return {"success": False, "message": f"알 수 없는 스킬: {skill_id}"}
    
    def _execute_heal(self, user: Character, party: PartyManager) -> Dict[str, Any]:
        """파티 치유 스킬"""
        total_healed = 0
        healed_members = []
        
        # 사용자의 마법 능력에 따른 회복량 결정
        base_heal = 30
        magic_bonus = getattr(user, 'magic_attack', 10) // 5
        heal_amount = base_heal + magic_bonus
        
        for member in party.get_alive_members():
            if member.current_hp < member.max_hp:
                healed = member.heal(heal_amount)
                if healed > 0:
                    total_healed += healed
                    healed_members.append(f"{member.name}: +{healed} HP")
        
        if total_healed > 0:
            message = f"{user.name}의 치유로 파티가 회복되었습니다!\n" + "\n".join(healed_members)
            return {"success": True, "message": message, "total_healed": total_healed}
        else:
            return {"success": False, "message": "회복이 필요한 멤버가 없습니다."}
    
    def _execute_teleport(self, user: Character, world, target_pos) -> Dict[str, Any]:
        """공간 도약 스킬 - 벽이나 함정을 뛰어넘어 이동 (경로 확인)"""
        if not world:
            return {"success": False, "message": "이동할 수 없는 지역입니다."}
        
        # 플레이어 현재 위치에서 2-5칸 범위 내에서 빈 공간 찾기
        current_pos = getattr(world, 'player_pos', (0, 0))
        x, y = current_pos
        
        # 가능한 도약 위치들 (2-5칸 거리로 확장)
        jump_range = 5  # 3 -> 5로 확장
        possible_positions = []
        
        for dx in range(-jump_range, jump_range + 1):
            for dy in range(-jump_range, jump_range + 1):
                distance = abs(dx) + abs(dy)
                if 2 <= distance <= jump_range:  # 최소 2칸, 최대 5칸
                    new_x, new_y = x + dx, y + dy
                    
                    # 월드 경계 체크
                    if (0 <= new_x < getattr(world, 'width', 80) and 
                        0 <= new_y < getattr(world, 'height', 25)):
                        
                        # 해당 위치가 이동 가능한지 체크
                        if (hasattr(world, 'tiles') and world.tiles and
                            len(world.tiles) > new_y and len(world.tiles[new_y]) > new_x):
                            
                            target_tile = world.tiles[new_y][new_x]
                            if (hasattr(target_tile, 'is_walkable') and target_tile.is_walkable()):
                                
                                # 경로상에 벽이 있는지 확인 (직선 경로)
                                if self._is_path_clear(world, (x, y), (new_x, new_y)):
                                    # 적이나 장애물이 있는지 추가 체크
                                    if not self._has_obstacle_at_position(world, (new_x, new_y)):
                                        possible_positions.append((new_x, new_y, distance))
        
        if possible_positions:
            # 거리순으로 정렬하여 가까운 곳부터 선택
            possible_positions.sort(key=lambda pos: pos[2])
            
            # 상위 5개 위치 중 랜덤 선택
            import random
            best_positions = possible_positions[:min(5, len(possible_positions))]
            target_x, target_y, distance = random.choice(best_positions)
            
            if hasattr(world, 'player_pos'):
                old_pos = world.player_pos
                world.player_pos = (target_x, target_y)
                
                # 시야 업데이트 (있는 경우)
                if hasattr(world, 'update_visibility'):
                    world.update_visibility()
                
                return {
                    "success": True, 
                    "message": f"{user.name}이(가) 공간을 도약하여 {distance}칸 이동했습니다!\n위치: ({old_pos[0]}, {old_pos[1]}) → ({target_x}, {target_y})",
                    "new_position": (target_x, target_y),
                    "distance": distance
                }
        
        return {"success": False, "message": "도약할 안전한 위치를 찾을 수 없습니다. 주변에 벽이나 장애물이 너무 많습니다."}
    
    def _is_path_clear(self, world, start_pos, end_pos) -> bool:
        """두 지점 사이의 경로에 벽이 있는지 확인 (브레젠햄 라인 알고리즘 사용)"""
        x0, y0 = start_pos
        x1, y1 = end_pos
        
        # 브레젠햄 라인 알고리즘으로 경로상의 모든 점 확인
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        
        x, y = x0, y0
        
        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1
        
        error = dx - dy
        
        while True:
            # 현재 위치가 벽인지 확인 (시작점과 끝점 제외)
            if (x, y) != start_pos and (x, y) != end_pos:
                if (hasattr(world, 'tiles') and world.tiles and
                    0 <= y < len(world.tiles) and 0 <= x < len(world.tiles[y])):
                    
                    tile = world.tiles[y][x]
                    if hasattr(tile, 'is_walkable') and not tile.is_walkable():
                        return False  # 경로상에 벽이 있음
                else:
                    return False  # 월드 경계 밖
            
            if x == x1 and y == y1:
                break
                
            e2 = 2 * error
            if e2 > -dy:
                error -= dy
                x += x_inc
            if e2 < dx:
                error += dx
                y += y_inc
        
        return True  # 경로가 깨끗함
    
    def _has_obstacle_at_position(self, world, position) -> bool:
        """특정 위치에 적이나 기타 장애물이 있는지 확인"""
        x, y = position
        
        # 적이 있는지 확인
        if hasattr(world, 'floor_enemies') and world.floor_enemies:
            for enemy_pos in world.floor_enemies.keys():
                if enemy_pos == position:
                    return True
        
        # 기타 장애물 확인 (함정, 특수 타일 등)
        if (hasattr(world, 'tiles') and world.tiles and
            0 <= y < len(world.tiles) and 0 <= x < len(world.tiles[y])):
            
            tile = world.tiles[y][x]
            # 특수 타일 타입 확인 (있는 경우)
            if hasattr(tile, 'type'):
                # 함정이나 특수 지형은 피하기
                dangerous_types = ['TRAP', 'LAVA', 'WATER', 'PIT']
                if hasattr(tile.type, 'name') and tile.type.name in dangerous_types:
                    return True
        
        return False
    
    def _execute_detect_items(self, user: Character, world) -> Dict[str, Any]:
        """아이템 탐지 스킬"""
        if not world:
            return {"success": False, "message": "탐지할 영역이 없습니다."}
        
        detected_items = []
        player_pos = getattr(world, 'player_pos', (0, 0))
        px, py = player_pos
        
        # 5x5 범위 내 아이템 탐지
        detection_range = 5
        for dx in range(-detection_range, detection_range + 1):
            for dy in range(-detection_range, detection_range + 1):
                check_x, check_y = px + dx, py + dy
                
                # 월드 경계 체크
                if (0 <= check_x < getattr(world, 'width', 80) and 
                    0 <= check_y < getattr(world, 'height', 25)):
                    
                    # 해당 위치에 아이템이 있는지 확인
                    if hasattr(world, 'floor_items') and world.floor_items:
                        if (check_x, check_y) in world.floor_items:
                            items_at_pos = world.floor_items[(check_x, check_y)]
                            
                            # items_at_pos가 리스트인지 단일 아이템인지 확인
                            if isinstance(items_at_pos, list):
                                items_to_check = items_at_pos
                            else:
                                items_to_check = [items_at_pos]
                            
                            for item in items_to_check:
                                if item:  # None 체크
                                    item_name = getattr(item, 'name', '알 수 없는 아이템')
                                    distance = abs(dx) + abs(dy)
                                    detected_items.append(f"{item_name} (거리: {distance})")
        
        message = f"{user.name}이(가) 주변을 탐지했습니다!"
        if detected_items:
            message += f"\n🎁 발견된 아이템 ({len(detected_items)}개):\n" + "\n".join(detected_items)
        else:
            message += "\n💔 주변에 숨겨진 아이템이 없습니다."
        
        return {"success": True, "message": message, "detected_items": detected_items}
    
    def _execute_detect_enemies(self, user: Character, world) -> Dict[str, Any]:
        """적 탐지 스킬"""
        if not world:
            return {"success": False, "message": "탐지할 영역이 없습니다."}
        
        detected_enemies = []
        player_pos = getattr(world, 'player_pos', (0, 0))
        px, py = player_pos
        
        # 7x7 범위 내 적 탐지
        detection_range = 7
        for dx in range(-detection_range, detection_range + 1):
            for dy in range(-detection_range, detection_range + 1):
                check_x, check_y = px + dx, py + dy
                
                # 월드 경계 체크
                if (0 <= check_x < getattr(world, 'width', 80) and 
                    0 <= check_y < getattr(world, 'height', 25)):
                    
                    # 해당 위치에 적이 있는지 확인
                    if hasattr(world, 'floor_enemies') and world.floor_enemies:
                        if (check_x, check_y) in world.floor_enemies:
                            enemy = world.floor_enemies[(check_x, check_y)]
                            enemy_name = getattr(enemy, 'name', '알 수 없는 적')
                            distance = abs(dx) + abs(dy)
                            detected_enemies.append(f"{enemy_name} (거리: {distance})")
        
        message = f"{user.name}이(가) 적의 위치를 탐지했습니다!"
        if detected_enemies:
            message += f"\n⚔️ 탐지된 적 ({len(detected_enemies)}마리):\n" + "\n".join(detected_enemies)
        else:
            message += "\n✅ 주변에 적이 없어 안전합니다."
        
        return {"success": True, "message": message, "detected_enemies": detected_enemies}
    
    def _execute_escape(self, user: Character, world) -> Dict[str, Any]:
        """탈출 스킬"""
        if not world:
            return {"success": False, "message": "탈출할 수 없습니다."}
        
        # 안전한 위치 찾기
        safe_positions = []
        if hasattr(world, 'find_safe_positions'):
            safe_positions = world.find_safe_positions()
        
        if safe_positions:
            # 가장 가까운 안전한 위치로 이동
            import random
            escape_pos = random.choice(safe_positions[:3])  # 상위 3개 중 랜덤
            
            if hasattr(world, 'player_pos'):
                old_pos = world.player_pos
                world.player_pos = escape_pos
                
                # 시야 업데이트
                if hasattr(world, 'update_visibility'):
                    world.update_visibility()
                
                distance = abs(escape_pos[0] - old_pos[0]) + abs(escape_pos[1] - old_pos[1])
                message = f"{user.name}이(가) 안전한 곳으로 파티를 이끌었습니다!\n위치: ({old_pos[0]}, {old_pos[1]}) → ({escape_pos[0]}, {escape_pos[1]}) (거리: {distance})"
                return {"success": True, "message": message, "new_position": escape_pos}
        
        message = f"{user.name}이(가) 탈출을 시도했지만 안전한 장소를 찾을 수 없습니다!"
        return {"success": False, "message": message}
    
    def _execute_illuminate(self, user: Character, world) -> Dict[str, Any]:
        """조명 스킬"""
        if world and hasattr(world, 'visibility_radius'):
            # 시야 반경을 일시적으로 확장
            original_radius = world.visibility_radius
            world.visibility_radius = min(15, original_radius + 5)  # 최대 15까지 확장
            
            # 시야 업데이트
            if hasattr(world, 'update_visibility'):
                world.update_visibility()
            
            message = f"{user.name}이(가) 주변을 밝게 비췄습니다!\n✨ 시야가 확장되었습니다! (반경: {original_radius} → {world.visibility_radius})"
            
            # 10턴 후 원래대로 복구하는 효과 (실제 구현에서는 턴 시스템과 연동)
            return {"success": True, "message": message, "effect_duration": 10, "original_radius": original_radius}
        else:
            message = f"{user.name}이(가) 주변을 밝게 비췄습니다!"
            return {"success": True, "message": message}
    
    def _execute_purify(self, user: Character, party: PartyManager) -> Dict[str, Any]:
        """정화 스킬"""
        from .status_effects import StatusEffectType
        
        # 디버프 효과 타입들 정의
        debuff_types = {
            StatusEffectType.POISON, StatusEffectType.BURN, StatusEffectType.BLEED,
            StatusEffectType.CORROSION, StatusEffectType.FROSTBITE, StatusEffectType.LIGHTNING_SHOCK,
            StatusEffectType.CURSE, StatusEffectType.NECROSIS, StatusEffectType.STUN,
            StatusEffectType.SLEEP, StatusEffectType.CHARM, StatusEffectType.FEAR,
            StatusEffectType.CONFUSION, StatusEffectType.PARALYSIS, StatusEffectType.SILENCE,
            StatusEffectType.BLIND, StatusEffectType.PETRIFY, StatusEffectType.FREEZE,
            StatusEffectType.SLOW, StatusEffectType.ROOT, StatusEffectType.DEBUFF_ATTACK,
            StatusEffectType.WEAKENED, StatusEffectType.DEBUFF_DEFENSE, StatusEffectType.ARMOR_BREAK,
            StatusEffectType.VULNERABILITY, StatusEffectType.DEBUFF_SPEED, StatusEffectType.MANA_BURN
        }
        
        purified_members = []
        
        for member in party.get_alive_members():
            if hasattr(member, 'status_manager'):
                debuffs_removed = []
                
                # 현재 효과 목록을 복사해서 안전하게 제거
                current_effects = member.status_manager.effects[:]
                for effect in current_effects:
                    if effect.type in debuff_types:
                        remove_message = member.status_manager.remove_effect(effect.type)
                        if remove_message:  # 실제로 제거된 경우
                            debuffs_removed.append(effect.type.value)
                
                if debuffs_removed:
                    purified_members.append(f"{member.name}: {', '.join(debuffs_removed)} 제거")
        
        if purified_members:
            message = f"{user.name}의 정화로 상태이상이 제거되었습니다!\n" + "\n".join(purified_members)
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": "제거할 상태이상이 없습니다."}
    
    def _execute_haste(self, user: Character, party: PartyManager) -> Dict[str, Any]:
        """시간 조작 스킬 - 적들의 시간을 늦춤"""
        # 월드의 모든 적들에게 slow 효과 적용
        affected_enemies = 0
        
        # 실제 게임에서는 world 객체를 통해 적들에게 접근
        # 여기서는 시뮬레이션으로 효과 설명
        message_parts = [f"{user.name}이(가) 시간의 흐름을 조작했습니다!"]
        
        # 파티 멤버들의 ATB 게이지도 약간 증가
        enhanced_members = []
        for member in party.get_alive_members():
            if hasattr(member, 'atb_gauge'):
                member.atb_gauge = min(100, member.atb_gauge + 20)
                enhanced_members.append(f"{member.name}: ATB +20%")
        
        if enhanced_members:
            message_parts.append("파티원들이 상대적으로 빨라졌습니다:")
            message_parts.extend(enhanced_members)
        
        # 적들에게 슬로우 효과 적용 (실제 구현에서는 world 객체 필요)
        message_parts.append("주변의 모든 적들이 느려졌습니다! (5턴간 지속)")
        
        return {
            "success": True, 
            "message": "\n".join(message_parts),
            "effect_duration": 5,
            "effect_type": "time_manipulation"
        }
    
    def _is_on_cooldown(self, skill_id: str) -> bool:
        """스킬 쿨다운 확인"""
        if skill_id not in self.last_used:
            return False
        
        # 실제 게임에서는 턴 카운터와 비교
        cooldown = self.field_skills[skill_id]["cooldown"]
        turns_passed = 0  # 실제 턴 카운터와 연동 필요
        
        return turns_passed < cooldown
    
    def get_skill_info(self, skill_id: str) -> str:
        """스킬 정보 반환"""
        if skill_id not in self.field_skills:
            return "알 수 없는 스킬"
        
        skill_info = self.field_skills[skill_id]
        info_lines = [
            f"🎯 {skill_info['name']}",
            f"📝 {skill_info['description']}",
            f"💙 MP 소모: {skill_info['mp_cost']}",
            f"⏰ 쿨다운: {skill_info['cooldown']}턴",
            f"👥 필요 직업: {', '.join(skill_info['required_class'])}"
        ]
        
        return "\n".join(info_lines)

# 전역 필드 스킬 선택기
_field_skill_selector = None

def get_field_skill_selector():
    """필드 스킬 선택기 인스턴스 반환"""
    global _field_skill_selector
    if _field_skill_selector is None:
        from .ffvii_sound_system import get_ffvii_sound_system
        _field_skill_selector = FieldSkillSelector(get_ffvii_sound_system())
    return _field_skill_selector
