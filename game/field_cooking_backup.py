"""
필드 요리 시스템 - 필드에서 요리 관련 기능 사용
"""

import random
from typing import List, Optional
from .cooking_system import get_cooking_system, CookingSystem
from .input_utils import KeyboardInput

# 색상 정의
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'

class FieldCookingInterface:
    """필드에서 사용하는 요리 인터페이스"""
    
    def __init__(self):
        self.cooking_system = get_cooking_system()
        self.keyboard = KeyboardInput()
    
    def show_field_cooking_menu(self):
        """필드 요리 메뉴 표시"""
        while True:
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{WHITE}{BOLD}🏕️ 필드 활동{RESET}")
            print(f"{CYAN}{'='*60}{RESET}")
            print(f"{GREEN}1.{RESET} 🍳 요리하기")
            print(f"{GREEN}2.{RESET} 📦 식재료 인벤토리")
            print(f"{GREEN}3.{RESET} 📖 레시피 확인")
            print(f"{GREEN}4.{RESET} 🌿 채집하기")
            print(f"{GREEN}5.{RESET} 🎯 자유 요리")
            print(f"{GREEN}6.{RESET} ✨ 활성 요리 효과")
            print(f"{RED}Q.{RESET} 🚪 나가기")
            print(f"{CYAN}{'='*60}{RESET}")
            print(f"{YELLOW}요리 레벨: {self.cooking_system.cooking_level} (경험치: {self.cooking_system.cooking_experience}){RESET}")
            print(f"{YELLOW}선택하세요: {RESET}", end="")
            
            choice = self.keyboard.get_key().upper()
            
            if choice == '1':
                self._cook_dish_menu()
            elif choice == '2':
                self._show_ingredient_inventory()
            elif choice == '3':
                self._show_recipes()
            elif choice == '4':
                self._foraging_simulation()
            elif choice == '5':
                self._free_cooking_menu()
            elif choice == '6':
                self._show_active_buffs()
            elif choice == 'Q':
                break
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
    
    def _show_ingredient_inventory(self):
        """식재료 인벤토리 표시"""
        self.cooking_system.show_ingredients_inventory()
        self.keyboard.wait_for_key(f"\n{CYAN}아무 키나 눌러 돌아가기...{RESET}")
    
    def _show_recipes(self):
        """레시피 표시"""
        self.cooking_system.show_available_recipes()
        self.keyboard.wait_for_key(f"\n{CYAN}아무 키나 눌러 돌아가기...{RESET}")
    
    def _show_active_buffs(self):
        """활성 버프 표시"""
        self.cooking_system.show_active_buffs()
        self.keyboard.wait_for_key(f"\n{CYAN}아무 키나 눌러 돌아가기...{RESET}")
    
    def _cook_dish_menu(self):
        """요리 제작 메뉴"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🍳 요리 제작{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        available_recipes = []
        for recipe_name in self.cooking_system.discovered_recipes:
            if self.cooking_system.can_cook(recipe_name):
                available_recipes.append(recipe_name)
        
        if not available_recipes:
            print(f"{YELLOW}현재 만들 수 있는 요리가 없습니다.{RESET}")
            self.keyboard.wait_for_key(f"\n{CYAN}아무 키나 눌러 돌아가기...{RESET}")
            return
        
        # 우선도순으로 정렬
        available_recipes.sort(key=lambda x: self.cooking_system.all_recipes[x].priority, reverse=True)
        
        print(f"{YELLOW}만들 수 있는 요리:{RESET}")
        for i, recipe_name in enumerate(available_recipes, 1):
            recipe = self.cooking_system.all_recipes[recipe_name]
            priority_stars = "⭐" * min(recipe.priority, 5)
            print(f"{GREEN}{i}.{RESET} {recipe.icon} {recipe.name} {priority_stars}")
        
        print(f"\n{YELLOW}요리할 번호를 입력하세요 (0: 취소): {RESET}", end="")
        
        try:
            choice = int(self.keyboard.get_number_input())
            if choice == 0:
                return
            elif 1 <= choice <= len(available_recipes):
                selected_recipe = available_recipes[choice - 1]
                self._cook_selected_dish(selected_recipe)
            else:
                print(f"{RED}잘못된 선택입니다.{RESET}")
        except ValueError:
            print(f"{RED}숫자를 입력해주세요.{RESET}")
        
        self.keyboard.wait_for_key(f"\n{CYAN}아무 키나 눌러 계속...{RESET}")
    
    def _cook_selected_dish(self, recipe_name: str):
        """선택된 요리 제작"""
        recipe = self.cooking_system.all_recipes[recipe_name]
        
        print(f"\n{YELLOW}🍳 {recipe.name}을(를) 요리 중...{RESET}")
        print(f"{WHITE}{recipe.description}{RESET}")
        
        # 요리 제작
        success, message = self.cooking_system.cook_dish(recipe_name)
        
        if success:
            if "곤죽" in message:
                print(f"\n{RED}💥 {message}{RESET}")
            else:
                print(f"\n{GREEN}✅ {message}{RESET}")
                print(f"{CYAN}파티 전체에게 효과가 적용되었습니다.{RESET}")
            
            # 효과 표시
            if recipe_name in [buff.recipe_name for buff in self.cooking_system.active_buffs]:
                print(f"\n{YELLOW}효과:{RESET}")
                for buff in self.cooking_system.active_buffs:
                    if buff.recipe_name == recipe_name:
                        for effect, value in buff.effects.items():
                            print(f"  {effect}: +{value}")
                        break
        else:
            print(f"\n{RED}❌ {message}{RESET}")
    
    def _free_cooking_menu(self):
        """자유 요리 메뉴"""
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}{BOLD}🎯 자유 요리{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        print(f"{WHITE}보유한 재료를 자유롭게 조합해서 요리해보세요!{RESET}")
        print(f"{YELLOW}새로운 레시피를 발견할 수 있습니다.{RESET}")
        
        if not self.cooking_system.ingredients_inventory:
            print(f"{RED}보유한 식재료가 없습니다.{RESET}")
            self.keyboard.wait_for_key(f"\n{CYAN}아무 키나 눌러 돌아가기...{RESET}")
            return
        
        # 재료 목록 표시
        print(f"\n{CYAN}보유 재료:{RESET}")
        ingredients_list = list(self.cooking_system.ingredients_inventory.keys())
        for i, ingredient in enumerate(ingredients_list, 1):
            amount = self.cooking_system.ingredients_inventory[ingredient]
            ingredient_data = self.cooking_system.all_ingredients[ingredient]
            print(f"{i}. {ingredient_data.icon} {ingredient} x{amount} (가치: {ingredient_data.value:.1f})")
        
        selected_ingredients = {}
        
        while True:
            print(f"\n{YELLOW}사용할 재료 번호를 입력하세요 (0: 요리 시작, -1: 취소): {RESET}", end="")
            
            try:
                choice = int(self.keyboard.get_number_input())
                
                if choice == -1:
                    return
                elif choice == 0:
                    if selected_ingredients:
                        break
                    else:
                        print(f"{RED}재료를 최소 1개는 선택해야 합니다.{RESET}")
                        continue
                elif 1 <= choice <= len(ingredients_list):
                    ingredient = ingredients_list[choice - 1]
                    max_amount = self.cooking_system.ingredients_inventory[ingredient]
                    
                    print(f"{YELLOW}{ingredient} 몇 개 사용하시겠습니까? (최대 {max_amount}개): {RESET}", end="")
                    amount = int(self.keyboard.get_number_input())
                    
                    if 1 <= amount <= max_amount:
                        selected_ingredients[ingredient] = amount
                        print(f"{GREEN}{ingredient} x{amount} 추가됨{RESET}")
                    else:
                        print(f"{RED}잘못된 수량입니다.{RESET}")
                else:
                    print(f"{RED}잘못된 선택입니다.{RESET}")
            except ValueError:
                print(f"{RED}숫자를 입력해주세요.{RESET}")
        
        # 자유 요리 실행
        print(f"\n{YELLOW}🍳 요리 중...{RESET}")
        success, message = self.cooking_system.cook_free_style(selected_ingredients)
        
        if success:
            if "곤죽" in message:
                print(f"\n{RED}💥 {message}{RESET}")
            else:
                print(f"\n{GREEN}✅ {message}{RESET}")
        else:
            print(f"\n{RED}❌ {message}{RESET}")
        
        self.keyboard.wait_for_key(f"\n{CYAN}아무 키나 눌러 계속...{RESET}")
    
    def _foraging_simulation(self):
        """채집 시뮬레이션"""
        print(f"\n{GREEN}🌿 채집을 시작합니다...{RESET}")
        print(f"{WHITE}주변을 둘러보며 식재료를 찾고 있습니다.{RESET}")
        
        # 3번의 채집 시도
        found_count = 0
        for i in range(3):
            print(f"\n{CYAN}채집 시도 {i+1}/3...{RESET}")
            
            ingredient = self.cooking_system.get_random_field_ingredient()
            if ingredient:
                amount = random.randint(1, 2)
                self.cooking_system.add_ingredient(ingredient, amount)
                ingredient_data = self.cooking_system.all_ingredients[ingredient]
                rarity_color = [WHITE, GREEN, BLUE, MAGENTA, YELLOW][min(ingredient_data.rarity-1, 4)]
                
                print(f"{GREEN}발견! {ingredient_data.icon} {rarity_color}{ingredient}{RESET} x{amount}")
                found_count += 1
            else:
                print(f"{YELLOW}이번엔 아무것도 찾지 못했습니다.{RESET}")
        
        if found_count == 0:
            print(f"\n{RED}아쉽게도 이번 채집에서는 아무것도 찾지 못했습니다.{RESET}")
        else:
            print(f"\n{GREEN}채집 완료! 총 {found_count}가지 재료를 찾았습니다.{RESET}")
        
        self.keyboard.wait_for_key(f"\n{CYAN}아무 키나 눌러 돌아가기...{RESET}")

def handle_enemy_defeat_ingredient_drop(enemy_name: str, enemy_level: int) -> Optional[str]:
    """적 처치 시 식재료 드롭 처리"""
    cooking_system = get_cooking_system()
    dropped_ingredient = cooking_system.get_random_ingredient_drop(enemy_level)
    
    if dropped_ingredient:
        amount = random.randint(1, 2)
        cooking_system.add_ingredient(dropped_ingredient, amount)
        ingredient_data = cooking_system.all_ingredients[dropped_ingredient]
        rarity_color = [WHITE, GREEN, BLUE, MAGENTA, YELLOW][min(ingredient_data.rarity-1, 4)]
        rarity_text = ["일반", "희귀", "레어", "에픽", "전설"][min(ingredient_data.rarity-1, 4)]
        
        print(f"\n{GREEN}🎁 식재료 획득!{RESET}")
        print(f"{ingredient_data.icon} {rarity_color}{dropped_ingredient}{RESET} ({rarity_text}) x{amount} 을(를) 획득했습니다!")
        print(f"{WHITE}{ingredient_data.description}{RESET}")
        print(f"{CYAN}가치: {ingredient_data.value:.1f}개당 | 타입: {ingredient_data.type.value}{RESET}")
        
        # 랜덤 레시피 발견 체크
        discovered_recipe = cooking_system.discover_random_recipe()
        if discovered_recipe:
            print(f"{YELLOW}💡 새로운 레시피를 발견했습니다: {discovered_recipe}!{RESET}")
        
        return dropped_ingredient
    
    return None

def handle_field_ingredient_find() -> Optional[str]:
    """필드에서 식재료 발견 처리"""
    cooking_system = get_cooking_system()
    ingredient = cooking_system.get_random_field_ingredient()
    
    if ingredient:
        cooking_system.add_ingredient(ingredient, 1)
        ingredient_data = cooking_system.all_ingredients[ingredient]
        rarity_color = [WHITE, GREEN, BLUE, MAGENTA, YELLOW][min(ingredient_data.rarity-1, 4)]
        
        print(f"\n{GREEN}🌿 야생 식재료 발견!{RESET}")
        print(f"{ingredient_data.icon} {rarity_color}{ingredient}{RESET} 을(를) 발견했습니다!")
        print(f"{WHITE}{ingredient_data.description}{RESET}")
        print(f"{CYAN}가치: {ingredient_data.value:.1f} | 타입: {ingredient_data.type.value}{RESET}")
        
        return ingredient
    else:
        print(f"{YELLOW}이 지역에서는 특별한 식재료를 찾을 수 없었습니다.{RESET}")
    return None

# 걸음마다 요리 버프 업데이트 함수
def update_cooking_buffs_on_step():
    """걸음마다 요리 버프 업데이트"""
    cooking_system = get_cooking_system()
    cooking_system.update_buffs_on_step()

# 필드 요리 인터페이스 인스턴스
field_cooking = FieldCookingInterface()

def get_field_cooking_interface():
    """필드 요리 인터페이스 반환"""
    return field_cooking
