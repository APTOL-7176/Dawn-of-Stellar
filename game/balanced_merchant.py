#!/usr/bin/env python3
"""
밸런스 조정된 상인 시스템
- 랜덤한 좋은 아이템들
- 들쭉날쭉한 가격
- 한정된 재고
- 층별 제한된 아이템 등급
"""

import random
from typing import Dict, List, Optional, Tuple
from enum import Enum

# 아이템 시스템에서 소모품 데이터베이스 임포트
try:
    from .item_system import get_consumable_database, ItemRarity as ConsumableRarity, Consumable
except ImportError:
    from item_system import get_consumable_database, ItemRarity as ConsumableRarity, Consumable

class ItemRarity(Enum):
    """아이템 희귀도"""
    COMMON = "일반"
    UNCOMMON = "고급"
    RARE = "희귀"
    EPIC = "영웅"
    LEGENDARY = "전설"
    MYTHIC = "신화"

class ItemType(Enum):
    """아이템 타입"""
    WEAPON = "무기"
    ARMOR = "방어구"
    ACCESSORY = "장신구"
    CONSUMABLE = "소모품"
    MATERIAL = "재료"

class MerchantItem:
    """상인 아이템"""
    
    def __init__(self, name: str, item_type: ItemType, rarity: ItemRarity,
                 base_price: int, description: str, min_floor: int = 1,
                 effects: Dict = None, stock: int = 1):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.base_price = base_price
        self.description = description
        self.min_floor = min_floor
        self.effects = effects or {}
        self.stock = stock
        self.max_stock = stock
        
        # 가격 변동 (들쭉날쭉하게)
        price_variation = random.uniform(0.7, 1.4)
        self.current_price = int(base_price * price_variation)

class BalancedMerchant:
    """밸런스 조정된 상인"""
    
    def __init__(self):
        self.name = random.choice([
            "떠도는 상인 길버트", "신비한 상인 아스트라", "베테랑 상인 머독",
            "젊은 상인 레오", "수상한 상인 발터", "친절한 상인 로즈",
            "고집센 상인 크로그", "현명한 상인 엘다"
        ])
        
        self.inventory: List[MerchantItem] = []
        self.gold = random.randint(500, 2000)
        self.restock_timer = 0
        self.personality = random.choice([
            "stingy",      # 구두쇠 - 비싼 가격
            "generous",    # 관대함 - 저렴한 가격  
            "chaotic",     # 혼돈 - 극단적 가격
            "normal"       # 보통 - 일반 가격
        ])
        
        self._initialize_item_pool()
    
    def _initialize_item_pool(self):
        """아이템 풀 초기화"""
        self.item_pool = {
            # 무기 (각 등급별 균등하게)
            ItemType.WEAPON: [
                # 일반 무기 (1층부터)
                MerchantItem("낡은 검", ItemType.WEAPON, ItemRarity.COMMON, 50, 
                           "오래되었지만 쓸만한 검", 1, {"attack": 8}, 2),
                MerchantItem("나무 지팡이", ItemType.WEAPON, ItemRarity.COMMON, 45,
                           "마법사용에 적합한 지팡이", 1, {"magic_power": 6}, 2),
                MerchantItem("단검", ItemType.WEAPON, ItemRarity.COMMON, 40,
                           "빠르고 가벼운 단검", 1, {"attack": 6, "speed": 3}, 2),
                MerchantItem("활", ItemType.WEAPON, ItemRarity.COMMON, 55,
                           "원거리 공격용 활", 1, {"attack": 7, "accuracy": 5}, 2),
                
                # 고급 무기 (3층부터)
                MerchantItem("강철 검", ItemType.WEAPON, ItemRarity.UNCOMMON, 150,
                           "단단한 강철로 만든 검", 3, {"attack": 15, "defense": 2}, 1),
                MerchantItem("마법 지팡이", ItemType.WEAPON, ItemRarity.UNCOMMON, 180,
                           "마법력이 깃든 지팡이", 3, {"magic_power": 18, "mp": 10}, 1),
                MerchantItem("은 단검", ItemType.WEAPON, ItemRarity.UNCOMMON, 120,
                           "은으로 만든 빠른 단검", 3, {"attack": 12, "speed": 8, "critical": 3}, 1),
                MerchantItem("복합 활", ItemType.WEAPON, ItemRarity.UNCOMMON, 140,
                           "강화된 복합 활", 3, {"attack": 14, "accuracy": 8}, 1),
                
                # 희귀 무기 (7층부터)
                MerchantItem("미스릴 검", ItemType.WEAPON, ItemRarity.RARE, 350,
                           "전설의 금속 미스릴로 제작", 7, {"attack": 25, "magic_defense": 5}, 1),
                MerchantItem("현자의 지팡이", ItemType.WEAPON, ItemRarity.RARE, 420,
                           "현자가 사용하던 지팡이", 7, {"magic_power": 30, "mp": 20, "wisdom": 10}, 1),
                MerchantItem("그림자 단검", ItemType.WEAPON, ItemRarity.RARE, 300,
                           "그림자에서 나타나는 단검", 7, {"attack": 20, "speed": 15, "stealth": 1}, 1),
                MerchantItem("엘븐 활", ItemType.WEAPON, ItemRarity.RARE, 380,
                           "엘프족이 만든 정교한 활", 7, {"attack": 23, "accuracy": 15, "range": 2}, 1),
                
                # 영웅 무기 (12층부터)
                MerchantItem("용의 검", ItemType.WEAPON, ItemRarity.EPIC, 800,
                           "용의 힘이 깃든 검", 12, {"attack": 40, "fire_damage": 15}, 1),
                MerchantItem("대마법사의 지팡이", ItemType.WEAPON, ItemRarity.EPIC, 950,
                           "대마법사만이 다룰 수 있는 지팡이", 12, {"magic_power": 45, "all_spell_boost": 20}, 1),
                
                # 전설 무기 (18층부터)
                MerchantItem("엑스칼리버", ItemType.WEAPON, ItemRarity.LEGENDARY, 2000,
                           "전설의 성검", 18, {"attack": 60, "holy_damage": 25, "leadership": 1}, 1),
                MerchantItem("메테오 스태프", ItemType.WEAPON, ItemRarity.LEGENDARY, 2200,
                           "별의 힘을 담은 지팡이", 18, {"magic_power": 65, "meteor_spell": 1}, 1),
                
                # 신화 무기 (25층부터)
                MerchantItem("창조의 검", ItemType.WEAPON, ItemRarity.MYTHIC, 5000,
                           "세상을 창조한 신의 검", 25, {"attack": 100, "creation_power": 1}, 1)
            ],
            
            # 방어구 (무기와 동일한 수량)
            ItemType.ARMOR: [
                # 일반 방어구
                MerchantItem("가죽 갑옷", ItemType.ARMOR, ItemRarity.COMMON, 60,
                           "기본적인 가죽 갑옷", 1, {"defense": 8, "hp": 10}, 2),
                MerchantItem("천 로브", ItemType.ARMOR, ItemRarity.COMMON, 50,
                           "마법사용자용 로브", 1, {"magic_defense": 6, "mp": 8}, 2),
                MerchantItem("경량 갑옷", ItemType.ARMOR, ItemRarity.COMMON, 55,
                           "움직임이 자유로운 갑옷", 1, {"defense": 6, "speed": 2}, 2),
                MerchantItem("견습 로브", ItemType.ARMOR, ItemRarity.COMMON, 45,
                           "초보 마법사용 로브", 1, {"magic_defense": 5, "mp": 5}, 2),
                
                # 고급 방어구
                MerchantItem("사슬 갑옷", ItemType.ARMOR, ItemRarity.UNCOMMON, 160,
                           "사슬로 엮은 튼튼한 갑옷", 3, {"defense": 18, "hp": 20}, 1),
                MerchantItem("마법사 로브", ItemType.ARMOR, ItemRarity.UNCOMMON, 140,
                           "마법 보조 효과가 있는 로브", 3, {"magic_defense": 15, "mp": 25, "magic_power": 5}, 1),
                MerchantItem("민첩 갑옷", ItemType.ARMOR, ItemRarity.UNCOMMON, 130,
                           "속도를 향상시키는 갑옷", 3, {"defense": 12, "speed": 10, "evasion": 5}, 1),
                MerchantItem("학자 로브", ItemType.ARMOR, ItemRarity.UNCOMMON, 150,
                           "학자들이 애용하는 로브", 3, {"magic_defense": 16, "mp": 20, "wisdom": 3}, 1),
                
                # 희귀 방어구
                MerchantItem("플레이트 아머", ItemType.ARMOR, ItemRarity.RARE, 400,
                           "최고급 판금 갑옷", 7, {"defense": 30, "hp": 40, "intimidation": 1}, 1),
                MerchantItem("현자의 로브", ItemType.ARMOR, ItemRarity.RARE, 380,
                           "지혜로운 현자의 로브", 7, {"magic_defense": 25, "mp": 50, "all_resist": 10}, 1),
                MerchantItem("그림자 갑옷", ItemType.ARMOR, ItemRarity.RARE, 350,
                           "그림자 속에 숨게해주는 갑옷", 7, {"defense": 20, "speed": 20, "stealth": 2}, 1),
                MerchantItem("대마법사 로브", ItemType.ARMOR, ItemRarity.RARE, 420,
                           "대마법사의 권위를 상징", 7, {"magic_defense": 28, "mp": 60, "magic_power": 10}, 1),
                
                # 영웅 방어구
                MerchantItem("드래곤 스케일", ItemType.ARMOR, ItemRarity.EPIC, 900,
                           "용의 비늘로 만든 갑옷", 12, {"defense": 45, "fire_resist": 50}, 1),
                MerchantItem("아크메이지 로브", ItemType.ARMOR, ItemRarity.EPIC, 850,
                           "아크메이지만이 입을 수 있는 로브", 12, {"magic_defense": 40, "mp": 100, "spell_amp": 25}, 1),
                
                # 전설 방어구
                MerchantItem("성기사 갑옷", ItemType.ARMOR, ItemRarity.LEGENDARY, 2100,
                           "성스러운 기사의 갑옷", 18, {"defense": 65, "holy_resist": 75, "leadership": 1}, 1),
                MerchantItem("시공 로브", ItemType.ARMOR, ItemRarity.LEGENDARY, 2000,
                           "시공을 다루는 로브", 18, {"magic_defense": 60, "time_control": 1}, 1),
                
                # 신화 방어구
                MerchantItem("절대 방어", ItemType.ARMOR, ItemRarity.MYTHIC, 5500,
                           "모든 공격을 막아내는 갑옷", 25, {"defense": 120, "absolute_defense": 1}, 1)
            ],
            
            # 장신구 (방어구와 동일한 수량)
            ItemType.ACCESSORY: [
                # 일반 장신구
                MerchantItem("힘의 반지", ItemType.ACCESSORY, ItemRarity.COMMON, 80,
                           "착용자의 힘을 증가시킨다", 1, {"attack": 5}, 1),
                MerchantItem("민첩 목걸이", ItemType.ACCESSORY, ItemRarity.COMMON, 75,
                           "움직임을 빠르게 해준다", 1, {"speed": 4}, 1),
                MerchantItem("지혜 귀걸이", ItemType.ACCESSORY, ItemRarity.COMMON, 70,
                           "마법 능력을 향상시킨다", 1, {"magic_power": 4}, 1),
                MerchantItem("체력 팔찌", ItemType.ACCESSORY, ItemRarity.COMMON, 85,
                           "체력을 증가시켜준다", 1, {"hp": 15}, 1),
                
                # 고급 장신구
                MerchantItem("전사의 반지", ItemType.ACCESSORY, ItemRarity.UNCOMMON, 200,
                           "전사의 기운이 깃든 반지", 3, {"attack": 10, "critical": 3}, 1),
                MerchantItem("바람 목걸이", ItemType.ACCESSORY, ItemRarity.UNCOMMON, 180,
                           "바람의 속도를 빌려준다", 3, {"speed": 8, "evasion": 5}, 1),
                MerchantItem("현자의 귀걸이", ItemType.ACCESSORY, ItemRarity.UNCOMMON, 190,
                           "현자의 지혜가 담긴 귀걸이", 3, {"magic_power": 8, "mp": 15}, 1),
                MerchantItem("생명 팔찌", ItemType.ACCESSORY, ItemRarity.UNCOMMON, 170,
                           "생명력을 강화해준다", 3, {"hp": 30, "regen": 1}, 1),
                
                # 희귀 장신구
                MerchantItem("용사의 반지", ItemType.ACCESSORY, ItemRarity.RARE, 450,
                           "용사가 착용하던 반지", 7, {"attack": 15, "critical": 8, "leadership": 1}, 1),
                MerchantItem("정령 목걸이", ItemType.ACCESSORY, ItemRarity.RARE, 400,
                           "정령의 축복이 깃든 목걸이", 7, {"magic_power": 12, "elemental_boost": 20}, 1),
                MerchantItem("불멸 팔찌", ItemType.ACCESSORY, ItemRarity.RARE, 480,
                           "죽음을 거부하는 팔찌", 7, {"hp": 60, "death_resist": 50}, 1),
                MerchantItem("행운의 귀걸이", ItemType.ACCESSORY, ItemRarity.RARE, 420,
                           "행운을 가져다주는 귀걸이", 7, {"luck": 20, "critical": 5, "rare_drop": 15}, 1),
                
                # 영웅 장신구
                MerchantItem("영웅의 증표", ItemType.ACCESSORY, ItemRarity.EPIC, 1000,
                           "진정한 영웅의 상징", 12, {"all_stats": 10, "hero_aura": 1}, 1),
                MerchantItem("시간의 반지", ItemType.ACCESSORY, ItemRarity.EPIC, 1100,
                           "시간을 조종하는 반지", 12, {"speed": 25, "time_manipulation": 1}, 1),
                
                # 전설 장신구
                MerchantItem("운명의 목걸이", ItemType.ACCESSORY, ItemRarity.LEGENDARY, 2500,
                           "운명을 바꾸는 목걸이", 18, {"luck": 50, "fate_control": 1}, 1),
                MerchantItem("신의 반지", ItemType.ACCESSORY, ItemRarity.LEGENDARY, 2800,
                           "신이 착용하던 반지", 18, {"all_stats": 25, "divine_power": 1}, 1),
                
                # 신화 장신구
                MerchantItem("창조주의 인장", ItemType.ACCESSORY, ItemRarity.MYTHIC, 6000,
                           "창조주의 권능이 깃든 인장", 25, {"all_stats": 50, "creation_authority": 1}, 1)
            ],
            
            # 소모품
            ItemType.CONSUMABLE: [
                MerchantItem("체력 포션", ItemType.CONSUMABLE, ItemRarity.COMMON, 25,
                           "HP를 50 회복", 1, {"heal_hp": 50}, 5),
                MerchantItem("마나 포션", ItemType.CONSUMABLE, ItemRarity.COMMON, 30,
                           "MP를 30 회복", 1, {"heal_mp": 30}, 5),
                MerchantItem("해독제", ItemType.CONSUMABLE, ItemRarity.COMMON, 20,
                           "독 상태를 치료", 1, {"cure_poison": 1}, 3),
                MerchantItem("고급 체력 포션", ItemType.CONSUMABLE, ItemRarity.UNCOMMON, 80,
                           "HP를 150 회복", 3, {"heal_hp": 150}, 3),
                MerchantItem("고급 마나 포션", ItemType.CONSUMABLE, ItemRarity.UNCOMMON, 90,
                           "MP를 100 회복", 3, {"heal_mp": 100}, 3),
                MerchantItem("만능 치료약", ItemType.CONSUMABLE, ItemRarity.RARE, 200,
                           "모든 상태이상 치료", 7, {"cure_all": 1}, 2),
                MerchantItem("불사의 영약", ItemType.CONSUMABLE, ItemRarity.EPIC, 500,
                           "HP를 완전히 회복하고 부활", 12, {"full_heal": 1, "revive": 1}, 1),
                MerchantItem("신의 물약", ItemType.CONSUMABLE, ItemRarity.LEGENDARY, 1500,
                           "모든 능력치 영구 증가", 18, {"permanent_boost": 5}, 1)
            ]
        }
    
    def generate_stock(self, current_floor: int, stock_size: int = 12) -> List[MerchantItem]:
        """현재 층에 맞는 재고 생성"""
        self.inventory.clear()
        
        # 층별 희귀도 확률 조정
        rarity_chances = self._get_rarity_chances(current_floor)
        
        # 카테고리별 재고 생성 (재고량 증가)
        weapons = self._select_items_by_rarity(ItemType.WEAPON, current_floor, 3, rarity_chances)
        armors = self._select_items_by_rarity(ItemType.ARMOR, current_floor, 3, rarity_chances)
        accessories = self._select_items_by_rarity(ItemType.ACCESSORY, current_floor, 2, rarity_chances)
        consumables = self._select_items_by_rarity(ItemType.CONSUMABLE, current_floor, 4, rarity_chances)
        
        self.inventory.extend(weapons + armors + accessories + consumables)
        
        # 가격 조정 (성격에 따라)
        self._adjust_prices()
        
        return self.inventory
    
    def _get_rarity_chances(self, floor: int) -> Dict[ItemRarity, float]:
        """층별 희귀도 확률"""
        if floor <= 3:
            return {
                ItemRarity.COMMON: 0.80,
                ItemRarity.UNCOMMON: 0.20,
                ItemRarity.RARE: 0.0,
                ItemRarity.EPIC: 0.0,
                ItemRarity.LEGENDARY: 0.0,
                ItemRarity.MYTHIC: 0.0
            }
        elif floor <= 7:
            return {
                ItemRarity.COMMON: 0.60,
                ItemRarity.UNCOMMON: 0.35,
                ItemRarity.RARE: 0.05,
                ItemRarity.EPIC: 0.0,
                ItemRarity.LEGENDARY: 0.0,
                ItemRarity.MYTHIC: 0.0
            }
        elif floor <= 12:
            return {
                ItemRarity.COMMON: 0.40,
                ItemRarity.UNCOMMON: 0.40,
                ItemRarity.RARE: 0.18,
                ItemRarity.EPIC: 0.02,
                ItemRarity.LEGENDARY: 0.0,
                ItemRarity.MYTHIC: 0.0
            }
        elif floor <= 18:
            return {
                ItemRarity.COMMON: 0.20,
                ItemRarity.UNCOMMON: 0.35,
                ItemRarity.RARE: 0.35,
                ItemRarity.EPIC: 0.10,
                ItemRarity.LEGENDARY: 0.0,
                ItemRarity.MYTHIC: 0.0
            }
        elif floor <= 25:
            return {
                ItemRarity.COMMON: 0.10,
                ItemRarity.UNCOMMON: 0.25,
                ItemRarity.RARE: 0.40,
                ItemRarity.EPIC: 0.20,
                ItemRarity.LEGENDARY: 0.05,
                ItemRarity.MYTHIC: 0.0
            }
        else:  # 25층 이상
            return {
                ItemRarity.COMMON: 0.05,
                ItemRarity.UNCOMMON: 0.15,
                ItemRarity.RARE: 0.35,
                ItemRarity.EPIC: 0.30,
                ItemRarity.LEGENDARY: 0.13,
                ItemRarity.MYTHIC: 0.02
            }
    
    def _select_items_by_rarity(self, item_type: ItemType, floor: int, count: int, 
                               rarity_chances: Dict[ItemRarity, float]) -> List[MerchantItem]:
        """희귀도에 따른 아이템 선택"""
        # 소모품의 경우 별도 처리
        if item_type == ItemType.CONSUMABLE:
            return self._select_consumables(floor, count, rarity_chances)
        
        available_items = [item for item in self.item_pool[item_type] 
                          if item.min_floor <= floor]
        
        selected = []
        for _ in range(count):
            # 희귀도 결정
            rand = random.random()
            cumulative = 0
            selected_rarity = ItemRarity.COMMON
            
            for rarity, chance in rarity_chances.items():
                cumulative += chance
                if rand <= cumulative:
                    selected_rarity = rarity
                    break
            
            # 해당 희귀도의 아이템 중 랜덤 선택
            rarity_items = [item for item in available_items if item.rarity == selected_rarity]
            if rarity_items:
                item = random.choice(rarity_items)
                # 새로운 인스턴스 생성 (재고별로 다른 가격)
                new_item = MerchantItem(
                    item.name, item.item_type, item.rarity, item.base_price,
                    item.description, item.min_floor, item.effects.copy(), item.stock
                )
                selected.append(new_item)
        
        return selected
    
    def _adjust_prices(self):
        """상인 성격에 따른 가격 조정"""
        for item in self.inventory:
            if self.personality == "stingy":
                # 구두쇠 - 20-50% 비싸게
                multiplier = random.uniform(1.2, 1.5)
            elif self.personality == "generous":
                # 관대함 - 10-30% 저렴하게
                multiplier = random.uniform(0.7, 0.9)
            elif self.personality == "chaotic":
                # 혼돈 - 극단적 가격 (50% 저렴 또는 200% 비싸게)
                if random.random() < 0.3:
                    multiplier = random.uniform(0.5, 0.8)  # 매우 저렴
                else:
                    multiplier = random.uniform(1.5, 2.0)  # 매우 비쌈
            else:
                # 보통 - 기본 변동
                multiplier = random.uniform(0.9, 1.1)
            
            item.current_price = int(item.current_price * multiplier)
    
    def get_personality_greeting(self) -> str:
        """성격에 따른 인사말"""
        greetings = {
            "stingy": [
                f"어서오게... {self.name}일세. 좋은 물건이 있지만 값은 비싸다네.",
                "흥정은 사양하네. 내 물건은 그만한 값어치를 한다고!",
                "돈 없으면 구경만 하고 가게나."
            ],
            "generous": [
                f"환영하네! 나는 {self.name}이라네. 좋은 가격에 좋은 물건을 팔고 있다네!",
                "모험가에게는 특별 할인을 해주지! 뭐가 필요한가?",
                "위험한 모험을 하는 자네들을 위해 좋은 물건을 준비했네."
            ],
            "chaotic": [
                f"크크크... {self.name}이다. 오늘은 운이 좋을까? 나쁠까?",
                "가격은... 음... 기분에 따라 정하겠네! 운에 맡기게!",
                "혹시 도박은 좋아하나? 내 물건들도 도박 같은 가격이지!"
            ],
            "normal": [
                f"어서 오세요. {self.name}입니다. 필요한 물건이 있으시면 말씀하세요.",
                "좋은 품질의 상품들을 적당한 가격에 판매하고 있습니다.",
                "뭔가 찾고 계신 특별한 물건이 있나요?"
            ]
        }
        
        return random.choice(greetings.get(self.personality, greetings["normal"]))
    
    def buy_item(self, item: MerchantItem, player_gold: int) -> Dict:
        """아이템 구매"""
        if item not in self.inventory:
            return {"success": False, "message": "그 아이템은 없습니다."}
        
        if player_gold < item.current_price:
            return {"success": False, "message": "골드가 부족합니다!"}
        
        if item.stock <= 0:
            return {"success": False, "message": "재고가 없습니다."}
        
        # 구매 성공
        item.stock -= 1
        if item.stock <= 0:
            self.inventory.remove(item)
        
        self.gold += item.current_price
        
        return {
            "success": True, 
            "message": f"{item.name}을(를) {item.current_price} 골드에 구매했습니다!",
            "cost": item.current_price,
            "item": item
        }
    
    def sell_item_to_merchant(self, item_name: str, sell_price: int, player_gold: int) -> Dict:
        """플레이어가 상인에게 아이템 판매"""
        if self.gold < sell_price:
            return {"success": False, "message": "상인에게 골드가 부족합니다."}
        
        # 상인 성격에 따른 가격 조정
        if self.personality == "stingy":
            actual_price = int(sell_price * 0.6)  # 40% 할인해서 구매
        elif self.personality == "generous":
            actual_price = int(sell_price * 0.9)  # 10% 할인해서 구매
        else:
            actual_price = int(sell_price * 0.75)  # 25% 할인해서 구매
        
        if self.gold < actual_price:
            return {"success": False, "message": "상인에게 골드가 부족합니다."}
        
        self.gold -= actual_price
        
        return {
            "success": True,
            "message": f"{item_name}을(를) {actual_price} 골드에 판매했습니다!",
            "gold_gained": actual_price
        }
    
    def _select_consumables(self, floor: int, count: int, rarity_chances: Dict[ItemRarity, float]) -> List[MerchantItem]:
        """소모품 선택"""
        try:
            consumable_db = get_consumable_database()
            available_consumables = list(consumable_db.consumables.values())
            
            selected = []
            for _ in range(count):
                # 희귀도 결정
                rand = random.random()
                cumulative = 0
                selected_rarity = ItemRarity.COMMON
                
                for rarity, chance in rarity_chances.items():
                    cumulative += chance
                    if rand <= cumulative:
                        selected_rarity = rarity
                        break
                
                # ConsumableRarity로 변환
                consumable_rarity = self._convert_merchant_rarity(selected_rarity)
                
                # 해당 희귀도의 소모품 중 랜덤 선택
                rarity_consumables = [c for c in available_consumables if c.rarity == consumable_rarity]
                if rarity_consumables:
                    consumable = random.choice(rarity_consumables)
                    
                    # 가격 계산
                    base_price = self._calculate_consumable_price(consumable)
                    
                    # MerchantItem으로 변환
                    merchant_item = MerchantItem(
                        name=consumable.name,
                        item_type=ItemType.CONSUMABLE,
                        rarity=selected_rarity,
                        base_price=base_price,
                        description=consumable.description or f"{consumable.effect_type} 효과",
                        min_floor=1,
                        effects={"effect_type": consumable.effect_type, "effect_value": consumable.effect_value},
                        stock=random.randint(1, 3)
                    )
                    
                    selected.append(merchant_item)
            
            return selected
        except Exception as e:
            print(f"소모품 선택 중 오류 발생: {e}")
            return []
    
    def _convert_merchant_rarity(self, merchant_rarity: ItemRarity) -> ConsumableRarity:
        """상인 아이템 희귀도를 소모품 희귀도로 변환"""
        conversion = {
            ItemRarity.COMMON: ConsumableRarity.COMMON,
            ItemRarity.UNCOMMON: ConsumableRarity.RARE,
            ItemRarity.RARE: ConsumableRarity.RARE,
            ItemRarity.EPIC: ConsumableRarity.EPIC,
            ItemRarity.LEGENDARY: ConsumableRarity.LEGENDARY,
            ItemRarity.MYTHIC: ConsumableRarity.MYTHIC
        }
        return conversion.get(merchant_rarity, ConsumableRarity.COMMON)
    
    def _calculate_consumable_price(self, consumable: Consumable) -> int:
        """소모품 기본 가격 계산"""
        base_prices = {
            ConsumableRarity.COMMON: 15,
            ConsumableRarity.RARE: 40,
            ConsumableRarity.EPIC: 100,
            ConsumableRarity.LEGENDARY: 250,
            ConsumableRarity.MYTHIC: 600
        }
        
        base_price = base_prices.get(consumable.rarity, 20)
        
        # 효과 값에 따른 가격 조정
        if consumable.effect_value > 100:
            base_price = int(base_price * 1.5)
        elif consumable.effect_value > 50:
            base_price = int(base_price * 1.2)
        
        # 전체 대상 아이템은 비싸게
        if "all" in consumable.target_type:
            base_price = int(base_price * 1.5)
        
        return base_price
    
    def offer_repair_service(self, party_manager) -> bool:
        """장비 수리 서비스 제공"""
        print(f"\n{self.name}: '장비 수리도 해드립니다! 골드만 있으면요!'")
        
        # 수리 가능한 장비 찾기
        repairable_items = []
        for member in party_manager.get_alive_members():
            if hasattr(member, 'equipment') and member.equipment:
                for slot, equipment in member.equipment.items():
                    if equipment and hasattr(equipment, 'current_durability'):
                        if equipment.current_durability < equipment.max_durability:
                            repair_needed = equipment.max_durability - equipment.current_durability
                            repair_cost = self._calculate_repair_cost(equipment, repair_needed)
                            repairable_items.append((member, slot, equipment, repair_cost))
        
        if not repairable_items:
            print(f"{self.name}: '모든 장비가 완벽한 상태네요! 수리할 게 없습니다.'")
            return False
        
        print(f"\n🔧 수리 서비스 메뉴:")
        print("="*60)
        
        # 수리 옵션 표시
        for i, (member, slot, equipment, cost) in enumerate(repairable_items, 1):
            durability_percent = int((equipment.current_durability / equipment.max_durability) * 100)
            print(f"{i}. {member.name}의 {equipment.name}")
            print(f"   내구도: {equipment.current_durability}/{equipment.max_durability} ({durability_percent}%)")
            print(f"   수리비: {cost} 골드")
        
        print(f"\n{len(repairable_items) + 1}. 모든 장비 일괄 수리")
        total_cost = sum(cost for _, _, _, cost in repairable_items)
        
        # 성격에 따른 할인
        if self.personality == "generous":
            total_cost = int(total_cost * 0.8)
            print(f"   총 비용: {total_cost} 골드 (친절 할인 20%)")
        elif self.personality == "stingy":
            total_cost = int(total_cost * 1.2)
            print(f"   총 비용: {total_cost} 골드 (바가지 요금 +20%)")
        else:
            print(f"   총 비용: {total_cost} 골드")
        
        print(f"\n0. 나가기")
        
        try:
            choice = int(input(f"\n선택하세요: "))
            
            if choice == 0:
                return False
            elif 1 <= choice <= len(repairable_items):
                # 개별 장비 수리
                member, slot, equipment, cost = repairable_items[choice - 1]
                
                # 성격에 따른 가격 조정
                if self.personality == "generous":
                    cost = int(cost * 0.8)
                elif self.personality == "stingy":
                    cost = int(cost * 1.2)
                
                if party_manager.gold < cost:
                    print(f"{self.name}: '골드가 부족하시네요. {cost} 골드가 필요합니다.'")
                    return False
                
                # 수리 실행
                party_manager.gold -= cost
                equipment.current_durability = equipment.max_durability
                equipment.is_broken = False
                
                print(f"✨ {equipment.name}이(가) 완전히 수리되었습니다!")
                print(f"💰 {cost} 골드를 지불했습니다. (잔액: {party_manager.gold}G)")
                return True
                
            elif choice == len(repairable_items) + 1:
                # 일괄 수리
                if party_manager.gold < total_cost:
                    print(f"{self.name}: '골드가 부족하시네요. {total_cost} 골드가 필요합니다.'")
                    return False
                
                # 모든 장비 수리
                party_manager.gold -= total_cost
                repaired_count = 0
                
                for member, slot, equipment, _ in repairable_items:
                    equipment.current_durability = equipment.max_durability
                    equipment.is_broken = False
                    repaired_count += 1
                
                print(f"✨ 모든 장비가 완전히 수리되었습니다! ({repaired_count}개)")
                print(f"💰 {total_cost} 골드를 지불했습니다. (잔액: {party_manager.gold}G)")
                return True
            else:
                print("잘못된 선택입니다.")
                return False
                
        except (ValueError, KeyboardInterrupt):
            print("취소되었습니다.")
            return False
    
    def _calculate_repair_cost(self, equipment, repair_amount: int) -> int:
        """수리 비용 계산"""
        # 기본 수리비: 수리량 * 2
        base_cost = repair_amount * 2
        
        # 장비 등급에 따른 수리비 배율
        rarity_multipliers = {
            "일반": 1.0,
            "고급": 1.5,
            "희귀": 2.0,
            "영웅": 3.0,
            "전설": 5.0,
            "신화": 8.0
        }
        
        if hasattr(equipment, 'rarity'):
            if hasattr(equipment.rarity, 'value'):
                multiplier = rarity_multipliers.get(equipment.rarity.value, 1.0)
            else:
                multiplier = rarity_multipliers.get(str(equipment.rarity), 1.0)
        else:
            multiplier = 1.0
        
        final_cost = int(base_cost * multiplier)
        
        # 최소 수리비
        return max(final_cost, 5)
    
    def restock(self, current_floor: int):
        """재고 보충"""
        self.restock_timer = 0
        self.generate_stock(current_floor)
        print(f"🛍️ {self.name}이 재고를 보충했습니다!")

# 전역 상인 관리자
balanced_merchant = BalancedMerchant()

def get_balanced_merchant() -> BalancedMerchant:
    """밸런스 조정된 상인 반환"""
    return balanced_merchant
