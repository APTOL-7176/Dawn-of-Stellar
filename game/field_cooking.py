"""
필드 요리 인터페이스 - 채집 시스템, BRV/상처 연동 포함
"""

from typing import Dict, List, Optional, Tuple
import random

from game.cooking_system import cooking_system, ENEMY_SPECIFIC_DROPS, GATHERING_LOCATIONS
from game.color_text import (colored, bright_green, bright_yellow, bright_red, 
                            bright_cyan, bright_white, RED, GREEN, YELLOW, BLUE, 
                            MAGENTA, CYAN, WHITE, RESET, BOLD)

class FieldCookingInterface:
    """필드 요리 인터페이스"""
    
    def __init__(self):
        self.cooking_system = cooking_system
    
    def show_cooking_menu(self):
        """요리 메뉴 표시"""
        while True:
            print(f"\n{CYAN}{'='*80}{RESET}")
            print(f"{WHITE}{BOLD}🍳 야외 요리 & 채집 시스템{RESET}")
            print(f"{CYAN}{'='*80}{RESET}")
            
            # 파티의 실제 총 무게한계 계산
            total_weight = self.cooking_system.get_total_inventory_weight()
            max_weight = self._get_party_max_weight()
            
            weight_ratio = total_weight / max_weight if max_weight > 0 else 0
            if weight_ratio >= 0.8:
                weight_color = RED
            elif weight_ratio >= 0.6:
                weight_color = YELLOW
            else:
                weight_color = GREEN
                
            print(f"{WHITE}현재 인벤토리 무게: {weight_color}{total_weight:.1f}kg / {max_weight:.1f}kg{RESET}")
            print(f"{WHITE}요리 레벨: {GREEN}{self.cooking_system.cooking_level}{RESET} "
                  f"(경험치: {self.cooking_system.cooking_experience}/{self.cooking_system.cooking_level * 100}){RESET}")
            
            # 빠른 요리 메뉴 (발견한 레시피)
            quick_recipes = self.cooking_system.get_quick_cooking_menu()
            if quick_recipes:
                print(f"\n{MAGENTA}⚡ 빠른 요리 (발견한 레시피):{RESET}")
                for i, recipe_name in enumerate(quick_recipes[:5], 1):  # 최대 5개만 표시
                    recipe = self.cooking_system.all_recipes[recipe_name]
                    print(f"{YELLOW}[Q{i}] {recipe.icon} {recipe_name}{RESET}")
                print(f"{CYAN}💡 빠른 요리: Q1, Q2... 입력 후 엔터{RESET}")
            
            # 상시 도전 모드 - 재료 개수만 표시
            total_ingredients = sum(self.cooking_system.ingredients_inventory.values())
            print(f"\n{CYAN}📦 보유 재료: 총 {total_ingredients}개 (내용물 미확인){RESET}")
            
            print(f"\n{YELLOW}[1] 요리 제작하기 (감각에 의존){RESET}")
            print(f"{YELLOW}[2] 완성된 요리 보기{RESET}")
            print(f"{YELLOW}[3] 요리 먹기{RESET}")
            print(f"{YELLOW}[4] 활성 요리 효과 보기{RESET}")
            print(f"{YELLOW}[5] 채집 장소 가기{RESET}")
            print(f"{YELLOW}[0] 돌아가기{RESET}")
            
            choice = input(f"\n{WHITE}선택: {RESET}").strip()
            
            # 빠른 요리 처리
            if choice.upper().startswith('Q'):
                try:
                    quick_idx = int(choice[1:]) - 1
                    if 0 <= quick_idx < len(quick_recipes):
                        recipe_name = quick_recipes[quick_idx]
                        result, message = self.cooking_system.quick_cook_dish(recipe_name)
                        if result:
                            print(f"{GREEN}{message}{RESET}")
                            # 새 레시피 발견 시 특별 사운드
                            if "새로운 요리를 발견" in message:
                                try:
                                    from game.audio_system import get_audio_manager, SFXType
                                    audio_manager = get_audio_manager()
                                    audio_manager.play_sfx(SFXType.SKILL_LEARN)
                                except:
                                    pass
                        else:
                            print(f"{RED}{message}{RESET}")
                    else:
                        print(f"{RED}잘못된 빠른 요리 번호입니다.{RESET}")
                except (ValueError, IndexError):
                    print(f"{RED}잘못된 입력입니다.{RESET}")
            elif choice == "1":
                self._show_challenge_cooking()  # 상시 도전 모드
            elif choice == "2":
                self.cooking_system.show_cooked_food_inventory()
            elif choice == "3":
                self._show_food_consumption()
            elif choice == "4":
                self.cooking_system.show_active_buffs()
            elif choice == "5":
                self._show_gathering_menu()
            elif choice == "0":
                break
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
            
            input(f"\n{CYAN}계속하려면 Enter를 누르세요...{RESET}")
    
    def _get_party_max_weight(self) -> float:
        """파티의 총 무게한계 계산"""
        # cooking_system에서 계산하도록 위임
        return self.cooking_system.get_max_inventory_weight()
    
    def _show_gathering_menu(self):
        """채집 장소 메뉴"""
        print(f"\n{CYAN}{'='*80}{RESET}")
        print(f"{WHITE}{BOLD}🌍 채집 장소 선택{RESET}")
        print(f"{CYAN}{'='*80}{RESET}")
        
        # 채집 상태 정보 표시
        try:
            from game.gathering_limiter import get_gathering_status
            status = get_gathering_status()
            
            cooldown_remaining = status['cooldown_remaining_steps']
            if cooldown_remaining > 0:
                print(f"{RED}⏰ 채집 쿨다운: {cooldown_remaining}걸음 더 이동 필요{RESET}")
            else:
                print(f"{GREEN}✅ 채집 가능{RESET}")
            print()
        except ImportError:
            pass
        
        locations = list(GATHERING_LOCATIONS.items())
        
        for i, (location_name, location_data) in enumerate(locations, 1):
            print(f"\n{YELLOW}[{i}] {location_data['icon']} {location_name}{RESET}")
            print(f"    {WHITE}{location_data['description']}{RESET}")
            print(f"    {GREEN}일반 재료: {', '.join(location_data['common'][:3])}...{RESET}")
            print(f"    {BLUE}희귀 재료: {', '.join(location_data['uncommon'][:2])}...{RESET}")
            print(f"    {MAGENTA}전설 재료: {', '.join(location_data['rare'])}...{RESET}")
        
        try:
            choice = int(input(f"\n{WHITE}어디로 가시겠습니까? (0: 취소): {RESET}"))
            if choice == 0:
                return
            
            if 1 <= choice <= len(locations):
                location_name = locations[choice-1][0]
                self._start_gathering(location_name)
            else:
                print(f"{RED}잘못된 번호입니다.{RESET}")
        
        except ValueError:
            print(f"{RED}숫자를 입력해주세요.{RESET}")
    
    def _start_gathering(self, location_name: str):
        """채집 시작"""
        location_data = GATHERING_LOCATIONS[location_name]
        
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}{location_data['icon']} {location_name}에서 채집 중...{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        print(f"{WHITE}{location_data['description']}{RESET}")
        
        # 채집 제한 확인
        try:
            from game.gathering_limiter import can_gather_at_location, record_gathering_attempt
            can_gather, message = can_gather_at_location(location_name)
            
            if not can_gather:
                print(f"{RED}❌ {message}{RESET}")
                input(f"\n{CYAN}아무 키나 눌러 돌아가기...{RESET}")
                return
        except ImportError:
            pass  # 제한 시스템이 없으면 계속 진행
        
        print(f"{YELLOW}채집을 시작합니다...{RESET}")
        
        # 채집 시도
        gathered_ingredients = self.cooking_system.gather_ingredients_from_location(location_name)
        
        # 채집 성공 시 기록
        if gathered_ingredients:
            try:
                record_gathering_attempt(location_name)
            except (ImportError, NameError):
                pass
        
        if gathered_ingredients:
            print(f"\n{GREEN}🎉 채집 성공!{RESET}")
            
            for ingredient_name in gathered_ingredients:
                if ingredient_name in self.cooking_system.all_ingredients:
                    ingredient = self.cooking_system.all_ingredients[ingredient_name]
                    rarity_colors = [WHITE, GREEN, BLUE, MAGENTA, YELLOW]
                    rarity_color = rarity_colors[min(ingredient.rarity-1, 4)]
                    
                    print(f"  {ingredient.icon} {rarity_color}{ingredient_name}{RESET} "
                          f"(희귀도 {ingredient.rarity}⭐, 무게: {ingredient.weight:.1f}kg)")
            
            print(f"\n{CYAN}총 {len(gathered_ingredients)}개의 재료를 채집했습니다!{RESET}")
        else:
            print(f"{YELLOW}아무것도 찾지 못했습니다... 다음에 다시 시도해보세요.{RESET}")
    
    def _show_cooking_recipes(self):
        """요리 제작 메뉴"""
        print(f"\n{CYAN}{'='*80}{RESET}")
        print(f"{WHITE}{BOLD}🥘 요리 제작{RESET}")
        print(f"{CYAN}{'='*80}{RESET}")
        
        # 우선도순으로 레시피 정렬
        available_recipes = []
        for recipe_name, recipe in self.cooking_system.all_recipes.items():
            if recipe_name == "곤죽":  # 곤죽은 제외
                continue
            
            can_cook, _ = self.cooking_system.can_cook_with_substitutes(recipe_name)
            if can_cook:
                available_recipes.append((recipe_name, recipe))
        
        available_recipes.sort(key=lambda x: x[1].priority, reverse=True)
        
        if not available_recipes:
            print(f"{RED}현재 만들 수 있는 요리가 없습니다.{RESET}")
            return
        
        print(f"{GREEN}제작 가능한 요리 (우선도순):{RESET}")
        for i, (recipe_name, recipe) in enumerate(available_recipes, 1):
            difficulty_color = [WHITE, GREEN, YELLOW, MAGENTA, RED][min(recipe.difficulty-1, 4)]
            priority_color = [WHITE, GREEN, YELLOW, CYAN, MAGENTA][min((recipe.priority-1)//2, 4)]
            
            print(f"\n{YELLOW}[{i}] {recipe.icon} {priority_color}{recipe_name}{RESET}")
            print(f"    {WHITE}{recipe.description}{RESET}")
            print(f"    우선도: {priority_color}{recipe.priority}{RESET}, "
                  f"난이도: {difficulty_color}{recipe.difficulty}{RESET}, "
                  f"무게: {recipe.weight:.1f}kg")
            print(f"    지속시간: {CYAN}{recipe.duration_steps}걸음{RESET}")
            
            # 필요 재료 표시
            print(f"    필요 재료:")
            for ingredient_type, needed_value in recipe.ingredients.items():
                print(f"      - {ingredient_type}: {needed_value:.1f} 가치")
            
            # 효과 표시
            if recipe.effects:
                effects_display = []
                for effect, value in recipe.effects.items():
                    if "max_" in effect and "_increase" in effect:
                        effects_display.append(f"{effect}: +{value} (영구적)")
                    elif "wound_healing" in effect:
                        effects_display.append(f"상처 치유: {value}%")
                    elif "brv_" in effect:
                        effects_display.append(f"BRV {effect.split('_', 1)[1]}: +{value}")
                    else:
                        effects_display.append(f"{effect}: +{value}")
                
                effects_str = ", ".join(effects_display)
                print(f"    효과: {GREEN}{effects_str}{RESET}")
            
            if recipe.special_effects:
                print(f"    특수효과: {MAGENTA}{', '.join(recipe.special_effects)}{RESET}")
        
        try:
            choice = int(input(f"\n{WHITE}제작할 요리 번호 (0: 취소): {RESET}"))
            if choice == 0:
                return
            
            if 1 <= choice <= len(available_recipes):
                recipe_name = available_recipes[choice-1][0]
                success, message = self.cooking_system.cook_dish(recipe_name)
                
                if success:
                    print(f"{GREEN}✅ {message}{RESET}")
                else:
                    print(f"{RED}❌ {message}{RESET}")
            else:
                print(f"{RED}잘못된 번호입니다.{RESET}")
        
        except ValueError:
            print(f"{RED}숫자를 입력해주세요.{RESET}")
    
    def _show_food_consumption(self):
        """요리 섭취 메뉴"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🍽️ 요리 섭취{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        if not self.cooking_system.cooked_food_inventory:
            print(f"{RED}먹을 수 있는 요리가 없습니다.{RESET}")
            return
        
        foods = list(self.cooking_system.cooked_food_inventory.items())
        
        for i, (food_name, amount) in enumerate(foods, 1):
            recipe = self.cooking_system.all_recipes[food_name]
            print(f"\n{YELLOW}[{i}] {recipe.icon} {food_name} x{amount}{RESET}")
            print(f"    {WHITE}{recipe.description}{RESET}")
            
            if recipe.effects:
                effects_display = []
                for effect, value in recipe.effects.items():
                    if "max_" in effect and "_increase" in effect:
                        effects_display.append(f"{effect}: +{value} (영구적)")
                    elif "wound_healing" in effect:
                        effects_display.append(f"상처 치유: {value}%")
                    elif "brv_" in effect:
                        effects_display.append(f"BRV {effect.split('_', 1)[1]}: +{value}")
                    else:
                        effects_display.append(f"{effect}: +{value}")
                
                effects_str = ", ".join(effects_display)
                print(f"    효과: {GREEN}{effects_str}{RESET}")
            
            print(f"    지속시간: {CYAN}{recipe.duration_steps}걸음{RESET}")
        
        try:
            choice = int(input(f"\n{WHITE}먹을 요리 번호 (0: 취소): {RESET}"))
            if choice == 0:
                return
            
            if 1 <= choice <= len(foods):
                food_name = foods[choice-1][0]
                success, message = self.cooking_system.consume_food(food_name)
                
                if success:
                    print(f"{GREEN}✅ {message}{RESET}")
                else:
                    print(f"{RED}❌ {message}{RESET}")
            else:
                print(f"{RED}잘못된 번호입니다.{RESET}")
        
        except ValueError:
            print(f"{RED}숫자를 입력해주세요.{RESET}")

def handle_enemy_defeat(enemy_name: str, enemy_level: int) -> List[str]:
    """적 처치 시 식재료 드롭 처리 (개선된 알림 포함)"""
    dropped_ingredients = []
    
    # 적별 특정 드롭 체크
    specific_drop = cooking_system.get_enemy_specific_ingredient_drop(enemy_name, enemy_level)
    if specific_drop and specific_drop in cooking_system.all_ingredients:
        if cooking_system.add_ingredient(specific_drop, 1):
            ingredient = cooking_system.all_ingredients[specific_drop]
            rarity_colors = [WHITE, GREEN, BLUE, MAGENTA, YELLOW]
            rarity_color = rarity_colors[min(ingredient.rarity-1, 4)]
            
            print(f"\n{CYAN}🎁 특별 드롭!{RESET}")
            print(f"{ingredient.icon} {rarity_color}{specific_drop}{RESET} (희귀도 {ingredient.rarity}⭐) 획득!")
            print(f"무게: {ingredient.weight:.1f}kg")
            dropped_ingredients.append(specific_drop)
        else:
            print(f"{RED}⚠️ 인벤토리가 가득 차서 {specific_drop}을(를) 얻을 수 없습니다!{RESET}")
    
    # 일반 랜덤 드롭
    random_drop = cooking_system.get_random_ingredient_drop(enemy_level)
    if random_drop and random_drop in cooking_system.all_ingredients:
        if cooking_system.add_ingredient(random_drop, 1):
            ingredient = cooking_system.all_ingredients[random_drop]
            rarity_colors = [WHITE, GREEN, BLUE, MAGENTA, YELLOW]
            rarity_color = rarity_colors[min(ingredient.rarity-1, 4)]
            
            print(f"\n{GREEN}📦 식재료 발견!{RESET}")
            print(f"{ingredient.icon} {rarity_color}{random_drop}{RESET} (희귀도 {ingredient.rarity}⭐) 획득!")
            print(f"무게: {ingredient.weight:.1f}kg")
            dropped_ingredients.append(random_drop)
        else:
            print(f"{RED}⚠️ 인벤토리가 가득 차서 {random_drop}을(를) 얻을 수 없습니다!{RESET}")
    
    return dropped_ingredients

def handle_field_ingredient_find() -> Optional[str]:
    """필드에서 식재료 발견 처리"""
    # 3% 확률로 필드 재료 발견 (채집지가 있으니 확률 감소)
    if random.random() < 0.03:
        # 낮은 희귀도 재료 위주로 발견
        common_ingredients = [name for name, ingredient in cooking_system.all_ingredients.items() 
                             if ingredient.rarity <= 2]
        
        if common_ingredients:
            found_ingredient = random.choice(common_ingredients)
            
            if cooking_system.add_ingredient(found_ingredient, 1):
                ingredient = cooking_system.all_ingredients[found_ingredient]
                rarity_colors = [WHITE, GREEN, BLUE, MAGENTA, YELLOW]
                rarity_color = rarity_colors[min(ingredient.rarity-1, 4)]
                
                print(f"\n{YELLOW}🌿 필드에서 식재료 발견!{RESET}")
                print(f"{ingredient.icon} {rarity_color}{found_ingredient}{RESET} 획득!")
                print(f"무게: {ingredient.weight:.1f}kg")
                
                return found_ingredient
            else:
                print(f"{RED}⚠️ 인벤토리가 가득 차서 {found_ingredient}을(를) 주울 수 없습니다!{RESET}")
    
    return None

def handle_gathering_encounter():
    """채집지 발견 인카운터"""
    locations = list(GATHERING_LOCATIONS.keys())
    discovered_location = random.choice(locations)
    location_data = GATHERING_LOCATIONS[discovered_location]
    
    print(f"\n{CYAN}🌍 채집지 발견!{RESET}")
    print(f"{location_data['icon']} {GREEN}{discovered_location}{RESET}을(를) 발견했습니다!")
    print(f"{WHITE}{location_data['description']}{RESET}")
    
    choice = input(f"\n{YELLOW}채집을 시작하시겠습니까? (y/n): {RESET}").strip().lower()
    
    if choice == 'y':
        gathered = cooking_system.gather_ingredients_from_location(discovered_location)
        
        if gathered:
            print(f"\n{GREEN}🎉 채집 성공!{RESET}")
            for ingredient_name in gathered:
                if ingredient_name in cooking_system.all_ingredients:
                    ingredient = cooking_system.all_ingredients[ingredient_name]
                    rarity_colors = [WHITE, GREEN, BLUE, MAGENTA, YELLOW]
                    rarity_color = rarity_colors[min(ingredient.rarity-1, 4)]
                    
                    print(f"  {ingredient.icon} {rarity_color}{ingredient_name}{RESET} "
                          f"(희귀도 {ingredient.rarity}⭐)")
        else:
            print(f"{YELLOW}아무것도 찾지 못했습니다...{RESET}")
    else:
        print(f"{YELLOW}채집을 포기했습니다.{RESET}")

def update_cooking_buffs_on_step():
    """걸음마다 요리 버프 업데이트"""
    cooking_system.update_buffs_on_step()

def get_cooking_effects_for_party() -> Dict[str, int]:
    """파티에 적용할 요리 효과 반환"""
    return cooking_system.get_total_effects()

def get_cooking_special_effects() -> List[str]:
    """파티에 적용할 특수 요리 효과 반환"""
    return cooking_system.get_special_effects()

def apply_cooking_effects_to_character(character, effects: Dict[str, int]):
    """캐릭터에게 요리 효과 적용"""
    if not effects:
        return
    
    # HP/MP 회복
    if "hp_recovery" in effects:
        old_hp = character.current_hp
        character.current_hp = min(character.max_hp, character.current_hp + effects["hp_recovery"])
        if character.current_hp > old_hp:
            print(f"{GREEN}{character.name}의 HP가 {character.current_hp - old_hp} 회복되었습니다!{RESET}")
    
    if "mp_recovery" in effects:
        old_mp = character.current_mp
        character.current_mp = min(character.max_mp, character.current_mp + effects["mp_recovery"])
        if character.current_mp > old_mp:
            print(f"{BLUE}{character.name}의 MP가 {character.current_mp - old_mp} 회복되었습니다!{RESET}")
    
    # 최대 HP/MP 영구 증가
    if "max_hp_increase" in effects:
        if not hasattr(character, '_cooking_max_hp_bonus'):
            character._cooking_max_hp_bonus = 0
        
        bonus_increase = effects["max_hp_increase"] - character._cooking_max_hp_bonus
        if bonus_increase > 0:
            character.max_hp += bonus_increase
            character.current_hp += bonus_increase  # 현재 HP도 같이 증가
            character._cooking_max_hp_bonus = effects["max_hp_increase"]
            print(f"{MAGENTA}{character.name}의 최대 HP가 {bonus_increase} 영구 증가했습니다! (총 +{effects['max_hp_increase']}){RESET}")
    
    if "max_mp_increase" in effects:
        if not hasattr(character, '_cooking_max_mp_bonus'):
            character._cooking_max_mp_bonus = 0
        
        bonus_increase = effects["max_mp_increase"] - character._cooking_max_mp_bonus
        if bonus_increase > 0:
            character.max_mp += bonus_increase
            character.current_mp += bonus_increase  # 현재 MP도 같이 증가
            character._cooking_max_mp_bonus = effects["max_mp_increase"]
            print(f"{MAGENTA}{character.name}의 최대 MP가 {bonus_increase} 영구 증가했습니다! (총 +{effects['max_mp_increase']}){RESET}")
    
    # 상처 치유
    if "wound_healing" in effects and hasattr(character, 'wounds'):
        heal_amount = int(character.wounds * (effects["wound_healing"] / 100))
        if heal_amount > 0:
            character.wounds = max(0, character.wounds - heal_amount)
            print(f"{GREEN}🩹 {character.name}의 상처가 {heal_amount} 치유되었습니다! (남은 상처: {character.wounds}){RESET}")
    
    # HP 지속 회복 (hp_regen_per_step 특수효과)
    for buff in cooking_system.active_buffs:
        if "hp_regen_per_step" in buff.special_effects and "hp_regen_per_step" in buff.effects:
            old_hp = character.current_hp
            character.current_hp = min(character.max_hp, character.current_hp + buff.effects["hp_regen_per_step"])
            if character.current_hp > old_hp:
                print(f"{GREEN}🍃 {character.name}의 HP가 {buff.effects['hp_regen_per_step']} 지속 회복되었습니다!{RESET}")
    
    def _show_challenge_cooking(self):
        """상시 도전 요리 모드 (재료 확인 불가)"""
        print(f"\n{RED}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🔥 요리 제작 (감각에 의존){RESET}")
        print(f"{RED}{'='*60}{RESET}")
        print(f"{WHITE}재료를 확인할 수 없습니다! 감각과 기억에 의존해서 요리하세요!{RESET}")
        
        # 재료 개수만 표시
        total_ingredients = sum(self.cooking_system.ingredients_inventory.values())
        print(f"{YELLOW}📦 보유 재료: 총 {total_ingredients}개 (내용물 미확인){RESET}")
        
        # 발견한 레시피 힌트 (이름만)
        if self.cooking_system.discovered_recipes:
            print(f"\n{CYAN}🧠 기억하는 요리법:{RESET}")
            discovered_list = sorted(list(self.cooking_system.discovered_recipes))
            for i, recipe_name in enumerate(discovered_list):
                recipe = self.cooking_system.all_recipes[recipe_name]
                print(f"  {recipe.icon} {recipe_name}")
                if i >= 9:  # 최대 10개까지만 표시
                    remaining = len(discovered_list) - 10
                    if remaining > 0:
                        print(f"  ... 외 {remaining}개")
                    break
        
        print(f"\n{CYAN}💡 알려진 요리법을 시도해보세요:{RESET}")
        print(f"{WHITE}예: '구운 고기', '야채 수프', '과일 샐러드', '빵' 등{RESET}")
        print(f"{YELLOW}⚠️ 요리명을 정확히 입력한 후 엔터를 눌러주세요{RESET}")
        
        while True:
            print(f"\n{CYAN}{'='*40}{RESET}")
            recipe_name = input(f"{WHITE}🍳 요리명 입력 (빈칸 + 엔터: 뒤로가기): {RESET}").strip()
            
            if not recipe_name:
                print(f"{YELLOW}요리 제작을 취소합니다.{RESET}")
                break
                
            print(f"{CYAN}'{recipe_name}' 요리를 시도합니다...{RESET}")
            
            if recipe_name in self.cooking_system.all_recipes:
                result, message = self.cooking_system.cook_dish(recipe_name)
                if result:
                    print(f"{GREEN}✨ {message}{RESET}")
                    # 새로운 레시피 발견 시 특별 효과
                    if recipe_name not in self.cooking_system.discovered_recipes:
                        print(f"{MAGENTA}🎉 새로운 요리를 발견했습니다! 이제 빠른 요리에서 사용할 수 있습니다!{RESET}")
                        try:
                            from game.audio_system import get_audio_manager, SFXType
                            audio_manager = get_audio_manager()
                            audio_manager.play_sfx(SFXType.SKILL_LEARN)
                        except:
                            pass
                    # 계속할지 물어보기
                    continue_choice = input(f"\n{CYAN}계속 요리하시겠습니까? (y/엔터: 계속, n: 나가기): {RESET}").strip().lower()
                    if continue_choice == 'n':
                        break
                else:
                    print(f"{RED}❌ {message}{RESET}")
            else:
                print(f"{RED}❓ '{recipe_name}' - 그런 요리법을 모르겠습니다...{RESET}")
                
                # 유사한 요리명 제안
                similar_recipes = []
                for known_recipe in self.cooking_system.all_recipes.keys():
                    if any(word in known_recipe.lower() for word in recipe_name.lower().split()):
                        similar_recipes.append(known_recipe)
                
                if similar_recipes:
                    suggestions = similar_recipes[:3]
                    print(f"{YELLOW}💡 혹시 이런 요리를 찾으셨나요? {', '.join(suggestions)}{RESET}")
                
                # 전체 요리 목록 힌트 (처음 몇 개만)
                all_recipes = list(self.cooking_system.all_recipes.keys())
                print(f"{BLUE}📖 참고 - 일부 요리법: {', '.join(all_recipes[:8])}...{RESET}")

def get_brv_cooking_modifiers() -> Dict[str, float]:
    """BRV 시스템에 적용할 요리 효과 반환"""
    effects = cooking_system.get_total_effects()
    modifiers = {}
    
    if "brv_gain_bonus" in effects:
        modifiers["brv_gain_multiplier"] = 1.0 + (effects["brv_gain_bonus"] / 100.0)
    
    if "brv_damage_bonus" in effects:
        modifiers["brv_damage_multiplier"] = 1.0 + (effects["brv_damage_bonus"] / 100.0)
    
    if "brv_defense_bonus" in effects:
        modifiers["brv_defense_multiplier"] = 1.0 + (effects["brv_defense_bonus"] / 100.0)
    
    return modifiers

def get_field_cooking_interface(party_manager=None):
    """필드 요리 인터페이스 인스턴스 반환"""
    interface = FieldCookingInterface()
    if party_manager:
        interface.cooking_system.set_party_manager(party_manager)
    return interface
